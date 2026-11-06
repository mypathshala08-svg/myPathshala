import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='09-stream-processing', lesson='04-kafka-with-spark', n='9.4', module_label='Module 9 · Stream processing',
    title='Kafka with Spark and Flink',
    desc='Processing Kafka with engines: Spark Structured Streaming (Kafka source schema, from_json, windows, watermarks, output modes, checkpoints and offsets) and Apache Flink (continuous processing, snapshots, Flink SQL), compared with Kafka Streams and ksqlDB. Real PySpark 4.3 lab on Kafka 4.4: 5-minute revenue per city, one late row dropped by the watermark, and offsets read from the checkpoint.',
    og_desc='PySpark 4.3 on Kafka 4.4: windowed revenue, a watermark drop, and offsets in the checkpoint.',
    minutes=24, level='Intermediate',
    lead='What if your team writes Python? We read Kafka with <b>Spark Structured Streaming</b>, compute windowed revenue with a <b>watermark</b>, and open the <b>checkpoint</b>; then compare <b>Flink</b>, Kafka Streams and ksqlDB. <b>All outputs are real.</b>',
    chips=['Mumbai 230', '1 row dropped', 'Offsets in checkpoint', 'Runs in your browser (Python)'])
MAIN = '''# Micro-batches with a watermark (Spark-style), in plain Python
DELAY = 60                     # watermark delay (s)
events = [[("Mumbai", 60, 80), ("Pune", 120, 90), ("Mumbai", 240, 150), ("Mumbai", 360, 60), ("Pune", 450, 45)],
          [("Mumbai", 180, 20), ("Pune", 480, 30)]]       # batch 2: chai late, poha on time
state, max_ts = {}, 0
for b, batch in enumerate(events):
    wm = max_ts - DELAY        # watermark used for this batch
    for city, ts, amt in batch:
        win = ts // 300 * 300
        if win + 300 <= wm:
            print(f"batch {b}: {city} at {ts}s dropped (window closed, watermark {wm})"); continue
        state[(win, city)] = state.get((win, city), 0) + amt
    max_ts = max([max_ts] + [ts for _, ts, _ in batch])
print(state)
'''
RUN = dict(heading='Run the code: watermarks', intro='<p>Why chai was dropped. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    wm = max_ts - DELAY        # watermark used for this batch', 'Watermark from earlier batches.'), ('        if win + 300 <= wm:', 'Window ended before the watermark: drop.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Set DELAY = 600.', code=None),
        dict(label='2 · Predict first: watermark', hint='<b>Predict first:</b> max 12:07:30, delay 1 min.', code='print("12:06:30")\n'),
        dict(label='3 · Window', hint='5-minute window of 12:04.', code='m = 4\nprint(f"12:{m // 5 * 5:02d}-12:{m // 5 * 5 + 5:02d}")\n'),
        dict(label='4 · Offsets', hint='Read checkpoint JSON.', code='import json\nprint(json.loads(\'{"orders-94":{"0":6,"1":1}}\')["orders-94"])\n'),
        dict(label='5 · Spot the error', hint='Missing Kafka package.', expect='error', code='raise RuntimeError("Failed to find data source: kafka. Please deploy the application as per the deployment section of Structured Streaming + Kafka Integration Guide.")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: PySpark + Kafka', intro='<p>Needs Spark 4.3 and the Kafka jars. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Jars', cmd='spark-sql-kafka-0-10_2.13-4.3.0.jar, spark-token-provider-kafka-0-10_2.13-4.3.0.jar, kafka-clients-3.9.2.jar, commons-pool2-2.12.1.jar', file='terminal', output='', note='Or --packages org.apache.spark:spark-sql-kafka-0-10_2.13:4.3.0.'),
           dict(title='2 · Run', cmd='PYSPARK_SUBMIT_ARGS="--jars … pyspark-shell" python3 l94.py', file='terminal', output='|12:00|12:05|Mumbai|2     |230    |', note='Local mode.'),
           dict(title='3 · Checkpoint', cmd='cat /tmp/chk94/offsets/3', file='terminal', output='{"orders-94":{"0":6,"1":1}}', note='Last line.')])
TRACE = dict(heading='Chai at 12:03 step by step', intro='<p>Watermark check.</p>',
    code='max_seen = 12 * 60 + 7.5\nwm = max_seen - 1\nwindow_end = 12 * 60 + 5\nprint(window_end <= wm)\n',
    notes={2: 'Watermark :: 12:06:30.', 4: 'Closed :: Dropped.'})
WORKED_INTRO = 'Three engine decisions.'
EXAMPLES = [
    dict(level='b', tag='Engines · choose', title='Pick an engine', problem='<p>Python team, Kafka → lakehouse.</p>', inp='need',
         approach=['Python.', 'Lake sink.', 'Spark Structured Streaming.'], code='print("Spark")\n', notes={1: 'Fit :: Skills + sinks.'}, tryit='Types table.'),
    dict(level='i', tag='Spark · modes', title='Output mode', problem='<p>Write final windows to Parquet.</p>', inp='mode',
         approach=['File sinks need append.', 'Append emits after watermark passes.', 'Delay = window + watermark.'], code='print("outputMode(\\"append\\")")\n', notes={1: 'Final :: Like suppress.'}, tryit='Lesson 9.3.'),
    dict(level='a', tag='Flink · SQL', title='Flink SQL table', problem='<p>SQL users, low latency.</p>', inp='DDL',
         approach=['CREATE TABLE with kafka connector.', 'WATERMARK FOR ts AS ts - INTERVAL 1 MINUTE.', 'TUMBLE window query.'], code="print(\"CREATE TABLE orders (city STRING, amount INT, ts TIMESTAMP(3), WATERMARK FOR ts AS ts - INTERVAL '1' MINUTE) WITH ('connector'='kafka', 'topic'='orders-94', 'format'='json')\")\n", notes={1: 'SQL :: Same ideas.'}, tryit='Scenario 2.')]
QUIZ = mix([
    dict(q='Beginner: Spark reads Kafka value as…', options=['String', 'Binary', 'JSON object', 'Avro'], answer=1, why='Cast/parse it.'),
    dict(q='Beginner: Spark stores Kafka offsets in…', options=['Consumer group', 'The checkpoint', 'ZooKeeper', 'The registry'], answer=1, why='Step 5.'),
    dict(q='Beginner: Flink processes…', options=['Micro-batches only', 'Record at a time', 'Only files', 'Only SQL'], answer=1, why='Continuous.'),
    dict(q='Intermediate: Watermark 1 min with max 12:07:30 is…', options=['12:07:30', '12:06:30', '12:05', '12:08:30'], answer=1, why='Max − delay.'),
    dict(q='Intermediate: chai at 12:03 was…', options=['Counted', 'Dropped', 'Errored', 'Sent to DLQ'], answer=1, why='Window closed.'),
    dict(q='Intermediate: Mumbai 12:00–12:05 revenue was…', options=['80', '230', '150', '290'], answer=1, why='80 + 150.'),
    dict(q='Advanced: Spark’s Kafka sink alone is…', options=['Exactly-once', 'At-least-once', 'At-most-once', 'Transactional by default'], answer=1, why='Use idempotent sinks.'),
    dict(q='Advanced: Kafka Streams fits best when…', options=['Python team', 'Java service, Kafka in and out', 'Many file sources', 'Ad-hoc SQL'], answer=1, why='Library.')])
REVISION = ['Library (Kafka Streams) vs engines (Spark, Flink) vs SQL (ksqlDB).', 'Spark: readStream kafka → binary value → from_json; micro-batches.',
    'Watermark = max event time − delay; windows behind it closed; late rows dropped.', 'Lab: Mumbai 230, Pune 90; chai dropped; offsets {"0":6,"1":1} in checkpoint.', 'Flink: continuous, snapshots, Flink SQL; choose by language, latency, sinks.']
FAQ = [('Can Spark commit offsets to Kafka?', 'Not for progress tracking; the checkpoint is the source of truth. You can set a group id prefix but lag tools need special handling.'),
    ('Is Spark streaming slow?', 'Micro-batches add latency (sub-second to seconds); Spark 4 adds a real-time mode for lower latency in some cases.'),
    ('Where can I learn Spark streaming deeply?', 'In our Spark course, Module 9 Structured Streaming (linked in the concept map).'),
    ('Do I need Schema Registry with Spark?', 'For Avro, use from_avro with the schema (or a registry-aware library); JSON uses from_json.')]
PRACTICE_INTRO = 'Engine programs.'
PROBLEMS = [
    dict(level='easy', title='Cast', stmt='Bytes to string.', inp='bytes', code='print(b"idli".decode())\n', explain='CAST(value AS STRING).'),
    dict(level='easy', title='Watermark', stmt='Max 600 s, delay 60.', inp='ints', code='print(600 - 60)\n', explain='540.'),
    dict(level='easy', title='Window', stmt='5-min start of 07:30.', inp='min', code='print(7.5 // 5 * 5)\n', explain='5.'),
    dict(level='medium', title='Revenue', stmt='Sum per city.', inp='list', code='from collections import defaultdict\nr = defaultdict(int)\nfor c, a in [("Mumbai", 80), ("Mumbai", 150), ("Pune", 90)]: r[c] += a\nprint(dict(r))\n', explain='230/90.'),
    dict(level='medium', title='Late?', stmt='Window end 300, watermark 390.', inp='ints', code='print(300 <= 390)\n', explain='Dropped.'),
    dict(level='medium', title='Offsets lag', stmt='End 10, checkpoint 6.', inp='ints', code='print(10 - 6)\n', explain='4 behind.'),
    dict(level='business', title='Latency', stmt='Trigger 3 s + process 1 s.', inp='ints', code='print(3 + 1, "s worst case")\n', explain='~4 s.'),
    dict(level='business', title='Pick', stmt='Need ms latency, Java.', inp='str', code='print("Kafka Streams or Flink")\n', explain='Not micro-batch.')]
SCN_INTRO = 'Engine interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“How does Spark read from Kafka?”', 'Explain.', 'answer?', '<p>With readStream.format("kafka"): each micro-batch reads new offset ranges per partition into a DataFrame (key, value, topic, partition, offset, timestamp). Offsets and state are kept in a checkpoint.</p>', '“Through a consumer group commit.”') +
    scn('Data', 'Mid-level', 'Missing data in windows', 'Late mobile events.', 'fix?', '<ul><li>Increase watermark delay.</li><li>Monitor numRowsDroppedByWatermark.</li></ul>', 'Remove the watermark (state grows forever).') +
    scn('Platform', 'Mid-level', 'No lag metrics', 'Spark job invisible to lag tools.', 'why?', '<ul><li>Offsets in checkpoint.</li><li>Use lastProgress / custom exporter.</li></ul>', 'Add a consumer group manually.') +
    scn('Architecture', 'Senior', 'Choose', 'Fraud ms + BI hourly.', 'design?', '<ul><li>Flink/Kafka Streams for fraud.</li><li>Spark → lakehouse for BI.</li></ul>', 'One engine for all.'))
