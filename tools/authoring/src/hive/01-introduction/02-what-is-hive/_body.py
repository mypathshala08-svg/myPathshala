import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *

# ---------------------------------------------------------------- story
sc = (box(14, 20, 190, 110, 'red') + t(109, 38, '2007: the Java queue', 10, 'red', bold=True) +
      ''.join(t(28, 58 + k * 16, s, 8.8, anchor='start') for k, s in enumerate(['Analyst: “Total orders per city?”', 'Engineer: “Give me two days.”', '… writes a Java MapReduce job …', '… tests, deploys, fixes a bug …', 'Answer arrives on Thursday.'])) +
      arrow(212, 75, 246, 75, 'ink3', 2.2) +
      box(254, 20, 372, 110, 'green') + t(440, 38, 'With Hive: SQL in, answer out', 10, 'green', bold=True) +
      t(270, 62, 'SELECT city, COUNT(*)', 9, anchor='start', mono=True) + t(270, 76, 'FROM orders GROUP BY city;', 9, anchor='start', mono=True) +
      t(270, 104, 'Analyst runs it herself. Answer in minutes.', 8.8, 'ink2', anchor='start'))
scene_svg = scene('A queue of analysts waiting two days for a Java engineer, compared with an analyst running a SQL query herself in Hive.', sc,
                  'Hive turned “ask an engineer” into <tspan font-weight="700" class="s-acc">“run it yourself”</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>The analyst who had to wait two days</h2>
  <div class="story">
    <p class="narration">TiffinGo’s analyst Meera knows SQL very well. Her question is simple: “How many orders did each city give us last month?” But the orders are no longer in a small database. They are 2 TB of files spread over a Hadoop cluster, and the only way to read them is a Java MapReduce program. Meera cannot write one. She sends a request to the engineering team and waits.</p>

{scene_svg}

K> Sir, that sounds silly. Meera knows exactly what she wants. Why should she depend on an engineer for a simple count?
A> That was the exact problem a team at Facebook faced around 2007. Their data was growing fast on Hadoop, hundreds of analysts knew SQL, and only a few engineers could write MapReduce. So they built a layer that lets people write SQL-like queries, and the layer writes the MapReduce programs for them. They called it <b>Hive</b>, and in 2008 it was given to the Apache community as open source.
R> So Hive is a program that converts SQL into Java?
A> Close. Hive <b>translates a SQL-like language called HiveQL into distributed jobs</b>, runs them on the cluster, and returns the result. It also keeps a catalogue that says “the table <code>orders</code> is the folder <code>/data/orders</code> and has these columns”. That catalogue is the part many beginners miss, and Lesson 1.3 is entirely about it.
K> So is Hive a database like MySQL?
A> That is the best question of the day, and the honest answer is “not really”. Let us find out why.
  </div>
</section>
'''

# ---------------------------------------------------------------- definition
lv = '''
LEVELS> Hive at three levels
L1> A library
      <ul>
        <li>The <b>books</b> are your data files in HDFS. Hive does not move or copy them when you create a table.</li>
        <li>The <b>catalogue cards</b> (the <b>metastore</b>) say which shelf holds which book and what each chapter (column) is called.</li>
        <li>You, the reader, ask the librarian a question in plain language (<b>HiveQL</b>). The librarian (Hive) sends helpers (YARN containers) to the right shelves, collects the information and hands you the answer.</li>
        <li>This is great for questions like “how many books about cooking were borrowed this year?” and not great for “find book number 42 right now”.</li>
      </ul>
L2> What Hive is, and is not
      <ul>
        <li><b>Hive is:</b> a data-warehouse layer on Hadoop; SQL-like language (HiveQL); a metastore of table definitions; a compiler that turns queries into distributed jobs; support for many file formats (text, ORC, Parquet, Avro).</li>
        <li><b>Schema on read:</b> the files exist first; the table definition describes how to read them. Bad values do not stop a load: a value that cannot be parsed simply reads as <code>NULL</code>.</li>
        <li><b>Batch analytics (OLAP):</b> built to scan huge data and summarise it. A query takes seconds to minutes because starting distributed work has a fixed cost.</li>
        <li><b>Not OLTP:</b> not for thousands of small reads and writes per second (orders being placed, balances being updated). Use MySQL, PostgreSQL or a NoSQL store for that.</li>
        <li><b>Scales out:</b> to query ten times more data, add more machines; you do not change the SQL.</li>
      </ul>
L3> Architecture position, engines and where Hive is going
      <ul>
        <li><b>Execution engine:</b> in modern Hive queries run on <b>Apache Tez</b> by default; the original MapReduce engine is deprecated. Optional <b>LLAP</b> (long-lived daemons with caching) gives faster interactive queries.</li>
        <li><b>ACID tables:</b> since Hive 3, managed tables in ORC can be transactional (INSERT, UPDATE, DELETE, MERGE with snapshot isolation). Still batch-oriented, not OLTP.</li>
        <li><b>The metastore outlived the engine:</b> the Hive Metastore is the de-facto table catalogue for Spark, Trino/Presto, Impala, Flink and cloud services, even in platforms that no longer run HiveServer2.</li>
        <li><b>Open table formats:</b> Hive 4 can work with Apache Iceberg tables, and many clouds offer Hive-compatible catalogues (AWS Glue, for example).</li>
        <li><b>Where Hive fits now:</b> large nightly batch ETL, a shared SQL layer for analysts and BI tools, and the metastore. For interactive dashboards many teams add Trino, Impala, Spark SQL or a cloud warehouse next to it.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>What is Apache Hive?</h2>
''' + def_block(
    '<b>Apache Hive</b> is an open-source <b>data-warehouse system built on top of Apache Hadoop</b> that provides a <b>SQL-like query language, HiveQL</b>, for reading, writing and managing large datasets stored in distributed storage such as HDFS or cloud object stores. Hive keeps <b>table definitions</b> (schemas, partitions, locations) in a <b>metastore</b>, compiles each query into a plan of distributed tasks that run on an execution engine such as <b>Apache Tez</b> under <b>YARN</b>, and applies the schema when the data is read (<b>schema on read</b>). It is designed for <b>batch analytical (OLAP) workloads</b>, not for online transaction processing.',
    'Hive lets you ask questions of huge files using SQL. You describe the files as a table once; after that, you just write <code>SELECT</code>. Hive works out how to split the work across many machines. Think of it as <b>SQL on top of Hadoop</b>.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('HiveQL', 'Hive’s SQL-like language. Mostly standard SQL, plus extras for partitions, file formats and Hadoop.'),
    ('Metastore', 'The catalogue (a small database) that stores table names, columns, types, partitions and file locations.'),
    ('Schema on read', 'The data is stored as it is; the schema is applied only when you read it. Contrast: an RDBMS checks data when you write it.'),
    ('OLAP / OLTP', 'Analytical queries over lots of data (OLAP) versus many small transactions (OLTP).'),
    ('Execution engine', 'The component that runs a query’s tasks on the cluster: Tez (default), MapReduce (old) or Spark (optional).'),
    ('HiveServer2', 'The service that accepts SQL connections (JDBC/ODBC, Beeline) from users and tools.'),
    ('Beeline', 'The command-line SQL client that connects to HiveServer2.'),
    ('SerDe', 'Serializer/Deserializer: the code that turns a file’s bytes into columns and back.'),
]) + '''

  <h3>Hive and a traditional database (RDBMS), side by side</h3>
''' + table(['', 'Traditional RDBMS (MySQL, PostgreSQL)', 'Apache Hive'], [
    ['<b>Best for</b>', 'Transactions: many small reads and writes', 'Analytics: scans and summaries over huge data'],
    ['<b>Data size</b>', 'Gigabytes to a few terabytes on one server', 'Terabytes to petabytes across a cluster'],
    ['<b>Schema</b>', 'On write: bad data is rejected', 'On read: bad values read as NULL'],
    ['<b>Query speed</b>', 'Milliseconds for a lookup', 'Seconds to minutes (start-up cost), very high throughput'],
    ['<b>Updates</b>', 'Row-level, instant', 'Supported with ACID tables, but batch-style'],
    ['<b>Storage</b>', 'Its own files on one server', 'Files in HDFS or cloud storage, shared with other tools'],
    ['<b>Indexes</b>', 'Central to performance', 'Mostly replaced by partitioning, bucketing and columnar formats'],
    ['<b>Scale-out</b>', 'Hard (sharding, replicas)', 'Natural: add worker nodes'],
], minw=640) + lv + '''
EXAM> “Hive is not a database; it is a data-warehouse <i>infrastructure</i> on Hadoop.” For a 5-mark answer give: definition, origin (Facebook, 2007; Apache 2008), three features (HiveQL, schema on read, scalability), one limitation (high latency, not for OLTP) and the diagram “Client → Hive → Metastore + YARN + HDFS”.
</section>
'''

# ---------------------------------------------------------------- types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>How people use Hive, and what else is out there</h2>
''' + cards([
    ('Beeline (command line)', 'Connects to HiveServer2 with a JDBC URL. The standard way to run queries and scripts. The old “Hive CLI” is deprecated.', 'Engineers'),
    ('BI tools and JDBC/ODBC', 'Power BI, Tableau, Excel and Python connect to HiveServer2 and see Hive tables like any database.', 'Analysts'),
    ('Notebooks and Hue', 'Browser-based editors for writing queries, browsing tables and sharing results.', 'Analysts'),
    ('Scheduled scripts', 'Airflow, Oozie or cron run <code>beeline -f script.hql</code> every night to build reports.', 'Pipelines'),
    ('Metastore only', 'Spark, Trino and others use Hive’s metastore as their table catalogue without running Hive queries.', 'Platforms'),
]) + '''

  <h3>Hive and the other “SQL on big data” engines</h3>
''' + table(['Engine', 'Strength', 'Typical latency', 'When teams choose it'], [
    ['<b>Hive (on Tez)</b>', 'Huge batch jobs, mature, rich ecosystem, metastore', 'Seconds to hours', 'Nightly ETL, large reports, shared warehouse layer'],
    ['<b>Spark SQL</b>', 'In-memory processing, code + SQL together', 'Seconds to minutes', 'ETL pipelines with Python/Scala, machine learning prep'],
    ['<b>Trino / Presto</b>', 'Interactive queries across many sources', 'Sub-second to seconds', 'Ad-hoc analysis, federated queries'],
    ['<b>Impala</b>', 'Low-latency SQL on Hadoop data', 'Sub-second to seconds', 'Interactive BI on Hadoop clusters'],
    ['<b>Cloud warehouses</b> (BigQuery, Redshift, Snowflake)', 'Managed, no cluster to run', 'Seconds', 'Teams that prefer a managed service'],
], minw=640) + '''
  <h3>Hive vs Pig vs hand-written MapReduce</h3>
''' + table(['', 'Hive', 'Pig', 'MapReduce (Java)'], [
    ['Language', 'HiveQL: SQL-like, declarative', 'Pig Latin: step-by-step data flow script', 'Java code: map() and reduce() classes'],
    ['Built for', 'Analysts and SQL users; reports, warehouse tables', 'Programmers writing ETL pipelines', 'Engineers needing full control'],
    ['Schema', 'Tables in the metastore (schema on read)', 'Optional, declared in the script', 'None: you parse every record yourself'],
    ['Lines of code for word count', 'A few lines of SQL', 'About 5 lines', '60+ lines of Java'],
    ['Status today', 'Actively developed (Hive 4.x)', 'Still an Apache project, but rarely chosen for new work (teams use Spark or Hive)', 'Still in Hadoop, rarely written by hand'],
], minw=680) + '''
  <h3>A short history</h3>
''' + table(['Year', 'What happened'], [
    ['2007–2008', 'Built at Facebook so SQL-skilled analysts could query Hadoop; contributed to the Apache Software Foundation.'],
    ['2010', 'Became a top-level Apache project.'],
    ['2013–2014', 'Stinger initiative: ORC format, vectorized execution, and the <b>Tez</b> engine make Hive many times faster.'],
    ['2016', 'Hive 2: LLAP (long-lived daemons) for interactive queries.'],
    ['2018', 'Hive 3: ACID tables by default for managed tables, standalone metastore, MapReduce deprecated.'],
    ['2024', 'Hive 4.0 (March): Iceberg tables, the old Hive CLI replaced by Beeline, many optimiser improvements.'],
    ['2025–2026', 'Hive 4.1 (July 2025), 4.2 (November 2025) and 4.2.1 (August 2026), the version used in this course’s lab.'],
], minw=520) + '''
  <h3>Features, advantages and limitations</h3>
''' + table(['Features (what Hive offers)', 'Advantages (why teams use it)', 'Limitations (where it is the wrong tool)'], [
    ['<b>HiveQL</b>: SQL-like language with joins, window functions, CTEs', 'Analysts reuse SQL skills; no Java MapReduce code', '<b>High latency</b>: seconds even for tiny queries; not for real-time answers'],
    ['<b>Schema on read</b> over files in HDFS or object storage', 'Load raw files first, decide the schema later', '<b>Not OLTP</b>: no fast single-row inserts, updates or lookups'],
    ['<b>Partitioning and bucketing</b>', 'Queries read only the folders they need', 'Bad partition design creates millions of small files'],
    ['<b>Many file formats</b>: text, SequenceFile, RCFile, Avro, ORC, Parquet, JSON', 'Store data once, read it from Hive, Spark, Trino', 'Text formats are slow and large compared with ORC/Parquet'],
    ['<b>Metastore</b> shared by many engines', 'One catalogue for the whole data platform', 'The metastore becomes critical infrastructure to run and back up'],
    ['<b>UDFs</b> and SerDes for custom logic and formats', 'Extend Hive in Java or with scripts', 'Custom code must be deployed and maintained'],
    ['<b>ACID tables</b> (ORC) and <b>Iceberg</b> tables', 'UPDATE, DELETE and MERGE on big tables', 'Row-level changes are heavy compared with an RDBMS; compaction needed'],
    ['<b>Optimiser and engines</b>: cost-based optimiser, Tez, vectorisation, LLAP', 'Scales from gigabytes to petabytes by adding machines', 'Tuning needs knowledge of plans, statistics and the cluster'],
], minw=760) + '''
TIP> In interviews do not say “Hive is slow”. Say: “Hive has a high start-up latency but very high throughput, so it is ideal for large batch analytics, and it is not meant for point lookups.”
</section>
'''

# ---------------------------------------------------------------- steps
c1 = '''rows = "1,Pune,220\\n2,Thane,abc\\n3,Mumbai,310"
schema = [("id", int), ("city", str), ("amount", int)]
def read(line):
    out = []
    for (name, typ), raw in zip(schema, line.split(",")):
        try:
            out.append(typ(raw))
        except ValueError:
            out.append(None)          # Hive reads an unparseable value as NULL
    return out
for line in rows.split("\\n"):
    print(read(line))'''
c2 = '''files = {"/data/orders/part-0": "1,Pune,220\\n2,Thane,150", "/data/orders/part-1": "3,Pune,180"}
metastore = {"orders": {"location": "/data/orders", "columns": ["id", "city", "amount"]}}
t = metastore["orders"]
data = [l.split(",") for p, c in files.items() if p.startswith(t["location"]) for l in c.split("\\n")]
print("table orders reads", len(files), "files and", len(data), "rows")'''
c3 = '''del metastore_entry if False else None''' if False else '''files = {"/data/orders/part-0": "x", "/data/orders/part-1": "y"}
metastore = {"orders": "/data/orders"}
del metastore["orders"]            # DROP TABLE on an EXTERNAL table
print("tables:", list(metastore), "| files still there:", sorted(files))'''
q1 = '''CREATE EXTERNAL TABLE orders (
  id INT, city STRING, amount INT)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/data/orders';'''
q2 = '''SELECT city, SUM(amount) AS total
FROM orders
GROUP BY city;'''
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>From files to an answer, the Hive way</h2>
''' + stepper([
    ('Start with plain files in HDFS',
     '<p>The order files already sit in the folder <code>/data/orders</code>, one CSV per day. Nothing is loaded into a database.</p>',
     'This is the big difference from MySQL: the data is not imported into Hive’s own storage. Other tools (Spark, Pig, MapReduce) can read the very same files.'),
    ('Describe the files as a table (HiveQL)',
     code('sql', 'create_table.hql', q1),
     'This statement is fast even for 2 TB, because Hive does not touch the data. It only writes a few rows into the <b>metastore</b>: name, columns, delimiter and location.'),
    ('Schema is applied when data is read',
     code('python', 'schema_on_read.py', c1, run_code(c1)),
     'Row 2 has “abc” where a number should be. Hive does not refuse the file; the value reads as <code>NULL</code>. This is why Hive data-quality checks (counting NULLs) matter so much.'),
    ('Ask a question in SQL',
     code('sql', 'query.hql', q2),
     'Meera writes the same <code>SELECT … GROUP BY</code> she knows from MySQL. HiveServer2 receives it, checks the table in the metastore and compiles it into a plan of map and reduce stages (Lesson 1.4).'),
    ('The table is a window on the files',
     code('python', 'table_is_a_window.py', c2, run_code(c2)),
     'The metastore stores only where the files are and how to read them. The query reads whatever files are in that folder at that moment: drop a new file in the folder and the next query includes it.'),
    ('Dropping an external table keeps the data',
     code('python', 'drop_external.py', c3, run_code(c3)),
     '<code>DROP TABLE</code> on an <b>external</b> table removes only the metastore entry. The files stay. (On a <i>managed</i> table Hive owns the files and deletes them too. Lesson 2.2 is about this difference.)'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
def term(lines, h=170):
    o = '<rect x="14" y="14" width="332" height="196" rx="8" class="s-board"/><text x="26" y="30" font-size="9" class="mono" style="fill:#7F8C86">beeline&gt; (illustrative)</text>'
    for k, (txt, col) in enumerate(lines):
        o += f'<text x="26" y="{50 + k * 14}" font-size="8.4" class="mono" style="fill:{col}">{txt}</text>'
    return o
G, W, Y = '#9FD3B8', '#EDEBE3', '#F5C77E'
see = [
    term([('CREATE EXTERNAL TABLE orders (', W), ('  id INT, city STRING, amount INT)', W), ("LOCATION '/data/orders';", W)]),
    term([('CREATE EXTERNAL TABLE orders (…);', W), ('No rows affected (0.21 seconds)', G), ('', W), ('Created instantly, even for 2 TB.', Y)]),
    term([('SELECT city, SUM(amount) AS total', W), ('FROM orders GROUP BY city;', W)]),
    term([('SELECT city, SUM(amount) …', W), ('INFO : Tez session started', G), ('Map 1: 16/16   Reducer 2: 1/1', G), ('INFO : Completed executing', G)]),
    term([('+---------+--------+', W), ('| city    | total  |', W), ('| Mumbai  | 450    |', G), ('| Pune    | 560    |', G), ('| Thane   | 240    |', G), ('+---------+--------+', W), ('3 rows selected (21.4 seconds)', Y)]),
    term([('DROP TABLE orders;', W), ('No rows affected (0.12 seconds)', G), ('', W), ('hdfs dfs -ls /data/orders', W), ('part-0 … part-15   (files still there)', G)]),
]
def md(rows=None, files=True, glow=False):
    o = box(10, 18, 150, 100, 'blue') + t(85, 32, 'Metastore', 9, bold=True) + t(85, 44, '(table catalogue)', 7.8, 'ink2')
    if rows:
        o += box(20, 54, 130, 52, 'card') + ''.join(t(26, 68 + k * 11, s, 7.4, anchor='start', mono=True) for k, s in enumerate(rows))
    o += box(180, 18, 170, 100, 'green') + t(265, 32, 'HDFS  /data/orders', 9, bold=True)
    if files:
        for k in range(8):
            o += fill(192 + (k % 4) * 38, 46 + (k // 4) * 30, 32, 22, 'green' if not glow else 'acc', rx=3) + t(208 + (k % 4) * 38, 60 + (k // 4) * 30, f'p{k}', 7.4, extra=' style="fill:#fff"', bold=True)
        o += t(265, 110, '… 16 files, 2 TB', 7.8, 'ink2')
    else:
        o += t(265, 76, 'empty', 9, 'ink3')
    return o
rowsets = ['orders → /data/orders', 'cols: id, city, amount', 'delimiter: ,']
behind = [
    md() + t(180, 150, 'The files exist. The catalogue knows nothing yet.', 9, 'ink2'),
    md(rowsets) + '<path d="M150 80L180 80" class="s-wire"/>' + t(180, 150, 'Only a few rows written to the metastore. Files untouched.', 9, 'green', bold=True),
    md(rowsets) + t(180, 150, 'HiveServer2 reads the table definition from the metastore', 9, 'ink2'),
    md(rowsets, glow=True) + t(180, 150, 'Tez tasks read the files in parallel', 9, 'acc', bold=True) + t(180, 168, 'Each file part becomes work for a container', 8.6, 'ink2'),
    md(rowsets) + t(180, 150, 'Result rows go back to the user. Nothing is stored.', 9, 'green', bold=True),
    md(None) + t(180, 150, 'Metastore entry removed. The files stay.', 9, 'green', bold=True) + t(180, 168, '(this was an EXTERNAL table)', 8.6, 'ink2'),
]
see_caps = ['Meera describes the order files as a table. She writes the columns and the folder.',
            'The statement returns in a fraction of a second, no matter how big the data is.',
            'She asks her question in ordinary SQL.',
            'Hive starts a Tez session and runs map and reduce stages on the cluster. 16 map tasks, 1 reducer.',
            'Three rows come back after about 21 seconds. (Time is illustrative.)',
            'She drops the table. The folder with the files is still there, so no data was lost.']
behind_caps = ['Before anything: 16 files in HDFS, and an empty catalogue.',
               'CREATE EXTERNAL TABLE adds one entry to the metastore. Not a single byte of data is copied or moved.',
               'The query arrives. Hive looks up “orders” in the metastore to learn the folder, columns and file format.',
               'Hive plans the job. YARN gives containers and each reads some files from HDFS, applying the schema on the fly.',
               'The final rows are streamed back through HiveServer2 to Beeline. Intermediate data is thrown away.',
               'DROP TABLE on an external table removes only the metastore entry. Other tools can still read the files.']
two = anim_two('Create, query, drop', 'A Hive table is a window on files', 'Beeline commands creating, querying and dropping an external table',
               'The metastore and HDFS files during create, query and drop', see, behind, see_caps, behind_caps)

# ---- scenario 1: the Java queue vs Hive
def tl(x, y, w, color, label):
    return fill(x, y, w, 14, color, rx=4) + t(x + w / 2, y + 10.5, label, 7.8, bold=True, extra=' style="fill:#fff"')
sa = (t(14, 24, 'Request: “orders per city”', 9, 'ink2', anchor='start') + t(14, 44, 'Meera', 8.4, anchor='start', bold=True) + tl(60, 33, 80, 'amber', 'asks') +
      cap('Meera needs an answer. In 2007 there is only one way in.', '', 'card', y=150, h=34))
sb = (t(14, 24, 'Without Hive', 9, 'red', anchor='start', bold=True) + t(14, 44, 'Meera', 8.4, anchor='start', bold=True) + tl(60, 33, 40, 'amber', 'ask') + tl(100, 33, 190, 'red', 'wait …') +
      t(14, 70, 'Engineer', 8.4, anchor='start', bold=True) + tl(100, 59, 150, 'blue', 'write Java') + tl(250, 59, 60, 'violet', 'test') +
      cap('Day 1–2: a Java MapReduce job is written and tested.', 'Meera cannot help; she does not know Java.', 'red', y=130, h=46))
sc_ = (t(14, 24, 'Without Hive', 9, 'red', anchor='start', bold=True) + t(14, 44, 'Meera', 8.4, anchor='start', bold=True) + tl(60, 33, 40, 'amber', 'ask') + tl(100, 33, 190, 'red', 'wait …') + tl(290, 33, 54, 'green', 'answer') +
       t(14, 70, 'Engineer', 8.4, anchor='start', bold=True) + tl(100, 59, 150, 'blue', 'write Java') + tl(250, 59, 60, 'violet', 'test') +
       cap('Day 3: the answer arrives. One question, three days.', 'Every new question starts the queue again.', 'red', y=130, h=46))
sd = (t(14, 24, 'With Hive', 9, 'green', anchor='start', bold=True) + t(14, 44, 'Meera', 8.4, anchor='start', bold=True) + tl(60, 33, 70, 'amber', 'writes SQL') + tl(130, 33, 40, 'acc', 'runs') + tl(170, 33, 40, 'green', 'answer') +
      t(14, 70, 'Engineer', 8.4, anchor='start', bold=True) + tl(60, 59, 250, 'grey', 'free to build the next pipeline') +
      cap('Same question, answered the same morning.', 'Meera can ask ten questions in a day.', 'green', y=130, h=46))
se = (t(180, 30, 'What changed', 10.5, 'acc', bold=True) + ''.join(t(34, 56 + k * 22, s, 8.8, anchor='start') for k, s in enumerate(['• Analysts self-serve with SQL they already know.', '• Engineers build pipelines instead of one-off jobs.', '• Hive writes the distributed program automatically.', '• The same data stays available to every tool.'])) + cap('Hive made big data accessible to SQL people.', '', 'green', y=164, h=34))
s1 = anim_one('Real-time scenario 1', 'Why Hive was needed: the engineer queue',
              'Follow the same business question with and without Hive. Time is shown as bars: the longer the bar, the longer the wait.',
              'From “ask an engineer” to “run it myself”', 'Timeline of an analyst waiting for a Java engineer versus running a SQL query directly in Hive', [sa, sb, sc_, sd, se],
              ['Meera needs the number of orders per city. The data is on Hadoop, and Hadoop speaks Java.',
               'Without Hive she asks an engineer, who writes and tests a MapReduce job over two days.',
               'The answer arrives on day 3. If she then wants “per city per week”, the queue starts again.',
               'With Hive she writes SQL, runs it, and has her answer the same morning, while the engineer builds something else.',
               'Hive’s main contribution is not speed; it is access. SQL people can now use big data directly.'],
              hid='scenario-queue')

# ---- scenario 2: OLTP vs OLAP
def bar(y, label, frac, col, txt):
    return t(14, y + 11, label, 8.2, anchor='start') + '<rect x="130" y="%d" width="150" height="14" rx="4" class="s-card2"/>' % y + (fill(130, y, max(2, round(150 * frac)), 14, col, rx=4)) + t(346, y + 11, txt, 8, 'ink', anchor='end', bold=True)
oa = (t(180, 22, 'Task 1: find order #4021 (one row)', 9.6, bold=True) + bar(40, 'MySQL', .03, 'green', '3 ms') + bar(66, 'Hive', .55, 'red', '≈ 15 s') +
      cap('Point lookup: MySQL wins by a mile.', 'Hive pays a start-up cost even for one row.', 'card', y=110, h=46) +
      t(180, 178, 'Bar lengths are illustrative, not measurements.', 8, 'ink3'))
ob = (t(180, 22, 'Task 2: total sales per city, 2 TB', 9.6, bold=True) + bar(40, 'MySQL (1 server)', 1, 'red', 'hours / fails') + bar(66, 'Hive (40 nodes)', .12, 'green', 'minutes') +
      cap('Big scan: Hive spreads it over 40 machines.', 'One server runs out of disk, memory or patience.', 'green', y=110, h=46) +
      t(180, 178, 'Bar lengths are illustrative, not measurements.', 8, 'ink3'))
oc = (t(180, 22, 'Task 3: place 5,000 orders per second', 9.6, bold=True) + bar(40, 'MySQL', .2, 'green', 'designed for it') + bar(66, 'Hive', 1, 'red', 'wrong tool') +
      cap('Many tiny writes: every write would be a job.', 'Use a transactional database for this.', 'red', y=110, h=46) +
      t(180, 178, 'Bar lengths are illustrative, not measurements.', 8, 'ink3'))
od = (t(180, 24, 'The usual platform: use both', 10, 'acc', bold=True) + label_box(14, 40, 96, 44, ['App', 'MySQL / NoSQL'], 'blue', 8.6) + arrow(112, 62, 142, 62) + label_box(144, 40, 96, 44, ['Data lake', 'HDFS / S3'], 'green', 8.6) + arrow(242, 62, 270, 62) + label_box(272, 40, 76, 44, ['Hive', 'analytics'], 'acc', 8.6) +
      cap('Operational databases record the orders.', 'Hive analyses all of them together, later.', 'blue', y=110, h=46))
oe = (t(180, 24, 'Choosing the tool', 10, 'acc', bold=True) + ''.join(t(26, 50 + k * 17, s, 8.6, anchor='start') for k, s in enumerate(['One record, instantly → MySQL / PostgreSQL / NoSQL', 'Scan billions of rows → Hive, Spark, Trino', 'Interactive dashboard → Trino / Impala / warehouse', 'Nightly ETL on a Hadoop cluster → Hive or Spark'])) + cap('Right tool, right job.', '', 'green', y=130, h=34))
s2 = anim_one('Real-time scenario 2', 'Hive vs MySQL: three tasks, three winners',
              'Same company, three different tasks. See where Hive shines and where it is the wrong tool. Bars are illustrative to show the idea, not benchmarks.',
              'Choosing between Hive and an RDBMS', 'Comparison of Hive and MySQL on a point lookup, a huge aggregation and many small writes', [oa, ob, oc, od, oe],
              ['Finding one order by its number: MySQL answers in milliseconds. Hive needs seconds because it starts distributed work first.',
               'Total sales per city over 2 TB: one MySQL server struggles or fails. Hive splits the work over many machines and finishes in minutes.',
               'Taking 5,000 orders a second: each Hive write would be a job. Use a transactional database.',
               'Real platforms use both: operational databases record the data, a data lake collects it, Hive analyses it.',
               'The rule of thumb: Hive for large analytical scans, an RDBMS or NoSQL for operational lookups and writes.'],
              hid='scenario-oltp')

# ---- scenario 3: one metastore, many engines
def eng(x, name, tone):
    return label_box(x, 100, 78, 32, [name], tone, 8.6)
ma = (label_box(110, 20, 140, 44, ['Hive Metastore', 'table catalogue'], 'blue', 9) + label_box(110, 100, 140, 44, ['Files in HDFS / S3', '/data/orders'], 'green', 9) +
      t(180, 84, 'orders → /data/orders · id, city, amount', 7.8, 'ink2', mono=True) + cap('Step 1: Hive creates the table. The metastore records it.', '', 'blue', y=158, h=34))
mb = (label_box(14, 20, 90, 34, ['Hive'], 'acc', 9) + label_box(110, 20, 140, 34, ['Hive Metastore'], 'blue', 9) + label_box(110, 100, 140, 34, ['Files in HDFS / S3'], 'green', 9) +
      arrow(106, 37, 108, 37) + arrow(180, 56, 180, 98, 'ink3') + cap('Hive queries the table through the metastore.', '', 'acc', y=158, h=34))
mc = (label_box(14, 20, 90, 34, ['Hive'], 'acc', 9) + label_box(256, 20, 90, 34, ['Spark SQL'], 'violet', 9) + label_box(110, 20, 140, 34, ['Hive Metastore'], 'blue', 9) + label_box(110, 100, 140, 34, ['Files in HDFS / S3'], 'green', 9) +
      arrow(180, 56, 180, 98, 'ink3') + arrow(256, 37, 252, 37) + cap('Spark SQL reads the same table. No copy, no redefinition.', '', 'violet', y=158, h=34))
md_ = (label_box(14, 12, 90, 30, ['Hive'], 'acc', 9) + label_box(256, 12, 90, 30, ['Spark SQL'], 'violet', 9) + label_box(14, 56, 90, 30, ['Trino'], 'amber', 9) + label_box(256, 56, 90, 30, ['Impala'], 'green', 9) + label_box(110, 30, 140, 40, ['Hive Metastore'], 'blue', 9) + label_box(110, 100, 140, 34, ['Files in HDFS / S3'], 'green', 9) +
       arrow(180, 72, 180, 98, 'ink3') + cap('Trino, Impala and others do the same.', 'One definition, many engines, one copy of the data.', 'blue', y=150, h=46))
me = (label_box(14, 20, 100, 44, ['Move to cloud'], 'card', 9) + arrow(116, 42, 140, 42) + label_box(142, 20, 204, 44, ['LOCATION changes:', 's3://tiffingo/orders'], 'green', 9) + t(180, 92, 'Table definitions and queries stay the same.', 9, 'ink2') +
      cap('The metastore outlived Hadoop as a standard catalogue.', 'Many cloud services offer a Hive-compatible catalogue.', 'green', y=116, h=46))
s3 = anim_one('Real-time scenario 3 · advanced', 'One metastore, many engines',
              'The metastore is Hive’s most reusable part. Watch the same table definition serve Hive, Spark, Trino and Impala, and survive a move to the cloud.',
              'The metastore as shared catalogue', 'Hive, Spark SQL, Trino and Impala all using one Hive Metastore over the same files', [ma, mb, mc, md_, me],
              ['Hive creates the table orders. The metastore records its location and columns. The data stays in files.',
               'Hive queries the table: it asks the metastore what the table is, then reads the files.',
               'Spark SQL, configured to use the same metastore, sees the table too. Nothing is copied or defined twice.',
               'Trino, Impala and other engines can do the same: one definition, many readers, one copy of the data.',
               'When the platform moves to cloud storage only the table’s location changes. Queries do not. That is why the Hive Metastore is used far beyond Hive itself.'],
              hid='scenario-metastore')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Create a table, query it, drop it: what you see and what really happens</h2>
  <p>Left: the Beeline screen. Right: the metastore and the HDFS files. Watch how little happens when a table is created, and why the data survives a drop.</p>
''' + two + '''
  <p>Three live scenarios follow: why Hive was needed, where Hive wins or loses against MySQL, and how the metastore is shared by many engines.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

# ---------------------------------------------------------------- real-world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Where companies use Hive</h2>
''' + usecase(
    '<rect x="16" y="24" width="88" height="42" rx="6" class="s-card2"/>' + ''.join(fill(24 + k * 14, 50 - (k % 3) * 8 - 6, 10, 12 + (k % 3) * 8, 'green') for k in range(5)),
    '1. Nightly sales and revenue reports',
    'A retailer’s stores upload the day’s billing files to HDFS. At 2 a.m. a scheduled Hive script joins sales with product and store tables and writes a summary table. By morning, managers open dashboards built on it.',
    ['Billing files', '*Hive batch job', 'Summary table', 'Dashboard']) + '\n' + usecase(
    '<rect x="16" y="20" width="88" height="50" rx="6" class="s-board"/><text x="26" y="40" font-size="8" class="mono" style="fill:#9FD3B8">GET /api/pay 200</text><text x="26" y="54" font-size="8" class="mono" style="fill:#F5C77E">GET /api/pay 500</text>',
    '2. Web and app log analysis',
    'Servers write terabytes of logs every day. A Hive table over the log folder lets support teams count error codes per hour, per app version, without writing code.',
    ['Log files', '*Hive table', 'Errors per hour']) + '\n' + usecase(
    '<rect x="16" y="20" width="88" height="50" rx="6" class="s-card2"/>' + t(60, 42, 'call records', 8.4, bold=True) + t(60, 58, '30 TB / month', 8.4, 'ink2'),
    '3. Telecom usage analytics',
    'A telecom operator stores call and data records for billing and planning. Analysts use HiveQL to find busy cells, churn signals and plan usage over months of history.',
    ['Call records', '*HiveQL', 'Network planning']) + '\n' + usecase(
    '<rect x="16" y="24" width="88" height="40" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'Power BI / Tableau', 8.4, 'blue', bold=True) + t(60, 56, 'via JDBC', 8, 'ink2'),
    '4. BI tools on a data lake',
    'Business users connect Power BI, Tableau or Excel to HiveServer2 with an ODBC/JDBC driver and build charts over Hive tables, without knowing that files and clusters are behind them.',
    ['Dashboard', '*HiveServer2', 'Data lake']) + '\n' + usecase(
    cyl(36, 18, 48, 34, 'Catalog', 'blue') + '<path d="M60 56v8" class="s-line"/>' + box(14, 64, 92, 18, 'green') + t(60, 76, 'S3 / HDFS', 8, bold=True),
    '5. Metastore as the cloud data catalogue',
    'On cloud platforms (for example Amazon EMR, Google Dataproc or Azure HDInsight) the Hive Metastore, or a compatible catalogue, tells Spark, Hive and Trino what tables exist over the object store.',
    ['Cloud storage', '*Metastore', 'Spark / Hive / Trino']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not any particular company’s internal systems.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> you should know basic SQL (<code>SELECT</code>, <code>GROUP BY</code>) and that HDFS stores files as blocks on many machines. Rusty? Read <a href="../01-prerequisites-sql-hdfs-and-yarn-refresher/">Lesson 1.1: Prerequisites</a> first (25 minutes).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
