import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
SCR = os.path.join(HERE, '..', '..', 'lab', 'scripts') + os.sep
def capf(n):
    return re.sub(r'; Query ID[^\n]*', '', open(CAP + n).read().rstrip())
def script(n):
    return open(SCR + n).read().rstrip()
def plain(n):
    lines = [l for l in capf(n).split('\n') if l.startswith('| ')]
    lines = [re.sub(r'\s*\|$', '', l[2:]).rstrip() for l in lines]
    return '\n'.join(l for l in lines if l.strip() not in ('Explain', '|', '')).strip('\n')
def pick(n, keys):
    return '\n'.join(l for l in plain(n).split('\n') if any(k in l for k in keys))

def opbox(x, y, label, sub='', tone='card', w=128, h=26):
    o = box(x, y, w, h, tone) + t(x + w / 2, y + (11 if sub else 16), label, 7.2, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 21, sub, 6.4, 'ink2', mono=True)
    return o

# ---------------------------------------------------------------- story
sc = (box(10, 12, 170, 128, 'card') + t(95, 30, 'Hive task', 8.8, bold=True) + t(95, 54, 'row → text line', 7.6, 'ink2', mono=True) + t(95, 72, '100001\\t2026-10…\\t530.00', 6.8, 'ink2', mono=True) +
      arrow(184, 64, 236, 64, 'acc', 2.2) + t(210, 56, 'stdin', 7, 'acc', mono=True) +
      box(240, 30, 150, 80, 'violet') + t(315, 56, 'python3 slot.py', 8.4, bold=True, mono=True) + t(315, 76, 'any language', 7.4, 'ink2') + t(315, 92, 'reads lines, prints lines', 7, 'ink2') +
      arrow(394, 64, 446, 64, 'acc', 2.2) + t(420, 56, 'stdout', 7, 'acc', mono=True) +
      box(450, 12, 180, 128, 'green') + t(540, 30, 'Back to Hive', 8.8, 'green', bold=True) + t(540, 54, 'text → columns', 7.6, 'ink2', mono=True) + t(540, 72, '100001  dinner  26.50', 7, 'ink', mono=True) + t(540, 96, 'AS (order_id, slot, gst)', 7, 'ink2', mono=True))
scene_svg = scene('Each Hive row is written as a tab-separated line to the standard input of a Python script; every line the script prints is split back into columns.', sc,
                  'TRANSFORM streams rows <tspan font-weight="700" class="s-acc">through any program</tspan>: text in, text out.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Our data scientists write Python, not Java”</h2>
  <div class="story">
    <p class="narration">Riya’s team has a Python function that labels each order with a meal slot and computes GST. The data platform team says Hive UDFs must be Java (Lesson 9.1). Riya does not want to rewrite working Python code.</p>

{scene_svg}

R> Sir, can Hive call my Python function directly?
A> Not as a function, but as a <b>stream</b>. <code>SELECT TRANSFORM (cols) USING 'python3 script.py' AS (…)</code> starts your script inside each task, writes every row to its standard input as a tab-separated line, and reads its standard output back as rows. It is the Hadoop Streaming idea inside SQL.
K> That sounds too easy. What is the catch?
A> Several, and we will hit each one in the lab: all output columns are strings unless you declare types, NULL arrives as <code>\\N</code>, a Hive 4 setting silently <b>removed our SORT BY</b> and gave wrong answers, crashes show up as a vague “Error 20001”, Windows line endings break scripts, and the script was <b>6× slower</b> than plain SQL. All outputs are real, from Hive 4.2.1; the scripts are in the course lab folder.
  </div>
</section>
'''

lv = '''
LEVELS> TRANSFORM at three levels
L1> Passing notes through a window
      <ul>
        <li>Hive writes each row on a slip of paper (one text line) and passes it to your program.</li>
        <li>Your program reads the slip, writes an answer slip, and passes it back.</li>
        <li>Hive turns the answer slips back into a table. Any language that reads and prints lines works.</li>
      </ul>
L2> The rules of the stream
      <ul>
        <li>Columns are joined with <b>tabs</b>, rows end with a newline; NULL is written as <code>\\N</code>.</li>
        <li><code>AS (a, b)</code> gives string columns; <code>AS (a INT, b DECIMAL(10,2))</code> casts them.</li>
        <li><code>ADD FILE</code> ships the script to every task; it runs in the task’s working directory.</li>
        <li>For “reducer” scripts, rows must arrive grouped and sorted: <code>DISTRIBUTE BY</code> key <code>SORT BY</code> key, order in a subquery.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>Hive 4.2.1 removed the subquery’s <code>SORT BY</code> (<code>hive.remove.orderby.in.subquery=true</code>): the plan changed from <code>SHUFFLE</code> to <code>PARTITION_ONLY_SHUFFLE</code> and the script returned 63 wrong rows instead of 3.</li>
        <li>A Python exception surfaced in Beeline only as <code>[Error 20001]</code>; the traceback was in the task log. A CRLF script gave <code>[Error 20003]</code> and <code>env: ‘python3\\r’</code>.</li>
        <li>On 5,000,000 rows: TRANSFORM about 9.4 s vs SQL CASE about 1.5 s, identical results. Plans with scripts are “not optimized by CBO”.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>TRANSFORM and custom scripts</h2>
''' + def_block(
    '<code>SELECT TRANSFORM (expr, …) USING \'command\' [AS (col [type], …)]</code> streams the selected rows through an external program. Hive serialises each row as a line of tab-separated text (NULL as <code>\\N</code>) to the program’s standard input and deserialises each line of its standard output into a row, by default as STRING columns. The program, shipped to tasks with <code>ADD FILE</code> (or <code>ADD ARCHIVE</code>), runs once per task; placing TRANSFORM over a subquery with <code>DISTRIBUTE BY</code> and <code>SORT BY</code> makes it act as a reducer over grouped, ordered rows. The older keywords <code>MAP</code> and <code>REDUCE</code> are aliases for TRANSFORM.',
    'TRANSFORM lets a Hive query send its rows, as lines of text, to a script in Python or any other language, and read the script’s printed lines back as a table.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('TRANSFORM', 'Stream rows through an external command.'),
    ('ADD FILE', 'Ship a script or file to every task.'),
    ('stdin / stdout', 'Where the script reads rows and prints results.'),
    ('\\N', 'How NULL is written in the stream.'),
    ('Mapper script', 'Row-by-row script: no grouping needed.'),
    ('Reducer script', 'Needs rows grouped and sorted by key.'),
    ('DISTRIBUTE BY / SORT BY', 'Route rows by key and sort them in each reducer.'),
    ('stderr', 'Where errors and debug output go: the task log.'),
]) + '''

  <h3>TRANSFORM vs Java UDF vs SQL</h3>
''' + table(['', 'SQL / built-ins', 'Java UDF (9.1)', 'TRANSFORM script'], [
    ['Language', 'HiveQL', 'Java / JVM', 'Any (Python, R, shell …)'],
    ['Speed (lab, 5M rows)', '≈ 1.5 s', 'close to built-ins (≈ 15% slower in 9.1)', '≈ 9.4 s'],
    ['Types', 'Native', 'Native', 'Text; cast with AS (… type)'],
    ['Optimiser', 'Full CBO', 'Full CBO', '“Plan not optimized by CBO”'],
    ['Deployment', 'None', 'JAR + CREATE FUNCTION', 'ADD FILE + interpreter on every node'],
    ['Security', 'Normal', 'Normal', 'Disabled under SQL-standard authorization'],
], minw=720) + lv + '''
EXAM> “How do you use a Python script in Hive?” ADD FILE the script, then SELECT TRANSFORM (cols) USING 'python3 script.py' AS (out_cols). Hive writes rows as tab-separated lines to stdin and reads stdout back; NULL is \\N; outputs are strings unless typed. For reducer-style scripts use DISTRIBUTE BY / SORT BY in a subquery. Debug with the task’s stderr log.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Two shapes of scripts</h2>
''' + table(['Shape', 'Query pattern', 'Script assumes', 'Lab example'], [
    ['Mapper', '<code>SELECT TRANSFORM (…) USING … FROM t</code>', 'Nothing about order; one line in, zero or more lines out', '<code>slot.py</code>: meal slot and GST'],
    ['Reducer', '<code>FROM (SELECT … DISTRIBUTE BY k SORT BY k, ts) s SELECT TRANSFORM (…) USING …</code>', 'All rows of a key are contiguous and sorted', '<code>gaps.py</code>: hours between orders'],
    ['Map + reduce', 'Mapper subquery inside a reducer query', 'Both of the above', 'Classic Hadoop Streaming jobs'],
], minw=740) + '''
WARN> In Hive 4, <code>hive.remove.orderby.in.subquery</code> is <b>true</b>: ORDER BY / SORT BY inside a subquery may be dropped as “useless”. Reducer scripts then see unsorted, interleaved rows and produce wrong results without any error. Set it to false for such queries, and check the plan for <code>SHUFFLE</code> rather than <code>PARTITION_ONLY_SHUFFLE</code>.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>A Python mapper, a Python reducer, and their traps</h2>
  <p>All outputs are real, from Hive 4.2.1 (Python 3.9 in the HiveServer2 container, where Tez runs its tasks in our lab).</p>
''' + stepper([
    ('Step 1 · The mapper script',
     code('python', 'slot.py', script('slot.py')),
     'A plain Python program: read lines from <code>sys.stdin</code>, split on tabs, print tab-separated results. It must handle <code>\\N</code> (Hive’s NULL) itself, and it never imports anything Hive-specific, so you can test it from a shell with <code>printf \'1\\t2026-10-05 20:10:00\\t530.00\\n\' | python3 slot.py</code>.'),
    ('Step 2 · Run it from Hive',
     code('sql', 'Beeline', "ADD FILE /data/scripts/slot.py;\nSELECT TRANSFORM (order_id, order_ts, amount)\n       USING 'python3 slot.py'\n       AS (order_id, slot, gst)\nFROM orders WHERE order_id <= 100005;", capf('l93_slot.txt')),
     '<code>ADD FILE</code> copies the script into each task’s working directory, so <code>USING</code> refers to it by its bare name. Each output line became one row with the three names given in <code>AS</code>.'),
    ('Step 3 · Everything is a string, unless you say otherwise',
     code('sql', 'Beeline', "CREATE TEMPORARY TABLE t1 AS SELECT TRANSFORM (order_id, order_ts, amount)\n  USING 'python3 slot.py' AS (order_id, slot, gst) FROM orders WHERE order_id <= 100002;\nDESCRIBE t1;\nCREATE TEMPORARY TABLE t2 AS SELECT TRANSFORM (order_id, order_ts, amount)\n  USING 'python3 slot.py' AS (order_id INT, slot STRING, gst DECIMAL(10,2)) FROM orders WHERE order_id <= 100002;\nDESCRIBE t2;", capf('l93_types.txt')),
     'Without types, <code>order_id</code> and <code>gst</code> are <b>strings</b>: sorting and arithmetic would behave like text (“9.00” &gt; “26.50”). Typed <code>AS</code> lets Hive convert them; a value that cannot be converted becomes NULL silently (Lesson 8.5).'),
    ('Step 4 · A reducer script needs grouped, sorted input',
     code('python', 'gaps.py', script('gaps.py')),
     'This script assumes that all orders of one customer arrive <b>together</b> and <b>in time order</b>: it keeps the current customer and flushes when the key changes. That is exactly what <code>DISTRIBUTE BY customer_id SORT BY customer_id, order_ts</code> should guarantee.'),
    ('Step 5 · The Hive 4 trap: the SORT BY disappeared',
     code('sql', 'Beeline', "ADD FILE /data/scripts/gaps.py;\nFROM (SELECT customer_id, order_ts FROM orders WHERE customer_id IN (7, 15, 1492)\n      DISTRIBUTE BY customer_id SORT BY customer_id, order_ts) t\nSELECT TRANSFORM (customer_id, order_ts) USING 'python3 gaps.py'\n       AS (customer_id INT, orders INT, avg_gap_hours DOUBLE);\n-- first rows of 63", capf('l93_gaps_wrong_head.txt') + '\n…\n\n-- EXPLAIN: the shuffle into the script\n' + pick('l93_plan_true.txt', ('Plan not optimized', '<-Map 1', 'SHUFFLE', 'command'))),
     'Three customers should give three rows. We got <b>63</b>, with negative gaps. The plan shows why: <code>PARTITION_ONLY_SHUFFLE</code> routes rows by customer but <b>does not sort</b>. Hive 4’s default <code>hive.remove.orderby.in.subquery=true</code> treated the subquery’s SORT BY as unnecessary. No error, no warning. Note also “Plan not optimized by CBO because the statement uses scripts”.'),
    ('Step 6 · Fix it, and check against SQL',
     code('sql', 'Beeline', "SET hive.remove.orderby.in.subquery=false;\n-- same query as Step 5\n\n-- cross-check in plain SQL:\nSELECT customer_id, COUNT(*) AS orders,\n  ROUND((unix_timestamp(MAX(order_ts)) - unix_timestamp(MIN(order_ts))) / 3600 / (COUNT(*) - 1), 1) AS avg_gap_hours\nFROM orders WHERE customer_id IN (7, 15, 1492) GROUP BY customer_id ORDER BY customer_id;", capf('l93_gaps.txt') + '\n\n' + pick('l93_plan_false.txt', ('<-Map 1', 'SHUFFLE')) + '\n\n' + capf('l93_check.txt')),
     'With the setting off, the plan shows a real <code>SHUFFLE</code> (sorted) and the script returns <b>3 rows</b>: 29, 27 and 41 orders with average gaps of 25.2, 24.3 and 17.3 hours, exactly what plain SQL computes (the average gap is (last − first) / (n − 1)). Always validate a script against a SQL calculation on a sample.'),
    ('Step 7 · When the script fails',
     code('sql', 'Beeline', "ADD FILE /data/scripts/fragile.py;      -- raises ValueError when amount > 850\nSELECT TRANSFORM (order_id, amount) USING 'python3 fragile.py' AS (order_id, amount) FROM orders;\n\nSELECT TRANSFORM (order_id) USING 'python4 slot.py' AS (x) FROM orders LIMIT 1;   -- no such interpreter\n\nADD FILE /data/scripts/slot_crlf.py;    -- saved with Windows line endings\nSELECT TRANSFORM (…) USING 'slot_crlf.py' AS (…) FROM orders …;", '-- Beeline\n' + capf('l93_fragile_beeline.txt') + '\n\n-- task log (HiveServer2 log in our local-mode lab)\n' + capf('l93_fragile_log.txt') + '\n\n' + capf('l93_nopython_clean.txt') + '\n\n' + capf('l93_crlf_clean.txt')),
     'Beeline only says <b>Error 20001</b> (“may have crashed with an error”). The real reason, the Python <b>traceback</b>, goes to the task’s stderr: order 112253 had amount 880.00. A missing interpreter gives <b>Error 20000</b> and “Cannot run program”. A script with Windows (CRLF) line endings, run through its shebang, fails with <b>Error 20003</b>; the log shows <code>env: ‘python3\\r’</code>. Convert with <code>dos2unix</code> or call <code>python3 script.py</code> explicitly.'),
    ('Step 8 · The cost of streaming',
     code('sql', 'Beeline', "-- 5,000,000 rows (orders_ts_big), results cache off, two runs each\nSELECT slot, COUNT(*) AS n FROM (\n  SELECT TRANSFORM (order_id, order_ts, amount) USING 'python3 slot.py' AS (order_id, slot, gst)\n  FROM orders_ts_big) t GROUP BY slot ORDER BY slot;\n\nSELECT slot, COUNT(*) AS n FROM (\n  SELECT CASE WHEN hour(order_ts) BETWEEN 6 AND 10 THEN 'breakfast' … ELSE 'late-night' END AS slot\n  FROM orders_ts_big) t GROUP BY slot ORDER BY slot;", capf('l93_bigt_result.txt') + '\n\n' + capf('l93_speed.txt')),
     'Identical results (we compared them), but TRANSFORM took about <b>9.4 s</b> against <b>1.5 s</b> for the SQL CASE: every row was turned into text, piped to Python, parsed, printed and parsed back, and none of it was vectorised. Use TRANSFORM for logic that only exists in Python (a library, a model), not for what SQL already does.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([("> SELECT TRANSFORM (order_id, order_ts, amount)", W), ("    USING 'python3 slot.py' AS (order_id, slot, gst)", W), ('100001  dinner     26.50', G), ('100003  breakfast  20.50', G), ('t1: order_id string, gst string', Y)], size=7.2),
    term([('-- SORT BY removed (default)', W), ('PARTITION_ONLY_SHUFFLE [RS_11]', RD), ('15   2   -219.4', RD), ('7    1   NULL', RD), ('… 63 rows instead of 3', RD)], size=7.4),
    term([('SET hive.remove.orderby.in.subquery=false;', W), ('SHUFFLE [RS_11]', G), ('7     29   25.2', G), ('15    27   24.3', G), ('1492  41   17.3   = SQL check', G)], size=7.2),
    term([('[Error 20001]: … custom script.', RD), ('  It may have crashed with an error.', RD), ('task log: Traceback …', Y), ('ValueError: amount too large', Y), ('  for order 112253: 880.00', Y)], size=7.2),
    term([('TRANSFORM  9.405 s', RD), ('SQL CASE   1.605 s', G), ('TRANSFORM  9.349 s', RD), ('SQL CASE   1.429 s', G), ('same 5 slots, same counts', W)], size=7.6),
]
def pipe(hi):
    o = opbox(16, 56, 'Hive operator', 'row → text', 'blue', 96) + arrow(114, 69, 140, 69, 'acc', 1.6) + opbox(142, 56, 'script', 'stdin → stdout', 'violet' if hi != 1 else 'acc', 90) + arrow(234, 69, 260, 69, 'acc', 1.6) + opbox(262, 56, 'Hive operator', 'text → row', 'green', 90)
    o += t(187, 104, 'stderr → task log', 7.4, 'red' if hi == 3 else 'ink2', mono=True)
    return o
B1 = [
    t(180, 22, 'Rows become lines of text', 9.4, bold=True) + pipe(0) + cap('Tab-separated; NULL is \\N; output is text.', '', 'blue', y=150, h=34),
    t(180, 22, 'Reducer scripts need sorted groups', 9.4, bold=True) + ''.join(box(30 + k * 26, 60, 22, 18, ['blue', 'amber', 'blue', 'green', 'amber', 'green', 'blue', 'amber', 'green', 'blue', 'green'][k]) for k in range(11)) + cap('Unsorted: one key arrives in pieces.', '', 'amber', y=150, h=34),
    t(180, 22, 'Sorted: each key arrives once, in order', 9.4, bold=True) + ''.join(box(30 + k * 26, 60, 22, 18, (['blue'] * 4 + ['amber'] * 3 + ['green'] * 4)[k]) for k in range(11)) + cap('SHUFFLE sorts; PARTITION_ONLY_SHUFFLE does not.', '', 'green', y=150, h=34),
    t(180, 22, 'Errors go to stderr, not to Beeline', 9.4, bold=True) + pipe(3) + cap('Read the task log for the traceback.', '', 'amber', y=150, h=34),
    t(180, 22, 'Serialise, pipe, parse: per row', 9.4, bold=True) + fill(40, 56, 260, 12, 'acc', rx=2) + t(40, 82, 'TRANSFORM ≈ 9.4 s', 7.6, 'ink2', anchor='start', mono=True) + fill(40, 92, 42, 12, 'green', rx=2) + t(40, 118, 'SQL ≈ 1.5 s', 7.6, 'ink2', anchor='start', mono=True) + cap('No vectorisation, no CBO inside the script.', '', 'amber', y=150, h=34),
]
see_caps = ['slot.py labelled each order; untyped outputs were strings.',
            'With the default setting, the reducer script returned 63 wrong rows.',
            'With SORT BY kept, it returned 3 rows that match SQL.',
            'Beeline showed Error 20001; the traceback was in the task log.',
            'TRANSFORM was about 6× slower than the SQL CASE.']
behind_caps = ['Hive serialises each row, the script prints lines, Hive parses them back.',
               'Rows of one customer arrived interleaved and unsorted.',
               'Sorted input lets the script process one key at a time.',
               'The script’s stderr is captured in the task’s log.',
               'Every row crosses a process boundary twice.']
two = anim_two('TRANSFORM', 'Streaming rows through Python', 'Real lab outputs', 'What happens in the task', see, B1, see_caps, behind_caps)

# ---- scenario 1: model scoring
m1 = (t(180, 22, 'Score orders with a Python model', 9.4, bold=True) + t(180, 56, 'fraud model trained with scikit-learn', 8.4, 'ink2') + cap('Logic exists only in Python.', '', 'blue', y=150, h=34))
m2 = (t(180, 22, 'Ship script and model', 9.4, bold=True) + t(180, 52, 'ADD FILE score.py;', 8, 'ink', mono=True) + t(180, 70, 'ADD ARCHIVE model.tar.gz;', 8, 'ink', mono=True) + cap('Every node also needs the Python packages.', '', 'amber', y=150, h=34))
m3 = (t(180, 22, 'Load the model once per task', 9.4, bold=True) + t(180, 56, 'outside the for-line loop', 8.4, 'ink2') + cap('Not once per row.', '', 'green', y=150, h=34))
m4 = (t(180, 22, 'Write typed, tested output', 9.4, bold=True) + t(180, 56, 'AS (order_id INT, fraud_score DOUBLE)', 8, 'ink', mono=True) + cap('Validate on a sample against Python alone.', '', 'green', y=150, h=34))
m5 = (t(180, 22, 'At scale: use Spark instead', 9.4, 'acc', bold=True) + t(180, 56, 'pandas UDFs, vectorised, same tables', 8.2, 'ink2') + cap('Many teams move scoring to Spark.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Scoring a Python model inside Hive',
              'A common reason for TRANSFORM. (Typical setup; costs as measured in Step 8.)',
              'Model scoring', 'Ship the script and model with ADD FILE/ARCHIVE, load the model once per task, type the outputs, or move scoring to Spark', [m1, m2, m3, m4, m5],
              ['The model is written in Python.',
               'Ship script, model and packages.',
               'Load once per task.',
               'Type and validate outputs.',
               'For large volumes, Spark is usually better.'],
              hid='scenario-model')

# ---- scenario 2: wrong results from a reducer script
w1 = (t(180, 22, 'Session report changed after the Hive 4 upgrade', 9.4, bold=True) + t(180, 56, 'no errors, numbers just different', 8.4, 'ink2') + cap('A silent correctness bug.', '', 'amber', y=150, h=34))
w2 = (t(180, 22, 'EXPLAIN the old and new plans', 9.4, bold=True) + t(180, 56, 'SHUFFLE → PARTITION_ONLY_SHUFFLE', 8.4, 'red', mono=True) + cap('The subquery sort was removed.', '', 'amber', y=150, h=34))
w3 = (t(180, 22, 'The setting', 9.4, bold=True) + t(180, 56, 'hive.remove.orderby.in.subquery = true', 8.2, 'ink', mono=True) + cap('Our lab: 63 rows instead of 3.', '', 'amber', y=150, h=34))
w4 = (t(180, 22, 'Fix and guard', 9.4, bold=True) + t(180, 56, 'set it to false for script jobs', 8.4, 'ink2') + cap('Add a SQL cross-check to the job.', '', 'green', y=150, h=34))
w5 = (t(180, 22, 'Better: make the script order-proof', 9.4, 'acc', bold=True) + t(180, 56, 'or replace it with window functions', 8.2, 'ink2') + cap('LAG() over (PARTITION BY … ORDER BY …).', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Numbers changed after an upgrade',
              'How a reducer script silently broke. (Upgrade story typical; the behaviour is from our lab.)',
              'Silent script bug', 'Hive 4 removed a subquery SORT BY; the reducer script saw unsorted rows; disabling the removal or using window functions fixes it', [w1, w2, w3, w4, w5],
              ['Results changed without errors.',
               'The plan lost its sort.',
               'A Hive 4 default caused it.',
               'Turn it off and add checks.',
               'Or avoid order-dependent scripts.'],
              hid='scenario-upgrade')

# ---- scenario 3: governance
g1 = (t(180, 22, 'Security review of TRANSFORM', 9.4, bold=True) + t(180, 56, 'scripts run arbitrary programs on cluster nodes', 8, 'red') + cap('Powerful, and risky on shared clusters.', '', 'amber', y=150, h=34))
g2 = (t(180, 22, 'SQL-standard authorization', 9.4, bold=True) + t(180, 56, 'TRANSFORM is not allowed when it is on', 8.2, 'ink2') + cap('Many secured clusters disable scripts.', '', 'blue', y=150, h=34))
g3 = (t(180, 22, 'Where scripts are allowed', 9.4, bold=True) + t(180, 56, 'dedicated ETL queues, reviewed scripts', 8.2, 'ink2') + cap('Versioned in a repository.', '', 'green', y=150, h=34))
g4 = (t(180, 22, 'Same interpreter everywhere', 9.4, bold=True) + t(180, 56, 'python3 version and packages on every node', 8, 'ink2') + cap('Or ship a virtualenv with ADD ARCHIVE.', '', 'green', y=150, h=34))
g5 = (t(180, 22, 'Plan the exit', 9.4, 'acc', bold=True) + t(180, 56, 'built-ins → Java UDF → Spark Python UDF', 8.2, 'ink2') + cap('TRANSFORM as a bridge, not a platform.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Should we allow TRANSFORM at all?',
              'A platform decision about scripts. (Typical policies.)',
              'Script governance', 'TRANSFORM runs arbitrary programs, is disabled under SQL-standard authorization, and needs consistent interpreters; many platforms restrict it', [g1, g2, g3, g4, g5],
              ['Scripts run any program on nodes.',
               'SQL-standard authorization blocks TRANSFORM.',
               'Allow it only where reviewed.',
               'Keep interpreters consistent.',
               'Plan to move logic to better tools.'],
              hid='scenario-governance')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Rows through a pipe</h2>
  <p>Left: real outputs. Right: what happens inside the task.</p>
''' + two + '''
  <p>Three live scenarios follow: scoring a Python model, a silent upgrade bug, and governance.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>TRANSFORM at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'legacy', 11, 'green', bold=True) + t(60, 58, 'streaming jobs', 7.4, 'ink2'),
    '1. Migrating Hadoop Streaming jobs',
    'Old Python or Perl MapReduce streaming jobs can run almost unchanged as TRANSFORM queries during a migration.',
    ['Streaming job', '*TRANSFORM', 'Hive SQL']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'parse', 11, 'blue', bold=True) + t(60, 58, 'odd formats', 7.4, 'ink2'),
    '2. Parsing unusual formats',
    'Lines from proprietary logs are parsed with a Python library that has no Hive equivalent.',
    ['Raw lines', '*python parser', 'Columns']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'score', 11, 'violet', bold=True) + t(60, 58, 'models', 7.4, 'ink2'),
    '3. Batch model scoring',
    'Small and medium batch scoring runs a Python model over Hive rows without moving data out.',
    ['Rows', '*model.py', 'Scores']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'proto', 11, 'acc', bold=True) + t(60, 58, 'prototypes', 7.4, 'ink2'),
    '4. Prototyping logic',
    'Analysts test a rule in Python on real data, then the platform team turns the proven rule into SQL or a Java UDF.',
    ['Idea', '*script', 'UDF / SQL']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'shell', 11, 'acc', bold=True) + t(60, 58, 'tools', 7.4, 'ink2'),
    '5. Calling command-line tools',
    'Any executable works with TRANSFORM: a geocoder, a checksum tool or a text normaliser installed on the nodes.',
    ['Rows', '*CLI tool', 'Results']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> DISTRIBUTE BY and SORT BY (<a href="../../03-querying/04-order-sort-distribute-cluster-by/">3.4</a>), Java UDFs (<a href="../01-user-defined-functions/">9.1</a>) and reading failures (<a href="../../08-optimisation/05-troubleshooting-slow-queries/">8.5</a>). Basic Python helps.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
