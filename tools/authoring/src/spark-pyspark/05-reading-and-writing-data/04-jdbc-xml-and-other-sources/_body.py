import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l54_jdbc.txt'
def sec(a, b=None, drop=()):
    s = capsec(C, a, b, drop)
    s = re.sub(r'#\d+L?', '', s)
    return '\n'.join(l if len(l) <= 140 else l[:137] + ' …' for l in s.split('\n'))
XML = open(os.path.join(HERE, '..', '..', 'lab', 'data_m5_menu.xml')).read().rstrip()

def db(x, y, label='PostgreSQL', tone='card'):
    return cyl(x, y, 80, 70, label, tone, 8)

def jdbc_pic(n=1, hi=None, conns=None):
    o = db(10, 30, 'Postgres', 'blue')
    for k in range(n):
        yy = 22 + k * 28 if n > 1 else 52
        o += arrow(92, 65, 200, yy + 10, 'ink3', 1.0) + opbox(204, yy, f'task {k + 1}', (conns[k] if conns else ''), 'green' if hi is None or k in hi else 'card', 140, 25 if n > 1 else 26)
    return o

# ---------------------------------------------------------------- story
sc_ = (jdbc_pic(4, None, ['id < 2.25M', '2.25M–3.5M', '3.5M–4.75M', '≥ 4.75M']) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured (1M orders)', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('TimeZone "Asia/Calcutta": FATAL', 'red'), ('plain JDBC read: 1 partition', 'amber'),
           ('4 partitions: [0,375k,625k,0]', 'amber'), ('narrow bounds: [0,0,0,1M]', 'red'),
           ('filter pushed: WHERE city = Pune', 'green'), ('XML: built in, rowTag', 'green')])))
scene_svg = scene('JDBC reads and writes relational databases; XML, text and binary files are other built-in sources. We loaded a million orders into PostgreSQL 16, read them back serially and in parallel, logged the SQL Spark sent, and read an XML menu.', sc_,
                  'One JDBC connection unless you <tspan font-weight="700" class="s-acc">partition</tspan>; bounds only set the <tspan font-weight="700" class="s-acc">stride</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“A 32-core cluster, and the database load is one task”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s order service runs on PostgreSQL. Every night a Spark job copies the orders table into the lake. The job runs on 32 cores, yet the Spark UI shows a single task reading for an hour. When Arjun Sir added a partitioned read, three tasks finished in seconds and one ran as long as before.</p>

{scene_svg}

K> Sir, Spark is parallel. Why does it read a database with one task?
A> Because Spark cannot guess how to split an SQL table. Unless you give a numeric <b>partition column</b>, bounds and a number of partitions, it opens <b>one connection</b> and runs one query.
R> And the one slow task after partitioning?
A> The bounds you give only decide where the ranges are cut; they do not filter rows. If the bounds do not match the data, one range gets almost everything. Today we write and read PostgreSQL, watch the SQL Spark sends, test pushdown, then read XML, text and binary files. All outputs are real (PySpark 4.3.0, PostgreSQL 16).
  </div>
</section>
'''

lv = '''
LEVELS> Databases and other sources at three levels
L1> Copying a library catalogue
      <ul>
        <li>One clerk copying the whole catalogue is slow. Four clerks can split it: A–F, G–M, N–S, T–Z.</li>
        <li>If you say “split from A to F” but most books start with Z, the last clerk does all the work.</li>
        <li>Asking the librarian for “only Pune books” is faster than copying all and throwing most away.</li>
      </ul>
L2> The API
      <ul>
        <li><code>spark.read.jdbc(url, table, properties=…)</code> or <code>format("jdbc")</code> with <code>dbtable</code> or <code>query</code>; parallel: <code>column</code>/<code>partitionColumn</code>, <code>lowerBound</code>, <code>upperBound</code>, <code>numPartitions</code>; also <code>fetchsize</code>, <code>batchsize</code>.</li>
        <li>The JDBC driver jar must be on the classpath (<code>--jars</code> or <code>--packages</code>).</li>
        <li>XML is built in since Spark 4.0: <code>spark.read.option("rowTag", "restaurant").xml(path)</code>. Also <code>text</code>, <code>binaryFile</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>The first connection failed: PostgreSQL 16 rejected the JVM time zone <code>Asia/Calcutta</code>; <code>-Duser.timezone=Asia/Kolkata</code> fixed it.</li>
        <li>A plain read was 1 partition. With bounds 1M–6M and 4 partitions the rows split [0, 375,000, 625,000, 0]; with bounds 1M–2M all 1,000,000 rows went to the last partition.</li>
        <li>A filter became <code>WHERE ("city" = 'Pune') AND ("amount" &gt; 800)</code> in PostgreSQL’s log.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>JDBC and other built-in sources</h2>
''' + def_block(
    'The <b>JDBC data source</b> reads tables or query results from relational databases into DataFrames and writes DataFrames to tables, using the database’s JDBC driver. A read is a single partition and a single connection unless <code>partitionColumn</code>, <code>lowerBound</code>, <code>upperBound</code> and <code>numPartitions</code> are given; Spark then issues one query per partition with a range predicate on the partition column, where the bounds only define the partition stride and <b>do not filter</b> the rows. <code>numPartitions</code> also caps concurrent connections for reads and writes. Filters, column selections, and in the V2 path aggregates and limits, are <b>pushed down</b> into the generated SQL when possible. Spark 4.0 added a built-in <b>XML</b> source (<code>rowTag</code> selects the element that forms a row, attributes become <code>_</code>-prefixed fields); other built-in sources include <code>text</code> (one row per line) and <code>binaryFile</code> (one row per file with path, modification time, length and content).',
    'JDBC lets Spark talk to databases like PostgreSQL and MySQL. Tell Spark how to split the table, or it reads with one connection. Filters are sent to the database. Spark 4 can also read XML directly, plus plain text and whole binary files.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('JDBC URL', '<code>jdbc:postgresql://host:5432/db</code>.'),
    ('JDBC driver', 'The database’s jar, e.g. postgresql-42.7.4.jar.'),
    ('dbtable / query', 'A table (or subquery) / a query to read.'),
    ('partitionColumn', 'Numeric, date or timestamp column to split on.'),
    ('lower/upperBound', 'Where ranges are cut; not a filter.'),
    ('numPartitions', 'Parallel queries and max connections.'),
    ('fetchsize / batchsize', 'Rows per round trip for reads / writes.'),
    ('rowTag', 'The XML element that becomes one row.'),
]) + '''

  <h3>Read options that matter</h3>
''' + table(['Option', 'Default', 'Effect'], [
    ['<code>partitionColumn</code> + bounds + <code>numPartitions</code>', 'none', 'Without them: 1 partition, 1 connection'],
    ['<code>fetchsize</code>', '0 (driver default)', 'Some drivers fetch everything into memory unless set'],
    ['<code>batchsize</code> (write)', '1000', '10,000 cut our write from 34.1 to 27.9 s'],
    ['<code>pushDownPredicate</code>', 'true', 'Filters run in the database'],
    ['<code>pushDownAggregate</code> / <code>pushDownLimit</code>', 'true (V2)', 'Aggregates and limits pushed when supported'],
    ['<code>query</code>', 'none', 'Let the database compute (cannot be combined with partitionColumn)'],
    ['<code>truncate</code> (write)', 'false', 'Overwrite by TRUNCATE instead of DROP, where the dialect supports it'],
], minw=680) + lv + '''
EXAM> “How do you read a large table from a database in parallel?” Use a numeric, evenly distributed column as <code>partitionColumn</code>, set <code>lowerBound</code>/<code>upperBound</code> to its real min and max (query them first) and <code>numPartitions</code> to what the database can handle; remember the bounds do not filter, so wrong bounds create skewed partitions. Push filters down and consider reading from a replica.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Other sources in the box</h2>
''' + table(['Source', 'Read', 'One row is', 'Lab'], [
    ['XML (Spark 4.0+)', '<code>spark.read.option("rowTag", "restaurant").xml(p)</code>', 'One element', '3 restaurants, dishes as array of structs'],
    ['text', '<code>spark.read.text(p)</code>', 'One line, column <code>value</code>', '24,000 review lines'],
    ['binaryFile', '<code>spark.read.format("binaryFile").load(p)</code>', 'One file: path, modificationTime, length, content', 'menu.xml, 474 bytes'],
    ['Hive tables', '<code>spark.table("db.t")</code>', 'Table row', 'Lesson 7.2'],
    ['Kafka', '<code>spark.readStream.format("kafka")</code>', 'One message', 'Module 9'],
    ['Delta / Iceberg', '<code>format("delta")</code> (package)', 'Table row', 'Lesson 11.5'],
], minw=700) + '''
WARN> A parallel JDBC read opens <code>numPartitions</code> connections at once against a production database. Agree the number with the database owners, read from a replica where possible, and never point a 200-task Spark job at a primary OLTP database.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>PostgreSQL, XML and friends</h2>
  <p>All outputs are real: PySpark 4.3.0 in local mode with 4 cores, <code>postgresql-42.7.4.jar</code>, PostgreSQL 16 in Docker with <code>log_statement = 'all'</code> so we can read the SQL Spark sends.</p>
''' + stepper([
    ('Step 1 · Writing 1M orders to PostgreSQL',
     code('python', 'l54_jdbc.py', 'URL = "jdbc:postgresql://localhost:5433/tiffingo"\nPROPS = {"user": "postgres", "password": "…", "driver": "org.postgresql.Driver"}\nfor bs in (1000, 10000):\n    orders.repartition(4).write.mode("overwrite").jdbc(URL, "orders", properties={**PROPS, "batchsize": str(bs)})', sec('== 1)', '== 2)')),
     'The first attempt failed before writing a row: the JVM reported the old time-zone name <code>Asia/Calcutta</code> and PostgreSQL 16 refused it. Starting the driver with <code>-Duser.timezone=Asia/Kolkata</code> fixed it, a real problem on Indian machines. Then 4 tasks inserted 1M rows; larger batches saved 18%. Spark created the table itself (<code>text</code> for strings): create tables yourself when types and indexes matter.'),
    ('Step 2 · A plain read is one partition',
     code('python', 'l54_jdbc.py', 'd = spark.read.jdbc(URL, "orders", properties=PROPS)\nd.rdd.getNumPartitions()\nd.agg(F.sum("amount")).first()', sec('== 2)', '== 3)')),
     'One partition means one task, one connection, one query (<code>SELECT … FROM orders</code>), whatever the cluster size. Fine for small tables; for big ones this is the one-hour single task of our story.'),
    ('Step 3 · A parallel read, and its SQL',
     code('python', 'l54_jdbc.py', 'p = spark.read.jdbc(URL, "orders", column="order_id", lowerBound=1_000_000,\n                   upperBound=6_000_000, numPartitions=4, properties=PROPS)\np.agg(F.sum("amount")).first()\n# WHERE clauses from the PostgreSQL log\np.rdd.glom().map(len).collect()', sec('== 3)', '== 4)')),
     'Spark divided 1M–6M into four strides of 1.25M and sent four queries. The first range also takes values below the lower bound and nulls, the last everything above the upper bound. Our million orders had ids between 2.25M and 4.75M, so two partitions were <b>empty</b> and the work split 375,000 / 625,000. Query <code>min</code> and <code>max</code> first and use them as bounds.'),
    ('Step 4 · Bounds do not filter',
     code('python', 'l54_jdbc.py', 'narrow = spark.read.jdbc(URL, "orders", column="order_id", lowerBound=1_000_000,\n                        upperBound=2_000_000, numPartitions=4, properties=PROPS)\nnarrow.count(); narrow.rdd.glom().map(len).collect()', sec('== 4)', '== 5)')),
     'Many people expect bounds to filter. They do not: all <b>1,000,000</b> rows came back, but every one landed in the last partition (<code>order_id &gt;= 1,750,000</code>), so the “parallel” read was serial again. This is the slow last task of our story. To filter, use <code>where</code> (pushed down) or a subquery in <code>dbtable</code>.'),
    ('Step 5 · Pushdown and the query option',
     code('python', 'l54_jdbc.py', 'f = d.where("city = \'Pune\' AND amount > 800").select("order_id", "amount")\nf.explain(); f.count()\n# SQL from the PostgreSQL log\nspark.read.format("jdbc").option("query", "SELECT city, sum(amount) AS revenue FROM orders GROUP BY city")…', sec('== 5)', '== 7)')),
     'The plan marks pushed filters with <code>*</code>, and PostgreSQL received exactly that <code>WHERE</code> clause; for a <code>count()</code> Spark even asked only for <code>SELECT 1</code>. Only 17,621 rows crossed the network. With the <code>query</code> option the database did the whole aggregation and returned 8 rows. Push work to the database when it has indexes and the result is small.'),
    ('Step 6 · XML, text and binaryFile',
     code('xml', 'menu.xml', XML) + code('python', 'l54_jdbc.py', 'x = spark.read.option("rowTag", "restaurant").xml(".../menu.xml")\nx.printSchema()\nx.select("_id", "_city", "name", F.size("dish").alias("dishes")).show()\nx.select("name", F.explode("dish").alias("d")).select("name", "d._veg", "d.title", "d.price").show()\nspark.read.text(".../reviews"); spark.read.format("binaryFile").load(".../m5/*.{csv,xml,jsonl}")', sec('== 7)')),
     'No extra package: XML is built into Spark 4. Each <code>&lt;restaurant&gt;</code> became a row; attributes became <code>_id</code> and <code>_city</code>; repeated <code>&lt;dish&gt;</code> elements became an array of structs. A restaurant without dishes got a null array (size NULL). <code>text</code> gives one row per line; <code>binaryFile</code> one row per file with its bytes, useful for images or PDFs.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('TimeZone "Asia/Calcutta": FATAL', RD), ('-Duser.timezone=Asia/Kolkata', G), ('batchsize 10000: 27.9 s', W)], size=7.4),
    term([('plain read: 1 partition', Y), ('sum in 1.4 s', W)], size=7.6),
    term([('4 partitions, bounds 1M–6M', W), ('rows: [0, 375000, 625000, 0]', Y)], size=7.4),
    term([('bounds 1M–2M', W), ('rows: 1,000,000 (not filtered)', Y), ('[0, 0, 0, 1000000]', RD)], size=7.4),
    term([('PushedFilters: *EqualTo(city,Pune)', G), ('SQL: WHERE ("city" = \'Pune\') …', G), ('rows: 17,621', W)], size=7.2),
]
B1 = [
    t(180, 14, 'Driver jar, URL, time zone', 9.4, bold=True) + db(20, 32) + flow([('JDBC driver', 'jar', 'violet'), ('session', 'TimeZone', 'acc')], x0=130, y=52, w=96, gap=18) + cap('The JVM time zone is sent to the DB.', '', 'amber', y=144, h=30),
    t(180, 14, 'One query, one task', 9.4, bold=True) + jdbc_pic(1) + cap('No partitionColumn: no parallelism.', '', 'amber', y=144, h=30),
    t(180, 14, 'One range query per task', 9.4, bold=True) + jdbc_pic(4, {1, 2}, ['id < 2.25M · 0', '2.25–3.5M · 375k', '3.5–4.75M · 625k', '≥ 4.75M · 0']) + cap('Bounds should match min and max.', '', 'blue', y=144, h=30),
    t(180, 14, 'Wrong bounds: one busy task', 9.4, bold=True) + jdbc_pic(4, {3}, ['id < 1.25M · 0', '1.25–1.5M · 0', '1.5–1.75M · 0', '≥ 1.75M · 1M']) + cap('Bounds cut ranges; they never filter.', '', 'red', y=144, h=30),
    t(180, 14, 'Filters run in the database', 9.4, bold=True) + db(20, 32, 'WHERE', 'green') + arrow(102, 66, 200, 66, 'ink3', 1.1) + opbox(204, 52, '17,621 rows', 'not 1,000,000', 'green', 130, 30) + cap('Less data over the network.', '', 'green', y=144, h=30),
]
see_caps = ['A time-zone name stopped the connection.', 'One partition for the whole table.', 'Two of four partitions were empty.', 'All rows in the last partition.', 'The filter reached PostgreSQL.']
behind_caps = ['JDBC session settings come from the JVM.', 'Spark cannot guess how to split SQL.', 'Strides from lower to upper bound.', 'Edges catch everything outside.', 'Pushdown rewrites your filter as SQL.']
two = anim_two('JDBC and other sources', 'Talking to a database', 'Real lab outputs', 'Connections and queries', see, B1, see_caps, behind_caps)

# ---- scenario 1: nightly copy
e1 = (t(180, 22, 'Nightly copy: 200M orders', 9.4, bold=True) + t(180, 56, 'spark.read.jdbc(url, "orders")', 8.2, 'ink', mono=True) + cap('One task, one hour.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Add partitionColumn', 9.4, bold=True) + t(180, 56, 'bounds guessed: 1 to 10,000,000', 8.4, 'ink2') + cap('Ids now reach 210M.', '', 'amber', y=150, h=34))
e3 = (t(180, 22, 'Last task gets 95% of rows', 9.4, bold=True) + t(180, 56, 'still almost an hour', 8.4, 'ink2') + cap('Like our Step 4.', '', 'red', y=150, h=34))
e4 = (t(180, 22, 'Query min/max first', 9.4, bold=True) + t(180, 56, 'SELECT min(order_id), max(order_id)', 8.0, 'ink', mono=True) + cap('Bounds from the data.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Incremental instead', 9.4, 'acc', bold=True) + t(180, 56, 'WHERE updated_at > last run (or CDC)', 8.0, 'ink2') + cap('Copy only changes.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'A nightly database copy on one core',
              'Parallel JDBC reads. (Typical; behaviour from our lab.)',
              'JDBC partitioning', 'Without partition options JDBC reads with one task; bounds that do not match the data put all rows in one partition', [e1, e2, e3, e4, e5],
              ['One task.', 'Guessed bounds.', 'Skewed.', 'Real min/max.', 'Incremental.'],
              hid='scenario-jdbc-parallel')

# ---- scenario 2: overloading the DB
b1 = (t(180, 22, 'numPartitions = 200', 9.4, bold=True) + t(180, 56, '“more parallel is faster”', 8.4, 'ink2') + cap('Against the primary DB.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, '200 connections at once', 9.4, bold=True) + t(180, 56, 'checkout API times out', 8.4, 'ink2') + cap('Customers cannot order.', '', 'red', y=150, h=34))
b3 = (t(180, 22, 'Read from a replica', 9.4, bold=True) + t(180, 56, 'reporting copy of the database', 8.4, 'ink2') + cap('Primary untouched.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Agree a connection budget', 9.4, bold=True) + t(180, 56, 'numPartitions = 8, fetchsize 10,000', 8.2, 'ink2') + cap('Predictable load.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Schedule off-peak', 9.4, 'acc', bold=True) + t(180, 56, 'and monitor DB metrics', 8.4, 'ink2') + cap('Shared responsibility.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Spark took down the checkout database',
              'numPartitions is a connection count. (Typical.)',
              'JDBC load', 'numPartitions opens that many concurrent connections; read from replicas with an agreed budget', [b1, b2, b3, b4, b5],
              ['200 partitions.', 'Outage.', 'Replica.', 'Budget.', 'Off-peak.'],
              hid='scenario-jdbc-load')

# ---- scenario 3: time zone
u1 = (t(180, 22, 'Job works on the cloud cluster', 9.4, bold=True) + t(180, 56, 'TZ = UTC', 8.4, 'ink', mono=True) + cap('Fine for months.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'A developer runs it locally', 9.4, bold=True) + t(180, 56, 'JVM default: Asia/Calcutta', 8.4, 'ink', mono=True) + cap('Connection refused.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'FATAL: invalid TimeZone', 9.4, bold=True) + t(180, 56, 'PostgreSQL 16 rejects the old name', 8.4, 'ink2') + cap('Our Step 1.', '', 'red', y=150, h=34))
u4 = (t(180, 22, 'Set it explicitly', 9.4, bold=True) + t(180, 56, '-Duser.timezone=Asia/Kolkata', 8.4, 'ink', mono=True) + cap('Driver and executors.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'And spark.sql.session.timeZone', 9.4, 'acc', bold=True) + t(180, 56, 'timestamps read and written consistently', 8.2, 'ink2') + cap('Same results everywhere.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'It fails only on my laptop',
              'Time zones in JDBC connections. (Behaviour from our lab.)',
              'JDBC time zone', 'The JVM time zone is sent to the database; set user.timezone and the Spark session time zone explicitly', [u1, u2, u3, u4, u5],
              ['UTC cluster.', 'Local JVM.', 'Rejected.', 'Set JVM zone.', 'Session zone.'],
              hid='scenario-timezone')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Talking to a database</h2>
  <p>Left: real outputs. Right: connections and the queries they run.</p>
''' + two + '''
  <p>Three live scenarios follow: a database copy on one core, a read that overloaded the database, and a connection that failed only on a laptop.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Databases and other sources at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'ingest', 11, 'blue', bold=True) + t(60, 58, 'OLTP → lake', 7.4, 'ink2'),
    '1. Database to lake',
    'Order, payment and customer tables are copied nightly or incrementally from replicas into Parquet/Delta.',
    ['Replica', '*parallel JDBC', 'Lake']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'serve', 12, 'green', bold=True) + t(60, 58, 'results', 7.4, 'ink2'),
    '2. Results back to apps',
    'Aggregated recommendations or risk scores are written to PostgreSQL/MySQL tables that apps read.',
    ['Spark result', '*JDBC write', 'App DB']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'XML', 12, 'violet', bold=True) + t(60, 58, 'feeds', 7.4, 'ink2'),
    '3. XML feeds',
    'Banks, insurers and governments still exchange XML; Spark 4 reads it without extra packages.',
    ['XML feed', '*rowTag', 'Table']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'logs', 12, 'acc', bold=True) + t(60, 58, 'text', 7.4, 'ink2'),
    '4. Log files',
    'Plain-text logs are read with spark.read.text and parsed with regexp_extract.',
    ['Logs', '*text + regex', 'Structured']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'images', 11, 'acc', bold=True) + t(60, 58, 'binary', 7.4, 'ink2'),
    '5. Images and documents',
    'binaryFile loads menu photos or invoices with their paths for ML models and OCR.',
    ['Files', '*binaryFile', 'Model input']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> partitions in <a href="../../02-rdds/01-what-is-an-rdd/">2.1</a>, nested data in <a href="../01-csv-and-json/">5.1</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
