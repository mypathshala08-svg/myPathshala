import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()

META = dict(
    module='09-mapreduce-in-depth', lesson='03-custom-writable-types', n='9.3',
    module_label='Module 9 · MapReduce in depth',
    title='Custom Writable types',
    desc='Hadoop Writable and WritableComparable explained with a real job on Hadoop 3.5.0: a composite (student, day) key and an (orders, total, max) value over 5 lakh orders. The naive Writable (writeUTF + int/long) produced 17.5 MB of map output, more than the Text version (12.5 MB); a compact Writable with VInt/VLong produced 4.1 MB, 4.3× smaller, with identical 59,946 output rows. write/readFields order, compareTo, hashCode, the no-arg constructor (NoSuchMethodException on the cluster), object reuse, built-in types and sizes, RawComparator, Writable vs Serializable. Python byte-size simulation, quiz and interview scenarios.',
    og_desc='A custom Writable made the shuffle 40% bigger, until we encoded it properly: 35 → 8 bytes per record on a real cluster.',
    minutes=26, level='Intermediate',
    lead='Every key and value in MapReduce is turned into bytes, sorted, copied and turned back into objects. Writable is how you control those bytes. This lesson builds a composite key and a value type, measures three encodings of the same record on a real cluster, and shows the one mistake that compiles fine and fails on every task.',
    chips=['35 vs 25 vs 8 bytes, measured', 'Real NoSuchMethodException', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Count the bytes of one record, three ways',
    intro='<p>Python\'s <code>struct</code> module can write the same bytes as Java\'s <code>DataOutput</code>. This code serializes one map output record the way each of our three jobs did, and also implements Hadoop\'s VInt encoding (<code>WritableUtils.writeVLong</code>).</p>',
    code='''import struct

def write_utf(s):                      # DataOutput.writeUTF: 2-byte length + UTF-8 bytes
    b = s.encode()
    return struct.pack(">H", len(b)) + b

def write_vint(i):                     # WritableUtils.writeVInt / writeVLong (for i >= 0)
    if -112 <= i <= 127:
        return bytes([i & 0xFF])
    data = i.to_bytes((i.bit_length() + 7) // 8, "big")
    return bytes([(-112 - len(data)) & 0xFF]) + data

def text(s):                           # Text: VInt length + UTF-8 bytes
    b = s.encode()
    return write_vint(len(b)) + b

student, day, amount = "S1413", "2026-09-10", 45
naive = write_utf(student) + write_utf(day) + struct.pack(">iqi", 1, amount, amount)
as_text = text(student + "\\t" + day) + text(f"1,{amount},{amount}")
compact = write_vint(1413) + write_vint(253) + write_vint(1) + write_vint(amount) + write_vint(amount)

for name, b in [("Writable (UTF)", naive), ("Text", as_text), ("Writable (VInt)", compact)]:
    print(f"{name:16} {len(b):2} bytes  {b.hex(' ')}")
''',
    anno=[
        ('    return struct.pack(">H", len(b)) + b', 'writeUTF always spends 2 bytes on the length: "2026-09-10" costs 12 bytes.'),
        ('naive = write_utf(student) + write_utf(day) + struct.pack(">iqi", 1, amount, amount)', '">iqi" = int, long, int, big-endian: 4 + 8 + 4 = 16 bytes, mostly zeros.'),
        ('    return bytes([(-112 - len(data)) & 0xFF]) + data', 'One marker byte saying how many bytes follow, then only those bytes: 1413 → 8e 05 85.'),
    ],
    tasks=[
        dict(label='1 · Three encodings', hint='Press <b>Run</b>. Check the sizes against the lab: 17,500,000 / 12,500,000 / 4,068,724 bytes for 5 lakh records.', code=None),
        dict(label='2 · Bytes for the whole job', hint='<b>Predict first:</b> multiply the naive and Text sizes by 5 lakh. Do you get the lab\'s Map output bytes exactly?',
             code='''records = 500_000
for name, per_record, lab in [("Writable (UTF)", 35, 17_500_000), ("Text", 25, 12_500_000)]:
    print(f"{name:15} {per_record * records:>12,}  lab: {lab:>12,}  match: {per_record * records == lab}")
print("compact average:", round(4_068_724 / records, 3), "bytes per record")
'''),
        dict(label='3 · VInt sizes', hint='How many bytes does a VInt need for 1, 127, 128, 255, 256, 2000 and 1 lakh? Where do the student numbers and days of September fall?',
             code='''def vint_len(i):
    if -112 <= i <= 127:
        return 1
    return 1 + (i.bit_length() + 7) // 8

for n in [1, 127, 128, 255, 256, 2000, 100_000]:
    print(f"{n:>7} -> {vint_len(n)} byte(s)")
print("September days of year:", 244, "to", 273)
'''),
        dict(label='4 · Sort by a composite key', hint='Keys sort by student, then day, like <code>compareTo</code>. Python tuples compare the same way. Sort these keys.',
             code='''keys = [("S0002", "2026-09-03"), ("S0001", "2026-09-02"), ("S0002", "2026-09-01"),
        ("S0001", "2026-09-10"), ("S0001", "2026-09-01")]
for k in sorted(keys):                 # tuple order = field by field, like compareTo
    print(*k)
'''),
        dict(label='5 · Spot the error', hint='write() and readFields() disagree: one writes a long, the other reads an int. Make readFields match.',
             code='''import struct, io
def write(orders, total, mx):
    return struct.pack(">iqi", orders, total, mx)
def read_fields(b):
    f = io.BytesIO(b)
    orders, total, mx = struct.unpack(">iii", f.read(12))
    rest = f.read()
    if rest:
        raise ValueError(f"{len(rest)} bytes left over: the next record would start in the wrong place")
    return orders, total, mx
print(read_fields(write(1, 45, 45)))
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: three encodings of the same job',
    intro='<p>Use the Module 8 lab cluster (Lesson 8.1) and <code>student_orders.csv</code> from <code>make_student_orders.py</code> (Lesson 9.1). Copy the three Java files and <code>writable_lab.sh</code> into <code>/tmp/mr9</code> in the namenode container, compile them into <code>mr9.jar</code>, and run the script. It takes about 2 minutes.</p>',
    items=[
        dict(title='Composite key and value with writeUTF and fixed-size numbers', file='StudentDay.java',
             cmd=rd('java/StudentDay.java') + '\n// Inside the namenode container, in /tmp/mr9:\n//   mkdir -p classes && javac -cp $(hadoop classpath) -d classes *.java && jar cf mr9.jar -C classes .\n//   hadoop jar mr9.jar StudentDay /user/hadoop/data/student_orders.csv /out/StudentDay',
             output='Map output records=500000\nMap output bytes=17500000\nMap output materialized bytes=5604593\nCombine output records=151475\nReduce output records=59946',
             note='Real counters from the run in the next item. 35 bytes per record.'),
        dict(title='The same job with Text', file='StudentDayText.java',
             cmd=rd('java/StudentDayText.java'),
             output='Map output records=500000\nMap output bytes=12500000\nMap output materialized bytes=4132541\nCombine output records=151475\nReduce output records=59946',
             note='25 bytes per record: the strings are short and every number here has two digits.'),
        dict(title='Compact encoding with VInt and VLong', file='StudentDayCompact.java',
             cmd=rd('java/StudentDayCompact.java'),
             output='Map output records=500000\nMap output bytes=4068724\nMap output materialized bytes=1601326\nCombine output records=151475\nReduce output records=59946',
             note='About 8 bytes per record. toString() prints the student and date back in their usual form.'),
        dict(title='Run all three, compare, then break the constructor', file='writable_lab.sh',
             cmd=rd('writable_lab.sh') + '\n# Inside the namenode container:  bash /tmp/mr9/writable_lab.sh',
             output=rd('tx93.txt').strip(),
             note='Real output. The output lines for S0001 appear twice because the first rows of the file are S0001\'s. The constructor test is done with sed on a copy, so StudentDay.java is unchanged.'),
    ],
)

TRACE = dict(
    heading='write() then readFields() into a reused object',
    intro='<p>Follow one record through <code>write</code> and <code>readFields</code>. Notice that reading fills an existing object instead of creating a new one.</p>',
    code='''import struct, io
class Spend:
    def __init__(self):
        self.orders, self.total, self.max = 0, 0, 0
buf = struct.pack(">iqi", 1, 45, 45) + struct.pack(">iqi", 2, 65, 45)
reused = Spend()
f = io.BytesIO(buf)
for _ in range(2):
    reused.orders, reused.total, reused.max = struct.unpack(">iqi", f.read(16))
    print(id(reused) % 1000, reused.orders, reused.total, reused.max)
''',
    notes={5: 'Bytes :: Two serialized values, 16 bytes each, one after the other.',
           9: 'readFields :: The same object is refilled for every record, as Hadoop does.',
           10: 'Same id :: One object, two different contents.'},
)

WORKED_INTRO = 'Three design problems: sizing a record, choosing an encoding, and a key that partitions wrongly.'
EXAMPLES = [
    dict(level='b', tag='Sizing · bytes', title='How big is this record?',
         problem='<p>A key holds a city name written with <code>writeUTF</code> ("Mumbai") and a year as <code>writeInt</code>. The value is a <code>writeLong</code> total. How many bytes per record, and how many MB for 2 crore records?</p>',
         inp='writeUTF("Mumbai") + int + long',
         approach=['writeUTF = 2 + number of bytes.',
                   'int = 4, long = 8.',
                   'Multiply by the number of records.'],
         code='''per = (2 + len("Mumbai")) + 4 + 8
print(per, "bytes per record,", round(per * 20_000_000 / 1024**2), "MB")
''', notes={1: 'Fixed costs :: The 2-byte length prefix is paid on every record.'},
         tryit='Store the city as a small code number with writeVInt instead: about 1 + 3 + 3 bytes.'),
    dict(level='i', tag='Design · encoding', title='Pick an encoding for a phone-number key',
         problem='<p>A telecom job keys records by a 10-digit mobile number. Compare storing it as Text, as <code>writeLong</code>, and as a VLong.</p>',
         inp='9876543210',
         approach=['Text: VInt length + 10 characters.',
                   'writeLong: always 8 bytes.',
                   'VLong: marker + the bytes the number needs.'],
         code='''n = 9876543210
text = 1 + len(str(n))
fixed = 8
vlong = 1 + (n.bit_length() + 7) // 8
print(f"Text {text} · long {fixed} · VLong {vlong} bytes")
''', notes={4: 'VLong :: 34 bits need 5 bytes plus the marker.'},
         tryit='The difference per record is small; over a billion call records it is several GB of shuffle.'),
    dict(level='a', tag='Correctness · partitioning', title='A key whose hashCode breaks the job',
         problem='<p>A developer writes a composite key but forgets to override <code>hashCode()</code>, so Java\'s default (based on the object\'s identity) is used. Equal keys from two map tasks get different hash codes. What happens to the reducers\' output?</p>',
         inp='key (S0001, 2026-09-01) from two maps',
         approach=['HashPartitioner uses hashCode() % reducers.',
                   'Identity hash codes differ between objects and JVMs.',
                   'Simulate two maps sending the same key.'],
         code='''import random, zlib
reducers = 4
same_key = ("S0001", "2026-09-01")
for map_task in ["map 0", "map 1"]:
    identity_hash = random.Random(map_task).getrandbits(31)    # different per object/JVM
    print(map_task, "sends", same_key, "to reducer", identity_hash % reducers)
content_hash = zlib.crc32("|".join(same_key).encode())                 # same fields, same number
print("hash from the fields -> reducer", content_hash % reducers, "for both maps")
''', notes={5: 'Identity hash :: Not based on the fields, so equal keys can land on different reducers.'},
         tryit='The result: one student-day split across two reducers, two output rows for one key, and totals that look half as big.'),
]

QUIZ = mix([
    dict(q='Which two methods does every Writable implement?', options=['serialize() and deserialize()', 'write(DataOutput) and readFields(DataInput)', 'toBytes() and fromBytes()', 'map() and reduce()'], answer=1,
         why='They write the fields and read them back, in the same order.'),
    dict(q='What must a map output KEY type implement?', options=['Writable only', 'WritableComparable, because keys are sorted in the shuffle', 'Serializable', 'Comparable only'], answer=1,
         why='compareTo() defines the sort order of keys.'),
    dict(q='Which method decides which reducer a key goes to with the default partitioner?', options=['compareTo()', 'hashCode()', 'toString()', 'readFields()'], answer=1,
         why='HashPartitioner: (hashCode() & Integer.MAX_VALUE) % reducers.'),
    dict(q='What happened when the key had no public no-argument constructor?', options=['It did not compile', 'NoSuchMethodException at runtime and the job failed', 'Hadoop used the other constructor', 'Output keys were null'], answer=1,
         why='Hadoop creates instances by reflection with new Key().'),
    dict(q='Why was the first custom Writable bigger than the Text version?', options=['Writables are always bigger', 'writeUTF adds 2 bytes per string and writeInt/writeLong use 4/8 bytes even for small numbers', 'It used compression', 'The combiner did not run'], answer=1,
         why='35 bytes vs 25 bytes per record in our lab.'),
    dict(q='How many bytes does a VInt use for the number 100?', options=['4', '1', '2', '5'], answer=1,
         why='Values from -112 to 127 fit in a single byte.'),
    dict(q='Why must readFields() set every field?', options=['For speed only', 'Hadoop reuses the same object, so an unset field keeps the previous record\'s value', 'To avoid compile errors', 'Because toString() needs it'], answer=1,
         why='One object is refilled for every record.'),
    dict(q='What does a RawComparator do?', options=['Compares keys as bytes without deserializing them', 'Compresses keys', 'Partitions keys', 'Sorts reducer output files'], answer=0,
         why='It makes the sort faster; Text and IntWritable have one.'),
])

REVISION = [
    '<b>Writable</b>: <code>write(DataOutput)</code> + <code>readFields(DataInput)</code>, same fields, same order.',
    'Keys: <b>WritableComparable</b> (<code>compareTo</code> = sort order) and a consistent <code>hashCode</code>/<code>equals</code> (partitioning).',
    'Public <b>no-arg constructor</b> required (reflection); <code>readFields</code> must overwrite every field (objects are reused).',
    'Sizes: writeUTF 2 + bytes; int 4; long 8; VInt 1–5, VLong 1–9; Text = VInt length + bytes; NullWritable 0.',
    'Lab: 35 B (writeUTF + fixed numbers) vs 25 B (Text) vs ≈8 B (VInt) per record; 17.5 / 12.5 / 4.1 MB for 5 lakh records; same 59,946 rows.',
    '<code>toString()</code> controls how the type appears in TextOutputFormat output.',
    'Faster sorting: a RawComparator compares serialized bytes. Avro/Parquet for data files shared with other tools.',
]
FAQ = [
    ('What is a Writable in Hadoop?', 'Writable is Hadoop\'s serialization interface. A class implements write(DataOutput) to write its fields as bytes and readFields(DataInput) to read them back. Hadoop uses Writables for all MapReduce keys and values and in SequenceFiles. Common built-in Writables are Text, IntWritable, LongWritable, DoubleWritable and NullWritable.'),
    ('What is the difference between Writable and WritableComparable?', 'Writable only serializes and deserializes. WritableComparable also implements Comparable, so objects can be sorted. MapReduce sorts map output by key, so every key type must be WritableComparable; value types only need Writable.'),
    ('Why does Hadoop not use Java serialization?', 'Java serialization writes class information and object metadata with every object and creates a new object when reading, which is slow and large for billions of small records. Writables write only the field values, can be reused for every record, and many can be compared directly in serialized form with a RawComparator.'),
    ('How do you create a custom key in MapReduce?', 'Write a class that implements WritableComparable&lt;YourKey&gt;, with a public no-argument constructor, write() and readFields() handling the same fields in the same order, compareTo() defining the sort order, and hashCode() and equals() based on the same fields so the partitioner sends equal keys to the same reducer. Override toString() for readable text output.'),
    ('Why does my custom Writable job fail with NoSuchMethodException &lt;init&gt;()?', 'Hadoop creates key and value objects by reflection with the no-argument constructor. If your class only has a constructor with parameters, Java does not generate the default one, and tasks fail at runtime with NoSuchMethodException: YourClass.&lt;init&gt;(). Add a public no-argument constructor (and make nested classes static).'),
]

PRACTICE_INTRO = 'Writable exercises using the sizes and counters measured in the lab.'
PROBLEMS = [
    dict(level='easy', title='Bytes per record', stmt='Compute bytes per record for the three jobs from Map output bytes and Map output records.', inp='17,500,000 · 12,500,000 · 4,068,724 / 500,000',
         code='''for name, b in [("UTF", 17_500_000), ("Text", 12_500_000), ("VInt", 4_068_724)]:
    print(name, round(b / 500_000, 2))
''', explain='35, 25 and 8.14 bytes.'),
    dict(level='easy', title='How much smaller?', stmt='How many times smaller is the compact Writable than the first Writable, and than Text?', inp='three byte counts',
         code='''print(round(17_500_000 / 4_068_724, 1), round(12_500_000 / 4_068_724, 1))
''', explain='4.3× smaller than the naive Writable and 3.1× smaller than Text.'),
    dict(level='easy', title='writeUTF cost', stmt='How many bytes does writeUTF use for "S0001" and for "2026-09-01"?', inp='two strings',
         code='''for s in ["S0001", "2026-09-01"]:
    print(s, 2 + len(s.encode()))
''', explain='7 and 12: 19 bytes of key in the naive version.'),
    dict(level='medium', title='Materialized vs raw', stmt='Map output materialized bytes are what is actually written to disk for the shuffle (with partition framing and checksums). Compute the ratio materialized / raw for each job. Which shrinks most?', inp='materialized and raw bytes',
         code='''jobs = {"UTF": (5_604_593, 17_500_000), "Text": (4_132_541, 12_500_000), "VInt": (1_601_326, 4_068_724)}
for k, (m, r) in jobs.items():
    print(k, round(m / r, 2))
''', explain='About 0.32, 0.33 and 0.39: the combiner shrank all three record counts from 500,000 to 151,475 before writing; the compact records had less redundancy to begin with.'),
    dict(level='medium', title='VInt encoder', stmt='Write Hadoop\'s VInt encoding for non-negative numbers and print the hex for 45, 253, 1413 and 2000.', inp='4 numbers',
         code='''def vint(i):
    if i <= 127:
        return bytes([i])
    data = i.to_bytes((i.bit_length() + 7) // 8, "big")
    return bytes([(-112 - len(data)) & 0xFF]) + data
for n in [45, 253, 1413, 2000]:
    print(n, vint(n).hex(" "))
''', explain='2d · 8f fd · 8e 05 85 · 8e 07 d0. The marker byte 8f means one data byte follows, 8e means two.'),
    dict(level='medium', title='Composite key order', stmt='Sort these (student, day) keys the way compareTo does, and say which reducer call comes first.', inp='4 keys',
         code='''keys = [("S0010", "2026-09-01"), ("S0002", "2026-09-30"), ("S0002", "2026-09-01"), ("S0100", "2026-09-05")]
print(sorted(keys))
''', explain='S0002 first (both days in order), then S0010, then S0100: string order works because the IDs are zero-padded.'),
    dict(level='business', title='Shuffle savings per year', stmt='A nightly job shuffles 800 GB with Text records. A compact Writable would cut the bytes by 3×. The network and disk cost is ₹2 per GB shuffled (illustrative). What is saved in a year?', inp='800 GB/night · 3× smaller · ₹2/GB',
         code='''saved_gb = 800 - 800 / 3
print(f"Rs {saved_gb * 2 * 365:,.0f} per year")
''', explain='About ₹3.9 lakh a year, plus faster jobs. Worth a day of a developer\'s time; not worth it for a 1 GB job.'),
    dict(level='advanced', title='Zero-padding pitfall', stmt='If student IDs were not zero-padded (S1, S2, S10), a String compareTo sorts them as text. Show the order, then fix it by comparing the numbers.', inp='S1, S2, S10, S9',
         code='''ids = ["S1", "S2", "S10", "S9"]
print("as text:  ", sorted(ids))
print("as number:", sorted(ids, key=lambda s: int(s[1:])))
''', explain='Text order gives S1, S10, S2, S9. Storing the number (as the compact key does) sorts correctly and is smaller.'),
]

SCN_INTRO = 'Writable questions test whether you understand what really travels between map and reduce.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Concepts · basics</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“Why does Hadoop have its own IntWritable instead of using Integer?”</h4>
      <p class="scn__situation">A common opener in Hadoop interviews.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> serialization basics.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Keys and values are sent between JVMs and written to disk, so they must be serialized.</li>
          <li>Writable writes only the field bytes (4 for an int), with no class metadata, and objects are reused for every record.</li>
          <li>Keys are WritableComparable so they can be sorted, often byte by byte with a RawComparator.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Debugging · runtime</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>The job runs in your IDE tests but fails on the cluster with NoSuchMethodException</h4>
      <p class="scn__situation">The message ends with MyKey.&lt;init&gt;().</p>
      <p class="scn__look"><b>The interviewer is checking:</b> reflection and constructors.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Hadoop instantiates keys and values by reflection with a no-argument constructor.</li>
          <li>Adding a constructor with parameters removed Java's default one; add a public no-arg constructor.</li>
          <li>For nested classes, make them static, or reflection cannot create them either.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Performance · shuffle</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>A job with a custom Writable shuffles more data than the old Text version</h4>
      <p class="scn__situation">The team expected the opposite.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> encoding choices.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Compare Map output bytes / Map output records for both versions to get bytes per record.</li>
          <li>Look at write(): writeUTF adds 2 bytes per string, writeInt/writeLong use 4/8 bytes even for tiny numbers.</li>
          <li>Encode IDs and dates as numbers, use VInt/VLong, drop fields the reducer doesn't need; in our lab 35 → 8 bytes per record.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Correctness · keys</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Output has duplicate keys across part files</h4>
      <p class="scn__situation">The same (customer, day) appears in part-r-00001 and part-r-00003 with different totals.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> hashCode and equals contracts.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>The key's hashCode() is not based on its fields (or is inconsistent with equals/compareTo), so equal keys go to different reducers.</li>
          <li>Implement hashCode() from the same fields compareTo() uses; avoid Object.hashCode() and anything JVM-specific.</li>
          <li>Rerun the job: each key then appears exactly once.</li>
        </ul>
      </div></details>
    </article>
'''
