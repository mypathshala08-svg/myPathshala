import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l91_concepts.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)

def table_grow(x, y, rows, new=0, label=''):
    o = t(x + 50, y - 6, label, 7.2, 'ink2', bold=True) if label else ''
    for k in range(rows):
        o += box(x, y + k * 12, 100, 10, 'acc' if k >= rows - new else 'card', rx=2)
    return o

# ---------------------------------------------------------------- story
sc_ = (table_grow(20, 30, 6, 2, 'unbounded input table') + arrow(126, 66, 170, 66, 'ink3', 1.1) + t(148, 58, 'query', 7, 'ink2') +
       opbox(176, 50, 'same groupBy', 'run per micro-batch', 'blue', 120, 32) + arrow(298, 66, 330, 66, 'ink3', 1.1) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured (rate source)', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('isStreaming: True', 'blue'), ('count() → error', 'red'),
           ('trigger 2 s: 100 rows/batch', 'green'), ('batch took ~0.4 s', 'green'),
           ('availableNow: 3 batches, stop', 'green'), ('restart: only new file (50)', 'green')])))
scene_svg = scene('Structured Streaming treats a stream as a table that keeps growing and runs the same DataFrame query on each new slice of rows in small batches. We ran a rate source with a 2 second trigger and a file stream with trigger availableNow.', sc_,
                  'A stream is a table that <tspan font-weight="700" class="s-acc">never stops growing</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Can the dashboard update every few seconds?”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s city dashboard was refreshed by a batch job every hour. During a festival sale, operations wanted live order counts per city, within seconds, and asked the data team to “make the batch job run every 5 seconds”.</p>

{scene_svg}

K> Sir, can’t we just run the same Spark job in a loop?
A> You would re-read everything each time and lose track of what was already counted. <b>Structured Streaming</b> does the loop for you: it remembers what it has read, processes only new rows in each <b>micro-batch</b>, and keeps the running totals.
R> Do we need a new API?
A> Almost the same DataFrame API: <code>readStream</code> instead of <code>read</code>, <code>writeStream.start()</code> instead of <code>write</code>. Today we start our first streaming queries and read their progress. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Streaming at three levels
L1> A bank passbook
      <ul>
        <li>You do not reprint the whole passbook after every deposit. The clerk prints only the new entries and the new balance.</li>
        <li>The last printed line is the bookmark (checkpoint); the balance is the state.</li>
      </ul>
L2> The API
      <ul>
        <li><code>spark.readStream.format(...).load()</code> gives a streaming DataFrame (<code>isStreaming</code> = True).</li>
        <li>Transform it like any DataFrame, then <code>df.writeStream.format(...).outputMode(...).trigger(...).option("checkpointLocation", ...).start()</code> returns a <code>StreamingQuery</code>.</li>
        <li>Monitor with <code>q.status</code>, <code>q.lastProgress</code>, <code>q.recentProgress</code>; stop with <code>q.stop()</code> or wait with <code>awaitTermination()</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>An action like <code>count()</code> on a streaming DataFrame fails; only <code>writeStream.start()</code> runs it.</li>
        <li>With a 2 s trigger and 50 rows/s, each batch read 100 rows and took about 0.4 s.</li>
        <li><code>availableNow</code> processed 3 files in 3 batches and stopped; rerun with the same checkpoint read only the new file.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Structured Streaming</h2>
''' + def_block(
    '<b>Structured Streaming</b> is Spark’s stream processing engine built on the Spark SQL engine. A data stream is modelled as an <b>unbounded input table</b> to which new rows are appended; a query on it is written with the same DataFrame/SQL API as a batch query, and Spark runs it <b>incrementally</b>, by default as a series of <b>micro-batches</b>. Each micro-batch reads new data from the source (tracked as offsets), updates any state such as running aggregates, and writes results to a sink according to the <b>output mode</b>. A <b>trigger</b> decides when micro-batches run (as fast as possible, at fixed intervals, once over all available data, or continuously). Progress and offsets are stored in a <b>checkpoint location</b>, which allows end-to-end exactly-once results with replayable sources and idempotent sinks.',
    'Structured Streaming lets you write a normal DataFrame query and run it on data that keeps arriving. Spark treats the stream as a growing table, processes the new rows in small batches, remembers where it stopped, and keeps running totals up to date.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Streaming DataFrame', 'From readStream; isStreaming=True.'),
    ('Unbounded table', 'The stream seen as a growing table.'),
    ('Micro-batch', 'One small batch of new rows.'),
    ('Trigger', 'When the next micro-batch runs.'),
    ('Source', 'Where rows come from (Kafka, files…).'),
    ('Sink', 'Where results go.'),
    ('StreamingQuery', 'Handle returned by start().'),
    ('Checkpoint', 'Folder with offsets and state.'),
]) + '''

  <h3>Batch vs streaming</h3>
''' + table(['', 'Batch', 'Streaming'], [
    ['Read', '<code>spark.read</code>', '<code>spark.readStream</code>'],
    ['Write', '<code>df.write…save()</code>', '<code>df.writeStream…start()</code>'],
    ['Runs', 'Once, on all data', 'Repeatedly, on new data'],
    ['Remembers', 'Nothing', 'Offsets + state in the checkpoint'],
    ['Actions like count()', 'Allowed', 'Error: use writeStream.start()'],
], minw=560) + lv + '''
EXAM> “What is Structured Streaming?” A stream-processing engine on Spark SQL that treats a stream as an unbounded table and runs a DataFrame/SQL query on it incrementally in micro-batches (or continuous mode). You define source, transformations, sink, output mode and trigger; progress and state are saved in a checkpoint, giving fault tolerance and exactly-once results with replayable sources and idempotent sinks.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Triggers</h2>
''' + table(['Trigger', 'Code', 'Behaviour', 'Use'], [
    ['Default', '(none)', 'Next batch as soon as the previous ends', 'Low latency'],
    ['Fixed interval', '<code>trigger(processingTime="2 seconds")</code>', 'One batch every interval', 'Steady load'],
    ['Available now', '<code>trigger(availableNow=True)</code>', 'All data available now, in several batches, then stop', 'Scheduled incremental jobs'],
    ['Continuous', '<code>trigger(continuous="1 second")</code>', 'Long-running tasks, ms latency', 'Experimental; map-only'],
], minw=640) + '''
WARN> <code>trigger(once=True)</code> is deprecated; use <code>availableNow=True</code>, which respects rate limits such as <code>maxFilesPerTrigger</code> and splits the work into several batches. And always set a <code>checkpointLocation</code> on real sinks: without it Spark uses a temporary folder and a restart reprocesses everything from the start.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Your first streaming queries</h2>
  <p>All outputs are real: PySpark 4.3.0, <code>local[2]</code>. The <b>rate</b> source generates rows with a timestamp and an increasing value, ideal for testing; later lessons use Kafka and files.</p>
''' + stepper([
    ('Step 1 · A streaming DataFrame',
     code('python', 'l91_concepts.py', 's = spark.readStream.format("rate").option("rowsPerSecond", 50).load()\nprint("isStreaming:", s.isStreaming); s.printSchema()\ns.count()     # a batch action', sec('== 1)', '== 2)')),
     '<code>readStream</code> returns a DataFrame with a schema, but nothing has been read yet. Calling a batch action like <code>count()</code> fails, because a stream has no end to count to. Streaming queries only run through <code>writeStream…start()</code>.'),
    ('Step 2 · Micro-batches and progress',
     code('python', 'l91_concepts.py', 'orders = s.select("timestamp", (F.col("value") % 4).alias("city_id"), (F.col("value") % 500).alias("amount"))\nagg = orders.groupBy("city_id").agg(F.count("*").alias("orders"), F.sum("amount").alias("revenue"))\nq = (agg.writeStream.format("memory").queryName("rev").outputMode("complete")\n        .trigger(processingTime="2 seconds").option("checkpointLocation", CK + "/a").start())\n# every 2.2 s: q.lastProgress', sec('== 2)', '== 3)')),
     'The <code>groupBy</code> is exactly the batch code. Spark ran a micro-batch every 2 s: at 50 rows per second each batch read <b>100 rows</b> and took about <b>0.4 s</b>, so the query keeps up (processed rows/s > input rows/s). The memory sink holds the running totals, readable with SQL. <code>q.status</code> shows “Waiting for next trigger” between batches.'),
    ('Step 3 · availableNow and the checkpoint',
     code('python', 'l91_concepts.py', 'fs = spark.readStream.schema("order_id long, amount long").option("maxFilesPerTrigger", 1).json(src)\nq2 = fs.writeStream.format("parquet").option("path", OUT) \\\n       .option("checkpointLocation", CK + "/b").trigger(availableNow=True).start()\nq2.awaitTermination()\n# add f3.json, start the same query again', sec('== 3)')),
     'Three JSON files, one per batch (<code>maxFilesPerTrigger=1</code>), and the query <b>stopped by itself</b>. After adding a fourth file, the same query with the same checkpoint ran batch 3 with only the <b>50 new rows</b>: total 350, nothing read twice. This is how many teams run “streaming” jobs on a schedule: incremental, cheap, and restartable.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('isStreaming: True', G), ('s.count() -> ERROR', RD), ('use writeStream.start()', Y)], size=7.6),
    term([('batch 2: 50 rows, 418 ms', W), ('batch 3: 100 rows, 364 ms', G), ('batch 4: 100 rows, 552 ms', G)], size=7.4),
    term([('city 0: 88 orders, 15312', W), ('city 1: 88 orders, 15400', W), ('status: Waiting for next trigger', Y)], size=7.2),
    term([('availableNow: (0,100) (1,100) (2,100)', G), ('stopped by itself: True', G), ('rerun: (3, 50) only new file', G)], size=7.2),
]
B1 = [
    t(180, 14, 'A table that keeps growing', 9.4, bold=True) + table_grow(130, 34, 7, 2, '') + t(250, 100, 'new rows', 7.4, 'acc') + cap('Same DataFrame API.', '', 'blue', y=144, h=30),
    t(180, 14, 'Trigger → micro-batch', 9.4, bold=True) + flow([('trigger', 'every 2 s', 'violet'), ('read new', 'offsets', 'blue'), ('process', 'update state', 'green'), ('sink', 'write', 'blue')], y=50, w=72, gap=14) + cap('Repeat forever.', '', 'green', y=144, h=30),
    t(180, 14, 'State: running totals', 9.4, bold=True) + opbox(30, 46, 'old totals', 'state', 'green', 120, 32) + t(180, 62, '+', 12, 'ink2') + opbox(210, 46, 'new batch', '100 rows', 'acc', 120, 32) + cap('Only new rows are read.', '', 'green', y=144, h=30),
    t(180, 14, 'Checkpoint = bookmark', 9.4, bold=True) + flow([('run 1', 'files 0–2', 'blue'), ('checkpoint', 'offsets', 'violet'), ('run 2', 'file 3 only', 'green')], y=50, w=96, gap=16) + cap('Restart where you stopped.', '', 'green', y=144, h=30),
]
see_caps = ['A streaming DataFrame.', 'Micro-batches.', 'Results in the sink.', 'availableNow + restart.']
behind_caps = ['The unbounded table.', 'The micro-batch loop.', 'Incremental state.', 'Checkpoints.']
two = anim_two('Structured Streaming', 'The micro-batch loop', 'Real lab outputs', 'What Spark does', see, B1, see_caps, behind_caps)

e1 = (t(180, 22, 'Hourly batch dashboard', 9.4, bold=True) + t(180, 56, 'festival: ops want live numbers', 8.4, 'ink2') + cap('An hour is too late.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'readStream from Kafka', 9.4, bold=True) + t(180, 56, 'same groupBy as the batch job', 8.4, 'ink2') + cap('Little new code.', '', 'green', y=150, h=34))
e3 = (t(180, 22, 'Trigger every 5 seconds', 9.4, bold=True) + t(180, 56, 'batch ~0.4 s in our lab', 8.4, 'ink2') + cap('Keeps up easily.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Write to a serving table', 9.4, bold=True) + t(180, 56, 'dashboard reads it', 8.4, 'ink2') + cap('Seconds, not hours.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Watch lastProgress', 9.4, 'acc', bold=True) + t(180, 56, 'processed/s vs input/s', 8.4, 'ink2') + cap('Falling behind?', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'The live festival dashboard',
              'From hourly batch to streaming. (Typical; latency from our lab.)',
              'Live dashboard', 'The batch aggregation becomes a streaming query with a short trigger', [e1, e2, e3, e4, e5],
              ['Hourly.', 'readStream.', 'Trigger.', 'Serve.', 'Monitor.'],
              hid='scenario-dashboard')
b1 = (t(180, 22, 'Partner drops files hourly', 9.4, bold=True) + t(180, 56, 'batch job re-reads the folder', 8.4, 'ink2') + cap('Duplicates, or tracking by hand.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'File stream + checkpoint', 9.4, bold=True) + t(180, 56, 'Spark remembers seen files', 8.4, 'ink2') + cap('No manual bookkeeping.', '', 'green', y=150, h=34))
b3 = (t(180, 22, 'trigger(availableNow=True)', 9.4, bold=True) + t(180, 56, 'scheduled every hour', 8.4, 'ink2') + cap('Runs, then stops.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Only new files read', 9.4, bold=True) + t(180, 56, 'batch 3: 50 rows in our lab', 8.4, 'ink2') + cap('Cheap.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Switch to always-on later', 9.4, 'acc', bold=True) + t(180, 56, 'same code, change the trigger', 8.4, 'ink2') + cap('Flexible.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Incremental files without bookkeeping',
              'availableNow as a scheduled incremental job. (Typical; behaviour from our lab.)',
              'availableNow', 'A file stream with availableNow processes only new files on each scheduled run', [b1, b2, b3, b4, b5],
              ['Files.', 'Checkpoint.', 'availableNow.', 'New only.', 'Flexible.'],
              hid='scenario-availablenow')
u1 = (t(180, 22, 'Batches getting slower', 9.4, bold=True) + t(180, 56, 'triggerExecution 2 s → 9 s', 8.4, 'ink2') + cap('Trigger is 5 s.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'processed/s < input/s', 9.4, bold=True) + t(180, 56, 'backlog grows every batch', 8.4, 'ink2') + cap('Latency climbs.', '', 'red', y=150, h=34))
u3 = (t(180, 22, 'Find the slow part', 9.4, bold=True) + t(180, 56, 'durationMs, state size, Spark UI', 8.4, 'ink2') + cap('Often state growth.', '', 'amber', y=150, h=34))
u4 = (t(180, 22, 'Fix: watermark / scale', 9.4, bold=True) + t(180, 56, 'Lessons 9.3 and 9.5', 8.4, 'ink2') + cap('Bound the state.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Alert on lag', 9.4, 'acc', bold=True) + t(180, 56, 'from StreamingQueryListener', 8.4, 'ink2') + cap('Before users notice.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'A stream that falls behind',
              'Reading progress metrics. (Typical.)',
              'Falling behind', 'Compare processed and input rows per second to spot a stream that cannot keep up', [u1, u2, u3, u4, u5],
              ['Slower.', 'Backlog.', 'Find.', 'Fix.', 'Alert.'],
              hid='scenario-lag')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>The micro-batch loop</h2>
  <p>Left: real outputs. Right: what Spark does on every trigger.</p>
''' + two + '''
  <p>Three live scenarios follow: a live dashboard, incremental file loads, and a stream falling behind.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Streaming at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'live', 12, 'blue', bold=True) + t(60, 58, 'metrics', 7.4, 'ink2'),
    '1. Live business metrics',
    'Orders, revenue and delivery times per city refreshed every few seconds.',
    ['Kafka', '*groupBy', 'Dashboard']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'ingest', 11, 'green', bold=True) + t(60, 58, 'lakehouse', 7.4, 'ink2'),
    '2. Continuous ingestion',
    'Events land in Delta or Iceberg tables minutes after they happen.',
    ['Events', '*readStream', 'Lake table']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'fraud', 12, 'violet', bold=True) + t(60, 58, 'alerts', 7.4, 'ink2'),
    '3. Fraud and abuse alerts',
    'Payment streams are checked against rules and recent behaviour.',
    ['Payments', '*rules', 'Alerts']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'hourly', 11, 'acc', bold=True) + t(60, 58, 'availableNow', 7.4, 'ink2'),
    '4. Incremental batch',
    'Scheduled availableNow runs replace hand-written “what’s new” logic.',
    ['Scheduler', '*availableNow', 'New data only']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'IoT', 12, 'acc', bold=True) + t(60, 58, 'riders', 7.4, 'ink2'),
    '5. Rider tracking',
    'GPS pings from delivery riders feed ETAs and zone heatmaps.',
    ['GPS pings', '*windows', 'ETA']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> DataFrames in <a href="../../04-dataframes/01-sparksession-and-dataframes/">4.1</a>, groupBy in <a href="../../06-transformations/01-groupby-and-pivot/">6.1</a>, reading files in <a href="../../05-reading-and-writing-data/01-csv-and-json/">5.1</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
