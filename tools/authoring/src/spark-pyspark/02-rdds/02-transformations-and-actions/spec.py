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
    module='02-rdds', lesson='02-transformations-and-actions', n='2.2',
    module_label='Module 2 · RDDs: Spark’s foundation',
    title='RDD transformations and actions',
    desc='The RDD operations you will use most, with real PySpark 4.3.0 outputs on TiffinGo order notes: map vs flatMap (5,000 lines → 12,671 dishes), filter, distinct, union, sample, mapPartitions (4 setups instead of 100,000), collect, take, top, takeOrdered, reduce, fold, aggregate, countByValue and saveAsTextFile, plus the closure trap (a driver counter that stays 0, an accumulator that works) and where print() goes on a cluster.',
    og_desc='A counter that stays at zero, prints that vanish, and 100,000 setups that should have been 4: RDD transformations and actions with real outputs.',
    minutes=34, level='Beginner → Intermediate',
    lead='This lesson covers the RDD operations every Spark developer uses, on TiffinGo’s real order notes, and two classic surprises: a <b>driver variable that never changes</b> and <b>prints that disappear</b> on a cluster. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', '20+ operations', 'The closure trap, reproduced', 'Runs in your browser (Python)'],
)

MAIN = '''# RDD-style operations on a Python list of order notes (this runs in your browser)
from functools import reduce
lines = ["100001|Chole Bhature,Aloo Paratha,Lassi|spice:medium",
         "100002|Veg Hakka Noodles,Manchurian|spice:hot",
         "100003|Poha,Misal Pav|spice:mild"]

parts = [l.split("|") for l in lines]                        # map
dishes = [d for l in lines for d in l.split("|")[1].split(",")]   # flatMap
hot = [l for l in lines if "spice:hot" in l]                  # filter
menu = sorted(set(dishes))                                    # distinct
print("map    :", parts[0])
print("flatMap:", len(lines), "lines ->", len(dishes), "dishes")
print("filter :", len(hot), "hot")
print("reduce :", reduce(lambda a, b: a + b, [530, 210, 480]))
'''
RUN = dict(
    heading='Run the code: RDD operations in plain Python',
    intro='<p>Each line imitates one RDD operation on a small list. Press <b>Run</b>, then try the challenges, including the closure trap.</p>',
    code=MAIN,
    anno=[
        ('dishes = [d for l in lines for d in l.split("|")[1].split(",")]   # flatMap', 'Two loops in one comprehension = flatMap: each line gives several dishes.'),
        ('menu = sorted(set(dishes))                                    # distinct', 'Spark’s distinct must shuffle to find duplicates in different partitions.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then change map to keep only the order id.', code=None),
        dict(label='2 · Predict first: aggregate', hint='<b>Predict first:</b> what does aggregate return for these partitions?',
             code='''parts = [[530, 210], [480, 990], [120, 340]]
seq = lambda acc, x: (acc[0] + x, acc[1] + 1)
comb = lambda a, b: (a[0] + b[0], a[1] + b[1])
from functools import reduce
partials = [reduce(seq, p, (0, 0)) for p in parts]
print(partials, "->", reduce(comb, partials, (0, 0)))
'''),
        dict(label='3 · The closure trap', hint='Simulate tasks that receive a copy of the driver’s variable.',
             code='''import copy
counter = {"value": 0}
for partition in ([530, 210], [480, 990]):
    task_copy = copy.deepcopy(counter)     # what Spark ships to a task
    for x in partition:
        task_copy["value"] += x
print("driver counter:", counter["value"])
'''),
        dict(label='4 · Accumulator idea', hint='Tasks send their partial sums back; the driver adds them.',
             code='''partials = []
for partition in ([530, 210], [480, 990], [120, 340]):
    partials.append(sum(partition))        # each task's update
print("accumulator:", sum(partials))
'''),
        dict(label='5 · Spot the error', hint='This uses map where flatMap is needed.', expect='error',
             code='''lines = ["Poha,Idli", "Dosa"]
words = [l.split(",") for l in lines]       # map: a list per line
assert all(isinstance(w, str) for w in words), "use flatMap: you got lists, not words"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: try the operations',
    intro='<p>In the <code>pyspark</code> shell with <code>order_items.txt</code>. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Most ordered dishes', cmd='lines = sc.textFile("order_items.txt")\ndishes = lines.flatMap(lambda l: l.split("|")[1].split(","))\nsorted(dishes.countByValue().items(), key=lambda kv: -kv[1])[:3]', file='pyspark',
             output="[('Sambar Rice', 502), ('Curd Rice', 494), ('Idli', 484)]", note='countByValue returns a dict to the driver: fine for 32 keys.'),
        dict(title='2 · Largest and smallest', cmd='amounts = sc.parallelize([530, 210, 480, 990, 120, 340], 3)\namounts.top(2), amounts.takeOrdered(2)', file='pyspark',
             output='([990, 530], [120, 210])', note='takeOrdered(n, key=lambda x: -x) gives the largest too.'),
        dict(title='3 · Output files', cmd='dishes.distinct().saveAsTextFile("out_menu")\n!ls out_menu', file='pyspark',
             output='_SUCCESS  part-00000  part-00001', note='One part file per partition. Use coalesce(1) for a single small file.'),
    ],
)

TRACE = dict(
    heading='How reduce works across partitions',
    intro='<p>Follow Spark’s two-level reduce on three partitions.</p>',
    code='''parts = [[530, 210], [480, 990], [120, 340]]
f = lambda a, b: a + b
partials = []
for p in parts:                     # one task per partition
    acc = p[0]
    for x in p[1:]:
        acc = f(acc, x)
    partials.append(acc)
total = partials[0]
for x in partials[1:]:              # on the driver
    total = f(total, x)
print(partials, total)
''',
    notes={4: 'Tasks :: Each partition is reduced on an executor.', 9: 'Driver :: The partial results are combined.', 11: 'Order :: Because the order of combining can vary, f must be associative and commutative.'},
)

WORKED_INTRO = 'Three everyday tasks solved with RDD operations.'
EXAMPLES = [
    dict(level='b', tag='Data engineering · parsing', title='Notes to a dictionary',
         problem='<p>Turn the notes field <code>spice:hot,cutlery:no</code> into a dict per order.</p>',
         inp='order_items lines',
         approach=['map to split on |.', 'split notes on , and :.', 'Build (id, dict).'],
         code='''line = "100002|Veg Hakka Noodles,Manchurian,Fried Rice|spice:mild,cutlery:yes"
oid, _, notes = line.split("|")
print((oid, dict(n.split(":") for n in notes.split(","))))
''', notes={3: 'Spark :: lines.map(parse) with this logic inside parse.'},
         tryit='Count orders without cutlery: filter on the dict, then count().'),
    dict(level='i', tag='Analytics · aggregation', title='Average in one pass',
         problem='<p>Compute the average order amount with a single action.</p>',
         inp='amounts RDD',
         approach=['aggregate (sum, count).', 'Divide on the driver.', 'No second pass.'],
         code='''s, n = 2670, 6          # amounts.aggregate((0,0), seq, comb)
print("average:", s / n)
''', notes={1: 'aggregate :: Real result from Step 5.'},
         tryit='Compare with amounts.mean(), a built-in action for numeric RDDs.'),
    dict(level='a', tag='Integration · performance', title='Batch API calls per partition',
         problem='<p>Send dish names to a pricing API in batches of 100, one client per partition.</p>',
         inp='dishes RDD',
         approach=['mapPartitions.', 'Create the client once.', 'Yield results per batch.'],
         code='''def price_partition(it):
    client = "PricingClient()"          # created once per partition
    batch = []
    for d in it:
        batch.append(d)
        if len(batch) == 100:
            yield from ((x, 0) for x in batch); batch = []
    yield from ((x, 0) for x in batch)
print(list(price_partition(iter(["Poha", "Idli"]))))
''', notes={2: 'Once :: Like our 4 setups instead of 100,000.'},
         tryit='Use foreachPartition instead when nothing needs to be returned.'),
]

QUIZ = mix([
    dict(q='Beginner: Which operation turns lines into words?', options=['map', 'flatMap', 'filter', 'reduce'], answer=1,
         why='map would give one list per line.'),
    dict(q='Beginner: Which is an action?', options=['filter', 'distinct', 'take', 'union'], answer=2,
         why='take returns elements to the driver.'),
    dict(q='Beginner: What did flatMap produce from 5,000 order lines?', options=['5,000', '12,671 dishes', '32', '1,695'], answer=1,
         why='About 2.5 dishes per order.'),
    dict(q='Intermediate: Which transformation needs a shuffle?', options=['map', 'filter', 'distinct', 'flatMap'], answer=2,
         why='Duplicates can be in different partitions.'),
    dict(q='Intermediate: Why did the driver counter stay 0?', options=['Bug in Spark', 'Tasks updated copies of the closure’s variables', 'foreach is lazy', 'Overflow'], answer=1,
         why='Use an accumulator.'),
    dict(q='Intermediate: Where do print() calls inside foreach appear on a cluster?', options=['Driver console', 'Executor logs', 'Nowhere', 'History server only'], answer=1,
         why='We found them in the executors’ stderr.'),
    dict(q='Advanced: What must a reduce function be?', options=['Fast', 'Associative and commutative', 'Pure Python', 'Typed'], answer=1,
         why='Spark combines partials in any order.'),
    dict(q='Advanced: Why use mapPartitions for a database client?', options=['It is lazy', 'Setup runs once per partition, not per element', 'It avoids shuffles', 'It sorts data'], answer=1,
         why='4 setups instead of 100,000.'),
])

REVISION = [
    '<b>Transformations</b> return new RDDs (lazy); <b>actions</b> run jobs and return results or write data.',
    '<code>map</code>: 1 → 1; <code>flatMap</code>: 1 → 0..n (5,000 lines → 12,671 dishes); <code>filter</code> keeps matches.',
    '<code>distinct</code> shuffles; <code>union</code> keeps duplicates; <code>sample</code> sizes are approximate.',
    '<code>mapPartitions</code>: function per partition (4 setups vs 100,000).',
    'Actions: <code>take</code>/<code>top</code>/<code>takeOrdered</code> are cheap; <code>collect</code>/<code>countByValue</code> bring everything to the driver.',
    '<code>reduce</code> (associative + commutative), <code>fold</code> (start value), <code>aggregate</code> (different result type).',
    'Closures are copied to tasks: driver variables do not change (0); use <b>accumulators</b> (2670).',
    'On a cluster, <code>print</code> in executors goes to executor logs.',
]
FAQ = [
    ('What is the difference between foreach and map?', 'map is a transformation that returns a new RDD and runs nothing. foreach is an action that runs a function for its side effects and returns None.'),
    ('Is countByValue the same as reduceByKey?', 'They count the same thing, but countByValue is an action that returns a dict to the driver, while map((x, 1)).reduceByKey(add) is a transformation whose result stays distributed. Use the latter for large numbers of keys (Lesson 2.5).'),
    ('Can accumulators be wrong?', 'Updates made inside transformations can be counted twice if a task is retried or a stage recomputed. Updates inside actions such as foreach are applied once per successful task. Lesson 3.2 shows this.'),
    ('Why is my saveAsTextFile output split into many files?', 'One file per partition, written in parallel by the executors. Reduce the partitions with coalesce if you need fewer files.'),
    ('Does take() scan everything?', 'No. It runs a job on the first partition and, if not enough elements are found, on more partitions, so it is cheap for small n.'),
]

PRACTICE_INTRO = 'Small programs that imitate RDD operations.'
PROBLEMS = [
    dict(level='easy', title='flatMap words', stmt='Split review lines into words.', inp='two lines',
         code='''lines = ["poha was tasty", "idli was cold"]
print([w for l in lines for w in l.split()])
''', explain='rdd.flatMap(lambda l: l.split()).'),
    dict(level='easy', title='Hot orders', stmt='Keep lines with spice:hot.', inp='three lines',
         code='''lines = ["1|Poha|spice:hot", "2|Idli|spice:mild", "3|Dosa|spice:hot"]
print([l for l in lines if "spice:hot" in l])
''', explain='rdd.filter(lambda l: "spice:hot" in l).'),
    dict(level='easy', title='Top 2', stmt='Largest two amounts.', inp='list',
         code='''print(sorted([530, 210, 480, 990, 120, 340], reverse=True)[:2])
''', explain='rdd.top(2) without sorting everything.'),
    dict(level='medium', title='Fold with a start value', stmt='Sum with fold per partition, then combine.', inp='3 partitions',
         code='''parts = [[530, 210], [480, 990], [120, 340]]
print(sum(sum(p, 0) for p in parts))
''', explain='The start value must be neutral (0 for +), because Spark uses it per partition and again when combining.'),
    dict(level='medium', title='Min and max in one pass', stmt='aggregate to (min, max).', inp='amounts',
         code='''vals = [530, 210, 480, 990, 120, 340]
acc = (float("inf"), float("-inf"))
for v in vals:
    acc = (min(acc[0], v), max(acc[1], v))
print(acc)
''', explain='One action instead of min() and max().'),
    dict(level='medium', title='Per-partition counting', stmt='Count elements per partition.', inp='partitions',
         code='''parts = [range(2517), range(2483)]
print([sum(1 for _ in p) for p in parts])
''', explain='rdd.mapPartitions(lambda it: [sum(1 for _ in it)]).collect()'),
    dict(level='business', title='Connections saved', stmt='Database connections with map vs mapPartitions.', inp='2,000,000 rows, 40 partitions',
         code='''print(2_000_000, "vs", 40)
''', explain='A 50,000× reduction in connection set-ups.'),
    dict(level='business', title='Silent counter impact', stmt='Bad rows missed if the counter always reads 0.', inp='0.1% of 5M rows per night',
         code='''print(int(5_000_000 * 0.001), "bad rows unreported per night")
''', explain='Closure bugs hide data-quality problems; test counters on known bad data.'),
]

SCN_INTRO = 'Transformations, actions and closures are interview favourites.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', 'map vs flatMap',
        'Explain map and flatMap with an example.',
        'do you know the difference?',
        '<p>map returns exactly one element per input, e.g. splitting a line gives one list per line. flatMap can return zero or more elements per input and flattens them, e.g. splitting lines into individual words. In our lab, flatMap turned 5,000 order lines into 12,671 dish names.</p>', 'Saying flatMap is faster.') +
    scn('Data engineering', 'Fresher', 'Transformations vs actions',
        'Name three transformations and three actions.',
        'can you classify?',
        '''<ul>
          <li>Transformations: map, filter, flatMap, distinct, union, mapPartitions (lazy, return RDDs).</li>
          <li>Actions: collect, count, take, reduce, foreach, saveAsTextFile (run jobs).</li>
        </ul>''', 'Listing groupByKey as an action.') +
    scn('Data engineering', 'Mid-level', 'Counter stays zero',
        'A global counter updated in rdd.foreach is always 0.',
        'do you understand closures?',
        '''<ol>
          <li>The function and its variables are serialised and copied to each task.</li>
          <li>Each task updates its own copy; the driver’s variable never changes.</li>
          <li>Use an accumulator, or compute the count with filter().count().</li>
        </ol>''', 'Making the variable global.') +
    scn('Platform', 'Senior', 'Writing to an external system',
        'A job writes each record to a REST API and overloads it.',
        'can you control parallelism?',
        '''<ul>
          <li>Use foreachPartition: one client per partition, batched requests, retries.</li>
          <li>Control concurrency with the number of partitions (coalesce) and executor cores.</li>
          <li>Make writes idempotent: tasks can be retried.</li>
        </ul>''', 'Calling the API from collect() on the driver.')
)
