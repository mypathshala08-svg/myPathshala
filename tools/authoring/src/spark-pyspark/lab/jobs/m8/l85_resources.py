"""8.5 resources & dynamic allocation (runs on the standalone cluster)."""
import sys, time, json, threading, urllib.request
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.getOrCreate(); sc = spark.sparkContext
conf = sc.getConf()
for k in ("spark.executor.cores","spark.executor.memory","spark.cores.max","spark.dynamicAllocation.enabled","spark.dynamicAllocation.maxExecutors"):
    print(f"{k} = {conf.get(k, '(default)')}")
t0 = time.time(); log = []
def poll():
    while True:
        try:
            ex = json.load(urllib.request.urlopen(f"{sc.uiWebUrl}/api/v1/applications/{sc.applicationId}/executors"))
            e = [x for x in ex if x["id"] != "driver" and x["isActive"]]
            log.append((round(time.time()-t0), len(e), sum(x["totalCores"] for x in e)))
        except Exception: pass
        time.sleep(2)
threading.Thread(target=poll, daemon=True).start()
def work(label, n):
    t = time.time()
    spark.range(0, n, 1, 16).select(F.sha2(F.sha2(F.col("id").cast("string"), 256), 512).alias("h")).groupBy(F.substring("h", 1, 2)).count().collect()
    print(f"[{round(time.time()-t0):3}s] {label}: {time.time()-t:.1f} s")
time.sleep(6); work("job 1", 30_000_000)
print(f"[{round(time.time()-t0):3}s] idle 40 s ..."); time.sleep(40)
work("job 2", 30_000_000); time.sleep(3)
seen = []
for s in log:
    if not seen or seen[-1][1:] != s[1:]: seen.append(s)
print("executors over time (t s, executors, cores):", seen)
