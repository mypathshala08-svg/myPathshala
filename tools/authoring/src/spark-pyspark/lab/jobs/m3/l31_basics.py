"""cache() vs persist(): defaults, laziness, SQL CACHE TABLE, unpersist."""
import json, urllib.request, time
from pyspark import StorageLevel
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master("local[2]").getOrCreate()
sc = spark.sparkContext
def storage():
    return json.load(urllib.request.urlopen(f"{sc.uiWebUrl}/api/v1/applications/{sc.applicationId}/storage/rdd"))
orders = spark.read.parquet("/root/lab/spark/data/orders_big")

df = orders.where("status = 'DELIVERED'").cache()
print("1) DataFrame cache() level :", df.storageLevel)
print("   cached blocks before any action:", len(storage()))
df.count()
s = storage()[0]
print("   after count():", s["numCachedPartitions"], "of", s["numPartitions"], "partitions,", round(s["memoryUsed"] / 2**20, 1), "MiB in memory")
print("   storage name:", s["name"][:60] + "…")

rdd = sc.parallelize(range(10)).cache()
print("2) RDD cache() level       :", rdd.getStorageLevel())

p = orders.persist(StorageLevel.DISK_ONLY)
print("3) persist(DISK_ONLY)      :", p.storageLevel)

spark.sql("CACHE TABLE delivered AS SELECT * FROM parquet.`/root/lab/spark/data/orders_big` WHERE status = 'DELIVERED'")
print("4) CACHE TABLE (eager): cached entries now", len(storage()))
spark.sql("CACHE LAZY TABLE lazy_t AS SELECT city FROM parquet.`/root/lab/spark/data/orders_big`")
print("   CACHE LAZY TABLE: cached entries now", len(storage()))
print("   isCached('delivered'):", spark.catalog.isCached("delivered"))

df.unpersist(); p.unpersist(); spark.sql("UNCACHE TABLE delivered"); spark.catalog.clearCache()
print("5) after unpersist/clearCache: cached entries", len(storage()))
spark.stop()
