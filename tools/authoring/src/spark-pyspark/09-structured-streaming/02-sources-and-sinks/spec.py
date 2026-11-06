import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='09-structured-streaming', lesson='02-sources-and-sinks', n='9.2',
    module_label='Module 9 · Structured Streaming',
    title='Sources and sinks',
    desc='Structured Streaming sources and sinks with PySpark 4.3.0 and a real Kafka 3.9 broker: the fixed Kafka schema (binary key and value), parsing JSON with from_json, maxOffsetsPerTrigger splitting 600 events into batches of 248, 248 and 104, a Parquet file sink, foreachBatch writing city totals to PostgreSQL, a Kafka sink, the console sink, and why startingOffsets is ignored on an existing checkpoint.',
    og_desc='Kafka in, Parquet, PostgreSQL, Kafka and console out: Spark Structured Streaming sources and sinks with a real broker.',
    minutes=30, level='Intermediate',
    lead='Every streaming query reads from a source and writes to a sink. This lesson reads a real <b>Kafka</b> topic, parses its binary values, rate-limits batches with <code>maxOffsetsPerTrigger</code>, and writes to Parquet, PostgreSQL via <code>foreachBatch</code>, another Kafka topic and the console. <b>All outputs are real</b> (PySpark 4.3.0, Kafka 3.9).',
    chips=['PySpark 4.3.0', 'Real Kafka broker', 'foreachBatch → Postgres', 'Runs in your browser (Python)'],
)

MAIN = '''# Parsing Kafka messages (what from_json does for each row)
import json
messages = [
    (0, 0, b'{"order_id": 300, "city": "Mumbai", "amount": 300}'),
    (0, 1, b'{"order_id": 301, "city": "Pune", "amount": 301}'),
    (1, 0, b'{"order_id": 1, "city": "Pune", "amount": 1}'),
]
for partition, offset, value in messages:
    o = json.loads(value.decode("utf-8"))        # CAST(value AS STRING) + from_json
    print(partition, offset, o["order_id"], o["city"], o["amount"])

last = {}
for p, off, _ in messages:
    last[p] = off + 1                            # next offset to read, per partition
print("offsets to store in the checkpoint:", last)
'''
RUN = dict(
    heading='Run the code: Kafka messages and offsets',
    intro='<p>What Spark does with each Kafka message and offset. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    o = json.loads(value.decode("utf-8"))        # CAST(value AS STRING) + from_json', 'Kafka values are bytes; you decide how to decode and parse them.'),
        ('    last[p] = off + 1                            # next offset to read, per partition', 'Offsets are tracked per partition; this is what makes Kafka replayable.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then add a message on partition 2.', code=None),
        dict(label='2 · Predict first: batches', hint='<b>Predict first:</b> 600 messages with maxOffsetsPerTrigger=250.',
             code='''import math
print(math.ceil(600 / 250), "batches (lab: 248, 248, 104)")
'''),
        dict(label='3 · Bad JSON', hint='from_json returns null for bad records.',
             code='''import json
for v in [b'{"order_id": 1}', b'not json']:
    try:
        print(json.loads(v))
    except ValueError:
        print(None)
'''),
        dict(label='4 · Kafka sink row', hint='Build the key/value pair the Kafka sink needs.',
             code='''import json
row = {"order_id": 450, "city": "Mumbai", "amount": 450}
print(str(row["order_id"]), json.dumps(row))
'''),
        dict(label='5 · Spot the error', hint='Changing startingOffsets on an existing checkpoint.', expect='error',
             code='''checkpoint_exists, starting = True, "earliest"
assert not checkpoint_exists, "startingOffsets is ignored: the checkpoint offsets win; use a new checkpoint to reprocess"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: Kafka streams',
    intro='<p>Start PySpark with the Kafka package, e.g. <code>pyspark --packages org.apache.spark:spark-sql-kafka-0-10_2.13:4.3.0</code>. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Topic', cmd='/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic orders --partitions 3', file='bash',
             output='Created topic orders.', note='Kafka in Docker: apache/kafka.'),
        dict(title='2 · Without the package', cmd='spark.read.format("kafka").load()', file='pyspark',
             output='[KAFKA_DATA_SOURCE_NOT_ENABLED] Failed to find data source: kafka.', note='Add the connector.'),
        dict(title='3 · Read back', cmd='spark.read.format("kafka").option("kafka.bootstrap.servers", "localhost:9092").option("subscribe", "big_orders").load().count()', file='pyspark',
             output='50', note='Batch read of a topic.'),
    ],
)

TRACE = dict(
    heading='Splitting a rate limit across partitions',
    intro='<p>How 250 messages per batch are shared by 3 partitions.</p>',
    code='''limit = 250
lag = {"p0": 229, "p1": 177, "p2": 194}
total = sum(lag.values())
take = {}
for p, n in lag.items():
    take[p] = int(limit * n / total)
print(take, sum(take.values()))
''',
    notes={2: 'Lag :: Messages waiting per partition.', 6: 'Proportional :: Rounding gives 248, not 250.'},
)

WORKED_INTRO = 'Three source/sink decisions at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='Kafka · parse', title='Parse order events',
         problem='<p>Turn Kafka values into columns.</p>',
         inp='value: binary JSON',
         approach=['CAST(value AS STRING).', 'from_json with a schema.', 'Select the struct fields.'],
         code='''expr = 'from_json(CAST(value AS STRING), "order_id long, city string, amount long")'
print(expr)
''', notes={1: 'Schema :: Explicit, so batches stay consistent.'},
         tryit='Step 1.'),
    dict(level='i', tag='Sinks · choose', title='Which sink?',
         problem='<p>Finance needs city totals in PostgreSQL.</p>',
         inp='no JDBC streaming sink',
         approach=['Use foreachBatch.', 'Batch JDBC writer inside.', 'Make it idempotent with batch_id.'],
         code='''sinks = {"lake": "parquet/delta", "finance db": "foreachBatch + JDBC", "fraud": "kafka"}
print(sinks)
''', notes={1: 'One query per sink :: Own checkpoint each.'},
         tryit='Step 3.'),
    dict(level='a', tag='Kafka · restart', title='Reprocess a topic',
         problem='<p>A bug corrupted output; reprocess the last 7 days.</p>',
         inp='topic retention 14 days',
         approach=['New checkpoint path.', 'startingOffsets by timestamp or earliest.', 'Write to a new output path, then swap.'],
         code='''retention, need = 14, 7
print("possible" if need <= retention else "data already deleted")
''', notes={2: 'startingOffsetsByTimestamp :: Start from a time.'},
         tryit='Scenario 3.'),
]

QUIZ = mix([
    dict(q='Beginner: Kafka value column type?', options=['string', 'binary', 'struct', 'map'], answer=1,
         why='Cast it.'),
    dict(q='Beginner: Function to parse JSON strings?', options=['to_json', 'from_json', 'json_tuple only', 'explode'], answer=1,
         why='With a schema.'),
    dict(q='Beginner: Sink for debugging that prints batches?', options=['kafka', 'console', 'parquet', 'jdbc'], answer=1,
         why='Also memory.'),
    dict(q='Intermediate: maxOffsetsPerTrigger=250 on 600 messages gave…', options=['1 batch', '248, 248, 104', '250 × 3', '600'], answer=1,
         why='Split across partitions.'),
    dict(q='Intermediate: Write streaming results to PostgreSQL with…', options=['format("jdbc")', 'foreachBatch + batch JDBC', 'console', 'memory'], answer=1,
         why='No streaming JDBC sink.'),
    dict(q='Intermediate: The Kafka sink needs…', options=['Any columns', 'A value column (key optional)', 'A schema registry', 'offset'], answer=1,
         why='We used to_json.'),
    dict(q='Advanced: startingOffsets changed on an existing checkpoint…', options=['Applies', 'Is ignored', 'Deletes data', 'Fails always'], answer=1,
         why='Checkpoint offsets win.'),
    dict(q='Advanced: Why is the socket source for testing only?', options=['Slow', 'Not replayable / no fault tolerance', 'No schema', 'Python only'], answer=1,
         why='Cannot re-read after failure.'),
])

REVISION = [
    'Kafka source: key, value (binary), topic, partition, offset, timestamp.',
    'Parse with <code>from_json(CAST(value AS STRING), schema)</code>.',
    '<code>maxOffsetsPerTrigger</code> limits batch size (248/248/104).',
    'File sinks: exactly-once via <code>_spark_metadata</code>; Kafka sink: at-least-once.',
    '<code>foreachBatch(df, batch_id)</code> lets you use any batch writer.',
    'One query + one checkpoint per sink.',
    '<code>startingOffsets</code> only applies to a new checkpoint.',
]
FAQ = [
    ('Do I need a schema registry for Avro/Protobuf?', 'Spark has from_avro/from_protobuf; with a registry you usually strip the wire-format header or use a platform integration.'),
    ('Can one query write to two sinks?', 'Use foreachBatch and write the batch twice (cache it first), or start two queries.'),
    ('How do I write to a Delta or Iceberg table?', 'writeStream.format("delta") / toTable("name"); both are idempotent table sinks.'),
    ('What does failOnDataLoss do?', 'Fails the query if offsets it needs were deleted by Kafka retention; set false only if losing data is acceptable.'),
    ('Is foreach different from foreachBatch?', 'foreach calls your writer per row (open/process/close); foreachBatch gives a whole DataFrame per batch and is usually simpler and faster.'),
]

PRACTICE_INTRO = 'Programs about sources, offsets and sinks.'
PROBLEMS = [
    dict(level='easy', title='Batches', stmt='Batches for 10,000 messages at 2,000 per trigger.', inp='10000, 2000',
         code='''print(10000 // 2000)
''', explain='5.'),
    dict(level='easy', title='Next offset', stmt='Next offset after reading 0..94.', inp='94',
         code='''print(94 + 1)
''', explain='Stored per partition.'),
    dict(level='easy', title='Files written', stmt='Files from 3 batches × 3 partitions.', inp='3, 3',
         code='''print(3 * 3)
''', explain='9, as in the lab.'),
    dict(level='medium', title='Parse', stmt='Parse a JSON value.', inp='bytes',
         code='''import json
print(json.loads(b'{"order_id": 7, "amount": 99}'.decode())["amount"])
''', explain='from_json in Spark.'),
    dict(level='medium', title='Filter for sink', stmt='Keep orders ≥ 450.', inp='amounts',
         code='''print([a for a in [120, 455, 499, 300] if a >= 450])
''', explain='big_orders topic.'),
    dict(level='medium', title='Catch-up time', stmt='Batches to catch up 20M at 2M per batch.', inp='20M, 2M',
         code='''print(20 // 2)
''', explain='10 batches.'),
    dict(level='business', title='Retention', stmt='Can we replay 10 days with 7-day retention?', inp='10, 7',
         code='''print(10 <= 7)
''', explain='No: data already deleted.'),
    dict(level='business', title='Teams served', stmt='Queries needed for lake, finance, fraud.', inp='3 sinks',
         code='''print(3, "queries, 3 checkpoints")
''', explain='Independent restarts.'),
]

SCN_INTRO = 'Kafka + Spark is the most common streaming stack in interviews.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“Read Kafka in Spark”',
        'Write the code to read JSON orders from Kafka.',
        'steps?',
        '<p><code>spark.readStream.format("kafka").option("kafka.bootstrap.servers", s).option("subscribe", "orders").load()</code>, then <code>select(from_json(col("value").cast("string"), schema).alias("o")).select("o.*")</code>, then <code>writeStream</code> with a checkpoint.</p>', 'Forgetting to cast value from binary.') +
    scn('Data engineering', 'Mid-level', 'Writing to a database',
        'Stream totals into PostgreSQL.',
        'how?',
        '''<ul>
          <li>foreachBatch with the batch JDBC writer.</li>
          <li>Idempotent: upsert or delete+insert by batch_id.</li>
          <li>Own checkpoint location.</li>
        </ul>''', 'Looking for a format("jdbc") streaming sink.') +
    scn('Data engineering', 'Mid-level', 'Huge backlog',
        'After an outage the first batch keeps failing.',
        'fix?',
        '''<ol>
          <li>Set maxOffsetsPerTrigger to bound batches.</li>
          <li>Watch lag shrink across batches.</li>
          <li>Keep the limit for future restarts.</li>
        </ol>''', 'Just adding memory.') +
    scn('Platform', 'Senior', 'Reprocessing',
        'Design safe reprocessing of a Kafka-fed table.',
        'approach?',
        '''<ul>
          <li>Version checkpoints and output paths (v2).</li>
          <li>startingOffsets / byTimestamp within retention.</li>
          <li>Backfill to v2, validate, then switch readers.</li>
        </ul>''', 'Editing checkpoint files by hand.')
)
