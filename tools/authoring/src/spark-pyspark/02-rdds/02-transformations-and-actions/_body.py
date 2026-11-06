import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
def pick(n, *keys):
    return '\n'.join(l for l in capf(n).split('\n') if any(l.startswith(k) for k in keys))

def opbox(x, y, label, sub='', tone='card', w=128, h=26):
    o = box(x, y, w, h, tone) + t(x + w / 2, y + (11 if sub else 16), label, 7.2, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 21, sub, 6.4, 'ink2', mono=True)
    return o

def flow(a, op, b, tone='blue', note=''):
    """input box → op → output box"""
    o = opbox(14, 34, 'input', a, 'card', 120, 30) + arrow(136, 49, 168, 49, 'acc', 1.6)
    o += opbox(170, 38, op, '', tone, 70, 22) + arrow(242, 49, 262, 49, 'acc', 1.6)
    o += opbox(264, 34, 'output', b, 'green', 86, 30)
    if note:
        o += t(180, 90, note, 7, 'ink2')
    return o

# ---------------------------------------------------------------- story
sc = (opbox(14, 18, 'Transformations', 'map · flatMap · filter', 'blue', 160, 30) + opbox(14, 58, '… more', 'distinct · union · mapPartitions', 'blue', 160, 30) +
      arrow(176, 48, 222, 76, 'acc', 1.4) + opbox(14, 104, 'Actions', 'collect · reduce · count · save', 'violet', 160, 30) + arrow(176, 119, 222, 90, 'acc', 1.4) +
      box(226, 60, 150, 42, 'amber') + t(301, 78, 'new RDD  vs  result', 8, bold=True) + t(301, 93, 'lazy        runs a job', 7, 'ink2', mono=True) +
      box(410, 12, 222, 136, 'card') + t(521, 30, 'From the lab', 8.6, bold=True) +
      ''.join(t(422, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
          ('flatMap: 5,000 lines → 12,671 dishes', 'ink'), ('distinct: 32 dishes', 'ink'), ('aggregate: (2670, 6)', 'green'),
          ('driver counter after foreach: 0', 'red'), ('accumulator: 2670', 'green'), ('mapPartitions: 4 setups, not 100,000', 'green')])))
scene_svg = scene('RDD operations come in two kinds: transformations return a new RDD and run nothing; actions return a result to the driver (or write data) and run a job. The right side shows real results, including the most famous RDD trap.', sc,
                  'Transformations <tspan font-weight="700" class="s-acc">describe</tspan>; actions <tspan font-weight="700" class="s-acc">deliver</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“My counter says zero”</h2>
  <div class="story">
    <p class="narration">Kabir is reading the old RDD job. It splits order notes into dishes, counts the most popular ones and adds up revenue. One function is supposed to add every amount to a Python variable called <code>total</code>. On the cluster, <code>total</code> is always 0, and the job’s <code>print()</code> lines never appear. Riya bets it is a bug in Spark.</p>

{scene_svg}

K> Sir, the code clearly adds to <code>total</code>. Why is it zero?
A> Because that code did not run in your Python process. Functions passed to RDD operations are shipped to the <b>executors</b> with a <b>copy</b> of the variables they use. The executors added to their copies; your driver’s <code>total</code> never changed. Spark has a tool for exactly this: the <b>accumulator</b>.
R> And the missing prints?
A> They went to the executors’ logs. Today we go through the transformations and actions you will use most, on TiffinGo’s order notes and amounts, and reproduce both surprises. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Transformations and actions at three levels
L1> Recipes and serving
      <ul>
        <li><b>Transformations</b> are recipe steps: “split the notes”, “keep only hot orders”. Writing them down cooks nothing.</li>
        <li><b>Actions</b> are “serve it now”: count, collect, save. Only then does the kitchen work.</li>
        <li>Cooks work in their own kitchens: a note you change on your desk does not change theirs.</li>
      </ul>
L2> The common operations
      <ul>
        <li>Element-wise: <code>map</code> (one in, one out), <code>flatMap</code> (one in, zero or more out), <code>filter</code>.</li>
        <li>Set-like: <code>distinct</code>, <code>union</code>, <code>intersection</code>, <code>subtract</code>; sampling: <code>sample</code>.</li>
        <li>Per partition: <code>mapPartitions</code>, <code>glom</code>. Actions: <code>collect</code>, <code>count</code>, <code>first</code>, <code>take</code>, <code>top</code>, <code>takeOrdered</code>, <code>reduce</code>, <code>fold</code>, <code>aggregate</code>, <code>countByValue</code>, <code>foreach</code>, <code>saveAsTextFile</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li><code>flatMap</code> turned 5,000 order lines into 12,671 dish names; <code>distinct</code> found 32 dishes.</li>
        <li>A driver variable updated in <code>foreach</code> stayed <b>0</b>; an accumulator gave 2670. On the cluster, <code>print</code> output was in the executors’ stderr files.</li>
        <li><code>map</code> ran a setup step 100,000 times; <code>mapPartitions</code> ran it 4 times (once per partition).</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Transformations, actions and closures</h2
>''' + def_block(
    'RDDs support two kinds of operations. <b>Transformations</b> (such as <code>map</code>, <code>flatMap</code>, <code>filter</code>, <code>distinct</code>, <code>union</code>, <code>mapPartitions</code>) create a new RDD from an existing one and are evaluated lazily. <b>Actions</b> (such as <code>collect</code>, <code>count</code>, <code>take</code>, <code>reduce</code>, <code>fold</code>, <code>aggregate</code>, <code>foreach</code>, <code>saveAsTextFile</code>) trigger a job and return a value to the driver or write to storage. Functions passed to these operations, together with the variables they reference (their <b>closure</b>), are serialised and sent to executors; each task works on its own copy, so changes to driver variables inside them are not visible to the driver. Shared state must use <b>accumulators</b> (add-only, read on the driver) or <b>broadcast variables</b> (read-only).',
    'Transformations make a new RDD and wait; actions run the work and give you an answer. The functions you pass run on other machines with their own copies of your variables, so changing a normal variable inside them does nothing on your side.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('map', 'One output per input element.'),
    ('flatMap', 'Zero or more outputs per input; results are flattened.'),
    ('mapPartitions', 'Your function gets a whole partition (an iterator) at once.'),
    ('reduce / fold', 'Combine all elements with a function (fold has a start value).'),
    ('aggregate', 'Like fold, but the result type can differ from the elements.'),
    ('Closure', 'A function plus the outside variables it uses.'),
    ('Accumulator', 'A shared counter tasks can add to; the driver reads it.'),
    ('foreach', 'Action that runs a function on every element, for side effects.'),
]) + '''

  <h3>The operations in this lesson</h3>
''' + table(['Operation', 'Kind', 'Returns', 'Lab result'], [
    ['<code>map(f)</code>', 'Transformation', 'RDD, same count', 'line → [id, dishes, notes]'],
    ['<code>flatMap(f)</code>', 'Transformation', 'RDD, any count', '5,000 lines → 12,671 dishes'],
    ['<code>filter(f)</code>', 'Transformation', 'RDD, fewer', '1,695 hot orders'],
    ['<code>distinct()</code>', 'Transformation (shuffle)', 'RDD, unique', '32 dishes'],
    ['<code>mapPartitions(f)</code>', 'Transformation', 'RDD', '[2517, 2483] lines per partition'],
    ['<code>collect()</code>, <code>take(n)</code>, <code>first()</code>', 'Action', 'Python list / element', 'to the driver'],
    ['<code>reduce</code>, <code>fold</code>, <code>aggregate</code>', 'Action', 'One value', '2670, 2670, (2670, 6)'],
    ['<code>foreach(f)</code>', 'Action', '<code>None</code>', 'side effects on executors'],
    ['<code>saveAsTextFile(dir)</code>', 'Action', 'files', 'part-00000, part-00001, _SUCCESS'],
], minw=740) + lv + '''
EXAM> “Difference between map and flatMap?” map returns exactly one element per input; flatMap can return zero or more and flattens them, e.g. splitting lines into words. “Why does updating a variable in foreach not work?” The closure is copied to each executor; use an accumulator for counters.
</section>
'''
definition = definition.replace('</h2\n>', '</h2>\n')

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Choosing the right operation</h2>
''' + table(['You want to…', 'Use', 'Avoid', 'Why'], [
    ['Turn lines into words', '<code>flatMap(split)</code>', '<code>map(split)</code>', 'map gives a list per line, not words'],
    ['See a few elements', '<code>take(5)</code>', '<code>collect()</code>', 'collect brings everything to the driver'],
    ['Largest / smallest n', '<code>top(n)</code>, <code>takeOrdered(n)</code>', '<code>sortBy</code> + <code>collect</code>', 'top keeps only n per partition'],
    ['Sum and count together', '<code>aggregate</code>', 'two separate actions', 'one pass over the data'],
    ['Count occurrences (small result)', '<code>countByValue()</code>', '—', 'returns a dict to the driver'],
    ['Open a connection per partition', '<code>mapPartitions</code> / <code>foreachPartition</code>', '<code>map</code> / <code>foreach</code>', 'once per partition, not per element'],
    ['Count something on the side', 'accumulator', 'global variable', 'closures are copies'],
], minw=740) + '''
WARN> <code>collect()</code> and <code>countByValue()</code> bring their whole result into the <b>driver</b>. On five lines that is fine; on five billion it kills the driver (Lesson 1.3). Prefer <code>take</code>, <code>top</code>, aggregations that return small results, or <code>saveAsTextFile</code>.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Every common operation, with real results</h2>
  <p>All outputs are real: PySpark 4.3.0 in local mode (Steps 1–7) and on our standalone cluster (Step 8). Data: <code>order_items.txt</code>, 5,000 lines like <code>100001|Chole Bhature,Aloo Paratha,Lassi,Rajma Chawal|spice:medium,cutlery:yes</code>, and six order amounts.</p>
''' + stepper([
    ('Step 1 · map and flatMap',
     code('python', 'ops.py', 'lines = sc.textFile("order_items.txt")\nparts = lines.map(lambda l: l.split("|"))\nprint("map       :", parts.first())\ndishes = lines.flatMap(lambda l: l.split("|")[1].split(","))\nprint("flatMap   :", dishes.take(5), "| elements:", dishes.count())', pick('l22_ops.txt', 'map ', 'flatMap')),
     '<code>map</code> turned each line into <b>one</b> list of three fields. <code>flatMap</code> returned the dish names of each line as separate elements: 5,000 lines became 12,671 dishes, about 2.5 per order. Whenever one input should become several outputs (words, items, events), use <code>flatMap</code>.'),
    ('Step 2 · filter, distinct, union, sample',
     code('python', 'ops.py', 'spicy = lines.filter(lambda l: "spice:hot" in l)\nmenu = dishes.distinct()\nboth = sc.parallelize(["Poha", "Idli"]).union(sc.parallelize(["Idli", "Dosa"]))\nlines.sample(False, 0.001, seed=7).count()', pick('l22_ops.txt', 'filter', 'distinct', 'union', 'sample')),
     '<code>filter</code> kept 1,695 orders that asked for hot food. <code>distinct</code> found 32 different dishes; it needs a shuffle, because duplicates can sit in different partitions. <code>union</code> just appends, keeping duplicates. <code>sample(False, 0.001)</code> returned 2 lines, not exactly 5: sampling is random per element, so the size is only approximate.'),
    ('Step 3 · mapPartitions: once per partition',
     code('python', 'closure.py', "setups = sc.accumulator(0)\ndef per_element(x):\n    setups.add(1)                 # e.g. open a DB connection for every element\n    return x * 2\ndef per_partition(it):\n    setups.add(1)                 # once per partition\n    return (x * 2 for x in it)\nbig = sc.parallelize(range(100_000), 4)\nbig.map(per_element).count()\nbig.mapPartitions(per_partition).count()", pick('l22_closure.txt', 'map ', 'mapPartitions') + '\n\nlines.mapPartitions(lambda it: [sum(1 for _ in it)]).collect()\n' + pick('l22_ops.txt', 'mapPartitions')),
     'With <code>map</code>, any setup inside the function runs for <b>every element</b>: 100,000 times. With <code>mapPartitions</code>, the function receives an iterator over a whole partition and the setup runs <b>4 times</b>. That is how you open one database connection or load one model per partition. The function must return an iterator or list.'),
    ('Step 4 · Actions that return elements',
     code('python', 'ops.py', 'amounts = sc.parallelize([530, 210, 480, 990, 120, 340], 3)\namounts.collect(); amounts.count(); amounts.first(); amounts.take(2)\namounts.top(2); amounts.takeOrdered(2)', pick('l22_ops.txt', 'collect', 'count ', 'top')),
     '<code>take(2)</code> returns the first elements in partition order; <code>top(2)</code> the largest; <code>takeOrdered(2)</code> the smallest (or by a key you give). <code>take</code> and <code>first</code> can stop after the first partitions, so they are cheap even on huge RDDs.'),
    ('Step 5 · reduce, fold, aggregate',
     code('python', 'ops.py', 'amounts.reduce(lambda a, b: a + b)\namounts.fold(0, lambda a, b: a + b)\namounts.aggregate((0, 0),\n                  lambda acc, x: (acc[0] + x, acc[1] + 1),      # within a partition\n                  lambda a, b: (a[0] + b[0], a[1] + b[1]))     # across partitions', pick('l22_ops.txt', 'reduce', 'fold', 'aggregate')),
     '<code>reduce</code> combines elements pairwise; the function must be associative and commutative, because Spark reduces each partition first and then combines the partial results. <code>fold</code> adds a neutral start value (0 for sums). <code>aggregate</code> can build a different type: here a (sum, count) pair in one pass, so the average is 2670 / 6 = 445.'),
    ('Step 6 · countByValue and saveAsTextFile',
     code('python', 'ops.py', 'sorted(dishes.countByValue().items(), key=lambda kv: -kv[1])[:3]\nmenu.saveAsTextFile("out_menu")\nsorted(os.listdir("out_menu"))', pick('l22_ops.txt', 'countByValue', 'saveAsTextFile')),
     '<code>countByValue</code> returned a Python dict of all 32 dishes to the driver; Sambar Rice is the most ordered (502). <code>saveAsTextFile</code> wrote <b>one file per partition</b> (2 here), a <code>_SUCCESS</code> marker and hidden checksum files. Spark refuses to write into an existing folder, so remove it or choose a new name.'),
    ('Step 7 · The closure trap, and the fix',
     code('python', 'closure.py', 'counter = 0\ndef add(x):\n    global counter\n    counter += x\namounts.foreach(add)\nprint("driver variable after foreach:", counter)\n\nacc = sc.accumulator(0)\namounts.foreach(lambda x: acc.add(x))\nprint("accumulator after foreach    :", acc.value)', pick('l22_closure.txt', 'driver variable', 'accumulator')),
     'Exactly Kabir’s bug. <code>add</code> and the variable it uses were pickled and sent to each task, which updated <b>its own copy</b> of <code>counter</code>; the driver’s copy stayed 0, even in local mode. An <b>accumulator</b> is designed for this: tasks can only add to it and the driver reads the total (2670). Lesson 3.2 covers accumulators and broadcast variables in depth.'),
    ('Step 8 · Where print() goes on a cluster',
     code('python', 'rdd_shuffle.py (cluster)', 'sc.parallelize(["poha", "idli", "dosa"], 2).foreach(lambda x: print("EXECUTOR SAYS:", x))\nprint("driver: foreach finished")', 'driver output:\ndriver: foreach finished\n\n' + capf('l22_executor_print.txt')),
     'On the cluster, the driver printed only its own line. The prints ran inside executor processes, so they landed in each executor’s log under the worker’s <code>work/</code> folder, also reachable from the Executors tab (stdout/stderr links). In local mode you see them in your terminal, which hides the problem. To look at data, bring a little back with <code>take()</code> and print on the driver.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('map     : [id, dishes, notes]', W), ('flatMap : Chole Bhature, Aloo Paratha …', G), ('elements: 12671', G)], size=7.2),
    term([('filter   : 1695 hot orders', G), ('distinct : 32 dishes', G), ("union    : ['Poha','Idli','Idli','Dosa']", Y)], size=7.2),
    term([('map           -> setup calls: 100000', RD), ('mapPartitions -> setup calls: 4', G)], size=7.4),
    term([('reduce    : 2670', G), ('fold      : 2670', G), ('aggregate : (2670, 6)', G)], size=7.8),
    term([('driver variable after foreach: 0', RD), ('accumulator after foreach    : 2670', G), ('prints: in executor stderr', Y)], size=7.2),
]
B1 = [
    t(180, 16, 'One-to-one vs one-to-many', 9.4, bold=True) + flow('"…|Poha,Idli|…"', 'flatMap', 'Poha · Idli', 'blue', 'map would give one list per line') + cap('Use flatMap to explode records.', '', 'blue', y=112, h=30),
    t(180, 16, 'Keep, de-duplicate, append', 9.4, bold=True) + flow('Idli · Idli · Dosa', 'distinct', 'Idli · Dosa', 'violet', 'distinct needs a shuffle; union does not') + cap('Some transformations move data.', '', 'violet', y=112, h=30),
    t(180, 16, 'Per element vs per partition', 9.4, bold=True) + flow('100,000 elements', 'mapPart.', '4 setups', 'green', 'one connection per partition') + cap('Expensive setup: once per partition.', '', 'green', y=112, h=30),
    t(180, 16, 'Partials first, then combine', 9.4, bold=True) + flow('[530,210] [480,990] …', 'aggregate', '(2670, 6)', 'amber', 'seqOp per partition, combOp across') + cap('Functions must not depend on order.', '', 'amber', y=112, h=30),
    t(180, 16, 'Copies, not shared variables', 9.4, bold=True) + opbox(14, 34, 'driver', 'counter = 0', 'blue', 110, 30) + opbox(236, 24, 'task 1', 'its own counter', 'amber', 110, 26) + opbox(236, 58, 'task 2', 'its own counter', 'amber', 110, 26) + arrow(126, 49, 234, 37, 'acc', 1.2) + arrow(126, 49, 234, 71, 'acc', 1.2) + t(180, 100, 'accumulators flow back; normal variables do not', 7, 'ink2') + cap('Use accumulators for counters.', '', 'red', y=112, h=30),
]
see_caps = ['flatMap split 5,000 lines into 12,671 dishes.',
            'filter, distinct and union on real order notes.',
            'Setup ran 100,000 times with map, 4 with mapPartitions.',
            'Three ways to total the amounts.',
            'The driver variable stayed 0; the accumulator worked.']
behind_caps = ['flatMap flattens the returned lists.',
               'distinct must bring equal values together.',
               'The function receives an iterator per partition.',
               'Spark combines per-partition results.',
               'Each task got a pickled copy of the closure.']
two = anim_two('Transformations and actions', 'Describe, then deliver', 'Real lab outputs', 'What each one does', see, B1, see_caps, behind_caps)

# ---- scenario 1: counter bug
e1 = (t(180, 22, '“Bad rows: 0” every night', 9.4, bold=True) + t(180, 56, 'bad = 0; rdd.foreach(check)', 8.4, 'ink', mono=True) + cap('But the data has errors.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Reproduce', 9.4, bold=True) + t(180, 56, 'driver variable after foreach: 0', 8.4, 'ink', mono=True) + cap('Closure copies.', '', 'amber', y=150, h=34))
e3 = (t(180, 22, 'Accumulator', 9.4, bold=True) + t(180, 56, 'bad = sc.accumulator(0)', 8.4, 'ink', mono=True) + cap('Tasks add, driver reads.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Or count with an action', 9.4, bold=True) + t(180, 56, 'rdd.filter(is_bad).count()', 8.4, 'ink', mono=True) + cap('Exact and simple.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Alert works again', 9.4, 'acc', bold=True) + t(180, 56, 'bad rows: 12', 8.4, 'ink', mono=True) + cap('Silent bugs are the worst.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'A data-quality counter that always says zero',
              'The closure trap in production. (Typical; behaviour from our lab.)',
              'Closures', 'Driver variables changed inside RDD functions are only changed in executor copies; use an accumulator or a counting action', [e1, e2, e3, e4, e5],
              ['Always zero.', 'Reproduced.', 'Accumulator.', 'Or filter + count.', 'Fixed.'],
              hid='scenario-counter')

# ---- scenario 2: one connection per partition
b1 = (t(180, 22, 'Push results to a database', 9.4, bold=True) + t(180, 56, 'rdd.foreach(lambda r: insert(r))', 8.4, 'ink', mono=True) + cap('A connection per row.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Database overwhelmed', 9.4, bold=True) + t(180, 56, '2 million connections opened', 8.4, 'ink2') + cap('Like our 100,000 setups.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'foreachPartition', 9.4, bold=True) + t(180, 56, 'open once, insert a batch, close', 8.4, 'ink2') + cap('Per partition, not per row.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Control the partitions', 9.4, bold=True) + t(180, 56, 'coalesce(20) → 20 connections', 8.4, 'ink', mono=True) + cap('Protect the database.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Or use a DataFrame writer', 9.4, 'acc', bold=True) + t(180, 56, 'df.write.jdbc(…) batches for you', 8.2, 'ink', mono=True) + cap('Lesson 5.4.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Writing to a database without killing it',
              'Why mapPartitions/foreachPartition exist. (Typical; setup counts from our lab.)',
              'Per-partition work', 'Expensive setup belongs in foreachPartition or mapPartitions; control the number of partitions to control the load', [b1, b2, b3, b4, b5],
              ['Row by row.', 'Too many connections.', 'Per partition.', 'Fewer partitions.', 'Or the JDBC writer.'],
              hid='scenario-db')

# ---- scenario 3: collect killing the driver
u1 = (t(180, 22, '“Just to check the data”', 9.4, bold=True) + t(180, 56, 'print(rdd.collect())', 8.4, 'ink', mono=True) + cap('On 3 billion rows.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Driver dies', 9.4, bold=True) + t(180, 56, 'OutOfMemoryError / killed', 8.4, 'ink', mono=True) + cap('Everything was sent to one JVM.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'Look at a few', 9.4, bold=True) + t(180, 56, 'rdd.take(10) · rdd.top(10)', 8.4, 'ink', mono=True) + cap('Stops early.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Summaries, not rows', 9.4, bold=True) + t(180, 56, 'count · aggregate · countByValue (small)', 8, 'ink', mono=True) + cap('Small results.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Or write it out', 9.4, 'acc', bold=True) + t(180, 56, 'saveAsTextFile / df.write', 8.4, 'ink', mono=True) + cap('Executors write in parallel.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'collect() on a big RDD',
              'The most common way to crash a driver. (Typical.)',
              'Driver-safe actions', 'collect brings every element to the driver; use take, top, aggregations or writes for big data', [u1, u2, u3, u4, u5],
              ['collect everything.', 'Driver OOM.', 'Take a few.', 'Aggregate.', 'Write in parallel.'],
              hid='scenario-collect2')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Describe, then deliver</h2>
  <p>Left: real outputs. Right: what each operation does.</p>
''' + two + '''
  <p>Three live scenarios follow: a counter that stays zero, writing to a database, and collect() on big data.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>These operations at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'flatMap', 10, 'blue', bold=True) + t(60, 58, 'events', 7.4, 'ink2'),
    '1. Exploding records',
    'One order with many items, one log line with many fields: flatMap turns them into one record each.',
    ['Order', '*flatMap', 'Items']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'per-part', 9, 'green', bold=True) + t(60, 58, 'clients', 7.4, 'ink2'),
    '2. One client per partition',
    'Calling APIs, caches or ML models with one client per partition instead of one per record.',
    ['Partition', '*mapPartitions', 'Batch call']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'counters', 9, 'violet', bold=True) + t(60, 58, 'quality', 7.4, 'ink2'),
    '3. Data-quality counters',
    'Accumulators count malformed lines while a job runs, for logs and alerts.',
    ['Parse', '*accumulator', 'Alert']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'top-n', 11, 'acc', bold=True) + t(60, 58, 'reports', 7.4, 'ink2'),
    '4. Top-N reports',
    'top and takeOrdered find the largest orders or busiest dishes without sorting everything.',
    ['RDD', '*top(10)', 'Report']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'debug', 11, 'acc', bold=True) + t(60, 58, 'safely', 7.4, 'ink2'),
    '5. Safe debugging',
    'Engineers inspect data with take() on the driver instead of print() inside executors.',
    ['RDD', '*take(5)', 'Driver print']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> Lesson <a href="../01-what-is-an-rdd/">2.1</a> (creating RDDs) and the lambda patterns in <a href="../../01-introduction/01-prerequisites-python-sql-and-hadoop/">1.1</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
