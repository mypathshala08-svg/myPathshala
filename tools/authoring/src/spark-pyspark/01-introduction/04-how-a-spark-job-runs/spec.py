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
    module='01-introduction', lesson='04-how-a-spark-job-runs', n='1.4',
    module_label='Module 1 · Start here: why Spark?',
    title='How a PySpark program becomes jobs, stages and tasks',
    desc='Follow one PySpark program through Spark 4.3.0 with real outputs and Spark UI screenshots: three transformations in 334 ms with no jobs, a typo caught before any job, two actions becoming five jobs with AQE and skipped stages, the Exchange that splits stages, four tasks reading 1,250,000 rows each and shuffling only 32 rows thanks to partial aggregation, and the Jobs, Stages and SQL tabs that show it all.',
    og_desc='Two actions, five jobs, one shuffle of 32 rows: a PySpark program followed through Spark’s engine and UI, with real screenshots.',
    minutes=36, level='Beginner → Intermediate',
    lead='This lesson answers the most important question for anyone writing Spark code: <b>what actually runs, and when?</b> We follow one program on 5,000,000 orders from transformations to an action, to jobs, stages and tasks, and read every step in the <b>Spark UI</b>. <b>All outputs and screenshots are real</b> (Spark 4.3.0).',
    chips=['Spark 4.3.0', 'Real Spark UI screenshots', 'Lazy vs eager, measured', 'Runs in your browser (Python)'],
)

MAIN = '''# A tiny lazy "DataFrame": transformations record steps, an action runs them
class LazyFrame:
    def __init__(self, rows, steps=()):
        self.rows, self.steps = rows, list(steps)
    def where(self, f):            # transformation: just remember it
        return LazyFrame(self.rows, self.steps + [("where", f)])
    def with_gst(self):
        return LazyFrame(self.rows, self.steps + [("map", lambda r: {**r, "gst": r["amount"] * 0.05})])
    def collect(self):             # action: now do the work
        out = self.rows
        for kind, f in self.steps:
            out = [r for r in out if f(r)] if kind == "where" else [f(r) for r in out]
        return out

orders = LazyFrame([{"city": "Mumbai", "amount": 530}, {"city": "Pune", "amount": 210}])
plan = orders.where(lambda r: r["amount"] > 300).with_gst()
print("steps recorded:", [k for k, _ in plan.steps])
print("result:", plan.collect())
'''
RUN = dict(
    heading='Run the code: build your own lazy DataFrame',
    intro='<p>PySpark cannot run in the browser, but its execution model can. This small class behaves like Spark: transformations record steps, actions run them. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('        return LazyFrame(self.rows, self.steps + [("where", f)])', 'Like df.where(): returns a new object with one more step; no rows are touched.'),
        ('    def collect(self):             # action: now do the work', 'Like collect() or show(): only here are the steps applied to the data.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Add a second where() and check that nothing runs until collect().', code=None),
        dict(label='2 · Predict first: stages', hint='<b>Predict first:</b> how many stages for read → where → groupBy → orderBy?',
             code='''ops = ["read", "where", "groupBy", "orderBy"]
wide = {"groupBy", "orderBy", "join", "repartition", "distinct"}
stages = 1 + sum(op in wide for op in ops)
print("stages:", stages)
'''),
        dict(label='3 · Tasks per stage', hint='One task per partition. Compute total tasks.',
             code='''partitions = [4, 1]        # stage 1 read 4 partitions; after AQE, 1 partition
print("tasks:", sum(partitions))
'''),
        dict(label='4 · Partial aggregation', hint='How many rows cross the shuffle with and without partial aggregation?',
             code='''tasks, rows_per_task, cities = 4, 1_187_500, 8
print("without partial agg:", tasks * rows_per_task)
print("with partial agg   :", tasks * cities)
'''),
        dict(label='5 · Spot the error', hint='This loop runs one action per city.', expect='error',
             code='''cities = ["Mumbai", "Pune", "Delhi"]
actions = len(cities)                 # df.where(city == c).count() in a loop
assert actions == 1, f"{actions} jobs; use one groupBy('city').count() instead"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: look inside a job',
    intro='<p>With PySpark installed (Lesson 1.5). <b>Outputs are real</b> (Spark 4.3.0).</p>',
    items=[
        dict(title='1 · Label your jobs', cmd='spark.sparkContext.setJobDescription("B: show() the city report")\ndaily.orderBy(F.desc("revenue")).show(10)', file='pyspark',
             output='\n'.join(capf('l14_anatomy.txt').split('\n')[1:6]) + '\n…',
             note='The description appears in the Jobs tab (screenshot in Step 4).'),
        dict(title='2 · The physical plan', cmd='daily.explain()', file='pyspark',
             output=capf('l14_anatomy.txt').split('== Physical Plan ==')[1].strip().split('\n         +- Project')[0] + '\n…',
             note='One Exchange = one shuffle = two stages.'),
        dict(title='3 · Jobs via the REST API', cmd='curl -s http://localhost:4040/api/v1/applications/<app-id>/jobs', file='terminal',
             output=capf('l14_rest.txt').split('STAGES')[0].split('JOBS\n')[1].rstrip(),
             note='Port 4040 while the application runs; the history server (18080) afterwards. Shown here summarised.'),
    ],
)

TRACE = dict(
    heading='How a groupBy splits into two stages',
    intro='<p>Follow partial and final aggregation across a shuffle.</p>',
    code='''partitions = [[("Mumbai", 530), ("Pune", 210)], [("Mumbai", 480), ("Delhi", 990)]]
partials = []
for p in partitions:                       # stage 1: one task per partition
    acc = {}
    for city, amt in p:
        acc[city] = acc.get(city, 0) + amt
    partials.append(acc)
final = {}
for acc in partials:                       # shuffle, then stage 2
    for city, s in acc.items():
        final[city] = final.get(city, 0) + s
print(partials, final)
''',
    notes={3: 'Stage 1 :: Each task aggregates its own partition (partial_sum).', 7: 'Shuffle write :: Only the small partial results leave the task.', 11: 'Stage 2 :: Final sums per city.'},
)

WORKED_INTRO = 'Three ways to use jobs, stages and the UI in real work.'
EXAMPLES = [
    dict(level='b', tag='Concepts · actions', title='Count the actions',
         problem='<p>How many jobs (at least) will this code start?</p>',
         inp='five lines of PySpark',
         approach=['Mark transformations.', 'Mark actions.', 'Each action ≥ 1 job.'],
         code='''lines = [("df = spark.read.parquet(p)", "reader: small job"), ("f = df.where(...)", "transformation"),
         ("g = f.groupBy('city').count()", "transformation"), ("g.show()", "ACTION"), ("print(f.count())", "ACTION")]
for code, kind in lines:
    print(f"{kind:18} {code}")
''', notes={4: 'show :: With AQE it started 2 jobs in our lab.'},
         tryit='Check the Jobs tab: our run had 5 jobs.'),
    dict(level='i', tag='Debugging · UI', title='Find the slow stage',
         problem='<p>Use stage metrics to decide where to look first.</p>',
         inp='stage durations and task max/median',
         approach=['Sort stages by duration.', 'Compare max and median task time.', 'Open the SQL tab.'],
         code='''stages = {"stage 1": (5.0, 4.0, 4.0), "stage 3": (0.5, 0.5, 0.5), "stage 7": (380, 4, 360)}
for s, (dur, med, mx) in sorted(stages.items(), key=lambda x: -x[1][0]):
    flag = "SKEW?" if mx > 10 * med else ""
    print(f"{s}: {dur:6.1f} s  median task {med} s  max {mx} s {flag}")
''', notes={3: 'Skew :: One task far slower than the median usually means one hot key.'},
         tryit='Lesson 8.6 is a full Spark UI troubleshooting guide.'),
    dict(level='a', tag='Performance · plans', title='Remove a useless shuffle',
         problem='<p>A pipeline repartitions before a groupBy on the same key. Is it needed?</p>',
         inp='repartition(200, "city").groupBy("city")',
         approach=['Count Exchanges in explain().', 'groupBy already hash-partitions by key.', 'Drop the repartition.'],
         code='''before = ["Exchange hashpartitioning(city, 200)  <- repartition", "HashAggregate (no extra exchange)"]
after = ["HashAggregate partial", "Exchange hashpartitioning(city, 200)", "HashAggregate final"]
print("before:", before); print("after :", after)
''', notes={1: 'Before :: The repartition shuffles full rows; without it, only partial results are shuffled.'},
         tryit='Run both with explain() and compare shuffle write in the Stages tab.'),
]

QUIZ = mix([
    dict(q='Beginner: Which one is an action?', options=['where', 'groupBy', 'count', 'withColumn'], answer=2,
         why='Actions return results and start jobs.'),
    dict(q='Beginner: How long did three transformations take in the lab?', options=['3.6 s', '334 ms with 0 jobs', '0 ms', '20 s'], answer=1,
         why='Only analysis, no execution.'),
    dict(q='Beginner: One task processes…', options=['one row', 'one partition of one stage', 'one job', 'one executor'], answer=1,
         why='Four partitions → four tasks.'),
    dict(q='Intermediate: Where does a job split into stages?', options=['At every transformation', 'At shuffle (wide) boundaries', 'At every file', 'Never'], answer=1,
         why='Exchange in the plan.'),
    dict(q='Intermediate: Why was a misspelt column reported before any action?', options=['Bug', 'DataFrame operations are analysed eagerly', 'Parquet checks names', 'AQE'], answer=1,
         why='Executed lazily, analysed eagerly.'),
    dict(q='Intermediate: Why did show() start two jobs?', options=['Two executors', 'AQE runs the shuffle map stage as its own job, then re-plans', 'Retry', 'Two files'], answer=1,
         why='Stage 2 was then skipped in job 2.'),
    dict(q='Advanced: How many rows did stage 1 write to the shuffle?', options=['5,000,000', '4,750,000', '32', '8'], answer=2,
         why='8 partial results per task × 4 tasks.'),
    dict(q='Advanced: What does a “skipped” stage mean?', options=['It failed', 'Its shuffle output already existed', 'It was empty', 'It was cancelled'], answer=1,
         why='Job 1 had written it.'),
])

REVISION = [
    '<b>Transformations</b> are lazy (plan only); <b>actions</b> start jobs. Lab: 334 ms / 0 jobs vs 3.6 s / 2 jobs.',
    'DataFrames are <b>analysed eagerly</b>: bad column names fail immediately.',
    'Action → <b>job(s)</b> → <b>stages</b> (cut at shuffles) → <b>tasks</b> (one per partition).',
    'Narrow ops are pipelined in one stage; wide ops (groupBy, join, orderBy, repartition) add an <b>Exchange</b>.',
    'AQE: one action can start 2 jobs; reused shuffle output shows as <b>skipped</b> stages.',
    'Partial aggregation: 4 tasks × 1,250,000 rows → only 32 rows shuffled.',
    'UI: Jobs → Stages (task percentiles) → SQL tab (rows per operator). Port 4040, history server 18080.',
]
FAQ = [
    ('Why is the Spark UI gone after my job ends?', 'The UI lives in the driver. When the application stops, it disappears unless event logging is on and a history server reads the logs. Our lab enables spark.eventLog.enabled and runs a history server on port 18080.'),
    ('What is the number 200 in Exchange hashpartitioning(city, 200)?', 'spark.sql.shuffle.partitions, the default number of shuffle partitions. With AQE enabled (the default), Spark coalesces them at run time based on real data sizes; our tiny shuffle ended in 1 partition.'),
    ('Is RDD code also lazy?', 'Yes. RDD transformations (map, filter) are lazy and actions (collect, count, saveAsTextFile) run jobs. The difference is that RDDs are not optimised by Catalyst (Module 2).'),
    ('Does show() process all the data?', 'Not always. For a simple scan, show() reads only enough partitions for the first rows. With a groupBy or orderBy, like ours, all data must be processed first.'),
    ('Can I see the plan without running the job?', 'Yes: df.explain() prints the plan, and explain("formatted") gives a readable version. No job is started (Lesson 7.3).'),
]

PRACTICE_INTRO = 'Programs about laziness, stages and tasks.'
PROBLEMS = [
    dict(level='easy', title='Action or not?', stmt='Classify operations.', inp='list of names',
         code='''actions = {"show", "count", "collect", "write", "take", "first"}
for op in ["where", "show", "groupBy", "count", "select"]:
    print(op, "ACTION" if op in actions else "transformation")
''', explain='Only actions start jobs.'),
    dict(level='easy', title='Tasks in a stage', stmt='Tasks for 8 partitions.', inp='8',
         code='''print(8)
''', explain='One task per partition.'),
    dict(level='easy', title='Waves', stmt='How long do 8 tasks of 4 s take on 4 slots?', inp='8 tasks, 4 slots, 4 s',
         code='''print(-(-8 // 4) * 4, "s")
''', explain='Two waves of four.'),
    dict(level='medium', title='Count stages', stmt='Stages for a pipeline.', inp='read, where, join, groupBy, write',
         code='''wide = {"join", "groupBy", "orderBy", "repartition"}
ops = ["read", "where", "join", "groupBy", "write"]
print(1 + sum(o in wide for o in ops))
''', explain='Broadcast joins avoid the join shuffle (Lesson 8.2), giving one stage fewer.'),
    dict(level='medium', title='Shuffle reduction', stmt='Rows saved by partial aggregation.', inp='4.75 M rows, 32 partial rows',
         code='''print(f"{1 - 32 / 4_750_000:.6%} fewer rows shuffled")
''', explain='Why groupBy with sum/count is cheap compared to collecting all rows.'),
    dict(level='medium', title='Loop to groupBy', stmt='Rewrite a loop of counts as one query.', inp='3 cities',
         code='''print("df.groupBy('city').count()   # 1 job instead of one job per city")
''', explain='Each count() in a loop re-reads the data.'),
    dict(level='business', title='Wasted scans', stmt='Cost of a 120-action notebook.', inp='120 jobs × 10 s vs 1 job × 15 s',
         code='''print(120 * 10 / 60, "min vs", 15 / 60, "min")
''', explain='Same answer, a fraction of the cluster time.'),
    dict(level='business', title='Network saved', stmt='Bytes shuffled with and without partial aggregation.', inp='4.75 M rows × 20 B vs 2.6 KiB',
         code='''print(round(4_750_000 * 20 / 2**20, 1), "MiB vs 0.003 MiB")
''', explain='At terabyte scale this is the difference between minutes and hours.'),
]

SCN_INTRO = 'Jobs, stages and tasks are asked about in nearly every Spark interview.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“What is lazy evaluation?”',
        'Explain lazy evaluation with an example.',
        'do you know transformations vs actions?',
        '<p>Transformations like where and groupBy only build a plan; nothing is computed until an action like count, show or write. Spark can then optimise the whole plan, e.g. push filters into the scan and aggregate partially before shuffling. In our lab three transformations took 334 ms with no jobs; one collect() took 3.6 s.</p>', 'Saying transformations run in the background.') +
    scn('Data engineering', 'Fresher', 'Job vs stage vs task',
        'Define job, stage and task.',
        'can you be precise?',
        '''<ul>
          <li>Job: started by an action.</li>
          <li>Stage: part of a job between shuffles; narrow ops pipelined.</li>
          <li>Task: one stage on one partition, run on an executor slot.</li>
        </ul>''', 'Mixing up stages and tasks.') +
    scn('Data engineering', 'Mid-level', 'Notebook with hundreds of jobs',
        'A notebook starts 300 jobs and takes 30 minutes.',
        'can you read the Jobs tab?',
        '''<ol>
          <li>Find actions in loops (count, collect, show).</li>
          <li>Replace them with one grouped query or cache a reused DataFrame.</li>
          <li>Verify the job count and duration in the UI.</li>
        </ol>''', 'Adding executors.') +
    scn('Platform', 'Senior', 'Explain a slow stage',
        'One stage takes 90% of a job’s time.',
        'can you use the UI systematically?',
        '''<ul>
          <li>Stages tab: task duration percentiles, shuffle read/write, spill.</li>
          <li>Max ≫ median → skew; all slow → too few partitions or too much data per task.</li>
          <li>SQL tab: which operator; then fix (AQE skew handling, salting, partitions, broadcast).</li>
        </ul>''', 'Guessing from the code without looking at the UI.')
)
