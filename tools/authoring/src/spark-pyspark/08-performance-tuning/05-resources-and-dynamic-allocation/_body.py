import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l85_resources.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)

# executors over time (t s, executors) from the dynamic-allocation run
DYN = [(2, 0), (20, 1), (22, 3), (26, 4), (65, 2), (67, 0), (101, 1), (103, 2), (105, 3), (107, 4), (132, 4)]
def timeline(x, y, w=320, h=60, pts=DYN, tmax=135, nmax=4, tone='green', jobs=((6, 51), (92, 132))):
    o = box(x, y, w, h, 'card')
    for a, b in jobs:
        o += box(x + a / tmax * w, y + h + 4, (b - a) / tmax * w, 8, 'blue', rx=2)
    d = ''
    for k, (tt, n) in enumerate(pts):
        px, py = x + tt / tmax * w, y + h - n / nmax * (h - 8)
        if k:
            d += f' L{px:.1f},{prev:.1f} L{px:.1f},{py:.1f}'
        else:
            d = f'M{px:.1f},{py:.1f}'
        prev = py
    o += f'<path d="{d}" fill="none" stroke="var(--green)" stroke-width="2"/>'
    o += t(x - 4, y + 10, '4', 6.6, 'ink2', anchor='end') + t(x - 4, y + h, '0', 6.6, 'ink2', anchor='end')
    o += t(x + w, y + h + 22, 'blue = jobs running', 6.6, 'blue', anchor='end')
    return o

# ---------------------------------------------------------------- story
sc_ = (t(14, 24, 'executors over time (dynamic allocation)', 7.4, 'ink2', anchor='start', bold=True) + timeline(24, 34, 340, 70) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured (2-worker cluster)', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('static: 4 executors held', 'amber'), ('  for the whole 93 s', 'amber'),
           ('dynamic: 0 → 4 → 0 → 4', 'green'), ('  released when idle', 'green'),
           ('cold start: +14 s', 'red'), ('3g executor: never starts', 'red')])))
scene_svg = scene('Executors are the processes that run Spark tasks; their number, cores and memory decide how much work runs at once. On a two-worker standalone cluster we held 4 executors statically, then let dynamic allocation add and remove them, and asked for executors bigger than any worker.', sc_,
                  'Dynamic allocation gives cores back <tspan font-weight="700" class="s-acc">when you are idle</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Our cluster is full, but nothing is running”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s shared cluster kept rejecting new jobs. The UI showed every core taken, yet most applications were notebooks sitting idle for hours, each holding the executors it got at start-up.</p>

{scene_svg}

K> Sir, an idle notebook is not running anything. Why does it keep the machines?
A> Because by default an application keeps the executors it asked for until it ends. <b>Dynamic allocation</b> lets Spark request executors when tasks are waiting and release them after they have been idle for a while.
R> And how big should each executor be?
A> That is the other half: cores, memory and how many executors. Today we run on a real standalone cluster: static vs dynamic, a <code>cores.max</code> cap, and an executor too big to fit anywhere. All outputs are real (Spark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Resources at three levels
L1> Hiring delivery riders
      <ul>
        <li>Static: hire 50 riders for the whole day, even at 3 pm when nobody orders.</li>
        <li>Dynamic: call riders in when orders queue up, send them home after 10 idle minutes. Cheaper, but the first orders of the dinner rush wait a bit.</li>
      </ul>
L2> The settings
      <ul>
        <li>Size: <code>spark.executor.cores</code>, <code>spark.executor.memory</code>, <code>spark.executor.instances</code> (static), <code>spark.cores.max</code> (standalone cap).</li>
        <li>Dynamic: <code>spark.dynamicAllocation.enabled</code>, <code>…minExecutors</code>, <code>…maxExecutors</code>, <code>…executorIdleTimeout</code> (60 s), <code>…schedulerBacklogTimeout</code> (1 s), plus <code>…shuffleTracking.enabled</code> or an external shuffle service.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>Static: 4 one-core executors held from start to end (job 1 30.9 s, job 2 16.0 s).</li>
        <li>Dynamic: 0 → 4 executors in 6 s once tasks queued, back to 0 after ~15 idle seconds, up again for job 2.</li>
        <li>Asking for 3 GB executors on 2 GB workers: “Initial job has not accepted any resources”.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Executor resources and dynamic allocation</h2>
''' + def_block(
    'A Spark application’s capacity is the number of <b>executors</b> times their <b>cores</b> (task slots), each with a fixed heap (<code>spark.executor.memory</code>) and off-heap overhead. The cluster manager (standalone, YARN or Kubernetes) launches executors only on nodes with enough free cores and memory. With <b>static allocation</b>, the application keeps a fixed set of executors for its lifetime. With <b>dynamic allocation</b> (<code>spark.dynamicAllocation.enabled=true</code>), Spark requests more executors when tasks have been pending longer than <code>schedulerBacklogTimeout</code>, growing exponentially up to <code>maxExecutors</code>, and removes executors idle for <code>executorIdleTimeout</code>. Because removed executors may hold shuffle files, dynamic allocation needs an <b>external shuffle service</b> or <b>shuffle tracking</b>, which keeps executors with live shuffle data until <code>shuffleTracking.timeout</code>.',
    'An application runs tasks on executors; executors × cores is how many tasks run at once. Normally an app keeps its executors until it ends. With dynamic allocation, Spark asks for executors when work is waiting and gives them back when they sit idle, so shared clusters are used better.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Executor', 'JVM process that runs tasks.'),
    ('Executor cores', 'Task slots per executor.'),
    ('Cluster manager', 'Standalone, YARN, Kubernetes.'),
    ('Static allocation', 'Fixed executors for the app’s life.'),
    ('Dynamic allocation', 'Executors added/removed by load.'),
    ('Backlog timeout', 'Pending time before asking for more.'),
    ('Idle timeout', 'Idle time before release (60 s).'),
    ('Shuffle tracking', 'Keep executors that hold shuffle data.'),
]) + '''

  <h3>Static vs dynamic</h3>
''' + table(['', 'Static', 'Dynamic', 'Lab'], [
    ['Executors', 'Fixed (instances or all cores)', 'min … max, by backlog', '4 vs 0→4→0→4'],
    ['Idle cost', 'Holds resources', 'Releases after idle timeout', 'released ~15 s after job 1'],
    ['Start-up', 'Ready immediately', 'Ramp-up delay', 'job 1: 30.9 s vs 45.0 s'],
    ['Best for', 'Steady pipelines, SLAs', 'Shared clusters, notebooks, varying load', ''],
], minw=620) + lv + '''
EXAM> “What is dynamic allocation?” Spark scales the number of executors of an application with its workload: it requests executors when tasks are backlogged (up to maxExecutors) and removes executors idle longer than executorIdleTimeout (default 60 s). It requires an external shuffle service or <code>spark.dynamicAllocation.shuffleTracking.enabled</code> so shuffle files are not lost. It improves utilisation of shared clusters at the cost of ramp-up latency.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Sizing executors</h2>
''' + table(['Shape', 'Example', 'Pros', 'Cons'], [
    ['Tiny (1 core)', '1 core, 1–2 GB', 'Fine-grained', 'No sharing of broadcasts/cache; JVM overhead per core'],
    ['Balanced', '4–5 cores, 16–32 GB', 'Good I/O throughput, shared broadcast', 'Common default'],
    ['Fat (whole node)', '32+ cores, 200 GB', 'Few JVMs', 'Long GC pauses, HDFS client contention'],
], minw=620) + '''
WARN> An executor must fit on one worker: <b>cores and memory plus overhead</b>. Ask for more than any node has and Spark does not fail, it <b>waits forever</b>, logging “Initial job has not accepted any resources”. Also, cores are only as real as the hardware: our 2 workers advertise 4 cores on a host with 2 physical CPUs, which is why 4 executors were not faster than 2 in the lab.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Executors on a real cluster</h2>
  <p>All outputs are real: Spark 4.3.0 standalone cluster in Docker, 1 master and 2 workers with 2 cores and 2 GB each (host: 2 physical CPUs). Each run submits the same application: wait 6 s, job 1 (30M SHA hashes), idle 40 s, job 2. A thread polls <code>/api/v1/applications/…/executors</code> every 2 s.</p>
''' + stepper([
    ('Step 1 · Static allocation',
     code('bash', 'submit', 'spark-submit --master spark://spark-master:7077 \\\n  --conf spark.executor.cores=1 --conf spark.executor.memory=1g \\\n  /jobs/l85_resources.py', sec('### --conf spark.executor.cores=1 --conf spark.executor.memory=1g\n', '### --conf spark.cores.max')),
     'With 1-core executors, the standalone master started <b>4 executors</b> (2 per worker) and the app kept all 4 for its whole life, including the 40 idle seconds. Job 1 (30.9 s) includes JVM warm-up; job 2 took 16.0 s.'),
    ('Step 2 · Capping with cores.max',
     code('bash', 'submit', 'spark-submit … --conf spark.cores.max=2 --conf spark.executor.cores=1 /jobs/l85_resources.py', sec('### --conf spark.cores.max', '### --conf spark.executor.cores=1 --conf spark.executor.memory=1g --conf spark.dynamicAllocation')),
     'On standalone, an app takes all free cores unless capped. With <code>cores.max=2</code> it got <b>2 executors</b>, leaving 2 cores for other apps, and was not slower (24.5 s / 14.1 s), because our host has only 2 physical CPUs. Advertised cores beyond the real CPUs only add contention.'),
    ('Step 3 · Dynamic allocation',
     code('bash', 'submit', 'spark-submit … --conf spark.executor.cores=1 --conf spark.executor.memory=1g \\\n  --conf spark.dynamicAllocation.enabled=true \\\n  --conf spark.dynamicAllocation.shuffleTracking.enabled=true \\\n  --conf spark.dynamicAllocation.executorIdleTimeout=10s \\\n  --conf spark.dynamicAllocation.shuffleTracking.timeout=10s \\\n  --conf spark.dynamicAllocation.minExecutors=0 --conf spark.dynamicAllocation.maxExecutors=4 \\\n  /jobs/l85_resources.py', sec('### --conf spark.executor.cores=1 --conf spark.executor.memory=1g --conf spark.dynamicAllocation', '### --conf spark.executor.memory=3g', drop=('###',))),
     'The timeline tells the story. At 2 s: <b>0</b> executors. Job 1 queued tasks, so Spark requested 1, then 3, then 4 executors (20–26 s). After job 1 finished, idle executors were released (2 at 65 s, 0 at 67 s). Job 2 brought them back (101–107 s). The cost: every job started cold, so job 1 took 45.0 s and job 2 41.3 s instead of 30.9 s and 16.0 s. Production idle timeouts are longer (60 s default) to avoid that churn.'),
    ('Step 4 · An executor that does not fit',
     code('bash', 'submit', 'spark-submit … --conf spark.executor.memory=3g /jobs/l85_resources.py   # workers have 2g', sec('### --conf spark.executor.memory=3g')),
     'No error, no executors. The app waited, logging this warning every 15 s, until we killed it. In the master UI its state was <b>WAITING</b> with 0 cores. Always check executor size against node size, including memory overhead on YARN and Kubernetes.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('static: executors over time', W), ('[(6, 4, 4)]', Y), ('job 1 30.9 s | job 2 16.0 s', W)], size=7.4),
    term([('cores.max=2: [(2, 2, 2)]', G), ('job 1 24.5 s | job 2 14.1 s', W)], size=7.4),
    term([('dynamic: (2,0) (20,1) (22,3) (26,4)', G), ('(65,2) (67,0)  released', G), ('(101,1) ... (107,4) again', G), ('job 1 45.0 s | job 2 41.3 s', Y)], size=7.0),
    term([('executor.memory=3g', W), ('Initial job has not accepted', RD), ('any resources', RD)], size=7.4),
]
B1 = [
    t(180, 14, 'Static: hold everything', 9.4, bold=True) + timeline(24, 40, 320, 60, pts=[(0, 4), (135, 4)], jobs=((6, 37), (77, 93))) + cap('Idle cores stay reserved.', '', 'amber', y=144, h=30),
    t(180, 14, 'cores.max caps the app', 9.4, bold=True) + ''.join(opbox(30 + k * 80, 50, f'core {k + 1}', 'app' if k < 2 else 'free', 'green' if k < 2 else 'card', 70, 30) for k in range(4)) + cap('Room for other apps.', '', 'green', y=144, h=30),
    t(180, 14, 'Dynamic: follow the backlog', 9.4, bold=True) + timeline(24, 40, 320, 60) + cap('Add on backlog, remove when idle.', '', 'green', y=144, h=30),
    t(180, 14, 'Must fit on one worker', 9.4, bold=True) + opbox(30, 46, 'worker', '2 cores · 2 GB', 'card', 130, 34) + opbox(200, 46, 'executor ask', '3 GB', 'red', 130, 34) + t(180, 110, 'never placed → app WAITING', 7.6, 'red') + cap('Size executors from nodes.', '', 'amber', y=144, h=30),
]
see_caps = ['Static allocation.', 'cores.max cap.', 'Dynamic allocation.', 'Too-big executor.']
behind_caps = ['Fixed executors.', 'Sharing a standalone cluster.', 'Scale up and down.', 'Placement constraints.']
two = anim_two('Executors and dynamic allocation', 'How many executors, when', 'Real cluster outputs', 'What the cluster does', see, B1, see_caps, behind_caps)

e1 = (t(180, 22, '30 notebooks, all idle', 9.4, bold=True) + t(180, 56, 'each holding 10 executors', 8.4, 'ink2') + cap('Cluster “full”.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Enable dynamic allocation', 9.4, bold=True) + t(180, 56, 'min 0, idle timeout 10 min', 8.4, 'ink2') + cap('Plus shuffle tracking.', '', 'green', y=150, h=34))
e3 = (t(180, 22, 'Idle notebooks release', 9.4, bold=True) + t(180, 56, '0 → 4 → 0 in our lab', 8.4, 'ink2') + cap('Cores return to the pool.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'First query waits a bit', 9.4, bold=True) + t(180, 56, 'executor start-up seconds', 8.4, 'ink2') + cap('Acceptable for notebooks.', '', 'amber', y=150, h=34))
e5 = (t(180, 22, 'More users per cluster', 9.4, 'acc', bold=True) + t(180, 56, 'same hardware', 8.4, 'ink2') + cap('Lower cost.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'The full but idle cluster',
              'Dynamic allocation for notebooks. (Typical; timeline from our lab.)',
              'Dynamic allocation', 'Dynamic allocation releases idle executors from interactive sessions', [e1, e2, e3, e4, e5],
              ['Idle.', 'Enable.', 'Release.', 'Ramp-up.', 'Shared.'],
              hid='scenario-notebooks')
b1 = (t(180, 22, 'Nightly job has an SLA', 9.4, bold=True) + t(180, 56, 'must finish by 6 am', 8.4, 'ink2') + cap('Predictability matters.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Dynamic: slow ramp-up', 9.4, bold=True) + t(180, 56, 'cold executors per stage gap', 8.4, 'ink2') + cap('45.0 s vs 30.9 s in our lab.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'Raise minExecutors', 9.4, bold=True) + t(180, 56, 'or initialExecutors', 8.4, 'ink2') + cap('Warm baseline.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Or static for this job', 9.4, bold=True) + t(180, 56, 'spark.executor.instances=40', 8.4, 'ink', mono=True) + cap('Dedicated window.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Measure both', 9.4, 'acc', bold=True) + t(180, 56, 'runtime and cluster cost', 8.4, 'ink2') + cap('Pick per workload.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'When dynamic is too slow',
              'Ramp-up latency vs utilisation. (Typical; timings from our lab.)',
              'Ramp-up', 'Dynamic allocation adds start-up latency; use minExecutors or static allocation for SLA jobs', [b1, b2, b3, b4, b5],
              ['SLA.', 'Ramp-up.', 'Baseline.', 'Static.', 'Measure.'],
              hid='scenario-sla')
u1 = (t(180, 22, 'Job stuck at 0 tasks', 9.4, bold=True) + t(180, 56, 'no errors for 20 minutes', 8.4, 'ink2') + cap('Logs: not accepted any resources.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Check executor size', 9.4, bold=True) + t(180, 56, '30g + 3g overhead per executor', 8.4, 'ink2') + cap('Nodes have 32 GB.', '', 'red', y=150, h=34))
u3 = (t(180, 22, 'Or the queue is full', 9.4, bold=True) + t(180, 56, 'YARN queue / K8s quota', 8.4, 'ink2') + cap('Same symptom.', '', 'amber', y=150, h=34))
u4 = (t(180, 22, 'Resize to fit nodes', 9.4, bold=True) + t(180, 56, '5 cores, 20g + 2g overhead', 8.4, 'ink2') + cap('Several per node.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Executors start in seconds', 9.4, 'acc', bold=True) + t(180, 56, 'tasks flow', 8.4, 'ink2') + cap('Fixed.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'The job that never started',
              'Executor sizing vs node capacity. (Typical; warning reproduced in our lab.)',
              'Placement', 'Executors bigger than any node, or full queues, leave an app waiting without an error', [u1, u2, u3, u4, u5],
              ['Stuck.', 'Too big.', 'Queue.', 'Resize.', 'Running.'],
              hid='scenario-fit')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>How many executors, when</h2>
  <p>Left: real cluster outputs. Right: what the cluster manager does.</p>
''' + two + '''
  <p>Three live scenarios follow: idle notebooks, an SLA job, and an executor that never fits.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Resource management at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'shared', 11, 'blue', bold=True) + t(60, 58, 'clusters', 7.4, 'ink2'),
    '1. Shared analytics clusters',
    'Dynamic allocation with min 0 lets dozens of notebooks share one cluster.',
    ['Idle session', '*release', 'Free cores']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'SLA', 12, 'green', bold=True) + t(60, 58, 'pipelines', 7.4, 'ink2'),
    '2. SLA pipelines',
    'Critical nightly jobs use static executors or a high minExecutors for predictable runtimes.',
    ['Nightly job', '*static', 'On time']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'K8s', 12, 'violet', bold=True) + t(60, 58, 'autoscale', 7.4, 'ink2'),
    '3. Kubernetes autoscaling',
    'Dynamic allocation with shuffle tracking adds executor pods; the node autoscaler adds nodes.',
    ['Backlog', '*more pods', 'More nodes']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'shape', 12, 'acc', bold=True) + t(60, 58, 'executors', 7.4, 'ink2'),
    '4. Executor shapes',
    'Platform teams publish standard small/medium/large executor shapes that fit their nodes.',
    ['Node size', '*shape', 'Fits']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'cost', 12, 'acc', bold=True) + t(60, 58, 'reports', 7.4, 'ink2'),
    '5. Cost reports',
    'Executor-hours per application from the history server show which jobs hold idle resources.',
    ['History server', '*executor-hours', 'Cost owner']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> architecture in <a href="../../01-introduction/03-spark-architecture/">1.3</a>, the lab cluster in <a href="../../01-introduction/05-install-pyspark-and-a-spark-cluster/">1.5</a>, memory in <a href="../04-memory-spill-and-oom/">8.4</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
