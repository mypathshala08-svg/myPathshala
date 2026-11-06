import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='13-capstone', lesson='02-build-the-pipeline', n='13.2',
    module_label='Module 13 · Capstone',
    title='Build the pipeline',
    desc='Capstone part 2: build the TiffinGo pipeline the production way. Pure, unit-tested PySpark transforms (clean_orders with try_cast and a quarantine reason, latest-row customers, broadcast-join daily city revenue, churn features), a pipeline script writing partitioned silver Parquet, quality gates that fail the run, JSON run metrics, and the same job submitted to a standalone cluster with --py-files.',
    og_desc='Pure transforms, 5 unit tests, quality gates and spark-submit: the capstone pipeline with real outputs.',
    minutes=30, level='Advanced',
    lead='Turn the profiling rules into a <b>production pipeline</b>: pure transforms, <b>unit tests</b>, partitioned <b>silver</b>, a <b>quarantine</b>, <b>quality gates</b> and two <b>gold</b> tables, then submit the same code to a cluster. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['835,067 silver rows', '5 tests passed', 'Quality gates', 'Runs in your browser (Python)'],
)

MAIN = '''# The capstone pipeline in miniature: clean, quarantine, dedup, gate, gold
raw = [
    ("1", "Mumbai", "250", "delivered"), ("2", "Pune", "N/A", "DELIVERED"),
    ("3", "Mumbai", "-90", "DELIVERED"), ("1", "Mumbai", "250", "DELIVERED"),
    ("4", "Pune", "400", "CANCELLED"), ("5", "Pune", "300", "DELIVERED"),
]

def to_int(s):
    try:
        return int(s)
    except ValueError:
        return None

valid, quarantine, seen = [], [], set()
for oid, city, amt, status in raw:
    a = to_int(amt)
    problem = "bad_amount" if a is None else ("negative_amount" if a < 0 else None)
    if problem:
        quarantine.append((oid, amt, problem))
    elif oid not in seen:                      # dedup only valid rows
        seen.add(oid)
        valid.append((oid, city, a, status.strip().upper()))

pct = 100 * len(quarantine) / len(raw)
print("silver:", len(valid), "quarantine:", quarantine)
assert pct < 50, "too many bad rows: stop and alert"

gold = {}
for _, city, a, status in valid:
    if status == "DELIVERED":
        gold[city] = gold.get(city, 0) + a
print("daily_city_revenue:", gold)
'''
RUN = dict(
    heading='Run the code: the pipeline in miniature',
    intro='<p>Every stage of the capstone on six rows. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    elif oid not in seen:                      # dedup only valid rows', 'Validate first, then deduplicate, so a bad copy never wins.'),
        ('assert pct < 50, "too many bad rows: stop and alert"', 'The quality gate: the real pipeline uses 2%.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then change the gate to 2 and run again.', code=None),
        dict(label='2 · Predict first: reconcile', hint='<b>Predict first:</b> raw − silver − quarantine = ?',
             code='''print(842587 - 835067 - 4944)
'''),
        dict(label='3 · A unit test', hint='Pin one behaviour.',
             code='''def clean_status(s):
    return s.strip().upper()
assert clean_status(" delivered ") == "DELIVERED"
print("test passed")
'''),
        dict(label='4 · Features', hint='Days since last order, 99 if none.',
             code='''last = {7: 13}
for c in (7, 9):
    print(c, last.get(c, 99))
'''),
        dict(label='5 · Spot the error', hint='The bad-day gate.', expect='error',
             code='''quarantine_pct = 5.34
assert quarantine_pct < 2.0, "too many bad rows: stop and alert"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: test and run the pipeline',
    intro='<p>From the lab folder <code>jobs/m13</code>. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Tests', cmd='pytest -q tiffingo/tests', file='terminal',
             output='.....  [100%]\n5 passed in 16.14s', note='Run before every change.'),
        dict(title='2 · Pipeline', cmd='python tiffingo/pipeline.py data/m13', file='terminal',
             output='"silver_rows": 835067, "quarantined": 4944, "quarantine_pct": 0.59, "total_seconds": 25.2', note='JSON run metrics.'),
        dict(title='3 · Cluster', cmd='spark-submit --master spark://spark-master:7077 --py-files transforms.zip tiffingo/pipeline.py /data/m13', file='terminal',
             output='"silver_rows": 835067, ... "total_seconds": 38.3', note='Same numbers.'),
    ],
)

TRACE = dict(
    heading='The first failing rule wins',
    intro='<p>How the <code>problem</code> column is decided.</p>',
    code='''def problem(order_id, ts, amount):
    if order_id is None: return "bad_order_id"
    if ts is None: return "bad_timestamp"
    if amount is None: return "bad_amount"
    if amount < 0: return "negative_amount"
    return None
print(problem(4, None, 100), problem(3, "t", -90), problem(1, "t", 250))
''',
    notes={1: 'Order :: Mirrors F.when(...).when(...).', 6: 'None :: Valid rows have no problem.'},
)

WORKED_INTRO = 'Three engineering decisions inside the pipeline.'
EXAMPLES = [
    dict(level='b', tag='Capstone · structure', title='Split transforms from I/O',
         problem='<p>One 300-line notebook cell does everything.</p>',
         inp='notebook',
         approach=['Move logic into functions returning DataFrames.', 'Keep read/write in pipeline.py.', 'Test functions on tiny data.'],
         code='''layout = ["transforms.py  (pure)", "pipeline.py    (I/O, gates)", "tests/         (pytest)"]
print("\\n".join(layout))
''', notes={1: 'Testable :: No files needed in tests.'},
         tryit='Step 2.'),
    dict(level='i', tag='Capstone · files', title='One file per day',
         problem='<p><code>partitionBy("order_date")</code> wrote 56 files for 14 days.</p>',
         inp='4 input partitions',
         approach=['Each task writes one file per date it holds.', 'repartition("order_date") first.', 'Now 14 files.'],
         code='''tasks, days = 4, 14
print("without:", tasks * days, "files; with repartition:", days)
''', notes={1: 'Small files :: Lesson 5.3.'},
         tryit='Step 3.'),
    dict(level='a', tag='Capstone · gates', title='Choose gate thresholds',
         problem='<p>How strict should the quarantine gate be?</p>',
         inp='history',
         approach=['Look at normal runs (0.59%).', 'Set a margin above (2%).', 'Hard asserts for invariants (unique ids).'],
         code='''normal, gate = 0.59, 2.0
for pct in (0.59, 1.4, 5.34):
    print(pct, "ok" if pct < gate else "STOP")
''', notes={1: 'Data-driven :: Thresholds come from history.'},
         tryit='Types table.'),
]

QUIZ = mix([
    dict(q='Beginner: A pure transform…', options=['Reads files', 'Takes and returns DataFrames, no I/O', 'Writes to S3', 'Prints only'], answer=1,
         why='That makes it testable.'),
    dict(q='Beginner: Bad rows in the capstone go to…', options=['Gold', 'Quarantine with a problem', 'Are dropped', 'Become 0'], answer=1,
         why='4,944 rows kept aside.'),
    dict(q='Beginner: How many tests passed?', options=['3', '5', '14', '84'], answer=1,
         why='5 passed in 16.14 s.'),
    dict(q='Intermediate: Why dedup after validation?', options=['Faster', 'So a bad copy cannot win over a good one', 'Spark requires it', 'No reason'], answer=1,
         why='11 bad copies went to quarantine.'),
    dict(q='Intermediate: Why repartition("order_date") before partitionBy?', options=['More files', 'One file per day', 'Sorting', 'Compression'], answer=1,
         why='56 → 14 files.'),
    dict(q='Intermediate: Gold daily_city_revenue has 84 rows because…', options=['84 restaurants', '6 cities × 14 days', 'Random', '84 tests'], answer=1,
         why='Grain = city per day.'),
    dict(q='Advanced: Gates should run…', options=['After gold', 'Before gold is written', 'Weekly', 'Only in tests'], answer=1,
         why='Never publish bad numbers.'),
    dict(q='Advanced: --py-files transforms.zip is needed because…', options=['Executors must import transforms', 'It is faster', 'It compresses data', 'YARN only'], answer=0,
         why='Code ships with the job.'),
])

REVISION = [
    'Layout: transforms.py (pure) + pipeline.py (I/O, gates, metrics) + tests/.',
    'clean_orders: try_cast, problem column, quarantine, dedup valid rows, order_date.',
    '842,587 raw = 835,067 silver + 4,944 quarantine + 2,576 duplicates.',
    'Gates: no NULL amounts, unique ids, quarantine_pct < 2% (lab 0.59%).',
    'repartition(order_date) → 14 files; gold: 84 city-day rows, 20,000 customers.',
    '5 tests passed; cluster run with --py-files gives identical numbers (38.3 s).',
]
FAQ = [
    ('Should I use a data-quality library instead of asserts?', 'For larger teams yes: tools like Great Expectations, Soda or Delta/DLT expectations give reports and history. Plain asserts are the same idea and fine for a capstone.'),
    ('Why print metrics as JSON?', 'Schedulers and log systems can parse it, so you can chart row counts and durations over time and alert on changes.'),
    ('Why not write gold with Delta Lake?', 'You can (Lesson 11.5): Delta adds ACID writes and time travel. Parquet keeps the capstone runnable without extra packages.'),
    ('How do I schedule it?', 'Airflow, Databricks Jobs or a cron/k8s CronJob calling spark-submit; the job must fail loudly so retries and alerts work.'),
]

PRACTICE_INTRO = 'Pipeline programs.'
PROBLEMS = [
    dict(level='easy', title='Quarantine %', stmt='Share of bad rows.', inp='4,944 / 842,587',
         code='''print(round(4944 / 842587 * 100, 2))
''', explain='0.59.'),
    dict(level='easy', title='Normalise status', stmt='Trim and upper-case.', inp='" delivered "',
         code='''print(" delivered ".strip().upper())
''', explain='Like F.upper(F.trim()).'),
    dict(level='easy', title='Grain', stmt='Rows in a city-day table.', inp='6 cities, 14 days',
         code='''print(6 * 14)
''', explain='84.'),
    dict(level='medium', title='Latest row wins', stmt='Keep newest signup per customer.', inp='rows',
         code='''rows = [(5, "Free", "2025-01-01"), (5, "Gold", "2025-06-01")]
latest = {}
for cid, plan, d in sorted(rows, key=lambda r: r[2]):
    latest[cid] = plan
print(latest)
''', explain='Window row_number in Spark.'),
    dict(level='medium', title='Revenue per city', stmt='Delivered only.', inp='orders',
         code='''o = [("Mumbai", 200, "DELIVERED"), ("Mumbai", 300, "DELIVERED"), ("Mumbai", 999, "CANCELLED")]
print(sum(a for c, a, s in o if s == "DELIVERED"))
''', explain='500, matching the unit test.'),
    dict(level='medium', title='Days since last', stmt='as_of minus last order.', inp='dates',
         code='''import datetime as dt
print((dt.date(2026, 11, 2) - dt.date(2026, 10, 20)).days)
''', explain='13, as in the test.'),
    dict(level='business', title='Bad day', stmt='Does 3,000 extra bad rows on a 60,000-row day pass?', inp='gate 2%',
         code='''print(3000 / 60000 * 100 < 2)
''', explain='No: stop and alert.'),
    dict(level='business', title='Files saved', stmt='Files per year with and without repartition.', inp='4 tasks',
         code='''print(365 * 4, "vs", 365)
''', explain='Fewer small files.'),
]

SCN_INTRO = 'Pipeline-building questions test engineering habits.'
SCENARIOS = (
    scn('Any company · data', 'Fresher', '“How did you test your project?”',
        'Explain the tests.',
        'answer?',
        '<p>I kept transforms pure and wrote pytest tests with a shared SparkSession: quarantine reasons, deduplication, latest customer row, delivered-only revenue with assertDataFrameEqual, and features for customers without orders. 5 tests run in about 16 seconds.</p>', '“I checked the output manually.”') +
    scn('Data engineering', 'Mid-level', 'Bad records',
        'How do you handle rows that fail validation?',
        'approach?',
        '''<ul>
          <li>try_cast, never plain CAST on raw text.</li>
          <li>Quarantine table with the original value and a reason.</li>
          <li>Gate on the bad-row share; report upstream.</li>
        </ul>''', 'Filtering them out silently.') +
    scn('Data engineering', 'Mid-level', 'Re-runs',
        'A day must be reprocessed. How do you avoid duplicates?',
        'design?',
        '''<ul>
          <li>Overwrite the day’s partition (dynamic overwrite).</li>
          <li>Deduplicate on the business key.</li>
          <li>Deterministic logic; compare metrics to the previous run.</li>
        </ul>''', 'Append mode.') +
    scn('Platform', 'Senior', 'Packaging',
        'How do you ship this job to a cluster?',
        'answer?',
        '''<ul>
          <li>Module zipped and passed with --py-files (or a wheel/venv, Lesson 11.2).</li>
          <li>Config via arguments, not hard-coded paths.</li>
          <li>Event log on; scheduler handles retries and alerts.</li>
        </ul>''', 'Copying the notebook to the server.')
)
