"""One engine, many APIs: the same TiffinGo orders through five Spark components."""
import time
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master("local[2]").appName("components").getOrCreate()
orders = spark.read.parquet("/root/lab/spark/data/orders_big").where("status = 'DELIVERED'")

print("1) Spark SQL")
orders.createOrReplaceTempView("orders")
spark.sql("SELECT city, COUNT(*) AS orders FROM orders GROUP BY city ORDER BY orders DESC LIMIT 3").show()

print("2) DataFrame API")
orders.groupBy("city").agg(F.round(F.avg("amount"), 2).alias("avg_amount")).orderBy("city").show(3)

print("3) pandas API on Spark")
import pyspark.pandas as ps
pdf = orders.pandas_api()
print(pdf.groupby("city")["amount"].sum().sort_values(ascending=False).head(3))

print("\n4) MLlib")
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.clustering import KMeans
sample = orders.sample(fraction=0.01, seed=1).select("amount")
vec = VectorAssembler(inputCols=["amount"], outputCol="features").transform(sample)
model = KMeans(k=3, seed=1).fit(vec)
print("order-size clusters (centres):", sorted(round(float(c[0]), 1) for c in model.clusterCenters()))

print("\n5) Structured Streaming")
q = (spark.readStream.format("rate").option("rowsPerSecond", 5).load()
     .writeStream.format("memory").queryName("ticks").start())
time.sleep(6); q.stop()
print("rows received in ~6 s:", spark.sql("SELECT COUNT(*) FROM ticks").first()[0])
spark.stop()
