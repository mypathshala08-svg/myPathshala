import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l51_csv_json.txt'
def sec(a, b=None, drop=()):
    s = capsec(C, a, b, drop)
    return '\n'.join(l if len(l) <= 140 else l[:137] + ' …' for l in s.split('\n'))
RAW = open(os.path.join(HERE, '..', '..', 'lab', 'data_m5_partner_orders.csv')).read().rstrip()

def lines(x, y, rows, tones, w=190, h=14):
    o = ''
    for k, (r, tn) in enumerate(zip(rows, tones)):
        o += box(x, y + k * (h + 2), w, h, tn, rx=2) + t(x + 5, y + k * (h + 2) + 10, r, 6.4, 'ink', anchor='start', mono=True)
    return o
L5 = ['9001,Pune,450,2026-11-01,…', '9003,Delhi,abc,…', '9004,…,"Loved it.', 'Will order again"', '9005,…,Cold,EXTRA', '9006,…,02/11/2026,…']

# ---------------------------------------------------------------- story
sc_ = (lines(14, 22, L5, ['card', 'acc', 'violet', 'violet', 'acc', 'acc']) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('default read: 8 rows from 7', 'red'), ('multiLine + escape: 7 rows', 'green'),
           ('DROPMALFORMED count(): 6', 'amber'), ('…all columns: 4 rows', 'red'),
           ('JSON array w/o multiLine: 39 junk', 'red'), ('csv.gz: 1 partition, 3.4 s vs 2.0', 'amber')])))
scene_svg = scene('CSV and JSON are the most common exchange formats and the messiest. We read a partner file with quoted commas, line breaks, bad numbers, an extra column and a different date format, then JSON events and a gzip file.', sc_,
                  'Text formats need <tspan font-weight="700" class="s-acc">options</tspan>, a <tspan font-weight="700" class="s-acc">schema</tspan> and a plan for bad rows.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Seven orders came in, eight went out”</h2>
  <div class="story">
    <p class="narration">A new partner sends TiffinGo a daily CSV. On day one Kabir’s job loaded it with the defaults: the report showed <b>eight</b> orders though the partner sent <b>seven</b>, one review was cut in half, and a Delhi order had no amount. Nobody got an error.</p>

{scene_svg}

K> Sir, Spark read the file. Why is the data wrong?
A> Because a CSV is just text, and Spark only knows what you tell it: is there a header, how are quotes escaped, can a value contain a line break, what does a date look like, and what should happen to a bad line?
R> And JSON? It has types already.
A> JSON has its own traps: one object per line by default, inference that reads everything, and nested data. Today we read the real partner file six ways, keep the bad rows instead of losing them, read JSON lines and a JSON array, flatten nested items, and see why a gzip file is read by one core. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Reading text files at three levels
L1> A handwritten register
      <ul>
        <li>A CSV is a register where commas separate the columns. If someone writes a comma inside a name, you need quotes to know it is one name.</li>
        <li>If a note continues on the next line, you must know it is still the same entry.</li>
        <li>Some entries are unreadable: decide whether to keep them aside, skip them, or stop.</li>
      </ul>
L2> The API
      <ul>
        <li><code>spark.read.csv(path, header=True, schema=…, multiLine=True, escape=\'"\', mode=…, dateFormat=…, nullValue=…)</code>.</li>
        <li>Modes: <code>PERMISSIVE</code> (default, bad fields → null, raw line in <code>_corrupt_record</code> if it is in the schema), <code>DROPMALFORMED</code>, <code>FAILFAST</code>.</li>
        <li><code>spark.read.json(path)</code> expects JSON Lines; use <code>multiLine=True</code> for a JSON array or pretty-printed file.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>Defaults turned 7 orders into 8 rows; <code>multiLine</code> and <code>escape=\'"\'</code> gave 7 correct rows.</li>
        <li><code>DROPMALFORMED</code> kept 6 rows for <code>count()</code> but 4 when all columns were read: CSV parsing depends on the columns you select.</li>
        <li>A gzip CSV was read as one partition: 3.4 s against 2.0 s for the plain file split into 7.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>The CSV and JSON data sources</h2>
''' + def_block(
    'The <b>CSV</b> and <b>JSON</b> sources are built-in, text-based file data sources of Spark SQL, accessed with <code>spark.read.csv()</code> / <code>.json()</code> or <code>format("csv"|"json")</code>. Both are configured by options: for CSV, among others <code>header</code>, <code>sep</code>, <code>quote</code>, <code>escape</code>, <code>multiLine</code>, <code>nullValue</code>, <code>dateFormat</code>, <code>timestampFormat</code>, <code>inferSchema</code>, <code>enforceSchema</code>; for JSON, <code>multiLine</code>, <code>primitivesAsString</code>, <code>dropFieldIfAllNull</code>. Malformed input is handled by the parse <code>mode</code>: <code>PERMISSIVE</code> (default) sets unparsable fields to null and, if a string field named by <code>columnNameOfCorruptRecord</code> exists in the schema, stores the raw record there; <code>DROPMALFORMED</code> drops such records; <code>FAILFAST</code> raises an exception. JSON is read as JSON Lines (one object per line) unless <code>multiLine</code> is set, and its schema is inferred from all records unless one is supplied. Files compressed with a non-splittable codec such as gzip are processed by a single task per file.',
    'CSV and JSON are text, so Spark needs to be told how to read them: header, quotes, line breaks, dates, nulls, and what to do with bad lines. Give a schema, keep bad lines in a corrupt-record column, and remember that one gzip file is read by one core.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('header', 'First line holds column names.'),
    ('quote / escape', 'How a value with commas or quotes is written.'),
    ('multiLine', 'A record may span several lines.'),
    ('mode', 'PERMISSIVE, DROPMALFORMED or FAILFAST.'),
    ('_corrupt_record', 'Column that keeps the raw bad line.'),
    ('JSON Lines', 'One JSON object per line (the default).'),
    ('explode', 'One output row per array element.'),
    ('Splittable', 'A file several tasks can read in parts.'),
]) + '''

  <h3>The three parse modes</h3>
''' + table(['Mode', 'Bad record', 'Lab (7 orders, 3 bad)'], [
    ['<code>PERMISSIVE</code> (default)', 'Kept; bad fields null; raw line in <code>_corrupt_record</code>', '7 rows, 3 flagged'],
    ['<code>DROPMALFORMED</code>', 'Dropped silently', '4 rows (6 for <code>count()</code>!)'],
    ['<code>FAILFAST</code>', 'Job fails with MALFORMED_RECORD_IN_PARSING', 'failed on order 9003'],
], minw=620) + lv + '''
EXAM> “How do you handle corrupt records in CSV?” Read with an explicit schema that includes a string column <code>_corrupt_record</code> in PERMISSIVE mode, cache the result, split good rows from rows where <code>_corrupt_record</code> is not null, and write the bad rows to a quarantine table with a count. Use FAILFAST when any bad row must stop the pipeline; avoid DROPMALFORMED because rows disappear without a trace.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>CSV options you will actually need</h2>
''' + table(['Option', 'Default', 'Set it when'], [
    ['<code>header</code>', 'false', 'The file has a header line (almost always)'],
    ['<code>sep</code>', '<code>,</code>', 'Pipe- or tab-separated files'],
    ['<code>quote</code> / <code>escape</code>', '<code>"</code> / <code>\\</code>', 'Quotes are doubled (<code>""</code>), as Excel writes them: <code>escape=\'"\'</code>'],
    ['<code>multiLine</code>', 'false', 'Quoted values can contain line breaks'],
    ['<code>nullValue</code>', 'empty string', '<code>NA</code>, <code>NULL</code>, <code>-</code> mean missing'],
    ['<code>dateFormat</code> / <code>timestampFormat</code>', 'ISO', 'Dates like <code>02/11/2026</code>'],
    ['<code>mode</code>, <code>columnNameOfCorruptRecord</code>', 'PERMISSIVE', 'Always decide how to treat bad rows'],
    ['<code>enforceSchema</code>', 'true', 'Set false to check header names against your schema'],
    ['<code>encoding</code>', 'UTF-8', 'Files from old systems (e.g. ISO-8859-1)'],
], minw=680) + '''
WARN> <code>_corrupt_record</code> has two traps. Spark refuses queries that reference <b>only</b> that column on a raw file (UNSUPPORTED_FEATURE.<wbr>QUERY_ONLY_<wbr>CORRUPT_<wbr>RECORD_<wbr>COLUMN), so cache or save the parsed data first. And the CSV parser only converts the columns your query needs, so which rows count as “bad” depends on the columns you select (Step 4).
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>A messy partner file, JSON events and a gzip export</h2>
  <p>All outputs are real: PySpark 4.3.0, local mode with 4 cores. This is the partner file, exactly as received:</p>
''' + code('csv', 'partner_orders.csv', RAW) + stepper([
    ('Step 1 · Defaults, then header and schema',
     code('python', 'l51_csv_json.py', 'spark.read.csv(f"{D}/partner_orders.csv").show(3)\nschema = "order_id INT, city STRING, amount INT, order_date DATE, review STRING"\np = spark.read.csv(f"{D}/partner_orders.csv", header=True, schema=schema)\np.show(truncate=28); p.count()', sec('== 1)', '== 3)')),
     'Without options every column is a string named <code>_c0…</code> and the header is a data row. With header and schema it looks better, but count the rows: <b>8</b> from 7 orders. The line break inside 9004’s review started a new “row” of nulls; <code>abc</code> became a null amount; <code>02/11/2026</code> a null date; 9005’s extra column vanished; and 9007’s doubled quotes stayed as raw text. Not one error.'),
    ('Step 2 · Keep the bad lines',
     code('python', 'l51_csv_json.py', 's2 = schema + ", _corrupt_record STRING"\np2 = spark.read.csv(f"{D}/partner_orders.csv", header=True, schema=s2).cache()\np2.select("order_id", "amount", "order_date", "_corrupt_record").show(truncate=40)\np2.where("_corrupt_record IS NOT NULL").count()', sec('== 3)', '== 4)')),
     'Adding a string column called <code>_corrupt_record</code> to the schema makes PERMISSIVE mode keep the <b>raw line</b> of every row it could not parse. Now the problems are visible: four lines, including the broken half of 9004’s review. We cached first: Spark refuses a query that uses only the corrupt-record column of a raw file.'),
    ('Step 3 · multiLine and escape',
     code('python', 'l51_csv_json.py', 'p3 = spark.read.csv(f"{D}/partner_orders.csv", header=True, schema=s2,\n                    multiLine=True, escape=\'"\')\np3.select("order_id", "amount", "order_date", "review", "_corrupt_record").show(truncate=30)\np3.count()', sec('== 4)', '== 5)')),
     '<code>multiLine=True</code> let the quoted review keep its line break, and <code>escape=\'"\'</code> understood Excel-style doubled quotes: <code>He said "wow"</code>. Now there are <b>7 rows</b>, and exactly the three really bad ones are flagged: <code>abc</code>, the extra column and the foreign date format. This is the correct reading of the file.'),
    ('Step 4 · DROPMALFORMED, FAILFAST, and a surprise',
     code('python', 'l51_csv_json.py', 'dm = spark.read.csv(path, schema=schema, mode="DROPMALFORMED", **opts)\ndm.count(); len(dm.collect())\nspark.read.csv(path, schema=schema, mode="FAILFAST", **opts).collect()\nc = spark.read.csv(path, schema=s2, **opts)\nc.select("order_id", "city", "_corrupt_record").collect()   # vs c.collect()', sec('== 5)', '== 6)')),
     'FAILFAST stopped at order 9003. DROPMALFORMED is stranger: <code>count()</code> said <b>6</b>, but collecting all columns gave <b>4</b>. The CSV reader only converts the columns a query needs (column pruning), so a bad <code>amount</code> is not noticed when amount is not read. The same happened with the corrupt-record column: 1 bad row when reading three columns, 3 when reading all. Decide bad rows on the full schema, once, then work from the cached or written result.'),
    ('Step 5 · Dates, JSON Lines and a JSON array',
     code('python', 'l51_csv_json.py', 'spark.read.csv(path, …, dateFormat="dd/MM/yyyy")\nj = spark.read.json(f"{D}/app_events.jsonl"); j.printSchema()\nj.select("order_id", "city", F.size("items").alias("n_items"), "rider.name", "coupon").show()\nspark.read.json(f"{D}/app_events_array.json").columns\nspark.read.json(f"{D}/app_events_array.json", multiLine=True).columns', sec('== 6)', '== 9)')),
     '<code>dateFormat="dd/MM/yyyy"</code> fixed 9006 but broke 9001: one format per read. For mixed formats read the column as a string and use <code>coalesce(try_to_date(c, f1), try_to_date(c, f2))</code>. The JSON Lines file gave nested columns: an array of structs, a struct and a coupon field that only one event had. Note <code>order_id</code> became a <b>string</b> because one event sent <code>"9103"</code>. The same events as a JSON array were 39 lines of <code>_corrupt_record</code> until <code>multiLine=True</code>.'),
    ('Step 6 · explode, gzip and JSON inference',
     code('python', 'l51_csv_json.py', 'j.select("order_id", F.explode("items").alias("it")).select("order_id", "it.dish", "it.qty").show()\nfor path in (big5m_csv, big5m_gz):            # 5M orders, 221 MiB vs 47 MiB gzip\n    df = spark.read.csv(path, header=True, schema=…); df.agg(F.sum("amount")).collect()\nspark.read.json(f"{D}/orders_json")                 # 1M rows, infer\nspark.read.json(f"{D}/orders_json", schema=…)', sec('== 9)')),
     '<code>explode</code> turned 3 events into 3 item rows (9103 had none and disappeared; <code>explode_outer</code> keeps it). The plain 221 MiB CSV was split into <b>7 partitions</b>; the 47 MiB gzip file into <b>1</b>, because gzip cannot be read from the middle. On a warm second run: 2.0 s against 3.4 s, and on a cluster the gap grows with every idle core. JSON inference read all 1M records (2.1 s) before any query and guessed every number as <code>bigint</code>.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('header + schema, defaults', W), ('rows: 8   (7 orders sent)', RD), ('review cut, amount null', Y)], size=7.6),
    term([('_corrupt_record keeps raw lines', G), ('bad rows: 4', Y)], size=7.6),
    term([('multiLine=True, escape=\'"\'', W), ('rows: 7', G), ('3 flagged: abc, EXTRA, 02/11/2026', Y)], size=7.2),
    term([('DROPMALFORMED count(): 6', Y), ('DROPMALFORMED all cols: 4', RD), ('FAILFAST: stopped at 9003', W)], size=7.4),
    term([('plain csv: 7 partitions, 2.0 s', G), ('csv.gz   : 1 partition, 3.4 s', Y), ('JSON infer: 2.1 s, all bigint', Y)], size=7.4),
]
B1 = [
    t(180, 14, 'A line break is not a new row', 9.4, bold=True) + lines(80, 30, L5[:4], ['card', 'card', 'violet', 'red']) + cap('Without multiLine, one row became two.', '', 'red', y=144, h=30),
    t(180, 14, 'PERMISSIVE keeps the evidence', 9.4, bold=True) + lines(20, 34, ['9003,Delhi,abc,…', '9006,…,02/11/2026,…'], ['acc', 'acc'], 150) + opbox(200, 34, '_corrupt_record', 'raw line', 'violet', 140, 30) + arrow(170, 50, 200, 50, 'ink3', 1.0) + cap('Bad fields null, raw line saved.', '', 'green', y=144, h=30),
    t(180, 14, 'Quotes and line breaks', 9.4, bold=True) + lines(60, 36, ['"Loved it.↵Will order again"', '"He said ""wow"""'], ['green', 'green'], 240) + cap('multiLine and escape fixed both rows.', '', 'green', y=144, h=30),
    t(180, 14, 'Only needed columns are parsed', 9.4, bold=True) + flow([('count()', 'no columns', 'amber'), ('6 rows', 'abc unseen', 'amber')], y=34, w=96, gap=22) + flow([('all columns', 'parsed', 'green'), ('4 rows', 'all checked', 'green')], y=82, w=96, gap=22) + cap('Bad depends on what you read.', '', 'red', y=144, h=30),
    t(180, 14, 'gzip has no split points', 9.4, bold=True) + ''.join(opbox(20 + k * 46, 40, f'p{k + 1}', '', 'green', 40, 24) for k in range(7)) + opbox(20, 84, 'one task reads all 47 MiB', 'csv.gz', 'amber', 320, 26) + cap('Use splittable formats or many files.', '', 'amber', y=144, h=30),
]
see_caps = ['Defaults: 8 rows from 7 orders.', 'The bad lines became visible.', 'The correct reading: 7 rows.', 'count() and collect() disagreed.', 'One core for the gzip file.']
behind_caps = ['A newline ends a record by default.', 'Raw text goes to _corrupt_record.', 'Quotes may hold commas and newlines.', 'Column pruning skips unused fields.', 'Non-splittable codec: one task per file.']
two = anim_two('Reading CSV and JSON', 'Text needs instructions', 'Real lab outputs', 'What the parser does', see, B1, see_caps, behind_caps)

# ---- scenario 1: silent row inflation
e1 = (t(180, 22, 'Partner CSV, default options', 9.4, bold=True) + t(180, 56, 'spark.read.csv(path, header=True)', 8.2, 'ink', mono=True) + cap('Daily load.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Order count > partner count', 9.4, bold=True) + t(180, 56, '8 vs 7 in our sample', 8.4, 'ink2') + cap('Reviews contain line breaks.', '', 'amber', y=150, h=34))
e3 = (t(180, 22, 'Finance disputes the invoice', 9.4, bold=True) + t(180, 56, 'phantom rows of nulls', 8.4, 'ink2') + cap('Nobody saw an error.', '', 'red', y=150, h=34))
e4 = (t(180, 22, 'multiLine + escape + schema', 9.4, bold=True) + t(180, 56, 'plus _corrupt_record', 8.4, 'ink', mono=True) + cap('Counts match the partner.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Reconcile every load', 9.4, 'acc', bold=True) + t(180, 56, 'rows read = rows sent + quarantined', 8.2, 'ink2') + cap('A control total.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'More orders than the partner sent',
              'Line breaks inside CSV values. (Behaviour from our lab.)',
              'CSV line breaks', 'Quoted values with line breaks split into extra rows unless multiLine is enabled; reconcile row counts on every load', [e1, e2, e3, e4, e5],
              ['Default read.', 'Extra rows.', 'Dispute.', 'Right options.', 'Control totals.'],
              hid='scenario-multiline')

# ---- scenario 2: quarantine
b1 = (t(180, 22, 'Bad rows must not stop the load', 9.4, bold=True) + t(180, 56, 'but must not vanish either', 8.4, 'ink2') + cap('Requirement from finance.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'PERMISSIVE + _corrupt_record', 9.4, bold=True) + t(180, 56, 'schema + ", _corrupt_record STRING"', 8.0, 'ink', mono=True) + cap('Read once, cache.', '', 'green', y=150, h=34))
b3 = (t(180, 22, 'Split good and bad', 9.4, bold=True) + t(180, 56, 'where _corrupt_record IS NULL / NOT NULL', 7.8, 'ink', mono=True) + cap('Two outputs.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Quarantine table + alert', 9.4, bold=True) + t(180, 56, 'bad_rows(date, file, raw_line)', 8.2, 'ink', mono=True) + cap('Partner fixes and resends.', '', 'violet', y=150, h=34))
b5 = (t(180, 22, 'Not DROPMALFORMED', 9.4, 'acc', bold=True) + t(180, 56, 'its count even changes by query', 8.4, 'ink2') + cap('6 vs 4 in our lab.', '', 'red', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'A quarantine for bad rows',
              'Handling corrupt records in production. (Typical; behaviour from our lab.)',
              'Corrupt records', 'Keep bad rows in a corrupt-record column, split them into a quarantine table and alert; never drop them silently', [b1, b2, b3, b4, b5],
              ['Requirement.', 'Keep raw lines.', 'Split.', 'Quarantine.', 'Avoid DROPMALFORMED.'],
              hid='scenario-quarantine')

# ---- scenario 3: one big gzip
u1 = (t(180, 22, 'Nightly export: one 40 GB .csv.gz', 9.4, bold=True) + t(180, 56, '100-core cluster', 8.4, 'ink2') + cap('Job takes 2 hours.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Spark UI: 1 task running', 9.4, bold=True) + t(180, 56, '99 cores idle', 8.4, 'ink2') + cap('gzip is not splittable.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'Ask for many files', 9.4, bold=True) + t(180, 56, 'or bzip2 / uncompressed', 8.4, 'ink2') + cap('Parallel reads.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Or convert once', 9.4, bold=True) + t(180, 56, 'read gz → repartition → Parquet', 8.4, 'ink2') + cap('Later jobs are fast.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Our lab', 9.4, 'acc', bold=True) + t(180, 56, '1 vs 7 partitions, 3.4 vs 2.0 s', 8.4, 'ink2') + cap('Bigger files, bigger gap.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'One file, one core',
              'Splittable compression. (Typical; numbers from our lab.)',
              'gzip splits', 'A gzip file is read by one task; prefer many files, splittable codecs, or convert once to Parquet', [u1, u2, u3, u4, u5],
              ['Big gzip.', 'One task.', 'Many files.', 'Convert once.', 'Measured.'],
              hid='scenario-gzip')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Text needs instructions</h2>
  <p>Left: real outputs. Right: what the parser does with each line.</p>
''' + two + '''
  <p>Three live scenarios follow: more orders than the partner sent, a quarantine for bad rows, and a gzip file that used one core.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>CSV and JSON at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'partners', 10, 'blue', bold=True) + t(60, 58, 'CSV feeds', 7.4, 'ink2'),
    '1. Partner and bank files',
    'Settlement and partner feeds arrive as CSV; jobs read them with a fixed schema, a corrupt-record column and control totals.',
    ['CSV drop', '*schema + PERMISSIVE', 'Clean + quarantine']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'events', 11, 'green', bold=True) + t(60, 58, 'JSON lines', 7.4, 'ink2'),
    '2. App events',
    'Mobile and web events land as JSON Lines in object storage and are flattened with explode and struct access.',
    ['JSON Lines', '*explode', 'Event tables']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'API', 12, 'violet', bold=True) + t(60, 58, 'dumps', 7.4, 'ink2'),
    '3. API exports',
    'Pretty-printed JSON arrays from APIs are read with multiLine and a schema.',
    ['API dump', '*multiLine', 'DataFrame']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'bronze', 11, 'acc', bold=True) + t(60, 58, 'raw layer', 7.4, 'ink2'),
    '4. Raw to columnar',
    'Text files are read once in a “bronze” step and written as Parquet or Delta for every later job (Lesson 5.2).',
    ['CSV / JSON', '*read once', 'Parquet']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'Excel', 12, 'acc', bold=True) + t(60, 58, 'exports', 7.4, 'ink2'),
    '5. Spreadsheet exports',
    'Exports from Excel use doubled quotes and local date formats: escape and dateFormat options are standard.',
    ['Excel CSV', '*escape=\'"\'', 'Correct values']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> schemas in <a href="../../04-dataframes/02-creating-dataframes-and-schemas/">4.2</a> and nulls in <a href="../../04-dataframes/04-nulls-and-duplicates/">4.4</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
