import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
BODY = body(HERE)
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep

META = dict(
    module='02-hiveql', lesson='05-loading-data', n='2.5',
    module_label='Module 2 · Tables and data',
    title='Loading data: LOAD, INSERT, CTAS and multi-insert',
    desc='Every way to load data into Hive with real Hive 4.2.1 results: LOAD DATA LOCAL (copy) vs LOAD DATA (move), INTO vs OVERWRITE, _copy_1 files and duplicate loads, no validation on LOAD, skip.header per file, INSERT INTO/OVERWRITE SELECT, INSERT VALUES and small files, CREATE TABLE AS SELECT, multi-table insert in one scan, staging directories and idempotent loads.',
    og_desc='2,000 customers became 4,000 after a retry. Learn every way to load Hive tables, and how to make loads safe to re-run.',
    minutes=34, level='Beginner → Advanced',
    lead='There are two families of loading in Hive. <code>LOAD DATA</code> only copies or moves files into the table folder: instant, and completely trusting. <code>INSERT</code>, <code>CTAS</code> and the multi-insert run a query and write fresh files in the table’s format. This lesson loads the same file twice, loads a JSON file into a CSV table, writes three tables in one scan and shows how one-row inserts create small files. <b>All outputs are real</b>, from Hive 4.2.1.',
    chips=['Real Hive 4.2.1 outputs', 'Idempotent loads', 'Multi-insert', 'Runs in your browser (Python)'],
)

MAIN = '''# A table folder and what each load does to it
folder = {}

def load_into(name, rows):            # LOAD DATA ... INTO
    new = name
    n = 1
    while new in folder:              # same name exists -> name_copy_1, _copy_2, ...
        stem, ext = name.rsplit(".", 1)
        new = f"{stem}_copy_{n}.{ext}"; n += 1
    folder[new] = rows

def load_overwrite(name, rows):       # LOAD DATA ... OVERWRITE INTO
    folder.clear()
    folder[name] = rows

load_into("customers_day1.csv", 2000)
load_into("customers_day1.csv", 2000)          # the retried job
print(folder, "->", sum(folder.values()), "rows")
load_overwrite("customers_day2.csv", 2000)
print(folder, "->", sum(folder.values()), "rows")
'''
RUN = dict(
    heading='Run the code: simulate loads on a table folder',
    intro='<p>A dictionary plays the table folder: file name → rows. The functions copy Hive’s rules for <code>INTO</code>, <code>OVERWRITE</code> and file naming. Then you will build a multi-insert router and an idempotency check. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('while new in folder:              # same name exists -> name_copy_1, _copy_2, ...', 'Hive never overwrites a file on <code>INTO</code>; it renames the newcomer, exactly like <code>customers_day1_copy_1.csv</code> in the lab.'),
        ('folder.clear()', 'OVERWRITE deletes the existing files first. That is what makes it safe to re-run.'),
    ],
    tasks=[
        dict(label='1 · INTO vs OVERWRITE', hint='Press <b>Run</b>. Then call <code>load_into</code> a third time and predict the new file name.', code=None),
        dict(label='2 · Multi-insert router', hint='<b>Predict first:</b> how many rows go to each table? One loop over the source feeds three outputs, like <code>FROM … INSERT … INSERT</code>.',
             code='''orders = [("UPI", 220), ("COD", 150), ("UPI", 180), ("Card", 310), ("UPI", 90), ("COD", 60)]
upi, cod, mix = [], [], {}
for payment, amount in orders:          # one scan
    if payment == "UPI": upi.append(amount)
    if payment == "COD": cod.append(amount)
    mix[payment] = mix.get(payment, 0) + 1
print("upi_orders :", upi)
print("cod_orders :", cod)
print("payment_mix:", mix)
'''),
        dict(label='3 · Header skip per file', hint='skip.header.line.count = 1 removes the first line of <b>every</b> file. Add a third file and predict the total.',
             code='''files = {"customers_day2.csv": 2001, "restaurants.json": 120}   # lines per file
skip = 1
rows = sum(lines - skip for lines in files.values())
print("rows read:", rows)
'''),
        dict(label='4 · Files per INSERT', hint='Each INSERT … VALUES adds a file. How many files after inserting 10,000 events one at a time, versus in batches of 1,000?',
             code='''events = 10_000
for batch in [1, 1000]:
    files = -(-events // batch)        # ceiling division
    print(f"batch {batch:5}: {files:6} files")
'''),
        dict(label='5 · Spot the error', hint='The nightly job appends with INTO and the scheduler retries once. The duplicate check fails. Change the load to overwrite so the assertion passes.', expect='error',
             code='''table = []
def nightly(day_rows):
    table.extend(day_rows)          # INSERT INTO
day = [101, 102, 103]
nightly(day)
nightly(day)                        # retry after a timeout
assert len(table) == len(set(table)), f"{len(table) - len(set(table))} duplicate rows"
print("ok", table)
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: watch loads behind the scenes',
    intro='<p>Run these on the lab after the steps. <b>Outputs are real</b>, recorded from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · INTO adds, OVERWRITE replaces', cmd="INSERT INTO cod_orders SELECT order_id, city, amount FROM orders_ext WHERE payment='COD';\nSELECT COUNT(*) AS after_insert_into FROM cod_orders;\nINSERT OVERWRITE TABLE cod_orders SELECT order_id, city, amount FROM orders_ext WHERE payment='COD';\nSELECT COUNT(*) AS after_overwrite FROM cod_orders;\n-- run the OVERWRITE once more\nSELECT COUNT(*) AS after_overwrite_again FROM cod_orders;", file='Beeline',
             output=open(CAP + 'l25_idem.txt').read().rstrip(),
             note='The table already held 5,005 COD orders; INSERT INTO doubled them to 10,010. OVERWRITE gives 5,005 every time it runs.'),
        dict(title='2 · The staging folder', cmd='-- in the INFO log of any INSERT', file='Beeline (INFO lines)',
             output='INFO  : Loading data to table tiffingo.payment_mix from file:/opt/hive/data/warehouse/tiffingo.db/payment_mix/.hive-staging_hive_2026-10-26_10-52-00_788_1131033452752262091-3/-ext-10004\nINFO  : Loading data to table tiffingo.upi_orders from file:/opt/hive/data/warehouse/tiffingo.db/upi_orders/.hive-staging_hive_2026-10-26_10-52-00_788_1131033452752262091-3/-ext-10000\nINFO  : Loading data to table tiffingo.cod_orders from file:/opt/hive/data/warehouse/tiffingo.db/cod_orders/.hive-staging_hive_2026-10-26_10-52-00_788_1131033452752262091-3/-ext-10002',
             note='Results are written into a hidden <code>.hive-staging_…</code> folder and moved into the table only when the job succeeds. A failed INSERT leaves the table unchanged.'),
        dict(title='3 · Statistics come for free', cmd='DESCRIBE FORMATTED city_sales;', file='Beeline',
             output='| Table Type:                   | EXTERNAL_TABLE                                     | NULL |\n|                               | TRANSLATED_TO_EXTERNAL                             | TRUE |\n|                               | external.table.purge                               | TRUE |\n|                               | numRows                                            | 8    |\n| InputFormat:                  | org.apache.hadoop.hive.ql.io.orc.OrcInputFormat    | NULL |\n(lines picked from the output)',
             note='CTAS wrote ORC and recorded <code>numRows</code>: the optimiser now knows the table has 8 rows without counting. LOAD DATA does not compute such statistics.'),
    ],
)

TRACE = dict(
    heading='A multi-insert, one row at a time',
    intro='<p>Follow one scan over five orders. Each row is checked once and sent to every target it belongs to.</p>',
    code='''orders = [(1, "UPI"), (2, "COD"), (3, "UPI"), (4, "Card"), (5, "COD")]
upi, cod, counts = [], [], {}
for oid, pay in orders:
    if pay == "UPI":
        upi.append(oid)
    if pay == "COD":
        cod.append(oid)
    counts[pay] = counts.get(pay, 0) + 1
print(upi, cod, counts)
''',
    notes={3: 'Scan :: One pass over the source, like Map 1 reading orders_ext once.', 8: 'Target 3 :: The group-by target sees every row too.'},
)

WORKED_INTRO = 'Three loading tasks from TiffinGo’s pipelines: planning a retry-safe nightly load, checking a load for duplicates and lost rows, and estimating what a multi-insert saves.'
EXAMPLES = [
    dict(level='b', tag='Pipelines · SQL', title='Generate a retry-safe load statement',
         problem='<p>For each table in a nightly plan, generate the INSERT statement. Tables marked <code>rebuild</code> are fully replaced; tables marked <code>append</code> must still be safe to re-run, so they overwrite only the day being loaded (a partition).</p>',
         inp='city_sales: rebuild · daily_orders: append by order_date · run date 2026-10-25',
         approach=['Loop over the plan.', 'Rebuild → INSERT OVERWRITE TABLE.', 'Append → INSERT OVERWRITE … PARTITION for the run date, never INSERT INTO.'],
         code='''run_date = "2026-10-25"
plan = [("city_sales", "rebuild"), ("daily_orders", "append")]
for table, mode in plan:
    if mode == "rebuild":
        print(f"INSERT OVERWRITE TABLE {table} SELECT ...;")
    else:
        print(f"INSERT OVERWRITE TABLE {table} PARTITION (order_date='{run_date}') SELECT ... WHERE order_date='{run_date}';")
''', notes={6: 'Safe :: Overwriting one day makes a retry replace that day only.'},
         tryit='Write the bad version with INSERT INTO and run the job twice in your head: daily_orders would hold the 25th twice. Partitions are taught in Module 5.'),
    dict(level='i', tag='Quality · reconciliation', title='Reconcile a load: duplicates and lost rows',
         problem='<p>After loading, compare the source ids with the table ids: report duplicate ids, ids that were lost, and whether the load passed.</p>',
         inp='source ids [101..110] · table ids loaded with one retry and one dropped row',
         approach=['Count occurrences of each id in the table.', 'Duplicates: count > 1. Lost: in source but not in table.', 'Pass only when both lists are empty.'],
         code='''source = list(range(101, 111))
table = source[:6] + source[:6] + source[7:]       # retry duplicated 6 rows, id 107 lost
counts = {}
for i in table:
    counts[i] = counts.get(i, 0) + 1
dups = sorted(i for i, c in counts.items() if c > 1)
lost = sorted(set(source) - set(counts))
print("duplicates:", dups)
print("lost      :", lost)
print("PASS" if not dups and not lost else "FAIL: do not publish")
''', notes={7: 'Lost :: Rows rejected by casts or filters show up here.'},
         tryit='In Hive: SELECT order_id FROM t GROUP BY order_id HAVING COUNT(*) > 1, and a LEFT JOIN from source to target WHERE target.order_id IS NULL.'),
    dict(level='a', tag='Performance · scans', title='What does a multi-insert save?',
         problem='<p>A 1.8 TB orders table must be split into 4 tables. Separate INSERTs scan the source 4 times; a multi-insert scans it once. With a scan speed of 6 GB per second for the cluster, compare the time spent scanning.</p>',
         inp='1.8 TB source · 4 targets · 6 GB/s',
         approach=['Convert TB to GB.', 'Separate: 4 scans; multi-insert: 1 scan.', 'Divide by the scan speed and compare.'],
         code='''tb, targets, gb_per_s = 1.8, 4, 6
gb = tb * 1024
separate = targets * gb / gb_per_s
multi = gb / gb_per_s
print(f"separate INSERTs: {separate / 60:.1f} min of scanning")
print(f"multi-insert    : {multi / 60:.1f} min of scanning")
print(f"saved           : {(separate - multi) / 60:.1f} min")
''', notes={5: 'Compare :: Only the scan cost changes; writing the outputs costs the same.'},
         tryit='In the lab the multi-insert read 50,002 rows once (RECORDS_IN_Map_1) and wrote 35,020 rows into three tables. Change targets to 10 to see why big fan-outs use this form.'),
]

QUIZ = mix([
    dict(q='Beginner: What does LOAD DATA LOCAL INPATH do with the file?', options=['Parses it and converts it to ORC', 'Copies it from the HiveServer2 local disk into the table folder', 'Moves it within HDFS', 'Uploads it to the metastore'], answer=1,
         why='LOCAL copies from the local file system of the HiveServer2 host; nothing is parsed.'),
    dict(q='Beginner: Which keyword replaces existing data instead of adding to it?', options=['APPEND', 'REPLACE', 'OVERWRITE', 'TRUNCATE'], answer=2,
         why='INSERT OVERWRITE and LOAD … OVERWRITE INTO remove the old files first.'),
    dict(q='Beginner: What does CREATE TABLE t AS SELECT … do?', options=['Creates an empty table', 'Creates the table from the query’s columns and fills it with the result', 'Creates a view', 'Copies only the schema of another table'], answer=1,
         why='CTAS defines and fills the table in one statement (LIKE copies only the schema).'),
    dict(q='Intermediate: The same file was loaded twice with LOAD DATA … INTO. What happened in the lab?', options=['An error: file exists', 'The second load was ignored', 'Both files were kept (the second renamed _copy_1), doubling the rows', 'The first file was replaced'], answer=2,
         why='2,000 became 4,000 rows; Hive renamed the newcomer customers_day1_copy_1.csv.'),
    dict(q='Intermediate: What did LOAD DATA (without LOCAL) do to the source file in the lab?', options=['Copied it', 'Moved it into the table folder', 'Deleted it without loading', 'Compressed it'], answer=1,
         why='Without LOCAL the file is moved within the table’s file system; it disappeared from incoming/.'),
    dict(q='Intermediate: Why was the row count 2,119 instead of 2,120 after loading a 120-line JSON file into the CSV table?', options=['JSON rows are merged', 'skip.header.line.count removed the first line of the JSON file too', 'One JSON line was invalid', 'Hive deduplicates rows'], answer=1,
         why='The header rule applies to every file in the table folder.'),
    dict(q='Advanced: What is the main benefit of FROM src INSERT … INSERT …?', options=['It makes outputs ACID', 'The source is scanned once for several targets', 'It skips the staging folder', 'It avoids writing files'], answer=1,
         why='One Map vertex read 50,002 rows once and fed three tables.'),
    dict(q='Advanced: Which load is safe to re-run after a failure without creating duplicates?', options=['INSERT INTO t SELECT …', 'LOAD DATA LOCAL INPATH … INTO TABLE t', 'INSERT OVERWRITE TABLE t SELECT …', 'INSERT INTO t VALUES …'], answer=2,
         why='OVERWRITE produces the same final data no matter how many times it runs.'),
])

REVISION = [
    '<code>LOAD DATA LOCAL INPATH</code> = <b>copy</b> from HiveServer2’s disk; <code>LOAD DATA INPATH</code> = <b>move</b> within the cluster FS. No parsing, no validation.',
    '<code>INTO</code> adds files (same name → <code>_copy_1</code>); <code>OVERWRITE</code> deletes old files first.',
    '<code>skip.header.line.count</code> applies to <b>every file</b> in the table folder.',
    '<code>INSERT INTO|OVERWRITE TABLE t SELECT …</code> runs a job and writes files in t’s format (text → ORC).',
    '<code>INSERT INTO t [(cols)] VALUES …</code>: one new file per statement → small-files risk.',
    '<code>CREATE TABLE t STORED AS ORC AS SELECT …</code> (CTAS): schema from the query; stats recorded.',
    '<code>FROM s INSERT … INSERT …</code>: one scan, many targets.',
    'Retry-safe = OVERWRITE (table or partition) or MERGE. Check counts vs distinct keys after loads. Writes go via <code>.hive-staging</code>, then move in.',
]
FAQ = [
    ('Does LOAD DATA convert my CSV into ORC if the table is ORC?', 'No. LOAD only moves or copies files; the table would then contain CSV files that the ORC reader cannot read, and queries fail or return garbage. To convert, create a text table over the CSV (or load into one) and run INSERT … SELECT into the ORC table.'),
    ('Is LOAD DATA LOCAL “local” to my laptop?', 'It is local to the HiveServer2 host (the machine or container running HiveServer2), not to the computer where Beeline runs. In our lab both happen inside the hiveserver2 container. On a cluster you normally put files into HDFS or object storage first (with hdfs dfs -put or a transfer tool) and then use LOAD DATA INPATH or simply point an external table at the folder.'),
    ('Why did INSERT … VALUES take seconds for two rows?', 'Each INSERT is a full query: it is compiled, a Tez job runs, files are written to a staging folder and moved into place. That overhead is the same for 2 rows or 2 million rows. Hive is built for large batch writes; for frequent small writes use batching or a system designed for it.'),
    ('What is the difference between CTAS and CREATE TABLE LIKE?', 'CREATE TABLE … LIKE copies another table’s definition and creates an empty table. CTAS creates a table from a query’s result columns and fills it with the rows. CTAS fails if the table already exists; to refresh an existing table use INSERT OVERWRITE instead.'),
    ('How do I stop small files from piling up?', 'Write in batches, prefer INSERT OVERWRITE of whole partitions, enable Hive’s merge settings so jobs combine small output files, and periodically rewrite (compact) tables that collected many files. ACID and Iceberg tables have compaction built in. Module 5 covers this in detail.'),
]

PRACTICE_INTRO = 'Programs on load rules: file naming, overwrite vs append, header skipping, reconciliation and cost.'
PROBLEMS = [
    dict(level='easy', title='Next copy name', stmt='The folder already has orders.csv and orders_copy_1.csv. What name will the next LOAD … INTO of orders.csv get?', inp='orders.csv, orders_copy_1.csv',
         code='''existing = {"orders.csv", "orders_copy_1.csv"}
n, name = 1, "orders.csv"
while name in existing:
    name = f"orders_copy_{n}.csv"; n += 1
print(name)
''', explain='orders_copy_2.csv. Seeing _copy_ files in a table folder is a strong sign of repeated loads.'),
    dict(level='easy', title='INTO vs OVERWRITE counts', stmt='A table has 5,005 rows. What is the count after INSERT INTO of 5,005 rows, and after INSERT OVERWRITE of 5,005 rows?', inp='5,005 + 5,005',
         code='''rows = 5005
print("INTO     :", rows + 5005)
print("OVERWRITE:", 5005)
''', explain='10,010 and 5,005: the exact numbers we saw for cod_orders.'),
    dict(level='easy', title='Header lines lost', stmt='A table with skip.header.line.count = 1 has 12 files, each with a header. The files hold 120,012 lines in total. How many rows are read?', inp='12 files · 120,012 lines',
         code='''print(120_012 - 12 * 1)
''', explain='120,000. If some files had no header, real rows would be lost silently: keep all files in one consistent layout.'),
    dict(level='medium', title='Route rows to targets', stmt='Split orders into three lists in one pass: amount ≥ 300 (big), city Pune (pune) and everything (all_count).', inp='[(1,"Pune",320),(2,"Thane",150),(3,"Pune",90),(4,"Mumbai",410)]',
         code='''orders = [(1, "Pune", 320), (2, "Thane", 150), (3, "Pune", 90), (4, "Mumbai", 410)]
big, pune, total = [], [], 0
for oid, city, amt in orders:
    if amt >= 300: big.append(oid)
    if city == "Pune": pune.append(oid)
    total += 1
print(big, pune, total)
''', explain='[1, 4] [1, 3] 4. A row can go to several targets in a multi-insert, as order 1 does.'),
    dict(level='medium', title='Find duplicate ids', stmt='Print ids that appear more than once after a load.', inp='[7, 8, 9, 8, 10, 7]',
         code='''ids = [7, 8, 9, 8, 10, 7]
seen, dups = set(), set()
for i in ids:
    (dups if i in seen else seen).add(i)
print(sorted(dups))
''', explain='[7, 8]. In Hive: GROUP BY id HAVING COUNT(*) > 1.'),
    dict(level='medium', title='Rows rejected by casts', stmt='A raw table has 50,002 rows; the curated INSERT keeps rows where id, amount and timestamp are not NULL; 50,000 rows arrive. What share was rejected?', inp='50,002 → 50,000',
         code='''raw, cur = 50_002, 50_000
print(f"rejected {raw - cur} rows ({(raw - cur) / raw:.4%})")
''', explain='2 rows (0.0040%), exactly orders 150001 and 150002 from our dataset.'),
    dict(level='business', title='Cost of a duplicated day', stmt='A retry duplicated one day of 48,000 orders worth an average Rs 290. By how much was reported revenue inflated?', inp='48,000 × Rs 290',
         code='''orders, avg = 48_000, 290
print(f"inflated by Rs {orders * avg:,}")
''', explain='Rs 1,39,20,000 (13.92 million). One INSERT INTO in a retried job can misreport a crore of revenue.'),
    dict(level='business', title='Small files after a year', stmt='A job inserts once per minute, creating one file each time. How many files after a year, and after switching to hourly batches?', inp='per minute vs per hour, 365 days',
         code='''print("per minute:", 60 * 24 * 365)
print("per hour  :", 24 * 365)
''', explain='525,600 files versus 8,760. Batching is a 60× reduction before any compaction.'),
]

SCN_INTRO = 'Loading questions test practical pipeline experience. Expect to explain LOAD vs INSERT and how you avoid duplicates.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“How do you load a CSV into Hive?”',
        'The interviewer asks for the steps to get a CSV from your laptop into a Hive ORC table.',
        'do you know LOAD vs INSERT and formats?',
        '''<ol>
          <li>Copy the file to HDFS (<code>hdfs dfs -put</code>) or object storage.</li>
          <li>Create a text table (external, with the right delimiter and header skip) over that folder, or LOAD the file into one.</li>
          <li>Create the ORC table and run <code>INSERT OVERWRITE TABLE orc_t SELECT … FROM text_t</code> to convert and type the data.</li>
        </ol>''', '“LOAD DATA straight into the ORC table”: LOAD does not convert formats.') +
    scn('Data engineering · reliability', 'Mid-level', 'Numbers doubled after a retry',
        'A dashboard shows double sales for one day. The scheduler log shows the nightly Hive task ran twice.',
        'do you understand idempotent loads?',
        '''<ul>
          <li>The task used INSERT INTO (or LOAD … INTO), so the retry appended the same day again.</li>
          <li>Fix the data: re-run that day with INSERT OVERWRITE of its partition.</li>
          <li>Fix the job: overwrite exactly the slice it loads, or MERGE on keys; add a post-load duplicate check.</li>
        </ul>''', 'disabling retries; failures will still happen, so loads must be re-runnable.') +
    scn('Platform · performance', 'Mid-level', 'One source, many tables',
        'A job runs five INSERT … SELECT statements over the same 2 TB table to build five region tables. It takes three hours.',
        'do you know multi-insert?',
        '''<ul>
          <li>Rewrite as <code>FROM big_table INSERT OVERWRITE TABLE r1 SELECT … WHERE … INSERT OVERWRITE TABLE r2 …</code>.</li>
          <li>The source is read once instead of five times; output writing cost stays the same.</li>
          <li>Also consider one partitioned table by region instead of five tables (Module 5).</li>
        </ul>''', 'adding more nodes before removing the four extra scans.') +
    scn('Operations · small files', 'Mid-level', 'Queries slowed down over months',
        'An events table that started fast now takes minutes. The table folder has 300,000 files of a few KB each.',
        'can you connect loading style to the small-files problem?',
        '''<ol>
          <li>Each INSERT (especially frequent INSERT … VALUES or tiny batches) created new files.</li>
          <li>Compact: rewrite partitions with INSERT OVERWRITE … SELECT and merge settings, or run compaction for ACID/Iceberg tables.</li>
          <li>Prevent: batch writes, target files of hundreds of MB, monitor file counts per partition.</li>
        </ol>''', 'blaming the cluster size.')
)
