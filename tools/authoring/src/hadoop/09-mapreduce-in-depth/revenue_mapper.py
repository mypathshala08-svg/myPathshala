#!/usr/bin/env python3
# revenue_mapper.py: Hadoop Streaming mapper. Reads order lines on stdin, writes "category<TAB>amount".
import sys

menu = {}
with open("menu.csv") as f:                 # shipped with -files, appears in the task's working folder
    for line in f:
        item, category, price, counter = line.strip().split(",")
        menu[item] = category

for line in sys.stdin:
    order_id, student, time, item, amount = line.strip().split(",")
    print(f"{menu.get(item, 'unknown')}\t{amount}")
