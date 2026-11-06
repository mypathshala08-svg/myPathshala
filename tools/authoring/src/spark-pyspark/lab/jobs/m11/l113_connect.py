"""11.3 Spark Connect: a thin client talking gRPC to a Spark server on sc://localhost:15002."""
import os, time, warnings, subprocess
warnings.filterwarnings("ignore")
t = time.time()
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.remote("sc://localhost:15002").getOrCreate()
print("== 1) a remote session")
print("session class:", type(spark).__module__ + "." + type(spark).__name__, "| server version:", spark.version, f"| connect + first query: {time.time()-t:.2f} s")
import glob
java_kids = 0
for st in glob.glob("/proc/[0-9]*/stat"):
    try:
        parts = open(st).read().split()
        if int(parts[3]) == os.getpid() and "java" in parts[1]: java_kids += 1
    except Exception: pass
print("JVM processes started by this Python client:", java_kids)
print("== 2) normal DataFrame code works")
o = spark.read.parquet("/root/lab/spark/data/orders_big")
t = time.time(); r = o.groupBy("city").agg(F.sum("amount").alias("revenue")).orderBy(F.desc("revenue")).limit(3).collect()
print([(x.city, x.revenue) for x in r], f"| {time.time()-t:.2f} s on the server")
print("== 3) what is not available")
for name, f in [("spark.sparkContext", lambda: spark.sparkContext), ("df.rdd", lambda: o.rdd)]:
    try:
        f(); print(name, "-> OK")
    except Exception as e:
        print(f"{name} -> {type(e).__name__}: {str(e).splitlines()[0][:110]}")
print("== 4) errors appear when the plan is analysed on the server")
bad = o.select("no_such_column")              # no error yet: only a plan was built on the client
print("built a DataFrame with a missing column: no error yet")
try:
    bad.columns
except Exception as e:
    m = str(e); print("on .columns ->", type(e).__name__, m[m.find("["):m.find("]") + 1])
print("== 5) sessions are isolated")
s2 = SparkSession.builder.remote("sc://localhost:15002").create()
spark.range(3).createOrReplaceTempView("my_view")
print("session 1 sees my_view:", spark.catalog.tableExists("my_view"), "| session 2 sees my_view:", s2.catalog.tableExists("my_view"))
print("session ids differ:", spark.session_id != s2.session_id)
print("== 6) Python UDFs run on the server side")
@F.udf("double")
def gst(a): return round(a * 1.05, 2)
print(spark.range(1, 4).select((F.col("id") * 100).alias("a")).select("a", gst("a").alias("with_gst")).collect())
s2.stop(); spark.stop()
