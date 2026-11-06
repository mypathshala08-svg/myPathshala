#!/usr/bin/env python3
"""Hive TRANSFORM mapper: order_id, order_ts, amount -> order_id, slot, gst
Hive sends one tab-separated line per row; NULL arrives as \\N."""
import sys

def slot(hour):
    if 6 <= hour < 11:  return "breakfast"
    if 11 <= hour < 16: return "lunch"
    if 16 <= hour < 19: return "snacks"
    if 19 <= hour < 23: return "dinner"
    return "late-night"

for line in sys.stdin:
    order_id, ts, amount = line.rstrip("\n").split("\t")
    s = slot(int(ts[11:13])) if ts != "\\N" else "\\N"
    gst = f"{float(amount) * 0.05:.2f}" if amount != "\\N" else "\\N"
    print(f"{order_id}\t{s}\t{gst}")
