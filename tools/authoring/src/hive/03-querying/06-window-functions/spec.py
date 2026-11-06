import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from hivekit import tables
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
BODY = body(HERE)

META = dict(
    module='03-querying', lesson='06-window-functions', n='3.6',
    module_label='Module 3 · Querying with HiveQL',
    title='Window functions: ranking, running totals and LAG/LEAD',
    desc='Hive window (analytic) functions explained with real Hive 4.2.1 results: OVER, PARTITION BY and ORDER BY, ROW_NUMBER vs RANK vs DENSE_RANK on ties, top-N per group, running totals and moving averages with ROWS frames, LAG and LEAD, FIRST_VALUE and the LAST_VALUE frame trap, NTILE, PERCENT_RANK, CUME_DIST, share of total, and why QUALIFY needs care.',
    og_desc='Top 3 per city, running totals and the gap since the last order: Hive window functions with real outputs and the traps explained.',
    minutes=35, level='Beginner → Advanced',
    lead='GROUP BY squeezes many rows into one. Window functions keep every row and add a calculation over related rows: a rank inside the city, a running total by date, the previous order of the same customer. This lesson answers three real requests from the TiffinGo growth team, compares the three ranking functions on real ties, and shows two traps that silently give wrong answers. <b>All outputs are real</b>, from Hive 4.2.1.',
    chips=['Real Hive 4.2.1 outputs', 'Ranking on real ties', 'Running totals and LAG', 'Runs in your browser (Python)'],
)

MAIN = '''# ROW_NUMBER, RANK and DENSE_RANK over the same ordered partition
rows = [("Chennai", 1208, 33), ("Chennai", 1370, 33), ("Chennai", 1936, 33),
        ("Chennai", 682, 32), ("Chennai", 697, 32)]          # real counts, ranks 6..10

rn, rank, dense = 5, 5, 5          # the five rows above these had ranks 1..5
prev = None
for i, (city, cust, n) in enumerate(rows):
    rn += 1                                  # ROW_NUMBER: always +1
    if n != prev:
        rank = rn                            # RANK: jump to the row number
        dense += 1                           # DENSE_RANK: next integer, no gaps
    prev = n
    print(f"{city} {cust:5} n={n}  rn={rn:2}  rank={rank}  dense={dense}")
'''
RUN = dict(
    heading='Run the code: ranks, running totals and LAG',
    intro='<p>These programs compute window functions by hand on real lab numbers, so you can see exactly what Hive does row by row. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    rn += 1                                  # ROW_NUMBER: always +1', 'ROW_NUMBER never repeats, so ties get different numbers. Add a tie-breaker in ORDER BY to make it deterministic.'),
        ('        rank = rn                            # RANK: jump to the row number', 'After three rows tied at 6, RANK jumps to 9: it leaves gaps.'),
        ('        dense += 1                           # DENSE_RANK: next integer, no gaps', 'DENSE_RANK gives 7 after the tie: no gaps.'),
    ],
    tasks=[
        dict(label='1 · Three ranking functions', hint='Press <b>Run</b> and compare with the real Hive output in Step 1: rn 6–10, rank 6, 6, 6, 9, 9 and dense 6, 6, 6, 7, 7.', code=None),
        dict(label='2 · Running total', hint='<b>Predict first:</b> what is the running total on 10-04? (Real Hive answer: 298540.)',
             code='''days = [("10-01", 72810), ("10-02", 71370), ("10-03", 73760), ("10-04", 80600)]
total = 0
for day, rev in days:
    total += rev                      # SUM(revenue) OVER (ORDER BY order_date)
    print(day, rev, total)
'''),
        dict(label='3 · Moving average with a ROWS frame', hint='ROWS BETWEEN 2 PRECEDING AND CURRENT ROW: at most three rows. Change <code>k</code> to 7 to get the 7-day average from the lesson.',
             code='''revs = [72810, 71370, 73760, 80600, 69350, 81120, 73640, 75370]
k = 3
for i, r in enumerate(revs):
    window = revs[max(0, i - k + 1): i + 1]
    print(i + 1, r, round(sum(window) / len(window), 2))
'''),
        dict(label='4 · LAG: hours since the previous order', hint='LAG(order_ts) OVER (PARTITION BY customer_id ORDER BY order_ts). Real answer for customer 1492: None, 90.1, 6.9, 5.9.',
             code='''from datetime import datetime
ts = ["2026-10-01 09:02", "2026-10-05 03:06", "2026-10-05 10:00", "2026-10-05 15:55"]
prev = None
for t in ts:
    cur = datetime.strptime(t, "%Y-%m-%d %H:%M")
    gap = None if prev is None else round((cur - prev).total_seconds() / 3600, 1)
    print(t, gap)
    prev = cur
'''),
        dict(label='5 · Spot the error', hint='This “top order per city” uses RANK, and two Pune orders tie. The report must have exactly one row per city. Fix it with a ROW_NUMBER-style counter plus a tie-breaker.', expect='error',
             code='''orders = [(1, "Pune", 460), (2, "Pune", 460), (3, "Thane", 320), (4, "Pune", 410)]
best = []
for city in ["Pune", "Thane"]:
    rows = sorted([o for o in orders if o[1] == city], key=lambda o: -o[2])
    top = rows[0][2]
    best += [o for o in rows if o[2] == top]          # RANK() = 1 keeps every tie
assert len(best) == 2, f"{len(best)} rows: RANK = 1 returns all tied rows"
print(best)
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

_lag = tables(open(CAP + 'l36_lag_share.txt').read())
PCRUN = dict(
    heading='Run on your PC: distribution functions and the QUALIFY check',
    intro='<p>Three more queries to try in Beeline on the TiffinGo data. <b>Outputs are real</b>, from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · NTILE, PERCENT_RANK and CUME_DIST', cmd='SELECT order_id, amount,\n  NTILE(4)       OVER (ORDER BY amount) AS quartile,\n  ROUND(PERCENT_RANK() OVER (ORDER BY amount), 3) AS pr,\n  ROUND(CUME_DIST()    OVER (ORDER BY amount), 3) AS cd\nFROM orders WHERE order_id < 100009 ORDER BY amount;', file='Beeline',
             output=_lag[2],
             note='NTILE(4) splits 8 rows into 4 buckets of 2. PERCENT_RANK is (rank − 1) / (rows − 1), so it starts at 0. CUME_DIST is rows up to and including this one ÷ all rows, so it ends at 1.'),
        dict(title='2 · QUALIFY inside a subquery', cmd='SELECT COUNT(*) AS n FROM (\n  SELECT order_id, city FROM orders\n  QUALIFY ROW_NUMBER() OVER (PARTITION BY city ORDER BY amount DESC, order_id) = 1\n  ORDER BY city) t;', file='Beeline',
             output='+----+\n| n  |\n+----+\n| 8  |\n+----+',
             note='One row per city, as expected. The very same QUALIFY + ORDER BY run as the outer query returned all 50,000 rows in our lab. Count the rows of any QUALIFY query before trusting it on your Hive version.'),
        dict(title='3 · Window over grouped rows: share of city total', cmd="SELECT city, payment, COUNT(*) AS n,\n  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY city), 1) AS pct\nFROM orders WHERE city = 'Thane'\nGROUP BY city, payment ORDER BY n DESC;", file='Beeline',
             output=_lag[1],
             note='Windows run after GROUP BY, so <code>SUM(COUNT(*)) OVER (…)</code> adds the group counts of the city. The four shares add to 100.1 because of rounding.'),
    ],
)

TRACE = dict(
    heading='Computing a running total and LAG, one row at a time',
    intro='<p>Hive sorts the partition, then walks the rows in order, keeping state from the previous rows. Watch <code>running</code> and <code>prev</code>.</p>',
    code='''revs = [72810, 71370, 73760]
running = 0
prev = None
for r in revs:
    running = running + r
    change = None if prev is None else r - prev
    prev = r
print(running, change)
''',
    notes={5: 'Frame :: Default frame with ORDER BY: from the first row up to the current row.', 6: 'LAG :: The first row has no previous row, so LAG gives NULL.', 8: 'Result :: 217940 and 2390, the same as the real 10-03 row.'},
)

WORKED_INTRO = 'Three requests that need window functions: one row per key, a ranked leaderboard with ties, and sessions from gaps.'
EXAMPLES = [
    dict(level='b', tag='Data quality · ROW_NUMBER', title='Keep the latest version of each order',
         problem='<p>A change feed sends several versions of the same order. Keep the newest one per <code>order_id</code>: <code>ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC) = 1</code> in a subquery.</p>',
         inp='(order_id, status, updated_at): (101, placed, 09:00), (101, delivered, 09:40), (102, placed, 09:05), (101, cancelled, 09:20)',
         approach=['Group the versions by order_id (PARTITION BY).', 'Sort each group by updated_at, newest first.', 'Number the rows and keep number 1.'],
         code='''feed = [(101, "placed", "09:00"), (101, "delivered", "09:40"),
        (102, "placed", "09:05"), (101, "cancelled", "09:20")]
latest = {}
for oid, status, ts in sorted(feed, key=lambda r: (r[0], r[2]), reverse=True):
    if oid not in latest:                 # row number 1 in this partition
        latest[oid] = (status, ts)
print(latest)
''', notes={5: 'rn = 1 :: The first row seen for each order after sorting newest first.'},
         tryit='Two versions with the same timestamp make the choice random. Add a second ORDER BY column, such as a sequence number, as a tie-breaker.'),
    dict(level='i', tag='Leaderboard · DENSE_RANK', title='Top 6 order counts in Chennai, ties included',
         problem='<p>Marketing wants “the customers with the top 6 order counts” in Chennai, and tied customers must all get the reward. Which ranking function, and how many customers qualify?</p>',
         inp='Chennai counts (real): 41, 39, 38, 37, 34, 33, 33, 33, 32, 32',
         approach=['“Top 6 counts” means the six highest distinct values: DENSE_RANK ≤ 6.', '“Top 6 customers” would be ROW_NUMBER ≤ 6.', 'Compare both.'],
         code='''counts = [41, 39, 38, 37, 34, 33, 33, 33, 32, 32]
top6_values = sorted(set(counts), reverse=True)[:6]
print("ROW_NUMBER <= 6:", counts[:6])
print("DENSE_RANK <= 6:", [c for c in counts if c in top6_values])
''', notes={2: 'Distinct values :: DENSE_RANK numbers distinct values with no gaps.'},
         tryit='ROW_NUMBER picks 6 customers and drops two of the three tied at 33 at random; DENSE_RANK rewards 8. Ask the business which meaning they want before writing the query.'),
    dict(level='a', tag='Product analytics · LAG + running SUM', title='Turn order times into sessions',
         problem='<p>Treat orders less than 12 hours apart as one session. Mark a new session when the gap from <code>LAG(order_ts)</code> is NULL or ≥ 12 hours, then number sessions with a running <code>SUM(flag)</code>.</p>',
         inp='customer 1492 (real): 10-01 09:02, 10-05 03:06, 10-05 10:00, 10-05 15:55',
         approach=['Gap from the previous order with LAG.', 'new_session = 1 if the gap is NULL or ≥ 12 h, else 0.', 'Session id = running SUM of new_session.'],
         code='''gaps = [None, 90.1, 6.9, 5.9]          # real LAG gaps in hours
session = 0
for g in gaps:
    flag = 1 if g is None or g >= 12 else 0
    session += flag                    # SUM(flag) OVER (ORDER BY order_ts)
    print(g, flag, "session", session)
''', notes={5: 'Running sum :: Each new_session flag starts a new number.'},
         tryit='Change the threshold to 6 hours. The last two orders split into separate sessions because 6.9 ≥ 6.'),
]

QUIZ = mix([
    dict(q='Beginner: How is a window function different from GROUP BY?', options=['It is faster', 'It keeps every input row and adds a calculated column', 'It removes duplicates', 'It only works on numbers'], answer=1,
         why='GROUP BY returns one row per group; a window function returns one value per input row.'),
    dict(q='Beginner: Three customers tie at rank 6. What rank does the next customer get with RANK()?', options=['7', '9', '6', '10'], answer=1,
         why='RANK leaves gaps: 6, 6, 6, then 9. DENSE_RANK would give 7. Real Chennai data in Step 1.'),
    dict(q='Beginner: What does LAG(amount) return on the first row of a partition?', options=['0', 'The same amount', 'NULL (unless a default is given)', 'An error'], answer=2,
         why='There is no previous row. LAG(amount, 1, 0) supplies 0 instead.'),
    dict(q='Intermediate: Which clause restarts the calculation for each city?', options=['ORDER BY city', 'PARTITION BY city', 'GROUP BY city', 'CLUSTER BY city'], answer=1,
         why='PARTITION BY splits rows into independent windows.'),
    dict(q='Intermediate: Why can’t you write WHERE ROW_NUMBER() OVER (…) = 1?', options=['ROW_NUMBER needs GROUP BY', 'WHERE runs before window functions are computed', 'Hive has no ROW_NUMBER', 'It works fine'], answer=1,
         why='Compute the window in a subquery or CTE, then filter in the outer query.'),
    dict(q='Intermediate: LAST_VALUE(amount) OVER (ORDER BY order_id) returned each row’s own amount. Why?', options=['A Hive bug', 'The default frame ends at the current row', 'LAST_VALUE ignores ORDER BY', 'The data was not sorted'], answer=1,
         why='Use ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING for the real last value.'),
    dict(q='Advanced: What does ROWS BETWEEN 6 PRECEDING AND CURRENT ROW give over daily rows?', options=['A 6-day window', 'A window of up to 7 rows (a 7-day moving window if no day is missing)', 'All rows', 'Only 6 rows after'], answer=1,
         why='Six earlier rows plus the current one. Missing days would make it span more calendar days.'),
    dict(q='Advanced: In our Hive 4.2.1 lab, what happened to QUALIFY with ORDER BY in the same top-level query?', options=['Error', 'Correct result', 'All 50,000 rows came back: the filter was ignored', 'It returned 0 rows'], answer=2,
         why='QUALIFY alone, or inside a subquery, returned the correct rows. Use the subquery pattern and verify counts.'),
])

REVISION = [
    'Syntax: <code>func(…) OVER (PARTITION BY … ORDER BY … [ROWS|RANGE BETWEEN …])</code>. Every input row stays.',
    '<b>ROW_NUMBER</b> 1,2,3 always unique · <b>RANK</b> ties share, then gaps (6,6,6,9) · <b>DENSE_RANK</b> no gaps (6,6,6,7).',
    'Top-N per group: rank in a subquery / CTE, filter <code>rn &lt;= N</code> outside. Add a tie-breaker for ROW_NUMBER.',
    '<b>Running total</b>: <code>SUM(x) OVER (ORDER BY d)</code>. <b>Moving average</b>: <code>ROWS BETWEEN 6 PRECEDING AND CURRENT ROW</code>.',
    '<b>LAG / LEAD</b>(col, offset, default): previous / next row; NULL at the edges without a default.',
    '<b>FIRST_VALUE</b> is safe; <b>LAST_VALUE</b> needs a frame to UNBOUNDED FOLLOWING.',
    '<b>NTILE(n)</b> buckets · <b>PERCENT_RANK</b> = (rank−1)/(rows−1) · <b>CUME_DIST</b> = rows ≤ current / rows.',
    'Windows run after WHERE, GROUP BY and HAVING, so <code>SUM(COUNT(*)) OVER (PARTITION BY city)</code> works; you cannot use them in WHERE.',
    'QUALIFY exists in Hive 4, but check it on your version; the subquery pattern is portable.',
]
FAQ = [
    ('ROWS or RANGE: what is the difference?', 'ROWS counts physical rows: 6 PRECEDING means six rows back. RANGE works on the ORDER BY value, so rows with the same value are treated together, and with no explicit frame and an ORDER BY the default is RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW. With duplicate ORDER BY values a running total using the default frame jumps for all tied rows at once. Use ROWS when you want strictly one row at a time.'),
    ('Are window functions slow in Hive?', 'Each distinct PARTITION BY / ORDER BY combination needs the data shuffled and sorted by those keys, much like a GROUP BY. Functions that share the same OVER clause are computed in one pass, so reuse one definition (a named WINDOW) where you can, and filter rows with WHERE before the window runs.'),
    ('Can I use a window function without PARTITION BY?', 'Yes. The whole result becomes one window, as in the Pune running total. Be careful on big tables: one window means one reducer has to sort everything.'),
    ('What does OVER () with nothing inside mean?', 'The window is all rows with no order, so SUM(x) OVER () puts the grand total on every row. That is handy for percentage-of-total columns.'),
    ('Is QUALIFY safe to use?', 'QUALIFY is supported in Hive 4 and filtered correctly on its own and inside a subquery in our tests. Combined with ORDER BY in the same top-level query, Hive 4.2.1 returned every row. Until you have tested your exact version, prefer the subquery pattern, and always check the row count.'),
]

PRACTICE_INTRO = 'Programs that compute window results by hand on real lab numbers, with the HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Number rows per city', stmt='Give each order a row number within its city, highest amount first.', inp='(city, amount) pairs',
         code='''orders = [("Pune", 410), ("Thane", 300), ("Pune", 460), ("Thane", 250), ("Pune", 120)]
for city in ["Pune", "Thane"]:
    for i, (c, a) in enumerate(sorted([o for o in orders if o[0] == city], key=lambda o: -o[1]), 1):
        print(c, a, i)
''', explain='ROW_NUMBER() OVER (PARTITION BY city ORDER BY amount DESC). Numbering restarts at 1 for Thane.'),
    dict(level='easy', title='Grand total on every row', stmt='Show each city’s revenue and its share of the total.', inp='real revenue for four cities',
         code='''rev = {"Mumbai": 2941120, "Bengaluru": 2724070, "Pune": 2344660, "Hyderabad": 1763190}
total = sum(rev.values())                    # SUM(revenue) OVER ()
for c, r in rev.items():
    print(c, r, f"{100 * r / total:.1f}%")
''', explain='SUM(revenue) OVER () is the total of all rows; dividing gives the share.'),
    dict(level='easy', title='RANK vs DENSE_RANK', stmt='Rank the amounts [500, 480, 480, 460] both ways.', inp='four amounts',
         code='''a = [500, 480, 480, 460]
rank = [1 + sum(1 for y in a if y > x) for x in a]
dense = [1 + len({y for y in a if y > x}) for x in a]
print(rank, dense)
''', explain='RANK [1, 2, 2, 4] and DENSE_RANK [1, 2, 2, 3].'),
    dict(level='medium', title='Day-on-day change', stmt='Compute revenue − LAG(revenue) for the real Pune days.', inp='10-01 … 10-05',
         code='''revs = [72810, 71370, 73760, 80600, 69350]
print([None] + [b - a for a, b in zip(revs, revs[1:])])
''', explain='[None, −1440, 2390, 6840, −11250]: the same as the real change_vs_prev column.'),
    dict(level='medium', title='Next order with LEAD', stmt='For each order of customer 1492 show the time of the next order, or “last” if none.', inp='real order times',
         code='''ts = ["10-01 09:02", "10-05 03:06", "10-05 10:00", "10-05 15:55"]
for cur, nxt in zip(ts, ts[1:] + ["last"]):
    print(cur, "->", nxt)
''', explain='LEAD(order_ts, 1, \'last\') looks one row ahead; the default replaces NULL on the final row (cast the timestamp to STRING to use a text default).'),
    dict(level='medium', title='Quartiles with NTILE', stmt='Split 8 sorted amounts into 4 buckets.', inp='real amounts of orders 100001–100008',
         code='''amounts = sorted([530, 500, 410, 180, 480, 460, 310, 360])
n, k = len(amounts), 4
for i, a in enumerate(amounts):
    print(a, i * k // n + 1)
''', explain='Buckets 1,1,2,2,3,3,4,4, matching the real NTILE(4) output. When rows do not divide evenly, the first buckets get one extra row.'),
    dict(level='business', title='Best day so far', stmt='For each Pune day, show the highest daily revenue seen up to that day (a running MAX).', inp='real daily revenue',
         code='''revs = [72810, 71370, 73760, 80600, 69350, 81120]
best = 0
for r in revs:
    best = max(best, r)                      # MAX(revenue) OVER (ORDER BY order_date)
    print(r, best)
''', explain='The record moves to 80600 on 10-04 and to 81120 on 10-06. Useful for “new record day” alerts.'),
    dict(level='business', title='Dedup before counting', stmt='A feed has 5 rows for 3 orders. How many delivered orders are there after keeping the latest version of each?', inp='(order, status, version)',
         code='''feed = [(1, "placed", 1), (1, "delivered", 2), (2, "placed", 1), (2, "cancelled", 2), (3, "delivered", 1)]
latest = {}
for o, s, v in sorted(feed, key=lambda r: r[2]):
    latest[o] = s
print(latest, "delivered:", sum(1 for s in latest.values() if s == "delivered"))
''', explain='3 orders with 2 delivered. Counting raw rows would report 5 orders and 2 still “placed”, although both of those orders moved on. Status counts must come from the latest version of each order.'),
]

SCN_INTRO = 'Window functions are among the most asked SQL interview topics. Expect top-N per group, the ranking differences and LAG questions.'
SCENARIOS = (
    scn('Any company · SQL', 'Fresher', '“Second highest order in each city”',
        'Write a query that returns the second highest order amount in every city.',
        'do you know ranking functions and ties?',
        '''<pre>SELECT city, amount FROM (
  SELECT city, amount,
         DENSE_RANK() OVER (PARTITION BY city ORDER BY amount DESC) AS dr
  FROM orders) x
WHERE dr = 2;</pre>
        <p>Say why DENSE_RANK: if two orders tie for the highest, RANK would skip 2.</p>''', 'Using LIMIT, which gives one global answer, not one per city.') +
    scn('Data engineering', 'Mid-level', 'Duplicates from a change feed',
        'The orders table receives every update of an order. Reports double count. Fix it.',
        'can you de-duplicate with ROW_NUMBER?',
        '''<ol>
          <li>Rank versions: <code>ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC, seq DESC)</code>.</li>
          <li>Keep <code>rn = 1</code> in an outer query, and write the result to a clean table or view.</li>
          <li>Check: COUNT(*) equals COUNT(DISTINCT order_id).</li>
        </ol>''', 'SELECT DISTINCT, which keeps every version because the statuses differ.') +
    scn('Analytics', 'Mid-level', 'QUALIFY returns too many rows',
        'A colleague’s “latest row per key” query with QUALIFY and ORDER BY returns all rows on your cluster.',
        'do you verify results instead of trusting syntax?',
        '''<ul>
          <li>Compare COUNT(*) of the result with the number of distinct keys.</li>
          <li>Rewrite with the subquery pattern, or move ORDER BY to an outer query; both worked in our lab.</li>
          <li>Report the behaviour with the exact Hive version, and add a row-count check to the job.</li>
        </ul>''', '“QUALIFY is standard, so it must be right”.') +
    scn('Product analytics', 'Senior', 'Sessions and retention',
        'Define user sessions (gap ≥ 30 minutes starts a new session) and report sessions per user per day.',
        'can you combine LAG with a running sum?',
        '''<ul>
          <li>Gap: <code>unix_timestamp(ts) - unix_timestamp(LAG(ts) OVER (PARTITION BY user ORDER BY ts))</code>.</li>
          <li>Flag: 1 when the gap is NULL or ≥ 1800 seconds; session id = <code>SUM(flag) OVER (PARTITION BY user ORDER BY ts ROWS UNBOUNDED PRECEDING)</code>.</li>
          <li>Then GROUP BY user, date, session id.</li>
        </ul>''', 'A self-join on “the previous event”, which is slow and hard to get right.')
)
