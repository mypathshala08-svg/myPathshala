"""13.1 Generate TiffinGo raw landing data with realistic problems."""
import os, json, random, shutil, datetime as dt
random.seed(13)
R = "/root/lab/spark/data/m13/landing"; shutil.rmtree(R, ignore_errors=True)
for d in ("orders", "restaurants", "customers"): os.makedirs(f"{R}/{d}")
cities = ["Mumbai", "Pune", "Delhi", "Bengaluru", "Hyderabad", "Chennai"]
# restaurants: JSON lines, one chain is huge (skew)
rest = [{"rest_id": i, "name": f"Rest {i}", "city": random.choice(cities), "cuisine": random.choice(["North Indian", "South Indian", "Chinese", "Biryani", "Cafe"])} for i in range(1, 801)]
rest[0].update(name="Cloud Kitchen Co", city="Mumbai")
with open(f"{R}/restaurants/restaurants.json", "w") as f:
    for r in rest: f.write(json.dumps(r) + "\n")
# customers: CSV with messy phones and duplicate ids
with open(f"{R}/customers/customers.csv", "w") as f:
    f.write("customer_id,name,city,plan,phone,signup_date\n")
    for c in range(1, 20001):
        phone = random.choice([str(9800000000 + c), str(9800000000 + c), "N/A", ""]) if c % 50 == 0 else str(9800000000 + c)
        f.write(f"{c},Cust {c},{random.choice(cities)},{random.choices(['Free','Silver','Gold'],[6,3,1])[0]},{phone},2025-{random.randint(1,12):02d}-{random.randint(1,28):02d}\n")
    for c in range(1, 101):                            # 100 duplicate customer rows
        f.write(f"{c},Cust {c},{random.choice(cities)},Free,{9800000000 + c},2025-01-01\n")
# orders: 14 daily CSV files, amounts as text with problems, some late/duplicate/bad rows
start = dt.date(2026, 10, 20); oid = 0
for d in range(14):
    day = start + dt.timedelta(days=d)
    with open(f"{R}/orders/orders_{day}.csv", "w") as f:
        f.write("order_id,customer_id,rest_id,order_ts,amount,status\n")
        for _ in range(60000):
            oid += 1
            rid = 1 if random.random() < 0.3 else random.randint(2, 800)
            amt = str(random.randint(80, 1500))
            r = random.random()
            if r < 0.004: amt = random.choice(["", "N/A", "12O"])          # bad amounts
            elif r < 0.006: amt = "-" + amt                                   # negative
            status = random.choices(["DELIVERED", "CANCELLED", "PLACED"], [85, 10, 5])[0]
            ts = dt.datetime.combine(day, dt.time(random.randint(7, 23), random.randint(0, 59)))
            f.write(f"{oid},{random.randint(1, 20500)},{rid},{ts:%Y-%m-%d %H:%M:%S},{amt},{status}\n")
            if random.random() < 0.003:                                       # duplicates (retries)
                f.write(f"{oid},{random.randint(1, 20000)},{rid},{ts:%Y-%m-%d %H:%M:%S},{amt},{status}\n")
print("files:", {d: len(os.listdir(f"{R}/{d}")) for d in os.listdir(R)}, "| orders written:", oid)
