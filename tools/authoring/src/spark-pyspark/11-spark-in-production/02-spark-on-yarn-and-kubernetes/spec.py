import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='11-spark-in-production', lesson='02-spark-on-yarn-and-kubernetes', n='11.2',
    module_label='Module 11 · Spark in production',
    title='Spark on YARN and Kubernetes',
    desc='Spark on YARN with a real Hadoop 3.4.1 cluster and Spark 4.3.0: client vs cluster mode, the five files uploaded to HDFS staging, the driver running in ApplicationMaster container 000001 with output only in yarn logs, and a job stuck in ACCEPTED because the only NodeManager was UNHEALTHY (disk over 90%), plus Spark-on-Kubernetes settings (images, service accounts, pod templates, shuffle tracking) from the official documentation.',
    og_desc='Why a Spark job sits in ACCEPTED for an hour: Spark on a real YARN cluster in client and cluster mode, and what changes on Kubernetes.',
    minutes=28, level='Intermediate → Advanced',
    lead='On shared platforms Spark asks a cluster manager for resources. This lesson runs PySpark on a <b>real YARN cluster</b> in client and cluster mode, follows the HDFS staging and containers, finds the driver’s output, reproduces a job <b>stuck in ACCEPTED</b>, and maps it all to <b>Kubernetes</b>. <b>All YARN outputs are real</b> (Spark 4.3.0, Hadoop 3.4.1).',
    chips=['Spark 4.3.0 on YARN', 'Hadoop 3.4.1', 'Kubernetes settings', 'Runs in your browser (Python)'],
)

MAIN = '''# Will YARN start this application? (simplified scheduler check)
nodes = [{"name": "yarn:34797", "healthy": False, "free_mb": 4096, "free_vcores": 4}]
am_mb, exec_mb, overhead = 768, 768, 384
executors = 2

usable = [n for n in nodes if n["healthy"]]
need_am = am_mb + overhead
if not usable:
    print("state: ACCEPTED (no healthy node for the ApplicationMaster)")
elif max(n["free_mb"] for n in usable) < need_am:
    print("state: ACCEPTED (AM container does not fit)")
else:
    free = sum(n["free_mb"] for n in usable) - need_am
    got = min(executors, free // (exec_mb + overhead))
    print(f"state: RUNNING with {got} executor(s)")
'''
RUN = dict(
    heading='Run the code: will YARN start it?',
    intro='<p>A simplified version of why our job waited. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('usable = [n for n in nodes if n["healthy"]]', 'UNHEALTHY nodes (e.g. disk over 90%) get no containers at all.'),
        ('need_am = am_mb + overhead', 'Each container needs its memory plus overhead; YARN rounds up to its allocation increments.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then set <code>"healthy": True</code>.', code=None),
        dict(label='2 · Predict first: containers', hint='<b>Predict first:</b> cluster mode with 2 executors needs how many containers?',
             code='''executors = 2
print(1 + executors, "containers (AM with driver + executors)")
'''),
        dict(label='3 · Disk check', hint='Is a node above YARN’s 90% threshold healthy?',
             code='''used, total = 228, 252
pct = used / total * 100
print(round(pct, 1), "% ->", "UNHEALTHY" if pct > 90 else "healthy")
'''),
        dict(label='4 · K8s command', hint='Build a Kubernetes spark-submit.',
             code='''api, image = "https://api.k8s.local:6443", "tiffingo/spark-py:4.3.0"
print(f"spark-submit --master k8s://{api} --deploy-mode cluster "
      f"--conf spark.kubernetes.container.image={image} local:///opt/app/billing.py")
'''),
        dict(label='5 · Spot the error', hint='An executor larger than any node.', expect='error',
             code='''node_mb, executor_mb, overhead_mb = 4096, 4096, 410
assert executor_mb + overhead_mb <= node_mb, "container never fits: application waits forever"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: YARN commands',
    intro='<p>Inside the lab’s Hadoop + Spark container. <b>Outputs are real</b> (Hadoop 3.4.1, Spark 4.3.0).</p>',
    items=[
        dict(title='1 · Node health', cmd='yarn node -list -all', file='bash',
             output='      yarn:45775	        RUNNING	        yarn:8042	                           0', note='After freeing disk.'),
        dict(title='2 · Submit in cluster mode', cmd='spark-submit --master yarn --deploy-mode cluster --num-executors 2 --executor-memory 768m /jobs/m11/yarn_job.py', file='bash',
             output='Client: Application report for application_1793860298532_0003 (state: FINISHED)\n\t final status: SUCCEEDED', note='Driver output is in YARN logs.'),
        dict(title='3 · Driver output', cmd='yarn logs -applicationId application_1793860298532_0003 | grep driver', file='bash',
             output='driver host: yarn | driver container: container_1793860298532_0003_01_000001', note='The AM container.'),
    ],
)

TRACE = dict(
    heading='Who runs where in cluster mode',
    intro='<p>Follow container assignment for a YARN cluster-mode job.</p>',
    code='''containers = []
containers.append("000001: ApplicationMaster + driver")
for i in range(2):
    containers.append(f"00000{i + 2}: executor {i + 1}")
for c in containers:
    print(c)
''',
    notes={2: 'AM :: First container; driver lives here in cluster mode.', 4: 'Executors :: Requested by the AM.'},
)

WORKED_INTRO = 'Three platform decisions at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='YARN · submit', title='Submit to YARN',
         problem='<p>Run billing.py on the Hadoop cluster in the finance queue.</p>',
         inp='queue finance',
         approach=['--master yarn.', '--deploy-mode cluster.', '--queue finance.'],
         code='''print("spark-submit --master yarn --deploy-mode cluster --queue finance --num-executors 10 billing.py")
''', notes={1: 'HADOOP_CONF_DIR :: Must point to the cluster config.'},
         tryit='Step 2.'),
    dict(level='i', tag='YARN · debug', title='Job never starts',
         problem='<p>Application state ACCEPTED for 30 minutes.</p>',
         inp='yarn CLI',
         approach=['yarn node -list -all: healthy nodes?', 'Queue capacity used?', 'AM fits on a node?'],
         code='''checks = ["yarn node -list -all", "yarn queue -status finance", "yarn application -status <app>"]
print("\\n".join(checks))
''', notes={1: 'Silent :: ACCEPTED is not an error state.'},
         tryit='Step 4.'),
    dict(level='a', tag='K8s · design', title='Package for Kubernetes',
         problem='<p>Move the job to Kubernetes.</p>',
         inp='Python deps + app',
         approach=['Image FROM a Spark base with Python.', 'pip install deps; COPY app.', 'Service account + namespace.'],
         code='''dockerfile = ["FROM apache/spark-py:4.x", "RUN pip install -r requirements.txt", "COPY app/ /opt/app/"]
print("\\n".join(dockerfile))
''', notes={1: 'Image :: Replaces --py-files and HDFS staging.'},
         tryit='Scenario 3.'),
]

QUIZ = mix([
    dict(q='Beginner: Master URL for YARN?', options=['spark://yarn', 'yarn', 'k8s://yarn', 'local'], answer=1,
         why='Plus HADOOP_CONF_DIR.'),
    dict(q='Beginner: YARN’s cluster scheduler is the…', options=['NameNode', 'ResourceManager', 'DataNode', 'Driver'], answer=1,
         why='NodeManagers run containers.'),
    dict(q='Beginner: On Kubernetes, executors run as…', options=['Containers on YARN', 'Pods', 'Threads', 'Lambdas'], answer=1,
         why='Created by the driver pod.'),
    dict(q='Intermediate: In YARN cluster mode the driver runs in…', options=['The submitter', 'The ApplicationMaster container', 'The NameNode', 'An executor'], answer=1,
         why='Container 000001.'),
    dict(q='Intermediate: Where are app files staged on YARN?', options=['Driver memory', 'HDFS staging directory', 'Kafka', 'Docker image'], answer=1,
         why='.sparkStaging/<app>.'),
    dict(q='Intermediate: Driver output in cluster mode?', options=['Your terminal', 'yarn logs -applicationId', 'Nowhere', 'HDFS root'], answer=1,
         why='AM container logs.'),
    dict(q='Advanced: App stuck in ACCEPTED, nodes UNHEALTHY. Cause?', options=['Python bug', 'No usable node for the AM', 'Too many partitions', 'Kafka lag'], answer=1,
         why='Disk > 90% in our lab.'),
    dict(q='Advanced: Dynamic allocation on Kubernetes needs…', options=['External shuffle service', 'Shuffle tracking', 'HDFS', 'Nothing'], answer=1,
         why='No shuffle service by default.'),
])

REVISION = [
    'YARN: RM schedules; AM container negotiates executor containers.',
    'Cluster mode: driver in the AM container; client mode: in the submitter.',
    'spark-submit uploads libs, script, pyspark.zip, py4j, conf to HDFS staging.',
    'Driver output in cluster mode: yarn logs (container 000001).',
    'ACCEPTED forever: unhealthy nodes, full queues, or containers that do not fit.',
    'Kubernetes: image, namespace + service account, pods, pod templates.',
    'K8s dynamic allocation uses shuffle tracking.',
]
FAQ = [
    ('Do I need Hadoop installed to submit to YARN?', 'You need the cluster’s Hadoop configuration (HADOOP_CONF_DIR) and Spark built with YARN support; pip PySpark includes it.'),
    ('What is the Spark Operator?', 'A Kubernetes operator that manages Spark jobs declared as SparkApplication resources, handling submission, restarts and monitoring.'),
    ('Can I use --py-files on Kubernetes?', 'Yes, with remote URLs or files in the image, but baking dependencies into the image is the common practice.'),
    ('Is YARN still relevant?', 'Yes, many on-premise and EMR/Dataproc deployments use it, while new platforms often choose Kubernetes.'),
    ('Why did the lab not run Kubernetes?', 'Our sandbox cannot run containers inside containers, which local Kubernetes (kind/minikube) needs; the YARN parts are real runs.'),
]

PRACTICE_INTRO = 'Programs about containers and scheduling.'
PROBLEMS = [
    dict(level='easy', title='Containers', stmt='Containers for 10 executors in cluster mode.', inp='10',
         code='''print(10 + 1)
''', explain='Plus the AM.'),
    dict(level='easy', title='Container size', stmt='Executor container with 10% overhead (min 384 MB).', inp='768 MB',
         code='''print(768 + max(384, int(768 * 0.1)))
''', explain='1,152 MB.'),
    dict(level='easy', title='Fits?', stmt='Do 3 such containers fit in 4,096 MB?', inp='3 × 1152',
         code='''print(3 * 1152 <= 4096)
''', explain='Yes.'),
    dict(level='medium', title='Executors per node', stmt='Executors that fit on a 64 GB node at 9 GB each.', inp='64, 9',
         code='''print(64 // 9)
''', explain='7.'),
    dict(level='medium', title='Health', stmt='Mark nodes unhealthy above 90% disk.', inp='usage',
         code='''u = {"n1": 72, "n2": 93, "n3": 88}
print([n for n, p in u.items() if p > 90])
''', explain='n2.'),
    dict(level='medium', title='Staged files', stmt='Files staged for a PySpark cluster-mode job.', inp='lab',
         code='''print(["__spark_libs__.zip", "app.py", "pyspark.zip", "py4j-src.zip", "__spark_conf__.zip"])
''', explain='5, as in the lab.'),
    dict(level='business', title='Waiting cost', stmt='SLA minutes lost if a job waits 60 min in ACCEPTED weekly.', inp='60 × 52',
         code='''print(60 * 52, "minutes per year")
''', explain='Alert on start time.'),
    dict(level='business', title='Spot savings', stmt='Saving with spot executors at 70% discount on ₹1,00,000/month executor cost.', inp='70%',
         code='''print("₹", int(100000 * 0.7))
''', explain='Keep the driver on-demand.'),
]

SCN_INTRO = 'Platform questions test operational experience.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“How does Spark run on YARN?”',
        'Explain the flow.',
        'components?',
        '<p>spark-submit uploads files to HDFS staging and asks the ResourceManager for an ApplicationMaster container. The AM requests executor containers from NodeManagers. In cluster mode the driver runs inside the AM container; in client mode it runs in the submitter.</p>', 'Confusing NameNode with ResourceManager.') +
    scn('Data engineering', 'Mid-level', 'Stuck in ACCEPTED',
        'A job is in ACCEPTED for 40 minutes.',
        'what do you check?',
        '''<ul>
          <li>yarn node -list -all for UNHEALTHY/LOST nodes (disk, memory).</li>
          <li>Queue capacity and limits.</li>
          <li>Whether the AM/executor size fits any node.</li>
        </ul>''', 'Resubmitting repeatedly.') +
    scn('Data engineering', 'Mid-level', 'Missing logs',
        'A cluster-mode job failed but the terminal shows no traceback.',
        'where to look?',
        '''<ol>
          <li>yarn logs -applicationId (AM container = driver).</li>
          <li>Spark history server for stages/tasks.</li>
          <li>On K8s: kubectl logs of the driver pod.</li>
        </ol>''', 'Rerunning in client mode in production.') +
    scn('Platform', 'Senior', 'YARN → Kubernetes',
        'Plan migrating Spark jobs from YARN to Kubernetes.',
        'plan?',
        '''<ul>
          <li>Standard images with Spark, Python and libraries.</li>
          <li>Namespaces, service accounts, quotas, pod templates.</li>
          <li>Shuffle tracking, event logs to object storage, Spark Operator.</li>
        </ul>''', 'Lifting the YARN configs unchanged.')
)
