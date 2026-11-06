"""TiffinGo city report: the first job we submit to the cluster."""
import time
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.appName("tiffingo-city-report").getOrCreate()
sc = spark.sparkContext
print("app id      :", sc.applicationId)
print("master      :", sc.master)
print("deploy mode :", sc.getConf().get("spark.submit.deployMode"))
print("parallelism :", sc.defaultParallelism)
orders = spark.read.csv("/data/tiffingo/orders.csv", header=True, inferSchema=True)        # job 0 (+1 for schema inference)
report = (orders.where(F.col("status") == "DELIVERED")
                .groupBy("city")
                .agg(F.count("*").alias("orders"), F.sum(F.col("amount").try_cast("int")).alias("revenue"))
                .orderBy(F.desc("revenue")))
report.show(8)
time.sleep(1)
spark.stop()
