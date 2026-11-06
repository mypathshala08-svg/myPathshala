import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='13-capstone', lesson='03-review-and-interview-preparation', n='13.3',
    module_label='Module 13 · Capstone',
    title='Review and interview preparation',
    desc='Capstone part 3: review the TiffinGo pipeline with evidence (56 vs 14 output files, BroadcastHashJoin and PartitionFilters in the plan, sort-merge 5.30 s vs AQE 1.12 s vs broadcast 0.59 s under 30% skew, a quality gate stopping a 5.34% bad day), then turn it into a STAR project story and revise the whole PySpark course with the questions interviewers ask.',
    og_desc='Prove your Spark pipeline with plans and timings, then tell it as an interview story: capstone review plus course-wide revision.',
    minutes=30, level='Advanced',
    lead='Finish the capstone like a senior engineer: <b>review</b> the pipeline with real evidence (files, plans, timings, a failing gate), write your <b>60-second project story</b>, and <b>revise the whole course</b> with interview questions. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['Broadcast 0.59 s vs 5.30 s', 'Plan evidence', 'Project story', 'Runs in your browser (Python)'],
)

MAIN = '''# Review evidence for the capstone, as numbers you can explain
tasks, days = 4, 14
print("files without repartition:", tasks * days, "| with:", days)

timings = {"sort-merge, AQE off": 5.30, "sort-merge, AQE on": 1.12, "broadcast": 0.59}
best = min(timings, key=timings.get)
for k, v in timings.items():
    print(f"{k:20} {v:5.2f} s  x{v / timings[best]:.1f}")

def gate(bad, total, limit=2.0):
    pct = round(100 * bad / total, 2)
    return pct, ("ok" if pct < limit else "STOP")

print("normal day:", gate(4944, 842587))
print("bad day   :", gate(3204, 60000))
'''
RUN = dict(
    heading='Run the code: the review in numbers',
    intro='<p>The evidence behind every interview answer. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('print("files without repartition:", tasks * days, "| with:", days)', 'Each task writes one file per day it holds unless you repartition first.'),
        ('    return pct, ("ok" if pct < limit else "STOP")', 'The quality gate: fail the run rather than publish bad gold.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then try 8 tasks.', code=None),
        dict(label='2 · Predict first: speed-up', hint='<b>Predict first:</b> 5.30 / 0.59 ≈ ?',
             code='''print(round(5.30 / 0.59, 1))
'''),
        dict(label='3 · Stages', hint='Shuffles split stages: count them.',
             code='''ops = ["read", "filter", "groupBy*", "select", "join*", "write"]
print("stages:", 1 + sum(o.endswith("*") for o in ops))
'''),
        dict(label='4 · Year of files', hint='Daily partitions for a year.',
             code='''print(365 * 4, "vs", 365)
'''),
        dict(label='5 · Spot the error', hint='Calling an action on nothing.', expect='error',
             code='''plan = None
print(plan.count("BroadcastHashJoin"))
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: the review script',
    intro='<p>From the lab folder <code>jobs/m13</code>, after the pipeline has run. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Review', cmd='python review.py data/m13', file='terminal',
             output='without repartition: 56 files for 14 days | pipeline (repartition first): 14 files\nBroadcastHashJoin: True | SortMergeJoin: False | AdaptiveSparkPlan isFinalPlan=true: True', note='Plan evidence.'),
        dict(title='2 · Pruning', cmd='spark.read.parquet("data/m13/silver/orders").filter("order_date = \'2026-11-01\'").explain()', file='pyspark',
             output='PartitionFilters: [isnotnull(order_date), (order_date = 2026-11-01)]', note='One folder read.'),
        dict(title='3 · Gate', cmd='(see review.py step 4)', file='terminal',
             output='quarantine_pct: 5.34 -> STOP: too many bad rows (gate < 2%)', note='Bad day stopped.'),
    ],
)

TRACE = dict(
    heading='Lazy until an action',
    intro='<p>The most-asked Spark fundamental, as a tiny model.</p>',
    code='''plan = []
def transform(name):
    plan.append(name)
transform("filter")
transform("groupBy")
print("nothing ran yet:", plan)
print("action -> run", len(plan), "steps")
''',
    notes={2: 'Lazy :: Transformations only add to the plan.', 7: 'Action :: count/collect/write trigger execution.'},
)

WORKED_INTRO = 'Three interview answers built from the capstone.'
EXAMPLES = [
    dict(level='b', tag='Interview · fundamentals', title='“Transformation vs action?”',
         problem='<p>The classic first question.</p>',
         inp='—',
         approach=['Transformations are lazy and build a plan.', 'Actions run it.', 'Give a capstone example.'],
         code='''print("transform: clean_orders (filter, select, dropDuplicates)")
print("action   : write.parquet / count in the gates")
''', notes={1: 'Concrete :: Use your own code as the example.'},
         tryit='Trace above.'),
    dict(level='i', tag='Interview · performance', title='“Why did you broadcast?”',
         problem='<p>Explain the join choice.</p>',
         inp='800 vs 835,067 rows',
         approach=['Small dimension fits in memory.', 'No shuffle of orders; skew irrelevant.', 'Show the measurement.'],
         code='''print("restaurants 800 rows -> broadcast")
print("measured: 0.59 s vs 5.30 s sort-merge (AQE off)")
''', notes={1: 'Evidence :: Numbers end the debate.'},
         tryit='Step 3.'),
    dict(level='a', tag='Interview · design', title='“How do you guarantee correctness?”',
         problem='<p>A senior-level follow-up.</p>',
         inp='pipeline',
         approach=['Unit tests on transforms.', 'Reconciliation: raw = silver + quarantine + duplicates.', 'Gates before publishing gold.'],
         code='''print(842587 == 835067 + 4944 + 2576)
''', notes={1: 'Reconcile :: Every row is accounted for.'},
         tryit='Step 4.'),
]

QUIZ = mix([
    dict(q='Beginner: Without repartition, 4 tasks × 14 days wrote…', options=['14 files', '56 files', '4 files', '1 file'], answer=1,
         why='One file per task per day.'),
    dict(q='Beginner: Which join did the gold plan use?', options=['SortMergeJoin', 'BroadcastHashJoin', 'Cartesian', 'None'], answer=1,
         why='Restaurants has 800 rows.'),
    dict(q='Beginner: STAR stands for…', options=['Spark, Table, AQE, RDD', 'Situation, Task, Action, Result', 'Start, Test, Assert, Run', 'None'], answer=1,
         why='A project story structure.'),
    dict(q='Intermediate: PartitionFilters in the plan means…', options=['Rows filtered after read', 'Folders skipped by the filter', 'A bug', 'Caching'], answer=1,
         why='Partition pruning.'),
    dict(q='Intermediate: Under skew, AQE on (sort-merge) took…', options=['5.30 s', '1.12 s', '0.59 s', '25 s'], answer=1,
         why='Broadcast was fastest at 0.59 s.'),
    dict(q='Intermediate: The bad day had a quarantine share of…', options=['0.59%', '2%', '5.34%', '30%'], answer=2,
         why='Above the 2% gate: STOP.'),
    dict(q='Advanced: Data grows 100×. First change?', options=['Bigger driver', 'Incremental processing of new partitions', 'collect()', 'Disable AQE'], answer=1,
         why='Avoid full rebuilds.'),
    dict(q='Advanced: Best answer to “what would you change?”', options=['Nothing', 'Named limitations with fixes', 'Blame the data', 'Rewrite in pandas'], answer=1,
         why='Shows judgement.'),
])

REVISION = [
    'Review with evidence: files, plan, pruning, timed alternatives, failure tests.',
    'Files: 56 → 14 with repartition(order_date).',
    'Plan: BroadcastHashJoin, AQE final plan, PartitionFilters on order_date.',
    'Skew: sort-merge 5.30 s (AQE off), 1.12 s (AQE on), broadcast 0.59 s.',
    'Gate: bad day 5.34% → STOP before gold.',
    'Story: STAR with numbers; prepare follow-ups on scale, correctness and changes.',
    'Revise: architecture, lazy evaluation, formats, joins, AQE, skew, streaming, MLlib, production, Spark 4.',
]
FAQ = [
    ('Can I put this capstone on my CV?', 'Yes, as a project: describe it honestly as a portfolio pipeline on generated data, and be ready to show the code and explain every number.'),
    ('Should I put the code on GitHub?', 'Yes: transforms, tests, pipeline, a README with the architecture diagram and the run metrics. Do not commit the data.'),
    ('How do I extend it?', 'Make it incremental, write gold as Delta or Iceberg (11.5), add a streaming orders source (Module 9), or train the churn model (Module 10) on customer_features.'),
    ('What else do interviews cover?', 'SQL (window functions, joins), Python, data modelling and one cloud platform; Spark questions usually focus on internals, performance and debugging.'),
    ('I finished the course. What next?', 'Build one more project on real public data, learn one platform (Databricks, EMR or Fabric) in depth, and practise explaining plans from the Spark UI.'),
]

PRACTICE_INTRO = 'Interview-style programs.'
PROBLEMS = [
    dict(level='easy', title='Reconcile', stmt='Check every row is accounted for.', inp='counts',
         code='''print(842587 == 835067 + 4944 + 2576)
''', explain='True.'),
    dict(level='easy', title='Speed-up', stmt='Broadcast vs naive.', inp='5.30, 0.59',
         code='''print(round(5.30 / 0.59, 1), "x")
''', explain='About 9×.'),
    dict(level='easy', title='Files', stmt='Output files per run.', inp='tasks, days',
         code='''print(4 * 14, 14)
''', explain='56 vs 14.'),
    dict(level='medium', title='Shuffle partitions', stmt='Partitions for 50 GB at 128 MB.', inp='50 GB',
         code='''print(50 * 1024 // 128)
''', explain='400 (Lesson 8.1).'),
    dict(level='medium', title='Broadcast or not', stmt='Decide from size (10 MB default threshold).', inp='sizes MB',
         code='''for name, mb in [("restaurants", 0.05), ("customers", 1.2), ("orders", 900)]:
    print(name, "broadcast" if mb <= 10 else "shuffle")
''', explain='Default autoBroadcastJoinThreshold is 10 MB.'),
    dict(level='medium', title='Window: top per group', stmt='Biggest order per city.', inp='orders',
         code='''o = [("Mumbai", 900), ("Mumbai", 1200), ("Pune", 700)]
best = {}
for c, a in o:
    best[c] = max(best.get(c, 0), a)
print(best)
''', explain='row_number over partitionBy(city).'),
    dict(level='business', title='Cost of a slow join', stmt='Seconds saved per year on a nightly job.', inp='5.30 → 0.59',
         code='''print(round((5.30 - 0.59) * 365))
''', explain='Scales with data size.'),
    dict(level='business', title='Bad days caught', stmt='Gate catches 1 bad day a month: wrong reports avoided per year.', inp='12',
         code='''print(12, "wrong dashboards avoided")
''', explain='Why gates matter.'),
]

SCN_INTRO = 'Final interview round: project and fundamentals.'
SCENARIOS = (
    scn('Any company · data', 'Fresher', '“Explain how Spark runs your job.”',
        'Fundamentals from Module 1–2.',
        'answer?',
        '<p>The driver builds a logical plan from my transformations, Catalyst optimises it, and an action like write triggers a job. The job splits into stages at shuffles (my groupBy and repartition), each stage into tasks, one per partition, run by executors in parallel.</p>', 'Saying “Spark runs it in memory”.') +
    scn('Data engineering', 'Mid-level', 'Slow job',
        'Your nightly job went from 25 s to 10 minutes.',
        'debug?',
        '''<ol>
          <li>Spark UI: which stage, skewed tasks, spill (Lesson 8.6).</li>
          <li>Plan: did a broadcast become sort-merge?</li>
          <li>Data: volume or key distribution changed?</li>
        </ol>''', 'Adding executors blindly.') +
    scn('Data engineering', 'Mid-level', 'Correctness',
        'Finance says yesterday’s revenue is wrong.',
        'response?',
        '''<ul>
          <li>Reconcile counts: raw vs silver vs quarantine.</li>
          <li>Check duplicates and status filter; run tests.</li>
          <li>Fix, re-run the partition idempotently, add a test.</li>
        </ul>''', 'Patching numbers by hand.') +
    scn('Platform', 'Senior', 'Design at scale',
        'Design this pipeline for 50 cities and real-time revenue.',
        'design?',
        '''<ul>
          <li>Kafka → Structured Streaming with watermarks into Delta silver.</li>
          <li>Incremental gold; batch features nightly for ML.</li>
          <li>Expectations as gates, checkpoints, monitoring and alerts.</li>
        </ul>''', 'Running the batch job every minute.')
)
