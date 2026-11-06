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
    module='01-introduction', lesson='05-install-pyspark-and-a-spark-cluster', n='1.5',
    module_label='Module 1 · Start here: why Spark?',
    title='Install PySpark 4.3 and a Docker Spark cluster',
    desc='Set up the course lab with real outputs: pip install pyspark 4.3.0 (280 JARs, 486 MB), spark-submit and the pyspark shell, a first program in local mode, one Docker image with Python 3.12 and Java 21 for every role, a Compose file for a standalone master, two workers and a history server, the first cluster job, the 5,000,000-order dataset, and a deliberate Python 3.13 vs 3.12 mismatch that breaks a lambda.',
    og_desc='pip install pyspark, then a four-container Spark 4.3 cluster in Docker, and a deliberate Python version mismatch: the complete PySpark lab set-up, with real outputs.',
    minutes=35, level='Beginner',
    lead='This lesson builds the lab used in the rest of the course: <b>PySpark on your own machine</b> for quick work and a <b>Spark 4.3.0 standalone cluster in Docker</b> (master, two workers, history server) for everything that needs real executors. All files are in the course lab folder, and <b>every output is real</b>.',
    chips=['PySpark 4.3.0 · Java 21', 'Docker Compose cluster', 'Files included', 'Runs in your browser (Python)'],
)

MAIN = '''# Check a Spark environment description before you install (versions as in this course)
env = {"java": "21.0.12", "python_driver": "3.13.17", "python_executors": "3.12.12",
       "pyspark": "4.3.0", "pandas": "3.0.5"}

problems = []
if env["java"].split(".")[0] not in ("17", "21"):
    problems.append("Java must be 17 or 21 for Spark 4.x")
if tuple(map(int, env["python_driver"].split(".")[:2])) < (3, 10):
    problems.append("Python 3.10+ needed")
if env["python_driver"].split(".")[:2] != env["python_executors"].split(".")[:2]:
    problems.append("driver and executor Python minor versions differ -> PYTHON_VERSION_MISMATCH")
if int(env["pandas"].split(".")[0]) >= 3:
    problems.append("pandas 3 not fully supported by PySpark 4.3: pin pandas<3")
print("\\n".join(problems) or "environment OK")
'''
RUN = dict(
    heading='Run the code: an environment checker',
    intro='<p>This program checks a Spark environment against the rules from this lesson, using the versions we met in the lab. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('if env["python_driver"].split(".")[:2] != env["python_executors"].split(".")[:2]:', 'The exact problem we created in Step 8: 3.13 on the driver, 3.12 on the executors.'),
        ('if int(env["pandas"].split(".")[0]) >= 3:', 'PySpark 4.3.0 printed a FutureWarning for pandas 3.0.5.'),
    ],
    tasks=[
        dict(label='1 · Check the lab', hint='Press <b>Run</b>. Then set both Pythons to 3.12.12 and pandas to 2.3.3 and run again.', code=None),
        dict(label='2 · Predict first: cluster capacity', hint='<b>Predict first:</b> 3 workers with 4 cores and 8 GiB, executors of 2 cores and 3 GiB. How many executors?',
             code='''workers, cores, mem = 3, 4, 8
ec, em = 2, 3
per_worker = min(cores // ec, mem // em)
print("executors:", workers * per_worker, " parallelism:", workers * per_worker * ec)
'''),
        dict(label='3 · Ports to remember', hint='Map each UI to its port in our lab.',
             code='''ports = {"application UI (while running)": 4040, "master UI (host)": 8090,
         "worker UIs (host)": "8091 / 8092", "history server": 18080, "master RPC": 7077}
for k, v in ports.items():
    print(f"{str(v):12} {k}")
'''),
        dict(label='4 · Disk budget', hint='How much disk does the lab need?',
             code='''sizes_gb = {"image": 1.83, "orders_big": 0.035, "big_csv": 0.087, "event logs (approx.)": 0.05}
print(round(sum(sizes_gb.values()), 2), "GB")
'''),
        dict(label='5 · Spot the error', hint='This config hard-codes the master in the code.', expect='error',
             code='''code = 'SparkSession.builder.master("spark://spark-master:7077").getOrCreate()'
assert ".master(" not in code, "pass --master to spark-submit instead, so the same code runs everywhere"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: manage the lab cluster',
    intro='<p>Everyday commands for the Docker cluster. <b>Outputs are real.</b></p>',
    items=[
        dict(title='1 · Status of the containers', cmd='docker compose -p sparklab -f cluster.yml ps', file='terminal',
             output=capf('l15_ps.txt'),
             note='Stop with docker compose -p sparklab -f cluster.yml down; data in ./data and ./events stays.'),
        dict(title='2 · Master status as JSON', cmd='curl -s http://localhost:8090/json/', file='terminal',
             output=capf('l15_master.txt'),
             note='Summarised. Workers ALIVE and the finished application.'),
        dict(title='3 · Finished applications', cmd='curl -s http://localhost:18080/api/v1/applications', file='terminal',
             output=capf('l15_apps.txt') + '\n…',
             note='Summarised from the JSON; the first three applications of the lab. Every application that wrote an event log is listed.'),
    ],
)

TRACE = dict(
    heading='Why the lambda failed but the count worked',
    intro='<p>Follow where each piece of the Step 8 program runs.</p>',
    code='''driver_py, executor_py = "3.13", "3.12"
steps = [("spark.range(1000).count()", "JVM"), ("map(lambda x: x * 2)", "Python worker")]
for code, where in steps:
    ok = where == "JVM" or driver_py == executor_py
    print(f"{code:28} runs in {where:13} -> {'OK' if ok else 'PYTHON_VERSION_MISMATCH'}")
''',
    notes={2: 'JVM :: DataFrame operations are executed by Spark’s JVM code on executors.', 4: 'Python worker :: A lambda is pickled by the driver’s Python and must be run by a compatible Python on executors.'},
)

WORKED_INTRO = 'Three set-up decisions for real teams.'
EXAMPLES = [
    dict(level='b', tag='Setup · local', title='A requirements file',
         problem='<p>Write the requirements file for the course.</p>',
         inp='versions from this lesson',
         approach=['Pin PySpark.', 'Pin pandas below 3.', 'Add PyArrow.'],
         code='''for line in ["pyspark==4.3.0", "pandas<3", "pyarrow", "jupyterlab  # optional"]:
    print(line)
''', notes={2: 'pandas :: Remove the pin once PySpark fully supports pandas 3.'},
         tryit='pip install -r requirements.txt in a fresh virtual environment.'),
    dict(level='i', tag='Platform · Docker', title='Add a third worker',
         problem='<p>Extend the Compose file with another worker.</p>',
         inp='cluster.yml',
         approach=['Copy a worker service.', 'Change the name and host port.', 'Start it.'],
         code='''print("""  spark-worker-3:
    <<: *spark
    hostname: spark-worker-3
    command: spark-class org.apache.spark.deploy.worker.Worker --cores 2 --memory 2g --webui-port 8081 spark://spark-master:7077
    ports: ["8093:8081"]
    depends_on: [spark-master]""")
''', notes={4: 'Resources :: Do not give workers more cores and memory than your computer has.'},
         tryit='docker compose -p sparklab -f cluster.yml up -d spark-worker-3; check the master UI.'),
    dict(level='a', tag='Platform · environments', title='Ship a Python environment',
         problem='<p>Executors need numpy and the same Python; the cluster image cannot change.</p>',
         inp='YARN or Kubernetes cluster',
         approach=['Pack a venv or conda env.', 'Ship it with the job.', 'Point PYSPARK_PYTHON at it.'],
         code='''print("venv-pack -o env.tar.gz")
print("spark-submit --archives env.tar.gz#env \\\\")
print("  --conf spark.pyspark.python=./env/bin/python app.py")
''', notes={2: 'Archives :: Unpacked on each executor under the name after #.'},
         tryit='On our standalone lab the image already matches, so this is not needed.'),
]

QUIZ = mix([
    dict(q='Beginner: What does pip install pyspark include?', options=['Only Python wrappers', 'The full Spark runtime (JARs and scripts)', 'Java', 'Hadoop HDFS'], answer=1,
         why='280 JARs, 486 MB.'),
    dict(q='Beginner: What must you install besides pyspark?', options=['Scala', 'A Java 17 or 21 runtime', 'Hadoop', 'Maven'], answer=1,
         why='Spark’s engine runs on the JVM.'),
    dict(q='Beginner: Which port shows the UI of a running application?', options=['7077', '4040', '18080', '22'], answer=1,
         why='18080 is the history server for finished apps.'),
    dict(q='Intermediate: Why use one image for master, workers and driver?', options=['Smaller downloads', 'Java, Python and library versions match everywhere', 'It is required by Docker', 'Faster networks'], answer=1,
         why='Mismatches break Python code (Step 8).'),
    dict(q='Intermediate: What does the history server need?', options=['A running driver', 'Event logs written by applications', 'Hive', 'YARN'], answer=1,
         why='spark.eventLog.enabled=true and a shared log folder.'),
    dict(q='Intermediate: In Step 8, which part failed?', options=['spark.range().count()', 'The RDD map with a Python lambda', 'Connecting to the master', 'Writing Parquet'], answer=1,
         why='Python code runs in executor-side Python workers.'),
    dict(q='Advanced: How many task slots did our cluster offer?', options=['2', '4', '8', '16'], answer=1,
         why='2 workers × 2 cores.'),
    dict(q='Advanced: Why not hard-code .master() in production code?', options=['It is slower', 'The same code should run locally, in CI and on clusters; spark-submit sets the master', 'It is deprecated', 'It breaks Py4J'], answer=1,
         why='Configuration belongs outside the code.'),
])

REVISION = [
    'Laptop: Java 17/21 + <code>pip install pyspark==4.3.0</code> (bundles Spark: 280 JARs, 486 MB; needs only py4j).',
    'Tools: <code>spark-submit</code>, <code>pyspark</code> shell (<code>spark</code>, <code>sc</code> ready), UI on <b>4040</b> while running.',
    'First SparkSession: 6–15 s start-up on the lab machine.',
    'Docker lab: one image (Python 3.12, Java 21, PySpark 4.3.0, pandas&lt;3) for master, 2 workers, history server.',
    'Ports: 7077 (master RPC), 8090 (master UI), 8091/8092 (workers), 18080 (history).',
    'First cluster job: parallelism 4, 20.6 s; event logs → history server.',
    'Driver Python 3.13 vs executors 3.12 → <code>[PYTHON_VERSION_MISMATCH]</code> for lambdas/UDFs; DataFrame ops unaffected.',
]
FAQ = [
    ('Do I need Docker for this course?', 'For most lessons, pip install pyspark is enough. Docker is needed for lessons that show cluster behaviour: executors, failures, the master UI and the history server.'),
    ('Which Java should I install?', 'Java 17 or 21; the lab uses 21 (Eclipse Temurin). Java 8 and 11 do not work with Spark 4.'),
    ('How much memory does the lab need?', 'About 6–8 GB free for the cluster (two workers with 2 GiB each plus the driver and the containers). Reduce worker memory in cluster.yml on smaller machines.'),
    ('Can I use the official apache/spark image instead?', 'Yes, but check its Spark, Java and Python versions. The 3.5.6 image we had in the lab came with Java 11 and Python 3.8, too old for Spark 4; that is why we built our own.'),
    ('Is Spark standalone used in production?', 'Sometimes, for small dedicated clusters. Most production Spark runs on YARN, Kubernetes or managed services (Lesson 11.2). The concepts you practise here are the same.'),
]

PRACTICE_INTRO = 'Small programs about installing and sizing a Spark lab.'
PROBLEMS = [
    dict(level='easy', title='Master URL', stmt='Build the master URL from the Compose file.', inp='spark-master, 7077',
         code='''print("spark://" + "spark-master" + ":" + str(7077))
''', explain='From the host, use spark://localhost:7077.'),
    dict(level='easy', title='Parallelism', stmt='Total cores of the lab cluster.', inp='2 workers × 2 cores',
         code='''print(2 * 2)
''', explain='This is defaultParallelism on the cluster.'),
    dict(level='easy', title='Package size', stmt='Share of the pip package taken by JARs.', inp='462 MB of 486 MB',
         code='''print(f"{462 / 486:.0%}")
''', explain='PySpark is mostly Spark’s Java/Scala runtime.'),
    dict(level='medium', title='Version check', stmt='Compare two Python versions by minor version.', inp='3.13.17, 3.12.12',
         code='''a, b = "3.13.17", "3.12.12"
print("match" if a.split(".")[:2] == b.split(".")[:2] else "MISMATCH")
''', explain='Patch versions may differ; minor versions must match.'),
    dict(level='medium', title='Worker memory', stmt='Max worker memory on a 16 GB laptop leaving 6 GB for everything else.', inp='2 workers',
         code='''print((16 - 6) / 2, "GB per worker")
''', explain='Set --memory in cluster.yml accordingly.'),
    dict(level='medium', title='Event log size', stmt='Estimate event log storage for a month.', inp='200 apps/day × 2 MB',
         code='''print(200 * 2 * 30 / 1024, "GB")
''', explain='Configure spark.history.fs.cleaner.* to delete old logs.'),
    dict(level='business', title='Laptop vs cloud lab', stmt='Monthly cost of a small cloud cluster for practice.', inp='3 nodes × ₹15/hour × 40 hours (illustrative)',
         code='''print("₹", 3 * 15 * 40)
''', explain='The Docker lab costs nothing beyond your machine.'),
    dict(level='business', title='Onboarding time', stmt='Time saved per new joiner with a ready image.', inp='4 h manual vs 0.5 h with image, 20 joiners/year',
         code='''print((4 - 0.5) * 20, "hours per year")
''', explain='A pinned image also prevents version-mismatch incidents.'),
]

SCN_INTRO = 'Set-up questions test practical experience.'
SCENARIOS = (
    scn('Any company · PySpark', 'Fresher', '“How do you install PySpark?”',
        'Describe a local PySpark set-up.',
        'do you know the moving parts?',
        '<p>Install Java 17 or 21, create a virtual environment, pip install pyspark with a pinned version (plus pandas and pyarrow if needed), then create a SparkSession with master local[*] and run a smoke test. The UI is on port 4040 while the application runs.</p>', 'Saying Hadoop must be installed first.') +
    scn('Data engineering', 'Mid-level', 'PYTHON_VERSION_MISMATCH',
        'A job fails with PYTHON_VERSION_MISMATCH on the cluster.',
        'can you fix environments?',
        '''<ol>
          <li>Driver and executor Python minor versions differ.</li>
          <li>Use the same image or interpreter everywhere, or set spark.pyspark.python / PYSPARK_PYTHON.</li>
          <li>Ship dependencies as a packed environment if the cluster cannot be changed.</li>
        </ol>''', 'Reinstalling pyspark on the laptop only.') +
    scn('Platform', 'Mid-level', 'UI disappears after the job',
        'The team cannot see the Spark UI of last night’s failed job.',
        'do you know the history server?',
        '''<ul>
          <li>Enable spark.eventLog.enabled with a shared spark.eventLog.dir.</li>
          <li>Run a history server reading that directory (port 18080).</li>
          <li>Set retention and cleaning for the logs.</li>
        </ul>''', 'Asking people to keep the driver running.') +
    scn('Architecture', 'Senior', 'Standardise Spark environments',
        'Ten teams run Spark on laptops, CI and Kubernetes with different versions.',
        'can you design for consistency?',
        '''<ul>
          <li>One base image per Spark version with Java, Python and core libraries pinned; teams extend it.</li>
          <li>Same image for notebooks, CI and cluster jobs; masters set by configuration, not code.</li>
          <li>Upgrade by publishing a new image and testing jobs against it.</li>
        </ul>''', 'Letting every team pick versions freely.')
)
