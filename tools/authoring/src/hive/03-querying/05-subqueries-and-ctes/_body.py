import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()

# ---------------------------------------------------------------- story
sc = (box(10, 12, 290, 128, 'red') + t(155, 30, 'Before: one 40-line nested query', 8.8, 'red', bold=True) +
      ''.join(box(24 + k * 12, 42 + k * 14, 262 - k * 24, 86 - k * 28, 'card') for k in range(3)) + t(155, 132, 'SELECT … FROM (SELECT … FROM (SELECT …', 7.4, 'ink2', mono=True) +
      arrow(304, 76, 336, 76, 'ink3', 2.2) + box(340, 12, 290, 128, 'green') + t(485, 30, 'After: named steps with WITH', 8.8, 'green', bold=True) +
      ''.join(label_box(352, 42 + k * 30, 266, 24, [s], tone, 7.6) for k, (s, tone) in enumerate([('city_rev   AS (revenue per city)', 'acc'), ('avg_rev    AS (average of city_rev)', 'blue'), ('SELECT … FROM city_rev CROSS JOIN avg_rev', 'violet')])))
scene_svg = scene('A deeply nested query is rewritten as named steps with a WITH clause: city revenue, its average, and a final select.', sc,
                  'Same result, but each step has a <tspan font-weight="700" class="s-acc">name</tspan> you can read and test.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Which cities beat the average city, and by how much?”</h2>
  <div class="story">
    <p class="narration">Riya inherits a 40-line report query with three levels of brackets: revenue per city, then the average of those revenues, then the cities above average. Nobody dares to touch it. She also has a bug: a “cities without orders” check returns nothing, although Nashik clearly has no orders.</p>

{scene_svg}

R> Sir, can a query use the result of another query?
A> In three places. In <b>FROM</b>, a subquery is a temporary table. In <b>WHERE</b>, a subquery answers a question such as “is this customer in the Gold list?”. And with <b>WITH</b>, a common table expression, you give each step a name and read the query top to bottom like a recipe.
K> And her empty result?
A> That is the most famous trap in SQL: <code>NOT IN</code> with a NULL in the list returns no rows at all. We will reproduce it, then fix it with NOT EXISTS. Today you will also stack results with UNION, find common rows with INTERSECT and differences with EXCEPT.
  </div>
</section>
'''

lv = '''
LEVELS> Subqueries at three levels
L1> A question inside a question
      <ul>
        <li>“Show the Gold customers’ orders” needs a list first (who is Gold?) and then a filter. The inner question is a <b>subquery</b>.</li>
        <li>A <b>CTE</b> (<code>WITH name AS (…)</code>) is the same idea with a label, like writing intermediate results on a whiteboard with headings.</li>
        <li><b>UNION</b> stacks two lists; <b>INTERSECT</b> keeps what is on both; <b>EXCEPT</b> keeps what is only on the first.</li>
      </ul>
L2> Where subqueries can go in Hive
      <ul>
        <li><b>FROM (subquery) alias</b>: a derived table. Hive requires the alias (ParseException without it in our lab).</li>
        <li><b>WHERE col [NOT] IN (subquery)</b>, <b>WHERE [NOT] EXISTS (subquery)</b>: correlated subqueries can refer to the outer row.</li>
        <li><b>Scalar subqueries</b> returning one value: in WHERE and HAVING (<code>amount &gt; (SELECT AVG(amount) * 2.5 FROM orders)</code>), and in Hive 4 also in the SELECT list (tested).</li>
        <li><b>WITH a AS (…), b AS (…) SELECT …</b>: later CTEs can use earlier ones; a CTE exists only for that statement.</li>
        <li><b>UNION ALL</b> keeps duplicates; <b>UNION</b> (= UNION DISTINCT) removes them; <b>INTERSECT</b>, <b>EXCEPT</b> and <b>MINUS</b> are supported (distinct by default). Both sides must have the same number of compatible columns.</li>
      </ul>
L3> How Hive runs them
      <ul>
        <li><b>IN/EXISTS subqueries become joins</b>: semi joins for IN/EXISTS, anti joins for NOT EXISTS. Check EXPLAIN.</li>
        <li><b>NOT IN and NULL</b>: <code>x NOT IN (a, b, NULL)</code> is never true (it is NULL when x is not a or b), so the whole query returns nothing. NOT EXISTS ignores NULLs.</li>
        <li><b>CTE materialisation:</b> a CTE is normally inlined like a view. If it is referenced at least <code>hive.optimize.cte.materialize.threshold</code> times (3 in our lab), Hive computes it once into a temporary table.</li>
        <li><b>UNION</b> needs an extra de-duplication shuffle; prefer UNION ALL when duplicates are impossible or wanted.</li>
        <li>Scalar subqueries must return at most one row; otherwise the query fails at run time.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Subqueries, CTEs and set operations</h2>
''' + def_block(
    'A <b>subquery</b> is a SELECT statement nested inside another statement: in the FROM clause as a derived table (which must be aliased), or in WHERE/HAVING (and in Hive 4 the SELECT list) as an <b>IN</b>, <b>EXISTS</b> or <b>scalar</b> subquery, optionally <b>correlated</b> with the outer query. A <b>common table expression</b> (CTE) defines named, statement-scoped result sets with <code>WITH name AS (SELECT …)</code>. <b>Set operations</b> combine results of compatible queries: <b>UNION ALL</b> (all rows), <b>UNION [DISTINCT]</b>, <b>INTERSECT</b> and <b>EXCEPT/MINUS</b>.',
    'You can use one query’s result inside another: as a temporary table, as a list to check against, or as a single number to compare with. WITH lets you name each step. UNION, INTERSECT and EXCEPT combine two result lists like set operations.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Derived table', 'A subquery in FROM, used like a table: <code>FROM (SELECT …) r</code>.'),
    ('Correlated subquery', 'A subquery that refers to the outer row: <code>WHERE o.customer_id = c.customer_id</code>.'),
    ('Scalar subquery', 'Returns exactly one value, e.g. the overall average.'),
    ('CTE', 'Common table expression: <code>WITH name AS (…)</code>, valid for one statement.'),
    ('Inlining', 'Replacing a CTE or view by its query text during compilation.'),
    ('Materialisation', 'Computing a CTE once into a temporary table and reusing it.'),
    ('Set operation', 'UNION, INTERSECT, EXCEPT: combine two results with the same columns.'),
    ('NOT IN trap', 'A NULL in the NOT IN list makes the condition NULL for every row.'),
]) + '''

  <h3>Choosing the right construct</h3>
''' + table(['Need', 'Use', 'Real example (lab)'], [
    ['Filter on an aggregated result', 'Derived table or CTE', 'Cities with revenue &gt; Rs 20 lakh → 3 rows'],
    ['Rows whose key is in another list', '<code>IN (subquery)</code> or <code>EXISTS</code>', 'Orders of Gold customers → 13,014'],
    ['Rows with no match', '<code>NOT EXISTS</code> (not NOT IN!)', 'Target cities without orders → Nashik'],
    ['Compare with one computed value', 'Scalar subquery', 'Orders above 2.5 × average → Rs 880 orders'],
    ['Several steps, readable', 'CTEs with WITH', 'Cities above the average city: 3 rows'],
    ['Stack two results', 'UNION ALL / UNION', '10 rows vs 7 distinct cities'],
    ['Common or missing values', 'INTERSECT / EXCEPT / MINUS', '6 common cities; Nashik; Chennai and Navi Mumbai'],
], minw=680) + lv + '''
EXAM> “What is a subquery? Give two types.” Define it as a query inside another, then show a FROM-clause subquery (with alias) and a WHERE-clause subquery with IN or EXISTS. Mention that Hive converts IN/EXISTS into semi joins and that CTEs (WITH) make long queries readable.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Subquery forms and set operations</h2>
''' + cards([
    ('FROM-clause subquery', 'A temporary table inside one query. Must have an alias: <code>FROM (…) r</code>.', 'Derived table'),
    ('IN / NOT IN', 'Membership in a list. Safe with IN; dangerous with NOT IN when the list can contain NULL.', 'Lists'),
    ('EXISTS / NOT EXISTS', 'Correlated yes/no test per row. The safe way to write anti joins.', 'Existence'),
    ('Scalar subquery', 'One value: thresholds, averages, maximums. Allowed in WHERE, HAVING and (Hive 4) SELECT.', 'Single value'),
    ('WITH (CTE)', 'Named steps, top to bottom. Can chain: later CTEs read earlier ones.', 'Readability'),
    ('UNION ALL / UNION', 'Stack results; UNION removes duplicates with an extra shuffle.', 'Combine'),
    ('INTERSECT / EXCEPT', 'Common rows / rows only in the first result; MINUS is a synonym for EXCEPT.', 'Compare'),
]) + '''
WARN> Never write <code>WHERE id NOT IN (SELECT id FROM other)</code> unless <code>other.id</code> is declared or filtered <code>NOT NULL</code>. One NULL and the query silently returns zero rows. <code>NOT EXISTS</code> gives the expected answer.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>From nested brackets to named steps</h2>
  <p>All outputs are real, from the Hive 4.2.1 lab.</p>
''' + stepper([
    ('Step 1 · A subquery in FROM (with its alias)',
     code('sql', 'Beeline', "SELECT city, revenue\nFROM (SELECT city, SUM(amount) AS revenue FROM orders GROUP BY city) r\nWHERE revenue > 2000000 ORDER BY revenue DESC;\n\n-- the same without the alias r:\nSELECT city, revenue FROM (SELECT city, SUM(amount) AS revenue FROM orders GROUP BY city)\nWHERE revenue > 2000000;",
          tables(capf('l35_from.txt'))[0] + '\n\n' + capf('l35_from.txt').split('Error: ')[1].split('; Query ID')[0].join(['Error: ', ''])),
     'The inner query is a temporary table with a column called revenue, which the outer WHERE can filter, something impossible in one level (Lesson 3.1). Hive insists on a name for the derived table.'),
    ('Step 2 · IN, EXISTS and scalar subqueries in WHERE',
     code('sql', 'Beeline', "SELECT COUNT(*) AS gold_orders FROM orders\nWHERE customer_id IN (SELECT customer_id FROM customers WHERE plan = 'Gold');\n\nSELECT COUNT(*) AS big_spenders FROM customers c\nWHERE EXISTS (SELECT 1 FROM orders o\n              WHERE o.customer_id = c.customer_id AND o.amount >= 800);\n\nSELECT order_id, amount FROM orders\nWHERE amount > (SELECT AVG(amount) * 2.5 FROM orders)\nORDER BY amount DESC LIMIT 3;", capf('l35_where.txt')),
     'Gold customers placed 13,014 orders; 51 customers have at least one order of Rs 800 or more (a correlated EXISTS); and the scalar subquery computes 2.5 × the average once, then filters.'),
    ('Step 3 · The NOT IN trap',
     code('sql', 'Beeline', "-- no NULL in the list:\nSELECT city FROM city_targets WHERE city NOT IN (SELECT DISTINCT city FROM orders);\n-- one NULL added to the list:\nSELECT city FROM city_targets WHERE city NOT IN\n  (SELECT city FROM (SELECT DISTINCT city FROM orders\n                     UNION ALL SELECT CAST(NULL AS STRING) AS city) x);\n-- NOT EXISTS with the same list:\nSELECT city FROM city_targets t WHERE NOT EXISTS\n  (SELECT 1 FROM (… same list with NULL …) x WHERE x.city = t.city);", capf('l35_notin.txt')),
     'Same question, three answers. With a NULL in the list, <code>\'Nashik\' NOT IN (…, NULL)</code> is NULL, not true, so <b>no row</b> survives. NOT EXISTS ignores the NULL and still returns Nashik. This is Riya’s bug.'),
    ('Step 4 · The same report as named steps (CTEs)',
     code('sql', 'Beeline', "WITH city_rev AS (SELECT city, SUM(amount) AS revenue FROM orders\n                  WHERE status = 'DELIVERED' GROUP BY city),\n     avg_rev  AS (SELECT AVG(revenue) AS avg_revenue FROM city_rev)\nSELECT c.city, c.revenue, ROUND(c.revenue / a.avg_revenue, 2) AS vs_avg\nFROM city_rev c CROSS JOIN avg_rev a\nWHERE c.revenue > a.avg_revenue ORDER BY c.revenue DESC;", tables(capf('l35_cte_union.txt'))[0]),
     '<code>avg_rev</code> reads <code>city_rev</code>, and the final SELECT reads both. Mumbai earns 1.60 × the average city’s delivered revenue. Each step can be tested alone by selecting from it.'),
    ('Step 5 · Scalar subqueries in SELECT and HAVING (Hive 4)',
     code('sql', 'Beeline', "SELECT t.city, (SELECT COUNT(*) FROM orders o WHERE o.city = t.city) AS n\nFROM city_targets t ORDER BY t.city LIMIT 3;\n\nSELECT city, SUM(amount) FROM orders GROUP BY city\nHAVING SUM(amount) > (SELECT AVG(amount) * 8000 FROM orders);", capf('l35_selectsub.txt') + '\n' + capf('l35_having.txt')),
     'A correlated scalar subquery in the SELECT list counts orders per target city; Hive rewrites it into a join and aggregation. HAVING can compare groups with a scalar subquery too.'),
    ('Step 6 · UNION ALL vs UNION',
     code('sql', 'Beeline', "SELECT city FROM city_targets UNION ALL SELECT city FROM restaurants WHERE restaurant_id <= 3;\nSELECT city FROM city_targets UNION     SELECT city FROM restaurants WHERE restaurant_id <= 3;",
          '10 rows with UNION ALL (Thane, Mumbai, Thane, Mumbai, Pune, …)\n' + tables(capf('l35_cte_union.txt'))[2]),
     '7 targets + 3 restaurants = 10 rows with UNION ALL, duplicates included. UNION removes duplicates: 7 distinct cities, at the cost of an extra shuffle.'),
    ('Step 7 · INTERSECT, EXCEPT, MINUS',
     code('sql', 'Beeline', "SELECT DISTINCT city FROM orders INTERSECT SELECT city FROM city_targets;\nSELECT city FROM city_targets EXCEPT SELECT DISTINCT city FROM orders;\nSELECT DISTINCT city FROM orders MINUS  SELECT city FROM city_targets;",
          tables(capf('l35_cte_union.txt'))[3] + '\n' + tables(capf('l35_cte_union.txt'))[4] + '\n' + tables(capf('l35_cte_union.txt'))[5]),
     'Six cities have both orders and targets; Nashik has a target but no orders; Chennai and Navi Mumbai have orders but no target: the same answers the joins gave in Lesson 3.3, written as set operations.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('> WITH city_rev AS (… GROUP BY city),', W), ('       avg_rev AS (SELECT AVG(revenue) …', W), ('                   FROM city_rev)', W), ('  SELECT … FROM city_rev c', W), ('  CROSS JOIN avg_rev a WHERE …;', W)]),
    term([('> SET hive.optimize.cte.materialize.threshold;', W), ('| hive.optimize.cte.materialize.threshold=3 |', G), ('', W), ('-- city_rev is used 2 times (< 3):', Y), ('-- inlined, not materialised', Y)]),
    term([('| Mumbai     | 2712610.00  | 1.60 |', G), ('| Bengaluru  | 2499060.00  | 1.47 |', G), ('| Pune       | 2148270.00  | 1.27 |', G), ('3 rows selected', Y)]),
    term([("> … WHERE city NOT IN (SELECT DISTINCT city", W), ("      FROM orders UNION ALL SELECT NULL …);", W), ('+-------+', G), ('| city  |', G), ('+-------+', G), ('+-------+', G), ('(no rows)', RD)]),
    term([("> … WHERE NOT EXISTS (SELECT 1 FROM (…) x", W), ("      WHERE x.city = t.city);", W), ('| Nashik  |', G)]),
]
B1 = [
    t(180, 22, 'Named steps form a small pipeline', 9.4, bold=True) + label_box(14, 50, 104, 54, ['orders', '50,000 rows'], 'card', 8) + arrow(120, 77, 134, 77) + label_box(136, 50, 100, 54, ['city_rev', '8 rows'], 'acc', 8) + arrow(238, 77, 252, 77) + label_box(254, 50, 92, 54, ['avg_rev', '1 row'], 'blue', 8) +
    cap('Each CTE reads the ones before it.', '', 'blue', y=170, h=34),
    t(180, 22, 'CTEs are inlined (like views)', 9.4, bold=True) + box(30, 44, 300, 90, 'card') + t(180, 64, 'SELECT … FROM (city_rev query) c', 8, 'ink', mono=True) + t(180, 82, 'CROSS JOIN (SELECT AVG(revenue)', 8, 'ink', mono=True) + t(180, 98, '            FROM (city_rev query)) a', 8, 'ink', mono=True) +
    cap('Used 3+ times → computed once (threshold 3).', '', 'blue', y=170, h=34),
    t(180, 22, 'Final step: compare each city with the average', 9.2, bold=True) + bars([('Mumbai', 100, 'green', '1.60×'), ('Bengaluru', 92, 'green', '1.47×'), ('Pune', 79, 'green', '1.27×'), ('average', 62, 'grey', '1.00×')], y=44, x=110, w=190) +
    cap('Only cities above 1.00× are returned.', '', 'green', y=170, h=34),
    t(180, 22, "Why NOT IN (…, NULL) returns nothing", 9.4, 'red', bold=True) + t(180, 52, "'Nashik' NOT IN ('Pune', …, NULL)", 8.6, 'ink', mono=True) + t(180, 72, "= 'Nashik'<>'Pune' AND … AND 'Nashik'<>NULL", 8.2, 'ink', mono=True).replace("<>", '&lt;&gt;') + t(180, 92, '= TRUE AND … AND NULL  →  NULL', 8.6, 'red', mono=True, bold=True) +
    cap('NULL is not TRUE, so WHERE drops every row.', '', 'red', y=170, h=34),
    t(180, 22, 'NOT EXISTS looks for a matching row', 9.4, 'green', bold=True) + t(180, 56, "is there x with x.city = 'Nashik'?", 8.6, 'ink', mono=True) + t(180, 76, "NULL = 'Nashik' is NULL → not a match", 8.4, 'ink2') + t(180, 96, 'no match found → Nashik kept', 8.6, 'green', bold=True) +
    cap('NULLs in the list cannot block the answer.', '', 'green', y=170, h=34),
]
see_caps = ['Riya rewrites the nested report with two named CTEs.',
            'The materialisation threshold is 3; city_rev is used twice, so Hive inlines it.',
            'Three cities beat the average city’s delivered revenue.',
            'With one NULL in the list, NOT IN returns no rows at all.',
            'NOT EXISTS with the same list correctly returns Nashik.']
behind_caps = ['orders feeds city_rev (8 rows), which feeds avg_rev (1 row); the final SELECT uses both.',
               'CTEs are expanded like views; a CTE referenced at least 3 times would be computed once into a temporary table.',
               'Each city’s revenue is divided by the average; only ratios above 1 pass the WHERE.',
               'NOT IN expands to a chain of <> comparisons joined by AND; one comparison with NULL makes the whole result NULL.',
               'NOT EXISTS asks whether a matching row exists. NULL never matches, so it cannot hide the answer.']
two = anim_two('CTEs and NOT IN', 'Named steps, and the NULL trap', 'Real Beeline output', 'How Hive evaluates the CTEs and the NOT IN condition', see, B1, see_caps, behind_caps)

# ---- scenario 1: refactor
r1 = (t(180, 22, 'A 120-line report nobody can change', 9.6, bold=True) + ''.join(box(20 + k * 14, 40 + k * 12, 320 - k * 28, 100 - k * 24, 'card') for k in range(4)) + cap('Four levels of nesting, one typo away from wrong.', '', 'red', y=160, h=34))
r2 = (t(180, 22, 'Step 1: lift each level into a CTE', 9.6, bold=True) + ''.join(label_box(24, 44 + k * 26, 312, 22, [s], 'acc', 7.6) for k, s in enumerate(['delivered AS (filter orders)', 'city_rev AS (group delivered)', 'targets_m AS (this month’s targets)', 'final SELECT joins city_rev and targets_m'])) +
      cap('Same logic, read top to bottom.', '', 'green', y=160, h=34))
r3 = (t(180, 22, 'Step 2: test each CTE alone', 9.6, bold=True) + t(180, 56, 'WITH … SELECT COUNT(*) FROM delivered;', 8.6, 'ink', mono=True) + t(180, 76, 'WITH … SELECT * FROM city_rev;', 8.6, 'ink', mono=True) + cap('Find the wrong step, not the wrong line.', '', 'blue', y=160, h=34))
r4 = (t(180, 22, 'Step 3: compare with the old result', 9.6, bold=True) + t(180, 56, '(old EXCEPT new) and (new EXCEPT old) must be empty', 8.4, 'ink2') + cap('Set operations prove the refactor is safe.', '', 'green', y=160, h=34))
r5 = (t(180, 22, 'Reuse across statements?', 9.6, 'acc', bold=True) + t(180, 56, 'a CTE lives for one statement only', 8.6, 'ink2') + t(180, 76, 'for reuse: a view (Module 9) or a table', 8.6, 'ink2') + cap('Pick the right scope.', '', 'blue', y=160, h=34))
s1 = anim_one('Real-time scenario 1', 'Refactoring a nested report with CTEs',
              'Long nested queries are where bugs hide. Turn them into named, testable steps and prove nothing changed.',
              'Refactoring', 'A deeply nested query rewritten as CTEs, each step tested, and old and new results compared with EXCEPT', [r1, r2, r3, r4, r5],
              ['A report with four nested levels is hard to read and risky to change.',
               'Each level becomes a named CTE in reading order.',
               'Every CTE can be checked on its own.',
               'EXCEPT in both directions proves the old and new queries return the same rows.',
               'CTEs last for one statement; use views or tables to reuse logic across queries.'],
              hid='scenario-refactor')

# ---- scenario 2: NOT IN in production
n1 = (t(180, 22, 'Daily job: customers to send a “we miss you” coupon', 9.2, bold=True) + t(180, 56, 'WHERE customer_id NOT IN (SELECT customer_id FROM orders_last_30d)', 7.6, 'ink', mono=True) + cap('Worked for months: ~400 customers a day.', '(illustrative)', 'green', y=160, h=46))
n2 = (t(180, 22, 'Guest checkout launched', 9.6, bold=True) + t(180, 56, 'orders_last_30d now has customer_id NULL for guests', 8.4, 'ink2') + cap('The job suddenly selects 0 customers.', 'No error, no alert.', 'red', y=160, h=46))
n3 = (t(180, 22, 'Why: one NULL poisons NOT IN', 9.6, 'red', bold=True) + t(180, 56, 'x NOT IN (…, NULL) is NULL for every x', 8.6, 'ink', mono=True) + cap('Exactly what we reproduced in Step 3.', '', 'red', y=160, h=34))
n4 = (t(180, 22, 'Fix', 9.6, 'green', bold=True) + t(180, 52, 'WHERE NOT EXISTS (SELECT 1 FROM orders_last_30d o', 8, 'ink', mono=True) + t(180, 66, '                  WHERE o.customer_id = c.customer_id)', 8, 'ink', mono=True) + cap('Or add WHERE customer_id IS NOT NULL', 'inside the subquery.', 'green', y=160, h=46))
n5 = (t(180, 22, 'Guard', 9.6, 'acc', bold=True) + t(180, 56, 'alert when a daily count drops to 0 or falls by 90%', 8.4, 'ink2') + cap('Silent zeroes are the worst bugs.', '', 'blue', y=160, h=34))
s2 = anim_one('Real-time scenario 2', 'The coupon job that silently stopped',
              'A real-world shape of the NOT IN trap: nothing changed in the query, but the data started containing NULLs.',
              'NOT IN in production', 'A NOT IN subquery returns zero rows after guest orders introduce NULL customer ids; NOT EXISTS fixes it', [n1, n2, n3, n4, n5],
              ['A daily job finds customers without recent orders using NOT IN.',
               'Guest checkout adds orders with NULL customer_id.',
               'One NULL in the subquery makes NOT IN NULL for every customer: zero results.',
               'Rewrite with NOT EXISTS, or exclude NULLs inside the subquery.',
               'Alert on sudden drops in daily counts.'],
              hid='scenario-notin')

# ---- scenario 3: set operations for reconciliation
q1 = (t(180, 22, 'Two systems, two city lists', 9.6, bold=True) + label_box(20, 50, 140, 60, ['orders', '8 cities'], 'acc', 8.4) + label_box(200, 50, 140, 60, ['city_targets', '7 cities'], 'blue', 8.4) + cap('Which cities are in both, or only one?', '', 'blue', y=160, h=34))
q2 = (t(180, 22, 'INTERSECT (real)', 9.6, 'green', bold=True) + t(180, 56, 'Bengaluru, Delhi, Hyderabad, Mumbai, Pune, Thane', 8.2, 'ink', mono=True) + cap('6 cities in both lists.', '', 'green', y=160, h=34))
q3 = (t(180, 22, 'EXCEPT, both directions (real)', 9.6, bold=True) + t(180, 56, 'targets EXCEPT orders → Nashik', 8.6, 'ink', mono=True) + t(180, 76, 'orders MINUS targets → Chennai, Navi Mumbai', 8.6, 'ink', mono=True) + cap('Gaps on each side.', '', 'amber', y=160, h=34))
q4 = (t(180, 22, 'Same answers as joins (Lesson 3.3)', 9.6, bold=True) + t(180, 56, 'semi join ↔ INTERSECT · anti join ↔ EXCEPT', 8.6, 'ink2') + cap('Set operations compare whole rows; joins compare keys.', '', 'blue', y=160, h=34))
q5 = (t(180, 22, 'Distinct by default', 9.6, 'acc', bold=True) + t(180, 56, 'INTERSECT/EXCEPT remove duplicates; UNION ALL keeps them', 8.4, 'ink2') + cap('Pick ALL or DISTINCT on purpose.', '', 'green', y=160, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Reconciling lists with INTERSECT and EXCEPT',
              'Set operations are the quickest way to compare two lists. All results here are real.',
              'Set operations', 'INTERSECT and EXCEPT applied to cities with orders and cities with targets, matching the earlier join results', [q1, q2, q3, q4, q5],
              ['Orders know 8 cities, targets know 7.',
               'INTERSECT returns the 6 cities in both.',
               'EXCEPT and MINUS return what is missing on each side.',
               'They match the semi and anti joins from Lesson 3.3, but compare entire rows.',
               'INTERSECT and EXCEPT are distinct by default; UNION ALL keeps duplicates.'],
              hid='scenario-sets-ops')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>CTEs step by step, and the NOT IN trap</h2>
  <p>Left: real Beeline output. Right: how Hive evaluates the CTEs and the NOT IN condition.</p>
''' + two + '''
  <p>Three live scenarios follow: refactoring with CTEs, NOT IN in a production job, and set operations for reconciliation.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Subqueries and CTEs in real work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'WITH …', 10, 'green', bold=True, mono=True) + t(60, 58, 'readable steps', 7.4, 'ink2'),
    '1. Readable reporting SQL',
    'Analytics teams write reports as chains of CTEs (filter → aggregate → compare), which code reviewers can follow and test step by step.',
    ['Raw tables', '*CTE chain', 'Report']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'IN (…)', 10, 'blue', bold=True, mono=True) + t(60, 58, 'segment filter', 7.4, 'ink2'),
    '2. Segment filters',
    'Marketing defines segments (Gold customers, lapsed users) as subqueries; campaign queries filter orders or events with IN or EXISTS.',
    ['Segment', '*IN / EXISTS', 'Campaign list']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:#D64545"/>' + t(60, 42, 'NOT EXISTS', 8.6, 'red', bold=True, mono=True) + t(60, 58, 'safe anti join', 7.4, 'ink2'),
    '3. Missing-record checks',
    'Payments without orders, deliveries without payments: NOT EXISTS checks run daily and are robust to NULLs in the other table.',
    ['Two tables', '*NOT EXISTS', 'Exceptions']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'EXCEPT', 10, 'violet', bold=True, mono=True) + t(60, 58, 'regression test', 7.4, 'ink2'),
    '4. Testing query changes',
    'Before replacing a production query, teams run old EXCEPT new and new EXCEPT old; both must be empty for the change to ship.',
    ['Old vs new', '*EXCEPT ×2', 'Ship if empty']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'UNION ALL', 9, 'acc', bold=True, mono=True) + t(60, 58, 'combine sources', 7.4, 'ink2'),
    '5. Combining sources',
    'Orders from the app and from partner platforms land in separate tables; a UNION ALL view combines them with a source column for reports.',
    ['App + partners', '*UNION ALL', 'One order view']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> you need GROUP BY (<a href="../02-group-by-and-grouping-sets/">3.2</a>) and joins (<a href="../03-joins/">3.3</a>); the <code>city_targets</code> table comes from Lesson 3.3.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
