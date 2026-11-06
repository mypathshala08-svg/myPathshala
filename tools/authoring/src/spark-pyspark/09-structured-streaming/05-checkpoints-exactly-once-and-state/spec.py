import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='09-structured-streaming', lesson='05-checkpoints-exactly-once-and-state', n='9.5',
    module_label='Module 9 · Structured Streaming',
    title='Checkpoints, exactly-once and state',
    desc='Fault tolerance in Structured Streaming with PySpark 4.3.0 and Kafka 3.9: restarting a Kafka query from its checkpoint (only the 500 new rows read), the offsets and commits logs, a simulated crash inside foreachBatch where a plain append wrote 2,099 rows for 1,500 orders and an idempotent batch_id write kept 1,500, deduplicating 1,800 events to 1,500 with dropDuplicatesWithinWatermark on the RocksDB state store, and STATE_STORE_KEY_SCHEMA_NOT_COMPATIBLE after changing a grouping key.',
    og_desc='We crashed a Spark stream on purpose: a plain append wrote 2,099 rows for 1,500 orders; an idempotent sink kept 1,500. Checkpoints and exactly-once, explained.',
    minutes=32, level='Intermediate → Advanced',
    lead='Exactly-once in streaming needs three things: a replayable source, a checkpoint and an idempotent sink. This lesson restarts a Kafka query, opens its checkpoint, <b>crashes a sink on purpose</b> with and without idempotent writes, deduplicates replays with <b>RocksDB state</b>, and breaks a checkpoint by changing the query. <b>All outputs are real</b> (PySpark 4.3.0, Kafka 3.9).',
    chips=['PySpark 4.3.0', 'Crash simulated', 'RocksDB state', 'Runs in your browser (Python)'],
)

MAIN = '''# Why a replayed batch duplicates an append sink (simplified)
batches = {0: 599, 1: 599, 2: 302}
committed = set()
append_sink, idempotent_sink = [], {}
crashed = False

def run_batch(bid):
    global crashed
    rows = batches[bid]
    append_sink.append((bid, rows))      # INSERT
    idempotent_sink[bid] = rows          # upsert by batch_id
    if bid == 1 and not crashed:
        crashed = True
        raise RuntimeError("crash before commit")
    committed.add(bid)

for attempt in (1, 2):
    try:
        for bid in batches:
            if bid not in committed:
                run_batch(bid)
    except RuntimeError as e:
        print("attempt", attempt, "failed:", e)

print("append    :", sum(r for _, r in append_sink), "rows")
print("idempotent:", sum(idempotent_sink.values()), "rows")
'''
RUN = dict(
    heading='Run the code: replay after a crash',
    intro='<p>The lab’s crash in miniature. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    committed.add(bid)', 'The commit log is written only after the sink has finished; a crash before it means a replay.'),
        ('    idempotent_sink[bid] = rows          # upsert by batch_id', 'Keyed by batch id, a replay overwrites instead of adding.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>: 2,099 vs 1,500, as in the lab.', code=None),
        dict(label='2 · Predict first: restart', hint='<b>Predict first:</b> batches 0–1 committed, 2 not. What runs on restart?',
             code='''committed, planned = {0, 1}, [0, 1, 2]
print([b for b in planned if b not in committed])
'''),
        dict(label='3 · Dedup', hint='Remove retried order ids.',
             code='''events = [1, 2, 3, 2, 1, 4]
seen, out = set(), []
for e in events:
    if e not in seen:
        seen.add(e); out.append(e)
print(out, "state:", seen)
'''),
        dict(label='4 · Offsets', hint='Rows in batch 1 from the offsets log.',
             code='''b0 = {"0": 503, "1": 497}          # offsets/0 from the lab
b1 = {"0": 762, "1": 738}
print(sum(b1[p] - b0[p] for p in b1), "rows")
'''),
        dict(label='5 · Spot the error', hint='Changing the grouping key type on an old checkpoint.', expect='error',
             code='''old_key, new_key = "long", "string"
assert old_key == new_key, "STATE_STORE_KEY_SCHEMA_NOT_COMPATIBLE: use a new checkpoint"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: checkpoints',
    intro='<p>After running the lab’s file-sink query twice. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Checkpoint folders', cmd='ls ck95/files', file='bash',
             output='commits  metadata  offsets  sources', note='state/ appears for stateful queries.'),
        dict(title='2 · Offsets of batch 1', cmd='tail -1 ck95/files/offsets/1', file='bash',
             output='{"pay":{"0":762,"1":738}}', note='Per partition.'),
        dict(title='3 · Sink log', cmd='ls out95/_spark_metadata', file='bash',
             output='0  1', note='Committed batches of the file sink.'),
    ],
)

TRACE = dict(
    heading='Restart logic',
    intro='<p>How Spark decides what to run after a restart.</p>',
    code='''offsets = [0, 1, 2]
commits = [0, 1]
last_commit = max(commits)
todo = [b for b in offsets if b > last_commit]
print("replay:", todo)
''',
    notes={1: 'WAL :: Batches planned.', 2: 'Commits :: Batches finished.', 4: 'Replay :: Same offsets, same batch id.'},
)

WORKED_INTRO = 'Three reliability decisions at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='Checkpoint · basics', title='Where should the checkpoint live?',
         problem='<p>The driver runs on a node that may be replaced.</p>',
         inp='cluster storage options',
         approach=['Not local disk.', 'HDFS / S3 / ADLS / GCS.', 'One path per query.'],
         code='''path = "s3://tiffingo-streams/checkpoints/city_rev/v1"
print(path.startswith(("s3://", "abfss://", "hdfs://", "gs://")))
''', notes={1: 'Version :: v1 in the path for future migrations.'},
         tryit='Step 2.'),
    dict(level='i', tag='Exactly-once · sink', title='Make a JDBC sink idempotent',
         problem='<p>foreachBatch inserts city totals into PostgreSQL.</p>',
         inp='batch_id',
         approach=['Delete rows of this batch_id.', 'Insert the batch.', 'Same transaction.'],
         code='''sql = ["BEGIN", "DELETE FROM city_rev WHERE batch_id = :b", "INSERT ... batch_id = :b", "COMMIT"]
print("; ".join(sql))
''', notes={2: 'Replay-safe :: A second run replaces the first.'},
         tryit='Step 3.'),
    dict(level='a', tag='State · migration', title='Change a stateful query',
         problem='<p>Add <code>zone</code> to the grouping keys.</p>',
         inp='running query',
         approach=['Key schema changes → incompatible.', 'New checkpoint + output path.', 'Backfill within retention, switch readers.'],
         code='''steps = ["deploy v2 with ck/v2", "startingOffsets=earliest", "validate", "switch readers", "stop v1"]
print(" → ".join(steps))
''', notes={1: 'Plan :: Treat as a migration.'},
         tryit='Step 5.'),
]

QUIZ = mix([
    dict(q='Beginner: What does the checkpoint store?', options=['Only data', 'Offsets, commits and state', 'Logs', 'Jars'], answer=1,
         why='Plus metadata.'),
    dict(q='Beginner: Restart with the same checkpoint reads…', options=['Everything again', 'Only uncommitted/new data', 'Nothing', 'Random data'], answer=1,
         why='Batch 1 only, 500 rows.'),
    dict(q='Beginner: Is the file sink exactly-once?', options=['No', 'Yes, via _spark_metadata', 'Only with Kafka', 'Only in complete mode'], answer=1,
         why='Skips committed batches.'),
    dict(q='Intermediate: Crash after writing, before commit. Spark…', options=['Skips the batch', 'Replays it with the same batch id', 'Fails forever', 'Loses data'], answer=1,
         why='Write-ahead log.'),
    dict(q='Intermediate: Plain append in foreachBatch gives…', options=['Exactly-once', 'At-least-once (2,099 for 1,500)', 'At-most-once', 'Nothing'], answer=1,
         why='Make it idempotent.'),
    dict(q='Intermediate: Deduplicate with bounded state using…', options=['distinct()', 'dropDuplicatesWithinWatermark', 'cache()', 'repartition'], answer=1,
         why='Needs a watermark.'),
    dict(q='Advanced: Changing grouping key type on an old checkpoint…', options=['Works', 'Fails: state key schema not compatible', 'Silently resets', 'Drops state'], answer=1,
         why='New checkpoint needed.'),
    dict(q='Advanced: Why RocksDB state store?', options=['Faster SQL', 'Large state off the JVM heap', 'Needed for Kafka', 'Exactly-once'], answer=1,
         why='Less GC pressure.'),
])

REVISION = [
    'Checkpoint: offsets (WAL), commits, state, sources, metadata.',
    'Restart replays uncommitted batches with the same offsets and batch id.',
    'Exactly-once = replayable source + checkpoint + idempotent sink.',
    'Crash lab: append 2,099 rows for 1,500; batch_id upsert 1,500.',
    '<code>dropDuplicatesWithinWatermark</code>: 1,800 → 1,500 with bounded state.',
    'RocksDB state store for large state.',
    'Stateful schema changes need a new checkpoint (STATE_STORE_KEY_SCHEMA_NOT_COMPATIBLE).',
]
FAQ = [
    ('Can I delete old checkpoint files?', 'Spark cleans old batch files itself (spark.sql.streaming.minBatchesToRetain); never delete them by hand.'),
    ('Is the Kafka sink exactly-once?', 'No, at-least-once; consumers should deduplicate (e.g. by key) or use idempotent processing.'),
    ('Can two queries share a checkpoint?', 'No; each query needs its own location.'),
    ('How do I inspect state?', 'Spark has a state data source: spark.read.format("statestore").load(checkpointPath) for debugging.'),
    ('What is transformWithState?', 'A newer API (Spark 4) for arbitrary stateful processing with timers and TTL, replacing flatMapGroupsWithState for many cases.'),
]

PRACTICE_INTRO = 'Programs about checkpoints, replays and state.'
PROBLEMS = [
    dict(level='easy', title='Duplicate rows', stmt='Extra rows from replaying batch 1.', inp='2099 vs 1500',
         code='''print(2099 - 1500)
''', explain='599 = batch 1.'),
    dict(level='easy', title='New rows', stmt='Rows read on restart.', inp='1500 − 1000',
         code='''print(1500 - 1000)
''', explain='Only new data.'),
    dict(level='easy', title='Duplicates removed', stmt='Events dropped by dedup.', inp='1800, 1500',
         code='''print(1800 - 1500)
''', explain='300 retries.'),
    dict(level='medium', title='Replay set', stmt='Batches to replay.', inp='offsets 0..4, commits 0..2',
         code='''print([b for b in range(5) if b > 2])
''', explain='[3, 4].'),
    dict(level='medium', title='Idempotent write', stmt='Upsert by batch_id.', inp='writes',
         code='''sink = {}
for bid, rows in [(0, 599), (1, 599), (1, 599), (2, 302)]:
    sink[bid] = rows
print(sum(sink.values()))
''', explain='1,500.'),
    dict(level='medium', title='Dedup', stmt='Unique ids in order.', inp='events',
         code='''print(list(dict.fromkeys([5, 3, 5, 9, 3])))
''', explain='Keep first.'),
    dict(level='business', title='Overstated revenue', stmt='Revenue overstated by one replayed batch.', inp='599 orders × ₹250',
         code='''print("₹", 599 * 250)
''', explain='Why idempotency matters.'),
    dict(level='business', title='Backfill window', stmt='Can v2 backfill 5 days with 7-day retention?', inp='5, 7',
         code='''print(5 <= 7)
''', explain='Yes, migrate before retention runs out.'),
]

SCN_INTRO = 'Exactly-once and checkpoint questions separate senior streaming candidates.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“What is a checkpoint in streaming?”',
        'Explain checkpoints.',
        'what is inside?',
        '<p>A directory on durable storage where the query saves the offsets each batch will read (write-ahead log), which batches committed, and state for stateful operators. On restart Spark resumes from it, replaying any uncommitted batch.</p>', 'Confusing it with RDD checkpointing only.') +
    scn('Data engineering', 'Mid-level', 'Duplicate rows after restart',
        'A database sink shows duplicated rows after a crash.',
        'why and fix?',
        '''<ul>
          <li>Batch replayed after crash; foreachBatch did plain inserts.</li>
          <li>Upsert / delete+insert by batch_id or MERGE on business key.</li>
          <li>In my lab: 2,099 rows for 1,500 → fixed to 1,500.</li>
        </ul>''', 'Blaming Kafka.') +
    scn('Data engineering', 'Mid-level', 'Retried events',
        'Producers resend events; counts are inflated.',
        'approach?',
        '''<ol>
          <li>dropDuplicatesWithinWatermark on the event id.</li>
          <li>Watermark sized to the retry window.</li>
          <li>RocksDB state store for many keys.</li>
        </ol>''', 'dropDuplicates without a watermark (unbounded state).') +
    scn('Platform', 'Senior', 'Stateful upgrades',
        'How do you deploy a change to a stateful streaming job?',
        'process?',
        '''<ul>
          <li>Classify the change: compatible or not.</li>
          <li>Incompatible: new checkpoint + output version, backfill, switch readers.</li>
          <li>Versioned checkpoint paths and runbooks.</li>
        </ul>''', 'Deleting the checkpoint and restarting.')
)
