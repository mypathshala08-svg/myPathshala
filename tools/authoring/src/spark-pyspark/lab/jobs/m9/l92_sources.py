"""9.2 Sources and sinks: Kafka in/out, files, foreachBatch to PostgreSQL, console."""
import time, shutil, json
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master("local[2]").config("spark.sql.shuffle.partitions", 2).getOrCreate()
D = "/root/lab/spark/data/m9"; shutil.rmtree(D + "/ck92", ignore_errors=True); shutil.rmtree(D + "/out92", ignore_errors=True)
K = "localhost:9092"
print("== 1) produce 600 order events to Kafka topic 'orders' (3 partitions)")
ev = spark.range(600).select(F.col("id").cast("string").alias("key"),
    F.to_json(F.struct(F.col("id").alias("order_id"), F.element_at(F.array(*[F.lit(c) for c in ("Mumbai","Pune","Delhi")]), (F.col("id") % 3 + 1).cast("int")).alias("city"),
                       (F.col("id") % 500).alias("amount"))).alias("value"))
ev.write.format("kafka").option("kafka.bootstrap.servers", K).option("topic", "orders").save()
print("== 2) read the topic as a stream: fixed Kafka schema")
raw = spark.readStream.format("kafka").option("kafka.bootstrap.servers", K).option("subscribe", "orders").option("startingOffsets", "earliest").option("maxOffsetsPerTrigger", 250).load()
raw.printSchema()
sch = "order_id long, city string, amount long"
orders = raw.select(F.col("partition"), F.col("offset"), F.from_json(F.col("value").cast("string"), sch).alias("o")).select("partition", "offset", "o.*")
print("== 3) file sink (parquet) with maxOffsetsPerTrigger=250, availableNow")
q = orders.writeStream.format("parquet").option("path", D + "/out92").option("checkpointLocation", D + "/ck92/files").trigger(availableNow=True).start()
q.awaitTermination()
for p in q.recentProgress:
    so = p["sources"][0]
    print(f"batch {p['batchId']}: rows {p['numInputRows']} | endOffset {so['endOffset']}")
r = spark.read.parquet(D + "/out92"); print("rows in parquet:", r.count(), "| files:", len(r.inputFiles()))
r.orderBy("partition", "offset").show(3)
print("== 4) foreachBatch -> PostgreSQL (idempotent per batch)")
url = "jdbc:postgresql://localhost:5433/tiffingo"; props = {"user": "postgres", "password": "tiffin", "driver": "org.postgresql.Driver"}
def to_pg(df, batch_id):
    out = df.groupBy("city").agg(F.count("*").alias("orders"), F.sum("amount").alias("revenue")).withColumn("batch_id", F.lit(batch_id))
    out.write.jdbc(url, "city_rev_stream", mode="append", properties=props)
    print(f"  foreachBatch batch_id={batch_id}: {df.count()} rows -> {out.count()} city rows")
spark.read.jdbc(url, "(select 1 as x) t", properties=props)  # warm-up
spark.createDataFrame([], "city string, orders long, revenue long, batch_id long").write.jdbc(url, "city_rev_stream", mode="overwrite", properties=props)
q2 = orders.writeStream.foreachBatch(to_pg).option("checkpointLocation", D + "/ck92/pg").trigger(availableNow=True).start(); q2.awaitTermination()
spark.read.jdbc(url, "city_rev_stream", properties=props).groupBy("city").agg(F.sum("orders").alias("orders"), F.sum("revenue").alias("revenue")).orderBy("city").show()
print("== 5) Kafka sink: enrich and write to topic 'big_orders'")
big = orders.filter("amount >= 450").select(F.col("order_id").cast("string").alias("key"), F.to_json(F.struct("order_id", "city", "amount")).alias("value"))
q3 = big.writeStream.format("kafka").option("kafka.bootstrap.servers", K).option("topic", "big_orders").option("checkpointLocation", D + "/ck92/kafka").trigger(availableNow=True).start(); q3.awaitTermination()
back = spark.read.format("kafka").option("kafka.bootstrap.servers", K).option("subscribe", "big_orders").load()
print("messages in big_orders:", back.count()); back.selectExpr("CAST(key AS STRING) k", "CAST(value AS STRING) v").show(2, truncate=False)
print("== 6) console sink (debugging)")
q4 = orders.limit(3).writeStream.format("console").outputMode("append").trigger(availableNow=True).option("checkpointLocation", D + "/ck92/console").start(); q4.awaitTermination()
