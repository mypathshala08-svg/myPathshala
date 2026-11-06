"""8.2 Join strategies."""
import sys; sys.path.insert(0, "/root/lab/spark/jobs/m8")
from common import mk
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master("local[4]").config("spark.driver.memory", "3g").config("spark.sql.adaptive.enabled","false").config("spark.driver.maxResultSize","64m").getOrCreate()
stages, run = mk(spark)
o = spark.read.parquet("/root/lab/spark/data/orders_big")
cust = spark.range(1, 4001).select(F.col("id").cast("int").alias("customer_id"), (F.col("id") % 5).alias("tier"))
print("default autoBroadcastJoinThreshold:", spark.conf.get("spark.sql.autoBroadcastJoinThreshold"))
def strat(df):
    p = df._jdf.queryExecution().executedPlan().toString()
    for k in ("BroadcastHashJoin","SortMergeJoin","ShuffledHashJoin","BroadcastNestedLoopJoin","CartesianProduct"):
        if k in p: return k
sink = lambda df: (lambda: df.write.format("noop").mode("overwrite").save())
print("== 1) auto choice")
j = o.join(cust, "customer_id")
print("small dim (4000 rows) ->", strat(j))
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)
print("threshold -1 ->", strat(o.join(cust, "customer_id")))
print("== 2) hints (threshold -1, so only hint decides)")
for h in ("broadcast","merge","shuffle_hash","shuffle_replicate_nl"):
    d = o.join(cust.hint(h), "customer_id")
    print(f"hint {h:21} -> {strat(d)}")
for h in ("broadcast","merge","shuffle_hash"):
    d = o.join(cust.hint(h), "customer_id"); sink(d)(); run(f"join with {h}", sink(d))
print("== 3) exchanges in plan")
for h in ("broadcast","merge"):
    p = o.join(cust.hint(h), "customer_id")._jdf.queryExecution().executedPlan().toString()
    print(h, "-> Exchange hashpartitioning:", p.count("Exchange hashpartitioning"), "| BroadcastExchange:", p.count("BroadcastExchange"))
print("== 4) forcing broadcast of a BIG side (5M rows)")
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)
o2 = o.select("order_id", "amount")
run("broadcast 5M-row side", sink(o.join(F.broadcast(o2), "order_id")))
run("sort-merge same join", sink(o.join(o2, "order_id")))
print("== 5) bucketed tables: join without shuffle")
spark.sql("DROP TABLE IF EXISTS ob"); spark.sql("DROP TABLE IF EXISTS cb")
o.write.bucketBy(16, "customer_id").sortBy("customer_id").mode("overwrite").saveAsTable("ob")
cust.write.bucketBy(16, "customer_id").sortBy("customer_id").mode("overwrite").saveAsTable("cb")
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)
b = spark.table("ob").join(spark.table("cb"), "customer_id")
p = b._jdf.queryExecution().executedPlan().toString()
print("bucketed join:", strat(b), "| Exchange count:", p.count("Exchange"))
nb = o.join(cust, "customer_id"); p2 = nb._jdf.queryExecution().executedPlan().toString()
print("plain join:", strat(nb), "| Exchange count:", p2.count("Exchange"))
sink(b)(); run("bucketed SMJ", sink(b)); sink(nb)(); run("plain SMJ", sink(nb))
