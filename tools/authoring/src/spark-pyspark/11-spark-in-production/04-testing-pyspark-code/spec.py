import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='11-spark-in-production', lesson='04-testing-pyspark-code', n='11.4',
    module_label='Module 11 · Spark in production',
    title='Testing PySpark code',
    desc='Unit-testing PySpark with pytest and pyspark.testing (PySpark 4.3.0): a pure delivery-fee transformation, a session-scoped SparkSession fixture started once in 5.3 s, assertDataFrameEqual (row order ignored) and assertSchemaEqual, a deliberately failing test whose DIFFERENT_ROWS diff marks the wrong Mumbai fee (60 vs 40), a 13.6 s suite, and the test pyramid from unit to data-quality checks.',
    og_desc='Catch a pricing bug before release: pytest + assertDataFrameEqual tests for PySpark transformations, with a real failing diff.',
    minutes=24, level='Intermediate',
    lead='Spark jobs can compute the wrong numbers without failing. This lesson writes <b>pytest</b> tests for a fee transformation using a shared local SparkSession and <code>pyspark.testing</code>, reads a real failure diff, and places unit tests in a wider testing strategy. <b>All outputs are real</b> (PySpark 4.3.0, pytest).',
    chips=['PySpark 4.3.0', 'pytest', 'assertDataFrameEqual', 'Runs in your browser (Python)'],
)

MAIN = '''# The fee rule as plain Python, with table-driven tests
def fee(city, amount):
    if amount >= 500:
        return 0
    return 60 if city == "Mumbai" else 40

cases = [("Pune", 450, 40), ("Mumbai", 300, 60), ("Mumbai", 800, 0), ("Delhi", 500, 0), ("Mumbai", 499, 60)]
failed = 0
for city, amount, expected in cases:
    got = fee(city, amount)
    status = "ok " if got == expected else "FAIL"
    failed += got != expected
    print(f"{status} {city:7} {amount:4} -> {got} (expected {expected})")
print(len(cases) - failed, "passed,", failed, "failed")
'''
RUN = dict(
    heading='Run the code: table-driven tests',
    intro='<p>The same rule and cases as the lab, in plain Python. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('cases = [("Pune", 450, 40), ("Mumbai", 300, 60), ("Mumbai", 800, 0), ("Delhi", 500, 0), ("Mumbai", 499, 60)]', 'One row per branch plus the boundaries (499 and 500).'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then introduce the bug: Mumbai → 40.', code=None),
        dict(label='2 · Predict first: diff share', hint='<b>Predict first:</b> 1 of 4 rows differs.',
             code='''print(1 / 4 * 100, "% of rows differ")
'''),
        dict(label='3 · Order-insensitive compare', hint='Compare rows ignoring order.',
             code='''actual = [("Pune", 450), ("Delhi", 500), ("Mumbai", 1100)]
expected = [("Delhi", 500), ("Mumbai", 1100), ("Pune", 450)]
print(sorted(actual) == sorted(expected))
'''),
        dict(label='4 · Suite time', hint='Per-test vs shared session.',
             code='''tests, startup, per_test = 100, 5.3, 0.4
print("per-test sessions:", round(tests * (startup + per_test)), "s | shared:", round(startup + tests * per_test), "s")
'''),
        dict(label='5 · Spot the error', hint='The weekend bug as a failing test.', expect='error',
             code='''def fee(city, amount):
    return 0 if amount >= 500 else 40      # typo: Mumbai should be 60
assert fee("Mumbai", 300) == 60, "DIFFERENT_ROWS: Row(order_id=2, delivery_fee=40) vs expected 60"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: pytest',
    intro='<p>In the lab’s <code>testing</code> folder with <code>pip install pytest</code>. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Run the suite', cmd='python -m pytest -q tests', file='bash',
             output='....F\n…\n1 failed, 4 passed in 13.60s', note='One deliberate failure.'),
        dict(title='2 · Slowest steps', cmd='python -m pytest -q --durations=3 tests', file='bash',
             output='6.64s setup    tests/test_transforms.py::test_fee_rules', note='Session start-up.'),
        dict(title='3 · Import the helpers', cmd='from pyspark.testing import assertDataFrameEqual, assertSchemaEqual', file='python',
             output='', note='Built into PySpark 3.5+.'),
    ],
)

TRACE = dict(
    heading='How a DataFrame diff is found',
    intro='<p>Compare sorted rows and mark differences.</p>',
    code='''actual = [(1, 40), (2, 60), (3, 0)]
expected = [(1, 40), (2, 40), (3, 0)]
diff = []
for a, e in zip(sorted(actual), sorted(expected)):
    if a != e:
        diff.append((a, e))
print(diff)
''',
    notes={4: 'Sort :: Order is ignored by default.', 6: 'Mark :: These rows get a ! in the report.'},
)

WORKED_INTRO = 'Three testing decisions at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='Testing · structure', title='Make a job testable',
         problem='<p>A 300-line script reads, transforms and writes in one function.</p>',
         inp='monolithic job',
         approach=['Extract transformations into functions.', 'Keep read/write in main().', 'Test the functions.'],
         code='''layout = {"main.py": "read -> transform -> write", "transforms.py": "pure functions", "tests/": "pytest"}
print(layout)
''', notes={1: 'Pure :: No I/O inside transformations.'},
         tryit='Step 1.'),
    dict(level='i', tag='Testing · cases', title='Choose test rows',
         problem='<p>Test a discount: 10% above ₹1000, 20% for Gold above ₹1000.</p>',
         inp='rule',
         approach=['One row per branch.', 'Boundary values 999/1000.', 'Nulls if allowed.'],
         code='''rows = [("Free", 999), ("Free", 1000), ("Gold", 1000), ("Gold", 500), ("Gold", None)]
print(len(rows), "rows cover the rule")
''', notes={2: 'Boundaries :: Most bugs live at the edges.'},
         tryit='Step 3.'),
    dict(level='a', tag='Testing · CI', title='Run tests in CI',
         problem='<p>Run the suite on every pull request.</p>',
         inp='GitHub Actions',
         approach=['Set up Java 17+ and Python.', 'pip install pyspark pytest.', 'pytest -q.'],
         code='''steps = ["actions/setup-java (17)", "actions/setup-python", "pip install pyspark==4.3.0 pytest", "pytest -q"]
print("\\n".join(steps))
''', notes={1: 'Java :: PySpark needs a JVM in CI.'},
         tryit='Scenario 1.'),
]

QUIZ = mix([
    dict(q='Beginner: Best unit of PySpark testing?', options=['The whole job', 'A DataFrame-in/DataFrame-out function', 'The cluster', 'The Spark UI'], answer=1,
         why='Pure transformations.'),
    dict(q='Beginner: Helper to compare DataFrames?', options=['df.equals', 'assertDataFrameEqual', 'df.compare', 'assert df == df2'], answer=1,
         why='pyspark.testing.'),
    dict(q='Beginner: Master for unit tests?', options=['yarn', 'local[1]', 'k8s', 'spark://'], answer=1,
         why='Small and fast.'),
    dict(q='Intermediate: Why scope="session" for the Spark fixture?', options=['Required', 'Start Spark once (5.3 s)', 'Isolation', 'Logging'], answer=1,
         why='Start-up dominates.'),
    dict(q='Intermediate: Does assertDataFrameEqual care about row order by default?', options=['Yes', 'No', 'Only for ints', 'Only with sort'], answer=1,
         why='checkRowOrder=False.'),
    dict(q='Intermediate: The lab failure reported…', options=['A stack trace only', 'Both sides with the differing row marked', 'Counts only', 'Nothing'], answer=1,
         why='! Row(order_id=2…).'),
    dict(q='Advanced: Which test catches a column turning from long to string?', options=['Row count', 'assertSchemaEqual', 'Spark UI', 'None'], answer=1,
         why='Schema test.'),
    dict(q='Advanced: Why can count-only tests miss bugs?', options=['They are slow', 'Wrong values keep the same count', 'They need clusters', 'They are flaky'], answer=1,
         why='The fee bug kept 4 rows.'),
])

REVISION = [
    'Separate I/O from transformations; test the transformations.',
    'pytest + session-scoped local SparkSession (5.3 s once).',
    'assertDataFrameEqual: row-order-insensitive diff; assertSchemaEqual for types.',
    'One input row per branch plus boundaries.',
    'Lab: 4 passed, 1 failed with DIFFERENT_ROWS (60 vs 40), 13.6 s.',
    'Counts alone miss logic bugs.',
    'Add integration and data-quality checks; run tests in CI.',
]
FAQ = [
    ('What about chispa?', 'A popular library with similar DataFrame assertions; pyspark.testing now covers the common cases built in.'),
    ('Can I test with pandas instead of Spark?', 'For logic written in pandas UDFs, test the pandas function directly; for DataFrame code, use a local Spark.'),
    ('How do I test code that reads files?', 'Write small fixture files into pytest’s tmp_path and point the reader at them (integration test).'),
    ('Should tests use production data?', 'Not unit tests; use small, deliberate rows. Production samples belong in data-quality checks.'),
    ('How do I test streaming code?', 'Use file or rate sources with availableNow and memory/foreachBatch sinks, as in Module 9’s labs.'),
]

PRACTICE_INTRO = 'Programs about test design.'
PROBLEMS = [
    dict(level='easy', title='Fee', stmt='Fee for Mumbai ₹300.', inp='rule',
         code='''print(0 if 300 >= 500 else 60)
''', explain='60.'),
    dict(level='easy', title='Diff %', stmt='Rows differing: 1 of 4.', inp='1, 4',
         code='''print(25.0)
''', explain='As in the report.'),
    dict(level='easy', title='Suite time', stmt='Time for 5 tests sharing a 5.3 s start.', inp='13.6 s total',
         code='''print(round(13.6 - 5.3, 1), "s of actual tests")
''', explain='Start-up is a big share.'),
    dict(level='medium', title='Boundaries', stmt='Values to test around ₹500.', inp='500',
         code='''print([499, 500, 501])
''', explain='Edges.'),
    dict(level='medium', title='Schema compare', stmt='Compare (name, type) lists.', inp='schemas',
         code='''a = [("order_id", "long"), ("total", "long")]
b = [("order_id", "long"), ("total", "string")]
print([x for x, y in zip(a, b) if x != y])
''', explain='Type drift found.'),
    dict(level='medium', title='Parametrize', stmt='Generate test ids.', inp='cases',
         code='''cases = [("Pune", 450), ("Mumbai", 300)]
print([f"{c}-{a}" for c, a in cases])
''', explain='pytest.mark.parametrize ids.'),
    dict(level='business', title='Bug cost', stmt='Undercharge for 12,000 Mumbai orders × ₹20.', inp='12000, 20',
         code='''print("₹", 12000 * 20)
''', explain='₹2.4 lakh in one weekend.'),
    dict(level='business', title='CI minutes', stmt='Monthly CI minutes for 400 PRs × 1 min.', inp='400',
         code='''print(400, "minutes")
''', explain='Cheap insurance.'),
]

SCN_INTRO = 'Testing questions separate production engineers from notebook users.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“How do you unit-test PySpark?”',
        'Describe your approach.',
        'tools?',
        '<p>Put transformations in functions that take and return DataFrames; in pytest, create a local SparkSession once (session fixture), build small input DataFrames, call the function and compare with assertDataFrameEqual / assertSchemaEqual.</p>', 'Testing only by running the whole job.') +
    scn('Data engineering', 'Mid-level', 'Slow tests',
        'The PySpark test suite takes 10 minutes.',
        'improve?',
        '''<ul>
          <li>One session-scoped SparkSession.</li>
          <li>local[1], 1 shuffle partition, UI off.</li>
          <li>Tiny inputs; avoid big generated data.</li>
        </ul>''', 'Removing tests.') +
    scn('Data engineering', 'Mid-level', 'Good test data',
        'Which rows do you put in a test?',
        'strategy?',
        '''<ol>
          <li>One row per rule branch.</li>
          <li>Boundary values and nulls.</li>
          <li>Expected output written by hand, reviewed with the business.</li>
        </ol>''', 'Copying a production sample.') +
    scn('Platform', 'Senior', 'Quality strategy',
        'Design testing for 100 Spark pipelines.',
        'layers?',
        '''<ul>
          <li>Unit + schema tests in CI on every PR.</li>
          <li>Integration tests with fixture files.</li>
          <li>Data-quality gates in production runs.</li>
        </ul>''', 'Only manual checks of dashboards.')
)
