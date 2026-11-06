import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from hivekit import tables
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
BODY = body(HERE)

META = dict(
    module='06-file-formats', lesson='03-parquet-and-compression', n='6.3',
    module_label='Module 6 · File formats and compression',
    title='Parquet and compression codecs',
    desc='Parquet in Hive and compression codecs, with real Hive 4.2.1 results: Parquet structure (row groups, column chunks, pages, footer), Hive writing UNCOMPRESSED Parquet by default, dictionary vs PLAIN encodings, INT96 vs INT64 timestamps, real sizes for ORC and Parquet with NONE, SNAPPY, LZ4, ZLIB, GZIP and ZSTD, measured codec speeds, Parquet vs ORC statistics-based skipping, reading Parquet files from other engines by column name, and why toy-sized benchmarks mislead.',
    og_desc='Hive wrote our Parquet table with no compression at all. Parquet internals, five codecs measured on real data, and ORC vs Parquet side by side.',
    minutes=35, level='Intermediate → Advanced',
    lead='Parquet is the format every big data engine shares, and the codec inside it decides both your storage bill and your read speed. In this lesson Kabir discovers that Hive 4.2.1 wrote his Parquet table <b>uncompressed</b>, opens the file to see its encodings, measures five codecs on the same data, and compares Parquet with ORC on size, timestamps and skipping. <b>All outputs are real</b>, from Hive 4.2.1 and our own measurements.',
    chips=['Real Hive 4.2.1 outputs', 'Five codecs measured', 'ORC vs Parquet', 'Runs in your browser (Python)'],
)

MAIN = '''# Compression ratio and speed of the codecs Python ships with,
# on order lines like TiffinGo's (Snappy/LZ4/ZSTD are not in the browser)
import zlib, bz2, lzma, time
lines = "".join(f"{100000 + i},{(i * 7919) % 2000 + 1},{['Mumbai','Pune','Thane','Delhi'][i % 4]},"
                f"2026-10-{i % 30 + 1:02d},{(i * 37) % 800 + 40}.00,UPI,DELIVERED\\n" for i in range(20000))
data = lines.encode()

for name, comp, dec in [("zlib-1", lambda d: zlib.compress(d, 1), zlib.decompress),
                        ("zlib-6", lambda d: zlib.compress(d, 6), zlib.decompress),
                        ("bzip2", bz2.compress, bz2.decompress),
                        ("lzma", lzma.compress, lzma.decompress)]:
    t = time.perf_counter(); z = comp(data); c = time.perf_counter() - t
    t = time.perf_counter(); dec(z); d = time.perf_counter() - t
    print(f"{name:7} ratio {len(data) / len(z):4.1f}x  compress {c * 1000:6.1f} ms  decompress {d * 1000:6.1f} ms")
'''
RUN = dict(
    heading='Run the code: the codec trade-off',
    intro='<p>Compression always trades CPU time for space. These programs measure it in your browser and show why encodings matter. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('for name, comp, dec in [("zlib-1", lambda d: zlib.compress(d, 1), zlib.decompress),', 'zlib is the algorithm behind ORC’s ZLIB and GZIP. Level 1 is faster, level 6 smaller.'),
        ('                        ("lzma", lzma.compress, lzma.decompress)]:', 'lzma (xz) is like bzip2: very small, very slow. Neither is used inside ORC or Parquet.'),
    ],
    tasks=[
        dict(label='1 · Ratio vs speed', hint='Press <b>Run</b>. Stronger codecs give a higher ratio and take longer, the same pattern as our measured Snappy → bzip2 table.', code=None),
        dict(label='2 · Predict first: encoding before compression', hint='<b>Predict first:</b> which is smaller after zlib: sorted ids written as text, or as (start, step, count)? (ORC’s RLE stored 50,000 sorted ids in 161 bytes.)',
             code='''import zlib
ids = range(100001, 150001)
plain = ",".join(map(str, ids)).encode()
rle = b"100001,1,50000"
print("plain + zlib:", len(zlib.compress(plain)))
print("RLE         :", len(rle))
'''),
        dict(label='3 · Dictionary encoding', hint='Parquet and ORC replace repeated strings by small numbers. Real lab: city took about 19–21 KB for 50,000 rows.',
             code='''cities = ["Mumbai", "Pune", "Thane", "Delhi", "Bengaluru", "Chennai", "Hyderabad", "Navi Mumbai"]
values = [cities[(i * 7) % 8] for i in range(50000)]
dictionary = sorted(set(values))
codes = [dictionary.index(v) for v in values[:10]]
print(dictionary)
print("first codes:", codes, " bytes as text:", sum(len(v) for v in values), " as 3-bit codes:", 50000 * 3 // 8)
'''),
        dict(label='4 · Storage cost by codec', hint='Real Parquet sizes for 50,000 orders. Change <code>rows</code> to 1 billion to see the yearly difference.',
             code='''sizes = {"UNCOMPRESSED": 1093857, "SNAPPY": 762424, "ZSTD": 582505, "GZIP": 536505}
rows = 50000
for codec, b in sizes.items():
    print(f"{codec:12} {b / rows * 1_000_000_000 / 1e9:7.1f} GB per billion rows")
'''),
        dict(label='5 · Spot the error', hint='This job sets a codec name that does not exist, so nothing is compressed. Use one of SNAPPY, GZIP, ZSTD, LZ4.', expect='error',
             code='''VALID = {"UNCOMPRESSED", "SNAPPY", "GZIP", "ZSTD", "LZ4", "LZ4_RAW", "BROTLI", "LZO"}
table_props = {"parquet.compression": "ZSTANDARD"}
codec = table_props["parquet.compression"]
assert codec in VALID, f"unknown Parquet codec '{codec}'"
print("writing with", codec)
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: check the codec settings and mixed files',
    intro='<p>More statements to try on the lab. <b>Outputs are real</b>, from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · The defaults that decide compression', cmd='SET hive.exec.orc.default.compress;\nSET hive.exec.compress.intermediate;\nSET hive.parquet.write.int64.timestamp;\nSET parquet.compression;          -- not set: the writer default applies', file='Beeline',
             output=capf('l63_set2.txt'),
             note='parquet.compression is not set at all, so the Parquet writer used its own default (UNCOMPRESSED in our lab). Intermediate data between Tez stages is not compressed either; <code>hive.exec.compress.intermediate=true</code> can help network-heavy jobs.'),
        dict(title='2 · One table, two codecs', cmd="SELECT regexp_extract(INPUT__FILE__NAME, '[^/]+$', 0) AS file, COUNT(*) AS n\nFROM cust_pq GROUP BY INPUT__FILE__NAME;\n-- part-v1.parquet: snappy, part-v2.parquet: zstd (written by pyarrow)", file='Beeline',
             output=capf('l63_mixed.txt'),
             note='Each Parquet file records its own codec per column chunk, so files with different codecs can live in one table. That is what makes changing the codec gradually (scenario 3) safe.'),
        dict(title='3 · Choose codecs per table', cmd="CREATE TABLE orders_hot  STORED AS ORC     TBLPROPERTIES ('orc.compress'='SNAPPY')       AS SELECT * FROM orders;\nCREATE TABLE orders_cold STORED AS PARQUET TBLPROPERTIES ('parquet.compression'='ZSTD') AS SELECT * FROM orders;", file='Beeline',
             output='same rows as c_orc_snappy (570,494 bytes) and c_pq_zstd (582,505 bytes) in Step 3',
             note='Set the codec in the DDL so it travels with the table, rather than relying on a session SET that other jobs may forget.'),
    ],
)

TRACE = dict(
    heading='Choosing a codec from requirements',
    intro='<p>A small decision procedure using our measured numbers. Watch <code>pick</code> change as the rules are applied.</p>',
    code='''codecs = {"snappy": (3.0, 1385), "lz4": (3.2, 2593), "zstd": (5.1, 1162), "gzip": (5.2, 622)}
need_ratio, need_speed = 4.0, 1000          # at least 4x smaller, 1,000 MB/s reads
pick = None
for name, (ratio, speed) in codecs.items():
    if ratio >= need_ratio and speed >= need_speed:
        pick = name
print(pick)
''',
    notes={1: 'Data :: Ratio and decompression MB/s from Step 4.', 5: 'Rule :: Both requirements must hold.', 7: 'Result :: Only ZSTD meets both, which is why it has become a popular default.'},
)

WORKED_INTRO = 'Three codec and format decisions with real numbers.'
EXAMPLES = [
    dict(level='b', tag='Storage · estimate', title='How much does compression save per year?',
         problem='<p>TiffinGo will keep 3 years of orders in Parquet. Using the real bytes per order, estimate storage for UNCOMPRESSED, SNAPPY and ZSTD at 50 lakh orders a day.</p>',
         inp='bytes for 50,000 orders: 1,093,857 / 762,424 / 582,505',
         approach=['Bytes per order = size ÷ 50,000.', 'Multiply by orders per day × 365 × 3.', 'Compare in GB.'],
         code='''sizes = {"UNCOMPRESSED": 1093857, "SNAPPY": 762424, "ZSTD": 582505}
orders = 50_00_000 * 365 * 3
for codec, b in sizes.items():
    print(f"{codec:12} {b / 50000 * orders / 1e9:6.1f} GB")
''', notes={3: 'Scale :: Real data compresses differently; measure one real partition before planning.'},
         tryit='ZSTD needs about 56 GB less than uncompressed over three years (64 GB instead of 120 GB). Orders are small rows; event and log tables are often a thousand times bigger, and HDFS replication (3 copies) triples every number.'),
    dict(level='i', tag='Engineering · format choice', title='ORC or Parquet for this table?',
         problem='<p>Score both formats for a table with these needs: (1) Hive UPDATE/DELETE, (2) read by Spark notebooks, (3) smallest storage. Weight the needs 3, 2, 1.</p>',
         inp='ORC: ACID yes, Spark yes, smallest yes · Parquet: ACID no (in Hive), Spark yes, smallest no',
         approach=['Give each format 1 or 0 per need.', 'Multiply by the weight.', 'Pick the higher total.'],
         code='''weights = {"hive_acid": 3, "spark": 2, "smallest": 1}
orc = {"hive_acid": 1, "spark": 1, "smallest": 1}
parquet = {"hive_acid": 0, "spark": 1, "smallest": 0}
for name, f in [("ORC", orc), ("Parquet", parquet)]:
    print(name, sum(weights[k] * f[k] for k in weights))
''', notes={1: 'Weights :: Hive ACID tables require ORC, so that need dominates.'},
         tryit='Remove the ACID need and Parquet ties ORC on Spark, losing only on size. Many teams then pick Parquet for its wider tool support, or Iceberg on Parquet for updates (Module 7).'),
    dict(level='a', tag='Performance · benchmark design', title='Why the 50,000-row benchmark was useless',
         problem='<p>All formats took 3.1–3.4 s in Step 8. Model query time as fixed overhead + bytes ÷ read speed, and find the table size at which ORC (0.44 MB per 50,000 rows) beats text (3.74 MB) by more than 10%.</p>',
         inp='overhead 3.0 s; effective read speed 50 MB/s (illustrative)',
         approach=['time = overhead + size / speed.', 'Grow the row count.', 'Stop when text is 10% slower than ORC.'],
         code='''overhead, speed = 3.0, 50e6
text_b, orc_b = 3735865 / 50000, 437536 / 50000      # bytes per row (real)
rows = 50000
while True:
    t_text = overhead + rows * text_b / speed
    t_orc = overhead + rows * orc_b / speed
    if t_text > 1.1 * t_orc:
        break
    rows *= 2
print(f"{rows:,} rows: text {t_text:.1f} s, ORC {t_orc:.1f} s")
''', notes={7: 'Growth :: Overhead stops dominating once the data takes seconds to read.'},
         tryit='The difference appears around a few million rows in this model. Benchmarks need realistic volumes, and counters (rows, bytes read) are more reliable than wall time on small tests.'),
]

QUIZ = mix([
    dict(q='Beginner: In our Hive 4.2.1 lab, how was a plain CTAS STORED AS PARQUET compressed?', options=['ZLIB', 'SNAPPY', 'UNCOMPRESSED', 'ZSTD'], answer=2,
         why='Set parquet.compression (table property or session) to get compression.'),
    dict(q='Beginner: Which codec is generally the fastest to decompress?', options=['bzip2', 'gzip', 'LZ4', 'ZLIB'], answer=2,
         why='Measured: LZ4 2,593 MB/s vs gzip 622 and bzip2 38.'),
    dict(q='Beginner: What is the Parquet equivalent of an ORC stripe?', options=['Page', 'Row group', 'Footer', 'Dictionary'], answer=1,
         why='Row groups contain column chunks, which contain pages.'),
    dict(q='Intermediate: Which property sets the codec of an ORC table?', options=["'parquet.compression'", "'orc.compress'", "'hive.exec.compress.output'", "'orc.codec'"], answer=1,
         why="TBLPROPERTIES ('orc.compress'='ZSTD'); the default comes from hive.exec.orc.default.compress (ZLIB)."),
    dict(q='Intermediate: Why was the sorted order_id 200 KB in Parquet but 161 bytes in ORC?', options=['Parquet is broken', 'Parquet stored it PLAIN; ORC used run-length encoding', 'ORC dropped the column', 'Different data'], answer=1,
         why='Encodings matter as much as codecs.'),
    dict(q='Intermediate: Hive reads a Parquet file whose columns are in a different order than the table. What happens?', options=['Values shift', 'Error', 'Columns are matched by name', 'Only the first column is read'], answer=2,
         why='Real lab: files from pyarrow with a different order read correctly; a missing column became NULL.'),
    dict(q='Advanced: How did Hive 4.2.1 write Parquet timestamps by default?', options=['INT64 millis', 'INT96', 'STRING', 'DATE'], answer=1,
         why='hive.parquet.write.int64.timestamp=false. Set it to true for INT64 microseconds.'),
    dict(q='Advanced: All formats answered in 3.1–3.4 s on 50,000 rows. What does that show?', options=['Formats do not matter', 'Fixed job overhead dominates small data; benchmark at realistic scale', 'Text is best', 'Parquet is slowest'], answer=1,
         why='Use counters and realistic volumes to compare formats.'),
])

REVISION = [
    '<b>Parquet:</b> file = row groups (≈128 MB) → column chunks → pages (≈1 MB); footer with schema + statistics; <code>PAR1</code> at both ends.',
    '<b>Hive 4.2.1 default:</b> Parquet <b>UNCOMPRESSED</b> (set <code>parquet.compression</code>); ORC <b>ZLIB</b> (<code>orc.compress</code>).',
    '<b>Real sizes:</b> ORC ZSTD 436 KB ≈ ZLIB 438 · Parquet GZIP 537 · ZSTD 583 · SNAPPY 762 · NONE 1,094.',
    '<b>Speed (measured):</b> LZ4/Snappy fastest · ZSTD gzip-like ratio with ~2× faster decompression · bzip2 best ratio, ~36× slower than Snappy.',
    '<b>Choose:</b> hot → Snappy/LZ4 · warm/cold → ZSTD (or ZLIB/GZIP) · text archives → bzip2. Compress inside containers.',
    '<b>Encodings first:</b> dictionary for repeats, RLE for runs; Parquet stored sorted ids PLAIN (200 KB) vs ORC 161 bytes.',
    '<b>Timestamps:</b> INT96 by default; <code>hive.parquet.write.int64.timestamp=true</code> → INT64 micros.',
    'Parquet columns matched <b>by name</b>; missing → NULL; mixed codecs per file are fine.',
    'Skipping: sorted int filter skipped Parquet row groups (1,458 rows); decimal <code>amount &gt; 900</code> did not (ORC did). Benchmark at real scale.',
]
FAQ = [
    ('Should I choose ORC or Parquet?', 'Choose ORC for Hive-centred warehouses and when you need Hive ACID tables; it was smaller on our data and skipped more. Choose Parquet when many engines share the data (Spark, Trino, cloud services, pandas), or when a table format like Iceberg or Delta is built on it. Both are good; consistency within a platform matters more than the choice.'),
    ('Is Snappy still a good default?', 'It is fast and safe, which is why it was the default in many tools for years. ZSTD now gives much smaller files with decompression speeds that are close enough for most analytics, so many teams have switched. Use Snappy or LZ4 where CPU is the bottleneck.'),
    ('Does compression make queries slower?', 'It costs CPU to decompress, but it saves disk and network reads. For big analytic scans on HDFS or object storage, reading fewer bytes usually wins, so compressed columnar data is faster overall. On tiny datasets, as our 50,000-row test showed, neither effect is visible.'),
    ('Why does Hive still write INT96 timestamps?', 'For compatibility with older Hive, Impala and Spark versions that expect INT96. Newer readers prefer INT64 with a logical timestamp type. If all your readers are recent, enabling <code>hive.parquet.write.int64.timestamp</code> avoids the deprecated encoding; test time zone handling in each engine.'),
    ('Can one table mix ORC and Parquet files?', 'Not in one plain table: the table’s InputFormat and SerDe decide how every file is read. Different partitions can have different formats (ALTER TABLE … PARTITION … SET FILEFORMAT), but this is confusing and rarely worth it. Codecs, on the other hand, can safely differ file by file.'),
]

PRACTICE_INTRO = 'Programs about codecs, sizes and Parquet behaviour, with the HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Compression ratio', stmt='Compute the ratio of uncompressed to ZSTD Parquet.', inp='1,093,857 and 582,505 bytes',
         code='''print(round(1093857 / 582505, 2))
''', explain='1.88×. ZSTD almost halves our Parquet table.'),
    dict(level='easy', title='Magic bytes check', stmt='Check whether a file looks like Parquet.', inp='first and last 4 bytes',
         code='''head, tail = b"PAR1", b"PAR1"
print(head == b"PAR1" and tail == b"PAR1")
''', explain='Parquet files start and end with PAR1; the footer length sits just before the final PAR1.'),
    dict(level='easy', title='Pick a codec', stmt='Pick a codec for each table temperature.', inp='hot, warm, cold, text archive',
         code='''policy = {"hot": "SNAPPY or LZ4", "warm": "ZSTD", "cold": "ZSTD or GZIP", "text archive": "BZIP2"}
for k, v in policy.items():
    print(k, "->", v)
''', explain='Follows the measured trade-off: speed for hot data, size for data stored long.'),
    dict(level='medium', title='Decompression time', stmt='How long does it take to decompress 10 GB with each codec on one core?', inp='measured MB/s',
         code='''speeds = {"lz4": 2593, "snappy": 1385, "zstd": 1162, "gzip": 622, "bzip2": 38}
for c, s in speeds.items():
    print(f"{c:7} {10000 / s:7.1f} s")
''', explain='From 4 seconds (LZ4) to over 4 minutes (bzip2) per core. Clusters spread it over many cores, but the ratio stays.'),
    dict(level='medium', title='Rows read with sorted row groups', stmt='Parquet row groups of 1,460 rows; customer 1492 falls in one group. How many rows are read?', inp='35 groups',
         code='''groups = [(1350, 1409), (1409, 1469), (1469, 1528), (1528, 1584)]
print([g for g in groups if g[0] <= 1492 <= g[1]], "-> about 1,458 rows")
''', explain='One row group (1469–1528), matching the real counter of 1,458 rows.'),
    dict(level='medium', title='Missing column in old files', stmt='Read old Parquet records that lack the plan column.', inp='old and new records',
         code='''cols = ["customer_id", "name", "plan", "city"]
recs = [{"customer_id": 1, "name": "Aarav Desai", "city": "Bengaluru"}, {"customer_id": 4, "plan": "Gold", "city": "Pune", "name": "Diya Patil"}]
for r in recs:
    print([r.get(c) for c in cols])
''', explain='Missing columns read as NULL (None), by name, as in the real cust_pq output. Avro could have supplied a default instead.'),
    dict(level='business', title='Monthly saving from a codec switch', stmt='A team stores 300 TB of Snappy Parquet. Estimate the saving if rewritten with ZSTD using the lab ratio.', inp='SNAPPY 762,424 vs ZSTD 582,505 bytes',
         code='''ratio = 582505 / 762424
print(round(300 * (1 - ratio)), "TB saved")
''', explain='About 71 TB, using the lab ratio. Real ratios vary by data; test a sample first.'),
    dict(level='business', title='Codec decision record', stmt='Print a one-line decision for a shared Parquet table.', inp='needs: shared with Spark, read hourly, 2-year retention',
         code='''print("Parquet + ZSTD, INT64 timestamps, partitioned by date: shared engines, frequent reads, long retention")
''', explain="DDL: STORED AS PARQUET TBLPROPERTIES ('parquet.compression'='ZSTD') with SET hive.parquet.write.int64.timestamp=true in the load job."),
]

SCN_INTRO = 'Codec and format questions often come as cost or performance problems. Show that you can reason with numbers.'
SCENARIOS = (
    scn('Any company · Big data', 'Fresher', '“ORC vs Parquet”',
        'Compare ORC and Parquet and say when you would use each.',
        'do you know both are columnar and where they differ?',
        '<p>Both are columnar, self-describing, compressed formats with statistics for skipping. ORC has stripes with row-group indexes every 10,000 rows and bloom filters, is the default choice in Hive and required for Hive ACID; Parquet has row groups and pages and is the common format across Spark, Trino and cloud tools. Pick ORC for Hive-centred warehouses, Parquet for multi-engine lakes.</p>', 'Saying one is “row” and the other “column” based.') +
    scn('Data engineering', 'Mid-level', 'Parquet table bigger than expected',
        'A new Parquet table is twice the size of the ORC table with the same data.',
        'do you check the codec?',
        '''<ol>
          <li>Inspect the files (parquet-tools / pyarrow): compression UNCOMPRESSED.</li>
          <li>Set <code>parquet.compression</code> in TBLPROPERTIES (ZSTD or SNAPPY) and rewrite the data.</li>
          <li>Add codec review to table-creation checklists.</li>
        </ol>''', '“Parquet is just bigger than ORC.”') +
    scn('Platform', 'Mid-level', 'Timestamps differ between Hive and Spark',
        'The same Parquet table shows different timestamps in Hive and in Spark.',
        'do you know INT96 and time zone handling?',
        '''<ul>
          <li>Check the physical type: Hive writes INT96 by default; engines interpret it and time zones differently.</li>
          <li>Write INT64 timestamps (<code>hive.parquet.write.int64.timestamp=true</code>) and agree on UTC storage.</li>
          <li>Verify a few known rows in every engine.</li>
        </ul>''', 'Adding 5:30 by hand in one engine.') +
    scn('Architecture', 'Senior', 'Codec strategy for a growing lake',
        'Storage grows 40% a year and query CPU is also rising. Propose a codec and format strategy.',
        'can you balance storage and CPU with evidence?',
        '''<ul>
          <li>Measure on real partitions: size and query CPU for Snappy, ZSTD and ZLIB.</li>
          <li>Hot partitions in a fast codec, older partitions rewritten to ZSTD; compress intermediate data for shuffle-heavy jobs.</li>
          <li>Standardise formats (ORC for Hive ACID, Parquet/Iceberg for shared data) and track bytes stored and scanned per table.</li>
        </ul>''', '“Use the strongest compression everywhere.”')
)
