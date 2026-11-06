import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='05-reading-and-writing-data', lesson='04-jdbc-xml-and-other-sources', n='5.4',
    module_label='Module 5 · Reading and writing data',
    title='JDBC, XML and other sources',
    desc='Spark and PostgreSQL 16 over JDBC with PySpark 4.3.0: a connection refused for the JVM time zone Asia/Calcutta, writing 1M orders with batchsize, a plain read in one partition, a parallel read whose generated WHERE clauses we logged, skew from bounds ([0, 375000, 625000, 0]) and bounds that do not filter (all 1M rows in the last partition), filter pushdown visible in the database log, the query option, plus the built-in XML source of Spark 4, text and binaryFile.',
    og_desc='Our "parallel" JDBC read put all 1,000,000 rows in one partition: bounds do not filter. JDBC, XML and other sources in Spark, tested against PostgreSQL 16.',
    minutes=32, level='Intermediate',
    lead='Much business data lives in relational databases. This lesson connects Spark to PostgreSQL, shows exactly which SQL Spark sends, and how to read in parallel without skew or overloading the database. Then it reads XML, now built into Spark 4, and text and binary files. <b>All outputs are real</b> (PySpark 4.3.0, PostgreSQL 16).',
    chips=['PySpark 4.3.0 + PostgreSQL 16', 'Generated SQL logged', 'XML built in (Spark 4)', 'Runs in your browser (Python)'],
)

MAIN = '''# The WHERE clauses Spark generates for a partitioned JDBC read
def strides(column, lower, upper, n):
    step = (upper - lower) // n
    cuts = [lower + step * k for k in range(1, n)]
    clauses = [f'"{column}" < {cuts[0]} or "{column}" is null']
    for a, b in zip(cuts, cuts[1:]):
        clauses.append(f'"{column}" >= {a} AND "{column}" < {b}')
    clauses.append(f'"{column}" >= {cuts[-1]}')
    return clauses

for w in strides("order_id", 1_000_000, 6_000_000, 4):
    print("WHERE", w)
'''
RUN = dict(
    heading='Run the code: the SQL behind a parallel read',
    intro='<p>A model that reproduces the WHERE clauses from the PostgreSQL log in Step 3. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    clauses = [f\'"{column}" < {cuts[0]} or "{column}" is null\']', 'The first partition also takes everything below the lower bound, and nulls.'),
        ('    clauses.append(f\'"{column}" >= {cuts[-1]}\')', 'The last takes everything above the upper bound: bounds never filter.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Compare with Step 3’s log. Then try bounds 1M–2M.', code=None),
        dict(label='2 · Predict first: skew', hint='<b>Predict first:</b> ids are 2.25M–4.75M. Which partitions get rows?',
             code='''cuts = [2_250_000, 3_500_000, 4_750_000]
ids = range(2_250_000, 4_750_000, 250_000)
def part(i):
    return sum(i >= c for c in cuts)
print([part(i) for i in ids])
'''),
        dict(label='3 · Good bounds', hint='Use the real min and max.',
             code='''lo, hi, n = 2_250_000, 4_750_000, 4
step = (hi - lo) // n
print([(lo + k * step, lo + (k + 1) * step) for k in range(n)])
'''),
        dict(label='4 · Pushdown', hint='Build the SQL Spark sends for a filter.',
             code='''filters = ['"city" = \\'Pune\\'', '"amount" > 800']
print("SELECT order_id, amount FROM orders WHERE " + " AND ".join(f"({f})" for f in filters))
'''),
        dict(label='5 · Spot the error', hint='This read uses 200 partitions on the primary database.', expect='error',
             code='''job = {"numPartitions": 200, "target": "primary"}
assert job["numPartitions"] <= 16 and job["target"] == "replica", "200 concurrent connections on the primary: use a replica and an agreed connection budget"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: JDBC and XML',
    intro='<p>Start <code>pyspark --jars postgresql-42.7.4.jar --driver-java-options -Duser.timezone=Asia/Kolkata</code>. <b>Outputs are real</b> (PySpark 4.3.0, PostgreSQL 16).</p>',
    items=[
        dict(title='1 · One partition', cmd='spark.read.jdbc(URL, "orders", properties=PROPS).rdd.getNumPartitions()', file='pyspark',
             output='1', note='Add partition options for parallelism.'),
        dict(title='2 · Bounds do not filter', cmd='n = spark.read.jdbc(URL, "orders", column="order_id", lowerBound=1_000_000,\n    upperBound=2_000_000, numPartitions=4, properties=PROPS)\nn.count(), n.rdd.glom().map(len).collect()', file='pyspark',
             output='(1000000, [0, 0, 0, 1000000])', note='All rows in the last partition.'),
        dict(title='3 · XML', cmd='spark.read.option("rowTag", "restaurant").xml("menu.xml").columns', file='pyspark',
             output="['_city', '_id', 'dish', 'name']", note='Attributes get an underscore.'),
    ],
)

TRACE = dict(
    heading='Which partition does a row go to?',
    intro='<p>Follow rows through the generated ranges.</p>',
    code='''cuts = [1_250_000, 1_500_000, 1_750_000]    # bounds 1M-2M, 4 partitions
for oid in (2_300_000, 3_900_000, 4_700_000):
    p = sum(oid >= c for c in cuts)
    print(oid, "-> partition", p)
''',
    notes={1: 'Bounds :: Only used to compute these cut points.', 3: 'Last range :: Every id above 1.75M lands in partition 3.'},
)

WORKED_INTRO = 'Three database tasks at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='JDBC · basics', title='Read a small lookup table',
         problem='<p>Read the restaurants table from PostgreSQL.</p>',
         inp='a few thousand rows',
         approach=['Driver jar on the classpath.', 'URL and properties.', 'One partition is fine.'],
         code='''print("""rest = spark.read.jdbc("jdbc:postgresql://db:5432/tiffingo", "restaurants",
                     properties={"user": "etl", "password": secret, "driver": "org.postgresql.Driver"})""")
''', notes={1: 'Secrets :: Read passwords from a secret store, not code.'},
         tryit='Step 2.'),
    dict(level='i', tag='JDBC · parallel', title='Copy a big table in parallel',
         problem='<p>Copy 200M orders quickly without skew.</p>',
         inp='order_id from 1 to ~210M',
         approach=['Query min/max on the replica.', 'Bounds = min/max.', 'numPartitions from the connection budget.'],
         code='''lo, hi, n = 1, 210_000_000, 16
print(f"lowerBound={lo}, upperBound={hi}, numPartitions={n}, about {(hi - lo) // n:,} ids per query")
''', notes={1: 'Even :: Real bounds give even ranges if ids are dense.'},
         tryit='Step 3–4: skew from wrong bounds.'),
    dict(level='a', tag='JDBC · design', title='Let the database aggregate',
         problem='<p>Daily revenue by city from an indexed table.</p>',
         inp='orders with an index on order_date',
         approach=['query option with GROUP BY.', 'Only small results cross the network.', 'Or pushDownAggregate.'],
         code='''print("""spark.read.format("jdbc").option("url", URL).options(**PROPS) \\
  .option("query", "SELECT city, sum(amount) revenue FROM orders WHERE order_date = CURRENT_DATE GROUP BY city").load()""")
''', notes={2: 'Small :: 8 rows instead of a million.'},
         tryit='Step 5.'),
]

QUIZ = mix([
    dict(q='Beginner: How many partitions does a plain JDBC read have?', options=['200', '1', 'One per core', 'One per table column'], answer=1,
         why='One task, one connection.'),
    dict(q='Beginner: What must be on the classpath for JDBC?', options=['Avro jar', 'The database’s JDBC driver', 'Hive', 'Nothing'], answer=1,
         why='e.g. postgresql-42.7.4.jar.'),
    dict(q='Beginner: Which Spark version made XML built in?', options=['2.4', '3.5', '4.0', 'Never'], answer=2,
         why='rowTag option.'),
    dict(q='Intermediate: Do lowerBound/upperBound filter rows?', options=['Yes', 'No, they only set the stride', 'Only lowerBound', 'Only on PostgreSQL'], answer=1,
         why='All 1M rows came back.'),
    dict(q='Intermediate: What does numPartitions also limit?', options=['Memory', 'Concurrent JDBC connections', 'Shuffle partitions', 'Files'], answer=1,
         why='Protect the database.'),
    dict(q='Intermediate: How did a filter reach PostgreSQL?', options=['It did not', 'As a WHERE clause (pushdown)', 'As a view', 'As a trigger'], answer=1,
         why='Seen in the statement log.'),
    dict(q='Advanced: Why did our first connection fail?', options=['Wrong password', 'JVM time zone Asia/Calcutta rejected', 'No driver', 'Firewall'], answer=1,
         why='Fixed with -Duser.timezone=Asia/Kolkata.'),
    dict(q='Advanced: Bounds 1M–6M, ids 2.25M–4.75M, 4 partitions. Rows per partition?', options=['Even', '[0, 375k, 625k, 0]', 'All in first', 'All in last'], answer=1,
         why='Ranges did not match the data.'),
])

REVISION = [
    'JDBC: driver jar + URL + properties; <code>dbtable</code> or <code>query</code>.',
    'Plain read = <b>1 partition, 1 connection</b>.',
    'Parallel: <code>partitionColumn</code>, bounds, <code>numPartitions</code>; one range query per task.',
    'Bounds <b>do not filter</b>: use real min/max (wrong bounds put 1M rows in one partition).',
    '<code>numPartitions</code> = concurrent connections: use replicas and a budget.',
    'Filters (and V2 aggregates/limits) are pushed down as SQL; <code>batchsize</code>/<code>fetchsize</code> for throughput.',
    'Spark 4: built-in XML (<code>rowTag</code>, attributes as <code>_attr</code>); <code>text</code>, <code>binaryFile</code>.',
]
FAQ = [
    ('Can I partition on a string column?', 'partitionColumn must be numeric, date or timestamp. For others, pass your own list of predicates (<code>predicates=[…]</code> in <code>spark.read.jdbc</code>) or partition on a hash expression in a subquery.'),
    ('How do I copy only new rows?', 'Filter on an updated_at or id watermark (pushed down), or use change data capture (Debezium → Kafka) for continuous sync.'),
    ('Does overwrite drop my table?', 'By default overwrite drops and recreates it with Spark’s types. Create the table yourself and use truncate=true where the dialect supports it, or write to a staging table and swap.'),
    ('Is Spark a good tool for writing to OLTP databases?', 'For bulk loads of results, yes, with modest parallelism and batching. For per-event updates, use the application or a streaming sink designed for it.'),
    ('Do I still need spark-xml from Databricks?', 'Not on Spark 4.0+, where XML is built in with similar options (rowTag, attributePrefix, valueTag).'),
]

PRACTICE_INTRO = 'Programs about JDBC ranges, connections and sources.'
PROBLEMS = [
    dict(level='easy', title='Stride', stmt='Stride for bounds 1M–6M and 4 partitions.', inp='lower, upper, n',
         code='''print((6_000_000 - 1_000_000) // 4)
''', explain='1.25M ids per range.'),
    dict(level='easy', title='Batch saving', stmt='Percent saved with batchsize 10,000.', inp='34.1 vs 27.9 s',
         code='''print(f"{1 - 27.9 / 34.1:.0%}")
''', explain='Fewer round trips.'),
    dict(level='easy', title='Rows transferred', stmt='Share of rows sent after pushdown.', inp='17,621 of 1,000,000',
         code='''print(f"{17621 / 1_000_000:.1%}")
''', explain='The database filtered the rest.'),
    dict(level='medium', title='Partition of a row', stmt='Partition index for an id.', inp='cuts 2.25M, 3.5M, 4.75M',
         code='''cuts = [2_250_000, 3_500_000, 4_750_000]
print(sum(3_900_000 >= c for c in cuts))
''', explain='Partition 2.'),
    dict(level='medium', title='Even bounds', stmt='Ranges for 8 partitions between real min and max.', inp='2.25M–4.75M',
         code='''lo, hi, n = 2_250_000, 4_750_000, 8
s = (hi - lo) // n
print([lo + k * s for k in range(n + 1)])
''', explain='Even split if ids are dense.'),
    dict(level='medium', title='XML attributes', stmt='Field names Spark gives XML attributes.', inp='id, city',
         code='''print(["_" + a for a in ("id", "city")])
''', explain='attributePrefix defaults to _.'),
    dict(level='business', title='Copy time', stmt='Time with 16 even partitions if one task takes 60 min.', inp='ideal speed-up',
         code='''print(60 / 16, "minutes (ideal)")
''', explain='Real gains depend on the database.'),
    dict(level='business', title='Connection budget', stmt='Max partitions if the DB allows 50 extra connections and 3 jobs run together.', inp='50, 3',
         code='''print(50 // 3, "partitions per job")
''', explain='Agree it with the DBAs.'),
]

SCN_INTRO = 'JDBC questions show whether you have moved real data out of production databases.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“How do you read from MySQL/PostgreSQL?”',
        'Read a database table into Spark.',
        'do you know the basics?',
        '<p>Put the JDBC driver jar on the classpath, then <code>spark.read.jdbc(url, table, properties={"user", "password", "driver"})</code> or <code>format("jdbc")</code> with <code>dbtable</code>/<code>query</code>. For big tables I add partitionColumn, bounds and numPartitions.</p>', 'Not mentioning the driver.') +
    scn('Data engineering', 'Mid-level', 'Parallel read still slow',
        'A partitioned JDBC read has one long-running task.',
        'do you understand bounds?',
        '''<ul>
          <li>Bounds only set the stride; values outside go to the first/last partition.</li>
          <li>Use real min/max; pick an evenly distributed column.</li>
          <li>In my test wrong bounds put all 1M rows in the last partition.</li>
        </ul>''', 'Raising numPartitions.') +
    scn('Data engineering', 'Mid-level', 'Reduce data transferred',
        'Only Pune orders above ₹800 are needed from a large table.',
        'do you know pushdown?',
        '''<ol>
          <li>Apply where() on the JDBC DataFrame; Spark pushes it as SQL.</li>
          <li>Check PushedFilters in explain() or the DB log.</li>
          <li>Or use the query option for aggregations.</li>
        </ol>''', 'Reading everything and filtering in Spark.') +
    scn('Platform', 'Senior', 'Safe extraction',
        'Design nightly extraction from 20 production databases.',
        'can you protect source systems?',
        '''<ul>
          <li>Replicas or snapshots, connection budgets per DB, off-peak schedules.</li>
          <li>Incremental loads by watermark, or CDC into Kafka.</li>
          <li>Secrets in a vault, explicit time zones, monitoring of DB load.</li>
        </ul>''', 'Full copies of every table with maximum parallelism.')
)
