import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()

RED = [6821, 35419, 6737, 4398, 7966, 5821, 5141, 7697]
def reducers(y=44, hi=1, mx=36000, h=80):
    o = ''
    for k, v in enumerate(RED):
        bh = round(h * v / mx)
        o += fill(28 + k * 40, y + h - bh, 30, bh, 'red' if k == hi else 'blue') + t(43 + k * 40, y + h + 12, f'R{k}', 7.4, 'ink2', mono=True)
    return o

# ---------------------------------------------------------------- story
sc = (box(10, 12, 196, 128, 'card') + t(108, 30, 'Too many partitions', 8.8, 'red', bold=True) +
      ''.join(fill(22 + (k % 16) * 11, 42 + (k // 16) * 11, 8, 8, 'red', rx=1) for k in range(112)) + t(108, 132, '2,000 folders × 858-byte files', 7.2, 'ink2') +
      box(222, 12, 196, 128, 'card') + t(320, 30, 'Small files', 8.8, 'amber', bold=True) +
      ''.join(fill(236 + (k % 8) * 21, 46 + (k // 8) * 22, 16, 14, 'amber', rx=2) for k in range(24)) + t(320, 132, '8 tiny files from 8 small inserts', 7.2, 'ink2') +
      box(434, 12, 196, 128, 'card') + t(532, 30, 'Skew', 8.8, 'acc', bold=True) +
      ''.join(fill(448 + k * 22, 120 - (78 if k == 1 else 14 + (k * 7) % 12), 16, (78 if k == 1 else 14 + (k * 7) % 12), 'red' if k == 1 else 'blue', rx=2) for k in range(8)) + t(532, 132, 'one reducer gets 35,419 rows', 7.2, 'ink2'))
scene_svg = scene('Three panels: on the left a grid of two thousand tiny partition folders, in the middle many tiny files, on the right eight reducer bars where one bar is five times taller than the others.', sc,
                  'Three ways a good layout goes bad: <tspan font-weight="700" class="s-acc">too many partitions, small files and skew</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“We partitioned everything. Why is it slower?”</h2>
  <div class="story">
    <p class="narration">Excited by Lessons 5.1–5.3, Kabir’s team partitions a copy of orders by <code>customer_id</code>, loads an events table every three hours, and onboards a cloud-kitchen chain that brings 30,000 orders under a single restaurant id. A week later, three complaints arrive: a simple report takes twice as long, a partition holds a pile of tiny files, and one job always waits for one last task.</p>

{scene_svg}

K> Sir, partitions and buckets were supposed to make things faster!
A> They do, when the layout fits the data. Partition by customer and you get 2,000 folders of 858-byte files: our real test ran a full GROUP BY in 7.3 seconds instead of 3.2. Load every three hours and each insert adds another small file. And when one key owns 37.5% of the rows, the task that receives it does five times the work of the others.
R> So how do we decide?
A> With a few numbers and a few rules. Today we measure all three problems in the lab, fix the small files two ways (and find that CONCATENATE refuses Hive 4’s default tables), and look at Hive’s skew tools: map-side aggregation, <code>hive.groupby.skewindata</code> and skewed tables. All outputs are real, from Hive 4.2.1.
  </div>
</section>
'''

lv = '''
LEVELS> Layout design at three levels
L1> Shelves, boxes and one overloaded worker
      <ul>
        <li><b>Too many partitions:</b> a shelf with 2,000 boxes, each holding one sheet. Finding anything means opening many boxes.</li>
        <li><b>Small files:</b> every small delivery adds a new envelope to the box. Eventually the box is full of envelopes, each with a few lines.</li>
        <li><b>Skew:</b> eight workers share the work by first letter, but half the parcels start with “A”. One worker is still busy long after the others go home.</li>
      </ul>
L2> The rules of thumb
      <ul>
        <li><b>Partition column:</b> used in most filters, with a number of values that keeps each partition large (in production, hundreds of MB or more). Dates are the classic choice; ids almost never are.</li>
        <li><b>Count before you choose:</b> distinct values × years of history = partitions. 2,000 customers gave 2,000 folders and 2,000 files on day one.</li>
        <li><b>Small files</b> come from frequent small inserts, many tasks writing to many partitions, and streaming. Fix with fewer, bigger writes, <code>DISTRIBUTE BY</code> the partition key, <code>hive.merge.tezfiles=true</code>, or periodic compaction by rewriting partitions.</li>
        <li><b>Skew:</b> check the top keys first: <code>SELECT key, COUNT(*) … ORDER BY 2 DESC LIMIT 10</code>.</li>
      </ul>
L3> What Hive 4.2.1 really did in our lab
      <ul>
        <li><code>ALTER TABLE … CONCATENATE</code> was refused (Error 30034: managed tables only), and a plain <code>CREATE TABLE</code> in Hive 4 makes an external table (Lesson 2.2). Rewriting the partition with <code>INSERT OVERWRITE … SELECT</code> from itself merged 8 files into 1.</li>
        <li><code>hive.merge.tezfiles</code> is <b>false</b> by default; turning it on merged 4 output files into 1 in the same statement (threshold <code>hive.merge.smallfiles.avgsize</code> = 16 MB).</li>
        <li>GROUP BY already aggregates in the map tasks (<code>hive.map.aggr=true</code>), which shrinks most GROUP BY skew. <code>hive.groupby.skewindata=true</code> adds a second reduce stage that first spreads keys randomly.</li>
        <li><b>Skewed tables:</b> <code>SKEWED BY (restaurant_id) ON (0) STORED AS DIRECTORIES</code> stored the big key in its own folder; a query for it read 30,000 rows, other keys read the 50,000 in the default folder.</li>
        <li>Skew joins: <code>hive.optimize.skewjoin</code> (default false) handles keys above <code>hive.skewjoin.key</code> (100,000 rows) with a follow-up map join.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Layout design, the small files problem and data skew</h2>
''' + def_block(
    '<b>Partition design</b> is the choice of partition (and bucket) columns so that common queries prune most data while each partition remains large enough to be read efficiently. The <b>small files problem</b> occurs when a table consists of many files much smaller than the storage block size, which increases NameNode (or object store) metadata load, task start-up and file-open overhead. <b>Data skew</b> is an uneven distribution of rows across keys, so that the partitions of a shuffle (or the partitions or buckets of a table) receive very different amounts of data and the slowest task determines the job’s run time.',
    'A good layout prunes a lot but keeps folders and files big. Too many partitions or too many tiny files make every query open more files than needed. Skew means one key has far more rows than the others, so one task does most of the work while the rest wait.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Over-partitioning', 'So many partitions that each one holds very little data.'),
    ('Small file', 'A file much smaller than the block size (128 MB on HDFS by default).'),
    ('Compaction', 'Rewriting many small files into fewer large ones.'),
    ('hive.merge.tezfiles', 'Merge small output files at the end of a Tez job (default false).'),
    ('Skew', 'A few keys have far more rows than the rest.'),
    ('Straggler', 'The last, slow task that keeps the whole job waiting.'),
    ('hive.groupby.skewindata', 'Two-stage GROUP BY: random spread first, then final aggregation.'),
    ('Skewed table', '<code>SKEWED BY (col) ON (values)</code>: stores heavy values separately.'),
]) + '''

  <h3>The three problems in numbers (real lab)</h3>
''' + table(['Problem', 'What we measured', 'Effect'], [
    ['Over-partitioning', '<code>orders_by_cust</code>: 2,000 partitions, 2,000 files, median 858 bytes', '1.72 MB on disk instead of 0.44 MB; GROUP BY 7.3 s instead of 3.2 s'],
    ['Small files', '8 small inserts → 8 files of 1.3–1.5 KB in one partition', '8 files to open; after rewrite: 1 file, 7.5 KB'],
    ['Skew', 'restaurant 0 = 30,000 of 80,000 rows (37.5%)', 'one of 8 reducers gets 35,419 rows, the others 4,398–7,966'],
], minw=680) + lv + '''
EXAM> “What is the small files problem in Hadoop/Hive and how do you fix it?” Say: many files much smaller than the block size overload the NameNode and add task and file-open overhead; fix by writing fewer, larger files (batching, DISTRIBUTE BY partition key, merge settings) and by compacting existing partitions. For skew, mention identifying hot keys, map-side aggregation, <code>hive.groupby.skewindata</code>, skew join settings and salting.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>A checklist for designing and fixing layouts</h2>
''' + table(['Question', 'Good sign', 'Warning sign'], [
    ['How do most queries filter?', 'By date (and maybe region)', 'By an id or a free-text column'],
    ['Distinct values of the partition column × history', 'Hundreds to a few thousand partitions per year', 'Tens of thousands per year'],
    ['Data per partition', 'Hundreds of MB or more', 'KBs or a few MB'],
    ['Files per partition', 'A few, of large size', 'Dozens of small ones (_copy_1, _copy_2 …)'],
    ['Top key share', 'Below a few percent', 'One key holds 10%+ of rows'],
], minw=640) + '''
''' + table(['Problem', 'Fixes', 'Notes'], [
    ['Over-partitioning', 'Partition by a coarser column (date, month); move ids to <b>bucketing</b>; rely on ORC/Parquet statistics', 'Recreate the table and copy the data'],
    ['Small files (new)', 'Batch inserts; <code>DISTRIBUTE BY</code> partition key; <code>SET hive.merge.tezfiles=true</code>', 'Avg-size threshold 16 MB by default'],
    ['Small files (existing)', '<code>INSERT OVERWRITE … PARTITION … SELECT</code> from itself; <code>ALTER TABLE … CONCATENATE</code> (managed tables only); ACID compaction (Module 7)', 'Run off-peak, partition by partition'],
    ['GROUP BY skew', 'Map-side aggregation (on by default); <code>SET hive.groupby.skewindata=true</code>', 'Adds a stage'],
    ['JOIN skew', '<code>SET hive.optimize.skewjoin=true</code>; map join if one side is small; <b>salting</b> the hot key', 'Check EXPLAIN'],
    ['Known hot values', '<code>SKEWED BY (col) ON (v) STORED AS DIRECTORIES</code>', 'Hot value gets its own folder'],
], minw=720) + '''
WARN> Do not “fix” slowness by adding partition levels. Every extra level multiplies the number of folders and divides the data per file. Measure with counters and file listings first.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Measure each problem, then fix it</h2>
  <p>All outputs are real, from the Hive 4.2.1 lab (database <code>tiffingo</code>).</p>
''' + stepper([
    ('Step 1 · Over-partitioning: partition by customer_id',
     code('sql', 'Beeline', "CREATE TABLE orders_by_cust (order_id INT, city STRING, order_ts TIMESTAMP,\n  amount DECIMAL(10,2))\nPARTITIONED BY (customer_id INT) STORED AS ORC;\n\nINSERT OVERWRITE TABLE orders_by_cust PARTITION (customer_id)\nSELECT order_id, city, order_ts, amount, customer_id FROM orders;\n-- Error 20004: too many dynamic partitions (limit 100 per node)\n\nSET hive.exec.max.dynamic.partitions=3000;\nSET hive.exec.max.dynamic.partitions.pernode=3000;\n-- run the INSERT again\nSELECT COUNT(*) AS partitions FROM (SELECT DISTINCT customer_id FROM orders_by_cust) x;", tables(capf('l54_overpart2.txt'))[0] + "\n\n$ ls …/orders_by_cust | wc -l      → 2000 folders, 2000 files\n  file sizes: min 707, median 858, max 1047 bytes"),
     'The default limits stopped the first try, a hint that something is off. After raising them: 2,000 folders, each with one file under 1.1 KB. On HDFS every file and folder is an object in NameNode memory, whatever its size.'),
    ('Step 2 · Measure the cost',
     code('sql', 'Beeline', "SELECT city, COUNT(*), SUM(amount) FROM <table> GROUP BY city;\n-- run 3 times on each table, median shown", capf('l54_overpart_cmp.txt')),
     'Same 50,000 rows. The customer-partitioned table is <b>4 times bigger</b> on disk (each ORC file carries its own header, footer and statistics) and the full query takes more than twice as long, because Hive lists 2,000 partitions and opens 2,000 files. Partitioning by date (30 partitions) cost almost nothing.'),
    ('Step 3 · Small files from frequent loads',
     code('sql', 'Beeline', "CREATE TABLE events_small (order_id INT, city STRING, amount DECIMAL(10,2))\nPARTITIONED BY (order_date DATE) STORED AS ORC;\n\n-- every 3 hours a job appends the latest orders:\nINSERT INTO events_small PARTITION (order_date='2026-10-05')\nSELECT order_id, city, amount FROM orders\nWHERE order_date = '2026-10-05' AND hour(order_ts) < 3;\n-- … 7 more runs for 03–05, 06–08, …, 21–23", capf('l54_small_files.txt')),
     'Each <code>INSERT INTO</code> adds a new file (<code>_copy_1</code>, <code>_copy_2</code> …) instead of changing the old ones. One day already has 8 files; a year of 3-hourly loads would be 2,920 files for one table, and every query on a day must open all of them.'),
    ('Step 4 · Compact: CONCATENATE refused, rewrite works',
     code('sql', 'Beeline', "ALTER TABLE events_small PARTITION (order_date='2026-10-05') CONCATENATE;\n\n-- rewrite the partition from itself instead:\nINSERT OVERWRITE TABLE events_small PARTITION (order_date='2026-10-05')\nSELECT order_id, city, amount FROM events_small WHERE order_date = '2026-10-05';", capf('l54_compacted.txt').replace('\n\n> INSERT OVERWRITE TABLE events_small PARTITION (order_date=\'2026-10-05\')\n  SELECT order_id, city, amount FROM events_small WHERE order_date=\'2026-10-05\';', '\n')),
     'CONCATENATE (a fast ORC/RCFile stripe merge) works only on managed tables, and Hive 4 turned our plain CREATE TABLE into an external one. Rewriting the partition reads it once and writes one file: 8 files and 11,300 bytes became 1 file and 7,520 bytes, with the same count and sum. Schedule this for “closed” partitions, such as yesterday.'),
    ('Step 5 · Prevent small files at write time',
     code('sql', 'Beeline', "SET mapreduce.job.reduces=4;\nINSERT OVERWRITE TABLE events_small PARTITION (order_date='2026-10-06')\nSELECT order_id, city, amount FROM orders WHERE order_date = '2026-10-06'\nDISTRIBUTE BY rand();           -- 4 reducers → 4 files\n\nSET hive.merge.tezfiles=true;   -- then run the same INSERT again", capf('l54_merge.txt')),
     'Four reducers wrote four 2 KB files. With <code>hive.merge.tezfiles=true</code> Hive added a merge step and wrote one 7.5 KB file, because the average file was below <code>hive.merge.smallfiles.avgsize</code> (16 MB). For dynamic partition inserts, <code>DISTRIBUTE BY</code> the partition column does the same job: each partition is written by one reducer.'),
    ('Step 6 · Skew: find the hot key',
     code('sql', 'Beeline', "-- a cloud-kitchen chain joins: 30,000 extra orders under restaurant_id 0\nSELECT restaurant_id, COUNT(*) AS n,\n       ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct\nFROM orders_skew GROUP BY restaurant_id ORDER BY n DESC LIMIT 4;\n\n-- rows per reducer if keys are hashed into 8 reducers\nSELECT pmod(murmur_hash(restaurant_id), 8) AS reducer, COUNT(*) AS rows_to_reducer\nFROM orders_skew GROUP BY pmod(murmur_hash(restaurant_id), 8) ORDER BY reducer;", capf('l54_skewdata.txt')),
     'One restaurant owns 37.5% of the rows; the next is at 1.3%. With rows routed by key, reducer 1 gets 35,419 rows while the others get 4,398–7,966: the job waits for that one task. (The second query only illustrates the routing; Hive’s shuffle uses its own hash, but every row of a key always goes to the same reducer.)'),
    ('Step 7 · Hive’s skew tools',
     code('sql', 'Beeline', "SET hive.groupby.skewindata;   SET hive.optimize.skewjoin;   SET hive.map.aggr;\n\nSET hive.groupby.skewindata=true;\nEXPLAIN SELECT restaurant_id, SUM(amount) FROM orders_skew GROUP BY restaurant_id;\n\nCREATE TABLE orders_lb (order_id INT, customer_id INT, restaurant_id INT,\n  city STRING, amount DECIMAL(10,2))\nSKEWED BY (restaurant_id) ON (0) STORED AS DIRECTORIES\nSTORED AS ORC;\nINSERT OVERWRITE TABLE orders_lb SELECT * FROM orders_skew;",
          'hive.groupby.skewindata=false · hive.optimize.skewjoin=false · hive.map.aggr=true\n\n-- default plan:          Reducer 2 <- Map 1 (SIMPLE_EDGE)\n-- with skewindata=true:  Reducer 2 <- Map 1 (SIMPLE_EDGE)\n                          Reducer 3 <- Reducer 2 (SIMPLE_EDGE)\n\n$ find …/orders_lb -type f\n./HIVE_DEFAULT_LIST_BUCKETING_DIR_NAME/000000_0\n./restaurant_id=0/000000_0\n\n' + capf('l54_lb.txt')),
     'Even the default plan has a Group By in Map 1: map-side aggregation turns 30,000 rows of restaurant 0 into one partial sum per task, so GROUP BY skew is usually mild. <code>skewindata</code> adds Reducer 3 (spread randomly first, then combine). The skewed table put restaurant 0 in its own folder: querying it read 30,000 rows, while any other restaurant read the 50,000 in the default folder.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('> INSERT … PARTITION (customer_id) …', W), ('  Error 20004: too many dynamic partitions', RD), ('> SET …max.dynamic.partitions(.pernode)=3000;', W), ('| partitions |', W), ('| 2000       |', Y)]),
    term([('table            files   bytes      GROUP BY', W), ('orders               1   437,536    3.2 s', G), ('orders_by_day       30   409,088    3.4 s', G), ('orders_by_cust    2000 1,723,882    7.3 s', RD)], size=7.6),
    term([('$ ls …/order_date=2026-10-05/', W), ('1452 000000_0', Y), ('1354 000000_0_copy_1', Y), ('…    (8 files)', Y), ('> … CONCATENATE;  Error 30034', RD), ('> INSERT OVERWRITE … → 7520 000000_0', G)]),
    term([('| restaurant_id | n     | pct  |', W), ('| 0             | 30000 | 37.5 |', RD), ('| 40            | 1010  | 1.3  |', G), ('| reducer 1     | 35419 rows   |', RD), ('| reducers 0,2-7| 4398–7966    |', G)], size=7.6),
    term([('> SET hive.groupby.skewindata=true;', W), ('> EXPLAIN … GROUP BY restaurant_id;', W), ('  Reducer 3 <- Reducer 2 (SIMPLE_EDGE)', G), ('> SKEWED BY (restaurant_id) ON (0) …', W), ('  ./restaurant_id=0/000000_0', G)]),
]
def tinyfolders(n, size, tone):
    return ''.join(fill(20 + (k % 26) * 12.5, 42 + (k // 26) * 12, 9, 9, tone, rx=1) for k in range(n))
B1 = [
    t(180, 22, 'One folder + one file per customer', 9.4, bold=True) + tinyfolders(182, 9, 'red') + t(180, 136, '… 2,000 of them, ~858 bytes each', 7.8, 'ink2') + cap('Each file and folder costs metadata and an open.', '', 'amber', y=150, h=34),
    t(180, 22, 'Fixed overhead per file', 9.4, bold=True) + fill(30, 50, 300 * 437536 / 1723882, 18, 'green') + t(30, 44, 'flat: 437,536 bytes', 8, 'green', anchor='start', bold=True) + fill(30, 96, 300, 18, 'red') + t(30, 90, '2,000 partitions: 1,723,882 bytes', 8, 'red', anchor='start', bold=True) +
    cap('ORC header, footer and statistics × 2,000 files.', 'Plus listing 2,000 folders per query.', 'amber', y=150, h=46),
    t(180, 22, 'INSERT INTO adds a file every time', 9.4, bold=True) + ''.join(box(24 + k * 40, 50, 34, 40, 'amber') + t(41 + k * 40, 74, f'_{k}', 7.4, 'ink', mono=True) for k in range(8)) + arrow(180, 96, 180, 114, 'green', 2) + box(150, 116, 60, 22, 'green') + t(180, 131, '1 file', 7.8, bold=True) + cap('Rewrite the partition once it is closed.', '', 'green', y=150, h=34),
    t(180, 22, 'Rows per reducer', 9.4, bold=True) + reducers() + cap('One reducer holds the hot key: the straggler.', 'All rows of a key go to the same reducer.', 'amber', y=150, h=46),
    t(180, 22, 'Spread first, combine later', 9.4, bold=True) + box(24, 48, 92, 70, 'blue') + t(70, 64, 'Map 1', 8.4, bold=True) + t(70, 80, 'partial sums', 7.4, 'ink2') + t(70, 94, '(map.aggr)', 7, 'ink2', mono=True) +
    arrow(118, 82, 140, 82, 'ink3') + box(142, 48, 92, 70, 'green') + t(188, 64, 'Reducer 2', 8.4, bold=True) + t(188, 80, 'random spread', 7.4, 'ink2') + arrow(236, 82, 258, 82, 'ink3') + box(260, 48, 80, 70, 'green') + t(300, 64, 'Reducer 3', 8.4, bold=True) + t(300, 80, 'final sum', 7.4, 'ink2') +
    cap('skewindata = two stages instead of one.', '', 'green', y=150, h=34),
]
see_caps = ['Partitioning by customer needed raised limits and created 2,000 partitions.',
            'The same data took 4× the disk and twice the query time.',
            'Small inserts left 8 tiny files; CONCATENATE was refused; a rewrite merged them.',
            'One restaurant has 37.5% of rows; one reducer gets 35,419 of them.',
            'Two-stage GROUP BY and a skewed table are Hive’s built-in answers.']
behind_caps = ['Every partition is a folder and a file, however few rows it holds.',
               'Each ORC file carries fixed metadata, and each query lists and opens every file.',
               'INSERT INTO never modifies existing files; it only adds new ones.',
               'Rows are sent to reducers by key, so a hot key overloads one reducer.',
               'Map-side partial sums and a random first stage spread the hot key’s work.']
two = anim_two('Layout problems', 'Over-partitioning, small files and skew', 'Real Beeline output', 'Why each problem costs time', see, B1, see_caps, behind_caps)

# ---- scenario 1: redesign
r1 = (t(180, 22, 'Requirement: clicks, 40 crore rows a day', 9.4, bold=True) + t(180, 56, 'queries: by day; by day + user; by day + page', 8.4, 'ink2') + cap('Design before the first load.', '(sample figures)', 'blue', y=150, h=46))
r2 = (t(180, 22, 'Option A: PARTITIONED BY (dt, user_id)', 9.4, 'red', bold=True) + t(180, 56, 'crores of folders, KB-sized files', 8.4, 'red') + cap('Over-partitioning: rejected.', '', 'amber', y=150, h=34))
r3 = (t(180, 22, 'Option B: PARTITIONED BY (dt)', 9.4, 'green', bold=True) + t(180, 56, 'CLUSTERED BY (user_id) INTO 256 BUCKETS', 8.4, 'ink', mono=True) + t(180, 74, '365 partitions a year, 256 big files each', 8.4, 'green') + cap('Date pruning + bucket pruning for users.', '', 'green', y=150, h=34))
r4 = (t(180, 22, 'Page filters', 9.4, bold=True) + t(180, 56, 'no partition: ORC min/max + bloom filters on page', 8.2, 'ink2') + cap('Columnar statistics skip stripes (Module 6).', '', 'blue', y=150, h=34))
r5 = (t(180, 22, 'Estimate first', 9.4, 'acc', bold=True) + t(180, 56, 'size per partition = daily volume ÷ partitions per day', 8.2, 'ink2', mono=True) + cap('If it is KB or a few MB, partition coarser.', '', 'amber', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Designing a clicks table before it exists',
              'Choosing the layout for a high-volume table. (Typical design discussion; figures are illustrative.)',
              'Layout design', 'Partitioning by day and user would create crores of tiny partitions; partition by day and bucket by user instead, and rely on ORC statistics for other columns', [r1, r2, r3, r4, r5],
              ['A big events table with three common query patterns.',
               'Partitioning by user too would explode the folder count.',
               'Partition by day and bucket by user: few folders, big files.',
               'Other columns are filtered with ORC statistics, not partitions.',
               'Always estimate data per partition before deciding.'],
              hid='scenario-design')

# ---- scenario 2: streaming small files
m1 = (t(180, 22, 'A job writes every 5 minutes', 9.4, bold=True) + t(180, 56, '288 inserts a day → 288 files per day', 8.4, 'red', mono=True) + cap('Queries on “today” slow down hour by hour.', '', 'amber', y=150, h=34))
m2 = (t(180, 22, 'Write side', 9.4, bold=True) + t(180, 56, 'SET hive.merge.tezfiles=true;', 8.4, 'ink', mono=True) + t(180, 74, 'merges files within each run only', 8.2, 'ink2') + cap('Helps each insert, not across inserts.', '', 'blue', y=150, h=34))
m3 = (t(180, 22, 'Nightly compaction of yesterday', 9.4, bold=True) + t(180, 52, "INSERT OVERWRITE TABLE t PARTITION (dt='${y}')", 8, 'ink', mono=True) + t(180, 68, "SELECT … FROM t WHERE dt='${y}';", 8, 'ink', mono=True) + cap('288 files → a few large files.', '', 'green', y=150, h=34))
m4 = term([('8 files · 11,300 bytes', Y), ('> INSERT OVERWRITE … PARTITION (…) SELECT …;', W), ('1 file  ·  7,520 bytes · same COUNT, same SUM', G)], label='real output · Hive 4.2.1')
m5 = (t(180, 22, 'Or use a table format built for it', 9.4, 'acc', bold=True) + t(180, 56, 'ACID tables (auto compaction) or Iceberg', 8.4, 'ink2') + cap('Module 7.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Five-minute loads and the growing pile of files',
              'Near-real-time loads create many small files. Write-time merging and nightly compaction keep them under control. Compaction result is real.',
              'Small files over time', 'A five-minute load creates 288 files a day; merge settings help each run, and a nightly rewrite compacts yesterday’s partition', [m1, m2, m3, m4, m5],
              ['Each micro-batch adds files: 288 a day.',
               'hive.merge.tezfiles merges files produced inside one job.',
               'A nightly job rewrites yesterday’s partition into a few big files.',
               'In our lab: 8 files became 1 with identical results.',
               'ACID compaction and Iceberg automate this (Module 7).'],
              hid='scenario-smallfiles')

# ---- scenario 3: skew join salting
k1 = (t(180, 22, 'orders ⋈ restaurants on restaurant_id', 9.4, bold=True) + t(180, 56, 'restaurant 0: 37.5% of orders', 8.4, 'red', mono=True) + cap('One join task does a third of the work.', '', 'amber', y=150, h=34))
k2 = (t(180, 22, 'First choice: map join', 9.4, bold=True) + t(180, 56, 'restaurants is small → broadcast it', 8.4, 'ink2') + cap('No shuffle by key, so no skew. Check EXPLAIN.', '', 'green', y=150, h=34))
k3 = (t(180, 22, 'Both sides big? Skew join', 9.4, bold=True) + t(180, 56, 'SET hive.optimize.skewjoin=true;', 8.4, 'ink', mono=True) + t(180, 74, 'keys over hive.skewjoin.key (100,000 rows) handled separately', 7.6, 'ink2') + cap('Hot keys get a follow-up map join.', '', 'blue', y=150, h=34))
k4 = (t(180, 22, 'Manual fix: salting', 9.4, bold=True) + t(180, 52, 'big side:   key || "_" || pmod(hash(order_id), 8)', 7.8, 'ink', mono=True) + t(180, 68, 'small side: key || "_" || 0..7  (8 copies)', 7.8, 'ink', mono=True) + cap('The hot key is split over 8 reducers.', '', 'green', y=150, h=34))
k5 = (t(180, 22, 'Measure', 9.4, 'acc', bold=True) + t(180, 56, 'compare slowest task time before and after', 8.4, 'ink2') + cap('Skew fixes trade extra work for balance.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'A hot key in a join: map join, skew join or salting',
              'The same hot restaurant in a join. Three standard remedies, from simplest to most manual. (Typical approach.)',
              'Skewed join', 'A hot join key overloads one task; use a map join when one side is small, Hive skew join for large sides, or salt the key to spread it', [k1, k2, k3, k4, k5],
              ['The hot restaurant sends a third of the join to one task.',
               'If the other side is small, a broadcast map join avoids the problem.',
               'Hive’s skew join handles very large keys in a separate map join.',
               'Salting splits the hot key into several sub-keys.',
               'Measure the slowest task before and after.'],
              hid='scenario-skewjoin')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Why the layout goes bad, and how to fix it</h2>
  <p>Left: real Beeline output. Right: why each problem costs time.</p>
''' + two + '''
  <p>Three live scenarios follow: designing a big table, five-minute loads, and a hot key in a join.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Layout work in real teams</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'review', 10, 'green', bold=True) + t(60, 58, 'before create', 7.4, 'ink2'),
    '1. Table design reviews',
    'Many data platform teams review new big tables before creation: partition column, expected data per partition, bucket count and file format.',
    ['Proposal', '*size estimate', 'Approved layout']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'compact', 10, 'blue', bold=True) + t(60, 58, 'nightly', 7.4, 'ink2'),
    '2. Scheduled compaction',
    'Pipelines that load often run a nightly job that rewrites yesterday’s partitions into large files, keeping NameNode and query costs stable.',
    ['Small files', '*rewrite partition', 'Few big files']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'files/part', 9, 'violet', bold=True, mono=True) + t(60, 58, 'monitoring', 7.4, 'ink2'),
    '3. Storage health dashboards',
    'Admins track average file size and files per partition from the metastore statistics (numFiles, totalSize) and alert on tables that drift into small files.',
    ['Metastore stats', '*files & sizes', 'Alerts']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'hot keys', 10, 'acc', bold=True) + t(60, 58, 'big sellers', 7.4, 'ink2'),
    '4. Marketplaces and hot sellers',
    'E-commerce and food delivery data often has a few giant sellers or a NULL / “unknown” key with many rows. Teams handle them separately or salt them in joins.',
    ['Top-key check', '*skew handling', 'Balanced tasks']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'NULL key', 10, 'acc', bold=True, mono=True) + t(60, 58, 'often the hottest', 7.4, 'ink2'),
    '5. NULL join keys',
    'Rows with a NULL foreign key all hash to the same place. Filtering them out before the join (they never match anyway) often removes the worst skew.',
    ['Join input', '*WHERE key IS NOT NULL', 'Even shuffle']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> finish Lessons <a href="../01-partitioning/">5.1</a>, <a href="../02-dynamic-partitions-and-msck/">5.2</a> and <a href="../03-bucketing/">5.3</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
