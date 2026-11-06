import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='08-performance-tuning', lesson='02-join-strategies', n='8.2',
    module_label='Module 8 · Performance tuning',
    title='Join strategies',
    desc='Spark join strategies measured with PySpark 4.3.0: 5M orders joined to 4,000 customers with broadcast, shuffle_hash, merge and shuffle_replicate_nl hints (1.55 s, 4.53 s, 6.73 s, CartesianProduct), Exchange counts in the plan, forcing a broadcast of a 5M-row side, and bucketed tables that sort-merge join with zero shuffles (1.68 s vs 5.31 s).',
    og_desc='Broadcast 1.55 s, sort-merge 6.73 s, bucketed 1.68 s: the same Spark join with every strategy, measured and explained.',
    minutes=30, level='Intermediate → Advanced',
    lead='The same join can be 4x faster or slower depending on the <b>physical strategy</b>. This lesson forces broadcast hash, shuffled hash and sort-merge joins with hints, counts shuffles in the plan, tests a dangerous forced broadcast, and removes the shuffle with <b>bucketing</b>. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', '4 join hints', 'Bucketing measured', 'Runs in your browser (Python)'],
)

MAIN = '''# How Spark picks a join strategy (simplified)
def choose(small_mb, threshold_mb=10, equi=True, hint=None):
    if hint:
        return hint
    if not equi:
        return "BroadcastNestedLoopJoin" if small_mb <= threshold_mb else "CartesianProduct"
    if threshold_mb >= 0 and small_mb <= threshold_mb:
        return "BroadcastHashJoin"
    return "SortMergeJoin"

print(choose(0.06))                    # 4,000 customers
print(choose(0.06, threshold_mb=-1))   # broadcast disabled
print(choose(800))                     # big dimension
print(choose(800, hint="ShuffledHashJoin"))
'''
RUN = dict(
    heading='Run the code: choosing a join',
    intro='<p>A simplified version of Spark’s join selection. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    if threshold_mb >= 0 and small_mb <= threshold_mb:', 'autoBroadcastJoinThreshold: 10 MB by default, -1 disables it.'),
        ('    return "SortMergeJoin"', 'spark.sql.join.preferSortMergeJoin=true makes this the default for big sides.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then raise the threshold to 1000 for the 800 MB side.', code=None),
        dict(label='2 · Predict first: shuffles', hint='<b>Predict first:</b> how many sides are shuffled per strategy?',
             code='''shuffles = {"BroadcastHashJoin": 0, "ShuffledHashJoin": 2, "SortMergeJoin": 2, "bucketed SMJ": 0}
for k, v in shuffles.items():
    print(f"{k:18} {v}")
'''),
        dict(label='3 · Broadcast cost', hint='Memory used by a broadcast on 200 executors.',
             code='''side_mb, executors = 300, 200
print(side_mb * executors / 1024, "GB of executor memory in total")
'''),
        dict(label='4 · Buckets that match', hint='Which bucket of customers does order bucket 3 need?',
             code='''buckets = 16
for cid in (3, 19, 35):
    print(cid, "-> bucket", cid % buckets)
'''),
        dict(label='5 · Spot the error', hint='A broadcast hint on a side that grew to 12 GB.', expect='error',
             code='''side_gb = 12
assert side_gb < 8, "Spark cannot broadcast tables larger than 8 GB (and the driver usually dies first)"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: join strategies',
    intro='<p>In the <code>pyspark</code> shell. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Threshold', cmd='spark.conf.get("spark.sql.autoBroadcastJoinThreshold")', file='pyspark',
             output="'10485760b'", note='10 MB.'),
        dict(title='2 · Hint', cmd='o.join(cust.hint("shuffle_hash"), "customer_id").explain()', file='pyspark',
             output='+- ShuffledHashJoin [customer_id], [customer_id], Inner, BuildRight', note='Build side = hashed side.'),
        dict(title='3 · SQL hint', cmd='spark.sql("SELECT /*+ BROADCAST(c) */ * FROM o JOIN c USING (customer_id)").explain()', file='pyspark',
             output='+- BroadcastHashJoin [customer_id], [customer_id], Inner, BuildRight, false', note='Same as F.broadcast.'),
    ],
)

TRACE = dict(
    heading='A hash join in miniature',
    intro='<p>Build a hash table from the small side, probe it with the big side.</p>',
    code='''small = [(1, "Gold"), (2, "Silver")]
big = [(101, 1), (102, 2), (103, 1)]
table = {}
for k, v in small:
    table[k] = v
out = []
for oid, k in big:
    out.append((oid, table[k]))
print(out)
''',
    notes={3: 'Build :: Small side becomes a hash table.', 6: 'Probe :: Each big-side row looks up its key.'},
)

WORKED_INTRO = 'Three join decisions at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='Joins · basics', title='Will it broadcast?',
         problem='<p>A restaurants table is 6 MB on disk. Default settings.</p>',
         inp='6 MB, 10 MB threshold',
         approach=['Compare estimate to threshold.', 'Parquet size underestimates memory.', 'Check the plan.'],
         code='''print("BroadcastHashJoin" if 6 <= 10 else "SortMergeJoin")
''', notes={1: 'Estimate :: Based on file size statistics.'},
         tryit='Step 1.'),
    dict(level='i', tag='Joins · hints', title='Choose a hint',
         problem='<p>A 2 GB dim joins a 2 TB fact; executors have 8 GB.</p>',
         inp='2 GB vs 2 TB',
         approach=['2 GB per executor is too much to broadcast safely.', 'Shuffled hash avoids the sort.', 'Or sort-merge if memory is tight.'],
         code='''dim_gb, exec_gb = 2, 8
print("shuffle_hash" if dim_gb < exec_gb * 0.1 * 50 else "merge")
''', notes={2: 'Per partition :: SHJ needs one partition of the small side in memory.'},
         tryit='Step 2.'),
    dict(level='a', tag='Joins · bucketing', title='Is bucketing worth it?',
         problem='<p>A 500 GB join runs 24 times a day.</p>',
         inp='shuffle 10 min each',
         approach=['Bucketing costs one shuffle at write time.', 'Saves the shuffle on every join.', 'Compare.'],
         code='''write_once, saved_per_run, runs = 15, 10, 24
print("saves", saved_per_run * runs - write_once, "minutes per day")
''', notes={1: 'Trade-off :: Only for repeated joins on the same key.'},
         tryit='Step 5.'),
]

QUIZ = mix([
    dict(q='Beginner: Which join avoids shuffling the big table?', options=['Sort-merge', 'Broadcast hash', 'Shuffled hash', 'Cartesian'], answer=1,
         why='Small side copied.'),
    dict(q='Beginner: Default autoBroadcastJoinThreshold?', options=['1 MB', '10 MB', '100 MB', '1 GB'], answer=1,
         why='-1 disables.'),
    dict(q='Beginner: DataFrame broadcast hint?', options=['df.cache()', 'F.broadcast(df)', 'df.persist()', 'df.repartition()'], answer=1,
         why='Or df.hint("broadcast").'),
    dict(q='Intermediate: Lab timings broadcast vs sort-merge?', options=['Same', '1.55 s vs 6.73 s', '6.73 s vs 1.55 s', '10 s vs 1 s'], answer=1,
         why='4.3x.'),
    dict(q='Intermediate: How many hash Exchanges in a sort-merge join plan?', options=['0', '1', '2', '200'], answer=2,
         why='One per side.'),
    dict(q='Intermediate: Bucketed tables joined on the bucket key…', options=['Need 2 shuffles', 'Need no shuffle', 'Are broadcast', 'Fail'], answer=1,
         why='0 Exchanges, 1.68 s.'),
    dict(q='Advanced: Risk of broadcasting a big side?', options=['None', 'Driver OOM / broadcast timeout', 'Wrong results', 'More shuffles'], answer=1,
         why='Collected on the driver.'),
    dict(q='Advanced: shuffle_replicate_nl on an equi-join gave…', options=['BHJ', 'SMJ', 'CartesianProduct', 'SHJ'], answer=2,
         why='Avoid for equi-joins.'),
])

REVISION = [
    'BHJ: copy small side, no shuffle of the big side (1.55 s).',
    'SMJ: shuffle + sort both (6.73 s); SHJ: shuffle + hash (4.53 s).',
    'Threshold 10 MB; -1 disables broadcast globally (dangerous).',
    'Hints: broadcast, merge, shuffle_hash, shuffle_replicate_nl; SQL <code>/*+ BROADCAST(t) */</code>.',
    'Count <code>Exchange hashpartitioning</code> nodes to see shuffles.',
    'Forced broadcasts of big sides risk driver OOM and timeouts.',
    'Bucketing on the join key: SMJ with 0 Exchanges (1.68 s vs 5.31 s).',
]
FAQ = [
    ('Which side should be broadcast?', 'The smaller side after filters, and for outer joins only the side that is allowed to be the build side (for a left join, the right side).'),
    ('Why did Spark not broadcast a 6 MB Parquet table?', 'Size estimates use statistics; in memory the data may be much larger, or a filter or UDF may make the estimate unknown. Check the plan, use AQE or a hint.'),
    ('Is shuffled hash join better than sort-merge?', 'Often faster because it skips the sort, but each partition of the build side must fit in memory. Spark 4 picks it more often when preferSortMergeJoin is false or a hint is given.'),
    ('Does bucketing work with plain Parquet paths?', 'No, the bucket spec lives in the catalog; read it as a table with spark.table.'),
    ('What is a storage-partitioned join?', 'A V2 data source feature (e.g. Iceberg) where tables partitioned the same way are joined without a shuffle, similar to bucketing.'),
]

PRACTICE_INTRO = 'Programs about join strategies.'
PROBLEMS = [
    dict(level='easy', title='Speed-up', stmt='Broadcast vs sort-merge.', inp='1.55 vs 6.73 s',
         code='''print(round(6.73 / 1.55, 1))
''', explain='4.3x.'),
    dict(level='easy', title='Broadcast check', stmt='Broadcast a 25 MB side by default?', inp='10 MB',
         code='''print(25 <= 10)
''', explain='No, unless hinted or threshold raised.'),
    dict(level='easy', title='Bucket of a key', stmt='Bucket for customer 37 in 16 buckets (simplified).', inp='37',
         code='''print(37 % 16)
''', explain='Spark uses Murmur3 hash, same idea.'),
    dict(level='medium', title='Broadcast memory', stmt='Total memory for a 200 MB broadcast on 150 executors.', inp='200 MB',
         code='''print(200 * 150 / 1024, "GB")
''', explain='Each executor holds a copy.'),
    dict(level='medium', title='Shuffle volume', stmt='Data shuffled by SMJ vs BHJ.', inp='fact 400 GB, dim 50 MB',
         code='''print("SMJ:", 400 + 0.05, "GB | BHJ: 0 GB (+ broadcast)")
''', explain='The big side dominates.'),
    dict(level='medium', title='Pick strategy', stmt='Write the decision rule.', inp='sizes',
         code='''def pick(small_mb):
    return "broadcast" if small_mb <= 10 else "sort-merge"
print([pick(s) for s in (1, 9, 50)])
''', explain='Simplified.'),
    dict(level='business', title='Daily saving', stmt='Minutes saved per day with broadcast.', inp='5.18 s × 2,000 runs',
         code='''print(round(5.18 * 2000 / 60), "minutes")
''', explain='Small joins run often.'),
    dict(level='business', title='Bucketing ROI', stmt='Break-even runs for bucketing.', inp='write 15 min, save 10 min/run',
         code='''import math
print(math.ceil(15 / 10), "runs")
''', explain='Pays off after two joins.'),
]

SCN_INTRO = 'Join strategy questions are a favourite in Spark interviews.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“What is a broadcast join?”',
        'Explain broadcast joins.',
        'when used?',
        '<p>Spark sends the small table to every executor and builds a hash table, so the large table is joined where it sits without a shuffle. It is used automatically below <code>autoBroadcastJoinThreshold</code> (10 MB) or with <code>F.broadcast</code>. In my test it was 4.3x faster than sort-merge.</p>', 'Broadcasting large tables.') +
    scn('Data engineering', 'Mid-level', 'Slow dimension join',
        'Joining orders to a 5 MB city table takes 10 minutes.',
        'what do you check?',
        '''<ul>
          <li>The plan: SortMergeJoin with two Exchanges?</li>
          <li>The threshold setting (maybe -1) and size estimates.</li>
          <li>Add a broadcast hint or rely on AQE; verify BroadcastHashJoin.</li>
        </ul>''', 'Adding executors.') +
    scn('Data engineering', 'Mid-level', 'Broadcast OOM',
        'A job fails with driver OutOfMemory during a broadcast.',
        'fix?',
        '''<ol>
          <li>Find which side is broadcast; its real size grew.</li>
          <li>Remove the hint or lower the threshold for that query.</li>
          <li>Use shuffled hash or sort-merge for that join.</li>
        </ol>''', 'Raising driver memory forever.') +
    scn('Platform', 'Senior', 'Repeated big joins',
        'Two 1 TB tables are joined on the same key 20 times a day.',
        'design?',
        '''<ul>
          <li>Bucket (or cluster/partition the same way in Iceberg/Delta) both on the key.</li>
          <li>Verify zero Exchanges in the join plan.</li>
          <li>Keep bucket counts aligned as data grows.</li>
        </ul>''', 'Relying on more shuffle partitions only.')
)
