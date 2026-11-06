import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l81_avro.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('Kafka stores bytes and never checks them. So what stops one team from sending "qty": "two" and breaking ten consumers?',
    'A <b>schema registry</b> plus a serializer. The producer looks up (or registers) the schema, writes a <b>5-byte header</b> (magic byte + schema id) and compact <b>Avro</b> bytes. Consumers fetch the schema by id and decode. In our lab one order took <b>20 bytes instead of 50</b> as JSON, and a bad record was rejected <b>inside the producer</b>, before it ever reached Kafka.',
    ['What a schema registry stores and how ids, subjects and versions work.',
     'The wire format byte by byte.',
     'Avro vs Protobuf vs JSON Schema, and where validation happens.'])
cmap = concept_map('Concept map. Beginner: bytes in Kafka, serializer, schema. Intermediate: Schema Registry, subject, version, schema id, Avro. Advanced: wire format, subject naming strategies, _schemas topic, Protobuf and JSON Schema, Connect converters.',
    [[('by', 'Kafka stores bytes', 'Lesson 2.1', B + '02-producers/01-how-a-producer-sends-a-message/'), ('se', 'Serializer', 'object → bytes', None)],
     [('sr', 'Schema Registry', 'REST :8081', None), ('su', 'Subject + version', 'orders-81-value v1', None), ('id', 'Schema id', 'global number', None), ('av', 'Avro', 'compact binary', None)],
     [('wf', 'Wire format', '0 + id + data', None), ('ns', 'Naming strategy', 'topic / record', None), ('st', '_schemas topic', 'compacted', None), ('ev', 'Evolution', 'Lesson 8.2', B + '08-schemas/02-schema-evolution-and-compatibility/')]],
    [('by', 'se'), ('se', 'sr'), ('sr', 'su'), ('su', 'id'), ('se', 'av'), ('id', 'wf'), ('su', 'ns'), ('sr', 'st'), ('su', 'ev')],
    {'se', 'sr', 'su', 'id', 'av', 'wf', 'ns', 'st'},
    '<b>Builds on:</b> <a href="../../02-producers/01-how-a-producer-sends-a-message/">2.1</a>, <a href="../../07-kafka-connect/01-kafka-connect/">7.1</a> (converters). <b>Next:</b> <a href="../02-schema-evolution-and-compatibility/">8.2 Evolution and compatibility</a>.')
whw = why_how_where(
    'Producers and consumers are deployed by different teams at different times. Without a shared contract, a field rename or type change silently breaks readers, and JSON repeats every field name in every message.',
    'The serializer registers/looks up the schema under a subject (default <code>&lt;topic&gt;-value</code>), gets a global id, and prefixes each message with magic byte 0 + 4-byte id. Deserializers cache id → schema. The registry stores schemas in the compacted <code>_schemas</code> topic and enforces compatibility rules on new versions.',
    'Any multi-team Kafka platform; Connect (AvroConverter/ProtobufConverter); CDC pipelines; data lakes that need typed columns. Implementations: Confluent Schema Registry, Apicurio, Karapace, AWS Glue Schema Registry.',
    'Every client needs registry access (and its own auth). Data is no longer human-readable with plain console tools. Registry downtime blocks producers that see a new schema (cached ones keep working).')

def wire(hl=-1):
    parts = [('00', 'magic', 'violet', 34), ('00 00 00 01', 'schema id', 'amber', 100), ('02 08 69 64 6c 69 04 …', 'Avro data', 'green', 190)]
    o = ''; x = 10
    for k, (hx, lbl, tn, w) in enumerate(parts):
        o += box(x, 50, w, 36, 'acc' if k == hl else tn, rx=4) + t(x + w / 2, 72, hx, 7.6, mono=True) + t(x + w / 2, 104, lbl, 7.4, bold=True)
        x += w + 6
    return o + t(176, 30, 'one Kafka record value (20 bytes)', 7.8, bold=True)
scene_svg = scene('The Confluent wire format of one record value: byte 0 is the magic byte 0, bytes 1 to 4 hold schema id 1, and the remaining 15 bytes are Avro-encoded data.', wire(),
                  '<tspan font-weight="700" class="s-acc">5-byte header</tspan> + Avro: 20 bytes vs 50 as JSON.')
dialogue = '''K> Sir, billing’s consumer crashed at 3 a.m. Someone in the app team changed qty from a number to the word "two".
A> Kafka accepted it because Kafka never looks inside messages. The fix is a <b>contract</b>: a schema in a registry, enforced by the serializer.
R> Doesn’t that make every message bigger?
A> Smaller, actually. Avro sends no field names, only values, plus a 5-byte header pointing to the schema. Let’s count the bytes.'''

lv = '''
LEVELS> Schemas at three levels
L1> The form with numbered boxes
      <ul>
        <li>Instead of writing “Item: idli, Quantity: 2” every time, everyone uses form #1, where box 1 is item and box 2 is quantity. You only write the form number and the values. The registry is the cupboard holding all form designs.</li>
      </ul>
L2> The pieces
      <ul>
        <li><b>Schema</b>: field names and types (Avro JSON, .proto, or JSON Schema). <b>Subject</b>: a named history of schemas, default <code>&lt;topic&gt;-key</code> / <code>&lt;topic&gt;-value</code> (TopicNameStrategy). <b>Version</b>: 1, 2, 3… per subject. <b>Id</b>: global and unique per distinct schema.</li>
        <li>Serializer settings: <code>auto.register.schemas</code> (true by default; turn off in production and register via CI), <code>use.latest.version</code>.</li>
        <li>REST: <code>GET /subjects</code>, <code>/subjects/{s}/versions/latest</code>, <code>/schemas/ids/{id}</code>, <code>POST /subjects/{s}/versions</code>, <code>/config</code>.</li>
      </ul>
L3> Under the hood
      <ul>
        <li>Wire format: byte 0 = 0, bytes 1–4 = big-endian schema id, then the payload (Protobuf adds message-index bytes).</li>
        <li>Avro binary has no field names: ints/longs are zig-zag varints (2 → <code>04</code>), strings are length + UTF-8 (<code>08 69 64 6c 69</code> = 4, “idli”), doubles are 8 little-endian bytes.</li>
        <li><code>RecordNameStrategy</code> / <code>TopicRecordNameStrategy</code> allow several event types in one topic. The registry is a single-writer service backed by the <code>_schemas</code> topic; run several instances for availability.</li>
      </ul>
/LEVELS
'''
HX = figure('Dissection of the 20 bytes of order 1: 00 magic, 00 00 00 01 schema id 1, 02 is id 1 as zig-zag varint, 08 is string length 4, 69 64 6c 69 is idli, 04 is qty 2, and 8 bytes for the double 40.0.',
    t(16, 22, 'Order 1 byte by byte (real hex from the lab)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('00', 'violet', 1), ('00 00 00 01', 'amber', 2), ('02', 'blue', 3), ('08 69 64 6c 69', 'green', 4), ('04', 'blue', 5), ('00…44 40', 'card', 6)]) +
    legend(16, 84, [(1, 'Magic byte', 'format version 0'), (2, 'Schema id', '1 → fetch from registry'), (3, 'id = 1', 'zig-zag varint: 1 → 02'),
                    (4, 'item', 'length 4 (08) + “idli”'), (5, 'qty = 2', 'zig-zag: 2 → 04'), (6, 'price', '8-byte double 40.0')], size=8, gap=15, w=90),
    h=186, caption='No field names are sent: the schema supplies them.')
extra = '''

  <h3>Dissect the bytes</h3>
''' + HX

types_html = table(['Format', 'Schema language', 'Binary?', 'Strengths', 'Watch out'], [
    ['Avro', 'JSON (.avsc)', 'yes', 'compact, great evolution rules, Hadoop/lake friendly', 'needs writer schema to read'],
    ['Protobuf', '.proto', 'yes', 'gRPC ecosystem, generated code', 'field numbers must never be reused'],
    ['JSON Schema', 'JSON Schema', 'no (JSON)', 'readable, easy for web teams', 'bigger, looser evolution'],
    ['Plain JSON', 'none', 'no', 'zero setup', 'no contract at all'],
], minw=660) + table(['Term', 'Our lab'], [
    ['Subject', 'orders-81-value'], ['Version', '1'], ['Schema id', '1'], ['Storage', '_schemas (1 partition, compacted)'], ['Default compatibility', 'BACKWARD'],
], minw=420)
warn = 'Leave auto.register.schemas=true only in development. In production, register schemas through a reviewed CI step and set it to false, or any producer deploy can register a schema nobody approved.'

steps = [
    ('Step 1 · Start the registry',
     code('bash', 'terminal', 'docker run -d --name sr --network kafnet -p 8081:8081 \\\n  -e SCHEMA_REGISTRY_HOST_NAME=sr -e SCHEMA_REGISTRY_LISTENERS=http://0.0.0.0:8081 \\\n  -e SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS=k1:9092,k2:9092,k3:9092 confluentinc/cp-schema-registry:8.1.0\ncurl -s localhost:8081/config', sec('== 1)', '== 2)')),
     'The registry keeps everything in the compacted <code>_schemas</code> topic; default compatibility is BACKWARD (Lesson 8.2).'),
    ('Step 2 · Produce with Avro',
     code('python', 'l81.py', 'schema = {"type": "record", "name": "Order", "fields": [id int, item string, qty int, price double]}\nser = AvroSerializer(SchemaRegistryClient({"url": SR}), json.dumps(schema))\np.produce("orders-81", value=ser(order, SerializationContext("orders-81", MessageField.VALUE)))', sec('== 2)', '== 3)')),
     'The first produce registered the schema under subject <code>orders-81-value</code>: version 1, global id 1.'),
    ('Step 3 · Look at the bytes',
     code('python', 'l81.py', 'b = raw_value\nprint(b.hex(" "), b[0], int.from_bytes(b[1:5], "big"))', sec('== 3)', '== 4)')),
     'Magic 0, schema id 1, then 15 bytes of Avro: 20 bytes in total, 60% smaller than the same order as JSON.'),
    ('Step 4 · Decode',
     code('python', 'l81.py', 'de = AvroDeserializer(SchemaRegistryClient({"url": SR}))\nde(raw, SerializationContext("orders-81", MessageField.VALUE))', sec('== 4)', '== 5)')),
     'The deserializer read id 1, fetched (and cached) the schema, and rebuilt the dicts.'),
    ('Step 5 · Without the registry',
     code('python', 'l81.py', 'print(raw_value[:24])', sec('== 5)', '== 6)')),
     'A plain consumer sees binary: readable text only for strings. Use schema-aware tools (kafka-avro-console-consumer, UI tools).'),
    ('Step 6 · Bad data stopped early',
     code('python', 'l81.py', 'ser({"id": 4, "item": "vada", "qty": "two", "price": 60.0}, ctx)', sec('== 6)')),
     'The serializer refused the record in the producer process: Kafka and every consumer were protected.'),
]
see = [term([('BACKWARD', W), ('_schemas 1 partition compact', G)], size=7.0), term([('orders-81-value', G), ('version 1 · id 1', Y)], size=7.2),
       term([('00 | 00 00 00 01 | ...', Y), ('20 bytes vs 50 JSON', G)], size=7.0), term([("{'id': 1, 'item': 'idli'...}", G)], size=7.0),
       term([("b'\\x00\\x00\\x00\\x00\\x01\\x04\\x08dosa...'", RD)], size=6.8), term([('TypeError: an integer is', RD), ('required on field qty', RD)], size=7.0)]
B1 = [wire(1), wire(1), wire(0), wire(2), wire(2), wire(-1)]
B1 = [b + cap(c, '', tn, y=124, h=30) for b, c, tn in zip(B1, ['Registry stores schemas', 'Id written in header', 'Magic + id = 5 bytes', 'Schema fetched by id', 'Binary without schema', 'Rejected before Kafka'], ['blue', 'amber', 'violet', 'green', 'red', 'red'])]
two = anim_two('Schema Registry and Avro', 'Register, encode, decode, reject', 'Real outputs from the lab', 'Inside the bytes', see, B1, ['Start.', 'Register.', 'Bytes.', 'Decode.', 'Raw.', 'Reject.'], ['Store.', 'Id.', 'Header.', 'Lookup.', 'Binary.', 'Guard.'])
pe = peel('One produce, layer by layer', 'Order 1 with AvroSerializer. (Simplified.)',
    [('Object', ''), ('Lookup', ''), ('Register', ''), ('Encode', ''), ('Frame', ''), ('Send', '')],
    [['Object', 'dict order 1', '', ''], ['Lookup', 'cache: schema → id?', 'miss first time', ''], ['Register', 'POST /subjects/', 'orders-81-value/versions', '→ id 1'],
     ['Encode', 'Avro binary', '15 bytes', 'types checked'], ['Frame', 'magic 0', '+ id 1 (4 bytes)', '= 20 bytes'], ['Send', 'producer.produce', 'Kafka stores bytes', '']],
    ['Dict.', 'Cache.', 'Register.', 'Encode.', 'Frame.', 'Send.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'The 3 a.m. crash', 'qty sent as text. (Typical.)', ('Schema contract', 'Validate in the serializer'), [
    ('App sends qty "two"', 'plain JSON', 'Accepted by Kafka.', 'blue'), ('Billing crashes', 'parse error', 'Incident.', 'red'),
    ('Adopt Avro + registry', 'schema in CI', 'Contract.', 'green'), ('Bad deploy fails in test', 'TypeError in producer', 'Caught early.', 'green'),
    ('Consumers safe', 'typed data', 'Done.', 'blue')], ['Send.', 'Crash.', 'Contract.', 'Catch.', 'Safe.'], 'scenario-crash') + \
       five('Real-time scenario 2', 'Storage bill', 'JSON field names everywhere. (Typical.)', ('Compact encoding', 'Values only'), [
    ('2 B events/day as JSON', '~50 bytes each', 'Big.', 'blue'), ('Switch to Avro', '~20 bytes', '60% smaller.', 'green'),
    ('Plus compression', 'zstd per batch', 'Smaller still.', 'green'), ('Less disk and network', 'RF 3 × savings', 'Cheaper.', 'green'),
    ('Same data', 'decoded by schema', 'Done.', 'blue')], ['JSON.', 'Avro.', 'Compress.', 'Save.', 'Same.'], 'scenario-size') + \
       five('Real-time scenario 3 · advanced', 'Several event types, one topic', 'Order events must stay ordered. (Typical.)', ('Subject naming strategy', 'RecordNameStrategy'), [
    ('OrderPlaced, OrderCooked', 'same key order', 'One topic.', 'blue'), ('TopicNameStrategy', 'one schema per topic', 'Conflict.', 'red'),
    ('TopicRecordNameStrategy', 'subject per type', 'Fix.', 'green'), ('Consumers switch on type', 'union or generic', 'Decode.', 'green'),
    ('Order kept per key', 'one partition', 'Done.', 'blue')], ['Types.', 'Clash.', 'Strategy.', 'Decode.', 'Ordered.'], 'scenario-strategy')
assemble(HERE, h2_story='A contract for your messages', hook_html=hk,
    narration='TiffinGo’s billing consumer crashed because the app team changed a field type. Kabir wants a way to stop bad data before it reaches Kafka.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Schema Registry and Avro',
    formal='A <b>schema registry</b> is a service that stores versioned schemas under <b>subjects</b>, assigns each distinct schema a global <b>id</b>, and enforces compatibility rules. Schema-aware <b>serializers</b> validate and encode records (e.g. in <b>Avro</b>, Protobuf or JSON Schema) and prefix them with a magic byte and the schema id; <b>deserializers</b> resolve the id to the writer schema to decode.',
    simple='The registry is a shared rulebook for message shapes. Producers must follow the rules, and each message carries a tiny number saying which rule it follows, so consumers can read it.',
    term_rows=[('Schema', 'Fields + types.'), ('Subject', 'Named schema history.'), ('Version', 'Number within a subject.'), ('Schema id', 'Global id in each message.'), ('Avro', 'Compact binary format.'), ('Magic byte', 'Format marker 0.'), ('Serializer', 'Object → bytes.'), ('_schemas', 'Registry storage topic.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Kafka validates messages.', 'Kafka stores bytes; serializers validate.', 'Step 6.'),
               ('Schemas make messages bigger.', 'Avro: 20 vs 50 bytes.', 'Step 3.'),
               ('The whole schema travels with each message.', 'Only a 4-byte id.', 'Step 3.')],
    exam='“What is Schema Registry?” Central store of versioned schemas per subject; serializers register/look up, write magic byte + schema id + Avro/Protobuf/JSON payload; deserializers fetch by id; compatibility checks on new versions; stored in _schemas.',
    types_h2='Formats and terms', types_html=types_html, warn=warn,
    steps_h2='Register, encode, decode', steps_intro='All outputs are real: Confluent Schema Registry 8.1.0, Python confluent-kafka 2.16, Kafka 4.4.0.',
    steps=steps, two=two, peel_intro='Now peel one produce.', peel_html=pe,
    scen_intro='Three live scenarios: a crash, a storage bill, and multi-type topics.', scen=scen,
    uc_h2='Schemas at work', ucs=[uc_('team', 'contracts', 'blue', '1. Team contracts', 'Producers and consumers deploy independently.', ['Team A', '*schema', 'Team B']),
        uc_('cdc', 'CDC', 'violet', '2. CDC pipelines', 'Debezium + AvroConverter.', ['DB', '*Avro', 'Lake']),
        uc_('lake', 'lake', 'green', '3. Typed data lakes', 'Columns created from schemas.', ['Topic', '*schema', 'Parquet']),
        uc_('gov', 'govern', 'amber', '4. Data governance', 'Catalog of all event types.', ['Events', '*registry', 'Catalog'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../../07-kafka-connect/01-kafka-connect/">7.1 Connect</a>.')
