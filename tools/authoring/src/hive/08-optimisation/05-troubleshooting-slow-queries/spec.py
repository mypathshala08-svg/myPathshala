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
    module='08-optimisation', lesson='05-troubleshooting-slow-queries', n='8.5',
    module_label='Module 8 · Query optimisation',
    title='Troubleshooting slow and failing queries',
    desc='A method for troubleshooting Hive 4 queries with real Hive 4.2.1 outputs: SHOW PROCESSLIST and KILL QUERY, reading a Tez task failure (4 attempts, the last Caused by), strict checks for Cartesian products, partition filters and ORDER BY without LIMIT, dynamic partition limits (Error 20004), query timeouts, 300 small files vs one file, CONCATENATE refused on external tables, silent NULLs from bad casts, and the Tez counters worth reading.',
    og_desc='Kill a runaway query, read a Tez failure from the bottom, and find wrong numbers that raise no error. Troubleshooting Hive 4.2.1 with real outputs.',
    minutes=40, level='Intermediate → Advanced',
    lead='The last lesson of Module 8 turns the module into a <b>method</b>: find the problem query, read the error properly, fix the cause. We produce eight real problems in the lab (a runaway join, a failing task, three strict-check rejections, a partition limit, a timeout, 300 small files and silent NULLs) and solve each one. <b>All outputs are real</b>, from Hive 4.2.1.',
    chips=['Eight real problems', 'Read errors from the bottom', 'Counters that matter', 'Runs in your browser (Python)'],
)

MAIN = '''# Read a Hive/Tez error the way an on-call engineer does: last "Caused by" first
error = """FAILED: Execution Error, return code 2 from org.apache.hadoop.hive.ql.exec.tez.TezTask. Vertex failed, vertexName=Map 1
TaskAttempt 0 failed
Caused by: java.lang.RuntimeException: org.apache.hadoop.hive.ql.metadata.HiveException: Hive Runtime Error while processing row
Caused by: org.apache.hadoop.hive.ql.metadata.HiveException: Hive Runtime Error while processing row
Caused by: org.apache.hadoop.hive.ql.metadata.HiveException: ASSERT_TRUE(): assertion failed.
DAG did not succeed due to VERTEX_FAILURE. failedVertices:1 killedVertices:1"""

lines = error.split("\\n")
causes = [l for l in lines if l.startswith("Caused by")]
kind = "runtime (return code 2)" if "return code 2" in lines[0] else "compile time"
print("kind      :", kind)
print("vertex    :", lines[0].split("vertexName=")[1])
print("root cause:", causes[-1].split(": ", 2)[-1])
'''
RUN = dict(
    heading='Run the code: triage like an on-call engineer',
    intro='<p>These programs apply the troubleshooting method to the real messages and numbers from the lab. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('causes = [l for l in lines if l.startswith("Caused by")]', 'Java nests exceptions: each “Caused by” wraps the next. The innermost one, printed last, is the real reason.'),
        ('kind = "runtime (return code 2)" if "return code 2" in lines[0] else "compile time"', 'Compile-time errors (SemanticException, code 40000/100xx) happen before any task; return code 2 means a task failed at run time.'),
    ],
    tasks=[
        dict(label='1 · Root cause', hint='Press <b>Run</b>. The message is from the lab (shortened). The root cause is the assertion, not “Hive Runtime Error”.', code=None),
        dict(label='2 · Predict first: compile or runtime?', hint='<b>Predict first:</b> classify each real message before running.',
             code='''msgs = ["FAILED: SemanticException Cartesian products are disabled for safety reasons",
        "FAILED: Execution Error, return code 2 from ...TezTask. Vertex failed",
        "[Error 20004]: Fatal error occurred when node tried to create too many dynamic partitions",
        "Query timed out after 0 seconds"]
for m in msgs:
    kind = "compile" if "SemanticException" in m else "runtime"
    print(f"{kind:8} <- {m[:60]}")
'''),
        dict(label='3 · Small-files cost', hint='Real timings: 300 files vs 1 file, same 5,000,000 rows.',
             code='''before = [1.806, 1.706]
after = [1.046, 0.976]
avg = lambda xs: sum(xs) / len(xs)
print(f"300 files: {avg(before):.2f} s, 1 file: {avg(after):.2f} s, {avg(before) / avg(after):.1f}x slower")
'''),
        dict(label='4 · NULL check after a load', hint='Count values that would become NULL when cast, like the lab’s data quality query.',
             code='''vals = ["1,250.00", "300.00", "N/A", "99.5", "2,000"]
def to_dec(s):
    try: return float(s)
    except ValueError: return None
ok = sum(to_dec(v) is not None for v in vals)
fixed = sum(to_dec(v.replace(",", "")) is not None for v in vals)
print("cast ok:", ok, "became NULL:", len(vals) - ok, "ok after removing commas:", fixed)
'''),
        dict(label='5 · Spot the error', hint='This alert never fires for silent NULLs. Fix the condition.', expect='error',
             code='''rows, non_null = 1_000_000, 938_796
null_rate = (rows - non_null) / rows
alert = null_rate > 0.5                      # bug: threshold far too high
assert alert, f"NULL rate {null_rate:.1%}: alert on a jump from the usual rate, not only above 50%"
print("ALERT")
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: a data quality check and two quick diagnostics',
    intro='<p>Small queries that belong in every troubleshooting toolkit. <b>Outputs are real</b>, from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · How many values become NULL, and does the fix work?', cmd="SELECT COUNT(*) AS total_rows,\n       COUNT(CAST(a AS DECIMAL(10,2))) AS cast_ok,\n       COUNT(*) - COUNT(CAST(a AS DECIMAL(10,2))) AS became_null,\n       COUNT(CAST(regexp_replace(a, ',', '') AS DECIMAL(10,2))) AS cast_ok_after_fix\nFROM (SELECT stack(5, '1,250.00', '300.00', 'N/A', '99.5', '2,000') AS a) s;", file='Beeline',
             output=capf('l85_dq.txt'),
             note='Three of five values silently became NULL. Removing commas rescues two; “N/A” stays NULL, which is correct, but it should be counted and reported, not hidden.'),
        dict(title='2 · Is a table fragmented?', cmd="SHOW TBLPROPERTIES orders_frag ('numFiles');   -- before the rewrite", file='Beeline',
             output='\n'.join(capf('l85_small_mk.txt').split('\n')[-5:]),
             note='300 files for 5,000,000 rows (about 10 MB of ORC): roughly 34 KB per file. A quick health check over all tables compares numFiles with totalSize.'),
        dict(title='3 · Is one key hot?', cmd='SELECT customer_id, COUNT(*) AS n FROM orders_skew\nGROUP BY customer_id ORDER BY n DESC LIMIT 3;', file='Beeline',
             output=capf('l83_skewmk.txt'),
             note='From Lesson 8.3: one customer holds 40% of the rows. When one task runs far longer than the rest, this query is the first check.'),
    ],
)

TRACE = dict(
    heading='Tez retrying a failing task',
    intro='<p>Watch the attempts for Map 1’s only task. Bad data fails every time, so the retries cannot succeed.</p>',
    code='''max_attempts = 4
failed = 0
for attempt in range(max_attempts):
    ok = False                       # amount >= 800 exists in every attempt
    if not ok:
        failed += 1
task_failed = failed == max_attempts
print("attempts failed:", failed, "-> vertex failed:", task_failed)
''',
    notes={1: 'Attempts :: Our lab showed TaskAttempt 0, 1, 2 and 3: four tries.', 4: 'Same data :: A retry re-reads the same rows, so a data error repeats.', 7: 'Result :: OWN_TASK_FAILURE, then VERTEX_FAILURE for the DAG.'},
)

WORKED_INTRO = 'Three troubleshooting tasks from real on-call shifts.'
EXAMPLES = [
    dict(level='b', tag='Operations · triage', title='Sort the morning’s problems',
         problem='<p>Classify five Monday-morning messages into compile-time, runtime, performance and correctness problems.</p>',
         inp='the five symptoms from the story',
         approach=['SemanticException → compile time.', 'Vertex failed / Error 20004 / timeout → runtime.', 'Long running → performance; wrong totals → correctness.'],
         code='''issues = {"report still running after 40 min": "performance",
          "Vertex failed, return code 2": "runtime",
          "dashboard totals 12% lower, no errors": "correctness",
          "[Error 20004] too many dynamic partitions": "runtime (limit)",
          "Cartesian products are disabled": "compile time (strict check)"}
for k, v in issues.items():
    print(f"{v:28} <- {k}")
''', notes={6: 'Order :: Correctness problems first: wrong numbers reach decisions.'},
         tryit='Each class has its first tool: PROCESSLIST and counters, the last Caused by, the strict-check message, NULL and row counts.'),
    dict(level='i', tag='Data engineering · small files', title='Find fragmented tables',
         problem='<p>Given numFiles and totalSize per table, list tables whose average file is under 16 MB with more than 100 files.</p>',
         inp='orders_frag: 300 files, 10.2 MB · orders_big: 1 file, 10.2 MB · clicks: 40,000 files, 80 GB (illustrative)',
         approach=['Average size = totalSize / numFiles.', 'Apply both thresholds.', 'Rewrite the worst first.'],
         code='''tables = {"orders_frag": (300, 10.2e6), "orders_big": (1, 10.2e6), "clicks": (40000, 80e9)}
for t, (files, size) in tables.items():
    avg_mb = size / files / 1e6
    if files > 100 and avg_mb < 16:
        print(f"{t:12} {files:>6} files, avg {avg_mb:.2f} MB -> rewrite with hive.merge.tezfiles=true")
''', notes={4: 'Rule :: 16 MB matches hive.merge.smallfiles.avgsize in our lab.'},
         tryit='Both orders_frag and clicks qualify. CONCATENATE works for managed ORC/RC tables; external ones need a rewrite, as in Step 6.'),
    dict(level='a', tag='Platform · guard rails', title='Choose guard rails for a shared cluster',
         problem='<p>A shared cluster has 300 analysts. Choose settings that stop the three costliest mistakes seen last quarter.</p>',
         inp='incidents: accidental cross join, full scans of a 3-year partitioned table, ORDER BY on 2 billion rows',
         approach=['Map each incident to a strict check.', 'Add a timeout for ad-hoc queues.', 'Communicate the messages users will see.'],
         code='''rails = {"cross join": "hive.strict.checks.cartesian.product=true",
         "full scans": "hive.strict.checks.no.partition.filter=true",
         "huge ORDER BY": "hive.strict.checks.orderby.no.limit=true",
         "runaway ad-hoc": "hive.query.timeout.seconds=1800s"}
for incident, setting in rails.items():
    print(f"{incident:15} -> SET {setting};")
''', notes={5: 'Timeout :: Only for the ad-hoc queue: ETL jobs may legitimately run longer.'},
         tryit='All three strict checks produced clear, named errors in our lab. Set them in hive-site.xml for the cluster, not per session.'),
]

QUIZ = mix([
    dict(q='Beginner: Which command lists running queries in Hive 4?', options=['SHOW JOBS', 'SHOW PROCESSLIST', 'SHOW QUERIES', 'LIST TASKS'], answer=1,
         why='It shows sessions, Query IDs, state and elapsed time.'),
    dict(q='Beginner: Where is the real reason in a long Hive/Tez error?', options=['The first line', 'Usually the last “Caused by”', 'The Query ID', 'The stack’s first “at …” line'], answer=1,
         why='Lab: ASSERT_TRUE(): assertion failed, after several wrapper exceptions.'),
    dict(q='Beginner: What did CAST(\'12a\' AS INT) return?', options=['An error', 'NULL', '12', '0'], answer=1,
         why='Silent NULLs: no error, smaller totals.'),
    dict(q='Intermediate: How many attempts did Tez make for the failing task?', options=['1', '2', '4', 'Unlimited'], answer=2,
         why='TaskAttempt 0–3, then the vertex failed.'),
    dict(q='Intermediate: Which setting blocks queries on partitioned tables without a partition filter?', options=['hive.strict.checks.cartesian.product', 'hive.strict.checks.no.partition.filter', 'hive.exec.dynamic.partition', 'hive.optimize.ppd'], answer=1,
         why='Error 10056 in our lab.'),
    dict(q='Intermediate: What does Error 20004 mean?', options=['Disk full', 'A task tried to create more dynamic partitions than allowed', 'Bad SQL', 'Timeout'], answer=1,
         why='Maximum was 10 per node; the task reached 11.'),
    dict(q='Advanced: 300 small files were grouped into one Tez task. Was the query still slower?', options=['No, grouping removes the cost', 'Yes, about 1.7 s vs 1.0 s with one file', 'It failed', 'It was faster'], answer=1,
         why='Each file still has to be opened and its footer read.'),
    dict(q='Advanced: Why did ALTER TABLE orders_frag CONCATENATE fail?', options=['ORC not supported', 'Concatenate only works on managed tables; this one was external', 'Too many files', 'Statistics missing'], answer=1,
         why='Error 30034; a rewrite with hive.merge.tezfiles=true fixed it.'),
])

REVISION = [
    '<b>Method:</b> find (PROCESSLIST, counters) → read (last “Caused by”) → fix the cause → measure again.',
    '<code>SHOW PROCESSLIST</code> shows Query IDs; <code>KILL QUERY \'id\'</code> cancels (“Query was cancelled. User invoked KILL QUERY”).',
    '<b>Compile-time</b> (SemanticException) vs <b>runtime</b> (return code 2, Vertex failed, task attempts 0–3).',
    '<b>Strict checks:</b> cartesian.product, no.partition.filter (Error 10056), orderby.no.limit; or <code>hive.mapred.mode=strict</code>.',
    '<b>Limits:</b> <code>hive.exec.max.dynamic.partitions[.pernode]</code> (Error 20004), <code>hive.query.timeout.seconds</code>.',
    '<b>Small files:</b> INPUT_FILES 300 → 1.7 s vs 1 file → 1.0 s; CONCATENATE only on managed tables; rewrite with <code>hive.merge.tezfiles=true</code>.',
    '<b>Silent NULLs:</b> bad casts, /0, invalid dates, decimal overflow → NULL; check <code>COUNT(*) - COUNT(col)</code> after loads.',
    '<b>Counters:</b> RECORDS_IN, INPUT_FILES, GROUPED_INPUT_SPLITS, SPILLED_RECORDS, SHUFFLE_BYTES(_TO_DISK), DESERIALIZE_ERRORS, CREATED_FILES.',
]
FAQ = [
    ('Where are the full logs?', 'HiveServer2 writes its log (often under /tmp/&lt;user&gt;/hive.log or the service log directory); Beeline shows a summary, and with <code>--verbose=true</code> or INFO lines more detail. Task logs live with the Tez containers: in YARN, <code>yarn logs -applicationId application_…</code> or the Tez UI. The Query ID links all of them.'),
    ('What does “return code 2” mean?', 'It is the code HiveServer2 reports when the Tez (or MapReduce) task of the query failed at run time. It says nothing about why; the reason is in the diagnostics that follow, typically the last “Caused by”.'),
    ('How do I find out of memory errors?', 'Look for <code>java.lang.OutOfMemoryError</code>, “Container killed … running beyond physical memory limits”, or map-join memory messages in the task diagnostics. Common fixes: correct statistics so a big table is not broadcast (8.2/8.3), larger <code>hive.tez.container.size</code> with heap about 80%, or less data per task.'),
    ('Is it safe to just raise limits like max dynamic partitions?', 'Only after checking why the limit was hit. Partitioning by a high-cardinality column (a timestamp, a user ID) can create millions of tiny partitions and overload the metastore. The limit is often protecting you.'),
    ('Does Hive keep a history of queries?', 'HiveServer2’s web UI (port 10002) shows recent and running queries with their plans and timings. Distributions add query history tables and tools (for example Hue, Cloudera’s query history). In our lab the <code>sys</code> database was not installed, so we used PROCESSLIST and logs.'),
]

PRACTICE_INTRO = 'Programs for everyday troubleshooting checks, with the HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Pairs in a self-join', stmt='How many pairs does joining a customer’s 2,500 orders with themselves create, for 2,000 customers?', inp='2,500 rows per key, 2,000 keys',
         code='''print(2500 * 2500 * 2000)
''', explain='12,500,000,000 pairs: why the runaway query in Step 1 had to be killed.'),
    dict(level='easy', title='Files per MB', stmt='Average file size of orders_frag.', inp='10,195,843 bytes in 300 files (approx.)',
         code='''print(round(10_195_843 / 300 / 1024, 1), "KB per file")
''', explain='About 33 KB per file: far below any sensible target size.'),
    dict(level='easy', title='Partitions per task', stmt='Will an insert of 30 dates fail with pernode=10?', inp='30 dates, one task',
         code='''print(30 > 10)
''', explain='True: Error 20004. One task saw all 30 dates.'),
    dict(level='medium', title='Last Caused by', stmt='Extract the root cause from a list of exception lines.', inp='lines from the lab',
         code='''lines = ["Caused by: java.lang.RuntimeException: ... Hive Runtime Error while processing row",
         "Caused by: org.apache.hadoop.hive.ql.metadata.HiveException: ASSERT_TRUE(): assertion failed."]
print([l for l in lines if l.startswith("Caused by")][-1].split("HiveException: ")[-1])
''', explain='The same idea works with grep on a log: grep "Caused by" hive.log | tail -1.'),
    dict(level='medium', title='Classify by error code', stmt='Map Hive error codes to categories.', inp='10056, 20004, 30034, 40000',
         code='''codes = {10056: "semantic analysis (strict check)", 20004: "runtime, retry unlikely to help", 30034: "other (concatenate rule)", 40000: "generic, retry may help"}
for c, k in codes.items():
    print(c, "->", k)
''', explain='Hive’s ErrorMsg ranges: 1xxxx semantic analysis, 2xxxx runtime errors where retries are unlikely to help, 3xxxx errors with no retry advice, 4xxxx errors where a retry may help. The text after the code is what matters most.'),
    dict(level='medium', title='NULL rate jump', stmt='Alert when today’s NULL rate is more than 5 points above the 7-day average.', inp='rates',
         code='''history = [0.001, 0.0012, 0.0009, 0.001, 0.0011, 0.001, 0.0012]
today = 0.061
avg = sum(history) / len(history)
print("ALERT" if today - avg > 0.05 else "ok", f"(avg {avg:.2%}, today {today:.1%})")
''', explain='A relative check catches format changes that a fixed threshold would miss.'),
    dict(level='business', title='Cost of a runaway query', stmt='A runaway query holds 200 containers for 3 hours before someone kills it. How many container-hours?', inp='illustrative',
         code='''print(200 * 3, "container-hours")
''', explain='600 container-hours; a query timeout on the ad-hoc queue would have stopped it.'),
    dict(level='business', title='Rerun scope', stmt='A load failed on 3 of 30 partitions. Rerun everything or only the failed ones?', inp='30 partitions, 20 min each (illustrative)',
         code='''print("all:", 30 * 20, "min  vs  failed only:", 3 * 20, "min")
''', explain='Idempotent INSERT OVERWRITE per partition makes partial reruns safe and fast.'),
]

SCN_INTRO = 'Troubleshooting is where interviews become practical; walk through your method out loud.'
SCENARIOS = (
    scn('Any company · Hive', 'Fresher', '“A Hive query failed. What do you do?”',
        'Describe your first steps.',
        'do you read errors methodically?',
        '<p>Check whether it failed at compile time (SemanticException: fix the SQL or the setting it names) or at run time (return code 2, Vertex failed). For runtime failures I read the last “Caused by” in the diagnostics or the task logs, which names the real reason: bad data, a UDF error, memory. I fix that cause and rerun only what failed.</p>', 'Rerunning repeatedly without reading the error.') +
    scn('Data engineering', 'Mid-level', 'A query got slow',
        'A daily query went from 5 to 40 minutes.',
        'can you measure before changing settings?',
        '''<ol>
          <li>Compare counters with an older run: RECORDS_IN, INPUT_FILES, SHUFFLE_BYTES, SPILLED_RECORDS.</li>
          <li>Compare EXPLAIN plans: pruning, join type, statistics (Col:NONE, stale numRows).</li>
          <li>Fix the cause found (filter, statistics, small files, skew), one change at a time.</li>
        </ol>''', 'Doubling container memory first.') +
    scn('Analytics', 'Mid-level', 'Numbers look wrong',
        'Revenue on the dashboard dropped 12% but no job failed.',
        'do you know silent failure modes?',
        '''<ul>
          <li>Check NULL counts and row counts per load; failed casts become NULL silently.</li>
          <li>Check duplicates per key after joins (fan-out) and late-arriving partitions.</li>
          <li>Fix the conversion, reload affected partitions, add a data quality check.</li>
        </ul>''', 'Assuming the business changed.') +
    scn('Platform', 'Senior', 'Protecting a shared cluster',
        'Design guard rails for a cluster used by 300 analysts and 50 ETL jobs.',
        'can you prevent problems, not only fix them?',
        '''<ul>
          <li>Strict checks on (cartesian, partition filter, ORDER BY without LIMIT), query timeouts on ad-hoc queues, sensible dynamic partition limits.</li>
          <li>Queues or workload management separating ETL and ad-hoc; counters exported and charted per job.</li>
          <li>Runbooks: PROCESSLIST/KILL, reading failures, partition reruns, small-file housekeeping, data quality checks.</li>
        </ul>''', 'Relying on users to write safe SQL.')
)
