"""2.5 Make a real duplicate: a follower is frozen, so acks=all is slow; the producer times out and retries."""
import sys, time
from confluent_kafka import Producer
topic, idem = sys.argv[1], sys.argv[2] == "on"
res = []
p = Producer({"bootstrap.servers": "k1:9092", "acks": "all", "enable.idempotence": idem, "retries": 10,
              "request.timeout.ms": 3000, "message.timeout.ms": 120000, "retry.backoff.ms": 500,
              "max.in.flight.requests.per.connection": 5})
p.produce(topic, key="user3@upi", value="pay Rs 75000 (t045)", callback=lambda e, m: res.append(e.str() if e else f"offset {m.offset()}"))
t0 = time.time(); p.flush(150)
print(f"  enable.idempotence={idem}: delivered after {time.time()-t0:.0f} s -> {res}")
