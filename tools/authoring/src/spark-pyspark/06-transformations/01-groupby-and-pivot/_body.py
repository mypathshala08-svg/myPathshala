import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l61_group.txt'
def sec(a, b=None, drop=()):
    s = capsec(C, a, b, drop)
    s = re.sub(r'#\d+L?', '', s)
    return '\n'.join(l if len(l) <= 140 else l[:137] + ' …' for l in s.split('\n'))

def mini(x, y, rows, w=(46, 52), tone='card', head=None):
    o = ''
    if head:
        for c, hname in enumerate(head):
            o += t(x + sum(w[:c]) + w[c] / 2, y - 4, hname, 6.4, 'ink2', bold=True)
    for r, row in enumerate(rows):
        for c, v in enumerate(row):
            o += box(x + sum(w[:c]), y + r * 15, w[c] - 2, 13, tone, rx=2) + t(x + sum(w[:c]) + w[c] / 2 - 1, y + r * 15 + 9.5, v, 6.4, mono=True)
    return o
LONG = [['Pune', 'DELIV', '473,621'], ['Pune', 'CANC', '25,025'], ['Delhi', 'DELIV', '475,037'], ['Delhi', 'CANC', '25,047']]
WIDE = [['Pune', '473,621', '25,025'], ['Delhi', '475,037', '25,047']]

# ---------------------------------------------------------------- story
sc_ = (mini(14, 34, LONG, (44, 44, 52), head=['city', 'status', 'n']) + arrow(160, 64, 196, 64, 'ink3', 1.1) + t(178, 56, 'pivot', 6.8, 'ink2') +
       mini(202, 42, WIDE, (44, 56, 50), 'green', head=['city', 'DELIVERED', 'CANCELLED']) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured (5M orders)', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('partial_sum before the shuffle', 'green'), ('null city = its own group', 'amber'),
           ('pivot w/o values: 4 extra jobs', 'amber'), ('…2.72 s vs 1.30 s with values', 'green'),
           ('pivot on order_id: > 10000 error', 'red'), ('unpivot: 8 x 3 = 24 rows', 'green')])))
scene_svg = scene('groupBy aggregates rows that share a key; pivot turns key values into columns and unpivot turns them back. We built TiffinGo’s city report from 5 million orders and timed pivot with and without a list of values.', sc_,
                  'Aggregate <tspan font-weight="700" class="s-acc">early</tspan>; give pivot its <tspan font-weight="700" class="s-acc">values</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“One row per city, one column per status”</h2>
  <div class="story">
    <p class="narration">The operations head wants a daily sheet: one row per city with orders, revenue, average bill, customers and cancellations, and a second sheet with delivered, cancelled and refunded revenue side by side. Riya wrote it with <code>groupBy</code> and <code>pivot</code>. It worked, but the REFUNDED column was missing and the job ran more Spark jobs than she expected.</p>

{scene_svg}

R> Sir, there are refunded orders in the app. Why no column?
A> Pivot without a value list first runs a query to find the distinct values, and in this data set there were none. Give the list yourself: the column is always there, and Spark skips that extra query.
K> And groupBy on 5 million rows: is it one big shuffle?
A> A smaller one than you think: Spark adds up inside each partition first. Today: aggregates, partial aggregation, null keys, rollup and cube, pivot and its limits, unpivot and collecting lists. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Aggregation at three levels
L1> Counting votes
      <ul>
        <li>Each polling booth counts its own votes first, then sends only totals to the centre. That is partial aggregation.</li>
        <li>A pivot is turning the result list (party, votes) into a table with one column per party.</li>
        <li>Blank ballots still form a pile of their own: nulls are a group.</li>
      </ul>
L2> The API
      <ul>
        <li><code>df.groupBy(cols).agg(F.count, F.sum, F.avg, F.countDistinct, F.collect_list…)</code>; <code>rollup</code> and <code>cube</code> add subtotals.</li>
        <li><code>groupBy(k).pivot(col, [values]).agg(…)</code>; <code>unpivot(ids, values, name, value)</code> (alias <code>melt</code>, Spark 3.4+).</li>
        <li>Conditional counts: <code>F.sum(F.when(cond, 1).otherwise(0))</code> or <code>F.count_if(cond)</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>The plan aggregated twice: <code>partial_sum</code> per partition, shuffle, final <code>sum</code>.</li>
        <li>Pivot without values ran 4 extra jobs and took 2.72 s; with values, 0 extra jobs and 1.30 s, and the empty REFUNDED column existed.</li>
        <li>Pivot on <code>order_id</code> failed: more than 10,000 distinct values (<code>spark.sql.pivotMaxValues</code>).</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Grouping, pivoting and unpivoting</h2>
''' + def_block(
    '<code>groupBy</code> returns a <code>GroupedData</code> object whose <code>agg</code> computes aggregate functions over the rows of each group of equal key values; null keys form a group of their own. Spark executes most aggregations in two phases: a <b>partial aggregation</b> within each input partition, a shuffle by the grouping keys, and a final merge, so only partial results cross the network. <code>rollup</code> and <code>cube</code> compute additional grouping sets (hierarchical subtotals, or all combinations) with nulls marking the rolled-up columns. <code>pivot(col, values)</code> rotates distinct values of a column into output columns of an aggregation; if values are not given, Spark first computes them with a separate query and limits them to <code>spark.sql.pivotMaxValues</code> (10,000). <code>unpivot</code> (also <code>melt</code>) performs the reverse, turning columns into rows.',
    'groupBy puts rows with the same key together and computes totals, counts or averages per group. Spark adds things up inside each partition first, so the shuffle is small. pivot turns values into columns, unpivot turns columns back into rows. Give pivot its list of values.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('groupBy / agg', 'Group rows by keys and compute aggregates.'),
    ('Partial aggregation', 'Per-partition pre-aggregation before the shuffle.'),
    ('countDistinct', 'Number of different values in a group.'),
    ('rollup', 'Subtotals along a hierarchy (city → status).'),
    ('cube', 'Subtotals for every combination.'),
    ('pivot', 'Values of a column become columns.'),
    ('unpivot / melt', 'Columns become rows.'),
    ('collect_list / set', 'Gather group values into an array.'),
]) + '''

  <h3>Common aggregate functions</h3>
''' + table(['Function', 'Returns', 'Nulls'], [
    ['<code>count("*")</code> / <code>count(c)</code>', 'rows / non-null values', 'counted / skipped'],
    ['<code>sum</code>, <code>avg</code>, <code>min</code>, <code>max</code>', 'number', 'skipped'],
    ['<code>countDistinct</code> / <code>approx_count_distinct</code>', 'distinct count', 'skipped'],
    ['<code>count_if(cond)</code>', 'rows where cond is true', '—'],
    ['<code>collect_list</code> / <code>collect_set</code>', 'array (with / without duplicates)', 'skipped'],
    ['<code>first</code>, <code>last</code>, <code>max_by(c, ord)</code>, <code>min_by</code>', 'a value from the group', 'first/last depend on order'],
    ['<code>percentile_approx</code>, <code>median</code>', 'percentile', 'skipped'],
], minw=600) + lv + '''
EXAM> “Why should you pass values to pivot?” Without them Spark runs an extra query over the data to find distinct values (4 extra jobs in our lab, 2.72 s vs 1.30 s), the output columns depend on the data (a missing status means a missing column), and more than 10,000 values fails. With a list, the schema is fixed and the extra pass disappears.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Grouping sets</h2>
''' + table(['Method', 'Groups produced for (city, status)', 'Lab (Pune, Delhi × 2 statuses)'], [
    ['<code>groupBy</code>', '(city, status)', '4 rows'],
    ['<code>rollup</code>', '(city, status), (city), ()', '7 rows: + city totals + grand total'],
    ['<code>cube</code>', '(city, status), (city), (status), ()', '9 rows: + status totals'],
    ['SQL <code>GROUPING SETS</code>', 'exactly the sets you list', 'any'],
], minw=640) + '''
WARN> In rollup and cube results a <code>NULL</code> in a key column means “all values” (a subtotal), but a real null key also shows as <code>NULL</code>. Use <code>F.grouping("city")</code> or <code>grouping_id()</code> to tell them apart, or replace null keys with <code>"unknown"</code> before grouping.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>The city report</h2>
  <p>All outputs are real: PySpark 4.3.0, local mode with 4 cores, <code>orders_big</code> (5,000,000 orders), 8 shuffle partitions.</p>
''' + stepper([
    ('Step 1 · Many aggregates in one pass',
     code('python', 'l61_group.py', 'o.groupBy("city").agg(F.count("*").alias("orders"), F.sum("amount").alias("revenue"),\n    F.round(F.avg("amount"), 1).alias("avg"), F.countDistinct("customer_id").alias("customers"),\n    F.sum(F.when(F.col("status") == "CANCELLED", 1).otherwise(0)).alias("cancelled")).orderBy("city").show()', sec('== 1)', '== 2)')),
     'One <code>agg</code> computed five figures per city in a single job. The conditional count is a <code>sum</code> of a <code>when</code>. Mumbai and Bengaluru have twice the orders of other cities, and every city served all 3,999 customers (a generated data set).'),
    ('Step 2 · Partial aggregation',
     code('python', 'l61_group.py', 'o.groupBy("city").agg(F.sum("amount")).explain()', sec('== 2)', '== 3)')),
     'Read bottom-up: the scan reads two columns, the first <code>HashAggregate</code> computes <code>partial_sum</code> per city <b>inside each partition</b>, the <code>Exchange</code> shuffles only those partial sums (a few rows per partition instead of 5 million), and the top <code>HashAggregate</code> adds them up. This is why <code>groupBy().agg()</code> is far cheaper than <code>groupByKey</code> in Lesson 2.4.'),
    ('Step 3 · Null keys and subtotals',
     code('python', 'l61_group.py', 'd.groupBy("city").sum("n").show()\ns = o.where("city IN (\'Pune\', \'Delhi\') AND status IN (\'DELIVERED\', \'CANCELLED\')")\ns.rollup("city", "status").agg(F.count("*").alias("n")).show()\ns.cube("city", "status").count().count(); s.rollup("city", "status").count().count()', sec('== 3)', '== 5)')),
     'Null keys were grouped together, not dropped. <code>rollup</code> added a total per city (status NULL) and a grand total (both NULL): 998,730 orders. <code>cube</code> also added totals per status across cities: 9 rows instead of 7. Note how a subtotal NULL looks exactly like a real null key.'),
    ('Step 4 · Pivot, with and without values',
     code('python', 'l61_group.py', 'o.groupBy("city").pivot("status").agg(F.sum("amount"))\no.groupBy("city").pivot("status", ["DELIVERED", "CANCELLED", "REFUNDED"]).agg(F.sum("amount"))\n# jobs counted with the REST API while building the DataFrame', sec('== 5)', '== 6)')),
     'Without values, merely <b>defining</b> the pivot ran 4 jobs to find the distinct statuses, and only two existed in this data, so the REFUNDED column did not appear. With a list: no extra jobs, half the time, and a stable schema where REFUNDED is simply null. Downstream code and dashboards should never depend on which values happened to occur.'),
    ('Step 5 · The pivot limit',
     code('python', 'l61_group.py', 'o.groupBy("city").pivot("customer_id").count()          # 4,000 columns\no.limit(20000).groupBy("city").pivot("order_id").count()', sec('== 6)', '== 7)')),
     'Pivoting on customers produced a <b>4,000-column</b> DataFrame without complaint; on order ids Spark stopped at 10,000 distinct values. Wide pivots are slow to plan and hard to use; if a column has thousands of values, keep the data long and aggregate.'),
    ('Step 6 · Unpivot and collecting values',
     code('python', 'l61_group.py', 'wide.unpivot(["city"], ["DELIVERED", "CANCELLED", "REFUNDED"], "status", "revenue")\no.where("customer_id = 1806").groupBy("customer_id").agg(F.count("*").alias("n"),\n    F.collect_set("city").alias("cities"), F.slice(F.sort_array(F.collect_list("amount"), asc=False), 1, 3).alias("top3"))', sec('== 7)')),
     '<code>unpivot</code> turned 8 rows × 3 status columns back into 24 long rows, including null REFUNDED values. <code>collect_set</code> gathered the 8 cities customer 1806 ordered in, and <code>collect_list</code> + <code>sort_array</code> + <code>slice</code> their three biggest bills. Collected arrays live in one row: never collect a group that can hold millions of values.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('city   orders  revenue  cancelled', W), ('Pune   498646  254.0M   25025', W), ('Mumbai 1001205 510.3M   49775', W)], size=7.4),
    term([('HashAggregate sum', W), ('Exchange hashpartitioning(city)', Y), ('HashAggregate partial_sum', G)], size=7.4),
    term([('rollup: 7 rows, cube: 9 rows', W), ('NULL = subtotal (or null key!)', Y)], size=7.4),
    term([('pivot no values : 4 jobs, 2.72 s', Y), ('pivot with values: 0 jobs, 1.30 s', G), ('REFUNDED column only with list', W)], size=7.2),
    term([('unpivot: 24 rows', G), ('pivot on order_id: > 10000 values', RD)], size=7.6),
]
B1 = [
    t(180, 14, 'One pass, many figures', 9.4, bold=True) + flow([('5M rows', 'orders', 'card'), ('groupBy', 'city', 'blue'), ('8 rows', '5 aggregates', 'green')], y=50, w=96, gap=22) + cap('One job for the whole report.', '', 'blue', y=144, h=30),
    t(180, 14, 'Add up before shuffling', 9.4, bold=True) + ''.join(opbox(14, 30 + k * 34, f'partition {k + 1}', 'partial sums', 'green', 96, 28) + arrow(110, 44 + k * 34, 200, 66, 'ink3', 1.0) for k in range(3)) + opbox(204, 50, 'final sum', '8 cities', 'blue', 110, 32) + cap('Only partial results cross the network.', '', 'green', y=144, h=30),
    t(180, 14, 'Subtotals', 9.4, bold=True) + mini(60, 30, [['Pune', 'DELIV', '473,621'], ['Pune', 'NULL', '498,646'], ['NULL', 'NULL', '998,730']], (60, 60, 70), head=['city', 'status', 'n']) + cap('NULL marks the rolled-up column.', '', 'amber', y=144, h=30),
    t(180, 14, 'Rows become columns', 9.4, bold=True) + mini(14, 34, LONG, (44, 44, 52), head=['city', 'status', 'n']) + arrow(160, 64, 196, 64, 'ink3', 1.1) + mini(202, 42, WIDE, (44, 56, 50), 'green', head=['city', 'DELIVERED', 'CANCELLED']) + cap('A value list fixes the columns.', '', 'green', y=144, h=30),
    t(180, 14, 'And back again', 9.4, bold=True) + mini(14, 42, WIDE, (44, 56, 50), 'green', head=['city', 'DELIVERED', 'CANCELLED']) + arrow(170, 64, 196, 64, 'ink3', 1.1) + mini(202, 34, LONG, (44, 44, 52), head=['city', 'status', 'n']) + cap('unpivot: columns become rows.', '', 'blue', y=144, h=30),
]
see_caps = ['Five aggregates per city.', 'Two aggregation steps in the plan.', 'Subtotals from rollup and cube.', 'Values list: no extra jobs.', 'Back to long; very wide pivots fail.']
behind_caps = ['groupBy + agg in one job.', 'Partial aggregation per partition.', 'Grouping sets add totals.', 'Distinct values define columns.', 'unpivot reverses pivot.']
two = anim_two('groupBy and pivot', 'Summaries and reshaping', 'Real lab outputs', 'What Spark computes', see, B1, see_caps, behind_caps)

# ---- scenario 1: missing column
e1 = (t(180, 22, 'Dashboard expects REFUNDED', 9.4, bold=True) + t(180, 56, 'pivot("status") without values', 8.4, 'ink', mono=True) + cap('Works most days.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'A day with no refunds', 9.4, bold=True) + t(180, 56, 'column REFUNDED does not exist', 8.4, 'ink2') + cap('Dashboard query fails.', '', 'red', y=150, h=34))
e3 = (t(180, 22, 'Schema depends on data', 9.4, bold=True) + t(180, 56, 'the extra distinct query decides', 8.4, 'ink2') + cap('Like our Step 4.', '', 'amber', y=150, h=34))
e4 = (t(180, 22, 'Pass the values', 9.4, bold=True) + t(180, 56, 'pivot("status", STATUSES)', 8.4, 'ink', mono=True) + cap('Same columns every day.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Fill nulls for display', 9.4, 'acc', bold=True) + t(180, 56, 'na.fill(0) on the pivot result', 8.4, 'ink', mono=True) + cap('0 refunds, not missing.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'A column that disappeared',
              'Stable pivot schemas. (Behaviour from our lab.)',
              'Pivot values', 'Without a values list the pivot columns depend on the data; pass the list for a stable schema and no extra query', [e1, e2, e3, e4, e5],
              ['Dashboard.', 'No refunds.', 'Data decides.', 'List values.', 'Fill zeros.'],
              hid='scenario-pivot')

# ---- scenario 2: subtotal confusion
b1 = (t(180, 22, 'Finance report with rollup', 9.4, bold=True) + t(180, 56, 'rollup("region", "city")', 8.4, 'ink', mono=True) + cap('Subtotals per region.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Orders with no city', 9.4, bold=True) + t(180, 56, 'city is null for 2% of orders', 8.4, 'ink2') + cap('Also show as NULL.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'Totals counted twice', 9.4, bold=True) + t(180, 56, 'analyst sums all NULL rows', 8.4, 'ink2') + cap('Wrong board numbers.', '', 'red', y=150, h=34))
b4 = (t(180, 22, 'grouping_id()', 9.4, bold=True) + t(180, 56, 'marks real subtotal rows', 8.4, 'ink', mono=True) + cap('Or fill keys first.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Label subtotals', 9.4, 'acc', bold=True) + t(180, 56, '“All cities” instead of NULL', 8.4, 'ink2') + cap('Readable output.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'NULL meant two different things',
              'Subtotals and null keys. (Typical.)',
              'rollup nulls', 'Rollup uses NULL for subtotals, which collides with real null keys; use grouping_id or fill keys before grouping', [b1, b2, b3, b4, b5],
              ['Rollup.', 'Null keys.', 'Double count.', 'grouping_id.', 'Label.'],
              hid='scenario-rollup')

# ---- scenario 3: skewed key
u1 = (t(180, 22, 'groupBy("restaurant_id")', 9.4, bold=True) + t(180, 56, 'one chain = 40% of orders', 8.4, 'ink2') + cap('One reduce task is huge.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Partial aggregation helps', 9.4, bold=True) + t(180, 56, 'sums are combined per partition', 8.4, 'ink2') + cap('For sum and count.', '', 'green', y=150, h=34))
u3 = (t(180, 22, 'But not collect_list', 9.4, bold=True) + t(180, 56, 'every value must travel', 8.4, 'ink2') + cap('One task, one giant array.', '', 'red', y=150, h=34))
u4 = (t(180, 22, 'Aggregate, not collect', 9.4, bold=True) + t(180, 56, 'counts, sums, top-N with windows', 8.4, 'ink2') + cap('Small results per key.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Skew handling', 9.4, 'acc', bold=True) + t(180, 56, 'salting, AQE skew join', 8.4, 'ink2') + cap('Lesson 8.3.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'One key holds 40% of the data',
              'Aggregations on skewed keys. (Typical.)',
              'Skewed groupBy', 'Partial aggregation makes sums cheap even on skewed keys, but collect_list must move every value to one task', [u1, u2, u3, u4, u5],
              ['Skew.', 'Partial agg.', 'collect_list.', 'Aggregate.', 'Salting.'],
              hid='scenario-skew-agg')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Summaries and reshaping</h2>
  <p>Left: real outputs. Right: what Spark computes.</p>
''' + two + '''
  <p>Three live scenarios follow: a pivot column that disappeared, NULL meaning two things, and a skewed key.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Aggregations at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'KPIs', 12, 'blue', bold=True) + t(60, 58, 'daily', 7.4, 'ink2'),
    '1. Daily KPI tables',
    'Orders, revenue, average bill and cancellations per city and day are one groupBy over the fact table.',
    ['Orders', '*groupBy + agg', 'KPI table']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'pivot', 12, 'green', bold=True) + t(60, 58, 'sheets', 7.4, 'ink2'),
    '2. Spreadsheet-style reports',
    'Status or month columns for finance sheets are pivots with a fixed value list.',
    ['Long table', '*pivot(values)', 'Wide sheet']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'totals', 11, 'violet', bold=True) + t(60, 58, 'rollup', 7.4, 'ink2'),
    '3. Hierarchical totals',
    'Region → city → restaurant totals for management reports come from rollup or GROUPING SETS.',
    ['Facts', '*rollup', 'Subtotals']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'ML', 12, 'acc', bold=True) + t(60, 58, 'features', 7.4, 'ink2'),
    '4. Customer features',
    'Per-customer counts, sums and favourite cities feed churn and recommendation models.',
    ['Orders', '*groupBy customer', 'Features']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'melt', 12, 'acc', bold=True) + t(60, 58, 'tidy', 7.4, 'ink2'),
    '5. Tidying wide files',
    'Wide spreadsheets from partners (one column per month) are unpivoted into long tables.',
    ['Wide CSV', '*unpivot', 'Long table']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> reduceByKey vs groupByKey in <a href="../../02-rdds/04-narrow-vs-wide-and-the-shuffle/">2.4</a>, nulls in <a href="../../04-dataframes/04-nulls-and-duplicates/">4.4</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
