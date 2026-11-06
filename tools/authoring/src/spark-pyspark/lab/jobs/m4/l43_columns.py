"""4.3 Working with columns."""
import time
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master("local[2]").getOrCreate()
def short(e):
    return str(e).split("\n")[0][:190]
schema = "order_id INT, customer_id INT, restaurant_id INT, city STRING, order_ts STRING, amount STRING, payment STRING, status STRING"
o = spark.read.csv("/root/lab/spark/data/tiffingo/orders.csv", header=True, schema=schema)

print("== 1) four ways to name a column")
a = o.select("city", o.city, o["city"], F.col("city"))
print(a.columns)
print(type(F.col("city")).__name__, F.col("amount") * 2)

print("== 2) select with expressions")
o.select("order_id", F.upper("city").alias("CITY"), (F.col("order_id") % 7).alias("bucket")).show(3)
o.selectExpr("order_id", "upper(city) AS CITY", "order_id % 7 AS bucket").show(3)

print("== 3) cast under ANSI")
print("ansi enabled:", spark.conf.get("spark.sql.ansi.enabled"))
try:
    o.select(F.col("amount").cast("int")).agg(F.sum("amount")).show()
except Exception as e:
    print("cast  :", type(e).__name__, short(e))
print("try_cast:", o.select(F.col("amount").try_cast("int").alias("amt")).agg(F.sum("amt"), F.count("amt"), F.count("*")).collect()[0])
print("order_ts try_to_timestamp nulls:", o.select(F.try_to_timestamp("order_ts").alias("ts")).where("ts IS NULL").count())
print("bad ts value:", [r.order_ts for r in o.where(F.try_to_timestamp("order_ts").isNull()).select("order_ts").collect()])

print("== 4) withColumn, withColumns, rename, drop")
c = (o.withColumn("amount", F.col("amount").try_cast("int"))
      .withColumn("order_ts", F.try_to_timestamp("order_ts"))
      .withColumns({"gst": F.round(F.col("amount") * 0.05, 2), "hour": F.hour("order_ts")})
      .withColumnRenamed("payment", "pay_mode")
      .drop("restaurant_id", "no_such_column"))
c.printSchema()

print("== 5) when / otherwise")
c = c.withColumn("slot", F.when(F.col("hour") < 11, "breakfast")
                          .when(F.col("hour") < 16, "lunch")
                          .when(F.col("hour") < 22, "dinner")
                          .otherwise("late-night"))
c.groupBy("slot").count().orderBy("slot").show()

print("== 6) filter / where")
print(c.where((F.col("city") == "Pune") & (F.col("amount") > 500)).count(),
      c.filter("city = 'Pune' AND amount > 500").count())
try:
    c.where(F.col("city") == "Pune" & F.col("amount") > 500).count()
except Exception as e:
    print("no brackets:", type(e).__name__, short(e))
try:
    c.where((F.col("city") == "Pune") and (F.col("amount") > 500)).count()
except Exception as e:
    print("python and :", type(e).__name__, short(e))
print("isin:", c.where(F.col("city").isin("Pune", "Mumbai")).count(), "| like:", c.where(F.col("city").like("B%")).count())

print("== 7) a missing column")
try:
    c.select("ammount").show()
except Exception as e:
    print(type(e).__name__, short(e))

print("== 8) withColumn in a loop vs one select (300 new columns)")
base = spark.range(1000)
for label in ("withColumn loop", "withColumns (one call)", "select (one call)"):
    t = time.time()
    if label == "withColumn loop":
        d = base
        for i in range(300):
            d = d.withColumn(f"c{i}", F.col("id") + i)
    elif label.startswith("withColumns"):
        d = base.withColumns({f"c{i}": F.col("id") + i for i in range(300)})
    else:
        d = base.select("*", *[(F.col("id") + i).alias(f"c{i}") for i in range(300)])
    build = time.time() - t
    t = time.time(); d.count(); run = time.time() - t
    print(f"{label:24}: build {build:5.2f} s, count {run:4.2f} s, columns {len(d.columns)}")
