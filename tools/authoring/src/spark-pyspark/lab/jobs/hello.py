import time, sys
from pyspark.sql import SparkSession
t=time.time()
spark = SparkSession.builder.appName("hello").master("local[2]").getOrCreate()
print("startup_s", round(time.time()-t,2))
print("version", spark.version, "| master", spark.sparkContext.master, "| ui", spark.sparkContext.uiWebUrl)
df = spark.range(1, 1_000_001)
print("sum", df.selectExpr("sum(id)").first()[0], "| partitions", df.rdd.getNumPartitions())
spark.stop()
