import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l62_join.txt'
def sec(a, b=None, drop=()):
    s = capsec(C, a, b, drop)
    return '\n'.join(l if len(l) <= 140 else l[:137] + ' …' for l in s.split('\n'))

def venn(x, y, left_on=True, mid_on=True, right_on=False, label=''):
    lt = 'blue' if left_on else 'card'
    rt = 'green' if right_on else 'card'
    o = f'<circle cx="{x}" cy="{y}" r="34" class="{TONES[lt][0]}" style="stroke:{TONES[lt][1]};opacity:.9"/>'
    o += f'<circle cx="{x + 40}" cy="{y}" r="34" class="{TONES[rt][0]}" style="stroke:{TONES[rt][1]};opacity:.9"/>'
    if mid_on:
        o += f'<path d="M{x + 20} {y - 27.7}A34 34 0 0 1 {x + 20} {y + 27.7}A34 34 0 0 1 {x + 20} {y - 27.7}Z" class="s-soft-violet" style="stroke:var(--violet)"/>'
    return o + t(x + 20, y + 50, label, 7.4, 'ink', bold=True)

# ---------------------------------------------------------------- story
sc_ = (venn(50, 60, True, True, False, 'left') + venn(170, 60, False, True, False, 'inner') + venn(290, 60, True, False, False, 'left_anti') +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('null rest_id: never matches', 'amber'), ('2 columns named city: AMBIGUOUS', 'red'),
           ('dup key: 5M → +498,646 rows', 'red'), ('inner w/ customers: 5M → 2.5M', 'red'),
           ('broadcast 0.8 s vs SMJ 3.2 s', 'green'), ('anti join: 1 customer never ordered', 'green')])))
scene_svg = scene('A join combines rows of two DataFrames on matching keys. We joined orders with restaurants, promotions and customers and counted what each join type, null key and duplicate key did to the row count.', sc_,
                  'Check <tspan font-weight="700" class="s-acc">row counts</tspan> after every join: joins can lose rows or multiply them.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Half our orders disappeared”</h2>
  <div class="story">
    <p class="narration">Kabir joined 5 million orders with the customer table to add customer plans. The revenue dashboard dropped by half overnight. The next week a colleague joined orders with a city-to-state table that had Pune twice, and Pune’s revenue doubled.</p>

{scene_svg}

K> Sir, a join should just add columns. How can it change the number of rows?
A> An <b>inner</b> join keeps only rows with a match: orders whose customer is not in the customer table vanish. And every match produces a row: if a key appears twice on the right, each order with that key appears twice.
R> So which join should Kabir have used?
A> A left join, and a check that the right-hand key is unique. Today: all join types on a tiny example, null keys, ambiguous columns, duplicate keys, the cost of joining 5 million rows, and broadcast vs sort-merge joins. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Joins at three levels
L1> Matching two lists
      <ul>
        <li>An order slip says “restaurant 101”; the restaurant list says “101 = Desai Mess”. A join writes the name on the slip.</li>
        <li>Inner: keep only slips whose restaurant is on the list. Left: keep all slips, blank name if unknown.</li>
        <li>If the list has 101 twice, the slip is photocopied twice.</li>
      </ul>
L2> The API
      <ul>
        <li><code>a.join(b, on, how)</code>; <code>on</code> is a column name, a list of names (no duplicate key columns) or an expression (<code>a.k == b.k</code>).</li>
        <li><code>how</code>: inner (default), left, right, full, left_semi, left_anti, cross (<code>crossJoin</code>).</li>
        <li>Strategies: broadcast hash join (small side ≤ <code>spark.sql.autoBroadcastJoinThreshold</code>, 10 MB), sort-merge join, shuffled hash join; hint with <code>F.broadcast(df)</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>Null keys matched nothing with <code>==</code> but did with <code>eqNullSafe</code>.</li>
        <li>An inner join with the 2,000-customer table kept 2,498,734 of 5,000,000 orders; a duplicate Pune key added 498,646 rows.</li>
        <li>Joining 5M orders with customers: broadcast 0.8 s, sort-merge (broadcast off) 3.2 s.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Joins</h2>
''' + def_block(
    'A <b>join</b> combines rows from two DataFrames whose join condition evaluates to true. An <b>inner</b> join returns matched pairs only; <b>left/right/full outer</b> joins also return unmatched rows of the left, right or both sides with nulls for the other side; a <b>left semi</b> join returns left rows that have a match (without right columns) and a <b>left anti</b> join left rows without a match; a <b>cross</b> join returns the Cartesian product. Each match produces one output row, so duplicate keys multiply rows. Null keys never satisfy an equality condition; <code>eqNullSafe</code> (<code>&lt;=&gt;</code>) treats nulls as equal. Spark chooses a physical strategy: a <b>broadcast hash join</b> when one side is estimated below <code>spark.sql.autoBroadcastJoinThreshold</code> (10 MB by default) or hinted, otherwise usually a <b>sort-merge join</b>, which shuffles and sorts both sides by the key.',
    'A join puts matching rows from two tables side by side. Inner keeps only matches, left keeps every row of the left table, anti finds rows with no match. Duplicate keys multiply rows and null keys never match. Small tables are sent to every executor (broadcast), big ones are shuffled.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Join key', 'The column(s) compared.'),
    ('inner / left / right / full', 'Which unmatched rows are kept.'),
    ('left_semi', 'Rows of left that have a match.'),
    ('left_anti', 'Rows of left with no match.'),
    ('eqNullSafe', 'Equality where null = null.'),
    ('Broadcast hash join', 'Small side copied to every executor.'),
    ('Sort-merge join', 'Both sides shuffled and sorted by key.'),
    ('Fan-out', 'Rows multiplied by duplicate keys.'),
]) + '''

  <h3>Join types on our example (5 orders, 5 restaurants)</h3>
''' + table(['how', 'Rows', 'Keeps'], [
    ['<code>inner</code>', '3', 'orders with a known restaurant'],
    ['<code>left</code>', '5', 'all orders (unknown restaurant → null name)'],
    ['<code>right</code>', '5', 'all restaurants'],
    ['<code>full</code>', '7', 'everything from both'],
    ['<code>left_semi</code>', '3', 'orders that have a restaurant (order columns only)'],
    ['<code>left_anti</code>', '2', 'orders with no restaurant'],
    ['<code>crossJoin</code>', '25', 'every pair'],
], minw=560) + lv + '''
EXAM> “Why did my row count change after a join?” An inner join drops rows without a match (our 5M orders became 2.5M because half the customer ids were missing from the dimension), and duplicate keys on the other side multiply rows (one duplicate Pune row added 498,646). Use left joins for enrichment, check the right key is unique, and compare counts before and after.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Join strategies</h2>
''' + table(['Strategy', 'Chosen when', 'Shuffle', 'Lab (5M orders × customers)'], [
    ['Broadcast hash join', 'One side small (≤ 10 MB est.) or <code>broadcast()</code> hint', 'No (small side copied)', '0.8 s; 0.3 s with hint'],
    ['Sort-merge join', 'Both sides large (default for equi-joins)', 'Both sides', '3.2 s with broadcast off; 5M × 5M: 4.5 s'],
    ['Shuffled hash join', 'One side much smaller but too big to broadcast (AQE may pick it)', 'Both sides', '—'],
    ['Broadcast nested loop', 'Non-equi joins (e.g. ranges)', 'No', 'Can be very slow'],
    ['Cartesian product', 'crossJoin of two large sides', 'Yes', 'Avoid'],
], minw=700) + '''
WARN> After <code>a.join(b, a.k == b.k)</code> both <code>k</code> columns stay, and any other column with the same name (like <code>city</code>) becomes <b>ambiguous</b>. Join on a list of names (<code>a.join(b, ["k"])</code>) to keep one key column, and rename or alias the other duplicates before or right after the join.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Joins that lose, add and multiply rows</h2>
  <p>All outputs are real: PySpark 4.3.0, local mode with 4 cores. Steps 1–4 use 5 orders and 5 restaurants (one order and one restaurant have a null id); Steps 5–6 use 5M orders and the 2,000-row customer table.</p>
''' + stepper([
    ('Step 1 · Six join types',
     code('python', 'l62_join.py', 'for how in ("inner", "left", "right", "full", "left_semi", "left_anti"):\n    r = orders.join(rest.select("rest_id", "name"), "rest_id", how)\n    print(how, r.count(), …)', sec('== 1)', '== 2)')),
     'Inner kept the 3 orders with a known restaurant. Left kept all 5, with null names for order 4 (null id) and order 5 (id 109, unknown). Right and full added restaurants without orders. <code>left_semi</code> answered “which orders have a restaurant” without bringing restaurant columns; <code>left_anti</code> found the 2 that do not: the classic data-quality check.'),
    ('Step 2 · Null keys never match',
     code('python', 'l62_join.py', 'orders.join(rest, orders.rest_id == rest.rest_id).where(orders.rest_id.isNull()).count()\norders.join(rest, orders.rest_id.eqNullSafe(rest.rest_id)).where(orders.rest_id.isNull()).count()', sec('== 2)', '== 3)')),
     'Order 4 and “Unknown Kitchen” both have a null id, yet <code>==</code> did not match them: null = null is unknown (Lesson 4.4). <code>eqNullSafe</code> matched them. Usually not matching nulls is what you want; use null-safe joins only when null is a real, meaningful key.'),
    ('Step 3 · Ambiguous columns',
     code('python', 'l62_join.py', 'j = orders.join(rest, orders.rest_id == rest.rest_id); j.columns\nj.select("city")\norders.join(rest, ["rest_id"]).columns\nj.select(orders.city.alias("order_city"), rest.city.alias("rest_city"), "name")', sec('== 3)', '== 4)')),
     'Joining on an expression kept <b>both</b> <code>rest_id</code> columns and both <code>city</code> columns; selecting <code>city</code> failed with AMBIGUOUS_REFERENCE. Joining on a list kept one <code>rest_id</code> (first), but <code>city</code> was still duplicated. Refer to columns through their DataFrame (<code>orders.city</code>) and alias them.'),
    ('Step 4 · Duplicate keys multiply rows',
     code('python', 'l62_join.py', 'orders.join(promos, "city").count()          # Pune has 3 promo codes\ncities = spark.createDataFrame([("Pune", "MH"), ("Pune", "Maharashtra")], "city STRING, state STRING")\nbig.join(cities, "city").count()', sec('== 4)', '== 5)')),
     'Three Pune orders × three Pune promos = 9 rows, plus 1 Delhi = 10 from 5 orders (Mumbai, without promos, vanished in the inner join). On real data, a lookup table with Pune entered twice turned 498,646 Pune orders into <b>997,292</b> rows: Pune revenue doubled. Check uniqueness before joining: <code>dim.groupBy(key).count().where("count &gt; 1")</code>.'),
    ('Step 5 · Inner join with a dimension, and strategies',
     code('python', 'l62_join.py', 'custs = spark.read.csv(".../customers.csv", header=True, inferSchema=True)   # 2,000 rows\nbig.join(custs, "customer_id")                    # strategy from the plan\nbig.join(big.select("order_id", …), "order_id")\nspark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1); big.join(custs, "customer_id").count()\nbig.join(F.broadcast(custs), "customer_id").count()', sec('== 5)', '== 7)')),
     'The orders reference 4,000 customer ids but the customer table holds 2,000: the inner join silently returned <b>2,498,734</b> of 5,000,000 rows, Kabir’s missing half. Use <code>left</code> to enrich. The small table was broadcast automatically (0.8 s); with broadcast disabled Spark used a sort-merge join and took 3.2 s. Two big sides always need a sort-merge join (4.5 s here).'),
    ('Step 6 · Semi and anti joins for questions',
     code('python', 'l62_join.py', 'custs.join(big, "customer_id", "left_anti").count()     # never ordered\ncusts.join(big, "customer_id", "left_semi").count()     # ordered at least once', sec('== 7)')),
     'Semi and anti joins answer “exists?” questions without duplicating rows: each customer appears at most once however many orders they have. Far better than a join followed by <code>distinct</code>, and the right tool for finding orphans in data-quality checks.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('inner 3, left 5, right 5, full 7', W), ('left_semi 3, left_anti 2', G)], size=7.6),
    term([('null == null      : 0 matches', Y), ('eqNullSafe        : 1 match', G)], size=7.6),
    term([("columns: …rest_id, …rest_id, city, city", W), ('select("city"): AMBIGUOUS_REFERENCE', RD)], size=7.2),
    term([('5 orders x promos -> 10 rows', Y), ('Pune 498,646 -> 997,292 rows', RD)], size=7.4),
    term([('inner with customers: 2,498,734', RD), ('broadcast 0.8 s | SMJ 3.2 s', G)], size=7.4),
]
B1 = [
    t(180, 14, 'What each join keeps', 9.4, bold=True) + venn(40, 66, False, True, False, 'inner') + venn(150, 66, True, True, False, 'left') + venn(260, 66, True, True, True, 'full') + cap('Choose by which rows must survive.', '', 'blue', y=144, h=30),
    t(180, 14, 'NULL = NULL is unknown', 9.4, bold=True) + opbox(30, 50, 'order 4', 'rest_id NULL', 'card', 110, 30) + opbox(220, 50, 'Unknown Kitchen', 'rest_id NULL', 'card', 110, 30) + t(180, 70, '≠', 14, 'red', bold=True) + cap('eqNullSafe makes them match.', '', 'amber', y=144, h=30),
    t(180, 14, 'Both sides keep their columns', 9.4, bold=True) + flow([('orders.city', 'Pune', 'blue'), ('rest.city', 'Pune', 'green')], y=50, w=120, gap=30) + cap('Alias duplicates after the join.', '', 'red', y=144, h=30),
    t(180, 14, 'One row per match', 9.4, bold=True) + opbox(20, 56, 'Pune order', '× 1', 'blue', 100, 30) + ''.join(arrow(120, 71, 200, 40 + k * 32, 'ink3', 1.0) + opbox(204, 28 + k * 32, ['FEST20', 'NEW50', 'WEEKEND'][k], '', 'acc', 100, 24) for k in range(3)) + cap('Duplicate keys multiply rows.', '', 'red', y=144, h=30),
    t(180, 14, 'Small side goes everywhere', 9.4, bold=True) + opbox(20, 56, 'customers', '2,000 rows', 'green', 100, 30) + ''.join(arrow(120, 71, 200, 40 + k * 32, 'ink3', 1.0) + opbox(204, 28 + k * 32, f'executor {k + 1}', 'orders part', 'blue', 110, 24) for k in range(3)) + cap('No shuffle of the 5M orders.', '', 'green', y=144, h=30),
]
see_caps = ['Six types, six row counts.', 'Null keys did not match.', 'Two columns with one name.', 'One duplicate doubled Pune.', 'Half the orders vanished; broadcast 4x faster.']
behind_caps = ['Unmatched rows: dropped or kept.', 'Three-valued logic again.', 'Joins keep both inputs’ columns.', 'Each match is an output row.', 'Broadcast hash join for small tables.']
two = anim_two('Joins', 'Matching rows across tables', 'Real lab outputs', 'How rows are matched', see, B1, see_caps, behind_caps)

# ---- scenario 1: missing customers
e1 = (t(180, 22, 'Enrich orders with plans', 9.4, bold=True) + t(180, 56, 'orders.join(customers, "customer_id")', 8.2, 'ink', mono=True) + cap('Default: inner.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Revenue halves overnight', 9.4, bold=True) + t(180, 56, 'new customers not yet in the dim', 8.4, 'ink2') + cap('2.5M of 5M orders kept.', '', 'red', y=150, h=34))
e3 = (t(180, 22, 'Use a left join', 9.4, bold=True) + t(180, 56, 'join(customers, "customer_id", "left")', 8.2, 'ink', mono=True) + cap('All orders survive.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Count orphans', 9.4, bold=True) + t(180, 56, 'left_anti join → alert', 8.4, 'ink2') + cap('Fix the dimension load.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Assert counts', 9.4, 'acc', bold=True) + t(180, 56, 'rows after enrichment == rows before', 8.2, 'ink2') + cap('In every pipeline.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Half the revenue disappeared',
              'Inner joins drop unmatched rows. (Numbers from our lab.)',
              'Inner join loss', 'An inner join with an incomplete dimension silently drops facts; enrich with left joins and alert on orphans', [e1, e2, e3, e4, e5],
              ['Inner join.', 'Rows lost.', 'Left join.', 'Orphans.', 'Assert.'],
              hid='scenario-inner-loss')

# ---- scenario 2: duplicate dimension rows
b1 = (t(180, 22, 'City → state lookup', 9.4, bold=True) + t(180, 56, 'Pune entered twice (MH, Maharashtra)', 8.2, 'ink2') + cap('A manual edit.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Pune revenue doubles', 9.4, bold=True) + t(180, 56, '498,646 → 997,292 rows', 8.4, 'ink', mono=True) + cap('Like our Step 4.', '', 'red', y=150, h=34))
b3 = (t(180, 22, 'Check the key is unique', 9.4, bold=True) + t(180, 56, 'groupBy(key).count().where("count > 1")', 7.8, 'ink', mono=True) + cap('Before every join.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Deduplicate the dimension', 9.4, bold=True) + t(180, 56, 'one row per key (row_number)', 8.4, 'ink2') + cap('Lesson 4.4.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Enforce in the table', 9.4, 'acc', bold=True) + t(180, 56, 'unique-key tests in CI', 8.4, 'ink2') + cap('Catch it on load.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Pune’s revenue doubled',
              'Fan-out from duplicate keys. (Numbers from our lab.)',
              'Join fan-out', 'Duplicate keys on the lookup side multiply fact rows; test key uniqueness before joining', [b1, b2, b3, b4, b5],
              ['Duplicate key.', 'Doubled.', 'Check.', 'Dedup.', 'Enforce.'],
              hid='scenario-fanout')

# ---- scenario 3: broadcast choice
u1 = (t(180, 22, 'Join 2B events with a 50 MB dim', 9.4, bold=True) + t(180, 56, 'above the 10 MB threshold', 8.4, 'ink2') + cap('Sort-merge join chosen.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Both sides shuffled', 9.4, bold=True) + t(180, 56, '2B rows over the network', 8.4, 'ink2') + cap('Slow.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'broadcast(dim) hint', 9.4, bold=True) + t(180, 56, 'or raise the threshold to 100 MB', 8.4, 'ink2') + cap('Dim copied to executors.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Big table not shuffled', 9.4, bold=True) + t(180, 56, 'our lab: 3.2 s → 0.3 s', 8.4, 'ink2') + cap('With the hint.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Not for big sides', 9.4, 'acc', bold=True) + t(180, 56, 'driver and executor memory limits', 8.4, 'ink2') + cap('Lesson 8.2.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'A dimension just above the threshold',
              'Choosing the join strategy. (Typical; timings from our lab.)',
              'Broadcast joins', 'Broadcasting a small table avoids shuffling the large one; hint or raise the threshold within memory limits', [u1, u2, u3, u4, u5],
              ['Above threshold.', 'Shuffle.', 'Hint.', 'Faster.', 'Limits.'],
              hid='scenario-broadcast-join')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Matching rows across tables</h2>
  <p>Left: real outputs. Right: how rows are matched.</p>
''' + two + '''
  <p>Three live scenarios follow: revenue that halved, revenue that doubled, and a dimension just above the broadcast threshold.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Joins at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'star', 12, 'blue', bold=True) + t(60, 58, 'schema', 7.4, 'ink2'),
    '1. Fact + dimensions',
    'Order facts are enriched with customer, restaurant and date dimensions using left broadcast joins.',
    ['Facts', '*left + broadcast', 'Wide table']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'DQ', 12, 'green', bold=True) + t(60, 58, 'orphans', 7.4, 'ink2'),
    '2. Orphan checks',
    'left_anti joins list facts whose keys are missing in the dimension.',
    ['Facts', '*left_anti', 'Alerts']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'CDC', 12, 'violet', bold=True) + t(60, 58, 'upserts', 7.4, 'ink2'),
    '3. Applying changes',
    'Full outer joins between snapshots find inserted, updated and deleted rows.',
    ['Old + new', '*full join', 'Changes']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'segments', 10, 'acc', bold=True) + t(60, 58, 'marketing', 7.4, 'ink2'),
    '4. Audience building',
    'Semi and anti joins pick customers who ordered last month but not this month.',
    ['Customers', '*semi / anti', 'Campaign list']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'fraud', 12, 'acc', bold=True) + t(60, 58, 'links', 7.4, 'ink2'),
    '5. Linking records',
    'Self-joins on device or phone find accounts that share identifiers.',
    ['Accounts', '*self-join', 'Linked pairs']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> broadcast joins in <a href="../../03-persistence-and-shared-variables/02-broadcast-variables-and-accumulators/">3.2</a>, nulls in <a href="../../04-dataframes/04-nulls-and-duplicates/">4.4</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
