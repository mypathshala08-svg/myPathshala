from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local[2]").getOrCreate()
spark.read.parquet("/root/lab/spark/data/orders_big").createOrReplaceTempView("orders")
print("-- SQL pipe syntax (Spark 4.0+)")
spark.sql("""FROM orders
|> WHERE status = 'CANCELLED'
|> AGGREGATE COUNT(*) AS cancelled GROUP BY city
|> ORDER BY cancelled DESC
|> LIMIT 3""").show()
print("-- VARIANT for semi-structured JSON (Spark 4.0+)")
spark.sql("""SELECT v:restaurant::string AS restaurant, v:items[0].dish::string AS first_dish, v:rating::double AS rating
FROM (SELECT parse_json('{"restaurant":"Desai Mess","items":[{"dish":"Idli","qty":2}],"rating":4.8}') AS v)""").show()
spark.stop()
