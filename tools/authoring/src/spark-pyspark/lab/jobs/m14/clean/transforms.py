"""TiffinGo order transforms: small, pure, testable functions (DataFrame in, DataFrame out)."""
from pyspark.sql import DataFrame, functions as F

def only_valid(df: DataFrame) -> DataFrame:
    return df.filter((F.col("qty") > 0) & F.col("item").isNotNull())

def add_amount(prices: dict):
    def _f(df: DataFrame) -> DataFrame:
        m = F.create_map(*[x for k, v in prices.items() for x in (F.lit(k), F.lit(v))])
        return df.withColumn("amount", F.col("qty") * m[F.col("item")])
    return _f

def revenue_by_city(df: DataFrame) -> DataFrame:
    return df.groupBy("city").agg(F.sum("amount").alias("revenue")).orderBy("city")
