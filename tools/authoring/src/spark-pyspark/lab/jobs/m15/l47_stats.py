import time, random
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master("local[2]").appName("l47").getOrCreate()
random.seed(7)
cities = ["Mumbai", "Pune", "Delhi"]; pays = ["UPI", "Card", "Cash"]
rows = []
for i in range(200000):
    c = random.choices(cities, [5, 2, 3])[0]; p = random.choices(pays, [6, 3, 1])[0]
    km = round(random.uniform(0.5, 12), 1)
    mins = round(12 + 2.6 * km + random.gauss(0, 4), 1)
    amt = int(random.lognormvariate(5.3, 0.45))
    rows.append((i, c, p, km, mins, amt))
df = spark.createDataFrame(rows, "order_id int, city string, pay string, km double, mins double, amount int").cache()
df.count()
print("== 1) describe() vs summary()")
df.select("km", "mins", "amount").describe().show()
df.select("amount").summary("count", "min", "25%", "50%", "75%", "max").show()
print("== 2) approxQuantile: accuracy vs time (amount, median and p95)")
for err in [0.1, 0.01, 0.0]:
    t = time.time(); q = df.approxQuantile("amount", [0.5, 0.95], err)
    print(f"  relativeError {err:<5} -> {q}  {time.time()-t:.2f} s")
print("== 3) correlation and covariance")
print("  corr(km, mins)   =", round(df.stat.corr("km", "mins"), 3))
print("  corr(km, amount) =", round(df.stat.corr("km", "amount"), 3))
print("  cov(km, mins)    =", round(df.stat.cov("km", "mins"), 2))
print("== 4) crosstab city x pay")
df.stat.crosstab("city", "pay").orderBy("city_pay").show()
print("== 5) freqItems (approximate, may include false positives)")
print(" ", df.stat.freqItems(["pay"], 0.25).collect()[0][0])
print("== 6) sample(fraction=0.01) is not exact")
for s in [1, 2, 3]:
    print(f"  seed {s}: {df.sample(fraction=0.01, seed=s).count()} rows")
print("== 7) sampleBy: stratified by city")
st = df.sampleBy("city", {"Mumbai": 0.01, "Pune": 0.05, "Delhi": 0.0}, seed=1)
st.groupBy("city").count().orderBy("city").show()
print("== 8) randomSplit([0.8, 0.2])")
a, b = df.randomSplit([0.8, 0.2], seed=42)
print(f"  train {a.count()}  test {b.count()}")
