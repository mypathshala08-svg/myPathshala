import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='04-dataframes', lesson='06-collect-topandas-and-arrow', n='4.6',
    module_label='Module 4 · DataFrames',
    title='collect, toPandas and Arrow',
    desc='Bringing Spark data into Python with PySpark 4.3.0: first, take, tail, collect and toLocalIterator; one million rows timed with collect (8.4 s), toPandas without Arrow (9.9 s) and with Arrow (1.4 s), and the new toArrow (0.65 s); Arrow enabled by default since Spark 4.2; an INT column with a null turning into float64; pandas back to Spark 11.8 s vs 2.6 s; and spark.driver.maxResultSize stopping a 5-million-row collect before the driver ran out of memory.',
    og_desc='toPandas on 1M rows: 9.9 s without Arrow, 1.4 s with it. And maxResultSize stopped a 5M-row collect. collect, toPandas and Arrow, measured.',
    minutes=30, level='Intermediate',
    lead='Sooner or later you need Spark data in plain Python: for a chart, a model or an API. This lesson shows every way to bring rows to the <b>driver</b>, how <b>Apache Arrow</b> speeds up pandas conversion, how types change on the way, and how to avoid crashing the driver. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0 + pandas 3', 'Arrow on vs off timed', 'maxResultSize triggered', 'Runs in your browser (Python)'],
)

MAIN = '''# Will this fit on the driver? A quick estimate before collect()/toPandas()
rows = 5_000_000
bytes_per_row_arrow = 44          # ~42 MiB per 1M rows in our toArrow() test
python_overhead = 8               # Row objects cost far more than columnar data

arrow_mib = rows * bytes_per_row_arrow / 2**20
rows_mib = arrow_mib * python_overhead
limit_mib = 1024                  # spark.driver.maxResultSize default (1g)

print(f"as Arrow    : {arrow_mib:,.0f} MiB")
print(f"as Row objs : ~{rows_mib:,.0f} MiB")
print("fits under maxResultSize:", arrow_mib < limit_mib)
'''
RUN = dict(
    heading='Run the code: will it fit?',
    intro='<p>A rough sizing model before you call <code>toPandas</code>. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('bytes_per_row_arrow = 44          # ~42 MiB per 1M rows in our toArrow() test', 'Six columns of orders; your rows may be wider.'),
        ('python_overhead = 8               # Row objects cost far more than columnar data', 'A rough factor for illustration, not a measured constant.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then try 50 million rows.', code=None),
        dict(label='2 · Predict first: Arrow speed-up', hint='<b>Predict first:</b> how many times faster was toPandas with Arrow?',
             code='''no_arrow, arrow = 9.89, 1.42
print(f"{no_arrow / arrow:.1f}x faster")
'''),
        dict(label='3 · int with null', hint='What pandas does with a missing integer.',
             code='''vals = [450, None]
as_float = [float(v) if v is not None else float("nan") for v in vals]
print(as_float)
'''),
        dict(label='4 · Aggregate first', hint='Rows to bring back after groupBy city.',
             code='''rows, cities = 5_000_000, 8
print("collect all:", rows, "| after groupBy:", cities)
'''),
        dict(label='5 · Spot the error', hint='This config “fixes” a maxResultSize failure.', expect='error',
             code='''conf = {"spark.driver.maxResultSize": "0"}
assert conf["spark.driver.maxResultSize"] != "0", "0 means unlimited: the driver will crash instead; fix the collect"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: Arrow and the driver',
    intro='<p>In the <code>pyspark</code> shell with pandas and PyArrow installed. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Is Arrow on?', cmd='spark.conf.get("spark.sql.execution.arrow.pyspark.enabled")', file='pyspark',
             output="'true'", note='Default since Spark 4.2.'),
        dict(title='2 · An int with a null', cmd='spark.createDataFrame([(1, 450), (2, None)], "id INT, amount INT").toPandas().amount.dtype', file='pyspark',
             output="dtype('float64')", note='450 becomes 450.0.'),
        dict(title='3 · Too much for the driver', cmd='big.collect()      # with spark.driver.maxResultSize=50m', file='pyspark',
             output='Total size of serialized results of 1 tasks (63.9 MiB) is bigger than spark.driver.maxResultSize (50.0 MiB)', note='The job is aborted, the driver survives.'),
    ],
)

TRACE = dict(
    heading='Rows vs Arrow batches',
    intro='<p>Count how many conversions happen in each path.</p>',
    code='''rows, batch = 1_000_000, 10_000
row_path = rows                  # one conversion per row
arrow_path = rows // batch       # one per batch of 10,000
print("row path  :", row_path, "conversions")
print("arrow path:", arrow_path, "batches")
''',
    notes={2: 'Rows :: Each row becomes a Python object.', 3: 'Arrow :: maxRecordsPerBatch = 10,000 in our defaults.'},
)

WORKED_INTRO = 'Three driver-side tasks done safely.'
EXAMPLES = [
    dict(level='b', tag='Driver · basics', title='Chart daily revenue',
         problem='<p>Plot revenue per day for October without crashing the driver.</p>',
         inp='orders_big',
         approach=['Filter and groupBy in Spark.', 'toPandas on ~31 rows.', 'Plot in pandas.'],
         code='''print("""pdf = (orders.where("order_date >= '2026-10-01'")
             .groupBy("order_date").agg(F.sum("amount").alias("revenue"))
             .orderBy("order_date").toPandas())
pdf.plot(x="order_date", y="revenue")""")
''', notes={2: 'Small :: Only one row per day reaches the driver.'},
         tryit='Step 6: aggregate first.'),
    dict(level='i', tag='Driver · types', title='Keep integers integers',
         problem='<p>Convert to pandas without turning amount into floats.</p>',
         inp='amount INT with nulls',
         approach=['Fill or keep nulls deliberately.', 'Convert to nullable Int64 in pandas.', 'Check dtypes.'],
         code='''print("""pdf = df.toPandas()
pdf["amount"] = pdf["amount"].astype("Int64")   # nullable integer""")
''', notes={2: 'Nullable :: pandas Int64 (capital I) keeps missing values as &lt;NA&gt;.'},
         tryit='Step 4: float64 by default.'),
    dict(level='a', tag='Driver · streaming out', title='Send rows to an API',
         problem='<p>Push 2M rows to a partner API from Python.</p>',
         inp='DataFrame of notifications',
         approach=['toLocalIterator, not collect.', 'Batch the requests.', 'Or foreachPartition on executors.'],
         code='''rows = list(range(7))          # stands for: df.toLocalIterator()
size = 3
batches = [rows[i:i + size] for i in range(0, len(rows), size)]
print(len(batches), "requests:", batches)
''', notes={1: 'Memory :: The driver holds one partition at a time.'},
         tryit='foreachPartition sends from executors in parallel.'),
]

QUIZ = mix([
    dict(q='Beginner: Where do collect() results go?', options=['Executors', 'The driver process', 'HDFS', 'A temp view'], answer=1,
         why='One Python process.'),
    dict(q='Beginner: Which is safest for peeking at data?', options=['collect()', 'toPandas()', 'take(5)', 'toArrow()'], answer=2,
         why='Only 5 rows.'),
    dict(q='Beginner: Is Arrow on by default in Spark 4.3?', options=['No', 'Yes, since 4.2', 'Only on Databricks', 'Only for UDFs'], answer=1,
         why='arrow.pyspark.enabled = true.'),
    dict(q='Intermediate: How much faster was toPandas with Arrow on 1M rows?', options=['Same', 'About 7x', '100x', 'Slower'], answer=1,
         why='9.9 s → 1.4 s.'),
    dict(q='Intermediate: An INT column with a null becomes in pandas…', options=['int64', 'float64', 'object', 'string'], answer=1,
         why='NaN needs floats.'),
    dict(q='Intermediate: What does toLocalIterator() keep in driver memory?', options=['All rows', 'One partition at a time', 'Nothing', 'One row'], answer=1,
         why='Good for streaming rows out.'),
    dict(q='Advanced: What does spark.driver.maxResultSize do?', options=['Limits executor memory', 'Aborts jobs whose collected results exceed it', 'Sets Arrow batch size', 'Limits shuffle'], answer=1,
         why='63.9 MiB > 50 MiB → aborted.'),
    dict(q='Advanced: What does toArrow() return (Spark 4.0+)?', options=['pandas DataFrame', 'PyArrow Table', 'list of Row', 'RDD'], answer=1,
         why='0.65 s, 42 MiB in our test.'),
])

REVISION = [
    '<code>first</code>/<code>head</code>/<code>take</code>/<code>tail</code>: a few Rows; <code>collect()</code>: all Rows; <code>toLocalIterator()</code>: a partition at a time.',
    'Everything you collect lands in the <b>driver</b>: aggregate or filter in Spark first.',
    'Arrow is on by default since 4.2; 1M rows: toPandas 9.9 s → 1.4 s; <code>toArrow()</code> 0.65 s.',
    'pandas → Spark: 11.8 s → 2.6 s with Arrow; for big data use pandas UDFs.',
    'Types change: INT with null → <code>float64</code>; dates → object; decimals → Decimal objects.',
    '<code>spark.driver.maxResultSize</code> (1g) aborts oversized collects; keep it.',
    'Large outputs: write files or tables, not collect.',
]
FAQ = [
    ('Is toPandas distributed?', 'No. The executors compute the DataFrame, but the result is assembled in the driver. Use the pandas API on Spark (pyspark.pandas) for distributed pandas-like code.'),
    ('What is the pandas API on Spark?', '<code>import pyspark.pandas as ps</code> gives a pandas-like API that runs on Spark, distributed. It is useful for porting pandas code; plain DataFrames are usually faster.'),
    ('Why do I see an Arrow fallback warning?', 'A column type was not supported by the Arrow path, so Spark used the slow row path. Cast that column or accept the slower conversion.'),
    ('Should I raise spark.driver.memory?', 'Only when the driver legitimately needs it (broadcasts, large plans, modest collects). It does not make collecting big data a good idea.'),
    ('Does Spark Connect support toPandas?', 'Yes; results stream to the client in Arrow batches. The same size limits apply on the client side.'),
]

PRACTICE_INTRO = 'Programs about sizes, speed-ups and safe collection.'
PROBLEMS = [
    dict(level='easy', title='Speed-up', stmt='Arrow speed-up for pandas → Spark.', inp='11.82 s vs 2.58 s',
         code='''print(f"{11.82 / 2.58:.1f}x")
''', explain='Arrow helps both directions.'),
    dict(level='easy', title='Arrow size', stmt='MiB per million rows in Arrow.', inp='42 MiB for 1M rows',
         code='''print(42 / 1, "MiB per million rows")
''', explain='Useful for sizing collects.'),
    dict(level='easy', title='Over the limit', stmt='By how much did the result exceed the limit?', inp='63.9 vs 50 MiB',
         code='''print(round(63.9 - 50, 1), "MiB")
''', explain='The job was aborted.'),
    dict(level='medium', title='Fits?', stmt='Can 30M rows be collected under 1 GiB as Arrow?', inp='42 MiB per 1M rows',
         code='''mib = 30 * 42
print(mib, "MiB ->", "fits" if mib < 1024 else "too big")
''', explain='And Python objects are bigger still.'),
    dict(level='medium', title='Nullable ints', stmt='Keep ints with missing values as integers.', inp='[450, None, 380]',
         code='''vals = [450, None, 380]
print([v if v is not None else "<NA>" for v in vals])
''', explain='pandas Int64 shows &lt;NA&gt;.'),
    dict(level='medium', title='Batches', stmt='Arrow batches for 1M rows.', inp='maxRecordsPerBatch 10,000',
         code='''print(1_000_000 // 10_000)
''', explain='One conversion per batch, not per row.'),
    dict(level='business', title='Hourly saving', stmt='Seconds saved per day by enabling Arrow for an hourly round trip.', inp='(9.89 + 11.82) − (1.42 + 2.58), 24 runs',
         code='''print(round(((9.89 + 11.82) - (1.42 + 2.58)) * 24), "s per day")
''', explain='About 7 minutes a day.'),
    dict(level='business', title='Report rows', stmt='Rows in a city × day revenue report for October.', inp='8 cities, 31 days',
         code='''print(8 * 31)
''', explain='Tiny: safe for toPandas.'),
]

SCN_INTRO = 'Driver-side questions reveal whether you have crashed a driver before.'
SCENARIOS = (
    scn('Any company · PySpark', 'Fresher', '“collect vs take?”',
        'What is the difference between collect() and take(n)?',
        'do you know driver limits?',
        '<p><code>collect()</code> brings every row to the driver; <code>take(n)</code> brings only n rows and can stop early. On big data collect can exhaust driver memory or hit maxResultSize; I use take, show or limit to look at data, and collect only small, aggregated results.</p>', '“collect is fine, Spark is distributed.”') +
    scn('Data engineering', 'Mid-level', 'toPandas is slow',
        'toPandas of a few million rows takes a minute.',
        'do you know Arrow?',
        '''<ul>
          <li>Check spark.sql.execution.arrow.pyspark.enabled (true by default since 4.2).</li>
          <li>Look for fallback warnings from unsupported types.</li>
          <li>Reduce rows and columns first; my test: 9.9 s → 1.4 s for 1M rows with Arrow.</li>
        </ul>''', 'Raising driver memory only.') +
    scn('Data engineering', 'Mid-level', 'maxResultSize error',
        'A job fails with “Total size of serialized results … bigger than spark.driver.maxResultSize”.',
        'do you fix causes, not limits?',
        '''<ol>
          <li>Find the collect/toPandas (or a large broadcast).</li>
          <li>Aggregate, filter, or write output instead.</li>
          <li>Raise the limit only for a known, bounded result.</li>
        </ol>''', 'Setting it to 0.') +
    scn('ML platform', 'Senior', 'pandas models on big data',
        'Data scientists score with scikit-learn via toPandas on 50M rows.',
        'can you scale Python safely?',
        '''<ul>
          <li>Broadcast the model and score with a pandas UDF or mapInPandas on executors.</li>
          <li>Arrow batches keep conversion fast.</li>
          <li>Write results to a table; collect only metrics.</li>
        </ul>''', 'A bigger driver machine.')
)
