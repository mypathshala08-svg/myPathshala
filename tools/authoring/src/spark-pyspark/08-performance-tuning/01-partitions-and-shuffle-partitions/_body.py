import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l81_partitions.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)

def pbars(x, y, sizes, tone='card', label='', hot=45):
    o = t(x, y - 6, label, 7.2, 'ink2', anchor='start', bold=True) if label else ''
    for k, s in enumerate(sizes):
        o += box(x + k * 14, y + (60 - s), 10, max(s, 1), tone if s < hot else 'acc', rx=2)
    return o

# ---------------------------------------------------------------- story
sc_ = (pbars(14, 40, [3] * 12, 'card', '2,000 tiny tasks') + arrow(190, 70, 214, 70, 'ink3', 1.1) + pbars(224, 40, [30, 30, 30, 30, 30, 30, 30, 30], 'green', '8 right-sized') +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured (5M orders)', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('2000 small files: 4.06 s', 'red'), ('8 normal files : 0.20 s', 'green'),
           ('shuffle=2000   : 8.13 s', 'red'), ('shuffle=16     : 1.82 s', 'green'),
           ('shuffle=200+AQE: 8 tasks', 'green'), ('city key: 6 of 8 used', 'amber')])))
scene_svg = scene('Partitions decide how many tasks Spark runs. We measured the same 5 million orders read from 2,000 small files versus 8 normal files, and a groupBy with 1 to 2,000 shuffle partitions.', sc_,
                  'Too few partitions waste cores; <tspan font-weight="700" class="s-acc">too many waste time</tspan> on scheduling.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Set shuffle partitions to 2000, it’s a big job”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s nightly revenue job got slower after a new engineer set <code>spark.sql.shuffle.partitions=2000</code> “for safety” and another job left 2,000 tiny Parquet files behind. Nothing failed; everything just crawled.</p>

{scene_svg}

K> Sir, more partitions means more parallel work, so it should be faster, right?
A> Only up to the number of cores. Every partition is a <b>task</b>, and every task has a fixed cost: scheduling, opening files, writing shuffle blocks. Past a point you pay that cost thousands of times for nothing.
R> So how do we pick the number?
A> Today we measure it: input partitions from file sizes, the small-files problem, shuffle partitions from 1 to 2,000, and <code>repartition</code> vs <code>coalesce</code>. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Partitions at three levels
L1> Cutting a big pizza
      <ul>
        <li>Four friends, one pizza: four slices is perfect. One slice means three friends wait; 2,000 slices means everyone spends the evening picking crumbs.</li>
        <li>A partition is a slice of data, a task is one friend eating it, a core is one friend.</li>
      </ul>
L2> The settings
      <ul>
        <li>Reading files: <code>spark.sql.files.maxPartitionBytes</code> (128 MB) and <code>spark.sql.files.openCostInBytes</code> (4 MB).</li>
        <li>After a shuffle: <code>spark.sql.shuffle.partitions</code> (200), merged by AQE (Lesson 7.4).</li>
        <li>In code: <code>repartition(n)</code>, <code>repartition(n, col)</code>, <code>coalesce(n)</code>, <code>df.rdd.getNumPartitions()</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>Same data: 2,000 small files took 4.06 s, 8 normal files 0.20 s (64 vs 5 tasks).</li>
        <li>groupBy with AQE off: 16 partitions 1.82 s, 200 partitions 2.50 s, 2,000 partitions 8.13 s.</li>
        <li><code>repartition(8, "city")</code> filled only 6 partitions, unevenly (0.5M to 1.5M rows).</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Partitions and shuffle partitions</h2>
''' + def_block(
    'A <b>partition</b> is a chunk of a DataFrame processed by one <b>task</b> on one executor core. For file sources, Spark packs files into input partitions of at most <code>spark.sql.files.maxPartitionBytes</code> (128 MB by default), counting each file as at least <code>spark.sql.files.openCostInBytes</code> (4 MB) and spreading small inputs across <code>defaultParallelism</code>. After a wide transformation (groupBy, join, orderBy, window), the data is redistributed into <code>spark.sql.shuffle.partitions</code> partitions (200 by default), which Adaptive Query Execution can coalesce at run time. <code>repartition()</code> shuffles to a new number (optionally by column hash); <code>coalesce()</code> merges partitions without a shuffle and can only reduce the count.',
    'Spark splits data into partitions, and each partition becomes one task on one core. File reading decides the first partitions; every shuffle creates a new set (200 by default). Too few partitions leave cores idle or make tasks huge; too many add overhead for each tiny task.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Partition', 'One chunk of data = one task.'),
    ('Task', 'Unit of work on one core.'),
    ('defaultParallelism', 'Total cores (4 in our lab).'),
    ('maxPartitionBytes', 'Max input split size (128 MB).'),
    ('openCostInBytes', 'Fake cost per file (4 MB).'),
    ('shuffle.partitions', 'Partitions after a shuffle (200).'),
    ('repartition', 'Shuffle to n partitions.'),
    ('coalesce', 'Merge partitions, no shuffle.'),
]) + '''

  <h3>Where partition counts come from</h3>
''' + table(['Stage', 'Decided by', 'Lab result'], [
    ['Reading files', 'maxPartitionBytes, openCostInBytes, file count, cores', '34.6 MiB → 4 partitions; 4 MB → 16'],
    ['Many small files', 'One task can pack several files', '2,000 files → 63 partitions, 4.06 s'],
    ['After a shuffle', 'spark.sql.shuffle.partitions (+ AQE)', '200 → 204 tasks; with AQE → 8'],
    ['In your code', 'repartition / coalesce', 'repartition(8) = 8 × 625,000 rows'],
], minw=620) + lv + '''
EXAM> “How do you choose the number of partitions?” Aim for tasks of roughly 100–200 MB of input (or shuffle data) each and at least 2–3 tasks per core. Keep input files near 128 MB–1 GB, set <code>spark.sql.shuffle.partitions</code> high enough for the largest data and let AQE coalesce, use <code>coalesce</code> to reduce partitions before writing and <code>repartition</code> to increase them or redistribute by key.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>repartition vs coalesce</h2>
''' + table(['Method', 'Shuffle?', 'Can increase?', 'Result in our lab'], [
    ['<code>repartition(8)</code>', 'Yes (round-robin)', 'Yes', '8 equal partitions of 625,000'],
    ['<code>repartition(8, "city")</code>', 'Yes (hash of city)', 'Yes', 'only 6 used, 0.5M–1.5M rows'],
    ['<code>repartitionByRange(8, "amount")</code>', 'Yes (sampled ranges)', 'Yes', 'sorted ranges (Lesson 8.3)'],
    ['<code>coalesce(2)</code>', 'No', 'No', '2 × 2,500,000'],
    ['<code>spark.sql.shuffle.partitions</code>', 'n/a', 'n/a', 'every groupBy/join/sort'],
], minw=640) + '''
WARN> <code>coalesce(1)</code> before a write looks harmless, but it also pulls the <b>work before it</b> into one task, because coalesce does not add a stage boundary. On a real cluster with many cores that turns a parallel job into a single-threaded one. If you need one output file after heavy work, prefer <code>repartition(1)</code> (one extra shuffle, but the heavy part stays parallel).
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Measuring partition counts</h2>
  <p>All outputs are real: PySpark 4.3.0, <code>local[4]</code> on a machine with 2 physical CPUs, 5,000,000 orders in 8 Parquet files (34.6 MiB). Tasks are counted from the Spark REST API; every timing is a warm run.</p>
''' + stepper([
    ('Step 1 · Input partitions follow file size',
     code('python', 'l81_partitions.py', 'print(sc.defaultParallelism, spark.conf.get("spark.sql.files.maxPartitionBytes"))\nfor mpb in ("128MB", "16MB", "4MB"):\n    spark.conf.set("spark.sql.files.maxPartitionBytes", mpb)\n    print(mpb, spark.read.parquet(P).rdd.getNumPartitions())', sec('files:', '== 2)')),
     'With 128 MB and 16 MB we still got <b>4</b> partitions: Spark also divides small inputs across the 4 cores (34.6 MiB / 4 ≈ 8.7 MB per split), so the cap did not matter. Only when the cap fell below that (4 MB) did the count rise to <b>16</b>.'),
    ('Step 2 · The small-files problem',
     code('python', 'l81_partitions.py', 'spark.read.parquet(P).repartition(2000).write.parquet(small)   # 2,000 files\nd = spark.read.parquet(small)\nrun("count over 2000 small files", lambda: d.agg(F.sum("amount")).collect())\nrun("count over 8 normal files",   lambda: big.agg(F.sum("amount")).collect())', sec('== 2)', '== 3)')),
     'Exactly the same rows. Spark packed the 2,000 files into <b>63</b> partitions (each file is charged 4 MB of “open cost”), but still had to open 2,000 files and read 2,000 footers: <b>4.06 s vs 0.20 s</b>, 20x slower. On S3 or ADLS each open is a network request, so the gap is bigger. Fix it at write time (Lesson 5.3) or compact the files.'),
    ('Step 3 · Shuffle partitions from 1 to 2,000',
     code('python', 'l81_partitions.py', 'spark.conf.set("spark.sql.adaptive.enabled", "false")   # see the raw effect\nq = lambda: big.groupBy("customer_id", "order_date").agg(F.sum("amount")) \\\n                .write.format("noop").mode("overwrite").save()\nfor n in (1, 4, 16, 200, 2000):\n    spark.conf.set("spark.sql.shuffle.partitions", n); q(); run(f"... {n}", q)', sec('== 3)', '== 4)')),
     'A U-shaped curve. <b>1</b> partition: one core does all the reduce work (2.55 s). <b>4–16</b>: best (1.82 s). <b>200</b>: 204 tasks, mostly tiny (2.50 s). <b>2,000</b>: 2,004 tasks and 2,000 shuffle files per map task: <b>8.13 s</b>, 4.5x slower than the best. With AQE on, the 200 were coalesced to <b>8</b> tasks automatically.'),
    ('Step 4 · How rows land in partitions',
     code('python', 'l81_partitions.py', 'count = lambda d: sorted(d.groupBy(F.spark_partition_id()).count().rdd.map(lambda x: x[1]).collect())\nprint(count(big.repartition(8)))\nprint(count(big.repartition(8, "city")))\nprint(count(big.coalesce(2)))', sec('== 4)', '== 5)')),
     '<code>repartition(8)</code> is round-robin: perfectly even. <code>repartition(8, "city")</code> hashes 8 cities into 8 buckets, but two cities collided and two buckets stayed <b>empty</b>: 6 partitions, from 0.5M to 1.5M rows. Hash partitioning on a low-cardinality column is uneven by nature. <code>coalesce(2)</code> just glued neighbours together.'),
    ('Step 5 · coalesce(1) vs repartition(1)',
     code('python', 'l81_partitions.py', 'h = lambda d: d.select(F.sha2(F.col("order_id").cast("string"), 256))\nrun("4 partitions",       lambda: sink(h(big)))\nrun("after coalesce(1)",  lambda: sink(h(big.coalesce(1))))\nrun("after repartition(1)", lambda: sink(h(big.repartition(1))))', sec('== 5)')),
     'Look at the <b>task counts</b>: <code>coalesce(1)</code> ran everything as <b>1 task</b>; <code>repartition(1)</code> ran 4 parallel tasks for the hashing and then 1 to gather (5 tasks). Here coalesce was not slower, because the hash is cheap and our machine has only 2 physical CPUs. With an expensive step on a 100-core cluster, that single task is the whole job. Read the task count, not one timing.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('128MB: 4 partitions', W), ('16MB : 4 partitions', W), ('4MB  : 16 partitions', G)], size=7.6),
    term([('2000 files -> 63 partitions', Y), ('small files: 4.06 s, 64 tasks', RD), ('8 files    : 0.20 s, 5 tasks', G)], size=7.4),
    term([('shuffle=1   : 2.55 s', Y), ('shuffle=16  : 1.82 s', G), ('shuffle=2000: 8.13 s', RD), ('200 + AQE   : 8 tasks', G)], size=7.4),
    term([('repartition(8): 8 x 625000', G), ('by city: 6 used, 0.5M..1.5M', Y), ('coalesce(2): 2 x 2500000', W)], size=7.4),
]
B1 = [
    t(180, 14, 'Files → input partitions', 9.4, bold=True) + flow([('8 files', '34.6 MiB', 'blue'), ('split', '≈8.7 MB', 'violet'), ('4 tasks', '1 per core', 'green')], y=50, w=96, gap=16) + cap('min(128 MB, size ÷ cores) decides.', '', 'green', y=144, h=30),
    t(180, 14, 'Each file has a cost', 9.4, bold=True) + t(90, 34, '2,000 small files', 7.4, 'ink2', bold=True) + ''.join(box(20 + (k % 14) * 10, 42 + (k // 14) * 10, 7, 7, 'acc', rx=1) for k in range(84)) + t(90, 136, '2,000 opens + footers', 7, 'red') + t(270, 34, '8 normal files', 7.4, 'ink2', bold=True) + ''.join(box(214 + (k % 4) * 28, 46 + (k // 4) * 34, 22, 28, 'green', rx=2) for k in range(8)) + t(270, 136, '8 opens', 7, 'green') + cap('Opening files dominates.', '', 'amber', y=144, h=30),
    t(180, 14, 'The U-curve', 9.4, bold=True) + pbars(30, 50, [28, 20, 18, 26, 60], 'green', '1 · 4 · 16 · 200 · 2000', hot=50) + t(240, 90, 'best near cores × 2–4', 7.4, 'ink2') + cap('Too few and too many both hurt.', '', 'amber', y=144, h=30),
    t(180, 14, 'Hash on a few values', 9.4, bold=True) + pbars(30, 50, [17, 17, 17, 33, 33, 50, 1, 1], 'green', 'repartition(8, city)', hot=48) + cap('Collisions and empty buckets.', '', 'amber', y=144, h=30),
]
see_caps = ['Input partitions.', '2,000 small files.', 'Shuffle partitions.', 'Rows per partition.']
behind_caps = ['How files are split.', 'Per-file overhead.', 'Overhead vs parallelism.', 'Hash partitioning skew.']
two = anim_two('Partitions', 'How many tasks, and why', 'Real lab outputs', 'What Spark does', see, B1, see_caps, behind_caps)

e1 = (t(180, 22, 'Nightly job: 2,000 partitions', 9.4, bold=True) + t(180, 56, 'set “for safety”', 8.4, 'ink2') + cap('2,004 tasks per groupBy.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'UI: tasks take 20 ms each', 9.4, bold=True) + t(180, 56, 'scheduler busy, cores idle', 8.4, 'ink2') + cap('Overhead > work.', '', 'amber', y=150, h=34))
e3 = (t(180, 22, 'Size the shuffle', 9.4, bold=True) + t(180, 56, 'shuffle GB ÷ 128 MB per task', 8.4, 'ink2') + cap('Upper bound, not a guess.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Turn AQE coalescing on', 9.4, bold=True) + t(180, 56, '200 → 8 tasks in our lab', 8.4, 'ink2') + cap('Small days handled.', '', 'green', y=150, h=34))
e5 = (t(180, 22, '8.13 s → 1.82 s', 9.4, 'acc', bold=True) + t(180, 56, 'same data, same code', 8.4, 'ink2') + cap('4.5x faster.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Undoing “2,000 for safety”',
              'Right-sizing shuffle partitions. (Typical; numbers from our lab.)',
              'Shuffle partitions', 'Size shuffle partitions from data volume and let AQE coalesce them', [e1, e2, e3, e4, e5],
              ['Too many.', 'Overhead.', 'Size it.', 'AQE.', 'Faster.'],
              hid='scenario-shuffle')
b1 = (t(180, 22, 'Streaming job writes every minute', 9.4, bold=True) + t(180, 56, '1,440 files a day per partition', 8.4, 'ink2') + cap('Small files pile up.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Reports read 2,000 files', 9.4, bold=True) + t(180, 56, '4.06 s vs 0.20 s in our lab', 8.4, 'ink2') + cap('20x slower for the same rows.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'Nightly compaction job', 9.4, bold=True) + t(180, 56, 'read → repartition(n) → write', 8.4, 'ink', mono=True) + cap('Files near 128 MB–1 GB.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Or a table format', 9.4, bold=True) + t(180, 56, 'Delta OPTIMIZE / Iceberg rewrite', 8.4, 'ink2') + cap('Compaction built in.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Monitor file counts', 9.4, 'acc', bold=True) + t(180, 56, 'alert if avg file < 32 MB', 8.4, 'ink2') + cap('Catch it early.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'The 2,000-file table',
              'Small files and compaction. (Typical; timings from our lab.)',
              'Small files', 'Compact small files so each task reads a reasonable amount of data', [b1, b2, b3, b4, b5],
              ['Many files.', 'Slow reads.', 'Compact.', 'Formats.', 'Monitor.'],
              hid='scenario-smallfiles')
u1 = (t(180, 22, 'Heavy enrichment, then one file', 9.4, bold=True) + t(180, 56, '.coalesce(1).write.csv(...)', 8.4, 'ink', mono=True) + cap('Partner wants a single CSV.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'UI: 1 task for the whole job', 9.4, bold=True) + t(180, 56, '99 cores idle for 40 minutes', 8.4, 'ink2') + cap('coalesce pulled work into 1 task.', '', 'red', y=150, h=34))
u3 = (t(180, 22, 'Use repartition(1)', 9.4, bold=True) + t(180, 56, 'heavy part parallel, then gather', 8.4, 'ink2') + cap('5 tasks vs 1 in our lab.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Or write many, merge after', 9.4, bold=True) + t(180, 56, 'only small final outputs in 1 file', 8.4, 'ink2') + cap('One file is a bottleneck.', '', 'amber', y=150, h=34))
u5 = (t(180, 22, 'Rule of thumb', 9.4, 'acc', bold=True) + t(180, 56, 'check task counts per stage', 8.4, 'ink2') + cap('Not just total time.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'The coalesce(1) trap',
              'coalesce vs repartition before a write. (Typical; task counts from our lab.)',
              'coalesce(1)', 'coalesce(1) runs upstream work in one task; repartition(1) keeps it parallel', [u1, u2, u3, u4, u5],
              ['One file.', 'One task.', 'repartition.', 'Alternatives.', 'Check tasks.'],
              hid='scenario-coalesce1')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>How many tasks, and why</h2>
  <p>Left: real outputs. Right: what Spark does with partitions.</p>
''' + two + '''
  <p>Three live scenarios follow: too many shuffle partitions, too many small files, and the coalesce(1) trap.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Partition tuning at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'ETL', 12, 'blue', bold=True) + t(60, 58, 'nightly', 7.4, 'ink2'),
    '1. Nightly ETL',
    'Shuffle partitions sized from the largest day’s shuffle data; AQE merges them on quiet days.',
    ['Shuffle size', '*÷ 128 MB', 'Partition count']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'lake', 12, 'green', bold=True) + t(60, 58, 'compaction', 7.4, 'ink2'),
    '2. Data lake compaction',
    'Scheduled jobs rewrite small files into large ones so every reader gets faster.',
    ['Small files', '*repartition + write', 'Big files']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'by key', 11, 'violet', bold=True) + t(60, 58, 'partitionBy', 7.4, 'ink2'),
    '3. Partitioned writes',
    'repartition by the partition column before partitionBy keeps one file per folder instead of one per task.',
    ['repartition(col)', '*partitionBy(col)', 'Few files']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'API', 12, 'acc', bold=True) + t(60, 58, 'parallel', 7.4, 'ink2'),
    '4. Calling slow APIs',
    'Increase partitions before a mapPartitions step that calls an external service, to raise concurrency.',
    ['Few partitions', '*repartition(64)', 'More calls in flight']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'export', 11, 'acc', bold=True) + t(60, 58, 'one file', 7.4, 'ink2'),
    '5. Single-file exports',
    'Small final results are written with repartition(1) after the heavy work is done.',
    ['Heavy work', '*repartition(1)', 'One CSV']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> partitions and the shuffle in <a href="../../02-rdds/04-narrow-vs-wide-and-the-shuffle/">2.4</a>, small files in <a href="../../05-reading-and-writing-data/03-writing-data-and-small-files/">5.3</a>, AQE in <a href="../../07-spark-sql/04-adaptive-query-execution/">7.4</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
