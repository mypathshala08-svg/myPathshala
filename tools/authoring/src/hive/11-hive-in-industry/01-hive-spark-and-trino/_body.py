import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
ENG = os.path.join(HERE, '..', '..', 'lab', 'engines') + os.sep
def capf(n):
    return re.sub(r'; Query ID[^\n]*', '', open(CAP + n).read().rstrip())
def first(n, key):
    return next(l for l in capf(n).split('\n') if key in l)
def tim(s):
    """Drop spark-sql 'Time taken' lines."""
    return '\n'.join(l for l in s.split('\n') if not l.startswith('Time taken'))

def opbox(x, y, label, sub='', tone='card', w=128, h=26):
    o = box(x, y, w, h, tone) + t(x + w / 2, y + (11 if sub else 16), label, 7.2, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 21, sub, 6.4, 'ink2', mono=True)
    return o

# ---------------------------------------------------------------- story
sc = (opbox(14, 20, 'Hive 4.2.1', 'ETL, ACID, MVs', 'blue', 130, 30) + opbox(14, 62, 'Spark 3.5.6', 'data science, ML', 'green', 130, 30) + opbox(14, 104, 'Trino 476', 'interactive BI', 'violet', 130, 30) +
      arrow(146, 35, 226, 72, 'acc', 1.6) + arrow(146, 77, 226, 77, 'acc', 1.6) + arrow(146, 119, 226, 82, 'acc', 1.6) +
      box(230, 46, 130, 62, 'amber') + t(295, 70, 'One metastore', 8.6, bold=True) + t(295, 88, 'thrift :9083', 7.4, 'ink2', mono=True) +
      arrow(364, 77, 400, 77, 'acc', 2) +
      box(404, 12, 226, 128, 'card') + t(517, 30, 'Same table, three answers?', 8.6, bold=True) +
      ''.join(t(416, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([('orders (ORC): 50,000 everywhere', 'green'), ('orders_tx (ACID) in Hive: 5,000,001', 'ink'), ('  in Trino: 5,000,004', 'red'), ('  in Spark: 0', 'red'), ('orders_ice (Iceberg): 4,886', 'ink')])))
scene_svg = scene('Hive, Spark and Trino share one Hive metastore. A plain ORC table gave the same answer everywhere; the transactional table gave three different counts.', sc,
                  'One catalogue does not mean <tspan font-weight="700" class="s-acc">one behaviour</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Spark says there are no orders”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s data scientists use Spark, the BI team wants Trino for dashboards, and the warehouse is built in Hive. Everyone points their engine at the same Hive metastore. On Monday, a data scientist reports that the orders table is empty. In Hive it has five million rows.</p>

{scene_svg}

K> Sir, if all three engines read the same metastore, how can the answers differ?
A> The metastore only says <b>where</b> a table is and <b>what format</b> it has. Each engine reads the files with its own code. Plain ORC or Parquet tables are easy. Hive’s own <b>transactional</b> tables, Hive-specific <b>views</b>, and <b>Iceberg</b> tables created through Hive each need special support, and the metastore API itself changes between versions.
R> So we test?
A> We test. Today we connect Spark 3.5.6 and Trino 476 to our Hive 4.2.1 metastore and run the same queries everywhere. The first attempt fails, one table gives three different counts, and the SQL dialects disagree on details. All outputs are real.
  </div>
</section>
'''

lv = '''
LEVELS> Many engines at three levels
L1> One library catalogue, several readers
      <ul>
        <li>The metastore is a shared catalogue. Hive, Spark and Trino are different readers using it.</li>
        <li>Each reader must understand the book’s language (file format) and any special rules (transactions, Iceberg).</li>
        <li>Same catalogue, but a reader that does not know the rules may read the wrong pages.</li>
      </ul>
L2> How each engine connects
      <ul>
        <li><b>Spark SQL</b>: Hive support plus <code>hive.metastore.uris</code>; its built-in Hive client is 2.3.x, configurable with <code>spark.sql.hive.metastore.version</code> and <code>.jars</code>.</li>
        <li><b>Trino</b>: a catalog file with <code>connector.name=hive</code> and <code>hive.metastore.uri</code>; Iceberg tables through a separate <code>iceberg</code> catalog.</li>
        <li><b>Hive</b>: native; the only engine that writes Hive ACID tables with all features (MERGE, compaction, materialized views).</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>Spark’s built-in 2.3.9 client failed on Hive 4’s metastore (<code>Invalid method name: 'get_table'</code>); a 3.1.3 client worked.</li>
        <li>ORC, text and Parquet tables and the views gave identical answers in all engines. The ACID table: Hive 5,000,001 rows, Trino 5,000,004 (deleted and old versions included), Spark <b>0</b>, with no error.</li>
        <li>Trino’s native local file system silently returned 0 rows for <code>file:</code> locations; Spark could not open the Iceberg table through Hive’s storage handler or its own Hive catalog.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>One metastore, many engines</h2>
''' + def_block(
    'The <b>Hive Metastore</b> (HMS) has become the shared catalogue of the open data stack: Spark SQL, Trino/Presto, Impala, Flink and many cloud services read and write table definitions through its Thrift API. Sharing the catalogue lets each engine see the same databases, tables, schemas, partitions and locations, but each engine reads and writes the <b>data files</b> with its own readers. Compatibility therefore depends on the metastore API version, the file formats and SerDes, Hive-specific features (ACID tables, views in HiveQL, storage handlers such as Iceberg’s) and SQL dialect differences.',
    'Hive, Spark and Trino can all use the same Hive metastore, so a table created in one is visible in the others. Whether they return the same answer depends on whether each engine understands the table’s format and Hive-specific features.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Engine', 'The program that runs SQL: Hive, Spark, Trino, Impala …'),
    ('Thrift API', 'The protocol engines use to talk to the metastore.'),
    ('Metastore client', 'An engine’s library for that API (Spark built-in: Hive 2.3.9).'),
    ('Catalog (Trino)', 'A configured connector, e.g. hive or iceberg.'),
    ('Storage handler', 'Hive plug-in for special tables (Iceberg, HBase, Kafka …).'),
    ('Dialect', 'Each engine’s SQL details: types, reserved words, functions.'),
    ('Table format', 'ORC/Parquet files, Hive ACID, Iceberg, Delta …'),
    ('Interoperability test', 'Running the same queries in every engine before trusting them.'),
]) + '''

  <h3>Who reads what: our lab’s results</h3>
''' + table(['Table type', 'Hive 4.2.1', 'Spark 3.5.6 (Hive 3.1.3 client)', 'Trino 476'], [
    ['External ORC / text (<code>orders</code>, <code>customers</code>)', '✓ reference', '✓ identical results', '✓ identical (with Hadoop FS support)'],
    ['Spark-created Parquet / ORC tables', '✓ read', '✓', '—'],
    ['Hive views (<code>v_gold_orders</code>)', '✓', '✓ 13,014', '✓ 13,014 (views enabled)'],
    ['Full ACID (<code>orders_tx</code>)', '✓ 5,000,001', '✗ 0 rows, no error', '✗ 5,000,004: deletes ignored'],
    ['Iceberg via Hive (<code>orders_ice</code>)', '✓ 4,886', '✗ could not load (see Step 6)', '✓ 4,886 via iceberg catalog'],
], minw=760) + lv + '''
EXAM> “Can Spark and Trino use Hive tables?” Yes, through the Hive metastore: Spark with Hive support and hive.metastore.uris, Trino with a hive catalog. Plain ORC/Parquet tables work well. Check Hive ACID tables, HiveQL views and Iceberg tables per engine and version; metastore client versions must also be compatible.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Which engine for which job</h2>
''' + table(['Engine', 'Strengths', 'Typical use', 'Watch out for'], [
    ['Hive (Tez/LLAP)', 'ACID, MERGE, MVs, compaction, mature SQL', 'Batch ETL, warehouse loads', 'Start-up latency for small queries'],
    ['Spark SQL', 'Python/Scala APIs, ML, streaming, large ETL', 'Data engineering, data science', 'Hive ACID support; metastore client version'],
    ['Trino / Presto', 'Low-latency MPP, many connectors, federation', 'Interactive BI, ad-hoc', 'Long jobs restart on failure (unless fault-tolerant mode)'],
    ['Impala', 'Low-latency C++ MPP, Kudu', 'BI on Cloudera', 'Mostly Cloudera platforms'],
    ['Flink', 'Streaming SQL', 'Real-time pipelines writing tables', 'Batch features limited'],
], minw=760) + '''
WARN> Never assume a table is “just a table” across engines. In our lab the same transactional table gave three different counts, and two of the three engines raised <b>no error</b>. Run a small interoperability test (row counts, a few aggregates) for every table type and engine version before people rely on it.
</section>
'''

SPARK3 = open(ENG + 'sparksql3.sh').read().rstrip()
TRINO_CAT = open(ENG + 'trino/catalog/hive.properties').read().rstrip() + '\n\n# iceberg.properties\n' + open(ENG + 'trino/catalog/iceberg.properties').read().rstrip()
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Three engines, one metastore, real answers</h2>
  <p>All outputs are real: Hive 4.2.1, Spark 3.5.6 (<code>apache/spark</code> image) and Trino 476 (<code>trinodb/trino</code>), all connected to the lab metastore and the same warehouse volume. Scripts are in the course lab folder (<code>lab/engines</code>).</p>
''' + stepper([
    ('Step 1 · Spark’s first attempt fails',
     code('bash', 'spark-sql (built-in Hive client)', "spark-sql --conf spark.hadoop.hive.metastore.uris=thrift://metastore:9083 \\\n  -e \"SHOW DATABASES; USE tiffingo; SELECT COUNT(*) FROM orders;\"", 'default\ntiffingo\n' + capf('l111_spark_default.txt')),
     'Spark listed the databases, then failed on the first table: Spark 3.5 ships a <b>Hive 2.3.9</b> metastore client, which calls the Thrift method <code>get_table</code>; the Hive 4 metastore no longer offers it. Same catalogue, incompatible client.'),
    ('Step 2 · Use a newer metastore client',
     code('bash', 'sparksql3.sh', SPARK3),
     'Spark can load a different Hive client: <code>spark.sql.hive.metastore.version=3.1.3</code> with <code>.jars=maven</code> downloaded 209 JAR files (236 MB) on the first run, then <code>SELECT COUNT(*) FROM orders</code> returned <b>50,000</b>, as in Hive. In production you pin these JARs locally (<code>.jars=path</code>) instead of downloading at start-up.'),
    ('Step 3 · The same report in Spark and Trino',
     code('sql', 'spark-sql  ·  trino', "-- Spark\nSELECT c.city, COUNT(*) AS n, SUM(o.amount) AS rev FROM orders o JOIN customers c ON o.customer_id = c.customer_id\nWHERE o.order_date = '2026-10-05' AND c.plan = 'Gold' GROUP BY c.city ORDER BY rev DESC LIMIT 3;\nSELECT COUNT(*) AS gold_orders FROM v_gold_orders;          -- the Hive view from Lesson 9.2\n\n-- Trino\nSELECT … FROM hive.tiffingo.orders o JOIN hive.tiffingo.customers c … WHERE o.order_date = DATE '2026-10-05' …;\nSELECT COUNT(*) AS gold_orders FROM hive.tiffingo.v_gold_orders;", '-- Spark\n' + tim(capf('l111_spark_q.txt')) + '\n\n-- Trino\n' + capf('l111_trino_q.txt') + '\n' + capf('l111_trino_view.txt')),
     'Identical to Hive’s answer from Lesson 8.1 (Bengaluru 100, 26,600.00), and the Hive view gave 13,014 Gold orders in both engines. Trino needed <code>hive.hive-views.enabled=true</code> to read Hive views (off by default) and three-part names <code>catalog.schema.table</code>.'),
    ('Step 4 · Trino’s catalog files, and a silent zero',
     code('properties', 'etc/trino/catalog/hive.properties', TRINO_CAT),
     'Our first Trino configuration used the new native local file system (<code>fs.native-local.enabled=true</code>). Every table returned <b>0 rows</b>, with no error, because our tables have <code>file:</code> locations:\n\n' + '<code>' + capf('l111_trino_zero.txt').split('\n')[1] + '</code> → 0. Switching to <code>fs.hadoop.enabled=true</code> gave 2,000 and 50,000. On HDFS or S3 you configure the matching file system; the lesson is to verify counts, not just connectivity.'),
    ('Step 5 · The transactional table: three engines, three answers',
     code('sql', 'Hive  ·  Trino  ·  Spark', "-- Hive\nSELECT COUNT(*) AS n FROM orders_tx;\nSELECT order_id, status FROM orders_tx WHERE order_id > 999000000 ORDER BY order_id;\n-- Trino\nSELECT COUNT(*) AS rows FROM hive.tiffingo.orders_tx;\nSELECT order_id, status FROM hive.tiffingo.orders_tx WHERE order_id > 999000000 ORDER BY order_id, status;\n-- Spark\nSELECT COUNT(*) FROM orders_tx;", '-- Hive\n' + capf('l111_hive_acid.txt') + '\n' + capf('l111_hive_acid_rows.txt') + '\n\n-- Trino\n' + capf('l111_trino_acid.txt') + '\n' + capf('l111_trino_acid_rows.txt') + '\n\n-- Spark\n' + tim(capf('l111_spark_acid.txt'))),
     '<code>orders_tx</code> is the full-ACID table from Modules 9 and 10, with rows inserted, deleted and updated since. <b>Hive</b>: 5,000,001 rows, order 999000010 once, CANCELLED. <b>Trino 476</b>: 5,000,004: it ignored the delete deltas and returned two deleted orders and the old NEW version of the updated one. <b>Spark</b>: <b>0 rows</b>, because Spark does not read Hive ACID tables. None of the wrong answers raised an error.'),
    ('Step 6 · Iceberg tables: format first, engine second',
     code('sql', 'Spark  ·  Trino', "-- Spark through the Hive table definition\nSELECT COUNT(*) FROM orders_ice;\n-- Spark through its Iceberg catalog (iceberg-spark-runtime 1.9.1, type=hive)\nSELECT COUNT(*) AS rows FROM ice.tiffingo.orders_ice;\n\n-- Trino: hive catalog, then iceberg catalog\nSELECT COUNT(*) FROM hive.tiffingo.orders_ice;\nSELECT COUNT(*) AS rows FROM iceberg.tiffingo.orders_ice;\nSELECT snapshot_id, operation FROM iceberg.tiffingo.\"orders_ice$snapshots\" ORDER BY committed_at;", '-- Spark\n' + first('l111_spark_ice.txt', 'ClassNotFoundException: org.apache.iceberg.mr.hive.HiveIcebergStorageHandler') + '\n' + first('l111_spark_ice2.txt', 'TApplicationException') + '\n\n-- Trino\n' + capf('l111_trino_ice_hive.txt') + '\n' + capf('l111_trino_ice.txt') + '\n' + capf('l111_trino_snap.txt')),
     'Through the Hive definition, Spark needs Hive’s Iceberg storage handler class; through its own Iceberg catalog, it hit the same <code>get_table</code> incompatibility as in Step 1, because Iceberg’s Hive catalog uses Spark’s built-in client. <b>Trino</b> refused it in the hive catalog but read it through the <b>iceberg</b> catalog: 4,886 rows, as in Hive, and the same four snapshots from Lesson 7.3. For Iceberg, engines should use an Iceberg catalog (Hive metastore, REST, Glue), not Hive’s table definition.'),
    ('Step 7 · Writing from Spark, reading in Hive',
     code('sql', 'spark-sql, then Beeline', "-- Spark\nCREATE TABLE spark_city_pq USING parquet AS SELECT city, COUNT(*) AS n FROM orders GROUP BY city;\nCREATE TABLE spark_city_orc STORED AS ORC AS SELECT city, COUNT(*) AS n FROM orders GROUP BY city;\n-- Hive\nSELECT * FROM spark_city_pq ORDER BY city LIMIT 3;\nSELECT * FROM spark_city_orc ORDER BY city LIMIT 3;\nSHOW TBLPROPERTIES spark_city_pq;", capf('l111_hive_reads.txt')),
     'Both Spark tables were readable in Hive with identical numbers. The Spark “data source” table carries Spark-only properties (<code>spark.sql.sources.provider = parquet</code>, the schema as JSON), and Hive 4’s metastore turned it into an EXTERNAL table with purge. Writing simple Parquet or ORC tables from Spark for Hive and Trino to read is the safest direction.'),
    ('Step 8 · Dialects and speed',
     code('sql', 'Hive  ·  Trino  ·  all three', "-- Hive: 'rows' is a reserved word\nSELECT COUNT(*) AS rows FROM orders_tx;\n-- Trino: no implicit string → date cast\nSELECT COUNT(*) FROM hive.tiffingo.orders WHERE order_date = '2026-10-05';\n\n-- same aggregation on orders_big (5,000,000 rows, ORC), three runs each\nSELECT city, status, COUNT(*) AS n, SUM(amount) AS rev, AVG(amount) AS avg_amt\nFROM tiffingo.orders_big WHERE amount > 100 GROUP BY city, status;", capf('l111_hive_rows_err.txt') + '\n\n' + capf('l111_trino_type.txt') + '\n\n' + capf('l111_times.txt')),
     'SQL that runs in one engine may not parse in another: <code>rows</code> is reserved in Hive but fine in Trino; Trino will not compare a DATE with a string literal, which Hive casts silently. On our single-node lab, Trino answered in about <b>0.75 s</b> once warm, Hive in about 1.6 s and Spark in about 2.1 s. Treat these as indicative only: one machine, tiny data, different ways of measuring.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('spark-sql> SELECT COUNT(*) FROM orders;', W), ("Invalid method name: 'get_table'", RD), ('spark.sql.hive.metastore.version=3.1.3', W), ('50000', G)], size=7.4),
    term([('Hive   Bengaluru 100 26600.00', G), ('Spark  Bengaluru 100 26600.00', G), ('Trino  Bengaluru 100 26600.00', G), ('v_gold_orders: 13014 everywhere', G)], size=7.6),
    term([('orders_tx  Hive   5,000,001', G), ('orders_tx  Trino  5,000,004', RD), ('orders_tx  Spark  0', RD), ('no errors in Trino or Spark', Y)], size=7.6),
    term([('Spark: HiveIcebergStorageHandler not found', RD), ("Spark ice catalog: 'get_table'", RD), ('Trino hive catalog: Cannot query Iceberg', Y), ('Trino iceberg catalog: 4886', G)], size=7.2),
    term([("Hive:  AS rows → ParseException", RD), ("Trino: date = varchar → error", RD), ('Trino 0.75 s · Hive 1.6 s · Spark 2.1 s', W)], size=7.4),
]
def hub(hi):
    o = box(130, 54, 100, 34, 'amber') + t(180, 75, 'metastore', 8, bold=True)
    for k, (name, x, y) in enumerate([('Hive', 20, 30), ('Spark', 20, 96), ('Trino', 250, 63)]):
        o += opbox(x, y, name, '', 'acc' if k == hi else ['blue', 'green', 'violet'][k], 90, 26)
    o += arrow(112, 46, 130, 64, 'ink3', 1.4) + arrow(112, 108, 130, 80, 'ink3', 1.4) + arrow(250, 76, 232, 72, 'ink3', 1.4)
    return o
B1 = [
    t(180, 22, 'The metastore API has versions', 9.4, bold=True) + hub(1) + cap('Old clients may call methods that no longer exist.', '', 'amber', y=140, h=34),
    t(180, 22, 'Plain files: one truth', 9.4, bold=True) + hub(-1) + cap('ORC/Parquet/text read the same everywhere.', '', 'green', y=140, h=34),
    t(180, 22, 'Hive ACID needs Hive’s reader', 9.4, bold=True) + hub(0) + cap('Base + deltas + delete deltas must be merged.', 'Others: wrong rows or none.', 'amber', y=130, h=46),
    t(180, 22, 'Iceberg needs an Iceberg catalog', 9.4, bold=True) + hub(2) + cap('Not Hive’s storage-handler definition.', '', 'violet', y=140, h=34),
    t(180, 22, 'Same tables, different SQL', 9.4, bold=True) + hub(-1) + cap('Reserved words, casts, functions differ.', '', 'blue', y=140, h=34),
]
see_caps = ['Spark’s built-in client could not talk to the Hive 4 metastore.',
            'Plain tables and views gave identical answers.',
            'The ACID table gave three different counts.',
            'Iceberg worked in Trino through its iceberg catalog.',
            'Dialects differ; timings are indicative.']
behind_caps = ['Thrift methods change between metastore versions.',
               'All engines read the same ORC files the same way.',
               'Only Hive merged the delta and delete-delta folders correctly.',
               'Iceberg metadata is read by Iceberg libraries.',
               'Each engine has its own parser and type rules.']
two = anim_two('Many engines', 'One catalogue, three readers', 'Real lab outputs', 'Why answers differ', see, B1, see_caps, behind_caps)

# ---- scenario 1: data scientist sees empty table
e1 = (t(180, 22, '“orders_tx is empty in Spark”', 9.4, bold=True) + t(180, 56, 'Hive shows 5,000,001 rows', 8.4, 'ink2') + cap('Exactly our Step 5.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Check the table type', 9.4, bold=True) + t(180, 56, "transactional = true, full ACID", 8.4, 'ink', mono=True) + cap('Spark does not read Hive ACID.', '', 'amber', y=150, h=34))
e3 = (t(180, 22, 'Short-term', 9.4, bold=True) + t(180, 56, 'Hive writes a nightly ORC/Parquet snapshot', 8.2, 'ink2') + cap('Spark reads the snapshot.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Or use HWC / JDBC', 9.4, bold=True) + t(180, 56, 'Hive Warehouse Connector on Cloudera', 8.2, 'ink2') + cap('Hive reads, Spark receives rows.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Long-term', 9.4, 'acc', bold=True) + t(180, 56, 'convert shared tables to Iceberg', 8.2, 'ink2') + cap('One table format all engines support.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'An “empty” table in Spark',
              'A frequent incident on mixed Hive/Spark platforms. (Behaviour from our lab; options typical.)',
              'ACID across engines', 'Spark returned 0 rows from a Hive ACID table; snapshots, connectors or Iceberg solve it', [e1, e2, e3, e4, e5],
              ['Spark shows no rows.',
               'The table is Hive full-ACID.',
               'Export a plain snapshot.',
               'Or read through Hive.',
               'Move shared tables to Iceberg.'],
              hid='scenario-empty')

# ---- scenario 2: BI on Trino
b1 = (t(180, 22, 'Move dashboards to Trino', 9.4, bold=True) + t(180, 56, 'same Hive tables, faster answers', 8.4, 'ink2') + cap('Trino ≈ 0.75 s vs Hive ≈ 1.6 s in our lab.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Configure catalogs', 9.4, bold=True) + t(180, 56, 'hive.properties · iceberg.properties', 8.4, 'ink', mono=True) + cap('Plus file-system settings.', '', 'green', y=150, h=34))
b3 = (t(180, 22, 'Test every table type', 9.4, bold=True) + t(180, 56, 'counts in Hive vs Trino', 8.4, 'ink2') + cap('ACID was wrong in our lab.', '', 'amber', y=150, h=34))
b4 = (t(180, 22, 'Rewrite SQL', 9.4, bold=True) + t(180, 56, "DATE '…' literals, ANSI functions", 8.4, 'ink', mono=True) + cap('Dialect differences.', '', 'blue', y=150, h=34))
b5 = (t(180, 22, 'Keep Hive for loads', 9.4, 'acc', bold=True) + t(180, 56, 'Hive ETL → Trino BI on the same metastore', 8, 'ink2') + cap('A very common split.', '', 'green', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Dashboards on Trino, loads in Hive',
              'A common architecture, with the checks our lab says are needed.',
              'Hive + Trino', 'Trino reads Hive tables for BI after catalog setup, per-table verification and SQL rewrites; Hive keeps the ETL', [b1, b2, b3, b4, b5],
              ['Trino for interactive dashboards.',
               'Configure the catalogs.',
               'Verify counts per table type.',
               'Adapt the SQL.',
               'Hive keeps the loads.'],
              hid='scenario-trino')

# ---- scenario 3: upgrade compatibility matrix
u1 = (t(180, 22, 'Upgrading the metastore to Hive 4', 9.4, bold=True) + t(180, 56, 'what breaks in other engines?', 8.4, 'ink2') + cap('Our Step 1 is the warning.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Inventory clients', 9.4, bold=True) + t(180, 56, 'Spark versions, Trino, Impala, Flink, tools', 8.2, 'ink2') + cap('Each has its own metastore client.', '', 'green', y=150, h=34))
u3 = (t(180, 22, 'Test on a copy', 9.4, bold=True) + t(180, 56, 'restored metastore (Lesson 10.1) + each engine', 8, 'ink2') + cap('Counts per table type.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Fix clients', 9.4, bold=True) + t(180, 56, 'spark.sql.hive.metastore.version / jars', 8.2, 'ink', mono=True) + cap('Or upgrade the engine.', '', 'amber', y=150, h=34))
u5 = (t(180, 22, 'Publish a matrix', 9.4, 'acc', bold=True) + t(180, 56, 'engine × table type × supported?', 8.2, 'ink2') + cap('Like the table in this lesson.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'A compatibility matrix before an upgrade',
              'How platform teams avoid surprises. (Typical practice; failures as seen in our lab.)',
              'Compatibility testing', 'List every metastore client, test each against a restored copy, fix client versions and publish an engine-by-table-type matrix', [u1, u2, u3, u4, u5],
              ['A metastore upgrade affects all engines.',
               'List all clients.',
               'Test on a restored copy.',
               'Adjust client versions.',
               'Share a support matrix.'],
              hid='scenario-matrix')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>One catalogue, three readers</h2>
  <p>Left: real outputs. Right: why the answers agree or differ.</p>
''' + two + '''
  <p>Three live scenarios follow: an empty table in Spark, BI on Trino, and a compatibility matrix.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Multi-engine platforms at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'ETL + BI', 11, 'green', bold=True) + t(60, 58, 'split', 7.4, 'ink2'),
    '1. Hive for loads, Trino for dashboards',
    'Many companies run nightly Hive or Spark ETL and serve analysts through Trino on the same metastore.',
    ['Hive ETL', '*metastore', 'Trino BI']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'ML', 12, 'blue', bold=True) + t(60, 58, 'features', 7.4, 'ink2'),
    '2. Data science on warehouse tables',
    'Spark notebooks read Hive tables for feature engineering and write results back for Hive and BI.',
    ['Hive tables', '*Spark', 'Features']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'federate', 10, 'violet', bold=True) + t(60, 58, 'Trino', 7.4, 'ink2'),
    '3. Federated queries',
    'Trino joins Hive tables with PostgreSQL, MySQL or Kafka in one query without copying data.',
    ['Hive + RDBMS', '*Trino', 'One answer']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'Iceberg', 11, 'acc', bold=True) + t(60, 58, 'shared', 7.4, 'ink2'),
    '4. Shared tables in Iceberg',
    'Tables written by several engines move to Iceberg, which all major engines read and write consistently.',
    ['Many writers', '*Iceberg', 'Consistent']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'tests', 11, 'acc', bold=True) + t(60, 58, 'interop', 7.4, 'ink2'),
    '5. Interoperability tests in CI',
    'Platform teams run the same count and checksum queries in every engine after each upgrade.',
    ['Upgrade', '*test suite', 'Trust']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> ACID tables (<a href="../../07-acid-and-iceberg/01-acid-tables-update-delete/">7.1</a>), Iceberg (<a href="../../07-acid-and-iceberg/03-compaction-and-iceberg/">7.3</a>) and the metastore (<a href="../../10-administration-and-security/01-metastore-administration/">10.1</a>).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
