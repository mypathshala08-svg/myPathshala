"""Broadcast variables vs closures, on the cluster."""
import time, random
from operator import add
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.appName("tiffingo-broadcast").getOrCreate()
sc = spark.sparkContext
R = random.Random(1)
plans = {cid: R.choice(["Gold", "Silver", "Basic", "Basic"]) for cid in range(400_000)}   # big lookup table
orders = sc.parallelize(range(2_000_000), 16).map(lambda i: (i % 400_000, (i * 7919) % 900 + 60))

sc.setJobDescription("A: lookup dict captured in the closure (3 jobs)")
t = time.time()
for _ in range(3):
    res_a = orders.map(lambda kv: (plans[kv[0]], kv[1])).reduceByKey(add).collect()
ta = time.time() - t

b = sc.broadcast(plans)
sc.setJobDescription("B: same lookup through a broadcast variable (3 jobs)")
t = time.time()
for _ in range(3):
    res_b = orders.map(lambda kv: (b.value[kv[0]], kv[1])).reduceByKey(add).collect()
tb = time.time() - t
print(f"closure  : {ta:5.1f} s for 3 jobs  {sorted(res_a)}")
print(f"broadcast: {tb:5.1f} s for 3 jobs  same result: {sorted(res_a) == sorted(res_b)}")

b.unpersist()
print("after unpersist, still usable:", orders.map(lambda kv: b.value[kv[0]]).first())
b.destroy()
try:
    orders.map(lambda kv: b.value[kv[0]]).first()
except Exception as e:
    print("after destroy:", type(e).__name__, str(e).split("\n")[0][:120])

print("\n-- DataFrame joins with a small table --")
big = spark.read.parquet("/data/orders_big")
cust = spark.read.csv("/data/tiffingo/customers.csv", header=True, inferSchema=True).withColumn("customer_id", F.col("customer_id") + 2000)
sc.setJobDescription("C: join, automatic broadcast")
t = time.time(); n1 = big.join(cust, "customer_id").groupBy("plan").count().collect(); t1 = time.time() - t
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
sc.setJobDescription("D: join, broadcast disabled")
t = time.time(); n2 = big.join(cust, "customer_id").groupBy("plan").count().collect(); t2 = time.time() - t
print(f"broadcast hash join : {t1:4.1f} s  {sorted((r.plan, r['count']) for r in n1)}")
print(f"sort-merge join     : {t2:4.1f} s  same: {sorted(n1) == sorted(n2)}")
spark.conf.unset("spark.sql.autoBroadcastJoinThreshold")
big.join(F.broadcast(cust), "customer_id").explain()
spark.stop()
