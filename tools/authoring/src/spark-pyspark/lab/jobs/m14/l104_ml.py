import random
from pyspark.sql import SparkSession, functions as F
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator, RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.ml.fpm import FPGrowth
spark = SparkSession.builder.master("local[2]").appName("l104").config("spark.ui.showConsoleProgress", "false").getOrCreate()
spark.sparkContext.setLogLevel("ERROR"); random.seed(7)
# customers: three hidden behaviours
rows = []
for i in range(3000):
    g = i % 3
    o, s = [(random.gauss(4, 1), random.gauss(180, 30)), (random.gauss(15, 3), random.gauss(220, 40)), (random.gauss(6, 2), random.gauss(650, 90))][g]
    rows.append((i, max(o, 0.5), max(s, 50.0)))
cust = spark.createDataFrame(rows, "customer_id int, orders_per_month double, avg_spend double")
vec = VectorAssembler(inputCols=["orders_per_month", "avg_spend"], outputCol="raw").transform(cust)
scaled = StandardScaler(inputCol="raw", outputCol="features", withMean=True).fit(vec).transform(vec)
print("== 1) KMeans: choose k with the silhouette score (3,000 customers, scaled features)")
ev = ClusteringEvaluator()
for k in [2, 3, 4, 5]:
    m = KMeans(k=k, seed=1).fit(scaled)
    print(f"  k={k}  silhouette {ev.evaluate(m.transform(scaled)):.3f}")
m = KMeans(k=3, seed=1).fit(scaled)
print("== 2) the three segments (k=3)")
(m.transform(scaled).groupBy("prediction").agg(F.count("*").alias("customers"), F.round(F.avg("orders_per_month"), 1).alias("orders_pm"), F.round(F.avg("avg_spend")).alias("avg_spend"))
 .orderBy("prediction").show())
# ratings: users like dishes of their taste group
dishes = ["idli", "dosa", "vada", "upma", "thali", "biryani", "paneer", "naan", "lassi", "kulfi", "jalebi", "rasgulla"]
taste = {0: {"idli", "dosa", "vada", "upma"}, 1: {"thali", "biryani", "paneer", "naan"}, 2: {"lassi", "kulfi", "jalebi", "rasgulla"}}
r = []
for u in range(1500):
    likes = taste[u % 3]
    for d_i, d in enumerate(dishes):
        if random.random() < 0.6:
            r.append((u, d_i, float(min(5, max(1, round(random.gauss(4.5 if d in likes else 2.0, 0.6)))))))
ratings = spark.createDataFrame(r, "user int, dish int, rating float")
train, test = ratings.randomSplit([0.8, 0.2], seed=3)
test = test.union(spark.createDataFrame([(9999, 0, 4.0)], "user int, dish int, rating float"))   # a brand-new user
print(f"== 3) ALS collaborative filtering ({ratings.count():,} ratings, 1,500 users, 12 dishes)")
for cs in ["nan", "drop"]:
    als = ALS(userCol="user", itemCol="dish", ratingCol="rating", rank=3, maxIter=20, regParam=0.05, coldStartStrategy=cs, seed=1)
    model = als.fit(train)
    pred = model.transform(test)
    rmse = RegressionEvaluator(metricName="rmse", labelCol="rating").evaluate(pred)
    print(f"  coldStartStrategy={cs:4s}  RMSE {rmse}")
names = spark.createDataFrame(list(enumerate(dishes)), "dish int, name string")
recs = model.recommendForUserSubset(spark.createDataFrame([(0,), (1,), (2,)], "user int"), 3)
print("== 4) top-3 recommendations (user 0 = south Indian taste, 1 = meals, 2 = desserts)")
for row in recs.orderBy("user").collect():
    print(f"  user {row.user}: " + ", ".join(f"{dishes[x.dish]} {x.rating:.1f}" for x in row.recommendations))
print("== 5) FPGrowth: what is ordered together?")
baskets = []
for b in range(2000):
    base = random.choice([["idli", "vada", "chai"], ["dosa", "chutney", "chai"], ["thali", "lassi"], ["biryani", "raita", "kulfi"]])
    items = [x for x in base if random.random() < 0.85] + ([random.choice(["water", "papad"])] if random.random() < 0.3 else [])
    if items: baskets.append((b, sorted(set(items))))
fp = FPGrowth(itemsCol="items", minSupport=0.1, minConfidence=0.6).fit(spark.createDataFrame(baskets, "id int, items array<string>"))
(fp.associationRules.orderBy(F.desc("lift")).select(F.concat_ws("+", "antecedent").alias("if"), F.concat_ws("+", "consequent").alias("then"),
  F.round("confidence", 2).alias("conf"), F.round("lift", 1).alias("lift")).show(6, truncate=False))
spark.stop()
