import pytest
from pyspark.testing import assertDataFrameEqual, assertSchemaEqual
from pyspark.sql.types import StructType, StructField, StringType, LongType, IntegerType
from transforms import add_delivery_fee, city_revenue

@pytest.fixture
def orders(spark):
    return spark.createDataFrame([(1, "Pune", 450), (2, "Mumbai", 300), (3, "Mumbai", 800), (4, "Delhi", 500)],
                                 "order_id long, city string, amount long")

def test_fee_rules(spark, orders):
    out = add_delivery_fee(orders).select("order_id", "delivery_fee", "total")
    expected = spark.createDataFrame([(1, 40, 490), (2, 60, 360), (3, 0, 800), (4, 0, 500)],
                                     "order_id long, delivery_fee int, total long")
    assertDataFrameEqual(out, expected)

def test_city_revenue_ignores_row_order(spark, orders):
    expected = spark.createDataFrame([("Delhi", 500), ("Mumbai", 1100), ("Pune", 450)], "city string, revenue long")
    assertDataFrameEqual(city_revenue(orders), expected)          # order of rows does not matter

def test_schema(orders):
    expected = StructType([StructField("order_id", LongType()), StructField("city", StringType()),
                           StructField("amount", LongType()), StructField("delivery_fee", IntegerType(), False),
                           StructField("total", LongType())])
    assertSchemaEqual(add_delivery_fee(orders).schema, expected)

def test_boundary_is_free(spark):
    df = spark.createDataFrame([(9, "Mumbai", 500)], "order_id long, city string, amount long")
    assert add_delivery_fee(df).first()["delivery_fee"] == 0

def test_wrong_expectation_shows_diff(spark, orders):     # deliberately wrong: Mumbai fee 40
    out = add_delivery_fee(orders).select("order_id", "delivery_fee")
    expected = spark.createDataFrame([(1, 40), (2, 40), (3, 0), (4, 0)], "order_id long, delivery_fee int")
    assertDataFrameEqual(out, expected)
