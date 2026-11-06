import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()

# ---------------------------------------------------------------- story
sc = (box(10, 12, 210, 128, 'card') + t(115, 30, 'orders: 50,000 rows', 9, bold=True) + ''.join(fill(22 + (k % 12) * 16, 42 + (k // 12) * 14, 12, 10, 'acc' if k in (3, 17, 30, 44) else 'grey', rx=2) for k in range(60)) +
      t(115, 132, 'rows that pass WHERE are orange', 7.6, 'ink2') + arrow(224, 76, 262, 76, 'ink3', 2.2) +
      box(266, 26, 160, 100, 'blue') + t(346, 44, 'WHERE', 9, 'blue', bold=True, mono=True) + ''.join(t(276, 62 + k * 14, s, 7.6, anchor='start', mono=True) for k, s in enumerate(["city = 'Pune'", 'amount BETWEEN 500', '  AND 520', "payment IN ('UPI','Card')"])) +
      arrow(430, 76, 466, 76, 'ink3', 2.2) + box(470, 26, 160, 100, 'green') + t(550, 44, 'SELECT', 9, 'green', bold=True, mono=True) + ''.join(t(480, 62 + k * 14, s, 7.6, anchor='start', mono=True) for k, s in enumerate(['order_id, city,', 'amount, payment', 'ROUND, CASE, IF …', 'LIMIT 5'])))
scene_svg = scene('A table of fifty thousand orders is filtered by a WHERE clause on city, amount and payment, then the SELECT list picks and computes columns.', sc,
                  '<tspan font-weight="700" class="s-acc">WHERE</tspan> chooses rows, <tspan font-weight="700" class="s-acc">SELECT</tspan> chooses and computes columns.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Which Pune orders between Rs 500 and Rs 520 were paid online?”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s finance team asks Kabir small questions all day: orders in one city, in a price band, paid by UPI or card; customers whose name starts with Riya; amounts rounded for a report; a size label for each order. Kabir knows basic SQL, but Hive has surprises: <code>NULL = NULL</code> is not true, <code>ROUND(2.5)</code> is not what Python says, and his column alias “does not exist” in WHERE.</p>

{scene_svg}

K> Sir, SELECT and WHERE are the same as MySQL, no?
A> Ninety per cent the same. The ten per cent is where reports go wrong: how <b>NULL</b> compares, how numbers are <b>rounded</b> and <b>divided</b>, which <b>pattern</b> operators exist, and the order in which Hive evaluates a query. Today you will meet every operator family on real TiffinGo data.
R> And the functions? ROUND, CASE, IF?
A> Those too, plus a few Hive specials: <code>RLIKE</code> for regular expressions, <code>&lt;=&gt;</code> for NULL-safe comparison, <code>LIMIT … OFFSET</code>, virtual columns that tell you which file a row came from, and selecting columns by a regular expression.
  </div>
</section>
'''

lv = '''
LEVELS> SELECT and WHERE at three levels
L1> A filter and a form
      <ul>
        <li><b>WHERE</b> is a sieve: only rows that pass every condition go through.</li>
        <li><b>SELECT</b> is the form you fill for each passing row: which columns, and any calculated ones (a rounded amount, a label).</li>
        <li><b>LIMIT</b> says how many forms you want back.</li>
        <li><b>NULL</b> means “unknown”. Comparing anything with unknown gives unknown, so such rows do not pass WHERE.</li>
      </ul>
L2> The operator families
      <ul>
        <li><b>Relational:</b> <code>= == &lt;&gt; != &lt; &lt;= &gt; &gt;=</code>, <code>[NOT] BETWEEN a AND b</code>, <code>IS [NOT] NULL</code>, <code>[NOT] LIKE</code> (<code>%</code> any text, <code>_</code> one character), <code>RLIKE</code> / <code>REGEXP</code> (Java regular expressions), <code>&lt;=&gt;</code> (NULL-safe equal), <code>IS [NOT] DISTINCT FROM</code>.</li>
        <li><b>Arithmetic:</b> <code>+ - * /</code>, <code>%</code> (remainder), <code>DIV</code> (whole-number division), bitwise <code>&amp; | ^ ~</code>.</li>
        <li><b>Logical:</b> <code>AND OR NOT !</code>, <code>[NOT] IN (…)</code>, <code>[NOT] EXISTS (subquery)</code>.</li>
        <li><b>String:</b> <code>||</code> concatenates (same as <code>concat()</code>).</li>
        <li><b>Complex types:</b> <code>a[n]</code>, <code>m['key']</code>, <code>s.field</code> (Lesson 2.3).</li>
        <li><b>Conditional functions:</b> <code>CASE WHEN … THEN … END</code>, <code>IF(cond, a, b)</code>, <code>COALESCE(a, b, …)</code>, <code>NVL(a, b)</code>.</li>
        <li><b>Maths:</b> <code>ROUND(x, d)</code>, <code>FLOOR</code>, <code>CEIL</code>, <code>ABS</code>, <code>POW</code>, <code>SQRT</code>.</li>
      </ul>
L3> Rules and Hive-specific features
      <ul>
        <li><b>Evaluation order:</b> FROM → WHERE → (GROUP BY) → SELECT → ORDER BY → LIMIT. A SELECT alias cannot be used in WHERE (error 10004 in our lab).</li>
        <li><b>Three-valued logic:</b> <code>NULL = NULL</code> is NULL (not true); <code>NULL &lt;=&gt; NULL</code> is true. <code>NOT IN</code> with a NULL in the list returns no rows (Lesson 3.5).</li>
        <li><b>ROUND is half-up:</b> <code>ROUND(2.5)</code> = 3 in Hive; Python’s <code>round(2.5)</code> is 2 (banker’s rounding). <code>ROUND(x, -2)</code> rounds to hundreds.</li>
        <li><b>LIMIT n OFFSET m</b> (Hive 2.0+) skips m rows; use it only with ORDER BY, or the rows are arbitrary.</li>
        <li><b>Virtual columns:</b> <code>INPUT__FILE__NAME</code> and <code>BLOCK__OFFSET__INSIDE__FILE</code> show where a row was read from: great for debugging bad rows.</li>
        <li><b>Identifiers:</b> names are case-insensitive; backticks allow spaces and symbols (<code>`order id`</code>). With <code>hive.support.quoted.identifiers=none</code> a backticked name becomes a <b>regex column list</b>.</li>
        <li><b>FROM is optional:</b> <code>SELECT 1 + 1</code> works, handy for testing functions.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>SELECT, WHERE, operators and functions</h2>
''' + def_block(
    'A HiveQL <b>SELECT</b> statement retrieves rows from tables, views, joins or subqueries: <code>SELECT [ALL | DISTINCT] expr [AS alias], … FROM source [WHERE condition] [GROUP BY …] [HAVING …] [ORDER BY …] [LIMIT [offset,] n]</code>. The <b>WHERE</b> clause keeps only rows for which a Boolean expression is <b>true</b> (rows where it is false or NULL are discarded). Expressions are built from <b>built-in operators</b> (relational, arithmetic, logical, string and complex-type operators) and <b>built-in functions</b> (mathematical, conditional, string, date and others).',
    'SELECT picks columns and computes new ones; WHERE keeps only the rows where your condition is definitely true. Operators compare and calculate; functions like ROUND, CASE and IF transform values. Unknown values (NULL) never pass a normal comparison.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Predicate', 'A condition that is true, false or NULL for each row, such as <code>amount &gt; 500</code>.'),
    ('Three-valued logic', 'In SQL a condition can be true, false or unknown (NULL). WHERE keeps only true.'),
    ('NULL-safe equal', '<code>a &lt;=&gt; b</code>: true when both are NULL, false when only one is.'),
    ('RLIKE / REGEXP', 'Match a Java regular expression anywhere in the text (anchor with ^ and $ for a full match).'),
    ('DISTINCT', 'Removes duplicate rows from the result (ALL, the default, keeps them).'),
    ('Alias', 'A new name for an output column: <code>amount * 1.18 AS with_gst</code>.'),
    ('Virtual column', 'A column Hive adds itself, such as <code>INPUT__FILE__NAME</code>.'),
    ('Predicate pushdown', 'Hive applies WHERE as early as possible, ideally while reading files (Lesson 1.4).'),
]) + '''

  <h3>Operators and functions, tested on Hive 4.2.1</h3>
''' + table(['Expression', 'Result', 'Remember'], [
    ['<code>NULL = NULL</code>', '<code>NULL</code>', 'Never use = to test for NULL'],
    ['<code>NULL &lt;=&gt; NULL</code> · <code>1 &lt;=&gt; NULL</code>', '<code>true</code> · <code>false</code>', 'NULL-safe equality'],
    ['<code>1 IS DISTINCT FROM NULL</code>', '<code>true</code>', 'Standard SQL form of !&lt;=&gt;'],
    ['<code>17 % 5</code> · <code>17 DIV 5</code>', '<code>2</code> · <code>3</code>', 'Remainder and whole-number division'],
    ['<code>6 &amp; 3</code> · <code>6 | 3</code> · <code>6 ^ 3</code>', '<code>2</code> · <code>7</code> · <code>5</code>', 'Bitwise AND, OR, XOR (flags)'],
    ["<code>'Kharghar' || '-' || 'Navi Mumbai'</code>", '<code>Kharghar-Navi Mumbai</code>', 'String concatenation'],
    ['<code>ROUND(1234.5678, 2)</code> · <code>ROUND(1234.5678, -2)</code>', '<code>1234.57</code> · <code>1200</code>', 'Negative digits round left of the point'],
    ['<code>ROUND(2.5)</code>', '<code>3</code>', 'Half-up (Python gives 2)'],
    ['<code>FLOOR(-2.5)</code> · <code>CEIL(-2.5)</code>', '<code>-3</code> · <code>-2</code>', 'Floor goes down, ceil goes up, even for negatives'],
    ['<code>POW(2, 10)</code> · <code>SQRT(144)</code>', '<code>1024.0</code> · <code>12.0</code>', 'Return DOUBLE'],
], minw=640) + lv + '''
EXAM> “Explain the categories of built-in operators in Hive with examples.” Write four groups with two examples each: relational (<code>=</code>, <code>BETWEEN</code>, <code>LIKE</code>, <code>RLIKE</code>, <code>IS NULL</code>), arithmetic (<code>+</code>, <code>%</code>, <code>DIV</code>), logical (<code>AND</code>, <code>OR</code>, <code>NOT</code>, <code>IN</code>), and complex-type operators (<code>a[n]</code>, <code>m[k]</code>, <code>s.x</code>). Mention that comparisons with NULL return NULL.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Ways to filter, and which to choose</h2>
''' + table(['You want', 'Write', 'Avoid'], [
    ['One of a few values', "<code>payment IN ('UPI','Card')</code>", "Long chains of <code>OR payment = …</code>"],
    ['A range', '<code>amount BETWEEN 500 AND 520</code> (both ends included)', 'Forgetting BETWEEN is inclusive'],
    ['Starts with / contains', "<code>name LIKE 'Riya%'</code>, <code>LIKE '%Mess%'</code>", 'RLIKE when LIKE is enough'],
    ['A real pattern', "<code>name RLIKE '^(Aarav|Diya) (Patil|Iyer)$'</code>", 'Unanchored regex when you need a full match'],
    ['Missing values', '<code>col IS NULL</code> / <code>IS NOT NULL</code>', '<code>col = NULL</code> (always NULL)'],
    ['Equal, treating NULL as a value', '<code>a &lt;=&gt; b</code> or <code>a IS NOT DISTINCT FROM b</code>', '<code>a = b</code> when both may be NULL'],
    ['Filter on a calculated value', 'Repeat the expression in WHERE, or use a subquery/CTE', 'A SELECT alias in WHERE (error 10004)'],
], minw=680) + cards([
    ('CASE', 'Many branches: <code>CASE WHEN amount &gt;= 600 THEN \'large\' WHEN … ELSE \'small\' END</code>. Checked top to bottom.', 'Labels'),
    ('IF', '<code>IF(payment = \'COD\', \'cash\', \'digital\')</code>. Shorter for two branches; Hive-specific.', 'Two-way'),
    ('COALESCE / NVL', 'First non-NULL value: <code>COALESCE(nickname, name, \'unknown\')</code>; NVL takes exactly two.', 'Defaults'),
    ('DISTINCT', '<code>SELECT DISTINCT payment</code> or <code>COUNT(DISTINCT city)</code>. Needs a shuffle on big data.', 'Unique values'),
]) + '''
TIP> When a query returns fewer rows than expected, look for NULLs first: a NULL in a filtered column silently removes the row. Count them with <code>SUM(CASE WHEN col IS NULL THEN 1 ELSE 0 END)</code>.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Answer finance’s questions, one operator family at a time</h2>
  <p>All outputs are real, from the Hive 4.2.1 lab, on the curated <code>orders</code> table (50,000 clean orders in ORC).</p>
''' + stepper([
    ('Step 1 · Combine relational and logical operators',
     code('sql', 'Beeline', "SELECT order_id, city, amount, payment FROM orders\nWHERE city = 'Pune' AND amount BETWEEN 500 AND 520\n  AND payment IN ('UPI','Card')\nLIMIT 5;", capf('l31_a.txt').split('+-----------+---------+-----------+')[0].rstrip()),
     'Three conditions joined with AND; BETWEEN includes both ends (520.00 appears). Without ORDER BY, which five rows you get is not guaranteed.'),
    ('Step 2 · Unique values',
     code('sql', 'Beeline', "SELECT COUNT(*) AS all_rows, COUNT(DISTINCT city) AS cities,\n       COUNT(DISTINCT payment) AS payments FROM orders;\nSELECT DISTINCT payment FROM orders;",
          '+-----------+---------+-----------+\n| all_rows  | cities  | payments  |\n+-----------+---------+-----------+\n| 50000     | 8       | 4         |\n+-----------+---------+-----------+\n+----------+\n| payment  |\n+----------+\n| COD      |\n| Card     |\n| UPI      |\n| Wallet   |\n+----------+'),
     '50,000 orders, 8 cities, 4 payment modes. DISTINCT needs a shuffle so equal values meet in one reducer.'),
    ('Step 3 · Patterns: LIKE and RLIKE',
     code('sql', 'Beeline', "SELECT name, city FROM customers WHERE name LIKE 'Riya%' LIMIT 3;\nSELECT name FROM customers WHERE name RLIKE '^(Aarav|Diya) (Patil|Iyer)$' LIMIT 4;",
          '+-----------------+------------+\n|      name       |    city    |\n+-----------------+------------+\n| Riya Fernandes  | Pune       |\n| Riya Gupta      | Bengaluru  |\n| Riya Sharma     | Bengaluru  |\n+-----------------+------------+\n+--------------+\n|     name     |\n+--------------+\n| Diya Iyer    |\n| Aarav Patil  |\n| Diya Iyer    |\n| Diya Patil   |\n+--------------+'),
     'LIKE has two wildcards (<code>%</code>, <code>_</code>). RLIKE takes a full regular expression; <code>^</code> and <code>$</code> force the whole name to match. Two customers are called Diya Iyer: names are not unique, ids are.'),
    ('Step 4 · NULL, arithmetic, bitwise and maths',
     code('sql', 'Beeline', "SELECT NULL = NULL AS eq, NULL <=> NULL AS nullsafe, 1 <=> NULL AS one_ns,\n       17 % 5 AS modulo, 17 DIV 5 AS idiv, 6 & 3 AS band, 6 | 3 AS bor, 6 ^ 3 AS bxor,\n       'Kharghar' || '-' || 'Navi Mumbai' AS concat_op,\n       ROUND(1234.5678, 2) AS r2, ROUND(1234.5678, -2) AS rneg,\n       FLOOR(-2.5) AS fl, CEIL(-2.5) AS ce, ROUND(2.5) AS r_half;",
          '| eq   | nullsafe | one_ns | modulo | idiv | band | bor | bxor | concat_op            | r2      | rneg | fl | ce | r_half |\n| NULL | true     | false  | 2      | 3    | 2    | 7   | 5    | Kharghar-Navi Mumbai | 1234.57 | 1200 | -3 | -2 | 3      |\n(borders removed to fit)'),
     'No FROM is needed to test expressions. Note the two traps: <code>NULL = NULL</code> is NULL, and <code>ROUND(2.5)</code> is 3 (half-up), unlike Python.'),
    ('Step 5 · CASE, IF, COALESCE and NVL',
     code('sql', 'Beeline', "SELECT order_id, amount,\n  CASE WHEN amount >= 600 THEN 'large' WHEN amount >= 300 THEN 'medium' ELSE 'small' END AS size_band,\n  IF(payment = 'COD', 'cash', 'digital') AS pay_type,\n  COALESCE(NULL, payment) AS c, NVL(NULL, 'x') AS n\nFROM orders LIMIT 3;", capf('l31_b.txt').split('+----------+')[0].rstrip()),
     'CASE checks branches in order and takes the first true one, so put the strictest condition first. IF is Hive shorthand for a two-branch CASE.'),
    ('Step 6 · Aliases, LIMIT … OFFSET and quoted names',
     code('sql', 'Beeline', "SELECT order_id, amount FROM orders ORDER BY order_id LIMIT 2 OFFSET 3;\nSELECT order_id, amount * 1.18 AS with_gst FROM orders WHERE with_gst > 700 LIMIT 2;\nSELECT order_id AS `order id`, city AS `delivery-city` FROM orders LIMIT 2;",
          capf('l31_limit_alias.txt').split(': (possible')[0] + ' …\n+-----------+----------------+\n| order id  | delivery-city  |\n+-----------+----------------+\n| 100001    | Mumbai         |\n| 100002    | Mumbai         |\n+-----------+----------------+'),
     'OFFSET 3 skipped orders 100001–100003. The alias <code>with_gst</code> does not exist yet when WHERE runs (WHERE is evaluated before SELECT); repeat the expression or wrap the query in a subquery. Backticks allow spaces and hyphens in names.'),
    ('Step 7 · Where did this row come from?',
     code('sql', 'Beeline', 'SELECT order_id, INPUT__FILE__NAME AS file, BLOCK__OFFSET__INSIDE__FILE AS offset_\nFROM orders_ext LIMIT 2;', '+-----------+--------------------------------------------+----------+\n| order_id  |                    file                    | offset_  |\n+-----------+--------------------------------------------+----------+\n| 100001    | file:/data/tiffingo/orders_ext/orders.csv  | 0        |\n| 100002    | file:/data/tiffingo/orders_ext/orders.csv  | 61       |\n+-----------+--------------------------------------------+----------+'),
     'Virtual columns give the file and the byte position of each row: the first line is 61 bytes long, so line 2 starts at byte 61. When a bad row appears among thousands of files, this tells you exactly which file to open.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
ROWS = [('100226', 'Pune', '520', 'Card'), ('100227', 'Thane', '510', 'UPI'), ('100365', 'Pune', '510', 'UPI'), ('100370', 'Pune', '505', 'COD'), ('100380', 'Pune', '700', 'UPI'), ('100386', 'Pune', '510', 'UPI')]
def grid(marks, note=''):
    o = ''
    for k, (oid, city, amt, pay) in enumerate(ROWS):
        m = marks[k]
        tone = {'p': 'green', 'x': 'red', '?': 'card'}[m]
        o += box(14, 40 + k * 22, 236, 18, tone) + t(20, 53 + k * 22, f'{oid}  {city:6} {amt:>4}  {pay}', 7.8, 'ink', anchor='start', mono=True)
        o += t(262, 53 + k * 22, {'p': 'pass', 'x': 'drop', '?': ''}[m], 7.8, 'green' if m == 'p' else 'red', anchor='start', bold=True)
    if note:
        o += t(180, 186, note, 8, 'ink2')
    return o
see = [
    term([("> SELECT order_id, city, amount, payment", W), ("  FROM orders", W), ("  WHERE city = 'Pune'", W), ("    AND amount BETWEEN 500 AND 520", W), ("    AND payment IN ('UPI','Card')", W), ('  LIMIT 5;', W)]),
    term([('> EXPLAIN SELECT … (same query);', W), ('Plan optimized by CBO.', G), ('Stage-0  Fetch Operator  limit:5', G), ('  Limit [LIM_3]  Number of rows:5', G), ('    Filter Operator [FIL_5]', G), ('      predicate:(amount BETWEEN 500 AND 520', G), ("        and (city = 'Pune') and (payment)", G), ("        IN ('Card', 'UPI'))", G), ('      TableScan [TS_0]', G)], size=7.6, step=13),
    term([('| 100226 | Pune | 520.00 | Card |', G), ('| 100365 | Pune | 510.00 | UPI  |', G), ('| 100386 | Pune | 510.00 | UPI  |', G), ('| 100416 | Pune | 510.00 | UPI  |', G), ('| 101410 | Pune | 520.00 | UPI  |', G), ('5 rows selected', Y)]),
    term([('> SELECT NULL = NULL, NULL <=> NULL;', W), ('| NULL | true |', Y), ('> SELECT COUNT(*) FROM orders_ext', W), ('  WHERE amount = NULL;', W), ('| 0 |', RD), ('> … WHERE amount IS NULL;', W), ('| 1 |', G)]),
    term([('> SELECT order_id, amount * 1.18 AS with_gst', W), ('  FROM orders WHERE with_gst > 700;', W), ('Error: … [Error 10004]: Invalid table', RD), ("  alias or column reference 'with_gst'", RD)]),
    term([("> SELECT ROUND(2.5), FLOOR(-2.5), CEIL(-2.5);", W), ('| 3 | -3 | -2 |', G), ('', W), ('>>> round(2.5)    # Python', W), ('2', Y)]),
]
B1 = [
    t(180, 22, 'Six sample rows reach WHERE', 9.4, bold=True) + grid(['?'] * 6, 'Every condition is checked for every row'),
    t(180, 22, 'All three conditions must be true', 9.4, bold=True) + grid(['p', 'x', 'p', 'x', 'x', 'p'], 'Thane: city fails · 505 COD: payment fails · 700: range fails'),
    t(180, 22, 'Passing rows → SELECT list → LIMIT', 9.4, bold=True) + grid(['p', 'x', 'p', 'x', 'x', 'p']) + box(14, 176, 330, 22, 'green') + t(180, 191, '4 columns kept · stop after 5 rows', 8.4, bold=True),
    (t(180, 22, 'Three-valued logic', 9.4, bold=True) + ''.join(label_box(14 + k * 112, 44, 104, 50, [a, b], tone, 8.2) for k, (a, b, tone) in enumerate([('city = \'Pune\'', 'true → kept', 'green'), ('city = \'Thane\'', 'false → dropped', 'red'), ('city = NULL', 'NULL → dropped', 'amber')])) +
    t(180, 122, 'WHERE keeps only TRUE. NULL is not true.', 8.6, 'ink2') + cap('Test missing values with IS NULL or &lt;=&gt;.', '', 'blue', y=170, h=34)),
    t(180, 22, 'Logical order of a query', 9.4, bold=True) + ''.join(chip(14 + k * 56, 50, nm, 'acc' if nm in ('WHERE', 'SELECT') else 'grey', w=52, h=22, size=7.6) for k, nm in enumerate(['FROM', 'WHERE', 'GROUP', 'SELECT', 'ORDER', 'LIMIT'])) +
    t(180, 96, 'with_gst is created in SELECT (step 4),', 8.4, 'ink2') + t(180, 112, 'but WHERE (step 2) has already run', 8.4, 'red', bold=True) + cap('Repeat the expression, or use a subquery.', '', 'blue', y=170, h=34),
    t(180, 22, 'Rounding rules differ', 9.4, bold=True) + label_box(14, 44, 160, 60, ['Hive ROUND(2.5)', '3  (half away from zero)'], 'green', 8.2) + label_box(186, 44, 160, 60, ['Python round(2.5)', '2  (half to even)'], 'amber', 8.2) +
    t(180, 126, 'FLOOR always goes down, CEIL always up: FLOOR(-2.5) = -3', 8.2, 'ink2') + cap('Match rounding rules when you reconcile reports.', '', 'blue', y=170, h=34),
]
see_caps = ['Kabir writes finance’s question as one SELECT with three conditions.',
            'EXPLAIN shows one Filter right after the TableScan, and no Tez job at all: a simple filter with LIMIT runs as a fetch task.',
            'Five matching Pune orders come back, the first five Hive finds.',
            'NULL = NULL is NULL, so WHERE amount = NULL counts 0 rows; IS NULL finds the 1 bad order.',
            'Using a SELECT alias in WHERE fails with error 10004.',
            'Hive rounds 2.5 up to 3; Python rounds it to 2.']
behind_caps = ['Each row is tested against every condition.',
               'A row passes only if all ANDed conditions are true. One false condition drops it.',
               'Passing rows keep only the selected columns, and Hive stops once 5 rows are found.',
               'WHERE keeps rows whose condition is TRUE; false and NULL are both dropped.',
               'SELECT is evaluated after WHERE, so its aliases are not yet known when WHERE runs.',
               'Hive’s ROUND rounds halves away from zero; Python uses banker’s rounding to the even number.']
two = anim_two('SELECT and WHERE', 'From question to five rows', 'Real Beeline output', 'What happens to each row', see, B1, see_caps, behind_caps)

# ---- scenario 1: NULLs disappear from a report
z1 = (t(180, 22, '“Orders not paid by UPI”', 9.6, bold=True) + t(180, 54, "WHERE payment &lt;&gt; 'UPI'", 9, 'ink', mono=True) + bars([('UPI', 60, 'blue', '30,011'), ('others', 40, 'green', '19,989'), ('NULL', 4, 'amber', '?')], y=72) +
      cap('Some new orders have payment = NULL (app bug).', '', 'amber', y=160, h=34))
z2 = (t(180, 22, 'NULL rows vanish from both sides', 9.6, 'red', bold=True) + t(180, 54, "payment = 'UPI'  → NULL → dropped", 8.4, 'ink', mono=True) + t(180, 72, "payment &lt;&gt; 'UPI' → NULL → dropped", 8.4, 'ink', mono=True) +
      cap('UPI + non-UPI ≠ total orders.', 'Finance spots the gap.', 'red', y=150, h=46))
z3 = (t(180, 22, 'Make NULL explicit', 9.6, 'green', bold=True) + t(180, 56, "WHERE payment &lt;&gt; 'UPI' OR payment IS NULL", 8.6, 'ink', mono=True) + t(180, 76, "or: WHERE NOT (payment &lt;=&gt; 'UPI')", 8.6, 'ink', mono=True) +
      cap('Now the counts add up.', '', 'green', y=150, h=34))
z4 = (t(180, 22, 'Label unknowns in reports', 9.6, bold=True) + t(180, 56, "COALESCE(payment, 'UNKNOWN') AS payment", 8.6, 'ink', mono=True) + cap('A visible UNKNOWN row is better than a silent gap.', '', 'green', y=150, h=34))
z5 = (t(180, 22, 'Reconcile every report', 9.6, 'acc', bold=True) + t(180, 56, 'sum of groups = COUNT(*) of the table?', 8.6, 'ink2') + cap('If not, look for NULLs first.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Where did those orders go? NULLs in filters',
              'A classic reporting bug. Our curated table has no NULL payments; imagine an app release that sends some. (Counts illustrative.)',
              'NULL in filters', 'Orders with NULL payment disappear from both the UPI and the non-UPI report until NULL is handled explicitly', [z1, z2, z3, z4, z5],
              ['Finance asks for orders not paid by UPI. A bug sends some orders with no payment value.',
               'Comparisons with NULL are NULL, so those orders appear in neither report.',
               'Add OR payment IS NULL, or use the NULL-safe operator.',
               'In reports, turn NULL into a visible UNKNOWN label with COALESCE.',
               'Always check that the parts add up to the total.'],
              hid='scenario-nulls')

# ---- scenario 2: rounding reconciliation
q1 = (t(180, 22, 'GST report: Hive vs a Python check', 9.6, bold=True) + t(180, 54, 'amount × 5% GST, rounded to rupees', 8.6, 'ink2') + bars([('Hive', 100, 'green', 'Rs 1,24,503'), ('Python', 99.99, 'amber', 'Rs 1,24,497')], y=72) +
      cap('A difference of a few rupees.', 'Auditors want it explained.', 'amber', y=150, h=46))
q2 = (t(180, 22, 'The cause: halves', 9.6, bold=True) + t(180, 54, 'tax = 12.5 → Hive ROUND gives 13, Python round gives 12', 8.2, 'ink', mono=True) + cap('Different tie-breaking rules.', '', 'red', y=150, h=34))
q3 = (t(180, 22, 'Fix: one rounding rule everywhere', 9.6, 'green', bold=True) + t(180, 56, "Python: Decimal(x).quantize(Decimal('1'), ROUND_HALF_UP)", 7.8, 'ink', mono=True) + t(180, 74, 'Hive: ROUND(x) (already half-up)', 7.8, 'ink', mono=True) + cap('Now both systems agree.', '', 'green', y=150, h=34))
q4 = (t(180, 22, 'Round once, at the right level', 9.6, bold=True) + t(180, 56, 'per line, then sum ≠ sum, then round', 8.6, 'ink2') + cap('Agree with finance which one the law requires.', '', 'blue', y=150, h=34))
q5 = (t(180, 22, 'Use DECIMAL for money', 9.6, 'acc', bold=True) + t(180, 56, 'ROUND on DOUBLE can also be off by binary fractions', 8.4, 'ink2') + cap('DECIMAL + one rounding rule = reproducible totals.', '', 'green', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'A rounding difference in a tax report',
              'Two systems, two rounding rules. (Amounts illustrative; the ROUND(2.5) behaviour is real.)',
              'Rounding', 'Hive and Python round halves differently, producing a small total difference until one rule is used', [q1, q2, q3, q4, q5],
              ['A GST total from Hive differs from a Python cross-check by a few rupees.',
               'Hive rounds halves up; Python rounds halves to the even number.',
               'Use the same half-up rule in both systems.',
               'Decide whether to round each line or the total; the results differ.',
               'Store money as DECIMAL to avoid binary fraction errors too.'],
              hid='scenario-rounding')

# ---- scenario 3: debugging with virtual columns
v1 = (t(180, 22, 'A bad row among 3,000 files', 9.6, bold=True) + t(180, 56, "SELECT * FROM events WHERE amount IS NULL;  -- 1 row", 8, 'ink', mono=True) + cap('Which file is it in?', '', 'amber', y=150, h=34))
v2 = (t(180, 22, 'Ask the virtual columns', 9.6, bold=True) + t(180, 52, 'SELECT INPUT__FILE__NAME,', 8.4, 'ink', mono=True) + t(180, 68, '       BLOCK__OFFSET__INSIDE__FILE', 8.4, 'ink', mono=True) + t(180, 84, 'FROM orders_ext WHERE amount IS NULL;', 8.4, 'ink', mono=True) + cap('File path and byte offset of the row.', '', 'blue', y=150, h=34))
v3 = term([('> SELECT INPUT__FILE__NAME,', W), ('    BLOCK__OFFSET__INSIDE__FILE', W), ('  FROM orders_ext WHERE amount IS NULL;', W), ('| file:/data/tiffingo/orders_ext/', G), ('|   orders.csv | 3085865 |', G), ('$ tail -c +3085866 orders.csv | head -1', W), ('150001,17,3,Pune,2026-10-31 21:15:00,', RD), ('  abc,UPI,DELIVERED', RD)], size=7.6, step=13)
v4 = (t(180, 22, 'Fix at the source', 9.6, 'green', bold=True) + t(180, 56, 'amount “abc” came from a test order', 8.6, 'ink2') + cap('Send the file name and line to the producer.', '', 'green', y=150, h=34))
v5 = (t(180, 22, 'Other virtual columns', 9.6, 'acc', bold=True) + t(26, 52, 'ROW__ID (ACID tables: write id, bucket, row id)', 8.2, 'ink', anchor='start', mono=True) + t(26, 70, 'INPUT__FILE__NAME · BLOCK__OFFSET__INSIDE__FILE', 8.2, 'ink', anchor='start', mono=True) +
      cap('Names have two underscores on each side.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Finding a bad row with virtual columns',
              'When a query shows one strange row, find its file and position in seconds.',
              'Virtual columns', 'Using INPUT__FILE__NAME and BLOCK__OFFSET__INSIDE__FILE to locate the source line of a bad row', [v1, v2, v3, v4, v5],
              ['One row in a large external table has a NULL amount.',
               'INPUT__FILE__NAME and BLOCK__OFFSET__INSIDE__FILE return its file and byte offset.',
               'Jump to byte 3,085,865 of the file and the raw line appears: amount “abc”.',
               'Report the exact file and line to the data producer.',
               'ACID tables also expose ROW__ID.'],
              hid='scenario-virtual')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>A filter, row by row</h2>
  <p>Left: Beeline. Right: what happens to six sample orders as the query runs.</p>
''' + two + '''
  <p>Three live scenarios follow: NULLs in filters, a rounding mismatch and debugging with virtual columns.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>SELECT and WHERE in daily work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'WHERE …', 9, 'blue', bold=True, mono=True) + t(60, 58, 'ad-hoc question', 7.4, 'ink2'),
    '1. Ad-hoc questions from business teams',
    'Operations asks for “Pune COD orders above Rs 500 yesterday”. A WHERE with IN, BETWEEN and a date filter answers it in one query.',
    ['Question', '*SELECT … WHERE', 'Answer']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'CASE', 10, 'acc', bold=True, mono=True) + t(60, 58, 'segments', 7.4, 'ink2'),
    '2. Business labels',
    'CASE turns numbers into segments: small/medium/large baskets, new/returning customers, on-time/late deliveries. Dashboards group by these labels.',
    ['Amounts', '*CASE WHEN', 'Segments']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'RLIKE', 10, 'violet', bold=True, mono=True) + t(60, 58, 'pattern checks', 7.4, 'ink2'),
    '3. Data quality checks',
    'RLIKE finds malformed values: phone numbers that are not 10 digits, PIN codes with letters, emails without @. The result feeds a quality dashboard.',
    ['Raw table', '*RLIKE rules', 'Bad-value report']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, '&lt;=&gt;', 11, 'green', bold=True, mono=True) + t(60, 58, 'change detection', 7.4, 'ink2'),
    '4. Finding changed rows',
    'Comparing yesterday’s and today’s copies of a table, <code>NOT (a.col &lt;=&gt; b.col)</code> correctly treats NULL-to-NULL as unchanged and value-to-NULL as a change.',
    ['Two snapshots', '*NULL-safe compare', 'Changed rows']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'FILE__NAME', 8.4, 'acc', bold=True, mono=True) + t(60, 58, 'debugging', 7.4, 'ink2'),
    '5. Tracing bad data to its file',
    'Support engineers add INPUT__FILE__NAME to a query to find which upload brought a broken row, then ask that source to resend.',
    ['Bad row', '*Virtual column', 'Source file']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> the queries use the curated <code>orders</code> table (ORC, 50,000 rows) built with CTAS from <code>orders_ext</code>, as in <a href="../../02-hiveql/05-loading-data/">Lesson 2.5</a>. The CTAS is shown in “Run on your PC”.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
