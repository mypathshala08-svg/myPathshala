import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='04-dataframes', lesson='03-working-with-columns', n='4.3',
    module_label='Module 4 · DataFrames',
    title='Working with columns',
    desc='Selecting, adding, renaming, casting and filtering columns in PySpark 4.3.0 on TiffinGo orders: four ways to name a column, select and selectExpr, an ANSI cast that fails on one "abc" while try_cast returns null, withColumn and withColumns, when/otherwise and the null that falls into otherwise, filter traps (missing brackets, Python and) and a typo caught at analysis, plus 300 columns added in 6.87 s with a withColumn loop versus 0.98 s with withColumns.',
    og_desc='Adding 300 columns: 6.87 s with a withColumn loop, 0.98 s with one withColumns call. Working with columns in PySpark, measured.',
    minutes=32, level='Beginner → Intermediate',
    lead='Most DataFrame code is column work: choosing columns, computing new ones, fixing types and filtering rows. This lesson covers the column API, Spark 4’s <b>ANSI casts</b>, the classic filter mistakes, and why a <code>withColumn</code> loop is slow. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', 'ANSI cast vs try_cast', 'withColumn loop timed', 'Runs in your browser (Python)'],
)

MAIN = '''# when / otherwise as plain Python: note what happens to None
def slot(hour):
    if hour is not None and hour < 11:
        return "breakfast"
    if hour is not None and hour < 16:
        return "lunch"
    if hour is not None and hour < 22:
        return "dinner"
    return "late-night"            # otherwise(): also catches None!

hours = [8, 13, 20, 23, None]
for h in hours:
    print(h, "->", slot(h))
'''
RUN = dict(
    heading='Run the code: when / otherwise and nulls',
    intro='<p>A model of Step 4. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    return "late-night"            # otherwise(): also catches None!', 'A null comparison is not true, so Spark falls through to otherwise too.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then add a first check that returns "unknown" for None.', code=None),
        dict(label='2 · Predict first: try_cast', hint='<b>Predict first:</b> sum and count after try_cast of these strings.',
             code='''vals = ["530", "500", "abc", "410"]
nums = [int(v) if v.isdigit() else None for v in vals]
ok = [n for n in nums if n is not None]
print("sum", sum(ok), "count", len(ok), "rows", len(vals))
'''),
        dict(label='3 · Operator precedence', hint='Why brackets matter: & binds tighter than ==.',
             code='''city, amount = "Pune", 600
print((city == "Pune") & (amount > 500))
'''),
        dict(label='4 · Build columns in one go', hint='Create a dict of 5 feature expressions, as for withColumns.',
             code='''features = {f"amount_x{k}": f"amount * {k}" for k in range(1, 6)}
print(features)
'''),
        dict(label='5 · Spot the error', hint='This filter uses Python and.', expect='error',
             code='''code = "df.where((col('city') == 'Pune') and (col('amount') > 500))"
assert " and " not in code, "use & with brackets: (a) & (b); Python and raises CANNOT_CONVERT_COLUMN_INTO_BOOL"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: columns',
    intro='<p>In the <code>pyspark</code> shell with the orders DataFrame. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · ANSI mode', cmd='spark.conf.get("spark.sql.ansi.enabled")', file='pyspark',
             output="'true'", note='Default since Spark 4.0.'),
        dict(title='2 · try_cast', cmd='o.select(F.col("amount").try_cast("int").alias("amt")).agg(F.count("amt"), F.count("*")).first()', file='pyspark',
             output='Row(count(amt)=50001, count(1)=50002)', note='One value was not a number.'),
        dict(title='3 · A filter', cmd='c.where((F.col("city") == "Pune") & (F.col("amount") > 500)).count()', file='pyspark',
             output='860', note='Same as the SQL string version.'),
    ],
)

TRACE = dict(
    heading='Why a withColumn loop is slow',
    intro='<p>Count how much plan the driver analyses in each approach.</p>',
    code='''analysed = 0
plan = 1
for i in range(5):              # 5 x withColumn
    plan += 1
    analysed += plan
print("loop:", analysed, "nodes analysed")
print("one call:", 1 + 1, "nodes analysed")
''',
    notes={4: 'Growth :: Each new DataFrame has a bigger plan to analyse.', 7: 'One projection :: withColumns or select adds one node.'},
)

WORKED_INTRO = 'Three column tasks from TiffinGo pipelines.'
EXAMPLES = [
    dict(level='b', tag='Columns · basics', title='Add GST and a rounded total',
         problem='<p>Add gst (5%) and total, rounded to 2 decimals.</p>',
         inp='amount column',
         approach=['Compute in one withColumns.', 'Round with F.round.', 'Check the schema.'],
         code='''amount = 530
gst = round(amount * 0.05, 2)
print({"gst": gst, "total": round(amount + gst, 2)})
''', notes={2: 'Spark :: F.round(F.col("amount") * 0.05, 2).'},
         tryit='Use DECIMAL for real money (Lesson 4.2).'),
    dict(level='i', tag='Columns · quality', title='Typed columns with a bad-row count',
         problem='<p>Convert amount and order_ts and report bad rows.</p>',
         inp='string columns',
         approach=['try_cast / try_to_timestamp.', 'Count nulls created.', 'Write bad rows aside.'],
         code='''raw = [("530", "2026-10-29 20:49:00"), ("abc", "2026-10-17 20:25:00"), ("410", "31/10/2026 21:20")]
bad = [r for r in raw if not r[0].isdigit() or "/" in r[1]]
print(len(bad), "bad rows:", bad)
''', notes={2: 'Lab :: The real file had exactly these two kinds of bad value.'},
         tryit='Module 5 adds read modes for corrupt records.'),
    dict(level='a', tag='Columns · performance', title='Generate features from config',
         problem='<p>Add 300 features defined in a config file, fast.</p>',
         inp='list of (name, SQL expression)',
         approach=['Build a dict of Columns.', 'One withColumns call.', 'Or selectExpr with all strings.'],
         code='''config = [(f"amt_x{k}", f"amount * {k}") for k in range(3)]   # 300 in production
exprs = {name: f"F.expr({sql!r})" for name, sql in config}
print("df.withColumns(", exprs, ")")
''', notes={3: 'One call :: 0.98 s instead of 6.87 s for 300 columns in our lab.'},
         tryit='Step 6 timings.'),
]

QUIZ = mix([
    dict(q='Beginner: Which is the recommended way to refer to a column anywhere?', options=['df.city', 'F.col("city")', '"city" * 2', 'city'], answer=1,
         why='Works even before the DataFrame exists.'),
    dict(q='Beginner: withColumn with an existing column name…', options=['Fails', 'Adds a duplicate', 'Replaces the column', 'Renames it'], answer=2,
         why='Same name = replace.'),
    dict(q='Beginner: How do you combine two conditions?', options=['and', '(a) & (b)', 'a && b', 'a + b'], answer=1,
         why='Operators with brackets.'),
    dict(q='Intermediate: In Spark 4, cast("int") on "abc" gives…', options=['null', '0', 'CAST_INVALID_INPUT error', '"abc"'], answer=2,
         why='ANSI mode is on by default.'),
    dict(q='Intermediate: What does try_cast do with "abc"?', options=['Error', 'Returns null', 'Returns 0', 'Drops the row'], answer=1,
         why='Then count the nulls.'),
    dict(q='Intermediate: A row with hour = null in when(hour < 11, …).otherwise("late-night") becomes…', options=['null', 'breakfast', 'late-night', 'error'], answer=2,
         why='Null conditions are not true.'),
    dict(q='Advanced: Why is a withColumn loop slow?', options=['It reads data each time', 'Each call creates a plan that is re-analysed', 'It shuffles', 'It caches'], answer=1,
         why='6.87 s vs 0.98 s for 300 columns.'),
    dict(q='Advanced: When does a misspelt column name fail?', options=['At write time', 'At analysis, before any job', 'Never', 'Inside executors'], answer=1,
         why='UNRESOLVED_COLUMN with a suggestion.'),
])

REVISION = [
    'Name columns with <code>"c"</code>, <code>df.c</code>, <code>df["c"]</code> or <code>F.col("c")</code>; a Column is an expression.',
    '<code>select</code>/<code>selectExpr</code>, <code>withColumn</code>/<code>withColumns</code>, <code>withColumnRenamed</code>, <code>drop</code> (ignores missing names).',
    'Spark 4 ANSI: <code>cast</code> fails on bad input; <code>try_cast</code>/<code>try_to_timestamp</code> return null.',
    '<code>F.when(…).otherwise(…)</code>: nulls fall into otherwise.',
    'Filters: <code>(a) &amp; (b)</code>, <code>|</code>, <code>~</code>; never Python and/or.',
    'Typos fail at analysis with “Did you mean”.',
    '300 columns: loop 6.87 s, <code>withColumns</code> 0.98 s, one <code>select</code> 0.83 s.',
]
FAQ = [
    ('Should I turn ANSI mode off after upgrading?', 'Only as a short-term bridge. ANSI errors reveal bad data that Spark 3 silently turned into nulls; fix them with try_cast and quarantine instead.'),
    ('Is where() different from filter()?', 'No, they are aliases.'),
    ('Is selectExpr slower than functions?', 'No. Both become the same Catalyst expressions; choose the one your team reads best.'),
    ('How do I add a constant column?', '<code>df.withColumn("source", F.lit("app"))</code>. lit wraps a Python value as a Column.'),
    ('Why does df.count give a method instead of a column?', 'Attribute access clashes with DataFrame methods. Use <code>F.col("count")</code> or <code>df["count"]</code> for such names.'),
]

PRACTICE_INTRO = 'Programs about column expressions, casts and filters.'
PROBLEMS = [
    dict(level='easy', title='Bad share', stmt='Share of rows lost to try_cast.', inp='50,001 of 50,002 valid',
         code='''print(f"{1 - 50001 / 50002:.4%}")
''', explain='Small, but it would have failed the job.'),
    dict(level='easy', title='Meal slot', stmt='Return the slot for an hour.', inp='hour 14',
         code='''h = 14
print("breakfast" if h < 11 else "lunch" if h < 16 else "dinner" if h < 22 else "late-night")
''', explain='Same order as when().'),
    dict(level='easy', title='GST', stmt='GST at 5% on ₹860.', inp='860',
         code='''print(round(860 * 0.05, 2))
''', explain='F.round(col * 0.05, 2) in Spark.'),
    dict(level='medium', title='Rename map', stmt='Convert column names to snake_case.', inp='OrderID, CustomerID, OrderTS',
         code='''import re
names = ["OrderID", "CustomerID", "OrderTS"]
print({n: re.sub(r"(?<!^)(?=[A-Z][a-z])", "_", n).lower() for n in names})
''', explain='Feed the dict to withColumnsRenamed.'),
    dict(level='medium', title='Parse safely', stmt='Parse timestamps, None on failure.', inp='two formats',
         code='''from datetime import datetime
def parse(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None
print([parse(s) for s in ("2026-10-29 20:49:00", "31/10/2026 21:20")])
''', explain='Like try_to_timestamp.'),
    dict(level='medium', title='Plan growth', stmt='Total nodes analysed for n withColumn calls.', inp='n = 300',
         code='''n = 300
print(sum(range(2, n + 2)))
''', explain='Grows with n squared.'),
    dict(level='business', title='High-value Pune', stmt='Share of Pune and Mumbai orders that are Pune orders above ₹500.', inp='860 of 17,946 (lab)',
         code='''print(f"{860 / 17946:.1%}")
''', explain='Filter, then count.'),
    dict(level='business', title='Driver time saved', stmt='Minutes saved per day by replacing the loop.', inp='5.9 s saved per run, 96 runs/day',
         code='''print(round(5.9 * 96 / 60, 1), "minutes")
''', explain='Driver time is cluster time too.'),
]

SCN_INTRO = 'Column questions are where interviewers spot real PySpark experience.'
SCENARIOS = (
    scn('Any company · PySpark', 'Fresher', '“select vs withColumn?”',
        'When do you use select and when withColumn?',
        'do you know projections?',
        '<p><code>select</code> returns exactly the columns you list (and can compute new ones); <code>withColumn</code> keeps all columns and adds or replaces one. For many new columns use <code>withColumns</code> or one select, because each withColumn adds a projection to the plan.</p>', '“They are the same.”') +
    scn('Data engineering', 'Fresher', 'Multiple conditions',
        'Filter Pune orders above ₹500.',
        'do you know operator rules?',
        '''<ul>
          <li><code>df.where((F.col("city") == "Pune") &amp; (F.col("amount") &gt; 500))</code></li>
          <li>Or <code>df.where("city = 'Pune' AND amount &gt; 500")</code>.</li>
          <li>Python and/or raise CANNOT_CONVERT_COLUMN_INTO_BOOL.</li>
        </ul>''', 'Forgetting brackets.') +
    scn('Data engineering', 'Mid-level', 'Job fails after Spark 4 upgrade',
        'CAST_INVALID_INPUT appears after upgrading. What do you do?',
        'do you know ANSI mode?',
        '''<ol>
          <li>Spark 4 enables ANSI: bad casts fail instead of returning null.</li>
          <li>Find the bad values; use try_cast where bad input is expected.</li>
          <li>Quarantine and monitor nulls; avoid disabling ANSI globally.</li>
        </ol>''', 'Setting spark.sql.ansi.enabled=false everywhere.') +
    scn('Data engineering', 'Senior', 'Slow driver before jobs start',
        'A job spends minutes before the first Spark job appears.',
        'can you diagnose plan-analysis cost?',
        '''<ul>
          <li>Look for long chains: withColumn loops, many unions, deep plans.</li>
          <li>Batch columns with withColumns/select; checkpoint very long chains (Lesson 3.3).</li>
          <li>Measure build time separately from run time.</li>
        </ul>''', 'Adding executors.')
)
