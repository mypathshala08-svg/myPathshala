# append_demo.py: the same day written twice with mode("append") vs mode("overwrite")
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.appName("capstone-append-demo").getOrCreate()
day = spark.read.parquet("hdfs://namenode/capstone/silver/orders").where("dt = '2026-09-14'")
for mode in ["append", "overwrite"]:
    path = f"hdfs://namenode/capstone/tmp/{mode}_demo"
    for run in (1, 2):
        day.write.mode(mode).parquet(path)
        r = spark.read.parquet(path).agg(F.count("*"), F.sum("amount")).first()
        print(f"{mode:<9} run {run}: orders {r[0]:,}  revenue {r[1]:,}")
