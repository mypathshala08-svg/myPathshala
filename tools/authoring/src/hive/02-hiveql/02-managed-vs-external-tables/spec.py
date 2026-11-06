import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
BODY = body(HERE)
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep

META = dict(
    module='02-hiveql', lesson='02-managed-vs-external-tables', n='2.2',
    module_label='Module 2 · Tables and data',
    title='Managed vs external tables',
    desc='Managed and external tables in Hive 4: who owns the data, where it lives, what DROP, TRUNCATE and UPDATE do, the external.table.purge property, Hive 4 translation of plain CREATE TABLE, ACID delta folders, orphan files and how to choose a table type. Real outputs from Hive 4.2.1.',
    og_desc='Two DROP TABLE commands: one deletes 4,820 orders, the other deletes nothing. Learn why, with real Hive 4 outputs.',
    minutes=30, level='Beginner → Advanced',
    lead='<code>DROP TABLE</code> can delete your data or leave it untouched, depending on who owns it. This lesson creates three tables over the same TiffinGo orders (external, plain and ACID managed), updates a row, truncates, drops all three and inspects the folders after every step. You will also see two real incidents: a purge flag that deletes a shared folder, and a DROP that leaves orphan files. <b>All outputs are real</b>, from Hive 4.2.1.',
    chips=['Real Hive 4.2.1 outputs', 'ACID delta folders', '3 incident scenarios', 'Runs in your browser (Python)'],
)

MAIN = '''# What does DROP TABLE delete? The rule Hive 4 follows.
tables = {
    "orders_ext":   {"type": "EXTERNAL_TABLE", "purge": False},
    "orders_plain": {"type": "EXTERNAL_TABLE", "purge": True},   # plain CREATE TABLE in Hive 4
    "orders_acid":  {"type": "MANAGED_TABLE",  "purge": None},
}

def drop_deletes_files(t):
    return t["type"] == "MANAGED_TABLE" or t["purge"] is True

for name, t in tables.items():
    action = "metadata + files" if drop_deletes_files(t) else "metadata only"
    print(f"DROP {name:13} -> deletes {action}")
'''
RUN = dict(
    heading='Run the code: the rules of ownership',
    intro='<p>These programs encode what you observed in the lab: which tables lose their files on DROP, which statements each type accepts, and how an ACID table records changes as new folders. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('"orders_plain": {"type": "EXTERNAL_TABLE", "purge": True},', 'This is how Hive 4 stored our plain <code>CREATE TABLE</code>: external, with <code>external.table.purge=TRUE</code>.'),
        ('return t["type"] == "MANAGED_TABLE" or t["purge"] is True', 'The whole rule in one line: managed, or external with purge, means DROP deletes files.'),
    ],
    tasks=[
        dict(label='1 · DROP rule', hint='Press <b>Run</b>. Then set <code>orders_ext</code>’s purge to <code>True</code> and see the risk.', code=None),
        dict(label='2 · Which statements are allowed?', hint='<b>Predict first:</b> which of TRUNCATE and UPDATE work on each type? The table comes from the lab results.',
             code='''allowed = {
    "MANAGED (ACID)":   {"TRUNCATE": True,  "UPDATE": True},
    "EXTERNAL + purge": {"TRUNCATE": True,  "UPDATE": False},
    "EXTERNAL":         {"TRUNCATE": False, "UPDATE": False},
}
for kind, ops in allowed.items():
    print(f"{kind:17}", ", ".join(f"{op}: {'yes' if ok else 'no'}" for op, ok in ops.items()))
'''),
        dict(label='3 · ACID deltas', hint='Each write is a transaction. Inserts add a <code>delta</code> folder; an update adds a <code>delete_delta</code> and a <code>delta</code>. Add a DELETE as transaction 3.',
             code='''folders = []
def write(txn, kind, stmt=0):
    name = f"{kind}_{txn:07d}_{txn:07d}_{stmt:04d}"
    folders.append(name)
write(1, "delta")              # INSERT
write(2, "delete_delta")       # UPDATE: old version removed
write(2, "delta", 1)           # UPDATE: new version added
for f in sorted(folders):
    print(f)
'''),
        dict(label='4 · Reading an ACID table', hint='A reader starts from inserted rows and removes those listed in delete deltas, then adds the new versions. Predict the amount for 100010.',
             code='''inserted = {100010: 260, 100012: 300}          # delta_1
deleted  = {100010}                             # delete_delta_2
updated  = {100010: 999}                        # delta_2
current = {k: v for k, v in inserted.items() if k not in deleted}
current.update(updated)
print(current)
'''),
        dict(label='5 · Spot the error', hint='A clean-up script drops every table whose name starts with <code>tmp_</code>. One of them is a purge table over a shared folder. The safety check fails: fix the list or the rule.', expect='error',
             code='''tables = {"tmp_city": ("/warehouse/tiffingo.db/tmp_city", True),
          "tmp_events": ("/landing/app_events", True)}      # shared folder!
for name, (path, purge) in tables.items():
    if name.startswith("tmp_"):
        assert not (purge and path.startswith("/landing")), f"{name} would delete shared data at {path}"
        print("drop", name)
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: ownership experiments',
    intro='<p>Use the lab from Lesson 1.5 with the orders file copied to <code>data/tiffingo/orders_ext/</code>. <b>Outputs are real</b>, recorded from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · The ACID folders after INSERT and UPDATE', cmd='docker exec hiveserver2 find /opt/hive/data/warehouse/tiffingo.db/orders_acid -type d', file='Terminal',
             output='\n'.join('/opt/hive/data/warehouse/tiffingo.db/' + l for l in open(CAP + 'l22_acid_dirs.txt').read().split()),
             note='Transaction 1 (INSERT) made <code>delta_0000001_0000001_0000</code>. Transaction 2 (UPDATE) made <code>delete_delta_0000002_0000002_0000</code> and <code>delta_0000002_0000002_0001</code>. Compaction later merges them (Module 7).'),
        dict(title='2 · Re-create an external table after DROP', cmd="DROP TABLE orders_ext;\nCREATE EXTERNAL TABLE orders_ext (order_id INT, customer_id INT, restaurant_id INT, city STRING,\n  order_ts TIMESTAMP, amount INT, payment STRING, status STRING)\nROW FORMAT DELIMITED FIELDS TERMINATED BY ','\nLOCATION 'file:///data/tiffingo/orders_ext';\nSELECT COUNT(*) FROM orders_ext;", file='Beeline',
             output=open(CAP + 'l22_recreate.txt').read().rstrip(),
             note='All 50,002 rows are back at once, because DROP never touched the files. This is why external tables are used for data other systems own.'),
        dict(title='3 · Purge on, then DROP', cmd="CREATE EXTERNAL TABLE scratch_copy (line STRING) LOCATION 'file:///data/tiffingo/scratch_copy';\nALTER TABLE scratch_copy SET TBLPROPERTIES ('external.table.purge'='true');\nDROP TABLE scratch_copy;\n-- then, in a terminal:\nls /data/tiffingo/scratch_copy", file='Beeline + Terminal',
             output="ls: cannot access '/data/tiffingo/scratch_copy': No such file or directory",
             note='The purge flag turned DROP into a delete of the whole folder. Our first attempt failed silently because the metastore user could not delete root-owned files: the metastore log said <code>Failed to delete … it still exists</code>. We fixed the folder permissions and repeated it.'),
    ],
)

TRACE = dict(
    heading='Deciding what DROP deletes, one table at a time',
    intro='<p>Follow the loop through three table descriptions. Watch <code>deletes</code> change with the type and the purge flag.</p>',
    code='''tables = [("orders_ext", "EXTERNAL", False), ("orders_plain", "EXTERNAL", True), ("orders_acid", "MANAGED", None)]
kept = []
for name, kind, purge in tables:
    deletes = kind == "MANAGED" or purge is True
    if not deletes:
        kept.append(name)
print("files kept after DROP:", kept)
''',
    notes={4: 'Rule :: Managed, or external with purge, means the files go.', 6: 'Keep :: Only plain external tables leave their files behind.'},
)

WORKED_INTRO = 'Three ownership tasks from real platform work: auditing what a clean-up would delete, sizing ACID delta growth, and planning a safe conversion.'
EXAMPLES = [
    dict(level='b', tag='Audit · DROP safety', title='What will a clean-up script delete?',
         problem='<p>A list of tables with type, purge flag and size is given. Before running a clean-up that drops all of them, print which tables would lose their files and the total size deleted.</p>',
         inp='orders_ext EXTERNAL purge=False 3.0 MB · orders_plain EXTERNAL purge=True 0.3 MB · orders_acid MANAGED 0.1 MB · app_events EXTERNAL purge=True 1,200 MB',
         approach=['Apply the DROP rule to each table.', 'Collect those that delete files and add their sizes.', 'Print the list and the total.'],
         code='''tables = [("orders_ext", "EXTERNAL", False, 3.0), ("orders_plain", "EXTERNAL", True, 0.3),
          ("orders_acid", "MANAGED", None, 0.1), ("app_events", "EXTERNAL", True, 1200.0)]
lost, total = [], 0.0
for name, kind, purge, mb in tables:
    if kind == "MANAGED" or purge is True:
        lost.append(name)
        total += mb
print("files deleted for:", lost)
print("total deleted:", total, "MB")
''', notes={5: 'Rule :: Same rule as the lab showed.'},
         tryit='app_events is a shared landing table with purge switched on. Set its purge to False and the deleted total drops from 1,200.4 MB to 0.4 MB.'),
    dict(level='i', tag='ACID · file growth', title='How many delta folders after a month?',
         problem='<p>A managed ACID table receives 24 inserts per day (one per hour) and 4 update batches per day. Each insert adds one delta folder; each update adds one delta and one delete_delta. How many folders after 30 days without compaction, and after daily compaction to one base folder?</p>',
         inp='24 inserts/day · 4 updates/day · 30 days',
         approach=['Folders per day = inserts + 2 × updates.', 'Multiply by days for no compaction.', 'With daily major compaction: one base plus the current day’s deltas at most.'],
         code='''inserts, updates, days = 24, 4, 30
per_day = inserts + 2 * updates
print("folders per day      :", per_day)
print("after 30 days, none  :", per_day * days)
print("with daily compaction:", 1 + per_day, "at most")
''', notes={3: 'Count :: Each update writes two folders.'},
         tryit='960 folders means 960 directory listings for every query. Change updates to 40 per day: the growth shows why ACID tables need compaction (Module 7).'),
    dict(level='a', tag='Migration · plan', title='Convert a plain table into an ACID table safely',
         problem='<p>A team wants UPDATE on <code>orders_plain</code> (external + purge, text). You cannot simply flip a property; you plan: create an ACID copy, copy rows, verify counts, swap names. Print the plan with the SQL for each step and check the counts match.</p>',
         inp='orders_plain has 4,820 rows',
         approach=['Write each step as (description, SQL).', 'Simulate the copy and compare counts.', 'Only print the swap if counts match.'],
         code='''steps = [
    ("create ACID copy", "CREATE TABLE orders_new (order_id INT, city STRING, amount INT) STORED AS ORC TBLPROPERTIES ('transactional'='true')"),
    ("copy rows",        "INSERT INTO orders_new SELECT * FROM orders_plain"),
    ("verify",           "SELECT COUNT(*) FROM orders_new"),
]
source_rows = 4820
copied_rows = 4820          # result of the verify step
for i, (what, sql) in enumerate(steps, 1):
    print(f"{i}. {what:16} {sql[:60]}...")
if copied_rows == source_rows:
    print("4. swap names     ALTER TABLE orders_plain RENAME TO orders_old; ALTER TABLE orders_new RENAME TO orders_plain")
else:
    print("STOP: counts differ")
''', notes={9: 'Check :: Never swap before the counts agree.'},
         tryit='Set copied_rows to 4819. The plan stops before the swap. Real migrations add checksums (SUM of amount) as well as counts.'),
]

QUIZ = mix([
    dict(q='Beginner: What does DROP TABLE do to a plain external table (purge off)?', options=['Deletes metadata and files', 'Deletes only the metadata; the files stay', 'Deletes only the files', 'Nothing'], answer=1,
         why='In the lab orders.csv was still there after DROP, and re-creating the table returned 50,002 rows.'),
    dict(q='Beginner: Where is a managed table stored by default?', options=['Anywhere the user chooses', 'Under the warehouse folder of its database', 'In the metastore database', 'In /tmp'], answer=1,
         why='For example file:/opt/hive/data/warehouse/tiffingo.db/orders_acid.'),
    dict(q='Beginner: Which type should you use for files that a Kafka connector writes and several teams read?', options=['Managed ACID', 'External with purge off', 'Temporary', 'External with purge on'], answer=1,
         why='Hive must not own or delete files another system writes; purge must stay off.'),
    dict(q='Intermediate: In Hive 4 with default settings, what does a plain CREATE TABLE (no transactional property) produce?', options=['MANAGED_TABLE, transactional', 'EXTERNAL_TABLE with external.table.purge=TRUE', 'A view', 'A temporary table'], answer=1,
         why='Hive 4 translates it (TRANSLATED_TO_EXTERNAL=TRUE). DROP still deletes its files.'),
    dict(q='Intermediate: Which statement failed on the plain external table orders_ext?', options=['SELECT COUNT(*)', 'TRUNCATE TABLE', 'DESCRIBE FORMATTED', 'DROP TABLE'], answer=1,
         why='“Cannot truncate non-managed table orders_ext.” Hive will not empty files it does not own.'),
    dict(q='Intermediate: Why was UPDATE refused on orders_plain?', options=['The table was empty', 'The table is not transactional', 'UPDATE does not exist in HiveQL', 'The user had no password'], answer=1,
         why='Error 10297: update or delete on a table that is not transactional. Only ACID tables accept UPDATE/DELETE/MERGE.'),
    dict(q='Advanced: An UPDATE on an ACID table created which folders?', options=['It edited the ORC file in place', 'A delete_delta and a new delta for the transaction', 'A base folder only', 'A .crc file only'], answer=1,
         why='Files are never edited: delete_delta_0000002… marks the old row, delta_0000002…_0001 holds the new one.'),
    dict(q='Advanced: DROP TABLE reported success but the files are still there. What is the most likely cause?', options=['DROP never deletes files', 'The metastore user lacked permission to delete the folder', 'The table was ACID', 'Beeline was in silent mode'], answer=1,
         why='Metadata is removed first, then files are deleted as the metastore user; in our lab the log said “Failed to delete … it still exists”.'),
])

REVISION = [
    '<b>Managed</b>: Hive owns metadata + files; warehouse location; DROP deletes files; Hive 3/4 managed = <b>ACID</b> (transactional).',
    '<b>External</b>: Hive owns metadata only; any LOCATION; DROP keeps files; TRUNCATE/UPDATE refused.',
    '<code>external.table.purge=TRUE</code> → DROP deletes an external table’s files. Never on shared folders.',
    'Hive 4: plain <code>CREATE TABLE</code> → <code>EXTERNAL_TABLE</code> + purge + <code>TRANSLATED_TO_EXTERNAL</code> (when <code>hive.create.as.acid=false</code>).',
    "ACID: <code>STORED AS ORC TBLPROPERTIES ('transactional'='true')</code>; writes create <code>delta_…</code>, deletes <code>delete_delta_…</code>; compaction merges.",
    'Check before DROP: <code>DESCRIBE FORMATTED</code> → Table Type, purge, transactional, Location.',
    'DROP = metastore step + storage step; permission problems leave <b>orphan files</b> (see metastore log).',
    'Choose: other tools write? → external. Rows change? → ACID (or Iceberg). DROP should clean up? → managed/purge.',
]
FAQ = [
    ('Is “internal table” the same as “managed table”?', 'Yes. Older books and many interview questions say internal table; Hive’s metadata calls it MANAGED_TABLE. In Hive 3 and later managed tables are transactional, so “internal” also implies ACID in modern Hive.'),
    ('Can I convert an external table into a managed one?', 'The table type is stored as a property (EXTERNAL=TRUE/FALSE) that ALTER TABLE can change, and the metastore accepted the change in our lab. But a managed table in Hive 4 is expected to be transactional, and a text table in a shared folder cannot become ACID in place. The safe way is to create a new transactional table, copy the rows with INSERT … SELECT, verify, and swap names.'),
    ('Does DROP on a managed table go to the trash?', 'On HDFS with trash enabled, dropped data is moved to the user’s .Trash folder for a configured time, which allows recovery; DROP TABLE … PURGE skips the trash. Object stores have no HDFS trash, so use bucket versioning or backups there. Our local lab has no trash.'),
    ('Why does Hive 4 translate my table to external instead of making it managed?', 'Managed tables are reserved for data whose every write Hive controls, so it can offer ACID transactions. A non-transactional table cannot give those guarantees, so the metastore stores it as external with purge on: you keep the old “DROP deletes data” behaviour without pretending it is ACID. Setting hive.create.as.acid=true makes plain CREATE TABLE produce ACID tables instead.'),
    ('Can Spark read Hive managed ACID tables?', 'Not with plain Spark readers: they would see delta and delete_delta folders and could return deleted or duplicated rows. Spark needs a connector that understands Hive ACID, or the data should be in an external format built for many engines, such as Iceberg (Module 7). This is a common reason teams keep shared tables external.'),
]

PRACTICE_INTRO = 'Programs on DROP rules, permitted statements, ACID folders and safe clean-ups.'
PROBLEMS = [
    dict(level='easy', title='Kept or deleted?', stmt='For each table (type, purge), print whether DROP keeps the files.', inp='EXTERNAL/False · EXTERNAL/True · MANAGED/None',
         code='''for kind, purge in [("EXTERNAL", False), ("EXTERNAL", True), ("MANAGED", None)]:
    keeps = kind == "EXTERNAL" and purge is not True
    print(kind, purge, "-> keeps files" if keeps else "-> deletes files")
''', explain='Only a plain external table keeps its files.'),
    dict(level='easy', title='Default location', stmt='Print the default folder of managed table orders_acid in database tiffingo, warehouse /opt/hive/data/warehouse.', inp='tiffingo · orders_acid',
         code='''print("/opt/hive/data/warehouse/tiffingo.db/orders_acid")
''', explain='Managed and purge tables without LOCATION live under &lt;warehouse&gt;/&lt;db&gt;.db/&lt;table&gt;.'),
    dict(level='easy', title='Name the delta', stmt='Build the delta folder name for transaction 7, statement 0, with 7-digit padding and 4-digit statement id.', inp='txn 7, stmt 0',
         code='''txn, stmt = 7, 0
print(f"delta_{txn:07d}_{txn:07d}_{stmt:04d}")
''', explain='delta_0000007_0000007_0000, the same pattern as the lab’s delta_0000001_0000001_0000.'),
    dict(level='medium', title='Count rows in an ACID read', stmt='Inserted ids [1..6], delete deltas remove {2, 5}, update delta adds new versions of {5}. How many rows does a reader see?', inp='inserted 6 · deleted {2,5} · re-added {5}',
         code='''inserted = set(range(1, 7))
deleted, readded = {2, 5}, {5}
visible = (inserted - deleted) | readded
print(sorted(visible), len(visible))
''', explain='5 rows: id 2 is gone, id 5 is visible in its new version. An update is a delete plus an insert.'),
    dict(level='medium', title='Which statements will fail?', stmt='Given a list of (statement, table type), print which would fail on Hive 4.', inp='TRUNCATE/EXTERNAL · UPDATE/EXTERNAL+purge · DELETE/MANAGED · TRUNCATE/EXTERNAL+purge',
         code='''ok = {("TRUNCATE", "EXTERNAL"): False, ("UPDATE", "EXTERNAL+purge"): False,
      ("DELETE", "MANAGED"): True, ("TRUNCATE", "EXTERNAL+purge"): True}
for (stmt, kind), works in ok.items():
    print(f"{stmt:8} on {kind:15} {'works' if works else 'fails'}")
''', explain='Matches the lab: external refuses TRUNCATE; only ACID managed tables accept UPDATE and DELETE; TRUNCATE works on purge tables.'),
    dict(level='medium', title='Find shared-folder risks', stmt='Flag tables with purge on whose location starts with /landing/ or /shared/.', inp='a: /landing/x purge · b: /warehouse/… purge · c: /shared/y no purge',
         code='''tables = {"a": ("/landing/x", True), "b": ("/warehouse/t.db/b", True), "c": ("/shared/y", False)}
for n, (loc, purge) in tables.items():
    if purge and loc.startswith(("/landing/", "/shared/")):
        print("RISK:", n, loc)
''', explain='Only a is risky: a DROP would delete a shared landing folder.'),
    dict(level='business', title='Cost of orphan files', stmt='An orphan check finds 340 GB of folders with no table. Storage costs Rs 1.8 per GB per month. What is the yearly cost of leaving them?', inp='340 GB · Rs 1.8/GB/month',
         code='''gb, rate = 340, 1.8
print("per month: Rs", gb * rate, "| per year: Rs", gb * rate * 12)
''', explain='Rs 612 per month, Rs 7,344 a year, plus the risk that a future table on those paths reads stale rows.'),
    dict(level='business', title='Trash saves the day', stmt='HDFS trash keeps deleted files for 1,440 minutes. A wrong DROP happened at 09:10 and was noticed at 18:40 the next day. Can it be restored from trash?', inp='interval 1,440 min · 09:10 day 1 → 18:40 day 2',
         code='''elapsed = (24 * 60 - (9 * 60 + 10)) + (18 * 60 + 40)
print("minutes since DROP:", elapsed, "| restorable:", elapsed <= 1440)
''', explain='2,010 minutes > 1,440, so the trash has been emptied. Teams with critical tables add snapshots or versioning, and alert on DROP of important tables.'),
]

SCN_INTRO = '“Managed vs external” is one of the most-asked Hive interview questions. Strong answers include Hive 3/4 behaviour and a real incident.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Managed vs external: which would you use?”',
        'The interviewer gives two datasets: clickstream files written by a Kafka job, and a cleaned orders table that needs refunds applied.',
        'can you connect table type to ownership and features?',
        '''<ul>
          <li>Clickstream: <b>external</b> table on the Kafka job’s folder, purge off, because another system owns the files and DROP must not delete them.</li>
          <li>Orders: <b>managed ACID</b> table (ORC, transactional) so refunds can be applied with UPDATE or MERGE.</li>
          <li>Mention that in Hive 3/4 managed means transactional, and that a plain CREATE TABLE becomes external with purge in Hive 4.</li>
        </ul>''', '“external is always safer”: you lose UPDATE, DELETE, MERGE and TRUNCATE.') +
    scn('Operations · incident', 'Mid-level', 'A shared folder disappeared after a DROP',
        'The marketing team’s landing folder vanished. The audit log shows a DROP TABLE on a table in a sandbox database.',
        'do you know the purge flag and how to investigate?',
        '''<ol>
          <li>Check the dropped table’s last DDL: it was external but had <code>external.table.purge=true</code> and pointed at the shared folder.</li>
          <li>Restore from HDFS trash or snapshots (or object-store versioning) quickly, before trash expiry.</li>
          <li>Prevent: no purge on shared paths, restrict ALTER TABLE properties, separate sandbox paths, alert on DROP of tables with purge on non-warehouse paths.</li>
        </ol>''', 'blaming HDFS; the metastore did exactly what the table properties said.') +
    scn('Platform · upgrade', 'Mid-level', 'Upgrading from Hive 2 to Hive 4',
        'Your company has 3,000 Hive 2 managed text tables. What changes for users after an upgrade to Hive 4?',
        'do you know the managed-table changes since Hive 3?',
        '''<ul>
          <li>Managed tables are now ACID; non-transactional managed tables are typically migrated to external tables with purge (the upgrade tooling does this), so DROP still deletes data.</li>
          <li>Plain CREATE TABLE in Hive 4 makes external purge tables unless <code>hive.create.as.acid</code> is enabled.</li>
          <li>Other engines must not write into ACID table folders; shared tables should stay external (or move to Iceberg).</li>
          <li>Audit: list each table’s type, purge flag and location before and after.</li>
        </ul>''', '“nothing changes, it is the same SQL”.') +
    scn('Data engineering · debugging', 'Fresher', 'Rows appear that should be deleted',
        'A Spark job reads the folder of a Hive ACID table and reports refunded orders that Hive no longer shows.',
        'do you understand delta and delete_delta files?',
        '''<ul>
          <li>ACID tables record deletes in <code>delete_delta</code> folders; Hive merges them when reading.</li>
          <li>A plain Spark file reader sees all files, so deleted and old versions of rows appear.</li>
          <li>Read through Hive (or an ACID-aware connector), or publish a shared copy in an external format (ORC/Parquet or Iceberg) for other engines.</li>
        </ul>''', 'blaming the data; the reader is not ACID-aware.')
)
