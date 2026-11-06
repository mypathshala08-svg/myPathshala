import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='07-kafka-connect', lesson='01-kafka-connect', n='7.1', module_label='Module 7 · Kafka Connect',
    title='Kafka Connect: source and sink connectors',
    desc='Kafka Connect explained: workers, connectors and tasks, source and sink connectors, converters and the JsonConverter schema envelope, single message transforms (SMTs), internal config/offset/status topics, the REST API, the offsets API, and error tolerance with a dead letter queue. Real Kafka 4.4 lab: a file streamed into Kafka with SMTs, live appends, a stored file position, and a bad JSON record routed to a DLQ with context headers.',
    og_desc='Kafka Connect on 4.4: one JSON config streams a file into Kafka, SMTs reshape it, and bad records land in a DLQ.',
    minutes=24, level='Intermediate',
    lead='How do you move data into and out of Kafka without code? We run a <b>Connect worker</b>, stream a file with <b>SMTs</b>, and send a broken record to a <b>DLQ</b>. <b>All outputs are real.</b>',
    chips=['REST :8083', 'schema/payload envelope', 'Offset = byte 53', 'Runs in your browser (Python)'])
MAIN = '''# A tiny Connect pipeline: source -> SMTs -> converter
import json
lines = ["idli,2,40", "dosa,1,90"]

def hoist(v):  return {"line": v}                        # HoistField$Value
def insert(v): return {**v, "source": "kitchen-file"}    # InsertField$Value

def convert(v, schemas=False):
    if schemas:
        return json.dumps({"schema": {"type": "struct"}, "payload": v})
    return json.dumps(v)

offset = 0
for ln in lines:
    print(convert(insert(hoist(ln))))
    offset += len(ln) + 1
print("stored source offset:", {"position": offset})
'''
RUN = dict(heading='Run the code: a mini pipeline', intro='<p>Connect’s steps in plain Python. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    print(convert(insert(hoist(ln))))', 'SMTs run in order, then the converter.'), ('    offset += len(ln) + 1', 'File source offset = byte position.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Then set schemas=True.', code=None),
        dict(label='2 · Predict first: offset', hint='<b>Predict first:</b> 5 lines of our file end at byte…', code='lines = ["idli,2,40", "dosa,1,90", "thali,1,150", "vada,3,60", "lassi,2,90"]\nprint(sum(len(l) + 1 for l in lines))\n'),
        dict(label='3 · Envelope', hint='schemas.enable=true.', code='import json\nprint(json.dumps({"schema": {"type": "string", "optional": False}, "payload": "idli,2,40"}))\n'),
        dict(label='4 · Tasks', hint='10 tables, tasks.max 4.', code='print(min(10, 4), "tasks")\n'),
        dict(label='5 · Spot the error', hint='InsertField on a plain string.', expect='error', code='v = "idli,2,40"\nif not isinstance(v, dict):\n    raise TypeError("Only Struct objects supported for [field insertion]")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: a Connect worker', intro='<p>Needs Docker and the 3-broker lab. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Start worker', cmd='docker run -d --name kc --network kafnet -p 8083:8083 -v $PWD/plugins:/plugins -v $PWD/worker.properties:/w.properties -v $PWD/data:/data --entrypoint /opt/kafka/bin/connect-distributed.sh apache/kafka:4.4.0 /w.properties', file='terminal', output='', note='plugin.path=/plugins.'),
           dict(title='2 · Check', cmd='curl -s localhost:8083/', file='terminal', output='{"version":"4.4.0","commit":"1156b2752aaa28ea","kafka_cluster_id":"TiffinGoKafkaLab0001A"}', note='REST API.'),
           dict(title='3 · Status', cmd='curl -s localhost:8083/connectors/file-src/status', file='terminal', output='connector RUNNING on kc:8083 | tasks [(0, \'RUNNING\')]', note='Summarised.'),
           dict(title='4 · Offsets', cmd='curl -s localhost:8083/connectors/file-src/offsets', file='terminal', output='{"offsets":[{"partition":{"filename":"/data/orders.txt"},"offset":{"position":53}}]}', note='KIP-875.')])
TRACE = dict(heading='One record step by step', intro='<p>Hoist, insert, convert.</p>',
    code='v = "vada,3,60"\nv = {"line": v}\nv["source"] = "kitchen-file"\nprint(v)\n',
    notes={2: 'HoistField :: String → struct.', 3: 'InsertField :: Add static field.', 4: 'Converter :: JSON bytes next.'})
WORKED_INTRO = 'Three Connect decisions.'
EXAMPLES = [
    dict(level='b', tag='Connect · choose', title='Code or connector?', problem='<p>Copy a Postgres table to Kafka.</p>', inp='need',
         approach=['Search for an existing connector.', 'Debezium (CDC) or JDBC source.', 'Write code only if none fits.'], code='print("Debezium Postgres connector")\n', notes={1: 'Reuse :: Retries, offsets free.'}, tryit='Lesson 7.2.'),
    dict(level='i', tag='Connect · converters', title='Plain JSON for consumers', problem='<p>Consumers complain about schema/payload wrapper.</p>', inp='config',
         approach=['value.converter.schemas.enable=false.', 'Or Avro + Schema Registry.', 'Per connector override.'], code='print({"value.converter.schemas.enable": "false"})\n', notes={1: 'Trade-off :: Sinks may need schemas.'}, tryit='Step 3 vs 4.'),
    dict(level='a', tag='Connect · errors', title='Robust sink', problem='<p>Occasional malformed records.</p>', inp='config',
         approach=['errors.tolerance=all.', 'DLQ topic + context headers.', 'errors.log.enable for logs.'], code='print({"errors.tolerance": "all", "errors.deadletterqueue.topic.name": "dlq", "errors.deadletterqueue.context.headers.enable": "true"})\n', notes={1: 'Visible :: Never silent drops.'}, tryit='Step 6.')]
QUIZ = mix([
    dict(q='Beginner: A source connector…', options=['Reads from Kafka', 'Writes into Kafka from another system', 'Deletes topics', 'Elects leaders'], answer=1, why='Into Kafka.'),
    dict(q='Beginner: Connect is managed via…', options=['SQL', 'A REST API', 'ZooKeeper', 'SSH only'], answer=1, why='Port 8083.'),
    dict(q='Beginner: A task is…', options=['A topic', 'A unit of work of a connector', 'A broker', 'A schema'], answer=1, why='tasks.max.'),
    dict(q='Intermediate: schemas.enable=true makes JsonConverter…', options=['Compress', 'Wrap values in schema + payload', 'Drop keys', 'Use Avro'], answer=1, why='Envelope.'),
    dict(q='Intermediate: Our file source offset after 5 lines was…', options=['5', '53', '0', '25'], answer=1, why='Byte position.'),
    dict(q='Intermediate: SMT stands for…', options=['Single message transform', 'Stream merge table', 'Schema map type', 'Sink mode toggle'], answer=0, why='Per record.'),
    dict(q='Advanced: In distributed mode, offsets live in…', options=['A local file', 'connect-offsets topic', 'ZooKeeper', 'The source DB'], answer=1, why='Compacted topic.'),
    dict(q='Advanced: The DLQ header showing where it failed…', options=['__connect.errors.stage', 'x-attempt', 'kafka.offset', 'retry-at'], answer=0, why='VALUE_CONVERTER in our lab.')])
REVISION = ['Worker runs connectors split into tasks; source in, sink out.', 'Converter = bytes ↔ data; SMT = per-record reshape.',
    'State in connect-configs/offsets/status (compacted); REST on 8083.', 'Lab: envelope vs plain; HoistField+InsertField; offset position 53.', 'errors.tolerance=all + DLQ with __connect.errors.* headers.']
FAQ = [('Where do I get connectors?', 'Confluent Hub, Debezium, Apache Camel Kafka connectors, vendors, or write your own with the Connect API.'),
    ('Does Connect need its own cluster?', 'It runs as separate worker processes; often a dedicated Connect cluster per team or use case.'),
    ('Can SMTs filter records?', 'Yes: the Filter SMT with predicates (e.g. TopicNameMatches, HasHeaderKey).'),
    ('Do source connectors support exactly-once?', 'Yes since Kafka 3.3 (KIP-618) when exactly.once.source.support=enabled and the connector supports it.')]
PRACTICE_INTRO = 'Connect programs.'
PROBLEMS = [
    dict(level='easy', title='Topic name', stmt='Route with prefix.', inp='str', code='print("raw." + "orders")\n', explain='Like RegexRouter.'),
    dict(level='easy', title='Hoist', stmt='Wrap a string.', inp='str', code='print({"line": "idli,2,40"})\n', explain='HoistField.'),
    dict(level='easy', title='Offset', stmt='Bytes for "idli,2,40\\n".', inp='str', code='print(len("idli,2,40\\n"))\n', explain='10.'),
    dict(level='medium', title='Mask', stmt='Mask a phone field.', inp='dict', code='r = {"item": "idli", "phone": "98200"}\nr["phone"] = "*****"\nprint(r)\n', explain='MaskField.'),
    dict(level='medium', title='Filter', stmt='Drop test orders.', inp='list', code='rs = [{"id": 1, "test": False}, {"id": 2, "test": True}]\nprint([r for r in rs if not r["test"]])\n', explain='Filter SMT.'),
    dict(level='medium', title='Parse DLQ headers', stmt='Find stage.', inp='dict', code='h = {"__connect.errors.stage": "VALUE_CONVERTER"}\nprint(h["__connect.errors.stage"])\n', explain='Where it failed.'),
    dict(level='business', title='Tasks needed', stmt='60 MB/s, 15 MB/s per task.', inp='ints', code='print(-(-60 // 15))\n', explain='4.'),
    dict(level='business', title='Saved code', stmt='3 integrations × 400 lines.', inp='ints', code='print(3 * 400, "lines avoided")\n', explain='Config instead.')]
SCN_INTRO = 'Connect interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“What is Kafka Connect?”', 'Explain.', 'answer?', '<p>A framework to move data between Kafka and other systems using source and sink connectors configured via REST, with offsets, scaling and error handling built in.</p>', '“A Kafka client library.”') +
    scn('Data platform', 'Mid-level', 'Task FAILED', 'Sink stopped at night.', 'do?', '<ul><li>GET status for the trace.</li><li>Fix, tolerance + DLQ, restart tasks.</li></ul>', 'Recreate topics.') +
    scn('Data platform', 'Mid-level', 'Weird JSON', 'Consumers see schema/payload.', 'fix?', '<ul><li>schemas.enable=false or Avro + registry.</li></ul>', 'Parse twice.') +
    scn('Platform', 'Senior', 'Scale', 'Connector lags.', 'plan?', '<ul><li>Raise tasks.max, add workers.</li><li>Check sink throughput and batching.</li></ul>', 'More partitions only.'))
