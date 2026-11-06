import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
def sect(n, a, b=None):
    s = capf(n); i = s.index(a); j = s.index(b, i) if b else len(s)
    return s[i:j].rstrip()

def opbox(x, y, label, sub='', tone='card', w=128, h=26):
    o = box(x, y, w, h, tone) + t(x + w / 2, y + (11 if sub else 16), label, 7.2, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 21, sub, 6.4, 'ink2', mono=True)
    return o

def fig(src, w, h, alt, caption):
    return f'''  <figure style="margin:18px 0">
    <img src="{src}" width="{w}" height="{h}" loading="lazy" alt="{alt}" style="max-width:100%;height:auto;border:1px solid var(--line);border-radius:8px">
    <figcaption class="muted" style="font-size:.9em;margin-top:6px">{caption}</figcaption>
  </figure>
'''

def ladder(hi=-1, note=''):
    """code → plan → job → stages → tasks"""
    items = [('Your code', 'lazy steps', 'blue'), ('Action', 'show · count', 'violet'), ('Job', '≥ 1 per action', 'amber'),
             ('Stages', 'cut at shuffles', 'green'), ('Tasks', '1 per partition', 'green')]
    o = ''
    for k, (a, b, tone) in enumerate(items):
        x = 10 + k * 70
        o += opbox(x, 40, a, b, 'acc' if k == hi else tone, 64, 30)
        if k:
            o += arrow(x - 6, 55, x, 55, 'ink3', 1.2)
    return o

# ---------------------------------------------------------------- story
sc = (ladder(-1) +
      box(410, 12, 222, 136, 'card') + t(521, 30, 'One program, measured', 8.6, bold=True) +
      ''.join(t(422, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
          ('3 transformations : 334 ms, 0 jobs', 'green'), ('1 collect()       : 3.6 s, 2 jobs', 'amber'),
          ('show() → 2 jobs, 3 stages', 'ink'), ('stage 1: 4 tasks × 1,250,000 rows', 'ink'),
          ('shuffled: 32 rows, not 4.75 M', 'green'), ('typo → error before any job', 'red')])))
scene_svg = scene('Transformations only describe work; an action starts one or more jobs; each job is split into stages at shuffle boundaries; each stage runs one task per partition. The numbers on the right come from one real program.', sc,
                  'Nothing runs until an <tspan font-weight="700" class="s-acc">action</tspan> asks for a result.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Why did my three lines take no time, and the fourth took ages?”</h2>
  <div class="story">
    <p class="narration">Riya timed her PySpark notebook cell by cell. Reading five million orders, filtering and grouping took a fraction of a second. Then <code>show()</code> took several seconds. She suspects her timer is broken. Kabir opens the Spark UI and sees “jobs”, “stages” and “tasks” he cannot explain.</p>

{scene_svg}

R> Sir, did Spark really read five million rows in 0.3 seconds?
A> It read nothing. Transformations such as <code>where</code> and <code>groupBy</code> only add steps to a <b>plan</b>. When you call an <b>action</b> such as <code>show()</code>, Spark optimises the whole plan and starts a <b>job</b>. The job is cut into <b>stages</b> wherever data must be shuffled, and each stage runs one <b>task</b> per partition.
K> And the Spark UI shows all of that?
A> Every job, stage and task, with timings and row counts. Today we run one program on the cluster, label its jobs, and read the UI, the plan and the REST API together. All screenshots and outputs are real, from Spark 4.3.0.
  </div>
</section>
'''

lv = '''
LEVELS> Jobs, stages and tasks at three levels
L1> Ordering food for a party
      <ul>
        <li>Writing the shopping list (transformations) costs nothing; going to the shop (action) is the real work.</li>
        <li>The trip has legs: buy everything in each shop (stage), then bring it all together (shuffle) before cooking.</li>
        <li>Several friends shop at once, one aisle each (tasks on partitions).</li>
      </ul>
L2> The rules
      <ul>
        <li><b>Transformations</b> (where, select, withColumn, groupBy, join) are lazy; <b>actions</b> (show, count, collect, write) run jobs.</li>
        <li>A <b>job</b> is cut into <b>stages</b> at <b>wide</b> dependencies (shuffles: groupBy, join, orderBy, repartition). <b>Narrow</b> steps (filter, select) are fused into one stage.</li>
        <li>One <b>task</b> per partition per stage. With Adaptive Query Execution (AQE), one action can start several jobs; stages whose output already exists are <b>skipped</b>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>Defining three transformations took 334 ms and started 0 jobs (Spark still <b>analysed</b> them: a misspelt column failed at once).</li>
        <li><code>show()</code> started 2 jobs; the first stage read 4 partitions × 1,250,000 rows but wrote only <b>32</b> rows to the shuffle, thanks to partial aggregation.</li>
        <li>Reading Parquet started a small job before any action, to read the file footers and schema.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Actions, jobs, stages and tasks</h2>
''' + def_block(
    'Spark evaluates <b>lazily</b>: transformations build a logical plan without processing data, while <b>actions</b> trigger execution. For each action, Spark SQL’s optimizer (Catalyst) produces a physical plan, and the driver’s DAG scheduler submits one or more <b>jobs</b>. Each job is divided into <b>stages</b> at shuffle boundaries (wide dependencies, where rows must be redistributed between partitions); consecutive narrow operations are pipelined inside one stage. A stage runs as a set of <b>tasks</b>, one per partition, executed in parallel on executor slots. Shuffle map stages write shuffle files that the next stage reads. The <b>Spark UI</b> (port 4040 while the application runs, or the history server afterwards) shows jobs, stages, tasks, storage, executors and SQL plans with their metrics.',
    'Spark waits until you ask for a result. Then it turns your code into a job, cuts the job into stages wherever data must move between machines, and runs one task per piece of data. The Spark UI shows all of this.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Transformation', 'Describes a new DataFrame: where, select, groupBy … Lazy.'),
    ('Action', 'Asks for a result: show, count, collect, write. Runs jobs.'),
    ('Job', 'The work started by an action (sometimes several per action).'),
    ('Stage', 'Part of a job with no shuffle inside; ends at a shuffle.'),
    ('Task', 'One stage applied to one partition, on one executor slot.'),
    ('Narrow / wide', 'Narrow: each output partition needs one input partition. Wide: needs many (shuffle).'),
    ('AQE', 'Adaptive Query Execution: re-plans between stages using real sizes.'),
    ('Skipped stage', 'A stage whose shuffle output already exists, so it is not run again.'),
]) + '''

  <h3>The program and what it became</h3>
''' + table(['Code', 'Kind', 'Jobs started', 'Seen in the lab'], [
    ['<code>spark.read.parquet(…)</code>', 'Reader', '1 small job (footers/schema)', 'Job 0: 1 task'],
    ['<code>.where(…)</code>, <code>.groupBy(…).agg(…)</code>', 'Transformations', '0', '334 ms in total (analysis only)'],
    ['<code>.orderBy(…).show(10)</code>', 'Action', '2 (AQE: map stage, then result)', 'Jobs 1–2: 4 tasks + 1 task'],
    ['<code>orders.count()</code>', 'Action', '2', 'Jobs 3–4: 4 tasks + 1 task'],
    ['<code>daily.explain()</code>', 'Prints the plan', '0', 'Physical plan with one Exchange'],
], minw=740) + lv + '''
EXAM> “What is the difference between a job, a stage and a task?” An action triggers a job; the job is split into stages at shuffle (wide) boundaries; each stage runs as tasks, one per partition, in parallel on executors. Narrow transformations are pipelined within a stage. Transformations are lazy; only actions start jobs.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Narrow vs wide, and the tabs of the Spark UI</h2>
''' + table(['Operation', 'Dependency', 'New stage?', 'Example'], [
    ['where, select, withColumn, map', 'Narrow', 'No (pipelined)', '<code>where(status = DELIVERED)</code>'],
    ['union, coalesce (fewer partitions)', 'Narrow', 'No', '<code>coalesce(1)</code>'],
    ['groupBy + agg, distinct', 'Wide', 'Yes (Exchange)', '<code>groupBy("city")</code>'],
    ['join (not broadcast)', 'Wide', 'Yes', 'orders ⋈ customers'],
    ['orderBy / sort, repartition', 'Wide', 'Yes', '<code>orderBy(desc("revenue"))</code>'],
], minw=680) + table(['UI tab', 'Shows', 'Use it to'], [
    ['Jobs', 'Every job, its description, duration, stages, tasks', 'Find the slow action'],
    ['Stages', 'Tasks per stage, shuffle read/write, task time percentiles', 'Spot skew and spills'],
    ['Storage', 'Cached DataFrames and how much is in memory', 'Check cache() worked (Lesson 3.1)'],
    ['Environment', 'Spark, Java, Python versions and every configuration', 'Confirm settings'],
    ['Executors', 'Executors, cores, tasks, memory, GC, logs', 'Find failing or overloaded executors'],
    ['SQL / DataFrame', 'Each query’s plan with row counts per operator', 'See where rows are filtered or exploded'],
], minw=680) + '''
WARN> Calling several actions on the same DataFrame repeats the work each time: our <code>show()</code> and <code>count()</code> both read the Parquet files. If you reuse a result, cache it (Lesson 3.1) or write it once. Also avoid actions inside loops “just to check”.
</section>
'''

FIG1 = fig('ui-jobs.webp', 1280, 760, 'Spark UI Jobs tab listing five completed jobs with descriptions A, B and C', 'Real screenshot: the Jobs tab of our program. The descriptions come from <code>setJobDescription()</code>. Job 0 ran before any action; <code>show()</code> and <code>count()</code> started two jobs each.')
FIG2 = fig('ui-job2.webp', 1280, 860, 'Details for job 2 with a DAG of a skipped stage 2 and a completed stage 3', 'Real screenshot: job 2’s DAG. Stage 2 (grey) is <b>skipped</b>: its shuffle files were written by job 1. Stage 3 reads them (AQEShuffleRead), finishes the aggregation and takes the top rows.')
FIG3 = fig('ui-stage1.webp', 1280, 900, 'Details for stage 1 with four tasks each reading 1,250,000 records and writing 8 shuffle records', 'Real screenshot: stage 1 ran 4 tasks, each reading 1,250,000 records and writing only <b>8</b> shuffle records (one partial result per city).')
FIG4 = fig('ui-sqlplan.webp', 1280, 1100, 'SQL tab plan visualisation with row counts 5,000,000, 4,750,000, 32 and 8 between operators', 'Real screenshot: the SQL tab for <code>show()</code>. Rows between operators: 5,000,000 scanned → 4,750,000 after the filter → <b>32</b> into the Exchange → 8 cities.')

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>One program, followed through the engine</h2>
  <p>All outputs are real: Spark 4.3.0 in local mode (Steps 1–2) and on our standalone cluster with two executors (Steps 3–7), reading <code>orders_big</code>: 5,000,000 orders in 8 Parquet files. Screenshots come from the history server.</p>
''' + stepper([
    ('Step 1 · Transformations are free; actions are not',
     code('python', 'lazy.py', 'orders = spark.read.parquet("orders_big")\nt = time.time()\nreport = (orders.where(F.col("status") == "DELIVERED")\n                .withColumn("gst", F.col("amount") * 0.05)\n                .groupBy("city").agg(F.sum("gst").alias("gst")))\nprint(time.time() - t, "jobs:", ...)      # 3 transformations\nt = time.time()\nrows = report.collect()                     # 1 action\nprint(time.time() - t, "jobs:", ...)', capf('l14_lazy.txt')),
     'Three transformations took 334 ms and ran <b>no jobs</b>. One action took 3.6 s and ran 2 jobs. The 334 ms were not data processing: Spark <b>analysed</b> the plan (resolved columns and types) and stopped there.'),
    ('Step 2 · Lazy, but checked at once',
     code('python', 'typo.py', 'orders = spark.read.parquet("orders_big")\nbad = orders.groupBy("cty").count()          # typo; no action called', capf('l14_eager.txt').split(', `amount`')[0] + ', …]'),
     'The error appeared on the transformation line, not at a later action: DataFrame operations are <b>analysed eagerly</b> and <b>executed lazily</b>. Spark even suggested the right column. (With Spark Connect clients, analysis can be deferred; Lesson 11.3.)'),
    ('Step 3 · The program on the cluster',
     code('python', 'job_anatomy.py', 'sc.setJobDescription("A: read + filter + groupBy (lazy, nothing runs yet)")\norders = spark.read.parquet("/data/orders_big")\ndaily = (orders.where(F.col("status") == "DELIVERED").groupBy("city")\n               .agg(F.count("*").alias("orders"), F.sum("amount").alias("revenue")))\nprint("input partitions:", orders.rdd.getNumPartitions())\n\nsc.setJobDescription("B: show() the city report")\ndaily.orderBy(F.desc("revenue")).show(10)\n\nsc.setJobDescription("C: count() all orders")\nprint("total orders:", orders.count())', sect('l14_anatomy.txt', 'input partitions', '== Physical')),
     '<code>setJobDescription</code> labels jobs in the UI. 8 Parquet files became <b>4 partitions</b>: Spark packed the small files into one split per core (4 cores in the cluster). Mumbai and Bengaluru have about twice the orders of other cities because the generator weighted them.'),
    ('Step 4 · Five jobs from two actions',
     code('bash', 'history server REST API', 'python3 rest.py tiffingo-job-anatomy      # /api/v1/applications/<id>/jobs and /stages', sect('l14_rest.txt', 'JOBS', 'EXECUTORS')) + FIG1,
     'Job 0 (labelled A) ran <b>before any action</b>: reading Parquet lists the files and reads their footers to learn the schema. <code>show()</code> started jobs 1 and 2: with AQE, Spark first runs the stage before the shuffle as its own job, looks at the real shuffle sizes, then plans the rest. Job 2’s “5 tasks” include 4 of skipped stage 2; only 1 task ran. <code>count()</code> did the same with jobs 3 and 4.'),
    ('Step 5 · Stages: where the shuffle cuts the job',
     code('python', 'explain.py', 'daily.explain()', sect('l14_anatomy.txt', '== Physical')) + FIG2,
     'Read the plan bottom-up. Scan, Filter, Project and the first <b>HashAggregate</b> (partial counts and sums) are narrow, so they run in one stage. <b>Exchange hashpartitioning(city, 200)</b> is the shuffle: rows of the same city must meet. Everything after it is the next stage. The 200 partitions shrank at run time: AQE coalesced them because the data was tiny.'),
    ('Step 6 · Tasks: one per partition',
     code('text', 'stage 1, from the Stages tab', 'Tasks: 4   Input: 161.2 KiB / 5,000,000 records\nper task: 1,250,000 records in, 8 shuffle records out (667 B)\nduration: 3–4 s each, GC 0.2 s\nShuffle write total: 2.6 KiB / 32 records') + FIG3,
     'Four partitions, four tasks, one on each of the 4 executor slots, all at once. Each task aggregated its 1,250,000 rows down to <b>8 rows</b> (one per city) <b>before</b> the shuffle. That is why only 32 rows and 2.6 KiB crossed the network instead of 4.75 million rows. The low “Input” size is Parquet’s compression and column pruning: only <code>city</code>, <code>amount</code> and <code>status</code> were read.'),
    ('Step 7 · The SQL tab: rows between operators',
     code('text', 'SQL / DataFrame tab, query 0', 'Scan parquet          5,000,000 rows\nFilter                4,750,000 rows  (5% CANCELLED removed)\nHashAggregate partial →  32 rows\nExchange + AQEShuffleRead\nHashAggregate final   →   8 rows\nTakeOrderedAndProject →  top 10 (8 cities)') + FIG4,
     'The SQL tab is usually the fastest way to understand a slow query: it shows each operator with its row counts and time. Here the filter removed 250,000 cancelled orders, and the partial aggregation did almost all the work in the first stage (10.1 s of task time across 4 tasks) while the final stage took 37 ms.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('3 transformations :  334.4 ms  jobs: 0', G), ('1 action collect(): 3591.4 ms  jobs: 2', Y), ('rows returned: 8', W)], size=7.2),
    term([('groupBy("cty")', W), ('[UNRESOLVED_COLUMN.WITH_SUGGESTION]', RD), ('Did you mean `city`?', G)], size=7.4),
    term([('job 0  A: read …       1 task', W), ('job 1  B: show()        4 tasks', G), ('job 2  B: show()        1 task (+4 skipped)', G), ('job 3–4 C: count()', W)], size=7.0),
    term([('HashAggregate (final)', W), ('Exchange hashpartitioning(city, 200)', Y), ('HashAggregate (partial)', W), ('Filter · FileScan parquet', W)], size=7.2),
    term([('4 tasks × 1,250,000 rows', W), ('8 shuffle rows per task', G), ('32 rows shuffled in total', G), ('final stage: 37 ms', G)], size=7.4),
]
def stg(hi):
    o = box(14, 30, 150, 84, 'acc' if hi == 1 else 'green') + t(89, 44, 'Stage 1 · 4 tasks', 7.6, bold=True)
    o += ''.join(t(24, 60 + k * 13, s, 6.6, 'ink2', anchor='start', mono=True) for k, s in enumerate(['scan → filter → project', '→ partial aggregate', '1,250,000 rows / task', '→ 8 rows / task']))
    o += arrow(166, 72, 206, 72, 'red' if hi == 2 else 'acc', 2) + t(186, 66, 'shuffle', 6.4, 'ink2')
    o += box(208, 44, 140, 56, 'acc' if hi == 3 else 'blue') + t(278, 62, 'Stage 2 · 1 task', 7.6, bold=True) + t(278, 80, 'final aggregate · top 10', 6.6, 'ink2', mono=True)
    return o
B1 = [
    t(180, 16, 'A plan, not a result', 9.4, bold=True) + ladder(0) + cap('Transformations add steps; nothing runs.', '', 'blue', y=96, h=34),
    t(180, 16, 'Analysis happens immediately', 9.4, bold=True) + ladder(0) + cap('Names and types are checked at once.', '', 'violet', y=96, h=34),
    t(180, 16, 'Actions start jobs', 9.4, bold=True) + ladder(2) + cap('With AQE, one action can mean 2 jobs.', '', 'amber', y=96, h=34),
    t(180, 16, 'Shuffles cut stages', 9.4, bold=True) + stg(2) + cap('Exchange = stage boundary.', '', 'amber', y=126, h=34),
    t(180, 16, 'Partial aggregation first', 9.4, bold=True) + stg(1) + cap('Shrink rows before they travel.', '', 'green', y=126, h=34),
]
see_caps = ['Defining the report was instant; collecting it took 3.6 s.',
            'A typo failed before any job ran.',
            'Two actions became five jobs.',
            'The plan has one Exchange: one shuffle.',
            'Each task sent 8 rows, not 1.25 million.']
behind_caps = ['Spark records transformations as a logical plan.',
               'The analyzer resolves columns eagerly.',
               'AQE runs the map stage, then re-plans.',
               'Narrow steps are pipelined inside a stage.',
               'Partial sums per partition, final sums after the shuffle.']
two = anim_two('How a job runs', 'Action → job → stages → tasks', 'Real lab outputs', 'Inside the engine', see, B1, see_caps, behind_caps)

# ---- scenario 1: count in a loop
e1 = (t(180, 22, 'Notebook takes 20 minutes', 9.4, bold=True) + t(180, 56, 'for c in cities: df.where(city == c).count()', 8, 'ink', mono=True) + cap('One job per city.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Jobs tab', 9.4, bold=True) + t(180, 56, '120 jobs, each scanning all files', 8.4, 'ink2') + cap('The UI shows the pattern.', '', 'amber', y=150, h=34))
e3 = (t(180, 22, 'One action instead', 9.4, bold=True) + t(180, 56, 'df.groupBy("city").count()', 8.4, 'ink', mono=True) + cap('One job, one scan.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Result', 9.4, bold=True) + t(180, 56, '20 minutes → under a minute', 8.4, 'ink2') + cap('Same numbers.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Rule', 9.4, 'acc', bold=True) + t(180, 56, 'count the actions in your code', 8.4, 'ink2') + cap('Each one is a job.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Actions inside a loop',
              'A very common beginner slowdown. (Typical; job behaviour from our lab.)',
              'Too many actions', 'Every action is a job that re-reads the data; replace loops of actions with one grouped query', [e1, e2, e3, e4, e5],
              ['Slow notebook.', 'Many jobs in the UI.', 'Group once.', 'Much faster.', 'Count actions.'],
              hid='scenario-loop')

# ---- scenario 2: slow stage diagnosis
b1 = (t(180, 22, 'Nightly job 2× slower', 9.4, bold=True) + t(180, 56, 'which part?', 8.4, 'ink2') + cap('Open the Jobs tab.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Find the slow stage', 9.4, bold=True) + t(180, 56, 'Stages: duration, shuffle read/write', 8.2, 'ink2') + cap('One stage takes 80%.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'Task percentiles', 9.4, bold=True) + t(180, 56, 'median 4 s · max 6 min', 8.4, 'ink', mono=True) + cap('One huge task: skew.', '', 'amber', y=150, h=34))
b4 = (t(180, 22, 'SQL tab', 9.4, bold=True) + t(180, 56, 'join on customer_id, one key with 30% of rows', 8, 'ink2') + cap('Found the cause.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Fix', 9.4, 'acc', bold=True) + t(180, 56, 'AQE skew join · salting (Lesson 8.3)', 8.2, 'ink2') + cap('Measure again in the UI.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Reading the Spark UI during an incident',
              'How engineers find the slow part of a job. (Typical workflow.)',
              'Spark UI diagnosis', 'Jobs → slowest stage → task time percentiles → SQL plan shows where and why; then fix and compare', [b1, b2, b3, b4, b5],
              ['Something is slow.', 'Find the stage.', 'Look at task spread.', 'Find the operator.', 'Fix and measure.'],
              hid='scenario-ui')

# ---- scenario 3: unnecessary shuffles
u1 = (t(180, 22, 'Three Exchanges in the plan', 9.4, bold=True) + t(180, 56, 'repartition · groupBy · orderBy', 8.4, 'ink', mono=True) + cap('Three shuffles.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Which are needed?', 9.4, bold=True) + t(180, 56, 'repartition(200) before groupBy', 8.4, 'ink', mono=True) + cap('Useless: groupBy shuffles anyway.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'orderBy on 50 M rows', 9.4, bold=True) + t(180, 56, 'only the top 10 are used', 8.4, 'ink2') + cap('Use orderBy + limit: TakeOrdered.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'After', 9.4, bold=True) + t(180, 56, 'one Exchange, like our job', 8.4, 'ink2') + cap('Less network, less disk.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Habit', 9.4, 'acc', bold=True) + t(180, 56, 'explain() before you ship', 8.4, 'ink', mono=True) + cap('Count the Exchanges.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Removing shuffles you do not need',
              'A code-review habit of experienced Spark engineers. (Typical.)',
              'Shuffle hygiene', 'Read explain() output, count Exchange operators and remove the ones that do not change the result', [u1, u2, u3, u4, u5],
              ['Three shuffles.', 'One is useless.', 'One is too big.', 'One remains.', 'Always explain().'],
              hid='scenario-shuffles')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Action → job → stages → tasks</h2>
  <p>Left: real outputs. Right: what happens inside the engine.</p>
''' + two + '''
  <p>Three live scenarios follow: actions in a loop, diagnosing with the UI, and removing shuffles.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Jobs, stages and the UI at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'UI', 12, 'blue', bold=True) + t(60, 58, 'on-call', 7.4, 'ink2'),
    '1. On-call debugging',
    'The first step for a slow or failed job is the Spark UI or history server: slowest stage, task spread, SQL plan.',
    ['Alert', '*Spark UI', 'Root cause']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'review', 10, 'green', bold=True) + t(60, 58, 'explain()', 7.4, 'ink2'),
    '2. Code review with explain()',
    'Teams check plans for extra Exchanges, missing filters and wrong join strategies before merging.',
    ['Pull request', '*explain()', 'Approved']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'labels', 11, 'violet', bold=True) + t(60, 58, 'jobs', 7.4, 'ink2'),
    '3. Labelled jobs',
    'setJobDescription and job groups make long pipelines readable in the UI and in monitoring tools.',
    ['Pipeline', '*labels', 'Readable UI']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'history', 10, 'acc', bold=True) + t(60, 58, 'server', 7.4, 'ink2'),
    '4. Persistent UIs in the cloud',
    'Managed services keep the Spark UI after clusters end (e.g. EMR’s persistent application UI) for audits and tuning.',
    ['Event logs', '*history', 'Post-mortem']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'REST', 12, 'acc', bold=True) + t(60, 58, 'metrics', 7.4, 'ink2'),
    '5. Automated job reports',
    'Platform teams pull /api/v1 metrics after each run to track task time, shuffle bytes and cost per job.',
    ['Job ends', '*REST API', 'Dashboard']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> Lesson <a href="../03-spark-architecture/">1.3</a> (driver and executors). From the Hive course: a Spark stage is like a Tez vertex, and an Exchange is like a Tez shuffle edge.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
