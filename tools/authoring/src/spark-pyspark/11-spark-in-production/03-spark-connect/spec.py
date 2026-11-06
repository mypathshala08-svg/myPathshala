import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='11-spark-in-production', lesson='03-spark-connect', n='11.3',
    module_label='Module 11 · Spark in production',
    title='Spark Connect',
    desc='Spark Connect with Spark 4.3.0: a Connect server on sc://localhost:15002 and a thin Python client that starts no JVM (classic PySpark starts one), unchanged DataFrame code aggregating 5M orders on the server, sparkContext and df.rdd unsupported (JVM_ATTRIBUTE_NOT_SUPPORTED, NOT_IMPLEMENTED), analysis errors raised only when the server analyses the plan, isolated sessions, and Python UDFs running server-side.',
    og_desc='A Python client with no JVM running Spark queries on a remote server: Spark Connect explained with real outputs and its limits.',
    minutes=24, level='Intermediate',
    lead='<b>Spark Connect</b> splits PySpark into a thin client and a Spark server talking gRPC. This lesson starts a Connect server, runs normal DataFrame code from a client with <b>no JVM</b>, and tests the differences: no SparkContext or RDDs, later error reporting, and isolated sessions. <b>All outputs are real</b> (Spark 4.3.0).',
    chips=['Spark 4.3.0', 'Connect server + client', 'Limits tested', 'Runs in your browser (Python)'],
)

MAIN = '''# What a Connect client sends: a plan, not data (simplified)
import json
plan = {"limit": 3,
        "input": {"sort": {"by": "revenue", "desc": True},
                  "input": {"aggregate": {"group_by": ["city"], "agg": "sum(amount) AS revenue"},
                            "input": {"read": {"format": "parquet", "path": "/data/orders_big"}}}}}
msg = json.dumps(plan)
print("bytes sent to the server:", len(msg))
print("rows the server reads   : 5,000,000")
print("rows sent back          : 3")
'''
RUN = dict(
    heading='Run the code: a plan over the wire',
    intro='<p>A simplified picture of what crosses the network. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('plan = {"limit": 3,', 'The client builds a nested, unresolved plan; the real protocol uses protobuf.'),
        ('print("rows sent back          : 3")', 'Only results return, as Arrow batches.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then remove the limit: what would come back?', code=None),
        dict(label='2 · Predict first: classic or Connect?', hint='<b>Predict first:</b> which APIs work under Connect?',
             code='''apis = {"df.groupBy": True, "spark.sql": True, "spark.sparkContext": False, "df.rdd": False, "F.udf": True}
print([k for k, ok in apis.items() if not ok])
'''),
        dict(label='3 · Connection string', hint='Build an sc:// URL with options.',
             code='''host, port, user = "spark.internal", 15002, "vineeta"
print(f"sc://{host}:{port}/;user_id={user};use_ssl=true")
'''),
        dict(label='4 · Lazy errors', hint='When does a bad column fail?',
             code='''steps = ["select('no_such_column')  -> plan only, no error",
         ".columns / .collect()       -> server analyses -> UNRESOLVED_COLUMN"]
print("\\n".join(steps))
'''),
        dict(label='5 · Spot the error', hint='Using SparkContext on a Connect session.', expect='error',
             code='''is_connect = True
assert not is_connect, "[JVM_ATTRIBUTE_NOT_SUPPORTED] Attribute sparkContext is not supported in Spark Connect"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: Spark Connect',
    intro='<p>With PySpark 4.3 installed (plus <code>grpcio</code>, <code>grpcio-status</code>, <code>googleapis-common-protos</code>). <b>Outputs are real</b> (Spark 4.3.0).</p>',
    items=[
        dict(title='1 · Start the server', cmd='$SPARK_HOME/sbin/start-connect-server.sh', file='bash',
             output='SparkConnectServer: Spark Connect server started at: 0.0.0.0:15002', note='In the server log.'),
        dict(title='2 · Connect', cmd='spark = SparkSession.builder.remote("sc://localhost:15002").getOrCreate()\ntype(spark).__module__, spark.version', file='python',
             output="('pyspark.sql.connect.session', '4.3.0')", note='Thin client.'),
        dict(title='3 · RDD', cmd='spark.range(3).rdd', file='python',
             output='PySparkNotImplementedError: [NOT_IMPLEMENTED] rdd is not implemented.', note='Use DataFrames.'),
    ],
)

TRACE = dict(
    heading='Client vs server responsibilities',
    intro='<p>Who does what for one query.</p>',
    code='''client = ["build plan", "serialize", "send gRPC"]
server = ["analyze", "optimize", "execute", "stream Arrow"]
for step in client:
    print("client:", step)
for step in server:
    print("server:", step)
''',
    notes={1: 'Client :: No Spark engine here.', 2: 'Server :: Catalyst + executors.'},
)

WORKED_INTRO = 'Three Spark Connect decisions at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='Connect · basics', title='Point a notebook at a server',
         problem='<p>Use the shared server from a notebook without changing code.</p>',
         inp='server address',
         approach=['Set SPARK_REMOTE.', 'SparkSession.builder.getOrCreate() picks it up.', 'Same DataFrame code.'],
         code='''import os
os.environ["SPARK_REMOTE"] = "sc://spark.internal:15002"
print("SPARK_REMOTE =", os.environ["SPARK_REMOTE"])
''', notes={2: 'Env var :: No code change needed.'},
         tryit='Step 1.'),
    dict(level='i', tag='Connect · migration', title='Audit code for Connect',
         problem='<p>Will a 2,000-line job run on Connect?</p>',
         inp='source code',
         approach=['Search for JVM-bound APIs.', 'List lines to rewrite.', 'Run tests with SPARK_REMOTE.'],
         code='''src = ["df.rdd.map(f)", "sc = spark.sparkContext", "df.groupBy('city').count()", "df._jdf.queryExecution()"]
bad = ("rdd", "sparkContext", "_jdf", "broadcast(", "accumulator")
print([l for l in src if any(b in l for b in bad)])
''', notes={2: 'Patterns :: Anything touching the JVM.'},
         tryit='Step 3.'),
    dict(level='a', tag='Connect · data', title='Where must files be?',
         problem='<p>An analyst reads a CSV from her laptop path.</p>',
         inp='/Users/v/sales.csv',
         approach=['The server reads paths, not the client.', 'Upload to shared storage.', 'Or createDataFrame from a small pandas DataFrame.'],
         code='''path = "/Users/v/sales.csv"
print("server cannot see it" if path.startswith("/Users") else "ok")
''', notes={1: 'Server-side :: Paths resolve on the server.'},
         tryit='Step 2.'),
]

QUIZ = mix([
    dict(q='Beginner: Spark Connect protocol?', options=['JDBC', 'gRPC', 'REST only', 'SSH'], answer=1,
         why='Plans as protobuf.'),
    dict(q='Beginner: Default Connect port?', options=['4040', '7077', '15002', '8088'], answer=2,
         why='sc://host:15002.'),
    dict(q='Beginner: Does the client need Java?', options=['Yes', 'No', 'Only for UDFs', 'Only on Windows'], answer=1,
         why='0 JVMs in the lab.'),
    dict(q='Intermediate: Which works under Connect?', options=['df.rdd', 'spark.sparkContext', 'df.groupBy().agg()', '_jdf'], answer=2,
         why='DataFrame API.'),
    dict(q='Intermediate: A missing column error appears…', options=['When defined', 'When the server analyses the plan', 'Never', 'At import'], answer=1,
         why='On .columns / actions.'),
    dict(q='Intermediate: Two clients’ temp views…', options=['Shared', 'Isolated per session', 'Deleted', 'Global'], answer=1,
         why='Session isolation.'),
    dict(q='Advanced: Where do Python UDFs execute?', options=['On the client', 'On the server’s executors', 'In the browser', 'Not supported'], answer=1,
         why='Install libraries on the server.'),
    dict(q='Advanced: Reading "/Users/v/a.csv" from a remote client…', options=['Works', 'The server cannot see that path', 'Auto-uploads', 'Uses HDFS'], answer=1,
         why='Paths are server-side.'),
])

REVISION = [
    'Client builds unresolved plans → gRPC → Connect server executes → Arrow back.',
    'Connect: <code>builder.remote("sc://host:15002")</code> or SPARK_REMOTE.',
    'Client needs no JVM (lab: 0 vs 1 for classic).',
    'No SparkContext, RDDs or _jdf (JVM_ATTRIBUTE_NOT_SUPPORTED / NOT_IMPLEMENTED).',
    'Analysis errors appear when the server analyses the plan.',
    'Sessions are isolated: temp views per client.',
    'Paths and UDF libraries are resolved on the server.',
]
FAQ = [
    ('Is Spark Connect slower?', 'There is a small network and serialization overhead per request; heavy work runs on the server as usual.'),
    ('Can I use pandas API on Spark and MLlib?', 'Most DataFrame-based APIs work; check the docs for your version, as coverage has grown in Spark 4.'),
    ('How is authentication done?', 'Usually via a gateway or token parameters in the connection string and TLS; the open-source server has minimal built-in auth.'),
    ('What is Databricks Connect?', 'Databricks’ client built on Spark Connect to run code from IDEs against Databricks clusters.'),
    ('Can Structured Streaming use Connect?', 'Yes, streaming queries can be started and managed from Connect clients, with some API differences (e.g. foreachBatch functions run on the server).'),
]

PRACTICE_INTRO = 'Programs about Connect behaviour.'
PROBLEMS = [
    dict(level='easy', title='URL', stmt='Build sc:// URL.', inp='host, port',
         code='''print("sc://%s:%d" % ("localhost", 15002))
''', explain='Default port.'),
    dict(level='easy', title='Rows back', stmt='Rows returned from 5M after groupBy city limit 3.', inp='lab',
         code='''print(3)
''', explain='Only results travel.'),
    dict(level='easy', title='JVMs', stmt='JVMs on 40 laptops: classic vs Connect.', inp='40',
         code='''print(40, "vs", 0)
''', explain='One server pool instead.'),
    dict(level='medium', title='Audit', stmt='Find JVM-bound lines.', inp='lines',
         code='''lines = ["x.rdd.count()", "df.select('a')", "spark.sparkContext.setLogLevel('WARN')"]
print([l for l in lines if "rdd" in l or "sparkContext" in l])
''', explain='Rewrite these.'),
    dict(level='medium', title='Session view', stmt='Model session isolation.', inp='two sessions',
         code='''s1, s2 = {"views": {"my_view"}}, {"views": set()}
print("my_view" in s1["views"], "my_view" in s2["views"])
''', explain='True False.'),
    dict(level='medium', title='Path check', stmt='Flag client-local paths.', inp='paths',
         code='''paths = ["/Users/v/a.csv", "s3a://lake/a.csv", "C:/data/b.csv"]
print([p for p in paths if p.startswith(("/Users", "C:"))])
''', explain='Server cannot read them.'),
    dict(level='business', title='Laptop RAM saved', stmt='GB saved with no local driver at 4 GB each.', inp='40 × 4',
         code='''print(40 * 4, "GB")
''', explain='Notebooks stay light.'),
    dict(level='business', title='Upgrade effort', stmt='Machines to upgrade: classic vs Connect.', inp='40 laptops vs 2 servers',
         code='''print(40, "vs", 2)
''', explain='Central upgrades.'),
]

SCN_INTRO = 'Spark Connect is a key Spark 4 topic.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“What is Spark Connect?”',
        'Explain Spark Connect.',
        'benefits?',
        '<p>A client-server architecture: a thin client sends unresolved plans over gRPC to a Spark Connect server that executes them. Clients need no JVM, sessions are isolated, and client and server can be upgraded separately.</p>', 'Saying it is a JDBC driver.') +
    scn('Data engineering', 'Mid-level', 'Migration blockers',
        'What can stop a PySpark job from running on Connect?',
        'list?',
        '''<ul>
          <li>RDD APIs and SparkContext usage.</li>
          <li>Direct JVM access (_jdf, py4j), accumulators, sc.broadcast.</li>
          <li>Local file paths the server cannot read.</li>
        </ul>''', 'Assuming 100% compatibility.') +
    scn('Data engineering', 'Mid-level', 'Late errors',
        'A typo in a column name is reported far from where it was written.',
        'why?',
        '''<ol>
          <li>Connect clients build plans without schema knowledge.</li>
          <li>Errors appear when the server analyses the plan.</li>
          <li>Call .columns or an action in tests to surface them.</li>
        </ol>''', 'Blaming the server.') +
    scn('Platform', 'Senior', 'Multi-user Spark',
        'Design Spark access for 200 analysts.',
        'design?',
        '''<ul>
          <li>Pools of Spark Connect servers behind an authenticating gateway.</li>
          <li>Thin clients in notebooks/IDEs; quotas per team.</li>
          <li>Central upgrades and monitoring.</li>
        </ul>''', 'One local driver per laptop.')
)
