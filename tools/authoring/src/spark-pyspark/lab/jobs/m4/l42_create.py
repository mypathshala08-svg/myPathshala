"""4.2 Creating DataFrames and schemas."""
import time, json, urllib.request, datetime as dt
import pandas as pd
from pyspark.sql import SparkSession, Row, functions as F
from pyspark.sql.types import *
spark = SparkSession.builder.master("local[2]").getOrCreate()
sc = spark.sparkContext
def jobs():
    return len(json.load(urllib.request.urlopen(f"{sc.uiWebUrl}/api/v1/applications/{sc.applicationId}/jobs")))
def short(e):
    return str(e).split("\n")[0][:170]

print("== 1) list of tuples, column names only")
df = spark.createDataFrame([(1, "Idli", 60.0), (2, "Dosa", 90.5)], ["id", "dish", "price"])
print(df.dtypes)

print("== 2) Row objects / dicts / pandas / RDD / range")
print("Row   :", spark.createDataFrame([Row(id=1, dish="Idli", veg=True)]).dtypes)
print("dict  :", spark.createDataFrame([{"id": 1, "dish": "Idli", "on": dt.date(2026, 11, 4)}]).dtypes)
print("pandas:", spark.createDataFrame(pd.DataFrame({"id": [1, 2], "price": [60.0, 90.5]})).dtypes)
print("RDD   :", sc.parallelize([(1, "a")]).toDF(["id", "code"]).dtypes)
print("range :", spark.range(0, 10, 2).dtypes, spark.range(0, 10, 2).count(), "rows")

print("== 3) inference problems")
for name, data in [("int then float", [(1,), (2.5,)]), ("int then string", [(1,), ("two",)]),
                   ("all None", [(None,), (None,)])]:
    try:
        d = spark.createDataFrame(data, ["v"])
        print(f"{name:16}: {d.dtypes} -> {[r.v for r in d.collect()]}")
    except Exception as e:
        print(f"{name:16}: {type(e).__name__}: {short(e)}")

print("== 4) DDL string schema")
ddl = "order_id INT, city STRING, amount DECIMAL(10,2), order_ts TIMESTAMP"
from decimal import Decimal
for v in (450, 450.75, Decimal("450.75")):
    try:
        d = spark.createDataFrame([(1, "Pune", v, dt.datetime(2026, 11, 4, 20, 15))], ddl)
        print(f"{type(v).__name__:8} -> OK", d.collect()[0].amount)
    except Exception as e:
        print(f"{type(v).__name__:8} -> {type(e).__name__}: {short(e)}")
d.printSchema()

print("== 5) StructType with nullable=False")
schema = StructType([StructField("order_id", IntegerType(), nullable=False),
                     StructField("city", StringType(), True)])
try:
    spark.createDataFrame([(1, "Pune"), (None, "Delhi")], schema).show()
except Exception as e:
    print("None in non-nullable:", type(e).__name__, short(e))
try:
    spark.createDataFrame([("x", "Pune")], schema).show()
except Exception as e:
    print("wrong type         :", type(e).__name__, short(e))

print("== 6) nested types")
nested = StructType([
    StructField("restaurant_id", IntegerType()),
    StructField("tags", ArrayType(StringType())),
    StructField("contact", StructType([StructField("phone", StringType()), StructField("email", StringType())])),
    StructField("prices", MapType(StringType(), IntegerType()))])
n = spark.createDataFrame([(2, ["late-night", "jain"], ("+91-1", "k@t.in"), {"thali": 180, "dosa": 90})], nested)
n.printSchema()
n.select("restaurant_id", n.tags[0].alias("tag0"), "contact.email", n.prices["thali"].alias("thali")).show()

print("== 7) schema as JSON and DDL")
js = n.schema.json()
print("json chars:", len(js), "|", js[:90], "...")
back = StructType.fromJson(json.loads(js))
print("round trip equal:", back == n.schema)
print("simpleString:", n.schema.simpleString())
print("DDL via spark.sql:", spark.createDataFrame([], n.schema)._jdf.schema().toDDL())

print("== 8) empty DataFrame with a schema")
e = spark.createDataFrame([], "id INT, city STRING")
print(e.count(), e.dtypes)

print("== 9) reading CSV: inferSchema vs explicit schema (2M rows)")
path = "/root/lab/spark/data/big_csv"
for label, kw in [("no schema", {}), ("inferSchema", {"inferSchema": True}),
                  ("explicit schema", {"schema": None})]:
    j0 = jobs(); t = time.time()
    if label == "explicit schema":
        kw = {"schema": big_schema}
    r = spark.read.options(header=True).csv(path, **kw)
    t1 = time.time() - t; j1 = jobs() - j0
    r.agg(F.count("*")).collect()
    print(f"{label:16}: read() {t1:4.1f} s, jobs at read: {j1} | types {[x[1] for x in r.dtypes][:4]}")
    if label == "inferSchema":
        big_schema = r.schema

print("== 10) samplingRatio")
t = time.time()
r = spark.read.options(header=True, inferSchema=True, samplingRatio=0.01).csv(path)
print(f"inferSchema with samplingRatio=0.01: {time.time()-t:.1f} s, same types: {r.schema == big_schema}")
