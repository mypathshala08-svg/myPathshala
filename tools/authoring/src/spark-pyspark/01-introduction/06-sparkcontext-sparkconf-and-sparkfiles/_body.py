import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit2 import *
C = 'l16_context.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('Every PySpark program has one object that talks to the cluster. You rarely create it yourself any more, so what is it, and what breaks if you make two?',
    'The <b>SparkContext</b>. Since Spark 2 it hides inside the <b>SparkSession</b>, but it still owns the connection to the master, the executors, shipped files and Python modules. In our lab, a second SparkContext raised <code>ValueError: Cannot run multiple SparkContexts at once</code>; a CSV shipped with <code>addFile</code> appeared on both workers at <code>$SPARK_HOME/work/app-…/menu_prices.csv</code>; and an environment variable reached the executors but not the driver.',
    ['SparkConf, SparkContext and SparkSession: who creates whom.',
     'Shipping files (SparkFiles) and Python modules (addPyFile) to executors.',
     'The parameters and settings you will meet in old code and interviews.'])
cmap = concept_map('Concept map. Beginner: driver, cluster, entry point. Intermediate: SparkConf, SparkContext, SparkSession, configuration precedence. Advanced: addFile and SparkFiles, addPyFile, executor environment, one context per process.',
    [[('ar', 'Architecture', 'Lesson 1.3', B + '01-introduction/03-spark-architecture/'), ('ep', 'Entry point', 'driver program', None)],
     [('cf', 'SparkConf', 'settings', None), ('sc', 'SparkContext', 'cluster connection', None), ('ss', 'SparkSession', 'Lesson 4.1', B + '04-dataframes/01-sparksession-and-dataframes/'), ('pr', 'Precedence', 'code > submit > defaults', None)],
     [('sf', 'SparkFiles', 'addFile / get', None), ('pf', 'addPyFile', 'ship modules', None), ('ev', 'executorEnv', 'env vars', None), ('pk', 'Packaging', 'Lesson 11.1', B + '11-spark-in-production/01-spark-submit-and-deploy-modes/')]],
    [('ar', 'ep'), ('ep', 'cf'), ('cf', 'sc'), ('sc', 'ss'), ('cf', 'pr'), ('sc', 'sf'), ('sc', 'pf'), ('cf', 'ev'), ('pf', 'pk')],
    {'ep', 'cf', 'sc', 'ss', 'pr', 'sf', 'pf', 'ev'},
    '<b>Builds on:</b> <a href="../03-spark-architecture/">1.3 Architecture</a>, <a href="../05-install-pyspark-and-a-spark-cluster/">1.5 Install</a>. <b>Next:</b> <a href="../../02-rdds/01-what-is-an-rdd/">2.1 RDDs</a>.')
whw = why_how_where(
    'Every job needs settings (app name, master, memory) and a live connection to the cluster. Many jobs also need a lookup file or a helper module on every executor.',
    'You describe settings in a <b>SparkConf</b>; <code>SparkSession.builder…getOrCreate()</code> creates (or reuses) one <b>SparkContext</b> that registers with the master and gets executors. <code>sc.addFile</code> copies a file to every executor’s work folder, where <code>SparkFiles.get(name)</code> finds it; <code>sc.addPyFile</code> does the same for Python modules and puts them on the path.',
    'Every PySpark program; small lookup files (price lists, ML models, GeoIP databases) and shared helper code on clusters; reading old RDD-era code; interviews.',
    'One active SparkContext per Python process. Big files belong in storage (S3, HDFS) or a broadcast, not addFile. For many dependencies use packaged environments (Lesson 11.1).')

def ctx(hl=-1):
    parts = [('SparkConf', 'settings', 'card'), ('SparkContext', 'connection', 'blue'), ('SparkSession', 'DataFrames, SQL', 'green')]
    o = ''
    for k, (n, d, tn) in enumerate(parts):
        o += box(8 + k * 118, 30, 104, 46, 'acc' if k == hl else tn, rx=8) + t(60 + k * 118, 50, n, 8, bold=True) + t(60 + k * 118, 66, d, 6.8)
        if k < 2: o += arrow(112 + k * 118, 53, 126 + k * 118, 53)
    o += box(126, 92, 104, 30, 'violet' if hl != 3 else 'acc', rx=6) + t(178, 111, 'files + modules', 7.2, bold=True) + arrow(178, 76, 178, 92)
    return o + t(176, 18, 'driver process', 7.4)
scene_svg = scene('Inside the driver: a SparkConf holds settings, the SparkContext uses them to connect to the cluster and ship files and modules, and the SparkSession wraps the SparkContext for DataFrames and SQL.', ctx(),
                  'SparkSession is the front door; <tspan font-weight="700" class="s-acc">SparkContext</tspan> is the engine room.')
dialogue = '''K> Sir, old tutorials start with <code>sc = SparkContext(...)</code>, ours start with <code>SparkSession.builder</code>. Which one is right?
A> Both. The SparkSession creates a SparkContext for you and keeps it in <code>spark.sparkContext</code>. You still use the context for files, modules and RDDs.
R> Can a job have two of them, one per team?
A> No, one per process. Let’s try it, and also ship a price list and a Python module to the workers.'''

lv = '''
LEVELS> SparkConf, SparkContext and SparkFiles at three levels
L1> Booking a kitchen
      <ul>
        <li>The order form (SparkConf) says what you need. The booking (SparkContext) gets you the kitchen and staff. The restaurant manager (SparkSession) gives you the menu and recipes on top. If every cook needs the price list, you photocopy it to each station (addFile).</li>
      </ul>
L2> The API
      <ul>
        <li><code>SparkConf().setAppName(…).setMaster(…).set(key, value)</code>, <code>conf.get(key)</code>, <code>conf.getAll()</code>; chainable.</li>
        <li><code>SparkSession.builder.config(conf=conf).getOrCreate()</code>; <code>spark.sparkContext</code> exposes <code>version, master, appName, applicationId, defaultParallelism, pythonVer, uiWebUrl</code>.</li>
        <li><code>sc.addFile(path)</code> + <code>SparkFiles.get(name)</code> / <code>SparkFiles.getRootDirectory()</code>; <code>sc.addPyFile(path)</code> for .py/.zip/.egg; <code>spark.executorEnv.NAME</code> for environment variables.</li>
      </ul>
L3> Details that matter
      <ul>
        <li>Precedence: values set in code on SparkConf beat <code>spark-submit --conf</code>, which beats <code>spark-defaults.conf</code>. Leave <code>master</code> out of code so the same script runs locally and on clusters.</li>
        <li>Old <code>SparkContext(master, appName, sparkHome, pyFiles, environment, batchSize, serializer, conf, gateway, jsc, profiler_cls)</code> parameters still exist; <code>serializer</code> and <code>profiler_cls</code> appear in Lessons 3.4 and 8.7.</li>
        <li>Spark Connect clients (Lesson 11.3) have no SparkContext at all: use <code>spark.addArtifacts</code> instead of addFile/addPyFile there.</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of the executor path of a shipped file: SPARK_HOME, work, the application id app-20261106092444-0001, the executor id 0 or 1, and the file name menu_prices.csv.',
    t(16, 22, 'Where SparkFiles.get() found the file on a worker (real)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('$SPARK_HOME', 'card', 1), ('/work', 'blue', 2), ('/app-20261106092444-0001', 'violet', 3), ('/0', 'amber', 4), ('/menu_prices.csv', 'green', 5)]) +
    legend(16, 84, [(1, 'Spark home', 'on the worker machine'), (2, 'Work dir', 'per-application scratch space'), (3, 'Application id', 'same as sc.applicationId'),
                    (4, 'Executor id', 'executor 0 on worker 1, 1 on worker 2'), (5, 'File', 'copied from the driver by addFile')], size=8, gap=15, w=90),
    h=172, caption='Never hard-code this path: always ask SparkFiles.get().')
extra = '''

  <h3>Dissect a SparkFiles path</h3>
''' + DIS

types_html = table(['Object', 'Created by', 'You use it for'], [
    ['SparkConf', 'you', 'app name, memory, any spark.* setting'], ['SparkContext (sc)', 'getOrCreate (one per process)', 'RDDs, files, modules, job groups, status'],
    ['SparkSession (spark)', 'SparkSession.builder', 'DataFrames, SQL, catalog'], ['SparkFiles', 'class methods only', 'find files shipped with addFile'],
], minw=560) + table(['Ship…', 'API', 'Lands where'], [
    ['a data file', 'sc.addFile / --files', 'executor work dir, find with SparkFiles.get'], ['a .py / .zip module', 'sc.addPyFile / --py-files', 'executor work dir, on sys.path'],
    ['a whole environment', '--archives env.tar.gz#env (Lesson 11.1)', 'unpacked per executor'], ['an env variable', 'spark.executorEnv.NAME', 'executor processes only'],
], minw=560)
warn = 'Do not create SparkContext(...) in library code or notebooks that may already have one: use SparkSession.builder.getOrCreate() (or SparkContext.getOrCreate()). And never rely on executor files from addFile being present on the driver path: on the driver use SparkFiles.getRootDirectory().'

steps = [
    ('Step 1 · SparkConf',
     code('python', 'l16_context.py', 'conf = (SparkConf().setAppName("l16-context").set("spark.executor.memory", "1g")\n        .set("spark.executorEnv.TIFFINGO_CITY", "Mumbai"))\nfor k, v in sorted(conf.getAll()): print(k, v)', sec('== 1)', '== 2)')),
     'Only what we set appears; the master URL came from <code>spark-submit --master spark://spark-master:7077</code>.'),
    ('Step 2 · The SparkContext inside the session',
     code('python', 'l16_context.py', 'spark = SparkSession.builder.config(conf=conf).getOrCreate()\nsc = spark.sparkContext\nprint(sc.version, sc.master, sc.applicationId, sc.defaultParallelism, sc.uiWebUrl)', sec('== 2)', '== 3)')),
     'Version 4.3.0 on our standalone cluster; 2 workers × 2 cores give defaultParallelism 4.'),
    ('Step 3 · One per process',
     code('python', 'l16_context.py', 'SparkContext(conf=SparkConf().setAppName("second"))\nSparkContext.getOrCreate() is sc', sec('== 3)', '== 4)')),
     'A second context is refused; getOrCreate returns the existing one.'),
    ('Step 4 · SparkFiles',
     code('python', 'l16_context.py', 'sc.addFile("/jobs/m14/menu_prices.csv")\ndef price_part(rows):\n    prices = dict(l.strip().split(",") for l in open(SparkFiles.get("menu_prices.csv")).readlines()[1:])\n    …\norders.mapPartitions(price_part).collect()', sec('== 4)', '== 5)')),
     'Each executor read its own copy: worker 1 priced idli and dosa, worker 2 thali and vada. The driver keeps its copy in a temporary userFiles folder.'),
    ('Step 5 · addPyFile',
     code('python', 'l16_context.py', 'sc.addPyFile("/jobs/m14/tiffingo_rules.py")\ndef with_gst(x):\n    import tiffingo_rules           # import inside the task\n    return (x[0], x[1], tiffingo_rules.gst(x[1]))', sec('== 5)', '== 6)')),
     'Our 5% GST rule ran on the executors without installing anything on the workers.'),
    ('Step 6 · Executor environment',
     code('python', 'l16_context.py', '.set("spark.executorEnv.TIFFINGO_CITY", "Mumbai")\nsc.parallelize([0], 1).map(lambda _: os.environ.get("TIFFINGO_CITY")).collect()', sec('== 6)')),
     'Executors see it; the driver does not. Use it for executor-side settings only.'),
]
see = [term([('spark.app.name = l16-context', W), ('spark.executor.memory = 1g', W)], size=7.0), term([('4.3.0 · spark://spark-master:7077', G), ('defaultParallelism 4', W)], size=7.0),
       term([('ValueError: Cannot run multiple', RD), ('SparkContexts at once', RD)], size=7.0), term([('spark-worker-1 … dosa 270', G), ('spark-worker-2 … thali 150', G)], size=7.0),
       term([("('idli', 90, 94)", G), ("('thali', 150, 158)", G)], size=7.0), term([('executors: Mumbai', G), ('driver: None', Y)], size=7.2)]
B1 = [ctx(0), ctx(1), ctx(1), ctx(3), ctx(3), ctx(0)]
B1 = [b + cap(c, '', tn, y=130, h=30) for b, c, tn in zip(B1, ['Settings', 'One context', 'Second refused', 'File on every executor', 'Module on every executor', 'Env on executors'], ['blue', 'blue', 'red', 'green', 'green', 'amber'])]
two = anim_two('SparkContext and SparkFiles', 'Settings, context, shipping', 'Real outputs from the cluster', 'Inside the driver', see, B1, ['Conf.', 'Context.', 'One only.', 'addFile.', 'addPyFile.', 'Env.'], ['Set.', 'Connect.', 'Refuse.', 'Ship.', 'Import.', 'Executors.'])
pe = peel('One shipped file, layer by layer', 'menu_prices.csv with addFile. (Simplified.)',
    [('addFile', ''), ('Driver server', ''), ('Task starts', ''), ('Fetch', ''), ('get()', ''), ('Read', '')],
    [['addFile', 'driver registers', 'menu_prices.csv', ''], ['Driver server', 'file served by', 'driver’s file server', ''], ['Task starts', 'executor sees', 'new file in task info', ''],
     ['Fetch', 'downloads once', 'to work/app-…/0/', 'cached per executor'], ['get()', 'SparkFiles.get', 'returns local path', ''], ['Read', 'open() in Python', 'build price dict', '']],
    ['Register.', 'Serve.', 'Notice.', 'Download.', 'Locate.', 'Use.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Every executor needs a model file', 'A 20 MB fraud model. (Typical.)', ('addFile + mapPartitions', 'Load once per partition'), [
    ('Model on the driver', 'tasks need it', 'Problem.', 'blue'), ('sc.addFile(model.pkl)', 'copied once per executor', 'Ship.', 'green'),
    ('mapPartitions', 'load with SparkFiles.get', 'Once per partition.', 'green'), ('Score rows', 'no driver round trips', 'Fast.', 'green'),
    ('Big models → storage', 'S3/HDFS path instead', 'Scale.', 'blue')], ['Need.', 'Ship.', 'Load.', 'Score.', 'Scale.'], 'scenario-model') + \
       five('Real-time scenario 2', 'Works locally, fails on cluster', 'ModuleNotFoundError on executors. (Typical.)', ('addPyFile / --py-files', 'Ship your code'), [
    ('import helpers in a UDF', 'local OK', 'Hidden.', 'blue'), ('On cluster: ModuleNotFoundError', 'executors lack it', 'Fail.', 'red'),
    ('sc.addPyFile("helpers.zip")', 'or --py-files', 'Ship.', 'green'), ('Third-party libs?', '--archives venv (11.1)', 'Bigger.', 'amber'),
    ('Same code everywhere', 'reproducible', 'Done.', 'blue')], ['Import.', 'Fail.', 'Ship.', 'Env.', 'Done.'], 'scenario-module') + \
       five('Real-time scenario 3 · advanced', 'Notebook says “multiple SparkContexts”', 'Shared notebook kernel. (Typical.)', ('getOrCreate', 'Reuse the active context'), [
    ('Cell creates SparkContext()', 'kernel already has one', 'Error.', 'red'), ('Use getOrCreate()', 'reuse', 'Fix.', 'green'),
    ('Need new settings?', 'stop() then build', 'Restart.', 'amber'), ('Static configs', 'only at start (e.g. executor memory)', 'Know.', 'blue'),
    ('Runtime SQL configs', 'spark.conf.set any time', 'Flexible.', 'green')], ['Error.', 'Reuse.', 'Stop.', 'Static.', 'Runtime.'], 'scenario-notebook')
assemble(HERE, h2_story='The object behind every PySpark job', hook_html=hk,
    narration='Kabir copied a 2017 tutorial that starts with SparkContext, while the course uses SparkSession. He also needs a price list on every worker.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='SparkConf, SparkContext and SparkFiles',
    formal='<b>SparkConf</b> holds key–value Spark properties for an application. The <b>SparkContext</b> is the driver-side connection to a cluster manager: it requests executors, schedules jobs, and distributes files (<code>addFile</code>) and Python dependencies (<code>addPyFile</code>); only one may be active per process. The <b>SparkSession</b> wraps a SparkContext for the DataFrame and SQL APIs. <b>SparkFiles</b> resolves local paths of files distributed with <code>addFile</code>.',
    simple='SparkConf is your settings list, SparkContext is the live link to the cluster, and SparkSession is the friendly front door built on it. SparkFiles tells each worker where its copy of a shipped file is.',
    term_rows=[('SparkConf', 'Settings object.'), ('SparkContext', 'Cluster connection (sc).'), ('SparkSession', 'DataFrame/SQL entry point.'), ('getOrCreate', 'Reuse or create.'), ('addFile', 'Ship a file.'), ('SparkFiles.get', 'Local path on a worker.'), ('addPyFile', 'Ship Python code.'), ('executorEnv', 'Env vars for executors.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('SparkContext is obsolete.', 'It lives inside every SparkSession.', 'Step 2.'),
               ('You can open one context per team.', 'One per process.', 'Step 3.'),
               ('Env vars set in Spark reach the driver.', 'executorEnv is executors only.', 'Step 6.')],
    exam='“SparkContext vs SparkSession?” SparkSession (2.0+) is the unified entry point wrapping one SparkContext; SparkConf holds settings (code > submit > defaults); addFile + SparkFiles.get for data files, addPyFile/--py-files for code; one active context per process.',
    types_h2='Objects and shipping', types_html=types_html, warn=warn,
    steps_h2='Context, files and modules on a cluster', steps_intro='All outputs are real: Spark 4.3.0 standalone cluster (1 master, 2 workers), job submitted with spark-submit.',
    steps=steps, two=two, peel_intro='Now peel one shipped file.', peel_html=pe,
    scen_intro='Three live scenarios: a model file, a missing module, and a notebook error.', scen=scen,
    uc_h2='Where you meet them', ucs=[uc_('look', 'lookups', 'blue', '1. Small lookup files', 'Prices, holidays, GeoIP.', ['File', '*addFile', 'Every task']),
        uc_('ml', 'models', 'violet', '2. ML model files', 'Score inside mapPartitions.', ['Model', '*SparkFiles', 'Predictions']),
        uc_('code', 'code', 'green', '3. Shared helper code', 'addPyFile / --py-files.', ['Module', '*ship', 'Import']),
        uc_('legacy', 'legacy', 'amber', '4. Reading old code', 'sc = SparkContext(conf=…).', ['Old job', '*understand', 'Migrate'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../03-spark-architecture/">1.3 Architecture</a>.')
