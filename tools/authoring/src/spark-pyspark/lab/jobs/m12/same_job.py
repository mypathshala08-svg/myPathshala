"""12.1 The same job on three 'platforms': local, standalone cluster, YARN."""
import time
t0 = time.time()
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.appName("tiffingo-same-job").getOrCreate(); sc = spark.sparkContext
t1 = time.time()
df = spark.range(0, 20_000_000, 1, 8).select((F.col("id") % 6).alias("city"), (F.col("id") % 500).alias("amount"))
t = time.time(); r = df.groupBy("city").agg(F.sum("amount").alias("rev")).orderBy("city").collect(); q = time.time() - t
print(f"master={sc.master:32} | session start {t1 - t0:4.1f} s | query {q:4.1f} s | result rows {len(r)} | first {r[0]['rev']}")
spark.stop()
