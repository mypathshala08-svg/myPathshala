import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
def has(n, *keys):
    return '\n'.join(l for l in capf(n).split('\n') if any(k in l for k in keys))
LAZY = capf('l23_lazy.txt')
LINEAGE = LAZY[LAZY.index('(3) PythonRDD[8]'):LAZY.index('3) Every action')].rstrip()
LINEAGE_SHORT = re.sub(r' at [^\n\[]*?(\[\])', '', LINEAGE).replace('/root/lab/spark/data/tiffingo/', '')

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

def dag(hi=-1, skipped=False, cached=False):
    """textFile → flatMap → map | shuffle | reduceByKey → action"""
    o = box(10, 26, 170, 74, 'card' if skipped else 'blue') + t(95, 40, 'Stage A' + (' (skipped)' if skipped else ''), 7.4, 'ink2', bold=True)
    for k, n in enumerate(['textFile', 'flatMap', 'map']):
        o += opbox(18 + k * 54, 50, n, '', 'acc' if hi == k else ('card' if skipped else 'green'), 50, 22)
    o += t(95, 92, 'pipelined, one task per partition', 6.4, 'ink2')
    o += arrow(182, 61, 214, 61, 'acc', 1.8) + t(198, 54, 'shuffle', 6.2, 'ink2')
    o += box(216, 26, 136, 74, 'blue') + t(284, 40, 'Stage B', 7.4, 'ink2', bold=True)
    o += opbox(224, 50, 'reduceByKey', '', 'acc' if hi == 3 else 'green', 70, 22) + opbox(298, 50, 'action', '', 'acc' if hi == 4 else 'violet', 48, 22)
    if cached:
        o += f'<circle cx="259" cy="82" r="5" fill="#7BD35C" stroke="#3A8A2A"/>' + t(270, 85, 'cached', 6.4, 'green', anchor='start')
    return o

# ---------------------------------------------------------------- story
sc = (dag(-1) +
      box(410, 12, 222, 136, 'card') + t(521, 30, 'Measured', 8.6, bold=True) +
      ''.join(t(422, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
          ('bug in map: silent until count()', 'red'), ('lineage: +-(3) marks the shuffle', 'ink'), ('2 actions, no cache: 48,000 calls', 'amber'),
          ('2 actions, cached: 24,000 calls', 'green'), ('job A 14.0 s, job B 0.2 s', 'green'), ('map stage skipped: shuffle reused', 'green')])))
scene_svg = scene('Spark records RDD operations as a lineage graph and only runs it when an action needs a result. Narrow steps are pipelined into one stage; a shuffle starts the next. The numbers show what laziness costs and what Spark reuses.', sc,
                  'Nothing runs until an action; <tspan font-weight="700" class="s-acc">everything</tspan> reruns unless something is kept.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“The bug was in line 4, but Spark complained in line 20”</h2>
  <div class="story">
    <p class="narration">Riya wrote a word count over three months of TiffinGo reviews. Line 4 had a bug in a <code>map</code>, but the error only appeared at line 20, the <code>count()</code>. Then she added a second report on the same words and the job took twice as long. Kabir says Spark is “lazy”, which sounds like an insult.</p>

{scene_svg}

R> Sir, why did Spark not stop at the line with the bug?
A> Because nothing on that line ran. A transformation only adds a node to the <b>lineage graph</b>, a DAG. When an action needs a result, Spark walks the graph, cuts it into stages at shuffles and runs it. Errors inside your functions appear only then.
K> And the second report took as long as the first?
A> Every action walks the lineage again from the start, unless something is kept along the way: a <b>cache</b>, or <b>shuffle files</b> that Spark reuses on its own. Today we look at the DAG as text and in the UI, count how often our functions really run, and find out what Spark reuses. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Laziness and the DAG at three levels
L1> A to-do list, not a done list
      <ul>
        <li>Transformations write steps on a to-do list. An action says “do the list now”.</li>
        <li>If a step is wrong, you find out only when someone tries to do it.</li>
        <li>Doing the list twice means doing the work twice, unless you keep the results.</li>
      </ul>
L2> How Spark uses the DAG
      <ul>
        <li>Each RDD points to its parents; together they form a <b>directed acyclic graph</b> (DAG) of the computation.</li>
        <li>At an action, the <b>DAGScheduler</b> cuts the graph into stages at shuffle dependencies; narrow steps inside a stage are <b>pipelined</b> (one pass per partition).</li>
        <li>Laziness lets Spark combine steps, skip work that is not needed (<code>take</code> reads only some partitions) and recompute lost partitions.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>A <code>map(lambda l: len(l) / 0)</code> was accepted; <code>count()</code> raised <code>ZeroDivisionError</code> from a Python worker.</li>
        <li>Without cache, two actions ran the tokenizer 48,000 times on 24,000 lines; with <code>cache()</code>, 24,000.</li>
        <li>On the cluster, a second action on the same reduced RDD <b>skipped</b> the map stage: Spark reused the shuffle files (14.0 s → 0.2 s of task time).</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Lazy evaluation and the lineage DAG</h2>
''' + def_block(
    '<b>Lazy evaluation</b> means that RDD transformations are not executed when they are called; Spark records each new RDD with its dependencies on parent RDDs, forming a <b>lineage graph</b> (a directed acyclic graph, DAG). When an <b>action</b> is invoked, the DAGScheduler builds stages from the graph, splitting at shuffle (wide) dependencies and pipelining narrow transformations within each stage, and submits tasks. Each action re-evaluates the lineage from its sources, except where results are already available: RDDs persisted with <code>cache()</code>/<code>persist()</code>, and shuffle outputs from earlier stages, which allow those stages to be <b>skipped</b>. Errors in user functions surface only when the action runs the corresponding tasks. The lineage also provides fault tolerance by allowing lost partitions to be recomputed.',
    'Spark writes down your steps instead of doing them. When you ask for a result, it plans and runs everything needed. Each new request runs the steps again, unless results were kept in memory (cache) or Spark can reuse earlier shuffle data.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Lazy evaluation', 'Transformations are recorded, not run, until an action.'),
    ('Lineage', 'The chain of parent RDDs; <code>toDebugString()</code> shows it.'),
    ('DAG', 'Directed acyclic graph: steps with arrows, no cycles.'),
    ('DAGScheduler', 'The driver part that cuts the DAG into stages.'),
    ('Pipelining', 'Running several narrow steps in one pass over a partition.'),
    ('Skipped stage', 'A stage whose shuffle output already exists.'),
    ('cache()', 'Keep an RDD’s partitions in memory after first use.'),
    ('Storage level', 'Where and how cached data is kept (memory, disk, serialised).'),
]) + '''

  <h3>Laziness in RDDs and DataFrames</h3>
''' + table(['', 'RDD', 'DataFrame'], [
    ['Transformations run', 'At the action', 'At the action'],
    ['Errors in your code appear', 'At the action (Python worker error)', 'Column/type errors at once (analysis); data errors at the action'],
    ['Optimisation before running', 'None: steps run as written', 'Catalyst rewrites the whole plan'],
    ['See the plan', '<code>rdd.toDebugString()</code>', '<code>df.explain()</code>'],
    ['Reuse between actions', 'cache, shuffle files', 'cache, shuffle files, AQE reuse'],
], minw=680) + lv + '''
EXAM> “What is lazy evaluation and why does Spark use it?” Transformations only build a lineage DAG; actions trigger execution. Spark can then pipeline narrow operations into stages, avoid unnecessary work, optimise (for DataFrames), and recover lost partitions from lineage. The cost: each action recomputes the lineage unless data is cached or shuffle output is reused.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>What Spark reuses, and what it recomputes</h2>
''' + table(['Situation', 'Recomputed on the next action?', 'Seen in the lab'], [
    ['Plain RDD, narrow steps only', 'Yes, from the source', 'tokenize ran 48,000 times for 2 actions'],
    ['After <code>cache()</code> (once filled)', 'No, read from executor memory', '24,000 calls; job D 0.3 s'],
    ['Before a shuffle that already ran', 'No, shuffle files reused (stage skipped)', 'Job B: stage 2 skipped'],
    ['Cached partition lost (executor died)', 'Only that partition, from lineage', 'Lesson 1.3'],
    ['After <code>checkpoint()</code>', 'No; lineage is cut and saved to storage', 'Lesson 3.3'],
], minw=680) + '''
WARN> Reused shuffle files are a bonus, not a plan: they disappear when executors are lost or the shuffle data is cleaned up, and they only cover work <b>before</b> the shuffle. If you will use an RDD several times, <code>cache()</code> it deliberately and <code>unpersist()</code> it afterwards.
</section>
'''

FIG1 = fig('ui-rdd-skipped.webp', 1280, 700, 'Job details DAG with stage 2 skipped and stage 3 run', 'Real screenshot: job B, the second <code>count()</code> without cache. Stage 2 (textFile, flatMap, map) is grey and <b>skipped</b>: Spark reused the shuffle files written by job A.')
FIG2 = fig('ui-rdd-cached.webp', 1280, 700, 'Job details DAG with a green dot marking a cached RDD in stage 7', 'Real screenshot: job D after <code>cache()</code>. The green dot in stage 7 marks the cached RDD; the filter ran on it directly.')
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Watching laziness happen</h2>
  <p>All outputs are real: PySpark 4.3.0 in local mode (Steps 1–4) and on the standalone cluster (Steps 5–6). Data: three months of TiffinGo reviews, 24,000 lines in 3 files.</p>
''' + stepper([
    ('Step 1 · A bug that waits for an action',
     code('python', 'lazy.py', 'lines = sc.textFile("reviews")\nbad = lines.map(lambda l: len(l) / 0)\nprint("defined bad RDD, no error yet:", bad)\nbad.count()', has('l23_lazy.txt', 'defined bad') + '\nERROR Executor: Exception in task 1.0 in stage 0.0 (TID 1)\norg.apache.spark.api.python.PythonException: [PYTHON_EXCEPTION] An exception was thrown from the Python worker: …\n  File "lazy.py", line 8, in &lt;lambda&gt;\n    bad = lines.map(lambda l: len(l) / 0)\nZeroDivisionError: division by zero'.replace('&lt;', '<') + '\n' + has('l23_lazy.txt', 'at count()')),
     'Defining <code>bad</code> was accepted: Spark cannot check what a Python lambda will do. The error appeared at <code>count()</code>, raised inside a <b>Python worker</b> on an executor and reported with the original line. In long pipelines, the line where the error is reported is the action, not the bug. Test functions on a small sample with <code>take()</code> while developing.'),
    ('Step 2 · Read the lineage',
     code('python', 'lazy.py', 'counts = (lines.flatMap(lambda l: l.split())\n               .map(lambda w: (w, 1))\n               .reduceByKey(lambda a, b: a + b)\n               .filter(lambda kv: kv[1] > 5000))\nprint(counts.toDebugString().decode())', LINEAGE_SHORT),
     'Read bottom-up. <code>HadoopRDD</code> and <code>MapPartitionsRDD</code> come from <code>textFile</code>. PySpark <b>fused</b> <code>flatMap</code> and <code>map</code> into one <code>PythonRDD[4]</code>: pipelining in action. <code>+-(3)</code> marks a <b>shuffle boundary</b>: everything indented below it is one stage (3 tasks), everything above is the next stage, starting with <code>ShuffledRDD</code>. The <code>filter</code> after <code>reduceByKey</code> was fused into the final <code>PythonRDD[8]</code>.'),
    ('Step 3 · Every action recomputes',
     code('python', 'lazy.py', 'calls = sc.accumulator(0)\ndef tokenize(l):\n    calls.add(1)\n    return l.split()\nwords = lines.flatMap(tokenize)\nwords.count(); words.distinct().count()\nprint("no cache:", calls.value)\n\ncalls.value = 0\nwords_c = lines.flatMap(tokenize).cache()\nwords_c.count(); words_c.distinct().count()\nprint("cached  :", calls.value, words_c.getStorageLevel())', has('l23_lazy.txt', 'tokenize()', 'storage level')),
     'Two actions on an uncached RDD ran <code>tokenize</code> <b>48,000 times</b> for 24,000 lines: the whole lineage was executed twice, file reading included. After <code>cache()</code>, the first action filled the cache and the second read from memory: 24,000 calls. RDD <code>cache()</code> in PySpark stores <b>serialised</b> data in memory (“Memory Serialized 1x Replicated”).'),
    ('Step 4 · Laziness lets Spark do less',
     code('python', 'take.py', 'lines.map(lambda l: l.upper()).take(5)     # only as many partitions as needed\nlines.map(lambda l: l.upper()).count()     # every partition\n# jobs and tasks read from the UI\'s REST API (port 4040)', capf('l23_take.txt')),
     'Because nothing runs early, Spark knows what the action actually needs. <code>take(5)</code> ran only on the first partition; <code>count()</code> on all three. The same idea lets DataFrames push filters into file scans (Lesson 7.3). With RDDs, Spark cannot reorder your lambdas, but it still avoids running what no action asked for.'),
    ('Step 5 · The DAG on the cluster: stages and skipping',
     code('python', 'rdd_dag.py (cluster)', 'counts = lines.flatMap(lambda l: l.split()).map(lambda w: (w, 1)).reduceByKey(add)\nsc.setJobDescription("A: top words (no cache)");      counts.takeOrdered(3, key=lambda kv: -kv[1])\nsc.setJobDescription("B: count() again, no cache");   counts.count()\ncounts.cache()\nsc.setJobDescription("C: count after cache() - fills the cache"); counts.count()\nsc.setJobDescription("D: filter on the cached RDD");  counts.filter(lambda kv: kv[1] > 5000).count()', capf('l23_cluster.txt') + '\n\n' + capf('l23_rest.txt')) + FIG1,
     'Job A ran both stages: 14.0 s of task time, mostly reading and tokenising. Job B, without any cache, <b>skipped</b> the map stage and took 0.2 s: the shuffle files from job A were still on the executors, so Spark started from them. Only the work <b>after</b> the shuffle reran. “and” and “was” top the list because every review contains them; Lesson 2.5 filters such words out.'),
    ('Step 6 · A cached RDD in the DAG',
     code('text', 'Jobs → job 3 → DAG Visualization', 'stage 6 skipped (shuffle files reused)\nstage 7: partitionBy → mapPartitions → ● cached RDD → filter → count') + FIG2,
     'After <code>cache()</code>, job C computed the reduced RDD once more and stored it; job D found it in memory (the <b>green dot</b>) and only ran the filter. The Storage tab would list the RDD with its size and fraction cached. Lesson 3.1 compares storage levels and their costs.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('bad = lines.map(lambda l: len(l) / 0)', W), ('defined bad RDD, no error yet', G), ('bad.count()', W), ('ZeroDivisionError: division by zero', RD)], size=7.2),
    term([('(3) PythonRDD[8]', W), (' |  ShuffledRDD[6]', W), (' +-(3) PairwiseRDD[5]   ← shuffle', Y), ('    |  textFile', W)], size=7.2),
    term([('no cache: tokenize() calls 48000', RD), ('cached  : tokenize() calls 24000', G), ('Memory Serialized 1x Replicated', W)], size=7.2),
    term([('job A: stage 0 + stage 1   14.0 s', W), ('job B: stage 2 skipped      0.2 s', G), ('shuffle files reused', G)], size=7.4),
    term([('counts.cache(); counts.count()', W), ('job D: filter on cached RDD 0.3 s', G), ('green dot in the DAG', G)], size=7.4),
]
B1 = [
    t(180, 14, 'Nothing runs at definition', 9.4, bold=True) + dag(1) + cap('Errors appear when tasks run.', '', 'amber', y=112, h=30),
    t(180, 14, 'Shuffles cut stages', 9.4, bold=True) + dag(3) + cap('+-(3) in toDebugString = new stage.', '', 'blue', y=112, h=30),
    t(180, 14, 'Each action walks the graph', 9.4, bold=True) + dag(0) + cap('Unless a result is kept.', '', 'amber', y=112, h=30),
    t(180, 14, 'Shuffle output is reused', 9.4, bold=True) + dag(4, skipped=True) + cap('Stage A skipped on the 2nd action.', '', 'green', y=112, h=30),
    t(180, 14, 'Cache cuts the walk short', 9.4, bold=True) + dag(4, skipped=True, cached=True) + cap('Read from memory, run the rest.', '', 'green', y=112, h=30),
]
see_caps = ['A broken map was accepted; count() failed.',
            'The lineage shows one shuffle boundary.',
            'Without cache, the tokenizer ran twice per line.',
            'The second action skipped the map stage.',
            'The cached RDD served the last action.']
behind_caps = ['Transformations only add nodes to the DAG.',
               'flatMap and map were pipelined into one PythonRDD.',
               'Lineage is evaluated from the source per action.',
               'Shuffle files from job A were still there.',
               'Only the filter ran on cached data.']
two = anim_two('Lazy evaluation', 'A plan that runs on demand', 'Real lab outputs', 'The DAG underneath', see, B1, see_caps, behind_caps)

# ---- scenario 1: error far from bug
e1 = (t(180, 22, 'Nightly job fails at write()', 9.4, bold=True) + t(180, 56, 'ValueError in a Python worker', 8.4, 'ink', mono=True) + cap('The bug is 40 lines earlier.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Read the Python traceback', 9.4, bold=True) + t(180, 56, 'File "job.py", line 12, in parse', 8.4, 'ink', mono=True) + cap('It names the real line.', '', 'green', y=150, h=34))
e3 = (t(180, 22, 'Reproduce on a sample', 9.4, bold=True) + t(180, 56, 'rdd.map(parse).take(100)', 8.4, 'ink', mono=True) + cap('Fast feedback.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Find the bad record', 9.4, bold=True) + t(180, 56, 'try/except → tag bad rows', 8.4, 'ink2') + cap('Do not crash on one line.', '', 'amber', y=150, h=34))
e5 = (t(180, 22, 'Test functions alone', 9.4, 'acc', bold=True) + t(180, 56, 'pytest on parse() without Spark', 8.4, 'ink2') + cap('Lesson 11.4.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'An error reported far from its cause',
              'What laziness means for debugging. (Typical; behaviour from our lab.)',
              'Lazy errors', 'Errors in lambdas surface at the action; read the Python traceback, reproduce with take() and test functions outside Spark', [e1, e2, e3, e4, e5],
              ['Fails at the end.', 'Traceback points back.', 'Sample it.', 'Handle bad records.', 'Unit-test functions.'],
              hid='scenario-lazyerror')

# ---- scenario 2: reports twice as slow
b1 = (t(180, 22, 'Three reports, one RDD', 9.4, bold=True) + t(180, 56, 'top dishes · complaints · counts', 8.4, 'ink2') + cap('Each 10 minutes.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Look at the DAG', 9.4, bold=True) + t(180, 56, 'parsing stage runs 3 times', 8.4, 'ink2') + cap('Like our 48,000 calls.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'cache() the parsed RDD', 9.4, bold=True) + t(180, 56, 'parsed = raw.map(parse).cache()', 8.4, 'ink', mono=True) + cap('Parse once.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Check the Storage tab', 9.4, bold=True) + t(180, 56, 'fraction cached: 100%', 8.4, 'ink', mono=True) + cap('Fits in memory?', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'unpersist() at the end', 9.4, 'acc', bold=True) + t(180, 56, '10 + 2 + 2 minutes', 8.4, 'ink2') + cap('Instead of 30.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Three reports that each parse everything',
              'The cost of forgetting laziness. (Typical; counts from our lab.)',
              'Reuse with cache', 'Each action recomputes the lineage; cache the shared RDD once, verify it in the Storage tab and unpersist afterwards', [b1, b2, b3, b4, b5],
              ['Three actions.', 'Parsing three times.', 'Cache once.', 'Verify.', 'Release.'],
              hid='scenario-reports')

# ---- scenario 3: very long lineage
u1 = (t(180, 22, 'Iterative job, 200 loops', 9.4, bold=True) + t(180, 56, 'rdd = rdd.map(update) in a loop', 8.4, 'ink', mono=True) + cap('Lineage grows every loop.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Driver slows, then fails', 9.4, bold=True) + t(180, 56, 'StackOverflowError in the scheduler', 8.2, 'ink', mono=True) + cap('A 200-step graph.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'A lost partition', 9.4, bold=True) + t(180, 56, 'recompute all 200 steps', 8.4, 'ink2') + cap('Very slow recovery.', '', 'amber', y=150, h=34))
u4 = (t(180, 22, 'checkpoint() every 20 loops', 9.4, bold=True) + t(180, 56, 'sc.setCheckpointDir(…); rdd.checkpoint()', 8, 'ink', mono=True) + cap('Saves data, cuts lineage.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Short lineage again', 9.4, 'acc', bold=True) + t(180, 56, 'Lesson 3.3', 8.4, 'ink2') + cap('Fast recovery, stable driver.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'When the lineage gets too long',
              'Why iterative jobs need checkpoints. (Typical.)',
              'Long lineage', 'Iterative jobs grow the lineage each loop; checkpointing saves the data and cuts the graph', [u1, u2, u3, u4, u5],
              ['Lineage grows.', 'Scheduler struggles.', 'Recovery is slow.', 'Checkpoint.', 'Short graph.'],
              hid='scenario-lineage')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>A plan that runs on demand</h2>
  <p>Left: real outputs. Right: the DAG underneath.</p>
''' + two + '''
  <p>Three live scenarios follow: an error far from its cause, reports that repeat work, and a lineage that grows too long.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Laziness at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'sample', 11, 'blue', bold=True) + t(60, 58, 'first', 7.4, 'ink2'),
    '1. Developing on samples',
    'Engineers test each step with take() on a few rows before running the full action on terabytes.',
    ['Code', '*take(10)', 'Full run']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'cache', 11, 'green', bold=True) + t(60, 58, 'reuse', 7.4, 'ink2'),
    '2. Shared intermediate data',
    'One parsed dataset feeds several reports; it is cached once and released after the last report.',
    ['Parse', '*cache', 'Reports']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'DAG', 12, 'violet', bold=True) + t(60, 58, 'review', 7.4, 'ink2'),
    '3. Reading DAGs in reviews',
    'toDebugString and the DAG view show unintended shuffles and repeated stages before a job ships.',
    ['Job', '*DAG', 'Fix']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'ML', 12, 'acc', bold=True) + t(60, 58, 'iterations', 7.4, 'ink2'),
    '4. Iterative algorithms',
    'Graph and ML algorithms cache their working set and checkpoint periodically to keep lineage short.',
    ['Loop', '*cache + checkpoint', 'Converge']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'debug', 11, 'acc', bold=True) + t(60, 58, 'workers', 7.4, 'ink2'),
    '5. Debugging Python workers',
    'PythonException tracebacks in executor logs point to the line in your function that failed.',
    ['Action fails', '*traceback', 'Fix line']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> Lessons <a href="../02-transformations-and-actions/">2.2</a> (operations) and <a href="../../01-introduction/04-how-a-spark-job-runs/">1.4</a> (jobs, stages, tasks).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
