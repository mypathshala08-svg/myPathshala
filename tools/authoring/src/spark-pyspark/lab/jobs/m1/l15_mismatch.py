from pyspark.sql import SparkSession
spark = (SparkSession.builder.master("spark://localhost:7077").appName("version-mismatch")
         .config("spark.driver.host", "172.19.0.1").config("spark.driver.bindAddress", "0.0.0.0").getOrCreate())
print("DataFrame count on the cluster:", spark.range(1000).count())
try:
    print(spark.sparkContext.parallelize(range(10), 2).map(lambda x: x * 2).sum())
except Exception as e:
    msg = str(e)
    i = msg.find("PYTHON_VERSION_MISMATCH")
    print(msg[i:i+200] if i >= 0 else msg.splitlines()[0][:200])
spark.stop()
