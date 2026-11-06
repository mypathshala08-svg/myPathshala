import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from hivekit import tables
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return re.sub(r'; Query ID[^\n]*', '', open(CAP + n).read().rstrip())
BODY = body(HERE)

META = dict(
    module='09-extending-hive', lesson='03-transform-with-python', n='9.3',
    module_label='Module 9 · Extending Hive',
    title='TRANSFORM with Python scripts',
    desc='Stream Hive rows through Python with SELECT TRANSFORM … USING, tested on Hive 4.2.1: ADD FILE, the tab-separated stream and \\N for NULL, typed AS columns, mapper and reducer scripts with DISTRIBUTE BY / SORT BY, the Hive 4 setting that removed a subquery SORT BY and produced 63 wrong rows, CLUSTER BY pitfalls, script errors 20000/20001/20003 and where the traceback is, Windows line endings, and a 6× cost against plain SQL.',
    og_desc='Python inside Hive queries, with the traps shown: a Hive 4 default that silently broke a reducer script, and a 6× slowdown against SQL.',
    minutes=35, level='Intermediate → Advanced',
    lead='The last lesson of Module 9 runs <b>Python</b> inside Hive queries with <code>TRANSFORM</code>. We write a mapper and a reducer script for TiffinGo, then hit every trap in the lab: untyped outputs, a silently removed sort, vague script errors, Windows line endings and the cost of streaming. <b>All outputs are real</b>, from Hive 4.2.1; the scripts are in the course lab folder (<code>tools/authoring/src/hive/lab/scripts</code>).',
    chips=['Real Hive 4.2.1 outputs', 'Mapper and reducer scripts', 'A silent Hive 4 trap', 'Runs in your browser (Python)'],
)

MAIN = '''# What Hive does around your script, simulated in Python
rows = [(100001, "2026-10-05 20:10:00", "530.00"), (100003, None, "410.00")]

def to_line(row):                       # Hive -> script: tabs, \\N for NULL
    return "\\t".join("\\\\N" if v is None else str(v) for v in row)

def slot_script(line):                  # the user's script (simplified slot.py)
    oid, ts, amt = line.split("\\t")
    slot = "\\\\N" if ts == "\\\\N" else ("dinner" if 19 <= int(ts[11:13]) < 23 else "other")
    return f"{oid}\\t{slot}\\t{float(amt) * 0.05:.2f}"

for r in rows:
    line = to_line(r)
    out = slot_script(line)
    print(repr(line), "->", out.split("\\t"))   # Hive splits the output back into columns
'''
RUN = dict(
    heading='Run the code: the stream around a script',
    intro='<p>These programs simulate the text stream between Hive and a TRANSFORM script, and the reducer logic. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    return "\\t".join("\\\\N" if v is None else str(v) for v in row)', 'Exactly what cat -A showed in the lab: tab-separated values, NULL as \\N, one line per row.'),
        ('    print(repr(line), "->", out.split("\\t"))   # Hive splits the output back into columns', 'Every output column is text until you give types in AS (…).'),
    ],
    tasks=[
        dict(label='1 · The stream', hint='Press <b>Run</b>. The second row’s NULL timestamp travels as <code>\\N</code> and must be handled by the script.', code=None),
        dict(label='2 · Predict first: unsorted reducer input', hint='<b>Predict first:</b> rows of customer 15 arrive interleaved with others. How many output rows does a “flush on key change” reducer produce?',
             code='''stream = [15, 7, 15, 7, 1492, 7, 1492]          # keys as they arrived
out, current = 0, None
for k in stream:
    if k != current:
        out += 1                              # a new group starts
        current = k
print("groups emitted:", out, "(correct: 3)")
'''),
        dict(label='3 · Sorted input', hint='Sort by key and time first, as SORT BY customer_id, order_ts does.',
             code='''rows = [(15, 3), (7, 1), (15, 1), (7, 2), (15, 2)]       # (customer, hour)
rows.sort()
from itertools import groupby
for k, g in groupby(rows, key=lambda r: r[0]):
    hours = [h for _, h in g]
    gaps = [b - a for a, b in zip(hours, hours[1:])]
    print(k, len(hours), sum(gaps) / len(gaps))
'''),
        dict(label='4 · Strings sort as text', hint='Untyped AS columns are strings. See why “9.00” sorts after “26.50”.',
             code='''gst = ["26.50", "9.00", "20.50"]
print("as text   :", sorted(gst))
print("as numbers:", sorted(gst, key=float))
'''),
        dict(label='5 · Spot the error', hint='This script crashes on NULL amounts. Fix it like slot.py does.', expect='error',
             code='''line = "100009\\t\\\\N"
oid, amt = line.split("\\t")
try:
    print(oid, float(amt) * 0.05)            # bug: \\N is not a number
except ValueError as e:
    raise AssertionError("check for \\\\N before converting, and print \\\\N back") from e
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: see the raw stream, and a CLUSTER BY trap',
    intro='<p>Two more experiments. <b>Outputs are real</b>, from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · Look at exactly what a script receives', cmd="SELECT TRANSFORM (order_id, CAST(NULL AS STRING), city, 'a b')\n       USING 'cat -A' AS (raw_line)\nFROM orders WHERE order_id <= 100002;", file='Beeline',
             output=capf('l93_cat.txt'),
             note='<code>cat -A</code> makes invisible characters visible: <code>^I</code> is a tab, <code>\\N</code> is NULL, <code>$</code> is the end of the line. Spaces inside values are kept. The best first step when a script misbehaves.'),
        dict(title='2 · CLUSTER BY groups, but does not sort by time', cmd="ADD FILE /data/scripts/gaps.py;\nFROM (SELECT customer_id, order_ts FROM orders WHERE customer_id IN (7, 15, 1492)\n      CLUSTER BY customer_id) t\nSELECT TRANSFORM (customer_id, order_ts) USING 'python3 gaps.py'\n       AS (customer_id INT, orders INT, avg_gap_hours DOUBLE);", file='Beeline',
             output=capf('l93_cluster.txt'),
             note='The counts are right (each customer arrived as one group), but the gaps are wrong, even negative: CLUSTER BY customer_id sorts only by the key, not by order_ts. A reducer script needs DISTRIBUTE BY key SORT BY key, time (with the subquery sort kept).'),
    ],
)

TRACE = dict(
    heading='The reducer script, line by line',
    intro='<p>Follow <code>gaps.py</code> over sorted input for two customers (hours since midnight, simplified).</p>',
    code='''lines = [("7", 1), ("7", 25), ("7", 50), ("15", 3), ("15", 30)]
current, times, out = None, [], []
for cid, h in lines:
    if cid != current and current is not None:
        out.append((current, len(times), (times[-1] - times[0]) / (len(times) - 1)))
        times = []
    current = cid
    times.append(h)
out.append((current, len(times), (times[-1] - times[0]) / (len(times) - 1)))
print(out)
''',
    notes={4: 'Key change :: Customer 15 starts, so customer 7 is complete and can be printed.', 8: 'Collect :: Times of the current customer.', 9: 'Last group :: The final customer is flushed after the input ends.'},
)

WORKED_INTRO = 'Three TRANSFORM decisions from real projects.'
EXAMPLES = [
    dict(level='b', tag='Analytics · choosing', title='SQL, UDF or TRANSFORM?',
         problem='<p>Pick the tool for four tasks.</p>',
         inp='four tasks from TiffinGo teams',
         approach=['If SQL can do it, use SQL.', 'Reusable JVM logic → Java UDF.', 'Python-only libraries → TRANSFORM (or Spark).'],
         code='''tasks = {"meal slot from order time": "SQL CASE",
         "city name cleaning used everywhere": "Java UDF (9.1)",
         "score with a scikit-learn model": "TRANSFORM or Spark",
         "parse a vendor log with a Python library": "TRANSFORM"}
for k, v in tasks.items():
    print(f"{v:22} <- {k}")
''', notes={2: 'Speed :: SQL was 6× faster than the script for the meal slot in Step 8.'},
         tryit='Our slot.py is a teaching example: in production the SQL CASE is the right answer.'),
    dict(level='i', tag='Data engineering · testing', title='Test a script without Hive',
         problem='<p>Feed a script the exact lines Hive would send and compare with expected output.</p>',
         inp='two lines, one with a NULL timestamp',
         approach=['Build lines with tabs and \\N.', 'Run the script function.', 'Compare.'],
         code='''def slot(line):
    oid, ts, amt = line.split("\\t")
    s = "\\\\N" if ts == "\\\\N" else ("dinner" if 19 <= int(ts[11:13]) < 23 else "other")
    return f"{oid}\\t{s}\\t{float(amt) * 0.05:.2f}"
tests = {"1\\t2026-10-05 20:10:00\\t530.00": "1\\tdinner\\t26.50", "2\\t\\\\N\\t100.00": "2\\t\\\\N\\t5.00"}
print(all(slot(i) == o for i, o in tests.items()))
''', notes={5: 'Fixtures :: The first case is a real lab row: order 100001, dinner, 26.50.'},
         tryit='In a shell: printf "1\\t2026-10-05 20:10:00\\t530.00\\n" | python3 slot.py'),
    dict(level='a', tag='Platform · reliability', title='Make a reducer script safe',
         problem='<p>List the settings and checks a production job with a reducer script needs.</p>',
         inp='Hive 4 cluster, Python 3 on all nodes',
         approach=['Keep the subquery sort.', 'Type outputs.', 'Validate against SQL on a sample.'],
         code='''checklist = [
  "SET hive.remove.orderby.in.subquery=false;",
  "DISTRIBUTE BY key SORT BY key, time   (not CLUSTER BY key)",
  "AS (col TYPE, ...) for every output column",
  "EXPLAIN shows SHUFFLE, not PARTITION_ONLY_SHUFFLE",
  "sample cross-check against a SQL calculation",
]
for c in checklist:
    print("-", c)
''', notes={2: 'Sort :: Without it, Hive 4 dropped the order in our lab.'},
         tryit='Every item on this list caught a real problem in this lesson’s lab.'),
]

QUIZ = mix([
    dict(q='Beginner: How does Hive send a row to a TRANSFORM script?', options=['As JSON', 'As one tab-separated line on stdin', 'As a Python object', 'As a file per row'], answer=1,
         why='cat -A showed ^I (tab) between values and $ at the end.'),
    dict(q='Beginner: How does NULL appear in the stream?', options=['As an empty string', 'As \\N', 'As None', 'As NULL'], answer=1,
         why='The script must handle \\N itself.'),
    dict(q='Beginner: What is the type of AS (a, b) output columns?', options=['Inferred', 'STRING', 'INT', 'Same as input'], answer=1,
         why='Declare AS (a INT, b DECIMAL(10,2)) to get typed columns.'),
    dict(q='Intermediate: Which statement ships a script to every task?', options=['LOAD FILE', 'ADD FILE', 'CREATE FUNCTION', 'COPY'], answer=1,
         why='ADD FILE /data/scripts/slot.py; then USING \'python3 slot.py\'.'),
    dict(q='Intermediate: Why did the reducer script return 63 rows for 3 customers?', options=['Duplicate data', 'Hive 4 removed the subquery SORT BY, so rows arrived unsorted', 'Python bug', 'Too many reducers'], answer=1,
         why='hive.remove.orderby.in.subquery=true; the plan showed PARTITION_ONLY_SHUFFLE.'),
    dict(q='Intermediate: Where was the Python traceback?', options=['In Beeline', 'In the task’s stderr log', 'Nowhere', 'In the metastore'], answer=1,
         why='Beeline only showed Error 20001.'),
    dict(q='Advanced: Why did CLUSTER BY customer_id still give wrong gaps?', options=['It does not group', 'It sorts only by customer_id, not by time', 'It is ignored', 'It drops rows'], answer=1,
         why='Use DISTRIBUTE BY customer_id SORT BY customer_id, order_ts.'),
    dict(q='Advanced: How did TRANSFORM compare with SQL on 5,000,000 rows?', options=['Faster', 'About 9.4 s vs 1.5 s', 'Equal', 'It failed'], answer=1,
         why='Text serialisation and a process pipe for every row.'),
])

REVISION = [
    '<code>ADD FILE script.py; SELECT TRANSFORM (cols) USING \'python3 script.py\' AS (out_cols) FROM t;</code>',
    'Stream format: tab-separated lines, NULL = <code>\\N</code>; outputs are STRING unless typed in AS.',
    'Mapper scripts need nothing special; reducer scripts need <code>DISTRIBUTE BY k SORT BY k, ts</code> in a subquery.',
    'Hive 4: <code>hive.remove.orderby.in.subquery=true</code> removed our SORT BY → set false; check for SHUFFLE in EXPLAIN.',
    'CLUSTER BY k sorts only by k. Plans with scripts are “not optimized by CBO”.',
    'Errors: 20000 (cannot start), 20001 (crashed while streaming), 20003 (failed on close); traceback in the task’s stderr.',
    'Windows line endings break shebang scripts (<code>env: python3\\r</code>); use dos2unix or call python3 explicitly.',
    'Cost: ≈ 6× slower than SQL in the lab. Disabled under SQL-standard authorization.',
]
FAQ = [
    ('Where does the script run?', 'Inside each task (map or reduce) on the worker nodes, in the task’s working directory, using the interpreter installed there. Every node needs the same Python version and packages, or you ship an environment with ADD ARCHIVE.'),
    ('Can a script return more or fewer rows than it receives?', 'Yes. It may print zero, one or many lines per input line; Hive just reads whatever comes out. A reducer script usually prints one line per group.'),
    ('How do I debug a script?', 'Run it locally with the lines Hive would send (use USING \'cat -A\' to see them), print debug messages to stderr (never stdout, which becomes data), and read the task log for tracebacks.'),
    ('Is TRANSFORM allowed on secured clusters?', 'Often not. With SQL-standard based authorization, Hive rejects queries with a transform clause (“Query with transform clause is disallowed in current configuration”), because scripts can run arbitrary programs. Ranger-secured platforms usually restrict it too.'),
    ('What is the modern alternative?', 'Spark SQL with Python UDFs, especially vectorised pandas UDFs, reads the same metastore tables and runs Python far more efficiently. Many teams keep TRANSFORM only for legacy jobs.'),
]

PRACTICE_INTRO = 'Programs that work with the TRANSFORM stream, with the HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Build a stream line', stmt='Write the line Hive sends for a row with a NULL.', inp='(100001, NULL, Mumbai)',
         code='''row = (100001, None, "Mumbai")
print("\\t".join("\\\\N" if v is None else str(v) for v in row))
''', explain='Matches cat -A: 100001^I\\N^IMumbai$.'),
    dict(level='easy', title='Meal slot', stmt='Return the slot for an hour, like slot.py.', inp='hour 20',
         code='''h = 20
print("breakfast" if 6 <= h < 11 else "lunch" if 11 <= h < 16 else "snacks" if 16 <= h < 19 else "dinner" if 19 <= h < 23 else "late-night")
''', explain='Order 100001 at 20:xx was labelled dinner.'),
    dict(level='easy', title='Slowdown', stmt='How many times slower was TRANSFORM than SQL?', inp='9.405 s and 1.605 s',
         code='''print(round(9.405 / 1.605, 1))
''', explain='About 5.9×; the second runs gave 9.349 vs 1.429 s (6.5×).'),
    dict(level='medium', title='Average gap', stmt='Average hours between consecutive orders, from sorted times.', inp='hours 0, 30, 45',
         code='''t = [0, 30, 45]
gaps = [b - a for a, b in zip(t, t[1:])]
print(sum(gaps) / len(gaps), (t[-1] - t[0]) / (len(t) - 1))
''', explain='Both formulas give 22.5: the SQL cross-check used (last − first) / (n − 1).'),
    dict(level='medium', title='Parse typed output', stmt='Convert script output lines to typed tuples like AS (id INT, slot STRING, gst DECIMAL).', inp='two lines',
         code='''from decimal import Decimal
lines = ["100001\\tdinner\\t26.50", "100004\\tbreakfast\\t9.00"]
print([(int(a), b, Decimal(c)) for a, b, c in (l.split("\\t") for l in lines)])
''', explain='What Hive does when AS declares types; unconvertible values become NULL.'),
    dict(level='medium', title='Detect CRLF', stmt='Check a script file’s bytes for Windows line endings.', inp='script text',
         code='''src = "#!/usr/bin/env python3\\r\\nimport sys\\r\\n"
print("CRLF found: convert with dos2unix" if "\\r\\n" in src else "ok")
''', explain='The CRLF version of slot.py failed with env: python3\\r.'),
    dict(level='business', title='Cost per month', stmt='A nightly job uses TRANSFORM (9.4 s per 5M rows) on 2 billion rows. Estimate time vs SQL at 1.5 s per 5M.', inp='linear scaling (illustrative)',
         code='''scale = 2_000_000_000 / 5_000_000
print("TRANSFORM:", round(9.4 * scale / 60), "min  SQL:", round(1.5 * scale / 60), "min (single-task equivalents)")
''', explain='63 vs 10 minutes of task time per run: worth rewriting in SQL if possible.'),
    dict(level='business', title='Migration plan', stmt='Order three legacy streaming jobs for migration.', inp='jobs with daily runtime and type',
         code='''jobs = [("sessions.py", 90, "reducer"), ("clean.py", 40, "mapper"), ("score.py", 20, "model")]
for name, mins, kind in sorted(jobs, key=lambda j: -j[1]):
    target = "window functions" if kind == "reducer" else "SQL / UDF" if kind == "mapper" else "Spark pandas UDF"
    print(f"{name:12} {mins:>3} min -> {target}")
''', explain='Start with the longest job; reducer logic like gaps.py often becomes LAG() over (PARTITION BY … ORDER BY …).'),
]

SCN_INTRO = 'TRANSFORM questions check streaming basics and whether you know when not to use it.'
SCENARIOS = (
    scn('Any company · Hive', 'Fresher', '“Can Hive run Python?”',
        'Explain how to use a Python script in a Hive query.',
        'do you know TRANSFORM and the stream format?',
        '<p>Yes, through TRANSFORM. ADD FILE ships the script; SELECT TRANSFORM (cols) USING \'python3 script.py\' AS (outputs) sends each row as a tab-separated line to the script’s stdin and reads its stdout lines back as rows. NULL arrives as \\N and outputs are strings unless typed. Native UDFs, by contrast, must be Java.</p>', 'Saying Hive supports Python UDFs natively.') +
    scn('Data engineering', 'Mid-level', 'Script results wrong after an upgrade',
        'A sessionisation script gives different numbers after moving to Hive 4, without errors.',
        'can you find an ordering problem?',
        '''<ol>
          <li>EXPLAIN: look for PARTITION_ONLY_SHUFFLE instead of SHUFFLE before the Transform Operator.</li>
          <li>Check hive.remove.orderby.in.subquery (true in Hive 4); set it to false for this job.</li>
          <li>Use DISTRIBUTE BY key SORT BY key, time and cross-check a sample with SQL.</li>
        </ol>''', 'Rewriting the script before checking the input order.') +
    scn('Analytics', 'Mid-level', 'Error 20001',
        'A query with a TRANSFORM script fails with “Error 20001: … may have crashed with an error”.',
        'do you know where script errors go?',
        '''<ul>
          <li>Read the task log (stderr) for the Python traceback.</li>
          <li>Reproduce locally with the same input lines (USING 'cat -A' shows them).</li>
          <li>Handle \\N and malformed values in the script; log bad rows to stderr instead of crashing.</li>
        </ul>''', 'Re-running the query unchanged.') +
    scn('Platform', 'Senior', 'Retire TRANSFORM',
        'A platform has 40 TRANSFORM jobs and is enabling SQL-standard authorization. Plan the change.',
        'can you plan a migration?',
        '''<ul>
          <li>Inventory jobs by runtime and type (mapper, reducer, model).</li>
          <li>Mappers → SQL or Java UDFs; reducers → window functions; models → Spark Python/pandas UDFs.</li>
          <li>Validate each rewrite against the old output on samples before enabling authorization.</li>
        </ul>''', 'Turning authorization on first and fixing failures later.')
)
