import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()

# ---------------------------------------------------------------- story
def folder(x, y, label, on=True, tone='card'):
    op = '' if on else ' opacity=".3"'
    return f'<g{op}>' + f'<path d="M{x} {y+4}h14l4 4h26v22h-44z" class="{TONES[tone][0]}" style="stroke:{TONES[tone][1]}"/>' + t(x + 22, y + 40, label, 6.6, 'ink2', mono=True) + '</g>'
sc = (box(10, 12, 230, 128, 'card') + t(125, 30, 'orders: one big folder', 8.8, bold=True) +
      ''.join(fill(24 + (k % 12) * 17, 44 + (k // 12) * 14, 13, 10, 'acc', rx=2) for k in range(60)) + t(125, 132, 'WHERE order_date = 10-05 → read all 50,000 rows', 7.2, 'red', bold=True) +
      arrow(246, 76, 286, 76, 'acc', 2.2) +
      box(292, 12, 338, 128, 'green') + t(461, 30, 'orders_by_day: one folder per day', 8.8, 'green', bold=True) +
      ''.join(folder(304 + k * 46, 48, f'10-0{k + 1}', on=(k == 4), tone='green' if k == 4 else 'card') for k in range(7)) +
      t(461, 112, 'order_date=2026-10-05/ only', 8, 'ink', mono=True, bold=True) + t(461, 132, 'read 1,621 rows instead of 50,000', 7.6, 'green', bold=True))
scene_svg = scene('On the left one folder holds all orders, so a query for one day reads all 50,000 rows. On the right the table has one folder per day, and the same query opens only the 5 October folder and reads 1,621 rows.', sc,
                  'A partition is just a <tspan font-weight="700" class="s-acc">sub-folder</tspan>. Filter on it, and Hive opens only the folders you need.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Every daily report reads the whole month”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s operations team runs the same question every morning: yesterday’s orders and revenue per city. The <code>orders</code> table holds a month of data and keeps growing. Kabir notices that a query for a single day reads all 50,000 rows, every time. At 50 lakh orders a month, that would be 50 lakh rows read to answer a one-day question.</p>

{scene_svg}

K> Sir, the WHERE clause says one day. Why does Hive still read everything?
A> Because the table is one folder of files, and Hive cannot know which file holds which day without opening it. If we store each day in <b>its own sub-folder</b>, <code>order_date=2026-10-05/</code>, Hive reads the folder name and skips the others. That is <b>partitioning</b>.
R> So the date is in the folder name, not inside the file?
A> Exactly. The partition column lives in the metastore and the path; the data files hold only the other columns. Today we build <code>orders_by_day</code>, prove with Hive’s own counters that a one-day query reads 1,621 rows instead of 50,000, and find two ways to lose that benefit without noticing. All outputs are real, from Hive 4.2.1.
  </div>
</section>
'''

lv = '''
LEVELS> Partitioning at three levels
L1> Files sorted into labelled boxes
      <ul>
        <li>Imagine a month of bills in one big box. To find 5 October’s bills you must look at every bill.</li>
        <li>Now keep one box per day, with the date written on it. You open only the “5 October” box.</li>
        <li>In Hive the box is a folder like <code>order_date=2026-10-05</code>, and the label is the <b>partition column</b>. You choose it with <code>PARTITIONED BY</code> when you create the table.</li>
      </ul>
L2> How Hive uses partitions
      <ul>
        <li>Every partition is a row in the metastore (table <code>PARTITIONS</code>) pointing to its folder. <code>SHOW PARTITIONS t;</code> lists them.</li>
        <li>When WHERE filters on the partition column, the planner asks the metastore for the matching partitions only. This is <b>partition pruning</b>; <code>EXPLAIN DEPENDENCY</code> shows which partitions a query will read.</li>
        <li><b>Static partition:</b> you name the value: <code>INSERT … PARTITION (order_date='2026-10-05') SELECT …</code> or <code>LOAD DATA … PARTITION (dt='…')</code>. <b>Dynamic:</b> Hive takes the value from the data (Lesson 5.2).</li>
        <li>Partitions can nest: <code>PARTITIONED BY (order_date DATE, city STRING)</code> creates <code>order_date=…/city=…/</code>.</li>
      </ul>
L3> What the planner can and cannot prune
      <ul>
        <li>In our lab Hive 4.2.1 pruned even through functions on the partition column: <code>date_format(order_date,'EEE')='Sat'</code> read 4 partitions, <code>order_date &gt;= date_sub(current_date, 3)</code> read 7.</li>
        <li>It <b>cannot</b> prune on a different column that “means the same”: <code>to_date(order_ts)='2026-10-05'</code> read all 30 folders and 50,000 rows, although the answer was identical. It also cannot prune when the filter is <code>OR</code>-ed with a non-partition condition.</li>
        <li>Static partitions are <b>trusted</b>, not checked: loading 3 October’s file into <code>dt='2026-10-04'</code> succeeded and duplicated 1,668 orders.</li>
        <li>Safety switch: <code>SET hive.strict.checks.no.partition.filter=true</code> rejects queries on partitioned tables without a partition filter (Error 10056). Default in 4.2.1: false.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Partitioning in Hive</h2>
''' + def_block(
    '<b>Partitioning</b> divides a table into parts based on the values of one or more <b>partition columns</b>, declared with <code>PARTITIONED BY (col type, …)</code>. Each distinct combination of values is a <b>partition</b>, stored as a separate sub-directory of the table location named <code>col=value</code> and registered in the metastore. Partition columns are virtual: they are not stored inside the data files, but can be queried like normal columns. When a query filters on partition columns, Hive reads only the matching partitions; this is called <b>partition pruning</b>.',
    'You tell Hive to keep each day (or city, or month) in its own folder. When you ask for one day, Hive opens only that folder and skips the rest, so the query reads much less data.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Partition column', 'The column in <code>PARTITIONED BY</code>; its value is the folder name, not data in the file.'),
    ('Partition', 'One value (or combination) of the partition columns, e.g. <code>order_date=2026-10-05</code>.'),
    ('Partition pruning', 'Skipping partitions that the WHERE clause rules out, before any file is read.'),
    ('Static partition', 'You write the value in the statement: <code>PARTITION (dt=\'2026-10-03\')</code>.'),
    ('Dynamic partition', 'Hive takes the value from the last SELECT column (Lesson 5.2).'),
    ('Multi-level partition', '<code>PARTITIONED BY (order_date, city)</code> → <code>order_date=…/city=…/</code>.'),
    ('EXPLAIN DEPENDENCY', 'Shows the tables and partitions a query will read.'),
    ('RECORDS_IN_Map_1', 'Tez counter: how many rows the first stage really read.'),
]) + '''

  <h3>The proof: same answer, very different work (real Tez counters)</h3>
''' + table(['Table and filter', 'Answer', 'Rows read', 'Folders read'], [
    ['<code>orders</code> (not partitioned), <code>order_date=\'2026-10-05\'</code>', '230', '50,000', '1'],
    ['<code>orders_by_day</code>, <code>order_date=\'2026-10-05\'</code>', '230', '<b>1,621</b>', '<b>1</b> of 30'],
    ['<code>orders_by_day</code>, <code>to_date(order_ts)=\'2026-10-05\'</code>', '230', '50,000', '30 of 30'],
], minw=640) + lv + '''
EXAM> “What is partitioning and why is it used?” Say: it splits a table into sub-directories by the value of a column; queries that filter on that column read only the matching directories (partition pruning), so they scan less data. Partition columns are not stored in the data files. Then name static vs dynamic partitions.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Ways to create and fill partitions</h2>
''' + table(['Way', 'Statement', 'Good for'], [
    ['Static INSERT', "<code>INSERT INTO t PARTITION (order_date='2026-10-01') SELECT … WHERE order_date = '2026-10-01'</code>", 'Daily jobs that load one known day'],
    ['Static LOAD', "<code>LOAD DATA LOCAL INPATH 'f.csv' INTO TABLE t PARTITION (dt='2026-10-03')</code>", 'Landing a file that belongs to one day'],
    ['Dynamic INSERT', '<code>INSERT OVERWRITE TABLE t PARTITION (order_date) SELECT …, order_date FROM orders</code>', 'Back-filling many days at once (5.2)'],
    ['Mixed (static + dynamic)', "<code>PARTITION (order_date='2026-10-05', city)</code>", 'One day, split by city automatically'],
    ['Empty partition', "<code>ALTER TABLE t ADD PARTITION (order_date='2026-10-31')</code>", 'Pre-creating folders, external data'],
], minw=720) + '''
''' + table(['Command', 'What it does'], [
    ['<code>SHOW PARTITIONS t [PARTITION (col=\'v\')]</code>', 'Lists partitions, optionally filtered'],
    ['<code>DESCRIBE FORMATTED t PARTITION (col=\'v\')</code>', 'Location, numFiles, numRows, totalSize of one partition'],
    ['<code>ALTER TABLE t ADD [IF NOT EXISTS] PARTITION (…) [LOCATION \'…\']</code>', 'Registers a partition (and its folder)'],
    ['<code>ALTER TABLE t PARTITION (…) RENAME TO PARTITION (…)</code>', 'Changes the value and moves the folder'],
    ['<code>ALTER TABLE t DROP [IF EXISTS] PARTITION (col &gt;= \'v\')</code>', 'Removes one or a range of partitions'],
    ['<code>EXPLAIN DEPENDENCY SELECT …</code>', 'Which partitions the query will read'],
], minw=640) + '''
WARN> Choose a partition column with a <b>moderate</b> number of values that queries filter on: date is the classic choice. Partitioning by <code>customer_id</code> (2,000 values) or <code>order_id</code> (50,000) creates thousands of tiny folders and makes every query slower. Lesson 5.4 covers design.
</section>
'''

dep = capf('l51_dep.txt')
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Kabir builds orders_by_day</h2>
  <p>All outputs are real, from the Hive 4.2.1 lab (database <code>tiffingo</code>).</p>
''' + stepper([
    ('Step 1 · Create the table and load two days with static partitions',
     code('sql', 'Beeline', "CREATE TABLE orders_by_day (\n  order_id INT, customer_id INT, city STRING, order_ts TIMESTAMP,\n  amount DECIMAL(10,2), payment STRING, status STRING)\nPARTITIONED BY (order_date DATE)\nSTORED AS ORC;\n\nINSERT INTO orders_by_day PARTITION (order_date='2026-10-01')\nSELECT order_id, customer_id, city, order_ts, amount, payment, status\nFROM orders WHERE order_date = '2026-10-01';\n-- same for 2026-10-02\n\nSHOW PARTITIONS orders_by_day;\nSELECT order_date, COUNT(*) AS n FROM orders_by_day GROUP BY order_date;",
          tables(capf('l51_create.txt'))[0] + '\n' + tables(capf('l51_create.txt'))[1]),
     '<code>order_date</code> is <b>not</b> in the column list; it appears only in <code>PARTITIONED BY</code>. In a static insert the SELECT returns only the 7 data columns, and the PARTITION clause supplies the date.'),
    ('Step 2 · The partition column is in the folder name, not the file',
     code('sql', 'Beeline', "DESCRIBE orders_by_day;", tables(capf('l51_create.txt'))[2] + "\n\n$ find …/tiffingo.db/orders_by_day -type f\n…/orders_by_day/order_date=2026-10-01/000000_0\n…/orders_by_day/order_date=2026-10-02/000000_0"),
     'DESCRIBE lists <code>order_date</code> twice: as a queryable column, and under “# Partition Information”. On disk each day is a folder <code>order_date=…</code> with its own ORC file. The rest of October was loaded with one dynamic insert (Lesson 5.2), giving 30 partitions.'),
    ('Step 3 · Ask Hive which partitions it will read',
     code('sql', 'Beeline', "EXPLAIN DEPENDENCY SELECT COUNT(*) FROM orders_by_day\nWHERE order_date = '2026-10-05';\n\nEXPLAIN DEPENDENCY SELECT COUNT(*) FROM orders_by_day\nWHERE order_date BETWEEN '2026-10-05' AND '2026-10-07';", tables(dep)[0] + '\n' + tables(dep)[1]),
     '<code>input_partitions</code> lists exactly one folder for one day and three for a three-day range. Pruning happens at <b>planning</b> time, from the metastore, before any file is opened.'),
    ('Step 4 · Prove it with Tez counters',
     code('sql', 'Beeline', "SET hive.tez.exec.print.summary=true;\nSELECT COUNT(*) AS n FROM orders_by_day WHERE order_date='2026-10-05' AND city='Pune';\nSELECT COUNT(*) AS n FROM orders        WHERE order_date='2026-10-05' AND city='Pune';", capf('l51_counters.txt').split('\nSELECT COUNT(*) AS n FROM orders_by_day WHERE to_date')[0]),
     'Both queries answer 230 (Pune, 5 October, the same as Lesson 3.6). The partitioned table read <b>1,621</b> rows; the flat table read all <b>50,000</b>. That is 31 times less work for one day, and the gap grows with every month of history.'),
    ('Step 5 · Trap 1: filtering on the wrong column',
     code('sql', 'Beeline', "SELECT COUNT(*) AS n FROM orders_by_day\nWHERE to_date(order_ts) = '2026-10-05' AND city = 'Pune';\n\n-- EXPLAIN DEPENDENCY, number of input partitions (real):\n--   no WHERE                                        30\n--   city = 'Pune'                                   30\n--   order_date = '2026-10-05' OR city = 'Pune'      30\n--   date_format(order_date, 'EEE') = 'Sat'           4\n--   order_date >= date_sub(current_date, 3)          7\n--   to_date(order_ts) = '2026-10-05'                30",
          capf('l51_counters.txt').split('\n', 4)[4]),
     '<code>order_ts</code> holds the same day, but it is an ordinary column, so Hive must open all 30 folders. Functions on the partition column itself still pruned in 4.2.1 (4 Saturdays, the last 7 days). An <code>OR</code> with a non-partition condition disables pruning. Always filter on the partition column directly.'),
    ('Step 6 · Trap 2: static partitions are trusted, not checked',
     code('sql', 'Beeline', "CREATE TABLE orders_daily_txt (order_id INT, customer_id INT, restaurant_id INT,\n  city STRING, amount INT, payment STRING, status STRING)\nPARTITIONED BY (dt STRING) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',';\n\nLOAD DATA LOCAL INPATH '/data/stage/orders_2026-10-03.csv'\n  INTO TABLE orders_daily_txt PARTITION (dt='2026-10-03');\n-- the next morning, a copy-paste mistake:\nLOAD DATA LOCAL INPATH '/data/stage/orders_2026-10-03.csv'\n  INTO TABLE orders_daily_txt PARTITION (dt='2026-10-04');\n\nSELECT dt, COUNT(*) AS n, SUM(amount) AS rev FROM orders_daily_txt GROUP BY dt ORDER BY dt;\nSELECT COUNT(*) AS same_orders_twice FROM orders_daily_txt a JOIN orders_daily_txt b\n  ON a.order_id = b.order_id AND a.dt = '2026-10-03' AND b.dt = '2026-10-04';", capf('l51_wrong.txt')),
     'Hive moved the file into <code>dt=2026-10-04/</code> without looking inside: the CSV has no date column, so there is nothing to check. 1,668 orders now count twice. The fix was <code>ALTER TABLE orders_daily_txt DROP PARTITION (dt=\'2026-10-04\')</code>. Add a check in daily jobs, such as comparing <code>MIN/MAX(order_ts)</code> with the partition value.'),
    ('Step 7 · Manage partitions and switch on the safety check',
     code('sql', 'Beeline', "ALTER TABLE orders_by_day ADD PARTITION (order_date='2026-10-31');\nALTER TABLE orders_by_day PARTITION (order_date='2026-10-31')\n  RENAME TO PARTITION (order_date='2026-11-01');\nALTER TABLE orders_by_day DROP IF EXISTS PARTITION (order_date >= '2026-11-01');\n\nSET hive.strict.checks.no.partition.filter=true;\nSELECT COUNT(*) FROM orders_by_day;",
          capf('l51_strict.txt').split('. If you know')[0] + ' …'),
     '<code>ADD</code> creates an empty partition (a query on it returns 0 rows), <code>RENAME</code> moves it, and <code>DROP</code> accepts a range. With the strict check on, a query without a partition filter is refused (Error 10056): useful on shared clusters, where one forgotten filter can read years of data.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
def days(sel, red=False):
    o = ''
    for k in range(10):
        on = k in sel
        tone = ('red' if red else 'green') if on else 'card'
        o += box(18 + (k % 5) * 66, 46 + (k // 5) * 44, 60, 36, tone) + t(48 + (k % 5) * 66, 62 + (k // 5) * 44, f'10-{k + 1:02d}', 8, 'ink' if on else 'ink3', mono=True, bold=on) + t(48 + (k % 5) * 66, 75 + (k // 5) * 44, 'read' if on else 'skip', 6.8, 'green' if on and not red else ('red' if on else 'ink3'))
    return o
see = [
    term([('> CREATE TABLE orders_by_day (…)', W), ('  PARTITIONED BY (order_date DATE) STORED AS ORC;', W), ("> INSERT … PARTITION (order_date='2026-10-01') …", W), ('> SHOW PARTITIONS orders_by_day;', W), ('| order_date=2026-10-01 |', G), ('| order_date=2026-10-02 |', G)]),
    term([("> EXPLAIN DEPENDENCY … WHERE order_date = '2026-10-05';", W), ('  "input_partitions":[', W), ('    "…@order_date=2026-10-05"]', G), ('', W), ('  1 partition of 30', G)]),
    term([("> SELECT COUNT(*) … order_date='2026-10-05' AND city='Pune';", W), ('| 230 |', G), ('  RECORDS_IN_Map_1: 1621', G), ('  (flat orders table: 50000)', Y)]),
    term([("> … WHERE to_date(order_ts) = '2026-10-05' …", W), ('| 230 |', G), ('  RECORDS_IN_Map_1: 50000', RD), ('  INPUT_DIRECTORIES_Map_1: 30', RD)]),
    term([("> LOAD DATA … orders_2026-10-03.csv", W), ("    INTO TABLE … PARTITION (dt='2026-10-04');", W), ('| 2026-10-03 | 1668 | 493530 |', G), ('| 2026-10-04 | 1668 | 493530 |', RD), ('  same orders, two days', RD)]),
]
B1 = [
    t(180, 22, 'Metastore: one row per partition', 9.4, bold=True) + box(20, 40, 150, 90, 'violet') + t(95, 56, 'PARTITIONS', 8.2, bold=True, mono=True) + t(30, 74, 'order_date=2026-10-01', 7.2, 'ink2', anchor='start', mono=True) + t(30, 88, 'order_date=2026-10-02', 7.2, 'ink2', anchor='start', mono=True) +
    arrow(172, 82, 206, 82, 'ink3') + folder(212, 52, '10-01/') + folder(270, 52, '10-02/') + cap('Each partition = metastore row + folder.', 'The date is not stored inside the ORC file.', 'blue', y=150, h=46),
    t(180, 22, 'Planner prunes before reading', 9.4, bold=True) + days({4}) + cap('WHERE order_date = 10-05 → one folder', 'decided from metadata alone', 'green', y=150, h=46),
    t(180, 22, 'Work done (rows read)', 9.4, bold=True) + fill(30, 50, 300 * 1621 / 50000, 20, 'green') + t(30, 44, 'orders_by_day: 1,621', 8, 'green', anchor='start', bold=True) + fill(30, 96, 300, 20, 'acc') + t(30, 90, 'orders (flat): 50,000', 8, 'acc', anchor='start', bold=True) +
    cap('Same answer, 31× fewer rows.', 'Grows with every month of history.', 'green', y=150, h=46),
    t(180, 22, 'order_ts is not the partition column', 9.4, bold=True) + days(set(range(10)), red=True) + cap('Hive cannot know which folder holds which order_ts.', 'All 30 folders opened.', 'amber', y=150, h=46),
    t(180, 22, 'Static value = a label, not a check', 9.4, bold=True) + box(30, 46, 120, 50, 'card') + t(90, 66, 'orders_2026-10-03', 7.6, 'ink', mono=True) + t(90, 82, '.csv (no date col)', 7.2, 'ink2', mono=True) +
    arrow(152, 70, 200, 70, 'red', 2) + folder(214, 48, 'dt=2026-10-04/', tone='red') + cap('LOAD only moves the file.', 'Validate dates in the job.', 'amber', y=150, h=46),
]
see_caps = ['Kabir creates the partitioned table and loads two days.',
            'EXPLAIN DEPENDENCY: a one-day query reads one partition.',
            'Tez counters: 1,621 rows read instead of 50,000.',
            'Filtering on order_ts instead reads every folder.',
            'A file loaded into the wrong partition duplicates orders.']
behind_caps = ['Each partition is a row in the metastore and a folder named order_date=….',
               'The planner matches the WHERE clause against partition values and drops the rest.',
               'Fewer folders opened means fewer rows read for the same answer.',
               'order_ts is an ordinary column; only the partition column can prune.',
               'In a static load Hive trusts the value you write and never looks inside the file.']
two = anim_two('Partitions', 'Folders, pruning and the two traps', 'Real Beeline output', 'What the metastore, the planner and the folders do', see, B1, see_caps, behind_caps)

# ---- scenario 1: daily ETL with overwrite
e1 = (t(180, 22, 'Nightly job: load yesterday', 9.4, bold=True) + t(180, 56, "INSERT OVERWRITE TABLE orders_by_day", 8.4, 'ink', mono=True) + t(180, 72, "  PARTITION (order_date='${hivevar:d}') SELECT …", 8.4, 'ink', mono=True) + cap('One partition per run, value passed in.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Job fails half-way and is re-run', 9.4, bold=True) + t(180, 56, 'INTO would add the rows a second time', 8.4, 'red') + t(180, 74, 'OVERWRITE replaces just that partition', 8.4, 'green', bold=True) + cap('Re-runs are safe (idempotent).', '', 'green', y=150, h=34))
e3 = (t(180, 22, 'Other days are untouched', 9.4, bold=True) + days({4}) + cap('OVERWRITE on one partition never deletes the others.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Check before publishing', 9.4, bold=True) + t(180, 56, 'MIN(to_date(order_ts)) = MAX(…) = ${d} ?', 8.4, 'ink', mono=True) + cap('Catches the wrong-date load from Step 6.', '', 'amber', y=150, h=34))
e5 = (t(180, 22, 'Retention', 9.4, 'acc', bold=True) + t(180, 56, "ALTER TABLE … DROP PARTITION (order_date < '2025-10-01')", 7.8, 'ink', mono=True) + cap('Old data goes in one metadata operation.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'A nightly load that is safe to re-run',
              'Most production tables are loaded one partition per run. INSERT OVERWRITE on that partition makes re-runs safe. (Typical pattern.)',
              'Daily partition load', 'A nightly job overwrites one date partition, can be re-run safely, leaves other days alone, is validated and old partitions are dropped', [e1, e2, e3, e4, e5],
              ['The scheduler passes yesterday’s date into the job.',
               'If the job is re-run, OVERWRITE replaces the partition instead of doubling it.',
               'Only the named partition changes.',
               'A quick check confirms the data really belongs to that day.',
               'Retention is one DROP PARTITION with a range.'],
              hid='scenario-nightly')

# ---- scenario 2: forgotten filter
f1 = (t(180, 22, 'A dashboard query without a date filter', 9.4, bold=True) + t(180, 56, 'SELECT city, SUM(amount) FROM orders_by_day GROUP BY city', 7.8, 'ink', mono=True) + cap('Reads every partition: years of data.', '', 'amber', y=150, h=34))
f2 = term([('> SET hive.strict.checks.no.partition.filter=true;', W), ('> SELECT COUNT(*) FROM orders_by_day;', W), ('Error 10056: Queries against partitioned', RD), ('  tables without a partition filter are', RD), ('  disabled for safety reasons.', RD)], label='real output · Hive 4.2.1')
f3 = term([('> SET hive.strict.checks.no.partition.filter=true;', W), ("> SELECT COUNT(*) AS n FROM orders_by_day", W), ("    WHERE order_date = '2026-10-05';", W), ('| 1621 |', G)], label='real output · Hive 4.2.1')
f4 = (t(180, 22, 'Where to set it', 9.4, bold=True) + t(180, 56, 'hive-site.xml for shared clusters, or per session', 8.4, 'ink2') + cap('Default in 4.2.1 is false.', '', 'blue', y=150, h=34))
f5 = (t(180, 22, 'Result', 9.4, 'acc', bold=True) + t(180, 56, 'mistakes fail fast instead of running for an hour', 8.4, 'ink2') + cap('Cheap protection for busy clusters.', '', 'green', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Stopping full-table scans on a shared cluster',
              'One missing WHERE clause on a partitioned table can read years of data. Hive can refuse such queries. Results are real.',
              'Strict partition filter', 'With the strict check enabled, a query without a partition filter fails with error 10056 and a filtered one runs', [f1, f2, f3, f4, f5],
              ['A dashboard query forgot the date filter.',
               'With the strict check on, Hive refuses it with error 10056.',
               'The same query with a partition filter runs normally.',
               'Admins set it cluster-wide; users can set it per session.',
               'Costly mistakes now fail in a second.'],
              hid='scenario-strict')

# ---- scenario 3: two levels
m1 = (t(180, 22, 'Kitchen managers query one city, one day', 9.4, bold=True) + t(180, 56, 'PARTITIONED BY (order_date DATE, city STRING)', 8, 'ink', mono=True) + cap('Two-level folders: order_date=…/city=…/', '', 'blue', y=150, h=34))
m2 = term([('> SHOW PARTITIONS orders_day_city;', W), ('| order_date=2026-10-05/city=Bengaluru |', G), ('| order_date=2026-10-05/city=Chennai   |', G), ('| …                                    |', W), ('| order_date=2026-10-05/city=Thane     |', G), ('  8 partitions for one day', Y)], label='real output · Hive 4.2.1', size=7.4)
m3 = (t(180, 22, 'Filter on both → one small folder', 9.4, bold=True) + t(180, 56, "order_date='2026-10-05' AND city='Thane'", 8.4, 'green', mono=True) + cap('Filter on city only → one folder per day.', 'Order the levels by how queries filter.', 'green', y=150, h=46))
m4 = (t(180, 22, 'The cost', 9.4, bold=True) + t(180, 56, '30 days × 8 cities = 240 partitions / month', 8.4, 'ink', mono=True) + t(180, 74, 'smaller files, more metastore rows', 8.4, 'red') + cap('Each level multiplies the partition count.', '', 'amber', y=150, h=34))
m5 = (t(180, 22, 'Rule of thumb', 9.4, 'acc', bold=True) + t(180, 56, 'aim for hundreds of MB or more per partition', 7.8, 'ink2') + cap('Details and alternatives in Lesson 5.4.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Two-level partitions: date and city',
              'Nested partitions make very selective queries cheap, at the price of many more folders. Partition list is real.',
              'Multi-level partitions', 'A table partitioned by date and city creates eight folders per day; filtering on both reads one small folder', [m1, m2, m3, m4, m5],
              ['The table is partitioned first by date, then by city.',
               'One day created eight city folders.',
               'Filtering on both columns reads a single small folder.',
               'But the number of partitions multiplies.',
               'Keep partitions large; Lesson 5.4 shows the alternatives.'],
              hid='scenario-multilevel')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Folders, metadata and pruning</h2>
  <p>Left: real Beeline output. Right: what the metastore, the planner and the folders do.</p>
''' + two + '''
  <p>Three live scenarios follow: a safe nightly load, a safety switch for shared clusters, and two-level partitions.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Partitioning at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'dt=…', 11, 'green', bold=True, mono=True) + t(60, 58, 'daily tables', 7.4, 'ink2'),
    '1. Daily event and transaction tables',
    'Payment, click and order tables in data lakes are almost always partitioned by date, so daily reports and nightly jobs read one day.',
    ['Events', '*PARTITIONED BY dt', 'Daily reports']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'DROP', 11, 'blue', bold=True, mono=True) + t(60, 58, 'retention', 7.4, 'ink2'),
    '2. Data retention and privacy rules',
    'Policies such as “keep raw logs for 90 days” are applied by dropping old partitions, a quick metadata operation instead of a DELETE over billions of rows.',
    ['Old partitions', '*DROP PARTITION', 'Compliant lake']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'OVERWRITE', 9, 'violet', bold=True, mono=True) + t(60, 58, 're-runnable', 7.4, 'ink2'),
    '3. Safe re-processing',
    'When late data arrives or a bug is fixed, teams rebuild only the affected days with INSERT OVERWRITE … PARTITION, without touching the rest of the table.',
    ['Fix', '*OVERWRITE one day', 'Corrected history']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'region=…', 10, 'acc', bold=True, mono=True) + t(60, 58, 'per country', 7.4, 'ink2'),
    '4. Regional data',
    'Companies operating in several countries often add a region or country level, so local teams and local data rules work on their own folders.',
    ['Global table', '*region partition', 'Local queries']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'Spark/Trino', 9, 'acc', bold=True) + t(60, 58, 'same folders', 7.4, 'ink2'),
    '5. Shared by many engines',
    'The same partitioned folders in the metastore are pruned by Spark, Trino and Impala too, so one good layout speeds up every tool.',
    ['Metastore', '*partition list', 'Any engine']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> you need managed vs external tables (<a href="../../02-hiveql/02-managed-vs-external-tables/">2.2</a>), loading data (<a href="../../02-hiveql/05-loading-data/">2.5</a>) and how a query becomes a job (<a href="../../01-introduction/04-how-a-hive-query-becomes-a-job/">1.4</a>).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
