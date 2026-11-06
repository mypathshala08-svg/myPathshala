"""10.2 Feature engineering and classification: scaling, buckets, 4 classifiers."""
import time
from pyspark.sql import SparkSession, functions as F
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler, Imputer, StandardScaler, Bucketizer
from pyspark.ml.classification import LogisticRegression, DecisionTreeClassifier, RandomForestClassifier, GBTClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator
spark = SparkSession.builder.master("local[4]").config("spark.driver.memory", "3g").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
df = spark.read.parquet("/root/lab/spark/data/m10/customers.parquet")
train, test = df.randomSplit([0.8, 0.2], seed=7); train.cache().count(); test.cache().count()
num = ["orders_30d", "avg_amount", "days_since_last", "complaints", "late_pct", "tenure_months"]
prep = [Imputer(inputCols=["avg_amount", "late_pct"], outputCols=["avg_amount", "late_pct"], strategy="median"),
        StringIndexer(inputCols=["city", "plan"], outputCols=["city_idx", "plan_idx"], handleInvalid="keep"),
        OneHotEncoder(inputCols=["city_idx", "plan_idx"], outputCols=["city_oh", "plan_oh"])]
print("== 1) Imputer: what it filled")
im = prep[0].fit(train); print("medians:", dict(zip(["avg_amount", "late_pct"], [round(float(v), 1) for v in im.surrogateDF.first()])))
print("nulls before:", train.filter("avg_amount IS NULL").count(), "| after:", im.transform(train).filter("avg_amount IS NULL").count())
print("== 2) StandardScaler")
va = VectorAssembler(inputCols=["orders_30d", "avg_amount", "days_since_last"], outputCol="raw")
p = Pipeline(stages=[prep[0], va, StandardScaler(inputCol="raw", outputCol="scaled", withMean=True, withStd=True)]).fit(train)
r = p.transform(train).select("raw", "scaled").first(); print("raw   :", [round(float(x), 2) for x in r["raw"]]); print("scaled:", [round(float(x), 2) for x in r["scaled"]])
print("std of inputs:", [round(float(x), 1) for x in p.stages[-1].std])
print("== 3) Bucketizer: tenure bands")
bk = Bucketizer(splits=[0, 6, 12, 24, 48], inputCol="tenure_months", outputCol="tenure_band")
bk.transform(train).groupBy("tenure_band").agg(F.count("*").alias("customers"), F.round(F.avg("churned"), 3).alias("churn_rate")).orderBy("tenure_band").show()
print("== 4) four classifiers, same features")
feat = VectorAssembler(inputCols=num + ["city_oh", "plan_oh"], outputCol="features")
scaled = StandardScaler(inputCol="features", outputCol="sfeatures")
auc_e = BinaryClassificationEvaluator(labelCol="churned", rawPredictionCol="probability", metricName="areaUnderROC")
acc_e = MulticlassClassificationEvaluator(labelCol="churned", metricName="accuracy")
models = {
    "LogisticRegression": [scaled, LogisticRegression(featuresCol="sfeatures", labelCol="churned", maxIter=50)],
    "DecisionTree(depth 5)": [DecisionTreeClassifier(labelCol="churned", maxDepth=5)],
    "RandomForest(50 trees)": [RandomForestClassifier(labelCol="churned", numTrees=50, maxDepth=6, seed=1)],
    "GBT(50 iters)": [GBTClassifier(labelCol="churned", maxIter=50, maxDepth=4, seed=1)],
}
fitted = {}
for name, tail in models.items():
    t = time.time(); m = Pipeline(stages=prep + [feat] + tail).fit(train); ft = time.time() - t
    pr = m.transform(test); fitted[name] = m
    print(f"{name:24}: fit {ft:5.1f} s | AUC {auc_e.evaluate(pr):.4f} | accuracy {acc_e.evaluate(pr):.4f}")
print("== 5) what the models learned")
names = num + [f"city={c}" for c in fitted["GBT(50 iters)"].stages[1].labelsArray[0]] + [f"plan={c}" for c in fitted["GBT(50 iters)"].stages[1].labelsArray[1]]
lr = fitted["LogisticRegression"].stages[-1]
print("LR coefficients (scaled):", sorted([(n, round(float(c), 2)) for n, c in zip(names, lr.coefficients)], key=lambda x: -abs(x[1]))[:6])
rf = fitted["RandomForest(50 trees)"].stages[-1]
print("RF importances:", sorted([(n, round(float(v), 3)) for n, v in zip(names, rf.featureImportances.toArray())], key=lambda x: -x[1])[:6])
dt = fitted["DecisionTree(depth 5)"].stages[-1]; print("tree root:", dt.toDebugString.split("\n")[1].strip())
print("== 6) without scaling, LR with regularization")
for sc in (False, True):
    tail = ([scaled, LogisticRegression(featuresCol="sfeatures", labelCol="churned", regParam=0.1, maxIter=50)] if sc
            else [LogisticRegression(labelCol="churned", regParam=0.1, standardization=False, maxIter=50)])
    m = Pipeline(stages=prep + [feat] + tail).fit(train)
    print(f"regParam 0.1, scaled={sc}: AUC {auc_e.evaluate(m.transform(test)):.4f}")
