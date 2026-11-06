import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='08-performance-tuning', lesson='03-data-skew-and-salting', n='8.3',
    module_label='Module 8 · Performance tuning',
    title='Data skew and salting',
    desc='Data skew measured with PySpark 4.3.0 on 6M orders where one restaurant has 60%: task duration and shuffle records from the Spark REST API for a skewed window (one task read 3.9M rows), a groupBy saved by partial aggregation, a skewed join, a salted join with exploded salts, AQE skew-join splitting (max task 2.8 s to 1.3 s), and isolating the hot key (17.2 s to 10.8 s).',
    og_desc='One restaurant, 60% of orders, one task doing all the work: Spark data skew measured and fixed with salting, AQE and hot-key isolation.',
    minutes=32, level='Intermediate → Advanced',
    lead='A stage is only as fast as its slowest task. This lesson creates a <b>hot key</b> holding 60% of orders, measures the straggler in task metrics, shows why groupBy survives it, and fixes joins and windows with <b>salting</b>, AQE skew joins and hot-key isolation. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', 'Task metrics via REST', 'Salting measured', 'Runs in your browser (Python)'],
)

MAIN = '''# Salting a hot key: rows per task before and after (simplified)
import random
random.seed(1)
rows = [1] * 600 + [k for k in range(2, 402)]      # key 1 holds 60%
P, S = 8, 16                                       # reduce tasks, salts

def tasks(keys):
    t = [0] * P
    for k in keys:
        t[hash(k) % P] += 1
    return t

print("plain :", tasks(rows))
salted = [(k, random.randrange(S)) for k in rows]
print("salted:", tasks(salted))
'''
RUN = dict(
    heading='Run the code: salting a hot key',
    intro='<p>See how adding a salt spreads one hot key across tasks. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('rows = [1] * 600 + [k for k in range(2, 402)]      # key 1 holds 60%', 'Same shape as the lab: one restaurant with 60% of orders.'),
        ('salted = [(k, random.randrange(S)) for k in rows]', 'The key becomes (key, salt), so key 1 hashes to up to 16 different tasks.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then set S = 2 and S = 64.', code=None),
        dict(label='2 · Predict first: skew ratio', hint='<b>Predict first:</b> max ÷ median records from the lab window stage.',
             code='''mx, med = 3897000, 287000
print(round(mx / med, 1), "x")
'''),
        dict(label='3 · Replication cost', hint='Salting copies the other side S times.',
             code='''menu_rows, S = 400000, 16
print(menu_rows * S, "rows on the replicated side")
'''),
        dict(label='4 · Two-stage aggregation', hint='Aggregate by (key, salt), then by key.',
             code='''from collections import Counter
import random
rows = [("r1", 5)] * 6 + [("r2", 3)] * 2
stage1 = Counter()
for k, v in rows:
    stage1[(k, random.randrange(3))] += v
final = Counter()
for (k, s), v in stage1.items():
    final[k] += v
print(dict(final))
'''),
        dict(label='5 · Spot the error', hint='The salted join forgot to explode the small side.', expect='error',
             code='''orders = [("r1", 3)]                 # (key, salt)
menu = [("r1", 0)]                   # salt only 0, not 0..S-1
matches = [o for o in orders if o in menu]
assert matches, "rows with salt != 0 found no match: explode the small side over all salts"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: skew',
    intro='<p>In the <code>pyspark</code> shell. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Find hot keys', cmd='o.groupBy("rest_id").count().orderBy(F.desc("count")).show(3)', file='pyspark',
             output='+-------+-------+\n|rest_id|  count|\n+-------+-------+\n|      1|3600000|\n|     51|   1500|\n|     71|   1500|\n+-------+-------+', note='One key, 60%.'),
        dict(title='2 · Salt', cmd='ms = menu.withColumn("salt", F.explode(F.sequence(F.lit(0), F.lit(15))))\nms.count()', file='pyspark',
             output='6400000', note='400,000 × 16.'),
        dict(title='3 · Same result', cmd='j.count() == js.count()', file='pyspark',
             output='True', note='Salting must not change the answer.'),
    ],
)

TRACE = dict(
    heading='Salted join, step by step',
    intro='<p>Watch one order meet its menu item through a salt.</p>',
    code='''S = 3
order = ("r1", 2)
menu = [("r1", s) for s in range(S)]
match = [m for m in menu if m == order]
print(match)
''',
    notes={2: 'Big side :: Random salt 2.', 3: 'Small side :: One copy per salt.', 4: 'Exactly one :: Each order matches once.'},
)

WORKED_INTRO = 'Three skew problems at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='Skew · detect', title='Is this stage skewed?',
         problem='<p>Task summary: median 30 s, max 40 min.</p>',
         inp='Spark UI task summary',
         approach=['Compute max ÷ median.', 'Above ~5 is skew.', 'Check shuffle read per task.'],
         code='''print(round(40 * 60 / 30), "x")
''', notes={1: 'Ratio :: 80x: badly skewed.'},
         tryit='Step 1.'),
    dict(level='i', tag='Skew · salt', title='Choose the salt count',
         problem='<p>The hot partition is 12 GB; others ~400 MB.</p>',
         inp='12 GB vs 400 MB',
         approach=['S ≈ hot ÷ typical.', 'Cap it; replication cost grows with S.', 'Salt only the hot keys.'],
         code='''import math
print(min(math.ceil(12 * 1024 / 400), 64))
''', notes={1: 'Cap :: Very high S replicates the other side too much.'},
         tryit='Step 4.'),
    dict(level='a', tag='Skew · distinct', title='Skewed countDistinct',
         problem='<p><code>countDistinct(customer_id)</code> per restaurant is slow for the hot restaurant.</p>',
         inp='60% hot key',
         approach=['Stage 1: distinct (rest, customer).', 'Stage 2: count per rest.', 'Or approx_count_distinct.'],
         code='''pairs = {("r1", c) for c in [1, 2, 2, 3]} | {("r2", 9)}
from collections import Counter
print(Counter(r for r, c in pairs))
''', notes={1: 'Distinct first :: The shuffle carries pairs, not lists.'},
         tryit='Two-stage aggregation.'),
]

QUIZ = mix([
    dict(q='Beginner: Data skew means…', options=['Corrupt data', 'Uneven rows per key/partition', 'Too many columns', 'Slow disks'], answer=1,
         why='One task does most work.'),
    dict(q='Beginner: Where do you see skew?', options=['Driver logs only', 'Spark UI task summary: max ≫ median', 'df.schema', 'spark.conf'], answer=1,
         why='Duration and shuffle read.'),
    dict(q='Beginner: Does adding executors fix one hot key?', options=['Yes', 'No, one task runs on one core', 'Only with cache', 'Only in SQL'], answer=1,
         why='Spread the key instead.'),
    dict(q='Intermediate: Why did groupBy sum not suffer?', options=['AQE', 'Partial aggregation before the shuffle', 'Broadcast', 'Luck'], answer=1,
         why='~800 records per task.'),
    dict(q='Intermediate: In a salted join, the small side is…', options=['Filtered', 'Exploded over all salt values', 'Broadcast', 'Sorted'], answer=1,
         why='Each copy has one salt.'),
    dict(q='Intermediate: Salting cost?', options=['None', 'The other side grows S times', 'Wrong results', 'More stages always'], answer=1,
         why='Choose S carefully.'),
    dict(q='Advanced: AQE skew join applies to…', options=['All aggregations', 'Sort-merge/shuffled hash joins over thresholds', 'Windows', 'Broadcast joins'], answer=1,
         why='5x median and 256 MB by default.'),
    dict(q='Advanced: A window over a hot key…', options=['Is fixed by salting directly', 'Needs the hot key handled separately or two-stage', 'Is always fast', 'Uses AQE skew join'], answer=1,
         why='A rank needs all rows of a key.'),
])

REVISION = [
    'Skew: hot key → one huge task; stage waits for it.',
    'Detect: task summary max vs median; lab 5.5 s vs 0.7 s, 3.9M vs 0.28M records.',
    'Sums/counts are protected by partial aggregation (max task 73 ms).',
    'Salted join: rand salt on big side, explode 0..S-1 on small side, join on (key, salt).',
    'Salting multiplies the other side by S; salt only hot keys when possible.',
    'AQE skew join split the hot partition: max 2.8 s → 1.3 s.',
    'Windows: isolate the hot key (17.2 s → 10.8 s); filter NULL/default keys.',
]
FAQ = [
    ('How do I find the hot keys?', 'groupBy(key).count().orderBy(desc("count")).show(); or approx with sample(). Also check NULLs and default values.'),
    ('Is salting still needed with AQE?', 'Less often. AQE handles skewed joins above its thresholds; salting remains useful for aggregations like collect_list, windows, and joins AQE does not split (for example some outer joins).'),
    ('What salt count should I use?', 'Roughly the ratio of the hot partition to a normal one, capped (often 8–64), and only for hot keys.'),
    ('Does broadcast avoid skew?', 'Yes for the join itself: the big side is not shuffled, so its hot key stays spread across input partitions.'),
    ('Can skew cause OOM?', 'Yes: the hot task may need more memory than an executor has, leading to heavy spill or OutOfMemoryError (Lesson 8.4).'),
]

PRACTICE_INTRO = 'Programs about skew detection and salting.'
PROBLEMS = [
    dict(level='easy', title='Skew ratio', stmt='max ÷ min records in the window stage.', inp='3897000, 279000',
         code='''print(round(3897000 / 279000, 1))
''', explain='14x.'),
    dict(level='easy', title='Hot share', stmt='Share of the hot key.', inp='3.6M of 6M',
         code='''print(3.6 / 6 * 100, "%")
''', explain='60%.'),
    dict(level='easy', title='Salted rows', stmt='Replicated side size.', inp='400,000 × 16',
         code='''print(400000 * 16)
''', explain='6.4M rows.'),
    dict(level='medium', title='Salt key', stmt='Write a salted key.', inp='key, S',
         code='''import random
S = 8
print([("r1", random.randrange(S)) for _ in range(5)])
''', explain='F.rand() * S in Spark.'),
    dict(level='medium', title='Detect skew', stmt='Flag tasks > 5x median.', inp='durations',
         code='''import statistics
d = [700, 900, 800, 5500, 850]
m = statistics.median(d)
print([x for x in d if x > 5 * m])
''', explain='Same rule as AQE.'),
    dict(level='medium', title='Two-stage sum', stmt='Sum by (key, salt) then key.', inp='rows',
         code='''from collections import defaultdict
s1 = defaultdict(int)
for i, (k, v) in enumerate([("a", 1)] * 6 + [("b", 2)]):
    s1[(k, i % 3)] += v
s2 = defaultdict(int)
for (k, _), v in s1.items():
    s2[k] += v
print(dict(s2))
''', explain='Same answer, spread work.'),
    dict(level='business', title='Idle cores', stmt='Core-minutes wasted by a 40-min straggler on 200 cores.', inp='others done in 1 min',
         code='''print(199 * 39, "core-minutes")
''', explain='Skew is expensive.'),
    dict(level='business', title='Lab saving', stmt='Saving from isolating the hot key.', inp='17.22 vs 10.77 s',
         code='''print(round((17.22 - 10.77) / 17.22 * 100), "%")
''', explain='About 37% here; more on a cluster.'),
]

SCN_INTRO = 'Skew is one of the most asked Spark tuning topics.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“What is data skew?”',
        'Explain skew and its effect.',
        'symptom?',
        '<p>Some keys have far more rows than others, so after a shuffle one partition is huge. Its task runs much longer than the rest and the whole stage waits for it; in the Spark UI the max task time is far above the median.</p>', 'Confusing skew with too little memory in general.') +
    scn('Data engineering', 'Mid-level', 'Salting',
        'Explain salting for a skewed join.',
        'steps?',
        '''<ol>
          <li>Add salt = rand() × S (int) to the skewed side.</li>
          <li>Explode the other side over salts 0..S-1.</li>
          <li>Join on (key, salt) and drop salt; result is unchanged.</li>
        </ol>''', 'Salting both sides randomly (rows never match).') +
    scn('Data engineering', 'Mid-level', 'Skewed aggregation',
        'collect_list per user fails for a bot user.',
        'fix?',
        '''<ul>
          <li>Filter or cap bot users.</li>
          <li>Two-stage aggregation on (user, salt).</li>
          <li>Avoid collecting huge lists; aggregate instead.</li>
        </ul>''', 'Raising executor memory only.') +
    scn('Platform', 'Senior', 'Skew at scale',
        'Design skew handling for a marketplace platform.',
        'approach?',
        '''<ul>
          <li>AQE skew join on with tuned thresholds; monitor max/median ratios.</li>
          <li>Hot-key lists maintained from data stats; salt only those.</li>
          <li>Data quality checks for NULL/default keys.</li>
        </ul>''', 'Salting every join by default.')
)
