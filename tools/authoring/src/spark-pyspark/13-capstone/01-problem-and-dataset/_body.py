import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l131_profile.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)

def layers(x, y, hi=None):
    items = [('landing', 'raw CSV / JSON', 'card'), ('silver', 'typed, deduped', 'blue'), ('gold', 'revenue, features', 'green'), ('consumers', 'BI, churn model', 'violet')]
    o = ''
    for k, (n, d, tone) in enumerate(items):
        o += opbox(x + k * 86, y, n, d, 'acc' if hi == k else tone, 78, 38)
        if k:
            o += arrow(x + k * 86 - 8, y + 19, x + k * 86, y + 19, 'ink3', 1)
    o += opbox(x + 86, y + 50, 'quarantine', 'bad rows + reason', 'red', 78, 30)
    o += arrow(x + 125, y + 38, x + 125, y + 50, 'red', 1)
    return o

# ---------------------------------------------------------------- story
sc_ = (layers(14, 40) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Profiled (842,587 orders)', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('dup order_id rows : 2,587', 'amber'), ('orphan customers  : 20,639', 'amber'),
           ('amount not number : 3,279', 'red'), ('negative amounts  : 1,665', 'red'),
           ('rest 1 = 30% of orders', 'violet'), ('plain CAST → error', 'red')])))
scene_svg = scene('The capstone builds a complete TiffinGo pipeline: two weeks of raw order files, customers and restaurants land in a folder with real-world problems. Before writing any pipeline code we profile the data with Spark and turn every finding into a requirement.', sc_,
                  'Profile first: <tspan font-weight="700" class="s-acc">the data decides</tspan> the design.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Build us a revenue and churn pipeline”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s leadership wants two things every morning: revenue per city per day, and a churn-risk score for every customer. The raw data is what it always is: daily CSV exports of orders, a customer file from the CRM, and a restaurant list from the partner app. Nobody has checked its quality.</p>

{scene_svg}

K> Sir, this is the capstone. Shall we start writing the pipeline?
A> Not yet. Senior engineers spend the first hour <b>profiling</b>: how many rows, which keys repeat, which values are broken, how skewed the data is. Every surprise you find now is a bug you do not ship later.
R> And then?
A> Then we design the layers: landing, silver, gold, and a quarantine for bad rows, using everything from the course: schemas, try_cast, dedup, joins, partitioning, tests, spark-submit. This lesson is the problem and the data; the next builds it; the last reviews it like an interview. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> The capstone at three levels
L1> Opening a restaurant kitchen
      <ul>
        <li>Before cooking for 800 restaurants’ worth of orders, the chef inspects deliveries: rotten vegetables (bad values), double deliveries (duplicates), boxes with no label (orphans).</li>
        <li>Good ingredients go to the kitchen (silver); bad ones are set aside with a note (quarantine).</li>
      </ul>
L2> The deliverables
      <ul>
        <li><b>silver.orders</b>: typed, deduplicated, partitioned by <code>order_date</code>; <b>silver.customers</b>: one row per customer.</li>
        <li><b>gold.daily_city_revenue</b>: orders, revenue, average order per city per day; <b>gold.customer_features</b>: 14-day orders, spend, recency for churn scoring (Module 10).</li>
        <li><b>quarantine.orders</b>: every rejected row with a reason; a quality gate that stops the run if too many rows are bad.</li>
      </ul>
L3> What profiling found
      <ul>
        <li>842,587 order rows in 14 files; 2,587 rows repeat an <code>order_id</code> (retries).</li>
        <li>3,279 amounts are not numbers (empty, “N/A”, “12O” with a letter O) and 1,665 are negative; a plain CAST fails under ANSI.</li>
        <li>One restaurant has 30% of all orders: a skew risk for joins (Module 8).</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>The capstone problem</h2>
''' + def_block(
    'The capstone is a batch data pipeline in the <b>medallion architecture</b>. Raw files arrive in a <b>landing</b> zone unchanged. A <b>silver</b> layer applies explicit schemas, converts types safely, normalises values, removes duplicates and resolves the latest version of each entity, writing partitioned Parquet; rows that cannot be repaired go to a <b>quarantine</b> table with a reason. A <b>gold</b> layer builds business-level aggregates and features for consumers. <b>Data profiling</b> (row counts, key uniqueness, referential integrity, invalid and out-of-range values, distributions and skew) precedes design, and its findings become explicit <b>data-quality rules</b> enforced as gates in the pipeline.',
    'We build a pipeline that turns messy daily files into trusted tables: raw files stay as they arrived, a cleaned layer fixes types and duplicates and sets aside bad rows, and a business layer produces revenue reports and customer features. First we measure what is wrong with the data, then we design rules to handle it.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Landing', 'Raw files, exactly as received.'),
    ('Silver', 'Clean, typed, deduplicated data.'),
    ('Gold', 'Business aggregates and features.'),
    ('Quarantine', 'Rejected rows with a reason.'),
    ('Profiling', 'Measuring data before designing.'),
    ('Orphan', 'Foreign key with no matching row.'),
    ('Quality gate', 'Check that can stop the pipeline.'),
    ('Grain', 'What one row means in a table.'),
]) + '''

  <h3>The datasets</h3>
''' + table(['Source', 'Format', 'Rows', 'Known problems (found below)'], [
    ['orders (14 daily files)', 'CSV, header, all text', '842,587', 'duplicate order_ids, bad and negative amounts, 30% skew'],
    ['customers (CRM export)', 'CSV', '20,100', '100 duplicate ids, 194 invalid phones'],
    ['restaurants (partner app)', 'JSON lines', '800', 'clean; one chain is huge'],
    ['orders → customers', 'key', '', '20,639 orders reference unknown customers'],
], minw=620) + lv + '''
EXAM> “How do you start a new data pipeline?” Profile the sources first: volumes, schemas, key uniqueness, referential integrity, invalid values, distributions and skew. Turn findings into explicit rules (types, dedup keys, quarantine reasons, thresholds), define the grain and owners of each output table, then design layers (landing/raw, silver/cleaned, gold/business) and tests before writing transformation code.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>From finding to rule</h2>
''' + table(['Finding', 'Rule in the pipeline', 'Course lesson'], [
    ['Everything is text in CSV', 'Explicit schema; <code>try_cast</code> to typed columns', '4.2, 12.3'],
    ['Bad / negative amounts', 'Quarantine with reason <code>bad_amount</code> / <code>negative_amount</code>', '4.4'],
    ['Duplicate order_ids', '<code>dropDuplicates(["order_id"])</code> after validation', '4.4'],
    ['Duplicate customers', 'Keep the latest row per id (window <code>row_number</code>)', '6.3'],
    ['Orphan customer_ids', 'Keep orders; left join for features; report the count', '6.2'],
    ['30% skewed restaurant', 'Broadcast the small restaurant table', '8.2, 8.3'],
    ['Daily files', 'Partition silver by <code>order_date</code>, one file per day', '5.3, 8.1'],
], minw=620) + '''
WARN> Do not “fix” bad data silently. Turning “N/A” into 0 makes revenue wrong, and dropping rows hides an upstream bug. Keep the bad rows with a reason, count them every run, and stop the pipeline when the share jumps. Also decide the <b>grain</b> before coding: here one silver row = one order, one gold row = one city per day.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Profiling the raw data</h2>
  <p>All outputs are real: PySpark 4.3.0, <code>local[4]</code>. The raw data was generated by the lab’s <code>generate.py</code> with realistic problems (it is synthetic, but nothing below was edited by hand). Everything is read as text first so that nothing is lost while profiling.</p>
''' + stepper([
    ('Step 1 · Sizes and schemas',
     code('python', 'profile_raw.py', 'o = spark.read.option("header", True).csv(f"{R}/orders")      # all columns as string\nc = spark.read.option("header", True).csv(f"{R}/customers")\nr = spark.read.json(f"{R}/restaurants")\nprint(o.count(), len(o.inputFiles()), c.count(), r.count()); o.printSchema()', sec('== 1)', '== 2)')),
     '842,587 order rows in 14 daily files, 20,100 customer rows, 800 restaurants. Reading CSV without a schema gives all-string columns: perfect for profiling, because nothing is converted or dropped yet.'),
    ('Step 2 · Keys: duplicates and orphans',
     code('python', 'profile_raw.py', 'o.count() - o.select("order_id").distinct().count()\nc.count() - c.select("customer_id").distinct().count()\no.join(c.select("customer_id").distinct(), "customer_id", "left_anti").count()', sec('== 2)', '== 3)')),
     '<b>2,587</b> extra rows repeat an existing order_id (app retries), and 100 customers appear twice. A <code>left_anti</code> join finds <b>20,639</b> orders whose customer is missing from the CRM export. Each number becomes a rule: dedup keys, “latest row wins”, and a decision on orphans.'),
    ('Step 3 · Bad values',
     code('python', 'profile_raw.py', 'amt = F.col("amount").try_cast("int")\no.select(F.sum(amt.isNull().cast("int")), F.sum((amt < 0).cast("int")), F.min(amt), F.max(amt)).show()\no.filter(amt.isNull()).groupBy("amount").count().show()\no.select(F.col("amount").cast("int")).agg(F.sum("amount")).collect()     # plain CAST', sec('== 3)', '== 4)')),
     '<code>try_cast</code> (Lesson 12.3) shows 3,279 amounts that are not numbers: empty (read as NULL), “N/A”, and “12O” with a capital letter O. Another 1,665 are negative. A plain <code>CAST</code> on this column fails with <b>CAST_INVALID_INPUT</b> under Spark 4’s ANSI mode, so the pipeline must handle these explicitly. Customers also have 194 invalid phone numbers.'),
    ('Step 4 · Distributions and skew',
     code('python', 'profile_raw.py', 'o.groupBy("status").count().orderBy(F.desc("count")).show()\no.groupBy("rest_id").count().orderBy(F.desc("count")).limit(3).collect()\no.groupBy(F.to_date("order_ts").alias("day")).count().orderBy("day").show(3)', sec('== 4)')),
     '85% of orders are DELIVERED, which is what revenue counts. Restaurant 1 (“Cloud Kitchen Co”) has <b>30%</b> of all orders: any shuffle on <code>rest_id</code> would put a third of the data in one task (Lesson 8.3), so the restaurant join must be a broadcast. About 60,000 orders per day: a natural partition column.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('orders rows: 842587 | files: 14', W), ('customers rows: 20100', W), ('restaurants rows: 800', W)], size=7.4),
    term([('duplicate order_id rows: 2587', Y), ('duplicate customer_id rows: 100', Y), ('orphan customer_ids: 20639', Y)], size=7.2),
    term([('not a number: 3279 (NULL, N/A, 12O)', RD), ('negative: 1665', RD), ('plain CAST -> CAST_INVALID_INPUT', RD)], size=7.0),
    term([('DELIVERED 716556 | CANCELLED 84207', W), ('rest 1: 253012 orders = 30.0%', Y), ('~60,000 orders per day', W)], size=7.0),
]
B1 = [
    t(180, 14, 'Medallion layers', 9.4, bold=True) + layers(10, 40) + cap('Raw stays raw; bad rows set aside.', '', 'blue', y=144, h=30),
    t(180, 14, 'Keys tell the story', 9.4, bold=True) + opbox(20, 46, 'order_id', 'must be unique', 'amber', 100, 34) + opbox(130, 46, 'customer_id', 'latest row wins', 'amber', 100, 34) + opbox(240, 46, 'FK → CRM', '20,639 orphans', 'amber', 100, 34) + cap('Dedup and integrity rules.', '', 'amber', y=144, h=30),
    t(180, 14, 'try_cast finds, CAST fails', 9.4, bold=True) + opbox(20, 46, "'12O'", 'try_cast → NULL', 'green', 150, 34) + opbox(190, 46, "'12O'", 'CAST → error', 'red', 150, 34) + cap('Quarantine with a reason.', '', 'red', y=144, h=30),
    t(180, 14, 'Skew decides the join', 9.4, bold=True) + ''.join(box(40 + k * 28, 110 - h, 20, h, 'acc' if h > 50 else 'green', rx=2) for k, h in enumerate([70, 10, 9, 10, 9, 10, 9, 10])) + t(290, 70, 'rest 1 = 30%', 8, 'red', bold=True) + cap('Broadcast restaurants.', '', 'green', y=144, h=30),
]
see_caps = ['Sizes.', 'Keys.', 'Bad values.', 'Distributions.']
behind_caps = ['The layers.', 'Key rules.', 'Safe casting.', 'Skew-aware design.']
two = anim_two('Capstone: problem and data', 'Profile before you build', 'Real profiling outputs', 'What it means for the design', see, B1, see_caps, behind_caps)

e1 = (t(180, 22, 'Revenue report off by 2%', 9.4, bold=True) + t(180, 56, 'finance asks why', 8.4, 'ink2') + cap('After months in production.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Cause: duplicate retries', 9.4, bold=True) + t(180, 56, 'same order_id counted twice', 8.4, 'ink2') + cap('Never profiled.', '', 'red', y=150, h=34))
e3 = (t(180, 22, 'Profile first, every source', 9.4, bold=True) + t(180, 56, 'counts, keys, values, skew', 8.4, 'ink2') + cap('One hour of work.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Rules written down', 9.4, bold=True) + t(180, 56, 'dedup on order_id', 8.4, 'ink2') + cap('Reviewed with finance.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Checks every run', 9.4, 'acc', bold=True) + t(180, 56, 'duplicates removed: 2,576', 8.4, 'ink2') + cap('Lesson 13.2.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'The 2% revenue gap',
              'Why profiling comes first. (Typical; counts from our lab.)',
              'Profiling', 'Profiling sources before building turns hidden problems into explicit rules', [e1, e2, e3, e4, e5],
              ['Gap.', 'Duplicates.', 'Profile.', 'Rules.', 'Checks.'],
              hid='scenario-profile')
b1 = (t(180, 22, '20,639 orders, unknown customer', 9.4, bold=True) + t(180, 56, 'CRM export lags the app', 8.4, 'ink2') + cap('Drop them?', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Dropping loses revenue', 9.4, bold=True) + t(180, 56, 'they are real paid orders', 8.4, 'ink2') + cap('Wrong for finance.', '', 'red', y=150, h=34))
b3 = (t(180, 22, 'Keep in silver and gold revenue', 9.4, bold=True) + t(180, 56, 'revenue by restaurant city', 8.4, 'ink2') + cap('No customer needed.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Features: customers only', 9.4, bold=True) + t(180, 56, 'left join from customers', 8.4, 'ink2') + cap('Scored when they appear.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Report the orphan count', 9.4, 'acc', bold=True) + t(180, 56, 'ask CRM team to fix sync', 8.4, 'ink2') + cap('Fix at the source.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Orders without customers',
              'Handling referential-integrity gaps. (Typical; count from our lab.)',
              'Orphans', 'Decide per output whether orphan rows are kept, and report them upstream', [b1, b2, b3, b4, b5],
              ['Orphans.', 'Drop?', 'Keep.', 'Features.', 'Report.'],
              hid='scenario-orphans')
u1 = (t(180, 22, 'Interviewer: “design a pipeline”', 9.4, bold=True) + t(180, 56, 'for messy daily files', 8.4, 'ink2') + cap('Classic system-design question.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Start with questions', 9.4, bold=True) + t(180, 56, 'volume, freshness, consumers', 8.4, 'ink2') + cap('Not with code.', '', 'green', y=150, h=34))
u3 = (t(180, 22, 'Then profiling and rules', 9.4, bold=True) + t(180, 56, 'keys, bad values, skew', 8.4, 'ink2') + cap('Show the numbers.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Layers and gates', 9.4, bold=True) + t(180, 56, 'landing → silver → gold', 8.4, 'ink2') + cap('Plus quarantine.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Testing and operations', 9.4, 'acc', bold=True) + t(180, 56, 'tests, submit, monitoring', 8.4, 'ink2') + cap('Lessons 13.2–13.3.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'The pipeline design interview',
              'Structuring a design answer. (Typical.)',
              'Design interview', 'Answer pipeline design questions from requirements and data profiling to layers, tests and operations', [u1, u2, u3, u4, u5],
              ['Question.', 'Requirements.', 'Profile.', 'Layers.', 'Operate.'],
              hid='scenario-interview')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Profile before you build</h2>
  <p>Left: real profiling outputs. Right: what each finding means for the design.</p>
''' + two + '''
  <p>Three live scenarios follow: a revenue gap, orphan orders, and a design interview.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>This pattern at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'retail', 11, 'blue', bold=True) + t(60, 58, 'sales', 7.4, 'ink2'),
    '1. Retail sales',
    'Store POS exports land daily; silver dedups receipts, gold builds sales by store and day.',
    ['POS files', '*silver/gold', 'Sales cube']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'bank', 12, 'green', bold=True) + t(60, 58, 'txns', 7.4, 'ink2'),
    '2. Banking transactions',
    'Transactions with invalid amounts are quarantined for operations review.',
    ['Core banking', '*quarantine', 'Ops queue']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'health', 11, 'violet', bold=True) + t(60, 58, 'claims', 7.4, 'ink2'),
    '3. Insurance claims',
    'Claims from many partners are profiled and normalised before fraud models.',
    ['Partner files', '*rules', 'Clean claims']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'telco', 12, 'acc', bold=True) + t(60, 58, 'CDRs', 7.4, 'ink2'),
    '4. Telecom usage',
    'Call records are partitioned by day; subscriber features feed churn models.',
    ['CDRs', '*daily partitions', 'Churn features']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'edu', 12, 'acc', bold=True) + t(60, 58, 'courses', 7.4, 'ink2'),
    '5. EdTech engagement',
    'Course events become daily engagement tables and dropout-risk features.',
    ['Events', '*gold features', 'Risk scores']) + '''
  <p class="muted">The capstone data is synthetic and generated by the lab script.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> this capstone uses the whole course, especially nulls and duplicates (<a href="../../04-dataframes/04-nulls-and-duplicates/">4.4</a>), CSV/JSON (<a href="../../05-reading-and-writing-data/01-csv-and-json/">5.1</a>), joins (<a href="../../06-transformations/02-joins/">6.2</a>) and skew (<a href="../../08-performance-tuning/03-data-skew-and-salting/">8.3</a>).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
