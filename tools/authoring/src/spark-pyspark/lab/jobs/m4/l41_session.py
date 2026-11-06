"""4.1 SparkSession and DataFrames: entry point, getOrCreate, newSession, immutability, laziness, plans."""
import time, json, urllib.request
from pyspark.sql import SparkSession, functions as F

print("== 1) builder.getOrCreate")
spark = (SparkSession.builder.appName("tiffingo-4.1").master("local[2]")
         .config("spark.sql.shuffle.partitions", "8").getOrCreate())
print("version            :", spark.version)
print("app name           :", spark.sparkContext.appName)
print("master             :", spark.sparkContext.master)
print("shuffle partitions :", spark.conf.get("spark.sql.shuffle.partitions"))
print("UI                 :", spark.sparkContext.uiWebUrl)

print("== 2) a second getOrCreate")
s2 = SparkSession.builder.appName("another-name").config("spark.sql.shuffle.partitions", "50").getOrCreate()
print("same object        :", s2 is spark)
print("app name           :", s2.sparkContext.appName)
print("shuffle partitions :", s2.conf.get("spark.sql.shuffle.partitions"))

print("== 3) newSession")
s3 = spark.newSession()
print("same SparkContext  :", s3.sparkContext is spark.sparkContext)
spark.range(3).createOrReplaceTempView("nums")
print("view in spark      :", [t.name for t in spark.catalog.listTables()])
print("view in newSession :", [t.name for t in s3.catalog.listTables()])
s3.conf.set("spark.sql.shuffle.partitions", "4")
print("conf spark / s3    :", spark.conf.get("spark.sql.shuffle.partitions"), "/", s3.conf.get("spark.sql.shuffle.partitions"))

print("== 4) a DataFrame from orders.csv")
t = time.time()
orders = spark.read.csv("/root/lab/spark/data/tiffingo/orders.csv", header=True, inferSchema=True)
print(f"read took {time.time()-t:.1f} s (inferSchema scans the file)")
print(type(orders).__name__, "| columns:", orders.columns)
orders.printSchema()
orders.show(3)
print("rows:", orders.count(), "| partitions:", orders.rdd.getNumPartitions())
print("why is amount a string?", [r.amount for r in orders.where("try_cast(amount AS INT) IS NULL").select("amount").collect()])
orders = orders.withColumn("amount", F.expr("try_cast(amount AS INT)"))
print("amount now:", dict(orders.dtypes)["amount"])

print("== 5) immutable")
o2 = orders.withColumn("amount_gst", F.round(F.col("amount") * 1.05, 2))
print("orders columns:", len(orders.columns), "| o2 columns:", len(o2.columns), "| same object:", o2 is orders)

print("== 6) lazy: count jobs")
def jobs():
    return len(json.load(urllib.request.urlopen(f"{spark.sparkContext.uiWebUrl}/api/v1/applications/{spark.sparkContext.applicationId}/jobs")))
j0 = jobs()
q = (orders.where(F.col("status") == "DELIVERED")
           .groupBy("city").agg(F.sum("amount").alias("revenue"))
           .orderBy(F.desc("revenue")))
print("jobs after building the query:", jobs() - j0)
q.show(5)
print("jobs after show():", jobs() - j0)

print("== 7) the plan")
q.explain()

print("== 8) Row objects")
r = q.first()
print(r)
print(r["city"], r.revenue, r.asDict())

print("== 9) DataFrame vs SQL: same plan")
orders.createOrReplaceTempView("orders")
sq = spark.sql("SELECT city, sum(amount) AS revenue FROM orders WHERE status='DELIVERED' GROUP BY city ORDER BY revenue DESC")
p1 = q._jdf.queryExecution().optimizedPlan().toString()
p2 = sq._jdf.queryExecution().optimizedPlan().toString()
import re
norm = lambda s: re.sub(r"#\d+L?", "", s)
print("optimized plans equal (ids removed):", norm(p1) == norm(p2))

print("== 10) stop")
spark.stop()
print("active session after stop:", SparkSession.getActiveSession())
