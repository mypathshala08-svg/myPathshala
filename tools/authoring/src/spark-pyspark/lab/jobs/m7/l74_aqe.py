"""7.4 Adaptive Query Execution: coalescing, join switching, skew."""
import time, json, urllib.request, re
from pyspark.sql import SparkSession, functions as F
spark = (SparkSession.builder.master("local[4]").config("spark.driver.memory", "3g").getOrCreate())
sc = spark.sparkContext
def stages():
    return json.load(urllib.request.urlopen(f"{sc.uiWebUrl}/api/v1/applications/{sc.applicationId}/stages"))
def run(label, f):
    b = {s["stageId"] for s in stages()}
    t = time.time(); f(); el = time.time() - t
    new = [s for s in stages() if s["stageId"] not in b and s["status"] == "COMPLETE"]
    tasks = sum(s["numTasks"] for s in new)
    print(f"{label:34}: {el:5.2f} s, stages {len(new)}, tasks {tasks}")
def final_plan(df):
    df.collect()
    return df._jdf.queryExecution().executedPlan().toString()
o = spark.read.parquet("/root/lab/spark/data/orders_big")
print("adaptive.enabled:", spark.conf.get("spark.sql.adaptive.enabled"), "| shuffle.partitions:", spark.conf.get("spark.sql.shuffle.partitions"))

print("== 1) coalescing shuffle partitions")
q = lambda: o.groupBy("city").agg(F.sum("amount")).collect()
for aqe in ("false", "true"):
    spark.conf.set("spark.sql.adaptive.enabled", aqe); q()
    run(f"groupBy city, AQE {aqe}", q)
spark.conf.set("spark.sql.adaptive.enabled", "true")
d = o.groupBy("city").agg(F.sum("amount"))
p = final_plan(d)
print([l.strip() for l in p.splitlines() if "AQEShuffleRead" in l or "isFinalPlan" in l][:2])

print("== 2) switching to a broadcast join at runtime")
c = spark.read.csv("/root/lab/spark/data/tiffingo/customers.csv", header=True, inferSchema=True).drop("city")
big_side = o.groupBy("customer_id").agg(F.sum("amount").alias("spent"))          # unknown size before running
small_after = c.where("plan = 'Gold' AND state = 'KA'")                          # tiny after filter
j = o.join(small_after.hint("no_broadcast_hash") if False else small_after, "customer_id")
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)       # static planner cannot broadcast
spark.conf.set("spark.sql.adaptive.autoBroadcastJoinThreshold", "10485760")   # AQE may, using runtime sizes
for aqe in ("false", "true"):
    spark.conf.set("spark.sql.adaptive.enabled", aqe)
    jj = o.join(c.where("plan = 'Gold' AND state = 'KA'"), "customer_id").groupBy("plan").count()
    p = final_plan(jj)
    strat = sorted({w for l in p.splitlines() for w in re.findall(r"(BroadcastHashJoin|SortMergeJoin|ShuffledHashJoin)", l)})
    jj.collect(); t = time.time(); jj.collect()
    print(f"AQE {aqe:5}: {strat}, {time.time()-t:.2f} s")
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "10485760")
spark.conf.set("spark.sql.adaptive.enabled", "true")

print("== 3) a skewed join")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "8m")
spark.conf.set("spark.sql.adaptive.advisoryPartitionSizeInBytes", "4m")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "3")
spark.conf.set("spark.sql.adaptive.autoBroadcastJoinThreshold", "-1")      # force a sort-merge join
skew = o.withColumn("rest_id", F.when(F.rand(7) < 0.6, F.lit(1)).otherwise((F.rand(8) * 2000).cast("int") + 2).cast("long"))
rests = spark.range(1, 2002).withColumnRenamed("id", "rest_id").withColumn("rname", F.concat(F.lit("R"), F.col("rest_id")))
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)
print("top key share:", skew.where("rest_id = 1").count() / 5_000_000)
for label, conf in (("AQE off", {"spark.sql.adaptive.enabled": "false"}),
                    ("AQE on, skewJoin off", {"spark.sql.adaptive.enabled": "true", "spark.sql.adaptive.skewJoin.enabled": "false"}),
                    ("AQE on, skewJoin on", {"spark.sql.adaptive.enabled": "true", "spark.sql.adaptive.skewJoin.enabled": "true"})):
    for k, v in conf.items():
        spark.conf.set(k, v)
    f = lambda: skew.join(rests, "rest_id").agg(F.sum("amount")).collect()
    f(); run(label, f)
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
sj = skew.join(rests, "rest_id").agg(F.sum("amount"))
p = final_plan(sj)
print([l.strip()[:110] for l in p.splitlines() if "skew" in l.lower()][:3])
