import os
from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local[2]").getOrCreate()
path = "/root/lab/spark/data/big_csv"
size = sum(os.path.getsize(os.path.join(path, f)) for f in os.listdir(path) if f.endswith(".csv"))
print(f"input: {size/2**20:.0f} MiB in {len([f for f in os.listdir(path) if f.endswith('.csv')])} files")
for mb in (128, 32, 8):
    spark.conf.set("spark.sql.files.maxPartitionBytes", f"{mb}m")
    n = spark.read.csv(path, header=True).rdd.getNumPartitions()
    print(f"maxPartitionBytes={mb:>3} MiB -> {n:>2} partitions (= tasks in the first stage)")
spark.stop()
