import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l46_collect.txt'
def sec(a, b=None, drop=()):
    s = capsec(C, a, b, drop)
    return '\n'.join(l if len(l) <= 140 else l[:137] + ' …' for l in s.split('\n'))

def jvm_py(mode='rows', hi=None):
    """executors (JVM) -> driver JVM -> Python driver, with rows or Arrow batches"""
    o = ''
    for k in range(2):
        o += opbox(8, 30 + k * 48, f'Executor {k + 1}', 'JVM', 'card', 90, 32)
    o += opbox(140, 50, 'Driver JVM', 'collects', 'violet' if hi == 'jvm' else 'card', 90, 34)
    o += opbox(266, 50, 'Python', 'your process', 'blue' if hi == 'py' else 'card', 88, 34)
    for k in range(2):
        o += arrow(98, 46 + k * 48, 140, 67, 'ink3', 1.0)
    if mode == 'rows':
        o += ''.join(box(236 + k * 7, 92 + (k % 2) * 6, 5, 5, 'amber', rx=1) for k in range(4)) + t(248, 116, 'row by row', 6.8, 'amber')
    else:
        o += box(238, 94, 22, 14, 'green', rx=2) + t(249, 120, 'columnar batches', 6.8, 'green')
    o += arrow(230, 67, 266, 67, 'ink3', 1.2)
    return o

# ---------------------------------------------------------------- story
sc_ = (jvm_py('arrow', 'py') +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured (1M rows)', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('collect()           : 8.4 s', 'amber'), ('toPandas, no Arrow : 9.9 s', 'red'),
           ('toPandas, Arrow    : 1.4 s', 'green'), ('toArrow()          : 0.65 s', 'green'),
           ('int with null -> float64', 'amber'), ('5M collect: maxResultSize stop', 'red')])))
scene_svg = scene('collect, toPandas and toArrow bring distributed data into one Python process on the driver. We timed them on a million orders with and without Apache Arrow, and collected 5 million rows into a small driver limit.', sc_,
                  'Bring <tspan font-weight="700" class="s-acc">results</tspan> to the driver, not <tspan font-weight="700" class="s-acc">data</tspan>; Arrow makes the trip 7x faster.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“It worked on the sample”</h2>
  <div class="story">
    <p class="narration">Riya built a chart in her notebook with <code>orders.toPandas()</code> on a 10,000-row sample. In production the same line ran on the whole table. The driver ran out of memory, the notebook kernel died, and the scheduled report never arrived.</p>

{scene_svg}

R> Sir, toPandas is the easiest way to plot. Is it forbidden?
A> Not forbidden, just <b>dangerous on big data</b>. <code>collect</code> and <code>toPandas</code> copy every row into the single driver process. Aggregate in Spark first, then bring the small result to pandas.
K> I read that Arrow makes it faster. Do we need to switch it on?
A> Since Spark 4.2 it is on by default. Today we look at every way to bring rows to the driver, time collect and toPandas with and without Arrow, see how types change on the way, go back from pandas to Spark, and let the driver’s safety limit stop a 5-million-row collect. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Bringing data to the driver at three levels
L1> A warehouse and one desk
      <ul>
        <li>The cluster is a warehouse; the driver is one office desk. You can bring a summary sheet to the desk, not the whole warehouse.</li>
        <li><code>take(5)</code> is asking for five boxes; <code>collect()</code> is asking for every box.</li>
        <li>Arrow is moving boxes on pallets instead of one by one.</li>
      </ul>
L2> The API
      <ul>
        <li>To Python objects: <code>first</code>, <code>head(n)</code>, <code>take(n)</code>, <code>tail(n)</code>, <code>collect()</code> (list of Row), <code>toLocalIterator()</code> (one partition at a time).</li>
        <li>To pandas and Arrow: <code>toPandas()</code>, <code>toArrow()</code> (Spark 4.0+); back: <code>spark.createDataFrame(pdf)</code>.</li>
        <li>Settings: <code>spark.sql.execution.arrow.pyspark.enabled</code> (true since 4.2), <code>…fallback.enabled</code>, <code>spark.driver.maxResultSize</code> (1g), <code>spark.driver.memory</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>1M rows: <code>collect</code> 8.4 s; <code>toPandas</code> 9.9 s without Arrow, 1.4 s with Arrow; <code>toArrow</code> 0.65 s.</li>
        <li>An integer column with a null became <code>float64</code> in pandas (450 → 450.0, None → NaN).</li>
        <li><code>createDataFrame(pandas)</code> of 1M rows: 11.8 s without Arrow, 2.6 s with. A 5M-row collect stopped at <code>maxResultSize</code> (63.9 MiB &gt; 50 MiB).</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Moving data between Spark and Python</h2>
''' + def_block(
    'Actions such as <code>collect()</code>, <code>take(n)</code> and <code>toPandas()</code> transfer the rows of a distributed DataFrame from the executors to the <b>driver</b>, where they are materialised in the Python process: as a list of <code>Row</code> objects, a pandas DataFrame, or (with <code>toArrow()</code>, Spark 4.0+) a PyArrow Table. The data must fit in driver memory; <code>spark.driver.maxResultSize</code> (default 1g) aborts jobs whose serialized results exceed the limit. <b>Apache Arrow</b> is a columnar in-memory format that PySpark uses to transfer data in batches between the JVM and Python without per-row serialization, for <code>toPandas</code>, <code>createDataFrame</code> from pandas, and pandas UDFs. It is controlled by <code>spark.sql.execution.arrow.pyspark.enabled</code>, enabled by default since Spark 4.2, with automatic fallback to the row-based path when a type is not supported.',
    'collect and toPandas copy the data from all machines into your one Python program. That is fine for small results and dangerous for big tables. Arrow is a fast format for moving columns between Spark and pandas; in Spark 4.2 and later it is used automatically.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Driver', 'The single process that runs your Python code.'),
    ('collect()', 'All rows to the driver as Row objects.'),
    ('take(n) / head(n)', 'Only the first n rows.'),
    ('toLocalIterator()', 'Rows one partition at a time.'),
    ('toPandas()', 'All rows into a pandas DataFrame.'),
    ('Apache Arrow', 'Columnar memory format for fast transfer.'),
    ('toArrow()', 'All rows into a PyArrow Table (4.0+).'),
    ('maxResultSize', 'Driver’s limit for collected results.'),
]) + '''

  <h3>Which one to use?</h3>
''' + table(['Need', 'Use', 'Lab'], [
    ['Look at a few rows', '<code>show()</code>, <code>take(5)</code>, <code>first()</code>', 'instant'],
    ['The last rows', '<code>tail(n)</code>', 'tail(1): 5999999'],
    ['A small result for Python code', '<code>collect()</code> after aggregation', '8 city rows'],
    ['A chart or pandas analysis', '<code>toPandas()</code> after aggregation', '1M rows: 1.4 s with Arrow'],
    ['Arrow-native tools (DuckDB, Polars)', '<code>toArrow()</code>', '0.65 s, 42 MiB'],
    ['Stream all rows through Python', '<code>toLocalIterator()</code>', 'one partition in memory at a time'],
    ['Big output', 'Write a file or table', 'Module 5'],
], minw=640) + lv + '''
EXAM> “Why avoid collect() on large DataFrames?” It moves every row to the single driver process; the driver can run out of memory or hit <code>spark.driver.maxResultSize</code>, and all parallelism is lost. Aggregate or filter in Spark first, use <code>take</code>/<code>limit</code> to look at samples, and write large results to storage.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>How types change on the way to pandas</h2>
''' + table(['Spark type', 'pandas dtype (Arrow)', 'Watch out'], [
    ['<code>int</code> / <code>bigint</code>', '<code>int32</code> / <code>int64</code>', 'With a null: <b>float64</b>, null → NaN'],
    ['<code>double</code>', '<code>float64</code>', 'null → NaN'],
    ['<code>string</code>', 'string (<code>str</code>)', 'null → None/NaN'],
    ['<code>date</code>', '<code>object</code> (Python dates)', 'Convert with <code>pd.to_datetime</code> if needed'],
    ['<code>timestamp</code>', '<code>datetime64</code>', 'Shown in the session time zone, without tz info'],
    ['<code>decimal</code>', '<code>object</code> (Decimal)', 'Slow in pandas; cast if exactness is not needed'],
    ['<code>array</code> / <code>struct</code> / <code>map</code>', 'NumPy arrays / dicts / lists', 'Unsupported types fall back to the slow row path'],
], minw=640) + '''
WARN> A notebook sample hides the problem. Code that calls <code>toPandas()</code> or <code>collect()</code> must be reviewed for the <b>size of what it brings back</b>. Put the aggregation, filter or <code>limit</code> in Spark, right before the call, and keep <code>spark.driver.maxResultSize</code> at a safe value so a mistake fails fast instead of killing the driver.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>From the cluster to pandas and back</h2>
  <p>All outputs are real: PySpark 4.3.0 with pandas 3.0 and PyArrow 26, local mode, driver memory 2 GB, <code>orders_big</code> (5M rows). Timings vary by a second or two between runs.</p>
''' + stepper([
    ('Step 1 · The defaults',
     code('python', 'l46_collect.py', 'for k in ("spark.sql.execution.arrow.pyspark.enabled",\n          "spark.sql.execution.arrow.pyspark.fallback.enabled",\n          "spark.sql.execution.arrow.maxRecordsPerBatch"):\n    print(k, spark.conf.get(k))\nspark.sparkContext.getConf().get("spark.driver.maxResultSize", "(not set: 1g)")', sec('== 1)', '== 2)')),
     'Arrow is <b>on</b> by default: the PySpark 4.2 migration guide changed <code>arrow.pyspark.enabled</code> to true. If a type cannot be converted, Spark falls back to the slow path instead of failing. Arrow batches hold 10,000 records. The driver accepts up to 1 GB of collected results unless configured otherwise.'),
    ('Step 2 · Small amounts of data',
     code('python', 'l46_collect.py', 'd = big.orderBy("order_id")\nd.first(); d.head(2); d.take(2); d.tail(1)\nd.limit(3).collect()\nit = big.toLocalIterator(); next(it)', sec('== 2)', '== 3)')),
     '<code>first</code>, <code>head</code>, <code>take</code> and <code>tail</code> return a few <code>Row</code> objects. <code>collect()</code> returns a Python list of Rows, all of them. <code>toLocalIterator()</code> fetches one partition at a time, so the driver holds only the largest partition, not the whole DataFrame: useful to stream rows into another system from Python.'),
    ('Step 3 · One million rows: collect, toPandas, toArrow',
     code('python', 'l46_collect.py', 'm = big.limit(1_000_000).cache(); m.count()\nrows = m.collect()\nfor arrow in ("false", "true"):\n    spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", arrow)\n    pdf = m.toPandas()\ntbl = m.toArrow()', sec('== 3)', '== 4)')),
     '<code>collect()</code> created a million Python <code>Row</code> objects: 8.4 s. <code>toPandas</code> without Arrow went through the same rows: 9.9 s. With Arrow the data crossed as <b>columnar batches</b>: <b>1.4 s, 7x faster</b>. <code>toArrow()</code>, new in Spark 4.0, skipped pandas entirely: 0.65 s and 42 MiB, half the pandas size, ready for DuckDB or Polars.'),
    ('Step 4 · An int with a null becomes a float',
     code('python', 'l46_collect.py', 'n = spark.createDataFrame([(1, 450), (2, None)], "id INT, amount INT")\nfor arrow in ("false", "true"):\n    spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", arrow)\n    p = n.toPandas(); print(p.amount.dtype, p.amount.tolist())', sec('== 4)', '== 5)')),
     'pandas’ classic <code>int64</code> cannot hold a missing value, so both paths turned the column into <code>float64</code>: 450 became 450.0 and null became NaN. Code that checks <code>dtype == int</code> or writes the data back can break. Fill or cast before converting, or convert to nullable <code>Int64</code> in pandas.'),
    ('Step 5 · pandas back to Spark',
     code('python', 'l46_collect.py', 'pdf = pd.DataFrame({"id": np.arange(1_000_000), "amount": rng.integers(50, 900, 1_000_000)})\nfor arrow in ("false", "true"):\n    spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", arrow)\n    s = spark.createDataFrame(pdf); s.count()', sec('== 5)', '== 6)')),
     'Going the other way, Arrow cut 11.8 s to <b>2.6 s</b>. This matters when a Python model scores data in pandas and the results go back into a Spark table. For big data, though, prefer pandas UDFs (Lesson 6.6), which run pandas code <b>on the executors</b> in parallel.'),
    ('Step 6 · The driver’s safety limit',
     code('python', 'l46_collect.py', 'spark = SparkSession.builder.config("spark.driver.maxResultSize", "50m").getOrCreate()\nbig.collect()                     # 5 million rows\nbig.groupBy("city").agg(F.sum("amount").alias("rev")).toPandas()', sec('== 6)')),
     'Collecting 5 million rows failed after 1.1 s: the serialized result of one task, 63.9 MiB, was bigger than the 50 MiB limit, and Spark aborted the job <b>before</b> the driver could run out of memory. That is what <code>maxResultSize</code> is for; do not raise it to “fix” a collect. The right fix is on the last line: aggregate first, then bring back 8 rows.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('arrow.pyspark.enabled : true', G), ('fallback.enabled      : true', W), ('maxResultSize         : 1g', W)], size=7.6),
    term([('first(), take(2), tail(1)', W), ('collect(): list of Row', Y), ('toLocalIterator: 1 partition', G)], size=7.6),
    term([('collect()       : 8.37 s', Y), ('toPandas no Arrow: 9.89 s', RD), ('toPandas Arrow   : 1.42 s', G), ('toArrow()        : 0.65 s', G)], size=7.4),
    term([('INT [450, null] -> pandas', W), ('dtype float64', Y), ('[450.0, nan]', Y)], size=7.6),
    term([('collect 5M rows:', W), ('63.9 MiB > maxResultSize 50 MiB', RD), ('aggregate first: (8, 2)', G)], size=7.4),
]
B1 = [
    t(180, 14, 'Arrow on by default (4.2+)', 9.4, bold=True) + jvm_py('arrow') + cap('Columnar transfer, row fallback.', '', 'green', y=144, h=30),
    t(180, 14, 'Everything lands in one process', 9.4, bold=True) + jvm_py('rows', 'py') + cap('Bring small results only.', '', 'blue', y=144, h=30),
    t(180, 14, 'Rows vs columnar batches', 9.4, bold=True) + jvm_py('arrow', 'jvm') + cap('7x faster to pandas.', '', 'green', y=144, h=30),
    t(180, 14, 'pandas int cannot hold null', 9.4, bold=True) + flow([('INT', '450, null', 'card'), ('pandas', 'int64?', 'amber'), ('float64', '450.0, NaN', 'acc')], y=50, w=96, gap=22) + cap('Types change on the way.', '', 'amber', y=144, h=30),
    t(180, 14, 'The driver guards itself', 9.4, bold=True) + jvm_py('rows', 'jvm') + t(185, 104, 'limit 50 MiB', 7.6, 'red', bold=True) + cap('Job aborted before OOM.', '', 'red', y=144, h=30),
]
see_caps = ['Arrow is enabled by default.', 'Ways to bring rows back.', '1M rows: 9.9 s vs 1.4 s.', 'A null turned ints into floats.', 'maxResultSize stopped a 5M collect.']
behind_caps = ['Batches between the JVM and Python.', 'Executors to driver to Python.', 'Arrow skips per-row conversion.', 'NaN needs a float column.', 'Results are checked against the limit.']
two = anim_two('collect, toPandas and Arrow', 'Results to the driver, not data', 'Real lab outputs', 'The trip to Python', see, B1, see_caps, behind_caps)

# ---- scenario 1: notebook to production
e1 = (t(180, 22, 'Notebook chart', 9.4, bold=True) + t(180, 56, 'orders.sample(…).toPandas().plot()', 8.0, 'ink', mono=True) + cap('10,000 rows: fine.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Scheduled job, full table', 9.4, bold=True) + t(180, 56, 'orders.toPandas()', 8.4, 'ink', mono=True) + cap('Driver memory explodes.', '', 'amber', y=150, h=34))
e3 = (t(180, 22, 'Kernel dies, no report', 9.4, bold=True) + t(180, 56, 'or maxResultSize error', 8.4, 'ink2') + cap('Like our 5M collect.', '', 'red', y=150, h=34))
e4 = (t(180, 22, 'Aggregate in Spark', 9.4, bold=True) + t(180, 56, 'groupBy("city", "day").agg(…).toPandas()', 7.8, 'ink', mono=True) + cap('Hundreds of rows.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Same chart, tiny transfer', 9.4, 'acc', bold=True) + t(180, 56, 'seconds, not crashes', 8.4, 'ink2') + cap('Results, not data.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'A chart that crashed in production',
              'toPandas on full tables. (Typical; limits from our lab.)',
              'toPandas on big data', 'Converting a full table copies every row into the driver; aggregate in Spark first and convert only the result', [e1, e2, e3, e4, e5],
              ['Sample works.', 'Full table.', 'Crash.', 'Aggregate.', 'Small result.'],
              hid='scenario-chart')

# ---- scenario 2: slow export to pandas model
b1 = (t(180, 22, 'Model scores in pandas', 9.4, bold=True) + t(180, 56, 'toPandas() -> model -> createDataFrame', 8.0, 'ink', mono=True) + cap('Every hour, 1M rows.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Arrow disabled in old config', 9.4, bold=True) + t(180, 56, 'copied from a Spark 3 cluster', 8.4, 'ink2') + cap('About 20 s of transfer.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'Arrow on', 9.4, bold=True) + t(180, 56, '9.9 + 11.8 s -> 1.4 + 2.6 s', 8.4, 'ink', mono=True) + cap('Our lab numbers.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Better: pandas UDF', 9.4, bold=True) + t(180, 56, 'score on executors, in parallel', 8.4, 'ink2') + cap('Lesson 6.6.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Check fallbacks', 9.4, 'acc', bold=True) + t(180, 56, 'warnings mean the slow path', 8.4, 'ink2') + cap('Unsupported types.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Twenty seconds of copying every hour',
              'Arrow for pandas round trips. (Timings from our lab.)',
              'Arrow transfer', 'Arrow makes toPandas and createDataFrame from pandas several times faster; pandas UDFs avoid the round trip', [b1, b2, b3, b4, b5],
              ['Round trip.', 'Arrow off.', 'Arrow on.', 'pandas UDF.', 'Watch fallback.'],
              hid='scenario-arrow')

# ---- scenario 3: raising maxResultSize
u1 = (t(180, 22, 'Job fails: maxResultSize', 9.4, bold=True) + t(180, 56, 'Total size … bigger than 1024 MiB', 8.2, 'ink', mono=True) + cap('A quick fix is tempting.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'maxResultSize=0 (unlimited)', 9.4, bold=True) + t(180, 56, 'next run: driver OOM', 8.4, 'ink2') + cap('The guard was removed.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'Find the collect', 9.4, bold=True) + t(180, 56, 'collect / toPandas / broadcast of big data', 8.0, 'ink2') + cap('The real cause.', '', 'red', y=150, h=34))
u4 = (t(180, 22, 'Write instead of collect', 9.4, bold=True) + t(180, 56, 'df.write.parquet(…)', 8.4, 'ink', mono=True) + cap('Executors write in parallel.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Keep the limit', 9.4, 'acc', bold=True) + t(180, 56, 'fail fast, not crash', 8.4, 'ink2') + cap('A safety net.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Removing the safety net',
              'What maxResultSize is for. (Typical; behaviour from our lab.)',
              'maxResultSize', 'The limit stops oversized results before the driver runs out of memory; fix the collect, do not remove the limit', [u1, u2, u3, u4, u5],
              ['Limit hit.', 'Limit removed.', 'Find the cause.', 'Write output.', 'Keep the guard.'],
              hid='scenario-maxresult')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Results to the driver, not data</h2>
  <p>Left: real outputs. Right: how data travels from executors into Python.</p>
''' + two + '''
  <p>Three live scenarios follow: a chart that crashed in production, a slow pandas round trip, and a safety limit that was switched off.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Driver-side data at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'charts', 12, 'blue', bold=True) + t(60, 58, 'notebooks', 7.4, 'ink2'),
    '1. Charts and reports',
    'Notebooks aggregate in Spark and convert the small result with toPandas for matplotlib or Plotly.',
    ['Spark aggregate', '*toPandas', 'Chart']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'Arrow', 12, 'green', bold=True) + t(60, 58, 'DuckDB', 7.4, 'ink2'),
    '2. Arrow-native tools',
    'Results move to DuckDB or Polars through toArrow without a pandas copy.',
    ['Spark', '*toArrow', 'DuckDB / Polars']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'config', 11, 'violet', bold=True) + t(60, 58, 'lookups', 7.4, 'ink2'),
    '3. Small lookups for code',
    'Lists of active cities or thresholds are collected (a few rows) to drive the rest of the job.',
    ['Tiny table', '*collect', 'Python logic']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'ML', 12, 'acc', bold=True) + t(60, 58, 'training', 7.4, 'ink2'),
    '4. Single-node model training',
    'A sampled or aggregated training set is converted to pandas for scikit-learn when it fits on one machine.',
    ['Sample', '*toPandas', 'scikit-learn']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'API', 12, 'acc', bold=True) + t(60, 58, 'push', 7.4, 'ink2'),
    '5. Pushing rows to an API',
    'toLocalIterator streams rows partition by partition to an external service without holding all of them.',
    ['DataFrame', '*toLocalIterator', 'API calls']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> the driver’s role in <a href="../../01-introduction/03-spark-architecture/">1.3</a> and actions in <a href="../../02-rdds/02-transformations-and-actions/">2.2</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
