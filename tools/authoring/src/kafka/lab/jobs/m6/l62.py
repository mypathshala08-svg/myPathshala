import time, json, subprocess
from confluent_kafka import Producer, Consumer
from confluent_kafka.admin import AdminClient, NewTopic
BS = 'k1:9092,k2:9092,k3:9092'
T = ['orders-62', 'orders-62-retry-5s', 'orders-62-retry-30s', 'orders-62-dlq']
a = AdminClient({'bootstrap.servers': BS})
a.delete_topics(T); time.sleep(4)
for f in a.create_topics([NewTopic(t, 1, 3) for t in T]).values(): f.result()
p = Producer({'bootstrap.servers': BS, 'acks': 'all'})
orders = [{'id': i, 'kind': k} for i, k in enumerate(['ok', 'ok', 'bad-json', 'ok', 'flaky', 'ok', 'payment-down', 'ok'], 1)]
for o in orders: p.produce('orders-62', json.dumps(o) if o['kind'] != 'bad-json' else '{id: 3, kind: bad', key=str(o['id']))
p.flush()
print('== 1) 8 orders: 5 ok, 1 malformed, 1 flaky (works on 2nd try), 1 payment-down (always fails)')
calls = {}
class Transient(Exception): pass
class Permanent(Exception): pass
def process(raw):
    try: o = json.loads(raw)
    except Exception: raise Permanent('JSONDecodeError')
    calls[o['id']] = calls.get(o['id'], 0) + 1
    if o['kind'] == 'flaky' and calls[o['id']] < 2: raise Transient('timeout from kitchen API')
    if o['kind'] == 'payment-down': raise Transient('payment gateway 503')
    return o['id']
NEXT = {'orders-62': ('orders-62-retry-5s', 5), 'orders-62-retry-5s': ('orders-62-retry-30s', 30), 'orders-62-retry-30s': ('orders-62-dlq', 0)}
SHRINK = {5: 2, 30: 4}   # lab: shrink delays to 2 s and 4 s so the demo is short
c = Consumer({'bootstrap.servers': BS, 'group.id': 'kitchen-62-%d' % time.time(), 'auto.offset.reset': 'earliest', 'enable.auto.commit': False})
c.subscribe(T[:3])
t0 = time.time(); done = 0; log = []
while time.time() - t0 < 25:
    m = c.poll(0.5)
    if m is None or m.error(): continue
    h = dict(m.headers() or [])
    due = float(h.get('x-retry-at', b'0'))
    if time.time() < due:                       # not yet due: pause partition, seek back
        c.seek(__import__('confluent_kafka').TopicPartition(m.topic(), m.partition(), m.offset()))
        time.sleep(0.2); continue
    attempt = int(h.get('x-attempt', b'1'))
    try:
        oid = process(m.value().decode())
        log.append(f'  +{time.time()-t0:4.1f}s {m.topic():20s} order {oid} OK (attempt {attempt})')
    except (Transient, Permanent) as e:
        nxt, d = NEXT[m.topic()] if isinstance(e, Transient) else ('orders-62-dlq', 0)
        hdr = [('x-attempt', str(attempt + 1)), ('x-error', f'{type(e).__name__}: {e}'),
               ('x-original-topic', h.get('x-original-topic', m.topic().encode()).decode() if isinstance(h.get('x-original-topic'), bytes) else m.topic()),
               ('x-original-offset', h.get('x-original-offset', str(m.offset()).encode()).decode() if isinstance(h.get('x-original-offset'), bytes) else str(m.offset()))]
        if d: hdr.append(('x-retry-at', str(time.time() + SHRINK[d])))
        p.produce(nxt, m.value(), key=m.key(), headers=hdr); p.flush()
        log.append(f'  +{time.time()-t0:4.1f}s {m.topic():20s} key {m.key().decode()} {type(e).__name__} ({e}) -> {nxt}')
    c.commit(m, asynchronous=False)
c.close()
print('== 2) processing log (main topic never blocked by retries)')
print('\n'.join(log))
print('== 3) the dead letter queue')
d = Consumer({'bootstrap.servers': BS, 'group.id': 'dlq-reader-%d' % time.time(), 'auto.offset.reset': 'earliest'})
d.subscribe(['orders-62-dlq']); t1 = time.time()
while time.time() - t1 < 8:
    m = d.poll(0.5)
    if m is None or m.error(): continue
    print(f'  key={m.key().decode()} value={m.value().decode()}')
    for k, v in m.headers(): print(f'     {k} = {v.decode()}')
d.close()
print('== 4) end offsets per topic')
for t in T:
    out = subprocess.run(['docker','exec','k1','/opt/kafka/bin/kafka-get-offsets.sh','--bootstrap-server','k1:9092','--topic',t], capture_output=True, text=True).stdout.strip()
    print('  ' + out)
