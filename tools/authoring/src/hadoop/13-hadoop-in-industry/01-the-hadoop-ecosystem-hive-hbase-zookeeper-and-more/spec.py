import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()

META = dict(
    module='13-hadoop-in-industry', lesson='01-the-hadoop-ecosystem-hive-hbase-zookeeper-and-more', n='13.1',
    module_label='Module 13 · Hadoop in industry today',
    title='The Hadoop ecosystem: Hive, HBase, ZooKeeper and more',
    desc='The Hadoop ecosystem mapped layer by layer: HDFS and Ozone, Iceberg/Delta/Hudi, the Hive metastore, MapReduce/Tez/Spark/Flink, Hive/Spark SQL/Trino/Impala, HBase, ZooKeeper, Kafka and NiFi, Airflow, Ranger/Knox/Atlas. Which projects are active and which are retired (Sqoop 2021, Oozie 2025, Flume dormant 2024), checked on 22 Oct 2026. Real run: Spark SQL on our YARN cluster defines an external table over HDFS and its plan shows map-side combine, shuffle and reduce. Architecture diagram, animations, quiz and interview scenarios.',
    og_desc='Hive, HBase, ZooKeeper, Kafka, Spark, Iceberg, Ranger: where each fits on top of HDFS and YARN, what retired, and a real SQL-on-Hadoop run.',
    minutes=28, level='Beginner',
    lead='Hadoop itself is HDFS, YARN and MapReduce. Around it grew a family of projects that let analysts write SQL, apps look up single rows, pipelines ingest events and admins secure everything. This lesson maps them by layer, marks which are alive and which retired, and runs SQL on our own cluster to show the MapReduce pattern still inside.',
    chips=['Real Spark SQL run on YARN', 'Ecosystem map + 2 animations', 'Status checked 22 Oct 2026'],
)

RUN = dict(
    heading='Pick the right tool, then run a GROUP BY by hand',
    intro='<p>Part one is a tiny rule engine: describe a requirement and it suggests ecosystem projects. Part two does what our SQL engine did for <code>GROUP BY item</code>: partial counts per task (map + combine), a shuffle by key, and a final sum (reduce).</p>',
    code='''RULES = [  # (keyword in the requirement, suggestion)
    ("sql", "Hive / Spark SQL / Trino over metastore tables"),
    ("single row", "HBase (get by row key)"),
    ("events", "Kafka, then Spark or Flink"),
    ("update", "Iceberg / Delta / Hudi table format"),
    ("schedule", "Airflow (Oozie is retired)"),
    ("leader", "ZooKeeper"),
    ("access", "Ranger policies + Kerberos"),
]
def pick(req):
    return [tool for key, tool in RULES if key in req.lower()] or ["plain HDFS files + Spark"]

for r in ["Analysts need SQL on 3 years of bills",
          "App must fetch a single row per customer in 10 ms",
          "Clickstream events every second, update totals"]:
    print(f"{r[:44]:44} -> {pick(r)}")

# GROUP BY item, the way the plan executed it
tasks = [["chai", "dosa", "chai"], ["thali", "chai"], ["dosa", "chai", "thali"]]
partial = []
for t in tasks:                               # HashAggregate partial_count, per task
    counts = {}
    for item in t:
        counts[item] = counts.get(item, 0) + 1
    partial.append(counts)
print("partial counts:", partial)
final = {}
for counts in partial:                        # Exchange (shuffle by item) + final count
    for item, n in counts.items():
        final[item] = final.get(item, 0) + n
print("final        :", dict(sorted(final.items())))
''',
    anno=[
        ('    return [tool for key, tool in RULES if key in req.lower()] or ["plain HDFS files + Spark"]', 'A requirement can match several rules: real platforms combine tools.'),
        ('for t in tasks:                               # HashAggregate partial_count, per task', 'This loop is the combiner (Lesson 9.1): each task counts its own rows first.'),
        ('for counts in partial:                        # Exchange (shuffle by item) + final count', 'Only small partial counts cross the network, then the reducer adds them.'),
    ],
    tasks=[
        dict(label='1 · Tools and GROUP BY', hint='Press <b>Run</b>. Which requirement matched two tools?', code=None),
        dict(label='2 · Add a rule', hint='Add a rule so that “stream” suggests Flink. Then test “Fraud score on a payment stream”.',
             code='''RULES = [("sql", "Hive / Trino"), ("single row", "HBase"), ("events", "Kafka")]
RULES.append(("stream", "Flink (continuous processing)"))
req = "Fraud score on a payment stream"
print([tool for key, tool in RULES if key in req.lower()])
'''),
        dict(label='3 · Revenue per item', hint='Change the GROUP BY simulation to SUM(amount). Rows are (item, amount).',
             code='''tasks = [[("chai", 15), ("dosa", 45)], [("thali", 80), ("chai", 15)]]
final = {}
for t in tasks:
    part = {}
    for item, amount in t:
        part[item] = part.get(item, 0) + amount
    for item, s in part.items():
        final[item] = final.get(item, 0) + s
print(dict(sorted(final.items())))
'''),
        dict(label='4 · Alive or retired?', hint='Look up each project in the status table (from the Apache Attic, checked 22 Oct 2026).',
             code='''status = {"Sqoop": "retired 2021", "Oozie": "retired 2025", "Flume": "dormant 2024",
          "Sentry": "retired 2020", "Hive": "active", "HBase": "active", "ZooKeeper": "active"}
for p in ["Sqoop", "Hive", "Oozie", "ZooKeeper", "Flume"]:
    print(f"{p:10} {status[p]}")
'''),
        dict(label='5 · Spot the error', hint='The metastore lookup fails for a table that was never created. Make the code print a helpful message instead.',
             code='''metastore = {"canteen.orders": "hdfs://namenode/user/hadoop/data/student_orders.csv"}
print("reading", metastore["canteen.menu"])
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: SQL on Hadoop with Spark',
    intro='<p>Uses the Module 8 lab. Download Spark 4.0.4 (<code>spark-4.0.4-bin-hadoop3.tgz</code> from dlcdn.apache.org), copy it into the namenode container and unpack it. Spark needs to know where Hadoop\'s configuration is so it can find HDFS and YARN. Three executors of 512 MB fit our small cluster.</p>',
    items=[
        dict(title='SQL over an HDFS file, on YARN', file='sql_on_hadoop.sql',
             cmd=rd('lab/sql_on_hadoop.sql') + '\n-- In the namenode container (after unpacking Spark into /tmp/opt):\n--   export SPARK_HOME=/tmp/opt/spark-4.0.4-bin-hadoop3\n--   export HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop\n--   $SPARK_HOME/bin/spark-sql --master yarn --num-executors 3 --executor-memory 512m \\\n--       --executor-cores 1 --driver-memory 512m -f sql_on_hadoop.sql',
             output=rd('tx131.txt').strip(),
             note='Real output with Spark\'s INFO/WARN logging filtered out. The first query takes longer (11.1 s) because executors and the plan warm up; later ones reuse them. spark-sql creates metastore_db (a local Derby metastore) and spark-warehouse in the folder you run it from.'),
    ],
)

TRACE = dict(
    heading='How a metastore answers “where is this table?”',
    intro='<p>An engine never scans HDFS looking for a table. It asks the metastore for the location and format, then plans the read.</p>',
    code='''metastore = {}
metastore["canteen.orders"] = {"location": "hdfs://namenode/user/hadoop/data/student_orders.csv",
                               "format": "csv", "columns": ["order_id", "student", "ts", "item", "amount"]}
query_table, needed = "canteen.orders", ["item"]
entry = metastore[query_table]
cols = [c for c in entry["columns"] if c in needed]
print("read", entry["location"], "as", entry["format"], "columns", cols)
''',
    notes={2: 'CREATE TABLE :: Only this dictionary entry is written; no data moves.',
           5: 'Lookup :: Every engine (Hive, Spark, Trino) asks the same metastore.',
           6: 'Pruning :: Only the needed column is planned, as in the plan, which read only the item column.'},
)

WORKED_INTRO = 'Four “which tool?” decisions from different industries, each reasoned from the requirement.'
EXAMPLES = [
    dict(level='b', tag='Retail · SQL', title='Analysts want SQL on five years of sales',
         problem='<p>A retail chain has 5 years of daily sales as CSV files in HDFS. Analysts know SQL, not Java. What do you add, and do you need to copy the data?</p>',
         inp='CSV in HDFS · SQL users',
         approach=['SQL over files = a metastore table + a SQL engine.',
                   'An EXTERNAL table points at the files: nothing is copied.',
                   'Later, convert to Parquet for speed (Lesson 10.2).'],
         code='''files_gb, copy_needed = 900, False
print(f"Define an external table over {files_gb} GB; copy needed: {copy_needed}")
print("Engine: Hive or Spark SQL for batch, Trino for quick questions")
''', notes={1: 'External :: Like our canteen.orders table: 0.753 s to create.'},
         tryit='Our CREATE TABLE took 0.753 s for 19.4 MB, and would take the same for 900 GB: only metadata is written.'),
    dict(level='i', tag='Telecom · NoSQL', title='Customer care needs one subscriber in 10 ms',
         problem='<p>A care agent types a mobile number and must see the plan and last recharge within 10 ms. The data is 40 crore rows. Is Hive the right choice?</p>',
         inp='40 crore rows · 1 row per request · 10 ms',
         approach=['A SQL engine scans files; even a fast one takes seconds.',
                   'A key-value store reads one row by key directly.',
                   'Keep both: HBase for lookups, Parquet tables for analytics.'],
         code='''rows, row_bytes, disk_mb_s = 400_000_000, 200, 150
scan_s = rows * row_bytes / (disk_mb_s * 1024 * 1024)
print(f"full scan on one disk: {scan_s / 60:.0f} minutes; HBase get by key: a few milliseconds")
''', notes={2: 'Scan :: Even split over 100 disks this is seconds, not milliseconds.'},
         tryit='Design the HBase row key as the mobile number (maybe reversed or salted to avoid hot spots).'),
    dict(level='i', tag='Logistics · workflow', title='Replacing Oozie after its retirement',
         problem='<p>A logistics firm runs 120 Oozie workflows. Oozie was retired to the Apache Attic in February 2025. Plan the move and estimate effort at 1.5 days per workflow with 2 engineers.</p>',
         inp='120 workflows · 1.5 days each · 2 engineers',
         approach=['Target: Airflow DAGs calling the same Spark/Hive jobs.',
                   'Migrate in waves, run old and new side by side, compare outputs.',
                   'Estimate calendar time.'],
         code='''workflows, days_each, engineers = 120, 1.5, 2
print(f"{workflows * days_each / engineers:.0f} working days, about {workflows * days_each / engineers / 21:.1f} months")
''', notes={1: 'Effort :: Parallel runs add time; plan buffer.'},
         tryit='Prioritise workflows that break most often or block an upgrade.'),
    dict(level='a', tag='Fintech · tables', title='Deleting one customer\'s data on request',
         problem='<p>A fintech must delete a customer\'s records on request from a 2 TB transactions table stored as Parquet in HDFS (5,000 files). Plain Parquet files cannot be edited in place. Compare rewriting everything with a table format.</p>',
         inp='2 TB · 5,000 files · rows of 1 customer spread over ~40 files',
         approach=['Plain files: rewrite every file that contains the customer, and know which ones they are.',
                   'Iceberg/Delta/Hudi: DELETE … WHERE customer = …, rewriting only affected files and committing a snapshot.',
                   'Compare bytes rewritten.'],
         code='''total_gb, files, affected = 2048, 5000, 40
naive = total_gb
smart = total_gb / files * affected
print(f"rewrite everything: {naive} GB; table format rewrites ~{smart:.1f} GB in {affected} files")
''', notes={2: 'Naive :: Without file-level metadata you cannot know which files to touch.'},
         tryit='Lesson 13.4 runs a real Iceberg DELETE on HDFS and time-travels back to the old snapshot.'),
]

QUIZ = mix([
    dict(q='Which three components are Hadoop itself (not the wider ecosystem)?', options=['Hive, HBase, ZooKeeper', 'HDFS, YARN and MapReduce (plus Common)', 'Spark, Kafka, Flink', 'Ranger, Knox, Atlas'], answer=1,
         why='Everything else is a separate project built around them.'),
    dict(q='What does the metastore store?', options=['The table data', 'Table definitions: columns, format and file location', 'Kerberos tickets', 'YARN logs'], answer=1,
         why='Our CREATE TABLE wrote only a definition and took 0.753 s.'),
    dict(q='Which project gives millisecond reads of a single row by key on top of HDFS?', options=['Hive', 'HBase', 'Oozie', 'Sqoop'], answer=1,
         why='Hive and other SQL engines scan files; HBase serves rows by key.'),
    dict(q='What does ZooKeeper do in a Hadoop cluster?', options=['Stores large files', 'Coordination: leader election, locks, configuration', 'Runs SQL', 'Compresses data'], answer=1,
         why='For example, deciding which NameNode is active (Lesson 7.1).'),
    dict(q='Which project was retired to the Apache Attic in June 2021?', options=['Hive', 'Sqoop', 'Spark', 'HBase'], answer=1,
         why='Oozie followed in February 2025; Flume became dormant in October 2024.'),
    dict(q='In Spark\'s plan, what is the Exchange hashpartitioning step?', options=['Reading the CSV', 'The shuffle that sends each key to one task', 'Writing the output', 'Starting YARN'], answer=1,
         why='Same role as the partitioner and shuffle of Lessons 8.4 and 9.2.'),
    dict(q='What does EXTERNAL mean for a table?', options=['The data is in another country', 'Dropping the table does not delete the files', 'It is stored in HBase', 'It can only be read by Trino'], answer=1,
         why='Our table pointed at an existing HDFS file.'),
    dict(q='What is a common replacement for Oozie today?', options=['Flume', 'Apache Airflow', 'Sentry', 'Pig'], answer=1,
         why='Workflows are written as Python DAGs.'),
])

REVISION = [
    'Hadoop = <b>HDFS + YARN + MapReduce</b> (+ Common). The ecosystem is built <i>around</i> it.',
    'Layers: storage (HDFS, Ozone, object stores) → tables (Iceberg/Delta/Hudi, metastore, HBase, Kudu) → YARN → engines (MapReduce, Tez, Spark, Flink) and SQL (Hive, Spark SQL, Trino, Impala, Drill).',
    'Around them: ingestion (Kafka, NiFi), workflow (Airflow), coordination (ZooKeeper), security (Ranger, Knox, Atlas).',
    'Retired: Sqoop (Jun 2021), Sentry (Dec 2020), Oozie (Feb 2025); Flume dormant since Oct 2024 (checked 22 Oct 2026).',
    'Metastore = table definitions; engines share it. EXTERNAL tables just point at files.',
    'Lab: Spark SQL on YARN, GROUP BY over 5 lakh orders in 11.1 s; plan = partial aggregate → shuffle → final aggregate.',
]
FAQ = [
    ('What are the main components of the Hadoop ecosystem?', 'The core is HDFS (storage), YARN (resource management) and MapReduce (processing). Around it: Hive and other SQL engines (Spark SQL, Trino, Impala), HBase for low-latency key access, ZooKeeper for coordination, Spark, Tez and Flink as processing engines, Kafka and NiFi for ingestion, Airflow for scheduling, Ranger, Knox and Atlas for security and governance, and table formats such as Apache Iceberg.'),
    ('What is the difference between Hive and HBase?', 'Hive is a SQL engine over files: good for scanning and aggregating large tables, with query times of seconds to minutes. HBase is a NoSQL store for reading and writing individual rows by key in milliseconds. Many systems use both: HBase to serve applications, Hive or Spark for analytics.'),
    ('Is Sqoop still used?', 'Apache Sqoop was retired to the Apache Attic in June 2021, and Amazon EMR stopped including it from release 7.4.0. Older clusters may still run it, but new pipelines usually use Spark JDBC reads or change-data-capture into Kafka.'),
    ('Why does Hadoop need ZooKeeper?', 'Distributed services must agree on facts such as which NameNode is active or which HBase server owns which rows, even when machines fail. ZooKeeper provides a small, replicated, strongly consistent store with watches and ephemeral nodes that these services use for leader election, locks and configuration.'),
    ('What is the Hive metastore?', 'A service and database holding table and partition definitions: column names and types, storage format, and file locations. Hive, Spark, Trino, Impala and others share it, so a table defined once can be queried by many engines.'),
]

PRACTICE_INTRO = 'Ecosystem exercises: place projects, read our real results, and choose tools.'
PROBLEMS = [
    dict(level='easy', title='Average order value per item', stmt='From our real GROUP BY, compute revenue per order for thali, dosa and chai.', inp='thali 30292 2423360 · dosa 49927 2246715 · chai 149669 2245035',
         code='''for item, n, rev in [("thali", 30292, 2423360), ("dosa", 49927, 2246715), ("chai", 149669, 2245035)]:
    print(item, rev / n)
''', explain='80, 45 and 15: the menu prices, so the SQL result agrees with the data.'),
    dict(level='easy', title='Share of the lunch rush', stmt='What share of all 5 lakh orders came in the 13 and 14 o\'clock hours?', inp='13 → 56,026 · 14 → 62,213',
         code='''print(f"{(56026 + 62213) / 500000:.1%}")
''', explain='23.6% of orders in two of the thirteen opening hours.'),
    dict(level='easy', title='Retired or not', stmt='Count how many of these are retired or dormant: Sqoop, Hive, Oozie, Flume, HBase, Sentry.', inp='status table',
         code='''gone = {"Sqoop", "Oozie", "Flume", "Sentry"}
print(len(gone & {"Sqoop", "Hive", "Oozie", "Flume", "HBase", "Sentry"}))
''', explain='4 of 6. Hive and HBase are active.'),
    dict(level='medium', title='Layer sorter', stmt='Assign each project to its layer.', inp='8 projects',
         code='''layer = {"HDFS": "storage", "Iceberg": "tables", "YARN": "resources", "Spark": "engine",
         "Trino": "SQL", "Kafka": "ingestion", "ZooKeeper": "coordination", "Ranger": "security"}
for p, l in layer.items():
    print(f"{p:10} {l}")
''', explain='The same layers as the architecture diagram.'),
    dict(level='medium', title='Combiner savings', stmt='5 lakh rows, 8 items, 3 tasks. How many records cross the shuffle with and without partial aggregation?', inp='500,000 rows · 8 keys · 3 tasks',
         code='''rows, keys, tasks = 500_000, 8, 3
print("without:", rows, "with partial aggregation:", keys * tasks)
''', explain='500,000 vs at most 24: why the plan aggregates before the Exchange.'),
    dict(level='medium', title='Which engine?', stmt='Match: nightly 2 TB batch, ad-hoc analyst SQL in seconds, per-second event stream.', inp='3 workloads',
         code='''m = {"nightly 2 TB batch": "Spark (or Hive on Tez)", "ad-hoc SQL in seconds": "Trino / Impala",
     "per-second event stream": "Flink or Spark Structured Streaming via Kafka"}
for k, v in m.items():
    print(f"{k:24} -> {v}")
''', explain='One cluster often runs all three on YARN or alongside it.'),
    dict(level='business', title='Cost of a retired tool', stmt='A retired tool gets no security fixes. If an incident costs ₹50 lakh with a 5% yearly chance, and migration costs ₹12 lakh once, how many years until migration pays off?', inp='₹50 lakh × 5% vs ₹12 lakh',
         code='''risk_per_year = 50 * 0.05
print(f"{12 / risk_per_year:.1f} years")
''', explain='About 4.8 years on risk alone (illustrative); add support and hiring costs and it pays off sooner.'),
    dict(level='advanced', title='Mini metastore', stmt='Build a dict-based metastore with create, describe and drop; EXTERNAL drop keeps files, MANAGED drop deletes them.', inp='2 tables',
         code='''files = {"/data/orders.csv", "/warehouse/menu"}
ms = {"orders": ("EXTERNAL", "/data/orders.csv"), "menu": ("MANAGED", "/warehouse/menu")}
def drop(t):
    kind, loc = ms.pop(t)
    if kind == "MANAGED":
        files.discard(loc)
drop("orders"); drop("menu")
print("tables:", ms, "files left:", files)
''', explain='Only the external table\'s file survives, the same rule Hive and Spark follow.'),
]

SCN_INTRO = 'Ecosystem questions test whether you know what each tool is for, and what is current.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Concepts · map</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“Draw the Hadoop ecosystem”</h4>
      <p class="scn__situation">A whiteboard question in most big-data interviews.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> layers and one purpose per tool.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Bottom: HDFS (or object storage); middle: YARN; top: engines (MapReduce, Tez, Spark) and SQL (Hive, Trino).</li>
          <li>Side services: HBase for key lookups, ZooKeeper for coordination, Kafka for ingestion, Airflow for scheduling, Ranger for security.</li>
          <li>Mention what changed: Sqoop and Oozie retired; Iceberg-style table formats are now common.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Design · storage</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>“Hive or HBase for our customer 360 view?”</h4>
      <p class="scn__situation">The app needs one customer instantly; analysts need segments over all customers.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> access patterns.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Point reads by key with low latency → HBase (row key design, avoid hot spots).</li>
          <li>Scans and aggregations → Parquet/Iceberg tables queried with Hive, Spark or Trino.</li>
          <li>Feed both from the same pipeline; don't force one store to do both jobs.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Operations · migration</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Your cluster still runs Sqoop and Oozie</h4>
      <p class="scn__situation">Both are retired. The manager asks what to do and how risky it is.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> awareness and a safe plan.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Retired means no releases or security fixes; vendors may still ship them for a while, but plan to leave.</li>
          <li>Sqoop → Spark JDBC or CDC into Kafka; Oozie → Airflow DAGs calling the same jobs.</li>
          <li>Migrate in waves with side-by-side runs and output comparison; retire the old ones last.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Internals · engines</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“Does Hive still use MapReduce?”</h4>
      <p class="scn__situation">A follow-up after you mention Hive.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> engines vs SQL layer.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Hive is a SQL layer; the execution engine is pluggable. Hive 4 encourages Tez; MapReduce was the original engine.</li>
          <li>Whatever the engine, a GROUP BY becomes partial aggregation, a shuffle by key and a final aggregation.</li>
          <li>Spark SQL showed exactly this in our EXPLAIN output.</li>
        </ul>
      </div></details>
    </article>
'''
