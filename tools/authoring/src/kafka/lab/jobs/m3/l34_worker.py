"""3.4 A billing worker that 'crashes' after processing 25 records. mode: atmost | atleast."""
import sys, os, json
from confluent_kafka import Consumer
mode, T, G, crash_after, log = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
c = Consumer({"bootstrap.servers": "k1:9092", "group.id": G, "auto.offset.reset": "earliest", "enable.auto.commit": False, "session.timeout.ms": 6000})
c.subscribe([T]); done = 0; idle = 0
with open(log, "a") as out:
    while idle < 20:
        msgs = c.consume(10, 1.0)
        if not msgs:
            idle += 1; continue
        idle = 0
        if mode == "atmost": c.commit(asynchronous=False)            # commit BEFORE processing
        for m in msgs:
            out.write(m.value().decode() + "\n"); out.flush()       # "send the invoice"
            done += 1
            if done == crash_after:
                os._exit(1)                                          # crash: no clean shutdown
        if mode == "atleast": c.commit(asynchronous=False)           # commit AFTER processing
c.close()
