"""Project 2 · UPI fraud alert: simulated payments, including one card that pays very fast."""
import json, random, time
T0 = 1793900000.0                                   # simulated clock: one payment every 5 s
from confluent_kafka import Producer
random.seed(11)
p = Producer({"bootstrap.servers": "localhost:9092", "partitioner": "murmur2_random"})
users = [f"user{i}@upi" for i in range(1, 9)]
for i in range(1, 61):
    u = random.choice(users)
    if 30 <= i < 36: u = "user9@upi"              # 6 rapid payments from one account
    amt = random.choice([50, 120, 300, 900]) if u != "user9@upi" else 4999
    if i == 45: u, amt = "user3@upi", 75000         # one unusually large payment
    p.produce("payments", key=u, value=json.dumps({"txn": f"t{i:03d}", "vpa": u, "amount": amt, "ts": T0 + (i * 5 if not 30 <= i < 36 else 150 + (i - 30) * 3)}))
    p.poll(0); time.sleep(0.1)
p.flush(); print("sent 60 payments")
