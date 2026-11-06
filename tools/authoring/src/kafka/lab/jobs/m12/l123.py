import json, time, random, subprocess, threading
from confluent_kafka import Producer, Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer, AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField
PRODUCE = False
BS = 'k1:9092,k2:9092,k3:9092'; SR = 'http://localhost:8081'; T = 'cap-orders'
src = SchemaRegistryClient({'url': SR})
schema = src.get_latest_version(T + '-value').schema.schema_str
ser = AvroSerializer(src, schema); de = AvroDeserializer(src)
p = Producer({'bootstrap.servers': BS, 'acks': 'all', 'enable.idempotence': True})
random.seed(7); items = ['idli', 'dosa', 'thali', 'vada', 'lassi', 'pizza']
for i in range(3001, 6001) if PRODUCE else []:
    o = {'id': i, 'city': random.choice(['Mumbai', 'Pune', 'Delhi']), 'item': random.choice(items), 'qty': random.choice([1, 2, 3, 0])}
    p.produce(T, key=o['city'], value=ser(o, SerializationContext(T, MessageField.VALUE)))
p.flush()
print("== 1) 3,000 new orders waiting (ids 3001-6000); a broker dies during processing")
prices = {'idli': 45, 'dosa': 90, 'thali': 150, 'vada': 60, 'lassi': 45}
def chaos():
    time.sleep(2); subprocess.run(['docker', 'kill', 'k3'], capture_output=True); print("  t+2s: docker kill k3")
threading.Thread(target=chaos).start()
c = Consumer({'bootstrap.servers': BS, 'group.id': 'cap-processor', 'enable.auto.commit': False, 'isolation.level': 'read_committed', 'auto.offset.reset': 'earliest'})
tp = Producer({'bootstrap.servers': BS, 'transactional.id': 'cap-processor-1'}); tp.init_transactions(); c.subscribe([T])
ok = dlq = 0; idle = 0; t0 = time.time(); batches = 0
while ok + dlq < 3000 and time.time() - t0 < 120:
    msgs = c.consume(200, 1.0)
    if not msgs: continue
    tp.begin_transaction(); batches += 1
    for m in msgs:
        if m.error(): continue
        o = de(m.value(), SerializationContext(T, MessageField.VALUE))
        if o['qty'] <= 0 or o['item'] not in prices:
            tp.produce('cap-orders-dlq', key=m.key(), value=json.dumps(o), headers=[('x-error', 'bad')]); dlq += 1
        else:
            tp.produce('cap-orders-enriched', key=m.key(), value=json.dumps({**o, 'amount': o['qty'] * prices[o['item']]})); ok += 1
    tp.send_offsets_to_transaction(c.position(c.assignment()), c.consumer_group_metadata()); tp.commit_transaction()
c.close()
print(f"== 2) processor finished: {ok} enriched + {dlq} DLQ = {ok+dlq} in {batches} transactions, {time.time()-t0:.1f} s, with k3 down")
subprocess.run(['docker', 'start', 'k3'], capture_output=True); time.sleep(15)
def read_ids(topic):
    r = Consumer({'bootstrap.servers': BS, 'group.id': 'audit-%s-%d' % (topic, time.time()), 'auto.offset.reset': 'earliest', 'isolation.level': 'read_committed'})
    r.subscribe([topic]); ids = []; t = time.time()
    while time.time() - t < 12:
        m = r.poll(0.5)
        if m and not m.error(): ids.append(json.loads(m.value())['id'])
    r.close(); return ids
e, d = read_ids('cap-orders-enriched'), read_ids('cap-orders-dlq')
print("== 3) audit (read_committed, all 6,000 orders)")
print(f"  enriched {len(e)} (unique {len(set(e))}), dlq {len(d)} (unique {len(set(d))}), total unique {len(set(e) | set(d))}")
print(f"  every id 1..6000 accounted exactly once: {sorted(set(e) | set(d)) == list(range(1, 6001)) and len(e) + len(d) == 6000}")
