"""Project 2 · UPI fraud alert: reads payments, applies 2 rules, writes alerts to another topic."""
import json, time
from collections import defaultdict, deque
from confluent_kafka import Consumer, Producer
c = Consumer({"bootstrap.servers": "localhost:9092", "group.id": "fraud-detector", "auto.offset.reset": "earliest"})
p = Producer({"bootstrap.servers": "localhost:9092"})
c.subscribe(["payments"])
recent = defaultdict(deque)                          # vpa -> timestamps in the last 60 s
checked, alerts, idle = 0, 0, 0
while idle < 8:
    m = c.poll(1.0)
    if m is None or m.error():
        idle += 1; continue
    idle = 0; checked += 1
    t = json.loads(m.value()); q = recent[t["vpa"]]
    q.append(t["ts"])
    while q and t["ts"] - q[0] > 60: q.popleft()
    reason = "amount over Rs 50,000" if t["amount"] > 50000 else ("more than 4 payments in 60 s" if len(q) > 4 else None)
    if reason:
        alerts += 1
        p.produce("fraud-alerts", key=t["vpa"], value=json.dumps({**t, "reason": reason}))
        print(f"  FLAG {t['txn']} {t['vpa']} Rs {t['amount']}: {reason}")
p.flush(); c.close()
print(f"checked {checked} payments, raised {alerts} alerts")
