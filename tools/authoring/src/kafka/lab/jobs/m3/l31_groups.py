"""3.1 Consumer poll loop and groups: assignment callback, fetch batches, group describe."""
import json, time, threading, subprocess
from confluent_kafka import Producer, Consumer
from common import BS, fresh
T = "orders-31"
fresh(T, 6)
p = Producer({"bootstrap.servers": BS, "partitioner": "murmur2_random", "linger.ms": 5})
for i in range(600):
    p.produce(T, key=f"o{i}", value=json.dumps({"order": f"o{i}", "amount": 100 + i % 7 * 50}))
p.flush()
print("== 1) one consumer: assignment callback and poll batches")
c = Consumer({"bootstrap.servers": BS, "group.id": "kitchen-31", "auto.offset.reset": "earliest", "client.id": "kitchen-1"})
c.subscribe([T], on_assign=lambda cons, parts: print("  on_assign:", sorted(p.partition for p in parts)))
got, polls, t0 = 0, 0, time.time()
while got < 600 and time.time() - t0 < 30:
    msgs = c.consume(num_messages=200, timeout=1.0)          # one poll can return many records
    if msgs:
        polls += 1; got += len(msgs)
        if polls <= 3: print(f"  poll {polls}: {len(msgs)} records, first from P{msgs[0].partition()} offset {msgs[0].offset()}")
print(f"  total {got} records in {polls} polls")
print("== 2) two more members join the same group")
stop = threading.Event(); owned = {}
def member(name):
    m = Consumer({"bootstrap.servers": BS, "group.id": "kitchen-31", "client.id": name})
    m.subscribe([T], on_assign=lambda cons, parts: owned.__setitem__(name, sorted(x.partition for x in parts)))
    while not stop.is_set(): m.poll(0.2)
    m.close()
ths = [threading.Thread(target=member, args=(n,)) for n in ("kitchen-2", "kitchen-3")]
[t.start() for t in ths]
t1 = time.time()
while time.time() - t1 < 15: c.poll(0.2)
print("  kitchen-1 now owns:", sorted(x.partition for x in c.assignment()))
for n in sorted(owned): print(f"  {n} owns: {owned[n]}")
print("== 3) the broker's view: kafka-consumer-groups --describe --members")
print(subprocess.run(["docker", "exec", "k1", "/opt/kafka/bin/kafka-consumer-groups.sh", "--bootstrap-server", "k1:9092",
                      "--describe", "--group", "kitchen-31", "--members"], capture_output=True, text=True).stdout.rstrip())
print("== 4) group state")
print(subprocess.run(["docker", "exec", "k1", "/opt/kafka/bin/kafka-consumer-groups.sh", "--bootstrap-server", "k1:9092",
                      "--describe", "--group", "kitchen-31", "--state"], capture_output=True, text=True).stdout.rstrip())
stop.set(); [t.join() for t in ths]; c.close()
