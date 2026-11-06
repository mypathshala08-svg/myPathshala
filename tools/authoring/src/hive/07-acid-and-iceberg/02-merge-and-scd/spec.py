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
    module='07-acid-and-iceberg', lesson='02-merge-and-scd', n='7.2',
    module_label='Module 7 · Transactions, MERGE and Iceberg',
    title='MERGE and slowly changing dimensions',
    desc='Hive MERGE explained with real Hive 4.2.1 results: upserts with WHEN MATCHED UPDATE / DELETE and WHEN NOT MATCHED INSERT in one transaction, the delta folders and ROW__IDs a MERGE writes, the cardinality violation with duplicate source keys, SCD type 1, 2 and 3, a working SCD type 2 MERGE using a NULL join key, proof that it is idempotent, and a point-in-time join that splits a customer’s orders by the plan they had at the time.',
    og_desc='One statement to update, delete and insert, and a type 2 MERGE that keeps history. Real Hive 4.2.1 results, including the error duplicate keys cause.',
    minutes=35, level='Intermediate → Advanced',
    lead='Every night TiffinGo’s app database sends changed customers: upgrades, moves, closed accounts and sign-ups. <b>MERGE</b> applies them to a Hive ACID table in one statement and one transaction. When finance also wants history, the same statement can maintain a <b>slowly changing dimension type 2</b>. Kabir builds both, hits the duplicate-key error, re-runs the job to prove it is safe, and shows why history changes the revenue report. <b>All outputs are real</b>, from Hive 4.2.1.',
    chips=['Real Hive 4.2.1 outputs', 'Upsert in one statement', 'Working SCD type 2', 'Runs in your browser (Python)'],
)

MAIN = '''# MERGE in plain Python: route each source row to a clause
target = {1: ("Bengaluru", "Silver"), 2: ("Mumbai", "Basic"), 3: ("Mumbai", "Gold"),
          4: ("Bengaluru", "Basic"), 5: ("Bengaluru", "Basic"), 6: ("Pune", "Basic")}
source = [(2, "Mumbai", "Gold", "U"), (3, "Pune", "Gold", "U"), (4, "Bengaluru", "Basic", "U"),
          (6, None, None, "D"), (7, "Hyderabad", "Silver", "I")]

for cid, city, plan, op in source:
    if cid in target:                                   # WHEN MATCHED
        if op == "D":
            del target[cid]; print(cid, "DELETE")
        elif target[cid] != (city, plan):              # AND changed
            target[cid] = (city, plan); print(cid, "UPDATE")
        else:
            print(cid, "no change")
    else:                                               # WHEN NOT MATCHED
        target[cid] = (city, plan); print(cid, "INSERT")
print(target)
'''
RUN = dict(
    heading='Run the code: how MERGE routes rows',
    intro='<p>These programs mimic MERGE and SCD type 2 with the same data as the real lab. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('        if op == "D":', 'Listed first, like WHEN MATCHED AND s.op = \'D\' THEN DELETE: the first applicable clause wins.'),
        ('        elif target[cid] != (city, plan):              # AND changed', 'The change condition keeps customer 4 untouched, as its real ROW__ID showed.'),
    ],
    tasks=[
        dict(label='1 · Route the rows', hint='Press <b>Run</b>. The result matches the real table after Step 2.', code=None),
        dict(label='2 · Predict first: duplicate keys', hint='<b>Predict first:</b> what should happen when the source has two rows for customer 2? (Real Hive: Cardinality Violation, nothing applied.)',
             code='''source = [(2, "Gold"), (3, "Gold"), (2, "Silver")]
keys = [k for k, _ in source]
dupes = sorted({k for k in keys if keys.count(k) > 1})
if dupes:
    print(f"Cardinality Violation: keys {dupes} match more than once -> MERGE refused, nothing applied")
else:
    print("ok: every target row matches at most one source row")
'''),
        dict(label='3 · SCD type 2', hint='Changed customers are closed and re-inserted. Real result: 9 rows, 7 current.',
             code='''hist = [[c, p, "2026-10-01", "9999-12-31", True] for c, p in [(1, "Silver"), (2, "Basic"), (3, "Mumbai/Gold"), (4, "Basic"), (5, "Basic"), (6, "Basic")]]
changes = {2: "Gold", 3: "Pune/Gold", 4: "Basic", 7: "Silver"}
for cid, new in changes.items():
    cur = next((r for r in hist if r[0] == cid and r[4]), None)
    if cur and cur[1] != new:
        cur[3], cur[4] = "2026-10-26", False                    # close
        hist.append([cid, new, "2026-10-27", "9999-12-31", True])
    elif cur is None:
        hist.append([cid, new, "2026-10-27", "9999-12-31", True])
print(len(hist), "rows,", sum(r[4] for r in hist), "current")
for r in sorted(hist):
    print(r)
'''),
        dict(label='4 · Point in time', hint='Which version was valid on each order date? Real answer for customer 2: 14 Basic, 5 Gold.',
             code='''versions = [("Basic", "2026-10-01", "2026-10-26"), ("Gold", "2026-10-27", "9999-12-31")]
orders = ["2026-10-03", "2026-10-15", "2026-10-26", "2026-10-27", "2026-10-29"]
for d in orders:
    plan = next(p for p, a, b in versions if a <= d <= b)
    print(d, plan)
'''),
        dict(label='5 · Spot the error', hint='This change check misses a city that was NULL before. Use a null-safe comparison (like Hive’s &lt;=&gt;).', expect='error',
             code='''def changed(old, new):
    if old is None or new is None:
        return False            # like SQL: NULL <> 'Pune' is NULL, not true
    return old != new
old_city, new_city = None, "Pune"
assert changed(old_city, new_city), "a NULL -> Pune change was missed"
print("detected")
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: SCD2 checks',
    intro='<p>Checks every SCD2 table should pass. Run them on <code>dim_customer_hist</code> in the lab.</p>',
    items=[
        dict(title='1 · Exactly one current row per key', cmd='SELECT customer_id, COUNT(*) AS current_rows\nFROM dim_customer_hist WHERE is_current\nGROUP BY customer_id HAVING COUNT(*) <> 1;', file='Beeline',
             output=capf('l72_check1.txt') + '\n(no rows: the check passes)',
             note='Any row returned means the MERGE logic produced two current versions or none.'),
        dict(title='2 · History after the merge, and the re-run', cmd='SELECT COUNT(*) AS rows_after_rerun, SUM(IF(is_current, 1, 0)) AS current_rows\nFROM dim_customer_hist;', file='Beeline',
             output=capf('l72_rerun.txt'),
             note='6 original rows + 2 new versions + 1 new customer = 9; 7 customers are current. The same numbers after a second run prove the job is idempotent.'),
        dict(title='3 · Which version was valid on a date', cmd="SELECT customer_id, city, plan FROM dim_customer_hist\nWHERE DATE '2026-10-20' BETWEEN eff_from AND eff_to AND customer_id IN (2, 3)\nORDER BY customer_id;", file='Beeline',
             output=capf('l72_check3.txt'),
             note='The same BETWEEN condition used in the point-in-time join. On 20 October Ananya was still Basic.'),
    ],
)

TRACE = dict(
    heading='The NULL-key trick, row by row',
    intro='<p>The SCD2 source contains each changed row twice. Watch which copy matches a current target row and which one is inserted.</p>',
    code='''current = {2: "Basic", 3: "Mumbai", 4: "Basic"}
source = [(2, 2, "Gold"), (3, 3, "Pune"), (4, 4, "Basic"), (None, 2, "Gold"), (None, 3, "Pune")]
actions = []
for join_key, cid, val in source:
    if join_key in current:
        if current[join_key] != val:
            actions.append((cid, "close old"))
    else:
        actions.append((cid, "insert new"))
print(actions)
''',
    notes={2: 'Source :: The UNION ALL from Step 6: real keys for all rows, NULL keys for changed rows only.', 5: 'Match :: A NULL join key never matches, exactly like NULL = 2 in SQL.', 10: 'Result :: Customers 2 and 3 are closed and re-inserted; 4 is matched but unchanged.'},
)

WORKED_INTRO = 'Three MERGE tasks from TiffinGo’s data team.'
EXAMPLES = [
    dict(level='b', tag='Pipeline · reconciliation', title='Check a MERGE with counts',
         problem='<p>Before the MERGE the target had 6 rows. The source has 2 updates, 1 delete, 1 insert and 1 unchanged row. Predict the row count after the MERGE and the number of rows that get a new write id.</p>',
         inp='target 6 rows; source: U, U, unchanged, D, I',
         approach=['Rows after = before + inserts − deletes.', 'Rewritten rows = updates + inserts.', 'Compare with the real table.'],
         code='''before = 6
ops = ["U", "U", "same", "D", "I"]
after = before + ops.count("I") - ops.count("D")
new_writeid = ops.count("U") + ops.count("I")
print("rows after:", after, " rows with write id 2:", new_writeid)
''', notes={4: 'Write ids :: The real ROW__ID query showed write id 2 for customers 2, 3 and 7.'},
         tryit='6 rows and 3 rows with write id 2, exactly as in Step 3. A count check like this catches silent logic errors.'),
    dict(level='i', tag='Data quality · de-duplication', title='Make the source safe for MERGE',
         problem='<p>The CDC feed has several events per customer. Keep only the latest per customer before merging, to avoid the cardinality violation.</p>',
         inp='events (customer, ts, plan): (2, 09:00, Silver), (2, 21:30, Gold), (3, 10:15, Gold)',
         approach=['Group events by customer.', 'Keep the one with the latest timestamp.', 'Merge the result.'],
         code='''events = [(2, "09:00", "Silver"), (2, "21:30", "Gold"), (3, "10:15", "Gold")]
latest = {}
for cid, ts, plan in sorted(events, key=lambda e: e[1]):
    latest[cid] = (ts, plan)
print(latest)
''', notes={3: 'Latest wins :: In HiveQL: ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY ts DESC) = 1 in a subquery used as the MERGE source.'},
         tryit='Without this step the real MERGE failed with “Cardinality Violation” and changed nothing.'),
    dict(level='a', tag='Analytics · SCD2', title='Revenue by the plan at order time',
         problem='<p>Using the two versions of customer 2 and her orders, compute revenue by plan with a point-in-time join and with a current-row join, and the difference reported as Gold.</p>',
         inp='versions: Basic 10-01…10-26, Gold 10-27…; orders: 14 before 10-27 at ₹300, 5 after at ₹350 (sample amounts)',
         approach=['Assign each order the version valid on its date.', 'Sum by plan.', 'Compare with all orders labelled Gold.'],
         code='''orders = {"2026-10-02..10-26": (14, 300), "2026-10-27..10-31": (5, 350)}   # (count, amount)
def plan_on(period):
    return "Basic" if period.startswith("2026-10-02") else "Gold"
by_plan = {}
for period, (n, amt) in orders.items():
    by_plan[plan_on(period)] = by_plan.get(plan_on(period), 0) + n * amt
print("point in time:", by_plan)
print("current-row join: Gold =", sum(n * a for n, a in orders.values()))
''', notes={2: 'Validity :: Equivalent to o.order_date BETWEEN eff_from AND eff_to.'},
         tryit='The current-row join overstates Gold revenue by ₹4,200 for just one customer. Counts match the real query: 14 and 5 orders.'),
]

QUIZ = mix([
    dict(q='Beginner: What does MERGE do?', options=['Joins two tables in a SELECT', 'Applies inserts, updates and deletes from a source to a target in one statement', 'Merges small files', 'Combines two partitions'], answer=1,
         why='One statement, one transaction.'),
    dict(q='Beginner: Which table must be transactional in a MERGE?', options=['The source', 'The target', 'Both', 'Neither'], answer=1,
         why='Only the target is written; the source can be any table or subquery.'),
    dict(q='Beginner: In SCD type 2, what happens when a customer changes city?', options=['The row is overwritten', 'The old row is closed and a new row added', 'A column prev_city is filled', 'Nothing'], answer=1,
         why='Type 1 overwrites, type 3 uses a previous-value column.'),
    dict(q='Intermediate: Two source rows match the same target row. What did Hive 4.2.1 do?', options=['Used the first row', 'Used the last row', 'Failed with Cardinality Violation and changed nothing', 'Inserted a duplicate'], answer=2,
         why='hive.merge.cardinality.check=true. De-duplicate the source.'),
    dict(q='Intermediate: Why add “AND (t.city <> s.city OR t.plan <> s.plan)” to WHEN MATCHED … UPDATE?', options=['It is required syntax', 'So unchanged rows are not rewritten', 'To delete rows', 'To speed up the join'], answer=1,
         why='Customer 4 kept write id 1 in our lab.'),
    dict(q='Intermediate: In the SCD2 MERGE, why do changed rows appear with a NULL join key?', options=['To delete them', 'Because NULL never matches, so they reach WHEN NOT MATCHED and are inserted', 'To skip them', 'NULL means unchanged'], answer=1,
         why='The same change must both close the old version (match) and insert a new one (no match).'),
    dict(q='Advanced: What did re-running the SCD2 MERGE do?', options=['Added duplicate versions', 'Nothing: still 9 rows, 7 current', 'Failed', 'Deleted history'], answer=1,
         why='The job is idempotent, so failed nights can be re-run safely.'),
    dict(q='Advanced: t.city is NULL and s.city is \'Pune\'. Is the change detected by t.city <> s.city?', options=['Yes', 'No: the comparison is NULL, not true', 'Only in strict mode', 'Hive raises an error'], answer=1,
         why="Use NOT (t.city <=> s.city) or compare hashes."),
])

REVISION = [
    '<code>MERGE INTO t USING s ON key WHEN MATCHED [AND c] THEN UPDATE SET … | DELETE WHEN NOT MATCHED [AND c] THEN INSERT VALUES (…)</code>.',
    'Target = full ACID table; source = anything. One statement = one write id = one transaction.',
    'First applicable clause wins: put DELETE (op = \'D\') before UPDATE.',
    'Add a change condition to UPDATE; use null-safe <code>&lt;=&gt;</code> or hashes for NULLs.',
    '<b>Cardinality violation:</b> one target row matched by two source rows → whole MERGE fails, nothing applied. De-duplicate with ROW_NUMBER.',
    '<b>SCD1</b> overwrite · <b>SCD2</b> eff_from / eff_to / is_current · <b>SCD3</b> previous-value column.',
    '<b>SCD2 MERGE:</b> source = all rows with real key ∪ changed rows with NULL key; match on key AND is_current; close on MATCHED, insert on NOT MATCHED.',
    'Idempotent: re-run gave 9 rows, 7 current. Check one current row per key.',
    '<b>Point-in-time join:</b> <code>o.date BETWEEN h.eff_from AND h.eff_to</code> (14 Basic + 5 Gold vs 19 “Gold”).',
]
FAQ = [
    ('Can I MERGE into an Iceberg table?', 'Yes. Hive 4 supports MERGE on Iceberg tables with the same syntax, writing Iceberg delete files and data files instead of Hive deltas (Lesson 7.3). This is useful when Spark or Trino also read the table.'),
    ('Is MERGE faster than a separate UPDATE, DELETE and INSERT?', 'Usually yes: it reads the source and target once, and it is one transaction instead of three, so readers never see a half-applied change. The cost is a join between source and target, so filter the target (partitions, is_current) in the ON clause.'),
    ('How do I choose eff_from for a change?', 'Use the time the change happened in the source system if you have it (from CDC), otherwise the load date. Keep the convention consistent, and make eff_to the day before the next version’s eff_from (or use half-open ranges, eff_from ≤ date &lt; eff_to) so versions never overlap.'),
    ('Should every dimension be SCD2?', 'No. Keep history only for attributes that matter for analysis (plan, city, segment). Fast-changing or irrelevant attributes (last login time) belong in a separate table or SCD1, otherwise the dimension grows a new version for every small change.'),
    ('What does MERGE do with rows in the target that are not in the source?', 'Nothing. Hive’s MERGE has no WHEN NOT MATCHED BY SOURCE clause. To delete target rows that disappeared from a full extract, add an explicit delete marker to the source or run a separate DELETE … WHERE key NOT IN (…).'),
]

PRACTICE_INTRO = 'Programs that simulate MERGE and SCD logic, with the HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Classify source rows', stmt='Mark each source key as MATCHED or NOT MATCHED against the target keys.', inp='target {1..6}, source {2, 3, 4, 6, 7}',
         code='''target = {1, 2, 3, 4, 5, 6}
for k in [2, 3, 4, 6, 7]:
    print(k, "MATCHED" if k in target else "NOT MATCHED")
''', explain='Only customer 7 is new, as in the real MERGE.'),
    dict(level='easy', title='Find duplicate keys', stmt='Find keys that appear more than once in the source.', inp='[2, 3, 4, 6, 7, 2]',
         code='''keys = [2, 3, 4, 6, 7, 2]
print(sorted({k for k in keys if keys.count(k) > 1}))
''', explain='Key 2 caused the real Cardinality Violation. In HiveQL: GROUP BY customer_id HAVING COUNT(*) &gt; 1.'),
    dict(level='easy', title='SCD type for a column', stmt='Choose SCD1 or SCD2 for each attribute.', inp='plan, city, last_login, phone',
         code='''choice = {"plan": "SCD2", "city": "SCD2", "last_login": "SCD1", "phone": "SCD1"}
print(choice)
''', explain='Keep history where analysis needs it; overwrite volatile or irrelevant attributes.'),
    dict(level='medium', title='Rows after SCD2', stmt='6 current customers; 2 change, 1 is new, 1 is unchanged. How many rows and current rows after the MERGE?', inp='6, 2 changes, 1 new',
         code='''rows = 6 + 2 + 1
current = 6 + 1
print(rows, current)
''', explain='9 rows, 7 current: the real result.'),
    dict(level='medium', title='Build the SCD2 source', stmt='Generate the (join_key, customer) pairs for the SCD2 MERGE source.', inp='all staging keys {2, 3, 4, 7}; changed {2, 3}',
         code='''staging, changed = [2, 3, 4, 7], {2, 3}
src = [(k, k) for k in staging] + [(None, k) for k in staging if k in changed]
print(src)
''', explain='Six source rows: four with real keys, two with NULL keys for the changed customers.'),
    dict(level='medium', title='Null-safe change check', stmt='Detect changes including NULL → value.', inp='pairs of old/new city',
         code='''def changed(a, b):
    return not (a == b or (a is None and b is None))
for old, new in [("Mumbai", "Pune"), (None, "Pune"), (None, None), ("Pune", "Pune")]:
    print(old, new, changed(old, new))
''', explain="Hive: NOT (t.city <=> s.city). Plain <> would miss the second case."),
    dict(level='business', title='Revenue overstatement', stmt='How much Gold revenue does a current-row join overstate for customer 2?', inp='14 Basic orders at ₹300 (sample)',
         code='''print(14 * 300, "rupees wrongly counted as Gold")
''', explain='₹4,200 for one customer; across thousands of upgrades the plan report would be badly wrong.'),
    dict(level='business', title='Nightly job checklist', stmt='Print the steps of a safe nightly SCD2 job.', inp='—',
         code='''steps = ["load staging", "keep latest row per key", "MERGE (close + insert)",
         "check one current row per key", "check counts", "compact if many deltas"]
for i, s in enumerate(steps, 1):
    print(i, s)
''', explain='Each step corresponds to something we ran or a failure we hit in this lesson.'),
]

SCN_INTRO = 'MERGE and SCD questions are standard for data engineering roles, often as a whiteboard exercise.'
SCENARIOS = (
    scn('Any company · SQL', 'Fresher', '“What is an upsert?”',
        'Explain upsert and how to do it in Hive.',
        'do you know MERGE and its requirement?',
        '<p>Update the row if its key exists, insert it if not. In Hive: <code>MERGE INTO target t USING source s ON t.id = s.id WHEN MATCHED THEN UPDATE SET … WHEN NOT MATCHED THEN INSERT VALUES (…)</code>, where the target is a transactional ORC table. It runs as one transaction.</p>', 'Describing INSERT OVERWRITE of the whole table as an upsert.') +
    scn('Data engineering', 'Mid-level', 'MERGE fails with a cardinality violation',
        'The nightly MERGE fails: “Cardinality Violation in Merge statement”.',
        'do you know the cause and the fix?',
        '''<ol>
          <li>The source has more than one row for some keys (several CDC events, or a bad join).</li>
          <li>Find them: GROUP BY key HAVING COUNT(*) &gt; 1.</li>
          <li>Keep the latest per key with ROW_NUMBER in the source subquery; the target was not changed, so just re-run.</li>
        </ol>''', 'Setting hive.merge.cardinality.check=false, which makes the result unpredictable.') +
    scn('Analytics', 'Mid-level', 'Design an SCD2 customer dimension',
        'Design a customer dimension that answers “which plan was the customer on when they ordered?”.',
        'can you design columns, load logic and queries?',
        '''<ul>
          <li>Columns: business key, attributes, eff_from, eff_to (9999-12-31 for current), is_current; optionally a surrogate key.</li>
          <li>Load: MERGE closing changed current rows and inserting new versions (NULL-key trick), idempotent.</li>
          <li>Query: join facts on key AND fact_date BETWEEN eff_from AND eff_to; test one current row per key.</li>
        </ul>''', 'Storing only the current value and trying to rebuild history from logs later.') +
    scn('Platform', 'Senior', 'Large nightly MERGE too slow',
        'A MERGE of 50 lakh changes into a 2-billion-row ACID table takes 4 hours.',
        'can you optimise reads, writes and table health?',
        '''<ul>
          <li>Prune the target in ON (partitions, is_current), send only real changes (hash compare).</li>
          <li>Check deltas and compaction status; compact after the merge.</li>
          <li>Consider partitioning the target by the column most changes are filtered on, or Iceberg with merge-on-read deletes.</li>
        </ul>''', 'Running the MERGE more often without measuring where the time goes.')
)
