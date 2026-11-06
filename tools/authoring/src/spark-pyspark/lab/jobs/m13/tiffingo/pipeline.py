"""TiffinGo capstone pipeline: landing -> silver -> gold, with data-quality gates."""
import sys, time, json
from pyspark.sql import SparkSession, functions as F
sys.path.insert(0, "/root/lab/spark/jobs/m13/tiffingo"); sys.path.insert(0, "/jobs/m13/tiffingo")
from transforms import ORDER_SCHEMA, clean_orders, clean_customers, daily_city_revenue, customer_features
BASE = sys.argv[1] if len(sys.argv) > 1 else "/root/lab/spark/data/m13"
spark = SparkSession.builder.appName("tiffingo-capstone").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
t0 = time.time(); m = {}
def step(name, f):
    t = time.time(); r = f(); m[name] = round(time.time() - t, 2); return r
raw_o = spark.read.option("header", True).schema(ORDER_SCHEMA).csv(f"{BASE}/landing/orders")
raw_c = spark.read.option("header", True).csv(f"{BASE}/landing/customers")
rest = spark.read.json(f"{BASE}/landing/restaurants")
valid, quar = clean_orders(raw_o)
customers = clean_customers(raw_c)
# silver
step("silver_orders", lambda: valid.repartition("order_date").write.mode("overwrite").partitionBy("order_date").parquet(f"{BASE}/silver/orders"))
step("quarantine", lambda: quar.write.mode("overwrite").parquet(f"{BASE}/quarantine/orders"))
step("silver_customers", lambda: customers.write.mode("overwrite").parquet(f"{BASE}/silver/customers"))
so = spark.read.parquet(f"{BASE}/silver/orders"); sc_ = spark.read.parquet(f"{BASE}/silver/customers"); q = spark.read.parquet(f"{BASE}/quarantine/orders")
# quality gates
raw_n, good_n, bad_n = raw_o.count(), so.count(), q.count()
checks = {
    "raw_rows": raw_n, "silver_rows": good_n, "quarantined": bad_n,
    "duplicates_removed": raw_n - bad_n - good_n,
    "quarantine_by_problem": {r.problem: r["count"] for r in q.groupBy("problem").count().collect()},
    "silver_null_amounts": so.filter("amount IS NULL").count(),
    "silver_unique_order_ids": so.select("order_id").distinct().count() == good_n,
    "quarantine_pct": round(bad_n / raw_n * 100, 2),
}
assert checks["silver_null_amounts"] == 0 and checks["silver_unique_order_ids"], "quality gate failed"
assert checks["quarantine_pct"] < 2.0, "too many bad rows: stop and alert"
# gold
step("gold_daily_city", lambda: daily_city_revenue(so, rest).write.mode("overwrite").parquet(f"{BASE}/gold/daily_city_revenue"))
as_of = so.agg(F.max("order_date")).first()[0]
step("gold_customer_features", lambda: customer_features(so, sc_, as_of).write.mode("overwrite").parquet(f"{BASE}/gold/customer_features"))
checks["silver_partitions"] = so.select("order_date").distinct().count()
checks["gold_daily_city_rows"] = spark.read.parquet(f"{BASE}/gold/daily_city_revenue").count()
checks["gold_customers"] = spark.read.parquet(f"{BASE}/gold/customer_features").count()
checks["step_seconds"] = m; checks["total_seconds"] = round(time.time() - t0, 1)
print(json.dumps(checks, indent=1, default=str))
spark.stop()
