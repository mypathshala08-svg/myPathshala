"""Word count and pair-RDD operations on TiffinGo reviews and orders."""
import time
from operator import add
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master("local[2]").getOrCreate()
sc = spark.sparkContext
D = "/root/lab/spark/data/tiffingo"
reviews = sc.textFile(f"{D}/reviews")

print("== WORD COUNT ==")
stop = {"was", "and", "for", "it", "too"}
counts = (reviews.flatMap(lambda line: line.lower().split())
                 .filter(lambda w: w not in stop)
                 .map(lambda w: (w, 1))
                 .reduceByKey(add))
print("distinct words:", counts.count())
print("top 8:", counts.takeOrdered(8, key=lambda kv: -kv[1]))
complaints = counts.filter(lambda kv: kv[0] in {"cold", "late", "oily", "spilled"}).sortByKey().collect()
print("complaint words (sortByKey):", complaints)

print("\n== THE SAME WITH DATAFRAMES ==")
df = spark.read.text(f"{D}/reviews")
top_df = (df.select(F.explode(F.split(F.lower("value"), " ")).alias("w"))
            .where(~F.col("w").isin(*stop)).groupBy("w").count()
            .orderBy(F.desc("count")).limit(3).collect())
print("top 3:", [(r.w, r["count"]) for r in top_df])

print("\n== PAIR RDD OPERATIONS ON ORDERS ==")
rows = (sc.textFile(f"{D}/orders.csv").filter(lambda l: not l.startswith("order_id"))
          .map(lambda l: l.split(",")).filter(lambda f: f[5].isdigit()))
city_amt = rows.map(lambda f: (f[3], int(f[5])))                       # (city, amount)
print("first pairs   :", city_amt.take(2))
print("countByKey    :", sorted(city_amt.countByKey().items(), key=lambda kv: -kv[1])[:3])
sum_cnt = city_amt.aggregateByKey((0, 0), lambda a, v: (a[0] + v, a[1] + 1), lambda a, b: (a[0] + b[0], a[1] + b[1]))
avg = sum_cnt.mapValues(lambda s: round(s[0] / s[1], 2)).sortByKey()
print("aggregateByKey avg:", avg.take(3))
comb = city_amt.combineByKey(lambda v: (v, v), lambda c, v: (min(c[0], v), max(c[1], v)), lambda a, b: (min(a[0], b[0]), max(a[1], b[1])))
print("combineByKey (min,max):", sorted(comb.collect())[:3])

cust = (sc.textFile(f"{D}/customers.csv").filter(lambda l: not l.startswith("customer_id"))
          .map(lambda l: l.split(",")).map(lambda f: (f[0], f[5])))         # (customer_id, plan)
orders_by_cust = rows.map(lambda f: (f[1], int(f[5])))                   # (customer_id, amount)
joined = orders_by_cust.join(cust)                                       # (cid, (amount, plan))
plan_rev = joined.map(lambda kv: (kv[1][1], kv[1][0])).reduceByKey(add).sortBy(lambda kv: -kv[1])
print("join -> revenue by plan:", plan_rev.collect())
print("rows: orders", orders_by_cust.count(), "| joined", joined.count(),
      "| leftOuterJoin", orders_by_cust.leftOuterJoin(cust).count())
spark.stop()
