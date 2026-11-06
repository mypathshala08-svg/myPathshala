import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
BODY = body(HERE)

META = dict(
    module='01-introduction', lesson='02-what-is-hive', n='1.2',
    module_label='Module 1 · Start here: why Hive?',
    title='What is Hive? The story of SQL on Hadoop',
    desc='What is Apache Hive? Why Facebook built it, what HiveQL, the metastore and schema on read mean, how Hive differs from MySQL and from Spark SQL, Trino and Impala. A story-based lesson with animations, real-time scenarios, runnable Python and interview questions.',
    og_desc='Hive lets you query huge files in HDFS with SQL. Learn why it was built, what it is, and where it fits.',
    minutes=30, level='Beginner → Advanced',
    lead='Meera the analyst knows SQL, but the company’s data now lives as files on a Hadoop cluster. Hive is the layer that lets her ask questions in SQL while the cluster does the heavy lifting. This lesson tells the story behind Hive, defines it precisely, and compares it honestly with a normal database and with other SQL engines.',
    chips=['Story-based', '4 animations', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Schema on read: the idea behind every Hive table',
    intro='<p>A Hive table is a <i>description</i> of files. This program imitates that: a CSV text and a schema are kept apart, and the schema is applied only when a row is read. Notice what happens with a bad value, and compare with what Python normally does. Then try the challenges.</p>',
    code='''csv_text = """1,Pune,220
2,Thane,abc
3,Mumbai,310"""
schema = [("id", int), ("city", str), ("amount", int)]

def read_row(line):
    row = []
    for (name, typ), raw in zip(schema, line.split(",")):
        try:
            row.append(typ(raw))
        except ValueError:
            row.append(None)        # like Hive: unparseable value -> NULL
    return row

rows = [read_row(l) for l in csv_text.split("\\n")]
for r in rows:
    print(r)
total = sum(r[2] for r in rows if r[2] is not None)
print("SUM(amount) ignores NULL:", total)
''',
    anno=[
        ('schema = [("id", int), ("city", str), ("amount", int)]', 'The table definition, kept separate from the data, like a row in the metastore.'),
        ('except ValueError: row.append(None)', 'Hive does not reject a bad value; the column reads as NULL. This is the heart of schema on read.'),
        ('sum(... if r[2] is not None)', 'SQL aggregates such as <code>SUM</code> skip NULLs, so one bad value silently lowers the total. Always count NULLs when loading data.'),
    ],
    tasks=[
        dict(label='1 · Read with a schema', hint='Press <b>Run</b>. Row 2 has <code>None</code> for amount. Fix the data and run again.', code=None),
        dict(label='2 · Count the NULLs', hint='<b>Predict first:</b> how many NULLs per column? A data-quality check like this is the first query to run on a new Hive table.',
             code='''csv_text = "1,Pune,220\\n2,Thane,abc\\n3,,310\\n4,Pune,xyz"
schema = [("id", int), ("city", str), ("amount", int)]
def read_row(line):
    out = []
    for (n, typ), raw in zip(schema, line.split(",")):
        try:
            out.append(typ(raw) if raw != "" else None)
        except ValueError:
            out.append(None)
    return out
rows = [read_row(l) for l in csv_text.split("\\n")]
for i, (name, _) in enumerate(schema):
    print(name, "NULLs:", sum(1 for r in rows if r[i] is None))
'''),
        dict(label='3 · Same files, two schemas', hint='The same text read with two different table definitions. Predict the output, then add a third schema that reads the amount as text.',
             code='''line = "7,Pune,220"
wide = [("id", int), ("city", str), ("amount", int)]
odd = [("city", str), ("amount", int), ("id", int)]
for schema in (wide, odd):
    out = []
    for (n, typ), raw in zip(schema, line.split(",")):
        try:
            out.append((n, typ(raw)))
        except ValueError:
            out.append((n, None))
    print(out)
'''),
        dict(label='4 · A tiny “SELECT … WHERE”', hint='Filter the parsed rows like <code>WHERE amount &gt; 200</code> and project two columns. NULL never satisfies a comparison in SQL; check that None rows are dropped.',
             code='''rows = [[1, "Pune", 220], [2, "Thane", None], [3, "Mumbai", 310]]
result = [(r[1], r[2]) for r in rows if r[2] is not None and r[2] > 200]
print(result)
'''),
        dict(label='5 · Spot the error', hint='Plain Python refuses a bad value, unlike Hive. Run it, read the error, and make it behave like Hive (return None instead).', expect='error',
             code='''raw = "abc"
amount = int(raw)
print(amount)
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: your first Hive table',
    intro='<p>If you have a Hive setup (for example the Hadoop lab plus Hive), these commands create the table from this lesson. <b>The outputs below are typical examples written for this lesson, not a recording of a particular machine</b>; times, host names and file counts will differ.</p>',
    items=[
        dict(title='1 · Connect with Beeline', cmd="beeline -u jdbc:hive2://localhost:10000 -n hadoop\n0: jdbc:hive2://localhost:10000> SHOW DATABASES;", file='Terminal',
             output='+----------------+\n| database_name  |\n+----------------+\n| default        |\n+----------------+\n1 row selected (0.31 seconds)',
             note='Port 10000 is HiveServer2’s default. The <code>default</code> database always exists.'),
        dict(title='2 · Put a file in HDFS and describe it as a table', cmd="hdfs dfs -mkdir -p /data/orders\nhdfs dfs -put orders.csv /data/orders/\n\nCREATE EXTERNAL TABLE orders (id INT, city STRING, amount INT)\nROW FORMAT DELIMITED FIELDS TERMINATED BY ','\nSTORED AS TEXTFILE LOCATION '/data/orders';", file='Terminal / Beeline',
             output='No rows affected (0.214 seconds)',
             note='Notice how quickly it returns: no data was read or copied. Only the metastore changed.'),
        dict(title='3 · Look at the definition and query it', cmd='DESCRIBE orders;\nSELECT city, SUM(amount) AS total FROM orders GROUP BY city;', file='Beeline',
             output='+-----------+------------+----------+\n| col_name  | data_type  | comment  |\n+-----------+------------+----------+\n| id        | int        |          |\n| city      | string     |          |\n| amount    | int        |          |\n+-----------+------------+----------+',
             note='The second query launches a Tez job (you will see progress lines). Its rows depend on your <code>orders.csv</code>.'),
    ],
)

TRACE = dict(
    heading='Reading rows with a schema, one line at a time',
    intro='<p>Watch how each raw text value is converted using the schema, and how a bad value becomes <code>None</code> (NULL) instead of stopping the program.</p>',
    code='''schema = [int, str, int]
lines = ["1,Pune,220", "2,Thane,abc"]
table = []
for line in lines:
    row = []
    for typ, raw in zip(schema, line.split(",")):
        try:
            row.append(typ(raw))
        except ValueError:
            row.append(None)
    table.append(row)
print(table)
''',
    notes={8: 'Parse :: Apply the schema to one raw value. This is what a SerDe does.', 10: 'NULL :: The conversion failed, so Hive-style behaviour: store NULL and carry on.'},
)

WORKED_INTRO = 'Three small jobs that capture what Hive does: read text with a schema, decide whether a workload belongs in Hive, and estimate why Hive’s start-up cost matters. All run live and are traced in memory.'
EXAMPLES = [
    dict(level='b', tag='Data quality · NULL check', title='How many bad values does the file hold?',
         problem='<p>A daily order file arrives as CSV text. The schema says <code>amount</code> must be an integer. Count how many rows have an unparseable amount, and compute the total of the valid ones.</p>',
         inp='rows: 220, 150, abc, 90, (empty), 60',
         approach=['Go through each raw amount.', 'Try to convert to int; count failures as NULL.', 'Add up the valid amounts.'],
         code='''raw_amounts = ["220", "150", "abc", "90", "", "60"]
nulls, total = 0, 0
for raw in raw_amounts:
    try:
        total += int(raw)
    except ValueError:
        nulls += 1
print("NULL amounts:", nulls)
print("SUM of valid:", total)
''', notes={5: 'Parse :: A good value is added; a bad one raises ValueError and is counted as NULL.'},
         tryit='A silent NULL lowers the SUM without any error. In a real warehouse you would compare NULL counts with yesterday’s to catch a broken feed.'),
    dict(level='i', tag='Architecture · choose the tool', title='Hive or a normal database?',
         problem='<p>For each workload decide if Hive is a good fit. Rule: Hive fits if the data is large (over 1 TB) <b>and</b> the queries scan or summarise rather than look up single rows.</p>',
         inp='3 workloads with size in TB and query style',
         approach=['Describe each workload by size and style.', 'Apply the rule.', 'Print the recommendation.'],
         code='''workloads = [("monthly revenue report", 5, "scan"),
             ("find order by id", 5, "lookup"),
             ("customer profile page", 0.01, "lookup")]
for name, tb, style in workloads:
    fit = tb > 1 and style == "scan"
    print(f"{name:24} -> {'Hive' if fit else 'RDBMS / NoSQL'}")
''', notes={5: 'Rule :: Large AND scanning.'},
         tryit='Add “nightly clean-up of 20 TB of logs” (scan) and “live inventory count” (lookup, 0.5 TB). Which tool does each pick?'),
    dict(level='a', tag='Performance · start-up cost', title='When does Hive’s fixed overhead stop mattering?',
         problem='<p>Assume a Hive query has a fixed start-up cost of <b>15 s</b> and scans at <b>2 GB/s</b> across the cluster, while a single database server scans at <b>0.2 GB/s</b> with <b>0.01 s</b> start-up. For data sizes 1 GB, 100 GB and 5,000 GB, print each system’s time and the winner. (Illustrative model.)</p>',
         inp='sizes: 1, 100, 5000 GB',
         approach=['Time = start-up + size ÷ scan speed.', 'Compute for both systems.', 'Print which is faster.'],
         code='''for gb in [1, 100, 5000]:
    hive = 15 + gb / 2.0
    db = 0.01 + gb / 0.2
    winner = "Hive" if hive < db else "database"
    print(f"{gb:5} GB  hive {hive:8.1f}s  db {db:9.1f}s  -> {winner}")
''', notes={2: 'Model :: A fixed start-up cost plus size divided by speed.'},
         tryit='Find the size where they tie: solve 15 + g/2 = 0.01 + g/0.2. The point is that start-up cost matters only for small data.'),
]

QUIZ = mix([
    dict(q='What is Apache Hive?', options=['A NoSQL document store', 'A data-warehouse layer on Hadoop that lets you query data with SQL-like HiveQL', 'A replacement for HDFS', 'A programming language that compiles to Java'], answer=1,
         why='Hive provides HiveQL, a metastore and a compiler that turns queries into distributed jobs over data in HDFS or cloud storage.'),
    dict(q='Where does Hive store the data of an external table?', options=['In the metastore database', 'In files in HDFS (or cloud storage) at the table’s location', 'In HiveServer2’s memory', 'In ZooKeeper'], answer=1,
         why='The metastore holds only definitions; the rows live as files at the table’s location.'),
    dict(q='What does “schema on read” mean?', options=['Data is checked and rejected when written', 'The schema is applied when data is read, so bad values read as NULL', 'The schema is stored inside every row', 'Only schema changes are allowed'], answer=1,
         why='Files are stored as they are. The table definition says how to interpret them at query time.'),
    dict(q='Which workload is a poor fit for Hive?', options=['Nightly report over 5 TB of sales', 'Looking up one customer’s profile in under 50 ms for a web page', 'Counting errors in terabytes of logs', 'Building a summary table for dashboards'], answer=1,
         why='Hive has high start-up latency; it is for batch analytics, not interactive point lookups.'),
    dict(q='What happens when you DROP an EXTERNAL table?', options=['The files in HDFS are deleted', 'Only the metastore entry is removed; the files stay', 'The whole database is deleted', 'Nothing happens'], answer=1,
         why='Hive does not own the data of an external table, so it removes only the definition.'),
    dict(q='Which engine does modern Hive use by default to run queries?', options=['Apache Tez', 'Hadoop Streaming', 'Apache Flink', 'MySQL'], answer=0,
         why='Hive on Tez is the default; the MapReduce engine is deprecated.'),
    dict(q='Why do Spark and Trino often use the Hive Metastore?', options=['Because they cannot read files', 'To share one table catalogue so tables are defined once and readable by many engines', 'Because Hive must execute their queries', 'Because it is faster than their own storage'], answer=1,
         why='The metastore is a shared catalogue of table definitions and locations, independent of the engine that reads the data.'),
])

REVISION = [
    '<b>Hive</b> = SQL-like <b>HiveQL</b> on Hadoop data. Started at Facebook (2007), Apache 2008.',
    'Three parts: <b>files in HDFS</b>, a <b>metastore</b> (table definitions), a <b>compiler + engine</b> (Tez on YARN).',
    '<b>Schema on read</b>: bad values read as NULL; always count NULLs.',
    '<b>OLAP, not OLTP</b>: high start-up latency, high throughput; no point lookups.',
    '<b>EXTERNAL</b> table: DROP removes only metadata. <b>Managed</b> table: Hive owns the files.',
    'Access: <b>Beeline</b> (JDBC to HiveServer2, port 10000), BI tools, scheduled scripts.',
    'Alternatives: Spark SQL, Trino/Presto, Impala, cloud warehouses. They often share the Hive Metastore.',
    'Versions: Tez + ORC (2013–14), LLAP (Hive 2), ACID default managed tables (Hive 3), Iceberg support (Hive 4).',
]
FAQ = [
    ('Is Hive a database?', 'Not in the usual sense. Hive keeps table definitions in a metastore (a small relational database) but stores the data as files in HDFS or cloud storage, and it has no query engine of its own beyond the compiler: queries run as distributed jobs. It is best described as a data-warehouse system on Hadoop that provides SQL access.'),
    ('Who created Hive and why?', 'A team at Facebook built it around 2007 so that analysts who knew SQL could query very large datasets on Hadoop without writing Java MapReduce programs. It was contributed to the Apache Software Foundation in 2008 and became a top-level Apache project in 2010.'),
    ('Why are Hive queries slow for small data?', 'Every query has fixed costs: compiling, requesting containers from YARN, starting tasks and writing results. For a few megabytes these costs dominate. For terabytes they are negligible compared with the parallel scan time.'),
    ('What is the difference between Hive and HBase?', 'Hive provides SQL-style analytics over files and is batch-oriented. HBase is a NoSQL, column-family store with fast random reads and writes by key. They solve different problems, and Hive can even query HBase tables through a storage handler.'),
    ('Does Hive still matter when Spark and cloud warehouses exist?', 'Yes, in two ways. Many large organisations still run Hive for batch ETL and as the shared SQL layer on Hadoop-style data lakes, and the Hive Metastore has become the common table catalogue for Spark, Trino, Impala and cloud services. Knowing Hive therefore helps with all of them.'),
]

PRACTICE_INTRO = 'Programs about schema on read, NULLs, tool choice and latency: the ideas you need before writing real HiveQL in Module 2.'
PROBLEMS = [
    dict(level='easy', title='Parse a row', stmt='Parse the line “5,Pune,220” using the schema int, str, int and print the typed values.', inp='"5,Pune,220"',
         code='''schema = [int, str, int]
print([t(v) for t, v in zip(schema, "5,Pune,220".split(","))])
''', explain='Each raw string is converted by the matching type: this is what a SerDe does for every row.'),
    dict(level='easy', title='Table or files?', stmt='A metastore says orders is at /data/orders. List which of these files belong to the table.', inp='/data/orders/p0, /data/orders/p1, /data/other/p0',
         code='''files = ["/data/orders/p0", "/data/orders/p1", "/data/other/p0"]
print([f for f in files if f.startswith("/data/orders/")])
''', explain='A table is just a folder. Anything in that folder is part of the table; files elsewhere are not.'),
    dict(level='easy', title='External drop', stmt='After DROP TABLE on an external table, are the files still there? Simulate with a dict and a list.', inp='metastore {orders}, files [p0, p1]',
         code='''metastore = {"orders": "/data/orders"}
files = ["p0", "p1"]
del metastore["orders"]
print("tables:", len(metastore), "| files:", len(files))
''', explain='The metastore entry is gone; the files are untouched. For a managed table the files would be deleted too.'),
    dict(level='medium', title='NULL percentage', stmt='Given amounts as text, print the percentage that read as NULL.', inp='["220", "x", "150", "", "90", "60", "n/a", "75"]',
         code='''vals = ["220", "x", "150", "", "90", "60", "n/a", "75"]
def ok(v):
    try:
        int(v); return True
    except ValueError:
        return False
bad = sum(1 for v in vals if not ok(v))
print(f"{bad} of {len(vals)} are NULL = {100 * bad / len(vals):.1f}%")
''', explain='3 of 8, 37.5%. A data-quality rule might alert above 1%.'),
    dict(level='medium', title='Pick a tool', stmt='Write a function that returns "Hive" for large scans, otherwise "RDBMS/NoSQL", and test three workloads.', inp='(10, "scan"), (10, "lookup"), (0.1, "scan")',
         code='''def pick(tb, style):
    return "Hive" if tb >= 1 and style == "scan" else "RDBMS/NoSQL"
for w in [(10, "scan"), (10, "lookup"), (0.1, "scan")]:
    print(w, "->", pick(*w))
''', explain='Small data fits comfortably in a normal database even for scans. Lookups are an RDBMS/NoSQL job at any size.'),
    dict(level='medium', title='Break-even size', stmt='Hive costs 15 s + size/2 GB/s; a database costs size/0.2 GB/s. Find the smallest whole number of GB where Hive is faster.', inp='15 + g/2 < g/0.2',
         code='''g = 1
while not (15 + g / 2.0 < g / 0.2):
    g += 1
print("Hive wins from", g, "GB")
''', explain='From 4 GB (4 GB: Hive 17 s vs database 20 s). Below that the start-up cost is not worth it. (Illustrative model.)'),
    dict(level='business', title='Month-end report: where to run it?', stmt='A 3 TB orders table must be summarised every night, and a web page needs single orders in under 100 ms. Decide where each workload runs and print the reason.', inp='3 TB nightly summary; 100 ms point lookups',
         code='''jobs = [("nightly summary", "scan", "Hive: large scan, batch, results ready by morning"),
        ("order page lookup", "lookup", "MySQL/NoSQL: needs milliseconds")]
for name, style, why in jobs:
    print(name, "->", why)
''', explain='This is how real platforms are built: an operational store serves the app, and a Hive (or similar) layer analyses the same orders in batch.'),
    dict(level='business', title='Cost of a bad feed', stmt='A feed of 1,000,000 orders averaging Rs 250 has 2% of amounts unparseable (read as NULL). How much revenue does SUM miss?', inp='1,000,000 orders · Rs 250 · 2% NULL',
         code='''orders, avg, bad = 1_000_000, 250, 0.02
print("missing revenue: Rs", int(orders * bad * avg))
''', explain='Rs 50,00,000 silently missing from the report. Schema on read is flexible, but it makes NULL checks a mandatory part of every pipeline.'),
]

SCN_INTRO = 'Typical “what is Hive and when would you use it?” questions, as company interviewers ask them.'
SCENARIOS = (
    scn('Any company · concepts', 'Fresher', '“Is Hive a database?”',
        'The interviewer asks: “Hive has tables and SQL, so it is a database, right?”',
        'do you separate metadata, storage and compute?',
        '''<ul>
          <li>Hive stores table <b>definitions</b> in a metastore; the <b>data</b> stays as files in HDFS or cloud storage.</li>
          <li>Queries are compiled into distributed jobs on Tez/YARN, so latency is seconds to minutes, not milliseconds.</li>
          <li>So it is a data-warehouse layer providing SQL on Hadoop, not an OLTP database.</li>
        </ul>''', 'a flat “yes” or “no” without explaining the difference.') +
    scn('Data platform · design', 'Mid-level', 'Dashboards are slow',
        'A manager says: “Our Tableau dashboards on Hive take 40 seconds per click. Is Hive bad?”',
        'do you understand latency vs throughput and know the options?',
        '''<ol>
          <li>Hive on Tez has start-up overhead per query, so it is not ideal for interactive clicks.</li>
          <li>Options: build summary tables nightly so dashboards read small tables, enable LLAP or caching, use ORC/Parquet with partitioning, or add an interactive engine (Trino, Impala) on the same metastore.</li>
          <li>Keep Hive for the heavy batch transformations.</li>
        </ol>''', 'rewriting everything in another tool without first measuring where the time goes.') +
    scn('Any company · concepts', 'Fresher', 'A bad value in a Hive table',
        'A file has “abc” in a numeric column. A colleague expects the load to fail.',
        'do you know schema on read?',
        '''<ul>
          <li>Hive does not validate on write. The file is stored unchanged; at read time the value cannot be parsed and appears as NULL.</li>
          <li>Aggregates like SUM ignore NULLs, so totals can be silently low.</li>
          <li>Therefore: validate in the pipeline, count NULLs per column and compare with history.</li>
        </ul>''', 'saying “Hive rejects the row”.') +
    scn('Operations · migration', 'Mid-level', 'Moving to the cloud',
        'The company will move HDFS data to S3 or another cloud store. Will analysts need to rewrite their Hive tables and queries?',
        'do you understand the role of the metastore and table locations?',
        '''<ul>
          <li>Table definitions live in the metastore; the data location is one property of each table.</li>
          <li>Copy the data to object storage, then change the table location (or recreate external tables) to point to it. Queries stay the same.</li>
          <li>Check file-format, permission and consistency differences of the object store, and test performance.</li>
        </ul>''', 'promising “no changes at all”; locations, security and performance still need work.')
)
