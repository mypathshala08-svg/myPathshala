# silver_gold.py: cleaned text -> silver Parquet (partitioned by day) -> gold KPI tables
import sys
from pyspark.sql import SparkSession, functions as F

spark = (SparkSession.builder.appName("capstone-silver-gold")
         .config("spark.sql.sources.partitionOverwriteMode", "dynamic")   # re-runs replace only their days
         .config("spark.sql.shuffle.partitions", "6").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")
B = "hdfs://namenode/capstone"
cols = ["status", "order_id", "dt", "ts", "college", "student_id", "item", "category", "qty", "amount",
        "pay_mode", "late", "unknown_item", "undercharged"]

schema = ", ".join(c + " STRING" for c in cols)          # read everything as text first, then cast
raw = spark.read.schema(schema).option("sep", "\t").csv(f"{B}/stage/clean")   # BAD rows fill 3 columns
orders = (raw.where("status = 'OK'").drop("status")
          .withColumn("ts", F.to_timestamp("ts")).withColumn("dt", F.to_date("dt"))
          .withColumn("qty", F.col("qty").cast("int")).withColumn("amount", F.col("amount").cast("int"))
          .withColumn("late", F.col("late") == "1").withColumn("unknown_item", F.col("unknown_item") == "1")
          .withColumn("undercharged", F.col("undercharged").cast("int")))
days = sys.argv[1:]                                    # optional: only these days (a backfill)
if days:
    orders = orders.where(F.col("dt").isin(days))
orders.write.mode("overwrite").partitionBy("dt").parquet(f"{B}/silver/orders")
raw.where("status = 'BAD'").select("order_id", "dt").toDF("file_day", "raw_line") \
   .write.mode("overwrite").json(f"{B}/quarantine/orders")

pay = spark.read.json(f"{B}/bronze/payments").withColumn("dt", F.to_date(F.substring("ts", 1, 10)))
pay.write.mode("overwrite").partitionBy("dt").parquet(f"{B}/silver/payments")

o = spark.read.parquet(f"{B}/silver/orders")
p = spark.read.parquet(f"{B}/silver/payments")
ok = p.where("status = 'SUCCESS'").select("order_id", F.col("amount").alias("paid"))
upi = o.where("pay_mode = 'UPI'").join(ok, "order_id", "left")          # every UPI order, paid or not
gold = {
  "daily_college": o.groupBy("dt", "college").agg(F.count("*").alias("orders"), F.sum("amount").alias("revenue")),
  "item_mix": o.groupBy("college", "item", "category").agg(F.count("*").alias("orders"), F.sum("amount").alias("revenue")),
  "hourly": o.groupBy(F.hour("ts").alias("hour")).agg(F.count("*").alias("orders")),
  "upi_recon": (o.where("pay_mode = 'UPI'").groupBy("college").agg(F.sum("amount").alias("pos_upi"))
                .join(p.join(o.select("order_id", "college"), "order_id").groupBy("college").agg(
                      F.sum(F.when(F.col("status") == "SUCCESS", F.col("amount")).otherwise(0)).alias("gateway_success"),
                      F.sum(F.when(F.col("status") == "REFUNDED", F.col("amount")).otherwise(0)).alias("refunds"),
                      F.sum(F.when(F.col("status") == "FAILED", 1).otherwise(0)).alias("failed_attempts")), "college")
                .withColumn("gap", F.col("pos_upi") - F.col("gateway_success"))),
  "upi_gaps": (upi.where("paid IS NULL").groupBy("dt", "college", F.hour("ts").alias("hour"))
               .agg(F.count("*").alias("orders"), F.sum("amount").alias("unconfirmed"))),
}
for name, df in gold.items():
    df.coalesce(1).write.mode("overwrite").parquet(f"{B}/gold/{name}")

print("== silver.orders ==")
o.agg(F.count("*").alias("orders"), F.sum("amount").alias("revenue"), F.countDistinct("dt").alias("days"),
      F.sum(F.col("late").cast("int")).alias("late"), F.sum(F.col("unknown_item").cast("int")).alias("unknown"),
      F.sum("undercharged").alias("undercharged")).show()
print("== gold.daily_college: month by canteen ==")
spark.read.parquet(f"{B}/gold/daily_college").groupBy("college").agg(F.sum("orders").alias("orders"),
      F.sum("revenue").alias("revenue")).orderBy(F.desc("revenue")).show()
print("== gold.upi_recon ==")
spark.read.parquet(f"{B}/gold/upi_recon").orderBy("college").show()
print("== gold.upi_gaps: UPI orders with no SUCCESS from the gateway ==")
spark.read.parquet(f"{B}/gold/upi_gaps").orderBy("dt", "college", "hour").show()
print("== gold.hourly: top 3 hours ==")
spark.read.parquet(f"{B}/gold/hourly").orderBy(F.desc("orders")).show(3)
print("== gold.item_mix: maggi and Panvel chai ==")
spark.read.parquet(f"{B}/gold/item_mix").where("item = 'maggi' or (college = 'PNL' and item = 'chai')").show()
