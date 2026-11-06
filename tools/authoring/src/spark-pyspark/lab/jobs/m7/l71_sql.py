"""7.1 Spark SQL and views."""
import time, os, shutil
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master("local[4]").config("spark.sql.shuffle.partitions", "8").getOrCreate()
def short(e, n=190):
    return str(e).split("\n")[0][:n]
o = spark.read.parquet("/root/lab/spark/data/orders_big")

print("== 1) a temp view and SQL")
o.createOrReplaceTempView("orders")
spark.sql("SELECT city, count(*) AS orders, sum(amount) AS revenue FROM orders WHERE status = 'DELIVERED' GROUP BY city ORDER BY revenue DESC LIMIT 3").show()
print("type:", type(spark.sql("SELECT 1")).__name__)

print("== 2) DataFrame <-> SQL")
top = spark.sql("SELECT city, sum(amount) AS revenue FROM orders GROUP BY city")
print(top.where("revenue > 500000000").select(F.upper("city").alias("city")).collect())

print("== 3) temp views belong to a session; global temp views do not")
o.createOrReplaceGlobalTempView("orders_g")
s2 = spark.newSession()
for name in ("orders", "global_temp.orders_g"):
    try:
        print(f"{name:22} in new session:", s2.sql(f"SELECT count(*) FROM {name}").first()[0])
    except Exception as e:
        print(f"{name:22} in new session:", type(e).__name__, short(e, 120))

print("== 4) a view is a saved query, not saved data")
p = "/root/lab/spark/data/m7/live"
shutil.rmtree(p, ignore_errors=True)
spark.range(3).write.parquet(p)
spark.read.parquet(p).createOrReplaceTempView("live")
print("count:", spark.sql("SELECT count(*) FROM live").first()[0])
spark.range(100, 105).write.mode("append").parquet(p)
print("after appending 5 rows, same view:", spark.sql("SELECT count(*) FROM live").first()[0])
spark.sql("REFRESH TABLE live")
print("after REFRESH TABLE:", spark.sql("SELECT count(*) FROM live").first()[0])

print("== 5) SQL views over SQL")
spark.sql("""CREATE OR REPLACE TEMP VIEW city_daily AS
             SELECT city, order_date, sum(amount) AS revenue, count(*) AS n FROM orders GROUP BY city, order_date""")
spark.sql("SELECT city, round(avg(revenue)) AS avg_daily FROM city_daily GROUP BY city ORDER BY avg_daily DESC LIMIT 3").show()

print("== 6) parameters, not string concatenation")
city = "Pune' OR '1'='1"
bad = f"SELECT count(*) FROM orders WHERE city = '{city}'"
print("f-string query  :", spark.sql(bad).first()[0])
print("named parameter :", spark.sql("SELECT count(*) FROM orders WHERE city = :city", args={"city": city}).first()[0])
print("good value      :", spark.sql("SELECT count(*) FROM orders WHERE city = :city", args={"city": "Pune"}).first()[0])
print("DataFrame in SQL:", spark.sql("SELECT count(*) FROM {t} WHERE amount > {m}", t=o, m=900).first()[0])

print("== 7) SQL pipe syntax (Spark 4)")
spark.sql("""FROM orders
             |> WHERE status = 'CANCELLED'
             |> AGGREGATE count(*) AS cancelled GROUP BY city
             |> ORDER BY cancelled DESC
             |> LIMIT 3""").show()

print("== 8) SQL errors are analysis errors")
for q in ("SELECT cty FROM orders", "SELECT city, sum(amount) FROM orders"):
    try:
        spark.sql(q).collect()
    except Exception as e:
        print(type(e).__name__, short(e, 150))

print("== 9) the catalog")
print([(t.name, t.isTemporary, t.tableType) for t in spark.catalog.listTables()])
