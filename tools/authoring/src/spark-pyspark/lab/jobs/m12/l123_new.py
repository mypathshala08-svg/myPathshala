"""12.3 What's new in Spark 4.x, tried on PySpark 4.3.0."""
import warnings; warnings.filterwarnings("ignore")
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master("local[2]").config("spark.ui.showConsoleProgress", "false").getOrCreate()
spark.sparkContext.setLogLevel("OFF")
def q(label, sql):
    try:
        rows = spark.sql(sql).collect()
        print(f"{label}: {[tuple(r) for r in rows][:6]}")
    except Exception as e:
        m = str(e); i = m.find("["); print(f"{label}: ERROR {m[i:m.find(']', i) + 1] if i >= 0 else m.splitlines()[0][:100]}")
print("Spark", spark.version, "| ansi:", spark.conf.get("spark.sql.ansi.enabled"))
print("== 4.0 ANSI by default")
q("SELECT 1/0", "SELECT 1/0")
q("CAST('12a' AS INT)", "SELECT CAST('12a' AS INT)")
q("try_cast('12a' AS INT)", "SELECT try_cast('12a' AS INT)")
q("try_divide(1, 0)", "SELECT try_divide(1, 0)")
spark.conf.set("spark.sql.ansi.enabled", "false")
q("ANSI off: 1/0, CAST('12a')", "SELECT 1/0, CAST('12a' AS INT)")
spark.conf.set("spark.sql.ansi.enabled", "true")
print("== 4.0 SQL: pipe syntax, session variables, collation")
spark.createDataFrame([("Mumbai", 300), ("MUMBAI", 200), ("Pune", 450)], "city string, amount int").createOrReplaceTempView("o")
q("pipe syntax", "FROM o |> WHERE amount > 100 |> AGGREGATE sum(amount) AS total GROUP BY city |> ORDER BY city")
q("session variable", "DECLARE VARIABLE min_amt INT DEFAULT 250; ")
q("use variable", "SELECT city, amount FROM o WHERE amount >= min_amt ORDER BY city")
q("collation UTF8_LCASE", "SELECT city COLLATE UTF8_LCASE AS c, sum(amount) FROM o GROUP BY 1")
q("default collation", "SELECT city, sum(amount) FROM o GROUP BY 1 ORDER BY 1")
print("== 4.1 SQL scripting (GA, on by default)")
q("script", """BEGIN
  DECLARE total INT DEFAULT 0;
  DECLARE i INT DEFAULT 1;
  WHILE i <= 4 DO SET total = total + i * 100; SET i = i + 1; END WHILE;
  SELECT total;
END""")
q("recursive CTE", "WITH RECURSIVE r(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM r WHERE n < 5) SELECT sum(n) FROM r")
print("== 4.0 Python UDTF and Python data source")
from pyspark.sql.functions import udtf
@udtf(returnType="item string, qty int")
class SplitItems:
    def eval(self, order: str):
        for part in order.split(","):
            name, qty = part.split(":"); yield name.strip(), int(qty)
print("UDTF:", [tuple(r) for r in SplitItems(F.lit("dosa:2, idli:3, vada:1")).collect()])
from pyspark.sql.datasource import DataSource, DataSourceReader
class Menu(DataSource):
    @classmethod
    def name(cls): return "menu"
    def schema(self): return "dish string, price int"
    def reader(self, schema): return MenuReader()
class MenuReader(DataSourceReader):
    def read(self, partition):
        yield ("Masala Dosa", 120); yield ("Pav Bhaji", 140)
spark.dataSource.register(Menu)
print("Python data source:", [tuple(r) for r in spark.read.format("menu").load().collect()])
print("== 4.2 geospatial, 4.3 new SQL")
q("ST functions available", "SHOW FUNCTIONS LIKE 'st_*'")
q("GEOMETRY from WKB point", "SELECT typeof(st_geomfromwkb(X'0101000000B81E85EB513852405C8FC2F528123340')), st_srid(st_geomfromwkb(X'0101000000B81E85EB513852405C8FC2F528123340'))")
q("jaro_winkler_similarity", "SELECT round(jaro_winkler_similarity('Biryani House', 'Biriyani House'), 3)")
q("to_base32", "SELECT to_base32('TIFFIN')")
q("UNNEST in FROM", "SELECT * FROM UNNEST(array(10, 20, 30)) AS t(x)")
spark.conf.set("spark.sql.join.asofJoin.enabled", "true")
spark.createDataFrame([("Mumbai", 10), ("Mumbai", 25)], "city string, t int").createOrReplaceTempView("orders_t")
spark.createDataFrame([("Mumbai", 5, 1.0), ("Mumbai", 20, 1.5)], "city string, t int, surge double").createOrReplaceTempView("surge_t")
q("ASOF JOIN (enabled)", "SELECT o.t, s.surge FROM orders_t o ASOF JOIN surge_t s MATCH_CONDITION (o.t >= s.t) ON o.city = s.city ORDER BY o.t")
spark.conf.set("spark.sql.join.asofJoin.enabled", "false")
q("ASOF JOIN (off by default)", "SELECT 1 FROM o a ASOF JOIN o b MATCH_CONDITION (a.amount >= b.amount) ON a.city = b.city")
