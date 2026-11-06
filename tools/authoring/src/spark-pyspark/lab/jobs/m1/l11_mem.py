import os, pandas as pd
p = "/root/lab/spark/data/tiffingo/orders.csv"
df = pd.read_csv(p)
fm, mm = os.path.getsize(p) / 2**20, df.memory_usage(deep=True).sum() / 2**20
print(f"file on disk : {fm:.1f} MiB")
print(f"in pandas    : {mm:.1f} MiB  ({mm/fm:.1f}x the file)")
print(f"rows: {len(df):,}")
