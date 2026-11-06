import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
BODY = body(HERE)

META = dict(
    module='02-hiveql', lesson='01-databases-and-tables', n='2.1',
    module_label='Module 2 · Tables and data',
    title='Databases and tables',
    desc='Create Hive databases and tables: CREATE DATABASE with comments and properties, CREATE TABLE with columns, row format, file format and TBLPROPERTIES, USE, SHOW, DESCRIBE, DESCRIBE FORMATTED, SHOW CREATE TABLE, CREATE TABLE LIKE, temporary tables, Hive 4 table translation and real error messages. All outputs recorded from Hive 4.2.1.',
    og_desc='A database is a named shelf, a table is a labelled box. Create both, load 2,000 customers and read everything Hive knows about them.',
    minutes=30, level='Beginner → Intermediate',
    lead='Every Hive project starts with two statements: <code>CREATE DATABASE</code> and <code>CREATE TABLE</code>. In this lesson you build the TiffinGo database and its customers table, load 2,000 customers, and learn to read <code>DESCRIBE FORMATTED</code> and <code>SHOW CREATE TABLE</code>, where you will meet Hive 4’s table translation. <b>All outputs are real</b>, from the Hive 4.2.1 lab.',
    chips=['Real Hive 4.2.1 outputs', '3 animations', 'DESCRIBE FORMATTED guide', 'Runs in your browser (Python)'],
)

MAIN = '''# A tiny metastore: databases hold tables, tables hold metadata
warehouse = "file:/opt/hive/data/warehouse"
metastore = {"default": {}}

def create_database(db):
    if db in metastore:
        print("already exists:", db); return
    metastore[db] = {}
    print("created", db, "at", f"{warehouse}/{db}.db")

def create_table(db, table, columns):
    if table in metastore[db]:
        raise ValueError(f"AlreadyExistsException: {db}.{table}")
    metastore[db][table] = {"columns": columns, "location": f"{warehouse}/{db}.db/{table}"}

create_database("tiffingo")
create_table("tiffingo", "customers", [("customer_id", "int"), ("name", "string"), ("plan", "string")])
for col, typ in metastore["tiffingo"]["customers"]["columns"]:
    print(f"{col:12} {typ}")
print(metastore["tiffingo"]["customers"]["location"])
'''
RUN = dict(
    heading='Run the code: a metastore in a dictionary',
    intro='<p>A Python dictionary plays the metastore: databases contain tables, tables contain columns and a location. It is a toy, but it follows the same rules: unique names per database, default folders under the warehouse, and metadata separate from data. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('metastore[db] = {}', 'Like a row in <code>DBS</code>: the database exists as soon as it is recorded. Hive also creates the folder <code>tiffingo.db</code>.'),
        ('raise ValueError(f"AlreadyExistsException: {db}.{table}")', 'Table names are unique within a database. The real error is <code>AlreadyExistsException</code>.'),
        ('"location": f"{warehouse}/{db}.db/{table}"', 'Without a LOCATION clause, a table folder is created inside its database folder.'),
    ],
    tasks=[
        dict(label='1 · Create and describe', hint='Press <b>Run</b>. Then add a <code>joined_on date</code> column and run again.', code=None),
        dict(label='2 · Same name, two databases', hint='<b>Predict first:</b> can <code>orders</code> exist in both <code>tiffingo_raw</code> and <code>tiffingo</code>? Run to check.',
             code='''metastore = {"tiffingo_raw": {}, "tiffingo": {}}
for db in metastore:
    metastore[db]["orders"] = {"location": f"/warehouse/{db}.db/orders"}
for db, tables in metastore.items():
    for t, meta in tables.items():
        print(f"{db}.{t:7} -> {meta['location']}")
'''),
        dict(label='3 · Qualified names', hint='Resolve names the way Hive does: <code>db.table</code> is used as is, a bare name uses the current database. Change <code>current</code> to <code>"default"</code>.',
             code='''current = "tiffingo"
def resolve(name):
    return name if "." in name else f"{current}.{name}"
for n in ["customers", "tiffingo_raw.orders", "orders"]:
    print(f"{n:20} -> {resolve(n)}")
'''),
        dict(label='4 · DROP DATABASE rules', hint='A non-empty database cannot be dropped without CASCADE. Try <code>cascade=True</code>.',
             code='''metastore = {"tiffingo": {"customers": {}, "orders": {}}}
def drop_database(db, cascade=False):
    if metastore[db] and not cascade:
        return f"InvalidOperationException: Database {db} is not empty."
    n = len(metastore.pop(db))
    return f"dropped {db} and {n} tables"
print(drop_database("tiffingo"))
'''),
        dict(label='5 · Spot the error', hint='The script creates the same table twice and stops, just like <code>beeline -f</code>. Make it re-runnable with an <code>if not exists</code> check.', expect='error',
             code='''tables = {}
def create_table(name):
    if name in tables:
        raise RuntimeError(f"AlreadyExistsException: {name} already exists")
    tables[name] = []
create_table("customers")
create_table("customers")      # a re-run of the same script
print("done")
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: inspect databases and tables',
    intro='<p>Run these in Beeline on the lab from Lesson 1.5. <b>The outputs are real</b>, recorded from Hive 4.2.1; wide columns are trimmed with “…”.</p>',
    items=[
        dict(title='1 · Patterns, columns and the current database', cmd="SHOW DATABASES LIKE 'tif%';\nUSE tiffingo;\nSHOW TABLES LIKE 'cust%';\nDESCRIBE customers plan;\nSELECT current_database();", file='Beeline',
             output='''+----------------+
| database_name  |
+----------------+
| tiffingo       |
+----------------+
+------------+
|  tab_name  |
+------------+
| customers  |
+------------+
+-----------+------------+--------------------+
| col_name  | data_type  |      comment       |
+-----------+------------+--------------------+
| plan      | string     | from deserializer  |
+-----------+------------+--------------------+
+-----------+
|    _c0    |
+-----------+
| tiffingo  |
+-----------+''',
             note='<code>DESCRIBE table column</code> (space, not a dot) describes one column. For a single column Hive 4 prints “from deserializer” instead of your comment; the full <code>DESCRIBE customers</code> shows it.'),
        dict(title='2 · A temporary table', cmd='CREATE TEMPORARY TABLE tmp_city (city STRING);\nSHOW TABLES;', file='Beeline',
             output='''+-------------+
|  tab_name   |
+-------------+
| customers   |
| orders_ext  |
| t_acid      |
| tmp_city    |
+-------------+''',
             note='<code>tmp_city</code> is listed only in your session and disappears when you disconnect. (Our lab already had <code>orders_ext</code> and <code>t_acid</code> from Lesson 2.2.)'),
        dict(title='3 · The folders behind the tables', cmd='docker exec hiveserver2 ls -la /opt/hive/data/warehouse/tiffingo.db/customers', file='Terminal',
             output='''total 104
drwxr-xr-x 2 hive hive  4096 Oct 26 10:22 .
drwxr-xr-x 4 hive hive  4096 Oct 26 10:22 ..
-rw-r--r-- 1 hive hive 91618 Oct 26 10:22 customers.csv
-rw-r--r-- 1 hive hive   724 Oct 26 10:22 .customers.csv.crc''',
             note='The table’s data is just the file you loaded, 91,618 bytes. The <code>.crc</code> file is a checksum written by Hadoop’s local file system client; on HDFS checksums are kept by the DataNodes instead.'),
    ],
)

TRACE = dict(
    heading='Creating a database and a table, one line at a time',
    intro='<p>Watch the dictionary that plays the metastore grow: a database entry first, then a table entry with its columns and default location.</p>',
    code='''warehouse = "/warehouse"
metastore = {}
metastore["tiffingo"] = {}
cols = [("customer_id", "int"), ("plan", "string")]
loc = f"{warehouse}/tiffingo.db/customers"
metastore["tiffingo"]["customers"] = {"cols": cols, "loc": loc}
print(metastore["tiffingo"]["customers"]["loc"])
''',
    notes={3: 'DBS :: CREATE DATABASE: a new entry, and in real Hive a folder tiffingo.db.', 6: 'TBLS :: CREATE TABLE: columns and location recorded. No data has moved.'},
)

WORKED_INTRO = 'Three jobs a data engineer does in the first month: decide where tables will live, generate a CREATE TABLE from a sample file, and pull the important facts out of DESCRIBE FORMATTED.'
EXAMPLES = [
    dict(level='b', tag='Layout · paths', title='Where will each table’s files go?',
         problem='<p>The warehouse is <code>hdfs://nn:8020/warehouse</code>. Print the default folder for each table in the plan below, and the folder for a table that has its own LOCATION.</p>',
         inp='tiffingo.customers · tiffingo.orders · tiffingo_mart.daily_sales · tiffingo_raw.orders with LOCATION /landing/orders',
         approach=['Default folder = warehouse / db.db / table.', 'If a LOCATION is given, use it as it is.', 'Print one line per table.'],
         code='''warehouse = "hdfs://nn:8020/warehouse"
plan = [("tiffingo", "customers", None), ("tiffingo", "orders", None),
        ("tiffingo_mart", "daily_sales", None), ("tiffingo_raw", "orders", "/landing/orders")]
for db, table, location in plan:
    path = location or f"{warehouse}/{db}.db/{table}"
    print(f"{db + '.' + table:26} {path}")
''', notes={4: 'Choose :: LOCATION wins; otherwise the default folder is used.'},
         tryit='Change the warehouse to an object store path such as s3a://tiffingo-lake/warehouse. The SQL stays the same; only the paths change.'),
    dict(level='i', tag='DDL · generation', title='Generate CREATE TABLE from a CSV sample',
         problem='<p>A new file arrives with a header and one sample row. Guess a Hive type for each column (int, double, date or string) and print a CREATE TABLE statement with a comma delimiter and a header-skip property.</p>',
         inp='restaurant_id,name,city,rating,opened_on\\n7,Patil Mess,Pune,4.3,2021-06-01',
         approach=['Split header and sample row.', 'Test each value: integer, decimal, yyyy-mm-dd date, otherwise string.', 'Build the column list and the statement.'],
         code='''header = "restaurant_id,name,city,rating,opened_on".split(",")
sample = "7,Patil Mess,Pune,4.3,2021-06-01".split(",")
def guess(v):
    if v.isdigit(): return "INT"
    if v.replace(".", "", 1).isdigit(): return "DOUBLE"
    if len(v) == 10 and v[4] == "-" and v[7] == "-": return "DATE"
    return "STRING"
cols = ",\\n  ".join(f"{h} {guess(v)}" for h, v in zip(header, sample))
print(f"CREATE TABLE restaurants (\\n  {cols})")
print("ROW FORMAT DELIMITED FIELDS TERMINATED BY ','")
print("TBLPROPERTIES ('skip.header.line.count'='1');")
''', notes={8: 'Build :: One “name TYPE” per column, joined with commas.'},
         tryit='Change the rating to “4,3” (a decimal comma, common in some exports). The guess becomes STRING, and in Hive that column would also break the comma delimiter. Always check samples before trusting a guess.'),
    dict(level='a', tag='Metadata · audit', title='Pull facts from DESCRIBE FORMATTED',
         problem='<p>An audit script saves <code>DESCRIBE FORMATTED</code> output for each table. From the real lines below, extract the table type, location, purge flag and size, and decide what a DROP would do.</p>',
         inp='Real lines from DESCRIBE FORMATTED customers (Hive 4.2.1)',
         approach=['Split each line on “|” and strip spaces.', 'Store “key: value” pairs (the first two cells) in a dictionary.', 'Apply the rule: managed, or external with purge = TRUE, means DROP deletes files.'],
         code='''lines = """| Location:                     | file:/opt/hive/data/warehouse/tiffingo.db/customers | NULL |
| Table Type:                   | EXTERNAL_TABLE                                     | NULL |
|                               | external.table.purge                               | TRUE |
|                               | totalSize                                          | 91618 |""".splitlines()
info = {}
for ln in lines:
    cells = [c.strip() for c in ln.strip("|").split("|")]
    key = cells[0].rstrip(":") or cells[1]
    info[key] = cells[1] if cells[0] else cells[2]
deletes = info["Table Type"] == "MANAGED_TABLE" or info.get("external.table.purge") == "TRUE"
print(info)
print("DROP deletes the files:", deletes)
''', notes={9: 'Rule :: Purge turns an external table’s DROP into a delete.'},
         tryit='Change TRUE to FALSE on the purge line. Now DROP would keep the files. That one property decides whether a DROP is reversible.'),
]

QUIZ = mix([
    dict(q='Beginner: Where is the default folder of a new database called tiffingo?', options=['<warehouse>/tiffingo', '<warehouse>/tiffingo.db', '/tmp/tiffingo', 'Inside the metastore database'], answer=1,
         why='Hive appends .db: in our lab file:/opt/hive/data/warehouse/tiffingo.db.'),
    dict(q='Beginner: Which statement shows the columns of a table?', options=['SHOW TABLES', 'DESCRIBE customers', 'USE customers', 'SELECT COLUMNS customers'], answer=1,
         why='DESCRIBE lists column names, types and comments; DESCRIBE FORMATTED adds storage details.'),
    dict(q='Beginner: Does CREATE TABLE copy any data?', options=['Yes, it copies all files in the warehouse', 'No, it records metadata and creates an empty folder', 'Yes, but only the first block', 'Only for TEXTFILE tables'], answer=1,
         why='CREATE TABLE writes to the metastore; data arrives later with LOAD, INSERT or files placed in the location.'),
    dict(q='Intermediate: Which property makes queries ignore the first line of a CSV file?', options=['skip.first.line=true', 'skip.header.line.count=1', 'header=true', 'serialization.header=1'], answer=1,
         why="TBLPROPERTIES ('skip.header.line.count'='1') skipped the header, so the plans added up to exactly 2,000 customers."),
    dict(q='Intermediate: In Hive 4.2.1 which pattern matched the tiffingo database?', options=["LIKE 'tif*'", "LIKE 'tif%'", "LIKE 'tif?'", "LIKE tif"], answer=1,
         why='SQL wildcards are used: % for any characters. In our run tif* matched nothing.'),
    dict(q='Intermediate: DROP DATABASE tiffingo fails with “Database tiffingo is not empty”. What does adding CASCADE do?', options=['Ignores the error and keeps everything', 'Drops every table in the database, then the database', 'Moves the tables to default', 'Only drops empty tables'], answer=1,
         why='CASCADE drops all tables first. For managed or purge tables their data is deleted too, so use it with care.'),
    dict(q='Advanced: After CREATE TABLE customers (… ) STORED AS TEXTFILE, DESCRIBE FORMATTED shows EXTERNAL_TABLE. Why?', options=['A bug in Beeline', 'Hive 4 translates non-transactional managed tables into external tables with external.table.purge=TRUE', 'TEXTFILE tables are always external in every Hive version', 'Because the database has a comment'], answer=1,
         why='With hive.create.as.acid=false, Hive 4 stores non-ACID managed tables as external purge tables (TRANSLATED_TO_EXTERNAL=TRUE). DROP still deletes the data.'),
    dict(q='Advanced: Which output can you save in Git to recreate a table exactly?', options=['DESCRIBE', 'SHOW TABLES', 'SHOW CREATE TABLE', 'SHOW DATABASES'], answer=2,
         why='SHOW CREATE TABLE prints the full DDL with SerDe, formats, location and properties filled in.'),
])

REVISION = [
    '<b>Database</b> = namespace; metastore row in <code>DBS</code>; folder <code>&lt;warehouse&gt;/&lt;db&gt;.db</code>. Synonym: schema.',
    '<b>Table</b> = columns + types + row format (SerDe, delimiter) + file format + location + type + TBLPROPERTIES.',
    '<code>CREATE DATABASE IF NOT EXISTS db COMMENT … WITH DBPROPERTIES (…)</code> · <code>USE db</code> · <code>SHOW DATABASES LIKE \'tif%\'</code>.',
    '<code>DESCRIBE t</code> (columns) · <code>DESCRIBE FORMATTED t</code> (everything) · <code>SHOW CREATE TABLE t</code> (full DDL).',
    'Forms: plain, <code>LIKE</code> (shape only), CTAS (Lesson 2.5), <code>EXTERNAL</code> (2.2), <code>TEMPORARY</code> (session only).',
    "<code>TBLPROPERTIES ('skip.header.line.count'='1')</code> skips CSV headers.",
    'Hive 4: non-transactional <code>CREATE TABLE</code> → <code>EXTERNAL_TABLE</code> + <code>external.table.purge=TRUE</code> + <code>TRANSLATED_TO_EXTERNAL</code>.',
    'Errors: <code>Table not found</code> (compile time), <code>AlreadyExistsException</code>, <code>Database … is not empty</code> (use CASCADE carefully). Use qualified names <code>db.table</code> in scripts.',
]
FAQ = [
    ('Is a Hive database the same as a database in MySQL?', 'Not quite. In MySQL a database contains tables whose data the MySQL server stores and manages. In Hive a database is mainly a namespace and a default folder; the data is ordinary files in HDFS or object storage that other tools can also read. Hive treats DATABASE and SCHEMA as synonyms.'),
    ('What is the difference between DESCRIBE, DESCRIBE EXTENDED and DESCRIBE FORMATTED?', 'DESCRIBE lists columns, types and comments. DESCRIBE EXTENDED adds all table details in one long, hard-to-read line. DESCRIBE FORMATTED shows the same details neatly in sections: detailed table information (location, owner, type, parameters) and storage information (SerDe, input/output format, buckets). Engineers use FORMATTED.'),
    ('Why did my CREATE TABLE become an EXTERNAL_TABLE?', 'Hive 4 keeps “managed” tables for transactional (ACID) data. When hive.create.as.acid is false and the table is not transactional, the metastore stores it as an external table with external.table.purge=TRUE and marks it TRANSLATED_TO_EXTERNAL=TRUE. It behaves like a classic managed table for DROP (files are deleted), but it is not ACID. Lesson 2.2 compares the types.'),
    ('Can I rename a database?', 'Not with a simple command in most Hive versions; you can change a database’s properties, owner and (in newer versions) location with ALTER DATABASE. Teams usually create the new database and move or recreate tables. Choose database names carefully at the start.'),
    ('Should I use USE or qualified names?', 'Use USE when exploring interactively. In scheduled scripts, views and shared code, write db.table everywhere so the meaning does not depend on the current database. Many teams also pass the database name as a variable (--hivevar db=…) to run the same script in dev and production.'),
]

PRACTICE_INTRO = 'Programs that practise the rules of databases and tables: names, folders, DDL text and metadata.'
PROBLEMS = [
    dict(level='easy', title='Database folder', stmt='Print the default folder for databases sales and hr under warehouse /warehouse.', inp='sales, hr',
         code='''for db in ["sales", "hr"]:
    print(f"/warehouse/{db}.db")
''', explain='Hive adds “.db” to the database name. The default database is the exception: its tables sit directly in the warehouse folder.'),
    dict(level='easy', title='Lower-case names', stmt='Hive stores names in lower case. Print how CREATE TABLE Customers, CUSTOMERS and customers would be stored, and whether they clash.', inp='Customers · CUSTOMERS · customers',
         code='''names = ["Customers", "CUSTOMERS", "customers"]
stored = [n.lower() for n in names]
print(stored, "| clash:", len(set(stored)) < len(stored))
''', explain='All three are customers, so the second CREATE would fail with AlreadyExistsException.'),
    dict(level='easy', title='Qualify a name', stmt='Write a function that returns db.table, using the current database when no database is given.', inp='current = tiffingo · names: orders, mart.daily_sales',
         code='''current = "tiffingo"
def qualify(n):
    return n if "." in n else f"{current}.{n}"
print(qualify("orders"), qualify("mart.daily_sales"))
''', explain='tiffingo.orders and mart.daily_sales. The same rule decides which table an unqualified query reads.'),
    dict(level='medium', title='Build a CREATE DATABASE statement', stmt='Generate CREATE DATABASE IF NOT EXISTS with a comment and two DBPROPERTIES from a dictionary.', inp="name tiffingo_mart · comment 'Report tables' · owner_team=analytics, layer=gold",
         code='''name, comment = "tiffingo_mart", "Report tables"
props = {"owner_team": "analytics", "layer": "gold"}
p = ", ".join(f"'{k}'='{v}'" for k, v in props.items())
print(f"CREATE DATABASE IF NOT EXISTS {name}\\n  COMMENT '{comment}'\\n  WITH DBPROPERTIES ({p});")
''', explain='Generating DDL from configuration keeps dev, test and production identical.'),
    dict(level='medium', title='Rows after skipping a header', stmt='A CSV has 2,001 lines including the header. How many rows does COUNT(*) return with and without skip.header.line.count = 1?', inp='2,001 lines',
         code='''lines = 2001
print("with skip   :", lines - 1)
print("without skip:", lines, "(the header becomes a row with NULL customer_id)")
''', explain='2,000 versus 2,001. Without the property the header line is read as data; “customer_id” cannot be an INT, so that column is NULL in an extra row.'),
    dict(level='medium', title='Find temporary clutter', stmt='From a list of table names, print those that look temporary (start with tmp_ or test, or end with _old or _bkp).', inp='orders, tmp_city, test1, customers_old, menu, orders_bkp',
         code='''names = ["orders", "tmp_city", "test1", "customers_old", "menu", "orders_bkp"]
junk = [n for n in names if n.startswith(("tmp_", "test")) or n.endswith(("_old", "_bkp"))]
print(junk)
''', explain='Teams run checks like this on SHOW TABLES output to keep shared databases clean, and move experiments to sandboxes.'),
    dict(level='business', title='Storage per database', stmt='totalSize values (bytes) from DESCRIBE FORMATTED are given per table. Sum them per database and print in MB.', inp='tiffingo.customers 91,618 · tiffingo.orders 3,086,726 · tiffingo_raw.orders 3,086,726',
         code='''sizes = {"tiffingo.customers": 91618, "tiffingo.orders": 3086726, "tiffingo_raw.orders": 3086726}
per_db = {}
for name, b in sizes.items():
    db = name.split(".")[0]
    per_db[db] = per_db.get(db, 0) + b
for db, b in per_db.items():
    print(f"{db:13} {b / 1024 / 1024:.2f} MB")
''', explain='3.03 MB and 2.94 MB. The same sum on a real warehouse shows which layer costs most storage. totalSize is only reliable when statistics are up to date.'),
    dict(level='business', title='Naming policy check', stmt='The policy says table names are lower_snake_case, start with a letter and are at most 40 characters. Check these names.', inp='daily_sales, DailySales, 2024_orders, customer_lifetime_value_by_city_and_month_v2',
         code='''import re
names = ["daily_sales", "DailySales", "2024_orders", "customer_lifetime_value_by_city_and_month_v2"]
for n in names:
    ok = bool(re.fullmatch(r"[a-z][a-z0-9_]*", n)) and len(n) <= 40
    print(f"{n:46} {'ok' if ok else 'violates policy'}")
''', explain='Only daily_sales passes. A check like this in code review avoids names that are hard to type, sort or search.'),
]

SCN_INTRO = 'Interviewers use simple DDL to see whether you understand what Hive stores and where. These come up for freshers and mid-level roles.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“What happens when you create a table in Hive?”',
        'The interviewer asks you to explain CREATE TABLE in Hive to someone who knows only MySQL.',
        'do you separate metadata from data?',
        '''<ol>
          <li>Hive writes the table’s definition to the metastore: columns and types, row format (SerDe and delimiter), file format, location, table type and properties.</li>
          <li>It creates an empty folder (unless a LOCATION is given). No data is moved or checked.</li>
          <li>Data is added later by LOAD DATA, INSERT or by placing files in the location; the schema is applied when the data is read (schema on read).</li>
        </ol>''', 'saying the table is “created in Hive’s storage engine”; Hive has no storage engine of its own.') +
    scn('Data engineering · investigation', 'Fresher', 'Where does this table really read from?',
        'A report shows yesterday’s numbers twice. You suspect the table is reading the wrong folder.',
        'do you know the commands that reveal a table’s storage?',
        '''<ul>
          <li>Run <code>DESCRIBE FORMATTED</code> (or <code>SHOW CREATE TABLE</code>) and read Location, Table Type, SerDe and properties.</li>
          <li>List the location (<code>hdfs dfs -ls</code>) and check for duplicate or unexpected files.</li>
          <li>Check that the report uses a qualified name, so it is not reading a same-named table in another database.</li>
        </ul>''', 'rewriting the query before checking what the table points at.') +
    scn('Platform · Hive 4 upgrade', 'Mid-level', 'Why did our managed tables become external?',
        'After an upgrade to Hive 4, DESCRIBE FORMATTED shows EXTERNAL_TABLE with TRANSLATED_TO_EXTERNAL for tables created with plain CREATE TABLE. A colleague worries data will be kept after DROP.',
        'do you know Hive’s managed vs external rules in version 3 and later?',
        '''<ul>
          <li>Since Hive 3, managed tables are meant for ACID (transactional) data. Non-transactional managed tables are translated to external tables with <code>external.table.purge=TRUE</code>.</li>
          <li>Because purge is TRUE, DROP still deletes the files: behaviour matches the old managed table.</li>
          <li>If the team wants ACID features (UPDATE, DELETE, MERGE), create tables as transactional ORC, or set <code>hive.create.as.acid</code> as a policy decision.</li>
        </ul>''', 'claiming it is a bug or that DROP is now safe.') +
    scn('Operations · safety', 'Mid-level', 'Someone ran DROP DATABASE … CASCADE',
        'A sandbox clean-up script ran DROP DATABASE tiffingo CASCADE on the wrong environment.',
        'do you understand the blast radius and prevention?',
        '''<ol>
          <li>CASCADE dropped every table; managed and purge-enabled external tables lost their files, plain external tables kept them.</li>
          <li>Recovery: HDFS trash or snapshots, object-store versioning, or a metastore database backup plus re-creating DDL from Git.</li>
          <li>Prevention: separate permissions per database, no CASCADE in automated scripts, environment name passed explicitly and checked, and backups of the metastore.</li>
        </ol>''', '“just restore the metastore”: metadata without files, or files without metadata, are both incomplete.')
)
