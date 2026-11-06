import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='07-spark-sql', lesson='02-tables-catalog-and-hive-metastore', n='7.2',
    module_label='Module 7 · Spark SQL',
    title='Tables, catalog and Hive metastore',
    desc='Tables and catalogs in PySpark 4.3.0 with an embedded Hive metastore: enableHiveSupport, managed tables with saveAsTable and external tables with LOCATION, partitions and ANALYZE TABLE statistics (200,000 rows, 8 distinct cities), the catalog API, tables reopened by name from a second application while the temp view was gone, DROP TABLE deleting managed files but keeping external ones, and MSCK REPAIR TABLE registering a hand-written partition.',
    og_desc='DROP TABLE deleted the files of one table and kept the other’s. Managed vs external tables and the Hive metastore in Spark, tested.',
    minutes=30, level='Intermediate',
    lead='Paths are fragile; names are not. This lesson registers tables in a <b>Hive metastore</b>, shows the difference between <b>managed</b> and <b>external</b> tables, partitions and statistics, the catalog API, and what survives a new application. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0 + Hive metastore', 'Two applications', 'DROP tested', 'Runs in your browser (Python)'],
)

MAIN = '''# What DROP TABLE does, by table type (a model of Step 6)
tables = {
    "orders_m": {"type": "MANAGED", "files": ["part-0.parquet"]},
    "orders_x": {"type": "EXTERNAL", "files": ["part-0.parquet"]},
}
def drop(name):
    t = tables.pop(name)
    if t["type"] == "MANAGED":
        t["files"].clear()            # Spark deletes the data
    return t["files"]

for name in ("orders_m", "orders_x"):
    print(name, "files left:", drop(name))
print("catalog now:", list(tables))
'''
RUN = dict(
    heading='Run the code: managed vs external',
    intro='<p>A model of Step 6. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('        t["files"].clear()            # Spark deletes the data', 'Lab: managed files 1 → 0.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then add a third, external table and drop it.', code=None),
        dict(label='2 · Predict first: new application', hint='<b>Predict first:</b> what does a new application see?',
             code='''metastore = {"orders_m", "orders_p", "orders_x"}
temp_views = set()            # session-scoped, not stored
print("tables:", sorted(metastore), "| temp views:", temp_views)
'''),
        dict(label='3 · Partition repair', hint='Folders on disk vs partitions in the metastore.',
             code='''on_disk = {"city=Pune", "city=Delhi", "city=Surat"}
registered = {"city=Pune", "city=Delhi"}
print("to add:", on_disk - registered)
'''),
        dict(label='4 · Statistics', hint='What ANALYZE adds.',
             code='''before = {"sizeInBytes": 1466559}
after = dict(before, rowCount=200000, city_distinct=8)
print(before, "->", after)
'''),
        dict(label='5 · Spot the error', hint='Raw source data stored as a managed table.', expect='error',
             code='''raw = {"name": "raw_partner_archive", "type": "MANAGED"}
assert raw["type"] == "EXTERNAL", "DROP TABLE would delete the raw files: register raw data as EXTERNAL"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: the catalog',
    intro='<p>Start with <code>SparkSession.builder.enableHiveSupport()</code>. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Catalog type', cmd='spark.conf.get("spark.sql.catalogImplementation")', file='pyspark',
             output="'hive'", note='in-memory without Hive support.'),
        dict(title='2 · Table types', cmd='[(t.name, t.tableType) for t in spark.catalog.listTables("tiffingo")]', file='pyspark',
             output="[('orders_m', 'MANAGED'), ('orders_p', 'MANAGED'), ('orders_x', 'EXTERNAL')]", note='Also from a new application.'),
        dict(title='3 · Statistics', cmd='[r.data_type for r in spark.sql("DESCRIBE TABLE EXTENDED tiffingo.orders_m").collect() if r.col_name == "Statistics"]', file='pyspark',
             output="['1466559 bytes, 200000 rows']", note='After ANALYZE TABLE.'),
    ],
)

TRACE = dict(
    heading='Resolving a table name',
    intro='<p>Follow how Spark finds what “tiffingo.orders_m” means.</p>',
    code='''temp_views = {"tmp_orders": "plan"}
metastore = {"tiffingo.orders_m": "warehouse/tiffingo.db/orders_m"}
def resolve(name):
    if name in temp_views:
        return "temp view"
    return metastore.get(name, "TABLE_OR_VIEW_NOT_FOUND")
print(resolve("tmp_orders"), "|", resolve("tiffingo.orders_m"), "|", resolve("orders_y"))
''',
    notes={4: 'First :: Temp views shadow tables with the same name.', 6: 'Metastore :: Persistent names and locations.'},
)

WORKED_INTRO = 'Three catalog tasks for TiffinGo’s lake.'
EXAMPLES = [
    dict(level='b', tag='Tables · basics', title='Register the raw archive safely',
         problem='<p>Make raw partner files queryable without risking them.</p>',
         inp='Parquet files in /lake/raw/partner',
         approach=['External table with LOCATION.', 'Check Type in DESCRIBE.', 'Query by name.'],
         code='''print("""spark.sql("CREATE TABLE raw.partner USING parquet LOCATION '/lake/raw/partner'")
spark.sql("DESCRIBE TABLE EXTENDED raw.partner").where("col_name = 'Type'").show()""")
''', notes={1: 'Safe :: DROP keeps the files.'},
         tryit='Step 2.'),
    dict(level='i', tag='Tables · partitions', title='Add today’s partition',
         problem='<p>Files for today were copied by another tool.</p>',
         inp='new folder dt=2026-11-04',
         approach=['ALTER TABLE ADD PARTITION (fast).', 'Or MSCK REPAIR (scans all).', 'Verify with SHOW PARTITIONS.'],
         code='''print("ALTER TABLE sales.orders ADD PARTITION (dt='2026-11-04')")
''', notes={1: 'Targeted :: Cheaper than scanning every folder.'},
         tryit='Step 6.'),
    dict(level='a', tag='Tables · platform', title='Choose a catalog for the platform',
         problem='<p>Spark, Trino and BI must share table definitions.</p>',
         inp='cloud lake',
         approach=['Metastore service on Postgres, or Glue/Unity.', 'External raw, managed curated.', 'ANALYZE after loads.'],
         code='''layers = {"raw": "EXTERNAL", "curated": "MANAGED (or Delta)", "stats": "ANALYZE nightly"}
for k, v in layers.items():
    print(f"{k:8} -> {v}")
''', notes={1: 'Shared :: One catalog for all engines.'},
         tryit='Lesson 11.5 adds table formats.'),
]

QUIZ = mix([
    dict(q='Beginner: What does enableHiveSupport() give Spark?', options=['Faster joins', 'A persistent Hive metastore catalog', 'Hive engine execution', 'HDFS'], answer=1,
         why='catalogImplementation = hive.'),
    dict(q='Beginner: saveAsTable creates a…', options=['Temp view', 'Managed table', 'External table', 'File only'], answer=1,
         why='Data under the warehouse dir.'),
    dict(q='Beginner: Does a temp view survive a new application?', options=['Yes', 'No', 'Only with Hive', 'Only cached'], answer=1,
         why='tableExists → False.'),
    dict(q='Intermediate: DROP TABLE on an external table…', options=['Deletes files', 'Removes only metadata', 'Fails', 'Moves files'], answer=1,
         why='1 file left in our lab.'),
    dict(q='Intermediate: What does ANALYZE TABLE add?', options=['Indexes', 'Row counts and column statistics', 'Partitions', 'Compression'], answer=1,
         why='200,000 rows, 8 distinct cities.'),
    dict(q='Intermediate: Files copied into a new partition folder are…', options=['Visible immediately', 'Invisible until the partition is registered', 'Deleted', 'Merged'], answer=1,
         why='MSCK REPAIR → 10 rows.'),
    dict(q='Advanced: Why not use embedded Derby in production?', options=['Too fast', 'Single application, single machine', 'No SQL', 'Licence'], answer=1,
         why='Use MySQL/Postgres or a managed catalog.'),
    dict(q='Advanced: Which table type for raw data shared with other tools?', options=['Managed', 'External', 'Temp view', 'Global view'], answer=1,
         why='Survives DROP and table changes.'),
])

REVISION = [
    'Catalog resolves names; <code>enableHiveSupport()</code> → persistent Hive metastore.',
    'Managed (<code>saveAsTable</code>): Spark owns files; <b>DROP deletes them</b>.',
    'External (<code>LOCATION</code>): DROP keeps files.',
    'Partitions live in the metastore; <code>MSCK REPAIR</code>/<code>ADD PARTITION</code> for outside writes.',
    '<code>ANALYZE TABLE … COMPUTE STATISTICS</code> feeds the optimizer.',
    'New application: tables found by name; temp views gone.',
    'Production: metastore service (MySQL/Postgres), Glue or Unity; not Derby.',
]
FAQ = [
    ('Do I need Hive installed?', 'No. PySpark includes the Hive client libraries; an embedded Derby metastore needs nothing else. A shared metastore needs a service and database.'),
    ('Where is spark-warehouse?', 'spark.sql.warehouse.dir, by default ./spark-warehouse relative to the working directory; set it explicitly.'),
    ('Can Spark read Hive tables created by Hive?', 'Yes, through the same metastore, including Hive SerDe tables (with some limits on transactional ACID tables).'),
    ('What is a persistent view?', 'CREATE VIEW db.v AS … stores the query in the catalog for all applications. It still stores no data.'),
    ('How do Delta and Iceberg relate?', 'They are table formats with their own metadata logs; they register in a catalog but track files themselves, so no MSCK REPAIR is needed (Lesson 11.5).'),
]

PRACTICE_INTRO = 'Programs about tables and catalog metadata.'
PROBLEMS = [
    dict(level='easy', title='Table type', stmt='Will DROP delete data?', inp='MANAGED / EXTERNAL',
         code='''for t in ("MANAGED", "EXTERNAL"):
    print(t, "->", "deletes data" if t == "MANAGED" else "keeps data")
''', explain='Ownership decides.'),
    dict(level='easy', title='Qualified name', stmt='Build a qualified table name.', inp='db tiffingo, table orders',
         code='''print("tiffingo" + "." + "orders")
''', explain='database.table.'),
    dict(level='easy', title='Partitions', stmt='Partitions for 8 cities.', inp='partitionBy city',
         code='''print(8)
''', explain='SHOW PARTITIONS.'),
    dict(level='medium', title='Missing partitions', stmt='Folders not yet registered.', inp='disk vs metastore',
         code='''disk = {"Pune", "Delhi", "Surat"}; ms = {"Pune", "Delhi"}
print(disk - ms)
''', explain='MSCK REPAIR adds them.'),
    dict(level='medium', title='Average row size', stmt='Bytes per row from statistics.', inp='1,466,559 bytes, 200,000 rows',
         code='''print(round(1_466_559 / 200_000, 1), "bytes")
''', explain='Compressed Parquet.'),
    dict(level='medium', title='Shadowing', stmt='Which object wins for a name?', inp='temp view and table both "orders"',
         code='''print("temp view (it shadows the table)")
''', explain='Use qualified names.'),
    dict(level='business', title='Data at risk', stmt='Data deleted by dropping a managed raw table.', inp='2 years × 50 GB/month',
         code='''print(2 * 12 * 50, "GB")
''', explain='Use EXTERNAL for raw.'),
    dict(level='business', title='Stats freshness', stmt='Days since last ANALYZE if run weekly.', inp='max staleness',
         code='''print(6, "days at most")
''', explain='Run after big loads too.'),
]

SCN_INTRO = 'Catalog questions show whether you have run a real data platform.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“Managed vs external table”',
        'Explain the difference.',
        'ownership?',
        '<p>A managed table’s data lives under the warehouse directory and Spark deletes it on DROP. An external table points to a location I control; DROP removes only the metadata. Raw and shared data should be external.</p>', '“They are the same.”') +
    scn('Data engineering', 'Mid-level', 'Table missing new data',
        'Files were copied into a partitioned table folder but queries miss them.',
        'partition metadata?',
        '''<ul>
          <li>Partitions are stored in the metastore.</li>
          <li>ALTER TABLE ADD PARTITION or MSCK REPAIR TABLE.</li>
          <li>Prefer writing through Spark or a table format.</li>
        </ul>''', 'Re-creating the table.') +
    scn('Data engineering', 'Mid-level', 'Jobs with hard-coded paths',
        'Every job reads s3 paths directly. Any problem?',
        'catalog thinking?',
        '''<ol>
          <li>Moving data breaks jobs; no shared schema or stats.</li>
          <li>Register tables; read with spark.table.</li>
          <li>Run ANALYZE for better plans.</li>
        </ol>''', '“Paths are simpler.”') +
    scn('Platform', 'Senior', 'Metastore design',
        'Design the catalog for Spark, Trino and BI on a lake.',
        'architecture?',
        '''<ul>
          <li>Shared metastore service (HA, Postgres) or Glue/Unity.</li>
          <li>Raw external, curated managed or Delta/Iceberg.</li>
          <li>Permissions, stats jobs, backups of the metastore DB.</li>
        </ul>''', 'Embedded Derby per job.')
)
