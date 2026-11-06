import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l71_connect.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('Your team wrote 400 lines of Python to copy a file into Kafka, and another 400 to copy Kafka into a database. Kafka Connect does both with a JSON config and zero code.',
    '<b>Kafka Connect</b> is a separate runtime (workers) that runs ready-made <b>connectors</b>: <b>source</b> connectors pull data into Kafka, <b>sink</b> connectors push it out. Converters turn bytes into data, <b>SMTs</b> reshape records on the way, and a dead letter queue catches bad ones. In our lab one REST call streamed a kitchen file into Kafka, appended lines arrived in seconds, and a broken JSON record went to the DLQ with headers telling exactly where it came from.',
    ['Workers, connectors, tasks: who does what.',
     'Converters vs SMTs, and why schemas.enable changes your JSON.',
     'Offsets, restarts and error handling (DLQ) in Connect.'])
cmap = concept_map('Concept map. Beginner: source, sink, connector. Intermediate: worker, task, converter, SMT, REST API. Advanced: internal topics, offsets, standalone vs distributed, error tolerance and DLQ, rebalancing tasks.',
    [[('pr', 'Producer / consumer', 'Modules 2–3', B + '02-producers/01-how-a-producer-sends-a-message/'), ('so', 'Source / sink', 'in / out', None)],
     [('wk', 'Worker', 'JVM process', None), ('cn', 'Connector + tasks', 'config → work', None), ('cv', 'Converter', 'bytes ↔ data', None), ('sm', 'SMT', 'reshape 1 record', None)],
     [('it', 'Internal topics', 'configs/offsets/status', None), ('of', 'Source offsets', 'file position', None), ('dq', 'Errors + DLQ', 'Lesson 6.2', B + '06-queues-and-error-handling/02-retry-topics-and-dead-letter-queues/'), ('cd', 'CDC', 'Lesson 7.2', B + '07-kafka-connect/02-change-data-capture-with-debezium/')]],
    [('pr', 'so'), ('so', 'cn'), ('wk', 'cn'), ('cn', 'cv'), ('cv', 'sm'), ('wk', 'it'), ('it', 'of'), ('cn', 'dq'), ('cn', 'cd')],
    {'so', 'wk', 'cn', 'cv', 'sm', 'it', 'of', 'dq'},
    '<b>Builds on:</b> Modules 2–3, <a href="../../06-queues-and-error-handling/02-retry-topics-and-dead-letter-queues/">6.2</a>. <b>Next:</b> <a href="../02-change-data-capture-with-debezium/">7.2 CDC with Debezium</a>.')
whw = why_how_where(
    'Every system-to-Kafka integration needs the same hard parts: retries, offsets, scaling, restarts, schemas, error handling. Connect solves them once; you only configure.',
    'Workers form a group (like consumers) and share connectors’ tasks. A source task reads from the outside system and returns records; the worker converts and produces them. A sink task receives records the worker consumed and writes them out. Configs, offsets and status live in compacted Kafka topics; you manage everything through a REST API on port 8083.',
    'Databases (JDBC, Debezium CDC), S3/GCS/HDFS sinks, Elasticsearch/OpenSearch, Snowflake/BigQuery, MirrorMaker 2 (itself a set of connectors). Hundreds of connectors on Confluent Hub and open source.',
    'Connectors are plugins (JARs) you must install on every worker (plugin.path). Complex per-record logic belongs in Kafka Streams/Flink, not in a chain of SMTs.')

def pipe(hl=-1):
    parts = [('file / DB', 'card'), ('source task', 'blue'), ('converter', 'violet'), ('SMT', 'amber'), ('topic', 'green')]
    o = ''
    for k, (n, tn) in enumerate(parts):
        o += box(8 + k * 70, 50, 62, 40, 'acc' if k == hl else tn, rx=6) + t(39 + k * 70, 74, n, 7.2, bold=True)
        if k < 4: o += arrow(70 + k * 70, 70, 78 + k * 70, 70)
    return o + t(180, 30, 'worker (JVM) runs tasks, REST :8083', 7.6)
scene_svg = scene('A Connect pipeline: an external file or database is read by a source task inside a worker, passed through a converter and a single message transform, and written to a Kafka topic.', pipe(),
                  'Config, not code: <tspan font-weight="700" class="s-acc">source → converter → SMT → topic</tspan>.')
dialogue = '''K> Sir, the kitchen system writes orders to a CSV file. I was about to write a Python tailer with retries and checkpoints…
A> Stop. That is exactly what a <b>source connector</b> does. You send one JSON config to the Connect REST API.
R> And checkpoints? If it restarts, will it re-read the whole file?
A> No. Connect stores the <b>source offset</b> (here, the byte position in the file) in a Kafka topic. Let’s set it up and break it on purpose.'''

lv = '''
LEVELS> Kafka Connect at three levels
L1> Plug adapters
      <ul>
        <li>Kafka is a power strip. Connectors are adapters: one for files, one for Postgres, one for S3. You don’t rewire the house; you plug in the right adapter and set a few switches.</li>
      </ul>
L2> The parts
      <ul>
        <li><b>Worker</b>: the JVM process (<code>connect-distributed.sh</code>). Several workers with the same <code>group.id</code> form a cluster and share tasks.</li>
        <li><b>Connector</b>: a config + plugin; it splits the job into up to <code>tasks.max</code> <b>tasks</b>, which do the copying.</li>
        <li><b>Converter</b> (<code>key.converter</code>, <code>value.converter</code>): bytes ↔ Connect data. JsonConverter with <code>schemas.enable=true</code> wraps every value in <code>{"schema":…,"payload":…}</code>; Avro/Protobuf converters use Schema Registry (Module 8).</li>
        <li><b>SMT</b> (single message transform): small per-record changes, e.g. HoistField, InsertField, MaskField, ReplaceField, TimestampConverter, RegexRouter, Filter + predicates.</li>
      </ul>
L3> Operations
      <ul>
        <li>Distributed mode stores state in <code>connect-configs</code> (1 partition), <code>connect-offsets</code> (25) and <code>connect-status</code> (5), all compacted. Standalone mode keeps offsets in a local file: dev only.</li>
        <li>REST: <code>PUT /connectors/{name}/config</code>, <code>GET …/status</code>, <code>POST …/restart?includeTasks=true</code>, <code>PUT …/pause</code>, <code>GET/PATCH/DELETE …/offsets</code> (KIP-875, stop the connector first to change offsets).</li>
        <li>Errors: <code>errors.tolerance=none</code> (default) fails the task; <code>all</code> skips bad records. Sinks can route them to <code>errors.deadletterqueue.topic.name</code> with <code>__connect.errors.*</code> headers. <code>errors.retry.timeout</code> retries transient failures.</li>
        <li>Since Kafka 3.x/4.x workers use incremental cooperative rebalancing, so adding a worker moves only some tasks.</li>
      </ul>
/LEVELS
'''
ENV = figure('Dissection of a JsonConverter value with schemas enabled: the schema part says type string, optional false; the payload part is the line idli,2,40.',
    t(16, 22, 'One record with schemas.enable=true', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('{"schema":', 'violet', 1), ('{"type":"string","optional":false}', 'blue', 2), ('"payload":', 'green', 3), ('"idli,2,40"}', 'acc', 4)]) +
    legend(16, 84, [(1, 'Envelope', 'added by JsonConverter, every record'), (2, 'Schema', 'type info so sinks can create columns'),
                    (3, 'Payload', 'the actual data'), (4, 'Value', 'one line of the file')], size=8, gap=15, w=90),
    h=152, caption='Real record from our lab. With schemas.enable=false you get just the payload.')
extra = '''

  <h3>Dissect the envelope</h3>
''' + ENV

types_html = table(['Term', 'What it is', 'Our lab'], [
    ['Worker', 'JVM running connectors', 'container kc, REST :8083'], ['Connector', 'config + plugin', 'file-src, file-sink'],
    ['Task', 'unit of work', 'tasks.max=1'], ['Converter', 'bytes ↔ data', 'JsonConverter'], ['SMT', 'per-record change', 'HoistField, InsertField'],
    ['DLQ', 'bad records topic (sinks)', 'dlq-71'],
], minw=560) + table(['Mode', 'State stored in', 'Use'], [
    ['Standalone', 'local file', 'dev, single machine'], ['Distributed', 'Kafka topics', 'production, scaling, failover'],
], minw=480)
warn = 'errors.tolerance=all without a DLQ silently drops bad records. Always pair it with a DLQ topic and context headers, and alert when the DLQ grows. Also, never put passwords in plain config: use config providers (e.g. FileConfigProvider) so GET /connectors does not leak them.'

steps = [
    ('Step 1 · Worker and plugins',
     code('bash', 'terminal', 'connect-distributed.sh worker.properties   # in container kc\ncurl -s localhost:8083/\ncurl -s localhost:8083/connector-plugins', sec('== 1)', '== 2)')),
     'The worker reports Kafka 4.4.0 and lists installed plugins: file source/sink (copied from the Kafka libs into plugin.path), Debezium Postgres (Lesson 7.2) and MirrorMaker 2’s connectors, which ship with Kafka.'),
    ('Step 2 · Internal topics',
     code('bash', 'terminal', 'kafka-topics.sh --bootstrap-server k1:9092 --describe --topic connect-configs,connect-offsets,connect-status', sec('== 2)', '== 3)')),
     'All three are compacted: only the latest config, offset and status per key matter. 1 / 25 / 5 partitions are the defaults.'),
    ('Step 3 · File source, default converter',
     code('bash', 'terminal', 'curl -X PUT localhost:8083/connectors/file-raw/config -H "Content-Type: application/json" -d \'{\n  "connector.class": "org.apache.kafka.connect.file.FileStreamSourceConnector",\n  "file": "/data/orders.txt", "topic": "orders-71-raw", "tasks.max": "1"}\'', sec('== 3)', '== 4)')),
     'Each line became a record wrapped in the schema/payload envelope.'),
    ('Step 4 · SMTs and plain JSON',
     code('json', 'file-src config', '"value.converter.schemas.enable": "false",\n"transforms": "wrap,tag",\n"transforms.wrap.type": "org.apache.kafka.connect.transforms.HoistField$Value",\n"transforms.wrap.field": "line",\n"transforms.tag.type": "org.apache.kafka.connect.transforms.InsertField$Value",\n"transforms.tag.static.field": "source",\n"transforms.tag.static.value": "kitchen-file"', sec('== 4)', '== 5)')),
     'HoistField turned the string into a struct <code>{line: …}</code>; InsertField added <code>source</code>. Order matters: InsertField needs a struct, so wrap comes first.'),
    ('Step 5 · Live streaming and offsets',
     code('bash', 'terminal', 'curl -s localhost:8083/connectors/file-src/status\nprintf "vada,3,60\\nlassi,2,90\\n" >> orders.txt\ncurl -s localhost:8083/connectors/file-src/offsets', sec('== 5)', '== 6)')),
     'Two appended lines arrived within seconds (3 → 5 records). The stored offset is the byte position 53 in the file: after a restart the task continues from there.'),
    ('Step 6 · Sink with a DLQ',
     code('json', 'file-sink config', '"errors.tolerance": "all",\n"errors.deadletterqueue.topic.name": "dlq-71",\n"errors.deadletterqueue.context.headers.enable": "true"', sec('== 6)')),
     'Two good records were written; the broken one went to dlq-71 with headers: exception class and message, original topic bad-71, partition 0, offset 1, connector name and the failing stage VALUE_CONVERTER. The task kept RUNNING.'),
]
see = [term([('version 4.4.0', G), ('FileStreamSource', W), ('PostgresConnector', W)], size=7.2), term([('configs 1 · offsets 25', W), ('status 5 · compact', G)], size=7.2),
       term([('{"schema":{...},', Y), ('"payload":"idli,2,40"}', G)], size=7.0), term([('{"line":"idli,2,40",', G), ('"source":"kitchen-file"}', G)], size=7.0),
       term([('RUNNING', G), ('records now 5', W), ('position 53', Y)], size=7.2), term([('out.txt 2 rows', G), ('dlq-71: DataException', RD), ('offset 1 VALUE_CONVERTER', Y)], size=7.0)]
B1 = [pipe(1), pipe(4), pipe(2), pipe(3), pipe(0), pipe(-1)]
B1 = [b + cap(c, '', tn, y=120, h=30) for b, c, tn in zip(B1, ['Worker runs tasks', 'State in Kafka', 'Converter adds envelope', 'SMTs reshape', 'Offsets = file position', 'Bad record → DLQ'], ['blue', 'green', 'violet', 'amber', 'blue', 'red'])]
two = anim_two('Kafka Connect', 'Source, SMTs, sink, DLQ', 'Real outputs from the lab', 'Inside the pipeline', see, B1, ['Worker.', 'Topics.', 'Envelope.', 'SMT.', 'Stream.', 'DLQ.'], ['Tasks.', 'State.', 'Schema.', 'Reshape.', 'Offset.', 'Park.'])
pe = peel('One line, layer by layer', '“vada,3,60” appended to the file. (Simplified.)',
    [('Poll', ''), ('Record', ''), ('SMTs', ''), ('Convert', ''), ('Produce', ''), ('Offset', '')],
    [['Poll', 'source task reads', 'new bytes at pos 43', ''], ['Record', 'SourceRecord', 'value "vada,3,60"', 'offset pos 53'],
     ['SMTs', 'HoistField → {line}', 'InsertField → source', ''], ['Convert', 'JsonConverter', 'schemas off → plain JSON', ''],
     ['Produce', 'worker producer', 'topic orders-71', 'acks=all'], ['Offset', 'flush every 2 s', 'connect-offsets', 'position 53']],
    ['Read.', 'Wrap.', 'Shape.', 'Bytes.', 'Send.', 'Remember.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Worker crash', 'One of two workers dies. (Typical.)', ('Distributed mode', 'Tasks move to survivors'), [
    ('2 workers, 4 tasks', 'balanced', 'Running.', 'blue'), ('Worker 2 dies', 'tasks stop', 'Failure.', 'red'),
    ('Group rebalances', 'tasks to worker 1', 'Incremental.', 'amber'), ('Resume from offsets', 'connect-offsets', 'No re-read.', 'green'),
    ('Worker 2 returns', 'tasks shared again', 'Healed.', 'green')], ['Run.', 'Crash.', 'Move.', 'Resume.', 'Heal.'], 'scenario-worker') + \
       five('Real-time scenario 2', 'Sink task FAILED', 'One bad row stops the warehouse load. (Typical.)', ('errors.tolerance', 'Skip + DLQ instead of failing'), [
    ('Default tolerance none', 'bad JSON', 'Task FAILED.', 'red'), ('Status API', 'trace in status', 'Diagnose.', 'amber'),
    ('Set tolerance all + DLQ', 'context headers', 'Config change.', 'green'), ('Restart', 'POST …/restart?includeTasks=true', 'Running.', 'green'),
    ('Fix and replay DLQ', 'Lesson 6.2', 'Clean.', 'blue')], ['Fail.', 'Inspect.', 'Tolerate.', 'Restart.', 'Replay.'], 'scenario-failed') + \
       five('Real-time scenario 3 · advanced', 'Re-ingest from the start', 'Reset a source offset. (Typical.)', ('Offsets API', 'KIP-875'), [
    ('Need full re-load', 'file re-generated', 'Request.', 'blue'), ('PUT …/stop', 'connector STOPPED', 'Required.', 'amber'),
    ('DELETE …/offsets', 'or PATCH position 0', 'Reset.', 'green'), ('PUT …/resume', 'reads from 0', 'Reload.', 'green'),
    ('Downstream dedupe', 'keys / upserts', 'Safe.', 'blue')], ['Ask.', 'Stop.', 'Reset.', 'Resume.', 'Dedupe.'], 'scenario-reset')
assemble(HERE, h2_story='Integration without writing code', hook_html=hk,
    narration='TiffinGo’s old kitchen system writes orders to a CSV file, and analytics wants them in Kafka and then in a warehouse. Kabir was about to write custom code.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Kafka Connect',
    formal='<b>Kafka Connect</b> is a framework and runtime for scalable, fault-tolerant data integration between Kafka and other systems. <b>Workers</b> run <b>connectors</b> (source or sink plugins) that are divided into <b>tasks</b>; records pass through <b>converters</b> (serialization) and optional <b>single message transforms</b>. In distributed mode, configuration, source offsets and status are stored in compacted Kafka topics and the cluster is managed via a REST API.',
    simple='Connect is a ready-made engine that copies data into Kafka (source) or out of Kafka (sink). You choose a connector, send a small JSON config, and it handles restarts, checkpoints and scaling for you.',
    term_rows=[('Worker', 'Process running connectors.'), ('Connector', 'Plugin + config.'), ('Task', 'Unit doing the copying.'), ('Source', 'Into Kafka.'), ('Sink', 'Out of Kafka.'), ('Converter', 'Bytes ↔ data.'), ('SMT', 'Per-record transform.'), ('plugin.path', 'Where connector JARs live.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Connect runs inside the broker.', 'It is a separate process/cluster.', 'Container kc.'),
               ('A restart re-reads everything.', 'Source offsets are stored.', 'Step 5: position 53.'),
               ('One bad record must stop the pipeline.', 'errors.tolerance + DLQ.', 'Step 6.')],
    exam='“What is Kafka Connect?” Framework to move data in/out of Kafka with source/sink connectors; workers, connectors, tasks; converters, SMTs; distributed mode with config/offset/status topics; REST API; error tolerance and DLQ.',
    types_h2='Parts and modes', types_html=types_html, warn=warn,
    steps_h2='Source, transform, sink', steps_intro='All outputs are real: Kafka 4.4.0 Connect worker (distributed mode) against the 3-broker lab.',
    steps=steps, two=two, peel_intro='Now peel one appended line.', peel_html=pe,
    scen_intro='Three live scenarios: a worker crash, a failed sink, and an offset reset.', scen=scen,
    uc_h2='Connect at work', ucs=[uc_('db', 'CDC', 'blue', '1. Database → Kafka', 'Debezium, JDBC source.', ['DB', '*source', 'Topic']),
        uc_('lake', 'lake', 'green', '2. Kafka → data lake', 'S3/GCS/HDFS sinks, Parquet.', ['Topic', '*sink', 'S3']),
        uc_('search', 'search', 'violet', '3. Kafka → search', 'Elasticsearch/OpenSearch sink.', ['Topic', '*sink', 'Index']),
        uc_('mm', 'replicate', 'amber', '4. Cluster → cluster', 'MirrorMaker 2 runs on Connect.', ['DC1', '*MM2', 'DC2'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../../06-queues-and-error-handling/02-retry-topics-and-dead-letter-queues/">6.2 DLQs</a>.')
