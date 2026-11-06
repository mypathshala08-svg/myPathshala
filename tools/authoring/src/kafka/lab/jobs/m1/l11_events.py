"""1.1 One stream, two independent readers, replay. confluent-kafka (librdkafka)."""
import json, time, sys
from confluent_kafka import Producer, Consumer, TopicPartition
from confluent_kafka.admin import AdminClient, NewTopic
BS = "k1:9092,k2:9092,k3:9092"; T = "order-events"
a = AdminClient({"bootstrap.servers": BS})
a.delete_topics([T]); time.sleep(3)
a.create_topics([NewTopic(T, 3, 3)])[T].result(); time.sleep(2)
print("== 1) TiffinGo app produces 6 order events")
p = Producer({"bootstrap.servers": BS})
events = [("o101", "PLACED", "Mumbai", 250), ("o102", "PLACED", "Pune", 480), ("o101", "PAID", "Mumbai", 250),
          ("o103", "PLACED", "Delhi", 300), ("o102", "PAID", "Pune", 480), ("o101", "DELIVERED", "Mumbai", 250)]
def cb(err, m):
    print(f"  sent {m.key().decode()} {json.loads(m.value())['status']:9} -> partition {m.partition()} offset {m.offset()}")
for oid, st, city, amt in events:
    p.produce(T, key=oid, value=json.dumps({"order": oid, "status": st, "city": city, "amount": amt}), callback=cb)
    p.poll(0)
p.flush()
def read(group, reset="earliest"):
    c = Consumer({"bootstrap.servers": BS, "group.id": group, "auto.offset.reset": reset, "enable.auto.commit": True})
    c.subscribe([T]); got = []; t0 = time.time()
    while len(got) < 6 and time.time() - t0 < 20:
        m = c.poll(1.0)
        if m and not m.error():
            got.append(f"{m.key().decode()}:{json.loads(m.value())['status']}")
    c.close(); return got
print("== 2) kitchen service reads")
k = read("kitchen"); print("  kitchen got", len(k), "events:", ", ".join(sorted(k)))
print("== 3) billing service reads the SAME events independently")
b = read("billing"); print("  billing got", len(b), "events:", ", ".join(sorted(b)))
print("== 4) events are not deleted after reading")
c = Consumer({"bootstrap.servers": BS, "group.id": "probe"})
for pt in range(3):
    lo, hi = c.get_watermark_offsets(TopicPartition(T, pt), timeout=10)
    print(f"  partition {pt}: first offset {lo}, next offset {hi} -> {hi - lo} events still stored")
c.close()
print("== 5) a NEW analytics service joins tomorrow and replays from the start")
r = read("analytics"); print("  analytics got", len(r), "events (full history)")
