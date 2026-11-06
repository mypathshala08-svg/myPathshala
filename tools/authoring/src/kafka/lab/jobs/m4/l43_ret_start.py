"""4.3a Time retention: retention.ms=60 s, segment.ms=10 s; produce in 3 waves 15 s apart."""
import json, time, subprocess
from confluent_kafka import Producer
from common import BS, fresh
T = "ret-43"
fresh(T, 1, 3, {"retention.ms": "60000", "segment.ms": "10000"})
p = Producer({"bootstrap.servers": BS})
for wave in range(3):
    for i in range(100):
        p.produce(T, value=json.dumps({"wave": wave, "i": i}))
    p.flush(); time.sleep(15)
p.produce(T, value="roll"); p.flush()
