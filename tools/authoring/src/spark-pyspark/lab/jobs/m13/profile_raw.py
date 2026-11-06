"""13.1 Profile the raw landing data before designing the pipeline."""
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master("local[4]").config("spark.ui.showConsoleProgress", "false").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
R = "/root/lab/spark/data/m13/landing"
o = spark.read.option("header", True).csv(f"{R}/orders")          # everything as string first
c = spark.read.option("header", True).csv(f"{R}/customers")
r = spark.read.json(f"{R}/restaurants")
print("== 1) sizes and schemas")
print("orders rows:", o.count(), "| files:", len(o.inputFiles()), "| customers rows:", c.count(), "| restaurants rows:", r.count())
o.printSchema()
print("== 2) keys: duplicates and orphans")
print("duplicate order_id rows:", o.count() - o.select("order_id").distinct().count())
print("duplicate customer_id rows:", c.count() - c.select("customer_id").distinct().count())
orph = o.join(c.select("customer_id").distinct(), "customer_id", "left_anti").count()
print("orders whose customer_id is not in customers:", orph)
print("== 3) bad values")
amt = F.col("amount").try_cast("int")   # Spark 4: try_cast instead of a failing cast
o.select(F.sum(amt.isNull().cast("int")).alias("amount_not_a_number"),
         F.sum((amt < 0).cast("int")).alias("amount_negative"),
         F.min(amt).alias("min_amount"), F.max(amt).alias("max_amount")).show()
o.filter(amt.isNull()).groupBy("amount").count().orderBy("amount").show()
c.select(F.sum((F.col("phone").try_cast("bigint").isNull()).cast("int")).alias("phone_invalid")).show()
try:
    o.select(F.col("amount").cast("int")).agg(F.sum("amount")).collect()
except Exception as e:
    m = str(e); print("plain CAST under ANSI ->", m[m.find("["):m.find("]") + 1])
print("== 4) distribution and skew")
o.groupBy("status").count().orderBy(F.desc("count")).show()
top = o.groupBy("rest_id").count().orderBy(F.desc("count")).limit(3).collect()
print("top restaurants by orders:", [(x.rest_id, x["count"]) for x in top], "| share of #1:", round(top[0]["count"] / o.count() * 100, 1), "%")
o.groupBy(F.to_date("order_ts").alias("day")).count().orderBy("day").show(3)
