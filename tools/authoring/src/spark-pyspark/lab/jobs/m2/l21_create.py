"""Five ways to create an RDD, and what an RDD really is."""
from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local[2]").appName("rdd-basics").getOrCreate()
sc = spark.sparkContext
D = "/root/lab/spark/data/tiffingo"

print("1) parallelize a Python list")
amounts = sc.parallelize([530, 210, 480, 990, 120, 340], 3)
print("   ", amounts, "| partitions:", amounts.getNumPartitions())
print("    glom():", amounts.glom().collect())

print("2) textFile: one element per line")
items = sc.textFile(f"{D}/order_items.txt")
print("    partitions:", items.getNumPartitions(), "| lines:", items.count())
print("    first():", items.first())

print("3) textFile on a folder (3 files)")
reviews = sc.textFile(f"{D}/reviews")
print("    partitions:", reviews.getNumPartitions(), "| lines:", reviews.count())

print("4) wholeTextFiles: one element per FILE (path, content)")
whole = sc.wholeTextFiles(f"{D}/reviews")
print("    elements:", whole.count(), "|", [(p.split('/')[-1], len(c)) for p, c in whole.collect()])

print("5) from a DataFrame: df.rdd")
df = spark.read.csv(f"{D}/orders.csv", header=True)
rows = df.rdd
print("    type of element:", type(rows.first()).__name__, "|", rows.first()["city"], rows.first()["amount"])

print("\nImmutability: transformations return NEW RDDs")
big = amounts.filter(lambda a: a >= 300)
print("    amounts:", amounts.collect(), "\n    big    :", big.collect(), "| same object?", big is amounts)
print("\nLineage of big:")
print(big.toDebugString().decode())
spark.stop()
