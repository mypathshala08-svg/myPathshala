"""4.6 collect, toPandas and Arrow."""
import time, tracemalloc, resource
import pandas as pd, numpy as np
from pyspark.sql import SparkSession, functions as F
spark = (SparkSession.builder.master("local[2]")
         .config("spark.driver.memory", "2g").getOrCreate())
def short(e):
    return str(e).split("\n")[0][:200]
big = spark.read.parquet("/root/lab/spark/data/orders_big")

print("== 1) defaults")
for k in ("spark.sql.execution.arrow.pyspark.enabled", "spark.sql.execution.arrow.pyspark.fallback.enabled",
          "spark.sql.execution.arrow.maxRecordsPerBatch"):
    print(f"{k:52}: {spark.conf.get(k)}")
print(f"{'spark.driver.maxResultSize':52}: {spark.sparkContext.getConf().get('spark.driver.maxResultSize', '(not set: 1g)')}")

print("== 2) the ways to bring rows to the driver")
d = big.orderBy("order_id")
print("first()  :", d.first())
print("head(2)  :", len(d.head(2)), "| take(2):", len(d.take(2)), "| tail(1):", d.tail(1)[0].order_id)
print("collect():", type(d.limit(3).collect()).__name__, "of", type(d.limit(3).collect()[0]).__name__)
it = big.toLocalIterator()
print("toLocalIterator first:", next(it).order_id)

print("== 3) collect vs toPandas, 1M rows")
m = big.limit(1_000_000).cache(); m.count()
t = time.time(); rows = m.collect(); print(f"collect()           : {time.time()-t:5.2f} s, {len(rows):,} Row objects")
del rows
for arrow in ("false", "true"):
    spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", arrow)
    t = time.time(); pdf = m.toPandas(); dt_ = time.time() - t
    print(f"toPandas arrow={arrow:5}: {dt_:5.2f} s, shape {pdf.shape}, {pdf.memory_usage(deep=True).sum()/2**20:.0f} MiB in pandas")
t = time.time(); tbl = m.toArrow(); print(f"toArrow()           : {time.time()-t:5.2f} s, {tbl.num_rows:,} rows, {tbl.nbytes/2**20:.0f} MiB")
print("pandas dtypes (arrow):", dict(pdf.dtypes.astype(str)))

print("== 4) types change on the way: nulls in int columns")
n = spark.createDataFrame([(1, 450), (2, None)], "id INT, amount INT")
for arrow in ("false", "true"):
    spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", arrow)
    p = n.toPandas()
    print(f"arrow={arrow:5}: amount dtype {p.amount.dtype}, values {p.amount.tolist()}")

print("== 5) pandas -> Spark")
pdf = pd.DataFrame({"id": np.arange(1_000_000), "amount": np.random.default_rng(1).integers(50, 900, 1_000_000)})
for arrow in ("false", "true"):
    spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", arrow)
    t = time.time(); s = spark.createDataFrame(pdf); s.count()
    print(f"createDataFrame(pandas) arrow={arrow:5}: {time.time()-t:5.2f} s")

print("== 6) maxResultSize protects the driver")
spark.stop()
spark = (SparkSession.builder.master("local[2]").config("spark.driver.maxResultSize", "50m").getOrCreate())
big = spark.read.parquet("/root/lab/spark/data/orders_big")
try:
    t = time.time(); r = big.collect(); print("collected", len(r))
except Exception as e:
    msg = str(e)
    i = msg.find("Total size")
    print(f"collect() of 5M rows failed after {time.time()-t:.1f} s:")
    print("  ", msg[i:i+170].split("\n")[0] if i >= 0 else short(e))
print("aggregate first, then collect:", big.groupBy("city").agg(F.sum("amount").alias("rev")).orderBy("city").toPandas().shape)
