from pyspark.sql import SparkSession
for master in ["local[1]", "local[2]", "local[*]"]:
    spark = SparkSession.builder.master(master).getOrCreate()
    sc = spark.sparkContext
    execs = sc._jsc.sc().getExecutorMemoryStatus().size()
    print(f"{master:9} defaultParallelism={sc.defaultParallelism}  JVMs holding executors={execs} (the driver itself)")
    spark.stop()
