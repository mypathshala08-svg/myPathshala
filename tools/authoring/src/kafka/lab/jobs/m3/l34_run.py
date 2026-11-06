import subprocess, os, json
from collections import Counter
from confluent_kafka import Producer
from common import BS, fresh
for mode in ("atmost", "atleast"):
    T, G, log = f"inv-{mode}", f"billing-{mode}", f"/tmp/claude-0/inv-{mode}.log"
    fresh(T, 1)
    if os.path.exists(log): os.remove(log)
    p = Producer({"bootstrap.servers": BS})
    for i in range(1, 51): p.produce(T, value=f"invoice-{i:02d}")
    p.flush()
    first = subprocess.run(["python3", "l34_worker.py", mode, T, G, "25", log]).returncode
    second = subprocess.run(["python3", "l34_worker.py", mode, T, G, "0", log]).returncode
    lines = open(log).read().split()
    c = Counter(lines)
    print(f"== {mode.replace('atmost', 'at-most-once').replace('atleast', 'at-least-once')}: 50 invoices, worker crashes after 25, then restarts")
    print(f"  first run exit code {first}, second run exit code {second}")
    print(f"  invoices processed: {len(lines)}   unique: {len(c)}   missing: {50 - len(c)}   processed twice: {sum(1 for v in c.values() if v > 1)}")
    print("  missing:", [f"invoice-{i:02d}" for i in range(1, 51) if f"invoice-{i:02d}" not in c][:6])
    print("  duplicates:", sorted(k for k, v in c.items() if v > 1)[:6])
