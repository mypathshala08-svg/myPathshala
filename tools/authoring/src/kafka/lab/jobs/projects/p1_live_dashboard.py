"""Project 1 · TiffinGo live order tracker: consumer. Running revenue per city + big-order alert."""
import json, time
from collections import defaultdict
from confluent_kafka import Consumer
c = Consumer({"bootstrap.servers": "localhost:9092", "group.id": "live-dashboard", "auto.offset.reset": "earliest"})
c.subscribe(["orders"])
revenue, count, seen, idle = defaultdict(int), defaultdict(int), 0, 0
while idle < 10:                                   # stop after 10 s with no data (demo)
    m = c.poll(1.0)
    if m is None or m.error():
        idle += 1; continue
    idle = 0
    o = json.loads(m.value()); seen += 1
    revenue[o["city"]] += o["amount"]; count[o["city"]] += 1
    if o["amount"] >= 1000:
        print(f"  ALERT big order {o['order_id']} {o['city']} Rs {o['amount']} (partition {m.partition()}, offset {m.offset()})")
    if seen % 10 == 0:
        board = "  ".join(f"{k}: {count[k]} / Rs {revenue[k]}" for k in sorted(revenue))
        print(f"[{seen:3} orders] {board}")
c.close()
