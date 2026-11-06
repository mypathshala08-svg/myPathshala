"""11.5a Delta Lake (PySpark 4.1 + delta-spark 4.3.1; Delta does not support Spark 4.3 yet)."""
import os, shutil, json, warnings; warnings.filterwarnings("ignore")
import pyspark
from delta import configure_spark_with_delta_pip
from delta.tables import DeltaTable
from pyspark.sql import SparkSession, functions as F
b = (SparkSession.builder.master("local[2]").config("spark.sql.shuffle.partitions", 2).config("spark.ui.showConsoleProgress", "false")
     .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
     .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog"))
spark = configure_spark_with_delta_pip(b).getOrCreate(); spark.sparkContext.setLogLevel("ERROR")
import delta; print("PySpark", pyspark.__version__, "| delta-spark", __import__("importlib.metadata").metadata.version("delta-spark"))
P = "/root/lab/spark/data/m11/delta_orders"; shutil.rmtree(P, ignore_errors=True)
print("== 1) write a Delta table")
o = spark.createDataFrame([(1, "Pune", 450, "PLACED"), (2, "Mumbai", 300, "PLACED"), (3, "Delhi", 800, "PLACED")], "order_id long, city string, amount long, status string")
o.write.format("delta").save(P)
print("files:", sorted(os.listdir(P))); print("_delta_log:", sorted(f for f in os.listdir(P + "/_delta_log") if not f.startswith(".")))
print("== 2) UPDATE, DELETE, MERGE")
t = DeltaTable.forPath(spark, P)
t.update("order_id = 1", {"status": F.lit("DELIVERED")})
t.delete("order_id = 2")
upd = spark.createDataFrame([(3, "Delhi", 800, "DELIVERED"), (4, "Thane", 120, "PLACED")], o.schema)
(t.alias("t").merge(upd.alias("u"), "t.order_id = u.order_id")
   .whenMatchedUpdateAll().whenNotMatchedInsertAll().execute())
spark.read.format("delta").load(P).orderBy("order_id").show()
print("== 3) history and time travel")
t.history().select("version", "operation", "operationParameters.predicate").orderBy("version").show(truncate=False)
print("version 0 rows:", spark.read.format("delta").option("versionAsOf", 0).load(P).count(), "| latest rows:", spark.read.format("delta").load(P).count())
print("== 4) schema enforcement")
bad = spark.createDataFrame([(5, "Pune", "999", "PLACED")], "order_id long, city string, amount string, status string")
try:
    bad.write.format("delta").mode("append").save(P)
except Exception as e:
    m = str(e); print("append with amount as string ->", m.splitlines()[0][:150])
extra = spark.createDataFrame([(6, "Pune", 220, "PLACED", "UPI")], "order_id long, city string, amount long, status string, payment string")
try:
    extra.write.format("delta").mode("append").save(P)
except Exception as e:
    print("append with new column ->", str(e).splitlines()[0][:120])
extra.write.format("delta").mode("append").option("mergeSchema", "true").save(P)
print("with mergeSchema:", spark.read.format("delta").load(P).columns)
print("== 5) a commit in the log")
last = sorted(f for f in os.listdir(P + "/_delta_log") if f.endswith(".json"))[-1]
acts = [list(json.loads(l).keys())[0] for l in open(f"{P}/_delta_log/{last}")]
print(last, "actions:", acts)
