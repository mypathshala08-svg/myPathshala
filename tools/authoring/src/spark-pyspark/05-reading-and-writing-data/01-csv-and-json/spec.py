import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='05-reading-and-writing-data', lesson='01-csv-and-json', n='5.1',
    module_label='Module 5 · Reading and writing data',
    title='CSV and JSON',
    desc='Reading messy CSV and JSON with PySpark 4.3.0: a real partner file where default options produced 8 rows from 7 orders, header, schema, multiLine and escape for quoted line breaks and doubled quotes, _corrupt_record in PERMISSIVE mode, DROPMALFORMED giving 6 rows for count() but 4 for all columns, FAILFAST, dateFormat, JSON Lines versus JSON arrays, nested structs and explode, a gzip CSV read by one task (3.4 s vs 2.0 s), and JSON inference.',
    og_desc='Default options turned 7 partner orders into 8 rows, and DROPMALFORMED counted 6 or 4 depending on the columns read. CSV and JSON in Spark, measured.',
    minutes=34, level='Beginner → Intermediate',
    lead='Module 5 is about getting data in and out. Text formats come first because they are everywhere and messy. This lesson reads a real partner CSV with every common problem, handles corrupt records properly, and reads nested JSON. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', 'Real messy partner file', 'Corrupt records kept', 'Runs in your browser (Python)'],
)

MAIN = '''# Why one CSV line with a line break becomes two rows (simplified parser)
text = 'order_id,review\\n9004,"Loved it.\\nWill order again"\\n9005,Cold\\n'

def split_naive(t):                      # multiLine=false: a newline ends a record
    return [l for l in t.split("\\n")[1:] if l]

def split_quoted(t):                     # multiLine=true: newlines inside quotes are data
    rows, cur, inq = [], "", False
    for ch in t.split("\\n", 1)[1]:
        if ch == '"':
            inq = not inq
        if ch == "\\n" and not inq:
            rows.append(cur); cur = ""
        else:
            cur += ch
    return rows

print("naive :", split_naive(text))
print("quoted:", split_quoted(text))
'''
RUN = dict(
    heading='Run the code: why line breaks matter',
    intro='<p>A tiny parser shows what <code>multiLine</code> changes. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('def split_naive(t):                      # multiLine=false: a newline ends a record', 'Spark’s default: 7 orders became 8 rows in the lab.'),
        ('        if ch == "\\n" and not inq:', 'Inside quotes a newline is part of the value.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Count the rows in each output.', code=None),
        dict(label='2 · Predict first: DROPMALFORMED', hint='<b>Predict first:</b> rows kept when only order_id is parsed vs all columns (lab).',
             code='''print("count() -> 6 rows (bad amount and date not parsed)")
print("all columns -> 4 rows")
'''),
        dict(label='3 · Doubled quotes', hint='Excel writes a quote inside a value as two quotes.',
             code='''raw = '"He said ""wow"""'
print(raw[1:-1].replace('""', '"'))
'''),
        dict(label='4 · Two date formats', hint='Try one format, then the other, like coalesce(try_to_date…).',
             code='''from datetime import datetime
def parse(s):
    for f in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, f).date()
        except ValueError:
            pass
print([str(parse(s)) for s in ("2026-11-01", "02/11/2026")])
'''),
        dict(label='5 · Spot the error', hint='This reader drops bad rows silently.', expect='error',
             code='''opts = {"mode": "DROPMALFORMED"}
assert opts["mode"] != "DROPMALFORMED", "rows vanish without a trace: use PERMISSIVE with _corrupt_record and quarantine"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: CSV and JSON',
    intro='<p>In the <code>pyspark</code> shell with the lab files. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Defaults vs options', cmd='spark.read.csv(p, header=True, schema=schema).count(), \\\nspark.read.csv(p, header=True, schema=schema, multiLine=True, escape=\'"\').count()', file='pyspark',
             output='(8, 7)', note='7 orders in the file.'),
        dict(title='2 · A JSON array', cmd='spark.read.json("app_events_array.json").columns', file='pyspark',
             output="['_corrupt_record']", note='Add multiLine=True.'),
        dict(title='3 · gzip partitions', cmd='spark.read.csv("big5m_gz", header=True).rdd.getNumPartitions()', file='pyspark',
             output='1', note='The plain CSV had 7.'),
    ],
)

TRACE = dict(
    heading='PERMISSIVE: keep good fields, save the raw line',
    intro='<p>Follow how one bad line is stored.</p>',
    code='''line = "9003,Delhi,abc,2026-11-02,Late"
f = line.split(",")
amount = int(f[2]) if f[2].isdigit() else None
corrupt = line if amount is None else None
print({"order_id": int(f[0]), "amount": amount, "_corrupt_record": corrupt})
''',
    notes={3: 'Null :: The field that fails becomes null.', 4: 'Evidence :: The whole raw line goes to _corrupt_record.'},
)

WORKED_INTRO = 'Three reading tasks from TiffinGo’s ingestion jobs.'
EXAMPLES = [
    dict(level='b', tag='CSV · basics', title='Read the partner file correctly',
         problem='<p>Read partner_orders.csv with the right options.</p>',
         inp='quoted commas, line breaks, doubled quotes',
         approach=['header and schema.', 'multiLine and escape=\'"\'.', 'Check the row count.'],
         code='''print("""p = (spark.read.option("header", True).option("multiLine", True)
     .option("escape", '"').schema(schema).csv(path))
assert p.count() == 7""")
''', notes={2: 'Options :: multiLine for line breaks, escape for doubled quotes.'},
         tryit='Step 3: 7 correct rows.'),
    dict(level='i', tag='CSV · quality', title='Quarantine bad rows',
         problem='<p>Load good rows and keep bad ones for the partner.</p>',
         inp='schema + _corrupt_record',
         approach=['Read PERMISSIVE with the corrupt column.', 'Cache.', 'Split and write both.'],
         code='''print("""df = spark.read.schema(schema + ", _corrupt_record STRING").options(**opts).csv(path).cache()
df.where("_corrupt_record IS NULL").drop("_corrupt_record").write.mode("append").saveAsTable("orders_raw")
df.where("_corrupt_record IS NOT NULL").select("_corrupt_record").write.mode("append").saveAsTable("orders_bad")""")
''', notes={1: 'Cache :: Spark refuses queries that use only the corrupt column of a raw file.'},
         tryit='Step 4 shows why to decide on the full schema.'),
    dict(level='a', tag='JSON · nested', title='One row per ordered dish',
         problem='<p>Turn app events into (order_id, dish, qty) rows.</p>',
         inp='items: array<struct<dish, qty>>',
         approach=['Give a schema (order_id as STRING or cast).', 'explode_outer(items).', 'Select struct fields.'],
         code='''events = [(9101, [("Thali", 2)]), (9102, [("Dosa", 1), ("Idli", 2)]), (9103, [])]
rows = [(o, d, q) for o, items in events for d, q in (items or [(None, None)])]
print(rows)
''', notes={2: 'explode_outer :: 9103 keeps a row with nulls instead of disappearing.'},
         tryit='Lesson 6.5 covers complex types in depth.'),
]

QUIZ = mix([
    dict(q='Beginner: What does header=True do?', options=['Writes a header', 'Uses the first line as column names', 'Infers types', 'Skips bad rows'], answer=1,
         why='Without it the header is a data row.'),
    dict(q='Beginner: Which option lets a quoted value contain line breaks?', options=['escape', 'multiLine', 'sep', 'nullValue'], answer=1,
         why='Otherwise one record becomes two rows.'),
    dict(q='Beginner: Default mode for CSV and JSON?', options=['FAILFAST', 'DROPMALFORMED', 'PERMISSIVE', 'STRICT'], answer=2,
         why='Bad fields become null.'),
    dict(q='Intermediate: Where does PERMISSIVE store the raw bad line?', options=['Logs', '_corrupt_record (if in the schema)', 'A side file', 'Nowhere'], answer=1,
         why='Add it as a string column.'),
    dict(q='Intermediate: How does spark.read.json read a JSON array file by default?', options=['Correctly', 'As _corrupt_record rows', 'As one string', 'Error'], answer=1,
         why='JSON Lines is the default; use multiLine.'),
    dict(q='Intermediate: Why did DROPMALFORMED keep 6 rows for count() but 4 for all columns?', options=['Random', 'Only needed columns are parsed', 'Caching', 'AQE'], answer=1,
         why='Column pruning in the CSV parser.'),
    dict(q='Advanced: Why was the gzip CSV read by one task?', options=['Too small', 'gzip is not splittable', 'Bug', 'Header'], answer=1,
         why='1 partition vs 7.'),
    dict(q='Advanced: Best handling of bad rows in a finance feed?', options=['DROPMALFORMED', 'PERMISSIVE + _corrupt_record + quarantine', 'Ignore', 'inferSchema'], answer=1,
         why='Nothing vanishes; partners can fix data.'),
])

REVISION = [
    'CSV options: <code>header</code>, schema, <code>multiLine</code>, <code>escape=\'"\'</code>, <code>nullValue</code>, <code>dateFormat</code>.',
    'Defaults turned 7 orders into <b>8 rows</b>; correct options gave 7.',
    'Modes: PERMISSIVE (+ <code>_corrupt_record</code>), DROPMALFORMED (silent), FAILFAST (stop).',
    'CSV parses only needed columns: DROPMALFORMED kept 6 vs 4 rows; decide bad rows on the full schema and cache.',
    'One <code>dateFormat</code> per read; mixed formats: string + <code>coalesce(try_to_date…)</code>.',
    'JSON = JSON Lines by default; arrays need <code>multiLine</code>; nested → struct/array; <code>explode</code>.',
    'gzip is not splittable: 1 partition (3.4 s vs 2.0 s). JSON inference reads everything.',
]
FAQ = [
    ('Is bzip2 splittable?', 'Yes, bzip2 can be split, but it is slow to compress. In practice prefer many moderate files or convert to Parquet.'),
    ('How do I read a pipe-separated file?', 'Use <code>sep="|"</code> (or <code>delimiter</code>). Spark also accepts multi-character separators.'),
    ('What does enforceSchema=false do?', 'With a header, Spark checks that header names match your schema and warns or fails on mismatch, instead of silently applying the schema by position.'),
    ('Can I read many files at once?', 'Yes: pass a folder, a glob (<code>orders_2026-11-*.csv</code>) or a list of paths. Use <code>recursiveFileLookup</code> for nested folders and <code>input_file_name()</code> or <code>_metadata.file_path</code> to know the source file.'),
    ('Should I keep data in CSV?', 'Only at the edges. Read text once and store Parquet, ORC or a table format for analysis (Lesson 5.2).'),
]

PRACTICE_INTRO = 'Programs about parsing text data safely.'
PROBLEMS = [
    dict(level='easy', title='Extra rows', stmt='Extra rows created by line breaks.', inp='8 read, 7 sent',
         code='''print(8 - 7)
''', explain='One review contained a line break.'),
    dict(level='easy', title='Bad share', stmt='Share of bad rows in the partner file.', inp='3 of 7',
         code='''print(f"{3 / 7:.0%}")
''', explain='Report this to the partner.'),
    dict(level='easy', title='Split a quoted CSV line', stmt='Parse a line with a quoted comma.', inp='9002,"Navi Mumbai, MH",380',
         code='''import csv
print(next(csv.reader(['9002,"Navi Mumbai, MH",380'])))
''', explain='Quotes protect the comma.'),
    dict(level='medium', title='Control total', stmt='Check rows read + quarantined = rows sent.', inp='4 good, 3 bad, 7 sent',
         code='''good, bad, sent = 4, 3, 7
print("OK" if good + bad == sent else "MISMATCH")
''', explain='Run on every load.'),
    dict(level='medium', title='Explode', stmt='Flatten orders to dish rows.', inp='nested items',
         code='''orders = {9101: ["Thali"], 9102: ["Dosa", "Idli"]}
print([(o, d) for o, ds in orders.items() for d in ds])
''', explain='F.explode in Spark.'),
    dict(level='medium', title='JSON Lines', stmt='Convert a JSON array to JSON Lines.', inp='[{...}, {...}]',
         code='''import json
arr = [{"order_id": 1}, {"order_id": 2}]
print("\\n".join(json.dumps(o) for o in arr))
''', explain='The format Spark reads by default.'),
    dict(level='business', title='Idle cores', stmt='Idle cores while one gzip file is read.', inp='100-core cluster',
         code='''print(100 - 1)
''', explain='Ask for split files.'),
    dict(level='business', title='Disputed amount', stmt='Value of orders with unreadable amounts.', inp='3 bad of 7, average ₹420',
         code='''print("₹", 3 * 420, "needs manual review")
''', explain='Quarantine keeps them visible.'),
]

SCN_INTRO = 'Interviewers love messy-CSV questions because every data engineer has met one.'
SCENARIOS = (
    scn('Any company · PySpark', 'Fresher', '“How do you read a CSV in PySpark?”',
        'Read a CSV with a header into a DataFrame.',
        'do you know the essential options?',
        '<p><code>spark.read.option("header", True).schema(schema).csv(path)</code>. I give an explicit schema instead of inferSchema, and set multiLine/escape/nullValue/dateFormat when the file needs them. I also decide the mode for bad rows.</p>', 'Only <code>spark.read.csv(path)</code>.') +
    scn('Data engineering', 'Mid-level', 'Corrupt records',
        'Some rows in a feed are malformed. How do you handle them?',
        'do you know modes and quarantine?',
        '''<ul>
          <li>PERMISSIVE with a <code>_corrupt_record</code> string column; cache; split good and bad.</li>
          <li>Write bad rows to a quarantine table, alert, reconcile counts.</li>
          <li>FAILFAST where any bad row must stop; avoid DROPMALFORMED.</li>
        </ul>''', 'Silently dropping rows.') +
    scn('Data engineering', 'Mid-level', 'Row counts differ from the source',
        'Spark reports more rows than the source system sent.',
        'can you debug parsing?',
        '''<ol>
          <li>Look for line breaks inside quoted values: enable multiLine.</li>
          <li>Check escape (doubled quotes) and separators inside values.</li>
          <li>Compare counts with a control file every load.</li>
        </ol>''', 'Deduplicating to hide the difference.') +
    scn('Platform', 'Senior', 'A 40 GB gzip file',
        'One huge gzip file makes the job slow on a large cluster.',
        'do you know splittability?',
        '''<ul>
          <li>gzip is read by one task: ask the producer for many files or a splittable format.</li>
          <li>Otherwise convert once: read, repartition, write Parquet.</li>
          <li>Measure partitions and task counts in the Spark UI.</li>
        </ul>''', 'Adding executors.')
)
