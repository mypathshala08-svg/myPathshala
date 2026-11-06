import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
CLD = os.path.join(HERE, '..', '..', 'lab', 'cloud') + os.sep
def capf(n):
    return re.sub(r'; Query ID[^\n]*', '', open(CAP + n).read().rstrip())

def opbox(x, y, label, sub='', tone='card', w=128, h=26):
    o = box(x, y, w, h, tone) + t(x + w / 2, y + (11 if sub else 16), label, 7.2, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 21, sub, 6.4, 'ink2', mono=True)
    return o

# ---------------------------------------------------------------- story
sc = (opbox(14, 22, 'HiveServer2 + Tez', 'compute: can be switched off', 'blue', 150, 30) + opbox(14, 66, 'Metastore', 'Postgres / Glue / Dataproc MS', 'amber', 150, 30) +
      arrow(166, 37, 236, 66, 'acc', 1.6) + arrow(166, 81, 236, 81, 'acc', 1.4) +
      box(240, 44, 140, 60, 'green') + t(310, 66, 'Object storage', 8.6, bold=True) + t(310, 84, 's3a://tiffingo-lake', 7.2, 'ink2', mono=True) +
      box(410, 12, 222, 128, 'card') + t(521, 30, 'What changed on S3', 8.6, bold=True) +
      ''.join(t(422, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([('no credentials in tasks → fail', 'red'), ('1 file written, 4 server-side copies', 'amber'), ('85 requests for one partition', 'amber'), ('new folder: invisible until MSCK', 'ink'), ('cluster gone, data stays', 'green')])))
scene_svg = scene('Compute (HiveServer2 and Tez), the catalogue (metastore) and the data (object storage) are separate in the cloud. Our lab table on S3 showed five behaviours you do not see on HDFS.', sc,
                  'In the cloud, storage <tspan font-weight="700" class="s-acc">outlives</tspan> the cluster.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Shut the cluster down at night”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s finance team sees the Hadoop cluster bill: twelve machines run all night for a load that takes forty minutes. The new plan is to keep the data in cloud object storage, start a cluster for the load, and shut it down afterwards. Kabir is asked to prove it works with Hive.</p>

{scene_svg}

K> Sir, if Hive just reads files, does it matter whether they are on HDFS or on S3?
A> The SQL is the same; the table location changes from <code>hdfs://</code> to <code>s3a://</code>. But object storage is <b>not a file system</b>. A “rename” is a copy plus a delete, a “folder” is only a key prefix, every listing is an HTTP request, and permissions come from cloud credentials, not from Linux users.
R> So the same query can behave differently?
A> It answers the same, but it fails differently, costs differently and is slower in different places. Today we connect our Hive 4.2.1 lab to an S3-compatible server, write a partitioned table there, count every request Hive makes, and compare the managed cloud services. All outputs are real.
  </div>
</section>
'''

lv = '''
LEVELS> Hive in the cloud at three levels
L1> Kitchen and warehouse
      <ul>
        <li>The cluster is the kitchen; object storage is the warehouse across the road.</li>
        <li>You can close the kitchen at night; the food in the warehouse stays.</li>
        <li>Moving a box inside the warehouse is slow: you copy it to a new shelf and throw the old one away.</li>
      </ul>
L2> The pieces you configure
      <ul>
        <li>A file-system connector: <b>S3A</b> (<code>s3a://</code>, open source), <b>EMRFS</b> on Amazon EMR (<code>s3://</code>), the Cloud Storage connector on Dataproc (<code>gs://</code>), <b>ABFS</b> on Azure (<code>abfs://</code>).</li>
        <li>Credentials for every process that touches data: HiveServer2, the metastore <b>and</b> the Tez tasks (an IAM role or service account in production).</li>
        <li>A metastore outside the cluster: a managed database, AWS Glue Data Catalog or Dataproc Metastore, so the catalogue survives when clusters are deleted.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>Tasks without credentials failed with <code>NoAuthWithAWSException</code>; the session itself had connected fine.</li>
        <li>One partition overwrite wrote <b>1</b> object and made <b>4</b> server-side copies through staging folders: 85 requests in total.</li>
        <li>A folder added with an S3 tool stayed invisible to Hive (0 rows) until <code>MSCK REPAIR TABLE</code>; staging on another file system was refused (<code>Wrong FS</code>).</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Hive with object storage and managed services</h2>
''' + def_block(
    'In the cloud, Hive usually runs with <b>separated storage and compute</b>: table data lives in object storage (Amazon S3, Google Cloud Storage, Azure Data Lake Storage Gen2) accessed through a Hadoop file-system connector, the metastore runs as a managed database or catalogue service (AWS Glue Data Catalog, Dataproc Metastore, Azure SQL Database), and compute runs on managed clusters (Amazon EMR, Google Dataproc, Azure HDInsight) that can be resized or deleted without losing data. Object stores offer strong read-after-write consistency but no atomic rename and no real directories, so Hive’s staging-and-move commit, partition discovery and listing-heavy planning cost more requests and time than on HDFS.',
    'In the cloud, Hive tables usually live in object storage such as S3, the metastore is a managed service, and the cluster is temporary. The SQL stays the same; renames, folders, credentials and costs behave differently.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Object storage', 'Buckets of objects addressed by key: S3, GCS, ADLS Gen2.'),
    ('S3A', 'Hadoop’s open-source S3 connector, URI scheme s3a://.'),
    ('EMRFS', 'Amazon EMR’s own S3 connector, scheme s3://.'),
    ('Key prefix', 'The “folder” part of an object key, e.g. order_date=2026-10-01/.'),
    ('Directory marker', 'An empty object ending in / that tools create to look like a folder.'),
    ('Staging directory', 'Where Hive writes results before moving them into the table (.hive-staging).'),
    ('Transient cluster', 'A cluster created for one job and deleted afterwards.'),
    ('Glue Data Catalog', 'AWS’s managed, Hive-metastore-compatible catalogue.'),
]) + '''

  <h3>HDFS versus object storage, as Hive sees it</h3>
''' + table(['Operation', 'HDFS', 'Object storage (S3, GCS, ADLS)', 'Seen in our lab'], [
    ['Rename a file or folder', 'Metadata change, atomic', 'Copy every object, then delete (ADLS Gen2 with hierarchical namespace: atomic)', '1 write + 4 copies for one file'],
    ['List a folder', 'NameNode call', 'Paged HTTP LIST requests', '90 requests for a 9-file query'],
    ['A new folder appears', 'Hive still needs the partition in the metastore', 'Same', '0 rows until MSCK REPAIR'],
    ['Who may read', 'Linux users, HDFS ACLs, Ranger', 'IAM roles, bucket policies, service accounts', 'Tasks failed without keys'],
    ['Cluster deleted', 'Data deleted with it', 'Data stays', '—'],
], minw=760) + lv + '''
EXAM> “How does Hive work on S3?” Through a Hadoop connector (S3A, or EMRFS on EMR) with tables at s3a:// or s3:// locations, credentials from IAM roles, and usually an external metastore such as Glue. S3 has no atomic rename, so commits copy data and listings cost requests; use fewer, larger files, partition pruning, and table formats such as Iceberg that avoid renames.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Managed Hive in the three big clouds</h2>
  <p>Versions from the providers’ release documentation, checked October 2026. All three still ship <b>Hive 3.x</b>, not Hive 4.</p>
''' + table(['Service', 'Hive version (latest release)', 'Storage', 'Metastore options', 'Notes'], [
    ['Amazon EMR 7.x', 'Hive 3.1.3 (EMR 7.14: <code>3.1.3-amzn-24</code>)', 'S3 via EMRFS (<code>s3://</code>)', 'Glue Data Catalog, or external MySQL/Aurora', 'EMR Serverless runs Hive jobs without a cluster'],
    ['Google Dataproc 2.2', 'Hive 3.1.3 (image 2.2.x, Spark 3.5.3)', 'Cloud Storage (<code>gs://</code>)', 'Dataproc Metastore (Hive 3.1.2 default; 2.3.6, 2.2.0, 1.2.2)', 'Dataproc Metastore offers no Hive 4.x'],
    ['Azure HDInsight 5.1', 'Hive 3.1.2 (Spark 3.3.1, Hadoop 3.3.4)', 'ADLS Gen2 (<code>abfs://</code>)', 'Built-in or custom Azure SQL Database', 'HDInsight on AKS retired 31 Jan 2025; Microsoft points to Fabric'],
    ['Self-managed (our lab)', 'Hive 4.2.1', 'Any S3-compatible store via S3A', 'Postgres/MySQL metastore', 'Newest features; you run everything'],
], minw=820) + '''
''' + table(['Related service', 'What it does with Hive tables'], [
    ['AWS Glue Data Catalog', 'Hive-compatible catalogue used by EMR, Athena, Redshift Spectrum and Glue jobs; the Glue client for Hive 3 arrived in May 2026.'],
    ['Amazon Athena', 'Serverless SQL (Trino-based) over tables in the Glue catalogue, written with Hive-style DDL; partition projection computes partitions instead of listing them.'],
    ['BigQuery / BigLake', 'Can query external tables on Cloud Storage that Dataproc jobs wrote.'],
    ['Microsoft Fabric', 'Microsoft’s suggested destination for HDInsight on AKS workloads (Spark and Delta, not Hive).'],
], minw=640) + '''
WARN> A managed service means somebody else patches the machines, not that the behaviour is the same as on-premises. Check the <b>Hive version</b> (cloud services are on 3.x, so Hive 4 features such as Iceberg-first defaults and newer SQL may be missing), the <b>connector</b> and the <b>catalogue</b> before you migrate SQL.
</section>
'''

CORE = open(CLD + 'core-site.xml').read().rstrip()
S3YML = open(CLD + 's3.yml').read().rstrip().replace('/root/lab/cloud/', './cloud/')
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>A Hive table on S3, request by request</h2>
  <p>Our lab uses an S3-compatible server (moto) on the lab machine, so every request can be logged and nothing costs money. Hive 4.2.1 talks to it through the standard <b>S3A</b> connector, exactly as it would to Amazon S3. Configuration files are in the course lab folder (<code>lab/cloud</code>).</p>
''' + stepper([
    ('Step 1 · Point Hadoop at the object store',
     code('xml', 'core-site.xml (metastore and HiveServer2)', CORE) + code('yaml', 'compose override s3.yml', S3YML),
     '<code>HADOOP_OPTIONAL_TOOLS=hadoop-aws</code> puts the S3A connector and the AWS SDK on Hive’s classpath. <code>path.style.access</code> and the endpoint are only needed for S3-compatible servers; on AWS you set the region. <b>Never put keys in core-site.xml in production</b>: on EC2/EMR the instance’s IAM role provides credentials automatically.'),
    ('Step 2 · The first write fails in the tasks',
     code('sql', 'beeline', "INSERT OVERWRITE TABLE orders_s3 PARTITION (order_date)\nSELECT order_id, customer_id, city, amount, status, order_date\nFROM orders WHERE order_date BETWEEN '2026-10-01' AND '2026-10-07';", capf('l112_nocreds.txt')),
     'Creating the table worked: the metastore and HiveServer2 could reach the bucket. The INSERT failed inside a <b>Tez task</b>, which did not see the keys we had first put only in the session. Every process that reads or writes data needs credentials. We added <code>AWS_ACCESS_KEY_ID</code>/<code>AWS_SECRET_ACCESS_KEY</code> to both containers (Step 1); in the cloud an instance role covers all processes.'),
    ('Step 3 · A partitioned Parquet table on S3',
     code('sql', 'beeline', "CREATE EXTERNAL TABLE orders_s3 (\n  order_id INT, customer_id INT, city STRING, amount DECIMAL(10,2), status STRING)\nPARTITIONED BY (order_date DATE)\nSTORED AS PARQUET\nLOCATION 's3a://tiffingo-lake/warehouse/orders_s3';\n\n-- the INSERT from Step 2, then:\nSELECT order_date, COUNT(*) AS n FROM orders_s3 GROUP BY order_date ORDER BY order_date;", capf('l112_s3_load.txt')),
     'The same counts as the source <code>orders</code> table for each day. Nothing in the SQL is cloud-specific except the <code>LOCATION</code>. External tables on object storage are the most common cloud pattern: dropping the table or deleting the cluster leaves the data in the bucket.'),
    ('Step 4 · What is really in the bucket',
     code('python', 'list the objects (boto3, like aws s3 ls --recursive)', "s3.list_objects_v2(Bucket='tiffingo-lake', Prefix='warehouse/orders_s3/')", capf('l112_s3_list.txt')),
     'Seven Parquet objects, one per partition, and a <b>0-byte object</b> <code>warehouse/orders_s3/</code>: a directory marker, because S3 has no folders. <code>order_date=2026-10-01/</code> is only part of each key. Tools that “list a folder” send LIST requests with a prefix, page by page.'),
    ('Step 5 · One partition overwrite, every request counted',
     code('sql', 'beeline (S3 server log counted)', "INSERT OVERWRITE TABLE orders_s3 PARTITION (order_date = '2026-10-08')\nSELECT order_id, customer_id, city, amount, status FROM orders_s3 WHERE order_date = '2026-10-07';", capf('l112_requests.txt') + '\n\n' + capf('l112_writepath.txt')),
     'One output file, but <b>85 requests</b>. The task wrote the data once (<code>_task_tmp…</code>), then Hive “renamed” it three times through its staging folders and once into the partition. On S3 each rename is a <b>server-side copy</b> plus a delete. With one small file it is quick; with thousands of large files the commit can take longer than the query. A second run made 93 requests.'),
    ('Step 6 · Staging must stay on the table’s file system',
     code('sql', 'beeline', "SET hive.exec.stagingdir=file:///tmp/hstage;\nINSERT OVERWRITE TABLE orders_s3 PARTITION (order_date = '2026-10-08') SELECT …;", capf('l112_stage_err.txt')),
     'Moving staging off S3 to avoid the copies does not work: the final move must happen inside one file system. The real fixes are writers that commit without renames: EMR’s <b>S3-optimised committer</b> for its engines, the S3A <b>magic/staging committers</b> for Spark and MapReduce, or table formats such as <b>Iceberg</b>, which write files once and commit by swapping a metadata pointer (Lesson 11.3).'),
    ('Step 7 · Files added outside Hive stay invisible',
     code('sql', 'boto3, then beeline', "-- copy a partition object with an S3 tool\ns3.copy_object(..., Key='warehouse/orders_s3/order_date=2026-10-09/000000_0')\n\nSELECT COUNT(*) AS n FROM orders_s3 WHERE order_date = '2026-10-09';\nSHOW PARTITIONS orders_s3;\nMSCK REPAIR TABLE orders_s3;\nSELECT COUNT(*) AS n FROM orders_s3 WHERE order_date = '2026-10-09';", capf('l112_msck_before.txt') + '\n\n-- after MSCK REPAIR\n' + capf('l112_msck.txt')),
     'The object was in the bucket, but the metastore knew only eight partitions, so Hive answered <b>0</b> without an error. <code>MSCK REPAIR TABLE</code> listed the prefixes and added the partition: 1,662 rows. In the cloud, upstream jobs often drop files straight into buckets; either they register partitions (<code>ALTER TABLE … ADD PARTITION</code>), you run MSCK on a schedule, or, on Athena, partition projection computes partitions without listing.'),
    ('Step 8 · Reading from S3 versus local storage',
     code('sql', 'beeline, two runs each', "CREATE TABLE orders_loc STORED AS PARQUET AS SELECT * FROM orders_s3;   -- local copy, 14,950 rows\nSELECT city, SUM(amount) FROM orders_loc GROUP BY city;\nSELECT city, SUM(amount) FROM orders_s3  GROUP BY city;", capf('l112_timing.txt')),
     'Same answers. The S3 table took slightly longer and made 90 requests (45 HEAD, 45 GET) for nine small files; the local table made none. Our S3 server runs on the same machine, so each request takes about a millisecond. Real S3 requests take tens of milliseconds and are billed per thousand, which is why small files hurt more in the cloud than on HDFS. Treat the times as indicative.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('INSERT … PARTITION (order_date)', W), ('NoAuthWithAWSException', RD), ('add AWS keys to both containers', W), ('INSERT ok: 7 partitions', G)], size=7.4),
    term([('warehouse/orders_s3/             0', Y), ('…/order_date=2026-10-01/000000_0  23724', W), ('…/order_date=2026-10-07/000000_0  24025', W), ('objects: 8', G)], size=7.0),
    term([('PUT  _task_tmp…/-tmp.000000_0', W), ('PUT  -tmp.-ext-10000/000000_0', Y), ('PUT  -ext-10000/000000_0', Y), ('PUT  order_date=…/000000_0', Y), ('85 requests', RD)], size=7.2),
    term([('copy object to order_date=2026-10-09', W), ('COUNT(*) → 0', RD), ('MSCK REPAIR TABLE orders_s3', W), ('COUNT(*) → 1662', G)], size=7.4),
    term([('orders_loc  5.0–5.3 s   0 requests', G), ('orders_s3   5.9–6.4 s  90 requests', Y), ('same answers', G)], size=7.4),
]
def lay(hi):
    o = ''
    for k, (name, sub, x, y) in enumerate([('Hive + Tez', 'compute', 20, 34), ('Metastore', 'partitions', 20, 92), ('S3 bucket', 'objects', 230, 62)]):
        o += opbox(x, y, name, sub, 'acc' if k == hi else ['blue', 'amber', 'green'][k], 110, 30)
    o += arrow(132, 49, 228, 74, 'ink3', 1.4) + arrow(132, 107, 228, 82, 'ink3', 1.4)
    return o
B1 = [
    t(180, 22, 'Every process needs credentials', 9.4, bold=True) + lay(0) + cap('Tasks read and write objects directly.', 'In the cloud: an IAM role.', 'amber', y=132, h=44),
    t(180, 22, 'Folders are only key prefixes', 9.4, bold=True) + lay(2) + cap('Listing = paged HTTP requests.', '', 'blue', y=140, h=34),
    t(180, 22, 'Rename = copy + delete', 9.4, bold=True) + lay(2) + cap('Hive’s staging moves become copies.', 'Iceberg/committers avoid them.', 'amber', y=132, h=44),
    t(180, 22, 'The metastore decides what exists', 9.4, bold=True) + lay(1) + cap('New prefixes need ADD PARTITION or MSCK.', '', 'violet', y=140, h=34),
    t(180, 22, 'Requests cost time and money', 9.4, bold=True) + lay(2) + cap('Fewer, larger files; prune partitions.', '', 'green', y=140, h=34),
]
see_caps = ['The tasks had no credentials until we gave them keys.',
            'Eight objects, one of them an empty “folder” marker.',
            'One output file needed 85 requests.',
            'A new partition stayed invisible until MSCK REPAIR.',
            'Same answer from S3, more requests and time.']
behind_caps = ['Tez tasks open S3 connections of their own.',
               'S3 stores keys; “directories” are conventions.',
               'Each staging move is a server-side copy.',
               'Hive plans from metastore partitions, not from the bucket.',
               'Each file costs at least a HEAD and a GET.']
two = anim_two('Hive on object storage', 'Same SQL, different storage', 'Real lab outputs', 'What object storage does', see, B1, see_caps, behind_caps)

# ---- scenario 1: transient cluster
e1 = (t(180, 22, 'Nightly load, 40 minutes', 9.4, bold=True) + t(180, 56, '12 nodes running 24 hours', 8.4, 'ink2') + cap('Paying for idle machines.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Move data to the bucket', 9.4, bold=True) + t(180, 56, "LOCATION 's3://tiffingo-lake/…'", 8.2, 'ink', mono=True) + cap('Data outlives clusters.', '', 'green', y=150, h=34))
e3 = (t(180, 22, 'Move the catalogue out', 9.4, bold=True) + t(180, 56, 'Glue Data Catalog or managed RDS', 8.4, 'ink2') + cap('Metastore must survive too.', '', 'amber', y=150, h=34))
e4 = (t(180, 22, 'Create → run → delete', 9.4, bold=True) + t(180, 56, 'scheduler starts an EMR cluster per load', 8.2, 'ink2') + cap('Or EMR Serverless.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Analysts keep querying', 9.4, 'acc', bold=True) + t(180, 56, 'Athena / Trino on the same catalogue', 8.2, 'ink2') + cap('No cluster needed for reads.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'A cluster that exists only for the load',
              'The most common reason companies move Hive to the cloud. (Typical architecture.)',
              'Transient clusters', 'Data in object storage and a catalogue outside the cluster let a scheduler create a cluster per job and delete it afterwards', [e1, e2, e3, e4, e5],
              ['Idle cluster costs money.',
               'Tables point at the bucket.',
               'The metastore lives outside.',
               'One cluster per run.',
               'Reads go serverless.'],
              hid='scenario-transient')

# ---- scenario 2: slow commit with many small files
b1 = (t(180, 22, 'Query done, job still running', 9.4, bold=True) + t(180, 56, '20 minutes after the last task', 8.4, 'ink2') + cap('A classic S3 complaint.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Look at the output', 9.4, bold=True) + t(180, 56, '40,000 small files per run', 8.4, 'ink', mono=True) + cap('Each moved by copy + delete.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'Fewer, larger files', 9.4, bold=True) + t(180, 56, 'hive.merge.tezfiles, DISTRIBUTE BY', 8.2, 'ink', mono=True) + cap('Lesson 5.4.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Rename-free commits', 9.4, bold=True) + t(180, 56, 'EMR S3-optimised / S3A committers', 8.2, 'ink2') + cap('Write once, no copies.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Or Iceberg', 9.4, 'acc', bold=True) + t(180, 56, 'commit = swap one metadata pointer', 8.2, 'ink2') + cap('Lesson 11.3.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'The commit that took longer than the query',
              'What our 85-request partition overwrite becomes at scale. (Fixes typical.)',
              'S3 commits', 'Hive’s rename-based commit copies every output file on S3; fewer files, rename-free committers or Iceberg fix it', [b1, b2, b3, b4, b5],
              ['Tasks finish, job does not.',
               'Too many files to copy.',
               'Merge small files.',
               'Use a committer.',
               'Or use Iceberg.'],
              hid='scenario-commit')

# ---- scenario 3: migrating on-prem Hive 4 to a managed service
u1 = (t(180, 22, 'Move on-prem Hive to EMR', 9.4, bold=True) + t(180, 56, 'Hive 4.2.1 → EMR Hive 3.1.3', 8.4, 'ink', mono=True) + cap('A version step back.', '', 'amber', y=150, h=34))
u2 = (t(180, 22, 'Copy the data', 9.4, bold=True) + t(180, 56, 'distcp hdfs://… s3://…', 8.4, 'ink', mono=True) + cap('Validate counts per partition.', '', 'green', y=150, h=34))
u3 = (t(180, 22, 'Move the catalogue', 9.4, bold=True) + t(180, 56, 'metastore → Glue (or keep an RDS HMS)', 8.2, 'ink2') + cap('Rewrite every LOCATION.', '', 'blue', y=150, h=34))
u4 = (t(180, 22, 'Replace security', 9.4, bold=True) + t(180, 56, 'Ranger/Kerberos → IAM, Lake Formation', 8.2, 'ink2') + cap('Lesson 10.2 does not carry over.', '', 'amber', y=150, h=34))
u5 = (t(180, 22, 'Re-test the SQL', 9.4, 'acc', bold=True) + t(180, 56, 'Hive 4 syntax and Iceberg defaults', 8.2, 'ink2') + cap('Run the 11.1 interop test.', '', 'green', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'From on-premises Hive to a managed service',
              'A migration plan with the version facts from section 3. (Typical steps.)',
              'Cloud migration', 'Copy data, move or rebuild the catalogue, replace on-prem security with cloud IAM and re-test SQL against the managed Hive version', [u1, u2, u3, u4, u5],
              ['Managed Hive is 3.x.',
               'Copy and validate data.',
               'Rebuild the catalogue.',
               'New permission model.',
               'Test every query.'],
              hid='scenario-migrate')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Same SQL, different storage</h2>
  <p>Left: real outputs. Right: what object storage does underneath.</p>
''' + two + '''
  <p>Three live scenarios follow: a transient cluster, a slow commit, and a migration to a managed service.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Hive in the cloud at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'transient', 10, 'green', bold=True) + t(60, 58, 'EMR', 7.4, 'ink2'),
    '1. Clusters per job',
    'Schedulers create EMR or Dataproc clusters for nightly Hive loads and delete them after; data and catalogue persist.',
    ['Schedule', '*cluster', 'S3 tables']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'Glue', 12, 'blue', bold=True) + t(60, 58, 'catalogue', 7.4, 'ink2'),
    '2. One catalogue for many services',
    'Hive on EMR, Athena, Redshift Spectrum and Glue jobs share table definitions in the Glue Data Catalog.',
    ['Hive DDL', '*Glue', 'Athena SQL']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'lift', 11, 'violet', bold=True) + t(60, 58, '&amp; shift', 7.4, 'ink2'),
    '3. Lift-and-shift of on-prem Hive',
    'Companies copy HDFS data to buckets with DistCp and run the same HiveQL on Dataproc or HDInsight.',
    ['HDFS', '*DistCp', 'Bucket']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'lake', 12, 'acc', bold=True) + t(60, 58, 'landing', 7.4, 'ink2'),
    '4. Landing zones with partition repair',
    'Upstream systems drop daily files into prefixes; a job runs ADD PARTITION or MSCK so Hive and Athena see them.',
    ['Files land', '*MSCK', 'Queryable']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'FinOps', 10, 'acc', bold=True) + t(60, 58, 'requests', 7.4, 'ink2'),
    '5. Cost control',
    'Teams track request counts and small files per table, because object stores bill per request.',
    ['Many files', '*compact', 'Lower bill']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> external tables (<a href="../../02-hiveql/02-managed-vs-external-tables/">2.2</a>), MSCK (<a href="../../05-partitioning-and-bucketing/02-dynamic-partitions-and-msck/">5.2</a>), small files (<a href="../../05-partitioning-and-bucketing/04-partition-design-small-files-and-skew/">5.4</a>) and the metastore (<a href="../../10-administration-and-security/01-metastore-administration/">10.1</a>).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
