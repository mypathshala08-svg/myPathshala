-- TiffinGo data tests: run after every load. Any FAIL should alert the on-call engineer.
-- One small INSERT per test (a single six-way UNION ALL hits Tez's 120-counter limit, Lesson 12.2).
USE tiffingo_dw;
CREATE TABLE IF NOT EXISTS dq_results (test STRING, passed BOOLEAN, detail STRING, run_ts TIMESTAMP) STORED AS ORC;
TRUNCATE TABLE dq_results;
INSERT INTO dq_results SELECT 'fact key unique', COUNT(*) = COUNT(DISTINCT order_id),
  CONCAT(COUNT(*), ' rows / ', COUNT(DISTINCT order_id), ' ids'), CURRENT_TIMESTAMP FROM fact_orders;
INSERT INTO dq_results SELECT 'gold net = fact net', g.v = f.v, CONCAT(g.v, ' vs ', f.v), CURRENT_TIMESTAMP
  FROM (SELECT SUM(net_revenue) AS v FROM gold_city_daily) g
  CROSS JOIN (SELECT SUM(amount) AS v FROM fact_orders WHERE status = 'DELIVERED') f;
INSERT INTO dq_results SELECT 'one current row per customer', SUM(IF(c <> 1, 1, 0)) = 0,
  CONCAT(SUM(IF(c <> 1, 1, 0)), ' violations'), CURRENT_TIMESTAMP
  FROM (SELECT customer_id, SUM(IF(is_current, 1, 0)) AS c FROM dim_customer GROUP BY customer_id) x;
INSERT INTO dq_results SELECT 'no negative SCD intervals', COUNT(*) = 0, CONCAT(COUNT(*), ' rows'), CURRENT_TIMESTAMP
  FROM dim_customer WHERE valid_to < valid_from;
INSERT INTO dq_results SELECT 'every fact restaurant known', COUNT(*) = 0, CONCAT(COUNT(*), ' orphans'), CURRENT_TIMESTAMP
  FROM fact_orders f LEFT JOIN dim_restaurant r ON r.restaurant_id = f.restaurant_id WHERE r.restaurant_id IS NULL;
INSERT INTO dq_results SELECT 'reject rate below 1%',
  SUM(IF(step = 'rejected', row_count, 0)) / SUM(IF(step = 'raw_rows', row_count, 0)) < 0.01,
  CONCAT(ROUND(100 * SUM(IF(step = 'rejected', row_count, 0)) / SUM(IF(step = 'raw_rows', row_count, 0)), 2), '%'),
  CURRENT_TIMESTAMP FROM etl_audit;
INSERT INTO dq_results SELECT 'every day loaded', COUNT(DISTINCT order_date) = 31,
  CONCAT(COUNT(DISTINCT order_date), ' of 31 days'), CURRENT_TIMESTAMP FROM gold_city_daily
  WHERE order_date BETWEEN DATE '2026-10-01' AND DATE '2026-10-31';
SELECT test, IF(passed, 'PASS', 'FAIL') AS result, detail FROM dq_results;
