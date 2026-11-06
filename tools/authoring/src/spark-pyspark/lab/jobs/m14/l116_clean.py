import time, sys, io, contextlib, subprocess
sys.path.insert(0, "/root/lab/spark/jobs/m14/clean")
from pyspark.sql import SparkSession, functions as F
from transforms import only_valid, add_amount, revenue_by_city
spark = SparkSession.builder.master("local[2]").appName("l116").config("spark.ui.showConsoleProgress", "false").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
orders = spark.range(2_000_000).select(
    F.element_at(F.array(*[F.lit(c) for c in ["Mumbai", "Pune", "Delhi"]]), (F.col("id") % 3 + 1).cast("int")).alias("city"),
    F.element_at(F.array(*[F.lit(c) for c in ["idli", "dosa", "thali", "pizza"]]), (F.col("id") % 4 + 1).cast("int")).alias("item"),
    (F.col("id") % 4).cast("int").alias("qty"))
PRICES = {"idli": 45, "dosa": 90, "thali": 150}
print("== 1) one readable chain of small functions")
print("  orders.transform(only_valid).transform(add_amount(PRICES)).transform(revenue_by_city)")
orders.transform(only_valid).transform(add_amount(PRICES)).transform(revenue_by_city).show()
def plan_nodes(df):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): df.explain(mode="extended")
    an = buf.getvalue().split("== Analyzed Logical Plan ==")[1].split("== Optimized")[0]
    return an.count("Project [")
print("== 2) 20 x withColumn vs one select (analysed plan size, time to build the DataFrame)")
t = time.time(); d1 = orders
for i in range(20): d1 = d1.withColumn(f"c{i}", F.col("qty") + i)
t1 = time.time() - t
t = time.time(); d2 = orders.select("*", *[(F.col("qty") + i).alias(f"c{i}") for i in range(20)]); t2 = time.time() - t
print(f"  withColumn x20 : {plan_nodes(d1):2d} Project nodes, built in {t1*1000:5.0f} ms")
print(f"  one select     : {plan_nodes(d2):2d} Project nodes, built in {t2*1000:5.0f} ms")
print(f"  withColumns    : {plan_nodes(orders.withColumns({f'c{i}': F.col('qty') + i for i in range(20)})):2d} Project nodes")
print("== 3) renaming many columns")
cols = [c.upper() for c in orders.columns]
print("  chained withColumnRenamed:", plan_nodes(orders.withColumnRenamed("city", "CITY").withColumnRenamed("item", "ITEM").withColumnRenamed("qty", "QTY")), "Project nodes")
print("  orders.toDF(*cols)       :", plan_nodes(orders.toDF(*cols)), "Project node ->", orders.toDF(*cols).columns)
print("== 4) 'is there any bad order?' count() > 0 vs isEmpty()")
bad = orders.filter("qty = 0")
t = time.time(); a = bad.count() > 0; ta = time.time() - t
t = time.time(); b = not bad.isEmpty(); tb = time.time() - t
print(f"  count() > 0 : {a}  {ta:5.2f} s (scans everything)")
print(f"  isEmpty()   : {b}  {tb:5.2f} s (stops at the first row)")
spark.stop()
print("== 5) unit tests for the transforms (pytest)")
r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "/root/lab/spark/jobs/m14/clean/test_transforms.py"], capture_output=True, text=True, cwd="/root/lab/spark/jobs/m14/clean")
print("  " + [l for l in r.stdout.splitlines() if "passed" in l or "failed" in l][-1])
