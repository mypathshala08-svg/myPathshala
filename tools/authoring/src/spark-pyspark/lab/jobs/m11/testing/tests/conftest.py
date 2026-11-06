import pytest, time
from pyspark.sql import SparkSession

@pytest.fixture(scope="session")
def spark():
    t = time.time()
    s = (SparkSession.builder.master("local[1]").appName("tests")
         .config("spark.sql.shuffle.partitions", "1")
         .config("spark.ui.enabled", "false").getOrCreate())
    print(f"\n[fixture] SparkSession started in {time.time() - t:.1f} s")
    yield s
    s.stop()
