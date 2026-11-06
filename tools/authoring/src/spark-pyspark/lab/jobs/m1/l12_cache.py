"""Why in-memory matters: the same 3 questions on the same data, without and with cache()."""
import time
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master("local[2]").appName("cache").getOrCreate()
def three_questions(df):
    t = time.time()
    df.groupBy("city").count().collect()
    df.agg(F.avg("amount")).collect()
    df.where("amount > 900").count()
    return time.time() - t
src = (spark.read.csv("/root/lab/spark/data/big_csv", header=True, inferSchema=False)
       .withColumn("amount", F.col("amount").cast("int")))
three_questions(src.limit(10))          # warm up the JVM
print(f"without cache: {three_questions(src):.1f} s  (CSV parsed 3 times)")
cached = src.cache(); cached.count()
print(f"with cache   : {three_questions(cached):.1f} s  (rows kept in executor memory)")
spark.stop()
