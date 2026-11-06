import sys, subprocess, platform, pyspark, pandas, pyarrow
print("python ", platform.python_version())
print("pyspark", pyspark.__version__)
print("pandas ", pandas.__version__, "| pyarrow", pyarrow.__version__)
print(subprocess.run(["java", "-version"], capture_output=True, text=True).stderr.splitlines()[0])
