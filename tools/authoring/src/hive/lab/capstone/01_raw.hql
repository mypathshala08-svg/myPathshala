CREATE DATABASE IF NOT EXISTS tiffingo_dw COMMENT 'TiffinGo capstone warehouse';
USE tiffingo_dw;
CREATE EXTERNAL TABLE IF NOT EXISTS raw_orders (
  order_id STRING, customer_id STRING, restaurant_id STRING, order_ts STRING,
  amount STRING, payment STRING, status STRING, updated_at STRING)
PARTITIONED BY (load_date STRING)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION 'file:///data/capstone/landing/orders'
TBLPROPERTIES ('skip.header.line.count'='1');
CREATE EXTERNAL TABLE IF NOT EXISTS raw_customers (
  customer_id STRING, name STRING, city STRING, plan STRING, updated_at STRING)
PARTITIONED BY (load_date STRING)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
LOCATION 'file:///data/capstone/landing/customers'
TBLPROPERTIES ('skip.header.line.count'='1');
CREATE EXTERNAL TABLE IF NOT EXISTS raw_deliveries (
  order_id BIGINT, event STRING, event_ts STRING, rider_id INT)
PARTITIONED BY (load_date STRING)
STORED AS JSONFILE
LOCATION 'file:///data/capstone/landing/deliveries';
CREATE EXTERNAL TABLE IF NOT EXISTS raw_restaurants (
  restaurant_id INT, name STRING, city STRING, cuisine STRING, rating DECIMAL(2,1),
  tags ARRAY<STRING>, onboarded STRING)
STORED AS JSONFILE
LOCATION 'file:///data/capstone/landing/restaurants';
MSCK REPAIR TABLE raw_orders;
MSCK REPAIR TABLE raw_customers;
MSCK REPAIR TABLE raw_deliveries;
