import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
def sec(c, a, b=None, drop=()):
    return capsec(c, a, b, drop)
LOC, CL, GC, TS = 'l132_pipeline_local.txt', 'l132_pipeline_cluster.txt', 'l132_gold.txt', 'l132_tests.txt'

def flowrow(x, y, hi=None):
    items = [('read', 'schema'), ('clean', 'try_cast'), ('dedup', 'order_id'), ('write', 'partition'), ('gates', 'assert'), ('gold', 'aggregate')]
    o = ''
    for k, (n, d) in enumerate(items):
        o += opbox(x + k * 56, y, n, d, 'acc' if hi == k else 'card', 50, 34)
        if k:
            o += arrow(x + k * 56 - 6, y + 17, x + k * 56, y + 17, 'ink3', 1)
    return o

sc_ = (flowrow(10, 40) +
       box(370, 12, 262, 132, 'card') + t(500, 30, 'One run (local[4], 25.2 s)', 8.6, bold=True) +
       ''.join(t(382, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('raw rows        : 842,587', 'ink'), ('silver rows     : 835,067', 'green'),
           ('quarantined     : 4,944', 'red'), ('dups removed    : 2,576', 'amber'),
           ('gold city rows  : 84', 'green'), ('tests           : 5 passed', 'green')])))
scene_svg = scene('The capstone pipeline: read the landing files with a schema, clean with try_cast, quarantine bad rows, deduplicate, write partitioned silver Parquet, run quality gates, then build two gold tables. Unit tests cover every transform and the same code runs with spark-submit on a cluster.', sc_,
                  'Pure transforms, <tspan font-weight="700" class="s-acc">tested</tspan>, then submitted.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>From notebook to a real job</h2>
  <div class="story">
    <p class="narration">Profiling is done (Lesson 13.1). Now Kiran has to turn the rules into a pipeline that runs every night without anyone watching. Her first attempt is one long notebook cell.</p>

{scene_svg}

K> Sir, it works in my notebook. Can we schedule it?
A> A notebook is a draft. Production code has <b>pure transform functions</b> in a module, <b>unit tests</b> for each one, a thin <b>pipeline script</b> that does the reading and writing, and <b>quality gates</b> that stop the run when data is wrong.
R> Why separate transforms from reading and writing?
A> Because a function that takes a DataFrame and returns a DataFrame can be tested on four hand-made rows in seconds. The pipeline script then just wires them together, and spark-submit ships the module to the cluster. All outputs below are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> The pipeline at three levels
L1> A kitchen line
      <ul>
        <li>Each station does one job (wash, cut, cook, plate) and can be checked on its own: those are the transforms and their tests.</li>
        <li>The head chef checks every plate before it leaves; a bad batch stops service: that is the quality gate.</li>
      </ul>
L2> The code layout
      <ul>
        <li><code>tiffingo/transforms.py</code>: <code>clean_orders</code>, <code>clean_customers</code>, <code>daily_city_revenue</code>, <code>customer_features</code>. No I/O.</li>
        <li><code>tiffingo/pipeline.py</code>: reads landing, calls transforms, writes silver/quarantine/gold, runs gates, prints metrics as JSON.</li>
        <li><code>tiffingo/tests/</code>: pytest with a shared <code>spark</code> fixture (Lesson 11.4).</li>
      </ul>
L3> Engineering choices
      <ul>
        <li>An explicit DDL schema reads every column as string; <code>try_cast</code> converts, and a single <code>problem</code> column records the first failed rule.</li>
        <li>Validation happens before <code>dropDuplicates</code>, so a bad copy never “wins” over a good one; <code>repartition("order_date")</code> before <code>partitionBy</code> gives one file per day.</li>
        <li>Gates: zero NULL amounts, unique order ids, quarantine share under 2%; otherwise <code>assert</code> fails the job and the scheduler alerts.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>A production batch pipeline</h2>
''' + def_block(
    'A production Spark batch job separates <b>pure transformations</b> (functions from DataFrames to DataFrames, free of I/O) from an <b>orchestration script</b> that reads sources with explicit schemas, applies the transformations, writes outputs idempotently (overwrite of the run’s partitions), and evaluates <b>data-quality gates</b> whose failure aborts the run. Transformations are covered by <b>unit tests</b> on small in-memory DataFrames; the job is packaged (e.g. a zip passed with <code>--py-files</code>) and launched with <code>spark-submit</code> on a cluster manager, emitting <b>run metrics</b> for monitoring.',
    'Write the cleaning and business logic as small functions you can test on a few rows, keep reading and writing in one short script, check the results before publishing them, and run the same code on a cluster with spark-submit.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Pure transform', 'DataFrame in, DataFrame out, no I/O.'),
    ('Fixture', 'Shared SparkSession for tests.'),
    ('Idempotent', 'Re-running gives the same result.'),
    ('Quality gate', 'Check that fails the run.'),
    ('Run metrics', 'Counts and timings per run.'),
    ('--py-files', 'Ships your Python modules.'),
    ('problem column', 'Why a row was quarantined.'),
    ('as_of', 'Reference date for features.'),
]) + '''

  <h3>The outputs</h3>
''' + table(['Table', 'Grain (one row =)', 'Rows (lab)', 'Built by'], [
    ['silver/orders', 'one valid order', '835,067 in 14 date partitions', '<code>clean_orders</code>'],
    ['quarantine/orders', 'one rejected row + problem', '4,944', '<code>clean_orders</code>'],
    ['silver/customers', 'one customer (latest row)', '20,000', '<code>clean_customers</code>'],
    ['gold/daily_city_revenue', 'one city per day', '84 (6 cities × 14 days)', '<code>daily_city_revenue</code>'],
    ['gold/customer_features', 'one customer', '20,000', '<code>customer_features</code>'],
], minw=620) + lv + '''
EXAM> “How do you make a Spark job production-ready?” Put logic in pure, unit-tested functions; read with explicit schemas; handle bad records explicitly (quarantine, not silent drops); make writes idempotent; add data-quality gates that fail the job; emit metrics; package dependencies and run with spark-submit under a scheduler with retries and alerts.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Where each check lives</h2>
''' + table(['Check', 'Where', 'What happens on failure'], [
    ['A transform is wrong', 'Unit test (pytest, CI)', 'Merge blocked; never reaches production'],
    ['One row is bad', '<code>problem</code> column → quarantine', 'Row kept aside with reason; run continues'],
    ['Too many rows are bad', 'Gate: quarantine_pct &lt; 2%', 'Job fails; scheduler alerts; gold not overwritten'],
    ['Output broken (NULLs, dup ids)', 'Gate: assert on silver', 'Job fails before gold'],
    ['Job slow or skewed', 'Run metrics, Spark UI, event log', 'Investigate (Lesson 13.3)'],
], minw=620) + '''
WARN> Gates must run <b>before</b> gold is written, otherwise dashboards read yesterday’s bad data as truth. And never catch the gate’s exception just to “keep the job green”: a failed run that alerts is far cheaper than a wrong revenue number in a board meeting.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Building the pipeline</h2>
  <p>All outputs are real: PySpark 4.3.0, <code>local[4]</code> and a standalone cluster (Lesson 11.1). Full code is in the lab folder <code>jobs/m13/tiffingo/</code>.</p>
''' + stepper([
    ('Step 1 · Silver: clean and quarantine',
     code('python', 'tiffingo/transforms.py', 'def clean_orders(raw):\n    typed = raw.select(F.col("order_id").try_cast("long").alias("order_id"), ...,\n                       F.col("amount").try_cast("int").alias("amount"),\n                       F.upper(F.trim("status")).alias("status"), F.col("amount").alias("amount_raw"))\n    problem = (F.when(F.col("order_id").isNull(), "bad_order_id")\n                .when(F.col("order_ts").isNull(), "bad_timestamp")\n                .when(F.col("amount").isNull(), "bad_amount")\n                .when(F.col("amount") < 0, "negative_amount"))\n    typed = typed.withColumn("problem", problem)\n    quarantine = typed.filter(F.col("problem").isNotNull())\n    valid = (typed.filter(F.col("problem").isNull()).dropDuplicates(["order_id"])\n             .withColumn("order_date", F.to_date("order_ts")).drop("problem", "amount_raw"))\n    return valid, quarantine', sec(GC, '== quarantine sample')),
     'One function returns two DataFrames. <code>try_cast</code> never throws; the first failing rule fills <code>problem</code>, and the original text is kept in <code>amount_raw</code> so the source team can see exactly what arrived. Deduplication runs only on valid rows.'),
    ('Step 2 · Unit tests',
     code('python', 'tests/test_transforms.py', 'def test_bad_rows_go_to_quarantine(spark):\n    df = raw(spark, [("1", "7", "1", "2026-10-20 10:00:00", "250", "delivered"),\n                     ("2", "7", "1", "2026-10-20 11:00:00", "N/A", "DELIVERED"),\n                     ("3", "7", "1", "2026-10-20 12:00:00", "-90", "DELIVERED"),\n                     ("4", "7", "1", "not a time", "100", "DELIVERED")])\n    valid, quar = clean_orders(df)\n    assert [r.order_id for r in valid.collect()] == [1]\n    assert sorted((r.order_id, r.problem) for r in quar.collect()) == \\\n        [(2, "bad_amount"), (3, "negative_amount"), (4, "bad_timestamp")]\n# + duplicates, latest customer, delivered-only revenue (assertDataFrameEqual), no-order features\n$ pytest -q tiffingo/tests', sec(TS, '.....')),
     'Five tests, one per behaviour, each on a handful of rows. <code>assertDataFrameEqual</code> (Lesson 11.4) compares the gold output to an expected DataFrame. These run in CI on every change.'),
    ('Step 3 · Run the pipeline',
     code('bash', 'terminal', 'python tiffingo/pipeline.py data/m13\n# silver: valid.repartition("order_date").write.partitionBy("order_date").parquet(...)\n# gates : assert silver_null_amounts == 0 and silver_unique_order_ids\n#         assert quarantine_pct < 2.0, "too many bad rows: stop and alert"', sec(LOC, '{')),
     '842,587 raw = 835,067 silver + 4,944 quarantined + 2,576 duplicates. (Profiling found 2,587 duplicate rows; 11 of those copies were bad and went to quarantine instead.) Both gates pass at 0.59%. Silver takes most of the 25 s because it reads and shuffles all raw rows once.'),
    ('Step 4 · The gold tables',
     code('python', 'pyspark', 'spark.read.parquet("data/m13/gold/daily_city_revenue").orderBy("order_date", "city").show(6)\nspark.read.parquet("data/m13/gold/customer_features").orderBy("customer_id").show(4)', sec(GC, '== gold.daily', '== quarantine')),
     'Mumbai’s revenue is about 3.5× other cities because Cloud Kitchen Co is there: the broadcast join made that skew harmless. <code>customer_features</code> has one row per customer; customers with no recent orders get 0 orders and 99 days since last order, ready for the churn model from Module 10.'),
    ('Step 5 · Submit to the cluster',
     code('bash', 'terminal', 'cd jobs/m13 && zip -r transforms.zip -j tiffingo/transforms.py\nspark-submit --master spark://spark-master:7077 \\\n  --py-files /jobs/m13/transforms.zip --conf spark.eventLog.enabled=true \\\n  /jobs/m13/tiffingo/pipeline.py /data/m13', sec(CL, '"silver_rows"')),
     'The same script, unchanged, on the standalone cluster. The numbers are identical (that is the point of idempotent, deterministic logic); the run took 38.3 s because the small lab cluster has fewer cores than <code>local[4]</code> and writes through Docker volumes. The event log feeds the History Server for the review in 13.3.'),
]) + '''
</section>
'''

see = [
    term([('valid, quarantine = clean_orders(raw)', W), ('720082  N/A   bad_amount', RD), ('720477  -93   negative_amount', RD)], size=7.2),
    term([('$ pytest -q tiffingo/tests', W), ('.....   [100%]', G), ('5 passed in 16.14s', G)], size=7.4),
    term([('silver_rows: 835067', G), ('quarantined: 4944 (0.59%)', Y), ('duplicates_removed: 2576', Y)], size=7.2),
    term([('2026-10-20 Mumbai  21494  16848561', W), ('2026-10-20 Pune     6062   4794755', W), ('gold_customers: 20000', G)], size=7.0),
]
B1 = [
    t(180, 14, 'Two outputs from one function', 9.4, bold=True) + opbox(20, 50, 'raw', 'strings', 'card', 80, 34) + arrow(100, 67, 140, 50, 'ink3', 1) + arrow(100, 67, 140, 90, 'red', 1) + opbox(140, 32, 'valid', 'typed, dedup', 'green', 90, 34) + opbox(140, 80, 'quarantine', 'problem', 'red', 90, 34) + cap('Nothing silently dropped.', '', 'blue', y=144, h=30),
    t(180, 14, 'Tests on tiny DataFrames', 9.4, bold=True) + ''.join(opbox(20 + k * 66, 50, n, 'pass', 'green', 60, 34) for k, n in enumerate(['quar', 'dedup', 'latest', 'revenue', 'feature'])) + cap('Each behaviour pinned.', '', 'green', y=144, h=30),
    t(180, 14, 'Rows reconcile', 9.4, bold=True) + t(180, 52, '842,587 = 835,067 + 4,944 + 2,576', 8.6, 'ink', mono=True) + opbox(40, 76, 'gate 1', 'no NULL, unique', 'green', 130, 34) + opbox(190, 76, 'gate 2', '0.59% < 2%', 'green', 130, 34) + cap('Gates pass → gold.', '', 'green', y=144, h=30),
    t(180, 14, 'Gold, ready for consumers', 9.4, bold=True) + opbox(20, 50, 'daily_city_revenue', '84 rows → BI', 'blue', 150, 34) + opbox(190, 50, 'customer_features', '20,000 → churn ML', 'violet', 150, 34) + cap('Same numbers on the cluster.', '', 'blue', y=144, h=30),
]
two = anim_two('Capstone: the pipeline', 'Build, test, gate, publish', 'Real pipeline outputs', 'How the pieces fit', see, B1,
               ['Clean.', 'Test.', 'Reconcile.', 'Publish.'], ['Valid vs quarantine.', 'Unit tests.', 'Gates.', 'Gold tables.'])

def five(title, lines, hid, kind, sub, cons, caps):
    fr = [t(180, 22, a, 9.4, 'acc' if i == 4 else 'ink', bold=True) + t(180, 56, b, 8.4, 'ink2') + cap(c, '', tone, y=150, h=34) for i, (a, b, c, tone) in enumerate(lines)]
    return anim_one(kind, title, sub, cons[0], cons[1], fr, caps, hid=hid)

s1 = five('The 3 a.m. bad file', [
    ('Partner sends a broken export', '3,000 amounts = “N/A”', 'Nightly run starts.', 'blue'),
    ('Rows go to quarantine', 'quarantine_pct jumps to 5.34%', 'Gate threshold 2%.', 'red'),
    ('Gate fails the job', 'gold is not overwritten', 'Dashboards keep yesterday.', 'green'),
    ('Scheduler alerts on-call', 'quarantine shows the reason', 'Fix at source.', 'green'),
    ('Re-run after the fix', 'idempotent overwrite', 'No duplicates.', 'blue')],
    'scenario-gate', 'Real-time scenario 1', 'A gate stopping a bad day. (Lab numbers from 13.3.)',
    ('Quality gate', 'Fail the run and keep the last good gold instead of publishing bad numbers'),
    ['Bad file.', 'Quarantine.', 'Stop.', 'Alert.', 'Re-run.'])
s2 = five('“The numbers changed when I re-ran it”', [
    ('Analyst re-runs a day', 'revenue doubles', 'Append mode used.', 'blue'),
    ('Cause: append, not overwrite', 'same rows written twice', 'Not idempotent.', 'red'),
    ('Fix: overwrite the partition', 'dynamic partition overwrite', 'Lesson 5.3.', 'green'),
    ('Dedup on order_id', 'retries cannot double count', 'Profile finding.', 'green'),
    ('Re-run safe any time', 'same 835,067 rows', 'Local and cluster match.', 'blue')],
    'scenario-idempotent', 'Real-time scenario 2', 'Why re-runs must be safe. (Typical.)',
    ('Idempotency', 'Overwrite by partition and deduplicate so re-running a day gives the same result'),
    ['Re-run.', 'Append.', 'Overwrite.', 'Dedup.', 'Safe.'])
s3 = five('A bug fix breaks revenue', [
    ('Dev changes status logic', 'lower() instead of upper()', 'Small refactor.', 'blue'),
    ('Unit test fails in CI', 'delivered-only revenue test', 'assertDataFrameEqual.', 'red'),
    ('Bug never ships', 'fixed in minutes', 'Not found by finance.', 'green'),
    ('Tests document behaviour', 'five rules, five tests', 'New devs read them.', 'green'),
    ('Add a test per incident', 'suite grows with lessons', 'Regression-proof.', 'blue')],
    'scenario-tests', 'Real-time scenario 3 · advanced', 'Unit tests catching a regression. (Typical.)',
    ('Unit tests', 'Test pure transforms on tiny DataFrames so logic bugs fail in CI, not in production'),
    ['Change.', 'CI fails.', 'Caught.', 'Docs.', 'Grow.'])

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Build, test, gate, publish</h2>
  <p>Left: real pipeline outputs. Right: how the pieces fit.</p>
''' + two + '''
  <p>Three live scenarios follow: a gate stopping a bad file, a non-idempotent re-run, and a test catching a regression.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

def uc_(word, sub, tone, title, desc, flow_):
    return usecase(f'<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-{tone}" style="stroke:var(--{tone if tone != "acc" else "track"})"/>' + t(60, 42, word, 11, tone, bold=True) + t(60, 58, sub, 7.4, 'ink2'), title, desc, flow_)
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>This pattern at work</h2>
''' + '\n'.join([
    uc_('retail', 'sales', 'blue', '1. Daily sales close', 'Nightly job builds store revenue; a gate blocks publishing if receipts are missing.', ['POS files', '*gated job', 'Finance BI']),
    uc_('bank', 'recon', 'green', '2. Payments reconciliation', 'Transactions are typed and deduplicated; unmatched ones are quarantined for review.', ['Ledger + PSP', '*quarantine', 'Ops']),
    uc_('ride', 'features', 'violet', '3. Driver features', 'Daily features feed incentive and churn models (Module 10).', ['Trips', '*gold features', 'ML']),
    uc_('telco', 'billing', 'acc', '4. Usage billing', 'Tested transforms guarantee each call record is billed exactly once.', ['CDRs', '*dedup + tests', 'Invoices']),
    uc_('health', 'claims', 'blue', '5. Claims pipeline', 'Partner claims files with bad codes are quarantined, not dropped.', ['Partners', '*rules', 'Adjudication']),
]) + '''
  <p class="muted">The capstone data is synthetic and generated by the lab script.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> read the profiling results in <a href="../01-problem-and-dataset/">13.1</a>. This lesson uses partitioned writes (<a href="../../05-reading-and-writing-data/03-writing-data-and-small-files/">5.3</a>), spark-submit (<a href="../../11-spark-in-production/01-spark-submit-and-deploy-modes/">11.1</a>) and testing (<a href="../../11-spark-in-production/04-testing-pyspark-code/">11.4</a>).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
