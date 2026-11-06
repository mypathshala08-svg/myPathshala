import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep

# ---------------------------------------------------------------- story
def folder(x, y, w, label, tone='card', size=8):
    return box(x, y, w, 22, tone) + t(x + 8, y + 14.5, label, size, anchor='start', mono=True)
sc = (box(12, 14, 196, 124, 'red') + t(110, 30, 'Before: everything in default', 9, 'red', bold=True) +
      ''.join(t(24 + (k % 2) * 92, 50 + (k // 2) * 15, nm, 7.4, 'ink2', anchor='start', mono=True) for k, nm in enumerate(['orders', 'orders_v2', 'orders_final', 'cust', 'customers_new', 'test1', 'kabir_tmp', 'menu', 'menu_old', 'rest']))
      + arrow(214, 76, 252, 76, 'ink3', 2.2) +
      box(258, 14, 370, 124, 'green') + t(443, 30, 'After: one database per subject', 9, 'green', bold=True) +
      ''.join(box(270 + k * 120, 42, 110, 84, tone) + t(325 + k * 120, 58, db, 8.4, bold=True, mono=True) +
              ''.join(t(280 + k * 120, 76 + j * 14, tb, 7.4, 'ink2', anchor='start', mono=True) for j, tb in enumerate(tbls))
              for k, (db, tone, tbls) in enumerate([('tiffingo_raw', 'card', ['orders', 'customers', 'restaurants']), ('tiffingo', 'acc', ['orders', 'customers', 'daily_sales']), ('kabir_sandbox', 'blue', ['tmp_city', 'test1'])])))
scene_svg = scene('Ten confusingly named tables in the default database are reorganised into three databases: raw data, cleaned company tables and a personal sandbox.', sc,
                  'A database is a <tspan font-weight="700" class="s-acc">named shelf</tspan>: same table names, no clashes, clear owners.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Which of these five orders tables is the real one?”</h2>
  <div class="story">
    <p class="narration">On his second week at TiffinGo, Kabir runs <code>SHOW TABLES</code> and gets 140 names: <code>orders</code>, <code>orders_v2</code>, <code>orders_final</code>, <code>orders_final_new</code>, <code>kabir_tmp</code>… Everyone created tables in <code>default</code>. Nobody knows which <code>orders</code> the finance report reads.</p>

{scene_svg}

K> Sir, can I just call my table <code>orders</code>? Someone already took that name.
A> In one <b>database</b> a name can exist only once. Hive lets you make many databases: think of them as <b>shelves in a library</b>. The raw files on one shelf, the cleaned company tables on another, your experiments on your own.
R> Is a database a real thing on disk, or only a name?
A> Both. In the metastore it is a row in the <code>DBS</code> table. On disk it is a folder, <code>tiffingo.db</code>, inside the warehouse, and every table you create in it gets its own sub-folder.
K> And how do I see what a table really is, its columns, its format, where its files are?
A> Three commands: <code>DESCRIBE</code>, <code>DESCRIBE FORMATTED</code> and <code>SHOW CREATE TABLE</code>. Today you will create the TiffinGo database, a customers table, load 2,000 customers and read everything Hive knows about it. You will also meet a Hive 4 surprise: the table you create may not be the type you asked for.
  </div>
</section>
'''

# ---------------------------------------------------------------- definition
lv = '''
LEVELS> Databases and tables at three levels
L1> Shelves and labelled boxes
      <ul>
        <li>A <b>database</b> is a shelf with a name, like <code>tiffingo</code>.</li>
        <li>A <b>table</b> is a labelled box on that shelf: the label lists the columns (name, city, plan…), the box holds the data files.</li>
        <li>Two shelves can each have a box called <code>orders</code>; you say which one with <code>shelf.box</code>, for example <code>tiffingo.orders</code>.</li>
        <li><code>USE tiffingo;</code> means “I am standing at this shelf now”, so you can write just <code>orders</code>.</li>
      </ul>
L2> What Hive records
      <ul>
        <li><code>CREATE DATABASE</code> adds a row in the metastore table <code>DBS</code> and a folder <code>&lt;warehouse&gt;/&lt;name&gt;.db</code>, for us <code>file:/opt/hive/data/warehouse/tiffingo.db</code>.</li>
        <li><code>CREATE TABLE</code> records the <b>columns and types</b>, the <b>row format</b> (how a line becomes columns: a SerDe and a delimiter), the <b>file format</b> (TEXTFILE, ORC, Parquet…), the <b>location</b> and <b>table properties</b>.</li>
        <li>Without <code>LOCATION</code> the table folder is <code>&lt;db folder&gt;/&lt;table&gt;</code>.</li>
        <li>Names are not case-sensitive and are stored in lower case; <code>Customers</code> and <code>customers</code> are the same table.</li>
      </ul>
L3> Details that matter at work
      <ul>
        <li><b>Hive 4 table translation:</b> with the default <code>hive.create.as.acid=false</code>, a plain <code>CREATE TABLE</code> that is not transactional is stored as <code>EXTERNAL_TABLE</code> with <code>external.table.purge=TRUE</code> and <code>TRANSLATED_TO_EXTERNAL=TRUE</code>. It behaves like a managed table (DROP deletes data) but is not ACID. Lesson 2.2 explains why.</li>
        <li><b>Table properties</b> (<code>TBLPROPERTIES</code>) carry behaviour: <code>skip.header.line.count</code>, <code>transactional</code>, compression, statistics such as <code>numFiles</code> and <code>totalSize</code>.</li>
        <li><b>Patterns:</b> in Hive 4 <code>SHOW TABLES LIKE</code> uses SQL wildcards: <code>'cust%'</code> matched, <code>'tif*'</code> matched nothing in our run.</li>
        <li><b>Safety:</b> <code>DROP DATABASE</code> refuses a non-empty database unless you add <code>CASCADE</code>, which drops every table in it. <code>IF EXISTS</code> / <code>IF NOT EXISTS</code> make scripts safe to re-run.</li>
        <li><b>Temporary tables</b> live only for your session and are invisible to others.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Databases and tables in Hive</h2>
''' + def_block(
    'In Hive a <b>database</b> (synonym: <b>schema</b>) is a named namespace for tables, recorded in the metastore and mapped by default to the directory <code>&lt;warehouse&gt;/&lt;database&gt;.db</code>. A <b>table</b> is a metastore entry that describes data files by their <b>columns and data types</b>, <b>row format</b> (SerDe and delimiters), <b>storage format</b> (input/output format), <b>location</b>, <b>table type</b> (managed or external) and <b>table properties</b>. Tables are created with <code>CREATE TABLE</code> and inspected with <code>DESCRIBE [FORMATTED]</code> and <code>SHOW CREATE TABLE</code>.',
    'A database is a named folder for tables. A table is a description, kept in the metastore, of how to read some files as rows and columns: which columns, what types, how lines are split, what format the files have and where they are.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('DDL', 'Data Definition Language: statements that create, change or drop objects (CREATE, ALTER, DROP).'),
    ('Namespace', 'A space where each name is unique. Two databases can each contain a table called <code>orders</code>.'),
    ('Qualified name', '<code>database.table</code>, for example <code>tiffingo.customers</code>. Works from any current database.'),
    ('Warehouse', 'The root folder for databases and managed tables (<code>hive.metastore.warehouse.dir</code>).'),
    ('SerDe', 'Serializer/Deserializer: the code that turns a stored line into columns and back.'),
    ('TBLPROPERTIES', 'Key–value settings attached to a table, such as <code>skip.header.line.count</code>.'),
    ('DESCRIBE FORMATTED', 'Shows columns plus location, owner, table type, SerDe, formats and properties.'),
    ('SHOW CREATE TABLE', 'Prints the full DDL that would recreate the table, with every default filled in.'),
]) + '''

  <h3>Hive’s data units, from biggest to smallest</h3>
''' + table(['Unit', 'What it is', 'On disk', 'Lesson'], [
    ['<b>Database</b>', 'A namespace for tables', '<code>&lt;warehouse&gt;/tiffingo.db/</code>', 'This lesson'],
    ['<b>Table</b>', 'Rows with the same columns', '<code>…/tiffingo.db/orders/</code>', 'This lesson, 2.2'],
    ['<b>Partition</b>', 'A slice of a table by a column value, e.g. one day', '<code>…/orders/order_date=2026-10-25/</code>', 'Module 5'],
    ['<b>Bucket</b>', 'A file inside a table or partition, chosen by hash(column) mod N', '<code>…/order_date=…/000003_0</code>', 'Module 5'],
], minw=640) + '''

  <h3>The commands you will use every day</h3>
''' + table(['Statement', 'What it does', 'Real result in our lab'], [
    ["<code>CREATE DATABASE IF NOT EXISTS tiffingo COMMENT '…' WITH DBPROPERTIES (…)</code>", 'Create a database (once)', 'Folder <code>tiffingo.db</code> in the warehouse'],
    ["<code>SHOW DATABASES LIKE 'tif%'</code>", 'List databases matching a pattern', '<code>tiffingo</code>'],
    ['<code>USE tiffingo</code>', 'Set the current database', '<code>current_database()</code> → <code>tiffingo</code>'],
    ['<code>CREATE TABLE customers (…)</code>', 'Describe a new table', 'Row in <code>TBLS</code>, folder <code>tiffingo.db/customers</code>'],
    ['<code>DESCRIBE customers</code>', 'Columns, types, comments', '6 columns'],
    ['<code>DESCRIBE FORMATTED customers</code>', 'Everything Hive knows', 'Location, type, SerDe, properties'],
    ['<code>SHOW CREATE TABLE customers</code>', 'Full DDL with defaults', 'Shows it became <code>CREATE EXTERNAL TABLE</code>'],
    ['<code>DROP DATABASE tiffingo [CASCADE]</code>', 'Remove a database', 'Refused while tables exist, unless CASCADE'],
], minw=680) + lv + '''
EXAM> “Write the syntax of CREATE TABLE in Hive.” <code>CREATE [EXTERNAL] [TEMPORARY] TABLE [IF NOT EXISTS] [db.]name (col type [COMMENT '…'], …) [COMMENT '…'] [PARTITIONED BY (…)] [ROW FORMAT DELIMITED FIELDS TERMINATED BY ','] [STORED AS format] [LOCATION 'path'] [TBLPROPERTIES (…)];</code> Then name what goes to the metastore (schema, format, location) and that no data is moved by CREATE.
</section>
'''

# ---------------------------------------------------------------- types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Ways to create databases and tables</h2>
''' + cards([
    ('CREATE TABLE (columns)', 'You list the columns and types, and optionally row format, file format, location and properties. The most common form.', 'Everyday'),
    ('CREATE TABLE … LIKE', 'Copies another table’s definition (columns, format, properties) without any data. <code>CREATE TABLE customers_copy LIKE customers</code>.', 'Same shape'),
    ('CREATE TABLE … AS SELECT', 'CTAS: creates the table from a query’s result, columns and data together. Lesson 2.5.', 'From a query'),
    ('CREATE EXTERNAL TABLE', 'Describes files that something else owns; DROP leaves the files. Lesson 2.2.', 'Shared files'),
    ('CREATE TEMPORARY TABLE', 'Lives only for your session, visible only to you. Good for intermediate steps.', 'Scratch'),
    ('CREATE DATABASE … LOCATION', 'Puts a database folder somewhere other than the warehouse, for example a team bucket.', 'Custom place'),
]) + '''

  <h3>Typical database layout in a company</h3>
''' + table(['Database', 'Holds', 'Who writes', 'Example tables'], [
    ['<code>tiffingo_raw</code> (landing / bronze)', 'Files as they arrived, usually external tables', 'Ingestion jobs', '<code>orders</code>, <code>app_events</code>'],
    ['<code>tiffingo</code> (curated / silver)', 'Cleaned, typed, de-duplicated tables', 'Data engineering', '<code>orders</code>, <code>customers</code>'],
    ['<code>tiffingo_mart</code> (gold)', 'Aggregates for reports and dashboards', 'Analytics engineering', '<code>daily_city_sales</code>'],
    ['<code>sandbox_kabir</code>', 'Personal experiments, cleaned up regularly', 'One person', '<code>tmp_city</code>'],
], minw=620) + '''
TIP> Always <b>qualify</b> table names in scheduled scripts: <code>SELECT … FROM tiffingo.orders</code>. A script that relies on <code>USE</code> can read the wrong <code>orders</code> if someone changes the first line.
</section>
'''

# ---------------------------------------------------------------- steps
def cap_file(name):
    return open(CAP + name).read()
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Create the TiffinGo database and its first table</h2>
  <p>All outputs are real, from the Hive 4.2.1 lab of Lesson 1.5.</p>
''' + stepper([
    ('Step 1 · Create a database with a comment and an owner',
     code('sql', 'Beeline', "CREATE DATABASE IF NOT EXISTS tiffingo\n  COMMENT 'TiffinGo food delivery data'\n  WITH DBPROPERTIES ('owner_team'='data-eng');\nSHOW DATABASES;",
          '+----------------+\n| database_name  |\n+----------------+\n| default        |\n| tiffingo       |\n+----------------+'),
     '<code>IF NOT EXISTS</code> makes the statement safe to run twice. The comment and properties are stored in the metastore and help the next person understand what the database is for.'),
    ('Step 2 · See where it lives',
     code('sql', 'Beeline', 'DESCRIBE DATABASE EXTENDED tiffingo;',
          '| db_name  | comment                     | location                                  | owner_name | parameters            |\n| tiffingo | TiffinGo food delivery data | file:/opt/hive/data/warehouse/tiffingo.db | hive       | {owner_team=data-eng} |\n(columns trimmed)'),
     'The location is <code>&lt;warehouse&gt;/tiffingo.db</code>. On a real cluster it would start with <code>hdfs://</code> or <code>s3a://</code>. Hive 4 also prints a <code>managedlocation</code> column (same folder here).'),
    ('Step 3 · Create the customers table',
     code('sql', 'Beeline', "USE tiffingo;\nCREATE TABLE customers (\n  customer_id INT COMMENT 'unique id',\n  name STRING, city STRING, state STRING,\n  joined_on DATE,\n  plan STRING COMMENT 'Gold, Silver or Basic')\nCOMMENT 'TiffinGo customers'\nROW FORMAT DELIMITED FIELDS TERMINATED BY ','\nSTORED AS TEXTFILE\nTBLPROPERTIES ('skip.header.line.count'='1');\nDESCRIBE customers;",
          '+--------------+------------+------------------------+\n|   col_name   | data_type  |        comment         |\n+--------------+------------+------------------------+\n| customer_id  | int        | unique id              |\n| name         | string     |                        |\n| city         | string     |                        |\n| state        | string     |                        |\n| joined_on    | date       |                        |\n| plan         | string     | Gold, Silver or Basic  |\n+--------------+------------+------------------------+'),
     'Three parts: the columns, how a line is split (<code>ROW FORMAT DELIMITED</code> with commas), and the file format. <code>skip.header.line.count=1</code> tells readers to ignore the CSV header line.'),
    ('Step 4 · Put data in and query it',
     code('sql', 'Beeline', "LOAD DATA LOCAL INPATH '/data/tiffingo/customers/customers.csv' INTO TABLE customers;\nSELECT plan, COUNT(*) AS n FROM customers GROUP BY plan ORDER BY n DESC;",
          '+---------+------+\n|  plan   |  n   |\n+---------+------+\n| Basic   | 999  |\n| Gold    | 517  |\n| Silver  | 484  |\n+---------+------+'),
     '999 + 517 + 484 = 2,000 customers, so the header line was skipped correctly. <code>LOAD DATA</code> copied the file into the table folder (Lesson 2.5 covers loading in depth).'),
    ('Step 5 · Read everything Hive knows',
     code('sql', 'Beeline', 'DESCRIBE FORMATTED customers;',
          '| # Detailed Table Information  |                                                    |\n| Database:                     | tiffingo                                           |\n| Owner:                        | hive                                               |\n| Location:                     | file:/opt/hive/data/warehouse/tiffingo.db/customers |\n| Table Type:                   | EXTERNAL_TABLE                                     |\n| Table Parameters:             |                                                    |\n|                               | TRANSLATED_TO_EXTERNAL   TRUE                      |\n|                               | external.table.purge     TRUE                      |\n|                               | numFiles                 1                         |\n|                               | skip.header.line.count   1                         |\n|                               | totalSize                91618                     |\n| # Storage Information         |                                                    |\n| SerDe Library:                | org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe |\n| InputFormat:                  | org.apache.hadoop.mapred.TextInputFormat           |\n(trimmed)'),
     'Surprise: we wrote <code>CREATE TABLE</code>, but the type is <code>EXTERNAL_TABLE</code> with <code>TRANSLATED_TO_EXTERNAL</code> and <code>external.table.purge=TRUE</code>. Hive 4 stores non-transactional “managed” tables this way; DROP still deletes the files. Details in Lesson 2.2.'),
    ('Step 6 · Get the full DDL',
     code('sql', 'Beeline', 'SHOW CREATE TABLE customers;',
          "CREATE EXTERNAL TABLE `customers`(\n  `customer_id` int COMMENT 'unique id',\n  `name` string, … ,\n  `plan` string COMMENT 'Gold, Silver or Basic')\nCOMMENT 'TiffinGo customers'\nROW FORMAT SERDE\n  'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'\nWITH SERDEPROPERTIES (\n  'field.delim'=',',\n  'serialization.format'=',')\nSTORED AS INPUTFORMAT\n  'org.apache.hadoop.mapred.TextInputFormat'\nOUTPUTFORMAT\n  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'\nLOCATION\n  'file:/opt/hive/data/warehouse/tiffingo.db/customers'\nTBLPROPERTIES (\n  'TRANSLATED_TO_EXTERNAL'='TRUE',\n  'external.table.purge'='TRUE',\n  'skip.header.line.count'='1', …)"),
     '<code>ROW FORMAT DELIMITED … STORED AS TEXTFILE</code> is shorthand: Hive expands it into a SerDe class, an input format and an output format. Save this output in Git; it recreates the table exactly.'),
    ('Step 7 · Copy a shape and see the guard rails',
     code('sql', 'Beeline', "CREATE TABLE customers_copy LIKE customers;\nCREATE TABLE customers (id INT);\nSELECT * FROM tiffingo.customer;\nDROP DATABASE tiffingo;",
          cap_file('l21_exists.txt').split('; Query ID')[0] + '\n' + cap_file('l21_notfound.txt').split('; Query ID')[0] + '\n' + cap_file('l21_dropdb.txt').split('; Query ID')[0]),
     '<code>LIKE</code> copies the definition, not the rows. A duplicate name fails with <code>AlreadyExistsException</code>, a typo with <code>Table not found</code> at compile time, and a non-empty database cannot be dropped without <code>CASCADE</code>.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
def wh(dbs, hl=None):
    """warehouse folder tree at bottom-left; dbs: list of (db, [tables])"""
    o = box(10, 120, 168, 100, 'card') + t(18, 134, 'warehouse/', 8, 'ink', anchor='start', bold=True, mono=True)
    y = 148
    for db, tbls in dbs:
        o += t(26, y, db + '.db/', 7.6, 'acc' if hl == db else 'ink', anchor='start', mono=True, bold=hl == db); y += 12
        for tb in tbls:
            o += t(40, y, tb + '/', 7.4, 'green' if hl == tb else 'ink2', anchor='start', mono=True, bold=hl == tb); y += 12
    return o
def ms(rows, hl=None):
    """metastore tables at the right"""
    o = box(186, 120, 164, 100, 'violet') + t(268, 134, 'metastore (Postgres)', 8, bold=True)
    y = 150
    for k, (tab, val) in enumerate(rows):
        o += t(194, y, f'{tab:8} {val}', 7.2, 'acc' if hl == k else 'ink2', anchor='start', mono=True, bold=hl == k); y += 13
    return o
def head(title, sub=''):
    return t(180, 22, title, 9.4, bold=True) + (t(180, 38, sub, 8, 'ink2') if sub else '')
see = [
    term([("> CREATE DATABASE IF NOT EXISTS tiffingo", W), ("  COMMENT 'TiffinGo food delivery data';", W), ('No rows affected', G), ('> SHOW DATABASES;', W), ('| default        |', G), ('| tiffingo       |', G)]),
    term([('> USE tiffingo;', W), ('> CREATE TABLE customers (', W), ('    customer_id INT, name STRING, …)', W), ("  ROW FORMAT DELIMITED FIELDS TERMINATED BY ','", W), ("  TBLPROPERTIES ('skip.header.line.count'='1');", W), ('No rows affected', G)]),
    term([('> DESCRIBE customers;', W), ('| customer_id  | int     | unique id |', G), ('| name         | string  |           |', G), ('| city         | string  |           |', G), ('| joined_on    | date    |           |', G), ('| plan         | string  | Gold, …   |', G)]),
    term([("> LOAD DATA LOCAL INPATH '/data/…/customers.csv'", W), ('  INTO TABLE customers;', W), ('No rows affected', G), ('> SELECT plan, COUNT(*) AS n …', W), ('| Basic   | 999  |', G), ('| Gold    | 517  |', G), ('| Silver  | 484  |', G)]),
    term([('> DESCRIBE FORMATTED customers;', W), ('Table Type:  EXTERNAL_TABLE', Y), ('  TRANSLATED_TO_EXTERNAL  TRUE', Y), ('  external.table.purge    TRUE', Y), ('  numFiles 1   totalSize 91618', G), ('SerDe Library: …LazySimpleSerDe', G)]),
    term([('> CREATE TABLE customers (id INT);', W), ('Error: … AlreadyExistsException(message:', RD), ('  Table hive.tiffingo.customers already exists)', RD), ('> DROP DATABASE tiffingo;', W), ('Error: … Database tiffingo is not empty.', RD), ('  One or more tables exist.', RD)], size=7.6),
]
B1 = [
    head('A database = a metastore row + a folder') + box(40, 50, 280, 52, 'acc') + t(180, 70, "DBS: tiffingo · 'TiffinGo food delivery data'", 8, bold=True) + t(180, 88, 'owner_team = data-eng', 7.6, 'ink2', mono=True) +
    wh([('tiffingo', [])], 'tiffingo') + ms([('DBS', 'default'), ('DBS', 'tiffingo')], 1),
    head('A table = columns + format + location', 'Nothing is read or copied yet') + label_box(20, 48, 100, 56, ['columns', '6 names + types'], 'blue', 8) + label_box(130, 48, 100, 56, ['row format', 'split on “,”'], 'acc', 8) + label_box(240, 48, 100, 56, ['location', 'tiffingo.db/…'], 'green', 8) +
    wh([('tiffingo', ['customers'])], 'customers') + ms([('DBS', 'tiffingo'), ('TBLS', 'customers'), ('SDS', 'location, format'), ('COLS', '6 columns'), ('PARAMS', 'skip.header…')], 1),
    head('DESCRIBE reads only the metastore', 'No files, no Tez job: answers in milliseconds') + arrow(268, 116, 268, 64, 'violet', 2) + box(150, 40, 200, 22, 'violet') + t(250, 55, 'COLUMNS_V2 → 6 rows', 8, bold=True, mono=True) +
    wh([('tiffingo', ['customers'])]) + ms([('TBLS', 'customers'), ('COLS', 'customer_id int'), ('COLS', 'name string'), ('COLS', '… plan string')], 1),
    head('LOAD copies the file into the table folder', 'The query then reads it through the SerDe') + box(20, 48, 140, 56, 'card') + t(90, 66, '/data/…/customers.csv', 7.6, mono=True) + t(90, 84, '2,001 lines', 8, 'ink2') + arrow(162, 76, 196, 76, 'green', 2.2) +
    box(198, 48, 150, 56, 'green') + t(273, 66, 'tiffingo.db/customers/', 7.6, mono=True) + t(273, 84, 'customers.csv (91,618 B)', 7.6, 'ink2') +
    wh([('tiffingo', ['customers'])], 'customers') + ms([('PARAMS', 'numFiles 1'), ('PARAMS', 'totalSize 91618'), ('', ''), ('header', 'line 1 skipped')], 1),
    head('Hive 4 translated the table type', 'hive.create.as.acid = false and the table is not transactional') + box(20, 48, 150, 56, 'card') + t(95, 66, 'You asked for', 8, 'ink2') + t(95, 84, 'CREATE TABLE', 9, bold=True, mono=True) + arrow(172, 76, 188, 76, 'acc', 2) +
    box(190, 48, 160, 56, 'acc') + t(270, 66, 'Hive stored', 8, 'ink2') + t(270, 82, 'EXTERNAL_TABLE', 8.6, bold=True, mono=True) + t(270, 96, '+ external.table.purge', 7.4, 'ink2', mono=True) +
    wh([('tiffingo', ['customers'])]) + ms([('TBLS', 'EXTERNAL_TABLE'), ('PARAMS', 'TRANSLATED_TO_'), ('', '   EXTERNAL=TRUE'), ('PARAMS', 'purge=TRUE')], 0),
    head('The metastore guards names and contents') + box(20, 44, 150, 64, 'red') + t(95, 62, 'customers exists', 8.4, 'red', bold=True) + t(95, 80, 'same name in same db', 7.6, 'ink2') + t(95, 94, '→ AlreadyExists', 7.6, 'ink2', mono=True) +
    box(190, 44, 160, 64, 'red') + t(270, 62, 'tiffingo has tables', 8.4, 'red', bold=True) + t(270, 80, 'DROP DATABASE refused', 7.6, 'ink2') + t(270, 94, 'CASCADE would drop all', 7.6, 'ink2', mono=True) +
    wh([('tiffingo', ['customers', 'customers_copy'])]) + ms([('TBLS', 'customers'), ('TBLS', 'customers_copy'), ('', ''), ('check', 'unique (db, name)')], 3),
]
see_caps = ['Kabir creates the tiffingo database with a comment, and SHOW DATABASES lists it next to default.',
            'He creates the customers table: columns, a comma delimiter and a property to skip the header line.',
            'DESCRIBE answers instantly with the six columns, their types and comments.',
            'He loads the CSV file and counts customers per plan: 999 + 517 + 484 = 2,000.',
            'DESCRIBE FORMATTED reveals the table type: EXTERNAL_TABLE, translated, with purge.',
            'A duplicate CREATE and a DROP of a non-empty database are both refused.']
behind_caps = ['The metastore gets a row in DBS and the warehouse gets a folder tiffingo.db.',
               'Rows are added in TBLS, SDS (location and format), COLUMNS_V2 and TABLE_PARAMS, and an empty folder customers is made.',
               'DESCRIBE is a metadata-only command: it reads the column rows from the metastore. No files are opened.',
               'LOAD DATA copies the file into the table folder and updates numFiles and totalSize. Queries skip line 1.',
               'Because the table is not transactional and hive.create.as.acid is false, Hive 4 stores it as an external table with purge on.',
               'The metastore enforces a unique table name per database and refuses to drop a database that still has tables.']
two = anim_two('Databases and tables', 'From CREATE DATABASE to DESCRIBE FORMATTED', 'Beeline commands and their real output', 'Metastore rows and warehouse folders after each command', see, B1, see_caps, behind_caps)

# ---- scenario 1: layers of databases
l1 = (head('Every team writes to default', '140 tables, no owners') + ''.join(fill(30 + (k % 14) * 22, 54 + (k // 14) * 18, 16, 12, 'red' if k % 5 == 0 else 'grey', rx=2) for k in range(56)) +
      cap('Which orders table is the real one?', 'Name clashes: orders_v2, orders_final, orders_final_new…', 'red', y=150, h=46))
l2 = (head('Split by stage: raw → curated → mart') + label_box(10, 50, 104, 60, ['tiffingo_raw', 'as received'], 'card', 8) + arrow(116, 80, 128, 80) + label_box(130, 50, 100, 60, ['tiffingo', 'clean, typed'], 'acc', 8) + arrow(232, 80, 244, 80) + label_box(246, 50, 104, 60, ['tiffingo_mart', 'for reports'], 'green', 8) +
      cap('Each database has one purpose and one owner.', 'Same table name can exist in each stage.', 'green', y=150, h=46))
l3 = (head('Qualified names remove doubt') + t(180, 66, 'SELECT … FROM tiffingo.orders o', 9, 'ink', mono=True, bold=True) + t(180, 84, 'JOIN tiffingo_raw.restaurants r', 9, 'ink', mono=True, bold=True) + t(180, 112, 'works whatever the current database is', 8.4, 'ink2') +
      cap('db.table in every scheduled script.', '', 'blue', y=150, h=34))
l4 = (head('Sandboxes for experiments') + label_box(30, 50, 140, 60, ['sandbox_kabir', 'tmp tables, tests'], 'blue', 8.4) + label_box(190, 50, 140, 60, ['sandbox_riya', 'tmp tables, tests'], 'blue', 8.4) +
      cap('Personal databases keep shared ones clean.', 'Clean them up on a schedule, or use TEMPORARY tables.', 'blue', y=150, h=46))
l5 = (head('Permissions follow databases') + ''.join(t(26, 56 + k * 19, s, 8.4, anchor='start') for k, s in enumerate(['tiffingo_raw  → ingestion jobs write; engineers read', 'tiffingo      → data engineering writes; analysts read', 'tiffingo_mart → analysts and BI read', 'sandbox_*     → only the owner'])) +
      cap('Access rules are simpler per database (Module 10).', '', 'green', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Organising a warehouse with databases',
              'See how TiffinGo goes from 140 tables in default to a clear layout that new joiners understand on day one.',
              'Database layout', 'Tables moved from one crowded default database into raw, curated, mart and sandbox databases', [l1, l2, l3, l4, l5],
              ['Everyone created tables in default. Names clash and nobody knows which table is official.',
               'The team creates one database per stage: raw files, cleaned company tables and report-ready marts.',
               'Scheduled scripts use qualified names such as tiffingo.orders, so they never read the wrong table.',
               'Each person experiments in a sandbox database or with temporary tables.',
               'Access is granted per database: who may write and who may only read.'],
              hid='scenario-layout')

# ---- scenario 2: reading DESCRIBE FORMATTED
r1 = term([('> DESCRIBE FORMATTED customers;', W), ('| customer_id | int    | unique id |', G), ('| …           |        |           |', G), ('| # Detailed Table Information |', Y), ('| Location: | file:/…/tiffingo.db/customers |', W), ('| Table Type: | EXTERNAL_TABLE |', W), ('| # Storage Information |', Y)], size=7.6)
r2 = (head('Section 1 · Columns', 'Name, type, comment') + box(20, 52, 320, 50, 'blue') + t(30, 70, 'customer_id  int     unique id', 8.2, anchor='start', mono=True) + t(30, 86, 'plan         string  Gold, Silver or Basic', 8.2, anchor='start', mono=True) +
      cap('Check types first: a wrong type gives NULLs.', '', 'blue', y=150, h=34))
r3 = (head('Section 2 · Detailed Table Information') + box(20, 44, 320, 92, 'acc') + ''.join(t(30, 62 + k * 15, s, 7.8, anchor='start', mono=True) for k, s in enumerate(['Location:    …/tiffingo.db/customers', 'Table Type:  EXTERNAL_TABLE', 'Owner:       hive', 'numFiles 1 · totalSize 91618', 'external.table.purge  TRUE'])) +
      cap('Where are the files, who owns them, what happens on DROP?', '', 'acc', y=150, h=34))
r4 = (head('Section 3 · Storage Information') + box(20, 44, 320, 92, 'green') + ''.join(t(30, 62 + k * 15, s, 7.6, anchor='start', mono=True) for k, s in enumerate(['SerDe Library: …lazy.LazySimpleSerDe', 'InputFormat:   …mapred.TextInputFormat', 'Num Buckets:   -1   (not bucketed)', 'field.delim    ,', 'Compressed:    No'])) +
      cap('How lines become columns, and in what format.', '', 'green', y=150, h=34))
r5 = (head('Four questions, answered in seconds', '') + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['1. Managed or external? → Table Type + purge', '2. Where are the files? → Location', '3. How is a line split? → SerDe + field.delim', '4. How big? → numFiles, totalSize (if stats exist)'])) +
      cap('Run DESCRIBE FORMATTED before you change any table.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Reading DESCRIBE FORMATTED like an engineer',
              'Its output is long. Learn its three sections and the four questions it answers. The values are from our lab.',
              'DESCRIBE FORMATTED', 'The three sections of DESCRIBE FORMATTED output: columns, detailed table information and storage information', [r1, r2, r3, r4, r5],
              ['DESCRIBE FORMATTED prints a long table with three sections marked by #.',
               'Section 1 lists the columns with types and comments.',
               'Section 2 gives the location, table type, owner and table parameters such as numFiles and purge.',
               'Section 3 shows the SerDe, input format, buckets and delimiter.',
               'Use it to answer four questions before touching a table: type, location, format and size.'],
              hid='scenario-describe')

# ---- scenario 3: errors
e1 = term([('> SELECT * FROM tiffingo.customer;', W), ('Error: … SemanticException [Error 10001]:', RD), ("  Line 1:14 Table not found 'customer'", RD), ('', W), ('→ compile time: no job was started', Y)])
e2 = term([('> CREATE TABLE customers (id INT);', W), ('Error: … AlreadyExistsException(', RD), ('  message:Table hive.tiffingo.customers', RD), ('  already exists)', RD), ('', W), ('→ use IF NOT EXISTS in re-runnable scripts', Y)])
e3 = term([("> SHOW DATABASES LIKE 'tif*';", W), ('+----------------+', G), ('| database_name  |', G), ('+----------------+', G), ("> SHOW DATABASES LIKE 'tif%';", W), ('| tiffingo       |', G), ('→ Hive 4: use % (SQL wildcard)', Y)])
e4 = term([('> DROP DATABASE tiffingo;', W), ('Error: … InvalidOperationException(', RD), ('  Database tiffingo is not empty.', RD), ('  One or more tables exist.)', RD), ('', W), ('DROP DATABASE … CASCADE  ← drops every table', Y)])
e5 = (head('A script stops at the first error') + box(20, 44, 150, 96, 'card') + ''.join(t(30, 62 + k * 15, s, 7.8, ['green', 'green', 'red', 'ink3', 'ink3'][k], anchor='start', mono=True) for k, s in enumerate(['1 CREATE DATABASE ✓', '2 CREATE TABLE ✓', '3 CREATE TABLE ✗', '4 LOAD DATA (skipped)', '5 SELECT (skipped)'])) +
      t(260, 80, 'beeline -f', 9, bold=True, mono=True) + t(260, 98, 'exits with an error code', 8, 'ink2') + cap('Make DDL idempotent: IF [NOT] EXISTS.', 'Then a failed run can simply be re-run.', 'blue', y=154, h=46))
s3 = anim_one('Real-time scenario 3 · advanced', 'Four real errors and what they teach',
              'Every message here was produced by our lab. Learn to read them; they tell you exactly what is wrong.',
              'Errors', 'Real Hive 4 error messages: table not found, already exists, wildcard mismatch and non-empty database, then script behaviour', [e1, e2, e3, e4, e5],
              ['A typo in a table name fails at compile time with SemanticException 10001. No cluster time is used.',
               'Creating a table that exists fails with AlreadyExistsException. IF NOT EXISTS avoids it.',
               'In Hive 4 the pattern tif* matched nothing; the SQL wildcard tif% matched tiffingo.',
               'DROP DATABASE refuses a database that has tables. CASCADE drops them all, so use it with great care.',
               'beeline -f stops at the first failing statement. Re-runnable DDL makes recovery easy.'],
              hid='scenario-errors')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Six commands, two views</h2>
  <p>Left: Beeline and its real output. Right: the rows in the metastore and the folders in the warehouse that each command creates.</p>
''' + two + '''
  <p>Three live scenarios follow: organising databases, reading DESCRIBE FORMATTED, and understanding errors.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Databases and tables in daily work</h2>
''' + usecase(
    ''.join(box(14 + k * 34, 26, 28, 40, tone) for k, tone in enumerate(['card', 'acc', 'green'])) + t(60, 80, 'raw · curated · mart', 7, 'ink2'),
    '1. Layered warehouses',
    'Most companies keep raw landing data, cleaned tables and report tables in separate databases. A table’s database tells you how much you can trust it.',
    ['Files arrive', '*raw → curated → mart', 'Reports']) + '\n' + usecase(
    '<rect x="16" y="20" width="88" height="50" rx="6" class="s-board"/><text x="24" y="40" font-size="7.6" class="mono" style="fill:#9FD3B8">git: ddl/</text><text x="24" y="54" font-size="7.6" class="mono" style="fill:#F5C77E">customers.hql</text>',
    '2. DDL in version control',
    'Teams keep every <code>CREATE TABLE</code> in Git (often taken from <code>SHOW CREATE TABLE</code>). Changes are reviewed like code and the same file builds dev, test and production.',
    ['Pull request', '*Review DDL', 'Deploy']) + '\n' + usecase(
    '<rect x="16" y="20" width="88" height="50" rx="6" class="s-card2"/>' + t(60, 40, 'dev_ · test_ · prod', 8, 'acc', bold=True) + t(60, 56, 'same tables', 7.4, 'ink2'),
    '3. One database per environment',
    'On a shared cluster, <code>dev_tiffingo</code>, <code>test_tiffingo</code> and <code>tiffingo</code> hold the same tables. A <code>--hivevar db=…</code> switch points the same script at each.',
    ['Script', '*${db}.orders', 'Right environment']) + '\n' + usecase(
    '<rect x="16" y="20" width="88" height="50" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 40, 'catalogue', 9, 'violet', bold=True) + t(60, 56, 'comments · owners', 7.4, 'ink2'),
    '4. Data discovery',
    'Data catalogue tools read databases, tables, column comments and properties from the metastore. Good comments written at <code>CREATE</code> time become documentation everyone can search.',
    ['COMMENT', '*Metastore', 'Catalogue search']) + '\n' + usecase(
    '<rect x="16" y="20" width="88" height="50" rx="6" class="s-card2"/>' + t(60, 40, 'TEMPORARY', 8.4, 'blue', bold=True, mono=True) + t(60, 56, 'gone at logout', 7.4, 'ink2'),
    '5. Scratch work without clutter',
    'Analysts use <code>CREATE TEMPORARY TABLE</code> for intermediate steps. The table disappears when the session ends, so shared databases stay clean.',
    ['Big query', '*Temp table', 'Final result']) + '''
  <p class="muted">Examples are simplified. Naming conventions differ between companies.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> have the lab from <a href="../../01-introduction/05-install-hive-and-beeline/">Lesson 1.5</a> running and Beeline connected. The customers file comes from the course dataset.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
