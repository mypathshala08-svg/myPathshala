from pyspark.sql import SparkSession, functions as F
from graphframes import GraphFrame
spark = (SparkSession.builder.master("local[2]").appName("l124").config("spark.ui.showConsoleProgress", "false")
         .config("spark.jars", ",".join("/root/lab/spark/jars/gf/" + j for j in [
             "graphframes-spark4_2.13-0.12.3.jar", "graphframes-graphx-spark4_2.13-0.12.3.jar", "datasketches-java-6.2.0.jar", "datasketches-memory-3.0.2.jar", "java-semver-0.10.2.jar"]))
         .getOrCreate())
spark.sparkContext.setLogLevel("ERROR"); spark.sparkContext.setCheckpointDir("/tmp/gf-ckpt")
v = spark.createDataFrame([("asha", "customer"), ("ravi", "customer"), ("meera", "customer"), ("kabir", "customer"), ("zoya", "customer"),
                           ("arjun", "customer"), ("neha", "customer"), ("om", "customer"), ("tara", "customer")], "id string, kind string")
e = spark.createDataFrame([("asha", "ravi", "referred"), ("asha", "meera", "referred"), ("ravi", "kabir", "referred"), ("meera", "kabir", "referred"),
                           ("kabir", "zoya", "referred"), ("zoya", "asha", "referred"), ("arjun", "neha", "referred"), ("neha", "om", "referred"),
                           ("tara", "tara", "referred")], "src string, dst string, relationship string")
g = GraphFrame(v, e)
print(f"== 1) referral graph: {g.vertices.count()} customers, {g.edges.count()} referrals")
print("== 2) degrees (who refers, who is referred)")
g.inDegrees.join(g.outDegrees, "id", "full").fillna(0).orderBy(F.desc("inDegree"), "id").show(5)
print("== 3) PageRank: most influential customers")
pr = g.pageRank(resetProbability=0.15, maxIter=10)
pr.vertices.select("id", F.round("pagerank", 3).alias("pagerank")).orderBy(F.desc("pagerank")).show(4)
print("== 4) connected components: separate referral communities")
cc = g.connectedComponents()
cc.groupBy("component").agg(F.sort_array(F.collect_list("id")).alias("members")).orderBy(F.size("members").desc()).show(truncate=False)
print("== 5) motif: chains a -> b -> c (two-step referrals)")
g.find("(a)-[]->(b); (b)-[]->(c)").filter("a.id != c.id").select(F.col("a.id").alias("a"), F.col("b.id").alias("b"), F.col("c.id").alias("c")).orderBy("a", "b").show(6)
print("== 6) shortest paths to kabir (hops)")
g.shortestPaths(landmarks=["kabir"]).select("id", F.col("distances")["kabir"].alias("hops_to_kabir")).orderBy("hops_to_kabir", "id").show(9)
spark.stop()
