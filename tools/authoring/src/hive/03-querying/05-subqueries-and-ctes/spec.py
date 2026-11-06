import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
BODY = body(HERE)

META = dict(
    module='03-querying', lesson='05-subqueries-and-ctes', n='3.5',
    module_label='Module 3 · Querying with HiveQL',
    title='Subqueries, CTEs and UNION',
    desc='Subqueries in FROM (alias required), IN, EXISTS, correlated and scalar subqueries in WHERE, HAVING and SELECT, the NOT IN with NULL trap and NOT EXISTS, common table expressions (WITH) and CTE materialisation, UNION ALL vs UNION, INTERSECT, EXCEPT and MINUS, all with real Hive 4.2.1 results.',
    og_desc='One NULL makes NOT IN return nothing. Subqueries, CTEs and set operations in Hive, with real results and the traps explained.',
    minutes=30, level='Beginner → Advanced',
    lead='Real questions need several steps: compute revenue per city, then the average, then compare. Hive lets one query use another in FROM, in WHERE and as named steps with <code>WITH</code>. This lesson rewrites a nested report as readable CTEs, reproduces the famous NOT IN trap that returns zero rows, and compares lists with UNION, INTERSECT and EXCEPT. <b>All outputs are real</b>, from Hive 4.2.1.',
    chips=['Real Hive 4.2.1 outputs', 'The NOT IN trap', 'CTEs and set operations', 'Runs in your browser (Python)'],
)

MAIN = '''# CTE-style steps in Python: each step is a named result built from the previous ones
orders = [("Mumbai", 590), ("Pune", 410), ("Mumbai", 530), ("Thane", 300),
          ("Pune", 460), ("Delhi", 310), ("Mumbai", 500), ("Thane", 250)]

city_rev = {}                                         # WITH city_rev AS (... GROUP BY city)
for city, amount in orders:
    city_rev[city] = city_rev.get(city, 0) + amount

avg_rev = sum(city_rev.values()) / len(city_rev)     # avg_rev AS (SELECT AVG(revenue) ...)

for city, rev in sorted(city_rev.items(), key=lambda kv: -kv[1]):   # final SELECT
    if rev > avg_rev:
        print(f"{city:7} {rev:5}  {rev / avg_rev:.2f}x average")
'''
RUN = dict(
    heading='Run the code: steps, subqueries and the NOT IN trap',
    intro='<p>These programs mirror the lesson: named steps like CTEs, an IN filter, NOT IN with three-valued logic (None plays NULL) and set operations with Python sets. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('city_rev = {}                                         # WITH city_rev AS (... GROUP BY city)', 'Step 1 has a name and can be printed on its own: that is the testability CTEs give you.'),
        ('avg_rev = sum(city_rev.values()) / len(city_rev)     # avg_rev AS (SELECT AVG(revenue) ...)', 'Step 2 reads step 1, like a CTE reading an earlier CTE.'),
    ],
    tasks=[
        dict(label='1 · Named steps', hint='Press <b>Run</b>. Then print <code>city_rev</code> and <code>avg_rev</code> separately, as you would test each CTE.', code=None),
        dict(label='2 · IN subquery', hint='<b>Predict first:</b> how many orders belong to Gold customers?',
             code='''customers = {1: "Gold", 2: "Basic", 3: "Gold", 4: "Silver"}
orders = [(101, 1), (102, 2), (103, 3), (104, 1), (105, 4)]
gold = {c for c, plan in customers.items() if plan == "Gold"}        # the subquery
print([oid for oid, cust in orders if cust in gold])                  # WHERE customer_id IN (...)
'''),
        dict(label='3 · NOT IN with three-valued logic', hint='Each comparison with None is unknown. Run with and without the None in the list.',
             code='''def not_in(x, values):
    result = True
    for v in values:
        if v is None:
            result = None if result else result     # unknown
        elif x == v:
            return False
    return result
lst = ["Pune", "Mumbai", None]
for city in ["Nashik", "Pune"]:
    print(city, "NOT IN", lst, "->", not_in(city, lst))
'''),
        dict(label='4 · Set operations', hint='UNION, INTERSECT and EXCEPT are set union, intersection and difference. Real city lists from the lab.',
             code='''orders = {"Bengaluru", "Chennai", "Delhi", "Hyderabad", "Mumbai", "Navi Mumbai", "Pune", "Thane"}
targets = {"Bengaluru", "Delhi", "Hyderabad", "Mumbai", "Nashik", "Pune", "Thane"}
print("INTERSECT:", sorted(orders & targets))
print("targets EXCEPT orders:", sorted(targets - orders))
print("orders EXCEPT targets:", sorted(orders - targets))
print("UNION:", len(orders | targets), "cities")
'''),
        dict(label='5 · Spot the error', hint='The coupon job uses NOT IN against a list that now contains None (guest orders). The check fails because nobody is selected. Rewrite as “not exists”: keep customers that have no equal value in the list.', expect='error',
             code='''recent = [17, 42, None]                    # customer ids with recent orders
customers = [8, 17, 23, 42]
def not_in(x, values):
    if x in [v for v in values if v is not None]: return False
    return None if None in values else True
selected = [c for c in customers if not_in(c, recent) is True]
assert selected == [8, 23], f"selected {selected}: one NULL made NOT IN unknown for everyone"
print(selected)
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: errors and settings',
    intro='<p>Two common errors and one setting. <b>Outputs are real</b>, from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · UNION with different columns', cmd='SELECT city FROM city_targets UNION ALL SELECT city, region FROM city_targets;', file='Beeline',
             output=open(CAP + 'l35_unionerr.txt').read().split('; Query ID')[0],
             note='Both sides of a set operation need the same number of columns with compatible types. Add a NULL or constant column to the shorter side if needed.'),
        dict(title='2 · When are CTEs materialised?', cmd='SET hive.optimize.cte.materialize.threshold;', file='Beeline',
             output='+--------------------------------------------+\n|                    set                     |\n+--------------------------------------------+\n| hive.optimize.cte.materialize.threshold=3  |\n+--------------------------------------------+',
             note='A CTE referenced at least 3 times in a query is computed once into a temporary table; otherwise it is inlined like a view. Materialising saves repeated work for expensive CTEs.'),
        dict(title='3 · Derived tables need a name', cmd='SELECT city, revenue FROM (SELECT city, SUM(amount) AS revenue FROM orders GROUP BY city)\nWHERE revenue > 2000000;', file='Beeline',
             output=open(CAP + 'l35_from.txt').read().split('Error: ')[1].split('; Query ID')[0].join(['Error: ', '']),
             note='Add an alias after the closing bracket: <code>… GROUP BY city) r WHERE …</code>.'),
    ],
)

TRACE = dict(
    heading='Evaluating NOT IN with a NULL, one comparison at a time',
    intro='<p>Watch the result for Nashik start as true and become unknown when the comparison with None (NULL) is reached.</p>',
    code='''values = ["Pune", "Mumbai", None]
x = "Nashik"
result = True
for v in values:
    if v is None:
        result = None
    elif v == x:
        result = False
print("Nashik NOT IN list ->", result)
''',
    notes={6: 'NULL :: x <> NULL is unknown, so the AND-chain becomes unknown.', 9: 'Result :: Unknown is not true, so WHERE would drop Nashik.'},
)

WORKED_INTRO = 'Three multi-step questions from TiffinGo: cities above average, customers who ordered big, and a safe lapsed-customer list.'
EXAMPLES = [
    dict(level='b', tag='Reporting · scalar subquery', title='Orders far above the average',
         problem='<p>List orders whose amount is more than 2.5 × the average order, as <code>WHERE amount &gt; (SELECT AVG(amount) * 2.5 FROM orders)</code>.</p>',
         inp='amounts: 290, 300, 880, 250, 310, 280, 270, 260, 300, 240',
         approach=['Compute the average once (the scalar subquery).', 'Multiply by 2.5.', 'Keep amounts above the threshold.'],
         code='''amounts = [290, 300, 880, 250, 310, 280, 270, 260, 300, 240]
threshold = sum(amounts) / len(amounts) * 2.5
print("threshold:", round(threshold, 2))
print([a for a in amounts if a > threshold])
''', notes={2: 'Scalar :: One value, computed before the filter.'},
         tryit='Large outliers raise the average itself. Try a median-based threshold instead and compare.'),
    dict(level='i', tag='Segments · EXISTS', title='Customers with at least one big order',
         problem='<p>Count customers having at least one order of Rs 800 or more, as a correlated <code>EXISTS</code>. Each customer should be counted once.</p>',
         inp='orders (customer, amount): (1, 820), (1, 840), (2, 300), (3, 880), (4, 120)',
         approach=['For each customer, ask whether any of their orders is ≥ 800.', 'Count customers, not orders.', 'Compare with a naive count of big orders.'],
         code='''orders = [(1, 820), (1, 840), (2, 300), (3, 880), (4, 120)]
customers = [1, 2, 3, 4]
exists = [c for c in customers if any(cust == c and amt >= 800 for cust, amt in orders)]
print("customers (EXISTS):", exists, "->", len(exists))
print("big orders (JOIN would count):", sum(1 for _, a in orders if a >= 800))
''', notes={3: 'EXISTS :: Stops at the first match per customer.'},
         tryit='The real lab answer was 51 customers. A JOIN without DISTINCT would count big orders instead (3 here vs 2 customers).'),
    dict(level='a', tag='Robustness · NULL-safe anti join', title='A lapsed-customer list that survives NULLs',
         problem='<p>Customers with no order in the last 30 days. Recent order customer ids include None (guest orders). Implement NOT IN (wrong) and NOT EXISTS (right) and compare.</p>',
         inp='customers [8, 17, 23, 42] · recent ids [17, 42, None]',
         approach=['NOT IN: unknown when the list has a None and no match.', 'NOT EXISTS: keep customers with no equal id in the list (None never equals anything).', 'Print both.'],
         code='''customers = [8, 17, 23, 42]
recent = [17, 42, None]
def not_in(x):
    if x in [r for r in recent if r is not None]: return False
    return None if None in recent else True
not_in_rows = [c for c in customers if not_in(c) is True]
not_exists_rows = [c for c in customers if not any(r == c for r in recent if r is not None)]
print("NOT IN    :", not_in_rows)
print("NOT EXISTS:", not_exists_rows)
''', notes={7: 'Safe :: NULL never equals a customer id, so it cannot hide anyone.'},
         tryit='Remove None from recent: both methods agree. That is why the bug appears only when new data introduces NULLs.'),
]

QUIZ = mix([
    dict(q='Beginner: What does Hive require for a subquery in the FROM clause?', options=['A LIMIT', 'An alias (a name)', 'An ORDER BY', 'A GROUP BY'], answer=1,
         why='Without an alias the lab gave a ParseException “cannot recognize input … in subquery source”.'),
    dict(q='Beginner: Which keyword starts a common table expression?', options=['DEFINE', 'WITH', 'TEMP', 'USING'], answer=1,
         why='WITH city_rev AS (…), avg_rev AS (…) SELECT …'),
    dict(q='Beginner: UNION ALL vs UNION?', options=['Same thing', 'UNION ALL keeps duplicates; UNION removes them', 'UNION keeps duplicates', 'UNION ALL sorts the result'], answer=1,
         why='10 rows vs 7 distinct cities in the lab.'),
    dict(q='Intermediate: city NOT IN (list) where the list contains a NULL returns…', options=['Rows not in the list', 'No rows at all', 'Only NULL rows', 'An error'], answer=1,
         why='The condition is NULL for every row that does not match, so WHERE drops everything. Use NOT EXISTS.'),
    dict(q='Intermediate: Which returns cities with a target but no orders?', options=['targets INTERSECT orders', 'targets EXCEPT orders', 'orders EXCEPT targets', 'targets UNION orders'], answer=1,
         why='Nashik. MINUS is a synonym for EXCEPT.'),
    dict(q='Intermediate: How does Hive usually execute IN and EXISTS subqueries?', options=['Row by row loops', 'As semi joins (and anti joins for NOT EXISTS)', 'By materialising every subquery', 'They are not supported'], answer=1,
         why='The optimiser rewrites them into join plans; check EXPLAIN.'),
    dict(q='Advanced: When does Hive materialise a CTE instead of inlining it?', options=['Always', 'Never', 'When it is referenced at least hive.optimize.cte.materialize.threshold times (3 in our lab)', 'Only for ORC tables'], answer=2,
         why='Below the threshold CTEs are inlined like views.'),
    dict(q='Advanced: Which subquery placement did Hive 4.2.1 accept in our tests?', options=['Only FROM', 'FROM and WHERE only', 'FROM, WHERE, HAVING and the SELECT list (scalar)', 'None'], answer=2,
         why='A correlated scalar subquery in SELECT counted orders per target city.'),
])

REVISION = [
    'Subquery in <b>FROM</b> = derived table, <b>alias required</b>.',
    '<b>IN</b>, <b>EXISTS</b> (correlated allowed) in WHERE; Hive turns them into semi joins; NOT EXISTS → anti join.',
    '<b>Scalar subquery</b> (one value) in WHERE, HAVING and, in Hive 4, the SELECT list.',
    '<b>NOT IN + NULL</b> in the list → zero rows. Use <b>NOT EXISTS</b> or filter NULLs inside the subquery.',
    '<b>WITH a AS (…), b AS (…)</b>: named, statement-scoped steps; later CTEs can use earlier ones. Inlined unless used ≥ <code>hive.optimize.cte.materialize.threshold</code> (3) times.',
    '<b>UNION ALL</b> keeps duplicates; <b>UNION</b> removes them (extra shuffle). Same column count and compatible types required.',
    '<b>INTERSECT</b> (common), <b>EXCEPT</b> / <b>MINUS</b> (first minus second), distinct by default.',
    'Prove a refactor: <code>(old EXCEPT new)</code> and <code>(new EXCEPT old)</code> both empty.',
]
FAQ = [
    ('Is a CTE faster than a subquery?', 'Usually neither: Hive inlines a CTE just like a subquery, so the plan is the same. The benefit is readability and testability. A CTE used many times can be materialised (threshold setting), which may help or hurt depending on its cost; check EXPLAIN.'),
    ('Can I use a CTE in another query later?', 'No. A CTE exists only for the statement it belongs to. To reuse logic, create a view (logic only, Module 9) or a table (stored result) with CTAS.'),
    ('Why does NOT IN behave strangely with NULL?', 'x NOT IN (a, b, NULL) means x <> a AND x <> b AND x <> NULL. The last comparison is NULL, so the whole condition is NULL when x is neither a nor b, and WHERE keeps only TRUE. NOT EXISTS asks whether a matching row exists, which NULLs cannot satisfy, so it gives the intuitive answer.'),
    ('UNION or UNION ALL in pipelines?', 'UNION ALL whenever the inputs cannot overlap or duplicates are meaningful (most pipelines, e.g. combining app and partner orders). UNION adds a de-duplication shuffle; use it only when you really need distinct rows, and consider whether a key-based de-duplication (ROW_NUMBER, Lesson 3.6) is more correct.'),
    ('Do INTERSECT and EXCEPT treat NULLs as equal?', 'Set operations compare whole rows and treat NULLs in the same position as matching for the purpose of duplicates and comparison, unlike the = operator. This makes them handy for comparing two result sets that contain NULLs.'),
]

PRACTICE_INTRO = 'Programs on derived tables, IN/EXISTS, the NOT IN trap and set operations, with HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Filter on an aggregate', stmt='From revenue per city, keep cities above Rs 20 lakh (derived table + WHERE).', inp='real revenue for Mumbai, Bengaluru, Pune, Hyderabad',
         code='''rev = {"Mumbai": 2941120, "Bengaluru": 2724070, "Pune": 2344660, "Hyderabad": 1763190}
print({c: r for c, r in rev.items() if r > 2_000_000})
''', explain='Mumbai, Bengaluru, Pune: the same three cities as the real derived-table query.'),
    dict(level='easy', title='UNION vs UNION ALL', stmt='Combine [Thane, Mumbai, Pune] and [Thane, Delhi] with and without duplicates.', inp='two lists',
         code='''a, b = ["Thane", "Mumbai", "Pune"], ["Thane", "Delhi"]
print("UNION ALL:", a + b)
print("UNION    :", sorted(set(a + b)))
''', explain='5 rows vs 4. UNION removes the repeated Thane.'),
    dict(level='easy', title='EXCEPT', stmt='Which cities have targets but no orders?', inp='targets and order cities from the lab',
         code='''targets = {"Bengaluru", "Delhi", "Hyderabad", "Mumbai", "Nashik", "Pune", "Thane"}
orders = {"Bengaluru", "Chennai", "Delhi", "Hyderabad", "Mumbai", "Navi Mumbai", "Pune", "Thane"}
print(targets - orders)
''', explain='{Nashik}: targets EXCEPT orders.'),
    dict(level='medium', title='Correlated count', stmt='For each target city count its orders (a correlated scalar subquery in SELECT).', inp='targets [Delhi, Nashik, Pune] · order cities list',
         code='''order_cities = ["Pune", "Delhi", "Pune", "Mumbai", "Pune"]
for t in ["Delhi", "Nashik", "Pune"]:
    print(t, sum(1 for c in order_cities if c == t))
''', explain='Delhi 1, Nashik 0, Pune 3. Note Nashik gets 0, not NULL: COUNT of no rows is 0.'),
    dict(level='medium', title='NOT IN vs NOT EXISTS', stmt='For x = 5 and lists [1, 2] and [1, 2, None], compute NOT IN (three-valued) and NOT EXISTS.', inp='x = 5',
         code='''def not_in(x, lst):
    if x in [v for v in lst if v is not None]: return False
    return None if None in lst else True
for lst in ([1, 2], [1, 2, None]):
    print(lst, "NOT IN:", not_in(5, lst), "| NOT EXISTS:", not any(v == 5 for v in lst if v is not None))
''', explain='With None in the list NOT IN is unknown (None) while NOT EXISTS stays True.'),
    dict(level='medium', title='Prove two results equal', stmt='Check two query results for equality using set differences both ways.', inp='old and new result rows',
         code='''old = {("Mumbai", 2941120), ("Pune", 2344660)}
new = {("Pune", 2344660), ("Mumbai", 2941120)}
print("equal:", not (old - new) and not (new - old))
''', explain='Both EXCEPT directions empty → identical (as sets). Also compare COUNT(*) to catch duplicate differences.'),
    dict(level='business', title='Coupon list size', stmt='2,000 customers; 1,620 ordered in the last 30 days (illustrative). How many lapsed customers should the NOT EXISTS job return, and what does NOT IN return after one guest order with NULL id appears?', inp='2,000 customers, 1,620 recent',
         code='''total, recent = 2000, 1620
print("NOT EXISTS:", total - recent)
print("NOT IN with a NULL:", 0)
''', explain='380 versus 0: a silent business failure caused by one NULL.'),
    dict(level='business', title='Revenue share above average', stmt='What share of total delivered revenue comes from the three above-average cities (Mumbai 27.13 lakh, Bengaluru 24.99, Pune 21.48; total 135.55 lakh)?', inp='real delivered revenue in lakh',
         code='''top = 27.13 + 24.99 + 21.48
print(f"{top / 135.55:.1%} of delivered revenue from 3 of 8 cities")
''', explain='About 54.3%, from the real delivered revenue. CTEs make such follow-up questions a one-line change to the final SELECT.'),
]

SCN_INTRO = 'Subquery questions test SQL depth. The NOT IN trap and CTE readability come up again and again.'
SCENARIOS = (
    scn('Any company · SQL', 'Fresher', '“Write it with a subquery”',
        'Find cities whose total revenue is above the average city revenue.',
        'can you layer queries correctly?',
        '''<pre>WITH city_rev AS (SELECT city, SUM(amount) AS revenue FROM orders GROUP BY city)
SELECT city, revenue
FROM city_rev
WHERE revenue &gt; (SELECT AVG(revenue) FROM city_rev);</pre>''', 'AVG(amount) of orders instead of the average of city revenues.') +
    scn('Data quality', 'Mid-level', 'A query suddenly returns zero rows',
        'A NOT IN query that worked for months returns nothing after a source system change.',
        'do you know NOT IN with NULLs?',
        '''<ol>
          <li>Check the subquery column for NULLs: a single NULL makes NOT IN unknown for every row.</li>
          <li>Rewrite with NOT EXISTS, or add WHERE col IS NOT NULL inside the subquery.</li>
          <li>Add monitoring for sudden drops to zero.</li>
        </ol>''', '“Hive lost the data”.') +
    scn('Analytics engineering', 'Mid-level', 'Refactoring a legacy query',
        'You must change a 200-line nested query and prove the result did not change.',
        'do you have a safe refactoring method?',
        '''<ul>
          <li>Rewrite as CTEs, one per logical step, and test each step’s row counts.</li>
          <li>Compare old and new with EXCEPT in both directions plus COUNT(*).</li>
          <li>Keep the final query in version control with a short description of each CTE.</li>
        </ul>''', '“it looks the same to me”.') +
    scn('Data engineering', 'Fresher', 'Combining two order sources',
        'App orders and partner orders are in two tables with the same columns. Build one view for reporting.',
        'do you choose UNION ALL vs UNION correctly?',
        '''<ul>
          <li>Use <code>UNION ALL</code> with a source column: <code>SELECT …, 'app' AS source FROM app_orders UNION ALL SELECT …, 'partner' FROM partner_orders</code>.</li>
          <li>UNION would waste a shuffle and could merge genuinely different orders that look identical.</li>
          <li>De-duplicate by business key (order id) if overlaps are possible.</li>
        </ul>''', 'UNION “to be safe”.')
)
