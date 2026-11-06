import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from hivekit import tables
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
BODY = body(HERE)

META = dict(
    module='06-file-formats', lesson='01-text-sequence-and-avro', n='6.1',
    module_label='Module 6 · File formats and compression',
    title='Text, SequenceFile and Avro tables',
    desc='Hive file formats explained with real Hive 4.2.1 results: the same 50,000 rows written as TEXTFILE, SEQUENCEFILE, RCFILE, AVRO, ORC and PARQUET with real file sizes and magic bytes, row vs columnar layout, compressed text (gzip, bzip2, Snappy) and splittability, SequenceFile block compression, Avro’s embedded schema and schema evolution by name with defaults, the silent column shift in text tables, and why ALTER TABLE SET FILEFORMAT does not convert data.',
    og_desc='A partner added one column and the report showed a city called “Gold”. Hive file formats compared on real data, and how Avro survives schema changes.',
    minutes=35, level='Beginner → Advanced',
    lead='Every Hive table stores its rows in some file format, and the choice decides size, speed and what happens when the data changes. Kabir writes the same 50,000 orders in <b>all six formats</b>, compares their sizes (from 4.3 MB down to 0.44 MB), then solves a real bug: a partner added a column and a text table silently shifted values, while an Avro table read everything correctly. <b>All outputs are real</b>, from Hive 4.2.1.',
    chips=['Real Hive 4.2.1 outputs', 'Six formats, real sizes', 'Avro schema evolution', 'Runs in your browser (Python)'],
)

MAIN = '''# Why a text table breaks when a column is inserted: it reads by POSITION
table_columns = ["customer_id", "name", "city"]
lines = ["1,Aarav Desai,Bengaluru",          # v1 file
         "4,Diya Patil,Gold,Pune"]           # v2 file: plan added before city

for line in lines:
    values = line.split(",")
    row = {col: values[i] for i, col in enumerate(table_columns)}   # by position
    print(row)

# Avro-style: each record carries field NAMES, missing fields get the default
records = [{"customer_id": 1, "name": "Aarav Desai", "city": "Bengaluru"},
           {"customer_id": 4, "name": "Diya Patil", "plan": "Gold", "city": "Pune"}]
for r in records:
    print({c: r.get(c, "Basic" if c == "plan" else None) for c in ["customer_id", "name", "plan", "city"]})
'''
RUN = dict(
    heading='Run the code: position vs name',
    intro='<p>These programs show how formats store and find values: by position in text, by name in Avro, and how compression changes size. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    row = {col: values[i] for i, col in enumerate(table_columns)}   # by position', 'Exactly what a delimited text SerDe does: the third value is “city”, whatever it really is.'),
        ('    print({c: r.get(c, "Basic" if c == "plan" else None) for c in ["customer_id", "name", "plan", "city"]})', 'Like Avro schema resolution: match by name, use the default for a missing field.'),
    ],
    tasks=[
        dict(label='1 · Position vs name', hint='Press <b>Run</b>. The first loop reproduces the real text-table bug (city = Gold); the second matches the real Avro output.', code=None),
        dict(label='2 · Predict first: compressing text', hint='<b>Predict first:</b> how much smaller will gzip and bzip2 make 2,000 repeated order lines? (Real Hive: gzip 5.2×, bzip2 8× on 50,000 orders.)',
             code='''import gzip, bz2
rows = "".join(f"{100000 + i},{i % 2000},Mumbai,2026-10-05,{(i * 37) % 800 + 40}.00,UPI,DELIVERED\\n" for i in range(2000))
data = rows.encode()
print("text ", len(data))
print("gzip ", len(gzip.compress(data)), round(len(data) / len(gzip.compress(data)), 1), "x")
print("bzip2", len(bz2.compress(data)), round(len(data) / len(bz2.compress(data)), 1), "x")
'''),
        dict(label='3 · Magic bytes', hint='Each binary format starts with its own signature. Add Parquet’s (b"PAR1") and test it.',
             code='''MAGIC = {b"SEQ": "SEQUENCEFILE", b"RCF": "RCFILE", b"Obj": "AVRO", b"ORC": "ORC"}
def detect(first_bytes):
    for m, name in MAGIC.items():
        if first_bytes.startswith(m):
            return name
    return "probably TEXT"
for head in [b"SEQ\\x06org.apache", b"Obj\\x01\\x04avro", b"ORC\\x0b", b"100001\\x011932"]:
    print(head[:6], "->", detect(head))
'''),
        dict(label='4 · Row layout vs column layout', hint='Columnar layout puts similar values side by side. Compare how well each layout compresses.',
             code='''import zlib
rows = [(100000 + i, ["Mumbai", "Pune", "Thane"][i % 3], ["UPI", "Card"][i % 2]) for i in range(3000)]
row_layout = "".join(f"{a},{b},{c};" for a, b, c in rows).encode()
col_layout = (",".join(str(r[0]) for r in rows) + "|" + ",".join(r[1] for r in rows) + "|" + ",".join(r[2] for r in rows)).encode()
print("row   ", len(zlib.compress(row_layout)))
print("column", len(zlib.compress(col_layout)))
'''),
        dict(label='5 · Spot the error', hint='A new field was added to the schema without a default, so old records cannot be read. Give “plan” a default value.', expect='error',
             code='''schema = [("customer_id", None), ("name", None), ("plan", None), ("city", None)]   # (field, default)
old_record = {"customer_id": 1, "name": "Aarav Desai", "city": "Bengaluru"}
row = {}
for field, default in schema:
    if field not in old_record:
        assert default is not None, f"field '{field}' is missing in old data and has no default"
        row[field] = default
    else:
        row[field] = old_record[field]
print(row)
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: what STORED AS really means',
    intro='<p>Three more statements to try in Beeline on the TiffinGo data. <b>Outputs are real</b>, from Hive 4.2.1.</p>',
    items=[
        dict(title='1 · STORED AS expands into three classes', cmd='DESCRIBE FORMATTED f_text;     -- and f_seq, f_avro\n-- selected lines', file='Beeline',
             output='f_text\n' + capf('l61_fmt_f_text.txt') + '\n\nf_seq\n' + capf('l61_fmt_f_seq.txt') + '\n\nf_avro\n' + capf('l61_fmt_f_avro.txt'),
             note='STORED AS is a shortcut for an InputFormat (how files are split and read), an OutputFormat (how they are written) and a SerDe (how bytes become columns). Text and SequenceFile share the same LazySimpleSerDe; only the container differs.'),
        dict(title='2 · Avro with compression', cmd='SET hive.exec.compress.output=true;\nSET mapreduce.output.fileoutputformat.compress.codec=org.apache.hadoop.io.compress.DefaultCodec;\nCREATE TABLE f_avro_deflate STORED AS AVRO AS SELECT * FROM orders;\n$ ls -l …/f_avro_deflate', file='Beeline',
             output='f_avro          2,510,687 bytes  (codec: null)\nf_avro_deflate    772,457 bytes  (codec: deflate, read back from the file header)',
             note='Avro compresses blocks of records inside the file, so it stays splittable. Deflate cut the file to less than a third. Avro also supports Snappy and other codecs.'),
        dict(title='3 · Compressed text is read transparently', cmd='SELECT COUNT(*), SUM(amount) FROM f_text_gz;', file='Beeline',
             output=capf('l61_gz.txt'),
             note='Hive picked the gzip codec from the <code>.gz</code> extension. The totals match the original orders table: 50,000 rows and ₹1,47,21,180.'),
    ],
)

TRACE = dict(
    heading='Avro schema resolution, one field at a time',
    intro='<p>For each field of the reader (table) schema, Avro looks for a field with the same name in the writer (file) schema. Watch <code>row</code> fill up.</p>',
    code='''reader = [("customer_id", None), ("name", None), ("plan", "Basic"), ("city", None)]
writer_record = {"customer_id": 1, "name": "Aarav Desai", "city": "Bengaluru"}
row = {}
for name, default in reader:
    if name in writer_record:
        row[name] = writer_record[name]
    else:
        row[name] = default
print(row)
''',
    notes={5: 'By name :: The match is by field name, so the order of fields in the file does not matter.', 8: 'Default :: The v1 file has no plan field, so the reader default is used, exactly like the real “Basic”.'},
)

WORKED_INTRO = 'Three format decisions from TiffinGo’s data team.'
EXAMPLES = [
    dict(level='b', tag='Storage · conversion', title='How much will converting to ORC save?',
         problem='<p>The raw zone holds 90 days of order text files at the lab’s ratio. Estimate the storage for text, Avro and ORC using the real sizes of 50,000 orders.</p>',
         inp='50,000 orders: text 3,735,865 B · Avro 2,510,687 B · ORC 437,536 B; 1,621 orders per day',
         approach=['Bytes per order for each format.', 'Multiply by orders per day and days.', 'Compare.'],
         code='''sizes = {"TEXT": 3735865, "AVRO": 2510687, "ORC": 437536}
orders_per_day, days = 1621, 90
for fmt, b in sizes.items():
    per_order = b / 50000
    print(fmt, round(per_order, 1), "B/order", round(per_order * orders_per_day * days / 1e6, 1), "MB for 90 days")
''', notes={4: 'Ratio :: Real ratios from Step 2; real data compresses differently, so measure your own.'},
         tryit='Scale orders_per_day to 50,00,000 to see why large companies care: text needs about 34 GB for 90 days where ORC needs about 4 GB. Event tables with billions of rows a day turn the same ratio into terabytes.'),
    dict(level='i', tag='Data quality · schema drift', title='Detect a shifted column in a text table',
         problem='<p>After a partner change, check the city column of a text table against the list of valid cities and report suspicious values, before they reach reports.</p>',
         inp='city values from cust_txt (real): Bengaluru, Mumbai, Mumbai, Gold, Basic',
         approach=['Keep a reference list of valid cities.', 'Find values not in it.', 'Alert if any appear.'],
         code='''valid = {"Mumbai", "Pune", "Thane", "Navi Mumbai", "Bengaluru", "Hyderabad", "Delhi", "Chennai"}
cities = ["Bengaluru", "Mumbai", "Mumbai", "Gold", "Basic"]
bad = sorted({c for c in cities if c not in valid})
print("suspicious:", bad, "-> ALERT" if bad else "OK")
''', notes={3: 'Check :: In HiveQL: SELECT city, COUNT(*) FROM cust_txt WHERE city NOT IN (…) GROUP BY city.'},
         tryit='A second useful check: count fields per line. Lines with 4 fields in a 3-column file mean the layout changed.'),
    dict(level='a', tag='Architecture · evolution', title='Is this Avro schema change safe?',
         problem='<p>Before deploying a new schema, check it against the current one: every new field must have a default, and no field may change type.</p>',
         inp='old {id:int, name:string, city:string} · new {id:int, name:string, plan:string default Basic, city:string, pincode:int (no default)}',
         approach=['Find fields added in the new schema.', 'Check each has a default.', 'Check shared fields keep their type.'],
         code='''old = {"id": "int", "name": "string", "city": "string"}
new = {"id": ("int", None), "name": ("string", None), "plan": ("string", "Basic"),
       "city": ("string", None), "pincode": ("int", None)}
problems = []
for f, (typ, default) in new.items():
    if f not in old and default is None:
        problems.append(f"{f}: new field without default")
    elif f in old and old[f] != typ:
        problems.append(f"{f}: type changed")
print(problems or "compatible")
''', notes={6: 'Rule :: Old files lack the field; without a default, readers cannot fill it.'},
         tryit='Give pincode a default (or make it a union with null and default null) and the change becomes backward compatible, like Hive’s own generated schemas.'),
]

QUIZ = mix([
    dict(q='Beginner: Which format does Hive 4.2.1 use for CREATE TABLE without STORED AS?', options=['ORC', 'Parquet', 'TEXTFILE', 'Avro'], answer=2,
         why='hive.default.fileformat=TextFile in our lab. Some vendor builds change it.'),
    dict(q='Beginner: Which of these is a columnar format?', options=['SEQUENCEFILE', 'AVRO', 'ORC', 'TEXTFILE'], answer=2,
         why='RCFile, ORC and Parquet are columnar; Text, SequenceFile and Avro are row formats.'),
    dict(q='Beginner: What does an Avro file contain besides the data?', options=['Nothing else', 'Its schema in JSON', 'An index of every row', 'The table name only'], answer=1,
         why='The file header starts with “Obj” and the writer schema.'),
    dict(q='Intermediate: A partner inserts a new column in the middle of a CSV read by a text table. What happens?', options=['Hive raises an error', 'Values shift into the wrong columns silently', 'Hive adds the column', 'The new column is ignored correctly'], answer=1,
         why='Text tables read by position. Real lab: city = “Gold”.'),
    dict(q='Intermediate: Why is a large .gz text file slow to process?', options=['gzip is lossy', 'gzip files are not splittable, so one task reads it all', 'Hive cannot read gzip', 'It must be unzipped by hand'], answer=1,
         why='bzip2 and container formats are splittable.'),
    dict(q='Intermediate: Which format was the LARGEST for our 50,000 orders?', options=['TEXTFILE', 'SEQUENCEFILE', 'AVRO', 'RCFILE'], answer=1,
         why='4.34 MB: each row is wrapped in a key/value record, and nothing was compressed by default.'),
    dict(q='Advanced: What does ALTER TABLE t SET FILEFORMAT ORC do to existing text files?', options=['Converts them', 'Nothing: they stay text and can no longer be read as ORC', 'Deletes them', 'Compresses them'], answer=1,
         why='Real error: Malformed ORC file … Invalid postscript. Rewrite with INSERT OVERWRITE or CTAS.'),
    dict(q='Advanced: An Avro schema adds field plan with default “Basic”. What do old files return for plan?', options=['NULL', 'An error', '“Basic”', 'An empty string'], answer=2,
         why='Reader/writer schema resolution fills the default for missing fields.'),
])

REVISION = [
    '<b>STORED AS</b> TEXTFILE · SEQUENCEFILE · RCFILE · AVRO · ORC · PARQUET (· JSONFILE). Default in 4.2.1: <b>TEXTFILE</b>, delimiter <code>\\001</code>.',
    '<b>Row:</b> Text, SequenceFile, Avro · <b>Column:</b> RCFile, ORC, Parquet.',
    '<b>Real sizes</b> (50,000 orders): Seq 4.34 MB · Text 3.74 · Avro 2.51 · RC 2.02 · Parquet 1.09 · ORC 0.44.',
    'Output not compressed by default (<code>hive.exec.compress.output=false</code>); ORC uses ZLIB by default.',
    '<b>Splittable:</b> text yes, .gz/.snappy text no, bzip2 yes (slow); SequenceFile, Avro, ORC, Parquet yes (block compression + sync markers).',
    '<b>Magic bytes:</b> SEQ · RCF · Obj · ORC · PAR1.',
    '<b>Avro:</b> schema in the file; table schema via <code>avro.schema.literal</code> / <code>avro.schema.url</code>; fields matched by <b>name</b>; new fields need a <b>default</b>.',
    '<b>Text:</b> no schema → matched by <b>position</b> → silent shifts when columns change.',
    '<code>SET FILEFORMAT</code> changes metadata only → rewrite data with CTAS / INSERT OVERWRITE.',
]
FAQ = [
    ('Which format should I use for a new Hive table?', 'For analytics tables, ORC (the most optimised format in Hive, required for Hive ACID tables) or Parquet (when Spark, Trino or Impala also read the table). Use text only for raw landing data, and Avro for data exchanged between systems or streams where the schema changes over time.'),
    ('Is RCFile still used?', 'Rarely for new work. RCFile was the first columnar format in Hive; ORC was designed as its successor with better compression, statistics and indexes. You will still find RCFile tables in older warehouses, and converting them to ORC with CTAS usually reduces storage.'),
    ('Can Hive read JSON files?', 'Yes: <code>STORED AS JSONFILE</code> or the JsonSerDe (Lessons 2.4 and 4.3). JSON is self-describing like Avro but text-based, larger and slower to parse, and every record repeats the field names.'),
    ('Does Avro schema evolution work for Parquet and ORC too?', 'Partly. ORC and Parquet tables in Hive support adding columns at the end with ALTER TABLE … ADD COLUMNS, and old files return NULL for the new column. Renames and reordering are handled differently by each format and engine, so test them. Iceberg tables (Module 7) track columns by id and handle evolution most safely.'),
    ('Why did SequenceFile come out larger than text?', 'Hive writes each row as a record with a length header and an empty key, plus sync markers, and in our lab nothing was compressed. With BLOCK compression it dropped to 1.38 MB. SequenceFile’s advantage was never size; it was a simple, splittable binary container for MapReduce.'),
]

PRACTICE_INTRO = 'Programs about formats, compression and schemas, with the HiveQL in each explanation.'
PROBLEMS = [
    dict(level='easy', title='Size ratio', stmt='How many times smaller is ORC than text for our orders?', inp='3,735,865 and 437,536 bytes',
         code='''print(round(3735865 / 437536, 1))
''', explain='8.5 times, from the real Step 2 sizes.'),
    dict(level='easy', title='Split a Ctrl-A line', stmt='Split a default Hive text line into fields.', inp='"100001\\x011932\\x0135\\x01Mumbai"',
         code='''line = "100001\\x011932\\x0135\\x01Mumbai"
print(line.split("\\x01"))
''', explain='Hive’s default field delimiter is \\001 (Ctrl-A), which is why the raw file looks like one long word in many editors.'),
    dict(level='easy', title='Row or column?', stmt='Classify the six formats.', inp='six format names',
         code='''for f in ["TEXTFILE", "SEQUENCEFILE", "RCFILE", "AVRO", "ORC", "PARQUET"]:
    print(f, "column" if f in ("RCFILE", "ORC", "PARQUET") else "row")
''', explain='Three row formats and three columnar formats.'),
    dict(level='medium', title='Fields per line check', stmt='Detect lines whose field count differs from the table’s.', inp='lines from cust_txt',
         code='''expected = 3
lines = ["1,Aarav Desai,Bengaluru", "4,Diya Patil,Gold,Pune", "5,Ishaan Khan,Basic,Thane"]
print([l for l in lines if len(l.split(",")) != expected])
''', explain='Two lines have 4 fields: the partner changed the layout. A pre-load check like this catches it before Hive shifts the values.'),
    dict(level='medium', title='Default for a missing field', stmt='Read old records with a new schema that adds plan (default Basic).', inp='two records, one without plan',
         code='''recs = [{"id": 1, "city": "Bengaluru"}, {"id": 4, "plan": "Gold", "city": "Pune"}]
for r in recs:
    print(r["id"], r.get("plan", "Basic"), r["city"])
''', explain='The same result as the real cust_avro query.'),
    dict(level='medium', title='Is the codec splittable?', stmt='For text files, mark which codecs allow parallel reading of one file.', inp='none, gzip, bzip2, snappy',
         code='''splittable = {"none": True, "gzip": False, "bzip2": True, "snappy": False}
for c, s in splittable.items():
    print(c, "splittable" if s else "one task per file")
''', explain='For text files. Inside SequenceFile, Avro, ORC and Parquet, all codecs stay splittable because compression is per block.'),
    dict(level='business', title='Migration plan from RCFile', stmt='A warehouse has 40 TB of RCFile tables. Estimate the size after converting to ORC using the lab ratio.', inp='RCFile 2,019,223 B vs ORC 437,536 B for the same rows',
         code='''ratio = 2019223 / 437536
print(round(ratio, 1), "x smaller ->", round(40 / ratio, 1), "TB")
''', explain='About 8.7 TB, using the lab ratio of 4.6×. Real data varies; convert one table first and measure.'),
    dict(level='business', title='Choose a format per use', stmt='Pick a format for each need.', inp='four needs',
         code='''needs = {"partner CSV landing": "TEXTFILE", "Kafka events with changing schema": "AVRO",
         "Hive analytics + ACID updates": "ORC", "shared with Spark and Trino": "PARQUET"}
for n, f in needs.items():
    print(f"{n:35} -> {f}")
''', explain='A common real-world split. ORC and Parquet are both fine for analytics; ORC is required for Hive ACID tables (Module 7).'),
]

SCN_INTRO = 'File format questions test whether you understand storage, compression and schemas, not just syntax.'
SCENARIOS = (
    scn('Any company · Hive', 'Fresher', '“Which file formats does Hive support?”',
        'List them and compare them briefly.',
        'can you group formats and give one reason for each?',
        '<p>TEXTFILE (default, human-readable), SEQUENCEFILE (binary key/value, splittable), RCFILE (early columnar), AVRO (row format with embedded schema and evolution), ORC (columnar, best for Hive, ACID), PARQUET (columnar, best for sharing with Spark/Trino). For analytics use ORC or Parquet; for exchange and streams use Avro.</p>', 'Listing names without any comparison.') +
    scn('Data engineering', 'Mid-level', 'Values in the wrong columns',
        'After a vendor update, the city column of a report shows plan names, with no error from Hive.',
        'do you know text tables read by position?',
        '''<ol>
          <li>Check a raw file: the vendor inserted a column.</li>
          <li>Short term: update the table columns to the new layout for new files (or separate old and new files into different tables or partitions).</li>
          <li>Long term: agree an Avro (or Parquet) contract with the vendor, and add a field-count / valid-values check before loading.</li>
        </ol>''', 'Blaming Hive or re-running the job.') +
    scn('Platform', 'Mid-level', 'One job runs on a single task',
        'A daily 20 GB CSV.gz file takes hours to process; the job has just one map task.',
        'do you understand splittability?',
        '''<ul>
          <li>gzip files cannot be split, so one task reads all 20 GB.</li>
          <li>Ask the producer for several smaller files, or a splittable container (Avro/Parquet), or convert once with a single job and process the ORC copy.</li>
          <li>bzip2 is splittable but slow; prefer container formats.</li>
        </ul>''', '“Increase the number of mappers”, which cannot split a gzip stream.') +
    scn('Architecture', 'Senior', 'Choosing formats for a new lake',
        'Design the formats for a new data lake that receives partner CSVs, Kafka events and serves BI and data science.',
        'can you assign formats by purpose?',
        '''<ul>
          <li>Raw zone: keep files as received (CSV/JSON/Avro), short retention.</li>
          <li>Events: Avro with a schema registry; compatible-change rules.</li>
          <li>Curated: ORC (Hive ACID needs) or Parquet (multi-engine), compressed with Snappy or ZSTD, partitioned by date (Module 5); consider Iceberg for evolution and updates (Module 7).</li>
        </ul>''', 'One format for everything.')
)
