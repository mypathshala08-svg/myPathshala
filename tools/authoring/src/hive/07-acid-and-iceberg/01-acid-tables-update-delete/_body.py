import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()

def folder(x, y, label, tone='card', w=96, sub=''):
    o = box(x, y, w, 30, tone) + t(x + w / 2, y + 13, label, 6.8, 'ink', mono=True, bold=True)
    if sub:
        o += t(x + w / 2, y + 25, sub, 6.4, 'ink2')
    return o

# ---------------------------------------------------------------- story
sc = (box(10, 12, 300, 128, 'card') + t(160, 30, 'Before: no UPDATE in Hive', 8.8, bold=True) +
      t(22, 54, '1. copy the whole table without the row', 7.6, 'ink2', anchor='start') + t(22, 70, '2. INSERT OVERWRITE everything back', 7.6, 'ink2', anchor='start') + t(22, 86, '3. hope nobody read it meanwhile', 7.6, 'red', anchor='start') +
      t(160, 120, '50,000 rows rewritten to fix 1', 8, 'red', bold=True) +
      box(330, 12, 300, 128, 'green') + t(480, 30, 'ACID table: UPDATE / DELETE', 8.8, 'green', bold=True) +
      folder(344, 46, 'delta_1', 'card', 84, 'insert') + folder(436, 46, 'delete_delta_2', 'acc', 90, 'old row out') + folder(534, 46, 'delta_2', 'green', 84, 'new row in') +
      t(480, 104, 'old files never change; new small files', 7.6, 'ink2') + t(480, 122, 'readers merge them on the fly', 7.6, 'green', bold=True))
scene_svg = scene('Without ACID, fixing one row means rewriting the whole table. With an ACID table, an UPDATE writes a small delete_delta file that removes the old row and a delta file with the new row; readers merge them.', sc,
                  'ACID tables turn UPDATE and DELETE into <tspan font-weight="700" class="s-acc">small new files</tspan> that readers merge, never edits in place.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“A customer upgraded to Gold. Do we rewrite the whole table?”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s support team changes customer plans, refunds cancelled orders and deletes test accounts every day. Kabir’s tables are plain Hive tables, and his first <code>UPDATE</code> fails with “table … is not transactional”. The old workaround was to rewrite a whole table or partition for every correction.</p>

{scene_svg}

K> Sir, HDFS files cannot be edited. How can Hive UPDATE anything?
A> It never edits a file. On a <b>transactional (ACID)</b> table, an UPDATE writes two small new folders: a <code>delete_delta</code> that says “row 1 of write 1 is gone”, and a <code>delta</code> with the new version. A reader opens the base data plus all deltas and merges them. Each statement is its own transaction, so readers see either all of it or none.
R> Then the folder fills up with deltas?
A> Yes, and a background <b>compactor</b> merges them (Lesson 7.3). Today we create ACID tables, run INSERT, UPDATE and DELETE, read the real delta files, see the hidden <code>ROW__ID</code>, and collect the errors you will meet: non-transactional tables, partition columns, external tables, BEGIN TRANSACTION and insert-only tables. All outputs are real, from Hive 4.2.1.
  </div>
</section>
'''

lv = '''
LEVELS> ACID tables at three levels
L1> A notebook you never erase
      <ul>
        <li>Imagine a register written in pen. To change an entry you do not erase it: you add a note at the end, “entry 2 is cancelled, new entry: …”.</li>
        <li>Whoever reads the register reads the original pages and all the notes, and works out the current state.</li>
        <li>That is how Hive ACID tables work on HDFS, where files cannot be edited.</li>
      </ul>
L2> What ACID means in Hive
      <ul>
        <li><b>A</b>tomic: a statement is all or nothing. <b>C</b>onsistent and <b>I</b>solated: readers see a snapshot of committed writes (snapshot isolation). <b>D</b>urable: committed data stays.</li>
        <li>Create with <code>TBLPROPERTIES ('transactional'='true')</code> on a <b>managed ORC</b> table. Needs <code>hive.support.concurrency=true</code> and <code>hive.txn.manager=…DbTxnManager</code> (already set in our lab).</li>
        <li>Every write gets a <b>write id</b>; data goes into <code>delta_&lt;from&gt;_&lt;to&gt;_&lt;stmt&gt;</code>, deletes into <code>delete_delta_…</code>, and after major compaction into <code>base_&lt;writeid&gt;</code>.</li>
        <li>Each row has a hidden <code>ROW__ID</code> (writeid, bucketid, rowid) that deletes refer to.</li>
        <li><b>Insert-only</b> tables (<code>'transactional_properties'='insert_only'</code>) work with any format but allow only INSERT.</li>
      </ul>
L3> What Hive 4.2.1 did (and refused) in our lab
      <ul>
        <li>An ACID table needed <b>no buckets</b> (Num Buckets −1). Old documentation saying “must be bucketed” describes Hive 1.x/2.x.</li>
        <li>UPDATE = delete_delta (old row, by ROW__ID) + delta (new row) <b>in the same write id</b>; only the touched partitions got new folders.</li>
        <li>Each statement auto-commits: <code>START TRANSACTION</code> → “not supported yet”.</li>
        <li>Refused: UPDATE on a non-ACID table (10297), on a partition column (10292), on an insert-only table (10414), and an EXTERNAL transactional table.</li>
        <li><code>DELETE … WHERE id IN (SELECT …)</code> worked: subqueries are allowed in the WHERE of UPDATE and DELETE.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>ACID (transactional) tables in Hive</h2>
''' + def_block(
    'A <b>transactional table</b> (ACID table) is a managed table, stored as ORC for full support, declared with <code>TBLPROPERTIES (\'transactional\'=\'true\')</code>, on which Hive supports <code>INSERT</code>, <code>UPDATE</code>, <code>DELETE</code> and <code>MERGE</code> with <b>atomicity</b>, <b>consistency</b>, <b>isolation</b> (snapshot isolation) and <b>durability</b>. Each statement runs in its own transaction managed by the metastore. Changes are written as new <b>delta</b> and <b>delete_delta</b> directories identified by write ids; readers merge the base and delta files at read time, and a <b>compactor</b> periodically rewrites them into fewer files.',
    'An ACID table is a Hive table you can UPDATE and DELETE. Hive never changes old files; it adds small files describing the changes, and every reader combines them. Each statement either fully happens or not at all.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Transactional table', 'Managed ORC table with <code>transactional=true</code>.'),
    ('Write id', 'A number per table for each write; appears in folder names.'),
    ('delta_x_y_s', 'New rows from write ids x to y (statement s).'),
    ('delete_delta_x_y_s', 'Row ids deleted by write ids x to y.'),
    ('base_N', 'All data up to write N after major compaction (7.3).'),
    ('ROW__ID', 'Hidden struct (writeid, bucketid, rowid) identifying each row.'),
    ('Snapshot isolation', 'A query sees the data as of when it started; later commits are invisible to it.'),
    ('Insert-only table', 'Transactional table that allows INSERT only, in any file format.'),
]) + '''

  <h3>Regular vs insert-only vs full ACID</h3>
''' + table(['', 'Regular (external) table', 'Insert-only ACID', 'Full ACID'], [
    ['Property', '(none)', "<code>transactional=true</code>, <code>transactional_properties=insert_only</code>", "<code>transactional=true</code>"],
    ['File format', 'Any', 'Any (we used TEXTFILE)', 'ORC'],
    ['INSERT', 'Yes', 'Yes, atomic', 'Yes, atomic'],
    ['UPDATE / DELETE / MERGE', 'No (Error 10297)', 'No (Error 10414)', 'Yes'],
    ['Table type', 'External or managed', 'Managed', 'Managed (external refused)'],
    ['Folders', 'Plain files', '<code>delta_N_N_0/000000_0</code>', '<code>delta_…</code>, <code>delete_delta_…</code>, <code>base_…</code>'],
], minw=720) + lv + '''
EXAM> “How does Hive support UPDATE and DELETE when HDFS files are immutable?” Answer: ACID tables write changes as new delta and delete_delta directories tagged with write ids; readers merge base and deltas using the hidden ROW__ID; compaction later merges them. Mention the requirements: managed ORC table, <code>transactional=true</code>, DbTxnManager, and that each statement auto-commits.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>DML on ACID tables</h2>
''' + table(['Statement', 'Example', 'Writes'], [
    ['INSERT', "<code>INSERT INTO cust_acid VALUES (6, 'Diya Patil', 'Pune', 'Silver');</code>", '<code>delta_N_N_0000</code>'],
    ['UPDATE', "<code>UPDATE cust_acid SET plan = 'Gold' WHERE customer_id = 2;</code>", '<code>delete_delta_N…</code> + <code>delta_N_N_0001</code>'],
    ['DELETE', '<code>DELETE FROM cust_acid WHERE customer_id = 5;</code>', '<code>delete_delta_N…</code>'],
    ['DELETE with subquery', '<code>DELETE FROM t WHERE id IN (SELECT id FROM …);</code>', 'delete_delta in touched partitions only'],
    ['MERGE', '<code>MERGE INTO t USING s ON … WHEN MATCHED … WHEN NOT MATCHED …</code>', 'Lesson 7.2'],
    ['Compaction', "<code>ALTER TABLE t COMPACT 'major';</code>", 'Lesson 7.3'],
], minw=720) + '''
''' + table(['Command', 'Shows'], [
    ['<code>SHOW TRANSACTIONS;</code>', 'Open and aborted transactions'],
    ['<code>SHOW LOCKS;</code>', 'Locks held, including the metastore’s own housekeeping locks'],
    ['<code>SHOW COMPACTIONS;</code>', 'Queued, running and finished compactions (7.3)'],
    ['<code>SELECT ROW__ID, * FROM t;</code>', 'Which write created each row version'],
], minw=560) + '''
WARN> ACID is designed for <b>occasional</b> corrections and batch upserts on large tables, not for a stream of single-row updates like an OLTP database. Each statement is a transaction with metastore round trips and new files; thousands of tiny updates create thousands of deltas. Batch them into one UPDATE or MERGE.
</section>
'''

dml = tables(capf('l71_dml.txt'))
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Kabir’s first transactional table</h2>
  <p>All outputs are real, from the Hive 4.2.1 lab (database <code>tiffingo</code>).</p>
''' + stepper([
    ('Step 1 · The settings behind ACID',
     code('sql', 'Beeline', "SET hive.support.concurrency;\nSET hive.txn.manager;\nSET hive.create.as.acid;", '| hive.support.concurrency=true |\n| hive.txn.manager=org.apache.hadoop.hive.ql.lockmgr.DbTxnManager |\n| hive.create.as.acid=false |'),
     'The transaction manager keeps transactions, write ids and locks in the metastore database. Our lab image has it switched on. <code>hive.create.as.acid=false</code> means tables are not transactional unless you ask (some vendor distributions make every managed table ACID by default).'),
    ('Step 2 · Create a transactional table and insert',
     code('sql', 'Beeline', "CREATE TABLE cust_acid (customer_id INT, name STRING, city STRING, plan STRING)\nSTORED AS ORC TBLPROPERTIES ('transactional'='true');\nINSERT INTO cust_acid SELECT customer_id, name, city, plan FROM customers WHERE customer_id <= 5;\nSELECT * FROM cust_acid ORDER BY customer_id;\nDESCRIBE FORMATTED cust_acid;     -- selected lines",
          tables(capf('l71_create.txt'))[0] + '\n\n| Table Type:   | MANAGED_TABLE |\n|               | transactional             | true    |\n|               | transactional_properties  | default |\n| Num Buckets:  | -1            |'),
     'Unlike our earlier plain CREATE TABLEs, which Hive 4 turned into external tables, this one is <b>MANAGED</b>: Hive must own the files to manage deltas. <code>transactional_properties=default</code> means full ACID. No buckets were needed.'),
    ('Step 3 · UPDATE, DELETE and another INSERT',
     code('sql', 'Beeline', "UPDATE cust_acid SET plan = 'Gold' WHERE customer_id = 2;\nDELETE FROM cust_acid WHERE customer_id = 5;\nINSERT INTO cust_acid VALUES (6, 'Diya Patil', 'Pune', 'Silver');\nSELECT * FROM cust_acid ORDER BY customer_id;", dml[0]),
     'Ananya is now Gold, Aarav Singh (5) is gone, Diya (6) is new. Each statement committed on its own; there is no BEGIN … COMMIT around them.'),
    ('Step 4 · What changed on disk',
     code('bash', 'Terminal', "find /opt/hive/data/warehouse/tiffingo.db/cust_acid | sort", capf('l71_layout1.txt').split('\n', 1)[1]),
     'Four statements, five folders, and no existing file was modified. The folder names carry the write id twice (a range, so compaction can merge several) and a statement number. The UPDATE produced a delete_delta and a delta with the <b>same write id 2</b>: it is one transaction.'),
    ('Step 5 · Read the delta files',
     code('bash', 'Terminal', "hive --orcfiledump -d <folder>/bucket_00000_0", capf('l71_dump.txt')),
     'A delete record stores no data, only which row it kills: “row 1 of write 1” (customer 2’s old version) and “row 4 of write 1” (customer 5). Operation 0 is an insert, 2 a delete. The new version of customer 2 is a fresh row created by write 2. This is how Hive “updates” immutable files.'),
    ('Step 6 · The hidden ROW__ID',
     code('sql', 'Beeline', "SELECT ROW__ID, customer_id, plan FROM cust_acid ORDER BY customer_id;", dml[1]),
     'Customers 1, 3 and 4 still come from write 1 (rows 0, 2, 3). Customer 2 now comes from write 2 and customer 6 from write 4. Readers drop any row whose (writeid, bucketid, rowid) appears in a delete_delta. The bucketid value also encodes the statement number, which is why the updated row shows 536870913.'),
    ('Step 7 · Partitioned ACID: refunds in one day',
     code('sql', 'Beeline', "CREATE TABLE orders_acid (order_id INT, customer_id INT, amount DECIMAL(10,2), status STRING)\nPARTITIONED BY (order_date DATE) STORED AS ORC TBLPROPERTIES ('transactional'='true');\nINSERT INTO orders_acid PARTITION (order_date)\n  SELECT order_id, customer_id, amount, status, order_date FROM orders WHERE order_date <= '2026-10-03';\n\nUPDATE orders_acid SET status = 'REFUNDED' WHERE order_date = '2026-10-02' AND status = 'CANCELLED';\nDELETE FROM orders_acid WHERE order_id IN\n  (SELECT order_id FROM orders WHERE order_date = '2026-10-03' AND amount < 50);\n\nSELECT order_date, status, COUNT(*) AS n FROM orders_acid GROUP BY order_date, status;\n$ find …/orders_acid -maxdepth 2 -type d",
          tables(capf('l71_refund.txt'))[0] + '\n\n./order_date=2026-10-01/delta_0000001_0000001_0000\n./order_date=2026-10-02/delete_delta_0000002_0000002_0000\n./order_date=2026-10-02/delta_0000001_0000001_0000\n./order_date=2026-10-02/delta_0000002_0000002_0001\n./order_date=2026-10-03/delete_delta_0000003_0000003_0000\n./order_date=2026-10-03/delta_0000001_0000001_0000'),
     'All 102 cancelled orders of 2 October became refunds (39 + 102 = 141), and 40 cheap orders of 3 October were deleted (1,668 → 1,628). Partition pruning works for DML too: 1 October was not touched, and each change landed only in its own partition folder.'),
    ('Step 8 · What ACID refuses',
     code('sql', 'Beeline', "UPDATE customers …;  START TRANSACTION;  CREATE EXTERNAL TABLE … transactional …;\nUPDATE orders_acid SET order_date = …;  UPDATE events_mm …;", capf('l71_errors.txt')),
     'Five real refusals: the table must be transactional and managed; there are no multi-statement transactions; you cannot move a row to another partition with UPDATE (delete and insert it instead); and insert-only tables accept only INSERT.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([("> UPDATE customers SET plan = 'Gold' …;", W), ('Error 10297: … not transactional', RD), ("> CREATE TABLE cust_acid (…) STORED AS ORC", W), ("    TBLPROPERTIES ('transactional'='true');", W), ('| Table Type: MANAGED_TABLE |', G)]),
    term([('> INSERT INTO cust_acid SELECT … ;', W), ('  delta_0000001_0000001_0000/', G), ('| 1 | Aarav Desai | … | Silver |', G), ('| 2 | Ananya Iyer | … | Basic  |', G)]),
    term([("> UPDATE cust_acid SET plan = 'Gold'", W), ('    WHERE customer_id = 2;', W), ('  delete_delta_0000002_0000002_0000/', Y), ('  delta_0000002_0000002_0001/', G), ('| 2 | Ananya Iyer | … | Gold |', G)]),
    term([('> DELETE FROM cust_acid WHERE customer_id = 5;', W), ('  delete_delta_0000003_0000003_0000/', Y), ('{"operation":2,"originalTransaction":1,', Y), (' "rowId":4,"row":null}', Y)], size=7.6),
    term([('> SELECT ROW__ID, customer_id, plan …;', W), ('| {"writeid":1,…,"rowid":0} | 1 | Silver |', G), ('| {"writeid":2,…,"rowid":0} | 2 | Gold   |', G), ('| {"writeid":4,…,"rowid":0} | 6 | Silver |', G)], size=7.4),
]
def rowbox(x, y, label, tone='card', strike=False):
    o = box(x, y, 140, 18, tone) + t(x + 6, y + 13, label, 7, 'ink', anchor='start', mono=True)
    if strike:
        o += f'<line x1="{x + 4}" y1="{y + 9}" x2="{x + 136}" y2="{y + 9}" stroke="#D64545" stroke-width="1.6"/>'
    return o
B1 = [
    t(180, 22, 'Transactional = managed + metastore-tracked', 9.4, bold=True) + box(20, 44, 150, 70, 'violet') + t(95, 62, 'metastore', 8.2, bold=True) + t(95, 80, 'TXNS · write ids', 7.2, 'ink2', mono=True) + t(95, 94, 'locks', 7.2, 'ink2', mono=True) +
    arrow(172, 78, 196, 78, 'ink3') + box(198, 44, 142, 70, 'blue') + t(269, 62, 'cust_acid/', 8.2, bold=True, mono=True) + t(269, 82, 'Hive owns the files', 7.2, 'ink2') + cap('External tables cannot be ACID.', '', 'blue', y=150, h=34),
    t(180, 22, 'Write 1: a delta folder', 9.4, bold=True) + folder(20, 40, 'delta_1_1_0', 'green', 120) + ''.join(rowbox(160, 38 + k * 20, f'w1 r{k}  customer {k + 1}') for k in range(5)) + cap('Rows numbered within the write.', '', 'green', y=150, h=34),
    t(180, 22, 'Write 2: UPDATE = delete + insert', 9.4, bold=True) + rowbox(20, 46, 'w1 r1  customer 2 Basic', 'red', strike=True) + folder(20, 70, 'delete_delta_2', 'acc', 140, 'w1 r1 is dead') +
    rowbox(200, 46, 'w2 r0  customer 2 Gold', 'green') + folder(200, 70, 'delta_2_2_0001', 'green', 140, 'new version') + cap('Both parts share write id 2: atomic.', '', 'green', y=150, h=34),
    t(180, 22, 'Write 3: DELETE records row ids only', 9.4, bold=True) + rowbox(20, 50, 'w1 r4  customer 5', 'red', strike=True) + folder(200, 44, 'delete_delta_3', 'acc', 140, '{w1, r4}') + cap('No data copied, just “this row is gone”.', '', 'amber', y=150, h=34),
    t(180, 22, 'Reader: merge base + deltas', 9.4, bold=True) + ''.join(rowbox(20, 36 + k * 20, s, tone, strike=st) for k, (s, tone, st) in enumerate([('w1 r0  customer 1', 'card', False), ('w1 r1  customer 2', 'red', True), ('w1 r2  customer 3', 'card', False), ('w1 r3  customer 4', 'card', False), ('w1 r4  customer 5', 'red', True)])) +
    rowbox(200, 46, 'w2 r0  customer 2 Gold', 'green') + rowbox(200, 70, 'w4 r0  customer 6', 'green') + cap('Skip deleted ROW__IDs, add new rows.', '', 'blue', y=150, h=34),
]
see_caps = ['UPDATE fails on a plain table; a transactional table is managed.',
            'The first INSERT creates a delta folder for write 1.',
            'UPDATE writes a delete_delta and a delta in the same write.',
            'DELETE writes only the id of the dead row.',
            'ROW__ID shows which write produced each visible row.']
behind_caps = ['The metastore tracks transactions, write ids and locks for transactional tables.',
               'Each row is identified by its write id and row number.',
               'The old version is marked deleted and a new version is written; old files stay untouched.',
               'A delete record points at (write, bucket, row) with no data.',
               'Readers combine all folders, skipping rows listed in delete deltas.']
two = anim_two('ACID tables', 'Deltas, delete deltas and ROW__ID', 'Real Beeline output', 'What the metastore and the folders record', see, B1, see_caps, behind_caps)

# ---- scenario 1: GDPR-like deletion
g1 = (t(180, 22, 'A customer asks to delete their data', 9.4, bold=True) + t(180, 56, 'privacy rules: remove within a deadline', 8.4, 'ink2') + cap('Plain tables: rewrite every partition with that customer.', '', 'amber', y=150, h=34))
g2 = (t(180, 22, 'ACID: one DELETE per table', 9.4, bold=True) + t(180, 56, 'DELETE FROM orders_acid WHERE customer_id = 1492;', 7.8, 'ink', mono=True) + cap('Delete deltas in the partitions that hold the customer.', '', 'green', y=150, h=34))
g3 = (t(180, 22, 'Is the data really gone?', 9.4, bold=True) + t(180, 56, 'old rows still sit in older delta files', 8.4, 'red') + t(180, 74, 'until compaction rewrites them', 8.4, 'ink2') + cap('Logically deleted ≠ physically deleted.', '', 'amber', y=150, h=34))
g4 = (t(180, 22, 'Finish the job', 9.4, bold=True) + t(180, 56, "ALTER TABLE … COMPACT 'major' (Lesson 7.3)", 8.4, 'ink', mono=True) + cap('Major compaction writes a base without the rows.', '', 'green', y=150, h=34))
g5 = (t(180, 22, 'Batch the requests', 9.4, 'acc', bold=True) + t(180, 56, 'collect a day of requests → one DELETE … IN (SELECT …)', 7.8, 'ink2', mono=True) + cap('One transaction instead of hundreds.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Deleting one customer’s data on request',
              'Data-protection requests are a classic reason for ACID tables. (Typical process; the DELETE pattern ran in our lab.)',
              'Right to erasure', 'ACID DELETE marks a customer’s rows deleted in delete deltas; major compaction removes them physically; requests are batched', [g1, g2, g3, g4, g5],
              ['A customer requests deletion of their data.',
               'One DELETE per table marks the rows.',
               'The old row versions remain in files until compaction.',
               'Major compaction rewrites the data without them.',
               'Batch daily requests into one statement.'],
              hid='scenario-erasure')

# ---- scenario 2: late corrections
c1 = (t(180, 22, 'Payments team: 102 orders were refunded', 9.4, bold=True) + t(180, 56, 'status must change from CANCELLED to REFUNDED', 8.2, 'ink2') + cap('Correcting yesterday’s data.', '', 'blue', y=150, h=34))
c2 = term([("> UPDATE orders_acid SET status = 'REFUNDED'", W), ("    WHERE order_date = '2026-10-02'", W), ("      AND status = 'CANCELLED';", W), ('| 2026-10-02 | REFUNDED | 141 |', G)], label='real output · Hive 4.2.1')
c3 = (t(180, 22, 'Only one partition touched', 9.4, bold=True) + folder(20, 50, 'date=10-01', 'card', 100, 'unchanged') + folder(130, 50, 'date=10-02', 'green', 100, '+2 folders') + folder(240, 50, 'date=10-03', 'card', 100, 'unchanged') + cap('Partition pruning applies to UPDATE too.', '', 'green', y=150, h=34))
c4 = (t(180, 22, 'Readers never see half an update', 9.4, bold=True) + t(180, 56, 'a report started before the commit sees the old state', 8, 'ink2') + cap('Snapshot isolation.', '', 'blue', y=150, h=34))
c5 = (t(180, 22, 'Prefer one big statement', 9.4, 'acc', bold=True) + t(180, 56, '102 single-row UPDATEs = 102 transactions, 204 folders', 7.8, 'red', mono=True) + cap('One set-based UPDATE = 1 transaction, 2 folders.', '', 'green', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Correcting a day of orders safely',
              'A set-based UPDATE on one partition, with real results.',
              'Data corrections', 'A single UPDATE converts a day of cancelled orders to refunds, touching only that partition, atomically', [c1, c2, c3, c4, c5],
              ['The payments team sends a correction.',
               'One UPDATE fixes all 102 orders.',
               'Only that day’s partition gets new delta folders.',
               'Readers see either the old or the new state, never a mix.',
               'Avoid row-by-row updates.'],
              hid='scenario-corrections')

# ---- scenario 3: choosing table type
k1 = (t(180, 22, 'Which tables should be ACID?', 9.4, bold=True) + t(180, 56, 'not every table needs UPDATE', 8.4, 'ink2') + cap('ACID adds files, locks and compaction work.', '', 'blue', y=150, h=34))
k2 = (t(180, 22, 'Append-only facts (clicks, logs)', 9.4, bold=True) + t(180, 56, 'external or insert-only tables', 8.4, 'ink', mono=True) + cap('Re-load whole partitions to fix them.', '', 'green', y=150, h=34))
k3 = (t(180, 22, 'Dimensions that change (customers)', 9.4, bold=True) + t(180, 56, 'full ACID + MERGE (Lesson 7.2)', 8.4, 'ink', mono=True) + cap('Upserts every night.', '', 'green', y=150, h=34))
k4 = (t(180, 22, 'Shared with Spark / Trino?', 9.4, bold=True) + t(180, 56, 'Hive ACID support varies by engine', 8.4, 'ink2') + t(180, 74, 'Iceberg is engine-neutral (Lesson 7.3)', 8.4, 'green', bold=True) + cap('Check every reader before choosing.', '', 'amber', y=150, h=34))
k5 = (t(180, 22, 'Rule of thumb', 9.4, 'acc', bold=True) + t(180, 56, 'ACID or Iceberg only where rows really change', 8.4, 'ink2') + cap('Keep the rest simple.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Choosing between external, insert-only, ACID and Iceberg',
              'A design decision every Hive warehouse faces. (Typical guidance.)',
              'Table type choice', 'Append-only data stays in external or insert-only tables; changing dimensions use ACID with MERGE; multi-engine tables consider Iceberg', [k1, k2, k3, k4, k5],
              ['ACID has costs, so use it where needed.',
               'Append-only facts do not need UPDATE.',
               'Changing dimensions are the classic ACID use.',
               'If other engines must write the table, consider Iceberg.',
               'Use transactional tables only where rows change.'],
              hid='scenario-choice')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>How an UPDATE becomes two small folders</h2>
  <p>Left: real Beeline output. Right: what the metastore and the folders record.</p>
''' + two + '''
  <p>Three live scenarios follow: deleting a customer’s data, correcting a day of orders, and choosing a table type.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>ACID tables at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'DELETE', 11, 'green', bold=True, mono=True) + t(60, 58, 'privacy', 7.4, 'ink2'),
    '1. Privacy deletions',
    'Data-protection laws such as India’s DPDP Act and Europe’s GDPR give people rights over their personal data; ACID DELETE plus compaction removes a person’s rows without rebuilding tables.',
    ['Request', '*DELETE + compact', 'Data removed']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'UPDATE', 11, 'blue', bold=True, mono=True) + t(60, 58, 'corrections', 7.4, 'ink2'),
    '2. Late corrections',
    'Refunds, chargebacks and status changes arrive after the original load; a set-based UPDATE fixes them in the right partitions.',
    ['Correction feed', '*UPDATE', 'Accurate reports']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'MERGE', 11, 'violet', bold=True, mono=True) + t(60, 58, 'upserts', 7.4, 'ink2'),
    '3. Nightly upserts from databases',
    'Changes from MySQL or PostgreSQL (CDC) are merged into Hive dimension tables every night with MERGE (Lesson 7.2).',
    ['CDC changes', '*MERGE', 'Current dimensions']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'atomic', 11, 'acc', bold=True) + t(60, 58, 'no half loads', 7.4, 'ink2'),
    '4. Atomic loads',
    'Insert-only transactional tables guarantee that a failed load leaves no partial files visible to readers.',
    ['Load job', '*insert-only ACID', 'All or nothing']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'streaming', 10, 'acc', bold=True) + t(60, 58, 'ingest', 7.4, 'ink2'),
    '5. Streaming ingestion',
    'Hive’s streaming API writes micro-batches as transactions into ACID tables, so data is queryable within minutes (with compaction keeping deltas in check).',
    ['Events', '*transactions', 'Fresh table']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> you need managed vs external tables (<a href="../../02-hiveql/02-managed-vs-external-tables/">2.2</a>), partitions (<a href="../../05-partitioning-and-bucketing/01-partitioning/">5.1</a>) and ORC (<a href="../../06-file-formats/02-orc-deep-dive/">6.2</a>).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
