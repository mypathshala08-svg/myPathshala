import socket, os
from pyspark import SparkConf, SparkContext, SparkFiles
from pyspark.sql import SparkSession
conf = (SparkConf().setAppName("l16-context").set("spark.executor.memory", "1g")
        .set("spark.executorEnv.TIFFINGO_CITY", "Mumbai").set("spark.ui.showConsoleProgress", "false"))
print("== 1) SparkConf: what we set in code (master comes from spark-submit)")
for k, v in sorted(conf.getAll()):
    if k.startswith(("spark.app.name", "spark.executor", "spark.master", "spark.submit.deployMode")): print(f"  {k} = {v}")
spark = SparkSession.builder.config(conf=conf).getOrCreate()
sc = spark.sparkContext; sc.setLogLevel("ERROR")
print("== 2) the SparkContext behind the SparkSession")
for name in ["version", "master", "appName", "applicationId", "defaultParallelism", "pythonVer", "uiWebUrl"]:
    print(f"  sc.{name:20s} {getattr(sc, name)}")
print("  spark.sparkContext is sc:", spark.sparkContext is sc)
print("== 3) only one SparkContext per Python process")
try:
    SparkContext(conf=SparkConf().setAppName("second"))
except ValueError as e:
    print("  ValueError:", str(e)[:150])
print("  getOrCreate returns the same one:", SparkContext.getOrCreate() is sc)
print("== 4) SparkFiles: ship a file to every executor")
sc.addFile("/jobs/m14/menu_prices.csv")
print("  driver root dir:", SparkFiles.getRootDirectory())
def price_part(rows):
    path = SparkFiles.get("menu_prices.csv")
    prices = dict(l.strip().split(",") for l in open(path).readlines()[1:])
    for item, qty in rows:
        yield (socket.gethostname(), path.replace("/usr/local/lib/python3.12/site-packages/pyspark", "$SPARK_HOME"), item, qty * int(prices[item]))
orders = sc.parallelize([("idli", 2), ("thali", 1), ("dosa", 3), ("vada", 1)], 4)
for r in sorted(orders.mapPartitions(price_part).collect()): print("  ", r)
print("== 5) addPyFile: ship our own Python module to executors")
sc.addPyFile("/jobs/m14/tiffingo_rules.py")
def with_gst(x):
    import tiffingo_rules
    return (x[0], x[1], tiffingo_rules.gst(x[1]))
print("  ", sc.parallelize([("idli", 90), ("thali", 150)], 2).map(with_gst).collect())
print("== 6) environment variable set with spark.executorEnv.*")
print("  executors see TIFFINGO_CITY =", sc.parallelize([0], 1).map(lambda _: os.environ.get("TIFFINGO_CITY")).collect()[0])
print("  driver sees TIFFINGO_CITY  =", os.environ.get("TIFFINGO_CITY"))
spark.stop()
