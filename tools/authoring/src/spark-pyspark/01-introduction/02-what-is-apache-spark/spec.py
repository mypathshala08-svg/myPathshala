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
    module='01-introduction', lesson='02-what-is-apache-spark', n='1.2',
    module_label='Module 1 · Start here: why Spark?',
    title='What is Apache Spark? From MapReduce to Spark 4',
    desc='What Apache Spark is, where it came from and why it replaced MapReduce for most work, shown with real PySpark 4.3.0 outputs: Spark SQL, the DataFrame API, the pandas API on Spark, MLlib and Structured Streaming on the same 5,000,000 orders; three questions taking 6.6 s without cache and 1.6 s with it; Spark 4 SQL pipe syntax and VARIANT; Spark’s components, history from 2009 to 4.3.0, and when not to use Spark.',
    og_desc='Five Spark components on the same five million orders, a 4× speed-up from caching, and Spark’s story from a Berkeley lab to Spark 4.3.',
    minutes=32, level='Beginner',
    lead='Spark is the most widely used engine for big data processing. This lesson explains <b>what Spark is</b>, what it is made of, and why it replaced MapReduce for most work. Instead of only describing the components, we run five of them on the same <b>5,000,000 TiffinGo orders</b> and measure what in-memory processing changes. <b>All outputs are real.</b>',
    chips=['PySpark 4.3.0', 'Five components, one dataset', 'Cache: 6.6 s → 1.6 s', 'Runs in your browser (Python)'],
)

MAIN = '''# Why in-memory matters: model the cost of repeated passes (lab numbers)
read_and_parse = 2.0      # seconds to read + parse the CSV once (approx. from our lab)
answer = 0.2              # seconds to answer one question once data is ready
questions = 3

no_cache = questions * (read_and_parse + answer)
with_cache = read_and_parse + questions * answer
print(f"no cache  : {no_cache:.1f} s")
print(f"with cache: {with_cache:.1f} s   ({no_cache / with_cache:.1f}x faster)")
'''
RUN = dict(
    heading='Run the code: memory versus disk',
    intro='<p>These programs model why Spark’s in-memory processing matters, using timings close to the lab’s. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('no_cache = questions * (read_and_parse + answer)', 'Every action re-reads the source, like MapReduce jobs or uncached Spark.'),
        ('with_cache = read_and_parse + questions * answer', 'Read once, then answer from executor memory.'),
    ],
    tasks=[
        dict(label='1 · Run the model', hint='Press <b>Run</b>. The lab measured 6.6 s and 1.6 s; how close is the model?', code=None),
        dict(label='2 · Predict first: 20 iterations', hint='<b>Predict first:</b> an ML algorithm makes 20 passes. What speed-up does caching give?',
             code='''read, answer, passes = 2.0, 0.2, 20
print(f"{passes * (read + answer) / (read + passes * answer):.1f}x")
'''),
        dict(label='3 · Pick the component', hint='Map each request to a Spark component.',
             code='''req = {"weekly SQL report": "Spark SQL",
       "port a pandas notebook": "pandas API on Spark",
       "orders per minute from Kafka": "Structured Streaming",
       "churn model": "MLlib"}
for k, v in req.items():
    print(f"{v:22} <- {k}")
'''),
        dict(label='4 · GraySort 2014', hint='Compare the 2014 sort records per machine.',
             code='''spark = dict(minutes=23, machines=206)
hadoop = dict(minutes=72, machines=2100)
print("Spark  machine-minutes:", spark["minutes"] * spark["machines"])
print("Hadoop machine-minutes:", hadoop["minutes"] * hadoop["machines"])
'''),
        dict(label='5 · Spot the error', hint='This claim ignores that one-pass jobs gain little from memory.', expect='error',
             code='''passes = 1
read, answer = 2.0, 0.2
speedup = passes * (read + answer) / (read + passes * answer)
assert speedup > 2, f"one pass: only {speedup:.1f}x; caching helps repeated reads"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: which Spark do I have?',
    intro='<p>Quick checks after installing PySpark (Lesson 1.5). <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Spark version', cmd='spark.version', file='pyspark', output="'4.3.0'",
             note='Released 30 October 2026. 4.2.x, 4.1.x, 4.0.x and 3.5.x also received maintenance releases in 2026.'),
        dict(title='2 · Pipe syntax', cmd="spark.sql(\"FROM orders |> WHERE status = 'CANCELLED' |> AGGREGATE COUNT(*) AS cancelled GROUP BY city |> ORDER BY cancelled DESC |> LIMIT 3\").show()", file='pyspark',
             output=capf('l12_new.txt').split('-- VARIANT')[0].replace('-- SQL pipe syntax (Spark 4.0+)\n', '').rstrip(),
             note='Spark 4.0+. The same query in classic SQL works too.'),
        dict(title='3 · Cache a DataFrame', cmd='df = spark.read.csv("big_csv", header=True).cache()\ndf.count()\ndf.is_cached', file='pyspark', output='2000000\nTrue',
             note='The first action fills the cache; later actions read from memory. See the Storage tab in the Spark UI (Lesson 1.4).'),
    ],
)

TRACE = dict(
    heading='Where the time goes with and without cache',
    intro='<p>Follow the cost of three actions on the same data.</p>',
    code='''read, answer = 2.0, 0.2
t_plain = t_cached = 0.0
cached = False
for q in range(3):
    t_plain += read + answer
    if not cached:
        t_cached += read; cached = True
    t_cached += answer
print(round(t_plain, 1), round(t_cached, 1))
''',
    notes={5: 'No cache :: Every action reads and parses the CSV again.', 7: 'First action :: Reads once and fills the cache.', 8: 'Later actions :: Answer from memory.'},
)

WORKED_INTRO = 'Three ways to explain Spark’s value in real decisions.'
EXAMPLES = [
    dict(level='b', tag='Concepts · components', title='Name the component',
         problem='<p>Write which Spark component handles each TiffinGo need.</p>',
         inp='four needs',
         approach=['SQL reports → Spark SQL.', 'Streams → Structured Streaming.', 'Models → MLlib.'],
         code='''needs = {"city revenue table": "Spark SQL / DataFrames",
         "live orders per minute": "Structured Streaming",
         "delivery-time model": "MLlib",
         "notebook on a remote cluster": "Spark Connect"}
for k, v in needs.items():
    print(f"{k:30} -> {v}")
''', notes={4: 'Connect :: Thin client, the cluster does the work (Lesson 11.3).'},
         tryit='All four share one SparkSession and the same tables.'),
    dict(level='i', tag='Performance · caching', title='Is caching worth it?',
         problem='<p>Decide whether to cache a DataFrame used by several reports.</p>',
         inp='read 2.0 s, answer 0.2 s, n reports',
         approach=['Compare n × (read + answer) with read + n × answer.', 'Check memory.', 'Unpersist after.'],
         code='''read, answer = 2.0, 0.2
for n in (1, 2, 5):
    gain = n * (read + answer) - (read + n * answer)
    print(n, "reports: save", round(gain, 1), "s")
''', notes={3: 'One report :: No gain; caching only helps when data is reused.'},
         tryit='Lesson 3.1 measures cache levels and memory use.'),
    dict(level='a', tag='Architecture · selection', title='Spark or not?',
         problem='<p>Choose an engine for four workloads.</p>',
         inp='size and latency needs',
         approach=['Small → single machine.', 'Interactive SQL → Trino.', 'Big ETL/ML/streams → Spark.'],
         code='''work = [("5 GB daily report", "DuckDB/Polars"), ("2 s BI dashboard", "Trino"),
        ("3 TB nightly ETL", "Spark"), ("Kafka to lakehouse every minute", "Spark Structured Streaming")]
for w, e in work:
    print(f"{w:32} {e}")
''', notes={1: 'Small data :: Spark’s start-up and distribution overhead is not worth it.'},
         tryit='Lesson 12.2 compares these engines with real benchmarks.'),
]

QUIZ = mix([
    dict(q='Beginner: Where was Spark created?', options=['Google', 'UC Berkeley’s AMPLab', 'Yahoo', 'Facebook'], answer=1,
         why='Started in 2009 by Matei Zaharia.'),
    dict(q='Beginner: Which is the main Spark API today?', options=['RDD', 'DataFrame / Spark SQL', 'DStreams', 'GraphX'], answer=1,
         why='RDDs remain for low-level work.'),
    dict(q='Beginner: Which component processes Kafka streams?', options=['MLlib', 'GraphX', 'Structured Streaming', 'Catalyst'], answer=2,
         why='DStreams is the legacy API.'),
    dict(q='Intermediate: Why is Spark usually faster than MapReduce?', options=['Written in Python', 'Keeps intermediate data in memory and plans the whole DAG', 'Uses bigger disks', 'Skips shuffles'], answer=1,
         why='MapReduce writes to disk after each step.'),
    dict(q='Intermediate: In the lab, what did cache() change for three questions?', options=['Nothing', '6.6 s → 1.6 s', '100× faster', 'Slower'], answer=1,
         why='About 4×, not 100×.'),
    dict(q='Intermediate: SQL and DataFrame code in Spark…', options=['Use different engines', 'Compile to the same optimised plan', 'SQL is always faster', 'DataFrames are always faster'], answer=1,
         why='Both go through Catalyst.'),
    dict(q='Advanced: Which became default in Spark 4.0?', options=['ANSI SQL mode', 'Java 8', 'DStreams', 'Mesos'], answer=0,
         why='Bad casts now fail.'),
    dict(q='Advanced: For a 5 GB report on one machine, which is often simpler?', options=['A 50-node Spark cluster', 'DuckDB or Polars', 'MapReduce', 'GraphX'], answer=1,
         why='Spark’s overhead pays off for larger data.'),
])

REVISION = [
    'Spark: open-source, distributed, <b>in-memory</b> engine; driver plans, executors run tasks.',
    'Components: Spark SQL/DataFrames (main), pandas API, Structured Streaming, MLlib, Spark Connect, Declarative Pipelines (4.1); RDDs low-level; DStreams/GraphX legacy.',
    'History: AMPLab 2009 → Apache TLP 2014 → 2.0 (2016) → 3.0 (2020) → 4.0 (May 2025) → <b>4.3.0 (30 Oct 2026)</b>.',
    'Faster than MapReduce mainly through memory and whole-job DAG planning; biggest gains for iterative work.',
    'Lab: same city totals via SQL, DataFrame and pandas API; cache: <b>6.6 s → 1.6 s</b>.',
    'Spark 4: ANSI default, pipe syntax <code>|&gt;</code>, <code>VARIANT</code>, Java 17+.',
    'Not always Spark: small data → pandas/Polars/DuckDB; interactive BI → Trino; ms latency → Flink.',
]
FAQ = [
    ('Is Spark a database?', 'No. Spark processes data stored elsewhere (files, object storage, databases, Kafka). With a catalogue such as the Hive metastore or Unity Catalog it can manage tables, but storage stays in files.'),
    ('Does Spark replace Hadoop?', 'It replaced MapReduce for most processing. HDFS and YARN can still be Spark’s storage and cluster manager; many companies now use object storage and Kubernetes instead.'),
    ('Is Spark only for Python?', 'No. Scala, Java, SQL and R are also supported (SparkR is deprecated in Spark 4). PySpark is the most popular way to use Spark today, which is why this course uses it.'),
    ('What is Databricks?', 'A company founded by Spark’s creators that offers a managed Spark platform with extras (Delta Lake, Unity Catalog, Photon). Apache Spark itself is free and open source.'),
    ('Why does a tiny job take seconds?', 'Starting the JVM, scheduling tasks and planning queries have fixed costs. Our first SparkSession took about 15 s to start on the lab machine. Spark is built for data where that overhead is small compared with the work.'),
]

PRACTICE_INTRO = 'Small programs about Spark’s ideas and history.'
PROBLEMS = [
    dict(level='easy', title='Spark’s age', stmt='How many years from AMPLab to Spark 4.3?', inp='2009, 2026',
         code='''print(2026 - 2009)
''', explain='17 years of development.'),
    dict(level='easy', title='Speed-up', stmt='Compute the caching speed-up from the lab.', inp='6.6 s, 1.6 s',
         code='''print(round(6.6 / 1.6, 1))
''', explain='About 4×.'),
    dict(level='easy', title='Component lookup', stmt='Print the component for streaming.', inp='dictionary',
         code='''c = {"sql": "Spark SQL", "stream": "Structured Streaming", "ml": "MLlib"}
print(c["stream"])
''', explain='DStreams is legacy.'),
    dict(level='medium', title='GraySort per machine', stmt='Compare TB sorted per machine-hour in 2014.', inp='Spark 100 TB/23 min/206; Hadoop 102.5 TB/72 min/2100',
         code='''s = 100 / (23 / 60 * 206)
h = 102.5 / (72 / 60 * 2100)
print(round(s, 2), round(h, 3), round(s / h), "x")
''', explain='A huge efficiency gap, mostly from Spark’s shuffle and memory use.'),
    dict(level='medium', title='Iterations', stmt='Speed-up of caching for k passes.', inp='read 2 s, answer 0.2 s',
         code='''for k in (1, 3, 10, 30):
    print(k, round(k * 2.2 / (2 + 0.2 * k), 1))
''', explain='The more passes, the more caching helps, up to the limit of read time / answer time.'),
    dict(level='medium', title='Pipe to classic SQL', stmt='Rewrite the pipe query as classic SQL.', inp='pipe query from Step 7',
         code='''print("SELECT city, COUNT(*) AS cancelled FROM orders WHERE status = 'CANCELLED'")
print("GROUP BY city ORDER BY cancelled DESC LIMIT 3")
''', explain='Both run the same plan.'),
    dict(level='business', title='Fewer systems', stmt='Yearly cost of three separate engines vs one.', inp='₹12 lakh per system per year (illustrative)',
         code='''print("3 systems:", 3 * 12, "lakh   1 Spark platform:", 12 + 6, "lakh (bigger cluster)")
''', explain='A unified engine also saves duplicated logic and people time.'),
    dict(level='business', title='Analyst hours', stmt='Hours saved per week if 20 report runs are 5 s faster each.', inp='20 runs/day, 5 days',
         code='''print(20 * 5 * 5 / 3600, "hours")
''', explain='Small for one person; large across hundreds of jobs and users.'),
]

SCN_INTRO = '“What is Spark?” is the first question in nearly every data engineering interview.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“What is Apache Spark?”',
        'Explain Spark in one minute.',
        'can you be precise and brief?',
        '<p>Spark is an open-source distributed engine for large-scale data processing. A driver plans work as a DAG and executors run tasks in parallel on partitions, keeping data in memory where possible. One engine covers SQL and DataFrames, streaming and machine learning, on a laptop, YARN, Kubernetes or managed cloud services.</p>', '“Spark is a faster Hadoop database.”') +
    scn('Data engineering', 'Fresher', 'Spark vs MapReduce',
        'Why did Spark replace MapReduce?',
        'do you know the real reasons?',
        '''<ul>
          <li>In-memory processing between steps; MapReduce writes to disk after each map/reduce.</li>
          <li>Whole-job DAG optimisation and a rich API (SQL, DataFrames, Python).</li>
          <li>One engine for batch, streaming and ML.</li>
        </ul>''', 'Only quoting “100× faster”.') +
    scn('Data engineering', 'Mid-level', 'Caching decision',
        'A notebook runs 10 queries on the same filtered DataFrame and is slow.',
        'do you know when to cache?',
        '''<ol>
          <li>Each action recomputes from the source.</li>
          <li>Cache the filtered DataFrame, trigger it once, check the Storage tab.</li>
          <li>Unpersist when done; do not cache everything.</li>
        </ol>''', 'Caching every DataFrame by default.') +
    scn('Architecture', 'Senior', 'Choose an engine',
        'Teams ask for Spark for every new dataset.',
        'can you weigh alternatives?',
        '''<ul>
          <li>Spark for large ETL, ML feature pipelines and streaming to tables.</li>
          <li>Single-machine engines for small data; Trino/warehouses for interactive SQL; Flink for very low latency.</li>
          <li>Standardise on shared table formats so engines can be mixed.</li>
        </ul>''', '“Spark for everything” without size or latency analysis.')
)
