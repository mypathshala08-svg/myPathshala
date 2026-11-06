import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
def part(n, a, b=None):
    s = capf(n)
    i = s.index(a)
    j = s.index(b, i + 1) if b else len(s)
    return s[i:j].rstrip()

def opbox(x, y, label, sub='', tone='card', w=128, h=26):
    o = box(x, y, w, h, tone) + t(x + w / 2, y + (11 if sub else 16), label, 7.2, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 21, sub, 6.4, 'ink2', mono=True)
    return o

# ---------------------------------------------------------------- story
sc = (opbox(14, 20, 'MapReduce (2004–)', 'disk after every step', 'card', 150, 30) +
      ''.join(box(20 + k * 36, 64, 28, 18, 'amber') + t(34 + k * 36, 76, 'disk', 6.4, 'ink2') for k in range(4)) +
      t(89, 104, 'read → map → write → read → reduce', 6.6, 'ink2', mono=True) +
      arrow(170, 60, 232, 60, 'acc', 2) +
      box(236, 22, 150, 76, 'green') + t(311, 44, 'Spark (2009–)', 9, bold=True) + t(311, 62, 'keeps data in memory', 7.2, 'ink2') + t(311, 78, 'between steps', 7.2, 'ink2') +
      box(410, 12, 222, 136, 'card') + t(521, 30, 'One engine, measured', 8.6, bold=True) +
      ''.join(t(422, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
          ('3 questions, no cache : 6.6 s', 'amber'), ('3 questions, cached   : 1.6 s', 'green'),
          ('SQL · DataFrame · pandas API', 'ink'), ('MLlib · Structured Streaming', 'ink'),
          ('same 5,000,000 orders', 'green'), ('Spark 4.3.0, Oct 2026', 'ink')])))
scene_svg = scene('MapReduce writes to disk between every step; Spark keeps intermediate data in memory and offers SQL, DataFrames, pandas-style code, machine learning and streaming on one engine.', sc,
                  'Spark is one engine for <tspan font-weight="700" class="s-acc">batch, SQL, ML and streaming</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Why not just use Hive for everything?”</h2>
  <div class="story">
    <p class="narration">Kabir has built TiffinGo’s warehouse in Hive. Riya needs the same orders for a churn model in Python and for a live dashboard of orders per minute. Kabir suggests three tools: Hive for SQL, a Python library for the model, something else for streaming. Arjun Sir suggests one.</p>

{scene_svg}

K> Sir, Hive already runs SQL on the cluster. What does Spark add?
A> Three things. Spark keeps data in <b>memory</b> between steps, so repeated and iterative work is much faster. It gives one engine for <b>SQL, Python DataFrames, machine learning and streaming</b>. And it runs the same code on a laptop, a Hadoop cluster, Kubernetes or a cloud service.
R> Can we see that, not just hear it?
A> Today we run five Spark components on the same five million TiffinGo orders, measure what caching does, and look at the newest Spark 4 features. Then we place Spark in its history, from a Berkeley research project to the most widely used big data engine.
  </div>
</section>
'''

lv = '''
LEVELS> Spark at three levels
L1> A big, fast shared kitchen
      <ul>
        <li>One head chef (the driver) splits a huge order into small dishes (tasks).</li>
        <li>Many cooks (executors) prepare them at the same time.</li>
        <li>Ingredients already chopped stay on the counter (memory) instead of going back to the store-room (disk).</li>
      </ul>
L2> What Spark is made of
      <ul>
        <li><b>Spark Core</b>: scheduling, memory, fault tolerance, the RDD API.</li>
        <li><b>Spark SQL / DataFrames</b>: the main API today, optimised by the Catalyst optimizer; the <b>pandas API on Spark</b> sits on top.</li>
        <li><b>Structured Streaming</b>, <b>MLlib</b>, <b>Spark Connect</b> (remote clients) and, since 4.1, <b>Declarative Pipelines</b>. GraphX and the old DStreams API are legacy.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>SQL, DataFrame and pandas-API code gave the same city totals on 5,000,000 orders; KMeans and a streaming query ran in the same session.</li>
        <li>Three questions on a 2,000,000-row CSV took <b>6.6 s</b> uncached and <b>1.6 s</b> after <code>cache()</code>.</li>
        <li>Spark 4 SQL pipe syntax and the <code>VARIANT</code> type worked out of the box in 4.3.0.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>What Apache Spark is</h2>
''' + def_block(
    '<b>Apache Spark</b> is an open-source, distributed engine for large-scale data processing. A Spark application consists of a <b>driver</b> that plans the work and <b>executors</b> that run tasks in parallel on partitions of the data, on a single machine or on a cluster managed by Spark standalone, YARN or Kubernetes. Spark keeps intermediate data in memory where possible, recovers lost work from the recorded lineage of each dataset, and provides unified APIs in Python, Scala, Java, SQL and R for batch processing (Spark SQL and DataFrames), streaming (Structured Streaming), machine learning (MLlib) and remote clients (Spark Connect).',
    'Spark is a free engine that processes big data on many machines at once. It keeps data in memory when it can, so it is fast, and the same engine does SQL, Python data work, machine learning and streaming.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Driver', 'The process that runs your program and plans the work.'),
    ('Executor', 'A worker process that runs tasks and can cache data.'),
    ('RDD', 'Resilient Distributed Dataset: Spark’s original low-level API.'),
    ('DataFrame', 'A distributed table; the main API since Spark 2.'),
    ('Catalyst', 'Spark SQL’s query optimizer.'),
    ('In-memory', 'Keeping data in RAM between steps instead of writing it to disk.'),
    ('Lineage', 'The recorded steps that built a dataset; used to recompute lost data.'),
    ('Spark Connect', 'A client–server protocol so thin clients can use a remote Spark.'),
]) + '''

  <h3>Spark’s history in eight dates</h3>
''' + table(['Year', 'Event', 'Why it matters'], [
    ['2009', 'Started by Matei Zaharia at UC Berkeley’s AMPLab', 'Research on fast, iterative cluster computing'],
    ['2010', 'Open-sourced', 'The RDD paper followed in 2012'],
    ['2013–2014', 'Donated to Apache; top-level project in Feb 2014; Spark 1.0 in May 2014', 'Databricks founded by the creators (2013)'],
    ['2014', 'Daytona GraySort: 100 TB sorted in 23 min on 206 machines', 'Hadoop MapReduce’s record: 72 min on 2,100 machines'],
    ['2016', 'Spark 2.0: DataFrames and Datasets unified, Structured Streaming', 'SQL engine at the centre'],
    ['2020', 'Spark 3.0: Adaptive Query Execution, Python focus', 'Big performance gains for SQL workloads'],
    ['2025', 'Spark 4.0 (May): ANSI by default, VARIANT, pipe syntax, Java 17+', '4.1 (Dec): Declarative Pipelines, SQL scripting'],
    ['2026', '4.2 (Jul) and <b>4.3.0 (30 Oct)</b>', 'The version used in this course'],
], minw=720) + lv + '''
EXAM> “What is Apache Spark and why is it faster than MapReduce?” A distributed, in-memory data processing engine with unified APIs for SQL, streaming, ML and graphs. It is faster mainly because it keeps intermediate data in memory and builds an optimised plan (DAG) for the whole job, instead of writing to disk after every map and reduce step.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Spark’s components and when to use each</h2>
''' + table(['Component', 'Use it for', 'Status in Spark 4.3', 'Course module'], [
    ['Spark SQL and DataFrames', 'ETL, reporting, joins, most work', 'Main API', '4–7'],
    ['pandas API on Spark', 'pandas-style code on big data', 'Supported (watch pandas versions)', '4.6, 12.2'],
    ['Structured Streaming', 'Kafka/files to tables, near-real-time', 'Main streaming API; Real-time Mode experimental', '9'],
    ['MLlib (<code>pyspark.ml</code>)', 'Pipelines, features, classic ML', 'Supported', '10'],
    ['Spark Connect', 'Notebooks and apps using a remote cluster', 'Mature since 4.0', '11.3'],
    ['Declarative Pipelines', 'Declaring tables and flows; Spark manages order', 'New in 4.1', '11'],
    ['RDD API (Spark Core)', 'Low-level control, unstructured data', 'Supported; DataFrames preferred', '2–3'],
    ['DStreams, GraphX', 'Old streaming, graph processing', 'Legacy', 'mentioned only'],
], minw=760) + table(['', 'Hadoop MapReduce', 'Hive on Tez', 'Apache Spark'], [
    ['Between steps', 'Writes to HDFS', 'Pipelined DAG, some disk', 'Memory where possible, DAG'],
    ['Languages', 'Java', 'SQL', 'Python, SQL, Scala, Java, R'],
    ['Iterative work (ML)', 'Very slow', 'Not designed for it', 'Fast with cache()'],
    ['Streaming', 'No', 'No', 'Structured Streaming'],
    ['Runs on', 'YARN', 'YARN', 'Local, standalone, YARN, Kubernetes, cloud'],
], minw=680) + '''
WARN> “100× faster than Hadoop” comes from old benchmarks of iterative, in-memory workloads. For a single scan of data on disk, Spark and Hive on Tez can be close. In our lab, caching made repeated questions <b>4×</b> faster, not 100×. Measure your own jobs.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>One engine, five components, one dataset</h2>
  <p>All outputs are real: PySpark 4.3.0 in local mode on the course lab machine, using <code>orders_big</code>: 5,000,000 generated TiffinGo orders in 8 Parquet files (Lesson 1.5 shows how it was made).</p>
''' + stepper([
    ('Step 1 · Spark SQL',
     code('python', 'components.py', 'orders = spark.read.parquet("orders_big").where("status = \'DELIVERED\'")\norders.createOrReplaceTempView("orders")\nspark.sql("SELECT city, COUNT(*) AS orders FROM orders GROUP BY city ORDER BY orders DESC LIMIT 3").show()', part('l12_components.txt', '+', '2)')),
     'Plain SQL on a temporary view. Anyone from the Hive course can use Spark from the first day. The SQL runs on the same engine as everything that follows.'),
    ('Step 2 · The DataFrame API',
     code('python', 'components.py', 'from pyspark.sql import functions as F\norders.groupBy("city").agg(F.round(F.avg("amount"), 2).alias("avg_amount")).orderBy("city").show(3)', part('l12_components.txt', '+', '3)')),
     'The same kind of question as Python method calls. DataFrame code and SQL compile to the <b>same plan</b> in Catalyst, so neither is faster; choose what reads better for the task.'),
    ('Step 3 · pandas API on Spark',
     code('python', 'components.py', 'import pyspark.pandas as ps\npdf = orders.pandas_api()\nprint(pdf.groupby("city")["amount"].sum().sort_values(ascending=False).head(3))', part('l12_components.txt', 'city\n', '4)')),
     'pandas syntax, Spark execution: <code>pdf</code> is distributed, not in local memory. Mumbai’s total (484,935,971) matches the SQL view. Useful for porting pandas code; for new code most teams use DataFrames.'),
    ('Step 4 · MLlib',
     code('python', 'components.py', 'from pyspark.ml.feature import VectorAssembler\nfrom pyspark.ml.clustering import KMeans\nsample = orders.sample(fraction=0.01, seed=1).select("amount")\nvec = VectorAssembler(inputCols=["amount"], outputCol="features").transform(sample)\nmodel = KMeans(k=3, seed=1).fit(vec)\nprint(sorted(round(float(c[0]), 1) for c in model.clusterCenters()))', part('l12_components.txt', 'order-size', '5)')),
     'K-means found three order sizes (about ₹210, ₹512 and ₹811) on a 1% sample. K-means repeats passes over the data until the centres stop moving: exactly the <b>iterative</b> workload where keeping data in memory matters most.'),
    ('Step 5 · Structured Streaming',
     code('python', 'components.py', 'q = (spark.readStream.format("rate").option("rowsPerSecond", 5).load()\n     .writeStream.format("memory").queryName("ticks").start())\ntime.sleep(6); q.stop()\nprint(spark.sql("SELECT COUNT(*) FROM ticks").first()[0])', part('l12_components.txt', 'rows received')),
     'A test source generating 5 rows per second, written to an in-memory table: 25 rows arrived before we stopped it (the first micro-batch starts after a short delay). The same DataFrame operations work on streams; Module 9 uses Kafka.'),
    ('Step 6 · Why in-memory matters',
     code('python', 'cache.py', "def three_questions(df):\n    df.groupBy(\"city\").count().collect()\n    df.agg(F.avg(\"amount\")).collect()\n    df.where(\"amount > 900\").count()\n\nsrc = spark.read.csv(\"big_csv\", header=True).withColumn(\"amount\", F.col(\"amount\").cast(\"int\"))\nthree_questions(src)                      # timed\ncached = src.cache(); cached.count()\nthree_questions(cached)                   # timed", capf('l12_cache.txt')),
     'Without caching, every question re-read and re-parsed the 2,000,000-row CSV. After <code>cache()</code>, the parsed rows stayed in executor memory and the same three questions took about a quarter of the time. MapReduce has no equivalent: each job starts from disk. Caching is covered properly in Lesson 3.1.'),
    ('Step 7 · Spark 4 features, live',
     code('sql', 'spark.sql(…)', "FROM orders\n|> WHERE status = 'CANCELLED'\n|> AGGREGATE COUNT(*) AS cancelled GROUP BY city\n|> ORDER BY cancelled DESC\n|> LIMIT 3;\n\nSELECT v:restaurant::string AS restaurant, v:items[0].dish::string AS first_dish, v:rating::double AS rating\nFROM (SELECT parse_json('{\"restaurant\":\"Desai Mess\",\"items\":[{\"dish\":\"Idli\",\"qty\":2}],\"rating\":4.8}') AS v);", re.sub(r'-- [^\n]*\n', '', capf('l12_new.txt'))),
     'Two Spark 4.0 additions that work in 4.3.0: <b>SQL pipe syntax</b> (<code>|&gt;</code>), which reads top to bottom in the order the steps run, and the <b>VARIANT</b> type, which stores JSON efficiently and extracts fields with paths like <code>v:items[0].dish</code>. Lesson 12.3 covers what is new in Spark 4.x.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('SELECT city, COUNT(*) … GROUP BY city', W), ('Mumbai     951430', G), ('Bengaluru  949842', G)], size=7.6),
    term([('pdf = orders.pandas_api()', W), ('pdf.groupby("city")["amount"].sum()', W), ('Mumbai  484935971', G)], size=7.4),
    term([('KMeans(k=3).fit(vec)', W), ('centres: 210.4, 511.8, 810.5', G), ('several passes over the data', Y)], size=7.4),
    term([('without cache: 6.6 s', Y), ('cache(); count()', W), ('with cache   : 1.6 s', G)], size=7.8),
    term([("FROM orders |> WHERE … |> AGGREGATE …", W), ('Bengaluru 50373 · Mumbai 49775', G), ("parse_json(…) → v:items[0].dish = Idli", G)], size=7.0),
]
def eng(hi):
    names = [('SQL', 12), ('DataFrame', 80), ('pandas API', 148), ('MLlib', 216), ('Streaming', 284)]
    o = ''
    for k, (n, x) in enumerate(names):
        o += opbox(x, 30, n, '', 'acc' if k in hi else 'blue', 62, 24)
        o += arrow(x + 31, 56, 180, 78, 'ink3', 1.1)
    o += box(60, 80, 240, 30, 'amber') + t(180, 99, 'Spark SQL engine · Catalyst · Spark Core', 7.6, bold=True)
    return o
B1 = [
    t(180, 16, 'Many APIs, one engine', 9.4, bold=True) + eng([0]) + cap('SQL compiles to the same plan as DataFrames.', '', 'blue', y=132, h=34),
    t(180, 16, 'pandas syntax, distributed data', 9.4, bold=True) + eng([2]) + cap('Not loaded into local memory.', '', 'green', y=132, h=34),
    t(180, 16, 'Iterative algorithms', 9.4, bold=True) + eng([3]) + cap('Repeated passes reward memory.', '', 'violet', y=132, h=34),
    t(180, 16, 'Memory instead of disk', 9.4, bold=True) + eng([1]) + cap('Parsed rows stay in executors.', 'MapReduce re-reads from disk.', 'amber', y=126, h=44),
    t(180, 16, 'Still evolving', 9.4, bold=True) + eng([0]) + cap('Spark 4: pipe syntax, VARIANT, ANSI.', '', 'blue', y=132, h=34),
]
see_caps = ['Spark SQL answered first.',
            'pandas-style code gave the same totals.',
            'K-means found three order sizes.',
            'Caching made the same questions 4× faster.',
            'Spark 4 SQL features in 4.3.0.']
behind_caps = ['All APIs share one optimizer and one engine.',
               'pyspark.pandas translates to Spark plans.',
               'Each iteration reads the same data again.',
               'cache() keeps data between actions.',
               'New syntax, same engine underneath.']
two = anim_two('What Spark is', 'One engine, many APIs', 'Real lab outputs', 'What Spark does', see, B1, see_caps, behind_caps)

# ---- scenario 1: three tools vs one
e1 = (t(180, 22, 'Three teams, three tools', 9.4, bold=True) + t(180, 56, 'Hive SQL · Python ML · a stream processor', 8.2, 'ink2') + cap('Three copies of the logic.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Numbers disagree', 9.4, bold=True) + t(180, 56, '“revenue” defined three ways', 8.4, 'ink2') + cap('Meetings about numbers.', '', 'amber', y=150, h=34))
e3 = (t(180, 22, 'One engine', 9.4, bold=True) + t(180, 56, 'Spark SQL + MLlib + Structured Streaming', 8.2, 'ink2') + cap('Shared code and tables.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Shared functions', 9.4, bold=True) + t(180, 56, 'def revenue(df): …  used by all', 8.4, 'ink', mono=True) + cap('Batch and stream reuse it.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Fewer systems to run', 9.4, 'acc', bold=True) + t(180, 56, 'one cluster, one skill set', 8.4, 'ink2') + cap('The “unified engine” benefit.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Three tools or one engine',
              'Why companies standardise on Spark. (Typical story.)',
              'Unified engine', 'SQL, ML and streaming in one engine let teams share logic and tables instead of keeping three copies', [e1, e2, e3, e4, e5],
              ['Three tools.', 'Three answers.', 'One engine.', 'One definition.', 'Less to operate.'],
              hid='scenario-unified')

# ---- scenario 2: ML iterations
b1 = (t(180, 22, 'Churn model, 20 iterations', 9.4, bold=True) + t(180, 56, 'each pass reads all features', 8.4, 'ink2') + cap('Classic iterative job.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'MapReduce style', 9.4, bold=True) + t(180, 56, '20 × read from disk', 8.4, 'ink', mono=True) + cap('Hours.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'Spark with cache()', 9.4, bold=True) + t(180, 56, '1 read, 19 passes from memory', 8.4, 'ink', mono=True) + cap('Our lab: 4× for 3 questions.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Check it fits', 9.4, bold=True) + t(180, 56, 'Storage tab: fraction cached', 8.4, 'ink2') + cap('Partly cached = partly slow.', '', 'amber', y=150, h=34))
b5 = (t(180, 22, 'Unpersist after', 9.4, 'acc', bold=True) + t(180, 56, 'df.unpersist()', 8.4, 'ink', mono=True) + cap('Free memory for the next job.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Where in-memory processing pays off',
              'The workload Spark was invented for. (Typical; speed-up from our lab.)',
              'Iterative processing', 'Cache data that is read many times, check it fits in memory, and release it afterwards', [b1, b2, b3, b4, b5],
              ['Many passes.', 'Disk every time.', 'Memory instead.', 'Verify caching.', 'Clean up.'],
              hid='scenario-iterative')

# ---- scenario 3: pick the right tool
u1 = (t(180, 22, '“Should we use Spark?”', 9.4, bold=True) + t(180, 56, 'a question in every design review', 8.4, 'ink2') + cap('Not always yes.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Data fits one machine?', 9.4, bold=True) + t(180, 56, 'pandas · Polars · DuckDB', 8.4, 'ink2') + cap('Simpler, often faster.', '', 'green', y=150, h=34))
u3 = (t(180, 22, 'Interactive BI on tables?', 9.4, bold=True) + t(180, 56, 'Trino or a warehouse', 8.4, 'ink2') + cap('Low-latency SQL.', '', 'violet', y=150, h=34))
u4 = (t(180, 22, 'Big ETL, ML, streams?', 9.4, bold=True) + t(180, 56, 'Spark', 9, 'acc', bold=True) + cap('Its home ground.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Millisecond event processing?', 9.4, 'acc', bold=True) + t(180, 56, 'Flink (or Spark Real-time Mode)', 8.2, 'ink2') + cap('Check latency needs.', '', 'amber', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'When Spark is the right choice',
              'A design-review checklist. (Typical guidance; Lesson 12.2 goes deeper.)',
              'Choosing Spark', 'Use single-machine tools for small data, Trino for interactive SQL, Spark for large ETL, ML and streaming, Flink for very low latency', [u1, u2, u3, u4, u5],
              ['Ask the question.', 'Small data.', 'Interactive SQL.', 'Large processing.', 'Very low latency.'],
              hid='scenario-choose')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>One engine, many APIs</h2>
  <p>Left: real outputs. Right: what Spark does underneath.</p>
''' + two + '''
  <p>Three live scenarios follow: one engine instead of three tools, iterative work, and when to choose Spark.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Spark at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'ETL', 12, 'blue', bold=True) + t(60, 58, 'lakehouse', 7.4, 'ink2'),
    '1. Data lake and lakehouse ETL',
    'Spark is the standard engine for turning raw files into Parquet, Delta or Iceberg tables on S3, ADLS or HDFS.',
    ['Raw files', '*Spark', 'Tables']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'ML', 12, 'green', bold=True) + t(60, 58, 'features', 7.4, 'ink2'),
    '2. Machine learning at scale',
    'AWS cites Yelp training ad-click models and The Washington Post building recommendations with Spark on EMR.',
    ['Events', '*features', 'Models']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'stream', 11, 'violet', bold=True) + t(60, 58, 'trends', 7.4, 'ink2'),
    '3. Near-real-time analytics',
    'Hearst used Spark Streaming to see which articles were trending; Kafka-to-table pipelines are common everywhere.',
    ['Kafka', '*Streaming', 'Dashboard']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'security', 9, 'acc', bold=True) + t(60, 58, 'events', 7.4, 'ink2'),
    '4. Security and log analytics',
    'CrowdStrike processes hundreds of terabytes of endpoint events with Spark to find malicious activity (AWS case study).',
    ['Logs', '*Spark', 'Alerts']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'cloud', 11, 'acc', bold=True) + t(60, 58, 'services', 7.4, 'ink2'),
    '5. Managed Spark everywhere',
    'Databricks, Amazon EMR, Google Dataproc, Azure Synapse and Microsoft Fabric all run Spark as a service.',
    ['Your code', '*managed Spark', 'No servers']) + '''
  <p class="muted">Customer examples are from the providers’ public pages; simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> Lesson <a href="../01-prerequisites-python-sql-and-hadoop/">1.1</a> (prerequisites). Knowing MapReduce from the Hadoop course helps with the comparison.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
