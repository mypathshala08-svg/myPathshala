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
    module='05-partitioning-and-bucketing', lesson='03-bucketing', n='5.3',
    module_label='Module 5 · Partitioning and bucketing',
    title='Bucketing: CLUSTERED BY, sampling and bucket joins',
    desc='Hive bucketing explained with real Hive 4.2.1 results: CLUSTERED BY … SORTED BY … INTO n BUCKETS, one file per bucket, the Murmur3 hash of bucketing_version 2 (not id mod n), INPUT__FILE__NAME, TABLESAMPLE by bucket, ROWS and rand(), bucket pruning (5,649 rows read instead of 50,000), partitioning vs bucketing, bucket map and SMB joins and what EXPLAIN really chose, plus two surprises: bucketed CTAS refused and LOAD DATA losing rows with a header.',
    og_desc='Is the bucket really id mod n? Not in Hive 4. Bucketing with real files, samples, pruning counters and a LOAD that silently lost three customers.',
    minutes=35, level='Beginner → Advanced',
    lead='Partitioning works for columns with a modest number of values. For ids, which have thousands or millions of values, Hive offers <b>bucketing</b>: a fixed number of files chosen by a hash. In this lesson Kabir buckets orders by customer, looks inside the 8 files, shows that Hive 4 uses Murmur3 and not “id mod n”, samples a stable 1-in-8 group while reading one file, and finds two surprises. <b>All outputs are real</b>, from Hive 4.2.1.',
    chips=['Real Hive 4.2.1 outputs', 'Murmur3, not mod n', 'Sampling and pruning', 'Runs in your browser (Python)'],
)

MAIN = '''# Bucketing: a hash of the column decides the file. Python's hash() for small
# ints is the value itself, like Hive's old version 1; version 2 uses Murmur3.
customers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
N = 4

buckets = {b: [] for b in range(N)}
for cid in customers:
    b = hash(cid) % N                 # version 1 idea: value mod N
    buckets[b].append(cid)

for b, ids in buckets.items():
    print(f"{b:06d}_0", ids)
'''
RUN = dict(
    heading='Run the code: hashing ids into bucket files',
    intro='<p>These programs place ids into bucket files and sample them, the way Hive does. Remember: real Hive 4 tables use Murmur3, so the exact file numbers differ (Step 2). Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    b = hash(cid) % N                 # version 1 idea: value mod N', 'The rule is always hash mod N. Only the hash function changed between bucketing versions.'),
        ('    print(f"{b:06d}_0", ids)', 'Hive names bucket files by number: 000000_0, 000001_0, …'),
    ],
    tasks=[
        dict(label='1 · Ids into buckets', hint='Press <b>Run</b>. Each bucket gets 4 of the 16 ids, and an id always lands in the same bucket.', code=None),
        dict(label='2 · Predict first: TABLESAMPLE', hint='<b>Predict first:</b> which file does BUCKET 6 OUT OF 8 read? (Real lab: 000005_0, 5,649 rows.)',
             code='''x, y = 6, 8          # TABLESAMPLE(BUCKET x OUT OF y ON customer_id)
n_buckets = 8
files = [b for b in range(n_buckets) if b % y == x - 1]
print([f"{b:06d}_0" for b in files])
'''),
        dict(label='3 · Half the buckets', hint='BUCKET 2 OUT OF 4 on an 8-bucket table reads two files. Real lab: 5,961 + 5,649 = 11,610 rows.',
             code='''rows = [6210, 5961, 6754, 5922, 6689, 5649, 6276, 6539]   # real rows per file
x, y = 2, 4
picked = [b for b in range(8) if b % y == x - 1]
print(picked, sum(rows[b] for b in picked))
'''),
        dict(label='4 · Keys are even, rows are not', hint='Add a “whale” customer with 5,000 orders to bucket 0 and see how uneven the files become.',
             code='''rows = [6210, 5961, 6754, 5922, 6689, 5649, 6276, 6539]
whale = 0
rows[0] += whale
avg = sum(rows) / len(rows)
print("largest / average =", round(max(rows) / avg, 2))
'''),
        dict(label='5 · Spot the error', hint='This loader skips one header line in every bucket file, like the real LOAD bug. Make it skip the header only once, before bucketing.', expect='error',
             code='''lines = ["customer_id,name", "1,Aarav", "2,Ananya", "3,Arjun", "4,Diya", "5,Ishaan"]
N = 2
files = {b: [] for b in range(N)}
for i, line in enumerate(lines):                 # header goes in as a row
    files[i % N].append(line)
loaded = [l for b in files.values() for l in b[1:]]   # skip 1 line per file
assert len(loaded) == 5, f"loaded {len(loaded)} customers, expected 5"
print(loaded)
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: partitions with buckets, shared groups and the hidden header',
    intro='<p>Three more queries to try in Beeline on the TiffinGo data. <b>Outputs are real</b>, from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · Partition by day, bucket by customer', cmd="CREATE TABLE orders_day_bkt (order_id INT, customer_id INT, city STRING, amount DECIMAL(10,2))\nPARTITIONED BY (order_date DATE)\nCLUSTERED BY (customer_id) INTO 4 BUCKETS STORED AS ORC;\nINSERT OVERWRITE TABLE orders_day_bkt PARTITION (order_date)\nSELECT order_id, customer_id, city, amount, order_date FROM orders WHERE order_date <= '2026-10-02';\nSELECT order_date, regexp_extract(INPUT__FILE__NAME, '[^/]+/[^/]+$', 0) AS file, COUNT(*) AS n\nFROM orders_day_bkt GROUP BY order_date, INPUT__FILE__NAME ORDER BY file;", file='Beeline',
             output=capf('l53_partbkt.txt'),
             note='Every partition folder gets its own 4 bucket files. The four files of 10-01 add up to 1,641, the day’s real count. Date filters prune folders; customer filters prune buckets inside them.'),
        dict(title='2 · Same bucket, same customers, in two tables', cmd="SELECT COUNT(*) AS same FROM\n  (SELECT DISTINCT customer_id FROM orders_bkt TABLESAMPLE(BUCKET 6 OUT OF 8 ON customer_id) a) x\nJOIN\n  (SELECT customer_id FROM customers_bkt TABLESAMPLE(BUCKET 6 OUT OF 8 ON customer_id) b) y\nON x.customer_id = y.customer_id;", file='Beeline',
             output=tables(capf('l53_same.txt'))[0],
             note='All 230 customers in bucket 6 of orders are exactly the customers in bucket 6 of customers: same column, same bucket count, same hash. This is the property bucket joins rely on.'),
        dict(title='3 · Find the hidden header', cmd="ALTER TABLE cust_bkt_load SET TBLPROPERTIES ('skip.header.line.count'='0');\nSELECT COUNT(*) AS lines_in_files, COUNT(customer_id) AS with_id FROM cust_bkt_load;\nSELECT regexp_extract(INPUT__FILE__NAME, '[^/]+$', 0) AS file, customer_id, name\nFROM cust_bkt_load WHERE customer_id IS NULL OR customer_id IN (1, 3, 5);", file='Beeline',
             output=capf('l53_load3.txt'),
             note='With skipping off, all 2,001 lines are back: the header sits in file 0 as a row with a NULL id, and customers 1, 3 and 5 are the first lines of files 1, 2 and 3. That explains the 1,997.'),
    ],
)

TRACE = dict(
    heading='Writing rows into bucket files',
    intro='<p>Each row is hashed and appended to its bucket’s file. Watch <code>files</code> fill up; equal ids always meet in the same file.</p>',
    code='''rows = [(100001, 7), (100002, 12), (100003, 7), (100004, 3)]
N = 4
files = {}
for order_id, cid in rows:
    b = cid % N
    files.setdefault(b, []).append(order_id)
print(files)
''',
    notes={5: 'Hash :: Version-1 style (value mod N) to keep the numbers easy; Hive 4 tables use Murmur3.', 7: 'Result :: Both orders of customer 7 are in the same file, which is what makes bucket sampling and joins work.'},
)

WORKED_INTRO = 'Three bucketing decisions from TiffinGo’s data team.'
EXAMPLES = [
    dict(level='b', tag='Design · partition or bucket?', title='Pick partitioning or bucketing for each column',
         problem='<p>For each column, decide: partition (few values, used in filters), bucket (many values, used in joins or lookups), or neither.</p>',
         inp='order_date (30/month), city (8), customer_id (2,000+), order_id (50,000), status (3)',
         approach=['Count distinct values.', 'Few values and filtered often → partition.', 'Many values and joined or looked up → bucket.'],
         code='''cols = {"order_date": (30, "filter"), "city": (8, "filter"), "customer_id": (2000, "join"),
        "order_id": (50000, "lookup"), "status": (3, "rare")}
for c, (n, use) in cols.items():
    if use == "filter" and n <= 1000:
        d = "partition"
    elif use in ("join", "lookup"):
        d = "bucket"
    else:
        d = "neither"
    print(f"{c:12} {n:6} {use:7} -> {d}")
''', notes={4: 'Rule :: A simplification. Real decisions also consider data size per partition (Lesson 5.4).'},
         tryit='city could be a second partition level only if each date-city folder stays large; otherwise keep it as a normal column.'),
    dict(level='i', tag='Analytics · sampling', title='Estimate total revenue from one bucket',
         problem='<p>Before running a heavy query, estimate total October revenue from bucket 6 of 8 and compare with the real total of all buckets.</p>',
         inp='rows per bucket (real), average order value 300',
         approach=['Take the rows of one bucket.', 'Scale by the number of buckets.', 'Compare with the full count.'],
         code='''rows = [6210, 5961, 6754, 5922, 6689, 5649, 6276, 6539]
sample = rows[5]                      # BUCKET 6 OUT OF 8
estimate = sample * 8
print("estimate", estimate, "actual", sum(rows), f"error {100 * (estimate - sum(rows)) / sum(rows):.1f}%")
''', notes={3: 'Scale :: One bucket holds about one-eighth of the keys, not exactly one-eighth of the rows.'},
         tryit='The estimate is 9.6% low because bucket 6 is the smallest file. Sample two or three buckets for a better estimate.'),
    dict(level='a', tag='Engineering · load pipeline', title='A safe load into a bucketed table',
         problem='<p>Write the steps so that a CSV with a header lands fully in a bucketed table, and prove the count, avoiding the LOAD bug from Step 7.</p>',
         inp='CSV: 1 header + 8 rows (a small version of the 2,000-customer file)',
         approach=['LOAD into a plain staging table with skip.header.line.count=1.', 'INSERT OVERWRITE the bucketed table from staging.', 'Compare COUNT(*) of both.'],
         code='''csv = ["customer_id,name"] + [f"{i},Customer {i}" for i in range(1, 9)]
stage = csv[1:]                                  # header skipped once, on the plain table
N = 4
buckets = {b: [] for b in range(N)}
for line in stage:                               # INSERT ... SELECT * FROM stage
    cid = int(line.split(",")[0])
    buckets[cid % N].append(line)
loaded = sum(len(v) for v in buckets.values())
print("stage", len(stage), "bucketed", loaded, "OK" if loaded == len(stage) else "MISMATCH")
''', notes={2: 'Staging :: The header is removed by the plain text table before any bucketing happens.'},
         tryit='Add the count check to the job and fail it on a mismatch: in our lab the direct LOAD gave 1,997 without any error.'),
]

QUIZ = mix([
    dict(q='Beginner: What does CLUSTERED BY (customer_id) INTO 8 BUCKETS create?', options=['8 folders', '8 files per table or partition, chosen by a hash of customer_id', '8 tables', 'An index on customer_id'], answer=1,
         why='One file per bucket: 000000_0 … 000007_0 in our lab.'),
    dict(q='Beginner: Which column type suits bucketing better than partitioning?', options=['order_date', 'status with 3 values', 'customer_id with thousands of values', 'country with 5 values'], answer=2,
         why='High-cardinality columns would create too many partitions; buckets stay at a fixed number.'),
    dict(q='Beginner: Is the bucketing column stored inside the data files?', options=['No, only in folder names', 'Yes, it is a normal column', 'Only in the metastore', 'Only when SORTED BY is used'], answer=1,
         why='Unlike a partition column, a bucket column stays in the data.'),
    dict(q='Intermediate: In our Hive 4.2.1 lab, customer 1 was in file 000005_0 of an 8-bucket table. Why not 000001_0?', options=['Random placement', 'bucketing_version 2 uses Murmur3, not the plain value', 'Files are numbered from the end', 'Sorting moved it'], answer=1,
         why='pmod(murmur_hash(1), 8) = 5; id mod 8 is the old version-1 rule.'),
    dict(q='Intermediate: TABLESAMPLE(BUCKET 6 OUT OF 8 ON customer_id) on an 8-bucket table reads…', options=['all 8 files', 'file 000006_0', 'file 000005_0', 'a random 1/8 of rows'], answer=2,
         why='Sample bucket numbers start at 1. Real: 5,649 rows, one file.'),
    dict(q='Intermediate: Is SET hive.enforce.bucketing=true needed in Hive 4?', options=['Yes, always', 'No, bucketing is always enforced since Hive 2.x', 'Only for ORC', 'Only with SORTED BY'], answer=1,
         why='The setting was removed; inserts always write the declared buckets.'),
    dict(q='Advanced: What happened when we used CREATE TABLE … CLUSTERED BY … AS SELECT?', options=['It worked', 'Error 10068: CTAS not supported for the target layout', 'It created an unbucketed table', 'It created 8 tables'], answer=1,
         why='Create the bucketed table first, then INSERT … SELECT.'),
    dict(q='Advanced: Both tables are bucketed on customer_id, yet EXPLAIN shows a broadcast map join. Why?', options=['Bucketing is broken', 'The optimiser found broadcasting the small table cheaper', 'Buckets must be 1', 'Joins ignore buckets in Hive'], answer=1,
         why='Bucket joins are a cost-based option; they pay off when both sides are large.'),
])

REVISION = [
    '<code>CLUSTERED BY (col) [SORTED BY (col)] INTO n BUCKETS</code> → n files per table or partition. Bucket column stays in the data.',
    'Bucket = hash(col) mod n. <b>bucketing_version 2 → Murmur3</b> (customer 1 → bucket 5 of 8), not id mod n.',
    'No <code>hive.enforce.bucketing</code> since Hive 2.x. Check placement with <code>INPUT__FILE__NAME</code>.',
    '<b>Partition vs bucket:</b> folders by value for low-cardinality filters · fixed files by hash for ids, joins, sampling. Combine them.',
    '<b>TABLESAMPLE(BUCKET x OUT OF y ON col)</b>: 1-based; reads only matching files on a bucketed table. <code>ON rand()</code> changes every run. <code>(n ROWS)</code> works; <code>PERCENT</code> was refused on Tez.',
    '<b>Bucket pruning:</b> <code>WHERE id = v</code> / <code>IN</code> → one bucket’s rows (5,649 not 50,000).',
    '<b>Bucket map / SMB join</b>: both sides bucketed (and sorted) on the key; optimiser decides; check EXPLAIN.',
    '<b>Gotchas:</b> bucketed CTAS → Error 10068; LOAD + header into bucketed table lost rows → stage, then INSERT.',
    'Buckets spread <b>keys</b> evenly, not rows: a heavy key makes a heavy bucket.',
]
FAQ = [
    ('How many buckets should I choose?', 'Pick a count that gives bucket files of a useful size, usually tens to hundreds of MB, and that you will not need to change, because changing it means rewriting the table. For tables you join, use the same count (or one a multiple of the other). Powers of two are common. With partitions, remember the count applies to every partition.'),
    ('What is the difference between CLUSTERED BY in CREATE TABLE and CLUSTER BY in a query?', 'CLUSTERED BY … INTO n BUCKETS is table DDL: it fixes how the table’s files are organised. CLUSTER BY col in a SELECT (Lesson 3.4) only distributes and sorts that query’s output across reducers; it does not change any table.'),
    ('Can I bucket an existing table?', 'ALTER TABLE … CLUSTERED BY only changes the metadata; existing files are not rewritten, so they no longer match the declaration. Create a new bucketed table, INSERT OVERWRITE … SELECT from the old one, check counts, and swap.'),
    ('Do Spark and Hive buckets match?', 'Not automatically. Spark’s own bucketing scheme (its hash function and file layout) is not the same as Hive’s. Spark can read Hive-bucketed tables, but for bucket joins across engines check that both use the Hive bucketing scheme (bucketing_version) for that table.'),
    ('Is bucketing still useful with Iceberg?', 'Iceberg replaces Hive bucketing with its own <b>bucket transform</b> in the partition spec, <code>PARTITIONED BY SPEC (bucket(16, customer_id))</code>, which also hashes ids into a fixed number of groups. The idea from this lesson carries over directly (Module 7).'),
]

PRACTICE_INTRO = 'Programs that simulate buckets, samples and checks, with the HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='File name of a bucket', stmt='Print Hive’s file name for buckets 0 to 3.', inp='4 buckets',
         code='''for b in range(4):
    print(f"{b:06d}_0")
''', explain='Bucket files are numbered from 000000_0; TABLESAMPLE numbers buckets from 1.'),
    dict(level='easy', title='Version-1 bucket', stmt='Using the old rule (value mod n), which bucket does customer 13 go to with 8 buckets?', inp='13, n = 8',
         code='''print(13 % 8)
''', explain='5 under version 1. In Hive 4 the real bucket is <code>pmod(murmur_hash(13), 8)</code>; check it with INPUT__FILE__NAME.'),
    dict(level='easy', title='Average customers per bucket', stmt='How many customers should each of 8 buckets hold?', inp='2,000 customers',
         code='''print(2000 / 8)
''', explain='250. The real lab had 230–269 per bucket.'),
    dict(level='medium', title='Files read by a sample', stmt='Which bucket files does BUCKET 3 OUT OF 4 read on a 16-bucket table?', inp='x = 3, y = 4, n = 16',
         code='''x, y, n = 3, 4, 16
print([f"{b:06d}_0" for b in range(n) if b % y == x - 1])
''', explain='4 files: 2, 6, 10 and 14. The sample size is n / y buckets.'),
    dict(level='medium', title='Skew check', stmt='Flag buckets more than 15% above the average size.', inp='real rows per bucket',
         code='''rows = [6210, 5961, 6754, 5922, 6689, 5649, 6276, 6539]
avg = sum(rows) / len(rows)
print(round(avg), [i for i, r in enumerate(rows) if r > 1.15 * avg])
''', explain='None: the largest is 8% above average. A whale customer would change that (Lesson 5.4).'),
    dict(level='medium', title='Count check after a load', stmt='Compare the source line count with the loaded count and report missing rows.', inp='2,001 lines with a header, 1,997 loaded',
         code='''source_lines, header, loaded = 2001, 1, 1997
missing = source_lines - header - loaded
print("missing", missing, "FAIL" if missing else "OK")
''', explain='The real LOAD lost 3 customers. A count check would have stopped the job.'),
    dict(level='business', title='Stable experiment group', stmt='Put customers into a test group if their bucket (8 buckets) is 0, and print the group size for ids 1–40 using value mod 8.', inp='ids 1–40',
         code='''group = [c for c in range(1, 41) if c % 8 == 0]
print(len(group), group)
''', explain='Real Hive: <code>TABLESAMPLE(BUCKET 1 OUT OF 8 ON customer_id)</code> or <code>pmod(murmur_hash(customer_id), 8) = 0</code>. The group is the same every day.'),
    dict(level='business', title='Cost of a bucketed lookup per day', stmt='A support tool looks up one customer across 30 day partitions, each with 8 buckets of about 200 rows. Compare rows read with and without bucket pruning.', inp='30 days, 8 buckets, 200 rows each',
         code='''days, buckets, rows = 30, 8, 200
print("without pruning", days * buckets * rows)
print("with pruning   ", days * rows)
''', explain='8 times fewer rows: one bucket per day instead of all eight.'),
]

SCN_INTRO = 'Bucketing questions test whether you know when to use it and how it differs from partitioning.'
SCENARIOS = (
    scn('Any company · Hive', 'Fresher', '“Partitioning vs bucketing”',
        'Explain both and say when to use each.',
        'do you know folders vs files, and cardinality?',
        '<p>Partitioning creates a folder per value of a column (date) and helps queries that filter on it; good for low-to-moderate cardinality. Bucketing hashes a column (customer_id) into a fixed number of files; good for high cardinality, sampling and joins. Partition columns are not in the files; bucket columns are. They can be combined: partition by date, bucket by customer.</p>', 'Saying bucketing is “partitioning with more partitions”.') +
    scn('Data science', 'Fresher', 'A reproducible sample',
        'Your notebook samples 10% of users with rand() and your numbers change every run.',
        'do you know deterministic sampling?',
        '''<ul>
          <li>Sample on the user column: <code>TABLESAMPLE(BUCKET 1 OUT OF 10 ON user_id)</code>, or filter <code>pmod(hash(user_id), 10) = 0</code>.</li>
          <li>On a table bucketed by user_id this also reads less data.</li>
        </ul>''', '“Set a random seed in Hive”.') +
    scn('Data engineering', 'Mid-level', 'Rows missing after moving to a bucketed table',
        'A CSV load into a newly bucketed table has slightly fewer rows than the file.',
        'do you reconcile and know load paths?',
        '''<ol>
          <li>Compare counts and find missing keys with a LEFT JOIN against a staging copy.</li>
          <li>Check table properties such as skip.header.line.count; in Hive 4.2.1 the header was stored as a row and each bucket file skipped its first line.</li>
          <li>Fix: LOAD into staging, INSERT … SELECT into the bucketed table, and keep the count check.</li>
        </ol>''', 'Assuming LOAD DATA is just a file move for every table type.') +
    scn('Platform', 'Senior', 'Speeding up a daily big-table join',
        'orders (2 billion rows) and payments (2 billion rows) are joined on order_id every night, and the shuffle dominates.',
        'do you understand bucket and SMB joins and their conditions?',
        '''<ul>
          <li>Bucket (and sort) both tables on order_id with the same bucket count, partitioned by the same date.</li>
          <li>Enable the bucket map / SMB join settings and confirm in EXPLAIN that the join uses buckets.</li>
          <li>Rewrite both tables once; keep all writers producing the same bucketing. Compare runtime and shuffle bytes before and after.</li>
        </ul>''', 'Bucketing only one side, or with different bucket counts.')
)
