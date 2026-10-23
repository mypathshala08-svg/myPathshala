# make_capstone.py: the capstone dataset for "Kadak Canteens", 4 college canteens in Navi Mumbai (September 2026)
# Raw POS files per canteen per day, UPI gateway files per day, the menu, and truth.json
# (the right answers, so your pipeline can be checked). Same files on every computer.
import csv, json, os, random
from datetime import date, datetime, timedelta

random.seed(14)
OUT = "capstone_raw"
COLLEGES = {"KHR": 4500, "VSH": 3800, "PNL": 3000, "NRL": 2200}      # orders on a normal day
MENU = [  # item, category, price, valid_from, valid_to
    ("chai", "drink", 15, "2026-09-01", "2026-09-15"), ("chai", "drink", 18, "2026-09-16", "2026-09-30"),
    ("coffee", "drink", 20, "2026-09-01", "2026-09-30"), ("samosa", "snack", 18, "2026-09-01", "2026-09-30"),
    ("vada pav", "snack", 20, "2026-09-01", "2026-09-30"), ("poha", "breakfast", 25, "2026-09-01", "2026-09-30"),
    ("idli", "breakfast", 30, "2026-09-01", "2026-09-30"), ("dosa", "meal", 45, "2026-09-01", "2026-09-30"),
    ("thali", "meal", 80, "2026-09-01", "2026-09-30")]
WEIGHT = {"chai": 30, "coffee": 8, "samosa": 14, "vada pav": 14, "poha": 9, "idli": 9, "dosa": 10, "thali": 6}
HOURS = [(8, 14), (9, 12), (10, 7), (11, 6), (12, 9), (13, 15), (14, 9), (15, 6), (16, 10), (17, 7), (18, 5)]

def next_open(d):                                # the next day the canteen is open
    return d + timedelta(2 if d.weekday() == 5 else 1)

def price(item, day):
    for it, cat, p, f, t in MENU:
        if it == item and f <= day <= t:
            return p

os.makedirs(f"{OUT}/payments", exist_ok=True)
with open(f"{OUT}/menu.csv", "w", newline="") as f:
    csv.writer(f).writerows([("item", "category", "price", "valid_from", "valid_to")] + MENU)

files = {}                 # (college, file_day) -> list of raw lines
pays = {}                  # day -> list of gateway events
truth = {"clean_orders": 0, "revenue": 0, "duplicates": 0, "malformed": 0, "test_orders": 0,
         "late": 0, "unknown_item": 0, "price_mismatch": 0, "undercharged": 0, "by_college": {}, "upi_net": 0, "refunds": 0, "upi_unconfirmed": 0}
days = [date(2026, 9, 1) + timedelta(d) for d in range(30)]
for c, base in COLLEGES.items():
    truth["by_college"][c] = {"orders": 0, "revenue": 0}
    for d in days:
        if d.weekday() == 6:                      # canteens are closed on Sundays
            continue
        ds = d.isoformat()
        n = int(base * random.uniform(0.85, 1.15))
        for k in range(1, n + 1):
            oid = f"{c}-{d:%m%d}-{k:05d}"
            h = random.choices([h for h, w in HOURS], [w for h, w in HOURS])[0]
            ts = f"{ds} {h:02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"
            item = random.choices(list(WEIGHT), list(WEIGHT.values()))[0]
            if c == "KHR" and ds >= "2026-09-21" and random.random() < 0.04:
                item = "maggi"                          # new dish, nobody added it to menu.csv
            qty = random.choices([1, 2, 3], [80, 15, 5])[0]
            p = 30 if item == "maggi" else price(item, ds)
            if c == "PNL" and item == "chai" and ds >= "2026-09-16":
                p = 15                                  # Panvel's POS never got the new chai price
            student = f"S{random.randint(1, 9000):05d}"
            if c == "VSH" and ds == "2026-09-03" and k % 250 == 0:
                student = "TEST"                        # a POS engineer testing the till
            mode = random.choices(["UPI", "CASH", "CARD"], [70, 25, 5])[0]
            row = f"{oid},{ts},{c},{student},{item},{qty},{qty * p},{mode}"
            fday = ds
            if random.random() < 0.006:                 # POS offline: row arrives in the next day's file
                fday = next_open(d).isoformat()
                if fday > "2026-09-30":
                    fday = ds
            files.setdefault((c, fday), []).append(row)
            if student == "TEST":
                truth["test_orders"] += 1
                continue
            truth["clean_orders"] += 1; truth["revenue"] += qty * p
            truth["by_college"][c]["orders"] += 1; truth["by_college"][c]["revenue"] += qty * p
            truth["late"] += fday != ds
            truth["unknown_item"] += item == "maggi"
            if item != "maggi" and p != price(item, ds):
                truth["price_mismatch"] += 1; truth["undercharged"] += qty * (price(item, ds) - p)
            if random.random() < 0.008:                 # POS re-sent the row (same or next file)
                again = fday if random.random() < 0.7 else min(next_open(date.fromisoformat(fday)).isoformat(), "2026-09-30")
                files.setdefault((c, again), []).append(row)
                truth["duplicates"] += 1
            if mode == "UPI":
                txn = f"T{random.randint(10**9, 10**10 - 1)}"
                ev = pays.setdefault(ds, [])
                outage = c == "NRL" and ds == "2026-09-22" and h == 13   # gateway down: no confirmations
                if random.random() < 0.01:              # first attempt failed, student paid again
                    ev.append({"txn_id": txn + "F", "order_id": oid, "amount": qty * p, "status": "FAILED", "ts": ts})
                if outage:
                    truth["upi_unconfirmed"] += qty * p
                else:
                    ev.append({"txn_id": txn, "order_id": oid, "amount": qty * p, "status": "SUCCESS", "ts": ts})
                    truth["upi_net"] += qty * p
                if random.random() < 0.004 and not outage:   # refunded later (cold food, wrong item)
                    ev.append({"txn_id": txn + "R", "order_id": oid, "amount": -qty * p, "status": "REFUNDED", "ts": ts})
                    truth["upi_net"] -= qty * p; truth["refunds"] += 1

bad = ["{oid},{ts},{c},S00042,dosa", "{oid},{ts},{c},S00042,dosa,1,forty five,UPI", "{oid},2026-09-31 10:00:00,{c},S00042,idli,1,30,CASH"]
for (c, ds), rows in sorted(files.items()):
    random.shuffle(rows)
    for j in range(random.randint(0, 6)):                # a few broken lines per file
        rows.insert(random.randrange(len(rows)), random.choice(bad).format(oid=f"{c}-BAD-{ds}-{j}", ts=ds + " 10:00:00", c=c))
        truth["malformed"] += 1
    os.makedirs(f"{OUT}/orders/{c}", exist_ok=True)
    with open(f"{OUT}/orders/{c}/orders_{c}_{ds}.csv", "w") as f:
        f.write("order_id,ts,college,student_id,item,qty,amount,pay_mode\n" + "\n".join(rows) + "\n")
for ds, ev in sorted(pays.items()):
    with open(f"{OUT}/payments/upi_{ds}.jsonl", "w") as f:
        f.write("".join(json.dumps(e) + "\n" for e in ev))
json.dump(truth, open(f"{OUT}/truth.json", "w"), indent=1)

size = sum(os.path.getsize(os.path.join(r, x)) for r, _, fs in os.walk(OUT) for x in fs)
nfiles = sum(len(fs) for _, _, fs in os.walk(OUT))
print(f"{nfiles} files, {size:,} bytes in {OUT}/")
print(f"clean orders {truth['clean_orders']:,}, revenue Rs {truth['revenue']:,}")
for k in ["duplicates", "malformed", "test_orders", "late", "unknown_item", "price_mismatch", "undercharged", "refunds", "upi_unconfirmed"]:
    print(f"  {k:<15}{truth[k]:>7,}")
