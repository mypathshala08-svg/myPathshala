from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local[1]").getOrCreate()
orders = spark.read.parquet("/root/lab/spark/data/orders_big")
try:
    bad = orders.groupBy("cty").count()          # typo; no action called
except Exception as e:
    print(type(e).__name__ + ":", str(e).splitlines()[0][:170])
spark.stop()
