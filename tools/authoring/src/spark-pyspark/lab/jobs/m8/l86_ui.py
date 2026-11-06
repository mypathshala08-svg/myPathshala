"""8.6 Keep a UI alive with a skewed + spilling job for screenshots."""
import time
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.window import Window
spark = (SparkSession.builder.master("local[2]").appName("tiffingo-ui-demo").config("spark.driver.memory", "1g")
         .config("spark.sql.adaptive.enabled", "false").config("spark.sql.shuffle.partitions", 4).config("spark.ui.port", "4050").getOrCreate())
o = spark.read.parquet("/root/lab/spark/data/m8/skew_orders")
spark.sparkContext.setJobDescription("skewed window by rest_id")
o.withColumn("rk", F.row_number().over(Window.partitionBy("rest_id").orderBy("amount"))).write.format("noop").mode("overwrite").save()
spark.sparkContext.setJobDescription("wide sort that spills")
spark.read.parquet("/root/lab/spark/data/orders_big").withColumn("pad", F.repeat(F.lit("x"), 100)).orderBy("amount").write.format("noop").mode("overwrite").save()
print("READY", flush=True); time.sleep(240)
