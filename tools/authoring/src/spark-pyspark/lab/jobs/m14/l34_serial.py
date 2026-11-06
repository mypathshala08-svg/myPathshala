import pickle, marshal, time, threading, sys
from pyspark import SparkContext, SparkConf
from pyspark.serializers import MarshalSerializer, CloudPickleSerializer
from pyspark.cloudpickle import dumps as cdumps
rows = [(i, "idli", 45.0) for i in range(200000)]
print("== 1) the same 200,000 Python tuples, three serializers (bytes / ms)")
for name, d, l in [("pickle", lambda o: pickle.dumps(o, 5), pickle.loads), ("marshal", marshal.dumps, marshal.loads)]:
    t = time.time(); b = d(rows); t1 = time.time(); l(b); t2 = time.time()
    print(f"  {name:8s} {len(b):>10,} bytes  dump {1000*(t1-t):5.0f} ms  load {1000*(t2-t1):5.0f} ms")
class Order:
    def __init__(self, i): self.i = i
try: marshal.dumps([Order(1)])
except ValueError as e: print("  marshal on a custom class:", type(e).__name__, "-", e)
print("== 2) functions: plain pickle vs cloudpickle (what PySpark uses for your code)")
tax = 1.05
f = lambda x: x * tax
try: pickle.dumps(f)
except Exception as e: print("  pickle.dumps(lambda):", type(e).__name__, str(e)[:70])
print("  cloudpickle.dumps(lambda):", len(cdumps(f)), "bytes (code + captured variable tax)")
big = {i: i * 2 for i in range(300000)}
g = lambda x: big.get(x, 0)
print("  lambda capturing a 300k-entry dict:", f"{len(cdumps(g)):,}", "bytes, shipped with EVERY task")
conf = SparkConf().setMaster("local[2]").setAppName("l34").set("spark.ui.showConsoleProgress", "false")
print("== 3) RDD serializer: CloudPickleSerializer (default) vs MarshalSerializer")
warm = SparkContext(conf=conf); warm.setLogLevel("ERROR"); warm.parallelize(range(1000)).count(); warm.stop()   # JVM warm-up, not timed
for name, ser in [("Marshal", MarshalSerializer()), ("CloudPickle (default)", CloudPickleSerializer()), ("Marshal (again)", MarshalSerializer())]:
    sc = SparkContext(conf=conf, serializer=ser); sc.setLogLevel("ERROR")
    sc.parallelize(range(1000), 8).count()
    t = time.time(); s = sc.parallelize(range(3_000_000), 8).map(lambda x: (x % 100, x)).reduceByKey(lambda a, b: a + b).count(); el = time.time() - t
    print(f"  {name:22s} {el:5.2f} s  (keys {s})  sc.serializer = {type(sc.serializer).__name__}")
    sc.stop()
print("== 4) a closure that cannot be serialized")
sc = SparkContext(conf=conf); sc.setLogLevel("ERROR")
lock = threading.Lock()
try:
    sc.parallelize([1, 2]).map(lambda x: (x, lock)).collect()
except Exception as e:
    msg = str(e).splitlines(); print("  ", next((l for l in msg if "pickle" in l.lower()), msg[0])[:140])
print("  fix: create the object inside the task (mapPartitions) or broadcast plain data")
print("== 5) broadcast instead of capturing big data")
bb = sc.broadcast(big)
h = lambda x: bb.value.get(x, 0)
print("  lambda using a broadcast:", len(cdumps(h)), "bytes per task; data sent once per executor")
print("  result:", sc.parallelize([1, 2, 3]).map(h).collect())
sc.stop()
from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local[2]").config("spark.ui.showConsoleProgress", "false").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
df = spark.range(2_000_000).selectExpr("id", "id * 1.5 AS amount", "concat('item-', id % 50) AS item")
print("== 6) DataFrame → pandas: pickled rows vs Arrow columns (2,000,000 rows)")
for arrow in ["false", "true"]:
    spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", arrow)
    t = time.time(); pdf = df.toPandas(); el = time.time() - t
    print(f"  arrow={arrow:5s} toPandas {el:5.2f} s  rows {len(pdf):,}")
spark.stop()
