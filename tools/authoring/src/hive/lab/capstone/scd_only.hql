USE tiffingo_dw;
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

