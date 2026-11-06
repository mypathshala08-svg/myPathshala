import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
D = 'l115_delta.txt'
I = 'l115_iceberg.txt'
def dsec(a, b=None):
    return capsec(D, a, b)
def isec(a, b=None):
    return capsec(I, a, b, drop=('scan filter pushed',))

def layers(x, y, fmt='Delta'):
    log = '_delta_log/*.json' if fmt == 'Delta' else 'metadata.json → manifests'
    o = opbox(x, y, 'table: orders', 'name in a catalog', 'blue', 330, 26)
    o += opbox(x, y + 34, 'transaction log / metadata', log, 'violet', 330, 30)
    o += ''.join(opbox(x + k * 84, y + 72, f'part-{k}.parquet', 'data file', 'green', 78, 30) for k in range(4))
    return o

# ---------------------------------------------------------------- story
sc_ = (layers(14, 22) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured (Delta 4.3 / Iceberg 1.12)', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('UPDATE/DELETE/MERGE: OK', 'green'), ('history: 4 versions', 'green'),
           ('wrong type: rejected', 'red'), ('new column: mergeSchema', 'amber'),
           ('Iceberg: days(ts) hidden', 'blue'), ('time travel: 450 → 500', 'violet')])))
scene_svg = scene('Delta Lake and Apache Iceberg add a transaction log on top of Parquet files, turning a folder into a table with ACID updates, history, time travel and schema rules. We updated, deleted and merged rows, travelled back in time, broke and evolved schemas, and used Iceberg’s hidden partitioning.', sc_,
                  'Parquet stores the data; the <tspan font-weight="700" class="s-acc">log</tspan> makes it a table.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“We need to fix one order in a 2 TB folder”</h2>
  <div class="story">
    <p class="narration">A customer asked TiffinGo to correct one order’s status. The orders lived in plain Parquet files: to change one row, the team rewrote a whole day’s partition, and a reader ran during the rewrite and saw half the data. The same month, a job appended amounts as strings and broke every dashboard.</p>

{scene_svg}

K> Sir, Parquet is great. Why does it not support UPDATE?
A> Parquet files are immutable, and a folder of them has no idea which files belong together. <b>Table formats</b> like Delta Lake and Apache Iceberg add a log of commits: each change writes new files and then atomically records “these files are now the table”.
R> And readers never see half a change?
A> Exactly: ACID transactions on a data lake, plus history, time travel and schema checks. Today we try both formats. Neither supports Spark 4.3 yet, so this lab runs PySpark 4.1.1 with delta-spark 4.3.1 and Iceberg 1.12.0. All outputs are real.
  </div>
</section>
'''

lv = '''
LEVELS> Table formats at three levels
L1> A register at the library
      <ul>
        <li>Books (Parquet files) never change; a register lists which books are on the shelf right now.</li>
        <li>To “edit” a book, you add a corrected copy and change the register in one stroke. Old register pages let you see the shelf as it was last week (time travel).</li>
      </ul>
L2> The API
      <ul>
        <li>Delta: <code>df.write.format("delta").save(path)</code>, <code>DeltaTable.forPath(spark, path)</code> with <code>.update()</code>, <code>.delete()</code>, <code>.merge()</code>, <code>.history()</code>; read <code>option("versionAsOf", n)</code>.</li>
        <li>Iceberg: catalog config, then SQL: <code>CREATE TABLE … USING iceberg PARTITIONED BY (days(ts))</code>, <code>UPDATE</code>, <code>DELETE</code>, <code>MERGE INTO</code>, <code>VERSION AS OF</code>, metadata tables like <code>t.snapshots</code>.</li>
        <li>Schema: Delta <code>mergeSchema</code>; Iceberg <code>ALTER TABLE … ADD/RENAME COLUMN</code>, <code>ADD PARTITION FIELD</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>Delta recorded WRITE, UPDATE, DELETE and MERGE as versions 0–3; version 0 is still readable.</li>
        <li>Appending <code>amount</code> as a string was rejected; a new column needed <code>mergeSchema</code>.</li>
        <li>Iceberg created <code>ts_day=…</code> folders from <code>days(ts)</code>, travelled back to a snapshot, and changed its partitioning without rewriting old data.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Delta Lake and Apache Iceberg</h2>
''' + def_block(
    '<b>Open table formats</b> store table data as Parquet files in object storage and add <b>metadata</b> that defines which files form each version of the table. <b>Delta Lake</b> keeps an ordered <b>transaction log</b> (<code>_delta_log/</code> JSON commits with periodic checkpoints); <b>Apache Iceberg</b> keeps a tree of metadata files, manifest lists and manifests, referenced by a catalog. Writers commit new versions atomically with optimistic concurrency, giving <b>ACID transactions</b>, row-level <code>UPDATE</code>/<code>DELETE</code>/<code>MERGE</code> (by rewriting or marking affected files), <b>time travel</b> to earlier versions or snapshots, <b>schema enforcement</b> and controlled <b>schema evolution</b>. Iceberg adds <b>hidden partitioning</b> (partition transforms such as <code>days(ts)</code> derived from columns) and partition evolution. Both integrate with Spark through connector packages and SQL extensions.',
    'Delta Lake and Iceberg turn folders of Parquet files into real tables. A log records every change, so you can update and delete rows safely, readers never see half-finished writes, you can read older versions, and wrong data types are rejected.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Table format', 'Metadata layer over data files.'),
    ('Transaction log', 'Ordered list of commits (Delta).'),
    ('Snapshot', 'Table state at one commit (Iceberg).'),
    ('ACID', 'All-or-nothing, isolated commits.'),
    ('MERGE', 'Upsert: update matches, insert new.'),
    ('Time travel', 'Read an earlier version.'),
    ('Schema enforcement', 'Reject mismatched writes.'),
    ('Hidden partitioning', 'Partitions derived from a column.'),
]) + '''

  <h3>Plain Parquet vs Delta vs Iceberg</h3>
''' + table(['Feature', 'Parquet folder', 'Delta Lake', 'Apache Iceberg'], [
    ['ACID commits', 'No', 'Yes (_delta_log)', 'Yes (metadata + catalog)'],
    ['UPDATE / DELETE / MERGE', 'Rewrite by hand', 'Yes', 'Yes'],
    ['Time travel', 'No', '<code>versionAsOf</code>, <code>timestampAsOf</code>', '<code>VERSION AS OF</code> snapshot'],
    ['Schema enforcement', 'No', 'Yes; <code>mergeSchema</code> to evolve', 'Yes; ALTER TABLE'],
    ['Partitioning', 'Folders you manage', 'Columns (+ liquid clustering)', 'Hidden transforms, evolvable'],
    ['Engines', 'All', 'Spark, Databricks, Trino, …', 'Spark, Trino, Flink, Snowflake, …'],
], minw=640) + lv + '''
EXAM> “Why use Delta Lake or Iceberg instead of plain Parquet?” They add a transactional metadata layer: atomic commits (no partial reads), row-level updates/deletes/merges, time travel, schema enforcement and evolution, and efficient metadata-based pruning. Delta uses an ordered JSON transaction log; Iceberg uses snapshots with manifests and a catalog, and adds hidden partitioning and partition evolution.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Setting them up in Spark</h2>
''' + table(['Format', 'Package', 'Session config'], [
    ['Delta Lake', '<code>pip install delta-spark</code> (matches Spark minor version)', '<code>spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension</code>, <code>spark.sql.catalog.spark_catalog=…DeltaCatalog</code>'],
    ['Iceberg', '<code>iceberg-spark-runtime-&lt;spark&gt;_2.13</code> jar', '<code>spark.sql.extensions=…IcebergSparkSessionExtensions</code>, <code>spark.sql.catalog.lake=…SparkCatalog</code> + type/warehouse'],
], minw=640) + '''
WARN> Table formats are tied to Spark versions. When we built this lesson, the newest Delta (4.4.1) supported Spark 4.2 and the newest Iceberg runtime targeted Spark 4.1, while PySpark was at 4.3. Platforms usually lag the newest Spark for this reason; check the compatibility matrix before upgrading Spark. Also, time travel only works while old files exist: <code>VACUUM</code> (Delta) and <code>expire_snapshots</code> (Iceberg) delete them.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Delta, then Iceberg</h2>
  <p>All outputs are real: PySpark 4.1.1 in a separate virtualenv, delta-spark 4.3.1 and iceberg-spark-runtime-4.1 1.12.0 (Iceberg Hadoop catalog on local disk), <code>local[2]</code>.</p>
''' + stepper([
    ('Step 1 · A Delta table is Parquet + a log',
     code('python', 'l115_delta.py', 'o.write.format("delta").save(P)\nprint(sorted(os.listdir(P)))\nprint(sorted(os.listdir(P + "/_delta_log")))', dsec('PySpark 4.1.1', '== 2)')),
     'The data is ordinary Parquet; what makes it a table is <code>_delta_log/00000000000000000000.json</code>, commit number 0, listing those files. Any reader that understands Delta reads the log first and then only the files it names.'),
    ('Step 2 · UPDATE, DELETE and MERGE',
     code('python', 'l115_delta.py', 't = DeltaTable.forPath(spark, P)\nt.update("order_id = 1", {"status": F.lit("DELIVERED")})\nt.delete("order_id = 2")\n(t.alias("t").merge(upd.alias("u"), "t.order_id = u.order_id")\n  .whenMatchedUpdateAll().whenNotMatchedInsertAll().execute())', dsec('== 2)', '== 3)')),
     'Row-level changes on a data lake: order 1 delivered, order 2 deleted, order 3 updated and order 4 inserted by one <b>MERGE</b> (an upsert). Each operation wrote new files and one new commit; readers saw either the old or the new table, never a mix.'),
    ('Step 3 · History and time travel',
     code('python', 'l115_delta.py', 't.history().select("version", "operation", "operationParameters.predicate").show()\nspark.read.format("delta").option("versionAsOf", 0).load(P)', dsec('== 3)', '== 4)')),
     'Four versions, each with its operation and predicate: an audit trail for free. <code>versionAsOf</code> 0 reads the table before any change (all three orders PLACED). Both versions have 3 rows, but different ones.'),
    ('Step 4 · Schema enforcement and evolution',
     code('python', 'l115_delta.py', 'bad.write.format("delta").mode("append").save(P)            # amount as string\nextra.write.format("delta").mode("append").save(P)          # new column payment\nextra.write.format("delta").mode("append").option("mergeSchema", "true").save(P)', dsec('== 4)')),
     'The string <code>amount</code> was <b>rejected</b>: exactly the dashboard-breaking append from the story. A new column was also refused until we said <code>mergeSchema</code>; then the table gained <code>payment</code> and commit 4 recorded the new metadata.'),
    ('Step 5 · Iceberg: hidden partitioning',
     code('sql', 'l115_iceberg.py', "CREATE TABLE lake.db.orders (order_id BIGINT, city STRING, amount BIGINT, ts TIMESTAMP)\n  USING iceberg PARTITIONED BY (days(ts));\nSELECT * FROM lake.db.orders WHERE ts >= TIMESTAMP'2026-11-02 00:00:00';", isec('== 1)', '== 3)')),
     'We partitioned by a <b>transform</b> of <code>ts</code>; Iceberg created <code>ts_day=…</code> folders itself. Queries filter on <code>ts</code> as usual, with no extra date column to remember, and Iceberg uses partition metadata to read only the matching file (1 of 2).'),
    ('Step 6 · Iceberg snapshots and evolution',
     code('sql', 'l115_iceberg.py', "UPDATE lake.db.orders SET amount = 500 WHERE order_id = 1;\nDELETE FROM lake.db.orders WHERE order_id = 2;\nSELECT … FROM lake.db.orders.snapshots;\nSELECT * FROM lake.db.orders VERSION AS OF <first snapshot>;\nALTER TABLE lake.db.orders ADD COLUMN payment STRING;\nALTER TABLE lake.db.orders RENAME COLUMN amount TO amount_rs;\nALTER TABLE lake.db.orders ADD PARTITION FIELD city;", isec('== 3)')),
     'Every change is a snapshot, queryable as a table. Time travel showed order 1 at ₹450 before the update. Then we added and <b>renamed</b> columns and added <code>city</code> to the partitioning without rewriting old files: old data stays under spec 0, new data (Thane) lands under <code>ts_day=…/city=…</code> with spec 1.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([("files: _delta_log, part-00000…parquet", W), ("_delta_log: 00000000000000000000.json", G)], size=7.0),
    term([('1 Pune  450 DELIVERED', G), ('3 Delhi 800 DELIVERED', G), ('4 Thane 120 PLACED', G), ('versions: WRITE UPDATE DELETE MERGE', W)], size=7.0),
    term([('amount as string ->', W), ('DELTA_FAILED_TO_MERGE_FIELDS', RD), ('new column -> METADATA_MISMATCH', Y), ('mergeSchema -> payment added', G)], size=7.0),
    term([('ts_day=2026-11-01, ts_day=2026-11-02', G), ('first snapshot: (1, 450)', W), ('now: (1, 500)', G), ('partition specs: [1, 0]', Y)], size=7.0),
]
B1 = [
    t(180, 14, 'Files + log = table', 9.4, bold=True) + layers(14, 34) + cap('Readers follow the log.', '', 'blue', y=144, h=30),
    t(180, 14, 'A change = new files + 1 commit', 9.4, bold=True) + flow([('write', 'new files', 'green'), ('commit', '0003.json', 'violet'), ('readers', 'see v3', 'blue')], y=50, w=96, gap=16) + cap('Atomic: old or new, never half.', '', 'green', y=144, h=30),
    t(180, 14, 'The schema is a contract', 9.4, bold=True) + opbox(20, 46, 'amount: long', 'table schema', 'green', 140, 34) + t(180, 66, '≠', 14, 'red') + opbox(200, 46, 'amount: string', 'incoming', 'red', 140, 34) + cap('Rejected unless you evolve it.', '', 'red', y=144, h=30),
    t(180, 14, 'Hidden partitions', 9.4, bold=True) + opbox(20, 46, 'WHERE ts >= …', 'user query', 'blue', 140, 34) + arrow(162, 63, 196, 63, 'ink3', 1.1) + opbox(200, 46, 'days(ts)', 'ts_day=2026-11-02', 'violet', 140, 34) + cap('Pruning without extra columns.', '', 'green', y=144, h=30),
]
see_caps = ['A Delta table.', 'Row-level changes.', 'Schema rules.', 'Iceberg.']
behind_caps = ['Transaction log.', 'Atomic commits.', 'Enforcement.', 'Partition transforms.']
two = anim_two('Delta Lake and Iceberg', 'Tables on a data lake', 'Real lab outputs', 'What the format does', see, B1, see_caps, behind_caps)

e1 = (t(180, 22, 'Correct one order’s status', 9.4, bold=True) + t(180, 56, 'plain Parquet: rewrite a day', 8.4, 'ink2') + cap('Readers saw half.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Convert to Delta/Iceberg', 9.4, bold=True) + t(180, 56, 'CONVERT TO DELTA / migrate', 8.4, 'ink2') + cap('Same Parquet files.', '', 'green', y=150, h=34))
e3 = (t(180, 22, 'UPDATE … WHERE order_id', 9.4, bold=True) + t(180, 56, 'one commit', 8.4, 'ink2') + cap('Atomic.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'GDPR delete requests', 9.4, bold=True) + t(180, 56, 'DELETE WHERE customer_id = …', 8.2, 'ink', mono=True) + cap('Then VACUUM.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Audit via history', 9.4, 'acc', bold=True) + t(180, 56, 'who changed what, when', 8.4, 'ink2') + cap('Built in.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Fixing one row safely',
              'Row-level changes on a data lake. (Typical; operations from our lab.)',
              'Row updates', 'Table formats make UPDATE, DELETE and MERGE atomic on lake storage', [e1, e2, e3, e4, e5],
              ['Rewrite.', 'Convert.', 'UPDATE.', 'DELETE.', 'Audit.'],
              hid='scenario-update')
b1 = (t(180, 22, 'CDC from the orders database', 9.4, bold=True) + t(180, 56, 'inserts, updates, deletes', 8.4, 'ink2') + cap('Stream from Kafka.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'foreachBatch + MERGE', 9.4, bold=True) + t(180, 56, 'match on order_id', 8.4, 'ink2') + cap('Upsert each batch.', '', 'green', y=150, h=34))
b3 = (t(180, 22, 'Idempotent by design', 9.4, bold=True) + t(180, 56, 'replayed batch = same result', 8.4, 'ink2') + cap('Lesson 9.5.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Lake mirrors the database', 9.4, bold=True) + t(180, 56, 'minutes behind', 8.4, 'ink2') + cap('Analytics-ready.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Compact small files', 9.4, 'acc', bold=True) + t(180, 56, 'OPTIMIZE / rewrite_data_files', 8.4, 'ink', mono=True) + cap('Keep reads fast.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Mirroring a database into the lake',
              'Streaming MERGE into table formats. (Typical.)',
              'CDC MERGE', 'Streaming CDC data is merged into Delta or Iceberg tables batch by batch', [b1, b2, b3, b4, b5],
              ['CDC.', 'MERGE.', 'Idempotent.', 'Mirror.', 'Compact.'],
              hid='scenario-cdc')
u1 = (t(180, 22, 'Bad job overwrote orders', 9.4, bold=True) + t(180, 56, 'at 03:10 last night', 8.4, 'ink2') + cap('Dashboards wrong.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Look at history', 9.4, bold=True) + t(180, 56, 'version 4812 = bad write', 8.4, 'ink2') + cap('Find the commit.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'RESTORE TABLE … VERSION 4811', 9.4, bold=True) + t(180, 56, 'or Iceberg rollback_to_snapshot', 8.2, 'ink2') + cap('Minutes, not days.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Rerun the fixed job', 9.4, bold=True) + t(180, 56, 'new version on top', 8.4, 'ink2') + cap('History kept.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Retention matters', 9.4, 'acc', bold=True) + t(180, 56, 'VACUUM removes old files', 8.4, 'ink2') + cap('Keep enough days.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Undoing a bad write',
              'Time travel and rollback. (Typical; time travel from our lab.)',
              'Rollback', 'Table history lets you find and roll back a bad write while old files are retained', [u1, u2, u3, u4, u5],
              ['Bad write.', 'History.', 'Restore.', 'Rerun.', 'Retention.'],
              hid='scenario-restore')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Tables on a data lake</h2>
  <p>Left: real outputs. Right: what the table format does.</p>
''' + two + '''
  <p>Three live scenarios follow: fixing one row, mirroring a database, and undoing a bad write.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Table formats at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'lake', 12, 'blue', bold=True) + t(60, 58, 'house', 7.4, 'ink2'),
    '1. Lakehouse tables',
    'Bronze/silver/gold tables in Delta or Iceberg replace a separate warehouse for many workloads.',
    ['Raw', '*Delta/Iceberg', 'Gold tables']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'GDPR', 12, 'green', bold=True) + t(60, 58, 'deletes', 7.4, 'ink2'),
    '2. Privacy deletes',
    'Customer deletion requests become DELETE statements plus file cleanup.',
    ['Request', '*DELETE + VACUUM', 'Compliant']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'CDC', 12, 'violet', bold=True) + t(60, 58, 'MERGE', 7.4, 'ink2'),
    '3. CDC mirrors',
    'Database changes stream into lake tables with MERGE.',
    ['Debezium', '*MERGE', 'Lake copy']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'multi', 11, 'acc', bold=True) + t(60, 58, 'engine', 7.4, 'ink2'),
    '4. Many engines, one table',
    'Spark writes, Trino and Snowflake read the same Iceberg tables.',
    ['Spark write', '*Iceberg catalog', 'Trino read']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'audit', 12, 'acc', bold=True) + t(60, 58, 'history', 7.4, 'ink2'),
    '5. Audits and ML',
    'Time travel reproduces the exact training data of a past model.',
    ['Model v3', '*VERSION AS OF', 'Same data']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> Parquet in <a href="../../05-reading-and-writing-data/02-parquet-orc-and-avro/">5.2</a>, writing and small files in <a href="../../05-reading-and-writing-data/03-writing-data-and-small-files/">5.3</a>, tables and catalogs in <a href="../../07-spark-sql/02-tables-catalog-and-hive-metastore/">7.2</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
