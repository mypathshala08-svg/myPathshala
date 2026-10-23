import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()
TX = rd('tx102.txt')
TX_WRITE, TX_READ = TX.split('== read:')
TX_READ = '== read:' + TX_READ

META = dict(
    module='10-data-formats', lesson='02-parquet-and-orc', n='10.2',
    module_label='Module 10 · Data formats and compression',
    title='Parquet and ORC',
    desc='Columnar file formats measured on a real Hadoop 3.5.0 cluster: 5 lakh orders written by MapReduce as Parquet (uncompressed 7.4 MB, Snappy 4.4 MB, ZSTD 2.8 MB) and ORC (ZLIB 3.3 MB, ZSTD 2.9 MB) vs a 19.4 MB CSV. Inside an ORC file with orc-tools (576 bytes for 2 lakh order ids), projection (192,526 bytes read instead of 19.4 MB, same answer), predicate pushdown with row-group statistics (1 of 10 row groups when sorted), Parquet row groups, column chunks and pages, ORC stripes, encodings, Parquet vs ORC, Python simulations, quiz and interview scenarios.',
    og_desc='Same job, same answer, 100× fewer bytes read: Parquet and ORC measured on a real Hadoop cluster.',
    minutes=30, level='Intermediate',
    lead='Parquet and ORC store a table column by column. A query then reads only the columns it needs, repeated values shrink to almost nothing, and per-block statistics let readers skip data that cannot match. This lesson writes both formats from MapReduce, opens them up, and measures what projection and predicate pushdown save.',
    chips=['192 KB read instead of 19.4 MB', 'Inside real Parquet and ORC files', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Store the same rows by row and by column',
    intro='<p>This model stores a few orders row by row (like CSV) and column by column with the two tricks columnar formats use: a <b>dictionary</b> for repeated strings and <b>run-length encoding</b> for repeats in a row. It counts bytes so you can compare.</p>',
    code='''rows = [(1, "S0001", "chai", 15), (2, "S0001", "chai", 15), (3, "S0002", "chai", 15),
        (4, "S0002", "dosa", 45), (5, "S0003", "chai", 15), (6, "S0003", "chai", 15),
        (7, "S0003", "poha", 25), (8, "S0004", "chai", 15)]

row_bytes = sum(len(",".join(map(str, r))) + 1 for r in rows)          # CSV-style

def dictionary(col):                       # each distinct value once + a small code per row
    d = {v: i for i, v in enumerate(dict.fromkeys(col))}
    return sum(len(str(v)) for v in d) + len(col), [d[v] for v in col]   # 1 byte per code

def rle(codes):                            # (value, run length) pairs
    runs = []
    for c in codes:
        if runs and runs[-1][0] == c: runs[-1][1] += 1
        else: runs.append([c, 1])
    return runs

col_bytes = 0
for name, i in [("order_id", 0), ("student", 1), ("item", 2), ("amount", 3)]:
    col = [r[i] for r in rows]
    if name == "order_id":                  # delta: start + step, like ORC's RLE v2
        size = 2
    else:
        dict_size, codes = dictionary(col)
        size = dict_size - len(col) + 2 * len(rle(codes))
    col_bytes += size
    print(f"{name:9} {size:3} bytes")
print(f"row layout {row_bytes} bytes, column layout {col_bytes} bytes")
''',
    anno=[
        ('def dictionary(col):                       # each distinct value once + a small code per row', 'Our real item column has only 8 distinct values: ORC wrote DICTIONARY_V2[8] and stored 2 lakh items in 92,796 bytes.'),
        ('        size = 2', 'Sequential ids are “start at 1, add 1”: ORC stored 217,602 order ids in 576 bytes.'),
        ('        size = dict_size - len(col) + 2 * len(rle(codes))', 'Runs of the same code collapse into one (value, count) pair.'),
    ],
    tasks=[
        dict(label='1 · Row vs column', hint='Press <b>Run</b>. Which column shrinks the most, and why?', code=None),
        dict(label='2 · Projection', hint='<b>Predict first:</b> a query needs only the item column. What fraction of a CSV line does it actually use?',
             code='''line = "1,S1413,2026-09-14 15:30,dosa,45\\n"
item = line.split(",")[3]
print(f"line {len(line)} bytes, item {len(item)} bytes: {len(item) / len(line):.0%} of what a row reader reads")
print("lab: Parquet item only read", 192526, "of", 19427239, f"CSV bytes = {192526 / 19427239:.1%}")
'''),
        dict(label='3 · Skip row groups', hint='Each row group has a min and max student. Which ones must be read for S1413? Try the unsorted ranges too.',
             code='''sorted_groups = [("S0001", "S0013"), ("S0013", "S0118"), ("S0118", "S0354"), ("S0354", "S0589"), ("S0589", "S0823"),
                 ("S0823", "S1058"), ("S1058", "S1295"), ("S1295", "S1530"), ("S1530", "S1766"), ("S1766", "S2000")]
unsorted_groups = [("S0001", "S2000")] * 10
for name, groups in [("sorted", sorted_groups), ("unsorted", unsorted_groups)]:
    need = [i for i, (lo, hi) in enumerate(groups) if lo <= "S1413" <= hi]
    print(f"{name:8}: read {len(need)} of {len(groups)} row groups {need}")
'''),
        dict(label='4 · Compression ratios', hint='Compute each file\'s size as a percentage of the CSV, using the real lab sizes.',
             code='''csv = 19418699
sizes = {"avro_deflate": 4793471, "parquet_none": 7428043, "parquet_snappy": 4438970, "parquet_zstd": 2775449,
         "orc_none": 9238947, "orc_zlib": 3252876, "orc_zstd": 2909570}
for name, b in sorted(sizes.items(), key=lambda x: x[1]):
    print(f"{name:15} {b:>10,}  {b / csv:6.1%}")
'''),
        dict(label='5 · Spot the error', hint='This reader asks for a column that is not in the schema. Fix the column name.',
             code='''schema = ["order_id", "student", "time", "item", "amount"]
wanted = ["items"]
print([schema.index(c) for c in wanted])
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: write, inspect and read Parquet and ORC',
    intro='<p>Use the Module 8 lab and the Module 9 dataset (<code>student_orders.csv</code> in HDFS). Hadoop ships Avro but not Parquet or ORC, so first run <code>get_jars.sh</code> inside the namenode container (in <code>/tmp/mr10</code>), then <code>source formats_env.sh</code> before every job: it puts the jars on your client classpath and ships them to the tasks with <code>-libjars</code>. Compile with <code>javac -cp $(hadoop classpath):$HADOOP_CLASSPATH -d classes *.java && jar cf mr10.jar -C classes .</code></p>',
    items=[
        dict(title='Classpath for the format jars', file='formats_env.sh',
             cmd=rd('formats_env.sh') + '\n# In /tmp/mr10 inside the namenode container:\n#   bash get_jars.sh\n#   source formats_env.sh',
             output='(no output: it only sets LIBJARS and HADOOP_CLASSPATH)\n\nWithout the zstd-jni line, our first Parquet ZSTD job failed in every map task:\nError: java.lang.ClassNotFoundException: com.github.luben.zstd.RecyclingBufferPool',
             note='Real error from our first run. zstd-jni ships in share/hadoop/tools/lib, which is not on the task classpath by default.'),
        dict(title='Write Parquet and ORC from MapReduce', file='ToColumnar.java',
             cmd=rd('java/ToColumnar.java') + '\n// Inside the container, after source formats_env.sh:\n//   hadoop jar mr10.jar ToColumnar -libjars $LIBJARS -D col.format=parquet -D col.codec=SNAPPY \\\n//       /user/hadoop/data/student_orders.csv /out/f_parquet_snappy\n//   hadoop jar mr10.jar ToColumnar -libjars $LIBJARS -D col.format=orc -D col.codec=ZLIB \\\n//       /user/hadoop/data/student_orders.csv /out/f_orc_zlib',
             output=TX_WRITE.strip(),
             note='Real output of columnar_lab.sh: the sizes of all six variants (plus the CSV and Avro from Lesson 10.1), then orc-tools meta on one ORC part file.'),
        dict(title='Count items from any format, with projection', file='ItemCountAny.java',
             cmd=rd('java/ItemCountAny.java') + '\n// -D in.format=parquet|orc and -D proj=true|false, e.g.:\n//   hadoop jar mr10.jar ItemCountAny -libjars $LIBJARS -D in.format=parquet -D proj=true /out/f_parquet_snappy /out/r_p1',
             output=TX_READ.strip(),
             note='Real output. Compare “HDFS bytes read”: projection cut Parquet from 4,431,110 to 192,526 bytes. Times barely differ because 19 MB is tiny next to the ~25 s of job start-up.'),
        dict(title='The whole lab', file='columnar_lab.sh',
             cmd=rd('columnar_lab.sh') + '\n# Run inside the namenode container, in /tmp/mr10:  bash columnar_lab.sh',
             output=TX.strip(),
             note='Real output, about 5 minutes. Run Lesson 10.1\'s rowformats_lab.sh first if you want the Avro size line filled in.'),
        dict(title='Inside a Parquet file, and row-group skipping', file='parquet_inside.py',
             cmd=rd('parquet_inside.py') + '\n# On your PC, next to student_orders.csv:\n#   pip install pyarrow\n#   python parquet_inside.py',
             output=rd('tx102b.txt').strip(),
             note='Real output with pyarrow 26. pyarrow guessed the time column as a timestamp, so its statistics print with seconds. The unsorted file must read every row group; sorted by student, only row group 7.'),
    ],
)

TRACE = dict(
    heading='Run-length encoding a column',
    intro='<p>Columnar files store runs of equal values as (value, count). Follow how a sorted item column collapses.</p>',
    code='''col = ["chai", "chai", "chai", "dosa", "dosa", "poha"]
runs = []
for v in col:
    if runs and runs[-1][0] == v:
        runs[-1][1] += 1
    else:
        runs.append([v, 1])
print(runs)
''',
    notes={5: 'Same as before :: The run just gets longer; nothing new is stored.',
           7: 'New value :: A new (value, 1) pair starts.'},
)

WORKED_INTRO = 'Three columnar-format problems: how many bytes a query reads, how sorting changes skipping, and what a format switch saves.'
EXAMPLES = [
    dict(level='b', tag='Projection · bytes', title='How much does a two-column query read?',
         problem='<p>In one ORC part file, the column sizes on disk are order_id 576, student 352,126, time 901,599, item 92,796 and amount 105,756 bytes. A query needs item and amount. How many column bytes does it read, and what share of all columns is that?</p>',
         inp='5 column sizes from orc-tools meta',
         approach=['Add up all column sizes.',
                   'Add up only the columns the query needs.',
                   'Divide.'],
         code='''cols = {"order_id": 576, "student": 352126, "time": 901599, "item": 92796, "amount": 105756}
need = cols["item"] + cols["amount"]
total = sum(cols.values())
print(f"read {need:,} of {total:,} bytes = {need / total:.1%}")
''', notes={2: 'Projection :: Only the requested columns\' streams are read.'},
         tryit='Now add the time column. It alone is 62% of the file: high-cardinality columns are the expensive ones.'),
    dict(level='i', tag='Pushdown · sorting', title='Why sorting decides how much you skip',
         problem='<p>A 10-row-group file holds orders of 2,000 students. Unsorted, every row group contains students S0001 to S2000. Sorted by student, each row group covers a narrow range. For a query on one student, how many row groups must be read in each case, and how many rows is that?</p>',
         inp='10 row groups of 50,000 rows',
         approach=['A row group is read if min ≤ value ≤ max.',
                   'Unsorted: every range is S0001–S2000.',
                   'Sorted: only the group whose range contains the student.'],
         code='''groups_sorted = [("S0001", "S0013"), ("S0013", "S0118"), ("S0118", "S0354"), ("S0354", "S0589"), ("S0589", "S0823"),
                 ("S0823", "S1058"), ("S1058", "S1295"), ("S1295", "S1530"), ("S1530", "S1766"), ("S1766", "S2000")]
for name, groups in [("unsorted", [("S0001", "S2000")] * 10), ("sorted", groups_sorted)]:
    n = sum(lo <= "S1413" <= hi for lo, hi in groups)
    print(f"{name:8}: {n} row groups, {n * 50_000:,} rows decoded for 184 matches")
''', notes={3: 'Statistics :: The real min/max per row group from orders_sorted.parquet.'},
         tryit='Row group 0 covers only S0001–S0013: the 20 heavy users fill it. Sorting also packs similar values together, so the sorted file was smaller too (5.9 MB vs 6.2 MB).'),
    dict(level='a', tag='Cost · migration', title='Is converting a table to Parquet worth it?',
         problem='<p>A 50 TB CSV table is scanned by 400 queries a month, each reading 3 of 20 columns on average. A query engine charges ₹400 per TB scanned (illustrative). Parquet with ZSTD makes the table 7× smaller and projection reads about 3/20 of it. Converting costs one 50 TB scan. Compare the monthly bill and the payback time.</p>',
         inp='50 TB · 400 queries · 3 of 20 columns · 7× compression',
         approach=['CSV cost per query = 50 TB × ₹400.',
                   'Parquet per query = 50 / 7 × 3/20 TB × ₹400.',
                   'Payback = conversion cost / monthly saving.'],
         code='''tb, price, queries = 50, 400, 400
csv_month = queries * tb * price
pq_month = queries * tb / 7 * 3 / 20 * price
convert = tb * price
print(f"CSV Rs {csv_month:,.0f}/month, Parquet Rs {pq_month:,.0f}/month")
print(f"conversion Rs {convert:,.0f}, paid back in {convert / (csv_month - pq_month) * 30:.1f} days")
''', notes={4: 'Columns :: Projection and compression multiply.'},
         tryit='The saving is about 98%. Real columns differ in size, so measure with your engine\'s “bytes scanned” rather than trusting the column count.'),
]

QUIZ = mix([
    dict(q='Why did the Parquet item-only job read 192,526 bytes while the CSV job read 19,427,239?', options=['Parquet deletes duplicate rows', 'It read only the item column chunks (projection), which are small and encoded', 'It read a cached copy', 'It sampled 1% of the rows'], answer=1,
         why='Same answer, chai 149,669, from a 100× smaller read.'),
    dict(q='What is a Parquet row group?', options=['One row of the table', 'A horizontal slice of rows, holding one column chunk per column', 'A folder of Parquet files', 'The file footer'], answer=1,
         why='File → row groups → column chunks → pages, plus a footer.'),
    dict(q='Where does a Parquet reader find the schema and column statistics?', options=['In the first line of the file', 'In the footer at the end of the file', 'In the NameNode', 'In a separate .schema file'], answer=1,
         why='Readers seek to the end, read the footer, then jump to the chunks they need.'),
    dict(q='Why did 217,602 order ids take only 576 bytes in ORC?', options=['They were dropped', 'Sequential numbers are stored as start + step with run-length/delta encoding', 'ORC stores ids in the footer only', 'They were compressed with ZLIB to 1%'], answer=1,
         why='The encoding, not the codec, did most of that work.'),
    dict(q='Filtering student = S1413 had to read 10 of 10 row groups in one file and 1 of 10 in another. What was different?', options=['The codec', 'The second file was sorted by student, so min/max ranges were narrow', 'The second file was ORC', 'The second file had fewer rows'], answer=1,
         why='Predicate pushdown depends on clustering.'),
    dict(q='Which ORC structure plays the role of a Parquet row group?', options=['Postscript', 'Stripe', 'Page', 'Dictionary'], answer=1,
         why='Stripes (64 MB by default) with index data every 10,000 rows.'),
    dict(q='Our Parquet ZSTD job failed in every map task with a ClassNotFoundException for a zstd class. What fixes it?', options=['Use more reducers', 'Ship the zstd-jni jar to the tasks, e.g. with -libjars', 'Format HDFS', 'Switch to text output'], answer=1,
         why='The client had the class, the task containers did not.'),
    dict(q='When is a columnar format a poor choice?', options=['Large analytical scans', 'Writing one record at a time with frequent appends', 'Queries reading few columns', 'Data with many repeated values'], answer=1,
         why='Use a row format (Avro) for record-at-a-time writes, then compact to Parquet.'),
])

REVISION = [
    '<b>Columnar</b> = values of one column stored together: <b>projection</b>, better <b>encoding/compression</b>, <b>predicate pushdown</b>.',
    '<b>Parquet</b>: file → row groups (128 MB default) → column chunks → pages; footer with schema and min/max; magic “PAR1”.',
    '<b>ORC</b>: stripes (64 MB) with index (every 10,000 rows), data streams, stripe footer; file footer + postscript.',
    'Lab sizes: CSV 19.4 MB · Parquet Snappy 4.4 · ZSTD 2.8 · ORC ZLIB 3.3 · ZSTD 2.9 MB.',
    'Lab reads: CSV 19,427,239 bytes · Parquet all columns 4,431,110 · item only 192,526 · ORC item only 263,343.',
    'Pushdown needs clustering: S1413 → 10 of 10 row groups unsorted, 1 of 10 sorted.',
    'Parquet: default in Spark/Trino/Impala/Iceberg/Delta. ORC: Hive, required for Hive ACID.',
]
FAQ = [
    ('What is the difference between Parquet and ORC?', 'Both are columnar formats with encodings, compression and statistics. Parquet organises a file into row groups, column chunks and pages, has strong support for nested data and is the default for Spark, Trino, Impala and table formats like Iceberg and Delta. ORC organises a file into stripes with lightweight indexes every 10,000 rows, came from the Hive project and is required for Hive ACID tables. Sizes and speed are usually similar; ecosystem decides.'),
    ('Why is Parquet faster than CSV?', 'A Parquet reader reads only the columns a query needs (projection), the data is much smaller because each column is encoded (dictionary, run-length, delta) and compressed, and min/max statistics let it skip row groups that cannot match a filter. In our lab a job needing one column read 192,526 bytes from Parquet against 19,427,239 bytes from the CSV.'),
    ('What is predicate pushdown?', 'Pushing a filter (a predicate such as student = &#39;S1413&#39;) down to the file reader so it can skip data using the statistics stored in the file. If a row group&#39;s min and max for a column cannot satisfy the filter, the reader skips the whole row group. It works best when data is sorted or clustered by the filtered column.'),
    ('What is a row group in Parquet?', 'A horizontal partition of a Parquet file containing a set of rows, stored as one column chunk per column. Each column chunk is divided into pages. The writer default size is 128 MB; statistics are kept per column chunk (and per page), so the row group is the main unit for skipping and for parallel reading.'),
    ('Should I use Avro or Parquet?', 'Use Avro (row-oriented) for writing records one at a time, messaging and data exchange where whole records are read and schemas evolve. Use Parquet (columnar) for analytical tables that are scanned with few columns and filters. A common pipeline writes Avro or JSON on ingest and compacts it into Parquet tables.'),
]

PRACTICE_INTRO = 'Columnar format exercises using the real sizes and reads from our lab.'
PROBLEMS = [
    dict(level='easy', title='How much smaller?', stmt='Compute how many times smaller each Parquet variant is than the CSV.', inp='19,418,699 vs 7,428,043 / 4,438,970 / 2,775,449',
         code='''csv = 19418699
for name, b in [("uncompressed", 7428043), ("snappy", 4438970), ("zstd", 2775449)]:
    print(f"parquet {name:12} {csv / b:.1f}x smaller")
''', explain='2.6×, 4.4× and 7.0×. Even with no codec, encodings alone made Parquet 2.6× smaller.'),
    dict(level='easy', title='Projection saving', stmt='How many times fewer bytes did the item-only read take than the all-columns read, for Parquet and for ORC?', inp='4,431,110 / 192,526 · 3,297,403 / 263,343',
         code='''print(f"parquet {4431110 / 192526:.0f}x, orc {3297403 / 263343:.1f}x")
''', explain='23× and 12.5×. The item column is one of the cheapest columns, so the saving is large.'),
    dict(level='easy', title='Bytes per value', stmt='How many bits per row did ORC use for order_id and for item?', inp='576 and 92,796 bytes for 217,602 rows',
         code='''rows = 217602
for name, b in [("order_id", 576), ("item", 92796)]:
    print(f"{name:8} {b * 8 / rows:.2f} bits per row")
''', explain='0.02 and 3.4 bits per row. A CSV spends about 6 bytes (48 bits) per order id.'),
    dict(level='medium', title='Dictionary encode a column', stmt='Dictionary-encode the item column: print the dictionary and the codes.', inp='6 values',
         code='''col = ["dosa", "samosa", "samosa", "chai", "dosa", "chai"]
d = {}
codes = [d.setdefault(v, len(d)) for v in col]
print(d)
print(codes)
''', explain='Three distinct strings stored once; the column becomes small integers that pack into a few bits each.'),
    dict(level='medium', title='Delta encoding', stmt='Delta-encode a sorted id column and decode it back.', inp='ids 1001..1006',
         code='''ids = [1001, 1002, 1003, 1004, 1005, 1006]
deltas = [ids[0]] + [b - a for a, b in zip(ids, ids[1:])]
print("encoded:", deltas)
back = [deltas[0]]
for d in deltas[1:]:
    back.append(back[-1] + d)
print("decoded:", back, back == ids)
''', explain='All deltas are 1, which run-length encoding then turns into “1 × 5”: why 2 lakh ids took 576 bytes.'),
    dict(level='medium', title='Row groups to read', stmt='Given row-group min/max dates, which groups must be read for orders on 2026-09-17?', inp='4 row groups',
         code='''groups = [("2026-09-01", "2026-09-08"), ("2026-09-08", "2026-09-15"), ("2026-09-15", "2026-09-23"), ("2026-09-23", "2026-09-30")]
print([i for i, (lo, hi) in enumerate(groups) if lo <= "2026-09-17" <= hi])
''', explain='Only group 2. ISO dates compare correctly as strings; that is one reason to store dates in sortable form.'),
    dict(level='business', title='Storage bill', stmt='The canteen chain keeps 3 years of orders: 200 GB of CSV per year, stored with replication 3 at ₹2 per GB per month. What is the monthly storage bill as CSV and as Parquet ZSTD (7× smaller)?', inp='600 GB · ×3 replicas · ₹2/GB-month',
         code='''csv_gb = 3 * 200
for name, gb in [("CSV", csv_gb), ("Parquet ZSTD", csv_gb / 7)]:
    print(f"{name:12} Rs {gb * 3 * 2:,.0f} per month")
''', explain='₹3,600 vs about ₹514 per month (illustrative prices), before counting the faster queries.'),
    dict(level='advanced', title='Choose a sort column', stmt='Queries filter by student 70% of the time and by item 30%. With 10 row groups, how many row groups does an average query read if the file is sorted by student, and if sorted by item? Assume a sorted column narrows to 1 group and an unsorted one needs all 10, except that 8 items sorted means about 2 groups per item.', inp='70% student, 30% item',
         code='''by_student = 0.7 * 1 + 0.3 * 10
by_item = 0.7 * 10 + 0.3 * 2
print(f"sorted by student: {by_student:.1f} groups per query, sorted by item: {by_item:.1f}")
''', explain='3.7 vs 7.6 groups: sort by the column most queries filter on. Engines also offer Z-ordering or bloom filters to help a second column.'),
]

SCN_INTRO = 'File formats come up in every data engineering interview, often as “Parquet or ORC?” or “why is this query slow?”.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Formats · basics</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“Why is Parquet better than CSV for analytics?”</h4>
      <p class="scn__situation">The standard opener.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> the three mechanisms, not just “it's compressed”.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Columnar: a query reads only the columns it needs (projection).</li>
          <li>Each column is encoded (dictionary, RLE, delta) and compressed; similar values compress far better.</li>
          <li>Footer statistics (min/max per row group) let readers skip data for filters; the schema travels with the file.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Performance · pushdown</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>“Our Parquet table is filtered by customer_id but every query scans the whole table.”</h4>
      <p class="scn__situation">The table is partitioned by date only.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> clustering and statistics.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Min/max statistics only skip row groups when values are clustered; random order makes every row group span all customers.</li>
          <li>Sort (or Z-order) data by customer_id within each date partition when writing or compacting; consider bloom filters for point lookups.</li>
          <li>Check the engine's “row groups skipped / bytes scanned” metrics before and after.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Design · choice</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>“Parquet or ORC for our new lake?”</h4>
      <p class="scn__situation">The team uses Spark for ETL and Trino and Hive for queries.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> ecosystem reasoning.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Both perform similarly; choose by ecosystem. Spark, Trino, Iceberg and Delta default to Parquet.</li>
          <li>Pick ORC if you need Hive ACID tables or have an existing ORC warehouse.</li>
          <li>Standardise the codec (Snappy for hot, ZSTD for cold) and target file sizes of hundreds of MB.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Operations · failure</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>A job writing Parquet with ZSTD fails with ClassNotFoundException in every map task</h4>
      <p class="scn__situation">The same code worked with Snappy, and the class compiles fine on the edge node.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> client vs task classpath.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>The task containers lack a jar the client has (here zstd-jni, which lives in share/hadoop/tools/lib).</li>
          <li>Ship it with -libjars (or build a fat jar, or set mapreduce.application.classpath on the cluster).</li>
          <li>Read the attempt diagnostics in the JobHistory server to see the exact missing class.</li>
        </ul>
      </div></details>
    </article>
'''
