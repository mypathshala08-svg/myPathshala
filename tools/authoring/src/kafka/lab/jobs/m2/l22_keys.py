"""2.2 Keys and partitioners: keyless sticky batches, murmur2 vs consistent_random, null key, hot key."""
import json
from collections import Counter
from confluent_kafka import Producer
from common import BS, fresh
def run(topic, conf, items, show=True):
    fresh(topic, 3)
    out = []
    p = Producer({"bootstrap.servers": BS, **conf})
    for k, v in items:
        p.produce(topic, key=k, value=v, callback=lambda e, m: out.append((m.key().decode() if m.key() else None, m.partition())))
        p.poll(0)
    p.flush(); return out
print("== 1) no key: records stick to one partition per batch (sticky partitioning)")
out = []
p = Producer({"bootstrap.servers": BS, "linger.ms": 50, "batch.num.messages": 10})
fresh("nokey-22", 3)
for burst in range(3):
    for i in range(10):
        p.produce("nokey-22", value=f"log-{burst}-{i}", callback=lambda e, m: out.append(m.partition()))
    p.flush()
runs, cur = [], None
for x in out:
    if runs and runs[-1][0] == x: runs[-1][1] += 1
    else: runs.append([x, 1])
print("  30 keyless records, partition runs:", " ".join(f"P{a}x{n}" for a, n in runs))
print("== 2) same keys, two partitioners")
keys = ["o101", "o102", "o103", "Mumbai", "Pune", "user9@upi"]
a = run("k-murmur", {"partitioner": "murmur2_random"}, [(k, "v") for k in keys])
b = run("k-crc", {"partitioner": "consistent_random"}, [(k, "v") for k in keys])
a, b = dict(a), dict(b)
for k in keys:
    print(f"  {k:10}  murmur2 (Java default) -> P{a[k]}   consistent_random (librdkafka default) -> P{b[k]}")
print("== 3) a hot key: 70% of traffic from one restaurant")
items = [("rest-1" if i % 10 < 7 else f"rest-{i}", "o") for i in range(1000)]
c = Counter(p for _, p in run("hot-22", {"partitioner": "murmur2_random"}, items))
print("  records per partition:", dict(sorted(c.items())))
print("== 4) fix: compound key rest-1#<order_id % 4> spreads the hot restaurant")
items = [((f"rest-1#{i % 4}") if i % 10 < 7 else f"rest-{i}", "o") for i in range(1000)]
c = Counter(p for _, p in run("hot-22b", {"partitioner": "murmur2_random"}, items))
print("  records per partition:", dict(sorted(c.items())))
