"""6.2 Joins: types, null keys, duplicates, ambiguity, strategies."""
import time
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master("local[4]").config("spark.sql.shuffle.partitions", "8").getOrCreate()
def short(e, n=190):
    return str(e).split("\n")[0][:n]
orders = spark.createDataFrame([(1, 101, "Pune"), (2, 102, "Delhi"), (3, 103, "Pune"), (4, None, "Mumbai"), (5, 109, "Pune")],
                               "order_id INT, rest_id INT, city STRING")
rest = spark.createDataFrame([(101, "Desai Mess", "Pune"), (102, "Nair Bhojanalay", "Delhi"), (103, "Patel Thali", "Pune"), (104, "Rao Tiffins", "Thane"), (None, "Unknown Kitchen", "Pune")],
                             "rest_id INT, name STRING, city STRING")

print("== 1) join types")
for how in ("inner", "left", "right", "full", "left_semi", "left_anti"):
    r = orders.join(rest.select("rest_id", "name"), "rest_id", how)
    print(f"{how:10}: {r.count()} rows | {sorted([(x.order_id if "order_id" in r.columns else None, x.name if "name" in r.columns else None) for x in r.collect()], key=str)}")

print("== 2) null keys never match")
print("== on null       :", orders.join(rest, orders.rest_id == rest.rest_id, "inner").where(orders.rest_id.isNull()).count())
print("eqNullSafe       :", orders.join(rest, orders.rest_id.eqNullSafe(rest.rest_id), "inner").where(orders.rest_id.isNull()).count())

print("== 3) ambiguous columns")
j = orders.join(rest, orders.rest_id == rest.rest_id)
print("columns:", j.columns)
try:
    j.select("city").show()
except Exception as e:
    print(type(e).__name__, short(e))
print("using a list of keys:", orders.join(rest, ["rest_id"]).columns)
j.select(orders.city.alias("order_city"), rest.city.alias("rest_city"), "name").show()

print("== 4) duplicate keys multiply rows")
promos = spark.createDataFrame([("Pune", "FEST20"), ("Pune", "NEW50"), ("Pune", "WEEKEND"), ("Delhi", "FEST20")], "city STRING, code STRING")
print("orders:", orders.count(), "| after join on city:", orders.join(promos, "city").count())
big = spark.read.parquet("/root/lab/spark/data/orders_big")
cities = spark.createDataFrame([("Pune", "MH"), ("Pune", "Maharashtra")], "city STRING, state STRING")
print("5M orders join a 2-row table with a duplicate key:", big.join(cities, "city").count(), "rows (Pune has", big.where("city='Pune'").count(), ")")

print("== 5) cross join")
print(orders.crossJoin(rest).count(), "rows")

print("== 6) strategies picked automatically")
custs = spark.read.csv("/root/lab/spark/data/tiffingo/customers.csv", header=True, inferSchema=True)
print("autoBroadcastJoinThreshold:", spark.conf.get("spark.sql.autoBroadcastJoinThreshold"))
for label, df in [("small dim", big.join(custs, "customer_id")),
                  ("two big", big.alias("a").join(big.select("order_id", F.col("amount").alias("a2")), "order_id"))]:
    p = df._jdf.queryExecution().executedPlan().toString()
    strat = [s for s in ("BroadcastHashJoin", "SortMergeJoin", "ShuffledHashJoin") if s in p]
    t = time.time(); n = df.count(); print(f"{label:10}: {strat} {n} rows {time.time()-t:.1f} s")
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)
t = time.time(); n = big.join(custs, "customer_id").count(); print(f"small dim, broadcast off: SortMergeJoin {n} rows {time.time()-t:.1f} s")
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "10485760")
t = time.time(); n = big.join(F.broadcast(custs), "customer_id").count(); print(f"hint broadcast(): {time.time()-t:.1f} s")

print("== 7) semi/anti: who never ordered?")
print("customers:", custs.count(), "| never ordered:", custs.join(big, "customer_id", "left_anti").count(),
      "| ordered:", custs.join(big, "customer_id", "left_semi").count())
