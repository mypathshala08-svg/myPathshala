#!/usr/bin/env python3
"""A script that fails on unexpected data, to show how Hive reports script errors."""
import sys
for line in sys.stdin:
    order_id, amount = line.rstrip("\n").split("\t")
    if float(amount) > 850:
        raise ValueError(f"amount too large for order {order_id}: {amount}")
    print(f"{order_id}\t{amount}")
