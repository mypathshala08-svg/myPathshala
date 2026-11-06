"""Laziness and lineage in RDDs."""
from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local[2]").getOrCreate()
sc = spark.sparkContext
lines = sc.textFile("/root/lab/spark/data/tiffingo/reviews")

print("1) A bug that waits for an action")
bad = lines.map(lambda l: len(l) / 0)
print("   defined bad RDD, no error yet:", bad)
try:
    bad.count()
except Exception as e:
    m = str(e); i = m.find("ZeroDivisionError")
    print("   at count():", m[i:i + 40].strip())

print("\n2) The lineage (DAG) of a word count")
counts = (lines.flatMap(lambda l: l.split())
               .map(lambda w: (w, 1))
               .reduceByKey(lambda a, b: a + b)
               .filter(lambda kv: kv[1] > 5000))
print(counts.toDebugString().decode())

print("3) Every action recomputes the lineage")
calls = sc.accumulator(0)
def tokenize(l):
    calls.add(1)
    return l.split()
words = lines.flatMap(tokenize)
words.count(); words.distinct().count()
print("   tokenize() calls for 2 actions, no cache:", calls.value, "(24,000 lines x 2)")
calls.value = 0
words_c = lines.flatMap(tokenize).cache()
words_c.count(); words_c.distinct().count()
print("   tokenize() calls for 2 actions, cached  :", calls.value)
print("   storage level:", words_c.getStorageLevel())
spark.stop()
