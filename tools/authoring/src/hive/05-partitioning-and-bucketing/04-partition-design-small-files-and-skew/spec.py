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
    module='05-partitioning-and-bucketing', lesson='04-partition-design-small-files-and-skew', n='5.4',
    module_label='Module 5 · Partitioning and bucketing',
    title='Partition design, small files and skew',
    desc='How to design Hive table layouts, with real Hive 4.2.1 measurements: over-partitioning (2,000 customer partitions: 4× the disk, twice the query time), the small files problem (INSERT INTO _copy_N files, CONCATENATE refused on external tables, compaction by INSERT OVERWRITE, hive.merge.tezfiles), and data skew (a key with 37.5% of rows, map-side aggregation, hive.groupby.skewindata, SKEWED BY … STORED AS DIRECTORIES, skew joins and salting).',
    og_desc='We partitioned by customer and the query got twice as slow. Real measurements of over-partitioning, small files and skew in Hive 4.2.1, and how to fix each.',
    minutes=35, level='Intermediate → Advanced',
    lead='Partitions and buckets speed Hive up only when the layout fits the data. This lesson measures what happens when it does not: <b>too many partitions</b> (2,000 tiny folders), <b>small files</b> from frequent loads, and <b>skew</b> where one key owns 37.5% of the rows. Then it fixes each one with tools you can run today. <b>All outputs are real</b>, from Hive 4.2.1.',
    chips=['Real Hive 4.2.1 measurements', 'Small files: detect and compact', 'Skew tools compared', 'Runs in your browser (Python)'],
)

MAIN = '''# Estimate a layout before creating it
daily_rows   = 1_621          # orders per day (real lab average)
bytes_per_row = 8             # compressed ORC bytes per row (real: 13,269 B / 1,621 rows)
years = 3

for name, parts_per_day in [("by day", 1), ("by day + city", 8), ("by day + customer", 2000)]:
    partitions = parts_per_day * 365 * years
    mb_per_part = daily_rows / parts_per_day * bytes_per_row / 1e6
    print(f"{name:18} {partitions:>9,} partitions  {mb_per_part:10.4f} MB each")
'''
RUN = dict(
    heading='Run the code: estimate before you partition',
    intro='<p>A few lines of arithmetic tell you whether a layout will produce healthy partitions. These programs also show small files and skew. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('bytes_per_row = 8             # compressed ORC bytes per row (real: 13,269 B / 1,621 rows)', 'From DESCRIBE FORMATTED of the real 10-05 partition in Lesson 5.1.'),
        ('    mb_per_part = daily_rows / parts_per_day * bytes_per_row / 1e6', 'Data per partition. Our tiny lab data is far below healthy sizes even by day; real tables are millions of times bigger.'),
    ],
    tasks=[
        dict(label='1 · Partition count and size', hint='Press <b>Run</b>. By customer gives 2.19 million partitions in 3 years, each a few bytes.', code=None),
        dict(label='2 · Predict first: a real-sized table', hint='<b>Predict first:</b> with 50 lakh orders a day, how big is one day partition? Change the numbers and run.',
             code='''daily_rows = 50_00_000
bytes_per_row = 8
print(round(daily_rows * bytes_per_row / 1e6), "MB per day partition")
print(round(daily_rows * bytes_per_row / 1e6 / 8), "MB per day+city partition")
'''),
        dict(label='3 · Files from micro-batches', hint='Every INSERT INTO adds a file. Change <code>every_minutes</code> to 60.',
             code='''every_minutes = 180
loads_per_day = 24 * 60 // every_minutes
print("files per day:", loads_per_day, " per year:", loads_per_day * 365)
'''),
        dict(label='4 · Skew: rows per reducer', hint='Real lab: reducer 1 got 35,419 rows. Salting splits the hot key into 8 sub-keys.',
             code='''hot, others = 30000, [6821, 5419, 6737, 4398, 7966, 5821, 5141, 7697]
before = max(o + (hot if i == 1 else 0) for i, o in enumerate(others))
after = max(o + hot // 8 for o in others)
print("slowest reducer before:", before, " after salting:", after)
'''),
        dict(label='5 · Spot the error', hint='This compaction job “merges” files by appending them, but forgets that the partition must be rewritten from itself. Fix the count check.', expect='error',
             code='''files = [203, 198, 205, 201, 199, 203, 206, 206]     # rows per small file (sums to 1,621)
merged = [sum(files)]                                # INSERT OVERWRITE ... SELECT from itself
merged_rows = sum(merged) + files[0]                 # bug: an old file was kept as well
assert merged_rows == sum(files), f"{merged_rows} rows after compaction, expected {sum(files)}"
print(merged)
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: watch file counts and query the skewed table',
    intro='<p>Statements to try in Beeline on the TiffinGo data. <b>Outputs are real</b>, from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · Merge settings and their defaults', cmd='SET hive.merge.tezfiles;\nSET hive.merge.mapfiles;\nSET hive.merge.smallfiles.avgsize;\nSET hive.merge.size.per.task;\nSET hive.skewjoin.key;\nSET hive.map.aggr;', file='Beeline',
             output='\n'.join(l for l in capf('l54_mergeset.txt').split('\n') if '=' in l),
             note='Tez jobs do not merge output files unless you set <code>hive.merge.tezfiles=true</code>. When they do, files are merged if their average size is below 16 MB, into files of about 256 MB.'),
        dict(title='2 · Find small files from the metastore', cmd="DESCRIBE FORMATTED events_small PARTITION (order_date='2026-10-06');\n-- look at numFiles and totalSize\nSELECT regexp_extract(INPUT__FILE__NAME, '[^/]+$', 0) AS file, COUNT(*) AS n\nFROM events_small WHERE order_date = '2026-10-05' GROUP BY INPUT__FILE__NAME;", file='Beeline',
             output='|   | numFiles   | 1     |\n|   | numRows    | 1678  |\n|   | totalSize  | 7682  |\n\n+-----------+-------+\n|   file    |   n   |\n+-----------+-------+\n| 000000_0  | 1621  |\n+-----------+-------+',
             note='totalSize ÷ numFiles is the average file size of a partition. Both days now have one file after the merge and the rewrite. A query over the metastore tables (or a script over SHOW PARTITIONS) can flag partitions with many tiny files.'),
        dict(title='3 · The skewed table in action', cmd="SET hive.tez.exec.print.summary=true;\nSELECT COUNT(*) AS n FROM orders_lb WHERE restaurant_id = 0;\nSELECT COUNT(*) AS n FROM orders_lb WHERE restaurant_id = 40;", file='Beeline',
             output=capf('l54_lb.txt'),
             note='The hot value lives in its own folder, so a query for it skips the 50,000 other rows. A query for any other restaurant reads only the default folder, skipping the 30,000 hot rows.'),
    ],
)

TRACE = dict(
    heading='Salting a hot key, one row at a time',
    intro='<p>Salting appends a small number to the hot key so its rows spread over several reducers. Watch <code>load</code> per reducer.</p>',
    code='''rows = [0, 0, 0, 0, 40, 0, 0, 65]       # restaurant ids; 0 is hot
SALTS = 4
load = {}
for i, rid in enumerate(rows):
    key = f"{rid}_{i % SALTS}" if rid == 0 else f"{rid}_0"
    load[key] = load.get(key, 0) + 1
print(load)
''',
    notes={5: 'Salt :: Only the hot key is split; other keys keep one sub-key. The small side of a join must be copied once per salt value.', 7: 'Result :: Restaurant 0’s six rows are spread over four sub-keys instead of one.'},
)

WORKED_INTRO = 'Three layout reviews from TiffinGo’s data platform team.'
EXAMPLES = [
    dict(level='b', tag='Design review · partitions', title='Is this partition column a good idea?',
         problem='<p>For each proposed partition column, estimate partitions per year and MB per partition at 50 lakh orders a day (about 40 MB of ORC a day), and flag anything under 10 MB.</p>',
         inp='order_date (1/day), city (8/day), restaurant_id (120/day), customer_id (2,000/day)',
         approach=['Partitions per year = values per day × 365.', 'MB per partition = 40 MB ÷ values per day.', 'Flag small partitions.'],
         code='''day_mb = 40
cols = {"order_date": 1, "order_date+city": 8, "order_date+restaurant": 120, "order_date+customer": 2000}
for c, per_day in cols.items():
    mb = day_mb / per_day
    print(f"{c:22} {per_day * 365:>8,}/yr  {mb:7.2f} MB  {'OK' if mb >= 10 else 'TOO SMALL'}")
''', notes={4: 'Size :: 40 MB a day split 8 ways is 5 MB per partition, already too small for HDFS-sized blocks.'},
         tryit='Only order_date passes. City and restaurant are better as plain columns (or buckets), filtered with ORC statistics.'),
    dict(level='i', tag='Operations · compaction', title='Which partitions need compaction?',
         problem='<p>From partition statistics (numFiles, totalSize), list partitions whose average file size is under 16 MB and that have more than 4 files: the candidates for a nightly rewrite.</p>',
         inp='four partitions with (numFiles, totalSize MB)',
         approach=['Average = totalSize ÷ numFiles.', 'Select small averages with many files.', 'Generate the rewrite statement.'],
         code='''parts = {"2026-10-03": (2, 900), "2026-10-04": (288, 410), "2026-10-05": (8, 0.011), "2026-10-06": (1, 380)}
for dt, (n, mb) in parts.items():
    avg = mb / n
    if avg < 16 and n > 4:
        print(f"{dt}: {n} files, avg {avg:.3f} MB -> INSERT OVERWRITE ... PARTITION (order_date='{dt}')")
''', notes={4: 'Rule :: The same threshold Hive’s merge uses by default (hive.merge.smallfiles.avgsize = 16 MB).'},
         tryit='10-05 is our real lab partition (8 files, 11,300 bytes). After the rewrite it had 1 file.'),
    dict(level='a', tag='Performance · skew', title='Will salting help this join?',
         problem='<p>The slowest task decides the runtime. Estimate the slowest reducer before and after salting the hot key 8 ways, when 8 reducers share 80,000 rows and one key has 30,000.</p>',
         inp='real reducer loads: 6821, 35419, 6737, 4398, 7966, 5821, 5141, 7697',
         approach=['Remove the hot key from its reducer.', 'Spread it evenly over all 8.', 'Compare the maximum load.'],
         code='''loads = [6821, 35419, 6737, 4398, 7966, 5821, 5141, 7697]
hot = 30000
base = loads[:]
base[1] -= hot
salted = [b + hot // 8 for b in base]
print("before", max(loads), "after", max(salted), f"speed-up x{max(loads) / max(salted):.1f}")
''', notes={4: 'Base :: Reducer 1 without the hot key has 5,419 rows, like the others.'},
         tryit='About 3× faster on the slowest task. The cost: the small side of the join is copied 8 times, so salting suits a hot key joined with a modest table.'),
]

QUIZ = mix([
    dict(q='Beginner: Why is partitioning by customer_id usually a bad idea?', options=['Hive forbids it', 'It creates a huge number of tiny partitions and files', 'customer_id cannot be a partition column', 'It makes inserts impossible'], answer=1,
         why='Real lab: 2,000 partitions, 4× the disk and twice the query time for the same data.'),
    dict(q='Beginner: What does each INSERT INTO into the same partition do to the files?', options=['Rewrites the existing file', 'Adds a new file (_copy_N)', 'Appends to the last file', 'Deletes old files'], answer=1,
         why='That is how frequent loads create small files.'),
    dict(q='Beginner: What is data skew?', options=['Wrong data types', 'Some keys have far more rows than others', 'Too many columns', 'Unsorted files'], answer=1,
         why='All rows of a key go to one task, so a hot key makes one slow task.'),
    dict(q='Intermediate: ALTER TABLE … CONCATENATE failed with Error 30034. Why?', options=['ORC is not supported', 'It works only on managed tables, and Hive 4 created an external table', 'The partition was empty', 'CONCATENATE needs Spark'], answer=1,
         why='Rewrite the partition with INSERT OVERWRITE … SELECT from itself instead.'),
    dict(q='Intermediate: What is the default of hive.merge.tezfiles in our Hive 4.2.1 lab?', options=['true', 'false', 'auto', '16 MB'], answer=1,
         why='Set it to true to merge small output files at the end of Tez jobs.'),
    dict(q='Intermediate: Why is GROUP BY skew usually milder than JOIN skew?', options=['GROUP BY is sorted', 'Map-side aggregation pre-sums each key in the map tasks', 'GROUP BY uses fewer reducers', 'It is not'], answer=1,
         why='hive.map.aggr=true: a hot key reaches the reducer as one partial result per map task.'),
    dict(q='Advanced: What did SET hive.groupby.skewindata=true change in EXPLAIN?', options=['Nothing', 'An extra reducer stage: Reducer 3 <- Reducer 2', 'A map join', 'Fewer map tasks'], answer=1,
         why='First stage spreads keys randomly, second stage combines partial results.'),
    dict(q='Advanced: SKEWED BY (restaurant_id) ON (0) STORED AS DIRECTORIES does what?', options=['Drops restaurant 0', 'Stores rows of restaurant 0 in their own sub-folder', 'Creates 0 buckets', 'Forces a skew join'], answer=1,
         why='Real lab: restaurant_id=0/ and HIVE_DEFAULT_LIST_BUCKETING_DIR_NAME/; a query for 0 read 30,000 rows.'),
])

REVISION = [
    '<b>Partition column:</b> used in most filters + few enough values that each partition stays large. Dates yes, ids no.',
    '<b>Estimate first:</b> values × history = partitions; daily size ÷ values per day = size per partition.',
    '<b>Over-partitioning (real):</b> 2,000 customer partitions → 1.72 MB vs 0.44 MB, GROUP BY 7.3 s vs 3.2 s.',
    '<b>Small files</b> come from INSERT INTO micro-batches (_copy_N), many tasks × many partitions, streaming.',
    '<b>Prevent:</b> batch loads, <code>DISTRIBUTE BY</code> the partition key, <code>hive.merge.tezfiles=true</code> (default false; avgsize 16 MB).',
    '<b>Compact:</b> <code>INSERT OVERWRITE … PARTITION … SELECT</code> from itself (8 files → 1). CONCATENATE = managed tables only (Error 30034).',
    '<b>Skew:</b> find top keys; GROUP BY → map-side aggregation (default) + <code>hive.groupby.skewindata</code>; JOIN → map join, <code>hive.optimize.skewjoin</code>, salting.',
    '<b>Skewed tables:</b> <code>SKEWED BY (col) ON (v) STORED AS DIRECTORIES</code> → hot value in its own folder.',
    'NULL join keys are a common hidden hot key: filter them before joining.',
]
FAQ = [
    ('What file size should I aim for?', 'On HDFS, files near the block size (128 or 256 MB) are a common target; on cloud object stores, files of a few hundred MB work well. The exact number matters less than avoiding thousands of KB-sized files. Hive’s own merge defaults (merge below 16 MB average, into about 256 MB) are a sensible guide.'),
    ('Why do small files hurt the NameNode?', 'The HDFS NameNode keeps every file, folder and block in memory, roughly 150 bytes each. A billion tiny files can exhaust it even if the data itself is small. Every query also pays to list, open and read the footer of each file.'),
    ('Is skew a problem for map tasks too?', 'Much less. Map tasks split input by file and block, not by key, so they get similar amounts of data. Skew appears when rows are shuffled by key: GROUP BY, JOIN, DISTRIBUTE BY, window PARTITION BY and dynamic partition inserts with DISTRIBUTE BY.'),
    ('Should I use hive.groupby.skewindata all the time?', 'No. It adds a stage to every GROUP BY, which costs time when there is no skew, and it does not support every query shape (for example several DISTINCT aggregates on different columns). Use it for specific queries with known hot keys.'),
    ('Do Iceberg tables fix these problems?', 'They help a lot: hidden partitioning avoids wrong filters, partition specs can change without rewriting old data, and compaction is a built-in procedure. You still have to pick a sensible partition granularity and handle skew in joins. Module 7 covers Iceberg in Hive.'),
]

PRACTICE_INTRO = 'Programs that estimate and fix layouts, with the HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Average file size', stmt='Compute the average file size of a partition from its statistics.', inp='numFiles 8, totalSize 11,300',
         code='''print(11300 / 8, "bytes per file")
''', explain='1,412 bytes per file: the real 10-05 partition before compaction.'),
    dict(level='easy', title='Partitions in 3 years', stmt='How many partitions does a date + city layout create in 3 years?', inp='8 cities',
         code='''print(365 * 3 * 8)
''', explain='8,760 partitions. Multiply by files per partition to get the file count.'),
    dict(level='easy', title='Top key share', stmt='What share of rows does the hot restaurant have?', inp='30,000 of 80,000',
         code='''print(f"{100 * 30000 / 80000:.1f}%")
''', explain="37.5%, as in the real query. In HiveQL: <code>COUNT(*) / SUM(COUNT(*)) OVER ()</code>."),
    dict(level='medium', title='Files written by a dynamic insert', stmt='How many files does a dynamic insert write when 20 tasks each see all 30 days, with and without DISTRIBUTE BY order_date?', inp='20 tasks, 30 days',
         code='''tasks, days = 20, 30
print(tasks * days, "without;", days, "with DISTRIBUTE BY")
''', explain='600 vs 30. DISTRIBUTE BY sends each day to one reducer.'),
    dict(level='medium', title='Is the merge triggered?', stmt='Hive merges Tez output when the average file size is below 16 MB. Check three jobs.', inp='(files, total MB)',
         code='''for files, mb in [(4, 0.008), (10, 900), (200, 600)]:
    avg = mb / files
    print(files, mb, f"avg {avg:.3f} MB", "merge" if avg < 16 else "no merge")
''', explain='Our real job (4 files, 8 KB) was merged into one file once hive.merge.tezfiles was on.'),
    dict(level='medium', title='Pick the coarser partition', stmt='Choose day or month partitioning so that partitions are at least 100 MB.', inp='daily data 12 MB',
         code='''daily = 12
for name, days in [("day", 1), ("month", 30)]:
    print(name, daily * days, "MB", "OK" if daily * days >= 100 else "too small")
''', explain='Monthly partitions (360 MB) are healthy; daily ones (12 MB) are too small. Queries for one day still prune to one month and use ORC statistics inside.'),
    dict(level='business', title='Cost of NULL keys in a join', stmt='3 crore orders have a NULL coupon_id. How many rows go to the NULL key’s reducer, and how many after filtering NULLs first?', inp='3 crore NULL rows',
         code='''null_rows = 3_00_00_000
print("to one reducer:", null_rows)
print("after WHERE coupon_id IS NOT NULL:", 0)
''', explain='NULL never matches in an inner join, so filtering it first removes the hottest key without changing the result.'),
    dict(level='business', title='Monthly compaction plan', stmt='A table gets 96 loads a day. How many files does a nightly compaction of yesterday save per month?', inp='96 loads/day, 1 file after compaction',
         code='''loads, days = 96, 30
print("files saved per month:", (loads - 1) * days)
''', explain='2,850 files a month that no query has to open again.'),
]

SCN_INTRO = 'Layout questions separate people who used Hive in production from people who read about it. Expect numbers.'
SCENARIOS = (
    scn('Any company · Hadoop', 'Fresher', '“What is the small files problem?”',
        'Explain the small files problem and two ways to fix it.',
        'do you know the cause and both prevention and cure?',
        '<p>Many files much smaller than the block size overload the NameNode, which holds metadata for every file in memory, and slow queries because each file must be listed, opened and read. Prevent it by writing fewer, larger files (batch loads, DISTRIBUTE BY the partition key, <code>hive.merge.tezfiles</code>). Cure it by compacting: rewrite partitions with INSERT OVERWRITE, CONCATENATE for managed ORC tables, or ACID/Iceberg compaction.</p>', '“Increase the block size”, which does not reduce the number of files.') +
    scn('Data engineering', 'Mid-level', 'The partitioned table got slower',
        'A colleague re-partitioned a table by (date, store_id) with 5,000 stores. Full-month reports became slower.',
        'can you reason with partition counts and sizes?',
        '''<ol>
          <li>Count partitions (30 × 5,000 = 150,000 a month) and average file size.</li>
          <li>Explain: listing and opening that many tiny files outweighs pruning.</li>
          <li>Propose: partition by date only; bucket or sort by store_id; rely on ORC statistics; compare with counters.</li>
        </ol>''', 'Adding more memory to HiveServer2.') +
    scn('E-commerce', 'Mid-level', 'One task runs for an hour',
        'A daily join of orders and sellers finishes 99% of tasks in five minutes, then one task runs for an hour.',
        'do you recognise skew and know the remedies?',
        '''<ul>
          <li>Find the hot key: top sellers by row count; check NULL keys too.</li>
          <li>If sellers is small, force a map join; otherwise try <code>hive.optimize.skewjoin</code>, or salt the hot keys.</li>
          <li>Filter NULL keys before joining; measure the slowest task again.</li>
        </ul>''', '“Add more reducers”: the hot key still goes to just one of them.') +
    scn('Platform', 'Senior', 'A near-real-time table',
        'Product wants orders queryable within 5 minutes in Hive, and the table must stay fast for a year.',
        'can you design for both freshness and file health?',
        '''<ul>
          <li>Partition by date; land 5-minute batches (accepting small files for today).</li>
          <li>Merge within each job (<code>hive.merge.tezfiles</code>) and compact yesterday nightly; monitor files per partition.</li>
          <li>Better long-term: an ACID or Iceberg table with automatic compaction; document the freshness and cost trade-off.</li>
        </ul>''', 'Partitioning by minute to “make queries faster”.')
)
