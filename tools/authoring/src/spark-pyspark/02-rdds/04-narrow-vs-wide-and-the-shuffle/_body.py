import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
def has(n, *keys):
    return '\n'.join(l for l in capf(n).split('\n') if any(k in l for k in keys))
def job(*ids):
    return '\n'.join(l.split('  |')[0].replace('stages ', 'stages ').rstrip() + '  |' + l.split('  |')[1] for l in capf('l24_rest.txt').split('\n') if any(l.startswith(f'job {i:2} ') for i in ids))

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

def deps(kind='narrow', hi=False):
    """3 parent partitions → 3 child partitions; narrow = straight, wide = all-to-all"""
    o = ''
    for k in range(3):
        o += opbox(20, 24 + k * 30, f'P{k}', '', 'blue', 60, 22) + opbox(280, 24 + k * 30, f'C{k}', '', 'green', 60, 22)
    if kind == 'narrow':
        o += ''.join(arrow(82, 35 + k * 30, 278, 35 + k * 30, 'acc', 1.4) for k in range(3))
        o += t(180, 22, 'one parent partition each', 7, 'ink2')
    else:
        o += ''.join(arrow(82, 35 + a * 30, 278, 35 + b * 30, 'red' if hi else 'acc', 1) for a in range(3) for b in range(3))
        o += t(180, 22, 'every child needs every parent', 7, 'ink2')
    return o

# ---------------------------------------------------------------- story
sc = (deps('narrow') +
      box(410, 12, 222, 136, 'card') + t(521, 30, 'Shuffle written, measured', 8.6, bold=True) +
      ''.join(t(422, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
          ('map + filter     :      0 KiB', 'green'), ('groupByKey       :  355.6 KiB', 'red'), ('reduceByKey      :  106.7 KiB', 'green'),
          ('repartition(2)   : 11,545 KiB', 'red'), ('coalesce(2)      :      0 KiB', 'green'), ('co-partitioned join:   0 KiB', 'green')])))
scene_svg = scene('Narrow transformations let each output partition be computed from one input partition, on the same executor. Wide transformations need data from every partition, so Spark shuffles it across the network. The numbers show shuffle bytes written by real jobs.', sc,
                  'The shuffle is where Spark spends its <tspan font-weight="700" class="s-acc">network, disk and time</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Two lines, same answer, twice the time”</h2>
  <div class="story">
    <p class="narration">Kabir wrote TiffinGo’s revenue-per-customer job with <code>groupByKey().mapValues(sum)</code>. Riya wrote the same thing with <code>reduceByKey(add)</code>. Both print 2,000 customers with identical totals. Kabir’s takes twice as long and his team lead keeps saying one word in the review: “shuffle”.</p>

{scene_svg}

K> Sir, both versions group by customer. Why is mine slower?
A> Grouping needs every order of a customer in one place, but those orders sit in different partitions on different executors. Moving them is the <b>shuffle</b>: write to local disk, send over the network, read back. <code>reduceByKey</code> adds up inside each partition first, so far less data moves. <code>groupByKey</code> sends the values as they are.
R> So which operations shuffle?
A> The <b>wide</b> ones. Today we run each kind on 2,000,000 TiffinGo order amounts on our cluster and read the shuffle bytes from the Spark UI: groupByKey vs reduceByKey, repartition vs coalesce, and a join that needs no shuffle at all. All numbers are real (Spark 4.3.0, two executors).
  </div>
</section>
'''

lv = '''
LEVELS> Narrow, wide and shuffle at three levels
L1> Sorting post in a post office
      <ul>
        <li><b>Narrow</b>: each clerk stamps the letters in their own tray. No one moves.</li>
        <li><b>Wide</b>: letters must be grouped by city, so every clerk sends some letters to every other clerk. That exchange is the shuffle.</li>
        <li>Counting letters per city in your own tray first, and sending only the counts, is much faster (reduceByKey).</li>
      </ul>
L2> The rules
      <ul>
        <li><b>Narrow dependency</b>: each child partition depends on at most one partition of each parent (map, filter, flatMap, mapValues, union, coalesce).</li>
        <li><b>Wide dependency</b>: a child partition depends on many parent partitions (groupByKey, reduceByKey, distinct, join, sortByKey, repartition). It starts a new stage.</li>
        <li>A shuffle writes map output to local disk, then reducers fetch it over the network: cost in disk, network, serialisation and memory.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>groupByKey wrote <b>355.6 KiB</b> of shuffle data and took 5.0 s; reduceByKey wrote <b>106.7 KiB</b> and took 2.3 s, with identical results.</li>
        <li>repartition(2) shuffled all 2,000,000 pairs (11.5 MiB); coalesce(2) merged partitions without a shuffle.</li>
        <li>Two RDDs partitioned the same way (8 partitions, same hash) were joined with <b>no new shuffle</b>; mapValues kept the partitioner, map lost it.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Narrow and wide dependencies, and the shuffle</h2>
''' + def_block(
    'Transformations create dependencies between RDDs. A <b>narrow dependency</b> exists when each partition of the parent is used by at most one partition of the child, so the work can be pipelined within one task and stage. A <b>wide (shuffle) dependency</b> exists when a child partition may need data from many parent partitions; Spark then performs a <b>shuffle</b>: map tasks partition their output by key (by default with a hash partitioner) and write it to local disk, and reduce tasks in the next stage fetch their parts over the network. Shuffles are the main cost of most Spark jobs. Operations such as <code>reduceByKey</code> and <code>aggregateByKey</code> combine values on the map side before shuffling; <code>groupByKey</code> ships the values. RDDs that share the same <b>partitioner</b> can be joined without another shuffle, and transformations such as <code>mapValues</code> preserve the partitioner.',
    'Some steps can be done on each piece of data where it is (narrow). Others need data from all pieces (wide), so Spark moves data between machines: the shuffle. Shuffles are slow, so send less data: combine first, avoid unneeded repartitioning, and reuse the same partitioning.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Narrow', 'Child partition needs one parent partition. No data moves.'),
    ('Wide', 'Child partition needs many parent partitions. Shuffle.'),
    ('Shuffle write', 'Map tasks write partitioned output to local disk.'),
    ('Shuffle read', 'Reduce tasks fetch their part from every map task.'),
    ('Map-side combine', 'Combining values per key before the shuffle (reduceByKey).'),
    ('Partitioner', 'Rule mapping a key to a partition (hash, range).'),
    ('Co-partitioned', 'Two RDDs with the same partitioner and number of partitions.'),
    ('coalesce', 'Merge partitions without a shuffle (only to reduce the number).'),
]) + '''

  <h3>Common operations by dependency</h3>
''' + table(['Narrow (no shuffle)', 'Wide (shuffle)', 'Depends'], [
    ['<code>map</code>, <code>flatMap</code>, <code>filter</code>', '<code>groupByKey</code>, <code>reduceByKey</code>', '<code>join</code>: narrow if co-partitioned'],
    ['<code>mapValues</code>, <code>flatMapValues</code>', '<code>distinct</code>, <code>sortByKey</code>, <code>sortBy</code>', '<code>coalesce(n, shuffle=True)</code> = repartition'],
    ['<code>union</code>, <code>sample</code>, <code>mapPartitions</code>', '<code>repartition</code>, <code>partitionBy</code>', '<code>cogroup</code>: like join'],
    ['<code>coalesce(n)</code> (fewer partitions)', '<code>aggregateByKey</code>, <code>combineByKey</code>', '—'],
], minw=680) + lv + '''
EXAM> “Narrow vs wide transformations?” Narrow: each output partition depends on one input partition (map, filter); no shuffle, pipelined in one stage. Wide: output partitions depend on many input partitions (groupByKey, reduceByKey, join, repartition); requires a shuffle and a new stage. Prefer reduceByKey over groupByKey because it combines values before shuffling.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Choosing operations to shuffle less</h2>
''' + table(['Instead of', 'Use', 'Why', 'Lab'], [
    ['<code>groupByKey().mapValues(sum)</code>', '<code>reduceByKey(add)</code>', 'Combines per partition before shuffling', '355.6 → 106.7 KiB'],
    ['<code>groupByKey()</code> for averages', '<code>aggregateByKey((0, 0), …)</code>', 'Ships (sum, count), not all values', 'Lesson 2.5'],
    ['<code>repartition(n)</code> to reduce partitions', '<code>coalesce(n)</code>', 'Merges locally, no shuffle', '11.5 MiB → 0'],
    ['Joining two RDDs repeatedly', '<code>partitionBy(n)</code> both once + cache', 'Later joins need no shuffle', 'join with 0 new shuffle'],
    ['<code>map</code> on a partitioned pair RDD', '<code>mapValues</code>', 'Keeps the partitioner', 'kept: True vs False'],
    ['Shuffling a small table to join a big one', 'Broadcast the small one', 'Only the small side moves', 'Lessons 3.2, 8.2'],
], minw=760) + '''
WARN> <code>coalesce</code> avoids a shuffle by <b>merging</b> neighbouring partitions, which can leave them unbalanced and reduces parallelism for everything before it in the same stage. Use it to write fewer files at the end of a job; use <code>repartition</code> when you need evenly sized partitions or more of them.
</section>
'''

FIG1 = fig('ui-rdd-groupbykey.webp', 1280, 820, 'Job 1 DAG for groupByKey with two stages and 355.6 KiB shuffle write and read', 'Real screenshot: groupByKey on the cluster. Stage 1 writes 355.6 KiB of shuffle data; stage 2 (partitionBy, mapPartitions) reads it. 8 tasks each.')
FIG2 = fig('ui-rdd-join.webp', 1280, 860, 'Job 5 DAG for a join with three stages', 'Real screenshot: the join without a shared partitioner. PySpark implements join as union + group: both inputs are shuffled again (stages 9 and 10).')
FIG3 = fig('ui-rdd-copart.webp', 1280, 820, 'Job 8 DAG with two skipped stages and one stage containing the join', 'Real screenshot: the co-partitioned join. The two partitionBy stages are skipped (already done and cached: green dots) and the join runs inside one stage with no new shuffle.')
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Measuring shuffles on the cluster</h2>
  <p>All outputs are real: Spark 4.3.0 standalone cluster, two executors with 2 cores each. Data: 2,000,000 generated (customer_id, amount) pairs for 2,000 TiffinGo customers, in 8 partitions. Shuffle sizes come from the history server’s REST API (job descriptions set with <code>setJobDescription</code>).</p>
''' + stepper([
    ('Step 1 · Narrow: no data moves',
     code('python', 'rdd_shuffle.py', 'pairs = sc.parallelize(range(2_000_000), 8).map(lambda i: (i % 2000, (i * 7919) % 900 + 60))\nn = pairs.filter(lambda kv: kv[1] > 500).map(lambda kv: kv[1] * 1.05).count()', has('l24_cluster.txt', 'narrow') + '\n\n' + job(0)),
     'Generate, filter and map ran as <b>one stage of 8 tasks</b>, one per partition, with <b>0 bytes</b> of shuffle. Each task read its partition, filtered it and mapped it in a single pass. Narrow steps are the cheap ones; most of the 5.4 s here is starting Python workers and generating the data.'),
    ('Step 2 · groupByKey: ship every value',
     code('python', 'rdd_shuffle.py', 'g = pairs.groupByKey().mapValues(sum).collect()', has('l24_cluster.txt', 'groupByKey') + '\n\n' + job(1)) + FIG1,
     'Two stages: 8 map tasks wrote the pairs to shuffle files partitioned by customer, 8 reduce tasks fetched them and summed. <b>355.6 KiB</b> crossed the shuffle. PySpark already packs values into batches, so the record count (448) counts batches, not pairs; the bytes are the number to watch.'),
    ('Step 3 · reduceByKey: combine first',
     code('python', 'rdd_shuffle.py', 'from operator import add\nr = pairs.reduceByKey(add).collect()\nsorted(g) == sorted(r)', has('l24_cluster.txt', 'reduceByKey') + '\n\n' + job(2)),
     'Same shape (2 stages, 16 tasks), same 2,000 totals, but only <b>106.7 KiB</b> written: about a third. Each map task first added up the amounts per customer <b>inside its partition</b> (map-side combine), so it shuffled one partial sum per customer instead of every amount. The job took 2.3 s instead of 5.0 s. With millions of values per key, the gap grows enormously.'),
    ('Step 4 · repartition vs coalesce',
     code('python', 'rdd_shuffle.py', 'pairs.repartition(2).count()\npairs.coalesce(2).count()', has('l24_cluster.txt', 'repartition', 'coalesce') + '\n\n' + job(3, 4)),
     'Both ended with 2 partitions. <code>repartition(2)</code> is a full shuffle: <b>11.5 MiB</b>, every pair written and read again, 2 stages. <code>coalesce(2)</code> just let each of 2 tasks read 4 of the old partitions: <b>1 stage, 0 bytes</b>. To reduce partitions, coalesce; to rebalance or increase them, repartition.'),
    ('Step 5 · A join that shuffles both sides',
     code('python', 'rdd_shuffle.py', 'totals = pairs.reduceByKey(add)                                  # 8 partitions\nnames = sc.parallelize([(c, f"cust{c}") for c in range(2000)], 4)    # 4 partitions\ntotals.join(names).count()', has('l24_cluster.txt', 'join A') + '\n\n' + job(5)) + FIG2,
     'Three stages and 32 tasks: the reduce for <code>totals</code>, then a shuffle of <b>both</b> inputs so that matching customer ids meet. In PySpark, <code>join</code> is built from <code>union</code> + group by key (visible in the DAG). <code>totals</code> had a partitioner, but <code>names</code> did not and had a different number of partitions, so both sides moved.'),
    ('Step 6 · Co-partition once, join without a shuffle',
     code('python', 'rdd_shuffle.py', 'part_totals = pairs.reduceByKey(add, 8).cache();  part_totals.count()\npart_names  = names.partitionBy(8).cache();        part_names.count()\npart_totals.join(part_names).count()                 # the join itself', has('l24_cluster.txt', 'join B') + '\n\n' + job(6, 7, 8)) + FIG3,
     'Jobs 6 and 7 partitioned and cached both sides with the same hash partitioner and 8 partitions: those shuffles are paid once. The join (job 8) then ran in <b>one stage</b> with two stages skipped and <b>0 bytes</b> of new shuffle: partition <i>k</i> of one side only needs partition <i>k</i> of the other. Worth it when the same RDDs are joined repeatedly.'),
    ('Step 7 · Keep the partitioner: mapValues, not map',
     code('python', 'rdd_shuffle.py', 'part_totals.mapValues(lambda v: v * 2).partitioner is not None\npart_totals.map(lambda kv: (kv[0], kv[1] * 2)).partitioner is not None', has('l24_cluster.txt', 'mapValues')),
     '<code>map</code> could change the keys, so Spark must forget the partitioner; a later join or reduce would shuffle again. <code>mapValues</code> guarantees keys stay the same, so the partitioner is kept. The same applies to <code>flatMapValues</code>. A one-word change that can save a whole shuffle.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('filter + map', W), ('1 stage · 8 tasks', G), ('shuffle write: 0 KiB', G)], size=7.8),
    term([('groupByKey().mapValues(sum)', W), ('2 stages · 16 tasks', Y), ('shuffle write: 355.6 KiB · 5.0 s', RD)], size=7.4),
    term([('reduceByKey(add)', W), ('shuffle write: 106.7 KiB · 2.3 s', G), ('same result: True', G)], size=7.4),
    term([('repartition(2): 11,545 KiB', RD), ('coalesce(2)   : 0 KiB, 1 stage', G)], size=7.6),
    term([('join, no shared partitioner: 3 stages', Y), ('co-partitioned join: 1 stage, 0 KiB', G), ('mapValues keeps partitioner: True', G), ('map keeps partitioner: False', RD)], size=7.0),
]
B1 = [
    t(180, 12, 'Narrow dependency', 9.4, bold=True) + deps('narrow') + cap('Pipelined in one task per partition.', '', 'green', y=118, h=30),
    t(180, 12, 'Wide dependency', 9.4, bold=True) + deps('wide', True) + cap('All values cross the network.', '', 'red', y=118, h=30),
    t(180, 12, 'Combine, then shuffle', 9.4, bold=True) + deps('wide') + cap('One partial sum per key per partition.', '', 'green', y=118, h=30),
    t(180, 12, 'Merge without moving', 9.4, bold=True) + opbox(20, 30, 'P0 P1 P2 P3', '', 'blue', 120, 24) + opbox(20, 66, 'P4 P5 P6 P7', '', 'blue', 120, 24) + arrow(142, 42, 238, 42, 'acc', 1.4) + arrow(142, 78, 238, 78, 'acc', 1.4) + opbox(240, 30, 'C0', 'read 4 parts', 'green', 100, 24) + opbox(240, 66, 'C1', 'read 4 parts', 'green', 100, 24) + cap('coalesce: narrow; repartition: wide.', '', 'blue', y=118, h=30),
    t(180, 12, 'Same partitioner, no shuffle', 9.4, bold=True) + deps('narrow') + cap('Partition k joins partition k.', '', 'green', y=118, h=30),
]
see_caps = ['Filter and map moved no data.',
            'groupByKey shuffled 355.6 KiB.',
            'reduceByKey shuffled a third as much.',
            'repartition shuffled everything; coalesce nothing.',
            'Co-partitioned RDDs joined without a shuffle.']
behind_caps = ['Each child partition needs one parent partition.',
               'Each child partition needs all parents.',
               'Map-side combine shrinks what moves.',
               'Neighbouring partitions are simply merged.',
               'Matching keys are already together.']
two = anim_two('Narrow vs wide', 'Where data moves', 'Real lab outputs', 'The dependencies', see, B1, see_caps, behind_caps)

# ---- scenario 1: groupByKey OOM
e1 = (t(180, 22, 'Job dies on one key', 9.4, bold=True) + t(180, 56, 'ExecutorLostFailure · OutOfMemory', 8.4, 'ink', mono=True) + cap('After a groupByKey.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'One customer, 40 M orders', 9.4, bold=True) + t(180, 56, 'a test account used by load tests', 8.4, 'ink2') + cap('All values in one list.', '', 'amber', y=150, h=34))
e3 = (t(180, 22, 'reduceByKey instead', 9.4, bold=True) + t(180, 56, 'only (sum, count) per partition', 8.4, 'ink2') + cap('Memory stays small.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Shuffle shrinks too', 9.4, bold=True) + t(180, 56, 'like 355.6 → 106.7 KiB', 8.4, 'ink', mono=True) + cap('And runs faster.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Filter test accounts', 9.4, 'acc', bold=True) + t(180, 56, 'data quality first', 8.4, 'ink2') + cap('Skew: Lesson 8.3.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'groupByKey on a hot key',
              'Why reviewers flag groupByKey. (Typical; shuffle sizes from our lab.)',
              'Map-side combine', 'groupByKey moves and holds every value of a key; reduceByKey/aggregateByKey combine first and use far less memory and network', [e1, e2, e3, e4, e5],
              ['Executor dies.', 'One giant key.', 'Combine first.', 'Smaller shuffle.', 'Clean the data.'],
              hid='scenario-hotkey')

# ---- scenario 2: repartition before write
b1 = (t(180, 22, '“Write one file per day”', 9.4, bold=True) + t(180, 56, 'rdd.repartition(1).saveAsTextFile()', 8.2, 'ink', mono=True) + cap('Full shuffle to one task.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Slow and fragile', 9.4, bold=True) + t(180, 56, 'all data through one executor', 8.4, 'ink2') + cap('Like our 11.5 MiB, times 1,000.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'coalesce(1)', 9.4, bold=True) + t(180, 56, 'no shuffle, but also 1 task upstream', 8.2, 'ink2') + cap('Can slow the whole stage.', '', 'amber', y=150, h=34))
b4 = (t(180, 22, 'Better: a few files', 9.4, bold=True) + t(180, 56, 'coalesce(8) → 8 reasonable files', 8.4, 'ink', mono=True) + cap('Parallel and tidy.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Size, not count', 9.4, 'acc', bold=True) + t(180, 56, 'aim for 128 MB–1 GB per file', 8.4, 'ink2') + cap('Lesson 5.3.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'One output file at any cost',
              'A common request with a hidden shuffle. (Typical; costs from our lab.)',
              'coalesce vs repartition', 'repartition(1) shuffles everything to one task; coalesce avoids the shuffle but limits parallelism; a few well-sized files is usually best', [b1, b2, b3, b4, b5],
              ['One file please.', 'Everything through one task.', 'coalesce has a catch.', 'A few files.', 'Think in sizes.'],
              hid='scenario-onefile')

# ---- scenario 3: repeated joins
u1 = (t(180, 22, 'Hourly job joins orders', 9.4, bold=True) + t(180, 56, 'with customers, 24 times a day', 8.4, 'ink2') + cap('Customers shuffled every time.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'partitionBy once', 9.4, bold=True) + t(180, 56, 'customers.partitionBy(200).cache()', 8.2, 'ink', mono=True) + cap('Pay the shuffle once.', '', 'green', y=150, h=34))
u3 = (t(180, 22, 'Same partitioner on orders', 9.4, bold=True) + t(180, 56, 'reduceByKey(add, 200)', 8.4, 'ink', mono=True) + cap('Co-partitioned.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Joins without shuffles', 9.4, bold=True) + t(180, 56, 'like our job 8: 0 KiB', 8.4, 'ink', mono=True) + cap('Only the new data moves.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Keep it with mapValues', 9.4, 'acc', bold=True) + t(180, 56, 'map() would lose the partitioner', 8.4, 'ink2') + cap('One word matters.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Joining the same data again and again',
              'How co-partitioning saves repeated shuffles. (Typical; behaviour from our lab.)',
              'Co-partitioning', 'Partition the reused side once with the same partitioner and number of partitions as the other side, cache it, and keep the partitioner with mapValues', [u1, u2, u3, u4, u5],
              ['Repeated joins.', 'Partition once.', 'Match the other side.', 'No shuffle.', 'Do not lose it.'],
              hid='scenario-copart')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Where data moves</h2>
  <p>Left: real outputs. Right: the dependencies between partitions.</p>
''' + two + '''
  <p>Three live scenarios follow: a hot key, one output file, and repeated joins.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Shuffles at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'review', 10, 'blue', bold=True) + t(60, 58, 'groupByKey', 7.4, 'ink2'),
    '1. Code reviews',
    'groupByKey followed by an aggregation is one of the first things reviewers replace with reduceByKey or aggregateByKey.',
    ['groupByKey', '*review', 'reduceByKey']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'files', 11, 'green', bold=True) + t(60, 58, 'sizes', 7.4, 'ink2'),
    '2. Output file sizes',
    'coalesce at the end of jobs keeps file counts sensible without a shuffle.',
    ['Many parts', '*coalesce', 'Fewer files']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'joins', 11, 'violet', bold=True) + t(60, 58, 'repeated', 7.4, 'ink2'),
    '3. Iterative joins',
    'Graph algorithms and iterative pipelines co-partition and cache the static side to avoid shuffling it each round.',
    ['Static side', '*partitionBy', 'Cheap joins']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'UI', 12, 'acc', bold=True) + t(60, 58, 'shuffle', 7.4, 'ink2'),
    '4. Tuning with shuffle metrics',
    'Shuffle read and write in the Stages tab show which step moves the most data and where to optimise.',
    ['Stages tab', '*shuffle bytes', 'Fix']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'cost', 11, 'acc', bold=True) + t(60, 58, 'network', 7.4, 'ink2'),
    '5. Cloud cost',
    'Shuffle traffic uses disks and network that cloud providers bill for; smaller shuffles mean cheaper jobs.',
    ['Shuffle', '*smaller', 'Lower bill']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> Lesson <a href="../03-lazy-evaluation-and-the-dag/">2.3</a> (stages and the DAG). Pair RDDs (key, value) are introduced fully in 2.5; here we only need <code>(customer_id, amount)</code>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
