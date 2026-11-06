#!/usr/bin/env python3
"""Hive TRANSFORM reducer: rows arrive grouped and sorted by customer_id, order_ts.
Emits customer_id, orders, average hours between consecutive orders."""
import sys
from datetime import datetime

def flush(cid, times):
    gaps = [(b - a).total_seconds() / 3600 for a, b in zip(times, times[1:])]
    avg = f"{sum(gaps) / len(gaps):.1f}" if gaps else "\\N"
    print(f"{cid}\t{len(times)}\t{avg}")

current, times = None, []
for line in sys.stdin:
    cid, ts = line.rstrip("\n").split("\t")
    if cid != current and current is not None:
        flush(current, times)
        times = []
    current = cid
    times.append(datetime.strptime(ts[:19], "%Y-%m-%d %H:%M:%S"))
if current is not None:
    flush(current, times)
