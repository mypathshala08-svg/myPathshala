import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()

SIZES = [('TEXT', 3735865), ('SEQUENCE', 4336792), ('RCFILE', 2019223), ('AVRO', 2510687), ('ORC', 437536), ('PARQUET', 1093857)]
def sizebars(y=40, hi=None):
    o = ''
    for k, (n, b) in enumerate(SIZES):
        w = round(220 * b / 4336792)
        col = 'acc' if hi is None or n in hi else 'grey'
        o += t(84, y + 11 + k * 20, n, 7.6, 'ink', anchor='end', mono=True) + fill(90, y + k * 20, w, 14, col, rx=2) + t(96 + w, y + 11 + k * 20, f'{b / 1e6:.2f} MB', 7.2, 'ink2', anchor='start', mono=True)
    return o

# ---------------------------------------------------------------- story
sc = (box(10, 12, 300, 128, 'card') + t(160, 30, 'Partner CSV, new version', 8.8, bold=True) +
      t(22, 54, 'v1: id,name,city', 7.8, 'ink2', anchor='start', mono=True) + t(22, 70, 'v2: id,name,plan,city', 7.8, 'acc', anchor='start', mono=True, bold=True) +
      t(22, 96, 'Hive text table reads by position:', 7.8, 'ink', anchor='start') + t(22, 114, '4 | Diya Patil | city = Gold', 8, 'red', anchor='start', mono=True, bold=True) + t(22, 130, 'no error', 7.4, 'red', anchor='start') +
      box(330, 12, 300, 128, 'green') + t(480, 30, 'Same data as Avro', 8.8, 'green', bold=True) +
      t(342, 54, 'every file carries its schema', 7.8, 'ink2', anchor='start') + t(342, 72, 'Hive reads fields by NAME', 7.8, 'ink', anchor='start', bold=True) +
      t(342, 96, '4 | Diya Patil | Gold | Pune', 8, 'green', anchor='start', mono=True, bold=True) + t(342, 114, '1 | Aarav Desai | Basic | Bengaluru', 8, 'green', anchor='start', mono=True) + t(342, 130, 'missing plan → default “Basic”', 7.4, 'ink2', anchor='start'))
scene_svg = scene('A partner adds a column in the middle of their CSV. The Hive text table reads by position and puts the plan into the city column without any error. The same data in Avro is read by field name, and old records get the default plan.', sc,
                  'The file format decides <tspan font-weight="700" class="s-acc">how Hive finds each value</tspan>: by position, or by name.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Why does the report show a city called Gold?”</h2>
  <div class="story">
    <p class="narration">A partner company sends TiffinGo customer files every week. This week the city report suddenly shows two new cities, <b>Gold</b> and <b>Basic</b>. Nobody changed the Hive table. Kabir opens the CSV and sees that the partner added a <code>plan</code> column in the middle.</p>

{scene_svg}

K> Sir, the query didn’t fail. It just put the plan into the city column!
A> A text table has no idea what the columns are called. Hive splits each line at the commas and takes the third value as <code>city</code>, whatever it is. Formats like <b>Avro</b> store the schema inside every file, so Hive can match fields by <b>name</b> and fill a default for fields that old files don’t have.
R> So which format should we use for everything?
A> It depends on the job. Today we write the same 50,000 orders in all six formats Hive supports and compare their sizes and their first bytes, compress text files, and look at the two row formats you will meet in older systems and data exchange: SequenceFile and Avro. Lessons 6.2 and 6.3 cover the columnar formats ORC and Parquet. All outputs are real, from Hive 4.2.1.
  </div>
</section>
'''

lv = '''
LEVELS> File formats at three levels
L1> The same data, packed differently
      <ul>
        <li>A file format is the way rows are written to disk. A <b>text</b> file is what you see in Notepad: values separated by commas, one row per line.</li>
        <li><b>Binary</b> formats (SequenceFile, Avro, ORC, Parquet) are not readable in Notepad, but they are smaller, faster to read and can store types and schemas.</li>
        <li>You choose the format with <code>STORED AS</code> when you create a table. If you say nothing, Hive 4.2.1 uses <b>TEXTFILE</b> (<code>hive.default.fileformat</code>).</li>
      </ul>
L2> Row formats vs column formats
      <ul>
        <li><b>Row-oriented:</b> TEXTFILE, SEQUENCEFILE, AVRO store one whole row after another. Good for writing records one by one and for exchanging data.</li>
        <li><b>Column-oriented:</b> RCFILE, ORC, PARQUET group values of the same column together. Good for analytics that read a few columns of many rows; they compress much better.</li>
        <li><b>Self-describing:</b> Avro, ORC and Parquet store the schema in the file. Text does not, so text tables read values <b>by position</b>.</li>
        <li><b>Splittable:</b> several tasks can read one big file in parallel. Plain text is splittable; a <code>.gz</code> text file is <b>not</b>; bzip2 text is; SequenceFile, Avro, ORC and Parquet are, because they compress in blocks with sync markers.</li>
      </ul>
L3> What Hive 4.2.1 did in our lab
      <ul>
        <li>Defaults: <code>hive.default.fileformat=TextFile</code> and <code>hive.exec.compress.output=false</code>, so a plain CTAS into TEXT, SEQUENCEFILE, RCFILE or AVRO wrote <b>uncompressed</b> files. ORC used ZLIB by default (<code>hive.exec.orc.default.compress</code>).</li>
        <li>SequenceFile was the <b>largest</b> (4.34 MB, bigger than the 3.74 MB text file): it wraps each text row in a key/value record.</li>
        <li>Avro wrote the full JSON schema into the file header; Hive turned each column into a nullable union <code>["null","int"]</code> with default null.</li>
        <li><code>ALTER TABLE … SET FILEFORMAT ORC</code> changes only metadata: the existing text file then failed with “Malformed ORC file … Invalid postscript” until the data was rewritten.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Hive file formats</h2>
''' + def_block(
    'A <b>file format</b> (storage format) defines how a table’s rows are encoded in its data files. In Hive it is declared with <code>STORED AS</code> (TEXTFILE, SEQUENCEFILE, RCFILE, AVRO, ORC, PARQUET, JSONFILE) or with explicit <code>INPUTFORMAT</code>/<code>OUTPUTFORMAT</code> classes and a <code>SerDe</code>. <b>TEXTFILE</b> stores delimited plain text; <b>SEQUENCEFILE</b> is Hadoop’s binary key/value container with optional record or block compression; <b>AVRO</b> is a row-oriented binary format whose files embed a JSON schema, supporting schema evolution through reader/writer schema resolution. Formats differ in size, read speed, splittability, type support and schema handling.',
    'The file format is how Hive writes your rows to disk. Text is easy to read but big and fragile. SequenceFile is Hadoop’s simple binary box. Avro is a binary row format that carries its own schema, so it survives columns being added. ORC and Parquet (next lessons) store data by column for fast analytics.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('STORED AS', 'Clause that picks the file format of a table.'),
    ('Row-oriented', 'All values of one row are stored together (text, SequenceFile, Avro).'),
    ('Column-oriented', 'All values of one column are stored together (RCFile, ORC, Parquet).'),
    ('Splittable', 'A file several tasks can read in parallel, starting from the middle.'),
    ('Magic bytes', 'The first bytes that identify a format: SEQ, RCF, Obj, ORC, PAR1.'),
    ('Codec', 'A compression algorithm: gzip, bzip2, Snappy, LZ4, ZSTD.'),
    ('Schema evolution', 'Changing a schema (add, rename, remove fields) while old files stay readable.'),
    ('Reader / writer schema', 'Avro resolves the schema a file was written with against the one you read with.'),
]) + '''

  <h3>The six formats at a glance</h3>
''' + table(['Format', 'Layout', 'Schema in file?', 'Splittable?', 'Typical use'], [
    ['TEXTFILE (CSV, TSV)', 'Row, plain text', 'No', 'Yes (not when .gz)', 'Landing raw files, data from other systems'],
    ['SEQUENCEFILE', 'Row, binary key/value', 'Class names only', 'Yes', 'Legacy MapReduce pipelines, packing small files'],
    ['RCFILE', 'Column groups per row group', 'No', 'Yes', 'Older warehouses; replaced by ORC'],
    ['AVRO', 'Row, binary', '<b>Yes</b>, JSON schema', 'Yes', 'Data exchange, Kafka/streaming, changing schemas'],
    ['ORC', 'Columnar, stripes', 'Yes', 'Yes', 'Hive analytics, ACID tables (6.2)'],
    ['PARQUET', 'Columnar, row groups', 'Yes', 'Yes', 'Analytics shared with Spark, Trino, Impala (6.3)'],
], minw=720) + lv + '''
EXAM> Frequently asked: “Name the file formats supported by Hive and compare them.” Give the six, split them into row (Text, SequenceFile, Avro) and columnar (RCFile, ORC, Parquet), and add one strength each: text is human-readable, SequenceFile is a binary key/value container, Avro supports schema evolution, ORC and Parquet compress well and skip data using statistics.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Ways to choose and change a format</h2>
''' + table(['Want', 'Statement', 'Note'], [
    ['Pick a format', '<code>CREATE TABLE t (…) STORED AS AVRO;</code>', 'Also SEQUENCEFILE, RCFILE, ORC, PARQUET, JSONFILE, TEXTFILE'],
    ['Convert data', '<code>CREATE TABLE t_orc STORED AS ORC AS SELECT * FROM t_text;</code>', 'Reads one format, writes another'],
    ['Compress text output', '<code>SET hive.exec.compress.output=true;</code> + <code>mapreduce.output.fileoutputformat.compress.codec</code>', 'Gzip, BZip2, Snappy, Default (deflate)'],
    ['Avro with your schema', "<code>TBLPROPERTIES ('avro.schema.literal'='{…}')</code> or <code>'avro.schema.url'='hdfs://…/x.avsc'</code>", 'Columns come from the schema'],
    ['Change the default', '<code>SET hive.default.fileformat=ORC;</code>', 'For tables created without STORED AS'],
    ['Custom format', '<code>STORED AS INPUTFORMAT \'…\' OUTPUTFORMAT \'…\'</code> + <code>ROW FORMAT SERDE \'…\'</code>', 'What STORED AS expands to'],
], minw=720) + '''
WARN> <code>ALTER TABLE t SET FILEFORMAT …</code> only changes the table definition. Files already in the table stay in the old format and cannot be read with the new one (Step 8). To really convert, create a new table with CTAS or rewrite the data with INSERT OVERWRITE.
</section>
'''

ev = tables(capf('l61_evo.txt'))
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>One dataset, six formats</h2>
  <p>All outputs are real, from the Hive 4.2.1 lab (database <code>tiffingo</code>).</p>
''' + stepper([
    ('Step 1 · What do you get without STORED AS?',
     code('sql', 'Beeline', "SET hive.default.fileformat;\nSET hive.exec.compress.output;\nSET hive.exec.orc.default.compress;", '| hive.default.fileformat=TextFile    |\n| hive.exec.compress.output=false     |\n| hive.exec.orc.default.compress=ZLIB |'),
     'A table created without <code>STORED AS</code> is a plain text table, with fields separated by the invisible character <code>\\001</code> (Ctrl-A) unless you give ROW FORMAT DELIMITED, and output is not compressed unless you ask. ORC is the exception: it has its own compression setting, ZLIB by default. (Some vendor distributions change these defaults to ORC; always check your cluster.)'),
    ('Step 2 · Write the same 50,000 orders six ways',
     code('sql', 'Beeline', "CREATE TABLE f_text    STORED AS TEXTFILE     AS SELECT * FROM orders;\nCREATE TABLE f_seq     STORED AS SEQUENCEFILE AS SELECT * FROM orders;\nCREATE TABLE f_rc      STORED AS RCFILE       AS SELECT * FROM orders;\nCREATE TABLE f_avro    STORED AS AVRO         AS SELECT * FROM orders;\nCREATE TABLE f_orc     STORED AS ORC          AS SELECT * FROM orders;\nCREATE TABLE f_parquet STORED AS PARQUET      AS SELECT * FROM orders;\n-- then: ls -l each table folder, and look at the first bytes of each file", capf('l61_sizes.txt')),
     'Same rows, very different files. SequenceFile is the <b>largest</b>: it stores each text row inside a binary key/value record. Avro saves space by storing numbers in binary. The columnar formats win clearly; ORC is 8.5 times smaller than text. Each binary format starts with its own <b>magic bytes</b>, which is how tools recognise a file.'),
    ('Step 3 · Compress text files, and why .gz hurts parallelism',
     code('sql', 'Beeline', "SET hive.exec.compress.output=true;\nSET mapreduce.output.fileoutputformat.compress.codec=org.apache.hadoop.io.compress.GzipCodec;\nCREATE TABLE f_text_gz STORED AS TEXTFILE AS SELECT * FROM orders;\n-- repeated with BZip2Codec and SnappyCodec\nSELECT COUNT(*), SUM(amount) FROM f_text_gz;", capf('l61_compressed.txt').split('\nSEQUENCEFILE')[0] + '\n\n' + capf('l61_gz.txt')),
     'Hive reads compressed text transparently, using the file extension to pick the codec. Gzip shrank the file 5×, bzip2 8×. The catch: a <code>.gz</code> (or plain <code>.snappy</code>) text file cannot be split, so one task must read the whole file, however large. bzip2 is splittable but very slow (Lesson 6.3 measures it). That is why big data teams compress inside container formats instead.'),
    ('Step 4 · SequenceFile: Hadoop’s binary container',
     code('sql', 'Beeline', "SET hive.exec.compress.output=true;\nSET mapreduce.output.fileoutputformat.compress.codec=org.apache.hadoop.io.compress.SnappyCodec;\nSET io.seqfile.compression.type=BLOCK;\nCREATE TABLE f_seq_snappy STORED AS SEQUENCEFILE AS SELECT * FROM orders;", 'f_seq (no compression)       4,336,792 bytes   SEQ…org.apache.hadoop.io.BytesWritable…\nf_seq_snappy (BLOCK snappy)  1,384,953 bytes'),
     'A SequenceFile is a list of binary key/value records with <b>sync markers</b>, so it stays splittable even when compressed. BLOCK compression compresses many records together (much better than RECORD). Hive stores the row in the value and leaves the key empty. It was the classic way to pack many small files into one; for analytics today, prefer ORC or Parquet.'),
    ('Step 5 · Avro carries its schema',
     code('sql', 'Beeline', "DESCRIBE f_avro;\n-- first bytes of the data file:\n$ head -c 400 …/f_avro/000000_0", tables(capf('l61_avro_show.txt'))[0] + '\n\nObj..avro.schema..{"type":"record","name":"f_avro","namespace":"tiffingo","fields":[\n  {"name":"order_id","type":["null","int"],"default":null},\n  {"name":"customer_id","type":["null","int"],"default":null}, …\n  {"name":"order_ts","type":["null",{"type":"long","logicalType":"timestamp-millis"}],"default":null}, …'),
     'Every Avro file begins with <code>Obj</code>, then its writer schema in JSON. Hive generated it from the table: each column is a union with <code>null</code> (Hive columns are nullable) and has a default. Timestamps became <code>timestamp-millis</code> longs and decimals became bytes with precision and scale.'),
    ('Step 6 · The partner adds a column: a text table reads by position',
     code('sql', 'Beeline', "-- part-v1.csv: 1,Aarav Desai,Bengaluru\n-- part-v2.csv: 4,Diya Patil,Gold,Pune        (plan added before city)\nCREATE EXTERNAL TABLE cust_txt (customer_id INT, name STRING, city STRING)\nROW FORMAT DELIMITED FIELDS TERMINATED BY ','\nLOCATION 'file:///data/tiffingo/cust_txt';\nSELECT * FROM cust_txt ORDER BY customer_id;", ev[0]),
     'No error and no warning. The third value of each line goes into <code>city</code>, so Diya’s plan “Gold” became her city, and the real city “Pune” was silently dropped as an extra field. This is exactly the bug in Kabir’s report.'),
    ('Step 7 · The same change in Avro: read by name, default for old files',
     code('sql', 'Beeline', "-- part-v1.avro written with schema {customer_id, name, city}\n-- part-v2.avro written with schema {customer_id, name, plan, city}\nCREATE EXTERNAL TABLE cust_avro STORED AS AVRO\nLOCATION 'file:///data/tiffingo/cust_avro'\nTBLPROPERTIES ('avro.schema.literal'='{\"type\":\"record\",\"name\":\"customer\",\n  \"fields\":[{\"name\":\"customer_id\",\"type\":\"int\"},{\"name\":\"name\",\"type\":\"string\"},\n  {\"name\":\"plan\",\"type\":\"string\",\"default\":\"Basic\"},{\"name\":\"city\",\"type\":\"string\"}]}');\nSELECT * FROM cust_avro ORDER BY customer_id;", ev[1]),
     'Hive gave Avro the table’s schema as the <b>reader</b> schema. For each file, Avro matched fields by name with that file’s <b>writer</b> schema: old v1 records have no <code>plan</code>, so they got the default “Basic”; v2 records kept “Gold” and the correct city. Rule for safe evolution: new fields need a default.'),
    ('Step 8 · Trap: SET FILEFORMAT does not convert data',
     code('sql', 'Beeline', "CREATE TABLE ff_trap STORED AS TEXTFILE AS\n  SELECT order_id, city, amount FROM orders WHERE order_id < 100004;\nALTER TABLE ff_trap SET FILEFORMAT ORC;\nSELECT * FROM ff_trap;\n\n-- fix: rewrite the data in the new format\nINSERT OVERWRITE TABLE ff_trap SELECT order_id, city, amount FROM orders WHERE order_id < 100004;\nSELECT * FROM ff_trap;", capf('l61_setff.txt').split('; Query ID')[0].replace('Error while compiling statement: ', '') + '\n\n' + capf('l61_setff2.txt')),
     'After the ALTER, Hive tried to read the old text file as ORC and could not find an ORC postscript (the small trailer every ORC file ends with, Lesson 6.2). Rewriting the rows produced a real ORC file. In production, convert with CTAS into a new table, compare counts, then swap names.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('> SET hive.default.fileformat;', W), ('| hive.default.fileformat=TextFile |', G), ('> SET hive.exec.compress.output;', W), ('| hive.exec.compress.output=false  |', Y)]),
    term([('TEXTFILE      3,735,865', W), ('SEQUENCEFILE  4,336,792', RD), ('RCFILE        2,019,223', W), ('AVRO          2,510,687', W), ('ORC             437,536', G), ('PARQUET       1,093,857', G)]),
    term([('$ head -c 40 each file', W), ('SEQ…org.apache.hadoop.io.BytesWritable', Y), ('RCF…hive.io.rcfile.column.number', Y), ('Obj…avro.schema {"type":"record"…', Y), ('ORC…            PAR1…', Y)]),
    term([('> SELECT * FROM cust_txt;', W), ('| 1 | Aarav Desai | Bengaluru |', G), ('| 4 | Diya Patil  | Gold      |', RD), ('| 5 | Ishaan Khan | Basic     |', RD)]),
    term([('> SELECT * FROM cust_avro;', W), ('| 1 | Aarav Desai | Basic | Bengaluru |', G), ('| 4 | Diya Patil  | Gold  | Pune      |', G), ('| 5 | Ishaan Khan | Basic | Thane     |', G)]),
]
def rowcol(y, mode):
    o = ''
    vals = [['100001', 'Mumbai', '530'], ['100002', 'Mumbai', '500'], ['100003', 'Pune', '410']]
    if mode == 'row':
        for r, row in enumerate(vals):
            for c, v in enumerate(row):
                o += box(20 + (r * 3 + c) * 36, y, 34, 22, ['acc', 'blue', 'green'][r]) + t(37 + (r * 3 + c) * 36, y + 14, v, 6.4, 'ink', mono=True)
    else:
        for c in range(3):
            for r in range(3):
                o += box(20 + (c * 3 + r) * 36, y, 34, 22, ['acc', 'blue', 'green'][r]) + t(37 + (c * 3 + r) * 36, y + 14, vals[r][c], 6.4, 'ink', mono=True)
    return o
B1 = [
    t(180, 22, 'No STORED AS → plain text lines', 9.4, bold=True) + t(30, 56, '100001^A1932^A35^AMumbai^A2026-10-29 20:49:00…', 7.6, 'ink', anchor='start', mono=True) + t(30, 72, '100002^A1991^A2^AMumbai^A2026-10-17 20:25:00…', 7.6, 'ink', anchor='start', mono=True) + t(30, 88, '^A = the default field delimiter \\001 (Ctrl-A)', 7.6, 'ink2', anchor='start') +
    cap('Readable, large, typeless.', 'Numbers and dates are stored as text.', 'blue', y=150, h=46),
    t(180, 22, 'Bytes on disk (same 50,000 rows)', 9.4, bold=True) + sizebars(36) + cap('Columnar formats compress best.', 'SequenceFile adds per-record overhead.', 'green', y=164, h=40),
    t(180, 22, 'Row layout vs column layout', 9.4, bold=True) + t(20, 42, 'row: TEXT · SEQUENCE · AVRO', 7.8, 'ink2', anchor='start') + rowcol(48, 'row') + t(20, 92, 'column: RCFILE · ORC · PARQUET', 7.8, 'ink2', anchor='start') + rowcol(98, 'col') +
    cap('Same values, different order on disk.', 'Similar values side by side compress well.', 'blue', y=150, h=46),
    t(180, 22, 'Text: values matched by position', 9.4, bold=True) + ''.join(box(20 + k * 82, 46, 76, 22, 'card') + t(58 + k * 82, 61, c, 7.6, 'ink', mono=True) for k, c in enumerate(['4', 'Diya Patil', 'Gold', 'Pune'])) +
    ''.join(t(58 + k * 82, 86, c, 7.6, 'red' if k >= 2 else 'green', mono=True, bold=True) for k, c in enumerate(['id', 'name', 'city', '(dropped)'])) + cap('Third field = city, whatever it is.', '', 'amber', y=150, h=34),
    t(180, 22, 'Avro: writer schema resolved by name', 9.4, bold=True) + box(20, 42, 150, 70, 'card') + t(95, 58, 'v1 file schema', 8, bold=True) + t(95, 76, 'id, name, city', 7.6, 'ink2', mono=True) + t(95, 96, '(no plan field)', 7.4, 'ink3', mono=True) +
    box(190, 42, 150, 70, 'green') + t(265, 58, 'table (reader) schema', 8, bold=True) + t(265, 76, 'id, name, plan, city', 7.6, 'ink', mono=True) + t(265, 96, 'plan default “Basic”', 7.4, 'green', mono=True, bold=True) + cap('Fields matched by name; missing ones get defaults.', '', 'green', y=150, h=34),
]
see_caps = ['Without STORED AS, Hive 4.2.1 writes uncompressed text.',
            'The same 50,000 orders in six formats: from 4.3 MB down to 0.44 MB.',
            'Each binary format announces itself in its first bytes.',
            'The text table put plan values into the city column.',
            'The Avro table read every file correctly, with a default for old ones.']
behind_caps = ['Text stores every value as characters, one row per line.',
               'Columnar formats group similar values and compress them well.',
               'Row formats keep each row together; columnar formats keep each column together.',
               'Delimited text has no schema, so fields are matched by position.',
               'Avro compares the file’s writer schema with the table’s reader schema, field by field.']
two = anim_two('File formats', 'Layout, size and schemas', 'Real Beeline output', 'How each format stores and finds values', see, B1, see_caps, behind_caps)

# ---- scenario 1: landing zone
l1 = (t(180, 22, 'Raw zone: files as they arrive', 9.4, bold=True) + t(180, 56, 'CSV / JSON from apps and partners → TEXTFILE tables', 8.2, 'ink2') + cap('Keep raw data exactly as received.', '', 'blue', y=150, h=34))
l2 = (t(180, 22, 'Curated zone: convert once', 9.4, bold=True) + t(180, 56, 'INSERT OVERWRITE … STORED AS ORC / PARQUET', 8.4, 'ink', mono=True) + cap('Typed, compressed, columnar.', '', 'green', y=150, h=34))
l3 = (t(180, 22, 'Size after conversion (real)', 9.4, bold=True) + sizebars(36, hi={'TEXT', 'ORC'}) + cap('3.74 MB of text → 0.44 MB of ORC.', '', 'green', y=164, h=40))
l4 = (t(180, 22, 'Reports read the curated tables', 9.4, bold=True) + t(180, 56, 'few columns × many rows → columnar wins', 8.4, 'ink2') + cap('Raw text is kept for audits and re-processing.', '', 'blue', y=150, h=34))
l5 = (t(180, 22, 'Retention', 9.4, 'acc', bold=True) + t(180, 56, 'raw: 30–90 days · curated: years', 8.4, 'ink2') + cap('Cheap storage for the long-lived copy.', '(typical policy)', 'blue', y=150, h=46))
s1 = anim_one('Real-time scenario 1', 'Raw text in, columnar out',
              'Most data lakes keep two copies: raw files in the format they arrived, and curated columnar tables for queries. Sizes are real.',
              'Landing and curated zones', 'Text files land in a raw zone and are converted once into ORC or Parquet for querying', [l1, l2, l3, l4, l5],
              ['Files land unchanged in text tables.',
               'A job converts them once into a columnar format.',
               'Our 50,000 orders shrank from 3.74 MB to 0.44 MB.',
               'Reports query only the curated tables.',
               'Raw files are kept for a shorter time.'],
              hid='scenario-zones')

# ---- scenario 2: schema change
c1 = (t(180, 22, 'Partner announces a new field', 9.4, bold=True) + t(180, 56, 'plan: Gold / Silver / Basic', 8.4, 'ink', mono=True) + cap('Old files will not have it.', '', 'blue', y=150, h=34))
c2 = (t(180, 22, 'Text: silent shift (real)', 9.4, 'red', bold=True) + t(180, 56, '4 | Diya Patil | city = Gold', 8.4, 'red', mono=True) + cap('Wrong data, no error.', '', 'amber', y=150, h=34))
c3 = (t(180, 22, 'Avro: add the field with a default', 9.4, 'green', bold=True) + t(180, 56, '{"name":"plan","type":"string","default":"Basic"}', 7.8, 'ink', mono=True) + cap('Old and new files read correctly (real).', '', 'green', y=150, h=34))
c4 = (t(180, 22, 'Rules for compatible changes', 9.4, bold=True) + ''.join(t(30, 52 + k * 18, s, 8.2, anchor='start') for k, s in enumerate(['• add fields with defaults', '• do not reuse a field name for new meaning', '• renames need aliases', '• keep schemas in a registry / .avsc file']))
      + cap('Same rules as Kafka schema registries.', '', 'blue', y=150, h=34))
c5 = (t(180, 22, 'Share one schema file', 9.4, 'acc', bold=True) + t(180, 56, "TBLPROPERTIES ('avro.schema.url'='hdfs://…/customer.avsc')", 7.6, 'ink', mono=True) + cap('Update the .avsc, every table follows.', '', 'green', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'A partner adds a column',
              'The same schema change in a text table and in an Avro table. Both outputs are real.',
              'Schema evolution', 'A new field shifts values in a text table but is handled by name with a default in an Avro table', [c1, c2, c3, c4, c5],
              ['The partner adds a plan field.',
               'The text table silently shifts values into the wrong column.',
               'Avro reads by name and fills the default for old records.',
               'Follow the rules for compatible schema changes.',
               'Keep the schema in one .avsc file referenced by the table.'],
              hid='scenario-evolution')

# ---- scenario 3: gzip splitting
g1 = (t(180, 22, 'A 10 GB orders.csv.gz arrives', 9.4, bold=True) + t(180, 56, 'gzip is not splittable', 8.4, 'red') + cap('One task must read all 10 GB, start to end.', '(sample size)', 'amber', y=150, h=46))
g2 = (t(180, 22, 'Same data as bzip2', 9.4, bold=True) + t(180, 56, 'splittable, but slow to compress and read', 8.4, 'ink2') + cap('Real lab: smallest text file, 8× smaller.', '', 'blue', y=150, h=34))
g3 = (t(180, 22, 'Better: convert once', 9.4, 'green', bold=True) + t(180, 56, 'gzip text → one job → ORC / Parquet', 8.4, 'ink', mono=True) + cap('Block compression inside the format: splittable.', '', 'green', y=150, h=34))
g4 = (t(180, 22, 'Or ask for smaller files', 9.4, bold=True) + t(180, 56, '100 × 100 MB .gz files → 100 parallel tasks', 8.4, 'ink2') + cap('Many medium files still run in parallel.', 'Each file gets its own task.', 'blue', y=150, h=46))
g5 = (t(180, 22, 'Rule', 9.4, 'acc', bold=True) + t(180, 56, 'compress inside a container format, not around it', 8.2, 'ink2') + cap('SequenceFile, Avro, ORC, Parquet all do this.', '', 'green', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'One giant .gz file and one busy task',
              'Compression around a text file can destroy parallelism. Container formats compress in blocks and stay splittable. (Typical case.)',
              'Splittable compression', 'A large gzip text file is read by a single task; converting to a container format or using several smaller files restores parallelism', [g1, g2, g3, g4, g5],
              ['A huge gzip file can only be read by one task.',
               'bzip2 is splittable but slow.',
               'Convert it once into ORC or Parquet.',
               'Or receive many medium files instead of one giant one.',
               'Compress inside the container format.'],
              hid='scenario-gzip')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Same rows, different files</h2>
  <p>Left: real Beeline output. Right: how each format stores and finds values.</p>
''' + two + '''
  <p>Three live scenarios follow: raw and curated zones, a schema change, and a giant gzip file.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Row formats at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'CSV', 12, 'green', bold=True, mono=True) + t(60, 58, 'landing', 7.4, 'ink2'),
    '1. Landing files from other systems',
    'Banks, telecoms and government portals often exchange CSV or fixed-width text. Teams land them in external TEXTFILE tables before converting.',
    ['Partner file', '*TEXTFILE table', 'Convert to ORC']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'Avro', 12, 'blue', bold=True) + t(60, 58, 'Kafka', 7.4, 'ink2'),
    '2. Streaming and Kafka pipelines',
    'Avro is the common message format with a schema registry; connectors write Avro files to the lake, and Hive tables read them with the same schemas.',
    ['Kafka topic', '*Avro files', 'Hive table']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, '.avsc', 12, 'violet', bold=True, mono=True) + t(60, 58, 'contracts', 7.4, 'ink2'),
    '3. Data contracts between teams',
    'An Avro schema file is a written agreement: producers may only make compatible changes, so consumers never break silently.',
    ['Producer', '*schema rules', 'Safe consumers']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'SEQ', 12, 'acc', bold=True, mono=True) + t(60, 58, 'legacy', 7.4, 'ink2'),
    '4. Legacy Hadoop jobs',
    'Older MapReduce pipelines still produce SequenceFiles, for example packing millions of small images or logs into a few large files.',
    ['Small files', '*SequenceFile', 'Fewer, bigger files']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'migrate', 10, 'acc', bold=True) + t(60, 58, 'RCFile → ORC', 7.4, 'ink2'),
    '5. Warehouse modernisation',
    'Teams moving old clusters to new ones convert RCFile and text tables into ORC or Parquet with CTAS, often cutting storage by several times.',
    ['Old tables', '*CTAS', 'ORC / Parquet']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> you need row formats and SerDes (<a href="../../02-hiveql/04-row-formats-and-serdes/">2.4</a>) and loading data (<a href="../../02-hiveql/05-loading-data/">2.5</a>).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
