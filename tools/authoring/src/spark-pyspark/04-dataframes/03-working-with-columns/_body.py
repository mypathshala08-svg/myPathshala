import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l43_columns.txt'
def sec(a, b=None, drop=()):
    s = capsec(C, a, b, drop)
    return '\n'.join(l if len(l) <= 150 else l[:147] + ' …' for l in s.split('\n'))

def cols(x, y, names, tones, title='', w=44, h=26):
    o = t(x, y - 6, title, 7.4, 'ink2', anchor='start', bold=True) if title else ''
    for k, (n, tn) in enumerate(zip(names, tones)):
        o += opbox(x + k * (w + 4), y, n, '', tn, w, h)
    return o

# ---------------------------------------------------------------- story
sc_ = (cols(14, 34, ['id', 'city', 'amt', 'ts'], ['card'] * 4, 'orders') + arrow(110, 76, 110, 92, 'ink3', 1.1) +
       cols(14, 100, ['id', 'city', 'amt', 'ts', 'gst', 'slot'], ['card', 'card', 'green', 'green', 'acc', 'acc'], '', 40, 26) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('cast("int") on "abc" -> error', 'red'), ('try_cast -> null, sum ok', 'green'),
           ('and / no brackets -> error', 'red'), ('typo ammount -> "Did you mean"', 'amber'),
           ('300 x withColumn: 6.87 s', 'amber'), ('one withColumns: 0.98 s', 'green')])))
scene_svg = scene('Column operations select, add, rename, cast and filter columns. We cleaned TiffinGo orders column by column and timed adding 300 columns in a loop against one call.', sc_,
                  'Columns are <tspan font-weight="700" class="s-acc">expressions</tspan>; build many at once, not one by one.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“The feature job takes ten minutes before it reads anything”</h2>
  <div class="story">
    <p class="narration">Riya’s feature job adds 300 columns to the orders DataFrame, one <code>withColumn</code> per feature in a loop. The Spark UI shows no jobs for the first minutes; the driver CPU is at 100%. Then a colleague’s change to the amount column fails the whole job with <code>CAST_INVALID_INPUT</code>.</p>

{scene_svg}

R> Sir, nothing is even running yet. What is the driver doing?
A> Analysing your plan, 300 times. Every <code>withColumn</code> creates a new DataFrame whose plan must be analysed again. Build the columns in <b>one</b> call and the waiting disappears.
K> And the cast error? The same code ran on Spark 3.
A> Spark 4 runs with <b>ANSI mode</b> on: a bad cast is an error, not a silent null. Today: naming columns, select and expressions, casts and <code>try_cast</code>, adding and renaming, <code>when/otherwise</code>, filters and their traps, and the 300-column timing. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Columns at three levels
L1> A spreadsheet
      <ul>
        <li>Selecting is hiding the columns you do not need; adding is a new column with a formula; filtering is hiding rows.</li>
        <li>A formula like <code>=B2*0.05</code> describes every row at once; a Column expression does the same.</li>
        <li>Typing a formula into each cell one by one is slow; writing it once for the whole column is fast.</li>
      </ul>
L2> The API
      <ul>
        <li>Name a column: <code>"city"</code>, <code>df.city</code>, <code>df["city"]</code>, <code>F.col("city")</code>; build expressions with operators and <code>pyspark.sql.functions</code>.</li>
        <li><code>select</code>, <code>selectExpr</code>, <code>withColumn</code>, <code>withColumns</code>, <code>withColumnRenamed</code>, <code>drop</code>, <code>cast</code>/<code>try_cast</code>, <code>F.when().otherwise()</code>, <code>where</code>/<code>filter</code>.</li>
        <li>Combine conditions with <code>&amp;</code>, <code>|</code>, <code>~</code> and brackets, never Python <code>and</code>/<code>or</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>With ANSI on, <code>cast("int")</code> failed on <code>'abc'</code>; <code>try_cast</code> gave null and a sum over 50,001 values.</li>
        <li>Missing brackets and Python <code>and</code> both raised CANNOT_CONVERT_COLUMN_INTO_BOOL; a typo got a “Did you mean” suggestion.</li>
        <li>300 columns: <code>withColumn</code> loop 6.87 s to build, <code>withColumns</code> 0.98 s, one <code>select</code> 0.83 s.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Column expressions</h2>
''' + def_block(
    'A <b>Column</b> in PySpark is an expression evaluated for every row of a DataFrame: a reference to an input column, a literal (<code>F.lit</code>), or a combination built with operators and functions from <code>pyspark.sql.functions</code>. Column expressions are used in projections (<code>select</code>, <code>withColumn</code>, <code>withColumns</code>), in predicates (<code>where</code>/<code>filter</code>) and in aggregations. Each such transformation returns a new DataFrame whose logical plan must be analysed by Catalyst; projections built in one call produce one plan node, while repeated <code>withColumn</code> calls add one node and one analysis each. Under ANSI mode (default since Spark 4.0), invalid casts and arithmetic overflow raise errors; <code>try_cast</code> and other <code>try_*</code> functions return null instead.',
    'A column in your code is a small formula, like <code>amount * 0.05</code>, that Spark applies to every row. You use these formulas to choose, add, change and filter columns. Add many columns in one step, and use <code>try_cast</code> when some values might be bad.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Column', 'An expression applied to every row.'),
    ('F', '<code>from pyspark.sql import functions as F</code>.'),
    ('lit()', 'A constant value as a column.'),
    ('alias()', 'Name the result column.'),
    ('selectExpr', 'select with SQL expression strings.'),
    ('withColumns', 'Add or replace many columns in one call (3.3+).'),
    ('ANSI mode', 'SQL standard behaviour: bad casts are errors.'),
    ('try_cast', 'Cast that returns null instead of failing.'),
]) + '''

  <h3>Which method?</h3>
''' + table(['Want to…', 'Use', 'Example'], [
    ['Keep some columns, compute others', '<code>select</code>', '<code>df.select("id", F.upper("city").alias("CITY"))</code>'],
    ['Write SQL snippets', '<code>selectExpr</code> / <code>F.expr</code>', '<code>df.selectExpr("id", "amount * 1.05 AS gross")</code>'],
    ['Add or replace one column', '<code>withColumn</code>', '<code>df.withColumn("gst", F.col("amount") * 0.05)</code>'],
    ['Add many columns', '<code>withColumns</code> or one <code>select</code>', '<code>df.withColumns({"a": …, "b": …})</code>'],
    ['Rename', '<code>withColumnRenamed</code> / <code>withColumnsRenamed</code>', '<code>df.withColumnRenamed("payment", "pay_mode")</code>'],
    ['Remove', '<code>drop</code>', '<code>df.drop("restaurant_id")</code>'],
    ['If / else', '<code>F.when(…).otherwise(…)</code>', 'meal slot from the hour'],
    ['Filter rows', '<code>where</code> = <code>filter</code>', '<code>df.where((F.col("city") == "Pune") &amp; (F.col("amount") &gt; 500))</code>'],
], minw=760) + lv + '''
EXAM> “withColumn in a loop: what is wrong?” Each call returns a new DataFrame and adds a projection to the plan, which Catalyst re-analyses every time; with hundreds of columns this costs seconds to minutes on the driver and can cause StackOverflowError. Use <code>withColumns</code> or a single <code>select</code> (300 columns: 6.87 s vs 0.98 s vs 0.83 s in our lab).
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Four ways to refer to a column</h2>
''' + table(['Form', 'Works when', 'Watch out'], [
    ['<code>"city"</code>', 'Most methods accept names', 'Not for expressions like <code>"amount" * 2</code>'],
    ['<code>df.city</code>', 'Name is a valid Python identifier', 'Fails for <code>order-id</code>; clashes with DataFrame methods (<code>df.count</code>)'],
    ['<code>df["city"]</code>', 'Any name', 'Bound to that DataFrame: useful to disambiguate joins'],
    ['<code>F.col("city")</code>', 'Anywhere, even before the DataFrame exists', 'Recommended default'],
], minw=680) + '''
WARN> Python’s <code>and</code>, <code>or</code> and <code>not</code> do not work on Columns, and <code>&amp;</code> binds tighter than <code>==</code>. Always write <code>(F.col("city") == "Pune") &amp; (F.col("amount") &gt; 500)</code> with brackets around each comparison, or use a SQL string: <code>df.where("city = 'Pune' AND amount &gt; 500")</code>.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Cleaning orders column by column</h2>
  <p>All outputs are real: PySpark 4.3.0, local mode, TiffinGo <code>orders.csv</code> read with a schema in which <code>amount</code> and <code>order_ts</code> are still strings.</p>
''' + stepper([
    ('Step 1 · Naming columns and select',
     code('python', 'l43_columns.py', 'o.select("city", o.city, o["city"], F.col("city")).columns\nF.col("amount") * 2\no.select("order_id", F.upper("city").alias("CITY"), (F.col("order_id") % 7).alias("bucket")).show(3)\no.selectExpr("order_id", "upper(city) AS CITY", "order_id % 7 AS bucket").show(3)', sec('== 1)', '== 3)')),
     'All four forms named the same column. <code>F.col("amount") * 2</code> is not a number but an expression, <code>Column&lt;\'*(amount, 2)\'&gt;</code>, evaluated later for every row. <code>select</code> with functions and <code>selectExpr</code> with SQL strings gave identical results.'),
    ('Step 2 · cast fails, try_cast survives',
     code('python', 'l43_columns.py', 'spark.conf.get("spark.sql.ansi.enabled")\no.select(F.col("amount").cast("int")).agg(F.sum("amount")).show()\no.select(F.col("amount").try_cast("int").alias("amt")).agg(F.sum("amt"), F.count("amt"), F.count("*"))\no.where(F.try_to_timestamp("order_ts").isNull()).select("order_ts")', sec('== 3)', '== 4)')),
     'ANSI mode is on in Spark 4, so one value, <code>abc</code>, failed the whole cast with CAST_INVALID_INPUT. <code>try_cast</code> turned it into null: 50,001 amounts summed to ₹1,47,21,390 out of 50,002 rows. <code>try_to_timestamp</code> found the other bad value, a date written as <code>31/10/2026 21:20</code>. Count the nulls after <code>try_*</code>: they are your bad rows.'),
    ('Step 3 · Add, rename and drop',
     code('python', 'l43_columns.py', 'c = (o.withColumn("amount", F.col("amount").try_cast("int"))\n      .withColumn("order_ts", F.try_to_timestamp("order_ts"))\n      .withColumns({"gst": F.round(F.col("amount") * 0.05, 2), "hour": F.hour("order_ts")})\n      .withColumnRenamed("payment", "pay_mode")\n      .drop("restaurant_id", "no_such_column"))\nc.printSchema()', sec('== 4)', '== 5)')),
     'Using an existing name in <code>withColumn</code> <b>replaces</b> the column; a new name adds one. <code>withColumns</code> added two at once. <code>drop</code> silently ignored a column that does not exist, which is convenient but can hide typos.'),
    ('Step 4 · when / otherwise',
     code('python', 'l43_columns.py', 'c = c.withColumn("slot", F.when(F.col("hour") < 11, "breakfast")\n                          .when(F.col("hour") < 16, "lunch")\n                          .when(F.col("hour") < 22, "dinner")\n                          .otherwise("late-night"))\nc.groupBy("slot").count().orderBy("slot").show()', sec('== 5)', '== 6)')),
     '<code>when</code> conditions are checked in order, like <code>CASE WHEN</code> in SQL. Note that a row whose <code>hour</code> is null (the bad timestamp) matches no condition and lands in <code>otherwise</code>: one of these 4,154 “late-night” orders is really unknown. Handle nulls explicitly when it matters (Lesson 4.4).'),
    ('Step 5 · Filters and their traps',
     code('python', 'l43_columns.py', 'c.where((F.col("city") == "Pune") & (F.col("amount") > 500)).count()\nc.filter("city = \'Pune\' AND amount > 500").count()\nc.where(F.col("city") == "Pune" & F.col("amount") > 500)          # no brackets\nc.where((F.col("city") == "Pune") and (F.col("amount") > 500))    # Python and\nc.select("ammount")', sec('== 6)', '== 8)')),
     'Column and SQL-string filters gave the same 860 Pune orders above ₹500. Without brackets, <code>&amp;</code> was applied first and produced nonsense; with Python <code>and</code>, Python tried to turn a Column into True/False. Both failed with CANNOT_CONVERT_COLUMN_INTO_BOOL. A misspelt column fails at <b>analysis</b>, before any job, with a helpful suggestion.'),
    ('Step 6 · 300 columns: loop vs one call',
     code('python', 'l43_columns.py', 'd = base\nfor i in range(300):\n    d = d.withColumn(f"c{i}", F.col("id") + i)                      # 300 plans\nd = base.withColumns({f"c{i}": F.col("id") + i for i in range(300)})   # one call\nd = base.select("*", *[(F.col("id") + i).alias(f"c{i}") for i in range(300)])', sec('== 8)')),
     'The loop needed <b>6.87 s</b> on the driver just to build the DataFrame, before any data was read; <code>withColumns</code> needed 0.98 s and one <code>select</code> 0.83 s. The data work (count) was tiny in all three. Riya’s minutes of waiting were plan analysis. The PySpark docs warn about exactly this: loops of <code>withColumn</code> can also end in StackOverflowError.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('"city", o.city, o["city"], col("city")', W), ('-> same column', G), ('col("amount") * 2 -> Column', W)], size=7.2),
    term([('cast("int") on "abc": CAST_INVALID_INPUT', RD), ('try_cast: 50,001 values, sum ok', G), ('bad ts: 31/10/2026 21:20', Y)], size=7.0),
    term([('withColumn(existing) -> replace', W), ('withColumns({gst, hour})', G), ('drop("no_such_column") -> ok', Y)], size=7.4),
    term([('city==Pune & amount>500: 860', G), ('no brackets: CANNOT_CONVERT…', RD), ('ammount: Did you mean amount?', Y)], size=7.2),
    term([('withColumn x300 : 6.87 s', RD), ('withColumns     : 0.98 s', G), ('one select      : 0.83 s', G)], size=7.6),
]
B1 = [
    t(180, 14, 'A column is an expression', 9.4, bold=True) + flow([('col("amount")', 'reference', 'card'), ('* 2', 'operator', 'violet'), ('per row', 'later', 'blue')], y=48, w=96, gap=22) + cap('Nothing is computed yet.', '', 'blue', y=144, h=30),
    t(180, 14, 'ANSI: errors, not silent nulls', 9.4, bold=True) + flow([('"abc"', 'value', 'card'), ('cast', 'error', 'acc')], y=40, w=96, gap=40) + flow([('"abc"', 'value', 'card'), ('try_cast', 'null', 'green')], y=88, w=96, gap=40) + cap('Choose fail-fast or tolerant.', '', 'amber', y=144, h=30),
    t(180, 14, 'New DataFrame each time', 9.4, bold=True) + cols(20, 50, ['id', 'city', 'amt', 'ts'], ['card'] * 4) + arrow(110, 80, 110, 92, 'ink3', 1.1) + cols(20, 98, ['id', 'city', 'amt', 'ts', 'gst', 'hr'], ['card', 'card', 'green', 'green', 'acc', 'acc'], '', 40) + cap('Replace or add columns.', '', 'green', y=144, h=30),
    t(180, 14, 'Conditions need brackets', 9.4, bold=True) + flow([('(city==Pune)', 'Column', 'green'), ('&', 'and', 'violet'), ('(amount>500)', 'Column', 'green')], y=50, w=96, gap=22) + cap('& | ~ with brackets, never and/or.', '', 'red', y=144, h=30),
    t(180, 14, 'Plans grow with each call', 9.4, bold=True) + ''.join(opbox(14 + k * 14, 36 + k * 9, '', '', 'amber', 90, 18) for k in range(6)) + t(100, 122, '300 projections', 7.4, 'ink2') + opbox(214, 60, 'withColumns', 'one projection', 'green', 130, 30) + cap('Build many columns in one call.', '', 'green', y=144, h=30),
]
see_caps = ['Four names, one column.', 'cast failed; try_cast did not.', 'Columns replaced and added.', 'Two traps and a suggestion.', '300 columns: 6.87 s vs 0.98 s.']
behind_caps = ['A Column is a formula.', 'Spark 4 runs in ANSI mode.', 'DataFrames are immutable.', 'Operators, not Python keywords.', 'Each withColumn is re-analysed.']
two = anim_two('Working with columns', 'Formulas for every row', 'Real lab outputs', 'The expression', see, B1, see_caps, behind_caps)

# ---- scenario 1: Spark 3 to 4 upgrade
e1 = (t(180, 22, 'Upgrade to Spark 4', 9.4, bold=True) + t(180, 56, 'same code, same data', 8.4, 'ink2') + cap('Job fails on day one.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'CAST_INVALID_INPUT', 9.4, bold=True) + t(180, 56, 'Spark 3 returned null silently', 8.4, 'ink2') + cap('ANSI is now on.', '', 'amber', y=150, h=34))
e3 = (t(180, 22, 'Do not turn ANSI off', 9.4, bold=True) + t(180, 56, 'silent nulls hid bad data', 8.4, 'ink2') + cap('The error is a gift.', '', 'red', y=150, h=34))
e4 = (t(180, 22, 'try_cast where bad data is expected', 9.4, bold=True) + t(180, 56, 'col("amount").try_cast("int")', 8.2, 'ink', mono=True) + cap('Then count the nulls.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Quarantine bad rows', 9.4, 'acc', bold=True) + t(180, 56, 'where amt IS NULL -> bad_rows table', 8.2, 'ink', mono=True) + cap('Visible, not lost.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'The upgrade that found bad data',
              'ANSI mode in Spark 4. (Typical; behaviour from our lab.)',
              'ANSI casts', 'Spark 4 fails on invalid casts; use try_cast where bad input is expected and quarantine the null results', [e1, e2, e3, e4, e5],
              ['Upgrade.', 'Cast error.', 'Keep ANSI.', 'try_cast.', 'Quarantine.'],
              hid='scenario-ansi')

# ---- scenario 2: feature job
b1 = (t(180, 22, '300 features in a loop', 9.4, bold=True) + t(180, 56, 'for f in features: df = df.withColumn(…)', 8.0, 'ink', mono=True) + cap('Minutes before any job.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Driver CPU 100%', 9.4, bold=True) + t(180, 56, 'Spark UI: no jobs yet', 8.4, 'ink2') + cap('Plan analysis, 300 times.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'One call', 9.4, bold=True) + t(180, 56, 'df.withColumns({name: expr, …})', 8.2, 'ink', mono=True) + cap('Build the dict in Python.', '', 'green', y=150, h=34))
b4 = (t(180, 22, '6.87 s -> 0.98 s', 9.4, bold=True) + t(180, 56, 'in our lab, 300 columns', 8.4, 'ink2') + cap('Bigger plans, bigger gains.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Same for renames', 9.4, 'acc', bold=True) + t(180, 56, 'withColumnsRenamed({…})', 8.4, 'ink', mono=True) + cap('Batch every change.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'A feature job stuck on the driver',
              'withColumn loops. (Typical; numbers from our lab.)',
              'withColumn loops', 'Each withColumn adds a projection that is re-analysed; build all columns with withColumns or one select', [b1, b2, b3, b4, b5],
              ['Loop.', 'Driver busy.', 'One call.', 'Faster.', 'Batch renames too.'],
              hid='scenario-loop')

# ---- scenario 3: null in when
u1 = (t(180, 22, 'Meal-slot report', 9.4, bold=True) + t(180, 56, 'when(hour < 11, …).otherwise("late-night")', 7.8, 'ink', mono=True) + cap('Looks complete.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Late-night orders jump', 9.4, bold=True) + t(180, 56, 'a feed sends bad timestamps', 8.4, 'ink2') + cap('hour is null.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'null matches no when()', 9.4, bold=True) + t(180, 56, 'falls into otherwise', 8.4, 'ink2') + cap('Like our Step 4.', '', 'red', y=150, h=34))
u4 = (t(180, 22, 'Handle null first', 9.4, bold=True) + t(180, 56, 'when(col("hour").isNull(), "unknown")', 8.0, 'ink', mono=True) + cap('Explicit bucket.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Monitor "unknown"', 9.4, 'acc', bold=True) + t(180, 56, 'alert when it grows', 8.4, 'ink2') + cap('Data quality signal.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'otherwise() swallowed the bad rows',
              'Nulls in conditional columns. (Typical; behaviour from our lab.)',
              'Nulls in when', 'A null condition is not true, so null rows fall into otherwise; test isNull first and track an unknown bucket', [u1, u2, u3, u4, u5],
              ['Report.', 'Spike.', 'Null to otherwise.', 'Unknown bucket.', 'Monitor.'],
              hid='scenario-when')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Formulas for every row</h2>
  <p>Left: real outputs. Right: what the column expressions do.</p>
''' + two + '''
  <p>Three live scenarios follow: a Spark 4 upgrade, a feature job stuck on the driver, and nulls that disappear into <code>otherwise</code>.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Column work at companies</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'clean', 12, 'blue', bold=True) + t(60, 58, 'types', 7.4, 'ink2'),
    '1. Type cleaning',
    'Raw string feeds are converted with try_cast and try_to_timestamp; rows that become null go to a quarantine table.',
    ['Raw strings', '*try_cast', 'Typed table']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'features', 10, 'green', bold=True) + t(60, 58, 'ML', 7.4, 'ink2'),
    '2. Feature engineering',
    'Hundreds of ratio and flag columns are generated from a config and added with one withColumns call.',
    ['Config', '*withColumns', 'Features']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'rules', 12, 'violet', bold=True) + t(60, 58, 'business', 7.4, 'ink2'),
    '3. Business rules',
    'Segments such as meal slot, order size band or customer tier are when/otherwise columns.',
    ['Order', '*when/otherwise', 'Segment']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'PII', 12, 'acc', bold=True) + t(60, 58, 'masking', 7.4, 'ink2'),
    '4. Masking personal data',
    'Phone and email columns are hashed or dropped before data leaves the secure zone.',
    ['Raw', '*sha2 / drop', 'Shared data']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'rename', 11, 'acc', bold=True) + t(60, 58, 'standards', 7.4, 'ink2'),
    '5. Naming standards',
    'Columns from source systems are renamed to company standards (snake_case, units in names) in one step.',
    ['Source names', '*withColumnsRenamed', 'Standard names']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> DataFrames and plans in <a href="../01-sparksession-and-dataframes/">4.1</a>, schemas in <a href="../02-creating-dataframes-and-schemas/">4.2</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
