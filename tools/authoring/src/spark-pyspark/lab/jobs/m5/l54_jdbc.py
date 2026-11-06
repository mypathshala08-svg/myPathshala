"""5.4 JDBC (PostgreSQL 16), XML and other sources."""
import time, subprocess, re
from pyspark.sql import SparkSession, functions as F
spark = (SparkSession.builder.master("local[4]")
         .config("spark.jars", "/root/lab/spark/jars/postgresql-42.7.4.jar").getOrCreate())
URL = "jdbc:postgresql://localhost:5433/tiffingo"
PROPS = {"user": "postgres", "password": "tiffin", "driver": "org.postgresql.Driver"}
def short(e, n=170):
    return str(e).split("\n")[0][:n]
def pg(sql):
    return subprocess.run(["docker", "exec", "pgspark", "psql", "-U", "postgres", "-d", "tiffingo", "-Atc", sql], capture_output=True, text=True).stdout.strip()
def pg_log_since(marker):
    log = subprocess.run(["docker", "logs", "pgspark"], capture_output=True, text=True).stderr
    log = log[log.rfind(marker):]
    return [re.sub(r".*LOG:  execute [^:]*: ", "", l) for l in log.splitlines() if "LOG:  execute" in l and "orders" in l and "pg_" not in l]

orders = spark.read.parquet("/root/lab/spark/data/orders_big").limit(1_000_000)

print("== 1) write 1M orders to PostgreSQL")
pg("DROP TABLE IF EXISTS orders")
print("first try (JVM time zone Asia/Calcutta): FATAL: invalid value for parameter \"TimeZone\": \"Asia/Calcutta\"")
print("fixed with -Duser.timezone=Asia/Kolkata")
for bs in (1000, 10000):
    t = time.time()
    orders.repartition(4).write.mode("overwrite").jdbc(URL, "orders", properties={**PROPS, "batchsize": str(bs)})
    print(f"batchsize {bs:5}: {time.time()-t:5.1f} s")
print("rows in Postgres:", pg("SELECT count(*) FROM orders"))
print("table created by Spark:", pg("SELECT string_agg(column_name || ' ' || data_type, ', ' ORDER BY ordinal_position) FROM information_schema.columns WHERE table_name='orders'"))

print("== 2) a plain read is ONE partition")
d = spark.read.jdbc(URL, "orders", properties=PROPS)
print("partitions:", d.rdd.getNumPartitions())
t = time.time(); print("sum:", d.agg(F.sum("amount")).first()[0], f"in {time.time()-t:.1f} s")

print("== 3) a parallel read")
pg("SELECT 1")  # marker
mark = f"marker_{int(time.time())}"; pg(f"SELECT '{mark}'")
p = spark.read.jdbc(URL, "orders", column="order_id", lowerBound=1_000_000, upperBound=6_000_000, numPartitions=4, properties=PROPS)
print("partitions:", p.rdd.getNumPartitions())
t = time.time(); print("sum:", p.agg(F.sum("amount")).first()[0], f"in {time.time()-t:.1f} s")
for q in sorted({q[q.find("WHERE"):].strip() for q in pg_log_since(mark) if '"order_id"' in q}):
    print("  SQL:", q[:90])
print("rows per partition:", p.rdd.glom().map(len).collect())

print("== 4) bounds do not filter")
narrow = spark.read.jdbc(URL, "orders", column="order_id", lowerBound=1_000_000, upperBound=2_000_000, numPartitions=4, properties=PROPS)
print("rows:", narrow.count(), "| per partition:", narrow.rdd.glom().map(len).collect())

print("== 5) pushdown")
mark = f"marker_{int(time.time())}b"; pg(f"SELECT '{mark}'")
f = d.where("city = 'Pune' AND amount > 800").select("order_id", "amount")
f.explain()
print("rows:", f.count())
for q in sorted({q.strip() for q in pg_log_since(mark)}):
    print("  SQL:", q[:150])

print("== 6) the query option")
top = (spark.read.format("jdbc").option("url", URL).options(**PROPS)
       .option("query", "SELECT city, sum(amount) AS revenue FROM orders GROUP BY city").load())
top.orderBy(F.desc("revenue")).show(3)

print("== 7) XML (built in since Spark 4.0)")
x = spark.read.option("rowTag", "restaurant").xml("/root/lab/spark/data/m5/menu.xml")
x.printSchema()
x.select("_id", "_city", "name", F.size("dish").alias("dishes")).show()
x.select("name", F.explode("dish").alias("d")).select("name", "d._veg", "d.title", "d.price").show(truncate=False)

print("== 8) text and binaryFile")
t = spark.read.text("/root/lab/spark/data/tiffingo/reviews")
print("text  :", t.columns, t.count(), "lines")
b = spark.read.format("binaryFile").load("/root/lab/spark/data/m5/*.{csv,xml,jsonl}")
b.select(F.regexp_extract("path", r"[^/]+$", 0).alias("file"), "length", "modificationTime").show(truncate=False)
