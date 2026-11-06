import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l84_memory.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
RB = capsec(C, '##### RUN B')
def secB(a, b=None):
    i = RB.index(a); j = RB.index(b, i) if b else len(RB)
    return RB[i:j].rstrip()

def heap(x, y, w=320, res=0.1, user=0.36, uni=0.54, hi=None):
    """JVM heap bar: reserved | user | unified (execution + storage)."""
    o = box(x, y, w, 40, 'card')
    xr, xu = x + w * res, x + w * (res + user)
    o += box(x, y, w * res, 40, 'red' if hi == 'res' else 'card') + t(x + w * res / 2, y + 24, '300M', 6.6, 'ink2')
    o += box(xr, y, w * user, 40, 'amber' if hi == 'user' else 'violet') + t(xr + w * user / 2, y + 18, 'user memory', 7, 'ink', bold=True) + t(xr + w * user / 2, y + 30, 'UDF objects, Python', 6.2, 'ink2')
    o += box(xu, y, w * uni / 2, 40, 'acc' if hi == 'exec' else 'blue') + t(xu + w * uni / 4, y + 18, 'execution', 7, 'ink', bold=True) + t(xu + w * uni / 4, y + 30, 'sort, hash, agg', 6.2, 'ink2')
    o += box(xu + w * uni / 2, y, w * uni / 2, 40, 'green') + t(xu + 3 * w * uni / 4, y + 18, 'storage', 7, 'ink', bold=True) + t(xu + 3 * w * uni / 4, y + 30, 'cache, broadcast', 6.2, 'ink2')
    return o

# ---------------------------------------------------------------- story
sc_ = (heap(14, 40, 360, hi='exec') + t(194, 30, 'one executor heap (spark.executor.memory)', 7.4, 'ink2', bold=True) + t(194, 104, 'execution + storage = (heap − 300 MB) × 0.6', 7.2, 'ink2', mono=True) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured (5M wide rows)', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('3g: sort, spill 0', 'green'), ('1g: spill 736 MiB mem', 'amber'),
           ('    + 91 MiB to disk', 'amber'), ('1g, 64 parts: spill 0', 'green'),
           ('collect_list/city: OOM', 'red'), ('…per customer: OK', 'green')])))
scene_svg = scene('Spark divides each executor heap into reserved, user and unified memory; sorts, joins and aggregations use execution memory and spill to disk when it runs out. We ran the same sort and aggregation with 3 GB and 1 GB of memory and measured spill and an OutOfMemoryError.', sc_,
                  'Spill is Spark <tspan font-weight="700" class="s-acc">saving itself</tspan>; OOM is when it cannot.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Just give it more memory”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s “all orders per city” export crashed with <code>java.lang.OutOfMemoryError</code>. The on-call engineer doubled executor memory, and it crashed again the next week. The ranking job never crashed, but the UI showed gigabytes of “spill”.</p>

{scene_svg}

K> Sir, what is spill? Is it an error?
A> No. When a sort or aggregation fills its share of memory, Spark writes sorted chunks to local disk and merges them later. The job survives, only slower. <b>OOM</b> is when something must stay in memory as one piece and does not fit, like one giant list.
R> So more memory is not the answer?
A> Sometimes it is, but usually the fix is smaller pieces of work: more partitions, no giant groups, no <code>collect</code> to the driver. Today we shrink memory on purpose and watch spill and OOM happen. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Memory at three levels
L1> A kitchen counter
      <ul>
        <li>The counter is memory, the store room is disk. When the counter fills, the cook moves trays to the store room and brings them back later: slower, but dinner is served (spill).</li>
        <li>If one wedding cake is bigger than the whole counter, nothing helps: it falls (OOM).</li>
      </ul>
L2> The settings
      <ul>
        <li><code>spark.executor.memory</code> (heap), <code>spark.executor.memoryOverhead</code> (off-heap, Python workers; default 10%, min 384 MB), <code>spark.driver.memory</code>, <code>spark.driver.maxResultSize</code> (1g).</li>
        <li><code>spark.memory.fraction</code> (0.6) for unified memory, <code>spark.memory.storageFraction</code> (0.5) protected for cache.</li>
        <li>Spill shows as “Spill (Memory)” and “Spill (Disk)” in the stage page.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>Same sort: 3 GB no spill; 1 GB spilled 736 MiB (91 MiB on disk) and was slower.</li>
        <li>With 64 partitions instead of 4, the 1 GB run did not spill at all.</li>
        <li><code>collect_list</code> per city (8 groups of ~600K strings) killed the 1 GB JVM; per customer (3,999 groups) it passed.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Unified memory, spill and OOM</h2>
''' + def_block(
    'Each executor JVM heap (<code>spark.executor.memory</code>) is split into 300 MB <b>reserved memory</b>, <b>user memory</b> for user data structures, and <b>unified memory</b> of <code>(heap − 300 MB) × spark.memory.fraction</code> (0.6). Unified memory is shared between <b>execution</b> (shuffles, sorts, hash joins and aggregations) and <b>storage</b> (cached blocks, broadcast variables); execution can evict cached blocks above <code>spark.memory.storageFraction</code>. When an operator cannot acquire more execution memory it <b>spills</b> its in-memory data to local disk and merges it later. An <b>OutOfMemoryError</b> happens when an object that cannot be spilled (a single huge row or group, a broadcast table, collected results on the driver) or non-heap usage exceeds the limits; containers can also be killed for exceeding <code>memoryOverhead</code>.',
    'Spark gives each executor a heap and uses about 60% of it (after 300 MB) for its own work and cache. When a sort or aggregation runs out of that space, it writes parts to disk and continues: that is spill, slow but safe. An out-of-memory error happens when something must fit in memory at once and does not.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Executor memory', 'JVM heap per executor.'),
    ('Memory overhead', 'Off-heap: Python, buffers.'),
    ('Unified memory', '(heap − 300 MB) × 0.6.'),
    ('Execution memory', 'Sorts, joins, aggregations.'),
    ('Storage memory', 'Cache and broadcasts.'),
    ('Spill (memory)', 'Size of data before spilling.'),
    ('Spill (disk)', 'Size written to disk (compressed).'),
    ('OOM', 'OutOfMemoryError: heap exhausted.'),
]) + '''

  <h3>Where memory goes</h3>
''' + table(['Region', 'Size (8 GB heap)', 'Used by', 'When full'], [
    ['Reserved', '300 MB', 'Spark internals', 'n/a'],
    ['User', '(8 GB − 300 MB) × 0.4 ≈ 3.1 GB', 'Your objects, UDF state', 'OOM'],
    ['Execution', 'up to ≈ 4.6 GB (shared)', 'Sort, hash join, aggregation', 'Spill to disk'],
    ['Storage', '≥ 2.3 GB protected (shared)', 'cache(), broadcast', 'Evict blocks'],
    ['Overhead (off-heap)', 'max(384 MB, 10%)', 'Python workers, netty, Arrow', 'Container killed'],
], minw=640) + lv + '''
EXAM> “Difference between spill and OOM?” Spill: an operator (sort, aggregation, join) ran out of execution memory and wrote data to local disk to continue; the job succeeds but slower, visible as Spill (Memory/Disk) in the stage page. OOM: memory needed at once exceeded what is available, e.g. a huge group in <code>collect_list</code>, a large broadcast, or <code>collect()</code> on the driver; fix the cause (more partitions, smaller groups, no collect) before adding memory.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Common OOMs and their fixes</h2>
''' + table(['Symptom', 'Usual cause', 'Fix'], [
    ['Driver OOM after <code>collect()</code> / <code>toPandas()</code>', 'Result too big for the driver', 'Write to storage; limit; aggregate first (Lesson 4.6)'],
    ['Driver OOM in a join', 'Broadcast of a big side', 'Remove hint / lower threshold (Lesson 8.2)'],
    ['Executor OOM in one task', 'Skewed key, giant group (<code>collect_list</code>)', 'Salt, smaller groups, avoid lists (8.3)'],
    ['Heavy spill, slow stage', 'Too few partitions for the data', 'More shuffle partitions / AQE'],
    ['“Container killed … exceeding memory limits”', 'Off-heap: Python UDFs, Arrow, buffers', 'Raise <code>memoryOverhead</code>; fewer cores per executor'],
], minw=640) + '''
WARN> Doubling <code>spark.executor.memory</code> hides the problem until the data doubles again. A single group that must be one Java object (one list, one row, one broadcast) grows with your data and will not fit at some point. Look for the <b>one big thing</b> first. Also note: bigger heaps mean longer garbage-collection pauses; executors of more than ~32–64 GB are rarely a good idea.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Shrinking memory on purpose</h2>
  <p>All outputs are real: PySpark 4.3.0, <code>local[2]</code> (in local mode the driver JVM is also the executor, so <code>spark.driver.memory</code> is the heap), AQE off, 4 shuffle partitions. 5,000,000 orders, each with an extra 100-character string column. Spill numbers come from the REST API stage metrics.</p>
''' + stepper([
    ('Step 1 · How big is unified memory?',
     code('python', 'l84_memory.py', 'heap = sc._jvm.java.lang.Runtime.getRuntime().maxMemory() / 2**20\nprint(f"JVM heap {heap:.0f} MiB -> unified pool ~ (heap - 300) * 0.6 = {(heap-300)*0.6:.0f} MiB")', sec('##### RUN A', '== 1)')),
     'With 3 GB the pool for execution and storage is about <b>1.6 GB</b>. With 1 GB it is only <b>434 MiB</b>, shared by 2 concurrent tasks. That is the budget every sort and aggregation competes for.'),
    ('Step 2 · The same sort at 3 GB and 1 GB',
     code('python', 'l84_memory.py', 'wide = o.withColumn("pad", F.repeat(F.lit("x"), 100))\nrun("orderBy amount (4 partitions)", sink(wide.orderBy("amount")))', '# driver 3g\n' + sec('== 1) global sort', '== 2)') + '\n# driver 1g\n' + secB('== 1)', '== 2)')),
     'At 3 GB: no spill. At 1 GB the same 4-partition sort <b>spilled 736 MiB</b> from memory, written as <b>91 MiB</b> on disk (spill files are compressed, so “memory” is always bigger than “disk”), and took 10.16 s instead of 9.09 s. With <b>64 partitions</b> each task sorted a 16x smaller piece, which fit: <b>no spill</b> even at 1 GB, and faster (6.54 s).'),
    ('Step 3 · An OutOfMemoryError',
     code('python', 'l84_memory.py', 'wide.groupBy("city").agg(F.collect_list("pad").alias("l")) \\\n    .write.format("noop").mode("overwrite").save()', '# driver 1g\n' + secB('== 2)', '== 3)')),
     'At 3 GB this passed. At 1 GB the JVM died with <b>Java heap space</b>, and Python lost its connection to it. Each city’s list (500K–1M strings of 100 characters, over 100 MB as Java objects) must exist as <b>one</b> value in one task, so it cannot be spilled. More partitions would not help: a group is never split.'),
    ('Step 4 · Fixing it without more memory',
     code('python', 'l84b_fix.py', 'run("count + sum per city (no list)", sink(wide.groupBy("city").agg(F.count("*"), F.sum("amount"))))\nrun("collect_list per customer",      sink(wide.groupBy("customer_id").agg(F.collect_list("pad"))))\nrun("top-5 per city via window",      sink(o.withColumn("r", F.row_number().over(w)).filter("r<=5")))', sec('== 3)')),
     'Same 1 GB. Asking what is actually needed fixed it: <b>count and sum</b> need no list (3.44 s, no spill). Lists per <b>customer</b> are 3,999 small groups, so they spilled safely (192 MiB) and finished. And “top 5 per city” is a window plus a filter, which spills instead of crashing. Memory was the symptom; the giant group was the cause.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('3g heap -> unified ~1663 MiB', G), ('1g heap -> unified ~434 MiB', Y)], size=7.6),
    term([('3g sort : spill 0', G), ('1g sort : spill 736 MiB mem', Y), ('          91.4 MiB disk', Y), ('1g, 64 p: spill 0, 6.54 s', G)], size=7.4),
    term([('collect_list per city', W), ('java.lang.OutOfMemoryError:', RD), ('  Java heap space', RD)], size=7.6),
    term([('sum per city   : 3.44 s, no spill', G), ('list per cust. : spill 192 MiB, OK', G), ('top-5 window   : spill 304 MiB, OK', G)], size=7.2),
]
B1 = [
    t(180, 14, 'One executor heap', 9.4, bold=True) + heap(20, 46) + t(180, 110, 'unified = (heap − 300 MB) × 0.6', 7.4, 'ink2', mono=True) + cap('Execution and storage share it.', '', 'blue', y=144, h=30),
    t(180, 14, 'Spill: sort in runs', 9.4, bold=True) + flow([('fill memory', 'sort run', 'blue'), ('write run', 'local disk', 'amber'), ('merge runs', 'output', 'green')], y=50, w=96, gap=16) + cap('Slower, but it finishes.', '', 'amber', y=144, h=30),
    t(180, 14, 'OOM: one thing too big', 9.4, bold=True) + heap(20, 46, hi='exec') + box(150, 40, 200, 52, 'red', rx=4) + t(250, 70, 'one city list > memory', 7.8, 'ink', bold=True) + cap('A group cannot be split or spilled.', '', 'red', y=144, h=30),
    t(180, 14, 'Make the pieces smaller', 9.4, bold=True) + flow([('more', 'partitions', 'green'), ('smaller', 'groups', 'green'), ('no', 'collect', 'green')], y=50, w=96, gap=16) + cap('Fix the cause, then size memory.', '', 'green', y=144, h=30),
]
see_caps = ['Memory budgets.', 'Spill.', 'OutOfMemoryError.', 'Fixes at 1 GB.']
behind_caps = ['Unified memory model.', 'External sort.', 'Unspillable objects.', 'Smaller units of work.']
two = anim_two('Memory, spill and OOM', 'What fits, what spills, what crashes', 'Real lab outputs', 'What Spark does', see, B1, see_caps, behind_caps)

e1 = (t(180, 22, 'Stage page: Spill 40 GB', 9.4, bold=True) + t(180, 56, 'shuffle read 6 GB, 200 tasks', 8.4, 'ink2') + cap('≈ 200 MB spilled per task.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Tasks too big for memory', 9.4, bold=True) + t(180, 56, 'each sorts more than it can hold', 8.4, 'ink2') + cap('Spill = disk I/O.', '', 'amber', y=150, h=34))
e3 = (t(180, 22, 'Raise shuffle partitions', 9.4, bold=True) + t(180, 56, '200 → 1,000 (or AQE advisory)', 8.4, 'ink2') + cap('4 → 64 removed spill in our lab.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Spill gone, stage 2x faster', 9.4, bold=True) + t(180, 56, 'same memory, same cluster', 8.4, 'ink2') + cap('Smaller pieces.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Some spill is fine', 9.4, 'acc', bold=True) + t(180, 56, 'watch spill ≫ shuffle size', 8.4, 'ink2') + cap('Tune when it dominates.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Gigabytes of spill',
              'Reducing spill with partitions. (Typical; pattern from our lab.)',
              'Spill', 'Heavy spill usually means tasks are too big; more partitions make each fit in memory', [e1, e2, e3, e4, e5],
              ['Spill.', 'Too big.', 'Partitions.', 'Faster.', 'Balance.'],
              hid='scenario-spill')
b1 = (t(180, 22, '“All orders per city” export', 9.4, bold=True) + t(180, 56, 'groupBy(city).agg(collect_list)', 8.2, 'ink', mono=True) + cap('One row per city.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Executor OOM, retried 4x', 9.4, bold=True) + t(180, 56, 'Java heap space', 8.4, 'red', mono=True) + cap('Job fails.', '', 'red', y=150, h=34))
b3 = (t(180, 22, 'Memory doubled', 9.4, bold=True) + t(180, 56, 'works… until next month', 8.4, 'ink2') + cap('Data keeps growing.', '', 'amber', y=150, h=34))
b4 = (t(180, 22, 'Write partitioned files instead', 9.4, bold=True) + t(180, 56, 'write.partitionBy("city")', 8.4, 'ink', mono=True) + cap('One folder per city, no list.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Same output, any size', 9.4, 'acc', bold=True) + t(180, 56, 'no giant objects in memory', 8.4, 'ink2') + cap('Fixed for good.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'The list that kept growing',
              'OOM from giant groups. (Typical; OOM reproduced in our lab.)',
              'Giant group', 'collect_list on a few keys creates objects too big for memory; write partitioned output instead', [b1, b2, b3, b4, b5],
              ['Export.', 'OOM.', 'More memory.', 'Partition.', 'Fixed.'],
              hid='scenario-list')
u1 = (t(180, 22, 'Pandas UDF job killed', 9.4, bold=True) + t(180, 56, 'exceeding memory limits (YARN/K8s)', 8.2, 'ink2') + cap('No Java OOM in logs.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'It is off-heap memory', 9.4, bold=True) + t(180, 56, 'Python workers + Arrow batches', 8.4, 'ink2') + cap('Counted in overhead.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'Raise memoryOverhead', 9.4, bold=True) + t(180, 56, 'spark.executor.memoryOverhead=2g', 8.2, 'ink', mono=True) + cap('Not executor.memory.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Smaller Arrow batches', 9.4, bold=True) + t(180, 56, 'arrow.maxRecordsPerBatch', 8.4, 'ink', mono=True) + cap('Less per worker.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Fewer cores per executor', 9.4, 'acc', bold=True) + t(180, 56, '= fewer Python workers', 8.4, 'ink2') + cap('Memory per task rises.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Killed by the container, not the JVM',
              'Off-heap memory and Python. (Typical.)',
              'Overhead', 'Python and Arrow memory is off-heap; raise memoryOverhead or reduce batch size', [u1, u2, u3, u4, u5],
              ['Killed.', 'Off-heap.', 'Overhead.', 'Batches.', 'Cores.'],
              hid='scenario-overhead')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>What fits, what spills, what crashes</h2>
  <p>Left: real outputs. Right: Spark’s memory model.</p>
''' + two + '''
  <p>Three live scenarios follow: heavy spill, a growing list, and a container killed for off-heap memory.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Memory tuning at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'spill', 12, 'blue', bold=True) + t(60, 58, 'review', 7.4, 'ink2'),
    '1. Spill reviews',
    'Stages where spill exceeds shuffle size get more partitions or a larger advisory size.',
    ['Spill metric', '*more partitions', 'No spill']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'sizing', 11, 'green', bold=True) + t(60, 58, 'executors', 7.4, 'ink2'),
    '2. Executor sizing',
    'Platform teams pick 4–5 cores and 16–32 GB per executor so each task gets enough memory.',
    ['Node', '*cores + memory', 'Executor shape']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'driver', 11, 'violet', bold=True) + t(60, 58, 'safety', 7.4, 'ink2'),
    '3. Driver protection',
    'maxResultSize stops accidental collects from killing shared notebooks.',
    ['collect()', '*maxResultSize', 'Clear error']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'Python', 11, 'acc', bold=True) + t(60, 58, 'overhead', 7.4, 'ink2'),
    '4. Python-heavy jobs',
    'Pandas UDF jobs set memoryOverhead explicitly instead of relying on the 10% default.',
    ['Pandas UDF', '*overhead 2–4 GB', 'Stable']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'cache', 12, 'acc', bold=True) + t(60, 58, 'budget', 7.4, 'ink2'),
    '5. Cache budgets',
    'Cached tables are checked in the Storage tab so they do not starve execution memory.',
    ['cache()', '*Storage tab', 'Room for joins']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> cache and storage levels in <a href="../../03-persistence-and-shared-variables/01-cache-and-persist/">3.1</a>, collect and the driver in <a href="../../04-dataframes/06-collect-topandas-and-arrow/">4.6</a>, skew in <a href="../03-data-skew-and-salting/">8.3</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
