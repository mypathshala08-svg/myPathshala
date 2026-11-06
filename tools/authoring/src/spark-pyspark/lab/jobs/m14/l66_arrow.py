import time
import pyarrow as pa, pyarrow.compute as pc, pandas as pd
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.functions import udf, pandas_udf, arrow_udf
spark = SparkSession.builder.master("local[2]").appName("l66").config("spark.ui.showConsoleProgress", "false").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
df = spark.range(3_000_000).select((F.col("id") % 500 + 50).cast("double").alias("amount")).cache(); df.count()
def gst_py(a): return a * 1.05
gst_udf = udf(gst_py, "double")
@pandas_udf("double")
def gst_pandas(a: pd.Series) -> pd.Series: return a * 1.05
@arrow_udf("double")
def gst_arrow(a: pa.Array) -> pa.Array: return pc.multiply(a, 1.05)
print("== 1) the same rule (amount * 1.05) four ways, 3,000,000 rows, sum of results")
def run(name, col):
    t = time.time(); s = df.select(col.alias("x")).agg(F.round(F.sum("x"), 0)).first()[0]; print(f"  {name:28s} {time.time()-t:5.2f} s  sum {s:,.0f}")
print("  spark.sql.execution.pythonUDF.arrow.enabled =", spark.conf.get("spark.sql.execution.pythonUDF.arrow.enabled"))
for c in [gst_arrow("amount"), gst_pandas("amount"), gst_udf("amount")]: df.select(c.alias("x")).agg(F.sum("x")).first()   # warm-up: start Python workers
run("built-in column * 1.05", F.col("amount") * 1.05)
run("@arrow_udf (pyarrow)", gst_arrow("amount"))
run("@pandas_udf", gst_pandas("amount"))
run("@udf (default settings)", gst_udf("amount"))
run("@udf useArrow=False (pickle)", udf(gst_py, "double", useArrow=False)("amount"))
print("== 2) arrow_udf is new in Spark 4.1; its function receives a", end=" ")
@arrow_udf("string")
def kind(a: pa.Array) -> pa.Array:
    print_type.append(type(a).__name__); return pa.array([type(a).__name__] * len(a))
print_type = []
print(spark.range(3).select(kind(F.col("id"))).first()[0])
print("== 3) groupBy().applyInArrow: one pyarrow Table per group")
def stats(t: pa.Table) -> pa.Table:
    return pa.table({"band": [t.column("band")[0].as_py()], "rows": [t.num_rows], "avg": [round(pc.mean(t.column("amount")).as_py(), 1)]})
(df.limit(10000).withColumn("band", F.when(F.col("amount") > 300, "big").otherwise("small"))
   .groupBy("band").applyInArrow(stats, "band string, rows long, avg double").orderBy("band").show())
spark.stop()
