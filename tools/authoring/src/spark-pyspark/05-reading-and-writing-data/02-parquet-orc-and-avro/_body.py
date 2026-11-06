import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l52_formats.txt'
def sec(a, b=None, drop=()):
    s = capsec(C, a, b, drop)
    s = re.sub(r'#\d+L?', '', s)
    return '\n'.join(l if len(l) <= 140 else l[:137] + ' …' for l in s.split('\n'))
S3 = re.sub(r', rows read [\d,]+', '', sec('== 3)', '== 3b)'))

def grid(x, y, cols, rows=4, cw=34, ch=14, hi=None, row_hi=None, label=''):
    """table drawn by rows (row store) — hi = column index to highlight"""
    o = t(x, y - 5, label, 7, 'ink2', anchor='start', bold=True) if label else ''
    for r in range(rows):
        for c, name in enumerate(cols):
            tone = 'green' if c == hi else ('acc' if r == row_hi else 'card')
            o += box(x + c * (cw + 2), y + r * (ch + 2), cw, ch, tone, rx=2)
            if r == 0:
                o += t(x + c * (cw + 2) + cw / 2, y + 10, name, 6.2, mono=True)
    return o

SIZES = [('csv', 218.3, 'amber'), ('json', 556.8, 'red'), ('parquet', 42.8, 'green'), ('orc', 36.1, 'green'), ('avro', 79.1, 'violet')]
def size_bars(x=14, y=30, w=300, hl=None):
    o = ''
    for k, (n, v, c) in enumerate(SIZES):
        yy = y + k * 20
        o += t(x, yy + 10, n, 7.4, 'ink', anchor='start', mono=True) + fill(x + 54, yy, max(3, v / 556.8 * w), 13, c if (hl is None or n in hl) else 'grey') + t(x + 60 + v / 556.8 * w, yy + 10, f'{v:.0f} MiB', 7.0, 'ink2', anchor='start')
    return o

# ---------------------------------------------------------------- story
sc_ = (size_bars(14, 22, 260) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured (5M orders)', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('JSON 557 MiB, Parquet 43, ORC 36', 'green'), ('Pune sum: CSV 2.37 s, ORC 0.37', 'green'),
           ('Parquet 1 column: 0.17 s vs 0.46', 'green'), ('sorted: 80,000 of 5M rows read', 'green'),
           ('new column: needs mergeSchema', 'amber'), ('INT -> STRING: CANNOT_MERGE', 'red')])))
scene_svg = scene('Parquet and ORC store data by column with types, statistics and compression; Avro stores rows in a compact binary form. We wrote the same 5 million orders in five formats and compared size, speed and what Spark can skip.', sc_,
                  'Columnar files are <tspan font-weight="700" class="s-acc">smaller</tspan> and let Spark <tspan font-weight="700" class="s-acc">skip</tspan> what a query does not need.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Why is our storage bill so high?”</h2>
  <div class="story">
    <p class="narration">TiffinGo kept every day’s orders as JSON in cloud storage because “it is readable”. A year later the bucket was huge, every dashboard query read every byte, and a simple “revenue in Pune” query took minutes on a large cluster.</p>

{scene_svg}

R> Sir, JSON is easy to open and check. What is wrong with it?
A> Nothing, for exchanging data. For storing and querying it, it is the worst choice: every record repeats every column name as text, numbers are text, and to read one column Spark must parse whole records.
K> So we switch to Parquet?
A> Parquet or ORC for analytics, Avro for row-by-row exchange such as Kafka messages. Today we write the same 5 million orders in CSV, JSON, Parquet, ORC and Avro, and measure size, query time, column pruning, row-group skipping, schema evolution and compression codecs. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> File formats at three levels
L1> A filing cabinet
      <ul>
        <li>A CSV or JSON file is a pile of handwritten forms: to find all amounts you read every form.</li>
        <li>Parquet and ORC keep one drawer per column (all amounts together), with a label on each folder saying the smallest and largest value inside.</li>
        <li>To add up amounts in Pune you open only two drawers and skip folders whose labels show they cannot match.</li>
      </ul>
L2> The API
      <ul>
        <li><code>df.write.parquet(path)</code>, <code>.orc(path)</code>, <code>.format("avro").save(path)</code>; read with <code>spark.read.parquet/orc</code> or <code>format("avro")</code>.</li>
        <li>Avro is a separate module: <code>--packages org.apache.spark:spark-avro_2.13:4.3.0</code> (or <code>--jars</code>).</li>
        <li>Options: <code>compression</code> (snappy, zstd, gzip…), <code>mergeSchema</code>; plans show <code>PushedFilters</code> and the columns read.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>5M orders: JSON 557 MiB, CSV 218, Avro 79, Parquet 43, ORC 36.</li>
        <li>“Sum of amount in Pune”: CSV 2.37 s, JSON 2.74 s, Avro 0.91 s, Parquet 0.47 s, ORC 0.37 s.</li>
        <li>On data sorted by <code>order_id</code>, a point lookup read 80,000 rows instead of 3,880,000 thanks to row-group statistics.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Columnar and binary file formats</h2>
''' + def_block(
    '<b>Apache Parquet</b> and <b>Apache ORC</b> are self-describing, <b>columnar</b> storage formats: a file is divided into row groups (Parquet) or stripes (ORC), and within each the values of every column are stored together, encoded (dictionary, run-length) and compressed, with min/max statistics in the metadata. Readers can therefore read only the needed columns (<b>column pruning</b>) and skip row groups whose statistics exclude a filter (<b>predicate pushdown</b>). <b>Apache Avro</b> is a row-oriented binary format with an embedded schema, designed for record-at-a-time serialization and schema evolution, commonly used for messages and data exchange. Parquet is Spark’s default data source format; Avro support is provided by the external <code>spark-avro</code> module. Spark preserves the schema in these files and can merge compatible schemas across files with <code>mergeSchema</code>.',
    'Parquet and ORC store each column separately, compressed and with statistics, so Spark reads only the columns and blocks a query needs. Avro stores whole rows in compact binary with its schema. Use Parquet or ORC for analytics, Avro for messages, and CSV/JSON only to exchange data.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Columnar', 'Values of one column stored together.'),
    ('Row group / stripe', 'A block of rows inside a Parquet / ORC file.'),
    ('Column pruning', 'Read only the columns the query uses.'),
    ('Predicate pushdown', 'Use filters and statistics to skip data.'),
    ('Min/max statistics', 'Smallest and largest value per block.'),
    ('Codec', 'Compression: snappy, zstd, gzip, lz4…'),
    ('mergeSchema', 'Combine different but compatible file schemas.'),
    ('spark-avro', 'The external module for Avro.'),
]) + '''

  <h3>Choosing a format</h3>
''' + table(['', 'CSV', 'JSON', 'Avro', 'Parquet', 'ORC'], [
    ['Layout', 'rows, text', 'rows, text', 'rows, binary', 'columns', 'columns'],
    ['Schema in file', 'no', 'no', 'yes', 'yes', 'yes'],
    ['Size (5M orders)', '218 MiB', '557 MiB', '79 MiB', '43 MiB', '36 MiB'],
    ['Pune sum', '2.37 s', '2.74 s', '0.91 s', '0.47 s', '0.37 s'],
    ['Skip columns/blocks', 'no', 'no', 'no', 'yes', 'yes'],
    ['Typical use', 'exchange', 'APIs, events', 'Kafka, exchange', 'lakes, Spark default', 'Hive, lakes'],
], minw=680) + lv + '''
EXAM> “Why is Parquet faster than CSV?” It is columnar and binary: Spark reads only the needed columns (column pruning), skips row groups using min/max statistics (predicate pushdown), and reads compressed, typed data without parsing text. In our lab the same query took 0.47 s on Parquet against 2.37 s on CSV, from a file 5x smaller.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Compression codecs</h2>
''' + table(['Codec', 'Parquet size (5M orders)', 'Write', 'Notes'], [
    ['snappy (Parquet and Avro default)', '42.8 MiB', '1.9 s', 'Fast, moderate compression'],
    ['zstd (ORC default in Spark 4)', '34.9 MiB', '2.0 s', 'Smaller at similar speed: a good modern default'],
    ['gzip', '35.4 MiB', '3.6 s', 'Slow to write'],
    ['uncompressed', '57.4 MiB', '1.8 s', 'Columnar encoding still saves a lot'],
], minw=640) + '''
WARN> Compression inside Parquet and ORC is per column chunk, so the files stay <b>splittable</b> whatever the codec. That is different from a <code>.csv.gz</code> file (Lesson 5.1), which is read by a single task. Do not gzip Parquet files from the outside.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Five formats, one dataset</h2>
  <p>All outputs are real: PySpark 4.3.0 with <code>spark-avro_2.13-4.3.0.jar</code>, local mode with 4 cores, 5,000,000 orders cached and written in 4 partitions. Query times are from a second (warm) run.</p>
''' + stepper([
    ('Step 1 · Defaults and writing five formats',
     code('python', 'l52_formats.py', 'for k in ("spark.sql.parquet.compression.codec", "spark.sql.orc.compression.codec",\n          "spark.sql.avro.compression.codec"):\n    print(k, spark.conf.get(k))\nfor fmt in ("csv", "json", "parquet", "orc", "avro"):\n    src.write.mode("overwrite").format(fmt).save(f"{OUT}/{fmt}")', sec('== 1)', '== 3)')),
     'Write times were similar (3–4 s), but sizes were not: JSON repeats every key in every record and was <b>13x larger</b> than Parquet. ORC was smallest, partly because Spark 4 compresses ORC with zstd by default while Parquet uses snappy. Avro’s compact binary rows sit in between.'),
    ('Step 2 · The same query on each format',
     code('python', 'l52_formats.py', 'df = reader(fmt)        # CSV and JSON with an explicit schema\ndf.where(F.col("city") == "Pune").agg(F.sum("amount")).collect()', S3),
     'Text formats must be parsed byte by byte; Avro avoids text parsing but still reads whole rows; Parquet and ORC read only <code>city</code> and <code>amount</code>, already typed and compressed. ORC was <b>6x faster</b> than CSV and over 7x faster than JSON.'),
    ('Step 3 · Column pruning, measured',
     code('python', 'l52_formats.py', 'for fmt in ("csv", "parquet"):\n    df = reader(fmt)\n    df.write.format("noop").mode("overwrite").save()                   # all columns\n    df.select("amount").write.format("noop").mode("overwrite").save()  # one column', sec('== 3b)', '== 5)')),
     'Reading one column instead of six made Parquet <b>2.7x faster</b> (0.46 → 0.17 s): the other columns were never touched. CSV also gained (the parser skips converting unused fields, Lesson 5.1) but still had to scan every byte. The plan shows it: <code>FileScan parquet [city, amount]</code> with <code>PushedFilters: [IsNotNull(city), EqualTo(city,Pune)]</code>.'),
    ('Step 4 · Skipping row groups with statistics',
     code('python', 'l52_formats.py', 'src.sortWithinPartitions("order_id").write.option("parquet.block.size", 8 * 2**20).parquet(sorted_path)\nfor path in (unsorted_path, sorted_path):\n    spark.read.parquet(path).where(F.col("order_id") == 4_200_000).count()\n# rows read: inputRecords from the REST API', sec('== 5)', '== 6)')),
     'Every row group stores the min and max of each column. In the unsorted file, ids were spread so most row groups “might” contain 4,200,000: 3.88 million rows were read. After sorting within partitions, only the row group whose range contained the id was read: <b>80,000 rows</b>. Sorting or clustering by the columns you filter on is what makes pushdown effective.'),
    ('Step 5 · Schema in the file, and schema evolution',
     code('python', 'l52_formats.py', 'spark.read.parquet(f"{OUT}/parquet").printSchema()\n# October without coupon, November with coupon\nspark.read.parquet(f"{OUT}/evolve").columns\nspark.read.option("mergeSchema", True).parquet(f"{OUT}/evolve").show()\n# December: amount written as STRING', sec('== 6)', '== 9)')),
     'No schema was given, yet types came back exactly (<code>order_id: long</code>, <code>order_date: date</code>): the schema lives in the file. When November added a <code>coupon</code> column, a plain read <b>silently missed it</b> (Spark used one file’s schema); <code>mergeSchema</code> combined both and filled October with null. A real type change, INT to STRING, could not be merged and failed loudly. Table formats such as Delta and Iceberg manage this for you (Lesson 11.5).'),
    ('Step 6 · Compression codecs',
     code('python', 'l52_formats.py', 'for codec in ("snappy", "zstd", "gzip", "uncompressed"):\n    src.write.mode("overwrite").option("compression", codec).parquet(f"{OUT}/codec_{codec}")', sec('== 9)')),
     '<b>zstd</b> was 18% smaller than snappy at the same write speed; gzip was as small but almost twice as slow to write. Read times differ little at this size. Even uncompressed, Parquet (57 MiB) was a quarter of CSV, thanks to columnar encoding. Set it with <code>option("compression", "zstd")</code> or <code>spark.sql.parquet.compression.codec</code>.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('json 557 MiB  csv 218 MiB', RD), ('avro 79 MiB', Y), ('parquet 43 MiB  orc 36 MiB', G)], size=7.6),
    term([('Pune sum  csv  2.37 s', RD), ('          avro 0.91 s', Y), ('          orc  0.37 s', G)], size=7.6),
    term([('parquet all columns : 0.46 s', W), ('parquet amount only : 0.17 s', G), ('FileScan [city, amount]', G)], size=7.4),
    term([('order_id = 4200000', W), ('unsorted: 3,880,000 rows read', Y), ('sorted  :    80,000 rows read', G)], size=7.4),
    term([('new column: missed without mergeSchema', Y), ('mergeSchema: coupon added', G), ('INT vs STRING: CANNOT_MERGE', RD)], size=7.0),
]
COLS = ['id', 'cust', 'city', 'date', 'amt', 'stat']
B1 = [
    t(180, 14, 'Bytes on disk', 9.4, bold=True) + size_bars(20, 30, 240) + cap('Same data, 15x difference.', '', 'green', y=144, h=30),
    t(180, 14, 'Row formats read everything', 9.4, bold=True) + grid(20, 36, COLS, rows=4, cw=24, label='CSV / JSON / Avro') + grid(196, 36, COLS, rows=4, cw=24, hi=None, label='Parquet / ORC') + ''.join(box(196 + c * 26, 52, 24, 46, 'green', rx=2) for c in (2, 4)) + cap('Columnar reads city and amount only.', '', 'green', y=144, h=30),
    t(180, 14, 'Column pruning', 9.4, bold=True) + grid(80, 36, COLS, rows=4, cw=30) + box(80 + 4 * 32, 52, 30, 46, 'green', rx=2) + cap('One column: 0.46 → 0.17 s.', '', 'green', y=144, h=30),
    t(180, 14, 'Row groups with min/max', 9.4, bold=True) + ''.join(opbox(20 + k * 84, 46, f'rg {k + 1}', f'{1 + k * 1.25:.2f}M–{2.25 + k * 1.25:.2f}M', 'green' if k == 2 else 'card', 76, 30) for k in range(4)) + cap('Sorted data: skip 3 of 4 blocks.', '', 'green', y=144, h=30),
    t(180, 14, 'Schemas travel and evolve', 9.4, bold=True) + flow([('Oct file', 'no coupon', 'card'), ('Nov file', '+ coupon', 'blue'), ('merged', 'coupon null in Oct', 'green')], y=40, w=96, gap=22) + opbox(118, 90, 'Dec: amount STRING', 'cannot merge', 'acc', 124, 30) + cap('Add columns, never change types.', '', 'amber', y=144, h=30),
]
see_caps = ['JSON 557 MiB, ORC 36 MiB.', 'ORC 6x faster than CSV.', 'One column read: 2.7x faster.', '80,000 rows instead of 3.88 million.', 'Added column merged; type change failed.']
behind_caps = ['Text repeats names; columns compress.', 'Rows must be read whole.', 'Columns are separate chunks.', 'Statistics decide what to skip.', 'The schema is stored in each file.']
two = anim_two('Parquet, ORC and Avro', 'Read only what you need', 'Real lab outputs', 'Inside the files', see, B1, see_caps, behind_caps)

# ---- scenario 1: JSON lake
e1 = (t(180, 22, 'A year of orders as JSON', 9.4, bold=True) + t(180, 56, 'dashboards read everything', 8.4, 'ink2') + cap('Big bill, slow queries.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Convert once to Parquet (zstd)', 9.4, bold=True) + t(180, 56, 'read JSON with schema → write', 8.4, 'ink2') + cap('A one-time job.', '', 'green', y=150, h=34))
e3 = (t(180, 22, 'Storage: about 13x smaller', 9.4, bold=True) + t(180, 56, '557 → 43 MiB in our lab', 8.4, 'ink2') + cap('Bill drops.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Queries: several times faster', 9.4, bold=True) + t(180, 56, 'only needed columns read', 8.4, 'ink2') + cap('2.74 s → 0.47 s here.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Keep raw JSON briefly', 9.4, 'acc', bold=True) + t(180, 56, 'bronze for replay, Parquet for use', 8.2, 'ink2') + cap('Lifecycle rule on raw.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'A data lake made of JSON',
              'Storing analytics data in a columnar format. (Typical; ratios from our lab.)',
              'JSON to Parquet', 'Converting stored JSON to Parquet cut size about 13x and query time several times in our lab', [e1, e2, e3, e4, e5],
              ['JSON lake.', 'Convert.', 'Smaller.', 'Faster.', 'Keep raw briefly.'],
              hid='scenario-json-lake')

# ---- scenario 2: filter on unsorted ids
b1 = (t(180, 22, 'Customer support looks up orders', 9.4, bold=True) + t(180, 56, 'where order_id = …', 8.4, 'ink', mono=True) + cap('Each lookup scans a lot.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Row groups cover all ids', 9.4, bold=True) + t(180, 56, 'min/max ranges overlap', 8.4, 'ink2') + cap('3.88M of 5M rows read.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'Sort within partitions on write', 9.4, bold=True) + t(180, 56, 'sortWithinPartitions("order_id")', 8.2, 'ink', mono=True) + cap('Narrow ranges per block.', '', 'green', y=150, h=34))
b4 = (t(180, 22, '80,000 rows read', 9.4, bold=True) + t(180, 56, 'the matching row group only', 8.4, 'ink2') + cap('Our Step 4.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Many filter columns?', 9.4, 'acc', bold=True) + t(180, 56, 'Z-order / liquid clustering (Delta)', 8.2, 'ink2') + cap('Lesson 11.5.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Point lookups that read everything',
              'Making predicate pushdown work. (Numbers from our lab.)',
              'Row-group skipping', 'Statistics only skip data when values are clustered; sort by frequently filtered columns when writing', [b1, b2, b3, b4, b5],
              ['Lookups.', 'Overlapping ranges.', 'Sort on write.', 'Skip blocks.', 'Clustering.'],
              hid='scenario-pushdown')

# ---- scenario 3: schema change
u1 = (t(180, 22, 'Upstream adds coupon column', 9.4, bold=True) + t(180, 56, 'new files have it, old do not', 8.4, 'ink2') + cap('Reports miss coupons.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Plain read uses one schema', 9.4, bold=True) + t(180, 56, 'coupon silently absent', 8.4, 'ink2') + cap('Like our Step 5.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'mergeSchema or a table format', 9.4, bold=True) + t(180, 56, 'Delta / Iceberg track the schema', 8.4, 'ink2') + cap('Columns added safely.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Then amount turns STRING', 9.4, bold=True) + t(180, 56, 'CANNOT_MERGE_INCOMPATIBLE_DATA_TYPE', 7.8, 'ink', mono=True) + cap('Reads fail.', '', 'red', y=150, h=34))
u5 = (t(180, 22, 'Contract: add, never change', 9.4, 'acc', bold=True) + t(180, 56, 'validate schema on write', 8.4, 'ink2') + cap('Reject bad files early.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'When the producer changes the schema',
              'Schema evolution in file formats. (Behaviour from our lab.)',
              'Schema evolution', 'New columns need mergeSchema or a table format; type changes break reads, so validate schemas when writing', [u1, u2, u3, u4, u5],
              ['New column.', 'Missed.', 'Merge.', 'Type change.', 'Contract.'],
              hid='scenario-evolution')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Read only what you need</h2>
  <p>Left: real outputs. Right: what is inside the files and what Spark skips.</p>
''' + two + '''
  <p>Three live scenarios follow: a data lake made of JSON, point lookups that read everything, and a producer that changes the schema.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>File formats at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'lake', 12, 'blue', bold=True) + t(60, 58, 'Parquet', 7.4, 'ink2'),
    '1. Data lakes',
    'S3, ADLS and GCS lakes store analytics tables as Parquet, usually under Delta Lake or Iceberg.',
    ['Raw', '*Parquet', 'Queries']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'Hive', 12, 'green', bold=True) + t(60, 58, 'ORC', 7.4, 'ink2'),
    '2. Hive warehouses',
    'Hive tables on Hadoop clusters are often ORC; Spark reads them with the same pruning and pushdown.',
    ['Hive table', '*ORC', 'Spark SQL']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'Kafka', 12, 'violet', bold=True) + t(60, 58, 'Avro', 7.4, 'ink2'),
    '3. Streaming messages',
    'Kafka topics carry Avro records with schemas in a schema registry; Spark decodes them with from_avro.',
    ['Kafka', '*Avro', 'Structured Streaming']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'cost', 12, 'acc', bold=True) + t(60, 58, 'storage', 7.4, 'ink2'),
    '4. Cost reduction',
    'Converting JSON or CSV archives to Parquet with zstd cuts storage and scan costs on pay-per-byte engines.',
    ['JSON archive', '*Parquet + zstd', 'Lower bill']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'BI', 12, 'acc', bold=True) + t(60, 58, 'fast scans', 7.4, 'ink2'),
    '5. BI on Spark and Trino',
    'Dashboards query Parquet through Spark SQL, Trino or Athena, which all use column pruning and statistics.',
    ['Parquet', '*pushdown', 'Dashboard']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> text formats in <a href="../01-csv-and-json/">5.1</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
