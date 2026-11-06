import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
def err(n):
    return capf(n).split('; Query ID')[0]

# ---------------------------------------------------------------- story
sc = (box(10, 12, 290, 128, 'card') + t(155, 30, 'order_items: 1 row per order', 8.8, bold=True) +
      t(24, 58, '100001', 8.2, 'ink', anchor='start', mono=True) + box(78, 46, 210, 20, 'acc', rx=4) + t(183, 60, '[Chole Bhature, Aloo Paratha, Lassi, …]', 7.2, 'ink', mono=True) +
      t(24, 90, '100002', 8.2, 'ink', anchor='start', mono=True) + box(78, 78, 210, 20, 'acc', rx=4) + t(183, 92, '[Veg Hakka Noodles, Manchurian, …]', 7.2, 'ink', mono=True) +
      t(155, 124, 'How many times was Lassi ordered?', 7.8, 'ink2') +
      arrow(306, 76, 326, 76, 'ink3', 2) +
      box(330, 12, 300, 128, 'green') + t(480, 30, 'LATERAL VIEW explode: 1 row per dish', 8.8, 'green', bold=True) +
      ''.join(t(346, 52 + k * 15, f'{o}  {d}', 7.8, 'ink', anchor='start', mono=True) for k, (o, d) in enumerate([('100001', 'Chole Bhature'), ('100001', 'Aloo Paratha'), ('100001', 'Lassi'), ('100001', 'Rajma Chawal'), ('100002', 'Veg Hakka Noodles'), ('100002', 'Manchurian')])))
scene_svg = scene('On the left, one row per order with an array of dishes. On the right, LATERAL VIEW explode produces one row per dish, keeping the order id next to each dish.', sc,
                  '<tspan font-weight="700" class="s-acc">explode</tspan> turns one array into many rows; <tspan font-weight="700" class="s-acc">LATERAL VIEW</tspan> keeps the other columns.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Which dishes sell the most?”</h2>
  <div class="story">
    <p class="narration">The menu team wants the five most ordered dishes. In <code>order_items</code> each order has <b>one row</b>, and the dishes sit inside an <code>ARRAY&lt;STRING&gt;</code> column. Kabir can read <code>dishes[0]</code>, the first dish, but he cannot GROUP BY something that is hidden inside an array.</p>

{scene_svg}

K> Sir, I need one row per dish, not one per order. I tried <code>SELECT order_id, explode(dishes)</code> and Hive refused.
A> <code>explode</code> is a table-generating function: one row goes in, many come out. On its own it cannot sit next to normal columns. <code>LATERAL VIEW explode(dishes) d AS dish</code> joins each generated row back to its order, so you keep <code>order_id</code>, the city, everything.
R> And maps, like the <code>prefs</code> column?
A> explode works on maps too and gives a key and a value. Today: arrays, maps and structs, explode and posexplode, LATERAL VIEW and its OUTER form, two real errors, and how to build arrays back with <code>collect_list</code>. All outputs are real.
  </div>
</section>
'''

lv = '''
LEVELS> Complex types and explode at three levels
L1> A tiffin box with compartments
      <ul>
        <li>An <b>array</b> is a list in one cell: <code>["Poha","Chai"]</code>. A <b>map</b> is labelled pairs: <code>{"spice":"mild"}</code>. A <b>struct</b> is a small record: <code>{"phone":…, "email":…}</code>.</li>
        <li>You can read one item: <code>dishes[0]</code>, <code>prefs['spice']</code>, <code>contact.phone</code>.</li>
        <li>To count or group the items you must first <b>unpack</b> the list into rows. That is <code>explode</code>.</li>
      </ul>
L2> UDTFs and LATERAL VIEW
      <ul>
        <li><b>UDTF</b> (table-generating function): <code>explode</code> (array → one column; map → key, value), <code>posexplode</code> (adds the position), <code>inline</code> (array of structs → columns), <code>stack</code> (values → rows), <code>json_tuple</code> and <code>parse_url_tuple</code> (Lesson 4.3).</li>
        <li><code>SELECT explode(col)</code> works only if it is the <b>only</b> expression in SELECT.</li>
        <li><code>FROM t LATERAL VIEW explode(t.col) alias AS c</code> joins each generated row with its source row, so other columns stay available for WHERE, GROUP BY and JOIN (through a subquery).</li>
        <li><code>LATERAL VIEW OUTER</code> keeps source rows whose array is empty or NULL, with NULL in the generated column.</li>
      </ul>
L3> What Hive does, and the costs
      <ul>
        <li>The plan uses a <b>Lateral View Forward</b>, a <b>UDTF operator</b> and a <b>Lateral View Join</b> inside the same map task: no shuffle is needed to explode.</li>
        <li>Row counts multiply: 5,000 orders became 12,671 dish rows. Two LATERAL VIEWs in one query multiply again (a cross product per row).</li>
        <li>Rules found in our lab: UDTF next to other columns → Error 10081; JOIN directly after a LATERAL VIEW → Error 10085 (explode in a subquery, then join); <code>stack</code> needs identical types in each column.</li>
        <li><code>collect_list</code> / <code>collect_set</code> reverse explode by aggregating back into arrays; the element order of collect_list is not guaranteed after a shuffle.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>explode and LATERAL VIEW</h2>
''' + def_block(
    'A <b>table-generating function (UDTF)</b> maps one input row to zero or more output rows. <code>explode(array)</code> returns one row per element and <code>explode(map)</code> one row per key–value pair; <code>posexplode</code> adds a 0-based position. A <b>LATERAL VIEW</b> applies a UDTF to each row of a base table and joins the output rows with that input row, forming a virtual table with a table alias and column aliases: <code>FROM base LATERAL VIEW [OUTER] udtf(expr) tableAlias AS colAlias, …</code>. With <code>OUTER</code>, rows for which the UDTF produces no output are kept with NULL values.',
    'explode opens a list stored in one cell and puts each item on its own row. LATERAL VIEW keeps the rest of the original row next to each item, so you can still see which order each dish came from.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('ARRAY&lt;T&gt;', 'An ordered list of values of one type. Index from 0.'),
    ('MAP&lt;K,V&gt;', 'Key–value pairs. Read with <code>m[\'key\']</code>; a missing key gives NULL.'),
    ('STRUCT', 'Named fields in one value. Read with <code>s.field</code>.'),
    ('UDTF', 'Function that returns rows: explode, posexplode, inline, stack, json_tuple.'),
    ('LATERAL VIEW', 'Applies a UDTF to each row and joins the output with that row.'),
    ('OUTER', 'Keeps rows whose array is empty or NULL.'),
    ('collect_list / collect_set', 'Aggregate rows back into an array (set removes duplicates).'),
]) + '''

  <h3>Reading complex values without exploding (real results)</h3>
''' + table(['Expression', 'Real result', 'Note'], [
    ["<code>dishes[0]</code> (order 100001)", 'Chole Bhature', 'First element'],
    ["<code>dishes[9]</code>", 'NULL', 'Index past the end: no error'],
    ["<code>size(dishes)</code>", '4', 'size of an empty array is 0, of NULL is -1'],
    ["<code>prefs['spice']</code>", 'medium', 'Map lookup by key'],
    ["<code>prefs['nuts']</code>", 'NULL', 'Missing key'],
    ["<code>contact.phone</code> (restaurant 1)", '+91-00000-00001', 'Struct field'],
    ["<code>array_contains(dishes, 'Lassi')</code>", 'true', 'Test without exploding'],
], minw=600) + lv + '''
EXAM> “What is LATERAL VIEW and why is it needed?” Answer: a UDTF such as explode cannot be selected together with other columns; LATERAL VIEW applies it to every row and joins the generated rows back to the source row. Mention OUTER for empty arrays and posexplode for positions.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>The table-generating functions</h2>
''' + table(['Function', 'Input → output', 'Typical use'], [
    ['<code>explode(array)</code>', 'one row per element (1 column)', 'Dishes, tags, product ids'],
    ['<code>explode(map)</code>', 'one row per pair (key, value)', 'Preferences, attributes, counters'],
    ['<code>posexplode(array)</code>', 'position (0-based) + element', 'Keep order: first dish, step number'],
    ['<code>inline(array&lt;struct&gt;)</code>', 'one row per struct, one column per field', 'Line items with dish and quantity'],
    ['<code>stack(n, v1, v2, …)</code>', 'n rows from a list of values', 'Unpivot columns into rows'],
    ['<code>json_tuple(json, k1, k2…)</code>', 'one row with several JSON fields', 'Lesson 4.3'],
    ['<code>parse_url_tuple(url, \'HOST\', \'PATH\', …)</code>', 'URL parts as columns', 'Web log analysis'],
], minw=700) + table(['Form', 'Write', 'When'], [
    ['UDTF alone', '<code>SELECT explode(dishes) AS dish FROM order_items</code>', 'Quick look; no other columns allowed'],
    ['LATERAL VIEW', '<code>FROM order_items LATERAL VIEW explode(dishes) d AS dish</code>', 'Normal use: keep other columns'],
    ['LATERAL VIEW OUTER', '<code>… LATERAL VIEW OUTER explode(dishes) d AS dish</code>', 'Keep rows with empty or NULL arrays'],
    ['Several views', '<code>… LATERAL VIEW explode(a) x AS a1 LATERAL VIEW explode(b) y AS b1</code>', 'Careful: rows multiply'],
], minw=700) + '''
WARN> Plain LATERAL VIEW silently drops rows whose array is empty or NULL. In our lab, cart 2 (<code>[]</code>) and cart 3 (NULL) vanished until <code>OUTER</code> was added. If a count of orders falls after exploding, check for this first.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>From one row per order to the menu team’s answer</h2>
  <p>All outputs are real, from the Hive 4.2.1 lab (order_items holds 5,000 orders).</p>
''' + stepper([
    ('Step 1 · Read arrays, maps and structs',
     code('sql', 'Beeline', "SELECT order_id, dishes[0] AS first_dish, dishes[9] AS no_such, size(dishes) AS n,\n  prefs['spice'] AS spice, prefs['nuts'] AS missing_key\nFROM order_items WHERE order_id <= 100002;\n\nSELECT name, contact.phone AS phone, tags[0] AS first_tag, size(tags) AS n_tags\nFROM restaurants WHERE restaurant_id <= 3;", capf('l42_access.txt')),
     'An index past the end and a missing map key both give NULL, not an error. Struct fields use a dot.'),
    ('Step 2 · Build complex values',
     code('sql', 'Beeline', "SELECT array('Poha', 'Chai') AS a, map('spice', 'hot', 'cutlery', 'no') AS m,\n  named_struct('city', 'Pune', 'pin', 411001) AS s;", capf('l42_ctor.txt')),
     '<code>array()</code>, <code>map()</code> and <code>named_struct()</code> create values in a query, for tests and for INSERT … SELECT into complex columns.'),
    ('Step 3 · explode alone, and the first error',
     code('sql', 'Beeline', "SELECT explode(dishes) AS dish FROM order_items WHERE order_id = 100001;\n\nSELECT order_id, explode(dishes) AS dish FROM order_items WHERE order_id = 100001;",
          capf('l42_explode_sel.txt') + '\n' + err('l42_udtf_err.txt')),
     'Alone, explode returns the 4 dishes, but without the order id. Adding a normal column next to it fails with Error 10081.'),
    ('Step 4 · LATERAL VIEW keeps the other columns',
     code('sql', 'Beeline', "SELECT o.order_id, d.dish\nFROM order_items o LATERAL VIEW explode(o.dishes) d AS dish\nWHERE o.order_id <= 100002;", capf('l42_lv.txt')),
     '<code>d</code> is the alias of the virtual table and <code>dish</code> its column. Two orders became 7 rows.'),
    ('Step 5 · posexplode and exploding a map',
     code('sql', 'Beeline', "SELECT order_id, pos, dish\nFROM order_items LATERAL VIEW posexplode(dishes) p AS pos, dish\nWHERE order_id = 100001;\n\nSELECT order_id, k, v\nFROM order_items LATERAL VIEW explode(prefs) m AS k, v\nWHERE order_id <= 100002;",
          capf('l42_pos.txt') + '\n' + capf('l42_map.txt')),
     'posexplode adds the position, starting at 0. A map explodes into two columns, key and value.'),
    ('Step 6 · Answer the question: top dishes and restaurant tags',
     code('sql', 'Beeline', "SELECT dish, COUNT(*) AS times\nFROM order_items LATERAL VIEW explode(dishes) d AS dish\nGROUP BY dish ORDER BY times DESC, dish LIMIT 5;\n\nSELECT tag, COUNT(*) AS restaurants, ROUND(AVG(rating), 2) AS avg_rating\nFROM restaurants LATERAL VIEW explode(tags) t AS tag\nGROUP BY tag ORDER BY restaurants DESC;",
          capf('l42_top.txt') + '\n' + capf('l42_tags.txt')),
     'Once the dishes are rows, normal GROUP BY works. Sambar Rice leads with 502 orders. The same pattern counts restaurants per tag.'),
    ('Step 7 · Trap: empty and NULL arrays disappear (use OUTER)',
     code('sql', 'Beeline', "SELECT cart_id, dishes, size(dishes) AS n FROM cart_demo ORDER BY cart_id;\n\nSELECT c.cart_id, d.dish FROM cart_demo c\n  LATERAL VIEW explode(c.dishes) d AS dish ORDER BY c.cart_id;\n\nSELECT c.cart_id, d.dish FROM cart_demo c\n  LATERAL VIEW OUTER explode(c.dishes) d AS dish ORDER BY c.cart_id;",
          capf('l42_outer_setup.txt') + '\n' + capf('l42_outer.txt')),
     'size returns 0 for an empty array and -1 for NULL. Without OUTER, carts 2 and 3 vanish; with OUTER they stay, with NULL as the dish.'),
    ('Step 8 · Two LATERAL VIEWs multiply rows',
     code('sql', 'Beeline', "SELECT r.name, t.tag, c.word\nFROM restaurants r\nLATERAL VIEW explode(r.tags) t AS tag\nLATERAL VIEW explode(split(r.cuisine, ' ')) c AS word\nWHERE r.restaurant_id = 8;", capf('l42_multi.txt')),
     '2 tags × 2 words = 4 rows for one restaurant. With long arrays this grows fast, so explode only what the question needs.'),
    ('Step 9 · Trap: JOIN after LATERAL VIEW, and collecting back',
     code('sql', 'Beeline', "-- fails:\nSELECT o.city, d.dish FROM order_items i LATERAL VIEW explode(i.dishes) d AS dish\n  JOIN orders o ON o.order_id = i.order_id;\n\n-- works: explode in a subquery, then join\nSELECT o.city, size(collect_list(e.dish)) AS n_rows, size(collect_set(e.dish)) AS n_distinct\nFROM (SELECT i.order_id, d.dish FROM order_items i\n      LATERAL VIEW explode(i.dishes) d AS dish) e\nJOIN orders o ON o.order_id = e.order_id\nGROUP BY o.city ORDER BY n_rows DESC LIMIT 4;",
          err('l42_joinerr.txt') + '\n\n' + capf('l42_collect.txt')),
     'Hive does not allow a JOIN directly after a LATERAL VIEW (Error 10085). Wrap the explode in a subquery. <code>collect_list</code> keeps duplicates, <code>collect_set</code> removes them: Mumbai had 2,508 dish rows but only 32 different dishes.'),
    ('Step 10 · inline and stack',
     code('sql', 'Beeline', "SELECT inline(array(named_struct('dish', 'Poha', 'qty', 2),\n                    named_struct('dish', 'Chai', 'qty', 3)));\n\nSELECT stack(3, 'UPI', 60.5, 'Card', 20.2, 'COD', 8.9) AS (payment, pct);\nSELECT stack(3, 'UPI', 60.5D, 'Card', 20.2D, 'COD', 8.9D) AS (payment, pct);",
          capf('l42_inline.txt') + '\n' + err('l42_stack.txt') + '\n' + capf('l42_stack2.txt')),
     '<code>inline</code> turns structs into columns. <code>stack</code> unpivots values into rows, but each column must have one type: 60.5 is DECIMAL(3,1) and 8.9 is DECIMAL(2,1), so Hive refused. The <code>D</code> suffix makes them all DOUBLE.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
DISH = ['Chole Bhature', 'Aloo Paratha', 'Lassi', 'Rajma Chawal']
see = [
    term([('> SELECT order_id, dishes FROM order_items', W), ('  WHERE order_id = 100001;', W), ('| 100001 | ["Chole Bhature","Aloo Paratha",', G), ('|        |  "Lassi","Rajma Chawal"]        |', G)]),
    term([('> SELECT order_id, explode(dishes) …', W), ('Error 10081: UDTF\'s are not supported', RD), ('  outside the SELECT clause, nor nested', RD), ('  in expressions', RD)]),
    term([('> … LATERAL VIEW explode(o.dishes) d AS dish', W), ('| 100001 | Chole Bhature |', G), ('| 100001 | Aloo Paratha  |', G), ('| 100001 | Lassi         |', G), ('| 100001 | Rajma Chawal  |', G)]),
    term([('> … LATERAL VIEW posexplode(dishes) p AS pos, dish', W), ('| 100001 | 0 | Chole Bhature |', G), ('| 100001 | 1 | Aloo Paratha  |', G), ('| 100001 | 2 | Lassi         |', G), ('| 100001 | 3 | Rajma Chawal  |', G)]),
    term([('> … LATERAL VIEW OUTER explode(c.dishes) …', W), ('| 1 | Poha |', G), ('| 1 | Chai |', G), ('| 2 | NULL |', Y), ('| 3 | NULL |', Y)]),
]
def src_row(hi=False):
    return box(14, 44, 332, 26, 'acc' if hi else 'card') + t(24, 61, '100001', 8, 'ink', anchor='start', mono=True) + t(206, 61, '[Chole Bhature, Aloo Paratha, Lassi, Rajma…]', 7, 'ink', mono=True)
def out_rows(pos=False, n=4):
    return ''.join(box(60, 88 + k * 16, 240, 14, 'green', rx=3) + t(70, 98 + k * 16, ('100001  ' + (str(k) + '  ' if pos else '') + DISH[k]), 7.6, 'ink', anchor='start', mono=True) for k in range(n))
B1 = [
    t(180, 22, 'One row, one array', 9.4, bold=True) + src_row(True) + t(180, 100, 'GROUP BY dish is impossible here', 8.4, 'red') + cap('The dishes are hidden inside one cell.', '', 'blue', y=150, h=34),
    t(180, 22, 'A UDTF returns rows, not a value', 9.4, bold=True) + src_row() + t(100, 100, 'order_id: 1 value', 8.2, 'ink2', mono=True) + t(260, 100, 'explode: 4 rows', 8.2, 'red', mono=True) + t(180, 118, 'cannot sit side by side', 8.4, 'red', bold=True) + cap('Hive cannot mix 1 value with 4 rows.', '', 'amber', y=150, h=34),
    t(180, 22, 'LATERAL VIEW: generate, then join back', 9.4, bold=True) + src_row() + arrow(180, 72, 180, 84, 'ink3', 1.6) + out_rows() + cap('Each dish row carries its order_id.', '', 'green', y=158, h=30),
    t(180, 22, 'posexplode adds the position', 9.4, bold=True) + src_row() + arrow(180, 72, 180, 84, 'ink3', 1.6) + out_rows(True) + cap('Positions start at 0.', '', 'green', y=158, h=30),
    t(180, 22, 'OUTER keeps empty and NULL arrays', 9.4, bold=True) + ''.join(box(20, 44 + k * 26, 140, 22, 'card') + t(90, 59 + k * 26, s, 7.8, 'ink', mono=True) for k, s in enumerate(['1  [Poha, Chai]', '2  []', '3  NULL'])) +
    t(260, 58, 'plain: 2 rows', 8.4, 'red', mono=True) + t(260, 82, 'OUTER: 4 rows', 8.4, 'green', mono=True) + t(260, 106, '(carts 2, 3 → NULL)', 7.8, 'ink2', mono=True) + cap('Without OUTER, carts 2 and 3 vanish.', '', 'amber', y=150, h=34),
]
see_caps = ['One order row holds an array of four dishes.',
            'explode next to another column fails with Error 10081.',
            'LATERAL VIEW explode gives one row per dish with the order id.',
            'posexplode also returns the position of each dish.',
            'LATERAL VIEW OUTER keeps carts with empty or NULL arrays.']
behind_caps = ['GROUP BY cannot see inside the array.',
               'A UDTF produces several rows, which cannot be placed next to a single value.',
               'The generated rows are joined back to the source row.',
               'Each output row gets a 0-based position.',
               'Plain LATERAL VIEW drops rows that generate nothing; OUTER keeps them with NULL.']
two = anim_two('LATERAL VIEW', 'One row in, many rows out', 'Real Beeline output', 'How the source row turns into generated rows', see, B1, see_caps, behind_caps)

# ---- scenario 1: menu analytics
a1 = (t(180, 22, 'Menu team: top 5 dishes', 9.6, bold=True) + t(180, 56, '5,000 orders → explode → 12,671 dish rows', 8.6, 'ink', mono=True) + cap('One order holds 2.5 dishes on average.', '', 'blue', y=150, h=34))
a2 = (t(180, 22, 'Real top 5', 9.6, bold=True) + bars([(d, round(v / 5.02), 'green', str(v)) for d, v in [('Sambar Rice', 502), ('Curd Rice', 494), ('Idli', 484), ('Manchurian', 477), ('Misal Pav', 472)]], x=110, y=40, w=190, h=13, gap=20) + cap('GROUP BY dish after LATERAL VIEW explode.', '', 'green', y=150, h=34))
a3 = (t(180, 22, 'Which orders contain Lassi?', 9.6, bold=True) + t(180, 56, 'explode + WHERE dish = \'Lassi\'  → 438', 8.4, 'ink', mono=True) + t(180, 76, 'array_contains(dishes, \'Lassi\') → 438', 8.4, 'green', mono=True) + cap('No explode needed for a simple “contains”.', '', 'green', y=150, h=34))
a4 = (t(180, 22, 'Dishes per city', 9.6, bold=True) + t(180, 52, 'explode in a subquery, then JOIN orders', 8.4, 'ink2') + t(180, 72, 'Mumbai: 2,508 rows, 32 distinct dishes', 8.4, 'ink', mono=True) + cap('collect_set gives the distinct list.', '', 'blue', y=150, h=34))
a5 = (t(180, 22, 'Result for the business', 9.6, 'acc', bold=True) + t(180, 56, 'South Indian rice dishes lead; plan stock and combos', 8.2, 'ink2') + cap('Arrays become insight after one explode.', '', 'green', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Top dishes for the menu team',
              'Answering a product question from an array column. Counts are real.',
              'Menu analytics', 'Dishes stored as arrays are exploded into rows and grouped to find the most ordered dishes', [a1, a2, a3, a4, a5],
              ['Exploding 5,000 orders produced 12,671 dish rows.',
               'GROUP BY dish gives the real top five.',
               'array_contains answers “contains Lassi” without exploding: 438 orders either way.',
               'Join to orders through a subquery to split by city.',
               'The result guides stock and combo planning.'],
              hid='scenario-menu')

# ---- scenario 2: OUTER and lost rows
o1 = (t(180, 22, 'Funnel: carts → checkout', 9.6, bold=True) + t(180, 56, 'carts table with dishes ARRAY (some carts empty)', 8.4, 'ink2') + cap('Analyst explodes dishes, then counts carts.', '', 'blue', y=150, h=34))
o2 = term([('> … LATERAL VIEW explode(c.dishes) …', W), ('| 1 | Poha |', G), ('| 1 | Chai |', G), ('  carts 2 and 3 missing', RD)], label='real output · Hive 4.2.1')
o3 = term([('> … LATERAL VIEW OUTER explode(c.dishes) …', W), ('| 1 | Poha |', G), ('| 1 | Chai |', G), ('| 2 | NULL |', Y), ('| 3 | NULL |', Y)], label='real output · Hive 4.2.1')
o4 = (t(180, 22, 'Count the right thing', 9.6, bold=True) + t(180, 56, 'COUNT(DISTINCT cart_id) after OUTER = 3', 8.6, 'green', mono=True) + t(180, 76, 'COUNT(*) after OUTER = 4 rows', 8.6, 'ink2', mono=True) + cap('Rows after explode are dish rows, not carts.', '', 'amber', y=150, h=34))
o5 = (t(180, 22, 'Checklist', 9.6, 'acc', bold=True) + ''.join(t(26, 52 + k * 19, s, 8.4, anchor='start') for k, s in enumerate(['• compare source row count before and after', '• use OUTER when every source row matters', '• count DISTINCT keys, not exploded rows'])) + cap('Explode changes the grain of the data.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Empty carts that vanished from a funnel',
              'A funnel undercounted carts because empty arrays produce no rows. Outputs are real.',
              'LATERAL VIEW OUTER', 'Plain LATERAL VIEW drops empty and NULL arrays; OUTER keeps them, and counting distinct keys gives the right number', [o1, o2, o3, o4, o5],
              ['Some carts have no dishes yet.',
               'Plain LATERAL VIEW returns rows only for cart 1.',
               'OUTER keeps carts 2 and 3 with NULL dishes.',
               'Count distinct cart ids, not exploded rows.',
               'Check row counts whenever the grain changes.'],
              hid='scenario-outer')

# ---- scenario 3: row explosion
e1 = (t(180, 22, 'Two arrays, one query', 9.6, bold=True) + t(180, 56, 'LATERAL VIEW explode(tags) … explode(words) …', 8.4, 'ink', mono=True) + cap('Every tag is paired with every word.', '', 'blue', y=150, h=34))
e2 = term([('> … restaurant_id = 8', W), ('| Singh Bhojanalay | jain   | North  |', G), ('| Singh Bhojanalay | jain   | Indian |', G), ('| Singh Bhojanalay | budget | North  |', G), ('| Singh Bhojanalay | budget | Indian |', G)], label='real output · Hive 4.2.1')
e3 = (t(180, 22, 'Grows as a product', 9.6, 'red', bold=True) + t(180, 56, '2 × 2 = 4 rows here', 8.6, 'ink', mono=True) + t(180, 76, '50 items × 40 events = 2,000 rows per source row', 8.2, 'red', mono=True) + cap('Big arrays can explode a job’s size.', '', 'amber', y=150, h=34))
e4 = (t(180, 22, 'Fixes', 9.6, 'green', bold=True) + ''.join(t(26, 52 + k * 19, s, 8.4, anchor='start') for k, s in enumerate(['• explode one array per query step', '• aggregate before joining another exploded set', '• use posexplode + matching pos for parallel arrays'])) + cap('Explode only what the question needs.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Parallel arrays', 9.6, 'acc', bold=True) + t(180, 56, 'dishes[i] belongs with qty[i]?', 8.4, 'ink2') + t(180, 76, 'posexplode both, keep rows where pos1 = pos2', 8.4, 'ink', mono=True) + cap('Better: store an array of structs and use inline.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'When two LATERAL VIEWs multiply rows',
              'Exploding two arrays in one query pairs every element with every other. The small example is real; the large numbers are illustrative.',
              'Row explosion', 'Two LATERAL VIEWs produce a cross product of the two arrays for each source row', [e1, e2, e3, e4, e5],
              ['Two exploded arrays in one query.',
               'One restaurant with 2 tags and 2 words gives 4 rows.',
               'The row count is the product of the array sizes.',
               'Explode one array at a time, or aggregate first.',
               'For arrays that belong together, match positions or use structs.'],
              hid='scenario-explosion')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>One row in, many rows out</h2>
  <p>Left: real Beeline output. Right: how the source row is turned into generated rows.</p>
''' + two + '''
  <p>Three live scenarios follow: menu analytics, lost empty carts and row explosion.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>explode and LATERAL VIEW at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'basket', 10, 'green', bold=True) + t(60, 58, 'items per order', 7.4, 'ink2'),
    '1. Basket analysis',
    'E-commerce and food apps store cart items as arrays; exploding them gives best sellers, items bought together and average basket size.',
    ['Orders', '*explode items', 'Top items']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'tags', 10, 'blue', bold=True) + t(60, 58, 'labels', 7.4, 'ink2'),
    '2. Tags and categories',
    'Products, articles and restaurants carry several tags; explode turns them into rows for counts and filters per tag.',
    ['Tag arrays', '*explode', 'Counts per tag']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'map', 10, 'violet', bold=True, mono=True) + t(60, 58, 'attributes', 7.4, 'ink2'),
    '3. Flexible attributes',
    'Device or app event properties are kept in MAP columns; explode(map) turns them into key–value rows for analysis without changing the schema.',
    ['Event props map', '*explode(map)', 'Key-value rows']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'stack', 10, 'acc', bold=True, mono=True) + t(60, 58, 'unpivot', 7.4, 'ink2'),
    '4. Unpivoting wide tables',
    'Monthly columns (jan, feb, mar…) from spreadsheets are turned into month–value rows with stack for loading into fact tables.',
    ['Wide table', '*stack', 'Long table']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'collect', 9, 'acc', bold=True, mono=True) + t(60, 58, 'rows → array', 7.4, 'ink2'),
    '5. Building features',
    'For recommendations, a customer’s ordered dishes are collected into an array with collect_set, the reverse of explode.',
    ['Order rows', '*collect_set', 'Dish list per customer']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> you need complex data types (<a href="../../02-hiveql/03-data-types/">2.3</a>) and GROUP BY (<a href="../../03-querying/02-group-by-and-grouping-sets/">3.2</a>).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
