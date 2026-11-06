import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
BODY = body(HERE)

META = dict(
    module='01-introduction', lesson='03-hive-architecture-and-metastore', n='1.3',
    module_label='Module 1 · Start here: why Hive?',
    title='Hive architecture and the metastore',
    desc='Apache Hive architecture in detail: clients, HiveServer2, Driver, Compiler, Metastore and its database, Tez on YARN and HDFS, the workflow of one query, default ports, embedded vs local vs remote metastore, and how to diagnose an outage. Story-based, with animations, runnable Python and interview scenarios.',
    og_desc='Meet every Hive component, see one query travel through them, and learn the metastore, the memory of your platform.',
    minutes=34, level='Beginner → Advanced',
    lead='Hive is a team of services: HiveServer2 takes your SQL, the compiler plans it with help from the metastore, YARN supplies workers and HDFS holds the files. This lesson draws the full architecture, follows one query through it step by step, opens the metastore’s database, and turns a red dashboard into a two-minute diagnosis.',
    chips=['Architecture diagram', '4 animations', 'Outage diagnosis', 'Runs in your browser (Python)'],
)

SETUP = '''import sqlite3
ms = sqlite3.connect(":memory:")
ms.executescript("""
CREATE TABLE DBS  (DB_ID INT, NAME TEXT);
CREATE TABLE TBLS (TBL_ID INT, DB_ID INT, TBL_NAME TEXT, TBL_TYPE TEXT, SD_ID INT);
CREATE TABLE SDS  (SD_ID INT, LOCATION TEXT);
CREATE TABLE COLUMNS_V2 (SD_ID INT, COLUMN_NAME TEXT, TYPE_NAME TEXT, IDX INT);
CREATE TABLE PARTITIONS (PART_ID INT, TBL_ID INT, PART_NAME TEXT);
INSERT INTO DBS VALUES (1, 'default'), (2, 'sales');
INSERT INTO SDS VALUES (10, 'hdfs://nn1:8020/data/orders'), (11, 'hdfs://nn1:8020/warehouse/sales.db/targets');
INSERT INTO TBLS VALUES (100, 1, 'orders', 'EXTERNAL_TABLE', 10), (101, 2, 'targets', 'MANAGED_TABLE', 11);
INSERT INTO COLUMNS_V2 VALUES (10,'id','int',0),(10,'city','string',1),(10,'amount','int',2),(11,'city','string',0),(11,'target','int',1);
""")
'''
MAIN = SETUP + '''
def describe(db, table):
    row = ms.execute("""SELECT t.TBL_TYPE, s.LOCATION, t.SD_ID FROM TBLS t
                        JOIN SDS s ON s.SD_ID = t.SD_ID JOIN DBS d ON d.DB_ID = t.DB_ID
                        WHERE d.NAME = ? AND t.TBL_NAME = ?""", (db, table)).fetchone()
    if row is None:
        raise SystemExit(f"Table not found: {db}.{table}")
    cols = ms.execute("SELECT COLUMN_NAME, TYPE_NAME FROM COLUMNS_V2 WHERE SD_ID = ? ORDER BY IDX", (row[2],)).fetchall()
    return row[0], row[1], cols

kind, loc, cols = describe("default", "orders")
print("type    :", kind)
print("location:", loc)
print("columns :", cols)
'''
RUN = dict(
    heading='A tiny metastore: the catalogue behind every Hive query',
    intro='<p>This program builds a simplified metastore in SQLite, using table names from the real Hive schema (<code>DBS</code>, <code>TBLS</code>, <code>SDS</code>, <code>COLUMNS_V2</code>, <code>PARTITIONS</code>). The function <code>describe()</code> does what the compiler does at the start of every query: it looks up a table’s type, location and columns. Then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('JOIN SDS s ON s.SD_ID = t.SD_ID', 'The table row points to a <b>storage descriptor</b> (SDS) that holds the location. In the real schema the SDS also holds the file format and SerDe.'),
        ('raise SystemExit("Table not found …")', 'If the table is not in the metastore the compiler stops at once: no cluster is used.'),
        ('ORDER BY IDX', 'Columns are returned in definition order; the schema is applied to files by position.'),
    ],
    tasks=[
        dict(label='1 · Describe a table', hint='Press <b>Run</b>. Then describe <code>("sales", "targets")</code> and compare the table type and location.', code=None),
        dict(label='2 · Add a partition', hint='<b>Predict first:</b> how many partitions does <code>orders</code> have afterwards? Each partition is one row in PARTITIONS. Add a third date and re-run.',
             code=SETUP + '''
ms.executemany("INSERT INTO PARTITIONS VALUES (?, 100, ?)", [(1, "order_date=2026-10-24"), (2, "order_date=2026-10-25")])
for (name,) in ms.execute("SELECT PART_NAME FROM PARTITIONS WHERE TBL_ID = 100 ORDER BY PART_ID"):
    print(name)
print("partitions:", ms.execute("SELECT COUNT(*) FROM PARTITIONS WHERE TBL_ID = 100").fetchone()[0])
'''),
        dict(label='3 · DROP: external vs managed', hint='Predict which location’s files Hive would delete. Only a MANAGED table’s files are removed; an EXTERNAL table loses just its metastore rows.',
             code=SETUP + '''
for name in ("orders", "targets"):
    kind, loc = ms.execute("SELECT TBL_TYPE, LOCATION FROM TBLS t JOIN SDS s ON s.SD_ID = t.SD_ID WHERE TBL_NAME = ?", (name,)).fetchone()
    action = "delete the FILES too" if kind == "MANAGED_TABLE" else "keep the files"
    print(f"DROP TABLE {name}: remove metadata and {action}")
    print("   location:", loc)
'''),
        dict(label='4 · Which tables live under a path?', hint='Find all tables whose location starts with <code>hdfs://nn1:8020/warehouse</code>. This is how admins find what to clean up or back up.',
             code=SETUP + '''
q = "SELECT t.TBL_NAME, s.LOCATION FROM TBLS t JOIN SDS s ON s.SD_ID = t.SD_ID WHERE s.LOCATION LIKE 'hdfs://nn1:8020/warehouse%'"
print(ms.execute(q).fetchall())
'''),
        dict(label='5 · Spot the error', hint='Compilation fails because of a typo in a metastore table name. Read the last line of the error and fix it.', expect='error',
             code=SETUP + '''
print(ms.execute("SELECT * FROM TBLZ").fetchall())
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: look at the architecture on a real machine',
    intro='<p>On a machine that runs Hive, these commands show the components from this lesson. <b>The outputs below are typical examples written for this lesson, not a recording from a particular machine</b>: host names, paths, versions and timestamps will differ.</p>',
    items=[
        dict(title='1 · Are HiveServer2 and the metastore listening?', cmd="ss -ltn | grep -E ':10000|:9083'\njps | grep -i runjar", file='Terminal (Hive node)',
             output='LISTEN 0 50 *:10000 *:*\nLISTEN 0 50 *:9083  *:*\n7421 RunJar\n7650 RunJar',
             note='Two lines for the two services. Both Hive services show up as <code>RunJar</code> in <code>jps</code>, so check the ports, not just the process name.'),
        dict(title='2 · What does the metastore know about my table?', cmd='beeline -u jdbc:hive2://localhost:10000 -e "DESCRIBE FORMATTED orders;"', file='Terminal',
             output='Database:        default\nTable Type:      EXTERNAL_TABLE\nLocation:        hdfs://master1:9000/data/orders\nSerDe Library:   org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe\nInputFormat:     org.apache.hadoop.mapred.TextInputFormat\n... (trimmed)',
             note='Every line comes from the metastore: location, type, SerDe and format. This is the single most useful command for understanding a table.'),
        dict(title='3 · Create the metastore database schema (once)', cmd='schematool -dbType mysql -initSchema', file='Terminal',
             output='Metastore connection URL:  jdbc:mysql://localhost:3306/metastore\nMetastore connection User:  hive\nStarting metastore schema initialization\nInitialization script completed',
             note='This creates the <code>DBS</code>, <code>TBLS</code>, <code>SDS</code> … tables you imitated in the Python above. Run it once for a new metastore database, never on one that already has data.'),
    ],
)

TRACE = dict(
    heading='The compiler’s first job, one line at a time',
    intro='<p>Before planning anything, the compiler checks every name against the metastore. Watch a good query pass and a typo stop early, without ever reaching the cluster.</p>',
    code='''metastore = {"orders": ["id", "city", "amount"]}
def compile_query(table, col):
    cols = metastore.get(table)
    if cols is None:
        return "Table not found"
    if col not in cols:
        return "Invalid column"
    return "plan OK"
print(compile_query("orders", "city"))
print(compile_query("ordres", "city"))
''',
    notes={3: 'Metastore :: Ask the catalogue about the table. This is the metastore call.', 5: 'Stop :: The table is not in the metastore, so compilation ends here with an error. No YARN container is used.', 8: 'Plan :: Names and types are valid, so planning can continue.'},
)

WORKED_INTRO = 'Three tasks from a platform engineer’s week: look up a table’s location, map error messages to components, and see why a huge number of partitions slows down planning. Each runs live and is traced in memory.'
EXAMPLES = [
    dict(level='b', tag='Metastore · lookup', title='Where are my tables stored?',
         problem='<p>The metastore lists these tables with their locations and types. Print the tables whose data Hive would <b>delete</b> if you dropped them (managed tables), with the path.</p>',
         inp='orders EXTERNAL /data/orders · targets MANAGED /warehouse/sales.db/targets · logs EXTERNAL /raw/logs',
         approach=['Keep each table as (name, type, location).', 'Keep only MANAGED tables.', 'Print name and path.'],
         code='''tables = [("orders", "EXTERNAL", "/data/orders"),
          ("targets", "MANAGED", "/warehouse/sales.db/targets"),
          ("logs", "EXTERNAL", "/raw/logs")]
for name, kind, path in tables:
    if kind == "MANAGED":
        print(name, "->", path, "(dropped with the table)")
''', notes={5: 'Check :: Only managed tables own their files.'},
         tryit='Add a managed table “temp_x”. A DROP TABLE on it would remove its folder too; this is why people use EXTERNAL tables for raw data.'),
    dict(level='i', tag='Operations · diagnosis', title='Which component is failing?',
         problem='<p>Map each error message to the Hive component to check first: connection errors → HiveServer2, “not found” → metastore, “ACCEPTED” → YARN, file or permission errors → HDFS. Print the owner for four messages.</p>',
         inp='4 error messages',
         approach=['Write the rules as (keyword, component) pairs.', 'For each message find the first keyword that appears.', 'Print the component.'],
         code='''rules = [("open connection", "HiveServer2 (port 10000)"), ("Table not found", "Metastore (port 9083)"),
         ("ACCEPTED", "YARN queue"), ("Permission denied", "HDFS")]
messages = ["Could not open connection to jdbc:hive2://hs2:10000",
            "SemanticException: Table not found default.orders",
            "application state: ACCEPTED for 900 s",
            "AccessControlException: Permission denied: user=meera"]
for m in messages:
    owner = next(c for k, c in rules if k in m)
    print(f"{owner:26} <- {m[:44]}")
''', notes={6: 'Match :: Find the first rule whose keyword appears in the message.'},
         tryit='Add a rule for “Connection refused: 9083” and a message that uses it. A good runbook is exactly a table like this.'),
    dict(level='a', tag='Performance · metastore load', title='Why do many partitions slow every query?',
         problem='<p>Assume compile time is <b>0.5 s</b> plus <b>0.1 ms</b> for every partition the metastore must describe. A table has 365, 36,500 or 300,000 partitions. Print the compile time of a query that touches the whole table, and of one that touches only 30 partitions. (Illustrative model.)</p>',
         inp='partitions: 365 · 36,500 · 300,000; filtered query: 30 partitions',
         approach=['Compile time = 0.5 + partitions × 0.0001 seconds.', 'Compute for “all partitions” and for “30 partitions”.', 'Print both.'],
         code='''for parts in [365, 36_500, 300_000]:
    full = 0.5 + parts * 0.0001
    pruned = 0.5 + 30 * 0.0001
    print(f"{parts:7} partitions: full scan plan {full:5.1f} s | pruned to 30: {pruned:.2f} s")
''', notes={2: 'Model :: Fixed cost plus a cost per partition fetched from the metastore.'},
         tryit='In real Hive, filtering on the partition column makes the compiler fetch only matching partitions. That is called partition pruning (Module 5).'),
]

QUIZ = mix([
    dict(q='Which Hive component accepts JDBC/ODBC connections from clients?', options=['Metastore', 'HiveServer2', 'NodeManager', 'DataNode'], answer=1,
         why='<b>HiveServer2</b> (port 10000 by default) handles client sessions and runs the Driver for each query.'),
    dict(q='What does the metastore store?', options=['The table data files', 'Metadata: databases, tables, columns, partitions and locations', 'YARN containers', 'Query results'], answer=1,
         why='Metadata lives in the metastore database; the data files live in HDFS or cloud storage.'),
    dict(q='At which step does Hive discover a mistyped table name?', options=['While reading files in a container', 'During compilation, when the compiler checks the metastore', 'After the reducers finish', 'Only when the result is fetched'], answer=1,
         why='Semantic analysis checks names and types against the metastore before any cluster work starts.'),
    dict(q='Users can connect but every query says “Table not found”. Which component should you check first?', options=['HiveServer2 port 10000', 'The metastore and its database', 'The YARN ResourceManager', 'Beeline'], answer=1,
         why='A working connection but failing name resolution points to the metastore (port 9083) or its database.'),
    dict(q='Which metastore deployment is recommended for production, shared by Hive, Spark and Trino?', options=['Embedded with Derby', 'Local inside each HiveServer2', 'Remote: a separate metastore service with a database like MySQL or PostgreSQL', 'No metastore'], answer=2,
         why='A remote metastore is one shared catalogue service; it can be made highly available and is used by all engines.'),
    dict(q='A query stays in ACCEPTED state for a long time. What is most likely?', options=['The metastore is down', 'YARN has no free containers in that queue', 'The table was dropped', 'HiveServer2 crashed'], answer=1,
         why='ACCEPTED means YARN has the application but is waiting for capacity to start it.'),
    dict(q='Where does the execution plan of a modern Hive query run by default?', options=['Inside the metastore', 'On Apache Tez, in YARN containers', 'In the Beeline client', 'On the NameNode'], answer=1,
         why='Hive on Tez is the default engine; MapReduce is deprecated.'),
])

REVISION = [
    'Flow: <b>Client → HiveServer2 (Driver, Compiler) → Metastore → Tez on YARN → HDFS → results back via HiveServer2</b>.',
    '<b>HiveServer2</b>: port 10000 (HTTP 10001, UI 10002). <b>Metastore</b>: port 9083. YARN UI 8088.',
    'The <b>Driver</b> runs inside HiveServer2 and controls each query’s lifecycle.',
    'The <b>compiler</b> parses, then <b>semantic analysis</b> uses the metastore, then plans and optimises (Calcite).',
    'Metastore = service + RDBMS. Stores tables, columns, types, <b>locations</b>, partitions, statistics. <b>Metadata, not data.</b>',
    'Modes: <b>embedded</b> (Derby, one user), <b>local</b>, <b>remote</b> (production, shared with Spark and Trino).',
    'Symptoms: cannot connect → HS2; table not found → metastore; ACCEPTED → YARN; file/permission → HDFS.',
    'Back up the metastore database: losing it loses the table definitions, not the files.',
]
FAQ = [
    ('What is the difference between HiveServer2 and the metastore?', 'HiveServer2 is the query service: it accepts client connections, compiles and runs queries. The metastore is the catalogue service: it stores and returns metadata about databases, tables, columns and partitions. HiveServer2 calls the metastore during compilation; Spark and Trino can call it directly without using HiveServer2.'),
    ('Is the metastore the same as the data warehouse?', 'No. The metastore holds only metadata in a relational database. The warehouse is the data itself: files in HDFS or object storage (managed tables live under the warehouse directory, external tables anywhere).'),
    ('What happens if the metastore database is lost?', 'The files in HDFS remain, but Hive no longer knows which tables exist, their columns, formats or partitions. You would have to restore from a backup, or recreate external tables and repair partitions by hand. That is why the metastore database is backed up and often replicated.'),
    ('Why does Hive need Derby, MySQL or PostgreSQL?', 'The metastore needs a transactional relational database to store its many small metadata rows reliably and query them quickly. Derby is bundled for quick tests; MySQL, PostgreSQL, Oracle or SQL Server are used in real deployments.'),
    ('Where does the Driver run?', 'Inside the HiveServer2 process. It is a logical component that coordinates compile, optimise, execute and fetch for each query, not a separate service you start.'),
]

PRACTICE_INTRO = 'Programs about the metastore, ports, and the path of a query. They are the everyday checks of a Hive administrator.'
PROBLEMS = [
    dict(level='easy', title='Port to service', stmt='Print the Hive service for each port: 10000, 9083, 10002, 8088.', inp='[10000, 9083, 10002, 8088]',
         code='''svc = {10000: "HiveServer2", 9083: "Metastore", 10002: "HiveServer2 web UI", 8088: "YARN ResourceManager UI"}
for p in [10000, 9083, 10002, 8088]:
    print(p, "->", svc[p])
''', explain='Memorise these four. They are the first things checked in any incident.'),
    dict(level='easy', title='Build a JDBC URL', stmt='Build the Beeline URL for host hs2.tiffingo.in, port 10000, database sales.', inp='hs2.tiffingo.in · 10000 · sales',
         code='''host, port, db = "hs2.tiffingo.in", 10000, "sales"
print(f"jdbc:hive2://{host}:{port}/{db}")
''', explain='The pattern is <code>jdbc:hive2://host:port/database</code>.'),
    dict(level='easy', title='Order of the flow', stmt='Put these stages of a query in the right order: Execute on YARN, Parse, Metastore lookup, Fetch results, Optimise.', inp='5 stages shuffled',
         code='''order = ["Parse", "Metastore lookup", "Optimise", "Execute on YARN", "Fetch results"]
for i, s in enumerate(order, 1):
    print(i, s)
''', explain='Parse and semantic analysis (with the metastore) come first, then optimise, then run, then fetch.'),
    dict(level='medium', title='Which component?', stmt='Write a function that returns the component to check for a symptom string, and test four symptoms.', inp='cannot connect · table not found · ACCEPTED · permission denied',
         code='''def check(symptom):
    s = symptom.lower()
    if "connect" in s: return "HiveServer2"
    if "not found" in s and "table" in s: return "Metastore"
    if "accepted" in s: return "YARN"
    return "HDFS"
for sym in ["cannot connect", "Table not found", "stuck in ACCEPTED", "permission denied"]:
    print(sym, "->", check(sym))
''', explain='A tiny runbook as code. Real runbooks add log locations and commands for each component.'),
    dict(level='medium', title='Partition count', stmt='A table is partitioned by date and city. There are 3 years of days (1,095) and 40 cities. How many partitions does the metastore hold?', inp='1,095 days × 40 cities',
         code='print(1095 * 40, "partitions")\n', explain='43,800 partitions in one table. Each is a metastore row, and compile time grows with how many must be fetched. Choose partition columns with moderate cardinality.'),
    dict(level='medium', title='Managed or external?', stmt='Given table types, list which tables lose their data files on DROP.', inp='orders EXTERNAL · targets MANAGED · stage MANAGED',
         code='''types = {"orders": "EXTERNAL", "targets": "MANAGED", "stage": "MANAGED"}
print(sorted(t for t, k in types.items() if k == "MANAGED"))
''', explain='Managed tables are owned by Hive; its DROP removes the files. External tables are only registered.'),
    dict(level='business', title='Metastore capacity check', stmt='A metastore database has 12 GB of disk left and grows 1.5 GB a month. After how many whole months will it be full? Alert at 80% of that space.', inp='12 GB free · 1.5 GB/month',
         code='''free, growth = 12, 1.5
print("full after", int(free // growth), "months")
print("alert after", int(free * 0.8 // growth), "months")
''', explain='8 months until full, and an alert at 6 months. A full metastore database means every query fails at compile time: this is a very real outage.'),
    dict(level='business', title='HiveServer2 sessions', stmt='Each HiveServer2 can handle 80 concurrent sessions comfortably. At month-end 500 analysts connect. How many HiveServer2 instances are needed? Round up.', inp='500 sessions · 80 per instance',
         code='''import math
print(math.ceil(500 / 80), "HiveServer2 instances")
''', explain='7 instances behind a load balancer or ZooKeeper-based discovery. Because sessions are stateful, clients must keep returning to the same instance.'),
]

SCN_INTRO = 'Architecture questions are favourites in Hive and data engineering interviews. Each of these is built from a real situation.'
SCENARIOS = (
    scn('Operations · troubleshooting', 'Fresher', 'Every dashboard failed at 9 a.m.',
        'Users report two errors: “could not open connection” on some tools and “table not found” on others. How do you approach it?',
        'can you map symptoms to components instead of restarting everything?',
        '''<ol>
          <li>Separate the symptoms. “Could not open connection” is the client failing to reach HiveServer2: check that the process is up and that port 10000 is listening.</li>
          <li>“Table not found” with a working connection points to the metastore: check port 9083 and its database (disk space, connections).</li>
          <li>Fix in that order, and confirm with a simple <code>SHOW TABLES</code> and a small <code>SELECT</code>.</li>
        </ol>''', 'restarting every service at once; you lose the evidence and may make it worse.') +
    scn('Any company · concepts', 'Fresher', '“Where is my data: in Hive or in HDFS?”',
        'A colleague asks whether the data of a table is “inside Hive”.',
        'do you separate metadata from data?',
        '''<ul>
          <li>The <b>data</b> is files in HDFS or object storage at the table’s location.</li>
          <li>The <b>metadata</b> (table name, columns, location, format, partitions) is in the metastore database.</li>
          <li>HiveServer2 and the engine are the services that connect the two when a query runs.</li>
        </ul>''', 'saying that Hive stores the data in its own database.') +
    scn('Data platform · design', 'Mid-level', 'Sharing tables with Spark',
        'The data science team wants to use Spark on the same tables analysts query with Hive. How do you set it up?',
        'do you know the metastore is the shared catalogue?',
        '''<ul>
          <li>Run (or use) a remote metastore service and configure Spark’s Hive support to use its URI (<code>hive.metastore.uris</code>).</li>
          <li>Spark then sees the same databases and tables with no redefinition; it reads the same files.</li>
          <li>Plan permissions (Ranger, HDFS ACLs) so both engines respect the same access rules.</li>
        </ul>''', 'copying tables or creating duplicate definitions in Spark.') +
    scn('Operations · reliability', 'Mid-level', 'Metastore high availability',
        'The business wants to avoid a single point of failure in the Hive platform. What would you do for the metastore?',
        'do you understand that the metastore is both a service and a database?',
        '''<ol>
          <li>Run two or more metastore service instances behind a load balancer or a list in <code>hive.metastore.uris</code>.</li>
          <li>Make the metastore database highly available (replication with automatic failover) and back it up regularly, testing restores.</li>
          <li>Monitor disk, connections and slow queries on the database; large partition counts need attention too.</li>
        </ol>''', 'adding metastore instances while leaving a single, unbacked-up database underneath.')
)
