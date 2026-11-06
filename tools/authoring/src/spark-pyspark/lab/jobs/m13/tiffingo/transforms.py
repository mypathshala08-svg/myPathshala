"""TiffinGo capstone: pure transformations (unit-tested)."""
from pyspark.sql import DataFrame, functions as F, Window

ORDER_SCHEMA = "order_id string, customer_id string, rest_id string, order_ts string, amount string, status string"

def clean_orders(raw: DataFrame):
    """Return (valid, quarantine). Typed columns via try_cast; one row per order_id."""
    typed = raw.select(
        F.col("order_id").try_cast("long").alias("order_id"),
        F.col("customer_id").try_cast("int").alias("customer_id"),
        F.col("rest_id").try_cast("int").alias("rest_id"),
        F.col("order_ts").try_cast("timestamp").alias("order_ts"),
        F.col("amount").try_cast("int").alias("amount"),
        F.upper(F.trim("status")).alias("status"),
        F.col("amount").alias("amount_raw"))
    problem = (F.when(F.col("order_id").isNull(), "bad_order_id")
                .when(F.col("order_ts").isNull(), "bad_timestamp")
                .when(F.col("amount").isNull(), "bad_amount")
                .when(F.col("amount") < 0, "negative_amount"))
    typed = typed.withColumn("problem", problem)
    quarantine = typed.filter(F.col("problem").isNotNull())
    valid = (typed.filter(F.col("problem").isNull())
             .dropDuplicates(["order_id"])
             .withColumn("order_date", F.to_date("order_ts"))
             .drop("problem", "amount_raw"))
    return valid, quarantine

def clean_customers(raw: DataFrame) -> DataFrame:
    w = Window.partitionBy("customer_id").orderBy(F.col("signup_date").desc())
    return (raw.select(F.col("customer_id").try_cast("int").alias("customer_id"), "name", "city", "plan",
                       F.col("phone").try_cast("bigint").alias("phone"), F.col("signup_date").try_cast("date").alias("signup_date"))
            .withColumn("rn", F.row_number().over(w)).filter("rn = 1").drop("rn"))

def daily_city_revenue(orders: DataFrame, restaurants: DataFrame) -> DataFrame:
    return (orders.filter(F.col("status") == "DELIVERED")
            .join(F.broadcast(restaurants.select("rest_id", "city")), "rest_id")
            .groupBy("order_date", "city")
            .agg(F.count("*").alias("orders"), F.sum("amount").alias("revenue"),
                 F.round(F.avg("amount"), 1).alias("avg_order")))

def customer_features(orders: DataFrame, customers: DataFrame, as_of) -> DataFrame:
    o = orders.filter(F.col("status") == "DELIVERED")
    f = o.groupBy("customer_id").agg(F.count("*").alias("orders_14d"), F.sum("amount").alias("spend_14d"),
                                     F.datediff(F.lit(as_of), F.max("order_date")).alias("days_since_last"))
    return customers.join(f, "customer_id", "left").fillna({"orders_14d": 0, "spend_14d": 0, "days_since_last": 99})
