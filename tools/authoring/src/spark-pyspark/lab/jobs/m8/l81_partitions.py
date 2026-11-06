"""8.1 Partitions and shuffle partitions."""
import time, json, urllib.request, os, glob
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master("local[4]").config("spark.driver.memory", "3g").getOrCreate()
sc = spark.sparkContext
def stages():
    return json.load(urllib.request.urlopen(f"{sc.uiWebUrl}/api/v1/applications/{sc.applicationId}/stages"))
def run(label, f):
    b = {s["stageId"] for s in stages()}
    t = time.time(); f(); el = time.time() - t
    new = [s for s in stages() if s["stageId"] not in b and s["status"] == "COMPLETE"]
    print(f"{label:40}: {el:5.2f} s, tasks {sum(s['numTasks'] for s in new):4}, spill {sum(s['memoryBytesSpilled'] for s in new)/2**20:6.1f} MiB")
P = "/root/lab/spark/data/orders_big"
print("files:", len(glob.glob(P + "/*.parquet")), "| size MiB:", round(sum(os.path.getsize(f) for f in glob.glob(P + "/*.parquet")) / 2**20, 1))
print("defaultParallelism:", sc.defaultParallelism, "| maxPartitionBytes:", spark.conf.get("spark.sql.files.maxPartitionBytes"))

print("== 1) input partitions follow file size")
for mpb in ("128MB", "16MB", "4MB"):
    spark.conf.set("spark.sql.files.maxPartitionBytes", mpb)
    print(f"maxPartitionBytes {mpb:5}: {spark.read.parquet(P).rdd.getNumPartitions()} partitions")
spark.conf.set("spark.sql.files.maxPartitionBytes", "128MB")

print("== 2) many small files")
small = "/root/lab/spark/data/m8/small_files"
spark.read.parquet(P).repartition(2000).write.mode("overwrite").parquet(small)
d = spark.read.parquet(small)
print("2000 files ->", d.rdd.getNumPartitions(), "partitions (files packed, openCostInBytes", spark.conf.get("spark.sql.files.openCostInBytes"), ")")
run("count over 2000 small files", lambda: d.agg(F.sum("amount")).collect())
big = spark.read.parquet(P)
run("count over 4 normal files", lambda: big.agg(F.sum("amount")).collect())

print("== 3) shuffle partitions (AQE off to see the raw effect)")
spark.conf.set("spark.sql.adaptive.enabled", "false")
q = lambda: big.groupBy("customer_id", "order_date").agg(F.sum("amount").alias("s")).write.format("noop").mode("overwrite").save()
for n in (1, 4, 16, 200, 2000):
    spark.conf.set("spark.sql.shuffle.partitions", n)
    q(); run(f"groupBy, shuffle.partitions={n}", q)
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.shuffle.partitions", 200)
run("groupBy, 200 + AQE", q)

print("== 4) rows per partition")
r = big.repartition(8)
print("repartition(8):", sorted(r.groupBy(F.spark_partition_id()).count().rdd.map(lambda x: x[1]).collect()))
rc = big.repartition(8, "city")
print("repartition(8, city):", sorted(rc.groupBy(F.spark_partition_id()).count().rdd.map(lambda x: x[1]).collect()))
print("coalesce(2):", sorted(big.coalesce(2).groupBy(F.spark_partition_id()).count().rdd.map(lambda x: x[1]).collect()))

print("== 5) coalesce(1) before a heavy step")
run("heavy UDF-free calc, 4 partitions", lambda: big.select(F.sha2(F.col("order_id").cast("string"), 256).alias("h")).write.format("noop").mode("overwrite").save())
run("same after coalesce(1)", lambda: big.coalesce(1).select(F.sha2(F.col("order_id").cast("string"), 256).alias("h")).write.format("noop").mode("overwrite").save())
run("same after repartition(1)", lambda: big.repartition(1).select(F.sha2(F.col("order_id").cast("string"), 256).alias("h")).write.format("noop").mode("overwrite").save())
