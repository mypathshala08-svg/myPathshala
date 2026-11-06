import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
LAB = os.path.join(HERE, '..', '..', 'lab') + os.sep
CAP = LAB + 'captures' + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()

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

DOCKERFILE = open(LAB + 'image/Dockerfile').read().rstrip()
COMPOSE = open(LAB + 'cluster.yml').read().rstrip()

def lab(hi=-1):
    o = opbox(10, 20, 'Laptop', 'pip install pyspark', 'acc' if hi == 0 else 'blue', 108, 30)
    o += box(132, 10, 222, 150, 'card') + t(243, 24, 'Docker: project sparklab', 7.4, 'ink2', bold=True)
    o += opbox(142, 32, 'spark-master', ':7077 · UI :8090', 'acc' if hi == 1 else 'amber', 98, 30)
    o += opbox(248, 32, 'spark-history', 'UI :18080', 'acc' if hi == 4 else 'violet', 98, 30)
    o += opbox(142, 82, 'spark-worker-1', '2 cores · 2 GiB', 'acc' if hi == 2 else 'green', 98, 30)
    o += opbox(248, 82, 'spark-worker-2', '2 cores · 2 GiB', 'acc' if hi == 2 else 'green', 98, 30)
    o += box(142, 124, 204, 26, 'acc' if hi == 3 else 'card') + t(244, 141, './data  ./jobs  ./events (shared)', 6.8, 'ink2', mono=True)
    o += arrow(118, 35, 140, 45, 'ink3', 1.2) + arrow(191, 82, 191, 64, 'ink3', 1.1) + arrow(297, 82, 230, 64, 'ink3', 1.1)
    return o

# ---------------------------------------------------------------- story
sc = (lab(-1) +
      box(410, 12, 222, 136, 'card') + t(521, 30, 'Set-up, measured', 8.6, bold=True) +
      ''.join(t(422, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
          ('pip package: 486 MB (280 JARs)', 'ink'), ('first SparkSession: 6–15 s', 'amber'), ('image: 1.83 GB', 'ink'),
          ('cluster up: 4 containers', 'green'), ('first job on cluster: 20.6 s', 'green'), ('py 3.13 vs 3.12 → MISMATCH', 'red')])))
scene_svg = scene('Two ways to run Spark in this course: PySpark from pip on your own machine for quick work, and a four-container Spark 4.3.0 cluster in Docker for everything that needs real executors, a master UI and a history server.', sc,
                  'Same Spark, <tspan font-weight="700" class="s-acc">laptop</tspan> or <tspan font-weight="700" class="s-acc">cluster</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“It works on my laptop. Does it work on the cluster?”</h2>
  <div class="story">
    <p class="narration">Riya has PySpark running on her laptop. Kabir wants to practise on something closer to production: a real master, real workers, a UI that survives after the job, and the five-million-order dataset from the earlier lessons. Arjun Sir gives them one afternoon.</p>

{scene_svg}

R> Sir, is <code>pip install pyspark</code> all I need?
A> For your laptop, almost: pip gives you Spark itself, but you still need <b>Java</b>. For a cluster, we use <b>Docker</b>: one image with Python, Java and PySpark, and a compose file that starts a master, two workers and a history server. The same image runs the driver, so versions always match.
K> Why does matching matter so much?
A> Because Python code you send to executors runs in <b>their</b> Python. We will break it on purpose. Everything today is real: PySpark 4.3.0 from pip, Python 3.12/3.13, Java 21, Docker Compose.
  </div>
</section>
'''

lv = '''
LEVELS> Installing Spark at three levels
L1> Two set-ups
      <ul>
        <li><b>Laptop</b>: install Java 17 or 21, then <code>pip install pyspark==4.3.0</code>. Run Python scripts or the <code>pyspark</code> shell.</li>
        <li><b>Docker cluster</b>: install Docker, build one image, run <code>docker compose up -d</code>. You get a master, two workers and a history server.</li>
        <li>Both run the same Spark code; the master URL decides where it runs.</li>
      </ul>
L2> What is inside
      <ul>
        <li>The pip package contains the whole Spark distribution: 280 JAR files (462 MB), <code>spark-submit</code>, <code>pyspark</code>, <code>spark-class</code>, the start scripts.</li>
        <li>The image adds Python 3.12 and a Java 21 runtime; containers differ only in the command they run (Master, Worker, HistoryServer).</li>
        <li>Shared folders: <code>./data</code> (datasets), <code>./jobs</code> (your scripts), <code>./events</code> (event logs for the history server).</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>A first SparkSession took 6–15 s to start on the lab machine; the cluster’s first job took 20.6 s end to end, mostly executor start-up.</li>
        <li>A driver on Python 3.13 with executors on 3.12 ran DataFrame code fine but failed on a Python lambda with <code>[PYTHON_VERSION_MISMATCH]</code>.</li>
        <li>pandas 3 triggered a PySpark warning, so the image pins <code>pandas&lt;3</code>.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>A PySpark installation and a standalone cluster</h2>
''' + def_block(
    'A <b>PySpark installation</b> consists of the <code>pyspark</code> Python package (which, when installed from PyPI, bundles the Spark runtime JARs and launch scripts), a supported Java runtime and a supported Python interpreter. Spark can run in <b>local mode</b> inside one JVM, or connect to a cluster manager. A <b>Spark standalone cluster</b> is Spark’s own cluster manager: a <b>master</b> process accepts applications and allocates resources, and <b>worker</b> processes on each machine launch executors. A <b>history server</b> reconstructs the web UI of finished applications from event logs. For PySpark, the driver and all executors must use compatible Python environments with the same minor version and the same libraries.',
    'Install Java and pip install pyspark to run Spark on your computer. For a practice cluster, run Spark’s master, workers and history server as Docker containers from one image, so every part uses the same versions.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('pyspark (pip)', 'Python package that includes Spark itself.'),
    ('spark-submit', 'Command that launches an application on a master.'),
    ('pyspark shell', 'Interactive Python with <code>spark</code> and <code>sc</code> ready.'),
    ('Master URL', '<code>local[*]</code>, <code>spark://host:7077</code>, <code>yarn</code>, <code>k8s://…</code>'),
    ('Worker', 'Standalone process that starts executors on its machine.'),
    ('History server', 'Shows the UI of finished applications from event logs.'),
    ('Event log', 'A file of everything an application did; <code>spark.eventLog.enabled</code>.'),
    ('PYSPARK_PYTHON', 'The Python that executors use for Python code.'),
]) + '''

  <h3>What you install, and where it comes from</h3>
''' + table(['Piece', 'Version in this course', 'Install with', 'Check with'], [
    ['Java runtime', '21 (17 also supported)', 'OS package or Eclipse Temurin', '<code>java -version</code>'],
    ['Python', '3.12 in the cluster, 3.10+ required', 'python.org, OS, conda', '<code>python3 --version</code>'],
    ['PySpark', '4.3.0', '<code>pip install pyspark==4.3.0</code>', '<code>pyspark.__version__</code>'],
    ['pandas, PyArrow', 'pandas &lt; 3, PyArrow current', 'pip', 'import warnings'],
    ['Docker + Compose', 'Any recent version', 'Docker Desktop / Engine', '<code>docker compose version</code>'],
], minw=720) + lv + '''
EXAM> “How do you set up PySpark locally?” Install Java 17 or 21, pip install pyspark (which bundles Spark), and run with master local[*]. For a multi-node practice environment, run Spark standalone (master + workers) in Docker or use a managed service; keep Python versions identical on driver and executors.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Ways to get Spark</h2>
''' + table(['Option', 'Good for', 'Effort', 'Notes'], [
    ['pip install pyspark', 'Learning, scripts, unit tests', 'Minutes', 'Needs Java; local mode'],
    ['Spark download (tgz) + SPARK_HOME', 'Servers, Scala/Java users', 'Minutes', 'Same JARs; set PATH'],
    ['conda-forge pyspark', 'Conda environments', 'Minutes', 'Can pull a JDK as well'],
    ['Docker standalone cluster (this lesson)', 'Practising cluster behaviour', 'An afternoon', 'Our lab; files in lab/'],
    ['Official <code>apache/spark</code> images', 'Kubernetes, quick containers', 'Minutes', 'Check the tag’s Python and Java versions'],
    ['Managed: Databricks, EMR, Dataproc, Fabric, Synapse', 'Production', 'Account setup', 'Versions chosen by the provider'],
    ['Google Colab / notebooks', 'Quick experiments', 'Minutes', 'pip install inside the notebook'],
], minw=760) + '''
WARN> On <b>Windows</b> without Docker, PySpark runs, but writing files can fail without Hadoop’s native helpers (<code>winutils.exe</code> and <code>hadoop.dll</code>). The Docker set-up in this lesson avoids that and behaves the same on Windows, macOS and Linux. Also avoid spaces in installation paths.
</section>
'''

FIG = fig('ui-master.webp', 1280, 760, 'Spark master web UI showing two alive workers with 2 cores and 2 GiB each and one completed application', 'Real screenshot: our master UI on port 8090 after the first job. Two workers ALIVE (4 cores, 4 GiB in total) and the completed <code>tiffingo-city-report</code> application.')
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>From pip to a four-container cluster</h2>
  <p>All outputs are real. Steps 1–3 run on the lab machine (Python 3.13, Java 21); Steps 4–8 use Docker. Every file is in the course lab folder (<code>lab/image/Dockerfile</code>, <code>lab/cluster.yml</code>, <code>lab/jobs/m1</code>).</p>
''' + stepper([
    ('Step 1 · Install PySpark and check it',
     code('bash', 'terminal', 'java -version                       # 17 or 21\npip install pyspark==4.3.0 "pandas<3" pyarrow\npip show pyspark | grep -E "Version|Requires"\ndu -sh $(python3 -c "import pyspark, os; print(os.path.dirname(pyspark.__file__))")/jars\nspark-submit --version', 'Version: 4.3.0\nRequires: py4j\n462M\t…/site-packages/pyspark/jars     (280 JAR files; 486 MB in total)\n' + capf('l15_version.txt')),
     'The pip package is Spark: 280 JAR files plus the launch scripts, about half a gigabyte. Its only Python dependency is <b>py4j</b>; pandas and PyArrow are optional extras. <code>spark-submit</code> is now on your PATH. Spark 4.3.0 is built with <b>Scala 2.13</b> and ran here on Java 21.'),
    ('Step 2 · Your first program',
     code('python', 'hello.py', "import time\nfrom pyspark.sql import SparkSession\nt = time.time()\nspark = SparkSession.builder.appName(\"hello\").master(\"local[2]\").getOrCreate()\nprint(\"startup_s\", round(time.time() - t, 2))\nprint(\"version\", spark.version, \"| master\", spark.sparkContext.master, \"| ui\", spark.sparkContext.uiWebUrl)\ndf = spark.range(1, 1_000_001)\nprint(\"sum\", df.selectExpr(\"sum(id)\").first()[0], \"| partitions\", df.rdd.getNumPartitions())\nspark.stop()", capf('l15_hello.txt')),
     'Starting the JVM took 6.3 s this time (15.3 s on the very first run, with cold caches). The sum of 1 to 1,000,000 is correct, computed in 2 partitions. While the program runs, the Spark UI is at the printed address on <b>port 4040</b>.'),
    ('Step 3 · The interactive shell',
     code('bash', 'terminal', 'pyspark\n>>> spark.version\n>>> sc.master\n>>> spark.range(5).count()', capf('l15_shell.txt')),
     'The <code>pyspark</code> command starts Python with a ready <code>spark</code> (SparkSession) and <code>sc</code> (SparkContext) in <code>local[*]</code> mode. Good for exploring; for anything you will run again, write a script. Jupyter works too: <code>pip install jupyterlab</code> and create the SparkSession in the first cell.'),
    ('Step 4 · One image for every role',
     code('dockerfile', 'lab/image/Dockerfile', DOCKERFILE, 'docker build -t tiffingo/spark:4.3.0 lab/image\n' + capf('l15_image.txt')),
     'We take Java 21 from the Eclipse Temurin image and install PySpark into a slim Python 3.12 image. The <b>same image</b> will run the master, the workers, the history server and the driver, so Java, Python, PySpark and pandas versions match everywhere. <code>SPARK_HOME</code> points at the pip package, which contains <code>spark-class</code> and the <code>sbin</code> scripts.'),
    ('Step 5 · Start the cluster',
     code('yaml', 'lab/cluster.yml', COMPOSE, 'docker compose -p sparklab -f cluster.yml up -d\n…\n' + capf('l15_ps.txt')),
     'Four containers from one image, each running one Spark class in the foreground (<code>SPARK_NO_DAEMONIZE</code>). Workers register with <code>spark://spark-master:7077</code> and offer 2 cores and 2 GiB each. Host ports: master UI <b>8090</b>, workers 8091/8092, history server <b>18080</b>, and 7077 for drivers.'),
    ('Step 6 · Submit the first job',
     code('bash', 'terminal', 'docker exec sparklab-spark-master-1 spark-submit \\\n  --master spark://spark-master:7077 \\\n  --conf spark.eventLog.enabled=true --conf spark.eventLog.dir=/opt/spark-events \\\n  /jobs/m1/city_report.py', capf('l15_first_submit.txt')) + FIG,
     'The driver ran in the master container (client mode) and got one executor per worker: <b>parallelism 4</b>. The report uses Lesson 1.1’s <code>orders.csv</code>, now counting only delivered orders (Mumbai: 9,250 orders, ₹27,12,820). With event logging on, the finished application appears in the history server at port 18080.'),
    ('Step 7 · Create the course dataset',
     code('bash', 'terminal', 'docker exec sparklab-spark-master-1 spark-submit --master spark://spark-master:7077 /jobs/m1/make_big.py\nls data/orders_big', capf('l15_makebig.txt')),
     '<code>make_big.py</code> generates 5,000,000 TiffinGo orders with <code>spark.range</code> and hash functions (deterministic, so your numbers match the lessons) and writes 8 Snappy-compressed Parquet files. The <code>_SUCCESS</code> file marks a completed write. Lessons 1.2–1.4 used this dataset.'),
    ('Step 8 · Break it on purpose: Python versions',
     code('python', 'mismatch.py (driver on the host: Python 3.13)', 'spark = (SparkSession.builder.master("spark://localhost:7077")\n         .config("spark.driver.host", "172.19.0.1").getOrCreate())\nprint("DataFrame count on the cluster:", spark.range(1000).count())\nprint(spark.sparkContext.parallelize(range(10), 2).map(lambda x: x * 2).sum())', capf('l15_mismatch.txt')),
     'DataFrame operations run entirely in the executors’ JVMs, so the count worked. The <code>lambda</code> must run in a <b>Python worker</b> on each executor, which here was Python 3.12, while the driver was 3.13. Spark retried the task 4 times, then failed. Fix: use the same Python minor version everywhere (our image), or set <code>PYSPARK_PYTHON</code> to a matching interpreter on the executors.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('pip install pyspark==4.3.0', W), ('Requires: py4j', W), ('280 JARs, 486 MB', Y), ('version 4.3.0 · Scala 2.13.18', G)], size=7.4),
    term([('startup_s 6.32', Y), ('master local[2] · ui :4040', W), ('sum 500000500000 · partitions 2', G)], size=7.4),
    term([('docker compose up -d', W), ('spark-master    7077 · 8090', G), ('spark-worker-1/2  8091/8092', G), ('spark-history   18080', G)], size=7.2),
    term([('app-…-0000 · client mode', W), ('parallelism : 4', G), ('Mumbai 9250 2712820', G), ('FINISHED 20.6 s', G)], size=7.4),
    term([('DataFrame count: 1000', G), ('lambda x: x * 2', W), ('[PYTHON_VERSION_MISMATCH]', RD), ('worker 3.12 · driver 3.13', RD)], size=7.4),
]
B1 = [
    lab(0) + cap('Spark ships inside the pip package.', '', 'blue', y=166, h=24),
    lab(0) + cap('Local mode: one JVM on your laptop.', '', 'blue', y=166, h=24),
    lab(1) + cap('Master, workers, history: one image.', '', 'amber', y=166, h=24),
    lab(2) + cap('Each worker starts an executor.', '', 'green', y=166, h=24),
    lab(2) + cap('Python code runs in the workers’ Python.', '', 'amber', y=166, h=24),
]
see_caps = ['pip installed the whole Spark runtime.',
            'The first program ran in local mode.',
            'Four containers came up.',
            'The first cluster job finished correctly.',
            'Different Python versions broke a lambda.']
behind_caps = ['JARs, scripts and py4j in site-packages.',
               'The UI lives on port 4040 while it runs.',
               'The same image, a different Spark class each.',
               '2 executors × 2 cores = parallelism 4.',
               'DataFrame ops stay in the JVM; lambdas do not.']
two = anim_two('Installing Spark', 'Laptop and Docker cluster', 'Real lab outputs', 'What runs where', see, B1, see_caps, behind_caps)

# ---- scenario 1: new laptop
e1 = (t(180, 22, 'New laptop, day one', 9.4, bold=True) + t(180, 56, 'pip install pyspark → JAVA_GATEWAY_EXITED', 8, 'ink', mono=True) + cap('Java missing.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Install Java 21', 9.4, bold=True) + t(180, 56, 'set JAVA_HOME', 8.4, 'ink', mono=True) + cap('Spark starts.', '', 'green', y=150, h=34))
e3 = (t(180, 22, 'pandas warning', 9.4, bold=True) + t(180, 56, 'pandas >= 3.0.0 not fully supported', 8.2, 'ink', mono=True) + cap('Pin pandas<3.', '', 'amber', y=150, h=34))
e4 = (t(180, 22, 'requirements.txt', 9.4, bold=True) + t(180, 56, 'pyspark==4.3.0 · pandas<3 · pyarrow', 8.2, 'ink', mono=True) + cap('Same for everyone.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Smoke test passes', 9.4, 'acc', bold=True) + t(180, 56, 'spark.range(5).count() → 5', 8.4, 'ink', mono=True) + cap('Ready in 15 minutes.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Setting up a new laptop',
              'The usual first-day problems. (Typical; errors from our lab.)',
              'Local set-up', 'Install Java, pin package versions in one file and run a smoke test', [e1, e2, e3, e4, e5],
              ['Java missing.', 'Install Java.', 'pandas warning.', 'Pin versions.', 'Smoke test.'],
              hid='scenario-laptop')

# ---- scenario 2: version mismatch on a cluster
b1 = (t(180, 22, 'Job fails only with UDFs', 9.4, bold=True) + t(180, 56, 'DataFrame steps run fine', 8.4, 'ink2') + cap('Classic mismatch sign.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Read the error', 9.4, bold=True) + t(180, 56, 'PYTHON_VERSION_MISMATCH 3.12 vs 3.13', 8.2, 'ink', mono=True) + cap('Driver ≠ executors.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'Same image everywhere', 9.4, bold=True) + t(180, 56, 'driver and executors from one image', 8.2, 'ink2') + cap('Our lab’s approach.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Or set the Python', 9.4, bold=True) + t(180, 56, 'PYSPARK_PYTHON / spark.pyspark.python', 8, 'ink', mono=True) + cap('Matching interpreter.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Ship libraries too', 9.4, 'acc', bold=True) + t(180, 56, 'packed venv / conda archive', 8.4, 'ink2') + cap('Same pandas, numpy …', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'It works locally but not on the cluster',
              'What Step 8 looks like in a real team. (Typical fixes.)',
              'Python environments', 'Driver and executors need the same Python minor version and libraries: one image, or a shipped environment', [b1, b2, b3, b4, b5],
              ['Only Python code fails.', 'Versions differ.', 'One image.', 'Or point to the right Python.', 'Ship the libraries.'],
              hid='scenario-mismatch')

# ---- scenario 3: dev to prod
u1 = (t(180, 22, 'Dev: Docker cluster', 9.4, bold=True) + t(180, 56, 'spark://spark-master:7077', 8.4, 'ink', mono=True) + cap('Cheap, local, realistic.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'CI: local mode', 9.4, bold=True) + t(180, 56, 'pytest with local[2]', 8.4, 'ink', mono=True) + cap('Fast tests.', '', 'green', y=150, h=34))
u3 = (t(180, 22, 'Prod: managed or K8s', 9.4, bold=True) + t(180, 56, 'EMR · Dataproc · Databricks · K8s', 8.2, 'ink2') + cap('Only the master changes.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Same versions', 9.4, bold=True) + t(180, 56, 'Spark 4.3 · Python 3.12 · Java 21', 8.2, 'ink', mono=True) + cap('Pinned in all three.', '', 'amber', y=150, h=34))
u5 = (t(180, 22, 'Same code', 9.4, 'acc', bold=True) + t(180, 56, 'no master() hard-coded', 8.4, 'ink2') + cap('Set it with spark-submit.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'One code base, three environments',
              'How teams move from laptop to production. (Typical practice.)',
              'Environments', 'Keep code free of hard-coded masters, pin versions everywhere and let spark-submit or the platform choose where it runs', [u1, u2, u3, u4, u5],
              ['Dev cluster.', 'Tests in CI.', 'Production platform.', 'Same versions.', 'Same code.'],
              hid='scenario-envs')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Laptop and Docker cluster</h2>
  <p>Left: real outputs. Right: what runs where.</p>
''' + two + '''
  <p>Three live scenarios follow: a new laptop, a version mismatch on a cluster, and moving from development to production.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Spark environments at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'pip', 12, 'blue', bold=True) + t(60, 58, 'laptops', 7.4, 'ink2'),
    '1. Developer laptops',
    'Engineers write and test PySpark locally with pip-installed Spark and small samples before running on clusters.',
    ['pip', '*local[*]', 'Tested code']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'image', 11, 'green', bold=True) + t(60, 58, 'pinned', 7.4, 'ink2'),
    '2. One container image per platform',
    'Teams build one image with Spark, Java, Python and libraries for notebooks, CI and Kubernetes jobs.',
    ['Dockerfile', '*image', 'Everywhere']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'CI', 12, 'violet', bold=True) + t(60, 58, 'tests', 7.4, 'ink2'),
    '3. Continuous integration',
    'Pull requests run PySpark unit tests in local mode on every commit (Lesson 11.4).',
    ['Commit', '*pytest + Spark', 'Merge']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'history', 10, 'acc', bold=True) + t(60, 58, 'server', 7.4, 'ink2'),
    '4. Shared history servers',
    'Platforms keep event logs in object storage and one history server for all teams’ finished jobs.',
    ['Event logs', '*history server', 'Debug later']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'training', 9, 'acc', bold=True) + t(60, 58, 'labs', 7.4, 'ink2'),
    '5. Training clusters',
    'Docker Compose clusters like ours are used in training and interviews to practise failures safely.',
    ['Compose', '*cluster', 'Practice']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> Lessons <a href="../01-prerequisites-python-sql-and-hadoop/">1.1</a> and <a href="../03-spark-architecture/">1.3</a>. You need Docker for Steps 4–8; Steps 1–3 need only Java and Python.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
