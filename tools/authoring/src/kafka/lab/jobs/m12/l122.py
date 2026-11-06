import json, time, random, subprocess, requests
from confluent_kafka import Producer, Consumer, TopicPartition
from confluent_kafka.admin import AdminClient, NewTopic, ConfigResource
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer, AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField
BS = 'k1:9092,k2:9092,k3:9092'; SR = 'http://localhost:8081'
T = {'orders': 'cap-orders', 'menu': 'cap-menu', 'ok': 'cap-orders-enriched', 'dlq': 'cap-orders-dlq'}
a = AdminClient({'bootstrap.servers': BS})
a.delete_topics(list(T.values())); time.sleep(5)
for k, t in T.items():
    cfg = {'cleanup.policy': 'compact'} if k == 'menu' else {'min.insync.replicas': '2'}
    a.create_topics([NewTopic(t, 6 if k == 'orders' else 3, 3, config=cfg)])[t].result()
requests.delete(f'{SR}/subjects/{T["orders"]}-value'); requests.delete(f'{SR}/subjects/{T["orders"]}-value?permanent=true')
print("== 1) topics created (orders 6 partitions, RF 3, min ISR 2; menu compacted)")
for t in T.values():
    md = a.list_topics(t).topics[t]
    print(f"  {t:22s} partitions {len(md.partitions)}")
# --- menu (compacted reference data)
p = Producer({'bootstrap.servers': BS, 'acks': 'all', 'enable.idempotence': True})
menu = {'idli': 40, 'dosa': 90, 'thali': 150, 'vada': 60, 'lassi': 45}
for k, v in menu.items(): p.produce(T['menu'], key=k, value=str(v))
p.produce(T['menu'], key='idli', value='45')        # price update; compaction keeps the latest
p.flush()
# --- orders with Avro + Schema Registry
schema = json.dumps({"type": "record", "name": "Order", "namespace": "in.tiffingo", "fields": [
    {"name": "id", "type": "int"}, {"name": "city", "type": "string"}, {"name": "item", "type": "string"}, {"name": "qty", "type": "int"}]})
src = SchemaRegistryClient({'url': SR}); ser = AvroSerializer(src, schema)
random.seed(42); cities = ['Mumbai', 'Pune', 'Delhi']; items = list(menu) + ['pizza']
t0 = time.time(); N = 3000
for i in range(1, N + 1):
    o = {'id': i, 'city': random.choice(cities), 'item': random.choice(items), 'qty': random.choice([1, 2, 3, 0])}
    p.produce(T['orders'], key=o['city'], value=ser(o, SerializationContext(T['orders'], MessageField.VALUE)))
    if i % 500 == 0: p.poll(0)
p.flush()
print(f"== 2) producer: {N} Avro orders (idempotent, acks=all) in {time.time()-t0:.1f} s; schema id {src.get_latest_version(T['orders']+'-value').schema_id}")
# --- processor: exactly-once consume-transform-produce
de = AvroDeserializer(src)
prices = {}
mc = Consumer({'bootstrap.servers': BS, 'group.id': 'cap-menu-%d' % time.time(), 'auto.offset.reset': 'earliest'})
mc.subscribe([T['menu']]); t1 = time.time()
while time.time() - t1 < 8:
    m = mc.poll(0.5)
    if m and not m.error(): prices[m.key().decode()] = int(m.value())
mc.close()
c = Consumer({'bootstrap.servers': BS, 'group.id': 'cap-processor', 'auto.offset.reset': 'earliest', 'enable.auto.commit': False, 'isolation.level': 'read_committed'})
tp = Producer({'bootstrap.servers': BS, 'transactional.id': 'cap-processor-1'})
tp.init_transactions(); c.subscribe([T['orders']])
ok = dlq = 0; revenue = {}; t2 = time.time(); idle = 0
while idle < 6:
    msgs = c.consume(500, 1.0)
    if not msgs: idle += 1; continue
    idle = 0; tp.begin_transaction()
    for m in msgs:
        if m.error(): continue
        o = de(m.value(), SerializationContext(m.topic(), MessageField.VALUE))
        reason = 'qty must be > 0' if o['qty'] <= 0 else ('unknown item' if o['item'] not in prices else None)
        if reason:
            tp.produce(T['dlq'], key=m.key(), value=json.dumps(o), headers=[('x-error', reason), ('x-original-offset', str(m.offset()))]); dlq += 1
        else:
            amount = o['qty'] * prices[o['item']]
            tp.produce(T['ok'], key=m.key(), value=json.dumps({**o, 'price': prices[o['item']], 'amount': amount})); ok += 1
            revenue[o['city']] = revenue.get(o['city'], 0) + amount
    tp.send_offsets_to_transaction(c.position(c.assignment()), c.consumer_group_metadata())
    tp.commit_transaction()
c.close()
print(f"== 3) processor (transactions, read_committed): {ok} enriched + {dlq} to DLQ = {ok+dlq} in {time.time()-t2:.1f} s")
print("  menu used (compacted, latest wins): idli =", prices['idli'])
print("  revenue by city:", dict(sorted(revenue.items())))
print("== 4) reconciliation and health")
def end(t): return sum(Consumer({'bootstrap.servers': BS, 'group.id': 'x'}).get_watermark_offsets(TopicPartition(t, i))[1] for i in range(len(a.list_topics(t).topics[t].partitions)))
print(f"  end offsets: orders {end(T['orders'])}, enriched {end(T['ok'])} (+ commit markers), dlq {end(T['dlq'])} (+ markers)")
out = subprocess.run(['docker','exec','-e','JMX_PORT=','k2','/opt/kafka/bin/kafka-consumer-groups.sh','--bootstrap-server','k2:9092','--describe','--group','cap-processor'],capture_output=True,text=True).stdout
lag = sum(int(l.split()[5]) for l in out.splitlines()[1:] if l.strip() and l.split()[5].isdigit())
print("  processor group lag:", lag)
dl = Consumer({'bootstrap.servers': BS, 'group.id': 'cap-dlqr-%d' % time.time(), 'auto.offset.reset': 'earliest'}); dl.subscribe([T['dlq']])
reasons = {}; t3 = time.time()
while time.time() - t3 < 8:
    m = dl.poll(0.5)
    if m and not m.error():
        r = dict(m.headers())['x-error'].decode(); reasons[r] = reasons.get(r, 0) + 1
dl.close(); print("  DLQ by reason:", reasons)
print("== 5) sink: Kafka Connect writes enriched orders to a file")
requests.delete('http://localhost:8083/connectors/cap-sink'); time.sleep(2)
requests.put('http://localhost:8083/connectors/cap-sink/config', json={"connector.class": "org.apache.kafka.connect.file.FileStreamSinkConnector", "file": "/data/cap-enriched.txt", "topics": T['ok'], "tasks.max": "1",
    "value.converter": "org.apache.kafka.connect.storage.StringConverter", "key.converter": "org.apache.kafka.connect.storage.StringConverter", "consumer.override.isolation.level": "read_committed"})
time.sleep(20)
st = requests.get('http://localhost:8083/connectors/cap-sink/status').json()
lines = open('/root/lab/kafka/connect/data/cap-enriched.txt').read().splitlines()
print("  connector", st['connector']['state'], "| lines in file:", len(lines))
print("  sample:", lines[0])
