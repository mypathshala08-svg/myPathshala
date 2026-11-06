import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()

# ---------------------------------------------------------------- story
def venn(x, y, l, r, mode):
    o = f'<circle cx="{x}" cy="{y}" r="30" class="s-soft-acc" style="stroke:var(--track)"/><circle cx="{x+36}" cy="{y}" r="30" class="s-soft-blue" style="stroke:var(--blue)"/>'
    return o + t(x - 12, y + 3, l, 7.4, bold=True) + t(x + 48, y + 3, r, 7.4, bold=True)
sc = (box(10, 12, 300, 128, 'card') + t(160, 30, 'Revenue (orders): 8 cities', 8.8, bold=True) +
      ''.join(t(24 + (k % 2) * 140, 50 + (k // 2) * 15, c, 7.8, 'ink' if c not in ('Chennai', 'Navi Mumbai') else 'acc', anchor='start', mono=True, bold=c in ('Chennai', 'Navi Mumbai')) for k, c in enumerate(['Bengaluru', 'Chennai', 'Delhi', 'Hyderabad', 'Mumbai', 'Navi Mumbai', 'Pune', 'Thane'])) +
      box(330, 12, 300, 128, 'card') + t(480, 30, 'Targets (city_targets): 7 cities', 8.8, bold=True) +
      ''.join(t(344 + (k % 2) * 140, 50 + (k // 2) * 15, c, 7.8, 'ink' if c != 'Nashik' else 'blue', anchor='start', mono=True, bold=c == 'Nashik') for k, c in enumerate(['Bengaluru', 'Delhi', 'Hyderabad', 'Mumbai', 'Nashik', 'Pune', 'Thane'])) +
      t(160, 128, 'no target set: Chennai, Navi Mumbai', 7.8, 'acc') + t(480, 128, 'no orders yet: Nashik', 7.8, 'blue'))
scene_svg = scene('Eight cities with revenue and seven cities with targets overlap in six; Chennai and Navi Mumbai have no target and Nashik has no orders.', sc,
                  'Six cities match. What happens to the other <tspan font-weight="700" class="s-acc">three</tspan> depends on the join type.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Why are Chennai and Navi Mumbai missing from the target report?”</h2>
  <div class="story">
    <p class="narration">Kabir joins TiffinGo’s revenue per city with the targets table to show achievement. The report has six cities. The CEO asks where Chennai and Navi Mumbai went, and why Nashik, the newest city with a target but no orders yet, is not there either.</p>

{scene_svg}

K> Sir, the join worked. It just… lost three cities.
A> An <b>inner join</b> keeps only rows that match on both sides. Chennai has revenue but no target row; Nashik has a target but no orders. Both are dropped. The question decides the join: “all cities with revenue” is a <b>left join</b>, “every city on either list” is a <b>full outer join</b>, “targets with no orders” is an <b>anti join</b>.
R> And for big tables? Joining 50,000 orders with seven targets?
A> Hive sees that the targets table is tiny and <b>broadcasts</b> it to every map task: a map join, no shuffle at all. We will read that in EXPLAIN, and meet the classic traps: a WHERE filter that silently turns a left join into an inner join, and NULL keys that never match.
  </div>
</section>
'''

lv = '''
LEVELS> Joins at three levels
L1> Matching two class registers
      <ul>
        <li>You have a list of students who paid fees and a list of students who sat the exam. A <b>join</b> lines up rows that share a key (the roll number).</li>
        <li><b>Inner</b>: only students on both lists. <b>Left</b>: everyone who paid, with exam details where they exist. <b>Full</b>: everyone on either list.</li>
        <li><b>Semi</b>: “who paid and also sat the exam?” (only the first list’s columns). <b>Anti</b>: “who paid but did not sit?”.</li>
        <li>Missing details on an outer side are shown as <b>NULL</b>.</li>
      </ul>
L2> Syntax and rules in Hive
      <ul>
        <li><code>[INNER] JOIN</code>, <code>LEFT|RIGHT|FULL [OUTER] JOIN</code>, <code>LEFT SEMI JOIN</code>, <code>CROSS JOIN</code>, all with <code>ON</code>.</li>
        <li><b>Anti join</b>: Hive 4.2.1 rejected <code>LEFT ANTI JOIN</code> syntax in our lab; write <code>NOT EXISTS (…)</code> or <code>LEFT JOIN … WHERE right.key IS NULL</code>.</li>
        <li><b>LEFT SEMI JOIN</b>: the right table may appear only in ON; returns each left row at most once.</li>
        <li>Joins are evaluated <b>before WHERE</b>. A WHERE condition on the right table of a LEFT JOIN removes the NULL rows and behaves like an inner join; put such conditions in <code>ON</code>.</li>
        <li><b>NULL keys never match</b> with <code>=</code>; use <code>&lt;=&gt;</code> if NULL should match NULL.</li>
        <li>Non-equality conditions (e.g. <code>BETWEEN</code> bands) are allowed in ON since Hive 2.2.</li>
      </ul>
L3> How Hive executes a join
      <ul>
        <li><b>Shuffle (common) join</b>: both tables are repartitioned by the join key and matched in reducers (<code>Merge Join Operator</code>, two <code>SIMPLE_EDGE</code>s).</li>
        <li><b>Map (broadcast) join</b>: the small table is loaded into memory in every map task; the big one is streamed with no shuffle (<code>Map Join Operator</code>, <code>BROADCAST_EDGE</code>). Chosen automatically by <code>hive.auto.convert.join</code> using size estimates (threshold <code>hive.auto.convert.join.noconditionaltask.size</code>).</li>
        <li>Several joins on the <b>same key</b> can run in one stage; different keys need separate shuffles.</li>
        <li>In a shuffle join, the table streamed through the reducer is the last one (or the one named with the <code>STREAMTABLE</code> hint); others are buffered.</li>
        <li>Bucket map joins and sort-merge-bucket joins need bucketed tables (Module 8).</li>
        <li><b>Joins are not commutative</b> for outer joins and are evaluated left to right.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Joins in HiveQL</h2>
''' + def_block(
    'A <b>join</b> combines rows of two or more tables according to a join condition in the <code>ON</code> clause. An <b>inner join</b> returns pairs of rows that satisfy the condition; a <b>left/right/full outer join</b> additionally returns unmatched rows of the left/right/both tables with NULLs for the other side; a <b>left semi join</b> returns each left row that has at least one match, without right-side columns; a <b>cross join</b> returns every combination. Hive executes joins as <b>shuffle joins</b> (both inputs partitioned by key and merged in reducers) or <b>map joins</b> (small tables broadcast to map tasks), chosen by the optimiser.',
    'A join puts rows from two tables side by side when their keys match. The join type decides what happens to rows without a partner: dropped (inner), kept with NULLs (outer), or used only as a yes/no test (semi, anti). Hive either shuffles both tables by key or copies a small table to every task.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Join key', 'The column(s) compared in ON, e.g. <code>city</code> or <code>customer_id</code>.'),
    ('Outer side', 'The table whose unmatched rows are kept (left in a LEFT JOIN).'),
    ('Semi join', 'Keep left rows that have a match; return only left columns, no duplicates from the right.'),
    ('Anti join', 'Keep left rows that have no match. Written with NOT EXISTS in Hive.'),
    ('Cartesian product', 'Every row paired with every row: CROSS JOIN. 7 × 4 = 28 in our test.'),
    ('Map join', 'Small table broadcast to all map tasks; no shuffle of the big table.'),
    ('Shuffle join', 'Both tables repartitioned by key and joined in reducers.'),
    ('Join explosion', 'Duplicate keys on both sides multiply rows (3 × 4 matches = 12 rows).'),
]) + '''

  <h3>Join types on revenue (8 cities) and targets (7 cities)</h3>
''' + table(['Join', 'Rows', 'Which cities', 'Real result'], [
    ['<code>JOIN</code> (inner)', '6', 'In both lists', 'Chennai, Navi Mumbai, Nashik dropped'],
    ['<code>LEFT JOIN</code>', '8', 'All revenue cities', 'Chennai, Navi Mumbai with target NULL'],
    ['<code>RIGHT JOIN</code>', '7', 'All target cities', 'Nashik with revenue NULL'],
    ['<code>FULL OUTER JOIN</code>', '9', 'Everyone', 'Both kinds of NULL rows'],
    ['<code>LEFT SEMI JOIN</code> (targets with orders)', '6', 'Target cities that have orders', 'Only targets’ columns'],
    ['<code>NOT EXISTS</code> (anti)', '1', 'Target cities without orders', 'Nashik'],
    ['<code>CROSS JOIN</code> payments', '28', '7 targets × 4 payment modes', 'Every combination'],
], minw=680) + lv + '''
EXAM> “Explain the types of joins in Hive with an example.” Draw two small tables, list inner, left outer, right outer, full outer and left semi join with the rows each returns, and state two rules: only equality joins in old versions (non-equi allowed since 2.2), and unmatched columns become NULL in outer joins. Mention map join for small tables.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Choose the join from the question</h2>
''' + table(['Question', 'Join', 'Sketch'], [
    ['Revenue vs target, only cities with both', 'Inner', '<code>s JOIN t ON s.city = t.city</code>'],
    ['Every city with revenue, target if any', 'Left outer', '<code>s LEFT JOIN t ON …</code>'],
    ['Every city on either list', 'Full outer', '<code>s FULL OUTER JOIN t ON …</code> + <code>COALESCE(s.city, t.city)</code>'],
    ['Targets that already have orders', 'Left semi', '<code>t LEFT SEMI JOIN orders o ON t.city = o.city</code>'],
    ['Targets with no orders yet', 'Anti', '<code>WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.city = t.city)</code>'],
    ['Every city × every payment mode (a grid)', 'Cross', '<code>t CROSS JOIN modes</code>'],
    ['Which price band is each order in?', 'Non-equi', '<code>ON o.amount BETWEEN b.lo AND b.hi</code>'],
], minw=680) + cards([
    ('Small × big', 'A small dimension (cities, plans, bands) with a big fact table: Hive picks a map join automatically. Keep statistics fresh so it knows the table is small.', 'Map join'),
    ('Big × big', 'Orders × payments events: a shuffle join by key. Filter and pre-aggregate before joining to shrink both sides.', 'Shuffle join'),
    ('Many tables', 'Fact table joined to several dimensions; joins on the same key share a stage.', 'Star schema'),
    ('Self join', 'A table joined to itself, e.g. customers referred by customers.', 'Hierarchies'),
]) + '''
WARN> Before joining, check that the key is unique on the side you expect to be unique (<code>SELECT key, COUNT(*) … GROUP BY key HAVING COUNT(*) &gt; 1</code>). Duplicate keys on both sides multiply rows and silently double revenue.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Revenue vs target, every way</h2>
  <p>All outputs are real (Hive 4.2.1 lab). <code>s</code> is a CTE with revenue per city: <code>WITH s AS (SELECT city, SUM(amount) AS revenue FROM orders GROUP BY city)</code>.</p>
''' + stepper([
    ('Step 1 · Inner join: only matches',
     code('sql', 'Beeline', "WITH s AS (SELECT city, SUM(amount) AS revenue FROM orders GROUP BY city)\nSELECT s.city, s.revenue, t.monthly_target\nFROM s JOIN city_targets t ON s.city = t.city ORDER BY s.city;", tables(capf('l33_basic.txt'))[0]),
     'Six rows. Chennai and Navi Mumbai (no target) and Nashik (no orders) are dropped without any warning: exactly the CEO’s question.'),
    ('Step 2 · Left join: keep every revenue city',
     code('sql', 'Beeline', "… FROM s LEFT JOIN city_targets t ON s.city = t.city ORDER BY s.city;", tables(capf('l33_basic.txt'))[1]),
     'All 8 revenue cities; the two without a target show NULL. This is the right shape for “achievement per city”, with NULL meaning “no target set”.'),
    ('Step 3 · Full outer join: everyone',
     code('sql', 'Beeline', "SELECT s.city AS s_city, t.city AS t_city, s.revenue, t.monthly_target\nFROM s FULL OUTER JOIN city_targets t ON s.city = t.city\nORDER BY COALESCE(s.city, t.city);", tables(capf('l33_basic.txt'))[2]),
     'Nine cities: six matched, two with only revenue, one (Nashik) with only a target. <code>COALESCE(s.city, t.city)</code> gives one city name for sorting and display.'),
    ('Step 4 · Semi and anti joins',
     code('sql', 'Beeline', "SELECT t.city FROM city_targets t LEFT SEMI JOIN orders o ON t.city = o.city;\nSELECT t.city FROM city_targets t LEFT ANTI JOIN orders o ON t.city = o.city;\nSELECT t.city FROM city_targets t\nWHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.city = t.city);",
          '6 rows: Bengaluru, Delhi, Hyderabad, Mumbai, Pune, Thane\n\n' + capf('l33_anti_err.txt').split('; Query ID')[0] + '\n\n+---------+\n| t.city  |\n+---------+\n| Nashik  |\n+---------+'),
     'The semi join returns each target city once, even though Pune has 7,930 matching orders. Hive 4.2.1 does not accept <code>LEFT ANTI JOIN</code> as syntax, but NOT EXISTS (or LEFT JOIN … WHERE o.city IS NULL) finds Nashik.'),
    ('Step 5 · The WHERE trap in outer joins',
     code('sql', 'Beeline', "-- filter in WHERE\n… FROM s LEFT JOIN city_targets t ON s.city = t.city WHERE t.region = 'West';\n-- filter in ON\n… FROM s LEFT JOIN city_targets t ON s.city = t.city AND t.region = 'West';", capf('l33_onwhere.txt')),
     'In WHERE, the condition runs after the join and drops rows whose region is NULL: 3 rows, an inner join in disguise. In ON, it only decides which target rows match: all 8 cities stay, non-West ones with NULL.'),
    ('Step 6 · NULL keys and the NULL-safe join',
     code('sql', 'Beeline', "-- a: {NULL, 'x'}   b: {NULL, 'x'}\nSELECT a.k, b.k FROM a JOIN b ON a.k = b.k;\nSELECT a.k, b.k FROM a JOIN b ON a.k <=> b.k;", '+------+------+\n| a_k  | b_k  |\n+------+------+\n| x    | x    |\n+------+------+\n+-------+-------+\n|  a_k  |  b_k  |\n+-------+-------+\n| x     | x     |\n| NULL  | NULL  |\n+-------+-------+'),
     'With <code>=</code> the NULL keys never match (NULL = NULL is NULL). With <code>&lt;=&gt;</code> they do. Decide on purpose: unknown customer ids usually should not join to each other.'),
    ('Step 7 · Map join or shuffle join? Read EXPLAIN',
     code('sql', 'Beeline', "EXPLAIN SELECT o.order_id, t.region FROM orders o JOIN city_targets t ON o.city = t.city;\nSET hive.auto.convert.join=false;   -- force a shuffle join, for comparison\nEXPLAIN SELECT o.order_id, t.region FROM orders o JOIN city_targets t ON o.city = t.city;",
          '-- default:\nMap 1 <- Map 2 (BROADCAST_EDGE)\n      Map 1 vectorized\n          Map Join Operator [MAPJOIN_22] (rows=43750 width=92)\n          <-Map 2 [BROADCAST_EDGE] vectorized\n\n-- auto.convert.join=false:\nReducer 2 <- Map 1 (SIMPLE_EDGE), Map 3 (SIMPLE_EDGE)\n      Reducer 2\n          Merge Join Operator [MERGEJOIN_15] (rows=43750 width=92)\n          <-Map 1 [SIMPLE_EDGE] vectorized\n          <-Map 3 [SIMPLE_EDGE] vectorized\n(lines picked from the plans)'),
     'By default the 7-row targets table is broadcast (<b>BROADCAST_EDGE</b>) and the join happens inside the map task reading orders: no reducer. Switched off, both tables are shuffled to Reducer 2 (<b>SIMPLE_EDGE</b> twice). Same result, very different cost on big data.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
LEFT = ['Bengaluru', 'Chennai', 'Mumbai', 'Pune']
RIGHT = ['Bengaluru', 'Mumbai', 'Nashik', 'Pune']
def lists(keepL, keepR, pairs, title):
    o = t(180, 22, title, 9.4, bold=True) + t(70, 40, 's (revenue)', 8, 'acc', bold=True) + t(290, 40, 'targets', 8, 'blue', bold=True)
    for k, c in enumerate(LEFT):
        o += box(14, 48 + k * 26, 112, 20, 'acc' if c in keepL else 'card') + t(70, 62 + k * 26, c, 8, 'ink' if c in keepL else 'ink3', mono=True)
    for k, c in enumerate(RIGHT):
        o += box(234, 48 + k * 26, 112, 20, 'blue' if c in keepR else 'card') + t(290, 62 + k * 26, c, 8, 'ink' if c in keepR else 'ink3', mono=True)
    for a, b in pairs:
        ia, ib = LEFT.index(a), RIGHT.index(b)
        o += f'<path d="M128 {58 + ia * 26}L232 {58 + ib * 26}" style="fill:none;stroke:var(--green);stroke-width:1.8"/>'
    return o
M = [('Bengaluru', 'Bengaluru'), ('Mumbai', 'Mumbai'), ('Pune', 'Pune')]
see = [
    term([('> … FROM s JOIN city_targets t', W), ('    ON s.city = t.city;', W), ('6 rows: Bengaluru, Delhi, Hyderabad,', G), ('        Mumbai, Pune, Thane', G)]),
    term([('> … FROM s LEFT JOIN city_targets t …;', W), ('| Chennai      | 752250.00   | NULL |', Y), ('| Navi Mumbai  | 1172750.00  | NULL |', Y), ('8 rows', G)]),
    term([('> … FROM s FULL OUTER JOIN city_targets t …;', W), ('| Chennai | NULL   | 752250.00 | NULL      |', Y), ('| NULL    | Nashik | NULL      | 500000.00 |', Y), ('9 rows', G)], size=7.6),
    term([('> … t LEFT SEMI JOIN orders o …;   -- 6 rows', W), ('> … WHERE NOT EXISTS (SELECT 1 FROM', W), ('    orders o WHERE o.city = t.city);', W), ('| Nashik  |', G)]),
    term([("> … LEFT JOIN t ON … WHERE t.region = 'West';", W), ('3 rows  (Mumbai, Pune, Thane)', RD), ("> … LEFT JOIN t ON … AND t.region = 'West';", W), ('8 rows  (others with region NULL)', G)], size=7.6),
    term([('> EXPLAIN … orders o JOIN city_targets t …;', W), ('Map 1 <- Map 2 (BROADCAST_EDGE)', G), ('  Map Join Operator [MAPJOIN_22]', G), ('> SET hive.auto.convert.join=false; EXPLAIN …', W), ('Reducer 2 <- Map 1 (SIMPLE_EDGE),', Y), ('             Map 3 (SIMPLE_EDGE)', Y)], size=7.6),
]
B1 = [
    lists(['Bengaluru', 'Mumbai', 'Pune'], ['Bengaluru', 'Mumbai', 'Pune'], M, 'INNER: only matched pairs survive') + cap('Chennai and Nashik have no partner: dropped.', '', 'red', y=164, h=34),
    lists(LEFT, ['Bengaluru', 'Mumbai', 'Pune'], M, 'LEFT: every left row, partner or NULL') + t(180, 92, 'Chennai → NULL', 7.8, 'amber', bold=True) + cap('Left side complete; right side may be NULL.', '', 'amber', y=164, h=34),
    lists(LEFT, RIGHT, M, 'FULL: every row from both sides') + t(180, 92, 'Chennai → NULL', 7.8, 'amber', bold=True) + t(180, 128, 'NULL ← Nashik', 7.8, 'amber', bold=True) + cap('Unmatched rows from both sides, padded with NULL.', '', 'amber', y=164, h=34),
    lists([], ['Nashik'], [], 'ANTI (NOT EXISTS): targets without orders') + t(180, 128, 'no match → kept', 7.8, 'green', bold=True) + cap('SEMI keeps the matched ones, ANTI the unmatched.', '', 'green', y=164, h=34),
    t(180, 22, 'WHERE runs after the join', 9.4, bold=True) + ''.join(label_box(14, 44 + k * 30, 150, 24, [r], tone, 7.6) for k, (r, tone) in enumerate([('Mumbai · West', 'green'), ('Pune · West', 'green'), ('Bengaluru · NULL', 'red'), ('Chennai · NULL', 'red')])) +
    t(262, 70, "WHERE region = 'West'", 8, 'ink', mono=True) + t(262, 86, 'NULL rows fail → dropped', 8, 'red', bold=True) + t(262, 112, "ON … AND region = 'West'", 8, 'ink', mono=True) + t(262, 128, 'rows stay, with NULL', 8, 'green', bold=True) +
    cap('Right-table filters of an outer join belong in ON.', '', 'blue', y=170, h=34),
    t(180, 22, 'Map join: the small table travels', 9.4, bold=True) + label_box(14, 46, 96, 44, ['city_targets', '7 rows'], 'blue', 8) + ''.join(arrow(112, 68, 150, 48 + k * 36, 'green', 1.6) for k in range(3)) +
    ''.join(label_box(152, 34 + k * 36, 196, 30, [f'Map task {k + 1}: orders split + targets'], 'acc', 7.4) for k in range(3)) + cap('No shuffle of orders, no reducer: BROADCAST_EDGE.', '', 'green', y=164, h=34),
]
see_caps = ['The inner join returns six cities.',
            'The left join keeps all eight revenue cities; two have no target.',
            'The full outer join returns nine cities, with NULLs on both sides.',
            'The semi join finds six target cities with orders; NOT EXISTS finds Nashik.',
            'The same filter in WHERE returns 3 rows, in ON returns 8.',
            'EXPLAIN shows a broadcast map join by default and a shuffle join when automatic conversion is off.']
behind_caps = ['Only rows with a partner on both sides are paired.',
               'Unmatched left rows are kept and the right columns are filled with NULL.',
               'Unmatched rows from both sides are kept and padded with NULL.',
               'Semi and anti joins only test whether a partner exists; they add no columns.',
               'The join runs first; WHERE then removes rows where region is NULL, undoing the LEFT join.',
               'The tiny table is copied into memory of every map task, so the big table never moves across the network.']
two = anim_two('Join types', 'Four cities, six joins', 'Real Beeline output', 'Which rows survive each join', see, B1, see_caps, behind_caps)

# ---- scenario 1: join explosion
x1 = (t(180, 22, 'Revenue per customer plan, doubled?', 9.6, bold=True) + t(180, 56, 'orders JOIN customer_addresses ON customer_id', 8.6, 'ink', mono=True) + cap('Total revenue came out 1.6× too high.', '(illustrative)', 'red', y=150, h=46))
x2 = (t(180, 22, 'Some customers have 2 or 3 addresses', 9.6, bold=True) + label_box(20, 46, 140, 60, ['customer 17', '5 orders'], 'acc', 8.4) + label_box(200, 46, 140, 60, ['customer 17', '3 addresses'], 'blue', 8.4) + t(180, 128, '5 × 3 = 15 joined rows', 9, 'red', bold=True) +
      cap('Every order is repeated per address.', '', 'red', y=150, h=34))
x3 = (t(180, 22, 'Detect it before joining', 9.6, bold=True) + t(180, 52, 'SELECT customer_id, COUNT(*) FROM customer_addresses', 8, 'ink', mono=True) + t(180, 66, 'GROUP BY customer_id HAVING COUNT(*) > 1;', 8, 'ink', mono=True) + cap('A key you think is unique often is not.', '', 'amber', y=150, h=34))
x4 = (t(180, 22, 'Fix: make the right side unique', 9.6, 'green', bold=True) + t(180, 56, 'join only the default address (is_default = true)', 8.4, 'ink2') + t(180, 74, 'or aggregate first: one row per customer', 8.4, 'ink2') + cap('One partner per order again.', '', 'green', y=150, h=34))
x5 = (t(180, 22, 'Check after joining', 9.6, 'acc', bold=True) + t(180, 56, 'COUNT(*) before join = COUNT(*) after join?', 8.6, 'ink2') + cap('A cheap guard against silent duplication.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'The join that doubled revenue',
              'Duplicate keys are the most common join bug in reporting. (Numbers illustrative.)',
              'Join explosion', 'Orders joined to a table with several addresses per customer multiply rows; checking key uniqueness and de-duplicating fixes it', [x1, x2, x3, x4, x5],
              ['A report joins orders to customer addresses and revenue comes out far too high.',
               'Customers with several addresses multiply their orders: 5 orders × 3 addresses = 15 rows.',
               'Check key uniqueness with GROUP BY … HAVING COUNT(*) > 1 before joining.',
               'Join to exactly one address per customer, or aggregate the right side first.',
               'Compare row counts before and after the join.'],
              hid='scenario-explosion')

# ---- scenario 2: star schema
st1 = (t(180, 22, 'A star schema', 9.6, bold=True) + node(130, 80, 100, 40, 'orders', 'fact, 50,000', 'acc') + node(20, 30, 90, 34, 'customers', '2,000', 'blue') + node(250, 30, 90, 34, 'city_targets', '7', 'blue') + node(20, 136, 90, 34, 'restaurants', '120', 'blue') + node(250, 136, 90, 34, 'price_bands', '3', 'blue') +
       arrow(128, 92, 110, 58) + arrow(232, 92, 250, 58) + arrow(128, 112, 110, 140) + arrow(232, 112, 250, 140))
st2 = term([('> SELECT c.plan, t.region, COUNT(*), SUM(o.amount)', W), ('  FROM orders o', W), ('  JOIN customers c ON o.customer_id = c.customer_id', W), ('  JOIN city_targets t ON o.city = t.city', W), ("  WHERE o.status = 'DELIVERED' GROUP BY …;", W), ('| Basic  | West  | 10449 | 3069650.00 |', G), ('| Basic  | South |  6856 | 2003620.00 |', G)], size=7.4)
st3 = (t(180, 22, 'Small dimensions → map joins', 9.6, 'green', bold=True) + t(180, 56, 'customers and city_targets fit in memory', 8.4, 'ink2') + t(180, 72, 'orders streams once through both lookups', 8.4, 'ink2') + cap('No shuffle for the joins themselves.', '', 'green', y=150, h=34))
st4 = (t(180, 22, 'Non-equi join to bands (real)', 9.6, bold=True) + t(180, 52, 'ON o.amount BETWEEN b.lo AND b.hi', 8.6, 'ink', mono=True) + bars([('small', 100, 'acc', '26,116'), ('medium', 84, 'blue', '21,848'), ('large', 8, 'green', '2,036')], y=66) +
       cap('Same counts as the CASE in Lesson 3.2.', '', 'blue', y=150, h=34))
st5 = (t(180, 22, 'Order of joins', 9.6, 'acc', bold=True) + ''.join(t(26, 52 + k * 19, s, 8.4, anchor='start') for k, s in enumerate(['• filter the fact table first (WHERE status …)', '• join the most selective dimension first', '• keep dimension statistics fresh (ANALYZE)', '• the cost-based optimiser reorders inner joins'])) +
       cap('Let the optimiser help, but give it statistics.', '', 'green', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'A star schema report: one fact, several dimensions',
              'Warehouse reports join a big fact table to small dimension tables. The numbers here are real lab results.',
              'Star joins', 'Orders joined to customers, targets and price bands; small dimensions become map joins', [st1, st2, st3, st4, st5],
              ['Orders is the fact table; customers, targets, restaurants and price bands are dimensions.',
               'One query joins orders to customers and targets and groups by plan and region.',
               'Small dimensions are broadcast, so the fact table is read once without shuffling for the joins.',
               'A non-equi join assigns each order to a price band.',
               'Filter early, keep statistics fresh and let the optimiser order the joins.'],
              hid='scenario-star')

# ---- scenario 3: skewed join
j1 = (t(180, 22, 'orders JOIN payments ON customer_id', 9.6, bold=True) + ''.join(fill(30 + k * 56, 120 - h, 40, h, 'red' if k == 0 else 'green') for k, h in enumerate([92, 20, 18, 22, 19])) + t(180, 136, 'key NULL (guest checkouts) = 30% of rows', 8.4, 'red', bold=True) +
      cap('One reducer gets all NULL keys.', '(illustrative)', 'red', y=150, h=46))
j2 = (t(180, 22, 'NULL keys never match anyway', 9.6, bold=True) + t(180, 56, "filter them before the join: WHERE customer_id IS NOT NULL", 8, 'ink', mono=True) + cap('Do not shuffle rows that cannot join.', '', 'green', y=150, h=34))
j3 = (t(180, 22, 'A real hot key (one big customer)', 9.6, bold=True) + t(26, 56, 'SET hive.optimize.skewjoin=true;', 8.4, 'ink', anchor='start', mono=True) + t(26, 74, 'SET hive.skewjoin.key=100000;', 8.4, 'ink', anchor='start', mono=True) + cap('Hive handles hot keys in a separate map join.', 'Module 8 covers skew joins in depth.', 'blue', y=150, h=46))
j4 = (t(180, 22, 'Or salt the key', 9.6, bold=True) + t(180, 56, 'spread the hot key over N reducers with a random suffix', 8.4, 'ink2') + cap('Duplicate the small side N times to match.', '', 'blue', y=150, h=34))
j5 = (t(180, 22, 'Spot it in the Tez UI', 9.6, 'acc', bold=True) + t(180, 56, 'one reducer task 10× longer than the median', 8.4, 'ink2') + cap('Check key frequencies before tuning.', '', 'green', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'A shuffle join stuck on one key',
              'Skew hurts joins as much as GROUP BY. Two common causes and their fixes. (Numbers illustrative.)',
              'Skewed joins', 'NULL keys and a hot key overload one reducer in a shuffle join; filtering, skew-join settings and salting help', [j1, j2, j3, j4, j5],
              ['A shuffle join stalls: one reducer receives a third of all rows.',
               'They are NULL keys, which can never match; filter them out before the join.',
               'For a genuine hot key, Hive’s skew-join settings process it separately.',
               'Salting spreads a hot key over several reducers.',
               'Diagnose with task times and key counts before changing settings.'],
              hid='scenario-skewjoin')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Which rows survive each join</h2>
  <p>Left: real Beeline output. Right: four sample cities from each side and the rows each join keeps.</p>
''' + two + '''
  <p>Three live scenarios follow: duplicate keys that explode a join, a star-schema report and a skewed shuffle join.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Joins in real pipelines</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'fact ⋈ dim', 9, 'acc', bold=True) + t(60, 58, 'star schema', 7.4, 'ink2'),
    '1. Enriching facts with dimensions',
    'Order facts get customer plan, restaurant cuisine and city region from dimension tables before reports group by them.',
    ['Facts', '*JOIN dimensions', 'Enriched table']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'LEFT JOIN', 9, 'blue', bold=True, mono=True) + t(60, 58, 'targets vs actuals', 7.4, 'ink2'),
    '2. Targets vs actuals',
    'Business reviews compare actual revenue with targets per city or team. A full outer join shows both missing targets and missing sales.',
    ['Actuals', '*FULL OUTER JOIN', 'Variance report']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'NOT EXISTS', 8.6, 'violet', bold=True, mono=True) + t(60, 58, 'gaps', 7.4, 'ink2'),
    '3. Finding gaps',
    'Customers who signed up but never ordered, payments with no matching order, orders with no delivery record: anti joins find the gaps reconciliation teams chase.',
    ['Two systems', '*Anti join', 'Exceptions list']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'BETWEEN', 9, 'green', bold=True, mono=True) + t(60, 58, 'range lookup', 7.4, 'ink2'),
    '4. Range lookups',
    'Tax slabs, delivery-fee bands and loyalty tiers live in small range tables; a non-equi join assigns each transaction to its slab.',
    ['Transactions', '*ON x BETWEEN lo AND hi', 'Slab per row']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:#D64545"/>' + t(60, 42, 'COUNT check', 8.6, 'red', bold=True) + t(60, 58, 'before = after', 7.4, 'ink2'),
    '5. Join quality checks',
    'Pipelines compare row counts before and after each join and test key uniqueness, so duplicated or lost rows stop the job instead of reaching dashboards.',
    ['Join', '*Count checks', 'Publish or stop']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> you need GROUP BY (<a href="../02-group-by-and-grouping-sets/">Lesson 3.2</a>). The small <code>city_targets</code> and <code>price_bands</code> tables are created in “Run on your PC”.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
