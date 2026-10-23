-- sql_on_hadoop.sql: SQL over files in HDFS, with a Hive-style metastore (Spark SQL, run on YARN)
CREATE DATABASE IF NOT EXISTS canteen;
DROP TABLE IF EXISTS canteen.orders;
CREATE TABLE canteen.orders (order_id BIGINT, student STRING, ts STRING, item STRING, amount INT)
  USING csv OPTIONS (path 'hdfs://namenode/user/hadoop/data/student_orders.csv');
DESCRIBE TABLE EXTENDED canteen.orders;
SELECT item, count(*) AS orders, sum(amount) AS revenue FROM canteen.orders GROUP BY item ORDER BY revenue DESC;
SELECT substr(ts, 12, 2) AS hour, count(*) AS orders FROM canteen.orders GROUP BY 1 ORDER BY orders DESC LIMIT 3;
EXPLAIN SELECT item, count(*) FROM canteen.orders GROUP BY item;
