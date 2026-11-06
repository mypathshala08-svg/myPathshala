import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l121_platforms.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)

PL = [('Databricks', 'DBR 19 → Spark 4.2', 'acc'), ('Fabric', 'Runtime 2.0 → 4.1', 'blue'), ('EMR', 'Spark 4.0.2', 'amber'),
      ('Dataproc', 'Runtime 3.0 → 4.0.1', 'green'), ('Glue', '5.1 → 3.5.6', 'violet'), ('Open source', '4.3.0', 'card')]
def grid(x, y, hi=None):
    o = ''
    for k, (n, v, tone) in enumerate(PL):
        o += opbox(x + (k % 3) * 112, y + (k // 3) * 42, n, v, 'acc' if hi == n else tone, 104, 34)
    return o

# ---------------------------------------------------------------- story
sc_ = (t(14, 22, 'Spark versions on platforms (Nov 2026)', 7.4, 'ink2', anchor='start', bold=True) + grid(14, 32) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured: same job, 3 targets', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('local[4]  : start 7.5, run 2.9 s', 'green'), ('standalone: start 10.7, run 6.3', 'blue'),
           ('YARN      : start 25.7, run 6.6', 'amber'), ('same result: 830000166', 'green'),
           ('code changed: 0 lines', 'green'), ('only --master changed', 'violet')])))
scene_svg = scene('Most companies run Spark through a platform such as Databricks, Microsoft Fabric, Amazon EMR, Google Dataproc or AWS Glue, each shipping its own Spark version. We ran one unchanged PySpark job on local mode, a standalone cluster and YARN, and compared the platforms’ current Spark versions from their documentation.', sc_,
                  'The code stays the same; <tspan font-weight="700" class="s-acc">the platform</tspan> decides version, cost and operations.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Which Spark should we buy?”</h2>
  <div class="story">
    <p class="narration">TiffinGo has outgrown its self-managed cluster. The CTO received three proposals: Databricks, the cloud provider’s managed Spark, and “keep running it ourselves on Kubernetes”. Each vendor claimed to be “the best Spark”.</p>

{scene_svg}

K> Sir, isn’t Spark just Spark? Why do these platforms differ so much?
A> The engine is the same open-source Apache Spark (sometimes with vendor additions). What differs is everything around it: which Spark version you get, how clusters start and scale, notebooks, security, table formats, cost model and who gets paged at night.
R> Can we see that the code really stays the same?
A> We run one job unchanged on three targets from this course, then compare what each major platform ships today, from their official pages. Lab outputs are real (Spark 4.3.0); platform facts are as of November 2026.
  </div>
</section>
'''

lv = '''
LEVELS> Spark platforms at three levels
L1> Cooking at home or eating out
      <ul>
        <li>Self-managed Spark is cooking at home: cheapest ingredients, all the work is yours. A managed platform is a restaurant: you order, they cook, you pay for the service.</li>
        <li>Serverless is a food-delivery app: you do not even see a kitchen; you pay per dish.</li>
      </ul>
L2> The main families
      <ul>
        <li><b>Lakehouse platforms</b>: Databricks, Microsoft Fabric (notebooks, jobs, catalogs, Delta, governance).</li>
        <li><b>Managed clusters / serverless</b>: Amazon EMR (on EC2, EKS, Serverless), Google Dataproc and Serverless for Apache Spark, AWS Glue for ETL.</li>
        <li><b>Self-managed</b>: open-source Spark on Kubernetes (Spark Operator) or YARN.</li>
      </ul>
L3> What we measured and found
      <ul>
        <li>One job, zero code changes: same result on local[4], standalone and YARN; start-up 7.5 s, 10.7 s and 25.7 s.</li>
        <li>Platform Spark versions lag open source: open-source 4.3.0; Databricks Runtime 19 has 4.2.0; Fabric Runtime 2.0 has 4.1; EMR 4.0.2; Dataproc Serverless runtime 3.0 has 4.0.1; Glue 5.1 is still on 3.5.6.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Spark platforms</h2>
''' + def_block(
    'A <b>Spark platform</b> packages Apache Spark with infrastructure and services: cluster provisioning and autoscaling (or serverless execution), a curated <b>runtime</b> that fixes the Spark, Scala, Java and Python versions plus connectors, development tools (notebooks, IDE integration, Spark Connect), job orchestration, data catalogs and governance, table formats, security integration and monitoring. Platforms differ in how close they track open-source releases, in proprietary engine optimisations (for example vectorised native execution), in pricing (per instance-hour, per compute unit, per job or per data processed) and in portability. Applications written against the standard DataFrame and SQL APIs usually move between platforms with configuration changes; platform-specific features (proprietary SQL, catalogs, utilities) create lock-in.',
    'A Spark platform is Spark plus everything needed to run it in a company: machines that start and stop by themselves, a chosen Spark version, notebooks, schedulers, security and monitoring. Your DataFrame code mostly stays the same; you choose a platform for cost, convenience, version and the tools around it.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Runtime', 'Bundle of Spark + libraries a platform ships.'),
    ('LTS', 'Long-term-support runtime version.'),
    ('Serverless Spark', 'No clusters to manage; pay per job.'),
    ('Lakehouse', 'Tables on object storage + warehouse features.'),
    ('Catalog', 'Central list of tables and permissions.'),
    ('Autoscaling', 'Platform adds/removes workers.'),
    ('Lock-in', 'Code tied to one vendor’s features.'),
    ('DBU / CU', 'Vendor compute billing units.'),
]) + '''

  <h3>Major platforms and their Spark (November 2026)</h3>
''' + table(['Platform', 'Latest Spark offered', 'Model', 'Notes'], [
    ['Apache Spark (open source)', '4.3.0 (30 Oct 2026)', 'Self-managed: K8s, YARN, standalone', 'Newest features first'],
    ['Databricks', 'DBR 19 → Spark 4.2.0; 18 LTS → 4.1.0', 'Lakehouse, clusters + serverless', 'Unity Catalog, Photon, Delta'],
    ['Microsoft Fabric', 'Runtime 2.0 → Spark 4.1 (Java 21, Python 3.13, Delta 4.2)', 'SaaS lakehouse', 'Runtime 1.3 (Spark 3.5) end of support announced'],
    ['Amazon EMR', 'Spark 4.0.2 (GA mid-2026)', 'EC2, EKS, Serverless', 'Iceberg v3, Lake Formation'],
    ['Google Serverless for Apache Spark', 'Runtime 3.0 → Spark 4.0.1 (Java 21, Python 3.12)', 'Serverless batches + sessions', 'Also Dataproc clusters'],
    ['AWS Glue', 'Glue 5.1 → Spark 3.5.6 (Python 3.11)', 'Serverless ETL jobs', 'Not yet on Spark 4'],
], minw=680) + '''
  <p class="muted">Sources (checked 5 Nov 2026): <a href="https://spark.apache.org/news/spark-4-3-0-released.html">Apache Spark 4.3.0 news</a>, <a href="https://docs.databricks.com/release-notes/cluster-images/index.html">Databricks Runtime release notes</a>, <a href="https://learn.microsoft.com/en-us/fabric/data-engineering/lifecycle">Fabric runtime lifecycle</a>, <a href="https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-emr-apache-spark">Amazon EMR Spark 4.0.2</a>, <a href="https://docs.cloud.google.com/dataproc-serverless/docs/concepts/versions/spark-runtime-3.0">Serverless for Apache Spark runtime 3.0</a>, <a href="https://aws.amazon.com/about-aws/whats-new/2026/04/aws-glue-5-1-all-govcloud-commercial-regions/">AWS Glue 5.1</a>. Versions change often; check before deciding.</p>
''' + lv + '''
EXAM> “How would you choose a Spark platform?” Start from requirements: data location and cloud, team skills, latency and scale, governance and security, required Spark version and table format, and cost model. Compare managed lakehouses (Databricks, Fabric), cloud-managed Spark (EMR, Dataproc, Glue) and self-managed Spark on Kubernetes. Keep code on standard DataFrame/SQL APIs and open table formats to stay portable, and benchmark a real workload before committing.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Choosing by situation</h2>
''' + table(['Situation', 'Often a good fit', 'Why'], [
    ['Many analysts + engineers, governance needed', 'Databricks or Fabric', 'Notebooks, catalog, SQL, ML in one place'],
    ['Already deep in one cloud, batch ETL', 'EMR / Dataproc / Glue', 'Native IAM, storage, billing'],
    ['Spiky, occasional jobs', 'Serverless Spark (EMR Serverless, Google Serverless, Glue)', 'No idle clusters'],
    ['Strict control, existing Kubernetes', 'Open-source Spark on K8s', 'Newest Spark, no licence fee, more ops work'],
    ['Small data (under a few GB)', 'Maybe no Spark at all', 'DuckDB/Polars on one machine (Lesson 12.2)'],
], minw=620) + '''
WARN> Check the Spark version before you plan features. In November 2026 a lesson written for Spark 4.3 could not run unchanged on AWS Glue (3.5.6), and even the newest Databricks runtime was one minor version behind open source. Also beware of “free” proprietary helpers (vendor-only SQL functions, file utilities, magic commands): they are convenient and they are what makes moving platforms expensive later.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>One job, three targets</h2>
  <p>All outputs are real: Spark 4.3.0. The job aggregates 20 million generated orders into 6 cities. It never mentions a cluster; only the <code>--master</code> given at launch changes. Our host has 2 physical CPUs, so the clusters are not faster here; the point is portability and start-up cost.</p>
''' + stepper([
    ('Step 1 · The job',
     code('python', 'same_job.py', 'spark = SparkSession.builder.appName("tiffingo-same-job").getOrCreate()\ndf = spark.range(0, 20_000_000, 1, 8).select((F.col("id") % 6).alias("city"), (F.col("id") % 500).alias("amount"))\nr = df.groupBy("city").agg(F.sum("amount").alias("rev")).orderBy("city").collect()'),
     'No master, no memory settings, no paths tied to a machine. This is what portable Spark code looks like: platform choices come from the launcher or the platform’s job definition.'),
    ('Step 2 · Local, standalone, YARN',
     code('bash', 'run', 'PYSPARK_SUBMIT_ARGS="--master local[4] pyspark-shell" python same_job.py\nspark-submit --master spark://spark-master:7077 same_job.py\nspark-submit --master yarn --num-executors 2 --executor-cores 1 --executor-memory 768m same_job.py', sec('## local[4]')),
     'Identical result on all three (city 0 revenue 830,000,166). Start-up time grew with the amount of machinery: 7.5 s locally, 10.7 s on the standalone cluster, <b>25.7 s</b> on YARN (staging files to HDFS, starting an ApplicationMaster, then executors). Managed platforms hide this with pre-warmed pools or serverless start-up, which is part of what you pay for.'),
    ('Step 3 · What the platform decides',
     code('text', 'platform runtimes', 'Databricks Runtime 19     -> Apache Spark 4.2.0  (Jul 2026)\nDatabricks Runtime 18 LTS -> Apache Spark 4.1.0  (Jun 2026)\nFabric Runtime 2.0        -> Apache Spark 4.1, Java 21, Python 3.13, Delta 4.2\nAmazon EMR                -> Apache Spark 4.0.2 (GA 2026)\nServerless for Apache Spark runtime 3.0 -> Spark 4.0.1, Java 21, Python 3.12\nAWS Glue 5.1              -> Apache Spark 3.5.6, Python 3.11\nApache Spark (OSS)        -> 4.3.0 (30 Oct 2026)'),
     'From the platforms’ own pages (sources above). A feature from Lesson 12.3, such as Spark 4.3’s <code>ASOF JOIN</code>, simply does not exist yet on most platforms. Conversely, platforms add their own features (Photon, Unity Catalog, Lake Formation permissions) that open source does not have.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('local[4]   start 7.5 s  query 2.9 s', G), ('standalone start 10.7 s query 6.3 s', W), ('yarn       start 25.7 s query 6.6 s', Y)], size=7.0),
    term([('same result everywhere:', W), ('first 830000166', G), ('code changed: 0 lines', G)], size=7.4),
    term([('OSS 4.3.0 | DBR 19: 4.2.0', W), ('Fabric RT 2.0: 4.1 | EMR: 4.0.2', W), ('Google RT 3.0: 4.0.1 | Glue 5.1: 3.5.6', Y)], label='vendor documentation · Nov 2026', size=7.0),
    term([('pick by: data, team, cost,', W), ('governance, version, lock-in', W)], label='summary', size=7.4),
]
B1 = [
    t(180, 14, 'More machinery, slower start', 9.4, bold=True) + ''.join(box(76, 40 + k * 26, v * 10, 18, tone, rx=3) + t(72, 53 + k * 26, n, 7.2, 'ink', anchor='end', bold=True) for k, (n, v, tone) in enumerate([('local', 7.5, 'green'), ('standalone', 10.7, 'blue'), ('YARN', 25.7, 'amber')])) + cap('Start-up seconds (bars).', '', 'blue', y=144, h=30),
    t(180, 14, 'Portable code', 9.4, bold=True) + flow([('same_job.py', 'no master', 'green'), ('--master', 'local/spark/yarn', 'violet'), ('same result', '830000166', 'green')], y=50, w=96, gap=16) + cap('Launcher decides where.', '', 'green', y=144, h=30),
    t(180, 14, 'Versions differ', 9.4, bold=True) + grid(14, 36) + cap('Check before you design.', '', 'amber', y=144, h=30),
    t(180, 14, 'What you really choose', 9.4, bold=True) + ''.join(opbox(14 + (k % 3) * 112, 40 + (k // 3) * 42, n, '', tone, 104, 30) for k, (n, tone) in enumerate([('version', 'blue'), ('ops work', 'amber'), ('cost model', 'violet'), ('governance', 'green'), ('tools', 'blue'), ('lock-in', 'red')])) + cap('Engine is the same.', '', 'green', y=144, h=30),
]
see_caps = ['Start-up per target.', 'Same code, same result.', 'Platform versions.', 'Decision factors.']
behind_caps = ['Infrastructure cost.', 'Portability.', 'Runtime lag.', 'Choosing a platform.']
two = anim_two('Spark platforms', 'Same engine, different packaging', 'Real outputs and facts', 'What it means', see, B1, see_caps, behind_caps)

e1 = (t(180, 22, 'Three proposals for TiffinGo', 9.4, bold=True) + t(180, 56, 'lakehouse, cloud Spark, self-managed', 8.2, 'ink2') + cap('All claim “best Spark”.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Write requirements first', 9.4, bold=True) + t(180, 56, 'data size, users, SLAs, governance', 8.2, 'ink2') + cap('Not features lists.', '', 'green', y=150, h=34))
e3 = (t(180, 22, 'Benchmark one real pipeline', 9.4, bold=True) + t(180, 56, 'same code on each trial', 8.4, 'ink2') + cap('Time and cost per run.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Count people cost too', 9.4, bold=True) + t(180, 56, 'self-managed needs on-call', 8.4, 'ink2') + cap('Licences vs salaries.', '', 'amber', y=150, h=34))
e5 = (t(180, 22, 'Decide with numbers', 9.4, 'acc', bold=True) + t(180, 56, 'keep open formats for exit', 8.4, 'ink2') + cap('Reversible choice.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Choosing a platform',
              'A structured platform decision. (Typical.)',
              'Platform choice', 'Choose a Spark platform from requirements, a real benchmark and total cost', [e1, e2, e3, e4, e5],
              ['Proposals.', 'Requirements.', 'Benchmark.', 'People.', 'Decide.'],
              hid='scenario-choose')
b1 = (t(180, 22, 'Job uses a new Spark function', 9.4, bold=True) + t(180, 56, 'works on the laptop (4.3)', 8.4, 'ink2') + cap('Deploy to the platform.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Fails: function not found', 9.4, bold=True) + t(180, 56, 'platform runs Spark 4.0', 8.4, 'ink2') + cap('Version mismatch.', '', 'red', y=150, h=34))
b3 = (t(180, 22, 'Pin local = platform version', 9.4, bold=True) + t(180, 56, 'pip install pyspark==4.0.*', 8.4, 'ink', mono=True) + cap('Test what you deploy.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'CI against the runtime', 9.4, bold=True) + t(180, 56, 'or Spark Connect to the platform', 8.4, 'ink2') + cap('Lesson 11.3.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Track runtime upgrades', 9.4, 'acc', bold=True) + t(180, 56, 'plan LTS moves yearly', 8.4, 'ink2') + cap('No surprises.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Works on my laptop, not on the platform',
              'Runtime version mismatches. (Typical.)',
              'Version drift', 'Develop and test against the same Spark version as the platform runtime', [b1, b2, b3, b4, b5],
              ['New func.', 'Fails.', 'Pin.', 'CI.', 'Upgrades.'],
              hid='scenario-version')
u1 = (t(180, 22, 'Nightly ETL, 40 minutes/day', 9.4, bold=True) + t(180, 56, 'cluster idle 23 hours', 8.4, 'ink2') + cap('Paying for idle.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Move to serverless Spark', 9.4, bold=True) + t(180, 56, 'pay per job run', 8.4, 'ink2') + cap('No idle cost.', '', 'green', y=150, h=34))
u3 = (t(180, 22, 'Start-up latency', 9.4, bold=True) + t(180, 56, 'seconds to minutes per job', 8.4, 'ink2') + cap('Fine for nightly.', '', 'amber', y=150, h=34))
u4 = (t(180, 22, 'Keep a cluster for BI', 9.4, bold=True) + t(180, 56, 'interactive needs warm compute', 8.4, 'ink2') + cap('Mix models.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Review the bill monthly', 9.4, 'acc', bold=True) + t(180, 56, 'cost per pipeline', 8.4, 'ink2') + cap('FinOps.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Paying for an idle cluster',
              'Serverless vs always-on clusters. (Typical.)',
              'Serverless', 'Serverless Spark removes idle cost for scheduled jobs; keep warm compute for interactive work', [u1, u2, u3, u4, u5],
              ['Idle.', 'Serverless.', 'Latency.', 'Mix.', 'Review.'],
              hid='scenario-serverless')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Same engine, different packaging</h2>
  <p>Left: real outputs and platform facts. Right: what they mean.</p>
''' + two + '''
  <p>Three live scenarios follow: choosing a platform, a version mismatch, and idle clusters.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Platforms at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'lake', 12, 'blue', bold=True) + t(60, 58, 'house', 7.4, 'ink2'),
    '1. Company-wide lakehouse',
    'Engineers, analysts and data scientists share one governed platform.',
    ['Notebooks', '*platform', 'Governed tables']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'ETL', 12, 'green', bold=True) + t(60, 58, 'serverless', 7.4, 'ink2'),
    '2. Serverless ETL',
    'Scheduled jobs run on EMR Serverless, Google Serverless Spark or Glue without clusters.',
    ['Schedule', '*serverless', 'Tables']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'K8s', 12, 'violet', bold=True) + t(60, 58, 'own', 7.4, 'ink2'),
    '3. Self-managed on Kubernetes',
    'Tech companies run open-source Spark next to their services for control and newest versions.',
    ['Spark Operator', '*K8s', 'Jobs']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'multi', 11, 'acc', bold=True) + t(60, 58, 'cloud', 7.4, 'ink2'),
    '4. Multi-cloud portability',
    'Open table formats and standard APIs let the same pipeline run on two clouds.',
    ['Iceberg/Delta', '*standard APIs', 'Any platform']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'FinOps', 10, 'acc', bold=True) + t(60, 58, 'cost', 7.4, 'ink2'),
    '5. Cost management',
    'Teams track cost per pipeline and move workloads between cluster and serverless.',
    ['Billing', '*per pipeline', 'Right model']) + '''
  <p class="muted">Examples are simplified. Platform facts change often; verify with vendor documentation.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> deploy modes in <a href="../../11-spark-in-production/01-spark-submit-and-deploy-modes/">11.1</a>, YARN and Kubernetes in <a href="../../11-spark-in-production/02-spark-on-yarn-and-kubernetes/">11.2</a>, table formats in <a href="../../11-spark-in-production/05-delta-lake-and-iceberg/">11.5</a>.</p></div>
'''
EXTRA = ''
_x = os.path.join(HERE, '_extra.py')
if os.path.exists(_x): exec(open(_x).read())
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + EXTRA + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
