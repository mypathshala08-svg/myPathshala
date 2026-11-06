import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='08-performance-tuning', lesson='01-partitions-and-shuffle-partitions', n='8.1',
    module_label='Module 8 · Performance tuning',
    title='Partitions and shuffle partitions',
    desc='Spark partitions measured with PySpark 4.3.0 on 5M orders: how maxPartitionBytes and cores decide input partitions, 2,000 small files vs 8 files (4.06 s vs 0.20 s), a groupBy with 1 to 2,000 shuffle partitions (best 1.82 s, worst 8.13 s, AQE coalesced 200 to 8 tasks), rows per partition for repartition, repartition by column and coalesce, and the coalesce(1) trap.',
    og_desc='2,000 shuffle partitions made a groupBy 4.5x slower; 2,000 small files made a read 20x slower. Partition sizing in Spark, measured.',
    minutes=30, level='Intermediate → Advanced',
    lead='Every partition is a task. This lesson measures how Spark picks input partitions, what 2,000 small files cost, the U-shaped curve of <code>spark.sql.shuffle.partitions</code>, and how <code>repartition</code> and <code>coalesce</code> place rows. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', '1 → 2,000 partitions', 'Small files measured', 'Runs in your browser (Python)'],
)

MAIN = '''# How many shuffle partitions? (simplified sizing rule)
shuffle_gb = 300            # shuffle write size seen in the Spark UI
target_mb = 128             # aim per task
cores = 200                 # executor cores in the cluster

by_size = shuffle_gb * 1024 // target_mb
by_cores = cores * 3        # at least 2-3 tasks per core
print("by size :", by_size)
print("by cores:", by_cores)
print("use     :", max(by_size, by_cores))
'''
RUN = dict(
    heading='Run the code: sizing shuffle partitions',
    intro='<p>A simple rule of thumb used by many teams. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('by_size = shuffle_gb * 1024 // target_mb', 'Enough partitions that each task handles about 128 MB.'),
        ('by_cores = cores * 3        # at least 2-3 tasks per core', 'Small data still needs enough tasks to keep every core busy.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then try a 2 GB shuffle: which rule wins?', code=None),
        dict(label='2 · Predict first: input splits', hint='<b>Predict first:</b> 34.6 MB on 4 cores with a 128 MB cap. How many splits?',
             code='''import math
total_mb, cores, cap_mb = 34.6, 4, 128
split = min(cap_mb, max(4, total_mb / cores))
print(math.ceil(total_mb / split), "partitions of", round(split, 1), "MB")
'''),
        dict(label='3 · Small files', hint='2,000 files of 17 KB, each charged 4 MB open cost.',
             code='''files, size_mb, open_mb = 2000, 0.017, 4
split_mb = 128
per_task = split_mb // (size_mb + open_mb)
print("files per task ~", int(per_task), "-> tasks ~", round(files / per_task))
'''),
        dict(label='4 · Hash collisions', hint='8 cities into 8 buckets: how many buckets are used?',
             code='''cities = ["Mumbai", "Pune", "Delhi", "Thane", "Chennai", "Hyderabad", "Bengaluru", "Navi Mumbai"]
buckets = {}
for c in cities:
    buckets.setdefault(sum(map(ord, c)) % 8, []).append(c)
print(len(buckets), "of 8 used:", buckets)
'''),
        dict(label='5 · Spot the error', hint='A job sets 2,000 shuffle partitions for 200 MB of shuffle.', expect='error',
             code='''shuffle_mb, parts = 200, 2000
assert shuffle_mb / parts >= 32, f"{shuffle_mb / parts:.2f} MB per task: overhead dominates (8.13 s vs 1.82 s in the lab)"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: partitions',
    intro='<p>In the <code>pyspark</code> shell (<code>pyspark --master local[4]</code>). <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Input partitions', cmd='spark.read.parquet("orders_big").rdd.getNumPartitions()', file='pyspark',
             output='4', note='34.6 MiB spread over 4 cores.'),
        dict(title='2 · Shuffle default', cmd='spark.conf.get("spark.sql.shuffle.partitions")', file='pyspark',
             output="'200'", note='AQE may merge them.'),
        dict(title='3 · Rows per partition', cmd='o.repartition(8, "city").groupBy(F.spark_partition_id()).count().count()', file='pyspark',
             output='6', note='Two buckets empty.'),
    ],
)

TRACE = dict(
    heading='Packing files into partitions',
    intro='<p>Follow Spark packing files into splits.</p>',
    code='''files = [3, 3, 3, 9, 1]
cap = 10
parts, cur = [], 0
for f in files:
    if cur + f > cap:
        parts.append(cur); cur = 0
    cur += f
parts.append(cur)
print(parts)
''',
    notes={2: 'Cap :: maxPartitionBytes (sizes in MB).', 5: 'Full :: Start a new partition.', 9: 'Result :: Fewer tasks than files.'},
)

WORKED_INTRO = 'Three partition decisions at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='Partitions · basics', title='How many tasks will this read run?',
         problem='<p>A table has 40 files of 300 MB each. Default settings.</p>',
         inp='12 GB, 128 MB cap',
         approach=['Each file splits at 128 MB.', '300 MB → 3 splits.', 'Multiply by files.'],
         code='''import math
print(40 * math.ceil(300 / 128), "tasks")
''', notes={1: 'Splittable :: Parquet files split at row-group boundaries.'},
         tryit='Step 1.'),
    dict(level='i', tag='Partitions · shuffle', title='Pick shuffle partitions',
         problem='<p>A join shuffles 80 GB on a 100-core cluster.</p>',
         inp='80 GB, 100 cores',
         approach=['80 GB ÷ 128 MB.', 'Compare with 3 × cores.', 'Take the larger.'],
         code='''by_size = 80 * 1024 // 128
print(max(by_size, 100 * 3))
''', notes={1: 'Size :: 640 tasks of ~128 MB.'},
         tryit='Step 3.'),
    dict(level='a', tag='Partitions · output', title='One file per date folder',
         problem='<p>Writing <code>partitionBy("order_date")</code> creates 200 files per date.</p>',
         inp='200 tasks × 30 dates',
         approach=['Each task writes one file per date it holds.', 'repartition by order_date first.', 'Now each date is in one task.'],
         code='''tasks, dates = 200, 30
print("before:", tasks * dates, "files | after:", dates, "files")
''', notes={2: 'Fix :: df.repartition("order_date").write.partitionBy("order_date")'},
         tryit='Lesson 5.3.'),
]

QUIZ = mix([
    dict(q='Beginner: One partition is processed by…', options=['One executor', 'One task', 'One job', 'One stage'], answer=1,
         why='One task on one core.'),
    dict(q='Beginner: Default spark.sql.shuffle.partitions?', options=['8', '64', '200', 'Number of cores'], answer=2,
         why='AQE can merge them.'),
    dict(q='Beginner: Which one avoids a shuffle?', options=['repartition', 'coalesce', 'orderBy', 'groupBy'], answer=1,
         why='coalesce only merges.'),
    dict(q='Intermediate: 2,000 small files vs 8 files, same rows. Lab result?', options=['Same speed', '4.06 s vs 0.20 s', 'Small files faster', 'Error'], answer=1,
         why='Per-file overhead.'),
    dict(q='Intermediate: groupBy with 2,000 shuffle partitions vs 16?', options=['Faster', '8.13 s vs 1.82 s', 'Same', 'Fails'], answer=1,
         why='Overhead of 2,004 tasks.'),
    dict(q='Intermediate: repartition(8, "city") with 8 cities gave…', options=['8 equal partitions', '6 used, uneven', '1 partition', '16'], answer=1,
         why='Hash collisions.'),
    dict(q='Advanced: Why can coalesce(1) be dangerous?', options=['It shuffles', 'Upstream work runs in a single task', 'It drops rows', 'It caches'], answer=1,
         why='No stage boundary.'),
    dict(q='Advanced: 34.6 MiB with a 16 MB cap on 4 cores gave 4 partitions because…', options=['A bug', 'Spark also spreads input over cores (≈8.7 MB each)', 'Files are not splittable', 'Cache'], answer=1,
         why='min(cap, max(openCost, size ÷ cores)).'),
])

REVISION = [
    'Partition = task = one core at a time.',
    'Input splits: <code>maxPartitionBytes</code> (128 MB), <code>openCostInBytes</code> (4 MB), cores.',
    'Small files: 2,000 files 4.06 s vs 8 files 0.20 s.',
    'Shuffle partitions: U-curve; 16 → 1.82 s, 2,000 → 8.13 s; AQE 200 → 8 tasks.',
    'Aim for ~128 MB per task and 2–3 tasks per core.',
    '<code>repartition(n, col)</code> hashes; low cardinality = uneven or empty partitions.',
    '<code>coalesce(1)</code> pulls upstream work into one task; prefer <code>repartition(1)</code> after heavy work.',
]
FAQ = [
    ('Should I always change spark.sql.shuffle.partitions?', 'Set it high enough for your biggest shuffle and let AQE coalesce it; on small data the default 200 with AQE is fine.'),
    ('What is a good task duration?', 'Usually from a few seconds to a few minutes. Many tasks under 100 ms mean too many partitions; tasks of tens of minutes mean too few or skew.'),
    ('Does repartition before a write help?', 'Yes, when you need fewer, bigger files or one file per output folder; it costs one shuffle.'),
    ('Why does getNumPartitions differ from the files count?', 'Spark splits big files and packs small ones together into splits.'),
    ('How does this work on Databricks?', 'Same settings; Databricks also offers auto-optimized shuffle and auto compaction on Delta tables.'),
]

PRACTICE_INTRO = 'Programs about partition sizing.'
PROBLEMS = [
    dict(level='easy', title='Tasks per core', stmt='Tasks per core for 200 partitions on 16 cores.', inp='200, 16',
         code='''print(200 / 16)
''', explain='12.5 waves of tasks.'),
    dict(level='easy', title='Small-file slowdown', stmt='How many times slower?', inp='4.06 vs 0.20 s',
         code='''print(round(4.06 / 0.20))
''', explain='About 20x.'),
    dict(level='easy', title='Shuffle slowdown', stmt='2,000 vs 16 partitions.', inp='8.13 vs 1.82 s',
         code='''print(round(8.13 / 1.82, 1))
''', explain='4.5x.'),
    dict(level='medium', title='Partitions by size', stmt='Partitions for a 50 GB shuffle at 128 MB.', inp='50 GB',
         code='''print(50 * 1024 // 128)
''', explain='400 tasks.'),
    dict(level='medium', title='Balance check', stmt='Max/median rows per partition.', inp='repartition(8, city)',
         code='''import statistics
p = [498646, 500086, 500552, 998365, 1000215, 1502136]
print(round(max(p) / statistics.median(p), 2))
''', explain='Above 2 means a slow straggler.'),
    dict(level='medium', title='Files written', stmt='Files from 200 tasks writing 30 dates.', inp='partitionBy',
         code='''print(200 * 30)
''', explain='Repartition by the column first.'),
    dict(level='business', title='Compaction saving', stmt='Seconds saved per day for 500 reads.', inp='3.86 s per read',
         code='''print(round(500 * 3.86 / 60), "minutes")
''', explain='Compaction pays for itself.'),
    dict(level='business', title='Idle cores', stmt='Core-minutes wasted by coalesce(1) on 100 cores for 40 min.', inp='99 idle',
         code='''print(99 * 40, "core-minutes")
''', explain='Use repartition(1) after the heavy step.'),
]

SCN_INTRO = 'Partition sizing comes up in nearly every Spark performance interview.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“repartition vs coalesce?”',
        'Explain the difference.',
        'shuffle?',
        '<p><code>repartition(n)</code> does a full shuffle and can increase or decrease partitions, giving even partitions (or hashed by a column). <code>coalesce(n)</code> merges existing partitions without a shuffle and can only decrease them; it may leave them uneven and can pull upstream work into fewer tasks.</p>', 'Saying coalesce is always better because it avoids a shuffle.') +
    scn('Data engineering', 'Mid-level', 'Thousands of tiny tasks',
        'A job’s stages each show 2,000 tasks of 20 ms.',
        'what to change?',
        '''<ul>
          <li>Lower shuffle partitions to fit data size, or rely on AQE coalescing.</li>
          <li>Check input file counts; compact small files.</li>
          <li>In my test 2,000 → 16 partitions took 8.13 s → 1.82 s.</li>
        </ul>''', 'Adding executors.') +
    scn('Data engineering', 'Mid-level', 'Small files',
        'Reads of a table are slow although it is only 30 GB.',
        'diagnose?',
        '''<ol>
          <li>Count files and average file size.</li>
          <li>Compact into 128 MB–1 GB files (repartition + overwrite, or OPTIMIZE).</li>
          <li>Fix the writer: repartition by partition columns before writing.</li>
        </ol>''', 'Increasing maxPartitionBytes only.') +
    scn('Platform', 'Senior', 'Default settings',
        'Set partition defaults for 300 batch jobs.',
        'strategy?',
        '''<ul>
          <li>AQE on with a 64–256 MB advisory size; shuffle partitions sized for the biggest jobs.</li>
          <li>Writers produce right-sized files; compaction for streaming outputs.</li>
          <li>Dashboards on task duration and file size distributions.</li>
        </ul>''', 'One hand-tuned number per job.')
)
