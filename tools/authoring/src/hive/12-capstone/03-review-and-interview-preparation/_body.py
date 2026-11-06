import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
LAB = os.path.join(HERE, '..', '..', 'lab') + os.sep
CAP = LAB + 'captures' + os.sep
def capf(n):
    return re.sub(r'; Query ID[^\n]*', '', open(CAP + n).read().rstrip())
TESTS = open(LAB + 'capstone/tests.hql').read().strip()

def opbox(x, y, label, sub='', tone='card', w=128, h=26):
    o = box(x, y, w, h, tone) + t(x + w / 2, y + (11 if sub else 16), label, 7.2, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 21, sub, 6.4, 'ink2', mono=True)
    return o

# ---------------------------------------------------------------- story
sc = (box(14, 12, 196, 128, 'card') + t(112, 30, 'Code review', 9, bold=True) +
      ''.join(t(26, 50 + k * 15, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
          ('✓ 7 data tests PASS', 'green'), ('! 31 files of 18 KB', 'amber'), ('! 9 delta dirs in one day', 'amber'), ('✓ re-run safe', 'green'), ('+ materialized view', 'blue')])) +
      arrow(212, 76, 246, 76, 'acc', 1.8) +
      box(250, 12, 160, 128, 'blue') + t(330, 30, 'Mock interview', 9, bold=True) +
      ''.join(t(262, 50 + k * 15, s, 7.2, 'ink2', anchor='start') for k, s in enumerate(['architecture', 'tables & partitions', 'joins & tuning', 'ACID & SCD', 'your project'])) +
      arrow(412, 76, 446, 76, 'acc', 1.8) +
      box(450, 12, 182, 128, 'green') + t(541, 30, 'Ready', 9, bold=True) +
      ''.join(t(462, 50 + k * 15, s, 7.2, 'ink', anchor='start') for k, s in enumerate(['60-second project pitch', '50 questions, short answers', 'numbers you can quote', 'resume lines'])))
scene_svg = scene('The last capstone lesson: a code review of the warehouse finds small files and ACID delta folders and adds tests and a materialized view; a mock interview covers architecture, tables, joins, tuning, ACID and the project; Kabir leaves ready with a pitch, answers and resume lines.', sc,
                  'Build it, <tspan font-weight="700" class="s-acc">review it</tspan>, then explain it in an interview.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Now defend it”</h2>
  <div class="story">
    <p class="narration">The warehouse works and the CEO has his numbers. Two things remain before Kabir can call the capstone finished: a code review by Arjun Sir, and a mock interview with Riya playing the interviewer, because Kabir has his first data engineering interview in two weeks.</p>

{scene_svg}

A> A pipeline that works today is not finished. In a review we ask: what will hurt in six months? Small files, growing delta folders, missing tests, slow dashboards.
K> And the interview, Sir? Everyone says Hive questions are just definitions.
R> Not when I ask them. I will ask “managed versus external”, and then “what did <i>you</i> choose in your project, and why?”
A> That is how good interviewers work. Today you will review the warehouse with real measurements, fix what the review finds, and then practise answering with numbers from your own project. Every output is real.
  </div>
</section>
'''

lv = '''
LEVELS> Review and interview preparation at three levels
L1> Check your work, then explain it
      <ul>
        <li>A review looks for problems that are not visible yet: too many tiny files, missing tests, slow queries.</li>
        <li>In an interview, a definition earns a point; a definition plus “in my project I saw…” earns the job.</li>
      </ul>
L2> What this lesson covers
      <ul>
        <li>Measuring files and ACID delta folders, running and checking a major compaction.</li>
        <li>Turning the reconciliation checks into an automated test file with PASS/FAIL results.</li>
        <li>A materialized view that Hive uses automatically, and what happens when it becomes stale.</li>
        <li>A 50-question bank grouped by topic, a project pitch and resume lines.</li>
      </ul>
L3> What senior interviewers listen for
      <ul>
        <li>Trade-offs with numbers: “31 files of 18 KB; at this size I would partition by month or move to Iceberg”.</li>
        <li>Failure stories: the SCD 2 replay bug, the Tez counter limit, the <code>DATE_FORMAT</code> surprise.</li>
        <li>Knowing what changed in Hive 4: Hive on Spark removed, MapReduce deprecated, Iceberg built in.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Production readiness review and interview preparation</h2>
''' + def_block(
    'A <b>production readiness review</b> of a data pipeline checks, with measurements, that it is correct (tests and reconciliation), reliable (idempotent, observable, recoverable), efficient (file sizes, compaction, statistics, pruning) and maintainable (documented design, naming, ownership) before it is relied upon. <b>Interview preparation</b> for a data engineering role turns that knowledge into concise, evidence-based answers: definitions, trade-offs and examples from one’s own project.',
    'Measure the warehouse, fix what will hurt later, add automatic tests. Then practise explaining Hive using your own project’s numbers.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Small files problem', 'Many files far smaller than a block: more metadata, more tasks, slower queries.'),
    ('Major compaction', 'Rewrites base + deltas of an ACID partition into one new base.'),
    ('Cleaner', 'Deletes obsolete delta and base folders after compaction.'),
    ('Data test', 'A query that returns PASS or FAIL for one expectation.'),
    ('Materialized view', 'A stored query result Hive can use to answer other queries.'),
    ('Query rewriting', 'The optimiser replaces a query on base tables with one on a materialized view.'),
    ('STAR answer', 'Situation, Task, Action, Result: a structure for project stories.'),
    ('Stale', 'A materialized view whose source tables have changed since it was built.'),
]) + '''

  <h3>The review checklist and our results</h3>
''' + table(['Area', 'Question', 'Result in our warehouse', 'Action'], [
    ['Correctness', 'Do layers reconcile?', 'Raw valid = fact = 47,553; gold = fact = ₹1,53,95,190', 'Automate as tests (Step 4)'],
    ['Reliability', 'Safe to re-run?', 'Yes, after the SCD 2 fix (Lesson 12.2)', 'Keep the re-run test'],
    ['Files', 'Healthy file sizes?', '31 fact files averaging 18 KB', 'Monthly partitions or Iceberg at this size'],
    ['ACID', 'Deltas under control?', 'Up to 9 delta folders in one partition', 'Compaction (Steps 2–3)'],
    ['Statistics', 'Does the optimiser know the data?', 'Column stats computed', 'ANALYZE after big loads'],
    ['Serving', 'Are dashboards fast?', 'Every KPI query scans the fact', 'Gold table + materialized view (Steps 5–6)'],
    ['Observability', 'Do we know what each load did?', '<code>etl_audit</code> per load and step', 'Alert on FAIL and on volume anomalies'],
], minw=820) + lv + '''
EXAM> In Hive 4, <b>Hive on Spark was removed</b> and <b>Hive on MapReduce is deprecated</b>; Tez is the default engine. Indexes were removed in Hive 3.0. Interview answers that still describe Hive on Spark as an option are out of date.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Interview rounds and what each tests</h2>
''' + table(['Round', 'Typical format', 'What to prepare from this course'], [
    ['Online test', '20–40 MCQs on SQL, Hadoop, Hive', 'Every lesson’s quiz; the 50-question bank below'],
    ['SQL coding', 'Write queries on a whiteboard or editor', 'GROUP BY, joins, window functions (Module 3), de-duplication with ROW_NUMBER'],
    ['Hive / big data concepts', 'Explain, compare, “what happens when…”', 'Architecture, tables, partitions, formats, ACID, tuning'],
    ['Project deep dive', '“Walk me through your project”', 'The capstone pitch and its numbers'],
    ['Design', '“Design a pipeline for…”', 'Layers, grain, SCD, idempotence, late data (Lessons 12.1–12.2)'],
    ['Troubleshooting', '“This query is slow / this job failed”', 'EXPLAIN, small files, skew, OOM (Module 8, Lesson 10.3)'],
    ['Behavioural', 'Teamwork, deadlines, explaining to non-technical people', 'STAR stories from the capstone'],
], minw=760) + table(['Question style', 'Example', 'How to answer'], [
    ['Definition', '“What is the metastore?”', 'One sentence + why it matters'],
    ['Comparison', '“ORDER BY vs SORT BY?”', 'A small table in words: what, how many reducers, when'],
    ['Scenario', '“Dashboard doubled after a re-run”', 'Cause → check → fix → prevention'],
    ['Trick', '“Can Hive do OLTP?”', 'No, then explain why, then what Hive ACID does offer'],
    ['Project', '“Why did you partition by order_date?”', 'Requirement → measurement → decision → trade-off'],
], minw=680) + '''
TIP> Write down five numbers from your capstone and use them: 48,871 raw rows, 546 duplicates, 112 rejects, 47,553 orders, 31 loads in 901 seconds. Numbers make answers believable.
</section>
'''

FAQBANK = [
    ('Architecture and basics', [
        ('What is Apache Hive and when would you use it?', 'A data warehouse system on Hadoop-compatible storage that lets you query and manage large datasets with SQL (HiveQL). Use it for batch ETL and analytics over large files; not for low-latency single-row lookups or OLTP. <a href="../../01-introduction/02-what-is-hive/">1.2</a>'),
        ('Can Hive be used for OLTP?', 'No. Queries start distributed jobs with seconds of latency, and although Hive ACID supports INSERT, UPDATE, DELETE and MERGE, it is designed for batches of changes, not thousands of small transactions per second. <a href="../../07-acid-and-iceberg/01-acid-tables-update-delete/">7.1</a>'),
        ('What does schema on read mean?', 'The table’s schema is applied when data is read, not checked when files are written. A file with a bad value loads fine and the value becomes NULL at query time, which is why our raw tables were all STRING. <a href="../../02-hiveql/04-row-formats-and-serdes/">2.4</a>'),
        ('What are the main components of Hive?', 'Clients (Beeline, JDBC/ODBC), HiveServer2, the Driver with compiler, optimiser and executor, the Metastore (service + relational database), and the execution engine (Tez by default) running on YARN over HDFS or object storage. <a href="../../01-introduction/03-hive-architecture-and-metastore/">1.3</a>'),
        ('Describe how a query is executed.', 'Client sends the query; the driver asks the compiler for a plan; the compiler gets table metadata from the metastore; the optimiser (CBO) improves the plan; the executor submits a Tez DAG to YARN; results are fetched back through HiveServer2. <a href="../../01-introduction/04-how-a-hive-query-becomes-a-job/">1.4</a>'),
        ('What is the metastore, and why is it not stored in HDFS?', 'It stores databases, tables, columns, partitions, locations and statistics. It needs fast random reads and updates and transactions, which a relational database (Derby, MySQL, PostgreSQL, Oracle) provides and HDFS files do not. <a href="../../10-administration-and-security/01-metastore-administration/">10.1</a>'),
        ('Embedded, local and remote metastore?', 'Embedded: Derby in the same JVM, one user, for testing. Local: the metastore code runs inside HiveServer2 but uses an external database. Remote: a separate metastore service on Thrift (port 9083) shared by Hive, Spark, Trino and others, the production choice.'),
        ('What is HCatalog?', 'A table and storage management layer on top of the metastore that lets Pig, MapReduce and other tools read and write Hive tables without knowing file formats; WebHCat is its REST interface.'),
    ]),
    ('Tables, formats and loading', [
        ('Managed versus external tables?', 'Hive owns managed table data: DROP deletes the files. External tables only point to a location: DROP removes metadata only. In Hive 4, non-ACID “managed” tables are translated to external tables with external.table.purge=true, as we saw in Lesson 12.2. <a href="../../02-hiveql/02-managed-vs-external-tables/">2.2</a>'),
        ('Can you change where a managed table is stored?', 'Yes: with LOCATION in CREATE TABLE, with ALTER TABLE … SET LOCATION, or globally with hive.metastore.warehouse.dir.'),
        ('What is a SerDe? What is an ObjectInspector?', 'A SerDe (serializer/deserializer) converts between file bytes and Hive rows (LazySimpleSerDe, JsonSerDe, OrcSerde, RegexSerDe). An ObjectInspector describes the structure of a row object so Hive can read its fields without knowing its Java class.'),
        ('Which classes read and write a text table?', '<code>org.apache.hadoop.mapred.<wbr>TextInputFormat</code> reads records; <code>org.apache.hadoop.hive.ql.io.<wbr>HiveIgnoreKeyTextOutputFormat</code> writes them; the SerDe (<code>LazySimpleSerDe</code>) splits and joins fields.'),
        ('ORC versus Parquet?', 'Both columnar, compressed, with min/max statistics for skipping. ORC is Hive’s native format and required for Hive ACID tables; Parquet is the most widely shared format across Spark, Trino and cloud warehouses. <a href="../../06-file-formats/02-orc-deep-dive/">6.2</a>'),
        ('What are Hive’s complex types?', 'ARRAY, MAP, STRUCT and UNIONTYPE; query them with index, key or dot syntax and flatten them with explode and LATERAL VIEW. <a href="../../04-complex-data/02-explode-and-lateral-view/">4.2</a>'),
        ('What does LOAD DATA do?', 'It moves (INPATH) or copies (LOCAL INPATH) files into the table’s folder without parsing them; Hive does not validate the content. <a href="../../02-hiveql/05-loading-data/">2.5</a>'),
        ('What is a .hiverc file?', 'A script of settings (SET …, ADD JAR …) that the old Hive CLI ran at start-up from the user’s home folder. With Beeline, pass an initialisation file with -i init.hql instead.'),
        ('How do you skip a CSV header?', 'TBLPROPERTIES (\'skip.header.line.count\'=\'1\'), as on our raw tables.'),
    ]),
    ('Querying', [
        ('ORDER BY, SORT BY, DISTRIBUTE BY, CLUSTER BY?', 'ORDER BY: total order, one reducer. SORT BY: sorted within each reducer. DISTRIBUTE BY: chooses which reducer gets each row. CLUSTER BY x = DISTRIBUTE BY x SORT BY x. <a href="../../03-querying/04-order-sort-distribute-cluster-by/">3.4</a>'),
        ('Which joins does Hive support?', 'INNER, LEFT, RIGHT, FULL OUTER, CROSS and LEFT SEMI JOIN (rows of the left table with a match, like EXISTS), plus anti joins in newer versions. <a href="../../03-querying/03-joins/">3.3</a>'),
        ('What is a map join?', 'The small table is loaded into memory on every task and joined without a shuffle; Hive converts joins automatically when the small side is below hive.auto.convert.join.noconditionaltask.size. <a href="../../08-optimisation/03-join-optimisations/">8.3</a>'),
        ('How does Hive handle skewed joins?', 'With hive.optimize.skewjoin, keys above a row threshold are processed in a separate map join; you can also salt hot keys or declare skewed values on the table.'),
        ('How do you remove duplicates but keep the newest row?', 'ROW_NUMBER() OVER (PARTITION BY key ORDER BY updated_at DESC) and keep rn = 1, as in our MERGE source. DISTINCT keeps both versions of a changed row. <a href="../../03-querying/06-window-functions/">3.6</a>'),
        ('How does Hive treat NULLs?', 'Comparisons with NULL are NULL (not true), so use IS NULL, COALESCE or NVL; a failed CAST returns NULL; in text files \\N means NULL by default.'),
        ('How do you list databases starting with c, or check a partition exists?', 'SHOW DATABASES LIKE \'c*\'; and SHOW PARTITIONS t PARTITION (dt=\'2026-10-05\');'),
        ('How do you pass variables to a script?', 'beeline --hivevar load_date=2026-10-05 -f daily_load.hql and ${hivevar:load_date} in the script; --hiveconf sets configuration values. Hive CLI and Beeline also run single statements with -e.'),
    ]),
    ('Partitioning and bucketing', [
        ('What is partitioning and why use it?', 'Splitting a table into folders by column values (dt=…). Queries that filter on the partition column read only matching folders (pruning), as EXPLAIN DEPENDENCY showed: 2 of 31 partitions. <a href="../../05-partitioning-and-bucketing/01-partitioning/">5.1</a>'),
        ('Static versus dynamic partitions?', 'Static: you name the partition value in the INSERT. Dynamic: Hive takes it from the last SELECT column; needs hive.exec.dynamic.partition.mode=nonstrict when no static part is given. <a href="../../05-partitioning-and-bucketing/02-dynamic-partitions-and-msck/">5.2</a>'),
        ('How are rows assigned to buckets?', 'hash(bucketing column) mod number of buckets. Bucketing helps sampling, bucket map joins and sort-merge-bucket joins. <a href="../../05-partitioning-and-bucketing/03-bucketing/">5.3</a>'),
        ('What is the small files problem and how do you fix it?', 'Many tiny files mean more metastore and NameNode load and more tasks. Fix: coarser partitions, hive.merge.* settings, CONCATENATE for ORC, compaction for ACID, or a table format such as Iceberg with compaction. <a href="../../05-partitioning-and-bucketing/04-partition-design-small-files-and-skew/">5.4</a>'),
        ('When do you need MSCK REPAIR TABLE?', 'When partition folders were created outside Hive; it adds missing partitions to the metastore (SYNC PARTITIONS also drops missing ones). Our raw tables used it once, then ALTER TABLE ADD IF NOT EXISTS PARTITION each night.'),
    ]),
    ('Performance and optimisation', [
        ('How do you find out why a query is slow?', 'EXPLAIN (or EXPLAIN ANALYZE / FORMATTED / CBO), the Tez UI or HiveServer2 web UI, and the logs: look for missing partition filters, a shuffle of a big table, skew in one task, small files or missing statistics. <a href="../../08-optimisation/05-troubleshooting-slow-queries/">8.5</a>'),
        ('What does the cost-based optimiser need?', 'Table and column statistics (ANALYZE TABLE … COMPUTE STATISTICS FOR COLUMNS) to choose join order and join type. <a href="../../08-optimisation/02-cbo-and-statistics/">8.2</a>'),
        ('What is vectorisation?', 'Processing a batch of rows (default 1,024) per operator call using column vectors, which cuts per-row overhead; works best with ORC. <a href="../../08-optimisation/04-vectorisation-tez-and-llap/">8.4</a>'),
        ('MapReduce, Tez, Spark as engines?', 'Tez is the default and builds one DAG per query. MapReduce is deprecated in Hive 4. Hive on Spark was removed in Hive 4.0; Spark now reads Hive tables through the metastore instead (Lesson 11.1).'),
        ('Common causes of OutOfMemory errors?', 'A map join whose “small” table is not small, huge GROUP BY key sets, skewed keys, too-small container memory, or wide rows with large collections. Fix the cause before raising memory.'),
        ('What is a materialized view in Hive?', 'A stored query result that the optimiser can use automatically when it is up to date; requires transactional source tables for automatic rewriting. Step 5–6 below show it.'),
        ('What happened to Hive indexes?', 'Removed in Hive 3.0. Use columnar formats with statistics and bloom filters, partitioning, and materialized views instead. <a href="../../09-extending-hive/02-views-and-materialized-views/">9.2</a>'),
    ]),
    ('ACID, SCD and modern Hive', [
        ('What does Hive ACID need, and what are its trade-offs?', 'ORC, transactional=true, managed table, and the DbTxnManager. Gains: UPDATE, DELETE, MERGE, consistent reads. Costs: delta folders, compaction, Hive-specific files other engines may misread. <a href="../../07-acid-and-iceberg/01-acid-tables-update-delete/">7.1</a>'),
        ('Minor versus major compaction?', 'Minor merges delta files into one delta; major rewrites base + deltas into a new base. The cleaner then removes old folders. <a href="../../07-acid-and-iceberg/03-compaction-and-iceberg/">7.3</a>'),
        ('How do you implement SCD type 2 in Hive?', 'MERGE with a source that contains every changed row twice: once with the key (to close the current version) and once with a NULL key (to insert the new one), plus a guard so only newer changes apply. <a href="../02-build-the-warehouse/">12.2</a>'),
        ('What is Apache Iceberg and why does it matter for Hive users?', 'An open table format with snapshots, hidden partitioning, partition evolution and engine-neutral row-level changes. Hive 4 creates and migrates Iceberg tables natively. <a href="../../11-hive-in-industry/03-lakehouse-and-migration/">11.3</a>'),
        ('How is Hive used in the cloud?', 'Managed clusters such as Amazon EMR, Google Dataproc and Azure HDInsight run Hive on object storage; AWS Glue Data Catalog or a managed metastore replace the self-run metastore. <a href="../../11-hive-in-industry/02-hive-in-the-cloud/">11.2</a>'),
        ('How is Hive secured?', 'Authentication (Kerberos, LDAP, SAML/JWT in Hive 4), authorization (SQL-standard based or Apache Ranger policies), and encryption in transit and at rest. <a href="../../10-administration-and-security/02-authorization-and-security/">10.2</a>'),
        ('How do you monitor Hive?', 'HiveServer2 web UI (port 10002), Tez UI, metrics (JMX), operation logs, the metastore’s compaction and lock tables, and data tests like ours. <a href="../../10-administration-and-security/03-monitoring-and-logs/">10.3</a>'),
    ]),
    ('Comparisons and judgement', [
        ('Hive versus HBase?', 'Hive: SQL analytics over files, batch, high latency. HBase: a NoSQL key-value store for random reads and writes in milliseconds. They are often used together.'),
        ('Hive versus Pig?', 'Both turn scripts into jobs. Hive uses SQL and a metastore; Pig used a procedural data-flow language. Pig is rarely used for new work today.'),
        ('Hive versus Spark SQL and Trino?', 'Hive excels at large SQL ETL and owns ACID tables; Spark SQL fits programmatic pipelines and ML; Trino is fastest for interactive queries. Many platforms share one metastore between all three. <a href="../../11-hive-in-industry/01-hive-spark-and-trino/">11.1</a>'),
        ('When was Hive not the right tool?', 'For sub-second dashboards (use Trino or a serving store), per-event updates (use a streaming system or HBase) and very small data (a single database is simpler).'),
        ('How do you ensure data quality in Hive?', 'Raw tables that keep everything, typed staging with reject reasons, quarantine, reconciliation between layers, automated PASS/FAIL tests and an audit table, as in this capstone.'),
        ('Why is Hive still relevant in 2026?', 'Its metastore is the catalogue of many data lakes, large companies run huge Hive SQL estates, and Hive 4 adds Iceberg, so Hive skills transfer directly to lakehouse work.'),
    ]),
]
def bank():
    out = []
    n = 0
    for topic, qs in FAQBANK:
        out.append(f'  <h4>{topic}</h4>\n  <div class="faq">')
        for q, a in qs:
            n += 1
            out.append(f'    <details><summary>{n}. {q}</summary><p>{a}</p></details>')
        out.append('  </div>')
    return '\n'.join(out), n
BANK, NQ = bank()

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Reviewing the warehouse with measurements</h2>
  <p>All outputs are real (Hive 4.2.1, the warehouse built in Lesson 12.2).</p>
''' + stepper([
    ('Step 1 · Measure files per table',
     code('bash', 'inside the HiveServer2 container', 'cd /opt/hive/data/warehouse/tiffingo_dw.db\n# data files only (no .crc checksums, no _orc_acid_version markers)\nfor t in fact_orders fact_deliveries gold_city_daily rejected_orders dim_customer; do\n  find $t -type f ! -name ".*" ! -name "_*" -printf "%s\\n" | awk -v t=$t \'{n++; s+=$1} END {print t, n, s, int(s/n)}\'\ndone', capf('l123_sizes.txt')),
     'One file per daily partition, 18 KB on average for the fact and 1.3 KB for gold, against a 128 MB block. At TiffinGo’s volume this is harmless, but the pattern is the classic small-files problem: at 365 days × 4 tables it becomes 1,460 tiny files a year. The review action: monthly partitions for tables of this size, or Iceberg with compaction. Partition by day only when a day holds hundreds of MB.'),
    ('Step 2 · ACID delta folders after a month of MERGEs',
     code('bash', 'list partitions of fact_orders', 'ls order_date=2026-10-05 order_date=2026-10-30 order_date=2026-10-31\n# summary for the whole table\n…\nls order_date=2026-10-28', capf('l123_files_before.txt') + '\n\norder_date=2026-10-28:\n' + capf('l123_p28_before.txt')),
     'Each MERGE that touches a partition adds a <code>delta</code> folder (inserted rows) and, for updates, a <code>delete_delta</code> folder. Old partitions had already been rewritten into a <code>base_</code> folder by Hive’s <b>automatic</b> compaction (the lab’s metastore runs the initiator and cleaner). Recent partitions still had up to 9 delta folders: every reader must merge them on the fly.'),
    ('Step 3 · Major compaction and its result',
     code('sql', 'beeline · then list again', "ALTER TABLE fact_orders PARTITION (order_date='2026-10-28') COMPACT 'major' AND WAIT;\nALTER TABLE fact_orders PARTITION (order_date='2026-10-29') COMPACT 'major' AND WAIT;\nSHOW COMPACTIONS tiffingo_dw.fact_orders PARTITION (order_date='2026-10-28');   -- selected columns", capf('l123_showc_short.txt') + '\n\n$ ls order_date=2026-10-28\n' + capf('l123_files_after.txt')),
     '<code>AND WAIT</code> blocks until the compaction finishes (3.4 seconds here). Nine folders became one <code>base_</code>; across the table, delta folders dropped from 15 to 1 and files from 192 to 124 (each base also holds small marker and checksum files). In production, check that automatic compaction keeps up: a growing list of “initiated” or “failed” rows in <code>SHOW COMPACTIONS</code> is an alert.'),
    ('Step 4 · Turn the reconciliation into automated tests',
     code('sql', 'tests.hql', TESTS, capf('l123_tests.txt')),
     'Seven expectations, each one row with PASS or FAIL. A scheduler runs this file after every load and alerts on any FAIL. The first version used one big <code>UNION ALL</code> and hit the same Tez 120-counter limit as Lesson 12.2, so each test became a small INSERT into <code>dq_results</code>. Tools such as Great Expectations or dbt tests do the same thing with more features; the idea is identical.'),
    ('Step 5 · A materialized view the optimiser uses',
     code('sql', 'beeline', "CREATE MATERIALIZED VIEW mv_city_status AS\nSELECT r.city, f.status, COUNT(*) AS n, SUM(f.amount) AS amt\nFROM fact_orders f JOIN dim_restaurant r ON r.restaurant_id = f.restaurant_id\nGROUP BY r.city, f.status;\n\nCREATE MATERIALIZED VIEW mv_status_day AS\nSELECT order_date, status, COUNT(*) AS n, SUM(amount) AS amt\nFROM fact_orders GROUP BY order_date, status;\n\n-- a normal query on the fact table\nEXPLAIN CBO SELECT status, SUM(amount) AS amt FROM fact_orders\nWHERE order_date >= DATE '2026-10-15' GROUP BY status;", capf('l123_mv1.txt') + '\n\n(mv_status_day created)\n\n' + capf('l123_mv3.txt')),
     'The first view was refused: automatic rewriting needs <b>transactional</b> source tables so Hive can tell whether the view is up to date, and <code>dim_restaurant</code> is plain ORC. The second view uses only the ACID fact. The query was written against <code>fact_orders</code>, yet the plan scans <code>mv_status_day</code>: 92 pre-aggregated rows (date × status) instead of 47,553 orders. Users do not need to know the view exists.'),
    ('Step 6 · When the view becomes stale',
     code('sql', 'after the next nightly load', "$ run_load.sh 2026-10-31\nEXPLAIN CBO SELECT status, SUM(amount) AS amt FROM fact_orders\nWHERE order_date >= DATE '2026-10-15' GROUP BY status;\n\nALTER MATERIALIZED VIEW mv_status_day REBUILD;\nEXPLAIN CBO …same query…;\nSELECT status, SUM(amount) AS amt FROM fact_orders WHERE order_date >= DATE '2026-10-15'\nGROUP BY status ORDER BY status;", capf('l123_mv4.txt') + '\n\n-- after REBUILD\n' + capf('l123_mv5.txt') + '\n\n' + capf('l123_mv6.txt')),
     'After the load wrote to <code>fact_orders</code>, the view was stale and Hive correctly went back to scanning the fact: a materialized view never returns outdated results unless you allow it with a rewriting time window. After <code>REBUILD</code> the plan used the view again. So the nightly script needs one more step: rebuild the views after the MERGE.'),
    ('Step 7 · What we would change at 100× scale',
     table(['Finding', 'At TiffinGo today', 'At 100× (≈150,000 orders a day)'], [
         ['Partition grain', 'Daily, 18 KB files', 'Daily is fine (~2 MB/day); still small: consider monthly + sort by date'],
         ['MERGE target scan', 'Whole fact (1 month)', 'Add <code>t.order_date &gt;= cutoff</code>; handle older corrections separately'],
         ['Compaction', 'Automatic + manual check', 'Dedicated compaction pool, alerts on backlog'],
         ['Serving', 'Gold table + MV', 'Gold as Iceberg for Trino dashboards; MV rebuild in the DAG'],
         ['Scheduling', 'Shell loop', 'Airflow DAG: load → tests → MV rebuild → publish'],
         ['Table format', 'Hive ACID', 'Iceberg (Lesson 11.3) so Spark and Trino read the same answer'],
     ], minw=720),
     'A good review ends with a short list of concrete changes and when they become necessary. Interviewers ask exactly this: “what would you change if the data grew 100 times?”'),
]) + f'''
  <h3 id="bank">Interview question bank: {NQ} questions with short answers</h3>
  <p>Grouped by topic, written from the questions most often listed on popular interview-preparation sites and from real interview rounds, and linked to the lesson that explains each one in depth. Answer aloud first, then open the answer.</p>
{BANK}

  <h3 id="pitch">Your project in 60 seconds</h3>
''' + table(['STAR', 'What to say (adapt with your own numbers)'], [
    ['Situation', 'A food-delivery company’s city revenue report was wrong because it summed raw files containing duplicates, re-sends, refunds and broken rows.'],
    ['Task', 'Build a Hive warehouse that loads nightly, keeps customer history and gives finance-reconcilable KPIs per city and plan.'],
    ['Action', 'Profiled 48,871 raw rows in Hive; designed raw/silver/gold with a partitioned ACID fact (MERGE on order_id), an SCD 2 customer dimension and a quarantine; wrote one idempotent HiveQL script with --hivevar and backfilled 31 days; added data tests, compaction and a materialized view.'],
    ['Result', '47,553 orders reconciled exactly with raw and gold; 112 bad rows quarantined with reasons; Mumbai’s revenue corrected from ₹42.8 lakh to ₹38.4 lakh; re-runs proven safe after fixing an SCD 2 replay bug.'],
], minw=640) + '''
  <h3 id="resume">Resume lines</h3>
  <ul>
    <li>Built an idempotent nightly Hive 4 pipeline (raw → silver → gold) for 49K order events/month with MERGE upserts on a partitioned ACID fact table and an SCD type 2 customer dimension.</li>
    <li>Designed data-quality controls (typed staging, quarantine with reject reasons, audit table, 7 automated PASS/FAIL tests) that reconciled raw, silver and gold to the rupee.</li>
    <li>Found and fixed a history-corrupting SCD 2 replay bug through re-run testing; added compaction checks and a materialized view used automatically by the optimiser.</li>
  </ul>
  <p class="muted">Use your own numbers. Never claim a project you did not build; interviewers will ask about details.</p>
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('fact_orders      31  565614  18245', W), ('gold_city_daily  31   40002   1290', W), ('128 MB block = 134217728', Y), ('→ small files', Y)], size=7.2),
    term([('order_date=2026-10-28:', W), ('  delete_delta_… × 3', Y), ('  delta_… × 6', Y), ('delta dirs (table): 15', Y)], size=7.4),
    term([('COMPACT \'major\' AND WAIT', W), ('MAJOR succeeded 3402 ms', G), ('order_date=2026-10-28: base_…', G), ('delta dirs (table): 1', G)], size=7.2),
    term([('fact key unique          PASS', G), ('gold net = fact net      PASS', G), ('one current row/customer PASS', G), ('… 7 of 7 PASS', G)], size=7.2),
    term([('EXPLAIN CBO … FROM fact_orders', W), ('HiveTableScan mv_status_day', G), ('after a load: scans fact_orders', Y), ('after REBUILD: mv again', G)], size=7.0),
    term([('“Walk me through your project.”', W), ('48,871 rows → 47,553 orders', G), ('112 rejects · 31 loads · 901 s', G), ('SCD 2 replay bug → fixed', G)], size=7.0),
]
def board(hi):
    items = [('files', 'size per file', 14, 40), ('deltas', 'ACID folders', 130, 40), ('compaction', 'base_', 246, 40),
             ('tests', 'PASS / FAIL', 14, 112), ('MV', 'rewrite', 130, 112), ('interview', 'your numbers', 246, 112)]
    o = ''
    for k, (name, sub, x, y) in enumerate(items):
        o += opbox(x, y, name, sub, 'acc' if k == hi else ['amber', 'amber', 'green', 'green', 'blue', 'violet'][k], 100, 30)
    return o
B1 = [
    t(180, 22, 'Bytes per file, not rows', 9.4, bold=True) + board(0) + cap('Small files cost metadata and tasks.', '', 'amber', y=172, h=34),
    t(180, 22, 'Every MERGE adds folders', 9.4, bold=True) + board(1) + cap('Readers merge deltas on the fly.', '', 'amber', y=172, h=34),
    t(180, 22, 'Rewrite into one base', 9.4, bold=True) + board(2) + cap('Cleaner removes the old folders.', '', 'green', y=172, h=34),
    t(180, 22, 'Expectations as queries', 9.4, bold=True) + board(3) + cap('Alert on any FAIL.', '', 'green', y=172, h=34),
    t(180, 22, 'Fresh views only', 9.4, bold=True) + board(4) + cap('Stale views are skipped, then rebuilt.', '', 'blue', y=172, h=34),
    t(180, 22, 'Evidence beats definitions', 9.4, bold=True) + board(5) + cap('Quote what you measured.', '', 'violet', y=172, h=34),
]
see_caps = ['Files are tiny compared with a block.',
            'A recent partition had nine delta folders.',
            'One major compaction: one base.',
            'Seven data tests, all PASS.',
            'The optimiser uses the view when fresh.',
            'The project, told with numbers.']
behind_caps = ['Each file means metadata and a task.',
               'Updates are delete + insert deltas.',
               'Base + deltas rewritten together.',
               'Reconciliation becomes automatic.',
               'Write IDs tell Hive if the view is current.',
               'Interviewers test understanding, not memory.']
two = anim_two('Review, then explain', 'From review to interview', 'Real lab outputs', 'What it means', see, B1, see_caps, behind_caps)

# ---- scenario 1: mock interview flow
e1 = (t(180, 22, '“Managed or external?”', 9.4, bold=True) + t(180, 56, 'definition: who owns the files', 8.4, 'ink2') + cap('Start with one clear sentence.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, '“What did you choose?”', 9.4, bold=True) + t(180, 56, 'raw external, silver managed', 8.4, 'ink2') + cap('Connect to your project.', '', 'green', y=150, h=34))
e3 = (t(180, 22, '“Why?”', 9.4, bold=True) + t(180, 56, 'dropping raw must not delete source', 8.2, 'ink2') + cap('Give the reason.', '', 'green', y=150, h=34))
e4 = (t(180, 22, '“Anything surprising?”', 9.4, bold=True) + t(180, 56, 'Hive 4: TRANSLATED_TO_EXTERNAL', 8.2, 'ink', mono=True) + cap('Show you looked closely.', '', 'violet', y=150, h=34))
e5 = (t(180, 22, 'Strong answer', 9.4, 'acc', bold=True) + t(180, 56, 'definition → choice → reason → detail', 8.2, 'ink2') + cap('A pattern for every question.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'One question, four follow-ups',
              'How a good interviewer digs, and how to answer each layer.',
              'Mock interview', 'An interviewer asks a definition, then what you chose, why, and what surprised you; answer each layer with your project', [e1, e2, e3, e4, e5],
              ['Definition.',
               'Your choice.',
               'Your reason.',
               'A real detail.',
               'The pattern.'],
              hid='scenario-interview')

# ---- scenario 2: compaction backlog
b1 = (t(180, 22, 'Queries slower every week', 9.4, bold=True) + t(180, 56, 'same data size, more time', 8.4, 'ink2') + cap('A production mystery.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Count delta folders', 9.4, bold=True) + t(180, 56, 'hundreds per partition', 8.4, 'ink2') + cap('Readers merge them all.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'SHOW COMPACTIONS', 9.4, bold=True) + t(180, 56, 'many “failed”, none recent', 8.4, 'ink2') + cap('The worker was not running.', '', 'red', y=150, h=34))
b4 = (t(180, 22, 'Fix and catch up', 9.4, bold=True) + t(180, 56, 'enable workers, COMPACT \'major\'', 8.2, 'ink', mono=True) + cap('Partition by partition.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Add an alert', 9.4, 'acc', bold=True) + t(180, 56, 'deltas per partition > threshold', 8.2, 'ink2') + cap('Never again silently.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'The warehouse that slowed down by itself',
              'A classic ACID operations incident. (Typical; numbers illustrative.)',
              'Compaction backlog', 'Queries slow down as delta folders pile up because compaction stopped; the fix is to restart compaction, compact, and alert on delta counts', [b1, b2, b3, b4, b5],
              ['Slower each week.',
               'Too many deltas.',
               'Compaction failing.',
               'Catch up.',
               'Monitor it.'],
              hid='scenario-compaction')

# ---- scenario 3: design round
u1 = (t(180, 22, '“Design a ride-booking warehouse”', 9.2, bold=True) + t(180, 56, 'rides, drivers, payments', 8.4, 'ink2') + cap('A design round.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Ask for the KPIs first', 9.4, bold=True) + t(180, 56, 'rides/day, cancellations, ETA', 8.4, 'ink2') + cap('Like Lesson 12.1.', '', 'green', y=150, h=34))
u3 = (t(180, 22, 'Grain and keys', 9.4, bold=True) + t(180, 56, 'one row per ride, latest status', 8.4, 'ink2') + cap('MERGE on ride_id.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'History and late data', 9.4, bold=True) + t(180, 56, 'driver SCD 2 · touched dates', 8.4, 'ink2') + cap('Same patterns, new nouns.', '', 'violet', y=150, h=34))
u5 = (t(180, 22, 'Quality and operations', 9.4, 'acc', bold=True) + t(180, 56, 'quarantine · tests · compaction', 8.2, 'ink2') + cap('That is a complete answer.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Reusing the capstone in a design round',
              'The capstone is a template for most “design a warehouse” questions.',
              'Design round', 'Answer a design question with the capstone pattern: KPIs, grain and keys, history and late data, quality and operations', [u1, u2, u3, u4, u5],
              ['New domain.',
               'Requirements first.',
               'Grain and key.',
               'History and late data.',
               'Quality and operations.'],
              hid='scenario-design')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>From review to interview</h2>
  <p>Left: real outputs from the review. Right: what each one means.</p>
''' + two + '''
  <p>Three live scenarios follow: a mock interview, a compaction incident, and a design round.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Where review and interview skills are used</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'review', 11, 'green', bold=True) + t(60, 58, 'before go-live', 7.4, 'ink2'),
    '1. Production readiness reviews',
    'Data platform teams review new pipelines against a checklist like ours before they feed executive dashboards.',
    ['New pipeline', '*review', 'Go-live']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'tests', 12, 'blue', bold=True) + t(60, 58, 'after each load', 7.4, 'ink2'),
    '2. Data tests in schedulers',
    'Airflow DAGs run data tests after each load and stop publishing when a test fails.',
    ['Load', '*tests', 'Publish or alert']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'ops', 12, 'violet', bold=True) + t(60, 58, 'compaction', 7.4, 'ink2'),
    '3. Operating ACID tables',
    'Teams monitor compaction backlog and delta counts the way they monitor disk space.',
    ['Deltas', '*compaction', 'Fast reads']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'hiring', 11, 'acc', bold=True) + t(60, 58, 'data roles', 7.4, 'ink2'),
    '4. Data engineering interviews',
    'Service companies, product companies and startups ask Hive, SQL and project questions for data engineer, ETL developer and analytics engineer roles.',
    ['Concepts', '*project story', 'Offer']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'MV', 12, 'acc', bold=True) + t(60, 58, 'fast BI', 7.4, 'ink2'),
    '5. Faster dashboards without changing them',
    'Materialized views let platform teams speed up common queries without asking analysts to rewrite reports.',
    ['Dashboard query', '*MV rewrite', 'Seconds']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> this lesson reviews the warehouse built in <a href="../02-build-the-warehouse/">Lesson 12.2</a> and uses compaction (<a href="../../07-acid-and-iceberg/03-compaction-and-iceberg/">7.3</a>) and materialized views (<a href="../../09-extending-hive/02-views-and-materialized-views/">9.2</a>).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB', NQ, 'questions')
