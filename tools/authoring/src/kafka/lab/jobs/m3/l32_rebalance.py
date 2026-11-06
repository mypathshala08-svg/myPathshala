"""3.2 What a rebalance costs: classic eager vs classic cooperative vs the new consumer protocol (KIP-848)."""
import sys, time, threading
from confluent_kafka import Producer, Consumer
from common import BS, fresh
MODES = {"eager":       {"group.protocol": "classic", "partition.assignment.strategy": "range"},
         "cooperative": {"group.protocol": "classic", "partition.assignment.strategy": "cooperative-sticky"},
         "consumer":    {"group.protocol": "consumer"}}
def run(mode):
    T, G = f"reb-{mode}", f"g-{mode}"
    fresh(T, 6)
    stop = threading.Event(); events = []
    def produce():
        p = Producer({"bootstrap.servers": BS, "linger.ms": 0})
        i = 0
        while not stop.is_set():
            p.produce(T, value=str(i)); p.poll(0); i += 1; time.sleep(0.01)
        p.flush()
    def member(name, start):
        time.sleep(start)
        conf = {"bootstrap.servers": BS, "group.id": G, "client.id": name, "auto.offset.reset": "latest", **MODES[mode]}
        if mode != "consumer": conf["session.timeout.ms"] = 10000
        c = Consumer(conf)
        def on_assign(cons, parts):
            if mode == "cooperative": cons.incremental_assign(parts)
            events.append((time.time(), name, "assigned", sorted(x.partition for x in parts)))
        def on_revoke(cons, parts):
            events.append((time.time(), name, "revoked", sorted(x.partition for x in parts)))
            if mode == "cooperative": cons.incremental_unassign(parts)
        c.subscribe([T], on_assign=on_assign, on_revoke=on_revoke)
        last = None
        while not stop.is_set():
            m = c.poll(0.05)
            if m and not m.error():
                events.append((time.time(), name, "msg", m.partition()))
        c.close()
    ths = [threading.Thread(target=produce), threading.Thread(target=member, args=("A", 0)), threading.Thread(target=member, args=("B", 0)),
           threading.Thread(target=member, args=("C", 14))]
    [t.start() for t in ths]; time.sleep(30); stop.set(); [t.join() for t in ths]
    join = min(t for t, n, k, _ in events if n == "C" and k in ("assigned",)) if any(n == "C" for _, n, _, _ in events) else None
    t0 = 14 + min(t for t, *_ in events) if events else 0
    print(f"== {mode}: partitions revoked/assigned around C joining")
    moved = 0
    for t, n, k, v in events:
        if k != "msg" and -6 < t - join < 6 and v:
            print(f"  {t - join:+6.2f}s  {n} {k:8} {v}")
            if k == "revoked": moved += len(v)
    print(f"  partitions taken away from A and B: {moved} of 6")
    for n in ("A", "B"):
        ts = [t for t, m, k, _ in events if m == n and k == "msg" and join - 6 < t < join + 6]
        gaps = max((b - a for a, b in zip(ts, ts[1:])), default=0)
        print(f"  {n}: longest gap between messages = {gaps:.2f} s")
run(sys.argv[1])
