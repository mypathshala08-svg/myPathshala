import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='08-performance-tuning', lesson='06-spark-ui-troubleshooting', n='8.6',
    module_label='Module 8 · Performance tuning',
    title='Spark UI troubleshooting',
    desc='Troubleshooting with the Spark UI using real Spark 4.3.0 screenshots: the SQL / DataFrame tab with named jobs, the plan graph with per-operator time (Sort 8.0 s after an Exchange of 6,000,000 rows), a skewed stage (median 2 s, max 5 s, one task reading 4.2M records) and a spilling stage (even tasks, 184 MiB spill each), plus a symptom-to-cause table, the History Server and the REST API.',
    og_desc='Real Spark UI screenshots of a skewed stage and a spilling stage: how to read the SQL tab, plan graph and task summary to find the cause.',
    minutes=28, level='Intermediate → Advanced',
    lead='Most slow Spark jobs can be diagnosed in minutes from the <b>Spark UI</b>. This lesson follows one path, SQL tab → plan graph → slowest stage → task summary, on <b>real screenshots</b> of a skewed window and a spilling sort, and maps each metric pattern to its cause. <b>All outputs are real</b> (Spark 4.3.0).',
    chips=['Spark 4.3.0', 'Real UI screenshots', 'Symptom → cause', 'Runs in your browser (Python)'],
)

MAIN = '''# Diagnose a stage from its task summary (simplified rules)
stage = {"tasks": 4, "dur_med": 2.0, "dur_max": 5.0,
         "rec_med": 636000, "rec_max": 4197000,
         "spill_tasks": 1, "gc_pct": 2}

def diagnose(s):
    found = []
    if s["dur_max"] > 2 * s["dur_med"] and s["rec_max"] > 3 * s["rec_med"]:
        found.append("skew: one task holds most records (8.3)")
    if s["spill_tasks"] == s["tasks"]:
        found.append("every task spills: tasks too big (8.4)")
    if s["tasks"] > 5000 and s["dur_med"] < 0.1:
        found.append("too many tiny tasks (8.1)")
    if s["gc_pct"] > 10:
        found.append("high GC: memory pressure (8.4)")
    return found or ["looks healthy"]

print(diagnose(stage))
'''
RUN = dict(
    heading='Run the code: diagnosing a stage',
    intro='<p>Rules of thumb that turn task-summary numbers into a cause. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    if s["dur_max"] > 2 * s["dur_med"] and s["rec_max"] > 3 * s["rec_med"]:', 'Skew: the slowest task also read far more data than the median task.'),
        ('    if s["spill_tasks"] == s["tasks"]:', 'Spill in every task (not just one) points to task size or memory, not skew.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>: the numbers are from our window stage screenshot.', code=None),
        dict(label='2 · Predict first: the sort stage', hint='<b>Predict first:</b> what does the sort stage show?',
             code='''s = {"tasks": 4, "dur_med": 1.6, "dur_max": 1.6, "rec_med": 1350379, "rec_max": 1361305, "spill_tasks": 4}
print("skew" if s["rec_max"] > 3 * s["rec_med"] else "no skew", "|", "all spill" if s["spill_tasks"] == s["tasks"] else "")
'''),
        dict(label='3 · Tiny tasks', hint='20,000 tasks with a 15 ms median.',
             code='''tasks, med_ms = 20000, 15
print("too many tiny tasks" if tasks > 5000 and med_ms < 100 else "ok")
'''),
        dict(label='4 · Skew ratio', hint='Share of records in the biggest task.',
             code='''print(round(4197000 / 6000000 * 100), "% of the stage in one task")
'''),
        dict(label='5 · Spot the error', hint='No event logs: the app finished and the UI is gone.', expect='error',
             code='''conf = {"spark.eventLog.enabled": "false"}
assert conf["spark.eventLog.enabled"] == "true", "no event logs: the History Server cannot show finished applications"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: the UI and its API',
    intro='<p>While a <code>pyspark</code> shell is open. <b>Outputs are real</b> (Spark 4.3.0).</p>',
    items=[
        dict(title='1 · UI address', cmd='spark.sparkContext.uiWebUrl', file='pyspark',
             output="'http://192.0.2.2:4040'", note='4041, 4042… if taken.'),
        dict(title='2 · Task summary via REST', cmd='curl -s "localhost:4050/api/v1/applications/$APP/stages/6/0/taskSummary?quantiles=0,0.5,1"', file='bash',
             output='"duration" : [ 1219.0, 1582.0, 1608.0 ],\n"memoryBytesSpilled" : [ 1.92937616E8, 1.92937616E8, 1.92937616E8 ]', note='Same numbers as the stage page.'),
        dict(title='3 · Event logs', cmd='spark-submit --conf spark.eventLog.enabled=true --conf spark.eventLog.dir=/opt/spark-events job.py', file='bash',
             output='# History Server on :18080 lists the finished application', note='See Lesson 1.5 cluster.'),
    ],
)

TRACE = dict(
    heading='Percentiles from task durations',
    intro='<p>How the summary table is computed from task durations.</p>',
    code='''d = sorted([0.5, 0.6, 2.0, 5.0])
n = len(d)
summary = {"min": d[0], "median": d[n // 2], "max": d[-1]}
ratio = summary["max"] / summary["median"]
print(summary, round(ratio, 1))
''',
    notes={1: 'Tasks :: Durations of the 4 window tasks (s).', 4: 'Ratio :: max ÷ median is the quickest skew test.'},
)

WORKED_INTRO = 'Three diagnoses from UI numbers.'
EXAMPLES = [
    dict(level='b', tag='UI · basics', title='Which stage first?',
         problem='<p>A job has 5 stages taking 10, 12, 340, 8 and 15 s.</p>',
         inp='stage durations',
         approach=['Sort by duration.', 'Start with the largest.', 'Ignore the rest for now.'],
         code='''st = [10, 12, 340, 8, 15]
print("stage", st.index(max(st)), "takes", round(max(st) / sum(st) * 100), "% of the job")
''', notes={1: 'Focus :: Fix the biggest stage first.'},
         tryit='Step 2.'),
    dict(level='i', tag='UI · patterns', title='Skew or spill?',
         problem='<p>Max task 9 min, median 8 min, every task spills 3 GB.</p>',
         inp='summary metrics',
         approach=['max ≈ median → no skew.', 'Spill everywhere → task size.', 'More partitions.'],
         code='''print("spill / task size" if 9 / 8 < 2 else "skew")
''', notes={1: 'Pattern :: Even durations, even spill.'},
         tryit='Step 4.'),
    dict(level='a', tag='UI · plan', title='Read the plan graph',
         problem='<p>A join query shows two Exchanges of 2 billion and 40 thousand rows.</p>',
         inp='SQL tab',
         approach=['The small side was shuffled too.', 'A broadcast would remove both Exchanges of the big side.', 'Check threshold/hint.'],
         code='''big, small = 2_000_000_000, 40_000
print("broadcast candidate" if small < 1_000_000 else "keep SMJ")
''', notes={2: 'Join :: Lesson 8.2.'},
         tryit='Step 2.'),
]

QUIZ = mix([
    dict(q='Beginner: Default port of the live Spark UI?', options=['8080', '4040', '18080', '7077'], answer=1,
         why='History Server uses 18080.'),
    dict(q='Beginner: A stage is split at…', options=['Every filter', 'Shuffle boundaries', 'Every column', 'Each file'], answer=1,
         why='Wide transformations.'),
    dict(q='Beginner: Which tab shows the physical plan graph?', options=['Jobs', 'Storage', 'SQL / DataFrame', 'Environment'], answer=2,
         why='With operator metrics.'),
    dict(q='Intermediate: Median 2 s, max 5 s, max records 4.2M vs 636K median. Diagnosis?', options=['Spill', 'Skew', 'Small files', 'Healthy'], answer=1,
         why='One task holds the hot key.'),
    dict(q='Intermediate: Even durations, every task spills. Diagnosis?', options=['Skew', 'Tasks too big for memory', 'Broadcast', 'Healthy'], answer=1,
         why='More partitions or memory.'),
    dict(q='Intermediate: How to see a finished app’s UI?', options=['Not possible', 'History Server with event logs', 'Driver logs', 'Restart it'], answer=1,
         why='spark.eventLog.enabled=true.'),
    dict(q='Advanced: Readable job names in the UI come from…', options=['appName only', 'sc.setJobDescription()', 'spark.conf', 'df.alias'], answer=1,
         why='Instead of “save at …”.'),
    dict(q='Advanced: 20,000 tasks of 15 ms suggests…', options=['Skew', 'Too many partitions / small files', 'OOM', 'Broadcast'], answer=1,
         why='Overhead dominates.'),
])

REVISION = [
    'Path: SQL tab → slowest query → plan graph → slowest stage → task summary.',
    'Skew: max ≫ median duration and records (5 s vs 2 s, 4.2M vs 636K).',
    'Spill everywhere with even tasks: tasks too big (184 MiB each).',
    'Thousands of ms-long tasks: too many partitions or small files.',
    'Plan graph: Exchanges = shuffles; operator time shows where it goes.',
    '<code>setJobDescription</code> names jobs; event logs + History Server keep the UI.',
    'REST API <code>/api/v1/…/taskSummary</code> gives the same numbers for automation.',
]
FAQ = [
    ('The UI is empty after my job finished. Why?', 'The live UI lives in the driver; when the app ends it is gone. Enable event logs and use the History Server.'),
    ('What is the Event Timeline?', 'A per-stage view of when each task ran on which executor; gaps and long bars show stragglers and idle time.'),
    ('Where do I see which config was used?', 'The Environment tab lists Spark properties in effect, including those set by the platform.'),
    ('How do I find the UI on a cluster?', 'YARN: ResourceManager → Application → Tracking UI; Kubernetes: port-forward the driver pod’s 4040; Databricks: Spark UI tab on the cluster.'),
    ('Is the REST API stable?', 'Yes, /api/v1 is the documented monitoring API, also served by the History Server.'),
]

PRACTICE_INTRO = 'Programs that turn UI numbers into decisions.'
PROBLEMS = [
    dict(level='easy', title='Skew ratio', stmt='max ÷ median duration.', inp='5 s, 2 s',
         code='''print(5 / 2)
''', explain='2.5x here; >5x is severe.'),
    dict(level='easy', title='Records share', stmt='Share in the biggest task.', inp='4,197,000 of 6,000,000',
         code='''print(round(4197000 / 6000000 * 100), "%")
''', explain='70% in one task.'),
    dict(level='easy', title='Spill total', stmt='Total spill of the sort stage.', inp='4 × 184 MiB',
         code='''print(4 * 184, "MiB")
''', explain='Even spill: task size.'),
    dict(level='medium', title='Slowest stage', stmt='Find the slowest stage id.', inp='durations',
         code='''st = {0: 0.3, 1: 3.6, 2: 5.6, 4: 2.3, 6: 5.6}
print(max(st, key=st.get))
''', explain='Ties: look at both.'),
    dict(level='medium', title='Tiny-task check', stmt='Flag stages with median < 100 ms and > 5,000 tasks.', inp='stages',
         code='''stages = [(20000, 15), (200, 2000)]
print([s for s in stages if s[0] > 5000 and s[1] < 100])
''', explain='Small files or too many partitions.'),
    dict(level='medium', title='GC share', stmt='GC time as % of task time.', inp='81 ms of 5 s',
         code='''print(round(81 / 5000 * 100, 1), "%")
''', explain='Low: not a GC problem.'),
    dict(level='business', title='Time to diagnose', stmt='Hours saved per year with a UI runbook.', inp='1 incident/week, 2 h → 15 min',
         code='''print(round(52 * (2 - 0.25)), "hours")
''', explain='Runbooks pay off.'),
    dict(level='business', title='Wasted reruns', stmt='Cluster hours wasted by blind restarts.', inp='3 reruns × 2 h × 20 executors',
         code='''print(3 * 2 * 20, "executor-hours")
''', explain='Diagnose first.'),
]

SCN_INTRO = 'Interviewers love “walk me through debugging a slow job”.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“What is in the Spark UI?”',
        'Name the main tabs.',
        'what each shows?',
        '<p>Jobs (per action), Stages (tasks and summary metrics), Storage (cached data), Environment (settings), Executors (health, GC, shuffle), and SQL / DataFrame (queries with plan graphs and operator metrics).</p>', 'Only mentioning the Jobs tab.') +
    scn('Data engineering', 'Mid-level', 'Slow job walkthrough',
        'A daily job doubled in duration.',
        'your steps?',
        '''<ol>
          <li>Compare today’s and yesterday’s runs in the History Server.</li>
          <li>Find the stage that grew; read its task summary.</li>
          <li>Match the pattern: skew, spill, input size, more tasks; fix that.</li>
        </ol>''', 'Restarting with more memory.') +
    scn('Data engineering', 'Mid-level', 'Skew vs spill',
        'How do you tell skew from memory problems in the UI?',
        'metrics?',
        '''<ul>
          <li>Skew: max ≫ median duration and shuffle read; spill in few tasks.</li>
          <li>Memory: even tasks, spill or high GC in all tasks.</li>
          <li>In my screenshots: 4.2M vs 636K records vs 184 MiB spill in every task.</li>
        </ul>''', 'Treating all spill as skew.') +
    scn('Platform', 'Senior', 'Observability',
        'Make Spark jobs debuggable across 500 pipelines.',
        'setup?',
        '''<ul>
          <li>Event logs to object storage + History Server with retention.</li>
          <li>Job descriptions and app names by convention.</li>
          <li>REST-based metrics (skew ratio, spill, GC) into dashboards and alerts.</li>
        </ul>''', 'Relying on driver logs only.')
)
