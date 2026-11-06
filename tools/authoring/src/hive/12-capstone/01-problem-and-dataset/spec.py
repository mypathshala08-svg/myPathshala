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
    module='12-capstone', lesson='01-problem-and-dataset', n='12.1',
    module_label='Module 12 · Capstone: a TiffinGo data warehouse',
    title='Capstone part 1: the business problem and profiling the dataset',
    desc='Start a real Hive data warehouse project: turn the CEO’s question into KPIs, inventory 94 landing files (orders CSV, customer CDC, JSON delivery events, restaurants), register them as raw external tables, and profile them in Hive 4.2.1: 546 duplicate rows, 660 refund versions, 2,078 late rows, 112 broken rows of five kinds, 469 customers who changed city or plan, and events that arrive before their orders. Then design the raw, silver and gold layers, the star schema, the grain, partitions and SCD types.',
    og_desc='The old report said Mumbai made ₹42.8 lakh. The data said otherwise. Profile October’s files in Hive before building the warehouse.',
    minutes=50, level='Intermediate → Advanced',
    lead='The capstone begins like a real project: a business question, messy files and no tables. In this lesson Kabir measures what the files really contain using Hive itself, and every finding becomes a design decision for the warehouse he builds in Lesson 12.2. <b>All outputs are real</b>, from our Hive 4.2.1 lab.',
    chips=['Hive 4.2.1 · real outputs', '94 landing files · 48,871 order rows', 'Requirements → profile → design', 'Runs in your browser (Python)'],
)

MAIN = '''# Profile a small sample of raw order rows the way Step 4 did
rows = [  # order_id, status, updated_at
    ("5006782", "DELIVERED", "2026-10-05 22:59"),
    ("5006782", "DELIVERED", "2026-10-05 22:59"),   # re-sent next night
    ("5006782", "REFUNDED",  "2026-10-09 14:47"),   # a second version
    ("5007134", "DELIVERED", "2026-10-05 14:43"),
    ("5007833", "CANCELLED", "2026-10-05 09:44"),
]
raw_rows = len(rows)
orders = len({r[0] for r in rows})
versions = len(set(rows))
print("raw rows:", raw_rows, "| orders:", orders, "| distinct versions:", versions)
print("exact copies:", raw_rows - versions, "| extra versions:", versions - orders)
'''
RUN = dict(
    heading='Run the code: profiling rules in Python',
    intro='<p>These programs repeat the profiling logic of Steps 4–8 on small samples taken from the lab. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('versions = len(set(rows))', 'A set removes exact copies, like <code>COUNT(DISTINCT order_id, status, updated_at)</code>.'),
        ('orders = len({r[0] for r in rows})', 'Like <code>COUNT(DISTINCT order_id)</code>: the number of business keys.'),
    ],
    tasks=[
        dict(label='1 · Copies versus versions', hint='Press <b>Run</b>. Add another re-sent copy of order 5007134 and predict both numbers first.', code=None),
        dict(label='2 · Keep the newest version', hint='The rule for the fact table: per order, the row with the largest <code>updated_at</code>.',
             code='''rows = [("5006782", "DELIVERED", "2026-10-05 22:59"),
        ("5006782", "REFUNDED",  "2026-10-09 14:47"),
        ("5007134", "DELIVERED", "2026-10-05 14:43")]
latest = {}
for oid, status, upd in rows:
    if oid not in latest or upd > latest[oid][1]:
        latest[oid] = (status, upd)
for oid, (status, upd) in sorted(latest.items()):
    print(oid, status, upd)
'''),
        dict(label='3 · Predict first: which rule fails?', hint='<b>Predict first</b> the reject reason of each row, then run. Rules are checked in this order.',
             code='''def reason(customer_id, order_ts, amount, restaurant_id, known=range(1, 151)):
    if not customer_id: return "missing customer"
    if len(order_ts) != 19 or order_ts[4] != "-": return "bad order_ts"
    try: a = float(amount)
    except ValueError: return "bad amount"
    if a <= 0: return "non-positive amount"
    if int(restaurant_id) not in known: return "unknown restaurant"
    return None
for row in [("2453", "2026-10-01 11:50:00", "NA", "7"), ("", "2026-10-01 12:00:00", "180.00", "9"),
            ("2029", "01/10/2026 12:05", "150.00", "11"), ("2493", "2026-10-01 11:40:00", "240.00", "999"),
            ("17", "2026-10-02 13:40:00", "-90.00", "12"), ("831", "2026-10-05 21:25:00", "730.00", "148")]:
    print(row, "->", reason(*row))
'''),
        dict(label='4 · Late rows', hint='Classify rows by comparing the order date with the load date, as in Step 6.',
             code='''rows = [("2026-10-09 23:55", "2026-10-10"), ("2026-10-10 12:00", "2026-10-10"),
        ("2026-10-05 14:43", "2026-10-09"), ("01/10/2026 12:05", "2026-10-01")]
for ts, load in rows:
    d = ts[:10]
    kind = "bad timestamp" if d[4] != "-" else ("same day" if d == load else "older order")
    print(f"{ts:17} loaded {load} -> {kind}")
'''),
        dict(label='5 · Spot the error', hint='This “total revenue” uses raw rows. The assertion compares it with the correct newest-version, delivered-only total. Fix the program so it passes.', expect='error',
             code='''rows = [("5006782", "DELIVERED", 450.0, "10-05"), ("5006782", "DELIVERED", 450.0, "10-05"),
        ("5006782", "REFUNDED", 450.0, "10-09"), ("5007134", "DELIVERED", 300.0, "10-05")]
total = sum(amount for _, _, amount, _ in rows)        # bug: copies, both versions
correct = 300.0                                         # only 5007134 is delivered in the end
assert total == correct, f"raw sum {total} != net revenue {correct}"
print("ok")
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: more of the profile',
    intro='<p>Three more profiling queries from the lab. <b>Outputs are real</b> (Hive 4.2.1). Build the lab with Lesson 1.5 and the capstone generator, then try them.</p>',
    items=[
        dict(title='1 · Raw tables really are text', cmd='DESCRIBE raw_orders;', file='beeline',
             output=capf('l121_desc.txt'),
             note='Every column is <code>string</code>, and <code>load_date</code> appears as a partition column. Types are applied in the silver layer, where a failed cast can be caught and explained.'),
        dict(title='2 · Reference data from JSON', cmd='SELECT restaurant_id, name, city, cuisine, rating, tags\nFROM raw_restaurants LIMIT 3;', file='beeline',
             output=capf('l121_rest.txt'),
             note='JSON arrays become <code>ARRAY&lt;STRING&gt;</code> directly. 150 restaurants, a full snapshot every time: an SCD type 1 dimension.'),
        dict(title='3 · Every partition is there', cmd='SHOW PARTITIONS raw_orders;', file='beeline',
             output='\n'.join(capf('l121_parts.txt').split('\n')[:6]) + '\n…',
             note='31 partitions, one per nightly drop. A missing date here means a missing file, which is the first thing a nightly job should check.'),
    ],
)

TRACE = dict(
    heading='Follow the profiling counts',
    intro='<p>Watch how the three counts of Step 4 separate copies from versions.</p>',
    code='''rows = [("A", "DELIVERED", 1), ("A", "DELIVERED", 1), ("A", "REFUNDED", 5), ("B", "DELIVERED", 2)]
distinct_versions = set(rows)
orders = {oid for oid, _, _ in rows}
copies = len(rows) - len(distinct_versions)
extra_versions = len(distinct_versions) - len(orders)
print("copies:", copies, "extra versions:", extra_versions)
''',
    notes={1: 'Raw :: Four rows as the source sent them.', 2: 'Distinct :: The set keeps one of the two identical rows.', 3: 'Keys :: Two business keys: A and B.',
           4: 'Copies :: 4 − 3 = 1 exact copy.', 5: 'Versions :: 3 − 2 = 1 extra version (A was refunded).'},
)

WORKED_INTRO = 'Three profiling tasks of the kind a data engineer gets in the first week of a project.'
EXAMPLES = [
    dict(level='b', tag='Data engineering · profiling', title='Daily volume check',
         problem='<p>Flag any nightly load whose row count is far from the usual range.</p>',
         inp='rows per load_date from Step 3',
         approach=['Compute the median.', 'Flag loads outside 50%–150% of it.', 'Print the result.'],
         code='''loads = {"10-01": 1508, "10-02": 1573, "10-03": 1775, "10-04": 1799, "10-05": 1544, "10-06": 1521, "10-07": 120}
vals = sorted(loads.values())
median = vals[len(vals) // 2]
for d, n in loads.items():
    flag = "ALERT" if not 0.5 * median <= n <= 1.5 * median else "ok"
    print(d, n, flag)
''', notes={3: 'Median :: Robust against one bad day, unlike the mean.', 5: 'Rule :: The 120-row day (illustrative) is flagged.'},
         tryit='In Hive: SELECT load_date, COUNT(*) FROM raw_orders GROUP BY load_date, then compare with PERCENTILE_APPROX(n, 0.5).'),
    dict(level='i', tag='Data modelling · SCD', title='Which plan was valid at order time?',
         problem='<p>Given Rohan Gupta’s versions, find his plan for three order dates.</p>',
         inp='customer 1033 versions from Step 8',
         approach=['List versions with valid_from.', 'Each version is valid until the next one starts.', 'Pick the version whose interval contains the order time.'],
         code='''versions = [("2026-09-30 23:00", "Bengaluru", "Basic"),
            ("2026-10-11 21:08", "Navi Mumbai", "Basic"),
            ("2026-10-25 17:31", "Navi Mumbai", "Silver")]
def as_of(ts):
    current = None
    for start, city, plan in versions:
        if start <= ts:
            current = (city, plan)
    return current
for ts in ["2026-10-05 13:00", "2026-10-20 20:00", "2026-10-28 12:30"]:
    print(ts, as_of(ts))
''', notes={5: 'Scan :: Versions are sorted by start time.', 7: 'As of :: Keep the last version that started before the order.'},
         tryit='This is the point-in-time join of Lesson 12.2: order_ts >= valid_from AND order_ts < valid_to.'),
    dict(level='a', tag='Architecture · sizing', title='Size the fact partitions',
         problem='<p>Estimate rows and ORC size per daily partition today and at 50× growth.</p>',
         inp='~1,500 orders/day; ~40 bytes per row in ORC (assumed)',
         approach=['Rows per day × bytes per row.', 'Compare with a 128 MB block.', 'Decide daily or monthly partitions.'],
         code='''rows_per_day, bytes_per_row, block = 1500, 40, 128 * 1024 * 1024
for growth in (1, 50):
    size = rows_per_day * growth * bytes_per_row
    print(f"growth {growth:>2}x: {size / 1024:,.0f} KB per day,",
          f"{100 * size / block:.2f}% of one block")
''', notes={3: 'Today :: About 59 KB per day: far below a block, so daily partitions mean small files.', 4: 'Growth :: Even 50× is still small; monthly partitions would also be fine.'},
         tryit='Lesson 12.3 measures the real files and compacts the ACID deltas.'),
]

QUIZ = mix([
    dict(q='Beginner: Why are all CSV columns STRING in the raw tables?', options=['Hive cannot read numbers from CSV', 'So that no value is lost or silently turned into NULL before we can inspect and explain it', 'STRING is faster', 'ORC requires it'], answer=1,
         why='Types are applied in silver, where a failed cast becomes a reject reason.'),
    dict(q='Beginner: What is the grain of fact_orders?', options=['One row per raw line', 'One row per order, newest version', 'One row per city per day', 'One row per customer'], answer=1,
         why='Duplicates and versions in raw collapse to one row per order_id.'),
    dict(q='Beginner: Which layer answers the CEO directly?', options=['Raw', 'Silver', 'Gold', 'Landing'], answer=2,
         why='Gold tables hold the aggregated KPIs.'),
    dict(q='Intermediate: 48,871 raw rows, 48,325 distinct versions, 47,665 orders. How many exact copies?', options=['1,206', '546', '660', '48,325'], answer=1,
         why='48,871 − 48,325 = 546. The 660 are second versions.'),
    dict(q='Intermediate: Why is fact_orders partitioned by order_date and not load_date?', options=['load_date is a string', 'Reports filter by when the order happened, so partition pruning needs order_date', 'Hive forbids load_date', 'It makes MERGE faster'], answer=1,
         why='load_date stays as a column for audits and re-runs.'),
    dict(q='Intermediate: Rohan moved city on 11 October. Which dimension type reports his 5 October orders with Bengaluru?', options=['SCD type 1', 'SCD type 2', 'SCD type 0', 'A gold table'], answer=1,
         why='Type 2 keeps the old version with valid_from / valid_to.'),
    dict(q='Advanced: Delivery events for 998 orders arrived before the order rows. What must the nightly gold step do?', options=['Ignore those deliveries', 'Rebuild every order date that the load touched, joining the full delivery table', 'Load events only weekly', 'Drop the orders'], answer=1,
         why='When the order arrives the next night, its date is touched and its delivery time is found.'),
    dict(q='Advanced: Which statement about CAST in Hive is true?', options=['CAST(\'NA\' AS DECIMAL) raises an error', 'A failed CAST returns NULL, so you must check for NULL explicitly', 'CAST rounds strings to 0', 'CAST is not allowed on partition columns'], answer=1,
         why='Useful for measuring, dangerous when loading blindly.'),
])

REVISION = [
    'Order of work: <b>requirements (KPIs) → source inventory → profiling → design → code</b>.',
    'Raw layer: <b>external</b> tables, all <b>STRING</b>, partitioned by <code>load_date</code>, registered with <code>MSCK REPAIR</code> or <code>ADD PARTITION</code>.',
    'Profile with three counts: <code>COUNT(*)</code>, <code>COUNT(DISTINCT key)</code>, <code>COUNT(DISTINCT key, version cols)</code> → copies and versions.',
    'Two dates per row: <b>load_date</b> (arrival) and <b>order_date</b> (event). Reports use the event date.',
    'Every quality rule gets a name; broken rows go to <b>quarantine</b> with a reason.',
    'Changing attributes needed “as of” → <b>SCD type 2</b> (valid_from, valid_to, is_current).',
    'State each fact’s <b>grain</b> first: <code>fact_orders</code> = one order, newest version.',
    'Real profile: 48,871 rows · 546 copies · 660 versions · 2,078 late · 112 broken · 469 changed customers.',
]
FAQ = [
    ('Is profiling really part of a Hive project?', 'Yes. In interviews and in real projects, the most common reason for wrong dashboards is an unchecked assumption about the source: a key that is not unique, a date that means something else, a status that changes later. A few <code>COUNT</code> and <code>GROUP BY</code> queries on raw tables catch them before they reach the CEO.'),
    ('Why not let Hive drop bad rows automatically?', 'Because nobody would know. If 3% of payments disappear silently, revenue is wrong and the source team never fixes their export. A quarantine table with a reason per row turns invisible errors into a daily report someone can act on.'),
    ('Medallion or Kimball?', 'They describe the same idea from different angles. Medallion (bronze, silver, gold) describes data quality layers; Kimball describes how to model the presentation layer as star schemas. Our silver layer holds Kimball facts and dimensions; gold holds aggregates.'),
    ('Should raw tables be managed or external?', 'External. The files belong to the source system’s drop zone; dropping or recreating the table must never delete them, and other tools may read the same folders. Silver and gold tables are managed because Hive owns that data.'),
    ('Is 12 MB of data enough for a real capstone?', 'For learning, yes: every problem a 12 TB warehouse has (duplicates, versions, late data, SCD, small files) is present, and every query runs in seconds on a laptop. The design decisions would be the same at scale; only partition sizes and bucketing choices change, which Lesson 12.3 discusses.'),
]

PRACTICE_INTRO = 'Programs that practise the profiling and design decisions, with the HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Copies and versions', stmt='Compute copies and extra versions from the three counts in Step 4.', inp='48,871 · 48,325 · 47,665',
         code='''raw, versions, orders = 48871, 48325, 47665
print("copies:", raw - versions, "extra versions:", versions - orders)
''', explain='SELECT COUNT(*), COUNT(DISTINCT order_id, status, updated_at), COUNT(DISTINCT order_id) FROM raw_orders;'),
    dict(level='easy', title='Total broken rows', stmt='Add up the rejected rows per rule over the month.', inp='31 NA, 8 negative, 11 bad dates, 31 no customer, 31 unknown restaurant',
         code='''rules = {"bad amount": 31, "non-positive amount": 8, "bad order_ts": 11, "missing customer": 31, "unknown restaurant": 31}
print(sum(rules.values()), "rows to quarantine")
''', explain='Valid only because each broken row fails one rule; otherwise count rows, not rules.'),
    dict(level='easy', title='Partition folder name', stmt='Build the landing folder for a load date.', inp='2026-10-05',
         code='''d = "2026-10-05"
print(f"landing/orders/load_date={d}/orders_{d.replace('-', '')}.csv")
''', explain='ALTER TABLE raw_orders ADD IF NOT EXISTS PARTITION (load_date=\'2026-10-05\'); registers it.'),
    dict(level='medium', title='Share of late rows', stmt='What percentage of raw rows describe an older day?', inp='1294 + 663 + 121 of 48,871',
         code='''late = 1294 + 663 + 121
print(f"{late} rows = {100 * late / 48871:.1f}%")
''', explain='Even 4% late data changes daily numbers if gold is built only from today’s file.'),
    dict(level='medium', title='Versions per customer', stmt='Count customers with more than one version.', inp='versions table from Step 8',
         code='''hist = {1: 3195, 2: 438, 3: 28, 4: 3}
changed = sum(n for v, n in hist.items() if v > 1)
print("changed customers:", changed, "| SCD2 rows:", sum(v * n for v, n in hist.items()))
''', explain='4,167 rows in raw_customers become 4,167 versions in dim_customer if every row is a real change.'),
    dict(level='medium', title='Pick the grain', stmt='Choose the grain for three candidate facts.', inp='descriptions',
         code='''facts = {"orders": "one row per order_id, newest updated_at",
         "deliveries": "one row per delivered order (PICKED_UP and DELIVERED pivoted)",
         "city KPIs": "one row per city per order_date"}
for name, grain in facts.items():
    print(f"{name:10}: {grain}")
''', explain='Saying the grain first prevents double counting in joins.'),
    dict(level='business', title='Revenue overstatement', stmt='How much bigger was Mumbai’s raw sum than the corrected value Lesson 12.2 computes?', inp='raw ₹42,77,880; assume corrected ₹38,50,000 (illustrative)',
         code='''raw, corrected = 4277880, 3850000
print(f"overstated by ₹{raw - corrected:,} ({100 * (raw - corrected) / corrected:.1f}%)")
''', explain='Lesson 12.2 replaces the assumed value with the real gold number.'),
    dict(level='business', title='KPI definition sheet', stmt='Print a KPI sheet row for net revenue.', inp='name, formula, grain, owner, freshness',
         code='''kpi = dict(name="Net revenue", formula="SUM(amount) WHERE status = 'DELIVERED' (latest version)",
           grain="city x order_date", owner="Finance", freshness="by 06:00 daily")
for k, v in kpi.items():
    print(f"{k:9}: {v}")
''', explain='Agreeing this before building avoids the “every report differs” problem.'),
]

SCN_INTRO = 'Capstone and project-discussion questions that interviewers ask data engineers.'
SCENARIOS = (
    scn('Any company · project round', 'Fresher', '“Walk me through how you started your project.”',
        'The interviewer asks about your Hive capstone.',
        'do you start from requirements and data, or from code?',
        '<p>Start from the business question (city KPIs for the CEO), define the KPIs with finance (net revenue = delivered only, by order date), list the sources, then profile them in Hive: three counts per key, late-row and rule checks. Only then design layers and tables. Give one number: “I found 546 duplicate rows and 660 refund versions, so I chose MERGE on order_id.”</p>', 'Starting with “I created a table and loaded the CSV”.') +
    scn('E-commerce · data quality', 'Mid-level', 'The dashboard is 10% too high',
        'Finance says your city revenue is 10% higher than their ledger.',
        'can you find double counting systematically?',
        '''<ol>
          <li>Check the grain: COUNT(*) vs COUNT(DISTINCT order_id) on the fact.</li>
          <li>Check versions: are refunds and cancellations excluded by the latest status?</li>
          <li>Check joins: a non-unique dimension key (e.g. SCD2 joined without a date condition) multiplies rows.</li>
          <li>Reconcile one day and one city row by row with finance.</li>
        </ol>''', 'Blaming the source without measuring.') +
    scn('Logistics · design', 'Mid-level', 'Late events',
        'Rider events arrive up to two days after the delivery. How do you keep daily KPIs correct?',
        'do you understand load date versus event date?',
        '''<ul>
          <li>Partition by event date; keep load date as a column.</li>
          <li>Each load computes the set of event dates it touched and rebuilds only those gold partitions.</li>
          <li>Publish a “closed” flag after N days so users know when a day stops changing.</li>
        </ul>''', 'Building gold only from today’s file.') +
    scn('Banking · modelling', 'Senior', 'Customer segment history',
        'Reports must show revenue by the customer segment valid at the time of each transaction, for 7 years.',
        'can you justify SCD type 2 and its cost?',
        '''<ul>
          <li>SCD2 dim with valid_from, valid_to, is_current; point-in-time join on the transaction time.</li>
          <li>Measure change rate first (here 469 of 3,664 customers in a month) to size the table.</li>
          <li>If only “current” and “previous” matter, type 3 is cheaper; if one attribute changes very often, split it (type 4).</li>
        </ul>''', 'Overwriting the segment and reporting history with today’s value.')
)
