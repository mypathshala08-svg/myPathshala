import sys; sys.path.insert(0, "/root/lab/spark/jobs/m8")
from common import mk
from pyspark.sql import SparkSession, functions as F
spark = (SparkSession.builder.master("local[2]").config("spark.driver.memory", "1g")
         .config("spark.sql.adaptive.enabled", "false").config("spark.sql.shuffle.partitions", 4).getOrCreate())
stages, run = mk(spark)
o = spark.read.parquet("/root/lab/spark/data/orders_big"); wide = o.withColumn("pad", F.repeat(F.lit("x"), 100))
sink = lambda df: (lambda: df.write.format("noop").mode("overwrite").save())
print("== 3) fixes at 1g")
run("count + sum per city (no list)", sink(wide.groupBy("city").agg(F.count("*"), F.sum("amount"))))
run("collect_list per customer (3999 small groups)", sink(wide.groupBy("customer_id").agg(F.collect_list("pad").alias("l"))))
run("top-5 per city via window, not list", sink(o.withColumn("r", F.row_number().over(__import__("pyspark.sql.window",fromlist=["Window"]).Window.partitionBy("city").orderBy(F.desc("amount")))).filter("r<=5")))
