"""6.5 Arrays, maps, structs, JSON strings and VARIANT."""
import time, json, random
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master("local[4]").config("spark.sql.shuffle.partitions", "8").getOrCreate()
def short(e, n=200):
    return str(e).split("\n")[0][:n]
o = spark.createDataFrame([
    (9101, ["Thali", "Lassi"], [180, 60], {"spice": "medium", "cutlery": "no"}, ("Ravi", 4.8)),
    (9102, ["Dosa", "Idli", "Coffee"], [90, 60, 30], {"spice": "high"}, ("Asha", None)),
    (9103, [], [], None, None)],
    "order_id INT, dishes ARRAY<STRING>, prices ARRAY<INT>, notes MAP<STRING,STRING>, rider STRUCT<name: STRING, rating: DOUBLE>")

print("== 1) arrays")
o.select("order_id", F.size("dishes").alias("n"), F.array_contains("dishes", "Dosa").alias("has_dosa"),
         F.transform("prices", lambda p: p * 105 / 100).alias("with_gst"),
         F.filter("prices", lambda p: p >= 60).alias("p60"),
         F.aggregate("prices", F.lit(0), lambda acc, p: acc + p).alias("total"),
         F.arrays_zip("dishes", "prices").alias("zipped")).show(truncate=False)

print("== 2) explode vs explode_outer vs posexplode")
print("explode      :", o.select(F.explode("dishes")).count(), "rows")
print("explode_outer:", o.select(F.explode_outer("dishes")).count(), "rows")
o.select("order_id", F.posexplode("dishes").alias("pos", "dish")).show()

print("== 3) maps and structs")
o.select("order_id", F.col("notes")["spice"].alias("spice"), F.map_keys("notes").alias("keys"),
         "rider.name", F.col("rider.rating").alias("rating")).show()

print("== 4) JSON strings: from_json, schema_of_json, to_json")
raw = spark.createDataFrame([('{"order_id": 1, "items": [{"dish": "Thali", "qty": 2}], "tip": 20}',),
                             ('{"order_id": 2, "items": [], "coupon": {"code": "FEST20", "pct": 20}}',),
                             ('{"order_id": "3", "items": "none"}',)], "payload STRING")
print("schema_of_json (row 1):", raw.select(F.schema_of_json(F.lit(raw.first().payload))).first()[0])
sch = "order_id INT, items ARRAY<STRUCT<dish: STRING, qty: INT>>, tip INT, coupon STRUCT<code: STRING, pct: INT>"
raw.select(F.from_json("payload", sch).alias("j")).select("j.order_id", "j.items", "j.tip", "j.coupon.code").show(truncate=False)
print(raw.select(F.to_json(F.struct(F.lit(9).alias("id"), F.array(F.lit("a"), F.lit("b")).alias("tags")))).first()[0])

print("== 5) VARIANT")
v = raw.select(F.parse_json("payload").alias("v"))
v.printSchema()
v.select(F.variant_get("v", "$.order_id", "int").alias("order_id"), F.variant_get("v", "$.items[0].dish", "string").alias("dish0"),
         F.variant_get("v", "$.coupon.code", "string").alias("coupon"), F.schema_of_variant("v").alias("schema")).show(truncate=False)
try:
    v.select(F.variant_get("v", "$.items", "array<struct<dish string, qty int>>")).collect()
except Exception as e:
    print("variant_get strict:", type(e).__name__, short(e, 170))
v.select(F.try_variant_get("v", "$.items", "array<struct<dish string, qty int>>").alias("items")).show(truncate=False)
spark.sql("SELECT parse_json('{\"a\": 1}'):a::int AS a, parse_json('{\"a\": {\"b\": [10, 20]}}'):a.b[1]::int AS b").show()

print("== 6) speed: 1M JSON strings, one field")
random.seed(1)
rows = [(json.dumps({"order_id": i, "city": random.choice(["Pune", "Delhi", "Mumbai"]), "amount": random.randint(50, 900),
                     "items": [{"dish": "Thali", "qty": 1}], "meta": {"app": "android", "v": "8.2"}}),) for i in range(1_000_000)]
j = spark.createDataFrame(rows, "payload STRING").repartition(4).cache(); j.count()
tests = [
    ("get_json_object", lambda: j.select(F.sum(F.get_json_object("payload", "$.amount").cast("int"))).first()[0]),
    ("from_json (schema)", lambda: j.select(F.sum(F.from_json("payload", "amount INT").amount)).first()[0]),
    ("parse_json + variant_get", lambda: j.select(F.sum(F.variant_get(F.parse_json("payload"), "$.amount", "int"))).first()[0]),
]
for label, f in tests:
    f(); t = time.time(); s = f(); print(f"{label:26}: sum {s}, {time.time()-t:.2f} s")
vt = j.select(F.parse_json("payload").alias("v")).cache(); vt.count()
f = lambda: vt.select(F.sum(F.variant_get("v", "$.amount", "int"))).first()[0]
f(); t = time.time(); s = f(); print(f"{'variant_get on stored VARIANT':26}: sum {s}, {time.time()-t:.2f} s")
