"""5.2 ISR and the high watermark: freeze a follower, write with acks=1, watch what consumers can see."""
import subprocess, time, re
from confluent_kafka import Producer, Consumer, TopicPartition
def sh(c): return subprocess.run(["docker", "exec", "k1", "sh", "-c", c], capture_output=True, text=True).stdout
T = "hw-52b"
sh(f"/opt/kafka/bin/kafka-topics.sh --bootstrap-server k1:9092 --create --topic {T} --replica-assignment 1:2:3")
time.sleep(5)
p = Producer({"bootstrap.servers": "k1:9092", "acks": "1", "enable.idempotence": False})
for i in range(5): p.produce(T, value=f"before-{i}")
p.flush(); time.sleep(2)
c = Consumer({"bootstrap.servers": "k1:9092", "group.id": "hw-probe"})
def hw(): return c.get_watermark_offsets(TopicPartition(T, 0), timeout=5)[1]
def isr(): return re.search(r"Isr: ([\d,]+)", sh(f"/opt/kafka/bin/kafka-topics.sh --bootstrap-server k1:9092 --describe --topic {T}")).group(1)
print("== 1) healthy: 5 records, high watermark", hw(), " ISR", isr())
subprocess.run(["docker", "pause", "k3"])
print("== 2) docker pause k3 (a follower). Write 5 more records with acks=1 (leader only)")
t0 = time.time()
for i in range(5): p.produce(T, value=f"during-{i}")
p.flush()
print(f"  acks=1 confirmed after {time.time() - t0:.2f} s: the leader has 10 records (log end offset 10)")
last = None
while time.time() - t0 < 20:
    h = hw()
    if h != last:
        print(f"  t+{time.time() - t0:4.1f}s  high watermark {h:2}  (consumers can read offsets < {h})")
        last = h
    time.sleep(0.25)
print("  ISR now", isr())
subprocess.run(["docker", "unpause", "k3"])
time.sleep(8)
print("== 3) unpause k3: it catches up and rejoins the ISR")
print("  high watermark", hw(), "  ISR", isr())
print("  under-replicated partitions now:", sh("/opt/kafka/bin/kafka-topics.sh --bootstrap-server k1:9092 --describe --under-replicated-partitions").strip() or "none")
c.close()
