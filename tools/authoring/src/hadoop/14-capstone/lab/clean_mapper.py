#!/usr/bin/env python3
# clean_mapper.py: parse raw POS lines; key every good row by order_id so copies meet in one reducer
import os, sys
from datetime import datetime

path = os.environ.get("mapreduce_map_input_file", "orders_XXX_0000-00-00.csv")
fday = path.rsplit("_", 1)[-1][:10]                      # date of the file the line arrived in

def count(name):
    print(f"reporter:counter:capstone,{name},1", file=sys.stderr)

for line in sys.stdin:
    line = line.rstrip("\n")
    if not line or line.startswith("order_id,"):
        continue                                          # header of each file
    f = line.split(",")
    try:
        if len(f) != 8:
            raise ValueError("fields")
        datetime.strptime(f[1], "%Y-%m-%d %H:%M:%S")      # rejects 2026-09-31
        int(f[5]), int(f[6])
    except ValueError:
        count("MALFORMED")
        print(f"~BAD\t{fday}\t{line}")                    # quarantine, keep the raw line
        continue
    if f[3] == "TEST":
        count("TEST_ORDER")
        continue
    print(f"{f[0]}\t{fday}\t{line}")
