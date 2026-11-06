"""5.3 Writing data: save modes, partitionBy, pruning, small files, dynamic overwrite, maxRecordsPerFile, tables."""
import time, os, glob, shutil, json, urllib.request
from pyspark.sql import SparkSession, functions as F
spark = (SparkSession.builder.master("local[4]")
         .config("spark.sql.warehouse.dir", "/root/lab/spark/data/m5/warehouse")
         .config("spark.sql.adaptive.coalescePartitions.enabled", "false")
         .getOrCreate())
sc = spark.sparkContext
O = "/root/lab/spark/data/m5/out"
shutil.rmtree(O, ignore_errors=True); os.makedirs(O)
def files(p):
    return [f for f in glob.glob(p + "/**", recursive=True) if os.path.isfile(f) and f.endswith(".parquet")]
def short(e, n=160):
    return str(e).split("\n")[0][:n]
orders = spark.read.parquet("/root/lab/spark/data/orders_big")
print("shuffle partitions:", spark.conf.get("spark.sql.shuffle.partitions"))

print("== 1) what a write produces")
small = orders.limit(1000).repartition(3)
small.write.parquet(f"{O}/first")
for f in sorted(os.listdir(f"{O}/first")):
    print("  ", f if len(f) < 60 else f[:48] + "…" + f[-16:])

print("== 2) save modes")
try:
    small.write.parquet(f"{O}/first")
except Exception as e:
    print("default (errorifexists):", type(e).__name__, short(e, 120))
small.write.mode("ignore").parquet(f"{O}/first");    print("ignore   :", spark.read.parquet(f"{O}/first").count(), "rows")
small.write.mode("append").parquet(f"{O}/first");    print("append   :", spark.read.parquet(f"{O}/first").count(), "rows,", len(files(f"{O}/first")), "files")
small.write.mode("overwrite").parquet(f"{O}/first"); print("overwrite:", spark.read.parquet(f"{O}/first").count(), "rows,", len(files(f"{O}/first")), "files")

print("== 3) partitionBy: folders per value")
orders.write.partitionBy("city").parquet(f"{O}/by_city")
print(sorted(os.listdir(f"{O}/by_city"))[:4], "…", len(os.listdir(f"{O}/by_city")), "entries")
p = spark.read.parquet(f"{O}/by_city")
print("columns:", p.columns)
p.where("city = 'Pune'").select("amount").explain()

print("== 4) partition pruning")
def stages():
    return json.load(urllib.request.urlopen(f"{sc.uiWebUrl}/api/v1/applications/{sc.applicationId}/stages"))
def recs(f):
    b = {s["stageId"] for s in stages()}; t = time.time(); f(); el = time.time() - t
    return el, sum(s["inputRecords"] for s in stages() if s["stageId"] not in b)
flat = spark.read.parquet("/root/lab/spark/data/orders_big")
for label, d in (("not partitioned", flat), ("partitioned by city", p)):
    q = lambda: d.where("city = 'Pune'").agg(F.sum("amount")).collect()
    q(); el, r = recs(q)
    print(f"{label:20}: {el:4.2f} s, rows read {r:,}")

print("== 5) the small-files problem")
agg = orders.groupBy("city", "order_date").agg(F.sum("amount").alias("revenue"), F.count("*").alias("orders"))
shutil.rmtree(f"{O}/daily", ignore_errors=True)
t = time.time(); agg.write.partitionBy("city").parquet(f"{O}/daily"); el = time.time() - t
fs = files(f"{O}/daily")
print(f"after groupBy (200 shuffle partitions): {len(fs)} files, avg {sum(map(os.path.getsize, fs)) / len(fs) / 1024:.1f} KiB, write {el:.1f} s")
t = time.time(); spark.read.parquet(f"{O}/daily").agg(F.sum("revenue")).collect(); print(f"  read back: {time.time()-t:.2f} s")
shutil.rmtree(f"{O}/daily2", ignore_errors=True)
t = time.time(); agg.repartition("city").write.partitionBy("city").parquet(f"{O}/daily2"); el = time.time() - t
fs = files(f"{O}/daily2")
print(f"repartition('city') first           : {len(fs)} files, avg {sum(map(os.path.getsize, fs)) / len(fs) / 1024:.1f} KiB, write {el:.1f} s")
t = time.time(); spark.read.parquet(f"{O}/daily2").agg(F.sum("revenue")).collect(); print(f"  read back: {time.time()-t:.2f} s")

print("== 6) maxRecordsPerFile")
orders.repartition(1).write.option("maxRecordsPerFile", 1_000_000).parquet(f"{O}/capped")
fs = sorted(files(f"{O}/capped"))
print(len(fs), "files:", [round(os.path.getsize(f) / 2**20, 1) for f in fs], "MiB")

print("== 7) overwrite one partition: static vs dynamic")
base = spark.createDataFrame([(1, "Pune", 450), (2, "Delhi", 380), (3, "Mumbai", 610)], "order_id INT, city STRING, amount INT")
fix = spark.createDataFrame([(4, "Pune", 999)], "order_id INT, city STRING, amount INT")
for mode in ("static", "dynamic"):
    path = f"{O}/ow_{mode}"
    base.write.partitionBy("city").parquet(path)
    spark.conf.set("spark.sql.sources.partitionOverwriteMode", mode)
    fix.write.mode("overwrite").partitionBy("city").parquet(path)
    print(f"{mode:8}: folders {sorted(os.listdir(path))} -> rows {sorted((r.city, r.amount) for r in spark.read.parquet(path).collect())}")
spark.conf.set("spark.sql.sources.partitionOverwriteMode", "static")

print("== 8) tables instead of paths")
spark.sql("DROP TABLE IF EXISTS daily_city")
agg.repartition("city").write.mode("overwrite").partitionBy("city").saveAsTable("daily_city")
print(spark.sql("SHOW PARTITIONS daily_city").count(), "partitions |", spark.table("daily_city").where("city='Pune'").count(), "Pune rows")
print([r.col_name + ": " + str(r.data_type) for r in spark.sql("DESCRIBE TABLE EXTENDED daily_city").collect() if r.col_name in ("Provider", "Location", "Type")])
