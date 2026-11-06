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
    module='05-partitioning-and-bucketing', lesson='01-partitioning', n='5.1',
    module_label='Module 5 · Partitioning and bucketing',
    title='Partitioning: make Hive read only the folders you need',
    desc='Hive partitioning explained with real Hive 4.2.1 results: PARTITIONED BY, static partitions with INSERT and LOAD DATA, the col=value folder layout, SHOW PARTITIONS, EXPLAIN DEPENDENCY, partition pruning proved with Tez counters (1,621 rows read instead of 50,000), multi-level partitions, ADD/RENAME/DROP PARTITION, the strict partition filter check, and two traps: filtering on the wrong column and loading data into the wrong partition.',
    og_desc='A one-day query read 50,000 rows. After partitioning it read 1,621. Hive partitioning with real counters and the traps that silently undo it.',
    minutes=35, level='Beginner → Advanced',
    lead='Partitioning is the single most important performance idea in Hive: store each day in its own folder, and a one-day query opens one folder. In this lesson Kabir builds <code>orders_by_day</code>, proves with Hive’s own counters that a one-day query now reads <b>1,621 rows instead of 50,000</b>, and finds two traps that undo partitioning without any error. <b>All outputs are real</b>, from Hive 4.2.1.',
    chips=['Real Hive 4.2.1 outputs', 'Pruning proved with counters', 'Static partitions', 'Runs in your browser (Python)'],
)

MAIN = '''# A partitioned table is a dict of folders: {partition value: rows}
orders = [(100001, "2026-10-01", "Pune", 530), (100002, "2026-10-01", "Thane", 500),
          (100003, "2026-10-02", "Pune", 410), (100004, "2026-10-05", "Pune", 180),
          (100005, "2026-10-05", "Mumbai", 480), (100006, "2026-10-07", "Pune", 460)]

folders = {}
for oid, day, city, amt in orders:                 # INSERT ... PARTITION (order_date)
    folders.setdefault(f"order_date={day}", []).append((oid, city, amt))

wanted = "order_date=2026-10-05"                    # WHERE order_date = '2026-10-05'
read = folders.get(wanted, [])                      # pruning: open one folder only
print(sorted(folders))
print("rows read:", len(read), "of", len(orders))
print("Pune revenue:", sum(a for _, c, a in read if c == "Pune"))
'''
RUN = dict(
    heading='Run the code: folders and pruning',
    intro='<p>A partitioned table behaves like a dictionary of folders keyed by the partition value. These programs show what pruning saves. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    folders.setdefault(f"order_date={day}", []).append((oid, city, amt))', 'The day becomes part of the folder name; the rows inside no longer need to store it.'),
        ('read = folders.get(wanted, [])                      # pruning: open one folder only', 'The planner picks the folder by name, without opening the others.'),
    ],
    tasks=[
        dict(label='1 · Folders and pruning', hint='Press <b>Run</b>. Only 2 of 6 rows are read, like 1,621 of 50,000 in the real lab.', code=None),
        dict(label='2 · Predict first: a date range', hint='<b>Predict first:</b> how many folders does 10-05 to 10-07 open? (Real EXPLAIN DEPENDENCY for the lab: 3.)',
             code='''days = [f"2026-10-{d:02d}" for d in range(1, 31)]
lo, hi = "2026-10-05", "2026-10-07"
picked = [d for d in days if lo <= d <= hi]
print(len(picked), picked)
'''),
        dict(label='3 · The wrong column', hint='Filtering on order_ts cannot use folder names, so every folder is opened. Real lab: 30 of 30.',
             code='''folders = {f"2026-10-{d:02d}": [f"2026-10-{d:02d} 12:00"] for d in range(1, 31)}
opened = 0
hits = 0
for name, rows in folders.items():           # no folder can be skipped
    opened += 1
    hits += sum(1 for ts in rows if ts.startswith("2026-10-05"))
print("folders opened:", opened, "matching rows:", hits)
'''),
        dict(label='4 · Savings over a year', hint='Change <code>rows_per_day</code> to 1_00_000 (one lakh). The fraction read stays 1/365.',
             code='''rows_per_day = 1621
days = 365
full = rows_per_day * days
print("flat table reads   ", full)
print("partitioned reads  ", rows_per_day)
print("times less work    ", full // rows_per_day)
'''),
        dict(label='5 · Spot the error', hint='Yesterday’s file was loaded into today’s partition too. Add a check that rejects a file whose dates do not match the partition value.', expect='error',
             code='''def load(part, rows):
    return {part: rows}            # Hive trusts the value; nothing is checked
file_rows = ["2026-10-03 10:01", "2026-10-03 12:40"]
p = load("2026-10-04", file_rows)
bad = [r for r in file_rows if not r.startswith("2026-10-04")]
assert not bad, f"{len(bad)} rows do not belong to 2026-10-04"
print(p)
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: inspect a partition and split one day by city',
    intro='<p>Three more statements to try in Beeline on the TiffinGo data. <b>Outputs are real</b>, from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · Statistics of one partition', cmd="DESCRIBE FORMATTED orders_by_day PARTITION (order_date='2026-10-05');\n-- selected lines", file='Beeline',
             output='| Partition Value:   | [2026-10-05]                                                   |\n| Location:          | file:/opt/hive/data/warehouse/tiffingo.db/orders_by_day/order_date=2026-10-05 |\n|                    | numFiles       | 1       |\n|                    | numRows        | 1621    |\n|                    | rawDataSize    | 695409  |\n|                    | totalSize      | 13269   |',
             note='Every partition has its own folder and its own statistics. ORC stored 1,621 rows in 13 KB on disk. The optimiser uses numRows when planning joins (Module 8).'),
        dict(title='2 · Static day, dynamic city', cmd="CREATE TABLE orders_day_city (order_id INT, customer_id INT, amount DECIMAL(10,2),\n  payment STRING, status STRING)\nPARTITIONED BY (order_date DATE, city STRING) STORED AS ORC;\n\nINSERT OVERWRITE TABLE orders_day_city PARTITION (order_date='2026-10-05', city)\nSELECT order_id, customer_id, amount, payment, status, city\nFROM orders WHERE order_date = '2026-10-05';\nSHOW PARTITIONS orders_day_city;", file='Beeline',
             output=capf('l51_multi.txt'),
             note='The date is fixed (static) and the city comes from the last SELECT column (dynamic). One statement created eight folders. A static level must come <b>before</b> any dynamic level.'),
        dict(title='3 · A safe partition filter check', cmd="SET hive.strict.checks.no.partition.filter=true;\nSELECT COUNT(*) AS n FROM orders_by_day WHERE order_date = '2026-10-05';", file='Beeline',
             output=capf('l51_strict_ok.txt'),
             note='With the safety check on, queries that filter on the partition column run normally; only unfiltered ones fail with Error 10056.'),
    ],
)

TRACE = dict(
    heading='Pruning, one partition at a time',
    intro='<p>The planner walks the list of partitions from the metastore and keeps those that match the filter. Watch <code>keep</code> grow.</p>',
    code='''partitions = ["2026-10-04", "2026-10-05", "2026-10-06", "2026-10-07", "2026-10-08"]
lo, hi = "2026-10-05", "2026-10-07"
keep = []
for p in partitions:
    if lo <= p <= hi:
        keep.append(p)
print(len(keep), "of", len(partitions), keep)
''',
    notes={1: 'Metastore :: Partition values come from metadata. No data file has been opened yet.', 5: 'Filter :: The WHERE condition is tested against the folder value, not against rows.', 7: 'Result :: Three partitions, the same as the real EXPLAIN DEPENDENCY output.'},
)

WORKED_INTRO = 'Three partition tasks from TiffinGo’s data team.'
EXAMPLES = [
    dict(level='b', tag='Reporting · pruning', title='Yesterday’s revenue per city',
         problem='<p>Every morning the job runs <code>SELECT city, SUM(amount) FROM orders_by_day WHERE order_date = date_sub(current_date, 1) GROUP BY city</code>. Simulate the folder read and the per-city sum.</p>',
         inp='folders for 10-25, 10-26, 10-27; today is 2026-10-27  (sample rows)',
         approach=['Work out yesterday’s date.', 'Open only that folder.', 'Sum the amounts per city.'],
         code='''from datetime import date, timedelta
folders = {"2026-10-25": [("Pune", 410)], "2026-10-26": [("Pune", 530), ("Thane", 320), ("Pune", 180)],
           "2026-10-27": [("Thane", 90)]}
yesterday = (date(2026, 10, 27) - timedelta(days=1)).isoformat()
totals = {}
for city, amt in folders[yesterday]:
    totals[city] = totals.get(city, 0) + amt
print(yesterday, totals)
''', notes={4: 'Partition value :: In Hive, date_sub(current_date, 1) on the partition column was pruned correctly in our lab.'},
         tryit='Change the filter to the last 3 days. In Hive: <code>order_date &gt;= date_sub(current_date, 3)</code>, which read 7 partitions in our lab because the data ends on 30 October.'),
    dict(level='i', tag='Data engineering · re-runs', title='Why INSERT OVERWRITE for daily loads',
         problem='<p>A nightly job loads one day. Tonight it crashes after writing and is re-run. Compare <code>INSERT INTO … PARTITION</code> with <code>INSERT OVERWRITE … PARTITION</code>.</p>',
         inp='1,641 rows for 2026-10-01 (real count), loaded twice',
         approach=['INTO appends to the folder.', 'OVERWRITE replaces the folder contents.', 'Count rows after two runs.'],
         code='''def run(table, part, rows, mode):
    if mode == "OVERWRITE":
        table[part] = list(rows)
    else:
        table.setdefault(part, []).extend(rows)

rows = list(range(1641))
for mode in ["INTO", "OVERWRITE"]:
    t = {}
    run(t, "2026-10-01", rows, mode)
    run(t, "2026-10-01", rows, mode)        # the re-run
    print(mode, len(t["2026-10-01"]))
''', notes={3: 'OVERWRITE :: Replaces only this partition. Other days stay as they are.'},
         tryit='INTO gives 3,282 rows, OVERWRITE gives 1,641. That is why production loads use OVERWRITE on one partition: they are idempotent (safe to repeat).'),
    dict(level='a', tag='Cost · capacity planning', title='How much does pruning save over a year?',
         problem='<p>Orders grow 10% a month from 1,621 a day. A daily report reads one day. Compare the rows read per report on a flat table and on a table partitioned by day, after 12 months.</p>',
         inp='1,621 orders/day in month 1, +10% each month, 30 days per month',
         approach=['Build daily volumes month by month.', 'Flat table: the report reads the whole history.', 'Partitioned: it reads the last day only.'],
         code='''daily = 1621
history = 0
for month in range(1, 13):
    history += daily * 30
    last_day = daily
    daily = round(daily * 1.10)
print("flat reads       ", history)
print("partitioned reads", last_day)
print("ratio            ", round(history / last_day))
''', notes={4: 'History :: A flat table keeps growing, so the same report gets slower every month.'},
         tryit='The ratio is about 225 after one year and keeps rising. With partitions the daily report costs roughly the same in month 12 as in month 1.'),
]

QUIZ = mix([
    dict(q='Beginner: Where is the value of a partition column stored?', options=['In every row of the data file', 'In the folder name and the metastore', 'In a separate index file', 'In the table comment'], answer=1,
         why='Partition columns are virtual: the data files hold only the other columns.'),
    dict(q='Beginner: What does partition pruning mean?', options=['Deleting old partitions', 'Skipping partitions the WHERE clause rules out', 'Merging small files', 'Sorting rows inside a partition'], answer=1,
         why='Hive reads only the folders that can match the filter. Real lab: 1 of 30 folders, 1,621 of 50,000 rows.'),
    dict(q='Beginner: Which command lists the partitions of a table?', options=['DESCRIBE PARTITIONS t', 'SHOW PARTITIONS t', 'LIST PARTITIONS t', 'SELECT * FROM PARTITIONS'], answer=1,
         why='SHOW PARTITIONS t, optionally with PARTITION (col=\'v\') to filter.'),
    dict(q='Intermediate: orders_by_day is partitioned by order_date. Which filter reads all 30 partitions?', options=["order_date = '2026-10-05'", "date_format(order_date,'EEE') = 'Sat'", "to_date(order_ts) = '2026-10-05'", "order_date BETWEEN '2026-10-05' AND '2026-10-07'"], answer=2,
         why='order_ts is an ordinary column. Functions on the partition column itself were still pruned in Hive 4.2.1.'),
    dict(q='Intermediate: In a static INSERT … PARTITION (order_date=\'2026-10-01\') SELECT …, which columns should the SELECT return?', options=['All columns including order_date', 'Only the non-partition columns', 'Only order_date', 'Any columns; Hive matches by name'], answer=1,
         why='The PARTITION clause supplies the value, so the SELECT returns the data columns only, in order.'),
    dict(q='Intermediate: You LOAD 3 October’s file INTO PARTITION (dt=\'2026-10-04\'). What does Hive do?', options=['Rejects it: dates do not match', 'Loads it into dt=2026-10-04 without checking', 'Moves rows to the right partition', 'Loads only matching rows'], answer=1,
         why='Real lab: 1,668 orders appeared under both days. Static values are trusted.'),
    dict(q='Advanced: What does SET hive.strict.checks.no.partition.filter=true do?', options=['Speeds up pruning', 'Rejects queries on partitioned tables without a partition filter', 'Forces dynamic partitions', 'Drops empty partitions'], answer=1,
         why='Error 10056 in our lab. Default in 4.2.1: false.'),
    dict(q='Advanced: Which is the best partition column for a 5-year orders table queried by day and by city?', options=['order_id', 'customer_id', 'order_date', 'amount'], answer=2,
         why='Moderate number of values and used in almost every filter. City can be a second level only if partitions stay large (Lesson 5.4).'),
])

REVISION = [
    '<code>PARTITIONED BY (order_date DATE)</code>: the column is <b>not</b> in the column list; each value is a folder <code>order_date=…/</code> + a metastore row.',
    '<b>Pruning:</b> filter on the partition column → Hive opens only matching folders (real: 1 of 30, 1,621 of 50,000 rows).',
    'Check it with <code>EXPLAIN DEPENDENCY</code> (input_partitions) or Tez counters (<code>RECORDS_IN_Map_1</code>).',
    '<b>No pruning</b> on other columns (<code>to_date(order_ts)</code> → 30 of 30) or with <code>OR</code> on a non-partition column. Functions on the partition column were pruned in 4.2.1.',
    '<b>Static:</b> <code>INSERT … PARTITION (col=\'v\') SELECT data cols</code> or <code>LOAD DATA … PARTITION (…)</code>. The value is trusted, never checked.',
    '<b>Manage:</b> SHOW PARTITIONS · ADD [IF NOT EXISTS] · RENAME TO PARTITION · DROP [IF EXISTS] (ranges allowed) · DESCRIBE FORMATTED … PARTITION.',
    '<b>Daily loads:</b> INSERT OVERWRITE one partition → safe to re-run.',
    '<b>Safety:</b> <code>hive.strict.checks.no.partition.filter=true</code> → Error 10056 for unfiltered queries.',
    'Good partition column: low-to-moderate cardinality, used in most filters (date). Bad: ids.',
]
FAQ = [
    ('Is partitioning the same as indexing?', 'No. An index points to rows inside files; a partition is a separate folder. Hive removed its old index feature in Hive 3.0. Partitioning, bucketing (Lesson 5.3) and the min/max statistics inside ORC and Parquet files are the ways Hive avoids reading data today.'),
    ('Can I change the partition column of an existing table?', 'Not in place. Create a new table with the new PARTITIONED BY, copy the data with a dynamic INSERT OVERWRITE … SELECT (Lesson 5.2), check the counts, then swap the names. Plan the partition column before the table grows.'),
    ('Why is the partition column typed DATE and not STRING?', 'Either works; the folder name is text in both cases. DATE stops values like “2026-13-45” and lets you compare and use date functions naturally. Many older tables use STRING (dt=\'20261005\'), so check the type before writing filters: comparing a STRING partition with a DATE value can force a cast.'),
    ('Does a partitioned table make every query faster?', 'Only queries that filter on the partition column. A query over the whole table reads everything anyway, and with many small partitions it can even be slower, because Hive must list and open more folders and files. That is why the choice of column matters (Lesson 5.4).'),
    ('What happens to the partition folder when I drop a partition?', 'For a managed table the folder and files are deleted. For an external table only the metastore entry is removed and the files stay, unless the table has <code>external.table.purge=true</code>, which Hive 4 sets on tables created with a plain CREATE TABLE (see Lesson 2.2).'),
]

PRACTICE_INTRO = 'Programs that simulate partitions and pruning, with the HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Build the folder names', stmt='Turn three partition values into Hive folder names.', inp="col = 'order_date', values 10-01, 10-02, 10-03",
         code='''col = "order_date"
for v in ["2026-10-01", "2026-10-02", "2026-10-03"]:
    print(f"{col}={v}/")
''', explain='Hive names each partition folder <code>col=value</code>. Two levels give <code>order_date=…/city=…/</code>.'),
    dict(level='easy', title='How many partitions?', stmt='A table is partitioned by date and city. How many partitions does one month create?', inp='30 days, 8 cities',
         code='''days, cities = 30, 8
print(days * cities)
''', explain='240 folders a month, 2,880 a year: each level multiplies the count. The real lab created 8 for one day.'),
    dict(level='easy', title='Fraction read', stmt='What share of rows does a one-day query read on the real table?', inp='1,621 of 50,000',
         code='''print(f"{100 * 1621 / 50000:.1f}%")
''', explain='3.2% of the rows: about 31 times less work than the flat table.'),
    dict(level='medium', title='Which partitions match?', stmt='Return the partitions that match <code>order_date &gt;= \'2026-10-28\'</code>.', inp='partitions 10-01 … 10-30',
         code='''parts = [f"2026-10-{d:02d}" for d in range(1, 31)]
print([p for p in parts if p >= "2026-10-28"])
''', explain='Three partitions. ISO dates (yyyy-MM-dd) sort correctly as text, which is one reason to use that format.'),
    dict(level='medium', title='Static insert column list', stmt='Given the table columns and the partition column, print the SELECT list for a static insert.', inp='orders_by_day',
         code='''table_cols = ["order_id", "customer_id", "city", "order_ts", "amount", "payment", "status"]
part_col = "order_date"
print("SELECT " + ", ".join(table_cols) + " FROM orders WHERE " + part_col + " = '2026-10-01'")
''', explain='The partition column is given in PARTITION (…), so it is not in the SELECT list. In a dynamic insert it would be added as the last column.'),
    dict(level='medium', title='Validate a daily file', stmt='Reject a load when any row’s date differs from the partition value.', inp="partition 2026-10-04, rows from 10-03",
         code='''part = "2026-10-04"
rows = ["2026-10-03 10:01", "2026-10-03 12:40", "2026-10-04 00:10"]
bad = [r for r in rows if r[:10] != part]
print("REJECT" if bad else "OK", len(bad), "bad rows")
''', explain="In HiveQL after loading to a staging table: <code>SELECT COUNT(*) FROM stage WHERE to_date(order_ts) &lt;&gt; '2026-10-04'</code>; stop the job if it is not 0."),
    dict(level='business', title='Retention: what to drop', stmt='Keep 90 days. On 2026-10-27, which month-start partitions are older than the cut-off?', inp='partitions on the 1st of each month in 2026',
         code='''from datetime import date, timedelta
cutoff = date(2026, 10, 27) - timedelta(days=90)
parts = [date(2026, m, 1) for m in range(1, 11)]
print("cutoff", cutoff)
print("drop", [p.isoformat() for p in parts if p < cutoff])
''', explain="<code>ALTER TABLE t DROP IF EXISTS PARTITION (order_date &lt; '2026-07-29')</code> removes them in one metadata operation."),
    dict(level='business', title='Monthly cost of a missing filter', stmt='A dashboard refreshes every 15 minutes without a date filter. How many rows does it read per day compared with a one-day filter, for a year of history?', inp='1,621 rows/day, 365 days',
         code='''refreshes = 24 * 4
full = 1621 * 365 * refreshes
filtered = 1621 * refreshes
print(full, filtered, full // filtered)
''', explain='365 times more data read every day. Turning on <code>hive.strict.checks.no.partition.filter</code> catches this before it reaches production.'),
]

SCN_INTRO = 'Partitioning is asked in almost every Hive and data engineering interview. Expect “why”, “which column” and “why is my query still slow”.'
SCENARIOS = (
    scn('Any company · Hive', 'Fresher', '“What is partitioning in Hive?”',
        'Explain partitioning and give an example.',
        'do you know what changes on disk and in the metastore?',
        '<p>Partitioning splits a table into sub-folders by a column’s value, like <code>order_date=2026-10-05/</code>. Each partition is registered in the metastore. Queries that filter on that column read only the matching folders (partition pruning). Partition columns are not stored inside the files. Example: a daily orders table, where yesterday’s report reads one folder.</p>', 'Saying partitions are “like indexes” or that they are separate tables.') +
    scn('Analytics', 'Mid-level', '“The table is partitioned, but my query is slow”',
        'A query on a date-partitioned table takes as long as on the flat table.',
        'can you verify pruning?',
        '''<ol>
          <li>Run <code>EXPLAIN DEPENDENCY</code> and count <code>input_partitions</code>.</li>
          <li>Check the WHERE clause: is it on the partition column, or on a timestamp column that holds the same date? Is it OR-ed with another condition?</li>
          <li>Rewrite the filter on the partition column and compare <code>RECORDS_IN_Map_1</code>.</li>
        </ol>''', '“Add more memory”, before checking what the query reads.') +
    scn('Data engineering', 'Mid-level', 'Duplicate orders in one day',
        'Finance finds the same orders on two days in a partitioned table loaded by LOAD DATA.',
        'do you know that static partition values are not validated?',
        '''<ul>
          <li>Confirm with a self-join on order_id across the two partitions.</li>
          <li>Drop or overwrite the wrong partition.</li>
          <li>Prevent it: load into staging, check that the dates match the target partition, then INSERT OVERWRITE that partition.</li>
        </ul>''', 'Running DISTINCT in every report instead of fixing the load.') +
    scn('Platform', 'Senior', 'Choosing the partition scheme',
        'A new events table will get 200 million rows a day from 40 countries; most queries filter by date, some by country.',
        'can you balance pruning against the number of partitions?',
        '''<ul>
          <li>Partition by event date first: every query uses it.</li>
          <li>Add country as a second level only if each day-country folder stays large; otherwise keep country as a normal column and let ORC/Parquet statistics or bucketing help.</li>
          <li>Estimate partitions per year (365 × 40 = 14,600) and file sizes before deciding, and enable the strict partition filter.</li>
        </ul>''', 'Partitioning by user_id or by hour without estimating folder counts.')
)
