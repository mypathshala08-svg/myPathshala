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
    module='03-persistence-and-shared-variables', lesson='02-broadcast-variables-and-accumulators', n='3.2',
    module_label='Module 3 · Persistence and shared variables',
    title='Broadcast variables and accumulators',
    desc='Spark’s shared variables, measured on a Spark 4.3.0 cluster: a 400,000-entry lookup dictionary in a closure (14.8 s for 3 jobs, 2.1 MiB shipped per job) vs a broadcast variable (8.2 s, sent once), what unpersist() and destroy() really do in PySpark, a broadcast hash join (4.8 s) vs a sort-merge join (6.1 s), accumulators that double count inside transformations but are exact in actions and across task retries, and a custom dictionary accumulator for data quality.',
    og_desc='The same lookup 45% faster with a broadcast, and an accumulator that counted one bad row as two: Spark’s shared variables, measured.',
    minutes=34, level='Intermediate',
    lead='Executors cannot see the driver’s variables. Spark offers two safe ways to share data with them: <b>broadcast variables</b>, read-only values sent once to every executor, and <b>accumulators</b>, counters that tasks add to. This lesson measures both on our cluster and tests every rule that decides whether an accumulator is right. <b>All outputs are real</b> (Spark 4.3.0).',
    chips=['Spark 4.3.0 cluster', 'Closure vs broadcast: 14.8 → 8.2 s', 'Accumulator rules tested', 'Runs in your browser (Python)'],
)

MAIN = '''# Bytes shipped: a lookup dict in the closure vs a broadcast (lab sizes)
dict_mib = 2.1           # pickled closure with the 400,000-entry dict (driver log)
tasks_per_job, jobs, executors = 16, 3, 2

closure_shipped = dict_mib * jobs                    # one closure broadcast per job
closure_unpickled = tasks_per_job * jobs             # every task unpickles its copy
bcast_shipped = dict_mib                             # sent once
bcast_unpickled = executors * 2                      # roughly once per Python worker (2 cores each)

print(f"closure  : {closure_shipped:.1f} MiB shipped, dict unpickled {closure_unpickled} times")
print(f"broadcast: {bcast_shipped:.1f} MiB shipped, dict unpickled ~{bcast_unpickled} times")
'''
RUN = dict(
    heading='Run the code: what travels to the executors',
    intro='<p>A small model of Step 1 and 2 using the lab’s numbers. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('closure_shipped = dict_mib * jobs                    # one closure broadcast per job', 'The driver log showed a 2.1 MiB block for each of the three closure jobs.'),
        ('bcast_unpickled = executors * 2                      # roughly once per Python worker (2 cores each)', 'Python workers keep the loaded broadcast value and reuse it for later tasks.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then try 200 tasks per job and 10 jobs.', code=None),
        dict(label='2 · Predict first: double counting', hint='<b>Predict first:</b> an accumulator in map, 3 uncached actions, 1 bad row. What does it show?',
             code='''bad_rows, actions_recomputing = 1, 3
print("accumulator:", bad_rows * actions_recomputing)
'''),
        dict(label='3 · Retries do not double count', hint='Only successful attempts are merged.',
             code='''attempts = [("task0", "failed", 1), ("task0", "success", 500), ("task1", "success", 500)]
print("accumulator:", sum(n for _, status, n in attempts if status == "success"))
'''),
        dict(label='4 · Dictionary accumulator', hint='Merge per-task dicts like AccumulatorParam.addInPlace.',
             code='''def merge(a, b):
    for k, v in b.items():
        a[k] = a.get(k, 0) + v
    return a
tasks = [{"cancelled": 1500, "bad amount": 1}, {"cancelled": 1563, "bad timestamp": 1}]
total = {}
for t in tasks:
    total = merge(total, t)
print(total)
'''),
        dict(label='5 · Spot the error', hint='This job reports a business total from an accumulator in a transformation.', expect='error',
             code='''uses = {"revenue_accumulator": "map"}
for name, where in uses.items():
    assert where in ("foreach", "foreachPartition"), f"{name} is updated in {where}: use an aggregation for exact totals"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: shared variables',
    intro='<p>In the <code>pyspark</code> shell. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Broadcast a lookup', cmd='zones = sc.broadcast({"Mumbai": "West", "Pune": "West", "Delhi": "North"})\nsc.parallelize(["Mumbai", "Delhi"]).map(lambda c: (c, zones.value[c])).collect()', file='pyspark',
             output="[('Mumbai', 'West'), ('Delhi', 'North')]", note='Read with .value inside tasks.'),
        dict(title='2 · The join plan', cmd='big.join(F.broadcast(cust), "customer_id").explain()', file='pyspark',
             output='\n'.join(capf('l32_plan.txt').split('\n')[:7]) + '\n…', note='BroadcastExchange + BroadcastHashJoin: no shuffle of the big side.'),
        dict(title='3 · Accumulator in an action', cmd='bad = sc.accumulator(0)\nlines.foreach(lambda l: bad.add(0 if l.split(",")[5].isdigit() else 1))\nbad.value', file='pyspark',
             output='1', note='Exact: updates in actions are applied once per successful task.'),
    ],
)

TRACE = dict(
    heading='Why an accumulator in map counted twice',
    intro='<p>Follow two actions on an uncached RDD with an accumulator in the map.</p>',
    code='''acc = 0
lines = ["530", "abc", "210"]
def parse(l):
    global acc
    if not l.isdigit():
        acc += 1
    return l
for action in ("count", "filter + count"):
    _ = [parse(l) for l in lines]       # each action re-runs the map
print("accumulator:", acc, "| real bad rows:", 1)
''',
    notes={5: 'Update :: Inside a transformation.', 8: 'Recompute :: Without cache, every action runs the map again.', 9: 'Result :: 2, although only one row is bad.'},
)

WORKED_INTRO = 'Three shared-variable decisions from real pipelines.'
EXAMPLES = [
    dict(level='b', tag='Data engineering · lookups', title='Tag orders with zones',
         problem='<p>Add a zone to each order using a small city → zone map.</p>',
         inp='orders RDD, 8 cities',
         approach=['Broadcast the dict.', 'Read b.value in map.', 'Done.'],
         code='''zones = {"Mumbai": "West", "Pune": "West", "Delhi": "North", "Chennai": "South"}
orders = [("Mumbai", 530), ("Delhi", 210)]
print([(c, a, zones[c]) for c, a in orders])     # Spark: b = sc.broadcast(zones); b.value[c]
''', notes={1: 'Small :: For 8 entries a closure is also fine; broadcast matters as the map grows.'},
         tryit='With DataFrames, join with a small zones DataFrame and Spark broadcasts it.'),
    dict(level='i', tag='Monitoring · accumulators', title='Count parse failures correctly',
         problem='<p>Report how many lines fail to parse without double counting.</p>',
         inp='raw lines, several actions later',
         approach=['Parse and cache once.', 'Or count failures with filter().count().', 'Accumulator only in an action.'],
         code='''print("parsed = lines.map(parse).cache(); parsed.count()   # accumulator exact once")
print("or:  bad = lines.filter(lambda l: not ok(l)).count() # exact, no accumulator")
''', notes={1: 'Cache :: Prevents re-running parse in later actions.'},
         tryit='Step 5 showed 2 without cache and 1 with it.'),
    dict(level='a', tag='Performance · joins', title='Broadcast join or not?',
         problem='<p>Decide join strategy for three dimension tables.</p>',
         inp='in-memory sizes',
         approach=['Below ~10–100 MB: broadcast.', 'Larger: sort-merge (AQE may convert).', 'Never broadcast near executor memory.'],
         code='''dims = {"customers": 0.3, "restaurants": 0.05, "events_by_user": 3500}
for d, mb in dims.items():
    print(f"{d:15} {mb:7} MB ->", "broadcast" if mb < 100 else "sort-merge")
''', notes={1: 'Sizes :: In memory, which can be far larger than the Parquet files.'},
         tryit='Lesson 8.2 measures join strategies on bigger data.'),
]

QUIZ = mix([
    dict(q='Beginner: What is a broadcast variable?', options=['A writable global', 'A read-only value sent once to each executor', 'A cached RDD', 'A Kafka topic'], answer=1,
         why='Read it with .value in tasks.'),
    dict(q='Beginner: Who can read an accumulator’s value?', options=['Every task', 'Only the driver', 'Nobody', 'Executors only'], answer=1,
         why='Tasks can only add.'),
    dict(q='Beginner: Which join does Spark use automatically for a small table?', options=['Cartesian', 'Broadcast hash join', 'Nested loop', 'Sort-merge only'], answer=1,
         why='Below autoBroadcastJoinThreshold (10 MB).'),
    dict(q='Intermediate: Why was the closure version slower?', options=['Bigger result', 'The dictionary travelled with every job and was unpickled by every task', 'More partitions', 'Disk spill'], answer=1,
         why='2.1 MiB per job; 14.8 s vs 8.2 s.'),
    dict(q='Intermediate: An accumulator in map, two uncached actions, one bad row. Value?', options=['0', '1', '2', 'Random'], answer=2,
         why='The map ran twice.'),
    dict(q='Intermediate: What happened when the broadcast was used after unpersist() in PySpark 4.3?', options=['It was re-sent', 'Tasks failed with FileNotFoundError', 'It returned None', 'It was faster'], answer=1,
         why='Treat unpersist as the end of use.'),
    dict(q='Advanced: A task failed after adding to an accumulator and was retried. Is it counted twice?', options=['Yes', 'No, updates from failed attempts are discarded', 'Only on YARN', 'Only for dicts'], answer=1,
         why='1,000, not 1,001.'),
    dict(q='Advanced: What must addInPlace in an AccumulatorParam be?', options=['Fast', 'Associative and commutative', 'Pure SQL', 'Idempotent only'], answer=1,
         why='Spark merges partial values in any order.'),
])

REVISION = [
    '<b>Broadcast</b>: <code>sc.broadcast(v)</code>, read <code>b.value</code>; sent once per executor, shared by tasks.',
    'Lab: dict in closure 14.8 s (2.1 MiB per job) vs broadcast 8.2 s (sent once). PySpark auto-broadcasts closures &gt; 1 MB, but per job.',
    '<code>unpersist()</code> / <code>destroy()</code> only when completely done (reuse failed in PySpark 4.3).',
    'DataFrames: broadcast hash join for small tables (auto &lt; 10 MB, or <code>F.broadcast</code>): 4.8 s vs 6.1 s sort-merge.',
    '<b>Accumulator</b>: tasks add, driver reads; custom types via <code>AccumulatorParam</code>.',
    'Exact in actions (foreach); may double count in transformations when recomputed (1 bad row → 2).',
    'Failed task attempts are not counted (1,000, not 1,001). Use aggregations for business totals.',
]
FAQ = [
    ('How big can a broadcast be?', 'It must fit in the driver and in every executor’s memory, alongside tasks. Lookup tables of a few to a few hundred MB are typical; gigabyte-sized broadcasts usually cause memory problems.'),
    ('Can I update a broadcast variable?', 'No. Broadcasts are read-only. To change the value, create a new broadcast (and destroy the old one when no running job uses it).'),
    ('Are accumulators visible in the Spark UI?', 'Named accumulators (created with a name in Scala/Java) appear on the stage pages. PySpark accumulators are mainly read on the driver.'),
    ('Why not just use a global variable?', 'Each task gets a copy of the closure, so changes never reach the driver (Lesson 2.2). Accumulators are designed to send updates back.'),
    ('Does Spark SQL use broadcast variables internally?', 'Yes. BroadcastExchange in a plan sends the small side of a join to every executor as a hash table, the same mechanism as sc.broadcast.'),
]

PRACTICE_INTRO = 'Programs about shipping values and counting safely.'
PROBLEMS = [
    dict(level='easy', title='Speed-up', stmt='Time saved by broadcasting.', inp='14.8 s vs 8.2 s',
         code='''print(f"{1 - 8.2 / 14.8:.0%} less time")
''', explain='Same three jobs, same results.'),
    dict(level='easy', title='Lookup', stmt='Tag cities with zones using a dict.', inp='dict and list',
         code='''zones = {"Mumbai": "West", "Delhi": "North"}
print([zones[c] for c in ["Delhi", "Mumbai"]])
''', explain='In Spark: b.value[c] inside map.'),
    dict(level='easy', title='Count in an action', stmt='Count bad amounts like foreach + accumulator.', inp='values',
         code='''acc = 0
for v in ["530", "abc", "210"]:
    acc += 0 if v.isdigit() else 1
print(acc)
''', explain='Exact: 1.'),
    dict(level='medium', title='Shipped bytes', stmt='Total closure bytes for n jobs.', inp='2.1 MiB, 10 jobs',
         code='''print(2.1 * 10, "MiB vs 2.1 MiB with a broadcast")
''', explain='Grows with every job when the dict is in the closure.'),
    dict(level='medium', title='Merge accumulators', stmt='Merge reason counts from three tasks.', inp='list of dicts',
         code='''from collections import Counter
print(dict(sum([Counter(a=1), Counter(a=2, b=1), Counter(b=3)], Counter())))
''', explain='Counter addition is associative and commutative.'),
    dict(level='medium', title='Threshold check', stmt='Will Spark auto-broadcast these tables?', inp='sizes in MB, 10 MB threshold',
         code='''for name, mb in {"customers": 0.3, "orders": 35}.items():
    print(name, mb < 10)
''', explain='Estimates come from statistics; F.broadcast forces it.'),
    dict(level='business', title='Cluster time saved', stmt='Hours saved per month by broadcasting.', inp='6.6 s saved per run, 300 runs a day',
         code='''print(round(6.6 * 300 * 30 / 3600, 1), "hours")
''', explain='About 16 hours of cluster time a month.'),
    dict(level='business', title='Wrong alert cost', stmt='False alerts per month from a doubled counter.', inp='threshold 150, true bad rows 100/day',
         code='''print(30 if 100 * 2 > 150 else 0, "false alerts")
''', explain='Every night pages someone for nothing.'),
]

SCN_INTRO = 'Shared-variable questions test whether you understand distribution.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', 'Broadcast variables',
        'What is a broadcast variable and when do you use it?',
        'do you know the use case?',
        '<p>A read-only value, such as a lookup table, sent once to every executor and cached there, so tasks can read it without shipping it with every task. I use it for lookups in RDD code and Spark uses the same idea for broadcast joins with small tables. In our test it cut a lookup job from 14.8 to 8.2 s.</p>', 'Saying broadcast variables can be updated by tasks.') +
    scn('Data engineering', 'Mid-level', 'Accumulator shows wrong count',
        'An accumulator counting bad rows shows double the real number.',
        'do you know accumulator semantics?',
        '''<ol>
          <li>It is updated inside a transformation; the stage ran twice (two actions, no cache).</li>
          <li>Move the update into an action, cache the parsed data, or compute with filter().count().</li>
          <li>Use accumulators for monitoring, not results.</li>
        </ol>''', 'Dividing the value by two.') +
    scn('Data engineering', 'Mid-level', 'Small-table join is slow',
        'Joining 5 billion orders with 2,000 customers takes long and shuffles a lot.',
        'do you know broadcast joins?',
        '''<ul>
          <li>Check explain(): SortMergeJoin with shuffles of both sides.</li>
          <li>Use F.broadcast(customers) or raise autoBroadcastJoinThreshold moderately.</li>
          <li>Verify BroadcastHashJoin in the plan and less shuffle in the UI.</li>
        </ul>''', 'Repartitioning the big table first.') +
    scn('Platform', 'Senior', 'Broadcast-related OOMs',
        'After raising the broadcast threshold to 2 GB, drivers and executors crash.',
        'can you reason about memory?',
        '''<ul>
          <li>The driver collects and builds the broadcast; every executor holds a copy next to its tasks.</li>
          <li>Measure in-memory sizes; keep thresholds in tens to hundreds of MB.</li>
          <li>Use sort-merge, bucketing or AQE for big-to-big joins.</li>
        </ul>''', 'Raising memory everywhere without limits.')
)
