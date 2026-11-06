"""12.2 Same three queries in pandas, Polars, DuckDB and PySpark. Usage: bench.py ENGINE DATASET"""
import sys, time, resource, warnings, glob; warnings.filterwarnings("ignore")
eng, ds = sys.argv[1], sys.argv[2]
P = {"5m": "/root/lab/spark/data/orders_big", "50m": "/root/lab/spark/data/m12/orders_50m"}[ds]
C = "/root/lab/spark/data/m12/customers"
files = sorted(glob.glob(P + "/*.parquet"))
T = {}
def tm(name, f):
    t = time.time(); r = f(); T[name] = time.time() - t; return r
t0 = time.time()
if eng == "pandas":
    import pandas as pd
    o = tm("load", lambda: pd.read_parquet(P)); c = pd.read_parquet(C)
    q1 = lambda: o.groupby("city", as_index=False)["amount"].sum()
    q2 = lambda: o.merge(c, on="customer_id").groupby("tier", as_index=False)["amount"].sum()
    q3 = lambda: o.sort_values("amount", ascending=False).groupby("city").head(3)
elif eng == "polars":
    import polars as pl
    o = pl.scan_parquet(files); c = pl.scan_parquet(C + "/*.parquet")
    T["load"] = 0.0
    q1 = lambda: o.group_by("city").agg(pl.col("amount").sum()).collect()
    q2 = lambda: o.join(c, on="customer_id").group_by("tier").agg(pl.col("amount").sum()).collect()
    q3 = lambda: o.sort("amount", descending=True).group_by("city").head(3).collect()
elif eng == "duckdb":
    import duckdb
    con = duckdb.connect(); T["load"] = 0.0
    q1 = lambda: con.sql(f"SELECT city, sum(amount) FROM '{P}/*.parquet' GROUP BY city").fetchall()
    q2 = lambda: con.sql(f"SELECT tier, sum(amount) FROM '{P}/*.parquet' o JOIN '{C}/*.parquet' c USING (customer_id) GROUP BY tier").fetchall()
    q3 = lambda: con.sql(f"SELECT * FROM '{P}/*.parquet' QUALIFY row_number() OVER (PARTITION BY city ORDER BY amount DESC) <= 3").fetchall()
elif eng == "pyspark":
    from pyspark.sql import SparkSession, functions as F, Window
    spark = tm("load", lambda: SparkSession.builder.master("local[4]").config("spark.driver.memory", "3g").config("spark.ui.showConsoleProgress", "false").getOrCreate())
    o = spark.read.parquet(P); c = spark.read.parquet(C)
    q1 = lambda: o.groupBy("city").agg(F.sum("amount")).collect()
    q2 = lambda: o.join(c, "customer_id").groupBy("tier").agg(F.sum("amount")).collect()
    q3 = lambda: o.withColumn("r", F.row_number().over(Window.partitionBy("city").orderBy(F.desc("amount")))).filter("r <= 3").collect()
for n, q in (("q1 groupBy", q1), ("q2 join+groupBy", q2), ("q3 top-3 per city", q3)):
    try:
        tm(n, q)
    except MemoryError:
        T[n] = float("nan")
rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
kids = 0
if eng == "pyspark":
    import os
    for st in glob.glob("/proc/[0-9]*/status"):
        try:
            txt = open(st).read()
            if "PPid:\t%d\n" % os.getpid() in txt and "java" in txt.split("\n")[0]:
                kids = int([l for l in txt.split("\n") if l.startswith("VmHWM")][0].split()[1]) / 1024
        except Exception: pass
print(f"{eng:8} {ds:4} | load/start {T['load']:5.1f} s | " + " | ".join(f"{k} {v:5.2f} s" for k, v in T.items() if k != "load") + f" | peak RSS {rss:6.0f} MB" + (f" (+JVM {kids:.0f} MB)" if eng == "pyspark" else ""))
