import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
def grab(n, *keys, limit=None):
    out = [l for l in capf(n).split('\n') if any(k in l for k in keys)]
    return '\n'.join(out[:limit] if limit else out)

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

def arch(hi=-1, dead=False, sub=''):
    """Driver, cluster manager, two workers with executors."""
    o = opbox(14, 60, 'Driver', 'SparkSession · DAG', 'acc' if hi == 0 else 'blue', 100, 32)
    o += opbox(140, 14, 'Cluster manager', 'standalone · YARN · K8s', 'acc' if hi == 1 else 'amber', 130, 30)
    o += arrow(64, 60, 140, 30, 'ink3', 1.3)
    for k, y in enumerate((70, 116)):
        d = dead and k == 1
        o += box(150, y, 196, 38, 'red' if d else ('acc' if hi == 2 else 'card'))
        o += t(156, y + 33, f'worker {k + 1}' + (' · stopped' if d else ''), 6.4, 'red' if d else 'ink2', anchor='start', bold=True)
        o += opbox(214, y + 6, 'Executor', '2 cores · tasks', 'card' if d else ('acc' if hi == 3 else 'green'), 124, 26)
        o += arrow(114, 76, 212, y + 19, 'red' if d else 'acc', 1.3)
    return o

# ---------------------------------------------------------------- story
sc = arch(-1) + (box(410, 12, 222, 136, 'card') + t(521, 30, 'Our cluster, really', 8.6, bold=True) +
      ''.join(t(422, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
          ('master: 2 workers, 4 cores, 4 GiB', 'ink'), ('executors granted in 0.1 s', 'green'), ('registered after ~8 s', 'amber'),
          ('cluster mode + Python: refused', 'red'), ('worker stopped → tasks re-run', 'green'), ('result still 5,000,000', 'green')])))
scene_svg = scene('A Spark application: one driver that plans, a cluster manager that hands out resources, and executors on worker machines that run tasks. Our lab cluster showed every part at work, including what happens when a worker disappears.', sc,
                  'The driver <tspan font-weight="700" class="s-acc">plans</tspan>; executors <tspan font-weight="700" class="s-acc">do</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Who actually does the work?”</h2>
  <div class="story">
    <p class="narration">Riya ran her first PySpark job on the lab cluster. It printed the right report, but she has questions: her laptop sent the code, yet the work happened “somewhere”. Kabir wonders what happens if one of the machines dies halfway, as it once did during a Hive load.</p>

{scene_svg}

R> Sir, where does my Python code actually run?
A> Your <code>main</code> program runs in the <b>driver</b>. The driver asks a <b>cluster manager</b> for resources, gets <b>executors</b> on worker machines, splits the job into <b>tasks</b> and sends them out. Executors run the tasks and keep cached data. The driver collects the results.
K> And if a worker dies?
A> Then the driver notices, and recomputes the lost pieces on the executors that are left, using the recorded <b>lineage</b>. We will stop a worker in the middle of a job and watch. Everything today runs on our Spark 4.3.0 standalone cluster in Docker: one master, two workers with 2 cores and 2 GiB each.
  </div>
</section>
'''

lv = '''
LEVELS> Spark architecture at three levels
L1> A restaurant kitchen
      <ul>
        <li>The <b>head chef</b> (driver) reads the order and plans the dishes.</li>
        <li>The <b>kitchen manager</b> (cluster manager) decides which cooks and stoves are free.</li>
        <li>The <b>cooks</b> (executors) cook their parts in parallel. If a cook leaves, the head chef gives that part to another cook.</li>
      </ul>
L2> The pieces and their jobs
      <ul>
        <li><b>Driver</b>: runs your program, holds the SparkSession, builds the DAG, schedules tasks, tracks results. One per application.</li>
        <li><b>Cluster manager</b>: Spark standalone, YARN or Kubernetes (Mesos was removed in Spark 4.0); or none in <code>local[*]</code> mode.</li>
        <li><b>Executors</b>: JVM processes on workers with a number of cores (task slots) and memory; they run tasks, store shuffle files and cached blocks. For Python functions they start Python worker processes.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>The master granted two executors (2 cores, 1 GiB each) instantly; they registered with the driver about 8 s later; the first task started 2 s after that.</li>
        <li>Submitting a Python app in <code>cluster</code> deploy mode to a standalone master was refused; client mode worked.</li>
        <li>Stopping a worker mid-stage lost an executor and its shuffle files; after a 77 s fetch timeout Spark resubmitted the missing tasks and still returned 5,000,000.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Driver, cluster manager and executors</h2>
''' + def_block(
    'A <b>Spark application</b> consists of a <b>driver</b> process and a set of <b>executor</b> processes. The driver runs the application’s main program, creates the SparkSession (and SparkContext), converts operations into a directed acyclic graph of stages, and schedules their <b>tasks</b> onto executors. Executors are launched on worker nodes by a <b>cluster manager</b> (Spark standalone, Hadoop YARN or Kubernetes); each runs tasks in a number of concurrent slots (cores), keeps data cached in memory or on disk, and serves shuffle data to other executors. Applications are isolated from each other; in <b>client</b> deploy mode the driver runs where the job was submitted, in <b>cluster</b> mode inside the cluster. If an executor is lost, the driver recomputes the lost partitions from their lineage.',
    'Every Spark program has one boss (the driver) and many workers (executors). A cluster manager gives the driver its executors. The driver splits the job into tasks; executors run them. If an executor dies, the driver redoes its part.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Application', 'One SparkSession: one driver plus its executors.'),
    ('Driver', 'Runs your main program; plans and schedules.'),
    ('Executor', 'A JVM on a worker that runs tasks and stores data.'),
    ('Task', 'The smallest unit of work: one partition, one stage.'),
    ('Core / slot', 'How many tasks an executor runs at the same time.'),
    ('Cluster manager', 'Gives out machines: standalone, YARN, Kubernetes.'),
    ('Deploy mode', 'Client (driver where you submit) or cluster (driver in the cluster).'),
    ('Lineage', 'The recipe for each partition; used to recompute lost work.'),
]) + '''

  <h3>Who does what</h3>
''' + table(['Component', 'How many', 'Does', 'Seen in our lab'], [
    ['Driver', '1 per application', 'Plans the DAG, schedules tasks, collects results, hosts the UI (port 4040)', '<code>spark-master</code>, 0 tasks run itself'],
    ['Cluster manager (standalone master)', '1 per cluster', 'Tracks workers, grants executors', '2 workers, 4 cores, 4 GiB'],
    ['Worker', 'Many', 'Starts executor processes', '2 containers'],
    ['Executor', 'Several per app', 'Runs tasks, caches, writes shuffle files', '2 × (2 cores, 1 GiB)'],
    ['Task', 'One per partition per stage', 'Processes one partition', '1–16 per stage'],
], minw=760) + lv + '''
EXAM> “Explain Spark’s architecture.” A driver runs the main program, builds the DAG and schedules tasks; a cluster manager (standalone, YARN, Kubernetes) allocates executors on worker nodes; executors run tasks in parallel, cache data and exchange shuffle data. Failures are handled by recomputing lost partitions from lineage.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Cluster managers and deploy modes</h2>
''' + table(['Mode / manager', 'Master URL', 'Where it fits', 'Notes (Spark 4.3)'], [
    ['Local', '<code>local[*]</code>, <code>local[2]</code>', 'Laptop, tests, learning', 'Driver and executor in one JVM'],
    ['Spark standalone', '<code>spark://host:7077</code>', 'Small dedicated clusters, this course’s lab', 'Simple; Python apps: client mode only'],
    ['Hadoop YARN', '<code>yarn</code>', 'Existing Hadoop clusters, EMR on EC2, Dataproc', 'Queues, Kerberos, HDFS locality (Lesson 11.2)'],
    ['Kubernetes', '<code>k8s://https://…</code>', 'Cloud-native platforms, EMR on EKS', 'Executors as pods (Lesson 11.2)'],
    ['Apache Mesos', '—', '—', 'Removed in Spark 4.0'],
], minw=760) + table(['Deploy mode', 'Driver runs', 'Good for', 'Watch out for'], [
    ['client (default)', 'Where you run spark-submit / your notebook', 'Interactive work, notebooks, debugging', 'Laptop must stay connected; network to executors'],
    ['cluster', 'Inside the cluster (YARN container, K8s pod)', 'Production jobs, schedulers', 'Logs are on the cluster; not for Python on standalone'],
], minw=680) + '''
WARN> The driver is a single point of failure for its application. Executors can be replaced; a crashed driver ends the job. Keep the driver light: avoid <code>collect()</code> of large results, which pulls all the data into the driver’s memory (Lesson 4.6).
</section>
'''

FIGS = fig('ui-exec.webp', 1280, 700, 'Spark UI Executors tab listing the driver and two executors with their cores, tasks and memory', 'Real screenshot: the Executors tab for one of our applications (from the history server). The driver runs no tasks; two executors with 2 cores each did all the work.')
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Watching driver, master and executors work</h2>
  <p>All outputs are real: Spark 4.3.0 in Docker (Lesson 1.5 builds this cluster), one standalone master and two workers with 2 cores and 2 GiB each, plus a history server. Logs are shortened; nothing else is changed.</p>
''' + FIGS + stepper([
    ('Step 1 · Local mode: everything in one JVM',
     code('python', 'local_modes.py', 'for master in ["local[1]", "local[2]", "local[*]"]:\n    spark = SparkSession.builder.master(master).getOrCreate()\n    sc = spark.sparkContext\n    execs = sc._jsc.sc().getExecutorMemoryStatus().size()\n    print(master, sc.defaultParallelism, execs)\n    spark.stop()', capf('l13_local.txt')),
     'In local mode there is no cluster manager: the driver JVM also acts as the only executor, and the number in brackets is the number of task slots. <code>local[*]</code> used all 2 cores of the lab machine. Perfect for learning and tests, but there is no fault tolerance across machines.'),
    ('Step 2 · Submit to the cluster: executors are granted',
     code('bash', 'spark-submit', 'spark-submit --master spark://spark-master:7077 \\\n  --conf spark.eventLog.enabled=true --conf spark.eventLog.dir=/opt/spark-events \\\n  /jobs/m1/city_report.py', grab('l13_driver_log.txt', 'Running Spark', 'Connected', 'Granted', 'Registered executor')),
     'The driver connected to the master, which granted one executor on each worker within the same second: <b>2 cores and 1 GiB</b> each (1 GiB is the default <code>spark.executor.memory</code>). The executors took about 7–8 s to start their JVMs and <b>register</b> with the driver. Only then can tasks run.'),
    ('Step 3 · The driver hands out tasks',
     code('text', 'driver log (continued)', '# same run, scheduler lines only', grab('l13_driver_log.txt', 'Got job', 'Submitting', 'Starting task', 'Finished task', 'finished', limit=11)),
     'For each job the driver’s <b>DAGScheduler</b> creates stages and submits their tasks; the <b>TaskSetManager</b> places each task on a free slot. Job 0 ran on executor 0, job 1 on executor 1: the driver uses whichever slot is free. Our small CSV is one partition, so each stage had only one task. (Why one <code>show()</code> started four jobs is Lesson 1.4.)'),
    ('Step 4 · Who did the work?',
     code('bash', 'history server REST API', 'curl -s http://localhost:18080/api/v1/applications/<app-id>/executors', capf('l13_rest_city.txt').split('EXECUTORS\n')[1]),
     'The driver ran <b>0 tasks</b>: it only planned and scheduled. The two executors shared the four tasks. “task time” for the driver is simply its uptime. The same numbers are on the Executors tab shown above.'),
    ('Step 5 · Client vs cluster deploy mode',
     code('bash', 'spark-submit', 'spark-submit --master spark://spark-master:7077 --deploy-mode cluster /jobs/m1/city_report.py', capf('l13_clustermode.txt').split('\n')[0]),
     'In <b>client</b> mode (the default, Steps 2–4) the driver ran inside the container where we typed <code>spark-submit</code>. <b>Cluster</b> mode puts the driver inside the cluster, so you can disconnect; Spark’s standalone manager refuses it for Python applications. On YARN and Kubernetes, Python apps can run in cluster mode (Lesson 11.2).'),
    ('Step 6 · A worker disappears in the middle of a job',
     code('bash', 'failover.py running, then', 'docker stop sparklab-spark-worker-2-1', capf('l13_failover.txt').split('\n', 1)[1]),
     'We stopped one worker while stage 13 was running. The driver marked executor 0 as lost and knew its <b>shuffle files</b> were gone too. Tasks reading those files waited until the fetch timed out (77 s), then failed with <code>FetchFailed</code>. Spark <b>resubmitted</b> the 2 lost map tasks of stage 12 and the 8 affected tasks of stage 13 on the surviving executor, using lineage. The job finished with the correct 5,000,000 orders. Slower, but right.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('local[2]  parallelism=2', W), ('executors: 1 (the driver)', Y), ('no cluster manager', W)], size=7.8),
    term([('Connected to Spark cluster', W), ('Granted executor 0: 2 cores, 1 GiB', G), ('Granted executor 1: 2 cores, 1 GiB', G), ('registered ~8 s later', Y)], size=7.2),
    term([('Got job 0 · Submitting 1 task', W), ('Starting task 0.0 → executor 0', G), ('job 1 task → executor 1', G), ('driver: 0 tasks itself', Y)], size=7.2),
    term([('--deploy-mode cluster', W), ('Cluster deploy mode is currently', RD), ('not supported for python apps', RD), ('on standalone clusters', RD)], size=7.2),
    term([('docker stop worker-2', W), ('Lost executor 0', RD), ('FetchFailed after 77 s', Y), ('Resubmitting stages 12, 13', G), ('orders: 5000000', G)], size=7.2),
]
B1 = [
    arch(0) + cap('Local: driver = executor.', '', 'blue', y=160, h=26),
    arch(1) + cap('The manager grants executors.', '', 'amber', y=160, h=26),
    arch(3) + cap('Tasks go to free slots.', '', 'green', y=160, h=26),
    arch(0) + cap('Where does the driver live?', '', 'violet', y=160, h=26),
    arch(0, dead=True) + cap('Lost work is recomputed from lineage.', '', 'green', y=160, h=26),
]
see_caps = ['Local mode: one JVM does everything.',
            'The master gave us two executors.',
            'The driver placed each task on a free slot.',
            'Cluster mode was refused for Python on standalone.',
            'A worker died; the job still finished correctly.']
behind_caps = ['Slots = the number in local[n].',
               'Each executor: 2 cores, 1 GiB by default.',
               'DAGScheduler → TaskSetManager → executor.',
               'Client mode: driver where you submit.',
               'Shuffle files were lost too, so map tasks re-ran.']
two = anim_two('Spark architecture', 'Driver, manager, executors', 'Real lab outputs', 'Who does what', see, B1, see_caps, behind_caps)

# ---- scenario 1: driver OOM from collect
e1 = (t(180, 22, 'Job dies at the end', 9.4, bold=True) + t(180, 56, 'java.lang.OutOfMemoryError in the driver', 8.2, 'ink', mono=True) + cap('Executors were fine.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Look at the last line', 9.4, bold=True) + t(180, 56, 'rows = df.collect()   # 40 million rows', 8.2, 'ink', mono=True) + cap('All data pulled to one JVM.', '', 'amber', y=150, h=34))
e3 = (t(180, 22, 'Keep work on executors', 9.4, bold=True) + t(180, 56, 'df.write.parquet(…)', 8.4, 'ink', mono=True) + cap('Write results in parallel.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Need a sample?', 9.4, bold=True) + t(180, 56, 'df.limit(100).toPandas()', 8.4, 'ink', mono=True) + cap('Bring back only a little.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Driver stays light', 9.4, 'acc', bold=True) + t(180, 56, 'plan, schedule, small results', 8.4, 'ink2') + cap('The architecture rule.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'The driver that ran out of memory',
              'One of the most common Spark failures. (Typical; architecture from our lab.)',
              'Driver memory', 'collect() pulls every row into the single driver; write results from executors or bring back only small samples', [e1, e2, e3, e4, e5],
              ['Driver OOM.', 'collect() on big data.', 'Write in parallel.', 'Sample if needed.', 'Light driver.'],
              hid='scenario-collect')

# ---- scenario 2: spot instances
b1 = (t(180, 22, 'Cheap spot machines', 9.4, bold=True) + t(180, 56, 'executors on instances that can vanish', 8.2, 'ink2') + cap('Like our docker stop.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'One disappears', 9.4, bold=True) + t(180, 56, 'Lost executor · FetchFailed', 8.4, 'ink', mono=True) + cap('Shuffle files lost too.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'Spark recomputes', 9.4, bold=True) + t(180, 56, 'resubmit lost map tasks', 8.4, 'ink2') + cap('Correct result, later.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Reduce the pain', 9.4, bold=True) + t(180, 56, 'decommissioning · external shuffle service', 8, 'ink2') + cap('Keep or migrate shuffle data.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Driver on-demand', 9.4, 'acc', bold=True) + t(180, 56, 'never put the driver on spot', 8.4, 'ink2') + cap('It cannot be replaced.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Running executors on spot instances',
              'How cloud teams save money safely. (Typical practice; failure behaviour from our lab.)',
              'Fault tolerance', 'Executors can be lost and their work recomputed; protect shuffle data and keep the driver on reliable machines', [b1, b2, b3, b4, b5],
              ['Cheap but unreliable.', 'An executor is lost.', 'Lineage saves the job.', 'Protect shuffle files.', 'Driver on-demand.'],
              hid='scenario-spot')

# ---- scenario 3: notebook disconnect
u1 = (t(180, 22, 'Overnight job from a laptop', 9.4, bold=True) + t(180, 56, 'client mode, laptop goes to sleep', 8.2, 'ink2') + cap('The driver was on the laptop.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Job killed', 9.4, bold=True) + t(180, 56, 'executors lose their driver', 8.4, 'ink2') + cap('Hours of work gone.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'Cluster mode', 9.4, bold=True) + t(180, 56, '--deploy-mode cluster (YARN / K8s)', 8.2, 'ink', mono=True) + cap('Driver lives in the cluster.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Or a scheduler', 9.4, bold=True) + t(180, 56, 'Airflow submits from a server', 8.4, 'ink2') + cap('Not from a laptop.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Notebooks: Spark Connect', 9.4, 'acc', bold=True) + t(180, 56, 'thin client, server-side driver', 8.2, 'ink2') + cap('Lesson 11.3.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'The job that died when the laptop slept',
              'Why deploy mode matters in production. (Typical; standalone limit from our lab.)',
              'Deploy modes', 'In client mode the driver dies with the client; use cluster mode, a scheduler host or Spark Connect for long jobs', [u1, u2, u3, u4, u5],
              ['Driver on the laptop.', 'Laptop sleeps, job dies.', 'Driver in the cluster.', 'Schedule from servers.', 'Remote driver for notebooks.'],
              hid='scenario-deploy')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Driver, manager, executors</h2>
  <p>Left: real outputs. Right: who does what.</p>
''' + two + '''
  <p>Three live scenarios follow: a driver out of memory, executors on spot instances, and a job lost with a sleeping laptop.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Architecture decisions at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'YARN', 12, 'blue', bold=True) + t(60, 58, 'Hadoop', 7.4, 'ink2'),
    '1. Spark on existing Hadoop clusters',
    'Companies with Hadoop run Spark on YARN next to Hive, sharing HDFS, queues and security.',
    ['spark-submit', '*YARN', 'Executors']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'K8s', 12, 'green', bold=True) + t(60, 58, 'pods', 7.4, 'ink2'),
    '2. Spark on Kubernetes',
    'Cloud-native teams run drivers and executors as pods, often with the Spark Operator or EMR on EKS.',
    ['Job', '*K8s', 'Pods']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'spot', 12, 'violet', bold=True) + t(60, 58, 'savings', 7.4, 'ink2'),
    '3. Cheap executors, safe driver',
    'AWS cites Krux running Spark on ephemeral EMR clusters with Spot instances; the driver stays on reliable nodes.',
    ['Spot', '*executors', 'Lower cost']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'serverless', 8, 'acc', bold=True) + t(60, 58, 'Spark', 7.4, 'ink2'),
    '4. Serverless Spark',
    'EMR Serverless, Dataproc Serverless and Databricks serverless hide the cluster manager entirely.',
    ['Code', '*service', 'Executors on demand']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'local', 11, 'acc', bold=True) + t(60, 58, 'tests', 7.4, 'ink2'),
    '5. Unit tests in local mode',
    'CI pipelines run PySpark tests with local[2]: same code, one JVM (Lesson 11.4).',
    ['Test', '*local[2]', 'Pass']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> Lesson <a href="../02-what-is-apache-spark/">1.2</a>. Coming from Hadoop? Driver ≈ ApplicationMaster’s planning role, executors ≈ long-lived containers that run many tasks.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
