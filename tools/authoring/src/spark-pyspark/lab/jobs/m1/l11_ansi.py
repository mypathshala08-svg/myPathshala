from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master("local[2]").getOrCreate()
df = spark.read.csv("/root/lab/spark/data/tiffingo/orders.csv", header=True)
print("spark.sql.ansi.enabled =", spark.conf.get("spark.sql.ansi.enabled"))
try:
    df.select(F.sum(F.col("amount").cast("double"))).show()
except Exception as e:
    print(type(e).__name__ + ":", str(e).splitlines()[0][:220])
df.select(F.sum(F.col("amount").try_cast("double")).alias("total"), F.count_if(F.col("amount").try_cast("double").isNull()).alias("bad_rows")).show()
