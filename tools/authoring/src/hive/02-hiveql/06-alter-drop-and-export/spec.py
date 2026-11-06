import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
BODY = body(HERE)
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep

META = dict(
    module='02-hiveql', lesson='06-alter-drop-and-export', n='2.6',
    module_label='Module 2 · Tables and data',
    title='ALTER, DROP, TRUNCATE and exporting data',
    desc='Change Hive tables safely and get data out: ALTER TABLE RENAME, ADD COLUMNS, CHANGE, REPLACE COLUMNS (positional mapping and shifted values), type widening vs incompatible changes, table properties, TRUNCATE, DROP PURGE, INSERT OVERWRITE [LOCAL] DIRECTORY and EXPORT/IMPORT. Real outputs from Hive 4.2.1.',
    og_desc='ALTER changes the label, not the file. See a removed column turn prices into categories, and learn the safe way to change and export tables.',
    minutes=30, level='Beginner → Advanced',
    lead='Tables change: new columns arrive, names improve, sensitive fields must go, and other teams want extracts. In Hive, <code>ALTER TABLE</code> changes only metadata, so the old files are read with the new definition. That makes adding columns trivial and removing them dangerous. This lesson tests every change, then empties, drops and exports tables, with <b>real Hive 4.2.1 output</b>.',
    chips=['Real Hive 4.2.1 outputs', 'Schema evolution rules', 'EXPORT / IMPORT', 'Runs in your browser (Python)'],
)

MAIN = '''# ALTER changes the column list; the file lines stay the same
file_lines = ["1,Poha,40", "2,Misal Pav,80", "3,Masala Chai,15,Beverage"]

def read(columns):
    for line in file_lines:
        values = line.split(",")
        row = {c: (values[i] if i < len(values) else None) for i, c in enumerate(columns)}
        print(row)

print("ADD COLUMNS (category):")
read(["item_id", "name", "price", "category"])
print("REPLACE COLUMNS without price:")
read(["item_id", "name", "category"])
'''
RUN = dict(
    heading='Run the code: positional reading after ALTER',
    intro='<p>The same three file lines are read with different column lists, just as Hive reads a text table after ALTER. Watch which changes keep values in place and which shift them. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('row = {c: (values[i] if i < len(values) else None) for i, c in enumerate(columns)}', 'Column <i>i</i> takes value <i>i</i> of the line, whatever its name: positional mapping. Missing values become None (NULL).'),
        ('read(["item_id", "name", "category"])', 'The third value is still the price, so “category” shows 40, 80 and 15, as in the lab.'),
    ],
    tasks=[
        dict(label='1 · ADD vs REPLACE', hint='Press <b>Run</b>. Then try a rename only: <code>["item_id", "name", "price_rs", "category"]</code>. Values stay in place.', code=None),
        dict(label='2 · Is this type change safe?', hint='<b>Predict first:</b> which changes are widening? A change is safe if every old value fits the new type.',
             code='''ranges = {"TINYINT": 127, "SMALLINT": 32767, "INT": 2147483647, "BIGINT": 9223372036854775807}
changes = [("INT", "BIGINT"), ("BIGINT", "INT"), ("SMALLINT", "INT"), ("INT", "TINYINT")]
for old, new in changes:
    safe = ranges[new] >= ranges[old]
    print(f"{old:8} -> {new:8}: {'widening, safe' if safe else 'narrowing, risky'}")
'''),
        dict(label='3 · Safe column removal', hint='Instead of REPLACE COLUMNS, build new rows that keep only the wanted columns (like CTAS). Remove <code>phone</code>.',
             code='''rows = [{"id": 1, "name": "Aarav", "phone": "+91-00000-00001", "city": "Pune"},
        {"id": 2, "name": "Diya", "phone": "+91-00000-00002", "city": "Thane"}]
keep = ["id", "name", "city"]
new_rows = [{c: r[c] for c in keep} for r in rows]
print(new_rows)
'''),
        dict(label='4 · Export as CSV text', hint='Write rows the way INSERT OVERWRITE DIRECTORY with a comma delimiter does: no header. Then add a header line yourself.',
             code='''rows = [("Mumbai", 9250, 2712820), ("Bengaluru", 8535, 2499060), ("Pune", 7269, 2148270)]
lines = [",".join(str(v) for v in r) for r in rows]
print("\\n".join(lines))
'''),
        dict(label='5 · Spot the error', hint='A script exports to the shared folder <code>/exports/finance</code> with OVERWRITE every month. The check fails because last month’s file disappears. Write to a dated sub-folder instead.', expect='error',
             code='''folders = {"/exports/finance": ["2026-09.csv"]}
def insert_overwrite_directory(path, filename):
    folders[path] = [filename]          # OVERWRITE empties the folder first
insert_overwrite_directory("/exports/finance", "2026-10.csv")
assert "2026-09.csv" in sum(folders.values(), []), "September export was deleted!"
print(folders)
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: more ALTER behaviour',
    intro='<p>Try these on the lab. <b>The outputs are real</b>, from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · Drop a column from an ORC table', cmd="CREATE TABLE orc_evo (order_id INT, city STRING, label STRING) STORED AS ORC;\nINSERT INTO orc_evo VALUES (1,'Pune','A'),(2,'Thane','B');\nALTER TABLE orc_evo REPLACE COLUMNS (order_id INT, label STRING);", file='Beeline',
             output=open(CAP + 'l26_orc_replace.txt').read().rstrip().split('; Query ID')[0],
             note='For ORC, Hive refused to drop a column. (The ORC file records its own schema, <code>struct&lt;order_id:int,city:string,label:string&gt;</code>, as <code>--orcfiledump</code> shows.) For delimited text the same statement was accepted and shifted the values.'),
        dict(title='2 · A renamed external table keeps its folder', cmd="CREATE EXTERNAL TABLE ext_ren (a STRING) LOCATION 'file:///data/tiffingo/menu_csv';\nALTER TABLE ext_ren RENAME TO ext_ren2;\nDESCRIBE FORMATTED ext_ren2;     -- Location line", file='Beeline',
             output='| Location:                     | file:/data/tiffingo/menu_csv                       | NULL                  |',
             note='Only the name changed. Hive does not move files it does not own; a warehouse table’s folder, by contrast, was renamed along with the table.'),
        dict(title='3 · Database properties', cmd="ALTER DATABASE tiffingo SET DBPROPERTIES ('owner_team'='data-eng', 'tier'='curated');\nDESCRIBE DATABASE EXTENDED tiffingo;", file='Beeline',
             output='| db_name  | comment                     | location                                  | owner_name | parameters                            |\n| tiffingo | TiffinGo food delivery data | file:/opt/hive/data/warehouse/tiffingo.db | hive       | {owner_team=data-eng, tier=curated}  |\n(columns trimmed)',
             note='Properties are labels for people and tools (owners, layers, retention). They change no data.'),
    ],
)

TRACE = dict(
    heading='Reading one line after REPLACE COLUMNS',
    intro='<p>Follow the value positions. The name list changes; the values in the line do not.</p>',
    code='''line = "1,Poha,40"
old_cols = ["item_id", "name", "price"]
new_cols = ["item_id", "name", "category"]
values = line.split(",")
before = dict(zip(old_cols, values))
after = dict(zip(new_cols, values))
print(before)
print(after)
''',
    notes={4: 'File :: The file still has the same three values.', 6: 'Shift :: Position 3 is now called category, but it holds the price.'},
)

WORKED_INTRO = 'Three change-management tasks: classifying requested ALTERs, generating a safe rewrite for a column removal, and planning monthly exports that never overwrite each other.'
EXAMPLES = [
    dict(level='b', tag='Change review', title='Classify requested schema changes',
         problem='<p>The team submits schema changes for a text table. Label each as safe (metadata only) or needs a rewrite.</p>',
         inp='add column tip at end · rename price → price_rs · remove phone · widen amount INT → BIGINT · move city to first position',
         approach=['Safe: add at end, rename, widen.', 'Rewrite: remove, reorder, narrow.', 'Print the plan.'],
         code='''changes = [("add", "tip"), ("rename", "price"), ("remove", "phone"), ("widen", "amount"), ("reorder", "city")]
safe_kinds = {"add", "rename", "widen"}
for kind, col in changes:
    verdict = "ALTER only (safe)" if kind in safe_kinds else "rewrite with CTAS/INSERT"
    print(f"{kind:8} {col:7} -> {verdict}")
''', notes={3: 'Rule :: Removing and reordering break positional formats.'},
         tryit='Add ("narrow", "order_id") and decide. Narrowing can turn values into NULL or garbage, so it always needs a rewrite with a check.'),
    dict(level='i', tag='Change · SQL', title='Generate the rewrite for a column removal',
         problem='<p>Given a table name and its columns, generate the four statements that remove a column safely: CTAS without it, a count check, RENAME swap, DROP old PURGE.</p>',
         inp='customers(id, name, phone, city, plan) · remove phone',
         approach=['Build the column list without the removed column.', 'Generate CTAS into table_v2.', 'Add check, swap and drop statements.'],
         code='''table, cols, remove = "customers", ["id", "name", "phone", "city", "plan"], "phone"
keep = ", ".join(c for c in cols if c != remove)
sql = [
    f"CREATE TABLE {table}_v2 STORED AS ORC AS SELECT {keep} FROM {table};",
    f"SELECT (SELECT COUNT(*) FROM {table}) = (SELECT COUNT(*) FROM {table}_v2) AS same_rows;",
    f"ALTER TABLE {table} RENAME TO {table}_old; ALTER TABLE {table}_v2 RENAME TO {table};",
    f"DROP TABLE {table}_old PURGE;",
]
print("\\n".join(sql))
''', notes={2: 'Keep :: Only the columns you keep are written to new files.'},
         tryit='Run the DROP only after the check returns true. In production, also look for views and jobs that select the removed column.'),
    dict(level='a', tag='Exports · planning', title='Dated export folders and retention',
         problem='<p>Finance gets a monthly export. Generate the folder for each month, and list which folders to delete to keep only the last 3 months.</p>',
         inp='months 2026-06 … 2026-10 · keep 3',
         approach=['Build /exports/finance/YYYY-MM for each month.', 'Sort and keep the newest 3.', 'Everything older is deleted by a separate, careful job.'],
         code='''months = ["2026-06", "2026-07", "2026-08", "2026-09", "2026-10"]
folders = [f"/exports/finance/{m}" for m in months]
keep = sorted(folders)[-3:]
delete = [f for f in folders if f not in keep]
print("write :", folders[-1])
print("keep  :", keep)
print("delete:", delete)
''', notes={3: 'Retain :: Deletion is a decision, not a side effect of OVERWRITE.'},
         tryit='Compare with writing every month to /exports/finance with OVERWRITE: only the latest month would ever exist.'),
]

QUIZ = mix([
    dict(q='Beginner: What does ALTER TABLE … ADD COLUMNS do to existing data files?', options=['Rewrites them with the new column', 'Nothing; old rows read NULL for the new column', 'Deletes them', 'Converts them to ORC'], answer=1,
         why='ALTER changes metadata only. Our old menu rows showed NULL for category.'),
    dict(q='Beginner: Which statement renames a table?', options=['RENAME TABLE a b', 'ALTER TABLE a RENAME TO b', 'ALTER TABLE a CHANGE b', 'UPDATE TABLE a SET NAME b'], answer=1,
         why='ALTER TABLE menu_t RENAME TO menu_items;'),
    dict(q='Beginner: What does TRUNCATE TABLE keep?', options=['Nothing', 'The table definition, but no rows', 'The rows, but no definition', 'Only the first row'], answer=1,
         why='After TRUNCATE the count was 0 and DESCRIBE still showed all four columns.'),
    dict(q='Intermediate: After REPLACE COLUMNS removed price from a text table, what did category show?', options=['NULL', 'The old price values', 'An error', 'The category values'], answer=1,
         why='Text columns are mapped by position; the third value of each line was the price.'),
    dict(q='Intermediate: Which type change did Hive accept on the ORC table?', options=['city STRING → INT', 'amount INT → BIGINT', 'Both', 'Neither'], answer=1,
         why='Widening INT to BIGINT is compatible; STRING to INT was refused as incompatible.'),
    dict(q='Intermediate: What happens to an external table’s folder on ALTER TABLE … RENAME?', options=['It is renamed too', 'It stays where it is; only the name changes', 'It is deleted', 'It is copied'], answer=1,
         why='ext_ren2 still pointed at file:/data/tiffingo/menu_csv. Warehouse tables, by contrast, had their folder renamed.'),
    dict(q='Advanced: What does EXPORT TABLE write?', options=['Only a CSV file', 'A _metadata file with the definition plus a data folder', 'Only the metastore rows', 'A SQL dump'], answer=1,
         why='IMPORT later rebuilt city_sales_restored with all 8 rows from those two parts.'),
    dict(q='Advanced: Why is INSERT OVERWRITE DIRECTORY to a shared folder dangerous?', options=['It is slow', 'It first deletes everything already in that folder', 'It writes ORC only', 'It needs ACID'], answer=1,
         why='Always export into a new, dated sub-folder.'),
])

REVISION = [
    'ALTER TABLE = <b>metadata only</b>; files are not rewritten.',
    'Safe: <code>ADD COLUMNS</code> (at the end, old rows NULL), rename with <code>CHANGE</code>, widen types (INT → BIGINT, → DECIMAL).',
    'Dangerous: <code>REPLACE COLUMNS</code> / reorder on text (values shift); ORC refused the drop; incompatible type changes refused.',
    '<code>RENAME TO</code>: warehouse folder renamed; external folder untouched.',
    "<code>SET TBLPROPERTIES</code> / <code>SHOW TBLPROPERTIES</code>; <code>ALTER DATABASE … SET DBPROPERTIES</code>.",
    '<code>TRUNCATE</code> keeps the definition; <code>DROP … PURGE</code> skips the trash.',
    "Export: <code>INSERT OVERWRITE [LOCAL] DIRECTORY '…' ROW FORMAT DELIMITED … SELECT</code> (no header, folder emptied first) · Beeline csv2 for small results.",
    "<code>EXPORT TABLE t TO '…'</code> → <code>_metadata</code> + <code>data/</code>; <code>IMPORT TABLE t2 FROM '…'</code>. Remove columns by rewriting (CTAS → check → RENAME swap → DROP PURGE).",
]
FAQ = [
    ('How do I drop a column in Hive?', 'There is no DROP COLUMN for classic Hive tables. REPLACE COLUMNS can redefine the list, but for delimited text it shifts values and for ORC Hive refused it in our test; either way the old data stays in the files. The reliable way is to create a new table with the columns you keep (CTAS or INSERT … SELECT), verify it, swap names and drop the old table. Iceberg tables support DROP COLUMN safely.'),
    ('Why did changing INT to DECIMAL work on the text table but changing STRING to INT failed on ORC?', 'For text, values are re-parsed from characters on every read, so a new numeric type simply parses “40” as 40.00. Hive checks type changes for compatibility with the stored data; widening numeric changes are allowed, while changing a string column to an integer is refused because existing values may not convert.'),
    ('Does RENAME break queries and views?', 'Yes, anything that refers to the old name fails or, worse, reads a new table that later takes the old name. Search for the old name in jobs and views before renaming, and consider leaving a view with the old name during a transition.'),
    ('What separator does INSERT OVERWRITE DIRECTORY use by default?', 'Hive’s default field delimiter, Ctrl-A (\\001), which looks invisible in many editors. Always add ROW FORMAT DELIMITED FIELDS TERMINATED BY \',\' (or a suitable format such as STORED AS ORC) when other people or tools will read the files. No header line is written.'),
    ('Is EXPORT/IMPORT a good backup method?', 'It is convenient for single tables and for moving tables between clusters, because data and definition travel together. For whole warehouses teams rely on storage snapshots, replication (Hive’s REPL commands, DistCp) and backups of the metastore database, which scale better.'),
]

PRACTICE_INTRO = 'Programs on schema changes, positional reading, safe rewrites and exports.'
PROBLEMS = [
    dict(level='easy', title='Values after ADD COLUMNS', stmt='The line "4,Upma,45" is read with columns item_id, name, price, category. Print the row.', inp='4,Upma,45',
         code='''cols = ["item_id", "name", "price", "category"]
vals = "4,Upma,45".split(",")
print({c: vals[i] if i < len(vals) else None for i, c in enumerate(cols)})
''', explain='category is None (NULL): the line has only three values.'),
    dict(level='easy', title='Rename keeps values', stmt='Read "1,Poha,40" with columns item_id, name, price_rs.', inp='1,Poha,40',
         code='''print(dict(zip(["item_id", "name", "price_rs"], "1,Poha,40".split(","))))
''', explain='Same value 40, new name price_rs. Renames are safe for positional formats.'),
    dict(level='easy', title='Export lines', stmt='Turn [("Pune", 7931), ("Thane", 4820)] into comma-separated lines with a header city,orders.', inp='two tuples',
         code='''rows = [("Pune", 7931), ("Thane", 4820)]
print("city,orders")
for c, n in rows:
    print(f"{c},{n}")
''', explain='Hive’s DIRECTORY export writes no header; add one when people open the file in a spreadsheet.'),
    dict(level='medium', title='Detect shifted columns', stmt='After a REPLACE COLUMNS, check whether the category column looks numeric for most rows (a sign of shifted data).', inp='["40", "80", "15", "Beverage"]',
         code='''cat = ["40", "80", "15", "Beverage"]
numeric = sum(v.isdigit() for v in cat)
print(f"{numeric}/{len(cat)} numeric -> {'likely shifted!' if numeric > len(cat) / 2 else 'looks fine'}")
''', explain='Simple profiling after schema changes catches shifts that Hive does not warn about.'),
    dict(level='medium', title='Widening checker', stmt='Given (old, new) decimal precisions and scales, decide whether every old value fits: new.p − new.s ≥ old.p − old.s and new.s ≥ old.s.', inp='(8,2)→(10,2) · (8,2)→(8,3) · (10,2)→(9,2)',
         code='''pairs = [((8, 2), (10, 2)), ((8, 2), (8, 3)), ((10, 2), (9, 2))]
for (p1, s1), (p2, s2) in pairs:
    ok = p2 - s2 >= p1 - s1 and s2 >= s1
    print(f"DECIMAL({p1},{s1}) -> DECIMAL({p2},{s2}): {'safe' if ok else 'may lose values'}")
''', explain='Only the first is safe. (8,3) has one fewer whole digit; (9,2) has one fewer whole digit too.'),
    dict(level='medium', title='Which folders survive a monthly OVERWRITE?', stmt='Simulate five monthly exports to the same folder with OVERWRITE and to dated folders. Count surviving files.', inp='5 months',
         code='''same, dated = {}, {}
for m in ["06", "07", "08", "09", "10"]:
    same["/exports/finance"] = [f"2026-{m}.csv"]
    dated[f"/exports/finance/2026-{m}"] = [f"2026-{m}.csv"]
print("same folder :", sum(len(v) for v in same.values()), "file")
print("dated folder:", sum(len(v) for v in dated.values()), "files")
''', explain='1 versus 5. OVERWRITE is a delete-then-write on the whole folder.'),
    dict(level='business', title='Rewrite cost for a column removal', stmt='Removing a column requires rewriting a 900 GB table. The cluster rewrites at 1.5 GB per second. How long does it take, and should it run in business hours?', inp='900 GB at 1.5 GB/s',
         code='''gb, rate = 900, 1.5
minutes = gb / rate / 60
print(f"about {minutes:.0f} minutes")
''', explain='About 10 minutes of full cluster throughput; schedule it in a quiet window and keep the old table until the new one is verified.'),
    dict(level='business', title='Export size check', stmt='Finance wants all 50,002 orders as CSV at about 62 bytes per line. Is Beeline streaming (limit 50 MB) fine, or should you use a DIRECTORY export?', inp='50,002 lines × 62 bytes',
         code='''size_mb = 50_002 * 62 / 1024 / 1024
print(f"{size_mb:.1f} MB ->", "Beeline csv2 is fine" if size_mb < 50 else "use INSERT OVERWRITE DIRECTORY")
''', explain='About 3 MB: Beeline csv2 with a header is simplest. A year of data across many cities would need a DIRECTORY export.'),
]

SCN_INTRO = 'Change and export questions test whether you have maintained real tables, not just created them.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“How do you add or rename a column?”',
        'The interviewer asks how to add a column and rename another on an existing Hive table with years of data.',
        'do you know ALTER is metadata-only?',
        '''<ul>
          <li><code>ALTER TABLE t ADD COLUMNS (c TYPE)</code> adds at the end; old rows return NULL.</li>
          <li><code>ALTER TABLE t CHANGE old new TYPE</code> renames (same position, same values).</li>
          <li>No data is rewritten, so both are instant even on terabytes. Update jobs that use the old column name.</li>
        </ul>''', '“Hive rewrites the table”: it does not.') +
    scn('Data quality · incident', 'Mid-level', 'Values in the wrong column after a schema change',
        'After a release, the category column of a text table shows numbers.',
        'do you understand positional mapping?',
        '''<ol>
          <li>Check the DDL history: a REPLACE COLUMNS or reorder removed or moved a column.</li>
          <li>Text columns map by position, so later columns now read neighbouring values.</li>
          <li>Restore the previous column list from Git (SHOW CREATE TABLE history), then remove the column properly by rewriting into a new table.</li>
        </ol>''', 'trying to fix it with another REPLACE COLUMNS guess.') +
    scn('Compliance', 'Mid-level', 'Delete a personal-data column',
        'Legal asks to remove customers’ phone numbers from the warehouse within 30 days.',
        'do you know metadata changes do not delete data?',
        '''<ul>
          <li>Rewrite each affected table without the column (CTAS/INSERT … SELECT), verify, swap names, DROP … PURGE the old ones.</li>
          <li>Find copies: exports, backups, derived tables, HDFS trash and snapshots; clean or let them expire per policy.</li>
          <li>Record what was done for the audit, and add the column to a “never copy” list for future tables.</li>
        </ul>''', '“ALTER TABLE … REPLACE COLUMNS removes it”.') +
    scn('Data engineering · delivery', 'Fresher', 'A daily extract for a partner',
        'A partner needs yesterday’s orders as a CSV every morning via SFTP.',
        'can you produce clean, safe exports?',
        '''<ol>
          <li><code>INSERT OVERWRITE DIRECTORY '/exports/partner/${run_date}' ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' SELECT … WHERE order_date = '${run_date}'</code>.</li>
          <li>Merge part files and add a header if needed, then hand over to the transfer job.</li>
          <li>Use a dated folder so retries overwrite only that day, and a retention job to remove old exports.</li>
        </ol>''', 'exporting to one fixed folder with OVERWRITE.')
)
