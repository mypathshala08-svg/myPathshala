import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()

FILES = [('000000_0', 6210, 247), ('000001_0', 5961, 244), ('000002_0', 6754, 269), ('000003_0', 5922, 237),
         ('000004_0', 6689, 262), ('000005_0', 5649, 230), ('000006_0', 6276, 250), ('000007_0', 6539, 261)]

def bucket_row(y, hi=None, tone='green', label=True):
    o = ''
    for k, (f, n, c) in enumerate(FILES):
        on = hi is None or k in hi
        o += box(14 + k * 41, y, 37, 40, tone if (hi is not None and k in hi) else 'card') + t(32 + k * 41, y + 16, f'B{k}', 8, 'ink' if on else 'ink3', bold=True) + (t(32 + k * 41, y + 30, f'{n:,}', 6.6, 'ink2' if on else 'ink3', mono=True) if label else '')
    return o

# ---------------------------------------------------------------- story
sc = (box(10, 12, 200, 128, 'card') + t(110, 30, '2,000 customers', 8.8, bold=True) +
      ''.join(t(22, 52 + k * 15, s, 7.4, 'ink2', anchor='start', mono=True) for k, s in enumerate(['customer 1  → ?', 'customer 2  → ?', 'customer 3  → ?', '…', 'customer 2000 → ?'])) +
      arrow(216, 76, 256, 76, 'acc', 2.2) + box(262, 46, 108, 60, 'acc') + t(316, 66, 'murmur3(id)', 8.2, bold=True, mono=True) + t(316, 82, 'mod 8', 8.2, bold=True, mono=True) + t(316, 98, 'bucket number', 7, 'ink2') +
      arrow(376, 76, 410, 76, 'acc', 2.2) + box(416, 12, 214, 128, 'green') + t(523, 30, '8 files, ~250 customers each', 8.8, 'green', bold=True) +
      ''.join(box(428 + (k % 4) * 50, 42 + (k // 4) * 44, 44, 36, 'card') + t(450 + (k % 4) * 50, 58 + (k // 4) * 44, f'0000{k}_0', 6.4, 'ink', mono=True) + t(450 + (k % 4) * 50, 70 + (k // 4) * 44, f'{FILES[k][2]} cust', 6.4, 'ink2') for k in range(8)) +
      t(523, 134, 'same customer → always the same file', 7.4, 'ink2'))
scene_svg = scene('Two thousand customers pass through a hash function and modulo 8; each lands in one of eight files of about 250 customers, and the same customer always lands in the same file.', sc,
                  'Bucketing spreads rows over a <tspan font-weight="700" class="s-acc">fixed number of files</tspan> by a hash of a column.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Can we partition by customer?”</h2>
  <div class="story">
    <p class="narration">The CRM team asks Kabir for two things: a quick 1-in-8 sample of customers to test a new loyalty rule, and faster joins between <code>orders</code> and <code>customers</code> on <code>customer_id</code>. Kabir’s first idea, after Lesson 5.1, is to partition by customer.</p>

{scene_svg}

K> Sir, if date partitions work so well, why not <code>PARTITIONED BY (customer_id)</code>?
A> Two thousand customers today, two lakh next year: that is two lakh folders with a few rows each. Partitioning is for columns with a modest number of values. For high-cardinality columns like ids we use <b>bucketing</b>: <code>CLUSTERED BY (customer_id) INTO 8 BUCKETS</code>. Hive hashes each id and writes it into one of exactly 8 files.
R> And the same customer always lands in the same file?
A> Always. That is what makes bucket sampling and bucket-aware joins possible. Today we look inside the 8 files, prove that the hash is <b>not</b> simply id mod 8 in Hive 4, sample one bucket while reading one file, and hit two surprises: bucketed CTAS is refused, and a LOAD into a bucketed table lost three customers. All outputs are real, from Hive 4.2.1.
  </div>
</section>
'''

lv = '''
LEVELS> Bucketing at three levels
L1> Roll numbers into sections
      <ul>
        <li>A school splits 2,000 students into 8 sections by a fixed rule on the roll number. Every student is always in the same section, and each section has roughly the same size.</li>
        <li>In Hive the sections are files. <code>CLUSTERED BY (customer_id) INTO 8 BUCKETS</code> creates 8 files per table (or per partition).</li>
        <li>Unlike a partition, the bucket column <b>stays in the data</b>, and the number of buckets never grows with the data.</li>
      </ul>
L2> How rows are placed and what it enables
      <ul>
        <li>Bucket number = hash(bucket column) mod number of buckets. Hive 3+ tables have <code>bucketing_version=2</code> and use the <b>Murmur3</b> hash. Our lab confirmed it: customer 1 is in bucket 5, which is <code>pmod(murmur_hash(1), 8)</code>, not <code>1 % 8</code>. Older articles that say “for INT the hash is the value” describe version 1.</li>
        <li><code>SORTED BY</code> sorts rows inside each bucket file.</li>
        <li><b>Sampling:</b> <code>TABLESAMPLE(BUCKET x OUT OF y ON col)</code> reads only the matching bucket files when y divides the bucket count.</li>
        <li><b>Bucket pruning:</b> <code>WHERE customer_id = 1</code> read 5,649 rows instead of 50,000 (<code>hive.tez.bucket.pruning=true</code>).</li>
        <li><code>hive.enforce.bucketing</code> is no longer needed: since Hive 2.x inserts always write the declared buckets.</li>
      </ul>
L3> Joins, loads and limits in Hive 4.2.1
      <ul>
        <li><b>Bucket map join / SMB join:</b> when both tables are bucketed (and sorted) on the join key with compatible bucket counts, the optimiser <i>can</i> join bucket i with bucket i without a full shuffle. It is a cost-based choice: on our small lab tables Hive picked a broadcast map join or a shuffle merge join instead. Always check <code>EXPLAIN</code>.</li>
        <li><b>CTAS</b> into a bucketed table was refused (Error 10068); create the table, then INSERT.</li>
        <li><b>LOAD DATA</b> into a bucketed table is rewritten into an insert job. With <code>skip.header.line.count=1</code> it lost customers 1, 3 and 5: the header became a data row, and then the first line of <b>every</b> bucket file was skipped. Load into a staging table, then INSERT … SELECT.</li>
        <li><code>TABLESAMPLE(10 PERCENT)</code> was refused on Tez in our lab; <code>TABLESAMPLE(100 ROWS)</code> and bucket sampling worked.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Bucketing (clustering) in Hive</h2>
''' + def_block(
    '<b>Bucketing</b> divides the data of a table, or of each partition, into a fixed number of files called <b>buckets</b>, declared with <code>CLUSTERED BY (col, …) [SORTED BY (col [ASC|DESC], …)] INTO n BUCKETS</code>. Each row is written to bucket <code>hash(bucketing columns) mod n</code>, so equal values always go to the same bucket. Bucketing columns remain ordinary columns of the data. Bucketing enables efficient <b>sampling</b> (<code>TABLESAMPLE</code>), <b>bucket pruning</b> on equality filters and, when tables are bucketed compatibly on the join key, <b>bucket map joins</b> and <b>sort-merge-bucket (SMB) joins</b>.',
    'Bucketing splits a table into a fixed number of files using a hash of a column such as customer_id. The same id always goes to the same file, so Hive can read just one file for a sample or for one id, and can join matching files of two tables.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Bucket', 'One of the n files of a bucketed table or partition, e.g. <code>000005_0</code>.'),
    ('CLUSTERED BY', 'The bucketing column(s). Not the same as the CLUSTER BY query clause (3.4).'),
    ('Murmur3', 'The hash used by bucketing_version 2 tables (Hive 3+).'),
    ('TABLESAMPLE', '<code>TABLESAMPLE(BUCKET x OUT OF y ON col)</code>: a sample by bucket.'),
    ('Bucket pruning', 'Reading only the bucket that can hold the value in <code>WHERE col = v</code>.'),
    ('Bucket map join', 'Each task loads only the matching bucket of the small table.'),
    ('SMB join', 'Sort-merge-bucket join: both tables bucketed and sorted on the key; merge bucket by bucket.'),
    ('INPUT__FILE__NAME', 'Virtual column: the file each row was read from.'),
]) + '''

  <h3>Partitioning vs bucketing</h3>
''' + table(['', 'Partitioning', 'Bucketing'], [
    ['Clause', '<code>PARTITIONED BY (col)</code>', '<code>CLUSTERED BY (col) INTO n BUCKETS</code>'],
    ['Unit on disk', 'A folder per value', 'A fixed number of files'],
    ['Column stored in files?', 'No (folder name)', 'Yes'],
    ['Best for', 'Few to moderate values used in filters (date)', 'Many values (ids), joins and sampling'],
    ['Grows with new values?', 'Yes, new folders', 'No, always n files'],
    ['Skips data by', 'Partition pruning', 'Bucket pruning and sampling'],
    ['Can combine?', 'Yes: partition by date, then bucket each day by customer_id', ''],
], minw=640) + lv + '''
EXAM> “Partitioning vs bucketing” is one of the most asked Hive questions. Say: partitioning makes folders by value and suits low-cardinality filter columns; bucketing hashes a column into a fixed number of files and suits high-cardinality columns, sampling and joins; they can be combined. Mention <code>CLUSTERED BY … INTO n BUCKETS</code> and <code>TABLESAMPLE</code>.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Ways to use buckets</h2>
''' + table(['Use', 'Statement', 'What happens'], [
    ['Create', '<code>CLUSTERED BY (customer_id) SORTED BY (customer_id) INTO 8 BUCKETS</code>', '8 files per table or partition, sorted inside'],
    ['Partition + bucket', '<code>PARTITIONED BY (order_date) CLUSTERED BY (customer_id) INTO 8 BUCKETS</code>', '8 files inside every day folder'],
    ['Fill', '<code>INSERT OVERWRITE TABLE t SELECT …</code>', 'Hive shuffles by the hash and writes n files'],
    ['Bucket sample', '<code>TABLESAMPLE(BUCKET 6 OUT OF 8 ON customer_id)</code>', 'Reads one file (real: 5,649 rows)'],
    ['Row sample', '<code>TABLESAMPLE(100 ROWS)</code>', 'First rows of each split'],
    ['Random sample', '<code>TABLESAMPLE(BUCKET 1 OUT OF 10 ON rand())</code>', 'Reads everything; different rows each run'],
    ['Point lookup', '<code>WHERE customer_id = 1</code>', 'Bucket pruning: one bucket’s rows read'],
    ['Join', 'Both tables <code>CLUSTERED BY</code> the join key', 'Bucket map / SMB join possible (check EXPLAIN)'],
], minw=720) + '''
WARN> Choosing the bucket count: aim for bucket files of a healthy size (tens to hundreds of MB in production), and for joins use the same count, or multiples, on both tables. Too many buckets on a small table just creates small files: our 8 buckets hold only 44–53 KB each, fine for learning but far too many for 50,000 rows in real life.
</section>
'''

smp = capf('l53_sample.txt').split('\n')
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Kabir buckets orders by customer</h2>
  <p>All outputs are real, from the Hive 4.2.1 lab (database <code>tiffingo</code>).</p>
''' + stepper([
    ('Step 1 · Create a bucketed, sorted table and fill it',
     code('sql', 'Beeline', "CREATE TABLE orders_bkt (\n  order_id INT, customer_id INT, city STRING, order_ts TIMESTAMP,\n  amount DECIMAL(10,2), payment STRING, status STRING)\nCLUSTERED BY (customer_id) SORTED BY (customer_id) INTO 8 BUCKETS\nSTORED AS ORC;\n\nINSERT OVERWRITE TABLE orders_bkt\nSELECT order_id, customer_id, city, order_ts, amount, payment, status FROM orders;\n\nDESCRIBE FORMATTED orders_bkt;   -- selected lines\n$ ls …/tiffingo.db/orders_bkt",
          '| bucketing_version | 2                                 |\n| Num Buckets:      | 8                                 |\n| Bucket Columns:   | [customer_id]                     |\n| Sort Columns:     | [Order(col:customer_id, order:1)] |\n\n000000_0  000001_0  000002_0  000003_0\n000004_0  000005_0  000006_0  000007_0'),
     'Exactly 8 files, one per bucket, named by bucket number. No <code>SET hive.enforce.bucketing</code> was needed; that setting only mattered before Hive 2. <code>bucketing_version=2</code> tells every engine which hash to use.'),
    ('Step 2 · Which file holds which customer?',
     code('sql', 'Beeline', "SELECT customer_id,\n       regexp_extract(INPUT__FILE__NAME, '[^/]+$', 0) AS file,\n       customer_id % 8                  AS mod8,\n       pmod(hash(customer_id), 8)       AS legacy_hash,\n       pmod(murmur_hash(customer_id), 8) AS murmur\nFROM orders_bkt WHERE customer_id IN (1, 2, 3, 4, 5, 6, 7, 8)\nGROUP BY customer_id, INPUT__FILE__NAME ORDER BY customer_id;", tables(capf('l53_which.txt'))[0]),
     'The real file number matches the <b>murmur</b> column every time, not <code>id % 8</code>. Many tutorials still teach “bucket = id mod n”; that was version 1. The <code>INPUT__FILE__NAME</code> virtual column is the quickest way to check where rows really are.'),
    ('Step 3 · How even are the buckets?',
     code('sql', 'Beeline', "SELECT regexp_extract(INPUT__FILE__NAME, '[^/]+$', 0) AS file,\n       COUNT(*) AS rows_in_file, COUNT(DISTINCT customer_id) AS customers\nFROM orders_bkt GROUP BY INPUT__FILE__NAME ORDER BY file;", tables(capf('l53_which.txt'))[1]),
     'Between 230 and 269 customers per bucket, close to 2,000 ÷ 8 = 250. Rows vary more (5,649 to 6,754), because some customers order more. A customer who orders 100 times more than others would make one bucket much bigger: bucketing spreads <b>keys</b>, not rows (skew, Lesson 5.4).'),
    ('Step 4 · Sample one bucket, read one file',
     code('sql', 'Beeline', "SET hive.tez.exec.print.summary=true;\nSELECT COUNT(*) AS n, COUNT(DISTINCT customer_id) AS c\nFROM orders_bkt TABLESAMPLE(BUCKET 6 OUT OF 8 ON customer_id) s;\n\nSELECT … FROM orders_bkt TABLESAMPLE(BUCKET 2 OUT OF 4 ON customer_id) s;\nSELECT … FROM orders     TABLESAMPLE(BUCKET 6 OUT OF 8 ON customer_id) s;  -- not bucketed", '\n'.join(smp[:6])),
     'Bucket numbers in TABLESAMPLE start at 1, so BUCKET 6 is file <code>000005_0</code>: 5,649 rows, 230 customers, one file read. <code>2 OUT OF 4</code> takes buckets 2 and 6 (files 1 and 5). On the unbucketed table the same sample gives the same answer but reads all 50,000 rows, because Hive must hash every row.'),
    ('Step 5 · Bucket pruning on an equality filter',
     code('sql', 'Beeline', "SET hive.tez.bucket.pruning;\nSELECT COUNT(*) AS n, COUNT(DISTINCT customer_id) AS c\nFROM orders_bkt WHERE customer_id = 1;", '+-------------------------------+\n| hive.tez.bucket.pruning=true  |\n+-------------------------------+\n' + '\n'.join(smp[6:8])),
     'Customer 1 has 26 orders. Hive computed customer 1’s bucket and read only that bucket’s 5,649 rows, not 50,000. It also worked for <code>IN (1, 2)</code>: 12,338 rows, exactly buckets 5 and 4. A wide range such as <code>BETWEEN 1 AND 1000</code> touches every bucket, so it saves nothing.'),
    ('Step 6 · Other samples: ROWS, rand() and PERCENT',
     code('sql', 'Beeline', "SELECT COUNT(*) AS n  FROM orders TABLESAMPLE(100 ROWS) s;\nSELECT COUNT(*) AS n1 FROM orders TABLESAMPLE(BUCKET 1 OUT OF 10 ON rand()) s;\nSELECT COUNT(*) AS n2 FROM orders TABLESAMPLE(BUCKET 1 OUT OF 10 ON rand()) s;\nSELECT COUNT(*) AS n  FROM orders TABLESAMPLE(10 PERCENT) s;",
          '\n'.join(tables(capf('l53_sample3.txt'))[:3]) + '\n' + capf('l53_pct2.txt').split('; Query ID')[0]),
     '<code>ON rand()</code> gives about 10% but a different sample each run (5,057, then 4,981), so results cannot be reproduced. Sample on a column (or <code>hash(col)</code>) for repeatable tests. Block sampling by PERCENT was refused on our Tez setup.'),
    ('Step 7 · Two surprises: CTAS and LOAD DATA',
     code('sql', 'Beeline', "CREATE TABLE customers_bkt CLUSTERED BY (customer_id) INTO 8 BUCKETS\nSTORED AS ORC AS SELECT * FROM customers;\n\nCREATE TABLE cust_bkt_load (customer_id INT, name STRING, city STRING, state STRING,\n  joined_on DATE, plan STRING)\nCLUSTERED BY (customer_id) INTO 4 BUCKETS\nROW FORMAT DELIMITED FIELDS TERMINATED BY ','\nTBLPROPERTIES ('skip.header.line.count'='1');\nLOAD DATA LOCAL INPATH '/data/tiffingo/customers/customers.csv' INTO TABLE cust_bkt_load;\nSELECT COUNT(*) AS loaded, MIN(customer_id) AS min_id, MAX(customer_id) AS max_id FROM cust_bkt_load;",
          capf('l53_ctas_err.txt').split('; Query ID')[0] + '\n\n' + tables(capf('l53_load2.txt'))[0]),
     'Bucketed CTAS is refused (the message says “partitioning”, but bucketing triggers it too). LOAD into a bucketed table ran an insert job and wrote 4 bucket files, but only <b>1,997</b> of 2,000 customers came back: the header line was stored as a row, and <code>skip.header.line.count</code> then skipped the first line of <b>each</b> of the 4 files, hiding customers 1, 3 and 5. Load into a plain staging table and INSERT … SELECT instead.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('> CREATE TABLE orders_bkt (…)', W), ('  CLUSTERED BY (customer_id) SORTED BY (customer_id)', W), ('  INTO 8 BUCKETS STORED AS ORC;', W), ('> INSERT OVERWRITE TABLE orders_bkt SELECT …;', W), ('$ ls  → 000000_0 … 000007_0', G)]),
    term([('| customer_id | file     | mod8 | murmur |', W), ('| 1           | 000005_0 | 1    | 5      |', G), ('| 2           | 000004_0 | 2    | 4      |', G), ('| 7           | 000000_0 | 7    | 0      |', G), ('  file = murmur, not mod8', Y)], size=7.6),
    term([('> … TABLESAMPLE(BUCKET 6 OUT OF 8', W), ('                 ON customer_id) s;', W), ('| 5649 | 230 |', G), ('  RECORDS_IN_Map_1: 5649   INPUT_FILES: 1', G)]),
    term([('> … FROM orders_bkt WHERE customer_id = 1;', W), ('| 26 | 1 |', G), ('  RECORDS_IN_Map_1: 5649 (not 50000)', G)]),
    term([("> LOAD DATA … INTO TABLE cust_bkt_load;", W), ('> SELECT COUNT(*), MIN(customer_id) …', W), ('| 1997 | 2 | 2000 |', RD), ('  customers 1, 3, 5 missing', RD)]),
]
B1 = [
    t(180, 22, 'Rows are shuffled by hash into 8 writers', 9.4, bold=True) + bucket_row(52, label=False) + t(180, 112, 'one reducer per bucket → one file per bucket', 8, 'ink2') + cap('n buckets = n files, sorted inside.', '', 'blue', y=150, h=34),
    t(180, 22, 'bucket = murmur3(customer_id) mod 8', 9.4, bold=True, mono=True) + bucket_row(52, hi={5}, label=False) + t(180, 112, 'customer 1 → murmur → 5 → 000005_0', 8, 'green', mono=True, bold=True) + cap('bucketing_version 2 (Hive 3+).', 'Version 1 used the plain value for INT.', 'blue', y=150, h=46),
    t(180, 22, 'TABLESAMPLE picks bucket 6 (1-based)', 9.4, bold=True) + bucket_row(52, hi={5}) + cap('Only file 000005_0 is opened.', 'Same answer on a flat table costs a full scan.', 'green', y=150, h=46),
    t(180, 22, 'WHERE customer_id = 1 → its bucket only', 9.4, bold=True) + bucket_row(52, hi={5}) + t(180, 112, 'hash the literal, keep that bucket', 8, 'ink2') + cap('Bucket pruning: works for = and IN.', '', 'green', y=150, h=34),
    t(180, 22, 'Header row + per-file skip', 9.4, bold=True) + ''.join(box(20 + k * 82, 46, 76, 60, 'red' if True else 'card') + t(58 + k * 82, 62, f'00000{k}_0', 7, 'ink', mono=True) + t(58 + k * 82, 80, ['header row', 'cust 1', 'cust 3', 'cust 5'][k], 7.6, 'red', bold=True) + t(58 + k * 82, 96, 'skipped', 6.8, 'ink2') for k in range(4)) +
    cap('skip.header.line.count applies to every file.', '1 header + 3 customers hidden = 1,997.', 'amber', y=150, h=46),
]
see_caps = ['Kabir creates and fills an 8-bucket table: 8 files appear.',
            'The real bucket of each customer matches murmur_hash, not id mod 8.',
            'Sampling one bucket reads one file: 5,649 rows.',
            'A filter on one customer reads only that customer’s bucket.',
            'LOAD into a bucketed table with a header lost three customers.']
behind_caps = ['The insert shuffles rows by the hash so each writer produces one bucket file.',
               'Hive 3+ tables use Murmur3 for the bucket number.',
               'TABLESAMPLE maps bucket 6 of 8 to file 000005_0 and skips the rest.',
               'Hive hashes the literal 1, finds bucket 5 and reads only it.',
               'The rewritten load stored the header as a row; then the first line of each bucket file was skipped.']
two = anim_two('Buckets', 'Hash, files, sampling and the LOAD surprise', 'Real Beeline output', 'Where each row goes and which files are read', see, B1, see_caps, behind_caps)

# ---- scenario 1: A/B sample
a1 = (t(180, 22, 'Test a loyalty rule on 1 in 8 customers', 9.4, bold=True) + t(180, 56, 'needs the SAME customers every day', 8.4, 'ink2') + cap('rand() samples change every run.', '(real: 5,057 then 4,981 rows)', 'amber', y=150, h=46))
a2 = (t(180, 22, 'Sample by bucket on the customer column', 9.4, bold=True) + t(180, 56, 'TABLESAMPLE(BUCKET 6 OUT OF 8 ON customer_id)', 7.8, 'ink', mono=True) + cap('Deterministic: 230 customers, every time.', '', 'green', y=150, h=34))
a3 = (t(180, 22, 'Cheap on a bucketed table', 9.4, bold=True) + bucket_row(52, hi={5}) + cap('One file read instead of eight.', '', 'green', y=150, h=34))
a4 = (t(180, 22, 'Same group in other tables', 9.4, bold=True) + t(180, 56, 'customers_bkt is bucketed the same way', 8.4, 'ink2') + t(180, 74, 'bucket 6 = the same 230 customers', 8.4, 'green', bold=True) + cap('Same column, same count, same hash → same group.', '', 'blue', y=150, h=34))
a5 = (t(180, 22, 'Compare', 9.4, 'acc', bold=True) + t(180, 56, 'test group (bucket 6) vs the rest', 8.4, 'ink2') + cap('A simple, repeatable experiment split.', '', 'green', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'A repeatable 1-in-8 customer test group',
              'Product teams need a stable sample of customers. Bucket sampling on the customer column gives one. Counts are real.',
              'Bucket sampling', 'A deterministic 1-in-8 sample of customers comes from one bucket of tables bucketed on customer_id', [a1, a2, a3, a4, a5],
              ['A random sample changes every run, so the test group would change too.',
               'Sampling on customer_id always selects the same customers.',
               'On a bucketed table this reads a single file.',
               'Tables bucketed the same way share the same groups.',
               'The test group and the rest can be compared fairly.'],
              hid='scenario-sample')

# ---- scenario 2: the LOAD bug
l1 = (t(180, 22, 'Monthly customer refresh via LOAD DATA', 9.4, bold=True) + t(180, 56, 'CSV with a header · bucketed text table', 8.4, 'ink2') + cap('It used to be an unbucketed table.', '', 'blue', y=150, h=34))
l2 = term([('> LOAD DATA … INTO TABLE cust_bkt_load;', W), ('> SELECT COUNT(*) FROM cust_bkt_load;', W), ('| 1997 |', RD), ('  expected 2000', Y)], label='real output · Hive 4.2.1')
l3 = term([("> ALTER TABLE … SET TBLPROPERTIES ('skip.header.line.count'='0');", W), ('| lines_in_files 2001 | with_id 2000 |', Y), ('| 000000_0 | NULL | name |', RD), ('  the header was stored as a row', RD)], label='real output · Hive 4.2.1', size=7.4)
l4 = (t(180, 22, 'Safe pattern', 9.4, 'green', bold=True) + t(180, 52, '1. LOAD into a plain staging table', 8.4, 'ink', anchor='middle') + t(180, 70, '2. INSERT OVERWRITE TABLE bucketed SELECT * FROM stage', 8, 'ink', mono=True) + t(180, 88, '3. compare counts', 8.4, 'ink') + cap('Every row arrives, buckets are correct.', '', 'green', y=150, h=34))
l5 = (t(180, 22, 'Lesson', 9.4, 'acc', bold=True) + t(180, 56, 'always reconcile row counts after a load', 8.4, 'ink2') + cap('Silent data loss is the worst kind.', '', 'amber', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Three customers vanished: LOAD into a bucketed table',
              'We found this while building the lesson. LOAD with a header into a bucketed table lost rows silently. Outputs are real.',
              'Load reconciliation', 'Loading a CSV with a header into a bucketed table lost three customers because the header became a row and each bucket file skipped its first line', [l1, l2, l3, l4, l5],
              ['The refresh job loads a CSV with a header into a bucketed table.',
               'The count is 1,997 instead of 2,000.',
               'Reading the files without skipping shows the header stored as a row.',
               'Load into staging, then INSERT … SELECT into the bucketed table.',
               'Reconcile counts after every load.'],
              hid='scenario-loadbug')

# ---- scenario 3: join planning
j1 = (t(180, 22, 'orders ⋈ customers on customer_id', 9.4, bold=True) + t(180, 56, 'both CLUSTERED BY (customer_id) INTO 8 BUCKETS', 8, 'ink', mono=True) + cap('The setup for bucket-aware joins.', '', 'blue', y=150, h=34))
j2 = (t(180, 22, 'Bucket map join (idea)', 9.4, bold=True) + ''.join(box(20 + k * 82, 46, 76, 24, 'card') + t(58 + k * 82, 62, f'orders B{k}', 7.4, 'ink', mono=True) + arrow(58 + k * 82, 72, 58 + k * 82, 86, 'green') + box(20 + k * 82, 88, 76, 24, 'green') + t(58 + k * 82, 104, f'cust B{k}', 7.4, 'ink', mono=True) for k in range(4)) + cap('Each task loads only its matching bucket.', 'SMB: both sorted → merge without hashing.', 'green', y=150, h=46))
j3 = term([('> EXPLAIN SELECT c.plan, COUNT(*) …', W), ('  FROM orders_bkt o JOIN customers_bkt c …', W), ('  Map 1 <- Map 3 (BROADCAST_EDGE)', Y), ('  Map Join Operator [MAPJOIN_26]', Y)], label='real output · Hive 4.2.1')
j4 = term([('> SET hive.auto.convert.join=false;', W), ('> EXPLAIN …', W), ('  Reducer 2 <- Map 1, Map 4 (SIMPLE_EDGE)', Y), ('  Merge Join Operator [MERGEJOIN_19]', Y)], label='real output · Hive 4.2.1')
j5 = (t(180, 22, 'What this means', 9.4, 'acc', bold=True) + t(180, 52, 'small dimension → broadcast is cheaper anyway', 8.2, 'ink2') + t(180, 70, 'bucket joins pay off when BOTH tables are big', 8.2, 'ink2') + cap('Bucketing makes it possible; the optimiser decides.', 'Check EXPLAIN on your data.', 'blue', y=150, h=46))
s3 = anim_one('Real-time scenario 3 · advanced', 'Bucket joins: possible, not guaranteed',
              'Both tables were bucketed and sorted on customer_id. Here is what Hive 4.2.1 actually chose on our small tables.',
              'Join planning', 'Two tables bucketed on the join key allow bucket map or SMB joins, but on small tables Hive chose a broadcast map join or a shuffle merge join', [j1, j2, j3, j4, j5],
              ['Both tables are bucketed the same way on the join key.',
               'In a bucket map join each task joins bucket i with bucket i only.',
               'With 2,000 customers, Hive simply broadcast the whole small table.',
               'With map joins turned off, it used a normal shuffle merge join.',
               'Bucket joins help when both sides are too large to broadcast; always confirm with EXPLAIN.'],
              hid='scenario-joins')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Hashing rows into buckets</h2>
  <p>Left: real Beeline output. Right: where each row goes and which files are read.</p>
''' + two + '''
  <p>Three live scenarios follow: a repeatable sample, a LOAD that lost rows, and what the optimiser did with bucketed joins.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Bucketing at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'BUCKET 1/32', 9, 'green', bold=True, mono=True) + t(60, 58, 'stable sample', 7.4, 'ink2'),
    '1. Repeatable samples and experiments',
    'Data scientists test queries and models on one bucket of a huge table, and product teams pick experiment groups by user bucket, so the same users are in the group every day.',
    ['Huge table', '*TABLESAMPLE bucket', 'Fast, stable sample']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'B i ⋈ B i', 10, 'blue', bold=True, mono=True) + t(60, 58, 'big joins', 7.4, 'ink2'),
    '2. Joining two large tables',
    'When two fact-sized tables are joined every day on the same key (orders and payments on order_id), bucketing both on that key lets the engine join matching buckets instead of shuffling everything.',
    ['Two big tables', '*bucketed on key', 'Bucket / SMB join']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'id = ?', 11, 'violet', bold=True, mono=True) + t(60, 58, 'lookups', 7.4, 'ink2'),
    '3. Customer look-ups',
    'Support tools that pull one customer’s history benefit from bucket pruning: only that customer’s bucket inside each date partition is read.',
    ['Customer id', '*bucket pruning', 'One file per day']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'ACID', 11, 'acc', bold=True, mono=True) + t(60, 58, 'transactional', 7.4, 'ink2'),
    '4. Transactional tables',
    'Older Hive versions required ACID tables to be bucketed; Hive 3+ does not, but bucketing still organises delta files by key in many existing warehouses (Module 7).',
    ['Updates', '*bucketed ACID', 'Organised deltas']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'v2 hash', 10, 'acc', bold=True, mono=True) + t(60, 58, 'engines agree', 7.4, 'ink2'),
    '5. Shared tables across engines',
    'Spark and Trino can read Hive-bucketed tables. The bucketing_version property tells them which hash Hive used, so bucket pruning and joins stay correct across engines.',
    ['Hive writes', '*bucketing_version', 'Spark / Trino read']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> finish partitioning (<a href="../01-partitioning/">5.1</a>) and joins (<a href="../../03-querying/03-joins/">3.3</a>); DISTRIBUTE BY and CLUSTER BY (<a href="../../03-querying/04-order-sort-distribute-cluster-by/">3.4</a>) explain the shuffle behind bucketing.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
