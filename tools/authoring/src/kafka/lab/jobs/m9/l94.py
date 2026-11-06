import time
from pyspark.sql import SparkSession, functions as F, types as T
spark = SparkSession.builder.appName("kitchen-94").master("local[2]").config("spark.sql.shuffle.partitions", "2").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
print("== 1) Spark", spark.version, "reading topic orders-94 as a streaming DataFrame")
raw = (spark.readStream.format("kafka").option("kafka.bootstrap.servers", "k1:9092,k2:9092,k3:9092")
       .option("subscribe", "orders-94").option("startingOffsets", "earliest").load())
raw.printSchema()
schema = T.StructType([T.StructField("city", T.StringType()), T.StructField("item", T.StringType()),
                       T.StructField("amount", T.IntegerType()), T.StructField("ts", T.TimestampType())])
orders = raw.select(F.from_json(F.col("value").cast("string"), schema).alias("o"), "partition", "offset").select("o.*", "partition", "offset")
agg = (orders.withWatermark("ts", "1 minute")
       .groupBy(F.window("ts", "5 minutes"), "city").agg(F.count("*").alias("orders"), F.sum("amount").alias("revenue")))
q = (agg.writeStream.outputMode("update").format("memory").queryName("rev")
     .option("checkpointLocation", "/tmp/chk94").trigger(processingTime="3 seconds").start())
for i in range(12):
    time.sleep(3)
    if spark.table("rev").count() >= 3: break
print("== 2) 5-minute revenue per city (watermark 1 minute)")
spark.table("rev").select(F.date_format("window.start", "HH:mm").alias("from"), F.date_format("window.end", "HH:mm").alias("to"), "city", "orders", "revenue").orderBy("from", "city").show(truncate=False)
late = spark.createDataFrame([("Mumbai", '{"city":"Mumbai","item":"chai","amount":20,"ts":"2026-11-06T12:03:00"}'), ("Pune", '{"city":"Pune","item":"poha","amount":30,"ts":"2026-11-06T12:08:00"}')], ["key", "value"])
late.write.format("kafka").option("kafka.bootstrap.servers", "k1:9092").option("topic", "orders-94").save()
print("== 3) two more records: chai at 12:03 (behind the watermark) and poha at 12:08")
time.sleep(10)
spark.table("rev").select(F.date_format("window.start", "HH:mm").alias("from"), "city", "orders", "revenue").orderBy("from", "city").show(truncate=False)
dropped = sum(op.get("numRowsDroppedByWatermark", 0) for pr in q.recentProgress for op in pr.get("stateOperators", []))
print("  rows dropped by watermark:", dropped)
p = q.lastProgress
print("== 4) last micro-batch progress")
print("  batchId", p["batchId"], "| numInputRows", p["numInputRows"], "| watermark", p["eventTime"].get("watermark"))
print("  source offsets", p["sources"][0]["endOffset"])
q.stop()
print("== 5) the checkpoint keeps Kafka offsets (Spark does not commit to a consumer group)")
import os
print("  ", sorted(os.listdir("/tmp/chk94")), "| offsets/:", sorted(os.listdir("/tmp/chk94/offsets"))[:4])
print("  ", open("/tmp/chk94/offsets/" + sorted([f for f in os.listdir("/tmp/chk94/offsets") if f.isdigit()], key=int)[-1]).read().splitlines()[-1])
