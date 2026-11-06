"""6.3 Window functions."""
import time
from pyspark.sql import SparkSession, functions as F, Window as W
spark = SparkSession.builder.master("local[4]").config("spark.sql.shuffle.partitions", "8").getOrCreate()
d = spark.createDataFrame([
    ("Pune", "2026-11-01", 450), ("Pune", "2026-11-02", 380), ("Pune", "2026-11-02", 380), ("Pune", "2026-11-03", 520),
    ("Delhi", "2026-11-01", 300), ("Delhi", "2026-11-02", 610), ("Delhi", "2026-11-03", 610)],
    "city STRING, day STRING, revenue INT")

print("== 1) ranking with ties")
w = W.partitionBy("city").orderBy(F.desc("revenue"))
d.select("city", "day", "revenue", F.row_number().over(w).alias("row_number"), F.rank().over(w).alias("rank"),
         F.dense_rank().over(w).alias("dense_rank")).orderBy("city", "row_number").show()

print("== 2) lag and lead")
w2 = W.partitionBy("city").orderBy("day")
d.select("city", "day", "revenue", F.lag("revenue").over(w2).alias("prev"),
         (F.col("revenue") - F.lag("revenue").over(w2)).alias("change"), F.lead("day").over(w2).alias("next_day")).orderBy("city", "day").show()

print("== 3) running total: default frame vs rowsBetween")
run_default = F.sum("revenue").over(W.partitionBy("city").orderBy("day"))
run_rows = F.sum("revenue").over(W.partitionBy("city").orderBy("day").rowsBetween(W.unboundedPreceding, W.currentRow))
d.where("city='Pune'").select("day", "revenue", run_default.alias("default_frame"), run_rows.alias("rows_frame")).orderBy("day").show()

print("== 4) moving average and share of total")
d.select("city", "day", "revenue",
         F.round(F.avg("revenue").over(W.partitionBy("city").orderBy("day").rowsBetween(-1, 0)), 1).alias("avg_2"),
         F.round(F.col("revenue") / F.sum("revenue").over(W.partitionBy("city")) * 100, 1).alias("pct_city")).orderBy("city", "day").show()

print("== 5) top 2 orders per city on 5M rows")
o = spark.read.parquet("/root/lab/spark/data/orders_big")
t = time.time()
top = (o.withColumn("rn", F.row_number().over(W.partitionBy("city").orderBy(F.desc("amount"), "order_id")))
        .where("rn <= 2").select("city", "order_id", "amount"))
top.orderBy("city", F.desc("amount")).show(6)
print(f"{time.time()-t:.1f} s")
top.explain()

print("== 6) a window without partitionBy")
t = time.time()
r = o.withColumn("global_rank", F.row_number().over(W.orderBy(F.desc("amount"), "order_id")))
print("partitions before:", o.rdd.getNumPartitions(), "| after:", r.rdd.getNumPartitions())
r.write.format("noop").mode("overwrite").save()
print(f"global row_number over 5M rows: {time.time()-t:.1f} s")
t = time.time()
o.withColumn("city_rank", F.row_number().over(W.partitionBy("city").orderBy(F.desc("amount"), "order_id"))).write.format("noop").mode("overwrite").save()
print(f"row_number per city: {time.time()-t:.1f} s")
