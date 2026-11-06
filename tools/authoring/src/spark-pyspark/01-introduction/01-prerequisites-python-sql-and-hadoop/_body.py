import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
def lines(n, *keys):
    return '\n'.join(l for l in capf(n).split('\n') if any(k in l for k in keys))

def opbox(x, y, label, sub='', tone='card', w=128, h=26):
    o = box(x, y, w, h, tone) + t(x + w / 2, y + (11 if sub else 16), label, 7.2, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 21, sub, 6.4, 'ink2', mono=True)
    return o

# ---------------------------------------------------------------- story
sc = (opbox(14, 16, 'Python', 'lambda · map · dict', 'blue', 120, 28) + opbox(14, 52, 'SQL', 'GROUP BY · JOIN · CAST', 'green', 120, 28) +
      opbox(14, 88, 'Java 17 / 21', 'Spark runs on the JVM', 'amber', 120, 28) + opbox(14, 124, 'Hadoop ideas', 'blocks · cluster · YARN', 'violet', 120, 28) +
      ''.join(arrow(136, y, 226, 82, 'acc', 1.4) for y in (30, 66, 102, 138)) +
      box(230, 54, 150, 56, 'acc') + t(305, 78, 'PySpark', 10, bold=True) + t(305, 96, 'Python API for Spark', 7.2, 'ink2') +
      box(410, 12, 222, 136, 'card') + t(521, 30, 'What Riya’s laptop showed', 8.6, bold=True) +
      ''.join(t(422, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
          ('no Java → JAVA_GATEWAY_EXITED', 'red'), ('1 bad row → amount is a string', 'amber'),
          ("CAST('abc') → CAST_INVALID_INPUT", 'red'), ('pandas and Spark: same totals', 'green'),
          ('87 MiB file → 2 partitions', 'ink'), ('lambda/map/reduce: same idea', 'green')])))
scene_svg = scene('Four things PySpark builds on: Python, SQL, a Java runtime and the ideas of distributed storage and computing. Each one showed up on Riya’s laptop before she wrote any real Spark code.', sc,
                  'PySpark is <tspan font-weight="700" class="s-acc">Python on top of</tspan> a distributed SQL engine.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“My notebook froze at six months of orders”</h2>
  <div class="story">
    <p class="narration">Riya, the data intern at TiffinGo, has a pandas notebook that builds the weekly city report. It worked for one month of orders. Marketing now wants six months, every city, every day, and the notebook freezes her laptop. Arjun Sir suggests Spark. Kabir, who just finished the Hive course, wants to join.</p>

{scene_svg}

R> Sir, I know pandas. Can I just start writing Spark?
A> Almost. PySpark looks like pandas but behaves like a distributed SQL engine that runs on Java. So you need four things: <b>Python</b> (functions, lambdas, dictionaries), <b>SQL</b> (grouping, joins, types), a <b>Java runtime</b>, and the <b>Hadoop ideas</b> of splitting data into blocks and spreading work over machines.
K> I know SQL and Hadoop from Hive. What can go wrong?
A> Let us find out on Riya’s laptop before we write a single real Spark job. Today every output is real: Python 3.13, PySpark 4.3.0 and Java 21.
  </div>
</section>
'''

lv = '''
LEVELS> Prerequisites at three levels
L1> What you need to know
      <ul>
        <li><b>Python</b>: variables, lists, dictionaries, functions, <code>lambda</code>, loops.</li>
        <li><b>SQL</b>: <code>SELECT … WHERE … GROUP BY … ORDER BY</code>, joins, data types.</li>
        <li><b>Basic Linux</b>: running a command, setting an environment variable, reading an error.</li>
        <li>Spark needs <b>Java</b> installed even when you only write Python.</li>
      </ul>
L2> Why each one matters in PySpark
      <ul>
        <li>Spark’s API is functional: <code>filter</code>, <code>map</code>, <code>reduce</code> and <code>groupBy</code> are the same ideas as in plain Python, applied to data on many machines.</li>
        <li>DataFrames are SQL tables in disguise: every <code>df.groupBy()</code> becomes a SQL plan, and Spark 4 follows ANSI SQL rules for types and casts.</li>
        <li>Your Python program only <b>drives</b> a Java process (through Py4J); without Java, nothing starts.</li>
        <li>Spark reads files in <b>partitions</b>, the same idea as HDFS blocks: one task per partition.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>No Java: <code>JAVA_HOME is not set</code>, then <code>[JAVA_GATEWAY_EXITED]</code>.</li>
        <li>One row with <code>amount = abc</code> made the whole column a string in <b>both</b> pandas and Spark; an ANSI cast failed with <code>CAST_INVALID_INPUT</code>, <code>try_cast</code> returned NULL.</li>
        <li>An 87 MiB file became <b>2</b> partitions on a 2-core laptop, not 1: Spark sizes splits from the cores too, not only from a block size.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>What you need before PySpark</h2>
''' + def_block(
    '<b>PySpark</b> is the Python API for Apache Spark. A PySpark program is ordinary Python that builds descriptions of computations (DataFrames, SQL queries, RDD operations); Spark’s engine, which runs on the Java Virtual Machine, turns them into tasks that run in parallel over partitions of the data. Working with PySpark therefore requires Python programming (functions, lambdas, collections), SQL (relational operations and data types, under Spark’s ANSI-compliant rules), a supported Java runtime (Java 17 or 21 for Spark 4.x), and the concepts of distributed data processing: data split into partitions or blocks, work spread over executors, and data moved between machines in a shuffle.',
    'PySpark lets you write Spark programs in Python. Python describes the work, Spark (running on Java) does it in parallel. So you need Python, SQL, Java installed, and the idea of splitting data over many machines.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('PySpark', 'Spark’s Python API: <code>pip install pyspark</code>.'),
    ('JVM', 'Java Virtual Machine. Spark’s engine runs inside it.'),
    ('Py4J', 'The bridge that lets Python call Spark’s Java objects.'),
    ('DataFrame', 'A distributed table with named, typed columns.'),
    ('Partition', 'One slice of the data; one task processes one partition.'),
    ('ANSI mode', 'Strict SQL rules (on by default since Spark 4.0): bad casts fail.'),
    ('lambda', 'A small unnamed Python function, e.g. <code>lambda x: x * 2</code>.'),
    ('Shuffle', 'Moving rows between machines so equal keys meet (for groupBy, join).'),
]) + '''

  <h3>From what you know to what Spark does</h3>
''' + table(['You already know', 'In PySpark it becomes', 'Seen in this lesson'], [
    ['Python <code>filter</code> / <code>map</code> / <code>reduce</code>', '<code>df.where()</code>, <code>df.withColumn()</code>, <code>agg()</code> over partitions', 'Step 3: the same logic on a Python list'],
    ['pandas <code>groupby().sum()</code>', '<code>df.groupBy().agg(F.sum())</code>', 'Step 4: identical city totals'],
    ['SQL <code>CAST</code>', 'ANSI <code>cast</code> fails on bad data; <code>try_cast</code> gives NULL', 'Step 5: <code>CAST_INVALID_INPUT</code>'],
    ['HDFS blocks of 128 MB', 'Input partitions sized by <code>maxPartitionBytes</code> <b>and</b> cores', 'Step 6: 87 MiB → 2, 3 or 11 partitions'],
    ['Installing Python packages', 'pip install pyspark <b>plus</b> a Java 17/21 runtime', 'Step 2: no Java, no Spark'],
], minw=760) + lv + '''
EXAM> “What are the prerequisites for PySpark?” Python (functions, lambdas, collections), SQL, a Java runtime (Java 17 or 21 for Spark 4), and distributed-computing basics such as partitions, parallel tasks and shuffles. Pandas experience helps, because the DataFrame API is similar, but Spark is lazy and distributed.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Who comes to PySpark from where</h2>
''' + table(['Your background', 'What feels familiar', 'What will surprise you', 'Start with'], [
    ['pandas / data analyst', 'DataFrames, groupby, columns', 'Laziness, no row index, ANSI type errors', 'Modules 4–6'],
    ['SQL / BI developer', 'Spark SQL, joins, windows', 'Python API, partitions, the Spark UI', 'Module 7, then 4'],
    ['Hive / Hadoop engineer', 'Metastore tables, HDFS, YARN', 'In-memory caching, DataFrame API, AQE', 'Modules 2–3, 7.2'],
    ['Java / Scala developer', 'JVM, typed APIs', 'Python workers, UDF costs, Arrow', 'Modules 4 and 6.6'],
    ['Data scientist', 'pandas, scikit-learn', 'MLlib pipelines, distributed training limits', 'Module 10'],
], minw=760) + '''
WARN> PySpark code looks like pandas, which is exactly why beginners trip. A pandas line runs immediately on one machine; a PySpark line usually just <b>adds a step to a plan</b> that runs later on many machines. Lessons 1.4 and 2.3 show this with real timings.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Checking every prerequisite on a real laptop</h2>
  <p>All outputs are real, from the course lab: Python 3.13, PySpark 4.3.0 (released 30 October 2026) and OpenJDK 21. The data is TiffinGo’s <code>orders.csv</code> from the Hive course: 50,002 orders, two of them deliberately broken.</p>
''' + stepper([
    ('Step 1 · Check Python, PySpark, pandas and Java',
     code('bash', 'terminal', 'python3 --version\npython3 -c "import pyspark, pandas, pyarrow; print(pyspark.__version__, pandas.__version__, pyarrow.__version__)"\njava -version', capf('l11_env.txt')),
     'Spark 4.x needs <b>Java 17 or 21</b> and, since Spark 4.1, <b>Python 3.10 or newer</b>. pandas and PyArrow are optional, but many PySpark features (<code>toPandas()</code>, pandas UDFs, the pandas API on Spark) use them. Our pandas is 3.0.5, and PySpark warned on import:\n\n<code>' + capf('l11_pandas_warn.txt').split('\n')[0].split('FutureWarning: ')[1] + '</code>\n\nThe course lab therefore pins <code>pandas&lt;3</code> in its Docker image (Lesson 1.5).'),
    ('Step 2 · What happens without Java',
     code('python', 'start_spark.py', 'from pyspark.sql import SparkSession\nspark = SparkSession.builder.master("local[1]").getOrCreate()', capf('l11_nojava.txt')),
     'We ran the same Python with Java removed from the <code>PATH</code>. The Python package was fine; the error came from the launcher script (<code>JAVA_HOME is not set</code>) and then from PySpark, because the Java process it starts in the background never came up. If you see <code>JAVA_GATEWAY_EXITED</code>, check Java first.'),
    ('Step 3 · The Python you need: filter, map, reduce, group',
     code('python', 'plain_python.py', "from functools import reduce\norders = [(\"Mumbai\", 530), (\"Pune\", 210), (\"Mumbai\", 480), (\"Delhi\", 990), (\"Pune\", 120)]\nbig = list(filter(lambda o: o[1] >= 300, orders))           # keep orders of 300 or more\ngst = list(map(lambda o: (o[0], round(o[1] * 0.05, 2)), big)) # 5% GST on each\ntotal = reduce(lambda a, b: a + b, [g for _, g in gst])       # add them up\nby_city = {}\nfor city, amt in orders:                                      # group by city\n    by_city[city] = by_city.get(city, 0) + amt", capf('l11_python.txt')),
     'These four patterns are the heart of Spark. <code>filter</code> and <code>map</code> work on each row independently, so Spark can run them on every partition at once. <code>reduce</code> and grouping need rows from different partitions to meet, which is what a <b>shuffle</b> does. If <code>lambda o: o[1] &gt;= 300</code> reads naturally to you, you are ready for RDDs in Module 2.'),
    ('Step 4 · The same question in pandas and PySpark',
     code('python', 'compare.py', "import pandas as pd\npdf = pd.read_csv(\"orders.csv\")\nprint(\"pandas dtypes:\", dict(pdf.dtypes.astype(str)))\npdf[\"amount\"] = pd.to_numeric(pdf[\"amount\"], errors=\"coerce\")\nprint(pdf.groupby(\"city\")[\"amount\"].sum().sort_values(ascending=False).head(3))\n\nfrom pyspark.sql import SparkSession, functions as F\nspark = SparkSession.builder.master(\"local[2]\").getOrCreate()\ndf = spark.read.csv(\"orders.csv\", header=True, inferSchema=True)\ndf.printSchema()\ndf.groupBy(\"city\").agg(F.sum(F.col(\"amount\").try_cast(\"double\")).alias(\"amount\")) \\\n  .orderBy(F.desc(\"amount\")).show(3)", re.sub(r' {20,}', '', capf('l11_compare.txt'))),
     'Identical totals, and the <b>same data problem</b> in both tools: one row has <code>amount = abc</code>, so pandas read the column as <code>str</code> and Spark’s schema inference chose <code>string</code>. Another row has a date in <code>31/10/2026 21:20</code> format, so <code>order_ts</code> is a string too. Knowing your data types is a prerequisite, not an extra.'),
    ('Step 5 · SQL types under ANSI rules',
     code('python', 'ansi.py', "print(\"spark.sql.ansi.enabled =\", spark.conf.get(\"spark.sql.ansi.enabled\"))\ndf.select(F.sum(F.col(\"amount\").cast(\"double\"))).show()            # strict cast\ndf.select(F.sum(F.col(\"amount\").try_cast(\"double\")).alias(\"total\"),\n          F.count_if(F.col(\"amount\").try_cast(\"double\").isNull()).alias(\"bad_rows\")).show()",
          capf('l11_ansi.txt').split('\n')[0] + '\n' + lines('l11_ansi.txt', 'SparkNumberFormatException').split('Correct the')[0] + '…\n' + '\n'.join(capf('l11_ansi.txt').split('\n')[-5:])),
     'Since Spark 4.0, <b>ANSI mode is on by default</b>: a cast that cannot succeed stops the job, as in a standard SQL database. In Spark 3 the same cast silently returned NULL. <code>try_cast</code> gives NULL on purpose, and <code>count_if</code> tells you how many rows failed (1). Your SQL knowledge carries over directly; just expect strictness.'),
    ('Step 6 · Hadoop’s block idea, Spark’s partitions',
     code('python', 'partitions.py', "for mb in (128, 32, 8):\n    spark.conf.set(\"spark.sql.files.maxPartitionBytes\", f\"{mb}m\")\n    n = spark.read.csv(\"big_csv\", header=True).rdd.getNumPartitions()\n    print(f\"maxPartitionBytes={mb:>3} MiB -> {n:>2} partitions (= tasks in the first stage)\")", capf('l11_blocks.txt')),
     'On HDFS a file is cut into 128 MB blocks. Spark cuts input into <b>partitions</b>, and the first stage runs one task per partition. With the 128 MiB default our 87 MiB file still became <b>2</b> partitions, because Spark also divides the input by the number of cores (2 here) so that every core gets work. Partitions return in Lessons 1.4, 2.4 and 8.1.'),
    ('Step 7 · When does pandas stop being enough?',
     code('python', 'memory.py', "df = pd.read_csv(\"orders.csv\")\nprint(df.memory_usage(deep=True).sum() / 2**20, \"MiB\")", capf('l11_mem.txt')),
     'pandas loads everything into one process’s memory: here 1.7 times the file size (pandas 3 stores strings compactly; with older pandas it is often 3–5×). One laptop with 16 GB therefore handles a few GB comfortably. TiffinGo’s six months are tens of GB, and growing. Spark splits the data so no single machine needs to hold it all. For data that fits on one machine, pandas, Polars or DuckDB are often simpler (Lesson 12.2).'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('$ java -version', W), ('openjdk version "21.0.12.1"', G), ('pyspark 4.3.0 · python 3.13.17', G), ('no Java → JAVA_GATEWAY_EXITED', RD)], size=7.4),
    term([('filter : 3 big orders', W), ('map    : 5% GST each', W), ('reduce : 100.0', G), ("groupBy: {'Mumbai': 1010, …}", G)], size=7.4),
    term([('pandas  amount: str', Y), ('spark   amount: string', Y), ('Mumbai 2941330.0 in both', G)], size=7.6),
    term([("CAST('abc' AS DOUBLE)", W), ('[CAST_INVALID_INPUT]', RD), ('try_cast → NULL, bad_rows = 1', G)], size=7.6),
    term([('87 MiB, 128 MiB max → 2 partitions', W), ('32 MiB max → 3 partitions', W), ('8 MiB max → 11 partitions', W)], size=7.4),
]
def stack(hi):
    o = ''
    for k, (name, sub, y) in enumerate([('Your Python code', 'PySpark API', 26), ('Py4J bridge', 'calls into the JVM', 64), ('Spark engine (Java)', 'plans · tasks', 102)]):
        o += opbox(40, y, name, sub, 'acc' if k == hi else ['blue', 'violet', 'amber'][k], 140, 28)
    o += arrow(110, 54, 110, 64, 'ink3', 1.4) + arrow(110, 92, 110, 102, 'ink3', 1.4)
    o += opbox(220, 102, 'partitions', 'p0 p1 p2 …', 'green' if hi != 3 else 'acc', 110, 28) + arrow(180, 116, 220, 116, 'ink3', 1.4)
    return o
B1 = [
    t(180, 16, 'Python drives a Java engine', 9.4, bold=True) + stack(2) + cap('No JVM, no Spark.', '', 'amber', y=144, h=30),
    t(180, 16, 'Row-by-row vs needs-all-rows', 9.4, bold=True) + stack(0) + cap('filter/map: per partition · group/reduce: shuffle.', '', 'blue', y=144, h=30),
    t(180, 16, 'Types decide everything', 9.4, bold=True) + stack(0) + cap('One bad value → a string column.', '', 'amber', y=144, h=30),
    t(180, 16, 'ANSI SQL rules', 9.4, bold=True) + stack(2) + cap('Strict cast fails; try_cast tolerates.', '', 'violet', y=144, h=30),
    t(180, 16, 'Blocks become partitions', 9.4, bold=True) + stack(3) + cap('One task per partition.', '', 'green', y=144, h=30),
]
see_caps = ['Java 21 and PySpark 4.3.0 found; without Java, Spark cannot start.',
            'Plain Python already uses Spark’s core ideas.',
            'One broken row made amount a string in pandas and Spark.',
            'Spark 4 refused the bad cast; try_cast counted it.',
            'Spark split the file into 2, 3 or 11 partitions.']
behind_caps = ['PySpark starts a JVM and talks to it through Py4J.',
               'Independent steps run in parallel; grouping needs a shuffle.',
               'Schema inference picks the type that fits every value.',
               'ANSI mode is the default since Spark 4.0.',
               'Split size depends on maxPartitionBytes and cores.']
two = anim_two('PySpark prerequisites', 'Python on top of a Java engine', 'Real lab outputs', 'What is underneath', see, B1, see_caps, behind_caps)

# ---- scenario 1: notebook freeze
e1 = (t(180, 22, 'Weekly city report in pandas', 9.4, bold=True) + t(180, 56, '1 month: 40 s · 6 months: laptop freezes', 8.2, 'ink2') + cap('Data outgrew one machine.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Check the size', 9.4, bold=True) + t(180, 56, 'memory_usage(deep=True) ≈ 1.7–5 × file', 8.2, 'ink', mono=True) + cap('More than the laptop’s RAM.', '', 'amber', y=150, h=34))
e3 = (t(180, 22, 'Same logic in PySpark', 9.4, bold=True) + t(180, 56, 'groupBy("city").agg(F.sum("amount"))', 8, 'ink', mono=True) + cap('Same answer, partitioned work.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Fix types first', 9.4, bold=True) + t(180, 56, 'try_cast + count bad rows', 8.4, 'ink', mono=True) + cap('Before trusting totals.', '', 'amber', y=150, h=34))
e5 = (t(180, 22, 'Run on the cluster', 9.4, 'acc', bold=True) + t(180, 56, 'same code, more executors', 8.4, 'ink2') + cap('Lessons 1.3–1.5.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'From a frozen notebook to PySpark',
              'A very common first contact with Spark. (Typical path; numbers from our lab.)',
              'pandas to PySpark', 'Measure memory, port the same groupBy to PySpark, fix types with try_cast, then scale out', [e1, e2, e3, e4, e5],
              ['pandas hits the memory wall.',
               'Measure, do not guess.',
               'Port the logic.',
               'Clean the types.',
               'Scale out.'],
              hid='scenario-notebook')

# ---- scenario 2: silent NULLs after upgrade
b1 = (t(180, 22, 'Upgrade Spark 3.5 → 4.x', 9.4, bold=True) + t(180, 56, 'nightly job fails on day one', 8.4, 'ink2') + cap('CAST_INVALID_INPUT', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Spark 3: silent NULLs', 9.4, bold=True) + t(180, 56, "CAST('abc') → NULL, no error", 8.4, 'ink', mono=True) + cap('Bad rows were hidden for years.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'Spark 4: ANSI on', 9.4, bold=True) + t(180, 56, 'spark.sql.ansi.enabled = true', 8.4, 'ink', mono=True) + cap('Bad data now stops the job.', '', 'violet', y=150, h=34))
b4 = (t(180, 22, 'Fix deliberately', 9.4, bold=True) + t(180, 56, 'try_cast + quarantine bad rows', 8.4, 'ink2') + cap('Count them; alert on growth.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Not: switch ANSI off', 9.4, 'acc', bold=True) + t(180, 56, 'that only hides the problem again', 8.2, 'ink2') + cap('Data quality is a prerequisite.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'A job that breaks after the Spark 4 upgrade',
              'What Step 5 means for existing pipelines. (Typical; behaviour from our lab.)',
              'ANSI mode', 'Spark 4 fails on casts Spark 3 silently turned into NULL; use try_cast and quarantine bad rows instead of disabling ANSI', [b1, b2, b3, b4, b5],
              ['Upgrade, then failure.',
               'Old behaviour hid errors.',
               'New default is strict.',
               'Handle bad rows explicitly.',
               'Keep ANSI on.'],
              hid='scenario-ansi')

# ---- scenario 3: onboarding checklist
u1 = (t(180, 22, 'New joiner, day one', 9.4, bold=True) + t(180, 56, '“Spark does not start”', 8.4, 'ink2') + cap('Usually the environment.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'java -version', 9.4, bold=True) + t(180, 56, '17 or 21 for Spark 4.x', 8.4, 'ink', mono=True) + cap('JAVA_HOME set?', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'python --version', 9.4, bold=True) + t(180, 56, '3.10+ · same minor on all machines', 8.2, 'ink', mono=True) + cap('Mismatch breaks Python UDFs (1.5).', '', 'amber', y=150, h=34))
u4 = (t(180, 22, 'pip pins', 9.4, bold=True) + t(180, 56, 'pyspark==4.3.0 · pandas<3 · pyarrow', 8.2, 'ink', mono=True) + cap('One requirements file.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Smoke test', 9.4, 'acc', bold=True) + t(180, 56, 'spark.range(5).count() == 5', 8.4, 'ink', mono=True) + cap('Then real work.', '', 'green', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'A team checklist for new laptops',
              'How data teams avoid a day of setup problems. (Typical practice.)',
              'Environment checklist', 'Check Java, Python and package versions, pin them in one file and run a smoke test before real work', [u1, u2, u3, u4, u5],
              ['Spark does not start.',
               'Check Java.',
               'Check Python.',
               'Pin packages.',
               'Smoke test.'],
              hid='scenario-checklist')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Python on top of a Java engine</h2>
  <p>Left: real outputs. Right: what is underneath.</p>
''' + two + '''
  <p>Three live scenarios follow: a frozen notebook, an upgrade that breaks on bad data, and a setup checklist.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Where these prerequisites show up at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'pandas', 11, 'blue', bold=True) + t(60, 58, '→ Spark', 7.4, 'ink2'),
    '1. Moving notebooks to PySpark',
    'Analysts port pandas reports to PySpark when data outgrows one machine; the groupBy logic stays, the execution model changes.',
    ['pandas', '*PySpark', 'Cluster']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'SQL', 12, 'green', bold=True) + t(60, 58, 'first', 7.4, 'ink2'),
    '2. SQL people on Spark',
    'BI developers write Spark SQL from day one; the DataFrame API follows the same relational ideas.',
    ['SQL skills', '*Spark SQL', 'Reports']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, "JVM", 12, "acc", bold=True) + t(60, 58, 'ops', 7.4, 'ink2'),
    '3. Platform images with pinned Java and Python',
    'Platform teams ship one image with Java, Python and package versions fixed for laptops, CI and clusters.',
    ['Pins', '*image', 'Same everywhere']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'ANSI', 12, 'violet', bold=True) + t(60, 58, 'quality', 7.4, 'ink2'),
    '4. Data-quality checks',
    'try_cast and bad-row counts become standard checks in pipelines after the Spark 4 upgrade.',
    ['Raw data', '*try_cast', 'Quarantine']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'hiring', 10, 'acc', bold=True) + t(60, 58, 'tests', 7.4, 'ink2'),
    '5. Interview screens',
    'Data engineering interviews test Python, SQL and partition basics before any Spark-specific question.',
    ['Python + SQL', '*screen', 'Spark round']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Coming from the Hive course?</b> You already know SQL, HDFS and YARN, and the TiffinGo data. Skim Steps 1–3 and focus on Steps 4–6.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
