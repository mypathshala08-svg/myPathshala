import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return re.sub(r'; Query ID[^\n]*', '', open(CAP + n).read().rstrip())
BODY = body(HERE)

META = dict(
    module='12-capstone', lesson='02-build-the-warehouse', n='12.2',
    module_label='Module 12 · Capstone: a TiffinGo data warehouse',
    title='Capstone part 2: build an idempotent Hive warehouse, raw to gold',
    desc='Build the TiffinGo warehouse in Hive 4.2.1 with one nightly script: typed staging with a quarantine of 112 rejected rows, a MERGE upsert into a partitioned ACID fact (47,553 orders, reconciled with raw), an SCD type 2 customer dimension, delivery events, a gold table rebuilt only for touched dates, and an audit table. Backfill 31 days, then test: re-runs found a real SCD 2 bug, a DATE_FORMAT weekend bug and a Tez counter limit, all fixed. Answer the CEO with point-in-time joins and prove partition pruning.',
    og_desc='31 nightly loads, 3 real bugs found by testing, and a CEO answer that finance can reconcile to the paisa.',
    minutes=60, level='Intermediate → Advanced',
    lead='Lesson 12.1 produced the design. This lesson builds it: thirteen tables, one nightly HiveQL script run 31 times, and the tests that make it trustworthy. The tests found three real bugs, and you will see each one and its fix. <b>All outputs are real</b>, from our Hive 4.2.1 lab.',
    chips=['Hive 4.2.1 · real outputs', 'MERGE · SCD 2 · dynamic partitions', '3 real bugs found and fixed', 'Runs in your browser (Python)'],
)

MAIN = '''# The nightly logic of fact_orders, in Python: MERGE with "newer wins"
fact = {}                      # order_id -> (status, updated_at, order_date)
loads = {
    "10-05": [("5006782", "DELIVERED", "10-05 22:59", "10-05"),
              ("5006782", "DELIVERED", "10-05 22:59", "10-05")],   # duplicate line
    "10-06": [("5006782", "DELIVERED", "10-05 22:59", "10-05")],   # re-sent
    "10-09": [("5006782", "REFUNDED",  "10-09 14:47", "10-05")],   # status change
}
for load, rows in loads.items():
    newest = {}
    for oid, st, upd, od in rows:                 # ROW_NUMBER() ... rn = 1
        if oid not in newest or upd > newest[oid][1]:
            newest[oid] = (st, upd, od)
    for oid, (st, upd, od) in newest.items():     # MERGE
        if oid not in fact or upd > fact[oid][1]:
            fact[oid] = (st, upd, od)
    print(load, fact)
'''
RUN = dict(
    heading='Run the code: the pipeline’s rules in Python',
    intro='<p>Each program models one step of <code>daily_load.hql</code> on a few rows, so you can change the data and see the rule work. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('        if oid not in fact or upd > fact[oid][1]:', 'The guard <code>WHEN MATCHED AND s.updated_at &gt; t.updated_at</code>: re-sent rows change nothing.'),
        ('        if oid not in newest or upd > newest[oid][1]:', 'Like <code>ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC)</code> = 1.'),
    ],
    tasks=[
        dict(label='1 · MERGE, newest wins', hint='Press <b>Run</b>. Then run the loop twice (copy the for-loop) and check the result does not change: idempotence.', code=None),
        dict(label='2 · SCD 2 with the guard', hint='Apply a change only if it is newer than the current version. Remove the guard and re-run the old change to see Step 7’s bug.',
             code='''dim = [["Bengaluru", "09-30 23:00", "9999", True]]          # city, valid_from, valid_to, current
def apply(city, upd):
    cur = [v for v in dim if v[3]][0]
    if upd > cur[1] and city != cur[0]:                    # the guard from Step 6
        cur[2], cur[3] = upd, False
        dim.append([city, upd, "9999", True])
apply("Mumbai", "10-14 17:39")
apply("Navi Mumbai", "10-28 21:05")
apply("Mumbai", "10-14 17:39")                             # re-run of 15 October
for v in dim: print(v)
'''),
        dict(label='3 · Predict first: touched dates', hint='<b>Predict first</b> which gold dates this load must rebuild, then run.',
             code='''load = "10-10"
rows = [("A", "10-10"), ("B", "10-10"), ("C", "10-09"), ("D", "10-06"), ("E", "10-10"), ("F", "10-08"), ("G", "10-07")]
touched = sorted({order_date for _, order_date in rows})
print("rebuild gold for:", touched, "->", len(touched), "partitions")
'''),
        dict(label='4 · Point-in-time join', hint='Credit each order to the plan valid at the order time, as in Step 12.',
             code='''versions = [("09-30 23:00", "10-25 17:31", "Basic"), ("10-25 17:31", "9999", "Silver")]
orders = [("10-05 13:00", 450), ("10-20 20:00", 300), ("10-28 12:30", 520)]
by_plan = {}
for ts, amt in orders:
    plan = [p for start, end, p in versions if start <= ts < end][0]
    by_plan[plan] = by_plan.get(plan, 0) + amt
print(by_plan)
'''),
        dict(label='5 · Spot the error', hint='This join has no date condition, like the last query of Step 12. Fix it so each order matches exactly one version.', expect='error',
             code='''versions = [("09-30", "10-25", "Basic"), ("10-25", "9999", "Silver")]
orders = [("10-05", 450), ("10-28", 520)]
joined = [(ts, amt, p) for ts, amt in orders for s, e, p in versions]   # bug: no date condition
assert len(joined) == len(orders), f"{len(joined)} joined rows for {len(orders)} orders"
print(joined)
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: more from the finished warehouse',
    intro='<p>Three more queries on the loaded warehouse. <b>Outputs are real</b> (Hive 4.2.1).</p>',
    items=[
        dict(title='1 · Best restaurant per city (window function)', cmd="SELECT city, name, cuisine, net FROM (\n  SELECT r.city, r.name, r.cuisine, SUM(f.amount) AS net,\n         RANK() OVER (PARTITION BY r.city ORDER BY SUM(f.amount) DESC) AS rk\n  FROM fact_orders f JOIN dim_restaurant r ON r.restaurant_id = f.restaurant_id\n  WHERE f.status = 'DELIVERED' AND f.order_date BETWEEN DATE '2026-10-01' AND DATE '2026-10-31'\n  GROUP BY r.city, r.name, r.cuisine) x\nWHERE rk = 1 ORDER BY net DESC;", file='beeline',
             output=capf('l122_top.txt'),
             note='A window function over an aggregate: rank restaurants inside each city by net revenue, keep rank 1. The partition filter prunes to October only.'),
        dict(title='2 · One gold partition', cmd="SELECT order_date, city, orders, delivered, cancelled, refunded, net_revenue,\n       avg_delivery_min, p90_delivery_min\nFROM gold_city_daily WHERE order_date = DATE '2026-10-05' ORDER BY net_revenue DESC;", file='beeline',
             output=capf('l122_gold_day.txt'),
             note='Six rows per day, one per city. The 4 refunds in Bengaluru on 5 October arrived in later loads and were applied when those loads rebuilt this partition.'),
        dict(title='3 · Column statistics for the optimiser', cmd="ANALYZE TABLE fact_orders PARTITION (order_date) COMPUTE STATISTICS FOR COLUMNS;\nDESCRIBE FORMATTED fact_orders PARTITION (order_date='2026-10-05') amount;", file='beeline',
             output=capf('l122_analyze.txt'),
             note='Min, max, nulls and distinct counts per partition feed the cost-based optimiser (Lesson 8.2). Run ANALYZE after large loads or schedule it weekly.'),
    ],
)

TRACE = dict(
    heading='Follow one order through four loads',
    intro='<p>Order 5006782’s journey: a duplicate, a re-send and a refund. Watch when the fact row actually changes.</p>',
    code='''fact = {}
for load, st, upd in [("10-05", "DELIVERED", 1), ("10-05", "DELIVERED", 1), ("10-06", "DELIVERED", 1), ("10-09", "REFUNDED", 5)]:
    old = fact.get("5006782")
    if old is None or upd > old[1]:
        fact["5006782"] = (st, upd)
print(fact)
''',
    notes={1: 'Start :: The fact table is empty.', 3: 'Lookup :: Find the current row for this order, if any.', 4: 'Guard :: Only insert, or update when the version is newer.', 5: 'Write :: The MERGE writes a new row version.'},
)

WORKED_INTRO = 'Three tasks from the build, written as small programs, with the HiveQL alongside.'
EXAMPLES = [
    dict(level='b', tag='Data engineering · quarantine', title='First failed rule wins',
         problem='<p>Assign each raw row exactly one reject reason, in a fixed order, as the CASE in Step 4 does.</p>',
         inp='four raw rows from 2 October',
         approach=['List the rules in order.', 'Return the first that fails.', 'None means accepted.'],
         code='''RULES = [("missing customer", lambda r: r["customer_id"] == ""),
         ("bad amount", lambda r: not r["amount"].replace(".", "", 1).lstrip("-").isdigit()),
         ("non-positive amount", lambda r: float(r["amount"]) <= 0),
         ("unknown restaurant", lambda r: int(r["restaurant_id"]) > 150)]
def reason(r):
    for name, broken in RULES:
        if broken(r):
            return name
rows = [dict(customer_id="2843", amount="-90.00", restaurant_id="12"), dict(customer_id="", amount="180.00", restaurant_id="9"),
        dict(customer_id="2785", amount="240.00", restaurant_id="999"), dict(customer_id="295", amount="NA", restaurant_id="7")]
for r in rows:
    print(r["customer_id"] or "(none)", "->", reason(r))
''', notes={5: 'Order :: Like CASE WHEN … WHEN …: the first true branch wins.', 10: 'Result :: The same four reasons as the real quarantine sample.'},
         tryit='In HiveQL, add a WHEN for payment NOT IN (\'UPI\', \'Card\', \'COD\', \'Wallet\').'),
    dict(level='i', tag='Data engineering · gold', title='Rebuild only touched partitions',
         problem='<p>Given today’s accepted rows, compute the gold partitions to overwrite and the rows each will contain.</p>',
         inp='fact rows after the MERGE',
         approach=['Collect order dates from today’s rows.', 'Recompute those dates from the whole fact.', 'Leave all other dates alone.'],
         code='''fact = [("10-09", "Mumbai", 300), ("10-09", "Pune", 200), ("10-10", "Mumbai", 450), ("10-08", "Mumbai", 120)]
today = [("10-10", "Mumbai"), ("10-09", "Pune")]
touched = {d for d, _ in today}
gold = {}
for d, city, amt in fact:
    if d in touched:
        gold[(d, city)] = gold.get((d, city), 0) + amt
for k in sorted(gold): print(k, gold[k])
''', notes={3: 'Touched :: Two dates: 10-09 and 10-10.', 6: 'Recompute :: Mumbai 10-09 is rebuilt too, although today’s row was Pune: the whole date is recomputed.'},
         tryit='The HiveQL: INSERT OVERWRITE … PARTITION (order_date) SELECT … WHERE f.order_date IN (SELECT DISTINCT order_date FROM stg_orders WHERE reject_reason IS NULL).'),
    dict(level='a', tag='Quality engineering · tests', title='A reconciliation test suite',
         problem='<p>Turn the checks of Steps 5, 8 and 9 into PASS/FAIL lines a scheduler can alert on.</p>',
         inp='numbers from the lab',
         approach=['Each test compares two numbers.', 'Print PASS or FAIL with the values.', 'Exit with an error if any fails.'],
         code='''tests = [("raw valid = fact rows", 47553, 47553),
         ("gold net = fact net", 15395190.00, 15395190.00),
         ("one current row per customer", 3664, 3664),
         ("quarantine = profile", 112, 31 + 31 + 31 + 11 + 8)]
failed = 0
for name, a, b in tests:
    ok = a == b
    failed += not ok
    print(("PASS" if ok else "FAIL"), name, a, b)
print("all tests passed" if not failed else f"{failed} failed")
''', notes={6: 'Compare :: Exact equality: money in DECIMAL, never FLOAT.', 9: 'Report :: In Hive: SELECT IF(a = b, \'PASS\', \'FAIL\') … per test.'},
         tryit='Lesson 12.3 runs these tests as one HiveQL file after every load.'),
]

QUIZ = mix([
    dict(q='Beginner: Which statement makes a nightly fact load safe to re-run?', options=['INSERT INTO fact_orders', 'MERGE on order_id with a “newer version only” condition', 'LOAD DATA INPATH', 'CREATE TABLE AS SELECT'], answer=1,
         why='Re-sent or repeated rows match and change nothing.'),
    dict(q='Beginner: How is the load date passed to daily_load.hql?', options=['Edited in the file each night', '--hivevar load_date=… and ${hivevar:load_date} in the script', 'A Java UDF', 'An environment variable only'], answer=1,
         why='Substituted before each statement is compiled.'),
    dict(q='Beginner: What did DATE_FORMAT(d, \'u\') return in Hive 4.2.1?', options=['The day of week', 'The year, 2026', 'NULL', 'An error'], answer=1,
         why='Java DateTimeFormatter: u is the year. Use DAYOFWEEK.'),
    dict(q='Intermediate: Why does the order MERGE use ROW_NUMBER first?', options=['To sort the output', 'A load can contain several rows for one order, and MERGE fails if two source rows match one target row', 'To create surrogate keys', 'For partition pruning'], answer=1,
         why='The cardinality check rejects duplicate matches.'),
    dict(q='Intermediate: The 10 October load touched five order dates. What did the gold step rewrite?', options=['All 31 partitions', 'Only those five partitions', 'Only 10 October', 'Nothing'], answer=1,
         why='Dynamic partition overwrite replaces only partitions in the output.'),
    dict(q='Intermediate: How many rows did fact JOIN dim_customer give without a date condition?', options=['47,553', '54,418', '4,166', '43,531'], answer=1,
         why='Customers with several versions multiply their orders.'),
    dict(q='Advanced: Why did re-running 15 October break dim_customer at first?', options=['Disk full', 'The old file was compared with the current version and treated as a change', 'MERGE is not supported', 'Duplicate order ids'], answer=1,
         why='Fixed by requiring updated_at > valid_from.'),
    dict(q='Advanced: In Hive 4, a non-transactional “managed” ORC table shows which table type?', options=['MANAGED_TABLE', 'EXTERNAL_TABLE with external.table.purge=TRUE', 'VIRTUAL_VIEW', 'INDEX_TABLE'], answer=1,
         why='TRANSLATED_TO_EXTERNAL=TRUE; DROP still deletes the data.'),
])

REVISION = [
    'One script per <code>load_date</code>: <code>beeline --hivevar load_date=… -f daily_load.hql</code>.',
    '<b>Overwrite</b> what can be recomputed (staging, quarantine, deliveries, gold); <b>MERGE</b> what changes (fact, SCD 2).',
    'MERGE pattern: <code>ROW_NUMBER()</code> → one row per key; <code>WHEN MATCHED AND s.updated_at &gt; t.updated_at</code>.',
    'SCD 2 in Hive: source twice (join_key = id closes, join_key = NULL inserts) + guard <code>updated_at &gt; valid_from</code>.',
    'Gold: dynamic-partition overwrite of the <b>touched</b> event dates.',
    'Test by <b>re-running</b> old loads and <b>reconciling</b>: raw valid 47,553 = fact; gold net = fact net; 112 rejects.',
    'Point-in-time join: <code>order_ts &gt;= valid_from AND order_ts &lt; valid_to</code>.',
    'Bugs found: <code>DATE_FORMAT \'u\'</code> = year in Hive 4; SCD 2 replay; Tez 120-counter limit → <code>STACK</code>.',
]
FAQ = [
    ('Why not one big INSERT OVERWRITE of the whole fact table every night?', 'It works for small tables and is perfectly idempotent. But the cost grows with history, not with the day’s changes, and you lose the ability to update rows in place. MERGE on an ACID table touches only changed rows; at TiffinGo’s real scale that is the difference between minutes and hours.'),
    ('Why does the MERGE not filter the target by order_date?', 'Late rows and refunds can belong to any earlier date, so the target cannot be pruned without knowing a limit. At large scale you add one, for example <code>AND t.order_date &gt;= DATE_SUB(load_date, 30)</code>, and send older corrections through a separate repair job.'),
    ('Could Spark do this instead of Hive?', 'Yes. The design (layers, keys, idempotent steps, SCD 2, touched dates) is engine-independent. Spark with Iceberg or Delta tables is a common choice today; Hive ACID tables are reliably read only by Hive (Lesson 11.1), which matters if Trino must read the fact.'),
    ('Why keep load_date inside fact_orders?', 'It tells you which load last changed each order. When a number changes, you can see which night’s file caused it, and a faulty load can be found and repaired.'),
    ('What about deletes in the source?', 'Our source never deletes orders; it changes their status. If a source sends deletes (an op column with D), add a <code>WHEN MATCHED AND s.op = \'D\' THEN DELETE</code> branch to the MERGE, or mark the row as deleted to keep history.'),
]

PRACTICE_INTRO = 'Programs that practise the pipeline’s rules, with the HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Reconcile fact with raw', stmt='Check that fact rows equal distinct raw orders minus rejected orders.', inp='47,665 distinct · 112 rejected · 47,553 fact',
         code='''print("PASS" if 47665 - 112 == 47553 else "FAIL")
''', explain='Holds because every rejected row had its own order id that never appeared in a valid row.'),
    dict(level='easy', title='Audit rows with STACK', stmt='Turn one row of four columns into four (step, n) rows.', inp='raw 1741, rejected 5, accepted 1730, dates 5',
         code='''row = dict(raw_rows=1741, rejected=5, accepted_distinct=1730, order_dates_touched=5)
for step, n in row.items():
    print(step, n)
''', explain='LATERAL VIEW STACK(4, \'raw_rows\', s.raw_rows, …) x AS step, n.'),
    dict(level='easy', title='Weekend flag', stmt='Mark Saturday and Sunday using DAYOFWEEK numbering.', inp='DAYOFWEEK: 1 = Sunday … 7 = Saturday',
         code='''import datetime as dt
for day in range(1, 5):
    d = dt.date(2026, 10, day)
    dow = (d.isoweekday() % 7) + 1          # Hive DAYOFWEEK numbering
    print(d, dow, dow in (1, 7))
''', explain='DAYOFWEEK(d) IN (1, 7). Never depend on a format letter you have not tested.'),
    dict(level='medium', title='Newest version per key', stmt='Keep the newest row per order from a load with duplicates.', inp='five rows',
         code='''rows = [(1, "DELIVERED", 3), (1, "DELIVERED", 3), (2, "CANCELLED", 1), (1, "REFUNDED", 7), (2, "CANCELLED", 1)]
best = {}
for k, st, upd in rows:
    if k not in best or upd > best[k][1]:
        best[k] = (st, upd)
print(best)
''', explain='SELECT * FROM (SELECT s.*, ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC) rn FROM stg_orders s) x WHERE rn = 1.'),
    dict(level='medium', title='Revenue overstatement, now real', stmt='Compute how much the old report overstated Mumbai.', inp='raw ₹42,77,880 · gold ₹38,36,320',
         code='''raw, gold = 4277880, 3836320
print(f"₹{raw - gold:,} too high ({100 * (raw - gold) / gold:.1f}%)")
''', explain='The assumed value in Lesson 12.1’s practice problem is now replaced by the real gold number.'),
    dict(level='medium', title='Find broken SCD intervals', stmt='Detect versions whose valid_to is before valid_from.', inp='versions of customer 1380 after the bug',
         code='''versions = [("09-30", "10-14"), ("10-14", "10-28"), ("10-14", "9999"), ("10-28", "10-14")]
bad = [v for v in versions if v[1] < v[0]]
print(len(bad), "broken:", bad)
''', explain='SELECT … WHERE valid_to < valid_from: should always return 0 rows. Add it to the test suite.'),
    dict(level='business', title='Gold vs current plan', stmt='How much revenue would be wrongly credited to Gold using today’s plan?', inp='₹17,76,740 as of order · ₹19,19,200 current',
         code='''pit, cur = 1776740, 1919200
print(f"₹{cur - pit:,} ({100 * (cur - pit) / pit:.1f}%) over-credited to Gold")
''', explain='A pricing team would overestimate the value of the Gold plan by 8%.'),
    dict(level='business', title='Nightly runtime budget', stmt='Will 31 loads at the measured speed fit a 4-hour backfill window?', inp='901 s for 31 loads',
         code='''total_s = 901
print(f"{total_s / 60:.1f} min for a month; a year of backfill ≈ {total_s * 12 / 3600:.1f} h")
''', explain='Measured in the lab; on a cluster the fixed overhead per statement is lower and data size dominates.'),
]

SCN_INTRO = 'Questions about building pipelines that interviewers ask after you describe your project.'
SCENARIOS = (
    scn('Any company · project round', 'Fresher', '“How did you handle duplicates?”',
        'You mention that the source sent duplicates.',
        'do you know window functions and MERGE?',
        '<p>Within a load, <code>ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC)</code> keeps one row per order. Across loads, MERGE on <code>order_id</code> updates only when the incoming <code>updated_at</code> is newer. Result: 48,871 raw rows became 47,553 orders, exactly the valid distinct ids in raw.</p>', '“I used DISTINCT” (it keeps both versions of a refunded order).') +
    scn('Product company · reliability', 'Mid-level', 'The job ran twice',
        'A scheduler bug ran last night’s load twice. Are the numbers doubled?',
        'is your pipeline idempotent and can you prove it?',
        '''<ul>
          <li>No: every step overwrites partitions or merges by key with a newer-only guard.</li>
          <li>Proof: re-run tests on old dates gave identical counts and sums (fact 47,553, ₹1,53,95,190).</li>
          <li>The audit table shows two runs with the same numbers, which is evidence for the incident report.</li>
        </ul>''', 'Saying “it should be fine” without a test.') +
    scn('Fintech · modelling', 'Mid-level', 'SCD 2 gone wrong',
        'After a backfill, some customers have two current rows and intervals that end before they start.',
        'can you debug an SCD 2 load?',
        '''<ol>
          <li>Query: customers with SUM(is_current) &lt;&gt; 1, and rows with valid_to &lt; valid_from.</li>
          <li>Cause: replayed old changes compared with newer versions, or changes processed out of order.</li>
          <li>Fix: only apply changes newer than the current valid_from; rebuild the dimension by replaying loads in order.</li>
        </ol>''', 'Deleting the bad rows by hand without fixing the MERGE.') +
    scn('Analytics platform', 'Senior', 'Late data and dashboards',
        'Dashboards for yesterday change during the next three days. Users complain.',
        'do you understand late data trade-offs?',
        '''<ul>
          <li>Explain why: late orders, refunds and delivery events are applied to their event date (5 dates touched by one load in our lab).</li>
          <li>Offer a “day closed after N days” flag in gold, and show both provisional and final numbers.</li>
          <li>Keep correctness: never freeze numbers by ignoring late rows.</li>
        </ul>''', 'Loading late rows into today’s date to keep yesterday stable.')
)
