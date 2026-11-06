"""2.4 acks vs failures. Topic pay-24b has min.insync.replicas=3; one broker is stopped, so only 2 replicas are in sync."""
import sys
from confluent_kafka import Producer
BS = "k1:9092,k2:9092,k3:9092"
def send(acks, retries):
    res = []
    p = Producer({"bootstrap.servers": BS, "acks": acks, "enable.idempotence": False, "retries": retries,
                  "message.timeout.ms": 8000, "partitioner": "murmur2_random"})
    for i in range(2):
        p.produce("pay-24b", key="user3@upi", value=f"payment {i}",
                  callback=lambda e, m: res.append(f"P{m.partition()} offset {m.offset()}" if e is None else e.str()))
    p.flush(15); return res
print("  acks=all (no retries):", send("all", 0))
print("  acks=all (retries on):", send("all", 5))
print("  acks=1                :", send("1", 0))
print("  acks=0                :", send("0", 0))
