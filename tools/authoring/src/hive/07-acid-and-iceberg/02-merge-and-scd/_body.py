import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()

def rowb(x, y, txt, tone='card', w=150, strike=False):
    o = box(x, y, w, 18, tone) + t(x + 6, y + 13, txt, 6.8, 'ink', anchor='start', mono=True)
    if strike:
        o += f'<line x1="{x + 4}" y1="{y + 9}" x2="{x + w - 4}" y2="{y + 9}" stroke="#D64545" stroke-width="1.6"/>'
    return o

# ---------------------------------------------------------------- story
sc = (box(10, 12, 190, 128, 'card') + t(105, 30, 'Tonight’s changes (staging)', 8.4, bold=True) +
      ''.join(t(20, 52 + k * 16, s, 7.2, 'ink2', anchor='start', mono=True) for k, s in enumerate(['2 Ananya  plan → Gold', '3 Arjun   city → Pune', '4 Gurpreet (no change)', '6 Diya    closed (D)', '7 Kavya   new'])) +
      arrow(206, 76, 246, 76, 'acc', 2.2) + box(252, 50, 96, 52, 'acc') + t(300, 72, 'one MERGE', 8.6, bold=True) + t(300, 88, 'statement', 8, 'ink2') +
      arrow(354, 76, 394, 76, 'acc', 2.2) + box(400, 12, 230, 128, 'green') + t(515, 30, 'dim_customer, atomically', 8.4, 'green', bold=True) +
      ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([('2 → UPDATE', 'ink'), ('3 → UPDATE', 'ink'), ('4 → untouched', 'ink2'), ('6 → DELETE', 'red'), ('7 → INSERT', 'green')])))
scene_svg = scene('Five staged changes go into one MERGE statement: two customers are updated, one unchanged customer is left alone, one closed account is deleted and one new customer is inserted, all in one transaction.', sc,
                  'MERGE applies <tspan font-weight="700" class="s-acc">inserts, updates and deletes</tspan> from one source in a single transaction.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Every night the app database sends changed customers. Apply them.”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s app runs on PostgreSQL. Every night a job exports the customers that changed: plan upgrades, address moves, closed accounts and new sign-ups. Kabir must apply them to the Hive customer table. Writing a separate UPDATE, DELETE and INSERT would mean three transactions and three chances to fail half-way.</p>

{scene_svg}

K> Sir, can one statement insert new customers and update existing ones?
A> That is <b>MERGE</b>: compare a source with a target on a key, then <code>WHEN MATCHED … UPDATE</code> or <code>DELETE</code>, and <code>WHEN NOT MATCHED … INSERT</code>. One statement, one transaction. People call it an <b>upsert</b>.
R> And the finance team wants history: what plan was the customer on when they ordered?
A> Then you keep old versions with dates: a <b>slowly changing dimension type 2</b>. MERGE can do that too, with a small trick. Today: a type 1 MERGE, the error you get with duplicate keys, a type 2 MERGE that keeps history, a re-run to prove it is safe, and a point-in-time join. All outputs are real, from Hive 4.2.1.
  </div>
</section>
'''

lv = '''
LEVELS> MERGE and SCD at three levels
L1> Updating an address book
      <ul>
        <li>You get a list of changes. For each person: if they are already in your book, change their entry; if not, add them; if they asked to be removed, cross them out.</li>
        <li>MERGE does exactly this for a whole table in one go.</li>
        <li>Sometimes you must not lose the old entry (“where did she live last year?”). Then you close the old entry with an end date and add a new one: that is SCD type 2.</li>
      </ul>
L2> The MERGE statement
      <ul>
        <li><code>MERGE INTO target t USING source s ON t.key = s.key</code>, then up to three clauses: <code>WHEN MATCHED [AND cond] THEN UPDATE SET …</code>, <code>WHEN MATCHED [AND cond] THEN DELETE</code>, <code>WHEN NOT MATCHED [AND cond] THEN INSERT VALUES (…)</code>.</li>
        <li>The target must be a <b>full ACID</b> table (7.1); the source can be any table, view or subquery.</li>
        <li><b>SCD type 1:</b> overwrite the old value (no history). <b>Type 2:</b> keep every version with <code>eff_from</code>, <code>eff_to</code>, <code>is_current</code>. <b>Type 3:</b> keep the previous value in an extra column.</li>
        <li>Add a change condition (<code>t.plan &lt;&gt; s.plan OR …</code>) so unchanged rows are not rewritten.</li>
      </ul>
L3> Hive specifics we verified
      <ul>
        <li><b>Cardinality check:</b> if two source rows match one target row, Hive fails the MERGE (“Cardinality Violation in Merge statement”, <code>hive.merge.cardinality.check=true</code>). The target stayed unchanged. De-duplicate the source first.</li>
        <li>One MERGE wrote two delete_deltas and two deltas under <b>one write id</b>: atomic. Untouched rows kept their old ROW__ID.</li>
        <li><b>SCD2 in one MERGE:</b> a changed row must both <i>close</i> the old version (MATCHED) and <i>insert</i> a new one (NOT MATCHED). The trick: feed changed rows twice, once with the real key and once with a NULL join key, which can never match.</li>
        <li>Re-running the same SCD2 MERGE changed nothing (9 rows, 7 current): it is idempotent, so a failed night can simply be re-run.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>MERGE and slowly changing dimensions</h2>
''' + def_block(
    '<b>MERGE</b> is a DML statement that synchronises a <b>target</b> transactional table with a <b>source</b> relation using a join condition. For each source row that matches a target row, the first applicable <code>WHEN MATCHED</code> clause updates or deletes the target row; for each source row without a match, a <code>WHEN NOT MATCHED</code> clause inserts a new row. The whole statement executes as one transaction. A <b>slowly changing dimension (SCD)</b> is a dimension table whose attributes change over time: <b>type 1</b> overwrites old values, <b>type 2</b> keeps full history by adding a new row per change with validity dates and a current flag, and <b>type 3</b> keeps a limited history in additional columns.',
    'MERGE compares new data with a table by key and, in one statement, updates the rows that changed, deletes the ones marked for removal and inserts the new ones. SCD is the name for the ways of keeping (or not keeping) old values of things like a customer’s city or plan.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Target / source', 'The ACID table being changed / the new data.'),
    ('Upsert', 'Update if the key exists, insert if not.'),
    ('WHEN MATCHED', 'Clause for source rows whose key exists in the target.'),
    ('WHEN NOT MATCHED', 'Clause for source rows with no matching target row.'),
    ('Cardinality violation', 'Two source rows match the same target row; Hive refuses.'),
    ('SCD type 1', 'Overwrite: only the current value exists.'),
    ('SCD type 2', 'History: <code>eff_from</code>, <code>eff_to</code>, <code>is_current</code> per version.'),
    ('Idempotent', 'Running a job twice gives the same result as running it once.'),
]) + '''

  <h3>SCD types compared</h3>
''' + table(['Type', 'What happens when Ananya upgrades to Gold', 'Rows for her', 'Answers “plan at order time”?'], [
    ['0', 'Nothing: values never change', '1 (Basic)', 'No'],
    ['1', 'plan overwritten to Gold', '1 (Gold)', 'No'],
    ['2', 'old row closed (eff_to = 2026-10-26), new row Gold from 2026-10-27', '2', '<b>Yes</b>'],
    ['3', 'plan = Gold, prev_plan = Basic', '1', 'Only one step back'],
], minw=680) + lv + '''
EXAM> “What is SCD type 2 and how do you implement it in Hive?” Explain the validity columns, then the MERGE: match current rows on the key and close them when attributes differ; insert new versions using a NULL join key for changed rows plus the real key for new rows. Mention that the target must be an ACID table and that duplicate source keys cause a cardinality violation.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>MERGE patterns</h2>
''' + table(['Pattern', 'Clauses', 'Use'], [
    ['Upsert (SCD1)', 'MATCHED AND changed → UPDATE · NOT MATCHED → INSERT', 'Current state of customers, products'],
    ['Upsert with deletes', '+ MATCHED AND s.op = \'D\' → DELETE', 'CDC feeds with I/U/D operations'],
    ['Insert only new keys', 'NOT MATCHED → INSERT', 'De-duplicated loads of events'],
    ['SCD2', 'MATCHED AND changed → UPDATE (close) · NOT MATCHED → INSERT (new version)', 'History for reporting and audits'],
    ['Soft delete', 'MATCHED AND s.op = \'D\' → UPDATE SET is_deleted = true', 'Keep closed accounts for audits'],
], minw=680) + '''
''' + table(['Rule', 'Why'], [
    ['Target must be full ACID (ORC, transactional=true)', 'MERGE writes deltas and delete deltas'],
    ['Each target row may match at most one source row', 'Otherwise: Cardinality Violation, nothing applied'],
    ['Put the more specific MATCHED clause first', 'The first applicable clause wins (DELETE before UPDATE)'],
    ['Add “AND changed” to UPDATE', 'Unchanged rows are not rewritten, fewer files'],
    ['Filter the target in ON (e.g. partitions, is_current)', 'Less data scanned and joined'],
], minw=620) + '''
WARN> Comparisons with <code>&lt;&gt;</code> ignore NULLs: if the old city is NULL and the new one is Pune, <code>t.city &lt;&gt; s.city</code> is NULL, not true, and the change is missed. In real jobs compare with <code>NOT (t.city &lt;=&gt; s.city)</code> (null-safe equality) or compare a hash of all columns.
</section>
'''

scd1 = tables(capf('l72_setup.txt'))
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Type 1, a failure, then type 2</h2>
  <p>All outputs are real, from the Hive 4.2.1 lab (database <code>tiffingo</code>).</p>
''' + stepper([
    ('Step 1 · Target and staging tables',
     code('sql', 'Beeline', "CREATE TABLE dim_customer (customer_id INT, name STRING, city STRING, plan STRING)\nSTORED AS ORC TBLPROPERTIES ('transactional'='true');\nINSERT INTO dim_customer SELECT customer_id, name, city, plan FROM customers WHERE customer_id <= 6;\n\nCREATE TABLE stg_customer (customer_id INT, name STRING, city STRING, plan STRING, op STRING);\nINSERT INTO stg_customer VALUES (2,'Ananya Iyer','Mumbai','Gold','U'), (3,'Arjun Nair','Pune','Gold','U'),\n  (4,'Gurpreet Das','Bengaluru','Basic','U'), (6,NULL,NULL,NULL,'D'), (7,'Kavya Reddy','Hyderabad','Silver','I');",
          scd1[0] + '\n' + scd1[1]),
     'The target is an ACID table; the staging table is an ordinary table. <code>op</code> says what happened in the source system: U(pdate), D(elete), I(nsert). Customer 4 is in the feed although nothing changed, which is common in real exports.'),
    ('Step 2 · One MERGE: update, delete and insert',
     code('sql', 'Beeline', "MERGE INTO dim_customer t USING stg_customer s ON t.customer_id = s.customer_id\nWHEN MATCHED AND s.op = 'D' THEN DELETE\nWHEN MATCHED AND (t.city <> s.city OR t.plan <> s.plan)\n  THEN UPDATE SET city = s.city, plan = s.plan\nWHEN NOT MATCHED THEN INSERT VALUES (s.customer_id, s.name, s.city, s.plan);\nSELECT * FROM dim_customer ORDER BY customer_id;", capf('l72_scd1.txt')),
     'Ananya is Gold, Arjun moved to Pune, Diya (6) is deleted and Kavya (7) is new. The DELETE clause is listed first so that a “D” row is never treated as an update. This is SCD type 1: the old values are gone.'),
    ('Step 3 · What one MERGE wrote',
     code('bash', 'Beeline / Terminal', "$ ls …/dim_customer\nSELECT ROW__ID.writeid AS writeid, customer_id, plan FROM dim_customer ORDER BY customer_id;", capf('l72_dirs.txt').split('\n', 1)[1] + '\n\n' + capf('l72_rowid.txt')),
     'All changes share write id 2, in four folders (one per clause type and statement part). Customer 4 kept write id 1: the “AND changed” condition stopped Hive from rewriting an unchanged row.'),
    ('Step 4 · Duplicate keys in the source: cardinality violation',
     code('sql', 'Beeline', "INSERT INTO stg_customer VALUES (2, 'Ananya Iyer', 'Mumbai', 'Silver', 'U');   -- a second row for customer 2\n-- run the same MERGE again\nSELECT customer_id, plan FROM dim_customer WHERE customer_id = 2;", capf('l72_card.txt') + '\n\n' + capf('l72_after_fail.txt')),
     'Two source rows (Gold and Silver) matched customer 2, so Hive could not know which one wins and failed the whole statement. The table was not changed at all. Fix: keep one row per key in the source, e.g. the latest with ROW_NUMBER() (Lesson 3.6).'),
    ('Step 5 · A type 2 table and the changes',
     code('sql', 'Beeline', "CREATE TABLE dim_customer_hist (customer_id INT, name STRING, city STRING, plan STRING,\n  eff_from DATE, eff_to DATE, is_current BOOLEAN)\nSTORED AS ORC TBLPROPERTIES ('transactional'='true');\nINSERT INTO dim_customer_hist SELECT customer_id, name, city, plan,\n  DATE '2026-10-01', DATE '9999-12-31', true FROM customers WHERE customer_id <= 6;\n\nCREATE TABLE stg2 (customer_id INT, name STRING, city STRING, plan STRING);\nINSERT INTO stg2 VALUES (2,'Ananya Iyer','Mumbai','Gold'), (3,'Arjun Nair','Pune','Gold'),\n  (4,'Gurpreet Das','Bengaluru','Basic'), (7,'Kavya Reddy','Hyderabad','Silver');",
          '-- 6 rows, all current, valid from 2026-10-01 to 9999-12-31'),
     'Every version has a validity range. “9999-12-31” is a common convention for “still valid”, so a simple BETWEEN works in joins. The staging table holds the same changes as before, without the delete.'),
    ('Step 6 · The SCD2 MERGE with a NULL join key',
     code('sql', 'Beeline', "MERGE INTO dim_customer_hist t\nUSING (\n  SELECT s.customer_id AS join_key, s.customer_id, s.name, s.city, s.plan FROM stg2 s\n  UNION ALL\n  SELECT CAST(NULL AS INT) AS join_key, s.customer_id, s.name, s.city, s.plan\n  FROM stg2 s JOIN dim_customer_hist d ON s.customer_id = d.customer_id AND d.is_current\n  WHERE s.city <> d.city OR s.plan <> d.plan\n) u\nON t.customer_id = u.join_key AND t.is_current\nWHEN MATCHED AND (t.city <> u.city OR t.plan <> u.plan)\n  THEN UPDATE SET eff_to = DATE '2026-10-26', is_current = false\nWHEN NOT MATCHED THEN INSERT VALUES (u.customer_id, u.name, u.city, u.plan,\n  DATE '2026-10-27', DATE '9999-12-31', true);\nSELECT * FROM dim_customer_hist ORDER BY customer_id, eff_from;", capf('l72_scd2.txt')),
     'Changed customers 2 and 3 appear twice in the source. With their real key they <b>match</b> the current row, which is closed (eff_to 10-26, is_current false). With a NULL key they can never match, so they are <b>inserted</b> as new current versions. Customer 4 matched but nothing changed; customer 7 had no match and was inserted. Old values are kept.'),
    ('Step 7 · Re-run it: nothing changes',
     code('sql', 'Beeline', "-- run exactly the same MERGE again\nSELECT COUNT(*) AS rows_after_rerun, SUM(IF(is_current, 1, 0)) AS current_rows\nFROM dim_customer_hist;", capf('l72_rerun.txt').split('\n', 0)[0]),
     'Still 9 rows with 7 current. The current rows now equal the staging values, so the change condition is false everywhere and the NULL-key branch selects nothing. An idempotent job can be safely re-run after a failure, which matters for nightly pipelines.'),
    ('Step 8 · Why type 2: the plan at order time',
     code('sql', 'Beeline', "-- point in time: the version valid on the order date\nSELECT h.plan AS plan_then, COUNT(*) AS orders FROM orders o\nJOIN dim_customer_hist h ON o.customer_id = h.customer_id\n AND o.order_date BETWEEN h.eff_from AND h.eff_to\nWHERE o.customer_id = 2 GROUP BY h.plan;\n\n-- current version only\nSELECT h.plan AS plan_now, COUNT(*) AS orders FROM orders o\nJOIN dim_customer_hist h ON o.customer_id = h.customer_id AND h.is_current\nWHERE o.customer_id = 2 GROUP BY h.plan;", capf('l72_asof.txt')),
     'Ananya placed 14 orders as a Basic customer and 5 after upgrading. A report joined on the current row only would say all 19 orders were Gold, overstating Gold revenue. This is why finance and analytics teams ask for SCD2.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('> MERGE INTO dim_customer t USING stg_customer s', W), ('    ON t.customer_id = s.customer_id', W), ("  WHEN MATCHED AND s.op = 'D' THEN DELETE", W), ('  WHEN MATCHED AND (changed) THEN UPDATE …', W), ('  WHEN NOT MATCHED THEN INSERT …;', W)], size=7.6),
    term([('| 2 | Ananya Iyer  | Mumbai    | Gold   |', G), ('| 3 | Arjun Nair   | Pune      | Gold   |', G), ('| 4 | Gurpreet Das | Bengaluru | Basic  |', W), ('| 7 | Kavya Reddy  | Hyderabad | Silver |', G), ('  (6 deleted)', Y)], size=7.6),
    term([('> … same MERGE, two source rows for customer 2', W), ('Cardinality Violation in Merge statement', RD), ('> SELECT plan FROM dim_customer', W), ('    WHERE customer_id = 2;   | Gold |', G)], size=7.6),
    term([('| 2 | Basic | 2026-10-01 | 2026-10-26 | false |', Y), ('| 2 | Gold  | 2026-10-27 | 9999-12-31 | true  |', G), ('| 3 | Mumbai… | 2026-10-01 | 2026-10-26 | false |', Y), ('| 3 | Pune …  | 2026-10-27 | 9999-12-31 | true  |', G), ('| 7 | Silver | 2026-10-27 | 9999-12-31 | true |', G)], size=7.2),
    term([('| plan_then | orders |', W), ('| Basic     | 14     |', G), ('| Gold      | 5      |', G), ('| plan_now  | orders |', W), ('| Gold      | 19     |', Y)]),
]
B1 = [
    t(180, 22, 'Join source and target on the key', 9.4, bold=True) + ''.join(rowb(20, 40 + k * 20, s, 'card', 140) for k, s in enumerate(['s 2  Gold', 's 3  Pune', 's 4  same', 's 6  D', 's 7  new'])) +
    ''.join(rowb(200, 40 + k * 20, s, tone, 140) for k, (s, tone) in enumerate([('t 2  Basic', 'card'), ('t 3  Mumbai', 'card'), ('t 4  Basic', 'card'), ('t 6  Pune', 'card'), ('(no row)', 'acc')])) +
    cap('Matched rows go to WHEN MATCHED; unmatched to NOT MATCHED.', '', 'blue', y=150, h=34),
    t(180, 22, 'First applicable clause wins', 9.4, bold=True) + ''.join(rowb(20, 40 + k * 20, s, tone, 320, strike=st) for k, (s, tone, st) in enumerate([('2  MATCHED, changed     → UPDATE', 'green', False), ('3  MATCHED, changed     → UPDATE', 'green', False), ('4  MATCHED, unchanged   → nothing', 'card', False), ('6  MATCHED, op = D      → DELETE', 'red', False), ('7  NOT MATCHED          → INSERT', 'green', False)])) +
    cap('All in one transaction (write id 2).', '', 'green', y=150, h=34),
    t(180, 22, 'Two source rows → one target row', 9.4, bold=True) + rowb(20, 50, 's 2  Gold', 'card', 120) + rowb(20, 74, 's 2  Silver', 'card', 120) + arrow(144, 60, 196, 70, 'red') + arrow(144, 84, 196, 74, 'red') + rowb(200, 62, 't 2', 'red', 120) +
    cap('Which value wins? Hive refuses and changes nothing.', 'De-duplicate the source first.', 'amber', y=150, h=46),
    t(180, 22, 'SCD2: changed rows enter twice', 9.4, bold=True) + rowb(20, 40, 'key=2  Gold', 'card', 120) + t(150, 52, '→ matches current → close it', 7, 'ink2', anchor='start') +
    rowb(20, 64, 'key=NULL  Gold', 'acc', 120) + t(150, 76, '→ never matches → insert new', 7, 'ink2', anchor='start') + rowb(20, 92, 'key=7  Silver', 'card', 120) + t(150, 104, '→ no match → insert', 7, 'ink2', anchor='start') +
    cap('NULL = NULL is never true in a join.', '', 'blue', y=150, h=34),
    t(180, 22, 'Join on the validity range', 9.4, bold=True) + fill(30, 60, 240, 22, 'blue') + t(150, 75, 'Basic: 10-01 … 10-26', 7.6, 'ink', mono=True, extra=' style="fill:#fff"') + fill(270, 60, 60, 22, 'green') + t(300, 75, 'Gold', 7.6, 'ink', extra=' style="fill:#fff"') +
    ''.join(f'<circle cx="{40 + k * 15}" cy="98" r="3" class="s-ink2"/>' for k in range(14)) + ''.join(f'<circle cx="{276 + k * 12}" cy="98" r="3" class="s-ink2"/>' for k in range(5)) + cap('14 orders as Basic, 5 as Gold.', '', 'green', y=150, h=34),
]
see_caps = ['A single MERGE with DELETE, UPDATE and INSERT clauses.',
            'The result: two updates, one insert, one delete, one row untouched.',
            'Duplicate keys in the source make the MERGE fail; nothing changes.',
            'SCD2 keeps the old versions with closed date ranges.',
            'A point-in-time join splits Ananya’s orders by the plan she had then.']
behind_caps = ['Hive joins source and target on the key, then routes each row to a clause.',
               'The first clause whose condition is true decides the action; all actions commit together.',
               'A target row may be changed by only one source row.',
               'A NULL join key forces the second copy of a changed row into the INSERT branch.',
               'Each order is matched to the version whose eff_from–eff_to range contains its date.']
two = anim_two('MERGE', 'Upserts, cardinality and SCD2', 'Real Beeline output', 'How MERGE routes each row', see, B1, see_caps, behind_caps)

# ---- scenario 1: CDC
d1 = (t(180, 22, 'CDC feed from PostgreSQL', 9.4, bold=True) + t(180, 56, 'every change event: op (I/U/D), key, values, ts', 8, 'ink2') + cap('A customer can change 3 times in a day.', '', 'blue', y=150, h=34))
d2 = (t(180, 22, 'Keep the latest event per key', 9.4, bold=True) + t(180, 54, 'ROW_NUMBER() OVER (PARTITION BY customer_id', 7.8, 'ink', mono=True) + t(180, 70, '                   ORDER BY ts DESC) = 1', 7.8, 'ink', mono=True) + cap('Prevents the cardinality violation.', '', 'green', y=150, h=34))
d3 = (t(180, 22, 'MERGE with three clauses', 9.4, bold=True) + t(180, 56, "D → DELETE · U → UPDATE · I → INSERT", 8.4, 'ink', mono=True) + cap('One transaction per night.', '', 'green', y=150, h=34))
d4 = (t(180, 22, 'Check the counts', 9.4, bold=True) + t(180, 56, 'target rows = before + inserts − deletes', 8.4, 'ink2', mono=True) + cap('Real lab: 6 + 1 − 1 = 6 rows.', '', 'blue', y=150, h=34))
d5 = (t(180, 22, 'Watch for late events', 9.4, 'acc', bold=True) + t(180, 56, 'apply only events newer than the target’s ts', 8.2, 'ink2') + cap('Add AND s.ts > t.ts to the UPDATE clause.', '', 'amber', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Applying a CDC feed every night',
              'Change data capture from an OLTP database into a Hive ACID table. (Typical pipeline; the MERGE pattern ran in our lab.)',
              'CDC upsert', 'Change events are de-duplicated to the latest per key and applied with a three-clause MERGE in one transaction', [d1, d2, d3, d4, d5],
              ['The database emits insert, update and delete events.',
               'Keep only the latest event per key.',
               'One MERGE applies deletes, updates and inserts.',
               'Reconcile row counts after the merge.',
               'Ignore events older than what the target already has.'],
              hid='scenario-cdc')

# ---- scenario 2: revenue by plan
r1 = (t(180, 22, 'Finance: “revenue by plan, last quarter”', 9.4, bold=True) + t(180, 56, 'customers upgrade and downgrade all the time', 8.2, 'ink2') + cap('Which plan counts: today’s or the one at order time?', '', 'blue', y=150, h=46))
r2 = term([('| plan_now | orders |', W), ('| Gold     | 19     |', Y), ('  current-row join: all orders “Gold”', RD)], label='real output · Hive 4.2.1')
r3 = term([('| plan_then | orders |', W), ('| Basic     | 14     |', G), ('| Gold      | 5      |', G)], label='real output · Hive 4.2.1')
r4 = (t(180, 22, 'Point-in-time join', 9.4, bold=True) + t(180, 56, 'o.order_date BETWEEN h.eff_from AND h.eff_to', 8.4, 'ink', mono=True) + cap('Each order meets exactly one version.', '', 'green', y=150, h=34))
r5 = (t(180, 22, 'Guard rail', 9.4, 'acc', bold=True) + t(180, 56, 'versions must not overlap: test it nightly', 8.4, 'ink2') + cap('Overlaps double-count revenue.', '', 'amber', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Revenue by the plan customers really had',
              'Why SCD2 matters for reporting. Both results are real.',
              'Point-in-time reporting', 'Joining orders to current customer rows misattributes revenue; joining on the validity range gives the plan at order time', [r1, r2, r3, r4, r5],
              ['Finance needs revenue by plan.',
               'Joining on current rows labels every order with today’s plan.',
               'Joining on the validity range uses the plan at order time.',
               'The BETWEEN join picks exactly one version per order.',
               'Test that versions never overlap.'],
              hid='scenario-pit')

# ---- scenario 3: performance
p1 = (t(180, 22, 'MERGE on a 2-billion-row target is slow', 9.4, bold=True) + t(180, 56, 'the join reads the whole target every night', 8.2, 'red') + cap('Only a few lakh rows actually change.', '(illustrative sizes)', 'amber', y=150, h=46))
p2 = (t(180, 22, 'Prune the target', 9.4, bold=True) + t(180, 56, "ON t.id = s.id AND t.order_date >= '2026-10-01'", 8, 'ink', mono=True) + cap('Partition filters in ON limit what is joined.', '', 'green', y=150, h=34))
p3 = (t(180, 22, 'Shrink the source', 9.4, bold=True) + t(180, 56, 'only changed rows; compare a hash of columns', 8.2, 'ink2') + cap('Fewer matches, fewer deltas.', '', 'green', y=150, h=34))
p4 = (t(180, 22, 'Keep the target compact', 9.4, bold=True) + t(180, 56, 'compaction after big merges (Lesson 7.3)', 8.2, 'ink2') + cap('Each merge adds delta folders.', '', 'blue', y=150, h=34))
p5 = (t(180, 22, 'Measure', 9.4, 'acc', bold=True) + t(180, 56, 'rows read, rows written, deltas created', 8.2, 'ink2') + cap('Tune the slowest part first.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Making a big MERGE fast',
              'Typical techniques used on very large targets. (Guidance; sizes are illustrative.)',
              'MERGE performance', 'Prune target partitions in the ON clause, send only changed rows, and compact after large merges', [p1, p2, p3, p4, p5],
              ['A nightly merge reads far more than it changes.',
               'Add partition filters to the ON clause.',
               'Send only real changes in the source.',
               'Compact the target after big merges.',
               'Measure each part before tuning.'],
              hid='scenario-perf')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>How MERGE decides what to do with each row</h2>
  <p>Left: real Beeline output. Right: how MERGE routes each row.</p>
''' + two + '''
  <p>Three live scenarios follow: a CDC feed, revenue by historical plan, and big-merge performance.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>MERGE and SCD at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'CDC', 12, 'green', bold=True, mono=True) + t(60, 58, 'nightly upsert', 7.4, 'ink2'),
    '1. Syncing OLTP databases',
    'Change data from MySQL, PostgreSQL or Oracle is merged into the warehouse every night or hour, keeping Hive tables close to the source.',
    ['Change events', '*MERGE', 'Synced table']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'SCD2', 12, 'blue', bold=True, mono=True) + t(60, 58, 'history', 7.4, 'ink2'),
    '2. Customer and product history',
    'Banks, insurers and retailers keep SCD2 dimensions for customers, branches and products so that reports use the attributes valid at transaction time.',
    ['Attribute change', '*close + insert', 'Point-in-time reports']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'dedupe', 11, 'violet', bold=True) + t(60, 58, 'insert new only', 7.4, 'ink2'),
    '3. De-duplicated event loads',
    'When a source re-sends events, a MERGE with only WHEN NOT MATCHED THEN INSERT adds new event ids and ignores repeats.',
    ['Re-sent events', '*NOT MATCHED → INSERT', 'No duplicates']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'audit', 11, 'acc', bold=True) + t(60, 58, 'who was it then', 7.4, 'ink2'),
    '4. Audits and regulators',
    'Auditors ask what a customer’s risk category or address was on a given date; SCD2 answers without restoring old backups.',
    ['Question about the past', '*BETWEEN eff dates', 'Answer']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'soft delete', 10, 'acc', bold=True) + t(60, 58, 'keep closed', 7.4, 'ink2'),
    '5. Closed accounts',
    'Instead of deleting closed accounts, many teams MERGE an is_deleted flag, so history and joins stay complete.',
    ['op = D', '*UPDATE flag', 'History kept']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> finish ACID tables (<a href="../01-acid-tables-update-delete/">7.1</a>), joins (<a href="../../03-querying/03-joins/">3.3</a>) and window functions (<a href="../../03-querying/06-window-functions/">3.6</a>).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
