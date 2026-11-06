import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='08-schemas', lesson='01-schema-registry', n='8.1', module_label='Module 8 · Schemas',
    title='Schema Registry and Avro',
    desc='Why Kafka needs schemas, how a schema registry works (subjects, versions, global ids, the _schemas topic), the Confluent wire format byte by byte, Avro binary encoding, and Avro vs Protobuf vs JSON Schema. Real lab with Confluent Schema Registry 8.1 and Kafka 4.4: an order encoded in 20 bytes instead of 50, decoded by schema id, and a bad record rejected inside the producer.',
    og_desc='Schema Registry + Avro on Kafka 4.4: 20 bytes instead of 50, and bad data stopped before Kafka.',
    minutes=22, level='Intermediate',
    lead='How do you stop bad data at the door? We run a <b>Schema Registry</b>, produce <b>Avro</b>, dissect the <b>bytes</b>, and watch a wrong type get rejected. <b>All outputs are real.</b>',
    chips=['20 vs 50 bytes', 'Magic byte + id', 'Rejected before Kafka', 'Runs in your browser (Python)'])
MAIN = '''# Build the Confluent wire format by hand (Avro-style encoding)
import struct

def zigzag(n):                 # Avro int/long encoding
    n = (n << 1) ^ (n >> 63)
    out = b""
    while True:
        b = n & 0x7F; n >>= 7
        out += bytes([b | (0x80 if n else 0)])
        if not n: return out

def avro_string(s):
    data = s.encode()
    return zigzag(len(data)) + data

order = {"id": 1, "item": "idli", "qty": 2, "price": 40.0}
body = zigzag(order["id"]) + avro_string(order["item"]) + zigzag(order["qty"]) + struct.pack("<d", order["price"])
msg = b"\\x00" + (1).to_bytes(4, "big") + body
print(msg.hex(" "), len(msg), "bytes")
'''
RUN = dict(heading='Run the code: encode by hand', intro='<p>Rebuild the lab’s 20 bytes. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    n = (n << 1) ^ (n >> 63)', 'Zig-zag: small numbers stay small, also negatives.'), ('msg = b"\\x00" + (1).to_bytes(4, "big") + body', 'Magic 0 + schema id 1.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>: compare with the lab hex.', code=None),
        dict(label='2 · Predict first: JSON size', hint='<b>Predict first:</b> bytes as JSON.', code='import json\nprint(len(json.dumps({"id": 1, "item": "idli", "qty": 2, "price": 40.0})))\n'),
        dict(label='3 · Read the header', hint='Schema id from bytes.', code='b = bytes.fromhex("0000000001")\nprint(b[0], int.from_bytes(b[1:5], "big"))\n'),
        dict(label='4 · Zig-zag', hint='Encode -1 and 2.', code='print([(n << 1) ^ (n >> 63) for n in (-1, 2)])\n'),
        dict(label='5 · Spot the error', hint='Wrong type for qty.', expect='error', code='qty = "two"\nif not isinstance(qty, int):\n    raise TypeError("an integer is required on field qty")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: registry + Avro', intro='<p>Needs Docker, the lab, and <code>pip install confluent-kafka[avro]</code>. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Registry', cmd='docker run -d --name sr --network kafnet -p 8081:8081 -e SCHEMA_REGISTRY_HOST_NAME=sr -e SCHEMA_REGISTRY_LISTENERS=http://0.0.0.0:8081 -e SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS=k1:9092 confluentinc/cp-schema-registry:8.1.0', file='terminal', output='', note='Port 8081.'),
           dict(title='2 · Config', cmd='curl -s localhost:8081/config', file='terminal', output='{"compatibilityLevel":"BACKWARD"}', note='Default.'),
           dict(title='3 · Subjects', cmd='curl -s localhost:8081/subjects', file='terminal', output='["orders-81-value"]', note='After producing.'),
           dict(title='4 · Schema by id', cmd='curl -s localhost:8081/schemas/ids/1', file='terminal', output='{"schema":"{\\"type\\":\\"record\\",\\"name\\":\\"Order\\",…}"}', note='What deserializers fetch.')])
TRACE = dict(heading='Encoding step by step', intro='<p>Header, then values.</p>',
    code='msg = b"\\x00"\nmsg += (1).to_bytes(4, "big")\nmsg += bytes([2])\nmsg += bytes([8]) + b"idli"\nprint(msg.hex(" "))\n',
    notes={1: 'Magic :: Format 0.', 2: 'Schema id :: 4 bytes big-endian.', 3: 'id=1 :: Zig-zag → 02.', 4: 'String :: Length 4 → 08.'})
WORKED_INTRO = 'Three schema decisions.'
EXAMPLES = [
    dict(level='b', tag='Schemas · format', title='Pick a format', problem='<p>Java + Python teams, data lake.</p>', inp='need',
         approach=['Avro: compact, lake friendly.', 'Protobuf if gRPC shop.', 'JSON Schema for web teams.'], code='print("Avro")\n', notes={1: 'Default :: Avro in Kafka land.'}, tryit='Types table.'),
    dict(level='i', tag='Schemas · CI', title='Register in CI', problem='<p>Unreviewed schemas appear.</p>', inp='config',
         approach=['auto.register.schemas=false in prod.', 'CI registers after review.', 'use.latest.version=true.'], code='print({"auto.register.schemas": False, "use.latest.version": True})\n', notes={1: 'Govern :: Reviewed contracts.'}, tryit='Warning box.'),
    dict(level='a', tag='Schemas · Connect', title='Avro in Connect', problem='<p>Debezium output should be Avro.</p>', inp='config',
         approach=['value.converter=AvroConverter.', 'value.converter.schema.registry.url.', 'Sinks get typed records.'], code='print({"value.converter": "io.confluent.connect.avro.AvroConverter", "value.converter.schema.registry.url": "http://sr:8081"})\n', notes={1: 'Typed :: Columns auto-created.'}, tryit='Lesson 7.2.')]
QUIZ = mix([
    dict(q='Beginner: Does Kafka validate message contents?', options=['Yes', 'No, it stores bytes', 'Only JSON', 'Only keys'], answer=1, why='Serializers validate.'),
    dict(q='Beginner: Default subject for topic orders values…', options=['orders', 'orders-value', 'value-orders', 'Order'], answer=1, why='TopicNameStrategy.'),
    dict(q='Beginner: The registry default compatibility is…', options=['NONE', 'BACKWARD', 'FULL', 'FORWARD'], answer=1, why='Lab /config.'),
    dict(q='Intermediate: Our Avro order size was…', options=['50 bytes', '20 bytes', '5 bytes', '100 bytes'], answer=1, why='vs 50 JSON.'),
    dict(q='Intermediate: Bytes 1–4 of the value are…', options=['Length', 'Schema id', 'CRC', 'Offset'], answer=1, why='Big-endian id.'),
    dict(q='Intermediate: The bad record (qty "two") was rejected by…', options=['The broker', 'The producer’s serializer', 'The consumer', 'Nobody'], answer=1, why='Before Kafka.'),
    dict(q='Advanced: Registry storage is…', options=['A database', 'The compacted _schemas topic', 'ZooKeeper', 'Files'], answer=1, why='Kafka-backed.'),
    dict(q='Advanced: Several event types in one topic need…', options=['TopicNameStrategy', 'RecordNameStrategy or TopicRecordNameStrategy', 'More partitions', 'NONE mode'], answer=1, why='Subject per type.')])
REVISION = ['Registry: subjects, versions, global ids; stored in _schemas; REST 8081.', 'Wire format: magic 0 + 4-byte id + payload.',
    'Lab: subject orders-81-value v1 id 1; 20 vs 50 bytes; decoded by id.', 'Serializer rejected qty "two" before Kafka.', 'Avro vs Protobuf vs JSON Schema; auto.register off in prod.']
FAQ = [('Is Schema Registry part of Apache Kafka?', 'No. It is a separate service (Confluent, Apicurio, Karapace, AWS Glue…).'),
    ('What if the registry is down?', 'Clients with cached schemas keep working; new schemas cannot be registered or fetched.'),
    ('Can the key also use Avro?', 'Yes, subject <topic>-key; many teams keep keys as simple strings.'),
    ('How do I read Avro from the CLI?', 'kafka-avro-console-consumer (Confluent) or tools like kcat with -s avro and -r registry.')]
PRACTICE_INTRO = 'Schema programs.'
PROBLEMS = [
    dict(level='easy', title='Subject', stmt='Value subject for payments.', inp='str', code='print("payments" + "-value")\n', explain='payments-value.'),
    dict(level='easy', title='Header', stmt='Header size.', inp='int', code='print(1 + 4)\n', explain='5 bytes.'),
    dict(level='easy', title='Saving', stmt='20 vs 50 bytes.', inp='ints', code='print(round((1 - 20 / 50) * 100), "% smaller")\n', explain='60%.'),
    dict(level='medium', title='Parse id', stmt='Id from 00 00 00 00 2a.', inp='hex', code='print(int.from_bytes(bytes.fromhex("000000002a")[1:5], "big"))\n', explain='42.'),
    dict(level='medium', title='Validate', stmt='Check field types.', inp='dict', code='s = {"id": int, "qty": int}\no = {"id": 1, "qty": "2"}\nprint([k for k, t in s.items() if not isinstance(o[k], t)])\n', explain="['qty']."),
    dict(level='medium', title='String bytes', stmt='Avro bytes for "dosa".', inp='str', code='print(bytes([8]) + b"dosa")\n', explain='Length 4 → 08.'),
    dict(level='business', title='Daily savings', stmt='1 B msgs × 30 bytes saved.', inp='ints', code='print(1_000_000_000 * 30 / 1e9, "GB/day (x RF 3)")\n', explain='30 GB.'),
    dict(level='business', title='Cache', stmt='Registry calls with id cache.', inp='ints', code='print(1, "per new schema id, not per message")\n', explain='Cheap.')]
SCN_INTRO = 'Schema interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“Why use Schema Registry?”', 'Explain.', 'answer?', '<p>To share and enforce message schemas between producers and consumers: serializers validate, messages carry a schema id instead of the full schema, and the registry checks that new versions stay compatible.</p>', '“To store messages.”') +
    scn('Platform', 'Mid-level', 'Unknown magic byte', 'Consumer error.', 'cause?', '<ul><li>Data not written with the registry serializer (plain JSON).</li><li>Align serializers or use a DLQ.</li></ul>', 'Restart the registry.') +
    scn('Platform', 'Mid-level', 'Rogue schemas', 'Random versions appear.', 'fix?', '<ul><li>auto.register.schemas=false.</li><li>CI registration, ACLs.</li></ul>', 'Delete subjects weekly.') +
    scn('Data', 'Senior', 'Format choice', 'Kafka → lakehouse.', 'choose?', '<ul><li>Avro (or Protobuf) with registry.</li><li>Sinks map to Parquet columns.</li></ul>', 'Plain JSON strings.'))
