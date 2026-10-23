import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()
TX = rd('tx101.txt').strip()
L = TX.split('\n')
pick = lambda *starts: '\n'.join(l for l in L if l.startswith(starts))
TX_SEQ = '\n'.join([L[0], pick('text ', 'seq_')] + L[L.index('== the first bytes of a SequenceFile (a header that names its own types)'):L.index('== hdfs dfs -text decodes both binary formats') + 3])
TX_AVRO = '\n'.join([L[0], pick('avro_'), '== hdfs dfs -text on the Avro file'] + [l for l in L if l.startswith('{"order_id":1,') or l.startswith('{"order_id":2,')] + L[L.index('== an Avro file carries its schema'):L.index('== read each format with the same item-count job')])
TX_READ = TX[TX.index('== read each format'):].strip()

META = dict(
    module='10-data-formats', lesson='01-text-sequencefile-and-avro', n='10.1',
    module_label='Module 10 · Data formats and compression',
    title='Text, SequenceFile and Avro',
    desc='Hadoop row-oriented file formats measured on a real Hadoop 3.5.0 cluster with 5 lakh orders: CSV 19.4 MB, SequenceFile uncompressed 24.0 MB, record-compressed 27.9 MB (worse!), block-compressed 4.7 MB, Avro 16.6 MB without a codec and 4.8 MB with deflate. SequenceFile headers and sync markers, Avro schemas, schema evolution with defaults (and the AvroTypeException without one), reading every format with one MapReduce job. Python simulation of zig-zag varints and schema resolution, quiz and interview scenarios.',
    og_desc='The same orders in CSV, SequenceFile and Avro: 19.4 MB, 4.7 MB, 4.8 MB, and a new column added without breaking old files.',
    minutes=28, level='Intermediate',
    lead='CSV is easy to read and says nothing about its own columns. Hadoop\'s SequenceFile and Apache Avro store the same records as compact binary, stay splittable when compressed, and (in Avro\'s case) carry a schema that can change safely over time. This lesson converts real data into all of them and measures what each choice costs.',
    chips=['7 encodings of the same data, measured', 'Schema evolution on a real file', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Encode one order three ways',
    intro='<p>This model builds the bytes of one order as a CSV line, as an uncompressed SequenceFile record, and as an Avro record (zig-zag variable-length integers, strings as length + bytes). The layouts follow the real formats; the file headers are left out.</p>',
    code='''import struct

order = (1, "S1413", "2026-09-14 15:30", "dosa", 45)

def zigzag_varint(n):                       # Avro's int/long encoding
    n = (n << 1) ^ (n >> 63)                # zig-zag: 0,-1,1,-2 -> 0,1,2,3
    out = b""
    while n > 0x7F:
        out += bytes([(n & 0x7F) | 0x80])   # 7 bits per byte, high bit = "more follows"
        n >>= 7
    return out + bytes([n])

csv = (",".join(map(str, order)) + "\\n").encode()

value = ",".join(map(str, order[1:])).encode()               # Text value
seq = struct.pack(">ii", 8 + 1 + len(value), 8) + struct.pack(">q", order[0]) + bytes([len(value)]) + value

avro = zigzag_varint(order[0])
for s in order[1:4]:
    avro += zigzag_varint(len(s)) + s.encode()
avro += zigzag_varint(order[4])

for name, b in [("CSV", csv), ("SequenceFile", seq), ("Avro", avro)]:
    print(f"{name:13} {len(b):3} bytes  {b[:24]!r}")
''',
    anno=[
        ('    n = (n << 1) ^ (n >> 63)                # zig-zag: 0,-1,1,-2 -> 0,1,2,3', 'Zig-zag maps small negative numbers to small positive ones, so -1 also fits in one byte.'),
        ('seq = struct.pack(">ii", 8 + 1 + len(value), 8) + struct.pack(">q", order[0]) + bytes([len(value)]) + value', 'Record length, key length, an 8-byte LongWritable key, then the Text value with its length. About 9 bytes more than the CSV line per order.'),
        ('avro += zigzag_varint(order[4])', 'No field names and no separators: the schema in the file header says what comes next.'),
    ],
    tasks=[
        dict(label='1 · Three encodings', hint='Press <b>Run</b>. Which is smallest, and why is the SequenceFile record bigger than the CSV line?', code=None),
        dict(label='2 · Zig-zag varints', hint='<b>Predict first:</b> how many bytes does Avro need for 0, -1, 45, 64, 1000 and 500000?',
             code='''def zigzag_varint(n):
    n = (n << 1) ^ (n >> 63)
    out = b""
    while n > 0x7F:
        out += bytes([(n & 0x7F) | 0x80])
        n >>= 7
    return out + bytes([n])

for n in [0, -1, 45, 64, 1000, 500000]:
    b = zigzag_varint(n)
    print(f"{n:>7} -> {len(b)} byte(s)  {b.hex()}")
'''),
        dict(label='3 · Read with a new schema', hint='Simulate Avro schema resolution: the reader expects a <code>payment</code> field with a default. Then remove the default and run again.',
             code='''writer = ["order_id", "student", "time", "item", "amount"]
reader = [("order_id", None), ("student", None), ("time", None), ("item", None), ("amount", None), ("payment", "cash")]
row = dict(zip(writer, [432369, "S0454", "2026-09-20 12:05", "chai", 15]))

out = {}
for name, default in reader:
    if name in row:
        out[name] = row[name]                 # matched by NAME, not position
    elif default is not None:
        out[name] = default                   # new field: fill the default
    else:
        raise ValueError("missing required field " + name)
print(out)
'''),
        dict(label='4 · RECORD vs BLOCK', hint='Compress 2,000 order values one by one (like RECORD) and all together (like BLOCK). Why did our RECORD SequenceFile grow?',
             code='''import zlib, random
random.seed(1)
items = ["chai", "coffee", "samosa", "vada pav", "poha", "idli", "dosa", "thali"]
vals = [f"S{random.randint(1, 2000):04d},2026-09-{random.randint(1, 30):02d} {random.randint(8, 20)}:{random.randint(0, 59):02d},{random.choice(items)},20".encode() for _ in range(2000)]
raw = sum(len(v) for v in vals)
record = sum(len(zlib.compress(v)) for v in vals)
block = len(zlib.compress(b"".join(vals)))
print(f"raw {raw:,}  RECORD {record:,}  BLOCK {block:,} bytes")
'''),
        dict(label='5 · Spot the error', hint='This reader schema adds <code>payment</code> without a default, so reading an old row fails. Give it a default of <code>"cash"</code>.',
             code='''row = {"order_id": 1, "item": "dosa", "amount": 45}
reader = {"order_id": None, "item": None, "amount": None, "payment": None}   # None = no default
out = {}
for name, default in reader.items():
    if name in row:
        out[name] = row[name]
    elif default is None:
        raise ValueError("missing required field " + name)
    else:
        out[name] = default
print(out)
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: one dataset, seven encodings',
    intro='<p>Use the Module 8 lab cluster (<code>docker compose -p lab8 up -d</code>) and Module 9\'s <code>student_orders.csv</code>, already in HDFS. Hadoop ships the Avro core library but not <code>avro-mapred</code>, which holds Avro\'s InputFormat and OutputFormat, so <code>get_jars.sh</code> (in the last item) downloads it and the other format jars from Maven Central into <code>/tmp/mr10/lib</code>, and <code>formats_env.sh</code> puts them on the client classpath and ships them to the tasks with <code>-libjars</code>. Then compile the Java files into <code>mr10.jar</code> and run the lab script; it takes about 6 minutes.</p>',
    items=[
        dict(title='CSV to SequenceFile', file='ToSequenceFile.java',
             cmd=rd('java/ToSequenceFile.java') + '\n// Inside the namenode container, in /tmp/mr10 (after get_jars.sh):\n//   source formats_env.sh\n//   mkdir -p classes && javac -cp $(hadoop classpath):$HADOOP_CLASSPATH -d classes *.java && jar cf mr10.jar -C classes .\n//   hadoop jar mr10.jar ToSequenceFile -libjars $LIBJARS -D seq.compress=BLOCK /user/hadoop/data/student_orders.csv /out/f_seq_block',
             output=TX_SEQ,
             note='Real output from rowformats_lab.sh (below): the sizes, the first 150 bytes of the block-compressed file (non-printable bytes shown as dots), and hdfs dfs -text decoding it.'),
        dict(title='CSV to Avro, then a new schema', file='ToAvro.java',
             cmd=rd('java/ToAvro.java') + '\n// Inside the namenode container, in /tmp/mr10:\n//   hadoop jar mr10.jar ToAvro -libjars $LIBJARS -D avro.codec=deflate /user/hadoop/data/student_orders.csv /out/f_avro_deflate',
             output=TX_AVRO,
             note='Real output from rowformats_lab.sh. The schema-evolution rows come from part-m-00002.avro, written by the third map task, which is why they start at order 432369.'),
        dict(title='One job that reads any format', file='ItemCountAny.java',
             cmd=rd('java/ItemCountAny.java') + '\n// In.format=text|seq|avro here; parquet and orc are used in Lesson 10.2.\n//   hadoop jar mr10.jar ItemCountAny -libjars $LIBJARS -D in.format=avro /out/f_avro_deflate /out/r_avro',
             output=TX_READ,
             note='Real output. Only the InputFormat and the mapper\'s first line change between formats; the combiner and reducer are Hadoop\'s built-in LongSumReducer.'),
        dict(title='The whole lab: jars, environment, conversions, reads', file='rowformats_lab.sh',
             cmd='# ---- get_jars.sh (run once in /tmp/mr10) ----\n' + rd('get_jars.sh') + '\n# ---- formats_env.sh ----\n' + rd('formats_env.sh') + '\n# ---- rowformats_lab.sh ----\n' + rd('rowformats_lab.sh') + '\n# Inside the namenode container:  bash /tmp/mr10/rowformats_lab.sh',
             output=TX,
             note='Real output, complete. Sizes are for one replica (hdfs dfs -du); HDFS stores three. Your timings will differ; the byte counts will not, because the dataset and the writers are deterministic.'),
    ],
)

TRACE = dict(
    heading='Encoding 300 as a zig-zag varint',
    intro='<p>Avro writes every int and long this way. Follow how 300 becomes two bytes.</p>',
    code='''n = 300
z = (n << 1) ^ (n >> 63)
out = []
while z > 0x7F:
    out.append((z & 0x7F) | 0x80)
    z >>= 7
out.append(z)
print(z, [hex(b) for b in out])
''',
    notes={2: 'Zig-zag :: 300 becomes 600; negative numbers would become odd numbers.',
           5: '7 bits :: The low 7 bits go out first, with the high bit set to say “more bytes follow”.',
           7: 'Last byte :: High bit clear: this is the end of the number.'},
)

WORKED_INTRO = 'Three format decisions with numbers: storage cost, finding a record in the middle of a file, and whether a schema change is safe.'
EXAMPLES = [
    dict(level='b', tag='Sizing · storage', title='What does the format save over three years?',
         problem='<p>The college\'s orders grow to 50 lakh a month and are kept for 3 years with replication 3. Using our lab\'s sizes for 5 lakh orders (CSV 19,418,699 bytes, Avro deflate 4,793,471 bytes), how much raw HDFS disk does each format need?</p>',
         inp='50 lakh/month · 36 months · ×3 replication',
         approach=['Bytes per order from the lab.',
                   'Orders in 3 years × bytes × 3 replicas.',
                   'Compare.'],
         code='''orders = 5_000_000 * 36
for name, size in [("CSV", 19_418_699), ("Avro deflate", 4_793_471)]:
    per_order = size / 500_000
    print(f"{name:12} {per_order:5.1f} B/order -> {orders * per_order * 3 / 1024**3:6.1f} GB raw disk")
''', notes={3: 'Per order :: Measured sizes divided by 5 lakh orders.'},
         tryit='About 20 GB vs 5 GB here. At real company scale (lakhs of events per second) the same 4× is the difference between 4 racks and 1.'),
    dict(level='i', tag='Internals · sync markers', title='Where does a map task start reading?',
         problem='<p>A file of records has a 4-byte sync marker <code>#SY#</code> written before every few records. A map task is given the split starting at byte 14. Find where it really starts reading, and why it can\'t simply start at byte 14.</p>',
         inp='one byte string, split start 14',
         approach=['Byte 14 is in the middle of a record.',
                   'Scan forward for the next sync marker.',
                   'Start right after it; the previous task finishes the record it is in.'],
         code='''data = b"#SY#r1:chai|r2:dosa|r3:poha|#SY#r4:idli|r5:thali|#SY#r6:vada pav|"
start = 14
pos = data.find(b"#SY#", start)
print("byte 14 is inside:", data[12:20])
print("first sync marker after 14 is at", pos, "-> start reading at", pos + 4, ":", data[pos + 4:pos + 11])
''', notes={3: 'Seek :: The same idea as skipping to the next newline in a text split (Lesson 8.2).'},
         tryit='A gzip\'d CSV has no such markers inside the compressed stream, which is why it can\'t be split (Lesson 10.3).'),
    dict(level='a', tag='Design · evolution', title='Which schema changes are safe?',
         problem='<p>Version 1 of the order schema is in use. The team proposes four changes. For each, can <b>new readers read old files</b> (backward compatible)?</p>',
         inp='4 proposed changes',
         approach=['Adding a field: old files lack it, so the reader needs a default.',
                   'Removing a field: the reader just skips it in old files.',
                   'Changing a type: only promotions like int → long are allowed.'],
         code='''changes = [("add payment, default 'cash'", "add", True), ("add payment, no default", "add", False),
           ("remove time", "remove", None), ("amount int -> string", "type", None)]
for desc, kind, has_default in changes:
    ok = (kind == "add" and has_default) or kind == "remove"
    print(f"{desc:28} backward compatible: {ok}")
''', notes={4: 'Rule :: Avro resolves by name; a missing value is only OK if the reader has a default.'},
         tryit='Removing a field breaks forward compatibility (old readers reading new files) unless the old schema gave that field a default.'),
]

QUIZ = mix([
    dict(q='Why was the uncompressed SequenceFile bigger than the CSV (24.0 MB vs 19.4 MB)?', options=['SequenceFiles store three copies', 'Each record stores its length, the key length and an 8-byte key', 'It stores the schema in every record', 'Hadoop pads records to 64 bytes'], answer=1,
         why='About 9 extra bytes per order; compression is where SequenceFile wins.'),
    dict(q='Which compression type made our SequenceFile largest?', options=['NONE', 'RECORD', 'BLOCK', 'All were equal'], answer=1,
         why='27.9 MB: a 30-byte value compressed alone doesn\'t shrink, and each pays overhead.'),
    dict(q='What makes SequenceFile and Avro files splittable even when compressed?', options=['They are always stored uncompressed', 'Sync markers between blocks of records', 'The NameNode indexes every record', 'They use bzip2'], answer=1,
         why='A reader starting mid-file scans to the next sync marker.'),
    dict(q='Where does an Avro data file keep its schema?', options=['In a separate .avsc file only', 'As JSON in the file header', 'In every record', 'In the NameNode'], answer=1,
         why='avro-tools getmeta showed avro.schema and avro.codec.'),
    dict(q='Reading an old Avro file with a new schema that adds a field WITH a default gives…', options=['An AvroTypeException', 'Each record with the default value in the new field', 'An empty field name', 'The job skips those records'], answer=1,
         why='Real: "payment":"cash" on every old record.'),
    dict(q='How does Avro match the writer\'s fields to the reader\'s?', options=['By position', 'By field name (and aliases)', 'By type only', 'It doesn\'t; schemas must be identical'], answer=1,
         why='That is what makes adding, removing and reordering fields possible.'),
    dict(q='Which command prints a SequenceFile or Avro file as readable text?', options=['hdfs dfs -cat', 'hdfs dfs -text', 'hdfs dfs -tail', 'hdfs fsck'], answer=1,
         why='-cat shows raw bytes; -text detects the format and decodes it.'),
    dict(q='For which job are SequenceFiles the most natural choice?', options=['Data shared with a Python team', 'Intermediate data between two chained MapReduce jobs', 'Kafka messages with a schema registry', 'Ad-hoc reading in a text editor'], answer=1,
         why='Binary Writables, no parsing, splittable, but Java-centric.'),
])

REVISION = [
    '<b>Text/CSV</b>: readable, no schema, splittable only uncompressed (or bzip2). Ours: 19.4 MB.',
    '<b>SequenceFile</b>: binary key-value Writables, class names + codec in the header, sync markers (~every 100 KB). NONE 24.0 MB, RECORD 27.9 MB, <b>BLOCK 4.7 MB</b>.',
    '<b>Avro</b>: JSON schema in the header, compact binary (zig-zag varints), sync markers between blocks, many languages. null 16.6 MB, snappy 7.8 MB, deflate 4.8 MB.',
    'Schema evolution: fields matched by <b>name</b>; new fields need a <b>default</b>; renames use <b>aliases</b>; int → long promotion allowed.',
    'Without a default: “AvroTypeException: … missing required field payment”.',
    '<code>hdfs dfs -text</code> decodes SequenceFile and Avro; <code>avro-tools getmeta / tojson</code> inspect Avro.',
    'Hadoop ships avro core, not <b>avro-mapred</b>: add it with <code>-libjars</code> and <code>HADOOP_CLASSPATH</code>.',
]
FAQ = [
    ('What is a SequenceFile in Hadoop?', 'A flat binary file of key-value pairs, where the keys and values are Writables. Its header names the key and value classes and the compression codec. Records can be stored uncompressed, record-compressed or block-compressed, and sync markers written every 100 KB or so let readers start in the middle, so the file stays splittable even when compressed. It is commonly used for intermediate MapReduce data and for packing many small files into one.'),
    ('What is Apache Avro and why is it used with Hadoop?', 'Avro is a language-neutral data serialization system. An Avro data file stores its schema as JSON in the header, followed by compact binary records in blocks separated by sync markers, optionally compressed with deflate, snappy, zstandard or others. It is splittable, readable from many languages, and supports schema evolution, which is why it is popular for data ingestion, Kafka messages and the raw zone of data lakes.'),
    ('What is schema evolution in Avro?', 'Reading data written with one schema (the writer&#39;s schema, stored in the file) using a different, compatible schema (the reader&#39;s schema). Avro matches fields by name: fields only in the reader&#39;s schema are filled from their default values, fields only in the writer&#39;s schema are ignored, aliases handle renames and some types can be promoted (int to long, float to double). Adding a field without a default breaks backward compatibility.'),
    ('What is the difference between SequenceFile and Avro?', 'Both are binary, row-oriented, compressible and splittable. A SequenceFile stores Java Writable key-value pairs and records only the class names, so it is mainly used inside Hadoop. Avro stores a full language-neutral schema with named, typed fields, can be read from many languages and supports schema evolution, so it suits data exchanged between systems and teams.'),
    ('Which compression type should I use for SequenceFiles?', 'BLOCK compression, which compresses many records together. RECORD compression compresses each value separately, which barely helps (or even hurts) for small values: in our lab a 5 lakh order SequenceFile was 24.0 MB uncompressed, 27.9 MB with RECORD and 4.7 MB with BLOCK compression.'),
]

PRACTICE_INTRO = 'Format exercises using the byte counts from our lab.'
PROBLEMS = [
    dict(level='easy', title='Bytes per order', stmt='Compute the average bytes per order for each format from the lab sizes.', inp='7 sizes for 500,000 orders',
         code='''sizes = {"text": 19418699, "seq_none": 24034722, "seq_record": 27878984, "seq_block": 4683378,
         "avro_null": 16558165, "avro_deflate": 4793471, "avro_snappy": 7791915}
for k, v in sizes.items():
    print(f"{k:13} {v / 500_000:5.1f} B/order")
''', explain='From 55.8 bytes (RECORD) down to 9.4 (BLOCK): a 6× spread for the same data.'),
    dict(level='easy', title='SequenceFile overhead', stmt='How many extra bytes per order did the uncompressed SequenceFile add over the CSV?', inp='24,034,722 vs 19,418,699',
         code='''print((24034722 - 19418699) / 500_000, "bytes per order")
''', explain='About 9.2: record length 4 + key length 4 + 8-byte key + value length 1, minus the order_id text, comma and newline.'),
    dict(level='easy', title='Compression ratio', stmt='What percentage of the CSV size is each compressed format?', inp='seq_block, avro_deflate, avro_snappy',
         code='''csv = 19418699
for name, s in [("seq_block", 4683378), ("avro_deflate", 4793471), ("avro_snappy", 7791915)]:
    print(f"{name:13} {100 * s / csv:5.1f}% of the CSV")
''', explain='About 24%, 25% and 40%: deflate compresses more, snappy is faster (Lesson 10.3).'),
    dict(level='medium', title='Decode a varint', stmt='Decode the Avro zig-zag varint bytes d8 04 back to a number.', inp='bytes 0xd8 0x04',
         code='''data = bytes([0xD8, 0x04])
n, shift = 0, 0
for b in data:
    n |= (b & 0x7F) << shift
    shift += 7
    if b < 0x80:
        break
print("zigzag value", n, "-> number", (n >> 1) ^ -(n & 1))
''', explain='600 after the 7-bit groups are joined, then un-zig-zag: 300.'),
    dict(level='medium', title='Schema resolver', stmt='Write a resolver that also skips fields present in the file but not in the reader\'s schema.', inp='writer has an extra "counter" field',
         code='''row = {"order_id": 7, "item": "chai", "amount": 15, "counter": "A"}
reader = [("order_id", None), ("item", None), ("amount", None), ("payment", "cash")]
out = {n: row.get(n, d) for n, d in reader if n in row or d is not None}
print(out)
''', explain='"counter" is ignored, "payment" filled from its default: both directions of evolution in one line.'),
    dict(level='medium', title='Small values don\'t compress', stmt='Compress one 30-byte value with zlib. Is the result smaller?', inp='"S1413,2026-09-14 15:30,dosa,45"',
         code='''import zlib
v = b"S1413,2026-09-14 15:30,dosa,45"
print(len(v), "->", len(zlib.compress(v)))
''', explain='30 → 38 bytes: compression needs repetition, and one short value has none. That is RECORD compression\'s problem.'),
    dict(level='business', title='Which format for the landing zone?', stmt='Partners send 20 crore events a day; three teams (Java, Python, Spark SQL) read them, and fields get added every quarter. Compare yearly raw storage (×3 replicas) as CSV vs Avro deflate using our bytes per order, and pick a format.', inp='38.8 vs 9.6 B/record',
         code='''per_year = 200_000_000 * 365
for name, b in [("CSV", 38.8), ("Avro deflate", 9.6)]:
    print(f"{name:12} {per_year * b * 3 / 1024**4:5.1f} TB per year")
''', explain='About 7.7 TB vs 1.9 TB a year, and Avro\'s schema with defaults lets the quarterly new fields arrive without breaking the Python and Java readers.'),
    dict(level='advanced', title='A tiny container file', stmt='Write records into blocks of 3 with a sync marker before each block, then read only the block that starts after byte 20.', inp='7 records',
         code='''SYNC = b"\\xff\\xfe"
recs = [f"r{i}".encode() for i in range(1, 8)]
f = b""
for i in range(0, len(recs), 3):
    f += SYNC + b",".join(recs[i:i + 3]) + b";"
start = f.find(SYNC, 20)
print(f)
print("split from byte 20 starts at", start, "->", f[start + 2:].split(b";")[0])
''', explain='The reader skips the partial block and starts at the next marker; the reader of the previous split finishes that block. This is how Avro and SequenceFile splits work.'),
]

SCN_INTRO = 'File format questions are common for data engineers: expect comparisons, schema evolution and “which format would you choose”.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Formats · basics</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“Compare Text, SequenceFile and Avro”</h4>
      <p class="scn__situation">A standard question in Hadoop interviews.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> schema, size, splittability, languages.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Text: readable, no schema, large; splittable only uncompressed or bzip2.</li>
          <li>SequenceFile: binary Writable key-value pairs, class names in the header, splittable with sync markers, BLOCK compression; Java-centric.</li>
          <li>Avro: JSON schema in the file, compact binary, splittable, any language, schema evolution. In my lab: CSV 19.4 MB, SequenceFile BLOCK 4.7 MB, Avro deflate 4.8 MB.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Avro · evolution</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>A producer added a field and consumers started failing</h4>
      <p class="scn__situation">After a release, Spark jobs reading old Avro files fail with “missing required field”.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> reader vs writer schema and defaults.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>The new reader schema has a field that old files lack and it has no default, so resolution fails.</li>
          <li>Fix: add a default (or make it a union with null, default null) and redeploy; old and new files then both read.</li>
          <li>Prevent it: a schema registry with BACKWARD compatibility checks in CI before producers can publish.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Performance · storage</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>“We compressed our SequenceFiles and they got bigger”</h4>
      <p class="scn__situation">A team switched on compression for an intermediate dataset of short records.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> RECORD vs BLOCK compression.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>They probably used RECORD compression: each small value is compressed alone, with no repetition to exploit and per-value overhead.</li>
          <li>Switch to BLOCK compression (mapreduce.output.fileoutputformat.compress.type=BLOCK), which compresses many records together.</li>
          <li>Our measurement: 24.0 MB uncompressed, 27.9 MB RECORD, 4.7 MB BLOCK.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Design · choice</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Choose formats for a new data lake</h4>
      <p class="scn__situation">Events arrive from Kafka; analysts run SQL over a few columns of billions of rows.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> row vs columnar by workload.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Raw/landing zone: Avro, which is fast to append, keeps whole records and schema history, and matches the Kafka schemas.</li>
          <li>Curated tables: Parquet or ORC, since columnar storage reads only the needed columns and compresses better.</li>
          <li>A scheduled job converts and compacts raw Avro into partitioned columnar tables.</li>
        </ul>
      </div></details>
    </article>
'''
