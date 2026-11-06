import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
BODY = body(HERE)
def capf(n):
    return open(CAP + n).read().rstrip()

META = dict(
    module='04-complex-data', lesson='02-explode-and-lateral-view', n='4.2',
    module_label='Module 4 · Functions and complex data',
    title='Arrays and maps: explode and LATERAL VIEW',
    desc='Working with ARRAY, MAP and STRUCT columns in Hive with real Hive 4.2.1 results: indexing, size, array_contains, constructors, explode, posexplode, exploding maps, LATERAL VIEW and LATERAL VIEW OUTER, multiple lateral views, inline and stack, collect_list and collect_set, and the errors 10081 and 10085.',
    og_desc='One row per order, many dishes inside. explode, posexplode and LATERAL VIEW in Hive with real outputs, the OUTER trap and two real errors.',
    minutes=35, level='Beginner → Advanced',
    lead='Hive tables often store lists and key–value pairs inside one cell: the dishes of an order, the tags of a restaurant, the preferences of a customer. To count or group them you must turn the list into rows. This lesson finds TiffinGo’s top dishes with <code>LATERAL VIEW explode</code>, shows why empty carts disappear without <code>OUTER</code>, and works around two real errors. <b>All outputs are real</b>, from Hive 4.2.1.',
    chips=['Real Hive 4.2.1 outputs', 'explode, posexplode, inline, stack', 'The OUTER trap', 'Runs in your browser (Python)'],
)

MAIN = '''# LATERAL VIEW explode in Python: one output row per array element, keeping the order id
orders = [(100001, ["Chole Bhature", "Aloo Paratha", "Lassi", "Rajma Chawal"]),
          (100002, ["Veg Hakka Noodles", "Manchurian", "Fried Rice"])]

rows = []
for order_id, dishes in orders:          # FROM order_items o
    for dish in dishes:                  # LATERAL VIEW explode(o.dishes) d AS dish
        rows.append((order_id, dish))

for r in rows:
    print(r)
print(len(orders), "orders ->", len(rows), "rows")
'''
RUN = dict(
    heading='Run the code: explode, OUTER and collect',
    intro='<p>These programs do in Python what Hive’s table-generating functions do, on the real lab values. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    for dish in dishes:                  # LATERAL VIEW explode(o.dishes) d AS dish', 'The inner loop is the UDTF: one input row produces several output rows.'),
        ('        rows.append((order_id, dish))', 'The order id is copied next to every dish: that is the “join back” LATERAL VIEW does.'),
    ],
    tasks=[
        dict(label='1 · LATERAL VIEW explode', hint='Press <b>Run</b>: 2 orders become 7 rows, as in the real Step 4.', code=None),
        dict(label='2 · posexplode and maps', hint='<b>Predict first:</b> what position does Lassi get?',
             code='''dishes = ["Chole Bhature", "Aloo Paratha", "Lassi", "Rajma Chawal"]
for pos, dish in enumerate(dishes):          # posexplode: positions start at 0
    print(pos, dish)
prefs = {"spice": "medium", "cutlery": "yes"}
for k, v in prefs.items():                    # explode(map) -> key, value
    print(k, v)
'''),
        dict(label='3 · Plain vs OUTER', hint='Carts 2 and 3 have an empty and a missing list. Compare the two outputs.',
             code='''carts = [(1, ["Poha", "Chai"]), (2, []), (3, None)]
plain = [(c, d) for c, ds in carts for d in (ds or [])]
outer = [(c, d) for c, ds in carts for d in (ds if ds else [None])]
print("plain:", plain)
print("outer:", outer)
'''),
        dict(label='4 · Count dishes, then collect back', hint='GROUP BY after exploding, and collect_set to rebuild a distinct list.',
             code='''orders = [["Idli", "Chai"], ["Idli", "Poha"], ["Sambar Rice", "Idli"]]
counts = {}
for dishes in orders:
    for d in dishes:
        counts[d] = counts.get(d, 0) + 1
print(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))
all_rows = [d for ds in orders for d in ds]
print("collect_list size:", len(all_rows), "| collect_set:", sorted(set(all_rows)))
'''),
        dict(label='5 · Spot the error', hint='The funnel must count 3 carts, but exploding dropped the empty ones. Fix it the OUTER way, and count distinct cart ids.', expect='error',
             code='''carts = [(1, ["Poha", "Chai"]), (2, []), (3, None)]
rows = [(c, d) for c, ds in carts for d in (ds or [])]      # plain LATERAL VIEW
n_carts = len({c for c, _ in rows})
assert n_carts == 3, f"only {n_carts} cart(s): empty and NULL arrays produced no rows"
print(n_carts)
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: plan, a filter and rebuilding arrays',
    intro='<p>Three more queries for Beeline on the TiffinGo data. <b>Outputs are real</b>, from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · The plan of a LATERAL VIEW', cmd='EXPLAIN SELECT o.order_id, d.dish\nFROM order_items o LATERAL VIEW explode(o.dishes) d AS dish;', file='Beeline',
             output='|           Lateral View Forward [LVF_1]             |\n|         UDTF Operator [UDTF_4]                     |\n|       Lateral View Join Operator [LVJ_5]           |\n(lines picked from the real plan)',
             note='The forward operator sends each row two ways: to the UDTF that generates dish rows, and straight to the join that glues the order columns back on. All of it runs in the map phase: exploding needs no shuffle.'),
        dict(title='2 · Filter on the exploded column, or not explode at all', cmd="SELECT COUNT(DISTINCT order_id) AS orders_with_lassi\nFROM order_items LATERAL VIEW explode(dishes) d AS dish WHERE dish = 'Lassi';\n\nSELECT COUNT(*) AS via_array_contains FROM order_items\nWHERE array_contains(dishes, 'Lassi');", file='Beeline',
             output=capf('l42_where.txt'),
             note='Both give 438. For a simple “contains” test, <code>array_contains</code> is cheaper because no extra rows are created.'),
        dict(title='3 · Collect rows back into an array', cmd="SELECT order_id, collect_list(dish) AS dishes_again\nFROM (SELECT order_id, dish FROM order_items\n      LATERAL VIEW explode(dishes) d AS dish WHERE order_id = 100001) x\nGROUP BY order_id;", file='Beeline',
             output=capf('l42_rebuild.txt'),
             note='collect_list reverses explode. Here the order happened to be kept, but after a shuffle the element order is not guaranteed; use posexplode and sort_array or an ordered struct if order matters.'),
    ],
)

TRACE = dict(
    heading='Exploding with and without OUTER, one cart at a time',
    intro='<p>Watch which carts produce rows. Cart 2 is empty and cart 3 is missing (None plays NULL).</p>',
    code='''carts = [(1, ["Poha", "Chai"]), (2, []), (3, None)]
out = []
for cart_id, dishes in carts:
    items = dishes if dishes else [None]
    for d in items:
        out.append((cart_id, d))
print(out)
''',
    notes={4: 'OUTER :: An empty or NULL array becomes one NULL row instead of none.', 6: 'Join back :: The cart id is attached to every generated row.'},
)

WORKED_INTRO = 'Three jobs with arrays and maps: the average basket, unpivoting a wide table, and pairing two parallel arrays.'
EXAMPLES = [
    dict(level='b', tag='Analytics · size()', title='Average dishes per order',
         problem='<p>Find the average basket size with <code>AVG(size(dishes))</code>, without exploding.</p>',
         inp='real total: 12,671 dishes in 5,000 orders; sample orders of 4, 3 and 3 dishes',
         approach=['size() counts elements per row.', 'AVG over orders gives the basket size.', 'No explode needed when you only need counts.'],
         code='''sizes = [4, 3, 3]
print("sample average:", round(sum(sizes) / len(sizes), 2))
print("real average:", round(12671 / 5000, 2))
''', notes={2: 'AVG(size(dishes)) :: One number per order, then the average.'},
         tryit='If some arrays were NULL, size returns -1 and would pull the average down. Use <code>AVG(IF(dishes IS NULL, NULL, size(dishes)))</code>.'),
    dict(level='i', tag='Reshaping · stack', title='Unpivot monthly columns into rows',
         problem='<p>A sheet has columns jul, aug, sep for each city. Turn them into (city, month, orders) rows with <code>LATERAL VIEW stack(3, \'jul\', jul, \'aug\', aug, \'sep\', sep) s AS month, orders</code>.</p>',
         inp='Pune: jul 7,100 · aug 7,350 · sep 7,020 (illustrative)',
         approach=['stack(n, …) makes n rows from the listed pairs.', 'Each pair is (label, value).', 'Values in one output column must share a type.'],
         code='''wide = {"city": "Pune", "jul": 7100, "aug": 7350, "sep": 7020}
for month in ["jul", "aug", "sep"]:
    print(wide["city"], month, wide[month])
''', notes={2: 'stack :: One output row per (label, value) pair.'},
         tryit='Mixing 60.5 and 8.9 in stack failed in our lab (DECIMAL(3,1) vs DECIMAL(2,1)). Cast all values to one type.'),
    dict(level='a', tag='Modelling · posexplode', title='Pair dishes with their quantities',
         problem='<p>An old table stores <code>dishes ARRAY</code> and <code>qty ARRAY</code> separately. Pair them with two posexplodes and <code>WHERE p1 = p2</code>, instead of a cross product.</p>',
         inp='dishes [Idli, Chai, Poha] · qty [2, 3, 1]',
         approach=['posexplode both arrays.', 'Keep rows where the positions match.', 'Compare with the 9-row cross product.'],
         code='''dishes, qty = ["Idli", "Chai", "Poha"], [2, 3, 1]
cross = [(p1, d, p2, q) for p1, d in enumerate(dishes) for p2, q in enumerate(qty)]
paired = [(d, q) for p1, d, p2, q in cross if p1 == p2]
print(len(cross), "cross rows ->", paired)
''', notes={3: 'p1 = p2 :: Keep only matching positions.'},
         tryit='The cleaner design is one <code>ARRAY&lt;STRUCT&lt;dish:STRING, qty:INT&gt;&gt;</code> column and <code>inline</code>, which returns dish and qty directly.'),
]

QUIZ = mix([
    dict(q='Beginner: What does dishes[0] return?', options=['The last dish', 'The first dish', 'The array size', 'An error'], answer=1,
         why='Array indexes start at 0. An index past the end gives NULL.'),
    dict(q='Beginner: What does explode do to an array of 4 dishes?', options=['Joins them into a string', 'Returns 4 rows, one per dish', 'Returns the first dish', 'Sorts them'], answer=1,
         why='explode is a table-generating function: one row in, many out.'),
    dict(q='Beginner: How do you read the phone field of a STRUCT column contact?', options=["contact['phone']", 'contact.phone', 'contact[0]', 'phone(contact)'], answer=1,
         why="Structs use a dot; maps use ['key']."),
    dict(q='Intermediate: SELECT order_id, explode(dishes) FROM order_items fails. What fixes it?', options=['GROUP BY order_id', 'FROM order_items LATERAL VIEW explode(dishes) d AS dish', 'Use posexplode', 'Add LIMIT'], answer=1,
         why='Error 10081: a UDTF cannot sit next to other columns. LATERAL VIEW joins the generated rows back.'),
    dict(q='Intermediate: A cart with an empty array, using plain LATERAL VIEW explode, produces…', options=['One NULL row', 'No rows', 'An error', 'One empty-string row'], answer=1,
         why='Use LATERAL VIEW OUTER to keep it with NULL.'),
    dict(q='Intermediate: size() of a NULL array in Hive returned…', options=['0', 'NULL', '-1', 'An error'], answer=2,
         why='Empty array → 0, NULL → -1 in our lab.'),
    dict(q='Advanced: Two LATERAL VIEWs over arrays of 2 and 2 elements give how many rows per source row?', options=['2', '4', '1', '0'], answer=1,
         why='A cross product: 2 × 2.'),
    dict(q='Advanced: Which pattern avoids Error 10085 (JOIN with a LATERAL VIEW)?', options=['Put the JOIN before FROM', 'Explode in a subquery, then join the subquery', 'Use OUTER', 'It cannot be done'], answer=1,
         why='FROM (SELECT … LATERAL VIEW explode …) e JOIN orders o ON …'),
])

REVISION = [
    '<b>Read</b> without exploding: <code>arr[i]</code> (0-based, NULL past end), <code>map[\'k\']</code> (NULL if missing), <code>struct.field</code>, <code>size</code> (empty 0, NULL -1), <code>array_contains</code>, <code>sort_array</code>, <code>map_keys</code>, <code>map_values</code>.',
    '<b>Build:</b> <code>array()</code>, <code>map()</code>, <code>named_struct()</code>, <code>struct()</code>.',
    '<b>UDTFs:</b> explode (array → value; map → key, value), posexplode (+ position from 0), inline (array of structs), stack (unpivot), json_tuple, parse_url_tuple.',
    'A UDTF alone in SELECT is fine; next to other columns → <b>Error 10081</b>. Use <code>FROM t LATERAL VIEW udtf(col) alias AS c</code>.',
    '<b>OUTER</b> keeps empty and NULL arrays (NULL in the new column).',
    'Several LATERAL VIEWs → <b>cross product</b> per row.',
    'JOIN right after a LATERAL VIEW → <b>Error 10085</b>: explode in a subquery first.',
    '<b>collect_list</b> (keeps duplicates) and <b>collect_set</b> (distinct) reverse explode; element order is not guaranteed.',
]
FAQ = [
    ('Is exploding expensive?', 'Exploding itself runs in the map phase without a shuffle, but it multiplies rows: everything after it (joins, GROUP BY, writes) handles more data. Filter source rows first, explode only the arrays you need, and use array_contains or size when you only need a yes/no or a count.'),
    ('Can I use explode in a WHERE clause?', 'No. UDTFs are allowed only in SELECT (alone) or in LATERAL VIEW. Filter on the generated column after the LATERAL VIEW, as in WHERE dish = \'Lassi\'.'),
    ('Why store arrays at all, instead of a separate table?', 'Arrays keep related values with their parent row, avoid a join for common reads and match JSON sources. A separate table (order_id, dish) is better when items are queried on their own all the time. Many teams keep both: raw arrays plus an exploded table built by the pipeline.'),
    ('Does Spark use the same syntax?', 'Spark SQL supports LATERAL VIEW explode and also allows explode directly in SELECT next to other columns. Queries written with LATERAL VIEW work in both engines.'),
    ('What is the difference between inline and explode?', 'explode on an array of structs gives one column holding each struct; inline spreads the struct fields into separate columns. For line items with several fields, inline is simpler.'),
]

PRACTICE_INTRO = 'Programs that reproduce explode and collect results on real lab values, with the HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='First and missing element', stmt='Return the first dish and the 10th dish of order 100001.', inp='[Chole Bhature, Aloo Paratha, Lassi, Rajma Chawal]',
         code='''dishes = ["Chole Bhature", "Aloo Paratha", "Lassi", "Rajma Chawal"]
print(dishes[0], dishes[9] if len(dishes) > 9 else None)
''', explain='dishes[0] = Chole Bhature, dishes[9] = NULL in Hive (no error), as in Step 1.'),
    dict(level='easy', title='Explode a map', stmt='Turn the preferences map into (key, value) rows.', inp="{'spice': 'mild', 'cutlery': 'yes'}",
         code='''prefs = {"spice": "mild", "cutlery": "yes"}
for k, v in prefs.items():
    print(k, v)
''', explain='LATERAL VIEW explode(prefs) m AS k, v gives two rows per order.'),
    dict(level='easy', title='Size of empty and NULL', stmt='Mimic Hive size() for [Poha, Chai], [] and NULL.', inp='three carts',
         code='''def size(a):
    return -1 if a is None else len(a)
print([size(a) for a in (["Poha", "Chai"], [], None)])
''', explain='[2, 0, -1], matching the real cart_demo output.'),
    dict(level='medium', title='Top tags', stmt='Count restaurants per tag from tag lists.', inp='three real restaurants',
         code='''tags = [["late-night"], ["late-night", "office-lunch", "jain"], ["jain", "veg", "budget"]]
c = {}
for ts in tags:
    for tg in ts:
        c[tg] = c.get(tg, 0) + 1
print(sorted(c.items(), key=lambda kv: (-kv[1], kv[0])))
''', explain='late-night 2 and jain 2. On all 120 restaurants the real leader was jain with 45.'),
    dict(level='medium', title='Cross product of two views', stmt='Pair 2 tags with the 2 words of “North Indian”.', inp='tags [jain, budget]',
         code='''for tag in ["jain", "budget"]:
    for word in "North Indian".split(" "):
        print(tag, word)
''', explain='4 rows, exactly the real output for restaurant 8.'),
    dict(level='medium', title='collect_list vs collect_set', stmt='For dish rows [Idli, Chai, Idli, Poha] give the list size and the distinct set.', inp='four rows',
         code='''rows = ["Idli", "Chai", "Idli", "Poha"]
print(len(rows), sorted(set(rows)))
''', explain='collect_list size 4; collect_set {Chai, Idli, Poha}. Mumbai had 2,508 rows and 32 distinct dishes.'),
    dict(level='business', title='Share of top dish', stmt='Sambar Rice appeared 502 times among 12,671 dish rows. What share is that, and how many orders on average contain about one Sambar Rice?', inp='real counts',
         code='''print(f"share {502 / 12671:.1%}")
print(f"about 1 in {5000 / 502:.0f} orders")
''', explain='About 4.0% of dish rows, roughly 1 order in 10. Useful for stock planning.'),
    dict(level='business', title='Funnel undercount', stmt='1,000 carts, 180 empty and 20 NULL. How many carts does a plain LATERAL VIEW count, and how many with OUTER?', inp='illustrative cart counts',
         code='''total, empty, null = 1000, 180, 20
print("plain:", total - empty - null, "| OUTER:", total)
''', explain='800 vs 1,000: a 20% undercount of carts that would make conversion look better than it is.'),
]

SCN_INTRO = 'Array questions appear in most Hive interviews: explode, LATERAL VIEW, OUTER and collect_set.'
SCENARIOS = (
    scn('Any company · HiveQL', 'Fresher', '“Count orders per dish”',
        'order_items(order_id INT, dishes ARRAY&lt;STRING&gt;). Return each dish and how many orders contain it.',
        'can you use LATERAL VIEW?',
        '''<pre>SELECT dish, COUNT(DISTINCT order_id) AS orders
FROM order_items LATERAL VIEW explode(dishes) d AS dish
GROUP BY dish
ORDER BY orders DESC;</pre>
        <p>COUNT(DISTINCT order_id) handles an order that lists the same dish twice.</p>''', 'SELECT order_id, explode(dishes), which fails with Error 10081.') +
    scn('Data engineering', 'Mid-level', 'Row counts dropped after a new pipeline step',
        'After adding an explode step, the number of customers in a report fell by 12%.',
        'do you know LATERAL VIEW drops empty arrays?',
        '''<ol>
          <li>Count source rows with <code>size(arr) &lt;= 0</code> (empty is 0, NULL is -1).</li>
          <li>Use <code>LATERAL VIEW OUTER</code> if every source row must stay.</li>
          <li>Count distinct keys, not exploded rows, in reports.</li>
        </ol>''', '“Some data was lost in HDFS.”') +
    scn('Analytics', 'Mid-level', 'Unpivot a wide spreadsheet',
        'Finance uploads a table with one column per month. Analysts need month as a row.',
        'do you know stack (or UNION ALL)?',
        '''<ul>
          <li><code>SELECT city, m.month, m.orders FROM wide LATERAL VIEW stack(3, 'jul', jul, 'aug', aug, 'sep', sep) m AS month, orders</code>.</li>
          <li>Make all values one type (CAST), or Hive rejects the call.</li>
          <li>One scan of the table, instead of three with UNION ALL.</li>
        </ul>''', 'Three separate queries glued together by hand.') +
    scn('Data modelling', 'Senior', 'Design line items for analytics',
        'Orders arrive as JSON with a list of items, each with dish, qty and price. How should the Hive tables look?',
        'can you balance nested and flat models?',
        '''<ul>
          <li>Raw table: <code>items ARRAY&lt;STRUCT&lt;dish:STRING, qty:INT, price:DECIMAL(8,2)&gt;&gt;</code> (one row per order).</li>
          <li>Curated table: <code>LATERAL VIEW inline(items)</code> into (order_id, dish, qty, price), partitioned by date.</li>
          <li>Avoid parallel arrays (dishes, qty) that must be matched by position.</li>
        </ul>''', 'Only a comma-separated string of dishes.')
)
