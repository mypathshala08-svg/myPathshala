"""Cached vs checkpointed RDD when a worker is lost."""
import os, time, sys
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("tiffingo-ckpt-failover").getOrCreate()
sc = spark.sparkContext
sc.setCheckpointDir("/data/ckpt_cluster")
calls = sc.accumulator(0)
def expensive(x):
    calls.add(1)
    s = 0
    for k in range(200):
        s += (x * k) % 7
    return (x % 1000, s)
mode = sys.argv[1]
r = sc.parallelize(range(400_000), 8).map(expensive).cache()
if mode == "checkpoint":
    r.checkpoint()
sc.setJobDescription(f"{mode}: first count")
t = time.time(); n = r.count(); print(f"{mode}: first count {n} in {time.time()-t:.1f} s, expensive() calls {calls.value}", flush=True)
open(f"/data/go_ready_{mode}", "w").close()
while not os.path.exists(f"/data/go_on_{mode}"):
    time.sleep(1)
time.sleep(12)                                   # let the driver notice the lost executor
before = calls.value
sc.setJobDescription(f"{mode}: count after a worker was stopped")
t = time.time(); n = r.count()
print(f"{mode}: after worker loss count {n} in {time.time()-t:.1f} s, extra expensive() calls {calls.value - before}", flush=True)
spark.stop()
