import datetime as dt
from pyspark.testing import assertDataFrameEqual
from transforms import ORDER_SCHEMA, clean_orders, clean_customers, daily_city_revenue, customer_features

def raw(spark, rows):
    return spark.createDataFrame(rows, ORDER_SCHEMA)

def test_bad_rows_go_to_quarantine(spark):
    df = raw(spark, [("1", "7", "1", "2026-10-20 10:00:00", "250", "delivered"),
                     ("2", "7", "1", "2026-10-20 11:00:00", "N/A", "DELIVERED"),
                     ("3", "7", "1", "2026-10-20 12:00:00", "-90", "DELIVERED"),
                     ("4", "7", "1", "not a time", "100", "DELIVERED")])
    valid, quar = clean_orders(df)
    assert [r.order_id for r in valid.collect()] == [1]
    assert sorted((r.order_id, r.problem) for r in quar.collect()) == [(2, "bad_amount"), (3, "negative_amount"), (4, "bad_timestamp")]

def test_duplicates_removed_and_status_normalised(spark):
    df = raw(spark, [("1", "7", "1", "2026-10-20 10:00:00", "250", " delivered "),
                     ("1", "7", "1", "2026-10-20 10:00:00", "250", "DELIVERED")])
    valid, _ = clean_orders(df)
    rows = valid.collect()
    assert len(rows) == 1 and rows[0].status == "DELIVERED" and rows[0].order_date == dt.date(2026, 10, 20)

def test_latest_customer_row_wins(spark):
    df = spark.createDataFrame([("5", "A", "Pune", "Free", "N/A", "2025-01-01"), ("5", "A", "Pune", "Gold", "9800000005", "2025-06-01")],
                               "customer_id string, name string, city string, plan string, phone string, signup_date string")
    r = clean_customers(df).collect()
    assert len(r) == 1 and r[0].plan == "Gold" and r[0].phone == 9800000005

def test_daily_city_revenue_only_delivered(spark):
    valid, _ = clean_orders(raw(spark, [("1", "7", "1", "2026-10-20 10:00:00", "200", "DELIVERED"),
                                        ("2", "8", "1", "2026-10-20 12:00:00", "300", "DELIVERED"),
                                        ("3", "8", "1", "2026-10-20 13:00:00", "999", "CANCELLED")]))
    rest = spark.createDataFrame([(1, "Mumbai")], "rest_id int, city string")
    expected = spark.createDataFrame([(dt.date(2026, 10, 20), "Mumbai", 2, 500, 250.0)],
                                     "order_date date, city string, orders long, revenue long, avg_order double")
    assertDataFrameEqual(daily_city_revenue(valid, rest), expected)

def test_features_for_customer_without_orders(spark):
    valid, _ = clean_orders(raw(spark, [("1", "7", "1", "2026-10-20 10:00:00", "200", "DELIVERED")]))
    cust = spark.createDataFrame([(7, "Pune"), (9, "Delhi")], "customer_id int, city string")
    f = {r.customer_id: (r.orders_14d, r.days_since_last) for r in customer_features(valid, cust, "2026-11-02").collect()}
    assert f == {7: (1, 13), 9: (0, 99)}
