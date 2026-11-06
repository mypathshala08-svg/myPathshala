import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit2 import *
C = 'l116_clean.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('Two PySpark scripts give the same numbers. One is 400 lines nobody dares touch; the other is five small functions with tests. Which one is faster?',
    'Often neither: Spark optimises both into the same plan. The difference is everything else: reading, testing, changing. Some habits <i>do</i> change the plan: 20 <code>withColumn</code> calls built <b>21 Project nodes</b> and took 220 ms just to construct, while one <code>select</code> built 2 nodes in 70 ms; <code>isEmpty()</code> answered in 0.12 s where <code>count() &gt; 0</code> took 0.31 s. Our TiffinGo transforms became a one-line <code>.transform()</code> chain with 2 passing pytest tests.',
    ['Structuring PySpark code as small DataFrame → DataFrame functions.',
     'Habits that change plans: select vs withColumn, toDF, isEmpty, filter early.',
     'Making code testable and configurable.'])
cmap = concept_map('Concept map. Beginner: functions, readability. Intermediate: DataFrame.transform, config, select vs withColumn, filter and prune early. Advanced: plan size, existence checks, project layout, tests, logging.',
    [[('ct', 'Catalyst + explain', 'Lesson 7.3', B + '07-spark-sql/03-catalyst-and-explain/'), ('co', 'Columns API', 'Lesson 4.3', B + '04-dataframes/03-working-with-columns/')],
     [('tf', 'transform()', 'chain functions', None), ('cf', 'Config in', 'no hard-coding', None), ('sw', 'select vs withColumn', 'plan size', None), ('fe', 'Filter + prune early', 'less data', None)],
     [('ie', 'isEmpty vs count', 'existence', None), ('ly', 'Project layout', 'package + entrypoint', B + '11-spark-in-production/01-spark-submit-and-deploy-modes/'), ('ts', 'Tests', 'Lesson 11.4', B + '11-spark-in-production/04-testing-pyspark-code/'), ('lg', 'Logging', 'driver logs', None)]],
    [('ct', 'sw'), ('co', 'sw'), ('co', 'tf'), ('tf', 'cf'), ('tf', 'ts'), ('sw', 'fe'), ('fe', 'ie'), ('tf', 'ly'), ('ly', 'lg')],
    {'tf', 'cf', 'sw', 'fe', 'ie', 'ly', 'lg'},
    '<b>Builds on:</b> <a href="../04-testing-pyspark-code/">11.4 Testing</a>, <a href="../../07-spark-sql/03-catalyst-and-explain/">7.3 explain</a>. <b>Next:</b> <a href="../../12-spark-in-industry/01-spark-platforms/">Module 12</a>.')
whw = why_how_where(
    'Pipelines live for years and change every month. Long notebook-style scripts hide bugs, cannot be tested, and are copied instead of reused. A few habits also keep Spark plans small and jobs cheap.',
    'Write each step as a pure function <code>DataFrame → DataFrame</code>; pass settings (prices, dates, paths) in; compose with <code>df.transform(f)</code>; keep I/O at the edges (read at start, write at end); test each function with a tiny DataFrame. Prefer one <code>select</code>/<code>withColumns</code> over many <code>withColumn</code>, filter and select columns early, and use <code>isEmpty()</code> for existence checks.',
    'Every production job, shared team libraries, code reviews, and interviews that ask “how do you structure PySpark code?”.',
    'Over-abstracting hurts too: keep functions small but meaningful, and check plans (<code>explain</code>) when performance matters.')

def chain(hl=-1):
    parts = [('orders', 'card'), ('only_valid', 'blue'), ('add_amount', 'violet'), ('revenue_by_city', 'green')]
    o = ''
    for k, (n, tn) in enumerate(parts):
        o += box(6 + k * 88, 44, 80, 34, 'acc' if k == hl else tn, rx=6) + t(46 + k * 88, 65, n, 7.4, bold=True)
        if k < 3: o += arrow(86 + k * 88, 61, 94 + k * 88, 61)
    return o + t(176, 24, 'df.transform(f).transform(g).transform(h)', 7.6, mono=True) + t(176, 104, 'each function: DataFrame in, DataFrame out, tested alone', 7.0)
scene_svg = scene('A clean pipeline: the orders DataFrame flows through three small functions, only_valid, add_amount and revenue_by_city, chained with DataFrame.transform; each can be tested alone.', chain(),
                  'Small functions, one <tspan font-weight="700" class="s-acc">transform</tspan> chain.')
dialogue = '''K> Sir, my revenue job works, but it is one 400-line notebook. Reviewers keep asking what each block does.
A> Turn each block into a function that takes a DataFrame and returns a DataFrame. Then the job reads like a sentence.
R> Does that make Spark slower?
A> Usually no, Catalyst sees the same plan. But some habits do change the plan. Let’s measure both.'''

lv = '''
LEVELS> Clean PySpark at three levels
L1> A recipe card per step
      <ul>
        <li>Instead of one long story, write one card per step (wash, cut, cook). Anyone can test one card, swap it, or reuse it in another dish.</li>
      </ul>
L2> The habits
      <ul>
        <li><b>Functions</b>: <code>def add_amount(prices): def _f(df): …; return _f</code> → <code>df.transform(add_amount(PRICES))</code>.</li>
        <li><b>Columns</b>: build many columns with one <code>select("*", …)</code> or <code>withColumns({…})</code>; rename many with <code>toDF(*names)</code> or <code>withColumnsRenamed</code>.</li>
        <li><b>Data volume</b>: filter early, select only needed columns, push filters to the source (Parquet); <code>isEmpty()</code> / <code>limit(1)</code> instead of <code>count() &gt; 0</code>.</li>
      </ul>
L3> Project shape
      <ul>
        <li>Package: <code>transforms.py</code> (pure functions), <code>io.py</code> (read/write), <code>config.yaml</code>, <code>main.py</code> (entrypoint wiring them), <code>tests/</code>; ship with <code>--py-files</code> or a wheel (Lesson 11.1).</li>
        <li>Name intermediate DataFrames by meaning, avoid <code>df1, df2</code>; log row counts sparingly (each count is a job).</li>
        <li>Reviews: read <code>explain("formatted")</code> for new jobs; watch for repeated scans, unexpected Exchanges and huge plans built in loops.</li>
      </ul>
/LEVELS
'''
DIS = figure('Plan size comparison from the lab: 20 withColumn calls produce 21 Project nodes and 220 ms build time; one select or withColumns produces 2 Project nodes and 70 ms.',
    t(16, 22, 'Analysed plan size (real)', 8.6, 'ink', anchor='start', bold=True) +
    t(16, 50, 'withColumn × 20', 8, 'ink', anchor='start', bold=True) + box(150, 38, 21 * 20, 18, 'red', rx=3) + t(150 + 21 * 20 + 30, 51, '21', 8, bold=True) +
    t(16, 80, 'one select', 8, 'ink', anchor='start', bold=True) + box(150, 68, 2 * 20, 18, 'green', rx=3) + t(150 + 40 + 20, 81, '2', 8, bold=True) +
    t(16, 110, 'withColumns', 8, 'ink', anchor='start', bold=True) + box(150, 98, 2 * 20, 18, 'green', rx=3) + t(150 + 40 + 20, 111, '2', 8, bold=True),
    h=130, caption='Project nodes in the analysed plan; Catalyst later collapses them, but building and analysing big plans costs driver time.')
extra = '''

  <h3>Plan size at a glance</h3>
''' + DIS

types_html = table(['Instead of…', 'Write…', 'Why'], [
    ['many withColumn in a loop', 'one select("*", …) or withColumns({…})', 'smaller plans, faster to build'], ['chained withColumnRenamed', 'toDF(*names) / withColumnsRenamed', 'one projection'],
    ['count() > 0', 'not df.isEmpty() / limit(1)', 'stops at first row'], ['select("*") then filter late', 'filter and select early', 'less data scanned and shuffled'],
    ['hard-coded paths/prices', 'parameters / config file', 'reuse, tests'], ['one 400-line script', 'small functions + transform()', 'readable, testable'],
], minw=620)
warn = 'Do not log df.count() after every step “for debugging” in production: each count is a full Spark job. Use counts in tests, or cache once and count deliberately.'

steps = [
    ('Step 1 · Small functions, one chain',
     code('python', 'transforms.py', 'def only_valid(df):\n    return df.filter((F.col("qty") > 0) & F.col("item").isNotNull())\n\ndef add_amount(prices):\n    def _f(df):\n        m = F.create_map(*[x for k, v in prices.items() for x in (F.lit(k), F.lit(v))])\n        return df.withColumn("amount", F.col("qty") * m[F.col("item")])\n    return _f\n\norders.transform(only_valid).transform(add_amount(PRICES)).transform(revenue_by_city)', sec('== 1)', '== 2)')),
     'Two million orders, three readable steps. Prices come in as a parameter; “pizza” is not on the menu, so its amount is null and ignored by sum.'),
    ('Step 2 · select vs withColumn',
     code('python', 'l116_clean.py', 'for i in range(20): d1 = d1.withColumn(f"c{i}", F.col("qty") + i)\nd2 = orders.select("*", *[(F.col("qty") + i).alias(f"c{i}") for i in range(20)])\norders.withColumns({f"c{i}": F.col("qty") + i for i in range(20)})', sec('== 2)', '== 3)')),
     'Same result columns; the loop builds 21 projections and takes 3× longer just to construct.'),
    ('Step 3 · Renaming',
     code('python', 'l116_clean.py', 'orders.withColumnRenamed("city", "CITY").withColumnRenamed(...)...\norders.toDF(*[c.upper() for c in orders.columns])', sec('== 3)', '== 4)')),
     'One projection for all names.'),
    ('Step 4 · Existence checks',
     code('python', 'l116_clean.py', 'bad = orders.filter("qty = 0")\nbad.count() > 0\nnot bad.isEmpty()', sec('== 4)', '== 5)')),
     'isEmpty stops at the first matching row.'),
    ('Step 5 · Tests',
     code('python', 'test_transforms.py', 'def test_amount_and_revenue(spark):\n    df = spark.createDataFrame([("Pune", "idli", 2), ("Pune", "dosa", 1)], "city string, item string, qty int")\n    out = df.transform(add_amount({"idli": 45, "dosa": 90})).transform(revenue_by_city).collect()\n    assert [(r.city, r.revenue) for r in out] == [("Pune", 180)]', sec('== 5)')),
     'Each function is tested with three rows, no files, no cluster.'),
]
see = [term([('Delhi 65000130', W), ('Mumbai 65000040', W), ('Pune 64999830', W)], size=7.0), term([('withColumn x20: 21 nodes 220 ms', RD), ('select: 2 nodes 70 ms', G)], size=6.8),
       term([('withColumnRenamed: 4 nodes', Y), ('toDF(*cols): 2 nodes', G)], size=7.0), term([('count() > 0: 0.31 s', Y), ('isEmpty(): 0.12 s', G)], size=7.0), term([('2 passed', G)], size=7.4)]
B1 = [chain(1), chain(2), chain(2), chain(1), chain(3)]
B1 = [b + cap(c, '', tn, y=118, h=30) for b, c, tn in zip(B1, ['Readable chain', 'Small plans', 'One rename', 'Stop early', 'Tested'], ['blue', 'green', 'green', 'amber', 'green'])]
two = anim_two('Clean PySpark', 'Readable, small plans, tested', 'Real outputs (local[2])', 'The chain', see, B1, ['Chain.', 'select.', 'toDF.', 'isEmpty.', 'pytest.'], ['3 steps.', '21 → 2.', '1 node.', '0.12 s.', 'Pass.'])
pe = peel('A clean job, layer by layer', 'TiffinGo revenue job. (Simplified.)',
    [('main.py', ''), ('config', ''), ('read', ''), ('transforms', ''), ('write', ''), ('tests', '')],
    [['main.py', 'parse args', 'build SparkSession', ''], ['config', 'prices, dates, paths', 'from YAML/args', ''], ['read', 'io.read_orders(spark, path)', 'schema explicit', ''],
     ['transforms', 'only_valid → add_amount', '→ revenue_by_city', 'pure'], ['write', 'io.write(df, path)', 'partitioned', ''], ['tests', 'pytest per function', 'tiny DataFrames', 'CI']],
    ['Start.', 'Settings.', 'Load.', 'Logic.', 'Save.', 'Prove.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'The 400-line notebook', 'New hire must change one rule. (Typical.)', ('Refactor', 'Extract functions'), [
    ('Rule hidden at line 287', 'fear of change', 'Problem.', 'red'), ('Extract steps', 'DataFrame → DataFrame', 'Refactor.', 'blue'),
    ('Add tests first', 'freeze behaviour', 'Safety.', 'green'), ('Change one function', 'tests pass', 'Change.', 'green'),
    ('Review in minutes', 'clear diff', 'Done.', 'blue')], ['Fear.', 'Extract.', 'Test.', 'Change.', 'Review.'], 'scenario-refactor') + \
       five('Real-time scenario 2', 'Driver slow before any task', 'Plan built in a loop. (Typical.)', ('Plan size', 'One select'), [
    ('500 withColumn in a loop', 'feature table', 'Slow start.', 'red'), ('explain shows huge plan', 'analysis time', 'Cause.', 'amber'),
    ('Build expressions list', 'one select', 'Fix.', 'green'), ('Driver minutes → seconds', 'same output', 'Win.', 'green'),
    ('Lint rule', 'no withColumn in loops', 'Prevent.', 'blue')], ['Loop.', 'Plan.', 'Select.', 'Fast.', 'Rule.'], 'scenario-plan') + \
       five('Real-time scenario 3 · advanced', 'Same job, three environments', 'Dev, test, prod differ. (Typical.)', ('Config in', 'One code path'), [
    ('Paths hard-coded', 'prod path in dev', 'Risk.', 'red'), ('config per env', 'YAML / args', 'Fix.', 'green'),
    ('Functions take parameters', 'pure', 'Reuse.', 'green'), ('Same tests everywhere', 'CI', 'Trust.', 'blue'),
    ('Package + entrypoint', 'spark-submit', 'Ship.', 'blue')], ['Hard-coded.', 'Config.', 'Params.', 'Tests.', 'Ship.'], 'scenario-config')
assemble(HERE, h2_story='Code your team can read, test and change', hook_html=hk,
    narration='Kabir’s revenue job is one long notebook. It works, but every change takes a day and reviewers cannot follow it.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Writing clean, modular PySpark',
    formal='<b>Modular PySpark</b> structures a pipeline as small, pure transformation functions with the signature <code>DataFrame → DataFrame</code>, configured through parameters and composed with <code>DataFrame.transform</code>, with input/output isolated at the edges. Combined with plan-aware habits (batched column expressions, early filtering and projection, cheap existence checks), it yields code that is testable, reusable and efficient.',
    simple='Write each step as a small function that takes a table and returns a table, pass settings in, chain the steps, and test each one. A few habits also keep Spark’s plans small.',
    term_rows=[('transform()', 'Apply a function to a DataFrame.'), ('Pure function', 'No hidden I/O or globals.'), ('withColumns', 'Add many columns at once.'), ('toDF(*cols)', 'Rename all columns.'), ('isEmpty()', 'Any rows?'), ('Project node', 'One select step in a plan.'), ('Entrypoint', 'main.py wiring steps.'), ('Config', 'Settings outside code.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Functions make Spark slower.', 'Same optimised plan.', 'Step 1.'),
               ('withColumn in a loop is free.', '21 nodes and 3× build time.', 'Step 2.'),
               ('count() is the way to check for rows.', 'isEmpty() stops early.', 'Step 4.')],
    exam='“How do you structure PySpark code?” Small pure DataFrame → DataFrame functions, parameters/config, DataFrame.transform chains, I/O at edges, tests per function; select/withColumns over looped withColumn, toDF for renames, filter/select early, isEmpty over count, explain for reviews.',
    types_h2='Habits that pay off', types_html=types_html, warn=warn,
    steps_h2='Refactor and measure', steps_intro='All outputs are real: PySpark 4.3.0, local[2], 2,000,000 synthetic orders, pytest 9.',
    steps=steps, two=two, peel_intro='Now peel a clean job.', peel_html=pe,
    scen_intro='Three live scenarios: a big notebook, a slow driver, and three environments.', scen=scen,
    uc_h2='Clean code at work', ucs=[uc_('lib', 'library', 'blue', '1. Team libraries', 'Shared transforms.', ['Functions', '*package', 'Teams']),
        uc_('rev', 'reviews', 'green', '2. Code reviews', 'Small diffs.', ['PR', '*clear', 'Merge']),
        uc_('ci', 'CI', 'violet', '3. CI tests', 'pytest per transform.', ['Commit', '*tests', 'Deploy']),
        uc_('env', 'envs', 'amber', '4. Many environments', 'Config, not edits.', ['Dev/Prod', '*config', 'Same code'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../04-testing-pyspark-code/">11.4 Testing</a>.')
