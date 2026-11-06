import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='13-capstone', lesson='01-problem-and-dataset', n='13.1',
    module_label='Module 13 · Capstone',
    title='The problem and the dataset',
    desc='Capstone part 1: TiffinGo asks for a daily revenue and churn-feature pipeline. Plan a medallion (landing, silver, gold, quarantine) design, then profile 842,587 raw orders, 20,100 customers and 800 restaurants with PySpark: duplicates, bad and negative amounts, orphan keys, invalid phones and a 30% skewed restaurant, and turn every finding into a cleaning rule.',
    og_desc='Plan a medallion pipeline and profile 842,587 messy orders with PySpark before writing a single transform.',
    minutes=26, level='Advanced',
    lead='Capstone time. TiffinGo wants <b>daily city revenue</b> and <b>churn features</b>. Before writing transforms, you <b>design the layers</b> and <b>profile the raw data</b>: duplicates, bad amounts, orphans, skew. Every finding becomes a rule. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['842,587 raw orders', 'Medallion design', 'Data profiling', 'Runs in your browser (Python)'],
)

MAIN = '''# Profile a tiny sample of raw orders, the way the capstone does
raw = [
    ("o1", "c1", "1", "250", "DELIVERED"),
    ("o2", "c2", "1", "12O", "DELIVERED"),
    ("o2", "c2", "1", "12O", "DELIVERED"),
    ("o3", "c9", "7", "-300", "CANCELLED"),
    ("o4", "c3", "1", "N/A", "PLACED"),
    ("o5", "c1", "4", "480", "DELIVERED"),
]
customers = {"c1", "c2", "c3"}

def to_num(s):
    try:
        return float(s)
    except ValueError:
        return None

ids = [r[0] for r in raw]
print("rows:", len(raw), "duplicate ids:", len(ids) - len(set(ids)))
print("not a number:", sum(to_num(r[3]) is None for r in raw))
print("negative:", sum((to_num(r[3]) or 0) < 0 for r in raw))
print("orphans:", sum(r[1] not in customers for r in raw))
top = max(set(r[2] for r in raw), key=lambda k: sum(r[2] == k for r in raw))
print("top restaurant share:", round(100 * sum(r[2] == top for r in raw) / len(raw)), "%")
'''
RUN = dict(
    heading='Run the code: profile raw orders',
    intro='<p>The capstone profile, on six rows. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('print("rows:", len(raw), "duplicate ids:", len(ids) - len(set(ids)))', 'Duplicates: same order_id twice (the lab found 2,587).'),
        ('print("orphans:", sum(r[1] not in customers for r in raw))', 'Orphans: customer_id not in the customers table.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then add a row with amount "abc".', code=None),
        dict(label='2 · Predict first: quarantine %', hint='<b>Predict first:</b> 4,944 bad rows of 842,587?',
             code='''print(round(100 * 4944 / 842587, 2), "%")
'''),
        dict(label='3 · Phone check', hint='Valid = 10 digits.',
             code='''phones = ["9820012345", "98200", "N/A", "9822254321"]
print([p for p in phones if not (p.isdigit() and len(p) == 10)])
'''),
        dict(label='4 · Orders per day', hint='842,587 orders over 14 days.',
             code='''print(842587 // 14)
'''),
        dict(label='5 · Spot the error', hint='A plain cast under ANSI.', expect='error',
             code='''amount = "12O"
print(int(amount))
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: profile the landing zone',
    intro='<p>Generate the data with <code>jobs/m13/generate.py</code>, then profile in <code>pyspark</code>. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Row counts', cmd='spark.read.option("header", True).csv("data/m13/landing/orders").count()', file='pyspark',
             output='842587', note='14 CSV files, all strings.'),
        dict(title='2 · Duplicate ids', cmd='o.count() - o.select("order_id").distinct().count()', file='pyspark',
             output='2587', note='dropDuplicates later.'),
        dict(title='3 · Bad amounts', cmd='o.filter(F.col("amount").try_cast("double").isNull()).count()', file='pyspark',
             output='3279', note='NULL, "12O", "N/A".'),
        dict(title='4 · Skew', cmd='o.groupBy("rest_id").count().orderBy(F.desc("count")).first()', file='pyspark',
             output="Row(rest_id='1', count=253012)", note='30% of all orders.'),
    ],
)

TRACE = dict(
    heading='One finding becomes one rule',
    intro='<p>The profile decides the cleaning code.</p>',
    code='''findings = {"duplicates": 2587, "bad_amount": 3279, "negative": 1665}
rules = {"duplicates": "dropDuplicates(order_id)",
         "bad_amount": "try_cast -> quarantine",
         "negative": "amount < 0 -> quarantine"}
for k, v in findings.items():
    print(k, v, "=>", rules[k])
''',
    notes={1: 'Measure :: Counts come from the profile.', 5: 'Rule :: Each finding maps to code in 13.2.'},
)

WORKED_INTRO = 'Three planning decisions for the TiffinGo capstone.'
EXAMPLES = [
    dict(level='b', tag='Capstone · layers', title='Choose the layers',
         problem='<p>Raw CSV and JSON land daily; analysts and ML need clean tables.</p>',
         inp='landing files',
         approach=['Landing: as-is, never edited.', 'Silver: typed, deduplicated, partitioned.', 'Gold: business aggregates; quarantine for bad rows.'],
         code='''for layer, what in [("landing", "raw files"), ("silver", "clean orders/customers"),
                    ("gold", "daily_city_revenue, customer_features"), ("quarantine", "bad rows + reason")]:
    print(f"{layer:10} {what}")
''', notes={1: 'Medallion :: Each layer has one job.'},
         tryit='Step 1.'),
    dict(level='i', tag='Capstone · orphans', title='Decide on orphan customers',
         problem='<p>20,639 orders reference unknown customers.</p>',
         inp='orders, customers',
         approach=['Do not drop: revenue is still real.', 'Keep in silver; left join for features.', 'Report the count every run.'],
         code='''orphans, total = 20639, 842587
print("keep, flag:", round(100 * orphans / total, 2), "% of orders")
''', notes={1: 'Business rule :: Ask before deleting data.'},
         tryit='Step 3.'),
    dict(level='a', tag='Capstone · skew', title='Plan for the 30% restaurant',
         problem='<p>Cloud Kitchen Co has 253,012 orders.</p>',
         inp='rest_id counts',
         approach=['Restaurants is small (800 rows): broadcast it.', 'Keep AQE skew handling on.', 'Partition by order_date, not rest_id.'],
         code='''print("broadcast restaurants:", 800, "rows")
print("partitionBy order_date: 14 days")
''', notes={1: 'Avoid :: A shuffle join on a skewed key.'},
         tryit='Step 4.'),
]

QUIZ = mix([
    dict(q='Beginner: The landing layer should…', options=['Be cleaned in place', 'Keep raw files unchanged', 'Hold aggregates', 'Be deleted daily'], answer=1,
         why='You can always replay from it.'),
    dict(q='Beginner: Silver holds…', options=['Raw CSV', 'Clean, typed, deduplicated data', 'Dashboards', 'Logs'], answer=1,
         why='Gold builds on it.'),
    dict(q='Beginner: Why profile before coding?', options=['It is faster', 'Findings decide the cleaning rules', 'Spark needs it', 'No reason'], answer=1,
         why='Measure, then code.'),
    dict(q='Intermediate: Duplicate order_id rows found?', options=['0', '100', '2,587', '20,639'], answer=2,
         why='100 is customers; 20,639 is orphans.'),
    dict(q='Intermediate: Plain CAST of "12O" under ANSI…', options=['Returns NULL', 'Raises CAST_INVALID_INPUT', 'Returns 12', 'Returns 0'], answer=1,
         why='Use try_cast and quarantine.'),
    dict(q='Intermediate: Rows with a bad or negative amount go to…', options=['Gold', 'Quarantine with a reason', '/dev/null', 'Landing'], answer=1,
         why='Never silently drop.'),
    dict(q='Advanced: Restaurant 1 has 30% of orders. Best join?', options=['Sort-merge on rest_id', 'Broadcast the 800-row table', 'Cross join', 'Collect to driver'], answer=1,
         why='Skew does not matter if nothing shuffles.'),
    dict(q='Advanced: Partition silver orders by…', options=['order_id', 'rest_id', 'order_date', 'amount'], answer=2,
         why='Low cardinality; matches daily queries.'),
])

REVISION = [
    'Goal: gold daily_city_revenue and customer_features from messy landing data.',
    'Layers: landing (raw) → silver (clean) → gold (aggregates) + quarantine.',
    'Profile: 842,587 orders, 2,587 duplicate ids, 3,279 bad and 1,665 negative amounts.',
    'Customers 20,100 (100 duplicates), 194 invalid phones; 20,639 orphan orders.',
    'Skew: restaurant 1 = 30% of orders → broadcast the 800-row restaurants table.',
    'Every finding → rule: dropDuplicates, try_cast + quarantine, latest row per customer.',
]
FAQ = [
    ('Why not clean the landing files directly?', 'Landing is your replay source; if a rule is wrong you rebuild silver from the untouched files.'),
    ('Is medallion the only design?', 'No, but landing/silver/gold is the common name on Databricks and lakehouse teams, and interviewers expect it.'),
    ('How big should a capstone dataset be?', 'Large enough to show partitioning and joins (here 842,587 rows), small enough to run on a laptop in under a minute.'),
    ('Can I use my own data?', 'Yes: replace generate.py with your files, run the profile first and write down your own findings.'),
]

PRACTICE_INTRO = 'Profiling programs for the capstone.'
PROBLEMS = [
    dict(level='easy', title='Duplicate count', stmt='Count duplicate ids.', inp='ids',
         code='''ids = ["o1", "o2", "o2", "o3", "o3", "o3"]
print(len(ids) - len(set(ids)))
''', explain='3.'),
    dict(level='easy', title='Null share', stmt='Percent of None amounts.', inp='list',
         code='''a = [250, None, 480, None]
print(100 * a.count(None) / len(a), "%")
''', explain='50%.'),
    dict(level='easy', title='Min and max', stmt='Range of numeric amounts.', inp='strings',
         code='''a = ["250", "-1500", "1500", "N/A"]
n = [float(x) for x in a if x.lstrip("-").isdigit()]
print(min(n), max(n))
''', explain='-1500 1500, matching the lab.'),
    dict(level='medium', title='Orphans', stmt='Orders with unknown customers.', inp='two lists',
         code='''orders = ["c1", "c2", "c9", "c8"]
known = {"c1", "c2"}
print([c for c in orders if c not in known])
''', explain='Set membership = anti join.'),
    dict(level='medium', title='Status counts', stmt='Group by status.', inp='list',
         code='''from collections import Counter
print(Counter(["DELIVERED", "DELIVERED", "CANCELLED", "PLACED"]))
''', explain='Like groupBy().count().'),
    dict(level='medium', title='Top share', stmt='Share of the busiest key.', inp='counts',
         code='''c = {"1": 253012, "792": 810}
print(round(100 * c["1"] / 842587, 1), "%")
''', explain='30.0%.'),
    dict(level='business', title='Revenue at risk', stmt='Negative-amount rows × average 400.', inp='1,665',
         code='''print(1665 * 400)
''', explain='Why bad rows need a report, not deletion.'),
    dict(level='business', title='Daily volume', stmt='Orders per day across 14 days.', inp='842,587',
         code='''print(round(842587 / 14))
''', explain='About 60,000 orders a day.'),
]

SCN_INTRO = 'Capstone interviews start with “how did you understand the data?”'
SCENARIOS = (
    scn('Any company · data', 'Fresher', '“Walk me through your project.”',
        'Start the capstone story.',
        'opening?',
        '<p>Problem first (daily revenue and churn features for a food-delivery app), then data (842k orders, customers, restaurants), then what I found while profiling (duplicates, bad amounts, orphans, skew), then the design (landing, silver, gold, quarantine).</p>', 'Starting with the tools list.') +
    scn('Data engineering', 'Mid-level', 'Unknown data',
        'You get a new 50 GB feed. What do you do first?',
        'first steps?',
        '''<ol>
          <li>Read as strings; count rows and files.</li>
          <li>Duplicates, nulls, casts with try_cast, ranges, orphans.</li>
          <li>Key distribution for skew; write findings as rules.</li>
        </ol>''', 'Casting with inferSchema and hoping.') +
    scn('Data engineering', 'Mid-level', 'Orphan rows',
        '2% of orders have no matching customer.',
        'decision?',
        '''<ul>
          <li>Keep them; revenue is real.</li>
          <li>Flag and report counts; ask the source team.</li>
          <li>Use left joins so they are not lost.</li>
        </ul>''', 'Inner join that silently drops them.') +
    scn('Analytics platform', 'Senior', 'Skewed key',
        'One merchant has 30% of all transactions.',
        'design?',
        '''<ul>
          <li>Broadcast the small dimension.</li>
          <li>AQE skew join for large–large joins; salting as a last resort.</li>
          <li>Never partition files by the skewed key.</li>
        </ul>''', 'repartition(merchant_id).')
)
