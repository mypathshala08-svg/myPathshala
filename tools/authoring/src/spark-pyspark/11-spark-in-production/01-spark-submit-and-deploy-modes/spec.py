import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='11-spark-in-production', lesson='01-spark-submit-and-deploy-modes', n='11.1',
    module_label='Module 11 · Spark in production',
    title='spark-submit and deploy modes',
    desc='spark-submit on a real Spark 4.3.0 standalone cluster: a PySpark job failing on executors with ModuleNotFoundError, fixed with --py-files, configuration precedence measured (code 12 beats --conf 100 beats properties file 50; --conf 1500m beats file 1g), client vs cluster deploy mode, and the error for Python cluster mode on standalone, plus options for shipping Python environments.',
    og_desc='Why your PySpark job works in a notebook but fails on the cluster: --py-files, config precedence and deploy modes, measured.',
    minutes=26, level='Intermediate',
    lead='<code>spark-submit</code> moves your code from a notebook to a cluster. This lesson submits a real job to a standalone cluster, breaks it with a missing module, ships it with <code>--py-files</code>, measures <b>configuration precedence</b>, and compares client and cluster deploy modes. <b>All outputs are real</b> (Spark 4.3.0).',
    chips=['Spark 4.3.0 cluster', '--py-files', 'Config precedence', 'Runs in your browser (Python)'],
)

MAIN = '''# Spark configuration precedence (simplified)
defaults_file = {"spark.executor.memory": "1g", "spark.sql.shuffle.partitions": "50", "spark.eventLog.enabled": "true"}
submit_conf   = {"spark.sql.shuffle.partitions": "100", "spark.executor.memory": "1500m"}
in_code       = {"spark.sql.shuffle.partitions": "12"}

effective = {}
for layer in (defaults_file, submit_conf, in_code):     # later layers win
    effective.update(layer)

for k, v in sorted(effective.items()):
    print(f"{k:30} = {v}")
'''
RUN = dict(
    heading='Run the code: which setting wins?',
    intro='<p>The lab’s three configuration layers. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('for layer in (defaults_file, submit_conf, in_code):     # later layers win', 'Properties file < spark-submit flags/--conf < SparkConf/builder in code.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then remove the setting from <code>in_code</code>.', code=None),
        dict(label='2 · Predict first: where is the driver?', hint='<b>Predict first:</b> client vs cluster mode.',
             code='''for mode in ("client", "cluster"):
    print(mode, "->", "submitting machine" if mode == "client" else "a node inside the cluster")
'''),
        dict(label='3 · Executor slots', hint='Total task slots from submit options.',
             code='''num_executors, executor_cores = 10, 4
print(num_executors * executor_cores, "tasks at once")
'''),
        dict(label='4 · Build the command', hint='Assemble a spark-submit command.',
             code='''opts = {"--master": "yarn", "--deploy-mode": "cluster", "--py-files": "deps.zip", "--conf": "spark.sql.shuffle.partitions=200"}
print("spark-submit " + " ".join(f"{k} {v}" for k, v in opts.items()) + " app.py 2026-11-05")
'''),
        dict(label='5 · Spot the error', hint='Python cluster mode on a standalone master.', expect='error',
             code='''master, mode, lang = "spark://spark-master:7077", "cluster", "python"
assert not (master.startswith("spark://") and mode == "cluster" and lang == "python"), \\
    "Cluster deploy mode is currently not supported for python applications on standalone clusters"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: spark-submit',
    intro='<p>Against the lab cluster from Lesson 1.5. <b>Outputs are real</b> (Spark 4.3.0).</p>',
    items=[
        dict(title='1 · Zip a package', cmd='cd pkg && python -m zipfile -c ../tiffin_utils.zip tiffin_utils', file='bash',
             output='', note='Zip the package folder.'),
        dict(title='2 · Submit', cmd='spark-submit --master spark://spark-master:7077 --py-files tiffin_utils.zip submit_job.py', file='bash',
             output='deployMode: client | driver host: spark-master\n…\nwith GST: [(100, 105.0), (200, 210.0), (300, 315.0)]', note='Executors import it.'),
        dict(title='3 · Cluster mode (Python, standalone)', cmd='spark-submit --master spark://spark-master:7077 --deploy-mode cluster submit_job.py', file='bash',
             output='Exception in thread "main" org.apache.spark.SparkException: Cluster deploy mode is currently not supported for python applications on standalone clusters.', note='Use YARN/K8s.'),
    ],
)

TRACE = dict(
    heading='Merging configuration layers',
    intro='<p>Watch the shuffle setting change as layers apply.</p>',
    code='''layers = [("file", 50), ("--conf", 100), ("code", 12)]
value = None
for name, v in layers:
    value = v
print(value)
''',
    notes={3: 'Layer :: Later layers overwrite earlier ones.', 5: 'Effective :: 12, from code.'},
)

WORKED_INTRO = 'Three submit decisions at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='Submit · basics', title='Write the command',
         problem='<p>Run billing.py on YARN, 10 executors of 4 cores and 8 GB, with helpers in utils.zip.</p>',
         inp='requirements',
         approach=['Master and deploy mode.', 'Resources.', 'Dependencies, then the script and its args.'],
         code='''cmd = ("spark-submit --master yarn --deploy-mode cluster --num-executors 10 "
       "--executor-cores 4 --executor-memory 8g --py-files utils.zip billing.py 2026-11-05")
print(cmd)
''', notes={1: 'Order :: Options before the application file.'},
         tryit='Step 2.'),
    dict(level='i', tag='Submit · deps', title='A library with C code',
         problem='<p>The job needs a library with compiled extensions not on the nodes.</p>',
         inp='compiled dependency',
         approach=['--py-files cannot ship compiled wheels reliably.', 'Pack a venv/conda env.', '--archives + PYSPARK_PYTHON.'],
         code='''print("venv-pack -o env.tar.gz")
print("spark-submit --archives env.tar.gz#env --conf spark.pyspark.python=./env/bin/python app.py")
''', notes={2: 'Archive :: Unpacked into each container as ./env.'},
         tryit='Scenario 1.'),
    dict(level='a', tag='Submit · config', title='Move settings out of code',
         problem='<p>The script hard-codes memory and partitions.</p>',
         inp='builder.config(...) in code',
         approach=['Code settings win over --conf.', 'Move them to properties files.', 'Print effective config.'],
         code='''code = {"spark.sql.shuffle.partitions": "12"}
print("remove from code:", list(code))
''', notes={1: 'Operators :: Can then tune per environment.'},
         tryit='Step 3.'),
]

QUIZ = mix([
    dict(q='Beginner: In client mode the driver runs…', options=['On a worker', 'In the spark-submit process', 'In HDFS', 'Nowhere'], answer=1,
         why='Where you submit.'),
    dict(q='Beginner: Ship your own Python modules with…', options=['--jars', '--py-files', '--driver-memory', '--queue'], answer=1,
         why='Zip of the package.'),
    dict(q='Beginner: Default config file name?', options=['spark.yaml', 'spark-defaults.conf', 'config.ini', 'hadoop.xml'], answer=1,
         why='Or --properties-file.'),
    dict(q='Intermediate: Code sets 12, --conf sets 100, file sets 50. Effective?', options=['50', '100', '12', 'Error'], answer=2,
         why='Code wins.'),
    dict(q='Intermediate: Driver fine, executors ModuleNotFoundError. Cause?', options=['Bug in Spark', 'Module not shipped to executors', 'Too little memory', 'Wrong master'], answer=1,
         why='Use --py-files.'),
    dict(q='Intermediate: Production jobs on YARN usually use…', options=['client mode from a laptop', 'cluster mode', 'local mode', 'console'], answer=1,
         why='Driver in the cluster.'),
    dict(q='Advanced: Python + cluster mode + standalone master?', options=['Works', 'Not supported', 'Needs --jars', 'Only with Kafka'], answer=1,
         why='Lab error.'),
    dict(q='Advanced: Ship a library with C extensions…', options=['--py-files zip', '--archives packed env (or container image)', '--conf', 'Not possible'], answer=1,
         why='venv-pack / conda-pack.'),
])

REVISION = [
    'spark-submit: master, deploy mode, resources, dependencies, app + args.',
    'client mode: driver in the submitter; cluster mode: driver in the cluster.',
    'Executors only have shipped code: --py-files, --archives, --packages, images.',
    'Lab: no --py-files → ModuleNotFoundError; with it → 105.0, 210.0.',
    'Precedence: code > --conf/flags > properties file (12 > 100 > 50).',
    'Python cluster mode is not supported on standalone.',
    'Keep environment settings out of code; print effective config.',
]
FAQ = [
    ('What does --packages do?', 'Downloads Maven artifacts (and dependencies) and adds them to driver and executor classpaths, e.g. spark-sql-kafka.'),
    ('Can I pass arguments to my script?', 'Yes, anything after the application file is passed to it (sys.argv).'),
    ('Where do I see the effective configuration?', 'Spark UI → Environment tab, or spark.sparkContext.getConf().getAll().'),
    ('What is spark.pyspark.python?', 'The Python executable used by executors (and driver with spark.pyspark.driver.python).'),
    ('Is local mode a deploy mode?', 'No, local[*] is a master URL: everything runs in one JVM, useful for development and tests.'),
]

PRACTICE_INTRO = 'Programs about submit options.'
PROBLEMS = [
    dict(level='easy', title='Slots', stmt='Task slots for 20 executors × 5 cores.', inp='20, 5',
         code='''print(20 * 5)
''', explain='100.'),
    dict(level='easy', title='Effective value', stmt='Apply layers.', inp='file 50, conf 100',
         code='''print({**{"p": 50}, **{"p": 100}}["p"])
''', explain='No code setting: 100.'),
    dict(level='easy', title='GST', stmt='The helper on 300.', inp='300',
         code='''print(round(300 * 1.05, 2))
''', explain='315.0.'),
    dict(level='medium', title='Parse args', stmt='Read the run date argument.', inp='argv',
         code='''import sys
argv = ["billing.py", "2026-11-05"]
print("run date:", argv[1])
''', explain='sys.argv in the job.'),
    dict(level='medium', title='Memory total', stmt='Cluster memory requested.', inp='10 × (8g + 0.8g overhead)',
         code='''print(10 * (8 + 0.8), "GB")
''', explain='Include overhead.'),
    dict(level='medium', title='Mode check', stmt='Allowed deploy mode?', inp='master, language',
         code='''def ok(master, lang, mode):
    return not (master.startswith("spark://") and lang == "python" and mode == "cluster")
print(ok("yarn", "python", "cluster"), ok("spark://m:7077", "python", "cluster"))
''', explain='True, False.'),
    dict(level='business', title='Failed nights', stmt='Hours lost to 4 failed nightly runs of 3 h.', inp='4 × 3',
         code='''print(4 * 3, "hours")
''', explain='Package dependencies properly.'),
    dict(level='business', title='Cost of idle submitter', stmt='Laptop-driver failures per month at 2/week.', inp='2 × 4',
         code='''print(2 * 4)
''', explain='Use cluster mode.'),
]

SCN_INTRO = 'spark-submit questions check production readiness.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“Client vs cluster mode”',
        'Explain the two deploy modes.',
        'when to use?',
        '<p>Client mode runs the driver in the spark-submit process (good for shells, notebooks, debugging). Cluster mode runs the driver inside the cluster so the job continues if the submitter disconnects (good for production). On standalone, Python supports only client mode.</p>', 'Thinking executors run on the laptop in client mode.') +
    scn('Data engineering', 'Mid-level', 'ModuleNotFoundError',
        'Job works locally, fails on the cluster with ModuleNotFoundError.',
        'fix?',
        '''<ul>
          <li>Executors lack the module; ship it with --py-files (zip/wheel).</li>
          <li>Compiled libs: --archives packed env or a container image.</li>
          <li>Pin versions in CI-built artifacts.</li>
        </ul>''', 'Installing manually on each node.') +
    scn('Data engineering', 'Mid-level', 'Ignored setting',
        'A --conf value has no effect.',
        'why?',
        '''<ol>
          <li>Check the Environment tab for the effective value.</li>
          <li>Code (builder.config/SparkConf) overrides --conf.</li>
          <li>Some settings must be set before the session starts.</li>
        </ol>''', 'Raising it further.') +
    scn('Platform', 'Senior', 'Submission standard',
        'Define how teams submit Spark jobs.',
        'standard?',
        '''<ul>
          <li>Cluster mode from the scheduler; versioned artifacts.</li>
          <li>Per-env properties files; no env settings in code.</li>
          <li>Event logs and history server for every job.</li>
        </ul>''', 'Ad-hoc commands from laptops.')
)
