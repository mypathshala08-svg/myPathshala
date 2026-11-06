import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='01-introduction', lesson='06-sparkcontext-sparkconf-and-sparkfiles', n='1.6', module_label='Module 1 · Start here',
    title='SparkContext, SparkConf and SparkFiles',
    desc='How PySpark connects to a cluster: SparkConf settings and precedence, the SparkContext inside every SparkSession, the one-context-per-process rule, shipping files with addFile and SparkFiles.get, shipping Python modules with addPyFile, and executor environment variables. Real Spark 4.3 cluster outputs.',
    og_desc='One SparkContext per process, a price list on every worker, and a module shipped with addPyFile: real Spark 4.3 outputs.',
    minutes=20, level='Beginner',
    lead='What is behind <code>SparkSession.builder</code>? We build a <b>SparkConf</b>, inspect the <b>SparkContext</b>, try to make a second one, and ship a file and a module to every worker with <b>SparkFiles</b> and <b>addPyFile</b>. <b>All outputs are real.</b>',
    chips=['One context per process', 'addFile + SparkFiles.get', 'addPyFile', 'Runs in your browser (Python)'])
MAIN = '''# A tiny SparkConf: settings with precedence (code > submit > defaults)
defaults = {"spark.app.name": "default", "spark.executor.memory": "1g"}
submit   = {"spark.master": "spark://spark-master:7077", "spark.executor.memory": "2g"}
in_code  = {"spark.app.name": "l16-context", "spark.executor.memory": "1g"}

final = {**defaults, **submit, **in_code}       # later wins
for k, v in sorted(final.items()):
    print(f"{k:24s} {v}")
'''
RUN = dict(heading='Run the code: configuration precedence', intro='<p>Which value wins? Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('final = {**defaults, **submit, **in_code}       # later wins', 'SparkConf in code overrides spark-submit.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Remove executor memory from in_code.', code=None),
        dict(label='2 · Predict first: parallelism', hint='<b>Predict first:</b> 2 workers × 2 cores.', code='print(2 * 2)\n'),
        dict(label='3 · Path', hint='Build an executor file path.', code='print("/".join(["$SPARK_HOME", "work", "app-20261106092444-0001", "0", "menu_prices.csv"]))\n'),
        dict(label='4 · GST', hint='Our shipped module.', code='def gst(a): return round(a * 1.05)\nprint(gst(90), gst(150))\n'),
        dict(label='5 · Spot the error', hint='Second context.', expect='error', code='raise ValueError("Cannot run multiple SparkContexts at once; existing SparkContext(app=l16-context)")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC', intro='<p>Works with local PySpark or the Docker cluster from Lesson 1.5. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Submit', cmd='docker exec spark-master spark-submit --master spark://spark-master:7077 /jobs/m14/l16_context.py', file='terminal', output='  sc.version              4.3.0\n  sc.defaultParallelism   4', note='Cluster.'),
           dict(title='2 · Ship a file', cmd='sc.addFile("menu_prices.csv"); SparkFiles.get("menu_prices.csv")', file='python', output='', note='Inside tasks.'),
           dict(title='3 · Ship code', cmd='spark-submit --py-files tiffingo_rules.py job.py', file='terminal', output='', note='Same as addPyFile.')])
TRACE = dict(heading='Settings step by step', intro='<p>Merge in order.</p>',
    code='final = {}\nfor layer in ({"m": "1g"}, {"m": "2g"}, {"m": "1g"}):\n    final.update(layer)\nprint(final)\n', notes={3: 'Last layer :: Code wins.'})
WORKED_INTRO = 'Three context decisions.'
EXAMPLES = [
    dict(level='b', tag='Context · start', title='Start a session', problem='<p>New script.</p>', inp='code',
         approach=['SparkSession.builder.appName(...).getOrCreate().', 'sc = spark.sparkContext if needed.', 'No master in code.'], code='print("spark = SparkSession.builder.appName(\\"report\\").getOrCreate()")\n', notes={1: 'Portable :: Same code local and cluster.'}, tryit='Step 2.'),
    dict(level='i', tag='Context · files', title='Lookup file on workers', problem='<p>Price list needed in a UDF.</p>', inp='file',
         approach=['addFile.', 'SparkFiles.get inside the task.', 'Load once per partition.'], code='print("sc.addFile(p); open(SparkFiles.get(\\"menu_prices.csv\\"))")\n', notes={1: 'Or broadcast :: Lesson 3.2.'}, tryit='Step 4.'),
    dict(level='a', tag='Context · config', title='Static vs runtime settings', problem='<p>Change executor memory mid-job.</p>', inp='config',
         approach=['Static: needs a new context.', 'Runtime SQL configs: spark.conf.set.', 'Plan at submit time.'], code='print({"static": "spark.executor.memory", "runtime": "spark.sql.shuffle.partitions"})\n', notes={1: 'Know which is which.'}, tryit='Scenario 3.')]
QUIZ = mix([
    dict(q='Beginner: The SparkSession contains…', options=['Many SparkContexts', 'One SparkContext', 'No context', 'A broker'], answer=1, why='spark.sparkContext.'),
    dict(q='Beginner: SparkConf holds…', options=['Data', 'Settings', 'Results', 'Logs'], answer=1, why='Key–value properties.'),
    dict(q='Beginner: A second SparkContext in one process…', options=['Works', 'Raises ValueError', 'Doubles speed', 'Restarts'], answer=1, why='Step 3.'),
    dict(q='Intermediate: SparkFiles.get returns…', options=['File contents', 'The local path of a shipped file', 'A URL', 'A DataFrame'], answer=1, why='Path.'),
    dict(q='Intermediate: Ship a helper module with…', options=['addFile', 'addPyFile', 'broadcast', 'cache'], answer=1, why='On sys.path.'),
    dict(q='Intermediate: spark.executorEnv.X is visible on…', options=['Driver only', 'Executors only', 'Both', 'Neither'], answer=1, why='Step 6.'),
    dict(q='Advanced: Highest precedence…', options=['spark-defaults.conf', 'spark-submit --conf', 'SparkConf in code', 'Environment'], answer=2, why='Code wins.'),
    dict(q='Advanced: Spark Connect clients ship files with…', options=['addFile', 'spark.addArtifacts', 'addPyFile', 'Nothing'], answer=1, why='No SparkContext.')])
REVISION = ['SparkConf → SparkContext → SparkSession; one context per process.', 'Lab: 4.3.0, defaultParallelism 4, second context ValueError.',
    'addFile + SparkFiles.get: file on every executor work dir.', 'addPyFile: ship modules; executorEnv for executor env vars.', 'Precedence: code > submit > defaults.']
FAQ = [('Do I need SparkContext for DataFrames?', 'No, use the SparkSession; the context is still there for RDDs, files and status.'),
    ('addFile or broadcast?', 'Broadcast for Python data you already have in the driver; addFile for files a library must open by path.'),
    ('Can I stop and recreate the context?', 'Yes: spark.stop(), then build again (needed to change static settings).'),
    ('What about --files?', 'spark-submit --files is the command-line equivalent of addFile.')]
PRACTICE_INTRO = 'Context programs.'
PROBLEMS = [
    dict(level='easy', title='Merge', stmt='Code overrides submit.', inp='dicts', code='print({**{"m": "2g"}, **{"m": "1g"}})\n', explain='1g.'),
    dict(level='easy', title='Parallelism', stmt='3 workers × 4 cores.', inp='ints', code='print(12)\n', explain='12.'),
    dict(level='easy', title='Name', stmt='File name from path.', inp='str', code='print("/w/app-1/0/menu_prices.csv".split("/")[-1])\n', explain='menu_prices.csv.'),
    dict(level='medium', title='Parse prices', stmt='CSV lines to dict.', inp='list', code='lines = ["item,price", "idli,45", "dosa,90"]\nprint({k: int(v) for k, v in (l.split(",") for l in lines[1:])})\n', explain='Lookup.'),
    dict(level='medium', title='GST', stmt='Apply 5%.', inp='list', code='print([round(a * 1.05) for a in (90, 150)])\n', explain='[94, 158].'),
    dict(level='medium', title='Static?', stmt='Classify settings.', inp='list', code='static = {"spark.executor.memory", "spark.executor.cores"}\nprint([s in static for s in ["spark.executor.memory", "spark.sql.shuffle.partitions"]])\n', explain='[True, False].'),
    dict(level='business', title='Copies', stmt='File copies on 50 executors.', inp='int', code='print(50)\n', explain='Once per executor.'),
    dict(level='business', title='Size check', stmt='100 MB file × 50 executors.', inp='ints', code='print(100 * 50, "MB moved")\n', explain='Use storage instead.')]
SCN_INTRO = 'Context interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“SparkContext vs SparkSession?”', 'Explain.', 'answer?', '<p>SparkSession (Spark 2+) is the single entry point for DataFrames and SQL; it creates and wraps one SparkContext, the driver’s connection to the cluster used for RDDs, files and job control.</p>', '“Same thing.”') +
    scn('Data', 'Mid-level', 'ModuleNotFoundError on executors', 'Works locally.', 'fix?', '<ul><li>addPyFile / --py-files, or --archives env.</li></ul>', 'pip install on driver.') +
    scn('Data', 'Mid-level', 'File not found in UDF', 'Path from laptop.', 'fix?', '<ul><li>addFile + SparkFiles.get, or storage path.</li></ul>', 'Hard-code /home/me/x.csv.') +
    scn('Platform', 'Senior', 'Config chaos', 'Settings differ per run.', 'fix?', '<ul><li>Precedence rules; keep master/memory in submit or defaults.</li></ul>', 'Hard-code everything.'))
