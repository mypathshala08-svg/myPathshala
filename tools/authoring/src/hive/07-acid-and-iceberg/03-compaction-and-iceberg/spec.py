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
    module='07-acid-and-iceberg', lesson='03-compaction-and-iceberg', n='7.3',
    module_label='Module 7 · Transactions, MERGE and Iceberg',
    title='Compaction and Iceberg tables',
    desc='Hive ACID compaction and Apache Iceberg tables in Hive 4, with real Hive 4.2.1 results: automatic major compaction after 11 deltas, minor and major compaction by hand, compaction thresholds, Iceberg tables with STORED BY ICEBERG and hidden partitioning, snapshots and position-delete files from UPDATE and DELETE, time travel with FOR SYSTEM_VERSION / SYSTEM_TIME AS OF, schema and partition evolution without rewriting, rollback, expiring snapshots, MERGE on Iceberg, and what Hive 4.2.1’s Iceberg compaction refused.',
    og_desc='Delta folders merged into one base, and an Iceberg table you can query as it was yesterday. Compaction and Iceberg in Hive 4.2.1, with real outputs.',
    minutes=40, level='Intermediate → Advanced',
    lead='Lessons 7.1 and 7.2 filled tables with delta folders. This lesson shows how the <b>compactor</b> cleans them up, automatically and by hand, and then introduces <b>Apache Iceberg</b>, the open table format Hive 4 supports natively: snapshots, time travel, rollback, schema and partition evolution, and tables shared with Spark and Trino. We also report two things Hive 4.2.1 refused in our lab. <b>All outputs are real</b>, from Hive 4.2.1.',
    chips=['Real Hive 4.2.1 outputs', 'Minor vs major compaction', 'Iceberg time travel', 'Runs in your browser (Python)'],
)

MAIN = '''# Iceberg snapshots: each commit records the list of live data and delete files
snapshots = []
files = []                                         # (name, rows)
def commit(op, add=(), deletes=0):
    global files
    files = files + list(add)
    deleted = sum(s["deletes"] for s in snapshots) + deletes
    snapshots.append({"op": op, "files": list(files), "deletes": deletes,
                      "live_rows": sum(r for _, r in files) - deleted})

commit("append", add=[("d1", 1641), ("d2", 1617), ("d3", 1668)])
commit("overwrite", add=[("d2_new", 102)], deletes=102)    # UPDATE of 102 rows
commit("delete", deletes=40)                               # DELETE of 40 rows

for i, s in enumerate(snapshots, 1):
    print(i, s["op"], "files:", len(s["files"]), "live rows:", s["live_rows"])
print("time travel to snapshot 1:", snapshots[0]["live_rows"], "rows")
'''
RUN = dict(
    heading='Run the code: snapshots, time travel and compaction',
    intro='<p>These programs model Iceberg snapshots and Hive compaction with the real row counts from the lab. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('commit("overwrite", add=[("d2_new", 102)], deletes=102)    # UPDATE of 102 rows', 'Merge-on-read: the UPDATE adds the new rows and a delete file for the old ones; old files stay.'),
        ('print("time travel to snapshot 1:", snapshots[0]["live_rows"], "rows")', 'Old snapshots still list their files, so the past stays readable.'),
    ],
    tasks=[
        dict(label='1 · Snapshots and live rows', hint='Press <b>Run</b>. Snapshot 1 has 4,926 rows; after the update and delete, 4,886, as in the real table.', code=None),
        dict(label='2 · Predict first: total-records', hint='<b>Predict first:</b> Iceberg’s summary said total-records = 5,028 after the delete. Why not 4,886?',
             code='''data_file_rows = 1641 + 1617 + 1668 + 102     # rows in data files
position_deletes = 102 + 40
print("rows in data files :", data_file_rows)
print("visible rows       :", data_file_rows - position_deletes)
'''),
        dict(label='3 · Compaction trigger', hint='The initiator queues a minor compaction when there are more than 10 deltas. Change <code>deltas</code>.',
             code='''deltas = 11
threshold = 10            # hive.compactor.delta.num.threshold
print("compact" if deltas > threshold else "wait", f"({deltas} deltas)")
'''),
        dict(label='4 · Rollback', hint='Rollback moves the current pointer; nothing is copied. Real: 8,251 → 4,886 rows.',
             code='''history = [("s1", 4926), ("s2", 4926), ("s3", 4886), ("s4", 8251)]
current = "s4"
target = "s3"
current = target
print("current snapshot:", current, "rows:", dict(history)[current])
'''),
        dict(label='5 · Spot the error', hint='This job expires snapshots before the 7-day retention the data science team needs. Fix the cut-off.', expect='error',
             code='''from datetime import date, timedelta
today = date(2026, 10, 27)
retention_days = 7
cutoff = today - timedelta(days=1)                       # bug
assert cutoff <= today - timedelta(days=retention_days), f"cut-off {cutoff} would break 7-day time travel"
print("EXPIRE_SNAPSHOTS before", cutoff)
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: thresholds, MERGE on Iceberg and file lists',
    intro='<p>More statements to try on the lab. <b>Outputs are real</b>, from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · The compaction thresholds in effect', cmd='SET hive.compactor.delta.num.threshold;\nSET hive.compactor.delta.pct.threshold;\nSET hive.compactor.abortedtxn.threshold;\nSET hive.compactor.check.interval;\nSET hive.compactor.worker.threads;', file='Beeline',
             output='\n'.join(l for l in capf('l73_thr.txt').split('\n') if '=' in l),
             note='The initiator checks every 300 seconds; more than 10 deltas, deltas above 10% of the base size, or 1,000 aborted transactions queue a compaction. One worker thread ran on HiveServer2 in our lab.'),
        dict(title='2 · MERGE into an Iceberg table', cmd="CREATE TABLE dim_ice (customer_id INT, city STRING, plan STRING) STORED BY ICEBERG;\nINSERT INTO dim_ice SELECT customer_id, city, plan FROM customers WHERE customer_id <= 4;\nMERGE INTO dim_ice t USING stg2 s ON t.customer_id = s.customer_id\nWHEN MATCHED AND (t.city <> s.city OR t.plan <> s.plan) THEN UPDATE SET city = s.city, plan = s.plan\nWHEN NOT MATCHED THEN INSERT VALUES (s.customer_id, s.city, s.plan);\nSELECT * FROM dim_ice ORDER BY customer_id;\nSELECT operation, summary['added-records'] AS added, summary['added-position-deletes'] AS pos_deletes\nFROM tiffingo.dim_ice.snapshots ORDER BY committed_at;", file='Beeline',
             output=capf('l73_ice_merge.txt'),
             note='The same MERGE as Lesson 7.2 works on Iceberg. It became one “overwrite” snapshot with 3 new rows (two updated customers and Kavya) and 2 position deletes for the old versions.'),
        dict(title='3 · The files behind an Iceberg table', cmd='SELECT content, file_format, record_count, file_size_in_bytes FROM tiffingo.dim_ice.files;', file='Beeline',
             output=capf('l73_files.txt'),
             note='content 0 = data file, 1 = position-delete file. Metadata tables like files, snapshots, history and partitions are queried as <code>db.table.metatable</code>.'),
    ],
)

TRACE = dict(
    heading='Major compaction, step by step',
    intro='<p>A major compaction reads the base and all deltas, drops deleted rows and writes one new base. Watch <code>base</code> being built.</p>',
    code='''deltas = {1: ["c1", "c2", "c3", "c4", "c5"], 2: ["c2*"], 4: ["c6"]}
deleted = {(1, 1), (1, 4)}
base = []
for w in sorted(deltas):
    for i, row in enumerate(deltas[w]):
        if (w, i) not in deleted:
            base.append(row)
print("base_4:", base)
''',
    notes={2: 'Deletes :: The delete records from Lesson 7.1: old customer 2 and customer 5.', 6: 'Filter :: Deleted rows are not copied; this is the moment they disappear from disk.', 8: 'Result :: One base folder replaces every delta and delete delta.'},
)

WORKED_INTRO = 'Three operational decisions about compaction and Iceberg.'
EXAMPLES = [
    dict(level='b', tag='Operations · compaction', title='Minor or major?',
         problem='<p>For three tables decide whether the initiator would queue minor, major or no compaction, using the default thresholds.</p>',
         inp='A: 12 deltas, delta size 3% of base · B: 4 deltas, 15% of base · C: 3 deltas, 2% of base',
         approach=['delta size &gt; 10% of base → major.', 'more than 10 deltas → minor.', 'otherwise nothing.'],
         code='''tables = {"A": (12, 0.03), "B": (4, 0.15), "C": (3, 0.02)}
for name, (n, pct) in tables.items():
    if pct > 0.1:
        kind = "MAJOR"
    elif n > 10:
        kind = "MINOR"
    else:
        kind = "none"
    print(name, kind)
''', notes={3: 'Order :: The size rule is checked first: a large delta share calls for a full rewrite.'},
         tryit='Our cust_acid table with 11 small deltas on no base got a MAJOR: with no base yet, the deltas are all of the data, which most likely triggered the size rule.'),
    dict(level='i', tag='Data science · reproducibility', title='Record the training snapshot',
         problem='<p>A model is trained on orders_ice. Store the snapshot id with the model, then reproduce the row count later even after new loads.</p>',
         inp='snapshots: 4523378673848349691 (4,926 rows), later 4541262957374694773 (4,886 rows)',
         approach=['At training time, read the current snapshot id.', 'Save it with the model.', 'Later, query FOR SYSTEM_VERSION AS OF that id.'],
         code='''snapshots = {4523378673848349691: 4926, 4541262957374694773: 4886}
model = {"name": "churn_v1", "snapshot": 4523378673848349691}
print("training rows:", snapshots[model["snapshot"]])
print(f"SELECT * FROM orders_ice FOR SYSTEM_VERSION AS OF {model['snapshot']};")
''', notes={3: 'Pin :: Same rows every time, as long as the snapshot is not expired.'},
         tryit='Real lab: AS OF the first snapshot returned 4,926 rows and 306 cancelled orders. Exclude pinned snapshots from expiry, or tag them (Iceberg branches and tags).'),
    dict(level='a', tag='Architecture · retention', title='How long to keep snapshots?',
         problem='<p>Each daily load creates one snapshot and about 2 GB of new files; updates replace about 10% of them. Estimate the extra storage kept for 7 and 30 days of time travel.</p>',
         inp='2 GB new data per day, 10% superseded per day (illustrative)',
         approach=['Superseded data per day = 0.2 GB.', 'Retention keeps superseded files alive.', 'Extra = 0.2 GB × days.'],
         code='''superseded_per_day = 2.0 * 0.10
for days in [7, 30]:
    print(days, "days of time travel keep about", round(superseded_per_day * days, 1), "GB of old files")
''', notes={2: 'Cost :: Old snapshots pin files that newer snapshots no longer use.'},
         tryit='1.4 GB for a week, 6 GB for a month: usually cheap compared with the value of rollback and reproducibility. Expire on a schedule.'),
]

QUIZ = mix([
    dict(q='Beginner: What does major compaction produce?', options=['More delta folders', 'A new base folder with deleted rows removed', 'A snapshot', 'A backup'], answer=1,
         why='base_0000010 in our lab replaced 11 folders.'),
    dict(q='Beginner: How do you create an Iceberg table in Hive 4?', options=['STORED AS ICEBERG', 'STORED BY ICEBERG', "TBLPROPERTIES ('iceberg'='true')", 'CREATE ICEBERG TABLE'], answer=1,
         why='Hive uses a storage handler: STORED BY ICEBERG.'),
    dict(q='Beginner: Which clause reads an Iceberg table as it was at an earlier snapshot?', options=['WHERE snapshot = …', 'FOR SYSTEM_VERSION AS OF snapshot_id', 'VERSION …', 'AS SNAPSHOT …'], answer=1,
         why="Or FOR SYSTEM_TIME AS OF 'timestamp'."),
    dict(q='Intermediate: What is the difference between minor and major compaction?', options=['None', 'Minor merges deltas only; major rewrites base + deltas into a new base', 'Minor is for Iceberg', 'Major only compresses'], answer=1,
         why='Minor keeps delete records; major removes deleted rows physically.'),
    dict(q='Intermediate: What is hidden partitioning?', options=['Partitions that are invisible to users entirely', 'Partitions derived from a column by a transform like day(order_date), filtered via the column itself', 'Encrypted partitions', 'Partitions in the metastore only'], answer=1,
         why='Queries filter on order_date; Iceberg maps it to order_date_day.'),
    dict(q='Intermediate: After ALTER TABLE … SET PARTITION SPEC (month(order_date)), what happens to old files?', options=['They are rewritten', 'They stay in day partitions; new data uses months', 'They are deleted', 'The table becomes unreadable'], answer=1,
         why='Real lab: spec 0 files and spec 1 files coexist.'),
    dict(q='Advanced: Why did total-records stay 5,028 after deleting 40 rows?', options=['The delete failed', 'It counts rows in data files; deletes are separate position-delete files', 'Iceberg cannot delete', 'Statistics were stale'], answer=1,
         why='COUNT(*) returned 4,886; compaction would apply the deletes physically.'),
    dict(q='Advanced: What happened to time travel after EXPIRE_SNAPSHOTS?', options=['Still worked for all times', 'Queries before the remaining snapshot failed: “Cannot find a snapshot older than …”', 'Data was lost', 'The table was dropped'], answer=1,
         why='Expire only what you no longer need to read.'),
])

REVISION = [
    '<b>Compaction:</b> minor = deltas → 1 delta; major = base + deltas → <code>base_N</code> (deleted rows gone). Initiator → worker → cleaner.',
    '<b>Thresholds:</b> &gt;10 deltas → minor; deltas &gt;10% of base → major; 1,000 aborted txns; checked every 300 s. <code>NO_AUTO_COMPACTION</code> to opt out.',
    "<b>Manual:</b> <code>ALTER TABLE t [PARTITION (…)] COMPACT 'minor'|'major' [AND WAIT]</code> · <code>SHOW COMPACTIONS</code>.",
    '<b>Iceberg:</b> <code>STORED BY ICEBERG</code>, <code>PARTITIONED BY SPEC (day(col))</code>; metadata.json → manifest list → manifests → data/delete files.',
    'Hive 4.2.1 defaults: format v2, Parquet ZSTD, merge-on-read; table is EXTERNAL with purge.',
    '<b>Time travel:</b> <code>FOR SYSTEM_VERSION AS OF id</code> / <code>FOR SYSTEM_TIME AS OF \'ts\'</code>; metadata tables <code>db.t.snapshots</code>, <code>.history</code>, <code>.files</code>.',
    '<b>Evolution:</b> ADD COLUMNS, <code>SET PARTITION SPEC</code> without rewriting old files.',
    "<b>Undo / clean:</b> <code>EXECUTE ROLLBACK(id)</code>, <code>EXECUTE EXPIRE_SNAPSHOTS('ts')</code> (time travel before it is gone).",
    'Hive 4.2.1 refused compacting our small Iceberg tables; INSERT OVERWRITE rewrites (not after partition evolution).',
]
FAQ = [
    ('Where does the compactor run?', 'The initiator and cleaner run in the metastore service; workers can run in the metastore or HiveServer2 depending on version and configuration (<code>hive.compactor.worker.threads</code>). At least one instance must have the initiator and workers enabled, otherwise deltas pile up. In our Docker lab, workers on HiveServer2 also needed the metastore database connection settings.'),
    ('Does compaction block queries?', 'Minor and major compaction do not block reads or writes: readers keep using the old files until the new base or delta is committed, and the cleaner removes old folders only when no reader needs them. Long-running queries or open transactions therefore delay cleaning.'),
    ('Is Iceberg replacing Hive ACID?', 'For new multi-engine data lakes many teams choose Iceberg, because Spark, Trino, Flink and cloud services can all read and write it with the same guarantees. Hive ACID remains common in existing Hive-centric warehouses. Hive 4 supports both, and can migrate Hive tables to Iceberg.'),
    ('What catalog does Hive use for Iceberg tables?', 'By default the Hive Metastore: the table is registered there with a pointer to its current metadata file (metadata_location). Other engines configured with the same metastore (the “hive catalog”) see the same table. Iceberg also supports REST, Glue and other catalogs.'),
    ('What does merge-on-read mean?', 'Updates and deletes write small delete files instead of rewriting data files, which makes writes cheap and reads slightly more expensive until compaction. The alternative, copy-on-write (<code>write.delete.mode=copy-on-write</code>), rewrites affected data files at write time: slower writes, faster reads.'),
]

PRACTICE_INTRO = 'Programs about compaction and Iceberg metadata, with the HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Folders after major compaction', stmt='A partition has 1 base and 7 deltas. How many folders remain after a major compaction (and cleaning)?', inp='1 base + 7 deltas',
         code='''print(1)
''', explain='One new base. Our 2 October partition went from 3 folders to base_0000003.'),
    dict(level='easy', title='Live rows', stmt='Data files hold 5,028 rows; position deletes cover 142. How many rows does COUNT(*) return?', inp='5,028 and 142',
         code='''print(5028 - 142)
''', explain='4,886, the real count of orders_ice before the 5 October load.'),
    dict(level='easy', title='Hidden partition value', stmt='Compute the day and month partition values for an order date.', inp='2026-10-02',
         code='''d = "2026-10-02"
print("order_date_day =", d, " order_date_month =", d[:7])
''', explain='The folder names Iceberg created: order_date_day=2026-10-02 and order_date_month=2026-10.'),
    dict(level='medium', title='Snapshot for a timestamp', stmt='Which snapshot was current at 10:07:10?', inp='snapshots at 10:07:04, 10:07:13, 10:07:14',
         code='''snaps = [("10:07:04", "s1"), ("10:07:13", "s2"), ("10:07:14", "s3")]
t = "10:07:10"
print([s for ts, s in snaps if ts <= t][-1])
''', explain='s1, which is why FOR SYSTEM_TIME AS OF \'2026-10-27 10:07:10\' returned 4,926 rows.'),
    dict(level='medium', title='Compaction candidates', stmt='List partitions with more than 10 deltas.', inp='delta counts per partition',
         code='''deltas = {"2026-10-01": 1, "2026-10-02": 14, "2026-10-03": 2, "2026-10-04": 11}
print([p for p, n in deltas.items() if n > 10])
''', explain="Run ALTER TABLE … PARTITION (order_date='…') COMPACT 'minor' for these, or let the initiator do it."),
    dict(level='medium', title='Expiry cut-off', stmt='Compute the EXPIRE_SNAPSHOTS timestamp for a 7-day retention.', inp='today 2026-10-27',
         code='''from datetime import date, timedelta
print((date(2026, 10, 27) - timedelta(days=7)).isoformat() + " 00:00:00")
''', explain="ALTER TABLE t EXECUTE EXPIRE_SNAPSHOTS('2026-10-20 00:00:00') keeps a week of time travel."),
    dict(level='business', title='Rollback impact', stmt='A bad load added 3,365 rows. Rolling back to the previous snapshot: how many rows remain?', inp='8,251 rows now',
         code='''print(8251 - 3365)
''', explain='4,886, exactly what the real rollback returned.'),
    dict(level='business', title='Choose ACID or Iceberg', stmt='Recommend a table type for each case.', inp='three cases',
         code='''cases = {"Hive-only warehouse, nightly MERGE": "Hive ACID",
         "Spark writes, Hive and Trino read": "Iceberg",
         "Need time travel for audits": "Iceberg"}
for c, r in cases.items():
    print(f"{c:38} -> {r}")
''', explain='Iceberg is the choice when other engines write or when history is needed; Hive ACID works well inside Hive-only platforms.'),
]

SCN_INTRO = 'Compaction and Iceberg are senior-level topics; expect “how does it work” and “what would you choose” questions.'
SCENARIOS = (
    scn('Any company · Hive', 'Fresher', '“What is compaction in Hive?”',
        'Explain compaction and its two types.',
        'do you connect deltas, read cost and cleanup?',
        '<p>Every insert, update and delete on an ACID table adds delta or delete_delta folders; reads must merge them all. Compaction rewrites them: minor merges deltas into one delta; major merges base and deltas into a new base and physically removes deleted rows. It runs automatically when thresholds are crossed, or with ALTER TABLE … COMPACT.</p>', 'Confusing it with ORC/file compression.') +
    scn('Data platform', 'Mid-level', 'Deltas keep growing',
        'An ACID table has 3,000 delta folders and SHOW COMPACTIONS is empty.',
        'can you troubleshoot the compactor?',
        '''<ol>
          <li>Check that the initiator is on (metastore) and that workers exist (<code>hive.compactor.worker.threads</code> &gt; 0 somewhere).</li>
          <li>Check worker logs for connection errors to the metastore database.</li>
          <li>Run a manual major compaction per partition off-peak, then fix the configuration.</li>
        </ol>''', '“Delete the delta folders by hand”, which corrupts the table.') +
    scn('Analytics', 'Mid-level', '“Give me the table as it was last Monday”',
        'An analyst needs last Monday’s state of an Iceberg orders table for an audit.',
        'do you know time travel and its limits?',
        '''<ul>
          <li>Query <code>FOR SYSTEM_TIME AS OF 'Monday 23:59:59'</code> (UTC), or find the snapshot id in <code>db.t.history</code>.</li>
          <li>Check snapshot retention: expired snapshots cannot be read.</li>
          <li>For permanent audit points, create a tag on the snapshot or export the result.</li>
        </ul>''', 'Restoring a backup into a new cluster.') +
    scn('Architecture', 'Senior', 'Lakehouse table design',
        'Design the main orders table for a lakehouse where Spark ingests, Hive and Trino query, and finance needs history.',
        'can you combine Iceberg features into an operable design?',
        '''<ul>
          <li>Iceberg v2 table, <code>PARTITIONED BY SPEC (day(order_ts))</code>, Parquet + ZSTD, sorted by customer for lookups.</li>
          <li>MERGE for corrections; scheduled compaction (rewrite data files) and EXPIRE_SNAPSHOTS with an agreed retention; tag month-end snapshots for finance.</li>
          <li>One shared catalog (Hive Metastore or REST) so every engine sees the same table.</li>
        </ul>''', 'Copying the table into each engine’s own format.')
)
