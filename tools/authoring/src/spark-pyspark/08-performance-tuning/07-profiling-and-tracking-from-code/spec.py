import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='08-performance-tuning', lesson='07-profiling-and-tracking-from-code', n='8.7', module_label='Module 8 · Performance tuning',
    title='Profiling and tracking from code',
    desc='Find slow Python inside Spark: the Spark 4 UDF profiler (perf and memory), reading cProfile output, the classic RDD profiler (spark.python.profile, BasicProfiler), and tracking running jobs and stages from code with StatusTracker and job groups. Real PySpark 4.3 lab: a UDF profiled and fixed from 29.5 s to 0.85 s.',
    og_desc='10.2 million hidden calls found by the Spark 4 UDF profiler, and a job watched live with StatusTracker.',
    minutes=20, level='Advanced',
    lead='Which Python line makes your Spark job slow? We turn on the <b>UDF profiler</b>, fix the hot spot, use the <b>classic profiler</b>, and watch a job live with <b>StatusTracker</b>. <b>All outputs are real.</b>',
    chips=['29.5 s → 0.85 s', 'spark.profile.show', 'StatusTracker', 'Runs in your browser (Python)'])
MAIN = '''# Profile a slow function with cProfile (what the UDF profiler does in each worker)
import cProfile, pstats, io

def slow_band(item):
    n = int(item.split("-")[1])
    return "hot" if sum(i * i for i in range(n)) % 3 == 0 else "cold"

pr = cProfile.Profile(); pr.enable()
for k in range(20000):
    slow_band(f"item-{k % 50}")
pr.disable()
s = io.StringIO(); pstats.Stats(pr, stream=s).sort_stats("tottime").print_stats(4)
print(s.getvalue()[:900])
'''
RUN = dict(heading='Run the code: profile a function', intro='<p>The same cProfile output the UDF profiler collects. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    return "hot" if sum(i * i for i in range(n)) % 3 == 0 else "cold"', 'The generator runs n times per row.'), ('s = io.StringIO(); pstats.Stats(pr, stream=s).sort_stats("tottime").print_stats(4)', 'Sort by tottime.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Then use the formula instead.', code=None),
        dict(label='2 · Predict first: speed-up', hint='<b>Predict first:</b> 29.49 ÷ 0.85.', code='print(round(29.49 / 0.85))\n'),
        dict(label='3 · Formula', hint='Sum of squares 0..n-1.', code='n = 10\nprint(sum(i * i for i in range(n)), (n - 1) * n * (2 * n - 1) // 6)\n'),
        dict(label='4 · Progress', hint='4 of 8 tasks.', code='print(f"{4 / 8:.0%}")\n'),
        dict(label='5 · Spot the error', hint='Two profilers at once.', expect='error', code='raise ValueError("tool 2 is already in use")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC', intro='<p>PySpark 4.x. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Turn on', cmd='spark.conf.set("spark.sql.pyspark.udf.profiler", "perf")', file='python', output='', note='Or "memory".'),
           dict(title='2 · Show', cmd='spark.profile.show(type="perf")', file='python', output='12600000 function calls in 11.592 seconds', note='After running the query.'),
           dict(title='3 · Track', cmd='st = spark.sparkContext.statusTracker(); st.getActiveJobsIds()', file='python', output='[5]', note='While a job runs.')])
TRACE = dict(heading='Progress step by step', intro='<p>Done ÷ total.</p>',
    code='num_tasks, done = 8, 4\nprint(f"{done}/{num_tasks} = {done / num_tasks:.0%}")\n', notes={2: 'getStageInfo :: numCompletedTasks.'})
WORKED_INTRO = 'Three profiling decisions.'
EXAMPLES = [
    dict(level='b', tag='Profile · start', title='First profile', problem='<p>One slow UDF.</p>', inp='steps',
         approach=['Sample the data.', 'udf.profiler = perf.', 'spark.profile.show().'], code='print(["sample", "perf", "show"])\n', notes={1: 'Cheap insight.'}, tryit='Step 1.'),
    dict(level='i', tag='Profile · fix', title='Replace a UDF', problem='<p>Hot spot is arithmetic.</p>', inp='rewrite',
         approach=['Express with F functions.', 'No Python worker.', 'Re-measure.'], code='print("F.when(expr % 3 == 0, ...)")\n', notes={1: '35× in lab.'}, tryit='Step 2.'),
    dict(level='a', tag='Track · groups', title='Cancel by group', problem='<p>Stop a runaway report.</p>', inp='api',
         approach=['setJobGroup("report", ...).', 'cancelJobGroup("report").', 'Connect: addTag / interruptTag.'], code='print("sc.cancelJobGroup(\\"nightly-report\\")")\n', notes={1: 'Clean stop.'}, tryit='Scenario 2.')]
QUIZ = mix([
    dict(q='Beginner: The Spark UI shows…', options=['Each Python line', 'Stages and tasks', 'Source code', 'Nothing'], answer=1, why='Not inside Python.'),
    dict(q='Beginner: Spark 4 UDF profiler is enabled with…', options=['spark.python.profile', 'spark.sql.pyspark.udf.profiler', 'spark.ui.enabled', 'cProfile.run'], answer=1, why='perf | memory.'),
    dict(q='Beginner: ncalls means…', options=['Seconds', 'Number of calls', 'Memory', 'Rows'], answer=1, why='Count.'),
    dict(q='Intermediate: Our fix made the job…', options=['2× faster', 'about 35× faster', 'slower', 'same'], answer=1, why='29.5 → 0.85 s.'),
    dict(q='Intermediate: getStageInfo gives…', options=['Source code', 'numTasks and numCompletedTasks', 'Logs', 'Schema'], answer=1, why='Progress.'),
    dict(q='Intermediate: Classic RDD profiler is enabled…', options=['Any time', 'At startup with spark.python.profile', 'In SQL', 'Never'], answer=1, why='Static.'),
    dict(q='Advanced: Both profilers in one session on Python 3.12+…', options=['Fine', 'ValueError: tool 2 is already in use', 'Faster', 'Ignored'], answer=1, why='Lab note.'),
    dict(q='Advanced: StatusTracker is…', options=['Strongly consistent', 'Weakly consistent, recent jobs only', 'Historical forever', 'A UI'], answer=1, why='retainedJobs.')])
REVISION = ['UDF profiler: spark.sql.pyspark.udf.profiler = perf | memory; spark.profile.show/dump.', 'Lab: 12.6 M calls, genexpr 10.2 M; built-ins 29.5 s → 0.85 s.',
    'Classic: spark.python.profile=true + sc.show_profiles (BasicProfiler).', 'StatusTracker: active jobs, job info, stage info; job groups.', 'Do not run both profilers together; profile samples.']
FAQ = [('Does the profiler work with pandas UDFs?', 'Yes, perf and memory profiling cover Python, pandas and Arrow UDFs.'),
    ('Where do I see memory results?', 'spark.profile.show(type="memory") after installing memory_profiler on the workers.'),
    ('Is StatusTracker the same as the REST API?', 'It reads the same scheduler state from inside the driver; the REST API serves it over HTTP.'),
    ('Can I profile the driver code?', 'Yes, with normal cProfile; the Spark profilers are for code running on executors.')]
PRACTICE_INTRO = 'Profiling programs.'
PROBLEMS = [
    dict(level='easy', title='Ratio', stmt='29.49 / 0.85.', inp='floats', code='print(round(29.49 / 0.85, 1))\n', explain='~34.7×.'),
    dict(level='easy', title='Share', stmt='10.2 of 12.6 M calls.', inp='floats', code='print(round(10.2 / 12.6 * 100), "%")\n', explain='81%.'),
    dict(level='easy', title='Progress', stmt='3 of 12 tasks.', inp='ints', code='print(f"{3 / 12:.0%}")\n', explain='25%.'),
    dict(level='medium', title='Top function', stmt='Max tottime.', inp='dict', code='t = {"genexpr": 1.034, "slow_band": 0.961, "split": 0.125}\nprint(max(t, key=t.get))\n', explain='genexpr.'),
    dict(level='medium', title='Formula check', stmt='Compare loop and formula.', inp='int', code='n = 37\nprint(sum(i * i for i in range(n)) == (n - 1) * n * (2 * n - 1) // 6)\n', explain='True.'),
    dict(level='medium', title='ETA', stmt='Remaining time.', inp='floats', code='done, total, secs = 4, 8, 20\nprint(secs / done * (total - done), "s left")\n', explain='20 s.'),
    dict(level='business', title='Cost saved', stmt='Nightly 30 min → 1 min.', inp='ints', code='print(29 * 30, "cluster minutes/month")\n', explain='870.'),
    dict(level='business', title='Sample size', stmt='1% of 400M rows.', inp='ints', code='print(400_000_000 // 100)\n', explain='4M.')]
SCN_INTRO = 'Profiling interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“How do you find a slow UDF?”', 'Explain.', 'answer?', '<p>Use the UDF profiler (spark.sql.pyspark.udf.profiler=perf) on a sample, read spark.profile.show(), find the function with the most calls/time, and replace it with built-in functions or vectorized UDFs.</p>', '“Add executors.”') +
    scn('Data', 'Mid-level', 'Profiler error', 'tool 2 already in use.', 'fix?', '<ul><li>Do not enable classic and UDF profilers together.</li></ul>', 'Downgrade Spark.') +
    scn('Platform', 'Mid-level', 'Progress for jobs', 'Scheduler blind.', 'how?', '<ul><li>StatusTracker polling, job groups, logs.</li></ul>', 'Screen-scrape UI.') +
    scn('Data', 'Senior', 'Python OOM', 'pandas UDF dies.', 'diagnose?', '<ul><li>Memory profiler on sample, batch size, iterator UDFs.</li></ul>', 'Double executor memory blindly.'))
