import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
BODY = body(HERE)
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep

META = dict(
    module='03-querying', lesson='01-select-where-and-functions', n='3.1',
    module_label='Module 3 · Querying with HiveQL',
    title='SELECT, WHERE and built-in functions',
    desc='HiveQL SELECT and WHERE with every family of built-in operators: relational (BETWEEN, LIKE, RLIKE, IS NULL, <=>, IS DISTINCT FROM), arithmetic (%, DIV, bitwise), logical (AND, OR, NOT, IN), string ||, plus CASE, IF, COALESCE, NVL, ROUND, FLOOR, CEIL, DISTINCT, LIMIT OFFSET, aliases, backticks, regex column selection and virtual columns. Real Hive 4.2.1 output.',
    og_desc='NULL = NULL is not true and ROUND(2.5) is 3: SELECT and WHERE in Hive, with every operator tested on real data.',
    minutes=32, level='Beginner → Intermediate',
    lead='SELECT and WHERE look like any SQL, but reports go wrong in the details: how NULL compares, how numbers round and divide, which pattern operators exist and in which order a query is evaluated. This lesson answers real TiffinGo questions with every operator family Hive offers, and shows Hive extras such as <code>RLIKE</code>, NULL-safe <code>&lt;=&gt;</code>, <code>LIMIT … OFFSET</code>, regex column lists and virtual columns. <b>All outputs are real</b>, from Hive 4.2.1.',
    chips=['Real Hive 4.2.1 outputs', 'All operator families', 'NULL and rounding traps', 'Runs in your browser (Python)'],
)

MAIN = '''# WHERE in Python: keep a row only when the condition is TRUE (None plays NULL)
orders = [(100226, "Pune", 520, "Card"), (100227, "Thane", 510, "UPI"),
          (100365, "Pune", 510, "UPI"), (100370, "Pune", 505, "COD"),
          (100380, "Pune", 700, "UPI"), (100999, None, 510, "UPI")]

def where(order_id, city, amount, payment):
    if city is None:
        return None                          # unknown: comparison with NULL
    return city == "Pune" and 500 <= amount <= 520 and payment in ("UPI", "Card")

for row in orders:
    result = where(*row)
    print(row[0], "->", {True: "kept", False: "dropped", None: "dropped (NULL)"}[result])
'''
RUN = dict(
    heading='Run the code: WHERE, NULL and functions in Python',
    intro='<p>Python imitates the rules you saw in the lab: WHERE keeps only rows whose condition is true, NULL comparisons are unknown, CASE checks branches in order, and Hive’s ROUND is half-up. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('return None                          # unknown: comparison with NULL', 'Any comparison with NULL is NULL (unknown). WHERE treats unknown like false.'),
        ('return city == "Pune" and 500 <= amount <= 520 and payment in ("UPI", "Card")', 'BETWEEN is inclusive (<code>&lt;=</code> on both sides); IN tests membership in a list.'),
    ],
    tasks=[
        dict(label='1 · Filter rows', hint='Press <b>Run</b>. Then change the range to 500–600 and predict which orders now pass.', code=None),
        dict(label='2 · CASE order matters', hint='<b>Predict first:</b> what label does 650 get? Then swap the first two branches and run again.',
             code='''def size_band(amount):
    if amount >= 600: return "large"        # CASE WHEN amount >= 600 THEN 'large'
    elif amount >= 300: return "medium"     # WHEN amount >= 300 THEN 'medium'
    else: return "small"                    # ELSE 'small'
for a in [650, 410, 120, 300]:
    print(a, size_band(a))
'''),
        dict(label='3 · Hive ROUND vs Python round', hint='Hive rounds halves away from zero. Compare with Python’s built-in for 0.5, 1.5, 2.5 and −2.5.',
             code='''from decimal import Decimal, ROUND_HALF_UP
def hive_round(x, d=0):
    q = Decimal(1).scaleb(-d)
    return float(Decimal(str(x)).quantize(q, rounding=ROUND_HALF_UP))
for x in [0.5, 1.5, 2.5, -2.5]:
    print(x, "hive:", hive_round(x), "python:", round(x))
'''),
        dict(label='4 · NULL-safe equality', hint='Write <code>&lt;=&gt;</code>: true when both are None, false when only one is. Check the four cases.',
             code='''def null_safe_eq(a, b):
    if a is None and b is None: return True
    if a is None or b is None: return False
    return a == b
for a, b in [(None, None), (1, None), (1, 1), (1, 2)]:
    print(a, b, "=", None if a is None or b is None else a == b, "| <=>", null_safe_eq(a, b))
'''),
        dict(label='5 · Spot the error', hint='The report should count orders that are not UPI, including those with unknown payment. The check fails because NULL rows are lost. Fix the condition.', expect='error',
             code='''payments = ["UPI", "Card", None, "COD", None, "UPI"]
def not_upi(p):
    return None if p is None else p != "UPI"     # like: WHERE payment <> 'UPI'
count = sum(1 for p in payments if not_upi(p) is True)
assert count == 4, f"counted {count}, expected 4 (2 non-UPI + 2 unknown)"
print(count)
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: build the table and try Hive extras',
    intro='<p>First create the curated <code>orders</code> table used throughout Module 3, then try two Hive extras. <b>Outputs are real</b>, from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · Build the curated orders table (once)', cmd="CREATE TABLE orders STORED AS ORC AS\nSELECT order_id, customer_id, restaurant_id, city, order_ts,\n       CAST(order_ts AS DATE) AS order_date,\n       CAST(amount AS DECIMAL(10,2)) AS amount, payment, status\nFROM orders_ext\nWHERE order_id IS NOT NULL AND amount IS NOT NULL AND order_ts IS NOT NULL;\nSELECT COUNT(*) FROM orders;", file='Beeline',
             output='+--------+\n|  _c0   |\n+--------+\n| 50000  |\n+--------+',
             note='The two dirty rows (amount “abc” and a date in the wrong layout) are left out, so 50,002 raw orders become 50,000 clean ones, typed and stored as ORC.'),
        dict(title='2 · Select columns by regular expression', cmd="SET hive.support.quoted.identifiers=none;\nSELECT `(order_ts|status|payment)?+.+` FROM orders LIMIT 2;", file='Beeline',
             output=open(CAP + 'l31_regexcol.txt').read().rstrip(),
             note='The pattern means “every column except order_ts, status and payment”. Handy for wide tables; set the property back to its default (<code>column</code>) afterwards, because backticks then stop meaning literal names.'),
        dict(title='3 · Standard NULL-safe comparison', cmd='SELECT 1 IS DISTINCT FROM NULL AS d, NULL IS NOT DISTINCT FROM NULL AS nd;', file='Beeline',
             output='+-------+-------+\n|   d   |  nd   |\n+-------+-------+\n| true  | true  |\n+-------+-------+',
             note='<code>IS [NOT] DISTINCT FROM</code> is the SQL-standard spelling of the NULL-safe comparison; Hive 4 supports both it and <code>&lt;=&gt;</code>.'),
    ],
)

TRACE = dict(
    heading='Evaluating a WHERE clause, one row at a time',
    intro='<p>Watch the three conditions being checked for each row and the result list growing only when all are true.</p>',
    code='''rows = [("Pune", 520, "Card"), ("Thane", 510, "UPI"), ("Pune", 505, "COD")]
kept = []
for city, amount, payment in rows:
    ok_city = city == "Pune"
    ok_amount = 500 <= amount <= 520
    ok_pay = payment in ("UPI", "Card")
    if ok_city and ok_amount and ok_pay:
        kept.append((city, amount, payment))
print(kept)
''',
    notes={4: 'Check :: Each condition is a true/false value for this row.', 7: 'AND :: All three must be true for the row to pass.'},
)

WORKED_INTRO = 'Three everyday SQL tasks at TiffinGo: segmenting orders with CASE, cleaning names with a pattern rule, and reconciling a report that loses NULL rows.'
EXAMPLES = [
    dict(level='b', tag='Reporting · CASE', title='Count orders per size band',
         problem='<p>Label each order small (&lt; 300), medium (300–599) or large (≥ 600) and count the bands. The Hive version is <code>SELECT CASE … END AS band, COUNT(*) FROM orders GROUP BY CASE … END</code>.</p>',
         inp='amounts: 530, 180, 720, 300, 90, 650',
         approach=['Write the CASE as a function with branches in order.', 'Count labels in a dictionary.', 'Print the bands.'],
         code='''amounts = [530, 180, 720, 300, 90, 650]
def band(a):
    if a >= 600: return "large"
    if a >= 300: return "medium"
    return "small"
counts = {}
for a in amounts:
    b = band(a)
    counts[b] = counts.get(b, 0) + 1
print(counts)
''', notes={9: 'Group :: Same as GROUP BY on the CASE expression.'},
         tryit='Move the medium test first. 720 and 650 become medium too: CASE stops at the first true branch.'),
    dict(level='i', tag='Data quality · patterns', title='Check customer names with a pattern rule',
         problem='<p>A rule says names are two words of letters, each starting with a capital. Find names that break it, as <code>WHERE NOT name RLIKE \'^[A-Z][a-z]+ [A-Z][a-z]+$\'</code> would.</p>',
         inp='Aarav Desai · riya sharma · Kabir  Khan · Diya Iyer · Meera D\'Souza · R2D2 Patil',
         approach=['Compile the regular expression.', 'fullmatch each name.', 'Print the names that fail.'],
         code='''import re
rule = re.compile(r"^[A-Z][a-z]+ [A-Z][a-z]+$")
names = ["Aarav Desai", "riya sharma", "Kabir  Khan", "Diya Iyer", "Meera D'Souza", "R2D2 Patil"]
for n in names:
    if not rule.fullmatch(n):
        print("breaks rule:", repr(n))
''', notes={5: 'Rule :: The same regex works in Hive RLIKE (Java syntax).'},
         tryit='Meera D\'Souza is a real name the rule wrongly rejects. Data rules must be checked with the business before they reject people’s names.'),
    dict(level='a', tag='Reconciliation · NULL', title='Make a split report add up',
         problem='<p>A report splits orders into UPI and non-UPI. With NULL payments, the parts do not add up to the total. Compute the three numbers both ways and show the fix with an explicit UNKNOWN group.</p>',
         inp='payments: UPI, Card, None, UPI, None',
         approach=['Count UPI with = and non-UPI with <>, skipping NULL like SQL.', 'Compare with the total.', 'Fix: label NULL as UNKNOWN (COALESCE) and group.'],
         code='''payments = ["UPI", "Card", None, "UPI", None]
upi = sum(1 for p in payments if p is not None and p == "UPI")
non_upi = sum(1 for p in payments if p is not None and p != "UPI")
print("total", len(payments), "| upi", upi, "| non-upi", non_upi, "| missing", len(payments) - upi - non_upi)
groups = {}
for p in payments:
    key = p if p is not None else "UNKNOWN"          # COALESCE(payment, 'UNKNOWN')
    groups[key] = groups.get(key, 0) + 1
print(groups, "sum =", sum(groups.values()))
''', notes={4: 'Gap :: 2 orders are in neither group.', 8: 'Fix :: Every row now lands in exactly one group.'},
         tryit='The Hive version: SELECT COALESCE(payment, \'UNKNOWN\'), COUNT(*) FROM orders GROUP BY COALESCE(payment, \'UNKNOWN\'). Add a check that the groups sum to COUNT(*).'),
]

QUIZ = mix([
    dict(q='Beginner: Which operator tests whether a value is missing?', options=['= NULL', 'IS NULL', '== NULL', 'NULL()'], answer=1,
         why='WHERE amount = NULL counted 0 rows in the lab; WHERE amount IS NULL found the 1 bad order.'),
    dict(q='Beginner: amount BETWEEN 500 AND 520 includes which values?', options=['501 to 519 only', '500 to 520, both ends included', '500 to 519', 'Only 500 and 520'], answer=1,
         why='BETWEEN is inclusive; order 100226 with 520.00 was returned.'),
    dict(q='Beginner: What does SELECT DISTINCT payment FROM orders return?', options=['Every row', 'Each payment value once', 'The number of payments', 'Only NULL payments'], answer=1,
         why='Four rows: COD, Card, UPI, Wallet.'),
    dict(q='Intermediate: What is the result of NULL <=> NULL in Hive?', options=['NULL', 'false', 'true', 'An error'], answer=2,
         why='<=> is NULL-safe equality: two NULLs are considered equal.'),
    dict(q='Intermediate: What does ROUND(2.5) return in Hive 4.2.1?', options=['2', '3', '2.5', '2.0'], answer=1,
         why='Hive rounds halves away from zero; Python round(2.5) returns 2.'),
    dict(q='Intermediate: Why does WHERE with_gst > 700 fail when with_gst is a SELECT alias?', options=['Aliases must be in capitals', 'WHERE is evaluated before SELECT, so the alias does not exist yet', 'Hive does not support aliases', 'with_gst is a reserved word'], answer=1,
         why='Error 10004. Repeat the expression in WHERE or use a subquery/CTE.'),
    dict(q='Advanced: Which operator matches a Java regular expression?', options=['LIKE', 'RLIKE', 'MATCH', 'GLOB'], answer=1,
         why="RLIKE (or REGEXP). LIKE supports only % and _ wildcards."),
    dict(q='Advanced: What do INPUT__FILE__NAME and BLOCK__OFFSET__INSIDE__FILE return?', options=['The table name and row count', 'The file a row was read from and the row’s byte position in it', 'The HDFS block size', 'The query id'], answer=1,
         why='The bad order was at byte 3,085,865 of orders.csv.'),
])

REVISION = [
    'Logical order: <b>FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT</b>; SELECT aliases are not visible in WHERE.',
    'WHERE keeps rows that are <b>TRUE</b>; false and NULL are dropped. <code>= NULL</code> never matches; use <code>IS [NOT] NULL</code>.',
    'Relational: <code>= &lt;&gt; != &lt; &gt; BETWEEN LIKE RLIKE/REGEXP IS NULL &lt;=&gt; IS [NOT] DISTINCT FROM</code>.',
    'Arithmetic: <code>+ - * /</code> (fraction), <code>DIV</code> (whole), <code>%</code>, bitwise <code>&amp; | ^ ~</code>. Logical: <code>AND OR NOT ! IN EXISTS</code>. String: <code>||</code>.',
    'Conditional: <code>CASE WHEN … END</code> (first true branch), <code>IF(c,a,b)</code>, <code>COALESCE</code>, <code>NVL</code>.',
    'Maths: <code>ROUND(x,d)</code> half-up (<code>ROUND(2.5)=3</code>, <code>ROUND(x,-2)</code> = hundreds), <code>FLOOR</code>, <code>CEIL</code>, <code>ABS</code>, <code>POW</code>, <code>SQRT</code>.',
    '<code>DISTINCT</code>, <code>LIMIT n OFFSET m</code> (with ORDER BY), backtick names, regex columns (<code>hive.support.quoted.identifiers=none</code>), <code>SELECT</code> without FROM.',
    'Virtual columns: <code>INPUT__FILE__NAME</code>, <code>BLOCK__OFFSET__INSIDE__FILE</code> (and <code>ROW__ID</code> for ACID).',
]
FAQ = [
    ('Why did my simple SELECT … WHERE … LIMIT finish instantly without a Tez job?', 'For simple queries (projections, filters and LIMIT, no aggregation or join) Hive can skip the Tez job and read the files directly in a “fetch task” (hive.fetch.task.conversion). Our EXPLAIN showed only Stage-0 with a Fetch Operator, a Limit and a Filter. Larger or more complex queries run as Tez DAGs.'),
    ('What is the difference between LIKE and RLIKE?', 'LIKE has two wildcards: % (any text) and _ (one character) and must match the whole value. RLIKE (also spelled REGEXP) takes a Java regular expression and matches if the pattern is found anywhere, so use ^ and $ to match the whole value. Prefer LIKE when it is enough: it is simpler and often faster.'),
    ('Why does WHERE col <> \'x\' not return rows where col is NULL?', 'Because NULL <> \'x\' is NULL (unknown), and WHERE keeps only TRUE. Add OR col IS NULL, or write NOT (col <=> \'x\'), when NULL rows should be included.'),
    ('Is IF() standard SQL?', 'No, IF(condition, a, b) is a Hive (and MySQL) function. CASE WHEN is standard and portable to Spark SQL, Trino and others, so many teams prefer CASE in shared code.'),
    ('Can I filter on a column alias from SELECT?', 'Not in the same query level, because WHERE is evaluated before SELECT. Repeat the expression in WHERE, or put the SELECT in a subquery or CTE and filter outside it. HAVING can use aggregates, and ORDER BY can use SELECT aliases because it is evaluated later.'),
]

PRACTICE_INTRO = 'Small programs that practise operators, NULL logic, rounding and conditional labels, with the matching HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Remainder and whole division', stmt='For 50,000 orders packed in boxes of 64, print full boxes and the leftover (Hive: DIV and %).', inp='50,000 and 64',
         code='''n, box = 50_000, 64
print("full boxes:", n // box, "| leftover:", n % box)
''', explain='781 full boxes and 16 left over. Hive: SELECT 50000 DIV 64, 50000 % 64.'),
    dict(level='easy', title='Inclusive range', stmt='Which of 499, 500, 510, 520, 521 pass amount BETWEEN 500 AND 520?', inp='499, 500, 510, 520, 521',
         code='''print([a for a in [499, 500, 510, 520, 521] if 500 <= a <= 520])
''', explain='[500, 510, 520]. Both ends are included.'),
    dict(level='easy', title='COALESCE', stmt='Return the first non-None value from (None, None, "Pune", "Thane").', inp='None, None, Pune, Thane',
         code='''def coalesce(*vals):
    return next((v for v in vals if v is not None), None)
print(coalesce(None, None, "Pune", "Thane"))
''', explain='Pune. COALESCE takes any number of arguments; NVL takes exactly two.'),
    dict(level='medium', title='LIKE as a function', stmt="Implement LIKE for patterns with % only, and test 'Riya%' and '%Mess' on a few names.", inp="Riya Gupta · Patil Mess · Riyaz Khan",
         code='''import re
def like(text, pattern):
    regex = "^" + ".*".join(re.escape(p) for p in pattern.split("%")) + "$"
    return re.match(regex, text) is not None
for n in ["Riya Gupta", "Patil Mess", "Riyaz Khan"]:
    print(n, like(n, "Riya%"), like(n, "%Mess"))
''', explain="'Riya%' also matches Riyaz Khan. Use 'Riya %' (with a space) if you mean the first name exactly."),
    dict(level='medium', title='Half-up rounding to 2 decimals', stmt='Round 2.345, 2.355 and 1234.5678 to 2 decimals the Hive way.', inp='2.345, 2.355, 1234.5678',
         code='''from decimal import Decimal, ROUND_HALF_UP
for x in ["2.345", "2.355", "1234.5678"]:
    print(x, Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
''', explain='2.35, 2.36, 1234.57. Using Decimal from text avoids binary errors that would make 2.345 round down.'),
    dict(level='medium', title='Bit flags', stmt='A restaurant flag uses bits: 1 = veg, 2 = jain, 4 = late-night. Flag 6 means which features? (Hive: flag & 2 > 0.)', inp='flag = 6',
         code='''flag = 6
for name, bit in [("veg", 1), ("jain", 2), ("late-night", 4)]:
    print(name, bool(flag & bit))
''', explain='jain and late-night. Bitwise & tests one bit; Hive supports & | ^ ~ on integers.'),
    dict(level='business', title='GST-inclusive filter', stmt='Find orders whose amount including 18% GST exceeds Rs 700. Write the Python filter, then the correct HiveQL (no alias in WHERE).', inp='530, 600, 610, 700',
         code='''amounts = [530, 600, 610, 700]
print([a for a in amounts if a * 1.18 > 700])
print("HiveQL: SELECT order_id, amount * 1.18 AS with_gst FROM orders WHERE amount * 1.18 > 700;")
''', explain='[600, 610, 700]. In Hive the expression is repeated in WHERE because the alias is not visible there.'),
    dict(level='business', title='Unknown payment share', stmt='Out of 50,000 orders, 412 have NULL payment after a faulty release. What share is that, and should the release be rolled back if the limit is 0.5%?', inp='412 of 50,000',
         code='''share = 412 / 50_000
print(f"{share:.2%} -> {'roll back' if share > 0.005 else 'within limit'}")
''', explain='0.82%, above the 0.5% limit. Hive: SELECT AVG(CASE WHEN payment IS NULL THEN 1 ELSE 0 END) FROM orders.'),
]

SCN_INTRO = 'SELECT and WHERE questions look easy; interviewers use them to test NULL logic and evaluation order.'
SCENARIOS = (
    scn('Any company · SQL basics', 'Fresher', '“Why does this query return no rows?”',
        'The interviewer shows: SELECT * FROM customers WHERE referral_code = NULL;',
        'do you know three-valued logic?',
        '''<ul>
          <li>Any comparison with NULL is NULL, and WHERE keeps only TRUE rows, so nothing is returned.</li>
          <li>Use <code>WHERE referral_code IS NULL</code>; for equality that should treat NULLs as equal use <code>&lt;=&gt;</code> or <code>IS NOT DISTINCT FROM</code>.</li>
        </ul>''', '“Hive has a bug with NULL”.') +
    scn('Analytics', 'Fresher', 'Using an alias in WHERE',
        'A candidate writes SELECT amount*1.18 AS gst_amt FROM orders WHERE gst_amt > 700 and gets error 10004.',
        'do you know the logical order of evaluation?',
        '''<ol>
          <li>WHERE runs before SELECT, so the alias does not exist yet.</li>
          <li>Repeat the expression in WHERE, or wrap: <code>SELECT * FROM (SELECT amount*1.18 AS gst_amt FROM orders) t WHERE gst_amt &gt; 700</code>.</li>
          <li>ORDER BY may use the alias because it runs after SELECT.</li>
        </ol>''', 'renaming the column in the table.') +
    scn('Finance · reconciliation', 'Mid-level', 'Totals differ from the finance system',
        'Hive and the finance team’s spreadsheet differ by a few rupees on a rounded GST total.',
        'can you reason about rounding and types?',
        '''<ul>
          <li>Check rounding rules: Hive ROUND is half-up; other tools may use half-even.</li>
          <li>Check where rounding happens: per line or on the total.</li>
          <li>Check types: DOUBLE amounts add binary errors; use DECIMAL.</li>
        </ul>''', '“it is just a small difference”: finance needs exact reconciliation.') +
    scn('Data engineering · debugging', 'Mid-level', 'One bad row in thousands of files',
        'A nightly job fails a quality check because one order has a NULL amount. The table has 3,000 files.',
        'do you know Hive’s virtual columns?',
        '''<ol>
          <li>Query <code>INPUT__FILE__NAME</code> and <code>BLOCK__OFFSET__INSIDE__FILE</code> for the bad row.</li>
          <li>Open the file at that offset to see the raw line.</li>
          <li>Report the file and line to the producer and add a check that quarantines such rows.</li>
        </ol>''', 'downloading and grepping every file.')
)
