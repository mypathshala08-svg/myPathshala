"""9.4 Windowed aggregations and stream joins."""
import shutil, os, json
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master("local[2]").config("spark.sql.shuffle.partitions", 2).config("spark.sql.session.timeZone", "UTC").getOrCreate()
D = "/root/lab/spark/data/m9"; shutil.rmtree(D + "/ck94", ignore_errors=True)
def files(name, batches, schema_rows):
    p = f"{D}/in94_{name}"; shutil.rmtree(p, ignore_errors=True); os.makedirs(p)
    for i, b in enumerate(batches):
        with open(f"{p}/b{i}.json", "w") as f:
            for r in b: f.write(json.dumps(dict(zip(schema_rows, r))) + "\n")
        os.utime(f"{p}/b{i}.json", (1_700_000_000 + i * 10,) * 2)
    return p
T = lambda hm: f"2026-11-05 {hm}:00"
clicks = files("clicks", [[(T("10:00"), "u1"), (T("10:02"), "u1"), (T("10:03"), "u2"), (T("10:09"), "u1"), (T("10:12"), "u2")]], ["ts", "user"])
c = spark.readStream.schema("ts timestamp, user string").json(clicks)
def collect(df, name, mode="complete", fmt=lambda r: r):
    q = df.writeStream.outputMode(mode).format("memory").queryName(name).trigger(availableNow=True).start(); q.awaitTermination()
    return [fmt(r) for r in spark.table(name).collect()]
hm = lambda x: x.strftime("%H:%M")
print("== 1) tumbling 5 min")
print(sorted(collect(c.groupBy(F.window("ts", "5 minutes")).count(), "tum", fmt=lambda r: (hm(r[0][0]), hm(r[0][1]), r[1]))))
print("== 2) sliding 10 min every 5 min (each event in 2 windows)")
print(sorted(collect(c.groupBy(F.window("ts", "10 minutes", "5 minutes")).count(), "sli", fmt=lambda r: (hm(r[0][0]), hm(r[0][1]), r[1]))))
print("== 3) session window, gap 5 min, per user")
print(sorted(collect(c.groupBy("user", F.session_window("ts", "5 minutes")).count(), "ses", fmt=lambda r: (r[0], hm(r[1][0]), hm(r[1][1]), r[2]))))
print("== 4) stream-static join: orders stream + restaurants table")
rest = spark.createDataFrame([(1, "Biryani House", "Mumbai"), (2, "Dosa Point", "Pune")], "rest_id int, name string, city string")
orders = files("orders", [[(T("10:00"), 101, 1), (T("10:01"), 102, 2), (T("10:02"), 103, 3)]], ["ts", "order_id", "rest_id"])
o = spark.readStream.schema("ts timestamp, order_id long, rest_id int").json(orders)
print("inner:", sorted(collect(o.join(rest, "rest_id"), "ss", "append", fmt=lambda r: (r["order_id"], r["name"]))))
print("left :", sorted(collect(o.join(rest, "rest_id", "left"), "ssl", "append", fmt=lambda r: (r["order_id"], r["name"]))))
print("== 5) stream-stream join: orders x deliveries within 30 min, with watermarks")
od = files("od", [
    [(T("10:00"), 1), (T("10:05"), 2), (T("10:10"), 3)],
    [(T("10:20"), 4)],
    [(T("11:30"), 5)],
], ["order_ts", "order_id"])
dl = files("dl", [
    [(T("10:25"), 1)],
    [(T("10:50"), 2), (T("10:30"), 4)],
    [(T("11:40"), 5)],
], ["deliver_ts", "d_order_id"])
os_ = spark.readStream.schema("order_ts timestamp, order_id long").option("maxFilesPerTrigger", 1).json(od).withWatermark("order_ts", "10 minutes")
ds = spark.readStream.schema("deliver_ts timestamp, d_order_id long").option("maxFilesPerTrigger", 1).json(dl).withWatermark("deliver_ts", "10 minutes")
cond = F.expr("d_order_id = order_id AND deliver_ts BETWEEN order_ts AND order_ts + INTERVAL 30 MINUTES")
for how in ("inner", "leftOuter"):
    out = []
    def fb(df, bid, how=how):
        rows = sorted((r["order_id"], hm(r["deliver_ts"]) if r["deliver_ts"] else None) for r in df.collect())
        print(f"  [{how}] batch {bid}: {rows}")
    q = os_.join(ds, cond, how).writeStream.foreachBatch(fb).option("checkpointLocation", f"{D}/ck94/{how}").trigger(availableNow=True).start(); q.awaitTermination()
    st = q.lastProgress["stateOperators"][0]
    print(f"  state rows at end: {st['numRowsTotal']}")
print("== 6) stream-stream join without watermark: state never cleaned")
q = spark.readStream.schema("order_ts timestamp, order_id long").option("maxFilesPerTrigger", 1).json(od).join(
    spark.readStream.schema("deliver_ts timestamp, d_order_id long").option("maxFilesPerTrigger", 1).json(dl), F.expr("d_order_id = order_id")) \
    .writeStream.format("noop").option("checkpointLocation", f"{D}/ck94/nowm").trigger(availableNow=True).start(); q.awaitTermination()
print("  state rows per batch:", [p["stateOperators"][0]["numRowsTotal"] for p in q.recentProgress])
