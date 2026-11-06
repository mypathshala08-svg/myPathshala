"""Same question, RDD API vs DataFrame API: revenue of delivered orders per city."""
import time
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master("local[2]").getOrCreate()
sc = spark.sparkContext
df = spark.read.parquet("/root/lab/spark/data/orders_big")
df.count()                                   # warm up file listing and JVM

t = time.time()
res_df = (df.where("status = 'DELIVERED'").groupBy("city").agg(F.sum("amount").alias("rev"))
            .orderBy(F.desc("rev")).collect())
t_df = time.time() - t

t = time.time()
res_rdd = (df.rdd.filter(lambda r: r.status == "DELIVERED")
                 .map(lambda r: (r.city, r.amount))
                 .reduceByKey(lambda a, b: a + b)
                 .sortBy(lambda kv: -kv[1]).collect())
t_rdd = time.time() - t

print("DataFrame:", [(r.city, r.rev) for r in res_df[:3]], f"{t_df:.1f} s")
print("RDD      :", res_rdd[:3], f"{t_rdd:.1f} s")
print("same answer:", [(r.city, r.rev) for r in res_df] == res_rdd, f"| RDD/DataFrame time: {t_rdd/t_df:.0f}x")
spark.stop()
