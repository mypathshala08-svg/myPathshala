import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l94_spark.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
S = '../../../spark-pyspark/09-structured-streaming/'
hk = hook('Your data team writes Python, not Java. Can they still do windowed, exactly-once stream processing on Kafka?',
    'Yes, with an <b>engine</b> instead of a library: <b>Spark Structured Streaming</b> or <b>Apache Flink</b>. In our lab, 15 lines of PySpark (Spark 4.3) read a Kafka topic as a streaming DataFrame, computed 5-minute revenue per city with a <b>watermark</b>, dropped one record that was too late, and stored its Kafka offsets in a <b>checkpoint</b>, not in a consumer group.',
    ['How Spark reads Kafka: the DataFrame schema, offsets and checkpoints.',
     'Watermarks vs Kafka Streams grace.',
     'Kafka Streams vs Spark vs Flink vs ksqlDB: when to pick which.'])
cmap = concept_map('Concept map. Beginner: engine vs library, DataFrame from Kafka. Intermediate: micro-batch, watermark, output modes, checkpoint. Advanced: exactly-once sinks, Flink state and checkpoints, choosing an engine, connecting to the lakehouse.',
    [[('ks', 'Kafka Streams', 'Lesson 9.1', B + '09-stream-processing/01-kafka-streams/'), ('wj', 'Windows + grace', 'Lesson 9.3', B + '09-stream-processing/03-windows-and-joins/')],
     [('sp', 'Spark readStream', 'kafka source', S + '02-sources-and-sinks/'), ('mb', 'Micro-batches', 'trigger', None), ('wm', 'Watermark', 'late limit', S + '03-output-modes-event-time-and-watermarks/'), ('ck', 'Checkpoint', 'offsets + state', S + '05-checkpoints-exactly-once-and-state/')],
     [('fl', 'Apache Flink', 'true streaming', None), ('sq', 'Flink SQL / ksqlDB', 'SQL on streams', None), ('ch', 'Choosing an engine', 'trade-offs', None), ('lh', 'Lakehouse sinks', 'Delta / Iceberg', None)]],
    [('ks', 'sp'), ('wj', 'wm'), ('sp', 'mb'), ('mb', 'wm'), ('mb', 'ck'), ('sp', 'fl'), ('fl', 'sq'), ('fl', 'ch'), ('ck', 'lh')],
    {'sp', 'mb', 'wm', 'ck', 'fl', 'sq', 'ch'},
    '<b>Builds on:</b> <a href="../03-windows-and-joins/">9.3</a> and the Spark course <a href="' + S + '01-streaming-concepts/">Module 9</a>. <b>Next:</b> Module 10 Kafka in production.')
whw = why_how_where(
    'Kafka Streams is Java-only and Kafka-to-Kafka. Data teams need Python/SQL, joins with files and databases, and writes to lakes and warehouses, at very large scale.',
    'Spark treats the topic as an unbounded table: each micro-batch reads new offset ranges per partition, runs the query incrementally with state, and records progress in a checkpoint. Flink runs continuous operators with distributed snapshots (checkpoints) for exactly-once state.',
    'Streaming ETL into Delta/Iceberg lakehouses, ML feature pipelines, large joins, real-time analytics; Flink for low-latency event processing and Flink SQL; managed services (Databricks, Confluent Cloud for Flink, AWS Managed Flink).',
    'A cluster to run and tune. Spark adds micro-batch latency (seconds); Flink is lower latency but more operational depth. Offsets live in checkpoints, so standard lag tools see no consumer group unless you add monitoring.')

def eng(hl=-1):
    parts = [('Kafka topic', 'blue'), ('readStream', 'violet'), ('window', 'amber'), ('sink', 'green')]
    o = ''
    for k, (n, tn) in enumerate(parts):
        o += box(8 + k * 88, 50, 78, 40, 'acc' if k == hl else tn, rx=6) + t(47 + k * 88, 74, n, 7.6, bold=True)
        if k < 3: o += arrow(88 + k * 88, 70, 94 + k * 88, 70)
    o += t(223, 104, 'watermark', 7.2) + box(96, 104, 78, 18, 'card', rx=4) + t(135, 117, 'checkpoint', 7.2, bold=True)
    return o + t(176, 30, 'Spark micro-batch every 3 s', 7.6)
scene_svg = scene('A Spark Structured Streaming pipeline: a Kafka topic is read by readStream, aggregated in windows with a watermark, and written to a sink; offsets and state are kept in a checkpoint.', eng(),
                  'An engine reads Kafka in <tspan font-weight="700" class="s-acc">micro-batches</tspan> and remembers offsets in a checkpoint.')
dialogue = '''K> Sir, analytics wants live revenue per city every 5 minutes, written to the lakehouse. They only know PySpark.
A> Then don’t force Kafka Streams on them. <b>Spark Structured Streaming</b> reads Kafka directly, in Python, with windows and watermarks.
R> Where does it keep its Kafka offsets? I don’t see a consumer group.
A> In its <b>checkpoint</b> folder. Let’s run it and open the folder.'''

lv = '''
LEVELS> Engines at three levels
L1> Factory vs workshop tool
      <ul>
        <li>Kafka Streams is a power tool you carry into your own workshop (your app). Spark and Flink are factories: you send them the job, they bring many machines, and they connect to many kinds of input and output.</li>
      </ul>
L2> Spark + Kafka
      <ul>
        <li><code>spark.readStream.format("kafka")</code> with <code>kafka.bootstrap.servers</code>, <code>subscribe</code>, <code>startingOffsets</code>. Columns: key, value (binary), topic, partition, offset, timestamp, timestampType. Parse value with <code>from_json</code> (or <code>from_avro</code> with the registry).</li>
        <li><code>withWatermark("ts", "1 minute")</code> = max event time seen − 1 min; windows older than that are finalized and late rows dropped (same idea as grace in 9.3).</li>
        <li>Output modes: append (final rows only), update (changed rows), complete (whole table). Package: <code>spark-sql-kafka-0-10</code> (+ kafka-clients, commons-pool2).</li>
      </ul>
L3> Guarantees and choices
      <ul>
        <li>Spark: offsets per batch are written to <code>checkpoint/offsets</code> before processing and <code>commits</code> after; with idempotent or transactional sinks (Delta, foreachBatch upserts) you get exactly-once end to end. The Kafka sink itself is at-least-once.</li>
        <li>Flink: <code>KafkaSource</code>/<code>KafkaSink</code>, event-time watermarks, keyed state, checkpoint barriers; exactly-once Kafka sink via transactions. Flink SQL: <code>CREATE TABLE … WITH ('connector'='kafka')</code>.</li>
        <li>ksqlDB: SQL server built on Kafka Streams (Confluent Community License). Choose by language, latency, sources/sinks and who operates it.</li>
      </ul>
/LEVELS
'''
CK = figure('The Spark checkpoint folder: commits, metadata, offsets, sources and state; the latest offsets file records topic orders-94 partition 0 at offset 6 and partition 1 at offset 1.',
    t(16, 22, 'Inside /tmp/chk94 (real listing)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('offsets/', 'amber', 1), ('commits/', 'green', 2), ('state/', 'violet', 3), ('sources/', 'blue', 4), ('metadata', 'card', 5)]) +
    legend(16, 84, [(1, 'offsets', 'planned Kafka offsets per batch: {"orders-94":{"0":6,"1":1}}'), (2, 'commits', 'batch finished: safe to move on'),
                    (3, 'state', 'window aggregates (revenue per city)'), (4, 'sources', 'initial offsets of the source'), (5, 'metadata', 'query id')], size=8, gap=15, w=90),
    h=172, caption='Delete it and the query starts over from startingOffsets.')
extra = '''

  <h3>Dissect the checkpoint</h3>
''' + CK

types_html = table(['', 'Kafka Streams', 'Spark Structured Streaming', 'Apache Flink', 'ksqlDB'], [
    ['Form', 'Java library', 'cluster engine', 'cluster engine', 'SQL server'], ['Languages', 'Java/Scala', 'Python, SQL, Scala, Java', 'Java, SQL, Python', 'SQL'],
    ['Model', 'record at a time', 'micro-batch (+ real-time mode)', 'record at a time', 'record at a time'], ['Latency', 'ms', 'sub-second to seconds', 'ms', 'ms'],
    ['Sources/sinks', 'Kafka only', 'many (lake, DB, files)', 'many', 'Kafka'], ['State', 'RocksDB + changelog', 'state store + checkpoint', 'RocksDB + snapshots', 'Kafka Streams'],
    ['Offsets', 'consumer group', 'checkpoint', 'checkpoint (+ optional commit)', 'consumer group'],
], minw=720)
warn = 'Never reuse one checkpoint folder for a changed query or another topic, and never delete it casually: it is the only record of which Kafka offsets were processed. Also, Spark does not commit offsets to Kafka, so consumer-group lag tools show nothing; monitor lastProgress or use a lag exporter that reads the checkpoint.'

steps = [
    ('Step 1 · Kafka as a DataFrame',
     code('python', 'l94.py', 'raw = (spark.readStream.format("kafka")\n       .option("kafka.bootstrap.servers", "k1:9092,k2:9092,k3:9092")\n       .option("subscribe", "orders-94").option("startingOffsets", "earliest").load())\nraw.printSchema()', sec('== 1)', '== 2)')),
     'Every Kafka record becomes a row with binary key and value plus topic, partition, offset and timestamp.'),
    ('Step 2 · Windowed revenue',
     code('python', 'l94.py', 'orders = raw.select(F.from_json(F.col("value").cast("string"), schema).alias("o")).select("o.*")\nagg = (orders.withWatermark("ts", "1 minute")\n       .groupBy(F.window("ts", "5 minutes"), "city")\n       .agg(F.count("*").alias("orders"), F.sum("amount").alias("revenue")))', sec('== 2)', '== 3)')),
     'Five orders, two 5-minute windows. Mumbai 12:00–12:05: idli 80 + thali 150 = 230.'),
    ('Step 3 · A late record',
     code('python', 'l94.py', 'write to orders-94: chai at 12:03 and poha at 12:08', sec('== 3)', '== 4)')),
     'The watermark was 12:07:30 − 1 min = 12:06:30, so window 12:00–12:05 was already closed: chai (12:03) was dropped (1 row). Poha updated Pune 12:05 to 2 orders, 75. The memory sink in update mode appends each update, which is why Pune 12:05 appears twice.'),
    ('Step 4 · Progress',
     code('python', 'l94.py', 'p = query.lastProgress\nprint(p["batchId"], p["numInputRows"], p["eventTime"]["watermark"], p["sources"][0]["endOffset"])', sec('== 4)', '== 5)')),
     'Batch 3, watermark now 12:07 (12:08 − 1 min), end offsets 6 and 1 per partition.'),
    ('Step 5 · The checkpoint',
     code('python', 'l94.py', 'os.listdir("/tmp/chk94"); open("/tmp/chk94/offsets/3").read()', sec('== 5)')),
     'The offsets live here, not in a Kafka consumer group: restart with the same checkpoint and the query continues exactly where it stopped.'),
]
see = [term([('key/value: binary', W), ('topic partition offset', W), ('timestamp', W)], size=7.0), term([('12:00 Mumbai 2 230', G), ('12:05 Pune 1 45', G)], size=7.0),
       term([('chai 12:03 dropped', RD), ('Pune 12:05 → 2, 75', G)], size=7.0), term([('batchId 3', W), ('watermark 12:07', Y), ('{"0":6,"1":1}', W)], size=7.0),
       term([('offsets commits state', W), ('{"orders-94":{"0":6,"1":1}}', G)], size=6.8)]
B1 = [eng(1), eng(2), eng(2), eng(1), eng(-1)]
B1 = [b + cap(c, '', tn, y=130, h=30) for b, c, tn in zip(B1, ['Topic as a table', 'Window + watermark', 'Late row dropped', 'Batch progress', 'Offsets in checkpoint'], ['violet', 'amber', 'red', 'blue', 'green'])]
two = anim_two('Kafka + Spark', 'Read, window, watermark, checkpoint', 'Real outputs from the lab', 'Inside the engine', see, B1, ['Read.', 'Window.', 'Late.', 'Progress.', 'Checkpoint.'], ['Rows.', 'Revenue.', 'Drop.', 'Batch.', 'Offsets.'])
pe = peel('One micro-batch, layer by layer', 'Batch with chai and poha. (Simplified.)',
    [('Plan', ''), ('Fetch', ''), ('Parse', ''), ('Aggregate', ''), ('Sink', ''), ('Commit', '')],
    [['Plan', 'latest offsets 0:6, 1:1', 'write offsets/N', ''], ['Fetch', 'executors read', 'offset ranges', 'per partition'], ['Parse', 'from_json', 'ts, city, amount', ''],
     ['Aggregate', 'state store', 'chai < watermark → drop', 'poha → Pune 12:05'], ['Sink', 'update mode', 'changed rows', ''], ['Commit', 'commits/N', 'watermark → 12:07', '']],
    ['Plan.', 'Read.', 'Parse.', 'Window.', 'Write.', 'Commit.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Python team, live revenue', 'Analytics owns the job. (Typical.)', ('Spark Structured Streaming', 'PySpark on Kafka'), [
    ('Need 5-min revenue', 'Python skills', 'Requirement.', 'blue'), ('readStream kafka', 'from_json', 'Read.', 'green'),
    ('window + watermark', '1-min lateness', 'Aggregate.', 'green'), ('Write to Delta', 'checkpoint', 'Exactly-once table.', 'green'),
    ('BI reads Delta', 'minutes fresh', 'Done.', 'blue')], ['Need.', 'Read.', 'Window.', 'Write.', 'Report.'], 'scenario-spark') + \
       five('Real-time scenario 2', 'Millisecond fraud check', 'Payments must be scored instantly. (Typical.)', ('Flink or Kafka Streams', 'Record-at-a-time'), [
    ('Micro-batch 3 s', 'too slow for approval', 'Latency.', 'red'), ('Flink job', 'keyed state per card', 'Low latency.', 'green'),
    ('Checkpoints', 'exactly-once state', 'Safe.', 'green'), ('Kafka sink transactional', 'decisions topic', 'Output.', 'green'),
    ('Or Kafka Streams', 'if Java service', 'Alternative.', 'blue')], ['Slow.', 'Flink.', 'Snapshot.', 'Emit.', 'Choose.'], 'scenario-flink') + \
       five('Real-time scenario 3 · advanced', 'Changed query, old checkpoint', 'Restart fails. (Typical.)', ('Checkpoint compatibility', 'State schema is tied to the query'), [
    ('Add a column to groupBy', 'redeploy', 'Change.', 'blue'), ('Restart with old checkpoint', 'state mismatch error', 'Fail.', 'red'),
    ('New checkpoint path', 'set startingOffsets', 'Fresh state.', 'green'), ('Backfill if needed', 'batch job on topic', 'Fill gap.', 'amber'),
    ('Version checkpoints', 'per query version', 'Practice.', 'blue')], ['Change.', 'Fail.', 'New path.', 'Backfill.', 'Version.'], 'scenario-chk')
assemble(HERE, h2_story='Stream processing for Python and SQL teams', hook_html=hk,
    narration='TiffinGo’s analytics team wants live 5-minute revenue per city in the lakehouse. They write PySpark, not Java.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Kafka with Spark and Flink',
    formal='<b>Spark Structured Streaming</b> and <b>Apache Flink</b> are distributed stream-processing engines with Kafka connectors. Spark models a Kafka topic as an unbounded table processed in micro-batches, tracking source offsets and operator state in a <b>checkpoint</b> and handling late data with <b>watermarks</b>. Flink processes records continuously with keyed state and consistent distributed snapshots. Both can provide exactly-once results with suitable sinks.',
    simple='Instead of putting stream logic inside a Java app, you can hand it to an engine like Spark or Flink. Spark reads Kafka every few seconds like a growing table, in Python or SQL, and remembers where it stopped in a checkpoint folder.',
    term_rows=[('Engine', 'Cluster that runs jobs.'), ('readStream', 'Spark streaming source.'), ('Micro-batch', 'Small batch every trigger.'), ('Watermark', 'Max event time − delay.'), ('Output mode', 'append/update/complete.'), ('Checkpoint', 'Offsets + state folder.'), ('Flink', 'Record-at-a-time engine.'), ('ksqlDB', 'SQL on Kafka Streams.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Spark commits offsets to a consumer group.', 'It stores them in the checkpoint.', 'Step 5.'),
               ('Late data always counts.', 'Behind the watermark it is dropped.', 'Step 3.'),
               ('One engine is best for everything.', 'Choose by language, latency, sinks.', 'Table.')],
    exam='“Kafka Streams vs Spark vs Flink?” Library vs engines; Spark micro-batch, watermark, checkpoint offsets, Python/SQL, lake sinks; Flink low-latency, snapshots, Flink SQL; Kafka Streams for Java services Kafka-to-Kafka; ksqlDB SQL.',
    types_h2='Choosing a stream processor', types_html=types_html, warn=warn,
    steps_h2='PySpark on Kafka', steps_intro='All outputs are real: Spark 4.3.0 (PySpark, local[2]) with spark-sql-kafka-0-10 4.3.0 against the 3-broker Kafka 4.4 lab. Flink is described, not run in our lab.',
    steps=steps, two=two, peel_intro='Now peel one micro-batch.', peel_html=pe,
    scen_intro='Three live scenarios: a Python team, millisecond fraud, and a changed query.', scen=scen,
    uc_h2='Engines at work', ucs=[uc_('etl', 'ETL', 'blue', '1. Streaming ETL', 'Kafka → Delta/Iceberg.', ['Topic', '*Spark', 'Lakehouse']),
        uc_('feat', 'ML', 'violet', '2. ML features', 'Rolling aggregates for models.', ['Events', '*window', 'Feature store']),
        uc_('fraud', 'fraud', 'red', '3. Low-latency detection', 'Flink keyed state.', ['Payments', '*Flink', 'Decisions']),
        uc_('sql', 'SQL', 'green', '4. SQL on streams', 'Flink SQL / ksqlDB.', ['Topic', '*SQL', 'Topic'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../03-windows-and-joins/">9.3 Windows</a>.')
