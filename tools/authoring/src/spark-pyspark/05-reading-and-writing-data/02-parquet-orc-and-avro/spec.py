import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='05-reading-and-writing-data', lesson='02-parquet-orc-and-avro', n='5.2',
    module_label='Module 5 · Reading and writing data',
    title='Parquet, ORC and Avro',
    desc='5 million orders written as CSV, JSON, Parquet, ORC and Avro with PySpark 4.3.0: sizes from 557 MiB (JSON) to 36 MiB (ORC), a Pune revenue query from 2.74 s to 0.37 s, column pruning (0.46 s vs 0.17 s), row-group skipping that read 80,000 instead of 3.88 million rows on sorted data, the schema stored in the file, mergeSchema for a new column, a type change that cannot be merged, and snappy vs zstd vs gzip compression.',
    og_desc='Same 5M orders: JSON 557 MiB, Parquet 43, ORC 36; the same query 2.74 s vs 0.37 s. Parquet, ORC and Avro, measured.',
    minutes=32, level='Intermediate',
    lead='The file format decides how much data Spark must read. This lesson compares text formats with the columnar formats <b>Parquet</b> and <b>ORC</b> and the row-based binary format <b>Avro</b>, and shows column pruning, predicate pushdown, schema evolution and compression in action. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0 + spark-avro', '5 formats, 5M rows', 'Row groups skipped', 'Runs in your browser (Python)'],
)

MAIN = '''# Row store vs column store: how many values must be read?
rows, cols = 5_000_000, 6
needed_cols = 2                      # city and amount

row_store = rows * cols              # CSV / JSON / Avro read whole rows
col_store = rows * needed_cols       # Parquet / ORC read two columns

print(f"row store   : {row_store:,} values")
print(f"column store: {col_store:,} values")
print(f"ratio       : {row_store / col_store:.0f}x fewer values")
'''
RUN = dict(
    heading='Run the code: why columns help',
    intro='<p>A model of column pruning for our query. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('col_store = rows * needed_cols       # Parquet / ORC read two columns', 'The plan showed FileScan parquet [city, amount].'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then try a table with 60 columns.', code=None),
        dict(label='2 · Predict first: row groups', hint='<b>Predict first:</b> how many row groups can a lookup skip when ids are sorted?',
             code='''groups = [(k * 80_000, (k + 1) * 80_000 - 1) for k in range(10)]
target = 412_345
read = [g for g in groups if g[0] <= target <= g[1]]
print("read", len(read), "of", len(groups), "row groups:", read)
'''),
        dict(label='3 · Size ratios', hint='Compare file sizes from the lab.',
             code='''sizes = {"json": 556.8, "csv": 218.3, "avro": 79.1, "parquet": 42.8, "orc": 36.1}
for k, v in sizes.items():
    print(f"{k:8} {v / sizes['parquet']:4.1f}x parquet")
'''),
        dict(label='4 · Merge schemas', hint='Union of columns across files.',
             code='''oct_cols = ["order_id", "city", "amount"]
nov_cols = ["order_id", "city", "amount", "coupon"]
print(list(dict.fromkeys(oct_cols + nov_cols)))
'''),
        dict(label='5 · Spot the error', hint='This plan gzips Parquet files after writing them.', expect='error',
             code='''plan = "df.write.parquet(path); then gzip every part file"
assert "gzip every" not in plan, "Parquet already compresses per column; external gzip makes files unsplittable and unreadable by Spark"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: formats',
    intro='<p>In the <code>pyspark</code> shell (start it with <code>--packages org.apache.spark:spark-avro_2.13:4.3.0</code> for Avro). <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Default codecs', cmd='spark.conf.get("spark.sql.parquet.compression.codec"), spark.conf.get("spark.sql.orc.compression.codec")', file='pyspark',
             output="('snappy', 'zstd')", note='Avro: snappy.'),
        dict(title='2 · Missed column', cmd='spark.read.parquet("evolve").columns', file='pyspark',
             output="['order_id', 'city', 'amount', 'month']", note='coupon appears only with mergeSchema.'),
        dict(title='3 · Merged', cmd='spark.read.option("mergeSchema", True).parquet("evolve").columns', file='pyspark',
             output="['order_id', 'city', 'amount', 'coupon', 'month']", note='October rows get null coupon.'),
    ],
)

TRACE = dict(
    heading='Skipping row groups with min/max',
    intro='<p>Follow which blocks a filter must read.</p>',
    code='''blocks = [("rg1", 1, 99), ("rg2", 100, 199), ("rg3", 200, 299)]
target = 150
for name, lo, hi in blocks:
    action = "read" if lo <= target <= hi else "skip"
    print(name, lo, hi, action)
''',
    notes={1: 'Statistics :: Each row group stores min and max per column.', 4: 'Pushdown :: Blocks that cannot match are never read.'},
)

WORKED_INTRO = 'Three storage decisions at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='Formats · basics', title='Convert a CSV feed to Parquet',
         problem='<p>Store the partner feed for analytics.</p>',
         inp='CSV with schema',
         approach=['Read with schema.', 'Write Parquet with zstd.', 'Read back and check the schema.'],
         code='''print("""(spark.read.schema(schema).option("header", True).csv("raw/partner/2026-11-04")
      .write.mode("overwrite").option("compression", "zstd").parquet("lake/partner/2026-11-04"))""")
''', notes={2: 'zstd :: 18% smaller than snappy at the same speed in our lab.'},
         tryit='Step 6 codecs.'),
    dict(level='i', tag='Formats · layout', title='Make lookups skip data',
         problem='<p>Speed up queries filtering by order_id.</p>',
         inp='orders, frequent order_id filters',
         approach=['sortWithinPartitions("order_id") on write.', 'Moderate row-group size.', 'Check rows read.'],
         code='''unsorted, sorted_ = 3_880_000, 80_000
print(f"{unsorted / sorted_:.0f}x fewer rows read")
''', notes={1: 'Lab :: inputRecords from the Spark REST API.'},
         tryit='Step 4.'),
    dict(level='a', tag='Formats · choice', title='Pick formats per layer',
         problem='<p>Choose formats for events, the lake and partner exchange.</p>',
         inp='Kafka events, analytics tables, partner files',
         approach=['Avro for Kafka messages (schema registry).', 'Parquet/Delta for the lake.', 'CSV only for partners who need it.'],
         code='''layers = {"kafka messages": "Avro", "lake tables": "Parquet (Delta/Iceberg)",
          "partner exchange": "CSV with a contract", "Hive legacy": "ORC"}
for k, v in layers.items():
    print(f"{k:17} -> {v}")
''', notes={1: 'Fit :: Row formats for messages, columnar for analytics.'},
         tryit='Lesson 11.5 covers Delta Lake and Iceberg.'),
]

QUIZ = mix([
    dict(q='Beginner: Which formats are columnar?', options=['CSV and JSON', 'Parquet and ORC', 'Avro and CSV', 'JSON and Avro'], answer=1,
         why='Columns stored together.'),
    dict(q='Beginner: Which was smallest for 5M orders?', options=['JSON', 'CSV', 'Avro', 'ORC'], answer=3,
         why='36 MiB.'),
    dict(q='Beginner: What is Spark’s default data source format?', options=['CSV', 'JSON', 'Parquet', 'Avro'], answer=2,
         why='format() defaults to parquet.'),
    dict(q='Intermediate: What does column pruning do?', options=['Deletes columns', 'Reads only needed columns', 'Sorts columns', 'Compresses columns'], answer=1,
         why='0.46 s → 0.17 s for one column.'),
    dict(q='Intermediate: How does Avro support come into Spark?', options=['Built in', 'The external spark-avro module', 'Hive only', 'Not supported'], answer=1,
         why='--packages or --jars.'),
    dict(q='Intermediate: A new column appears in newer Parquet files. A plain read…', options=['Fails', 'May miss the column', 'Merges it', 'Renames it'], answer=1,
         why='Use mergeSchema or a table format.'),
    dict(q='Advanced: Why did sorting by order_id help lookups?', options=['Smaller files', 'Row-group min/max ranges became narrow, so others were skipped', 'Caching', 'More partitions'], answer=1,
         why='80,000 vs 3.88M rows read.'),
    dict(q='Advanced: Are zstd-compressed Parquet files splittable?', options=['No', 'Yes, compression is per column chunk', 'Only small ones', 'Only with Avro'], answer=1,
         why='Unlike .csv.gz.'),
])

REVISION = [
    'Columnar (Parquet, ORC): read only needed columns, skip blocks with min/max statistics.',
    'Avro: binary rows with schema; external <code>spark-avro</code> module; good for messages.',
    '5M orders: JSON 557, CSV 218, Avro 79, Parquet 43, ORC 36 MiB.',
    'Pune sum: CSV 2.37 s, JSON 2.74 s, Avro 0.91 s, Parquet 0.47 s, ORC 0.37 s.',
    'Pushdown works when data is clustered: 80,000 vs 3.88M rows read.',
    'Schema lives in the file; new columns need <code>mergeSchema</code>; type changes fail.',
    'Codecs: snappy (default), zstd (smaller, same speed), gzip (slow write); still splittable.',
]
FAQ = [
    ('Parquet or ORC?', 'Both are excellent. Parquet is the default and most widely supported (Spark, Trino, pandas, DuckDB, Delta, Iceberg); ORC is common in Hive. Pick one per platform.'),
    ('Why not always use mergeSchema?', 'It reads the footers of all files to combine schemas, which is slow on thousands of files. Table formats store the schema centrally instead.'),
    ('What is a good file size?', 'Roughly 128 MB to 1 GB per file for large tables. Many tiny files are a problem of their own (Lesson 5.3).'),
    ('Can I read Parquet without Spark?', 'Yes: pandas, PyArrow, DuckDB, Polars, Trino and most warehouses read Parquet directly.'),
    ('How do I use Avro with Kafka?', 'Use <code>from_avro</code>/<code>to_avro</code> on the value column in Structured Streaming, usually with a schema registry (Module 9).'),
]

PRACTICE_INTRO = 'Programs about storage size, pruning and schemas.'
PROBLEMS = [
    dict(level='easy', title='Storage saving', stmt='Percent saved by Parquet over JSON.', inp='556.8 vs 42.8 MiB',
         code='''print(f"{1 - 42.8 / 556.8:.0%}")
''', explain='About 92% smaller.'),
    dict(level='easy', title='Speed-up', stmt='ORC speed-up over CSV.', inp='2.37 vs 0.37 s',
         code='''print(f"{2.37 / 0.37:.1f}x")
''', explain='Columns + binary + pruning.'),
    dict(level='easy', title='Codec choice', stmt='Smallest codec with write under 2.5 s.', inp='lab table',
         code='''c = {"snappy": (42.8, 1.9), "zstd": (34.9, 2.0), "gzip": (35.4, 3.6), "none": (57.4, 1.8)}
print(min((v[0], k) for k, v in c.items() if v[1] < 2.5))
''', explain='zstd.'),
    dict(level='medium', title='Columns read', stmt='Bytes read with pruning if columns are equal size.', inp='6 columns, 2 needed, 43 MiB',
         code='''print(round(43 * 2 / 6, 1), "MiB")
''', explain='Roughly; real columns differ in size.'),
    dict(level='medium', title='Blocks to read', stmt='Row groups that may contain a value.', inp='ranges and a target',
         code='''rgs = [(1, 500), (300, 900), (800, 1200)]
print(sum(lo <= 850 <= hi for lo, hi in rgs))
''', explain='Overlapping ranges defeat skipping.'),
    dict(level='medium', title='Schema check', stmt='Detect a type change between files.', inp='two schemas',
         code='''a = {"amount": "int"}; b = {"amount": "string"}
print([k for k in a if k in b and a[k] != b[k]])
''', explain='Reject before writing.'),
    dict(level='business', title='Monthly storage', stmt='Monthly cost for a year of orders.', inp='JSON 6.7 TB vs Parquet 0.5 TB at ₹1,800 per TB-month',
         code='''print("JSON ₹", round(6.7 * 1800), "| Parquet ₹", round(0.5 * 1800))
''', explain='Plus faster queries.'),
    dict(level='business', title='Scan cost', stmt='Pay-per-TB engine: cost of 100 queries.', inp='scan 6.7 TB vs 0.1 TB, ₹400 per TB',
         code='''print("JSON ₹", round(100 * 6.7 * 400), "| Parquet ₹", round(100 * 0.1 * 400))
''', explain='Pruning reduces bytes scanned.'),
]

SCN_INTRO = 'File-format questions test whether you understand what Spark reads from disk.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“Why Parquet?”',
        'Why do data lakes use Parquet instead of CSV?',
        'do you know columnar benefits?',
        '<p>Parquet is columnar, binary, compressed and stores its schema and statistics. Spark reads only needed columns and skips row groups using min/max values. In my test 5M orders were 43 MiB as Parquet vs 218 MiB as CSV, and a filter query was about 5x faster.</p>', '“It is just compressed CSV.”') +
    scn('Data engineering', 'Mid-level', 'Predicate pushdown not helping',
        'A filter on Parquet still reads most of the data.',
        'do you know when statistics help?',
        '''<ul>
          <li>Check PushedFilters in the plan.</li>
          <li>Min/max only help when values are clustered: sort or cluster by the filter column on write.</li>
          <li>Measure rows read before and after (3.88M vs 80,000 in my test).</li>
        </ul>''', 'Assuming pushdown always skips data.') +
    scn('Data engineering', 'Mid-level', 'Avro vs Parquet',
        'When would you choose Avro over Parquet?',
        'do you know row vs column use cases?',
        '''<ol>
          <li>Avro: row-oriented messages and exchange, Kafka with schema registry, schema evolution per record.</li>
          <li>Parquet: analytics scans of a few columns over many rows.</li>
          <li>Often both: Avro in Kafka, Parquet in the lake.</li>
        </ol>''', 'Saying one is always better.') +
    scn('Platform', 'Senior', 'Lake cost reduction',
        'Storage and query costs of the lake are rising fast.',
        'can you plan a format migration?',
        '''<ul>
          <li>Convert JSON/CSV archives to Parquet with zstd; keep raw briefly.</li>
          <li>Sort/cluster by common filters; target 128 MB–1 GB files.</li>
          <li>Move to a table format for schema evolution and compaction.</li>
        </ul>''', 'Only buying cheaper storage.')
)
