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
    module='05-partitioning-and-bucketing', lesson='02-dynamic-partitions-and-msck', n='5.2',
    module_label='Module 5 · Partitioning and bucketing',
    title='Dynamic partitions and MSCK REPAIR TABLE',
    desc='Hive dynamic partitions and MSCK explained with real Hive 4.2.1 results: one INSERT that creates 30 partitions, nonstrict vs strict mode (the 4.2.1 default is nonstrict), mixed static and dynamic partitions, max partition limits (errors 20004 and the per-statement check), __HIVE_DEFAULT_PARTITION__ for NULLs, the wrong-column-order trap, MSCK REPAIR TABLE with ADD, DROP and SYNC PARTITIONS, hive.msck.path.validation, and ALTER TABLE ADD PARTITION with LOCATION.',
    og_desc='One INSERT, 30 partitions, and three traps we hit in a real Hive 4.2.1 lab: wrong column order, NULL partitions and a deleted folder. Plus what MSCK can and cannot repair.',
    minutes=35, level='Beginner → Advanced',
    lead='Static partitions need one statement per value. <b>Dynamic partitions</b> let Hive read the value from the data and create the folders itself, so a month is one statement. The reverse problem, folders written by other tools that Hive does not know about, is solved with <b>MSCK REPAIR TABLE</b>. Both are powerful and both have sharp edges; we hit five of them in the lab. <b>All outputs are real</b>, from Hive 4.2.1.',
    chips=['Real Hive 4.2.1 outputs', 'One INSERT, 30 partitions', 'MSCK ADD / DROP / SYNC', 'Runs in your browser (Python)'],
)

MAIN = '''# A dynamic partition insert: the LAST column of each row picks the folder
rows = [(100004, 180, "2026-10-03"), (100001, 530, "2026-10-17"),
        (100002, 500, "2026-10-20"), (100013, 340, "2026-10-03")]

table = {}
for *data, part in rows:                       # SELECT ..., order_date  (last!)
    folder = f"order_date={part}"
    if folder not in table:
        print("creating", folder)
    table.setdefault(folder, []).append(tuple(data))

print(len(table), "partitions")
for f, r in sorted(table.items()):
    print(f, r)
'''
RUN = dict(
    heading='Run the code: rows choosing their own folders',
    intro='<p>These programs mimic how Hive routes rows in a dynamic partition insert and how MSCK compares folders with the metastore. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('for *data, part in rows:                       # SELECT ..., order_date  (last!)', 'Hive does not look at column names here: the trailing column is the partition value.'),
        ('        print("creating", folder)', 'A new value creates a new partition folder on the fly.'),
    ],
    tasks=[
        dict(label='1 · Dynamic routing', hint='Press <b>Run</b>. Two orders share 10-03, so 4 rows make 3 partitions.', code=None),
        dict(label='2 · Predict first: wrong column last', hint='<b>Predict first:</b> how many partitions if amount is last? (Real lab: 69 bogus partitions for one day.)',
             code='''rows = [(100004, "UPI", 180), (100001, "UPI", 530), (100002, "Card", 500), (100013, "UPI", 340)]
table = {}
for oid, payment, amount in rows:            # SELECT order_id, payment, amount
    table.setdefault(f"payment={amount:.2f}", []).append((oid, payment))
print(len(table), sorted(table))
'''),
        dict(label='3 · NULL goes to the default partition', hint='Real lab: 10 of 40 customers ended in __HIVE_DEFAULT_PARTITION__.',
             code='''cities = ["Mumbai", None, "Pune", None, "Thane"]
DEFAULT = "__HIVE_DEFAULT_PARTITION__"
for c in cities:
    print("ref_city=" + (c if c is not None else DEFAULT))
'''),
        dict(label='4 · MSCK: compare folders with the metastore', hint='Change <code>mode</code> to "DROP" or "SYNC" and run again.',
             code='''folders = {"dt=2026-10-02", "dt=2026-10-03", "dt=2026-10-05"}       # on storage
metastore = {"dt=2026-10-01", "dt=2026-10-02", "dt=2026-10-03"}     # registered
mode = "ADD"
if mode in ("ADD", "SYNC"):
    metastore |= folders - metastore
if mode in ("DROP", "SYNC"):
    metastore -= metastore - folders
print(mode, sorted(metastore))
'''),
        dict(label='5 · Spot the error', hint='The per-task limit is 10, but the data has 30 days. Fix the job by processing the days in chunks of at most 10.', expect='error',
             code='''days = [f"2026-10-{d:02d}" for d in range(1, 31)]
PERNODE = 10
created = set()
for d in days:                         # one task writes every day
    created.add(d)
    assert len(created) <= PERNODE, f"Error 20004: {len(created)} partitions on this node, max {PERNODE}"
print(len(created))
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: strict-mode-safe inserts and daily registration',
    intro='<p>More statements to try in Beeline on the TiffinGo data. <b>Outputs are real</b>, from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · Static date, dynamic city: works even in strict mode', cmd="SET hive.exec.dynamic.partition.mode=strict;\nCREATE TABLE orders_dc LIKE orders_day_city;\nINSERT OVERWRITE TABLE orders_dc PARTITION (order_date='2026-10-06', city)\nSELECT order_id, customer_id, amount, payment, status, city\nFROM orders WHERE order_date = '2026-10-06';\nSELECT city, COUNT(*) AS n FROM orders_dc GROUP BY city ORDER BY n DESC LIMIT 3;", file='Beeline',
             output=capf('l52_mixed.txt'),
             note='One static column satisfies strict mode. The static level must come first; <code>PARTITION (order_date, city=\'Pune\')</code> (dynamic before static) is not allowed.'),
        dict(title='2 · Register one new folder, twice', cmd="-- a new folder dt=2026-10-05 was written by the app team\nALTER TABLE app_clicks ADD IF NOT EXISTS PARTITION (dt='2026-10-05');\nALTER TABLE app_clicks ADD IF NOT EXISTS PARTITION (dt='2026-10-05');\nSELECT dt, COUNT(*) AS n FROM app_clicks GROUP BY dt ORDER BY dt;", file='Beeline',
             output=capf('l52_add.txt'),
             note='IF NOT EXISTS makes the second call a no-op, so the job can be re-run safely. (10-01 is gone after the SYNC in Step 8, and 10-04 was dropped by SYNC too.)'),
        dict(title='3 · What MSCK does with a badly named folder', cmd='SET hive.msck.path.validation;     -- the default\nMSCK REPAIR TABLE app_clicks;       -- with a folder named 2026/ under the table', file='Beeline',
             output=tables(capf('l52_msck4.txt'))[0] + '\n\n' + 'Error: … DDLTask. org.apache.hadoop.hive.metastore.api.MetastoreException: Invalid partition name file:/data/tiffingo/clicks/2026',
             note='<code>throw</code> stops the whole repair. <code>skip</code> ignores bad folders and repairs the rest; <code>ignore</code> tries to create partitions from them anyway, which is rarely what you want.'),
    ],
)

TRACE = dict(
    heading='Counting partitions against the limit',
    intro='<p>Each task tracks the partitions it has opened. Watch <code>opened</code> until it crosses the limit, as in the real Error 20004.</p>',
    code='''limit = 3
rows = ["10-01", "10-01", "10-02", "10-03", "10-04"]
opened = set()
for day in rows:
    opened.add(day)
    if len(opened) > limit:
        print("Fatal: too many dynamic partitions:", len(opened))
        break
print(sorted(opened))
''',
    notes={5: 'Open :: A repeated day reuses its open file; a new day opens a new one.', 7: 'Limit :: Hive fails the task at this point, exactly like “number of dynamic partitions on this node: 11” with a limit of 10.'},
)

WORKED_INTRO = 'Three partition-loading tasks from TiffinGo’s data team.'
EXAMPLES = [
    dict(level='b', tag='ETL · dynamic insert', title='Build the SELECT for a dynamic insert',
         problem='<p>Given a target table’s data columns and partition columns, generate the INSERT so that the partition columns come last, in the right order.</p>',
         inp='data: order_id, amount, payment, status · partitions: order_date, city',
         approach=['List the data columns in table order.', 'Append the partition columns in PARTITION order.', 'Build the statement.'],
         code='''data_cols = ["order_id", "amount", "payment", "status"]
part_cols = ["order_date", "city"]
select = ", ".join(data_cols + part_cols)
print(f"INSERT OVERWRITE TABLE orders_day_city PARTITION ({', '.join(part_cols)})")
print(f"SELECT {select} FROM orders;")
''', notes={3: 'Order :: Partition columns last, in the same order as PARTITION (…). This prevents the 69-folder accident.'},
         tryit='Generating the column list from table metadata (DESCRIBE) instead of typing it is how many frameworks avoid the wrong-order trap.'),
    dict(level='i', tag='Data quality · NULL partitions', title='Replace NULL before partitioning',
         problem='<p>Referral city is missing for some customers. Partition by it without creating <code>__HIVE_DEFAULT_PARTITION__</code>: use <code>coalesce(ref_city, \'UNKNOWN\')</code> as the last column.</p>',
         inp='["Mumbai", None, "Pune", None, "Thane", "Mumbai"]',
         approach=['Map NULL to an explicit label.', 'Group rows by the label.', 'Count rows per partition.'],
         code='''refs = ["Mumbai", None, "Pune", None, "Thane", "Mumbai"]
parts = {}
for r in refs:
    key = r if r is not None else "UNKNOWN"      # coalesce(ref_city, 'UNKNOWN')
    parts[key] = parts.get(key, 0) + 1
print(parts)
''', notes={4: 'coalesce :: The NULL rows now have a readable, queryable partition: ref_city = \'UNKNOWN\'.'},
         tryit='Real lab: without coalesce, <code>WHERE ref_city IS NULL</code> returned 0 rows while 10 rows sat in the default partition.'),
    dict(level='a', tag='Operations · MSCK planning', title='Which MSCK option is safe?',
         problem='<p>The metastore lists 10-01 … 10-04 (10-04 has a custom LOCATION). On storage, the <code>dt=</code> folders are 10-02, 10-03 and 10-05. Compute the result of ADD, DROP and SYNC, the way Hive 4.2.1 behaved in our lab.</p>',
         inp='metastore {01, 02, 03, 04*} · folders {02, 03, 05} · * custom location',
         approach=['ADD: register folders not in the metastore.', 'DROP: remove entries without a dt= folder; custom locations count as missing.', 'SYNC: both.'],
         code='''meta = {"10-01", "10-02", "10-03", "10-04"}
folders = {"10-02", "10-03", "10-05"}          # 10-04 lives in 2026/10/04, not dt=...
def msck(mode):
    m = set(meta)
    if mode in ("ADD", "SYNC"):
        m |= folders
    if mode in ("DROP", "SYNC"):
        m &= folders
    return sorted(m)
for mode in ["ADD", "DROP", "SYNC"]:
    print(mode, msck(mode))
''', notes={8: 'DROP :: 10-04 is dropped because its data is not in a dt= folder, even though it exists.'},
         tryit='None of the three options gives the correct set {02, 03, 04, 05}. Use ADD, then drop 10-01 explicitly with ALTER TABLE … DROP PARTITION.'),
]

QUIZ = mix([
    dict(q='Beginner: In a dynamic partition insert, where must the partition column appear in the SELECT?', options=['First', 'Last (in PARTITION order)', 'Anywhere; Hive matches by name', 'It must not appear'], answer=1,
         why='Partition values are taken from the trailing columns, by position.'),
    dict(q='Beginner: What does MSCK REPAIR TABLE do?', options=['Fixes corrupted files', 'Registers partition folders that exist on storage but not in the metastore', 'Compacts small files', 'Rebuilds statistics'], answer=1,
         why='It syncs the metastore with the partition folders; by default it only adds.'),
    dict(q='Beginner: Where do rows with a NULL partition value go?', options=['They are dropped', 'An error', '__HIVE_DEFAULT_PARTITION__', 'partition=NULL'], answer=2,
         why='Set by hive.exec.default.partition.name.'),
    dict(q='Intermediate: What is the default hive.exec.dynamic.partition.mode in our Hive 4.2.1 lab?', options=['strict', 'nonstrict', 'off', 'auto'], answer=1,
         why='Older versions defaulted to strict, which is why many scripts start with SET … =nonstrict.'),
    dict(q='Intermediate: In strict mode, which clause is accepted?', options=['PARTITION (order_date)', "PARTITION (order_date='2026-10-06', city)", "PARTITION (order_date, city='Pune')", 'PARTITION ()'], answer=1,
         why='At least one static column, and static levels before dynamic ones.'),
    dict(q='Intermediate: The order_id and amount columns were swapped at the end of a dynamic insert. What happens?', options=['Hive reports a type error', 'Hive fixes the order by name', 'Hive creates one partition per distinct value of the wrong column', 'Nothing is written'], answer=2,
         why='Real lab: 69 bogus partitions, and re-running correctly did not remove them.'),
    dict(q='Advanced: A partition’s folder was deleted outside Hive. Which command removes the stale entry without touching others?', options=['MSCK REPAIR TABLE t', 'MSCK REPAIR TABLE t ADD PARTITIONS', "ALTER TABLE t DROP PARTITION (dt='…')", 'ANALYZE TABLE t'], answer=2,
         why='Plain MSCK only adds. SYNC also removed a custom-location partition in our lab.'),
    dict(q='Advanced: MSCK fails with “Invalid partition name …/2026”. What is the quickest safe fix?', options=['Drop the table', 'SET hive.msck.path.validation=skip and run MSCK again', 'Rename every folder', 'Use LOAD DATA'], answer=1,
         why='skip ignores folders that are not col=value; register the odd folder with ALTER … ADD PARTITION … LOCATION.'),
])

REVISION = [
    '<b>Dynamic:</b> <code>INSERT OVERWRITE TABLE t PARTITION (col) SELECT …, col FROM src</code>. Partition columns <b>last</b>, by <b>position</b>.',
    '<b>Settings (4.2.1 defaults):</b> dynamic.partition = true · mode = <b>nonstrict</b> · max.dynamic.partitions = 1000 · pernode = 100.',
    '<b>Strict</b> needs a static column (Error 10096). Mixed: <code>PARTITION (order_date=\'…\', city)</code>, static first.',
    '<b>Limits:</b> per task → Error 20004; per statement → “created is 30, which is more than 20”.',
    '<b>NULL</b> → <code>__HIVE_DEFAULT_PARTITION__</code>; use <code>coalesce(col, \'UNKNOWN\')</code>.',
    '<b>Wrong order</b> → bogus partitions, no error; OVERWRITE does not clean other partitions.',
    '<b>MSCK REPAIR TABLE t [ADD|DROP|SYNC PARTITIONS]</b>: default ADD only; DROP removes entries without folders; SYNC both.',
    '<code>hive.msck.path.validation</code>: throw (default) · skip · ignore. Odd layouts → <code>ADD PARTITION … LOCATION</code>.',
    'A missing partition folder makes queries fail (“Input path does not exist”). Delete data with DROP PARTITION, not rm.',
]
FAQ = [
    ('Should I always use dynamic partitions?', 'Use dynamic inserts for back-fills and when one batch spans several partitions. For a normal daily job that loads one known day, a static partition is clearer, cheaper (each task writes one folder) and safer, because a bad date in the data cannot create unexpected partitions.'),
    ('Why does a dynamic insert sometimes create many small files?', 'Every task writes one file into every partition it touches. With 100 map tasks and 30 days you can get 3,000 files. Adding <code>DISTRIBUTE BY order_date</code> sends each day to one reducer, so each partition gets one file. Lesson 5.4 covers small files in detail.'),
    ('Is MSCK REPAIR TABLE slow?', 'It lists every folder under the table location, so its cost grows with the number of partitions, and on cloud object stores listing is slow. For daily ingestion, ALTER TABLE … ADD IF NOT EXISTS PARTITION for the new day is much cheaper. Use MSCK for one-off repairs and restores.'),
    ('Does MSCK work on managed tables?', 'Yes, it compares folders with the metastore for any partitioned table. In practice it is used mostly for external tables, because data for managed tables normally arrives through Hive itself, which registers partitions as it writes.'),
    ('Do Spark and Trino see partitions added by MSCK?', 'Yes. They read the same metastore, so once a partition is registered every engine can prune and read it. Spark has its own <code>MSCK REPAIR TABLE</code> / <code>ALTER TABLE … RECOVER PARTITIONS</code> that writes to the same metastore.'),
]

PRACTICE_INTRO = 'Programs that simulate dynamic partitioning and MSCK, with the HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Count partitions a back-fill will create', stmt='Count the distinct dates in a batch before running a dynamic insert.', inp='list of order dates',
         code='''dates = ["2026-10-01", "2026-10-01", "2026-10-02", "2026-10-30", "2026-10-02"]
print(len(set(dates)))
''', explain='In Hive: <code>SELECT COUNT(DISTINCT order_date) FROM orders</code>. Real lab: 30. Compare with the max partition limits before running.'),
    dict(level='easy', title='Folder name for NULL', stmt='Print the partition folder for each value, using Hive’s default name for NULL.', inp='["Pune", None]',
         code='''for v in ["Pune", None]:
    print("ref_city=" + (v if v is not None else "__HIVE_DEFAULT_PARTITION__"))
''', explain='Controlled by <code>hive.exec.default.partition.name</code>.'),
    dict(level='easy', title='Is this clause strict-safe?', stmt='Check whether a PARTITION clause has at least one static value.', inp="three clauses",
         code='''clauses = [{"order_date": None}, {"order_date": "2026-10-06", "city": None}, {"order_date": None, "city": None}]
for c in clauses:
    print(c, "OK in strict" if any(v is not None for v in c.values()) else "Error 10096")
''', explain='Only the mixed clause passes in strict mode.'),
    dict(level='medium', title='Chunk a back-fill', stmt='Split 30 days into runs of at most 10 partitions each.', inp='days 1–30, limit 10',
         code='''days = [f"2026-10-{d:02d}" for d in range(1, 31)]
for i in range(0, len(days), 10):
    chunk = days[i:i + 10]
    print(f"WHERE order_date BETWEEN '{chunk[0]}' AND '{chunk[-1]}'")
''', explain='Three INSERT OVERWRITE runs. Each stays under the limit and can be re-run on its own.'),
    dict(level='medium', title='Detect bogus partitions', stmt='Find partition values that are not valid payment modes.', inp='SHOW PARTITIONS output',
         code='''valid = {"UPI", "Card", "COD", "Wallet"}
parts = ["payment=480.00", "payment=Card", "payment=UPI", "payment=170.00"]
print([p for p in parts if p.split("=", 1)[1] not in valid])
''', explain="Real lab: 69 bogus partitions; <code>ALTER TABLE pay_by_mode DROP PARTITION (payment &lt; 'A')</code> removed them."),
    dict(level='medium', title='What MSCK will add', stmt='List the folders that MSCK (ADD) will register.', inp='folders vs metastore',
         code='''folders = {"dt=2026-10-01", "dt=2026-10-02", "dt=2026-10-03"}
meta = {"dt=2026-10-01"}
print(sorted(folders - meta))
''', explain='The set difference: 10-02 and 10-03, exactly what our second MSCK added.'),
    dict(level='business', title='Daily registration script', stmt='Generate the ALTER statements for the days that arrived since the last run.', inp='last registered 2026-10-03, today 2026-10-06',
         code='''from datetime import date, timedelta
last, today = date(2026, 10, 3), date(2026, 10, 6)
d = last + timedelta(days=1)
while d < today:
    print(f"ALTER TABLE app_clicks ADD IF NOT EXISTS PARTITION (dt='{d}');")
    d += timedelta(days=1)
''', explain='Two statements (10-04 and 10-05). Cheaper than MSCK on a table with years of folders, and safe to repeat.'),
    dict(level='business', title='Estimate small files', stmt='A dynamic insert runs with 50 map tasks over 30 days, and every task sees every day. How many files are written, and how many with DISTRIBUTE BY order_date?', inp='50 tasks, 30 days',
         code='''tasks, days = 50, 30
print("without DISTRIBUTE BY:", tasks * days)
print("with DISTRIBUTE BY   :", days)
''', explain='1,500 files vs 30. Each file adds work for the NameNode and for every later query.'),
]

SCN_INTRO = 'Dynamic partitions and MSCK appear in both fresher and data engineer interviews, usually with a “what went wrong” twist.'
SCENARIOS = (
    scn('Any company · Hive', 'Fresher', '“Static vs dynamic partitioning”',
        'Explain the difference and when you would use each.',
        'do you know how the value is chosen and the settings involved?',
        '<p>Static: the value is written in the statement, e.g. <code>PARTITION (dt=\'2026-10-05\')</code>; good for daily loads of a known day. Dynamic: <code>PARTITION (dt)</code> without a value, and Hive takes it from the last SELECT column, creating partitions as needed; good for back-fills. Dynamic needs <code>hive.exec.dynamic.partition=true</code>, and strict mode requires at least one static column. Limits: 1000 per statement, 100 per node by default.</p>', 'Saying dynamic is “always better”.') +
    scn('Data engineering', 'Mid-level', 'Hundreds of strange partitions appeared',
        'After a new back-fill job, SHOW PARTITIONS lists values like payment=480.00.',
        'do you know that dynamic partitions are positional?',
        '''<ol>
          <li>Check the SELECT: the partition column was not last.</li>
          <li>Drop the bogus partitions (or recreate the table); a corrected OVERWRITE does not remove them.</li>
          <li>Generate column lists from metadata, and alert when a load creates more partitions than expected.</li>
        </ol>''', '“Hive must have a bug”, without reading the SELECT.') +
    scn('Data platform', 'Mid-level', 'The table is empty after a migration',
        'Files were copied to the new cluster and the table was recreated with the same DDL, but SELECT COUNT(*) returns 0.',
        'do you know the metastore holds the partition list?',
        '''<ul>
          <li>The new metastore has the table but no partitions.</li>
          <li>Run <code>MSCK REPAIR TABLE t</code> (set <code>hive.msck.path.validation=skip</code> if odd folders exist), then check counts per partition.</li>
          <li>Re-add partitions with custom locations using ALTER … ADD PARTITION … LOCATION.</li>
        </ul>''', '“Reload all data”.') +
    scn('Analytics platform', 'Senior', 'Every query on a table fails',
        'Queries on the clicks table fail with “Input path does not exist”. A cleanup job ran last night.',
        'can you repair metastore/storage drift safely?',
        '''<ul>
          <li>Identify missing folders: compare SHOW PARTITIONS with a listing of the location.</li>
          <li>Drop exactly those partitions with ALTER TABLE … DROP PARTITION (plain MSCK only adds; SYNC may also drop custom-location partitions).</li>
          <li>Change the cleanup job to drop partitions through Hive, so files and metadata go together.</li>
        </ul>''', 'Running MSCK … SYNC on a production table without checking which partitions it will drop.')
)
