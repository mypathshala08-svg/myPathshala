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
    module='06-file-formats', lesson='02-orc-deep-dive', n='6.2',
    module_label='Module 6 · File formats and compression',
    title='ORC deep dive: stripes, indexes and bloom filters',
    desc='ORC file internals explained with a real file and real Hive 4.2.1 results: hive --orcfiledump, postscript, footer, stripes, row groups of 10,000 rows, file/stripe/row-group statistics, RLE v2 and dictionary encodings (161 bytes for 50,000 sorted ids), predicate pushdown measured with Tez counters (30,000 rows, then 0 splits), the effect of sorting (10,000 rows instead of 50,000), bloom filters (30,000 rows, index 890 → 65,439 bytes), stripe size and vectorised reading.',
    og_desc='The table was ORC and a lookup still read every row. Open a real ORC file, read its statistics, and measure what sorting and bloom filters really skip.',
    minutes=35, level='Intermediate → Advanced',
    lead='Everyone says “use ORC”, but few people look inside an ORC file. In this lesson Kabir opens one with <code>hive --orcfiledump</code>, reads its stripes, statistics and encodings, and then measures with Hive’s counters how many rows each optimisation really skips: predicate pushdown, sorting, bloom filters. <b>All outputs are real</b>, from Hive 4.2.1.',
    chips=['Real orcfiledump output', 'Pushdown measured', 'Sorting vs bloom filters', 'Runs in your browser (Python)'],
)

MAIN = '''# How ORC row-group statistics let a reader skip data
groups = [  # (min, max) of amount per 10,000-row group: real values from orcfiledump
    (40, 840), (40, 880), (40, 840), (40, 880), (40, 880)]

def can_match(lo, hi, threshold):          # WHERE amount > threshold
    return hi > threshold

for threshold in [870, 900]:
    read = [i for i, (lo, hi) in enumerate(groups) if can_match(lo, hi, threshold)]
    print(f"amount > {threshold}: read groups {read} -> {len(read) * 10000} rows")
'''
RUN = dict(
    heading='Run the code: statistics, sorting and bloom filters',
    intro='<p>These programs mimic what the ORC reader does with min/max statistics and bloom filters, using real numbers from our file. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('def can_match(lo, hi, threshold):          # WHERE amount > threshold', 'A group can only contain a match if its maximum is above the threshold.'),
        ('    read = [i for i, (lo, hi) in enumerate(groups) if can_match(lo, hi, threshold)]', 'Groups that cannot match are skipped without being decompressed.'),
    ],
    tasks=[
        dict(label='1 · Skipping with min/max', hint='Press <b>Run</b>. Real Hive: 30,000 rows for &gt; 870 and no data at all for &gt; 900.', code=None),
        dict(label='2 · Predict first: unsorted vs sorted', hint='<b>Predict first:</b> how many groups can contain customer 1492 in each layout? (Real: 50,000 vs 10,000 rows.)',
             code='''unsorted = [(1, 2000)] * 5
sorted_ = [(1, 404), (404, 800), (800, 1205), (1205, 1604), (1604, 2000)]   # real
for name, groups in [("unsorted", unsorted), ("sorted", sorted_)]:
    hits = [i for i, (lo, hi) in enumerate(groups) if lo <= 1492 <= hi]
    print(name, hits, len(hits) * 10000, "rows")
'''),
        dict(label='3 · Run-length encoding', hint='Sorted ids become one run (start, step, count). This is why order_id took 161 bytes.',
             code='''ids = list(range(100001, 150001))
runs = []
start, step, count = ids[0], ids[1] - ids[0], 1
for a, b in zip(ids, ids[1:]):
    if b - a == step:
        count += 1
    else:
        runs.append((start, step, count)); start, count = b, 1
runs.append((start, step, count))
print(len(ids), "values ->", runs)
'''),
        dict(label='4 · A tiny bloom filter', hint='A bloom filter never says “no” for a value that is present. Try other ids: some absent ones may say “maybe” (a false positive).',
             code='''import hashlib
BITS = 64
def positions(v, k=3):
    return [int(hashlib.md5(f"{v}-{i}".encode()).hexdigest(), 16) % BITS for i in range(k)]
group = [17, 1492, 603, 88, 1999]
bits = set()
for v in group:
    bits |= set(positions(v))
for q in [1492, 42, 1000, 603]:
    print(q, "maybe" if all(p in bits for p in positions(q)) else "definitely not")
'''),
        dict(label='5 · Spot the error', hint='This “pushdown” skips a group that does contain a match, which a real reader must never do. Fix the comparison.', expect='error',
             code='''groups = [(40, 840), (40, 880)]
data = [[300, 840], [870, 880, 50]]          # values inside each group
threshold = 860
read = [i for i, (lo, hi) in enumerate(groups) if lo > threshold]   # bug
found = sum(1 for i in read for v in data[i] if v > threshold)
true_count = sum(1 for g in data for v in g if v > threshold)
assert found == true_count, f"skipping lost rows: found {found}, expected {true_count}"
print(found)
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: the classes, the stats and the sorted index',
    intro='<p>More commands to try on the lab. <b>Outputs are real</b>, from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · ORC’s classes and table statistics', cmd='DESCRIBE FORMATTED f_orc;\n-- selected lines', file='Beeline',
             output=capf('l62_fmt.txt'),
             note='The metastore keeps numRows and totalSize too, from the write. The optimiser uses them to plan joins; the ORC reader uses the statistics inside the file to skip data.'),
        dict(title='2 · The row index of the sorted table', cmd='hive --orcfiledump --rowindex 2 /opt/hive/data/warehouse/tiffingo.db/orders_sorted/000000_0', file='Terminal',
             output='Row group indices for column 2:\n' + capf('l62_sorted_idx.txt'),
             note='Each group now covers about 400 customers, so <code>customer_id = 1492</code> can only be in entry 3. Compare with the unsorted file, where every entry says min 1, max 2000.'),
        dict(title='3 · Is pushdown enabled on your cluster?', cmd='SET hive.optimize.index.filter;\nSET hive.exec.orc.split.strategy;', file='Beeline',
             output='| hive.optimize.index.filter=true     |\n| hive.exec.orc.split.strategy=HYBRID |',
             note='The HYBRID split strategy decides whether to read file footers while planning (useful for few, large files) or not. Reading footers at planning time is what makes a 0-split result like the one for <code>amount &gt; 900</code> possible.'),
    ],
)

TRACE = dict(
    heading='Pushdown, one row group at a time',
    intro='<p>The reader walks the row-group index and decides read or skip before decompressing anything. Watch <code>read</code> and <code>skipped</code>.</p>',
    code='''groups = [(1, 404), (404, 800), (800, 1205), (1205, 1604), (1604, 2000)]
wanted = 1492
read, skipped = [], []
for i, (lo, hi) in enumerate(groups):
    if lo <= wanted <= hi:
        read.append(i)
    else:
        skipped.append(i)
print("read", read, "skipped", skipped)
''',
    notes={1: 'Index :: Real min/max of customer_id in the sorted file.', 5: 'Test :: Only a group whose range contains 1492 can hold its orders.', 9: 'Result :: One group of 10,000 rows, matching RECORDS_IN 10000.'},
)

WORKED_INTRO = 'Three ORC tuning decisions with real numbers.'
EXAMPLES = [
    dict(level='b', tag='Analytics · pushdown', title='Which queries can skip the file?',
         problem='<p>Using the real file statistics (amount 40–880, order_date 2026-10-01 to 10-30, city Bengaluru–Thane), decide for each filter whether Hive can skip the whole file.</p>',
         inp="amount > 900 · amount < 30 · order_date = '2026-11-01' · city = 'Pune'",
         approach=['Compare each filter with min and max.', 'If no value in [min, max] can match, skip.', 'Otherwise the file must be read.'],
         code='''stats = {"amount": (40, 880), "order_date": ("2026-10-01", "2026-10-30"), "city": ("Bengaluru", "Thane")}
tests = [("amount", ">", 900), ("amount", "<", 30), ("order_date", "=", "2026-11-01"), ("city", "=", "Pune")]
for col, op, v in tests:
    lo, hi = stats[col]
    possible = (hi > v) if op == ">" else (lo < v) if op == "<" else (lo <= v <= hi)
    print(f"{col} {op} {v!r}: {'read' if possible else 'SKIP file'}")
''', notes={5: 'Strings :: min/max for text are alphabetical: Pune lies between Bengaluru and Thane, so the file must be read.'},
         tryit='Real lab: amount &gt; 900 produced 0 splits. Try city = \'Agra\': it sorts before Bengaluru, so the file can be skipped.'),
    dict(level='i', tag='Design · sort order', title='Pick the sort column',
         problem='<p>Three query types hit a daily ORC partition: by customer (1,200 times a day), by restaurant (300) and by payment type (20). Choose one sort column using the share of groups each query must read.</p>',
         inp='5 row groups; a sorted column narrows a lookup to 1 group, unsorted to 5',
         approach=['Rows read per query = groups read × 10,000.', 'Weight by daily frequency.', 'Pick the column that minimises total rows read.'],
         code='''freq = {"customer_id": 1200, "restaurant_id": 300, "payment": 20}
for sort_col in freq:
    total = sum(n * (1 if c == sort_col else 5) * 10000 for c, n in freq.items())
    print(f"sort by {sort_col:13}: {total:,} rows read per day")
''', notes={3: 'Weighting :: Only the sorted column benefits; others still read every group.'},
         tryit='Sort by customer_id. Then consider a bloom filter for restaurant_id lookups; payment has only 4 values and gains little.'),
    dict(level='a', tag='Cost · bloom filters', title='Is the bloom filter worth its size?',
         problem='<p>The bloom filter added 64,549 bytes of index to a 437,536-byte file and cut a lookup from 50,000 to 30,000 rows. With 1,200 lookups a day on a 30-day table, is it worth it?</p>',
         inp='index 890 → 65,439 bytes per file; 30 files; rows read per lookup 50,000 → 30,000',
         approach=['Extra storage = extra bytes × files.', 'Rows saved = 20,000 × lookups × files.', 'Compare.'],
         code='''extra_bytes = (65439 - 890) * 30
rows_saved_per_day = (50000 - 30000) * 1200 * 30
print("extra storage:", round(extra_bytes / 1e6, 2), "MB")
print("rows not read per day:", f"{rows_saved_per_day:,}")
''', notes={3: 'Trade-off :: Storage is paid once; the savings repeat every query.'},
         tryit='The 15% extra space pays off for frequent lookups. For a table queried once a week by date only, skip the bloom filter.'),
]

QUIZ = mix([
    dict(q='Beginner: What does ORC store for every 10,000 rows of each column?', options=['A copy of the data', 'Statistics such as min, max, count and sum', 'A bloom filter always', 'Nothing'], answer=1,
         why='The row-group index. Bloom filters are only added for columns you list.'),
    dict(q='Beginner: Where does an ORC reader start reading a file?', options=['At the first byte', 'At the end: postscript and footer', 'In the middle', 'At a random stripe'], answer=1,
         why='The postscript says how to read the footer, which lists the stripes.'),
    dict(q='Beginner: Why did order_id take only 161 bytes for 50,000 values?', options=['It was dropped', 'Sorted ids are run-length encoded', 'It is a string', 'ZLIB is magic'], answer=1,
         why='RLE v2 stores the sequence as start, step and count.'),
    dict(q='Intermediate: Why did WHERE customer_id = 1492 read all 50,000 rows of f_orc?', options=['PPD was off', 'Every row group had min 1 and max 2000', 'ORC cannot filter integers', 'The file was corrupt'], answer=1,
         why='Unsorted data makes every range cover everything. Sorted, Hive read 10,000 rows.'),
    dict(q='Intermediate: What happened to WHERE amount > 900 when the file maximum is 880?', options=['Read 50,000 rows', 'Read 30,000 rows', 'No splits were created: the file was skipped', 'Error'], answer=2,
         why='File statistics ruled it out at planning time.'),
    dict(q='Intermediate: Which setting enables ORC predicate pushdown in Hive?', options=['hive.vectorized.execution.enabled', 'hive.optimize.index.filter', 'orc.create.index', 'hive.exec.orc.default.compress'], answer=1,
         why='true in our lab. With false, every query read 50,000 rows.'),
    dict(q='Advanced: Bloom filters help most for…', options=['Range filters on sorted columns', 'Equality lookups of values that appear in few row groups', 'GROUP BY queries', 'Every column'], answer=1,
         why='They answer “definitely not here” per group; ranges use min/max instead.'),
    dict(q='Advanced: What did smaller stripes (128 KB) do to our file?', options=['Made it smaller', 'Made 10 stripes and a 7% bigger file', 'Nothing', 'Broke the file'], answer=1,
         why='More indexes and footers, less compression context. Keep the 64 MB default.'),
])

REVISION = [
    '<b>Layout:</b> stripes (index · data streams · stripe footer) → file footer (schema, stripes, stats) → postscript (ends with “ORC”).',
    '<b>Statistics</b> at 3 levels: file, stripe, row group (10,000 rows, <code>orc.row.index.stride</code>).',
    '<b>Encodings:</b> RLE v2 for numbers (sorted ids → 161 bytes), dictionary for low-cardinality strings; then ZLIB (default) / Snappy / LZ4 / ZSTD.',
    '<b>Inspect:</b> <code>hive --orcfiledump [--rowindex cols] file</code>.',
    '<b>PPD</b> (<code>hive.optimize.index.filter=true</code>): amount &gt; 870 → 30,000 rows; amount &gt; 900 → 0 splits; off → 50,000.',
    '<b>Clustering matters:</b> unsorted lookup 50,000 rows; sorted 10,000.',
    '<b>Bloom filters</b> (<code>orc.bloom.filter.columns</code>, fpp 0.05): lookup 30,000; index 890 → 65,439 bytes. For = / IN only.',
    'Keep stripes large (64 MB default); tiny stripes made the file 7% bigger.',
    'ORC → vectorised reading (batches of 1,024 rows) and Hive ACID tables.',
]
FAQ = [
    ('Does Hive read the whole ORC file to find the statistics?', 'No. It reads the last bytes (postscript and footer), which contain the file and stripe statistics and the stripe locations. Row-group indexes sit at the start of each stripe and are read only for stripes that might match.'),
    ('Which filters can be pushed down into ORC?', 'Comparisons of a column with constants: =, &lt;, &gt;, &lt;=, &gt;=, BETWEEN, IN, IS NULL, and AND/OR/NOT combinations of these. Filters with functions on the column (<code>upper(city) = \'PUNE\'</code>) or comparisons between two columns cannot use the statistics; Hive still applies them, after reading.'),
    ('Should I sort every ORC table?', 'Sort tables that are read with selective filters on one main column (customer, device, store), and only by that column. Sorting costs a shuffle at write time, and a second sort order is impossible in the same file. Tables read only by date partition and full aggregates do not need it.'),
    ('How is ORC different from Parquet?', 'Both are columnar with statistics and compression. ORC has row-group indexes every 10,000 rows, built-in bloom filters and is the format for Hive ACID; Parquet is the most common format in Spark and cloud tools and organises data in row groups and pages. Lesson 6.3 compares them on the same data.'),
    ('What is the “ORC split strategy”?', 'How Hive plans tasks for ORC files: ETL reads file footers while planning (enables skipping whole files and stripes, good for few large files), BI does not (faster planning for many small files), HYBRID chooses between them based on file count and size. Our 0-split result shows footers being used at planning time.'),
]

PRACTICE_INTRO = 'Programs that reason about ORC statistics and encodings, with the HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Row groups in a file', stmt='How many row groups does a 50,000-row stripe have with the default stride?', inp='50,000 rows, stride 10,000',
         code='''import math
print(math.ceil(50000 / 10000))
''', explain='5 groups, matching the 5 entries in the real --rowindex output. With stride 1,000 there were 50.'),
    dict(level='easy', title='Compression ratio', stmt='Compare Hive’s raw size estimate with the file length.', inp='raw 24,650,000 bytes, file 437,536 bytes',
         code='''print(round(24650000 / 437536, 1), "x")
''', explain='About 56× from encodings plus ZLIB, by Hive’s own estimate of the in-memory size.'),
    dict(level='easy', title='Can this group match?', stmt='Does a group with amount 40–840 need reading for amount &gt;= 840?', inp='min 40, max 840',
         code='''lo, hi = 40, 840
print("read" if hi >= 840 else "skip")
''', explain='Yes: the maximum equals 840, so a match is possible. Edge cases matter: &gt; 840 would skip it.'),
    dict(level='medium', title='Dictionary saving', stmt='Estimate the bytes for 50,000 city values as text vs dictionary codes.', inp='8 cities, average 7 characters',
         code='''n, avg_len, distinct = 50000, 7, 8
plain = n * avg_len
dict_bytes = distinct * avg_len + n * 3 / 8        # 3 bits per code
print(plain, int(dict_bytes))
''', explain='About 350 KB vs 19 KB before compression. The real file stored city in 20,880 bytes.'),
    dict(level='medium', title='Rows read with a bloom filter', stmt='50 groups of 1,000 rows; the bloom filter says “no” for 20. How many rows are read?', inp='50 groups, 20 skipped',
         code='''print((50 - 20) * 1000)
''', explain='30,000, the real counter for orders_bloom.'),
    dict(level='medium', title='Sorted ranges', stmt='Split ids 1–2000 into 5 equal groups and find which holds 1492.', inp='ids 1–2000',
         code='''groups = [(i * 400 + 1, (i + 1) * 400) for i in range(5)]
print(groups, [i for i, (a, b) in enumerate(groups) if a <= 1492 <= b])
''', explain='Group 3, like the real sorted file (1205–1604). Real boundaries shift because customers have different numbers of orders.'),
    dict(level='business', title='Monthly read savings', stmt='A lookup runs 1,200 times a day on 30 daily ORC files. How many rows a day does sorting save?', inp='50,000 → 10,000 rows per file',
         code='''print(f"{(50000 - 10000) * 30 * 1200:,}")
''', explain='1.44 billion fewer rows read per day, from a one-time sort when writing.'),
    dict(level='business', title='Choose the table properties', stmt='Generate TBLPROPERTIES for an orders table with lookups on customer_id and restaurant_id.', inp='two lookup columns',
         code='''cols = ["customer_id", "restaurant_id"]
print("TBLPROPERTIES ('orc.compress'='ZSTD', 'orc.bloom.filter.columns'='" + ",".join(cols) + "')")
''', explain='ZSTD for size (Lesson 6.3) and bloom filters for the two lookup columns; keep the default stripe size and stride.'),
]

SCN_INTRO = 'ORC internals come up in senior Hive and data engineering interviews, usually as “why is this slow” or “explain the structure”.'
SCENARIOS = (
    scn('Any company · Hive', 'Fresher', '“Why is ORC faster than text?”',
        'Explain why queries on ORC tables are faster than on text tables.',
        'do you know columnar storage, compression and statistics?',
        '<p>ORC stores columns separately, so a query reads only the columns it needs; values are typed and encoded (RLE, dictionary) and compressed, so far fewer bytes are read (0.44 MB vs 3.74 MB for our orders); and statistics at file, stripe and 10,000-row level let Hive skip data that cannot match the WHERE clause. It also supports vectorised reading.</p>', 'Saying only “ORC is compressed”.') +
    scn('Analytics', 'Mid-level', 'ORC lookup still slow',
        'Point lookups by customer on an ORC table read the whole table.',
        'do you understand that statistics need clustered data?',
        '''<ol>
          <li>Check counters (RECORDS_IN) and <code>orcfiledump --rowindex</code>: every group spans the full id range.</li>
          <li>Rewrite partitions sorted by customer_id (DISTRIBUTE BY + SORT BY), or add a bloom filter if the data must stay in time order.</li>
          <li>Measure again: our lab went from 50,000 to 10,000 (sorted) or 30,000 (bloom) rows.</li>
        </ol>''', '“ORC already has indexes, so it must be the network.”') +
    scn('Data engineering', 'Mid-level', 'A filter that does not push down',
        'A query with <code>WHERE upper(city) = \'PUNE\'</code> reads everything, while <code>city = \'Pune\'</code> skips groups.',
        'do you know which predicates can use statistics?',
        '''<ul>
          <li>Functions on the column hide it from the ORC reader; it can compare only column vs constant.</li>
          <li>Clean the data at load time (store normalised values) and filter on the raw column.</li>
          <li>Verify with counters before and after.</li>
        </ul>''', 'Adding more bloom filters, which have the same limitation.') +
    scn('Platform', 'Senior', 'Designing an ORC table for mixed workloads',
        'A 2-billion-row events table is queried by date ranges, by device id lookups and by full daily aggregates.',
        'can you combine partitioning, sorting, bloom filters and codec choice?',
        '''<ul>
          <li>Partition by event date (Module 5); sort within each partition by device_id if lookups dominate, else keep time order and add a bloom filter on device_id.</li>
          <li>Keep 64 MB stripes and the 10,000 stride; choose ZSTD or ZLIB for size, Snappy/LZ4 for speed (6.3).</li>
          <li>Validate with orcfiledump and counters on one partition before rewriting everything.</li>
        </ul>''', 'Bloom filters on every column “to be safe”.')
)
