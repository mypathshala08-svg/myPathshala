"""8.4 Memory, spill and OOM. Run with tiny driver memory to force spill."""
import sys; sys.path.insert(0, "/root/lab/spark/jobs/m8")
from common import mk
from pyspark.sql import SparkSession, functions as F
mem = sys.argv[1]
spark = (SparkSession.builder.master("local[2]").config("spark.driver.memory", mem)
         .config("spark.sql.adaptive.enabled", "false").config("spark.sql.shuffle.partitions", 4).getOrCreate())
sc = spark.sparkContext; stages, run = mk(spark)
jc = sc._jsc.sc().getConf()
print("driver memory:", mem, "| memory.fraction:", jc.get("spark.memory.fraction", "0.6 (default)"), "| storageFraction:", jc.get("spark.memory.storageFraction", "0.5 (default)"))
rt = sc._jvm.java.lang.Runtime.getRuntime()
heap = rt.maxMemory() / 2**20
print(f"JVM heap {heap:.0f} MiB -> unified pool ~ (heap - 300) * 0.6 = {(heap-300)*0.6:.0f} MiB")
o = spark.read.parquet("/root/lab/spark/data/orders_big")
sink = lambda df: (lambda: df.write.format("noop").mode("overwrite").save())
wide = o.withColumn("pad", F.repeat(F.lit("x"), 100))
print("== 1) global sort of 5M wide rows")
run("orderBy amount (4 partitions)", sink(wide.orderBy("amount")))
spark.conf.set("spark.sql.shuffle.partitions", 64)
run("orderBy amount (64 partitions)", sink(wide.orderBy("amount")))
spark.conf.set("spark.sql.shuffle.partitions", 4)
print("== 2) collect_list per city (8 huge groups)")
try:
    run("collect_list per city", sink(wide.groupBy("city").agg(F.collect_list("pad").alias("l"))))
except Exception as e:
    m = str(e)
    for k in ("OutOfMemoryError", "Java heap space", "SparkOutOfMemoryError", "UNABLE_TO_ACQUIRE_MEMORY"):
        if k in m: print("FAILED with", k); break
    else: print("FAILED:", m.splitlines()[0][:200])
