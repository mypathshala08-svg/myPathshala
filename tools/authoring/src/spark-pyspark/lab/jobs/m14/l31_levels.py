from pyspark import StorageLevel
from pyspark.sql import SparkSession
names = [n for n in dir(StorageLevel) if n.isupper()]
print("== 1) every StorageLevel constant in PySpark 4.3 (useDisk, useMemory, useOffHeap, deserialized, replication)")
for n in names:
    s = getattr(StorageLevel, n)
    print(f"  {n:24s} disk={str(s.useDisk):5s} memory={str(s.useMemory):5s} offHeap={str(s.useOffHeap):5s} deserialized={str(s.deserialized):5s} replication={s.replication}")
print("  _SER names present:", [n for n in names if "SER" in n])
spark = SparkSession.builder.master("local-cluster[2,1,1024]").appName("l31b").config("spark.ui.showConsoleProgress", "false").getOrCreate() if False else None
spark = SparkSession.builder.master("local[2]").appName("l31b").config("spark.ui.showConsoleProgress", "false").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
df = spark.range(1_000_000)
df.persist(StorageLevel.MEMORY_AND_DISK_2); df.count()
print("== 2) persist(MEMORY_AND_DISK_2) then df.storageLevel:", df.storageLevel)
custom = StorageLevel(True, True, False, False, 3)
print("== 3) a custom level StorageLevel(True, True, False, False, 3):", custom)
rdd = spark.sparkContext.parallelize(range(10)).persist(StorageLevel.MEMORY_ONLY)
print("  RDD in PySpark, MEMORY_ONLY -> getStorageLevel():", rdd.getStorageLevel(), "| deserialized:", rdd.getStorageLevel().deserialized)
spark.stop()
