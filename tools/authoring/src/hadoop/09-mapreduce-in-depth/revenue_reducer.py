#!/usr/bin/env python3
# revenue_reducer.py: Hadoop Streaming reducer. Lines arrive SORTED by key; we detect where a key changes.
import sys

current, orders, total = None, 0, 0
for line in sys.stdin:
    category, amount = line.rstrip("\n").split("\t")
    if category != current:
        if current is not None:
            print(f"{current}\t{orders}\t{total}")
        current, orders, total = category, 0, 0
    orders += 1
    total += int(amount)
if current is not None:
    print(f"{current}\t{orders}\t{total}")
