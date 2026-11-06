import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from hivekit import tables
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return re.sub(r'; Query ID[^\n]*', '', open(CAP + n).read().rstrip())
BODY = body(HERE)

META = dict(
    module='11-hive-in-industry', lesson='03-lakehouse-and-migration', n='11.3',
    module_label='Module 11 · Hive in industry today',
    title='Lakehouse and migration: moving Hive tables to Iceberg',
    desc='Migrate real Hive tables to Apache Iceberg in Hive 4.2.1: an in-place migration that rewrote no data files, a transactional table refused and copied with CTAS so that Hive and Trino finally agree on 5,000,001 rows, partition evolution from daily to monthly without rewriting, DELETE and UPDATE as snapshots, time travel and rollback seen immediately in Trino, stray files ignored even after MSCK, and the cost of in-place versus copy migration on 5 million rows. Plus Iceberg, Delta Lake and Hudi in 2026.',
    og_desc='Same files, new metadata: an in-place Hive-to-Iceberg migration that rewrote zero data files, and an ACID table that finally gives one answer in Hive and Trino.',
    minutes=50, level='Intermediate → Advanced',
    lead='The problems from Lessons 11.1 and 11.2 (different answers per engine, MSCK, rename-based commits) are why companies move Hive tables to an open table format. This lesson migrates real tables from our Hive 4.2.1 lab to <b>Apache Iceberg</b>, in place and by copy, then evolves, changes, time-travels and rolls them back, checking every result in Trino. <b>All outputs are real.</b>',
    chips=['Hive 4.2.1 · Iceberg 1.9.1 · Trino 476', '0 data files rewritten', 'One answer in every engine', 'Runs in your browser (Python)'],
)

MAIN = '''# Plan a migration: which tables can convert in place?
tables = [
    ("orders_mig",  "external", "parquet"),
    ("orders_big",  "external", "orc"),
    ("orders_tx",   "managed",  "orc, transactional"),
    ("raw_events",  "external", "textfile"),
]
for name, kind, fmt in tables:
    in_place = kind == "external" and fmt.split(",")[0] in ("parquet", "orc", "avro")
    print(f"{name:11} {'in place' if in_place else 'copy (CTAS)':12}  {kind}, {fmt}")
'''
RUN = dict(
    heading='Run the code: planning and validating a migration',
    intro='<p>These programs model the decisions and checks of a Hive-to-Iceberg migration with the real numbers from the lab. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    in_place = kind == "external" and fmt.split(",")[0] in ("parquet", "orc", "avro")', 'Hive refused the transactional table in Step 4; text files are not an Iceberg data format.'),
        ('    ("orders_tx",   "managed",  "orc, transactional"),', 'The ACID table from Modules 7–11: copied with CTAS.'),
    ],
    tasks=[
        dict(label='1 · Plan the tables', hint='Press <b>Run</b>. Add a managed non-ACID Parquet table and see which path it gets.', code=None),
        dict(label='2 · Validate before and after', hint='Compare the baseline from Step 1 with the result after Step 2.',
             code='''before = {"n": 11631, "amt": 3415600.00}
after  = {"n": 11631, "amt": 3415600.00}
print("valid" if before == after else f"MISMATCH {before} vs {after}")
'''),
        dict(label='3 · Predict first: rows after DELETE', hint='<b>Predict first:</b> 23,382 rows, then 106 deleted. How many after the rollback?',
             code='''rows, deleted = 23382, 106
print("after delete:", rows - deleted)
print("after rollback to the snapshot before the delete:", rows)
'''),
        dict(label='4 · Months since 1970', hint='Iceberg stored the monthly partition as 681. Check it.',
             code='''y, m = 2026, 10
print((y - 1970) * 12 + (m - 1))
'''),
        dict(label='5 · Spot the error', hint='This validation compares only counts. A changed amount slips through.', expect='error',
             code='''hive  = {"n": 23276, "amt": 6869400.00}
trino = {"n": 23276, "amt": 6869390.00}
ok = hive["n"] == trino["n"]            # bug: only counts
assert ok == (hive == trino), "compare sums (checksums) too, not just counts"
print("ok")
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: inspect the Iceberg table',
    intro='<p>More from the migrated table. <b>Outputs are real</b> (Hive 4.2.1, Iceberg 1.9.1).</p>',
    items=[
        dict(title='1 · Partitions from Iceberg metadata', cmd='SHOW PARTITIONS orders_mig;', file='beeline',
             output=capf('l113_parts.txt'),
             note='Hive lists both specs: seven daily partitions and the monthly one. They come from Iceberg’s manifests, not from metastore partition rows.'),
        dict(title='2 · Snapshot lineage', cmd='SELECT snapshot_id, parent_id, operation\nFROM tiffingo.orders_mig.snapshots ORDER BY committed_at;', file='beeline',
             output='\n'.join(capf('l113_snaps2.txt').split('\n')[:8]),
             note='Each snapshot points to its parent. After the rollback the last two are kept, but they are no longer ancestors of the current state, until snapshot expiry removes them.'),
        dict(title='3 · The copied ACID table in Trino', cmd='SELECT COUNT(*) AS n FROM iceberg.tiffingo.orders_tx_ice;', file='trino',
             output='\n'.join(capf('l113_trino.txt').split('\n')[4:]),
             note='Compare 5,000,004 from the ACID original in Lesson 11.1.'),
    ],
)

TRACE = dict(
    heading='Why the copied table gives one answer',
    intro='<p>Follow what CTAS does with the ACID table’s base, deltas and delete deltas.</p>',
    code='''base = 5_000_000
inserted = 4      # 999000001, 999000002, 999000010 NEW, 999000010 CANCELLED
deleted = 3       # two DELETEs + old version from the UPDATE
ctas_rows = base + inserted - deleted          # Hive applies deletes while reading
print("rows written to Iceberg:", ctas_rows)
print("delete files in the new table: 0, so every engine reads", ctas_rows)
''',
    notes={1: 'Base :: The original 5 million rows in Hive ACID base files.', 4: 'CTAS :: Hive reads the ACID table correctly and writes plain Parquet.', 6: 'One answer :: No Hive-specific deltas remain for other engines to misread.'},
)

WORKED_INTRO = 'Three migration decisions from real platforms.'
EXAMPLES = [
    dict(level='b', tag='Data engineering · migration', title='Migrate one external table',
         problem='<p>Convert an external Parquet table to Iceberg with validation.</p>',
         inp='tiffingo.orders_mig',
         approach=['Record count and sum.', 'Migrate in place.', 'Compare.'],
         code='''for sql in ["SELECT COUNT(*), SUM(amount) FROM orders_mig;   -- baseline",
            "ALTER TABLE orders_mig SET TBLPROPERTIES ('storage_handler'='org.apache.iceberg.mr.hive.HiveIcebergStorageHandler');",
            "SELECT COUNT(*), SUM(amount) FROM orders_mig;   -- must match"]:
    print(sql)
''', notes={2: 'In place :: Metadata only; data files stay where they are.'},
         tryit='Run the same validation query in Trino through the iceberg catalog.'),
    dict(level='i', tag='Data engineering · ACID', title='Copy an ACID table with a name swap',
         problem='<p>Replace a Hive ACID table with an Iceberg copy that keeps its name.</p>',
         inp='orders_tx (full ACID)',
         approach=['CTAS into a new table.', 'Validate.', 'Rename old and new in one window.'],
         code='''steps = ["CREATE TABLE orders_tx_ice STORED BY ICEBERG STORED AS PARQUET AS SELECT * FROM orders_tx;",
         "-- validate: COUNT(*) and SUM(amount) in Hive and Trino",
         "ALTER TABLE orders_tx RENAME TO orders_tx_old;",
         "ALTER TABLE orders_tx_ice RENAME TO orders_tx;"]
print("\\n".join(steps))
''', notes={3: 'Window :: Stop writers between the CTAS and the rename, or replay their changes.'},
         tryit='Keep orders_tx_old until every consumer has run on the new table for a full cycle.'),
    dict(level='a', tag='Architecture · cost', title='Estimate a migration programme',
         problem='<p>Estimate cluster hours for migrating a warehouse, using the lab’s rates as a rough guide.</p>',
         inp='600 TB external, 120 TB ACID (illustrative)',
         approach=['In place: per table, not per TB.', 'Copy: proportional to data.', 'Add validation reads.'],
         code='''external_tables, acid_tb = 650, 120
copy_tb_per_hour = 2            # assumed cluster throughput
in_place_hours = external_tables * 1 / 60    # ~1 minute per table incl. validation
copy_hours = acid_tb / copy_tb_per_hour
print(f"in place: {in_place_hours:.0f} h   copy: {copy_hours:.0f} h")
''', notes={3: 'Throughput :: Measure on your own cluster; the lab is far too small to extrapolate.'},
         tryit='Validation (count + sum per partition) often costs more than the in-place migration itself.'),
]

QUIZ = mix([
    dict(q='Beginner: What does an in-place migration to Iceberg change?', options=['It rewrites all data files', 'It adds Iceberg metadata around the existing files', 'It moves data to HDFS', 'Nothing'], answer=1,
         why='0 data files rewritten in Step 2.'),
    dict(q='Beginner: Which statement migrates an external table in place in Hive 4?', options=['CONVERT TABLE t TO ICEBERG', "ALTER TABLE … SET TBLPROPERTIES with the Iceberg storage_handler", 'MSCK REPAIR TABLE t', 'DROP TABLE t'], answer=1,
         why='The storage handler property triggers the migration.'),
    dict(q='Beginner: Which is NOT an open table format?', options=['Apache Iceberg', 'Delta Lake', 'Apache Hudi', 'Parquet'], answer=3,
         why='Parquet is a file format; table formats organise files.'),
    dict(q='Intermediate: Why was the ACID table copied instead of migrated?', options=['Too large', 'Hive refuses to convert transactional tables; their delta files are Hive-specific', 'Wrong format', 'No permission'], answer=1,
         why='“Converting … transactional hive table to iceberg table is not allowed.”'),
    dict(q='Intermediate: What did Trino return for the copied table?', options=['5,000,004', '5,000,001, the same as Hive', '0', 'An error'], answer=1,
         why='No Hive deltas remain to misread.'),
    dict(q='Intermediate: What happened to old files after SET PARTITION SPEC (month(order_date))?', options=['Rewritten monthly', 'They kept the old daily spec; new data used the monthly spec', 'Deleted', 'Moved'], answer=1,
         why='Partition evolution affects new writes only.'),
    dict(q='Advanced: A file was copied into the migrated table’s folder and MSCK was run. Result?', options=['New rows appear', 'Count unchanged: only manifest-listed files belong to the table', 'Error', 'Duplicate partitions'], answer=1,
         why='Opposite of the plain table in Lesson 11.2.'),
    dict(q='Advanced: What does EXECUTE ROLLBACK change?', options=['Deletes data files', 'Points the table at an older snapshot', 'Restores a backup', 'Drops the table'], answer=1,
         why='Trino saw 23,382 immediately.'),
])

REVISION = [
    '<b>Lakehouse</b> = open files + open table format (Iceberg, Delta, Hudi) + shared catalogue.',
    '<b>In place</b>: <code>SET TBLPROPERTIES</code> with the Iceberg <code>storage_handler</code> on external Parquet/ORC/Avro tables: metadata only, 0 files rewritten.',
    '<b>ACID</b> tables are refused; copy with <code>CTAS … STORED BY ICEBERG</code>. Then Hive and Trino agree (5,000,001).',
    'Validate with count <b>and</b> sum, before and after, in every engine.',
    'Partition evolution: <code>SET PARTITION SPEC</code>; old files keep the old spec, nothing is rewritten.',
    'DML creates snapshots with delete files; time travel with <code>FOR SYSTEM_VERSION AS OF</code>; undo with <code>EXECUTE ROLLBACK</code>.',
    'Only manifest-listed files belong to the table: writers must commit through Iceberg.',
    'Cost: in place 4.4 s vs CTAS 16.7 s for 5M rows in the lab; copy cost grows with data.',
]
FAQ = [
    ('Can I go back after an in-place migration?', 'Not with a single built-in statement in our version. Because the data files are unchanged, you can recreate a plain external table on the same location as an emergency path, but files written after the migration may live in new folders and contain delete files. Test on a copy and keep the old DDL.'),
    ('Iceberg, Delta or Hudi?', 'For Hive users Iceberg is the natural choice: Hive 4 supports it natively and Trino, Spark, Flink and the big cloud warehouses read it. Delta Lake fits Databricks-centred platforms; Hudi is strong for CDC upserts. Interoperability layers such as Delta UniForm and Apache XTable reduce lock-in.'),
    ('Do I still need the Hive metastore?', 'Iceberg needs a catalogue to store the current metadata pointer. The Hive metastore is one option and is already there after a Hive migration; REST catalogues such as Apache Polaris, AWS Glue or Unity Catalog are others.'),
    ('What about snapshot growth?', 'Every commit adds a snapshot and files. Schedule snapshot expiry and compaction (Lesson 7.3) so storage and planning time stay under control, while keeping enough history for rollback.'),
    ('Why did Spark not appear in this lesson?', 'In Lesson 11.1, Spark 3.5’s Iceberg catalog could not talk to the Hive 4 metastore because of the metastore client version. With a compatible client or a REST catalogue, Spark reads the same Iceberg tables.'),
]

PRACTICE_INTRO = 'Programs for migration checks, with the SQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Migration statement', stmt='Generate the in-place migration statement for a table.', inp='orders_big',
         code='''t = "orders_big"
print(f"ALTER TABLE {t} SET TBLPROPERTIES ('storage_handler'='org.apache.iceberg.mr.hive.HiveIcebergStorageHandler');")
''', explain='Only for external Parquet, ORC or Avro tables.'),
    dict(level='easy', title='Rows after DML', stmt='Compute rows after the DELETE and UPDATE in Step 6.', inp='23,382 rows, 106 deleted, 1 updated',
         code='''print(23382 - 106 + 1 - 1)
''', explain='An update deletes one row version and adds one: count unchanged.'),
    dict(level='easy', title='Time-travel query', stmt='Write a time-travel query for a snapshot ID.', inp='8935160337224414664',
         code='''print("SELECT COUNT(*) FROM orders_mig FOR SYSTEM_VERSION AS OF 8935160337224414664;")
''', explain='FOR SYSTEM_TIME AS OF \'…\' works with a timestamp instead.'),
    dict(level='medium', title='Path chooser', stmt='Choose in place or copy for each table.', inp='table properties',
         code='''for name, external, transactional, fmt in [("a", True, False, "orc"), ("b", False, True, "orc"), ("c", True, False, "textfile")]:
    ok = external and not transactional and fmt in ("orc", "parquet", "avro")
    print(name, "in place" if ok else "copy")
''', explain='Text tables need a copy because Iceberg data files are Parquet, ORC or Avro.'),
    dict(level='medium', title='Partition validation', stmt='Compare per-partition counts before and after.', inp='two dictionaries',
         code='''before = {"2026-10-01": 1641, "2026-10-02": 1617}
after  = {"2026-10-01": 1641, "2026-10-02": 1617}
print([d for d in before if before[d] != after.get(d)] or "all partitions match")
''', explain='SELECT order_date, COUNT(*), SUM(amount) … GROUP BY order_date, in each engine.'),
    dict(level='medium', title='Find the rollback target', stmt='Pick the last snapshot before the first delete.', inp='snapshot list',
         code='''snaps = [("6356967414929367428", "append"), ("8935160337224414664", "append"),
         ("7700454950423225386", "delete"), ("7073719229572187090", "overwrite")]
target = None
for sid, op in snaps:
    if op == "delete":
        break
    target = sid
print("ALTER TABLE orders_mig EXECUTE ROLLBACK(" + target + ");")
''', explain='Verify the target with time travel before rolling back.'),
    dict(level='business', title='Storage during a copy', stmt='Extra storage while old and new tables coexist.', inp='120 TB ACID data, 30 days overlap',
         code='''tb, days, per_tb_month = 120, 30, 2000   # illustrative ₹ per TB-month
print(f"₹{tb * per_tb_month * days / 30:,.0f} for the overlap period")
''', explain='In-place migration avoids this cost entirely.'),
    dict(level='business', title='Incident time saved', stmt='Hours saved per bad load with rollback instead of restore.', inp='restore 6 h, rollback 0.25 h, 8 incidents a year',
         code='''print((6 - 0.25) * 8, "hours per year")
''', explain='Plus fewer wrong dashboards while the restore runs.'),
]

SCN_INTRO = 'Lakehouse and migration questions are common for senior data roles in 2026.'
SCENARIOS = (
    scn('Any company · lakehouse', 'Fresher', '“What is a lakehouse?”',
        'Explain a lakehouse and where Hive fits.',
        'do you know table formats?',
        '<p>Data stays in open files (Parquet/ORC) in a lake or object store; a table format such as Iceberg adds transactions, snapshots, schema and partition evolution; a shared catalogue lets Hive, Spark, Trino and others use the same tables. Hive 4 creates and queries Iceberg tables natively and its metastore can be the catalogue.</p>', 'Saying a lakehouse is a product you buy.') +
    scn('Data engineering', 'Mid-level', 'Migrate a Hive table to Iceberg',
        'An external ORC table of 50 TB must become Iceberg with minimal downtime.',
        'do you know in-place migration?',
        '''<ol>
          <li>Record per-partition counts and sums.</li>
          <li>Migrate in place with the Iceberg storage handler: metadata only, no data copy.</li>
          <li>Validate in every engine, then switch writers to Iceberg-aware commits.</li>
        </ol>''', 'Copying 50 TB with CTAS when in place is possible.') +
    scn('Platform', 'Mid-level', 'Rows written but not visible',
        'After migration, an upstream job’s new files do not appear in queries.',
        'do you understand manifests?',
        '''<ul>
          <li>The job still writes files into folders; Iceberg ignores files not in its manifests (MSCK does not help).</li>
          <li>Change the job to write through Spark, Flink, Hive or Trino with the Iceberg catalogue.</li>
          <li>Short-term: register files with an add_files procedure after validating their schema.</li>
        </ul>''', 'Running MSCK REPAIR again.') +
    scn('Architecture', 'Senior', 'Plan a warehouse-to-lakehouse migration',
        '800 Hive tables, 150 ACID, Spark and Trino users, cloud move planned.',
        'can you sequence the work?',
        '''<ul>
          <li>Inventory; waves: external in place, ACID by copy with name swap; catalogue choice (HMS vs REST) up front.</li>
          <li>Automated validation per partition in every engine; maintenance jobs for snapshot expiry and compaction.</li>
          <li>Combine with the cloud move: Iceberg removes rename-based commits on object storage.</li>
        </ul>''', 'Migrating everything in one weekend without validation.')
)
