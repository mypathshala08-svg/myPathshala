import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep

# ---------------------------------------------------------------- story
sc = (box(10, 10, 620, 128, 'card') + t(22, 26, 'Riya’s laptop · Docker', 9, 'ink2', anchor='start', bold=True) +
      node(24, 52, 112, 50, 'Beeline', 'the SQL client', 'blue') + arrow(138, 77, 176, 77, 'blue', 2) + t(157, 70, ':10000', 7.4, 'blue', bold=True) +
      node(178, 46, 132, 62, 'hiveserver2', 'compiles + runs SQL', 'acc') + t(244, 120, 'web UI :10002', 7.4, 'ink2') +
      arrow(312, 77, 350, 77, 'violet', 2) + t(331, 70, ':9083', 7.4, 'violet', bold=True) +
      node(352, 46, 120, 62, 'metastore', 'table catalogue', 'violet') + arrow(474, 77, 506, 77, 'green', 2) + t(490, 70, ':5432', 7.4, 'green', bold=True) +
      cyl(508, 46, 104, 62, 'Postgres', 'green', 8.6) + t(560, 120, 'hms-db', 7.4, 'ink2'))
scene_svg = scene('Three containers on a laptop: Beeline talks to hiveserver2 on port 10000, which asks the metastore on port 9083, which stores its catalogue in Postgres on port 5432.', sc,
                  'One command starts <tspan font-weight="700" class="s-acc">three containers</tspan>; Beeline is how you talk to them.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Can I run Hive on my 8 GB laptop?”</h2>
  <div class="story">
    <p class="narration">Riya has read four lessons about HiveServer2, the metastore and Tez. Now she wants to type a query and see a real answer, not a diagram. Kabir says TiffinGo’s cluster has hundreds of machines. Riya has one laptop with 8 GB of RAM and Windows.</p>

{scene_svg}

R> Sir, do I need a cluster to practise Hive? I can’t install Hadoop on twenty machines.
A> You need the <b>same pieces</b>, not the same size. HiveServer2, a metastore, a database for the metastore and some storage. Docker can run all of them on your laptop as <b>containers</b>: small isolated boxes, each with one program inside.
K> At TiffinGo the metastore database is Postgres on its own server. Can she copy that?
A> Exactly. With one <code>docker compose up</code> she gets three containers: <b>Postgres</b>, the <b>metastore</b> and <b>HiveServer2</b>. Same ports, same roles as production, just one machine. Tez runs in local mode inside HiveServer2 instead of on YARN.
R> And then I type SQL where?
A> In <b>Beeline</b>, the command-line client. It connects to HiveServer2 with a <b>JDBC URL</b>, the way a browser opens a website with a URL. Today you will install the lab, connect, create your first table over 50,002 TiffinGo orders and even look inside Postgres to see the row Hive wrote about your table.
  </div>
</section>
'''

# ---------------------------------------------------------------- definition
lv = '''
LEVELS> Your Hive lab at three levels
L1> A café with a counter
      <ul>
        <li><b>Beeline</b> is you at the counter, placing an order (a SQL statement).</li>
        <li><b>HiveServer2</b> is the cashier and kitchen: it takes the order, plans it and cooks it.</li>
        <li><b>The metastore</b> is the menu book: what dishes (tables) exist and where the ingredients (files) are kept.</li>
        <li><b>Postgres</b> is the cupboard where the menu book is stored, so it survives the night.</li>
        <li><b>Docker</b> is the building: it lets the whole café open with one key and close without leaving a mess.</li>
      </ul>
L2> What runs where
      <ul>
        <li><b>apache/hive:4.2.1</b> is the official image. One image, two roles, chosen with <code>SERVICE_NAME=metastore</code> or <code>SERVICE_NAME=hiveserver2</code>.</li>
        <li>On first start the metastore container runs <code>schematool</code>, which creates the metastore schema in Postgres (84 tables in our run, schema version 4.2.0).</li>
        <li>HiveServer2 listens on <b>10000</b> (Thrift/JDBC) and serves a web UI on <b>10002</b>. The metastore listens on <b>9083</b>.</li>
        <li>Table data goes to a Docker volume mounted at <code>/opt/hive/data/warehouse</code>; our own files are mounted at <code>/data</code>.</li>
        <li>Beeline connects with <code>jdbc:hive2://localhost:10000/</code>. In Hive 4 the old <code>hive</code> shell command also starts Beeline.</li>
      </ul>
L3> How the lab differs from production
      <ul>
        <li><b>Storage:</b> the lab uses the local file system (<code>file:///</code>); production uses HDFS or object storage (S3, GCS, ADLS). Same SQL, different <code>LOCATION</code> scheme.</li>
        <li><b>Engine:</b> the image sets <code>tez.local.mode=true</code>, so Tez tasks run inside the HiveServer2 JVM. On a cluster the Tez AM and tasks run in YARN containers.</li>
        <li><b>Security:</b> no authentication (any user name works). Production uses LDAP or Kerberos, TLS and Ranger policies (Module 10).</li>
        <li><b>High availability:</b> one of each here; production runs several HiveServer2 and metastore instances registered in ZooKeeper, and the JDBC URL uses <code>serviceDiscoveryMode=zooKeeper</code>.</li>
        <li><b>Metastore mode:</b> our lab is a <b>remote metastore</b> (a separate service on 9083). The single-container quick start uses an <b>embedded Derby</b> database inside HiveServer2: fine for one learner, never for a team.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>A Hive deployment and its client</h2>
''' + def_block(
    'A <b>Hive deployment</b> consists of <b>HiveServer2</b> (the service that accepts, compiles and executes HiveQL from clients over Thrift/JDBC/ODBC), a <b>Hive Metastore</b> service (which stores table and partition metadata in a relational database such as PostgreSQL, MySQL or the embedded Derby), a <b>storage layer</b> for table data (HDFS, object storage or a local file system) and an <b>execution engine</b> (normally Apache Tez on YARN). <b>Beeline</b> is the command-line JDBC client used to connect to HiveServer2 with a URL of the form <code>jdbc:hive2://host:port/database</code>.',
    'To use Hive you need a server that runs your SQL (HiveServer2), a catalogue of tables (the metastore and its database), a place for the files, and a client to type into (Beeline). Docker lets you start all of them on one laptop with one command.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Container', 'A running, isolated copy of an image: one program with everything it needs. Starts in seconds, removed without trace.'),
    ('Image', 'The packaged program a container is started from, for example <code>apache/hive:4.2.1</code>.'),
    ('Docker Compose', 'A YAML file listing several containers, their settings and how they connect; started with <code>docker compose up -d</code>.'),
    ('Port', 'A numbered door on a machine. 10000 = HiveServer2, 10002 = its web UI, 9083 = metastore, 5432 = Postgres.'),
    ('Volume', 'Storage that Docker keeps outside a container, so data survives when the container is recreated.'),
    ('JDBC URL', 'The address a client uses to reach HiveServer2: <code>jdbc:hive2://localhost:10000/default</code>.'),
    ('schematool', 'Hive’s tool that creates or upgrades the metastore tables inside the database.'),
    ('Beeline', 'Hive’s SQL shell. Interactive, or with <code>-e "SQL"</code> and <code>-f file.hql</code> for scripts.'),
]) + '''

  <h3>The ports of your lab</h3>
''' + table(['Port', 'Service', 'Who connects', 'Quick check'], [
    ['<b>10000</b>', 'HiveServer2 (Thrift binary, JDBC)', 'Beeline, DBeaver, Python, BI tools', '<code>beeline -u jdbc:hive2://localhost:10000/</code>'],
    ['<b>10002</b>', 'HiveServer2 web UI', 'You, in a browser', '<code>http://localhost:10002</code>'],
    ['<b>9083</b>', 'Hive Metastore (Thrift)', 'HiveServer2, Spark, Trino', '<code>hive.metastore.uris=thrift://metastore:9083</code>'],
    ['<b>5432</b>', 'PostgreSQL (metastore database)', 'Only the metastore', '<code>psql -U hive -d metastore_db</code>'],
], minw=640) + lv + '''
EXAM> “Name the components needed to run Hive and the default ports.” HiveServer2 (10000, web UI 10002), Hive Metastore (9083) with its RDBMS (Derby embedded, or MySQL/PostgreSQL for production), storage (HDFS/object store) and an execution engine (Tez on YARN). Mention Beeline as the JDBC client and the URL <code>jdbc:hive2://host:10000/db</code>.
</section>
'''

# ---------------------------------------------------------------- types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Ways to run Hive, and ways to connect</h2>
''' + cards([
    ('Single container (quick start)', 'One <code>docker run</code>: HiveServer2 with an embedded Derby metastore. Ready in about 20 seconds. Metadata lives inside the container and is lost when it is removed.', 'Learning · 1 user'),
    ('Docker Compose lab (this course)', 'Postgres + metastore + HiveServer2 as three containers with volumes. Same roles and ports as production; survives restarts.', 'Recommended'),
    ('Linux / WSL tarball', 'Download Hadoop, Tez and Hive, set <code>HADOOP_HOME</code>, edit XML files, run <code>schematool</code>. Teaches every config file; takes an afternoon.', 'Classic'),
    ('Managed cloud', 'Amazon EMR, Google Dataproc, Azure HDInsight or a Cloudera platform start a full cluster with Hive for you. Pay per hour.', 'Work'),
]) + '''

  <h3>Metastore modes</h3>
''' + table(['Mode', 'Where metadata lives', 'Who can share it', 'Use'], [
    ['<b>Embedded</b>', 'Derby database inside the HiveServer2 process', 'Only that one process', 'Quick start, unit tests'],
    ['<b>Local</b>', 'External database (Postgres/MySQL); metastore code runs inside HiveServer2', 'Several HiveServer2s, each with database credentials', 'Small setups (older pattern)'],
    ['<b>Remote</b>', 'External database behind a separate metastore service on 9083', 'Any engine: HiveServer2, Spark, Trino, Impala', 'Production and our lab'],
], minw=620) + '''

  <h3>Clients that talk to HiveServer2</h3>
''' + table(['Client', 'How it connects', 'Typical user'], [
    ['<b>Beeline</b>', 'JDBC, <code>beeline -u jdbc:hive2://…</code>', 'Data engineers, scripts, schedulers'],
    ['<b>DBeaver / DataGrip</b>', 'Hive JDBC driver, same URL', 'Analysts who prefer a GUI'],
    ['<b>BI tools</b> (Power BI, Tableau)', 'ODBC or JDBC driver', 'Dashboards'],
    ['<b>Python</b> (PyHive, JayDeBeApi)', 'Thrift or JDBC from code', 'Data apps, notebooks'],
    ['<b>Hue</b> (web SQL editor)', 'A web app that sends SQL to HiveServer2', 'Analysts on Cloudera/EMR clusters'],
    ['<b><code>hive</code> command</b>', 'In Hive 4 it starts Beeline; the old Hive CLI is gone', 'Old habits and old tutorials'],
], minw=560) + '''

  <h3>Modes of Hive: local mode and cluster mode</h3>
''' + table(['Mode', 'Where tasks run', 'When it is used', 'Setting'], [
    ['<b>Local mode</b>', 'Inside one JVM on one machine (our lab: Tez local mode inside HiveServer2)', 'Small data, learning, tests', '<code>tez.local.mode=true</code>; older docs: <code>mapreduce.framework.name=local</code>'],
    ['<b>Cluster mode</b> (called “MapReduce mode” in older books)', 'Containers on many YARN NodeManagers, data in HDFS', 'Real data volumes, production', 'Tez (or legacy MapReduce) on YARN'],
    ['<b>Automatic local mode</b>', 'Hive decides per query: tiny inputs run locally, big ones on the cluster', 'Speeds up very small queries on a cluster', '<code>hive.exec.mode.local.auto=true</code> (off by default)'],
], minw=640) + '''
WARN> Tutorials written for Hive 1 and 2 use the old <code>hive</code> shell that talked to the metastore directly, skipping HiveServer2. In Hive 4 that shell is removed: <code>hive</code> starts Beeline, and <code>hive -e "SQL"</code> without a URL fails with <code>Cannot run commands specified using -e. No current connection</code>. Always use <code>beeline -u …</code>.
</section>
'''

# ---------------------------------------------------------------- steps
COMPOSE = open(os.path.join(HERE, '..', '..', 'lab', 'docker-compose.yml')).read().strip()
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Install the lab and run your first query</h2>
  <p>Every output below was recorded from a real run of Hive 4.2.1 on 26 October 2026. Your times and container ids will differ.</p>
''' + stepper([
    ('Step 1 · Install Docker',
     '<p>Windows or macOS: install <b>Docker Desktop</b> (on Windows it uses WSL 2). Linux: install Docker Engine and the compose plugin. Then check (your versions may be newer):</p>' +
     code('bash', 'Terminal', 'docker --version\ndocker compose version', 'Docker version 29.9.2, build a82e528\nDocker Compose version v5.6.1'),
     'Give Docker at least <b>4 GB of RAM</b> (Settings → Resources). Our three containers used about 1.6 GB together when idle: HiveServer2 1.17 GB, metastore 348 MB, Postgres 102 MB.'),
    ('Step 2 · Get the files',
     '<p>Make a folder <code>hive-lab</code> with three things: the compose file below, the Postgres JDBC driver <code>postgresql-42.7.4.jar</code> (from Maven Central) and a <code>data</code> folder for your CSV files.</p>' +
     code('yaml', 'docker-compose.yml', COMPOSE),
     'One image, <code>apache/hive:4.2.1</code>, is used twice: <code>SERVICE_NAME</code> decides whether the container becomes the metastore or HiveServer2. <code>IS_RESUME: "true"</code> tells HiveServer2 not to initialise a schema itself.'),
    ('Step 3 · Start the three containers',
     code('bash', 'Terminal', 'docker compose -p hivelab up -d\ndocker compose -p hivelab ps', open(CAP + 'compose_ps.txt').read().rstrip()),
     'On the first start the metastore container runs <code>schematool -initOrUpgradeSchema</code> against Postgres. HiveServer2 accepts connections after roughly 20–60 seconds; before that you get <code>Connection refused</code>.'),
    ('Step 4 · Connect with Beeline',
     code('bash', 'Terminal', 'docker exec -it hiveserver2 beeline -u jdbc:hive2://localhost:10000/ -n hive',
          'Connecting to jdbc:hive2://localhost:10000/\nConnected to: Apache Hive (version 4.2.1)\nDriver: Hive JDBC (version 4.2.1)\nTransaction isolation: TRANSACTION_REPEATABLE_READ\nBeeline version 4.2.1 by Apache Hive\n0: jdbc:hive2://localhost:10000/>'),
     'Beeline runs inside the hiveserver2 container here, so <code>localhost</code> is correct. The prompt <code>0: jdbc:hive2://…&gt;</code> shows the connection number and URL. <code>-n hive</code> is the user name; the lab has no password.'),
    ('Step 5 · Describe 50,002 orders as a table',
     code('sql', 'Beeline', "CREATE EXTERNAL TABLE orders_raw (\n  order_id INT, customer_id INT, restaurant_id INT, city STRING,\n  order_ts TIMESTAMP, amount INT, payment STRING, status STRING)\nROW FORMAT DELIMITED FIELDS TERMINATED BY ','\nLOCATION 'file:///data/tiffingo/orders';\nSHOW TABLES;",
          '+-------------+\n|  tab_name   |\n+-------------+\n| orders_raw  |\n+-------------+'),
     'Copy <code>orders.csv</code> into <code>data/tiffingo/orders/</code> first. No data is copied by CREATE: Hive only records the columns, the delimiter and the folder in the metastore. <code>file:///</code> means the container’s own disk; on a cluster you would write an HDFS or S3 path.'),
    ('Step 6 · Ask a real question',
     code('sql', 'Beeline', "SELECT city, COUNT(*) AS orders FROM orders_raw\nWHERE city IN ('Pune','Thane') GROUP BY city ORDER BY city;",
          '+--------+---------+\n|  city  | orders  |\n+--------+---------+\n| Pune   | 7931    |\n| Thane  | 4820    |\n+--------+---------+\n2 rows selected (1.573 seconds)'),
     'This query runs a Tez DAG (Map 1 → Reducer 2 → Reducer 3) in local mode. The Tez counters printed in the log show <code>RECORDS_IN_Map_1: 50002</code>: every row was read, then filtered.'),
    ('Step 7 · Look behind the screen: the metastore row',
     code('bash', 'Terminal', 'docker exec hms-db psql -U hive -d metastore_db \\\n  -c \'SELECT "TBL_ID","TBL_NAME","TBL_TYPE","OWNER" FROM "TBLS";\'',
          ' TBL_ID |  TBL_NAME  |    TBL_TYPE    | OWNER \n--------+------------+----------------+-------\n      1 | orders_raw | EXTERNAL_TABLE | hive\n(1 row)'),
     'Your <code>CREATE TABLE</code> became one row in the Postgres table <code>TBLS</code> (plus rows in <code>SDS</code> for the location and <code>COLUMNS_V2</code> for the columns). Only look here to learn: never edit metastore tables by hand.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
def stack(on_db=False, on_ms=False, on_hs2=False, on_bl=False, flow=None, note=''):
    o = (node(14, 150, 76, 44, 'Postgres', ':5432', 'green', on_db) + node(102, 150, 76, 44, 'metastore', ':9083', 'violet', on_ms) +
         node(190, 150, 80, 44, 'hiveserver2', ':10000', 'acc', on_hs2, 8) + node(282, 150, 66, 44, 'Beeline', 'client', 'blue', on_bl))
    for x1, x2, col in (flow or []):
        o += arrow(x1, 172, x2, 172, col, 2.2)
    if note:
        o += t(180, 218, note, 8.4, 'ink2')
    return o

def flow(a, b, col):
    return (a, b, col)

see = [
    term([('$ docker compose -p hivelab up -d', W), ('Container hms-db       Started', G), ('Container metastore    Started', G), ('Container hiveserver2  Started', G)]),
    term([('$ docker logs metastore', W), ('schematool -dbType postgres', W), ('  -initOrUpgradeSchema', W), ('Initialized Hive Metastore Server', G), ('schema successfully..', G)]),
    term([('$ docker logs hiveserver2', W), ('Starting HiveServer2. PID is: 1', G), ('Starting Web UI on port 10002', G), ('Started HttpServer[hiveserver2]', G), ('  on port 10002', G)]),
    term([('$ beeline -u jdbc:hive2://localhost:10000/', W), ('Connected to: Apache Hive (version 4.2.1)', G), ('Driver: Hive JDBC (version 4.2.1)', G), ('0: jdbc:hive2://localhost:10000/>', Y)]),
    term([('> CREATE EXTERNAL TABLE orders_raw (…)', W), ("> LOCATION 'file:///data/tiffingo/orders';", W), ('No rows affected', G), ('> SHOW TABLES;', W), ('| orders_raw  |', G)]),
    term([('> SELECT city, COUNT(*) AS orders …', W), ('RECORDS_IN_Map_1: 50002', G), ('| Pune   | 7931    |', G), ('| Thane  | 4820    |', G), ('2 rows selected (1.573 seconds)', Y)]),
    term([('$ psql … SELECT … FROM "TBLS";', W), (' TBL_ID |  TBL_NAME  |    TBL_TYPE', W), ('      1 | orders_raw | EXTERNAL_TABLE', G), ('(1 row)', G)]),
]
B1 = [
    t(180, 24, 'Docker starts three containers', 9.4, bold=True) + t(180, 44, 'Start order follows depends_on', 8.4, 'ink2') + stack(True, True, True, False, note='All three are running, but not yet ready'),
    t(180, 24, 'schematool builds the catalogue', 9.4, bold=True) + box(30, 40, 300, 92, 'green') + t(180, 58, 'In Postgres: metastore_db', 8.8, bold=True) +
    ''.join(t(48 + (k % 4) * 72, 78 + (k // 4) * 16, nm, 7.4, 'ink2', anchor='start', mono=True) for k, nm in enumerate(['DBS', 'TBLS', 'SDS', 'COLUMNS_V2', 'PARTITIONS', 'VERSION', 'TXNS', '… 84 tables'])) +
    stack(True, True, False, False, [flow(100, 92, 'green')], 'Schema version 4.2.0 recorded in VERSION'),
    t(180, 24, 'HiveServer2 opens its doors', 9.4, bold=True) + box(40, 44, 280, 70, 'acc') + t(180, 62, 'port 10000: JDBC / Thrift clients', 8.6, bold=True) + t(180, 80, 'port 10002: web UI', 8.6, bold=True) + t(180, 100, 'connects to thrift://metastore:9083', 8, 'ink2', mono=True) +
    stack(True, True, True, False, [flow(188, 180, 'violet')], 'Ready after about 20–60 s'),
    t(180, 24, 'Beeline opens a JDBC session', 9.4, bold=True) + box(30, 44, 300, 70, 'blue') + t(180, 62, 'jdbc:hive2://localhost:10000/', 8.8, bold=True, mono=True) + t(180, 82, 'protocol · host · port · database', 8, 'ink2') + t(180, 100, 'HiveServer2 creates a session for user “hive”', 8, 'ink2') +
    stack(True, True, True, True, [flow(280, 272, 'blue')], 'One session per connection'),
    t(180, 24, 'CREATE TABLE writes metadata only', 9.4, bold=True) + box(20, 40, 150, 86, 'violet') + t(95, 56, 'metastore → Postgres', 8.2, bold=True) + t(28, 74, 'TBLS: orders_raw', 7.6, 'ink2', anchor='start', mono=True) + t(28, 88, 'SDS: file:/data/…', 7.6, 'ink2', anchor='start', mono=True) + t(28, 102, 'COLUMNS_V2: 8 cols', 7.6, 'ink2', anchor='start', mono=True) +
    box(190, 40, 150, 86, 'card') + t(265, 56, '/data/tiffingo/orders', 8, bold=True, mono=True) + t(265, 80, 'orders.csv · 3 MB', 8, 'ink2') + t(265, 100, 'untouched', 8.4, 'green', bold=True) +
    stack(True, True, True, True, [flow(188, 180, 'violet'), flow(100, 92, 'green')], 'The data files are not read or copied'),
    t(180, 24, 'SELECT runs a Tez DAG (local mode)', 9.4, bold=True) + label_box(14, 44, 100, 36, ['Map 1', 'read 50,002 rows'], 'acc', 8) + label_box(130, 44, 100, 36, ['Reducer 2', 'count per city'], 'blue', 8) + label_box(246, 44, 100, 36, ['Reducer 3', 'sort by city'], 'violet', 8) +
    arrow(116, 62, 128, 62) + arrow(232, 62, 244, 62) + t(180, 104, 'Tez runs inside the hiveserver2 JVM in this lab;', 8, 'ink2') + t(180, 118, 'on a cluster the tasks run in YARN containers', 8, 'ink2') +
    stack(True, True, True, True, [flow(280, 272, 'blue')], 'Rows return to Beeline through the same session'),
    t(180, 24, 'Your table, as Postgres sees it', 9.4, bold=True) + box(20, 44, 320, 64, 'green') + t(30, 64, 'TBL_ID  TBL_NAME    TBL_TYPE', 8, 'ink', anchor='start', mono=True) + t(30, 82, '1       orders_raw  EXTERNAL_TABLE', 8, 'green', anchor='start', mono=True) + t(180, 128, 'Hive’s catalogue is just rows in a database', 8.6, 'ink2') +
    stack(True, False, False, False, note='Never edit these rows by hand: use Hive DDL'),
]
see_caps = ['Riya starts the lab. Docker reports three containers started.',
            'The metastore container’s log shows schematool creating the metastore schema in Postgres.',
            'HiveServer2 logs that it has started and opened the web UI on 10002.',
            'Beeline connects. The prompt shows connection 0 and the JDBC URL.',
            'She creates an external table over the order folder. It returns at once.',
            'Her first query counts orders for Pune and Thane: 7,931 and 4,820, from 50,002 rows read.',
            'In Postgres she finds the row Hive wrote for her table.']
behind_caps = ['Docker starts Postgres, then the metastore, then HiveServer2 (depends_on). Running is not the same as ready.',
               'schematool connects to Postgres and creates the metastore tables (84 in this run) and records schema version 4.2.0.',
               'HiveServer2 binds port 10000 for clients and 10002 for the web UI, and connects to the metastore on 9083.',
               'Beeline opens a JDBC session: protocol hive2, host localhost, port 10000, database default.',
               'CREATE EXTERNAL TABLE adds rows in TBLS, SDS and COLUMNS_V2 through the metastore. The CSV file is not touched.',
               'SELECT is compiled into a Tez DAG of three vertices that runs in local mode inside HiveServer2.',
               'The catalogue is ordinary rows in Postgres. This is why the metastore database must be backed up.']
two = anim_two('Lab start-up', 'From docker compose up to your first answer', 'Terminal output while the lab starts and the first query runs', 'Containers, ports and the metastore database as each step happens', see, B1, see_caps, behind_caps)

# ---- scenario 1: embedded Derby vs remote metastore
d1 = (t(180, 22, 'Quick start: one container', 9.6, bold=True) + box(60, 40, 240, 90, 'acc') + t(180, 56, 'hive4 container', 8.6, bold=True) +
      node(76, 66, 96, 50, 'HiveServer2', ':10000', 'acc') + cyl(196, 64, 88, 54, 'Derby', 'green', 8.4) + t(180, 150, 'docker run … SERVICE_NAME=hiveserver2', 8, 'ink2', mono=True) +
      cap('Metastore and its database live inside HiveServer2.', 'Ready in about 20 s, 412 MB of RAM.', 'card', y=168, h=46))
d2 = (t(180, 22, 'Spark wants the same tables', 9.6, bold=True) + box(60, 40, 170, 90, 'acc') + node(72, 66, 70, 50, 'HS2', '', 'acc') + cyl(150, 64, 70, 54, 'Derby', 'green', 8) +
      node(262, 66, 84, 50, 'Spark', 'job', 'blue') + arrow(260, 91, 224, 91, 'red', 2) + t(300, 140, 'no door to knock on', 8, 'red', bold=True) +
      cap('Embedded Derby has no network port.', 'Other engines cannot share the catalogue.', 'red', y=168, h=46))
d3 = (t(180, 22, 'Container removed = catalogue gone', 9.6, 'red', bold=True) + box(60, 40, 240, 90, 'card') + t(180, 80, 'docker rm -f hive4', 9, 'ink', mono=True) + t(180, 104, 'tables, columns, locations: deleted', 8.4, 'red', bold=True) +
      cap('Metadata inside a container dies with it.', 'Files in a mounted folder survive; the table definitions do not.', 'red', y=168, h=46))
d4 = (t(180, 22, 'Remote metastore: the lab and production', 9.6, 'green', bold=True) + node(14, 52, 70, 46, 'HS2', ':10000', 'acc') + node(14, 108, 70, 40, 'Spark', '', 'blue') +
      arrow(86, 75, 136, 92, 'violet', 2) + arrow(86, 128, 136, 100, 'violet', 2) + node(138, 72, 92, 50, 'metastore', ':9083', 'violet') + arrow(232, 97, 262, 97, 'green', 2) + cyl(264, 70, 82, 54, 'Postgres', 'green', 8.4) +
      cap('Many engines, one catalogue.', 'Postgres lives in a volume and is backed up.', 'green', y=168, h=46))
d5 = (t(180, 22, 'Rule of thumb', 9.6, 'acc', bold=True) + ''.join(t(26, 50 + k * 20, s, 8.6, anchor='start') for k, s in enumerate(['Learning alone for an hour → single container', 'Following this course → compose lab (remote)', 'Team or production → remote metastore, HA,', '   backed-up RDBMS (Postgres or MySQL)'])) +
      cap('Derby is for tests, never for shared work.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Embedded Derby or a remote metastore?',
              'The quick-start container is tempting. See what happens when a second engine needs the tables, or when the container is removed.',
              'Metastore modes', 'An embedded Derby metastore inside one container compared with a remote metastore shared by HiveServer2 and Spark', [d1, d2, d3, d4, d5],
              ['The single-container quick start runs HiveServer2 with an embedded Derby database inside it.',
               'A Spark job cannot reach that catalogue: embedded Derby has no service port to connect to.',
               'Removing the container deletes the metastore with it. Data files in a mounted folder survive, but every table definition is lost.',
               'A remote metastore on port 9083 with Postgres behind it is shared by HiveServer2, Spark and other engines.',
               'Use the single container only for quick experiments; use a remote metastore for the course and for real work.'],
              hid='scenario-metastore')

# ---- scenario 2: JDBC URL anatomy + connection errors
u1 = (t(180, 22, 'Anatomy of a JDBC URL', 9.6, bold=True) + t(180, 58, 'jdbc:hive2://localhost:10000/tiffingo;ssl=true', 9.4, 'ink', mono=True, bold=True) +
      chip(22, 70, 'driver', 'blue', 50, 16) + chip(110, 70, 'host', 'acc', 46, 16) + chip(178, 70, 'port', 'violet', 40, 16) + chip(226, 70, 'database', 'green', 56, 16) + chip(290, 70, 'options', 'amber', 52, 16) +
      t(180, 112, 'Read it like a postal address: who, where, which door, which room.', 8.4, 'ink2') + cap('Every client uses the same URL format.', 'Beeline, DBeaver, Python, Power BI.', 'card', y=150, h=46))
u2 = (term([('$ beeline -u jdbc:hive2://localhost:10001/', W), ('WARN jdbc.HiveConnection: Failed to', RD), ('  connect to localhost:10001', RD), ('Could not open client transport …', RD), ('java.net.ConnectException:', RD), ('  Connection refused (state=08S01)', RD)]))
u3 = (t(180, 22, '“Connection refused” checklist', 9.6, 'red', bold=True) + ''.join(t(24, 48 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['1. Port: 10000 for JDBC, not 10002 (web UI)', '2. Is the container up?  docker compose ps', '3. Is it ready yet?  wait 20–60 s, read the log', '4. From your PC use the published port;', '   inside Docker use the service name (hiveserver2)'])) +
      cap('Refused = nobody listening on that host and port.', '', 'red', y=150, h=34))
u4 = (t(180, 22, 'localhost depends on where you stand', 9.6, bold=True) + box(14, 40, 160, 100, 'card') + t(94, 56, 'Your PC', 8.6, bold=True) + t(94, 78, 'localhost:10000', 8, 'ink2', mono=True) + t(94, 92, '→ published port', 8, 'ink2') +
      box(186, 40, 160, 100, 'acc') + t(266, 56, 'Inside the Docker network', 8.6, bold=True) + t(266, 78, 'hiveserver2:10000', 8, 'ink2', mono=True) + t(266, 92, 'metastore:9083', 8, 'ink2', mono=True) +
      cap('Containers find each other by service name.', 'That is why HiveServer2 uses thrift://metastore:9083.', 'blue', y=150, h=46))
u5 = (term([('$ beeline -u jdbc:hive2://localhost:10000/ -n hive', W), ('Connected to: Apache Hive (version 4.2.1)', G), ('0: jdbc:hive2://localhost:10000/> !tables', Y), ('| TABLE_SCHEM | TABLE_NAME | TABLE_TYPE …', W), ('| default     | orders_raw | TABLE      …', G), ('0: jdbc:hive2://localhost:10000/> !quit', Y)], label='terminal · real output (columns trimmed)'))
s2 = anim_one('Real-time scenario 2', 'JDBC URLs and “Connection refused”',
              'Most first-day problems are connection problems. Read the URL, then fix the most common error.',
              'Connecting', 'The parts of a Hive JDBC URL, a real Connection refused error, a checklist and a successful connection', [u1, u2, u3, u4, u5],
              ['A JDBC URL names the driver (hive2), the host, the port, the database and optional settings after semicolons.',
               'A real error from our lab: port 10001 has no listener, so the connection is refused.',
               'Check the port, whether the container is running, whether HiveServer2 has finished starting, and which host name applies.',
               'On your PC, localhost reaches the published port. Containers reach each other by service name.',
               'With the right URL Beeline connects. Commands that start with ! (like !tables and !quit) are Beeline’s own, not SQL.'],
              hid='scenario-jdbc')

# ---- scenario 3: Beeline for scripts
F = open(CAP + 'formats.txt').read()
b1 = term([('$ beeline -u … -e "SELECT city, COUNT(*) …"', W), ('+--------+---------+', G), ('|  city  | orders  |', G), ('+--------+---------+', G), ('| Pune   | 7931    |', G), ('| Thane  | 4820    |', G), ('+--------+---------+', G)], label='--outputformat=table (default)')
b2 = term([('$ beeline … --silent=true --outputformat=csv2 -e …', W), ('city,orders', G), ('Pune,7931', G), ('Thane,4820', G), ('', W), ('→ redirect to a file:  … > report.csv', Y)], label='--outputformat=csv2')
b3 = term([('--outputformat=tsv2', W), ('city    orders', G), ('Pune    7931', G), ('--outputformat=vertical', W), ('city    Pune', G), ('orders  7931', G), ('--outputformat=json', W), ('{"resultset":[{"city":"Pune",…', G)], label='other formats (real output)', step=13.5)
b4 = (t(180, 22, 'Scripts: -f file.hql', 9.6, bold=True) + box(20, 40, 150, 92, 'card') + t(95, 56, 'daily_report.hql', 8.4, bold=True, mono=True) + t(30, 76, 'USE tiffingo;', 7.6, 'ink2', anchor='start', mono=True) + t(30, 90, 'SELECT …;', 7.6, 'ink2', anchor='start', mono=True) + t(30, 104, 'INSERT …;', 7.6, 'ink2', anchor='start', mono=True) +
      arrow(172, 86, 196, 86) + box(198, 40, 142, 92, 'acc') + t(269, 60, 'beeline -u … -f', 8.4, bold=True, mono=True) + t(269, 80, 'runs each statement', 8, 'ink2') + t(269, 96, 'stops at first error', 8, 'red', bold=True) +
      cap('Schedulers (Airflow, cron) call Beeline this way.', 'The exit code tells them if it failed.', 'blue', y=150, h=46))
b5 = (t(180, 22, 'Pick the right switch', 9.6, 'acc', bold=True) + ''.join(t(24, 46 + k * 18, s, 8.4, anchor='start', mono=True) for k, s in enumerate(['-u URL -n user    connect', '-e "SQL"         one statement', '-f file.hql      a script', '--silent=true     hide INFO logs', '--outputformat=csv2   clean CSV', '--hivevar d=2026-10-31  variables'])) +
      cap('Beeline is a tool, not just a prompt.', '', 'green', y=160, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Beeline in scripts: output formats and files',
              'Analysts read the table format; programs need CSV or JSON. These outputs are from the lab.',
              'Beeline switches', 'Beeline output in table, csv2, tsv2, vertical and json formats, and running a script file', [b1, b2, b3, b4, b5],
              ['The default table format is easy to read but awkward for programs.',
               'With --silent=true and --outputformat=csv2 the output is clean CSV that can be redirected to a file.',
               'tsv2, vertical and json are also available. vertical is handy for wide rows.',
               'beeline -f runs a whole .hql script; schedulers use the exit code to detect failures.',
               'Remember the six switches: -u, -n, -e, -f, --silent and --outputformat, plus --hivevar for variables.'],
              hid='scenario-beeline')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Lab start-up: seven frames from <code>up -d</code> to a result</h2>
  <p>Left: the real terminal output. Right: which container is doing the work, and what changes in the metastore database.</p>
''' + two + '''
  <p>Three live scenarios follow: choosing a metastore mode, fixing connection errors, and using Beeline in scripts.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

# ---------------------------------------------------------------- real-world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Where a laptop lab and Beeline show up at work</h2>
''' + usecase(
    '<rect x="16" y="18" width="88" height="54" rx="6" class="s-card2"/>' + ''.join(fill(24 + k * 26, 30, 20, 30, c, rx=3) for k, c in enumerate(['green', 'violet', 'acc'])),
    '1. A safe place to try things',
    'Before running a risky <code>ALTER TABLE</code> or a new partition scheme on the shared cluster, engineers try it in a local Docker lab with a small copy of the data. Breaking a laptop lab costs nothing.',
    ['Idea', '*Local lab', 'Shared cluster']) + '\n' + usecase(
    '<rect x="16" y="20" width="88" height="50" rx="6" class="s-board"/><text x="24" y="40" font-size="8" class="mono" style="fill:#9FD3B8">test_report.hql</text><text x="24" y="56" font-size="8" class="mono" style="fill:#F5C77E">PASS 12/12</text>',
    '2. Testing SQL in CI',
    'A team keeps its HiveQL in Git. On every pull request the CI pipeline starts the Hive containers, runs each script with <code>beeline -f</code> on sample data and compares the output with expected results.',
    ['Pull request', '*Hive in Docker', 'Merge']) + '\n' + usecase(
    '<rect x="16" y="22" width="40" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/><path d="M60 45h20" class="s-line"/><rect x="82" y="22" width="24" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>',
    '3. BI tools on Hive',
    'A dashboard in a BI tool connects to HiveServer2 with the Hive ODBC/JDBC driver and the same host and port 10000. For interactive dashboards, teams often add a faster engine reading the same metastore.',
    ['Dashboard', '*JDBC/ODBC :10000', 'HiveServer2']) + '\n' + usecase(
    '<rect x="16" y="20" width="88" height="50" rx="6" class="s-board"/><text x="24" y="40" font-size="8" class="mono" style="fill:#9FD3B8">beeline -f daily.hql</text><text x="24" y="56" font-size="8" class="mono" style="fill:#F5C77E">exit code 0</text>',
    '4. Scheduled jobs',
    'Airflow or cron runs <code>beeline -u … --hivevar run_date=2026-10-31 -f daily.hql</code> every night. If a statement fails, Beeline exits with a non-zero code and the scheduler marks the task failed and retries or alerts.',
    ['Scheduler', '*beeline -f', 'Alert on failure']) + '\n' + usecase(
    '<rect x="16" y="20" width="88" height="50" rx="6" class="s-card2"/>' + t(60, 38, ':10002', 9, 'acc', bold=True, mono=True) + t(60, 56, 'open sessions · queries', 7, 'ink2'),
    '5. Who is running what?',
    'The HiveServer2 web UI on port 10002 lists open sessions, running and recent queries and their elapsed time. Support engineers use it to find the query that is slowing everyone down.',
    ['Slow cluster', '*Web UI :10002', 'Talk to the owner']) + '''
  <p class="muted">Examples are simplified. Company setups differ.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> you should know what HiveServer2 and the metastore do (<a href="../03-hive-architecture-and-metastore/">Lesson 1.3</a>). You will type a few terminal commands; <code>cd</code> and <code>ls</code> are enough.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
