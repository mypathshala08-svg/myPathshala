import json, urllib.request
from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local[2]").getOrCreate()
sc = spark.sparkContext
lines = sc.textFile("/root/lab/spark/data/tiffingo/reviews")
def jobs():
    u = f"{sc.uiWebUrl}/api/v1/applications/{sc.applicationId}/jobs"
    return json.load(urllib.request.urlopen(u))
lines.map(lambda l: l.upper()).take(5)
j = sorted(jobs(), key=lambda j: j["jobId"])
print("take(5): %d job(s), tasks %s" % (len(j), [x["numTasks"] for x in j]))
n0 = len(j)
lines.map(lambda l: l.upper()).count()
j = sorted(jobs(), key=lambda j: j["jobId"])[n0:]
print("count() : %d job(s), tasks %s" % (len(j), [x["numTasks"] for x in j]))
spark.stop()
