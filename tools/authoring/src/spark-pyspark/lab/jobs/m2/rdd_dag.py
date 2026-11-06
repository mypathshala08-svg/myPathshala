"""Word count DAG on the cluster: two actions, then cache."""
from operator import add
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("tiffingo-rdd-dag").getOrCreate()
sc = spark.sparkContext
lines = sc.textFile("/data/tiffingo/reviews")
counts = (lines.flatMap(lambda l: l.split()).map(lambda w: (w, 1)).reduceByKey(add))
sc.setJobDescription("A: top words (no cache)")
print(counts.takeOrdered(3, key=lambda kv: -kv[1]))
sc.setJobDescription("B: count() again, no cache")
print(counts.count())
counts.cache()
sc.setJobDescription("C: count after cache() - fills the cache")
print(counts.count())
sc.setJobDescription("D: filter on the cached RDD")
print(counts.filter(lambda kv: kv[1] > 5000).count())
spark.stop()
