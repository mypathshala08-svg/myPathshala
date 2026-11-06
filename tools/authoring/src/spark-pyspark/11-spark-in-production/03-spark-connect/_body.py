import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l113_connect.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)

def arch(x, y, connect=True):
    if connect:
        o = opbox(x, y + 20, 'Python client', 'no JVM', 'blue', 100, 40)
        o += arrow(x + 102, y + 40, x + 150, y + 40, 'violet', 1.4) + t(x + 126, y + 32, 'gRPC', 7, 'violet', bold=True) + t(x + 126, y + 56, 'plans', 6.6, 'ink2')
        o += box(x + 152, y, 190, 80, 'card') + t(x + 247, y + 14, 'Spark Connect server', 6.8, 'ink2', bold=True)
        o += opbox(x + 160, y + 24, 'driver', 'sessions', 'acc', 70, 34) + opbox(x + 238, y + 24, 'executors', 'tasks', 'green', 96, 34)
    else:
        o = box(x, y, 160, 80, 'card') + t(x + 80, y + 14, 'your Python process', 6.8, 'ink2', bold=True)
        o += opbox(x + 8, y + 24, 'Python', 'py4j', 'blue', 66, 34) + opbox(x + 82, y + 24, 'driver JVM', 'in-process', 'acc', 70, 34)
        o += arrow(x + 162, y + 40, x + 200, y + 40, 'ink3', 1.2) + opbox(x + 204, y + 24, 'executors', 'cluster', 'green', 100, 34)
    return o

# ---------------------------------------------------------------- story
sc_ = (t(14, 22, 'Spark Connect: client and server are separate', 7.4, 'ink2', anchor='start', bold=True) + arch(14, 34) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured (sc://localhost:15002)', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('client JVMs: 0 (classic: 1)', 'green'), ('connect + query: 0.52 s', 'green'),
           ('sparkContext: not supported', 'red'), ('df.rdd: not implemented', 'red'),
           ('bad column: error on use', 'amber'), ('2 sessions, views isolated', 'blue')])))
scene_svg = scene('Spark Connect separates the Python client from the Spark driver: the client builds query plans and sends them over gRPC to a long-running server. We started a Connect server, ran DataFrame code from a client with no JVM, and tested what is not supported, when errors appear, and session isolation.', sc_,
                  'The client sends <tspan font-weight="700" class="s-acc">plans, not code</tspan>; the server runs them.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Every analyst’s laptop runs a Spark driver”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s 40 analysts each started PySpark in their notebooks. Every notebook started its own driver JVM, needed Java installed, and crashed the laptop when someone collected a big table. Upgrading Spark meant upgrading 40 laptops.</p>

{scene_svg}

K> Sir, can’t the notebook just talk to a Spark that runs somewhere else?
A> That is <b>Spark Connect</b>. The notebook only has a thin Python client. It turns your DataFrame code into a plan and sends it over gRPC to a Spark Connect server, which runs it and streams results back.
R> Same DataFrame API?
A> Almost all of it. Today we start a server, connect a client, compare it with classic PySpark, and find the gaps: no SparkContext, no RDDs, lazy error reporting, isolated sessions. All outputs are real (Spark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Spark Connect at three levels
L1> Ordering food by phone
      <ul>
        <li>Classic PySpark: you bring a kitchen home and cook yourself. Spark Connect: you phone the restaurant with your order (the plan); the kitchen cooks and delivers the result.</li>
        <li>Each caller gets their own order slip (session), so two customers never mix their orders.</li>
      </ul>
L2> The API
      <ul>
        <li>Server: <code>$SPARK_HOME/sbin/start-connect-server.sh</code> (port 15002), or a managed endpoint.</li>
        <li>Client: <code>SparkSession.builder.remote("sc://host:15002").getOrCreate()</code>, or <code>SPARK_REMOTE</code>; lightweight package <code>pyspark-client</code>.</li>
        <li>Not available: <code>spark.sparkContext</code>, RDD APIs, direct JVM access (<code>_jdf</code>, py4j).</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>The Connect client process started 0 JVMs; a classic local session started 1.</li>
        <li>A missing column raised no error until the plan was analysed on the server.</li>
        <li>A temp view created in session 1 did not exist in session 2.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Spark Connect</h2>
''' + def_block(
    '<b>Spark Connect</b> (Spark 3.4+, central in Spark 4) is a client-server architecture for Spark. A thin client library implements the DataFrame and SQL APIs by building <b>unresolved logical plans</b> encoded as protocol buffers and sending them over <b>gRPC</b> to a Spark Connect server running inside a Spark driver. The server analyses, optimises and executes the plans and streams results back as Arrow batches. Each client gets its own isolated <b>session</b> (temporary views, configuration, UDFs), the client needs no JVM, and client and server can be upgraded independently within compatible versions. APIs that expose the driver’s JVM, such as <code>SparkContext</code> and RDDs, are not available; analysis errors surface when the server analyses a plan (on actions or schema access) rather than when the DataFrame is defined.',
    'With Spark Connect your Python program does not run Spark itself. It describes queries and sends them to a Spark server, which runs them and returns the results. Clients are light (no Java), each user has a separate session, and the DataFrame API stays the same, but low-level things like RDDs and SparkContext are not available.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Spark Connect server', 'Spark driver that accepts gRPC.'),
    ('Thin client', 'Python library, no JVM.'),
    ('sc:// URL', 'sc://host:15002 connection string.'),
    ('Unresolved plan', 'What the client sends.'),
    ('gRPC', 'Network protocol used.'),
    ('Arrow batches', 'Format of returned results.'),
    ('Session isolation', 'Views/config per client.'),
    ('pyspark-client', 'Pure-Python client package.'),
]) + '''

  <h3>Classic PySpark vs Spark Connect</h3>
''' + table(['', 'Classic', 'Spark Connect'], [
    ['Driver JVM', 'In your Python process (py4j)', 'In the server'],
    ['Client needs Java', 'Yes', 'No (lab: 0 JVMs)'],
    ['DataFrame / SQL API', 'Yes', 'Yes'],
    ['RDD, SparkContext, _jdf', 'Yes', 'No'],
    ['Analysis errors', 'When the DataFrame is defined', 'When the server analyses the plan'],
    ['Multi-user isolation', 'One app per user', 'Many sessions per server'],
], minw=560) + lv + '''
EXAM> “What is Spark Connect?” A client-server protocol where a lightweight client sends unresolved logical plans over gRPC to a Spark Connect server that executes them and returns Arrow results. Benefits: no JVM on clients, isolation between sessions, independent upgrades, Spark from any language or app. Limits: no RDD or SparkContext APIs and no direct JVM access; errors appear when plans are analysed on the server.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Ways to connect</h2>
''' + table(['Way', 'Example'], [
    ['Builder', '<code>SparkSession.builder.remote("sc://spark.internal:15002").getOrCreate()</code>'],
    ['Environment variable', '<code>export SPARK_REMOTE="sc://spark.internal:15002"</code>, then <code>pyspark</code>'],
    ['With options', '<code>sc://host:15002/;user_id=vineeta;token=…;use_ssl=true</code>'],
    ['Thin package', '<code>pip install pyspark-client</code> (no bundled jars)'],
    ['Managed', 'Databricks Connect and other platforms expose Connect endpoints'],
], minw=560) + '''
WARN> Code that touches the JVM breaks under Connect: <code>spark.sparkContext</code>, <code>df.rdd</code>, <code>sc.broadcast</code>, accumulators, and tricks like <code>df._jdf.queryExecution()</code> used earlier in this course. Rewrite RDD code with DataFrame functions (<code>mapInPandas</code>, <code>applyInPandas</code>, UDFs). Also expect errors later than you are used to: a typo in a column name surfaces only when the plan is analysed, so test with a real action.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>A server and a thin client</h2>
  <p>All outputs are real: Spark 4.3.0. The server was started with <code>sbin/start-connect-server.sh</code> on port 15002; the client is a separate Python process. Data: the 5,000,000-order Parquet table used in Module 8.</p>
''' + stepper([
    ('Step 1 · Connect',
     code('python', 'l113_connect.py', 'from pyspark.sql import SparkSession\nspark = SparkSession.builder.remote("sc://localhost:15002").getOrCreate()\nprint(type(spark), spark.version)\n# count JVM processes started by this Python process', sec('== 1)', '== 2)') + '\n' + sec('classic local session')),
     'The session is a <code>pyspark.sql.connect</code> session, talking to a Spark 4.3.0 server. Connecting and running a first query took about half a second, and this Python process started <b>no JVM</b>. For comparison, a classic <code>SparkSession.builder.master("local[1]")</code> started one Java child process.'),
    ('Step 2 · Normal DataFrame code',
     code('python', 'l113_connect.py', 'o = spark.read.parquet("/root/lab/spark/data/orders_big")\no.groupBy("city").agg(F.sum("amount").alias("revenue")).orderBy(F.desc("revenue")).limit(3).collect()', sec('== 2)', '== 3)')),
     'Unchanged code. The client sent a plan; the server read 5 million rows, aggregated and returned only 3 rows. Note the path is read <b>by the server</b>: files must be reachable from the server, not from the client laptop.'),
    ('Step 3 · What is not there',
     code('python', 'l113_connect.py', 'spark.sparkContext\no.rdd', sec('== 3)', '== 4)')),
     'Both depend on the driver JVM living in your process. Under Connect there is no such JVM, so <code>sparkContext</code> raises <code>JVM_ATTRIBUTE_NOT_SUPPORTED</code> and <code>df.rdd</code> is not implemented. Libraries and old code that use RDDs need rewriting before moving to Connect.'),
    ('Step 4 · When errors appear',
     code('python', 'l113_connect.py', 'bad = o.select("no_such_column")    # only a plan on the client\nbad.columns                          # the server analyses it now', sec('== 4)', '== 5)')),
     'Defining <code>bad</code> succeeded: the client does not know the table’s columns. The error came when we asked for <code>.columns</code>, which sends the plan to the server for analysis: <code>UNRESOLVED_COLUMN.WITH_SUGGESTION</code>. In classic PySpark the same line fails immediately.'),
    ('Step 5 · Sessions and UDFs',
     code('python', 'l113_connect.py', 's2 = SparkSession.builder.remote("sc://localhost:15002").create()\nspark.range(3).createOrReplaceTempView("my_view")\nspark.catalog.tableExists("my_view"), s2.catalog.tableExists("my_view")\n@F.udf("double")\ndef gst(a): return round(a * 1.05, 2)', sec('== 5)', 'classic local session')),
     'Two clients on one server got two sessions: session 2 cannot see session 1’s temp view, which is what you want for 40 analysts sharing a server. Python UDFs still work: the function is serialised and runs on the server’s executors, so the libraries it uses must be installed there.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('pyspark.sql.connect.session.SparkSession', W), ('server version: 4.3.0', G), ('client JVMs: 0 | classic: 1', G)], size=7.0),
    term([("('Mumbai', 510290994)", W), ("('Bengaluru', 508795383)", W), ('3 rows back from 5M', G)], size=7.4),
    term([('sparkContext -> JVM_ATTRIBUTE_NOT_SUPPORTED', RD), ('df.rdd -> NOT_IMPLEMENTED', RD)], size=7.0),
    term([('missing column: no error yet', Y), ('.columns -> UNRESOLVED_COLUMN', RD), ('view in s1: True | in s2: False', G)], size=7.0),
]
B1 = [
    t(180, 14, 'Classic: driver in your process', 9.4, bold=True) + arch(20, 40, connect=False) + cap('Java on every laptop.', '', 'amber', y=144, h=30),
    t(180, 14, 'Connect: plans over gRPC', 9.4, bold=True) + arch(10, 40) + cap('Results come back as Arrow.', '', 'green', y=144, h=30),
    t(180, 14, 'No JVM, no RDD', 9.4, bold=True) + opbox(20, 46, 'sparkContext / rdd', 'need local JVM', 'red', 150, 34) + opbox(190, 46, 'DataFrame / SQL', 'supported', 'green', 150, 34) + cap('Rewrite JVM-level code.', '', 'amber', y=144, h=30),
    t(180, 14, 'One server, many sessions', 9.4, bold=True) + ''.join(opbox(20 + k * 112, 46, f'session {k + 1}', 'own views', 'blue', 100, 34) for k in range(3)) + cap('Isolated per client.', '', 'green', y=144, h=30),
]
see_caps = ['A remote session.', 'Same DataFrame code.', 'Unsupported APIs.', 'Errors and sessions.']
behind_caps = ['Classic architecture.', 'Connect architecture.', 'JVM-bound APIs.', 'Session isolation.']
two = anim_two('Spark Connect', 'A thin client for Spark', 'Real lab outputs', 'What happens', see, B1, see_caps, behind_caps)

e1 = (t(180, 22, '40 notebooks, 40 drivers', 9.4, bold=True) + t(180, 56, 'Java on every laptop', 8.4, 'ink2') + cap('Hard to manage.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'One Connect server pool', 9.4, bold=True) + t(180, 56, 'next to the data', 8.4, 'ink2') + cap('Central upgrades.', '', 'green', y=150, h=34))
e3 = (t(180, 22, 'Notebooks: pyspark-client', 9.4, bold=True) + t(180, 56, 'SPARK_REMOTE=sc://…', 8.4, 'ink', mono=True) + cap('No JVM locally.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Isolated sessions', 9.4, bold=True) + t(180, 56, 'views and config per user', 8.4, 'ink2') + cap('No collisions.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Laptop crashes stop', 9.4, 'acc', bold=True) + t(180, 56, 'heavy work stays on the server', 8.4, 'ink2') + cap('Better experience.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Spark for 40 analysts',
              'Shared Spark Connect servers. (Typical; behaviour from our lab.)',
              'Shared server', 'Analysts use thin clients against shared Spark Connect servers', [e1, e2, e3, e4, e5],
              ['40 drivers.', 'Server.', 'Client.', 'Sessions.', 'Stable.'],
              hid='scenario-analysts')
b1 = (t(180, 22, 'Moving a job to Connect', 9.4, bold=True) + t(180, 56, 'fails at spark.sparkContext', 8.4, 'ink2') + cap('JVM_ATTRIBUTE_NOT_SUPPORTED', '', 'red', y=150, h=34))
b2 = (t(180, 22, 'Find JVM-bound code', 9.4, bold=True) + t(180, 56, 'rdd, sc.broadcast, _jdf, accumulators', 8.2, 'ink2') + cap('grep the codebase.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'Rewrite with DataFrames', 9.4, bold=True) + t(180, 56, 'mapInPandas, applyInPandas', 8.4, 'ink2') + cap('Supported.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Broadcast → join hint', 9.4, bold=True) + t(180, 56, 'F.broadcast(small_df)', 8.4, 'ink', mono=True) + cap('Same effect.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Test on Connect in CI', 9.4, 'acc', bold=True) + t(180, 56, 'SPARK_REMOTE in test env', 8.4, 'ink2') + cap('Catch it early.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'The job that needed SparkContext',
              'Migrating code to Spark Connect. (Typical; error from our lab.)',
              'Migration', 'Replace RDD and SparkContext code with DataFrame APIs before moving to Connect', [b1, b2, b3, b4, b5],
              ['Fails.', 'Find.', 'Rewrite.', 'Broadcast.', 'CI.'],
              hid='scenario-migrate')
u1 = (t(180, 22, 'A web app needs Spark', 9.4, bold=True) + t(180, 56, 'internal pricing tool', 8.4, 'ink2') + cap('No JVM in the container.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Thin client + Connect', 9.4, bold=True) + t(180, 56, 'requests become plans', 8.4, 'ink2') + cap('gRPC to the server.', '', 'green', y=150, h=34))
u3 = (t(180, 22, 'Small results only', 9.4, bold=True) + t(180, 56, 'aggregate on the server', 8.4, 'ink2') + cap('3 rows from 5M (lab).', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Auth in the URL', 9.4, bold=True) + t(180, 56, ';token=…;use_ssl=true', 8.4, 'ink', mono=True) + cap('Behind a gateway.', '', 'amber', y=150, h=34))
u5 = (t(180, 22, 'Spark as a service', 9.4, 'acc', bold=True) + t(180, 56, 'apps in any language', 8.4, 'ink2') + cap('Go, Rust, Swift clients exist.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Spark inside a web app',
              'Embedding Spark through Connect. (Typical.)',
              'Embedding', 'Applications use Spark Connect clients to send queries to a remote Spark server', [u1, u2, u3, u4, u5],
              ['App.', 'Client.', 'Small results.', 'Auth.', 'Service.'],
              hid='scenario-app')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>A thin client for Spark</h2>
  <p>Left: real outputs. Right: classic vs Connect.</p>
''' + two + '''
  <p>Three live scenarios follow: analysts on a shared server, migrating JVM-bound code, and Spark inside an app.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Spark Connect at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'IDE', 12, 'blue', bold=True) + t(60, 58, 'remote', 7.4, 'ink2'),
    '1. Local IDE, remote cluster',
    'Developers debug in VS Code while queries run on the shared cluster (e.g. Databricks Connect).',
    ['IDE', '*Connect', 'Cluster']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'notebooks', 9, 'green', bold=True) + t(60, 58, 'shared', 7.4, 'ink2'),
    '2. Shared notebook servers',
    'JupyterHub users share Connect servers instead of starting their own drivers.',
    ['Notebook', '*sc://', 'Shared server']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'apps', 12, 'violet', bold=True) + t(60, 58, 'services', 7.4, 'ink2'),
    '3. Applications',
    'Internal services query Spark without bundling a JVM.',
    ['Service', '*thin client', 'Results']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'upgrade', 10, 'acc', bold=True) + t(60, 58, 'server only', 7.4, 'ink2'),
    '4. Independent upgrades',
    'Platform teams upgrade the server while clients stay on compatible versions.',
    ['New Spark', '*server', 'Clients unchanged']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'langs', 12, 'acc', bold=True) + t(60, 58, 'Go/Rust', 7.4, 'ink2'),
    '5. Other languages',
    'Community clients for Go, Rust and Swift speak the same protocol.',
    ['Any language', '*gRPC', 'Spark']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> SparkSession in <a href="../../04-dataframes/01-sparksession-and-dataframes/">4.1</a>, UDFs in <a href="../../06-transformations/06-udfs/">6.6</a>, deploy modes in <a href="../01-spark-submit-and-deploy-modes/">11.1</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
