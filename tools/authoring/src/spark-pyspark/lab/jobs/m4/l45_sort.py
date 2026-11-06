"""4.5 Sorting, distinct, limit and union."""
import time, json, urllib.request
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master("local[2]").config("spark.sql.shuffle.partitions", "8").getOrCreate()
sc = spark.sparkContext
def stages():
    a = json.load(urllib.request.urlopen(f"{sc.uiWebUrl}/api/v1/applications/{sc.applicationId}/stages"))
    return a
def shuffled(before):
    now = stages(); ids = {s["stageId"] for s in before}
    new = [s for s in now if s["stageId"] not in ids]
    return len(new), round(sum(s["shuffleWriteBytes"] for s in new) / 2**20, 1)
def plan_ops(df):
    p = df._jdf.queryExecution().executedPlan().toString()
    return [l.strip("+-: ").split(" ")[0].split("(")[0] for l in p.splitlines() if l.strip()]
def short(e):
    return str(e).split("\n")[0][:180]
big = spark.read.parquet("/root/lab/spark/data/orders_big")
print("orders_big rows:", big.count(), "| partitions:", big.rdd.getNumPartitions())

print("== 1) orderBy vs sort vs sortWithinPartitions (write to noop)")
big.write.format("noop").mode("overwrite").save()   # warm-up: plain scan
for label, d in [("orderBy(amount desc)", big.orderBy(F.desc("amount"))),
                 ("sort('amount')", big.sort("amount")),
                 ("sortWithinPartitions", big.sortWithinPartitions(F.desc("amount")))]:
    b = stages(); t = time.time()
    d.write.format("noop").mode("overwrite").save()
    n, mb = shuffled(b)
    print(f"{label:22}: {time.time()-t:4.1f} s, new stages {n}, shuffle write {mb} MiB")
print("orderBy plan :", plan_ops(big.orderBy("amount"))[:4])
print("within plan  :", plan_ops(big.sortWithinPartitions("amount"))[:3])

print("== 2) nulls in sort order")
d = spark.createDataFrame([(1, 300), (2, None), (3, 120)], "id INT, amount INT")
print("asc            :", [r.amount for r in d.orderBy("amount").collect()])
print("desc           :", [r.amount for r in d.orderBy(F.desc("amount")).collect()])
print("asc_nulls_last :", [r.amount for r in d.orderBy(F.asc_nulls_last("amount")).collect()])
print("multi-column   :", [tuple(r) for r in spark.createDataFrame([("Pune", 5), ("Delhi", 9), ("Pune", 7)], "city STRING, n INT").orderBy("city", F.desc("n")).collect()])

print("== 3) limit")
b = stages(); t = time.time()
top = big.orderBy(F.desc("amount")).limit(5)
top.collect()
print(f"orderBy+limit(5): {time.time()-t:.1f} s, shuffle {shuffled(b)[1]} MiB, plan {plan_ops(top)[:2]}")
b = stages(); t = time.time()
big.limit(5).collect()
print(f"limit(5) only   : {time.time()-t:.2f} s, plan {plan_ops(big.limit(5))[:3]}")

print("== 4) distinct and countDistinct")
for label, f in [("distinct().count()", lambda: big.select("customer_id").distinct().count()),
                 ("countDistinct", lambda: big.select(F.countDistinct("customer_id")).first()[0]),
                 ("approx_count_distinct", lambda: big.select(F.approx_count_distinct("customer_id")).first()[0])]:
    t = time.time(); v = f(); print(f"{label:22}: {v} in {time.time()-t:.2f} s")

print("== 5) union is by position")
a = spark.createDataFrame([(1, "Pune", 450)], "order_id INT, city STRING, amount INT")
b2 = spark.createDataFrame([(2, 380, "Delhi")], "order_id INT, amount INT, city STRING")
try:
    a.union(b2).show()
except Exception as e:
    print("union:", type(e).__name__, short(e))
s1 = spark.createDataFrame([(1, "Pune", "UPI")], "order_id INT, city STRING, payment STRING")
s2 = spark.createDataFrame([(2, "Card", "Delhi")], "order_id INT, payment STRING, city STRING")
print("same types, different order -> no error:")
s1.union(s2).show()
s1.unionByName(s2).show()
a.unionByName(b2).show()
c = spark.createDataFrame([(3, "Pune")], "order_id INT, city STRING")
try:
    a.unionByName(c).show()
except Exception as e:
    print("unionByName missing col:", type(e).__name__, short(e))
a.unionByName(c, allowMissingColumns=True).show()

print("== 6) union keeps duplicates; partitions add up")
x = spark.range(0, 6, 1, 2); y = spark.range(3, 9, 1, 3)
u = x.union(y)
print("union rows:", u.count(), "| distinct:", u.distinct().count(), "| partitions:", u.rdd.getNumPartitions(), "| plan:", plan_ops(u)[:2])
print("intersect:", sorted(r.id for r in x.intersect(y).collect()), "| subtract:", sorted(r.id for r in x.subtract(y).collect()))
z = spark.createDataFrame([(1,), (1,), (2,)], "id INT"); w = spark.createDataFrame([(1,)], "id INT")
print("subtract :", [r.id for r in z.subtract(w).collect()], "| exceptAll:", sorted(r.id for r in z.exceptAll(w).collect()))
