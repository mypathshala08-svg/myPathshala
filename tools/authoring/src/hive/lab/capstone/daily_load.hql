-- TiffinGo nightly load. usage: beeline ... --hivevar load_date=2026-10-05 -f daily_load.hql
USE tiffingo_dw;
SET hive.exec.dynamic.partition.mode=nonstrict;

-- 0. make sure today's landing folders are registered
ALTER TABLE raw_orders     ADD IF NOT EXISTS PARTITION (load_date='${hivevar:load_date}');
ALTER TABLE raw_customers  ADD IF NOT EXISTS PARTITION (load_date='${hivevar:load_date}');
ALTER TABLE raw_deliveries ADD IF NOT EXISTS PARTITION (load_date='${hivevar:load_date}');

-- 1. reference data (type 1: overwrite)
INSERT OVERWRITE TABLE dim_restaurant
SELECT restaurant_id, name, city, cuisine, rating, tags, CAST(onboarded AS DATE) FROM raw_restaurants;

-- 2. type, validate and tag every raw row of this load
INSERT OVERWRITE TABLE stg_orders
SELECT CAST(o.order_id AS BIGINT), CAST(o.customer_id AS INT), CAST(o.restaurant_id AS INT),
       CAST(o.order_ts AS TIMESTAMP), CAST(o.amount AS DECIMAL(10,2)), o.payment, o.status,
       CAST(o.updated_at AS TIMESTAMP), TO_DATE(CAST(o.order_ts AS TIMESTAMP)),
       CONCAT_WS(',', o.order_id, o.customer_id, o.restaurant_id, o.order_ts, o.amount, o.payment, o.status, o.updated_at),
       CASE WHEN CAST(o.order_id AS BIGINT) IS NULL              THEN 'bad order_id'
            WHEN CAST(o.customer_id AS INT) IS NULL              THEN 'missing customer'
            WHEN CAST(o.order_ts AS TIMESTAMP) IS NULL           THEN 'bad order_ts'
            WHEN CAST(o.amount AS DECIMAL(10,2)) IS NULL         THEN 'bad amount'
            WHEN CAST(o.amount AS DECIMAL(10,2)) <= 0            THEN 'non-positive amount'
            WHEN r.restaurant_id IS NULL                         THEN 'unknown restaurant'
            WHEN o.status NOT IN ('DELIVERED', 'CANCELLED', 'REFUNDED') THEN 'bad status'
       END
FROM raw_orders o
LEFT JOIN dim_restaurant r ON CAST(o.restaurant_id AS INT) = r.restaurant_id
WHERE o.load_date = '${hivevar:load_date}';

-- 3. quarantine (idempotent: overwrite this load's partition)
INSERT OVERWRITE TABLE rejected_orders PARTITION (load_date='${hivevar:load_date}')
SELECT raw_line, reject_reason FROM stg_orders WHERE reject_reason IS NOT NULL;

-- 4. upsert orders: newest version per order wins; resends and duplicates change nothing
MERGE INTO fact_orders t
USING (SELECT * FROM (SELECT s.*, ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC) AS rn
                      FROM stg_orders s WHERE reject_reason IS NULL) x WHERE rn = 1) s
ON t.order_id = s.order_id
WHEN MATCHED AND s.updated_at > t.updated_at THEN
  UPDATE SET status = s.status, amount = s.amount, updated_at = s.updated_at, load_date = DATE '${hivevar:load_date}'
WHEN NOT MATCHED THEN
  INSERT VALUES (s.order_id, s.customer_id, s.restaurant_id, s.order_ts, s.amount, s.payment, s.status,
                 s.updated_at, DATE '${hivevar:load_date}', s.order_date);

-- 5. customers: SCD type 2 (close the old version, insert the new one)
MERGE INTO dim_customer t
USING (
  SELECT c.customer_id AS join_key, c.* FROM
    (SELECT * FROM (SELECT CAST(customer_id AS INT) AS customer_id, name, city, plan, CAST(updated_at AS TIMESTAMP) AS updated_at,
                           ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY updated_at DESC) AS rn
                    FROM raw_customers WHERE load_date = '${hivevar:load_date}') z WHERE rn = 1) c
  UNION ALL
  SELECT NULL AS join_key, c.* FROM
    (SELECT * FROM (SELECT CAST(customer_id AS INT) AS customer_id, name, city, plan, CAST(updated_at AS TIMESTAMP) AS updated_at,
                           ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY updated_at DESC) AS rn
                    FROM raw_customers WHERE load_date = '${hivevar:load_date}') z WHERE rn = 1) c
  JOIN dim_customer d ON d.customer_id = c.customer_id AND d.is_current
  WHERE c.updated_at > d.valid_from                     -- only changes newer than what we hold
    AND (d.city <> c.city OR d.plan <> c.plan OR d.name <> c.name)
) s
ON t.customer_id = s.join_key
WHEN MATCHED AND t.is_current AND s.updated_at > t.valid_from
               AND (t.city <> s.city OR t.plan <> s.plan OR t.name <> s.name) THEN
  UPDATE SET valid_to = s.updated_at, is_current = false
WHEN NOT MATCHED THEN
  INSERT VALUES (s.customer_id, s.name, s.city, s.plan, s.updated_at, TIMESTAMP '9999-12-31 00:00:00', true);

-- 6. delivery events: one row per order (pivot), overwrite this load
INSERT OVERWRITE TABLE fact_deliveries PARTITION (load_date='${hivevar:load_date}')
SELECT order_id,
       MAX(IF(event = 'PICKED_UP', CAST(event_ts AS TIMESTAMP), NULL)),
       MAX(IF(event = 'DELIVERED', CAST(event_ts AS TIMESTAMP), NULL)),
       MAX(rider_id)
FROM raw_deliveries WHERE load_date = '${hivevar:load_date}' GROUP BY order_id;

-- 7. gold: rebuild only the order dates this load touched (late rows and refunds touch old dates)
INSERT OVERWRITE TABLE gold_city_daily PARTITION (order_date)
SELECT r.city, COUNT(*),
       SUM(IF(f.status = 'DELIVERED', 1, 0)), SUM(IF(f.status = 'CANCELLED', 1, 0)), SUM(IF(f.status = 'REFUNDED', 1, 0)),
       SUM(IF(f.status <> 'CANCELLED', f.amount, 0)),
       SUM(IF(f.status = 'DELIVERED', f.amount, 0)),
       ROUND(100 * AVG(IF(f.payment = 'UPI', 1, 0)), 2),
       ROUND(AVG((UNIX_TIMESTAMP(d.delivered_ts) - UNIX_TIMESTAMP(f.order_ts)) / 60), 1),
       ROUND(PERCENTILE_APPROX((UNIX_TIMESTAMP(d.delivered_ts) - UNIX_TIMESTAMP(f.order_ts)) / 60, 0.9), 1),
       f.order_date
FROM fact_orders f
JOIN dim_restaurant r ON r.restaurant_id = f.restaurant_id
LEFT JOIN fact_deliveries d ON d.order_id = f.order_id
WHERE f.order_date IN (SELECT DISTINCT order_date FROM stg_orders WHERE reject_reason IS NULL)
GROUP BY r.city, f.order_date;

-- 8. audit trail for this run (one scan + STACK turns columns into rows)
INSERT INTO etl_audit
SELECT DATE '${hivevar:load_date}', x.step, x.n, CURRENT_TIMESTAMP
FROM (SELECT COUNT(*) AS raw_rows, SUM(IF(reject_reason IS NOT NULL, 1, 0)) AS rejected,
             COUNT(DISTINCT IF(reject_reason IS NULL, order_id, NULL)) AS accepted,
             COUNT(DISTINCT IF(reject_reason IS NULL, order_date, NULL)) AS dates
      FROM stg_orders) s
LATERAL VIEW STACK(4, 'raw_rows', s.raw_rows, 'rejected', s.rejected,
                      'accepted_distinct', s.accepted, 'order_dates_touched', s.dates) x AS step, n;
INSERT INTO etl_audit SELECT DATE '${hivevar:load_date}', 'fact_total', COUNT(*), CURRENT_TIMESTAMP FROM fact_orders;
INSERT INTO etl_audit SELECT DATE '${hivevar:load_date}', 'customers_current', COUNT(*), CURRENT_TIMESTAMP FROM dim_customer WHERE is_current;
