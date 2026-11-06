"""Checkpointing: cutting lineage, cost, and long iterative plans."""
import os, shutil, time
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master("local[2]").getOrCreate()
sc = spark.sparkContext
CK = "/root/lab/spark/data/ckpt"; shutil.rmtree(CK, ignore_errors=True)
sc.setCheckpointDir(CK)

print("== 1) RDD lineage grows in a loop ==")
r = sc.parallelize(range(100_000), 4).map(lambda x: (x % 100, 1))
for i in range(30):
    r = r.mapValues(lambda v: v + 1)
print("30 x mapValues   -> lineage lines:", len(r.toDebugString().decode().splitlines()), "(PySpark fuses narrow Python steps)")
day = sc.parallelize([(0, 1)], 1)
for i in range(30):                                   # append one small batch per day
    r = r.union(day)
print("+ 30 x union     -> lineage lines:", len(r.toDebugString().decode().splitlines()), "| partitions:", r.getNumPartitions())
r.checkpoint()
print("checkpoint() called; isCheckpointed:", r.isCheckpointed())
r.count()
print("after count();     isCheckpointed:", r.isCheckpointed(), "| file:", r.getCheckpointFile().replace("file:" + CK, "<ckpt>"))
print("lineage now:\n" + r.toDebugString().decode().replace("file:" + CK, "<ckpt>"))
files = [os.path.relpath(os.path.join(d, f), CK) for d, _, fs in os.walk(CK) for f in fs if not f.startswith(".")]
print("files:", sorted(files)[:5], "…", len(files), "files")

print("\n== 2) checkpoint computes the RDD twice unless cached ==")
calls = sc.accumulator(0)
def work(x):
    calls.add(1); return x * 2
a = sc.parallelize(range(10_000), 4).map(work); a.checkpoint(); a.count()
print("no cache  : work() calls =", calls.value)
calls.value = 0
b = sc.parallelize(range(10_000), 4).map(work).cache(); b.checkpoint(); b.count()
print("with cache: work() calls =", calls.value)

print("\n== 3) localCheckpoint: lineage cut, nothing written ==")
before = sum(len(fs) for _, _, fs in os.walk(CK))
c = sc.parallelize(range(1000), 2).map(lambda x: x + 1); c.localCheckpoint(); c.count()
print("lineage:", c.toDebugString().decode().strip().splitlines()[0], "| new files:", sum(len(fs) for _, _, fs in os.walk(CK)) - before)

print("\n== 4) a DataFrame built in a loop ==")
def build(n, ck_every=None):
    df = spark.range(200_000).withColumn("v", F.lit(0))
    for i in range(n):
        df = df.withColumn("v", F.col("v") + F.col("id") % 7)
        if ck_every and (i + 1) % ck_every == 0:
            df = df.checkpoint()
    return df
for n, ck in [(100, None), (200, None), (400, None), (400, 50)]:
    t = time.time(); df = build(n, ck); s = df.agg(F.sum("v")).first()[0]
    print(f"{n:3} steps, checkpoint every {str(ck):4}: {time.time() - t:5.1f} s  plan lines {len(df._jdf.queryExecution().analyzed().toString().splitlines()):4}  sum {s}")
spark.stop()
