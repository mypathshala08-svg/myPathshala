import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='12-spark-in-industry', lesson='05-pandas-api-on-spark', n='12.5', module_label='Module 12 · Spark in industry',
    title='pandas API on Spark',
    desc='pandas API on Spark (pyspark.pandas, formerly Koalas): run pandas-style code on Spark, convert with to_spark, pandas_api and to_pandas, default index types, ops on different frames, hidden costs, and when plain pandas is faster. Real PySpark 4.3 lab.',
    og_desc='Same answer, 0.12 s vs 14.6 s: an honest look at pandas API on Spark in PySpark 4.3.',
    minutes=18, level='Intermediate',
    lead='Run <b>pandas code on Spark</b> with <code>pyspark.pandas</code>. We compare it honestly with pandas, convert between three kinds of DataFrame, and learn the traps: index, diff frames and to_pandas. <b>All outputs are real.</b>',
    chips=['Same results', 'pandas 0.12 s vs 14.6 s', 'ops_on_diff_frames', 'Runs in your browser (Python)'])
MAIN = '''# Why a "default index" costs work in a distributed frame
partitions = [["Mumbai", "Pune"], ["Delhi"], ["Pune", "Delhi", "Mumbai"]]
# distributed-sequence: count rows per partition first, then offsets
sizes = [len(p) for p in partitions]
offsets = [sum(sizes[:i]) for i in range(len(sizes))]
rows = [(offsets[i] + j, city) for i, p in enumerate(partitions) for j, city in enumerate(p)]
print("sizes", sizes, "offsets", offsets)
print(rows)
# distributed: unique but not consecutive ids, no counting pass
print([(i * 1000 + j, c) for i, p in enumerate(partitions) for j, c in enumerate(p)])
'''
RUN = dict(heading='Run the code: building an index on partitions', intro='<p>Why 0, 1, 2… is not free on a cluster. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('offsets = [sum(sizes[:i]) for i in range(len(sizes))]', 'Needs a counting pass first.'), ('print([(i * 1000 + j, c) for i, p in enumerate(partitions) for j, c in enumerate(p)])', 'Cheap ids with gaps.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>.', code=None),
        dict(label='2 · Predict first: speed-up', hint='<b>Predict first:</b> ratio of times.', code='print(round(14.57 / 0.12))\n'),
        dict(label='3 · Driver memory', hint='Rows × bytes.', code='rows, row_bytes = 300_000_000, 60\nprint(rows * row_bytes / 1e9, "GB to the driver")\n'),
        dict(label='4 · Index join', hint='Align by index.', code='a = {0: 873, 1: 164}\nb = {0: 873, 1: 164}\nprint([a[i] + b[i] for i in a])\n'),
        dict(label='5 · Spot the error', hint='Different frames.', expect='error', code='ops_on_diff_frames = False\nif not ops_on_diff_frames:\n    raise ValueError("Cannot combine the series or dataframe because it comes from a different dataframe")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC', intro='<p>PySpark 4.x with pandas and pyarrow. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Run the lab', cmd='python3 l125_pandas.py', file='terminal', output='  default index type: distributed-sequence', note='~1 minute.'),
           dict(title='2 · Cheaper index', cmd='ps.read_csv(path, index_col="order_id")', file='python', output='', note='No generated index.')])
TRACE = dict(heading='Converting step by step', intro='<p>Three worlds.</p>',
    code='steps = ["ps.read_csv", "to_spark()", "pandas_api()", "head(5).to_pandas()"]\nfor s in steps:\n    print(s)\n', notes={2: 'Each :: is a conversion.'})
WORKED_INTRO = 'Three pandas-on-Spark decisions.'
EXAMPLES = [
    dict(level='b', tag='choose', title='pandas or ps?', problem='<p>Data is 200 MB.</p>', inp='size',
         approach=['Fits in memory?', 'Yes → pandas.', 'No → ps or PySpark.'], code='print("pandas" if 0.2 < 4 else "ps")\n', notes={1: 'GB vs RAM.'}, tryit='Step 1.'),
    dict(level='i', tag='convert', title='Finish in pandas', problem='<p>Plot city totals.</p>', inp='psdf',
         approach=['Aggregate in ps.', 'to_pandas() small.', 'Plot.'], code='print(["groupby", "sum", "to_pandas", "plot"])\n', notes={1: 'Small result.'}, tryit='Step 3.'),
    dict(level='a', tag='index', title='Avoid index cost', problem='<p>Huge CSV is slow.</p>', inp='options',
         approach=['index_col on read.', 'Or default_index_type distributed.', 'Measure.'], code='print({"compute.default_index_type": "distributed"})\n', notes={1: 'Cheaper.'}, tryit='Step 2.')]
QUIZ = mix([
    dict(q='Beginner: pyspark.pandas lets you…', options=['Write Scala', 'Use pandas-style code on Spark', 'Replace SQL', 'Use GPUs'], answer=1, why='Same API.'),
    dict(q='Beginner: to_pandas() brings data to…', options=['Executors', 'The driver', 'Disk', 'HDFS'], answer=1, why='Collect.'),
    dict(q='Beginner: On 300k rows, faster was…', options=['pyspark.pandas', 'pandas', 'Same', 'Neither'], answer=1, why='0.12 s.'),
    dict(q='Intermediate: Spark DataFrame → ps…', options=['to_spark()', 'pandas_api()', 'toPandas()', 'ps.sql'], answer=1, why='pandas_api.'),
    dict(q='Intermediate: Default index type…', options=['sequence', 'distributed-sequence', 'distributed', 'none'], answer=1, why='Step 2.'),
    dict(q='Intermediate: Old name of pyspark.pandas…', options=['Arrow', 'Koalas', 'Pandas2', 'Polars'], answer=1, why='Koalas.'),
    dict(q='Advanced: ops_on_diff_frames default in Spark 4…', options=['False', 'True', 'Removed', 'Error'], answer=1, why='Step 4.'),
    dict(q='Advanced: psdf.values…', options=['Is lazy', 'Collects to NumPy on driver', 'Writes Parquet', 'Fails'], answer=1, why='Costly.')])
REVISION = ['import pyspark.pandas as ps; pandas-like API on Spark (ex-Koalas).', 'Same results; small data: pandas 0.12 s vs ps 14.6 s (2.3 s warm).',
    'to_spark(), pandas_api(), to_pandas() (driver!).', 'Default index distributed-sequence; index_col or distributed to save work.', 'ops_on_diff_frames True by default in Spark 4.']
FAQ = [('Is every pandas function supported?', 'Most common ones; some are missing or slow. Check the API reference.'),
    ('Can I plot?', 'Yes, psdf.plot uses plotly by default and samples/aggregates first.'),
    ('pandas-on-Spark or PySpark DataFrame?', 'pandas skills and legacy code → ps; new pipelines → PySpark DataFrame API.'),
    ('Does it use Arrow?', 'Yes, conversions to pandas use Arrow.')]
PRACTICE_INTRO = 'pandas-on-Spark programs.'
PROBLEMS = [
    dict(level='easy', title='Ratio', stmt='Slowdown.', inp='floats', code='print(round(14.57 / 0.12))\n', explain='~121×.'),
    dict(level='easy', title='Warm', stmt='Warm vs cold.', inp='floats', code='print(round(14.57 - 2.31, 2))\n', explain='Startup cost.'),
    dict(level='easy', title='Mean', stmt='Group mean.', inp='dict', code='d = {"Pune": [100, 300]}\nprint({k: sum(v) / len(v) for k, v in d.items()})\n', explain='200.'),
    dict(level='medium', title='Offsets', stmt='Partition offsets.', inp='list', code='s = [3, 5, 2]\nprint([sum(s[:i]) for i in range(3)])\n', explain='[0, 3, 8].'),
    dict(level='medium', title='Fits?', stmt='Memory check.', inp='floats', code='print(300_000 * 60 / 1e6, "MB")\n', explain='18 MB: pandas.'),
    dict(level='medium', title='Align', stmt='Index join.', inp='dicts', code='a = {0: 1, 1: 2}; b = {1: 10, 0: 20}\nprint({i: a[i] + b[i] for i in a})\n', explain='By index.'),
    dict(level='business', title='Monthly run', stmt='Pick engine.', inp='GB', code='gb = 120\nprint("Spark" if gb > 16 else "pandas")\n', explain='Spark.'),
    dict(level='business', title='Daily run', stmt='Pick engine.', inp='GB', code='gb = 0.02\nprint("Spark" if gb > 16 else "pandas")\n', explain='pandas.')]
SCN_INTRO = 'pandas-on-Spark interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“What is the pandas API on Spark?”', 'Explain.', 'answer?', '<p>pyspark.pandas (formerly Koalas): pandas-style API executed by Spark; convert with to_spark, pandas_api, to_pandas.</p>', '“A faster pandas for any size.”') +
    scn('Analytics', 'Mid-level', 'OOM notebook', 'Scale it.', 'answer?', '<ul><li>Swap to ps, aggregate, collect small.</li></ul>', 'Bigger laptop.') +
    scn('Data', 'Mid-level', 'Slower', 'Small file slower.', 'why?', '<ul><li>Spark overhead; use pandas for small data.</li></ul>', 'Bug in Spark.') +
    scn('Platform', 'Senior', 'Index cost', 'Huge reads slow.', 'fix?', '<ul><li>index_col or distributed index; avoid diff-frame joins.</li></ul>', 'More executors only.'))
