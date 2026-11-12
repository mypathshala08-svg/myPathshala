import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit2 import *
C = 'l125_pandas.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('Your analyst knows pandas, not Spark. Can the same pandas code run on a cluster?',
    'Mostly, yes: <code>import pyspark.pandas as ps</code>. The same <code>read_csv → groupby → mean</code> gave identical numbers in pandas and in pandas-on-Spark. But on 300,000 rows pandas took <b>0.12 s</b> and pandas-on-Spark <b>14.6 s</b> on the first run (2.3 s warm). Spark pays off when data no longer fits one machine, not before. We also hit a <code>ValueError</code> when mixing two frames, and saw that the safety option is now <b>True</b> by default.',
    ['What pyspark.pandas is and when it beats plain pandas.', 'Moving between pandas, pandas-on-Spark and Spark DataFrames.', 'Default index, ops on different frames, and costly calls.'])
cmap = concept_map('Concept map. Beginner: pandas vs Spark DataFrames. Intermediate: pyspark.pandas API, to_spark, pandas_api, to_pandas. Advanced: default index types, ops on different frames, cost of len, iloc and values.',
    [[('pd', 'collect / toPandas', 'Lesson 4.6', B + '04-dataframes/06-collect-topandas-and-arrow/'), ('cmp', 'Spark vs pandas, Polars…', 'Lesson 12.2', B + '12-spark-in-industry/02-spark-vs-pandas-polars-duckdb-flink-trino/')],
     [('ps', 'pyspark.pandas', 'same API', None), ('ts', 'to_spark', 'to Spark DF', None), ('pa', 'pandas_api', 'back', None), ('tp', 'to_pandas', 'to driver', None)],
     [('ix', 'Default index', 'distributed-sequence', None), ('df', 'Diff frames', 'ValueError', None), ('ct', 'Hidden cost', 'len, iloc, values', None), ('udf', 'Arrow UDFs', 'Lesson 6.6', B + '06-transformations/06-udfs/')]],
    [('pd', 'ps'), ('cmp', 'ps'), ('ps', 'ts'), ('ts', 'pa'), ('ps', 'tp'), ('ps', 'ix'), ('ps', 'df'), ('tp', 'ct'), ('ps', 'udf')],
    {'ps', 'ts', 'pa', 'tp', 'ix', 'df', 'ct'},
    '<b>Builds on:</b> <a href="../02-spark-vs-pandas-polars-duckdb-flink-trino/">12.2</a>. <b>Next:</b> <a href="../../13-capstone/01-problem-and-dataset/">Module 13 capstone</a>.')
whw = why_how_where(
    'Teams have years of pandas code and pandas skills. pandas-on-Spark (formerly Koalas) lets that code scale out with few changes.',
    'A pandas-on-Spark DataFrame wraps a Spark DataFrame plus an index. Each pandas call is translated into Spark operations, run lazily, and only to_pandas()/printing brings rows to the driver.',
    'Scaling notebooks that outgrew one machine, migrating pandas jobs to a cluster, analysts working on lakehouse tables with a familiar API.',
    'Small data is slower than pandas; a global row order (index) is expensive; some pandas features are missing or costly; to_pandas() can crash the driver on big data.')
def two_worlds(hl=-1):
    o = box(16, 30, 100, 80, 'blue', rx=8) + t(66, 56, 'pandas', 9, bold=True) + t(66, 74, 'one machine', 7.2) + t(66, 90, '0.12 s', 7.2, bold=True)
    o += box(250, 30, 104, 80, 'green', rx=8) + t(302, 56, 'Spark DataFrame', 8, bold=True) + t(302, 74, 'cluster', 7.2)
    o += box(134, 22, 98, 96, 'amber' if hl >= 0 else 'violet', rx=8) + t(183, 48, 'pandas-on-Spark', 7.6, bold=True) + t(183, 66, 'pandas API', 7.2) + t(183, 82, 'Spark engine', 7.2) + t(183, 100, '14.6 s / 2.3 s', 7.2, bold=True)
    return o + t(124, 134, 'to_pandas() ←', 7) + t(242, 134, '→ to_spark()', 7)
scene_svg = scene('Three boxes: pandas on one machine, pandas-on-Spark in the middle with the pandas API on the Spark engine, and Spark DataFrame on the cluster; arrows show to_pandas and to_spark.', two_worlds(),
                  'Same pandas code, <tspan font-weight="700" class="s-acc">different engine underneath</tspan>.')
dialogue = '''K> Sir, Riya’s pandas notebook crashes on the full year of orders: memory error.
A> Rewrite it in PySpark? Maybe later. First try <b>import pyspark.pandas as ps</b>; most lines stay the same.
R> Will it be faster?
A> On big data, yes, because it can use the cluster. On small data, no. Let’s measure both, honestly.'''
lv = '''
LEVELS> pandas-on-Spark at three levels
L1> Same recipe, bigger kitchen
      <ul>
        <li>You keep your recipe (pandas code) but cook in a big hotel kitchen with many cooks (Spark). For two plates, your home stove is quicker.</li>
      </ul>
L2> The API
      <ul>
        <li><code>import pyspark.pandas as ps</code>; <code>ps.read_csv</code>, <code>ps.read_parquet</code>, <code>ps.read_table</code>, <code>ps.DataFrame(…)</code>, <code>ps.sql("… {df} …", df=psdf)</code>.</li>
        <li><code>psdf.to_spark()</code> → Spark DataFrame; <code>sdf.pandas_api()</code> → pandas-on-Spark; <code>psdf.to_pandas()</code> → real pandas on the driver.</li>
        <li>Options: <code>ps.set_option("compute.default_index_type", …)</code>, <code>"compute.ops_on_diff_frames"</code>.</li>
      </ul>
L3> Practical details
      <ul>
        <li>Default index <code>distributed-sequence</code> gives 0, 1, 2… but needs extra work; <code>distributed</code> is cheapest (ids not consecutive); pass <code>index_col</code> when reading to avoid it.</li>
        <li>Combining columns from two different frames needs a join on the index; in Spark 4 <code>compute.ops_on_diff_frames</code> is True by default (it was False in 3.x).</li>
        <li><code>len()</code>, <code>iloc[n]</code>, <code>.values</code> and printing all trigger Spark jobs; <code>.values</code> and <code>to_pandas()</code> collect everything to the driver.</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of a pandas-on-Spark line: ps.read_csv creates a lazy frame, groupby and mean are translated to Spark, to_pandas collects the small result.',
    t(16, 22, 'One pandas-on-Spark line (real)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('ps.read_csv', 'blue', 1), ('.groupby("city")', 'green', 2), ('["amount"].mean()', 'amber', 3), ('.to_pandas()', 'violet', 4)]) +
    legend(16, 84, [(1, 'Source', 'Spark reads the file'), (2, 'Translated', 'Spark groupBy'), (3, 'Lazy', 'nothing runs yet'),
                    (4, 'Action', '3 rows to the driver')], size=8, gap=15, w=90),
    h=156, caption='Only the small result (three cities) reaches pandas.')
extra = '''

  <h3>Dissect one line</h3>
''' + DIS
types_html = table(['Object', 'Lives where', 'API', 'Convert'], [
    ['pandas DataFrame', 'driver memory', 'pandas', 'ps.from_pandas(pdf) / spark.createDataFrame'],
    ['pandas-on-Spark DataFrame', 'cluster (lazy)', 'pandas-like', 'to_spark() · to_pandas()'],
    ['Spark DataFrame', 'cluster (lazy)', 'PySpark', 'pandas_api() · toPandas()']], minw=600)
warn = 'to_pandas() and .values collect every row to the driver: fine for 3 aggregated rows, fatal for 300 million. Aggregate or filter first, then convert. And benchmark honestly: for data that fits comfortably in memory, plain pandas (or Polars/DuckDB, Lesson 12.2) is usually faster.'
steps = [
    ('Step 1 · Same code, two engines',
     code('python', 'l125_pandas.py', 'pd.read_csv(path).groupby("city")["amount"].mean()\nps.read_csv(path).groupby("city")["amount"].mean().to_pandas()', sec('== 1)', '== 2)')),
     'Identical answers. Spark’s start-up and job overhead make it far slower on 300,000 rows.'),
    ('Step 2 · Type and default index',
     code('python', 'l125_pandas.py', 'psdf = ps.read_csv(path)\ntype(psdf); ps.get_option("compute.default_index_type"); psdf.head(3)', sec('== 2)', '== 3)')),
     'It looks like pandas, but the class lives in pyspark.pandas, and the 0, 1, 2… index is generated for you.'),
    ('Step 3 · Moving between worlds',
     code('python', 'l125_pandas.py', 'sdf = psdf.to_spark()\nback = sdf.pandas_api()\nsmall = psdf.head(5).to_pandas()', sec('== 3)', '== 4)')),
     'Use Spark for heavy lifting and pandas for the small final result.'),
    ('Step 4 · Two different frames',
     code('python', 'l125_pandas.py', 'ps.set_option("compute.ops_on_diff_frames", False)\npsdf["amount"] + other["amount"]', sec('== 4)', '== 5)')),
     'Spark 4 default is True (an index join happens silently); set False to catch accidental expensive joins.'),
    ('Step 5 · SQL and hidden costs',
     code('python', 'l125_pandas.py', 'ps.sql("SELECT city, count(*) AS n FROM {df} GROUP BY city", df=psdf)\nlen(psdf); psdf.iloc[5]; psdf.values', sec('== 5)')),
     'Everything works, but each line starts a Spark job; .values collects to NumPy on the driver.'),
]
see = [term([('pandas 0.12 s', G), ('ps     14.57 s', RD)], size=7.0), term([('pyspark.pandas.frame', W), ('distributed-sequence', W)], size=6.8),
       term([('to_spark  ok', G), ('to_pandas driver!', RD)], size=7.0), term([('default True', W), ('False: ValueError', RD)], size=7.0), term([('len 300000', W), ('warm 2.31 s', G)], size=7.0)]
B1 = [two_worlds(1), two_worlds(-1), two_worlds(1), two_worlds(1), two_worlds(-1)]
B1 = [b + cap(c, '', tn, y=146, h=24) for b, c, tn in zip(B1, ['Same answer', 'Index made', 'Convert', 'Join guard', 'Jobs hidden'], ['green', 'blue', 'amber', 'red', 'violet'])]
two = anim_two('pandas API on Spark', 'Same code, other engine', 'Real outputs (local[2])', 'pandas skills, cluster scale', see, B1, ['Compare.', 'Index.', 'Convert.', 'Frames.', 'Costs.'], ['Equal.', 'Seq.', 'Arrow.', 'Join.', 'Jobs.'])
pe = peel('pandas-on-Spark, layer by layer', 'What happens behind psdf.groupby().mean(). (Simplified.)',
    [('pandas call', ''), ('Translate', ''), ('Plan', ''), ('Run', ''), ('Index', ''), ('Return', '')],
    [['pandas call', 'groupby + mean', '', ''], ['Translate', 'Spark groupBy', 'agg(avg)', ''], ['Plan', 'Catalyst', 'optimises', ''],
     ['Run', 'tasks on executors', '', ''], ['Index', 'attach index', 'columns', ''], ['Return', 'lazy frame', 'until to_pandas', '']],
    ['API.', 'Translate.', 'Optimise.', 'Execute.', 'Index.', 'Lazy.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Notebook out of memory', 'pandas crashes on a year of data. (Typical.)', ('pyspark.pandas', 'Minimal changes'), [
    ('pd.read_csv crashes', 'MemoryError', 'Problem.', 'red'), ('import pyspark.pandas as ps', 'swap reader', 'Change.', 'green'),
    ('Aggregate in Spark', 'groupby, merge', 'Scale.', 'green'), ('to_pandas() small result', 'charts', 'Finish.', 'amber'),
    ('Later: move hot paths to PySpark', '', 'Mature.', 'blue')], ['Crash.', 'Swap.', 'Aggregate.', 'Collect small.', 'Refactor.'], 'scenario-oom') + \
       five('Real-time scenario 2', 'Slower after migration', 'Small data got slower. (Typical.)', ('Right tool', 'Measure first'), [
    ('Daily file 300k rows', 'was 0.12 s', 'Before.', 'blue'), ('Now 14.6 s', 'Spark overhead', 'After.', 'red'),
    ('Measure size', 'fits in memory', 'Analyse.', 'amber'), ('Keep pandas / DuckDB', 'for small', 'Decide.', 'green'),
    ('Spark for big monthly runs', '', 'Split.', 'green')], ['Before.', 'After.', 'Size.', 'Small tool.', 'Big tool.'], 'scenario-slow') + \
       five('Real-time scenario 3 · advanced', 'Silent expensive joins', 'Job got slow. (Typical.)', ('ops_on_diff_frames', 'Guard rails'), [
    ('a["x"] + b["y"]', 'two frames', 'Code.', 'blue'), ('Spark 4: index join', 'silent', 'Cost.', 'amber'),
    ('Set option False in tests', 'ValueError', 'Catch.', 'red'), ('Merge explicitly on keys', 'clear plan', 'Fix.', 'green'),
    ('Use index_col / distributed', 'cheaper index', 'Tune.', 'violet')], ['Code.', 'Join.', 'Catch.', 'Merge.', 'Index.'], 'scenario-join')
assemble(HERE, h2_story='Your pandas code, on a cluster', hook_html=hk,
    narration='TiffinGo’s analyst wrote a year of reports in pandas. Data grew; the notebook now fails. Can the same code run on Spark without a rewrite?',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='pandas API on Spark',
    formal='<b>pandas API on Spark</b> (<code>pyspark.pandas</code>, formerly Koalas, part of PySpark since 3.2) implements the pandas DataFrame and Series API on top of Spark DataFrames. Each pandas-on-Spark DataFrame holds a Spark DataFrame plus index metadata; operations are translated to Spark SQL plans and executed lazily across the cluster.',
    simple='Write pandas-style code; Spark does the work on many machines; bring back only small results as real pandas.',
    term_rows=[('ps', 'pyspark.pandas.'), ('psdf', 'pandas-on-Spark DataFrame.'), ('to_spark', 'To Spark DataFrame.'), ('pandas_api', 'Spark → ps.'), ('to_pandas', 'Collect to driver.'), ('Default index', 'Generated 0..n.'), ('Diff frames', 'Columns from two frames.'), ('Koalas', 'Old project name.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('pandas-on-Spark is always faster.', '0.12 s vs 14.6 s on small data.', 'Step 1.'),
               ('It is a pandas DataFrame.', 'Class is pyspark.pandas.frame.', 'Step 2.'),
               ('to_pandas() is free.', 'Collects all rows to the driver.', 'Warning.')],
    exam='“What is pandas API on Spark?” pyspark.pandas (ex-Koalas, 3.2+); ps.read_csv/parquet; to_spark(), pandas_api(), to_pandas(); default index types (sequence, distributed-sequence, distributed); compute.ops_on_diff_frames; small data → pandas is faster.',
    types_h2='Three DataFrames', types_html=types_html, warn=warn,
    steps_h2='pandas vs pandas-on-Spark', steps_intro='All outputs are real: PySpark 4.3.0, local[2], a 300,000-row CSV generated with a fixed seed.',
    steps=steps, two=two, peel_intro='Now peel one call.', peel_html=pe,
    scen_intro='Three live scenarios: out of memory, slower after migration, silent joins.', scen=scen,
    uc_h2='pandas-on-Spark at work', ucs=[uc_('nb', 'notebooks', 'blue', '1. Scale notebooks', 'Same code, more data.', ['pandas code', '*ps', 'Cluster']),
        uc_('mig', 'migrate', 'green', '2. Migration', 'Step towards PySpark.', ['Legacy', '*ps', 'Spark']),
        uc_('lake', 'lakehouse', 'amber', '3. Lakehouse EDA', 'read_table on Delta.', ['Tables', '*ps', 'Charts']),
        uc_('feat', 'features', 'violet', '4. ML features', 'pandas-style prep.', ['Raw', '*ps', 'MLlib'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../../04-dataframes/06-collect-topandas-and-arrow/">4.6 toPandas and Arrow</a>.')
