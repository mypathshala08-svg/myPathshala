import pandas as pd
from pyspark.sql import SparkSession, functions as F
path = "/root/lab/spark/data/tiffingo/orders.csv"
pdf = pd.read_csv(path)
print("pandas dtypes:", dict(pdf.dtypes.astype(str)))
pdf["amount"] = pd.to_numeric(pdf["amount"], errors="coerce")
print(pdf.groupby("city")["amount"].sum().sort_values(ascending=False).head(3).to_string())

spark = SparkSession.builder.master("local[2]").appName("l11").getOrCreate()
df = spark.read.csv(path, header=True, inferSchema=True)
df.printSchema()
(df.groupBy("city").agg(F.sum(F.col("amount").try_cast("double")).alias("amount"))
   .orderBy(F.desc("amount")).show(3))
spark.stop()
