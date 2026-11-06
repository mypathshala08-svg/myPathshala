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
    module='02-rdds', lesson='01-what-is-an-rdd', n='2.1',
    module_label='Module 2 · RDDs: Spark’s foundation',
    title='What is an RDD? Partitions, immutability and lineage',
    desc='Resilient Distributed Datasets explained with real PySpark 4.3.0 outputs: creating RDDs with parallelize, textFile, wholeTextFiles and df.rdd; seeing partitions with glom(); immutability and lineage with toDebugString(); the five properties of an RDD; and the same city-revenue question taking 4.0 s as a DataFrame and 30.2 s as an RDD.',
    og_desc='Five ways to create an RDD, the partitions inside, the lineage that makes it resilient, and why the same query ran 8× slower than a DataFrame.',
    minutes=32, level='Beginner → Intermediate',
    lead='Module 2 goes underneath DataFrames to <b>RDDs</b>, the abstraction every Spark job runs on. This lesson creates RDDs five ways from TiffinGo’s data, looks inside their partitions and lineage, and measures what RDDs cost compared with DataFrames. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', 'Five ways to create an RDD', 'RDD vs DataFrame: 8×', 'Runs in your browser (Python)'],
)

MAIN = '''# A toy RDD: partitions + a recipe (lineage), in plain Python
class ToyRDD:
    def __init__(self, partitions, parent=None, op=None):
        self.partitions, self.parent, self.op = partitions, parent, op
    @staticmethod
    def parallelize(data, n):
        size = -(-len(data) // n)
        return ToyRDD([data[i:i + size] for i in range(0, len(data), size)])
    def filter(self, f):
        return ToyRDD([[x for x in p if f(x)] for p in self.partitions], self, "filter")
    def glom(self):
        return self.partitions
    def lineage(self):
        r, chain = self, []
        while r:
            chain.append(r.op or "parallelize"); r = r.parent
        return " <- ".join(chain)

amounts = ToyRDD.parallelize([530, 210, 480, 990, 120, 340], 3)
big = amounts.filter(lambda a: a >= 300)
print("amounts:", amounts.glom())
print("big    :", big.glom())
print("lineage:", big.lineage())
'''
RUN = dict(
    heading='Run the code: build a toy RDD',
    intro='<p>PySpark cannot run in the browser, so this toy class imitates an RDD: data split into partitions and a recorded parent. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('        return ToyRDD([data[i:i + size] for i in range(0, len(data), size)])', 'Like sc.parallelize(data, 3): the list is cut into 3 partitions of 2.'),
        ('        return ToyRDD([[x for x in p if f(x)] for p in self.partitions], self, "filter")', 'A new RDD; the old one is untouched and becomes the parent (lineage).'),
    ],
    tasks=[
        dict(label='1 · Look inside', hint='Press <b>Run</b>. The output matches Spark’s glom() in Step 1.', code=None),
        dict(label='2 · Predict first: 4 partitions', hint='<b>Predict first:</b> how are 6 amounts split into 4 partitions with this rule?',
             code='''data, n = [530, 210, 480, 990, 120, 340], 4
size = -(-len(data) // n)
print([data[i:i + size] for i in range(0, len(data), size)])
'''),
        dict(label='3 · Rebuild a lost partition', hint='Partition 1 of big is lost. Recompute only it from the parent.',
             code='''amounts = [[530, 210], [480, 990], [120, 340]]
f = lambda a: a >= 300
lost = 1
print("rebuilt partition", lost, ":", [x for x in amounts[lost] if f(x)])
'''),
        dict(label='4 · Lines to fields', hint='Parse an order_items line like an RDD map would.',
             code='''line = "100001|Chole Bhature,Aloo Paratha,Lassi,Rajma Chawal|spice:medium,cutlery:yes"
oid, dishes, notes = line.split("|")
print(oid, dishes.split(","), dict(n.split(":") for n in notes.split(",")))
'''),
        dict(label='5 · Spot the error', hint='This code tries to change an RDD in place.', expect='error',
             code='''partitions = ((530, 210), (480, 990))          # immutable, like an RDD
try:
    partitions[0][0] = 999
except TypeError as e:
    raise AssertionError("RDDs are immutable: create a new one with map/filter instead") from e
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: inspect RDDs',
    intro='<p>In the <code>pyspark</code> shell (Lesson 1.5). <b>Outputs are real</b> (PySpark 4.3.0, <code>local[2]</code>).</p>',
    items=[
        dict(title='1 · Partitions and their contents', cmd='rdd = sc.parallelize([530, 210, 480, 990, 120, 340], 3)\nrdd.getNumPartitions(), rdd.glom().collect()', file='pyspark',
             output='(3, [[530, 210], [480, 990], [120, 340]])', note='Use glom() only on small data: it builds a list per partition.'),
        dict(title='2 · Lines per partition', cmd='sc.textFile("order_items.txt").mapPartitions(lambda it: [sum(1 for _ in it)]).collect()', file='pyspark',
             output='[2517, 2483]', note='Two partitions of roughly equal size.'),
        dict(title='3 · The lineage', cmd='big = rdd.filter(lambda a: a >= 300)\nprint(big.toDebugString().decode())', file='pyspark',
             output=capf('l21_create.txt').split('Lineage of big:\n')[1], note='(3) is the number of partitions; indentation shows parents.'),
    ],
)

TRACE = dict(
    heading='How an RDD rebuilds a lost partition',
    intro='<p>Follow lineage-based recovery for one partition.</p>',
    code='''parent = {0: [530, 210], 1: [480, 990], 2: [120, 340]}
op = lambda a: a >= 300
child = {k: [x for x in v if op(x)] for k, v in parent.items()}
del child[1]                                   # executor with partition 1 dies
child[1] = [x for x in parent[1] if op(x)]     # recompute from lineage
print(child)
''',
    notes={3: 'Compute :: Each partition of the child is computed from the same partition of the parent.', 4: 'Failure :: The data is gone, but the recipe is not.', 5: 'Recovery :: Only the lost partition is recomputed, not the whole RDD.'},
)

WORKED_INTRO = 'Three RDD decisions from real projects.'
EXAMPLES = [
    dict(level='b', tag='Data engineering · text', title='Count bad lines in a partner file',
         problem='<p>Find lines in order_items.txt that do not have three fields.</p>',
         inp='order_items.txt',
         approach=['textFile.', 'split on |.', 'filter wrong lengths.'],
         code='''lines = ["100001|Poha,Idli|spice:hot", "100002|Dosa", "100003|Thepla|spice:mild"]
bad = [l for l in lines if len(l.split("|")) != 3]
print("bad lines:", bad)
''', notes={2: 'Spark :: sc.textFile(p).filter(lambda l: len(l.split("|")) != 3).count()'},
         tryit='Our real file had no bad lines: all 5,000 had three fields.'),
    dict(level='i', tag='API choice · performance', title='RDD or DataFrame?',
         problem='<p>Decide the API for three tasks.</p>',
         inp='three tasks',
         approach=['Structured → DataFrame.', 'Free text parsing → RDD, then DataFrame.', 'Per-partition connections → RDD/mapPartitions.'],
         code='''tasks = {"revenue per city from Parquet": "DataFrame",
         "parse multi-line partner logs": "RDD, then DataFrame",
         "push each partition to a REST API": "RDD mapPartitions (or foreachPartition)"}
for k, v in tasks.items():
    print(f"{k:38} -> {v}")
''', notes={1: 'Measured :: 4.0 s vs 30.2 s for the first task in our lab.'},
         tryit='Lesson 4.1 introduces DataFrames properly.'),
    dict(level='a', tag='Internals · properties', title='Name the five properties',
         problem='<p>Describe big = amounts.filter(...) by its five RDD properties.</p>',
         inp='Step 5’s RDD',
         approach=['Partitions.', 'Compute function.', 'Dependencies, partitioner, locations.'],
         code='''props = {"partitions": 3, "compute": "apply the filter lambda to the parent's partition",
         "dependencies": "one-to-one on amounts (narrow)", "partitioner": None,
         "preferred locations": "none (data came from the driver)"}
for k, v in props.items():
    print(f"{k:20} {v}")
''', notes={3: 'Narrow :: Each child partition needs exactly one parent partition (Lesson 2.4).'},
         tryit='textFile on HDFS would have preferred locations: the DataNodes holding each block.'),
]

QUIZ = mix([
    dict(q='Beginner: What does RDD stand for?', options=['Relational Data Database', 'Resilient Distributed Dataset', 'Rapid Data Driver', 'Replicated Disk Data'], answer=1,
         why='Resilient through lineage, distributed over executors.'),
    dict(q='Beginner: What does textFile give per element?', options=['A whole file', 'One line', 'One word', 'A Row'], answer=1,
         why='wholeTextFiles gives whole files.'),
    dict(q='Beginner: Can you change an RDD in place?', options=['Yes', 'No, transformations return new RDDs', 'Only with cache()', 'Only in local mode'], answer=1,
         why='big is amounts → False.'),
    dict(q='Intermediate: How were 6 amounts split by parallelize(…, 3)?', options=['6-0-0', '2-2-2', '1-2-3', 'random'], answer=1,
         why='glom() showed [[530, 210], [480, 990], [120, 340]].'),
    dict(q='Intermediate: What makes RDDs resilient?', options=['3 replicas', 'Lineage: lost partitions are recomputed', 'Checkpoints only', 'Disk storage'], answer=1,
         why='Replication is HDFS’s method, not RDDs’.'),
    dict(q='Intermediate: What type are the elements of df.rdd?', options=['dict', 'Row', 'tuple of strings', 'Column'], answer=1,
         why='Row objects with named fields.'),
    dict(q='Advanced: Why was the RDD version 8× slower?', options=['Bigger data', 'Python lambdas, pickling, no Catalyst optimisation', 'Fewer partitions', 'Disk spill'], answer=1,
         why='Rows travelled JVM → Python → JVM.'),
    dict(q='Advanced: Which is NOT one of an RDD’s five properties?', options=['Partitions', 'Dependencies', 'A schema', 'Preferred locations'], answer=2,
         why='RDDs have no schema; DataFrames do.'),
])

REVISION = [
    '<b>RDD</b>: immutable, partitioned collection processed in parallel; resilient through <b>lineage</b>.',
    'Five properties: partitions, compute function, dependencies, optional partitioner, optional preferred locations.',
    'Create: <code>parallelize</code> (small driver data), <code>textFile</code> (lines), <code>wholeTextFiles</code> (files), <code>df.rdd</code> (Rows).',
    '<code>glom()</code> shows partitions; <code>toDebugString()</code> shows lineage.',
    'Transformations return <b>new</b> RDDs; the parent is unchanged.',
    'Lab: same answer, DataFrame 4.0 s vs RDD 30.2 s (8×): use DataFrames for structured data.',
    'RDDs for unstructured text, custom per-partition logic, legacy jobs; then convert to DataFrames.',
]
FAQ = [
    ('Are RDDs deprecated?', 'No. They remain part of Spark Core and every DataFrame runs on them. The documentation recommends DataFrames for most work, and the RDD API is not available through Spark Connect clients.'),
    ('What is the difference between SparkContext and SparkSession?', 'SparkSession is the entry point for DataFrames and SQL; it contains a SparkContext (spark.sparkContext), the entry point for RDDs. One application has one SparkContext.'),
    ('How many partitions should an RDD have?', 'Enough to keep every core busy, typically 2–4 per core, with partitions of tens to a few hundred MB. Too few wastes cores; too many adds scheduling overhead (Lesson 8.1).'),
    ('Does an RDD hold data?', 'Not necessarily. Until an action runs, an RDD is only a recipe. Data exists while tasks run, and stays in memory only if you cache it (Lesson 3.1).'),
    ('Can I convert an RDD to a DataFrame?', 'Yes: spark.createDataFrame(rdd, schema) or rdd.toDF(["col1", "col2"]) for RDDs of tuples or Rows. Lesson 4.2 covers schemas.'),
]

PRACTICE_INTRO = 'Small programs about partitions and lineage.'
PROBLEMS = [
    dict(level='easy', title='Split into partitions', stmt='Split 10 numbers into 3 partitions like parallelize.', inp='range(10), 3',
         code='''data, n = list(range(10)), 3
size = -(-len(data) // n)
print([data[i:i + size] for i in range(0, len(data), size)])
''', explain='Spark’s exact split may differ slightly, but the idea is contiguous slices.'),
    dict(level='easy', title='Lines to words', stmt='Count words in review lines.', inp='two lines',
         code='''lines = ["poha was tasty and hot", "idli was cold and late"]
print(sum(len(l.split()) for l in lines))
''', explain='In Spark: rdd.flatMap(lambda l: l.split()).count().'),
    dict(level='easy', title='File name from path', stmt='Get the month from a wholeTextFiles path.', inp='path string',
         code='''p = "file:/data/tiffingo/reviews/reviews_2026-09.txt"
print(p.split("_")[-1].replace(".txt", ""))
''', explain='wholeTextFiles keeps the path, so the file name can carry data.'),
    dict(level='medium', title='Lineage chain', stmt='Print a lineage like toDebugString.', inp='three operations',
         code='''ops = ["textFile", "map(split)", "filter(len == 3)"]
for depth, op in enumerate(reversed(ops)):
    print(" |  " * depth + op)
''', explain='The newest RDD is printed first, parents below.'),
    dict(level='medium', title='Partition balance', stmt='Check if partitions are balanced.', inp='lines per partition',
         code='''sizes = [2517, 2483]
print(f"imbalance: {max(sizes) / min(sizes):.2f}x")
''', explain='Close to 1.0 is good; large values mean skew (Lesson 8.3).'),
    dict(level='medium', title='Row access', stmt='Read fields from a Row-like object.', inp='namedtuple',
         code='''from collections import namedtuple
Row = namedtuple("Row", "city amount status")
r = Row("Mumbai", 530, "DELIVERED")
print(r.city, r[1])
''', explain='pyspark Row supports r.city and r["city"].'),
    dict(level='business', title='Cost of the RDD version', stmt='Cluster-hours saved by rewriting with DataFrames.', inp='30.2 s vs 4.0 s, job runs 500 times a day',
         code='''print(round((30.2 - 4.0) * 500 / 3600, 1), "hours per day")
''', explain='At scale, the 8× factor becomes real money.'),
    dict(level='business', title='Bad-line rate', stmt='Share of unparseable partner lines.', inp='12 bad of 48,000',
         code='''print(f"{12 / 48000:.3%}")
''', explain='Track it per partner; a jump means a format change upstream.'),
]

SCN_INTRO = 'RDD fundamentals are asked in nearly every Spark interview.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“What is an RDD?”',
        'Explain RDDs and their main features.',
        'do you know the core idea?',
        '<p>An RDD is Spark’s basic data structure: an immutable collection split into partitions across the cluster and processed in parallel. It is lazily evaluated and fault tolerant: Spark keeps the lineage of operations and recomputes lost partitions. I can create one with parallelize, textFile or from a DataFrame.</p>', 'Saying RDDs are stored replicated in memory.') +
    scn('Data engineering', 'Fresher', 'RDD vs DataFrame',
        'When would you use an RDD instead of a DataFrame?',
        'do you know the trade-off?',
        '''<ul>
          <li>DataFrame: structured data; Catalyst optimisation; much faster in Python (8× in our test).</li>
          <li>RDD: unstructured data, custom low-level logic, per-partition resources, legacy code.</li>
          <li>Often: parse with RDDs, then convert to a DataFrame.</li>
        </ul>''', '“RDDs are faster because they are lower level.”') +
    scn('Data engineering', 'Mid-level', 'Slow PySpark RDD job',
        'A job using df.rdd.map(...) is very slow.',
        'can you explain the cost?',
        '''<ol>
          <li>Each row is converted to a Python object and pickled to a Python worker.</li>
          <li>No optimisation: no column pruning, no code generation.</li>
          <li>Rewrite with DataFrame functions; verify identical results.</li>
        </ol>''', 'Adding executors without changing the code.') +
    scn('Platform', 'Senior', 'Explain lineage-based fault tolerance',
        'Why does Spark not replicate RDD data like HDFS?',
        'do you understand the design?',
        '''<ul>
          <li>Lineage records coarse-grained transformations; recomputing a lost partition is cheaper than replicating every intermediate dataset.</li>
          <li>Long lineages or expensive shuffles can be cut with checkpointing (Lesson 3.3).</li>
          <li>Cached data can optionally be replicated (MEMORY_ONLY_2) when recomputation is too costly.</li>
        </ul>''', 'Claiming RDDs are always replicated three times.')
)
