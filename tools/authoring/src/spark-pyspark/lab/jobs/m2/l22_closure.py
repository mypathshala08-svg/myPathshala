"""The closure trap: updating a driver variable inside foreach."""
from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local[2]").getOrCreate()
sc = spark.sparkContext
amounts = sc.parallelize([530, 210, 480, 990, 120, 340], 3)

counter = 0
def add(x):
    global counter
    counter += x
amounts.foreach(add)
print("driver variable after foreach:", counter)

acc = sc.accumulator(0)
amounts.foreach(lambda x: acc.add(x))
print("accumulator after foreach    :", acc.value)

printed = amounts.foreach(lambda x: print("executor prints", x))
print("foreach returned:", printed, "(the prints went to executor stdout, not here on a cluster)")

setups = sc.accumulator(0)
def per_element(x):
    setups.add(1)                 # e.g. open a DB connection for every element
    return x * 2
def per_partition(it):
    setups.add(1)                 # once per partition
    return (x * 2 for x in it)
big = sc.parallelize(range(100_000), 4)
big.map(per_element).count();        print("map           -> setup calls:", setups.value)
setups.value = 0
big.mapPartitions(per_partition).count(); print("mapPartitions -> setup calls:", setups.value)
spark.stop()
