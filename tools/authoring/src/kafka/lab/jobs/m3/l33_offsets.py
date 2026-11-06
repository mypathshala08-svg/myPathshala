"""3.3 Offsets, commits and lag: manual commit, lag growth, committed offsets, reset."""
import json, time, subprocess
from confluent_kafka import Producer, Consumer, TopicPartition
from common import BS, fresh
T, G = "orders-33", "billing-33"
fresh(T, 3)
def cli(*a):
    return subprocess.run(["docker", "exec", "k1", "/opt/kafka/bin/kafka-consumer-groups.sh", "--bootstrap-server", "k1:9092", *a],
                          capture_output=True, text=True).stdout.strip()
p = Producer({"bootstrap.servers": BS, "partitioner": "murmur2_random"})
def produce(n, start):
    for i in range(start, start + n): p.produce(T, key=f"o{i}", value=json.dumps({"order": f"o{i}"}))
    p.flush()
produce(300, 0)
print("== 1) billing reads 120 records and commits manually (enable.auto.commit=false)")
c = Consumer({"bootstrap.servers": BS, "group.id": G, "auto.offset.reset": "earliest", "enable.auto.commit": False})
c.subscribe([T]); n = 0
while n < 120:
    for m in c.consume(40, 2.0):
        n += 1
c.commit(asynchronous=False)
com = sorted((tp.partition, tp.offset) for tp in c.committed(c.assignment(), timeout=10))
print("  committed:", com, "(-1001 = no commit yet)")
CP = ",".join(str(pp) for pp, o in com if o >= 0)
c.close()
print(cli("--describe", "--group", G))
print("== 2) the app is down while 300 more orders arrive")
produce(300, 300)
print(cli("--describe", "--group", G))
print("== 3) shift back by 50 on the committed partitions (dry run: nothing changes yet)")
print(cli("--reset-offsets", "--group", G, "--topic", T + ":" + CP, "--shift-by", "-50", "--dry-run"))
print("== 4) reset to the earliest offset (execute)")
print(cli("--reset-offsets", "--group", G, "--topic", T, "--to-earliest", "--execute"))
print("== 5) where commits are stored: __consumer_offsets (formatted)")
out = subprocess.run(["docker", "exec", "k1", "sh", "-c", "/opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server k1:9092 --topic __consumer_offsets "
      "--from-beginning --formatter org.apache.kafka.tools.consumer.OffsetsMessageFormatter --timeout-ms 8000 2>/dev/null"],
      capture_output=True, text=True).stdout.replace("}{", "}\n{").split("\n")
for line in [l for l in out if '"billing-33"' in l][-3:]:
    print(" ", line)
