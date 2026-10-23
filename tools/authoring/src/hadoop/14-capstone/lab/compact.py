# compact.py: 104 small daily files -> one file per canteen, each line tagged with the day it arrived
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.appName("capstone-compact").getOrCreate()
B = "hdfs://namenode/capstone"
lines = (spark.read.text(f"{B}/bronze/orders/college=*")
         .withColumn("fday", F.regexp_extract(F.input_file_name(), r"_(\d{4}-\d{2}-\d{2})\.csv$", 1))
         .withColumn("college", F.regexp_extract(F.input_file_name(), r"college=(\w+)", 1))
         .where(~F.col("value").startswith("order_id,")))
(lines.select(F.concat_ws("\t", "fday", "value").alias("value"), "college")
      .repartition("college").write.mode("overwrite").partitionBy("college").text(f"{B}/bronze_monthly/orders"))
print("lines:", spark.read.text(f"{B}/bronze_monthly/orders").count())
