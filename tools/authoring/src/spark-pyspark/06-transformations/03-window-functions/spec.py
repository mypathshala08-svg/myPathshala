import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='06-transformations', lesson='03-window-functions', n='6.3',
    module_label='Module 6 · Transformations',
    title='Window functions',
    desc='Window functions in PySpark 4.3.0: row_number, rank and dense_rank on ties, lag and lead for day-over-day change, the default RANGE frame that repeated a running total (1210 twice) versus rowsBetween, moving averages and share of total, top-2 orders per city on 5M rows planned with WindowGroupLimit, and a window without partitionBy that collapsed 4 partitions into 1 (12.0 s vs 7.1 s).',
    og_desc='Our running total showed 1210 twice: the default window frame is RANGE, not ROWS. Window functions in PySpark, tested.',
    minutes=32, level='Intermediate',
    lead='Window functions compute ranks, previous values, running totals and shares while keeping every row. This lesson covers partitions, ordering and <b>frames</b>, the frame trap behind repeated running totals, and the top-N-per-group pattern on 5 million orders. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', 'Frame trap reproduced', 'WindowGroupLimit in the plan', 'Runs in your browser (Python)'],
)

MAIN = '''# Running total: ROWS frame vs RANGE frame (the default with orderBy)
days = [("11-01", 450), ("11-02", 380), ("11-02", 380), ("11-03", 520)]

rows_total, acc = [], 0
for d, r in days:                          # ROWS: one row at a time
    acc += r
    rows_total.append(acc)

range_total = []
for d, r in days:                          # RANGE: all peers with day <= d
    range_total.append(sum(x for dd, x in days if dd <= d))

print("ROWS :", rows_total)
print("RANGE:", range_total)
'''
RUN = dict(
    heading='Run the code: ROWS vs RANGE',
    intro='<p>A model of Step 3. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    range_total.append(sum(x for dd, x in days if dd <= d))', 'Both 11-02 rows include each other: 1210 twice, as in the lab.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then make the days unique: do the results agree?', code=None),
        dict(label='2 · Predict first: ranks', hint='<b>Predict first:</b> rank and dense_rank for 610, 610, 300.',
             code='''vals = [610, 610, 300]
rank = [1 + sum(v > x for v in vals) for x in vals]
dense = [sorted(set(vals), reverse=True).index(x) + 1 for x in vals]
print(rank, dense)
'''),
        dict(label='3 · lag', hint='Day-over-day change.',
             code='''rev = [450, 380, 380, 520]
print([None] + [b - a for a, b in zip(rev, rev[1:])])
'''),
        dict(label='4 · Top 2 per city', hint='row_number <= 2 per group.',
             code='''orders = [("Pune", 959, 7), ("Pune", 959, 3), ("Pune", 950, 1), ("Delhi", 959, 5)]
out = {}
for c, amt, oid in sorted(orders, key=lambda r: (r[0], -r[1], r[2])):
    out.setdefault(c, [])
    if len(out[c]) < 2:
        out[c].append(oid)
print(out)
'''),
        dict(label='5 · Spot the error', hint='This window has no partitionBy.', expect='error',
             code='''window = {"partitionBy": [], "orderBy": ["amount"]}
assert window["partitionBy"], "no partitionBy: all rows go to one partition; partition or use top-k/percentiles"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: windows',
    intro='<p>In the <code>pyspark</code> shell. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Default frame', cmd='[r.t for r in d.where("city=\'Pune\'").select(F.sum("revenue").over(\n    Window.partitionBy("city").orderBy("day")).alias("t")).orderBy("day").collect()]', file='pyspark',
             output='[450, 1210, 1210, 1730]', note='RANGE includes peers.'),
        dict(title='2 · Partitions', cmd='o.withColumn("r", F.row_number().over(Window.orderBy("amount"))).rdd.getNumPartitions()', file='pyspark',
             output='1', note='From 4 input partitions.'),
        dict(title='3 · Plan', cmd='top.explain()   # rn <= 2', file='pyspark',
             output='WindowGroupLimit [city], [amount DESC NULLS LAST, order_id ASC NULLS FIRST], row_number(), 2, Partial', note='Prunes before the shuffle.'),
    ],
)

TRACE = dict(
    heading='lag within partitions',
    intro='<p>Follow how lag resets at each new city.</p>',
    code='''rows = [("Delhi", 300), ("Delhi", 610), ("Pune", 450), ("Pune", 380)]
prev = {}
for city, rev in rows:
    print(city, rev, "prev:", prev.get(city))
    prev[city] = rev
''',
    notes={4: 'Partition :: Each city has its own previous value; the first is null.'},
)

WORKED_INTRO = 'Three window tasks from TiffinGo reports.'
EXAMPLES = [
    dict(level='b', tag='Windows · basics', title='Day-over-day revenue change',
         problem='<p>Change in revenue versus the previous day, per city.</p>',
         inp='daily revenue per city',
         approach=['Window by city ordered by day.', 'lag(revenue).', 'Subtract.'],
         code='''print("""w = Window.partitionBy("city").orderBy("day")
daily.withColumn("change", F.col("revenue") - F.lag("revenue").over(w))""")
''', notes={2: 'One shuffle :: No self-join needed.'},
         tryit='Step 2.'),
    dict(level='i', tag='Windows · frames', title='Correct running total',
         problem='<p>Running revenue per city, row by row.</p>',
         inp='orders with timestamps',
         approach=['Order by timestamp and order_id.', 'rowsBetween(unboundedPreceding, currentRow).', 'Check the last value equals the total.'],
         code='''print("""w = (Window.partitionBy("city").orderBy("order_ts", "order_id")
       .rowsBetween(Window.unboundedPreceding, Window.currentRow))
o.withColumn("running", F.sum("amount").over(w))""")
''', notes={2: 'Tiebreaker :: order_id makes the order unique.'},
         tryit='Step 3.'),
    dict(level='a', tag='Windows · sessions', title='Sessionise clicks',
         problem='<p>Number sessions per user with a 30-minute gap rule.</p>',
         inp='user_id, click_ts',
         approach=['lag(click_ts) per user.', 'new = gap > 30 min.', 'Running sum of new.'],
         code='''clicks = [0, 5, 50, 52, 120]          # minutes
session, out, prev = 0, [], None
for c in clicks:
    if prev is None or c - prev > 30:
        session += 1
    out.append(session); prev = c
print(out)
''', notes={4: 'Gap :: lag gives prev; a running sum numbers sessions.'},
         tryit='Use rowsBetween for the running sum.'),
]

QUIZ = mix([
    dict(q='Beginner: Does a window function reduce the number of rows?', options=['Yes', 'No', 'Only rank', 'Only sum'], answer=1,
         why='Unlike groupBy.'),
    dict(q='Beginner: Which gives 1, 1, 3 on ties?', options=['row_number', 'rank', 'dense_rank', 'ntile'], answer=1,
         why='Gaps after ties.'),
    dict(q='Beginner: What does lag return for the first row of a partition?', options=['0', 'null', 'The last row', 'Error'], answer=1,
         why='No previous row.'),
    dict(q='Intermediate: Default frame with orderBy?', options=['ROWS unbounded', 'RANGE unbounded preceding to current row', 'Whole partition', 'Current row only'], answer=1,
         why='Peers together.'),
    dict(q='Intermediate: Running total that grows row by row needs…', options=['rangeBetween', 'rowsBetween(unboundedPreceding, currentRow)', 'No frame', 'groupBy'], answer=1,
         why='830 then 1210.'),
    dict(q='Intermediate: Window with only partitionBy covers…', options=['One row', 'The whole partition', 'Previous rows', 'Nothing'], answer=1,
         why='Share of total.'),
    dict(q='Advanced: What did Spark add for row_number() <= 2?', options=['Broadcast', 'WindowGroupLimit before the shuffle', 'Cache', 'Sampling'], answer=1,
         why='Partial top-N per partition.'),
    dict(q='Advanced: Window without partitionBy on 5M rows…', options=['Faster', 'Moves all data to 1 partition', 'Fails always', 'Uses broadcast'], answer=1,
         why='12.0 s vs 7.1 s.'),
])

REVISION = [
    'Window = <code>partitionBy</code> + <code>orderBy</code> + frame; rows are kept.',
    'Ties: row_number 1,2; rank 1,1,3; dense_rank 1,1,2. Add tiebreakers.',
    '<code>lag</code>/<code>lead</code> for previous/next row, per partition.',
    'Default frame with orderBy = RANGE (peers together): 1210 twice. Use <code>rowsBetween</code>.',
    'Partition-only window = whole partition: shares of total.',
    'Top-N: <code>row_number() &lt;= N</code>; Spark plans WindowGroupLimit.',
    'No partitionBy → 1 partition (12.0 vs 7.1 s): avoid.',
]
FAQ = [
    ('ROWS or RANGE?', 'ROWS counts physical rows; RANGE uses ordering values (all equal values together, or a value range like the last 7 days). Choose explicitly.'),
    ('Can I use windows in SQL?', 'Yes: <code>SUM(amount) OVER (PARTITION BY city ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)</code>.'),
    ('Is a window cheaper than groupBy + join?', 'Usually: one shuffle by the partition keys instead of an aggregation plus a join.'),
    ('What about QUALIFY?', 'Spark 4.2 added QUALIFY in SQL to filter on window results directly, e.g. <code>QUALIFY row_number() OVER (…) = 1</code>.'),
    ('Do windows work in streaming?', 'Ranking windows over unbounded data are not supported in Structured Streaming; use time windows and aggregations (Module 9).'),
]

PRACTICE_INTRO = 'Programs about ranks, offsets and frames.'
PROBLEMS = [
    dict(level='easy', title='Share', stmt='Share of Pune’s revenue on 3 November.', inp='520 of 1730',
         code='''print(round(520 / 1730 * 100, 1))
''', explain='30.1 in the lab.'),
    dict(level='easy', title='Running total', stmt='Running total row by row.', inp='[450, 380, 380, 520]',
         code='''import itertools
print(list(itertools.accumulate([450, 380, 380, 520])))
''', explain='ROWS frame.'),
    dict(level='easy', title='Moving average', stmt='Average of current and previous.', inp='[450, 380, 380, 520]',
         code='''v = [450, 380, 380, 520]
print([v[0]] + [(a + b) / 2 for a, b in zip(v, v[1:])])
''', explain='rowsBetween(-1, 0).'),
    dict(level='medium', title='Dense rank', stmt='dense_rank of values.', inp='[520, 450, 380, 380]',
         code='''v = [520, 450, 380, 380]
order = sorted(set(v), reverse=True)
print([order.index(x) + 1 for x in v])
''', explain='No gaps.'),
    dict(level='medium', title='Peers', stmt='RANGE running total.', inp='days with ties',
         code='''d = [("01", 450), ("02", 380), ("02", 380), ("03", 520)]
print([sum(x for dd, x in d if dd <= k) for k, _ in d])
''', explain='Peers counted together.'),
    dict(level='medium', title='Gaps to sessions', stmt='Count sessions with a 30-min gap rule.', inp='[0, 10, 70, 75, 200]',
         code='''t = [0, 10, 70, 75, 200]
print(1 + sum(b - a > 30 for a, b in zip(t, t[1:])))
''', explain='lag + flag + sum.'),
    dict(level='business', title='Best day', stmt='City’s best day.', inp='daily revenue',
         code='''d = {"11-01": 450, "11-02": 760, "11-03": 520}
print(max(d, key=d.get))
''', explain='row_number = 1 ordered by revenue desc.'),
    dict(level='business', title='Growth', stmt='Day-over-day growth percent.', inp='450 → 520',
         code='''print(f"{(520 - 450) / 450:.1%}")
''', explain='lag in a window.'),
]

SCN_INTRO = 'Window questions are a favourite in data engineering interviews.'
SCENARIOS = (
    scn('Any company · PySpark', 'Fresher', '“rank vs dense_rank vs row_number”',
        'Explain the difference.',
        'ties?',
        '<p>On ties row_number still numbers 1, 2; rank gives 1, 1, 3; dense_rank 1, 1, 2. For “one row per group” I use row_number with a tiebreaker.</p>', 'Saying they are the same.') +
    scn('Data engineering', 'Mid-level', 'Top 3 per category',
        'Get the top 3 dishes by orders per restaurant.',
        'the pattern?',
        '''<ul>
          <li>Aggregate counts per (restaurant, dish).</li>
          <li>row_number over partitionBy(restaurant).orderBy(desc(count), dish).</li>
          <li>Filter rn &lt;= 3; Spark prunes early with WindowGroupLimit.</li>
        </ul>''', 'groupBy + collect_list + sort in Python.') +
    scn('Analytics', 'Mid-level', 'Running total repeats',
        'A running total shows the same value on two rows.',
        'frames?',
        '''<ol>
          <li>Default frame is RANGE; equal order values are peers.</li>
          <li>Use rowsBetween(unboundedPreceding, currentRow).</li>
          <li>Add a tiebreaker to make the order unique.</li>
        </ol>''', '“Spark bug.”') +
    scn('Data engineering', 'Senior', 'Slow window job',
        'A window job runs on one task and fails with OOM.',
        'partitioning?',
        '''<ul>
          <li>Check for windows without partitionBy (one partition).</li>
          <li>Skewed partition keys also concentrate rows.</li>
          <li>Rewrite with top-k, approximate percentiles or a better key.</li>
        </ul>''', 'Raising executor memory only.')
)
