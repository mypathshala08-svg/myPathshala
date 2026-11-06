import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit2 import *
C = 'l87_profile.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('The Spark UI says a stage spent 29 seconds “running Python”. Which line of your Python function burned the time?',
    'The Spark UI cannot see inside Python. A <b>profiler</b> can. With one setting, Spark 4’s <b>UDF profiler</b> showed our UDF made 10.2 million generator calls; replacing it with built-in functions took the job from <b>29.5 s to 0.85 s</b>. Then we watched a running job from code with the <b>StatusTracker</b>: tasks done per stage, live, without opening the UI.',
    ['Profiling Python UDFs in Spark 4 (perf and memory).',
     'The classic RDD profiler and its limits.',
     'Tracking jobs and stages from code with StatusTracker and job groups.'])
cmap = concept_map('Concept map. Beginner: slow job, where time goes. Intermediate: UDF profiler, cProfile output, Spark UI vs profiler. Advanced: memory profiler, classic RDD profiler, StatusTracker, job groups, custom progress.',
    [[('ui', 'Spark UI', 'Lesson 8.6', B + '08-performance-tuning/06-spark-ui-troubleshooting/'), ('ud', 'Python UDFs', 'Lesson 6.6', B + '06-transformations/06-udfs/')],
     [('up', 'UDF profiler', 'spark 4', None), ('cp', 'cProfile stats', 'ncalls, tottime', None), ('fx', 'Fix with built-ins', '35×', None), ('rp', 'RDD profiler', 'classic', None)],
     [('mp', 'Memory profiler', 'memory_profiler', None), ('st', 'StatusTracker', 'jobs, stages', None), ('jg', 'Job groups', 'setJobGroup', None), ('cx', 'SparkContext', 'Lesson 1.6', B + '01-introduction/06-sparkcontext-sparkconf-and-sparkfiles/')]],
    [('ui', 'up'), ('ud', 'up'), ('up', 'cp'), ('cp', 'fx'), ('up', 'rp'), ('up', 'mp'), ('ui', 'st'), ('st', 'jg'), ('cx', 'st')],
    {'up', 'cp', 'fx', 'rp', 'mp', 'st', 'jg'},
    '<b>Builds on:</b> <a href="../06-spark-ui-troubleshooting/">8.6 Spark UI</a>, <a href="../../06-transformations/06-udfs/">6.6 UDFs</a>. <b>Next:</b> <a href="../../09-structured-streaming/01-streaming-concepts/">Module 9</a>.')
whw = why_how_where(
    'The Spark UI shows stages and tasks, not which Python line is slow. Long jobs also need progress reporting in schedulers, notebooks or custom dashboards.',
    'Set <code>spark.sql.pyspark.<wbr>udf.profiler</code> to <code>perf</code> (cProfile) or <code>memory</code> (memory_profiler); run the query; read the results with <code>spark.profile.show()</code> or <code>dump()</code>. For RDD code, the older <code>spark.python.profile=true</code> + <code>sc.show_profiles()</code>. For progress, <code>sc.statusTracker()</code> returns job and stage info; <code>sc.setJobGroup</code> labels jobs.',
    'Slow UDF investigations, code reviews before production, notebook progress bars, orchestration that reports progress or cancels a job group.',
    'Profiling adds overhead: use it on samples, not in production runs. StatusTracker is weakly consistent and keeps only recent jobs (spark.ui.retainedJobs).')

def prof(hl=-1):
    rows = [('genexpr', 10.2, 'red'), ('slow_band', 0.96, 'amber'), ('split', 0.13, 'blue')]
    o = t(176, 20, 'Profile of UDF: calls (millions) and tottime', 7.4)
    for k, (n, v, tn) in enumerate(rows):
        w = int(v / 10.2 * 220)
        o += t(10, 48 + k * 26, n, 7.6, 'ink', anchor='start', bold=True) + box(80, 36 + k * 26, max(w, 4), 18, 'acc' if k == hl else tn, rx=3)
    return o + t(80 + 220 + 30, 49, '10.2 M', 7.4, bold=True) + t(176, 120, 'job 29.5 s → 0.85 s after the fix', 7.6, bold=True)
scene_svg = scene('UDF profiler output: the generator expression was called 10.2 million times, the UDF slow_band 400 thousand times, split 400 thousand times; after replacing the UDF with built-in functions the job went from 29.5 to 0.85 seconds.', prof(0),
                  'The profiler points at the line: <tspan font-weight="700" class="s-acc">10.2 million calls</tspan>.')
dialogue = '''K> Sir, the band-classification UDF takes half a minute. The Spark UI just shows one long stage.
A> The UI stops at the Python worker. Turn on the UDF profiler: it runs cProfile inside the workers and brings the numbers back to you.
R> And our scheduler wants a progress bar for the nightly job. Do we scrape the UI?
A> No, use the StatusTracker from code. Let’s do both.'''

lv = '''
LEVELS> Profiling and tracking at three levels
L1> A stopwatch per cook
      <ul>
        <li>The restaurant board (Spark UI) shows which orders are late. To know why, you time each cook’s steps (profiler). The manager’s tablet shows live “4 of 8 dishes done” (StatusTracker).</li>
      </ul>
L2> The settings and calls
      <ul>
        <li><code>spark.conf.set("spark.sql.pyspark.udf.profiler", "perf")</code> (or <code>"memory"</code>, needs <code>memory_profiler</code>); run; <code>spark.profile.show(type="perf")</code>, <code>spark.profile.dump(path)</code>, <code>spark.profile.clear()</code>. Works for Python, pandas and Arrow UDFs, also with Spark Connect.</li>
        <li>Classic: <code>spark.python.profile=true</code> at startup, then <code>sc.show_profiles()</code> / <code>sc.dump_profiles(path)</code>; custom classes via <code>SparkContext(profiler_cls=…)</code> (BasicProfiler by default).</li>
        <li><code>st = sc.statusTracker()</code>: <code>getActiveJobsIds()</code>, <code>getActiveStageIds()</code>, <code>getJobIdsForGroup(g)</code>, <code>getJobInfo(id)</code> (status, stageIds), <code>getStageInfo(id)</code> (numTasks, numActiveTasks, numCompletedTasks, numFailedTasks).</li>
      </ul>
L3> Gotchas
      <ul>
        <li>On Python 3.12+ the classic profiler and the UDF profiler cannot run in the same session: we got <code>ValueError: tool 2 is already in use</code>. Use one at a time.</li>
        <li>cProfile columns: <i>ncalls</i>, <i>tottime</i> (inside the function), <i>cumtime</i> (including callees). Look for huge call counts first.</li>
        <li>Job groups also allow <code>sc.cancelJobGroup(g)</code>; <code>spark.addTag</code>/<code>interruptTag</code> do the same for Spark Connect.</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of one cProfile line: 10200000 calls, 1.034 seconds total time in the function itself, 0.000 per call, 1.034 cumulative, located at l87_profile.py line 11 in a generator expression.',
    t(16, 22, 'One line of the UDF profile (real)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('10200000', 'red', 1), ('1.034', 'amber', 2), ('0.000', 'card', 3), ('1.034', 'blue', 4), ('l87_profile.py:11(&lt;genexpr&gt;)', 'green', 5)]) +
    legend(16, 84, [(1, 'ncalls', 'how many times it ran'), (2, 'tottime', 'seconds inside this function only'), (3, 'percall', 'tottime ÷ ncalls'),
                    (4, 'cumtime', 'including everything it called'), (5, 'where', 'file:line(function)')], size=8, gap=15, w=90),
    h=172, caption='Sum of squares in a generator, 400,000 times: the real culprit.')
extra = '''

  <h3>Dissect a profile line</h3>
''' + DIS

types_html = table(['Tool', 'Shows', 'Enable', 'Read'], [
    ['UDF profiler (perf)', 'cProfile of Python/pandas/Arrow UDFs', 'spark.sql.pyspark.<wbr>udf.profiler=perf', 'spark.profile.show()'],
    ['UDF profiler (memory)', 'line-by-line memory', '…=memory (+ memory_profiler)', 'spark.profile.show(type="memory")'],
    ['Classic RDD profiler', 'cProfile per RDD', 'spark.python.profile=true (startup)', 'sc.show_profiles()'],
    ['StatusTracker', 'live job/stage progress', 'sc.statusTracker()', 'getJobInfo / getStageInfo'],
    ['Spark UI / REST', 'stages, tasks, spill', 'always on', 'port 4040 / history server'],
], minw=680)
warn = 'Profile on a sample, not the full production run: cProfile adds overhead per Python call. And remember StatusTracker answers can be empty for a moment (weak consistency) and old jobs disappear after spark.ui.retainedJobs.'

steps = [
    ('Step 1 · Profile a slow UDF',
     code('python', 'l87_profile.py', 'spark.conf.set("spark.sql.pyspark.udf.profiler", "perf")\nband = udf(slow_band, "string")\ndf.select(band("item")).groupBy(...).count().collect()\nspark.profile.show(type="perf")', sec('== 1)', '== 2)')),
     '29.5 s for 400,000 rows. 12.6 million Python calls; 10.2 million of them are the generator on line 11.'),
    ('Step 2 · Fix with built-ins',
     code('python', 'l87_profile.py', 'n = F.split("item", "-").getItem(1).cast("int")\nF.when(((n - 1) * n * (2 * n - 1) / 6) % 3 == 0, "hot").otherwise("cold")', sec('== 2)', '== 3)')),
     'A closed formula in Spark expressions: 0.85 s, about 35× faster, and no Python workers at all.'),
    ('Step 3 · Watch a job with StatusTracker',
     code('python', 'l87_profile.py', 'st = sc.statusTracker()\nsc.setJobGroup("nightly-report", "orders per item")   # in the worker thread\nfor j in st.getActiveJobsIds(): st.getJobInfo(j); st.getStageInfo(s)', sec('== 3)', '== 4)')),
     'Live progress from code: stage 8 went 0 → 1 → 4 of 8 tasks. The group lists all its jobs.'),
    ('Step 4 · The classic RDD profiler',
     code('python', 'l87_profile.py', 'SparkSession.builder.config("spark.python.profile", "true")…\nsc.parallelize(range(200_000), 2).map(lambda x: sum(range(x % 300))).count()\nsc.show_profiles()', sec('== 4)')),
     'Per-RDD cProfile output. It must be enabled at startup and cannot share a session with the UDF profiler on modern Python.'),
]
see = [term([('job took 29.49 s', RD), ('10200000 calls genexpr', Y)], size=7.0), term([('job took 0.85 s', G)], size=7.2),
       term([('stage 8: 1/8 → 4/8 done', G), ('group: [6, 5, 4]', W)], size=7.0), term([('Profile of RDD<id=1>', W), ('builtins.sum 0.363 s', Y)], size=7.0)]
B1 = [prof(0), prof(-1), prof(1), prof(2)]
B1 = [b + cap(c, '', tn, y=130, h=30) for b, c, tn in zip(B1, ['Hot spot found', '35× faster', 'Live progress', 'Classic profiler'], ['red', 'green', 'blue', 'violet'])]
two = anim_two('Profiling', 'Find the line, watch the job', 'Real outputs (local[2])', 'Inside the Python workers', see, B1, ['Profile.', 'Fix.', 'Track.', 'Classic.'], ['10.2 M.', '0.85 s.', '4/8.', 'RDD.'])
pe = peel('A profiled UDF, layer by layer', 'slow_band with the perf profiler. (Simplified.)',
    [('Config', ''), ('Worker', ''), ('cProfile', ''), ('Accumulate', ''), ('Collect', ''), ('Show', '')],
    [['Config', 'udf.profiler = perf', 'session setting', ''], ['Worker', 'Python worker runs UDF', 'wrapped by profiler', ''], ['cProfile', 'records every call', 'ncalls, tottime', 'overhead!'],
     ['Accumulate', 'stats per UDF id', 'sent back with results', ''], ['Collect', 'driver merges', 'all tasks', ''], ['Show', 'spark.profile.show()', 'sorted table', '']],
    ['Set.', 'Wrap.', 'Count.', 'Return.', 'Merge.', 'Read.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'UDF job doubled in time', 'After a code change. (Typical.)', ('UDF profiler', 'Compare profiles'), [
    ('Nightly job 10 → 20 min', 'new UDF version', 'Regression.', 'red'), ('Profile a 1% sample', 'perf', 'Measure.', 'blue'),
    ('json.loads called per row twice', 'hot spot', 'Cause.', 'amber'), ('Parse once / from_json', 'built-in', 'Fix.', 'green'),
    ('Back to 9 min', 'profile in CI sample', 'Guard.', 'green')], ['Slow.', 'Sample.', 'Hot spot.', 'Fix.', 'Guard.'], 'scenario-regress') + \
       five('Real-time scenario 2', 'Scheduler needs progress', 'Airflow task shows nothing for an hour. (Typical.)', ('StatusTracker', 'Report from code'), [
    ('Long Spark job', 'no visibility', 'Problem.', 'amber'), ('setJobGroup("nightly")', 'label work', 'Tag.', 'blue'),
    ('Thread polls StatusTracker', 'done/total tasks', 'Measure.', 'green'), ('Log % every minute', 'scheduler shows it', 'Visible.', 'green'),
    ('cancelJobGroup on timeout', 'clean stop', 'Control.', 'blue')], ['Blind.', 'Tag.', 'Poll.', 'Log.', 'Cancel.'], 'scenario-progress') + \
       five('Real-time scenario 3 · advanced', 'Executors run out of memory in a pandas UDF', 'OOM in Python worker. (Typical.)', ('Memory profiler', 'Line-by-line'), [
    ('Python worker killed', 'container memory', 'Fail.', 'red'), ('udf.profiler = memory', 'on a sample', 'Measure.', 'blue'),
    ('Line 12: +900 MiB', 'copying a DataFrame', 'Cause.', 'amber'), ('Process in place / iterator UDF', 'smaller batches', 'Fix.', 'green'),
    ('maxRecordsPerBatch', 'tune', 'Tune.', 'green')], ['OOM.', 'Profile.', 'Line.', 'Fix.', 'Tune.'], 'scenario-mem')
assemble(HERE, h2_story='Finding the slow line of Python', hook_html=hk,
    narration='TiffinGo’s band-classification job spends most of its time in a Python UDF. The Spark UI shows one long stage and nothing more.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Profiling and tracking from code',
    formal='<b>Profiling</b> measures where a program spends time or memory. PySpark provides a session-level <b>UDF profiler</b> (Spark 4.0+; <code>spark.sql.pyspark.<wbr>udf.profiler</code> = perf or memory) that runs cProfile or memory_profiler inside Python workers and aggregates results on the driver, and an older RDD profiler enabled with <code>spark.python.profile</code>. The <b>StatusTracker</b> is a low-level API exposing weakly consistent information about active jobs and stages.',
    simple='A profiler tells you which Python lines are slow inside Spark; the StatusTracker tells your program how far a running job has got.',
    term_rows=[('Profiler', 'Measures time/memory per function.'), ('cProfile', 'Python’s built-in profiler.'), ('ncalls', 'Number of calls.'), ('tottime', 'Time inside function.'), ('cumtime', 'Including callees.'), ('StatusTracker', 'Job/stage progress API.'), ('Job group', 'Label for related jobs.'), ('BasicProfiler', 'Default classic profiler.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('The Spark UI shows slow Python lines.', 'It stops at the worker; use the profiler.', 'Step 1.'),
               ('UDFs are fine if they are short.', '10.2 M hidden calls in one line.', 'Step 1.'),
               ('Progress needs the UI.', 'StatusTracker from code.', 'Step 3.')],
    exam='“How do you profile PySpark?” Spark 4 UDF profiler (spark.sql.pyspark.<wbr>udf.profiler = perf or memory; spark.profile.show or dump); classic spark.python.profile with sc.show_profiles (BasicProfiler, cProfile); StatusTracker (getJobInfo, getStageInfo, getActiveJobsIds) and job groups; fix hot spots with built-in functions.',
    types_h2='Profiling and tracking tools', types_html=types_html, warn=warn,
    steps_h2='Profile, fix, track', steps_intro='All outputs are real: PySpark 4.3.0, local[2], Python 3.13.',
    steps=steps, two=two, peel_intro='Now peel a profiled UDF.', peel_html=pe,
    scen_intro='Three live scenarios: a regression, a progress bar, and a memory blow-up.', scen=scen,
    uc_h2='Profiling at work', ucs=[uc_('udf', 'UDFs', 'red', '1. Slow UDFs', 'Find the hot line.', ['UDF', '*perf', 'Fix']),
        uc_('mem', 'memory', 'amber', '2. Python OOMs', 'Memory profiler.', ['pandas UDF', '*memory', 'Fix']),
        uc_('prog', 'progress', 'blue', '3. Progress reporting', 'StatusTracker + job groups.', ['Job', '*poll', 'Log']),
        uc_('ci', 'CI', 'green', '4. Performance checks', 'Profile samples in CI.', ['PR', '*profile', 'Gate'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../../06-transformations/06-udfs/">6.6 UDFs</a>.')
