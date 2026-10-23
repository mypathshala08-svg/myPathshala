# check.py: acceptance tests. The pipeline's answers must equal truth.json from the generator.
import json
from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.appName("capstone-check").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
B = "hdfs://namenode/capstone"
t = json.load(open("capstone_raw/truth.json"))
o = spark.read.parquet(f"{B}/silver/orders")
s = o.agg(F.count("*"), F.sum("amount"), F.countDistinct("order_id"), F.sum(F.col("late").cast("int")),
          F.sum(F.col("unknown_item").cast("int")), F.sum("undercharged")).first()
recon = spark.read.parquet(f"{B}/gold/upi_recon").agg(F.sum("gateway_success"), F.sum("refunds"), F.sum("gap")).first()
daily = spark.read.parquet(f"{B}/gold/daily_college").agg(F.sum("revenue")).first()[0]
tests = [
    ("orders = truth", s[0], t["clean_orders"]),
    ("revenue = truth", s[1], t["revenue"]),
    ("order_id is unique", s[2], s[0]),
    ("late orders kept", s[3], t["late"]),
    ("unknown items flagged", s[4], t["unknown_item"]),
    ("undercharged rupees", s[5], t["undercharged"]),
    ("quarantined lines", spark.read.json(f"{B}/quarantine/orders").count(), t["malformed"]),
    ("gold revenue = silver", daily, s[1]),
    ("UPI net = truth", recon[0] + recon[1], t["upi_net"]),
    ("UPI gap = unconfirmed", recon[2], t["upi_unconfirmed"]),
]
for name, got, want in tests:
    print(f"{'PASS' if got == want else 'FAIL'}  {name:<24} got {got:>10,}  expected {want:>10,}")
print(f"{sum(g == w for _, g, w in tests)}/{len(tests)} checks passed")
