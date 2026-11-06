import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='07-spark-sql', lesson='04-adaptive-query-execution', n='7.4',
    module_label='Module 7 · Spark SQL',
    title='Adaptive Query Execution',
    desc='Adaptive Query Execution measured with PySpark 4.3.0 on 5M orders: AQE off vs on for a groupBy (204 tasks, 1.74 s vs 5 tasks, 0.62 s) with AQEShuffleRead coalesced, a sort-merge join switched to a broadcast join at run time (0.89 s vs 0.05 s), and a join on a key holding 60% of rows (3.67 s off, 2.57 s with coalescing, 1.92 s with skew-join splitting and SortMergeJoin(skew=true)), plus the settings and thresholds that control it.',
    og_desc='AQE cut a groupBy from 204 tasks to 5 and split a 60% hot key: three runtime optimizations in Spark, measured off vs on.',
    minutes=28, level='Intermediate → Advanced',
    lead='Catalyst plans with estimates; <b>Adaptive Query Execution</b> corrects the plan while the query runs, using real sizes. This lesson turns AQE off and on to measure partition coalescing, runtime join switching and skew-join handling, and shows how to read the final plan. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', 'AQE off vs on', 'Skew split shown', 'Runs in your browser (Python)'],
)

MAIN = '''# How AQE coalesces shuffle partitions (simplified)
sizes_kb = [2, 0, 1, 3, 0, 0, 2, 1] * 25           # 200 tiny partitions after a shuffle
target_kb = 64 * 1024                              # advisoryPartitionSizeInBytes = 64 MB

groups, current = [], 0
for s in sizes_kb:
    if current + s > target_kb and current:
        groups.append(current); current = 0
    current += s
groups.append(current)
print("planned partitions:", len(sizes_kb))
print("after coalescing  :", len(groups), "partition(s) of", groups, "KB")
'''
RUN = dict(
    heading='Run the code: coalescing partitions',
    intro='<p>A simplified model of Step 1. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('target_kb = 64 * 1024                              # advisoryPartitionSizeInBytes = 64 MB', 'Adjacent small partitions are merged up to this size.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then make every partition 1 GB: how many groups?', code=None),
        dict(label='2 · Predict first: skew', hint='<b>Predict first:</b> is a partition skewed? (5x median and over 256 MB)',
             code='''import statistics
sizes_mb = [40, 35, 2000, 38, 42]
med = statistics.median(sizes_mb)
print([s for s in sizes_mb if s > 5 * med and s > 256])
'''),
        dict(label='3 · Split it', hint='Split a skewed partition into advisory-sized pieces.',
             code='''import math
print(math.ceil(2000 / 64), "tasks instead of 1")
'''),
        dict(label='4 · Switch the join', hint='Runtime size vs broadcast threshold.',
             code='''runtime_mb, threshold_mb = 0.2, 10
print("broadcast" if runtime_mb <= threshold_mb else "sort-merge")
'''),
        dict(label='5 · Spot the error', hint='This job turned AQE off to “make plans predictable”.', expect='error',
             code='''conf = {"spark.sql.adaptive.enabled": "false"}
assert conf["spark.sql.adaptive.enabled"] == "true", "AQE off: 204 tasks instead of 5, no runtime broadcast, no skew split"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: AQE',
    intro='<p>In the <code>pyspark</code> shell. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · On by default', cmd='spark.conf.get("spark.sql.adaptive.enabled"), spark.conf.get("spark.sql.shuffle.partitions")', file='pyspark',
             output="('true', '200')", note='200 is the starting point.'),
        dict(title='2 · Final plan', cmd='d = o.groupBy("city").agg(F.sum("amount")); d.collect()\nd._jdf.queryExecution().executedPlan().toString().splitlines()[0]', file='pyspark',
             output='AdaptiveSparkPlan isFinalPlan=true', note='Contains AQEShuffleRead coalesced.'),
        dict(title='3 · Skew', cmd='# after the skewed join with lowered thresholds', file='pyspark',
             output='+- *(5) SortMergeJoin(skew=true) [rest_id#131L], [rest_id#133L], Inner', note='Split partitions.'),
    ],
)

TRACE = dict(
    heading='Stages, statistics, re-planning',
    intro='<p>Follow AQE between two stages.</p>',
    code='''stage1_output_mb = 0.01
threshold_mb = 64
plan = {"reduce_partitions": 200}
if stage1_output_mb < threshold_mb:
    plan["reduce_partitions"] = 1
print(plan)
''',
    notes={1: 'Runtime :: Size known only after the map stage ran.', 5: 'Re-plan :: The rest of the query uses the real number.'},
)

WORKED_INTRO = 'Three AQE decisions on the TiffinGo platform.'
EXAMPLES = [
    dict(level='b', tag='AQE · basics', title='Check AQE is working',
         problem='<p>Confirm AQE coalesced a job’s shuffle.</p>',
         inp='a groupBy job',
         approach=['Run the action.', 'Look at the final plan.', 'Count reduce tasks in the UI.'],
         code='''plan = "AdaptiveSparkPlan isFinalPlan=true\\n+- AQEShuffleRead coalesced"
print("coalesced" in plan)
''', notes={1: 'Final :: Only after running.'},
         tryit='Step 1.'),
    dict(level='i', tag='AQE · tuning', title='Pick shuffle partitions with AQE',
         problem='<p>Set partitions for jobs between 1 GB and 1 TB of shuffle.</p>',
         inp='variable volumes',
         approach=['Partitions high enough for the largest day.', 'Advisory size ~64–256 MB.', 'Let AQE merge small days.'],
         code='''largest_gb, advisory_mb = 1000, 128
print("shuffle.partitions >=", int(largest_gb * 1024 / advisory_mb))
''', notes={2: 'Upper bound :: AQE can merge, not split (outside skew joins).'},
         tryit='Scenario 1.'),
    dict(level='a', tag='AQE · skew', title='Is the hot key handled?',
         problem='<p>A join is slow; one key dominates.</p>',
         inp='Spark UI task times',
         approach=['Look for skew=true in the final plan.', 'Check thresholds vs partition sizes.', 'Salt if still skewed.'],
         code='''part_mb, median_mb = 900, 60
print("AQE splits it" if part_mb > 5 * median_mb and part_mb > 256 else "below thresholds: tune or salt")
''', notes={1: 'Both conditions :: factor and absolute size.'},
         tryit='Step 3.'),
]

QUIZ = mix([
    dict(q='Beginner: What does AQE use to re-plan?', options=['Guesses', 'Real sizes from finished stages', 'User hints only', 'Logs'], answer=1,
         why='Runtime statistics.'),
    dict(q='Beginner: Is AQE on by default in Spark 4?', options=['No', 'Yes, since 3.2', 'Only on Databricks', 'Only for SQL'], answer=1,
         why='spark.sql.adaptive.enabled = true.'),
    dict(q='Beginner: Coalescing does what?', options=['Splits partitions', 'Merges small shuffle partitions', 'Caches', 'Compresses'], answer=1,
         why='204 → 5 tasks.'),
    dict(q='Intermediate: Static broadcast disabled, small side after a filter. With AQE…', options=['Stays SMJ', 'Switches to broadcast at run time', 'Fails', 'Uses cross join'], answer=1,
         why='0.89 → 0.05 s.'),
    dict(q='Intermediate: Default skew conditions?', options=['2x median', '> 5x median and > 256 MB', '> 1 GB', 'Any key > 10%'], answer=1,
         why='We lowered them for the lab.'),
    dict(q='Intermediate: How do you see what AQE did?', options=['explain() before running', 'The final plan after running / Spark UI', 'Logs only', 'Not possible'], answer=1,
         why='isFinalPlan=true.'),
    dict(q='Advanced: Does AQE skew handling fix skewed aggregations?', options=['Yes', 'No, it targets joins', 'Only sums', 'Only with Python'], answer=1,
         why='Use partial aggregation or salting.'),
    dict(q='Advanced: Plan text for a split join?', options=['BroadcastHashJoin', 'SortMergeJoin(skew=true)', 'CartesianProduct', 'HashAggregate'], answer=1,
         why='With AQEShuffleRead … skewed.'),
])

REVISION = [
    'AQE re-plans at run time from real stage sizes; on by default since 3.2.',
    'Coalescing: 204 tasks → 5, 1.74 → 0.62 s; plan <code>AQEShuffleRead coalesced</code>.',
    'Join switching: SMJ → broadcast when a side is measured small (0.89 → 0.05 s).',
    'Skew join: split big partitions (3.67 → 1.92 s), <code>SortMergeJoin(skew=true)</code>.',
    'Skew thresholds: 5× median and 256 MB by default; joins only.',
    'Read the final plan (<code>isFinalPlan=true</code>) after running or in the Spark UI.',
    'Set shuffle partitions high enough; tune the advisory size.',
]
FAQ = [
    ('Should I still set spark.sql.shuffle.partitions?', 'Yes, as an upper bound high enough for the biggest input; AQE merges partitions but does not create more (except when splitting skew).'),
    ('Does AQE work with caching?', 'Yes, and cached data provides statistics; very complex plans may limit re-optimization.'),
    ('Does AQE work in Structured Streaming?', 'Not for micro-batch streaming queries in general; it targets batch queries.'),
    ('Can AQE make things slower?', 'Rarely; e.g. coalescing to too few partitions for a later heavy stage. Tune the advisory size or minPartitionNum.'),
    ('What about dynamic partition pruning?', 'A separate optimization: filters from a dimension join prune partitions of a fact table at run time; it works together with AQE.'),
]

PRACTICE_INTRO = 'Programs about runtime re-optimization.'
PROBLEMS = [
    dict(level='easy', title='Tasks saved', stmt='Tasks saved by coalescing.', inp='204 vs 5',
         code='''print(204 - 5)
''', explain='Empty tasks cost scheduling time.'),
    dict(level='easy', title='Speed-up', stmt='Skew join speed-up.', inp='3.67 vs 1.92 s',
         code='''print(round(3.67 / 1.92, 1))
''', explain='About 1.9x.'),
    dict(level='easy', title='Broadcast check', stmt='Will AQE broadcast a 3 MB side?', inp='threshold 10 MB',
         code='''print(3 <= 10)
''', explain='Measured at run time.'),
    dict(level='medium', title='Coalesce count', stmt='Partitions after merging to 64 MB.', inp='shuffle 1,000 MB',
         code='''import math
print(math.ceil(1000 / 64))
''', explain='About 16 tasks.'),
    dict(level='medium', title='Skew test', stmt='Find skewed partitions.', inp='sizes in MB',
         code='''import statistics
s = [50, 60, 55, 900, 58]
m = statistics.median(s)
print([x for x in s if x > 5 * m and x > 256])
''', explain='Both conditions.'),
    dict(level='medium', title='Split count', stmt='Tasks after splitting 900 MB at 128 MB.', inp='advisory size',
         code='''import math
print(math.ceil(900 / 128))
''', explain='Other side replicated per split.'),
    dict(level='business', title='Cluster minutes', stmt='Minutes saved per day by AQE on 100 jobs.', inp='1.1 s saved per job, 24 runs',
         code='''print(round(1.1 * 100 * 24 / 60), "minutes")
''', explain='Small savings add up.'),
    dict(level='business', title='Festival day', stmt='Partitions needed for 10x volume at 128 MB.', inp='normal 50 GB shuffle',
         code='''print(int(500 * 1024 / 128))
''', explain='Set as the upper bound; AQE merges on normal days.'),
]

SCN_INTRO = 'AQE questions are common for Spark 3+ roles.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“What is AQE?”',
        'Explain Adaptive Query Execution.',
        'the three features?',
        '<p>AQE re-optimises a query at run time using statistics from completed shuffle stages: it coalesces small shuffle partitions, switches sort-merge joins to broadcast joins when a side is small, and splits skewed join partitions. It is on by default since Spark 3.2.</p>', 'Confusing it with caching.') +
    scn('Data engineering', 'Mid-level', 'Too many tiny tasks',
        'A small job runs 200 tasks per stage.',
        'coalescing?',
        '''<ul>
          <li>Ensure AQE and coalescePartitions are enabled.</li>
          <li>Check the final plan for AQEShuffleRead coalesced.</li>
          <li>In my test 204 tasks became 5.</li>
        </ul>''', 'Hard-coding shuffle.partitions per job.') +
    scn('Data engineering', 'Mid-level', 'Slow skewed join',
        'One task of a join takes most of the time.',
        'skew handling?',
        '''<ol>
          <li>Check for SortMergeJoin(skew=true) in the final plan.</li>
          <li>If absent, compare partition sizes with skew thresholds; tune them.</li>
          <li>Fall back to salting or broadcasting the small side.</li>
        </ol>''', 'Adding executors.') +
    scn('Platform', 'Senior', 'Platform defaults',
        'Set Spark SQL defaults for hundreds of jobs.',
        'tuning strategy?',
        '''<ul>
          <li>AQE on; shuffle partitions high; advisory size by cluster size.</li>
          <li>Runtime broadcast threshold sized to executor memory.</li>
          <li>Monitor final plans and task skew in the UI/history server.</li>
        </ul>''', 'Turning AQE off for predictability.')
)
