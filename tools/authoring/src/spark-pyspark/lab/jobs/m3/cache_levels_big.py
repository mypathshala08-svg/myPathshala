"""Storage levels on the cluster: time, memory, disk and fraction cached."""
import json, time, urllib.request
from pyspark import StorageLevel
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.appName("tiffingo-cache-levels-big").getOrCreate()
sc = spark.sparkContext
def storage():
    u = f"http://localhost:4040/api/v1/applications/{sc.applicationId}/storage/rdd"
    return json.load(urllib.request.urlopen(u))
def q(df):
    return df.where("status = 'DELIVERED'").groupBy("city").agg(F.sum("amount")).collect()

base = (spark.read.parquet("/data/orders_big")
        .repartition(32)
        .withColumn("note", F.concat(F.sha2(F.col("order_id").cast("string"), 256), F.sha2(F.concat_ws("-", "order_id", "customer_id"), 256), F.sha2(F.concat_ws("+", "customer_id", "order_id"), 512))))
sc.setJobDescription("baseline: query twice, no cache")
t = time.time(); q(base); t1 = time.time() - t
t = time.time(); q(base); t2 = time.time() - t
print(f"{'NONE':22} 1st {t1:5.1f} s  2nd {t2:5.1f} s")

for name in ["MEMORY_ONLY", "MEMORY_AND_DISK", "DISK_ONLY"]:
    df = base.persist(getattr(StorageLevel, name))
    sc.setJobDescription(f"{name}: fill + query")
    t = time.time(); q(df); t1 = time.time() - t
    sc.setJobDescription(f"{name}: query again")
    t = time.time(); q(df); t2 = time.time() - t
    s = storage()[0]
    print(f"{name:22} 1st {t1:5.1f} s  2nd {t2:5.1f} s  cached {s['numCachedPartitions']}/{s['numPartitions']} partitions"
          f"  memory {s['memoryUsed']/2**20:7.1f} MiB  disk {s['diskUsed']/2**20:7.1f} MiB")
    df.unpersist(blocking=True)
spark.stop()
