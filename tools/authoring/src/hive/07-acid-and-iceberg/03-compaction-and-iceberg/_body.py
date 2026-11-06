import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()

def fol(x, y, label, tone='card', w=100, h=22, size=6.6):
    return box(x, y, w, h, tone) + t(x + w / 2, y + h / 2 + 3, label, size, 'ink', mono=True, bold=True)

# ---------------------------------------------------------------- story
sc = (box(10, 12, 300, 128, 'card') + t(160, 30, 'Hive ACID: compaction', 8.8, bold=True) +
      ''.join(fol(22 + (k % 4) * 70, 42 + (k // 4) * 26, f'delta_{k + 1}', 'acc', 64) for k in range(8)) +
      arrow(160, 96, 160, 108, 'green', 2) + fol(110, 110, 'base_0000010', 'green', 100) +
      box(330, 12, 300, 128, 'green') + t(480, 30, 'Iceberg: snapshots', 8.8, 'green', bold=True) +
      ''.join(box(346 + k * 70, 50, 60, 28, 'blue' if k < 3 else 'acc') + t(376 + k * 70, 68, f'snap {k + 1}', 7.4, 'ink', bold=True) + (arrow(406 + k * 70, 64, 416 + k * 70, 64, 'ink3') if k < 3 else '') for k in range(4)) +
      t(480, 100, 'FOR SYSTEM_VERSION AS OF snap 1', 7.6, 'ink', mono=True) + t(480, 120, 'time travel · rollback · evolution', 7.6, 'green', bold=True))
scene_svg = scene('On the left, eight small delta folders of a Hive ACID table are compacted into one base folder. On the right, an Iceberg table keeps a chain of snapshots that can be queried in the past, rolled back and evolved.', sc,
                  'Hive ACID cleans up with <tspan font-weight="700" class="s-acc">compaction</tspan>; Iceberg tracks every change as a <tspan font-weight="700" class="s-acc">snapshot</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“The customer table has 11 delta folders, and data science wants last week’s data back”</h2>
  <div class="story">
    <p class="narration">After a week of updates, Kabir’s ACID tables are full of small delta folders. At the same time the data science team, which works in Spark, asks two things Hive ACID cannot easily give: a table they can also write from Spark, and “the orders table exactly as it was before yesterday’s correction”.</p>

{scene_svg}

K> Sir, who cleans up all these delta folders?
A> The <b>compactor</b>. Minor compaction merges deltas into one delta; major compaction rewrites everything into a new <code>base</code>. It runs on its own when thresholds are crossed, or when you ask with <code>ALTER TABLE … COMPACT</code>.
R> And the request for last week’s data?
A> That is what <b>Apache Iceberg</b> is built for. Hive 4 creates Iceberg tables with <code>STORED BY ICEBERG</code>. Every change becomes a <b>snapshot</b> you can query (time travel) or return to (rollback), partitions can change without rewriting data, and Spark, Trino and Flink read and write the same table. Today we do both, on real data, including two things Hive 4.2.1 refused. All outputs are real.
  </div>
</section>
'''

lv = '''
LEVELS> Compaction and Iceberg at three levels
L1> Tidying up and keeping photos
      <ul>
        <li><b>Compaction</b> is tidying a drawer full of sticky notes: you copy everything onto one clean page and throw the notes away.</li>
        <li><b>Iceberg</b> keeps a photo of the table after every change. You can look at an old photo (time travel) or decide the old photo is the truth again (rollback).</li>
        <li>Both exist because files in a data lake are never edited, only added.</li>
      </ul>
L2> How each works
      <ul>
        <li><b>Hive ACID compaction:</b> <i>minor</i> merges delta (and delete_delta) folders into one; <i>major</i> merges base + deltas into a new <code>base_N</code>, physically removing deleted rows. The metastore’s <b>initiator</b> queues compactions when thresholds are crossed (for example more than 10 deltas, <code>hive.compactor.delta.num.threshold</code>), <b>workers</b> run them, and a <b>cleaner</b> removes the old folders.</li>
        <li><b>Iceberg table:</b> data files (Parquet by default in Hive 4) plus a <b>metadata tree</b>: metadata.json (schema, partition specs, snapshots) → manifest list per snapshot → manifests listing data files and their statistics.</li>
        <li><b>Hidden partitioning:</b> <code>PARTITIONED BY SPEC (day(order_date))</code>. Queries filter on <code>order_date</code>, and Iceberg prunes; no extra partition column.</li>
        <li>Iceberg v2 tables support UPDATE, DELETE and MERGE with <b>merge-on-read</b> delete files.</li>
      </ul>
L3> What we saw in Hive 4.2.1
      <ul>
        <li>ACID compaction needed the compactor configured on HiveServer2 and the metastore (in our Docker lab we had to give HiveServer2 the metastore database connection). Then the initiator compacted an 11-delta table on its own; a manual MINOR on the same table was <b>refused</b> (“None of the compaction thresholds met”).</li>
        <li>Iceberg defaults: format version 2, Parquet with ZSTD, merge-on-read, Iceberg 1.9.1.</li>
        <li>Snapshot summaries count rows in data files: after deleting 40 rows <code>total-records</code> stayed 5,028 because the delete is a separate position-delete file.</li>
        <li>Partition evolution worked without rewriting old files, but afterwards <code>INSERT OVERWRITE</code> was refused until data is rewritten to the new spec.</li>
        <li>Hive’s built-in Iceberg compaction refused our small test tables (“doesn’t meet requirements for compaction”); a manual rewrite with INSERT OVERWRITE merged 16 files into 1.</li>
        <li>EXPIRE_SNAPSHOTS removed old snapshots (and with them, time travel to those points).</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Compaction and Apache Iceberg</h2>
''' + def_block(
    '<b>Compaction</b> is the background process that rewrites a transactional table’s delta and delete-delta files into fewer files: <b>minor compaction</b> combines deltas into a single delta per bucket, and <b>major compaction</b> combines the base and all deltas into a new base, physically removing deleted rows. <b>Apache Iceberg</b> is an open table format for large analytic tables: a table is a set of immutable data files described by versioned metadata (metadata files, manifest lists and manifests). Each committed change creates a new <b>snapshot</b>, which enables <b>time travel</b>, <b>rollback</b>, <b>schema evolution</b> and <b>partition evolution</b>, with hidden partitioning and concurrent access from multiple engines.',
    'Compaction tidies an ACID table by merging its many small change files. Iceberg is a newer way to store tables: it records every change as a snapshot, so you can look at the table as it was, go back to an earlier version, change partitions or columns safely, and share the table with Spark and Trino.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Minor compaction', 'Deltas → one delta (and one delete_delta).'),
    ('Major compaction', 'Base + deltas → new base_N; deleted rows physically gone.'),
    ('Initiator / worker / cleaner', 'Decides what to compact / does it / deletes old files.'),
    ('Snapshot', 'The state of an Iceberg table after one commit.'),
    ('Time travel', '<code>FOR SYSTEM_VERSION AS OF id</code> or <code>FOR SYSTEM_TIME AS OF \'ts\'</code>.'),
    ('Hidden partitioning', 'Partitions derived from a column by a transform: day, month, bucket, truncate.'),
    ('Position delete file', 'Iceberg file listing (data file, row position) pairs that are deleted.'),
    ('Expire snapshots', 'Forget old snapshots so their files can be cleaned up.'),
]) + '''

  <h3>Hive ACID vs Iceberg in Hive 4</h3>
''' + table(['', 'Hive ACID table', 'Iceberg table'], [
    ['Create', "<code>STORED AS ORC TBLPROPERTIES ('transactional'='true')</code>", '<code>STORED BY ICEBERG</code>'],
    ['Table type', 'MANAGED', 'EXTERNAL (with purge), table_type=ICEBERG'],
    ['Default file format', 'ORC', 'Parquet (ZSTD)'],
    ['UPDATE / DELETE / MERGE', 'Yes (delta, delete_delta)', 'Yes (data + position delete files)'],
    ['History', 'No time travel', 'Snapshots: time travel, rollback'],
    ['Partitioning', 'Partition columns, fixed', 'Hidden transforms, can evolve'],
    ['Other engines writing', 'Limited', 'Spark, Trino, Flink, Impala …'],
    ['Housekeeping', 'Automatic compaction', 'Compaction + expire snapshots'],
], minw=680) + lv + '''
EXAM> Two frequent questions. “Minor vs major compaction”: minor merges deltas into one delta; major rewrites base + deltas into a new base and removes deleted rows; both are triggered by thresholds or ALTER TABLE … COMPACT. “What is Iceberg and why use it?”: an open table format with snapshot-based metadata giving ACID commits, time travel, rollback, schema and partition evolution, hidden partitioning and multi-engine access.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Commands for both worlds</h2>
''' + table(['Task', 'Hive ACID', 'Iceberg (Hive 4)'], [
    ['Compact', "<code>ALTER TABLE t [PARTITION (…)] COMPACT 'minor' | 'major' [AND WAIT];</code>", "<code>ALTER TABLE t COMPACT 'major' [AND WAIT];</code> or <code>OPTIMIZE TABLE t REWRITE DATA;</code>"],
    ['Watch', '<code>SHOW COMPACTIONS;</code>', '<code>SHOW COMPACTIONS;</code> and <code>SELECT … FROM db.t.files</code>'],
    ['History', '—', '<code>SELECT * FROM db.t.snapshots;</code> · <code>db.t.history</code>'],
    ['Time travel', '—', "<code>SELECT … FROM t FOR SYSTEM_VERSION AS OF 4523378673848349691;</code><br><code>… FOR SYSTEM_TIME AS OF '2026-10-27 10:07:10';</code>"],
    ['Undo', '—', '<code>ALTER TABLE t EXECUTE ROLLBACK(snapshot_id);</code>'],
    ['Clean old versions', 'Cleaner (automatic)', "<code>ALTER TABLE t EXECUTE EXPIRE_SNAPSHOTS('timestamp');</code>"],
    ['Change partitions', 'New table + copy', '<code>ALTER TABLE t SET PARTITION SPEC (month(order_date));</code>'],
    ['Add column', '<code>ALTER TABLE t ADD COLUMNS (…)</code>', '<code>ALTER TABLE t ADD COLUMNS (…)</code> (by column id)'],
], minw=760) + '''
''' + table(['Compaction threshold (metastore)', 'Default', 'Meaning'], [
    ['<code>hive.compactor.delta.num.threshold</code>', '10', 'More deltas than this → minor compaction'],
    ['<code>hive.compactor.delta.pct.threshold</code>', '0.1', 'Deltas larger than 10% of base → major compaction'],
    ['<code>hive.compactor.abortedtxn.threshold</code>', '1000', 'Aborted transactions → compaction'],
    ['<code>hive.compactor.check.interval</code>', '300 s', 'How often the initiator looks'],
    ['Table property <code>NO_AUTO_COMPACTION</code>', 'false', 'Disable automatic compaction for one table'],
], minw=640) + '''
WARN> Time travel only reaches snapshots that still exist. After <code>EXPIRE_SNAPSHOTS</code> our query for an older time failed with “Cannot find a snapshot older than …”. Agree a retention period (for example 7 days) with the teams that rely on time travel before expiring.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Compacting ACID tables, then a full Iceberg tour</h2>
  <p>All outputs are real, from the Hive 4.2.1 lab (database <code>tiffingo</code>). File names are shortened.</p>
''' + stepper([
    ('Step 1 · Automatic compaction after too many deltas',
     code('sql', 'Beeline', "-- cust_acid from Lesson 7.1, after six more single-row INSERTs: 11 delta / delete_delta folders\n-- (initiator enabled on the metastore, worker on HiveServer2)\n$ ls …/cust_acid\nSHOW COMPACTIONS;\nALTER TABLE cust_acid COMPACT 'minor' AND WAIT;", capf('l73_compact_auto.txt').split('\n', 2)[2]),
     'With 11 delta folders the table crossed the default threshold of 10, and the initiator queued a <b>MAJOR</b> compaction by itself (initiator id 60, not “manual”). All folders became one <code>base_0000010</code> (data up to write 10). Our manual MINOR request afterwards was refused: there was nothing worth compacting.'),
    ('Step 2 · Minor compaction by hand',
     code('sql', 'Beeline', "ALTER TABLE dim_customer_hist COMPACT 'minor' AND WAIT;", capf('l73_minor.txt')),
     'The four delta folders of writes 1–2 became one delta covering writes 1 to 3, and the delete delta was merged the same way. A minor compaction leaves deletes as delete records; it makes reads cheaper by reducing the number of folders. The <code>_v0000052</code> suffix is the compaction’s own transaction id.'),
    ('Step 3 · Major compaction of one partition',
     code('sql', 'Beeline', "ALTER TABLE orders_acid PARTITION (order_date='2026-10-02') COMPACT 'major' AND WAIT;", capf('l73_major_part.txt')),
     'The three folders of 2 October (original insert, refund update) became one base. The 102 superseded rows are now physically gone, the counts are identical, and the other partitions were not touched. Major compaction is what finally removes deleted personal data from disk (Lesson 7.1, scenario 1).'),
    ('Step 4 · An Iceberg table with hidden partitioning',
     code('sql', 'Beeline', "CREATE TABLE orders_ice (order_id INT, customer_id INT, city STRING,\n  amount DECIMAL(10,2), status STRING, order_date DATE)\nPARTITIONED BY SPEC (day(order_date))\nSTORED BY ICEBERG;\nINSERT INTO orders_ice SELECT order_id, customer_id, city, amount, status, order_date\nFROM orders WHERE order_date <= '2026-10-03';\nDESCRIBE FORMATTED orders_ice;       -- selected lines",
          tables(capf('l73_ice1.txt'))[0] + '\n\n' + capf('l73_ice_props.txt')),
     '<code>order_date</code> stays an ordinary column; the partition <code>order_date_day</code> is derived by the <code>day()</code> transform. Our lab’s defaults: Iceberg 1.9.1, format version 2, Parquet with ZSTD, and <b>merge-on-read</b> for updates and deletes. The metastore stores only a pointer, <code>metadata_location</code>, to the current metadata file.'),
    ('Step 5 · UPDATE and DELETE create snapshots',
     code('sql', 'Beeline', "UPDATE orders_ice SET status = 'REFUNDED' WHERE order_date = '2026-10-02' AND status = 'CANCELLED';\nDELETE FROM orders_ice WHERE order_date = '2026-10-03' AND amount < 50;\nSELECT snapshot_id, parent_id, operation,\n  summary['added-records'] AS added_rows, summary['added-position-deletes'] AS pos_deletes,\n  summary['total-records'] AS total_rows\nFROM tiffingo.orders_ice.snapshots ORDER BY committed_at;\n$ find …/orders_ice -type f | sort",
          tables(capf('l73_snaps.txt'))[0] + '\n\n' + capf('l73_ice_files.txt').split('\n', 1)[1]),
     'Three commits, three snapshots, each pointing to its parent. The UPDATE wrote 102 new rows and a <b>position-delete file</b> for the 102 old ones; the DELETE wrote only a position-delete file. Note <code>total-records</code> stays 5,028: it counts rows in data files, and deleted rows are hidden by delete files until compaction. A real <code>COUNT(*)</code> gives 4,886.'),
    ('Step 6 · Time travel',
     code('sql', 'Beeline', "SELECT COUNT(*) AS rows_v1, SUM(IF(status = 'CANCELLED', 1, 0)) AS cancelled_v1\nFROM orders_ice FOR SYSTEM_VERSION AS OF 4523378673848349691;\nSELECT COUNT(*) AS rows_now, SUM(IF(status = 'CANCELLED', 1, 0)) AS cancelled_now FROM orders_ice;\n\nSELECT COUNT(*) AS rows_at_10_07_10 FROM orders_ice FOR SYSTEM_TIME AS OF '2026-10-27 10:07:10';",
          capf('l73_tt.txt').split('\n+------------------------------+')[0] + '\n' + capf('l73_tt2.txt')),
     'The first snapshot still shows 4,926 rows and 306 cancelled orders; today there are 4,886 rows and 198 cancelled orders. A timestamp works too: at 10:07:10 (UTC) only the first snapshot existed. This is how data science gets “the table before yesterday’s correction” without a backup.'),
    ('Step 7 · Schema and partition evolution without rewriting',
     code('sql', 'Beeline', "ALTER TABLE orders_ice ADD COLUMNS (payment STRING);\nALTER TABLE orders_ice SET PARTITION SPEC (month(order_date));\nINSERT INTO orders_ice SELECT order_id, customer_id, city, amount, status, order_date, payment\nFROM orders WHERE order_date BETWEEN '2026-10-04' AND '2026-10-05';\nSELECT order_date, COUNT(*) AS n, COUNT(payment) AS with_payment FROM orders_ice\nGROUP BY order_date ORDER BY order_date;\nSELECT spec_id, COUNT(*) AS files FROM tiffingo.orders_ice.files GROUP BY spec_id;\n$ ls …/orders_ice/data",
          capf('l73_evo.txt') + '\n\norder_date_day=2026-10-01\norder_date_day=2026-10-02\norder_date_day=2026-10-03\norder_date_month=2026-10'),
     'Old rows read NULL for the new column. New data was written by month while old files stayed in day folders; Iceberg keeps both partition specs (spec 0 and 1) and prunes each correctly. In a plain Hive table either change would mean creating a new table and copying everything (Module 5). A query on 2 October still read only that day’s 1,617 rows.'),
    ('Step 8 · Rollback and expiring snapshots',
     code('sql', 'Beeline', "ALTER TABLE orders_ice EXECUTE ROLLBACK(4541262957374694773);\nSELECT COUNT(*) AS after_rollback FROM orders_ice;\nSELECT made_current_at, snapshot_id, is_current_ancestor FROM tiffingo.orders_ice.history;\n\n-- on events_ice (17 snapshots):\nALTER TABLE events_ice EXECUTE EXPIRE_SNAPSHOTS('<current UTC time + 1 minute>');\nSELECT COUNT(*) AS snapshots FROM tiffingo.events_ice.snapshots;\nSELECT COUNT(*) FROM events_ice FOR SYSTEM_TIME AS OF '2026-10-27 10:12:00';",
          tables(capf('l73_rollback.txt'))[0] + '\n' + tables(capf('l73_rollback.txt'))[1] + '\n' + tables(capf('l73_rollback.txt'))[2] + '\n\n' + tables(capf('l73_expire.txt'))[0] + '\n' + capf('l73_expired_tt.txt').split('; Query ID')[0]),
     'Rollback made the snapshot before the 5 October load current again: 8,251 → 4,886 rows, instantly, without copying data. The history shows the abandoned snapshot as no longer an ancestor. Expiring snapshots kept only the latest one, and time travel to an expired point now fails.'),
    ('Step 9 · Compacting Iceberg in Hive 4.2.1',
     code('sql', 'Beeline', "-- events_ice: 15 small INSERTs and one DELETE → 15 data files + 1 delete file\nALTER TABLE events_ice COMPACT 'major' AND WAIT;\nINSERT OVERWRITE TABLE events_ice SELECT * FROM events_ice;\n\n-- orders_ice after partition evolution:\nINSERT OVERWRITE TABLE orders_ice SELECT * FROM orders_ice;",
          capf('l73_ice_compact.txt').split('\n', 1)[1] + '\n\nError: … Cannot perform insert overwrite query on Iceberg table where partition evolution happened.\nIn order to successfully carry out any insert overwrite operation on this table, the data has to be\nrewritten conforming to the latest spec.'),
     'Hive 4.2.1 has built-in Iceberg compaction (COMPACT and OPTIMIZE TABLE), but its evaluator decides whether a table is worth compacting, and it refused our small tables. Rewriting with INSERT OVERWRITE worked on <code>events_ice</code>: 16 files became one with the same 24,236 rows. On <code>orders_ice</code> the overwrite was refused after partition evolution. In production, check SHOW COMPACTIONS, or run Iceberg’s <code>rewrite_data_files</code> from Spark.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('$ ls …/cust_acid       (11 delta folders)', W), ('> SHOW COMPACTIONS;', W), ('| 1 | cust_acid | MAJOR | succeeded | 60 |', G), ('$ ls …/cust_acid', W), ('base_0000010_v0000045', G)]),
    term([("> ALTER TABLE dim_customer_hist COMPACT 'minor' AND WAIT;", W), ('  delta_0000001_0000003_v0000052', G), ('  delete_delta_0000001_0000003_v0000052', G), ('  (was 4 deltas + 1 delete delta)', Y)], size=7.6),
    term([('> … FROM tiffingo.orders_ice.snapshots;', W), ('| append    | 4926 |      | 4926 |', G), ('| overwrite | 102  | 102  | 5028 |', G), ('| delete    |      | 40   | 5028 |', G)]),
    term([('> … FOR SYSTEM_VERSION AS OF 45233786…;', W), ('| 4926 | 306 |', G), ('> … orders_ice (now);', W), ('| 4886 | 198 |', G)]),
    term([('> ALTER TABLE orders_ice EXECUTE ROLLBACK(…);', W), ('| after_rollback | 4886 |', G), ("> … EXECUTE EXPIRE_SNAPSHOTS('…');", W), ('| snapshots | 1 |', Y), ('Cannot find a snapshot older than …', RD)], size=7.6),
]
def chain(n=4, cur=3, y=46, dim=None):
    o = ''
    for k in range(n):
        tone = 'green' if k == cur else ('card' if dim and k in dim else 'blue')
        o += box(24 + k * 82, y, 70, 30, tone) + t(59 + k * 82, y + 19, f'snap {k + 1}', 7.6, 'ink', bold=True)
        if k < n - 1:
            o += arrow(96 + k * 82, y + 15, 104 + k * 82, y + 15, 'ink3')
    return o
B1 = [
    t(180, 22, 'Initiator → worker → cleaner', 9.4, bold=True) + ''.join(fol(20 + (k % 4) * 60, 38 + (k // 4) * 24, f'Δ{k + 1}', 'acc', 54) for k in range(11)) +
    arrow(270, 62, 300, 62, 'green', 2) + fol(300, 50, 'base_10', 'green', 50) + cap('More than 10 deltas → MAJOR queued automatically.', 'Old folders removed by the cleaner.', 'green', y=150, h=46),
    t(180, 22, 'Minor: deltas → one delta', 9.4, bold=True) + ''.join(fol(20, 40 + k * 24, f'delta_{k + 1}', 'acc', 90) for k in range(4)) + arrow(118, 76, 180, 76, 'green', 2) + fol(190, 64, 'delta_1_3', 'green', 140) +
    cap('Deletes stay as delete records (major removes them).', '', 'blue', y=150, h=34),
    t(180, 22, 'Iceberg metadata tree', 9.4, bold=True) + box(130, 36, 100, 22, 'violet') + t(180, 51, 'metadata.json', 7.4, bold=True, mono=True) + arrow(180, 58, 180, 66, 'ink3') +
    box(130, 66, 100, 20, 'blue') + t(180, 80, 'manifest list', 7.2, bold=True) + arrow(180, 86, 180, 94, 'ink3') + box(130, 94, 100, 20, 'blue') + t(180, 108, 'manifests', 7.2, bold=True) +
    fol(20, 120, 'data.parquet', 'card', 100, 18) + fol(130, 120, 'pos-deletes', 'acc', 100, 18) + fol(240, 120, 'data.parquet', 'card', 100, 18) + cap('Each commit = new metadata.json = new snapshot.', '', 'blue', y=150, h=34),
    t(180, 22, 'Read an old snapshot', 9.4, bold=True) + chain(3, 2) + arrow(59, 92, 59, 80, 'acc', 2) + t(59, 104, 'AS OF snap 1', 7.4, 'acc', mono=True, bold=True) + cap('Old files are still there, so old snapshots are readable.', '', 'green', y=150, h=34),
    t(180, 22, 'Rollback moves the pointer', 9.4, bold=True) + chain(4, 2, dim={3}) + t(305, 96, 'abandoned', 7.2, 'ink3') + cap('No data copied: current = snap 3 again.', 'Expire removes old snapshots for good.', 'blue', y=150, h=46),
]
see_caps = ['The initiator compacted an 11-delta table into one base, on its own.',
            'A manual minor compaction merged four deltas into one.',
            'Each Iceberg commit adds a snapshot; deletes are separate files.',
            'Time travel reads the table as it was at an earlier snapshot.',
            'Rollback restores an older snapshot; expired snapshots are gone for good.']
behind_caps = ['The metastore’s initiator queues work when thresholds are crossed; workers rewrite; the cleaner deletes old folders.',
               'Minor compaction combines deltas; deleted rows remain as delete records.',
               'metadata.json points to a manifest list, which points to manifests, which list data and delete files.',
               'A query AS OF a snapshot uses that snapshot’s manifest list and ignores newer files.',
               'The table’s current pointer moves back; later snapshots are kept until expired.']
two = anim_two('Compaction and Iceberg', 'Merging deltas and travelling in time', 'Real Beeline output', 'What the compactor and Iceberg metadata do', see, B1, see_caps, behind_caps)

# ---- scenario 1: bad load undo
u1 = (t(180, 22, '09:10 · a load wrote wrong amounts', 9.4, bold=True) + t(180, 56, 'reports are already showing the bad numbers', 8.4, 'red') + cap('Plain Hive: restore from backup, hours.', '', 'amber', y=150, h=34))
u2 = (t(180, 22, 'Find the last good snapshot', 9.4, bold=True) + t(180, 56, 'SELECT * FROM db.orders_ice.history;', 8.4, 'ink', mono=True) + cap('Each load is one snapshot with a time.', '', 'blue', y=150, h=34))
u3 = term([('> ALTER TABLE orders_ice EXECUTE ROLLBACK(4541262957374694773);', W), ('> SELECT COUNT(*) FROM orders_ice;', W), ('| 4886 |', G)], label='real output · Hive 4.2.1', size=7.4)
u4 = (t(180, 22, 'Fix and reload', 9.4, bold=True) + t(180, 56, 'the bad snapshot stays in history for investigation', 8.2, 'ink2') + cap('Compare it with time travel before expiring.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Lesson', 9.4, 'acc', bold=True) + t(180, 56, 'keep snapshots long enough to undo mistakes', 8.4, 'ink2') + cap('Retention = how far back you can rescue.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Undoing a bad load in seconds',
              'Iceberg rollback replaces a restore from backup. The rollback result is real.',
              'Rollback', 'A bad load is undone by rolling the Iceberg table back to the last good snapshot, keeping the bad one for analysis', [u1, u2, u3, u4, u5],
              ['A load wrote wrong data and reports see it.',
               'The history table shows the snapshot before the load.',
               'Rollback makes it current again instantly.',
               'Fix the job and reload; investigate the bad snapshot.',
               'Snapshot retention decides how far back you can go.'],
              hid='scenario-rollback')

# ---- scenario 2: compaction ops
o1 = (t(180, 22, 'Ops dashboard for ACID tables', 9.4, bold=True) + t(180, 56, 'SHOW COMPACTIONS: initiated · working · succeeded · failed', 7.6, 'ink', mono=True) + cap('Watch failed and refused entries.', '', 'blue', y=150, h=34))
o2 = (t(180, 22, 'Common failures', 9.4, bold=True) + t(180, 52, 'compactor not running anywhere', 8, 'ink2') + t(180, 68, 'worker cannot reach the metastore DB', 8, 'ink2') + t(180, 84, '(our lab: “Version information not found”)', 7.6, 'red', mono=True) + cap('Check initiator, worker and cleaner settings.', '', 'amber', y=150, h=34))
o3 = (t(180, 22, 'Long-open transactions block cleaning', 9.4, bold=True) + t(180, 56, 'SHOW TRANSACTIONS → abort stuck ones', 8.4, 'ink', mono=True) + cap('Old folders stay until readers are done.', '', 'blue', y=150, h=34))
o4 = (t(180, 22, 'Schedule big majors off-peak', 9.4, bold=True) + t(180, 56, "ALTER TABLE … PARTITION (…) COMPACT 'major'", 8, 'ink', mono=True) + cap('Partition by partition after heavy MERGEs.', '', 'green', y=150, h=34))
o5 = (t(180, 22, 'Measure', 9.4, 'acc', bold=True) + t(180, 56, 'folders per partition, compaction duration', 8.4, 'ink2') + cap('Alert before reads slow down.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Keeping compaction healthy',
              'What platform teams monitor for Hive ACID tables. The error is the one our lab produced before configuration.',
              'Compaction operations', 'Monitor SHOW COMPACTIONS, fix compactor configuration, abort stuck transactions and schedule major compactions', [o1, o2, o3, o4, o5],
              ['SHOW COMPACTIONS is the starting point.',
               'Most failures are configuration: who runs the compactor and can it reach the metastore?',
               'Open transactions delay the cleaner.',
               'Run large major compactions off-peak.',
               'Track folders per partition.'],
              hid='scenario-compaction-ops')

# ---- scenario 3: ACID → Iceberg migration
m1 = (t(180, 22, 'Moving a table from Hive ACID to Iceberg', 9.4, bold=True) + t(180, 56, 'Spark jobs must now update it too', 8.4, 'ink2') + cap('Plan the switch carefully.', '', 'blue', y=150, h=34))
m2 = (t(180, 22, 'Create and copy', 9.4, bold=True) + t(180, 52, 'CREATE TABLE t_ice … PARTITIONED BY SPEC (day(dt))', 7.6, 'ink', mono=True) + t(180, 68, 'STORED BY ICEBERG AS SELECT * FROM t_acid;', 7.6, 'ink', mono=True) + cap('Hidden partitioning instead of a dt column.', '', 'green', y=150, h=34))
m3 = (t(180, 22, 'Verify', 9.4, bold=True) + t(180, 56, 'counts and sums per partition: old vs new', 8.4, 'ink2') + cap('Then point readers to the new table.', '', 'green', y=150, h=34))
m4 = (t(180, 22, 'Adapt jobs', 9.4, bold=True) + t(180, 56, 'MERGE works the same (real lab: dim_ice)', 8.4, 'ink2') + t(180, 74, 'add EXPIRE_SNAPSHOTS + compaction jobs', 8.4, 'ink2') + cap('New housekeeping replaces the ACID compactor.', '', 'blue', y=150, h=34))
m5 = (t(180, 22, 'Benefits', 9.4, 'acc', bold=True) + t(180, 56, 'multi-engine writes · time travel · evolution', 8.4, 'ink2') + cap('Many lakehouses standardise on Iceberg.', '', 'green', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Migrating an ACID table to Iceberg',
              'A common modernisation step. (Typical plan; MERGE on Iceberg ran in our lab.)',
              'ACID to Iceberg', 'Create an Iceberg table with hidden partitioning, copy and verify the data, switch readers, and add snapshot housekeeping', [m1, m2, m3, m4, m5],
              ['Other engines now need to write the table.',
               'Create an Iceberg copy with CTAS.',
               'Verify counts and sums, then switch readers.',
               'Keep MERGE jobs; add snapshot expiry and compaction.',
               'Gain multi-engine access, time travel and evolution.'],
              hid='scenario-migrate')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Merging deltas and travelling in time</h2>
  <p>Left: real Beeline output. Right: what the compactor and Iceberg metadata do.</p>
''' + two + '''
  <p>Three live scenarios follow: undoing a bad load, keeping compaction healthy, and migrating to Iceberg.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Compaction and Iceberg at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'base_N', 11, 'green', bold=True, mono=True) + t(60, 58, 'auto compaction', 7.4, 'ink2'),
    '1. Keeping ACID tables fast',
    'Warehouses with nightly MERGEs rely on the compactor; platform teams tune thresholds and watch SHOW COMPACTIONS like any other job.',
    ['Many deltas', '*compactor', 'Few files']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'AS OF', 12, 'blue', bold=True, mono=True) + t(60, 58, 'reproducible', 7.4, 'ink2'),
    '2. Reproducible ML training data',
    'Data scientists record the snapshot id used to train a model, so the exact training data can be read again months later.',
    ['Model training', '*snapshot id', 'Same data later']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'ROLLBACK', 10, 'violet', bold=True, mono=True) + t(60, 58, 'safe loads', 7.4, 'ink2'),
    '3. Safe pipelines',
    'If a load is wrong, teams roll the table back to the previous snapshot in seconds instead of restoring backups.',
    ['Bad load', '*rollback', 'Good data']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'Spark+Trino', 9, 'acc', bold=True) + t(60, 58, 'one table', 7.4, 'ink2'),
    '4. The open lakehouse',
    'Iceberg tables in a shared catalog are written by Spark and Flink and queried by Hive, Trino and cloud engines without copies.',
    ['Many engines', '*Iceberg', 'One table']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'month()', 11, 'acc', bold=True, mono=True) + t(60, 58, 'evolve', 7.4, 'ink2'),
    '5. Changing partitioning as data grows',
    'A table partitioned by month when small can move to day partitions when it grows, without rewriting history.',
    ['Growth', '*SET PARTITION SPEC', 'New layout']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> finish <a href="../01-acid-tables-update-delete/">7.1</a> and <a href="../02-merge-and-scd/">7.2</a>; partitioning (<a href="../../05-partitioning-and-bucketing/01-partitioning/">5.1</a>) and Parquet (<a href="../../06-file-formats/03-parquet-and-compression/">6.3</a>) help too.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
