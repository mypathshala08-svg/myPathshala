"""6.1 groupBy, agg, rollup/cube, pivot, unpivot."""
import time, json, urllib.request
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master("local[4]").config("spark.sql.shuffle.partitions", "8").getOrCreate()
sc = spark.sparkContext
def jobs():
    return len(json.load(urllib.request.urlopen(f"{sc.uiWebUrl}/api/v1/applications/{sc.applicationId}/jobs")))
o = spark.read.parquet("/root/lab/spark/data/orders_big")

print("== 1) groupBy + several aggregates")
o.groupBy("city").agg(F.count("*").alias("orders"), F.sum("amount").alias("revenue"),
                      F.round(F.avg("amount"), 1).alias("avg"), F.countDistinct("customer_id").alias("customers"),
                      F.sum(F.when(F.col("status") == "CANCELLED", 1).otherwise(0)).alias("cancelled")).orderBy("city").show()

print("== 2) partial aggregation in the plan")
o.groupBy("city").agg(F.sum("amount")).explain()

print("== 3) null keys form their own group")
d = spark.createDataFrame([("Pune", 10), (None, 5), ("Pune", 1), (None, 2)], "city STRING, n INT")
d.groupBy("city").sum("n").orderBy("city").show()

print("== 4) rollup and cube")
s = o.where("city IN ('Pune', 'Delhi') AND status IN ('DELIVERED', 'CANCELLED')")
s.rollup("city", "status").agg(F.count("*").alias("n")).orderBy(F.col("city").asc_nulls_last(), F.col("status").asc_nulls_last()).show()
print("cube rows:", s.cube("city", "status").count().count(), "| rollup rows:", s.rollup("city", "status").count().count())

print("== 5) pivot with and without values")
for label, f in [("no values", lambda: o.groupBy("city").pivot("status").agg(F.sum("amount"))),
                 ("values given", lambda: o.groupBy("city").pivot("status", ["DELIVERED", "CANCELLED", "REFUNDED"]).agg(F.sum("amount")))]:
    j0 = jobs(); t = time.time(); p = f(); jb = jobs() - j0
    p.orderBy("city").collect(); el = time.time() - t
    print(f"{label:12}: jobs while building {jb}, total {el:.2f} s, columns {p.columns}")
p.orderBy("city").show(4)

print("== 6) pivot limit")
w = o.groupBy("city").pivot("customer_id").count()
print("pivot on customer_id:", len(w.columns), "columns")
try:
    o.limit(20000).groupBy("city").pivot("order_id").count().collect()
except Exception as e:
    print(type(e).__name__, str(e).split("\n")[0][:200])

print("== 7) unpivot back")
wide = o.groupBy("city").pivot("status", ["DELIVERED", "CANCELLED", "REFUNDED"]).agg(F.sum("amount"))
long = wide.unpivot(["city"], ["DELIVERED", "CANCELLED", "REFUNDED"], "status", "revenue")
long.orderBy("city", "status").show(6)
print("rows:", long.count())

print("== 8) collect_list / collect_set")
o.where("customer_id = 1806").groupBy("customer_id").agg(F.count("*").alias("n"), F.collect_set("city").alias("cities"),
    F.slice(F.sort_array(F.collect_list("amount"), asc=False), 1, 3).alias("top3")).show(truncate=False)
