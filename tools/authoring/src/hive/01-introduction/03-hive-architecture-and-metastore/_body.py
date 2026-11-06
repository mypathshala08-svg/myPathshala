import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *


def arch_full():
    """Large architecture diagram (640 x 300) used in the definition."""
    o = ''
    # clients
    o += box(8, 24, 104, 150, 'card') + t(60, 40, 'Clients', 9.4, bold=True)
    for k, s in enumerate(['Beeline', 'BI tools (JDBC/ODBC)', 'Hue / notebooks', 'Python scripts']):
        o += box(16, 50 + k * 28, 88, 22, 'blue') + t(60, 64 + k * 28, s, 7.4, 'blue', bold=True)
    # HiveServer2
    o += box(144, 14, 232, 176, 'acc') + t(260, 30, 'HiveServer2 (port 10000)', 9.6, bold=True)
    o += box(156, 40, 208, 26, 'card') + t(260, 52, 'Session · authentication', 8.2, bold=True) + t(260, 62, 'Thrift server', 7.4, 'ink2')
    o += box(156, 72, 208, 26, 'card') + t(260, 84, 'Driver', 8.2, bold=True) + t(260, 94, 'controls the life of each query', 7.4, 'ink2')
    o += box(156, 104, 208, 46, 'card') + t(260, 116, 'Compiler + Optimizer', 8.2, bold=True) + t(260, 127, 'parse → analyse → plan → optimise', 7.4, 'ink2') + t(260, 138, '(uses Apache Calcite)', 7.4, 'ink2')
    o += box(156, 156, 208, 26, 'card') + t(260, 168, 'Execution plan (DAG of tasks)', 8.2, bold=True) + t(260, 178, 'handed to the execution engine', 7.4, 'ink2')
    # metastore
    o += box(408, 14, 112, 60, 'blue') + t(464, 30, 'Metastore', 9.2, bold=True) + t(464, 43, 'service (port 9083)', 7.6, 'ink2') + t(464, 56, 'table catalogue', 7.6, 'ink2')
    o += cyl(540, 20, 84, 52, 'MySQL /', 'card', 8) + t(582, 58, 'PostgreSQL', 7.6, bold=True)
    # yarn
    o += box(408, 96, 216, 94, 'green') + t(516, 111, 'YARN + Tez (execution engine)', 9, bold=True)
    o += box(418, 120, 96, 20, 'card') + t(466, 133, 'ResourceManager', 7.8, bold=True)
    for k in range(3):
        o += box(418 + k * 70, 148, 62, 34, 'card') + t(449 + k * 70, 160, 'NodeManager', 6.8, bold=True) + fill(424 + k * 70, 166, 22, 10, 'acc', rx=2) + fill(450 + k * 70, 166, 22, 10, 'acc', rx=2)
    # storage
    o += box(144, 214, 480, 74, 'green') + t(384, 230, 'Storage: HDFS or cloud object store (S3, ADLS, GCS)', 9.4, bold=True)
    for k in range(6):
        o += fill(160 + k * 74, 242, 66, 34, 'green' if k % 2 else 'blue', rx=4) + t(193 + k * 74, 257, ['orders', 'customers', 'logs', 'products', 'events', 'payments'][k], 7.8, bold=True, extra=' style="fill:#fff"') + t(193 + k * 74, 269, ['ORC', 'Parquet', 'text', 'ORC', 'Avro', 'ORC'][k], 6.8, extra=' style="fill:#fff"')
    o += box(8, 214, 120, 74, 'violet') + t(68, 232, 'Helpers', 9, bold=True) + t(68, 247, 'ZooKeeper (service', 7.4, 'ink2') + t(68, 258, 'discovery, HA)', 7.4, 'ink2') + t(68, 271, 'Ranger (security)', 7.4, 'ink2')
    # arrows
    o += arrow(114, 100, 142, 100, 'acc', 2) + t(128, 92, '1', 8.6, 'acc', bold=True)
    o += arrow(378, 118, 406, 62, 'blue', 2) + t(400, 98, '2', 8.6, 'blue', bold=True)
    o += arrow(522, 44, 538, 44, 'ink3', 1.6)
    o += arrow(378, 168, 406, 150, 'green', 2) + t(392, 170, '3', 8.6, 'green', bold=True)
    o += arrow(516, 192, 516, 212, 'green', 2) + t(528, 206, '4', 8.6, 'green', bold=True)
    o += arrow(260, 192, 260, 212, 'ink3', 1.6) + t(274, 206, '5', 8.6, 'ink3', bold=True)
    return o


def big_scene():
    return ('<div class="scene"><svg viewBox="0 0 640 300" role="img" aria-label="Hive architecture: clients connect to HiveServer2 which contains the driver and compiler, the compiler consults the metastore backed by a relational database, the plan runs on YARN with Tez, and containers read data files from HDFS or object storage.">'
            + arch_full() + '<text x="632" y="298" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')


# ---------------------------------------------------------------- story
sc = (label_box(14, 20, 120, 60, ['BI dashboard', 'shows: ERROR'], 'red', 9.6) + arrow(138, 50, 172, 50, 'red', 2) +
      label_box(176, 20, 120, 60, ['HiveServer2', 'the waiter'], 'acc', 9.6) + arrow(300, 50, 334, 50, 'ink3', 2) +
      label_box(338, 20, 120, 60, ['Metastore', 'the recipe book'], 'blue', 9.6) + arrow(462, 50, 496, 50, 'ink3', 2) +
      label_box(500, 20, 126, 60, ['YARN + HDFS', 'kitchen + pantry'], 'green', 9.6) +
      t(320, 108, 'Which one of them is not answering?', 10, 'red', bold=True))
scene_svg = scene('A dashboard shows an error. The request travels through HiveServer2, the metastore, YARN and HDFS, and one of them is not answering.', sc,
                  'Hive is a <tspan font-weight="700" class="s-acc">team</tspan>. To debug it, you must know who does what.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>The Tuesday morning when every dashboard turned red</h2>
  <div class="story">
    <p class="narration">At 9:05 on Tuesday, TiffinGo’s sales dashboard shows a red banner: “Could not open connection”. Ten minutes later the finance team’s Excel sheet fails with a different message: “Table not found: orders”. The support channel fills with questions. Kabir, who has been shadowing the platform team for a week, watches Arjun Sir open a terminal but not type anything yet.</p>

{scene_svg}

K> Sir, two different errors from the same Hive. Is Hive broken?
A> Hive is not one program, Kabir. It is a team. Think of a restaurant. <b>HiveServer2</b> is the <b>waiter</b>: it takes your order (the SQL) and brings the plate back. The <b>Driver and Compiler</b> are the <b>head chef</b> who turns the order into a plan. The <b>Metastore</b> is the <b>recipe book and pantry register</b>: it knows which tables exist, their columns and where their files are. <b>YARN</b> hands out the <b>cooks</b> (containers) and <b>HDFS</b> is the <b>pantry</b> where the actual ingredients (files) lie.
R> So “could not open connection” means the waiter is missing?
A> Exactly. And “table not found” while the waiter is fine means the recipe book is not answering. Two symptoms, two different components. Without this map you would restart everything and hope.
K> And how does an order travel between them?
A> That is today’s lesson: the <b>architecture</b> and the <b>workflow</b> of one query, then a close look at the metastore, the most important and most forgotten part of Hive. Let me check port 10000 first. I think I know which one is down.
  </div>
</section>
'''

# ---------------------------------------------------------------- definition
lv = '''
LEVELS> Hive’s architecture at three levels
L1> A restaurant
      <ul>
        <li><b>Customer (client):</b> you, with Beeline or a dashboard.</li>
        <li><b>Waiter (HiveServer2):</b> takes your order, checks you are allowed in, and returns your food.</li>
        <li><b>Head chef (Driver + Compiler):</b> reads the order and writes the cooking plan.</li>
        <li><b>Recipe book and register (Metastore):</b> knows which dishes (tables) exist and in which pantry shelf (folder) the ingredients are.</li>
        <li><b>Cooks (YARN containers, Tez):</b> do the cooking in parallel, close to the ingredients.</li>
        <li><b>Pantry (HDFS / S3):</b> holds the ingredients (files).</li>
      </ul>
L2> What each component does and where it listens
      <ul>
        <li><b>HiveServer2 (HS2):</b> Thrift service for JDBC/ODBC and Beeline, port <b>10000</b> (HTTP mode 10001, web UI 10002). Handles sessions, authentication (Kerberos, LDAP) and runs a <b>Driver</b> for each query.</li>
        <li><b>Compiler:</b> parses HiveQL, checks every table and column against the metastore (<b>semantic analysis</b>), builds a logical plan, optimises it and creates a physical plan: a <b>DAG</b> of tasks.</li>
        <li><b>Metastore (HMS):</b> Thrift service on port <b>9083</b> backed by a relational database (MySQL, PostgreSQL, …). Holds databases, tables, columns, partitions, file formats, locations and statistics.</li>
        <li><b>Execution engine:</b> Tez (default) runs the DAG on <b>YARN</b>; the ResourceManager grants containers, NodeManagers start them.</li>
        <li><b>Storage:</b> the data files in HDFS or cloud object storage, read through a file format and a SerDe.</li>
        <li><b>Helpers:</b> ZooKeeper for finding live HS2 instances, Apache Ranger for permissions, optional LLAP daemons for cached, faster queries.</li>
      </ul>
L3> Design choices, deployment and failure behaviour
      <ul>
        <li><b>Metastore modes:</b> <i>embedded</i> (Derby inside the same JVM; one user only, for learning), <i>local</i> (metastore code inside HS2, external database), <i>remote</i> (separate metastore service, shared by many engines; the production choice).</li>
        <li><b>The metastore is a single point of truth and a possible bottleneck:</b> every query’s compile step calls it. Tens of thousands of partitions in one table make planning slow. Production sites run two or more HMS instances behind a load balancer, with a replicated database.</li>
        <li><b>HS2 is stateful per session</b> (current database, settings, temporary tables); a load balancer needs session stickiness, or clients use ZooKeeper-based discovery.</li>
        <li><b>The Driver is not a separate process;</b> it runs inside HS2. Only the metastore, HS2 and the cluster are separate services you start and monitor.</li>
        <li><b>Authorisation</b> (who may read which table) is usually checked in HS2 using Ranger policies, while <b>HDFS permissions</b> add a second layer under the files.</li>
        <li><b>Failure map:</b> HS2 down → nobody can connect. Metastore down → connections work, queries fail at compile time. YARN full → query waits (ACCEPTED). HDFS or DataNode problem → tasks fail or are slow.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Hive architecture: components and the path of a query</h2>
''' + def_block(
    'The <b>Hive architecture</b> consists of: <b>clients</b> (Beeline, JDBC/ODBC applications) that connect to <b>HiveServer2</b>; the <b>Driver</b>, which controls the lifecycle of a query inside HiveServer2; the <b>Compiler and Optimizer</b>, which parse the HiveQL statement, validate it against the <b>Metastore</b> and produce an optimised execution plan; the <b>Metastore</b>, a service backed by a relational database that stores the metadata of databases, tables, columns, partitions and their storage locations; an <b>execution engine</b> (Apache Tez by default) that runs the plan as a directed acyclic graph of tasks in <b>YARN containers</b>; and the <b>storage layer</b> (HDFS or cloud object storage) where the data files reside in formats such as ORC, Parquet or text.',
    'You send SQL to <b>HiveServer2</b>. Hive checks the table details in the <b>metastore</b>, makes a plan, and asks <b>YARN</b> for workers. The workers read the files from <b>HDFS</b>. The result comes back to you. Metadata lives in the metastore; data lives in the files.') + '''

  <h3>The big picture</h3>
''' + big_scene() + '''
  <p class="muted">Numbers show the order of the main arrows: <b>1</b> client sends SQL · <b>2</b> compiler reads metadata · <b>3</b> plan submitted to YARN · <b>4</b> containers read and write files · <b>5</b> results come back through HiveServer2.</p>

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('HiveServer2', 'The Hive service that accepts client connections (Thrift, JDBC/ODBC) and runs queries. Default port 10000.'),
    ('Driver', 'The part of HiveServer2 that controls one query from compile to fetch.'),
    ('Compiler', 'Turns HiveQL text into an execution plan after checking names and types with the metastore.'),
    ('Metastore (HMS)', 'Service and database that store table definitions: names, columns, types, partitions, locations. Port 9083.'),
    ('DAG', 'Directed acyclic graph: tasks (vertices) connected by data flow (edges), with no cycles. Tez runs one DAG per query.'),
    ('Execution engine', 'Runs the plan on the cluster: Tez (default), MapReduce (deprecated), or Spark.'),
    ('Thrift', 'A cross-language RPC framework. Hive services talk to clients and to each other through it.'),
    ('SerDe', 'Code that reads and writes the bytes of a file as columns. Chosen by the table’s file format.'),
]) + '''

  <h3>Default ports and settings to remember</h3>
''' + table(['Service / setting', 'Default', 'Meaning'], [
    ['HiveServer2 (binary Thrift)', '<code>10000</code>', 'JDBC URL <code>jdbc:hive2://host:10000/default</code>'],
    ['HiveServer2 (HTTP mode)', '<code>10001</code>', 'Used through proxies and gateways (<code>hive.server2.transport.mode=http</code>)'],
    ['HiveServer2 web UI', '<code>10002</code>', 'Sessions, running queries, logs'],
    ['Metastore service', '<code>9083</code>', '<code>hive.metastore.uris = thrift://host:9083</code>'],
    ['Warehouse directory', '<code>/user/hive/warehouse</code>', '<code>hive.metastore.warehouse.dir</code>: where managed tables are stored (distributions may change it)'],
    ['Execution engine', '<code>tez</code>', '<code>hive.execution.engine</code>'],
    ['Metastore database', 'Derby (testing only)', 'Use MySQL or PostgreSQL in any real setup'],
], minw=600) + lv + '''
EXAM> For “Explain Hive architecture with a neat diagram” draw: <b>Clients → HiveServer2 (Driver, Compiler, Optimizer) → Execution engine (Tez on YARN) → HDFS</b>, and a separate <b>Metastore + RDBMS</b> that the compiler consults. Label the numbered flow (submit, get metadata, plan, execute, fetch). Add one line: “Metadata in the metastore, data in HDFS.”
</section>
'''

# ---------------------------------------------------------------- types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Three ways to run the metastore, and what each Hive service does</h2>
''' + cards([
    ('Embedded metastore', 'Metastore code and a Derby database run inside the HiveServer2 JVM. One session at a time. Fine for a first experiment on a laptop; never for sharing.', 'Learning only'),
    ('Local metastore', 'Metastore code runs inside HiveServer2, but the database is separate (for example MySQL). Many sessions work; every HS2 talks to the database directly.', 'Small setups'),
    ('Remote metastore', 'The metastore is its own service on port 9083 in front of the database. HiveServer2, Spark, Trino and others call it. Can run several copies for availability.', 'Production'),
]) + '''

  <h3>Who needs which service?</h3>
''' + table(['If you want to…', 'You need', 'Notes'], [
    ['Run SQL from Beeline or a BI tool', 'HiveServer2 + metastore + YARN + HDFS', 'The full path'],
    ['Query Hive tables from Spark', 'Metastore + HDFS (+ Spark on YARN)', 'HiveServer2 is not needed: Spark reads the catalogue directly'],
    ['Only look up table definitions', 'Metastore', 'Via the Thrift API or its database'],
    ['Run fast, cached interactive queries', 'HiveServer2 + LLAP daemons', 'LLAP is optional; keeps data and code warm in long-lived executors'],
    ['Control who can read which table', 'Ranger (or similar) with HiveServer2', 'Plus HDFS permissions below'],
], minw=560) + '''
  <h3>What the metastore actually stores</h3>
''' + table(['Information', 'Example for table <code>orders</code>', 'Why it matters'], [
    ['Database and table name', '<code>default.orders</code>, owner <code>meera</code>', 'Name resolution; ownership and permissions'],
    ['Columns and types', '<code>id INT, city STRING, amount INT</code>', 'The schema applied on read'],
    ['Location', '<code>hdfs://nn1:8020/data/orders</code>', 'Where the files are'],
    ['File format and SerDe', 'ORC / Parquet / text + SerDe class', 'How to decode the bytes'],
    ['Table type', '<code>EXTERNAL_TABLE</code> or <code>MANAGED_TABLE</code>', 'What DROP does'],
    ['Partitions', '<code>order_date=2026-10-25</code> → its folder', 'Lets queries skip folders (Module 5)'],
    ['Statistics', 'Row counts, min/max, distinct values', 'Lets the optimiser choose better plans'],
], minw=600) + '''
  <h3>Two more components you will read about: HCatalog and WebHCat</h3>
''' + table(['Component', 'What it is', 'Status today'], [
    ['<b>HCatalog</b>', 'A layer over the metastore that lets non-SQL tools (Pig, MapReduce programs) read and write Hive tables by name, without knowing paths or formats. Ships with Hive (<code>hcatalog/</code> folder, <code>hcat</code> command).', 'Still part of Hive 4.2.1. Today Spark, Trino and others usually talk to the metastore directly instead.'],
    ['<b>WebHCat</b> (Templeton)', 'A REST service on top of HCatalog to submit Hive, Pig and MapReduce jobs and read metadata over HTTP (default port 50111).', 'Still shipped (<code>webhcat_server.sh</code> in our image) but rarely deployed; teams use HiveServer2 (JDBC/ODBC), Hue or Knox instead.'],
    ['<b>Hue</b>', 'A web interface (not part of Hive) with a SQL editor that sends queries to HiveServer2.', 'Common on Cloudera and EMR clusters.'],
], minw=640) + '''
TIP> <b>Rule of thumb for outages:</b> “cannot connect” → HiveServer2. “Table or database not found” with a working connection → metastore (or its database). “Query waits” → YARN. “File not found / permission denied” → HDFS.
</section>
'''

# ---------------------------------------------------------------- steps
c1 = '''import sqlite3
ms = sqlite3.connect(":memory:")
ms.executescript("""
CREATE TABLE DBS  (DB_ID INT, NAME TEXT);
CREATE TABLE TBLS (TBL_ID INT, DB_ID INT, TBL_NAME TEXT, TBL_TYPE TEXT, SD_ID INT);
CREATE TABLE SDS  (SD_ID INT, LOCATION TEXT, INPUT_FORMAT TEXT);
CREATE TABLE COLUMNS_V2 (SD_ID INT, COLUMN_NAME TEXT, TYPE_NAME TEXT, IDX INT);
INSERT INTO DBS VALUES (1, 'default');
INSERT INTO SDS VALUES (10, 'hdfs://nn1:8020/data/orders', 'TextInputFormat');
INSERT INTO TBLS VALUES (100, 1, 'orders', 'EXTERNAL_TABLE', 10);
INSERT INTO COLUMNS_V2 VALUES (10,'id','int',0),(10,'city','string',1),(10,'amount','int',2);
""")
q = """SELECT t.TBL_NAME, s.LOCATION FROM TBLS t JOIN SDS s ON t.SD_ID = s.SD_ID
       JOIN DBS d ON d.DB_ID = t.DB_ID WHERE d.NAME = 'default' AND t.TBL_NAME = 'orders'"""
print(ms.execute(q).fetchone())'''
c2 = c1 + '''
print(ms.execute("SELECT COLUMN_NAME, TYPE_NAME FROM COLUMNS_V2 WHERE SD_ID = 10 ORDER BY IDX").fetchall())'''
c3 = '''metastore = {("default", "orders"): {"cols": ["id", "city", "amount"]}}
def compile_query(db, table, cols):
    meta = metastore.get((db, table))
    if meta is None:
        return f"SemanticException: Table not found {db}.{table}"
    bad = [c for c in cols if c not in meta["cols"]]
    return f"Invalid column {bad[0]}" if bad else "plan OK"
print(compile_query("default", "orders", ["city"]))
print(compile_query("default", "orders", ["town"]))
print(compile_query("default", "ordres", ["city"]))'''
c4 = '''plan = ["Map 1: TableScan orders -> Filter -> partial GroupBy",
        "Reducer 2: final GroupBy -> FileSink"]
for i, stage in enumerate(plan, 1):
    print(i, stage)'''
c5 = '''containers = {"Map 1": 16, "Reducer 2": 1}
node_free = 6
for vertex, n in containers.items():
    run_now = min(n, node_free)
    print(f"{vertex}: needs {n}, starts {run_now}, waits {n - run_now}")'''
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>One query, step by step through the architecture</h2>
''' + stepper([
    ('The client sends SQL to HiveServer2',
     code('bash', 'connect.sh', "beeline -u jdbc:hive2://hs2.tiffingo.in:10000/default -n meera"),
     'Beeline opens a Thrift connection on port 10000, authenticates (for example with Kerberos or LDAP) and opens a <b>session</b> that remembers the current database and settings. If port 10000 is closed, you never get past this step.'),
    ('The Driver starts the query; the Compiler asks the metastore',
     code('python', 'mini_metastore.py', c1, run_code(c1)),
     'To compile <code>SELECT … FROM orders</code>, the compiler needs to know what <code>orders</code> is. It calls the metastore, which looks in its database (here a simplified imitation of the real <code>DBS</code>, <code>TBLS</code> and <code>SDS</code> tables) and returns the location.'),
    ('The metastore also returns the columns',
     code('python', 'columns.py', c2, run_code(c2)),
     'Column names and types come back too, so the compiler can check that <code>city</code> exists and that <code>SUM(amount)</code> is valid on an integer. This is the <b>semantic analysis</b> step.'),
    ('Errors appear at compile time, before any cluster work',
     code('python', 'semantic.py', c3, run_code(c3)),
     'A wrong table or column name is caught here in a fraction of a second, without using a single YARN container. Real Hive reports “Table not found” or “Invalid column reference”.'),
    ('The plan is a small graph of stages',
     code('python', 'plan.py', c4, run_code(c4)),
     'After optimisation the plan is a DAG: a map vertex that reads and partially aggregates, and a reducer vertex that finishes. Lesson 1.4 opens this up with <code>EXPLAIN</code>.'),
    ('YARN grants containers; tasks read HDFS',
     code('python', 'containers.py', c5, run_code(c5)),
     'The engine asks the ResourceManager for containers. If the queue has fewer free than needed, some tasks wait their turn. Finished results go back through HiveServer2 to the client.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
def comp(x, y, w, h, title, sub, on, tone='card'):
    return box(x, y, w, h, 'acc' if on else tone) + t(x + w / 2, y + 12, title, 8, bold=True) + (t(x + w / 2, y + 23, sub, 6.8, 'ink2') if sub else '')


def arch_small(active=(), arrows=(), note=''):
    o = ''
    o += comp(6, 96, 66, 50, 'Client', 'Beeline / BI', 'client' in active)
    o += box(86, 14, 130, 130, 'card') + t(151, 26, 'HiveServer2', 8.6, bold=True)
    o += comp(94, 34, 114, 26, 'Session', 'auth, settings', 'session' in active)
    o += comp(94, 64, 114, 26, 'Driver', 'life of the query', 'driver' in active)
    o += comp(94, 94, 114, 26, 'Compiler', 'parse · plan · optimise', 'compiler' in active)
    o += t(151, 136, 'plan = DAG of tasks', 7, 'ink2')
    o += comp(232, 14, 122, 40, 'Metastore', 'catalogue service', 'meta' in active, 'blue')
    o += cyl(262, 60, 62, 30, 'RDBMS', 'acc' if 'db' in active else 'card', 8)
    o += comp(232, 100, 122, 50, 'YARN + Tez', 'RM + containers', 'yarn' in active, 'green')
    o += comp(86, 168, 268, 50, 'HDFS / cloud storage', 'orders files: p0 … p15', 'hdfs' in active, 'green')
    ar = {'c-h': (72, 121, 86, 121), 'h-m': (216, 40, 232, 34), 'm-d': (293, 54, 293, 62), 'h-y': (216, 125, 232, 125), 'y-s': (293, 150, 293, 168), 's-h': (150, 168, 150, 146)}
    for k, (a, b, c, d) in ar.items():
        o += arrow(a, b, c, d, 'acc' if k in arrows else 'ink3', 2.4 if k in arrows else 1.2)
    if note:
        o += t(180, 236, note, 8.6, 'acc', bold=True)
    return o


def term(lines):
    o = '<rect x="14" y="14" width="332" height="196" rx="8" class="s-board"/><text x="26" y="30" font-size="9" class="mono" style="fill:#7F8C86">beeline (illustrative)</text>'
    for k, (txt, col) in enumerate(lines):
        o += f'<text x="26" y="{50 + k * 14}" font-size="8.2" class="mono" style="fill:{col}">{txt}</text>'
    return o
G, W, Y = '#9FD3B8', '#EDEBE3', '#F5C77E'
see = [
    term([('$ beeline -u jdbc:hive2://hs2:10000/default', W), ('Connecting to jdbc:hive2://hs2:10000/default', G)]),
    term([('Connected to: Apache Hive', G), ('0: jdbc:hive2://hs2:10000> SELECT city,', W), ('    SUM(amount) FROM orders GROUP BY city;', W)]),
    term([('SELECT city, SUM(amount) FROM orders …', W), ('INFO : Compiling command(queryId=…)', G), ('INFO : Semantic Analysis Completed', G)]),
    term([('INFO : Semantic Analysis Completed', G), ('INFO : Completed compiling command', G), ('INFO : Executing command(queryId=…)', G)]),
    term([('INFO : Submitting tasks to Tez', G), ('Map 1: 0/16', Y), ('Map 1: 16/16   Reducer 2: 0/1', Y)]),
    term([('Map 1: 16/16   Reducer 2: 1/1', G), ('INFO : Completed executing command', G), ('INFO : Fetching results', G)]),
    term([('+---------+--------+', W), ('| city    | total  |', W), ('| Mumbai  | 450    |', G), ('| Pune    | 560    |', G), ('| Thane   | 240    |', G), ('3 rows selected (21.4 seconds)', Y)]),
]
behind = [
    arch_small({'client', 'session'}, {'c-h'}, '1  Connect: HiveServer2 opens a session'),
    arch_small({'session', 'driver'}, set(), '2  Driver takes the query and starts a lifecycle'),
    arch_small({'compiler', 'meta', 'db'}, {'h-m', 'm-d'}, '3  Compiler asks the metastore for table details'),
    arch_small({'compiler', 'driver'}, set(), '4  Optimised plan (DAG) ready; no cluster used yet'),
    arch_small({'driver', 'yarn'}, {'h-y'}, '5  Plan submitted: YARN grants containers'),
    arch_small({'yarn', 'hdfs'}, {'y-s'}, '6  Tasks read the files from HDFS'),
    arch_small({'driver', 'client'}, {'s-h', 'c-h'}, '7  Results flow back through HiveServer2'),
]
see_caps = ['Meera starts Beeline and points it at HiveServer2, port 10000.',
            'She is connected and types her query.',
            'Hive reports compiling and semantic analysis: names and types are being checked.',
            'Compiling is complete. Only now does Hive begin to use the cluster.',
            'Tez tasks start: first the 16 map tasks, then the reducer.',
            'All tasks complete and Hive fetches the results.',
            'Three rows appear. The whole trip took about 21 seconds (illustrative).']
behind_caps = ['The client connects to HiveServer2. A session is created and the user is authenticated.',
               'The Driver takes the statement and controls everything that happens to it from now on.',
               'The compiler asks the metastore (which reads its relational database) for the table’s location, columns and format.',
               'The optimiser finishes the plan. A typo in a table name would have failed back at step 3, without any cluster use.',
               'The engine submits the DAG to YARN. The ResourceManager grants containers.',
               'Containers run on worker nodes and read the table’s files from HDFS.',
               'Result data is written to a temporary location and streamed back by HiveServer2 to Beeline.']
two = anim_two('Life of a query', 'One query across the architecture', 'The messages Beeline prints during one query', 'Components of Hive lighting up as the query moves through them', see, behind, see_caps, behind_caps)

# ---- scenario 1: diagnosing the outage
def sym(title, line1, line2, tone='red'):
    return (box(20, 14, 320, 62, tone) + t(180, 32, title, 9.2, tone if tone != 'card' else 'ink', bold=True) +
            t(180, 50, line1, 8.2, 'ink', mono=True) + t(180, 64, line2, 8.2, 'ink2', mono=True))
def mini(active, label):
    boxes = [('HS2', 'acc'), ('Metastore', 'blue'), ('YARN', 'green'), ('HDFS', 'green')]
    o = ''
    for k, (nm, tone) in enumerate(boxes):
        x = 20 + k * 84
        bad = nm == active
        o += box(x, 96, 72, 36, 'red' if bad else 'card') + t(x + 36, 118, nm, 8.8, 'red' if bad else 'ink', bold=True)
        if bad:
            o += t(x + 36, 146, '✗ problem here', 7.8, 'red', bold=True)
        if k < 3:
            o += arrow(x + 73, 114, x + 83, 114, 'ink3', 1.2)
    return o
da = sym('Symptom 1', 'Could not open connection to', 'jdbc:hive2://hs2:10000') + mini('HS2', '') + cap('Nobody can connect: check HiveServer2 first.', 'Is the process up? Is port 10000 listening?', 'red', y=158, h=46)
db_ = sym('Symptom 2', 'SemanticException: Table not found', 'default.orders (connection works)') + mini('Metastore', '') + cap('Connected, but names do not resolve: metastore.', 'Is port 9083 answering? Is its database up?', 'red', y=158, h=46)
dc = sym('Symptom 3', 'state: ACCEPTED (for 15 minutes)', 'no progress bar') + mini('YARN', '') + cap('The query is waiting for containers: YARN queue.', 'Look at the ResourceManager UI (port 8088).', 'red', y=158, h=46)
dd = sym('Symptom 4', 'FileNotFoundException / Permission denied', 'hdfs://nn1:8020/data/orders/…') + mini('HDFS', '') + cap('Tasks cannot read the files: HDFS.', 'Check the path, permissions and DataNode health.', 'red', y=158, h=46)
de = (t(180, 24, 'Cheat sheet: symptom → component', 10, 'acc', bold=True) + ''.join(t(26, 46 + k * 17, s, 8.4, anchor='start', mono=True) for k, s in enumerate(['cannot connect          → HiveServer2 :10000', 'table/db not found      → Metastore :9083', 'stuck in ACCEPTED       → YARN queue', 'file / permission error → HDFS'])) + cap('This map turns a red dashboard into a 2-minute check.', '', 'green', y=130, h=34))
s1 = anim_one('Real-time scenario 1', 'Tuesday’s outage: which component is it?',
              'Four different error messages, one per component. Learn to read the symptom and jump straight to the right place.',
              'Reading symptoms', 'Four error symptoms each pointing to a different Hive component: HiveServer2, metastore, YARN and HDFS', [da, db_, dc, dd, de],
              ['The dashboard cannot open a connection to port 10000. That is HiveServer2: is the process running and is the port listening?',
               'The connection works but the table is not found. The metastore (or its database) is not answering, or the table was never created.',
               'The query is accepted but never starts. YARN has no free containers for that queue.',
               'The query starts but tasks fail reading files. Look at HDFS: path, permissions, DataNodes.',
               'Memorise the four pairs. On Tuesday morning Arjun Sir found the metastore’s MySQL database had run out of disk space.'],
              hid='scenario-outage')

# ---- scenario 2: metastore modes
def small(x, y, w, h, l1, l2, tone):
    return label_box(x, y, w, h, [l1, l2] if l2 else [l1], tone, 8.4)
m1 = (small(30, 20, 150, 54, 'HiveServer2', 'with embedded metastore', 'acc') + cyl(220, 28, 70, 38, 'Derby', 'card') + arrow(182, 47, 218, 47, 'ink3', 1.6) +
      t(180, 100, 'One JVM, one user, local files.', 9, 'ink2') + cap('Embedded: great for a first experiment on a laptop.', 'Only one session can use the Derby database.', 'card', y=114, h=46))
m2 = (small(14, 20, 100, 44, 'User 1', 'Beeline', 'blue') + small(126, 20, 100, 44, 'User 2', 'Beeline', 'blue') + small(238, 20, 108, 44, 'Embedded', 'Derby', 'red') +
      arrow(114, 42, 236, 42, 'red', 2) + arrow(226, 42, 236, 42, 'red', 2) + t(180, 90, '“Another instance of Derby may have already booted the database”', 7.8, 'red', bold=True) +
      cap('The second user is refused.', 'Embedded mode cannot be shared.', 'red', y=106, h=46))
m3 = (small(10, 14, 110, 44, 'HiveServer2', 'with local metastore code', 'acc') + small(10, 70, 110, 44, 'HiveServer2 #2', 'local metastore code', 'acc') + cyl(250, 40, 80, 46, 'MySQL', 'card') +
      arrow(122, 36, 248, 56, 'ink3', 1.6) + arrow(122, 92, 248, 74, 'ink3', 1.6) + cap('Local: many sessions, one shared database.', 'But each HS2 carries its own metastore code.', 'blue', y=130, h=46))
m4 = (small(6, 8, 92, 36, 'HiveServer2', '', 'acc') + small(6, 52, 92, 36, 'Spark SQL', '', 'violet') + small(6, 96, 92, 36, 'Trino', '', 'amber') + small(130, 18, 92, 40, 'Metastore #1', 'port 9083', 'blue') + small(130, 72, 92, 40, 'Metastore #2', 'port 9083', 'blue') + cyl(262, 40, 80, 46, 'MySQL', 'card') +
      ''.join(arrow(100, y, 128, 38 if k < 2 else 92, 'ink3', 1.2) for k, y in enumerate((26, 70, 114))) + arrow(224, 38, 260, 56, 'ink3', 1.4) + arrow(224, 92, 260, 72, 'ink3', 1.4) +
      cap('Remote: one catalogue service shared by every engine.', 'Two copies for availability, one replicated database.', 'green', y=142, h=46))
m5 = (t(180, 26, 'Choosing a mode', 10.5, 'acc', bold=True) + ''.join(t(26, 50 + k * 18, s, 8.6, anchor='start') for k, s in enumerate(['Laptop experiment → embedded (Derby)', 'Small shared test cluster → local + MySQL', 'Production, Spark/Trino share tables → remote', 'Always back up the metastore database!'])) + cap('The metastore database is the platform’s memory.', 'Lose it and the tables disappear, though the files remain.', 'red', y=130, h=46))
s2 = anim_one('Real-time scenario 2', 'Embedded, local or remote: why production uses a remote metastore',
              'The same catalogue can be deployed in three ways. See what breaks as more users and engines arrive.',
              'Metastore deployment modes', 'Embedded, local and remote metastore deployments and what each allows', [m1, m2, m3, m4, m5],
              ['Embedded mode runs the metastore and a Derby database inside HiveServer2. It is the quickest way to start on a laptop.',
               'A second user trying to connect is refused because Derby allows one process to open the database.',
               'Local mode puts the database outside (MySQL), so many sessions work, but every HiveServer2 contains metastore code.',
               'Remote mode runs the metastore as a service on port 9083. Hive, Spark and Trino all call it; two copies give high availability.',
               'The metastore’s database is the platform’s memory. If it is lost, the table definitions go with it, even though the data files remain. Back it up.'],
              hid='scenario-modes')

# ---- scenario 3: inside the metastore
r1 = (tall(20, 14, 320, 50, 'You run', ["CREATE EXTERNAL TABLE orders (id INT, city STRING, amount INT)", "LOCATION '/data/orders';"], 'blue', 7.4) +
      t(180, 90, 'Hive does not copy data. It writes a few rows into the metastore database.', 8.8, 'ink2') + cap('Step 1: a CREATE TABLE statement arrives.', '', 'blue', y=130, h=34))
r2 = (tall(10, 12, 100, 62, 'DBS', ['DB_ID  NAME', '1      default'], 'card', 7.4) + tall(120, 12, 230, 62, 'TBLS', ['TBL_ID TBL_NAME TBL_TYPE        SD_ID', '100    orders   EXTERNAL_TABLE  10'], 'acc', 7) +
      tall(10, 84, 130, 56, 'SDS', ['SD_ID LOCATION', '10    /data/orders'], 'green', 7.4) + tall(150, 84, 200, 56, 'COLUMNS_V2', ['id int · city string · amount int'], 'green', 7.4) +
      cap('Step 2: rows in four tables describe the table.', 'Names, type, location and columns. (Simplified.)', 'acc', y=150, h=46))
r3 = (tall(10, 12, 340, 56, 'PARTITIONS  (after adding a partition)', ['PART_ID TBL_ID PART_NAME', '5001    100    order_date=2026-10-25'], 'violet', 7.4) + t(180, 90, 'ALTER TABLE orders ADD PARTITION (order_date=\'2026-10-25\');', 7.6, 'ink2', mono=True) +
      cap('Step 3: each partition is one more row.', 'A year of daily partitions = 365 rows per table.', 'violet', y=110, h=46))
r4 = (tall(10, 12, 340, 56, 'Statistics (after ANALYZE TABLE)', ['rows: 12,000,000 · size: 1.8 GB', 'city: 38 distinct values · amount: min 20, max 1,850'], 'green', 7.4) +
      t(180, 90, 'Used by the optimiser to pick join order and parallelism.', 8.8, 'ink2') + cap('Step 4: statistics help the optimiser plan better.', '', 'green', y=110, h=34))
r5 = (t(180, 24, 'The metastore is small data, but queried constantly', 9.6, 'acc', bold=True) + ''.join(t(24, 48 + k * 17, s, 8.4, anchor='start') for k, s in enumerate(['• Every query compile calls it, often several times.', '• 100,000s of partitions in one table slow planning.', '• Run it on a fast database, with backups and monitoring.', '• Filtering on the partition column lets Hive fetch only matching partitions.'])) +
      cap('Treat the metastore as critical infrastructure.', '', 'red', y=126, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'What does CREATE TABLE really write?',
              'A look inside the metastore’s relational database. Table names follow the real Hive schema (DBS, TBLS, SDS, COLUMNS_V2, PARTITIONS); columns are simplified.',
              'Inside the metastore database', 'Rows written into the metastore database tables when an external table and a partition are created', [r1, r2, r3, r4, r5],
              ['Meera runs CREATE EXTERNAL TABLE. No data file is touched.',
               'The metastore stores a few rows: the database, the table with its type, the storage descriptor with the location and the columns.',
               'Adding a partition adds one row to PARTITIONS, pointing to its own folder.',
               'ANALYZE TABLE stores statistics such as row counts and distinct values, which the optimiser uses.',
               'The metastore holds small data but is asked constantly. Very large partition counts and a slow database are classic reasons for slow query planning.'],
              hid='scenario-inside')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>One query travelling through the architecture</h2>
  <p>Left: what Beeline prints. Right: which Hive component is working at that moment. Follow the glowing boxes and arrows.</p>
''' + two + '''
  <p>Three live scenarios follow: diagnosing a real outage from its symptom, the three metastore deployment modes, and a look inside the metastore’s database.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

# ---------------------------------------------------------------- real-world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Architecture knowledge in daily work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-board"/><text x="26" y="42" font-size="8" class="mono" style="fill:#9FD3B8">:10000 LISTEN</text><text x="26" y="56" font-size="8" class="mono" style="fill:#FF8A80">:9083  ???</text>',
    '1. First 5 minutes of an incident',
    'The on-call engineer checks which ports answer: 10000 (HiveServer2), 9083 (metastore), 8088 (YARN). The first silent port tells them which team to wake up.',
    ['Alert', '*Check ports', 'Right owner']) + '\n' + usecase(
    cyl(34, 20, 52, 34, 'MySQL', 'blue') + t(60, 72, 'nightly backup', 8, 'ink2'),
    '2. Backing up the metastore',
    'Because the metastore database is the platform’s memory, platform teams back it up every night and test restores. The data files may be safe in HDFS, but without the metastore nobody knows what they are.',
    ['Metastore DB', '*Backup', 'Restore test']) + '\n' + usecase(
    '<rect x="16" y="20" width="88" height="50" rx="6" class="s-card2"/>' + t(60, 40, 'Hive · Spark · Trino', 8, bold=True) + t(60, 56, 'one catalogue', 8, 'ink2'),
    '3. One catalogue for many tools',
    'A company adds Spark and Trino. Instead of redefining every table, they point both at the existing remote metastore. Every table is immediately visible, with the same names and locations.',
    ['Remote HMS', '*Spark + Trino', 'No duplicate tables']) + '\n' + usecase(
    '<rect x="16" y="20" width="88" height="50" rx="6" class="s-card2"/>' + t(60, 40, 'Ranger', 9, bold=True) + t(60, 56, 'analyst: SELECT only', 7.8, 'ink2'),
    '4. Who may read what',
    'Security teams define policies such as “marketing may read orders but not customers.phone”. HiveServer2 checks them for every query; HDFS permissions protect the raw files underneath.',
    ['Policy', '*HiveServer2 check', 'Allowed / denied']) + '\n' + usecase(
    '<path d="M20 66h80" class="s-line"/><rect x="26" y="44" width="18" height="22" rx="3" class="s-green"/><rect x="51" y="30" width="18" height="36" rx="3" style="fill:var(--track)"/><rect x="76" y="20" width="18" height="46" rx="3" style="fill:#D64545"/>',
    '5. Slow compile times',
    'A table with 300,000 partitions makes every query spend half a minute in compilation before any task starts, because the metastore returns a huge list. The team reduces partitions and tunes the metastore database.',
    ['Many partitions', '*Slow planning', 'Fewer partitions']) + '''
  <p class="muted">Examples are simplified. Port numbers are Hive defaults; your platform may differ.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> read <a href="../01-prerequisites-sql-hdfs-and-yarn-refresher/">Lesson 1.1</a> (SQL, HDFS blocks, YARN containers) and <a href="../02-what-is-hive/">Lesson 1.2</a> (what Hive is). You should know what a NameNode, a container and a table definition are.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
