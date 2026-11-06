import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from hivekit import tables
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
BODY = body(HERE)

META = dict(
    module='09-extending-hive', lesson='01-user-defined-functions', n='9.1',
    module_label='Module 9 · Extending Hive',
    title='User-defined functions: UDF, UDAF and UDTF in Java',
    desc='Write Hive user-defined functions in Java and run them on Hive 4.2.1: a GenericUDF that normalises city names, a GenericUDAF (spread = max − min) with partial aggregation, and a GenericUDTF used with LATERAL VIEW. Covers ADD JAR, temporary vs permanent functions (CREATE FUNCTION … USING JAR), the metastore FUNCS tables, SHOW FUNCTIONS LIKE in Hive 4, a real UDTF initialize() pitfall, vectorisation through VectorUDFAdaptor, timings against built-ins, macros and versioned deployments.',
    og_desc='Three Java functions for TiffinGo, compiled and run on Hive 4.2.1: UDF, UDAF and UDTF, with the two errors the tutorials don’t warn you about.',
    minutes=45, level='Intermediate → Advanced',
    lead='Module 9 is about extending Hive. This lesson writes all three kinds of Java functions for TiffinGo, a <b>UDF</b>, a <b>UDAF</b> and a <b>UDTF</b>, registers them for a session and permanently, finds them in the metastore, and measures their cost. <b>All outputs are real</b>, from Hive 4.2.1; the Java sources are in the course lab folder (<code>tools/authoring/src/hive/lab/udf</code>).',
    chips=['Real Java, real Hive 4.2.1', 'UDF · UDAF · UDTF', 'Two real pitfalls', 'Runs in your browser (Python)'],
)

MAIN = '''# The normalize_city rule in Python: same logic as the Java GenericUDF
OLD = {"bombay": "Mumbai", "bangalore": "Bengaluru", "madras": "Chennai",
       "calcutta": "Kolkata", "poona": "Pune", "gurgaon": "Gurugram"}

def normalize_city(raw):
    if raw is None:
        return None
    s = " ".join(raw.split())              # trim and squeeze spaces
    if not s:
        return None
    return OLD.get(s.lower()) or " ".join(w.capitalize() for w in s.lower().split(" "))

for raw in ["  bombay ", "BANGALORE", "navi   mumbai", "Pune", "", None]:
    print(repr(raw), "->", normalize_city(raw))
'''
RUN = dict(
    heading='Run the code: the three function shapes in Python',
    intro='<p>The same logic as the Java classes, small enough to run in your browser. The outputs match Hive’s. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    if raw is None:', 'Hive passes NULL as null. A UDF must handle it, usually by returning NULL.'),
        ('    return OLD.get(s.lower()) or " ".join(w.capitalize() for w in s.lower().split(" "))', 'Map known old names first, otherwise title-case each word, exactly like evaluate() in Java.'),
    ],
    tasks=[
        dict(label='1 · One row in, one value out', hint='Press <b>Run</b>. Compare with Step 2: Mumbai, Bengaluru, Navi Mumbai, Pune, None, None.', code=None),
        dict(label='2 · Predict first: UDAF partials', hint='<b>Predict first:</b> two map tasks each compute (min, max); the reducer merges them. What is the spread?',
             code='''parts = [(40, 780), (60, 880)]              # (min, max) from two map tasks
lo = min(p[0] for p in parts)
hi = max(p[1] for p in parts)
print("merged:", (lo, hi), "spread:", hi - lo)
'''),
        dict(label='3 · A UDTF', hint='One string in, many rows out. Malformed parts are skipped, bad quantities become None.',
             code='''def split_items(s):
    for part in s.split(","):
        kv = part.strip().split(":")
        if len(kv) != 2 or not kv[0]:
            continue
        try:
            qty = int(kv[1])
        except ValueError:
            qty = None
        yield kv[0].strip(), qty
print(list(split_items("dal:2, roti:4,paneer:x,,raita")))
'''),
        dict(label='4 · Why partials matter', hint='A wrong merge only shows when data is split. Compare merging (min, max) with averaging the partial spreads.',
             code='''parts = [(40, 780), (60, 880)]
right = max(p[1] for p in parts) - min(p[0] for p in parts)
wrong = sum(p[1] - p[0] for p in parts) / len(parts)
print("right:", right, " wrong (average of spreads):", wrong)
'''),
        dict(label='5 · Spot the error', hint='This UDF crashes on NULL. Fix it the way the Java version does.', expect='error',
             code='''def upper_city(raw):
    return raw.strip().upper()                  # bug: no NULL check
try:
    print(upper_city(None))
except AttributeError as e:
    raise AssertionError("handle None first: return None, like Hive UDFs return NULL") from e
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: function help, argument errors and macros',
    intro='<p>More statements to try after Step 4. <b>Outputs are real</b>, from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · Help for a permanent function', cmd='DESCRIBE FUNCTION EXTENDED tiffingo.spread;', file='Beeline',
             output=capf('l91_desc.txt'),
             note='Function type PERSISTENT and the JAR it is loaded from. The first line comes from the @Description annotation: always fill it in.'),
        dict(title='2 · Wrong arguments are caught at compile time', cmd='SELECT normalize_city(city, plan) FROM customers LIMIT 1;', file='Beeline',
             output=capf('l91_badarg.txt'),
             note='Our initialize() threw UDFArgumentException; Hive turned it into Error 10014 with our message, before any task started.'),
        dict(title='3 · A macro: SQL-only reuse, no Java', cmd='CREATE TEMPORARY MACRO gst(amount DECIMAL(10,2)) amount * 0.05;\nSELECT order_id, amount, gst(amount) AS gst FROM orders ORDER BY order_id LIMIT 3;', file='Beeline',
             output=capf('l91_macro.txt'),
             note='For a simple expression, a temporary macro is enough. Macros are session-only; for shared SQL logic use views (Lesson 9.2).'),
    ],
)

TRACE = dict(
    heading='A UDAF over two map tasks',
    intro='<p>Follow <code>spread(amount)</code> through partial aggregation: each map task keeps (min, max), the reducer merges.</p>',
    code='''task1 = [530, 500, 410]
task2 = [880, 40]
p1 = (min(task1), max(task1))          # terminatePartial on task 1
p2 = (min(task2), max(task2))          # terminatePartial on task 2
lo = min(p1[0], p2[0])                 # merge
hi = max(p1[1], p2[1])
print("spread:", hi - lo)              # terminate
''',
    notes={3: 'Partial :: Only two numbers leave each map task, not all its rows.', 5: 'Merge :: The reducer combines partials from every map task.', 7: 'Terminate :: The final value per group.'},
)

WORKED_INTRO = 'Three UDF decisions from real projects.'
EXAMPLES = [
    dict(level='b', tag='Analytics · choosing', title='UDF, UDAF or UDTF?',
         problem='<p>Pick the function kind for four requirements.</p>',
         inp='four requirements from the TiffinGo backlog',
         approach=['One value per row → UDF.', 'One value per group → UDAF.', 'Several rows per row → UDTF.'],
         code='''needs = {"mask phone numbers": "UDF", "weighted median delivery time per city": "UDAF",
         "split 'dal:2,roti:4' into rows": "UDTF", "clean city names": "UDF"}
for need, kind in needs.items():
    print(f"{kind:5} <- {need}")
''', notes={2: 'Built-in first :: Check whether mask_*, percentile or explode already cover the need.'},
         tryit='Hive 4 has built-in mask functions and percentile_approx; a UDF is only needed when the rule is specific to your business.'),
    dict(level='i', tag='Data engineering · testing', title='Test a UDF with known inputs',
         problem='<p>Write the expected-output table for normalize_city and compare it with what Hive returns.</p>',
         inp='the six inputs from Step 2',
         approach=['List inputs and expected outputs.', 'Run the same stack() query in Hive.', 'Diff the two.'],
         code='''expected = {"  bombay ": "Mumbai", "BANGALORE": "Bengaluru", "navi   mumbai": "Navi Mumbai", "Pune": "Pune", "": None}
hive_out = {"  bombay ": "Mumbai", "BANGALORE": "Bengaluru", "navi   mumbai": "Navi Mumbai", "Pune": "Pune", "": None}
bad = {k: (expected[k], hive_out.get(k)) for k in expected if expected[k] != hive_out.get(k)}
print("all good" if not bad else bad)
''', notes={3: 'Diff :: Any mismatch blocks the release.'},
         tryit='hive_out is the real result from Step 2. Keep this check in CI and run it after every JAR change.'),
    dict(level='a', tag='Platform · release', title='Plan a UDF release',
         problem='<p>Write the statements to move tiffingo.normalize_city from version 1.2 to 1.3 with a rollback path.</p>',
         inp='JARs on HDFS: /udf/tiffingo-udf-1.2.jar (live), /udf/tiffingo-udf-1.3.jar (new)',
         approach=['Upload the new JAR next to the old one.', 'Drop and recreate the function.', 'Keep the old JAR for rollback.'],
         code='''new = "hdfs:///udf/tiffingo-udf-1.3.jar"
cls = "in.myphatshala.hive.NormalizeCity"
print("DROP FUNCTION IF EXISTS tiffingo.normalize_city;")
print(f"CREATE FUNCTION tiffingo.normalize_city AS '{cls}' USING JAR '{new}';")
print("-- rollback: same two statements with ...-1.2.jar")
''', notes={4: 'Recreate :: New sessions load the new JAR; existing sessions may keep the old classes until they end.'},
         tryit='Our lab used file:/// paths because HiveServer2 runs Tez in local mode; on a cluster use HDFS or object storage so every node can read the JAR.'),
]

QUIZ = mix([
    dict(q='Beginner: Which kind of function turns one row into many rows?', options=['UDF', 'UDAF', 'UDTF', 'Macro'], answer=2,
         why='Like explode; used with LATERAL VIEW.'),
    dict(q='Beginner: How long does a TEMPORARY function exist?', options=['Forever', 'Until the end of the session', 'One query', 'Until HiveServer2 restarts'], answer=1,
         why='The next session got Error 10011: Invalid function.'),
    dict(q='Beginner: Which base class is recommended for a new scalar UDF?', options=['UDF', 'GenericUDF', 'GenericUDTF', 'AbstractGenericUDAFResolver'], answer=1,
         why='The old reflection-based UDF class is deprecated.'),
    dict(q='Intermediate: Where are permanent functions stored?', options=['In the JAR', 'In the metastore tables FUNCS and FUNC_RU', 'In hive-site.xml', 'In HDFS /tmp'], answer=1,
         why='Name, class and JAR URI, per database.'),
    dict(q='Intermediate: Which UDAF method runs on the reducer to combine partial results?', options=['iterate', 'merge', 'evaluate', 'forward'], answer=1,
         why='iterate runs on raw rows, terminatePartial emits partials, merge combines them, terminate returns the result.'),
    dict(q='Intermediate: In Hive 4.2.1, which pattern listed our functions?', options=["SHOW FUNCTIONS LIKE 'tiffingo*'", "SHOW FUNCTIONS LIKE 'tiffingo.%'", 'SHOW UDFS', 'LIST FUNCTIONS'], answer=1,
         why='SQL wildcards; the * pattern returned nothing.'),
    dict(q='Advanced: Why did our first UDTF fail with “Should not be called directly”?', options=['Wrong JAR', 'Hive called the older initialize(ObjectInspector[]), which we had not implemented', 'Missing @Description', 'NULL input'], answer=1,
         why='Implementing both initialize methods fixed it.'),
    dict(q='Advanced: How did our UDF run in a vectorised plan?', options=['Natively vectorised', 'Through VectorUDFAdaptor', 'It disabled vectorisation', 'In LLAP'], answer=1,
         why='About 3.2 s vs 2.8 s for built-ins on 5,000,000 rows.'),
])

REVISION = [
    '<b>UDF</b> 1→1 (<code>GenericUDF</code>: initialize, evaluate, getDisplayString) · <b>UDAF</b> N→1 (resolver + evaluator) · <b>UDTF</b> 1→N (<code>GenericUDTF</code>: initialize, process/forward, close).',
    'Build: <code>javac -cp "hive-exec.jar:hadoop-common.jar" …; jar cf udf.jar …</code>.',
    '<b>Temporary:</b> <code>ADD JAR …; CREATE TEMPORARY FUNCTION f AS \'cls\';</code> (one session).',
    '<b>Permanent:</b> <code>CREATE FUNCTION db.f AS \'cls\' USING JAR \'hdfs:///…jar\';</code> → metastore <code>FUNCS</code>/<code>FUNC_RU</code>.',
    'Check: <code>DESCRIBE FUNCTION EXTENDED f</code>, <code>SHOW FUNCTIONS LIKE \'db.%\'</code> (SQL wildcards in Hive 4).',
    'UDAF modes: PARTIAL1 (iterate→terminatePartial), PARTIAL2/FINAL (merge→terminate). Test against built-ins.',
    'Hive 4.2.1 UDTF: implement <code>initialize(ObjectInspector[])</code> too. Handle NULLs everywhere.',
    'UDFs run via <code>VectorUDFAdaptor</code>; built-ins were ~15% faster. Version JARs; macros for simple SQL reuse.',
]
FAQ = [
    ('Can I write Hive UDFs in Python?', 'Not as native UDFs: Hive loads JVM classes. Python logic runs through TRANSFORM (Lesson 9.3), which streams rows to a script, or in another engine such as Spark with Python UDFs. Any JVM language (Scala, Kotlin) works for native UDFs.'),
    ('Old UDF class or GenericUDF?', 'The old <code>org.apache.hadoop.hive.ql.exec.UDF</code> finds evaluate() by reflection and is deprecated. GenericUDF handles any type through ObjectInspectors, supports complex types and is faster. Use GenericUDF for new code.'),
    ('How do I mark a function as non-deterministic?', 'Annotate the class with <code>@UDFType(deterministic = false)</code> (like rand() or current time). The optimiser then does not cache or fold its result, and materialized-view rewriting avoids queries that use it.'),
    ('Can I write a vectorised UDF?', 'Yes, by implementing a VectorExpression and annotating the UDF with <code>@VectorizedExpressions</code>. It is more work and tied to Hive internals; most teams accept the adaptor unless a UDF dominates CPU time.'),
    ('Where should the JAR live?', 'Somewhere every HiveServer2 and task can read: HDFS, S3/ADLS/GCS, or a path in hive.aux.jars.path installed on every node. Our lab used a local path because Tez runs inside the HiveServer2 container.'),
]

PRACTICE_INTRO = 'Programs that reproduce UDF behaviour, with the HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Title case', stmt='Title-case a city name with extra spaces.', inp="'navi   mumbai'",
         code='''print(" ".join(w.capitalize() for w in "navi   mumbai".split()))
''', explain="normalize_city('navi   mumbai') returned 'Navi Mumbai' in Hive."),
    dict(level='easy', title='Spread', stmt='Compute max − min for a list of amounts.', inp='[530, 500, 410, 880, 40]',
         code='''a = [530, 500, 410, 880, 40]
print(max(a) - min(a))
''', explain='SELECT spread(amount) FROM … would return 840.0.'),
    dict(level='easy', title='Count UDTF rows', stmt='How many rows does split_items produce?', inp="'dal:2,roti:4,paneer:1'",
         code='''print(len("dal:2,roti:4,paneer:1".split(",")))
''', explain='Three rows; with LATERAL VIEW each is joined to its order.'),
    dict(level='medium', title='Old-name map', stmt='Map a list of old city names to current names.', inp='Bombay, Madras, Calcutta',
         code='''OLD = {"bombay": "Mumbai", "madras": "Chennai", "calcutta": "Kolkata"}
print([OLD.get(c.lower(), c) for c in ["Bombay", "Madras", "Calcutta"]])
''', explain='Exactly the lookup inside NormalizeCity.evaluate().'),
    dict(level='medium', title='Merge partials', stmt='Merge (min, max) partials from three map tasks.', inp='(40,780), (60,880), (100,500)',
         code='''parts = [(40, 780), (60, 880), (100, 500)]
print(min(p[0] for p in parts), max(p[1] for p in parts))
''', explain='The merge step of the Spread evaluator.'),
    dict(level='medium', title='Parse item quantities', stmt='Total quantity from an item string, skipping bad parts.', inp="'dal:2,roti:4,paneer:x'",
         code='''total = 0
for part in "dal:2,roti:4,paneer:x".split(","):
    k, _, v = part.partition(":")
    if v.isdigit():
        total += int(v)
print(total)
''', explain='In Hive: SELECT SUM(qty) FROM … LATERAL VIEW split_items(items) i AS item, qty;'),
    dict(level='business', title='UDF overhead', stmt='The UDF took 3.2 s vs 2.8 s for built-ins. Extra cost over 300 daily runs?', inp='lab timings',
         code='''print(round((3.2 - 2.8) * 300 / 60, 1), "minutes per day")
''', explain='Small here; on billions of rows the gap scales. Prefer built-ins when they are enough.'),
    dict(level='business', title='CASE copies vs one UDF', stmt='Six reports each carry a 40-line CASE. How many lines must change when a city is added?', inp='6 copies',
         code='''print("CASE copies:", 6, "edits · UDF:", 1, "edit + release")
''', explain='One tested function avoids six slightly different versions of the same rule.'),
]

SCN_INTRO = 'UDF questions test whether you know the three kinds, how they are registered and when not to write one.'
SCENARIOS = (
    scn('Any company · Hive', 'Fresher', '“What is a UDF in Hive?”',
        'Explain UDFs and how to use one.',
        'do you know the kinds and registration?',
        '<p>A user-defined function adds custom logic to HiveQL. UDFs return one value per row, UDAFs aggregate groups, UDTFs return several rows per row. You write them in Java (GenericUDF, GenericUDAFEvaluator, GenericUDTF), build a JAR, then ADD JAR and CREATE TEMPORARY FUNCTION for a session, or CREATE FUNCTION … USING JAR to store it in the metastore.</p>', 'Saying UDFs are written in SQL.') +
    scn('Data engineering', 'Mid-level', 'Function works in one session only',
        'A colleague’s UDF works in their Beeline session, but scheduled jobs fail with “Invalid function”.',
        'do you know temporary vs permanent functions?',
        '''<ol>
          <li>It was created as TEMPORARY: it exists only in that session.</li>
          <li>Put the JAR on HDFS or object storage, then CREATE FUNCTION db.f … USING JAR.</li>
          <li>Call it as db.f or from inside that database; check with DESCRIBE FUNCTION EXTENDED.</li>
        </ol>''', 'Copying ADD JAR into every script without a permanent function.') +
    scn('Analytics', 'Mid-level', 'Custom aggregate gives different results',
        'A custom UDAF returns correct results on small data but wrong ones on large tables.',
        'do you understand partial aggregation?',
        '''<ul>
          <li>On large data, map tasks produce partials that the reducer merges; small data may run in one task, hiding merge bugs.</li>
          <li>Check terminatePartial and merge: they must combine correctly (e.g. min/max, sum/count, not averages of averages).</li>
          <li>Test against a built-in equivalent on data split across several tasks.</li>
        </ul>''', 'Blaming Hive for non-determinism.') +
    scn('Platform', 'Senior', 'Governing UDFs',
        'Teams have registered 200 UDFs, some duplicated, some broken. Propose a policy.',
        'can you run UDFs like a product?',
        '''<ul>
          <li>One shared repository with tests, versioned JARs on HDFS, release by DROP/CREATE in a dedicated database (e.g. <code>udf</code>).</li>
          <li>Review: prefer built-ins and views; require @Description, NULL handling, deterministic flags.</li>
          <li>Inventory from the metastore (FUNCS/FUNC_RU) to find duplicates and dead JAR URIs.</li>
        </ul>''', 'Letting every team register functions anywhere.')
)
