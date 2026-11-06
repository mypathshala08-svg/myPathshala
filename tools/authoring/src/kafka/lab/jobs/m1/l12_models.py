"""1.2 Queue vs pub-sub in Kafka: one group shares work; many groups each get everything."""
import json, time, threading
from confluent_kafka import Producer, Consumer
from confluent_kafka.admin import AdminClient, NewTopic
BS = "k1:9092,k2:9092,k3:9092"; T = "deliveries"
a = AdminClient({"bootstrap.servers": BS}); a.delete_topics([T]); time.sleep(3)
a.create_topics([NewTopic(T, 3, 3)])[T].result(); time.sleep(2)
p = Producer({"bootstrap.servers": BS, "partitioner": "murmur2_random"})
for i in range(1, 13):
    p.produce(T, key=f"o{i}", value=json.dumps({"order": f"o{i}"}))
p.flush()
def run(names, group, out):
    def w(n):
        c = Consumer({"bootstrap.servers": BS, "group.id": group, "client.id": n, "auto.offset.reset": "earliest"})
        c.subscribe([T]); got, t0 = [], time.time()
        while time.time() - t0 < 15:
            m = c.poll(0.5)
            if m and not m.error(): got.append((m.partition(), m.key().decode()))
        out[n] = (sorted({x for x, _ in got}), [k for _, k in got]); c.close()
    ts = [threading.Thread(target=w, args=(n,)) for n in names]; [t.start() for t in ts]; [t.join() for t in ts]
print("== 1) QUEUE style: 3 riders in ONE group 'riders' share the 12 orders")
o = {}; run(["rider-A", "rider-B", "rider-C"], "riders", o)
for n in sorted(o): print(f"  {n}: partitions {o[n][0]} -> {len(o[n][1])} orders {o[n][1]}")
print("  total delivered:", sum(len(v[1]) for v in o.values()), "(each order once)")
print("== 2) PUB-SUB style: 2 different groups each get ALL 12")
o = {}; run(["sms-svc"], "sms", o); run(["analytics-svc"], "analytics", o)
for n in sorted(o): print(f"  {n}: {len(o[n][1])} orders")
print("== 3) a 4th rider in a 3-partition topic sits idle")
o = {}; run(["r1", "r2", "r3", "r4"], "riders4", o)
for n in sorted(o): print(f"  {n}: partitions {o[n][0]} -> {len(o[n][1])} orders")
