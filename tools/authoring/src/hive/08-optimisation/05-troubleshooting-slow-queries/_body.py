import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()

def plist():
    rows = [l for l in capf('l85_plist.txt').split('\n') if l.startswith('|')]
    cells = [[c.strip() for c in r.strip('|').split('|')] for r in rows]
    keep = [0, 2, 6, 7, 10, 11]
    out = [[c[i] for i in keep] for c in cells]
    w = [max(len(r[i]) for r in out) for i in range(len(keep))]
    line = '+' + '+'.join('-' * (x + 2) for x in w) + '+'
    fmt = lambda r: '| ' + ' | '.join(r[i].ljust(w[i]) for i in range(len(r))) + ' |'
    return '\n'.join([line, fmt(out[0]), line] + [fmt(r) for r in out[1:]] + [line])

def opbox(x, y, label, sub='', tone='card', w=128, h=26):
    o = box(x, y, w, h, tone) + t(x + w / 2, y + (11 if sub else 16), label, 7.2, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 21, sub, 6.4, 'ink2', mono=True)
    return o

# ---------------------------------------------------------------- story
sc = (box(10, 12, 190, 128, 'card') + t(105, 30, 'Monday 9:05 am', 8.8, bold=True) +
      ''.join(t(22, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([('report: still running', 'amber'), ('ETL: FAILED, return code 2', 'red'), ('dashboard: wrong totals', 'red'), ('loader: Error 20004', 'red'), ('ad-hoc: timed out', 'amber')])) +
      arrow(206, 76, 246, 76, 'acc', 2.2) + box(252, 46, 110, 60, 'violet') + t(307, 72, 'A method,', 8.4, bold=True) + t(307, 88, 'not guesses', 8.4, bold=True) +
      arrow(368, 76, 404, 76, 'acc', 2.2) + box(410, 12, 220, 128, 'green') + t(520, 30, 'Find · Read · Fix', 8.8, 'green', bold=True) +
      opbox(422, 40, '1 Find it', 'PROCESSLIST · counters', 'card', 196) + opbox(422, 72, '2 Read the error', 'last “Caused by”', 'card', 196) + opbox(422, 104, '3 Fix the cause', 'plan · stats · files · data', 'card', 196))
scene_svg = scene('Five problems on a Monday morning: a long-running report, a failed ETL job, wrong totals, a dynamic partition error and a timeout. The answer is a method: find the query, read the error, fix the cause.', sc,
                  'Every problem today was <tspan font-weight="700" class="s-acc">produced and solved in the lab</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Everything is broken and the CXO dashboard is due at ten”</h2>
  <div class="story">
    <p class="narration">It is Monday morning at TiffinGo. A report is still running, an ETL job failed with a wall of Java, a dashboard shows strange totals, a loader died with “Error 20004” and an analyst’s query timed out. Riya is on call for the first time.</p>

{scene_svg}

R> Sir, where do I even start? The logs are thousands of lines.
A> With a method. First <b>find</b> what is running and what failed: <code>SHOW PROCESSLIST</code>, the Tez summary and counters. Then <b>read</b> the error properly: the useful line is almost always the <i>last</i> “Caused by”. Then <b>fix the cause</b>, which is usually one of the things from this module: the plan, the statistics, the joins, the files or the data itself.
K> And some errors are good news?
A> Yes. Hive’s <b>strict checks</b> stop dangerous queries before they run: a Cartesian product, a scan of every partition, an ORDER BY without LIMIT. We will trigger each one, kill a runaway query, fail a task four times on purpose, hit the dynamic partition limit, speed up a table with 300 small files, and find wrong results that raise no error at all. All outputs are real, from Hive 4.2.1.
  </div>
</section>
'''

lv = '''
LEVELS> Troubleshooting at three levels
L1> A doctor’s routine
      <ul>
        <li>A doctor asks where it hurts, runs tests, then treats the cause, not the symptom. Do the same with queries.</li>
        <li><b>Slow</b> and <b>failed</b> are different problems: slow needs measuring (plan, counters); failed needs reading the error.</li>
        <li>Most error messages repeat themselves; the real reason is usually near the end.</li>
      </ul>
L2> Tools and where they point
      <ul>
        <li><b>Running now:</b> <code>SHOW PROCESSLIST</code>, <code>KILL QUERY 'id'</code>, YARN / Tez UI.</li>
        <li><b>Slow:</b> EXPLAIN (8.1), statistics (8.2), join type (8.3), vectorisation and task counts (8.4), counters like <code>INPUT_FILES</code>, <code>SPILLED_RECORDS</code>, <code>SHUFFLE_BYTES</code>.</li>
        <li><b>Failed:</b> the Hive error code, “Vertex failed”, task attempts, the last <code>Caused by</code>.</li>
        <li><b>Prevented:</b> strict checks for Cartesian products, partition filters, ORDER BY without LIMIT; limits on dynamic partitions; query timeouts.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>A failing expression made Map 1 fail <b>4 task attempts</b>, then the vertex, then the DAG; the cause was one line: <code>ASSERT_TRUE(): assertion failed</code>.</li>
        <li>300 small ORC files: the same 5,000,000-row query took about 1.7 s vs 1.0 s after rewriting into one file, though Tez grouped all 300 splits into one task. <code>CONCATENATE</code> refused: “only … managed tables”.</li>
        <li>Bad casts, division by zero, invalid dates and decimal overflow all returned <b>NULL</b> without any error.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Troubleshooting Hive queries</h2>
''' + def_block(
    '<b>Troubleshooting</b> a Hive query means locating the query and stage responsible for a problem, determining whether it is a <b>compile-time</b> error (parsing, semantic analysis, strict checks), a <b>runtime</b> failure (task or vertex failure, resource limits, timeouts), a <b>performance</b> problem (plan, statistics, data layout, skew, resources) or a <b>correctness</b> problem (silent NULLs, duplicates, wrong joins), and then fixing the root cause. The main evidence comes from <code>SHOW PROCESSLIST</code>, EXPLAIN, the Tez vertex summary and counters (<code>hive.tez.exec.print.summary</code>), HiveServer2 and Tez task logs, and the nested <code>Caused by</code> chain of exceptions.',
    'When a query is slow or fails, find which query and which step is the problem, read the actual cause in the error message, and fix that cause: the plan, the statistics, the files, the data or a setting. Guessing and adding memory usually does not help.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Compile-time error', 'Rejected before running: syntax, semantics, strict checks.'),
    ('Runtime failure', 'A task or vertex failed while running.'),
    ('Task attempt', 'One try of a task; Tez retries a failing task.'),
    ('Root cause', 'Usually the last “Caused by” in the stack.'),
    ('Strict checks', 'Settings that block risky queries before they run.'),
    ('Counter', 'A number Tez records per vertex: records, files, bytes, spills.'),
    ('Small files', 'Many tiny files that cost time to open and track.'),
    ('Silent NULL', 'A failed conversion that returns NULL instead of an error.'),
]) + '''

  <h3>Symptom → first place to look</h3>
''' + table(['Symptom', 'First look', 'Usual causes (lesson)'], [
    ['Query slower than yesterday', 'EXPLAIN diff, EXPLAIN ANALYZE', 'Stale stats, changed join (8.1–8.3)'],
    ['One task runs far longer', 'Tez UI per-task times, key counts', 'Skew (8.3)'],
    ['Many tasks, little data each', '<code>INPUT_FILES</code>, <code>RAW_INPUT_SPLITS</code>', 'Small files (5.4, this lesson)'],
    ['High CPU, simple query', 'EXPLAIN VECTORIZATION', 'Row mode, text format (8.4, 6.x)'],
    ['“Vertex failed … return code 2”', 'Last <code>Caused by</code>', 'Bad data, UDF error, memory'],
    ['“SemanticException”', 'The message itself', 'SQL error or strict check'],
    ['Wrong totals, no error', 'NULL counts, duplicates per key', 'Silent NULLs, join fan-out'],
], minw=720) + lv + '''
EXAM> “How do you troubleshoot a slow Hive query?” Reproduce and measure (Tez summary, counters), read the plan (EXPLAIN / ANALYZE), check statistics, join strategy, partition pruning, vectorisation, file counts and skew, change one thing at a time, and compare. For failures, read the last “Caused by” first.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Guard rails and limits (Hive 4.2.1 lab defaults)</h2>
''' + table(['Setting', 'Lab value', 'Stops'], [
    ['<code>hive.strict.checks.cartesian.product</code>', 'false', 'Joins without a join condition'],
    ['<code>hive.strict.checks.no.partition.filter</code>', 'false', 'Scans of partitioned tables without a partition filter'],
    ['<code>hive.strict.checks.orderby.no.limit</code>', 'false', 'ORDER BY without LIMIT (one reducer sorts everything)'],
    ['<code>hive.mapred.mode=strict</code>', 'not set', 'Turns the strict checks on together'],
    ['<code>hive.query.timeout.seconds</code>', '0s (none)', 'Queries running longer than the limit'],
    ['<code>hive.exec.max.dynamic.partitions[.pernode]</code>', '1000 / 100', 'Inserts creating too many partitions'],
    ['<code>hive.merge.tezfiles</code>', 'false', '(when true) merges small output files after a Tez job'],
], minw=720) + '''
WARN> The strict checks are <b>off</b> by default in our lab. Many platforms switch them on for shared clusters, so a query that worked on your laptop may be rejected in production. Read the message: it names the exact setting.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Eight real problems, produced and solved</h2>
  <p>All outputs are real, from the Hive 4.2.1 lab. Long Java messages are shortened with “…”.</p>
''' + stepper([
    ('Step 1 · Find what is running',
     code('sql', 'Beeline', "-- session 1: a runaway self-join on 5,000,000 rows\nSELECT COUNT(*) FROM orders_big_txt a JOIN orders_big_txt b ON a.customer_id = b.customer_id;\n\n-- session 2:\nSHOW PROCESSLIST;     -- selected columns", plist()),
     'Hive 4’s <code>SHOW PROCESSLIST</code> lists open sessions with the running <b>Query ID</b>, state and elapsed time. The query joins each customer’s 2,500 rows with the same 2,500 rows: about 12.5 billion pairs, a classic accidental explosion.'),
    ('Step 2 · Kill it',
     code('sql', 'Beeline', "KILL QUERY 'hive_20261027114151_acf33829-3758-4648-b9f7-99c5ef4540af';\n\n-- what session 1 sees:", capf('l85_victim.txt')),
     'The victim session gets <code>Query was cancelled. User invoked KILL QUERY</code> and its Tez DAG is stopped. Admins (or the query’s owner) can kill by Query ID, without restarting HiveServer2. In our lab the KILL statement itself did not return to its client promptly, so run it from a separate session and check PROCESSLIST again.'),
    ('Step 3 · Read a task failure from the bottom',
     code('sql', 'Beeline', "SELECT COUNT(*) FROM orders WHERE assert_true(amount < 800) IS NULL;\n-- the error, with the repeated stack traces removed", capf('l85_taskfail_clean.txt')),
     'The first line only says that Map 1 failed (<code>return code 2</code> is a runtime failure). Tez retried the task <b>4 times</b> (attempts 0–3), each failing with the same <b>last “Caused by”</b>: <code>ASSERT_TRUE(): assertion failed</code>, because some orders have amount ≥ 800. Then the vertex failed (<code>OWN_TASK_FAILURE</code>) and the DAG was stopped. In real jobs the last “Caused by” names the bad UDF, the corrupt file or the out-of-memory error; retries do not help with bad data.'),
    ('Step 4 · Strict checks: rejected before running',
     code('sql', 'Beeline', "SET hive.strict.checks.cartesian.product=true;\nSELECT COUNT(*) FROM customers a, customers b;\n\nSET hive.strict.checks.no.partition.filter=true;\nSELECT COUNT(*) FROM orders_by_day;\n\nSET hive.mapred.mode=strict;\nSELECT order_id FROM orders ORDER BY amount;", '\n\n'.join(capf(n) for n in ('l85_cartesian.txt', 'l85_partfilter.txt', 'l85_orderby.txt'))),
     'Three <b>SemanticException</b>s, raised at compile time, before any resource is used: a join without a condition (2,000 × 2,000 = 4,000,000 pairs here, billions in production), a full scan of a partitioned table, and a global sort without LIMIT. Each message names the setting. Note that <code>hive.mapred.mode=strict</code> alone was enough to block the ORDER BY.'),
    ('Step 5 · Runtime limits: dynamic partitions and timeouts',
     code('sql', 'Beeline', "SET hive.exec.dynamic.partition.mode=nonstrict;\nSET hive.exec.max.dynamic.partitions.pernode=10;\nINSERT INTO dp_test PARTITION (order_date) SELECT order_id, amount, order_date FROM orders;\n\nSET hive.query.timeout.seconds=1s;\nSELECT customer_id, COUNT(DISTINCT city), SUM(amount) FROM orders_big_txt GROUP BY customer_id;", capf('l85_dynpart_clean.txt') + '\n\n' + capf('l85_timeout.txt')),
     'The insert would create 30 daily partitions, but one task may create only 10: <b>Error 20004</b> stops it at the 11th, with the numbers in the message. Raise the limit only after checking that the partition column is right (a timestamp instead of a date can create millions). The timeout cancelled the query after 1 second; the message rounds it down to “0 seconds”.'),
    ('Step 6 · Slow because of 300 small files',
     code('sql', 'Beeline', "-- orders_frag: 5,000,000 rows written by 300 reducers with hive.merge.tezfiles=false\nSET hive.tez.exec.print.summary=true;\nSELECT city, COUNT(*), SUM(amount) FROM orders_frag GROUP BY city;\n\nALTER TABLE orders_frag CONCATENATE;\n\nSET hive.merge.tezfiles=true;\nINSERT OVERWRITE TABLE orders_frag SELECT * FROM orders_frag;", capf('l85_files.txt') + '\n\n' + capf('l85_concat_err.txt').split('; Query ID')[0]),
     'The counters show the problem: <code>INPUT_FILES_Map_1: 300</code>. Tez grouped all 300 splits into one task, yet the query took about <b>1.7 s</b> against <b>1.0 s</b> for the same data in one file: opening and reading 300 file footers costs time (and on HDFS, NameNode memory). <code>CONCATENATE</code> was refused because the table is external; rewriting it with <code>hive.merge.tezfiles=true</code> produced <b>1 file</b>.'),
    ('Step 7 · Wrong results without any error',
     code('sql', 'Beeline', "SELECT CAST('12a' AS INT) AS bad_cast, 10 / 0 AS div_zero,\n       CAST('2026-13-45' AS DATE) AS bad_date, CAST(99999 AS DECIMAL(4,2)) AS overflow;", capf('l85_silent.txt')),
     'Four mistakes, four <b>NULL</b>s, no error and no warning. In a SUM or COUNT(col) these rows just disappear, so a dashboard shows smaller totals. Check NULL counts after every load (<code>COUNT(*) - COUNT(col)</code>), and compare row counts between source and target.'),
    ('Step 8 · The counters worth reading',
     code('sql', 'Beeline', "SET hive.tez.exec.print.summary=true;\n-- run the query; selected counters from the INFO output (orders_frag, before the fix)", capf('l85_counters.txt')),
     'A short list covers most cases: <code>RECORDS_IN_Map_1</code> (rows read: is pruning working?), <code>INPUT_FILES</code> vs <code>GROUPED_INPUT_SPLITS</code> (small files), <code>SPILLED_RECORDS</code> and <code>SHUFFLE_BYTES_TO_DISK</code> (memory pressure in sorts and shuffles), <code>SHUFFLE_BYTES</code> (join and group-by traffic), <code>DESERIALIZE_ERRORS</code> (bad input), and <code>CREATED_FILES</code> on writes (small files in the making).'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('> SHOW PROCESSLIST;', W), ('hive  tez  hive_…114151_acf3…  RUNNING', Y), ("> KILL QUERY 'hive_…114151_…';", W), ('Query was cancelled.', G), ('User invoked KILL QUERY', G)], size=7.4),
    term([('FAILED: … return code 2 … TezTask.', RD), ('Vertex failed, vertexName=Map 1 …', RD), ('TaskAttempt 0 … 3 failed', Y), ('Caused by: … HiveException:', W), ('  ASSERT_TRUE(): assertion failed.', G)], size=7.4),
    term([('SemanticException Cartesian products', RD), ('  are disabled for safety reasons', RD), ('[Error 10056]: … without a partition filter', RD), ('Order by-s without limit are disabled', RD)], size=7.2),
    term([('INPUT_FILES_Map_1: 300', RD), ('GROUPED_INPUT_SPLITS_Map_1: 1', Y), ('300 files ≈ 1.7 s · 1 file ≈ 1.0 s', W), ('CONCATENATE … only … managed tables', RD), ('merge rewrite → numFiles 1', G)], size=7.2),
    term([("CAST('12a' AS INT)            NULL", Y), ('10 / 0                        NULL', Y), ("CAST('2026-13-45' AS DATE)    NULL", Y), ('CAST(99999 AS DECIMAL(4,2))   NULL', Y)], size=7.4),
]
def ladder(hi):
    names = [('Query', 'DAG'), ('Vertex', 'Map 1'), ('Task', '1 of N'), ('Attempt', '0 … 3'), ('Caused by', 'root cause')]
    o = ''
    for k, (a, b) in enumerate(names):
        o += opbox(14 + k * 68, 52, a, b, 'acc' if k == hi else 'card', 62, 30)
        if k:
            o += arrow(14 + k * 68 - 6, 67, 14 + k * 68, 67, 'ink3', 1.4)
    return o
B1 = [
    t(180, 22, 'Find it: sessions and query IDs', 9.4, bold=True) + ladder(0) + cap('Kill by Query ID, no restart needed.', '', 'blue', y=140, h=34),
    t(180, 22, 'Read failures from right to left', 9.4, bold=True) + ladder(4) + cap('The last “Caused by” is the real reason.', 'Retries cannot fix bad data.', 'amber', y=130, h=46),
    t(180, 22, 'Compile time: cheapest failure', 9.4, bold=True) + opbox(40, 56, 'SQL', '', 'card', 70) + arrow(112, 69, 140, 69, 'ink3') + opbox(142, 56, 'Strict checks', 'reject', 'red', 90) + t(290, 72, 'no job', 8.4, 'green', bold=True) + cap('Blocked before using the cluster.', '', 'green', y=140, h=34),
    t(180, 22, 'Small files: grouped, still costly', 9.4, bold=True) + ''.join(box(20 + (k % 15) * 10, 46 + (k // 15) * 10, 8, 8, 'amber') for k in range(60)) + arrow(176, 66, 210, 66, 'ink3', 1.6) + box(216, 46, 60, 40, 'green') + t(246, 70, '1 file', 7.6, 'ink', bold=True) + cap('Fewer files: less opening, less metadata.', '', 'green', y=140, h=34),
    t(180, 22, 'Silent NULLs shrink totals', 9.4, bold=True) + fill(40, 56, 260, 12, 'blue', rx=2) + t(40, 84, 'loaded rows', 7.6, 'ink2', anchor='start') + fill(40, 92, 210, 12, 'acc', rx=2) + t(40, 120, 'rows counted in SUM(amount)', 7.6, 'ink2', anchor='start') + cap('Check COUNT(*) - COUNT(col) after loads.', '', 'amber', y=140, h=34),
]
see_caps = ['A runaway query found with SHOW PROCESSLIST and killed.',
            'A task failed four times; the last Caused by says why.',
            'Strict checks rejected three risky queries.',
            '300 small files slowed the query; a merge rewrite fixed it.',
            'Four conversion mistakes returned NULL without an error.']
behind_caps = ['HiveServer2 tracks sessions and running queries by ID.',
               'A query is a DAG of vertices, tasks and attempts; errors nest the same way.',
               'Semantic analysis stops these queries before any task starts.',
               'Each file costs an open and a footer read, even inside one task.',
               'Hive returns NULL for values it cannot convert.']
two = anim_two('Troubleshooting', 'Find, read, fix', 'Real lab outputs', 'Where the evidence is', see, B1, see_caps, behind_caps)

# ---- scenario 1: overnight ETL failed
e1 = (t(180, 22, '02:10 · ETL failed: return code 2', 9.4, bold=True) + t(180, 56, 'Vertex failed, vertexName=Map 3', 8.2, 'red', mono=True) + cap('Runtime failure, not a SQL error.', '', 'amber', y=150, h=34))
e2 = (t(180, 22, 'Scroll to the last “Caused by”', 9.4, bold=True) + t(180, 56, 'NumberFormatException: For input string: "N/A"', 7.8, 'red', mono=True) + cap('A UDF met bad data. (Illustrative message.)', '', 'amber', y=150, h=34))
e3 = (t(180, 22, 'Find the rows', 9.4, bold=True) + t(180, 56, "WHERE amount_str RLIKE '[^0-9.]'", 8.2, 'ink', mono=True) + cap('47 rows from one source file.', '', 'blue', y=150, h=34))
e4 = (t(180, 22, 'Fix and protect', 9.4, bold=True) + t(180, 56, 'clean in staging · quarantine bad rows', 8.2, 'ink2') + cap('Do not let one row kill the job.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Rerun only what failed', 9.4, 'acc', bold=True) + t(180, 56, 'INSERT OVERWRITE the affected partition', 8, 'ink2') + cap('Idempotent loads make reruns safe.', '', 'green', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'A 2 a.m. ETL failure',
              'The usual path from a failed job to a fix. (Messages illustrative; the reading method is the one from Step 3.)',
              'Runtime failure', 'Read the last Caused by, find the bad rows, quarantine them and rerun the affected partition', [e1, e2, e3, e4, e5],
              ['The job failed at run time.',
               'The root cause is at the end of the stack.',
               'Query for the offending rows.',
               'Clean or quarantine bad data.',
               'Rerun only the affected partition.'],
              hid='scenario-etl')

# ---- scenario 2: slow report triage
t1 = (t(180, 22, '“The sales report takes 40 minutes”', 9.4, bold=True) + t(180, 56, 'used to take 5', 8.4, 'ink2') + cap('Measure before changing anything.', '', 'blue', y=150, h=34))
t2 = (t(180, 22, 'Counters', 9.4, bold=True) + t(180, 52, 'RECORDS_IN_Map_1: 8× higher than last month', 7.8, 'red', mono=True) + t(180, 70, 'INPUT_FILES_Map_1: 40,000', 7.8, 'red', mono=True) + cap('More data read, and in tiny files.', '', 'amber', y=150, h=34))
t3 = (t(180, 22, 'EXPLAIN DEPENDENCY', 9.4, bold=True) + t(180, 56, 'all partitions read: an OR broke pruning', 8.2, 'ink2') + cap('Lesson 8.1.', '', 'amber', y=150, h=34))
t4 = (t(180, 22, 'Two fixes', 9.4, bold=True) + t(180, 52, 'rewrite the filter → pruning back', 8, 'ink', mono=True) + t(180, 70, 'merge small files in the loader', 8, 'ink', mono=True) + cap('One change at a time, measured.', '', 'green', y=150, h=34))
t5 = (t(180, 22, 'Back to 5 minutes', 9.4, 'acc', bold=True) + t(180, 56, 'add the checks to the review list', 8.2, 'ink2') + cap('Prevent the regression next time.', '', 'green', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'A report eight times slower',
              'Counters point to the cause. (Numbers illustrative; the counters are the ones from Step 8.)',
              'Slow query triage', 'Counters showed more records and many small files; EXPLAIN showed lost pruning; two targeted fixes restored the runtime', [t1, t2, t3, t4, t5],
              ['Start by measuring.',
               'Counters show more data and many files.',
               'The plan shows why: pruning was lost.',
               'Fix the filter and the files.',
               'Add the checks to reviews.'],
              hid='scenario-slow')

# ---- scenario 3: wrong numbers
w1 = (t(180, 22, '“Revenue dropped 12% overnight”', 9.4, bold=True) + t(180, 56, 'no failed jobs, no errors', 8.4, 'ink2') + cap('Correctness problem, not performance.', '', 'blue', y=150, h=34))
w2 = (t(180, 22, 'Count NULLs', 9.4, bold=True) + t(180, 56, 'COUNT(*) - COUNT(amount) = 61,204 (was 12)', 8, 'red', mono=True) + cap('Silent NULLs, like Step 7.', '', 'amber', y=150, h=34))
w3 = (t(180, 22, 'Why?', 9.4, bold=True) + t(180, 56, "source now sends '1,250.00' with a comma", 8.2, 'ink2', mono=True) + cap('CAST to DECIMAL returns NULL.', '', 'amber', y=150, h=34))
w4 = (t(180, 22, 'Fix', 9.4, bold=True) + t(180, 56, "CAST(regexp_replace(a, ',', '') AS DECIMAL(10,2))", 7.6, 'ink', mono=True) + cap('Reload the affected partitions.', '', 'green', y=150, h=34))
w5 = (t(180, 22, 'Guard', 9.4, 'acc', bold=True) + t(180, 56, 'data quality check: NULL rate per column per load', 8, 'ink2') + cap('Alert before the dashboard is wrong.', '', 'green', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Wrong numbers, no errors',
              'The hardest problems raise no error. (Numbers illustrative; the NULL behaviour is from Step 7.)',
              'Silent data errors', 'A format change in the source made casts return NULL; NULL-rate checks after each load catch it', [w1, w2, w3, w4, w5],
              ['Totals changed with no failure.',
               'NULL counts jumped.',
               'A source format change broke the cast.',
               'Fix the conversion and reload.',
               'Automate NULL-rate checks.'],
              hid='scenario-wrong')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Find, read, fix</h2>
  <p>Left: real lab outputs. Right: where the evidence comes from.</p>
''' + two + '''
  <p>Three live scenarios follow: a night-time ETL failure, a slow report, and wrong numbers without errors.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Troubleshooting at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'on-call', 11, 'green', bold=True) + t(60, 58, 'runbooks', 7.4, 'ink2'),
    '1. On-call runbooks',
    'Data platform teams keep runbooks: how to find a query, kill it, read the error and rerun a partition safely.',
    ['Alert', '*runbook', 'Resolved']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'strict', 11, 'blue', bold=True, mono=True) + t(60, 58, 'shared clusters', 7.4, 'ink2'),
    '2. Guard rails on shared clusters',
    'Strict checks, query timeouts and partition limits stop one user’s mistake from consuming the whole cluster.',
    ['Risky SQL', '*rejected', 'Cluster safe']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'counters', 10, 'violet', bold=True) + t(60, 58, 'monitoring', 7.4, 'ink2'),
    '3. Job monitoring',
    'Counters such as records read, input files and spilled records are exported per job and charted to catch slow drifts.',
    ['Counters', '*trend', 'Early warning']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'DQ', 12, 'acc', bold=True) + t(60, 58, 'checks', 7.4, 'ink2'),
    '4. Data quality checks',
    'NULL rates, row counts and duplicate keys are checked after every load, catching silent conversion errors.',
    ['Load', '*DQ checks', 'Trusted numbers']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'files', 11, 'acc', bold=True) + t(60, 58, 'housekeeping', 7.4, 'ink2'),
    '5. Small-file housekeeping',
    'Scheduled jobs find tables with many small files and rewrite or compact them before queries and the NameNode suffer.',
    ['File scan', '*merge', 'Healthy tables']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> this lesson uses everything in Module 8: <a href="../01-explain-in-depth/">8.1</a>, <a href="../02-cbo-and-statistics/">8.2</a>, <a href="../03-join-optimisations/">8.3</a>, <a href="../04-vectorisation-tez-and-llap/">8.4</a>, plus small files from <a href="../../05-partitioning-and-bucketing/04-partition-design-small-files-and-skew/">5.4</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
