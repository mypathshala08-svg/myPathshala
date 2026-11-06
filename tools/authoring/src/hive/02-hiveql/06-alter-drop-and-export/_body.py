import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()

# ---------------------------------------------------------------- story
sc = (box(10, 14, 300, 126, 'card') + t(160, 32, 'The file (never rewritten by ALTER)', 8.8, bold=True) +
      ''.join(t(24, 54 + k * 15, s, 8.2, anchor='start', mono=True) for k, s in enumerate(['1,Poha,40', '2,Misal Pav,80', '3,Masala Chai,15,Beverage'])) +
      t(160, 122, 'position 1 · 2 · 3 · 4', 8, 'ink2', mono=True) +
      box(330, 14, 300, 58, 'green') + t(480, 32, 'ADD COLUMNS (category)', 8.6, 'green', bold=True, mono=True) + t(480, 52, 'old rows: category = NULL ✓', 8.4) +
      box(330, 82, 300, 58, 'red') + t(480, 100, 'REPLACE COLUMNS (id, name, category)', 8.2, 'red', bold=True, mono=True) + t(480, 120, 'category now shows 40, 80, 15 ✗', 8.4))
scene_svg = scene('A text file stays unchanged while ALTER TABLE changes only the column list; adding a column is safe, replacing columns shifts values into the wrong column.', sc,
                  'ALTER changes the <tspan font-weight="700" class="s-acc">label</tspan>, not the file: columns are matched by position.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“I removed the price column and now category says 40”</h2>
  <div class="story">
    <p class="narration">The menu table needs changes: a new <code>category</code> column, a clearer name for <code>price</code>, a new table name, and finally a CSV export for the finance team. Kabir also wants to drop the price column. After his <code>REPLACE COLUMNS</code>, the category of Poha shows <code>40</code>.</p>

{scene_svg}

K> Sir, I only changed the table definition. Where did 40 come from?
A> From the file. ALTER TABLE changes <b>metadata</b>; it does not rewrite data files. For a text table, columns are matched to the file by <b>position</b>. You told Hive the third column is now category, so Hive reads the third value on each line, the old price, as the category.
R> So which ALTER statements are safe?
A> Adding columns at the end, renaming a column, widening a type (INT to BIGINT), changing properties: all metadata-only and safe. Removing or reordering columns, or narrowing types, can scramble or lose data; Hive refuses some of them and silently allows others. Today we try each, then rename, truncate, drop and export, with the files in view.
  </div>
</section>
'''

lv = '''
LEVELS> Changing tables at three levels
L1> Relabelling boxes
      <ul>
        <li><b>ALTER TABLE</b> rewrites the label on the box. The things inside (files) are not touched.</li>
        <li>Adding a new heading at the end is fine: old items simply have nothing under it (NULL).</li>
        <li>Crossing out a heading in the middle makes every heading after it point at the wrong item.</li>
        <li><b>TRUNCATE</b> empties the box; <b>DROP</b> throws the box away; <b>EXPORT</b> packs a copy to send elsewhere.</li>
      </ul>
L2> The statements
      <ul>
        <li><code>ALTER TABLE t RENAME TO t2</code>: for warehouse tables (managed or purge) the folder is renamed too; for plain external tables only the name changes.</li>
        <li><code>ALTER TABLE t ADD COLUMNS (c TYPE)</code>: added at the end; existing rows read NULL.</li>
        <li><code>ALTER TABLE t CHANGE old new TYPE [COMMENT …]</code>: rename and/or retype one column.</li>
        <li><code>ALTER TABLE t REPLACE COLUMNS (…)</code>: replace the whole column list (the way to “drop” columns).</li>
        <li><code>ALTER TABLE t SET TBLPROPERTIES (…)</code>, <code>SET LOCATION '…'</code>, <code>ALTER DATABASE d SET DBPROPERTIES (…)</code>.</li>
        <li><code>TRUNCATE TABLE t</code>, <code>DROP TABLE [IF EXISTS] t [PURGE]</code>.</li>
        <li>Export: <code>INSERT OVERWRITE [LOCAL] DIRECTORY '…' ROW FORMAT … SELECT …</code>; backup/move: <code>EXPORT TABLE … TO</code> / <code>IMPORT TABLE … FROM</code>.</li>
      </ul>
L3> Rules confirmed in the lab
      <ul>
        <li><b>Positional mapping</b>: delimited text maps columns by position; our REPLACE COLUMNS put prices into category. For an ORC table Hive refused the same kind of change: “Replacing columns cannot drop columns … SerDe may be incompatible”.</li>
        <li><b>Type checks</b>: <code>CHANGE city city INT</code> on an ORC table was refused (“types incompatible with the existing columns”); <code>INT → BIGINT</code> was accepted.</li>
        <li><b>CHANGE INT → DECIMAL(8,2)</b> on text worked: 40 became 40.00, because text is re-parsed on every read.</li>
        <li><b>Rename moves the folder</b> for warehouse tables (<code>menu_t/</code> became <code>menu_items/</code>); an external table kept <code>file:/data/tiffingo/menu_csv</code>.</li>
        <li><b>EXPORT</b> writes a <code>_metadata</code> file plus a <code>data/</code> folder; IMPORT can create the table under a new name.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Changing, removing and exporting tables</h2>
''' + def_block(
    '<b>ALTER TABLE</b> modifies a table’s metadata in the metastore: its name, columns (ADD, CHANGE, REPLACE COLUMNS), properties, SerDe or location; it does not rewrite existing data files, so columns of existing files are interpreted according to the new definition (for delimited text, by <b>position</b>). <b>TRUNCATE TABLE</b> removes all rows of a managed-style table while keeping its definition; <b>DROP TABLE</b> removes the definition and, for managed or purge tables, the data. Data leaves Hive with <b>INSERT OVERWRITE [LOCAL] DIRECTORY … SELECT</b> (files in a chosen format) or <b>EXPORT TABLE</b> (data plus metadata for a later <b>IMPORT</b>).',
    'ALTER changes the table’s description, not its files, so Hive reads old files with the new column list in column order. TRUNCATE empties a table, DROP removes it, and you can write query results to a folder or export a whole table to import elsewhere.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Schema evolution', 'Changing a table’s columns over time while old data stays readable.'),
    ('Positional mapping', 'Column 3 of the definition reads value 3 of each record, whatever its name.'),
    ('Widening', 'Changing to a type that holds every old value (INT → BIGINT, INT → DECIMAL with room).'),
    ('Narrowing', 'A type that cannot hold every old value (BIGINT → INT, STRING → INT). Risky or refused.'),
    ('REPLACE COLUMNS', 'Swap the whole column list; used to remove columns, dangerous for positional formats.'),
    ('PURGE', 'With DROP: delete files immediately instead of moving them to the HDFS trash.'),
    ('EXPORT / IMPORT', 'Copy a table’s data and metadata to a path, and recreate it from there.'),
    ('DIRECTORY export', 'INSERT OVERWRITE DIRECTORY: write any query result as files in a folder.'),
]) + '''

  <h3>How safe is each change? (tested on text and ORC tables)</h3>
''' + table(['Change', 'Statement', 'Effect on existing data', 'Verdict'], [
    ['Add a column at the end', '<code>ADD COLUMNS (category STRING)</code>', 'Old rows read NULL', '<b>Safe</b>'],
    ['Rename a column', '<code>CHANGE price price_rs INT</code>', 'Same position, new name', '<b>Safe</b> (update queries)'],
    ['Widen a type', '<code>CHANGE amount amount BIGINT</code>', 'Values unchanged', '<b>Safe</b>'],
    ['Narrow or change type', '<code>CHANGE city city INT</code>', 'Refused in our lab (ORC)', 'Blocked / risky'],
    ['Remove a middle column', '<code>REPLACE COLUMNS (id, name, category)</code>', 'Text: later columns read the wrong values. ORC: refused', '<b>Dangerous</b>'],
    ['Reorder columns', '<code>CHANGE c c TYPE AFTER x</code>', 'Values stay in old positions', '<b>Dangerous</b>'],
    ['Rename a table', '<code>RENAME TO new</code>', 'Warehouse folder renamed', 'Safe; update readers'],
    ['Move data location', "<code>SET LOCATION '…'</code>", 'Table now reads another folder', 'Careful'],
], minw=720) + lv + '''
EXAM> “Write ALTER TABLE commands for: rename a table, add a column, rename a column.” <code>ALTER TABLE menu RENAME TO menu_items;</code> <code>ALTER TABLE menu_items ADD COLUMNS (category STRING);</code> <code>ALTER TABLE menu_items CHANGE price price_rs INT;</code> Then state that ALTER changes metadata only.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Getting data out of Hive</h2>
''' + table(['Method', 'Output', 'Use when'], [
    ["<code>INSERT OVERWRITE LOCAL DIRECTORY '/x' ROW FORMAT DELIMITED … SELECT …</code>", 'Files on the HiveServer2 host', 'A file for another team or tool (small results)'],
    ["<code>INSERT OVERWRITE DIRECTORY 'hdfs://…/x' STORED AS ORC SELECT …</code>", 'Files in the cluster file system', 'Handing data to Spark or another job'],
    ['<code>beeline --outputformat=csv2 -e "SELECT …" &gt; out.csv</code>', 'A CSV on the client machine', 'Small reports; everything streams through HiveServer2'],
    ["<code>EXPORT TABLE t TO '/backup/t'</code>", '<code>_metadata</code> + <code>data/</code>', 'Moving a table to another cluster, simple backups'],
    ["<code>IMPORT TABLE t2 FROM '/backup/t'</code>", 'A recreated table', 'Restoring or copying under a new name'],
], minw=680) + '''
WARN> <code>INSERT OVERWRITE DIRECTORY</code> first deletes everything in the target folder. Never point it at a folder that holds anything else, and especially not at a table’s location.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Change a table, then take data out</h2>
  <p>All outputs are real, from the Hive 4.2.1 lab.</p>
''' + stepper([
    ('Step 1 · Add a column at the end',
     code('sql', 'Beeline', "CREATE TABLE menu_t (item_id INT, name STRING, price INT)\n  ROW FORMAT DELIMITED FIELDS TERMINATED BY ',';\nINSERT INTO menu_t VALUES (1,'Poha',40),(2,'Misal Pav',80);\nALTER TABLE menu_t ADD COLUMNS (category STRING COMMENT 'meal type');\nINSERT INTO menu_t VALUES (3,'Masala Chai',15,'Beverage');\nSELECT * FROM menu_t ORDER BY item_id;", capf('l26_alter.txt').split('+-------------+')[0].rstrip()),
     'Old lines have only three values, so the new fourth column is NULL for them. New rows fill it. No file was rewritten.'),
    ('Step 2 · Rename a column and the table',
     code('sql', 'Beeline', "ALTER TABLE menu_t CHANGE price price_rs INT COMMENT 'price in rupees';\nALTER TABLE menu_t RENAME TO menu_items;\nSELECT item_id, name, price_rs, category FROM menu_items ORDER BY item_id;",
          '+----------+--------------+-----------+-----------+\n| item_id  |     name     | price_rs  | category  |\n+----------+--------------+-----------+-----------+\n| 1        | Poha         | 40        | NULL      |\n| 2        | Misal Pav    | 80        | NULL      |\n| 3        | Masala Chai  | 15        | Beverage  |\n+----------+--------------+-----------+-----------+\n\n$ ls /opt/hive/data/warehouse/tiffingo.db | grep menu\nmenu_items\n$ cat …/menu_items/*\n1,Poha,40\n2,Misal Pav,80\n3,Masala Chai,15,Beverage'),
     'The column keeps its position, so values are unchanged. Renaming moved the warehouse folder <code>menu_t/</code> to <code>menu_items/</code>. The files still contain only raw values: the names live in the metastore.'),
    ('Step 3 · REPLACE COLUMNS shifts data',
     code('sql', 'Beeline', "CREATE TABLE menu_shift LIKE menu_items;\nINSERT INTO menu_shift SELECT * FROM menu_items;\nALTER TABLE menu_shift REPLACE COLUMNS (item_id INT, name STRING, category STRING);\nSELECT * FROM menu_shift ORDER BY item_id;", capf('l26_replace.txt')),
     'Hive accepted the change without a warning. The third value on each line was the price, so “category” now shows 40, 80 and 15. For an ORC table Hive refused this change (“Replacing columns cannot drop columns”). To really remove a column, create a new table and <code>INSERT … SELECT</code> the columns you keep.'),
    ('Step 4 · Type changes: widen yes, incompatible no',
     code('sql', 'Beeline', "ALTER TABLE upi_orders CHANGE city city INT;        -- ORC table\nALTER TABLE upi_orders CHANGE amount amount BIGINT;\nALTER TABLE menu_items CHANGE price_rs price_rs DECIMAL(8,2);   -- text table\nSELECT * FROM menu_items ORDER BY item_id;",
          capf('l26_incompat.txt').split(':\n')[0] + ' …\n(amount → BIGINT: accepted)\n' + '\n'.join(capf('l26_misc.txt').split('\n')[13:20])),
     'Turning a STRING into an INT was refused for the ORC table. Widening INT to BIGINT and INT to DECIMAL were accepted; on the text table <code>40</code> now reads as <code>40.00</code>, because text is converted again on every read.'),
    ('Step 5 · Properties, TRUNCATE and DROP … PURGE',
     code('sql', 'Beeline', "ALTER TABLE menu_items SET TBLPROPERTIES ('owner_team'='menu');\nSHOW TBLPROPERTIES menu_items ('owner_team');\nTRUNCATE TABLE menu_items;\nSELECT COUNT(*) AS after_truncate FROM menu_items;\nDROP TABLE menu_items PURGE;",
          '\n'.join(capf('l26_misc.txt').split('\n')[0:5]) + '\n+-----------------+\n| after_truncate  |\n+-----------------+\n| 0               |\n+-----------------+'),
     'Properties are free-form labels useful for ownership and tooling. TRUNCATE kept the four columns but removed all rows. DROP … PURGE removed the table and its files without using a trash folder.'),
    ('Step 6 · Export a query result as CSV',
     code('sql', 'Beeline', "INSERT OVERWRITE LOCAL DIRECTORY '/data/exports/city_sales_csv'\nROW FORMAT DELIMITED FIELDS TERMINATED BY ','\nSELECT city, orders, revenue FROM city_sales ORDER BY revenue DESC;",
          '$ ls /data/exports/city_sales_csv\n000000_0\n$ head -3 /data/exports/city_sales_csv/000000_0\nMumbai,9250,2712820\nBengaluru,8535,2499060\nPune,7269,2148270'),
     'The result is written as ordinary files named like task outputs. Without <code>ROW FORMAT</code> Hive would use its default separator (Ctrl-A, <code>\\001</code>), which surprises spreadsheet users. There is no header line; add one in the tool that consumes the file.'),
    ('Step 7 · EXPORT, DROP, IMPORT',
     code('sql', 'Beeline', "EXPORT TABLE city_sales TO 'file:///data/exports/city_sales_bkp';\nDROP TABLE city_sales;\nIMPORT TABLE city_sales_restored FROM 'file:///data/exports/city_sales_bkp';\nSELECT COUNT(*) AS restored_rows FROM city_sales_restored;",
          capf('l26_export.txt') + '\n\n$ find /data/exports/city_sales_bkp -not -name ".*"\n…/city_sales_bkp/_metadata\n…/city_sales_bkp/data\n…/city_sales_bkp/data/000000_0'),
     'EXPORT wrote the table definition (<code>_metadata</code>) and the data files. After the DROP, IMPORT recreated it, under a new name, with all 8 rows. This also works between clusters when the folder is copied across.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
FILE = ['1,Poha,40', '2,Misal Pav,80', '3,Masala Chai,15,Beverage']
def view(cols, rows, tones=None, title='Columns Hive applies'):
    o = box(10, 40, 150, 70, 'card') + t(85, 54, 'file (unchanged)', 7.8, bold=True)
    for k, ln in enumerate(FILE):
        o += t(16, 70 + k * 13, ln, 7, 'ink', anchor='start', mono=True)
    o += box(170, 40, 180, 22, 'violet') + t(260, 55, ' · '.join(cols), 7.2, bold=True, mono=True)
    for k, r in enumerate(rows):
        o += t(176, 80 + k * 14, r, 7.4, (tones or ['ink'] * 3)[k], anchor='start', mono=True)
    return o
see = [
    term([('> ALTER TABLE menu_t ADD COLUMNS', W), ('  (category STRING);', W), ('> SELECT * FROM menu_t;', W), ('| 1 | Poha        | 40 | NULL     |', G), ('| 2 | Misal Pav   | 80 | NULL     |', G), ('| 3 | Masala Chai | 15 | Beverage |', G)]),
    term([('> ALTER TABLE menu_t CHANGE price price_rs INT;', W), ('> ALTER TABLE menu_t RENAME TO menu_items;', W), ('> SHOW TABLES LIKE \'menu%\';', W), ('| menu_items |', G)]),
    term([('> ALTER TABLE menu_shift REPLACE COLUMNS', W), ('  (item_id INT, name STRING, category STRING);', W), ('> SELECT * FROM menu_shift;', W), ('| 1 | Poha        | 40 |', RD), ('| 2 | Misal Pav   | 80 |', RD), ('| 3 | Masala Chai | 15 |', RD)]),
    term([('> ALTER TABLE upi_orders CHANGE city city INT;', W), ('Error: … Unable to alter table. The following', RD), ('  columns have types incompatible with the', RD), ('  existing columns in their respective positions', RD), ('> … CHANGE amount amount BIGINT;   (accepted)', G)], size=7.6),
    term([("> INSERT OVERWRITE LOCAL DIRECTORY", W), ("  '/data/exports/city_sales_csv'", W), ("  ROW FORMAT DELIMITED FIELDS TERMINATED BY ','", W), ('  SELECT …;', W), ('$ head -2 …/000000_0', W), ('Mumbai,9250,2712820', G), ('Bengaluru,8535,2499060', G)]),
    term([("> EXPORT TABLE city_sales TO '…/city_sales_bkp';", W), ('> DROP TABLE city_sales;', W), ("> IMPORT TABLE city_sales_restored FROM '…';", W), ('> SELECT COUNT(*) FROM city_sales_restored;', W), ('| 8 |', G)]),
]
B1 = [
    t(180, 22, 'ADD COLUMNS: a 4th name, nothing rewritten', 9.2, bold=True) + view(['item_id', 'name', 'price', 'category'], ['1 Poha 40 NULL', '2 Misal Pav 80 NULL', '3 Masala Chai 15 Beverage'], ['green'] * 3) +
    cap('Short lines simply have no 4th value → NULL.', '', 'green', y=150, h=34),
    t(180, 22, 'CHANGE renames, RENAME moves the folder', 9.2, bold=True) + view(['item_id', 'name', 'price_rs', 'category'], ['1 Poha 40 NULL', '…'], ['green', 'ink']) + t(260, 120, 'menu_t/ → menu_items/', 8, 'acc', bold=True, mono=True) +
    cap('Same positions, new names.', 'External tables keep their folder on RENAME.', 'blue', y=150, h=46),
    t(180, 22, 'REPLACE COLUMNS: positions shift', 9.2, 'red', bold=True) + view(['item_id', 'name', 'category'], ['1 Poha 40', '2 Misal Pav 80', '3 Masala Chai 15'], ['red'] * 3) +
    cap('Column 3 is still the price in the file.', 'Hive shows it as category. No warning.', 'red', y=150, h=46),
    t(180, 22, 'Type changes are checked', 9.2, bold=True) + label_box(14, 46, 160, 60, ['city STRING → INT', 'refused (incompatible)'], 'red', 8.2) + label_box(186, 46, 160, 60, ['amount INT → BIGINT', 'accepted (widening)'], 'green', 8.2) +
    t(180, 126, 'text table: INT → DECIMAL(8,2) read 40 as 40.00', 8, 'ink2') + cap('Widen freely; never narrow in place.', '', 'blue', y=150, h=34),
    t(180, 22, 'DIRECTORY export writes plain files', 9.2, bold=True) + label_box(14, 50, 120, 50, ['query result', '8 rows'], 'acc', 8.4) + arrow(136, 75, 168, 75, 'green', 2) + box(170, 44, 176, 62, 'green') + t(258, 62, 'city_sales_csv/', 8, bold=True, mono=True) + t(258, 80, '000000_0 (167 bytes)', 7.6, 'ink2', mono=True) + t(258, 94, 'no header line', 7.6, 'amber', bold=True) +
    cap('OVERWRITE empties the folder first!', '', 'amber', y=150, h=34),
    t(180, 22, 'EXPORT = data + metadata', 9.2, bold=True) + box(14, 44, 160, 80, 'blue') + t(94, 60, 'city_sales_bkp/', 8, bold=True, mono=True) + t(24, 80, '_metadata', 7.6, 'ink', anchor='start', mono=True) + t(24, 94, 'data/000000_0', 7.6, 'ink', anchor='start', mono=True) +
    arrow(176, 84, 196, 84, 'green', 2) + label_box(198, 54, 148, 60, ['IMPORT TABLE', 'city_sales_restored', '8 rows'], 'green', 8) + cap('Restore anywhere, even under a new name.', '', 'green', y=150, h=34),
]
see_caps = ['A category column is added. Old rows show NULL, the new row shows Beverage.',
            'A column and the table are renamed. Queries use the new names.',
            'REPLACE COLUMNS removes price from the definition; category now shows prices.',
            'An incompatible type change is refused; widening a type is accepted.',
            'A query result is exported as a comma-separated file.',
            'The table is exported, dropped and imported again with all 8 rows.']
behind_caps = ['ALTER only changed the metastore. Lines with three values have no fourth value, so category is NULL.',
               'CHANGE keeps the position; RENAME of a warehouse table also renames its folder.',
               'Text columns are matched by position. The third value of each line is still the price.',
               'Hive checks types against existing data positions for formats like ORC and refuses unsafe changes.',
               'INSERT OVERWRITE DIRECTORY clears the folder and writes task output files, without a header.',
               'EXPORT copies the metadata and the data files; IMPORT rebuilds the table from them.']
two = anim_two('ALTER and friends', 'The file stays, the label changes', 'Real Beeline output', 'The unchanged file and the column list Hive applies to it', see, B1, see_caps, behind_caps)

# ---- scenario 1: safe column removal
d1 = (t(180, 22, 'Request: drop the column “phone” (privacy)', 9.6, bold=True) + t(180, 56, 'customers(id, name, phone, city, plan)', 8.6, 'ink', mono=True) + cap('Tempting: REPLACE COLUMNS without phone.', '', 'amber', y=150, h=34))
d2 = (t(180, 22, 'What REPLACE COLUMNS would do', 9.6, 'red', bold=True) + t(180, 52, 'customers(id, name, city, plan)', 8.6, 'ink', mono=True) + t(180, 76, 'city ← old phone values · plan ← old city values', 8.2, 'red', mono=True) +
      cap('And the phone numbers are still in the files!', 'Metadata change ≠ deletion.', 'red', y=150, h=46))
d3 = (t(180, 22, 'Safe way: rewrite', 9.6, 'green', bold=True) + t(180, 52, 'CREATE TABLE customers_v2 STORED AS ORC AS', 8.2, 'ink', mono=True) + t(180, 66, 'SELECT id, name, city, plan FROM customers;', 8.2, 'ink', mono=True) +
      cap('New files without the column.', '', 'green', y=150, h=34))
d4 = (t(180, 22, 'Swap and clean up', 9.6, 'green', bold=True) + ''.join(t(26, 52 + k * 19, s, 8.4, anchor='start', mono=True) for k, s in enumerate(['verify counts', 'ALTER TABLE customers RENAME TO customers_old;', 'ALTER TABLE customers_v2 RENAME TO customers;', 'DROP TABLE customers_old PURGE;'])) +
      cap('PURGE: the old files really go.', '', 'green', y=150, h=34))
d5 = (t(180, 22, 'Also remember', 9.6, 'acc', bold=True) + ''.join(t(26, 52 + k * 19, s, 8.4, anchor='start') for k, s in enumerate(['• copies: exports, backups, other tables', '• HDFS trash and snapshots keep old files', '• views and jobs that select phone'])) +
      cap('Privacy deletion needs a data search, not one ALTER.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Removing a sensitive column the right way',
              'A privacy request asks to remove phone numbers from a customer table. ALTER alone is wrong twice.',
              'Column removal', 'Removing a column with REPLACE COLUMNS shifts values and leaves data in files; rewriting into a new table removes it', [d1, d2, d3, d4, d5],
              ['The privacy team asks to remove the phone column from customers.',
               'REPLACE COLUMNS would shift later columns and leave phone numbers in the files.',
               'The safe method writes a new table with only the wanted columns.',
               'After checking counts, swap the names and drop the old table with PURGE.',
               'Also clean copies, backups, trash and snapshots, and update dependent jobs.'],
              hid='scenario-privacy')

# ---- scenario 2: schema evolution across formats
e1 = (t(180, 22, 'The app adds a field every month', 9.6, bold=True) + t(180, 56, 'v1: id, city, amount  →  v2: + coupon  →  v3: + tip', 8.4, 'ink', mono=True) + cap('The table must keep reading old files.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Add at the end: works in every format', 9.6, 'green', bold=True) + t(180, 56, 'ALTER TABLE orders ADD COLUMNS (coupon STRING, tip INT);', 8, 'ink', mono=True) + t(180, 80, 'old files → NULL for coupon and tip', 8.4, 'ink2') + cap('Append-only evolution is safe.', '', 'green', y=150, h=34))
e3 = (t(180, 22, 'Removing or reordering', 9.6, 'amber', bold=True) + t(180, 56, 'text: column n = value n → values shift silently', 8.4, 'ink2') + t(180, 74, 'ORC: Hive refused to drop a column (our test)', 8.4, 'ink2') + cap('Never remove or reorder in place.', '', 'amber', y=150, h=34))
e4 = (t(180, 22, 'Name-based formats', 9.6, bold=True) + t(180, 56, 'Parquet and Avro can match columns by name', 8.6, 'ink2') + t(180, 74, '(Parquet by name, Avro with a schema and defaults)', 8.2, 'ink2') + cap('More forgiving, still test first.', 'Module 6.', 'blue', y=150, h=46))
e5 = (t(180, 22, 'Iceberg: evolution by column id', 9.6, 'green', bold=True) + t(180, 56, 'rename, drop, reorder: safe, tracked in metadata', 8.6, 'ink2') + cap('A main reason teams adopt Iceberg.', 'Module 7.', 'green', y=150, h=46))
s2 = anim_one('Real-time scenario 2', 'Schema evolution: what is safe in which format',
              'App data changes shape. Learn which changes every format survives.',
              'Schema evolution', 'Adding columns at the end works everywhere; positional formats break on removals; name-based formats and Iceberg handle more', [e1, e2, e3, e4, e5],
              ['New fields appear in app data every month.',
               'Adding columns at the end works for all formats: old files return NULL.',
               'Delimited text matches by position, so removing a column scrambles data; for ORC, Hive refused to drop the column.',
               'Parquet and Avro can resolve columns by name, which is more forgiving.',
               'Iceberg tracks columns by id, so renames, drops and reorders are safe.'],
              hid='scenario-evolution')

# ---- scenario 3: export for finance
x1 = (t(180, 22, 'Finance wants a monthly CSV', 9.6, bold=True) + t(180, 56, 'city, orders, revenue · opened in a spreadsheet', 8.6, 'ink2') + cap('Three ways to deliver it.', '', 'blue', y=150, h=34))
x2 = (t(180, 22, 'Small: Beeline csv2', 9.6, bold=True) + t(180, 56, 'beeline … --outputformat=csv2 -e "SELECT …" > sales.csv', 7.8, 'ink', mono=True) + t(180, 80, 'header included, streamed through HiveServer2', 8.2, 'ink2') + cap('Fine for thousands of rows.', '', 'green', y=150, h=34))
x3 = (t(180, 22, 'Large: DIRECTORY export', 9.6, bold=True) + t(180, 52, "INSERT OVERWRITE DIRECTORY '/exports/finance/2026-10'", 7.8, 'ink', mono=True) + t(180, 66, "ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' SELECT …;", 7.8, 'ink', mono=True) + t(180, 90, 'many part files, no header', 8.2, 'amber', bold=True) + cap('Parallel writes; merge files for spreadsheet users.', '', 'amber', y=150, h=34))
x4 = (t(180, 22, 'Danger: the target folder', 9.6, 'red', bold=True) + t(180, 56, "INSERT OVERWRITE DIRECTORY '/exports/finance'", 8, 'ink', mono=True) + t(180, 80, 'deletes all earlier months in that folder', 8.4, 'red', bold=True) + cap('Always write to a dated sub-folder.', '', 'red', y=150, h=34))
x5 = (t(180, 22, 'Moving whole tables', 9.6, 'green', bold=True) + t(180, 56, "EXPORT TABLE city_sales TO '/backup/city_sales';", 8, 'ink', mono=True) + t(180, 72, "IMPORT TABLE … FROM '…';  (8 rows restored in the lab)", 8, 'ink', mono=True) + cap('Data + definition travel together.', '', 'green', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Delivering data to people outside Hive',
              'Choose the export method by size and audience, and protect the target folder.',
              'Exports', 'Exporting with Beeline csv2, INSERT OVERWRITE DIRECTORY and EXPORT/IMPORT, and the danger of overwriting a shared folder', [x1, x2, x3, x4, x5],
              ['Finance needs a monthly CSV that opens in a spreadsheet.',
               'For small results, Beeline with csv2 output is simplest and includes a header.',
               'For large results, INSERT OVERWRITE DIRECTORY writes files in parallel, without a header.',
               'OVERWRITE deletes the target folder’s contents first, so always use a fresh, dated folder.',
               'To move a whole table with its definition, use EXPORT and IMPORT.'],
              hid='scenario-export')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Six changes, one unchanged file</h2>
  <p>Left: Beeline’s real output. Right: the file that never changes, and the column list Hive applies to it.</p>
''' + two + '''
  <p>Three live scenarios follow: removing a sensitive column, schema evolution across formats, and exports.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Changes and exports at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, '+ coupon', 9, 'green', bold=True, mono=True) + t(60, 58, 'ADD COLUMNS', 7.4, 'ink2'),
    '1. Growing event schemas',
    'When the app starts sending a new field, engineers add a column at the end of the event table. Old data reads NULL; no rewrite needed.',
    ['New field', '*ADD COLUMNS', 'Reports use it']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:#D64545"/>' + t(60, 42, 'privacy', 9, 'red', bold=True) + t(60, 58, 'rewrite + purge', 7.4, 'ink2'),
    '2. Data protection requests',
    'Removing personal data means rewriting tables without it and purging old files and copies, documented for audit. ALTER alone does not delete anything.',
    ['Request', '*Rewrite table', 'Purge copies']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'v2 → swap', 9, 'blue', bold=True, mono=True) + t(60, 58, 'RENAME', 7.4, 'ink2'),
    '3. Zero-downtime rebuilds',
    'A new version of a table is built beside the old one, verified, then swapped in with two RENAMEs, so readers never see a half-built table.',
    ['Build v2', '*RENAME swap', 'Drop old']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'CSV', 10, 'acc', bold=True, mono=True) + t(60, 58, 'to finance', 7.4, 'ink2'),
    '4. Extracts for other teams',
    'Monthly settlement and GST extracts are written with INSERT OVERWRITE DIRECTORY into dated folders and picked up by a transfer job.',
    ['Query', '*DIRECTORY export', 'SFTP / email']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'EXPORT', 9, 'violet', bold=True, mono=True) + t(60, 58, 'cluster → cluster', 7.4, 'ink2'),
    '5. Moving tables between clusters',
    'EXPORT writes data and metadata to a folder; after copying it (for example with DistCp), IMPORT recreates the table on the other cluster.',
    ['Cluster A', '*EXPORT / IMPORT', 'Cluster B']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> you will reuse <code>city_sales</code> and <code>upi_orders</code> from <a href="../05-loading-data/">Lesson 2.5</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
