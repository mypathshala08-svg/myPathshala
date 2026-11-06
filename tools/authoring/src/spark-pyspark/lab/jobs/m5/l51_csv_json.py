"""5.1 CSV and JSON: options, corrupt records, multiLine, nested JSON, compression and splits."""
import time, json, urllib.request
from pyspark.sql import SparkSession, functions as F
spark = (SparkSession.builder.master("local[4]")
         .config("spark.sql.files.maxPartitionBytes", "32m").getOrCreate())
sc = spark.sparkContext
D = "/root/lab/spark/data/m5"
def short(e, n=170):
    return str(e).split("\n")[0][:n]
schema = "order_id INT, city STRING, amount INT, order_date DATE, review STRING"

print("== 1) defaults: header off, everything string")
spark.read.csv(f"{D}/partner_orders.csv").show(3)

print("== 2) header + schema, PERMISSIVE (default)")
p = spark.read.csv(f"{D}/partner_orders.csv", header=True, schema=schema)
p.show(truncate=28)
print("rows:", p.count())

print("== 3) keep the bad lines: _corrupt_record")
s2 = schema + ", _corrupt_record STRING"
p2 = spark.read.csv(f"{D}/partner_orders.csv", header=True, schema=s2).cache()
p2.select("order_id", "amount", "order_date", "_corrupt_record").show(truncate=40)
print("bad rows:", p2.where("_corrupt_record IS NOT NULL").count())

print("== 4) multiLine=true")
p3 = spark.read.csv(f"{D}/partner_orders.csv", header=True, schema=s2, multiLine=True, escape='"')
p3.select("order_id", "amount", "order_date", "review", "_corrupt_record").show(truncate=30)
print("rows:", p3.count())

print("== 5) DROPMALFORMED and FAILFAST")
opts = dict(header=True, multiLine=True, escape='"')
dm = spark.read.csv(f"{D}/partner_orders.csv", schema=schema, mode="DROPMALFORMED", **opts)
print("DROPMALFORMED count()          :", dm.count())
print("DROPMALFORMED all columns      :", len(dm.collect()))
try:
    spark.read.csv(f"{D}/partner_orders.csv", schema=schema, mode="FAILFAST", **opts).collect()
except Exception as e:
    m = str(e); i = m.find("[MALFORMED_RECORD_IN_PARSING")
    print("FAILFAST:", m[i:m.find("]", m.find("parsing:", i)) + 1] if i >= 0 else short(e))

print("== 5b) bad rows depend on the columns you read")
c = spark.read.csv(f"{D}/partner_orders.csv", schema=s2, **opts)
print("select order_id, city, _corrupt_record:", sum(r._corrupt_record is not None for r in c.select("order_id", "city", "_corrupt_record").collect()))
print("select all columns                   :", sum(r._corrupt_record is not None for r in c.collect()))
print("== 6) dateFormat")
d = spark.read.csv(f"{D}/partner_orders.csv", header=True, schema=s2, multiLine=True, escape='"', dateFormat="dd/MM/yyyy")
print([(r.order_id, str(r.order_date)) for r in d.where("order_id IN (9001, 9006)").collect()])

print("== 7) JSON lines")
j = spark.read.json(f"{D}/app_events.jsonl")
j.printSchema()
j.select("order_id", "city", F.size("items").alias("n_items"), "rider.name", "coupon").show()

print("== 8) a JSON array file without multiLine")
ja = spark.read.json(f"{D}/app_events_array.json")
print("columns:", ja.columns, "| rows:", ja.count())
ja2 = spark.read.json(f"{D}/app_events_array.json", multiLine=True)
print("multiLine=True columns:", ja2.columns, "| rows:", ja2.count())

print("== 9) explode nested items")
j.select("order_id", F.explode("items").alias("it")).select("order_id", "it.dish", "it.qty").show()

print("== 10) gzip is not splittable")
spark.read.parquet("/root/lab/spark/data/orders_big").write.format("noop").mode("overwrite").save()   # warm-up
for label, path in [("plain csv", f"{D}/big5m_csv"), ("csv.gz", f"{D}/big5m_gz")] * 2:
    df = spark.read.csv(path, header=True, schema="order_id INT, customer_id INT, city STRING, order_date DATE, amount INT, status STRING")
    t = time.time(); n = df.agg(F.sum("amount")).collect()[0][0]
    print(f"{label:10}: partitions {df.rdd.getNumPartitions():2}, sum {n}, {time.time()-t:.1f} s")

print("== 11) JSON inference reads everything")
spark.read.parquet("/root/lab/spark/data/orders_big").limit(1_000_000).write.mode("overwrite").json(f"{D}/orders_json")
for label, kw in [("infer", {}), ("schema", {"schema": "order_id BIGINT, customer_id INT, city STRING, order_date DATE, amount INT, status STRING"})]:
    t = time.time(); df = spark.read.json(f"{D}/orders_json", **kw); t1 = time.time() - t
    print(f"{label:6}: read() {t1:.1f} s | {df.dtypes[:3]}")
