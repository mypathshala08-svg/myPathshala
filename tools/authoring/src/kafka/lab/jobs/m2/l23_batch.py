"""2.3 Batching (linger.ms) and compression: count batches and bytes on disk for 20,000 order events."""
import json, time, subprocess, random
from confluent_kafka import Producer
from common import BS, fresh
random.seed(3)
cities = ["Mumbai", "Pune", "Delhi", "Bengaluru", "Chennai"]
events = [json.dumps({"order_id": f"o{i:06d}", "city": random.choice(cities), "items": ["thali", "lassi"][: 1 + i % 2],
                      "amount": random.choice([120, 180, 250, 480]), "status": "PLACED"}) for i in range(20000)]
def disk(topic):
    out = subprocess.check_output(["docker", "exec", "k1", "sh", "-c",
        f"du -cb /var/lib/kafka/data/{topic}-[0-9]/*.log | tail -1; for f in /var/lib/kafka/data/{topic}-[0-9]/00000000000000000000.log; do /opt/kafka/bin/kafka-dump-log.sh --files $f 2>/dev/null | grep -c baseOffset; done"], text=True).split()
    return int(out[0]), sum(int(x) for x in out[2:])
def run(topic, conf):
    fresh(topic, 3, 3)
    p = Producer({"bootstrap.servers": BS, "partitioner": "murmur2_random", **conf})
    t0 = time.perf_counter()
    for i, e in enumerate(events):
        while True:
            try: p.produce(topic, key=f"o{i}", value=e); break
            except BufferError: p.poll(0.01)
        p.poll(0)
    p.flush(); secs = time.perf_counter() - t0
    time.sleep(1); b, n = disk(topic)
    return secs, b, n
raw = sum(len(e) for e in events)
print(f"== payload: 20,000 JSON orders, {raw/1024:.0f} KiB of JSON values (plus keys and record headers on disk)")
print("== 1) linger.ms: wait a little, send bigger batches")
for lg in (0, 5, 50):
    s, b, n = run(f"linger-{lg}", {"linger.ms": lg, "compression.type": "none"})
    print(f"  linger.ms={lg:<3}  batches on disk {n:5}   avg {20000/n:6.1f} records/batch   time {s:.2f} s")
print("== 2) compression.type (linger.ms=50)")
base = None
for c in ("none", "gzip", "snappy", "lz4", "zstd"):
    s, b, n = run(f"comp-{c}", {"linger.ms": 50, "compression.type": c})
    base = base or b
    print(f"  {c:7} log size (3 partitions) {b/1024:6.0f} KiB   {base/b:4.1f}x smaller than none   time {s:.2f} s")
