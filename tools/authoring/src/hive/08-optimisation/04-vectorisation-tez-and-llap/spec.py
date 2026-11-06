import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from hivekit import tables
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
def plain(n):
    lines = [l for l in capf(n).split('\n') if l.startswith('| ')]
    return '\n'.join(re.sub(r'\s*\|$', '', l[2:]).rstrip() for l in lines)
BODY = body(HERE)

META = dict(
    module='08-optimisation', lesson='04-vectorisation-tez-and-llap', n='8.4',
    module_label='Module 8 · Query optimisation',
    title='Vectorisation, Tez tuning and LLAP',
    desc='How Hive executes plans, measured on a 5-million-row table in Hive 4.2.1: vectorised vs row-mode execution (about 1.0 s vs 3.0 s), EXPLAIN VECTORIZATION and notVectorizedReason, the VectorUDFAdaptor for UDFs, ORC vs text with vectorisation, Tez split grouping and reducer parallelism (task counts changed by each setting), fetch-task conversion, container settings, and what LLAP needs (our attempt failed at the ZooKeeper registry).',
    og_desc='Vectorised: 1.0 s. Row mode: 3.0 s. Same query, 5 million rows. Vectorisation, Tez tuning and LLAP in Hive 4.2.1, measured.',
    minutes=40, level='Intermediate → Advanced',
    lead='Lessons 8.1–8.3 made the plan right. This lesson makes the <b>execution</b> fast: vectorisation, the Tez settings that decide how many tasks run, fetch tasks that skip the cluster, and LLAP. Every number is measured on a 5,000,000-row table, <b>all outputs real</b>, from Hive 4.2.1, including the LLAP attempt that failed and why.',
    chips=['Measured: 3× from vectorisation', 'Task counts per setting', 'LLAP requirements, honestly', 'Runs in your browser (Python)'],
)

MAIN = '''# Row-at-a-time vs batch-at-a-time, the idea behind vectorisation
import time
N = 1_000_000
amount = [i % 840 + 40 for i in range(N)]

t0 = time.perf_counter()
total = 0
for a in amount:                     # row mode: one step per row
    if a > 100:
        total += a
row_ms = (time.perf_counter() - t0) * 1000

t0 = time.perf_counter()
total2 = 0
for s in range(0, N, 1024):          # vectorised: one step per batch of 1,024
    batch = amount[s:s + 1024]
    total2 += sum(a for a in batch if a > 100)
vec_ms = (time.perf_counter() - t0) * 1000
print("same result:", total == total2)
print(f"row loop {row_ms:.0f} ms, batch loop {vec_ms:.0f} ms (Python, illustrative)")
'''
RUN = dict(
    heading='Run the code: batches, tasks and reducers',
    intro='<p>These programs model what Hive’s execution settings compute, using the lab numbers. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('for s in range(0, N, 1024):          # vectorised: one step per batch of 1,024', 'Hive’s VectorizedRowBatch holds 1,024 rows as column arrays. In Java the gain comes from tight loops over primitive arrays; Python only shows the structure.'),
        ('print(f"row loop {row_ms:.0f} ms, batch loop {vec_ms:.0f} ms (Python, illustrative)")', 'Python timings say little about Java. The real measurement is in Step 3: 300–400 ms vs about 2,300 ms.'),
    ],
    tasks=[
        dict(label='1 · Batches', hint='Press <b>Run</b>. Both loops compute the same total; Hive’s gain comes from doing the per-batch work in compiled, CPU-friendly loops.', code=None),
        dict(label='2 · Predict first: how many reducers?', hint='<b>Predict first:</b> estimated shuffle 6,171 rows × 124 bytes. How many reducers for each bytes-per-reducer value?',
             code='''import math
shuffle = 6171 * 124
for per_reducer in [256_000_000, 1_000_000, 100_000]:
    print(per_reducer, "->", min(1009, max(1, math.ceil(shuffle / per_reducer))), "reducers")
'''),
        dict(label='3 · How many map tasks?', hint='Tez grouping only <b>merges</b> input splits, it never cuts them. Our 246 MB text file had 8 splits of up to 32 MB (the local file system block size): by default Tez merged them into 1 task; with max 16 MB nothing could be merged, so 8 tasks ran.',
             code='''import math
file_mb, split_mb = 245.7, 32
splits = math.ceil(file_mb / split_mb)
for max_mb in [1024, 64, 32, 16]:
    per_group = max(1, max_mb // split_mb)
    print(f"max {max_mb:>4} MB -> splits {splits}, at most {per_group} per task -> at least {math.ceil(splits / per_group)} task(s)")
'''),
        dict(label='4 · Speed-ups from the lab', hint='Compute the speed-ups from the real runs.',
             code='''runs = {"vectorised vs row (query)": (3.035, 0.973), "vectorised vs row (Map 1)": (2360, 302),
        "adaptor all vs none": (3.47, 2.081), "ORC vs text (query)": (3.851, 1.003)}
for k, (slow, fast) in runs.items():
    print(f"{k:26} {slow / fast:.1f}x")
'''),
        dict(label='5 · Spot the error', hint='This check sets the Tez heap. Real guidance: heap about 80% of the container. Fix it.', expect='error',
             code='''container_mb = 4096
heap_mb = container_mb                  # bug: no room for off-heap memory
assert heap_mb <= 0.8 * container_mb, "leave ~20% of the container for non-heap memory"
print(f"SET hive.tez.java.opts=-Xmx{heap_mb}m;")
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: text vs ORC, and the vertex summary',
    intro='<p>Two more measurements on the lab. <b>Outputs are real</b>, from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · Text files can be vectorised too', cmd='EXPLAIN VECTORIZATION ONLY SUMMARY\nSELECT city, COUNT(*) FROM orders_big_txt GROUP BY city;', file='Beeline',
             output='\n'.join(l for l in plain('l84_txtvec.txt').split('\n') if any(k in l for k in ('Map 1', 'Execution mode', 'inputFileFormats', 'vectorized:', 'featureSupportInUse'))),
             note='The text table is vectorised as well: Hive deserialises the lines straight into column vectors. But reading and parsing text is still the expensive part, as the next item shows.'),
        dict(title='2 · Same query on ORC and on text, both vectorised', cmd='SET hive.tez.exec.print.summary=true;\nSELECT city, status, COUNT(*) AS n, SUM(amount) AS rev, AVG(amount) AS avg_amt\nFROM orders_big       -- then orders_big_txt\nWHERE amount > 100 GROUP BY city, status;', file='Beeline',
             output=capf('l84_fmt_runs.txt'),
             note='ORC: about 1.0 s (Map 1 about 340 ms). Text: about 3.9 s (Map 1 about 3,000–3,300 ms). Vectorisation does not remove the cost of parsing 246 MB of text; the format (Module 6) and the execution mode work together.'),
        dict(title='3 · The Tez vertex summary', cmd='SET hive.tez.exec.print.summary=true;\n-- printed after the query, in the INFO lines', file='Beeline',
             output=capf('l84_vec_summary.txt'),
             note='Per vertex: duration, CPU and GC time, input and output records. CPU and GC show 0 in our local-mode lab; on a cluster they are filled in and are the first numbers to look at for CPU-bound queries (Lesson 8.5).'),
    ],
)

TRACE = dict(
    heading='How Hive picks the reducer count',
    intro='<p>Follow the arithmetic for Reducer 2 with <code>hive.exec.reducers.bytes.per.reducer=100000</code>.</p>',
    code='''est_rows = 6171                 # rows into the shuffle (from EXPLAIN)
width = 124                     # bytes per row
shuffle = est_rows * width
per_reducer = 100000
reducers = -(-shuffle // per_reducer)
reducers = min(reducers, 1009)
print("reducers:", reducers)
''',
    notes={3: 'Estimate :: 765,204 bytes, from statistics, before the query runs.', 5: 'Ceiling :: 7.65 rounds up to 8: the real Reducer 2 ran 8 tasks.', 6: 'Cap :: hive.exec.reducers.max.'},
)

WORKED_INTRO = 'Three execution-tuning tasks you will meet on a platform team.'
EXAMPLES = [
    dict(level='b', tag='Analytics · checking', title='Is my query vectorised?',
         problem='<p>From EXPLAIN VECTORIZATION lines, report each vertex as vectorised or not, with the reason.</p>',
         inp='lines from the md5 test with adaptor mode none',
         approach=['Track the current vertex.', 'Read “vectorized: true/false”.', 'Keep notVectorizedReason.'],
         code='''lines = ["Map 1", "notVectorizedReason: UDF GenericUDFBridge ==> md5 not supported", "vectorized: false",
         "Reducer 2", "vectorized: true"]
vertex, reason = None, ""
for l in lines:
    if l.startswith(("Map", "Reducer")): vertex, reason = l, ""
    elif l.startswith("notVectorizedReason"): reason = l.split(": ", 1)[1]
    elif l.startswith("vectorized:"): print(vertex, "->", l.split(": ")[1], reason)
''', notes={4: 'Vertex :: Reasons belong to the vertex printed above them.'},
         tryit='Real output had exactly this shape: Map 1 false (md5), Reducer 2 true.'),
    dict(level='i', tag='Data engineering · tuning', title='Choose reducers for a daily job',
         problem='<p>A job shuffles about 120 GB. Pick bytes-per-reducer for about 1 GB per reducer and check it stays under the cap.</p>',
         inp='120 GB estimated shuffle (illustrative)',
         approach=['Divide shuffle by target size.', 'Check against hive.exec.reducers.max.', 'Prefer auto parallelism for variable data.'],
         code='''import math
shuffle_gb, target_gb, cap = 120, 1, 1009
n = math.ceil(shuffle_gb / target_gb)
print("reducers:", min(n, cap))
print("SET hive.exec.reducers.bytes.per.reducer=", target_gb * 1024 ** 3, ";", sep="")
''', notes={3: 'Target :: 0.25–1 GB per reducer is a common starting range; measure and adjust.'},
         tryit='With auto parallelism on, Tez can still lower the count at run time, as it did in our lab (8 → 2).'),
    dict(level='a', tag='Platform · memory', title='Size Tez containers',
         problem='<p>Nodes have 96 GB for YARN. Choose container size and heap so 20 tasks fit per node.</p>',
         inp='96 GB per node, 20 concurrent tasks (illustrative)',
         approach=['Container = node memory / tasks, rounded to the YARN minimum.', 'Heap ≈ 80% of the container.', 'Map-join hash tables live in that heap.'],
         code='''node_mb, tasks, yarn_min = 96 * 1024, 20, 1024
container = (node_mb // tasks) // yarn_min * yarn_min
heap = int(container * 0.8)
print(f"SET hive.tez.container.size={container};")
print(f"SET hive.tez.java.opts=-Xmx{heap}m;")
''', notes={3: 'Rounding :: YARN allocates in multiples of its minimum allocation.'},
         tryit='4,096 MB containers with a 3,276 MB heap. Bigger map joins need bigger containers, which means fewer tasks per node.'),
]

QUIZ = mix([
    dict(q='Beginner: How many rows does a VectorizedRowBatch hold by default?', options=['1', '128', '1,024', '1,000,000'], answer=2,
         why='Operators process 1,024 rows per call.'),
    dict(q='Beginner: Which setting enables vectorised execution on the map side?', options=['hive.vector.enable', 'hive.vectorized.execution.enabled', 'hive.tez.vector', 'hive.exec.parallel'], answer=1,
         why='Plus hive.vectorized.execution.reduce.enabled for reducers.'),
    dict(q='Beginner: Why does SELECT … LIMIT 5 often run without a Tez job?', options=['It is cached', 'Fetch-task conversion: HiveServer2 reads the files directly', 'LLAP', 'Statistics'], answer=1,
         why='hive.fetch.task.conversion=more; the plan is only a Fetch Operator.'),
    dict(q='Intermediate: What did vectorisation do to Map 1 on 5 million rows?', options=['Nothing', 'About 2,300 ms → 300–400 ms', 'Made it slower', 'Removed the reducer'], answer=1,
         why='Three runs each; whole query about 3.0 s → 1.0 s.'),
    dict(q='Intermediate: What does VectorUDFAdaptor do?', options=['Speeds up the UDF itself', 'Wraps a row-mode UDF so the rest of the plan stays vectorised', 'Disables vectorisation', 'Converts UDFs to SQL'], answer=1,
         why='Lab: 2.1 s with adaptor vs 3.4 s without.'),
    dict(q='Intermediate: Which setting changed Map 1 from 1 to 8 tasks on the 246 MB text file?', options=['hive.exec.reducers.max', 'tez.grouping.max-size / min-size', 'hive.tez.container.size', 'mapreduce.job.reduces'], answer=1,
         why='Split grouping decides map tasks.'),
    dict(q='Advanced: With bytes-per-reducer 100,000 and auto reducer parallelism on, what happened?', options=['8 reducers ran', 'Tez lowered the count at run time and 2 ran', '1,009 ran', 'Error'], answer=1,
         why='Auto parallelism adjusts using real shuffle sizes.'),
    dict(q='Advanced: Why did SET hive.execution.mode=llap fail in the lab?', options=['LLAP is removed in Hive 4', 'No LLAP daemons and no ZooKeeper registry to find them', 'Wrong file format', 'Vectorisation was off'], answer=1,
         why='NullPointerException in ZooKeeperHiveHelper: quorum is null.'),
])

REVISION = [
    '<b>Vectorisation:</b> 1,024-row column batches. <code>hive.vectorized.execution.enabled</code> / <code>.reduce.enabled</code>. Lab: Map 1 ≈ 2,300 → 300–400 ms; query ≈ 3.0 → 1.0 s.',
    'Check with <code>EXPLAIN VECTORIZATION [ONLY] SUMMARY | OPERATOR | EXPRESSION | DETAIL</code>: <code>Execution mode: vectorized</code>, <code>notVectorizedReason</code>.',
    'Row-only UDFs: <code>VectorUDFAdaptor</code> (<code>hive.vectorized.adaptor.usage.mode=all</code>) keeps the rest vectorised; prefer built-ins.',
    'Format still matters: vectorised text 3.9 s vs ORC 1.0 s on the same query.',
    '<b>Map tasks:</b> <code>tez.grouping.min-size / max-size</code> (lab: 1 → 8 tasks).',
    '<b>Reducers:</b> estimated shuffle / <code>hive.exec.reducers.bytes.per.reducer</code> (256 MB), cap <code>hive.exec.reducers.max</code> (1009); <code>hive.tez.auto.reducer.parallelism</code> trims (8 → 2); <code>mapreduce.job.reduces</code> forces.',
    '<b>Memory:</b> <code>hive.tez.container.size</code>, heap ≈ 80% via <code>hive.tez.java.opts</code>. <b>Fetch tasks:</b> <code>hive.fetch.task.conversion=more</code>.',
    '<b>LLAP:</b> persistent daemons + cache, found via ZooKeeper; <code>hive.execution.mode=llap</code> failed without them.',
]
FAQ = [
    ('What exactly does LLAP add over Tez containers?', 'Daemons that are already running (no JVM start-up), a shared in-memory columnar cache of ORC/Parquet data across queries, an I/O elevator that reads and decodes data asynchronously, and fine-grained fragment scheduling. Tez still plans and coordinates the DAG. It shines for many short interactive queries; for large batch ETL plain Tez containers are often enough.'),
    ('Is vectorisation always on?', 'In Hive 4 it is enabled by default for map and reduce sides. It can still fall back per vertex: unsupported UDFs (with the adaptor forbidden), some complex types or expressions, or input formats without vector support. Check EXPLAIN VECTORIZATION for key jobs.'),
    ('Should I set mapreduce.job.reduces for every query?', 'No. A fixed number is right for one data size only. Prefer correct statistics, a sensible bytes-per-reducer value and auto reducer parallelism; force a count only for a specific query with a known reason.'),
    ('What are Tez sessions and container reuse?', 'HiveServer2 can keep Tez application masters (sessions) open and reuse containers between tasks and queries, avoiding start-up cost. Settings such as <code>hive.server2.tez.initialize.default.sessions</code> (false in our lab), <code>hive.server2.tez.sessions.per.default.queue</code> and Tez’s container reuse control this. It is a cheaper step towards interactive latency than LLAP.'),
    ('What is hive.exec.parallel?', 'It let independent stages of a MapReduce plan run at the same time. On Tez the whole query is one DAG and independent vertices already run concurrently, so it matters little in Hive 4.'),
]

PRACTICE_INTRO = 'Programs that compute execution settings from real lab numbers, with the HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Vectorisation speed-up', stmt='Compute the Map 1 speed-up from run 1.', inp='2,360 ms row mode, 302 ms vectorised',
         code='''print(round(2360 / 302, 1))
''', explain='About 7.8× for this run; 6–7× across the three runs.'),
    dict(level='easy', title='Batches per task', stmt='How many 1,024-row batches does Map 1 process for 5,000,000 rows?', inp='5,000,000 rows',
         code='''import math
print(math.ceil(5_000_000 / 1024))
''', explain='4,883 batches instead of 5,000,000 per-row operator calls.'),
    dict(level='easy', title='Reducer count', stmt='Reducers for 765,204 estimated shuffle bytes at the default 256 MB per reducer.', inp='765,204 bytes',
         code='''import math
print(max(1, math.ceil(765204 / 256_000_000)))
''', explain='1: exactly what the default run used.'),
    dict(level='medium', title='Heap for a container', stmt='Compute -Xmx for container sizes.', inp='2048, 4096, 8192 MB',
         code='''for c in [2048, 4096, 8192]:
    print(f"container {c} -> -Xmx{int(c * 0.8)}m")
''', explain='SET hive.tez.container.size=4096; SET hive.tez.java.opts=-Xmx3276m;'),
    dict(level='medium', title='Map tasks from grouping', stmt='Estimate map tasks for files of different sizes with max grouping 256 MB.', inp='file sizes in MB',
         code='''import math
for mb in [10, 246, 5000]:
    print(mb, "MB ->", max(1, math.ceil(mb / 256)), "task(s)")
''', explain='A rough guide only: Tez merges whole splits, so the real count also depends on split sizes and cluster capacity. A 10 MB ORC file with one stripe is one task whatever you set.'),
    dict(level='medium', title='Find non-vectorised vertices', stmt='Report vertices with vectorized: false.', inp='EXPLAIN VECTORIZATION summary',
         code='''summary = {"Map 1": False, "Reducer 2": True, "Reducer 3": True}
print([v for v, ok in summary.items() if not ok])
''', explain='Look at the notVectorizedReason printed for Map 1.'),
    dict(level='business', title='CPU hours saved', stmt='A job spends 2 CPU-hours per run in row mode. Vectorised map work is about 6× faster. Saving per month (30 runs)?', inp='illustrative',
         code='''row_hours, speedup, runs = 2, 6, 30
print(round((row_hours - row_hours / speedup) * runs, 1), "CPU-hours per month")
''', explain='About 50 CPU-hours a month for one job, if all of it vectorises like our test.'),
    dict(level='business', title='Interactive or batch?', stmt='Classify workloads for Tez containers or LLAP.', inp='three workloads',
         code='''w = {"nightly 2 TB ETL": "Tez containers", "BI dashboards, 3 s target": "LLAP / pre-warmed sessions", "ad-hoc data preview": "fetch task"}
for k, v in w.items():
    print(f"{k:28} -> {v}")
''', explain='Match execution mode to workload: start-up cost matters for short queries, throughput for long ones.'),
]

SCN_INTRO = 'Execution tuning questions test whether you measure before you tune.'
SCENARIOS = (
    scn('Any company · Hive', 'Fresher', '“What is vectorised execution?”',
        'Explain vectorisation and how to check it.',
        'do you know batches and EXPLAIN VECTORIZATION?',
        '<p>Instead of one row at a time, operators process batches of 1,024 rows stored as column vectors, which reduces per-row overhead and uses the CPU better. It is on by default in Hive 4 and works best with ORC or Parquet. I check it with EXPLAIN VECTORIZATION: “Execution mode: vectorized” per vertex, or a notVectorizedReason.</p>', 'Confusing it with parallelism across tasks.') +
    scn('Data engineering', 'Mid-level', 'Job slowed after adding a UDF',
        'A job became about 3× slower after a custom UDF was added.',
        'can you find a vectorisation fallback?',
        '''<ol>
          <li>EXPLAIN VECTORIZATION on old and new SQL: look for vectorized: false and notVectorizedReason naming the UDF.</li>
          <li>Check hive.vectorized.adaptor.usage.mode; the adaptor keeps the rest vectorised.</li>
          <li>Replace the UDF with built-in functions or write a vectorised UDF.</li>
        </ol>''', 'Adding more containers.') +
    scn('Platform', 'Mid-level', 'Thousands of tiny reducers',
        'A job runs 1,009 reducers that each process a few MB and writes thousands of small files.',
        'do you know how reducer counts are chosen?',
        '''<ul>
          <li>Reducers = estimated shuffle / bytes-per-reducer, capped at hive.exec.reducers.max: the estimate is too high (statistics).</li>
          <li>Enable hive.tez.auto.reducer.parallelism so Tez trims at run time.</li>
          <li>Fix statistics; raise bytes-per-reducer if the target is too small.</li>
        </ul>''', 'Hard-coding mapreduce.job.reduces for every job.') +
    scn('Architecture', 'Senior', 'Interactive SQL for 200 analysts',
        'Design Hive for BI dashboards with a 3-second target alongside nightly ETL.',
        'do you know LLAP and its costs?',
        '''<ul>
          <li>LLAP daemons with cache for BI (needs ZooKeeper, dedicated memory), or pre-warmed Tez sessions as a lighter option.</li>
          <li>Workload management resource plans to separate BI and ETL.</li>
          <li>ORC with good layout and statistics, vectorisation verified; consider an MPP engine if latency targets are strict.</li>
        </ul>''', '“Just add nodes.”')
)
