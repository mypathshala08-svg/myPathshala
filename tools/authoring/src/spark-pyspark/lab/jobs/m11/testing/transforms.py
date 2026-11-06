from pyspark.sql import DataFrame, functions as F

def add_delivery_fee(orders: DataFrame) -> DataFrame:
    """Free delivery from Rs 500; otherwise Rs 40 (Rs 60 for Mumbai)."""
    fee = (F.when(F.col("amount") >= 500, 0)
            .when(F.col("city") == "Mumbai", 60)
            .otherwise(40))
    return orders.withColumn("delivery_fee", fee).withColumn("total", F.col("amount") + F.col("delivery_fee"))

def city_revenue(orders: DataFrame) -> DataFrame:
    return orders.groupBy("city").agg(F.sum("amount").alias("revenue"))
