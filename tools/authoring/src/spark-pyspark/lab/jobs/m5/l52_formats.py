"""5.2 Parquet, ORC and Avro vs CSV and JSON: size, speed, pruning, pushdown, schema evolution."""
import time, os, json, urllib.request, glob
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master("local[4]").config("spark.sql.shuffle.partitions", "8").getOrCreate()
sc = spark.sparkContext
OUT = "/root/lab/spark/data/m5/fmt"
def size_mib(p):
    return sum(os.path.getsize(f) for f in glob.glob(p + "/**", recursive=True) if os.path.isfile(f) and not os.path.basename(f).startswith((".", "_"))) / 2**20
def stages():
    return json.load(urllib.request.urlopen(f"{sc.uiWebUrl}/api/v1/applications/{sc.applicationId}/stages"))
def read_mib(f):
    before = {s["stageId"] for s in stages()}
    t = time.time(); f(); el = time.time() - t
    new = [s for s in stages() if s["stageId"] not in before]
    return el, sum(s["inputRecords"] for s in new)
src = spark.read.parquet("/root/lab/spark/data/orders_big").repartition(4)
src.cache().count()

print("== 1) defaults")
for k in ("spark.sql.parquet.compression.codec", "spark.sql.orc.compression.codec", "spark.sql.avro.compression.codec"):
    print(f"{k:38}: {spark.conf.get(k)}")

print("== 2) write 5M orders in five formats")
for fmt in ("csv", "json", "parquet", "orc", "avro"):
    w = src.write.mode("overwrite").format(fmt)
    if fmt == "csv":
        w = w.option("header", True)
    t = time.time(); w.save(f"{OUT}/{fmt}"); el = time.time() - t
    print(f"{fmt:8}: write {el:5.1f} s, size {size_mib(f'{OUT}/{fmt}'):6.1f} MiB")

schema = "order_id BIGINT, customer_id INT, city STRING, order_date DATE, amount INT, status STRING"
def reader(fmt):
    r = spark.read.format(fmt)
    if fmt == "csv":
        r = r.option("header", True).schema(schema)
    elif fmt == "json":
        r = r.schema(schema)
    return r.load(f"{OUT}/{fmt}")

print("== 3) query: sum(amount) for Pune (one column + one filter)")
for fmt in ("csv", "json", "parquet", "orc", "avro"):
    df = reader(fmt)
    q = lambda: df.where(F.col("city") == "Pune").agg(F.sum("amount")).collect()
    q()                                   # warm-up
    el, recs = read_mib(q)
    print(f"{fmt:8}: {el:5.2f} s, rows read {recs:,}")

print("== 3b) all columns vs one column (write to noop)")
for fmt in ("csv", "parquet"):
    df = reader(fmt)
    for label, d in (("all columns", df), ("amount only", df.select("amount"))):
        d.write.format("noop").mode("overwrite").save()
        t = time.time(); d.write.format("noop").mode("overwrite").save()
        print(f"{fmt:8} {label:12}: {time.time()-t:4.2f} s")

print("== 4) the plan shows pruning and pushdown")
reader("parquet").where(F.col("city") == "Pune").select("amount").explain()

print("== 5) row-group skipping: a selective filter on a sorted column")
src.sortWithinPartitions("order_id").write.mode("overwrite").option("parquet.block.size", 8 * 2**20).parquet(f"{OUT}/parquet_sorted")
for label, path in [("unsorted", f"{OUT}/parquet"), ("sorted by order_id", f"{OUT}/parquet_sorted")]:
    df = spark.read.parquet(path)
    q = lambda: df.where(F.col("order_id") == 4_200_000).count()
    q(); el, recs = read_mib(q)
    print(f"{label:20}: {el:4.2f} s, rows read {recs:,} of 5,000,000")

print("== 6) the schema travels with the file")
spark.read.parquet(f"{OUT}/parquet").printSchema()

import shutil; shutil.rmtree(f"{OUT}/evolve", ignore_errors=True)
print("== 7) schema evolution: a new column next month")
spark.createDataFrame([(1, "Pune", 450)], "order_id INT, city STRING, amount INT").write.mode("overwrite").parquet(f"{OUT}/evolve/month=10")
spark.createDataFrame([(2, "Delhi", 380, "FEST20")], "order_id INT, city STRING, amount INT, coupon STRING").write.mode("overwrite").parquet(f"{OUT}/evolve/month=11")
print("default    :", spark.read.parquet(f"{OUT}/evolve").columns)
m = spark.read.option("mergeSchema", True).parquet(f"{OUT}/evolve")
print("mergeSchema:", m.columns)
m.orderBy("order_id").show()

print("== 8) a type change breaks the read")
spark.createDataFrame([(3, "Pune", "450.50")], "order_id INT, city STRING, amount STRING").write.mode("overwrite").parquet(f"{OUT}/evolve/month=12")
try:
    spark.read.option("mergeSchema", True).parquet(f"{OUT}/evolve").show()
except Exception as e:
    import re
    for k in re.findall(r"\[[A-Z_.]+\][^\n]{0,110}", str(e))[:2]:
        print(k)

print("== 9) Parquet codecs")
for codec in ("snappy", "zstd", "gzip", "uncompressed"):
    t = time.time(); src.write.mode("overwrite").option("compression", codec).parquet(f"{OUT}/codec_{codec}"); el = time.time() - t
    df = spark.read.parquet(f"{OUT}/codec_{codec}")
    t = time.time(); df.agg(F.sum("amount")).collect(); r = time.time() - t
    print(f"{codec:12}: {size_mib(f'{OUT}/codec_{codec}'):5.1f} MiB, write {el:4.1f} s, read {r:4.2f} s")
