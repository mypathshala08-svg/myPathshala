import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from hivekit import tables
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return re.sub(r'; Query ID[^\n]*', '', open(CAP + n).read().rstrip())
BODY = body(HERE)

META = dict(
    module='11-hive-in-industry', lesson='01-hive-spark-and-trino', n='11.1',
    module_label='Module 11 · Hive in industry today',
    title='Hive, Spark SQL and Trino: one metastore, many engines',
    desc='Connect Spark 3.5.6 and Trino 476 to a Hive 4.2.1 metastore and compare real results: Spark’s built-in 2.3.9 metastore client failing with “Invalid method name get_table”, a Hive 3.1.3 client that works, identical answers for ORC tables and Hive views, a transactional table giving 5,000,001 rows in Hive, 5,000,004 in Trino and 0 in Spark, Iceberg through Trino’s iceberg catalog, Spark-written tables read by Hive, SQL dialect differences and indicative timings.',
    og_desc='Same Hive table, three engines, three answers: 5,000,001 in Hive, 5,000,004 in Trino, 0 in Spark. A real interoperability test on one metastore.',
    minutes=45, level='Intermediate → Advanced',
    lead='Module 11 places Hive in today’s data stack. Most companies run several engines on one Hive metastore. This lesson connects <b>Spark</b> and <b>Trino</b> to our Hive 4.2.1 lab and runs the same queries everywhere: plain tables agree, but versions, transactional tables, Iceberg and SQL dialects produce real surprises. <b>All outputs are real</b>; the engine configurations are in the course lab folder.',
    chips=['Hive 4.2.1 · Spark 3.5.6 · Trino 476', 'Three answers for one table', 'Configs included', 'Runs in your browser (Python)'],
)

MAIN = '''# An interoperability test: compare row counts per engine (real lab numbers)
results = {
    "orders (ORC)":        {"Hive": 50000,   "Spark": 50000, "Trino": 50000},
    "v_gold_orders (view)": {"Hive": 13014,   "Spark": 13014, "Trino": 13014},
    "orders_tx (ACID)":    {"Hive": 5000001, "Spark": 0,     "Trino": 5000004},
    "orders_ice (Iceberg)": {"Hive": 4886,   "Spark": None,  "Trino": 4886},
}
for table, counts in results.items():
    ref = counts["Hive"]
    bad = [e for e, c in counts.items() if c != ref]
    print(f"{table:22}", "OK" if not bad else "MISMATCH in " + ", ".join(bad))
'''
RUN = dict(
    heading='Run the code: an interoperability test',
    intro='<p>These programs model the checks a platform team runs across engines, with the real numbers from the lab. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    "orders_tx (ACID)":    {"Hive": 5000001, "Spark": 0,     "Trino": 5000004},', 'The real counts: neither Spark nor Trino raised an error.'),
        ('    bad = [e for e, c in counts.items() if c != ref]', 'Hive is the reference for Hive-native table types; compare every engine against it.'),
    ],
    tasks=[
        dict(label='1 · Find mismatches', hint='Press <b>Run</b>. Two table types fail the test; None means the engine could not read it at all.', code=None),
        dict(label='2 · Predict first: why 5,000,004?', hint='<b>Predict first:</b> the table had 5,000,000 rows, then 3 inserts, 2 deletes and 1 update. What does an engine that ignores delete deltas count?',
             code='''base, inserts, deletes, updates = 5_000_000, 3, 2, 1
correct = base + inserts - deletes
ignoring_deletes = base + inserts + updates     # an update = delete old + insert new
print("correct:", correct, " ignoring delete deltas:", ignoring_deletes)
'''),
        dict(label='3 · Which engine for which job?', hint='Map workloads to engines like the table in section 3.',
             code='''jobs = {"nightly MERGE into ACID tables": "Hive",
        "feature engineering in Python": "Spark",
        "dashboard with 2 s target": "Trino",
        "join Hive table with PostgreSQL": "Trino"}
for j, e in jobs.items():
    print(f"{e:6} <- {j}")
'''),
        dict(label='4 · Speed-up, honestly', hint='Compare warm runs from the lab. One machine, small data: indicative only.',
             code='''warm = {"Trino": 0.75, "Hive": 1.60, "Spark": 2.10}
base = warm["Hive"]
for e, s in warm.items():
    print(f"{e:5} {s:.2f} s  ({base / s:.1f}x vs Hive)")
'''),
        dict(label='5 · Spot the error', hint='This test only checks that a query runs. Make it compare counts.', expect='error',
             code='''spark_count, hive_count = 0, 5_000_001
test_passed = spark_count is not None          # bug: 0 rows also "runs"
assert test_passed == (spark_count == hive_count), "compare results, not just success"
print("passed")
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: Trino catalogs, tables and plans',
    intro='<p>More from the Trino side of the lab. <b>Outputs are real</b> (Trino 476).</p>',
    items=[
        dict(title='1 · Catalogs', cmd='SHOW CATALOGS;', file='trino',
             output=capf('l111_trino_catalogs.txt'),
             note='hive and iceberg come from our two catalog files; both point at the same metastore. system is built in.'),
        dict(title='2 · The Hive tables, seen from Trino', cmd="SHOW TABLES FROM hive.tiffingo LIKE 'orders%';", file='trino',
             output='\n'.join(capf('l111_trino_tables.txt').split('\n')[:14]) + '\n…',
             note='Every table registered in the metastore by Hive appears, whatever engine will be able to read it.'),
        dict(title='3 · A Trino distributed plan', cmd='EXPLAIN (TYPE DISTRIBUTED)\nSELECT city, COUNT(*) FROM hive.tiffingo.orders GROUP BY city;', file='trino',
             output=capf('l111_trino_explain.txt') + '\n…',
             note='Trino plans in fragments connected by exchanges, comparable to Tez vertices and edges in Lesson 8.1, with its own estimates from the same metastore statistics.'),
    ],
)

TRACE = dict(
    heading='Why the ACID counts differ',
    intro='<p>Follow how a correct reader and a reader that ignores delete deltas count <code>orders_tx</code>.</p>',
    code='''base_rows = 5_000_000
delta_rows = 4            # 999000001, 999000002, 999000010 (NEW), 999000010 (CANCELLED)
deleted = 3               # 999000001, 999000002, old 999000010 (NEW)
hive = base_rows + delta_rows - deleted
trino = base_rows + delta_rows
print("Hive:", hive, " Trino 476:", trino, " Spark: 0 (does not read Hive ACID)")
''',
    notes={2: 'Deltas :: Every insert and the new version of the update.', 3: 'Delete deltas :: Two DELETEs and the old version from the UPDATE.', 5: 'Mismatch :: An engine that skips delete deltas returns rows that no longer exist.'},
)

WORKED_INTRO = 'Three multi-engine decisions from real platforms.'
EXAMPLES = [
    dict(level='b', tag='Analytics · tooling', title='Pick the engine for a request',
         problem='<p>Decide which engine should answer four requests at TiffinGo.</p>',
         inp='four requests',
         approach=['Interactive → Trino.', 'Python/ML → Spark.', 'Writes to Hive ACID → Hive.'],
         code='''req = {"Top cities yesterday, on a dashboard": "Trino",
       "Train a churn model": "Spark",
       "Nightly MERGE of customer changes": "Hive",
       "One-off join with the payments PostgreSQL": "Trino (federation)"}
for k, v in req.items():
    print(f"{v:20} <- {k}")
''', notes={2: 'Federation :: Trino can join catalogs of different systems in one query.'},
         tryit='All three engines share the metastore, so the tables are the same; only the reader changes.'),
    dict(level='i', tag='Data engineering · interop', title='Make a table readable everywhere',
         problem='<p>Data scientists need yesterday’s orders from a Hive ACID table in Spark.</p>',
         inp='orders_tx (full ACID), Spark returns 0 rows',
         approach=['Write a plain snapshot from Hive.', 'Spark reads the snapshot.', 'Plan a move to Iceberg.'],
         code='''print("INSERT OVERWRITE TABLE orders_snapshot PARTITION (d = '2026-10-29')")
print("SELECT order_id, customer_id, city, amount, status FROM orders_tx WHERE order_date = '2026-10-29';")
print("-- orders_snapshot: STORED AS PARQUET, external, read by Spark and Trino")
''', notes={1: 'Snapshot :: Hive applies deletes and updates while writing plain files.'},
         tryit='Spark-written Parquet and ORC tables were read correctly by Hive in Step 7; the reverse works for plain tables too.'),
    dict(level='a', tag='Architecture · platform', title='Engine compatibility matrix',
         problem='<p>Turn the lab results into a support matrix for the platform wiki.</p>',
         inp='results from Steps 3–7',
         approach=['Rows = table types; columns = engines.', 'Mark supported, unsupported, or needs config.', 'Re-run after every upgrade.'],
         code='''matrix = {
  "ORC/Parquet/text": ("yes", "yes", "yes (Hadoop FS)"),
  "Hive views":       ("yes", "yes", "yes (enable views)"),
  "Hive full ACID":   ("yes", "NO (0 rows)", "NO (deletes ignored)"),
  "Iceberg":          ("yes", "needs Iceberg catalog", "yes (iceberg catalog)"),
}
print(f"{'':18} {'Hive':6} {'Spark':22} Trino")
for k, (h, s, t) in matrix.items():
    print(f"{k:18} {h:6} {s:22} {t}")
''', notes={5: 'Versions :: Valid for Hive 4.2.1, Spark 3.5.6 and Trino 476 in our lab; retest for yours.'},
         tryit='Publishing such a matrix saves every team from discovering the empty-table problem on its own.'),
]

QUIZ = mix([
    dict(q='Beginner: What do Hive, Spark and Trino share in this lesson?', options=['The data files only', 'The Hive metastore (catalogue) and the files', 'The SQL parser', 'Nothing'], answer=1,
         why='Each engine still reads files with its own code.'),
    dict(q='Beginner: Which engine is typically chosen for low-latency dashboards?', options=['Hive on Tez', 'Trino', 'MapReduce', 'Sqoop'], answer=1,
         why='Trino ran our aggregation in about 0.75 s warm.'),
    dict(q='Beginner: How did Trino address the orders table?', options=['orders', 'hive.tiffingo.orders', 'tiffingo:orders', '/warehouse/orders'], answer=1,
         why='catalog.schema.table.'),
    dict(q='Intermediate: Why did Spark first fail with “Invalid method name: get_table”?', options=['Wrong table', 'Its built-in Hive 2.3.9 metastore client uses a method Hive 4’s metastore removed', 'Network error', 'Permissions'], answer=1,
         why='A Hive 3.1.3 client worked.'),
    dict(q='Intermediate: What did Spark return for the Hive ACID table?', options=['An error', '0 rows, silently', 'The correct count', 'Duplicates'], answer=1,
         why='Spark does not read Hive ACID tables.'),
    dict(q='Intermediate: How did Trino read the Iceberg table?', options=['Through the hive catalog', 'Through an iceberg catalog on the same metastore', 'It could not', 'Through Spark'], answer=1,
         why='The hive catalog said “Cannot query Iceberg table”.'),
    dict(q='Advanced: Why did Trino count 5,000,004 rows?', options=['Duplicated files', 'It ignored Hive 4.2.1’s delete deltas, returning deleted and old versions', 'Statistics', 'A join'], answer=1,
         why='Hive: 5,000,001.'),
    dict(q='Advanced: What silently returned 0 rows in Trino?', options=['Wrong credentials', 'The native local file system with file: table locations', 'A missing view setting', 'Iceberg'], answer=1,
         why='fs.hadoop.enabled=true fixed it in our lab.'),
])

REVISION = [
    'One <b>metastore</b>, many engines: tables are shared; each engine reads files with its own code.',
    '<b>Spark</b>: Hive support + <code>hive.metastore.uris</code>; built-in client 2.3.9 failed on Hive 4 (<code>get_table</code>); <code>spark.sql.hive.metastore.version=3.1.3</code> worked.',
    '<b>Trino</b>: catalog files (<code>connector.name=hive</code>, <code>hive.metastore.uri</code>, file-system settings); <code>hive.hive-views.enabled</code> for views; <code>catalog.schema.table</code>.',
    'Plain ORC/Parquet/text tables and simple views: identical answers in all three engines.',
    'Hive full ACID: Hive 5,000,001 · Trino 476: 5,000,004 · Spark: 0. No errors.',
    'Iceberg: use an Iceberg catalog (Trino iceberg connector: 4,886 ✓); Spark 3.5 needed a compatible metastore client.',
    'Dialects differ (Hive reserves <code>rows</code>; Trino needs <code>DATE \'…\'</code>). Verify counts after every setup or upgrade.',
    'Indicative warm timings on 5M rows: Trino 0.75 s · Hive 1.6 s · Spark 2.1 s.',
]
FAQ = [
    ('Is Hive still used if Spark and Trino exist?', 'Yes. Hive is still common for SQL-based ETL and as the metastore that every other engine depends on, and Cloudera’s data warehouse runs on Hive with LLAP and Iceberg. Many platforms use Hive for loads and Spark or Trino for analysis.'),
    ('What is the Hive Warehouse Connector?', 'A Cloudera library that lets Spark read and write Hive managed (ACID) tables through HiveServer2/LLAP instead of reading the files directly, solving the “0 rows” problem of Step 5 on those platforms.'),
    ('Should all shared tables be Iceberg?', 'For tables written or read by several engines, many teams now choose Iceberg, because Hive, Spark, Trino, Flink and cloud services implement the same specification. Hive ACID remains fine for Hive-only tables. Lesson 11.3 covers migration.'),
    ('Why were Trino and Spark timings different from Hive’s?', 'Different architectures (Trino keeps long-running workers and pipelines data in memory; Spark and Hive on Tez schedule tasks), different measurement points, a single machine and small data. Benchmark on your own cluster and data.'),
    ('Do Spark and Trino respect Hive grants?', 'No, SQL-standard grants are enforced inside HiveServer2 (Lesson 10.2). Use Ranger plugins for each engine or a shared permission layer, and restrict direct file access.'),
]

PRACTICE_INTRO = 'Programs for cross-engine checks, with the SQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Count difference', stmt='How many extra rows did Trino return for orders_tx?', inp='Hive 5,000,001, Trino 5,000,004',
         code='''print(5_000_004 - 5_000_001)
''', explain='3: two deleted orders and the old version of the updated one.'),
    dict(level='easy', title='Three-part name', stmt='Build a Trino table name from catalog, schema and table.', inp='hive, tiffingo, orders',
         code='''print(".".join(["hive", "tiffingo", "orders"]))
''', explain='In Hive the same table is tiffingo.orders.'),
    dict(level='easy', title='Date literal', stmt='Rewrite a Hive filter for Trino.', inp="order_date = '2026-10-05'",
         code='''print("order_date = DATE '2026-10-05'")
''', explain='Trino refused DATE = VARCHAR; the typed literal works in Hive too.'),
    dict(level='medium', title='Rename reserved aliases', stmt='Rename aliases that are reserved words in Hive.', inp="aliases ['rows', 'n', 'date']",
         code='''reserved = {"rows", "date", "user", "time"}
print([a + "_cnt" if a in reserved else a for a in ["rows", "n", "date"]])
''', explain='AS rows failed in Hive with a ParseException; AS n worked.'),
    dict(level='medium', title='Spark config lines', stmt='Generate the spark-sql options for a Hive 3.1.3 client.', inp='metastore URI',
         code='''uri = "thrift://localhost:9083"
for k, v in {"spark.hadoop.hive.metastore.uris": uri, "spark.sql.hive.metastore.version": "3.1.3", "spark.sql.hive.metastore.jars": "maven"}.items():
    print(f"--conf {k}={v}")
''', explain='In production use jars=path with a pinned local copy.'),
    dict(level='medium', title='Trino catalog file', stmt='Write a Trino hive catalog for a metastore and HDFS-style paths.', inp='metastore host hms1',
         code='''lines = ["connector.name=hive", "hive.metastore.uri=thrift://hms1:9083", "fs.hadoop.enabled=true", "hive.hive-views.enabled=true"]
print("\\n".join(lines))
''', explain='Save as etc/trino/catalog/hive.properties and restart Trino.'),
    dict(level='business', title='Cost of a wrong count', stmt='A dashboard on Trino over an ACID table overcounts cancelled orders by 0.0001%. Does it matter?', inp='5,000,004 vs 5,000,001',
         code='''print(f"{(5_000_004 - 5_000_001) / 5_000_001:.5%}")
''', explain='Tiny here, but deletes can be large (GDPR erasure, refunds): the error grows with every delete, so fix the design, not the number.'),
    dict(level='business', title='Engine mix', stmt='Share of 1,000 daily queries per engine after moving BI to Trino.', inp='700 BI, 200 ETL, 100 ML (illustrative)',
         code='''q = {"Trino (BI)": 700, "Hive (ETL)": 200, "Spark (ML)": 100}
for k, v in q.items():
    print(f"{k:12} {v / 1000:.0%}")
''', explain='Most queries move to the fast engine; Hive keeps the heavy, transactional loads.'),
]

SCN_INTRO = 'Multi-engine questions are standard in data platform interviews.'
SCENARIOS = (
    scn('Any company · Hive', 'Fresher', '“Can Spark read Hive tables?”',
        'Explain how Spark and Trino use Hive tables.',
        'do you know the metastore’s role?',
        '<p>Yes: both connect to the Hive metastore, so they see the same databases and tables, then read the ORC/Parquet files directly. Spark needs Hive support and the metastore URI; Trino needs a hive catalog. Hive-specific table types such as ACID tables are not fully supported by all engines, so results should be checked.</p>', 'Saying Spark queries HiveServer2.') +
    scn('Data engineering', 'Mid-level', 'Different counts in two engines',
        'A table shows different row counts in Hive and Trino.',
        'can you find the cause?',
        '''<ol>
          <li>Check the table type: transactional? Iceberg? Views?</li>
          <li>For ACID tables, deletes and updates live in delete deltas some readers ignore; compare a few known deleted keys.</li>
          <li>Fix: read through the correct engine, write plain snapshots, or migrate to Iceberg.</li>
        </ol>''', '“Trino is wrong, ignore it.”') +
    scn('Platform', 'Mid-level', 'Spark fails after the metastore upgrade',
        'After upgrading the metastore to Hive 4, Spark jobs fail with “Invalid method name: get_table”.',
        'do you know client compatibility?',
        '''<ul>
          <li>Spark’s built-in Hive metastore client is too old for the new API.</li>
          <li>Configure spark.sql.hive.metastore.version / jars for a compatible client, or upgrade Spark.</li>
          <li>Test all engines against a restored metastore copy before future upgrades.</li>
        </ul>''', 'Rolling back the metastore without analysis.') +
    scn('Architecture', 'Senior', 'Design a multi-engine lakehouse',
        'Hive, Spark and Trino must share tables safely; some tables are updated daily.',
        'can you choose formats and catalogs?',
        '''<ul>
          <li>Shared, updated tables in Iceberg with one catalog (HMS, REST or Glue) that every engine uses.</li>
          <li>Hive ACID only for Hive-only tables; plain Parquet/ORC for append-only data.</li>
          <li>A compatibility matrix and automated cross-engine tests on every upgrade; Ranger for access in all engines.</li>
        </ul>''', 'Letting each team pick its own format and catalog.')
)
