import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
SRC = os.path.join(HERE, '..', '..', 'lab', 'udf') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
def java(n, start=None, end=None):
    lines = open(SRC + n).read().rstrip().split('\n')
    return '\n'.join(lines[start:end])
def nolicense(s):
    return re.sub(r'; Query ID.*', '', s)

def opbox(x, y, label, sub='', tone='card', w=128, h=26):
    o = box(x, y, w, h, tone) + t(x + w / 2, y + (11 if sub else 16), label, 7.2, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 21, sub, 6.4, 'ink2', mono=True)
    return o

# ---------------------------------------------------------------- story
sc = (box(10, 12, 190, 128, 'card') + t(105, 30, 'Partner feed: city column', 8.8, bold=True) +
      ''.join(t(22, 52 + k * 16, s, 7.4, c, anchor='start', mono=True) for k, (s, c) in enumerate([("'  bombay '", 'red'), ("'BANGALORE'", 'red'), ("'navi   mumbai'", 'red'), ("'Pune'", 'green'), ("''", 'red')])) +
      arrow(206, 76, 246, 76, 'acc', 2.2) + box(252, 46, 110, 60, 'violet') + t(307, 70, 'normalize_city()', 8, bold=True, mono=True) + t(307, 88, 'Java UDF', 8.4, bold=True) +
      arrow(368, 76, 404, 76, 'acc', 2.2) + box(410, 12, 220, 128, 'green') + t(520, 30, 'One rule, every query', 8.8, 'green', bold=True) +
      ''.join(t(426, 52 + k * 16, s, 7.4, 'ink', anchor='start', mono=True) for k, s in enumerate(['Mumbai', 'Bengaluru', 'Navi Mumbai', 'Pune', 'NULL'])))
scene_svg = scene('A partner feed sends city names in many spellings. A Java user-defined function, normalize_city, turns them into one clean value that every query can use.', sc,
                  'When SQL cannot express a rule cleanly, <tspan font-weight="700" class="s-acc">write it once in Java</tspan> and call it like a built-in.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Bombay, BANGALORE and navi   mumbai are all wrong”</h2>
  <div class="story">
    <p class="narration">TiffinGo has signed a new restaurant partner. Its feed spells cities any way it likes: old names, capitals, extra spaces. Kabir already has a 40-line CASE expression copied into six reports, and every copy is slightly different.</p>

{scene_svg}

K> Sir, can Hive call my own code instead of this CASE monster?
A> Yes. Hive lets you add <b>user-defined functions</b> written in Java. A <b>UDF</b> maps one row to one value, a <b>UDAF</b> aggregates many rows into one value like SUM, and a <b>UDTF</b> turns one row into many rows like explode. You compile them into a JAR and register them with <code>CREATE FUNCTION</code>.
R> Do we need a Hadoop cluster to build them?
A> Only a JDK and two JAR files from Hive. Today we write all three kinds for TiffinGo, register them temporarily and permanently, look at where Hive stores them, hit two real errors, and measure what a UDF costs compared with built-in functions. All outputs are real, from Hive 4.2.1; the Java sources are in the course lab folder.
  </div>
</section>
'''

lv = '''
LEVELS> User-defined functions at three levels
L1> Teaching Hive a new word
      <ul>
        <li>Hive has hundreds of built-in functions: <code>upper</code>, <code>sum</code>, <code>explode</code>. A UDF is one you add yourself.</li>
        <li>You write the rule once in Java, package it as a JAR, and tell Hive its name.</li>
        <li>After that, <code>SELECT normalize_city(city) FROM …</code> works like any built-in function.</li>
      </ul>
L2> Three kinds and how they are registered
      <ul>
        <li><b>UDF</b> (one row → one value): extend <code>GenericUDF</code>; implement <code>initialize</code> (check arguments, declare the return type), <code>evaluate</code>, <code>getDisplayString</code>.</li>
        <li><b>UDAF</b> (many rows → one value): a resolver plus a <code>GenericUDAFEvaluator</code> with <code>iterate</code>, <code>terminatePartial</code>, <code>merge</code>, <code>terminate</code>.</li>
        <li><b>UDTF</b> (one row → many rows): extend <code>GenericUDTF</code>; <code>process</code> calls <code>forward</code> for each output row.</li>
        <li><code>CREATE TEMPORARY FUNCTION</code> lasts for one session; <code>CREATE FUNCTION … USING JAR</code> is stored in the metastore for everyone.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>The temporary function was gone in the next session (<code>Error 10011: Invalid function</code>); permanent functions appeared as rows in the metastore’s <code>FUNCS</code> and <code>FUNC_RU</code> tables, qualified by database.</li>
        <li>Hive 4.2.1 called the older <code>initialize(ObjectInspector[])</code> of our UDTF: “Should not be called directly” until we implemented it.</li>
        <li><code>SHOW FUNCTIONS LIKE</code> takes SQL wildcards (<code>%</code>) in Hive 4; the <code>*</code> pattern from older tutorials returned nothing. The UDF ran through <code>VectorUDFAdaptor</code>: about 3.2 s vs 2.8 s for built-ins.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>User-defined functions in Hive</h2>
''' + def_block(
    'A <b>user-defined function</b> extends HiveQL with logic implemented in Java (or another JVM language) and loaded from a JAR. Hive distinguishes three kinds by how many rows go in and come out: a <b>UDF</b> (scalar, one row to one value; modern ones extend <code>GenericUDF</code>), a <b>UDAF</b> (aggregate, many rows to one value per group; implemented as a resolver and a <code>GenericUDAFEvaluator</code> that supports partial aggregation), and a <b>UDTF</b> (table-generating, one row to zero or more rows; extends <code>GenericUDTF</code>). Functions are registered per session with <code>CREATE TEMPORARY FUNCTION</code> or permanently in the metastore with <code>CREATE FUNCTION db.name AS \'class\' USING JAR \'uri\'</code>.',
    'A UDF is your own function that Hive can call. You write it in Java, put it in a JAR file, and register it with a name. Then you use it in queries like any built-in function.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('UDF', 'Scalar function: one input row → one value.'),
    ('UDAF', 'Aggregate function: a group of rows → one value.'),
    ('UDTF', 'Table function: one row → many rows.'),
    ('ObjectInspector', 'Hive’s description of a value’s type and how to read it.'),
    ('DeferredObject', 'A lazily evaluated argument passed to evaluate().'),
    ('Partial aggregation', 'Map tasks aggregate first; reducers merge the partials.'),
    ('Temporary function', 'Exists for one session only.'),
    ('Permanent function', 'Stored in the metastore with its JAR location.'),
]) + '''

  <h3>Which base class?</h3>
''' + table(['Need', 'Kind', 'Base class', 'Key methods', 'Built-in example'], [
    ['Clean or compute one value', 'UDF', '<code>GenericUDF</code>', 'initialize, evaluate', '<code>upper</code>, <code>concat</code>'],
    ['Aggregate a group', 'UDAF', '<code>AbstractGenericUDAFResolver</code> + <code>GenericUDAFEvaluator</code>', 'iterate, terminatePartial, merge, terminate', '<code>sum</code>, <code>percentile</code>'],
    ['Produce rows from a value', 'UDTF', '<code>GenericUDTF</code>', 'initialize, process (forward), close', '<code>explode</code>, <code>stack</code>'],
    ['Old simple API', 'UDF', '<code>UDF</code> with evaluate()', 'reflection-based', 'deprecated; avoid in new code'],
], minw=760) + lv + '''
EXAM> “Difference between UDF, UDAF and UDTF?” UDF: one row in, one value out (GenericUDF). UDAF: many rows in, one value out, with partial aggregation (iterate, terminatePartial, merge, terminate). UDTF: one row in, many rows out (GenericUDTF, forward), used with LATERAL VIEW. Register with ADD JAR + CREATE TEMPORARY FUNCTION, or CREATE FUNCTION … USING JAR for a permanent one.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Registering functions</h2>
''' + table(['Statement', 'Lifetime', 'Where the JAR must be', 'Visible as'], [
    ['<code>ADD JAR path; CREATE TEMPORARY FUNCTION f AS \'cls\';</code>', 'This session', 'Readable by HiveServer2 (local path or HDFS)', '<code>f</code>'],
    ['<code>CREATE FUNCTION db.f AS \'cls\' USING JAR \'uri\';</code>', 'Until DROP FUNCTION', 'A URI every node can read (HDFS, S3, or a shared path)', '<code>db.f</code>, or <code>f</code> inside <code>db</code>'],
    ['<code>hive.aux.jars.path</code> / <code>auxlib</code> + RELOAD', 'Server-wide', 'On every HiveServer2', 'After CREATE FUNCTION'],
    ['<code>DROP [TEMPORARY] FUNCTION [IF EXISTS] f;</code>', '—', '—', 'Removed'],
], minw=740) + '''
WARN> In production, put UDF JARs on HDFS or object storage with a <b>version in the file name</b> (<code>tiffingo-udf-1.2.jar</code>) and register the new version under the same function name. Overwriting a JAR in place can leave sessions running different code.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Three functions for TiffinGo, from Java to SQL</h2>
  <p>All outputs are real, from Hive 4.2.1. Java was compiled with JDK 21 (<code>--release 17</code>) against <code>hive-exec-4.2.1.jar</code> and <code>hadoop-common-3.4.1.jar</code>.</p>
''' + stepper([
    ('Step 1 · A GenericUDF: normalize_city',
     code('java', 'NormalizeCity.java', java('NormalizeCity.java', 12)),
     '<code>initialize</code> runs once, at compile time: it checks the arguments and returns the <b>ObjectInspector</b> of the result (a Java String). <code>evaluate</code> runs for every row: NULL in, NULL out; trim and squeeze spaces; map old names; otherwise title-case. <code>@Description</code> provides the help text for <code>DESCRIBE FUNCTION</code>.'),
    ('Step 2 · Compile, add the JAR, use it',
     code('sql', 'Beeline', "-- shell: javac --release 17 -cp \"lib/*\" -d classes src/in/myphatshala/hive/*.java\n--        jar cf tiffingo-udf.jar -C classes .\nADD JAR /data/udf/tiffingo-udf.jar;\nCREATE TEMPORARY FUNCTION normalize_city AS 'in.myphatshala.hive.NormalizeCity';\nSELECT raw, normalize_city(raw) AS city\nFROM (SELECT stack(6, '  bombay ', 'BANGALORE', 'navi   mumbai', 'Pune', '', CAST(NULL AS STRING)) AS raw) t;\nDESCRIBE FUNCTION EXTENDED normalize_city;", capf('l91_temp.txt')),
     'Six messy inputs, six clean outputs; empty and NULL both give NULL. <code>DESCRIBE FUNCTION EXTENDED</code> shows our <code>@Description</code> text, the class and <b>Function type: TEMPORARY</b>.'),
    ('Step 3 · Temporary means this session only',
     code('sql', 'Beeline', "-- a new Beeline session\nSELECT normalize_city('bombay');", nolicense(capf('l91_gone.txt'))),
     'The next session does not know the function: <b>Error 10011</b>. Temporary functions are fine for testing and ad-hoc scripts; shared reports need a permanent function.'),
    ('Step 4 · Permanent functions, stored in the metastore',
     code('sql', 'Beeline', "USE tiffingo;\nCREATE FUNCTION normalize_city AS 'in.myphatshala.hive.NormalizeCity' USING JAR 'file:///data/udf/tiffingo-udf.jar';\nCREATE FUNCTION split_items   AS 'in.myphatshala.hive.SplitItems'    USING JAR 'file:///data/udf/tiffingo-udf.jar';\nCREATE FUNCTION spread        AS 'in.myphatshala.hive.Spread'        USING JAR 'file:///data/udf/tiffingo-udf.jar';\nSHOW FUNCTIONS LIKE 'tiffingo.%';\nSHOW FUNCTIONS LIKE 'tiffingo*';     -- the pattern older tutorials use\n\n-- in the metastore database (PostgreSQL):\nSELECT f.\"FUNC_NAME\", f.\"CLASS_NAME\", f.\"FUNC_TYPE\", r.\"RESOURCE_URI\"\nFROM \"FUNCS\" f JOIN \"FUNC_RU\" r ON f.\"FUNC_ID\" = r.\"FUNC_ID\";", capf('l91_show.txt') + '\n' + capf('l91_star.txt') + '\n\n' + capf('l91_funcs_db.txt')),
     'Permanent functions belong to a <b>database</b> (<code>tiffingo.spread</code>) and are stored in the metastore tables <code>FUNCS</code> (name, class) and <code>FUNC_RU</code> (the JAR URI). Any session, on any HiveServer2 using this metastore, can call them. In Hive 4.2.1 <code>SHOW FUNCTIONS LIKE</code> used SQL wildcards: <code>\'tiffingo.%\'</code> listed all three, the old <code>\'tiffingo*\'</code> listed nothing.'),
    ('Step 5 · A UDAF: spread = max − min',
     code('java', 'Spread.java (evaluator)', java('Spread.java', 27, 78)),
     'Aggregates run in two phases. On the map side (<code>PARTIAL1</code>) <code>iterate</code> sees raw values and <code>terminatePartial</code> emits a small struct (min, max). On the reducer (<code>FINAL</code>) <code>merge</code> combines the structs and <code>terminate</code> returns max − min. That is why <code>init</code> returns a struct inspector in partial modes and a double in final modes.'),
    ('Step 6 · Check the UDAF against built-ins',
     code('sql', 'Beeline', "SELECT city, spread(amount) AS spread_udaf, MAX(amount) - MIN(amount) AS check_builtin, COUNT(*) AS n\nFROM orders GROUP BY city ORDER BY city;", capf('l91_spread.txt')),
     'Identical for every city, across 50,000 rows and both phases of aggregation. Always test a UDAF against an equivalent built-in or a hand count: merge bugs only appear when data is split over several tasks. (Our UDAF returns a DOUBLE, hence 800.0 vs the DECIMAL 800.00.)'),
    ('Step 7 · A UDTF: split_items, and a real Hive 4 surprise',
     code('java', 'SplitItems.java', java('SplitItems.java', 22, 53)),
     'Our first version implemented only <code>initialize(StructObjectInspector)</code>, as most tutorials show. Hive 4.2.1 failed at compile time with <code>' + capf('l91_udtf_err.txt').split('FAILED: ')[1] + '</code>: some code paths call the older <code>initialize(ObjectInspector[])</code>. Implementing both (the new one delegating to the old one) fixed it. <code>process</code> calls <code>forward</code> once per output row; malformed entries are skipped and a bad quantity becomes NULL.'),
    ('Step 8 · Use the UDTF, then see what a UDF costs',
     code('sql', 'Beeline', "SELECT split_items('dal:2, roti:4,paneer:x,,raita') AS (item, qty);\nSELECT o.order_no, i.item, i.qty\nFROM (SELECT stack(2, 101, 'dal:2,roti:4', 102, 'biryani:1') AS (order_no, items)) o\nLATERAL VIEW split_items(o.items) i AS item, qty;\n\nEXPLAIN VECTORIZATION EXPRESSION SELECT normalize_city(city), COUNT(*) FROM orders_big GROUP BY normalize_city(city);\n-- then time the UDF against initcap(trim(city)) on 5,000,000 rows", capf('l91_udtf.txt') + '\n\n' + '\n'.join(l.strip('| ').rstrip(' |').strip() for l in capf('l91_vec.txt').split('\n') if 'Adaptor' in l)[:400] + '\n\n' + capf('l91_speed.txt')),
     'One string became three rows (“raita” had no quantity and was skipped, “paneer:x” got NULL). With <b>LATERAL VIEW</b> each order joins with its own item rows. The UDF ran through <code>VectorUDFAdaptor</code> (Lesson 8.4): about <b>3.2 s</b> vs <b>2.8 s</b> for built-ins on 5,000,000 rows, plus about 1 s for loading the JAR on first use (run 1). Prefer built-ins when they can do the job.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([("> SELECT normalize_city('  bombay ');", W), ('Mumbai', G), ("> SELECT normalize_city('BANGALORE');", W), ('Bengaluru', G), ('Function type:TEMPORARY', Y)], size=7.6),
    term([('(new session)', W), ("> SELECT normalize_city('bombay');", W), ('[Error 10011]: Invalid function', RD), ('  normalize_city', RD)], size=7.6),
    term([('> SHOW FUNCTIONS LIKE \'tiffingo.%\';', W), ('tiffingo.normalize_city', G), ('tiffingo.split_items', G), ('tiffingo.spread', G), ('FUNCS / FUNC_RU rows in metastore', Y)], size=7.4),
    term([('city        spread_udaf  check_builtin', W), ('Bengaluru   800.0        800.00', G), ('Hyderabad   840.0        840.00', G), ('Mumbai      840.0        840.00', G)], size=7.6),
    term([("split_items('dal:2, roti:4,paneer:x,,raita')", W), ('dal      2', G), ('roti     4', G), ('paneer   NULL', Y), ('VectorUDFAdaptor(normalize_city(city))', Y)], size=7.2),
]
def kinds(hi):
    o = ''
    for k, (a, b, tone) in enumerate([('UDF', '1 row → 1 value', 'green'), ('UDAF', 'N rows → 1 value', 'blue'), ('UDTF', '1 row → N rows', 'violet')]):
        o += opbox(18 + k * 112, 52, a, b, 'acc' if k == hi else tone, 104, 30)
    return o
B1 = [
    t(180, 22, 'initialize once, evaluate per row', 9.4, bold=True) + kinds(0) + opbox(40, 100, 'initialize()', 'compile time', 'card', 120) + opbox(200, 100, 'evaluate()', 'each row', 'green', 120) + cap('Type checks happen before any data is read.', '', 'blue', y=150, h=34),
    t(180, 22, 'Temporary: lives in one session', 9.4, bold=True) + opbox(40, 56, 'session 1', 'ADD JAR + CREATE', 'green', 120) + opbox(200, 56, 'session 2', 'unknown', 'red', 120) + cap('Use CREATE FUNCTION … USING JAR to share.', '', 'amber', y=150, h=34),
    t(180, 22, 'Permanent: metastore rows', 9.4, bold=True) + opbox(30, 56, 'CREATE FUNCTION', '', 'card', 110) + arrow(142, 69, 166, 69, 'ink3') + opbox(168, 56, 'FUNCS · FUNC_RU', 'name · class · JAR', 'green', 150) + cap('Every session loads the JAR on first use.', '', 'green', y=150, h=34),
    t(180, 22, 'UDAF: partial then final', 9.4, bold=True) + kinds(1) + opbox(30, 100, 'map: iterate', '→ (min, max)', 'blue', 130) + arrow(162, 113, 190, 113, 'ink3') + opbox(192, 100, 'reduce: merge', '→ max − min', 'blue', 130) + cap('Small partial structs travel, not rows.', '', 'blue', y=150, h=34),
    t(180, 22, 'UDTF: forward() per output row', 9.4, bold=True) + kinds(2) + opbox(30, 100, "'dal:2,roti:4'", '', 'card', 120) + arrow(152, 113, 180, 113, 'ink3') + opbox(182, 96, 'dal 2', '', 'violet', 70) + opbox(256, 96, 'roti 4', '', 'violet', 70) + cap('Used with LATERAL VIEW.', '', 'violet', y=150, h=34),
]
see_caps = ['The UDF cleaned messy city names.',
            'A new session did not know the temporary function.',
            'Permanent functions were listed and stored in the metastore.',
            'The UDAF matched MAX − MIN for every city.',
            'The UDTF produced rows; the UDF ran through the vector adaptor.']
behind_caps = ['initialize checks types once; evaluate runs per row.',
               'Temporary functions are registered in the session only.',
               'CREATE FUNCTION writes the name, class and JAR URI to the metastore.',
               'Map tasks build partial results; reducers merge them.',
               'A UDTF emits zero or more rows per input row.']
two = anim_two('User-defined functions', 'From Java to SQL', 'Real lab outputs', 'How Hive calls your code', see, B1, see_caps, behind_caps)

# ---- scenario 1: deploying a new version
v1 = (t(180, 22, 'A bug fix for normalize_city', 9.4, bold=True) + t(180, 56, "'Gurugram' was missing from the map", 8.4, 'ink2') + cap('Fix the code, rebuild the JAR.', '', 'blue', y=150, h=34))
v2 = (t(180, 22, 'Do not overwrite the JAR in place', 9.4, bold=True) + t(180, 56, 'sessions may cache the old classes', 8.4, 'red') + cap('Different sessions, different results.', '', 'amber', y=150, h=34))
v3 = (t(180, 22, 'Upload a versioned JAR', 9.4, bold=True) + t(180, 56, 'hdfs:///udf/tiffingo-udf-1.3.jar', 8.4, 'ink', mono=True) + cap('Old version stays for rollback.', '', 'green', y=150, h=34))
v4 = (t(180, 22, 'Re-register', 9.4, bold=True) + t(180, 52, 'DROP FUNCTION tiffingo.normalize_city;', 7.8, 'ink', mono=True) + t(180, 70, "CREATE FUNCTION … USING JAR '…-1.3.jar';", 7.8, 'ink', mono=True) + cap('New sessions pick up 1.3.', '', 'green', y=150, h=34))
v5 = (t(180, 22, 'Test like code', 9.4, 'acc', bold=True) + t(180, 56, 'unit tests + a SQL check against known inputs', 8.2, 'ink2') + cap('Our stack() test is a ready-made check.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Releasing a new UDF version safely',
              'How teams roll out UDF fixes. (Typical practice.)',
              'UDF deployment', 'Build a versioned JAR, re-register the function and test it with known inputs; never overwrite JARs in place', [v1, v2, v3, v4, v5],
              ['A bug fix is needed.',
               'Overwriting the JAR in place is risky.',
               'Upload a new, versioned JAR.',
               'Drop and recreate the function.',
               'Test with known inputs.'],
              hid='scenario-version')

# ---- scenario 2: UDF vs built-in
b1 = (t(180, 22, 'Do we even need a UDF?', 9.4, bold=True) + t(180, 56, 'cleaning, parsing, hashing, masking', 8.4, 'ink2') + cap('Check the built-ins first.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Built-ins cover a lot', 9.4, bold=True) + t(180, 56, 'regexp_replace · initcap · get_json_object · mask', 7.8, 'ink', mono=True) + cap('Many have native vector versions.', '', 'green', y=150, h=34))
b3 = (t(180, 22, 'Measured', 9.4, bold=True) + t(180, 56, 'UDF ≈ 3.2 s · built-ins ≈ 2.8 s (5M rows)', 8, 'ink', mono=True) + cap('Plus ~1 s JAR load on first use.', '', 'amber', y=150, h=34))
b4 = (t(180, 22, 'UDF when the rule is real logic', 9.4, bold=True) + t(180, 56, 'lookup maps, checksums, business rules', 8.2, 'ink2') + cap('One tested implementation beats copies of CASE.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Or a view / macro', 9.4, 'acc', bold=True) + t(180, 56, 'CREATE TEMPORARY MACRO, views (Lesson 9.2)', 8, 'ink2') + cap('SQL-only reuse without Java.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'UDF or built-in?',
              'Choosing the cheapest tool that is correct. Timings are from our lab.',
              'UDF vs built-in', 'Built-in functions are faster and need no deployment; UDFs are for real logic that SQL expresses badly', [b1, b2, b3, b4, b5],
              ['Start with the built-in function list.',
               'Built-ins cover most cleaning tasks.',
               'Our UDF cost about 15% more time.',
               'Use UDFs for real business logic.',
               'Views and macros give SQL-only reuse.'],
              hid='scenario-builtin')

# ---- scenario 3: UDF in other engines
e1 = (t(180, 22, 'Spark and Trino read the same tables', 9.4, bold=True) + t(180, 56, 'can they call tiffingo.normalize_city?', 8.2, 'ink2') + cap('One metastore, many engines (Module 11).', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Spark SQL: yes, Hive UDF API', 9.4, bold=True) + t(180, 56, 'CREATE FUNCTION … USING JAR with Hive support', 8, 'ink', mono=True) + cap('Spark supports Hive UDF/UDAF/UDTF classes.', '', 'green', y=150, h=34))
e3 = (t(180, 22, 'Trino / Impala: different APIs', 9.4, bold=True) + t(180, 56, 'rewrite as their plugin functions', 8.2, 'ink2') + cap('Logic must be ported.', '', 'amber', y=150, h=34))
e4 = (t(180, 22, 'Keep the logic portable', 9.4, bold=True) + t(180, 56, 'core rule in a plain Java class, thin wrappers', 8.2, 'ink2') + cap('Test the core once.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Or materialise the result', 9.4, 'acc', bold=True) + t(180, 56, 'store city_clean in the table at load time', 8.2, 'ink2') + cap('Every engine just reads a column.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'One function, several engines',
              'What happens to Hive UDFs in a multi-engine platform. (Typical architecture.)',
              'Portable UDFs', 'Spark can run Hive UDF classes; other engines need ports; storing cleaned values at load time avoids the problem', [e1, e2, e3, e4, e5],
              ['Other engines share the tables.',
               'Spark SQL can load Hive UDFs.',
               'Trino and Impala need their own functions.',
               'Keep the core logic in plain Java.',
               'Or store the cleaned value once.'],
              hid='scenario-engines')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>How Hive runs your Java</h2>
  <p>Left: real outputs. Right: what Hive does with your classes.</p>
''' + two + '''
  <p>Three live scenarios follow: releasing a new version, UDF or built-in, and UDFs across engines.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>UDFs at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'clean', 11, 'green', bold=True) + t(60, 58, 'standardise', 7.4, 'ink2'),
    '1. Data standardisation',
    'City, phone, and address normalisation rules live in one tested UDF instead of copies of CASE expressions in every job.',
    ['Raw feed', '*UDF', 'Clean column']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'mask', 11, 'blue', bold=True) + t(60, 58, 'privacy', 7.4, 'ink2'),
    '2. Masking and tokenisation',
    'Security teams provide UDFs that tokenise or mask personal data with a company key before analysts see it.',
    ['PII', '*mask UDF', 'Safe data']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'parse', 11, 'violet', bold=True) + t(60, 58, 'custom formats', 7.4, 'ink2'),
    '3. Parsing custom formats',
    'UDTFs split proprietary strings (item lists, event payloads) into rows that SQL can aggregate.',
    ['Packed string', '*UDTF', 'Rows']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'UDAF', 12, 'acc', bold=True, mono=True) + t(60, 58, 'custom metrics', 7.4, 'ink2'),
    '4. Custom aggregates',
    'Approximate distinct counts with sketches, weighted medians or domain scores are added as UDAFs.',
    ['Groups', '*UDAF', 'Metric']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'geo', 12, 'acc', bold=True) + t(60, 58, 'libraries', 7.4, 'ink2'),
    '5. Reusing Java libraries',
    'Geospatial, ML-scoring or encryption libraries are wrapped as UDFs so SQL users can call them directly.',
    ['Java library', '*wrapper', 'SQL function']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> built-in functions (<a href="../../04-complex-data/01-string-date-and-conditional-functions/">4.1</a>), explode and LATERAL VIEW (<a href="../../04-complex-data/02-explode-and-lateral-view/">4.2</a>), vectorisation (<a href="../../08-optimisation/04-vectorisation-tez-and-llap/">8.4</a>). Basic Java helps.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
