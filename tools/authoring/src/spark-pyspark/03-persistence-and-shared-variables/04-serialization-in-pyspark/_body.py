import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit2 import *
C = 'l34_serial.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('A one-line lambda that looks up a price from a dict. Why did Spark send 2.8 MB with every single task?',
    'Because PySpark must <b>serialize</b> your function, and everything it captures, to send it to Python workers on the executors. The dict came along each time. With a <b>broadcast</b> the same function was 635 bytes. Serialization is the hidden tax in PySpark: code with cloudpickle, rows with pickle or Arrow. In our lab Arrow made <code>toPandas()</code> 6.5× faster (14.5 s → 2.2 s), while the old “use MarshalSerializer” advice made no measurable difference.',
    ['What gets serialized in PySpark, and when.',
     'pickle, cloudpickle, marshal and Arrow, measured.',
     'Avoiding big closures and unpicklable objects.'])
cmap = concept_map('Concept map. Beginner: objects to bytes, why it is needed. Intermediate: cloudpickle for functions, pickle/marshal for data, AutoBatchedSerializer, Arrow. Advanced: closure capture, broadcast, unpicklable objects, Kryo on the JVM side.',
    [[('ar', 'Python ↔ JVM', 'Lesson 1.3', B + '01-introduction/03-spark-architecture/'), ('wh', 'Why serialize', 'network, disk, cache', None)],
     [('cp', 'cloudpickle', 'functions', None), ('pk', 'pickle / marshal', 'records', None), ('ab', 'AutoBatched', 'batches', None), ('aw', 'Arrow', 'columns', B + '04-dataframes/06-collect-topandas-and-arrow/')],
     [('cl', 'Closure capture', 'hidden size', None), ('bc', 'Broadcast', 'Lesson 3.2', B + '03-persistence-and-shared-variables/02-broadcast-variables-and-accumulators/'), ('up', 'Unpicklable objects', 'locks, connections', None), ('kr', 'Kryo (JVM)', 'not for Python', None)]],
    [('ar', 'wh'), ('wh', 'cp'), ('wh', 'pk'), ('pk', 'ab'), ('wh', 'aw'), ('cp', 'cl'), ('cl', 'bc'), ('cp', 'up'), ('pk', 'kr')],
    {'wh', 'cp', 'pk', 'ab', 'aw', 'cl', 'up', 'kr'},
    '<b>Builds on:</b> <a href="../02-broadcast-variables-and-accumulators/">3.2 Broadcast</a>. <b>Next:</b> <a href="../../04-dataframes/01-sparksession-and-dataframes/">4.1 DataFrames</a>.')
whw = why_how_where(
    'Python objects live in one process. To run your function on 100 executors, or move records between Python and the JVM, Spark must turn them into bytes and back. That costs CPU, memory and network, and some objects cannot be turned into bytes at all.',
    'Your functions (and captured variables) are serialized with <b>cloudpickle</b> and shipped with each task. RDD records move between the JVM and Python workers as batched pickled bytes (<code>AutoBatchedSerializer</code>). DataFrame↔pandas transfers and pandas/Arrow UDFs use <b>Apache Arrow</b> columnar batches. JVM-only data (DataFrames, shuffles) uses Spark’s own binary formats; Kryo is a JVM option.',
    'Every UDF, map/filter lambda, broadcast, collect/toPandas and createDataFrame from Python objects.',
    'Large captured objects inflate every task; unpicklable objects (locks, DB connections, sockets) fail; pickle is Python-only and trusts its input.')

def pipe(hl=-1):
    parts = [('driver', 'your lambda', 'card'), ('cloudpickle', 'bytes', 'violet'), ('executor JVM', 'task', 'blue'), ('Python worker', 'unpickle + run', 'green')]
    o = ''
    for k, (n, d, tn) in enumerate(parts):
        o += box(6 + k * 88, 34, 80, 44, 'acc' if k == hl else tn, rx=6) + t(46 + k * 88, 52, n, 7.4, bold=True) + t(46 + k * 88, 68, d, 6.6)
        if k < 3: o += arrow(86 + k * 88, 56, 94 + k * 88, 56)
    return o + t(176, 20, 'every task carries the function and what it captured', 7.2) + t(176, 100, 'rows: pickle batches · DataFrames↔pandas: Arrow', 7.0)
scene_svg = scene('Serialization path: on the driver your lambda is turned into bytes by cloudpickle, sent with each task to the executor JVM, and unpickled and run by a Python worker; rows move as pickle batches and DataFrame-to-pandas transfers use Arrow.', pipe(),
                  'Code and data cross process boundaries as <tspan font-weight="700" class="s-acc">bytes</tspan>.')
dialogue = '''K> Sir, the old tutorial says “use MarshalSerializer, it is faster than pickle”. Should we switch?
A> Measure first. And check what is actually slow: often it is not the serializer but what you ask it to carry.
R> Like what?
A> Like a big dictionary hidden inside a lambda, or rows converted one by one instead of in Arrow columns. Let’s measure each.'''

lv = '''
LEVELS> Serialization at three levels
L1> Packing for a trip
      <ul>
        <li>Every worker needs your recipe (function). If you tape the whole pantry (big dict) to each recipe card, every card becomes heavy. Better: put the pantry in each kitchen once (broadcast) and keep the card light.</li>
      </ul>
L2> What PySpark uses
      <ul>
        <li><b>Functions</b>: cloudpickle (can serialize lambdas and closures that plain <code>pickle</code> cannot).</li>
        <li><b>RDD records</b>: <code>SparkContext(serializer=…)</code>, default CloudPickle/Pickle wrapped in <code>AutoBatchedSerializer</code>; <code>MarshalSerializer</code> only for simple built-in types.</li>
        <li><b>DataFrames</b>: stay in the JVM; Arrow is used for <code>toPandas()</code>, <code>createDataFrame(pandas)</code>, pandas/Arrow UDFs and (Spark 4) Arrow-optimized Python UDFs (<code>spark.sql.execution.arrow.pyspark.enabled</code>, <code>…pythonUDF.arrow.enabled</code>).</li>
      </ul>
L3> Pitfalls
      <ul>
        <li>Closures capture referenced variables (and sometimes <code>self</code>): check size with <code>pyspark.cloudpickle.dumps(f)</code>. Broadcast large read-only data.</li>
        <li>Unpicklable objects (locks, connections, clients): create them inside <code>mapPartitions</code>/<code>foreachPartition</code>, once per partition.</li>
        <li>Kryo (<code>spark.serializer=org.apache.spark.serializer.KryoSerializer</code>) affects JVM objects (RDDs of JVM types, shuffles in Scala jobs), not Python objects.</li>
      </ul>
/LEVELS
'''
DIS = figure('Size of one task closure: a lambda capturing a 300,000-entry dict is 2,804,549 bytes; the same lambda reading a broadcast variable is 635 bytes.',
    t(16, 22, 'Task closure sizes (real, cloudpickle)', 8.6, 'ink', anchor='start', bold=True) +
    box(16, 40, 600, 22, 'red', rx=4) + t(316, 55, 'lambda x: big.get(x)  →  2,804,549 bytes per task', 8, bold=True) +
    box(16, 72, 6, 22, 'green', rx=2) + t(30, 87, 'lambda x: bb.value.get(x)  →  635 bytes per task (+ data once per executor)', 8, 'ink', anchor='start', bold=True),
    h=110, caption='Bars to scale: broadcasting cut the task payload by ~4,400×.')
extra = '''

  <h3>See the hidden payload</h3>
''' + DIS

types_html = table(['What', 'Serializer', 'Notes'], [
    ['Your functions, lambdas', 'cloudpickle', 'captures referenced variables'], ['RDD records (Python)', 'Pickle/CloudPickle in AutoBatched', 'Marshal optional, simple types only'],
    ['toPandas / createDataFrame(pandas)', 'Arrow (if enabled)', 'columnar, vectorized'], ['pandas / Arrow UDFs', 'Arrow', 'batches of columns'],
    ['Python UDFs (Spark 4 default)', 'Arrow-optimized', 'pythonUDF.arrow.enabled = true'], ['DataFrame rows in the JVM', 'Spark binary (Tungsten)', 'no Python involved'],
    ['JVM RDDs / shuffles (Scala)', 'Java or Kryo', 'spark.serializer'],
], minw=620)
warn = 'Do not copy “switch to MarshalSerializer” advice blindly: in our lab it was not faster once the JVM was warm, and it fails on custom classes. The big wins are avoiding large closures (broadcast instead), keeping work in DataFrames, and enabling Arrow for pandas transfers.'

steps = [
    ('Step 1 · pickle vs marshal',
     code('python', 'l34_serial.py', 'rows = [(i, "idli", 45.0) for i in range(200000)]\npickle.dumps(rows, 5); marshal.dumps(rows)\nmarshal.dumps([Order(1)])', sec('== 1)', '== 2)')),
     'Similar size; marshal faster on plain tuples but cannot handle custom classes.'),
    ('Step 2 · Functions and closures',
     code('python', 'l34_serial.py', 'tax = 1.05; f = lambda x: x * tax\npickle.dumps(f)          # fails\ncloudpickle.dumps(f)     # works\ng = lambda x: big.get(x, 0)   # big = 300k-entry dict', sec('== 2)', '== 3)')),
     'Plain pickle cannot ship lambdas; cloudpickle can, and it ships everything they capture.'),
    ('Step 3 · RDD serializers, measured fairly',
     code('python', 'l34_serial.py', 'SparkContext(conf=conf, serializer=MarshalSerializer())\nsc.parallelize(range(3_000_000), 8).map(lambda x: (x % 100, x)).reduceByKey(add).count()', sec('== 3)', '== 4)')),
     'After a JVM warm-up the three runs were 1.0–1.7 s with no clear winner: the first run is usually slowest whatever its serializer.'),
    ('Step 4 · Unpicklable objects',
     code('python', 'l34_serial.py', 'lock = threading.Lock()\nsc.parallelize([1, 2]).map(lambda x: (x, lock)).collect()', sec('== 4)', '== 5)')),
     'Spark refuses before running anything.'),
    ('Step 5 · Broadcast instead',
     code('python', 'l34_serial.py', 'bb = sc.broadcast(big)\nh = lambda x: bb.value.get(x, 0)', sec('== 5)', '== 6)')),
     'The task closure shrinks to 635 bytes; the dict travels once per executor.'),
    ('Step 6 · Arrow for pandas',
     code('python', 'l34_serial.py', 'spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", arrow)\ndf.toPandas()   # 2,000,000 rows', sec('== 6)')),
     '14.5 s with row pickling, 2.2 s with Arrow columns.'),
]
see = [term([('pickle 3.47 MB 36/36 ms', W), ('marshal 3.40 MB 8/22 ms', W), ('marshal: custom class fails', RD)], size=6.8), term([('pickle lambda: PicklingError', RD), ('closure with dict: 2.8 MB', Y)], size=6.8),
       term([('Marshal 1.66 s', W), ('CloudPickle 1.22 s', W), ('Marshal again 1.02 s', W)], size=7.0), term([("cannot pickle '_thread.lock'", RD)], size=7.0),
       term([('broadcast closure: 635 bytes', G)], size=7.0), term([('arrow=false 14.54 s', RD), ('arrow=true 2.22 s', G)], size=7.0)]
B1 = [pipe(1), pipe(1), pipe(3), pipe(1), pipe(2), pipe(3)]
B1 = [b + cap(c, '', tn, y=118, h=30) for b, c, tn in zip(B1, ['Data to bytes', 'Code to bytes', 'No clear winner', 'Some objects cannot', 'Ship data once', 'Columns beat rows'], ['blue', 'violet', 'amber', 'red', 'green', 'green'])]
two = anim_two('Serialization', 'Measure what crosses the boundary', 'Real outputs (local[2])', 'The byte path', see, B1, ['Data.', 'Code.', 'RDD.', 'Fail.', 'Broadcast.', 'Arrow.'], ['Size.', 'Closure.', 'Fair test.', 'Lock.', '635 B.', '6.5×.'])
pe = peel('One map() task, layer by layer', 'rdd.map(lambda x: big.get(x)). (Simplified.)',
    [('Capture', ''), ('Pickle', ''), ('Ship', ''), ('Worker', ''), ('Rows', ''), ('Return', '')],
    [['Capture', 'lambda refers to big', 'cloudpickle follows refs', ''], ['Pickle', 'code + big dict', '2.8 MB', ''], ['Ship', 'inside each task', '× number of tasks', ''],
     ['Worker', 'Python worker', 'unpickles function', ''], ['Rows', 'JVM sends batches', 'pickled records', 'AutoBatched'], ['Return', 'results pickled', 'back to JVM', '']],
    ['Capture.', 'Pickle.', 'Ship.', 'Unpack.', 'Stream.', 'Return.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Slow job, tiny code', 'Task deserialization time high. (Typical.)', ('Closure size', 'Broadcast it'), [
    ('Spark UI: big task size warning', 'MB per task', 'Clue.', 'amber'), ('cloudpickle.dumps(f)', 'measure', 'Find.', 'blue'),
    ('Captured lookup dict', '50 MB', 'Cause.', 'red'), ('sc.broadcast(dict)', 'use .value', 'Fix.', 'green'),
    ('Tasks start fast', 'less network', 'Done.', 'green')], ['Warn.', 'Measure.', 'Cause.', 'Broadcast.', 'Fast.'], 'scenario-closure') + \
       five('Real-time scenario 2', 'PicklingError with a DB client', 'Writing rows to a database. (Typical.)', ('Per-partition resources', 'Create inside the task'), [
    ('client = DB() on driver', 'used in map', 'Fail.', 'red'), ('Not picklable', 'socket inside', 'Why.', 'amber'),
    ('foreachPartition', 'open client per partition', 'Fix.', 'green'), ('Batch inserts', 'close at end', 'Efficient.', 'green'),
    ('Or a Spark connector', 'JDBC sink', 'Better.', 'blue')], ['Fail.', 'Why.', 'Partition.', 'Batch.', 'Connector.'], 'scenario-db') + \
       five('Real-time scenario 3 · advanced', 'toPandas takes minutes', 'Reporting notebook. (Typical.)', ('Arrow', 'Columnar transfer'), [
    ('2M rows → pandas', '14 s', 'Slow.', 'red'), ('Enable Arrow', 'arrow.pyspark.enabled', 'Fix.', 'green'),
    ('2.2 s', '6.5× faster', 'Win.', 'green'), ('Unsupported type?', 'falls back unless fallback disabled', 'Check.', 'amber'),
    ('Better: aggregate first', 'collect less', 'Best.', 'blue')], ['Slow.', 'Arrow.', 'Fast.', 'Types.', 'Less data.'], 'scenario-arrow')
assemble(HERE, h2_story='The hidden tax of moving Python objects', hook_html=hk,
    narration='Kabir’s price lookup job is slow although the code is one line. An old tutorial suggests changing the serializer. Arjun Sir suggests measuring first.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Serialization in PySpark',
    formal='<b>Serialization</b> converts objects to bytes for transfer or storage. PySpark serializes user functions and their closures with <b>cloudpickle</b>, transfers RDD records between the JVM and Python workers using batched pickle (or marshal) serializers, and uses <b>Apache Arrow</b> columnar batches for pandas conversions and vectorized UDFs. JVM-side data uses Spark’s internal binary formats or the configured JVM serializer (Java or Kryo).',
    simple='To run your Python code on many machines, Spark turns your function and data into bytes. What your function “carries” matters most; Arrow moves whole columns at once and is much faster than row by row.',
    term_rows=[('Serialize', 'Object → bytes.'), ('cloudpickle', 'Pickles functions/closures.'), ('Closure', 'Function + captured variables.'), ('MarshalSerializer', 'Fast, simple types only.'), ('AutoBatchedSerializer', 'Batches records.'), ('Arrow', 'Columnar format.'), ('Kryo', 'JVM serializer.'), ('PicklingError', 'Cannot serialize.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('MarshalSerializer makes PySpark fast.', 'No clear gain in our fair test.', 'Step 3.'),
               ('Kryo speeds up PySpark UDFs.', 'Kryo is JVM-side only.', 'Table.'),
               ('Small code = small tasks.', 'Captured data rides along.', 'Step 2: 2.8 MB.')],
    exam='“Why are serializers needed in PySpark?” To ship functions (cloudpickle) and data between driver, JVM and Python workers; MarshalSerializer (fast, limited types) vs PickleSerializer (any object); batched; Arrow for pandas/vectorized UDFs; avoid big closures (broadcast); Kryo is for JVM objects.',
    types_h2='What uses which serializer', types_html=types_html, warn=warn,
    steps_h2='Measure every crossing', steps_intro='All outputs are real: PySpark 4.3.0, local[2], Python 3.13.',
    steps=steps, two=two, peel_intro='Now peel one map() task.', peel_html=pe,
    scen_intro='Three live scenarios: a heavy closure, a DB client, and slow toPandas.', scen=scen,
    uc_h2='Serialization at work', ucs=[uc_('udf', 'UDFs', 'blue', '1. UDFs', 'Arrow vs pickle path.', ['Rows', '*Arrow', 'Python']),
        uc_('look', 'lookups', 'green', '2. Lookups', 'Broadcast, not closures.', ['Dict', '*broadcast', 'Tasks']),
        uc_('pd', 'pandas', 'violet', '3. pandas handoff', 'toPandas with Arrow.', ['DataFrame', '*Arrow', 'pandas']),
        uc_('io', 'sinks', 'amber', '4. External sinks', 'Clients per partition.', ['Rows', '*foreachPartition', 'DB'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../02-broadcast-variables-and-accumulators/">3.2 Broadcast</a>.')
