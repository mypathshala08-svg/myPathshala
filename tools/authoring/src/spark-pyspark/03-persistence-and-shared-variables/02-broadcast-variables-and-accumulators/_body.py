import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
def has(n, *keys):
    return '\n'.join(l for l in capf(n).split('\n') if any(k in l for k in keys))

def opbox(x, y, label, sub='', tone='card', w=128, h=26):
    o = box(x, y, w, h, tone) + t(x + w / 2, y + (11 if sub else 16), label, 7.2, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 21, sub, 6.4, 'ink2', mono=True)
    return o

def share(kind='broadcast', hi=False):
    """driver ↔ executors; broadcast flows out once, accumulators flow back"""
    o = opbox(20, 50, 'driver', 'dict · counter', 'blue', 110, 32)
    for k, y in enumerate((24, 76)):
        o += opbox(232, y, f'executor {k}', 'tasks', 'green', 110, 32)
        if kind == 'broadcast':
            o += arrow(132, 66, 230, y + 16, 'red' if hi else 'acc', 1.6)
        elif kind == 'closure':
            for j in range(3):
                o += arrow(132, 60 + j * 6, 230, y + 10 + j * 6, 'red', 0.9)
        else:
            o += arrow(230, y + 16, 132, 66, 'violet', 1.6)
    return o

# ---------------------------------------------------------------- story
sc = (share('broadcast') +
      box(410, 12, 222, 136, 'card') + t(521, 30, 'Measured on the cluster', 8.6, bold=True) +
      ''.join(t(422, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
          ('dict in closure : 14.8 s, 3 jobs', 'amber'), ('broadcast dict  :  8.2 s, 3 jobs', 'green'), ('broadcast join  : 4.8 s', 'green'),
          ('sort-merge join : 6.1 s', 'amber'), ('accumulator in map, 2 actions: 2', 'red'), ('in foreach: 1 (correct)', 'green')])))
scene_svg = scene('Two kinds of shared variables: broadcast variables send a read-only value to every executor once; accumulators collect updates from tasks back to the driver. The numbers on the right are from our cluster and laptop.', sc,
                  'Broadcast <tspan font-weight="700" class="s-acc">out</tspan> once; accumulate <tspan font-weight="700" class="s-acc">back</tspan> safely.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Every task needs the customer list”</h2>
  <div class="story">
    <p class="narration">Each TiffinGo order must be tagged with its customer’s membership plan. Riya keeps the plans in a Python dictionary with 400,000 customers and uses it inside a <code>map</code>. It works, but slowly. Kabir also counts bad rows with an accumulator, and the count changes depending on how many reports run.</p>

{scene_svg}

R> Sir, the dictionary is only 2 MB. Why is it slow?
A> Because a dictionary used inside a function travels <b>with the function</b>: Spark pickles it into every job, and every task unpickles its own copy. A <b>broadcast variable</b> sends it once per executor and keeps it there for all tasks and jobs.
K> And my bad-row counter that says 2 when there is only 1 bad row?
A> Accumulators are exact only inside <b>actions</b>. Inside transformations, recomputation counts again. Today we measure both on our cluster, compare a broadcast join with a sort-merge join, and test every accumulator rule. All outputs are real (Spark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Shared variables at three levels
L1> Notice boards and tally sheets
      <ul>
        <li>A <b>broadcast variable</b> is a notice pinned once in every kitchen: all cooks read it, nobody changes it.</li>
        <li>An <b>accumulator</b> is a tally sheet: cooks only add marks, and only the head chef reads the total.</li>
        <li>Copying the whole notice into every order slip (a closure) works, but wastes paper and time.</li>
      </ul>
L2> The API
      <ul>
        <li><code>b = sc.broadcast(value)</code>; tasks read <code>b.value</code>; free with <code>b.unpersist()</code> or <code>b.destroy()</code>.</li>
        <li><code>acc = sc.accumulator(0)</code>; tasks call <code>acc.add(x)</code>; the driver reads <code>acc.value</code>. Custom types with <code>AccumulatorParam</code>.</li>
        <li>For DataFrames, <code>F.broadcast(small_df)</code> asks for a <b>broadcast hash join</b>; Spark also does it automatically below <code>spark.sql.autoBroadcastJoinThreshold</code> (10 MB by default).</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>A 400,000-entry dict in the closure: 14.8 s for 3 jobs and a 2.1 MiB pickled function shipped per job; as a broadcast: 8.2 s, shipped once.</li>
        <li>After <code>unpersist()</code>, using the broadcast again failed in PySpark 4.3 (<code>FileNotFoundError</code>); after <code>destroy()</code>, Spark refused at once.</li>
        <li>An accumulator inside <code>map</code> counted 1 bad row as 2 over two uncached actions; with cache or inside <code>foreach</code> it was exact; a failed and retried task was not double counted.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Broadcast variables and accumulators</h2>
''' + def_block(
    'Spark provides two kinds of shared variables. A <b>broadcast variable</b> wraps a read-only value created on the driver and distributes it efficiently to each executor once, where it is cached and shared by all tasks, instead of shipping a copy with every task’s closure. An <b>accumulator</b> is a variable that tasks can only add to through an associative and commutative operation, and whose value only the driver can read; Spark merges the updates of successful tasks. Updates performed inside <b>actions</b> are applied exactly once per task; updates inside <b>transformations</b> may be applied again if a stage is recomputed, so they are suitable for debugging and monitoring rather than exact results. Spark SQL uses broadcasting for <b>broadcast hash joins</b>, sending a small table to every executor so the large side does not need to be shuffled.',
    'A broadcast variable sends a read-only value (like a lookup table) to every executor once. An accumulator is a counter that tasks add to and the driver reads. Broadcasts make lookups and small-table joins fast; accumulators are exact inside actions, but can count twice inside transformations.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('sc.broadcast(v)', 'Send v to every executor once; read with <code>.value</code>.'),
    ('Closure capture', 'Variables used in a function travel with it to every task.'),
    ('unpersist() / destroy()', 'Free a broadcast’s copies; destroy also frees the driver’s.'),
    ('sc.accumulator(0)', 'A counter tasks can add to.'),
    ('AccumulatorParam', 'Defines zero and merge for custom accumulator types.'),
    ('Broadcast hash join', 'Small side sent to all executors; large side not shuffled.'),
    ('Sort-merge join', 'Both sides shuffled and sorted by key, then merged.'),
    ('autoBroadcastJoinThreshold', 'Max size for automatic broadcast joins (10 MB default).'),
]) + '''

  <h3>Closure vs broadcast vs accumulator</h3>
''' + table(['', 'Variable in a closure', 'Broadcast variable', 'Accumulator'], [
    ['Direction', 'Driver → every task', 'Driver → every executor, once', 'Tasks → driver'],
    ['Copies', 'One per task (per job)', 'One per executor', 'Partial value per task, merged'],
    ['Mutable?', 'Copies yes, driver no', 'Read-only', 'Add-only; read on driver'],
    ['Lab', '2.1 MiB per job, 14.8 s', '1,982 KiB once, 8.2 s', 'exact in foreach'],
    ['Use for', 'Small constants', 'Lookup tables, models, configs', 'Counters, metrics, debugging'],
], minw=720) + lv + '''
EXAM> “What are broadcast variables and accumulators?” Shared variables: broadcast variables send a read-only value to each executor once (lookup tables, small-table joins); accumulators let tasks add to a value that only the driver reads (counters). Accumulators are guaranteed exactly-once only for updates made inside actions.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Where shared variables fit</h2>
''' + table(['Need', 'Use', 'Watch out for'], [
    ['Look up codes, names or rates in every task', '<code>sc.broadcast(dict)</code>', 'Must fit in executor and driver memory'],
    ['Join a big table with a small one (DataFrames)', '<code>big.join(F.broadcast(small), key)</code>', 'Too large a broadcast can OOM executors'],
    ['Count bad rows while parsing', 'accumulator in <code>foreach</code> / action', 'In transformations it may double count'],
    ['Count several reasons at once', 'Custom <code>AccumulatorParam</code> (dict)', 'Keep the merged value small'],
    ['Share an ML model for scoring', 'Broadcast the model object', 'Re-broadcast after retraining'],
    ['Exact business totals', 'An aggregation (reduce, groupBy)', 'Not accumulators'],
], minw=700) + '''
WARN> Accumulators are not a way to compute results. Use them for monitoring (how many rows were bad, how many API calls failed) and compute real totals with aggregations. In our lab, one bad row was reported as 2 simply because two actions recomputed the same uncached map.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Measuring shared variables</h2>
  <p>All outputs are real: Spark 4.3.0 standalone cluster with two executors (Steps 1–4) and local mode with up to 3 attempts per task (Steps 5–7). Data: 2,000,000 generated order pairs, a 400,000-customer plan dictionary, <code>orders_big</code>, <code>customers.csv</code> and <code>orders.csv</code>.</p>
''' + stepper([
    ('Step 1 · A lookup table in the closure vs a broadcast',
     code('python', 'broadcast.py (cluster)', "plans = {cid: R.choice([\"Gold\", \"Silver\", \"Basic\", \"Basic\"]) for cid in range(400_000)}\norders = sc.parallelize(range(2_000_000), 16).map(lambda i: (i % 400_000, (i * 7919) % 900 + 60))\n\nfor _ in range(3):      # A: dict captured by the lambda\n    orders.map(lambda kv: (plans[kv[0]], kv[1])).reduceByKey(add).collect()\n\nb = sc.broadcast(plans)\nfor _ in range(3):      # B: dict read through the broadcast\n    orders.map(lambda kv: (b.value[kv[0]], kv[1])).reduceByKey(add).collect()", capf('l32_times.txt')),
     'Identical revenue per plan, 45% less time. With the dictionary in the closure, every job shipped the function together with the whole dictionary and every one of the 16 tasks unpickled its own copy. With a broadcast, each executor fetched it once and its Python workers reused it across tasks and jobs.'),
    ('Step 2 · What actually travelled',
     code('text', 'driver log: MemoryStore blocks', 'grep "Block broadcast_.*_piece0 stored" driver.log', capf('l32_blocks.txt')),
     'PySpark already protects you a little: a pickled function over 1 MB is sent as a broadcast automatically. That is the 2.1 MiB block created for <b>each</b> of the three closure jobs (broadcast 0, 3 and 6). Our explicit broadcast (9) was created once, and the three jobs that used it only shipped a small function holding a reference.'),
    ('Step 3 · The end of a broadcast: unpersist and destroy',
     code('python', 'broadcast.py (cluster)', 'b.unpersist()\norders.map(lambda kv: b.value[kv[0]]).first()\nb.destroy()\norders.map(lambda kv: b.value[kv[0]]).first()', capf('l32_lifecycle.txt')),
     '<code>unpersist()</code> deletes the executors’ copies. The documentation says a later use re-sends it, but in PySpark 4.3 the Python workers looked for their local file and the task failed 4 times. <code>destroy()</code> also deletes the driver’s copy, and Spark refused at task-serialisation time. Practical rule: call them only when you are completely done with the variable, then drop the Python reference.'),
    ('Step 4 · Broadcast joins for DataFrames',
     code('python', 'broadcast.py (cluster)', "big = spark.read.parquet(\"/data/orders_big\")                       # 5,000,000 orders\ncust = spark.read.csv(\"/data/tiffingo/customers.csv\", header=True, inferSchema=True)   # 2,000 rows\nbig.join(cust, \"customer_id\").groupBy(\"plan\").count().collect()      # automatic broadcast\nspark.conf.set(\"spark.sql.autoBroadcastJoinThreshold\", \"-1\")\nbig.join(cust, \"customer_id\").groupBy(\"plan\").count().collect()      # forced sort-merge join\nbig.join(F.broadcast(cust), \"customer_id\").explain()", has('l32_life_join.txt', 'join') + '\n\n' + capf('l32_plan.txt')),
     'The 2,000-row customer table was far below the 10 MB threshold, so Spark chose a <b>BroadcastHashJoin</b> by itself (4.8 s): customers were sent to every executor as a hash table and the 5 million orders never moved. With broadcasting disabled, both sides were shuffled for a sort-merge join (6.1 s). Same counts. On bigger clusters the gap grows with the size of the large side. Lesson 8.2 covers join strategies in depth.'),
    ('Step 5 · Accumulators inside transformations can double count',
     code('python', 'acc.py', "bad = sc.accumulator(0)\ndef parse(l):\n    f = l.split(\",\")\n    if not f[5].isdigit():\n        bad.add(1)\n        return None\n    return int(f[5])\namounts = lines.map(parse)\namounts.count(); amounts.filter(lambda x: x is not None).count()\nprint(bad.value)                                # no cache\n\namounts = lines.map(parse).cache()\namounts.count(); amounts.filter(lambda x: x is not None).count()\nprint(bad.value)                                # with cache", has('l32_acc_clean.txt', '1)', '2)')),
     '<code>orders.csv</code> has exactly one row with <code>amount = abc</code>. Two actions on the uncached RDD ran <code>parse</code> twice per line (Lesson 2.3), so the accumulator said <b>2</b>. With <code>cache()</code>, <code>parse</code> ran once: 1. Any recomputation (an evicted cache, a lost executor, a reused stage) can inflate counters updated in transformations.'),
    ('Step 6 · Exact inside actions, safe across retries',
     code('python', 'acc.py', "bad.value = 0\nlines.foreach(lambda l: bad.add(0 if l.split(\",\")[5].isdigit() else 1))\n\nseen = sc.accumulator(0)\ndef flaky(x):\n    seen.add(1)\n    if TaskContext.get().partitionId() == 0 and TaskContext.get().attemptNumber() == 0:\n        raise RuntimeError(\"simulated executor hiccup\")\n    return x\nsc.parallelize(range(1000), 2).map(flaky).count()", has('l32_acc_clean.txt', '3)', '4)')),
     'Inside the <code>foreach</code> action, the count was exactly 1. In the second test, the first attempt of task 0 added to the accumulator and then failed; Spark retried it and the job counted 1,000 rows. The accumulator also said <b>1,000</b>, not 1,001: updates from <b>failed</b> attempts are discarded. The danger is successful work done twice, not failures.'),
    ('Step 7 · A custom accumulator for data quality',
     code('python', 'acc.py', "class CounterParam(AccumulatorParam):\n    def zero(self, v): return {}\n    def addInPlace(self, a, b):\n        for k, v in b.items(): a[k] = a.get(k, 0) + v\n        return a\nreasons = sc.accumulator({}, CounterParam())\ndef check(l):\n    f = l.split(\",\")\n    if not f[5].isdigit(): reasons.add({\"amount not a number\": 1})\n    if \"/\" in f[4]: reasons.add({\"timestamp format\": 1})\n    if f[7] == \"CANCELLED\": reasons.add({\"cancelled\": 1})\nlines.foreach(check)", has('l32_acc_clean.txt', '5)')),
     'One pass over the 50,001 orders produced a small report: 3,063 cancelled orders, one bad amount and one bad timestamp, the two broken rows from Lesson 1.1. <code>zero</code> gives each task an empty dict; <code>addInPlace</code> merges dicts and must be associative and commutative. Keep accumulator values small: they travel to the driver with every task result.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('dict in closure: 14.8 s for 3 jobs', Y), ('broadcast     :  8.2 s for 3 jobs', G), ('same result: True', G)], size=7.4),
    term([('broadcast_0_piece0  2.1 MiB', Y), ('broadcast_3_piece0  2.1 MiB', Y), ('broadcast_6_piece0  2.1 MiB', Y), ('broadcast_9_piece0  1982 KiB (once)', G)], size=7.2),
    term([('BroadcastHashJoin ... BuildRight', G), ('broadcast hash join: 4.8 s', G), ('sort-merge join    : 6.1 s', Y)], size=7.4),
    term([('accumulator in map, 2 actions: 2', RD), ('with cache()                 : 1', G), ('in foreach                   : 1', G)], size=7.4),
    term([('task 0 failed once, retried', Y), ('count = 1000 | accumulator = 1000', G), ("{'cancelled': 3063, …}", G)], size=7.4),
]
B1 = [
    t(180, 14, 'Closure: copied per task', 9.4, bold=True) + share('closure') + cap('Many copies of the same dictionary.', '', 'red', y=116, h=30),
    t(180, 14, 'Broadcast: once per executor', 9.4, bold=True) + share('broadcast') + cap('Tasks share the executor’s copy.', '', 'green', y=116, h=30),
    t(180, 14, 'Small side broadcast', 9.4, bold=True) + share('broadcast', True) + cap('The 5 M orders never moved.', '', 'green', y=116, h=30),
    t(180, 14, 'Updates flow back', 9.4, bold=True) + share('acc') + cap('Recomputed tasks add again.', '', 'amber', y=116, h=30),
    t(180, 14, 'Only successful tasks count', 9.4, bold=True) + share('acc') + cap('Failed attempts are discarded.', '', 'violet', y=116, h=30),
]
see_caps = ['Broadcasting the dictionary cut time by 45%.',
            'The closure shipped 2.1 MiB with every job.',
            'Spark broadcast the small table by itself.',
            'One bad row counted twice without cache.',
            'Retries did not inflate the accumulator.']
behind_caps = ['Each task unpickled its own copy from the closure.',
               'The broadcast was sent once and reused.',
               'BroadcastExchange builds a hash table on each executor.',
               'map ran twice; so did acc.add.',
               'Spark merges updates from successful tasks only.']
two = anim_two('Shared variables', 'Out once, back safely', 'Real lab outputs', 'How values travel', see, B1, see_caps, behind_caps)

# ---- scenario 1: slow lookup job
e1 = (t(180, 22, 'Tagging job slows down', 9.4, bold=True) + t(180, 56, 'lookup dict grew to 400,000 keys', 8.4, 'ink2') + cap('Used inside map().', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Driver log', 9.4, bold=True) + t(180, 56, '2.1 MiB broadcast per job', 8.4, 'ink', mono=True) + cap('The closure travels each time.', '', 'amber', y=150, h=34))
e3 = (t(180, 22, 'Broadcast it once', 9.4, bold=True) + t(180, 56, 'b = sc.broadcast(plans)', 8.4, 'ink', mono=True) + cap('Read b.value in tasks.', '', 'green', y=150, h=34))
e4 = (t(180, 22, '45% faster', 9.4, bold=True) + t(180, 56, '14.8 s → 8.2 s for 3 jobs', 8.4, 'ink', mono=True) + cap('Same answers.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Or join', 9.4, 'acc', bold=True) + t(180, 56, 'DataFrame + F.broadcast(plans_df)', 8.2, 'ink', mono=True) + cap('Usually even better.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'A lookup that got slower every month',
              'The classic broadcast fix. (Real timings from our lab.)',
              'Broadcast lookups', 'Large values captured by closures are shipped with every job and task; broadcast them once, or express the lookup as a broadcast join', [e1, e2, e3, e4, e5],
              ['Slow tagging.', 'Closure shipped repeatedly.', 'Broadcast.', 'Faster.', 'Or a join.'],
              hid='scenario-lookup')

# ---- scenario 2: wrong data-quality metric
b1 = (t(180, 22, 'Bad-row alert fires', 9.4, bold=True) + t(180, 56, '“200 bad rows” · file has 100', 8.4, 'ink2') + cap('Counter is doubled.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Where is acc.add?', 9.4, bold=True) + t(180, 56, 'inside map(parse)', 8.4, 'ink', mono=True) + cap('A transformation.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'Two actions', 9.4, bold=True) + t(180, 56, 'count() and write()', 8.4, 'ink', mono=True) + cap('parse ran twice.', '', 'amber', y=150, h=34))
b4 = (t(180, 22, 'Fix', 9.4, bold=True) + t(180, 56, 'cache parsed data, or count bad rows', 8.2, 'ink2') + cap('with filter().count().', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Rule', 9.4, 'acc', bold=True) + t(180, 56, 'exact metrics come from actions', 8.4, 'ink2') + cap('Accumulators for monitoring.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'A data-quality metric that doubled',
              'Accumulators in transformations, in production. (Typical; behaviour from our lab.)',
              'Accumulator semantics', 'Updates inside transformations repeat when work is recomputed; use actions or aggregations for exact numbers', [b1, b2, b3, b4, b5],
              ['Alert doubled.', 'Update in map.', 'Two actions.', 'Cache or count.', 'Actions for exactness.'],
              hid='scenario-doublecount')

# ---- scenario 3: broadcast too big
u1 = (t(180, 22, '“Broadcast everything small”', 9.4, bold=True) + t(180, 56, 'threshold raised to 2 GB', 8.4, 'ink2') + cap('Dimension tables grew.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Driver and executors OOM', 9.4, bold=True) + t(180, 56, 'a 1.5 GB table on every executor', 8.4, 'ink2') + cap('Plus the driver builds it.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'Measure first', 9.4, bold=True) + t(180, 56, 'size in memory, not on disk', 8.4, 'ink2') + cap('Parquet is compressed.', '', 'amber', y=150, h=34))
u4 = (t(180, 22, 'Sensible threshold', 9.4, bold=True) + t(180, 56, 'tens to a few hundred MB', 8.4, 'ink2') + cap('Hint only where it helps.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Otherwise', 9.4, 'acc', bold=True) + t(180, 56, 'sort-merge join, bucketing, AQE', 8.2, 'ink2') + cap('Lessons 7.4 and 8.2.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'When broadcasting is too much',
              'The limits of broadcast joins. (Typical incident.)',
              'Broadcast limits', 'A broadcast is copied to the driver and every executor; keep broadcast tables small and let larger joins use sort-merge or AQE', [u1, u2, u3, u4, u5],
              ['Threshold too high.', 'Memory exhausted.', 'Measure.', 'Moderate limits.', 'Other strategies.'],
              hid='scenario-bigbroadcast')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Out once, back safely</h2>
  <p>Left: real outputs. Right: how values travel between driver and executors.</p>
''' + two + '''
  <p>Three live scenarios follow: a slow lookup, a doubled metric, and a broadcast that was too big.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Shared variables at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'lookups', 11, 'blue', bold=True) + t(60, 58, 'broadcast', 7.4, 'ink2'),
    '1. Reference data lookups',
    'Currency rates, product categories and city zones are broadcast to enrich billions of events.',
    ['Events', '*broadcast', 'Enriched']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'joins', 11, 'green', bold=True) + t(60, 58, 'star schema', 7.4, 'ink2'),
    '2. Fact-to-dimension joins',
    'Small dimension tables are broadcast-joined to large fact tables in warehouses on Spark.',
    ['Fact', '*broadcast join', 'Report']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'models', 11, 'violet', bold=True) + t(60, 58, 'scoring', 7.4, 'ink2'),
    '3. Model scoring',
    'A trained model is broadcast so each executor scores its partitions without reloading it.',
    ['Model', '*broadcast', 'Scores']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'metrics', 10, 'acc', bold=True) + t(60, 58, 'quality', 7.4, 'ink2'),
    '4. Pipeline metrics',
    'Accumulators count malformed records and API failures for logs and alerts.',
    ['Parse', '*accumulator', 'Alert']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'debug', 11, 'acc', bold=True) + t(60, 58, 'counters', 7.4, 'ink2'),
    '5. Debugging',
    'Temporary accumulators show how often a branch runs, a quick way to check assumptions.',
    ['Code path', '*acc.add', 'Insight']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> the closure trap in Lesson <a href="../../02-rdds/02-transformations-and-actions/">2.2</a> and caching in <a href="../01-cache-and-persist/">3.1</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
