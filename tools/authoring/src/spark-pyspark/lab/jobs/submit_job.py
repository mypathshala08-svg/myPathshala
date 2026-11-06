import socket, sys
from pyspark.sql import SparkSession, functions as F
spark = (SparkSession.builder.appName("tiffingo-submit-demo")
         .config("spark.sql.shuffle.partitions", "12")          # set in code
         .getOrCreate())
sc = spark.sparkContext; c = sc.getConf()
print("deployMode:", c.get("spark.submit.deployMode"), "| driver host:", socket.gethostname())
for k in ("spark.sql.shuffle.partitions", "spark.executor.memory", "spark.app.name", "spark.eventLog.enabled"):
    print(f"  {k} = {spark.conf.get(k, c.get(k, '(unset)'))}")
def add_gst(a):
    from tiffin_utils import gst          # imported on the executor
    return gst(a)
try:
    rows = spark.range(1, 4).select((F.col("id") * 100).alias("amount")).rdd.map(lambda r: (r.amount, add_gst(r.amount))).collect()
    print("with GST:", rows)
except Exception as e:
    m = str(e); i = m.find("ModuleNotFoundError"); print("FAILED on executor:", m[i:i+60] if i >= 0 else m.splitlines()[0][:120])
spark.stop()
