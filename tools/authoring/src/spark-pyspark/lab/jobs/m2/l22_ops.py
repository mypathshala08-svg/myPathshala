"""RDD transformations and actions on TiffinGo order_items.txt"""
import os, shutil
from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local[2]").getOrCreate()
sc = spark.sparkContext
lines = sc.textFile("/root/lab/spark/data/tiffingo/order_items.txt")       # 5,000 lines

print("== TRANSFORMATIONS ==")
parts = lines.map(lambda l: l.split("|"))
print("map       :", parts.first())
dishes = lines.flatMap(lambda l: l.split("|")[1].split(","))
print("flatMap   :", dishes.take(5), "| elements:", dishes.count())
spicy = lines.filter(lambda l: "spice:hot" in l)
print("filter    :", spicy.count(), "orders asked for hot")
menu = dishes.distinct()
print("distinct  :", menu.count(), "different dishes")
both = sc.parallelize(["Poha", "Idli"]).union(sc.parallelize(["Idli", "Dosa"]))
print("union     :", both.collect(), "(duplicates kept)")
print("sample    :", lines.sample(False, 0.001, seed=7).count(), "lines (about 0.1%)")
print("mapPartitions:", lines.mapPartitions(lambda it: [sum(1 for _ in it)]).collect(), "lines per partition")

print("\n== ACTIONS ==")
amounts = sc.parallelize([530, 210, 480, 990, 120, 340], 3)
print("collect   :", amounts.collect())
print("count     :", amounts.count(), "| first:", amounts.first(), "| take(2):", amounts.take(2))
print("top(2)    :", amounts.top(2), "| takeOrdered(2):", amounts.takeOrdered(2))
print("reduce    :", amounts.reduce(lambda a, b: a + b))
print("fold      :", amounts.fold(0, lambda a, b: a + b))
print("aggregate :", amounts.aggregate((0, 0), lambda acc, x: (acc[0] + x, acc[1] + 1), lambda a, b: (a[0] + b[0], a[1] + b[1])), "(sum, count)")
print("countByValue:", sorted(dishes.countByValue().items(), key=lambda kv: -kv[1])[:3])
out = "/root/lab/spark/data/out_menu"
shutil.rmtree(out, ignore_errors=True)
menu.saveAsTextFile(out)
print("saveAsTextFile:", sorted(os.listdir(out)))
spark.stop()
