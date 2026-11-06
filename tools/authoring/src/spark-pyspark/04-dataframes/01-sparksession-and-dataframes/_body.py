import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l41_session.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
PLAN = '\n'.join(l[:118] + (' …' if len(l) > 118 else '') for l in sec('== Physical Plan ==', '== 8)').split('\n'))

def session_pic(hi=None, extra=''):
    """Driver with SparkSession on top of SparkContext, two executors."""
    o = box(8, 26, 170, 104, 'blue' if hi == 'driver' else 'card') + t(93, 40, 'Driver (your Python)', 8.2, bold=True)
    o += opbox(20, 50, 'SparkSession', 'spark', 'acc' if hi == 'session' else 'card', 146, 26)
    o += opbox(20, 90, 'SparkContext', 'spark.sparkContext', 'violet' if hi == 'sc' else 'card', 146, 26)
    o += arrow(93, 76, 93, 90, 'ink3', 1.1)
    for k in range(2):
        y = 30 + k * 54
        o += opbox(232, y, f'Executor {k + 1}', 'tasks · cache', 'green' if hi == 'exec' else 'card', 120, 34)
        o += arrow(178, 80, 232, y + 17, 'ink3', 1.0)
    return o + extra

# ---------------------------------------------------------------- story
sc_ = (session_pic('session') +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('2nd getOrCreate: same object', 'green'), ('…but shuffle partitions 8 → 50', 'amber'),
           ('newSession: own views and conf', 'green'), ('amount read as string: one "abc"', 'red'),
           ('query built: 0 jobs; show(): 2', 'green'), ('DataFrame plan == SQL plan', 'green')])))
scene_svg = scene('A PySpark program starts with a SparkSession in the driver, which owns a SparkContext and talks to executors. We created sessions twice, read orders into a DataFrame and counted when work really happened.', sc_,
                  'One <tspan font-weight="700" class="s-acc">SparkSession</tspan> per application; DataFrames are <tspan font-weight="700" class="s-acc">lazy plans</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Why did my partitions change?”</h2>
  <div class="story">
    <p class="narration">Kabir moved his RDD code to DataFrames. His notebook created a <code>SparkSession</code> with 8 shuffle partitions. Later a helper module he imported also called <code>SparkSession.builder…getOrCreate()</code>, with 50. From that moment every query in his notebook used 50 partitions, and nobody had changed his code.</p>

{scene_svg}

K> Sir, I thought getOrCreate returns the existing session and ignores the new settings.
A> It returns the existing session, yes. But <b>runtime SQL settings</b> passed to the builder are applied to it. We will prove it, then build our first DataFrames properly.
R> And what exactly is the difference between the session and the SparkContext we used for RDDs?
A> The <b>SparkSession</b> is the entry point for DataFrames and SQL; it wraps the SparkContext, which still runs the jobs. Today: the builder, sessions, our first DataFrame from TiffinGo orders, laziness, plans and <code>Row</code> objects. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> SparkSession and DataFrames at three levels
L1> A restaurant kitchen
      <ul>
        <li>The SparkSession is the head chef’s order desk: every order (query) comes in through it.</li>
        <li>A DataFrame is an order written down as steps; nothing is cooked until someone says “serve” (an action).</li>
        <li>The cooks (executors) do the work; the head chef only plans and hands out tasks.</li>
      </ul>
L2> The API
      <ul>
        <li><code>SparkSession.builder.appName(…).master(…).config(k, v).getOrCreate()</code>; in the <code>pyspark</code> shell and notebooks it already exists as <code>spark</code>.</li>
        <li>A DataFrame is a distributed table with a <b>schema</b> (named, typed columns). Transformations (<code>select</code>, <code>where</code>, <code>groupBy</code>) return new DataFrames; actions (<code>show</code>, <code>count</code>, <code>collect</code>, write) run jobs.</li>
        <li>Rows come back as <code>Row</code> objects: <code>r.city</code>, <code>r["city"]</code>, <code>r.asDict()</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>A second <code>getOrCreate()</code> returned the same object, kept the app name, but changed <code>spark.sql.shuffle.partitions</code> from 8 to 50.</li>
        <li><code>newSession()</code> shared the SparkContext but had its own temp views and SQL conf.</li>
        <li>Building a query ran 0 jobs; <code>show()</code> ran 2. The DataFrame and the same SQL produced identical optimized plans.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>SparkSession and the DataFrame</h2>
''' + def_block(
    'A <b>SparkSession</b> is the unified entry point to Spark SQL and the DataFrame API (introduced in Spark 2.0). It wraps a SparkContext, holds the session’s SQL configuration, temporary views, functions and catalog, and is obtained with <code>SparkSession.builder.getOrCreate()</code>, which returns the active or default session if one exists. A <b>DataFrame</b> is an immutable, distributed collection of rows organised into named, typed columns, i.e. a table with a schema. It is lazily evaluated: transformations build a logical plan that the Catalyst optimizer turns into a physical plan when an action is called. DataFrames are executed by the same engine as Spark SQL, so equivalent DataFrame and SQL queries produce the same plan.',
    'The SparkSession is the object you start with: it reads data, runs SQL and makes DataFrames. A DataFrame is a big table spread over the cluster, with column names and types. Writing DataFrame code only plans the work; Spark runs it when you ask for a result.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('SparkSession', 'Entry point for DataFrames and SQL (<code>spark</code>).'),
    ('builder / getOrCreate()', 'Configure and get the session; returns the existing one if any.'),
    ('SparkContext', 'The engine connection inside the session (<code>spark.sparkContext</code>).'),
    ('DataFrame', 'Distributed table with a schema.'),
    ('Schema', 'Column names and data types; <code>printSchema()</code>.'),
    ('Row', 'One record returned to Python.'),
    ('Transformation / action', 'Builds the plan / runs a job.'),
    ('Catalyst', 'The optimizer that turns your query into a physical plan.'),
]) + '''

  <h3>RDD or DataFrame?</h3>
''' + table(['', 'RDD (Module 2)', 'DataFrame'], [
    ['Entry point', '<code>sc = spark.sparkContext</code>', '<code>spark</code> (SparkSession)'],
    ['Structure', 'Any Python objects', 'Rows with named, typed columns'],
    ['Optimised by', 'You', 'Catalyst + Tungsten (code generation)'],
    ['Python cost', 'Every function runs in Python workers', 'Built-in functions run in the JVM'],
    ['SQL', 'No', '<code>spark.sql()</code>, same engine'],
    ['Lab (Lesson 2.1)', '30.2 s', '4.0 s for the same answer'],
], minw=640) + lv + '''
EXAM> “What is a SparkSession?” The unified entry point (since Spark 2.0) for DataFrames, SQL and the catalog; it wraps a SparkContext and holds SQL configuration and temporary views. <code>getOrCreate()</code> returns the existing session if there is one. Write one SparkSession per application; use <code>newSession()</code> only when you need isolated views or SQL settings.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Ways to get a session</h2>
''' + table(['Where you are', 'What gives you <code>spark</code>', 'Notes'], [
    ['pyspark shell / notebook with PySpark', 'Created for you', 'Already called <code>spark</code>; <code>sc</code> too in the shell'],
    ['Python script (local)', '<code>SparkSession.builder.master("local[*]").getOrCreate()</code>', 'Lesson 1.5'],
    ['spark-submit to a cluster', '<code>SparkSession.builder.getOrCreate()</code>', 'Master and resources come from spark-submit (Module 11)'],
    ['Spark Connect client', '<code>SparkSession.builder.remote("sc://host:15002").getOrCreate()</code>', 'Thin client, no local JVM; no RDD API (Lesson 11.3)'],
    ['Databricks / EMR notebooks', 'Created by the platform', 'Do not stop it'],
], minw=720) + '''
WARN> Do not hard-code <code>.master("local[*]")</code> in code that will run on a cluster: a master set in code overrides <code>spark-submit --master</code>. Keep master and resource settings outside the code, and keep library modules free of their own <code>getOrCreate()</code> with settings: as Step 2 shows, those settings leak into the caller’s session.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>From a session to a first query</h2>
  <p>All outputs are real: PySpark 4.3.0 in local mode with two cores, reading TiffinGo’s <code>orders.csv</code> (50,002 rows).</p>
''' + stepper([
    ('Step 1 · Build the session',
     code('python', 'l41_session.py', 'from pyspark.sql import SparkSession, functions as F\nspark = (SparkSession.builder.appName("tiffingo-4.1").master("local[2]")\n         .config("spark.sql.shuffle.partitions", "8").getOrCreate())\nprint(spark.version, spark.sparkContext.appName, spark.sparkContext.master)\nprint(spark.conf.get("spark.sql.shuffle.partitions"))', sec('== 1)', '== 2)', drop=('UI ',))),
     'The builder collects settings and <code>getOrCreate()</code> starts the JVM, the SparkContext and the session. <code>spark.conf</code> reads and sets SQL settings at runtime; <code>spark.sparkContext</code> is the same SparkContext we used for RDDs in Module 2.'),
    ('Step 2 · A second getOrCreate() changes your settings',
     code('python', 'l41_session.py', 's2 = (SparkSession.builder.appName("another-name")\n      .config("spark.sql.shuffle.partitions", "50").getOrCreate())\nprint(s2 is spark, s2.sparkContext.appName, s2.conf.get("spark.sql.shuffle.partitions"))', sec('== 2)', '== 3)')),
     'The same object came back and the app name stayed (it belongs to the SparkContext, fixed at start-up). But the <b>runtime SQL setting was applied</b> to the existing session: from now on every shuffle in this application uses 50 partitions. You can see it later in the plan of Step 6 (<code>hashpartitioning(city, 50)</code>). Kabir’s mystery, solved.'),
    ('Step 3 · newSession(): isolated views and SQL conf',
     code('python', 'l41_session.py', 's3 = spark.newSession()\nspark.range(3).createOrReplaceTempView("nums")\nprint([t.name for t in spark.catalog.listTables()], [t.name for t in s3.catalog.listTables()])\ns3.conf.set("spark.sql.shuffle.partitions", "4")', sec('== 3)', '== 4)')),
     'A new session shares the SparkContext (and its executors and cache) but has its own temporary views, SQL configuration and registered functions. Servers such as the Spark Thrift Server use this to keep users apart. In normal jobs one session is enough.'),
    ('Step 4 · A first DataFrame',
     code('python', 'l41_session.py', 'orders = spark.read.csv(".../orders.csv", header=True, inferSchema=True)\norders.printSchema(); orders.show(3)\nprint(orders.count(), orders.rdd.getNumPartitions())\norders.where("try_cast(amount AS INT) IS NULL").select("amount").collect()\norders = orders.withColumn("amount", F.expr("try_cast(amount AS INT)"))', sec('== 4)', '== 5)')),
     'A DataFrame knows its <b>columns and types</b>. <code>inferSchema</code> read the file to guess types, and one bad value, <code>abc</code>, turned the whole <code>amount</code> column into a string (and one badly formatted date did the same to <code>order_ts</code>). We fixed <code>amount</code> with <code>try_cast</code>; Lesson 4.2 shows how an explicit schema avoids guessing.'),
    ('Step 5 · Immutable and lazy',
     code('python', 'l41_session.py', 'o2 = orders.withColumn("amount_gst", F.round(F.col("amount") * 1.05, 2))\nq = (orders.where(F.col("status") == "DELIVERED")\n           .groupBy("city").agg(F.sum("amount").alias("revenue"))\n           .orderBy(F.desc("revenue")))\n# count jobs with the REST API before and after\nq.show(5)', sec('== 5)', '== 7)')),
     '<code>withColumn</code> returned a <b>new</b> DataFrame; <code>orders</code> still has 8 columns. Building <code>q</code> ran no job at all: it is only a plan. <code>show()</code> ran 2 jobs (with adaptive execution, the shuffle stages run as separate jobs). Bengaluru is second with ₹24.99 lakh of delivered orders.'),
    ('Step 6 · The plan, Row objects and SQL',
     code('python', 'l41_session.py', 'q.explain()\nr = q.first(); print(r, r["city"], r.revenue, r.asDict())\norders.createOrReplaceTempView("orders")\nsq = spark.sql("SELECT city, sum(amount) AS revenue FROM orders WHERE status=\'DELIVERED\' GROUP BY city ORDER BY revenue DESC")\n# compare optimized plans', PLAN + '\n' + sec('== 8)', '== 10)')),
     'Read the plan from the bottom: scan only three columns with the filter <b>pushed into the scan</b>, a partial sum per partition, a shuffle by city (50 partitions, from Step 2), the final sum, a range shuffle and a sort. Results come back as <code>Row</code> objects. The SQL version produced exactly the same optimized plan: DataFrames and SQL are one engine.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('getOrCreate() -> spark', W), ('version 4.3.0, local[2]', G), ('shuffle partitions: 8', W)], size=7.6),
    term([('2nd getOrCreate: same object True', G), ('app name: tiffingo-4.1', W), ('shuffle partitions: 50 (!)', Y)], size=7.4),
    term([('read.csv(…, inferSchema=True)', W), ('amount: string  <- "abc"', RD), ('try_cast -> amount: int', G)], size=7.4),
    term([('query built  : 0 jobs', G), ('after show(): 2 jobs', Y), ('Mumbai 2712820', W)], size=7.6),
    term([('DataFrame plan == SQL plan', G), ('Row(city=\'Mumbai\', revenue=…)', W)], size=7.4),
]
B1 = [
    t(180, 14, 'One session in the driver', 9.4, bold=True) + session_pic('session') + cap('Entry point for DataFrames and SQL.', '', 'blue', y=144, h=30),
    t(180, 14, 'Runtime SQL conf is shared', 9.4, bold=True) + session_pic('session') + cap('Builder settings reach the old session.', '', 'amber', y=144, h=30),
    t(180, 14, 'A DataFrame has a schema', 9.4, bold=True) + flow([('CSV', 'orders.csv', 'card'), ('infer', 'scan file', 'amber'), ('DataFrame', '8 columns', 'blue'), ('fix types', 'try_cast', 'green')], y=50, w=72, gap=14) + cap('Guessing types can go wrong.', '', 'red', y=144, h=30),
    t(180, 14, 'Transformations only plan', 9.4, bold=True) + flow([('where', 'plan', 'card'), ('groupBy', 'plan', 'card'), ('orderBy', 'plan', 'card'), ('show()', 'jobs!', 'acc')], y=50, w=72, gap=14) + cap('Work starts at the action.', '', 'green', y=144, h=30),
    t(180, 14, 'One engine', 9.4, bold=True) + flow([('DataFrame', 'Python', 'blue'), ('Catalyst', 'optimise', 'violet'), ('plan', 'same', 'green')], y=50, w=96, gap=22) + opbox(8, 96, 'spark.sql(…)', 'SQL text', 'blue', 96, 30) + arrow(104, 111, 126, 70, 'ink3', 1.0) + cap('DataFrame and SQL: identical plans.', '', 'violet', y=144, h=30),
]
see_caps = ['The builder created the session.',
            'A second builder changed shuffle partitions.',
            'One bad value made amount a string.',
            'No job until show().',
            'Same plan for DataFrame and SQL.']
behind_caps = ['SparkSession wraps the SparkContext.',
               'getOrCreate applies runtime SQL settings.',
               'inferSchema reads data to guess types.',
               'The plan runs only at an action.',
               'Both go through Catalyst.']
two = anim_two('SparkSession and DataFrames', 'One entry point, lazy tables', 'Real lab outputs', 'Inside the driver', see, B1, see_caps, behind_caps)

# ---- scenario 1: notebook settings leak
e1 = (t(180, 22, 'Notebook: 8 shuffle partitions', 9.4, bold=True) + t(180, 56, 'small data, fast queries', 8.4, 'ink2') + cap('Tuned for a laptop.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'import team_utils', 9.4, bold=True) + t(180, 56, 'builder.config(…, "50").getOrCreate()', 8.0, 'ink', mono=True) + cap('A helper builds a session.', '', 'amber', y=150, h=34))
e3 = (t(180, 22, 'Every query now uses 50', 9.4, bold=True) + t(180, 56, '50 tiny tasks per shuffle', 8.4, 'ink2') + cap('Silent change, like Step 2.', '', 'red', y=150, h=34))
e4 = (t(180, 22, 'Fix the helper', 9.4, bold=True) + t(180, 56, 'def run(spark, df): …', 8.4, 'ink', mono=True) + cap('Pass the session in.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Settings in one place', 9.4, 'acc', bold=True) + t(180, 56, 'spark-submit --conf / job config', 8.4, 'ink2') + cap('Not scattered in modules.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'A helper module changes your session',
              'Why libraries should receive the session. (Typical; behaviour from our lab.)',
              'Session settings leak', 'getOrCreate with config in a helper changes runtime SQL settings of the caller’s session; pass the session in instead', [e1, e2, e3, e4, e5],
              ['Tuned notebook.', 'Helper calls getOrCreate.', 'Settings changed.', 'Pass spark in.', 'Configure once.'],
              hid='scenario-leak')

# ---- scenario 2: hard-coded local master
b1 = (t(180, 22, 'Job works on a laptop', 9.4, bold=True) + t(180, 56, '.master("local[*]")', 8.4, 'ink', mono=True) + cap('Hard-coded master.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'spark-submit --master yarn', 9.4, bold=True) + t(180, 56, 'job runs on ONE node anyway', 8.4, 'ink2') + cap('Code wins over the flag.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, '3 hours instead of 10 minutes', 9.4, bold=True) + t(180, 56, '1 machine, 0 executors used', 8.4, 'ink2') + cap('Cluster idle.', '', 'red', y=150, h=34))
b4 = (t(180, 22, 'Remove master from code', 9.4, bold=True) + t(180, 56, 'SparkSession.builder.getOrCreate()', 8.2, 'ink', mono=True) + cap('Let spark-submit decide.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Local runs via config', 9.4, 'acc', bold=True) + t(180, 56, 'spark-submit --master local[2]', 8.4, 'ink', mono=True) + cap('Same code everywhere.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'The job that never left the laptop',
              'Keep deployment settings out of the code. (Typical.)',
              'Hard-coded master', 'A master set in code overrides spark-submit; keep master and resources outside the application', [b1, b2, b3, b4, b5],
              ['Hard-coded.', 'Flag ignored.', 'Slow.', 'Remove it.', 'Configure outside.'],
              hid='scenario-master')

# ---- scenario 3: shared server
u1 = (t(180, 22, 'One Spark server, many analysts', 9.4, bold=True) + t(180, 56, 'Thrift Server / notebook gateway', 8.4, 'ink2') + cap('Shared SparkContext.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Two users, same view name', 9.4, bold=True) + t(180, 56, 'CREATE TEMP VIEW orders …', 8.4, 'ink', mono=True) + cap('Would clash in one session.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'A session per user', 9.4, bold=True) + t(180, 56, 'spark.newSession()', 8.4, 'ink', mono=True) + cap('Own views and SQL conf.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Still shared', 9.4, bold=True) + t(180, 56, 'executors, cache, global temp views', 8.4, 'ink2') + cap('Resources are common.', '', 'violet', y=150, h=34))
u5 = (t(180, 22, 'Our Step 3', 9.4, 'acc', bold=True) + t(180, 56, "views: ['nums'] vs []", 8.4, 'ink', mono=True) + cap('Isolation confirmed.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Many users on one Spark application',
              'How shared servers isolate users. (Typical; behaviour from our lab.)',
              'Session isolation', 'newSession gives each user separate temporary views and SQL settings while sharing executors and cache', [u1, u2, u3, u4, u5],
              ['Shared server.', 'Name clash.', 'newSession.', 'Shared resources.', 'Lab proof.'],
              hid='scenario-sessions')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>One entry point, lazy tables</h2>
  <p>Left: real outputs. Right: what happens in the driver.</p>
''' + two + '''
  <p>Three live scenarios follow: a helper that changes your session, a hard-coded master, and many users on one server.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>DataFrames at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'ETL', 12, 'blue', bold=True) + t(60, 58, 'pipelines', 7.4, 'ink2'),
    '1. Batch ETL',
    'Nightly jobs read raw files into DataFrames, clean and join them, and write tables, all through one SparkSession.',
    ['Raw files', '*DataFrames', 'Tables']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'SQL', 12, 'green', bold=True) + t(60, 58, 'analysts', 7.4, 'ink2'),
    '2. SQL and Python together',
    'Analysts write SQL and engineers write DataFrame code on the same tables; both produce the same plans.',
    ['spark.sql', '*Catalyst', 'Same engine']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'notebook', 10, 'violet', bold=True) + t(60, 58, 'spark ready', 7.4, 'ink2'),
    '3. Notebooks',
    'Databricks, EMR Studio and Jupyter give you a ready <code>spark</code> session for exploration.',
    ['Notebook', '*spark', 'Explore']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'server', 11, 'acc', bold=True) + t(60, 58, 'many users', 7.4, 'ink2'),
    '4. Shared SQL servers',
    'Thrift Server and Spark Connect servers give each client its own session on shared executors.',
    ['Client', '*newSession', 'Shared cluster']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'ML', 12, 'acc', bold=True) + t(60, 58, 'features', 7.4, 'ink2'),
    '5. Feature engineering',
    'Feature pipelines build DataFrames of customer and order features that MLlib (Module 10) trains on.',
    ['Orders', '*DataFrame', 'Features']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> drivers and executors in <a href="../../01-introduction/03-spark-architecture/">1.3</a>, lazy evaluation in <a href="../../02-rdds/03-lazy-evaluation-and-the-dag/">2.3</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
