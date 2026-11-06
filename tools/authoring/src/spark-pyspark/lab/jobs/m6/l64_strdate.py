"""6.4 String and date functions."""
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master("local[2]").getOrCreate()
def short(e, n=200):
    return str(e).split("\n")[0][:n]
r = spark.createDataFrame([
    ("  Ravi KUMAR ", "ravi.k@Mail.in", "+91 98200-11122", "Pune, MH 411001", "TG-2026-000781"),
    ("asha nair", "ASHA@tiffingo.IN", "9820011133", "Navi Mumbai, MH 400703", "TG-2026-001902")],
    "name STRING, email STRING, phone STRING, address STRING, ref STRING")

print("== 1) cleaning text")
r.select(F.initcap(F.trim("name")).alias("name"), F.lower("email").alias("email"),
         F.regexp_replace("phone", r"[^0-9]", "").alias("digits"),
         F.right(F.regexp_replace("phone", r"[^0-9]", ""), F.lit(10)).alias("phone10")).show(truncate=False)

print("== 2) extracting parts")
r.select(F.split("address", ",")[0].alias("city"), F.regexp_extract("address", r"(\d{6})", 1).alias("pin"),
         F.split_part("ref", F.lit("-"), F.lit(3)).cast("int").alias("ref_no"),
         F.substring_index("email", "@", -1).alias("domain"), F.concat_ws(" / ", "name", "ref").alias("label")).show(truncate=False)

print("== 3) parsing dates and timestamps")
d = spark.createDataFrame([("2026-11-04",), ("04/11/2026",), ("2026-02-30",)], "s STRING")
d.select("s", F.try_to_date("s").alias("iso"), F.try_to_date("s", "dd/MM/yyyy").alias("dmy"),
         F.coalesce(F.try_to_date("s"), F.try_to_date("s", "dd/MM/yyyy")).alias("either")).show()
try:
    d.select(F.to_date("s")).collect()
except Exception as e:
    print("to_date under ANSI:", type(e).__name__, short(e, 150))

print("== 4) date arithmetic")
t = spark.createDataFrame([("2026-10-29 20:49:00", "2026-11-04")], "ts STRING, today STRING").select(F.to_timestamp("ts").alias("ts"), F.to_date("today").alias("today"))
t.select(F.datediff("today", "ts").alias("days_since"), F.date_add("today", 30).alias("plus30"),
         F.add_months("today", 1).alias("next_month"), F.last_day("today").alias("month_end"),
         F.date_trunc("week", "ts").alias("week_start"), F.dayofweek("ts").alias("dow"), F.date_format("ts", "EEE, d MMM HH:mm").alias("pretty")).show(truncate=False)

print("== 5) week-based year: YYYY vs yyyy")
y = spark.createDataFrame([("2026-12-28",), ("2026-12-31",), ("2027-01-01",)], "s STRING").select(F.to_date("s").alias("d"))
y.select("d", F.date_format("d", "yyyy").alias("yyyy")).show()
try:
    y.select(F.date_format("d", "YYYY")).show()
except Exception as e:
    print("YYYY:", type(e).__name__, " ".join(str(e).split("\n")[:2])[:330])
y.select("d", F.year("d").alias("year"), F.weekofyear("d").alias("iso_week")).show()

print("== 6) time zones")
print("session time zone:", spark.conf.get("spark.sql.session.timeZone"))
z = spark.createDataFrame([("2026-11-04 15:30:00",)], "s STRING").select(F.to_timestamp("s").alias("ts"))
z.select("ts", F.unix_timestamp("ts").alias("epoch"), F.to_utc_timestamp("ts", "Asia/Kolkata").alias("as_utc"),
         F.from_utc_timestamp(F.to_utc_timestamp("ts", "Asia/Kolkata"), "America/New_York").alias("in_new_york")).show(truncate=False)
spark.conf.set("spark.sql.session.timeZone", "UTC")
print("same epoch, session UTC:", z.select(F.unix_timestamp("ts")).first()[0], "| shown as", z.select(F.col("ts").cast("string")).first()[0])
spark.conf.set("spark.sql.session.timeZone", "Asia/Kolkata")
print("same rows, session Asia/Kolkata:", z.select(F.col("ts").cast("string")).first()[0])

print("== 7) like, rlike, contains")
o = spark.read.csv("/root/lab/spark/data/tiffingo/customers.csv", header=True)
print("names starting with A:", o.where(F.col("name").startswith("A")).count(),
      "| like 'A%':", o.where(F.col("name").like("A%")).count(),
      "| rlike '^(Aarav|Ananya) ':", o.where(F.col("name").rlike("^(Aarav|Ananya) ")).count(),
      "| ilike '%iyer':", o.where(F.col("name").ilike("%iyer")).count())
