import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return re.sub(r'; Query ID[^\n]*', '', open(CAP + n).read().rstrip())

def opbox(x, y, label, sub='', tone='card', w=128, h=26):
    o = box(x, y, w, h, tone) + t(x + w / 2, y + (11 if sub else 16), label, 7.2, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 21, sub, 6.4, 'ink2', mono=True)
    return o

SHOW = '''CREATE EXTERNAL TABLE `orders_mig`( … `order_date` date)
PARTITIONED BY SPEC (`order_date`)
ROW FORMAT SERDE 'org.apache.iceberg.mr.hive.HiveIcebergSerDe'
STORED BY 'org.apache.iceberg.mr.hive.HiveIcebergStorageHandler'
LOCATION 'file:/opt/hive/data/warehouse/tiffingo.db/orders_mig'
TBLPROPERTIES (
  'MIGRATED_TO_ICEBERG'='true',
  'current-snapshot-summary'='{"added-data-files":"7","added-records":"11631", … "iceberg-version":"Apache Iceberg 1.9.1 …"}',
  'format-version'='2',
  'metadata_location'='file:/…/orders_mig/metadata/00001-dec3245f-….metadata.json',
  'schema.name-mapping.default'='[ {"field-id" : 1, "names" : [ "order_id" ]}, … ]',
  'table_type'='ICEBERG',
  'write.delete.mode'='merge-on-read',
  'write.format.default'='parquet',
  'write.update.mode'='merge-on-read', …)'''

# ---------------------------------------------------------------- story
sc = (opbox(14, 22, 'Hive tables today', 'external · ACID · 11 years', 'blue', 150, 30) + opbox(14, 70, 'Problems', 'MSCK · 3 engines, 3 counts', 'amber', 150, 30) +
      arrow(166, 50, 236, 66, 'acc', 1.8) +
      box(240, 40, 140, 60, 'green') + t(310, 62, 'Iceberg tables', 8.6, bold=True) + t(310, 80, 'same files, new metadata', 7.2, 'ink2', mono=True) +
      box(410, 12, 222, 128, 'card') + t(521, 30, 'What the migration showed', 8.6, bold=True) +
      ''.join(t(422, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([('in place: 0 data files rewritten', 'green'), ('ACID: refused → CTAS', 'amber'), ('Trino now 5,000,001 (was 5,000,004)', 'green'), ('new partition spec, no rewrite', 'green'), ('rollback in one statement', 'green')])))
scene_svg = scene('TiffinGo moves its Hive tables to Apache Iceberg. External tables convert in place by adding metadata; transactional tables have to be copied. Afterwards Hive and Trino agree.', sc,
                  'Migration changes the <tspan font-weight="700" class="s-acc">metadata</tspan>, not necessarily the data.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Can we fix this without copying 200 TB?”</h2>
  <div class="story">
    <p class="narration">After Lessons 11.1 and 11.2, TiffinGo’s platform team has a list: Spark sees an empty orders table, Trino overcounts, files dropped into S3 need MSCK, and commits on object storage copy every file. The architects propose a lakehouse on Apache Iceberg. The first question from management is about cost.</p>

{scene_svg}

K> Sir, do we have to rewrite all our tables to use Iceberg?
A> Not all. Iceberg keeps the data in ordinary Parquet, ORC or Avro files and adds its own <b>metadata</b>: snapshots, manifests and a schema with column IDs. For an external table, Hive 4 can write that metadata around the existing files: an <b>in-place migration</b>.
R> And transactional tables?
A> Those carry Hive’s delta and delete-delta folders, which Iceberg does not understand, so they must be <b>copied</b>. Today we migrate both kinds in our Hive 4.2.1 lab, evolve the partitioning, change rows, travel back in time, roll back, and check every result in Trino. All outputs are real.
  </div>
</section>
'''

lv = '''
LEVELS> Lakehouse migration at three levels
L1> A new index for the same library
      <ul>
        <li>The books (data files) stay on the shelves. Iceberg writes a new, exact index of which books belong to the table.</li>
        <li>Every change creates a new version of the index, so you can open yesterday’s version.</li>
        <li>A book placed on the shelf without updating the index is not part of the table.</li>
      </ul>
L2> The two migration paths in Hive 4
      <ul>
        <li><b>In place</b>: <code>ALTER TABLE t SET TBLPROPERTIES ('storage_handler'=…)</code> with Hive’s Iceberg storage handler class, for <b>external</b> Parquet, ORC or Avro tables. Metadata only.</li>
        <li><b>Copy</b>: <code>CREATE TABLE … STORED BY ICEBERG AS SELECT …</code> (or INSERT into a new table) for managed ACID tables, other formats, or when you also want a new layout.</li>
        <li>After either path: validate counts and sums in every engine, then switch readers and writers.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>In-place migration added 4 metadata files and rewrote <b>0</b> data files; the counts were identical.</li>
        <li>The ACID table was refused (“Converting … transactional hive table to iceberg table is not allowed”); CTAS gave 5,000,001 rows, and Trino now agreed.</li>
        <li>After migration, files copied into the folder stayed invisible even after <code>MSCK REPAIR</code>: only Iceberg’s manifests define the table.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Lakehouse tables and migrating Hive to Iceberg</h2>
''' + def_block(
    'A <b>lakehouse</b> stores data in open file formats in a data lake or object store and adds an <b>open table format</b>, such as Apache Iceberg, Delta Lake or Apache Hudi, that provides warehouse features: atomic commits, row-level changes, schema and partition evolution, snapshots and time travel, readable by many engines through a shared catalogue. <b>Migrating Hive tables to Iceberg</b> means creating Iceberg metadata for a table, either around its existing data files (in-place migration, possible for external Parquet, ORC and Avro tables) or by rewriting the data into a new Iceberg table (copy migration, required for Hive ACID tables), followed by validation and switching every reader and writer to the Iceberg table.',
    'A lakehouse keeps data in open files and adds a table format such as Iceberg for transactions and history. Hive external tables can become Iceberg tables in place; ACID tables must be copied.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Table format', 'Rules and metadata that turn files into a table: Hive layout, Iceberg, Delta, Hudi.'),
    ('Snapshot', 'One committed version of an Iceberg table.'),
    ('Manifest', 'An Avro file listing data files and their statistics.'),
    ('Name mapping', 'Maps column names in old files to Iceberg column IDs after migration.'),
    ('Partition spec', 'How Iceberg partitions data; can change without rewriting old data.'),
    ('Position delete', 'A small file marking deleted rows by file and position (merge-on-read).'),
    ('Time travel', 'Querying an older snapshot: FOR SYSTEM_VERSION AS OF.'),
    ('REST catalog', 'A standard HTTP API for Iceberg catalogues (Polaris, Glue, Unity …).'),
]) + '''

  <h3>Hive table layout versus Iceberg, as seen in the lab</h3>
''' + table(['Question', 'Hive layout (external / ACID)', 'Iceberg', 'Seen in our lab'], [
    ['Which files belong to the table?', 'Every file in the partition folders', 'Only files listed in the current snapshot’s manifests', 'Copied file ignored even after MSCK'],
    ['Where are partitions?', 'Metastore partition list', 'Iceberg metadata; spec can change', 'Daily spec + monthly spec in one table'],
    ['Deletes and updates', 'ACID delta / delete-delta folders, Hive-specific', 'Position or equality delete files, open spec', 'Hive and Trino both 5,000,001'],
    ['History', 'None (ACID: until compaction)', 'Snapshots, time travel, rollback', '4 snapshots, rollback in one statement'],
    ['Commit on object storage', 'Rename-based (11.2)', 'Swap one metadata pointer', '—'],
], minw=780) + lv + '''
EXAM> “How do you migrate a Hive table to Iceberg?” External Parquet/ORC/Avro tables in place by setting the storage_handler table property to Hive’s Iceberg storage handler, which only writes metadata. Managed ACID tables with CTAS … STORED BY ICEBERG. Then validate counts and checksums in every engine and move readers and writers.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Table formats and migration options</h2>
  <p>Status as of October 2026 from the projects’ release pages.</p>
''' + table(['Format', 'Origin', 'Strengths', 'Hive support', 'Notes (2026)'], [
    ['Apache Iceberg', 'Netflix → Apache', 'Engine-neutral spec, hidden partitioning, partition evolution, REST catalog', 'Native in Hive 4 (<code>STORED BY ICEBERG</code>; our lab bundles Iceberg 1.9.1)', 'Iceberg 1.11 (May 2026); spec v3 adds deletion vectors, row lineage, variant type'],
    ['Delta Lake', 'Databricks → Linux Foundation', 'Deep Spark/Databricks integration, Unity Catalog', 'Read via connectors, not native', 'Delta 4.1 (March 2026); UniForm can expose Iceberg metadata'],
    ['Apache Hudi', 'Uber → Apache', 'Upserts, incremental pulls, record indexes', 'Hive can read via Hudi’s input formats', 'Strong in CDC-heavy pipelines'],
    ['Hive ACID', 'Hive', 'MERGE, compaction, materialized views', 'Native', 'Hive-only reliably (11.1)'],
], minw=820) + table(['Migration method', 'Rewrites data?', 'Use when', 'Lab result'], [
    ['In place (<code>SET TBLPROPERTIES storage_handler</code>)', 'No', 'External Parquet / ORC / Avro tables', '5M rows in 4.4 s, 0 files rewritten'],
    ['CTAS / INSERT into a new Iceberg table', 'Yes', 'ACID tables, text/other formats, new layout or sort', '5M rows in 16.7 s'],
    ['Snapshot / add_files procedures (Spark)', 'No', 'Test a copy of the metadata first; register existing files', 'Not run in this lab'],
    ['Dual-write, then cut over', 'Yes', 'Critical tables with zero downtime', 'Typical practice'],
], minw=760) + '''
WARN> In-place migration changes the table for <b>every</b> engine at once. Engines without Iceberg support (Spark without the Iceberg runtime, older tools reading folders directly) stop seeing correct data, and writers that still drop files into folders write into the void. Migrate readers and writers in the same change window.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Migrating real tables, checking every number</h2>
  <p>All outputs are real: Hive 4.2.1 with its bundled Iceberg 1.9.1, and Trino 476 from Lesson 11.1 reading through its <code>iceberg</code> catalog on the same metastore.</p>
''' + stepper([
    ('Step 1 · A typical external Hive table',
     code('sql', 'beeline', "CREATE EXTERNAL TABLE orders_mig (\n  order_id INT, customer_id INT, city STRING, amount DECIMAL(10,2), status STRING)\nPARTITIONED BY (order_date DATE) STORED AS PARQUET\nLOCATION '/opt/hive/data/warehouse/tiffingo.db/orders_mig';\nINSERT OVERWRITE TABLE orders_mig PARTITION (order_date)\nSELECT order_id, customer_id, city, amount, status, order_date FROM orders\nWHERE order_date BETWEEN '2026-10-01' AND '2026-10-07';\nSELECT COUNT(*) AS n, SUM(amount) AS amt FROM orders_mig;", capf('l113_base.txt')),
     'Seven daily partitions, one Parquet file each. We record the count and the sum <b>before</b> migrating: these two numbers are the validation baseline.'),
    ('Step 2 · Migrate in place',
     code('sql', 'beeline, then list the folder', "ALTER TABLE orders_mig SET TBLPROPERTIES (\n  'storage_handler'='org.apache.iceberg.mr.hive.HiveIcebergStorageHandler');\nSELECT COUNT(*) AS n, SUM(amount) AS amt FROM orders_mig;", capf('l113_migrate.txt') + '\n\n$ find orders_mig -type f\n' + capf('l113_files.txt')),
     'Identical numbers. The seven data files were not touched; Hive added a <code>metadata/</code> folder with two metadata JSON files, one manifest and one manifest list. That is the whole migration. The partition folders keep their old names; Iceberg no longer needs them, because the manifests list every file.'),
    ('Step 3 · What the table definition became',
     code('sql', 'beeline (shortened)', 'SHOW CREATE TABLE orders_mig;', SHOW),
     'The storage handler and SerDe are Iceberg’s, the partition is now a <code>PARTITIONED BY SPEC</code>, and the first snapshot records 7 files and 11,631 rows. <code>format-version 2</code> allows row-level deletes; <code>merge-on-read</code> writes small delete files instead of rewriting data. <code>schema.name-mapping.default</code> lets Iceberg read the old Parquet files, which have column names but no Iceberg field IDs.'),
    ('Step 4 · ACID tables cannot migrate in place',
     code('sql', 'beeline · trino', "ALTER TABLE orders_tx SET TBLPROPERTIES (\n  'storage_handler'='org.apache.iceberg.mr.hive.HiveIcebergStorageHandler');\n\nCREATE TABLE orders_tx_ice STORED BY ICEBERG STORED AS PARQUET AS SELECT * FROM orders_tx;\nSELECT COUNT(*) AS n FROM orders_tx_ice;\nSELECT order_id, status FROM orders_tx_ice WHERE order_id > 999000000 ORDER BY order_id;\n\n-- Trino\nSELECT COUNT(*) AS n FROM iceberg.tiffingo.orders_tx_ice;", capf('l113_acid_mig.txt') + '\n\n' + capf('l113_ctas.txt') + '\n\n-- Trino\n' + '\n'.join(capf('l113_trino.txt').split('\n')[4:])),
     'Hive refused to convert the transactional table. The copy did what Lesson 11.1 could not: Hive applied all deletes and updates while reading, so the new table has 5,000,001 rows with order 999000010 once, CANCELLED. <b>Trino now returns 5,000,001 too</b>, where it returned 5,000,004 from the ACID table. One table format, one answer.'),
    ('Step 5 · Change the partitioning without rewriting',
     code('sql', 'beeline', "ALTER TABLE orders_mig SET PARTITION SPEC (month(order_date));\nINSERT INTO orders_mig SELECT order_id, customer_id, city, amount, status, order_date\nFROM orders WHERE order_date BETWEEN '2026-10-08' AND '2026-10-14';\n\nSELECT spec_id, `partition`, record_count FROM tiffingo.orders_mig.files ORDER BY spec_id, record_count;", capf('l113_evolve_files.txt')),
     'Seven small daily files stay in spec 0; the new week went into one monthly file under spec 1 (<code>681</code> is months since 1970, i.e. October 2026). Queries filtering on <code>order_date</code> prune both layouts, because Iceberg partitions are <b>hidden</b>: users never write the partition column. In plain Hive, changing the partition scheme means rewriting the whole table. (<code>partition</code> is a reserved word, hence the backticks.)'),
    ('Step 6 · Row-level changes become snapshots',
     code('sql', 'beeline', "DELETE FROM orders_mig WHERE status = 'CANCELLED' AND order_date = '2026-10-03';\nUPDATE orders_mig SET amount = amount + 10\nWHERE order_id = (SELECT MIN(order_id) FROM orders_mig WHERE order_date = '2026-10-10');\n\nSELECT snapshot_id, operation, summary['added-records'] AS added,\n       summary['deleted-records'] AS deleted, summary['added-position-deletes'] AS pos_del\nFROM tiffingo.orders_mig.snapshots ORDER BY committed_at;", capf('l113_dml.txt') + '\n\n' + capf('l113_snaps.txt')),
     'DML works on the migrated table, with no <code>transactional</code> property. The DELETE wrote one position-delete file for 106 rows; the UPDATE wrote one new row and one position delete. Four snapshots: migration, the new week, the delete and the update. 23,382 − 106 = 23,276 rows.'),
    ('Step 7 · Time travel, rollback, and Trino agrees',
     code('sql', 'beeline · trino', "SELECT COUNT(*) AS n, SUM(amount) AS amt FROM orders_mig FOR SYSTEM_VERSION AS OF 8935160337224414664;\n-- Trino, before the rollback\nSELECT COUNT(*) AS n, SUM(amount) AS amt FROM iceberg.tiffingo.orders_mig;\n\nALTER TABLE orders_mig EXECUTE ROLLBACK(8935160337224414664);\nSELECT COUNT(*) AS n, SUM(amount) AS amt FROM orders_mig;\nSELECT snapshot_id, is_current_ancestor FROM tiffingo.orders_mig.history;\n-- Trino, after\nSELECT COUNT(*) AS n FROM iceberg.tiffingo.orders_mig;", capf('l113_tt.txt') + '\n\n-- Trino, before the rollback\n' + '\n'.join(capf('l113_trino.txt').split('\n')[:4]) + '\n\n' + capf('l113_rollback.txt') + '\n' + capf('l113_snaps2.txt').split('\n', 8)[-1] + '\n\n-- Trino, after\n' + capf('l113_trino_rb.txt')),
     'Time travel read the state before the DELETE: 23,382 rows. Trino saw the current state with exactly Hive’s count and sum. The rollback moved the table pointer back; the history shows the DELETE and UPDATE snapshots as no longer ancestors, and Trino immediately read 23,382. Undoing a bad load is one statement, not a restore from backup.'),
    ('Step 8 · The folder is no longer the table',
     code('bash', 'copy a file into a new folder, then beeline', "cp orders_mig/order_date=2026-10-01/000000_0 orders_mig/order_date=2026-10-15/000000_0\n\nMSCK REPAIR TABLE orders_mig;\nSELECT COUNT(*) AS n FROM orders_mig;", capf('l113_stray.txt')),
     'In Lesson 11.2, a file copied into a new folder became visible after MSCK. Here it stays invisible: Iceberg reads only the files listed in its manifests. That protects the table from half-written or stray files, but it means every writer must commit through an Iceberg-aware engine. Upstream jobs that “just drop files” must change during the migration.'),
    ('Step 9 · What each migration path costs',
     code('sql', 'beeline (orders_big, 5,000,000 rows)', "-- in place, on an external ORC copy\nALTER TABLE ob_copy SET TBLPROPERTIES ('storage_handler'='org.apache.iceberg.mr.hive.HiveIcebergStorageHandler');\n-- copy\nCREATE TABLE ob_ctas STORED BY ICEBERG STORED AS ORC AS SELECT * FROM orders_big;", capf('l113_cost.txt')),
     'Both tables returned 5,000,000 rows. The in-place migration took about one second beyond Beeline’s start-up, because it only writes metadata; the copy reads and writes every row, so its cost grows with the data. At 200 TB the difference is hours of cluster time and double storage until the old table is dropped. Use in place where you can, copy where you must.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('ALTER TABLE orders_mig SET TBLPROPERTIES', W), ("  ('storage_handler'='…HiveIcebergStorageHandler')", W), ('11631 · 3415600.00 (before and after)', G), ('+4 metadata files, 0 data files rewritten', G)], size=6.8),
    term([('ALTER TABLE orders_tx … storage_handler', W), ('Converting … transactional … not allowed', RD), ('CTAS STORED BY ICEBERG → 5000001', G), ('Trino: 5000001 (was 5000004)', G)], size=7.0),
    term([('SET PARTITION SPEC (month(order_date))', W), ('spec 0: 7 daily files', Y), ('spec 1: 1 monthly file, 11751 rows', G), ('old files not rewritten', G)], size=7.2),
    term([('delete     pos_del 106', Y), ('overwrite  added 1, pos_del 1', Y), ('EXECUTE ROLLBACK(8935…)', W), ('Hive 23382 · Trino 23382', G)], size=7.2),
    term([('cp … order_date=2026-10-15/', W), ('MSCK REPAIR TABLE orders_mig', W), ('COUNT(*) → 23382 (unchanged)', Y), ('only manifests define the table', G)], size=7.2),
]
def lay(hi):
    o = ''
    for k, (name, sub, x, y) in enumerate([('metadata.json', 'current pointer', 20, 30), ('manifests', 'list of files', 20, 92), ('data files', 'Parquet / ORC', 230, 62)]):
        o += opbox(x, y, name, sub, 'acc' if k == hi else ['amber', 'violet', 'green'][k], 110, 30)
    o += arrow(132, 45, 132, 90, 'ink3', 1.4) + arrow(132, 107, 228, 80, 'ink3', 1.4)
    return o
B1 = [
    t(180, 22, 'Metadata around existing files', 9.4, bold=True) + lay(0) + cap('In place: new index, same files.', '', 'green', y=140, h=34),
    t(180, 22, 'ACID deltas need Hive to read', 9.4, bold=True) + lay(2) + cap('So ACID tables are copied, not converted.', '', 'amber', y=140, h=34),
    t(180, 22, 'Each file remembers its spec', 9.4, bold=True) + lay(1) + cap('Old and new layouts coexist.', '', 'violet', y=140, h=34),
    t(180, 22, 'A commit swaps the pointer', 9.4, bold=True) + lay(0) + cap('Rollback = point to an older snapshot.', '', 'blue', y=140, h=34),
    t(180, 22, 'Unlisted files do not exist', 9.4, bold=True) + lay(1) + cap('Writers must commit through Iceberg.', '', 'amber', y=140, h=34),
]
see_caps = ['In-place migration: same numbers, only metadata added.',
            'ACID refused; the copy gives one answer in Hive and Trino.',
            'New partition layout for new data only.',
            'Changes are snapshots; rollback is instant.',
            'A copied file stays invisible.']
behind_caps = ['The manifest lists the seven existing files.',
               'Delete deltas are Hive-specific; CTAS applies them.',
               'Manifests store each file’s partition spec ID.',
               'The catalogue points at a new metadata.json.',
               'Iceberg plans from manifests, not folders.']
two = anim_two('Migrating to Iceberg', 'Same files, new metadata', 'Real lab outputs', 'Inside the Iceberg table', see, B1, see_caps, behind_caps)

# ---- scenario 1: phased migration
e1 = (t(180, 22, '800 Hive tables', 9.4, bold=True) + t(180, 56, '650 external · 150 ACID', 8.4, 'ink2') + cap('Inventory first.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Wave 1: external, read-mostly', 9.4, bold=True) + t(180, 56, 'in place, metadata only', 8.4, 'ink2') + cap('Minutes per table.', '', 'green', y=150, h=34))
e3 = (t(180, 22, 'Wave 2: ACID tables', 9.4, bold=True) + t(180, 56, 'CTAS into new tables, swap names', 8.2, 'ink2') + cap('Plan storage and time.', '', 'amber', y=150, h=34))
e4 = (t(180, 22, 'Validate every table', 9.4, bold=True) + t(180, 56, 'COUNT + SUM per partition, all engines', 8.2, 'ink2') + cap('Like Steps 1, 2 and 7.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Move writers last', 9.4, 'acc', bold=True) + t(180, 56, 'no more “drop files into folders”', 8.2, 'ink2') + cap('Step 8 is the reason.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'A migration in waves',
              'How platform teams migrate hundreds of tables. (Typical plan; numbers illustrative.)',
              'Phased migration', 'Inventory tables, migrate external ones in place, copy ACID ones, validate in every engine and switch writers', [e1, e2, e3, e4, e5],
              ['Know what you have.',
               'Cheap wins first.',
               'Copy what must be copied.',
               'Prove the numbers.',
               'Change the writers.'],
              hid='scenario-waves')

# ---- scenario 2: bad load, rollback
b1 = (t(180, 22, '06:10 · dashboard doubled', 9.4, bold=True) + t(180, 56, 'nightly job loaded the same day twice', 8.2, 'ink2') + cap('A classic incident.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Find the last good snapshot', 9.4, bold=True) + t(180, 56, 'SELECT … FROM t.snapshots', 8.4, 'ink', mono=True) + cap('Before the bad append.', '', 'green', y=150, h=34))
b3 = (t(180, 22, 'Check it with time travel', 9.4, bold=True) + t(180, 56, 'FOR SYSTEM_VERSION AS OF …', 8.4, 'ink', mono=True) + cap('Counts look right.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Roll back', 9.4, bold=True) + t(180, 56, 'ALTER TABLE t EXECUTE ROLLBACK(…)', 8.2, 'ink', mono=True) + cap('All engines see it at once.', '', 'green', y=150, h=34))
b5 = (t(180, 22, '06:25 · fixed', 9.4, 'acc', bold=True) + t(180, 56, 'then fix the job and reload', 8.2, 'ink2') + cap('No backup restore.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Undoing a bad load in fifteen minutes',
              'What Step 7 looks like during an incident. (Typical timeline.)',
              'Snapshot rollback', 'Find the last good snapshot, verify it with time travel and roll back; every engine sees the fix immediately', [b1, b2, b3, b4, b5],
              ['Wrong numbers on a dashboard.',
               'List snapshots.',
               'Check the old state.',
               'Roll back.',
               'Fix the job.'],
              hid='scenario-rollback')

# ---- scenario 3: catalogue choice
u1 = (t(180, 22, 'Which catalogue?', 9.4, bold=True) + t(180, 56, 'Hive metastore, Glue, Polaris, Unity …', 8.2, 'ink2') + cap('Every engine must use the same one.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Keep the Hive metastore', 9.4, bold=True) + t(180, 56, 'Hive, Spark, Trino, Flink support it', 8.2, 'ink2') + cap('Simplest after a Hive migration.', '', 'green', y=150, h=34))
u3 = (t(180, 22, 'Or an Iceberg REST catalog', 9.4, bold=True) + t(180, 56, 'Apache Polaris (top-level, Feb 2026)', 8.2, 'ink2') + cap('Vendor-neutral, credential vending.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Watch client versions', 9.4, bold=True) + t(180, 56, 'Spark’s Iceberg catalog failed in 11.1', 8.2, 'ink2') + cap('Test every engine.', '', 'amber', y=150, h=34))
u5 = (t(180, 22, 'Hive stays useful', 9.4, 'acc', bold=True) + t(180, 56, 'SQL ETL on Iceberg, metastore for all', 8.2, 'ink2') + cap('Hive as one lakehouse engine.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Choosing the lakehouse catalogue',
              'The decision that comes right after the table format. (Options as of 2026.)',
              'Catalogue choice', 'Keep the Hive metastore or adopt an Iceberg REST catalog; either way every engine must use the same catalogue and be tested', [u1, u2, u3, u4, u5],
              ['One catalogue for all.',
               'HMS: already there.',
               'REST: the new standard.',
               'Versions matter.',
               'Hive keeps a role.'],
              hid='scenario-catalog')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Same files, new metadata</h2>
  <p>Left: real outputs. Right: what happens inside the Iceberg table.</p>
''' + two + '''
  <p>Three live scenarios follow: a migration in waves, a rollback during an incident, and choosing the catalogue.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Lakehouses at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'in place', 10, 'green', bold=True) + t(60, 58, 'migration', 7.4, 'ink2'),
    '1. Converting a Hive warehouse',
    'Companies with large Hive estates convert external tables in place and copy ACID tables, table by table.',
    ['Hive tables', '*Iceberg', 'Same files']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'engines', 10, 'blue', bold=True) + t(60, 58, 'one answer', 7.4, 'ink2'),
    '2. One table, many engines',
    'Spark writes, Trino serves dashboards, Hive runs SQL ETL and Flink streams into the same Iceberg tables.',
    ['Writers', '*Iceberg', 'Readers']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'undo', 12, 'violet', bold=True) + t(60, 58, 'snapshots', 7.4, 'ink2'),
    '3. Recovering from bad loads',
    'Snapshots, time travel and rollback replace many restore-from-backup procedures.',
    ['Bad load', '*rollback', 'Good data']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'GDPR', 12, 'acc', bold=True) + t(60, 58, 'deletes', 7.4, 'ink2'),
    '4. Row-level deletes for compliance',
    'Erasure requests become DELETE statements with delete files, compacted later, in every engine consistently.',
    ['Request', '*DELETE', 'Compacted']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'warehouse', 9, 'acc', bold=True) + t(60, 58, 'sharing', 7.4, 'ink2'),
    '5. Sharing with cloud warehouses',
    'Snowflake, BigQuery, Redshift and Databricks read Iceberg tables through catalogues, without copying data.',
    ['Lake tables', '*catalogue', 'Warehouses']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> Iceberg basics (<a href="../../07-acid-and-iceberg/03-compaction-and-iceberg/">7.3</a>), the multi-engine test (<a href="../01-hive-spark-and-trino/">11.1</a>) and object storage (<a href="../02-hive-in-the-cloud/">11.2</a>).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
