import time
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master("local[2]").getOrCreate()
sc = spark.sparkContext
orders = spark.read.parquet("/root/lab/spark/data/orders_big")
jobs_before = len(sc.statusTracker().getJobIdsForGroup())
t = time.time()
report = (orders.where(F.col("status") == "DELIVERED")
                .withColumn("gst", F.col("amount") * 0.05)
                .groupBy("city").agg(F.sum("gst").alias("gst")))
print(f"3 transformations : {1000*(time.time()-t):7.1f} ms   jobs run: {len(sc.statusTracker().getJobIdsForGroup()) - jobs_before}")
t = time.time()
rows = report.collect()
print(f"1 action collect(): {1000*(time.time()-t):7.1f} ms   jobs run: {len(sc.statusTracker().getJobIdsForGroup()) - jobs_before}")
print("rows returned:", len(rows))
spark.stop()
