import random, time
from pyspark.sql import SparkSession, functions as F
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler
from pyspark.ml.regression import LinearRegression, RandomForestRegressor, GBTRegressor
from pyspark.ml.evaluation import RegressionEvaluator
spark = SparkSession.builder.master("local[2]").appName("l105").getOrCreate()
random.seed(11)
rows = []
for i in range(60000):
    km = round(random.uniform(0.5, 12), 1); hour = random.randint(8, 23)
    rain = 1 if random.random() < 0.2 else 0; city = random.choice(["Mumbai", "Pune", "Delhi"])
    peak = 1 if hour in (13, 14, 20, 21) else 0
    mins = 10 + 2.5 * km + 6 * rain + 7 * peak + (4 if city == "Mumbai" else 0) + (5 if (rain and km > 8) else 0) + random.gauss(0, 3)
    rows.append((km, hour, rain, city, round(mins, 1)))
df = spark.createDataFrame(rows, "km double, hour int, rain int, city string, mins double")
train, test = df.randomSplit([0.8, 0.2], seed=42)
prep = [StringIndexer(inputCol="city", outputCol="ci"), OneHotEncoder(inputCols=["ci"], outputCols=["cv"]),
        VectorAssembler(inputCols=["km", "hour", "rain", "cv"], outputCol="features")]
ev = {m: RegressionEvaluator(labelCol="mins", metricName=m) for m in ["rmse", "mae", "r2"]}
print("== 1) LinearRegression: delivery minutes from km, hour, rain, city")
lr = Pipeline(stages=prep + [LinearRegression(labelCol="mins")]).fit(train)
m = lr.stages[-1]
print("  feature order: km, hour, rain, city=" + ", city=".join(lr.stages[0].labels[:-1]))
print("  coefficients:", [round(float(c), 2) for c in m.coefficients], " intercept:", round(m.intercept, 2))
print("  train R2:", round(m.summary.r2, 3), " train RMSE:", round(m.summary.rootMeanSquaredError, 2))
print("== 2) three regressors on the same test set")
feats_peak = prep[:2] + [VectorAssembler(inputCols=["km", "hour", "rain", "cv"], outputCol="features")]
for name, est in [("LinearRegression", LinearRegression(labelCol="mins")),
                  ("RandomForestRegressor", RandomForestRegressor(labelCol="mins", numTrees=40, maxDepth=8, seed=1)),
                  ("GBTRegressor", GBTRegressor(labelCol="mins", maxIter=40, maxDepth=5, seed=1))]:
    t = time.time(); p = Pipeline(stages=prep + [est]).fit(train).transform(test)
    print(f"  {name:<22} RMSE {ev['rmse'].evaluate(p):5.2f}  MAE {ev['mae'].evaluate(p):5.2f}  R2 {ev['r2'].evaluate(p):.3f}  {time.time()-t:4.1f} s")
print("== 3) why trees win: hour is not linear (peak at lunch and dinner)")
p = lr.transform(test).withColumn("err", F.col("prediction") - F.col("mins"))
p.groupBy("hour").agg(F.round(F.avg("err"), 1).alias("avg_error_lr")).filter(F.col("hour").isin(12, 13, 17, 20)).orderBy("hour").show()
print("== 4) feature importances (GBT)")
g = Pipeline(stages=prep + [GBTRegressor(labelCol="mins", maxIter=40, maxDepth=5, seed=1)]).fit(train).stages[-1]
gm = Pipeline(stages=prep + [GBTRegressor(labelCol="mins", maxIter=40, maxDepth=5, seed=1)]).fit(train)
labels = gm.stages[0].labels
g = gm.stages[-1]
for n, v in zip(["km", "hour", "rain"] + ["city=" + l for l in labels[:-1]], g.featureImportances.toArray()):
    print(f"  {n:<16} {v:.3f}")
print("== 5) a new order: 9 km, 20:00, raining, Mumbai")
new = spark.createDataFrame([(9.0, 20, 1, "Mumbai", 0.0)], df.schema)
print("  linear :", round(lr.transform(new).first().prediction, 1), "min")
print("  GBT    :", round(Pipeline(stages=prep + [GBTRegressor(labelCol="mins", maxIter=40, maxDepth=5, seed=1)]).fit(train).transform(new).first().prediction, 1), "min")
