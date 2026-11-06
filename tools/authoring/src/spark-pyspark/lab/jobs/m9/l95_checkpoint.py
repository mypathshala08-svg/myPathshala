"""9.5 Checkpoints, exactly-once and state."""
import shutil, os, json, time
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master("local[2]").config("spark.sql.shuffle.partitions", 2).config("spark.sql.session.timeZone", "UTC").getOrCreate()
D = "/root/lab/spark/data/m9"; CK = D + "/ck95"; OUT = D + "/out95"
for p in (CK, OUT): shutil.rmtree(p, ignore_errors=True)
K = "localhost:9092"
def produce(start, n):
    spark.range(start, start + n).select(F.col("id").cast("string").alias("key"),
        F.to_json(F.struct(F.col("id").alias("order_id"), (F.col("id") % 500).alias("amount"))).alias("value")) \
        .write.format("kafka").option("kafka.bootstrap.servers", K).option("topic", "pay").save()
def stream(**opt):
    return (spark.readStream.format("kafka").option("kafka.bootstrap.servers", K).option("subscribe", "pay")
            .option("startingOffsets", "earliest").options(**opt).load()
            .select(F.from_json(F.col("value").cast("string"), "order_id long, amount long").alias("o")).select("o.*"))
print("== 1) run, stop, produce more, restart from the checkpoint")
produce(0, 1000)
q = stream().writeStream.format("parquet").option("path", OUT).option("checkpointLocation", CK + "/files").trigger(availableNow=True).start(); q.awaitTermination()
print("run 1: batches", [p["batchId"] for p in q.recentProgress], "| rows in sink:", spark.read.parquet(OUT).count())
produce(1000, 500)
q = stream().writeStream.format("parquet").option("path", OUT).option("checkpointLocation", CK + "/files").trigger(availableNow=True).start(); q.awaitTermination()
r = spark.read.parquet(OUT)
print("run 2: batches", [p["batchId"] for p in q.recentProgress], "| rows in sink:", r.count(), "| distinct order_id:", r.select("order_id").distinct().count())
print("== 2) what is in a checkpoint")
for d in sorted(x for x in os.listdir(CK + "/files") if not x.startswith(".")): print(" ", d, sorted(x for x in os.listdir(f"{CK}/files/{d}") if not x.startswith(".")) if os.path.isdir(f"{CK}/files/{d}") else "")
print("  offsets/1:", open(CK + "/files/offsets/1").read().strip().split("\n")[-1])
print("  sink log:", sorted(x for x in os.listdir(OUT + "/_spark_metadata") if not x.startswith(".")))
print("== 3) a crash inside foreachBatch: replay = at-least-once")
store = {"append": [], "idempotent": {}}
crashed = {"append": False, "idempotent": False}
def make(kind):
    def fb(df, bid):
        rows = df.count()
        if kind == "append":
            store["append"].append((bid, rows))
        else:
            store["idempotent"][bid] = rows          # overwrite by batch_id (like MERGE / delete+insert)
        if bid == 1 and not crashed[kind]:
            crashed[kind] = True
            raise RuntimeError("simulated crash after writing batch 1")
    return fb
src = stream(maxOffsetsPerTrigger=600).withColumn("g", F.col("order_id") % 3)
for kind in ("append", "idempotent"):
    for attempt in (1, 2):
        q = src.writeStream.foreachBatch(make(kind)).option("checkpointLocation", f"{CK}/fb_{kind}") \
               .trigger(availableNow=True).start()
        try:
            q.awaitTermination(); print(f"  {kind} attempt {attempt}: finished")
        except Exception as e:
            print(f"  {kind} attempt {attempt}: FAILED ({'simulated crash' if 'simulated' in str(e) else str(e)[:60]})")
    data = store[kind] if kind == "append" else sorted(store[kind].items())
    total = sum(n for _, n in data)
    print(f"  {kind}: writes {data} -> total rows {total} (source has 1500)")
print("== 4) stateful dedup with watermark + RocksDB state store")
spark.conf.set("spark.sql.streaming.stateStore.providerClass", "org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider")
produce(0, 300)   # replay 300 duplicates of existing order ids
ded = (spark.readStream.format("kafka").option("kafka.bootstrap.servers", K).option("subscribe", "pay").option("startingOffsets", "earliest").load()
       .select(F.from_json(F.col("value").cast("string"), "order_id long, amount long").alias("o"), F.col("timestamp")).select("o.*", "timestamp")
       .withWatermark("timestamp", "10 minutes").dropDuplicatesWithinWatermark(["order_id"]))
q = ded.writeStream.format("memory").queryName("dedup").option("checkpointLocation", CK + "/dedup").trigger(availableNow=True).start(); q.awaitTermination()
st = q.lastProgress["stateOperators"][0]
print("  input rows:", sum(p["numInputRows"] for p in q.recentProgress), "| output rows:", spark.table("dedup").count(),
      "| state rows:", st["numRowsTotal"], "| provider:", "RocksDB" if "rocksdb" in json.dumps(st).lower() else st.get("operatorName"))
print("== 5) changing a stateful query on an old checkpoint")
spark.conf.unset("spark.sql.streaming.stateStore.providerClass")
agg1 = stream().groupBy((F.col("order_id") % 3).alias("k")).agg(F.count("*").alias("n"))
q = agg1.writeStream.outputMode("complete").format("memory").queryName("a1").option("checkpointLocation", CK + "/agg").trigger(availableNow=True).start(); q.awaitTermination()
produce(2000, 100)   # new data so the restarted query must run a batch
agg2 = stream().groupBy((F.col("order_id") % 3).cast("string").alias("k")).agg(F.count("*").alias("n"))   # key type changed
try:
    q = agg2.writeStream.outputMode("complete").format("memory").queryName("a2").option("checkpointLocation", CK + "/agg").trigger(availableNow=True).start(); q.awaitTermination()
    print("  restarted OK")
except Exception as e:
    m = str(e); i = m.find("[STATE_STORE"); print("  ERROR:", m[i:i+230].replace("\n", " "))
