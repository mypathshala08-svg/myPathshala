import time, threading, re, io, contextlib
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.functions import udf, pandas_udf
spark = (SparkSession.builder.master("local[2]").appName("l87")
         .config("spark.ui.showConsoleProgress", "false").getOrCreate())
sc = spark.sparkContext; sc.setLogLevel("ERROR")
df = spark.range(400_000).withColumn("item", F.concat(F.lit("item-"), (F.col("id") % 50).cast("string")))

def slow_band(item):                       # deliberately wasteful Python
    n = int(item.split("-")[1])
    return "hot" if sum(i * i for i in range(n)) % 3 == 0 else "cold"

print("== 1) Spark 4 UDF profiler: where does Python time go?")
spark.conf.set("spark.sql.pyspark.udf.profiler", "perf")
band = udf(slow_band, "string")
t = time.time(); df.select(band("item").alias("b")).groupBy("b").count().collect(); print(f"  job took {time.time()-t:.2f} s")
buf = io.StringIO()
with contextlib.redirect_stdout(buf): spark.profile.show(type="perf")
out = buf.getvalue().splitlines()
for l in out:
    if re.search(r"Profile of UDF|function calls|ncalls|slow_band|genexpr|<built-in method builtins.sum>|split", l): print("  " + l.strip()[:118])
spark.conf.unset("spark.sql.pyspark.udf.profiler")
print("== 2) after the fix: built-in functions, no Python UDF")
n = F.split("item", "-").getItem(1).cast("int")
t = time.time()
df.select(F.when(((n - 1) * n * (2 * n - 1) / 6) % 3 == 0, "hot").otherwise("cold").alias("b")).groupBy("b").count().collect()
print(f"  job took {time.time()-t:.2f} s (sum of squares 0..n-1 = (n-1)n(2n-1)/6)")
print("== 3) StatusTracker: watch a running job from another thread")
st = sc.statusTracker()
def work():
    sc.setJobGroup("nightly-report", "orders per item")
    spark.range(30_000_000).repartition(8).groupBy((F.col("id") % 7).alias("k")).count().collect()
th = threading.Thread(target=work); th.start(); seen = set()
for _ in range(60):
    time.sleep(0.5)
    for j in st.getActiveJobsIds():
        ji = st.getJobInfo(j)
        if ji is None: continue
        for s in ji.stageIds:
            si = st.getStageInfo(s)
            if si and (j, s, si.numCompletedTasks) not in seen and si.numTasks:
                seen.add((j, s, si.numCompletedTasks))
                print(f"  job {j} [{ji.status}] stage {s}: {si.numCompletedTasks}/{si.numTasks} tasks done, {si.numActiveTasks} running")
    if not th.is_alive(): break
th.join()
print("  jobs in group nightly-report:", st.getJobIdsForGroup("nightly-report"))
print("  active jobs now:", st.getActiveJobsIds())
spark.stop()
print("== 4) classic RDD profiler (new session with spark.python.profile=true)")
print("  note: it cannot run together with the UDF profiler in one session on Python 3.12+:")
print("        ValueError: tool 2 is already in use (both use cProfile/sys.monitoring)")
spark = (SparkSession.builder.master("local[2]").appName("l87b").config("spark.ui.showConsoleProgress", "false").config("spark.python.profile", "true").getOrCreate())
sc = spark.sparkContext; sc.setLogLevel("ERROR")
sc.parallelize(range(200_000), 2).map(lambda x: sum(range(x % 300))).count()
buf = io.StringIO()
with contextlib.redirect_stdout(buf): sc.show_profiles()
for l in buf.getvalue().splitlines():
    if re.search(r"Profile of RDD|function calls|builtins.sum|<lambda>", l): print("  " + l.strip()[:118])
spark.stop()
