import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l123_new.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)

REL = [('4.0', 'May 2025', 'ANSI on, VARIANT,\nConnect, pipe SQL', 'blue'), ('4.1', 'Dec 2025', 'SQL scripting GA,\nDeclarative Pipelines', 'green'),
       ('4.2', '2026', 'geospatial types,\nArrow UDFs default', 'violet'), ('4.3', 'Oct 2026', 'ASOF JOIN, JSON_TABLE,\nstateful RTM', 'acc')]
def timeline(x, y, hi=None):
    o = fill(x, y + 30, 340, 2, '#8A94A0', rx=0)
    for k, (v, d, f, tone) in enumerate(REL):
        xx = x + 10 + k * 86
        o += box(xx, y, 70, 22, 'acc' if hi == v else tone, rx=4) + t(xx + 35, y + 15, 'Spark ' + v, 7.6, 'ink', bold=True)
        o += t(xx + 35, y + 46, d, 6.6, 'ink2', mono=True)
        for j, line in enumerate(f.split('\n')):
            o += t(xx + 35, y + 62 + j * 11, line, 6.4, 'ink2')
    return o

# ---------------------------------------------------------------- story
sc_ = (timeline(14, 30) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Tried on PySpark 4.3.0', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('1/0 → DIVIDE_BY_ZERO', 'red'), ('try_divide(1,0) → NULL', 'green'),
           ('SQL script WHILE → 1000', 'green'), ('Python UDTF: 3 rows', 'green'),
           ('UTF8_LCASE: Mumbai=MUMBAI', 'blue'), ('ASOF JOIN: off by default', 'amber')])))
scene_svg = scene('Spark 4 is a new major line with four releases so far. We tried features from each on PySpark 4.3.0: ANSI SQL by default, safe try_ functions, pipe syntax, session variables, collations, SQL scripting, recursive CTEs, Python UDTFs, Python data sources, geospatial types and Spark 4.3 SQL additions.', sc_,
                  'Spark 4 is <tspan font-weight="700" class="s-acc">stricter</tspan> by default and far more SQL- and Python-friendly.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“The upgrade broke our job, and we found 10 new features”</h2>
  <div class="story">
    <p class="narration">When TiffinGo moved from Spark 3.5 to Spark 4, one nightly job failed on the first run with <code>CAST_INVALID_INPUT</code>: a column of phone numbers contained “N/A”. In Spark 3 that row had silently become NULL for years. The same week, engineers discovered they could now write loops in SQL and their own data sources in pure Python.</p>

{scene_svg}

K> Sir, why would Spark break working code?
A> Spark 4 turned on <b>ANSI SQL mode</b> by default. Invalid casts and division by zero now raise errors instead of producing NULL, which hid bad data. The fix is explicit: <code>try_cast</code>, <code>try_divide</code>, or cleaning the data.
R> And the new features?
A> Spark 4.0 to 4.3 added a lot: VARIANT, Spark Connect as a first-class client, pipe syntax, SQL scripting, Python UDTFs and data sources, geospatial types, real-time streaming. Today we run a tour of them on PySpark 4.3.0. All outputs are real.
  </div>
</section>
'''

lv = '''
LEVELS> Spark 4 at three levels
L1> A new car model
      <ul>
        <li>Stricter safety system: it refuses to start if a seatbelt is broken (ANSI errors) instead of driving anyway.</li>
        <li>New dashboard and controls (SQL scripting, pipe syntax), a remote-control key (Spark Connect), and a faster engine options list each year.</li>
      </ul>
L2> What to know
      <ul>
        <li>4.0: ANSI default, Java 17+, Scala 2.13, VARIANT, collations, pipe syntax, session variables, SQL UDFs, Python UDTF and Data Source APIs, Spark Connect improvements.</li>
        <li>4.1: SQL scripting GA, recursive CTEs, Spark Declarative Pipelines, Real-Time Mode for streaming.</li>
        <li>4.2: GEOMETRY/GEOGRAPHY types, CDC APIs, Arrow-optimised Python UDFs by default. 4.3: ASOF JOIN, JSON_TABLE, UNNEST, stateful Real-Time Mode, quarterly releases.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li><code>1/0</code> and <code>CAST('12a' AS INT)</code> failed; <code>try_divide</code>/<code>try_cast</code> returned NULL; ANSI off brought back silent NULLs.</li>
        <li>A SQL <code>WHILE</code> loop computed 1000; a recursive CTE summed 1..5 = 15.</li>
        <li><code>ASOF JOIN</code> worked only after enabling its flag.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Spark 4: what changed</h2>
''' + def_block(
    'Apache Spark 4.0 (2025) started a new major version that removed old platforms (Java 8/11, Scala 2.12, Mesos) and changed defaults, most visibly enabling <b>ANSI SQL mode</b> (<code>spark.sql.ansi.enabled=true</code>), so invalid operations such as overflow, division by zero and malformed casts raise errors rather than returning NULL. It added the <b>VARIANT</b> type for semi-structured data, <b>string collations</b>, SQL <b>pipe syntax</b>, <b>session variables</b>, SQL UDFs, Python <b>user-defined table functions</b> and a Python <b>Data Source API</b>, and made <b>Spark Connect</b> a central client architecture. Spark 4.1 made <b>SQL scripting</b> generally available, added recursive CTEs, <b>Spark Declarative Pipelines</b> and Real-Time Mode for Structured Streaming; 4.2 added geospatial types and change-data-capture APIs; 4.3 (October 2026, the first quarterly feature release) added ASOF joins, JSON_TABLE, UNNEST and stateful Real-Time Mode.',
    'Spark 4 is stricter by default (bad data raises errors instead of becoming NULL) and adds many features: semi-structured data, case-insensitive text comparison, SQL loops and variables, new ways to write Python functions and data sources, and a client-server mode. Each release since adds more SQL and streaming features.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('ANSI mode', 'Errors instead of silent NULLs.'),
    ('try_* functions', 'Return NULL instead of failing.'),
    ('Pipe syntax', 'FROM t |> WHERE … |> AGGREGATE …'),
    ('Session variable', 'DECLARE VARIABLE in SQL.'),
    ('Collation', 'Rules for comparing text (e.g. case).'),
    ('SQL scripting', 'BEGIN … WHILE … END in SQL.'),
    ('UDTF', 'Function returning many rows.'),
    ('Python data source', 'Custom reader written in Python.'),
]) + '''

  <h3>Spark 4 releases at a glance</h3>
''' + table(['Release', 'Highlights', 'Tried in this lesson'], [
    ['4.0 (2025)', 'ANSI default, Java 17+, VARIANT, collations, pipe syntax, session variables, Python UDTF & data sources, Connect', 'ANSI, try_*, pipe, variables, collation, UDTF, data source'],
    ['4.1 (Dec 2025)', 'SQL scripting GA, recursive CTE, Declarative Pipelines, Real-Time Mode', 'WHILE script, recursive CTE'],
    ['4.2 (2026)', 'GEOMETRY/GEOGRAPHY + ST_ functions, CDC, Arrow Python UDFs default, new UI', 'GEOMETRY from WKB'],
    ['4.3 (Oct 2026)', 'ASOF JOIN, JSON_TABLE, UNNEST, new functions, stateful Real-Time Mode, Python 3.10 dropped', 'ASOF, UNNEST, jaro_winkler, base32'],
], minw=660) + '''
  <p class="muted">Sources: Apache Spark release notes for <a href="https://spark.apache.org/releases/spark-release-4-0-0.html">4.0.0</a>, <a href="https://spark.apache.org/releases/spark-release-4-2-0.html">4.2.0</a>, <a href="https://spark.apache.org/releases/spark-release-4-3-0.html">4.3.0</a>, and Databricks’ <a href="https://www.databricks.com/blog/introducing-apache-sparkr-41">Spark 4.1 announcement</a> (checked 5 Nov 2026).</p>
''' + lv + '''
EXAM> “What changed in Spark 4?” Biggest behaviour change: ANSI SQL mode on by default, so bad casts, overflow and division by zero fail instead of returning NULL (use try_cast/try_divide). Platform: Java 17+, Scala 2.13. Features: VARIANT, collations, pipe syntax, session variables and SQL UDFs, Python UDTFs and data sources, Spark Connect; 4.1 added SQL scripting and Declarative Pipelines, 4.2 geospatial types and CDC, 4.3 ASOF joins and stateful real-time streaming.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Upgrading from Spark 3.5</h2>
''' + table(['Check', 'Why', 'Action'], [
    ['Java version', 'Spark 4 needs Java 17+ (21 supported)', 'Upgrade JDK on nodes/images'],
    ['ANSI errors', 'Bad casts, overflow, /0 now fail', 'Run tests; use try_* or clean data; ANSI off only as a temporary bridge'],
    ['Scala 2.13 libraries', 'Scala 2.12 jars do not load', 'Use _2.13 connectors'],
    ['Python & libraries', 'Older Python/NumPy/pandas dropped over 4.x', 'Pin supported versions'],
    ['RDD / SparkContext code', 'Not available on Spark Connect', 'Move to DataFrame APIs (11.3)'],
    ['Table-format connectors', 'Delta/Iceberg must match the Spark version', 'Check compatibility (11.5)'],
], minw=620) + '''
WARN> Do not “fix” an ANSI upgrade by globally setting <code>spark.sql.ansi.enabled=false</code>. It brings back silent NULLs (our lab: <code>1/0</code> and <code>CAST('12a')</code> both became NULL) and hides the bad data that the error just found. Handle the specific expressions with <code>try_cast</code>/<code>try_divide</code> and route invalid rows to a quarantine table. Also note new opt-in features such as <code>ASOF JOIN</code> are disabled by default and may not exist on your platform yet (Lesson 12.1).
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>A tour of Spark 4 on 4.3.0</h2>
  <p>All outputs are real: PySpark 4.3.0, <code>local[2]</code>. Each statement ran through <code>spark.sql</code> (or the Python APIs); errors show the error class.</p>
''' + stepper([
    ('Step 1 · ANSI mode by default',
     code('sql', 'l123_new.py', "SELECT 1/0;\nSELECT CAST('12a' AS INT);\nSELECT try_cast('12a' AS INT);\nSELECT try_divide(1, 0);\nSET spark.sql.ansi.enabled = false;  SELECT 1/0, CAST('12a' AS INT);", sec('Spark 4.3.0', '== 4.0 SQL')),
     'The two classic silent failures of Spark 3 now stop the query with <b>DIVIDE_BY_ZERO</b> and <b>CAST_INVALID_INPUT</b>. When NULL is really what you want, say so with <code>try_cast</code> and <code>try_divide</code>. With ANSI turned off, both quietly returned NULL: the behaviour that hid the “N/A” phone numbers for years.'),
    ('Step 2 · Pipe syntax, variables, collations',
     code('sql', 'l123_new.py', "FROM o |> WHERE amount > 100 |> AGGREGATE sum(amount) AS total GROUP BY city |> ORDER BY city;\nDECLARE VARIABLE min_amt INT DEFAULT 250;\nSELECT city, amount FROM o WHERE amount >= min_amt;\nSELECT city COLLATE UTF8_LCASE AS c, sum(amount) FROM o GROUP BY 1;", sec('== 4.0 SQL', '== 4.1')),
     'Pipe syntax reads top to bottom like a DataFrame chain (Lesson 7.1). A session variable parameterises SQL without string formatting. With the default binary collation, “Mumbai” and “MUMBAI” are different cities; with <code>UTF8_LCASE</code> they group together: <b>500</b>.'),
    ('Step 3 · SQL scripting and recursive CTEs (4.1)',
     code('sql', 'l123_new.py', "BEGIN\n  DECLARE total INT DEFAULT 0;\n  DECLARE i INT DEFAULT 1;\n  WHILE i <= 4 DO SET total = total + i * 100; SET i = i + 1; END WHILE;\n  SELECT total;\nEND;\nWITH RECURSIVE r(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM r WHERE n < 5) SELECT sum(n) FROM r;", sec('== 4.1', '== 4.0 Python')),
     'Procedural logic, previously only possible in Python or Scala around Spark, now runs in SQL: variables, a <code>WHILE</code> loop, and a final result (100+200+300+400 = <b>1000</b>). Recursive CTEs walk hierarchies such as category trees or referral chains (1+2+3+4+5 = 15).'),
    ('Step 4 · Python UDTFs and Python data sources',
     code('python', 'l123_new.py', '@udtf(returnType="item string, qty int")\nclass SplitItems:\n    def eval(self, order: str):\n        for part in order.split(","):\n            name, qty = part.split(":"); yield name.strip(), int(qty)\n\nclass Menu(DataSource):\n    @classmethod\n    def name(cls): return "menu"\n    def schema(self): return "dish string, price int"\n    def reader(self, schema): return MenuReader()\nspark.dataSource.register(Menu); spark.read.format("menu").load()', sec('== 4.0 Python', '== 4.2')),
     'A UDTF turns one input value into many rows: one order string became three item rows. A Python data source lets you add <code>spark.read.format("menu")</code> for any API or file type, in pure Python, with no Java connector. Both used to require Scala or awkward workarounds.'),
    ('Step 5 · Geospatial (4.2) and new SQL (4.3)',
     code('sql', 'l123_new.py', "SHOW FUNCTIONS LIKE 'st_*';\nSELECT typeof(st_geomfromwkb(X'0101…')), st_srid(st_geomfromwkb(X'0101…'));\nSELECT jaro_winkler_similarity('Biryani House', 'Biriyani House');\nSELECT * FROM UNNEST(array(10, 20, 30)) AS t(x);\nSET spark.sql.join.asofJoin.enabled = true;\nSELECT o.t, s.surge FROM orders_t o ASOF JOIN surge_t s MATCH_CONDITION (o.t >= s.t) ON o.city = s.city;", sec('== 4.2')),
     'Spark now has a native <b>GEOMETRY</b> type; our 4.3 build exposed a first set of <code>st_</code> functions working from WKB. <code>jaro_winkler_similarity</code> finds near-duplicate restaurant names (0.947). <b>ASOF JOIN</b> matches each order with the latest surge price at or before its time (10 → 1.0, 25 → 1.5), but only after enabling its flag; by default it fails with <code>UNSUPPORTED_FEATURE.ASOF_JOIN</code>.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('SELECT 1/0 -> DIVIDE_BY_ZERO', RD), ("CAST('12a') -> CAST_INVALID_INPUT", RD), ('try_cast / try_divide -> NULL', G), ('ANSI off -> silent NULLs', Y)], size=7.0),
    term([('pipe: MUMBAI 200, Mumbai 300, Pune 450', W), ('UTF8_LCASE: Mumbai 500, Pune 450', G)], size=7.0),
    term([('SQL script WHILE -> 1000', G), ('recursive CTE -> 15', G)], size=7.6),
    term([("UDTF: dosa 2, idli 3, vada 1", G), ("data source: Masala Dosa 120", G), ('ASOF JOIN: 10->1.0, 25->1.5', G), ('default: UNSUPPORTED_FEATURE', Y)], size=7.0),
]
B1 = [
    t(180, 14, 'Strict by default', 9.4, bold=True) + opbox(20, 46, "'12a' → INT", 'Spark 3: NULL', 'amber', 150, 34) + opbox(190, 46, "'12a' → INT", 'Spark 4: error', 'red', 150, 34) + cap('Bad data is visible now.', '', 'red', y=144, h=30),
    t(180, 14, 'Collation changes equality', 9.4, bold=True) + opbox(20, 46, 'binary', 'Mumbai ≠ MUMBAI', 'card', 150, 34) + opbox(190, 46, 'UTF8_LCASE', 'Mumbai = MUMBAI', 'green', 150, 34) + cap('Choose per column or query.', '', 'blue', y=144, h=30),
    t(180, 14, 'Spark 4 timeline', 9.4, bold=True) + timeline(14, 34) + cap('Quarterly releases from 4.3.', '', 'blue', y=144, h=30),
    t(180, 14, 'Python extends Spark', 9.4, bold=True) + flow([('UDTF', '1 → many rows', 'violet'), ('DataSource', 'custom reader', 'green'), ('no Java', 'pure Python', 'blue')], y=50, w=96, gap=16) + cap('Less Scala needed.', '', 'green', y=144, h=30),
]
see_caps = ['ANSI mode.', 'SQL ergonomics.', 'SQL scripting.', 'Python APIs and 4.3 SQL.']
behind_caps = ['Errors instead of NULLs.', 'Collations.', 'Release timeline.', 'Extending Spark in Python.']
two = anim_two('What’s new in Spark 4', 'A tour on 4.3.0', 'Real lab outputs', 'What changed', see, B1, see_caps, behind_caps)

e1 = (t(180, 22, 'Upgrade to Spark 4', 9.4, bold=True) + t(180, 56, 'job fails: CAST_INVALID_INPUT', 8.4, 'ink2') + cap('phone = “N/A”.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Tempting: ANSI off', 9.4, bold=True) + t(180, 56, 'silent NULLs return', 8.4, 'ink2') + cap('Hides the problem.', '', 'red', y=150, h=34))
e3 = (t(180, 22, 'try_cast where NULL is OK', 9.4, bold=True) + t(180, 56, 'explicit intent', 8.4, 'ink2') + cap('Readable.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Quarantine bad rows', 9.4, bold=True) + t(180, 56, 'try_cast IS NULL AND raw IS NOT NULL', 8.0, 'ink', mono=True) + cap('Report to source team.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Data quality improved', 9.4, 'acc', bold=True) + t(180, 56, 'errors found, not hidden', 8.4, 'ink2') + cap('Upgrade as an audit.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'The upgrade that found bad data',
              'Handling ANSI mode in a Spark 4 migration. (Typical; errors from our lab.)',
              'ANSI migration', 'Use try_ functions and quarantine tables instead of disabling ANSI mode', [e1, e2, e3, e4, e5],
              ['Fails.', 'ANSI off?', 'try_cast.', 'Quarantine.', 'Better data.'],
              hid='scenario-ansi')
b1 = (t(180, 22, 'Partner API, no connector', 9.4, bold=True) + t(180, 56, 'restaurant menus as JSON', 8.4, 'ink2') + cap('Used to need Scala.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Python DataSource', 9.4, bold=True) + t(180, 56, 'schema() + reader().read()', 8.4, 'ink', mono=True) + cap('Pure Python.', '', 'green', y=150, h=34))
b3 = (t(180, 22, 'spark.read.format("menu")', 9.4, bold=True) + t(180, 56, 'like any built-in source', 8.4, 'ink2') + cap('Lab: 2 dishes.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Partitions for parallel reads', 9.4, bold=True) + t(180, 56, 'one partition per page/region', 8.4, 'ink2') + cap('Scales out.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Share as a package', 9.4, 'acc', bold=True) + t(180, 56, 'register in every job', 8.4, 'ink2') + cap('Reusable connector.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'A connector in an afternoon',
              'Python Data Source API. (Typical; reader from our lab.)',
              'Python data source', 'Write custom Spark readers in Python with the Data Source API', [b1, b2, b3, b4, b5],
              ['API.', 'DataSource.', 'Read.', 'Partitions.', 'Share.'],
              hid='scenario-datasource')
u1 = (t(180, 22, 'Order × surge price at that time', 9.4, bold=True) + t(180, 56, 'latest price before each order', 8.4, 'ink2') + cap('Classic as-of problem.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Before: window + join tricks', 9.4, bold=True) + t(180, 56, 'complex and slow', 8.4, 'ink2') + cap('Hard to read.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'Spark 4.3: ASOF JOIN', 9.4, bold=True) + t(180, 56, 'MATCH_CONDITION (o.t >= s.t)', 8.2, 'ink', mono=True) + cap('10 → 1.0, 25 → 1.5 (lab).', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Flag required, for now', 9.4, bold=True) + t(180, 56, 'spark.sql.join.asofJoin.enabled', 8.2, 'ink', mono=True) + cap('Off by default.', '', 'amber', y=150, h=34))
u5 = (t(180, 22, 'Check your platform', 9.4, 'acc', bold=True) + t(180, 56, 'most runtimes are on 4.0–4.2', 8.4, 'ink2') + cap('Lesson 12.1.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Prices as of the order time',
              'New SQL in Spark 4.3. (Typical; output from our lab.)',
              'ASOF JOIN', 'Spark 4.3 adds ASOF JOIN for time-aligned joins, behind a flag', [u1, u2, u3, u4, u5],
              ['Problem.', 'Before.', 'ASOF.', 'Flag.', 'Platform.'],
              hid='scenario-asof')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>A tour on 4.3.0</h2>
  <p>Left: real outputs. Right: what changed.</p>
''' + two + '''
  <p>Three live scenarios follow: an ANSI upgrade, a Python connector, and ASOF joins.</p>
''' + s1 + s2 + s3 + '''
  <p><b>Congratulations:</b> this is the last lesson of the Apache Spark and PySpark course. You have gone from RDDs to DataFrames, SQL, tuning, streaming, ML, production and the wider industry, with real outputs at every step.</p>
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Spark 4 features at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'ANSI', 12, 'blue', bold=True) + t(60, 58, 'quality', 7.4, 'ink2'),
    '1. Safer pipelines',
    'ANSI errors stop bad data early; try_ functions mark intended NULLs.',
    ['Raw data', '*ANSI + try_cast', 'Clean + quarantine']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'SQL', 12, 'green', bold=True) + t(60, 58, 'scripts', 7.4, 'ink2'),
    '2. SQL-first teams',
    'Analytics engineers write loops, variables and pipelines in SQL.',
    ['SQL script', '*Spark 4.1+', 'Tables']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'JSON', 12, 'violet', bold=True) + t(60, 58, 'VARIANT', 7.4, 'ink2'),
    '3. Semi-structured events',
    'App events land as VARIANT and are queried without fixed schemas (Lesson 6.5).',
    ['Events', '*VARIANT', 'Queries']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'geo', 12, 'acc', bold=True) + t(60, 58, 'delivery', 7.4, 'ink2'),
    '4. Location analytics',
    'Native geometry types support delivery zones and distance analysis.',
    ['GPS', '*GEOMETRY', 'Zones']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'RTM', 12, 'acc', bold=True) + t(60, 58, 'streaming', 7.4, 'ink2'),
    '5. Low-latency streams',
    'Real-Time Mode brings sub-second Structured Streaming for supported queries.',
    ['Kafka', '*Real-Time Mode', 'Alerts']) + '''
  <p class="muted">Examples are simplified. Feature availability depends on your Spark version and platform.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> Spark SQL in <a href="../../07-spark-sql/01-spark-sql-and-views/">7.1</a>, VARIANT in <a href="../../06-transformations/05-complex-data-and-variant/">6.5</a>, Spark Connect in <a href="../../11-spark-in-production/03-spark-connect/">11.3</a>, platforms in <a href="../01-spark-platforms/">12.1</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
