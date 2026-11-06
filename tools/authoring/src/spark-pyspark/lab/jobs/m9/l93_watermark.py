"""9.3 Output modes, event time and watermarks (deterministic: one file per micro-batch)."""
import shutil, os, json
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master("local[2]").config("spark.sql.shuffle.partitions", 2).config("spark.sql.session.timeZone", "UTC").getOrCreate()
D = "/root/lab/spark/data/m9"; src = D + "/in93"; shutil.rmtree(src, ignore_errors=True); shutil.rmtree(D + "/ck93", ignore_errors=True); os.makedirs(src)
batches = [
    [("10:01", 100), ("10:02", 200), ("10:04", 50)],          # b0
    [("10:06", 300), ("10:03", 70), ("10:11", 20)],           # b1: 10:03 arrives late
    [("10:16", 10), ("10:02", 999), ("10:12", 40)],           # b2: 10:02 is very late
    [("10:22", 5)],                                           # b3: pushes watermark
    [("10:03", 7777), ("10:24", 1)],                          # b4: 10:03 after its window was emitted
]
for i, b in enumerate(batches):
    with open(f"{src}/b{i}.json", "w") as f:
        for ts, amt in b: f.write(json.dumps({"event_time": f"2026-11-05 {ts}:00", "amount": amt}) + "\n")
    os.utime(f"{src}/b{i}.json", (1_700_000_000 + i * 10, 1_700_000_000 + i * 10))   # file order = batch order
ev = spark.readStream.schema("event_time timestamp, amount long").option("maxFilesPerTrigger", 1).json(src)
def show(tag):
    def f(df, bid):
        rows = sorted((r["window"]["start"].strftime("%H:%M"), r["revenue"]) for r in df.collect())
        print(f"  [{tag}] batch {bid}: {rows}")
    return f
def run(name, df, mode):
    print(f"== {name} (outputMode={mode})")
    q = df.writeStream.outputMode(mode).foreachBatch(show(mode)).option("checkpointLocation", f"{D}/ck93/{name.split()[0]}").trigger(availableNow=True).start()
    q.awaitTermination()
    for p in q.recentProgress:
        wm = p.get("eventTime", {}).get("watermark")
        st = p.get("stateOperators", [{}])
        print(f"     progress batch {p['batchId']}: watermark {wm} | state rows {st[0].get('numRowsTotal') if st else None} | dropped late {st[0].get('numRowsDroppedByWatermark') if st else None}")
w5 = F.window("event_time", "5 minutes")
plain = ev.groupBy(w5).agg(F.sum("amount").alias("revenue"))
wm = ev.withWatermark("event_time", "5 minutes").groupBy(w5).agg(F.sum("amount").alias("revenue"))
run("1 complete", plain, "complete")
run("2 update", plain, "update")
try:
    run("3 append-no-watermark", plain, "append")
except Exception as e:
    print("  ERROR:", str(e).splitlines()[0][:170])
run("4 append-watermark", wm, "append")
run("5 update-watermark", wm, "update")
