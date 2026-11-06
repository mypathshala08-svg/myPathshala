USE tiffingo_dw;
-- conformed date dimension: 2026-01-01 .. 2027-12-31 (730 days)
CREATE TABLE IF NOT EXISTS dim_date STORED AS ORC AS
SELECT d AS date_key, YEAR(d) AS yr, MONTH(d) AS mon, DAY(d) AS dom,
       DATE_FORMAT(d, 'EEEE') AS day_name, DAYOFWEEK(d) IN (1, 7) AS is_weekend   -- 1 = Sunday, 7 = Saturday
FROM (SELECT DATE_ADD(DATE '2026-01-01', pos) AS d FROM (SELECT POSEXPLODE(SPLIT(SPACE(729), ' ')) AS (pos, x)) g) t;

CREATE TABLE IF NOT EXISTS dim_restaurant (
  restaurant_id INT, name STRING, city STRING, cuisine STRING, rating DECIMAL(2,1),
  tags ARRAY<STRING>, onboarded DATE)
STORED AS ORC;

CREATE TABLE IF NOT EXISTS dim_customer (
  customer_id INT, name STRING, city STRING, plan STRING,
  valid_from TIMESTAMP, valid_to TIMESTAMP, is_current BOOLEAN)
STORED AS ORC TBLPROPERTIES ('transactional'='true');

CREATE TABLE IF NOT EXISTS fact_orders (
  order_id BIGINT, customer_id INT, restaurant_id INT, order_ts TIMESTAMP,
  amount DECIMAL(10,2), payment STRING, status STRING, updated_at TIMESTAMP, load_date DATE)
PARTITIONED BY (order_date DATE)
STORED AS ORC TBLPROPERTIES ('transactional'='true');

CREATE TABLE IF NOT EXISTS fact_deliveries (
  order_id BIGINT, picked_up_ts TIMESTAMP, delivered_ts TIMESTAMP, rider_id INT)
PARTITIONED BY (load_date DATE)
STORED AS ORC;

CREATE TABLE IF NOT EXISTS stg_orders (
  order_id BIGINT, customer_id INT, restaurant_id INT, order_ts TIMESTAMP, amount DECIMAL(10,2),
  payment STRING, status STRING, updated_at TIMESTAMP, order_date DATE,
  raw_line STRING, reject_reason STRING)
STORED AS ORC;

CREATE TABLE IF NOT EXISTS rejected_orders (raw_line STRING, reject_reason STRING)
PARTITIONED BY (load_date DATE)
STORED AS ORC;

CREATE TABLE IF NOT EXISTS gold_city_daily (
  city STRING, orders BIGINT, delivered BIGINT, cancelled BIGINT, refunded BIGINT,
  gmv DECIMAL(14,2), net_revenue DECIMAL(14,2), upi_share DECIMAL(5,2),
  avg_delivery_min DECIMAL(6,1), p90_delivery_min DECIMAL(6,1))
PARTITIONED BY (order_date DATE)
STORED AS ORC;

CREATE TABLE IF NOT EXISTS etl_audit (
  load_date DATE, step STRING, row_count BIGINT, run_ts TIMESTAMP)
STORED AS ORC;
SHOW TABLES;
