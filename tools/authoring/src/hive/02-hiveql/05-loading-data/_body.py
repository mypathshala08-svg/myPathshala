import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()

# ---------------------------------------------------------------- story
sc = (node(10, 20, 150, 46, 'LOAD DATA', 'copy / move files as they are', 'blue') + node(10, 80, 150, 46, 'INSERT … SELECT', 'query writes new files', 'acc') +
      node(170, 20, 150, 46, 'CREATE TABLE … AS', 'table + data in one step', 'green') + node(170, 80, 150, 46, 'FROM … INSERT … INSERT', 'one scan, many tables', 'violet') +
      ''.join(arrow(324, 43 + k * 60, 380, 72, 'ink3', 1.6) for k in range(2)) + box(382, 30, 248, 90, 'card') + t(506, 50, 'tiffingo.db/…', 9, bold=True, mono=True) +
      ''.join(t(396, 68 + j * 14, s, 7.6, 'ink2', anchor='start', mono=True) for j, s in enumerate(['customers_day1.csv', 'customers_day1_copy_1.csv   ← loaded twice!', '000000_0, 000000_0_copy_1, …'])))
scene_svg = scene('Four ways to put data into Hive tables: LOAD DATA, INSERT SELECT, CREATE TABLE AS SELECT and multi-table insert, all ending as files in the table folder.', sc,
                  'Every way of loading ends the same way: <tspan font-weight="700" class="s-acc">files in the table’s folder</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Why does the customers table have 4,000 customers?”</h2>
  <div class="story">
    <p class="narration">TiffinGo has exactly 2,000 customers. Kabir’s nightly script loads the customer file into Hive, but one night the job is retried after a network blip. Next morning the dashboard shows 4,000 customers, and Riya notices that a file in the landing folder has vanished after a different load.</p>

{scene_svg}

K> Sir, I only ran <code>LOAD DATA</code> twice. Shouldn’t Hive notice it is the same file?
A> No. <code>LOAD DATA … INTO</code> simply puts the file into the table’s folder. The second time, a file with that name already exists, so Hive keeps both and renames the new one <code>customers_day1_copy_1.csv</code>. Two files, 4,000 rows. Hive does not check contents, schema or duplicates.
R> And my file that disappeared?
A> Without the word <code>LOCAL</code>, LOAD <b>moves</b> the file from the source path into the table; with <code>LOCAL</code> it copies from the server’s local disk. Today you will learn every way to fill a table: LOAD (copy or move), INSERT INTO and OVERWRITE, CREATE TABLE AS SELECT and the multi-insert that writes three tables in one scan. And how to make loads safe to re-run.
  </div>
</section>
'''

lv = '''
LEVELS> Loading data at three levels
L1> Putting groceries in a cupboard
      <ul>
        <li><b>LOAD DATA</b> = putting the bags in the cupboard as they are. Fast, no checking. Put the same bag twice and you have two.</li>
        <li><b>INSERT … SELECT</b> = cooking: take ingredients from one cupboard, prepare them, store the dish in another.</li>
        <li><b>OVERWRITE</b> = empty the shelf first, then put the new food in. Running it twice gives the same result.</li>
        <li><b>CTAS</b> = buy a new box and fill it in one step.</li>
      </ul>
L2> What each statement does
      <ul>
        <li><code>LOAD DATA LOCAL INPATH 'p' INTO TABLE t</code>: <b>copies</b> files from the HiveServer2 machine’s local disk into the table folder.</li>
        <li><code>LOAD DATA INPATH 'p' INTO TABLE t</code>: <b>moves</b> files that are already in the table’s file system (HDFS, or here the local FS).</li>
        <li><code>… OVERWRITE INTO TABLE</code>: removes the old files first.</li>
        <li><code>INSERT INTO t SELECT …</code> appends query results; <code>INSERT OVERWRITE TABLE t SELECT …</code> replaces them. Both run a Tez job and write new files (<code>000000_0</code>, …).</li>
        <li><code>INSERT INTO t VALUES (…)</code>: a few literal rows; each statement makes a new small file.</li>
        <li><code>CREATE TABLE t STORED AS ORC AS SELECT …</code> (CTAS): creates the table from the query’s columns and fills it.</li>
        <li><code>FROM src INSERT … INSERT …</code>: one scan of <code>src</code>, several targets.</li>
      </ul>
L3> The details that bite in production
      <ul>
        <li><b>LOAD does not validate</b> anything: loading a JSON file into a CSV table succeeded and produced NULL ids.</li>
        <li><b>skip.header.line.count applies to every file</b> in the folder: the first line of the JSON file was silently dropped (2,119 rows, not 2,120).</li>
        <li><b>File names:</b> a second file with the same name becomes <code>…_copy_1</code>; repeated INSERTs make <code>000000_0_copy_1</code>, <code>_copy_2</code>: the start of the small-files problem.</li>
        <li><b>Staging:</b> INSERT writes to a <code>.hive-staging_…</code> folder first and moves the files in at the end, so readers never see half-written results.</li>
        <li><b>Statistics:</b> CTAS and INSERT update <code>numRows</code> automatically (8 rows for city_sales), which helps the optimiser.</li>
        <li><b>Idempotency:</b> INSERT OVERWRITE and LOAD … OVERWRITE give the same result when re-run; INSERT INTO and LOAD … INTO do not.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Loading data into Hive tables</h2>
''' + def_block(
    'Data enters a Hive table in two ways. <b>LOAD DATA [LOCAL] INPATH \'path\' [OVERWRITE] INTO TABLE t</b> is a pure file operation: it copies (LOCAL) or moves files into the table’s location without parsing or validating them. <b>INSERT INTO | OVERWRITE TABLE t SELECT …</b>, <b>INSERT INTO t VALUES …</b>, <b>CREATE TABLE … AS SELECT</b> (CTAS) and the multi-table form <b>FROM src INSERT … INSERT …</b> run a query whose results are serialized in the target table’s format and written as new files; OVERWRITE replaces existing data, INTO appends.',
    'LOAD just puts files into the table’s folder: quick, but nothing is checked. INSERT and CTAS run a query and write fresh files in the table’s own format. OVERWRITE replaces, INTO adds.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('LOCAL', 'With LOAD: the path is on HiveServer2’s local disk and the file is copied. Without: the path is in the cluster file system and the file is moved.'),
    ('OVERWRITE', 'Delete the existing data of the table (or partition) before writing.'),
    ('CTAS', 'CREATE TABLE … AS SELECT: new table with the query’s columns and rows.'),
    ('Multi-insert', 'FROM src INSERT … INSERT …: read the source once, write several tables.'),
    ('Idempotent', 'Running it twice gives the same result as once. Essential for retried jobs.'),
    ('Staging directory', '<code>.hive-staging_…</code>: where INSERT writes before moving files into place.'),
    ('Small files', 'Many tiny files in a table: slow to list and read. Each INSERT … VALUES adds one.'),
    ('copy_N', 'Suffix Hive adds when a file of the same name already exists in the table folder.'),
]) + '''

  <h3>Choosing a loading method</h3>
''' + table(['Method', 'Parses data?', 'Changes format?', 'Re-run safe?', 'Best for'], [
    ['<code>LOAD DATA LOCAL INPATH … INTO</code>', 'No', 'No (file kept as is)', '<b>No</b>: duplicates', 'Quick tests, small files on the server'],
    ['<code>LOAD DATA INPATH … OVERWRITE INTO</code>', 'No', 'No', 'Yes', 'Moving landed files into a table'],
    ['<code>INSERT INTO t SELECT …</code>', 'Yes', 'Yes, to t’s format', '<b>No</b>', 'Appending new batches carefully'],
    ['<code>INSERT OVERWRITE TABLE t SELECT …</code>', 'Yes', 'Yes', 'Yes', 'Nightly rebuilds, raw → curated'],
    ['<code>INSERT INTO t VALUES …</code>', '—', 'Yes', 'No', 'A few reference rows, tests'],
    ['<code>CREATE TABLE t AS SELECT …</code>', 'Yes', 'Yes', 'Fails if t exists', 'One-off derived tables'],
    ['<code>FROM s INSERT … INSERT …</code>', 'Yes', 'Yes', 'With OVERWRITE', 'Splitting one big source into several tables'],
], minw=720) + lv + '''
EXAM> “Difference between LOAD DATA LOCAL and LOAD DATA.” LOCAL copies a file from the local file system of the HiveServer2 host; without LOCAL the file is moved within HDFS. Add: LOAD does not validate the data, OVERWRITE replaces existing files, and INSERT … SELECT is used when data must be transformed or converted to another format.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Loading patterns in a real pipeline</h2>
''' + cards([
    ('Landing → raw', 'Files are dropped into a folder by an ingestion tool. An external raw table simply points at the folder; nothing is loaded at all.', 'No LOAD needed'),
    ('Raw → curated', '<code>INSERT OVERWRITE TABLE curated SELECT CAST(…) … FROM raw</code>. Parses, types, cleans and writes ORC. Re-run safe.', 'Most common'),
    ('Curated → mart', 'CTAS or INSERT OVERWRITE of aggregates such as daily city sales for dashboards.', 'Reports'),
    ('Fan-out', 'A multi-insert splits one large source into several tables (by payment type, region…) in one scan.', 'Efficient'),
]) + '''

  <h3>LOAD vs INSERT on the same file</h3>
''' + table(['', 'LOAD DATA', 'INSERT … SELECT'], [
    ['Speed', 'Instant (file copy or rename)', 'Runs a Tez job'],
    ['Validation', 'None: wrong files load fine', 'Values pass through the SerDe and casts'],
    ['Target format', 'Must already match the table', 'Any: text in, ORC out'],
    ['Header lines', 'Stay in the file (use skip.header.line.count)', 'Filtered by the source table'],
    ['Typical mistake', 'Loading twice; loading the wrong file', 'INSERT INTO on retry: duplicates'],
], minw=560) + '''
WARN> A retried job that uses <code>INSERT INTO</code> or <code>LOAD … INTO</code> duplicates data silently. Write loads so that a re-run produces the same result: <code>OVERWRITE</code> a table or a partition (Module 5), or MERGE on a key (Module 7).
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Every way to load, tested</h2>
  <p>All outputs are real, from the Hive 4.2.1 lab.</p>
''' + stepper([
    ('Step 1 · LOAD the same file twice',
     code('sql', 'Beeline', "CREATE TABLE cust_load (customer_id INT, name STRING, city STRING, state STRING,\n  joined_on DATE, plan STRING)\nROW FORMAT DELIMITED FIELDS TERMINATED BY ','\nTBLPROPERTIES ('skip.header.line.count'='1');\nLOAD DATA LOCAL INPATH '/data/tiffingo/incoming/customers_day1.csv' INTO TABLE cust_load;\nSELECT COUNT(*) AS after_first FROM cust_load;\nLOAD DATA LOCAL INPATH '/data/tiffingo/incoming/customers_day1.csv' INTO TABLE cust_load;\nSELECT COUNT(*) AS after_same_file_again FROM cust_load;", capf('l25_load1.txt')),
     'No warning, just double the rows. The table folder now holds <code>customers_day1.csv</code> and <code>customers_day1_copy_1.csv</code>. This is Kabir’s 4,000 customers.'),
    ('Step 2 · LOAD without LOCAL moves the file; OVERWRITE replaces',
     code('sql', 'Beeline', "LOAD DATA INPATH 'file:///data/tiffingo/incoming/customers_day2.csv'\n  OVERWRITE INTO TABLE cust_load;\nSELECT COUNT(*) AS after_overwrite FROM cust_load;", capf('l25_load2.txt').split('+-------------+')[0].rstrip() + '\n\n$ ls /data/tiffingo/incoming\ncustomers_day1.csv          ← customers_day2.csv has gone'),
     'OVERWRITE removed both old files, so the count is right again: 2,000. And the source file was <b>moved</b> into the table folder, which is what surprised Riya. On HDFS this is a cheap rename.'),
    ('Step 3 · LOAD checks nothing',
     code('sql', 'Beeline', "LOAD DATA LOCAL INPATH '/data/tiffingo/restaurants/restaurants.json' INTO TABLE cust_load;\nSELECT COUNT(*) AS rows_total, COUNT(customer_id) AS with_id FROM cust_load;\nSELECT customer_id, name, city FROM cust_load WHERE customer_id IS NULL LIMIT 2;",
          '+-------------+----------+\n| rows_total  | with_id  |\n+-------------+----------+\n| 2119        | 2000     |\n+-------------+----------+\n+--------------+-----------------------------+--------------------+\n| customer_id  |            name             |        city        |\n+--------------+-----------------------------+--------------------+\n| NULL         |  "name": "Nair Bhojanalay"  |  "city": "Mumbai"  |\n| NULL         |  "name": "Gupta Mess"       |  "city": "Thane"   |\n+--------------+-----------------------------+--------------------+'),
     'A JSON file loaded happily into a CSV table: 119 junk rows with NULL ids. Why 119, not 120? <code>skip.header.line.count</code> is applied to <b>every file</b>, so the first restaurant was dropped as a “header”.'),
    ('Step 4 · CREATE TABLE AS SELECT',
     code('sql', 'Beeline', "CREATE TABLE city_sales STORED AS ORC AS\nSELECT city, COUNT(*) AS orders, SUM(amount) AS revenue\nFROM orders_ext WHERE status = 'DELIVERED' GROUP BY city;\nSELECT * FROM city_sales ORDER BY revenue DESC LIMIT 3;\nDESCRIBE city_sales;", capf('l25_ctas.txt')),
     'Columns and types come from the query: <code>COUNT(*)</code> and <code>SUM(int)</code> are BIGINT. The text orders became an ORC file <code>000000_0</code>, and Hive recorded <code>numRows 8</code> automatically.'),
    ('Step 5 · One scan, three tables',
     code('sql', 'Beeline', "FROM orders_ext o\nINSERT OVERWRITE TABLE upi_orders  SELECT o.order_id, o.city, o.amount WHERE o.payment = 'UPI'\nINSERT OVERWRITE TABLE cod_orders  SELECT o.order_id, o.city, o.amount WHERE o.payment = 'COD'\nINSERT OVERWRITE TABLE payment_mix SELECT o.payment, COUNT(*) GROUP BY o.payment;",
          'Map 1 .......... container     SUCCEEDED      1          1 …\nReducer 2 ...... container     SUCCEEDED      1          1 …\nReducer 3 ...... container     SUCCEEDED      1          1 …\nReducer 4 ...... container     SUCCEEDED      1          1 …\nReducer 5 ...... container     SUCCEEDED      1          1 …\nVERTICES: 05/05  [==========================>>] 100%  ELAPSED TIME: 2.19 s\nINFO  :    RECORDS_IN_Map_1: 50002\nINFO  :    RECORDS_OUT_1_tiffingo.upi_orders: 30011\nINFO  :    RECORDS_OUT_2_tiffingo.cod_orders: 5005\nINFO  :    RECORDS_OUT_3_tiffingo.payment_mix: 4\n35,020 rows affected (2.655 seconds)'),
     '<b>One</b> Map vertex read the 50,002 rows <b>once</b> and fed three outputs. Three separate INSERTs would have scanned the source three times.'),
    ('Step 6 · INSERT … VALUES and the small-files trap',
     code('sql', 'Beeline', "INSERT INTO payment_mix VALUES ('BNPL', 0), ('Gift card', 0);\nINSERT INTO payment_mix (payment) VALUES ('Crypto');\nSELECT * FROM payment_mix ORDER BY orders DESC;", capf('l25_values.txt') + "\n\n$ find …/payment_mix -type f -not -name '.*'\n000000_0\n000000_0_copy_1\n000000_0_copy_2"),
     'A column list lets you omit columns (orders is NULL for Crypto). Each INSERT statement created a <b>new file</b>: three files for seven rows. A loop that inserts one row at a time would create thousands. Notice too that the NULL sorted first in this DESC order.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
def folder(files, title='tiffingo.db/cust_load/', hl=None, rows=None):
    o = box(190, 40, 160, 120, 'card') + t(270, 56, title, 7.8, bold=True, mono=True)
    for k, f in enumerate(files):
        o += t(198, 76 + k * 14, f, 7.2, 'acc' if hl == k else 'ink', anchor='start', mono=True, bold=hl == k)
    if rows is not None:
        o += t(270, 150, f'COUNT(*) = {rows}', 8.4, 'green' if rows in ('2,000', '2000') else 'red', bold=True, mono=True)
    return o
def src(files, title='incoming/'):
    o = box(10, 40, 160, 120, 'blue') + t(90, 56, title, 7.8, bold=True, mono=True)
    for k, f in enumerate(files):
        o += t(18, 76 + k * 14, f, 7.2, 'ink', anchor='start', mono=True)
    return o
see = [
    term([("> LOAD DATA LOCAL INPATH '…/customers_day1.csv'", W), ('  INTO TABLE cust_load;', W), ('> SELECT COUNT(*) FROM cust_load;', W), ('| 2000 |', G)]),
    term([('> (the job is retried)', Y), ("> LOAD DATA LOCAL INPATH '…/customers_day1.csv'", W), ('  INTO TABLE cust_load;', W), ('> SELECT COUNT(*) FROM cust_load;', W), ('| 4000 |', RD)]),
    term([("> LOAD DATA INPATH 'file:///…/customers_day2.csv'", W), ('  OVERWRITE INTO TABLE cust_load;', W), ('> SELECT COUNT(*) …;', W), ('| 2000 |', G), ('$ ls incoming', W), ('customers_day1.csv', Y)]),
    term([("> LOAD DATA LOCAL INPATH '…/restaurants.json'", W), ('  INTO TABLE cust_load;', W), ('No rows affected', G), ('> SELECT COUNT(*), COUNT(customer_id) …;', W), ('| 2119 | 2000 |', RD)]),
    term([('> FROM orders_ext o', W), ('  INSERT OVERWRITE TABLE upi_orders  …', W), ('  INSERT OVERWRITE TABLE cod_orders  …', W), ('  INSERT OVERWRITE TABLE payment_mix …;', W), ('RECORDS_IN_Map_1: 50002', G), ('35,020 rows affected (2.655 seconds)', G)]),
    term([("> INSERT INTO payment_mix VALUES ('BNPL',0), …;", W), ("> INSERT INTO payment_mix (payment)", W), ("  VALUES ('Crypto');", W), ('$ ls payment_mix', W), ('000000_0  000000_0_copy_1', Y), ('000000_0_copy_2', Y)]),
]
B1 = [
    t(180, 22, 'LOCAL: copy into the table folder', 9.4, bold=True) + src(['customers_day1.csv', 'customers_day2.csv']) + arrow(172, 100, 188, 100, 'blue', 2) + folder(['customers_day1.csv'], hl=0, rows='2,000') +
    cap('A file copy. Nothing is parsed.', '', 'blue', y=176, h=34),
    t(180, 22, 'Same name again → _copy_1', 9.4, 'red', bold=True) + src(['customers_day1.csv', 'customers_day2.csv']) + arrow(172, 100, 188, 100, 'red', 2) + folder(['customers_day1.csv', 'customers_day1_copy_1.csv'], hl=1, rows='4,000') +
    cap('Two files, two copies of every customer.', '', 'red', y=176, h=34),
    t(180, 22, 'No LOCAL: move. OVERWRITE: clear first', 9.4, 'green', bold=True) + src(['customers_day1.csv', '(day2 moved away)']) + arrow(172, 100, 188, 100, 'green', 2) + folder(['customers_day2.csv'], hl=0, rows='2,000') +
    cap('Old files deleted, source file moved in.', 'Re-running gives the same result.', 'green', y=176, h=46),
    t(180, 22, 'LOAD trusts you completely', 9.4, 'red', bold=True) + src(['restaurants.json', '120 lines of JSON'], 'restaurants/') + arrow(172, 100, 188, 100, 'red', 2) + folder(['customers_day2.csv', 'restaurants.json'], hl=1, rows='2,119') +
    cap('JSON read as CSV: 119 junk rows.', 'Line 1 of the JSON was skipped as a “header”.', 'red', y=176, h=46),
    t(180, 22, 'Multi-insert: one scan, three outputs', 9.4, bold=True) + label_box(10, 60, 100, 50, ['Map 1', 'reads 50,002 rows'], 'acc', 8) +
    ''.join(arrow(112, 85, 150, 50 + k * 40, 'ink3', 1.6) + label_box(152, 34 + k * 40, 196, 32, [nm], tone, 8) for k, (nm, tone) in enumerate([('upi_orders · 30,011 rows', 'green'), ('cod_orders · 5,005 rows', 'blue'), ('payment_mix · 4 rows', 'violet')])) +
    cap('Files are written to .hive-staging, then moved in.', 'Readers never see half-written data.', 'blue', y=176, h=46),
    t(180, 22, 'Every INSERT statement = new file(s)', 9.4, 'amber', bold=True) + folder(['000000_0          4 rows', '000000_0_copy_1   2 rows', '000000_0_copy_2   1 row'], 'payment_mix/') + src(['INSERT … SELECT', "INSERT … VALUES ('BNPL'…)", "INSERT … VALUES ('Crypto')"], 'statements') +
    cap('Three files for seven rows.', 'Row-by-row inserts create the small-files problem.', 'amber', y=176, h=46),
]
see_caps = ['Kabir loads the customer file: 2,000 rows.',
            'The job is retried and loads the same file again: 4,000 rows, no warning.',
            'He switches to LOAD without LOCAL and with OVERWRITE: 2,000 rows again, but the source file is gone from incoming.',
            'A JSON file loads into the CSV table without any error, and the counts no longer add up.',
            'A multi-insert writes three tables from one read of the orders: 35,020 rows written.',
            'Two small INSERT … VALUES statements leave three files in the table folder.']
behind_caps = ['LOCAL copies the file from HiveServer2’s disk into the table folder.',
               'The name already exists, so the copy is renamed customers_day1_copy_1.csv. Both files are read.',
               'OVERWRITE deletes the old files; without LOCAL the source file is moved (renamed), not copied.',
               'LOAD never parses. The JSON lines become rows with NULL ids, and the header rule removes one line from each file.',
               'One Map vertex reads the source once and routes rows to three outputs, staged and then moved into place.',
               'Each INSERT writes at least one new file. Many tiny files slow down listing and reading.']
two = anim_two('Loading', 'Six loads and what they did to the folder', 'Real Beeline output', 'Files in the table folder after each statement', see, B1, see_caps, behind_caps)

# ---- scenario 1: idempotent nightly load
r1 = (t(180, 22, 'Nightly job: INSERT INTO', 9.6, bold=True) + t(180, 52, "INSERT INTO daily_orders SELECT … WHERE order_date = '2026-10-25'", 7.6, 'ink', mono=True) + bars([('run 1', 50, 'green', '48,000 rows')], y=74) +
      cap('First run: correct.', '', 'green', y=150, h=34))
r2 = (t(180, 22, 'Network blip: scheduler retries', 9.6, 'red', bold=True) + bars([('run 1', 50, 'green', '48,000'), ('retry', 50, 'red', '+48,000')], y=56) +
      cap('Revenue for 25 Oct is now doubled.', 'Finance finds out a week later.', 'red', y=150, h=46))
r3 = (t(180, 22, 'Fix: OVERWRITE the slice you load', 9.6, 'green', bold=True) + t(180, 52, "INSERT OVERWRITE TABLE daily_orders PARTITION (order_date='2026-10-25')", 7.4, 'ink', mono=True) + t(180, 66, 'SELECT … ;', 7.4, 'ink', mono=True) + bars([('run 1', 50, 'green', '48,000'), ('retry', 50, 'green', '48,000')], y=84) +
      cap('Re-runs replace instead of adding.', 'Partitions: Module 5.', 'green', y=150, h=46))
r4 = (t(180, 22, 'Or MERGE on a key', 9.6, 'blue', bold=True) + t(180, 56, 'MERGE INTO orders t USING new_orders s ON t.order_id = s.order_id', 7.4, 'ink', mono=True) + t(180, 72, 'WHEN MATCHED THEN UPDATE … WHEN NOT MATCHED THEN INSERT …', 7.4, 'ink', mono=True) +
      cap('For ACID tables that receive changes.', 'Module 7.', 'blue', y=150, h=46))
r5 = (t(180, 22, 'Check after every load', 9.6, 'acc', bold=True) + t(180, 56, 'SELECT COUNT(*), COUNT(DISTINCT order_id) FROM daily_orders', 7.6, 'ink', mono=True) + t(180, 72, "WHERE order_date = '2026-10-25';", 7.6, 'ink', mono=True) + t(180, 100, 'the two numbers must be equal', 8.6, 'green', bold=True) +
      cap('Duplicates are caught the same night.', '', 'green', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'The retried job that doubled revenue',
              'Retries are normal in schedulers. Loads must be written so that a retry is harmless. (Row counts illustrative.)',
              'Idempotent loads', 'A nightly INSERT INTO run twice doubles a day of data; INSERT OVERWRITE of a partition or MERGE avoids it', [r1, r2, r3, r4, r5],
              ['The nightly job appends one day of orders with INSERT INTO.',
               'A retry appends the same day again. Revenue for that day doubles silently.',
               'INSERT OVERWRITE of exactly the day being loaded makes a retry replace the data.',
               'Tables that receive updates use MERGE on the business key.',
               'A count vs distinct-key check after each load catches duplicates immediately.'],
              hid='scenario-idempotent')

# ---- scenario 2: raw → curated ORC
c1 = (t(180, 22, 'Raw text table: slow and untyped', 9.6, bold=True) + node(20, 50, 140, 50, 'orders_ext', 'CSV text, 50,002 rows', 'card') + t(270, 66, 'every query parses text', 8.2, 'ink2') + t(270, 82, 'and reads every column', 8.2, 'ink2') +
      cap('Fine for landing, poor for reporting.', '', 'amber', y=150, h=34))
c2 = (t(180, 22, 'Curate once with INSERT OVERWRITE', 9.6, bold=True) + t(180, 50, 'INSERT OVERWRITE TABLE orders_curated', 8, 'ink', mono=True) + t(180, 64, 'SELECT order_id, customer_id, city, order_ts,', 8, 'ink', mono=True) + t(180, 78, 'CAST(amount AS DECIMAL(10,2)), payment, status', 8, 'ink', mono=True) + t(180, 92, "FROM orders_ext WHERE order_id IS NOT NULL;", 8, 'ink', mono=True) +
      cap('Types fixed, junk filtered, ORC written.', '', 'green', y=150, h=34))
c3 = (t(180, 22, 'What changes for readers', 9.6, bold=True) + bars([('format', 100, 'green', 'ORC'), ('types', 100, 'green', 'typed'), ('re-run safe', 100, 'green', 'yes')], y=46) +
      cap('Reports read the curated table only.', '', 'green', y=150, h=34))
c4 = (t(180, 22, 'Rejected rows are measured', 9.6, bold=True) + t(180, 56, 'SELECT COUNT(*) FROM orders_ext WHERE order_id IS NULL', 7.8, 'ink', mono=True) + t(180, 72, '   OR amount IS NULL OR order_ts IS NULL;', 7.8, 'ink', mono=True) + t(180, 98, 'our data: 2 rows (amount “abc”, date 31/10/2026)', 8.4, 'amber', bold=True) +
      cap('Count what you drop; alert when it jumps.', '', 'amber', y=150, h=34))
c5 = (t(180, 22, 'Schedule', 9.6, 'acc', bold=True) + label_box(10, 60, 100, 50, ['files land', '00:30'], 'card', 8.4) + arrow(112, 85, 128, 85) + label_box(130, 60, 100, 50, ['curate', '01:00'], 'acc', 8.4) + arrow(232, 85, 248, 85) + label_box(250, 60, 100, 50, ['marts (CTAS)', '02:00'], 'green', 8.4) +
      cap('LOAD is rare; INSERT OVERWRITE does most work.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'From raw text to a curated ORC table',
              'The workhorse of Hive pipelines is INSERT OVERWRITE … SELECT from a raw table.',
              'Raw to curated', 'Orders in a raw text table are cast, filtered and written into an ORC table, with a count of rejected rows', [c1, c2, c3, c4, c5],
              ['The raw external text table is fine for landing but slow and untyped for reports.',
               'One INSERT OVERWRITE casts, filters and writes the data in ORC.',
               'Readers get typed, compressed data, and the job is safe to re-run.',
               'The same job counts rows it rejects: in our data, 2 orders (an amount “abc” and a date in the wrong layout).',
               'A typical night: files land, curation runs, then mart tables are rebuilt.'],
              hid='scenario-curate')

# ---- scenario 3: small files
f1 = (t(180, 22, 'A streaming job inserts every minute', 9.6, bold=True) + t(180, 56, 'INSERT INTO events VALUES (…);   -- 1,440 times a day', 8, 'ink', mono=True) +
      cap('Each statement writes a new file.', 'We saw it: three INSERTs, three files.', 'amber', y=150, h=46))
f2 = (t(180, 22, 'After 90 days', 9.6, 'red', bold=True) + ''.join(fill(20 + (k % 30) * 11, 40 + (k // 30) * 11, 9, 9, 'red' if k % 7 else 'amber', rx=1) for k in range(240)) + t(180, 138, '1,29,600 tiny files', 9, 'red', bold=True) +
      cap('Listing and opening files dominates query time.', 'The NameNode also tracks every file in memory.', 'red', y=150, h=46))
f3 = (t(180, 22, 'Fix 1: batch the writes', 9.6, 'green', bold=True) + t(180, 56, 'collect events, INSERT … SELECT once per hour or day', 8.4, 'ink2') + cap('Fewer, larger files (aim for 128 MB–1 GB).', '', 'green', y=150, h=34))
f4 = (t(180, 22, 'Fix 2: compact what exists', 9.6, 'green', bold=True) + t(180, 56, 'INSERT OVERWRITE TABLE events SELECT * FROM events;', 8, 'ink', mono=True) + t(180, 74, '(per partition, with merge settings) or ACID compaction', 8, 'ink2') +
      cap('Rewrite small files into big ones.', 'Module 5 covers merge settings.', 'green', y=150, h=46))
f5 = (t(180, 22, 'Right tool for streams', 9.6, 'acc', bold=True) + ''.join(t(26, 52 + k * 19, s, 8.4, anchor='start') for k, s in enumerate(['• Kafka → files every few minutes, compacted hourly', '• Iceberg tables with compaction (Module 7)', '• Hive is a batch engine: insert in batches'])) +
      cap('Row-at-a-time INSERT is an anti-pattern.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'How INSERT … VALUES creates a small-files problem',
              'One file per statement is harmless three times and disastrous a hundred thousand times. (Volumes illustrative.)',
              'Small files', 'A job inserting rows every minute creates over a hundred thousand files; batching and compaction fix it', [f1, f2, f3, f4, f5],
              ['A job inserts a few rows every minute with INSERT … VALUES.',
               'After 90 days the table has 129,600 tiny files; queries spend their time opening files.',
               'Batch the writes so each insert writes large files.',
               'Rewrite existing small files into large ones, or rely on compaction for ACID and Iceberg tables.',
               'Hive is a batch engine; streams should be landed and compacted, not inserted row by row.'],
              hid='scenario-smallfiles')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Six loads, two views</h2>
  <p>Left: Beeline’s real output. Right: the files in the table folder after each statement.</p>
''' + two + '''
  <p>Three live scenarios follow: retry-safe loads, raw-to-curated pipelines and the small-files problem.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Loading in daily pipelines</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'OVERWRITE', 8.6, 'green', bold=True, mono=True) + t(60, 58, 'nightly rebuild', 7.4, 'ink2'),
    '1. Nightly curated tables',
    'Most warehouse jobs are <code>INSERT OVERWRITE … SELECT</code> from raw into curated tables, partition by partition. A failed night is simply re-run.',
    ['Raw', '*INSERT OVERWRITE', 'Curated ORC']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'FROM … INSERT', 8, 'violet', bold=True, mono=True) + t(60, 58, 'fan-out', 7.4, 'ink2'),
    '2. Splitting a big feed',
    'A payments feed is split into UPI, card and wallet tables in one multi-insert, reading terabytes once instead of three times.',
    ['Payments feed', '*Multi-insert', '3 tables']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'CTAS', 10, 'acc', bold=True, mono=True) + t(60, 58, 'analysis copy', 7.4, 'ink2'),
    '3. Analyst working tables',
    'Analysts create a filtered copy with CTAS (“orders of the Diwali week”) in their sandbox and explore it quickly, without touching shared tables.',
    ['Big table', '*CTAS', 'Sandbox table']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'LOAD', 10, 'blue', bold=True, mono=True) + t(60, 58, 'move landed file', 7.4, 'ink2'),
    '4. Moving landed files',
    'When a transfer tool drops a ready-made file in HDFS, <code>LOAD DATA INPATH … OVERWRITE</code> moves it into the table in milliseconds, with no job.',
    ['Transfer tool', '*LOAD (move)', 'Table']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:#D64545"/>' + t(60, 42, 'COUNT = DISTINCT', 7.6, 'red', bold=True, mono=True) + t(60, 58, 'load check', 7.4, 'ink2'),
    '5. Post-load quality checks',
    'After every load a job compares row counts with the source and with distinct keys, and stops the pipeline if they differ.',
    ['Load', '*Checks', 'Publish or stop']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> you need the <code>orders_ext</code> table from <a href="../02-managed-vs-external-tables/">Lesson 2.2</a> and the SerDe ideas from <a href="../04-row-formats-and-serdes/">Lesson 2.4</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
