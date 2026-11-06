import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()

# ---------------------------------------------------------------- story
sc = (box(10, 12, 300, 128, 'red') + t(160, 30, 'Kabir: DROP TABLE orders_plain;', 9, 'red', bold=True, mono=True) +
      node(30, 46, 110, 40, 'metastore row', 'deleted', 'violet') + node(170, 46, 120, 40, 'folder + files', 'deleted', 'red') +
      t(160, 112, 'gone: 4,820 Thane orders', 8.6, 'red', bold=True) +
      box(330, 12, 300, 128, 'green') + t(480, 30, 'Riya: DROP TABLE orders_ext;', 9, 'green', bold=True, mono=True) +
      node(350, 46, 110, 40, 'metastore row', 'deleted', 'violet') + node(490, 46, 120, 40, 'orders.csv', 'still there', 'green') +
      t(480, 112, 're-create the table → 50,002 rows back', 8.6, 'green', bold=True))
scene_svg = scene('Two DROP TABLE statements: one deletes the table and its files, the other deletes only the table definition and leaves the files.', sc,
                  'Same command, different result: the <tspan font-weight="700" class="s-acc">table type</tspan> decides what DROP deletes.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“I only dropped the table. Where did the data go?”</h2>
  <div class="story">
    <p class="narration">Kabir and Riya each clean up a test table on the TiffinGo lab. Both type <code>DROP TABLE</code>. Riya re-creates hers a minute later and all 50,002 orders are still there. Kabir re-creates his and gets zero rows: the folder in the warehouse is gone.</p>

{scene_svg}

K> Sir, we ran the same command. Why did my data disappear and hers did not?
A> Because Hive has two kinds of ownership. For Riya’s table Hive owns only the <b>label</b>: the metadata. The files belong to someone else, so DROP removes the label and leaves the files. That is an <b>external table</b>. For your table Hive owned the label <b>and</b> the box: DROP removed both.
R> So I should always use external tables to be safe?
A> Not always. Hive can only offer some features when it owns the files: <code>UPDATE</code>, <code>DELETE</code>, <code>MERGE</code>, <code>TRUNCATE</code>, automatic clean-up. And Hive 4 adds a twist: your plain <code>CREATE TABLE</code> was stored as an external table with a <b>purge</b> flag, which makes DROP delete files anyway.
K> Three kinds, then. How do I tell them apart before I drop something?
A> <code>DESCRIBE FORMATTED</code>: look at <b>Table Type</b>, <b>external.table.purge</b> and <b>transactional</b>. Today we will create all three over the same orders, change one row, drop them and look at the folders after each step.
  </div>
</section>
'''

# ---------------------------------------------------------------- definition
lv = '''
LEVELS> Managed and external at three levels
L1> A rented flat and your own house
      <ul>
        <li><b>External table</b> = a flat you rent. You put your name on the door (the metadata). When you leave, you take the name plate; the flat and its furniture (the files) stay for the owner.</li>
        <li><b>Managed table</b> = your own house. When you sell it, everything inside goes too.</li>
        <li>Hive can renovate a house it owns (UPDATE, DELETE), but it must not change someone else’s flat.</li>
      </ul>
L2> The three kinds you will meet in Hive 4
      <ul>
        <li><b>MANAGED_TABLE</b> (transactional): created with <code>TBLPROPERTIES ('transactional'='true')</code>, usually ORC. Lives in the warehouse; supports INSERT, UPDATE, DELETE, MERGE; DROP deletes metadata and files.</li>
        <li><b>EXTERNAL_TABLE with external.table.purge=TRUE</b>: what a plain <code>CREATE TABLE</code> becomes (marked <code>TRANSLATED_TO_EXTERNAL</code>). Lives in the warehouse; INSERT and TRUNCATE work, UPDATE/DELETE do not; DROP deletes the files.</li>
        <li><b>EXTERNAL_TABLE</b> (plain): created with <code>CREATE EXTERNAL TABLE … LOCATION</code>. Files anywhere; DROP keeps them; TRUNCATE, UPDATE and DELETE are refused.</li>
      </ul>
L3> Why Hive 3 and 4 work this way
      <ul>
        <li>Since Hive 3, “managed” means <b>Hive controls every write</b>, so it can offer transactions: each write creates a <code>delta_…</code> folder, deletes create <code>delete_delta_…</code> folders, and readers see a consistent snapshot. Other tools must not write there directly.</li>
        <li>Non-transactional tables cannot give those guarantees, so the metastore stores them as external (<code>hive.create.as.acid=false</code> is the default in our lab; with it set to true, plain CREATE TABLE makes ACID tables).</li>
        <li><b>DROP is a metastore operation</b> that then deletes files as the metastore’s user. If that user lacks permission, the table disappears but the files stay (we reproduced this: “Failed to delete … it still exists” in the metastore log).</li>
        <li><code>external.table.purge</code> can be changed with <code>ALTER TABLE … SET TBLPROPERTIES</code>: flipping it to true on a shared folder is a classic way to delete someone else’s data.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Managed and external tables</h2>
''' + def_block(
    'A <b>managed (internal) table</b> is a table whose data files Hive owns: they are stored under the warehouse directory, written only through Hive, and deleted with the table on <code>DROP TABLE</code>; in Hive 3 and later managed tables are <b>transactional (ACID)</b>. An <b>external table</b> is a table for which Hive owns only the metadata: its <code>LOCATION</code> may be any path, other tools may write the files, and <code>DROP TABLE</code> removes only the metadata unless the property <code>external.table.purge</code> is <code>true</code>.',
    'Managed: Hive owns the table and the files, so dropping the table deletes the data. External: Hive only describes files that belong to someone else, so dropping the table leaves the data. In Hive 4 a plain CREATE TABLE gives an external table with “purge” switched on, which also deletes data on DROP.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Managed table', 'Hive owns data and metadata. Table Type <code>MANAGED_TABLE</code>; in Hive 4 transactional.'),
    ('External table', 'Hive owns only metadata. Table Type <code>EXTERNAL_TABLE</code>; files can live anywhere.'),
    ('external.table.purge', 'Table property: when <code>TRUE</code>, DROP also deletes an external table’s files.'),
    ('TRANSLATED_TO_EXTERNAL', 'Marker Hive 4 adds when it stored your plain CREATE TABLE as an external purge table.'),
    ('Transactional / ACID', 'A table where Hive tracks every write as a transaction, enabling UPDATE, DELETE and MERGE.'),
    ('delta / delete_delta', 'Folders an ACID table gets for each insert or update (new rows) and delete (removed rows).'),
    ('TRUNCATE', 'Deletes all rows but keeps the table definition. Refused on plain external tables.'),
    ('Orphan files', 'Files left on storage with no table pointing to them, for example after a failed delete.'),
]) + '''

  <h3>The three kinds side by side (tested on Hive 4.2.1)</h3>
''' + table(['', 'MANAGED_TABLE (transactional)', 'EXTERNAL + purge (plain CREATE TABLE)', 'EXTERNAL_TABLE'], [
    ['Created with', "<code>CREATE TABLE … STORED AS ORC TBLPROPERTIES ('transactional'='true')</code>", '<code>CREATE TABLE …</code>', "<code>CREATE EXTERNAL TABLE … LOCATION '…'</code>"],
    ['Default location', 'Warehouse: <code>tiffingo.db/orders_acid</code>', 'Warehouse: <code>tiffingo.db/orders_plain</code>', 'Any path you give'],
    ['Files after INSERT', '<code>delta_0000001_0000001_0000/bucket_00000_0</code>', '<code>000000_0</code>', 'Whatever was there, plus new files'],
    ['UPDATE / DELETE / MERGE', '<b>Yes</b>', 'No: “not transactional”', 'No'],
    ['TRUNCATE', 'Yes', 'Yes', 'No: “Cannot truncate non-managed table”'],
    ['DROP TABLE', 'Deletes metadata <b>and files</b>', 'Deletes metadata <b>and files</b>', 'Deletes metadata, <b>keeps files</b>'],
    ['Other tools may write files', 'No, only through Hive', 'Possible but unsafe', 'Yes, that is the point'],
    ['Typical use', 'Curated tables that change (orders, customers with updates)', 'Simple intermediate tables', 'Landing data, shared data, files produced by Spark/Kafka jobs'],
], minw=820) + lv + '''
EXAM> “Differentiate managed and external tables.” Give four points: who owns the data, default location (warehouse vs any LOCATION), effect of DROP (data deleted vs kept), and when to use each (Hive-only data vs data shared with other tools). For Hive 3/4 add: managed tables are ACID, and <code>external.table.purge</code> makes DROP delete external data.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Choosing a table type, and changing it later</h2>
''' + cards([
    ('External for landing data', 'Files dropped by an ingestion tool, Kafka connector or partner. Many tools read and write them; Hive must never delete them by accident.', 'Raw layer'),
    ('Managed ACID for curated data', 'Tables that need corrections: refunds, cancelled orders, customer address changes. MERGE and UPDATE work; compaction tidies files.', 'Curated layer'),
    ('External + purge for work tables', 'Intermediate results only Hive uses. DROP cleans up the files, no ACID overhead.', 'Scratch'),
    ('External on object storage', 'Tables over S3, GCS or ADLS paths shared with Spark and Trino, often in ORC, Parquet or Iceberg.', 'Lakehouse'),
]) + '''

  <h3>Statements that touch ownership</h3>
''' + table(['Statement', 'Effect', 'Care needed'], [
    ["<code>ALTER TABLE t SET TBLPROPERTIES ('external.table.purge'='true')</code>", 'Next DROP deletes the files', '<b>High</b>: check who else uses the folder'],
    ["<code>ALTER TABLE t SET TBLPROPERTIES ('external.table.purge'='false')</code>", 'Next DROP keeps the files', 'Safe'],
    ['<code>DROP TABLE t PURGE</code>', 'Deletes files without moving them to the HDFS trash', 'No undo from trash'],
    ['<code>DROP TABLE IF EXISTS t</code>', 'No error if the table is missing', 'Good in scripts'],
    ['<code>TRUNCATE TABLE t</code>', 'Removes all rows, keeps the definition', 'Not allowed on plain external tables'],
], minw=640) + '''
WARN> Never point two tables at the same folder unless both are external without purge. In our lab, flipping <code>external.table.purge</code> to true and dropping the table deleted the whole folder at once. On a shared HDFS path, that is somebody else’s data.
</section>
'''

ACIDDIRS = capf('l22_acid_dirs.txt')
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Three tables over the same orders, then three DROPs</h2>
  <p>All outputs are real (Hive 4.2.1 lab). The 50,002 orders file sits in <code>/data/tiffingo/orders_ext</code>.</p>
''' + stepper([
    ('Step 1 · An external table over existing files',
     code('sql', 'Beeline', "CREATE EXTERNAL TABLE orders_ext (\n  order_id INT, customer_id INT, restaurant_id INT, city STRING,\n  order_ts TIMESTAMP, amount INT, payment STRING, status STRING)\nROW FORMAT DELIMITED FIELDS TERMINATED BY ','\nLOCATION 'file:///data/tiffingo/orders_ext';"),
     'Hive records the definition and the folder; the 3 MB file is not moved. From now on Hive, and any other tool, can read it.'),
    ('Step 2 · A plain table and an ACID table, filled from it',
     code('sql', 'Beeline', "CREATE TABLE orders_plain (order_id INT, city STRING, amount INT);\nCREATE TABLE orders_acid  (order_id INT, city STRING, amount INT)\n  STORED AS ORC TBLPROPERTIES ('transactional'='true');\nINSERT INTO orders_plain SELECT order_id, city, amount FROM orders_ext WHERE city = 'Thane';\nINSERT INTO orders_acid  SELECT order_id, city, amount FROM orders_ext WHERE city = 'Thane';\nSELECT 'ext' AS t, COUNT(*) FROM orders_ext\nUNION ALL SELECT 'plain', COUNT(*) FROM orders_plain\nUNION ALL SELECT 'acid', COUNT(*) FROM orders_acid;", capf('l22_counts.txt')),
     'Both new tables hold the 4,820 Thane orders. The INSERT … SELECT ran as a Tez job and wrote new files into each table’s warehouse folder.'),
    ('Step 3 · Ask each table what it is',
     code('sql', 'Beeline', 'DESCRIBE FORMATTED orders_ext;    -- and orders_plain, orders_acid',
          'orders_ext   | Location:   | file:/data/tiffingo/orders_ext\n             | Table Type: | EXTERNAL_TABLE\n             |             | EXTERNAL                TRUE\n\norders_plain | Location:   | file:/opt/hive/data/warehouse/tiffingo.db/orders_plain\n             | Table Type: | EXTERNAL_TABLE\n             |             | TRANSLATED_TO_EXTERNAL  TRUE\n             |             | external.table.purge    TRUE\n\norders_acid  | Location:   | file:/opt/hive/data/warehouse/tiffingo.db/orders_acid\n             | Table Type: | MANAGED_TABLE\n             |             | transactional           true\n(lines picked from three outputs)'),
     'Three answers: plain external, external with purge (translated by Hive 4), and a true managed transactional table. These three lines decide what DROP will do.'),
    ('Step 4 · Look at the files',
     code('bash', 'Terminal', 'cd /opt/hive/data/warehouse/tiffingo.db\nfind orders_plain orders_acid -type f -not -name ".*"',
          'orders_acid/delta_0000001_0000001_0000/bucket_00000_0\norders_acid/delta_0000001_0000001_0000/_orc_acid_version\norders_plain/000000_0'),
     'The plain table got one ordinary file. The ACID table got a <b>delta folder</b> named after transaction 1 (<code>delta_&lt;min txn&gt;_&lt;max txn&gt;_&lt;statement&gt;</code>) containing an ORC bucket file.'),
    ('Step 5 · Change one row',
     code('sql', 'Beeline', 'UPDATE orders_acid  SET amount = 999 WHERE order_id = 100010;\nUPDATE orders_plain SET amount = 999 WHERE order_id = 100010;',
          capf('l22_update.txt').split('\n')[0] + '\n(SELECT after the update)\n' + '\n'.join(capf('l22_update.txt').split('\n')[1:]) + '\n\n' + capf('l22_update_err.txt').split('; Query ID')[0]),
     'The ACID table accepts the UPDATE (order 100010 now shows 999); the plain table refuses at compile time. Behind the screen the update wrote two new folders (Step 6 in the animation): <code>' + ACIDDIRS.replace('\n', '</code>, <code>') + '</code>.'),
    ('Step 6 · Try TRUNCATE on the external table',
     code('sql', 'Beeline', 'TRUNCATE TABLE orders_ext;', 'Error: Error while compiling statement: FAILED: SemanticException [Error 10146]: Cannot truncate non-managed table orders_ext.'),
     'Hive refuses to empty files it does not own. TRUNCATE on <code>orders_plain</code> (purge) worked in our lab and left 0 rows.'),
    ('Step 7 · Drop all three and look again',
     code('sql', 'Beeline', 'DROP TABLE orders_ext;\nDROP TABLE orders_plain;\nDROP TABLE orders_acid;\nSHOW TABLES;', capf('l22_after_drop.txt').split('customers\ntotal')[0].rstrip() + '\n\n$ ls /opt/hive/data/warehouse/tiffingo.db\ncustomers\n$ ls -la /data/tiffingo/orders_ext\n-rw-r--r-- 1 root root 3085976 Oct 26 10:30 orders.csv'),
     'The warehouse folders of <code>orders_plain</code> and <code>orders_acid</code> are gone. <code>orders.csv</code> in the external location is untouched; re-running the CREATE EXTERNAL TABLE from Step 1 returned <b>50,002</b> rows immediately.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
def trio(ext, plain, acid, note=''):
    """three columns: metadata chip + files box for each table"""
    o = ''
    for k, (name, st) in enumerate([('orders_ext', ext), ('orders_plain', plain), ('orders_acid', acid)]):
        x = 8 + k * 118
        meta, files, tone = st
        o += t(x + 55, 50, name, 7.8, bold=True, mono=True)
        o += node(x, 56, 110, 30, 'metadata', '', 'violet', meta, 7.6)
        o += box(x, 94, 110, 96, tone) if files else f'<g opacity=".35">{box(x, 94, 110, 96, "card")}</g>'
        for j, ln in enumerate(files or ['(no files)']):
            o += t(x + 6, 108 + j * 12, ln, 6.8, 'ink' if files else 'ink3', anchor='start', mono=True)
    if note:
        o += t(180, 212, note, 8.2, 'ink2')
    return o
EXTF = ['/data/tiffingo/', ' orders_ext/', '  orders.csv', '  (3 MB)']
see = [
    term([('> CREATE EXTERNAL TABLE orders_ext (…)', W), ("  LOCATION 'file:///data/tiffingo/orders_ext';", W), ('No rows affected', G), ('> SELECT COUNT(*) FROM orders_ext;', W), ('| 50002  |', G)]),
    term([('> CREATE TABLE orders_plain (…);', W), ('> CREATE TABLE orders_acid (…) STORED AS ORC', W), ("  TBLPROPERTIES ('transactional'='true');", W), ('> INSERT INTO … WHERE city = \'Thane\';  (x2)', W), ('| acid   | 4820   |', G), ('| plain  | 4820   |', G), ('| ext    | 50002  |', G)]),
    term([('> DESCRIBE FORMATTED …  (Table Type)', W), ('orders_ext    EXTERNAL_TABLE', G), ('orders_plain  EXTERNAL_TABLE', Y), ('  TRANSLATED_TO_EXTERNAL  TRUE', Y), ('  external.table.purge    TRUE', Y), ('orders_acid   MANAGED_TABLE', G), ('  transactional           true', G)]),
    term([('> UPDATE orders_acid SET amount = 999', W), ('  WHERE order_id = 100010;', W), ('| 100010 | Thane | 999 |', G), ('> UPDATE orders_plain SET amount = 999 …', W), ('Error: … [Error 10297]: Attempt to do', RD), ('  update or delete on table orders_plain', RD), ('  that is not transactional', RD)], size=7.6),
    term([('> TRUNCATE TABLE orders_ext;', W), ('Error: … [Error 10146]: Cannot truncate', RD), ('  non-managed table orders_ext.', RD), ('', W), ('(TRUNCATE on a purge table works:', Y), (' orders_plain → 0 rows)', Y)]),
    term([('> DROP TABLE orders_ext;', W), ('> DROP TABLE orders_plain;', W), ('> DROP TABLE orders_acid;', W), ('> SHOW TABLES;', W), ('| customers  |', G)]),
    term([('> CREATE EXTERNAL TABLE orders_ext (…)', W), ("  LOCATION 'file:///data/tiffingo/orders_ext';", W), ('> SELECT COUNT(*) FROM orders_ext;', W), ('| 50002  |', G), ('', W), ('Riya’s data came back. Kabir’s did not.', Y)]),
]
B1 = [
    t(180, 22, 'External: Hive records the folder', 9.4, bold=True) + trio((True, EXTF, 'green'), (False, None, 'card'), (False, None, 'card'), 'The file is not copied or moved'),
    t(180, 22, 'Two warehouse tables get new files', 9.4, bold=True) + trio((True, EXTF, 'green'), (True, ['tiffingo.db/', ' orders_plain/', '  000000_0'], 'acc'), (True, ['tiffingo.db/', ' orders_acid/', '  delta_0000001_', '   0000001_0000/', '   bucket_00000_0'], 'blue'), 'INSERT ran as a Tez job: transaction 1'),
    t(180, 22, 'Three kinds of table', 9.4, bold=True) + trio((True, EXTF, 'green'), (True, ['purge = TRUE', '(translated)'], 'acc'), (True, ['transactional', '= true'], 'blue'), 'Table Type + purge + transactional'),
    t(180, 22, 'UPDATE writes new folders, never edits a file', 9.4, bold=True) + trio((True, EXTF, 'green'), (True, ['000000_0', '', 'UPDATE refused'], 'acc'), (True, ['delta_…1…/', 'delete_delta_', ' 0000002_…/', 'delta_0000002_', ' 0000002_0001/'], 'blue'), 'Old row marked deleted, new row added (txn 2)'),
    t(180, 22, 'TRUNCATE only where Hive owns files', 9.4, bold=True) + trio((True, EXTF, 'green'), (True, ['(emptied in', ' our test)'], 'acc'), (True, ['delta + delete', ' folders'], 'blue'), 'External files are never emptied by Hive'),
    t(180, 22, 'DROP: metadata always, files only if owned', 9.4, bold=True) + trio((False, EXTF, 'green'), (False, None, 'card'), (False, None, 'card'), 'orders.csv survives; two folders deleted'),
    t(180, 22, 'Re-create the external table: data is back', 9.4, bold=True) + trio((True, EXTF, 'green'), (False, None, 'card'), (False, None, 'card'), 'Metadata can be rebuilt; deleted files cannot'),
]
see_caps = ['Riya creates an external table over the orders folder and counts 50,002 rows.',
            'Kabir creates a plain table and an ACID table and fills each with the 4,820 Thane orders.',
            'DESCRIBE FORMATTED shows three different table types and flags.',
            'The UPDATE works on the ACID table and is refused on the plain table.',
            'TRUNCATE is refused on the external table.',
            'All three tables are dropped. Only customers is left.',
            'Riya re-creates her external table and gets all 50,002 rows back.']
behind_caps = ['Only metadata is written. The file stays at /data/tiffingo/orders_ext.',
               'The plain table gets an ordinary file 000000_0. The ACID table gets a delta folder for transaction 1.',
               'Plain external, external with purge (Hive 4 translation) and managed transactional.',
               'The ACID table never edits a file: transaction 2 writes a delete_delta (old row) and a delta (new row).',
               'Hive refuses to empty a folder it does not own.',
               'Metadata is removed for all three. Files are deleted for the purge table and the managed table; the external file stays.',
               'Re-creating an external table is instant because the files were never touched.']
two = anim_two('Ownership', 'Three tables, same data, three different DROPs', 'Beeline commands and their real output', 'Metadata and files for each table after every step', see, B1, see_caps, behind_caps)

# ---- scenario 1: shared landing folder
f1 = (t(180, 22, 'One folder, two teams', 9.6, bold=True) + node(20, 44, 120, 46, 'Kafka connector', 'writes files', 'blue') + arrow(142, 67, 196, 100, 'blue', 2) +
      box(198, 84, 140, 56, 'green') + t(268, 104, '/landing/app_events/', 7.6, bold=True, mono=True) + t(268, 122, 'new files every hour', 7.6, 'ink2') +
      node(20, 112, 120, 46, 'Hive table', 'EXTERNAL', 'acc') + arrow(142, 135, 196, 118, 'acc', 2) + cap('Hive reads files another system owns.', 'External is the right type here.', 'green', y=168, h=46))
f2 = (t(180, 22, 'Someone flips the purge flag', 9.6, 'red', bold=True) + t(180, 64, "ALTER TABLE app_events SET TBLPROPERTIES", 8, 'ink', mono=True) + t(180, 80, "('external.table.purge'='true');", 8, 'ink', mono=True) +
      t(180, 112, '“so DROP cleans up after us”', 8.6, 'ink2') + cap('Harmless-looking change.', 'Nothing happens… yet.', 'amber', y=150, h=46))
f3 = (t(180, 22, 'A clean-up script drops the table', 9.6, 'red', bold=True) + box(198, 60, 140, 56, 'red') + t(268, 80, '/landing/app_events/', 7.6, bold=True, mono=True) + t(268, 98, 'DELETED', 9, 'red', bold=True) +
      node(20, 60, 120, 56, 'DROP TABLE', 'app_events', 'red') + arrow(142, 88, 196, 88, 'red', 2) + cap('The connector’s files are deleted too.', 'Other consumers lose their data.', 'red', y=150, h=46))
f4 = (t(180, 22, 'What we saw in the lab', 9.6, bold=True) + term([('> ALTER TABLE scratch_copy SET TBLPROPERTIES', W), ("  ('external.table.purge'='true');", W), ('> DROP TABLE scratch_copy;', W), ('$ ls /data/tiffingo/scratch_copy', W), ('ls: cannot access …: No such file or directory', RD)], label='real output', size=7.6, y0=60).replace('y="14" width="332" height="196"', 'y="32" width="332" height="120"').replace('y="30" font-size="9"', 'y="46" font-size="9"'))
f5 = (t(180, 22, 'Guard rails', 9.6, 'green', bold=True) + ''.join(t(24, 50 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• Landing tables: external, purge = false', '• Only admins may ALTER table properties', '• Snapshots or versioning on landing folders', '• Run DESCRIBE FORMATTED before any DROP'])) +
      cap('Ownership is a policy, not just a keyword.', '', 'green', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'The purge flag that deleted a shared folder',
              'External tables protect shared files only while purge is off. Follow a realistic incident and the guard rails that prevent it.',
              'Shared folders', 'A landing folder written by a connector and read by a Hive external table is deleted after the purge flag is switched on and the table dropped', [f1, f2, f3, f4, f5],
              ['A connector writes event files to a landing folder; a Hive external table reads them.',
               'Someone sets external.table.purge to true so that DROP “cleans up”.',
               'Months later a clean-up script drops the table and the folder is deleted, connector files included.',
               'We reproduced this in the lab: after the property change and DROP, the folder no longer existed.',
               'Keep purge off on shared folders, restrict ALTER, protect landing data with snapshots, and check before dropping.'],
              hid='scenario-purge')

# ---- scenario 2: delete failed, orphan files
o1 = (t(180, 22, 'DROP is two steps', 9.6, bold=True) + label_box(20, 50, 140, 50, ['1 · metastore', 'remove table rows'], 'violet', 8.4) + arrow(162, 75, 196, 75) + label_box(198, 50, 140, 50, ['2 · storage', 'delete the folder'], 'acc', 8.4) +
      cap('Step 2 runs as the metastore’s user.', 'It needs permission on the folder.', 'blue', y=150, h=46))
o2 = (t(180, 22, 'Step 2 fails: permission denied', 9.6, 'red', bold=True) + label_box(20, 50, 140, 50, ['1 · metastore', 'done ✓'], 'green', 8.4) + arrow(162, 75, 196, 75, 'red') + label_box(198, 50, 140, 50, ['2 · storage', 'failed ✗'], 'red', 8.4) +
      cap('Beeline still reports success.', 'The table is gone; the files are not.', 'red', y=150, h=46))
o3 = term([('$ docker logs metastore | grep Failed', W), ('WARN … fs.FileUtil: Failed to delete', Y), ('  file or dir [/data/tiffingo/', Y), ('  scratch_copy/customers.csv]:', Y), ('  it still exists.', Y), ('ERROR … utils.FileUtils: Failed to delete', RD), ('  file:/data/tiffingo/scratch_copy', RD)], label='metastore log · real output', size=7.6)
o4 = (t(180, 22, 'Orphan files', 9.6, bold=True) + box(60, 46, 240, 70, 'amber') + t(180, 66, '/data/tiffingo/scratch_copy/', 8.4, bold=True, mono=True) + t(180, 84, 'customers.csv (91,618 B)', 8, 'ink2', mono=True) + t(180, 102, 'no table points here', 8.4, 'red', bold=True) +
      cap('They cost storage and confuse the next person.', 'A new table on this path would see old rows.', 'amber', y=150, h=46))
o5 = (t(180, 22, 'Prevent and detect', 9.6, 'green', bold=True) + ''.join(t(24, 50 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• Correct ownership/ACLs for the hive user', '• Alert on “Failed to delete” in metastore logs', '• Regular job: folders with no table → report', '• Fix permissions, then remove orphans'])) +
      cap('Silent failures need monitoring.', '', 'green', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'DROP succeeded, but the files stayed',
              'This happened in our lab before we fixed folder permissions. It also happens on real clusters.',
              'Orphan files', 'A DROP removes metastore rows but fails to delete files because of permissions, leaving orphan files', [o1, o2, o3, o4, o5],
              ['DROP first removes the table from the metastore, then deletes the folder as the metastore’s user.',
               'If the user may not delete the files, the second step fails but the client still sees success.',
               'Only the metastore log tells the truth: Failed to delete … it still exists.',
               'The files are now orphans: no table uses them, and a future table on the same path would read them.',
               'Fix permissions, monitor the logs and run a regular orphan check.'],
              hid='scenario-orphans')

# ---- scenario 3: choose the type
c1 = (t(180, 22, 'Decide the type: three questions', 9.6, bold=True) + ''.join(t(24, 52 + k * 22, s, 8.8, anchor='start') for k, s in enumerate(['1. Does another tool write or read these files?', '2. Will rows be updated or deleted?', '3. Should DROP delete the data?'])) + cap('Answer before you write CREATE.', '', 'blue', y=150, h=34))
c2 = (t(180, 22, 'Landing data from a partner', 9.6, bold=True) + t(180, 52, 'other tool writes: yes · updates: no · DROP deletes: no', 8, 'ink2') + node(90, 70, 180, 50, 'EXTERNAL', 'purge = false', 'green') + cap('raw.partner_orders', '', 'green', y=150, h=34))
c3 = (t(180, 22, 'Orders with refunds and corrections', 9.6, bold=True) + t(180, 52, 'other tool writes: no · updates: yes · DROP deletes: yes', 8, 'ink2') + node(90, 70, 180, 50, 'MANAGED ACID', "ORC, transactional=true", 'blue') + cap('tiffingo.orders', '', 'blue', y=150, h=34))
c4 = (t(180, 22, 'A step inside a nightly job', 9.6, bold=True) + t(180, 52, 'other tool writes: no · updates: no · DROP deletes: yes', 8, 'ink2') + node(90, 70, 180, 50, 'CREATE TABLE', '→ external + purge', 'acc') + cap('tmp_daily_city_totals', '', 'acc', y=150, h=34))
c5 = (t(180, 22, 'Spark writes, Hive and Trino read', 9.6, bold=True) + t(180, 52, 'other tool writes: yes · updates: yes · DROP deletes: maybe', 8, 'ink2') + node(90, 70, 180, 50, 'EXTERNAL Iceberg', 'table format handles commits', 'violet') + cap('Module 7 covers Iceberg tables.', '', 'violet', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Pick the right type for four TiffinGo tables',
              'Three questions decide the type. See them applied to four real situations.',
              'Choosing a type', 'Three questions applied to landing data, corrected orders, a temporary step and a multi-engine table', [c1, c2, c3, c4, c5],
              ['Ask: who else touches the files, will rows change, and should DROP delete data?',
               'Partner files that other systems use: external, purge off.',
               'Orders that need refunds and corrections: managed ACID ORC.',
               'A temporary step in a nightly job: plain CREATE TABLE (external with purge in Hive 4).',
               'Data written by Spark and read by several engines with updates: an external Iceberg table.'],
              hid='scenario-choose')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Same data, three owners: seven frames</h2>
  <p>Left: Beeline and its real output. Right: the metadata and the files of each table after every statement.</p>
''' + two + '''
  <p>Three live scenarios follow: the purge flag, orphan files after a failed delete, and choosing a type.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Where each type is used</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, '/landing/', 8.4, 'green', bold=True, mono=True) + t(60, 58, 'external', 7.4, 'ink2'),
    '1. Landing zones',
    'Files arriving from apps, payment gateways or partners land in a folder that ingestion tools own. Hive external tables let analysts query them the same day without copying.',
    ['Source system', '*External table', 'Analysts']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'MERGE', 9, 'blue', bold=True, mono=True) + t(60, 58, 'ACID', 7.4, 'ink2'),
    '2. Tables that get corrected',
    'Order status changes from DELIVERED to REFUNDED days later. A managed ACID table takes a nightly MERGE of changes instead of rewriting the whole table.',
    ['Changes', '*MERGE into ACID', 'Current orders']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'Spark · Trino', 8, 'acc', bold=True) + t(60, 58, 'same files', 7.4, 'ink2'),
    '3. Multi-engine data lakes',
    'When Spark writes Parquet and Hive, Trino and BI tools read it, the tables are external so no single engine can delete the data by accident. Newer lakes use Iceberg tables for safe concurrent writes.',
    ['Spark writes', '*External / Iceberg', 'Many readers']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'tmp_', 9, 'acc', bold=True, mono=True) + t(60, 58, 'purge on', 7.4, 'ink2'),
    '4. Work tables in pipelines',
    'A nightly job builds intermediate tables and drops them at the end. Because they are purge tables, DROP removes the files and storage does not fill up.',
    ['Step 1', '*Work table', 'DROP at end']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:#D64545"/>' + t(60, 42, 'audit', 9, 'red', bold=True) + t(60, 58, 'type + purge', 7.4, 'ink2'),
    '5. Pre-upgrade audits',
    'Before moving to Hive 3 or 4, platform teams list every table’s type, purge flag and location, because the meaning of “managed” changed and DROP behaviour must stay what users expect.',
    ['Inventory', '*Check types', 'Safe upgrade']) + '''
  <p class="muted">Examples are simplified. Policies differ between companies.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> finish <a href="../01-databases-and-tables/">Lesson 2.1</a>, where a plain CREATE TABLE turned into an EXTERNAL_TABLE. This lesson explains why.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
