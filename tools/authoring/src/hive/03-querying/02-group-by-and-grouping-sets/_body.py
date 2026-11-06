import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()

# ---------------------------------------------------------------- story
sc = (box(10, 12, 190, 128, 'card') + t(105, 30, '50,000 order rows', 9, bold=True) + ''.join(fill(22 + (k % 10) * 17, 42 + (k // 10) * 14, 13, 10, ['acc', 'blue', 'green', 'violet'][k % 4], rx=2) for k in range(50)) +
      arrow(204, 76, 240, 76, 'ink3', 2.2) + box(244, 12, 180, 128, 'acc') + t(334, 30, 'GROUP BY city', 9, bold=True, mono=True) +
      ''.join(t(256, 50 + k * 14, s, 7.6, anchor='start', mono=True) for k, s in enumerate(['Mumbai     10,014', 'Bengaluru   9,298', 'Pune        7,930', 'Hyderabad   5,979', '…  8 rows'])) +
      arrow(428, 76, 464, 76, 'ink3', 2.2) + box(468, 12, 162, 128, 'green') + t(549, 30, 'ROLLUP / CUBE', 9, bold=True, mono=True) +
      ''.join(t(478, 50 + k * 14, s, 7.6, anchor='start', mono=True) for k, s in enumerate(['city × payment', '+ city subtotals', '+ grand total', 'in ONE query'])))
scene_svg = scene('Fifty thousand order rows are grouped by city into eight summary rows, and ROLLUP adds subtotals and a grand total in the same query.', sc,
                  'GROUP BY turns <tspan font-weight="700" class="s-acc">many rows into one row per group</tspan>; ROLLUP adds the totals.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“I need city totals, payment totals and a grand total, in one table”</h2>
  <div class="story">
    <p class="narration">The monthly business review needs one table: orders per city and payment mode, a subtotal for each city and a grand total at the bottom. Kabir’s first idea is three queries glued together with UNION ALL. His second attempt fails with <code>Expression not in GROUP BY key 'payment'</code>.</p>

{scene_svg}

K> Sir, why can’t I just select payment next to city?
A> Because after <code>GROUP BY city</code> each output row stands for a <b>whole group</b> of orders. Pune has 7,930 orders with four different payment modes: which one should Hive print? Every selected column must either be a grouping key or an <b>aggregate</b> such as COUNT or SUM.
R> And the subtotals? Three queries?
A> One query. <code>GROUPING SETS</code>, <code>ROLLUP</code> and <code>CUBE</code> compute several groupings at once from a single scan. And we will look behind the screen: Hive pre-aggregates inside each map task, so instead of shuffling 50,000 rows it shuffles 8.
  </div>
</section>
'''

lv = '''
LEVELS> Grouping at three levels
L1> Sorting coins into piles
      <ul>
        <li><b>GROUP BY city</b> puts all orders of the same city into one pile.</li>
        <li>For each pile you can ask summary questions: how many (<code>COUNT</code>), total (<code>SUM</code>), average (<code>AVG</code>), smallest and largest (<code>MIN</code>, <code>MAX</code>).</li>
        <li><b>HAVING</b> throws away whole piles after counting (“only cities with more than 6,000 orders”). WHERE throws away single orders before piling.</li>
        <li><b>ROLLUP</b> adds a pile total and a grand total, like the last lines of a bill.</li>
      </ul>
L2> The rules
      <ul>
        <li>Every SELECT column must be in GROUP BY or inside an aggregate (error 10025 otherwise).</li>
        <li><code>COUNT(*)</code> counts rows; <code>COUNT(col)</code> skips NULLs; <code>COUNT(DISTINCT col)</code> counts unique values; Hive also allows <code>COUNT(DISTINCT a, b)</code>.</li>
        <li>Hive extras: <code>collect_set</code> (unique values as an array), <code>collect_list</code> (all values), <code>percentile_approx</code>, <code>variance</code>, <code>stddev_pop</code>, <code>corr</code>.</li>
        <li><code>GROUPING SETS ((a,b),(a),())</code> = several GROUP BYs in one query; <code>WITH ROLLUP</code> = hierarchy (a,b) → (a) → (); <code>WITH CUBE</code> = every combination.</li>
        <li>In subtotal rows the rolled-up column is NULL; <code>grouping(col)</code> = 1 tells you that NULL means “all”.</li>
      </ul>
L3> What happens on the cluster
      <ul>
        <li><b>Map-side aggregation</b> (<code>hive.map.aggr=true</code>, default): each map task keeps a hash table of partial results and sends one row per key. Our lab: 8 intermediate rows instead of 50,000.</li>
        <li>The reducer merges partial results (<code>mode: mergepartial</code> in EXPLAIN). Averages travel as (sum, count) pairs, never as averages.</li>
        <li><b>COUNT(DISTINCT)</b> needs every distinct value to reach a reducer; on huge data rewrite it as a GROUP BY in a subquery, or use an approximate function.</li>
        <li><b>Skew:</b> one giant key (a city with 80% of orders) overloads one reducer; <code>hive.groupby.skewindata=true</code> adds an extra stage that spreads it first.</li>
        <li><code>GROUP BY 1</code> (by position) works only with <code>hive.groupby.position.alias=true</code>; it is off by default (error 10025 in our lab).</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>GROUP BY, aggregates and grouping sets</h2>
''' + def_block(
    '<b>GROUP BY</b> partitions the rows that pass WHERE into groups with equal values of the grouping expressions and returns one row per group; the select list may contain only grouping expressions and <b>aggregate functions</b> (COUNT, SUM, AVG, MIN, MAX, collect_set, percentile_approx and others) computed over each group. <b>HAVING</b> filters groups after aggregation. <b>GROUPING SETS</b>, <b>ROLLUP</b> and <b>CUBE</b> compute several groupings in one query, with NULL in the columns that are aggregated away and the <code>GROUPING__ID</code> virtual column or <code>grouping()</code> function identifying each grouping.',
    'GROUP BY makes one result row per group and answers “how many, how much” for each. HAVING keeps only the groups you want. ROLLUP and CUBE add subtotal and total rows in the same query.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Aggregate function', 'Computes one value from many rows: COUNT, SUM, AVG, MIN, MAX.'),
    ('Grouping key', 'The column(s) in GROUP BY that define the groups.'),
    ('HAVING', 'A filter on groups, applied after aggregation, can use aggregates.'),
    ('Grouping set', 'One grouping inside GROUPING SETS, e.g. <code>(city)</code> or <code>()</code> for the grand total.'),
    ('ROLLUP', 'Hierarchical subtotals: (a,b), (a), ().'),
    ('CUBE', 'All combinations: (a,b), (a), (b), ().'),
    ('GROUPING__ID', 'A number per row saying which columns were rolled up (bit set = aggregated away).'),
    ('Map-side aggregation', 'Partial aggregation inside each map task before the shuffle.'),
]) + '''

  <h3>Aggregate functions you will use</h3>
''' + table(['Function', 'Returns', 'Note (tested in the lab)'], [
    ['<code>COUNT(*)</code> / <code>COUNT(col)</code>', 'Rows / non-NULL values', '50,000 / 50,000 for payment'],
    ['<code>COUNT(DISTINCT col)</code>', 'Unique values', '2,000 customers ordered'],
    ['<code>COUNT(DISTINCT a, b)</code>', 'Unique combinations', '32 city–payment pairs (8 × 4)'],
    ['<code>SUM</code>, <code>AVG</code>, <code>MIN</code>, <code>MAX</code>', 'Totals and extremes', 'SUM of DECIMAL(10,2) stays exact'],
    ['<code>collect_set(col)</code> / <code>collect_list(col)</code>', 'Array of unique / all values', 'Order inside the array is not guaranteed'],
    ['<code>percentile_approx(x, 0.5)</code>', 'Approximate median (DOUBLE)', 'Interpolated: 271.04 for Bengaluru'],
    ['<code>percentile(int_col, 0.5)</code>', 'Exact percentile', 'Integers only; memory-heavy'],
    ['<code>stddev_pop</code>, <code>variance</code>, <code>corr(a,b)</code>', 'Statistics', 'For quality checks and features'],
], minw=640) + lv + '''
EXAM> “Difference between WHERE and HAVING.” WHERE filters individual rows before grouping and cannot use aggregates; HAVING filters groups after aggregation and can, e.g. <code>HAVING COUNT(*) &gt; 6000</code>. Add an example of each in one query.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Four ways to summarise</h2>
''' + table(['Form', 'Groupings produced', 'Rows for 2 cities × 4 payments', 'Use for'], [
    ['<code>GROUP BY city, payment</code>', '(city, payment)', '8', 'One level of detail'],
    ['<code>GROUPING SETS ((city,payment),(city),())</code>', 'Exactly the sets you list', '8 + 2 + 1 = 11', 'Custom combinations'],
    ['<code>WITH ROLLUP</code>', '(city,payment), (city), ()', '11', 'Hierarchies: country → state → city'],
    ['<code>WITH CUBE</code>', '(city,payment), (city), (payment), ()', '8 + 2 + 4 + 1 = 15', 'Pivot-style reports, every subtotal'],
], minw=680) + cards([
    ('Group by an expression', 'Group by the CASE that labels size bands, or by <code>substr(order_ts,1,7)</code> for months. Repeat the expression in GROUP BY.', 'Buckets'),
    ('Filter groups with HAVING', '<code>HAVING COUNT(*) &gt; 6000</code> or <code>HAVING SUM(amount) &gt; 1000000</code>.', 'Thresholds'),
    ('Lists per group', '<code>collect_set(payment)</code> gives the modes each city uses in one array.', 'Hive special'),
    ('One scan, many reports', 'GROUPING SETS replaces several UNION ALL queries, each of which would scan the table again.', 'Efficient'),
]) + '''
TIP> When a grouping column can itself be NULL, a NULL in a ROLLUP row is ambiguous: real NULL or “all”? Use <code>grouping(col)</code> (1 = rolled up) and label it: <code>CASE WHEN grouping(city) = 1 THEN 'ALL CITIES' ELSE city END</code>.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Build the business review table</h2>
  <p>All outputs are real, from the Hive 4.2.1 lab on the curated <code>orders</code> table.</p>
''' + stepper([
    ('Step 1 · Aggregates per city',
     code('sql', 'Beeline', "SELECT city, COUNT(*) AS orders, SUM(amount) AS revenue,\n       ROUND(AVG(amount),2) AS avg_order, MIN(amount) AS min_amt, MAX(amount) AS max_amt\nFROM orders WHERE status = 'DELIVERED'\nGROUP BY city ORDER BY revenue DESC;", capf('l32_a.txt').split('+------------+---------+')[0].rstrip()),
     'WHERE removed cancelled and refunded orders first; then each city became one row. Mumbai leads with Rs 27.1 lakh from 9,249 delivered orders.'),
    ('Step 2 · Keep only big groups with HAVING',
     code('sql', 'Beeline', 'SELECT city, COUNT(*) AS orders FROM orders\nGROUP BY city HAVING COUNT(*) > 6000 ORDER BY orders DESC;',
          '+------------+---------+\n|    city    | orders  |\n+------------+---------+\n| Mumbai     | 10014   |\n| Bengaluru  | 9298    |\n| Pune       | 7930    |\n+------------+---------+'),
     'HAVING runs after grouping and can use COUNT(*). Writing <code>WHERE COUNT(*) &gt; 6000</code> would fail: WHERE sees single rows, not groups.'),
    ('Step 3 · The classic error',
     code('sql', 'Beeline', 'SELECT city, payment, COUNT(*) FROM orders GROUP BY city;', capf('l32_a.txt').split('Error: ')[1].split('; Query ID')[0].join(['Error: ', ''])),
     'payment is neither grouped nor aggregated, so Hive cannot know which value to print. Add it to GROUP BY, aggregate it (<code>collect_set(payment)</code>) or remove it.'),
    ('Step 4 · Counting in different ways',
     code('sql', 'Beeline', 'SELECT COUNT(*) AS rows_, COUNT(payment) AS non_null_payment,\n       COUNT(DISTINCT customer_id) AS customers,\n       COUNT(DISTINCT city, payment) AS city_pay_pairs FROM orders;\nSELECT city, collect_set(payment) AS pay_modes, size(collect_list(order_id)) AS n\nFROM orders WHERE city IN (\'Chennai\',\'Thane\') GROUP BY city;',
          capf('l32_aggs.txt').split('+------------+---------------------+')[0].rstrip()),
     'All 2,000 customers ordered at least once; 8 cities × 4 modes = 32 pairs all occur. <code>collect_set</code> returns an array of unique values, in no guaranteed order (compare the two rows).'),
    ('Step 5 · Medians and spread',
     code('sql', 'Beeline', 'SELECT city, percentile_approx(CAST(amount AS DOUBLE), 0.5) AS median_amt,\n       percentile_approx(CAST(amount AS DOUBLE), 0.9) AS p90,\n       ROUND(stddev_pop(amount),2) AS sd\nFROM orders GROUP BY city ORDER BY city LIMIT 3;',
          '+------------+---------------------+---------------------+---------+\n|    city    |     median_amt      |         p90         |   sd    |\n+------------+---------------------+---------------------+---------+\n| Bengaluru  | 271.04046242774564  | 508.96470588235303  | 158.46  |\n| Chennai    | 274.6875            | 521.6818181818184   | 163.13  |\n| Delhi      | 275.30973451327435  | 517.7647058823529   | 161.41  |\n+------------+---------------------+---------------------+---------+'),
     'Amounts are multiples of 10, yet the median is 271.04: <code>percentile_approx</code> builds a histogram and <b>interpolates</b>. It is fast and memory-light; round it for reports, or use exact <code>percentile()</code> on integer columns.'),
    ('Step 6 · Subtotals and a grand total with ROLLUP',
     code('sql', 'Beeline', "SELECT city, payment, COUNT(*) AS n, GROUPING__ID AS gid,\n       grouping(city) AS g_city, grouping(payment) AS g_pay\nFROM orders WHERE city IN ('Pune','Thane')\nGROUP BY city, payment WITH ROLLUP\nORDER BY gid, city, payment;", capf('l32_sets.txt').split('| NULL   | NULL     | 12750  |\n+--------+----------+--------+\n')[1]),
     'One query, three levels: 8 detail rows (gid 0), 2 city subtotals (gid 1, payment rolled up) and 1 grand total (gid 3). 7,930 + 4,820 = 12,750. <code>grouping()</code> marks which NULLs mean “all”.'),
    ('Step 7 · Every combination with CUBE',
     code('sql', 'Beeline', "SELECT payment, status, COUNT(*) AS n FROM orders WHERE city = 'Chennai'\nGROUP BY payment, status WITH CUBE ORDER BY payment, status;",
          '\n'.join(capf('l32_cube.txt').split('\n')[:7]) + '\n… (Card, UPI and Wallet rows)\n' + '\n'.join(capf('l32_cube.txt').split('\n')[-6:])),
     'CUBE adds subtotals in <b>both</b> directions: per payment (status NULL) and per status (payment NULL), plus the total 2,523. 20 rows from one scan, ready for a pivot table.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
def task_box(x, y, title, rows, tone):
    o = box(x, y, 100, 18 + 12 * len(rows), tone) + t(x + 50, y + 12, title, 7.6, bold=True)
    for k, r in enumerate(rows):
        o += t(x + 6, y + 26 + k * 12, r, 7, 'ink', anchor='start', mono=True)
    return o
see = [
    term([('> SELECT city, COUNT(*) FROM orders', W), ('  GROUP BY city;', W), ('(three map tasks would each read part', Y), (' of the 50,000 rows on a real cluster)', Y)]),
    term([('> SET hive.map.aggr=true;   -- default', W), ('RECORDS_IN_Map_1: 50000', G), ('RECORDS_OUT_INTERMEDIATE_Map_1: 8', G)]),
    term([('> SET hive.map.aggr=false;', W), ('RECORDS_IN_Map_1: 50000', G), ('RECORDS_OUT_INTERMEDIATE_Map_1: 50000', RD)]),
    term([('| Mumbai     | 10014 |', G), ('| Bengaluru  | 9298  |', G), ('| Pune       | 7930  |', G), ('| …          |       |', G), ('8 rows selected (1.194 seconds)', Y)]),
    term([('> … GROUP BY city, payment WITH ROLLUP', W), ('| Pune  | COD  |  783 | 0 |', G), ('| …                       |', G), ('| Pune  | NULL | 7930 | 1 |', Y), ('| Thane | NULL | 4820 | 1 |', Y), ('| NULL  | NULL |12750 | 3 |', Y)]),
]
B1 = [
    t(180, 22, 'Rows are spread over map tasks', 9.4, bold=True) + task_box(10, 44, 'Map task 1', ['Pune', 'Thane', 'Pune', '…'], 'acc') + task_box(130, 44, 'Map task 2', ['Mumbai', 'Pune', 'Thane', '…'], 'acc') + task_box(250, 44, 'Map task 3', ['Thane', 'Mumbai', 'Pune', '…'], 'acc') +
    cap('Each task reads its own split.', '(our lab file is small: one task)', 'card', y=160, h=46),
    t(180, 22, 'Map-side aggregation: one row per city per task', 9.2, 'green', bold=True) + task_box(10, 44, 'Map task 1', ['Pune 2,611', 'Thane 1,602', '…'], 'green') + task_box(130, 44, 'Map task 2', ['Pune 2,660', 'Mumbai 3,340', '…'], 'green') + task_box(250, 44, 'Map task 3', ['Pune 2,659', 'Thane 1,610', '…'], 'green') +
    cap('Hash table of partial counts (mode: hash).', 'Only a few rows go into the shuffle.', 'green', y=160, h=46),
    t(180, 22, 'Without it: every row is shuffled', 9.4, 'red', bold=True) + ''.join(fill(20 + (k % 24) * 13, 48 + (k // 24) * 12, 10, 8, 'red', rx=1) for k in range(144)) + t(180, 140, '50,000 rows cross the network', 8.6, 'red', bold=True) +
    cap('Same answer, far more network traffic.', '', 'red', y=160, h=34),
    t(180, 22, 'Reducer merges partial results', 9.4, bold=True) + label_box(14, 46, 150, 70, ['Reducer 2', 'Pune: 2,611 + 2,660 + 2,659', '= 7,930'], 'blue', 7.8) + arrow(166, 81, 196, 81, 'green', 2) + label_box(198, 46, 150, 70, ['Result', '8 rows, one per city'], 'green', 8.4) +
    cap('mode: mergepartial. Averages travel as (sum, count).', '', 'blue', y=160, h=34),
    t(180, 22, 'ROLLUP = three groupings in one pass', 9.4, bold=True) + ''.join(label_box(14 + k * 114, 46, 104, 66, [a, b, c], tone, 7.6) for k, (a, b, c, tone) in enumerate([('(city, payment)', 'gid 0', '8 rows', 'acc'), ('(city)', 'gid 1', '2 rows', 'blue'), ('()', 'gid 3', '1 row', 'green')])) +
    cap('Rolled-up columns are NULL; grouping() says so.', '', 'blue', y=160, h=34),
]
see_caps = ['Kabir counts orders per city. On a real cluster several map tasks share the 50,000 rows.',
            'With map-side aggregation on (the default), only 8 intermediate rows leave the map stage.',
            'With it switched off, all 50,000 rows go to the shuffle.',
            'Either way the answer is the same: 8 cities.',
            'ROLLUP adds two city subtotals and a grand total of 12,750 to the 8 detail rows.']
behind_caps = ['Each map task reads part of the table (here the file is small, so one task does it all). Per-task numbers below are illustrative.',
               'Each task keeps a hash table and emits one partial count per city, so very few rows are shuffled.',
               'Without partial aggregation every row is sent to the reducers.',
               'The reducer adds the partial counts for each city and produces one row per city.',
               'Hive computes the three groupings from one scan and marks rolled-up columns with grouping() and GROUPING__ID.']
two = anim_two('Inside GROUP BY', 'How 50,000 rows become 8', 'Real Beeline output and counters', 'Map tasks, partial aggregation and the reducer', see, B1, see_caps, behind_caps)

# ---- scenario 1: UNION ALL vs GROUPING SETS
u1 = (t(180, 22, 'The old report: three queries', 9.6, bold=True) + ''.join(t(26, 52 + k * 18, s, 8, 'ink', anchor='start', mono=True) for k, s in enumerate(['SELECT city, payment, COUNT(*) … GROUP BY city, payment', 'UNION ALL', 'SELECT city, NULL, COUNT(*) … GROUP BY city', 'UNION ALL', 'SELECT NULL, NULL, COUNT(*) …'])) +
      cap('Three scans of the same table.', '', 'amber', y=160, h=34))
u2 = (t(180, 22, 'The new report: one query', 9.6, 'green', bold=True) + t(180, 60, 'GROUP BY city, payment', 8.6, 'ink', mono=True) + t(180, 76, 'GROUPING SETS ((city, payment), (city), ())', 8.6, 'ink', mono=True) + cap('One scan, same rows.', '', 'green', y=160, h=34))
u3 = (t(180, 22, 'Scan cost on a 2 TB table', 9.6, bold=True) + bars([('UNION ALL', 100, 'red', '3 × 2 TB'), ('GROUPING SETS', 33, 'green', '1 × 2 TB')], y=56) + cap('Two thirds of the reading saved.', '(illustrative)', 'green', y=160, h=46))
u4 = (t(180, 22, 'Label the totals', 9.6, bold=True) + t(180, 56, "CASE WHEN grouping(city)=1 THEN 'ALL' ELSE city END", 8, 'ink', mono=True) + cap('Business users never see a mysterious NULL.', '', 'blue', y=160, h=34))
u5 = (t(180, 22, 'Check: parts add up', 9.6, 'acc', bold=True) + t(180, 56, 'Pune 7,930 + Thane 4,820 = 12,750 (grand total row)', 8.4, 'ink2') + cap('Real numbers from our ROLLUP.', '', 'green', y=160, h=34))
s1 = anim_one('Real-time scenario 1', 'Replacing UNION ALL reports with GROUPING SETS',
              'Many old reports stack several GROUP BY queries. One query does the same work in one scan.',
              'Grouping sets', 'Three UNION ALL queries scanning a table three times replaced by one GROUPING SETS query', [u1, u2, u3, u4, u5],
              ['An old report computes detail, subtotals and the total with three queries joined by UNION ALL.',
               'GROUPING SETS lists the three groupings in one query.',
               'The table is read once instead of three times.',
               'grouping() lets you show “ALL” instead of NULL in total rows.',
               'Verify that subtotals add up to the grand total.'],
              hid='scenario-sets')

# ---- scenario 2: skewed group
k1 = (t(180, 22, 'GROUP BY restaurant_id: one reducer is slow', 9.4, bold=True) + ''.join(fill(30 + k * 56, 120 - h, 40, h, 'red' if k == 2 else 'green') for k, h in enumerate([20, 24, 90, 22, 18])) + t(180, 136, 'one chain restaurant has 40% of all orders', 8.4, 'red', bold=True) +
      cap('All its rows go to one reducer.', '(illustrative)', 'red', y=160, h=46))
k2 = (t(180, 22, 'Map-side aggregation helps first', 9.6, 'green', bold=True) + t(180, 56, 'each map task sends ONE partial count for the big key', 8.4, 'ink2') + cap('For COUNT/SUM, skew is mostly absorbed.', '', 'green', y=160, h=34))
k3 = (t(180, 22, 'It still hurts for COUNT(DISTINCT customer_id)', 9.2, 'red', bold=True) + t(180, 56, 'every distinct customer of the big restaurant', 8.4, 'ink2') + t(180, 72, 'must reach the same reducer', 8.4, 'ink2') + cap('Distinct values cannot be pre-summed.', '', 'red', y=160, h=34))
k4 = (t(180, 22, 'Fixes', 9.6, 'green', bold=True) + ''.join(t(26, 52 + k * 19, s, 8.2, anchor='start', mono=True) for k, s in enumerate(['SET hive.groupby.skewindata=true;', 'GROUP BY in a subquery, then COUNT(*)', 'approximate distinct counts', 'handle the hot key separately'])) +
      cap('Two-stage aggregation spreads the hot key.', '', 'green', y=160, h=34))
k5 = (t(180, 22, 'Rewrite pattern', 9.6, 'acc', bold=True) + t(180, 52, 'SELECT restaurant_id, COUNT(*) FROM (', 8, 'ink', mono=True) + t(180, 66, '  SELECT restaurant_id, customer_id FROM orders', 8, 'ink', mono=True) + t(180, 80, '  GROUP BY restaurant_id, customer_id) t', 8, 'ink', mono=True) + t(180, 94, 'GROUP BY restaurant_id;', 8, 'ink', mono=True) +
      cap('Same answer as COUNT(DISTINCT), better spread.', '', 'blue', y=160, h=34))
s2 = anim_one('Real-time scenario 2', 'One huge group slows the whole job',
              'Skew is the most common GROUP BY performance problem. See when map-side aggregation saves you and when it does not.',
              'Skewed groups', 'One restaurant with a large share of orders overloads a reducer; skew settings and query rewrites spread the work', [k1, k2, k3, k4, k5],
              ['One key holds a large share of rows, so the reducer that receives it runs much longer.',
               'For COUNT and SUM, map-side aggregation shrinks that key to a few partial rows.',
               'COUNT(DISTINCT) cannot be pre-summed, so the hot key still lands on one reducer.',
               'Use the skew setting, a two-level GROUP BY, approximate counts or special handling of the hot key.',
               'The two-level rewrite gives the same answer as COUNT(DISTINCT) with better parallelism.'],
              hid='scenario-skew')

# ---- scenario 3: approximate vs exact
a1 = (t(180, 22, 'Median order value per city', 9.6, bold=True) + t(180, 56, 'percentile_approx(amount, 0.5) → 271.04 (Bengaluru)', 8.4, 'ink', mono=True) + cap('But every amount is a multiple of 10!', '', 'amber', y=160, h=34))
a2 = (t(180, 22, 'Why a fraction?', 9.6, bold=True) + t(180, 56, 'a histogram of bins, then interpolation between them', 8.4, 'ink2') + cap('Approximate, fast, bounded memory.', '', 'blue', y=160, h=34))
a3 = (t(180, 22, 'Exact alternative', 9.6, bold=True) + t(180, 56, 'percentile(CAST(amount AS INT), 0.5)', 8.6, 'ink', mono=True) + t(180, 76, 'keeps every value of the group in memory', 8.4, 'ink2') + cap('Exact, but risky for huge groups.', '', 'amber', y=160, h=34))
a4 = (t(180, 22, 'More accuracy', 9.6, bold=True) + t(180, 56, 'percentile_approx(x, 0.5, 100000)  -- more bins', 8.4, 'ink', mono=True) + cap('Trade memory for precision.', '', 'blue', y=160, h=34))
a5 = (t(180, 22, 'For reports', 9.6, 'acc', bold=True) + t(180, 56, 'ROUND(percentile_approx(…), 0) and say “approx.”', 8.4, 'ink2') + cap('Tell readers when a number is approximate.', '', 'green', y=160, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Approximate medians: why 271.04?',
              'Percentiles on big data are usually approximate. Our lab result shows why the answer can be a value that never occurs.',
              'Percentiles', 'percentile_approx interpolates a median of 271.04 for amounts that are multiples of 10; exact percentile and accuracy settings compared', [a1, a2, a3, a4, a5],
              ['percentile_approx returned 271.04 for Bengaluru although every amount is a multiple of 10.',
               'It builds a compact histogram and interpolates between bins.',
               'Exact percentile() works on integer columns but holds all values of a group in memory.',
               'A larger accuracy argument gives more bins and a closer answer.',
               'Round approximate results and label them in reports.'],
              hid='scenario-percentile')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>From 50,000 rows to 8, and then to subtotals</h2>
  <p>Left: real Beeline output and Tez counters. Right: what the map tasks and the reducer do.</p>
''' + two + '''
  <p>Three live scenarios follow: grouping sets instead of UNION ALL, skewed groups, and approximate percentiles.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Grouping in daily analytics</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'GMV / day', 9, 'acc', bold=True) + t(60, 58, 'GROUP BY date', 7.4, 'ink2'),
    '1. Daily KPI tables',
    'Every morning a job groups yesterday’s orders by city and category to produce GMV, order count and average order value for the dashboards.',
    ['Orders', '*GROUP BY', 'KPI table']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'ROLLUP', 9, 'green', bold=True, mono=True) + t(60, 58, 'state → city', 7.4, 'ink2'),
    '2. Hierarchical sales reports',
    'Regional managers want state, city and outlet totals in one sheet. ROLLUP produces all levels with one scan.',
    ['Sales', '*ROLLUP', 'Report']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'HAVING', 9, 'violet', bold=True, mono=True) + t(60, 58, 'fraud rules', 7.4, 'ink2'),
    '3. Fraud and abuse rules',
    'Find accounts with more than 20 refunds in a week, or cards used in more than 5 cities in a day: GROUP BY the account with HAVING on the count.',
    ['Transactions', '*GROUP BY … HAVING', 'Alerts']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'CUBE', 10, 'blue', bold=True, mono=True) + t(60, 58, 'pivot data', 7.4, 'ink2'),
    '4. Pivot tables for BI tools',
    'A CUBE over payment mode and status produces every subtotal a pivot table needs, so the BI tool does not re-aggregate raw rows.',
    ['Orders', '*CUBE', 'Pivot']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'p50 · p90', 9, 'acc', bold=True) + t(60, 58, 'delivery times', 7.4, 'ink2'),
    '5. Service-level monitoring',
    'Operations tracks median and 90th-percentile delivery times per city with percentile_approx, because averages hide the slow tail.',
    ['Deliveries', '*percentile_approx', 'SLA dashboard']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> you should be comfortable with SELECT and WHERE (<a href="../01-select-where-and-functions/">Lesson 3.1</a>). Partial aggregation was introduced in <a href="../../01-introduction/04-how-a-hive-query-becomes-a-job/">Lesson 1.4</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
