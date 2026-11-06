import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='12-spark-in-industry', lesson='03-whats-new-in-spark-4', n='12.3',
    module_label='Module 12 · Spark in industry',
    title='What’s new in Spark 4',
    desc='A hands-on tour of Spark 4.0 to 4.3 on PySpark 4.3.0: ANSI SQL mode by default (DIVIDE_BY_ZERO, CAST_INVALID_INPUT) and try_cast/try_divide, pipe syntax, session variables, UTF8_LCASE collation, SQL scripting with WHILE loops and recursive CTEs (4.1), Python UDTFs and the Python Data Source API, GEOMETRY types (4.2), and Spark 4.3’s UNNEST, jaro_winkler_similarity and flag-gated ASOF JOIN, plus an upgrade checklist from Spark 3.5.',
    og_desc='Spark 4 breaks silent NULLs and adds SQL scripting, Python data sources, geospatial types and ASOF joins: a tour with real outputs on 4.3.0.',
    minutes=28, level='Intermediate',
    lead='Spark 4 changed defaults and added a lot. This lesson tours <b>Spark 4.0 to 4.3</b> on PySpark 4.3.0: <b>ANSI mode</b> and safe <code>try_</code> functions, modern SQL (pipes, variables, collations, scripting), Python UDTFs and data sources, geospatial types and <b>ASOF JOIN</b>, with an upgrade checklist. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', '4.0 → 4.3 features', 'Upgrade checklist', 'Runs in your browser (Python)'],
)

MAIN = '''# ANSI mode vs legacy behaviour, modelled in Python
def cast_int(s, ansi=True):
    try:
        return int(s)
    except ValueError:
        if ansi:
            raise ValueError(f"[CAST_INVALID_INPUT] '{s}' cannot be cast to INT")
        return None                      # Spark 3 default: silent NULL

def try_cast_int(s):
    try:
        return int(s)
    except ValueError:
        return None

phones = ["9820012345", "N/A", "9822254321"]
print("legacy :", [cast_int(p, ansi=False) for p in phones])
print("try_cast:", [try_cast_int(p) for p in phones])
try:
    print("ANSI   :", [cast_int(p) for p in phones])
except ValueError as e:
    print("ANSI   : ERROR", e)
'''
RUN = dict(
    heading='Run the code: ANSI mode',
    intro='<p>Why the upgrade broke the job, in plain Python. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('        return None                      # Spark 3 default: silent NULL', 'Spark 3 (ANSI off) turned bad values into NULL without telling anyone.'),
        ('    print("ANSI   :", [cast_int(p) for p in phones])', 'Spark 4 (ANSI on) raises CAST_INVALID_INPUT, exposing the bad row.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then remove "N/A" from the list.', code=None),
        dict(label='2 · Predict first: try_divide', hint='<b>Predict first:</b> what does try_divide(1, 0) return?',
             code='''def try_divide(a, b):
    return None if b == 0 else a / b
print(try_divide(1, 0), try_divide(10, 4))
'''),
        dict(label='3 · Collation', hint='Group cities case-insensitively.',
             code='''from collections import Counter
rows = [("Mumbai", 300), ("MUMBAI", 200), ("Pune", 450)]
c = Counter()
for city, amt in rows:
    c[city.lower()] += amt
print(dict(c))
'''),
        dict(label='4 · SQL script loop', hint='The lab’s WHILE loop.',
             code='''total, i = 0, 1
while i <= 4:
    total += i * 100
    i += 1
print(total)
'''),
        dict(label='5 · Spot the error', hint='ASOF JOIN without enabling it.', expect='error',
             code='''conf = {"spark.sql.join.asofJoin.enabled": "false"}
assert conf["spark.sql.join.asofJoin.enabled"] == "true", "[UNSUPPORTED_FEATURE.ASOF_JOIN] enable spark.sql.join.asofJoin.enabled"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: Spark 4 features',
    intro='<p>In the <code>pyspark</code> 4.3 shell. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · ANSI', cmd='spark.sql("SELECT 1/0").collect()', file='pyspark',
             output='[DIVIDE_BY_ZERO] Division by zero. Use `try_divide` to tolerate divisor being 0 and return NULL instead. …', note='On by default.'),
        dict(title='2 · Collation', cmd='spark.sql("SELECT city COLLATE UTF8_LCASE AS c, sum(amount) FROM o GROUP BY 1").collect()', file='pyspark',
             output="[Row(c='Mumbai', sum(amount)=500), Row(c='Pune', sum(amount)=450)]", note='Case-insensitive.'),
        dict(title='3 · Recursive CTE', cmd='spark.sql("WITH RECURSIVE r(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM r WHERE n < 5) SELECT sum(n) FROM r").first()[0]', file='pyspark',
             output='15', note='Spark 4.1+.'),
    ],
)

TRACE = dict(
    heading='A UDTF in miniature',
    intro='<p>One input row becomes several output rows.</p>',
    code='''order = "dosa:2, idli:3, vada:1"
rows = []
for part in order.split(","):
    name, qty = part.split(":")
    rows.append((name.strip(), int(qty)))
print(rows)
''',
    notes={3: 'eval :: Called once per input value.', 5: 'yield :: Each tuple becomes an output row.'},
)

WORKED_INTRO = 'Three Spark 4 decisions at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='Spark 4 · ANSI', title='Fix a failing cast',
         problem='<p><code>CAST(phone AS BIGINT)</code> fails on “N/A”.</p>',
         inp='phone strings',
         approach=['Keep ANSI on.', 'Use try_cast for intended NULLs.', 'Quarantine invalid rows.'],
         code='''print("SELECT try_cast(phone AS BIGINT) AS phone_num, phone FROM customers")
print("-- WHERE try_cast(phone AS BIGINT) IS NULL AND phone IS NOT NULL  -> quarantine")
''', notes={1: 'Explicit :: Intent is visible in the SQL.'},
         tryit='Step 1.'),
    dict(level='i', tag='Spark 4 · SQL', title='Parameterise SQL safely',
         problem='<p>Analysts paste values into SQL strings.</p>',
         inp='filter value',
         approach=['DECLARE VARIABLE.', 'SET VAR to change it.', 'Or named parameters in spark.sql.'],
         code='''print("DECLARE VARIABLE min_amt INT DEFAULT 250;")
print("SELECT * FROM o WHERE amount >= min_amt;")
''', notes={1: 'Safe :: No string injection (Lesson 7.1).'},
         tryit='Step 2.'),
    dict(level='a', tag='Spark 4 · upgrade', title='Plan the 3.5 → 4.x upgrade',
         problem='<p>200 jobs on Spark 3.5.</p>',
         inp='checklist',
         approach=['Java 17+, Scala 2.13 connectors.', 'Run tests with ANSI on.', 'Check platform and table-format versions.'],
         code='''steps = ["JDK 17/21", "_2.13 jars", "tests with ANSI", "try_* fixes", "Delta/Iceberg versions", "canary jobs"]
print(" -> ".join(steps))
''', notes={1: 'Gradual :: Canary jobs first.'},
         tryit='Types table.'),
]

QUIZ = mix([
    dict(q='Beginner: Biggest default change in Spark 4.0?', options=['RDDs removed', 'ANSI SQL mode on', 'Python 2', 'No SQL'], answer=1,
         why='Errors instead of NULLs.'),
    dict(q='Beginner: SELECT 1/0 in Spark 4 by default…', options=['NULL', 'DIVIDE_BY_ZERO error', 'Infinity', '0'], answer=1,
         why='Use try_divide.'),
    dict(q='Beginner: Minimum Java for Spark 4?', options=['8', '11', '17', '25'], answer=2,
         why='21 also supported.'),
    dict(q='Intermediate: try_cast(\'12a\' AS INT) returns…', options=['Error', 'NULL', '12', '0'], answer=1,
         why='Explicitly tolerant.'),
    dict(q='Intermediate: UTF8_LCASE collation makes…', options=['Text lowercase', 'Mumbai equal MUMBAI in comparisons', 'Sorting faster', 'Unicode illegal'], answer=1,
         why='Grouped to 500.'),
    dict(q='Intermediate: SQL scripting (BEGIN … END) became GA in…', options=['3.5', '4.0', '4.1', '4.3'], answer=2,
         why='On by default.'),
    dict(q='Advanced: A Python UDTF returns…', options=['One value', 'Many rows per input', 'A model', 'A file'], answer=1,
         why='3 items from 1 order.'),
    dict(q='Advanced: ASOF JOIN in Spark 4.3 by default…', options=['Works', 'Is disabled (flag needed)', 'Is removed', 'Only in Scala'], answer=1,
         why='spark.sql.join.asofJoin.enabled.'),
])

REVISION = [
    'Spark 4.0: ANSI default, Java 17+, Scala 2.13, VARIANT, collations, pipe SQL, variables, UDTF, Python data sources, Connect.',
    'ANSI: 1/0 and bad casts fail; use try_divide/try_cast; do not disable globally.',
    '4.1: SQL scripting GA, recursive CTE, Declarative Pipelines, Real-Time Mode.',
    '4.2: GEOMETRY/GEOGRAPHY, CDC, Arrow Python UDFs default.',
    '4.3 (Oct 2026): ASOF JOIN (flag), JSON_TABLE, UNNEST, stateful RTM, quarterly cadence.',
    'Lab: script 1000, CTE 15, UDTF 3 rows, LCASE 500, ASOF 10→1.0, 25→1.5.',
    'Upgrade: JDK, Scala 2.13 jars, ANSI tests, platform/table-format versions.',
]
FAQ = [
    ('Can I turn ANSI mode off?', 'Yes (spark.sql.ansi.enabled=false), but it restores silent NULLs; use it only as a short bridge while fixing queries.'),
    ('Is Spark 5 coming?', 'The 4.x line continues with quarterly feature releases from 4.3; follow the Apache Spark news page for plans.'),
    ('What are Spark Declarative Pipelines?', 'A 4.1+ framework where you declare datasets and flows in Python or SQL, and Spark handles ordering, checkpoints and retries.'),
    ('Do these features exist on my platform?', 'Only if its runtime includes that Spark version; see Lesson 12.1 for November 2026 versions.'),
    ('Where do I learn about each new release?', 'The release notes at spark.apache.org/releases and the Spark docs’ migration guides.'),
]

PRACTICE_INTRO = 'Programs about Spark 4 behaviour.'
PROBLEMS = [
    dict(level='easy', title='try_divide', stmt='Safe division.', inp='a, b',
         code='''def try_divide(a, b):
    return None if b == 0 else a / b
print(try_divide(10, 0))
''', explain='NULL instead of error.'),
    dict(level='easy', title='Recursive sum', stmt='Sum 1..5 like the CTE.', inp='5',
         code='''print(sum(range(1, 6)))
''', explain='15.'),
    dict(level='easy', title='Loop', stmt='The WHILE script.', inp='i 1..4',
         code='''print(sum(i * 100 for i in range(1, 5)))
''', explain='1000.'),
    dict(level='medium', title='Quarantine', stmt='Split valid/invalid phones.', inp='list',
         code='''p = ["9820012345", "N/A", "98222"]
ok = [x for x in p if x.isdigit() and len(x) == 10]
print(ok, [x for x in p if x not in ok])
''', explain='Route bad rows aside.'),
    dict(level='medium', title='ASOF', stmt='Latest surge at or before each order time.', inp='times',
         code='''surge = [(5, 1.0), (20, 1.5)]
for t in (10, 25):
    print(t, max((s for s in surge if s[0] <= t))[1])
''', explain='10 → 1.0, 25 → 1.5.'),
    dict(level='medium', title='Version gate', stmt='Can a 4.1 runtime use ASOF JOIN?', inp='(4,1) vs (4,3)',
         code='''print((4, 1) >= (4, 3))
''', explain='No.'),
    dict(level='business', title='Bad rows found', stmt='Phones that silently became NULL for 2 years at 50/day.', inp='50 × 730',
         code='''print(50 * 730)
''', explain='ANSI exposes them.'),
    dict(level='business', title='Upgrade plan', stmt='Weeks to migrate 200 jobs at 25/week.', inp='200, 25',
         code='''print(200 // 25, "weeks")
''', explain='Batch the upgrade.'),
]

SCN_INTRO = 'Spark 4 questions check that your knowledge is current.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“What is new in Spark 4?”',
        'Name the main changes.',
        'highlights?',
        '<p>ANSI SQL mode on by default; Java 17+ and Scala 2.13; VARIANT for semi-structured data; collations, pipe syntax, session variables; Python UDTFs and data sources; Spark Connect. Later 4.x releases added SQL scripting, Declarative Pipelines, geospatial types and ASOF joins.</p>', 'Only mentioning performance.') +
    scn('Data engineering', 'Mid-level', 'Upgrade failure',
        'After upgrading, jobs fail with CAST_INVALID_INPUT.',
        'fix?',
        '''<ul>
          <li>It is ANSI mode exposing bad data.</li>
          <li>Use try_cast where NULL is acceptable; quarantine invalid rows.</li>
          <li>Avoid globally disabling ANSI.</li>
        </ul>''', 'Setting ansi.enabled=false everywhere.') +
    scn('Data engineering', 'Mid-level', 'Custom source',
        'Read data from an internal REST API into Spark.',
        'approach?',
        '''<ol>
          <li>Python Data Source API: schema + reader.</li>
          <li>Partitions for parallel calls.</li>
          <li>Register and use spark.read.format(...).</li>
        </ol>''', 'Collecting the API response on the driver.') +
    scn('Platform', 'Senior', 'Version strategy',
        'How do you keep 300 jobs current with quarterly Spark releases?',
        'strategy?',
        '''<ul>
          <li>Track platform LTS runtimes; upgrade yearly.</li>
          <li>Test suites with the new version in CI (Lesson 11.4).</li>
          <li>Feature flags for new opt-in features; canary rollouts.</li>
        </ul>''', 'Upgrading every job immediately.')
)
