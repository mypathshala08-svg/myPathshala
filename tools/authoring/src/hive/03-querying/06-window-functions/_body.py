import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()

# ---------------------------------------------------------------- story
sc = (box(10, 12, 300, 128, 'card') + t(160, 30, 'GROUP BY city: rows collapse', 8.8, bold=True) +
      ''.join(fill(24 + (k % 10) * 26, 44 + (k // 10) * 16, 20, 12, 'acc', rx=2) for k in range(30)) + arrow(160, 96, 160, 112, 'ink3', 2) + box(110, 114, 100, 20, 'acc') + t(160, 128, '1 row per city', 7.8, bold=True) +
      box(330, 12, 300, 128, 'green') + t(480, 30, 'OVER (PARTITION BY city): rows stay', 8.8, 'green', bold=True) +
      ''.join(fill(344 + (k % 10) * 26, 44 + (k // 10) * 16, 20, 12, 'green', rx=2) + t(354 + (k % 10) * 26, 54 + (k // 10) * 16, str(k % 10 + 1), 6.4, 'ink', bold=True) for k in range(30)) +
      t(480, 128, 'every row gets its rank, total, previous…', 7.8, 'ink2'))
scene_svg = scene('GROUP BY collapses rows into one per city, while a window function keeps every row and adds a value computed over its city, such as a rank.', sc,
                  'Window functions <tspan font-weight="700" class="s-acc">keep every row</tspan> and add a value computed over its group.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Top 3 customers in every city, a running total and the gap since the last order”</h2>
  <div class="story">
    <p class="narration">The growth team sends Kabir three requests on one morning: the top three customers per city for a loyalty campaign; Pune’s daily revenue with a running total and a 7-day average; and, for each order, how many hours since the same customer’s previous order. With GROUP BY he can get totals per city, but then the individual customers disappear.</p>

{scene_svg}

K> Sir, GROUP BY gives me one row per city. I need every customer row, plus its rank inside its city.
A> That is exactly what <b>window functions</b> do. You write a function, then <code>OVER (PARTITION BY city ORDER BY …)</code>. Hive looks at all rows of the same city, in that order, computes the value, and writes it next to each row. Nothing collapses.
R> And “previous order” means looking at the row before?
A> <code>LAG</code> looks back, <code>LEAD</code> looks ahead, inside the window. A <b>frame</b> like <code>ROWS BETWEEN 6 PRECEDING AND CURRENT ROW</code> gives a moving 7-day average. Today all three requests, on real data, plus two traps: the default frame of LAST_VALUE, and a QUALIFY behaviour we found in Hive 4.2.1.
  </div>
</section>
'''

lv = '''
LEVELS> Window functions at three levels
L1> A class register with extra columns
      <ul>
        <li>Imagine the class list sorted by marks inside each section. Next to each student you can write: their rank in the section, the section total, the marks of the student just above.</li>
        <li>Each student keeps their own line; you only <b>add</b> information computed from their section. That is a window function.</li>
        <li>The <b>section</b> is the PARTITION; the <b>order of names</b> is the ORDER BY; the rows you look at for each student (“the 7 above me”) are the FRAME.</li>
      </ul>
L2> The families and the OVER clause
      <ul>
        <li><b>Ranking:</b> <code>ROW_NUMBER()</code> (1, 2, 3, 4 … always unique), <code>RANK()</code> (ties share, then gaps: 6, 6, 6, 9), <code>DENSE_RANK()</code> (ties share, no gaps: 6, 6, 6, 7), <code>NTILE(n)</code>, <code>PERCENT_RANK()</code>, <code>CUME_DIST()</code>.</li>
        <li><b>Offset:</b> <code>LAG(col, n, default)</code>, <code>LEAD(col, n, default)</code>, <code>FIRST_VALUE</code>, <code>LAST_VALUE</code>.</li>
        <li><b>Aggregates as windows:</b> <code>SUM/AVG/COUNT/MIN/MAX(…) OVER (…)</code>: running totals, moving averages, shares of a group total.</li>
        <li><code>OVER (PARTITION BY … ORDER BY … [ROWS|RANGE BETWEEN … AND …])</code>; reuse a definition with <code>WINDOW w AS (…)</code> and <code>OVER w</code>.</li>
      </ul>
L3> Frames, evaluation order and Hive specifics
      <ul>
        <li><b>Default frame:</b> with ORDER BY it is <code>RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW</code> (that is why SUM gives a running total and LAST_VALUE returns the current row); without ORDER BY it is the whole partition.</li>
        <li>Ranking functions and LAG/LEAD take no frame.</li>
        <li>Windows are computed <b>after</b> WHERE, GROUP BY and HAVING, so you cannot filter on them in WHERE (error 10002 in our lab); filter in an outer query, or with <code>QUALIFY</code>.</li>
        <li><b>QUALIFY in Hive 4.2.1:</b> it filtered correctly alone, but in our tests <b>QUALIFY together with ORDER BY</b> in the same query returned unfiltered rows (50,000 instead of 8). Until you have verified your version, prefer the subquery form <code>SELECT … FROM (… ROW_NUMBER() … AS rn) x WHERE rn = 1</code>.</li>
        <li>Windows over aggregates are allowed: <code>SUM(COUNT(*)) OVER (PARTITION BY city)</code> gives shares in one query.</li>
        <li>Execution: rows are shuffled by the partition key and sorted by the order key, then a PTF (partitioned table function) operator computes the values. Huge partitions (skew) are expensive.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Window (analytic) functions</h2>
''' + def_block(
    'A <b>window function</b> computes a value for each row from a set of related rows, its <b>window</b>, defined by the <code>OVER</code> clause: <code>PARTITION BY</code> divides rows into groups, <code>ORDER BY</code> orders rows within each partition, and an optional <b>frame</b> (<code>ROWS</code> or <code>RANGE BETWEEN … AND …</code>) limits the rows considered relative to the current row. Unlike GROUP BY, window functions do not reduce the number of rows. Hive provides ranking functions (ROW_NUMBER, RANK, DENSE_RANK, NTILE, PERCENT_RANK, CUME_DIST), offset functions (LAG, LEAD, FIRST_VALUE, LAST_VALUE) and aggregate functions used with OVER.',
    'A window function looks at a group of rows around each row (same city, earlier days…) and writes a result next to that row: a rank, a running total, the previous value. Every row stays in the result.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Window', 'The set of rows a function sees for the current row.'),
    ('PARTITION BY', 'Splits rows into independent groups (each city on its own).'),
    ('ORDER BY (in OVER)', 'The order inside each partition, used for ranks, running totals and LAG/LEAD.'),
    ('Frame', 'Which rows of the partition count, e.g. the 6 rows before and the current one.'),
    ('Running total', '<code>SUM(x) OVER (ORDER BY day)</code>: total from the first row to this one.'),
    ('Moving average', '<code>AVG(x) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)</code>.'),
    ('Top-N per group', 'ROW_NUMBER in a subquery, then <code>WHERE rn &lt;= N</code>.'),
    ('QUALIFY', 'A clause that filters on window results, like HAVING does for aggregates.'),
]) + '''

  <h3>Ranking functions on real ties (Chennai customers, orders placed)</h3>
''' + table(['n_orders', 'ROW_NUMBER', 'RANK', 'DENSE_RANK', 'Note'], [
    ['34', '5', '5', '5', ''],
    ['33', '6', '6', '6', 'Three customers tie at 33'],
    ['33', '7', '6', '6', 'ROW_NUMBER still increases'],
    ['33', '8', '6', '6', ''],
    ['32', '9', '9', '7', 'RANK jumps to 9, DENSE_RANK continues with 7'],
], minw=560) + lv + '''
EXAM> “Difference between RANK, DENSE_RANK and ROW_NUMBER.” Show one tie: ROW_NUMBER 6, 7, 8 (unique); RANK 6, 6, 6 then 9 (gaps); DENSE_RANK 6, 6, 6 then 7 (no gaps). Then write a top-3-per-group query with ROW_NUMBER in a subquery.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Common window patterns</h2>
''' + table(['Pattern', 'Write', 'Business use'], [
    ['Top-N per group', '<code>ROW_NUMBER() OVER (PARTITION BY city ORDER BY spend DESC)</code> then <code>rn &lt;= 3</code>', 'Loyalty campaigns, best sellers'],
    ['De-duplicate (latest per key)', '<code>ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC) = 1</code>', 'Clean CDC / duplicate events'],
    ['Running total', '<code>SUM(revenue) OVER (ORDER BY day)</code>', 'Month-to-date revenue'],
    ['Moving average', '<code>AVG(revenue) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)</code>', 'Smooth daily noise'],
    ['Change vs previous', '<code>revenue - LAG(revenue) OVER (ORDER BY day)</code>', 'Day-on-day growth'],
    ['Time since last event', '<code>ts - LAG(ts) OVER (PARTITION BY customer ORDER BY ts)</code>', 'Churn, sessions, fraud'],
    ['Share of group', '<code>COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY city)</code>', 'Payment mix per city'],
    ['Buckets / percentiles', '<code>NTILE(4)</code>, <code>PERCENT_RANK()</code>, <code>CUME_DIST()</code>', 'Quartiles, customer tiers'],
], minw=720) + '''
WARN> <code>LAST_VALUE(x) OVER (ORDER BY …)</code> usually returns the <b>current</b> row’s value, not the last one, because the default frame ends at the current row. Write <code>ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING</code> when you mean the last row of the partition (shown in Step 5).
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>The growth team’s three requests, and two traps</h2>
  <p>All outputs are real, from the Hive 4.2.1 lab.</p>
''' + stepper([
    ('Step 1 · Rank customers inside each city',
     code('sql', 'Beeline', "WITH c AS (SELECT city, customer_id, COUNT(*) AS n_orders\n           FROM orders GROUP BY city, customer_id)\nSELECT * FROM (\n  SELECT city, customer_id, n_orders,\n    ROW_NUMBER() OVER (PARTITION BY city ORDER BY n_orders DESC, customer_id) AS rn,\n    RANK()       OVER (PARTITION BY city ORDER BY n_orders DESC) AS rnk,\n    DENSE_RANK() OVER (PARTITION BY city ORDER BY n_orders DESC) AS drnk\n  FROM c WHERE city = 'Chennai') x\nWHERE rn BETWEEN 6 AND 10 ORDER BY rn;", tables(capf('l36_rank2_running.txt'))[0]),
     'Three customers tie at 33 orders. ROW_NUMBER breaks the tie (by customer_id, so it is repeatable); RANK gives 6, 6, 6 and jumps to 9; DENSE_RANK continues with 7. Window functions run on the grouped rows of the CTE.'),
    ('Step 2 · Top 1 per city: the subquery pattern',
     code('sql', 'Beeline', "SELECT * FROM (\n  SELECT order_id, city, amount,\n         ROW_NUMBER() OVER (PARTITION BY city ORDER BY amount DESC, order_id) AS rn\n  FROM orders WHERE order_id < 100020) x\nWHERE rn = 1 ORDER BY city;",
          '+-------------+------------+-----------+-------+\n| x.order_id  |   x.city   | x.amount  | x.rn  |\n+-------------+------------+-----------+-------+\n| 100013      | Bengaluru  | 340.00    | 1     |\n| 100007      | Delhi      | 310.00    | 1     |\n| 100008      | Hyderabad  | 360.00    | 1     |\n| 100009      | Mumbai     | 590.00    | 1     |\n| 100006      | Pune       | 460.00    | 1     |\n| 100019      | Thane      | 320.00    | 1     |\n+-------------+------------+-----------+-------+'),
     'The biggest order per city among the first 19 orders. Change <code>rn = 1</code> to <code>rn &lt;= 3</code> for the top three. This form works in every Hive version and every SQL engine.'),
    ('Step 3 · Running total, moving average, change vs previous day',
     code('sql', 'Beeline', "WITH d AS (SELECT order_date, SUM(amount) AS revenue FROM orders\n           WHERE city = 'Pune' GROUP BY order_date)\nSELECT order_date, revenue,\n  SUM(revenue) OVER (ORDER BY order_date) AS running_total,\n  ROUND(AVG(revenue) OVER (ORDER BY order_date\n        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2) AS avg_7d,\n  revenue - LAG(revenue) OVER (ORDER BY order_date) AS change_vs_prev\nFROM d ORDER BY order_date LIMIT 8;", tables(capf('l36_rank2_running.txt'))[1]),
     'Each day keeps its own row. running_total adds up from 1 October; avg_7d averages up to the last 7 days (fewer at the start); LAG gives NULL on the first day because there is no previous row.'),
    ('Step 4 · Gap since the customer’s previous order, and shares',
     code('sql', 'Beeline', "SELECT customer_id, order_ts,\n  LAG(order_ts) OVER (PARTITION BY customer_id ORDER BY order_ts) AS prev_ts,\n  ROUND((unix_timestamp(order_ts) - unix_timestamp(\n     LAG(order_ts) OVER (PARTITION BY customer_id ORDER BY order_ts))) / 3600, 1) AS gap_hours\nFROM orders WHERE customer_id = 1492 ORDER BY order_ts LIMIT 4;\n\nSELECT city, payment, COUNT(*) AS n,\n  ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY city), 1) AS pct\nFROM orders WHERE city = 'Thane' GROUP BY city, payment ORDER BY n DESC;",
          tables(capf('l36_lag_share.txt'))[0] + '\n' + tables(capf('l36_lag_share.txt'))[1]),
     'Customer 1492 came back after 90.1 hours, then twice more the same day. In the second query the window runs over the grouped counts: <code>SUM(COUNT(*)) OVER (PARTITION BY city)</code> is Thane’s total, so UPI is 60.5% of Thane’s orders.'),
    ('Step 5 · Trap: the default frame of LAST_VALUE',
     code('sql', 'Beeline', "SELECT order_id, amount,\n  FIRST_VALUE(amount) OVER w AS first_amt,\n  LAST_VALUE(amount)  OVER w AS last_default,\n  LAST_VALUE(amount)  OVER (ORDER BY order_id\n     ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_full\nFROM orders WHERE order_id < 100005\nWINDOW w AS (ORDER BY order_id) ORDER BY order_id;", capf('l36_lastvalue.txt')),
     'With the default frame (up to the current row) LAST_VALUE simply echoes each row’s amount. Only the explicit full frame returns 180.00, the real last value. The named <code>WINDOW w</code> avoids repeating the same OVER definition.'),
    ('Step 6 · Trap: filtering on a window function',
     code('sql', 'Beeline', "SELECT order_id FROM orders WHERE ROW_NUMBER() OVER (ORDER BY amount) = 1;\n\n-- QUALIFY alone filters correctly:\nSELECT order_id, city, amount FROM orders WHERE order_id < 100020\nQUALIFY ROW_NUMBER() OVER (PARTITION BY city ORDER BY amount DESC, order_id) = 1;\n\n-- QUALIFY + ORDER BY in the same query (Hive 4.2.1, our lab):\nSELECT … FROM orders QUALIFY ROW_NUMBER() OVER (…) = 1 ORDER BY city;",
          capf('l36_wherr.txt').split(': (possible')[0] + ' …\n\n6 rows (one per city, same as Step 2)\n\n50,000 rows returned: the QUALIFY filter was not applied'),
     'Window results do not exist yet when WHERE runs. QUALIFY is meant for this, and it worked on its own, but combined with ORDER BY at the same level our Hive 4.2.1 returned every row. Use the subquery pattern from Step 2 in production code, and test QUALIFY on your exact version before relying on it.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
DAYS = [('10-01', 72810), ('10-02', 71370), ('10-03', 73760), ('10-04', 80600), ('10-05', 69350), ('10-06', 81120)]
def daybars(k_cur, mode):
    o = ''
    mx = 82000
    for k, (d, v) in enumerate(DAYS):
        h = round(80 * v / mx)
        inwin = (k <= k_cur) if mode == 'running' else (k_cur - 6 < k <= k_cur) if mode == 'moving' else (k in (k_cur - 1, k_cur))
        col = 'acc' if k == k_cur else ('blue' if inwin else 'grey')
        o += fill(20 + k * 54, 130 - h, 40, h, col) + t(40 + k * 54, 144, d, 7.4, 'ink2', mono=True)
    return o
see = [
    term([('> … ROW_NUMBER() OVER (PARTITION BY city', W), ('        ORDER BY n_orders DESC, customer_id)', W), ('| 1208 | 33 | 6 | 6 | 6 |', G), ('| 1370 | 33 | 7 | 6 | 6 |', G), ('| 1936 | 33 | 8 | 6 | 6 |', G), ('|  682 | 32 | 9 | 9 | 7 |', Y)]),
    term([('> … SUM(revenue) OVER (ORDER BY order_date)', W), ('| 2026-10-01 | 72810.00 |  72810.00 |', G), ('| 2026-10-02 | 71370.00 | 144180.00 |', G), ('| 2026-10-03 | 73760.00 | 217940.00 |', G), ('| 2026-10-04 | 80600.00 | 298540.00 |', G)]),
    term([('> … AVG(revenue) OVER (ORDER BY order_date', W), ('     ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)', W), ('| 2026-10-04 | 74635.00 |', G), ('| 2026-10-05 | 73578.00 |', G), ('| 2026-10-06 | 74835.00 |', G)]),
    term([('> … revenue - LAG(revenue) OVER (ORDER BY …)', W), ('| 2026-10-01 | NULL      |', Y), ('| 2026-10-02 | -1440.00  |', G), ('| 2026-10-03 | 2390.00   |', G), ('| 2026-10-04 | 6840.00   |', G)]),
    term([('> … LAST_VALUE(amount) OVER w', W), ('| 100001 | 530.00 | 530.00 | 180.00 |', G), ('| 100002 | 500.00 | 500.00 | 180.00 |', G), ('| 100003 | 410.00 | 410.00 | 180.00 |', G), ('  last_default ≠ last row!', RD)]),
]
B1 = [
    t(180, 22, 'Partition, order, then number', 9.4, bold=True) + box(14, 40, 332, 120, 'card') + t(24, 56, 'partition: Chennai (ordered by n_orders DESC)', 7.8, 'ink2', anchor='start') +
    ''.join(box(24, 64 + k * 18, 312, 16, 'acc' if r[1] == 33 else 'card') + t(32, 76 + k * 18, f'{r[0]:>5}  n={r[1]}   rn={r[2]}  rank={r[3]}  dense={r[4]}', 7.6, 'ink', anchor='start', mono=True) for k, r in enumerate([(137, 34, 5, 5, 5), (1208, 33, 6, 6, 6), (1370, 33, 7, 6, 6), (1936, 33, 8, 6, 6), (682, 32, 9, 9, 7)])) +
    cap('Ties: same RANK, gap after; DENSE_RANK has no gap.', '', 'blue', y=176, h=34),
    t(180, 22, 'Running total: frame grows row by row', 9.4, bold=True) + daybars(3, 'running') + t(180, 162, 'default frame: UNBOUNDED PRECEDING → CURRENT ROW', 7.8, 'ink2', mono=True) + cap('10-04: 72,810 + 71,370 + 73,760 + 80,600 = 2,98,540', '', 'green', y=176, h=34),
    t(180, 22, 'Moving average: frame slides', 9.4, bold=True) + daybars(5, 'moving') + t(180, 162, 'ROWS BETWEEN 6 PRECEDING AND CURRENT ROW', 7.8, 'ink2', mono=True) + cap('Only 6 days exist yet, so 10-06 averages 6 values.', '', 'blue', y=176, h=34),
    t(180, 22, 'LAG: look one row back', 9.4, bold=True) + daybars(2, 'lag') + t(180, 162, '73,760 − 71,370 = 2,390', 8, 'ink2', mono=True) + cap('First row has no previous row → NULL.', '', 'amber', y=176, h=34),
    t(180, 22, 'Why LAST_VALUE echoed the current row', 9.4, bold=True) + ''.join(box(24 + k * 80, 50, 72, 30, 'acc' if k <= 1 else 'card') + t(60 + k * 80, 69, a, 8, 'ink', mono=True) for k, a in enumerate(['530', '500', '410', '180'])) +
    t(180, 102, 'current row = 500 → default frame = [530, 500]', 8, 'ink2', mono=True) + t(180, 120, 'last value in that frame = 500', 8.4, 'red', bold=True) + cap('Full frame (… UNBOUNDED FOLLOWING) gives 180.', '', 'green', y=176, h=34),
]
see_caps = ['ROW_NUMBER, RANK and DENSE_RANK side by side on a real three-way tie.',
            'A running total of Pune’s daily revenue.',
            'A 7-day moving average.',
            'Change versus the previous day with LAG; the first day is NULL.',
            'LAST_VALUE with the default frame returns the current row’s amount.']
behind_caps = ['Rows of each city are sorted by order count; ranking functions number them, handling ties differently.',
               'The default frame with ORDER BY covers all rows from the start up to the current one.',
               'A ROWS frame of 6 preceding rows and the current row slides along the days.',
               'LAG reads the value one row earlier in the same ordered partition.',
               'With ORDER BY, the default frame ends at the current row, so the “last” value is the current one.']
two = anim_two('Windows', 'Ranks, running totals and frames', 'Real Beeline output', 'The partition, the order and the frame for the highlighted row', see, B1, see_caps, behind_caps)

# ---- scenario 1: dedup CDC
d1 = (t(180, 22, 'Order status updates arrive as new rows', 9.4, bold=True) + ''.join(t(26, 52 + k * 17, s, 8, 'ink', anchor='start', mono=True) for k, s in enumerate(['100010 PLACED     10:01', '100010 PREPARING  10:07', '100010 DELIVERED  10:41', '100012 PLACED     10:03'])) +
      cap('Reports need the latest status per order.', '(sample events)', 'blue', y=150, h=46))
d2 = (t(180, 22, 'ROW_NUMBER per order, newest first', 9.6, bold=True) + t(180, 56, 'ROW_NUMBER() OVER (PARTITION BY order_id', 8.4, 'ink', mono=True) + t(180, 72, '                   ORDER BY event_ts DESC) AS rn', 8.4, 'ink', mono=True) +
      cap('rn = 1 is the latest event of each order.', '', 'green', y=150, h=34))
d3 = (t(180, 22, 'Keep rn = 1 in an outer query', 9.6, 'green', bold=True) + t(26, 56, '100010 DELIVERED  10:41   rn=1', 8.4, 'green', anchor='start', mono=True) + t(26, 74, '100012 PLACED     10:03   rn=1', 8.4, 'green', anchor='start', mono=True) + cap('One row per order: clean current state.', '', 'green', y=150, h=34))
d4 = (t(180, 22, 'Ties in time?', 9.6, bold=True) + t(180, 56, 'add a tiebreaker: ORDER BY event_ts DESC, event_id DESC', 8.2, 'ink', mono=True) + cap('Make ROW_NUMBER deterministic.', 'Otherwise reruns may pick different rows.', 'amber', y=150, h=46))
d5 = (t(180, 22, 'At scale', 9.6, 'acc', bold=True) + t(180, 56, 'shuffle by order_id, sort by time: one Tez stage', 8.4, 'ink2') + cap('Standard pattern for CDC and duplicate events.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Latest status per order: de-duplication with ROW_NUMBER',
              'Change events create several rows per order. ROW_NUMBER keeps the newest one. (Sample events.)',
              'De-duplication', 'Status events per order are numbered newest first and only row number 1 is kept', [d1, d2, d3, d4, d5],
              ['Each status change of an order arrives as a new row.',
               'ROW_NUMBER partitions by order and orders by time, newest first.',
               'An outer query keeps rn = 1: one current row per order.',
               'Add a tiebreaker so the choice is repeatable.',
               'Hive does this in one shuffle and sort per order key.'],
              hid='scenario-dedup')

# ---- scenario 2: QUALIFY finding
q1 = (t(180, 22, 'A tempting shortcut: QUALIFY', 9.6, bold=True) + t(180, 56, 'SELECT … FROM orders', 8.6, 'ink', mono=True) + t(180, 72, 'QUALIFY ROW_NUMBER() OVER (…) = 1', 8.6, 'ink', mono=True) + cap('Filters on a window result without a subquery.', '', 'blue', y=150, h=34))
q2 = term([('> … WHERE order_id < 100020', W), ('  QUALIFY ROW_NUMBER() OVER (PARTITION BY city', W), ('          ORDER BY amount DESC, order_id) = 1;', W), ('6 rows (one per city)', G)], label='real output · Hive 4.2.1')
q3 = term([('> SELECT order_id, city, amount FROM orders', W), ('  QUALIFY ROW_NUMBER() OVER (…) = 1', W), ('  ORDER BY city;', W), ('50,000 rows: QUALIFY not applied', RD)], label='real output · Hive 4.2.1')
q4 = (t(180, 22, 'Safe pattern everywhere', 9.6, 'green', bold=True) + t(180, 52, 'SELECT * FROM (', 8.4, 'ink', mono=True) + t(180, 66, '  SELECT …, ROW_NUMBER() OVER (…) AS rn FROM orders) x', 8.4, 'ink', mono=True) + t(180, 80, 'WHERE rn = 1 ORDER BY city;', 8.4, 'ink', mono=True) + cap('Correct in our tests and portable to any engine.', '', 'green', y=150, h=34))
q5 = (t(180, 22, 'Lesson for engineers', 9.6, 'acc', bold=True) + ''.join(t(26, 52 + k * 19, s, 8.4, anchor='start') for k, s in enumerate(['• test new syntax on your exact version', '• compare with a known-correct form', '• add row-count checks to pipelines'])) + cap('Trust, but verify.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'QUALIFY in Hive 4.2.1: a behaviour we found',
              'While building this lesson we compared QUALIFY with the classic subquery. Results below are real.',
              'Verifying syntax', 'QUALIFY filters correctly alone but returned unfiltered rows with ORDER BY in Hive 4.2.1; the subquery form is correct', [q1, q2, q3, q4, q5],
              ['QUALIFY filters on window results directly, like HAVING for aggregates.',
               'On its own it returned the expected 6 rows.',
               'With ORDER BY in the same query, our Hive 4.2.1 returned all 50,000 rows.',
               'The subquery pattern gave the right answer in every test.',
               'Always verify new features on your version and keep row-count checks in pipelines.'],
              hid='scenario-qualify')

# ---- scenario 3: sessionisation / churn
g1 = (t(180, 22, 'When did each customer go quiet?', 9.6, bold=True) + t(180, 56, 'gap = order_ts − LAG(order_ts) per customer', 8.6, 'ink', mono=True) + cap('Customer 1492: 90.1 h, then 6.9 h, 5.9 h (real).', '', 'blue', y=150, h=34))
g2 = (t(180, 22, 'Sessions: new session after a long gap', 9.4, bold=True) + t(180, 56, 'is_new = CASE WHEN gap_hours > 24 OR gap IS NULL THEN 1 ELSE 0 END', 7.4, 'ink', mono=True) + t(180, 74, 'session_no = SUM(is_new) OVER (PARTITION BY customer ORDER BY ts)', 7.4, 'ink', mono=True) +
      cap('A running sum of “new session” flags numbers the sessions.', '', 'green', y=150, h=34))
g3 = (t(180, 22, 'Churn signal', 9.6, bold=True) + t(180, 56, 'days since last order = today − MAX(order_ts) per customer', 8, 'ink', mono=True) + t(180, 74, 'compare with the customer’s usual gap (AVG of gaps)', 8.4, 'ink2') + cap('Unusually long silence → win-back offer.', '', 'amber', y=150, h=34))
g4 = (t(180, 22, 'Cost', 9.6, bold=True) + t(180, 56, 'one shuffle by customer_id, sort by order_ts', 8.4, 'ink2') + cap('Customers with huge histories form big partitions.', '', 'blue', y=150, h=34))
g5 = (t(180, 22, 'Same idea, other domains', 9.6, 'acc', bold=True) + t(180, 56, 'app sessions · card fraud velocity · machine downtime', 8.4, 'ink2') + cap('LAG + running SUM is a universal toolkit.', '', 'green', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Gaps, sessions and churn with LAG and running sums',
              'Time between events is one of the most useful features in analytics. Built entirely with window functions.',
              'Event gaps', 'LAG computes gaps between a customer’s orders; a running sum of new-session flags numbers sessions; gaps feed churn signals', [g1, g2, g3, g4, g5],
              ['LAG gives each order the customer’s previous order time; the difference is the gap.',
               'A flag for long gaps and a running SUM of flags numbers each customer’s sessions.',
               'Compare the current silence with the customer’s usual gap to spot churn.',
               'Each customer is a partition: one shuffle and sort.',
               'The same pattern works for app sessions, fraud and machine logs.'],
              hid='scenario-gaps')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Partitions, order and frames</h2>
  <p>Left: real Beeline output. Right: the window used for the highlighted row.</p>
''' + two + '''
  <p>Three live scenarios follow: de-duplication, a QUALIFY behaviour we verified, and gaps and sessions.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Window functions at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'TOP 3 / city', 9, 'green', bold=True) + t(60, 58, 'ROW_NUMBER', 7.4, 'ink2'),
    '1. Top-N per group',
    'Best-selling dishes per restaurant, top customers per city, latest price per product: ROW_NUMBER in a subquery is the standard tool.',
    ['Rows', '*ROW_NUMBER', 'rn ≤ N']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'MTD', 10, 'blue', bold=True) + t(60, 58, 'running SUM', 7.4, 'ink2'),
    '2. Month-to-date dashboards',
    'Finance dashboards show running revenue against target day by day with SUM() OVER (ORDER BY day).',
    ['Daily revenue', '*Running SUM', 'MTD chart']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'dedupe', 10, 'violet', bold=True) + t(60, 58, 'latest per key', 7.4, 'ink2'),
    '3. Cleaning duplicate and change data',
    'CDC feeds and retried events create several rows per key; ROW_NUMBER keeps the latest version before loading curated tables.',
    ['Raw events', '*ROW_NUMBER = 1', 'Current state']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'LAG', 10, 'acc', bold=True, mono=True) + t(60, 58, 'gaps & sessions', 7.4, 'ink2'),
    '4. Behaviour features for ML',
    'Days since last order, average gap, order number per customer and rolling 30-day spend are computed with window functions for churn and recommendation models.',
    ['Orders', '*LAG / rolling', 'Features']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'NTILE(10)', 9, 'acc', bold=True, mono=True) + t(60, 58, 'deciles', 7.4, 'ink2'),
    '5. Customer tiers',
    'Marketing splits customers into spend deciles with NTILE(10) to design tiered offers.',
    ['Spend per customer', '*NTILE', 'Tiers']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> you need GROUP BY (<a href="../02-group-by-and-grouping-sets/">3.2</a>) and subqueries/CTEs (<a href="../05-subqueries-and-ctes/">3.5</a>).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
