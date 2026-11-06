"""Accumulators: where they are exact, and where they double count."""
from pyspark import AccumulatorParam, TaskContext
from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local[2, 3]").getOrCreate()      # 2 cores, up to 3 attempts per task
sc = spark.sparkContext
lines = sc.textFile("/root/lab/spark/data/tiffingo/orders.csv").filter(lambda l: not l.startswith("order_id"))

bad = sc.accumulator(0)
def parse(l):
    f = l.split(",")
    if not f[5].isdigit():
        bad.add(1)
        return None
    return int(f[5])
amounts = lines.map(parse)
amounts.count(); amounts.filter(lambda x: x is not None).count()
print("1) inside a transformation, 2 actions, no cache:", bad.value, "(real bad rows: 1)")

bad.value = 0
amounts = lines.map(parse).cache()
amounts.count(); amounts.filter(lambda x: x is not None).count()
print("2) same, with cache():", bad.value)

bad.value = 0
lines.foreach(lambda l: bad.add(0 if l.split(",")[5].isdigit() else 1))
print("3) inside an action (foreach):", bad.value)

seen = sc.accumulator(0)
def flaky(x):
    seen.add(1)
    if TaskContext.get().partitionId() == 0 and TaskContext.get().attemptNumber() == 0:
        raise RuntimeError("simulated executor hiccup")
    return x
n = sc.parallelize(range(1000), 2).map(flaky).count()
print("4) task 0 failed once and was retried: count =", n, "| accumulator =", seen.value)

class CounterParam(AccumulatorParam):
    def zero(self, v): return {}
    def addInPlace(self, a, b):
        for k, v in b.items(): a[k] = a.get(k, 0) + v
        return a
reasons = sc.accumulator({}, CounterParam())
def check(l):
    f = l.split(",")
    if not f[5].isdigit(): reasons.add({"amount not a number": 1})
    if "/" in f[4]: reasons.add({"timestamp format": 1})
    if f[7] == "CANCELLED": reasons.add({"cancelled": 1})
lines.foreach(check)
print("5) custom accumulator (dict of reasons):", reasons.value)
spark.stop()
