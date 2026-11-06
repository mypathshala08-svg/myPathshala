import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='12-spark-in-industry', lesson='01-spark-platforms', n='12.1',
    module_label='Module 12 · Spark in industry',
    title='Spark platforms',
    desc='Spark platforms compared (November 2026): Databricks (Runtime 19 with Spark 4.2.0, 18 LTS with 4.1.0), Microsoft Fabric Runtime 2.0 (Spark 4.1), Amazon EMR (Spark 4.0.2), Google Serverless for Apache Spark runtime 3.0 (Spark 4.0.1), AWS Glue 5.1 (Spark 3.5.6) and open-source Spark 4.3.0, plus one unchanged PySpark job run on local mode, a standalone cluster and YARN (start-up 7.5 s, 10.7 s, 25.7 s) and how to choose a platform.',
    og_desc='Databricks, Fabric, EMR, Dataproc, Glue or open source? Which Spark version each ships in November 2026, and one job run on three targets.',
    minutes=24, level='Intermediate',
    lead='Most companies use Spark through a platform. This lesson runs one unchanged job on <b>three targets</b> from this course, compares the <b>Spark versions and models</b> of Databricks, Fabric, EMR, Google’s Serverless Spark, Glue and open source (from official pages, November 2026), and gives a way to choose. <b>Lab outputs are real</b> (Spark 4.3.0).',
    chips=['Spark 4.3.0', '3 launch targets', 'Platform versions (Nov 2026)', 'Runs in your browser (Python)'],
)

MAIN = '''# Score platforms against your own requirements (weights are yours to set)
weights = {"governance": 3, "low_ops": 3, "newest_spark": 1, "cost_small_jobs": 2, "portability": 2}
platforms = {
    "Lakehouse platform":   {"governance": 5, "low_ops": 5, "newest_spark": 4, "cost_small_jobs": 3, "portability": 3},
    "Cloud managed Spark":  {"governance": 4, "low_ops": 4, "newest_spark": 3, "cost_small_jobs": 4, "portability": 3},
    "Self-managed on K8s":  {"governance": 2, "low_ops": 1, "newest_spark": 5, "cost_small_jobs": 3, "portability": 5},
}
for name, s in platforms.items():
    score = sum(weights[k] * s[k] for k in weights)
    print(f"{name:22} {score}")
'''
RUN = dict(
    heading='Run the code: a weighted platform score',
    intro='<p>A simple decision matrix. The scores are illustrative; set your own. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('weights = {"governance": 3, "low_ops": 3, "newest_spark": 1, "cost_small_jobs": 2, "portability": 2}', 'Weights come from your requirements, not from vendor slides.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then make <code>newest_spark</code> weight 5.', code=None),
        dict(label='2 · Predict first: version lag', hint='<b>Predict first:</b> minor versions behind open-source 4.3.',
             code='''oss = 4.3
for name, v in {"Databricks 19": 4.2, "Fabric 2.0": 4.1, "EMR": 4.0, "Glue 5.1": 3.5}.items():
    print(f"{name:14} {round((oss - v) * 10) if v >= 4 else 'major version behind'}")
'''),
        dict(label='3 · Idle cost', hint='Cluster hours used vs paid.',
             code='''job_min_per_day, cluster_hours_per_day = 40, 24
print(round(job_min_per_day / 60 / cluster_hours_per_day * 100, 1), "% utilisation")
'''),
        dict(label='4 · Start-up overhead', hint='Start-up share of a run in the lab.',
             code='''for name, start, run in [("local", 7.5, 2.9), ("standalone", 10.7, 6.3), ("yarn", 25.7, 6.6)]:
    print(f"{name:10} {round(start / (start + run) * 100)}% start-up")
'''),
        dict(label='5 · Spot the error', hint='Using a Spark 4.3 feature on a Spark 3.5 runtime.', expect='error',
             code='''platform_spark, needed = (3, 5), (4, 3)
assert platform_spark >= needed, "feature not available on this runtime: check the platform's Spark version first"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: one job, many masters',
    intro='<p>With the lab cluster and YARN container. <b>Outputs are real</b> (Spark 4.3.0).</p>',
    items=[
        dict(title='1 · Local', cmd='PYSPARK_SUBMIT_ARGS="--master local[4] pyspark-shell" python same_job.py', file='bash',
             output='master=local[4]                         | session start  7.5 s | query  2.9 s | result rows 6 | first 830000166', note='No cluster.'),
        dict(title='2 · Standalone', cmd='spark-submit --master spark://spark-master:7077 same_job.py', file='bash',
             output='master=spark://spark-master:7077        | session start 10.7 s | query  6.3 s | result rows 6 | first 830000166', note='Same result.'),
        dict(title='3 · YARN', cmd='spark-submit --master yarn --num-executors 2 same_job.py', file='bash',
             output='master=yarn                             | session start 25.7 s | query  6.6 s | result rows 6 | first 830000166', note='Slowest start.'),
    ],
)

TRACE = dict(
    heading='Which platforms can run a feature?',
    intro='<p>Compare required and available Spark versions.</p>',
    code='''need = (4, 1)
runtimes = {"Fabric 2.0": (4, 1), "EMR": (4, 0), "Glue 5.1": (3, 5)}
ok = []
for name, v in runtimes.items():
    if v >= need:
        ok.append(name)
print(ok)
''',
    notes={1: 'Need :: e.g. SQL scripting GA in 4.1.', 5: 'Compare :: Tuples compare major then minor.'},
)

WORKED_INTRO = 'Three platform questions at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='Platforms · basics', title='Which Spark will I get?',
         problem='<p>The team wants SQL scripting (GA in Spark 4.1).</p>',
         inp='platform runtimes',
         approach=['List each platform’s current runtime.', 'Compare with 4.1.', 'Check LTS dates.'],
         code='''runtimes = {"Databricks 18 LTS": (4, 1), "Fabric 2.0": (4, 1), "EMR": (4, 0), "Glue 5.1": (3, 5)}
print([k for k, v in runtimes.items() if v >= (4, 1)])
''', notes={1: 'Nov 2026 :: From vendor documentation.'},
         tryit='Step 3.'),
    dict(level='i', tag='Platforms · cost', title='Cluster or serverless?',
         problem='<p>One 40-minute nightly job.</p>',
         inp='usage pattern',
         approach=['Utilisation of a 24 h cluster.', 'Serverless pays per run.', 'Accept start-up latency.'],
         code='''print("utilisation:", round(40 / (24 * 60) * 100, 1), "% -> serverless")
''', notes={1: 'Idle :: 97% of paid time unused.'},
         tryit='Scenario 3.'),
    dict(level='a', tag='Platforms · portability', title='Stay portable',
         problem='<p>Avoid being locked into one vendor.</p>',
         inp='codebase',
         approach=['Standard DataFrame/SQL APIs.', 'Open table formats + open catalogs.', 'Isolate vendor-only utilities.'],
         code='''rules = ["no vendor-only SQL in core logic", "Delta/Iceberg tables", "wrap platform utilities in one module"]
print("\\n".join(rules))
''', notes={1: 'Exit cost :: Lower when logic is standard.'},
         tryit='Use case 4.'),
]

QUIZ = mix([
    dict(q='Beginner: Does PySpark code usually change between platforms?', options=['Completely', 'Mostly not; config and launch change', 'Always rewritten', 'Only SQL changes'], answer=1,
         why='Same job, three targets.'),
    dict(q='Beginner: Serverless Spark means…', options=['No Spark', 'No clusters to manage; pay per job', 'Free', 'Only SQL'], answer=1,
         why='Platform manages compute.'),
    dict(q='Beginner: Newest open-source Spark (Nov 2026)?', options=['3.5.6', '4.0.2', '4.3.0', '5.0'], answer=2,
         why='Released 30 Oct 2026.'),
    dict(q='Intermediate: Which platform was still on Spark 3.5 (Nov 2026)?', options=['Databricks 19', 'Fabric 2.0', 'AWS Glue 5.1', 'EMR'], answer=2,
         why='Glue 5.1: Spark 3.5.6.'),
    dict(q='Intermediate: Slowest start-up in our lab?', options=['local', 'standalone', 'YARN', 'all equal'], answer=2,
         why='25.7 s: staging + AM.'),
    dict(q='Intermediate: Databricks Runtime 18 LTS ships…', options=['Spark 3.5', 'Spark 4.1.0', 'Spark 4.3.0', 'Spark 4.2.0'], answer=1,
         why='DBR 19 has 4.2.0.'),
    dict(q='Advanced: Biggest source of lock-in?', options=['DataFrame API', 'Vendor-only features and catalogs', 'Parquet', 'Python'], answer=1,
         why='Keep logic standard.'),
    dict(q='Advanced: Best evidence for choosing?', options=['Vendor benchmark', 'Your real pipeline on each trial', 'Popularity', 'Price list only'], answer=1,
         why='Measure your workload.'),
])

REVISION = [
    'Platforms = Spark + infra, runtime, tools, governance, billing.',
    'Same code ran on local, standalone, YARN; start-up 7.5 / 10.7 / 25.7 s.',
    'Nov 2026: OSS 4.3.0; Databricks 19 → 4.2.0; Fabric 2.0 → 4.1; EMR 4.0.2; Google RT 3.0 → 4.0.1; Glue 5.1 → 3.5.6.',
    'Platforms lag open source; check runtime versions before using features.',
    'Serverless for spiky jobs; warm clusters for interactive work.',
    'Portability: standard APIs, open table formats, isolated vendor utilities.',
    'Decide with requirements, a real benchmark and total cost (incl. people).',
]
FAQ = [
    ('Is Databricks Spark the same as Apache Spark?', 'It is built on Apache Spark and adds proprietary features (e.g. Photon engine, Unity Catalog); standard APIs behave the same.'),
    ('Why do platforms lag open-source releases?', 'They test, patch and bundle connectors and security features before release, and support older runtimes (LTS) for stability.'),
    ('What is an LTS runtime?', 'A runtime version supported for a long period with fixes, recommended for production jobs that should not change often.'),
    ('Is Synapse Spark still a choice?', 'Microsoft’s current Spark investment is Fabric; check Microsoft’s lifecycle pages for Synapse runtimes.'),
    ('Do I need a platform to learn Spark?', 'No: pip install pyspark and local mode (as in this course) cover almost everything.'),
]

PRACTICE_INTRO = 'Programs for platform decisions.'
PROBLEMS = [
    dict(level='easy', title='Version check', stmt='Is 4.0 ≥ 4.1?', inp='tuples',
         code='''print((4, 0) >= (4, 1))
''', explain='False.'),
    dict(level='easy', title='Start-up share', stmt='YARN start-up share of total.', inp='25.7, 6.6',
         code='''print(round(25.7 / (25.7 + 6.6) * 100), "%")
''', explain='80%.'),
    dict(level='easy', title='Utilisation', stmt='40 min/day on a 24 h cluster.', inp='40',
         code='''print(round(40 / 1440 * 100, 1), "%")
''', explain='2.8%.'),
    dict(level='medium', title='Weighted score', stmt='Score with weights.', inp='dicts',
         code='''w = {"a": 3, "b": 1}
s = {"a": 4, "b": 5}
print(sum(w[k] * s[k] for k in w))
''', explain='17.'),
    dict(level='medium', title='Filter runtimes', stmt='Runtimes with Spark 4+.', inp='dict',
         code='''r = {"Glue 5.1": (3, 5), "EMR": (4, 0), "Fabric 2.0": (4, 1)}
print([k for k, v in r.items() if v[0] >= 4])
''', explain='EMR, Fabric.'),
    dict(level='medium', title='Lag', stmt='Minor versions behind 4.3.', inp='4.0',
         code='''print(3 - 0)
''', explain='3 minor versions.'),
    dict(level='business', title='Idle cost', stmt='Monthly idle cost: cluster ₹400/h, used 0.7 h/day.', inp='400, 0.7',
         code='''print("₹", round((24 - 0.7) * 400 * 30))
''', explain='Serverless candidate.'),
    dict(level='business', title='People cost', stmt='Self-managed on-call: 0.5 FTE at ₹30 lakh/year.', inp='0.5, 30',
         code='''print("₹", 0.5 * 30, "lakh per year")
''', explain='Include it in TCO.'),
]

SCN_INTRO = 'Platform questions show architectural maturity.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“Name Spark platforms”',
        'Which platforms run Spark?',
        'examples?',
        '<p>Databricks and Microsoft Fabric (lakehouse platforms), Amazon EMR and AWS Glue, Google Dataproc / Serverless for Apache Spark, and open-source Spark on Kubernetes or YARN. They run the same engine with different versions, tools and pricing.</p>', 'Thinking each has a different API.') +
    scn('Data engineering', 'Mid-level', 'Runtime upgrade',
        'Your platform offers a new LTS runtime.',
        'plan?',
        '''<ul>
          <li>Read release notes and behaviour changes (e.g. ANSI mode).</li>
          <li>Run the test suite and sample jobs on the new runtime.</li>
          <li>Migrate job by job; keep rollback.</li>
        </ul>''', 'Switching all jobs at once.') +
    scn('Data engineering', 'Mid-level', 'Cost',
        'Spark costs doubled this quarter.',
        'investigate?',
        '''<ol>
          <li>Cost per pipeline and idle time.</li>
          <li>Move spiky jobs to serverless; autoscale clusters.</li>
          <li>Tune the top jobs (Module 8).</li>
        </ol>''', 'Buying reserved capacity first.') +
    scn('Architecture', 'Senior', 'Platform strategy',
        'Recommend a Spark platform for a growing company.',
        'approach?',
        '''<ul>
          <li>Requirements and TCO (licences + people).</li>
          <li>Benchmark a real pipeline on 2–3 candidates.</li>
          <li>Open formats and standard APIs to keep exit options.</li>
        </ul>''', 'Choosing by brand.')
)
