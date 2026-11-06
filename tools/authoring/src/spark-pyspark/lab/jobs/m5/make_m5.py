"""Messy partner files for Module 5."""
import json, os, random, gzip, shutil
D = "/root/lab/spark/data/m5"
os.makedirs(D, exist_ok=True)
# 1) partner CSV with real-world problems
rows = [
 'order_id,city,amount,order_date,review',
 '9001,Pune,450,2026-11-01,Good food',
 '9002,"Navi Mumbai, MH",380,2026-11-01,"Tasty, hot"',
 '9003,Delhi,abc,2026-11-02,Late',
 '9004,Pune,520,2026-11-02,"Loved it.\nWill order again"',
 '9005,Mumbai,610,2026-11-02,Cold,EXTRA',
 '9006,Hyderabad,300,02/11/2026,Fine',
 '9007,Bengaluru,275,2026-11-03,"He said ""wow"""',
]
open(f"{D}/partner_orders.csv", "w").write("\n".join(rows) + "\n")
# 2) JSON lines and a JSON array file
recs = [{"order_id": 9101, "city": "Pune", "items": [{"dish": "Thali", "qty": 2}], "rider": {"name": "Ravi", "rating": 4.8}},
        {"order_id": 9102, "city": "Delhi", "items": [{"dish": "Dosa", "qty": 1}, {"dish": "Idli", "qty": 2}], "coupon": "FEST20"},
        {"order_id": "9103", "city": "Mumbai", "items": [], "rider": {"name": "Asha"}}]
open(f"{D}/app_events.jsonl", "w").write("\n".join(json.dumps(r) for r in recs) + "\n")
open(f"{D}/app_events_array.json", "w").write(json.dumps(recs, indent=2))
# 3) gzip copy of big_csv (single file)
src = [f for f in os.listdir("/root/lab/spark/data/big_csv") if f.endswith(".csv")][0]
os.makedirs(f"{D}/big_csv_gz", exist_ok=True)
with open(f"/root/lab/spark/data/big_csv/{src}", "rb") as a, gzip.open(f"{D}/big_csv_gz/orders.csv.gz", "wb") as b:
    shutil.copyfileobj(a, b)
print(os.path.getsize(f"/root/lab/spark/data/big_csv/{src}") // 2**20, "MiB csv ->", os.path.getsize(f"{D}/big_csv_gz/orders.csv.gz") // 2**20, "MiB gz")
