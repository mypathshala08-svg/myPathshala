"""7.2 Tables, catalog and the Hive metastore. Run twice: 'create' then 'reopen'."""
import sys, os, shutil, glob
from pyspark.sql import SparkSession, functions as F
mode = sys.argv[1]
W = "/root/lab/spark/data/m7/warehouse"
os.chdir("/root/lab/spark/data/m7")            # metastore_db (Derby) is created here
spark = (SparkSession.builder.master("local[2]").appName("catalog-" + mode)
         .config("spark.sql.warehouse.dir", W).config("spark.sql.shuffle.partitions", "4")
         .enableHiveSupport().getOrCreate())
def short(e, n=170):
    return str(e).split("\n")[0][:n]
def files(p):
    return len([f for f in glob.glob(p + "/**", recursive=True) if f.endswith(".parquet")])

if mode == "create":
    print("== 1) catalog implementation:", spark.conf.get("spark.sql.catalogImplementation"))
    spark.sql("CREATE DATABASE IF NOT EXISTS tiffingo")
    print("databases:", [d.name for d in spark.catalog.listDatabases()])
    o = spark.read.parquet("/root/lab/spark/data/orders_big").limit(200_000)

    print("== 2) managed table")
    o.write.mode("overwrite").saveAsTable("tiffingo.orders_m")
    print("files under warehouse:", files(W + "/tiffingo.db/orders_m"))

    print("== 3) external table")
    ext = "/root/lab/spark/data/m7/ext_orders"
    shutil.rmtree(ext, ignore_errors=True)
    o.write.parquet(ext)
    spark.sql(f"CREATE TABLE tiffingo.orders_x USING parquet LOCATION '{ext}'")
    for t in ("orders_m", "orders_x"):
        d = {r.col_name: r.data_type for r in spark.sql(f"DESCRIBE TABLE EXTENDED tiffingo.{t}").collect()}
        print(t, "| Type:", d.get("Type"), "| Location:", d.get("Location"))

    print("== 4) partitioned table and partitions")
    o.write.mode("overwrite").partitionBy("city").saveAsTable("tiffingo.orders_p")
    print(spark.sql("SHOW PARTITIONS tiffingo.orders_p").count(), "partitions")

    print("== 5) statistics")
    print("before ANALYZE:", [r.data_type for r in spark.sql("DESCRIBE TABLE EXTENDED tiffingo.orders_m").collect() if r.col_name == "Statistics"])
    spark.sql("ANALYZE TABLE tiffingo.orders_m COMPUTE STATISTICS FOR COLUMNS city, amount")
    print("after ANALYZE :", [r.data_type for r in spark.sql("DESCRIBE TABLE EXTENDED tiffingo.orders_m").collect() if r.col_name == "Statistics"])
    spark.sql("DESCRIBE TABLE EXTENDED tiffingo.orders_m city").show(truncate=False)

    print("== 6) catalog API")
    print([(t.name, t.tableType, t.isTemporary) for t in spark.catalog.listTables("tiffingo")])
    print([(c.name, c.dataType, c.isPartition) for c in spark.catalog.listColumns("tiffingo.orders_p")][-2:])
    o.createOrReplaceTempView("tmp_orders")
    print("temp view listed:", [t.name for t in spark.catalog.listTables() if t.isTemporary])

else:
    print("== 7) a NEW application")
    print("tables:", [(t.name, t.tableType) for t in spark.catalog.listTables("tiffingo")])
    print("temp view survives?", spark.catalog.tableExists("tmp_orders"))
    print("orders_m rows:", spark.table("tiffingo.orders_m").count())
    print("== 8) DROP managed vs external")
    spark.sql("DROP TABLE tiffingo.orders_m"); spark.sql("DROP TABLE tiffingo.orders_x")
    print("managed files left :", files(W + "/tiffingo.db/orders_m"))
    print("external files left:", files("/root/lab/spark/data/m7/ext_orders"))
    print("== 9) new files in a partition folder are invisible until repaired")
    src = W + "/tiffingo.db/orders_p"
    spark.read.parquet("/root/lab/spark/data/orders_big").limit(10).drop("city").write.mode("overwrite").parquet(src + "/city=Surat")
    print("Surat rows before:", spark.table("tiffingo.orders_p").where("city='Surat'").count())
    spark.sql("MSCK REPAIR TABLE tiffingo.orders_p")
    print("Surat rows after MSCK REPAIR:", spark.table("tiffingo.orders_p").where("city='Surat'").count())
    print("metastore files:", sorted(os.listdir("/root/lab/spark/data/m7/metastore_db"))[:4])
