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
    module='10-administration-and-security', lesson='01-metastore-administration', n='10.1',
    module_label='Module 10 · Administration and security',
    title='Metastore administration',
    desc='Administer the Hive Metastore with real Hive 4.2.1 and PostgreSQL outputs: schematool -info, -validate and -upgradeSchema -dryRun, the metastore database tables (DBS, TBLS, SDS, PARTITIONS, TABLE_PARAMS, COLUMNS_V2, FUNCS), a warehouse-wide small-files report in SQL, backup with pg_dump and a tested restore, metastore settings seen from Hive, database properties, deployment modes and what happens when the metastore is down.',
    og_desc='Inside the Hive metastore: 84 PostgreSQL tables, a tested 1.2 MB backup, and what users see when it goes down. Real Hive 4.2.1 outputs.',
    minutes=35, level='Intermediate → Advanced',
    lead='Module 10 is about running Hive for others. It starts with the most important component: the <b>metastore</b>. We check its schema with <code>schematool</code>, read it with SQL, build a health report, <b>back it up and prove the restore</b>, and switch it off to see what users experience. <b>All outputs are real</b>, from Hive 4.2.1 with a PostgreSQL metastore.',
    chips=['Real schematool and SQL outputs', 'Tested backup and restore', 'Metastore outage seen live', 'Runs in your browser (Python)'],
)

MAIN = '''# A tiny model of the metastore's core tables
DBS = {1: "default", 2: "tiffingo"}
TBLS = [  # (tbl_id, db_id, name, type, sd_id)
    (10, 2, "orders", "EXTERNAL_TABLE", 100),
    (11, 2, "orders_tx", "MANAGED_TABLE", 101),
    (12, 2, "v_gold_orders", "VIRTUAL_VIEW", 102),
]
SDS = {100: "file:/opt/hive/data/warehouse/tiffingo.db/orders",
       101: "file:/opt/hive/data/warehouse/tiffingo.db/orders_tx",
       102: None}                                   # views have no location

for tbl_id, db_id, name, ttype, sd in TBLS:
    print(f"{DBS[db_id]}.{name:14} {ttype:15} {SDS[sd]}")
'''
RUN = dict(
    heading='Run the code: the metastore as tables',
    intro='<p>These programs model the metastore’s tables and the reports administrators build on them, with numbers from the lab. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    (10, 2, "orders", "EXTERNAL_TABLE", 100),', 'A TBLS row points to its database (DBS) and its storage descriptor (SDS), like the real join in Step 4.'),
        ('       102: None}                                   # views have no location', 'A view is metadata only: its storage descriptor has no data location.'),
    ],
    tasks=[
        dict(label='1 · Join the tables', hint='Press <b>Run</b>. The same join as Step 4: TBLS → DBS and TBLS → SDS.', code=None),
        dict(label='2 · Predict first: files per partition', hint='<b>Predict first:</b> 2,000 partitions, 1.6 MB in total. Average KB per file?',
             code='''files, mb = 2000, 1.6
print(round(mb * 1024 / files, 1), "KB per file")
'''),
        dict(label='3 · Count objects by type', hint='Reproduce the GROUP BY on TBL_TYPE from Step 3 with the real counts.',
             code='''types = ["EXTERNAL_TABLE"] * 61 + ["MANAGED_TABLE"] * 10 + ["VIRTUAL_VIEW"] * 2 + ["MATERIALIZED_VIEW"]
from collections import Counter
for t, n in Counter(types).most_common():
    print(f"{t:18} {n}")
print("total:", len(types))
'''),
        dict(label='4 · Backup schedule', hint='Choose dumps so that at most 1 hour of metadata changes can be lost.',
             code='''rpo_minutes = 60
dump_minutes = 1                     # the lab dump took seconds; big metastores take longer
print("dump every", rpo_minutes - dump_minutes, "minutes, keep 7 days")
'''),
        dict(label='5 · Spot the error', hint='This check says the restore is fine because the dump file exists. Fix it.', expect='error',
             code='''dump_exists, restore_validated = True, False
backup_ok = dump_exists                       # bug
assert backup_ok == restore_validated, "a backup is only proven by a validated restore"
print("backup OK")
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: columns, table properties and functions',
    intro='<p>More SQL against the metastore database. <b>Outputs are real</b> (PostgreSQL, <code>metastore_db</code>).</p>',
    items=[
        dict(title='1 · Columns of a table', cmd='SELECT c."COLUMN_NAME", c."TYPE_NAME", c."INTEGER_IDX"\nFROM "TBLS" t JOIN "SDS" s ON t."SD_ID" = s."SD_ID"\nJOIN "COLUMNS_V2" c ON c."CD_ID" = s."CD_ID"\nWHERE t."TBL_NAME" = \'customers\' ORDER BY 3;', file='psql · metastore_db',
             output=capf('l101_cols.txt'),
             note='Columns hang off a column descriptor (CD_ID) shared through the storage descriptor; INTEGER_IDX is the column position.'),
        dict(title='2 · Table properties', cmd='SELECT p."PARAM_KEY", p."PARAM_VALUE"\nFROM "TBLS" t JOIN "TABLE_PARAMS" p ON p."TBL_ID" = t."TBL_ID"\nWHERE t."TBL_NAME" = \'orders_tx\' AND p."PARAM_KEY" NOT LIKE \'%COLUMN_STATS%\' ORDER BY 1;', file='psql · metastore_db',
             output=capf('l101_params.txt'),
             note='Everything SHOW TBLPROPERTIES returns: statistics (numRows 5,000,000, numFiles 5) and flags such as transactional=true.'),
        dict(title='3 · Permanent functions (from Lesson 9.1)', cmd='SELECT f."FUNC_NAME", f."CLASS_NAME", f."FUNC_TYPE", r."RESOURCE_URI"\nFROM "FUNCS" f JOIN "FUNC_RU" r ON f."FUNC_ID" = r."FUNC_ID" ORDER BY 1;', file='psql · metastore_db',
             output=capf('l91_funcs_db.txt'),
             note='Function inventories, owners per database and table counts per team are typical platform reports built this way.'),
    ],
)

TRACE = dict(
    heading='A backup you can trust',
    intro='<p>Follow the steps from Step 6 and what each one proves.</p>',
    code='''steps = []
steps.append(("pg_dump", "1,226,478 bytes written"))
steps.append(("pg_restore into a new DB", "restored"))
steps.append(("schematool -validate", "SUCCESS"))
steps.append(("count tables / partitions", "74 / 2100 as in production"))
proven = all(result for _, result in steps)
print("backup proven:", proven)
''',
    notes={2: 'Dump :: Only proves that a file exists.', 4: 'Validate :: Proves the schema in the copy is complete and consistent.', 5: 'Compare :: Proves the content matches.'},
)

WORKED_INTRO = 'Three metastore tasks from real platform teams.'
EXAMPLES = [
    dict(level='b', tag='Operations · checks', title='Daily metastore checklist',
         problem='<p>Write the five checks an operator runs each morning.</p>',
         inp='a production HMS on PostgreSQL',
         approach=['Service up and answering.', 'Database healthy and backed up.', 'Metadata growth under control.'],
         code='''checks = ["HMS port 9083 answers on every instance",
          "last pg_dump < 24 h old, last restore drill < 90 days",
          "schematool -info: schema version as expected",
          "partitions per table below the agreed limit",
          "metastore DB size and connection count trend"]
for c in checks:
    print("[ ]", c)
''', notes={3: 'Version :: Catches half-finished upgrades.'},
         tryit='Our lab: schema 4.2.0, validation SUCCESS, largest table 2,000 partitions, database 21 MB.'),
    dict(level='i', tag='Platform · reports', title='Over-partitioned tables',
         problem='<p>From partition counts and sizes, list tables whose average partition is under 1 MB.</p>',
         inp='orders_by_cust 2,000 partitions 1.6 MB · orders_by_day 30 partitions 0.4 MB · a 10 GB table with 365 partitions (illustrative)',
         approach=['Average partition size = total / partitions.', 'Flag under 1 MB.', 'Report owners.'],
         code='''tables = {"orders_by_cust": (2000, 1.6), "orders_by_day": (30, 0.4), "sales_daily": (365, 10240)}
for t, (parts, mb) in tables.items():
    avg = mb / parts
    print(f"{t:15} {avg:8.3f} MB/partition", "<- too small" if avg < 1 else "")
''', notes={3: 'Threshold :: Lab tables are tiny; in production a common target is hundreds of MB per partition.'},
         tryit='The lab tables are small by design; the report logic is what matters.'),
    dict(level='a', tag='Architecture · HA', title='Size an HA metastore',
         problem='<p>300 users and 40 Spark jobs hit the metastore. Plan instances and the database.</p>',
         inp='illustrative load: 2,000 metastore calls per second at peak',
         approach=['Several stateless HMS instances behind hive.metastore.uris.', 'One replicated RDBMS.', 'Capacity per instance from measurement.'],
         code='''peak_calls, per_instance = 2000, 600       # measure per_instance in a load test
import math
n = math.ceil(peak_calls / per_instance) + 1   # +1 for failure
print("HMS instances:", n)
print("hive.metastore.uris=" + ",".join(f"thrift://hms{i}:9083" for i in range(1, n + 1)))
''', notes={3: 'N+1 :: One instance can fail without overloading the rest.'},
         tryit='Clients try the URIs in turn; in Step 8 the single URI failing meant no sessions at all.'),
]

QUIZ = mix([
    dict(q='Beginner: What does the Hive metastore store?', options=['The data rows', 'Metadata: databases, tables, columns, partitions, locations, statistics', 'Query results', 'Only passwords'], answer=1,
         why='The data files are stored separately.'),
    dict(q='Beginner: Which tool shows the metastore schema version?', options=['hive --version', 'schematool -info', 'beeline -v', 'pg_dump'], answer=1,
         why='Our lab: schema 4.2.0.'),
    dict(q='Beginner: What did users see with the metastore stopped?', options=['Slower queries', 'Sessions could not open: “Could not connect to meta store”', 'Only writes failed', 'Nothing'], answer=1,
         why='Every query needs table metadata.'),
    dict(q='Intermediate: Which metastore table holds table locations?', options=['TBLS', 'SDS (storage descriptors)', 'DBS', 'FUNCS'], answer=1,
         why='TBLS points to SDS for location and formats.'),
    dict(q='Intermediate: What does schematool -upgradeSchema -dryRun do?', options=['Upgrades immediately', 'Lists the upgrade scripts without running them', 'Deletes the schema', 'Backs up'], answer=1,
         why='“No schema upgrade required from version 4.2.0” in our lab.'),
    dict(q='Intermediate: How did we back up the metastore?', options=['hdfs dfs -get', 'pg_dump of the metastore database', 'EXPORT TABLE', 'Copying the warehouse'], answer=1,
         why='A 1.2 MB custom-format dump, restored and validated.'),
    dict(q='Advanced: Which numbers did the small-files report use?', options=['HDFS listings', 'numFiles and totalSize in PARTITION_PARAMS', 'Tez counters', 'Query logs'], answer=1,
         why='Statistics stored in the metastore.'),
    dict(q='Advanced: Why does the dump not protect your data?', options=['It is compressed', 'It contains only metadata; data files need separate protection', 'It is incremental', 'It expires'], answer=1,
         why='Use HDFS snapshots or object-store versioning for data.'),
])

REVISION = [
    '<b>HMS</b> = service (Thrift :9083) + RDBMS (PostgreSQL/MySQL in production). Clients: <code>hive.metastore.uris</code>.',
    '<b>schematool</b>: <code>-info</code>, <code>-validate</code>, <code>-initSchema</code>, <code>-upgradeSchema [-dryRun]</code>. Lab: 4.2.0, SUCCESS, no upgrade needed.',
    'Core tables: <code>DBS</code>, <code>TBLS</code>, <code>SDS</code>, <code>PARTITIONS</code>, <code>COLUMNS_V2</code>, <code>TABLE_PARAMS</code>, <code>PARTITION_PARAMS</code>, <code>FUNCS</code>.',
    'Read with SQL for reports (small files, partition counts, owners); change only through HiveQL/HMS API.',
    '<b>Backup</b>: pg_dump/mysqldump; prove with restore + <code>schematool -validate</code>. Metadata only.',
    'Modes: embedded (tests), local, remote (production), remote + HA; managed catalogues in the cloud.',
    'Metastore down → no sessions. Run ≥2 HMS instances; replicate the database.',
    'Database properties (<code>SET DBPROPERTIES</code>) record owners and classifications.',
]
FAQ = [
    ('Which database should back the metastore?', 'MySQL/MariaDB and PostgreSQL are the most common; Oracle and SQL Server are supported. Derby is only for tests because it allows one connection at a time. Choose what your team can operate, back up and replicate well.'),
    ('Can Spark use the same metastore?', 'Yes. Spark SQL with Hive support connects to HMS through hive.metastore.uris (or spark.sql.hive.metastore.* settings), so tables created by Hive appear in Spark and vice versa. Version compatibility between Spark’s Hive client and the HMS matters during upgrades.'),
    ('What is metastore.schema.verification?', 'A metastore setting (true by default) that makes HMS refuse to start or work against a schema of a different version, instead of silently altering it. Upgrades are then explicit, with schematool.'),
    ('How do I clean up old partitions automatically?', 'Hive 4 supports the table property <code>partition.retention.period</code> (with <code>discover.partitions</code>) handled by metastore housekeeping threads, or you run scheduled ALTER TABLE … DROP PARTITION jobs. Test retention on a copy first: dropping partitions of managed tables deletes data.'),
    ('Does the metastore store ACID transaction state?', 'Yes: open, committed and aborted transactions, write IDs and locks (Module 7) live in metastore tables such as TXNS and HIVE_LOCKS. That is why restoring an old metastore under live ACID tables needs great care.'),
]

PRACTICE_INTRO = 'Programs for metastore reports and checks, with the SQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Objects per type', stmt='Sum the object counts from TBLS.', inp='61, 10, 2, 1',
         code='''print(61 + 10 + 2 + 1)
''', explain='74 rows in TBLS, the same count found in the restored copy.'),
    dict(level='easy', title='Average file size', stmt='Average KB per file for orders_by_day.', inp='30 files, 0.4 MB',
         code='''print(round(0.4 * 1024 / 30, 1))
''', explain='About 13.7 KB (the report rounds MB first: 13.3).'),
    dict(level='easy', title='Version check', stmt='Is an upgrade needed?', inp='distribution 4.2.0, schema 4.2.0',
         code='''print("no upgrade needed" if "4.2.0" == "4.2.0" else "run schematool -upgradeSchema")
''', explain='Matches “No schema upgrade required from version 4.2.0”.'),
    dict(level='medium', title='Build a location', stmt='Compose the default location of a managed table.', inp='warehouse dir, database, table',
         code='''wh, db, tbl = "file:/opt/hive/data/warehouse", "tiffingo", "orders_tx"
print(f"{wh}/{db}.db/{tbl}")
''', explain='Exactly the LOCATION of orders_tx in SDS.'),
    dict(level='medium', title='Flag large partition counts', stmt='List tables over 1,000 partitions.', inp='counts from Step 4',
         code='''counts = {"orders_by_cust": 2000, "orders_by_day": 30, "orders_dyn": 30, "cust_by_ref": 9}
print([t for t, n in counts.items() if n > 1000])
''', explain='SQL: GROUP BY TBL_NAME HAVING COUNT(PART_ID) > 1000 on PARTITIONS joined to TBLS.'),
    dict(level='medium', title='Dump file name', stmt='Generate dated dump file names for a week.', inp='start 2026-10-29',
         code='''from datetime import date, timedelta
d = date(2026, 10, 29)
print([f"hms_{(d + timedelta(days=i)).isoformat()}.dump" for i in range(3)])
''', explain='pg_dump -Fc metastore_db -f /backups/hms_YYYY-MM-DD.dump, kept for a retention period.'),
    dict(level='business', title='Cost of an outage', stmt='The metastore is down for 20 minutes during business hours with 300 active users. Lost user-minutes?', inp='illustrative',
         code='''print(300 * 20, "user-minutes")
''', explain='6,000 user-minutes: a strong argument for a second HMS instance.'),
    dict(level='business', title='Backup storage', stmt='Daily dumps of 1.2 MB kept for 30 days, versus a production metastore of 20 GB.', inp='lab and illustrative sizes',
         code='''print("lab:", round(1.2 * 30, 1), "MB · production:", 20 * 30, "GB")
''', explain='Even large metastores are small compared with the data; keep generous retention.'),
]

SCN_INTRO = 'Metastore questions are common in platform and senior data engineering interviews.'
SCENARIOS = (
    scn('Any company · Hive', 'Fresher', '“What is the Hive metastore?”',
        'Explain the metastore and why it matters.',
        'do you separate metadata from data?',
        '<p>The metastore stores Hive’s metadata (databases, tables, columns, partitions, locations, formats, statistics) in a relational database and serves it through a Thrift service. Data lives in HDFS or object storage. Every query needs the metastore to know what a table is and where its files are; Spark and Trino often use the same metastore.</p>', 'Saying the metastore stores the data.') +
    scn('Data platform', 'Mid-level', 'Upgrade plan',
        'You must upgrade Hive 3 to Hive 4. What happens to the metastore?',
        'do you know schematool and backups?',
        '''<ol>
          <li>Back up the metastore database and test the restore.</li>
          <li>On a copy: schematool -info, -upgradeSchema -dryRun, then the upgrade and -validate.</li>
          <li>Test Hive and other engines against the upgraded copy, then repeat in production.</li>
        </ol>''', 'Upgrading binaries and hoping the schema follows.') +
    scn('Operations', 'Mid-level', 'All queries fail at once',
        'Every user gets “Could not connect to meta store using any of the URIs provided”.',
        'can you localise the failure?',
        '''<ul>
          <li>Check the HMS processes and port 9083 on each URI; check HMS logs for database errors.</li>
          <li>Check the backing database (up, connections, disk).</li>
          <li>Restore service, then add a second HMS instance and monitoring.</li>
        </ul>''', 'Restarting HiveServer2 repeatedly.') +
    scn('Architecture', 'Senior', 'One catalogue, many engines',
        'Design the metastore for Hive, Spark and Trino serving 500 users.',
        'can you design for availability and governance?',
        '''<ul>
          <li>Multiple HMS instances, replicated RDBMS, automated dumps with restore drills.</li>
          <li>Limits on partition counts; housekeeping; monitoring of size and latency.</li>
          <li>Ownership and classification properties; or a managed catalogue in the cloud.</li>
        </ul>''', 'One HMS on an engineer’s VM.')
)
