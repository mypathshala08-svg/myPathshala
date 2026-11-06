"""4.4 Nulls and duplicates on a dirty sign-up export."""
from pyspark.sql import SparkSession, functions as F, Window
spark = SparkSession.builder.master("local[2]").config("spark.sql.shuffle.partitions", "4").getOrCreate()
path = "/root/lab/spark/data/tiffingo/signups"

print("== 1) what CSV turns into null")
raw = spark.read.csv(path, header=True, inferSchema=True)
raw.printSchema()
def nulls(df):
    return df.select([F.sum(F.col(c).isNull().cast("int")).alias(c) for c in df.columns])
nulls(raw).show()
print("city = 'NA' rows:", raw.where("city = 'NA'").count(), "| rating NaN rows:", raw.where(F.isnan("rating")).count())

print('== 2) read again with nullValue="NA"')
s = spark.read.csv(path, header=True, inferSchema=True, nullValue="NA")
nulls(s).show()
print("rating NaN still:", s.where(F.isnan("rating")).count())
s = s.withColumn("rating", F.when(F.isnan("rating"), None).otherwise(F.col("rating")))

print("== 3) null comparisons")
spark.sql("""SELECT NULL = NULL AS eq, NULL <=> NULL AS null_safe, NULL > 1 AS gt,
             NOT NULL AS not_null, NULL AND false AS and_false, NULL OR true AS or_true""").show()
print("city = 'Pune'       :", s.where(F.col("city") == "Pune").count())
print("city != 'Pune'      :", s.where(F.col("city") != "Pune").count())
print("city is null        :", s.where(F.col("city").isNull()).count())
print("total               :", s.count())
print("NOT eqNullSafe Pune :", s.where(~F.col("city").eqNullSafe("Pune")).count())

print("== 4) aggregates skip nulls")
s.select(F.count("*").alias("rows"), F.count("age").alias("count_age"), F.avg("age").alias("avg_age"),
         F.sum("age").alias("sum_age"), (F.sum("age") / F.count("*")).alias("sum_over_rows")).show()

print("== 5) na.drop")
print("any    :", s.na.drop().count())
print("all    :", s.na.drop(how="all").count())
print("thresh6:", s.na.drop(thresh=6).count())
print("subset :", s.na.drop(subset=["city", "phone"]).count())

print("== 6) na.fill is type-aware")
f1 = s.na.fill(0)
print("fill(0) nulls      :", f1.select([F.sum(F.col(c).isNull().cast("int")).alias(c) for c in s.columns]).first().asDict())
f2 = s.na.fill("unknown")
print("fill('unknown')    :", f2.select([F.sum(F.col(c).isNull().cast("int")).alias(c) for c in s.columns]).first().asDict())
f3 = s.na.fill({"city": "unknown", "referral": "none", "age": -1})
print("fill(dict) referral:", [r.referral for r in f3.groupBy("referral").count().orderBy("referral").collect()])
print("coalesce           :", s.select(F.coalesce(F.col("phone").cast("string"), F.lit("no phone")).alias("p")).where("p = 'no phone'").count())
print("na.replace         :", s.na.replace({"INSTA": "Instagram"}, subset=["referral"]).where("referral = 'Instagram'").count())

print("== 7) duplicates")
print("rows            :", s.count())
print("distinct        :", s.distinct().count())
print("by user_id      :", s.dropDuplicates(["user_id"]).count())
print("distinct users  :", s.select("user_id").distinct().count(), "|", s.select(F.countDistinct("user_id")).first()[0])

print("== 8) which row does dropDuplicates keep?")
for parts in (1, 3, 7):
    k = s.repartition(parts).dropDuplicates(["user_id"])
    tot = k.agg(F.sum(F.unix_timestamp("signed_up_at"))).first()[0]
    print(f"repartition({parts}) checksum of kept signed_up_at: {tot}")

print("== 9) keep the first sign-up, deterministically")
w = Window.partitionBy("user_id").orderBy(F.col("signed_up_at").asc(), F.col("city").asc_nulls_last())
first = s.withColumn("rn", F.row_number().over(w)).where("rn = 1").drop("rn")
print("rows:", first.count())
for parts in (1, 3, 7):
    print(f"repartition({parts}) checksum:", s.repartition(parts).withColumn("rn", F.row_number().over(w)).where("rn = 1")
          .agg(F.sum(F.unix_timestamp("signed_up_at"))).first()[0])

print("== 10) plans")
s.dropDuplicates(["user_id"]).explain()
