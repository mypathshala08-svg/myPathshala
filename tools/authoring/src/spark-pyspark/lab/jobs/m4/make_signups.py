"""Dirty sign-up export from the TiffinGo app: nulls, blanks, 'NA', duplicates from retries."""
import random, csv, datetime as dt
random.seed(44)
cities = ["Mumbai", "Pune", "Bengaluru", "Delhi", "Hyderabad"]
rows = []
for i in range(1, 2001):
    ts = dt.datetime(2026, 10, 1) + dt.timedelta(minutes=random.randint(0, 40000))
    city = random.choice(cities)
    r = random.random()
    if r < 0.05: city = ""
    elif r < 0.08: city = "NA"
    phone = f"98{random.randint(10000000, 99999999)}" if random.random() > 0.04 else ""
    ref = random.choice(["", "", "FRIEND50", "INSTA", "GOOGLE"])
    age = str(random.randint(18, 60)) if random.random() > 0.06 else ""
    rating = random.choice(["4.5", "4.0", "3.5", "5.0", "", "NaN"])
    rows.append([1000 + i, f"user{i}@mail.in", phone, city, ref, age, rating, ts.strftime("%Y-%m-%d %H:%M:%S")])
dups = []
for r in random.sample(rows, 120):            # app retried the request: exact copies
    dups.append(list(r))
for r in random.sample(rows, 80):             # same user signs up again later
    r2 = list(r); t = dt.datetime.strptime(r[7], "%Y-%m-%d %H:%M:%S") + dt.timedelta(minutes=random.randint(5, 3000))
    r2[7] = t.strftime("%Y-%m-%d %H:%M:%S"); r2[3] = random.choice(cities); dups.append(r2)
rows += dups
random.shuffle(rows)
with open("/root/lab/spark/data/tiffingo/signups/signups.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["user_id", "email", "phone", "city", "referral", "age", "rating", "signed_up_at"]); w.writerows(rows)
print(len(rows), "rows")
