"""Narrow vs wide on the cluster: groupByKey vs reduceByKey, repartition vs coalesce, partitioners."""
import time
from operator import add
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("tiffingo-rdd-shuffle").getOrCreate()
sc = spark.sparkContext
def label(s): sc.setJobDescription(s)

# 2,000,000 (customer_id, amount) pairs in 8 partitions
pairs = sc.parallelize(range(2_000_000), 8).map(lambda i: (i % 2000, (i * 7919) % 900 + 60))

label("1 narrow: map + filter")
t = time.time(); n = pairs.filter(lambda kv: kv[1] > 500).map(lambda kv: kv[1] * 1.05).count()
print(f"narrow map+filter : {n} rows, {time.time()-t:.1f} s")

label("2 wide: groupByKey().mapValues(sum)")
t = time.time(); g = pairs.groupByKey().mapValues(sum).collect()
print(f"groupByKey        : {len(g)} keys, {time.time()-t:.1f} s")

label("3 wide: reduceByKey(add)")
t = time.time(); r = pairs.reduceByKey(add).collect()
print(f"reduceByKey       : {len(r)} keys, {time.time()-t:.1f} s, same result: {sorted(g) == sorted(r)}")

label("4 repartition(2)")
print("repartition(2) partitions:", pairs.repartition(2).getNumPartitions(), "->", pairs.repartition(2).count())
label("5 coalesce(2)")
print("coalesce(2)    partitions:", pairs.coalesce(2).getNumPartitions(), "->", pairs.coalesce(2).count())

label("6 join without a shared partitioner")
totals = pairs.reduceByKey(add)
names = sc.parallelize([(c, f"cust{c}") for c in range(2000)], 4)
print("join A:", totals.join(names).count(), "| partitioner of totals:", totals.partitioner is not None)
label("7 join with a shared partitioner")
part_totals = pairs.reduceByKey(add, 8).cache(); part_totals.count()
part_names = names.partitionBy(8).cache(); part_names.count()
label("7b join of co-partitioned RDDs")
print("join B:", part_totals.join(part_names).count())
label("8 mapValues keeps the partitioner, map loses it")
print("mapValues partitioner kept:", part_totals.mapValues(lambda v: v * 2).partitioner is not None,
      "| map partitioner kept:", part_totals.map(lambda kv: (kv[0], kv[1] * 2)).partitioner is not None)
label("9 print inside foreach (goes to executor logs)")
sc.parallelize(["poha", "idli", "dosa"], 2).foreach(lambda x: print("EXECUTOR SAYS:", x))
print("driver: foreach finished")
spark.stop()
