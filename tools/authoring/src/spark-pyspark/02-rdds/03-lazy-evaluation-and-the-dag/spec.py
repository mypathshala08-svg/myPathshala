import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
BODY = body(HERE)

META = dict(
    module='02-rdds', lesson='03-lazy-evaluation-and-the-dag', n='2.3',
    module_label='Module 2 · RDDs: Spark’s foundation',
    title='Lazy evaluation, lineage and the DAG',
    desc='How Spark’s laziness really behaves, measured with PySpark 4.3.0: a division by zero accepted at definition and raised at count(), the lineage of a word count read line by line with toDebugString(), a tokenizer running 48,000 times without cache and 24,000 with it, take(5) running 1 task while count() runs 3, and on the cluster a second action skipping its map stage because Spark reused the shuffle files (14.0 s → 0.2 s), with real DAG screenshots.',
    og_desc='A bug that waits for count(), a tokenizer that runs twice, and a stage Spark skips on its own: lazy evaluation and the DAG, measured.',
    minutes=32, level='Intermediate',
    lead='Lazy evaluation is the idea that explains most surprises in Spark: errors that appear in the wrong place, work that runs twice, and work that mysteriously does not run at all. This lesson measures each one on TiffinGo’s reviews and reads the <b>lineage DAG</b> as text and in the Spark UI. <b>All outputs and screenshots are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', 'toDebugString() explained', 'Skipped stages, explained', 'Runs in your browser (Python)'],
)

MAIN = '''# A lazy pipeline with a call counter: what runs, and how often?
calls = {"tokenize": 0}
def tokenize(line):
    calls["tokenize"] += 1
    return line.split()

lines = ["poha was tasty and hot", "idli was cold and late", "dosa was fresh and hot"]

plan = lambda: (w for l in lines for w in tokenize(l))     # a recipe, nothing runs yet
print("after defining:", calls)
print("count:", sum(1 for _ in plan()))                      # action 1
print("distinct:", len(set(plan())))                         # action 2
print("after 2 actions, no cache:", calls)

calls["tokenize"] = 0
cached = list(plan())                                        # cache = keep the result
print("count:", len(cached), "distinct:", len(set(cached)))
print("after 2 actions, cached:", calls)
'''
RUN = dict(
    heading='Run the code: count what laziness costs',
    intro='<p>A Python generator behaves like an uncached RDD: defining it runs nothing, and every consumer runs it again. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('plan = lambda: (w for l in lines for w in tokenize(l))     # a recipe, nothing runs yet', 'Like rdd.flatMap(tokenize): a description, not a result.'),
        ('cached = list(plan())                                        # cache = keep the result', 'Like rdd.cache() followed by the first action.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>: 6 calls without cache, 3 with cache, the same ratio as 48,000 vs 24,000 in the lab.', code=None),
        dict(label='2 · Predict first: three actions', hint='<b>Predict first:</b> how many tokenize calls for three actions on 24,000 lines without cache?',
             code='''lines, actions = 24_000, 3
print("no cache:", lines * actions, "| cached:", lines)
'''),
        dict(label='3 · take() stops early', hint='Simulate take(2) on 3 partitions: stop when enough elements are found.',
             code='''partitions = [["a", "b", "c"], ["d", "e"], ["f"]]
taken, tasks = [], 0
for p in partitions:
    tasks += 1
    taken += p[: 2 - len(taken)]
    if len(taken) == 2:
        break
print(taken, "tasks run:", tasks)
'''),
        dict(label='4 · Where are the stages?', hint='Cut a pipeline into stages at wide operations.',
             code='''ops = ["textFile", "flatMap", "map", "reduceByKey", "filter", "sortBy", "take"]
wide = {"reduceByKey", "groupByKey", "sortBy", "distinct", "join", "repartition"}
stages, cur = [], []
for op in ops:
    if op in wide and cur:
        stages.append(cur); cur = []
    cur.append(op)
stages.append(cur)
for i, s in enumerate(stages):
    print("stage", i, s)
'''),
        dict(label='5 · Spot the error', hint='This test passes because nothing ran.', expect='error',
             code='''ran = False
def parse(x):
    global ran; ran = True
    return 1 / 0
pipeline = (parse(x) for x in [1, 2, 3])    # lazy: like rdd.map(parse)
assert ran, "nothing executed: call an action (e.g. take) in your test"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: look at lineage and reuse',
    intro='<p>In the <code>pyspark</code> shell with the reviews folder. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Lineage of a word count', cmd='counts = sc.textFile("reviews").flatMap(lambda l: l.split()).map(lambda w: (w, 1)).reduceByKey(lambda a, b: a + b)\nprint(counts.toDebugString().decode())', file='pyspark',
             output=capf('l23_lazy.txt')[capf('l23_lazy.txt').index('(3) PythonRDD[8]'):capf('l23_lazy.txt').index('3) Every action')].rstrip(),
             note='This output also includes a final filter (PythonRDD[8]). +-(3) is the shuffle boundary.'),
        dict(title='2 · Cache and its storage level', cmd='words = sc.textFile("reviews").flatMap(lambda l: l.split()).cache()\nwords.count()\nrepr(words.getStorageLevel()); print(words.getStorageLevel())', file='pyspark',
             output=capf('l23_storage.txt'),
             note='PySpark RDDs are cached serialised in memory by default.'),
        dict(title='3 · Jobs and tasks for take and count', cmd='lines.map(lambda l: l.upper()).take(5)\nlines.map(lambda l: l.upper()).count()', file='pyspark',
             output=capf('l23_take.txt'), note='Counted through the UI REST API on port 4040.'),
    ],
)

TRACE = dict(
    heading='How the scheduler decides what to run',
    intro='<p>Follow the DAGScheduler’s decision for the second action in Step 5.</p>',
    code='''stages = {"A (map side)": {"needs": None, "output_exists": True},
          "B (reduce side)": {"needs": "A (map side)", "output_exists": False}}
to_run = []
for name, s in stages.items():
    if s["output_exists"]:
        print(name, "-> skipped (shuffle files available)")
    else:
        to_run.append(name)
print("run:", to_run)
''',
    notes={1: 'Map side :: Its shuffle files were written by the first action.', 5: 'Skipped :: Shown grey in the DAG view.', 8: 'Run :: Only the stage after the shuffle executes.'},
)

WORKED_INTRO = 'Three ways laziness shows up in real work.'
EXAMPLES = [
    dict(level='b', tag='Debugging · laziness', title='Find a bug before the full run',
         problem='<p>Test a parsing function on a few lines before running the whole job.</p>',
         inp='reviews folder',
         approach=['Define the RDD.', 'take(5) to force a small run.', 'Fix, then run the action.'],
         code='''def parse(line):
    dish, rest = line.split(" was ")
    return dish, rest.split(" and ")
print([parse(l) for l in ["poha was tasty and hot", "idli was cold and late"]])
''', notes={1: 'Spark :: sc.textFile("reviews").map(parse).take(5) runs only one task.'},
         tryit='A line without " was " would raise ValueError: handle it before the full run.'),
    dict(level='i', tag='Performance · reuse', title='Should I cache?',
         problem='<p>Decide whether to cache an RDD used by several actions.</p>',
         inp='cost per pass and number of actions',
         approach=['Count actions using it.', 'Compare recompute cost with memory.', 'Cache only if reused.'],
         code='''pass_s, actions = 14.0, 3
print("no cache:", pass_s * actions, "s  | cache:", pass_s + 0.3 * (actions - 1), "s (approx.)")
''', notes={1: 'Numbers :: 14.0 s for job A, 0.3 s for job D in our lab.'},
         tryit='If it is used once, caching only costs memory.'),
    dict(level='a', tag='Internals · stages', title='Predict skipped stages',
         problem='<p>Which stages run for a second action on a reduced RDD?</p>',
         inp='counts = ...reduceByKey(add)',
         approach=['Map stage wrote shuffle files.', 'They still exist.', 'Only the reduce stage runs.'],
         code='''shuffle_files_exist = True
print("map stage:", "skipped" if shuffle_files_exist else "run", "| reduce stage: run")
''', notes={1: 'Exist :: Until executors are lost or shuffle data is cleaned up.'},
         tryit='Stop a worker between the two actions and the map stage runs again (Lesson 1.3).'),
]

QUIZ = mix([
    dict(q='Beginner: When does rdd.map(f) run f?', options=['Immediately', 'When an action needs the result', 'When you print the RDD', 'Never'], answer=1,
         why='Transformations only record the step.'),
    dict(q='Beginner: Where did ZeroDivisionError appear?', options=['On the map line', 'At count()', 'At import', 'Nowhere'], answer=1,
         why='The lambda ran only during the action.'),
    dict(q='Beginner: What does toDebugString() show?', options=['The data', 'The lineage of the RDD', 'The logs', 'The schema'], answer=1,
         why='Parents, partitions and shuffle boundaries.'),
    dict(q='Intermediate: How many tokenize calls for 2 actions on 24,000 lines without cache?', options=['24,000', '48,000', '2', '0'], answer=1,
         why='The lineage ran twice.'),
    dict(q='Intermediate: What does +-(3) mean in toDebugString output?', options=['3 errors', 'A shuffle boundary; the stage below has 3 partitions', '3 cached copies', 'Python version'], answer=1,
         why='Indentation marks a new stage.'),
    dict(q='Intermediate: How many tasks did take(5) run on 3 partitions?', options=['3', '1', '5', '0'], answer=1,
         why='It stopped after the first partition.'),
    dict(q='Advanced: Why was the second action’s map stage skipped without cache?', options=['Bug', 'Shuffle files from the first action were reused', 'AQE', 'Speculation'], answer=1,
         why='14.0 s → 0.2 s of task time.'),
    dict(q='Advanced: Which fused flatMap and map into one PythonRDD?', options=['Catalyst', 'Pipelining of narrow Python transformations', 'cache()', 'The shuffle'], answer=1,
         why='One pass per partition.'),
])

REVISION = [
    'Transformations build a <b>lineage DAG</b>; actions run it. RDD lambda errors appear at the <b>action</b>.',
    '<code>toDebugString()</code>: read bottom-up; <code>+-(n)</code> = shuffle boundary; narrow Python steps fused into one PythonRDD.',
    'Each action re-evaluates the lineage: 48,000 tokenizer calls for 2 actions vs 24,000 with <code>cache()</code>.',
    'PySpark RDD cache default: memory, serialised.',
    'Laziness lets Spark do less: <code>take(5)</code> = 1 task, <code>count()</code> = 3 tasks.',
    'Shuffle files are reused across actions: map stage <b>skipped</b> (14.0 s → 0.2 s).',
    'Cache deliberately, unpersist afterwards; checkpoint long lineages (Lesson 3.3).',
]
FAQ = [
    ('Is DataFrame evaluation lazy too?', 'Execution is lazy, like RDDs. Analysis is eager: column names and types are checked when you define the transformation (Lesson 1.4). Errors inside Python UDFs still appear at the action.'),
    ('Why not run each transformation immediately?', 'Running at the action lets Spark see the whole pipeline, pipeline narrow steps into one pass, avoid unnecessary work and (for DataFrames) optimise the plan. It also keeps lineage small enough to recompute lost data.'),
    ('Does cache() run anything?', 'No. cache() only marks the RDD; the first action fills the cache. That is why examples call count() right after cache().'),
    ('How long do shuffle files stay?', 'Until the RDD that produced them is garbage-collected on the driver, the application ends, or the executor holding them is lost. They are not a replacement for caching.'),
    ('Can I see the DAG without the UI?', 'For RDDs, toDebugString(); for DataFrames, explain(). The UI’s DAG visualisation shows stages, skipped stages and cached RDDs graphically.'),
]

PRACTICE_INTRO = 'Programs about laziness, recomputation and stages.'
PROBLEMS = [
    dict(level='easy', title='Lazy generator', stmt='Show that a generator does nothing until consumed.', inp='three numbers',
         code='''def f(x):
    print("running", x); return x * 2
g = (f(x) for x in [1, 2, 3])
print("defined")
print(sum(g))
''', explain='Like an RDD transformation followed by an action.'),
    dict(level='easy', title='Recompute cost', stmt='Function calls for k actions without cache.', inp='24,000 lines, 4 actions',
         code='''print(24_000 * 4)
''', explain='With cache: 24,000.'),
    dict(level='easy', title='Stage count', stmt='Stages for textFile → flatMap → reduceByKey → collect.', inp='one wide op',
         code='''print(2)
''', explain='One shuffle = two stages.'),
    dict(level='medium', title='Read a lineage', stmt='Count shuffle boundaries in a toDebugString output.', inp='text',
         code='''s = """(3) PythonRDD[8]
 |  ShuffledRDD[6]
 +-(3) PairwiseRDD[5]
    |  HadoopRDD[0]"""
print(s.count("+-("))
''', explain='Each +-( starts a parent stage.'),
    dict(level='medium', title='take() tasks', stmt='Tasks needed for take(n) with partition sizes.', inp='[8000, 8000, 8000], n=10000',
         code='''sizes, n, tasks, got = [8000, 8000, 8000], 10_000, 0, 0
for s in sizes:
    tasks += 1; got += s
    if got >= n: break
print(tasks)
''', explain='Spark actually scales up the number of partitions it tries in each round.'),
    dict(level='medium', title='Cache benefit', stmt='Time saved by caching for 3 actions.', inp='14.0 s first pass, 0.3 s later',
         code='''print(3 * 14.0 - (14.0 + 2 * 0.3), "s saved")
''', explain='Roughly what our cluster numbers suggest.'),
    dict(level='business', title='Debugging time', stmt='Time saved by testing on take(100) first.', inp='full run 40 min, sample 30 s, 3 bugs',
         code='''print(3 * 40 - 3 * 0.5, "minutes saved")
''', explain='Laziness makes sample tests cheap.'),
    dict(level='business', title='Repeated work bill', stmt='Extra cluster time for 3 uncached reports per night.', inp='10 min parsing each, 30 nights',
         code='''print(2 * 10 * 30 / 60, "hours per month")
''', explain='Cache the parsed data once.'),
]

SCN_INTRO = 'Laziness and lineage questions test real understanding of Spark.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“What is lazy evaluation?”',
        'Explain lazy evaluation in Spark.',
        'do you know the benefit and the cost?',
        '<p>Transformations only record a lineage graph; Spark runs it when an action asks for a result. Benefits: pipelining, less unnecessary work, optimisation and recomputation of lost data. Cost: each action recomputes the lineage unless data is cached, and errors in my functions appear only at the action.</p>', 'Saying Spark is lazy because it caches everything.') +
    scn('Data engineering', 'Mid-level', 'Error at the wrong line',
        'A job fails at saveAsTextFile with a KeyError from a parse function.',
        'can you debug lazily evaluated code?',
        '''<ol>
          <li>Read the Python traceback in the PythonException: it names the function and line.</li>
          <li>Reproduce with rdd.map(parse).take(n) on a sample.</li>
          <li>Handle bad records explicitly; unit-test the function without Spark.</li>
        </ol>''', 'Blaming saveAsTextFile.') +
    scn('Data engineering', 'Mid-level', 'Second report as slow as the first',
        'Two actions on the same RDD each take 10 minutes.',
        'do you know what is reused?',
        '''<ul>
          <li>Each action recomputes the lineage; shuffle output may be reused, narrow work is not.</li>
          <li>Cache the shared RDD, trigger it once, check the Storage tab, unpersist later.</li>
        </ul>''', 'Adding more partitions.') +
    scn('Platform', 'Senior', 'Explain skipped stages',
        'A manager asks why the UI shows “skipped” stages.',
        'can you explain shuffle reuse?',
        '''<ul>
          <li>The stage’s output (shuffle files) already exists from an earlier job, so it is not rerun.</li>
          <li>Common with AQE (separate map-stage jobs) and repeated actions on the same shuffled RDD.</li>
          <li>Skipped is good; it means saved work.</li>
        </ul>''', '“Skipped means it failed.”')
)
