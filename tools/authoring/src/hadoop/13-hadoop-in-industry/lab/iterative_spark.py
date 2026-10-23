# iterative_spark.py: five passes over the same 140 MB (9 million orders).
# Pass k counts orders per item with amount >= threshold k. With cache(), only pass 1 reads HDFS.
import sys, time
from pyspark import StorageLevel
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("five passes (spark)").getOrCreate()
cache = sys.argv[2] == "cache"
orders = (spark.sparkContext.textFile(sys.argv[1])
          .map(lambda l: l.split(","))
          .filter(lambda f: f[0] != "order_id")
          .map(lambda f: (f[1], int(f[2]))))
if cache:
    orders = orders.persist(StorageLevel.MEMORY_AND_DISK)
total = time.time()
for k, threshold in enumerate([0, 18, 20, 25, 30], 1):
    t = time.time()
    counts = orders.filter(lambda p, th=threshold: p[1] >= th).map(lambda p: (p[0], 1)).reduceByKey(lambda a, b: a + b).collect()
    print(f"pass {k}: amount >= {threshold:2}: {sum(c for _, c in counts):>9,} orders, {time.time() - t:5.1f} s")
print(f"cache={cache}: 5 passes took {time.time() - total:.1f} s")
spark.stop()
