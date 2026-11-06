import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l45_sort.txt'
def sec(a, b=None, drop=()):
    s = capsec(C, a, b, drop + ('within plan', 'orderBy plan'))
    s = re.sub(r' \| plan: \[.*?\]', '', s)
    s = re.sub(r', plan \[.*?\]', '', s)
    return '\n'.join(l if len(l) <= 140 else l[:137] + ' …' for l in s.split('\n'))

def parts(x, y, vals, tone='card', w=34, h=16, label=''):
    o = t(x, y - 4, label, 6.8, 'ink2', anchor='start', bold=True) if label else ''
    for k, v in enumerate(vals):
        o += box(x + k * (w + 3), y, w, h, tone, rx=3) + t(x + k * (w + 3) + w / 2, y + 11, v, 6.8, mono=True)
    return o

# ---------------------------------------------------------------- story
sc_ = (parts(14, 36, ['530', '120', '840'], 'card', label='partition 1') + parts(14, 72, ['300', '760', '210'], 'card', label='partition 2') +
       arrow(130, 62, 170, 62, 'ink3', 1.1) + t(150, 54, 'orderBy', 6.8, 'ink2') +
       parts(176, 36, ['120', '210', '300'], 'green', label='after: p1') + parts(176, 72, ['530', '760', '840'], 'green', label='p2') +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('orderBy 5M rows: 6.7 s, 120 MiB', 'amber'), ('sortWithinPartitions: 2.0 s, 0', 'green'),
           ('orderBy+limit(5): 0.8 s, no shuffle', 'green'), ('countDistinct 3999, approx 3985', 'ink'),
           ('union by position: Card in city', 'red'), ('unionByName: correct', 'green')])))
scene_svg = scene('Sorting, distinct, limit and union look simple but differ greatly in cost and correctness. We timed them on 5 million orders and merged two feeds whose columns were in a different order.', sc_,
                  'A global sort is a <tspan font-weight="700" class="s-acc">shuffle</tspan>; union matches columns by <tspan font-weight="700" class="s-acc">position</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Why is Card a city?”</h2>
  <div class="story">
    <p class="narration">TiffinGo merged orders from its app and from a partner. Both feeds had <code>order_id, city, payment</code>, but the partner wrote <code>payment</code> before <code>city</code>. After <code>app.union(partner)</code> the city report showed thousands of orders from “Card” and “UPI”. No error, no warning.</p>

{scene_svg}

R> Sir, the columns have the same names. Why did Spark mix them?
A> Because <code>union</code> matches columns by <b>position</b>, like SQL <code>UNION ALL</code>. Names are ignored. <code>unionByName</code> matches by name.
K> And Riya’s top-5 query takes a second, but sorting the full table takes much longer. Isn’t it the same sort?
A> No. Spark knows it only needs five rows and never sorts the rest. Today: sorting and its shuffle, nulls in sort order, limit, distinct counts and every kind of union, with timings on 5 million orders. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Sort, distinct, limit and union at three levels
L1> Exam answer sheets
      <ul>
        <li>Sorting all sheets of a whole school by marks means collecting them from every class (a shuffle). Sorting inside each class is quick.</li>
        <li>Finding the top 5 does not need a full sort: each class sends its own top 5 and you pick from those.</li>
        <li>Stacking two piles of sheets works only if both forms have their boxes in the same order.</li>
      </ul>
L2> The API
      <ul>
        <li><code>orderBy</code>/<code>sort</code> (global, shuffle), <code>sortWithinPartitions</code> (no shuffle); <code>F.desc</code>, <code>asc_nulls_last</code> etc.</li>
        <li><code>limit(n)</code>, <code>distinct()</code>, <code>F.countDistinct</code>, <code>F.approx_count_distinct</code>.</li>
        <li><code>union</code> (by position, keeps duplicates), <code>unionByName(allowMissingColumns=True)</code>, <code>intersect</code>, <code>subtract</code>, <code>exceptAll</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>Sorting 5M orders: 6.7 s and 120 MiB of shuffle; <code>sortWithinPartitions</code>: 2.0 s and no shuffle.</li>
        <li><code>orderBy().limit(5)</code> became <b>TakeOrderedAndProject</b>: 0.8 s, no shuffle.</li>
        <li>Same-typed columns in a different order were unioned silently into the wrong columns; <code>unionByName</code> fixed it.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Ordering and combining DataFrames</h2>
''' + def_block(
    '<code>orderBy</code> (alias <code>sort</code>) returns a DataFrame totally ordered by the given expressions; Spark implements it with a <b>range-partitioning shuffle</b> (sampling the data to choose partition boundaries) followed by a sort within each partition. Ascending order places nulls first and descending order places them last unless specified. <code>sortWithinPartitions</code> sorts each partition without a shuffle. <code>limit(n)</code> returns at most n rows; combined with <code>orderBy</code> it is planned as a top-k operator (<code>TakeOrderedAndProject</code>) that keeps only n rows per partition. <code>distinct</code> removes duplicate rows via an aggregation (a shuffle). <code>union</code> returns all rows of two DataFrames with the same number of columns, <b>resolving columns by position</b> and keeping duplicates (SQL UNION ALL); <code>unionByName</code> resolves by name. <code>intersect</code>, <code>subtract</code> (EXCEPT DISTINCT) and <code>exceptAll</code> implement set operations.',
    'A full sort moves data between machines and is expensive; sorting within partitions or taking a top-N is cheap. distinct also needs a shuffle. union simply stacks two DataFrames by column position, so columns must be in the same order; unionByName lines them up by name.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('orderBy / sort', 'Global order; range shuffle.'),
    ('sortWithinPartitions', 'Order inside each partition; no shuffle.'),
    ('TakeOrderedAndProject', 'Top-k plan for orderBy + limit.'),
    ('nulls first / last', 'Where nulls go in the order.'),
    ('approx_count_distinct', 'HyperLogLog estimate of distinct values.'),
    ('union', 'Stack rows by column position (UNION ALL).'),
    ('unionByName', 'Stack rows by column name.'),
    ('exceptAll', 'Subtract keeping duplicates.'),
]) + '''

  <h3>What each operation costs</h3>
''' + table(['Operation', 'Shuffle?', 'Lab (5M orders)'], [
    ['<code>orderBy</code> / <code>sort</code>', 'Yes (range) + sampling', '6.7 s, 120.1 MiB'],
    ['<code>sortWithinPartitions</code>', 'No', '2.0 s, 0 MiB'],
    ['<code>orderBy(…).limit(5)</code>', 'No (top-k per partition)', '0.8 s'],
    ['<code>limit(5)</code>', 'No', '0.12 s'],
    ['<code>distinct</code> / <code>countDistinct</code>', 'Yes (aggregation)', '3,999 customers, 0.6–0.9 s'],
    ['<code>approx_count_distinct</code>', 'Small (sketches)', '3,985 (0.35% off)'],
    ['<code>union</code>', 'No', 'partitions add up: 2 + 3 = 5'],
], minw=620) + lv + '''
EXAM> “union vs unionByName?” <code>union</code> matches columns by position and keeps duplicates (UNION ALL); with same-typed columns in a different order it silently puts values in the wrong columns. <code>unionByName</code> matches by name and, with <code>allowMissingColumns=True</code>, fills missing columns with null. Use <code>distinct()</code> after union for SQL UNION semantics.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Set operations</h2>
''' + table(['Method', 'SQL', 'Duplicates', 'Lab (x = 0..5, y = 3..8)'], [
    ['<code>union</code> / <code>unionAll</code>', 'UNION ALL', 'kept', '12 rows, 9 distinct'],
    ['<code>union().distinct()</code>', 'UNION', 'removed', '9'],
    ['<code>unionByName</code>', '—', 'kept', 'by name'],
    ['<code>intersect</code>', 'INTERSECT', 'removed', '[3, 4, 5]'],
    ['<code>intersectAll</code>', 'INTERSECT ALL', 'kept', ''],
    ['<code>subtract</code>', 'EXCEPT', 'removed', '[0, 1, 2]'],
    ['<code>exceptAll</code>', 'EXCEPT ALL', 'kept', '[1,1,2] − [1] = [1, 2]'],
], minw=640) + '''
WARN> <code>limit(n)</code> without <code>orderBy</code> returns <b>some</b> n rows, not the first n of a file or of any order. It is fine for a peek; it is wrong for “latest 10 orders”. Always pair a meaningful limit with an <code>orderBy</code>, and add a tiebreaker column if values can repeat.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Sorting 5 million orders and merging two feeds</h2>
  <p>All outputs are real: PySpark 4.3.0, local mode with 2 cores, <code>orders_big</code> (5,000,000 rows in Parquet, 2 partitions), 8 shuffle partitions. Timings write to the <code>noop</code> sink so that no output cost is included.</p>
''' + stepper([
    ('Step 1 · A global sort is a shuffle',
     code('python', 'l45_sort.py', 'big.orderBy(F.desc("amount")).write.format("noop").mode("overwrite").save()\nbig.sort("amount").write.format("noop").mode("overwrite").save()\nbig.sortWithinPartitions(F.desc("amount")).write.format("noop").mode("overwrite").save()\n# stages and shuffle bytes from the REST API', sec('== 1)', '== 2)')),
     '<code>orderBy</code> and <code>sort</code> are the same operation: 4 new stages (a sampling job to choose range boundaries, then the shuffle) and <b>120 MiB</b> written to shuffle files, 6.7–7.0 s. <code>sortWithinPartitions</code> kept every row on its executor: one stage, no shuffle, 2.0 s. Use it when each output file only needs to be sorted inside, for example before writing Parquet for better compression.'),
    ('Step 2 · Where nulls go',
     code('python', 'l45_sort.py', 'd = spark.createDataFrame([(1, 300), (2, None), (3, 120)], "id INT, amount INT")\nd.orderBy("amount"); d.orderBy(F.desc("amount")); d.orderBy(F.asc_nulls_last("amount"))\ndf.orderBy("city", F.desc("n"))', sec('== 2)', '== 3)')),
     'Ascending puts nulls <b>first</b>, descending puts them <b>last</b>: a “cheapest orders” report would start with the unknown ones. <code>asc_nulls_last</code>, <code>desc_nulls_first</code> and friends make it explicit. Multiple columns sort left to right, each with its own direction.'),
    ('Step 3 · limit and top-N',
     code('python', 'l45_sort.py', 'top = big.orderBy(F.desc("amount")).limit(5)\ntop.collect()\nbig.limit(5).collect()\ntop.explain()      # TakeOrderedAndProject', sec('== 3)', '== 4)')),
     'Top 5 of 5 million took <b>0.8 s with no shuffle</b>: the plan is <code>TakeOrderedAndProject</code>, which keeps the 5 largest rows per partition and merges them on the driver. A plain <code>limit(5)</code> (plan <code>CollectLimit</code>) read just enough to return five rows: 0.12 s. Compare with the 6.7 s full sort in Step 1.'),
    ('Step 4 · distinct and counting distinct values',
     code('python', 'l45_sort.py', 'big.select("customer_id").distinct().count()\nbig.select(F.countDistinct("customer_id")).first()\nbig.select(F.approx_count_distinct("customer_id")).first()', sec('== 4)', '== 5)')),
     'Both exact methods found 3,999 customers; both need a shuffle. <code>approx_count_distinct</code> (HyperLogLog, default 5% maximum error) said 3,985, 0.35% off. On billions of rows and in streaming the approximate version is much cheaper, because it shuffles small sketches instead of values.'),
    ('Step 5 · union matches by position',
     code('python', 'l45_sort.py', 'a = spark.createDataFrame([(1, "Pune", 450)], "order_id INT, city STRING, amount INT")\nb2 = spark.createDataFrame([(2, 380, "Delhi")], "order_id INT, amount INT, city STRING")\na.union(b2).show()                            # types differ\ns1 = …"order_id INT, city STRING, payment STRING"\ns2 = …"order_id INT, payment STRING, city STRING"\ns1.union(s2).show(); s1.unionByName(s2).show(); a.unionByName(b2).show()\na.unionByName(c); a.unionByName(c, allowMissingColumns=True)', sec('== 5)', '== 6)')),
     'When the types clash, union tried to cast <code>Pune</code> to a number and ANSI mode stopped it. When the types match, there is <b>no error</b>: <code>Card</code> landed in <code>city</code> and <code>Delhi</code> in <code>payment</code>, exactly the bug in our story. <code>unionByName</code> put every value in the right column; a missing column was an error until <code>allowMissingColumns=True</code> filled it with null.'),
    ('Step 6 · Duplicates and set operations',
     code('python', 'l45_sort.py', 'x = spark.range(0, 6, 1, 2); y = spark.range(3, 9, 1, 3)\nu = x.union(y); u.count(), u.distinct().count(), u.rdd.getNumPartitions()\nx.intersect(y); x.subtract(y)\nz.subtract(w); z.exceptAll(w)', sec('== 6)')),
     '<code>union</code> kept the overlapping 3, 4, 5 twice: 12 rows, 9 distinct. It did not shuffle; it simply concatenated the partitions, so 2 + 3 = <b>5 partitions</b>. Repeated unions of many small DataFrames therefore create many partitions (and long lineages, Lesson 3.3). <code>subtract</code> removed duplicates as well, <code>exceptAll</code> removed one copy per match.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('orderBy             : 6.7 s, 120 MiB', Y), ('sortWithinPartitions: 2.0 s, 0 MiB', G)], size=7.6),
    term([('asc            : [None, 120, 300]', W), ('desc           : [300, 120, None]', W), ('asc_nulls_last : [120, 300, None]', G)], size=7.4),
    term([('orderBy+limit(5): 0.8 s, no shuffle', G), ('plan: TakeOrderedAndProject', W), ('limit(5) only   : 0.12 s', G)], size=7.4),
    term([('countDistinct        : 3999', W), ('approx_count_distinct: 3985', Y)], size=7.6),
    term([('union      : 2 | Card | Delhi', RD), ('unionByName: 2 | Delhi | Card', G), ('union rows 12, partitions 5', W)], size=7.4),
]
B1 = [
    t(180, 14, 'Range shuffle for a global order', 9.4, bold=True) + parts(20, 40, ['530', '120', '840'], label='p1') + parts(20, 76, ['300', '760', '210'], label='p2') + arrow(140, 66, 196, 66, 'ink3', 1.1) + parts(204, 40, ['120', '210', '300'], 'green', label='low range') + parts(204, 76, ['530', '760', '840'], 'green', label='high range') + cap('Every row may move.', '', 'amber', y=144, h=30),
    t(180, 14, 'Nulls have a place', 9.4, bold=True) + parts(40, 50, ['null', '120', '300'], 'card', 60, 20, 'asc') + parts(40, 96, ['120', '300', 'null'], 'green', 60, 20, 'asc_nulls_last') + cap('Say where nulls go.', '', 'blue', y=144, h=30),
    t(180, 14, 'Top-k per partition', 9.4, bold=True) + parts(20, 40, ['840', '530'], 'green', label='p1 top') + parts(20, 76, ['760', '300'], 'green', label='p2 top') + arrow(110, 66, 190, 66, 'ink3', 1.1) + opbox(196, 52, 'driver', 'merge 4 rows', 'blue', 120, 30) + cap('No full sort, no shuffle.', '', 'green', y=144, h=30),
    t(180, 14, 'Distinct needs grouping', 9.4, bold=True) + flow([('values', '5M', 'card'), ('shuffle', 'by value', 'amber'), ('3,999', 'exact', 'green')], y=40, w=96, gap=22) + flow([('sketches', 'small', 'violet'), ('3,985', 'approx', 'violet')], y=90, w=96, gap=22) + cap('Exact or approximate.', '', 'violet', y=144, h=30),
    t(180, 14, 'Position, not name', 9.4, bold=True) + parts(20, 40, ['id', 'city', 'pay'], 'card', 50, 18, 'app') + parts(20, 82, ['id', 'pay', 'city'], 'acc', 50, 18, 'partner') + t(200, 60, 'union: col 2 = col 2', 7.6, 'red', anchor='start', mono=True) + t(200, 92, 'byName: city = city', 7.6, 'green', anchor='start', mono=True) + cap('Use unionByName for feeds.', '', 'red', y=144, h=30),
]
see_caps = ['The global sort shuffled 120 MiB.', 'Nulls first ascending, last descending.', 'Top 5 without sorting everything.', 'Exact vs approximate distinct.', 'union mixed columns silently.']
behind_caps = ['Range partitions, then local sorts.', 'Explicit null ordering.', 'TakeOrderedAndProject.', 'Aggregation or HyperLogLog sketches.', 'union ignores column names.']
two = anim_two('Sorting, distinct, limit and union', 'Order costs a shuffle; union trusts positions', 'Real lab outputs', 'What moves', see, B1, see_caps, behind_caps)

# ---- scenario 1: partner feed
e1 = (t(180, 22, 'App feed + partner feed', 9.4, bold=True) + t(180, 56, 'app.union(partner)', 8.4, 'ink', mono=True) + cap('Same column names.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'City report: “Card”, “UPI”', 9.4, bold=True) + t(180, 56, 'thousands of orders', 8.4, 'ink2') + cap('No error anywhere.', '', 'amber', y=150, h=34))
e3 = (t(180, 22, 'Partner order: payment, city', 9.4, bold=True) + t(180, 56, 'union matched by position', 8.4, 'ink2') + cap('Like our Step 5.', '', 'red', y=150, h=34))
e4 = (t(180, 22, 'unionByName', 9.4, bold=True) + t(180, 56, 'app.unionByName(partner)', 8.4, 'ink', mono=True) + cap('Columns matched by name.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Check values too', 9.4, 'acc', bold=True) + t(180, 56, 'city IN (known cities)', 8.4, 'ink', mono=True) + cap('Catch the next surprise.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Payment methods became cities',
              'union by position. (Behaviour from our lab.)',
              'union by position', 'union ignores names; same-typed columns in a different order are silently swapped; use unionByName', [e1, e2, e3, e4, e5],
              ['Two feeds.', 'Wrong report.', 'Positions differ.', 'unionByName.', 'Validate.'],
              hid='scenario-union')

# ---- scenario 2: sorted export
b1 = (t(180, 22, 'Nightly export sorted by date', 9.4, bold=True) + t(180, 56, 'df.orderBy("order_date").write…', 8.2, 'ink', mono=True) + cap('Takes 40 minutes.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Nobody needs a global order', 9.4, bold=True) + t(180, 56, 'files are read by date filter', 8.4, 'ink2') + cap('Only order inside files.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'sortWithinPartitions', 9.4, bold=True) + t(180, 56, 'no range shuffle', 8.4, 'ink2') + cap('6.7 s → 2.0 s in our lab.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Or partitionBy("order_date")', 9.4, bold=True) + t(180, 56, 'folders per date (Lesson 5.3)', 8.4, 'ink2') + cap('Pruning instead of sorting.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Sort only when it matters', 9.4, 'acc', bold=True) + t(180, 56, 'final reports, top-N', 8.4, 'ink2') + cap('Not by habit.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'A global sort nobody needed',
              'Avoiding unnecessary shuffles. (Timings from our lab.)',
              'Unneeded global sort', 'A global orderBy shuffles all data; sort within partitions or partition the output instead', [b1, b2, b3, b4, b5],
              ['Global sort.', 'Not needed.', 'Local sort.', 'Partition.', 'Sort on purpose.'],
              hid='scenario-sort')

# ---- scenario 3: dashboard distinct
u1 = (t(180, 22, 'Daily active users, every minute', 9.4, bold=True) + t(180, 56, 'countDistinct(user_id) on 2B events', 8.2, 'ink2') + cap('Cluster busy all day.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Exact distinct shuffles values', 9.4, bold=True) + t(180, 56, 'every user id moves', 8.4, 'ink2') + cap('Expensive.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'approx_count_distinct', 9.4, bold=True) + t(180, 56, 'rsd=0.01 for 1% error', 8.4, 'ink', mono=True) + cap('Sketches, not values.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Dashboard is fine with ±1%', 9.4, bold=True) + t(180, 56, 'our lab: 0.35% off', 8.4, 'ink2') + cap('Much cheaper.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Exact for billing', 9.4, 'acc', bold=True) + t(180, 56, 'once a day, countDistinct', 8.4, 'ink2') + cap('Right tool per question.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Exact counts nobody needed',
              'Approximate distinct counts. (Typical; accuracy from our lab.)',
              'Approximate distinct', 'HyperLogLog sketches estimate distinct counts cheaply; use exact counts only where they are required', [u1, u2, u3, u4, u5],
              ['Heavy query.', 'Shuffles values.', 'Approximate.', 'Good enough.', 'Exact for billing.'],
              hid='scenario-hll')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Order costs a shuffle; union trusts positions</h2>
  <p>Left: real outputs. Right: what moves between partitions.</p>
''' + two + '''
  <p>Three live scenarios follow: payment methods that became cities, a global sort nobody needed, and exact counts on a dashboard.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Sorting and combining at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'top-N', 12, 'blue', bold=True) + t(60, 58, 'reports', 7.4, 'ink2'),
    '1. Leaderboards',
    'Top restaurants, top cities and top customers are orderBy + limit: cheap top-k plans.',
    ['Aggregate', '*orderBy + limit', 'Top 10']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'feeds', 12, 'green', bold=True) + t(60, 58, 'merge', 7.4, 'ink2'),
    '2. Merging feeds',
    'Data from apps, partners and regions is combined with unionByName and allowMissingColumns.',
    ['Feeds', '*unionByName', 'One table']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'DAU', 12, 'violet', bold=True) + t(60, 58, 'HLL', 7.4, 'ink2'),
    '3. Active-user metrics',
    'Product dashboards use approx_count_distinct for daily and monthly active users.',
    ['Events', '*approx distinct', 'DAU']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'diff', 12, 'acc', bold=True) + t(60, 58, 'reconcile', 7.4, 'ink2'),
    '4. Reconciliation',
    'exceptAll between yesterday’s and today’s snapshots lists added and removed records.',
    ['Two snapshots', '*exceptAll', 'Differences']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'files', 12, 'acc', bold=True) + t(60, 58, 'sorted', 7.4, 'ink2'),
    '5. Better compressed files',
    'Data is sorted within partitions before writing Parquet so similar values compress well and min/max stats skip more.',
    ['DataFrame', '*sortWithinPartitions', 'Parquet']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> shuffles in <a href="../../02-rdds/04-narrow-vs-wide-and-the-shuffle/">2.4</a>, duplicates in <a href="../04-nulls-and-duplicates/">4.4</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
