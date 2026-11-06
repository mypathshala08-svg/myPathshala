import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import tables
BODY = body(HERE)
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep

META = dict(
    module='03-querying', lesson='03-joins', n='3.3',
    module_label='Module 3 · Querying with HiveQL',
    title='Joins: inner, outer, semi, anti and cross',
    desc='Hive joins with real Hive 4.2.1 results: inner, left, right and full outer joins, LEFT SEMI JOIN, anti joins with NOT EXISTS (LEFT ANTI JOIN syntax rejected), CROSS JOIN, non-equi joins, multi-table star joins, the outer-join WHERE vs ON trap, NULL keys and <=>, join explosion, and map join vs shuffle join in EXPLAIN (BROADCAST_EDGE vs SIMPLE_EDGE).',
    og_desc='Six cities matched, three disappeared. Every Hive join type on real data, and how Hive decides between a map join and a shuffle join.',
    minutes=36, level='Beginner → Advanced',
    lead='Joins answer questions that span tables: revenue against targets, orders with customer plans, targets that have no orders yet. The join type decides which rows survive, and the execution strategy decides whether the big table crosses the network. This lesson runs every join type on TiffinGo data, shows the outer-join WHERE trap and NULL keys, and reads <code>EXPLAIN</code> to see a map join become a shuffle join. <b>All outputs are real</b>, from Hive 4.2.1.',
    chips=['Real Hive 4.2.1 outputs', 'Every join type', 'Map join vs shuffle join', 'Runs in your browser (Python)'],
)

MAIN = '''# Inner, left and full outer joins written by hand (None plays NULL)
revenue = {"Bengaluru": 2724070, "Chennai": 752250, "Mumbai": 2941120, "Pune": 2344660}
target = {"Bengaluru": 2600000, "Mumbai": 2800000, "Nashik": 500000, "Pune": 2000000}

inner = [(c, revenue[c], target[c]) for c in revenue if c in target]
left = [(c, revenue[c], target.get(c)) for c in revenue]
full = [(c, revenue.get(c), target.get(c)) for c in sorted(set(revenue) | set(target))]

print("inner:", len(inner), inner)
print("left :", len(left), [r for r in left if r[2] is None])
print("full :", len(full), [r for r in full if None in r])
'''
RUN = dict(
    heading='Run the code: joins with dictionaries',
    intro='<p>Joins are just matching keys. These programs build inner, outer, semi and anti joins, a broadcast (map) join, and show how duplicate keys multiply rows. The numbers are the real revenue figures from the lab. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('inner = [(c, revenue[c], target[c]) for c in revenue if c in target]', 'Inner join: keep a key only if it exists on both sides.'),
        ('left = [(c, revenue[c], target.get(c)) for c in revenue]', 'Left join: every left key; <code>.get</code> returns None (NULL) when there is no partner.'),
        ('full = [(c, revenue.get(c), target.get(c)) for c in sorted(set(revenue) | set(target))]', 'Full outer join: the union of keys from both sides.'),
    ],
    tasks=[
        dict(label='1 · Inner, left, full', hint='Press <b>Run</b>. Then add <code>"Thane": 1408910</code> to revenue only and predict the three counts.', code=None),
        dict(label='2 · Semi and anti', hint='<b>Predict first:</b> which target cities have orders, and which do not?',
             code='''target_cities = ["Bengaluru", "Delhi", "Mumbai", "Nashik", "Pune"]
order_cities = ["Pune", "Pune", "Mumbai", "Bengaluru", "Delhi", "Pune"]
have = set(order_cities)
print("semi:", [c for c in target_cities if c in have])       # LEFT SEMI JOIN
print("anti:", [c for c in target_cities if c not in have])   # NOT EXISTS
'''),
        dict(label='3 · Map (broadcast) join', hint='The small table becomes an in-memory dictionary; the big table is streamed once. No sorting or shuffling needed.',
             code='''targets = {"Mumbai": "West", "Pune": "West", "Bengaluru": "South"}   # small: broadcast
orders = [(100001, "Mumbai"), (100002, "Chennai"), (100003, "Pune")]  # big: streamed
for order_id, city in orders:
    region = targets.get(city)
    if region is not None:                 # inner join
        print(order_id, city, region)
'''),
        dict(label='4 · Join explosion', hint='Customer 17 has 3 addresses and 2 orders. How many rows does the join produce? Make addresses unique to fix it.',
             code='''orders = [(1, 17, 200), (2, 17, 300), (3, 42, 150)]
addresses = [(17, "Kharghar"), (17, "Vashi"), (17, "Panvel"), (42, "Thane")]
joined = [(o, a) for o in orders for a in addresses if o[1] == a[0]]
print("rows:", len(joined), "| revenue:", sum(o[2] for o, a in joined), "(true revenue 650)")
'''),
        dict(label='5 · Spot the error', hint='This “left join” then filters on the right table’s region, like a WHERE clause. The check fails because cities without a target vanish. Move the condition into the matching step (ON).', expect='error',
             code='''revenue = ["Bengaluru", "Chennai", "Mumbai"]
region = {"Bengaluru": "South", "Mumbai": "West"}
left = [(c, region.get(c)) for c in revenue]
result = [(c, r) for c, r in left if r == "West"]       # WHERE t.region = 'West'
assert len(result) == len(revenue), f"left join lost rows: {result}"
print(result)
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: the small tables, CROSS and range joins',
    intro='<p>Create the two small dimension tables used in this lesson, then try a cross join and a range join. <b>Outputs are real</b>, from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · Create the targets and price bands', cmd="CREATE TABLE city_targets (city STRING, monthly_target DECIMAL(12,2), region STRING) STORED AS ORC;\nINSERT INTO city_targets VALUES ('Mumbai', 2800000, 'West'), ('Pune', 2000000, 'West'),\n  ('Thane', 1300000, 'West'), ('Bengaluru', 2600000, 'South'), ('Hyderabad', 1700000, 'South'),\n  ('Delhi', 1600000, 'North'), ('Nashik', 500000, 'West');\nCREATE TABLE price_bands (band STRING, lo DECIMAL(10,2), hi DECIMAL(10,2)) STORED AS ORC;\nINSERT INTO price_bands VALUES ('small', 0, 299.99), ('medium', 300, 599.99), ('large', 600, 99999);\nSELECT COUNT(*) AS right_rows FROM (SELECT city FROM orders GROUP BY city) s RIGHT JOIN city_targets t ON s.city = t.city;", file='Beeline',
             output='+-------------+\n| right_rows  |\n+-------------+\n| 7           |\n+-------------+',
             note='The right join keeps all 7 target cities; one of them (Nashik) has no revenue.'),
        dict(title='2 · Cross join and a range (non-equi) join', cmd="SELECT COUNT(*) AS pairs FROM city_targets CROSS JOIN (SELECT DISTINCT payment FROM orders) p;\nSELECT b.band, COUNT(*) AS n FROM orders o\nJOIN price_bands b ON o.amount BETWEEN b.lo AND b.hi\nGROUP BY b.band ORDER BY n DESC;", file='Beeline',
             output='+--------+\n| pairs  |\n+--------+\n| 28     |\n+--------+\n+---------+--------+\n| b.band  |   n    |\n+---------+--------+\n| small   | 26116  |\n| medium  | 21848  |\n| large   | 2036   |\n+---------+--------+',
             note='7 cities × 4 payment modes = 28 pairs. The range join gives exactly the same counts as the CASE expression in Lesson 3.2: two methods, one answer.'),
        dict(title='3 · A three-table star join', cmd="SELECT c.plan, t.region, COUNT(*) AS orders, SUM(o.amount) AS revenue\nFROM orders o\nJOIN customers c ON o.customer_id = c.customer_id\nJOIN city_targets t ON o.city = t.city\nWHERE o.status = 'DELIVERED'\nGROUP BY c.plan, t.region ORDER BY revenue DESC LIMIT 5;", file='Beeline',
             output=tables(open(CAP + 'l33_multi.txt').read())[1],
             note='Basic-plan customers in the West bring the most delivered revenue. Orders from Chennai and Navi Mumbai are not counted here because those cities have no target row: the inner join dropped them.'),
    ],
)

TRACE = dict(
    heading='A broadcast join, one order at a time',
    intro='<p>The small targets table is loaded into a dictionary once; then each order looks up its city. Watch which orders find a partner.</p>',
    code='''targets = {"Mumbai": 2800000, "Pune": 2000000}
orders = [("Pune", 410), ("Chennai", 230), ("Mumbai", 530)]
joined = []
for city, amount in orders:
    t = targets.get(city)
    if t is not None:
        joined.append((city, amount, t))
print(joined)
''',
    notes={1: 'Build :: The small table is loaded into memory (the broadcast side).', 5: 'Probe :: Look up each streamed row; Chennai has no partner.'},
)

WORKED_INTRO = 'Three join tasks from TiffinGo’s analytics team: an achievement report that keeps every city, a reconciliation that finds gaps on both sides, and a check that catches join explosion before it reaches a dashboard.'
EXAMPLES = [
    dict(level='b', tag='Reporting · left join', title='Target achievement per city',
         problem='<p>For every city with revenue, print revenue, target and achievement %, or “no target” when the target is missing. This is <code>s LEFT JOIN city_targets</code>.</p>',
         inp='Real revenue and targets from the lab (four cities)',
         approach=['Loop over revenue cities.', 'Look up the target; None means no partner.', 'Print achievement or a label.'],
         code='''revenue = {"Chennai": 752250, "Mumbai": 2941120, "Pune": 2344660, "Thane": 1408910}
target = {"Mumbai": 2800000, "Pune": 2000000, "Thane": 1300000}
for city, rev in revenue.items():
    t = target.get(city)
    print(f"{city:8} {rev:>9,}  " + (f"{rev / t:.0%} of target" if t else "no target"))
''', notes={4: 'Left :: Missing target is None, not a dropped row.'},
         tryit='In Hive: SELECT s.city, s.revenue, t.monthly_target, ROUND(100 * s.revenue / t.monthly_target) FROM s LEFT JOIN city_targets t ON s.city = t.city. Dividing by NULL gives NULL, so label it with COALESCE.'),
    dict(level='i', tag='Reconciliation · full outer', title='Find gaps on both sides',
         problem='<p>Finance has a list of settled order ids from the payment gateway; Hive has delivered order ids. List orders delivered but not settled, and settled but not delivered: a full outer join on order_id.</p>',
         inp='delivered: 101–106 · settled: 102, 103, 105, 106, 109',
         approach=['Turn both lists into sets.', 'Left only = delivered − settled; right only = settled − delivered.', 'Matched = intersection.'],
         code='''delivered = {101, 102, 103, 104, 105, 106}
settled = {102, 103, 105, 106, 109}
print("matched           :", sorted(delivered & settled))
print("delivered, unpaid :", sorted(delivered - settled))
print("paid, not delivered:", sorted(settled - delivered))
''', notes={4: 'Gaps :: The rows with NULL on one side of a full outer join.'},
         tryit='Hive: SELECT COALESCE(d.order_id, s.order_id), d.order_id IS NULL AS missing_delivery, s.order_id IS NULL AS missing_settlement FROM delivered d FULL OUTER JOIN settled s ON d.order_id = s.order_id WHERE d.order_id IS NULL OR s.order_id IS NULL.'),
    dict(level='a', tag='Quality · explosion check', title='Catch join explosion before publishing',
         problem='<p>Before joining orders to a customer-address table, verify that each customer has exactly one address, and compare the row count before and after the join.</p>',
         inp='orders 3 rows · addresses with customer 17 twice',
         approach=['Count addresses per customer; any count > 1 is a risk.', 'Do the join and compare counts.', 'Fail the job if counts differ.'],
         code='''orders = [(1, 17), (2, 17), (3, 42)]
addresses = [(17, "Kharghar"), (17, "Vashi"), (42, "Thane")]
per_cust = {}
for c, _ in addresses:
    per_cust[c] = per_cust.get(c, 0) + 1
dupes = [c for c, n in per_cust.items() if n > 1]
joined = [(o, a) for o in orders for a in addresses if o[1] == a[0]]
print("duplicate keys:", dupes, "| rows before:", len(orders), "after:", len(joined))
print("FAIL: fix duplicates" if len(joined) != len(orders) else "OK")
''', notes={6: 'Check :: Keys that should be unique, but are not.'},
         tryit='Keep only one address per customer (for example the latest) and the counts match again. In Hive use ROW_NUMBER() (Lesson 3.6) to pick one row per customer.'),
]

QUIZ = mix([
    dict(q='Beginner: Which join returns only rows that match on both sides?', options=['LEFT OUTER JOIN', 'INNER JOIN', 'FULL OUTER JOIN', 'CROSS JOIN'], answer=1,
         why='Our inner join returned 6 cities; three unmatched ones were dropped.'),
    dict(q='Beginner: In a LEFT JOIN, what appears in the right-side columns for an unmatched left row?', options=['0', 'An empty string', 'NULL', 'The left value'], answer=2,
         why='Chennai and Navi Mumbai showed monthly_target NULL.'),
    dict(q='Beginner: How many rows does a CROSS JOIN of 7 cities and 4 payment modes return?', options=['7', '11', '28', '4'], answer=2,
         why='Every combination: 7 × 4 = 28 (real result).'),
    dict(q='Intermediate: Which query finds target cities with no orders in Hive 4.2.1?', options=['t LEFT ANTI JOIN orders o ON …', 't LEFT SEMI JOIN orders o ON …', 'SELECT … FROM t WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.city = t.city)', 't CROSS JOIN orders'], answer=2,
         why='LEFT ANTI JOIN was rejected as syntax in our lab; NOT EXISTS returned Nashik.'),
    dict(q='Intermediate: A LEFT JOIN has WHERE t.region = \'West\'. What happens?', options=['Nothing changes', 'Rows with NULL region are removed, so it behaves like an inner join', 'Hive raises an error', 'Only right rows are kept'], answer=1,
         why='3 rows instead of 8. Put right-side conditions in ON to keep the left rows.'),
    dict(q='Intermediate: Do NULL join keys match each other with ON a.k = b.k?', options=['Yes', 'No; use <=> if NULL should match NULL', 'Only in outer joins', 'Only for strings'], answer=1,
         why='NULL = NULL is NULL. With <=> the NULL rows joined.'),
    dict(q='Advanced: In EXPLAIN, what does “Map 1 <- Map 2 (BROADCAST_EDGE)” with a Map Join Operator indicate?', options=['A shuffle join', 'The small table from Map 2 is broadcast to Map 1 and joined there without a reducer', 'A cross join', 'A failed join'], answer=1,
         why='With hive.auto.convert.join=false the plan became a Merge Join in Reducer 2 with two SIMPLE_EDGEs.'),
    dict(q='Advanced: Revenue doubled after joining orders to an address table. Most likely cause?', options=['Map join', 'Duplicate keys on the address side multiplied rows', 'NULL keys', 'ORC compression'], answer=1,
         why='Check key uniqueness and compare row counts before and after joins.'),
])

REVISION = [
    '<b>INNER</b>: matches only · <b>LEFT/RIGHT/FULL OUTER</b>: keep unmatched rows of one/both sides with NULLs · <b>CROSS</b>: every combination.',
    '<b>LEFT SEMI JOIN</b>: left rows with a match, left columns only, no duplicates (right table only in ON).',
    '<b>Anti join</b>: <code>NOT EXISTS (…)</code> or <code>LEFT JOIN … WHERE r.key IS NULL</code> (LEFT ANTI JOIN syntax rejected in Hive 4.2.1).',
    'Joins happen <b>before WHERE</b>: right-side filters of a LEFT JOIN go in <b>ON</b>, or the join becomes inner.',
    'NULL keys never match with <code>=</code>; <code>&lt;=&gt;</code> makes NULL match NULL. Non-equi ON (BETWEEN) allowed since Hive 2.2.',
    '<b>Map join</b>: small table broadcast (<code>BROADCAST_EDGE</code>, <code>Map Join Operator</code>), automatic via <code>hive.auto.convert.join</code>. <b>Shuffle join</b>: <code>Merge Join</code> in a reducer, two <code>SIMPLE_EDGE</code>s.',
    'Duplicate keys multiply rows (join explosion): check uniqueness, compare counts before and after.',
    'Outer joins are not commutative; joins evaluate left to right; same-key joins can share a stage; skew → filter NULL keys, skew-join settings, salting.',
]
FAQ = [
    ('What is the difference between LEFT SEMI JOIN and INNER JOIN?', 'An inner join returns one row per matching pair and can include columns from both tables, so a left row with several matches appears several times. LEFT SEMI JOIN returns each left row at most once, only with left columns, which makes it the efficient form of IN/EXISTS. Our target cities appeared once each although Pune has 7,930 matching orders.'),
    ('Why did Hive reject LEFT ANTI JOIN?', 'In our Hive 4.2.1 lab the parser did not accept LEFT ANTI JOIN as a join type. Hive can still execute anti joins: write NOT EXISTS (correlated subquery) or a LEFT JOIN with WHERE right.key IS NULL; the optimiser can turn these into efficient anti-join plans internally.'),
    ('When does Hive choose a map join?', 'When hive.auto.convert.join is true (default) and the optimiser estimates that the smaller inputs fit under the configured size threshold (hive.auto.convert.join.noconditionaltask.size). Good statistics are essential: if Hive thinks a big table is small it can run out of memory; if it thinks a small table is big it does an unnecessary shuffle. RIGHT and FULL outer joins cannot broadcast the side whose unmatched rows must be kept.'),
    ('Is the old MAPJOIN hint still needed?', 'Rarely. Automatic conversion is preferred and the hint is ignored by default in modern Hive (hive.ignore.mapjoin.hint). Keep statistics fresh and check EXPLAIN instead of forcing join strategies.'),
    ('How do I join on a date range, like an order and the price list valid at that time?', 'Use a non-equi condition in ON: ON o.item_id = p.item_id AND o.order_ts >= p.valid_from AND o.order_ts < p.valid_to. Equality conditions on keys keep it efficient; pure range joins with no equality key can be expensive on big tables.'),
]

PRACTICE_INTRO = 'Programs that practise each join type, NULL keys and join checks, with the matching HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Inner join count', stmt='How many cities appear in both lists?', inp='A: Pune, Thane, Mumbai, Chennai · B: Mumbai, Pune, Nashik',
         code='''a = {"Pune", "Thane", "Mumbai", "Chennai"}
b = {"Mumbai", "Pune", "Nashik"}
print(sorted(a & b))
''', explain='Mumbai and Pune. Hive: SELECT a.city FROM a JOIN b ON a.city = b.city.'),
    dict(level='easy', title='Left join NULLs', stmt='Left-join A to B and print cities whose B side is missing.', inp='same lists',
         code='''a = ["Pune", "Thane", "Mumbai", "Chennai"]
b = {"Mumbai", "Pune", "Nashik"}
print([c for c in a if c not in b])
''', explain='Thane and Chennai get NULLs on the right. Nashik does not appear: it exists only on the right side.'),
    dict(level='easy', title='Cross join size', stmt='3 price bands × 8 cities × 4 payment modes: how many rows?', inp='3, 8, 4',
         code='''print(3 * 8 * 4)
''', explain='96 rows. Cross joins grow multiplicatively; never cross join two big tables by accident.'),
    dict(level='medium', title='Anti join', stmt='Customers who signed up but never ordered.', inp='customers 1–8 · order customer ids [2, 2, 5, 7, 1]',
         code='''customers = range(1, 9)
ordered = set([2, 2, 5, 7, 1])
print([c for c in customers if c not in ordered])
''', explain='[3, 4, 6, 8]. Hive: SELECT c.customer_id FROM customers c WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id).'),
    dict(level='medium', title='Range join', stmt='Assign each amount to a band: small < 300, medium 300–599.99, large ≥ 600, using a band table and a range test.', inp='amounts 120, 300, 599.99, 600',
         code='''bands = [("small", 0, 299.99), ("medium", 300, 599.99), ("large", 600, 99999)]
for a in [120, 300, 599.99, 600]:
    print(a, [b for b, lo, hi in bands if lo <= a <= hi])
''', explain='Each amount falls in exactly one band. Gaps or overlaps in a range table cause lost or duplicated rows: test the table itself.'),
    dict(level='medium', title='Rows after a duplicate-key join', stmt='Left table has keys [1, 1, 2]; right has [1, 1, 1, 2, 3]. How many rows does an inner join return?', inp='[1,1,2] ⋈ [1,1,1,2,3]',
         code='''left, right = [1, 1, 2], [1, 1, 1, 2, 3]
print(sum(1 for l in left for r in right if l == r))
''', explain='2 × 3 + 1 × 1 = 7 rows from 3 left rows. This multiplication is join explosion.'),
    dict(level='business', title='Unsettled orders value', stmt='Delivered orders 101–106 with amounts; gateway settled 102, 103, 105, 106. What value is delivered but unsettled?', inp='amounts {101: 220, 102: 150, 103: 180, 104: 310, 105: 90, 106: 60}',
         code='''amount = {101: 220, 102: 150, 103: 180, 104: 310, 105: 90, 106: 60}
settled = {102, 103, 105, 106}
missing = {k: v for k, v in amount.items() if k not in settled}
print(missing, "total Rs", sum(missing.values()))
''', explain='Orders 101 and 104, Rs 530 to chase with the payment gateway. A daily anti join drives the reconciliation queue.'),
    dict(level='business', title='Broadcast or shuffle?', stmt='The broadcast threshold is 10 MB per small table in this cluster. Decide the strategy for: city_targets 0.01 MB, customers 180 MB, price_bands 0.001 MB.', inp='three dimension sizes',
         code='''limit = 10
for name, mb in [("city_targets", 0.01), ("customers", 180), ("price_bands", 0.001)]:
    print(f"{name:13} {'map join (broadcast)' if mb <= limit else 'shuffle join'}")
''', explain='Customers is too big to broadcast under this limit. Real thresholds are configurable; check EXPLAIN for BROADCAST_EDGE vs SIMPLE_EDGE.'),
]

SCN_INTRO = 'Join questions are guaranteed in data interviews. Strong answers cover semantics, NULLs and the execution strategy.'
SCENARIOS = (
    scn('Any company · SQL', 'Fresher', '“Rows disappeared after my join”',
        'A report of revenue per city loses cities after joining a targets table.',
        'do you understand inner vs outer joins?',
        '''<ul>
          <li>An inner join keeps only matches; cities without a target are dropped.</li>
          <li>Use <code>LEFT JOIN</code> from the revenue side to keep every city; show NULL targets as “no target”.</li>
          <li>Use <code>FULL OUTER JOIN</code> to also see targets with no revenue.</li>
        </ul>''', 'adding fake targets to make the inner join work.') +
    scn('Analytics · subtle bug', 'Mid-level', 'A LEFT JOIN that behaves like INNER',
        'SELECT … FROM revenue r LEFT JOIN targets t ON r.city = t.city WHERE t.region = \'West\' returns fewer rows than expected.',
        'do you know join-then-WHERE semantics?',
        '''<ol>
          <li>The join runs first; WHERE then removes rows where t.region is NULL, i.e. all unmatched cities.</li>
          <li>Move the condition to ON (<code>… ON r.city = t.city AND t.region = 'West'</code>) to filter which target rows match, keeping all revenue rows.</li>
          <li>If the intention is “only West cities”, the inner join is fine; be explicit.</li>
        </ol>''', 'blaming Hive for losing rows.') +
    scn('Data engineering · performance', 'Mid-level', 'A join that should be instant takes 30 minutes',
        'Orders (2 TB) join a 50 KB cities table. EXPLAIN shows Merge Join with two SIMPLE_EDGEs.',
        'can you read plans and fix join strategy?',
        '''<ul>
          <li>The small table should be broadcast (map join). Hive did not convert, probably because of missing or wrong statistics or a disabled setting.</li>
          <li>Run <code>ANALYZE TABLE cities COMPUTE STATISTICS</code>, check <code>hive.auto.convert.join</code>, re-check EXPLAIN for <code>BROADCAST_EDGE</code>.</li>
          <li>Also filter orders early to reduce the data streamed.</li>
        </ul>''', 'forcing hints before checking statistics.') +
    scn('Finance · reconciliation', 'Mid-level', 'Find orders missing in the payment system',
        'You must list delivered orders with no settlement record, daily, on 50 million rows.',
        'can you write an efficient anti join?',
        '''<pre>SELECT d.order_id, d.amount
FROM delivered d
WHERE NOT EXISTS (SELECT 1 FROM settlements s
                  WHERE s.order_id = d.order_id);</pre>
        <p>Filter both sides to the same date range first, and make sure order_id has no NULLs (NULLs never match and would all appear as “missing”).</p>''', 'NOT IN on a column that may contain NULL (returns nothing; Lesson 3.5).')
)
