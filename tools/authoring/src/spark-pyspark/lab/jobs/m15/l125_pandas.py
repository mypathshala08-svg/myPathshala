import time, random, warnings
import pandas as pd
import pyspark.pandas as ps
from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local[2]").appName("l125").getOrCreate()
random.seed(3)
pdf = pd.DataFrame({"city": [random.choice(["Mumbai", "Pune", "Delhi"]) for _ in range(300000)],
                    "amount": [random.randint(50, 900) for _ in range(300000)]})
pdf.to_csv("/tmp/orders125.csv", index=False)
print("== 1) same pandas code, two engines")
t = time.time(); a = pd.read_csv("/tmp/orders125.csv").groupby("city")["amount"].mean().round(1).sort_index(); print("  pandas      :", {k: float(v) for k, v in a.items()}, f"{time.time()-t:.2f} s")
t = time.time(); b = ps.read_csv("/tmp/orders125.csv").groupby("city")["amount"].mean().round(1).sort_index().to_pandas(); print("  pyspark.pandas:", {k: float(v) for k, v in b.items()}, f"{time.time()-t:.2f} s")
print("== 2) type and index")
psdf = ps.read_csv("/tmp/orders125.csv")
print("  type:", type(psdf).__module__ + "." + type(psdf).__name__)
print("  default index type:", ps.get_option("compute.default_index_type"))
print("  head(3):"); print(psdf.head(3).to_string())
print("== 3) moving between worlds")
sdf = psdf.to_spark(); print("  to_spark() ->", type(sdf).__module__, sdf.columns)
back = sdf.pandas_api(); print("  pandas_api() ->", type(back).__module__)
pd_small = psdf.head(5).to_pandas(); print("  to_pandas() ->", type(pd_small).__module__, "(collects to driver!)")
print("== 4) combining two different pandas-on-Spark frames")
print("   compute.ops_on_diff_frames default:", ps.get_option("compute.ops_on_diff_frames"))
other = ps.read_csv("/tmp/orders125.csv")
try:
    ps.set_option("compute.ops_on_diff_frames", False)
    (psdf["amount"] + other["amount"]).head(2)
except Exception as e:
    print("  ", type(e).__name__ + ":", str(e).split(".")[0])
ps.set_option("compute.ops_on_diff_frames", True)
print("   with True (joins on the index):", [int(x) for x in (psdf["amount"] + other["amount"]).head(2).to_numpy()])
ps.reset_option("compute.ops_on_diff_frames")
print("== 5) SQL on a pandas-on-Spark frame")
print(ps.sql("SELECT city, count(*) AS n FROM {df} GROUP BY city ORDER BY city", df=psdf).to_string())
print("== 6) things that are expensive or unsupported")
print("  len(psdf) runs a Spark job:", len(psdf))
try:
    print("  iloc[5] ->", psdf.iloc[5])
except Exception as e:
    print("  iloc[5] ->", type(e).__name__ + ":", str(e)[:90])
try:
    print("  psdf.values ->", type(psdf.values))
except Exception as e:
    print("  psdf.values ->", type(e).__name__)
print("== 7) second run (JVM and caches warm)")
t = time.time(); ps.read_csv("/tmp/orders125.csv").groupby("city")["amount"].mean().to_pandas(); print(f"  pyspark.pandas: {time.time()-t:.2f} s")
print("  iloc[:3] works (slice):", len(psdf.iloc[:3]))
