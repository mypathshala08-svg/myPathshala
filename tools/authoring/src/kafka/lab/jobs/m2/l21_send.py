"""2.1 What happens when you call produce(): async send, callbacks, latency, flush, and a failed send."""
import json, time
from confluent_kafka import Producer
from common import BS, fresh
fresh("orders-21")
print("== 1) produce() returns immediately; the callback comes later")
p = Producer({"bootstrap.servers": BS, "linger.ms": 5})
events = []
def cb(err, m):
    events.append(f"  callback  {m.key().decode()} -> partition {m.partition()} offset {m.offset()}  latency {m.latency()*1000:.1f} ms")
t0 = time.perf_counter()
for i in range(1, 6):
    p.produce("orders-21", key=f"o{i}", value=json.dumps({"order": f"o{i}", "amount": 100 * i}), callback=cb)
    print(f"  produce() o{i} returned after {(time.perf_counter()-t0)*1000:.2f} ms  (in queue: {len(p)})")
print("  callbacks so far:", len(events))
n = p.flush(10)
print(f"  flush() done after {(time.perf_counter()-t0)*1000:.1f} ms, still queued: {n}")
print("\n".join(events))
print("== 2) the first send pays for metadata; later sends are faster")
lat = []
for i in range(200):
    p.produce("orders-21", key=f"x{i}", value="v", callback=lambda e, m: lat.append(m.latency()))
    p.poll(0)
p.flush()
lat.sort()
print(f"  200 records: median latency {lat[100]*1000:.1f} ms, p99 {lat[197]*1000:.1f} ms")
print("== 3) a failed send: the broker cannot be reached")
bad = Producer({"bootstrap.servers": "localhost:19999", "message.timeout.ms": 3000})
errs = []
bad.produce("orders-21", key="o9", value="lost?", callback=lambda e, m: errs.append(str(e)))
t1 = time.perf_counter(); bad.flush(10)
print(f"  after {time.perf_counter()-t1:.1f} s the callback said: {errs[0]}")
