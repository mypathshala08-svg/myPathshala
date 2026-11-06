import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return re.sub(r'; Query ID[^\n]*', '', open(CAP + n).read().rstrip())

def opbox(x, y, label, sub='', tone='card', w=128, h=26):
    o = box(x, y, w, h, tone) + t(x + w / 2, y + (11 if sub else 16), label, 7.2, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 21, sub, 6.4, 'ink2', mono=True)
    return o

# ---------------------------------------------------------------- story
sc = (opbox(14, 22, 'HiveServer2', 'SQL', 'blue', 120, 30) + opbox(14, 62, 'Spark', 'tables', 'blue', 120, 30) + opbox(14, 102, 'Trino', 'tables', 'blue', 120, 30) +
      arrow(136, 37, 214, 72, 'acc', 1.6) + arrow(136, 77, 214, 77, 'acc', 1.6) + arrow(136, 117, 214, 82, 'acc', 1.6) +
      box(218, 46, 150, 62, 'violet') + t(293, 70, 'Metastore', 9, bold=True) + t(293, 88, 'thrift :9083', 7.4, 'ink2', mono=True) +
      arrow(372, 77, 410, 77, 'acc', 2) +
      box(414, 12, 216, 128, 'green') + t(522, 30, 'PostgreSQL: metastore_db', 8.6, 'green', bold=True) +
      ''.join(t(428, 52 + k * 16, s, 7.2, 'ink', anchor='start', mono=True) for k, s in enumerate(['84 tables: DBS, TBLS, SDS,', 'PARTITIONS, TABLE_PARAMS …', '74 Hive tables, 2,100 partitions', 'dump: 1.2 MB, restore tested', 'schema version 4.2.0'])))
scene_svg = scene('HiveServer2, Spark and Trino all ask the metastore service where tables are; the metastore keeps everything in a PostgreSQL database of 84 tables, which the lab backed up and restored.', sc,
                  'Lose the data files and you lose a table; lose the <tspan font-weight="700" class="s-acc">metastore</tspan> and you lose all of them.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Who looks after the metastore?”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s platform team is preparing a Hive upgrade. The checklist has one scary line: “Back up the metastore”. Kabir realises nobody on the team has ever looked inside it.</p>

{scene_svg}

K> Sir, the metastore is just a service, right? If it breaks, we restart it.
A> The <b>service</b> you can restart. The <b>database</b> behind it is different: every table name, column, partition, location, statistic and function of every database lives there. Hive, Spark and Trino all depend on it. The data files without the metastore are just folders.
R> So administering it means…?
A> Knowing its <b>schema version</b> (schematool), being able to <b>read</b> it with SQL for health checks, <b>backing it up and proving the restore works</b>, and knowing what users see when it is down. We will do all four on our lab’s PostgreSQL metastore. All outputs are real, from Hive 4.2.1.
  </div>
</section>
'''

lv = '''
LEVELS> Metastore administration at three levels
L1> The library catalogue
      <ul>
        <li>The data files are the books; the metastore is the catalogue that says what each book is and on which shelf it stands.</li>
        <li>Without the catalogue the books still exist, but nobody can find them by name.</li>
        <li>Administrators keep the catalogue correct, backed up and available.</li>
      </ul>
L2> The parts you administer
      <ul>
        <li><b>The service</b>: Hive Metastore (HMS), Thrift on port 9083; clients find it through <code>hive.metastore.uris</code>.</li>
        <li><b>The database</b>: MySQL, PostgreSQL, Oracle or SQL Server (Derby only for tests). Tables such as <code>DBS</code>, <code>TBLS</code>, <code>SDS</code>, <code>PARTITIONS</code>, <code>TABLE_PARAMS</code>, <code>FUNCS</code>.</li>
        <li><b>schematool</b>: <code>-info</code>, <code>-validate</code>, <code>-initSchema</code>, <code>-upgradeSchema [-dryRun]</code>.</li>
        <li><b>Backups</b>: the database’s own tools (pg_dump, mysqldump), taken before every upgrade and regularly.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>The Hive 4.2.1 image reported distribution and schema version <b>4.2.0</b>; <code>-upgradeSchema -dryRun</code>: “No schema upgrade required”.</li>
        <li>84 metastore tables held 74 Hive objects and 2,100 partitions; a SQL health check found <code>orders_by_cust</code> with 2,000 files of 0.8 KB on average.</li>
        <li>A 1.2 MB pg_dump restored into a new database and passed <code>-validate</code>. With the metastore stopped, HiveServer2 could not even open a session.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Metastore administration</h2>
''' + def_block(
    'The <b>Hive Metastore</b> (HMS) is the service that stores and serves metadata for Hive and other engines: databases, tables, columns, partitions, storage descriptors (location, format, SerDe), statistics, constraints, functions, transactions and locks. It persists this metadata in a relational database through JDO/DataNucleus. <b>Metastore administration</b> covers creating and upgrading that database schema with <code>schematool</code>, configuring clients (<code>hive.metastore.uris</code>) and the warehouse locations, running housekeeping (compaction initiator, statistics, partition management), monitoring and scaling the service, and backing up and restoring the database.',
    'The metastore is Hive’s catalogue: a service plus a normal relational database that remembers every table and partition. Administering it means keeping its schema at the right version, checking its health, backing it up and keeping it running, because every Hive query and many other engines depend on it.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('HMS', 'Hive Metastore service (Thrift, port 9083).'),
    ('Backing database', 'The RDBMS that stores the metadata (PostgreSQL in our lab).'),
    ('schematool', 'Hive’s tool to create, upgrade and validate that schema.'),
    ('DBS / TBLS / SDS', 'Metastore tables for databases, tables and storage descriptors.'),
    ('TABLE_PARAMS', 'Key/value properties: numRows, totalSize, transactional …'),
    ('Warehouse dir', 'Default location of managed tables.'),
    ('Remote metastore', 'HMS as a separate service shared by several clients.'),
    ('Embedded metastore', 'HMS inside the client process; tests only.'),
]) + '''

  <h3>schematool commands</h3>
''' + table(['Command', 'Does', 'When'], [
    ['<code>schematool -dbType postgres -info</code>', 'Shows connection, Hive version and schema version', 'Any time; first step of every upgrade'],
    ['<code>-validate</code>', 'Checks version, sequences, tables, locations, NULLs', 'After upgrades and restores'],
    ['<code>-initSchema</code>', 'Creates an empty metastore schema', 'New installation'],
    ['<code>-upgradeSchema [-dryRun]</code>', 'Runs (or lists) the upgrade scripts', 'After installing a new Hive version'],
    ['<code>-initOrUpgradeSchema</code>', 'Init if empty, else upgrade', 'Automated deployments'],
    ['<code>-createCatalog / -moveTable</code>', 'Catalog management', 'Multi-catalog setups'],
], minw=700) + lv + '''
EXAM> “What is stored in the Hive metastore and how do you back it up?” Databases, tables, columns, partitions, locations, formats, statistics, functions, transactions and locks, in a relational database (MySQL/PostgreSQL in production). Back it up with the database’s tools (pg_dump, mysqldump), always before upgrades, and test restores with schematool -validate.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Metastore deployment modes</h2>
''' + table(['Mode', 'How', 'Use'], [
    ['Embedded', 'HMS and Derby inside the client JVM', 'Unit tests only: one user at a time'],
    ['Local', 'HMS inside HiveServer2, talks to an external RDBMS', 'Small setups'],
    ['Remote (our lab)', 'Separate HMS service(s) on 9083; clients use <code>hive.metastore.uris</code>', 'Production; shared by Hive, Spark, Trino, Impala'],
    ['Remote + HA', 'Several HMS instances listed in <code>hive.metastore.uris</code>, one shared RDBMS (itself replicated)', 'Large platforms'],
    ['Managed', 'AWS Glue Data Catalog, Dataproc Metastore, Azure-managed HMS', 'Cloud (Lesson 11.2)'],
], minw=700) + '''
WARN> Never edit metastore tables by hand on a running system except in a documented emergency, with a backup. Use HiveQL (ALTER TABLE, MSCK REPAIR) or the HMS API so that caches, events and other engines stay consistent. Reading them with SQL for reports and health checks is fine.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>A metastore health check, a backup and an outage</h2>
  <p>All outputs are real: schematool ran in the metastore container, SQL in the PostgreSQL container (<code>metastore_db</code>), HiveQL in Beeline.</p>
''' + stepper([
    ('Step 1 · Which schema version?',
     code('bash', 'metastore container', "schematool -dbType postgres -info \\\n  -url jdbc:postgresql://postgres:5432/metastore_db -driver org.postgresql.Driver \\\n  -userName hive -passWord ********", capf('l101_info.txt')),
     'The schema is at <b>4.2.0</b>, and so is the “distribution version” this tool reports, even though the image is Hive 4.2.1: patch releases usually do not change the metastore schema. Always run <code>-info</code> before and after an upgrade.'),
    ('Step 2 · Validate, and preview an upgrade',
     code('bash', 'metastore container', "schematool -dbType postgres … -validate\nschematool -dbType postgres … -upgradeSchema -dryRun", capf('l101_validate.txt') + '\n\n' + capf('l101_dryrun.txt')),
     '<code>-validate</code> checks the version row, internal sequences, the presence of every expected table, the locations, and columns that must not be NULL. <code>-dryRun</code> lists the SQL upgrade scripts without running them: here none were needed. On a real upgrade you would read those scripts, back up, then run without <code>-dryRun</code>.'),
    ('Step 3 · Inside the metastore database',
     code('sql', 'psql · metastore_db', "SELECT COUNT(*) AS metastore_tables FROM information_schema.tables WHERE table_schema = 'public';\nSELECT \"DB_ID\", \"NAME\", \"DB_LOCATION_URI\", \"DB_MANAGED_LOCATION_URI\", \"OWNER_NAME\" FROM \"DBS\";\nSELECT \"TBL_TYPE\", COUNT(*) FROM \"TBLS\" GROUP BY 1 ORDER BY 2 DESC;", capf('l101_count.txt') + '\n\n' + capf('l101_dbs.txt') + '\n\n' + capf('l101_types.txt')),
     'An ordinary PostgreSQL schema of <b>84 tables</b>. <code>DBS</code> has our two databases with their locations; <code>TBLS</code> holds 74 objects from this course: 61 external tables, 10 managed (transactional) tables, 2 views and 1 materialized view. Column names are upper case and quoted, a DataNucleus convention.'),
    ('Step 4 · Where a table lives',
     code('sql', 'psql · metastore_db', "SELECT t.\"TBL_NAME\", t.\"TBL_TYPE\", s.\"LOCATION\", s.\"INPUT_FORMAT\"\nFROM \"TBLS\" t JOIN \"SDS\" s ON t.\"SD_ID\" = s.\"SD_ID\" JOIN \"DBS\" d ON t.\"DB_ID\" = d.\"DB_ID\"\nWHERE d.\"NAME\" = 'tiffingo' AND t.\"TBL_NAME\" IN ('orders', 'orders_by_day', 'orders_tx');\n\nSELECT t.\"TBL_NAME\", COUNT(p.\"PART_ID\") AS partitions\nFROM \"TBLS\" t JOIN \"PARTITIONS\" p ON p.\"TBL_ID\" = t.\"TBL_ID\" GROUP BY 1 ORDER BY 2 DESC LIMIT 5;", capf('l101_tbls.txt') + '\n\n' + capf('l101_parts.txt')),
     'A table row points to a <b>storage descriptor</b> (<code>SDS</code>) with its location, input format and SerDe; each partition has its own storage descriptor too. The partition count per table is a key health number: <code>orders_by_cust</code>, the over-partitioned example from Lesson 5.4, has <b>2,000</b> partitions for 50,000 rows.'),
    ('Step 5 · A small-files report straight from the metastore',
     code('sql', 'psql · metastore_db', "WITH f AS (\n  SELECT t.\"TBL_NAME\" AS tbl, pp.\"PARAM_KEY\" AS k, pp.\"PARAM_VALUE\"::bigint AS v\n  FROM \"TBLS\" t JOIN \"PARTITIONS\" p ON p.\"TBL_ID\" = t.\"TBL_ID\"\n  JOIN \"PARTITION_PARAMS\" pp ON pp.\"PART_ID\" = p.\"PART_ID\"\n  WHERE pp.\"PARAM_KEY\" IN ('numFiles', 'totalSize'))\nSELECT tbl, SUM(v) FILTER (WHERE k = 'numFiles') AS files,\n       ROUND(SUM(v) FILTER (WHERE k = 'totalSize') / 1024.0 / 1024, 1) AS mb,\n       ROUND(SUM(v) FILTER (WHERE k = 'totalSize') / 1024.0 / NULLIF(SUM(v) FILTER (WHERE k = 'numFiles'), 0), 1) AS kb_per_file\nFROM f GROUP BY tbl ORDER BY files DESC LIMIT 5;", capf('l101_health.txt')),
     'Statistics stored per partition (<code>numFiles</code>, <code>totalSize</code>) let you scan the whole warehouse for small files <b>without touching HDFS</b>. <code>orders_by_cust</code>: 2,000 files of <b>0.8 KB</b> each. Platform teams run such reports nightly; remember that the numbers are only as fresh as the statistics (Lesson 8.2).'),
    ('Step 6 · Back up, and prove the restore',
     code('bash', 'postgres + metastore containers', "pg_dump -U hive -Fc metastore_db -f /tmp/hms_2026-10-29.dump\ncreatedb -U hive metastore_restore_test\npg_restore -U hive -d metastore_restore_test /tmp/hms_2026-10-29.dump\nschematool -dbType postgres -url jdbc:postgresql://postgres:5432/metastore_restore_test … -validate", capf('l101_backup.txt')),
     'The whole lab catalogue is a <b>1.2 MB</b> dump. Restored into a fresh database, it passed schematool validation and contained the same 74 tables and 2,100 partitions. A backup you have never restored is only a hope. Note that the dump contains <b>metadata only</b>: data files need their own protection (HDFS snapshots, object-store versioning).'),
    ('Step 7 · The metastore seen from Hive',
     code('sql', 'Beeline', "SET hive.metastore.uris;\nSET hive.metastore.warehouse.dir;\nSET hive.metastore.warehouse.external.dir;\nSET metastore.schema.verification;\nDESCRIBE DATABASE EXTENDED tiffingo;\nALTER DATABASE tiffingo SET DBPROPERTIES ('owner_team' = 'data-platform', 'pii' = 'yes');\nDESCRIBE DATABASE EXTENDED tiffingo;      -- selected columns", capf('l101_hiveside_clean.txt')),
     'HiveServer2 reaches the metastore at <code>thrift://metastore:9083</code>; managed tables go under <code>/opt/hive/data/warehouse</code>. Settings that live only in the metastore’s own configuration (<code>metastore.schema.verification</code>) show as undefined in a Hive session. Database properties are a cheap way to record ownership and data classification where every engine can read them.'),
    ('Step 8 · What users see when the metastore is down',
     code('bash', 'lab', "docker stop metastore\n-- Beeline: connect and run SELECT COUNT(*) FROM customers;\ndocker start metastore      -- the same query works again after ~25 s", capf('l101_down_clean.txt')),
     'With the metastore stopped, HiveServer2 could not even <b>open a session</b>: every query, by every user, failed with “Could not connect to meta store using any of the URIs provided”. After a restart everything worked again without touching HiveServer2. In production, run at least two metastore instances behind <code>hive.metastore.uris</code> and keep the database highly available.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('$ schematool -dbType postgres -info', W), ('Hive distribution version:  4.2.0', G), ('Metastore schema version:   4.2.0', G), ('$ schematool … -validate', W), ('Done with metastore validation: [SUCCESS]', G)], size=7.2),
    term([('metastore_tables: 84', G), ('EXTERNAL_TABLE     61', W), ('MANAGED_TABLE      10', W), ('VIRTUAL_VIEW        2', W), ('MATERIALIZED_VIEW   1', W)], size=7.6),
    term([('tbl             files   mb   kb_per_file', W), ('orders_by_cust   2000  1.6         0.8', RD), ('orders_by_day      30  0.4        13.3', W), ('orders_dyn         30  0.4        13.3', W)], size=7.4),
    term([('$ pg_dump -Fc metastore_db', W), ('1226478 bytes', G), ('$ pg_restore … metastore_restore_test', W), ('[SUCCESS]', G), ('74 tables, 2100 partitions', G)], size=7.4),
    term([('$ docker stop metastore', W), ('Failed to open new session: …', RD), ('Could not connect to meta store', RD), ('  using any of the URIs provided.', RD), ('$ docker start metastore  → works', G)], size=7.2),
]
def chain(hi):
    names = [('Engines', 'Hive · Spark · Trino', 'blue'), ('HMS', 'thrift :9083', 'violet'), ('RDBMS', 'metastore_db', 'green'), ('Files', 'warehouse', 'card')]
    o = ''
    for k, (a, b, tone) in enumerate(names):
        o += opbox(10 + k * 88, 54, a, b, 'acc' if k == hi else tone, 80, 30)
        if k:
            o += arrow(10 + k * 88 - 7, 69, 10 + k * 88 - 1, 69, 'ink3', 1.6)
    return o
B1 = [
    t(180, 22, 'schematool talks to the database directly', 9.4, bold=True) + chain(2) + cap('Version row, scripts, validation.', '', 'green', y=140, h=34),
    t(180, 22, 'Metadata is ordinary relational data', 9.4, bold=True) + chain(2) + t(180, 112, 'DBS → TBLS → SDS → PARTITIONS', 8.2, 'ink', mono=True) + cap('Readable with SQL for reports.', '', 'blue', y=140, h=34),
    t(180, 22, 'Health checks without touching files', 9.4, bold=True) + chain(2) + t(180, 112, 'numFiles / totalSize per partition', 8.2, 'ink', mono=True) + cap('Only as fresh as the statistics.', '', 'amber', y=140, h=34),
    t(180, 22, 'Backups protect the catalogue', 9.4, bold=True) + chain(2) + t(180, 112, 'dump + restore + validate', 8.2, 'green', mono=True) + cap('Data files need separate protection.', '', 'green', y=140, h=34),
    t(180, 22, 'No metastore, no Hive', 9.4, bold=True) + chain(1) + cap('Run several HMS instances; keep the RDBMS HA.', '', 'amber', y=140, h=34),
]
see_caps = ['schematool reported schema 4.2.0 and a valid metastore.',
            'The metastore database: 84 tables describing 74 Hive objects.',
            'A SQL report found 2,000 tiny files in one table.',
            'A 1.2 MB dump restored and validated.',
            'With the metastore stopped, no session could open.']
behind_caps = ['schematool reads and writes the schema version in the backing database.',
               'Tables, storage descriptors and partitions are linked rows.',
               'Statistics stored per partition give a warehouse-wide view.',
               'The dump holds all metadata, not the data files.',
               'Every engine needs the HMS to resolve table names.']
two = anim_two('Metastore', 'The catalogue behind every table', 'Real lab outputs', 'Where the metadata lives', see, B1, see_caps, behind_caps)

# ---- scenario 1: upgrade
u1 = (t(180, 22, 'Upgrade Hive 3.1 → 4.x', 9.4, bold=True) + t(180, 56, 'metastore schema must be upgraded too', 8.4, 'ink2') + cap('Plan it like a database migration.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, '1 · Back up and restore-test', 9.4, bold=True) + t(180, 56, 'pg_dump / mysqldump → restore to a copy', 8.2, 'ink', mono=True) + cap('Our lab: 1.2 MB, validated.', '', 'green', y=150, h=34))
u3 = (t(180, 22, '2 · Dry run on the copy', 9.4, bold=True) + t(180, 56, 'schematool -upgradeSchema -dryRun', 8.2, 'ink', mono=True) + cap('Read every script it will run.', '', 'green', y=150, h=34))
u4 = (t(180, 22, '3 · Upgrade the copy, test engines', 9.4, bold=True) + t(180, 56, 'Hive, Spark, Trino against the copy', 8.2, 'ink2') + cap('Other engines must support the new schema.', '', 'amber', y=150, h=34))
u5 = (t(180, 22, '4 · Downtime window, then production', 9.4, 'acc', bold=True) + t(180, 56, 'stop HMS → upgrade → -validate → start', 8.2, 'ink2') + cap('Keep the dump for rollback.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Upgrading the metastore schema',
              'The standard upgrade runbook. (Typical practice; commands as used in our lab.)',
              'Schema upgrade', 'Back up and restore-test, dry-run on a copy, test all engines, then upgrade production in a window', [u1, u2, u3, u4, u5],
              ['Hive upgrades include a schema upgrade.',
               'First a tested backup.',
               'Dry-run the upgrade scripts.',
               'Test every engine on the copy.',
               'Upgrade production with a rollback plan.'],
              hid='scenario-upgrade')

# ---- scenario 2: slow metastore
p1 = (t(180, 22, '“SHOW PARTITIONS takes a minute”', 9.4, bold=True) + t(180, 56, 'queries spend long in compilation', 8.4, 'ink2') + cap('Often a metastore problem.', '', 'blue', y=150, h=34))
p2 = (t(180, 22, 'Count partitions per table', 9.4, bold=True) + t(180, 56, 'one table with 2 million partitions', 8.4, 'red') + cap('Lab: 2,000 for 50,000 rows.', '', 'amber', y=150, h=34))
p3 = (t(180, 22, 'Fix the design', 9.4, bold=True) + t(180, 56, 'coarser partitions + bucketing (Lesson 5.4)', 8.2, 'ink2') + cap('Fewer, larger partitions.', '', 'green', y=150, h=34))
p4 = (t(180, 22, 'Tune the service', 9.4, bold=True) + t(180, 56, 'direct SQL on, HMS heap, DB indexes', 8.2, 'ink2') + cap('Scale out HMS instances.', '', 'green', y=150, h=34))
p5 = (t(180, 22, 'Housekeeping', 9.4, 'acc', bold=True) + t(180, 56, "partition retention: 'partition.retention.period'", 7.8, 'ink2', mono=True) + cap('Drop old partitions automatically.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'A slow metastore',
              'Metadata volume is the usual cause. (Typical incident; the counting query is from our lab.)',
              'Metastore performance', 'Too many partitions slow the metastore; count them, redesign, tune the service and expire old partitions', [p1, p2, p3, p4, p5],
              ['Compilation is slow.',
               'One table has far too many partitions.',
               'Redesign the partitioning.',
               'Tune and scale the metastore.',
               'Retire old partitions automatically.'],
              hid='scenario-slow')

# ---- scenario 3: disaster recovery
d1 = (t(180, 22, 'The metastore database disk failed', 9.4, bold=True) + t(180, 56, 'all queries: “Could not connect to meta store”', 8, 'red') + cap('As in our Step 8, but permanent.', '', 'amber', y=150, h=34))
d2 = (t(180, 22, 'Restore the last dump', 9.4, bold=True) + t(180, 56, 'pg_restore → schematool -validate', 8.2, 'ink', mono=True) + cap('Metadata as of the backup time.', '', 'green', y=150, h=34))
d3 = (t(180, 22, 'Reconcile changes since the backup', 9.4, bold=True) + t(180, 56, 'new partitions: MSCK REPAIR TABLE', 8.2, 'ink', mono=True) + cap('New tables must be recreated.', '', 'amber', y=150, h=34))
d4 = (t(180, 22, 'ACID tables are harder', 9.4, bold=True) + t(180, 56, 'transaction state lives in the metastore too', 8.2, 'ink2') + cap('Restore must match the data files’ write IDs.', '', 'amber', y=150, h=34))
d5 = (t(180, 22, 'Prevent', 9.4, 'acc', bold=True) + t(180, 56, 'replicated DB + frequent dumps + restore drills', 8, 'ink2') + cap('Measure recovery time before you need it.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Recovering a lost metastore',
              'A disaster-recovery walk-through. (Typical practice; ACID caveat from the metastore’s design.)',
              'Metastore DR', 'Restore the last dump, validate, re-discover partitions created since, and treat ACID tables with care', [d1, d2, d3, d4, d5],
              ['The catalogue is gone.',
               'Restore and validate the dump.',
               'Re-add what changed since.',
               'Transactional tables need extra care.',
               'Replicate and rehearse.'],
              hid='scenario-dr')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Looking after the catalogue</h2>
  <p>Left: real outputs. Right: where the metadata lives.</p>
''' + two + '''
  <p>Three live scenarios follow: a schema upgrade, a slow metastore, and disaster recovery.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Metastore administration at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'backup', 11, 'green', bold=True) + t(60, 58, 'and drills', 7.4, 'ink2'),
    '1. Backup and restore drills',
    'Nightly dumps of the metastore database and quarterly restore drills are standard on production platforms.',
    ['Dump', '*restore test', 'Confidence']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'upgrade', 11, 'blue', bold=True) + t(60, 58, 'schematool', 7.4, 'ink2'),
    '2. Version upgrades',
    'Every Hive upgrade starts with schematool -info and a dry run against a restored copy of the metastore.',
    ['Copy', '*dry run', 'Safe upgrade']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'reports', 11, 'violet', bold=True) + t(60, 58, 'from SQL', 7.4, 'ink2'),
    '3. Platform reports',
    'SQL on the metastore database lists tables per owner, partition counts, small-file hot spots and stale statistics.',
    ['Metastore DB', '*SQL', 'Dashboards']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'shared', 11, 'acc', bold=True) + t(60, 58, 'catalogue', 7.4, 'ink2'),
    '4. One catalogue for many engines',
    'Spark, Trino, Impala and Flink use the same HMS, so its availability is a platform-wide service level.',
    ['Engines', '*HMS', 'One truth']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'govern', 11, 'acc', bold=True) + t(60, 58, 'ownership', 7.4, 'ink2'),
    '5. Data governance',
    'Database and table properties record owners and classifications that catalog tools such as Atlas or DataHub read.',
    ['Properties', '*catalog tool', 'Lineage']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> architecture and the metastore (<a href="../../01-introduction/03-hive-architecture-and-metastore/">1.3</a>), managed vs external tables (<a href="../../02-hiveql/02-managed-vs-external-tables/">2.2</a>), partition design (<a href="../../05-partitioning-and-bucketing/04-partition-design-small-files-and-skew/">5.4</a>). Basic SQL on PostgreSQL helps.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
