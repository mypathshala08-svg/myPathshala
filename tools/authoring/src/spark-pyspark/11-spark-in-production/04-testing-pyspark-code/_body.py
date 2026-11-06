import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l114_tests.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
LAB = os.path.join(HERE, '..', '..', 'lab', 'jobs', 'm11', 'testing')
def src(p):
    return open(os.path.join(LAB, p)).read().rstrip()

def pyramid(x, y):
    o = ''
    rows = [('few end-to-end runs', 'cluster, real data', 'violet', 120), ('integration tests', 'read/write, schemas', 'blue', 200), ('unit tests', 'small DataFrames, local[1]', 'green', 280)]
    for k, (a, b, tone, w) in enumerate(rows):
        o += opbox(x + (280 - w) / 2, y + k * 34, a, b, tone, w, 30)
    return o

# ---------------------------------------------------------------- story
sc_ = (pyramid(30, 30) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured (pytest + PySpark 4.3)', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('session fixture: 5.3 s once', 'blue'), ('5 tests in 13.6 s', 'blue'),
           ('4 passed', 'green'), ('1 failed: DIFFERENT_ROWS', 'red'),
           ('diff marks row 2: 60 vs 40', 'amber'), ('row order ignored', 'green')])))
scene_svg = scene('PySpark transformations can be unit-tested like any Python function: build a tiny DataFrame, call the function, compare with an expected DataFrame. We tested a delivery-fee function with pytest, a shared SparkSession fixture and the assertDataFrameEqual helpers from pyspark.testing.', sc_,
                  'Test the logic on <tspan font-weight="700" class="s-acc">four rows</tspan>, not on four billion.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Mumbai customers were charged ₹40”</h2>
  <div class="story">
    <p class="narration">A small change to TiffinGo’s delivery-fee rules went to production on a Friday. Mumbai’s fee should have been ₹60, but a typo charged ₹40 to every Mumbai order all weekend. The job had run perfectly; it just computed the wrong numbers.</p>

{scene_svg}

K> Sir, how do you test a Spark job? It needs a cluster and terabytes of data.
A> The <b>logic</b> does not. Put each transformation in a function that takes a DataFrame and returns a DataFrame. Then test it with four hand-made rows on a local SparkSession, in seconds, on every commit.
R> And compare DataFrames how?
A> PySpark ships <code>pyspark.testing</code> with <code>assertDataFrameEqual</code> and <code>assertSchemaEqual</code>. Today we write five pytest tests for the fee function, including one that fails on purpose so you see the diff. All outputs are real (PySpark 4.3.0, pytest).
  </div>
</section>
'''

lv = '''
LEVELS> Testing at three levels
L1> Tasting before serving
      <ul>
        <li>A cook tastes one spoon of the curry, not the whole pot. A unit test runs your recipe on four rows and checks the taste.</li>
        <li>If the spoon is wrong, the whole pot would have been wrong.</li>
      </ul>
L2> The tools
      <ul>
        <li>pytest with a <code>scope="session"</code> fixture that creates one <code>SparkSession.builder.master("local[1]")</code>.</li>
        <li><code>from pyspark.testing import assertDataFrameEqual, assertSchemaEqual</code> (ignores row order by default, shows a diff).</li>
        <li>Small input DataFrames built with <code>spark.createDataFrame(rows, schema)</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>Starting Spark cost 5.3 s once for the whole test session; 5 tests ran in 13.6 s.</li>
        <li>The failing test printed both sides and marked the different row with <code>!</code>: Mumbai fee 60 vs 40.</li>
        <li>The revenue test passed although rows came back in a different order.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Testing PySpark code</h2>
''' + def_block(
    'Testable PySpark code separates <b>I/O</b> (reading and writing data) from <b>transformations</b>, written as pure functions that take and return DataFrames. <b>Unit tests</b> call these functions on small DataFrames created in the test and compare the result with an expected DataFrame, using a local SparkSession (<code>local[1]</code>, few shuffle partitions, UI disabled) created once per test session through a pytest fixture. PySpark’s <code>pyspark.testing</code> module provides <code>assertDataFrameEqual</code>, which compares rows (ignoring order by default, with tolerances for floating point) and reports differences, and <code>assertSchemaEqual</code> for column names, types and nullability. <b>Integration tests</b> add real reads and writes on small fixtures, and end-to-end runs on a staging cluster complete the test pyramid.',
    'Write each transformation as a function from DataFrame to DataFrame. In tests, build a few rows by hand, run the function on a local Spark, and compare the result with the rows you expect. PySpark has helpers that compare DataFrames and show exactly which rows differ.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Unit test', 'Checks one function on tiny data.'),
    ('Fixture', 'pytest setup shared by tests.'),
    ('scope="session"', 'Create once for all tests.'),
    ('assertDataFrameEqual', 'Compare rows, show a diff.'),
    ('assertSchemaEqual', 'Compare column names and types.'),
    ('Pure function', 'Same input → same output, no I/O.'),
    ('Integration test', 'Includes real reads/writes.'),
    ('CI', 'Tests run on every commit.'),
]) + '''

  <h3>What to test where</h3>
''' + table(['Level', 'What', 'Data', 'Speed'], [
    ['Unit', 'Transformation logic, edge cases', '3–20 hand-made rows', 'Seconds'],
    ['Schema', 'Output columns, types, nullability', 'Same small rows', 'Seconds'],
    ['Integration', 'Readers/writers, partitioning, formats', 'Small files in a temp dir', 'Tens of seconds'],
    ['Data quality', 'Row counts, nulls, ranges on real data', 'Production sample', 'Minutes, in the pipeline'],
], minw=600) + lv + '''
EXAM> “How do you test PySpark code?” Separate I/O from transformations; write transformations as DataFrame-in, DataFrame-out functions; unit-test them with pytest on small DataFrames using a session-scoped local SparkSession; compare with <code>assertDataFrameEqual</code>/<code>assertSchemaEqual</code> (or chispa); add integration tests for reads/writes and run everything in CI.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Useful options</h2>
''' + table(['Need', 'How'], [
    ['Fast local session', '<code>master("local[1]")</code>, <code>spark.sql.shuffle.partitions=1</code>, <code>spark.ui.enabled=false</code>'],
    ['One session for all tests', '<code>@pytest.fixture(scope="session")</code> in <code>conftest.py</code>'],
    ['Order matters', '<code>assertDataFrameEqual(a, b, checkRowOrder=True)</code>'],
    ['Floating point', '<code>assertDataFrameEqual(a, b, rtol=1e-5, atol=1e-8)</code>'],
    ['Compare to Python rows', '<code>assertDataFrameEqual(df, [Row(...), ...])</code>'],
    ['Test against Connect', 'Run the suite with <code>SPARK_REMOTE</code> set (Lesson 11.3)'],
], minw=560) + '''
WARN> Starting a SparkSession costs seconds (5.3 s in our lab). Creating one <b>per test</b> turns a 15-second suite into minutes, and developers stop running it. Use one session-scoped fixture, keep inputs tiny, and avoid <code>.collect()</code> on big generated data in unit tests. Also beware of tests that only check counts: our fee bug would have passed a row-count test.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Five tests for the fee rules</h2>
  <p>All outputs are real: PySpark 4.3.0, pytest, run with <code>python -m pytest -q -s --durations=3 tests</code>. Rule: free delivery from ₹500, otherwise ₹60 in Mumbai and ₹40 elsewhere.</p>
''' + stepper([
    ('Step 1 · The function under test',
     code('python', 'transforms.py', src('transforms.py')),
     'No reading, no writing, no SparkSession inside: just a DataFrame in and a DataFrame out. That is what makes it testable. The job’s main script reads the data, calls these functions and writes the result.'),
    ('Step 2 · One SparkSession for all tests',
     code('python', 'tests/conftest.py', src('tests/conftest.py')),
     'pytest creates the session the first time a test asks for <code>spark</code> and reuses it for every other test. One partition, one core and no UI keep it light. In our run it started once in <b>5.3 s</b>.'),
    ('Step 3 · The tests',
     code('python', 'tests/test_transforms.py', src('tests/test_transforms.py')),
     'Four rows cover every branch: Pune under ₹500 (₹40), Mumbai under ₹500 (₹60), Mumbai over ₹500 (free) and exactly ₹500 (free, the boundary). <code>assertDataFrameEqual</code> compares whole DataFrames; <code>assertSchemaEqual</code> checks names and types, including that <code>delivery_fee</code> is a non-nullable int. The last test is deliberately wrong.'),
    ('Step 4 · Running them',
     code('bash', 'pytest', 'python -m pytest -q -s --durations=3 tests', sec('[fixture]')),
     'Four dots passed, one <b>F</b> failed. The failure shows both sides and marks the differing row with <code>!</code>: actual Mumbai fee 60, expected 40, “25% of rows differ”. That is exactly the message that would have caught the weekend bug before release. The revenue test passed even though groupBy returns rows in any order. The whole suite: <b>13.6 s</b>, most of it Spark start-up.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('def add_delivery_fee(orders):', W), ('  >= 500 -> 0', G), ('  Mumbai -> 60, else 40', G)], size=7.4),
    term([('@pytest.fixture(scope="session")', W), ('[fixture] SparkSession started', W), ('  in 5.3 s (once)', G)], size=7.2),
    term([('....F', Y), ('[DIFFERENT_ROWS] ( 25.00000 % )', RD), ('! Row(order_id=2, delivery_fee=60)', RD), ('! Row(order_id=2, delivery_fee=40)', RD)], size=7.0),
    term([('1 failed, 4 passed in 13.60s', Y), ('6.64s setup test_fee_rules', W)], size=7.4),
]
B1 = [
    t(180, 14, 'I/O outside, logic inside', 9.4, bold=True) + flow([('read', 'main job', 'card'), ('transform', 'pure function', 'green'), ('write', 'main job', 'card')], y=50, w=96, gap=16) + cap('Only the middle needs unit tests.', '', 'green', y=144, h=30),
    t(180, 14, 'Session fixture', 9.4, bold=True) + opbox(20, 46, 'SparkSession', 'created once', 'acc', 110, 34) + ''.join(arrow(132, 63, 200, 36 + k * 18, 'ink3', 1) + opbox(204, 26 + k * 18, f'test {k + 1}', '', 'green', 80, 16) for k in range(5)) + cap('Pay start-up once.', '', 'blue', y=144, h=30),
    t(180, 14, 'Compare whole DataFrames', 9.4, bold=True) + opbox(20, 46, 'actual', '4 rows', 'blue', 100, 34) + t(180, 66, '≟', 14, 'ink2') + opbox(240, 46, 'expected', '4 rows', 'violet', 100, 34) + cap('Diff marks the wrong row.', '', 'red', y=144, h=30),
    t(180, 14, 'The test pyramid', 9.4, bold=True) + pyramid(40, 34) + cap('Many small, few big.', '', 'green', y=144, h=30),
]
see_caps = ['The function.', 'Session fixture.', 'A failing test.', 'Suite time.']
behind_caps = ['Separate I/O.', 'One session.', 'DataFrame comparison.', 'Test pyramid.']
two = anim_two('Testing PySpark', 'Small data, real checks', 'Real lab outputs', 'How it works', see, B1, see_caps, behind_caps)

e1 = (t(180, 22, 'Fee change on Friday', 9.4, bold=True) + t(180, 56, 'no tests, straight to prod', 8.4, 'ink2') + cap('Mumbai charged ₹40.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Weekend of wrong fees', 9.4, bold=True) + t(180, 56, 'job ran perfectly', 8.4, 'ink2') + cap('Logic bug.', '', 'red', y=150, h=34))
e3 = (t(180, 22, 'Add 4-row unit tests', 9.4, bold=True) + t(180, 56, 'one row per branch', 8.4, 'ink2') + cap('Plus the boundary.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'CI runs them on every PR', 9.4, bold=True) + t(180, 56, '~15 s per run', 8.4, 'ink2') + cap('Cheap.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Diff shows the bug', 9.4, 'acc', bold=True) + t(180, 56, 'row 2: 60 vs 40', 8.4, 'ink2') + cap('Caught before merge.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'The ₹40 weekend',
              'Unit tests for business rules. (Typical; diff from our lab.)',
              'Business rules', 'Small DataFrame tests per rule branch catch logic bugs before release', [e1, e2, e3, e4, e5],
              ['Change.', 'Bug.', 'Tests.', 'CI.', 'Caught.'],
              hid='scenario-fee')
b1 = (t(180, 22, 'Test suite takes 9 minutes', 9.4, bold=True) + t(180, 56, 'nobody runs it locally', 8.4, 'ink2') + cap('Tests skipped.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'A SparkSession per test', 9.4, bold=True) + t(180, 56, '~5 s × 100 tests', 8.4, 'ink2') + cap('Start-up dominates.', '', 'red', y=150, h=34))
b3 = (t(180, 22, 'Session-scoped fixture', 9.4, bold=True) + t(180, 56, 'conftest.py, created once', 8.4, 'ink2') + cap('5.3 s once (lab).', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'local[1], 1 shuffle partition', 9.4, bold=True) + t(180, 56, 'UI off, tiny inputs', 8.4, 'ink2') + cap('Less overhead.', '', 'green', y=150, h=34))
b5 = (t(180, 22, '9 min → under 1 min', 9.4, 'acc', bold=True) + t(180, 56, 'tests run again', 8.4, 'ink2') + cap('Fast feedback.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'The nine-minute test suite',
              'Fast PySpark tests. (Typical; start-up time from our lab.)',
              'Fast tests', 'One session-scoped SparkSession and tiny inputs keep PySpark tests fast', [b1, b2, b3, b4, b5],
              ['Slow.', 'Per test.', 'Fixture.', 'Settings.', 'Fast.'],
              hid='scenario-fast')
u1 = (t(180, 22, 'Logic tested, job still broke', 9.4, bold=True) + t(180, 56, 'upstream added a column type change', 8.2, 'ink2') + cap('amount became string.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Schema test on outputs', 9.4, bold=True) + t(180, 56, 'assertSchemaEqual', 8.4, 'ink', mono=True) + cap('Catches type drift.', '', 'green', y=150, h=34))
u3 = (t(180, 22, 'Integration test', 9.4, bold=True) + t(180, 56, 'read a sample file, write to tmp', 8.4, 'ink2') + cap('Real formats.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Data quality in pipeline', 9.4, bold=True) + t(180, 56, 'nulls, ranges, row counts', 8.4, 'ink2') + cap('On real data.', '', 'amber', y=150, h=34))
u5 = (t(180, 22, 'Layers of safety', 9.4, 'acc', bold=True) + t(180, 56, 'unit · schema · integration · DQ', 8.2, 'ink2') + cap('Defence in depth.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'When unit tests are not enough',
              'Schema, integration and data-quality tests. (Typical.)',
              'Test layers', 'Combine unit, schema, integration and data-quality checks for Spark pipelines', [u1, u2, u3, u4, u5],
              ['Broke.', 'Schema.', 'Integration.', 'DQ.', 'Layers.'],
              hid='scenario-layers')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Small data, real checks</h2>
  <p>Left: real outputs. Right: how the tests are structured.</p>
''' + two + '''
  <p>Three live scenarios follow: a pricing bug, a slow test suite, and the limits of unit tests.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Testing at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'CI', 12, 'blue', bold=True) + t(60, 58, 'every PR', 7.4, 'ink2'),
    '1. Pull-request checks',
    'GitHub Actions runs the PySpark test suite on every pull request.',
    ['PR', '*pytest', 'Merge if green']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'rules', 12, 'green', bold=True) + t(60, 58, 'pricing', 7.4, 'ink2'),
    '2. Business rules',
    'Fees, discounts and taxes each get table-driven tests with boundary rows.',
    ['Rule table', '*parametrized tests', 'Confidence']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'schema', 11, 'violet', bold=True) + t(60, 58, 'contracts', 7.4, 'ink2'),
    '3. Data contracts',
    'Output schemas are asserted so downstream teams are not surprised.',
    ['Output', '*assertSchemaEqual', 'Contract kept']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'upgrade', 10, 'acc', bold=True) + t(60, 58, 'Spark', 7.4, 'ink2'),
    '4. Spark upgrades',
    'The same suite runs on the new Spark version before the platform switches.',
    ['Spark 4.x', '*same tests', 'Safe upgrade']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'DQ', 12, 'acc', bold=True) + t(60, 58, 'pipeline', 7.4, 'ink2'),
    '5. Data quality gates',
    'Pipelines check counts, nulls and ranges on real data before publishing.',
    ['Daily data', '*checks', 'Publish or stop']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> creating DataFrames and schemas in <a href="../../04-dataframes/02-creating-dataframes-and-schemas/">4.2</a>, columns and <code>when</code> in <a href="../../04-dataframes/03-working-with-columns/">4.3</a>; basic pytest helps.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
