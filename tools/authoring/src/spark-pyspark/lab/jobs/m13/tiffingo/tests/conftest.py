import sys, pytest
sys.path.insert(0, __file__.rsplit("/tests/", 1)[0])
from pyspark.sql import SparkSession

@pytest.fixture(scope="session")
def spark():
    s = (SparkSession.builder.master("local[1]").config("spark.sql.shuffle.partitions", "1")
         .config("spark.ui.enabled", "false").getOrCreate())
    yield s
    s.stop()
