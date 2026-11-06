"""7.3 Catalyst and explain."""
import time
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master("local[4]").config("spark.sql.shuffle.partitions", "8").getOrCreate()
o = spark.read.parquet("/root/lab/spark/data/orders_big")
c = spark.read.csv("/root/lab/spark/data/tiffingo/customers.csv", header=True, inferSchema=True).drop("city")

q = (o.join(c, "customer_id")
      .withColumn("gst", F.col("amount") * F.lit(5) / F.lit(100))
      .where((F.col("plan") == "Gold") & (F.col("status") == "DELIVERED"))
      .where(F.col("amount") > F.lit(1) + F.lit(1) + F.lit(798))
      .select("order_id", "name", "amount", "gst"))

print("== 1) explain(extended): four plans")
q.explain(mode="extended")

print("== 2) explain(formatted)")
q.explain(mode="formatted")

print("== 3) explain(cost)")
o.where("city = 'Pune'").select("amount").explain(mode="cost")


print("== 5) whole-stage code generation")
s = o.where("amount > 800").agg(F.sum("amount"))
s.explain()
import io, contextlib
buf = io.StringIO()
spark.conf.set("spark.sql.adaptive.enabled", "false")      # show the static plan
s = o.where("amount > 800").agg(F.sum("amount"))
s.explain()
with contextlib.redirect_stdout(buf):
    s.explain(mode="codegen")
spark.conf.set("spark.sql.adaptive.enabled", "true")
lines = buf.getvalue().splitlines()
print(lines[0]); print([l for l in lines if "processNext" in l][:1])
print("generated code lines:", len(lines))

print("== 6) the same query written badly and well")
bad = (o.withColumn("x", F.col("amount") * 2).join(c, "customer_id").where(F.col("city") == "Pune").select("order_id", "name"))
good = (o.where(F.col("city") == "Pune").select("order_id", "customer_id").join(c.select("customer_id", "name"), "customer_id").select("order_id", "name"))
import re
norm = lambda d: re.sub(r"#\d+L?", "", d._jdf.queryExecution().optimizedPlan().toString())
print("optimized plans identical:", norm(bad) == norm(good))
for label, d in (("bad", bad), ("good", good)):
    d.count(); t = time.time(); d.count(); print(f"{label}: {time.time()-t:.2f} s")

print("== 7) what Catalyst cannot see through")
u = F.udf(lambda a: a > 800, "boolean")
o.where(u("amount")).select("order_id").explain()
