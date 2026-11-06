import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='06-transformations', lesson='01-groupby-and-pivot', n='6.1',
    module_label='Module 6 · Transformations',
    title='groupBy and pivot',
    desc='Aggregations in PySpark 4.3.0 on 5 million orders: several aggregates in one groupBy, partial aggregation visible in the plan, null keys as a group, rollup and cube subtotals (7 vs 9 rows), pivot without values running 4 extra jobs (2.72 s vs 1.30 s) and dropping an empty REFUNDED column, the 10,000-value pivot limit, unpivot back to 24 rows, and collect_list / collect_set.',
    og_desc='pivot() without a value list ran 4 extra jobs and silently dropped a column. groupBy and pivot in PySpark, measured on 5M orders.',
    minutes=30, level='Beginner → Intermediate',
    lead='Module 6 covers the transformations used in almost every pipeline. First: <b>aggregations</b>. This lesson builds a city report with <code>groupBy</code>, explains partial aggregation, subtotals with <code>rollup</code>/<code>cube</code>, and reshapes data with <code>pivot</code> and <code>unpivot</code>. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', '5M orders', 'Pivot jobs counted', 'Runs in your browser (Python)'],
)

MAIN = '''# Partial aggregation: what crosses the network?
partitions = [
    [("Pune", 450), ("Delhi", 300), ("Pune", 520)],
    [("Pune", 380), ("Delhi", 610)],
]
partials = []
for p in partitions:                      # step 1: inside each partition
    acc = {}
    for city, amount in p:
        acc[city] = acc.get(city, 0) + amount
    partials.append(acc)
print("sent over the shuffle:", partials)

final = {}
for acc in partials:                      # step 2: after the shuffle
    for city, s in acc.items():
        final[city] = final.get(city, 0) + s
print("final:", final)
'''
RUN = dict(
    heading='Run the code: two-phase aggregation',
    intro='<p>A model of the plan in Step 2. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('for p in partitions:                      # step 1: inside each partition', 'HashAggregate(partial_sum) in the plan.'),
        ('for acc in partials:                      # step 2: after the shuffle', 'The final HashAggregate after the Exchange.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Count rows before and after step 1.', code=None),
        dict(label='2 · Predict first: pivot columns', hint='<b>Predict first:</b> statuses present are DELIVERED and CANCELLED. Columns without and with a value list?',
             code='''present = ["DELIVERED", "CANCELLED"]
given = ["DELIVERED", "CANCELLED", "REFUNDED"]
print("no list:", sorted(present), "| with list:", given)
'''),
        dict(label='3 · Pivot by hand', hint='Turn (city, status, n) rows into a table.',
             code='''rows = [("Pune", "DEL", 473621), ("Pune", "CAN", 25025), ("Delhi", "DEL", 475037)]
wide = {}
for c, s, n in rows:
    wide.setdefault(c, {})[s] = n
print(wide)
'''),
        dict(label='4 · Rollup rows', hint='Groups produced by rollup(city, status).',
             code='''cities, statuses = 2, 2
print(cities * statuses + cities + 1, "rows")
'''),
        dict(label='5 · Spot the error', hint='This pivot has no value list.', expect='error',
             code='''code = 'df.groupBy("city").pivot("status").sum("amount")'
assert 'pivot("status", [' in code, "pass the values: stable columns and no extra distinct query"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: aggregation',
    intro='<p>In the <code>pyspark</code> shell. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Null key group', cmd='d.groupBy("city").sum("n").orderBy("city").collect()', file='pyspark',
             output="[Row(city=None, sum(n)=7), Row(city='Pune', sum(n)=11)]", note='Nulls are a group.'),
        dict(title='2 · Pivot columns', cmd='o.groupBy("city").pivot("status").sum("amount").columns', file='pyspark',
             output="['city', 'CANCELLED', 'DELIVERED']", note='Only values that occur.'),
        dict(title='3 · Unpivot', cmd='wide.unpivot(["city"], ["DELIVERED", "CANCELLED", "REFUNDED"], "status", "revenue").count()', file='pyspark',
             output='24', note='8 cities × 3 statuses.'),
    ],
)

TRACE = dict(
    heading='rollup step by step',
    intro='<p>Follow which groups rollup produces.</p>',
    code='''rows = [("Pune", "DEL", 3), ("Pune", "CAN", 1), ("Delhi", "DEL", 2)]
groups = {}
for city, status, n in rows:
    for key in ((city, status), (city, None), (None, None)):
        groups[key] = groups.get(key, 0) + n
print(groups)
''',
    notes={4: 'Grouping sets :: (city, status), (city), () for rollup.', 5: 'NULL :: None marks the rolled-up level.'},
)

WORKED_INTRO = 'Three reports built with aggregation.'
EXAMPLES = [
    dict(level='b', tag='Aggregation · basics', title='Daily KPIs per city',
         problem='<p>Orders, revenue and cancellations per city and day.</p>',
         inp='orders',
         approach=['groupBy city and order_date.', 'count, sum, count_if.', 'Round averages.'],
         code='''print("""o.groupBy("city", "order_date").agg(F.count("*").alias("orders"),
    F.sum("amount").alias("revenue"), F.count_if(F.col("status") == "CANCELLED").alias("cancelled"))""")
''', notes={2: 'count_if :: Shorter than sum(when(...)).'},
         tryit='Step 1.'),
    dict(level='i', tag='Aggregation · reshape', title='Revenue by status, fixed columns',
         problem='<p>A sheet with one column per status, even if a status is absent.</p>',
         inp='orders',
         approach=['Fixed value list.', 'pivot + sum.', 'na.fill(0).'],
         code='''STATUSES = ["DELIVERED", "CANCELLED", "REFUNDED"]
print(f'o.groupBy("city").pivot("status", {STATUSES}).sum("amount").na.fill(0)')
''', notes={1: 'Contract :: The column list is part of the report’s schema.'},
         tryit='Step 4.'),
    dict(level='a', tag='Aggregation · design', title='Totals for a management deck',
         problem='<p>Revenue by region and city with subtotals and a grand total.</p>',
         inp='orders with region',
         approach=['Fill null keys first.', 'rollup(region, city).', 'Label with grouping_id.'],
         code='''print("""o.na.fill({"region": "unknown", "city": "unknown"}) \\
  .rollup("region", "city").agg(F.sum("amount").alias("revenue"), F.grouping_id().alias("level"))""")
''', notes={1: 'Clean keys :: So NULL only means subtotal.'},
         tryit='Step 3.'),
]

QUIZ = mix([
    dict(q='Beginner: What does groupBy return before agg?', options=['A DataFrame', 'GroupedData', 'An RDD', 'A list'], answer=1,
         why='Call agg or an aggregate method.'),
    dict(q='Beginner: Are null keys dropped by groupBy?', options=['Yes', 'No, they form a group', 'Only in SQL', 'Error'], answer=1,
         why='NULL group with sum 7.'),
    dict(q='Beginner: Which adds subtotals along a hierarchy?', options=['cube', 'rollup', 'pivot', 'unpivot'], answer=1,
         why='rollup(city, status).'),
    dict(q='Intermediate: What is partial_sum in a plan?', options=['A bug', 'Per-partition pre-aggregation before the shuffle', 'Sampling', 'Cache'], answer=1,
         why='Only partial results are shuffled.'),
    dict(q='Intermediate: Why give pivot a value list?', options=['Required', 'Avoids an extra query and fixes the columns', 'Sorts output', 'Uses less memory only'], answer=1,
         why='4 extra jobs without it.'),
    dict(q='Intermediate: How many rows does cube(city, status) give for 2 × 2 values?', options=['4', '7', '9', '16'], answer=2,
         why='4 + 2 + 2 + 1.'),
    dict(q='Advanced: Default maximum distinct values for pivot?', options=['100', '1,000', '10,000', 'Unlimited'], answer=2,
         why='spark.sql.pivotMaxValues.'),
    dict(q='Advanced: Which aggregate does NOT benefit much from partial aggregation?', options=['sum', 'count', 'collect_list', 'max'], answer=2,
         why='Every value still travels.'),
])

REVISION = [
    '<code>groupBy(...).agg(...)</code>: many aggregates in one job; null keys form a group.',
    'Two-phase plan: <code>partial_sum</code> per partition → shuffle → final sum.',
    'Conditional counts: <code>sum(when(...))</code> or <code>count_if</code>.',
    '<code>rollup</code> (hierarchy) and <code>cube</code> (all combinations); NULL = subtotal; use <code>grouping_id</code>.',
    'Pivot with a <b>value list</b>: no extra jobs (2.72 → 1.30 s), stable columns.',
    'Pivot limit 10,000 values; <code>unpivot</code>/<code>melt</code> reverses.',
    '<code>collect_list</code>/<code>collect_set</code> for small groups only.',
]
FAQ = [
    ('Is groupBy().agg() the same as SQL GROUP BY?', 'Yes, they produce the same plan. Use whichever is clearer; spark.sql works on temp views.'),
    ('How do I aggregate with several conditions?', 'Use several <code>count_if</code>/<code>sum(when())</code> expressions in one agg, or FILTER clauses in SQL: <code>count(*) FILTER (WHERE status = \'CANCELLED\')</code>.'),
    ('Why are my aggregate column names like sum(amount)?', 'Default names; use <code>.alias()</code> on each aggregate.'),
    ('Can I pivot on two columns?', 'Pivot takes one column; combine two into one with concat_ws, or pivot then join.'),
    ('Is countDistinct expensive?', 'Yes, it must shuffle distinct values. For dashboards consider approx_count_distinct (Lesson 4.5).'),
]

PRACTICE_INTRO = 'Programs about grouping and reshaping.'
PROBLEMS = [
    dict(level='easy', title='Average bill', stmt='Average from revenue and orders.', inp='Pune 254,040,203 / 498,646',
         code='''print(round(254_040_203 / 498_646, 1))
''', explain='Lab avg 509.5.'),
    dict(level='easy', title='Cancel rate', stmt='Cancellation rate for Pune.', inp='25,025 of 498,646',
         code='''print(f"{25025 / 498646:.1%}")
''', explain='About 5%.'),
    dict(level='easy', title='Group sums', stmt='Sum per key.', inp='pairs',
         code='''pairs = [("Pune", 10), (None, 5), ("Pune", 1), (None, 2)]
s = {}
for k, v in pairs:
    s[k] = s.get(k, 0) + v
print(s)
''', explain='None is a key too.'),
    dict(level='medium', title='Shuffle saving', stmt='Rows shuffled with and without partial aggregation.', inp='5M rows, 4 partitions, 8 cities',
         code='''print("without:", 5_000_000, "| with:", 4 * 8)
''', explain='Partial sums only.'),
    dict(level='medium', title='Unpivot', stmt='Turn a wide row into long rows.', inp='{"city": "Pune", "DEL": 473621, "CAN": 25025}',
         code='''w = {"city": "Pune", "DEL": 473621, "CAN": 25025}
print([(w["city"], k, v) for k, v in w.items() if k != "city"])
''', explain='unpivot(["city"], ["DEL", "CAN"], ...).'),
    dict(level='medium', title='Cube size', stmt='Grouping sets in cube of 3 columns.', inp='2^n',
         code='''print(2 ** 3)
''', explain='Every subset of the columns.'),
    dict(level='business', title='Share of revenue', stmt='Mumbai’s share of total revenue.', inp='510,290,994 of 2,546,901,275',
         code='''print(f"{510_290_994 / 2_546_901_275:.1%}")
''', explain='Mumbai and Bengaluru ≈ 40%.'),
    dict(level='business', title='Refund column', stmt='Report value for a status with no rows.', inp='after na.fill(0)',
         code='''print({"REFUNDED": 0})
''', explain='Explicit zero beats a missing column.'),
]

SCN_INTRO = 'Aggregation questions are in every PySpark interview.'
SCENARIOS = (
    scn('Any company · PySpark', 'Fresher', '“Total revenue per city”',
        'Write PySpark for revenue and order count per city.',
        'basic groupBy?',
        '<p><code>df.groupBy("city").agg(F.sum("amount").alias("revenue"), F.count("*").alias("orders"))</code>. One agg computes several aggregates; I alias every result.</p>', 'Calling groupBy twice and joining.') +
    scn('Data engineering', 'Mid-level', 'groupBy vs groupByKey',
        'Why is DataFrame groupBy efficient?',
        'do you know partial aggregation?',
        '''<ul>
          <li>Catalyst plans partial aggregation per partition, then a shuffle of partial results.</li>
          <li>The plan shows partial_sum before the Exchange.</li>
          <li>groupByKey on RDDs ships every value.</li>
        </ul>''', '“Both shuffle everything.”') +
    scn('Data engineering', 'Mid-level', 'Pivot in production',
        'A daily pivot sometimes misses columns.',
        'do you know pivot semantics?',
        '''<ol>
          <li>Without values, columns come from the data.</li>
          <li>Pass the value list; fill nulls.</li>
          <li>Also saves an extra query (4 jobs in my test).</li>
        </ol>''', 'Adding columns afterwards with withColumn if missing.') +
    scn('Analytics', 'Senior', 'Subtotals',
        'Produce region/city subtotals and a grand total in one query.',
        'grouping sets?',
        '''<ul>
          <li>rollup(region, city) or GROUPING SETS.</li>
          <li>grouping_id to distinguish subtotal rows from null keys.</li>
          <li>Fill null keys beforehand.</li>
        </ul>''', 'Three queries and a union.')
)
