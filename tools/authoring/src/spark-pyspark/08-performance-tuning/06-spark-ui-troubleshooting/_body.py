import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l86_ui.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)

def fig(src, w, h, alt, caption):
    return f'''  <figure style="margin:18px 0">
    <img src="{src}" width="{w}" height="{h}" loading="lazy" alt="{alt}" style="max-width:100%;height:auto;border:1px solid var(--line);border-radius:8px">
    <figcaption class="muted" style="font-size:.9em;margin-top:6px">{caption}</figcaption>
  </figure>
'''

def tabs(hi):
    names = ['Jobs', 'Stages', 'Storage', 'Env', 'Executors', 'SQL']
    return ''.join(box(14 + k * 56, 30, 52, 20, 'acc' if n == hi else 'card', rx=3) + t(40 + k * 56, 43, n, 6.8, 'ink', bold=n == hi) for k, n in enumerate(names))

# ---------------------------------------------------------------- story
sc_ = (tabs('Stages') + box(14, 60, 332, 84, 'card') + t(24, 76, 'Summary Metrics for 4 Completed Tasks', 7.4, 'ink', anchor='start', bold=True) +
       ''.join(t(24 + c * 80, 94 + r * 14, v, 6.8, ('red' if (r, c) in ((0, 3), (1, 3)) else 'ink2'), anchor='start', mono=True)
               for r, row in enumerate([['Duration', '0.5 s', '2 s', '5 s'], ['Records', '571.5K', '636K', '4.2M'], ['Spill', '0', '0', '104 MiB']])
               for c, v in enumerate(row)) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Read the UI in order', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('1 SQL: slowest query', 'blue'), ('2 Jobs: slowest job', 'blue'),
           ('3 Stages: slowest stage', 'blue'), ('4 Task summary: max≫median', 'red'),
           ('5 Spill / GC / shuffle', 'amber'), ('6 Executors: failures', 'amber')])))
scene_svg = scene('The Spark UI shows every query, job, stage and task with metrics. We ran a skewed window and a sort that spills, then read the SQL tab, the stage pages and the task summary metrics to find the cause of each slowdown.', sc_,
                  'The answer is usually in the <tspan font-weight="700" class="s-acc">task summary</tspan> of the slowest stage.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“The job is slow. Why?”</h2>
  <div class="story">
    <p class="narration">The TiffinGo on-call channel gets the same message every week: “the job is slow today”. Some engineers restart it, some double the memory. The senior engineer opens the Spark UI and has an answer in two minutes.</p>

{scene_svg}

K> Sir, the UI has so many tabs and numbers. Where do I even start?
A> Always the same path: find the slowest <b>query</b>, then its slowest <b>stage</b>, then compare the slowest <b>task</b> with the median. The pattern of the numbers tells you the problem: skew, spill, too many tasks, a slow input, a failing executor.
R> Can we see it on a real job?
A> We will run a skewed window and a spilling sort, and read real screenshots of the SQL tab, the plan graph and two stage pages. This lesson ties together everything in Module 8. All outputs are real (Spark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> The Spark UI at three levels
L1> A hospital chart
      <ul>
        <li>The doctor does not read every line. First the vital signs that are off (slowest stage), then the detailed tests for that organ (task metrics).</li>
        <li>A fever pattern points to a cause: one hot task means skew, spill means not enough memory per task, thousands of tiny tasks mean too many partitions.</li>
      </ul>
L2> Where things are
      <ul>
        <li>Driver UI on port 4040 while the app runs; the <b>History Server</b> (18080) for finished apps with <code>spark.eventLog.enabled=true</code>.</li>
        <li>Tabs: Jobs, Stages, Storage, Environment, Executors, SQL / DataFrame (plan graph with metrics), Structured Streaming.</li>
        <li>Same data via REST: <code>/api/v1/applications/&lt;app&gt;/stages/&lt;id&gt;/&lt;attempt&gt;/taskSummary</code>.</li>
      </ul>
L3> What our screenshots showed
      <ul>
        <li>Window stage: median task 2 s, max 5 s; one task read 4.2M of 6M records and spilled 104 MiB.</li>
        <li>Sort stage: even tasks (1.2–1.6 s), every task spilled 184 MiB: memory, not skew.</li>
        <li>SQL plan graph: the Sort node took 8.0 s of task time, Exchange moved 6,000,000 rows.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>The Spark UI for troubleshooting</h2>
''' + def_block(
    'The <b>Spark web UI</b> is served by the driver (port 4040 by default) and shows the application’s jobs, stages, tasks, storage, environment, executors and SQL executions. A <b>job</b> is triggered by an action, split into <b>stages</b> at shuffle boundaries, each made of <b>tasks</b> (one per partition). The stage page shows <b>summary metrics</b> (min, 25th percentile, median, 75th percentile, max) for duration, GC time, input, shuffle read/write and spill, and a per-task table. The <b>SQL / DataFrame</b> tab shows the physical plan as a graph with per-operator metrics (rows, time, sizes). After an application ends, the same pages are available in the <b>Spark History Server</b> from event logs. Troubleshooting means locating the slowest stage and interpreting its metric distribution.',
    'The Spark UI shows every job, stage and task with timings and sizes. To find why a job is slow, open the slowest query, then the slowest stage, then compare the slowest task with the typical task. The pattern tells you whether it is skew, spill, too many small tasks or something else.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Job', 'Work triggered by one action.'),
    ('Stage', 'Tasks between shuffle boundaries.'),
    ('Task summary', 'Min/25%/median/75%/max metrics.'),
    ('Shuffle read', 'Data a task fetched from a shuffle.'),
    ('Spill', 'Data written to disk (8.4).'),
    ('GC time', 'JVM garbage-collection time.'),
    ('SQL tab', 'Plan graph with operator metrics.'),
    ('History Server', 'UI for finished apps (event logs).'),
]) + '''

  <h3>Symptom → cause</h3>
''' + table(['What you see', 'Likely cause', 'Lesson'], [
    ['Max task ≫ median, one task reads most records', 'Data skew', '8.3'],
    ['All tasks spill, durations even', 'Tasks too big for memory', '8.4'],
    ['Thousands of tasks of a few ms', 'Too many partitions / small files', '8.1'],
    ['Two big Exchanges before a join', 'Sort-merge where broadcast would do', '8.2'],
    ['High GC time (> 10%)', 'Memory pressure, too many objects', '8.4'],
    ['Failed tasks, lost executors', 'OOM, container kills, bad nodes', '8.4 / 8.5'],
    ['Long gaps with no running tasks', 'Driver work, waiting for executors', '8.5'],
], minw=620) + lv + '''
EXAM> “How do you troubleshoot a slow Spark job?” Open the Spark UI (or History Server), find the longest SQL query/job, then the longest stage. In its task summary compare max vs median duration and shuffle read (skew), check spill and GC time (memory), number and size of tasks (partitioning), input size (small files, no pruning), and the plan in the SQL tab (join strategy, Exchanges). Fix the specific cause, re-run, and compare the same metrics.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Which tab answers which question</h2>
''' + table(['Tab', 'Question it answers', 'Look at'], [
    ['SQL / DataFrame', 'Which query is slow, what plan ran?', 'Duration, plan graph, rows per node, Exchanges'],
    ['Jobs', 'Which action is slow?', 'Duration, stages, failed stages'],
    ['Stages', 'Where is the time inside a job?', 'Summary metrics, task table, event timeline'],
    ['Storage', 'What is cached, how much?', 'Size in memory/disk, fraction cached'],
    ['Executors', 'Are executors healthy?', 'Failed tasks, GC time, shuffle, dead executors'],
    ['Environment', 'Which settings were used?', 'Spark properties actually in effect'],
], minw=620) + '''
WARN> The live UI disappears when the application ends, and its job/stage history is capped (<code>spark.ui.retainedJobs</code>, <code>retainedStages</code>). For production, enable event logs (<code>spark.eventLog.enabled=true</code>, <code>spark.eventLog.dir</code>) and run a <b>History Server</b>, or you will be debugging yesterday’s failure from logs alone. Use <code>sc.setJobDescription()</code> so jobs show readable names instead of “save at …”.
</section>
'''

FIG1 = fig('ui-sql-tab.webp', 1280, 500, 'Spark UI SQL / DataFrame tab listing two completed queries: wide sort that spills (7 s) and skewed window by rest_id (9 s)', 'Real screenshot: the SQL / DataFrame tab. Job descriptions set with <code>setJobDescription</code> make the two queries easy to find.')
FIG2 = fig('ui-sql-plan.webp', 1280, 1230, 'Spark UI plan graph for the skewed window query: Scan parquet 6,000,000 rows, ColumnarToRow 3.5 s, Exchange, Sort 8.0 s, Window, noop write', 'Real screenshot: the plan graph of query 0. Edges show rows (6,000,000), boxes show total task time per code-generated stage (3.5 s scan, 8.0 s sort).')
FIG3 = fig('ui-stage-skew.webp', 1280, 1000, 'Spark UI stage 2 details: summary metrics with median duration 2 s and max 5 s, shuffle read records median 636000 and max 4197000, one task spilled 104 MiB', 'Real screenshot: the window stage. Median 2 s, max 5 s; the max task read 4,197,000 of 6,000,000 records and was the only one to spill (104 MiB). Skew.')
FIG4 = fig('ui-stage-spill.webp', 1280, 1000, 'Spark UI stage 6 details for the sort: four tasks with similar durations, each spilling about 184 MiB', 'Real screenshot: the sort stage. Durations are even (1.2–1.6 s) but every task spilled ~184 MiB. Not skew: tasks too big for 1 GB of memory.')

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Reading a real UI</h2>
  <p>All screenshots and numbers are real: Spark 4.3.0, <code>local[2]</code> with a 1 GB driver, AQE off, 4 shuffle partitions. Query 0: a window over restaurants where one has 60% of 6M orders (Lesson 8.3). Query 1: a sort of 5M wide rows (Lesson 8.4). The UI was kept alive and captured with a headless browser.</p>
''' + stepper([
    ('Step 1 · Name your jobs, find the slow query',
     code('python', 'l86_ui.py', 'sc = spark.sparkContext\nsc.setJobDescription("skewed window by rest_id")\nskewed_window.write.format("noop").mode("overwrite").save()\nsc.setJobDescription("wide sort that spills")\nwide_sort.write.format("noop").mode("overwrite").save()', sec('app:', '== Stage 2')) + FIG1,
     'Start at the <b>SQL / DataFrame</b> tab: one row per query, with duration and the jobs it ran. With descriptions set, “skewed window by rest_id” (9 s) is obvious; without them you would see two rows called “save at …”.'),
    ('Step 2 · Read the plan graph',
     code('text', 'Spark UI', 'SQL / DataFrame → query 0 → Plan Visualization', 'Scan parquet      6,000,000 rows\nColumnarToRow     (1) 3.5 s\nExchange          6,000,000 rows\nSort              (2) 8.0 s\nWindow\nOverwriteByExpression noop-table') + FIG2,
     'The graph shows the physical plan with metrics. The <b>Exchange</b> means a shuffle of all 6 million rows by <code>rest_id</code>. The blue boxes are whole-stage-codegen blocks with total task time: <b>8.0 s</b> in the Sort block (stage 2) vs 3.5 s for scanning. So the time is after the shuffle. Next: that stage.'),
    ('Step 3 · The skewed stage',
     code('text', 'Spark UI', 'Stages → stage 2 → Summary Metrics', sec('== Stage 2', '== Stage 6')) + FIG3,
     'Read the summary table across: duration min 0.5 s, median 2 s, <b>max 5 s</b>; shuffle read median 636,000 records, <b>max 4,197,000</b>. One task got 70% of the data, and only that task spilled (104 MiB). This is the skew signature: fix with the techniques from Lesson 8.3, not with more memory.'),
    ('Step 4 · The spilling stage',
     code('text', 'Spark UI', 'Stages → stage 6 → Summary Metrics', sec('== Stage 6')) + FIG4,
     'A different pattern: durations and records are even across the 4 tasks (1.2–1.6 s, 1.14M–1.36M records), but <b>every</b> task spilled about 184 MiB. No skew; each task is simply too big for the 1 GB heap. The fix from Lesson 8.4: more partitions (64 removed all spill) or more memory per task.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('query 0 skewed window   9 s', Y), ('query 1 wide sort       7 s', W)], size=7.6),
    term([('Exchange: 6,000,000 rows', W), ('Sort block: 8.0 s', RD), ('Scan block: 3.5 s', W)], size=7.6),
    term([('duration  0.5 | 2 | 5 s', Y), ('records   571K | 636K | 4.2M', RD), ('spill     0 | 0 | 104 MiB', Y)], size=7.4),
    term([('duration  1.2 | 1.6 | 1.6 s', G), ('records   1.14M .. 1.36M', G), ('spill     184 MiB every task', RD)], size=7.4),
]
B1 = [
    t(180, 14, 'Top-down: query first', 9.4, bold=True) + tabs('SQL') + flow([('query', 'slowest', 'blue'), ('job', '', 'blue'), ('stage', 'slowest', 'violet'), ('task', 'max vs med', 'acc')], y=70, w=72, gap=14) + cap('Narrow down, do not scan everything.', '', 'blue', y=144, h=30),
    t(180, 14, 'Where is the time?', 9.4, bold=True) + flow([('Scan', '3.5 s', 'card'), ('Exchange', '6M rows', 'amber'), ('Sort', '8.0 s', 'acc'), ('Window', '', 'card')], y=50, w=72, gap=14) + cap('After the shuffle → reduce stage.', '', 'amber', y=144, h=30),
    t(180, 14, 'Skew pattern', 9.4, bold=True) + ''.join(box(60 + k * 30, 120 - h, 22, h, 'acc' if h > 50 else 'green', rx=2) for k, h in enumerate([12, 13, 14, 70])) + t(260, 80, 'max ≫ median', 8, 'red', bold=True) + cap('One task holds the hot key.', '', 'red', y=144, h=30),
    t(180, 14, 'Spill pattern', 9.4, bold=True) + ''.join(box(60 + k * 30, 120 - h, 22, h, 'amber', rx=2) for k, h in enumerate([40, 46, 46, 46])) + t(260, 80, 'all even, all spill', 8, 'amber', bold=True) + cap('Tasks too big for memory.', '', 'amber', y=144, h=30),
]
see_caps = ['SQL tab.', 'Plan graph.', 'Skewed stage.', 'Spilling stage.']
behind_caps = ['The troubleshooting path.', 'Operator time.', 'Skew signature.', 'Memory signature.']
two = anim_two('Spark UI troubleshooting', 'Reading the numbers', 'Real UI metrics', 'What they mean', see, B1, see_caps, behind_caps)

e1 = (t(180, 22, '“Job slow today”', 9.4, bold=True) + t(180, 56, 'usually 20 min, now 2 h', 8.4, 'ink2') + cap('Open the History Server.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Slowest stage: a join', 9.4, bold=True) + t(180, 56, 'max task 95 min, median 40 s', 8.4, 'ink2') + cap('Skew.', '', 'red', y=150, h=34))
e3 = (t(180, 22, 'Which key?', 9.4, bold=True) + t(180, 56, 'new big restaurant chain', 8.4, 'ink2') + cap('groupBy(key).count().', '', 'amber', y=150, h=34))
e4 = (t(180, 22, 'Fix: AQE thresholds / salt', 9.4, bold=True) + t(180, 56, 'Lesson 8.3', 8.4, 'ink2') + cap('Targeted.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Compare after', 9.4, 'acc', bold=True) + t(180, 56, 'max task 6 min', 8.4, 'ink2') + cap('Same metrics, verified.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'The two-hour join',
              'Finding skew in the UI. (Typical; pattern from our screenshots.)',
              'Skew in the UI', 'The task summary shows max far above median; find the key and fix the skew', [e1, e2, e3, e4, e5],
              ['Slow.', 'Skew.', 'Key.', 'Fix.', 'Verify.'],
              hid='scenario-skewui')
b1 = (t(180, 22, 'Stage with 20,000 tasks', 9.4, bold=True) + t(180, 56, 'median task 15 ms', 8.4, 'ink2') + cap('Scheduler-bound.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Input: 20,000 files', 9.4, bold=True) + t(180, 56, 'avg 200 KB each', 8.4, 'ink2') + cap('Small files.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'Compact the table', 9.4, bold=True) + t(180, 56, 'Lesson 8.1 / 5.3', 8.4, 'ink2') + cap('Fewer, bigger files.', '', 'green', y=150, h=34))
b4 = (t(180, 22, '200 tasks of 2 s', 9.4, bold=True) + t(180, 56, 'stage 10x faster', 8.4, 'ink2') + cap('Overhead gone.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Add a file-size check', 9.4, 'acc', bold=True) + t(180, 56, 'to the writer job', 8.4, 'ink2') + cap('Prevent it.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Twenty thousand tiny tasks',
              'Too many tasks in the UI. (Typical.)',
              'Too many tasks', 'A huge count of millisecond tasks points to small files or too many partitions', [b1, b2, b3, b4, b5],
              ['Tasks.', 'Files.', 'Compact.', 'Faster.', 'Prevent.'],
              hid='scenario-tiny')
u1 = (t(180, 22, 'Job failed overnight', 9.4, bold=True) + t(180, 56, 'live UI gone', 8.4, 'ink2') + cap('Need history.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'History Server: stage 14', 9.4, bold=True) + t(180, 56, '4 failed attempts', 8.4, 'ink2') + cap('Executors lost.', '', 'red', y=150, h=34))
u3 = (t(180, 22, 'Executors tab', 9.4, bold=True) + t(180, 56, 'exit code 137 / OOMKilled', 8.4, 'ink', mono=True) + cap('Container memory.', '', 'amber', y=150, h=34))
u4 = (t(180, 22, 'Python UDF stage', 9.4, bold=True) + t(180, 56, 'raise memoryOverhead (8.4)', 8.4, 'ink2') + cap('Off-heap fix.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Event logs always on', 9.4, 'acc', bold=True) + t(180, 56, 'spark.eventLog.enabled=true', 8.4, 'ink', mono=True) + cap('Debug the past.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Debugging last night’s failure',
              'History Server and executor failures. (Typical.)',
              'History Server', 'Event logs and the History Server let you diagnose finished or failed applications', [u1, u2, u3, u4, u5],
              ['Failed.', 'History.', 'Executors.', 'Fix.', 'Logs on.'],
              hid='scenario-history')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Reading the numbers</h2>
  <p>Left: real UI metrics. Right: what each pattern means.</p>
''' + two + '''
  <p>Three live scenarios follow: a skewed join, thousands of tiny tasks, and a failure found in the History Server.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>The Spark UI at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'on-call', 11, 'blue', bold=True) + t(60, 58, 'runbook', 7.4, 'ink2'),
    '1. On-call runbooks',
    'Runbooks list the UI path: SQL tab → slowest stage → task summary → symptom table.',
    ['Alert', '*UI path', 'Cause']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'history', 11, 'green', bold=True) + t(60, 58, 'server', 7.4, 'ink2'),
    '2. Post-mortems',
    'Event logs kept for 30 days let teams compare a bad run with a good one.',
    ['Event logs', '*History Server', 'Diff runs']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'REST', 12, 'violet', bold=True) + t(60, 58, 'metrics', 7.4, 'ink2'),
    '3. Automated checks',
    'Jobs read their own stage metrics via the REST API and alert on skew or spill.',
    ['REST API', '*max/median', 'Alert']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'review', 11, 'acc', bold=True) + t(60, 58, 'plans', 7.4, 'ink2'),
    '4. Code reviews',
    'New pipelines attach a screenshot of the SQL plan graph showing the expected joins.',
    ['New job', '*plan graph', 'Approved']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'cost', 12, 'acc', bold=True) + t(60, 58, 'tuning', 7.4, 'ink2'),
    '5. Cost tuning',
    'Teams find the stages with the most task time and fix those first.',
    ['Task time', '*top stages', 'Savings']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> jobs, stages and tasks in <a href="../../01-introduction/04-how-a-spark-job-runs/">1.4</a>; this lesson uses the problems from <a href="../03-data-skew-and-salting/">8.3</a> and <a href="../04-memory-spill-and-oom/">8.4</a>.</p></div>
'''
EXTRA = ''
_x = os.path.join(HERE, '_extra.py')
if os.path.exists(_x): exec(open(_x).read())
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + EXTRA + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
