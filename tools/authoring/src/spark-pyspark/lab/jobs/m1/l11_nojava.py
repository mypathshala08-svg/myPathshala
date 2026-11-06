from pyspark.sql import SparkSession
try:
    SparkSession.builder.master("local[1]").getOrCreate()
except Exception as e:
    print(type(e).__name__ + ":", str(e).strip().splitlines()[0])
