#!/usr/bin/env python3
# clean_reducer.py: one line per order_id (keep the earliest copy), add category, flag problems
import csv, sys

menu = {}                                                 # item -> [(from, to, price, category)]
for r in csv.DictReader(open("menu.csv")):
    menu.setdefault(r["item"], []).append((r["valid_from"], r["valid_to"], int(r["price"]), r["category"]))

def count(name, k=1):
    print(f"reporter:counter:capstone,{name},{k}", file=sys.stderr)

def finish(copies):
    fday, line = min(copies)                              # earliest file wins
    count("DUPLICATE", len(copies) - 1)
    oid, ts, college, student, item, qty, amount, mode = line.split(",")
    dt, qty, amount = ts[:10], int(qty), int(amount)
    late = fday > dt
    price = next(((p, c) for a, b, p, c in menu.get(item, []) if a <= dt <= b), None)
    category = price[1] if price else "unknown"
    under = qty * price[0] - amount if price else 0
    count("CLEAN")
    if late: count("LATE")
    if not price: count("UNKNOWN_ITEM")
    if under: count("PRICE_MISMATCH"); count("UNDERCHARGED_RS", under)
    print("\t".join(map(str, ["OK", oid, dt, ts, college, student, item, category, qty, amount, mode,
                              int(late), int(not price), under])))

key, copies = None, []
for line in sys.stdin:
    k, fday, raw = line.rstrip("\n").split("\t", 2)
    if k == "~BAD":
        print(f"BAD\t{fday}\t{raw}")
        continue
    if k != key and copies:
        finish(copies); copies = []
    key = k
    copies.append((fday, raw))
if copies:
    finish(copies)
