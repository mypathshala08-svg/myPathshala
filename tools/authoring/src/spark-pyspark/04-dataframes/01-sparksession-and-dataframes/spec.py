import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='04-dataframes', lesson='01-sparksession-and-dataframes', n='4.1',
    module_label='Module 4 · DataFrames',
    title='SparkSession and DataFrames',
    desc='The SparkSession entry point and the DataFrame, tested with PySpark 4.3.0: a second getOrCreate() that silently changed shuffle partitions from 8 to 50, newSession() with its own views and SQL conf, a first DataFrame from TiffinGo orders where one "abc" made amount a string, a query that ran 0 jobs until show() ran 2, the physical plan with a pushed filter, Row objects, and a DataFrame and SQL query with identical plans.',
    og_desc='A second getOrCreate() silently changed our shuffle partitions from 8 to 50. SparkSession and DataFrames, tested with real outputs.',
    minutes=30, level='Beginner → Intermediate',
    lead='Module 4 moves from RDDs to <b>DataFrames</b>, the API used in almost all modern Spark code. This lesson covers the <b>SparkSession</b> entry point, what a DataFrame is, and how its laziness and plans work. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', 'getOrCreate surprise', 'Plan read line by line', 'Runs in your browser (Python)'],
)

MAIN = '''# A tiny model of getOrCreate(): one session, runtime settings applied
class Session:
    active = None
    def __init__(self, app, conf):
        self.app, self.conf = app, dict(conf)

def get_or_create(app, conf):
    if Session.active is None:
        Session.active = Session(app, conf)
    else:
        Session.active.conf.update(conf)      # runtime SQL settings are applied
    return Session.active

spark = get_or_create("tiffingo-4.1", {"spark.sql.shuffle.partitions": "8"})
s2 = get_or_create("another-name", {"spark.sql.shuffle.partitions": "50"})
print("same object:", s2 is spark)
print("app name   :", spark.app)
print("partitions :", spark.conf["spark.sql.shuffle.partitions"])
'''
RUN = dict(
    heading='Run the code: how getOrCreate behaves',
    intro='<p>A plain-Python model of Step 2. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('        Session.active.conf.update(conf)      # runtime SQL settings are applied', 'What we saw in the lab: 8 became 50 in the existing session.'),
        ('print("app name   :", spark.app)', 'The app name belongs to the SparkContext and stays.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then remove the conf from the second call: what does partitions print?', code=None),
        dict(label='2 · Predict first: lazy', hint='<b>Predict first:</b> how many jobs run while building a query of where + groupBy + orderBy?',
             code='''plan = []
for step in ("where", "groupBy", "orderBy"):
    plan.append(step)              # a transformation only adds to the plan
print("plan:", plan, "| jobs run:", 0)
print("show() -> jobs run: 2 (in our lab)")
'''),
        dict(label='3 · Immutable', hint='withColumn returns a new DataFrame; the old one is unchanged.',
             code='''orders = ("order_id", "city", "amount")
o2 = orders + ("amount_gst",)
print(len(orders), len(o2), o2 is orders)
'''),
        dict(label='4 · Rows', hint='A Row behaves like a named tuple.',
             code='''from collections import namedtuple
Row = namedtuple("Row", "city revenue")
r = Row("Mumbai", 2712820)
print(r.city, r[1], r._asdict())
'''),
        dict(label='5 · Spot the error', hint='This library function builds its own session with settings.', expect='error',
             code='''helper = {"calls_getOrCreate": True, "sets_conf": True}
assert not (helper["calls_getOrCreate"] and helper["sets_conf"]), "pass the caller's SparkSession in; do not configure it inside a library"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: the session',
    intro='<p>In a Python script or the <code>pyspark</code> shell. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Version and master', cmd='spark.version, spark.sparkContext.master', file='pyspark',
             output="('4.3.0', 'local[2]')", note='In the shell, spark already exists.'),
        dict(title='2 · A second getOrCreate', cmd='s2 = SparkSession.builder.config("spark.sql.shuffle.partitions", "50").getOrCreate()\ns2 is spark, spark.conf.get("spark.sql.shuffle.partitions")', file='pyspark',
             output="(True, '50')", note='The runtime SQL setting reached the existing session.'),
        dict(title='3 · Columns and types', cmd='orders.dtypes[:3]', file='pyspark',
             output="[('order_id', 'int'), ('customer_id', 'int'), ('restaurant_id', 'int')]", note='printSchema() shows the same as a tree.'),
    ],
)

TRACE = dict(
    heading='What runs when',
    intro='<p>Follow which lines only plan and which line runs a job.</p>',
    code='''plan, jobs = [], 0
for op in ("read", "where", "groupBy", "orderBy", "show"):
    if op == "show":
        jobs += 2
    else:
        plan.append(op)
print(plan, jobs)
''',
    notes={3: 'Action :: Only show() starts work: 2 jobs in our lab.', 6: 'Transformations :: Each one only extends the plan.'},
)

WORKED_INTRO = 'Three everyday decisions about sessions and DataFrames.'
EXAMPLES = [
    dict(level='b', tag='Setup · basics', title='A portable session',
         problem='<p>Write the session code for a job that runs locally and on a cluster.</p>',
         inp='one Python file',
         approach=['Builder with an app name only.', 'Master from spark-submit.', 'SQL settings from --conf.'],
         code='''print("""from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("orders-daily").getOrCreate()
# local test:   spark-submit --master local[2] job.py
# cluster:      spark-submit --master yarn --conf spark.sql.shuffle.partitions=200 job.py""")
''', notes={2: 'Portable :: No master in the code, so spark-submit decides.'},
         tryit='Module 11 covers spark-submit in depth.'),
    dict(level='i', tag='Code design', title='Library functions take the session',
         problem='<p>A shared module needs Spark. How should it get the session?</p>',
         inp='team_utils.py',
         approach=['Accept spark (or a DataFrame) as a parameter.', 'No builder config inside.', 'Or use SparkSession.active().'],
         code='''def daily_revenue(spark, path):
    return f"spark.read.parquet({path!r}).groupBy('city').sum('amount')"
print(daily_revenue("spark", "/data/orders"))
''', notes={1: 'Injected :: The caller controls configuration.'},
         tryit='Step 2: a helper changed 8 partitions to 50.'),
    dict(level='a', tag='Reading plans', title='Find the pushed filter',
         problem='<p>Prove that a filter is applied while reading, not after.</p>',
         inp='q.explain()',
         approach=['Read the plan bottom-up.', 'Look for PushedFilters in the scan.', 'Check ReadSchema has only needed columns.'],
         code='''scan = "FileScan csv [city,amount,status] PushedFilters: [IsNotNull(status), EqualTo(status,DELIVERED)]"
print("pushed:", "EqualTo(status,DELIVERED)" in scan)
print("columns read:", scan[scan.index("[") + 1:scan.index("]")])
''', notes={2: 'Pushdown :: Formats such as Parquet can skip data using pushed filters.'},
         tryit='Lesson 7.3 explains Catalyst and explain() fully.'),
]

QUIZ = mix([
    dict(q='Beginner: What is the entry point for DataFrames and SQL?', options=['SparkContext', 'SparkSession', 'SQLContext only', 'Executor'], answer=1,
         why='spark = SparkSession.builder…getOrCreate().'),
    dict(q='Beginner: What does getOrCreate() return if a session exists?', options=['An error', 'The existing session', 'A second SparkContext', 'None'], answer=1,
         why='s2 is spark → True.'),
    dict(q='Beginner: What is a DataFrame?', options=['A Python list', 'A distributed table with named, typed columns', 'A file format', 'A cluster'], answer=1,
         why='A table with a schema.'),
    dict(q='Intermediate: How many jobs ran while building a where/groupBy/orderBy query?', options=['3', '0', '1', '2'], answer=1,
         why='Transformations only plan; show() ran 2.'),
    dict(q='Intermediate: A second builder sets shuffle partitions to 50. What happens?', options=['Ignored', 'Applied to the existing session', 'A new SparkContext starts', 'Error'], answer=1,
         why='8 became 50 in our lab.'),
    dict(q='Intermediate: What does newSession() share with the original session?', options=['Temp views', 'SQL conf', 'The SparkContext and executors', 'Nothing'], answer=2,
         why='Views and SQL settings are separate.'),
    dict(q='Advanced: Why was amount inferred as a string?', options=['CSV has no numbers', 'One value, "abc", was not a number', 'ANSI mode', 'Header missing'], answer=1,
         why='inferSchema picks a type that fits every value.'),
    dict(q='Advanced: A DataFrame query and the same SQL query…', options=['Run on different engines', 'Produce the same optimized plan', 'SQL is always faster', 'DataFrame skips Catalyst'], answer=1,
         why='Both go through Catalyst.'),
])

REVISION = [
    '<b>SparkSession</b>: entry point for DataFrames and SQL; wraps the SparkContext (<code>spark.sparkContext</code>).',
    '<code>getOrCreate()</code> returns the existing session but applies runtime SQL settings (8 → 50 in our lab).',
    '<code>newSession()</code>: own temp views and SQL conf, shared SparkContext.',
    'A <b>DataFrame</b> is an immutable distributed table with a schema; <code>printSchema()</code>, <code>dtypes</code>, <code>columns</code>.',
    'Lazy: building a query ran 0 jobs; <code>show()</code> ran 2.',
    'Read <code>explain()</code> bottom-up; look for pushed filters and pruned columns.',
    'DataFrame and SQL share Catalyst: identical plans.',
]
FAQ = [
    ('Do I still need SparkContext?', 'Only for the RDD API, broadcast variables and accumulators. Get it from <code>spark.sparkContext</code>; never create a second one.'),
    ('Should I call spark.stop()?', 'At the end of a script, yes, it releases executors. In notebooks and on Databricks, do not stop the platform’s session.'),
    ('What about SQLContext and HiveContext?', 'Old entry points from Spark 1.x. SparkSession replaced them; use <code>.enableHiveSupport()</code> on the builder for a Hive metastore (Lesson 7.2).'),
    ('Is a DataFrame the same as a pandas DataFrame?', 'No. A Spark DataFrame is distributed and lazy; pandas is in one machine’s memory and eager. Lesson 4.6 converts between them.'),
    ('What is a Dataset?', 'A typed DataFrame in Scala and Java. In Python there is only the DataFrame, which is a Dataset of Row.'),
]

PRACTICE_INTRO = 'Programs about sessions, laziness and plans.'
PROBLEMS = [
    dict(level='easy', title='Columns added', stmt='Columns after adding one with withColumn.', inp='orders has 8 columns',
         code='''print(8 + 1, "in the new DataFrame;", 8, "in orders")
''', explain='DataFrames are immutable.'),
    dict(level='easy', title='Share of a city', stmt='Mumbai’s share of the top-5 revenue.', inp='lab revenue',
         code='''rev = {"Mumbai": 2712820, "Bengaluru": 2499060, "Pune": 2148270, "Hyderabad": 1627080, "Delhi": 1501340}
print(f"{rev['Mumbai'] / sum(rev.values()):.1%}")
''', explain='Aggregate in Spark; compute small shares anywhere.'),
    dict(level='easy', title='Row to dict', stmt='Turn a result row into a dict.', inp="Row(city='Mumbai', revenue=2712820)",
         code='''row = ("Mumbai", 2712820); names = ("city", "revenue")
print(dict(zip(names, row)))
''', explain='r.asDict() in PySpark.'),
    dict(level='medium', title='Bad values', stmt='Count values that are not integers.', inp='a column read as strings',
         code='''vals = ["530", "500", "abc", "410"]
print(sum(not v.isdigit() for v in vals))
''', explain='One bad value turned the column into strings.'),
    dict(level='medium', title='Tasks per shuffle', stmt='Tasks in the reduce stage for each setting.', inp='8 vs 50 partitions, 2 shuffles',
         code='''for p in (8, 50):
    print(p, "partitions ->", 2 * p, "reduce tasks")
''', explain='Small data does not need 50 partitions.'),
    dict(level='medium', title='Read a plan', stmt='List plan operators bottom-up.', inp='explain() lines',
         code='''plan = ["Sort", "Exchange rangepartitioning", "HashAggregate", "Exchange hashpartitioning", "HashAggregate partial", "Project", "Filter", "FileScan"]
print(" -> ".join(reversed(plan)))
''', explain='Execution starts at the scan.'),
    dict(level='business', title='Revenue in lakh', stmt='Show the top city’s revenue in lakh rupees.', inp='₹2,712,820',
         code='''print(round(2712820 / 1e5, 2), "lakh")
''', explain='Format numbers for business readers.'),
    dict(level='business', title='Idle cluster cost', stmt='Cost of a job stuck on one node due to a hard-coded master.', inp='3 h, 10-node cluster at ₹400 per node-hour',
         code='''print("₹", 3 * 10 * 400)
''', explain='The cluster was paid for but unused.'),
]

SCN_INTRO = 'Session and DataFrame questions open almost every PySpark interview.'
SCENARIOS = (
    scn('Any company · PySpark', 'Fresher', '“SparkSession vs SparkContext?”',
        'Explain the difference between SparkSession and SparkContext.',
        'do you know the entry points?',
        '<p>SparkContext is the connection to the cluster used by the RDD API. SparkSession, since Spark 2.0, is the single entry point for DataFrames, SQL and the catalog; it wraps a SparkContext, available as <code>spark.sparkContext</code>. One application has one SparkContext and normally one session.</p>', '“They are the same thing.”') +
    scn('Data engineering', 'Fresher', 'What is lazy evaluation in DataFrames?',
        'Why does nothing happen when I run a where and a groupBy?',
        'do you know transformations vs actions?',
        '''<ul>
          <li>Transformations build a logical plan; actions run it.</li>
          <li>Lazy plans let Catalyst optimise the whole query (pushdown, pruning).</li>
          <li>In our lab: 0 jobs while building, 2 jobs at show().</li>
        </ul>''', 'Saying each line runs immediately like pandas.') +
    scn('Data engineering', 'Mid-level', 'Settings changed by themselves',
        'Shuffle partitions changed mid-notebook. Why?',
        'do you know getOrCreate semantics?',
        '''<ol>
          <li>Another builder call with config reached the existing session.</li>
          <li>getOrCreate returns the same session and applies runtime SQL settings.</li>
          <li>Pass the session to helpers; set config once (spark-submit or job config).</li>
        </ol>''', 'Restarting the cluster without finding the cause.') +
    scn('Platform', 'Senior', 'Multi-tenant Spark',
        'Many analysts share one Spark server. How do you isolate them?',
        'do you know session isolation limits?',
        '''<ul>
          <li>newSession per user: own temp views, SQL conf, functions.</li>
          <li>Shared: executors, cache, global temp views; use scheduler pools or separate apps for resource isolation.</li>
          <li>Spark Connect gives each client a server-side session.</li>
        </ul>''', 'Claiming sessions isolate CPU and memory.')
)
