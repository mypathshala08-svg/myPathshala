import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l72_catalog.txt'
def sec(a, b=None, drop=()):
    s = capsec(C, a, b, drop)
    return '\n'.join(l if len(l) <= 140 else l[:137] + ' …' for l in s.split('\n'))

def meta(hi=None, dropped=None):
    o = cyl(14, 34, 96, 74, 'metastore', 'violet' if hi == 'ms' else 'card', 8)
    o += t(62, 120, 'names, schemas,', 6.8, 'ink2') + t(62, 130, 'locations, stats', 6.8, 'ink2')
    o += opbox(180, 30, 'warehouse/…/orders_m', 'MANAGED', 'acc' if dropped == 'm' else 'green', 160, 30)
    o += opbox(180, 76, '/data/ext_orders', 'EXTERNAL', 'green', 160, 30)
    o += arrow(110, 60, 180, 45, 'ink3', 1.0) + arrow(110, 76, 180, 91, 'ink3', 1.0)
    return o

# ---------------------------------------------------------------- story
sc_ = (meta('ms') +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('new app: tables still there', 'green'), ('temp view: gone', 'amber'),
           ('DROP managed: files 1 → 0', 'red'), ('DROP external: files kept', 'green'),
           ('new partition folder: 0 rows', 'amber'), ('MSCK REPAIR: 10 rows', 'green')])))
scene_svg = scene('A table is data files plus an entry in a catalog: name, schema, location, partitions and statistics. We created managed, external and partitioned tables in a Hive metastore, reopened them from a new application and dropped them.', sc_,
                  'The <tspan font-weight="700" class="s-acc">catalog</tspan> remembers; <tspan font-weight="700" class="s-acc">managed</tspan> tables take their files with them when dropped.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“I only dropped the table”</h2>
  <div class="story">
    <p class="narration">Kabir cleaned up old tables with <code>DROP TABLE</code>. One was the raw partner archive, created with <code>saveAsTable</code>. The next morning its two years of files were gone from storage, not just the name. A colleague’s table over the same kind of data survived the same command: it was <b>external</b>.</p>

{scene_svg}

K> Sir, the two tables looked identical in SQL. Why did one delete the data?
A> Spark owns the files of a <b>managed</b> table, so dropping it deletes them. For an <b>external</b> table Spark only knows the location; dropping it removes the name. The catalog knows which is which.
R> And the catalog is the Hive metastore we used in the Hive course?
A> Exactly. Spark can use it to remember tables between applications. Today: catalogs, managed vs external, partitions, statistics, the catalog API, reopening from a new application, DROP, and MSCK REPAIR. All outputs are real (PySpark 4.3.0 with an embedded Hive metastore).
  </div>
</section>
'''

lv = '''
LEVELS> Tables and the catalog at three levels
L1> A library catalogue
      <ul>
        <li>Books (files) sit on shelves; the catalogue card says title, author and shelf (name, schema, location).</li>
        <li>A library-owned book is thrown away when its card is removed (managed). A borrowed book goes back to its owner (external).</li>
        <li>A temp view is a sticky note on your desk: gone when you leave.</li>
      </ul>
L2> The API
      <ul>
        <li><code>SparkSession.builder.enableHiveSupport()</code> (Hive metastore) or the default in-memory catalog; <code>spark.sql.warehouse.dir</code> for managed tables.</li>
        <li><code>df.write.saveAsTable("db.t")</code> (managed), <code>CREATE TABLE t USING parquet LOCATION '…'</code> (external), <code>partitionBy</code>, <code>ANALYZE TABLE … COMPUTE STATISTICS</code>, <code>MSCK REPAIR TABLE</code>.</li>
        <li><code>spark.catalog.listDatabases/listTables/listColumns/tableExists/refreshTable</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>A second application found all three tables (<code>orders_m</code>, <code>orders_p</code>, <code>orders_x</code>); the temp view was gone.</li>
        <li><code>DROP TABLE</code>: managed files 1 → 0; external files kept.</li>
        <li>A partition folder added by hand was invisible (0 rows) until <code>MSCK REPAIR TABLE</code> (10 rows).</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Tables, the catalog and the metastore</h2>
''' + def_block(
    'Spark SQL resolves table names through a <b>catalog</b>. The default <code>in-memory</code> catalog lives only as long as the application; with <code>enableHiveSupport()</code> (<code>spark.sql.catalogImplementation=hive</code>) Spark uses a <b>Hive metastore</b>, a database that persistently stores databases, tables, schemas, storage locations, partitions and statistics, shared by Spark, Hive, Trino and other engines. A <b>managed table</b> has its data under the warehouse directory and is owned by Spark: <code>DROP TABLE</code> deletes the data. An <b>external table</b> points to a user-specified <code>LOCATION</code>; dropping it removes only the metadata. Partition metadata of Hive-format partitioned tables is stored in the metastore, so partitions added outside Spark must be registered (<code>MSCK REPAIR TABLE</code> or <code>ALTER TABLE ADD PARTITION</code>). Spark 3+ also supports pluggable catalogs (<code>spark.sql.catalog.*</code>) such as Unity Catalog, Iceberg and Glue.',
    'A table is files plus a catalog entry with its name, columns and location. The Hive metastore keeps these entries between applications. Managed tables belong to Spark (dropping deletes files), external tables only point to files (dropping keeps them).') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Catalog', 'Where table names are resolved.'),
    ('Hive metastore', 'Persistent catalog database (Derby, MySQL, Postgres…).'),
    ('Warehouse dir', 'Default location of managed tables.'),
    ('Managed table', 'Spark owns the files.'),
    ('External table', 'Metadata over files you own.'),
    ('ANALYZE TABLE', 'Collect row counts and column stats.'),
    ('MSCK REPAIR TABLE', 'Register partition folders found on disk.'),
    ('Catalog API', 'spark.catalog.*.'),
]) + '''

  <h3>Managed or external?</h3>
''' + table(['', 'Managed', 'External'], [
    ['Created with', '<code>saveAsTable</code>, <code>CREATE TABLE … AS SELECT</code>', '<code>CREATE TABLE … LOCATION</code>, <code>option("path", …)</code>'],
    ['Data location', 'warehouse/db.db/table', 'your path'],
    ['DROP TABLE', '<b>deletes data</b> (lab: 1 → 0 files)', 'keeps data (lab: 1 file left)'],
    ['Use for', 'tables fully owned by the pipeline', 'shared/raw data, data used by other tools'],
], minw=620) + lv + '''
EXAM> “Managed vs external tables?” For a managed table Spark controls both metadata and data under the warehouse directory, and DROP TABLE deletes the files. For an external table the catalog stores only metadata pointing to an existing location; DROP removes the entry and leaves the data. Use external tables for data that other systems own or that must survive table changes.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Catalogs you will meet</h2>
''' + table(['Catalog', 'Where', 'Notes'], [
    ['in-memory (default)', 'Any Spark', 'Tables forgotten when the application stops'],
    ['Hive metastore', 'Hadoop clusters, EMR, Dataproc', 'Embedded Derby for tests; MySQL/Postgres in production'],
    ['AWS Glue Data Catalog', 'EMR, Glue, Athena', 'Hive-compatible, shared with Athena'],
    ['Unity Catalog', 'Databricks (open-source version too)', 'Governance, permissions, lineage'],
    ['Iceberg / Delta catalogs', '<code>spark.sql.catalog.name=…</code>', 'Table formats with their own metadata (Lesson 11.5)'],
], minw=640) + '''
WARN> The embedded Derby metastore (a <code>metastore_db</code> folder in the current directory) allows only one application at a time and lives on one machine. It is fine for learning and tests. Shared clusters need a metastore service backed by MySQL or PostgreSQL, or a managed catalog.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Two applications, one metastore</h2>
  <p>All outputs are real: PySpark 4.3.0 with <code>enableHiveSupport()</code> and an embedded Derby metastore. Steps 1–5 run in one application; Step 6 in a second, separate Python process.</p>
''' + stepper([
    ('Step 1 · A Hive catalog and a database',
     code('python', 'l72_catalog.py', 'spark = (SparkSession.builder.config("spark.sql.warehouse.dir", W)\n         .enableHiveSupport().getOrCreate())\nspark.conf.get("spark.sql.catalogImplementation")\nspark.sql("CREATE DATABASE IF NOT EXISTS tiffingo")', sec('== 1)', '== 2)')),
     'With Hive support the catalog implementation is <code>hive</code>, and a <code>metastore_db</code> folder appeared beside the script. Databases are namespaces; tables are named <code>tiffingo.orders</code>.'),
    ('Step 2 · Managed and external tables',
     code('python', 'l72_catalog.py', 'o.write.mode("overwrite").saveAsTable("tiffingo.orders_m")\no.write.parquet(ext)\nspark.sql(f"CREATE TABLE tiffingo.orders_x USING parquet LOCATION \'{ext}\'")\nspark.sql("DESCRIBE TABLE EXTENDED tiffingo.orders_m")', sec('== 2)', '== 4)')),
     '<code>saveAsTable</code> wrote the data under the warehouse directory and registered a <b>MANAGED</b> table. <code>CREATE TABLE … LOCATION</code> registered existing files as an <b>EXTERNAL</b> table without copying anything. Same SQL to query both.'),
    ('Step 3 · Partitions and statistics',
     code('python', 'l72_catalog.py', 'o.write.mode("overwrite").partitionBy("city").saveAsTable("tiffingo.orders_p")\nspark.sql("SHOW PARTITIONS tiffingo.orders_p")\nspark.sql("ANALYZE TABLE tiffingo.orders_m COMPUTE STATISTICS FOR COLUMNS city, amount")\nspark.sql("DESCRIBE TABLE EXTENDED tiffingo.orders_m city")', sec('== 4)', '== 6)')),
     'The metastore recorded 8 partitions. Before <code>ANALYZE</code> the catalog knew only the size; afterwards it knew <b>200,000 rows</b> and per-column statistics (8 distinct cities, no nulls). The optimizer uses these numbers to choose join strategies (Lesson 7.3).'),
    ('Step 4 · The catalog API',
     code('python', 'l72_catalog.py', 'spark.catalog.listTables("tiffingo")\nspark.catalog.listColumns("tiffingo.orders_p")\no.createOrReplaceTempView("tmp_orders")', sec('== 6)', '== 7)')),
     'The catalog API answers questions in Python: which tables exist, of which type, which columns are partition columns. Temp views appear in the same listing, marked temporary.'),
    ('Step 5 · A new application',
     code('python', 'l72_catalog.py', '# separate process: python l72_catalog.py reopen\nspark.catalog.listTables("tiffingo")\nspark.catalog.tableExists("tmp_orders")\nspark.table("tiffingo.orders_m").count()', sec('== 7)', '== 8)')),
     'A brand-new process found all three tables and read 200,000 rows by name, with no paths in the code. The temp view did not survive. This is the point of a metastore: tables outlive applications and can be shared by jobs, notebooks and other engines.'),
    ('Step 6 · DROP and MSCK REPAIR',
     code('python', 'l72_catalog.py', 'spark.sql("DROP TABLE tiffingo.orders_m"); spark.sql("DROP TABLE tiffingo.orders_x")\n# write files into …/orders_p/city=Surat directly\nspark.table("tiffingo.orders_p").where("city=\'Surat\'").count()\nspark.sql("MSCK REPAIR TABLE tiffingo.orders_p")', sec('== 8)')),
     'Kabir’s accident, reproduced: dropping the managed table <b>deleted its files</b>; dropping the external table left them. Files written straight into a new <code>city=Surat</code> folder were invisible because the metastore did not know the partition; <code>MSCK REPAIR TABLE</code> scanned the folders and registered it: 10 rows.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('catalogImplementation: hive', G), ("databases: ['default', 'tiffingo']", W)], size=7.6),
    term([('orders_m: MANAGED  (warehouse)', W), ('orders_x: EXTERNAL (ext_orders)', W)], size=7.4),
    term([('8 partitions', W), ('ANALYZE: 200000 rows, 8 distinct', G)], size=7.6),
    term([('new app: orders_m, orders_p, orders_x', G), ('temp view survives? False', Y)], size=7.4),
    term([('DROP managed : files 0', RD), ('DROP external: files 1', G), ('Surat 0 -> MSCK REPAIR -> 10', G)], size=7.4),
]
B1 = [
    t(180, 14, 'A persistent catalog', 9.4, bold=True) + meta('ms') + cap('metastore_db holds table definitions.', '', 'violet', y=144, h=30),
    t(180, 14, 'Who owns the files?', 9.4, bold=True) + meta() + cap('Managed: Spark. External: you.', '', 'blue', y=144, h=30),
    t(180, 14, 'Metadata the optimizer uses', 9.4, bold=True) + flow([('table', 'size only', 'card'), ('ANALYZE', 'stats', 'blue'), ('optimizer', 'better plans', 'green')], y=50, w=96, gap=22) + cap('Row counts and column stats.', '', 'blue', y=144, h=30),
    t(180, 14, 'Names outlive applications', 9.4, bold=True) + flow([('app 1', 'creates', 'blue'), ('metastore', 'remembers', 'violet'), ('app 2', 'reads by name', 'green')], y=50, w=96, gap=22) + cap('Temp views do not survive.', '', 'green', y=144, h=30),
    t(180, 14, 'DROP deletes managed data', 9.4, bold=True) + meta(dropped='m') + cap('External data stays on disk.', '', 'red', y=144, h=30),
]
see_caps = ['Hive support enabled.', 'One table owned, one pointed to.', 'Partitions and statistics recorded.', 'Tables found by a new process.', 'DROP and repair.']
behind_caps = ['Metastore = persistent catalog.', 'Managed vs external.', 'Stats feed the optimizer.', 'Catalog survives restarts.', 'Ownership decides DROP.']
two = anim_two('Tables and the catalog', 'Names that outlive applications', 'Real lab outputs', 'Catalog and files', see, B1, see_caps, behind_caps)

e1 = (t(180, 22, 'Clean up old tables', 9.4, bold=True) + t(180, 56, 'DROP TABLE raw_partner_archive', 8.4, 'ink', mono=True) + cap('Created with saveAsTable.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Two years of files gone', 9.4, bold=True) + t(180, 56, 'managed table: data deleted', 8.4, 'ink2') + cap('Like our Step 6.', '', 'red', y=150, h=34))
e3 = (t(180, 22, 'Raw data as external tables', 9.4, bold=True) + t(180, 56, 'CREATE TABLE … LOCATION', 8.4, 'ink', mono=True) + cap('DROP keeps files.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Check before dropping', 9.4, bold=True) + t(180, 56, 'DESCRIBE EXTENDED → Type', 8.4, 'ink', mono=True) + cap('MANAGED or EXTERNAL.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Bucket versioning / time travel', 9.4, 'acc', bold=True) + t(180, 56, 'undo with storage or Delta', 8.4, 'ink2') + cap('Safety net.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'A DROP that deleted two years of data',
              'Managed vs external tables. (Behaviour from our lab.)',
              'DROP TABLE', 'Dropping a managed table deletes its files; keep raw data in external tables and check the type first', [e1, e2, e3, e4, e5],
              ['DROP.', 'Data gone.', 'External.', 'Check type.', 'Safety net.'],
              hid='scenario-drop')
b1 = (t(180, 22, 'Upstream copies files', 9.4, bold=True) + t(180, 56, 'into …/dt=2026-11-04/', 8.4, 'ink', mono=True) + cap('Hive-style partitioned table.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Queries show no new day', 9.4, bold=True) + t(180, 56, 'partition not in metastore', 8.4, 'ink2') + cap('0 rows.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'MSCK REPAIR TABLE', 9.4, bold=True) + t(180, 56, 'or ALTER TABLE ADD PARTITION', 8.4, 'ink2') + cap('Partition registered.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Better: write through Spark', 9.4, bold=True) + t(180, 56, 'saveAsTable / insertInto', 8.4, 'ink2') + cap('Metastore updated.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Table formats', 9.4, 'acc', bold=True) + t(180, 56, 'Delta/Iceberg track files in a log', 8.4, 'ink2') + cap('No repair needed.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Today’s partition is missing',
              'Partition metadata. (Behaviour from our lab.)',
              'MSCK REPAIR', 'Files written outside Spark are unknown to the metastore until partitions are added or repaired', [b1, b2, b3, b4, b5],
              ['Files copied.', 'Invisible.', 'Repair.', 'Write via Spark.', 'Table formats.'],
              hid='scenario-msck')
u1 = (t(180, 22, 'Each job hard-codes paths', 9.4, bold=True) + t(180, 56, 's3://bucket/x/y/orders_v3/', 8.4, 'ink', mono=True) + cap('Moving data breaks jobs.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Register tables once', 9.4, bold=True) + t(180, 56, 'spark.table("sales.orders")', 8.4, 'ink', mono=True) + cap('Jobs use names.', '', 'green', y=150, h=34))
u3 = (t(180, 22, 'Shared metastore', 9.4, bold=True) + t(180, 56, 'Spark, Hive, Trino, Athena', 8.4, 'ink2') + cap('One definition.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Statistics for the optimizer', 9.4, bold=True) + t(180, 56, 'ANALYZE after big loads', 8.4, 'ink2') + cap('Lesson 7.3.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Governance', 9.4, 'acc', bold=True) + t(180, 56, 'permissions in Unity/Ranger/Lake Formation', 8.0, 'ink2') + cap('Who may read what.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'From paths to a governed catalog',
              'Why platforms use catalogs. (Typical.)',
              'Catalogs', 'Registering tables in a shared catalog decouples jobs from paths and enables stats and permissions', [u1, u2, u3, u4, u5],
              ['Paths.', 'Names.', 'Shared.', 'Stats.', 'Governance.'],
              hid='scenario-catalog')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Names that outlive applications</h2>
  <p>Left: real outputs. Right: catalog and files.</p>
''' + two + '''
  <p>Three live scenarios follow: a DROP that deleted data, a missing partition, and moving from paths to a catalog.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Catalogs at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'shared', 11, 'blue', bold=True) + t(60, 58, 'metastore', 7.4, 'ink2'),
    '1. One metastore, many engines',
    'Spark writes tables; Hive, Trino and BI tools read them through the same metastore.',
    ['Spark', '*metastore', 'Trino / BI']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'raw', 12, 'green', bold=True) + t(60, 58, 'external', 7.4, 'ink2'),
    '2. Raw zones as external tables',
    'Landing data is registered externally so table changes never delete source files.',
    ['Landing files', '*EXTERNAL', 'Safe DROP']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'AWS', 12, 'violet', bold=True) + t(60, 58, 'Glue', 7.4, 'ink2'),
    '3. Glue Data Catalog',
    'EMR Spark uses Glue as its metastore so Athena sees the same tables.',
    ['EMR Spark', '*Glue', 'Athena']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'stats', 12, 'acc', bold=True) + t(60, 58, 'ANALYZE', 7.4, 'ink2'),
    '4. Statistics jobs',
    'Nightly ANALYZE TABLE keeps optimizer statistics fresh after loads.',
    ['Load', '*ANALYZE', 'Better plans']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'govern', 11, 'acc', bold=True) + t(60, 58, 'Unity', 7.4, 'ink2'),
    '5. Governance',
    'Unity Catalog and Lake Formation add permissions and lineage on top of table names.',
    ['Tables', '*grants', 'Controlled access']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> views in <a href="../01-spark-sql-and-views/">7.1</a>, partitioned writes in <a href="../../05-reading-and-writing-data/03-writing-data-and-small-files/">5.3</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
