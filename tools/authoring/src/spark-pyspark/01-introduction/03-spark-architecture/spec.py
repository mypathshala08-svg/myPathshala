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
    module='01-introduction', lesson='03-spark-architecture', n='1.3',
    module_label='Module 1 · Start here: why Spark?',
    title='Spark architecture: driver, executors and cluster managers',
    desc='How a Spark application is organised, shown on a real Spark 4.3.0 standalone cluster: local mode as one JVM, a master granting executors with 2 cores and 1 GiB, the driver scheduling every task while running none itself, client versus cluster deploy mode (refused for Python on standalone), and a worker stopped in the middle of a job: lost executor, FetchFailed after 77 seconds, resubmitted tasks and a correct result. Plus standalone, YARN and Kubernetes compared.',
    og_desc='We stopped a Spark worker in the middle of a job. Lost executor, FetchFailed, resubmitted tasks, and still the right answer: Spark’s architecture, live.',
    minutes=34, level='Beginner → Intermediate',
    lead='Every Spark program, from a laptop test to a 1,000-node job, has the same parts: a <b>driver</b>, a <b>cluster manager</b> and <b>executors</b>. This lesson shows each one at work on our Docker cluster, including what happens when a machine disappears. <b>All outputs and screenshots are real.</b>',
    chips=['Spark 4.3.0 standalone cluster', 'Worker killed mid-job', 'Real screenshots', 'Runs in your browser (Python)'],
)

MAIN = '''# Simulate a driver scheduling tasks onto executor slots (round robin on free slots)
executors = {"exec-0": 2, "exec-1": 2}     # cores = task slots
tasks = [f"task-{i}" for i in range(8)]

slots = [e for e, cores in executors.items() for _ in range(cores)]
waves = [tasks[i:i + len(slots)] for i in range(0, len(tasks), len(slots))]
for w, wave in enumerate(waves):
    print(f"wave {w}:", ", ".join(f"{t}->{s}" for t, s in zip(wave, slots)))
print("waves needed:", len(waves))
'''
RUN = dict(
    heading='Run the code: a tiny task scheduler',
    intro='<p>These programs model what the driver does with executors and slots. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('slots = [e for e, cores in executors.items() for _ in range(cores)]', 'Each core is one slot: one task at a time. Our lab had 2 executors × 2 cores = 4 slots.'),
        ('waves = [tasks[i:i + len(slots)] for i in range(0, len(tasks), len(slots))]', 'With 8 tasks and 4 slots, tasks run in 2 waves, like the 8 Parquet write tasks in Lesson 1.5.'),
    ],
    tasks=[
        dict(label='1 · Run the scheduler', hint='Press <b>Run</b>. Then give each executor 4 cores and count the waves.', code=None),
        dict(label='2 · Predict first: lose an executor', hint='<b>Predict first:</b> exec-1 dies after wave 0. How many waves does the rest take on exec-0 alone?',
             code='''remaining = 4                 # tasks of wave 1
slots_left = 2                # exec-0 only
lost_outputs = 2              # wave-0 tasks that ran on exec-1 must be redone
print("tasks to run:", remaining + lost_outputs, " waves:", -(-(remaining + lost_outputs) // slots_left))
'''),
        dict(label='3 · Executors for a cluster', hint='How many executors fit on a worker? Divide cores and memory.',
             code='''worker_cores, worker_mem_gb = 16, 64
exec_cores, exec_mem_gb = 4, 14     # leave memory for overhead and the OS
print("by cores :", worker_cores // exec_cores)
print("by memory:", worker_mem_gb // exec_mem_gb)
'''),
        dict(label='4 · Where is the driver?', hint='Pick a deploy mode for each situation.',
             code='''cases = {"notebook exploring data": "client",
         "nightly job from Airflow on YARN": "cluster",
         "Python app on standalone": "client (cluster not supported)"}
for k, v in cases.items():
    print(f"{v:32} <- {k}")
'''),
        dict(label='5 · Spot the error', hint='This plan puts the driver on a spot instance.', expect='error',
             code='''plan = {"driver": "spot", "executors": "spot"}
assert plan["driver"] != "spot", "a lost driver ends the job; keep it on reliable capacity"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: look at the parts',
    intro='<p>With the Docker cluster from Lesson 1.5 running. <b>Outputs are real.</b></p>',
    items=[
        dict(title='1 · Master status (JSON)', cmd='curl -s http://localhost:8090/json/', file='terminal',
             output=capf('l15_master.txt'),
             note='Shortened from the JSON. The same as the master web UI.'),
        dict(title='2 · Executors of an application', cmd='curl -s http://localhost:18080/api/v1/applications/<app-id>/executors', file='terminal',
             output=capf('l13_rest_city.txt').split('EXECUTORS\n')[1],
             note='The driver appears as an executor with 0 cores; it ran no tasks.'),
        dict(title='3 · Which master am I on?', cmd='spark.sparkContext.master\nspark.sparkContext.defaultParallelism', file='pyspark',
             output="'spark://spark-master:7077'\n4",
             note='Default parallelism = total executor cores (2 × 2).'),
    ],
)

TRACE = dict(
    heading='What the driver does when an executor is lost',
    intro='<p>Follow the bookkeeping behind Step 6.</p>',
    code='''map_outputs = {0: "exec-0", 1: "exec-1", 2: "exec-0", 3: "exec-1"}
alive = {"exec-1"}
lost = [p for p, e in map_outputs.items() if e not in alive]
for p in lost:
    map_outputs[p] = "exec-1"        # recompute from lineage
print("recomputed partitions:", lost, " now:", map_outputs)
''',
    notes={1: 'Shuffle files :: Each map task’s output lives on the executor that ran it.', 3: 'Lost :: exec-0’s files went with it, so partitions 0 and 2 must be redone.', 5: 'Lineage :: The driver knows how each partition was built and runs it again.'},
)

WORKED_INTRO = 'Three architecture decisions you will meet early.'
EXAMPLES = [
    dict(level='b', tag='Setup · local', title='Choose a local master',
         problem='<p>Pick a master URL for a laptop with 8 cores.</p>',
         inp='8-core laptop',
         approach=['local[*] uses all cores.', 'local[2] for tests.', 'Leave cores for other apps if needed.'],
         code='''for m, why in [("local[*]", "all 8 cores"), ("local[4]", "keep half for the IDE"), ("local[2]", "fast, predictable unit tests")]:
    print(f"{m:9} {why}")
''', notes={1: 'local[*] :: Our lab machine has 2 cores, so it gave parallelism 2.'},
         tryit='Check spark.sparkContext.defaultParallelism after starting.'),
    dict(level='i', tag='Platform · sizing', title='Size executors on a worker',
         problem='<p>A worker has 16 cores and 64 GB. Plan executors.</p>',
         inp='16 cores, 64 GB',
         approach=['4–5 cores per executor is common.', 'Leave 1 core and some memory for the OS.', 'Account for memory overhead.'],
         code='''cores, mem = 16 - 1, 64 - 4
per_exec_cores = 5
n = cores // per_exec_cores
per_exec_mem = mem / n / 1.1          # ~10% overhead
print(n, "executors x", per_exec_cores, "cores,", round(per_exec_mem), "GB each")
''', notes={4: 'Overhead :: spark.executor.memoryOverhead defaults to about 10% (min 384 MB).'},
         tryit='Lesson 8.5 sizes executors and dynamic allocation properly.'),
    dict(level='a', tag='Reliability · cloud', title='Design for lost executors',
         problem='<p>Make a nightly job survive spot interruptions.</p>',
         inp='YARN or Kubernetes on spot',
         approach=['Driver on on-demand.', 'Protect shuffle files.', 'Retries and timeouts.'],
         code='''settings = {"driver": "on-demand node",
            "spark.decommission.enabled": "true",
            "spark.storage.decommission.shuffleBlocks.enabled": "true",
            "spark.task.maxFailures": "4 (default)"}
for k, v in settings.items():
    print(f"{k:50} {v}")
''', notes={2: 'Decommission :: Executors leaving gracefully can migrate shuffle and cached blocks.'},
         tryit='In our lab the abrupt stop cost a 77 s timeout before recovery.'),
]

QUIZ = mix([
    dict(q='Beginner: Which process runs your main PySpark program?', options=['An executor', 'The driver', 'The worker', 'The history server'], answer=1,
         why='The driver ran 0 tasks but planned all of them.'),
    dict(q='Beginner: What runs the tasks?', options=['The driver', 'Executors', 'The master', 'Python only'], answer=1,
         why='Two executors shared the work.'),
    dict(q='Beginner: Which is NOT a Spark 4 cluster manager?', options=['Standalone', 'YARN', 'Kubernetes', 'Mesos'], answer=3,
         why='Mesos support was removed in Spark 4.0.'),
    dict(q='Intermediate: How many executors did a standalone job get in our lab?', options=['1', '2 (one per worker)', '4', '8'], answer=1,
         why='Each with 2 cores and 1 GiB.'),
    dict(q='Intermediate: What does local[2] mean?', options=['Two machines', 'One JVM with two task slots', 'Two drivers', 'Two executors'], answer=1,
         why='Driver and executor in one process.'),
    dict(q='Intermediate: --deploy-mode cluster for a Python app on standalone…', options=['Works', 'Is refused', 'Runs in local mode', 'Needs Mesos'], answer=1,
         why='Use client mode, YARN or Kubernetes.'),
    dict(q='Advanced: After a worker was stopped, why did map tasks run again?', options=['Bug', 'Its shuffle files were lost with the executor', 'AQE', 'Cache eviction'], answer=1,
         why='Lineage lets Spark recompute them.'),
    dict(q='Advanced: Where should the driver run on spot-heavy clusters?', options=['Spot', 'Reliable on-demand capacity', 'Any executor', 'The history server'], answer=1,
         why='A lost driver ends the application.'),
])

REVISION = [
    '<b>Driver</b>: main program, SparkSession, DAG, scheduling, results, UI :4040. One per app; single point of failure.',
    '<b>Cluster manager</b>: standalone, YARN, Kubernetes (Mesos removed in 4.0); none in <code>local[n]</code>.',
    '<b>Executors</b>: JVMs on workers; cores = task slots; run tasks, cache data, serve shuffle files.',
    'Lab: 2 executors × (2 cores, 1 GiB) granted instantly, registered ~8 s later; driver ran 0 tasks.',
    '<b>Client</b> mode: driver where you submit; <b>cluster</b> mode: driver in the cluster (not for Python on standalone).',
    'Worker lost → executor + shuffle files lost → FetchFailed (77 s) → resubmitted tasks → correct result.',
    'Keep the driver light: no <code>collect()</code> of big data.',
]
FAQ = [
    ('Is the driver the same as the master?', 'No. The standalone master is the cluster manager shared by all applications. Each application has its own driver. In our lab both happened to run in the same container because we submitted from there.'),
    ('How many executors should I use?', 'It depends on data size, cluster size and other users. Common starting points are 4–5 cores per executor and enough memory for the partitions each core processes. Dynamic allocation can add and remove executors automatically (Lesson 8.5).'),
    ('Where does Python run on the cluster?', 'The driver runs your Python program. For DataFrame operations, executors run JVM code only. For Python functions (RDD lambdas, Python UDFs), each executor starts Python worker processes, which is why Python versions must match (Lesson 1.5).'),
    ('What is the history server?', 'A web server that rebuilds the Spark UI from event logs after an application ends. Our lab runs one on port 18080; the screenshots in this lesson come from it.'),
    ('Can one cluster run many applications?', 'Yes. Each application gets its own driver and executors, isolated from the others; the cluster manager shares machines between them.'),
]

PRACTICE_INTRO = 'Programs about slots, executors and failures.'
PROBLEMS = [
    dict(level='easy', title='Total slots', stmt='Count task slots in a cluster.', inp='2 executors × 2 cores',
         code='''print(2 * 2)
''', explain='This is defaultParallelism in our lab.'),
    dict(level='easy', title='Waves', stmt='How many waves for 16 tasks on 4 slots?', inp='16, 4',
         code='''print(-(-16 // 4))
''', explain='Each wave runs as many tasks as there are slots.'),
    dict(level='easy', title='Master URL', stmt='Build a standalone master URL.', inp='host spark-master, port 7077',
         code='''print("spark://spark-master:7077")
''', explain='Pass with --master or SparkSession.builder.master().'),
    dict(level='medium', title='Executors per node', stmt='Executors per worker by cores and memory.', inp='32 cores, 128 GB, 5 cores and 18 GB per executor',
         code='''print(min((32 - 1) // 5, (128 - 8) // 18))
''', explain='The smaller limit wins.'),
    dict(level='medium', title='Recompute set', stmt='Which partitions must be recomputed?', inp='outputs per executor, one lost',
         code='''outs = {"e0": [0, 2, 4], "e1": [1, 3, 5]}
print(outs["e0"])
''', explain='Everything the lost executor produced and nobody else has.'),
    dict(level='medium', title='Deploy mode picker', stmt='Pick a deploy mode.', inp='interactive?',
         code='''for interactive in (True, False):
    print(interactive, "client" if interactive else "cluster")
''', explain='Interactive work needs the driver near you; scheduled jobs belong in the cluster.'),
    dict(level='business', title='Spot savings', stmt='Savings from spot executors.', inp='20 executors, ₹30/hour on-demand, ₹10/hour spot, 6 h/day (illustrative)',
         code='''print(f"₹{20 * (30 - 10) * 6 * 365:,} per year")
''', explain='Worth it when jobs tolerate occasional recomputation.'),
    dict(level='business', title='Cost of a timeout', stmt='Extra time from one lost executor.', inp='77 s stall, 30 jobs/day, 10% hit',
         code='''print(77 * 30 * 0.1 / 60, "minutes per day")
''', explain='Graceful decommissioning reduces this.'),
]

SCN_INTRO = 'Architecture questions appear in every Spark interview.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“Explain driver and executor”',
        'What do the driver and executors do?',
        'do you know the roles?',
        '<p>The driver runs my main program, creates the SparkSession, builds the DAG and schedules tasks. Executors are processes on worker nodes that run those tasks in parallel, cache data and exchange shuffle data. A cluster manager such as YARN, Kubernetes or Spark standalone launches the executors.</p>', '“The driver processes the data.”') +
    scn('Data engineering', 'Mid-level', 'Driver OutOfMemoryError',
        'A job fails with OutOfMemoryError in the driver.',
        'can you find the usual cause?',
        '''<ol>
          <li>Look for collect(), toPandas() or broadcast of large data.</li>
          <li>Write results from executors instead, or bring back a sample.</li>
          <li>Only then consider spark.driver.memory.</li>
        </ol>''', 'Increasing driver memory first.') +
    scn('Platform', 'Mid-level', 'Executor lost during a job',
        'Logs show “Lost executor” and FetchFailedException, but the job succeeded slowly.',
        'do you understand recovery?',
        '''<ul>
          <li>The executor and its shuffle files were lost; Spark recomputed missing map outputs from lineage.</li>
          <li>Find why: spot interruption, OOM-killed container, node failure.</li>
          <li>Mitigate: decommissioning, external shuffle service, right-sized memory.</li>
        </ul>''', 'Ignoring it because the job passed.') +
    scn('Architecture', 'Senior', 'Choose a cluster manager',
        'A new platform must run Spark for 20 teams.',
        'can you compare managers?',
        '''<ul>
          <li>YARN if Hadoop already exists; Kubernetes for container-based platforms and mixed workloads; serverless services to avoid operations.</li>
          <li>Standalone only for small dedicated clusters.</li>
          <li>Plan isolation (queues/namespaces), autoscaling and history server/log retention.</li>
        </ul>''', 'Picking Mesos (removed in Spark 4.0).')
)
