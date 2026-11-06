import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
BODY = body(HERE)

META = dict(
    module='03-persistence-and-shared-variables', lesson='03-checkpointing-and-fault-tolerance', n='3.3',
    module_label='Module 3 · Persistence and shared variables',
    title='Checkpointing and fault tolerance',
    desc='How Spark survives failures and when to checkpoint, measured with PySpark 4.3.0: a lineage growing to 92 lines through unions and cut to 2 by a checkpoint, the extra job that computes an uncached RDD twice (20,000 vs 10,000 calls), localCheckpoint, a 400-step DataFrame loop going from 9.9 s to 5.7 s with periodic checkpoints, and a worker stopped on the cluster: a cached RDD recomputed 200,000 expensive calls while a checkpointed one recomputed none.',
    og_desc='We stopped a worker twice: the cached RDD redid 200,000 expensive calls, the checkpointed one redid none. Checkpointing and fault tolerance, measured.',
    minutes=34, level='Intermediate → Advanced',
    lead='Spark recovers from failures by recomputing from lineage, but recomputation can be slow and lineages can grow too long. This lesson shows when a <b>checkpoint</b> helps, what it costs, and how it compares with a cache when a worker really disappears on our cluster. <b>All outputs are real</b> (Spark 4.3.0).',
    chips=['Spark 4.3.0 cluster', 'Worker killed: cache vs checkpoint', 'Lineage 92 → 2 lines', 'Runs in your browser (Python)'],
)

MAIN = '''# Recovery cost after losing half the executors: cache vs checkpoint (lab numbers)
partitions, lost = 8, 4
calls_per_partition = 50_000          # expensive() calls to build one partition
read_s_per_partition = 0.1            # reading a checkpoint file (approx.)

for strategy in ("cache only", "cache + checkpoint"):
    if strategy == "cache only":
        extra_calls = lost * calls_per_partition
    else:
        extra_calls = 0
    print(f"{strategy:20} extra expensive calls after the loss: {extra_calls:,}")
'''
RUN = dict(
    heading='Run the code: what recovery costs',
    intro='<p>A model of Step 6: 8 partitions, 4 lost with a worker. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('        extra_calls = lost * calls_per_partition', 'Cached blocks are lost with the executor and rebuilt from lineage: 200,000 calls in our lab.'),
        ('        extra_calls = 0', 'Checkpoint files on shared storage are simply read again.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then make each call ten times more expensive: does the answer change?', code=None),
        dict(label='2 · Predict first: twice computed', hint='<b>Predict first:</b> checkpoint() on an uncached RDD of 10,000 elements. How many work() calls?',
             code='''elements = 10_000
print("no cache  :", elements * 2, "(action + checkpoint job)")
print("with cache:", elements)
'''),
        dict(label='3 · Lineage growth', hint='Lines in toDebugString after n unions (about 3 per union, as in the lab).',
             code='''base = 2
for n in (10, 30, 100):
    print(n, "unions ->", base + 3 * n, "lines")
'''),
        dict(label='4 · When to checkpoint a loop', hint='Checkpoint every k steps: count checkpoints and maximum plan length.',
             code='''steps, k = 400, 50
print("checkpoints:", steps // k, "| longest plan between them:", k, "steps")
'''),
        dict(label='5 · Spot the error', hint='This plan uses localCheckpoint on spot nodes for a 6-hour job.', expect='error',
             code='''plan = {"method": "localCheckpoint", "nodes": "spot", "hours": 6}
assert not (plan["method"] == "localCheckpoint" and plan["nodes"] == "spot"), "local checkpoints die with executors: use checkpoint() on reliable storage"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: checkpoints',
    intro='<p>In the <code>pyspark</code> shell. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Checkpoint an RDD', cmd='sc.setCheckpointDir("ckpt")\nr.checkpoint(); r.count()\nr.isCheckpointed(), r.getCheckpointFile()', file='pyspark',
             output="(True, 'file:/…/ckpt/<uuid>/rdd-62')", note='The uuid folder belongs to this SparkContext.'),
        dict(title='2 · The cut lineage', cmd='print(r.toDebugString().decode())', file='pyspark',
             output='(34) UnionRDD[62] at union at DirectMethodHandleAccessor.java:103 []\n |   ReliableCheckpointRDD[64] at count at l33_ckpt.py:20 []', note='92 lines before the checkpoint.'),
        dict(title='3 · Checkpoint a DataFrame', cmd='df = df.checkpoint()           # eager by default\nlen(df._jdf.queryExecution().analyzed().toString().splitlines())', file='pyspark',
             output='1', note='The plan becomes a single scan of the checkpoint.'),
    ],
)

TRACE = dict(
    heading='What Spark reads after a lost executor',
    intro='<p>Follow how a partition is obtained in each strategy.</p>',
    code='''lost = {"p4", "p5", "p6", "p7"}
def get(p, strategy):
    if p not in lost:
        return "cached block"
    if strategy == "checkpoint":
        return "checkpoint file"
    return "recompute from lineage"
for s in ("cache", "checkpoint"):
    print(s, [get(p, s) for p in ("p0", "p4")])
''',
    notes={3: 'Alive :: Partitions on surviving executors are still cached.', 5: 'Checkpoint :: Files on reliable storage survive executor loss.', 7: 'Lineage :: Without a checkpoint, the parent RDDs are recomputed.'},
)

WORKED_INTRO = 'Three fault-tolerance decisions from real pipelines.'
EXAMPLES = [
    dict(level='b', tag='Reliability · basics', title='Checkpoint correctly',
         problem='<p>Checkpoint an expensive RDD without computing it twice.</p>',
         inp='scores RDD',
         approach=['Set a reliable checkpoint dir.', 'cache(), then checkpoint().', 'Trigger with an action.'],
         code='''print("""sc.setCheckpointDir("hdfs:///checkpoints/fraud/2026-11-04")
scores = orders.map(score).cache()
scores.checkpoint()
scores.count()""")
''', notes={2: 'Order :: cache before checkpoint so the checkpoint job reads the cache.'},
         tryit='Step 3: 20,000 vs 10,000 calls.'),
    dict(level='i', tag='Performance · loops', title='Checkpoint a long loop',
         problem='<p>A DataFrame is built in 400 steps and gets slower each step.</p>',
         inp='loop of withColumn / union',
         approach=['Checkpoint every n steps.', 'Measure plan length.', 'Prefer select with many columns at once.'],
         code='''steps, every = 400, 50
cuts = [i + 1 for i in range(0, steps, every)][1:] + [steps]
# at each cut: df = df.checkpoint()
print(len(cuts), "checkpoints at", cuts[:3], "...")
print("lab: 9.9 s -> 5.7 s")
''', notes={3: 'Alternative :: Building many columns in one select avoids the long plan entirely.'},
         tryit='Lesson 4.3 shows select vs withColumn chains.'),
    dict(level='a', tag='Architecture · reliability', title='Choose recovery per stage',
         problem='<p>Plan recovery for a pipeline on spot nodes.</p>',
         inp='parse → score (expensive) → join → write',
         approach=['Cheap stages: rely on lineage.', 'Expensive stage: cache + checkpoint.', 'Final result: write a table.'],
         code='''plan = {"parse": "lineage", "score": "cache + checkpoint (S3)", "join": "lineage",
        "write": "table (Parquet/Delta)"}
for k, v in plan.items():
    print(f"{k:6} -> {v}")
''', notes={2: 'Expensive :: Only the step that would hurt to redo needs a checkpoint.'},
         tryit='Driver on on-demand nodes (Lesson 1.3).'),
]

QUIZ = mix([
    dict(q='Beginner: How does Spark mainly recover lost data?', options=['Replicas', 'Recomputing from lineage', 'Asking the user', 'From HDFS logs'], answer=1,
         why='Checkpoints add a second way.'),
    dict(q='Beginner: Where should the checkpoint directory be?', options=['Driver memory', 'Reliable storage such as HDFS or S3', 'Executor /tmp', 'Python list'], answer=1,
         why='It must survive executor loss.'),
    dict(q='Beginner: What does checkpoint() do to the lineage?', options=['Doubles it', 'Cuts it at the checkpoint', 'Nothing', 'Prints it'], answer=1,
         why='92 lines → 2 lines.'),
    dict(q='Intermediate: Why did checkpointing compute the RDD twice?', options=['Bug', 'The checkpoint is written by a separate job that recomputes uncached data', 'Two executors', 'AQE'], answer=1,
         why='cache() first: 10,000 calls.'),
    dict(q='Intermediate: What is localCheckpoint’s weakness?', options=['It is slow', 'Its data is lost with the executor', 'It writes to S3', 'It keeps the lineage'], answer=1,
         why='Lineage cut, but no reliable copy.'),
    dict(q='Intermediate: How many times does Spark retry a failed task by default?', options=['Never', 'Up to 4 attempts in total', '10', 'Forever'], answer=1,
         why='spark.task.maxFailures = 4.'),
    dict(q='Advanced: After a worker was stopped, how many extra expensive calls did the checkpointed RDD need?', options=['200,000', '400,000', '0', '1'], answer=2,
         why='It read the checkpoint files.'),
    dict(q='Advanced: Why did a 400-step DataFrame loop speed up with checkpoints?', options=['Less data', 'Catalyst no longer had to analyse a 400-node plan', 'More executors', 'Caching'], answer=1,
         why='9.9 s → 5.7 s.'),
])

REVISION = [
    'Fault tolerance: task retries (maxFailures 4), recompute lost shuffle output and cached blocks from <b>lineage</b>.',
    '<code>sc.setCheckpointDir()</code> on reliable storage; <code>checkpoint()</code> writes files and <b>cuts the lineage</b> (92 → 2 lines).',
    'RDD checkpoints are lazy and use an extra job: <b>cache first</b> (20,000 → 10,000 calls).',
    '<code>localCheckpoint()</code>: lineage cut, no files, not fault tolerant.',
    'DataFrame <code>checkpoint()</code> is eager and resets long plans (400 steps: 9.9 s → 5.7 s).',
    'Worker lost: cache-only recomputed 200,000 calls; checkpointed recomputed 0 (0.8 s).',
    'Checkpoint files are internal and not cleaned by default; write real outputs as tables.',
]
FAQ = [
    ('Is a checkpoint the same as saving a table?', 'No. A checkpoint is for the running application: internal format, tied to a SparkContext, used to cut lineage and speed up recovery. To share data with other jobs, write a table (Parquet, Delta, Iceberg).'),
    ('Does Structured Streaming use the same checkpoints?', 'It uses a checkpoint location for a different purpose: offsets, commits and state for exactly-once processing. That directory must never be deleted while the query is in use (Module 9).'),
    ('Should I always checkpoint?', 'No. A checkpoint costs a full write and, without cache, a recomputation. Use it for long lineages and expensive results on unreliable infrastructure.'),
    ('Can I read a checkpoint after restarting the application?', 'Not through the public RDD API in a new application; reliable checkpoints are meant for the application that wrote them. That is another reason to write tables for reuse.'),
    ('What is speculative execution?', 'With spark.speculation=true, Spark starts a copy of tasks that run much slower than others and uses whichever finishes first. It helps with slow nodes, not with failures.'),
]

PRACTICE_INTRO = 'Programs about lineage, checkpoints and recovery.'
PROBLEMS = [
    dict(level='easy', title='Lineage shrink', stmt='Percent shorter lineage after the checkpoint.', inp='92 → 2 lines',
         code='''print(f"{1 - 2 / 92:.0%}")
''', explain='The chain is replaced by a reference to files.'),
    dict(level='easy', title='Extra calls', stmt='Extra calls when checkpointing without cache.', inp='10,000 elements',
         code='''print(20000 - 10000)
''', explain='One full extra computation.'),
    dict(level='easy', title='Attempts', stmt='Maximum attempts for one task by default.', inp='spark.task.maxFailures',
         code='''print(4)
''', explain='After 4 failures the job is aborted.'),
    dict(level='medium', title='Lost work', stmt='Calls to recompute after losing executors.', inp='8 partitions, 3 lost, 50,000 calls each',
         code='''print(3 * 50_000)
''', explain='Zero with a reliable checkpoint.'),
    dict(level='medium', title='Checkpoint frequency', stmt='Pick a checkpoint interval for 120 iterations.', inp='at most 15 steps between checkpoints',
         code='''import math
print(math.ceil(120 / 15), "checkpoints")
''', explain='Balance write cost against lineage length.'),
    dict(level='medium', title='Recovery choice', stmt='Choose recovery for each dataset.', inp='cost and reuse',
         code='''for name, cost in {"parsed": "cheap", "scores": "expensive"}.items():
    print(name, "lineage" if cost == "cheap" else "cache + checkpoint")
''', explain='Checkpoint only what hurts to recompute.'),
    dict(level='business', title='Hours saved', stmt='Hours saved per incident by checkpointing scores.', inp='2 h recompute vs 5 min read, 6 incidents/month',
         code='''print(round((2 - 5 / 60) * 6, 1), "hours per month")
''', explain='On spot clusters incidents are frequent.'),
    dict(level='business', title='Checkpoint storage', stmt='Monthly storage if checkpoints are never deleted.', inp='300 GB per run, 30 runs',
         code='''print(300 * 30 / 1000, "TB")
''', explain='Add a lifecycle rule.'),
]

SCN_INTRO = 'Fault-tolerance questions show whether you know how Spark really recovers.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“How is Spark fault tolerant?”',
        'Explain Spark’s fault tolerance.',
        'do you know lineage and retries?',
        '<p>Failed tasks are retried; lost partitions, including shuffle output and cached data, are recomputed from lineage, the record of transformations. Checkpointing saves data to reliable storage and cuts the lineage so recovery reads files. In our test, a checkpointed RDD needed no recomputation after a worker was lost.</p>', '“Spark replicates all data three times like HDFS.”') +
    scn('Data engineering', 'Mid-level', 'Cache vs checkpoint',
        'When do you use cache, checkpoint, or both?',
        'can you choose by goal?',
        '''<ul>
          <li>Cache: reuse within the application, fast, lost with executors.</li>
          <li>Checkpoint: cut long lineages, make expensive results survive failures; extra write.</li>
          <li>Both: cache then checkpoint, so the checkpoint does not recompute.</li>
        </ul>''', 'Checkpointing every DataFrame.') +
    scn('Data engineering', 'Mid-level', 'Loop gets slower each iteration',
        'A loop building a DataFrame slows down and the driver uses lots of CPU.',
        'do you recognise plan growth?',
        '''<ol>
          <li>Each iteration adds nodes; Catalyst re-analyses a growing plan.</li>
          <li>Checkpoint every n iterations, or restructure into fewer, wider steps.</li>
          <li>Measure: our 400-step loop went from 9.9 to 5.7 s.</li>
        </ol>''', 'Adding executors (the driver is the bottleneck).') +
    scn('Platform', 'Senior', 'Recovery design on spot capacity',
        'Nightly jobs on spot nodes often finish hours late.',
        'can you design for failure?',
        '''<ul>
          <li>Driver on on-demand capacity; executors on spot.</li>
          <li>Checkpoint expensive intermediate results to S3/HDFS; enable decommissioning to migrate blocks.</li>
          <li>Write final results as tables; monitor recomputed tasks and stage retries.</li>
        </ul>''', 'Moving everything to on-demand without analysis.')
)
