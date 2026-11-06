"""Project 1 · TiffinGo live order tracker: producer. Sends one order every 0.2 s."""
import json, random, time, sys
from confluent_kafka import Producer
random.seed(7)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 50
p = Producer({"bootstrap.servers": "localhost:9092", "partitioner": "murmur2_random"})
cities = ["Mumbai", "Pune", "Delhi", "Bengaluru"]
for i in range(1, N + 1):
    order = {"order_id": f"o{i:04d}", "city": random.choice(cities),
             "amount": random.choice([120, 180, 250, 320, 480, 1500]), "ts": time.time()}
    p.produce("orders", key=order["city"], value=json.dumps(order))
    p.poll(0)
    time.sleep(0.2)
p.flush()
print(f"sent {N} orders")
