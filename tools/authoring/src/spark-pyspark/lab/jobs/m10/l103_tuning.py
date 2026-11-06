"""10.3 Evaluation, tuning and saving models."""
import time, os, shutil
from pyspark.sql import SparkSession, functions as F
from pyspark.ml import Pipeline, PipelineModel
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler, Imputer, StandardScaler
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator, TrainValidationSplit
from pyspark.ml.functions import vector_to_array
spark = SparkSession.builder.master("local[4]").config("spark.driver.memory", "3g").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
df = spark.read.parquet("/root/lab/spark/data/m10/customers.parquet")
train, test = df.randomSplit([0.8, 0.2], seed=7); train.cache().count(); test.cache().count()
num = ["orders_30d", "avg_amount", "days_since_last", "complaints", "late_pct", "tenure_months"]
lr = LogisticRegression(featuresCol="sfeatures", labelCol="churned", maxIter=50)
pipe = Pipeline(stages=[
    Imputer(inputCols=["avg_amount", "late_pct"], outputCols=["avg_amount", "late_pct"], strategy="median"),
    StringIndexer(inputCols=["city", "plan"], outputCols=["city_idx", "plan_idx"], handleInvalid="keep"),
    OneHotEncoder(inputCols=["city_idx", "plan_idx"], outputCols=["city_oh", "plan_oh"]),
    VectorAssembler(inputCols=num + ["city_oh", "plan_oh"], outputCol="features"),
    StandardScaler(inputCol="features", outputCol="sfeatures"), lr])
model = pipe.fit(train); pred = model.transform(test).cache()
print("== 1) metrics")
for m in ("areaUnderROC", "areaUnderPR"):
    print(f"{m:13}: {BinaryClassificationEvaluator(labelCol='churned', metricName=m).evaluate(pred):.4f}")
for m in ("accuracy", "f1", "weightedPrecision", "weightedRecall"):
    print(f"{m:17}: {MulticlassClassificationEvaluator(labelCol='churned', metricName=m).evaluate(pred):.4f}")
print("baseline accuracy (always 'no churn'):", round(1 - test.agg(F.avg("churned")).first()[0], 4))
print("== 2) confusion matrix at threshold 0.5")
pred.groupBy("churned", "prediction").count().orderBy("churned", "prediction").show()
print("== 3) moving the threshold")
p1 = pred.withColumn("p", vector_to_array("probability")[1])
for th in (0.3, 0.5, 0.7):
    r = p1.select(F.sum(F.when((F.col("p") >= th) & (F.col("churned") == 1), 1).otherwise(0)).alias("tp"),
                  F.sum(F.when((F.col("p") >= th) & (F.col("churned") == 0), 1).otherwise(0)).alias("fp"),
                  F.sum(F.when((F.col("p") < th) & (F.col("churned") == 1), 1).otherwise(0)).alias("fn")).first()
    print(f"threshold {th}: flagged {r.tp + r.fp:5} | precision {r.tp / (r.tp + r.fp):.3f} | recall {r.tp / (r.tp + r.fn):.3f}")
print("== 4) tuning: TrainValidationSplit vs CrossValidator")
grid = ParamGridBuilder().addGrid(lr.regParam, [0.0, 0.01, 0.1]).addGrid(lr.elasticNetParam, [0.0, 0.5]).build()
ev = BinaryClassificationEvaluator(labelCol="churned")
print("grid size:", len(grid))
for name, tuner in (("TrainValidationSplit(0.8)", TrainValidationSplit(estimator=pipe, estimatorParamMaps=grid, evaluator=ev, trainRatio=0.8, parallelism=2, seed=3)),
                    ("CrossValidator(3 folds)", CrossValidator(estimator=pipe, estimatorParamMaps=grid, evaluator=ev, numFolds=3, parallelism=2, seed=3))):
    t = time.time(); tm = tuner.fit(train); el = time.time() - t
    metrics = tm.validationMetrics if hasattr(tm, "validationMetrics") else tm.avgMetrics
    best = tm.bestModel.stages[-1]
    print(f"{name:26}: {el:5.1f} s | models fit ~{len(grid) * (1 if 'Train' in name else 3) + 1} | best regParam {best.getRegParam()} elasticNet {best.getElasticNetParam()} | test AUC {ev.evaluate(tm.transform(test)):.4f}")
    print("   metric per grid point:", [round(float(m), 4) for m in metrics])
print("== 5) save and load the PipelineModel")
path = "/root/lab/spark/data/m10/churn_model_v1"; shutil.rmtree(path, ignore_errors=True)
model.write().overwrite().save(path)
print("saved:", sorted(os.listdir(path)), "| stages:", sorted(os.listdir(path + "/stages")))
loaded = PipelineModel.load(path)
a = model.transform(test).select("customer_id", "probability"); b = loaded.transform(test).select("customer_id", F.col("probability").alias("p2"))
same = a.join(b, "customer_id").filter(vector_to_array("probability")[1] != vector_to_array("p2")[1]).count()
print("rows with different predictions after reload:", same)
print("size on disk (KB):", round(sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(path) for f in fs) / 1024, 1))
print("== 6) batch scoring with the loaded model")
t = time.time(); n = loaded.transform(df).filter(vector_to_array("probability")[1] >= 0.7).count()
print(f"scored 200,000 customers in {time.time()-t:.1f} s | high-risk (p >= 0.7): {n}")
