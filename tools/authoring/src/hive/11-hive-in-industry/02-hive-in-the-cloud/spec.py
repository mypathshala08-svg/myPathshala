import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from hivekit import tables
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return re.sub(r'; Query ID[^\n]*', '', open(CAP + n).read().rstrip())
BODY = body(HERE)

META = dict(
    module='11-hive-in-industry', lesson='02-hive-in-the-cloud', n='11.2',
    module_label='Module 11 · Hive in industry today',
    title='Hive in the cloud: S3, EMR, Dataproc and HDInsight',
    desc='Run Hive 4.2.1 on S3-compatible object storage through the S3A connector and measure what changes: Tez tasks failing without credentials, a partitioned Parquet table on s3a://, directory markers, one partition overwrite costing 85 requests with four server-side copies, staging refused on another file system, partitions invisible until MSCK REPAIR, and request counts per query. Plus the Hive versions, storage connectors and metastore options of Amazon EMR, Google Dataproc and Azure HDInsight in 2026.',
    og_desc='One output file, 85 S3 requests and four server-side copies: what really happens when Hive writes to object storage, plus EMR, Dataproc and HDInsight compared.',
    minutes=45, level='Intermediate → Advanced',
    lead='Most new Hive deployments keep data in cloud object storage and treat clusters as temporary. This lesson connects our Hive 4.2.1 lab to an <b>S3-compatible server</b>, logs every request Hive makes, and compares the managed services of AWS, Google Cloud and Azure. <b>All outputs are real</b>; the configuration files are in the course lab folder.',
    chips=['Hive 4.2.1 · S3A', '85 requests for one partition', 'EMR · Dataproc · HDInsight', 'Runs in your browser (Python)'],
)

MAIN = '''# Request counts from the lab, and what they would cost at scale
lab = {"read 9 files": 90, "overwrite 1 partition (1 file)": 85}
for job, n in lab.items():
    print(f"{job:32} {n:4} requests")

# Each extra file costs at least a HEAD and a GET when it is read
files_per_day, days, queries_per_day = 400, 365, 200
gets = files_per_day * days * 2 * queries_per_day
print(f"\\nfull scans of a year of {files_per_day} files/day: {gets:,} requests per day")
'''
RUN = dict(
    heading='Run the code: requests, files and costs',
    intro='<p>These programs use the real request counts from the lab to reason about object storage at scale. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('lab = {"read 9 files": 90, "overwrite 1 partition (1 file)": 85}', 'Both numbers were counted in the S3 server log in Steps 5 and 8.'),
        ('gets = files_per_day * days * 2 * queries_per_day', 'Two requests per file is a lower bound; listings add more.'),
    ],
    tasks=[
        dict(label='1 · Requests at scale', hint='Press <b>Run</b>. Then halve the number of files per day and see the effect.', code=None),
        dict(label='2 · Predict first: renames', hint='<b>Predict first:</b> each output file was copied 4 times. How many copies for 5,000 files?',
             code='''files, copies_per_file = 5000, 4
print("server-side copies:", files * copies_per_file)
print("plus deletes:", files * copies_per_file)
'''),
        dict(label='3 · Pruning saves requests', hint='A filter on the partition column reads one day instead of all nine.',
             code='''per_file = 10     # HEAD + GET ≈ 10 requests per file in Step 8 (90 / 9)
for days in (9, 1):
    print(f"{days} partitions read -> about {days * per_file} requests")
'''),
        dict(label='4 · Pick a URI scheme', hint='Each cloud has its own connector and scheme.',
             code='''schemes = {"Amazon EMR": "s3://", "open-source S3A": "s3a://",
           "Google Dataproc": "gs://", "Azure HDInsight (ADLS Gen2)": "abfs://"}
for k, v in schemes.items():
    print(f"{v:8} {k}")
'''),
        dict(label='5 · Spot the error', hint='This check says a partition is ready because the object exists. Hive disagrees.', expect='error',
             code='''object_in_bucket = True
partition_in_metastore = False          # nobody ran MSCK / ADD PARTITION
hive_sees_rows = object_in_bucket       # bug
assert hive_sees_rows == (object_in_bucket and partition_in_metastore), "Hive reads metastore partitions"
print("ready")
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: the S3 side of the lab',
    intro='<p>More from the object-storage lab. <b>Outputs are real</b> (Hive 4.2.1 with S3A against a local S3-compatible server).</p>',
    items=[
        dict(title='1 · The table location', cmd='SHOW CREATE TABLE orders_s3;', file='beeline',
             output='''CREATE EXTERNAL TABLE `orders_s3`(
  `order_id` int, `customer_id` int, `city` string,
  `amount` decimal(10,2), `status` string)
PARTITIONED BY (`order_date` date)
ROW FORMAT SERDE 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
…
LOCATION 's3a://tiffingo-lake/warehouse/orders_s3'
TBLPROPERTIES ('bucketing_version'='2', …)''',
             note='The only cloud-specific part of the definition is the location URI.'),
        dict(title='2 · Hive’s object-store settings', cmd='SET hive.blobstore.supported.schemes;\nSET hive.blobstore.optimizations.enabled;\nSET hive.blobstore.use.blobstore.as.scratchdir;\nSET hive.exec.stagingdir;', file='beeline',
             output='hive.blobstore.supported.schemes=s3,s3a,s3n\nhive.blobstore.optimizations.enabled=true\nhive.blobstore.use.blobstore.as.scratchdir=false\nhive.exec.stagingdir=.hive-staging',
             note='Hive treats s3, s3a and s3n as blob stores and keeps intermediate scratch data off them by default; the final staging folder still sits beside the table (Step 5).'),
        dict(title='3 · Partitions after the repair', cmd='SELECT COUNT(*) AS n, COUNT(DISTINCT order_date) AS days FROM orders_s3;', file='beeline',
             output=capf('l112_counts.txt'),
             note='Nine partitions after MSCK REPAIR added the one created outside Hive.'),
    ],
)

TRACE = dict(
    heading='Why one file needed several copies',
    intro='<p>Follow the path of the single output file from Step 5 through Hive’s staging folders.</p>',
    code='''path = ["_task_tmp.-ext-10000/-tmp.000000_0",   # the task writes here (1 upload)
        "-tmp.-ext-10000/000000_0",             # task commit: rename 1
        "-tmp.-ext-10000.moved/000000_0",       # job commit:  rename 2
        "-ext-10000/000000_0",                  # rename 3
        "order_date=2026-10-08/000000_0"]       # move into the table: rename 4
copies = len(path) - 1
print("uploads: 1   server-side copies:", copies, "  deletes:", copies)
''',
    notes={1: 'Upload :: The only time the data bytes travel from the task to S3.', 2: 'Rename :: On HDFS a metadata change; on S3 a COPY plus DELETE.', 5: 'Final move :: Into the partition prefix the metastore points to.'},
)

WORKED_INTRO = 'Three cloud decisions from real platforms.'
EXAMPLES = [
    dict(level='b', tag='Data engineering · cloud', title='Rewrite a table for S3',
         problem='<p>Move an HDFS external table definition to an S3 bucket.</p>',
         inp="LOCATION 'hdfs://nn1/warehouse/orders'",
         approach=['Copy the data (DistCp).', 'Change the location.', 'Repair partitions.'],
         code='''print("hadoop distcp hdfs://nn1/warehouse/orders s3a://tiffingo-lake/warehouse/orders")
print("ALTER TABLE orders SET LOCATION 's3a://tiffingo-lake/warehouse/orders';")
print("MSCK REPAIR TABLE orders;   -- partition locations are stored separately")
''', notes={3: 'Partitions :: Each partition has its own location in the metastore; repair or re-add them after a move.'},
         tryit='Compare COUNT(*) per partition before and after, as in Step 3.'),
    dict(level='i', tag='Platform · cost', title='Size a transient cluster',
         problem='<p>Compare an always-on cluster with one created for a 40-minute nightly load.</p>',
         inp='12 nodes, illustrative ₹40 per node-hour',
         approach=['Always-on: 24 hours a day.', 'Transient: load time plus start-up.', 'Storage is paid in both cases.'],
         code='''nodes, rate = 12, 40
always_on = nodes * 24 * rate
transient = nodes * (40 + 10) / 60 * rate     # 10 minutes to start
print(f"always on: ₹{always_on:,.0f}/day   transient: ₹{transient:,.0f}/day")
''', notes={3: 'Start-up :: Clusters take minutes to create; include it.'},
         tryit='This only works if the metastore and data live outside the cluster.'),
    dict(level='a', tag='Architecture · migration', title='Choose a managed service',
         problem='<p>Pick a target for an on-premises Hive 4 platform using the 2026 version facts.</p>',
         inp='needs: Hive SQL, Iceberg, managed catalogue',
         approach=['List the Hive versions offered.', 'Check the catalogue options.', 'Note gaps against Hive 4.'],
         code='''svc = {"EMR 7.14": ("Hive 3.1.3", "Glue / RDS"),
       "Dataproc 2.2": ("Hive 3.1.3", "Dataproc Metastore ≤ 3.1.2"),
       "HDInsight 5.1": ("Hive 3.1.2", "Azure SQL"),
       "self-managed": ("Hive 4.2.1", "your own RDBMS")}
for k, (h, m) in svc.items():
    print(f"{k:14} {h:11} {m}")
''', notes={1: 'Versions :: From provider release notes, October 2026.'},
         tryit='Every managed option is a step back from Hive 4: re-test SQL and plan Iceberg through the engine that supports it best.'),
]

QUIZ = mix([
    dict(q='Beginner: Which URI scheme does Hadoop’s open-source S3 connector use?', options=['s3a://', 'hdfs://', 'gs://', 'file://'], answer=0,
         why='EMR’s own connector uses s3://.'),
    dict(q='Beginner: What happens to an external table’s data on S3 when the cluster is deleted?', options=['It is deleted', 'It stays in the bucket', 'It moves to HDFS', 'It is archived'], answer=1,
         why='Storage and compute are separate.'),
    dict(q='Beginner: Which Hive version do EMR, Dataproc and HDInsight ship in 2026?', options=['Hive 4.x', 'Hive 3.1.x', 'Hive 2.1', 'Hive 1.2'], answer=1,
         why='EMR 3.1.3, Dataproc 3.1.3, HDInsight 3.1.2.'),
    dict(q='Intermediate: Why did the first INSERT fail in our lab?', options=['Wrong bucket', 'The Tez tasks had no AWS credentials', 'Parquet unsupported', 'Metastore down'], answer=1,
         why='NoAuthWithAWSException in a task.'),
    dict(q='Intermediate: What is a rename on S3?', options=['A metadata change', 'A copy of the object plus a delete', 'Impossible', 'A symbolic link'], answer=1,
         why='One output file was copied four times.'),
    dict(q='Intermediate: An object was copied into a new partition prefix. What did Hive return?', options=['The new rows', '0 rows until MSCK REPAIR TABLE', 'An error', 'Duplicates'], answer=1,
         why='Hive plans from metastore partitions.'),
    dict(q='Advanced: Why did setting hive.exec.stagingdir to file:///tmp fail?', options=['Permissions', 'The final move must stay on the table’s file system (Wrong FS)', 'Disk full', 'Syntax'], answer=1,
         why='Use rename-free committers or Iceberg instead.'),
    dict(q='Advanced: Why do small files hurt more on object storage?', options=['They are larger', 'Each file costs billed requests with network latency', 'S3 cannot store them', 'Hive skips them'], answer=1,
         why='About 10 requests per file in Step 8.'),
])

REVISION = [
    'Cloud pattern: data in <b>object storage</b>, metastore outside the cluster, clusters that can be <b>deleted</b>.',
    'Connectors: <code>s3a://</code> (S3A), <code>s3://</code> (EMRFS), <code>gs://</code> (Dataproc), <code>abfs://</code> (ADLS Gen2).',
    'Every process needs credentials, including the Tez tasks; use IAM roles, not keys in files.',
    'S3 rename = copy + delete: one file, 1 upload, 4 copies, 85 requests.',
    'Staging must stay on the table’s file system (<code>Wrong FS</code>); use committers or Iceberg to avoid copies.',
    'Folders are key prefixes; new prefixes need <code>ADD PARTITION</code> or <code>MSCK REPAIR</code> (0 rows before, 1,662 after).',
    'About 10 requests per file read: fewer, larger files and partition pruning save time and money.',
    'Managed Hive in 2026: EMR 3.1.3 · Dataproc 3.1.3 · HDInsight 5.1 3.1.2. HDInsight on AKS retired 31 Jan 2025.',
]
FAQ = [
    ('Is S3 still “eventually consistent”?', 'No. Amazon S3 has offered strong read-after-write consistency for all requests since December 2020, and Google Cloud Storage and ADLS Gen2 are strongly consistent too. Old advice about S3Guard and consistency layers is obsolete; the rename and listing costs remain.'),
    ('Should I use s3:// or s3a://?', 'On Amazon EMR use <code>s3://</code>, which is EMRFS with EMR’s optimisations. Everywhere else (self-managed Hadoop, S3-compatible stores such as MinIO or Ceph) use <code>s3a://</code>. <code>s3n://</code> is obsolete.'),
    ('Can Hive ACID tables live on S3?', 'Yes, Hive ACID works on object storage, but every compaction and commit rewrites and moves files, so costs are higher. For updated tables in the cloud, most teams choose Iceberg (Lesson 11.3).'),
    ('Do I still need HDFS on a cloud cluster?', 'Usually a small one for scratch and temporary data, which Hive keeps off blob storage by default (<code>hive.blobstore.use.blobstore.as.scratchdir=false</code>). Table data lives in the bucket.'),
    ('Why does the lab use a fake S3 server?', 'So that every request can be logged and nothing costs money. It speaks the S3 API, and Hive uses the same S3A connector as with Amazon S3; latencies are much lower than in the real service.'),
]

PRACTICE_INTRO = 'Programs for object-storage checks, with the SQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Build a location', stmt='Build an S3A table location from bucket and path.', inp='tiffingo-lake, warehouse/orders_s3',
         code='''print("s3a://" + "tiffingo-lake" + "/" + "warehouse/orders_s3")
''', explain="Use it in LOCATION '…' of CREATE EXTERNAL TABLE."),
    dict(level='easy', title='Partition prefix', stmt='Build the key prefix of one partition.', inp='order_date = 2026-10-09',
         code='''print("warehouse/orders_s3/order_date=2026-10-09/")
''', explain='Objects under this prefix belong to the partition once the metastore knows it.'),
    dict(level='easy', title='Requests per file', stmt='Average requests per file in the read test.', inp='90 requests, 9 files',
         code='''print(90 / 9)
''', explain='HEAD and GET calls; larger files spread this cost over more rows.'),
    dict(level='medium', title='Missing partitions', stmt='Find prefixes in the bucket that the metastore does not know.', inp='bucket and metastore lists',
         code='''bucket = {"2026-10-07", "2026-10-08", "2026-10-09"}
metastore = {"2026-10-07", "2026-10-08"}
print("ALTER TABLE orders_s3 ADD", *[f"PARTITION (order_date='{d}')" for d in sorted(bucket - metastore)])
''', explain='Adding exact partitions is cheaper than MSCK, which lists the whole table.'),
    dict(level='medium', title='Copy cost of a commit', stmt='Estimate copied bytes for a commit.', inp='2,000 files of 128 MB, 4 copies each',
         code='''files, mb, copies = 2000, 128, 4
print(f"{files * mb * copies / 1024:,.0f} GB copied inside S3")
''', explain='Server-side copies are faster than uploads but still take time per object.'),
    dict(level='medium', title='Credentials check', stmt='List which processes need cloud credentials.', inp='Hive components',
         code='''for p in ["HiveServer2", "metastore", "Tez tasks", "compaction workers"]:
    print("needs access:", p)
''', explain='Our lab failed at the tasks; in the cloud one instance role covers all.'),
    dict(level='business', title='Always-on vs transient', stmt='Savings per year of a transient cluster.', inp='₹11,520/day vs ₹400/day (illustrative)',
         code='''print(f"₹{(11520 - 400) * 365:,} per year")
''', explain='Only possible because data and catalogue outlive the cluster.'),
    dict(level='business', title='Small-file bill', stmt='Request cost of reading 400 small files instead of 4 large ones, 200 times a day.', inp='illustrative ₹0.035 per 1,000 GETs',
         code='''price = 0.035 / 1000
for files in (400, 4):
    print(f"{files:4} files: ₹{files * 2 * 200 * 365 * price:,.0f} per year")
''', explain='Small per query, but it adds up across tables and is paid with latency too.'),
]

SCN_INTRO = 'Cloud questions appear in almost every data engineering interview today.'
SCENARIOS = (
    scn('Any company · cloud', 'Fresher', '“How is Hive different on S3?”',
        'Explain what changes when Hive tables live in S3 instead of HDFS.',
        'do you know storage/compute separation?',
        '<p>The SQL stays the same; the location becomes s3a:// or s3://. Data survives the cluster, so clusters can be temporary. Renames become copies, listings become requests, and permissions come from IAM roles. Partitions added directly to the bucket must be registered with ADD PARTITION or MSCK REPAIR.</p>', 'Saying S3 is just a remote HDFS.') +
    scn('Data engineering', 'Mid-level', 'Job finishes late on S3',
        'All tasks finish in 5 minutes, but the INSERT takes 25 minutes.',
        'do you know commit behaviour?',
        '''<ol>
          <li>Count output files: thousands of small files are moved by copy + delete during commit.</li>
          <li>Reduce files (merge settings, DISTRIBUTE BY) and use rename-free committers where the engine supports them.</li>
          <li>For new tables, use Iceberg, which commits through metadata.</li>
        </ol>''', '“Add more nodes.”') +
    scn('Platform', 'Mid-level', 'Rows missing after an upstream load',
        'An upstream job wrote today’s files to S3, but Hive shows no rows for today.',
        'do you know the metastore’s role?',
        '''<ul>
          <li>The partition is not registered: Hive plans from metastore partitions.</li>
          <li>Run ALTER TABLE … ADD PARTITION in the upstream job, or MSCK REPAIR on a schedule.</li>
          <li>On Athena, partition projection removes the need to register.</li>
        </ul>''', 'Restarting HiveServer2.') +
    scn('Architecture', 'Senior', 'Move an on-prem Hive 4 platform to the cloud',
        '200 TB on HDFS, Hive 4, Ranger, Spark and Trino users.',
        'can you plan versions, catalogue and security?',
        '''<ul>
          <li>Managed services ship Hive 3.x: decide between EMR/Dataproc/HDInsight with SQL re-testing, or self-managed Hive 4 on VMs or Kubernetes.</li>
          <li>Data via DistCp with per-partition validation; catalogue to Glue/Dataproc Metastore or an RDS-backed HMS.</li>
          <li>Security from Ranger/Kerberos to IAM and Lake Formation; consider moving shared tables to Iceberg during the move.</li>
        </ul>''', 'Copying data first and discovering the version gap later.')
)
