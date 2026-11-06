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
    module='07-acid-and-iceberg', lesson='01-acid-tables-update-delete', n='7.1',
    module_label='Module 7 · Transactions, MERGE and Iceberg',
    title='ACID tables: INSERT, UPDATE and DELETE',
    desc='Hive ACID transactional tables explained with real Hive 4.2.1 results: transactional=true on managed ORC tables, DbTxnManager, delta and delete_delta folders with write ids, what an UPDATE and a DELETE really write (orcfiledump of delete records), the hidden ROW__ID, partitioned ACID tables, DELETE with a subquery, insert-only tables, and the errors you meet: non-transactional tables, partition columns, external tables and START TRANSACTION.',
    og_desc='HDFS files cannot be edited, so how does Hive UPDATE a row? Real delta folders, delete records and ROW__ID from a Hive 4.2.1 lab.',
    minutes=35, level='Beginner → Advanced',
    lead='HDFS files can only be written once, yet Hive can UPDATE and DELETE rows. In this lesson Kabir creates <b>transactional (ACID) tables</b>, runs INSERT, UPDATE and DELETE, and then looks inside the folders to see exactly what Hive wrote: small <code>delta</code> and <code>delete_delta</code> files, linked by a hidden <code>ROW__ID</code>. He also collects the five errors that trip up beginners. <b>All outputs are real</b>, from Hive 4.2.1.',
    chips=['Real Hive 4.2.1 outputs', 'Inside delta files', 'ROW__ID explained', 'Runs in your browser (Python)'],
)

MAIN = '''# An ACID table as a list of folders. Readers merge them; nothing is edited.
deltas = {   # write id -> rows (row id, customer, plan)
    1: [(0, 1, "Silver"), (1, 2, "Basic"), (2, 3, "Gold"), (3, 4, "Basic"), (4, 5, "Basic")],
    2: [(0, 2, "Gold")],                 # UPDATE: new version of customer 2
    4: [(0, 6, "Silver")],               # INSERT
}
delete_deltas = {(1, 1), (1, 4)}         # (write id, row id): old customer 2, customer 5

visible = []
for write, rows in sorted(deltas.items()):
    for rowid, cust, plan in rows:
        if (write, rowid) not in delete_deltas:
            visible.append((cust, plan, f"ROW__ID=({write},{rowid})"))
for v in sorted(visible):
    print(v)
'''
RUN = dict(
    heading='Run the code: how a reader merges deltas',
    intro='<p>This program mimics how Hive reads an ACID table: all delta folders, minus the rows listed in delete deltas. The numbers match our real table. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('delete_deltas = {(1, 1), (1, 4)}         # (write id, row id): old customer 2, customer 5', 'Exactly the two delete records we read with orcfiledump in Step 5.'),
        ('        if (write, rowid) not in delete_deltas:', 'A row survives unless its ROW__ID was deleted by a later write.'),
    ],
    tasks=[
        dict(label='1 · Merge on read', hint='Press <b>Run</b>. The result is the real table after Step 3: customer 2 is Gold, 5 is gone, 6 is new.', code=None),
        dict(label='2 · Predict first: one more UPDATE', hint='<b>Predict first:</b> after updating customer 3 to Pune, how many folders does the table have? (Each UPDATE adds a delta and a delete_delta.)',
             code='''folders = ["delta_1", "delta_2_0001", "delete_delta_2", "delete_delta_3", "delta_4"]
write = 5
folders += [f"delete_delta_{write}", f"delta_{write}_0001"]     # UPDATE customer 3
print(len(folders), folders)
'''),
        dict(label='3 · Snapshot isolation', hint='A query that started before write 4 committed does not see customer 6. Change <code>snapshot</code> to 4.',
             code='''deltas = {1: [1, 2, 3, 4, 5], 2: [2], 4: [6]}
snapshot = 3                     # highest committed write when the query started
seen = sorted({c for w, rows in deltas.items() if w <= snapshot for c in rows})
print("query sees customers:", seen)
'''),
        dict(label='4 · Cost of row-by-row updates', hint='Compare 102 single-row UPDATEs with one set-based UPDATE, as in the refunds example.',
             code='''rows_to_fix = 102
one_by_one = {"transactions": rows_to_fix, "folders": rows_to_fix * 2}
set_based = {"transactions": 1, "folders": 2}
print("one by one:", one_by_one)
print("set based :", set_based)
'''),
        dict(label='5 · Spot the error', hint='This code “updates” the partition column, which Hive refuses (Error 10292). Rewrite it as a delete from the old partition plus an insert into the new one.', expect='error',
             code='''partitions = {"2026-10-03": [100013, 100046], "2026-10-02": [100002]}
def update_partition_column(order_id, new_date):
    raise ValueError("Error 10292: Updating values of partition columns is not supported")
update_partition_column(100013, "2026-10-02")
print(partitions)
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: insert-only tables, locks and transactions',
    intro='<p>More statements to try in Beeline on the TiffinGo lab. <b>Outputs are real</b>, from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · An insert-only transactional table in TEXTFILE', cmd="CREATE TABLE events_mm (id INT, event STRING) STORED AS TEXTFILE\n  TBLPROPERTIES ('transactional'='true', 'transactional_properties'='insert_only');\nINSERT INTO events_mm VALUES (1, 'app_open'), (2, 'add_to_cart');\nINSERT INTO events_mm VALUES (3, 'checkout');\nSELECT * FROM events_mm ORDER BY id;\n$ find …/events_mm -type f", file='Beeline',
             output=capf('l71_mm.txt') + '\n\n./delta_0000001_0000001_0000/000000_0\n./delta_0000002_0000002_0000/000000_0',
             note='Insert-only tables get atomic, isolated inserts (each in its own delta folder) with any file format, but no UPDATE or DELETE (Error 10414). The files are plain text, not ACID ORC.'),
        dict(title='2 · Locks', cmd='SHOW LOCKS;', file='Beeline',
             output=capf('l71_locks.txt'),
             note='With no query running, the only locks are the metastore’s own background tasks (leader election for housekeeping). While a DELETE runs you would see a lock on the table or partition being changed.'),
        dict(title='3 · Open transactions', cmd='SHOW TRANSACTIONS;', file='Beeline',
             output=capf('l71_txn.txt'),
             note='Empty: every statement committed immediately. A long-running or crashed write would appear here as OPEN or ABORTED; aborted transactions also make the compactor work harder (7.3).'),
    ],
)

TRACE = dict(
    heading='What an UPDATE writes, one step at a time',
    intro='<p>UPDATE finds the matching rows, writes their ROW__IDs to a delete delta and writes new versions to a delta, all under one write id. Watch both lists.</p>',
    code='''rows = {(1, 0): ("1", "Silver"), (1, 1): ("2", "Basic"), (1, 2): ("3", "Gold")}
write_id = 2
delete_delta, delta = [], []
for rid, (cust, plan) in rows.items():
    if cust == "2":
        delete_delta.append(rid)
        delta.append(((write_id, len(delta)), (cust, "Gold")))
print(delete_delta, delta)
''',
    notes={2: 'Write id :: One id for the whole statement, so the delete and the insert commit together.', 6: 'Delete :: Only the ROW__ID is recorded, like the real record {"originalTransaction":1,"rowId":1}.', 7: 'Insert :: The new version gets a new ROW__ID (2, 0).'},
)

WORKED_INTRO = 'Three ACID tasks from TiffinGo’s data team.'
EXAMPLES = [
    dict(level='b', tag='Operations · corrections', title='Refund all cancelled orders of one day',
         problem='<p>Write the UPDATE and compute the new counts per status for 2 October, using the real counts before the change.</p>',
         inp='before (real): CANCELLED 102, DELIVERED 1,476, REFUNDED 39',
         approach=['Filter on the partition column and the status.', 'Move the CANCELLED count into REFUNDED.', 'Check the total is unchanged.'],
         code='''before = {"CANCELLED": 102, "DELIVERED": 1476, "REFUNDED": 39}
after = dict(before)
after["REFUNDED"] += after.pop("CANCELLED")
print(after, sum(before.values()) == sum(after.values()))
''', notes={3: 'UPDATE :: UPDATE orders_acid SET status = \'REFUNDED\' WHERE order_date = \'2026-10-02\' AND status = \'CANCELLED\'.'},
         tryit='The real query returned DELIVERED 1,476 and REFUNDED 141, and the day still has 1,617 orders.'),
    dict(level='i', tag='Engineering · moving rows', title='“Update” a partition column',
         problem='<p>Order 100013 was booked under the wrong date. Hive refuses to UPDATE the partition column (Error 10292). Plan the two statements that move it, and check the counts.</p>',
         inp='10-03: 1,628 orders, 10-02: 1,617 orders (real, after earlier changes)',
         approach=['INSERT the corrected row into the right partition.', 'DELETE it from the wrong one.', 'Counts: one moves from 10-03 to 10-02.'],
         code='''counts = {"2026-10-02": 1617, "2026-10-03": 1628}
statements = ["INSERT INTO orders_acid PARTITION (order_date='2026-10-02') SELECT order_id, customer_id, amount, status FROM orders_acid WHERE order_id = 100013",
              "DELETE FROM orders_acid WHERE order_date = '2026-10-03' AND order_id = 100013"]
counts["2026-10-02"] += 1
counts["2026-10-03"] -= 1
print(*statements, sep="\\n")
print(counts)
''', notes={5: 'Order :: Insert first, then delete, so the order never disappears; better still, use one MERGE (7.2) to keep it in a single transaction.'},
         tryit='Two statements are two transactions: a reader between them could see the order twice. MERGE can do the delete and the insert atomically.'),
    dict(level='a', tag='Capacity · delta growth', title='When will this table need compaction?',
         problem='<p>A support tool runs 40 small UPDATEs a day on a customer table. Each UPDATE adds 2 folders. The compactor’s default trigger for minor compaction is more than 10 deltas. How soon is it reached, and how many folders would a month create without compaction?</p>',
         inp='40 updates/day, 2 folders each, threshold 10 deltas',
         approach=['Folders per day = 40 × 2.', 'Days to exceed 10 deltas.', 'Folders in 30 days.'],
         code='''per_day = 40 * 2
threshold = 10
hours = threshold / per_day * 24
print(f"threshold reached after about {hours:.1f} hours")
print("folders in 30 days without compaction:", per_day * 30)
''', notes={3: 'Threshold :: hive.compactor.delta.num.threshold (default 10), checked every 5 minutes by the initiator.'},
         tryit='About 3 hours, and 2,400 folders a month without compaction. Batching the 40 changes into one nightly MERGE needs just 2 folders a day.'),
]

QUIZ = mix([
    dict(q='Beginner: Which table property makes a Hive table transactional?', options=["'acid'='on'", "'transactional'='true'", "'orc.acid'='true'", "'update'='enabled'"], answer=1,
         why="TBLPROPERTIES ('transactional'='true') on a managed ORC table."),
    dict(q='Beginner: What does an UPDATE on an ACID table write?', options=['It edits the ORC file in place', 'A delete_delta for the old row and a delta for the new row', 'A full copy of the table', 'Nothing until compaction'], answer=1,
         why='Real folders: delete_delta_0000002… and delta_0000002_0000002_0001.'),
    dict(q='Beginner: Can an EXTERNAL table be transactional?', options=['Yes', 'No: Hive refuses', 'Only with Parquet', 'Only if partitioned'], answer=1,
         why='“cannot be declared transactional because it’s an external table”.'),
    dict(q='Intermediate: What is ROW__ID?', options=['The primary key you define', 'A hidden struct (writeid, bucketid, rowid) identifying each row', 'The line number in a text file', 'A UUID column'], answer=1,
         why='Delete deltas refer to rows by ROW__ID.'),
    dict(q='Intermediate: What happens with START TRANSACTION in Hive 4.2.1?', options=['Opens a multi-statement transaction', 'Error: not supported yet', 'It is ignored', 'Locks the database'], answer=1,
         why='Each statement auto-commits.'),
    dict(q='Intermediate: Which UPDATE did Hive refuse with Error 10292?', options=['UPDATE on a status column', 'UPDATE of a partition column', 'UPDATE with a WHERE subquery', 'UPDATE on an ORC table'], answer=1,
         why='Move rows between partitions with DELETE + INSERT or MERGE.'),
    dict(q='Advanced: What do insert-only transactional tables allow?', options=['UPDATE only', 'INSERT only, in any file format', 'DELETE only', 'Everything'], answer=1,
         why='UPDATE gave Error 10414 on our TEXTFILE insert-only table.'),
    dict(q='Advanced: Did our Hive 4.2.1 ACID table need buckets?', options=['Yes, CLUSTERED BY is required', 'No: Num Buckets was −1', 'Only for DELETE', 'Only with partitions'], answer=1,
         why='The bucketing requirement belonged to Hive 1.x/2.x.'),
])

REVISION = [
    "<b>Create:</b> managed ORC table + <code>TBLPROPERTIES ('transactional'='true')</code>; needs <code>hive.support.concurrency=true</code> + <code>DbTxnManager</code>. No buckets needed in Hive 3+.",
    '<b>Layout:</b> <code>delta_x_y_s</code> (new rows), <code>delete_delta_x_y_s</code> (dead ROW__IDs), <code>base_N</code> after major compaction.',
    '<b>UPDATE</b> = delete_delta + delta with the same write id; <b>DELETE</b> = delete_delta only; nothing is edited in place.',
    '<b>ROW__ID</b> = {writeid, bucketid, rowid}; readers drop deleted ids and merge the rest.',
    'Every statement auto-commits; <code>START TRANSACTION</code> is not supported.',
    '<b>Refused:</b> non-ACID table (10297), partition column update (10292), insert-only UPDATE (10414), external transactional table.',
    'DML prunes partitions; subqueries allowed in WHERE (<code>DELETE … WHERE id IN (SELECT …)</code>).',
    '<b>Insert-only</b> tables: any format, atomic INSERT, no UPDATE/DELETE.',
    'Batch changes: many tiny updates → many deltas → compaction load.',
]
FAQ = [
    ('Is Hive ACID suitable for an OLTP application?', 'No. Each statement is a distributed job with metastore transactions and new files, taking seconds, not milliseconds. ACID in Hive is for batch corrections, upserts and deletions on large analytic tables. Keep OLTP in MySQL or PostgreSQL and bring changes into Hive in batches.'),
    ('Can I convert an existing table to ACID?', 'A managed ORC table can be converted with <code>ALTER TABLE t SET TBLPROPERTIES (\'transactional\'=\'true\')</code>; existing files are treated as original files. An external table must first be converted to managed or copied into a new transactional table with INSERT … SELECT. Converting back from ACID to non-ACID is not supported.'),
    ('Can Spark read Hive ACID tables?', 'Not with plain Spark SQL; it does not understand delta and delete_delta folders and may return wrong results. Vendor connectors (for example the Hive Warehouse Connector) read through Hive. If several engines must read and write the same changing table, Iceberg (Lesson 7.3) is usually the better choice.'),
    ('What happens if an UPDATE fails half-way?', 'The transaction is aborted. Its delta folders may remain on disk, but readers ignore them because the write id is not committed, and the compactor’s cleaner removes them later. Readers never see half an update.'),
    ('Why does a SELECT on an ACID table get slower over time?', 'Each reader must open the base and every delta and delete_delta and merge them. After hundreds of small changes that becomes expensive. Compaction (Lesson 7.3) merges deltas back into fewer files; it runs automatically when thresholds are crossed.'),
]

PRACTICE_INTRO = 'Programs that simulate ACID folders and statements, with the HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Name the folder', stmt='Build the delta folder name for write 7, statement 0.', inp='write 7, statement 0',
         code='''w, s = 7, 0
print(f"delta_{w:07d}_{w:07d}_{s:04d}")
''', explain='delta_0000007_0000007_0000, the same pattern as the real folders.'),
    dict(level='easy', title='Visible rows', stmt='Rows 0–4 were written by write 1; rows 1 and 4 were deleted. Which remain?', inp='5 rows, deletes {1, 4}',
         code='''print([r for r in range(5) if r not in {1, 4}])
''', explain='Rows 0, 2, 3: customers 1, 3 and 4 in the real table.'),
    dict(level='easy', title='Which statements are allowed?', stmt='Mark each statement on an insert-only table as allowed or refused.', inp='INSERT, UPDATE, DELETE, SELECT',
         code='''allowed = {"INSERT": True, "UPDATE": False, "DELETE": False, "SELECT": True}
for s, ok in allowed.items():
    print(s, "allowed" if ok else "refused (Error 10414)")
''', explain='Insert-only tables accept INSERT and reads only.'),
    dict(level='medium', title='Count after a DELETE', stmt='3 October had 1,668 orders; 40 cost under ₹50. How many remain after the DELETE?', inp='1,668 and 40',
         code='''print(1668 - 40)
''', explain='1,628, matching the real result.'),
    dict(level='medium', title='Snapshot for a running report', stmt='A report started when the last committed write was 3. Which writes does it see?', inp='writes 1, 2, 3, 4 (4 committed later)',
         code='''committed_at_start = 3
print([w for w in [1, 2, 3, 4] if w <= committed_at_start])
''', explain='Writes 1–3. Write 4 committed after the report started, so snapshot isolation hides it.'),
    dict(level='medium', title='Folders per partition', stmt='An UPDATE touches 2 of 30 date partitions. How many new folders appear?', inp='2 partitions × (delta + delete_delta)',
         code='''print(2 * 2, "new folders; 28 partitions untouched")
''', explain='Changes are written only into the partitions that contain matching rows.'),
    dict(level='business', title='Erasure request batch', stmt='Turn a day of erasure requests into one DELETE statement.', inp='customer ids 1492, 77, 1003',
         code='''ids = [1492, 77, 1003]
print("DELETE FROM orders_acid WHERE customer_id IN (" + ", ".join(map(str, ids)) + ");")
''', explain='One transaction instead of three. Follow with a major compaction to remove the rows physically.'),
    dict(level='business', title='Daily delta budget', stmt='How many folders a day do 25 separate UPDATE jobs and 1 nightly MERGE create?', inp='UPDATE: 2 folders; MERGE with updates, deletes and inserts: up to 4',
         code='''print("25 updates:", 25 * 2, "folders")
print("1 merge   :", 4, "folders at most")
''', explain='Batching into one MERGE keeps the table fast and the compactor idle (Lesson 7.2 shows the real MERGE folders).'),
]

SCN_INTRO = 'ACID questions check whether you know how updates work on immutable storage and when not to use them.'
SCENARIOS = (
    scn('Any company · Hive', 'Fresher', '“Does Hive support UPDATE and DELETE?”',
        'Answer and explain the conditions.',
        'do you know the requirements and the mechanism?',
        '<p>Yes, on transactional (ACID) tables: managed ORC tables with <code>transactional=true</code> and the DbTxnManager enabled. Changes are written as delta and delete_delta directories; readers merge them; compaction cleans up. Each statement auto-commits. External and plain tables do not support UPDATE/DELETE.</p>', '“No, Hive is append-only” (true only before Hive 0.14).') +
    scn('Data engineering', 'Mid-level', 'UPDATE fails with Error 10297',
        'A colleague’s UPDATE on the sales table fails: “not transactional”.',
        'can you fix it the right way?',
        '''<ol>
          <li>Check DESCRIBE FORMATTED: external or managed, format, transactional property.</li>
          <li>If it is external (common in Hive 4), create a managed ORC transactional copy with INSERT … SELECT and switch readers.</li>
          <li>Or, if updates are rare, fix data by rewriting the affected partitions with INSERT OVERWRITE.</li>
        </ol>''', 'Setting transactional=true on an external table, which Hive rejects.') +
    scn('Platform', 'Mid-level', 'Queries on an ACID table getting slower',
        'A customer table updated by a support tool all day becomes slower to query each week.',
        'do you connect deltas to read cost?',
        '''<ul>
          <li>List the folders: hundreds of delta and delete_delta directories.</li>
          <li>Check SHOW COMPACTIONS and that the initiator and workers are running (7.3).</li>
          <li>Batch the tool’s changes into periodic MERGE statements.</li>
        </ul>''', '“Add memory to HiveServer2.”') +
    scn('Architecture', 'Senior', 'ACID or Iceberg?',
        'A new customer 360 table will be updated nightly by Hive and read by Spark and Trino.',
        'do you know engine support trade-offs?',
        '''<ul>
          <li>Hive ACID works well inside Hive but other engines need special connectors.</li>
          <li>Iceberg supports UPDATE/DELETE/MERGE from Hive 4 and is read and written natively by Spark and Trino, with snapshots and time travel.</li>
          <li>Choose Iceberg for multi-engine tables; Hive ACID if Hive is the only engine and the platform already runs it.</li>
        </ul>''', 'Choosing by habit without checking which engines must write.')
)
