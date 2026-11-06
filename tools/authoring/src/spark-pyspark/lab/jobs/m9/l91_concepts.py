"""9.1 Streaming concepts: rate source, micro-batches, triggers, progress."""
import time, shutil, json
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master("local[2]").config("spark.sql.shuffle.partitions", 2).getOrCreate()
CK = "/root/lab/spark/data/m9/ck91"; shutil.rmtree(CK, ignore_errors=True)
print("== 1) a streaming DataFrame")
s = spark.readStream.format("rate").option("rowsPerSecond", 50).load()
print("isStreaming:", s.isStreaming); s.printSchema()
try:
    s.count()
except Exception as e:
    print("ERROR:", str(e).splitlines()[0][:150])
print("== 2) micro-batches with a 2 s trigger (memory sink)")
orders = s.select(F.col("timestamp"), (F.col("value") % 4).alias("city_id"), (F.col("value") % 500).alias("amount"))
agg = orders.groupBy("city_id").agg(F.count("*").alias("orders"), F.sum("amount").alias("revenue"))
q = agg.writeStream.format("memory").queryName("rev").outputMode("complete").trigger(processingTime="2 seconds").option("checkpointLocation", CK + "/a").start()
for _ in range(4):
    time.sleep(2.2)
    p = q.lastProgress
    if p: print(f"batch {p['batchId']}: numInputRows {p['numInputRows']:4} | inputRows/s {p.get('inputRowsPerSecond',0):6.1f} | processedRows/s {p.get('processedRowsPerSecond',0):7.1f} | triggerExecution {p['durationMs'].get('triggerExecution')} ms")
spark.sql("SELECT * FROM rev ORDER BY city_id").show()
print("status:", q.status["message"], "| isActive:", q.isActive)
q.stop(); print("after stop isActive:", q.isActive)
print("== 3) trigger availableNow over files")
src = "/root/lab/spark/data/m9/in91"; shutil.rmtree(src, ignore_errors=True)
import os; os.makedirs(src)
for i in range(3):
    with open(f"{src}/f{i}.json", "w") as f:
        for j in range(100): f.write(json.dumps({"order_id": i*100+j, "amount": j}) + "\n")
fs = spark.readStream.schema("order_id long, amount long").option("maxFilesPerTrigger", 1).json(src)
OUT = "/root/lab/spark/data/m9/out91"; shutil.rmtree(OUT, ignore_errors=True)
q2 = fs.writeStream.format("parquet").option("path", OUT).trigger(availableNow=True).option("checkpointLocation", CK + "/b").start()
q2.awaitTermination()
print("batches:", [ (p["batchId"], p["numInputRows"]) for p in q2.recentProgress ], "| rows:", spark.read.parquet(OUT).count(), "| stopped by itself:", not q2.isActive)
with open(f"{src}/f3.json", "w") as f:
    for j in range(50): f.write(json.dumps({"order_id": 300+j, "amount": j}) + "\n")
q3 = fs.writeStream.format("parquet").option("path", OUT).trigger(availableNow=True).option("checkpointLocation", CK + "/b").start(); q3.awaitTermination()
print("rerun with same checkpoint:", [(p["batchId"], p["numInputRows"]) for p in q3.recentProgress], "-> only the new file | total rows:", spark.read.parquet(OUT).count())
