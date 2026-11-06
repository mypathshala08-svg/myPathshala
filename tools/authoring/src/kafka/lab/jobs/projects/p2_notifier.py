"""Project 2 · UPI fraud alert: a second service that reads the alerts topic and 'sends SMS'."""
import json
from confluent_kafka import Consumer
c = Consumer({"bootstrap.servers": "localhost:9092", "group.id": "sms-notifier", "auto.offset.reset": "earliest"})
c.subscribe(["fraud-alerts"]); idle = 0
while idle < 6:
    m = c.poll(1.0)
    if m is None or m.error():
        idle += 1; continue
    idle = 0; a = json.loads(m.value())
    print(f"  SMS to {a['vpa']}: payment {a['txn']} of Rs {a['amount']} held for review ({a['reason']})")
c.close()
