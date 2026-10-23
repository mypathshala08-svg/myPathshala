import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()

META = dict(
    module='13-hadoop-in-industry', lesson='03-hadoop-in-the-cloud-and-cloudera', n='13.3',
    module_label='Module 13 · Hadoop in industry today',
    title='Hadoop in the cloud, and Cloudera',
    desc='How Hadoop workloads run in the cloud and on Cloudera in 2026: object storage (S3, GCS, ADLS via s3a://, gs://, abfs://) instead of HDFS, separation of compute and storage, transient clusters, autoscaling, spot workers, cloud-aware committers, shared catalogs. Amazon EMR 7.14, Google Dataproc 2.3, Azure HDInsight 5.1 status, Cloudera Base on premises 7.3.2, hybrid set-ups, migration patterns and a cost calculator fed with our lab measurements. Architecture diagram, animations, quiz and interview scenarios.',
    og_desc='Rent a cluster for three hours, keep the data forever. How Hadoop runs on EMR, Dataproc, HDInsight and Cloudera today, with a cost calculator.',
    minutes=26, level='Intermediate',
    lead='Most new Hadoop-style work now runs on clusters that exist only while a job runs, reading data from cloud object storage. Many regulated companies still run Cloudera in their own data centres, often with the cloud on the side. This lesson explains the cloud pattern, compares the managed services as of October 2026, and puts numbers on always-on versus per-job clusters using measurements from our lab.',
    chips=['Platform versions checked Oct 2026', 'Architecture diagram + 2 animations', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Always-on vs transient: a cost and time calculator',
    intro='<p>Prices are <b>illustrative variables</b>, not quotes: change them to the numbers on your provider\'s price page. The structure of the comparison is what matters.</p>',
    code='''NODE_HOUR = 40.0            # illustrative Rs per worker-hour
workers, job_hours, nights = 20, 3, 30
setup = 0.25                # 15 minutes to create and terminate

always_on = workers * 24 * nights * NODE_HOUR
transient = workers * (job_hours + setup) * nights * NODE_HOUR
print(f"always-on : Rs {always_on:>9,.0f} a month")
print(f"transient : Rs {transient:>9,.0f} a month ({transient / always_on:.0%})")
busy = job_hours / 24
print(f"the always-on cluster is busy {busy:.0%} of the time")
''',
    anno=[
        ('transient = workers * (job_hours + setup) * nights * NODE_HOUR', 'You pay only while the cluster exists, including a few minutes to boot and shut down.'),
        ('busy = job_hours / 24', 'Utilisation decides the winner. A cluster busy 20 hours a day is cheaper to keep running.'),
    ],
    tasks=[
        dict(label='1 · Always-on vs transient', hint='Press <b>Run</b>. Then change <code>job_hours</code> to 20. Which option wins now?', code=None),
        dict(label='2 · Spot workers', hint='Keep 4 regular workers and make 16 spot workers 60% cheaper (illustrative). What fraction of the always-on cost is left?',
             code='''NODE_HOUR, hours, nights = 40.0, 3.25, 30
regular = 4 * hours * nights * NODE_HOUR
spot = 16 * hours * nights * NODE_HOUR * (1 - 0.60)
always_on = 20 * 24 * nights * NODE_HOUR
print(f"Rs {regular + spot:,.0f} = {(regular + spot) / always_on:.0%} of always-on")
'''),
        dict(label='3 · Storage: 3 copies vs object store', hint='100 TB of data. HDFS keeps 3 copies and disks at most 70% full. How many raw TB is that, and with RS-6-3 erasure coding (1.5x) instead?',
             code='''data_tb = 100
for name, factor in [("replication 3", 3.0), ("RS-6-3", 1.5)]:
    print(f"{name:13}: {data_tb * factor / 0.7:,.0f} TB of raw disk")
'''),
        dict(label='4 · Migration time', hint='Our lab copied 162 MB in 25.5 s with DistCp. How long would 50 TB take at that speed, and over a 10 Gbps link used at 70%?',
             code='''tb = 50
lab = 162 / 25.5                      # MB/s, measured in Lesson 12.2
link = 10 * 1000 / 8 * 0.7            # MB/s
for name, mb_s in [("lab speed", lab), ("10 Gbps", link)]:
    print(f"{name:9}: {tb * 1024 * 1024 / mb_s / 86400:6.1f} days")
'''),
        dict(label='5 · Spot the error', hint='This break-even calculation divides by the number of idle hours, which is zero for a cluster busy all day. Guard against it.',
             code='''busy_hours = 24
idle_hours = 24 - busy_hours
print("cost per idle hour:", 576000 / (idle_hours * 30))
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: compare the options with your own numbers',
    intro='<p>No cloud account is needed: this lesson did not create cloud resources. <code>cloud_vs_onprem.py</code> takes the throughput we measured in Lessons 12.2 and 12.3 and illustrative prices, and prints the three comparisons from Part 4. Put your provider\'s real prices into the variables at the top before using the numbers for a decision.</p>',
    items=[
        dict(title='Compute, storage and migration time', file='cloud_vs_onprem.py',
             cmd=rd('lab/cloud_vs_onprem.py') + '\n# Run:  python3 cloud_vs_onprem.py',
             output=rd('tx133.txt').strip(),
             note='Real output of the script. The prices inside it are illustrative placeholders; the measured inputs (6.4 MB/s DistCp in our lab) are real.'),
    ],
)

TRACE = dict(
    heading='Which URI scheme talks to which store?',
    intro='<p>Hadoop picks a FileSystem class from the scheme of the path. Follow four paths through the lookup.</p>',
    code='''schemes = {"hdfs": "DistributedFileSystem", "s3a": "S3AFileSystem",
           "gs": "GoogleHadoopFileSystem", "abfs": "AzureBlobFileSystem"}
paths = ["hdfs://namenode/data", "s3a://shop/data", "gs://shop/data", "abfs://c@acct.dfs.core.windows.net/data"]
for p in paths:
    scheme = p.split("://")[0]
    print(f"{scheme:5} -> {schemes[scheme]}")
''',
    notes={5: 'Scheme :: The part before :// decides the connector (fs.<scheme>.impl in core-site).',
           6: 'Same API :: Jobs call the FileSystem API; the store behind it changes.'},
)

WORKED_INTRO = 'Four cloud decisions from different industries, each with the numbers written out. All prices are illustrative.'
EXAMPLES = [
    dict(level='b', tag='Cost · media', title='A streaming company: always-on or nightly cluster?',
         problem='<p>A nightly recommendation job needs 30 workers for 4 hours. A worker costs ₹50 an hour (illustrative). Compare a month of an always-on cluster with a cluster created each night (add 15 minutes for start and stop).</p>',
         inp='30 workers · 4 h a night · ₹50/hour · 30 nights',
         approach=['Always-on: workers × 24 h × 30 nights × price.',
                   'Transient: workers × (4 + 0.25) h × 30 nights × price.',
                   'Compare the ratio.'],
         code='''always = 30 * 24 * 30 * 50
transient = 30 * 4.25 * 30 * 50
print(f"always-on Rs {always:,.0f}, transient Rs {transient:,.0f} ({transient / always:.0%})")
''', notes={2: 'Utilisation :: 4.25 of 24 hours is about 18%.'},
         tryit='If the same cluster also serves analysts from 9 to 6, it is busy 13 hours a day. Does transient still win?'),
    dict(level='i', tag='Storage · healthcare', title='A hospital archive: HDFS or object storage?',
         problem='<p>A hospital network keeps 40 TB of de-identified imaging metadata. On HDFS it needs 3 copies with disks at most 70% full, at ₹900 per raw TB-month; object storage costs ₹1,700 per TB-month (both illustrative). Which is cheaper per month?</p>',
         inp='40 TB · ×3 / 0.7 · ₹900 vs ₹1,700',
         approach=['Raw HDFS disk = 40 × 3 / 0.7.',
                   'Multiply each by its price.',
                   'Remember what each price includes (servers, power, staff vs a service).'],
         code='''raw = 40 * 3 / 0.7
print(f"HDFS {raw:.0f} TB raw: Rs {raw * 900:,.0f} | object store: Rs {40 * 1700:,.0f}")
''', notes={1: 'Headroom :: Lesson 12.3: keep HDFS disks below about 70% full.'},
         tryit='Patient-identifiable data may have to stay in a specific location under the hospital\'s policies: check that before comparing prices.'),
    dict(level='i', tag='Migration · telecom', title='How long to move 2 PB to the cloud?',
         problem='<p>A telecom operator wants to move 2 PB of call-record history. Its link to the cloud is 10 Gbps, and 70% can be used for the move. How many days does the bulk copy take?</p>',
         inp='2 PB · 10 Gbps · 70%',
         approach=['Usable speed in MB/s = 10,000 / 8 × 0.7.',
                   'Size in MB = 2 × 1024 × 1024 × 1024.',
                   'Days = size / speed / 86,400.'],
         code='''mb_s = 10 * 1000 / 8 * 0.7
size_mb = 2 * 1024 ** 3
print(f"{size_mb / mb_s / 86400:.0f} days at {mb_s:.0f} MB/s")
''', notes={1: 'Link :: Big migrations are network-bound, not Hadoop-bound.'},
         tryit='About a month. Teams run DistCp in waves and finish with -update passes (Lesson 12.2) for the data that changed meanwhile.'),
    dict(level='a', tag='Choice · fintech', title='Which platform for a payments analytics team?',
         problem='<p>A fintech must keep raw payment data in India, runs a steady 18-hour-a-day ETL, and has bursty fraud-model training a few days a month. Score three options: (A) Cloudera on-prem only, (B) cloud only, (C) hybrid: Cloudera on-prem for raw data and ETL, cloud for training on masked data.</p>',
         inp='3 options · 4 criteria',
         approach=['List the criteria: residency, steady load cost, burst cost, operations effort.',
                   'Score each option 1–3 (illustrative judgement).',
                   'Add up, then sanity-check the winner against the hard rule (residency).'],
         code='''scores = {"A on-prem": [3, 3, 1, 2], "B cloud": [2, 1, 3, 3], "C hybrid": [3, 3, 3, 1]}
for name, s in scores.items():
    print(f"{name:10} total {sum(s)}  (residency, steady, burst, ops) = {s}")
''', notes={1: 'Scores :: Residency can be met in the cloud too with an Indian region; check the rules, not just the score.'},
         tryit='Hybrid wins on fit but costs the most effort: two platforms, two security models. Many Indian banks still choose it.'),
]

QUIZ = mix([
    dict(q='What does "separation of compute and storage" mean in the cloud?', options=['Data and processing run on different continents', 'Data stays in object storage while clusters that process it are created and deleted independently', 'HDFS runs on separate disks', 'YARN runs without containers'], answer=1,
         why='The data outlives any cluster.'),
    dict(q='Which URI scheme reads Amazon S3 through Hadoop\'s connector?', options=['hdfs://', 's3a://', 'gs://', 'abfs://'], answer=1,
         why='gs:// is Google Cloud Storage, abfs:// is Azure Data Lake Storage Gen2.'),
    dict(q='Why do cloud jobs use special output committers or table formats?', options=['Object stores are read-only', 'A rename in object storage copies the data, so the classic rename-based commit is slow', 'HDFS committers need Kerberos', 'Parquet cannot be renamed'], answer=1,
         why='Examples: the S3A magic committer, or Iceberg committing by writing metadata.'),
    dict(q='Which statement about Azure HDInsight was true in October 2026?', options=['HDInsight 6.0 had just been released', 'HDInsight 5.1 was the only supported version, in maintenance mode', 'HDInsight on AKS was the recommended option', 'HDInsight 4.0 was still supported'], answer=1,
         why='HDInsight 4.0 retired on 31 Mar 2025 and HDInsight on AKS on 31 Jan 2025.'),
    dict(q='A cluster is busy 3 hours a day. Roughly what share of always-on compute cost does a per-night cluster cost (with 15 minutes of start/stop)?', options=['About 50%', 'About 14%', 'About 90%', 'Exactly 3%'], answer=1,
         why='3.25 / 24 ≈ 14%, before any spot discount.'),
    dict(q='Why are spot or preemptible workers usually safe for Spark and MapReduce tasks?', options=['They never fail', 'Lost tasks are simply rerun elsewhere, as long as the driver/AM is on a regular node', 'They have more memory', 'They store HDFS blocks'], answer=1,
         why='Lesson 8.6 showed a killed task being retried.'),
    dict(q='What is Cloudera Base on premises 7.3.2?', options=['A cloud-only service', 'A long-term-support Cloudera release for your own data centres (support through 2032)', 'Apache Hadoop 3.5', 'A replacement for Spark'], answer=1,
         why='It ships Hadoop 3.4, Spark 3.5, Iceberg support, Ozone and JDK 17 by default.'),
    dict(q='What usually limits a large on-prem-to-cloud migration?', options=['The number of YARN queues', 'Network bandwidth and change catch-up', 'The NameNode heap', 'Java version'], answer=1,
         why='2 PB over a 10 Gbps link at 70% takes about a month.'),
])

REVISION = [
    'Cloud pattern: data in <b>object storage</b> (S3, GCS, ADLS via <code>s3a://</code>, <code>gs://</code>, <code>abfs://</code>), clusters <b>transient</b> and <b>autoscaled</b>, metadata in a shared <b>catalog</b>.',
    'Trade-offs: no data locality; renames are copies (use cloud-aware committers or table formats); pay per hour; egress costs.',
    'Spot/preemptible workers for task nodes; keep the AM/driver on regular nodes.',
    'Oct 2026: EMR 7.14.0 (Hadoop 3.4.2, Spark 3.5.8, Iceberg 1.10.1); Dataproc 2.3.37 (Hadoop 3.3.6, Spark 3.5.3); HDInsight 5.1 maintenance mode; Cloudera Base on premises 7.3.2 LTS to 2032.',
    'Migration path: lift-and-shift → re-platform (transient, autoscale) → re-architect (lakehouse). Hybrid is common for regulated data.',
    'Illustrative calculator: 20 workers, 3 h a night → transient ≈ 14% of always-on; 100 TB on HDFS needs ≈ 429 TB raw disk.',
]
FAQ = [
    ('Is Hadoop still used in the cloud?', 'Its pieces are. Managed services such as Amazon EMR and Google Dataproc run YARN, Spark, Hive, HBase and other Hadoop-ecosystem projects, and Hadoop\'s FileSystem connectors (s3a, gs, abfs) are how those engines read cloud storage. What is used less is HDFS as the main store: data usually lives in object storage and clusters are temporary.'),
    ('What is the difference between HDFS and Amazon S3 for Hadoop jobs?', 'HDFS stores blocks on the cluster\'s own disks with three copies, gives data locality and cheap renames, but lives and dies with the cluster. S3 is a separately billed object store, independent of any cluster, without data locality and where a rename is a copy. Jobs switch by changing hdfs:// to s3a:// and using a suitable committer.'),
    ('What is a transient cluster?', 'A cluster created for a job or a batch window and deleted when the work finishes. Because the data is in object storage and table definitions are in a shared catalog, nothing is lost when the machines go away, and you pay only for the hours they ran.'),
    ('What does Cloudera offer today?', 'A supported distribution of the open-source data stack (Hadoop, Hive, Impala, Spark, HBase, Kafka, Ranger, Atlas and others) for your own data centres (Cloudera Base on premises, with 7.3.2 announced in March 2026 as an LTS release supported through 2032) and for public clouds, managed with Cloudera Manager. Hortonworks merged into Cloudera in 2019, and MapR\'s platform became HPE Ezmeral Data Fabric.'),
    ('Should a company move its Hadoop cluster to the cloud?', 'It depends on utilisation, data rules and skills. Bursty or mostly idle workloads usually save money on transient cloud clusters; steady, heavily used clusters may be cheaper on owned hardware; regulated data may need to stay in a specific location. Many organisations choose a hybrid. Compare with your own measured throughput and real prices, and treat this lesson\'s numbers as illustrative.'),
]

PRACTICE_INTRO = 'Cloud and Cloudera exercises using our lab measurements and illustrative prices.'
PROBLEMS = [
    dict(level='easy', title='Utilisation', stmt='A cluster runs jobs 6 hours a day. What percentage of the day is it busy?', inp='6 / 24',
         code='''print(f"{6 / 24:.0%} busy")
''', explain='25%: three quarters of an always-on cluster\'s cost pays for idle time.'),
    dict(level='easy', title='Change the path', stmt='Rewrite the input path hdfs://namenode/data/orders for S3 bucket "shop" and for GCS bucket "shop".', inp='one path, two stores',
         code='''path = "hdfs://namenode/data/orders"
rest = path.split("/", 3)[3]
print("s3a://shop/" + rest)
print("gs://shop/" + rest)
''', explain='s3a://shop/data/orders and gs://shop/data/orders: the job code stays the same.'),
    dict(level='easy', title='Raw disk for HDFS', stmt='How much raw disk does 25 TB of data need on HDFS with 3 copies and disks at most 70% full?', inp='25 × 3 / 0.7',
         code='''print(f"{25 * 3 / 0.7:.0f} TB")
''', explain='About 107 TB: object storage bills you for the 25 TB you store.'),
    dict(level='medium', title='Break-even hours', stmt='Transient clusters cost 15 extra minutes per run. Above how many busy hours a day does always-on become cheaper, if spot gives no discount?', inp='hours + 0.25 vs 24',
         code='''for h in [6, 12, 18, 23, 23.75, 24]:
    print(h, "transient cheaper" if h + 0.25 < 24 else "always-on cheaper or equal")
''', explain='Only above 23.75 hours: without other differences, per-run clusters win almost always on compute; in practice storage, start-up delays and staff time decide.'),
    dict(level='medium', title='Spot savings', stmt='A nightly job uses 10 workers for 5 hours at ₹40/hour; 8 of them can be spot at 60% off (illustrative). What is the monthly saving?', inp='10 workers · 5 h · 30 nights',
         code='''full = 10 * 5 * 30 * 40
spot = 2 * 5 * 30 * 40 + 8 * 5 * 30 * 40 * 0.4
print(f"Rs {full:,.0f} -> Rs {spot:,.0f}, saving Rs {full - spot:,.0f}")
''', explain='₹60,000 → ₹31,200, saving ₹28,800 a month (illustrative), as long as reruns after reclaimed workers stay rare.'),
    dict(level='medium', title='Transfer at lab speed', stmt='At our lab\'s DistCp speed (162 MB in 25.5 s), how many hours does a 100 GB daily increment take?', inp='100 GB · 6.35 MB/s',
         code='''mb_s = 162 / 25.5
print(f"{100 * 1024 / mb_s / 3600:.1f} hours")
''', explain='About 4.5 hours on our laptop lab; production clusters copy with many maps in parallel and much faster disks and networks.'),
    dict(level='business', title='Idle cluster alarm', stmt='A forgotten 50-worker cluster at ₹40/hour (illustrative) runs over a long weekend of 72 hours. What does it cost, and what setting prevents it?', inp='50 × 72 × ₹40',
         code='''print(f"Rs {50 * 72 * 40:,}")
''', explain='₹1,44,000 for nothing; enable auto-termination or an idle timeout and tag clusters with an owner.'),
    dict(level='advanced', title='Pick the platform', stmt='Write a function that suggests on-prem, cloud or hybrid from three answers: data must stay on own premises (yes/no), average utilisation (0–1), burstiness (low/high).', inp='3 inputs',
         code='''def suggest(on_prem_rule, utilisation, burst):
    if on_prem_rule and burst == "high":
        return "hybrid: regulated data on-prem, masked data to the cloud for peaks"
    if on_prem_rule:
        return "on-prem (e.g. Cloudera Base)"
    if utilisation > 0.7 and burst == "low":
        return "compare carefully: steady load can be cheaper on owned hardware"
    return "cloud with transient clusters"
for case in [(True, 0.8, "high"), (False, 0.15, "high"), (False, 0.85, "low"), (True, 0.5, "low")]:
    print(case, "->", suggest(*case))
''', explain='A simple rule of thumb in code. Real decisions also weigh skills, contracts and exit costs.'),
]

SCN_INTRO = 'Cloud-migration and platform questions are common for senior data engineers and architects.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Cloud · basics</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“How is running Spark on EMR or Dataproc different from our Hadoop cluster?”</h4>
      <p class="scn__situation">An interviewer checks whether you understand the cloud pattern.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> compute–storage separation.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Same engines (YARN, Spark, Hive), but data in object storage via s3a:// or gs://, not HDFS.</li>
          <li>Clusters can be transient and autoscaled; you pay per hour; spot workers for task nodes.</li>
          <li>Differences to handle: no data locality, renames are copies (use the right committer), shared catalog outside the cluster.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Migration · design</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Plan the migration of a 1 PB on-prem cluster to the cloud</h4>
      <p class="scn__situation">Hundreds of Hive tables, nightly Spark and MapReduce jobs, a 6-month deadline.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> phasing and risk control.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Inventory tables, jobs, owners and dependencies; decide what to retire.</li>
          <li>Bulk copy with DistCp in waves, keep in sync with -update or snapshot-diff; migrate the metastore.</li>
          <li>Move jobs table by table with parallel runs and result comparison; then switch, then decommission. Estimate network time first (1 PB at 10 Gbps ≈ 2 weeks of pure transfer).</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Cost · operations</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>“Our cloud bill doubled after moving off Hadoop. Why?”</h4>
      <p class="scn__situation">A manager expected savings.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> cloud cost habits.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Lift-and-shift kept always-on clusters sized for peak; enable autoscaling, auto-termination and spot task nodes.</li>
          <li>Check egress, small files and full-table scans (use Parquet/ORC, partitioning).</li>
          <li>Tag resources per team and set budgets and alerts.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Platform · strategy</span><span class="scn__tag scn__tag--level">Architect</span></div>
      <h4>A bank asks: Cloudera on-prem, cloud, or both?</h4>
      <p class="scn__situation">Regulated customer data, steady ETL, bursty data-science work.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> balanced reasoning without legal claims.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Start from data rules (confirmed with compliance), then utilisation and burst patterns.</li>
          <li>Steady, regulated workloads fit on-prem (e.g. Cloudera Base with Ranger/Atlas); bursts fit cloud with masked data.</li>
          <li>Plan one identity, one catalog and one policy model across both, or the hybrid becomes two silos.</li>
        </ul>
      </div></details>
    </article>
'''
