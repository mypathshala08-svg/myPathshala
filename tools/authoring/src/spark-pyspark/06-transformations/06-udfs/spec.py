import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='06-transformations', lesson='06-udfs', n='6.6',
    module_label='Module 6 · Transformations',
    title='UDFs',
    desc='User-defined functions in PySpark 4.3.0 on 5M orders: the same label as a built-in expression (0.85 s), a pickled Python UDF (3.50 s), an Arrow-optimised UDF (2.31 s, default since Spark 4.2) and a pandas UDF (2.10 s); BatchEvalPython in the plan; a UDF filter that disabled Parquet pushdown (4.09 s); a crash on None; a UDF declared int returning 472.5 giving None or 472 silently; and Spark 4 SQL UDFs with no Python step.',
    og_desc='Same label: built-in 0.85 s, Python UDF 3.50 s, and a UDF filter switched off Parquet pushdown. UDFs in PySpark 4, measured.',
    minutes=30, level='Intermediate',
    lead='When built-in functions are not enough, you can run your own Python code. This lesson compares built-ins with classic, Arrow-optimised and pandas UDFs on 5 million rows, shows what UDFs hide from the optimizer, the null and type traps, and Spark 4’s SQL UDFs. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', '4 implementations timed', 'Pushdown lost', 'Runs in your browser (Python)'],
)

MAIN = '''# Row-at-a-time vs batch processing (why pandas UDFs are faster)
import time
amounts = list(range(50, 950)) * 500             # 450,000 values

def band(a):
    return "high" if a >= 600 else "mid" if a >= 300 else "low"

t = time.time()
out1 = [band(a) for a in amounts]                # one call per value
t1 = time.time() - t

t = time.time()
cuts = {a: band(a) for a in set(amounts)}        # a "batch" trick: compute per distinct value
out2 = [cuts[a] for a in amounts]
t2 = time.time() - t
print(f"per row: {t1:.3f} s | batched: {t2:.3f} s | same: {out1 == out2}")
'''
RUN = dict(
    heading='Run the code: per-row calls cost time',
    intro='<p>A plain-Python illustration of why fewer, bigger calls are faster. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('out1 = [band(a) for a in amounts]                # one call per value', 'A classic Python UDF also pays serialisation per row.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Times are from your browser, not Spark.', code=None),
        dict(label='2 · Predict first: lab timings', hint='<b>Predict first:</b> how much slower was the pickled UDF than the built-in?',
             code='''builtin, pickled, arrow, pandas_udf = 0.85, 3.50, 2.31, 2.10
print(f"pickled {pickled / builtin:.1f}x, arrow {arrow / builtin:.1f}x, pandas {pandas_udf / builtin:.1f}x")
'''),
        dict(label='3 · Null-safe function', hint='Return None for None input.',
             code='''def band(a):
    if a is None:
        return None
    return "high" if a >= 600 else "mid" if a >= 300 else "low"
print([band(a) for a in (450, None, 700)])
'''),
        dict(label='4 · Declared types', hint='What should a UDF declared int return?',
             code='''value = 450 * 1.05
print(value, "-> declare double, or return round(value) for int")
'''),
        dict(label='5 · Spot the error', hint='This UDF only lowercases a string.', expect='error',
             code='''udf_body = "lambda s: s.lower()"
assert "lower" not in udf_body, "use F.lower(): built-in, no Python round trip, pushdown-friendly"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: UDFs',
    intro='<p>In the <code>pyspark</code> shell with pandas and PyArrow. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Arrow default', cmd='spark.conf.get("spark.sql.execution.pythonUDF.arrow.enabled")', file='pyspark',
             output="'true'", note='Spark 4.2+.'),
        dict(title='2 · Wrong return type', cmd='w = udf(lambda a: a * 1.05, "int", useArrow=True)\nspark.createDataFrame([(450,)], "amount INT").select(w("amount")).first()[0]', file='pyspark',
             output='472', note='None with useArrow=False.'),
        dict(title='3 · SQL UDF', cmd='spark.sql("CREATE OR REPLACE TEMPORARY FUNCTION gst(amount INT) RETURNS DOUBLE RETURN round(amount * 0.05, 2)")\nspark.sql("SELECT gst(530)").first()[0]', file='pyspark',
             output='26.5', note='Inlined, no Python.'),
    ],
)

TRACE = dict(
    heading='Where a UDF value travels',
    intro='<p>Follow one value through a Python UDF.</p>',
    code='''path = []
value = 450
path.append("JVM: read amount")
path.append("serialise to Python worker")
result = "mid" if 300 <= value < 600 else "other"
path.append("Python: band() -> " + result)
path.append("serialise back to JVM")
print(" -> ".join(path))
''',
    notes={4: 'Cost :: Every row crosses the process boundary (in batches with Arrow).', 7: 'Back :: Results return before any later filter runs.'},
)

WORKED_INTRO = 'Three UDF decisions at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='UDF · avoid', title='Replace a UDF with built-ins',
         problem='<p>Turn the band UDF into a built-in expression.</p>',
         inp='amount',
         approach=['when / otherwise.', 'Same thresholds.', 'Compare counts.'],
         code='''print("""band = (F.when(F.col("amount") >= 600, "high")
         .when(F.col("amount") >= 300, "mid").otherwise("low"))""")
''', notes={1: 'Lab :: 0.85 s instead of 3.50 s.'},
         tryit='Step 2.'),
    dict(level='i', tag='UDF · vectorise', title='A pandas UDF for a numpy formula',
         problem='<p>Compute a delivery-time score with numpy.</p>',
         inp='distance_km, prep_min',
         approach=['@pandas_udf("double").', 'Work on whole Series.', 'No Python loops.'],
         code='''import numpy as np
dist = np.array([2.0, 5.5, 10.0]); prep = np.array([10, 15, 20])
print(np.round(prep + dist * 3.2 + np.log1p(dist), 1))
''', notes={3: 'Vectorised :: One numpy call per batch.'},
         tryit='Step 2: pandas UDF 2.10 s.'),
    dict(level='a', tag='UDF · governance', title='One GST rule for all teams',
         problem='<p>Make the GST calculation reusable and fast.</p>',
         inp='SQL and Python users',
         approach=['SQL UDF in the catalog.', 'No Python step.', 'Document and test it.'],
         code='''print("CREATE FUNCTION finance.gst(amount INT) RETURNS DOUBLE RETURN round(amount * 0.05, 2)")
''', notes={1: 'Inlined :: Runs like a built-in expression.'},
         tryit='Step 6.'),
]

QUIZ = mix([
    dict(q='Beginner: Where does a Python UDF run?', options=['In the JVM', 'In Python worker processes', 'On the driver only', 'In the database'], answer=1,
         why='Data travels there and back.'),
    dict(q='Beginner: First choice before writing a UDF?', options=['pandas UDF', 'Built-in functions', 'RDDs', 'collect()'], answer=1,
         why='0.85 s vs 3.50 s.'),
    dict(q='Beginner: What does a pandas UDF receive?', options=['One value', 'A pandas Series batch', 'A whole table', 'A Row'], answer=1,
         why='Vectorised.'),
    dict(q='Intermediate: Default for pythonUDF.arrow.enabled in 4.3?', options=['false', 'true', 'auto', 'not set'], answer=1,
         why='Since 4.2.'),
    dict(q='Intermediate: What appears in the plan for a Python UDF?', options=['HashAggregate', 'BatchEvalPython / ArrowEvalPython', 'Exchange', 'Sort'], answer=1,
         why='A Python evaluation node.'),
    dict(q='Intermediate: Can a filter on a UDF be pushed to Parquet?', options=['Yes', 'No', 'Only for ORC', 'Only with Arrow'], answer=1,
         why='PushedFilters: [].'),
    dict(q='Advanced: A UDF declared int returns 472.5 with Arrow. Result?', options=['Error', '472', '472.5', 'None'], answer=1,
         why='None with pickling.'),
    dict(q='Advanced: How does a SQL UDF run?', options=['In Python', 'Inlined as an expression', 'On the driver', 'As a UDTF'], answer=1,
         why='No Python step in the plan.'),
])

REVISION = [
    'Built-ins first: 0.85 s vs Python UDF 3.50 s on 5M rows.',
    'Arrow-optimised Python UDFs are the default since 4.2 (2.31 s); pandas UDFs vectorise (2.10 s).',
    'UDFs are black boxes: BatchEvalPython in the plan, <b>no pushdown</b> (4.09 s).',
    'Handle <code>None</code>; a crash in Python fails the job.',
    'Declare exact return types: 472.5 as int → None (pickle) or 472 (Arrow).',
    'SQL UDFs (Spark 4) are inlined: no Python step.',
    'For models: pandas UDF / mapInPandas with a broadcast model.',
]
FAQ = [
    ('Are Scala/Java UDFs faster?', 'Yes, they run in the JVM without serialisation, but they are still opaque to Catalyst. Built-ins remain best.'),
    ('Can a UDF return a struct or array?', 'Yes; declare the type, e.g. "struct&lt;band:string,score:double&gt;" or "array&lt;string&gt;".'),
    ('How do I mark a UDF non-deterministic?', '<code>udf(...).asNondeterministic()</code>, so Spark does not assume it can call it any number of times with the same result.'),
    ('Do UDFs work with Spark Connect?', 'Yes; Python UDFs are sent to the server and run in its Python workers. Dependencies must be available there.'),
    ('What is a Python UDTF?', 'A table function (Spark 3.5+) that returns zero or more rows per input, decorated with @udtf; useful for splitting or expanding records.'),
]

PRACTICE_INTRO = 'Programs about UDF design and cost.'
PROBLEMS = [
    dict(level='easy', title='Slowdown', stmt='How many times slower is the pickled UDF?', inp='3.50 vs 0.85 s',
         code='''print(round(3.50 / 0.85, 1))
''', explain='About 4x.'),
    dict(level='easy', title='Band', stmt='Band for an amount.', inp='450',
         code='''a = 450
print("high" if a >= 600 else "mid" if a >= 300 else "low")
''', explain='when/otherwise in Spark.'),
    dict(level='easy', title='GST', stmt='GST via the SQL UDF formula.', inp='530',
         code='''print(round(530 * 0.05, 2))
''', explain='26.5.'),
    dict(level='medium', title='Null safety', stmt='Apply a function that skips None.', inp='[450, None, 700]',
         code='''f = lambda a: None if a is None else a * 2
print([f(a) for a in [450, None, 700]])
''', explain='Handle None first.'),
    dict(level='medium', title='Vectorised', stmt='Bands for a numpy array.', inp='amounts',
         code='''import numpy as np
a = np.array([120, 450, 700])
print(np.where(a >= 600, "high", np.where(a >= 300, "mid", "low")))
''', explain='pandas UDF style.'),
    dict(level='medium', title='Type check', stmt='Detect values that do not fit int.', inp='[472.5, 300.0]',
         code='''print([v for v in [472.5, 300.0] if v != int(v)])
''', explain='Declare double instead.'),
    dict(level='business', title='Nightly savings', stmt='Minutes saved per night replacing 10 UDF columns.', inp='2.65 s saved per column per 5M rows, 40 × 5M rows',
         code='''print(round(2.65 * 10 * 40 / 60, 1), "minutes")
''', explain='Built-ins add up.'),
    dict(level='business', title='Scoring batches', stmt='predict() calls for 50M rows.', inp='row UDF vs batches of 10,000',
         code='''print("row:", 50_000_000, "| batched:", 50_000_000 // 10_000)
''', explain='pandas UDF.'),
]

SCN_INTRO = 'UDF questions test whether you know what makes PySpark fast or slow.'
SCENARIOS = (
    scn('Any company · PySpark', 'Fresher', '“What is a UDF?”',
        'Explain UDFs and when to use them.',
        'basics and costs?',
        '<p>A user-defined function runs custom logic on columns. Python UDFs run in Python workers, so data is serialised back and forth and Catalyst cannot optimise them. I use built-in functions first, pandas UDFs for vectorisable Python, and SQL UDFs for reusable expressions.</p>', '“UDFs are the normal way to transform data.”') +
    scn('Data engineering', 'Mid-level', 'Slow job with UDFs',
        'A job with several Python UDFs is slow. What do you do?',
        'optimisation?',
        '''<ul>
          <li>Replace UDFs with built-ins where possible (when, regexp, try_to_date…).</li>
          <li>Vectorise the rest as pandas UDFs; keep Arrow enabled.</li>
          <li>Check the plan for BatchEvalPython and lost pushdown.</li>
        </ul>''', 'Adding executors.') +
    scn('Data engineering', 'Mid-level', 'UDF returns nulls',
        'A UDF sometimes returns null or wrong numbers.',
        'type awareness?',
        '''<ol>
          <li>Check None handling in the function.</li>
          <li>Check declared return type vs returned values (472.5 as int).</li>
          <li>Pickled vs Arrow UDFs coerce differently; test after upgrades.</li>
        </ol>''', 'Wrapping everything in try/except returning None.') +
    scn('ML platform', 'Senior', 'Scoring at scale',
        'Score a scikit-learn model on 50M rows nightly.',
        'vectorisation and distribution?',
        '''<ul>
          <li>Broadcast the model; pandas UDF or mapInPandas predicting per batch.</li>
          <li>Tune Arrow batch size; write results to a table.</li>
          <li>Never toPandas the full data set.</li>
        </ul>''', 'A row UDF calling predict per row.')
)
