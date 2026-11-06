"""4.3b Log compaction: keep only the latest value per key; tombstones delete keys."""
import time, subprocess
from confluent_kafka import Producer, Consumer
from common import BS, fresh
T = "menu-prices"
fresh(T, 1, 3, {"cleanup.policy": "compact", "segment.ms": "5000", "min.cleanable.dirty.ratio": "0.01",
                "delete.retention.ms": "5000", "min.compaction.lag.ms": "0"})
p = Producer({"bootstrap.servers": BS})
updates = [("thali", "120"), ("dosa", "80"), ("thali", "130"), ("lassi", "40"), ("dosa", "85"), ("thali", "140"),
           ("lassi", "45"), ("dosa", "90"), ("thali", "150"), ("vada", "30")]
for k, v in updates: p.produce(T, key=k, value=v)
p.produce(T, key="vada", value=None)          # tombstone: vada removed from the menu
p.flush()
def read():
    c = Consumer({"bootstrap.servers": BS, "group.id": f"r-{time.time()}", "auto.offset.reset": "earliest"})
    c.subscribe([T]); out, idle = [], 0
    while idle < 4:
        m = c.poll(1.0)
        if m is None: idle += 1; continue
        if not m.error(): out.append(f"{m.offset()}:{m.key().decode()}={m.value().decode() if m.value() else 'NULL'}")
    c.close(); return out
print("== 2) 11 records written (10 price updates + 1 tombstone)")
print("  ", " ".join(read()))
for i in range(8):                                  # keep the log moving so segments roll and the cleaner runs
    time.sleep(6); p.produce(T, key="tick", value=str(i)); p.flush()
print("== 3) after the cleaner ran (about 50 s later)")
print("  ", " ".join(r for r in read() if ":tick=" not in r))
print("  (tick records omitted; they only kept segments rolling)")
print(subprocess.run(["docker", "exec", "k1", "sh", "-c", "grep -h 'menu-prices' /opt/kafka/logs/log-cleaner.log 2>/dev/null | tail -3"], capture_output=True, text=True).stdout.rstrip()[:600])
