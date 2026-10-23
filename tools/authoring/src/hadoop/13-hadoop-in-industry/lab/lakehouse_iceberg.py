# lakehouse_iceberg.py: an Apache Iceberg table on HDFS (Spark 4.0 + Iceberg 1.10).
# Things a plain folder of Parquet files cannot do: row-level DELETE/UPDATE, snapshots, time travel,
# schema evolution - all as ordinary SQL, with the data still sitting in HDFS.
from pyspark.sql import SparkSession
spark = (SparkSession.builder.appName("lakehouse demo")
         .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
         .config("spark.sql.catalog.lake", "org.apache.iceberg.spark.SparkCatalog")
         .config("spark.sql.catalog.lake.type", "hadoop")                       # catalog = a folder in HDFS
         .config("spark.sql.catalog.lake.warehouse", "hdfs://namenode/lakehouse")
         .getOrCreate())
spark.sparkContext.setLogLevel("ERROR")
q = lambda sql: spark.sql(sql)
def show(title, sql):
    print(f"-- {title}"); q(sql).show(truncate=False)

q("DROP TABLE IF EXISTS lake.canteen.orders PURGE")
q("CREATE TABLE lake.canteen.orders (order_id BIGINT, student STRING, ts TIMESTAMP, item STRING, amount INT) "
  "USING iceberg PARTITIONED BY (days(ts))")
src = (spark.read.csv("hdfs://namenode/user/hadoop/data/student_orders.csv", inferSchema=True)
       .toDF("order_id", "student", "ts", "item", "amount"))
src.writeTo("lake.canteen.orders").append()
show("1. loaded", "SELECT count(*) AS orders, sum(amount) AS revenue FROM lake.canteen.orders")
q("DELETE FROM lake.canteen.orders WHERE item = 'coffee'")                 # e.g. a supplier's orders were fake
q("UPDATE lake.canteen.orders SET amount = 18 WHERE item = 'chai'")       # price correction
show("2. after DELETE coffee + UPDATE chai price", "SELECT count(*) AS orders, sum(amount) AS revenue FROM lake.canteen.orders")
show("3. every change is a snapshot", "SELECT snapshot_id, operation, summary['added-records'] AS added, summary['deleted-records'] AS deleted FROM lake.canteen.orders.snapshots ORDER BY committed_at")
first = q("SELECT snapshot_id FROM lake.canteen.orders.snapshots ORDER BY committed_at LIMIT 1").first()[0]
show("4. time travel: the table as it was at the first snapshot",
     f"SELECT count(*) AS orders, sum(amount) AS revenue FROM lake.canteen.orders VERSION AS OF {first}")
q("ALTER TABLE lake.canteen.orders ADD COLUMN payment STRING")
show("5. schema evolution: a new column, old rows read as NULL", "SELECT order_id, item, amount, payment FROM lake.canteen.orders ORDER BY order_id LIMIT 3")
show("6. partitions Iceberg manages for us (first 3 days)", "SELECT partition, record_count, file_count FROM lake.canteen.orders.partitions ORDER BY partition LIMIT 3")
spark.stop()
