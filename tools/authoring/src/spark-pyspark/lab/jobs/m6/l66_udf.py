"""6.6 UDFs: Python, Arrow-optimized, pandas, SQL; cost and pitfalls."""
import time
import pandas as pd
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.functions import udf, pandas_udf
spark = SparkSession.builder.master("local[4]").config("spark.sql.shuffle.partitions", "8").getOrCreate()
def short(e, n=200):
    return str(e).split("\n")[0][:n]
o = spark.read.parquet("/root/lab/spark/data/orders_big").cache(); o.count()

print("== 1) defaults")
print("pythonUDF.arrow.enabled:", spark.conf.get("spark.sql.execution.pythonUDF.arrow.enabled"))

def band(a):
    return "high" if a >= 600 else "mid" if a >= 300 else "low"
plain = udf(band, "string", useArrow=False)
arrowed = udf(band, "string", useArrow=True)
@pandas_udf("string")
def band_pd(a: pd.Series) -> pd.Series:
    return pd.cut(a, [-1, 299, 599, 10**9], labels=["low", "mid", "high"]).astype(str)
builtin = F.when(F.col("amount") >= 600, "high").when(F.col("amount") >= 300, "mid").otherwise("low")

print("== 2) same result four ways, 5M rows")
for label, col in [("built-in when()", builtin), ("Python UDF (pickle)", plain(F.col("amount"))),
                   ("Python UDF (Arrow)", arrowed(F.col("amount"))), ("pandas UDF", band_pd(F.col("amount")))]:
    o.select(col.alias("b")).groupBy("b").count().collect()          # warm-up
    t = time.time(); r = sorted((x.b, x["count"]) for x in o.select(col.alias("b")).groupBy("b").count().collect())
    print(f"{label:20}: {time.time()-t:5.2f} s  {r}")

print("== 3) the plan: a black box")
o.where(plain(F.col("amount")) == "high").select("order_id").explain()
o.where(builtin == "high").select("order_id").explain()

print("== 4) a UDF blocks pushdown on Parquet")
o.unpersist()
path = "/root/lab/spark/data/orders_big"
p = spark.read.parquet(path)
upper_city = udf(lambda c: c.upper() if c else None, "string")
for label, q in (("built-in", p.where(F.upper("city") == "PUNE")), ("UDF", p.where(upper_city("city") == "PUNE")),
                 ("plain filter", p.where(F.col("city") == "Pune"))):
    plan = q._jdf.queryExecution().executedPlan().toString()
    m = [l for l in plan.split("\n") if "PushedFilters" in l]
    pf = m[0][m[0].find("PushedFilters"):][:70] if m else ""
    q.count(); t = time.time(); n = q.count()
    q = None
    print(f"{label:12}: {n} rows, {time.time()-t:.2f} s, {pf}")

print("== 5) None and errors inside a UDF")
d = spark.createDataFrame([(450,), (None,)], "amount INT")
try:
    d.select(plain("amount")).collect()
except Exception as e:
    m = str(e); i = m.find("TypeError")
    print("UDF on None:", m[i:i + 80] if i >= 0 else short(e))
safe = udf(lambda a: None if a is None else band(a), "string")
print("null-safe UDF:", [r[0] for r in d.select(safe("amount")).collect()])
for arrow in (False, True):
    wrong = udf(lambda a: a * 1.05, "int", useArrow=arrow)
    print(f"declared int, returned 472.5, useArrow={arrow}:", [r[0] for r in spark.createDataFrame([(450,)], "amount INT").select(wrong("amount")).collect()])

print("== 6) SQL UDF (Spark 4)")
spark.sql("CREATE OR REPLACE TEMPORARY FUNCTION gst(amount INT) RETURNS DOUBLE RETURN round(amount * 0.05, 2)")
spark.sql("SELECT gst(530) AS gst").show()
o.createOrReplaceTempView("orders")
q = spark.sql("SELECT sum(gst(amount)) FROM orders")
q.collect(); t = time.time(); print("sum(gst) over 5M:", q.first()[0], f"{time.time()-t:.2f} s")
o.createOrReplaceTempView("orders")
print("plan has a Python step:", "BatchEvalPython" in q._jdf.queryExecution().executedPlan().toString() or "ArrowEvalPython" in q._jdf.queryExecution().executedPlan().toString())

print("== 7) register a Python UDF for SQL")
spark.udf.register("band", band, "string")
spark.sql("SELECT band(amount) b, count(*) n FROM orders GROUP BY b ORDER BY b").show()
