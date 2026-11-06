import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l111_submit.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)

def modes(x, y, cluster=False):
    o = box(x, y, 110, 70, 'card') + t(x + 55, y + 14, 'your laptop / edge node', 6.8, 'ink2', bold=True)
    o += opbox(x + 10, y + 24, 'spark-submit', 'client', 'blue', 90, 32)
    o += box(x + 130, y, 210, 70, 'card') + t(x + 235, y + 14, 'cluster', 6.8, 'ink2', bold=True)
    if cluster:
        o += opbox(x + 140, y + 24, 'driver', 'in a container', 'acc', 60, 32)
    else:
        o += opbox(x + 10, y + 46, 'driver', 'here', 'acc', 90, 20)
    for k in range(2):
        o += opbox(x + 210 + k * 64, y + 24, f'exec {k + 1}', 'tasks', 'green', 58, 32)
    return o

# ---------------------------------------------------------------- story
sc_ = (t(14, 22, 'client mode', 7.6, 'ink2', anchor='start', bold=True) + modes(14, 28) + t(14, 112, 'cluster mode: the driver also runs in the cluster', 7.2, 'ink2', anchor='start') +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured (standalone cluster)', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('no --py-files: ModuleNotFound', 'red'), ('--py-files zip: 105.0 210.0', 'green'),
           ('code 12 > --conf 100 > file 50', 'blue'), ('--conf 1500m > file 1g', 'blue'),
           ('python cluster mode on', 'red'), ('standalone: not supported', 'red')])))
scene_svg = scene('spark-submit packages an application and launches its driver and executors on a cluster. We submitted a PySpark job to a two-worker standalone cluster with and without its helper module, with settings in three places, and in cluster deploy mode.', sc_,
                  'Your laptop code runs <tspan font-weight="700" class="s-acc">somewhere else</tspan>; ship everything it needs.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“It works on my machine”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s billing job ran fine in a notebook. Scheduled with <code>spark-submit</code> on the cluster, it failed with <code>ModuleNotFoundError: tiffin_utils</code>. After a fix it ran, but with 50 shuffle partitions although the team had configured 100.</p>

{scene_svg}

K> Sir, the module is right there next to the script. Why can’t Spark find it?
A> Your script runs in the <b>driver</b>; your functions run in <b>executors</b>, on other machines. They only have what you ship with <code>--py-files</code>, or what is installed there.
R> And the 50 partitions?
A> Settings can come from four places, and they have an order. Today we submit a real job to our standalone cluster: missing module, shipping it, three layers of configuration, and deploy modes. All outputs are real (Spark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> spark-submit at three levels
L1> Sending a cook to another kitchen
      <ul>
        <li>The head chef (driver) plans; line cooks (executors) cook. If the recipe needs your secret masala, you must pack it in their bag (<code>--py-files</code>).</li>
        <li>Client mode: the head chef stays at your desk. Cluster mode: the head chef moves into the restaurant too.</li>
      </ul>
L2> The command
      <ul>
        <li><code>spark-submit --master … --deploy-mode client|cluster --py-files deps.zip --conf k=v --properties-file f.conf app.py args</code>.</li>
        <li>Resources: <code>--driver-memory</code>, <code>--executor-memory</code>, <code>--executor-cores</code>, <code>--num-executors</code> (YARN/K8s), <code>--total-executor-cores</code> (standalone).</li>
        <li>Dependencies: <code>--py-files</code>, <code>--jars</code>, <code>--packages</code>, <code>--archives</code> (e.g. a packed virtualenv).</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>Without <code>--py-files</code> the executors failed with <code>ModuleNotFoundError</code>; with the zip they computed GST.</li>
        <li>A value set in code (12) beat <code>--conf</code> (100), which beat the properties file (50).</li>
        <li>Python cluster mode on a standalone cluster is refused; use YARN or Kubernetes for that.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>spark-submit and deploy modes</h2>
''' + def_block(
    '<code>spark-submit</code> is the launcher for Spark applications. It takes the application file and its arguments, a <b>master URL</b> (<code>local[*]</code>, <code>spark://host:7077</code>, <code>yarn</code>, <code>k8s://…</code>), resource options and dependencies, builds the configuration and starts the driver. The <b>deploy mode</b> decides where the driver runs: in <b>client</b> mode it runs in the submitting process, which must stay alive and reachable from the executors; in <b>cluster</b> mode the cluster manager starts the driver on a cluster node and the submitter can exit. Executors only see code and libraries shipped with the application (<code>--py-files</code>, <code>--jars</code>, <code>--packages</code>, <code>--archives</code>) or pre-installed on the nodes. Configuration precedence is: properties set in the application code (<code>SparkConf</code>/<code>builder.config</code>), then <code>spark-submit</code> flags and <code>--conf</code>, then the properties file (<code>spark-defaults.conf</code>).',
    'spark-submit starts your application on a cluster. In client mode the driver runs where you typed the command; in cluster mode it runs inside the cluster. Executors are separate processes on other machines, so you must ship your Python modules and libraries to them. Settings written in code win over command-line settings, which win over the defaults file.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Master URL', 'Which cluster manager to use.'),
    ('Deploy mode', 'client or cluster: where the driver runs.'),
    ('--py-files', 'Ship .py/.zip/.egg to executors.'),
    ('--packages', 'Maven coordinates, downloaded.'),
    ('--archives', 'e.g. a packed virtualenv/conda env.'),
    ('--properties-file', 'Defaults like spark-defaults.conf.'),
    ('--conf k=v', 'Any Spark property.'),
    ('Edge node', 'Machine you submit from.'),
]) + '''

  <h3>Client vs cluster mode</h3>
''' + table(['', 'client', 'cluster'], [
    ['Driver runs', 'In the spark-submit process', 'On a cluster node (YARN AM / K8s pod)'],
    ['Submitter must stay up', 'Yes', 'No'],
    ['Driver output', 'Your terminal', 'Cluster logs (<code>yarn logs</code>, pod logs)'],
    ['Good for', 'Notebooks, shells, debugging', 'Scheduled production jobs'],
    ['Python on standalone', 'Supported', 'Not supported (lab error)'],
], minw=560) + lv + '''
EXAM> “Client vs cluster deploy mode?” In client mode the driver runs where spark-submit runs, so logs appear locally and the machine must stay connected to the executors; it suits interactive work. In cluster mode the driver runs inside the cluster, so the job survives the submitter disconnecting and is preferred for production on YARN and Kubernetes. Python applications cannot use cluster mode on a standalone cluster.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Shipping Python dependencies</h2>
''' + table(['Need', 'Option', 'Notes'], [
    ['Your own modules', '<code>--py-files deps.zip</code>', 'Added to the executors’ Python path'],
    ['Pure-Python libraries', '<code>--py-files</code> with a zipped site-packages', 'Only if no compiled code'],
    ['Libraries with C extensions', '<code>--archives env.tar.gz#env</code> + <code>PYSPARK_PYTHON=./env/bin/python</code>', 'conda-pack / venv-pack'],
    ['Container platforms', 'Bake into the image', 'Kubernetes, Databricks, EMR on EKS'],
    ['JVM libraries', '<code>--packages group:artifact:version</code> or <code>--jars</code>', 'e.g. Kafka, Delta'],
], minw=620) + '''
WARN> Settings in code win. Hard-coding <code>spark.sql.shuffle.partitions</code> or memory in <code>SparkSession.builder.config(...)</code> means operators cannot tune the job with <code>--conf</code> later (our 100 was silently ignored). Put environment-specific settings on the command line or in the properties file, keep only true requirements in code, and print the effective configuration at start-up.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Submitting to a real cluster</h2>
  <p>All outputs are real: Spark 4.3.0 standalone cluster in Docker (1 master, 2 workers). The job sets <code>spark.sql.shuffle.partitions=12</code> in code, prints its effective settings and runs a UDF that imports <code>tiffin_utils.gst</code> on the executors.</p>
''' + stepper([
    ('Step 1 · The missing module',
     code('bash', 'spark-submit', 'spark-submit --master spark://spark-master:7077 /jobs/m11/submit_job.py', sec('### 1)', '### 2)')),
     'The driver started fine (the import is inside the function). The <b>executors</b> failed when they ran the task: <code>tiffin_utils</code> exists only next to the script on the submitting machine. Client mode: the driver ran on <code>spark-master</code>, where we typed the command.'),
    ('Step 2 · Shipping it with --py-files',
     code('bash', 'spark-submit', 'cd pkg && python -m zipfile -c ../tiffin_utils.zip tiffin_utils\nspark-submit --master spark://spark-master:7077 --py-files /jobs/m11/tiffin_utils.zip /jobs/m11/submit_job.py', sec('### 2)', '### 3)')),
     'The zip was distributed with the application and put on every executor’s Python path: <b>100 → 105.0</b>, 200 → 210.0. The printed settings show what was really used: 12 shuffle partitions (from code), no executor memory and no event log (not set anywhere).'),
    ('Step 3 · Three places for settings',
     code('bash', 'spark-submit', '# defaults.conf: spark.executor.memory 1g, spark.sql.shuffle.partitions 50, spark.eventLog.enabled true\nspark-submit … --properties-file defaults.conf \\\n  --conf spark.sql.shuffle.partitions=100 --conf spark.executor.memory=1500m \\\n  --py-files tiffin_utils.zip submit_job.py', sec('### 3)', '### 4)')),
     'Precedence in action. <code>spark.eventLog.enabled</code> came from the file (only set there). <code>spark.executor.memory</code>: <code>--conf</code> 1500m beat the file’s 1g. <code>spark.sql.shuffle.partitions</code>: the code’s <b>12</b> beat both 100 and 50. That is exactly the story’s surprise.'),
    ('Step 4 · Cluster mode for Python on standalone',
     code('bash', 'spark-submit', 'spark-submit --master spark://spark-master:7077 --deploy-mode cluster /jobs/m11/submit_job.py', sec('### 4)')),
     'Rejected immediately. Standalone cluster mode works for JVM applications only. For Python jobs that must outlive the submitter, use YARN or Kubernetes cluster mode (next lesson), or run client mode from a durable scheduler host.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('deployMode: client', W), ('driver host: spark-master', W), ("ModuleNotFoundError: 'tiffin_utils'", RD)], size=7.2),
    term([('--py-files tiffin_utils.zip', W), ('with GST: (100, 105.0) (200, 210.0)', G)], size=7.2),
    term([('shuffle.partitions = 12  (code)', G), ('executor.memory = 1500m (--conf)', G), ('eventLog.enabled = true (file)', G)], size=7.2),
    term([('--deploy-mode cluster (Python)', W), ('Cluster deploy mode is currently', RD), ('not supported for python on standalone', RD)], size=7.0),
]
B1 = [
    t(180, 14, 'Executors run your functions', 9.4, bold=True) + opbox(20, 46, 'driver', 'has the script', 'acc', 120, 34) + arrow(142, 63, 196, 63, 'ink3', 1.1) + opbox(200, 46, 'executor', 'no tiffin_utils', 'red', 140, 34) + cap('Only shipped code is there.', '', 'red', y=144, h=30),
    t(180, 14, '--py-files ships it', 9.4, bold=True) + flow([('zip', 'tiffin_utils', 'violet'), ('submit', 'upload', 'blue'), ('executors', 'sys.path', 'green')], y=50, w=96, gap=16) + cap('Then the import works.', '', 'green', y=144, h=30),
    t(180, 14, 'Who wins?', 9.4, bold=True) + ''.join(opbox(30 + k * 104, 50, n, v, tone, 96, 34) for k, (n, v, tone) in enumerate([('code', '12 ✔', 'green'), ('--conf', '100', 'blue'), ('file', '50', 'card')])) + cap('code > --conf > properties file', '', 'blue', y=144, h=30),
    t(180, 14, 'Where the driver lives', 9.4, bold=True) + modes(10, 40, cluster=True) + cap('Cluster mode: YARN or K8s for Python.', '', 'amber', y=144, h=30),
]
see_caps = ['Missing module.', '--py-files.', 'Configuration precedence.', 'Cluster mode.']
behind_caps = ['Driver vs executors.', 'Shipping dependencies.', 'Settings precedence.', 'Deploy modes.']
two = anim_two('spark-submit', 'From script to cluster', 'Real lab outputs', 'What happens', see, B1, see_caps, behind_caps)

e1 = (t(180, 22, 'Notebook job → production', 9.4, bold=True) + t(180, 56, 'helpers in utils/ folder', 8.4, 'ink2') + cap('Scheduled with spark-submit.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Executors: ModuleNotFound', 9.4, bold=True) + t(180, 56, 'driver was fine', 8.4, 'ink2') + cap('Classic first failure.', '', 'red', y=150, h=34))
e3 = (t(180, 22, 'Build a wheel/zip in CI', 9.4, bold=True) + t(180, 56, 'tiffin_utils-1.4.zip', 8.4, 'ink', mono=True) + cap('Versioned artifact.', '', 'green', y=150, h=34))
e4 = (t(180, 22, '--py-files in the job spec', 9.4, bold=True) + t(180, 56, 'same artifact everywhere', 8.4, 'ink2') + cap('Reproducible.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'C libraries? pack an env', 9.4, 'acc', bold=True) + t(180, 56, '--archives env.tar.gz#env', 8.4, 'ink', mono=True) + cap('Or a container image.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'From notebook to scheduled job',
              'Packaging Python dependencies. (Typical; error from our lab.)',
              'Dependencies', 'Ship your modules and libraries with the job: --py-files, --archives or an image', [e1, e2, e3, e4, e5],
              ['Notebook.', 'Fails.', 'Package.', 'Ship.', 'Env.'],
              hid='scenario-deps')
b1 = (t(180, 22, 'Ops raise partitions to 400', 9.4, bold=True) + t(180, 56, '--conf on the scheduler', 8.4, 'ink2') + cap('Job still slow.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Spark UI → Environment', 9.4, bold=True) + t(180, 56, 'shuffle.partitions = 12', 8.4, 'ink', mono=True) + cap('Hard-coded in the script.', '', 'red', y=150, h=34))
b3 = (t(180, 22, 'Remove it from code', 9.4, bold=True) + t(180, 56, 'keep only true requirements', 8.4, 'ink2') + cap('Config outside code.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Per-env properties files', 9.4, bold=True) + t(180, 56, 'dev.conf / prod.conf', 8.4, 'ink2') + cap('Reviewed like code.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Print effective config', 9.4, 'acc', bold=True) + t(180, 56, 'at job start', 8.4, 'ink2') + cap('No more surprises.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'The setting that never applied',
              'Configuration precedence. (Typical; precedence from our lab.)',
              'Precedence', 'Settings in code override --conf and properties files; keep environment settings out of code', [b1, b2, b3, b4, b5],
              ['--conf.', 'Hard-coded.', 'Remove.', 'Files.', 'Print.'],
              hid='scenario-precedence')
u1 = (t(180, 22, 'Laptop submits nightly job', 9.4, bold=True) + t(180, 56, 'client mode over VPN', 8.4, 'ink2') + cap('Driver on the laptop.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Laptop sleeps at 2 a.m.', 9.4, bold=True) + t(180, 56, 'driver gone → job dies', 8.4, 'ink2') + cap('Executors lost their driver.', '', 'red', y=150, h=34))
u3 = (t(180, 22, 'Cluster mode on YARN/K8s', 9.4, bold=True) + t(180, 56, 'driver runs in the cluster', 8.4, 'ink2') + cap('Submitter can leave.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Submit from a scheduler', 9.4, bold=True) + t(180, 56, 'Airflow, not a laptop', 8.4, 'ink2') + cap('Durable.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Logs via the cluster', 9.4, 'acc', bold=True) + t(180, 56, 'yarn logs / kubectl logs', 8.4, 'ink', mono=True) + cap('Know where to look.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'The laptop that went to sleep',
              'Client vs cluster mode in production. (Typical.)',
              'Deploy mode', 'Production jobs use cluster mode or a durable submitter so the driver survives', [u1, u2, u3, u4, u5],
              ['Laptop.', 'Dies.', 'Cluster.', 'Scheduler.', 'Logs.'],
              hid='scenario-mode')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>From script to cluster</h2>
  <p>Left: real outputs. Right: what spark-submit does.</p>
''' + two + '''
  <p>Three live scenarios follow: packaging dependencies, a setting that never applied, and choosing a deploy mode.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>spark-submit at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'Airflow', 11, 'blue', bold=True) + t(60, 58, 'operator', 7.4, 'ink2'),
    '1. Scheduled pipelines',
    'Airflow’s SparkSubmitOperator runs the same spark-submit command every night.',
    ['DAG', '*spark-submit', 'Job']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'CI', 12, 'green', bold=True) + t(60, 58, 'artifacts', 7.4, 'ink2'),
    '2. CI-built artifacts',
    'CI builds a zip/wheel of the project and a pinned environment for every release.',
    ['Git tag', '*build zip', '--py-files']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'conf', 12, 'violet', bold=True) + t(60, 58, 'per env', 7.4, 'ink2'),
    '3. Environment configs',
    'dev, staging and prod properties files hold memory, partitions and endpoints.',
    ['prod.conf', '*--properties-file', 'Same code']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'pkgs', 12, 'acc', bold=True) + t(60, 58, 'connectors', 7.4, 'ink2'),
    '4. Connectors',
    '--packages pulls Kafka, Delta or JDBC connectors at submit time.',
    ['Maven coords', '*--packages', 'Classpath']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'shell', 12, 'acc', bold=True) + t(60, 58, 'client', 7.4, 'ink2'),
    '5. Interactive analysis',
    'pyspark shells and notebooks run in client mode against shared clusters.',
    ['Notebook', '*client mode', 'Results here']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> drivers and executors in <a href="../../01-introduction/03-spark-architecture/">1.3</a>, the lab cluster in <a href="../../01-introduction/05-install-pyspark-and-a-spark-cluster/">1.5</a>, resources in <a href="../../08-performance-tuning/05-resources-and-dynamic-allocation/">8.5</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
