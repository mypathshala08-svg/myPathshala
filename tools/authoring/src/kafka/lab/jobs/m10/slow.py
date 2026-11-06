import json, time
from confluent_kafka import Consumer
st = {}
def stats(s): st['d'] = json.loads(s)
c = Consumer({'bootstrap.servers': 'k1:9092,k2:9092,k3:9092', 'group.id': 'slow-kitchen-101', 'auto.offset.reset': 'earliest',
              'statistics.interval.ms': 2000, 'stats_cb': stats})
c.subscribe(['orders-101'])
t0, n = time.time(), 0
while time.time() - t0 < 18:
    m = c.poll(0.1)
    if m and not m.error():
        n += 1; time.sleep(0.02)
c.close()
d = st.get('d', {})
lag = {p: v['consumer_lag'] for p, v in d.get('topics', {}).get('orders-101', {}).get('partitions', {}).items() if p != '-1'}
print(f"  consumer processed {n} orders in 18 s")
print(f"  client-side view (librdkafka stats): consumer_lag per partition {lag}, rx msgs {d.get('rxmsgs')}")
