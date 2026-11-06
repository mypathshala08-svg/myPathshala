import sys, socket, os
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.appName("tiffingo-yarn-demo").getOrCreate(); sc = spark.sparkContext
print("master:", sc.master, "| deployMode:", sc.getConf().get("spark.submit.deployMode"), "| appId:", sc.applicationId)
print("driver host:", socket.gethostname(), "| driver container:", os.environ.get("CONTAINER_ID", "(none: client mode)"))
n = spark.range(5_000_000).select((F.col("id") % 7).alias("k")).groupBy("k").count().count()
print("groups:", n)
ex = sc._jsc.sc().getExecutorMemoryStatus().size() - 1
print("executors registered:", ex)
spark.stop()
