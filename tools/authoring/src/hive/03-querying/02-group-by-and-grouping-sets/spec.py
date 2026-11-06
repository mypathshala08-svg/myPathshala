import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
BODY = body(HERE)
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep

META = dict(
    module='03-querying', lesson='02-group-by-and-grouping-sets', n='3.2',
    module_label='Module 3 · Querying with HiveQL',
    title='GROUP BY, HAVING, ROLLUP and GROUPING SETS',
    desc='Aggregation in Hive with real Hive 4.2.1 results: GROUP BY rules (error 10025), COUNT(*) vs COUNT(col) vs COUNT(DISTINCT), SUM, AVG, MIN, MAX, collect_set, percentile_approx, HAVING, grouping by expressions and positions, GROUPING SETS, ROLLUP, CUBE, GROUPING__ID and grouping(), map-side aggregation (8 vs 50,000 shuffled rows) and skew.',
    og_desc='One query for detail, subtotals and the grand total. GROUP BY, HAVING, ROLLUP and CUBE in Hive, with what happens inside the map tasks.',
    minutes=34, level='Beginner → Advanced',
    lead='Most reports are aggregations: totals per city, counts per payment mode, subtotals and a grand total. This lesson builds TiffinGo’s monthly review table with GROUP BY, HAVING, ROLLUP and CUBE, explains the “Expression not in GROUP BY key” error, and shows behind the screen why Hive shuffles only 8 rows instead of 50,000. <b>All outputs are real</b>, from Hive 4.2.1.',
    chips=['Real Hive 4.2.1 outputs', 'ROLLUP · CUBE · GROUPING SETS', 'Map-side aggregation counters', 'Runs in your browser (Python)'],
)

MAIN = '''# GROUP BY city with map-side (partial) aggregation, in Python
splits = [["Pune", "Thane", "Pune", "Mumbai"], ["Pune", "Mumbai", "Mumbai"], ["Thane", "Pune"]]

partials = []
for split in splits:                    # each map task
    counts = {}
    for city in split:
        counts[city] = counts.get(city, 0) + 1
    partials.append(counts)
print("sent to shuffle:", partials)

final = {}
for p in partials:                      # the reducer merges
    for city, n in p.items():
        final[city] = final.get(city, 0) + n
print("result:", final)
'''
RUN = dict(
    heading='Run the code: grouping, partial aggregation and rollups',
    intro='<p>These programs do what Hive does for GROUP BY: partial counts per map task, a merge in the reducer, HAVING on groups, averages from (sum, count) pairs, and ROLLUP subtotals. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('for split in splits:                    # each map task', 'Each map task builds its own small hash table: <code>mode: hash</code> in EXPLAIN.'),
        ('for p in partials:                      # the reducer merges', 'The reducer adds the partial counts: <code>mode: mergepartial</code>.'),
    ],
    tasks=[
        dict(label='1 · Partial aggregation', hint='Press <b>Run</b>. Count how many (city, count) pairs were sent compared with 9 raw rows.', code=None),
        dict(label='2 · HAVING', hint='<b>Predict first:</b> which cities survive <code>HAVING COUNT(*) &gt; 2</code>? Change the threshold to 3.',
             code='''orders = ["Pune", "Thane", "Pune", "Mumbai", "Pune", "Mumbai", "Mumbai", "Thane", "Pune"]
groups = {}
for city in orders:
    groups[city] = groups.get(city, 0) + 1
print({c: n for c, n in groups.items() if n > 2})     # HAVING COUNT(*) > 2
'''),
        dict(label='3 · AVG across tasks', hint='Averages must travel as (sum, count). Compare the right answer with the average of the per-task averages.',
             code='''tasks = [[100, 200, 300], [600]]          # amounts of one city in two map tasks
pairs = [(sum(t), len(t)) for t in tasks]
right = sum(s for s, _ in pairs) / sum(c for _, c in pairs)
wrong = sum(s / c for s, c in pairs) / len(pairs)
print("right:", right, "| average of averages:", wrong)
'''),
        dict(label='4 · ROLLUP by hand', hint='Build detail, city subtotals and a grand total from (city, payment) counts. Real Pune numbers from the lab.',
             code='''detail = {("Pune", "COD"): 783, ("Pune", "Card"): 1567, ("Pune", "UPI"): 4746, ("Pune", "Wallet"): 834}
city_total = {}
for (city, pay), n in detail.items():
    city_total[city] = city_total.get(city, 0) + n
print("detail:", detail)
print("subtotal:", city_total)
print("grand total:", sum(detail.values()))
'''),
        dict(label='5 · Spot the error', hint='This “GROUP BY city” picks one payment per city, like selecting a column that is not grouped. The check fails because information is lost. Use a set of payments per city (collect_set) instead.', expect='error',
             code='''orders = [("Pune", "UPI"), ("Pune", "COD"), ("Thane", "Card")]
by_city = {}
for city, pay in orders:
    by_city[city] = pay                     # keeps only the last payment!
assert by_city["Pune"] == {"UPI", "COD"}, f"Pune shows only {by_city['Pune']!r}: payment is not a grouping key"
print(by_city)
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: counters, positions and expressions',
    intro='<p>Run these on the lab. <b>Outputs are real</b>, from Hive 4.2.1; with <code>--silent=false</code> Beeline prints the Tez counters.</p>',
    items=[
        dict(title='1 · Watch partial aggregation in the counters', cmd="SET hive.map.aggr=true;   SELECT city, COUNT(*) FROM orders GROUP BY city;\nSET hive.map.aggr=false;  SELECT city, COUNT(*) FROM orders GROUP BY city;", file='Beeline (INFO lines)',
             output=open(CAP + 'l32_mapaggr.txt').read().rstrip(),
             note='Same input, same 8-row answer. With map-side aggregation only 8 rows leave the map stage; without it, all 50,000. On a cluster that difference is network traffic and reducer time.'),
        dict(title='2 · GROUP BY a position', cmd="SELECT city, COUNT(*) FROM orders GROUP BY 1 ORDER BY 2 DESC LIMIT 2;\nSET hive.groupby.position.alias=true;\nSELECT city, COUNT(*) FROM orders GROUP BY 1 ORDER BY 2 DESC LIMIT 2;", file='Beeline',
             output="Error: Error while compiling statement: FAILED: SemanticException [Error 10025]: Line 1:7 Expression not in GROUP BY key 'city'\n+------------+--------+\n|    city    |  _c1   |\n+------------+--------+\n| Mumbai     | 10014  |\n| Bengaluru  | 9298   |\n+------------+--------+",
             note='By default Hive treats <code>1</code> as the constant number 1, not “column 1”. The setting enables positions; many teams prefer explicit names for readability.'),
        dict(title='3 · Group by an expression', cmd="SELECT CASE WHEN amount >= 600 THEN 'large' WHEN amount >= 300 THEN 'medium' ELSE 'small' END AS band,\n       COUNT(*) AS n\nFROM orders\nGROUP BY CASE WHEN amount >= 600 THEN 'large' WHEN amount >= 300 THEN 'medium' ELSE 'small' END\nORDER BY n DESC;", file='Beeline',
             output='+---------+--------+\n|  band   |   n    |\n+---------+--------+\n| small   | 26116  |\n| medium  | 21848  |\n| large   | 2036   |\n+---------+--------+',
             note='The expression is repeated in GROUP BY. Over half of TiffinGo’s orders are under Rs 300; only 2,036 are Rs 600 or more.'),
    ],
)

TRACE = dict(
    heading='Grouping five orders, one line at a time',
    intro='<p>Watch a dictionary of (count, sum) pairs grow per city, then the averages computed from the pairs at the end.</p>',
    code='''orders = [("Pune", 200), ("Thane", 150), ("Pune", 400), ("Thane", 90), ("Pune", 300)]
agg = {}
for city, amount in orders:
    n, s = agg.get(city, (0, 0))
    agg[city] = (n + 1, s + amount)
for city, (n, s) in agg.items():
    print(city, "orders:", n, "sum:", s, "avg:", s / n)
''',
    notes={5: 'Accumulate :: Keep count and sum per group, never a running average.', 7: 'Finish :: AVG = sum ÷ count, computed once per group.'},
)

WORKED_INTRO = 'Three aggregation jobs from TiffinGo: a city report with a threshold, a payment mix with shares, and a ROLLUP check that subtotals match the total.'
EXAMPLES = [
    dict(level='b', tag='Reporting · HAVING', title='Cities with average order above Rs 295',
         problem='<p>Using delivered orders, keep cities whose average order value is above Rs 295, as <code>GROUP BY city HAVING AVG(amount) &gt; 295</code>. Real averages from the lab are used as input.</p>',
         inp='Mumbai 293.29 · Bengaluru 292.80 · Pune 295.58 · Hyderabad 296.21 · Chennai 299.22',
         approach=['Treat each city’s average as already computed.', 'Apply the HAVING condition.', 'Sort the survivors by average, highest first.'],
         code='''avg = {"Mumbai": 293.29, "Bengaluru": 292.80, "Pune": 295.58, "Hyderabad": 296.21, "Chennai": 299.22}
kept = {c: a for c, a in avg.items() if a > 295}
for c, a in sorted(kept.items(), key=lambda kv: -kv[1]):
    print(f"{c:10} {a}")
''', notes={2: 'HAVING :: A filter on the aggregated value, not on single orders.'},
         tryit='Notice that the biggest city by revenue (Mumbai) does not have the biggest average order. Volume and basket size are different stories.'),
    dict(level='i', tag='Reporting · shares', title='Payment mix with percentages',
         problem='<p>From the real Pune payment counts, compute each mode’s share of Pune orders, as you would with <code>COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY city)</code> (Lesson 3.6).</p>',
         inp='Pune: COD 783, Card 1,567, UPI 4,746, Wallet 834',
         approach=['Sum the counts.', 'Divide each count by the total.', 'Print sorted by share.'],
         code='''pune = {"COD": 783, "Card": 1567, "UPI": 4746, "Wallet": 834}
total = sum(pune.values())
for mode, n in sorted(pune.items(), key=lambda kv: -kv[1]):
    print(f"{mode:6} {n:5}  {n / total:.1%}")
print("total ", total)
''', notes={2: 'Total :: 7,930, the same as Pune’s ROLLUP subtotal.'},
         tryit='UPI is about 60% of Pune’s orders. Add Thane’s numbers (COD 428, Card 972, UPI 2914, Wallet 506) and compare.'),
    dict(level='a', tag='Quality · reconciliation', title='Verify a ROLLUP result',
         problem='<p>Given ROLLUP output rows (city, payment, n, gid), check that each city subtotal equals the sum of its detail rows and that the grand total equals the sum of subtotals.</p>',
         inp='Real ROLLUP rows for Pune and Thane',
         approach=['Split rows by gid: 0 detail, 1 subtotal, 3 grand total.', 'Sum detail per city and compare with subtotals.', 'Compare the grand total with the sum of subtotals.'],
         code='''rows = [("Pune","COD",783,0),("Pune","Card",1567,0),("Pune","UPI",4746,0),("Pune","Wallet",834,0),
        ("Thane","COD",428,0),("Thane","Card",972,0),("Thane","UPI",2914,0),("Thane","Wallet",506,0),
        ("Pune",None,7930,1),("Thane",None,4820,1),(None,None,12750,3)]
detail = {}
for c, p, n, g in rows:
    if g == 0: detail[c] = detail.get(c, 0) + n
subs = {c: n for c, p, n, g in rows if g == 1}
grand = [n for c, p, n, g in rows if g == 3][0]
print("subtotals ok:", detail == subs, "| grand ok:", sum(subs.values()) == grand)
''', notes={6: 'Detail :: gid 0 rows are the full (city, payment) groups.'},
         tryit='Change Thane UPI to 2,913 to simulate a lost row: the check fails. Automated checks like this protect monthly reports.'),
]

QUIZ = mix([
    dict(q='Beginner: Which clause filters groups after aggregation?', options=['WHERE', 'HAVING', 'LIMIT', 'ON'], answer=1,
         why='HAVING COUNT(*) > 6000 kept Mumbai, Bengaluru and Pune.'),
    dict(q='Beginner: What does COUNT(col) count?', options=['All rows', 'Rows where col is not NULL', 'Distinct values', 'Columns'], answer=1,
         why='COUNT(*) counts rows; COUNT(col) skips NULLs; COUNT(DISTINCT col) counts unique values.'),
    dict(q='Beginner: SELECT city, payment, COUNT(*) FROM orders GROUP BY city fails. Why?', options=['COUNT needs an alias', 'payment is neither grouped nor aggregated', 'GROUP BY needs ORDER BY', 'city must be numeric'], answer=1,
         why='Error 10025: Expression not in GROUP BY key \'payment\'.'),
    dict(q='Intermediate: How many rows does WITH ROLLUP produce for 2 cities × 4 payment modes?', options=['8', '10', '11', '15'], answer=2,
         why='8 detail + 2 city subtotals + 1 grand total = 11 (CUBE would add 4 payment subtotals: 15).'),
    dict(q='Intermediate: In a ROLLUP row, how do you know that NULL in city means “all cities”?', options=['You cannot', 'grouping(city) = 1', 'city = \'ALL\'', 'GROUPING__ID = 0'], answer=1,
         why='grouping() returns 1 for columns aggregated away in that row; GROUPING__ID combines these bits.'),
    dict(q='Intermediate: Why did percentile_approx return 271.04 when all amounts are multiples of 10?', options=['A bug', 'It interpolates between histogram bins', 'It rounds amounts', 'It uses DOUBLE averages'], answer=1,
         why='It is approximate and interpolates; exact percentile() works on integers but uses more memory.'),
    dict(q='Advanced: With hive.map.aggr=true, how many intermediate rows left the map stage for GROUP BY city in our lab?', options=['50,000', '8', '1', '2,000'], answer=1,
         why='Each map task sends one partial row per city; with the setting off, all 50,000 rows were shuffled.'),
    dict(q='Advanced: Why can a single reducer still be slow for COUNT(DISTINCT customer_id) GROUP BY restaurant_id?', options=['COUNT(DISTINCT) is not allowed', 'Distinct values of a hot key cannot be pre-summed, so they all reach one reducer', 'ORC files are slow', 'HAVING is missing'], answer=1,
         why='Use hive.groupby.skewindata, a two-level GROUP BY, or approximate counts.'),
])

REVISION = [
    'GROUP BY: one row per group. SELECT only grouping keys and aggregates (else error 10025).',
    '<code>COUNT(*)</code> rows · <code>COUNT(col)</code> non-NULL · <code>COUNT(DISTINCT a[, b])</code> unique values/combinations.',
    '<code>SUM AVG MIN MAX</code>, <code>collect_set</code>/<code>collect_list</code> (arrays), <code>percentile_approx</code> (interpolated), <code>stddev_pop</code>, <code>variance</code>, <code>corr</code>.',
    'WHERE filters rows before grouping; <b>HAVING</b> filters groups after, and may use aggregates.',
    '<code>GROUPING SETS ((a,b),(a),())</code> · <code>WITH ROLLUP</code> (hierarchy) · <code>WITH CUBE</code> (all combinations). Rolled-up columns are NULL; use <code>grouping(col)</code> / <code>GROUPING__ID</code>.',
    'Group by expressions by repeating them; <code>GROUP BY 1</code> only with <code>hive.groupby.position.alias=true</code>.',
    'Map-side aggregation (<code>hive.map.aggr</code>): 8 vs 50,000 shuffled rows in our lab; reducers merge partials; AVG travels as (sum, count).',
    'Skew: <code>hive.groupby.skewindata=true</code>, two-level GROUP BY instead of COUNT(DISTINCT), handle hot keys separately.',
]
FAQ = [
    ('What is the difference between GROUP BY and DISTINCT?', 'SELECT DISTINCT a, b returns the unique combinations of a and b; GROUP BY a, b returns the same rows but also lets you compute aggregates per group. Hive plans both as a shuffle by the keys. Use DISTINCT for unique lists, GROUP BY when you need counts or sums.'),
    ('Why are there NULLs in my ROLLUP or CUBE output?', 'In subtotal and total rows the columns that were aggregated away are shown as NULL. If the data itself can contain NULLs in those columns, use grouping(col) (1 means rolled up) or GROUPING__ID to tell them apart, and replace them with labels like “ALL” in reports.'),
    ('Is percentile_approx accurate enough?', 'For medians and percentiles of large numeric columns it is usually close, and it uses bounded memory. You can increase accuracy with a third argument (more histogram bins). For small groups or integer data where you need the exact value, percentile() is exact. Always label approximate numbers in reports.'),
    ('Does GROUP BY sort the result?', 'No guarantee. Results may look sorted because of how reducers emit rows, but only ORDER BY guarantees order. Add ORDER BY when the order matters.'),
    ('How do I speed up COUNT(DISTINCT) on huge tables?', 'Hive needs all distinct values to meet, which can bottleneck one reducer. Rewrite as SELECT COUNT(*) FROM (SELECT DISTINCT col FROM t) x, or a two-level GROUP BY when counting distinct per group; consider approximate distinct counting where small errors are acceptable; and keep statistics fresh so the optimiser picks good parallelism.'),
]

PRACTICE_INTRO = 'Programs on grouping, HAVING, distinct counts, rollups and shares, with the matching HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Orders per payment', stmt='Count orders per payment mode from a list.', inp='UPI, COD, UPI, Card, UPI, Wallet',
         code='''pays = ["UPI", "COD", "UPI", "Card", "UPI", "Wallet"]
counts = {}
for p in pays:
    counts[p] = counts.get(p, 0) + 1
print(counts)
''', explain='Hive: SELECT payment, COUNT(*) FROM orders GROUP BY payment.'),
    dict(level='easy', title='COUNT(*) vs COUNT(col)', stmt='For [200, None, 150, None, 90], print COUNT(*) and COUNT(col).', inp='[200, None, 150, None, 90]',
         code='''vals = [200, None, 150, None, 90]
print("COUNT(*):", len(vals), "| COUNT(col):", sum(v is not None for v in vals))
''', explain='5 and 3. AVG(col) also ignores NULLs: it would be 440 ÷ 3, not 440 ÷ 5.'),
    dict(level='easy', title='Distinct customers', stmt='How many distinct customers placed these orders?', inp='[1932, 1991, 722, 1932, 15, 722]',
         code='''print(len(set([1932, 1991, 722, 1932, 15, 722])))
''', explain='4. Hive: COUNT(DISTINCT customer_id).'),
    dict(level='medium', title='Sizes of grouping outputs', stmt='For 8 cities and 4 payment modes, how many rows do GROUP BY, ROLLUP and CUBE produce (all combinations present)?', inp='8 cities × 4 modes',
         code='''c, p = 8, 4
print("GROUP BY:", c * p)
print("ROLLUP  :", c * p + c + 1)
print("CUBE    :", c * p + c + p + 1)
''', explain='32, 41 and 45 rows. CUBE adds per-payment subtotals that ROLLUP does not.'),
    dict(level='medium', title='Average without losing precision', stmt='Two map tasks report (sum, count) = (7,210, 25) and (2,300, 8). Compute the correct average.', inp='(7210, 25), (2300, 8)',
         code='''parts = [(7210, 25), (2300, 8)]
print(round(sum(s for s, _ in parts) / sum(c for _, c in parts), 2))
''', explain='9,510 ÷ 33 = 288.18. This is exactly how Hive merges partial AVG results.'),
    dict(level='medium', title='Collect set per city', stmt='Build the set of payment modes per city (collect_set).', inp='(Pune, UPI), (Pune, COD), (Thane, Card), (Pune, UPI)',
         code='''rows = [("Pune", "UPI"), ("Pune", "COD"), ("Thane", "Card"), ("Pune", "UPI")]
sets = {}
for city, pay in rows:
    sets.setdefault(city, set()).add(pay)
print({c: sorted(s) for c, s in sets.items()})
''', explain='Pune → [COD, UPI], Thane → [Card]. In Hive the array order is not guaranteed; sort_array() makes it stable.'),
    dict(level='business', title='Refund abuse rule', stmt='Flag customers with 3 or more refunds in a month (GROUP BY customer HAVING COUNT(*) >= 3).', inp='refunds by customer id: 17, 42, 17, 99, 17, 42, 42, 8',
         code='''refunds = [17, 42, 17, 99, 17, 42, 42, 8]
counts = {}
for c in refunds:
    counts[c] = counts.get(c, 0) + 1
print("flag:", sorted(c for c, n in counts.items() if n >= 3))
''', explain='Customers 17 and 42. Hive: SELECT customer_id FROM orders WHERE status = \'REFUNDED\' GROUP BY customer_id HAVING COUNT(*) >= 3.'),
    dict(level='business', title='Cost of three scans vs one', stmt='A report reads a 1.5 TB table three times with UNION ALL at Rs 0.4 per GB scanned. What does switching to GROUPING SETS save per run and per year (daily)?', inp='1.5 TB × 3 scans vs 1 scan',
         code='''gb, rate = 1.5 * 1024, 0.4
saved = (3 - 1) * gb * rate
print(f"per run: Rs {saved:,.0f} | per year: Rs {saved * 365:,.0f}")
''', explain='About Rs 1,229 per run and Rs 4.5 lakh a year, for rewriting one query.'),
]

SCN_INTRO = 'Aggregation questions appear in every data interview. Expect HAVING vs WHERE, ROLLUP and a performance follow-up.'
SCENARIOS = (
    scn('Any company · SQL', 'Fresher', '“WHERE or HAVING?”',
        'The interviewer asks for cities with more than 6,000 orders, counting only delivered orders.',
        'do you place each filter correctly?',
        '''<pre>SELECT city, COUNT(*) AS orders
FROM orders
WHERE status = 'DELIVERED'          -- row filter, before grouping
GROUP BY city
HAVING COUNT(*) &gt; 6000;             -- group filter, after grouping</pre>''', 'putting COUNT(*) in WHERE.') +
    scn('Retail · reporting', 'Mid-level', 'Subtotals without UNION ALL',
        'A manager wants state, city and grand totals in one result set.',
        'do you know ROLLUP/GROUPING SETS?',
        '''<ul>
          <li><code>GROUP BY state, city WITH ROLLUP</code> gives (state, city), (state) and () in one scan.</li>
          <li>Use <code>grouping(city)</code> to label subtotal rows and avoid confusing NULLs.</li>
          <li>For custom combinations use <code>GROUPING SETS</code>; for every combination <code>CUBE</code>.</li>
        </ul>''', 'three separate queries stitched together.') +
    scn('Data engineering · performance', 'Mid-level', 'GROUP BY is slow on one reducer',
        'A daily job groups 3 billion events by app_id; one reducer runs for an hour while others finish in minutes.',
        'can you diagnose skew and use Hive’s tools?',
        '''<ol>
          <li>Find the hot key: <code>SELECT app_id, COUNT(*) … ORDER BY 2 DESC LIMIT 10</code>.</li>
          <li>Make sure <code>hive.map.aggr</code> is on (partial aggregation absorbs most skew for COUNT/SUM).</li>
          <li>For DISTINCT-style aggregates, enable <code>hive.groupby.skewindata</code> or use a two-level GROUP BY; process the hot key separately if needed.</li>
        </ol>''', '“increase the number of reducers”: the hot key still lands on one.') +
    scn('Analytics · statistics', 'Fresher', 'Median vs average',
        'Product asks for the “typical” order value per city. Averages look inflated by a few large orders.',
        'do you know robust statistics in Hive?',
        '''<ul>
          <li>Report the median with <code>percentile_approx(amount, 0.5)</code> alongside the average.</li>
          <li>Explain that the approximation interpolates (our lab gave 271.04) and round for presentation.</li>
          <li>Add p90 to show the tail.</li>
        </ul>''', 'reporting only AVG for skewed money data.')
)
