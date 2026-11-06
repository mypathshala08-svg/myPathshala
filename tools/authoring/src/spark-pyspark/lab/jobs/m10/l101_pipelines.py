"""10.1 ML Pipelines: transformers, estimators, PipelineModel."""
import time
from pyspark.sql import SparkSession, functions as F
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler, Imputer
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator
spark = SparkSession.builder.master("local[4]").config("spark.driver.memory", "3g").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
df = spark.read.parquet("/root/lab/spark/data/m10/customers.parquet")
print("== 1) data"); print("rows", df.count(), "| churn rate", round(df.agg(F.avg("churned")).first()[0], 3)); df.show(3)
train, test = df.randomSplit([0.8, 0.2], seed=7)
print("train", train.count(), "| test", test.count())
print("== 2) a transformer vs an estimator")
idx = StringIndexer(inputCol="plan", outputCol="plan_idx")
print("StringIndexer is an Estimator:", type(idx).__mro__[1].__name__)
idx_model = idx.fit(train)
print("fit() returned:", type(idx_model).__name__, "| labels:", idx_model.labels)
idx_model.transform(train).select("plan", "plan_idx").distinct().orderBy("plan_idx").show()
va = VectorAssembler(inputCols=["orders_30d", "days_since_last"], outputCol="v")
print("VectorAssembler is a Transformer (no fit):", hasattr(va, "fit")); va.transform(train).select("orders_30d", "days_since_last", "v").show(2, truncate=False)
print("== 3) the full pipeline")
num = ["orders_30d", "avg_amount", "days_since_last", "complaints", "late_pct", "tenure_months"]
stages = [
    Imputer(inputCols=["avg_amount", "late_pct"], outputCols=["avg_amount", "late_pct"], strategy="median"),
    StringIndexer(inputCols=["city", "plan"], outputCols=["city_idx", "plan_idx"], handleInvalid="keep"),
    OneHotEncoder(inputCols=["city_idx", "plan_idx"], outputCols=["city_oh", "plan_oh"]),
    VectorAssembler(inputCols=num + ["city_oh", "plan_oh"], outputCol="features"),
    LogisticRegression(featuresCol="features", labelCol="churned", maxIter=50),
]
pipe = Pipeline(stages=stages)
t = time.time(); model = pipe.fit(train); print(f"fit: {time.time()-t:.1f} s ->", type(model).__name__)
print("stages after fit:", [type(s).__name__ for s in model.stages])
pred = model.transform(test)
print("new columns:", [c for c in pred.columns if c not in df.columns])
pred.select("customer_id", "churned", "rawPrediction", "probability", "prediction").show(3, truncate=False)
auc = BinaryClassificationEvaluator(labelCol="churned").evaluate(pred)
print("test AUC:", round(auc, 4))
print("features vector size:", pred.first()["features"].size)
print("== 4) unseen category at scoring time")
new = spark.createDataFrame([(999001, "Surat", "Gold", 3, 250.0, 40, 2, 30.0, 5, 0)], df.schema)
print("handleInvalid=keep:", model.transform(new).select("city", "city_idx", "prediction").collect())
strict = Pipeline(stages=[StringIndexer(inputCol="city", outputCol="city_idx")]).fit(train)
try:
    strict.transform(new).collect()
except Exception as e:
    m = str(e); i = m.find("Unseen label"); print("handleInvalid=error:", m[i:i+88] if i >= 0 else m.splitlines()[0][:150])
print("== 5) nulls without an Imputer")
noimp = Pipeline(stages=stages[1:])
try:
    noimp.fit(train).transform(test).count()
except Exception as e:
    m = str(e); i = m.find("Encountered null"); print("ERROR:", m[i:i+190].replace("\n", " ") if i >= 0 else m.splitlines()[0][:160])
