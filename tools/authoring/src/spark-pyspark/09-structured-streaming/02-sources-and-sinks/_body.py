import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l92_sources.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)

def kparts(x, y, offs, label='orders topic'):
    o = t(x + 80, y - 6, label, 7.2, 'ink2', bold=True)
    for k, n in enumerate(offs):
        o += t(x - 4, y + 12 + k * 18, f'p{k}', 6.8, 'ink2', anchor='end')
        for j in range(n):
            o += box(x + j * 16, y + 4 + k * 18, 13, 13, 'blue', rx=2)
    return o

# ---------------------------------------------------------------- story
sc_ = (kparts(30, 34, [6, 5, 5]) + arrow(140, 62, 176, 62, 'ink3', 1.1) + opbox(180, 46, 'Spark stream', 'parse JSON', 'violet', 96, 32) +
       arrow(278, 62, 300, 40, 'ink3', 1.1) + arrow(278, 62, 300, 84, 'ink3', 1.1) + opbox(302, 24, 'Parquet', 'files', 'green', 70, 28) + opbox(302, 72, 'Kafka', 'big_orders', 'green', 70, 28) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured (local Kafka)', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('600 events, 3 partitions', 'blue'), ('maxOffsets 250: 248+248+104', 'green'),
           ('parquet: 600 rows, 9 files', 'green'), ('foreachBatch → Postgres', 'green'),
           ('Kafka sink: 50 big orders', 'green'), ('value is binary: cast it', 'amber')])))
scene_svg = scene('A streaming query reads from a source such as Kafka or files and writes to one or more sinks. We produced 600 order events to a 3-partition Kafka topic and read them into Parquet files, PostgreSQL via foreachBatch, another Kafka topic and the console.', sc_,
                  'Sources must be <tspan font-weight="700" class="s-acc">replayable</tspan>; sinks should be idempotent.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Orders are in Kafka. Now what?”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s app publishes every order as a JSON event to a Kafka topic. Three teams want it: analytics wants Parquet files in the lake, finance wants city totals in PostgreSQL, and the fraud team wants big orders on a separate topic.</p>

{scene_svg}

K> Sir, Kafka gives us bytes. How does Spark know what an order looks like?
A> The Kafka source always gives the same columns: key, value, topic, partition, offset, timestamp. You cast <code>value</code> to a string and parse the JSON with a schema. The <b>offsets</b> are what Spark stores in the checkpoint to know where it stopped.
R> And one stream can feed three sinks?
A> Each sink is its own streaming query with its own checkpoint. Today we run a real Kafka broker, control batch sizes with <code>maxOffsetsPerTrigger</code>, and write to files, PostgreSQL, Kafka and the console. All outputs are real (PySpark 4.3.0, Kafka 3.9).
  </div>
</section>
'''

lv = '''
LEVELS> Sources and sinks at three levels
L1> A courier hub
      <ul>
        <li>Parcels arrive on numbered conveyor belts (Kafka partitions); each parcel has a sticker number (offset).</li>
        <li>The hub writes down the last sticker number it handled on each belt, so after a power cut it starts from the next one.</li>
        <li>Outgoing vans are sinks: some can safely receive the same parcel twice (idempotent), some cannot.</li>
      </ul>
L2> The API
      <ul>
        <li>Sources: <code>kafka</code>, files (<code>json</code>, <code>csv</code>, <code>parquet</code>, …), <code>rate</code>, <code>socket</code> (testing), Delta/Iceberg tables.</li>
        <li>Sinks: files, <code>kafka</code>, <code>foreachBatch</code>, <code>foreach</code>, <code>console</code> and <code>memory</code> (debugging), tables via <code>toTable</code>.</li>
        <li>Kafka options: <code>kafka.bootstrap.servers</code>, <code>subscribe</code>, <code>startingOffsets</code>, <code>maxOffsetsPerTrigger</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li><code>maxOffsetsPerTrigger=250</code> gave batches of 248, 248 and 104 rows (split across 3 partitions).</li>
        <li>The Parquet sink wrote 600 rows in 9 files; foreachBatch wrote 3 city rows per batch to PostgreSQL.</li>
        <li>The Kafka sink needed only <code>key</code> and <code>value</code> columns; 50 orders ≥ 450 reached <code>big_orders</code>.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Streaming sources and sinks</h2>
''' + def_block(
    'A streaming <b>source</b> provides new data for each micro-batch together with <b>offsets</b> that identify its position. For end-to-end fault tolerance a source must be <b>replayable</b>: given offsets recorded in the checkpoint, it can return exactly the same data again (Kafka, files and table formats are; the socket source is not). A <b>sink</b> receives the result of each micro-batch. The file sink and table sinks are <b>idempotent</b>: they record committed batches in a log, so a replayed batch is not written twice. The Kafka sink is at-least-once. <code>foreachBatch</code> passes each micro-batch as a normal DataFrame with its <code>batch_id</code> to a user function, so any batch writer (JDBC, MERGE, multiple outputs) can be used; exactly-once then depends on making that function idempotent.',
    'A source gives Spark new data and a position (offset) so it can resume; a sink receives each batch’s results. Kafka and files can be replayed, so after a failure Spark re-reads the same data. File sinks ignore duplicate batches. With foreachBatch you can write each batch anywhere using the normal DataFrame writer.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Topic / partition', 'Kafka stream and its ordered shards.'),
    ('Offset', 'Position of a message in a partition.'),
    ('startingOffsets', 'earliest / latest / JSON offsets.'),
    ('maxOffsetsPerTrigger', 'Rate limit per batch.'),
    ('Replayable source', 'Can return the same data again.'),
    ('Idempotent sink', 'Same batch twice = written once.'),
    ('foreachBatch', 'Your function per micro-batch.'),
    ('batch_id', 'Batch number, stable on replay.'),
]) + '''

  <h3>Common sources and sinks</h3>
''' + table(['Kind', 'Name', 'Replay / guarantee', 'Notes'], [
    ['Source', 'Kafka', 'Replayable (offsets)', 'Fixed schema: key, value (binary), topic, partition, offset, timestamp'],
    ['Source', 'Files', 'Replayable (file log)', 'Needs a schema; maxFilesPerTrigger'],
    ['Source', 'rate / socket', 'rate: test; socket: not fault-tolerant', 'Testing only'],
    ['Sink', 'Files / tables', 'Exactly-once (sink log)', 'append mode'],
    ['Sink', 'Kafka', 'At-least-once', 'Needs value (key optional)'],
    ['Sink', 'foreachBatch', 'Depends on your code', 'Any batch writer'],
    ['Sink', 'console / memory', 'Debugging only', 'Data on the driver'],
], minw=660) + lv + '''
EXAM> “How do you read Kafka in Structured Streaming?” <code>spark.readStream.format("kafka").option("kafka.bootstrap.servers", …).option("subscribe", topic).load()</code>, then <code>CAST(value AS STRING)</code> and <code>from_json</code> with a schema. Control batch size with <code>maxOffsetsPerTrigger</code> and the first position with <code>startingOffsets</code>; offsets are stored in the checkpoint so restarts resume exactly. For sinks without native support, use <code>foreachBatch</code> and make it idempotent.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Kafka source options</h2>
''' + table(['Option', 'Example', 'Meaning'], [
    ['<code>subscribe</code>', '"orders"', 'Topics (or subscribePattern / assign)'],
    ['<code>startingOffsets</code>', '"earliest" / "latest"', 'Only for a new checkpoint; later the checkpoint wins'],
    ['<code>maxOffsetsPerTrigger</code>', '250', 'Max messages per batch (rate limit)'],
    ['<code>failOnDataLoss</code>', 'true', 'Fail if offsets were deleted by retention'],
    ['<code>kafka.*</code>', 'kafka.security.protocol', 'Passed to the Kafka consumer'],
], minw=600) + '''
WARN> <code>startingOffsets</code> is read only when the checkpoint is <b>new</b>. Changing it to <code>"earliest"</code> on a running query to “reprocess everything” does nothing; you need a new checkpoint location. Also, Kafka support is not bundled with PySpark: add the <code>spark-sql-kafka-0-10</code> package (and its dependencies) with <code>--packages</code> or <code>--jars</code>, or you get <code>KAFKA_DATA_SOURCE_NOT_ENABLED</code>.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Kafka in, four sinks out</h2>
  <p>All outputs are real: PySpark 4.3.0, <code>local[2]</code>, Apache Kafka 3.9 in Docker with a 3-partition topic <code>orders</code>, PostgreSQL 16 for the JDBC sink. Each sink is a separate query with its own checkpoint, run with <code>availableNow</code> so it stops when the topic is drained.</p>
''' + stepper([
    ('Step 1 · Produce and look at the Kafka schema',
     code('python', 'l92_sources.py', 'ev.write.format("kafka").option("kafka.bootstrap.servers", K).option("topic", "orders").save()   # 600 JSON events\nraw = (spark.readStream.format("kafka").option("kafka.bootstrap.servers", K).option("subscribe", "orders")\n         .option("startingOffsets", "earliest").option("maxOffsetsPerTrigger", 250).load())\nraw.printSchema()', sec('== 1)', '== 3)')),
     'Whatever the messages contain, the Kafka source has the same 7 columns. <code>key</code> and <code>value</code> are <b>binary</b>; the rest describe where the message came from. We parse it with <code>F.from_json(F.col("value").cast("string"), "order_id long, city string, amount long")</code>.'),
    ('Step 2 · File sink with a rate limit',
     code('python', 'l92_sources.py', 'q = (orders.writeStream.format("parquet").option("path", D + "/out92")\n        .option("checkpointLocation", D + "/ck92/files").trigger(availableNow=True).start())', sec('== 3)', '== 4)')),
     'With <code>maxOffsetsPerTrigger=250</code> the 600 messages were split into <b>3 batches</b> (248, 248, 104; the limit is divided across partitions). The <code>endOffset</code> per partition is what goes into the checkpoint. The Parquet sink wrote 600 rows in 9 files (3 batches × 3 partitions) and keeps a <code>_spark_metadata</code> log so readers see only committed files.'),
    ('Step 3 · foreachBatch to PostgreSQL',
     code('python', 'l92_sources.py', 'def to_pg(df, batch_id):\n    out = df.groupBy("city").agg(F.count("*").alias("orders"), F.sum("amount").alias("revenue")) \\\n            .withColumn("batch_id", F.lit(batch_id))\n    out.write.jdbc(url, "city_rev_stream", mode="append", properties=props)\nq2 = orders.writeStream.foreachBatch(to_pg).option("checkpointLocation", …).trigger(availableNow=True).start()', sec('== 4)', '== 5)')),
     'Inside <code>foreachBatch</code>, <code>df</code> is a <b>normal DataFrame</b>: you can aggregate it and use the batch JDBC writer, which has no streaming version. Each batch wrote 3 city rows tagged with its <code>batch_id</code>; summing them gives 200 orders per city. Because this is a plain append, a replayed batch would be written twice: Lesson 9.5 shows the crash and the fix.'),
    ('Step 4 · Kafka sink and the console',
     code('python', 'l92_sources.py', 'big = orders.filter("amount >= 450").select(F.col("order_id").cast("string").alias("key"),\n                                            F.to_json(F.struct("order_id", "city", "amount")).alias("value"))\nbig.writeStream.format("kafka").option("kafka.bootstrap.servers", K).option("topic", "big_orders") \\\n   .option("checkpointLocation", …).trigger(availableNow=True).start()', sec('== 5)', '== 6)') + '\n' + sec('== 6)', '-------------------------------------------\nBatch: 1')),
     'The Kafka sink expects a <code>value</code> column (string or binary) and optionally <code>key</code>; we serialised the row back to JSON. 50 big orders reached <code>big_orders</code>, readable as a batch. The <b>console</b> sink prints each batch; handy while developing, useless in production.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('key: binary   value: binary', Y), ('topic partition offset', W), ('timestamp timestampType', W)], size=7.4),
    term([('batch 0: 248 rows', G), ('batch 1: 248 rows', G), ('batch 2: 104 rows', G), ('parquet: 600 rows, 9 files', G)], size=7.4),
    term([('batch_id=0: 248 -> 3 city rows', G), ('batch_id=1: 248 -> 3 city rows', G), ('Delhi 200 | Mumbai 200 | Pune 200', W)], size=7.2),
    term([('messages in big_orders: 50', G), ('{"order_id":450,...}', W)], size=7.4),
]
B1 = [
    t(180, 14, 'Kafka: partitions + offsets', 9.4, bold=True) + kparts(60, 40, [6, 5, 5], '') + t(240, 66, 'cast(value) → from_json', 7.4, 'violet') + cap('Bytes in, schema applied by you.', '', 'blue', y=144, h=30),
    t(180, 14, 'Rate limit per batch', 9.4, bold=True) + flow([('250', 'max offsets', 'violet'), ('split', 'per partition', 'blue'), ('batch', '248 rows', 'green')], y=50, w=96, gap=16) + cap('End offsets saved per batch.', '', 'green', y=144, h=30),
    t(180, 14, 'foreachBatch', 9.4, bold=True) + flow([('micro-batch', 'DataFrame', 'blue'), ('your code', 'groupBy', 'violet'), ('JDBC', 'append', 'green')], y=50, w=96, gap=16) + cap('Any batch writer.', '', 'green', y=144, h=30),
    t(180, 14, 'One query per sink', 9.4, bold=True) + opbox(20, 50, 'orders stream', '', 'blue', 100, 28) + ''.join(arrow(122, 64, 196, 34 + k * 30, 'ink3', 1) + opbox(200, 22 + k * 30, n, '', 'green', 130, 24) for k, n in enumerate(['parquet + ckpt A', 'postgres + ckpt B', 'kafka + ckpt C'])) + cap('Separate checkpoints.', '', 'amber', y=144, h=30),
]
see_caps = ['Kafka schema.', 'Rate-limited batches.', 'foreachBatch to Postgres.', 'Kafka sink.']
behind_caps = ['Parsing Kafka values.', 'maxOffsetsPerTrigger.', 'Batch writers in streams.', 'Fan-out to sinks.']
two = anim_two('Sources and sinks', 'From Kafka to four places', 'Real lab outputs', 'What Spark does', see, B1, see_caps, behind_caps)

e1 = (t(180, 22, 'App → Kafka “orders”', 9.4, bold=True) + t(180, 56, 'JSON events, 12 partitions', 8.4, 'ink2') + cap('The single source of truth.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Stream → lake (Parquet/Delta)', 9.4, bold=True) + t(180, 56, 'append, checkpoint A', 8.4, 'ink2') + cap('Exactly-once file sink.', '', 'green', y=150, h=34))
e3 = (t(180, 22, 'Stream → Postgres totals', 9.4, bold=True) + t(180, 56, 'foreachBatch, checkpoint B', 8.4, 'ink2') + cap('Make it idempotent (9.5).', '', 'amber', y=150, h=34))
e4 = (t(180, 22, 'Stream → Kafka “big_orders”', 9.4, bold=True) + t(180, 56, 'fraud team consumes it', 8.4, 'ink2') + cap('At-least-once.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Each sink independent', 9.4, 'acc', bold=True) + t(180, 56, 'restart one, others keep going', 8.4, 'ink2') + cap('Separate checkpoints.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'One topic, three teams',
              'Fan-out from Kafka. (Typical; pattern from our lab.)',
              'Fan-out', 'One Kafka topic feeds several streaming queries, each with its own sink and checkpoint', [e1, e2, e3, e4, e5],
              ['Topic.', 'Lake.', 'Postgres.', 'Kafka.', 'Independent.'],
              hid='scenario-fanout')
b1 = (t(180, 22, 'Stream down for 6 hours', 9.4, bold=True) + t(180, 56, '20 million messages waiting', 8.4, 'ink2') + cap('Restart.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'First batch: all 20 million', 9.4, bold=True) + t(180, 56, 'executor OOM, restart loop', 8.4, 'ink2') + cap('No rate limit.', '', 'red', y=150, h=34))
b3 = (t(180, 22, 'maxOffsetsPerTrigger=2M', 9.4, bold=True) + t(180, 56, 'catch up in 10 batches', 8.4, 'ink2') + cap('248 per 250 in our lab.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Lag shrinks steadily', 9.4, bold=True) + t(180, 56, 'watch offsets behind latest', 8.4, 'ink2') + cap('Predictable.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Keep the limit', 9.4, 'acc', bold=True) + t(180, 56, 'protects every restart', 8.4, 'ink2') + cap('Bounded batches.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Catching up after an outage',
              'Rate limiting Kafka reads. (Typical; behaviour from our lab.)',
              'Rate limit', 'maxOffsetsPerTrigger keeps catch-up batches small enough to succeed', [b1, b2, b3, b4, b5],
              ['Outage.', 'Huge batch.', 'Limit.', 'Catch up.', 'Keep it.'],
              hid='scenario-ratelimit')
u1 = (t(180, 22, '“Reprocess from the start”', 9.4, bold=True) + t(180, 56, 'set startingOffsets=earliest', 8.4, 'ink2') + cap('Restart the query.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Nothing reprocessed', 9.4, bold=True) + t(180, 56, 'checkpoint offsets win', 8.4, 'ink2') + cap('Option ignored.', '', 'red', y=150, h=34))
u3 = (t(180, 22, 'New checkpoint location', 9.4, bold=True) + t(180, 56, 'ck/orders_v2', 8.4, 'ink', mono=True) + cap('Now earliest applies.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Clean or version the sink', 9.4, bold=True) + t(180, 56, 'avoid duplicates in output', 8.4, 'ink2') + cap('New path or overwrite.', '', 'amber', y=150, h=34))
u5 = (t(180, 22, 'Check retention', 9.4, 'acc', bold=True) + t(180, 56, 'old offsets may be deleted', 8.4, 'ink2') + cap('failOnDataLoss.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'The option that did nothing',
              'startingOffsets vs the checkpoint. (Typical.)',
              'Reprocessing', 'startingOffsets applies only to a new checkpoint; reprocessing needs a new checkpoint and sink path', [u1, u2, u3, u4, u5],
              ['Earliest.', 'Ignored.', 'New ckpt.', 'Sink.', 'Retention.'],
              hid='scenario-reprocess')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>From Kafka to four places</h2>
  <p>Left: real outputs. Right: how sources and sinks work.</p>
''' + two + '''
  <p>Three live scenarios follow: one topic for three teams, catching up after an outage, and reprocessing.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Sources and sinks at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'Kafka', 12, 'blue', bold=True) + t(60, 58, '→ lake', 7.4, 'ink2'),
    '1. Event ingestion',
    'App events flow from Kafka into partitioned lake tables every minute.',
    ['Kafka', '*parse JSON', 'Lake table']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'CDC', 12, 'green', bold=True) + t(60, 58, 'Debezium', 7.4, 'ink2'),
    '2. Change data capture',
    'Database changes from Debezium topics are merged into lake tables with foreachBatch + MERGE.',
    ['CDC topic', '*foreachBatch MERGE', 'Current table']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'files', 12, 'violet', bold=True) + t(60, 58, 'landing', 7.4, 'ink2'),
    '3. File drops',
    'Partner CSVs landing in object storage are picked up by a file stream.',
    ['Landing folder', '*file source', 'Clean table']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'topic', 12, 'acc', bold=True) + t(60, 58, '→ topic', 7.4, 'ink2'),
    '4. Stream enrichment',
    'Raw events are enriched and filtered into new topics for other services.',
    ['Raw topic', '*enrich', 'Clean topic']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'serve', 12, 'acc', bold=True) + t(60, 58, 'DB', 7.4, 'ink2'),
    '5. Serving tables',
    'Aggregates are upserted into PostgreSQL or Redis for APIs.',
    ['Stream', '*foreachBatch upsert', 'API']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> streaming basics in <a href="../01-streaming-concepts/">9.1</a>, JSON and schemas in <a href="../../05-reading-and-writing-data/01-csv-and-json/">5.1</a>, JDBC in <a href="../../05-reading-and-writing-data/04-jdbc-xml-and-other-sources/">5.4</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
