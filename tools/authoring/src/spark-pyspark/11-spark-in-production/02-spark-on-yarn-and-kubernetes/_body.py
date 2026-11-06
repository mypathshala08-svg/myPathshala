import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l112_yarn.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
U = capsec('l112_unhealthy.txt', '$ yarn application')

def yarnbox(x, y, cluster=True):
    o = opbox(x, y, 'ResourceManager', 'schedules', 'violet', 150, 30)
    o += box(x, y + 40, 330, 70, 'card') + t(x + 165, y + 54, 'NodeManager (one node)', 6.8, 'ink2', bold=True)
    o += opbox(x + 10, y + 62, 'container 01', 'AM + driver' if cluster else 'AM only', 'acc', 100, 34)
    o += opbox(x + 118, y + 62, 'container 02', 'executor', 'green', 100, 34)
    o += opbox(x + 226, y + 62, 'container 03', 'executor', 'green', 96, 34)
    return o

# ---------------------------------------------------------------- story
sc_ = (yarnbox(14, 18) + arrow(166, 33, 200, 33, 'ink3', 1) + t(250, 37, 'HDFS staging', 7, 'blue', bold=True) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured (YARN 3.4 + Spark 4.3)', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('client: driver host = yarn', 'blue'), ('cluster: driver in container 1', 'green'),
           ('5 files uploaded to HDFS', 'blue'), ('3 containers: AM + 2 exec', 'green'),
           ('disk 90% → node UNHEALTHY', 'red'), ('app stuck in ACCEPTED', 'red')])))
scene_svg = scene('On YARN, Spark asks the ResourceManager for containers: one for the ApplicationMaster and one per executor. We ran a PySpark job on a real single-node Hadoop 3.4 YARN cluster in client and cluster mode, and hit an unhealthy node that left the job waiting.', sc_,
                  'On YARN and Kubernetes, Spark is <tspan font-weight="700" class="s-acc">a guest</tspan> asking for containers.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“The job has been ACCEPTED for an hour”</h2>
  <div class="story">
    <p class="narration">TiffinGo moved its Spark jobs from a dedicated standalone cluster to the company’s shared Hadoop cluster. The first job sat in state ACCEPTED for an hour without running a single task. Next year the platform team plans to move again, to Kubernetes.</p>

{scene_svg}

K> Sir, standalone, YARN, Kubernetes… does my PySpark code change?
A> Almost not at all. What changes is who gives Spark its machines. On YARN, a <b>ResourceManager</b> hands out containers; on Kubernetes, the API server creates pods. Spark asks, and waits until it gets them.
R> So “ACCEPTED” means it is still waiting?
A> Yes, waiting for its first container. Today we run a real YARN cluster in Docker, submit in client and cluster mode, read the logs, and reproduce the hour-long wait. Kubernetes we cover from the official documentation. All outputs are real (Spark 4.3.0, Hadoop 3.4.1).
  </div>
</section>
'''

lv = '''
LEVELS> Cluster managers at three levels
L1> Renting rooms in a hotel
      <ul>
        <li>Standalone is your own house. YARN and Kubernetes are hotels: you ask reception (ResourceManager / API server) for rooms (containers / pods), and they decide who gets what.</li>
        <li>If housekeeping marks a floor unusable, reception has no rooms to give and your booking waits.</li>
      </ul>
L2> The commands
      <ul>
        <li>YARN: <code>spark-submit --master yarn --deploy-mode cluster --num-executors 2 --executor-memory 768m app.py</code>, with <code>HADOOP_CONF_DIR</code> set; logs via <code>yarn logs -applicationId …</code>.</li>
        <li>Kubernetes: <code>spark-submit --master k8s://https://&lt;api-server&gt; --deploy-mode cluster --conf spark.kubernetes.container.image=… local:///opt/app/app.py</code>.</li>
        <li>Inspect: <code>yarn application -list</code>, <code>yarn node -list -all</code>; <code>kubectl get pods</code>, <code>kubectl logs</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>Cluster mode uploaded the Spark libs, script, pyspark.zip, py4j and config to HDFS staging, then ran the driver in container 000001.</li>
        <li>The driver’s output was only visible through YARN logs.</li>
        <li>A node above 90% disk use became UNHEALTHY; the application stayed ACCEPTED with 0% progress.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Spark on YARN and Kubernetes</h2>
''' + def_block(
    'Spark supports several <b>cluster managers</b>. On <b>Hadoop YARN</b>, spark-submit uploads the application and Spark libraries to a staging directory (usually HDFS) and asks the ResourceManager to start an <b>ApplicationMaster</b> (AM) container; the AM then negotiates executor containers on NodeManagers. In cluster mode the driver runs inside the AM container; in client mode the AM only requests executors and the driver stays in the submitter. On <b>Kubernetes</b>, spark-submit creates a driver <b>pod</b> from a container image, and the driver creates executor pods through the Kubernetes API; dependencies are baked into the image or fetched from remote storage, configuration uses <code>spark.kubernetes.*</code> properties and pod templates, and dynamic allocation relies on shuffle tracking. In both, the cluster manager’s scheduler (queues, quotas, node health) decides when resources are granted.',
    'YARN and Kubernetes are shared resource managers. Spark asks them for containers (YARN) or pods (Kubernetes) for its driver and executors. Your Spark code stays the same; the submit command, packaging and log locations change. If the manager cannot grant resources, the job waits.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('ResourceManager', 'YARN’s cluster-wide scheduler.'),
    ('NodeManager', 'YARN agent on each node.'),
    ('Container', 'CPU + memory slice on a node.'),
    ('ApplicationMaster', 'Per-app coordinator on YARN.'),
    ('Staging dir', 'HDFS folder with uploaded files.'),
    ('Pod', 'Kubernetes unit: driver or executor.'),
    ('Container image', 'Spark + Python + your code.'),
    ('Queue / namespace', 'Resource limits per team.'),
]) + '''

  <h3>Standalone vs YARN vs Kubernetes</h3>
''' + table(['', 'Standalone', 'YARN', 'Kubernetes'], [
    ['Master URL', '<code>spark://host:7077</code>', '<code>yarn</code>', '<code>k8s://https://api:6443</code>'],
    ['Shared with other systems', 'No', 'Hadoop jobs (Hive, MapReduce)', 'Any containerised service'],
    ['Python cluster mode', 'No', 'Yes', 'Yes'],
    ['Dependencies', 'Ship or install on nodes', 'Uploaded to HDFS staging', 'Container image'],
    ['Driver logs (cluster mode)', 'n/a', '<code>yarn logs</code>', '<code>kubectl logs</code>'],
    ['Isolation / quotas', 'Basic', 'Queues', 'Namespaces, quotas'],
], minw=640) + lv + '''
EXAM> “How does Spark run on YARN?” spark-submit uploads jars, Python files and config to a staging dir, the ResourceManager starts an ApplicationMaster container, and the AM requests executor containers from NodeManagers. In cluster mode the driver runs in the AM; in client mode it runs in the submitter. On Kubernetes, the driver runs as a pod built from a Spark image and creates executor pods via the API server.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Kubernetes essentials (from the official docs)</h2>
  <p class="muted">Our sandbox could not run nested containers, so this part is not a lab run; the settings are standard Spark-on-Kubernetes configuration.</p>
''' + table(['Setting', 'Example', 'Purpose'], [
    ['Master', '<code>--master k8s://https://api.k8s.local:6443</code>', 'Kubernetes API server'],
    ['Image', '<code>spark.kubernetes.container.image=tiffingo/spark-py:4.3.0</code>', 'Spark + Python + deps'],
    ['Namespace / account', '<code>spark.kubernetes.namespace</code>, <code>…authenticate.driver.serviceAccountName</code>', 'Permissions to create pods'],
    ['App file', '<code>local:///opt/app/billing.py</code> or <code>s3a://…</code>', 'Inside the image or remote'],
    ['Pod templates', '<code>spark.kubernetes.driver.podTemplateFile</code>', 'Node selectors, tolerations, volumes'],
    ['Dynamic allocation', '<code>spark.dynamicAllocation.shuffleTracking.enabled=true</code>', 'No external shuffle service on K8s'],
], minw=640) + '''
WARN> “ACCEPTED” or “Pending” is not an error, so nothing fails and nothing alerts. On YARN it means the queue or nodes cannot give the first container (unhealthy nodes, queue limits, an executor bigger than any node); on Kubernetes, pods stuck in Pending usually mean quota, node selectors or image pull problems. Check <code>yarn node -list -all</code> / <code>kubectl describe pod</code> before resubmitting, and add a timeout alert for jobs that do not start.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>A real YARN cluster in one container</h2>
  <p>All outputs are real: a Docker image with Hadoop 3.4.1 (HDFS NameNode + DataNode, YARN ResourceManager + NodeManager with 4 GB and 4 vcores) and Spark 4.3.0/PySpark. The job prints where its driver runs, groups 5 million rows and counts registered executors. Submitted with 2 executors of 1 core and 768 MB.</p>
''' + stepper([
    ('Step 1 · Client mode',
     code('bash', 'spark-submit', 'export HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop\nspark-submit --master yarn --deploy-mode client --num-executors 2 \\\n  --executor-cores 1 --executor-memory 768m /jobs/m11/yarn_job.py', sec('== client mode', '== cluster mode')),
     'Spark found the ResourceManager through <code>HADOOP_CONF_DIR</code>, the application went <b>ACCEPTED → RUNNING</b> once the ApplicationMaster container started, and 2 executors registered. In client mode the driver ran in our shell: there is no YARN container ID for it, and its output appeared directly in the terminal.'),
    ('Step 2 · Cluster mode',
     code('bash', 'spark-submit', 'spark-submit --master yarn --deploy-mode cluster --num-executors 2 --executor-cores 1 \\\n  --executor-memory 768m --conf spark.yarn.appMasterEnv.PYSPARK_PYTHON=python3 /jobs/m11/yarn_job.py', sec('== cluster mode', '== driver stdout')),
     'Before asking for containers, the client <b>uploaded</b> five files to HDFS staging: the Spark jars zip, our script, <code>pyspark.zip</code>, <code>py4j</code> and the config zip. Every container on any node downloads them from there. The terminal only showed status reports, ending in <b>final status: SUCCEEDED</b>; the job’s own prints were elsewhere.'),
    ('Step 3 · Finding the driver’s output',
     code('bash', 'yarn', 'yarn logs -applicationId application_1793860298532_0003\nls $HADOOP_HOME/logs/userlogs/application_1793860298532_0003/', sec('== driver stdout')),
     'The driver ran inside <b>container 000001</b>, the ApplicationMaster container; 000002 and 000003 were the executors. With log aggregation on, <code>yarn logs</code> collects all of them after the job. Knowing this is half of debugging on YARN.'),
    ('Step 4 · Stuck in ACCEPTED',
     code('bash', 'yarn', 'yarn application -list\nyarn node -list -all', U),
     'Our first attempt waited for minutes. The only NodeManager was <b>UNHEALTHY</b>: its disk was over YARN’s 90% utilisation threshold, so the ResourceManager had zero usable nodes and could not even start the ApplicationMaster. No exception, just ACCEPTED at 0%. Freeing disk space (and, in our lab, raising <code>max-disk-utilization-per-disk-percentage</code>) made the node RUNNING and the job started.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('state: ACCEPTED -> RUNNING', G), ('deployMode: client', W), ('driver container: (none)', Y), ('executors registered: 2', G)], size=7.2),
    term([('Uploading __spark_libs__…zip', W), ('Uploading yarn_job.py, pyspark.zip', W), ('state: FINISHED', G), ('final status: SUCCEEDED', G)], size=7.2),
    term([('deployMode: cluster', W), ('driver container:', W), ('  container_…_01_000001', G), ('containers 000001-000003', W)], size=7.2),
    term([('ACCEPTED  UNDEFINED  0%', Y), ('yarn:34797  UNHEALTHY', RD), ('used space above 90.0%', RD)], size=7.4),
]
B1 = [
    t(180, 14, 'Client mode on YARN', 9.4, bold=True) + yarnbox(14, 30, cluster=False) + cap('Driver stays in the shell.', '', 'blue', y=144, h=30),
    t(180, 14, 'Staging, then containers', 9.4, bold=True) + flow([('upload', '5 files', 'blue'), ('HDFS', 'staging', 'violet'), ('AM', 'container 1', 'acc'), ('executors', '2, 3', 'green')], y=50, w=72, gap=14) + cap('Every node fetches from HDFS.', '', 'green', y=144, h=30),
    t(180, 14, 'Cluster mode: driver in the AM', 9.4, bold=True) + yarnbox(14, 30, cluster=True) + cap('Output via yarn logs.', '', 'green', y=144, h=30),
    t(180, 14, 'No healthy node, no container', 9.4, bold=True) + opbox(20, 46, 'ResourceManager', '0 usable nodes', 'violet', 150, 34) + opbox(190, 46, 'NodeManager', 'UNHEALTHY (disk)', 'red', 150, 34) + cap('App waits in ACCEPTED.', '', 'red', y=144, h=30),
]
see_caps = ['Client mode.', 'Cluster mode.', 'Driver logs.', 'Stuck in ACCEPTED.']
behind_caps = ['AM requests executors.', 'HDFS staging.', 'Driver inside the AM.', 'Node health.']
two = anim_two('Spark on YARN', 'Asking for containers', 'Real lab outputs', 'What YARN does', see, B1, see_caps, behind_caps)

e1 = (t(180, 22, 'Job in ACCEPTED for 1 hour', 9.4, bold=True) + t(180, 56, 'no error anywhere', 8.4, 'ink2') + cap('Silent wait.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'yarn node -list -all', 9.4, bold=True) + t(180, 56, 'nodes UNHEALTHY: disk > 90%', 8.4, 'ink2') + cap('Our lab exactly.', '', 'red', y=150, h=34))
e3 = (t(180, 22, 'Or: queue at its limit', 9.4, bold=True) + t(180, 56, 'yarn queue -status analytics', 8.4, 'ink', mono=True) + cap('Other apps use it.', '', 'amber', y=150, h=34))
e4 = (t(180, 22, 'Fix the cause', 9.4, bold=True) + t(180, 56, 'clean disks / right queue / smaller AM', 8.2, 'ink2') + cap('Then it starts.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Alert: not RUNNING in 10 min', 9.4, 'acc', bold=True) + t(180, 56, 'scheduler-level timeout', 8.4, 'ink2') + cap('Catch it next time.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'The hour in ACCEPTED',
              'Diagnosing jobs that never start. (Typical; reproduced in our lab.)',
              'ACCEPTED', 'A job stuck in ACCEPTED is waiting for its ApplicationMaster container; check nodes and queues', [e1, e2, e3, e4, e5],
              ['Waiting.', 'Nodes.', 'Queue.', 'Fix.', 'Alert.'],
              hid='scenario-accepted')
b1 = (t(180, 22, 'Cluster-mode job failed', 9.4, bold=True) + t(180, 56, 'terminal: final status FAILED', 8.4, 'ink2') + cap('No Python traceback shown.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Driver ran in container 1', 9.4, bold=True) + t(180, 56, 'its stderr lives there', 8.4, 'ink2') + cap('Not on your screen.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'yarn logs -applicationId …', 9.4, bold=True) + t(180, 56, '-log_files stderr', 8.4, 'ink', mono=True) + cap('Traceback found.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Or the Spark history server', 9.4, bold=True) + t(180, 56, 'event logs on HDFS', 8.4, 'ink2') + cap('Stages and tasks.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Runbook it', 9.4, 'acc', bold=True) + t(180, 56, 'where every log lives', 8.4, 'ink2') + cap('Faster on-call.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Where is my traceback?',
              'Logs in cluster mode. (Typical; layout from our lab.)',
              'Logs', 'In cluster mode the driver’s output is in the AM container logs, not your terminal', [b1, b2, b3, b4, b5],
              ['Failed.', 'Container 1.', 'yarn logs.', 'History.', 'Runbook.'],
              hid='scenario-logs')
u1 = (t(180, 22, 'Move from YARN to Kubernetes', 9.4, bold=True) + t(180, 56, 'same PySpark code', 8.4, 'ink2') + cap('Platform change.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Build an image', 9.4, bold=True) + t(180, 56, 'spark + python + deps + app', 8.4, 'ink2') + cap('No HDFS staging.', '', 'green', y=150, h=34))
u3 = (t(180, 22, 'Service account + namespace', 9.4, bold=True) + t(180, 56, 'driver creates executor pods', 8.4, 'ink2') + cap('RBAC needed.', '', 'amber', y=150, h=34))
u4 = (t(180, 22, 'Shuffle tracking on', 9.4, bold=True) + t(180, 56, 'for dynamic allocation', 8.4, 'ink2') + cap('No shuffle service.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Or Spark Operator', 9.4, 'acc', bold=True) + t(180, 56, 'SparkApplication YAML', 8.4, 'ink2') + cap('GitOps-friendly.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'From YARN to Kubernetes',
              'What changes when moving platforms. (Typical; from the Spark docs.)',
              'Kubernetes', 'On Kubernetes, images replace staging, pods replace containers, and RBAC matters', [u1, u2, u3, u4, u5],
              ['Move.', 'Image.', 'RBAC.', 'Shuffle.', 'Operator.'],
              hid='scenario-k8s')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Asking for containers</h2>
  <p>Left: real outputs. Right: what YARN does.</p>
''' + two + '''
  <p>Three live scenarios follow: a job stuck in ACCEPTED, finding the driver’s traceback, and moving to Kubernetes.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Cluster managers at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'YARN', 12, 'blue', bold=True) + t(60, 58, 'Hadoop', 7.4, 'ink2'),
    '1. Hadoop data platforms',
    'Banks and telecoms run Spark next to Hive on YARN queues per team.',
    ['Team queue', '*YARN', 'Containers']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'EMR', 12, 'green', bold=True) + t(60, 58, 'Dataproc', 7.4, 'ink2'),
    '2. Managed Hadoop',
    'AWS EMR and Google Dataproc clusters run Spark on YARN by default.',
    ['Cloud cluster', '*YARN', 'Spark jobs']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'K8s', 12, 'violet', bold=True) + t(60, 58, 'pods', 7.4, 'ink2'),
    '3. Kubernetes platforms',
    'Spark Operator or spark-submit run jobs as pods next to microservices.',
    ['SparkApplication', '*operator', 'Pods']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'spot', 12, 'acc', bold=True) + t(60, 58, 'nodes', 7.4, 'ink2'),
    '4. Cheap executors',
    'Executors on spot/preemptible nodes, driver on on-demand nodes via node selectors.',
    ['Driver', '*on-demand', 'Executors on spot']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'logs', 12, 'acc', bold=True) + t(60, 58, 'on-call', 7.4, 'ink2'),
    '5. On-call debugging',
    'Runbooks map each failure to yarn logs, kubectl logs or the history server.',
    ['Alert', '*right log', 'Root cause']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> spark-submit and deploy modes in <a href="../01-spark-submit-and-deploy-modes/">11.1</a>, executors and resources in <a href="../../08-performance-tuning/05-resources-and-dynamic-allocation/">8.5</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
