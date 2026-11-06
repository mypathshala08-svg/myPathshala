import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='03-persistence-and-shared-variables', lesson='04-serialization-in-pyspark', n='3.4', module_label='Module 3 · Persistence and shared variables',
    title='Serialization in PySpark',
    desc='How PySpark turns code and data into bytes: cloudpickle for functions and closures, pickle and marshal serializers for RDD records, AutoBatchedSerializer, Apache Arrow for pandas conversions and vectorized UDFs, Kryo on the JVM side, closure size, broadcast and unpicklable objects. Real PySpark 4.3 measurements.',
    og_desc='A 2.8 MB lambda, a 635-byte fix, and Arrow making toPandas 6.5× faster: PySpark serialization measured.',
    minutes=20, level='Intermediate',
    lead='Why can a one-line lambda be slow? We measure <b>pickle vs marshal</b>, see what <b>cloudpickle</b> ships with each task, hit an <b>unpicklable</b> object, and compare <b>Arrow</b> with row pickling. <b>All outputs are real.</b>',
    chips=['2.8 MB closure', '635 B with broadcast', 'Arrow 14.5 s → 2.2 s', 'Runs in your browser (Python)'])
MAIN = '''# What does a function carry? (pickle sizes in plain Python)
import pickle
prices = {f"item-{i}": i for i in range(50000)}

def make_lookup(table):
    return lambda name: table.get(name, 0)      # closure captures `table`

small = make_lookup({"idli": 45})
big = make_lookup(prices)
# cloudpickle would serialize the captured table; here we measure the table itself
print("captured small table:", len(pickle.dumps({"idli": 45})), "bytes")
print("captured big table:  ", len(pickle.dumps(prices)), "bytes  <- sent with every task")
print(small("idli"), big("item-7"))
'''
RUN = dict(heading='Run the code: what a closure carries', intro='<p>Captured data travels with the function. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    return lambda name: table.get(name, 0)      # closure captures `table`', 'The lambda keeps a reference to table.'), ('print("captured big table:  ", len(pickle.dumps(prices)), "bytes  <- sent with every task")', 'Broadcast it instead.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Make prices 10× bigger.', code=None),
        dict(label='2 · Predict first: factor', hint='<b>Predict first:</b> 2,804,549 ÷ 635.', code='print(round(2804549 / 635))\n'),
        dict(label='3 · Arrow speed-up', hint='14.54 s vs 2.22 s.', code='print(round(14.54 / 2.22, 1))\n'),
        dict(label='4 · Per task cost', hint='2.8 MB × 200 tasks.', code='print(round(2.8 * 200), "MB over the network")\n'),
        dict(label='5 · Spot the error', hint='Lock in a closure.', expect='error', code='import pickle, threading\npickle.dumps(threading.Lock())\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC', intro='<p>Local PySpark. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Closure size', cmd='from pyspark.cloudpickle import dumps; len(dumps(lambda x: big.get(x, 0)))', file='python', output='2804549', note='Measure before shipping.'),
           dict(title='2 · Arrow', cmd='spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true"); df.toPandas()', file='python', output='arrow=true  toPandas  2.22 s', note='2M rows.')])
TRACE = dict(heading='Closure step by step', intro='<p>Capture, pickle, ship.</p>',
    code='import pickle\ntable = {"idli": 45}\nf_payload = pickle.dumps(table)\nprint(len(f_payload), "bytes per task")\n', notes={3: 'Captured :: Travels with f.'})
WORKED_INTRO = 'Three serialization decisions.'
EXAMPLES = [
    dict(level='b', tag='Serial · lookup', title='Lookup table in a UDF', problem='<p>50 MB dict needed by a map.</p>', inp='data',
         approach=['Do not capture it.', 'sc.broadcast(dict).', 'Use bc.value inside.'], code='print("bc = sc.broadcast(prices); rdd.map(lambda x: bc.value.get(x))")\n', notes={1: 'Once per executor.'}, tryit='Step 5.'),
    dict(level='i', tag='Serial · pandas', title='Fast toPandas', problem='<p>Notebook conversion slow.</p>', inp='config',
         approach=['Enable Arrow.', 'Collect fewer rows/columns.', 'Check fallback.'], code='print({"spark.sql.execution.arrow.pyspark.enabled": "true"})\n', notes={1: '6.5× in lab.'}, tryit='Step 6.'),
    dict(level='a', tag='Serial · resources', title='Clients in tasks', problem='<p>HTTP client per record.</p>', inp='pattern',
         approach=['mapPartitions.', 'Create client once per partition.', 'Close at end.'], code='print("def part(rows):\\n    c = Client()\\n    for r in rows: yield c.call(r)")\n', notes={1: 'No pickling needed.'}, tryit='Scenario 2.')]
QUIZ = mix([
    dict(q='Beginner: PySpark ships your lambdas with…', options=['marshal', 'cloudpickle', 'JSON', 'Kryo'], answer=1, why='Closures.'),
    dict(q='Beginner: Serialization is needed because…', options=['Python is slow', 'Objects must cross processes/machines as bytes', 'Disks need it', 'No reason'], answer=1, why='Boundaries.'),
    dict(q='Beginner: A big dict used in a lambda is…', options=['Ignored', 'Sent with every task', 'Cached on GPU', 'Compressed away'], answer=1, why='2.8 MB.'),
    dict(q='Intermediate: Marshal fails on…', options=['ints', 'custom class objects', 'tuples', 'strings'], answer=1, why='Step 1.'),
    dict(q='Intermediate: Our fair Marshal vs CloudPickle test showed…', options=['Marshal 10× faster', 'No clear winner', 'Pickle failed', 'Marshal crashed'], answer=1, why='Step 3.'),
    dict(q='Intermediate: Arrow made toPandas…', options=['Slower', 'About 6.5× faster', 'Same', 'Fail'], answer=1, why='14.5 → 2.2 s.'),
    dict(q='Advanced: Kryo affects…', options=['Python objects', 'JVM objects', 'Arrow', 'cloudpickle'], answer=1, why='JVM side.'),
    dict(q='Advanced: An unpicklable DB client should be…', options=['Captured', 'Created inside mapPartitions/foreachPartition', 'Broadcast', 'Cached'], answer=1, why='Per partition.')])
REVISION = ['Functions → cloudpickle; RDD records → batched pickle/marshal; pandas ↔ Spark → Arrow.', 'Captured variables travel with every task: 2.8 MB vs 635 B with broadcast.',
    'Marshal: simple types only; no clear win in a fair test.', 'Unpicklable objects (locks, clients) → create per partition.', 'Kryo is JVM-side; Arrow toPandas 14.5 → 2.2 s.']
FAQ = [('Can I use Kryo for PySpark?', 'It only changes how the JVM serializes JVM objects; Python objects still use pickle/cloudpickle/Arrow.'),
    ('Is pickle safe?', 'Only unpickle data you trust; Spark uses it internally between its own processes.'),
    ('Why AutoBatchedSerializer?', 'It groups records into batches sized by speed, reducing per-record overhead.'),
    ('Does Spark Connect change this?', 'UDFs are still pickled and run in Python workers on the server side.')]
PRACTICE_INTRO = 'Serialization programs.'
PROBLEMS = [
    dict(level='easy', title='Size', stmt='Pickle size of a tuple.', inp='tuple', code='import pickle\nprint(len(pickle.dumps((1, "idli", 45.0))))\n', explain='Bytes.'),
    dict(level='easy', title='Marshal', stmt='Marshal a list.', inp='list', code='import marshal\nprint(len(marshal.dumps([1, 2, 3])))\n', explain='Works.'),
    dict(level='easy', title='Speed-up', stmt='14.54 / 2.22.', inp='floats', code='print(round(14.54 / 2.22, 1))\n', explain='6.5×.'),
    dict(level='medium', title='Can marshal?', stmt='Test types.', inp='list', code='import marshal\nclass X: pass\nfor o in [1, "a", X()]:\n    try: marshal.dumps(o); print("ok")\n    except ValueError: print("no")\n', explain='Custom fails.'),
    dict(level='medium', title='Network', stmt='Closure × tasks.', inp='ints', code='print(2.8 * 500, "MB")\n', explain='1,400 MB.'),
    dict(level='medium', title='Round trip', stmt='Pickle round trip.', inp='dict', code='import pickle\nd = {"idli": 45}\nprint(pickle.loads(pickle.dumps(d)) == d)\n', explain='True.'),
    dict(level='business', title='Savings', stmt='Broadcast saves per task.', inp='ints', code='print(2804549 - 635, "bytes")\n', explain='~2.8 MB.'),
    dict(level='business', title='Report time', stmt='Daily toPandas saved.', inp='floats', code='print(round(14.54 - 2.22, 1), "s per run")\n', explain='12.3 s.')]
SCN_INTRO = 'Serialization interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“Why are serializers needed in PySpark?”', 'Explain.', 'answer?', '<p>To move code and data between the driver, the JVM executors and Python workers as bytes: cloudpickle for functions, pickle/marshal batches for RDD records, Arrow for pandas and vectorized UDFs.</p>', '“For compression.”') +
    scn('Data', 'Mid-level', 'PicklingError', 'Using a client in map.', 'fix?', '<ul><li>Create it in mapPartitions/foreachPartition.</li></ul>', 'Make it global.') +
    scn('Data', 'Mid-level', 'Tasks slow to start', 'Big task binary.', 'fix?', '<ul><li>Find captured data; broadcast it.</li></ul>', 'More executors.') +
    scn('Platform', 'Senior', 'Kryo for PySpark?', 'Team asks.', 'answer?', '<ul><li>JVM-only; focus on Arrow, closures, DataFrames.</li></ul>', '“Yes, 10× faster.”'))
