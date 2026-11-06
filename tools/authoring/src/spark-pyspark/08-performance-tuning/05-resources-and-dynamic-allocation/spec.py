import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='08-performance-tuning', lesson='05-resources-and-dynamic-allocation', n='8.5',
    module_label='Module 8 · Performance tuning',
    title='Resources and dynamic allocation',
    desc='Executor resources measured on a real Spark 4.3.0 standalone cluster: static allocation holding 4 executors, a spark.cores.max cap, dynamic allocation with shuffle tracking scaling 0 → 4 → 0 → 4 executors (with the ramp-up cost: 45.0 s vs 30.9 s), an executor larger than any worker waiting forever, and how to size executor cores, memory and counts.',
    og_desc='Watch Spark dynamic allocation add and release executors on a real cluster, 0 → 4 → 0 → 4, and what it costs in start-up time.',
    minutes=28, level='Intermediate → Advanced',
    lead='How many executors an application holds, and how big they are, decides both speed and cost. This lesson runs the same application on a real standalone cluster with static allocation, a <code>cores.max</code> cap, <b>dynamic allocation</b>, and an executor too big to fit. <b>All outputs are real</b> (Spark 4.3.0).',
    chips=['Spark 4.3.0 cluster', 'Executor timeline', 'Dynamic allocation', 'Runs in your browser (Python)'],
)

MAIN = '''# Sizing executors for a node (a common rule of thumb)
node_cores, node_mem_gb = 16, 64
reserve_cores, reserve_mem_gb = 1, 4          # OS and daemons
cores_per_exec = 5

execs = (node_cores - reserve_cores) // cores_per_exec
mem_per_exec = (node_mem_gb - reserve_mem_gb) / execs
overhead = max(0.384, mem_per_exec * 0.10 / 1.10)
heap = mem_per_exec - overhead
print("executors per node :", execs)
print("executor.memory    :", round(heap, 1), "GB")
print("memoryOverhead     :", round(overhead, 1), "GB")
'''
RUN = dict(
    heading='Run the code: sizing executors',
    intro='<p>A common starting point for executor shapes. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('cores_per_exec = 5', 'About 4–5 cores per executor is a widely used balance between parallelism and per-JVM overhead.'),
        ('overhead = max(0.384, mem_per_exec * 0.10 / 1.10)', 'Container size = heap + overhead; overhead defaults to 10% of the heap, at least 384 MB.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then try a 32-core, 256 GB node.', code=None),
        dict(label='2 · Predict first: does it fit?', hint='<b>Predict first:</b> 3 GB executor on 2 GB workers?',
             code='''worker_gb, ask_gb = 2, 3
print("placed" if ask_gb <= worker_gb else "WAITING: Initial job has not accepted any resources")
'''),
        dict(label='3 · Cluster capacity', hint='Task slots in a 10-node cluster.',
             code='''nodes, execs_per_node, cores = 10, 3, 5
print(nodes * execs_per_node * cores, "tasks at once")
'''),
        dict(label='4 · Dynamic ramp-up', hint='Executors requested per round (doubling) until max.',
             code='''n, mx, rounds = 1, 20, []
while sum(rounds) < mx:
    rounds.append(min(n, mx - sum(rounds))); n *= 2
print(rounds)
'''),
        dict(label='5 · Spot the error', hint='Dynamic allocation without a shuffle service or tracking.', expect='error',
             code='''conf = {"spark.dynamicAllocation.enabled": "true"}
assert conf.get("spark.dynamicAllocation.shuffleTracking.enabled") == "true" or conf.get("spark.shuffle.service.enabled") == "true", \\
    "removing executors would lose shuffle files: enable shuffleTracking or the external shuffle service"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your cluster: executors',
    intro='<p>On the lab cluster from Lesson 1.5. <b>Outputs are real</b> (Spark 4.3.0).</p>',
    items=[
        dict(title='1 · Workers', cmd='curl -s localhost:8090/json/ | python3 -c "import json,sys;d=json.load(sys.stdin);print(d[\'status\'],len(d[\'workers\']),d[\'cores\'])"', file='bash',
             output='ALIVE 2 4', note='2 workers, 4 cores.'),
        dict(title='2 · Executors of an app', cmd='spark.sparkContext.getConf().get("spark.dynamicAllocation.enabled", "false")', file='pyspark',
             output="'true'", note='Then watch the Executors tab.'),
        dict(title='3 · Too big', cmd='spark-submit … --conf spark.executor.memory=3g job.py', file='bash',
             output='WARN TaskSchedulerImpl: Initial job has not accepted any resources; check your cluster UI to ensure that workers are registered and have sufficient resources', note='Waits forever.'),
    ],
)

TRACE = dict(
    heading='Dynamic allocation decisions',
    intro='<p>Follow Spark adding and removing executors.</p>',
    code='''pending, execs, idle_s = 40, 0, 0
want = min(4, pending)
execs = want
pending = 0
idle_s = 15
if idle_s > 10:
    execs = 0
print(execs)
''',
    notes={2: 'Backlog :: Tasks pending → request up to max.', 6: 'Idle :: After the idle timeout, release.'},
)

WORKED_INTRO = 'Three resource decisions at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='Resources · capacity', title='How many tasks run at once?',
         problem='<p>20 executors with 4 cores each.</p>',
         inp='20 × 4',
         approach=['Task slots = executors × cores.', 'A stage of 400 tasks runs in waves.', 'Divide.'],
         code='''slots = 20 * 4
print(slots, "slots,", 400 / slots, "waves")
''', notes={1: 'Slots :: spark.task.cpus = 1 by default.'},
         tryit='Step 1.'),
    dict(level='i', tag='Resources · dynamic', title='Configure a notebook cluster',
         problem='<p>Notebooks should release resources after 10 minutes.</p>',
         inp='shared cluster',
         approach=['Enable dynamic allocation.', 'Shuffle tracking.', 'Idle timeout 600 s, min 0.'],
         code='''conf = {
  "spark.dynamicAllocation.enabled": "true",
  "spark.dynamicAllocation.shuffleTracking.enabled": "true",
  "spark.dynamicAllocation.executorIdleTimeout": "600s",
  "spark.dynamicAllocation.minExecutors": "0",
}
print(len(conf), "settings")
''', notes={3: 'Idle :: Default is 60 s.'},
         tryit='Step 3.'),
    dict(level='a', tag='Resources · sizing', title='Why is my app waiting?',
         problem='<p>An app shows 0 executors; nodes have 32 GB.</p>',
         inp='executor.memory 30g',
         approach=['Container = heap + overhead.', '30 + 3 > 32.', 'Shrink the executor.'],
         code='''heap, node = 30, 32
print("fits" if heap + max(0.384, heap * 0.1) <= node else "never placed")
''', notes={1: 'Overhead :: Counts on YARN/Kubernetes.'},
         tryit='Step 4.'),
]

QUIZ = mix([
    dict(q='Beginner: Task slots of an app =', options=['executors', 'executors × cores', 'cores ÷ executors', 'partitions'], answer=1,
         why='One task per core.'),
    dict(q='Beginner: Dynamic allocation does what?', options=['Caches data', 'Adds/removes executors by workload', 'Changes partitions', 'Picks joins'], answer=1,
         why='Backlog and idle timeouts.'),
    dict(q='Beginner: Default executorIdleTimeout?', options=['1 s', '60 s', '10 min', 'Never'], answer=1,
         why='We used 10 s in the lab.'),
    dict(q='Intermediate: Dynamic allocation needs…', options=['Nothing', 'Shuffle tracking or an external shuffle service', 'Kubernetes only', 'AQE off'], answer=1,
         why='Shuffle files must survive.'),
    dict(q='Intermediate: Lab cost of dynamic allocation?', options=['None', 'Ramp-up: 45.0 s vs 30.9 s', 'Wrong results', 'More spill'], answer=1,
         why='Cold executors.'),
    dict(q='Intermediate: On standalone, cap an app’s cores with…', options=['spark.cores.max', 'spark.task.cpus', 'shuffle.partitions', 'maxResultSize'], answer=0,
         why='Otherwise it takes all free cores.'),
    dict(q='Advanced: 3 GB executor on 2 GB workers?', options=['OOM', 'Waits: has not accepted any resources', 'Runs with 2 GB', 'Uses disk'], answer=1,
         why='Never placed.'),
    dict(q='Advanced: Why not one 64-core executor per node?', options=['Not allowed', 'Long GC pauses and contention', 'Faster', 'Less memory'], answer=1,
         why='4–5 cores per executor is common.'),
])

REVISION = [
    'Capacity = executors × cores; each executor = heap + overhead on one node.',
    'Static: executors held for the app’s life (4 held through idle time).',
    '<code>spark.cores.max</code> caps an app on standalone.',
    'Dynamic: add on backlog, remove after idle timeout; lab 0→4→0→4.',
    'Needs shuffle tracking or external shuffle service.',
    'Ramp-up cost: 45.0 s vs 30.9 s; use minExecutors/static for SLAs.',
    'Too-big executors never start: “has not accepted any resources”.',
]
FAQ = [
    ('Is dynamic allocation on by default?', 'No in open-source Spark; many platforms (Databricks autoscaling, EMR, Dataproc) enable it or an equivalent by default.'),
    ('What is the external shuffle service?', 'A long-running process on each node that serves shuffle files, so executors can be removed without losing them.'),
    ('Does dynamic allocation work with Structured Streaming?', 'Classic dynamic allocation is not designed for streaming; streaming has its own considerations.'),
    ('How many cores per executor?', 'Commonly 4–5; more can hurt I/O throughput and GC, fewer wastes memory on per-JVM overhead.'),
    ('Why were 4 executors not faster than 2 in the lab?', 'The host had only 2 physical CPUs; extra advertised cores just shared them.'),
]

PRACTICE_INTRO = 'Programs about executor resources.'
PROBLEMS = [
    dict(level='easy', title='Slots', stmt='Task slots for 12 executors of 5 cores.', inp='12, 5',
         code='''print(12 * 5)
''', explain='60 tasks at once.'),
    dict(level='easy', title='Waves', stmt='Waves for 1,000 tasks on 60 slots.', inp='1000, 60',
         code='''import math
print(math.ceil(1000 / 60))
''', explain='17 waves.'),
    dict(level='easy', title='Overhead', stmt='Overhead for a 20 GB heap.', inp='20 GB',
         code='''print(max(0.384, 20 * 0.1), "GB")
''', explain='2 GB.'),
    dict(level='medium', title='Executors per node', stmt='5-core executors on a 32-core node with 1 reserved.', inp='32 cores',
         code='''print((32 - 1) // 5)
''', explain='6 executors.'),
    dict(level='medium', title='Fits?', stmt='Does 24g heap fit a 28 GB node budget?', inp='24 + overhead',
         code='''print(24 + max(0.384, 2.4) <= 28)
''', explain='26.4 GB.'),
    dict(level='medium', title='Ramp-up overhead', stmt='Extra seconds from dynamic allocation in the lab.', inp='45.0 vs 30.9',
         code='''print(round(45.0 - 30.9, 1))
''', explain='Executors started cold.'),
    dict(level='business', title='Idle executor-hours', stmt='Executor-hours wasted by 30 idle notebooks with 10 executors for 6 h.', inp='30 × 10 × 6',
         code='''print(30 * 10 * 6)
''', explain='Dynamic allocation frees them.'),
    dict(level='business', title='Cost', stmt='Daily cost at ₹8 per executor-hour.', inp='1,800 executor-hours',
         code='''print("₹", 1800 * 8)
''', explain='₹14,400 per day.'),
]

SCN_INTRO = 'Resource sizing questions check you understand clusters, not just code.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“What is an executor?”',
        'Explain executors and cores.',
        'parallelism?',
        '<p>An executor is a JVM process on a worker that runs tasks and stores cached data. Each executor has a number of cores; executors × cores is how many tasks the application can run at the same time.</p>', 'Saying an executor is a machine.') +
    scn('Platform', 'Mid-level', 'Idle notebooks',
        'Users complain the shared cluster is always full.',
        'fix?',
        '''<ul>
          <li>Enable dynamic allocation with shuffle tracking, min 0.</li>
          <li>Reasonable idle timeout (5–10 min for notebooks).</li>
          <li>Cap maxExecutors per user/app.</li>
        </ul>''', 'Buying more nodes first.') +
    scn('Data engineering', 'Mid-level', 'App never starts',
        'spark-submit runs but no tasks start for 20 minutes.',
        'diagnose?',
        '''<ol>
          <li>Look for “Initial job has not accepted any resources”.</li>
          <li>Compare executor cores/memory + overhead with node capacity.</li>
          <li>Check queue/quota limits.</li>
        </ol>''', 'Restarting the job repeatedly.') +
    scn('Platform', 'Senior', 'Executor strategy',
        'Define executor settings for batch and interactive workloads.',
        'design?',
        '''<ul>
          <li>Standard shapes (e.g. 5 cores, 18–20 GB + overhead) that pack nodes.</li>
          <li>Interactive: dynamic allocation; SLA batch: static or high minExecutors.</li>
          <li>Track executor-hours and idle time per app.</li>
        </ul>''', 'One size for every workload.')
)
