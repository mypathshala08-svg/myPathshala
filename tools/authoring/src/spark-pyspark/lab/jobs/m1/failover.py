"""A heavier job; we stop one worker while it runs."""
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.appName("tiffingo-failover").getOrCreate()
o = spark.read.parquet("/data/orders_big").repartition(16)
h = o.withColumn("h", F.sha2(F.concat_ws("|", *[F.col(c).cast("string") for c in o.columns]), 512))
for i in range(40):
    h = h.withColumn("h", F.sha2(F.col("h"), 512))
res = h.groupBy("city").agg(F.count("*").alias("orders"), F.max("h").alias("max_hash"))
print("cities:", res.count(), "| orders:", res.agg(F.sum("orders")).first()[0])
spark.stop()
