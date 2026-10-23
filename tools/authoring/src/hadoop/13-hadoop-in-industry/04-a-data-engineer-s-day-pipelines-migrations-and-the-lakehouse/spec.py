import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()

META = dict(
    module='13-hadoop-in-industry', lesson='04-a-data-engineer-s-day-pipelines-migrations-and-the-lakehouse', n='13.4',
    module_label='Module 13 · Hadoop in industry today',
    title='A data engineer\'s day: pipelines, migrations and the lakehouse',
    desc='What a data engineer does all day, and the lakehouse run for real on Hadoop: an Apache Iceberg 1.10 table on HDFS with Spark 4.0 on YARN. 500,000 orders loaded, SQL DELETE and UPDATE (459,636 orders, revenue ₹12,493,729), three snapshots, time travel back to the original numbers, schema evolution, hidden day partitions. Pipelines (bronze/silver/gold, Airflow DAGs, idempotency, backfills, data contracts, quality checks), migrations from Hadoop to the lakehouse (inventory, DistCp, dual-run, reconcile, cut-over), Iceberg vs Delta vs Hudi, Python simulation, quiz and interview scenarios.',
    og_desc='Fix a month of wrong prices with SQL and still read last week\'s numbers: a real Iceberg lakehouse on Hadoop, and a data engineer\'s day around it.',
    minutes=32, level='Intermediate',
    lead='Most Hadoop knowledge ends up used in one job: data engineering. This lesson follows a data engineer through a working day, from a failed overnight pipeline to a migration check, and runs the modern piece of the stack on our own cluster: an Apache Iceberg lakehouse table on HDFS that supports updates, deletes, snapshots and time travel.',
    chips=['Real Iceberg table on HDFS', 'Architecture diagram + 2 animations', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='A table that keeps its history',
    intro='<p>A copy-on-write table in a few lines of Python: every change writes a new list of rows (new "files") and records a snapshot. The numbers are our lab\'s real totals, aggregated per item.</p>',
    code='''# per item: (orders, price) from our 500,000-order table
base = {"chai": (149669, 15), "coffee": (40364, 20), "dosa": (49927, 45), "idli": (44774, 30),
        "poha": (45336, 25), "samosa": (69884, 18), "thali": (30292, 80), "vada pav": (69754, 20)}
snapshots = []

def commit(op, rows):
    snapshots.append((len(snapshots) + 1, op, dict(rows)))     # copy-on-write: a whole new version

def stats(rows):
    return sum(n for n, p in rows.values()), sum(n * p for n, p in rows.values())

commit("append", base)
v2 = {k: v for k, v in snapshots[-1][2].items() if k != "coffee"}          # DELETE coffee
commit("overwrite", v2)
v3 = {k: (n, 18 if k == "chai" else p) for k, (n, p) in snapshots[-1][2].items()}   # UPDATE chai
commit("overwrite", v3)

for sid, op, rows in snapshots:
    print(sid, op.ljust(9), "orders %d, revenue %d" % stats(rows))
print("time travel to 1:", "orders %d, revenue %d" % stats(snapshots[0][2]))
''',
    anno=[
        ('    snapshots.append((len(snapshots) + 1, op, dict(rows)))     # copy-on-write: a whole new version', "Like Iceberg's copy-on-write: a change writes new data and a new snapshot; the old one is untouched."),
        ('v3 = {k: (n, 18 if k == "chai" else p) for k, (n, p) in snapshots[-1][2].items()}   # UPDATE chai', 'Our real UPDATE: chai from 15 to 18 rupees.'),
        ('print("time travel to 1:", "orders %d, revenue %d" % stats(snapshots[0][2]))', 'VERSION AS OF the first snapshot gave 500,000 and 12,852,002 in the lab.'),
    ],
    tasks=[
        dict(label='1 · Three snapshots', hint='Press <b>Run</b>. Do the numbers match the lab (500000 / 12852002 and 459636 / 12493729)?', code=None),
        dict(label='2 · Idempotent load', hint='<b>Predict first:</b> the same day is loaded twice by a retry. Compare append with overwrite-the-partition.',
             code='''table_append, table_overwrite = [], {}
day, rows = "2026-09-14", ["o1", "o2", "o3"]
for attempt in range(2):                      # the first run "failed" after writing, so it is retried
    table_append += rows                       # blind append
    table_overwrite[day] = list(rows)          # overwrite this day's partition
print("append   :", len(table_append), "rows")
print("overwrite:", sum(len(v) for v in table_overwrite.values()), "rows")
'''),
        dict(label='3 · Backfill plan', hint='A fix must be re-run for 1–30 September. Each day takes 7 minutes and Airflow may run 4 days at a time. How long?',
             code='''import math
days, minutes_per_day, parallel = 30, 7, 4
print(math.ceil(days / parallel) * minutes_per_day, "minutes")
'''),
        dict(label='4 · Reconcile', hint='Old Hive job vs new Spark job for the same day. Report which items differ.',
             code='''old = {"chai": 149669, "dosa": 49927, "idli": 44774, "poha": 45336}
new = {"chai": 149669, "dosa": 49927, "idli": 44770, "poha": 45336}
for item in sorted(old):
    if old[item] != new.get(item):
        print("MISMATCH", item, old[item], new.get(item))
print("totals", sum(old.values()), sum(new.values()))
'''),
        dict(label='5 · Spot the error', hint='This quality check crashes when a partner sends an empty file. Make it fail with a clear message instead.',
             code='''rows = []
avg_amount = sum(rows) / len(rows)
print("average", avg_amount)
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: an Iceberg lakehouse on the Module 8 lab',
    intro='<p>Use the Module 8 lab with Spark 4.0.4 installed as in Lesson 13.2. Download the Iceberg runtime for Spark 4.0 (<code>iceberg-spark-runtime-4.0_2.13-1.10.2.jar</code>, 47 MB) from Maven Central (<code>repo1.maven.org/maven2/org/apache/iceberg/</code>) and copy it into the namenode container. The table lives in <code>hdfs://namenode/lakehouse</code>. Keep at least a few GB free on your disk: our first attempt failed because the disk was 97% full.</p>',
    items=[
        dict(title='Load, change, time travel, evolve', file='lakehouse_iceberg.py',
             cmd=rd('lab/lakehouse_iceberg.py') + '\n# Inside lab8-namenode-1 (SPARK_HOME = where you unpacked Spark 4.0.4):\n#   export HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop\n#   $SPARK_HOME/bin/spark-submit --master yarn --num-executors 3 --executor-memory 768m \\\n#     --executor-cores 1 --driver-memory 768m \\\n#     --jars iceberg-spark-runtime-4.0_2.13-1.10.2.jar lakehouse_iceberg.py\n#   hdfs dfs -count /lakehouse/canteen/orders/data /lakehouse/canteen/orders/metadata',
             output=rd('tx134.txt').strip(),
             note='Real output from our cluster (YARN client lines removed). Snapshot IDs are random and differ on every run; the counts and totals are the same.'),
    ],
)

TRACE = dict(
    heading='A backfill that cannot double count',
    intro='<p>Three days are loaded, day 2 is reloaded after a fix. Watch the partition dictionary: the reload replaces day 2 instead of adding to it.</p>',
    code='''table = {}
loads = [("09-01", 120), ("09-02", 95), ("09-03", 110), ("09-02", 98)]
for day, rows in loads:
    table[day] = rows
total = sum(table.values())
print(table, total)
''',
    notes={3: 'Overwrite :: Each load owns one partition; the second 09-02 load replaces the first.',
           4: 'Result :: 328 rows, not 426: the retry did not double count.'},
)

WORKED_INTRO = 'Four everyday data-engineering calculations from different industries.'
EXAMPLES = [
    dict(level='b', tag='Pipelines · backfill', title='How long will the backfill take?',
         problem='<p>A logistics company finds a bug in its delivery-time pipeline for the last 45 days. One day takes 12 minutes on the cluster; the team can run 5 days in parallel without hurting other jobs. How long is the backfill, and when is it done if it starts at 19:00?</p>',
         inp='45 days · 12 min/day · 5 parallel',
         approach=['Waves = days ÷ parallel, rounded up.', 'Time = waves × minutes per day.', 'Add to the start time.'],
         code='''import math
waves = math.ceil(45 / 5)
minutes = waves * 12
print(f"{waves} waves, {minutes} minutes, done at {19 + minutes // 60}:{minutes % 60:02d}")
''', notes={2: 'Waves :: 9 waves of 5 days each.'},
         tryit='With 10 in parallel it is 60 minutes, if the cluster has room. Idempotent steps are what make this safe.'),
    dict(level='i', tag='Migration · plan', title='A migration timeline',
         problem='<p>A telecom operator moves 600 Hive tables and 900 jobs from on-prem Hadoop to an Iceberg lakehouse. A team migrates 40 jobs a week; every batch then dual-runs for 2 weeks before cut-over; the data copy (DistCp + snapshot diffs) starts at week 0 and takes 6 weeks. When can the old cluster be switched off?</p>',
         inp='900 jobs · 40/week · 2-week dual-run · 6-week copy',
         approach=['Weeks to rewrite all jobs = 900 ÷ 40.', 'The last batch still needs its 2 weeks of dual-running.', 'The copy must finish too; take the later date.'],
         code='''import math
rewrite = math.ceil(900 / 40)
last_cutover = rewrite + 2
print(f"jobs rewritten by week {rewrite}, last cut-over week {max(last_cutover, 6)}")
''', notes={2: 'Dual-run :: Old and new run side by side until results match.'},
         tryit='Old clusters usually stay a few more weeks in read-only mode for audits before decommissioning.'),
    dict(level='i', tag='Migration · reconcile', title='Do the two systems agree?',
         problem='<p>An insurer dual-runs claims aggregation. Old Hive output: 1,20,450 claims, ₹84.3 crore. New Spark output: 1,20,438 claims, ₹84.29 crore. Is the difference acceptable if the rule is "counts exact, money within 0.01%"?</p>',
         inp='counts and totals from both systems',
         approach=['Compare counts exactly.', 'Compare money as a percentage.', 'A mismatch means find the 12 missing claims before cut-over.'],
         code='''old_n, new_n = 120450, 120438
old_rs, new_rs = 84.30, 84.29
print("counts match:", old_n == new_n, "| missing:", old_n - new_n)
print(f"money diff: {abs(old_rs - new_rs) / old_rs * 100:.3f}%")
''', notes={3: 'Counts :: Exact match is required; 12 claims are missing.'},
         tryit='Typical causes: duplicate handling, time zones (UTC vs IST) at midnight, or NULLs treated differently.'),
    dict(level='a', tag='Lakehouse · storage', title='What does keeping snapshots cost?',
         problem='<p>A retail table is 8 TB and copy-on-write updates rewrite about 5% of its files every day. Snapshots are kept for 30 days for time travel. How much extra storage do the old files use, and what if retention drops to 7 days? (Replication or EC overhead not included.)</p>',
         inp='8 TB · 5% rewritten/day · 30 vs 7 days',
         approach=['Old files per day = 5% of 8 TB.', 'Kept for the retention period.', 'Compare.'],
         code='''table_tb, daily = 8, 0.05
for days in (30, 7):
    extra = table_tb * daily * days
    print(f"{days:>2} days: {extra:.1f} TB of old files ({extra / table_tb:.0%} of the table)")
''', notes={3: 'Retention :: Old files are deleted only when their snapshots expire.'},
         tryit='Our lab table rewrote all files twice, so before expiry it held three copies: snapshot retention is a real cost.'),
]

QUIZ = mix([
    dict(q='What did our DELETE and UPDATE do to the data files in Iceberg (copy-on-write)?', options=['Edited the Parquet files in place', 'Wrote new files and a new snapshot; the old files stayed', 'Deleted the table and reloaded it', 'Only changed the Hive metastore'], answer=1,
         why='Snapshots 2 and 3 were "overwrite" commits: 459,636 rows added each time.'),
    dict(q='Time travel to the first snapshot returned…', options=['459,636 orders', '500,000 orders and revenue 12,852,002', 'An error, because the files were changed', 'Only the coffee orders'], answer=1,
         why='The first snapshot\'s files are still in HDFS until expired.'),
    dict(q='Why must pipeline steps be idempotent?', options=['To run faster', 'So retries and backfills give the same result instead of duplicates', 'Because Airflow requires Python', 'To save memory'], answer=1,
         why='Overwrite a partition instead of appending blindly.'),
    dict(q='Which tool replaced Oozie in most new Hadoop/lakehouse projects?', options=['Sqoop', 'Apache Airflow', 'ZooKeeper', 'Flume'], answer=1,
         why='Oozie moved to the Apache Attic in February 2025.'),
    dict(q='What does "hidden partitioning" (PARTITIONED BY days(ts)) give you?', options=['No partitions at all', 'Iceberg derives the day from ts, so queries filter on ts and still prune partitions', 'Partitions invisible in HDFS', 'Encrypted partitions'], answer=1,
         why='Our table got one folder per day without a separate date column.'),
    dict(q='Adding a column to an Iceberg table…', options=['Rewrites all data files', 'Changes only metadata; old rows read NULL', 'Is impossible after data is loaded', 'Requires a new table'], answer=1,
         why='payment appeared instantly with NULL for existing rows.'),
    dict(q='In a migration, what must happen before cut-over?', options=['Delete the old cluster', 'Dual-run and reconcile counts and totals', 'Disable all quality checks', 'Rename every table'], answer=1,
         why='Proof that old and new give the same answers.'),
    dict(q='Our first Iceberg run failed with "Self-suppression not permitted". The real cause was…', options=['A bug in Iceberg', 'A nearly full disk: DataNodes could not accept new blocks', 'Wrong SQL syntax', 'Kerberos'], answer=1,
         why='The next attempt showed "could only be written to 0 of the 1 minReplication nodes".'),
])

REVISION = [
    'A data engineer moves data reliably every day, proves it is correct, migrates platforms and controls cost.',
    'Pipelines: bronze (raw) → silver (clean) → gold (business); Airflow DAGs with retries, SLAs, backfills; Oozie retired Feb 2025.',
    '<b>Idempotent</b> steps overwrite their own partition, so retries and backfills never double count.',
    'Migration: inventory → copy (DistCp, snapshot diff) → dual-run → reconcile → cut-over → decommission.',
    '<b>Lakehouse</b> = open files on cheap storage + table format (Iceberg/Delta/Hudi): ACID, row-level changes, snapshots, time travel, schema evolution.',
    'Lab: 500,000 → 459,636 orders, ₹12,852,002 → ₹12,493,729; three snapshots; time travel restored the first; 90 data files after copy-on-write.',
    'Expire old snapshots and compact small files, or storage grows with every change.',
]
FAQ = [
    ('What does a data engineer do every day?', 'Checks overnight pipelines and fixes failures, builds and changes pipelines (ingest, clean, aggregate), handles schema changes from source teams, runs backfills, adds data quality checks, supports analysts with "why is this number different" questions, works on platform migrations and reviews storage and compute costs.'),
    ('What is a lakehouse?', 'A data architecture that keeps data in open file formats such as Parquet on low-cost storage (HDFS or object storage) and adds database features through an open table format (Apache Iceberg, Delta Lake or Apache Hudi): ACID transactions, updates and deletes, snapshots and time travel, schema evolution, read by several engines through a shared catalog.'),
    ('Iceberg vs Delta Lake vs Hudi: which should I learn?', 'All three solve the same problem. Iceberg is engine-neutral and widely supported by Spark, Trino, Flink, Hive and the cloud platforms; Delta is closest to Spark and Databricks; Hudi is strong for streaming upserts. Learn the shared ideas (snapshots, copy-on-write vs merge-on-read, compaction, schema evolution) and one format in depth; switching later is easy.'),
    ('How do you migrate a Hadoop cluster to the cloud or a lakehouse?', 'Take an inventory of data, tables, jobs and users; copy data with DistCp and snapshot-diff syncs; convert or rewrite tables (Hive to Iceberg in place or by rewrite); rewrite jobs (MapReduce, Pig, Hive) in Spark SQL or similar; dual-run old and new and reconcile counts and totals; cut consumers over; keep the old system read-only for a while; then decommission.'),
    ('What is an idempotent pipeline?', 'A pipeline in which running a step again for the same input gives the same result, for example by overwriting the output partition for that date instead of appending to it. It makes retries and backfills safe and is one of the most important habits in data engineering.'),
]

PRACTICE_INTRO = 'Data-engineering exercises using our lakehouse run and everyday scenarios.'
PROBLEMS = [
    dict(level='easy', title='Check the revenue arithmetic', stmt='Recompute the revenue after DELETE coffee and UPDATE chai from the loaded revenue.', inp='12,852,002 · 40,364 coffee at ₹20 · 149,669 chai +₹3',
         code='''print(12852002 - 40364 * 20 + 149669 * 3)
''', explain='12,493,729, exactly the lab result.'),
    dict(level='easy', title='Rows written by copy-on-write', stmt='How many rows did Iceberg write in total across the three commits?', inp='500,000 + 459,636 + 459,636',
         code='''print(500000 + 459636 + 459636)
''', explain='1,419,272 rows written to keep a 459,636-row table with full history: the price of copy-on-write.'),
    dict(level='easy', title='Days in the table', stmt='The data folder had 31 directories. How many day partitions is that?', inp='31 dirs incl. data/ itself',
         code='''print(31 - 1, "days (September 2026)")
''', explain='30 day folders plus the data/ folder itself.'),
    dict(level='medium', title='A simple quality gate', stmt='Fail the load if more than 1% of rows have a missing amount or a negative one.', inp='a list of amounts',
         code='''amounts = [15, 20, None, 45, -18, 30, 25, 18, 20, 80]
bad = sum(1 for a in amounts if a is None or a < 0)
share = bad / len(amounts)
print(f"{bad} bad rows ({share:.0%})", "FAIL" if share > 0.01 else "OK")
''', explain='20% bad rows: the gate fails the task and gold is not updated.'),
    dict(level='medium', title='Schema change detector', stmt='Compare yesterday\'s and today\'s column lists from a partner and report what changed.', inp='two schemas',
         code='''old = ["txn_id", "payer", "payee", "amount", "ts"]
new = ["txn_id", "payer", "payee", "amount", "ts", "bank_ref"]
print("added:", [c for c in new if c not in old], "removed:", [c for c in old if c not in new])
''', explain='A new column: add it to silver (metadata-only in Iceberg) and update the data contract.'),
    dict(level='medium', title='Small files after streaming', stmt='A stream commits every minute into 12 partitions. How many files a day, and how many after an hourly compaction into one file per partition?', inp='1 commit/min · 12 files/commit',
         code='''per_day = 60 * 24 * 12
print(per_day, "files/day ->", 24 * 12, "after hourly compaction")
''', explain='17,280 tiny files a day become 288 (Lesson 7.5).'),
    dict(level='business', title='Snapshot retention vs cost', stmt='Old snapshot files use 12 TB at 30-day retention. Storage costs ₹1,800 per TB per month. What does cutting retention to 7 days save per year?', inp='12 TB · ₹1,800/TB/month',
         code='''saved_tb = 12 * (1 - 7 / 30)
print(f"Rs {saved_tb * 1800 * 12:,.0f} per year")
''', explain='About ₹1.98 lakh a year (illustrative price), at the cost of a shorter time-travel window for audits.'),
    dict(level='advanced', title='Merge-on-read vs copy-on-write', stmt='A 1,000-file table gets 50 small updates a day, each touching 20 files. Copy-on-write rewrites the touched files; merge-on-read writes one small delete file per update and compacts nightly. Compare files written per day.', inp='50 updates × 20 files',
         code='''cow = 50 * 20
mor = 50 + 20                 # 50 small delete files + nightly compaction rewriting about 20 files
print("copy-on-write:", cow, "files/day | merge-on-read:", mor, "files/day")
''', explain='1,000 vs 70 files written: merge-on-read suits frequent small updates; readers pay a little to merge the delete files until compaction.'),
]

SCN_INTRO = 'Data-engineering interviews mix pipeline design, debugging stories and lakehouse questions.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Pipelines · reliability</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>"Your nightly job failed. Walk me through your first hour."</h4>
      <p class="scn__situation">The settlement file is due at 11:00.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> calm, systematic debugging and communication.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Tell stakeholders it is late and when the next update comes; check which task failed and its logs (Lessons 11.5, 12.6).</li>
          <li>Find the cause (here: an upstream schema change), fix the smallest thing, re-run only the failed partition: safe because the step is idempotent.</li>
          <li>Afterwards: a data contract or schema check so it fails loudly and early next time.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Lakehouse · design</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>"Finance wants corrected numbers but also last month's report exactly as published."</h4>
      <p class="scn__situation">Corrections arrive weeks after month-end.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> snapshots, tags and retention.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Use a table format: apply corrections with UPDATE/MERGE; tag the snapshot used for each published report.</li>
          <li>Reports query the tag (time travel); dashboards query the current snapshot.</li>
          <li>Set snapshot retention to keep tagged snapshots and expire the rest to control storage.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Migration · planning</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>"Plan the move of a 2 PB Hadoop cluster to a lakehouse"</h4>
      <p class="scn__situation">Hundreds of Hive tables, MapReduce and Pig jobs, an Oozie scheduler.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> phasing and risk control.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Inventory and prioritise (usage, owners, dependencies); retire unused tables first.</li>
          <li>Copy with DistCp and snapshot diffs; migrate Hive tables to Iceberg in place or rewrite badly partitioned ones; move Oozie flows to Airflow and jobs to Spark SQL.</li>
          <li>Dual-run per domain with reconciliation reports, cut over consumer by consumer, keep the old cluster read-only, then decommission.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Concepts · formats</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>"Why not just use Parquet files in folders?"</h4>
      <p class="scn__situation">A follow-up after you mention Iceberg.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> what the table format adds.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Plain folders have no transactions: readers can see half-written data, and there is no safe UPDATE or DELETE.</li>
          <li>A table format adds atomic commits, snapshots and time travel, schema and partition evolution, and file-level statistics for pruning.</li>
          <li>The data is still Parquet, so any engine with a connector can read it.</li>
        </ul>
      </div></details>
    </article>
'''
