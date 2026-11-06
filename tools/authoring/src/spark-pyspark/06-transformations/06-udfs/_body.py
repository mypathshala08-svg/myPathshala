import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l66_udf.txt'
def sec(a, b=None, drop=()):
    s = capsec(C, a, b, drop)
    s = re.sub(r'#\d+L?', '', s)
    return '\n'.join(l if len(l) <= 140 else l[:137] + ' …' for l in s.split('\n'))
PLANS = sec('== 3)', '== 4)', drop=('InMemoryRelation', 'ColumnarToRow', 'FileScan'))

def jvm_py(batch=False, hi='py'):
    o = box(10, 30, 150, 90, 'blue') + t(85, 46, 'Executor JVM', 8, bold=True) + opbox(24, 56, 'scan, filter', 'built-ins', 'card', 122, 26)
    o += box(220, 30, 130, 90, 'violet' if hi == 'py' else 'card') + t(285, 46, 'Python worker', 8, bold=True) + opbox(232, 56, 'your function', 'band(a)', 'card', 106, 26)
    if batch:
        o += arrow(160, 76, 220, 76, 'ink3', 1.3) + box(176, 64, 28, 10, 'green', rx=2) + t(190, 92, 'Arrow batch', 6.4, 'green')
    else:
        o += arrow(160, 76, 220, 76, 'ink3', 1.0) + ''.join(box(168 + k * 9, 66, 6, 6, 'amber', rx=1) for k in range(5)) + t(190, 92, 'row by row', 6.4, 'amber')
    return o

# ---------------------------------------------------------------- story
sc_ = (jvm_py(False) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured (5M rows)', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('built-in when(): 0.85 s', 'green'), ('Python UDF (pickle): 3.50 s', 'red'),
           ('Arrow UDF 2.31 s, pandas 2.10 s', 'amber'), ('UDF filter: no pushdown, 4.09 s', 'red'),
           ('returns 472.5 as "int": None / 472', 'red'), ('SQL UDF: no Python step', 'green')])))
scene_svg = scene('A UDF runs your own Python function on every row, in Python worker processes beside the JVM. We computed the same order band with a built-in expression and three kinds of Python UDF, and looked at what UDFs hide from the optimizer.', sc_,
                  'A UDF is a <tspan font-weight="700" class="s-acc">black box</tspan>: use built-ins first, pandas UDFs when you must.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“It is only three lines of Python”</h2>
  <div class="story">
    <p class="narration">Riya wrapped a three-line function that labels orders “low”, “mid” or “high” in a <code>udf</code>, because it was easier than remembering Spark functions. The nightly job slowed down by minutes, a filter on the label stopped skipping Parquet data, and one night it crashed on a null amount.</p>

{scene_svg}

R> Sir, the function is trivial. Why is it slow?
A> Not the function: the trip. Each value leaves the JVM, is serialised to a Python worker, processed, and sent back. And Catalyst cannot see inside your function, so it cannot push filters down or simplify anything.
K> Then why do UDFs exist at all?
A> Because sometimes you need a Python library. Then use the fastest kind. Today: the same logic as a built-in, a classic Python UDF, an Arrow-optimised UDF and a pandas UDF on 5 million rows; plans; pushdown; nulls and return types; and SQL UDFs in Spark 4. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> UDFs at three levels
L1> Asking a translator
      <ul>
        <li>Spark’s own functions speak Spark’s language: fast and understood by the planner.</li>
        <li>A Python UDF is like sending every sentence to a translator in another room and waiting for the answer.</li>
        <li>Arrow and pandas UDFs send a whole page at a time instead of one sentence.</li>
      </ul>
L2> The API
      <ul>
        <li><code>F.udf(func, returnType, useArrow=…)</code> or <code>@udf</code>; <code>@pandas_udf("type")</code> on a function from <code>pd.Series</code> to <code>pd.Series</code>.</li>
        <li>For SQL: <code>spark.udf.register("name", func, type)</code>; SQL UDFs: <code>CREATE FUNCTION f(x INT) RETURNS … RETURN expr</code>.</li>
        <li><code>spark.sql.execution.pythonUDF.arrow.enabled</code> is true by default since Spark 4.2.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>Same result: built-in 0.85 s, pickled Python UDF 3.50 s, Arrow UDF 2.31 s, pandas UDF 2.10 s.</li>
        <li>A UDF in a filter disabled Parquet pushdown: 4.09 s vs under 1 s.</li>
        <li>A UDF declared <code>int</code> returning 472.5 gave <code>None</code> (pickled) or <code>472</code> (Arrow), silently.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>User-defined functions</h2>
''' + def_block(
    'A <b>user-defined function (UDF)</b> extends Spark SQL with custom logic. In PySpark, a <b>Python UDF</b> executes in Python worker processes: the executor JVM serialises input rows (with pickle, or with Apache Arrow for Arrow-optimised UDFs, the default since Spark 4.2), the worker evaluates the function and returns results. A <b>pandas UDF</b> (vectorised UDF) receives and returns batches as pandas Series via Arrow. UDFs are opaque to the Catalyst optimizer: predicates involving them cannot be pushed down to data sources, and their results are not used for constant folding or other rewrites; their declared return type must match the values returned. <b>SQL UDFs</b> (Spark 4.0) are defined with a SQL expression body and are inlined into the plan, so they run like built-in expressions.',
    'A UDF lets you run your own function on each row. Python UDFs are slow because data travels to Python and back, and Spark cannot optimise them. Use built-in functions first, a pandas UDF when you need Python libraries, and SQL UDFs to reuse expressions.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Python UDF', 'Row-at-a-time Python function.'),
    ('Arrow-optimised UDF', 'Python UDF with Arrow transfer (default in 4.2+).'),
    ('pandas UDF', 'Vectorised: pandas Series in, Series out.'),
    ('BatchEvalPython / ArrowEvalPython', 'Plan nodes for Python evaluation.'),
    ('Black box', 'Catalyst cannot look inside the function.'),
    ('Return type', 'Declared Spark type of the result.'),
    ('SQL UDF', 'CREATE FUNCTION … RETURN expression (Spark 4).'),
    ('UDTF', 'Python table function returning rows (Spark 3.5+).'),
]) + '''

  <h3>Which kind?</h3>
''' + table(['Kind', 'Runs in', 'Lab (5M rows)', 'Use when'], [
    ['Built-in functions / SQL expression', 'JVM, code-generated', '0.85 s', 'Always first choice'],
    ['SQL UDF (Spark 4)', 'Inlined as an expression', 'no Python step in plan', 'Reusable business expressions'],
    ['pandas UDF', 'Python, Arrow batches', '2.10 s', 'Vectorisable Python/numpy logic, ML models'],
    ['Arrow-optimised Python UDF', 'Python, Arrow transfer, row function', '2.31 s', 'Row logic that needs Python'],
    ['Classic (pickled) Python UDF', 'Python, row by row', '3.50 s', 'Legacy; avoid'],
], minw=700) + lv + '''
EXAM> “Why avoid Python UDFs?” Data must be serialised between the JVM and Python workers, the function runs row by row in Python, and Catalyst treats it as a black box, so filters on it are not pushed down and no optimisation applies. In our lab the same label took 0.85 s as a built-in and 3.50 s as a pickled UDF; a UDF filter on Parquet lost pushdown and took 4.09 s.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Python logic in Spark</h2>
''' + table(['API', 'Shape', 'Example use'], [
    ['<code>@udf</code>', 'value → value', 'parse a custom code'],
    ['<code>@pandas_udf</code> (Series → Series)', 'batch → batch', 'apply a numpy formula, score a model'],
    ['<code>@pandas_udf</code> (Series → scalar)', 'group → value', 'custom aggregation in groupBy'],
    ['<code>mapInPandas</code> / <code>mapInArrow</code>', 'iterator of DataFrames → iterator', 'batch scoring with setup per partition'],
    ['<code>applyInPandas</code>', 'group → DataFrame', 'per-city model fitting'],
    ['<code>@udtf</code> (Python UDTF)', 'value → rows', 'split one record into many rows'],
], minw=640) + '''
WARN> A Python UDF receives <code>None</code> for nulls, and if its result does not match the declared type it may silently become null or be truncated rather than fail. Always handle <code>None</code> first, declare the exact return type, and test the UDF on edge cases (nulls, empty strings, unexpected types) before running it on production data.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>One label, five implementations</h2>
  <p>All outputs are real: PySpark 4.3.0 with pandas 3.0 and PyArrow, local mode with 4 cores, 5,000,000 cached orders. Each timing is the second run of a fresh query.</p>
''' + stepper([
    ('Step 1 · Arrow for Python UDFs is on by default',
     code('python', 'l66_udf.py', 'spark.conf.get("spark.sql.execution.pythonUDF.arrow.enabled")', sec('== 1)', '== 2)')),
     'Since Spark 4.2 regular Python UDFs use Arrow to move data to Python workers unless you pass <code>useArrow=False</code> or turn the setting off. Old jobs upgraded to Spark 4.2+ get this change automatically, including its different type coercion (Step 5).'),
    ('Step 2 · The same label four ways',
     code('python', 'l66_udf.py', 'def band(a):\n    return "high" if a >= 600 else "mid" if a >= 300 else "low"\nplain = udf(band, "string", useArrow=False); arrowed = udf(band, "string", useArrow=True)\n@pandas_udf("string")\ndef band_pd(a: pd.Series) -> pd.Series:\n    return pd.cut(a, [-1, 299, 599, 10**9], labels=["low", "mid", "high"]).astype(str)\nbuiltin = F.when(F.col("amount") >= 600, "high").when(F.col("amount") >= 300, "mid").otherwise("low")', sec('== 2)', '== 3)')),
     'All four gave identical counts. The built-in expression took <b>0.85 s</b>; the classic pickled UDF <b>3.50 s</b> (4x slower), the Arrow UDF 2.31 s, the vectorised pandas UDF 2.10 s. The gap grows with more columns and more complex plans, and on a cluster each executor needs Python workers too.'),
    ('Step 3 · A black box in the plan',
     code('python', 'l66_udf.py', 'o.where(plain(F.col("amount")) == "high").select("order_id").explain()\no.where(builtin == "high").select("order_id").explain()', PLANS),
     'With the UDF, the plan has a <code>BatchEvalPython</code> node: rows go to Python, the result comes back as <code>pythonUDF0</code> and only then is filtered. With the built-in, the condition is an ordinary expression that Spark could even push into the in-memory scan. Catalyst can rearrange and simplify only what it can see.'),
    ('Step 4 · UDFs stop pushdown',
     code('python', 'l66_udf.py', 'p = spark.read.parquet(path)\nupper_city = udf(lambda c: c.upper() if c else None, "string")\np.where(F.upper("city") == "PUNE").count()\np.where(upper_city("city") == "PUNE").count()\np.where(F.col("city") == "Pune").count()', sec('== 4)', '== 5)')),
     'All three found 498,646 Pune orders. The plain filter was pushed into the Parquet scan (<code>EqualTo(city,Pune)</code>); the built-in <code>upper</code> at least pushed <code>IsNotNull</code>; the UDF pushed <b>nothing</b>, so every row had to travel through Python: 4.09 s against well under a second.'),
    ('Step 5 · Nulls and return types',
     code('python', 'l66_udf.py', 'd = spark.createDataFrame([(450,), (None,)], "amount INT")\nd.select(plain("amount")).collect()\nsafe = udf(lambda a: None if a is None else band(a), "string")\nfor arrow in (False, True):\n    wrong = udf(lambda a: a * 1.05, "int", useArrow=arrow)   # returns 472.5', sec('== 5)', '== 6)')),
     'A null reached the function as <code>None</code> and crashed it with a Python <code>TypeError</code>, failing the job. Handle <code>None</code> first. Worse, a function returning 472.5 while declared <code>int</code> gave <b>None</b> with pickling and <b>472</b> with Arrow: wrong either way, and with no error. The Spark 4.2 default switch to Arrow can change such results silently.'),
    ('Step 6 · SQL UDFs and registering for SQL',
     code('python', 'l66_udf.py', 'spark.sql("CREATE OR REPLACE TEMPORARY FUNCTION gst(amount INT) RETURNS DOUBLE RETURN round(amount * 0.05, 2)")\nspark.sql("SELECT gst(530) AS gst").show()\nspark.sql("SELECT sum(gst(amount)) FROM orders")      # plan: any Python step?\nspark.udf.register("band", band, "string")\nspark.sql("SELECT band(amount) b, count(*) n FROM orders GROUP BY b ORDER BY b").show()', sec('== 6)')),
     'A <b>SQL UDF</b>, new in Spark 4, packages an expression under a name; it is inlined into the plan, so the 5M-row sum ran with <b>no Python step</b>, like a built-in. <code>spark.udf.register</code> makes a Python UDF callable from SQL, with all the costs above. Prefer SQL UDFs for reusable business rules such as GST.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('pythonUDF.arrow.enabled: true', G), ('default since Spark 4.2', W)], size=7.6),
    term([('built-in  0.85 s', G), ('pickled   3.50 s', RD), ('Arrow     2.31 s', Y), ('pandas    2.10 s', Y)], size=7.6),
    term([('BatchEvalPython [band(amount)]', Y), ('Filter (pythonUDF0 = high)', W)], size=7.4),
    term([('UDF filter: PushedFilters: []', RD), ('4.09 s vs < 1 s', Y)], size=7.6),
    term([('None -> TypeError, job fails', RD), ('int UDF returns 472.5:', W), ('pickled None | Arrow 472', RD)], size=7.4),
]
B1 = [
    t(180, 14, 'Arrow transfer by default', 9.4, bold=True) + jvm_py(True) + cap('Batches instead of pickled rows.', '', 'green', y=144, h=30),
    t(180, 14, 'Each value makes a round trip', 9.4, bold=True) + jvm_py(False) + cap('Built-ins never leave the JVM.', '', 'amber', y=144, h=30),
    t(180, 14, 'Catalyst cannot see inside', 9.4, bold=True) + flow([('scan', '', 'card'), ('Python', 'band()', 'violet'), ('filter', 'after', 'amber')], y=50, w=96, gap=22) + cap('No rewrites around a black box.', '', 'amber', y=144, h=30),
    t(180, 14, 'Filters stay in Spark', 9.4, bold=True) + flow([('Parquet', 'all rows', 'acc'), ('UDF', 'every row', 'violet'), ('filter', '', 'card')], y=36, w=96, gap=22) + flow([('Parquet', 'pushed filter', 'green'), ('filter', '', 'green')], y=86, w=96, gap=22) + cap('Built-ins can be pushed down.', '', 'red', y=144, h=30),
    t(180, 14, 'Python semantics, Spark types', 9.4, bold=True) + opbox(20, 46, 'None', 'TypeError', 'acc', 100, 30) + opbox(140, 46, '472.5 → int', 'None (pickle)', 'acc', 100, 30) + opbox(260, 46, '472.5 → int', '472 (Arrow)', 'acc', 90, 30) + cap('Handle None; declare exact types.', '', 'red', y=144, h=30),
]
see_caps = ['Arrow is on for Python UDFs.', 'Built-in 4x faster than pickled UDF.', 'A Python node in the plan.', 'No pushdown through a UDF.', 'Crash on None; silent wrong types.']
behind_caps = ['Spark 4.2 default.', 'Serialisation and Python workers.', 'BatchEvalPython / ArrowEvalPython.', 'Opaque to the optimizer.', 'Python and Spark types differ.']
two = anim_two('UDFs', 'Your code inside Spark', 'Real lab outputs', 'JVM and Python', see, B1, see_caps, behind_caps)

# ---- scenario 1: replace a UDF
e1 = (t(180, 22, 'Nightly job with 12 UDFs', 9.4, bold=True) + t(180, 56, 'bands, cleaning, date parsing', 8.4, 'ink2') + cap('Runs 2 hours.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Most have built-in equivalents', 9.4, bold=True) + t(180, 56, 'when, regexp_replace, try_to_date', 8.4, 'ink', mono=True) + cap('Lessons 4.3, 6.4.', '', 'green', y=150, h=34))
e3 = (t(180, 22, 'Rewrite 10 of 12', 9.4, bold=True) + t(180, 56, 'Python step disappears from the plan', 8.4, 'ink2') + cap('Pushdown returns.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Remaining 2 → pandas UDF', 9.4, bold=True) + t(180, 56, 'vectorised with numpy', 8.4, 'ink2') + cap('Arrow batches.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Job: much faster', 9.4, 'acc', bold=True) + t(180, 56, 'our lab: 3.50 s → 0.85 s per label', 8.4, 'ink2') + cap('And fewer surprises.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Twelve UDFs in a nightly job',
              'Replacing UDFs with built-ins. (Typical; timings from our lab.)',
              'UDF replacement', 'Most UDFs have built-in equivalents; rewrite them, and vectorise the rest with pandas UDFs', [e1, e2, e3, e4, e5],
              ['Slow job.', 'Built-ins exist.', 'Rewrite.', 'Vectorise.', 'Faster.'],
              hid='scenario-replace-udf')

# ---- scenario 2: model scoring
b1 = (t(180, 22, 'Score 50M orders with a model', 9.4, bold=True) + t(180, 56, 'scikit-learn fraud model', 8.4, 'ink2') + cap('Python is required.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Row UDF calls predict per row', 9.4, bold=True) + t(180, 56, 'model.predict([[x]]) 50M times', 8.4, 'ink', mono=True) + cap('Hours.', '', 'red', y=150, h=34))
b3 = (t(180, 22, 'pandas UDF / mapInPandas', 9.4, bold=True) + t(180, 56, 'predict on 10,000 rows at once', 8.4, 'ink2') + cap('Vectorised.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Broadcast the model', 9.4, bold=True) + t(180, 56, 'load once per executor', 8.4, 'ink2') + cap('Lesson 3.2.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Write scores to a table', 9.4, 'acc', bold=True) + t(180, 56, 'not toPandas (Lesson 4.6)', 8.4, 'ink2') + cap('Stay distributed.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'A Python model on 50 million rows',
              'Vectorised UDFs for ML. (Typical.)',
              'pandas UDF scoring', 'Score Python models in batches with pandas UDFs or mapInPandas and a broadcast model', [b1, b2, b3, b4, b5],
              ['Model.', 'Row UDF.', 'Batches.', 'Broadcast.', 'Write out.'],
              hid='scenario-model-udf')

# ---- scenario 3: upgrade surprise
u1 = (t(180, 22, 'Upgrade to Spark 4.2', 9.4, bold=True) + t(180, 56, 'UDFs now Arrow-optimised', 8.4, 'ink2') + cap('No code change.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'A metric changes', 9.4, bold=True) + t(180, 56, 'was NULL, now a truncated number', 8.4, 'ink2') + cap('Return type mismatch.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'UDF declared int', 9.4, bold=True) + t(180, 56, 'returns float values', 8.4, 'ink2') + cap('None vs 472 in our lab.', '', 'red', y=150, h=34))
u4 = (t(180, 22, 'Fix the declaration', 9.4, bold=True) + t(180, 56, 'returnType="double" or round in code', 8.4, 'ink2') + cap('Exact types.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Test UDFs on upgrades', 9.4, 'acc', bold=True) + t(180, 56, 'compare outputs old vs new', 8.4, 'ink2') + cap('Lesson 11.4.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'An upgrade changed a number',
              'Arrow UDF type coercion. (Behaviour from our lab.)',
              'UDF return types', 'Mismatched UDF return types are coerced differently by pickled and Arrow UDFs; declare exact types and test on upgrades', [u1, u2, u3, u4, u5],
              ['Upgrade.', 'Changed.', 'Wrong type.', 'Fix.', 'Test.'],
              hid='scenario-udf-types')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Your code inside Spark</h2>
  <p>Left: real outputs. Right: what happens between the JVM and Python.</p>
''' + two + '''
  <p>Three live scenarios follow: a job with twelve UDFs, model scoring on 50 million rows, and an upgrade that changed a number.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>UDFs at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'ML', 12, 'blue', bold=True) + t(60, 58, 'scoring', 7.4, 'ink2'),
    '1. Model scoring',
    'Fraud and ETA models trained in Python score millions of orders with pandas UDFs.',
    ['Features', '*pandas UDF', 'Scores']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'rules', 12, 'green', bold=True) + t(60, 58, 'SQL UDF', 7.4, 'ink2'),
    '2. Shared business rules',
    'GST, delivery fee and band rules defined once as SQL UDFs and used by every team.',
    ['Rule', '*CREATE FUNCTION', 'Same everywhere']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'libs', 12, 'violet', bold=True) + t(60, 58, 'parsing', 7.4, 'ink2'),
    '3. Specialised libraries',
    'Address parsing, language detection or geohash libraries that have no Spark equivalent.',
    ['Text', '*Python library', 'Parsed fields']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'groups', 11, 'acc', bold=True) + t(60, 58, 'per city', 7.4, 'ink2'),
    '4. Per-group models',
    'applyInPandas fits a small forecasting model per city in parallel.',
    ['Group', '*applyInPandas', 'Forecasts']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'migrate', 10, 'acc', bold=True) + t(60, 58, 'cleanup', 7.4, 'ink2'),
    '5. UDF clean-up',
    'Platform teams replace legacy UDFs with built-ins during Spark upgrades.',
    ['Old UDFs', '*built-ins', 'Faster jobs']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> Arrow in <a href="../../04-dataframes/06-collect-topandas-and-arrow/">4.6</a>, built-in text and date functions in <a href="../04-string-and-date-functions/">6.4</a>.</p></div>
'''
EXTRA = ''
_x = os.path.join(HERE, '_extra.py')
if os.path.exists(_x): exec(open(_x).read())
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + EXTRA + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
