import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='09-structured-streaming', lesson='01-streaming-concepts', n='9.1',
    module_label='Module 9 · Structured Streaming',
    title='Streaming concepts',
    desc='Structured Streaming concepts with PySpark 4.3.0: streaming DataFrames from readStream, why count() fails, the unbounded-table model, micro-batches with a 2 second trigger (100 rows per batch in about 0.4 s) read from lastProgress, triggers (default, processingTime, availableNow, continuous), and an availableNow file stream that restarts from its checkpoint and reads only the new file.',
    og_desc='Your first Spark Structured Streaming queries: micro-batches, triggers and checkpoints, with real progress metrics.',
    minutes=26, level='Beginner → Intermediate',
    lead='Structured Streaming runs a normal DataFrame query on data that keeps arriving. This lesson builds streaming DataFrames, runs micro-batches with a trigger, reads <code>lastProgress</code>, and uses <code>availableNow</code> with a checkpoint to process only new files. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', 'Micro-batches measured', 'availableNow', 'Runs in your browser (Python)'],
)

MAIN = '''# The micro-batch loop in miniature
incoming = [[3, 5], [2], [], [7, 1, 4]]        # new rows per trigger
checkpoint = {"offset": 0}
state = {"orders": 0, "revenue": 0}

for batch_id, rows in enumerate(incoming):
    state["orders"] += len(rows)
    state["revenue"] += sum(rows)
    checkpoint["offset"] += len(rows)
    print(f"batch {batch_id}: read {len(rows)} new -> {state}")
print("checkpoint:", checkpoint)
'''
RUN = dict(
    heading='Run the code: the micro-batch loop',
    intro='<p>A tiny model of what Spark does on every trigger. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    state["orders"] += len(rows)', 'Only the new rows are processed; the running totals are state.'),
        ('    checkpoint["offset"] += len(rows)', 'The checkpoint records how far the source has been read, so a restart continues from here.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then add a fifth batch of rows.', code=None),
        dict(label='2 · Predict first: rows per batch', hint='<b>Predict first:</b> 50 rows/s with a 2 s trigger.',
             code='''rate, trigger_s = 50, 2
print(rate * trigger_s, "rows per micro-batch")
'''),
        dict(label='3 · Keeping up', hint='Is the stream keeping up?',
             code='''input_per_s, processed_per_s = 50.0, 274.7
print("keeping up" if processed_per_s > input_per_s else "falling behind")
'''),
        dict(label='4 · availableNow', hint='Files with maxFilesPerTrigger=1.',
             code='''files, per_trigger = 3, 1
print(files // per_trigger, "batches, then the query stops")
'''),
        dict(label='5 · Spot the error', hint='Calling a batch action on a stream.', expect='error',
             code='''is_streaming = True
assert not is_streaming, "Queries with streaming sources must be executed with writeStream.start()"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: a first stream',
    intro='<p>In the <code>pyspark</code> shell. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Streaming DataFrame', cmd='s = spark.readStream.format("rate").option("rowsPerSecond", 50).load()\ns.isStreaming', file='pyspark',
             output='True', note='Nothing read yet.'),
        dict(title='2 · Start', cmd='q = agg.writeStream.format("memory").queryName("rev").outputMode("complete").trigger(processingTime="2 seconds").start()\nspark.sql("SELECT * FROM rev ORDER BY city_id").show(2)', file='pyspark',
             output='+-------+------+-------+\n|city_id|orders|revenue|\n+-------+------+-------+\n|      0|    88|  15312|\n|      1|    88|  15400|\n+-------+------+-------+', note='Running totals.'),
        dict(title='3 · Progress', cmd='q.lastProgress["numInputRows"], q.status["message"]', file='pyspark',
             output="(100, 'Waiting for next trigger')", note='Then q.stop().'),
    ],
)

TRACE = dict(
    heading='Restarting from a checkpoint',
    intro='<p>Follow a restart that reads only new files.</p>',
    code='''seen = {"f0", "f1", "f2"}
folder = ["f0", "f1", "f2", "f3"]
new = []
for f in folder:
    if f not in seen:
        new.append(f)
        seen.add(f)
print(new)
''',
    notes={1: 'Checkpoint :: Files already processed.', 5: 'New :: Only f3 is read.'},
)

WORKED_INTRO = 'Three first streaming decisions at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='Streaming · basics', title='Batch to stream',
         problem='<p>Turn a batch city-revenue job into a stream.</p>',
         inp='spark.read.json(...)',
         approach=['read → readStream (with a schema).', 'Same groupBy.', 'write → writeStream…start().'],
         code='''batch = "spark.read.json(p).groupBy('city').sum('amount').write.save(o)"
stream = batch.replace("read.json", "readStream.schema(s).json").replace("write.save(o)", "writeStream.outputMode('complete').start()")
print(stream)
''', notes={2: 'Schema :: File streams need an explicit schema.'},
         tryit='Step 2.'),
    dict(level='i', tag='Streaming · triggers', title='Pick a trigger',
         problem='<p>Data arrives hourly; results needed within 2 hours.</p>',
         inp='hourly files',
         approach=['Always-on cluster is wasteful.', 'availableNow on a schedule.', 'Checkpoint keeps progress.'],
         code='''latency_needed_min, arrival_min = 120, 60
print("availableNow on a schedule" if latency_needed_min >= arrival_min else "always-on trigger")
''', notes={1: 'Cost :: Pay only while it runs.'},
         tryit='Step 3.'),
    dict(level='a', tag='Streaming · health', title='Is it keeping up?',
         problem='<p>Progress shows 800 input rows/s and 650 processed rows/s.</p>',
         inp='lastProgress',
         approach=['processed < input: backlog grows.', 'Find the slow stage.', 'Scale or reduce work.'],
         code='''backlog_per_min = (800 - 650) * 60
print(backlog_per_min, "rows of backlog added per minute")
''', notes={1: 'Lag :: Latency grows without bound.'},
         tryit='Scenario 3.'),
]

QUIZ = mix([
    dict(q='Beginner: How do you start a streaming query?', options=['df.count()', 'df.writeStream...start()', 'df.collect()', 'spark.stream()'], answer=1,
         why='Actions fail on streams.'),
    dict(q='Beginner: Structured Streaming models a stream as…', options=['A list', 'An unbounded table', 'An RDD only', 'A file'], answer=1,
         why='New rows are appended.'),
    dict(q='Beginner: Default execution model?', options=['Continuous', 'Micro-batches', 'One row at a time', 'Hourly'], answer=1,
         why='Continuous is experimental.'),
    dict(q='Intermediate: 50 rows/s, 2 s trigger. Rows per batch?', options=['50', '100', '25', '200'], answer=1,
         why='As in the lab.'),
    dict(q='Intermediate: trigger(availableNow=True) does what?', options=['Runs forever', 'Processes all available data, then stops', 'Runs once on one file', 'Disables checkpoints'], answer=1,
         why='Respects maxFilesPerTrigger.'),
    dict(q='Intermediate: Where are progress and offsets kept?', options=['Driver memory', 'The checkpoint location', 'The sink only', 'Logs'], answer=1,
         why='Needed for restarts.'),
    dict(q='Advanced: Restart with the same checkpoint and one new file. Reads…', options=['All 4 files', 'Only the new file', 'Nothing', 'Fails'], answer=1,
         why='Batch 3: 50 rows.'),
    dict(q='Advanced: processedRowsPerSecond < inputRowsPerSecond means…', options=['Healthy', 'The stream is falling behind', 'Data loss', 'Trigger too slow'], answer=1,
         why='Backlog grows.'),
])

REVISION = [
    'Stream = unbounded table; query runs incrementally in micro-batches.',
    '<code>readStream</code> → transform → <code>writeStream…start()</code>; batch actions fail.',
    'Triggers: default, processingTime, availableNow, continuous (experimental).',
    'Lab: 2 s trigger → 100 rows/batch in ~0.4 s.',
    'Monitor with <code>status</code>, <code>lastProgress</code>, <code>recentProgress</code>.',
    'availableNow: all new data in batches, then stop; great for scheduled jobs.',
    'Checkpoint stores offsets/state; restart reads only new data.',
]
FAQ = [
    ('Is Structured Streaming real-time?', 'Micro-batches give latencies from about a second upward; continuous mode and newer real-time modes target lower latency for simple queries.'),
    ('What about DStreams (Spark Streaming)?', 'The old RDD-based API is legacy; use Structured Streaming for new work.'),
    ('Do I need a schema for file streams?', 'Yes by default, so the schema does not change between batches; schema inference can be enabled but is risky.'),
    ('Can I run several streaming queries in one app?', 'Yes; each start() creates a query; use spark.streams.awaitAnyTermination().'),
    ('What does the memory sink do?', 'Keeps results in a driver-side table for testing; never use it for big data.'),
]

PRACTICE_INTRO = 'Programs about micro-batches and triggers.'
PROBLEMS = [
    dict(level='easy', title='Rows per batch', stmt='Rows per micro-batch.', inp='200 rows/s, 5 s trigger',
         code='''print(200 * 5)
''', explain='1,000 rows.'),
    dict(level='easy', title='Batches', stmt='Batches for 12 files with 3 files per trigger.', inp='12, 3',
         code='''print(12 // 3)
''', explain='4 batches.'),
    dict(level='easy', title='Keeping up', stmt='Is 0.4 s per batch fine for a 2 s trigger?', inp='0.4, 2',
         code='''print(0.4 < 2)
''', explain='Yes.'),
    dict(level='medium', title='Running totals', stmt='Keep totals over batches.', inp='batches',
         code='''total = 0
for b in [[3, 5], [2], [7]]:
    total += sum(b)
    print(total)
''', explain='State.'),
    dict(level='medium', title='Backlog', stmt='Backlog after 10 min.', inp='800 in, 650 out per s',
         code='''print((800 - 650) * 600)
''', explain='90,000 rows.'),
    dict(level='medium', title='New files', stmt='Files to process after restart.', inp='seen vs folder',
         code='''seen = {"a", "b"}
print(sorted({"a", "b", "c", "d"} - seen))
''', explain='Checkpoint logic.'),
    dict(level='business', title='Cluster hours', stmt='Hours per day: always-on vs 24 availableNow runs of 3 min.', inp='24 h vs 24 × 3 min',
         code='''print(24, "vs", 24 * 3 / 60)
''', explain='1.2 h.'),
    dict(level='business', title='Freshness', stmt='Worst-case freshness with 5 s trigger and 0.5 s batch.', inp='5, 0.5',
         code='''print(5 + 0.5, "s")
''', explain='Seconds instead of an hour.'),
]

SCN_INTRO = 'Streaming basics are asked in every data engineering interview.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“Batch vs streaming in Spark?”',
        'Explain the difference.',
        'API?',
        '<p>Batch reads a fixed dataset once with <code>spark.read</code>. Structured Streaming reads with <code>readStream</code>, treats input as an unbounded table and runs the same DataFrame query incrementally in micro-batches via <code>writeStream.start()</code>, keeping offsets and state in a checkpoint.</p>', 'Saying streaming needs a totally different API.') +
    scn('Data engineering', 'Mid-level', 'Scheduled incremental job',
        'Process new files every hour without reprocessing old ones.',
        'design?',
        '''<ul>
          <li>File stream with a schema and a checkpoint.</li>
          <li>trigger(availableNow=True), scheduled hourly.</li>
          <li>In my test a restart read only the new file.</li>
        </ul>''', 'Tracking processed files in a custom table.') +
    scn('Data engineering', 'Mid-level', 'Monitoring',
        'How do you know a stream is healthy?',
        'metrics?',
        '''<ol>
          <li>lastProgress: input vs processed rows/s, batch duration.</li>
          <li>State size and watermark.</li>
          <li>StreamingQueryListener → metrics/alerts.</li>
        </ol>''', 'Only checking that the job is running.') +
    scn('Platform', 'Senior', 'Streaming or batch?',
        'A team asks for streaming for daily reports.',
        'advice?',
        '''<ul>
          <li>Match latency needs to cost; daily needs no always-on stream.</li>
          <li>availableNow gives incremental processing on a schedule.</li>
          <li>Move to always-on only when latency demands it.</li>
        </ul>''', 'Streaming everything by default.')
)
