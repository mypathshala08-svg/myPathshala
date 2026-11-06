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
    module='01-introduction', lesson='01-prerequisites-python-sql-and-hadoop', n='1.1',
    module_label='Module 1 · Start here: why Spark?',
    title='Prerequisites: Python, SQL and Hadoop in one lesson',
    desc='Everything you need before PySpark, checked on a real laptop with PySpark 4.3.0, Python 3.13 and Java 21: what happens without Java (JAVA_GATEWAY_EXITED), the filter/map/reduce/group patterns in plain Python, the same city report in pandas and PySpark, one bad row turning a column into a string, Spark 4’s ANSI cast errors and try_cast, how a file becomes partitions, and when pandas stops being enough.',
    og_desc='No Java, no Spark; one bad row, a string column; one bad cast, a failed job. The PySpark prerequisites, checked on a real laptop.',
    minutes=30, level='Beginner',
    lead='Module 1 starts the Apache Spark and PySpark course. Before writing real Spark code, this lesson refreshes the four things PySpark builds on: <b>Python</b>, <b>SQL</b>, a <b>Java runtime</b> and the <b>ideas of distributed data</b>. Every check runs on a real laptop with PySpark 4.3.0, and every output is real.',
    chips=['PySpark 4.3.0 · Python 3.13 · Java 21', 'Real outputs', 'pandas vs PySpark', 'Runs in your browser (Python)'],
)

MAIN = '''# Spark's core patterns in plain Python (this runs in your browser)
from functools import reduce
orders = [("Mumbai", 530), ("Pune", 210), ("Mumbai", 480), ("Delhi", 990), ("Pune", 120)]

big = list(filter(lambda o: o[1] >= 300, orders))
gst = list(map(lambda o: (o[0], round(o[1] * 0.05, 2)), big))
total = reduce(lambda a, b: a + b, [g for _, g in gst])

by_city = {}
for city, amt in orders:
    by_city[city] = by_city.get(city, 0) + amt

print("filter :", big)
print("map    :", gst)
print("reduce :", total)
print("groupBy:", by_city)
'''
RUN = dict(
    heading='Run the code: Spark’s ideas in plain Python',
    intro='<p>PySpark itself cannot run in the browser, but its core ideas can. These programs use plain Python with the same logic as the lesson’s Spark examples. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('big = list(filter(lambda o: o[1] >= 300, orders))', 'Like df.where(F.col("amount") >= 300): each row is checked on its own.'),
        ('total = reduce(lambda a, b: a + b, [g for _, g in gst])', 'Like F.sum(): values from all rows are combined, which in Spark needs data from every partition.'),
    ],
    tasks=[
        dict(label='1 · Run the patterns', hint='Press <b>Run</b>. Change the threshold from 300 to 500 and predict the new total.', code=None),
        dict(label='2 · Predict first: partitions', hint='<b>Predict first:</b> split the orders into two “partitions”, sum each, then combine. Is the answer the same?',
             code='''orders = [("Mumbai", 530), ("Pune", 210), ("Mumbai", 480), ("Delhi", 990), ("Pune", 120)]
p0, p1 = orders[:3], orders[3:]
partial = [sum(a for _, a in p) for p in (p0, p1)]     # one task per partition
print("partials:", partial, " total:", sum(partial))
'''),
        dict(label='3 · try_cast in Python', hint='Spark’s try_cast returns NULL for bad values. Write the Python version.',
             code='''def try_cast(s):
    try:
        return float(s)
    except ValueError:
        return None
vals = ["530", "abc", "210"]
casted = [try_cast(v) for v in vals]
print(casted, " bad rows:", casted.count(None), " total:", sum(v for v in casted if v is not None))
'''),
        dict(label='4 · Memory estimate', hint='Will six months fit in pandas on a 16 GB laptop? Use the 1.7–5× factor from Step 7.',
             code='''file_gb = 2.9 / 1024 * 30 * 6     # 2.9 MiB per ~5 days of orders, scaled up (illustrative)
for factor in (1.7, 5):
    print(f"factor {factor}: {file_gb * factor:.2f} GB in memory")
'''),
        dict(label='5 · Spot the error', hint='This “sum” silently skips bad values. Make it report them.', expect='error',
             code='''vals = ["530", "abc", "210"]
good = [float(v) for v in vals if v.replace(".", "").isdigit()]
bad = len(vals) - len(good)
assert bad == 0, f"{bad} row(s) could not be cast; quarantine them instead of ignoring"
print(sum(good))
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: three quick checks',
    intro='<p>Run these after installing PySpark (Lesson 1.5 has the full setup). <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Versions', cmd='python3 -c "import pyspark; print(pyspark.__version__)"\njava -version', file='terminal',
             output='4.3.0\n' + capf('l11_env.txt').split('\n')[-1],
             note='Spark 4.x supports Java 17 and 21. Java 8 and 11 are no longer supported.'),
        dict(title='2 · Is ANSI mode on?', cmd='spark.conf.get("spark.sql.ansi.enabled")', file='pyspark',
             output="'true'",
             note='True by default since Spark 4.0. Keep it on and handle bad values with try_cast.'),
        dict(title='3 · How many partitions?', cmd='spark.read.csv("big_csv", header=True).rdd.getNumPartitions()', file='pyspark',
             output='2',
             note='87 MiB on a 2-core laptop with default settings. Change spark.sql.files.maxPartitionBytes and read again.'),
    ],
)

TRACE = dict(
    heading='How a grouped sum works in partitions',
    intro='<p>Follow how Spark-style partial sums combine into the final answer, using plain Python.</p>',
    code='''p0 = [("Mumbai", 530), ("Pune", 210), ("Mumbai", 480)]
p1 = [("Delhi", 990), ("Pune", 120)]
def partial(rows):
    out = {}
    for c, a in rows:
        out[c] = out.get(c, 0) + a
    return out
a, b = partial(p0), partial(p1)
final = {c: a.get(c, 0) + b.get(c, 0) for c in set(a) | set(b)}
print(a, b, final)
''',
    notes={3: 'Partial :: Each partition sums its own rows, like Spark’s partial_sum.', 8: 'Shuffle :: Rows with the same city from both partitions meet here.', 9: 'Final :: Pune 330 = 210 from p0 + 120 from p1.'},
)

WORKED_INTRO = 'Three small decisions every new PySpark user faces.'
EXAMPLES = [
    dict(level='b', tag='Setup · environment', title='Is my laptop ready?',
         problem='<p>Write a checklist script that prints the versions Spark depends on.</p>',
         inp='Python, Java, PySpark',
         approach=['Check Python ≥ 3.10.', 'Check Java 17 or 21.', 'Import pyspark.'],
         code='''import sys
py_ok = sys.version_info >= (3, 10)
java = "21.0.12"          # from java -version
java_ok = java.split(".")[0] in ("17", "21")
print("python ok:", py_ok, "| java ok:", java_ok)
''', notes={3: 'Java :: Spark 4.x runs on Java 17 or 21.'},
         tryit='Run the real checks from Step 1 on your machine.'),
    dict(level='i', tag='Data quality · ANSI', title='Count bad values before summing',
         problem='<p>Total the amounts but report how many rows could not be converted.</p>',
         inp='amount column with “abc”',
         approach=['try_cast to double.', 'count_if NULL.', 'Sum the rest.'],
         code='''print("df.select(")
print("  F.sum(F.col('amount').try_cast('double')).alias('total'),")
print("  F.count_if(F.col('amount').try_cast('double').isNull()).alias('bad_rows'))")
''', notes={3: 'count_if :: Gives 1 for TiffinGo’s orders.csv.'},
         tryit='Store bad rows in a separate quarantine table instead of dropping them.'),
    dict(level='a', tag='Architecture · sizing', title='pandas or Spark?',
         problem='<p>Decide which tool fits three TiffinGo datasets.</p>',
         inp='sizes in GB',
         approach=['Estimate in-memory size.', 'Compare with one machine.', 'Leave headroom.'],
         code='''ram_gb = 16
for name, gb in {"one week": 0.4, "six months": 12, "all history": 300}.items():
    need = gb * 3
    tool = "pandas/Polars/DuckDB" if need < ram_gb * 0.5 else "Spark"
    print(f"{name:12} {gb:6} GB -> {tool}")
''', notes={4: 'Factor :: 3× is a middle value between our 1.7× and older pandas’ 5×.'},
         tryit='Lesson 12.2 compares Spark with single-machine tools in detail.'),
]

QUIZ = mix([
    dict(q='Beginner: Why does PySpark need Java installed?', options=['It does not', 'Spark’s engine runs on the JVM; Python drives it', 'For the browser UI only', 'To compile Python'], answer=1,
         why='Without Java: JAVA_GATEWAY_EXITED.'),
    dict(q='Beginner: Which Java versions does Spark 4.x support?', options=['8 and 11', '17 and 21', 'Only 25', 'Any'], answer=1,
         why='Java 8 and 11 were dropped in Spark 4.0.'),
    dict(q='Beginner: Which Python function is like df.where()?', options=['map', 'filter', 'reduce', 'zip'], answer=1,
         why='Both keep rows matching a condition.'),
    dict(q='Intermediate: One row has amount “abc”. What type did schema inference give amount?', options=['int', 'double', 'string', 'decimal'], answer=2,
         why='The type must fit every value.'),
    dict(q='Intermediate: What does CAST(\'abc\' AS DOUBLE) do in Spark 4 by default?', options=['Returns NULL', 'Fails with CAST_INVALID_INPUT', 'Returns 0', 'Skips the row'], answer=1,
         why='ANSI mode is on by default since 4.0.'),
    dict(q='Intermediate: How do you get NULL instead of an error for bad values?', options=['cast', 'try_cast', 'coalesce', 'dropna'], answer=1,
         why='try_cast tolerates malformed input.'),
    dict(q='Advanced: An 87 MiB file with a 128 MiB maxPartitionBytes became how many partitions on 2 cores?', options=['1', '2', '128', '0'], answer=1,
         why='Spark also divides input by the number of cores.'),
    dict(q='Advanced: Which needs a shuffle when distributed?', options=['filter', 'map', 'group by city', 'select columns'], answer=2,
         why='Rows of the same city must meet.'),
])

REVISION = [
    'PySpark = Python API; the engine runs on the <b>JVM</b> (Py4J bridge). No Java → <code>JAVA_GATEWAY_EXITED</code>.',
    'Spark 4.x: <b>Java 17 or 21</b>; Spark 4.1+: <b>Python 3.10+</b>. pandas 3 triggered a warning in PySpark 4.3: pin <code>pandas&lt;3</code>.',
    'filter/map work per row (parallel); group/reduce need rows to meet (shuffle).',
    'pandas and PySpark gave the same city totals; both read <code>amount</code> as string because of one bad row.',
    '<b>ANSI mode</b> is on by default: bad casts fail (<code>CAST_INVALID_INPUT</code>); <code>try_cast</code> returns NULL.',
    'Input is split into <b>partitions</b>; one task per partition. Split size depends on <code>maxPartitionBytes</code> and cores.',
    'pandas holds data in one process (1.7× the CSV here); beyond one machine’s memory, use Spark.',
]
FAQ = [
    ('Do I need to know Scala or Java?', 'No. You need Java installed, not Java skills. Reading a Java stack trace helps, because Spark errors often contain one; the useful line is usually the first one with an error class such as CAST_INVALID_INPUT.'),
    ('Do I need Hadoop installed?', 'No. PySpark from pip includes the Hadoop client libraries it needs and runs on your local file system. Knowing HDFS and YARN helps when you deploy on a Hadoop cluster (Lesson 11.2).'),
    ('Is pandas knowledge required?', 'Helpful, not required. The DataFrame API has similar ideas, and Spark offers a pandas API (pyspark.pandas) for pandas-style code on a cluster.'),
    ('Which Python version should I use?', 'A supported version that is the same on your laptop, the driver and all executors. Lesson 1.5 shows the error when the driver uses 3.13 and executors use 3.12.'),
    ('Can I use Windows?', 'Yes, with Java and Python installed; writing files may additionally need Hadoop’s winutils on Windows. The course lab uses Docker, which works the same on Windows, macOS and Linux (Lesson 1.5).'),
]

PRACTICE_INTRO = 'Small Python programs that rehearse Spark’s patterns.'
PROBLEMS = [
    dict(level='easy', title='Filter big orders', stmt='Keep orders of 500 or more.', inp='list of (city, amount)',
         code='''orders = [("Mumbai", 530), ("Pune", 210), ("Delhi", 990)]
print([o for o in orders if o[1] >= 500])
''', explain="PySpark: df.where(F.col('amount') >= 500)."),
    dict(level='easy', title='Add a column', stmt='Add 5% GST to each order.', inp='list of amounts',
         code='''amounts = [530, 210, 990]
print([(a, round(a * 0.05, 2)) for a in amounts])
''', explain="PySpark: df.withColumn('gst', F.col('amount') * 0.05)."),
    dict(level='easy', title='Count by city', stmt='Count orders per city.', inp='list of cities',
         code='''from collections import Counter
print(Counter(["Mumbai", "Pune", "Mumbai", "Delhi"]))
''', explain="PySpark: df.groupBy('city').count()."),
    dict(level='medium', title='Partial sums', stmt='Sum per partition, then combine.', inp='two partitions',
         code='''parts = [[530, 480], [990, 120, 210]]
partial = [sum(p) for p in parts]
print(partial, sum(partial))
''', explain='This is how Spark computes a global sum: partial_sum per task, then one final sum.'),
    dict(level='medium', title='Bad value report', stmt='Report rows that are not numbers.', inp='string amounts',
         code='''vals = ["530", "abc", "210", "4x0"]
bad = [v for v in vals if not v.isdigit()]
print("bad:", bad)
''', explain='In Spark: count_if(try_cast(amount) IS NULL) and keep those rows in a quarantine table.'),
    dict(level='medium', title='Partition count', stmt='Estimate partitions for a file.', inp='87 MiB, 8 MiB max splits',
         code='''import math
print(math.ceil(87 / 8))
''', explain='Spark gave 11, matching this estimate.'),
    dict(level='business', title='Laptop or cluster?', stmt='Estimate memory needed for 6 months in pandas.', inp='12 GB of CSV, factor 1.7–5',
         code='''for f in (1.7, 5):
    print(f, "->", 12 * f, "GB")
''', explain='20–60 GB: more than a 16 GB laptop. A small Spark cluster handles it.'),
    dict(level='business', title='Cost of silent NULLs', stmt='Revenue missed if bad rows are silently NULL.', inp='0.2% bad rows, ₹1.5 crore weekly revenue (illustrative)',
         code='''print(f"₹{1.5e7 * 0.002:,.0f} per week not counted")
''', explain='ANSI errors make this visible instead of silently lowering totals.'),
]

SCN_INTRO = 'Prerequisite questions open most PySpark interviews.'
SCENARIOS = (
    scn('Any company · PySpark', 'Fresher', '“What is PySpark?”',
        'Explain PySpark and what it needs.',
        'do you understand the Python/JVM split?',
        '<p>PySpark is Spark’s Python API. My Python code builds DataFrame or SQL operations; Spark’s engine on the JVM plans and runs them as parallel tasks over partitions. It needs Python, a Java 17/21 runtime and the pyspark package; on a cluster, the same Python version on every node.</p>', 'Saying PySpark is a Python re-implementation of Spark.') +
    scn('Data engineering', 'Fresher', 'pandas vs PySpark',
        'When would you use PySpark instead of pandas?',
        'can you reason about data size?',
        '''<ul>
          <li>pandas: data fits comfortably in one machine’s memory; eager, simple.</li>
          <li>PySpark: data larger than one machine, or the same job must scale; lazy and distributed.</li>
          <li>For medium data on one machine, Polars or DuckDB are also good choices.</li>
        </ul>''', '“PySpark is always faster.”') +
    scn('Data engineering', 'Mid-level', 'Job fails after upgrade with CAST_INVALID_INPUT',
        'A Spark 3 job fails on Spark 4 with CAST_INVALID_INPUT.',
        'do you know ANSI mode?',
        '''<ol>
          <li>Spark 4 enables ANSI mode by default; invalid casts now fail instead of returning NULL.</li>
          <li>Use try_cast where bad values are expected, count and quarantine them.</li>
          <li>Avoid disabling ANSI globally; it hides data problems.</li>
        </ol>''', 'Setting spark.sql.ansi.enabled=false everywhere.') +
    scn('Platform', 'Mid-level', '“Java gateway process exited”',
        'A teammate gets JAVA_GATEWAY_EXITED when creating a SparkSession.',
        'can you debug the environment?',
        '''<ul>
          <li>Check java -version and JAVA_HOME: Spark 4 needs Java 17 or 21.</li>
          <li>Check that pyspark and the Java version match and that no old SPARK_HOME points elsewhere.</li>
          <li>Run a smoke test: spark.range(5).count().</li>
        </ul>''', 'Reinstalling Python first.')
)
