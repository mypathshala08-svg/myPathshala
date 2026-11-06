from pyspark.sql import SparkSession
from transforms import only_valid, add_amount, revenue_by_city
import pytest
@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder.master("local[1]").config("spark.ui.showConsoleProgress", "false").getOrCreate()
def test_only_valid_drops_bad_rows(spark):
    df = spark.createDataFrame([("Pune", "idli", 2), ("Pune", None, 1), ("Delhi", "dosa", 0)], "city string, item string, qty int")
    assert only_valid(df).count() == 1
def test_amount_and_revenue(spark):
    df = spark.createDataFrame([("Pune", "idli", 2), ("Pune", "dosa", 1)], "city string, item string, qty int")
    out = df.transform(add_amount({"idli": 45, "dosa": 90})).transform(revenue_by_city).collect()
    assert [(r.city, r.revenue) for r in out] == [("Pune", 180)]
