# item_revenue_spark.py: the same job as ItemRevenue.java (Lesson 8.1), in PySpark, twice:
# with the RDD API (map / reduceByKey, MapReduce thinking) and with DataFrames (SQL thinking).
import sys, time
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.appName("item revenue (spark)").getOrCreate()
path = sys.argv[1]

t = time.time()
rdd = (spark.sparkContext.textFile(path)
       .map(lambda line: line.split(","))
       .filter(lambda f: len(f) == 3 and f[0] != "order_id")
       .map(lambda f: (f[1], (1, int(f[2]))))                       # map: (item, (1, amount))
       .reduceByKey(lambda a, b: (a[0] + b[0], a[1] + b[1])))       # shuffle + reduce (with map-side combine)
for item, (n, total) in sorted(rdd.collect()):
    print(f"RDD  {item:9} {n:>8} {total:>10}")
print(f"RDD job took {time.time() - t:.1f} s, partitions: {rdd.getNumPartitions()}")

t = time.time()
df = spark.read.csv(path, header=True, inferSchema=True)
out = df.groupBy("item").agg(F.count("*").alias("orders"), F.sum("amount").alias("revenue")).orderBy("item")
out.show()
print(f"DataFrame job took {time.time() - t:.1f} s")
out.explain()
spark.stop()
