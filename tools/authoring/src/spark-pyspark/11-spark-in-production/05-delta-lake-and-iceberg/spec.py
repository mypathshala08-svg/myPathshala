import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='11-spark-in-production', lesson='05-delta-lake-and-iceberg', n='11.5',
    module_label='Module 11 · Spark in production',
    title='Delta Lake and Iceberg',
    desc='Delta Lake and Apache Iceberg with PySpark 4.1.1, delta-spark 4.3.1 and Iceberg 1.12.0: the _delta_log transaction log, UPDATE, DELETE and MERGE as versions 0–3, history and versionAsOf time travel, schema enforcement rejecting a string amount and mergeSchema adding a column, and Iceberg hidden partitioning with days(ts), snapshots, VERSION AS OF, column rename and partition evolution without rewriting data.',
    og_desc='UPDATE, MERGE, time travel and schema enforcement on a data lake: Delta Lake and Apache Iceberg with real Spark outputs.',
    minutes=32, level='Intermediate → Advanced',
    lead='<b>Table formats</b> turn Parquet folders into ACID tables. This lesson updates, deletes and merges rows in <b>Delta Lake</b>, reads its history and older versions, tests schema enforcement, and uses <b>Apache Iceberg</b>’s hidden partitioning, snapshots and schema/partition evolution. <b>All outputs are real</b> (PySpark 4.1.1, Delta 4.3.1, Iceberg 1.12.0).',
    chips=['Delta Lake 4.3.1', 'Iceberg 1.12.0', 'MERGE + time travel', 'Runs in your browser (Python)'],
)

MAIN = '''# A transaction log in miniature: each commit lists files added and removed
log = [
    {"v": 0, "op": "WRITE",  "add": ["p0", "p1"], "remove": []},
    {"v": 1, "op": "UPDATE", "add": ["p2"],       "remove": ["p0"]},
    {"v": 2, "op": "DELETE", "add": ["p3"],       "remove": ["p1"]},
]

def files_at(version):
    files = set()
    for c in log:
        if c["v"] > version:
            break
        files |= set(c["add"])
        files -= set(c["remove"])
    return sorted(files)

for v in range(3):
    print("version", v, "->", files_at(v))
'''
RUN = dict(
    heading='Run the code: replaying a transaction log',
    intro='<p>How a reader finds the files of any version. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('        files |= set(c["add"])', 'Replay commits in order: files added become part of the table…'),
        ('        files -= set(c["remove"])', '…and removed files leave it, but stay on disk for time travel until vacuumed.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then add a MERGE commit (add p4, remove p2).', code=None),
        dict(label='2 · Predict first: time travel', hint='<b>Predict first:</b> which files does version 0 need?',
             code='''print(["p0", "p1"], "-> still on disk, so version 0 is readable")
'''),
        dict(label='3 · MERGE logic', hint='Upsert rows by key.',
             code='''table = {1: "DELIVERED", 3: "PLACED"}
updates = {3: "DELIVERED", 4: "PLACED"}
table.update(updates)
print(sorted(table.items()))
'''),
        dict(label='4 · Hidden partition', hint='Partition value from days(ts).',
             code='''ts = "2026-11-02 09:00:00"
print("ts_day=" + ts[:10])
'''),
        dict(label='5 · Spot the error', hint='Appending a string amount to a long column.', expect='error',
             code='''table_type, incoming_type = "long", "string"
assert table_type == incoming_type, "DELTA_FAILED_TO_MERGE_FIELDS: Failed to merge fields 'amount' and 'amount'"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: Delta and Iceberg',
    intro='<p>In a virtualenv with <code>pyspark==4.1.*</code> and <code>delta-spark==4.3.1</code> (Iceberg: add the runtime jar). <b>Outputs are real</b>.</p>',
    items=[
        dict(title='1 · Delta history', cmd='DeltaTable.forPath(spark, P).history().select("version", "operation").show()', file='pyspark',
             output='|0      |WRITE    |\n|1      |UPDATE   |\n|2      |DELETE   |\n|3      |MERGE    |', note='Audit trail.'),
        dict(title='2 · Time travel', cmd='spark.read.format("delta").option("versionAsOf", 0).load(P).count()', file='pyspark',
             output='3', note='Before the changes.'),
        dict(title='3 · Iceberg snapshots', cmd='spark.sql("SELECT operation FROM lake.db.orders.snapshots").show()', file='pyspark',
             output='append\noverwrite\noverwrite', note='UPDATE and DELETE are overwrites.'),
    ],
)

TRACE = dict(
    heading='Atomic commit with optimistic concurrency',
    intro='<p>Two writers race for the next version.</p>',
    code='''latest = 3
writer_a = latest + 1
writer_b = latest + 1
committed = {}
for name, v in (("A", writer_a), ("B", writer_b)):
    if v in committed:
        print(name, "conflict -> retry as", v + 1)
    else:
        committed[v] = name
print(committed)
''',
    notes={2: 'Both :: Read version 3, want to write 4.', 6: 'Conflict :: Only one commit can own version 4.'},
)

WORKED_INTRO = 'Three table-format decisions at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='Delta · basics', title='Upsert daily changes',
         problem='<p>Apply a file of changed orders to the orders table.</p>',
         inp='changes DataFrame',
         approach=['DeltaTable.forPath.', 'merge on order_id.', 'whenMatchedUpdateAll / whenNotMatchedInsertAll.'],
         code='''print("t.alias('t').merge(c.alias('c'), 't.order_id = c.order_id')"
      ".whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()")
''', notes={1: 'Atomic :: One commit.'},
         tryit='Step 2.'),
    dict(level='i', tag='Iceberg · partitions', title='Partition by time',
         problem='<p>Most queries filter on order time.</p>',
         inp='ts column',
         approach=['PARTITIONED BY (days(ts)).', 'Users filter on ts.', 'Evolve to hours(ts) later if needed.'],
         code='''print("CREATE TABLE lake.db.orders (...) USING iceberg PARTITIONED BY (days(ts))")
''', notes={1: 'Hidden :: No derived date column to maintain.'},
         tryit='Step 5.'),
    dict(level='a', tag='Formats · choose', title='Delta or Iceberg?',
         problem='<p>Pick a format for a multi-engine platform.</p>',
         inp='Spark + Trino + Snowflake',
         approach=['List engines and their support.', 'Catalog strategy.', 'Spark version compatibility.'],
         code='''needs = {"Spark": True, "Trino": True, "Snowflake": True}
print("Iceberg (broad multi-engine catalog support)" if needs["Snowflake"] else "either")
''', notes={1: 'Both are open :: Interoperability tools (e.g. UniForm) exist.'},
         tryit='Definition table.'),
]

QUIZ = mix([
    dict(q='Beginner: Where does Delta store its commits?', options=['Hive only', '_delta_log folder', 'Kafka', 'Driver memory'], answer=1,
         why='JSON commits + checkpoints.'),
    dict(q='Beginner: Data files in Delta/Iceberg are…', options=['CSV', 'Parquet (usually)', 'Avro only', 'JSON'], answer=1,
         why='The log adds the table.'),
    dict(q='Beginner: MERGE does…', options=['Only inserts', 'Update matches and insert new rows', 'Deletes all', 'Joins only'], answer=1,
         why='Upsert.'),
    dict(q='Intermediate: Read Delta version 0 with…', options=['option("versionAsOf", 0)', 'spark.history()', 'RDD', 'VACUUM'], answer=0,
         why='Time travel.'),
    dict(q='Intermediate: Appending amount as string to a long column…', options=['Converted', 'Rejected (schema enforcement)', 'Silently null', 'New table'], answer=1,
         why='DELTA_FAILED_TO_MERGE_FIELDS.'),
    dict(q='Intermediate: Add a new column on append in Delta…', options=['Automatic', 'option("mergeSchema", "true")', 'Impossible', 'VACUUM'], answer=1,
         why='Explicit evolution.'),
    dict(q='Advanced: Iceberg hidden partitioning means…', options=['No partitions', 'Partitions derived by transforms like days(ts)', 'Secret folders', 'Only in Delta'], answer=1,
         why='Query ts directly.'),
    dict(q='Advanced: Time travel stops working after…', options=['A restart', 'Old files are vacuumed / snapshots expired', 'A MERGE', 'Adding a column'], answer=1,
         why='Retention.'),
])

REVISION = [
    'Table formats = Parquet files + transactional metadata.',
    'Delta: _delta_log commits; Iceberg: snapshots, manifests, catalog.',
    'UPDATE/DELETE/MERGE are atomic commits (lab versions 0–3).',
    'Time travel: versionAsOf / VERSION AS OF while files are retained.',
    'Schema enforcement rejects wrong types; mergeSchema / ALTER to evolve.',
    'Iceberg hidden partitioning (days(ts)) and partition evolution.',
    'Check format ↔ Spark version compatibility before upgrading.',
]
FAQ = [
    ('What is Delta UniForm?', 'A Delta feature that also writes Iceberg metadata so Iceberg readers can read Delta tables.'),
    ('Do I need Databricks for Delta?', 'No, Delta Lake is open source and works with open-source Spark via delta-spark.'),
    ('What catalog should Iceberg use?', 'Production setups use a REST catalog, Hive Metastore, AWS Glue or Nessie; the Hadoop catalog is for local tests.'),
    ('How do I avoid many small files?', 'Run OPTIMIZE (Delta) or rewrite_data_files (Iceberg) regularly, and size writes well (Lesson 5.3).'),
    ('What about Apache Hudi?', 'Another open table format with strong upsert/CDC features; the concepts are similar.'),
]

PRACTICE_INTRO = 'Programs about table-format concepts.'
PROBLEMS = [
    dict(level='easy', title='Version count', stmt='Versions after WRITE, UPDATE, DELETE, MERGE.', inp='4 ops',
         code='''print(4, "versions: 0..3")
''', explain='One per commit.'),
    dict(level='easy', title='Commit file', stmt='Name of commit 4.', inp='4',
         code='''print(f"{4:020d}.json")
''', explain='Zero-padded.'),
    dict(level='easy', title='Partition value', stmt='days(ts) for 2026-11-03 08:00.', inp='ts',
         code='''print("ts_day=2026-11-03")
''', explain='Hidden partition.'),
    dict(level='medium', title='Replay log', stmt='Files after commits.', inp='add/remove',
         code='''files = set()
for add, rem in [(["a", "b"], []), (["c"], ["a"])]:
    files |= set(add); files -= set(rem)
print(sorted(files))
''', explain='["b", "c"].'),
    dict(level='medium', title='Upsert', stmt='MERGE two dicts by key.', inp='table, updates',
         code='''t = {1: 450, 3: 800}
t.update({3: 800, 4: 120})
print(t)
''', explain='Update + insert.'),
    dict(level='medium', title='Schema check', stmt='Detect type mismatches.', inp='schemas',
         code='''table = {"amount": "long"}
incoming = {"amount": "string"}
print([c for c in incoming if table.get(c) not in (None, incoming[c])])
''', explain='Rejected column.'),
    dict(level='business', title='Rewrite cost', stmt='GB rewritten to fix 1 row in plain Parquet vs Delta.', inp='day 40 GB vs one 128 MB file',
         code='''print(40, "GB vs", 0.128, "GB")
''', explain='Row-level changes touch few files.'),
    dict(level='business', title='Retention storage', stmt='Extra storage for 7 days of history at 5% daily change on 2 TB.', inp='7 × 5% × 2 TB',
         code='''print(round(7 * 0.05 * 2, 2), "TB")
''', explain='Cost of time travel.'),
]

SCN_INTRO = 'Lakehouse table formats are core knowledge for modern data engineers.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“Why Delta Lake?”',
        'What does Delta add to Parquet?',
        'features?',
        '<p>A transaction log that gives ACID commits, row-level UPDATE/DELETE/MERGE, time travel, schema enforcement and evolution, and an audit history, while data stays in Parquet files.</p>', 'Saying Delta is a different file format from Parquet.') +
    scn('Data engineering', 'Mid-level', 'Upserts',
        'Apply daily changes to a 2 TB table.',
        'approach?',
        '''<ul>
          <li>Delta/Iceberg MERGE on the business key.</li>
          <li>Partition/cluster so MERGE touches few files.</li>
          <li>Compact files regularly.</li>
        </ul>''', 'Rewriting the whole table daily.') +
    scn('Data engineering', 'Mid-level', 'Bad overwrite',
        'A job overwrote yesterday’s data with garbage.',
        'recover?',
        '''<ol>
          <li>Find the bad version in history.</li>
          <li>RESTORE / rollback to the previous version.</li>
          <li>Fix the job; review retention settings.</li>
        </ol>''', 'Restoring from manual backups only.') +
    scn('Platform', 'Senior', 'Format choice',
        'Choose a table format for the company lakehouse.',
        'criteria?',
        '''<ul>
          <li>Engines that must read/write; catalog options.</li>
          <li>Spark version compatibility and upgrade cadence.</li>
          <li>Features: MERGE performance, clustering, CDC, governance.</li>
        </ul>''', 'Choosing by popularity alone.')
)
