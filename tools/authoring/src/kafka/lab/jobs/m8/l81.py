import json, subprocess, time, requests
from confluent_kafka import Producer, Consumer
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer, AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField, StringSerializer
BS = 'k1:9092,k2:9092,k3:9092'; SR = 'http://localhost:8081'; T = 'orders-81'
for s in requests.get(SR + '/subjects').json():
    requests.delete(f'{SR}/subjects/{s}'); requests.delete(f'{SR}/subjects/{s}?permanent=true')
a = AdminClient({'bootstrap.servers': BS}); a.delete_topics([T]); time.sleep(4)
a.create_topics([NewTopic(T, 1, 3)])['orders-81'].result()
print('== 1) the registry: default compatibility and its storage topic')
print('  GET /config ->', requests.get(SR + '/config').json())
out = subprocess.run(['docker','exec','k1','/opt/kafka/bin/kafka-topics.sh','--bootstrap-server','k1:9092','--describe','--topic','_schemas'],capture_output=True,text=True).stdout.splitlines()[0]
f=out.split('\t'); print('  ' + ' | '.join(x.strip() for x in f if x.strip().startswith(('Topic:', 'PartitionCount', 'ReplicationFactor', 'Configs'))))
schema = json.dumps({"type": "record", "name": "Order", "namespace": "in.tiffingo", "fields": [
    {"name": "id", "type": "int"}, {"name": "item", "type": "string"}, {"name": "qty", "type": "int"}, {"name": "price", "type": "double"}]})
src = SchemaRegistryClient({'url': SR})
ser = AvroSerializer(src, schema)
p = Producer({'bootstrap.servers': BS})
orders = [{"id": 1, "item": "idli", "qty": 2, "price": 40.0}, {"id": 2, "item": "dosa", "qty": 1, "price": 90.0}, {"id": 3, "item": "thali", "qty": 1, "price": 150.0}]
for o in orders:
    p.produce(T, key=str(o['id']), value=ser(o, SerializationContext(T, MessageField.VALUE)))
p.flush()
print('== 2) producing with AvroSerializer auto-registered the schema')
print('  GET /subjects ->', requests.get(SR + '/subjects').json())
v = requests.get(f'{SR}/subjects/{T}-value/versions/latest').json()
print('  latest version:', v['version'], ' schema id:', v['id'], ' type:', v.get('schemaType', 'AVRO'))
print('== 3) the bytes on the wire (first record)')
c = Consumer({'bootstrap.servers': BS, 'group.id': 'raw-%d' % time.time(), 'auto.offset.reset': 'earliest'}); c.subscribe([T])
raw = []
t0 = time.time()
while len(raw) < 3 and time.time() - t0 < 15:
    m = c.poll(0.5)
    if m and not m.error(): raw.append(m.value())
c.close()
b = raw[0]
print('  hex:', b.hex(' '))
print(f'  byte 0 magic = {b[0]}, bytes 1-4 schema id = {int.from_bytes(b[1:5], "big")}, then {len(b) - 5} bytes of Avro data')
js = json.dumps(orders[0]).encode()
print(f'  total {len(b)} bytes vs {len(js)} bytes as JSON: {js.decode()}')
print('== 4) decoding with AvroDeserializer (fetches schema id from the registry)')
de = AvroDeserializer(src)
for r in raw: print('  ', de(r, SerializationContext(T, MessageField.VALUE)))
print('== 5) a plain string consumer sees binary')
print('  ', raw[1][:24])
print('== 6) wrong type is stopped in the producer, before Kafka')
try:
    ser({"id": 4, "item": "vada", "qty": "two", "price": 60.0}, SerializationContext(T, MessageField.VALUE))
except Exception as e:
    print('  ', type(e).__name__ + ':', str(e)[:150])
