import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()

def folder(x, y, label, tone='card', on=True):
    op = '' if on else ' opacity=".3"'
    return f'<g{op}>' + f'<path d="M{x} {y+4}h14l4 4h26v22h-44z" class="{TONES[tone][0]}" style="stroke:{TONES[tone][1]}"/>' + t(x + 22, y + 40, label, 6.6, 'ink2', mono=True) + '</g>'

# ---------------------------------------------------------------- story
sc = (box(10, 12, 200, 128, 'card') + t(110, 30, 'orders (50,000 rows)', 8.8, bold=True) +
      ''.join(t(22, 50 + k * 14, s, 7.2, 'ink2', anchor='start', mono=True) for k, s in enumerate(['100001 … 2026-10-17', '100002 … 2026-10-20', '100003 … 2026-10-29', '100004 … 2026-10-03', '…'])) +
      t(110, 128, 'order_date = last SELECT column', 7.2, 'acc', bold=True) +
      arrow(216, 76, 262, 76, 'acc', 2.2) + box(268, 52, 96, 48, 'acc') + t(316, 72, 'one INSERT', 8.4, bold=True) + t(316, 86, 'PARTITION (order_date)', 6.6, 'ink2', mono=True) +
      arrow(370, 76, 410, 76, 'acc', 2.2) + box(416, 12, 214, 128, 'green') + t(523, 30, '30 folders, created by Hive', 8.8, 'green', bold=True) +
      ''.join(folder(428 + (k % 4) * 50, 42 + (k // 4) * 44, f'10-{k + 1:02d}', 'green') for k in range(8)) + t(523, 134, '… up to 10-30', 7.4, 'ink2'))
scene_svg = scene('Fifty thousand orders flow through one INSERT statement whose partition value comes from the last column of the SELECT; Hive creates thirty date folders on its own.', sc,
                  'A <tspan font-weight="700" class="s-acc">dynamic partition</tspan> takes its value from the data, so one statement fills many partitions.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Thirty INSERT statements for one month? There must be a better way.”</h2>
  <div class="story">
    <p class="narration">In Lesson 5.1 Kabir loaded two days of <code>orders_by_day</code> by hand, one static INSERT per day. Now he has to back-fill the whole month, and next week the app team will start dropping click files into date folders that Hive does not know about yet.</p>

{scene_svg}

K> Sir, do I really write 30 INSERT statements, one per date?
A> No. Leave the value out: <code>PARTITION (order_date)</code>, and put <code>order_date</code> as the <b>last</b> column of the SELECT. Hive reads the date of every row and writes it to the right folder, creating folders as it goes. That is a <b>dynamic partition</b> insert.
R> And the app team’s folders? Files are already there, in <code>dt=2026-10-01</code> style folders.
A> Then the files exist but the metastore has no partition rows, so Hive sees an empty table. <code>MSCK REPAIR TABLE</code> scans the folders and registers what is missing. Today: one-statement back-fills, the limits that protect the cluster, three traps we hit in the lab (wrong column order, NULL values, a missing folder), and what MSCK can and cannot repair. All outputs are real, from Hive 4.2.1.
  </div>
</section>
'''

lv = '''
LEVELS> Dynamic partitions and MSCK at three levels
L1> Hive sorts the letters for you
      <ul>
        <li>Static partition: you put every letter into the box you choose. Dynamic partition: you hand Hive the whole pile and it reads the address on each letter, opening a new box when it needs one.</li>
        <li>Write <code>PARTITION (order_date)</code> without a value, and put <code>order_date</code> last in the SELECT.</li>
        <li><b>MSCK REPAIR TABLE</b> is the opposite direction: boxes already exist on the shelf, and Hive writes them into its register (the metastore).</li>
      </ul>
L2> The settings and the rules
      <ul>
        <li><code>hive.exec.dynamic.partition</code> (default <b>true</b>) and <code>hive.exec.dynamic.partition.mode</code>. In our Hive 4.2.1 lab the default mode is <b>nonstrict</b>; many tutorials, written for older versions, say strict. In <b>strict</b> mode at least one partition column must be static (Error 10096).</li>
        <li>Dynamic partition columns are matched <b>by position</b>: they must be the last SELECT columns, in the same order as in PARTITION (…). Static levels must come before dynamic ones: <code>PARTITION (order_date='…', city)</code>.</li>
        <li>Limits: <code>hive.exec.max.dynamic.partitions</code> (1000 per statement) and <code>hive.exec.max.dynamic.partitions.pernode</code> (100 per task). They stop a bad column from creating thousands of folders.</li>
        <li>A NULL value goes to <code>__HIVE_DEFAULT_PARTITION__</code> (<code>hive.exec.default.partition.name</code>).</li>
      </ul>
L3> MSCK in Hive 4.2.1: options and edges
      <ul>
        <li><code>MSCK REPAIR TABLE t [ADD | DROP | SYNC PARTITIONS]</code>. Plain MSCK = ADD: it registers new <code>col=value</code> folders but never removes entries whose folders are gone. DROP removes those; SYNC does both.</li>
        <li>A folder that does not follow <code>col=value</code> made MSCK fail (“Invalid partition name”) because <code>hive.msck.path.validation=throw</code> by default; <code>skip</code> ignores such folders, <code>ignore</code> tries to use them anyway.</li>
        <li>SYNC treated a partition we had added with a custom <code>LOCATION</code> as missing and dropped it. Keep custom locations out of tables you SYNC.</li>
        <li>A partition whose folder was deleted made every query on the table fail (“Input path does not exist”) until it was repaired.</li>
        <li>Hive 4’s metastore also has a background partition-management task that can discover partitions for tables with the <code>discover.partitions=true</code> property (vendor platforms such as Cloudera switch it on for external tables). Our external table in plain Apache 4.2.1 did not have the property, so we used MSCK.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Dynamic partitions and partition repair</h2>
''' + def_block(
    'In a <b>dynamic partition insert</b> the partition clause names the partition columns without values, <code>INSERT OVERWRITE TABLE t PARTITION (col) SELECT …, col FROM src</code>, and Hive determines each row’s partition from the trailing columns of the SELECT, creating partitions as needed. It is controlled by <code>hive.exec.dynamic.partition</code>, <code>hive.exec.dynamic.partition.mode</code> (strict requires at least one static partition column) and limits on the number of partitions created. <b>MSCK REPAIR TABLE</b> compares the partition directories under a table’s location with the partitions registered in the metastore and adds (and optionally drops) metastore entries so that they match.',
    'Dynamic partitions let Hive decide which folder each row goes to, using a column of the data, so one statement can fill a month of partitions. MSCK REPAIR does the reverse job: when folders were created outside Hive, it tells the metastore about them.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Dynamic partition', '<code>PARTITION (order_date)</code> with no value; the value comes from the data.'),
    ('Mixed partition', '<code>PARTITION (order_date=\'2026-10-05\', city)</code>: static first, then dynamic.'),
    ('Strict / nonstrict', 'Strict mode demands at least one static partition column.'),
    ('pernode limit', 'Max partitions one task may create (default 100).'),
    ('__HIVE_DEFAULT_PARTITION__', 'Folder name used for NULL (or empty) partition values.'),
    ('MSCK REPAIR TABLE', 'Registers partition folders that exist on storage but not in the metastore.'),
    ('ADD / DROP / SYNC', 'MSCK options: add missing, drop stale, or both.'),
    ('hive.msck.path.validation', 'What MSCK does with badly named folders: throw (default), skip, ignore.'),
]) + '''

  <h3>Static vs dynamic partitions</h3>
''' + table(['', 'Static', 'Dynamic'], [
    ['Partition value', 'Written in the statement', 'Taken from the last SELECT columns'],
    ['Statements for 30 days', '30', '1'],
    ['Partition column in SELECT', 'Left out', 'Must be last, in order'],
    ['Checks', 'None: value is trusted (5.1)', 'Value is real data, but a wrong column order is not detected'],
    ['Typical use', 'Daily job for a known date', 'Back-fills, re-partitioning, splitting by city'],
    ['Cost', 'Each task writes one partition', 'Each task may write many: memory and many files'],
], minw=620) + lv + '''
EXAM> “Static vs dynamic partitioning” and “What does MSCK REPAIR TABLE do?” are standard questions. For dynamic, mention the two settings, that the partition column goes last in the SELECT, and the max-partition limits. For MSCK, say it syncs folders on HDFS with partition entries in the metastore, typically after files are copied in from outside Hive.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Getting partitions into the metastore</h2>
''' + table(['Situation', 'Use', 'Example'], [
    ['Back-fill a month from a flat table', 'Dynamic INSERT', '<code>INSERT OVERWRITE TABLE orders_by_day PARTITION (order_date) SELECT …, order_date FROM orders</code>'],
    ['One known day, split by city', 'Mixed static + dynamic', "<code>PARTITION (order_date='2026-10-05', city)</code>"],
    ['Files land in <code>dt=…</code> folders from another tool', 'MSCK REPAIR TABLE', '<code>MSCK REPAIR TABLE app_clicks</code>'],
    ['Folders deleted outside Hive', 'MSCK … DROP / SYNC PARTITIONS', '<code>MSCK REPAIR TABLE app_clicks SYNC PARTITIONS</code>'],
    ['Folder with a different layout', 'ALTER TABLE … ADD PARTITION … LOCATION', "<code>ADD PARTITION (dt='2026-10-04') LOCATION '…/2026/10/04'</code>"],
    ['One new folder every day', 'ALTER TABLE … ADD IF NOT EXISTS PARTITION', 'Cheaper than scanning everything with MSCK'],
], minw=720) + '''
''' + table(['Setting', 'Default in our 4.2.1 lab', 'Meaning'], [
    ['<code>hive.exec.dynamic.partition</code>', 'true', 'Dynamic partitions allowed'],
    ['<code>hive.exec.dynamic.partition.mode</code>', '<b>nonstrict</b>', 'strict needs one static column'],
    ['<code>hive.exec.max.dynamic.partitions</code>', '1000', 'Per statement'],
    ['<code>hive.exec.max.dynamic.partitions.pernode</code>', '100', 'Per task'],
    ['<code>hive.exec.default.partition.name</code>', '__HIVE_DEFAULT_PARTITION__', 'Where NULL values go'],
    ['<code>hive.msck.path.validation</code>', 'throw', 'Badly named folder → MSCK fails'],
], minw=640) + '''
WARN> A dynamic insert trusts the <b>position</b> of the columns, not their names. Put the wrong column last and Hive happily creates one partition per distinct value of that column. Always run the SELECT alone first and look at the last column.
</section>
'''

ord_bad = capf('l52_order.txt')
nulls = tables(capf('l52_null.txt'))
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Back-fill, three traps, then repair the click table</h2>
  <p>All outputs are real, from the Hive 4.2.1 lab (database <code>tiffingo</code>).</p>
''' + stepper([
    ('Step 1 · Check the settings, then back-fill a month in one statement',
     code('sql', 'Beeline', "SET hive.exec.dynamic.partition;\nSET hive.exec.dynamic.partition.mode;\n\nINSERT OVERWRITE TABLE orders_by_day PARTITION (order_date)\nSELECT order_id, customer_id, city, order_ts, amount, payment, status,\n       order_date                       -- partition column LAST\nFROM orders;\nSHOW PARTITIONS orders_by_day;",
          tables(capf('l51_set.txt'))[0] + '\n' + tables(capf('l51_set.txt'))[1] + '\n+------------------------+\n|       partition        |\n+------------------------+\n| order_date=2026-10-01  |\n| order_date=2026-10-02  |\n| …                      |\n| order_date=2026-10-30  |\n+------------------------+\n30 rows selected'),
     'Dynamic partitions are on and the mode is <b>nonstrict</b> in 4.2.1, so this works without any SET. One statement created 30 partitions. INSERT OVERWRITE replaces only the partitions that the query writes.'),
    ('Step 2 · Strict mode, the older default',
     code('sql', 'Beeline', "SET hive.exec.dynamic.partition.mode=strict;\nINSERT OVERWRITE TABLE orders_dyn PARTITION (order_date)\nSELECT order_id, customer_id, city, order_ts, amount, payment, status, order_date\nFROM orders;", capf('l52_strict.txt').split('; Query ID')[0]),
     'Strict mode demands at least one static column, for example <code>PARTITION (order_date=\'2026-10-05\', city)</code>. Many clusters (and many tutorials) still use strict, which is why you so often see <code>SET hive.exec.dynamic.partition.mode=nonstrict</code> at the top of scripts.'),
    ('Step 3 · Trap 1: the wrong column last',
     code('sql', 'Beeline', "CREATE TABLE pay_by_mode (order_id INT, amount DECIMAL(10,2))\nPARTITIONED BY (payment STRING) STORED AS ORC;\n\nINSERT OVERWRITE TABLE pay_by_mode PARTITION (payment)\nSELECT order_id, payment, amount          -- oops: amount is last\nFROM orders WHERE order_date = '2026-10-05';\n\nSELECT COUNT(*) AS partitions FROM (SELECT DISTINCT payment FROM pay_by_mode) x;\nSELECT payment, order_id, amount FROM pay_by_mode ORDER BY order_id LIMIT 3;", ord_bad),
     'Hive matched columns by position: <code>payment</code> went into the <code>amount</code> column (and became NULL, since “UPI” is not a number), and every distinct amount became a partition: <b>69 folders</b> like <code>payment=480.00</code>. No error, no warning.'),
    ('Step 4 · Re-running correctly does not clean up',
     code('sql', 'Beeline', "INSERT OVERWRITE TABLE pay_by_mode PARTITION (payment)\nSELECT order_id, amount, payment FROM orders WHERE order_date = '2026-10-05';\nSHOW PARTITIONS pay_by_mode;      -- 73 rows: 69 bad + 4 good\n\nALTER TABLE pay_by_mode DROP PARTITION (payment < 'A');\nSHOW PARTITIONS pay_by_mode;", '+-----------------+\n|    partition    |\n+-----------------+\n| payment=100.00  |\n| …  (69 numeric) |\n| payment=Card    |\n| payment=COD     |\n| payment=UPI     |\n| payment=Wallet  |\n+-----------------+\n\n' + capf('l52_order_fix.txt')),
     'A dynamic INSERT OVERWRITE replaces only the partitions it writes; the 69 wrong ones stayed and would still show up in every <code>GROUP BY payment</code>. Digits sort before letters, so <code>payment &lt; \'A\'</code> dropped exactly the numeric folders. On a real table, recreate it or drop the bad partitions explicitly.'),
    ('Step 5 · Trap 2: NULL values and the default partition',
     code('sql', 'Beeline', "CREATE TABLE cust_by_ref (customer_id INT, name STRING)\nPARTITIONED BY (ref_city STRING) STORED AS ORC;\nINSERT OVERWRITE TABLE cust_by_ref PARTITION (ref_city)\nSELECT customer_id, name, IF(customer_id % 4 = 0, NULL, city)\nFROM customers WHERE customer_id <= 40;\n\nSHOW PARTITIONS cust_by_ref;\nSELECT COUNT(*) AS null_rows FROM cust_by_ref WHERE ref_city IS NULL;\nSELECT COUNT(*) AS by_name FROM cust_by_ref\nWHERE ref_city = '__HIVE_DEFAULT_PARTITION__';", nulls[0] + '\n' + nulls[2] + '\n' + capf('l52_null2.txt')),
     'Ten customers had no referral city. Their rows went into <code>ref_city=__HIVE_DEFAULT_PARTITION__</code>, and in our lab <code>IS NULL</code> found <b>0</b> of them while the folder name found all 10. Replace NULLs before inserting, e.g. <code>coalesce(city, \'UNKNOWN\')</code>.'),
    ('Step 6 · The safety limits',
     code('sql', 'Beeline', "SET hive.exec.max.dynamic.partitions.pernode=10;\nINSERT OVERWRITE TABLE orders_dyn PARTITION (order_date) SELECT …, order_date FROM orders;\n\nSET hive.exec.max.dynamic.partitions=20;\nINSERT OVERWRITE TABLE orders_dyn PARTITION (order_date) SELECT …, order_date FROM orders;",
          capf('l52_pernode.txt') + '\n\n' + capf('l52_max.txt').split('; Query ID')[0]),
     'The per-task limit stops the task at the 11th partition (Error 20004); the per-statement limit is checked when files are moved into place, with the exact count it needed (30). The defaults (100 and 1000) are fine for daily data; raise them deliberately for big back-fills, never “just in case”.'),
    ('Step 7 · Files arrive outside Hive: MSCK REPAIR TABLE',
     code('sql', 'Beeline', "-- the app team already wrote …/clicks/dt=2026-10-01/part-0.csv\nCREATE EXTERNAL TABLE app_clicks (event_ts STRING, ip STRING, path STRING,\n  http_code INT, bytes INT)\nPARTITIONED BY (dt STRING)\nROW FORMAT DELIMITED FIELDS TERMINATED BY ','\nLOCATION 'file:///data/tiffingo/clicks';\nSELECT COUNT(*) AS n FROM app_clicks;\n\nMSCK REPAIR TABLE app_clicks;\nSELECT dt, COUNT(*) AS n FROM app_clicks GROUP BY dt;", tables(capf('l52_msck1.txt'))[1] + '\n\n' + tables(capf('l52_msck2.txt'))[1]),
     'The files were there, but the metastore had no partitions, so the table looked empty (0). MSCK found the <code>dt=2026-10-01</code> folder and registered it: 2,336 clicks. Files added later stay invisible until MSCK (or ALTER TABLE … ADD PARTITION) runs again.'),
    ('Step 8 · A badly named folder, a custom location and a deleted folder',
     code('sql', 'Beeline', "-- new folders: dt=2026-10-02, dt=2026-10-03 and 2026/10/04 (wrong layout)\nMSCK REPAIR TABLE app_clicks;\n\nSET hive.msck.path.validation=skip;\nMSCK REPAIR TABLE app_clicks;\nALTER TABLE app_clicks ADD PARTITION (dt='2026-10-04')\n  LOCATION 'file:///data/tiffingo/clicks/2026/10/04';\n\n-- later, someone deletes the dt=2026-10-01 folder\nSELECT dt, COUNT(*) FROM app_clicks GROUP BY dt;\nMSCK REPAIR TABLE app_clicks;                     -- still 4 partitions\nMSCK REPAIR TABLE app_clicks SYNC PARTITIONS;\nSHOW PARTITIONS app_clicks;",
          capf('l52_msck3.txt').split('Error: ')[1].split('; Query ID')[0].join(['Error: ', '']) + '\n\n' + tables(capf('l52_msck4.txt'))[3] + '\n\n' + 'Error: … InvalidInputException: Input path does not exist: file:/data/tiffingo/clicks/dt=2026-10-01\n\n' + tables(capf('l52_msck6.txt'))[1]),
     'One folder named <code>2026</code> made MSCK fail completely; with <code>skip</code> it registered 10-02 and 10-03, and ALTER … LOCATION added 10-04 (now 4 days: 2,336 + 664 + 500 + 300 rows). Deleting a folder broke every query on the table, and plain MSCK did not help, because it only adds. <b>SYNC</b> removed 10-01, but it also removed 10-04, whose folder was outside the <code>dt=…</code> layout. Prefer ADD/DROP on tables with custom locations.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('> INSERT OVERWRITE TABLE orders_by_day', W), ('    PARTITION (order_date)', W), ('  SELECT …, order_date FROM orders;', W), ('> SHOW PARTITIONS orders_by_day;', W), ('  30 rows: 2026-10-01 … 2026-10-30', G)]),
    term([('> … PARTITION (payment)', W), ('  SELECT order_id, payment, amount …', W), ('| partitions |', W), ('| 69         |', RD), ('| 480.00 | 100005 | NULL |', RD)]),
    term([('> … IF(customer_id % 4 = 0, NULL, city)', W), ('| ref_city=__HIVE_DEFAULT_PARTITION__ |', Y), ('> … WHERE ref_city IS NULL;', W), ('| 0  |', RD), ("> … = '__HIVE_DEFAULT_PARTITION__';  | 10 |", G)]),
    term([('> CREATE EXTERNAL TABLE app_clicks … ;', W), ('> SELECT COUNT(*) FROM app_clicks;   | 0 |', Y), ('> MSCK REPAIR TABLE app_clicks;', W), ('| 2026-10-01 | 2336 |', G)]),
    term([('> MSCK REPAIR TABLE app_clicks;', W), ('  Invalid partition name …/clicks/2026', RD), ('> SET hive.msck.path.validation=skip;', W), ('> … SYNC PARTITIONS;', W), ('  dt=2026-10-02, dt=2026-10-03 only', Y)]),
]
def row(y, cells, colors):
    return ''.join(box(20 + k * 80, y, 76, 18, colors[k]) + t(58 + k * 80, y + 13, c, 7.4, 'ink', mono=True) for k, c in enumerate(cells))
B1 = [
    t(180, 22, 'Each row’s last column picks the folder', 9.4, bold=True) + row(40, ['100004', '…', '180.00', '10-03'], ['card', 'card', 'card', 'acc']) + row(64, ['100001', '…', '530.00', '10-17'], ['card', 'card', 'card', 'acc']) +
    arrow(338, 58, 338, 100, 'acc') + folder(150, 98, 'order_date=10-03', 'green') + folder(230, 98, 'order_date=10-17', 'green') + cap('New value → new folder, created on the fly.', '', 'green', y=150, h=34),
    t(180, 22, 'Columns are matched by position', 9.4, bold=True) + row(40, ['order_id', 'payment', 'amount', ''], ['card', 'acc', 'red', 'card']) + t(58, 76, 'order_id', 7.4, 'ink2', mono=True) + t(138, 76, '→ amount', 7.4, 'red', mono=True) + t(218, 76, '→ partition', 7.4, 'red', mono=True) +
    t(180, 104, "'UPI' → DECIMAL → NULL;  480.00 → folder", 8, 'red', mono=True) + cap('Names are ignored; order decides.', '69 bogus partitions, no error.', 'amber', y=150, h=46),
    t(180, 22, 'NULL becomes a folder name', 9.4, bold=True) + t(180, 52, "NULL → 'ref_city=__HIVE_DEFAULT_PARTITION__'", 8, 'ink', mono=True) + folder(158, 66, '__HIVE_DEFAULT…', 'amber') +
    cap('In our lab IS NULL did not match it.', "Use coalesce(col, 'UNKNOWN') before inserting.", 'amber', y=150, h=46),
    t(180, 22, 'Storage and metastore out of sync', 9.4, bold=True) + box(20, 42, 150, 80, 'card') + t(95, 58, 'storage', 8.2, bold=True) + folder(72, 66, 'dt=10-01') +
    box(190, 42, 150, 80, 'violet') + t(265, 58, 'metastore', 8.2, bold=True) + t(265, 88, '(no rows)', 8, 'ink3') + t(265, 106, 'MSCK → dt=10-01', 7.8, 'green', mono=True, bold=True) + cap('MSCK copies folder names into the metastore.', '', 'blue', y=150, h=34),
    t(180, 22, 'What each MSCK option does', 9.4, bold=True) + ''.join(t(26, 52 + k * 18, s, 8, 'ink', anchor='start', mono=True) for k, s in enumerate(['ADD  (default): register new col=value folders', 'DROP: remove entries whose folder is gone', 'SYNC: ADD + DROP', 'custom LOCATION ≠ col=value → seen as gone'])) +
    cap('Pick the option, and know your layout.', '', 'amber', y=150, h=34),
]
see_caps = ['One dynamic INSERT creates all 30 date partitions.',
            'With the wrong column last, every amount became a partition.',
            'NULL values land in __HIVE_DEFAULT_PARTITION__, which IS NULL did not find.',
            'Folders written outside Hive appear only after MSCK REPAIR.',
            'A badly named folder breaks MSCK; SYNC also dropped a custom-location partition.']
behind_caps = ['Hive reads the trailing SELECT column of each row and writes the row into that partition folder.',
               'Partition columns are taken by position, so a wrong order puts the wrong data into the folder names.',
               'There is no folder name for NULL, so Hive uses a special default name.',
               'MSCK lists the folders under the table location and adds the missing ones to the metastore.',
               'ADD only adds; DROP and SYNC remove entries without a matching col=value folder.']
two = anim_two('Dynamic partitions', 'How Hive picks folders, and how MSCK syncs them', 'Real Beeline output', 'What Hive does with each row and each folder', see, B1, see_caps, behind_caps)

# ---- scenario 1: back-fill with a mixed partition
b1 = (t(180, 22, 'Re-partition a year of orders by city', 9.4, bold=True) + t(180, 56, 'PARTITION (order_date, city)', 8.6, 'ink', mono=True) + t(180, 74, '365 days × 8 cities = 2,920 partitions', 8.4, 'red', mono=True) + cap('More than the 1,000-per-statement limit.', '', 'amber', y=150, h=34))
b2 = (t(180, 22, 'Option 1: raise the limits', 9.4, bold=True) + t(180, 56, 'SET hive.exec.max.dynamic.partitions=3000;', 8, 'ink', mono=True) + t(180, 72, 'SET hive.exec.max.dynamic.partitions.pernode=…;', 8, 'ink', mono=True) + cap('Works, but each task may hold many open files.', 'Memory pressure on big data.', 'amber', y=150, h=46))
b3 = (t(180, 22, 'Option 2: one month per run', 9.4, bold=True) + t(180, 56, "WHERE order_date BETWEEN '2026-01-01' AND '2026-01-31'", 7.8, 'ink', mono=True) + t(180, 74, '≈ 31 × 8 = 248 partitions per run', 8.4, 'green', mono=True) + cap('Smaller, restartable chunks.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Option 3: DISTRIBUTE BY the partition keys', 9.4, bold=True) + t(180, 56, '… DISTRIBUTE BY order_date, city', 8.4, 'ink', mono=True) + cap('Each reducer writes few partitions, one file each.', 'Fewer small files (Lesson 5.4).', 'green', y=150, h=46))
b5 = (t(180, 22, 'Verify', 9.4, 'acc', bold=True) + t(180, 56, 'COUNT(*) per month: old table = new table', 8.4, 'ink2', mono=True) + cap('Then swap the table names.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Back-filling a year into date and city partitions',
              'A re-partitioning job meets the dynamic partition limits. Three ways through. (Typical plan; numbers from our data shape.)',
              'Large back-fill', 'A year by date and city needs 2,920 partitions, more than the default limit; raise limits, split by month, or distribute by the keys', [b1, b2, b3, b4, b5],
              ['A year by date and city needs about 2,920 partitions.',
               'You can raise the limits, at the cost of memory and open files.',
               'Or run one month at a time.',
               'DISTRIBUTE BY the partition keys keeps each reducer to a few partitions.',
               'Compare counts before switching.'],
              hid='scenario-backfill')

# ---- scenario 2: daily landing with ADD PARTITION
d1 = (t(180, 22, 'Upstream job writes one folder a day', 9.4, bold=True) + folder(60, 46, 'dt=10-02', 'green') + folder(130, 46, 'dt=10-03', 'green') + folder(200, 46, 'dt=10-04', 'green') + cap('Hive must learn about each new folder.', '', 'blue', y=150, h=34))
d2 = (t(180, 22, 'MSCK every day?', 9.4, bold=True) + t(180, 56, 'lists every folder of the table, every time', 8.4, 'ink2') + t(180, 74, 'slow when the table has years of folders', 8.4, 'red') + cap('Fine for small tables or one-off repairs.', '', 'amber', y=150, h=34))
d3 = (t(180, 22, 'Better: add exactly the new one', 9.4, bold=True) + t(180, 56, "ALTER TABLE app_clicks ADD IF NOT EXISTS", 8.2, 'ink', mono=True) + t(180, 72, "  PARTITION (dt='${hivevar:d}');", 8.2, 'ink', mono=True) + cap('Instant, and safe to re-run.', '', 'green', y=150, h=34))
d4 = term([("> ALTER TABLE app_clicks ADD PARTITION (dt='2026-10-04')", W), ("    LOCATION '…/clicks/2026/10/04';", W), ('| 2026-10-04 | 300 |', G)], label='real output · Hive 4.2.1')
d5 = (t(180, 22, 'Schedule', 9.4, 'acc', bold=True) + t(180, 56, 'land files → ADD PARTITION → row-count check', 8.4, 'ink2') + cap('MSCK … SYNC weekly as a safety net (no custom locations).', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Registering a new folder every day',
              'Many pipelines write files with Spark, Flume or a copy job and then tell Hive. Real ALTER result below.',
              'Daily partition registration', 'Instead of scanning all folders with MSCK daily, the job adds the one new partition with ALTER TABLE ADD PARTITION', [d1, d2, d3, d4, d5],
              ['Another tool writes a new date folder every day.',
               'MSCK lists every folder each time, which grows slow.',
               'ALTER TABLE … ADD IF NOT EXISTS PARTITION registers just the new one.',
               'It also handles folders with a different layout, via LOCATION.',
               'A periodic MSCK can catch anything missed.'],
              hid='scenario-addpartition')

# ---- scenario 3: deleted folder incident
x1 = (t(180, 22, '09:00 · every dashboard on app_clicks fails', 9.4, bold=True) + t(180, 56, 'Input path does not exist: …/dt=2026-10-01', 8, 'red', mono=True) + cap('A cleanup script deleted an old folder.', '(real error from our lab)', 'amber', y=150, h=46))
x2 = (t(180, 22, 'Plain MSCK does not fix it', 9.4, bold=True) + t(180, 56, 'MSCK REPAIR TABLE app_clicks;  → still 4 partitions', 8, 'ink', mono=True) + cap('Default MSCK only ADDs.', '', 'amber', y=150, h=34))
x3 = (t(180, 22, 'Targeted fix', 9.4, 'green', bold=True) + t(180, 56, "ALTER TABLE app_clicks DROP PARTITION (dt='2026-10-01');", 7.8, 'ink', mono=True) + cap('Or MSCK … DROP PARTITIONS.', '', 'green', y=150, h=34))
x4 = (t(180, 22, 'Careful with SYNC', 9.4, bold=True) + t(180, 56, 'SYNC also dropped dt=2026-10-04 (custom LOCATION)', 8, 'red', mono=True) + cap('Now a day of data “vanished” from Hive.', 'Re-add it with ALTER … LOCATION.', 'amber', y=150, h=46))
x5 = (t(180, 22, 'Prevent it', 9.4, 'acc', bold=True) + ''.join(t(30, 52 + k * 19, s, 8.4, anchor='start') for k, s in enumerate(['• delete data with DROP PARTITION, not rm', '• one layout for every folder', '• alert on query failures'])) + cap('Let Hive own its partitions.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'A deleted folder takes down every dashboard',
              'Files and the metastore must agree. These are the real behaviours we saw in Hive 4.2.1.',
              'Partition incident', 'A folder deleted outside Hive makes queries fail; plain MSCK does not help; DROP fixes it; SYNC also removed a custom-location partition', [x1, x2, x3, x4, x5],
              ['A folder was deleted outside Hive and queries now fail.',
               'Plain MSCK only adds partitions, so the stale entry stays.',
               'Drop the stale partition, or use MSCK with DROP PARTITIONS.',
               'SYNC removed a valid partition that lived outside the standard layout.',
               'Delete through Hive, keep one folder layout, and monitor.'],
              hid='scenario-incident')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Rows choosing folders, folders reaching the metastore</h2>
  <p>Left: real Beeline output. Right: what Hive does with each row and each folder.</p>
''' + two + '''
  <p>Three live scenarios follow: a large back-fill, daily partition registration, and a deleted-folder incident.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Dynamic partitions and MSCK at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'back-fill', 10, 'green', bold=True) + t(60, 58, 'one statement', 7.4, 'ink2'),
    '1. Back-fills and migrations',
    'When a team moves a flat table to a partitioned one, or re-partitions by a new column, a dynamic INSERT OVERWRITE does it in one statement per chunk.',
    ['Old table', '*dynamic INSERT', 'Partitioned table']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'late data', 10, 'blue', bold=True) + t(60, 58, 'right day', 7.4, 'ink2'),
    '2. Late-arriving events',
    'Mobile apps upload events days late. A dynamic insert puts each event into its own event-date partition instead of the day it arrived.',
    ['Event batch', '*PARTITION (event_date)', 'Correct days']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'MSCK', 11, 'violet', bold=True, mono=True) + t(60, 58, 'after copy', 7.4, 'ink2'),
    '3. Restores and cluster migrations',
    'After copying a warehouse folder tree to a new cluster with DistCp or restoring from backup, teams recreate the table DDL and run MSCK REPAIR to register all partitions again.',
    ['Copied folders', '*MSCK REPAIR', 'Queryable table']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'ADD PART', 10, 'acc', bold=True, mono=True) + t(60, 58, 'daily', 7.4, 'ink2'),
    '4. Ingestion from other tools',
    'Spark jobs, Kafka connectors and copy tools write date folders; the pipeline then adds the new partition to the metastore so Hive, Trino and Spark SQL can see it.',
    ['Writer job', '*ADD PARTITION', 'Visible to SQL']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'DEFAULT', 10, 'acc', bold=True, mono=True) + t(60, 58, 'data quality', 7.4, 'ink2'),
    '5. Data quality checks',
    'Teams alert when a __HIVE_DEFAULT_PARTITION__ folder appears or when a dynamic insert creates far more partitions than expected: both usually mean bad input.',
    ['Insert', '*partition count check', 'Alert']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> finish partitioning basics (<a href="../01-partitioning/">5.1</a>) and external tables (<a href="../../02-hiveql/02-managed-vs-external-tables/">2.2</a>).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
