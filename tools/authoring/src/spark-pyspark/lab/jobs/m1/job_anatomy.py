"""How one PySpark program becomes jobs, stages and tasks."""
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.appName("tiffingo-job-anatomy").getOrCreate()
sc = spark.sparkContext

sc.setJobDescription("A: read + filter + groupBy (lazy, nothing runs yet)")
orders = spark.read.parquet("/data/orders_big")
daily = (orders.where(F.col("status") == "DELIVERED")
               .groupBy("city")
               .agg(F.count("*").alias("orders"), F.sum("amount").alias("revenue")))
print("input partitions:", orders.rdd.getNumPartitions())

sc.setJobDescription("B: show() the city report")
daily.orderBy(F.desc("revenue")).show(10)

sc.setJobDescription("C: count() all orders")
print("total orders:", orders.count())
daily.explain()
spark.stop()
