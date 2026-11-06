import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l95_checkpoint.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)

def ckdir(x, y, hi=None):
    items = [('offsets/', 'planned: batch N reads up to …', 'blue'), ('commits/', 'done: batch N finished', 'green'),
             ('state/', 'running totals, join buffers', 'violet'), ('sources/ + metadata', 'query id, file lists', 'card')]
    o = ''
    for k, (n, d, tone) in enumerate(items):
        o += box(x, y + k * 24, 180, 20, 'acc' if hi == k else tone, rx=4) + t(x + 8, y + 13 + k * 24, n, 7.2, 'ink', anchor='start', bold=True, mono=True) + t(x + 188, y + 13 + k * 24, d, 6.8, 'ink2', anchor='start')
    return o

# ---------------------------------------------------------------- story
sc_ = (t(20, 22, 'checkpointLocation/', 7.6, 'ink2', anchor='start', bold=True, mono=True) + ckdir(20, 32) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured (Kafka → sinks)', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('restart: batch 1, +500 rows', 'green'), ('file sink: 1500 = 1500', 'green'),
           ('crash + append: 2099 rows', 'red'), ('crash + idempotent: 1500', 'green'),
           ('dedup: 1800 in → 1500 out', 'green'), ('key type changed: ERROR', 'red')])))
scene_svg = scene('A checkpoint stores which offsets each micro-batch planned to read, which batches committed, and the query state. We restarted a Kafka query, crashed a foreachBatch sink mid-stream with and without idempotent writes, deduplicated replayed events in a RocksDB state store, and changed a stateful query on an old checkpoint.', sc_,
                  'Exactly-once = <tspan font-weight="700" class="s-acc">replayable source + checkpoint + idempotent sink</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Finance found 600 extra orders”</h2>
  <div class="story">
    <p class="narration">A TiffinGo streaming job crashed at 2 a.m. and restarted automatically. Nothing was lost, but the next morning the PostgreSQL city totals were higher than the orders in the lake. The difference was exactly one micro-batch.</p>

{scene_svg}

K> Sir, Spark promises exactly-once. How did one batch get written twice?
A> Spark guarantees that each batch’s <b>data</b> is processed exactly once into its state and committed exactly once in its checkpoint. But if your sink wrote the batch and the job died before the commit, Spark replays that batch. A plain append then writes it again.
R> So the sink must cope with replays?
A> Yes: <b>idempotent</b> writes keyed by <code>batch_id</code>. Today we restart a Kafka query from its checkpoint, open the checkpoint folder, crash a sink on purpose, deduplicate replayed events with state, and break a checkpoint by changing the query. All outputs are real (PySpark 4.3.0, Kafka 3.9).
  </div>
</section>
'''

lv = '''
LEVELS> Fault tolerance at three levels
L1> A cashier’s register book
      <ul>
        <li>Before counting a bundle, the cashier writes “bundle 7: notes 101–200” (offsets). After putting it in the safe, she ticks “bundle 7 done” (commit).</li>
        <li>After a power cut she redoes any bundle without a tick. If the safe already had that bundle, she must check the bundle number first (idempotent) or the money is counted twice.</li>
      </ul>
L2> The pieces
      <ul>
        <li><code>option("checkpointLocation", path)</code>: offsets, commits, state, sources, metadata.</li>
        <li>Sources must be replayable (Kafka, files); sinks idempotent (file/table sinks, or <code>foreachBatch</code> keyed by <code>batch_id</code>).</li>
        <li>State: <code>dropDuplicatesWithinWatermark</code>, aggregations, joins; RocksDB via <code>spark.sql.streaming.stateStore.providerClass</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>Restart read only batch 1 (500 new rows); the file sink had 1,500 distinct orders.</li>
        <li>Crash after writing batch 1: append wrote 2,099 rows for 1,500; idempotent writes kept 1,500.</li>
        <li>Changing the grouping key type on an old checkpoint failed with <code>STATE_STORE_KEY_SCHEMA_NOT_COMPATIBLE</code>.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Checkpoints, exactly-once and state</h2>
''' + def_block(
    'The <b>checkpoint location</b> is a fault-tolerant directory (HDFS, S3, ADLS…) where a streaming query records, before each micro-batch, the source <b>offsets</b> it will process (write-ahead log), and after it the batch <b>commit</b>, together with versioned <b>state store</b> files for stateful operators. On restart Spark reads the last offsets and commits: an uncommitted batch is <b>re-executed with the same offsets and batch id</b>, and processing continues. Structured Streaming therefore provides <b>end-to-end exactly-once</b> semantics when the source is replayable and the sink is <b>idempotent</b> (it ignores or overwrites a batch it has already written, as the file sink does with its <code>_spark_metadata</code> log). Stateful operators keep data across batches in a state store (HDFS-backed by default, or RocksDB for large state), bounded by watermarks. The checkpoint is tied to the query: incompatible changes to stateful operators, such as a new grouping key schema, cannot reuse it.',
    'The checkpoint is the query’s memory: what it planned to read, what it finished, and its running state. After a crash Spark redoes any unfinished batch with exactly the same input. That gives exactly-once results only if the output can safely receive the same batch twice; file sinks can, your own foreachBatch code must be written to.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('offsets/', 'Write-ahead log of planned batches.'),
    ('commits/', 'Batches that completed.'),
    ('state/', 'State store files per operator.'),
    ('Replay', 'Re-running an uncommitted batch.'),
    ('Idempotent sink', 'Writing a batch twice = once.'),
    ('At-least-once', 'May write duplicates on replay.'),
    ('RocksDB state store', 'Off-heap state for large state.'),
    ('dropDuplicatesWithinWatermark', 'Dedup with bounded state.'),
]) + '''

  <h3>Guarantees by sink</h3>
''' + table(['Sink', 'On replay', 'End-to-end', 'Lab'], [
    ['File (Parquet)', 'Batch already in _spark_metadata → skipped', 'Exactly-once', '1,500 distinct of 1,500'],
    ['Delta / Iceberg table', 'Transaction log with batch ids', 'Exactly-once', ''],
    ['Kafka', 'Messages may be written again', 'At-least-once', 'consumers dedupe'],
    ['foreachBatch append', 'Batch written again', 'At-least-once', '2,099 rows for 1,500'],
    ['foreachBatch keyed by batch_id', 'Overwrites same batch', 'Exactly-once', '1,500 rows'],
], minw=640) + lv + '''
EXAM> “How does Structured Streaming achieve exactly-once?” Replayable sources (Kafka offsets, file lists) + a checkpoint with a write-ahead log of offsets and commit log + deterministic re-execution of uncommitted batches with the same batch id + idempotent sinks (file/table sinks, or foreachBatch writes keyed by batch_id/MERGE). State is checkpointed per batch. Without an idempotent sink you get at-least-once.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>What you can change on a checkpoint</h2>
''' + table(['Change', 'Allowed?', 'Notes'], [
    ['Add a filter / stateless column', 'Usually yes', 'Output schema of sink must still fit'],
    ['Trigger interval, maxOffsetsPerTrigger', 'Yes', 'Takes effect on restart'],
    ['Add a new Kafka topic to subscribe', 'Yes (new topic starts per startingOffsets)', ''],
    ['Grouping keys / aggregation state schema', 'No', '<code>STATE_STORE_KEY_SCHEMA_NOT_COMPATIBLE</code> (lab)'],
    ['Add/remove a stateful operator, change join type', 'No', 'New checkpoint + backfill'],
    ['Change sink type (files → Kafka)', 'Mostly no', 'New checkpoint'],
], minw=620) + '''
WARN> Never share one checkpoint between two queries, never copy a checkpoint to “restart from yesterday”, and never delete the <code>_spark_metadata</code> folder of a file sink: readers use it to ignore files of uncommitted batches. Keep checkpoints on durable storage (not a local disk of a driver that can disappear), and treat them as part of the job: version the path when the logic changes.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Breaking a stream on purpose</h2>
  <p>All outputs are real: PySpark 4.3.0, <code>local[2]</code>, Kafka 3.9 in Docker with a 2-partition topic <code>pay</code>. Queries use <code>trigger(availableNow=True)</code> so “stop” and “restart” are just two runs on the same checkpoint.</p>
''' + stepper([
    ('Step 1 · Restart from the checkpoint',
     code('python', 'l95_checkpoint.py', 'produce(0, 1000)\nstream().writeStream.format("parquet").option("path", OUT) \\\n        .option("checkpointLocation", CK + "/files").trigger(availableNow=True).start().awaitTermination()\nproduce(1000, 500)\n# same query, same checkpoint', sec('== 1)', '== 2)')),
     'Run 1 read the 1,000 events as batch 0. After 500 more events, the restarted query ran only <b>batch 1</b> with the new rows: 1,500 rows in the sink and <b>1,500 distinct</b> order ids. No duplicates and nothing missed.'),
    ('Step 2 · Inside the checkpoint',
     code('python', 'l95_checkpoint.py', 'for d in sorted(os.listdir(CK + "/files")): print(d, os.listdir(…))\nprint(open(CK + "/files/offsets/1").read().splitlines()[-1])', sec('== 2)', '== 3)')),
     '<code>offsets/1</code> was written <b>before</b> batch 1 ran: “read partition 0 up to 762 and partition 1 up to 738”. <code>commits/1</code> was written after it succeeded. If a crash happens between the two, Spark replays batch 1 with exactly those offsets. The Parquet sink keeps its own log (<code>_spark_metadata/0</code>, <code>1</code>) to skip a batch it already wrote.'),
    ('Step 3 · A crash inside foreachBatch',
     code('python', 'l95_checkpoint.py', 'def fb(df, bid):\n    rows = df.count()\n    if kind == "append": store["append"].append((bid, rows))      # INSERT\n    else:                store["idempotent"][bid] = rows          # upsert by batch_id\n    if bid == 1 and first_attempt:\n        raise RuntimeError("simulated crash after writing batch 1")\n# maxOffsetsPerTrigger=600 → batches of 599, 599, 302; start, crash, start again', sec('== 3)', '== 4)')),
     'Both sinks wrote batch 1 and then “crashed” before Spark could commit it. On restart Spark <b>replayed batch 1</b> (same id, same 599 rows). The append sink now has batch 1 twice: <b>2,099 rows for 1,500 orders</b>, exactly the finance bug. The idempotent sink stored by <code>batch_id</code>, so the replay overwrote itself: <b>1,500</b>. In a database, use MERGE/upsert or delete-then-insert by batch id in one transaction.'),
    ('Step 4 · Deduplicating with state (RocksDB)',
     code('python', 'l95_checkpoint.py', 'spark.conf.set("spark.sql.streaming.stateStore.providerClass",\n               "org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider")\nproduce(0, 300)      # the producer re-sends 300 old orders\nded = events.withWatermark("timestamp", "10 minutes").dropDuplicatesWithinWatermark(["order_id"])', sec('== 4)', '== 5)')),
     'Producers retry, so Kafka often contains duplicates. 1,800 events came in, <b>1,500 unique orders</b> came out: each order id is remembered in the state store and later copies are dropped. With the watermark, ids older than 10 minutes are forgotten, so state stays bounded. RocksDB keeps state off the JVM heap, the usual choice for millions of keys.'),
    ('Step 5 · Changing a stateful query',
     code('python', 'l95_checkpoint.py', 'agg1 = stream().groupBy((F.col("order_id") % 3).alias("k")).count()                    # run once\nagg2 = stream().groupBy((F.col("order_id") % 3).cast("string").alias("k")).count()   # same checkpoint', sec('== 5)')),
     'The state store holds keys with the old schema (a long). The new query’s key is a string, so restarting on the same checkpoint failed with <b>STATE_STORE_<wbr>KEY_SCHEMA_<wbr>NOT_COMPATIBLE</b> as soon as a batch ran. Changing stateful logic means a new checkpoint (and usually reprocessing from the source), so plan it like a migration.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('run 1: batches [0], rows 1000', W), ('run 2: batches [1], rows 1500', G), ('distinct order_id: 1500', G)], size=7.4),
    term([('commits [0, 1]  offsets [0, 1]', W), ('offsets/1: {"pay":{"0":762,"1":738}}', Y), ('sink log: [0, 1]', W)], size=7.0),
    term([('append: (0,599) (1,599) (1,599) (2,302)', RD), ('  -> 2099 rows for 1500', RD), ('idempotent: -> 1500 rows', G)], size=7.0),
    term([('dedup: 1800 in -> 1500 out', G), ('state rows 1500 (RocksDB)', G), ('key type changed:', W), ('STATE_STORE_KEY_SCHEMA_NOT_COMPATIBLE', RD)], size=6.8),
]
B1 = [
    t(180, 14, 'Restart = read the logs', 9.4, bold=True) + flow([('offsets/0', 'committed', 'green'), ('offsets/1', 'new data', 'blue'), ('commit 1', 'done', 'green')], y=50, w=96, gap=16) + cap('Continue after the last commit.', '', 'green', y=144, h=30),
    t(180, 14, 'Write-ahead, then commit', 9.4, bold=True) + ckdir(20, 36, hi=0) + cap('Offsets first, commit last.', '', 'blue', y=144, h=30),
    t(180, 14, 'Crash between write and commit', 9.4, bold=True) + flow([('write', 'batch 1', 'blue'), ('crash', 'no commit', 'red'), ('replay', 'batch 1 again', 'amber')], y=50, w=96, gap=16) + t(180, 110, 'append → duplicate · upsert by batch_id → safe', 7.2, 'ink2') + cap('The sink decides.', '', 'amber', y=144, h=30),
    t(180, 14, 'State lives in the checkpoint', 9.4, bold=True) + ckdir(20, 36, hi=2) + cap('Key schema must not change.', '', 'red', y=144, h=30),
]
see_caps = ['Restart.', 'Checkpoint contents.', 'Replay after a crash.', 'State: dedup and schema.']
behind_caps = ['Resuming from commits.', 'Offsets and commits.', 'Why sinks must be idempotent.', 'State store rules.']
two = anim_two('Checkpoints and exactly-once', 'What survives a crash', 'Real lab outputs', 'What Spark does', see, B1, see_caps, behind_caps)

e1 = (t(180, 22, 'Totals higher than the lake', 9.4, bold=True) + t(180, 56, 'difference = one batch', 8.4, 'ink2') + cap('After a 2 a.m. restart.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'foreachBatch did INSERT', 9.4, bold=True) + t(180, 56, 'batch replayed after crash', 8.4, 'ink2') + cap('2,099 for 1,500 in our lab.', '', 'red', y=150, h=34))
e3 = (t(180, 22, 'Key rows by batch_id', 9.4, bold=True) + t(180, 56, 'delete batch_id, then insert', 8.4, 'ink2') + cap('One transaction.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Or MERGE on business key', 9.4, bold=True) + t(180, 56, 'order_id / city + window', 8.4, 'ink2') + cap('Upsert.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Replays are harmless', 9.4, 'acc', bold=True) + t(180, 56, '1,500 = 1,500', 8.4, 'ink2') + cap('Exactly-once end to end.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'The duplicated batch',
              'Idempotent foreachBatch. (Typical; numbers from our lab.)',
              'Idempotent sink', 'Make foreachBatch writes idempotent with batch_id or MERGE so replays do not duplicate', [e1, e2, e3, e4, e5],
              ['Mismatch.', 'Replay.', 'batch_id.', 'MERGE.', 'Safe.'],
              hid='scenario-idempotent')
b1 = (t(180, 22, 'Payment events retried', 9.4, bold=True) + t(180, 56, 'same order_id sent 2–3 times', 8.4, 'ink2') + cap('Kafka has duplicates.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'dropDuplicates(order_id)', 9.4, bold=True) + t(180, 56, 'without watermark: state forever', 8.4, 'ink2') + cap('Grows without bound.', '', 'red', y=150, h=34))
b3 = (t(180, 22, 'WithinWatermark version', 9.4, bold=True) + t(180, 56, 'forget ids after 10 min', 8.4, 'ink2') + cap('Bounded state.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'RocksDB state store', 9.4, bold=True) + t(180, 56, 'millions of keys off-heap', 8.4, 'ink2') + cap('No GC pressure.', '', 'green', y=150, h=34))
b5 = (t(180, 22, '1,800 in, 1,500 out', 9.4, 'acc', bold=True) + t(180, 56, 'our lab', 8.4, 'ink2') + cap('Duplicates removed.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Retries everywhere',
              'Streaming deduplication. (Typical; numbers from our lab.)',
              'Dedup', 'dropDuplicatesWithinWatermark removes retried events with bounded state', [b1, b2, b3, b4, b5],
              ['Retries.', 'Unbounded.', 'Watermark.', 'RocksDB.', 'Result.'],
              hid='scenario-dedup')
u1 = (t(180, 22, 'Add a column to the groupBy', 9.4, bold=True) + t(180, 56, 'deploy, restart on old ckpt', 8.4, 'ink2') + cap('Job fails.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'STATE_STORE_KEY_SCHEMA_…', 9.4, bold=True) + t(180, 56, 'state written with old keys', 8.4, 'ink2') + cap('Incompatible.', '', 'red', y=150, h=34))
u3 = (t(180, 22, 'New checkpoint: ck/v2', 9.4, bold=True) + t(180, 56, 'new output path too', 8.4, 'ink2') + cap('Version both.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Backfill from the source', 9.4, bold=True) + t(180, 56, 'within Kafka retention', 8.4, 'ink2') + cap('Rebuild state.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Switch readers to v2', 9.4, 'acc', bold=True) + t(180, 56, 'then retire v1', 8.4, 'ink2') + cap('Planned migration.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Upgrading a stateful query',
              'Checkpoint compatibility. (Typical; error from our lab.)',
              'Migration', 'Incompatible stateful changes need a new checkpoint, output path and backfill', [u1, u2, u3, u4, u5],
              ['Change.', 'Error.', 'v2.', 'Backfill.', 'Switch.'],
              hid='scenario-migrate')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>What survives a crash</h2>
  <p>Left: real outputs. Right: how checkpoints and sinks give exactly-once.</p>
''' + two + '''
  <p>Three live scenarios follow: a duplicated batch, retried events, and upgrading a stateful query.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Reliable streaming at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'money', 12, 'blue', bold=True) + t(60, 58, 'exactly-once', 7.4, 'ink2'),
    '1. Payments and finance',
    'Totals are upserted by batch id or business key so restarts never double-count.',
    ['Payments', '*idempotent MERGE', 'Correct totals']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'dedup', 12, 'green', bold=True) + t(60, 58, 'events', 7.4, 'ink2'),
    '2. Event deduplication',
    'Retried app events are deduplicated within a watermark before analytics.',
    ['Raw events', '*dedup within watermark', 'Unique events']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'RocksDB', 10, 'violet', bold=True) + t(60, 58, 'big state', 7.4, 'ink2'),
    '3. Large state',
    'Per-user features over millions of users run on the RocksDB state store.',
    ['Users', '*RocksDB', 'Stable memory']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'deploy', 11, 'acc', bold=True) + t(60, 58, 'versions', 7.4, 'ink2'),
    '4. Safe deployments',
    'Checkpoint paths carry a version; incompatible changes go to v2 with a backfill.',
    ['New logic', '*ck/v2', 'Backfill']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'DR', 12, 'acc', bold=True) + t(60, 58, 'storage', 7.4, 'ink2'),
    '5. Durable checkpoints',
    'Checkpoints live on S3/ADLS/HDFS so a new driver on any node can resume.',
    ['Driver dies', '*same checkpoint', 'Resume']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> sources, sinks and foreachBatch in <a href="../02-sources-and-sinks/">9.2</a>, watermarks in <a href="../03-output-modes-event-time-and-watermarks/">9.3</a>, RDD checkpointing in <a href="../../03-persistence-and-shared-variables/03-checkpointing-and-fault-tolerance/">3.3</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
