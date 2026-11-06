import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()

SIZES = [('ORC NONE', 674283), ('ORC SNAPPY', 570494), ('ORC LZ4', 572490), ('ORC ZLIB', 437536), ('ORC ZSTD', 436490),
         ('PQ NONE', 1093857), ('PQ SNAPPY', 762424), ('PQ ZSTD', 582505), ('PQ GZIP', 536505)]
def codecbars(y=36, hi=None, step=12.5):
    o = ''
    for k, (n, b) in enumerate(SIZES):
        w = round(200 * b / 1093857)
        col = ('violet' if n.startswith('PQ') else 'blue') if hi is None or n in hi else 'grey'
        o += t(96, y + 9 + k * step, n, 7, 'ink', anchor='end', mono=True) + fill(102, y + k * step, w, 9, col, rx=2) + t(106 + w, y + 8 + k * step, f'{b / 1e3:.0f} KB', 6.6, 'ink2', anchor='start', mono=True)
    return o
SPEED = [('snappy', 3.0, 655, 1385), ('lz4', 3.2, 670, 2593), ('zstd-3', 5.1, 303, 1162), ('gzip-6', 5.2, 40, 622), ('bzip2-9', 8.0, 18, 38)]

# ---------------------------------------------------------------- story
sc = (box(10, 12, 300, 128, 'card') + t(160, 30, 'Data science team (Spark)', 8.8, bold=True) +
      t(22, 54, '“We want Parquet. And compress it,', 7.8, 'ink', anchor='start') + t(22, 70, ' storage costs too much.”', 7.8, 'ink', anchor='start') +
      t(22, 96, 'Hive CTAS STORED AS PARQUET:', 7.6, 'ink2', anchor='start') + t(22, 114, 'compression: UNCOMPRESSED', 8.4, 'red', anchor='start', mono=True, bold=True) + t(22, 130, '1,093,857 bytes', 7.6, 'ink2', anchor='start', mono=True) +
      box(330, 12, 300, 128, 'green') + t(480, 30, 'Same rows, codec chosen', 8.8, 'green', bold=True) +
      ''.join(t(342, 54 + k * 18, s, 7.8, 'ink', anchor='start', mono=True) for k, s in enumerate(['PARQUET + SNAPPY   762 KB', 'PARQUET + ZSTD     583 KB', 'PARQUET + GZIP     537 KB', 'ORC + ZSTD         436 KB'])) +
      t(480, 130, 'which one? size vs speed', 7.6, 'acc', bold=True))
scene_svg = scene('Hive writes Parquet uncompressed by default, about 1.09 MB for 50,000 orders. With Snappy, ZSTD or GZIP the same rows take 762, 583 or 537 KB; ORC with ZSTD takes 436 KB. The question is which codec to pick.', sc,
                  'Parquet is the shared language of Spark, Trino and the cloud. Pick its <tspan font-weight="700" class="s-acc">codec</tspan> on purpose.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Give us Parquet, and make it smaller”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s data science team works in Spark and asks for the orders table in <b>Parquet</b>. Kabir runs one CTAS and sends it. The next day the platform team complains about storage: the Parquet copy is <b>2.5 times larger</b> than the ORC table. Kabir checks the file and finds it was written with no compression at all.</p>

{scene_svg}

K> Sir, ORC compressed itself. Why didn’t Parquet?
A> Each format has its own codec setting. ORC defaults to ZLIB; in our Hive 4.2.1 the Parquet writer defaulted to <b>UNCOMPRESSED</b>. You set <code>parquet.compression</code> on the table or the session. The real question is which codec: Snappy and LZ4 are fast, ZLIB, GZIP and ZSTD are small, and bzip2 is very small and very slow.
R> And is Parquet different from ORC inside?
A> Same idea, different details: row groups instead of stripes, pages inside column chunks, statistics in the footer. Today we open a real Parquet file, measure five codecs on our data, and find three things that differ from ORC in Hive 4.2.1: no compression by default, INT96 timestamps, and a range filter that ORC skipped but Parquet did not. All outputs are real.
  </div>
</section>
'''

lv = '''
LEVELS> Parquet and codecs at three levels
L1> Zip files for columns
      <ul>
        <li>Parquet, like ORC, stores data <b>column by column</b> and keeps a summary of each column so tools can skip data.</li>
        <li>A <b>codec</b> is the zip method used inside the file. Faster codecs save less space; stronger codecs save more space but cost more CPU.</li>
        <li>Parquet is the most widely shared format: Spark, Trino, Impala, Athena, BigQuery and pandas all read it.</li>
      </ul>
L2> Parquet’s structure and Hive settings
      <ul>
        <li><b>File</b> = row groups + footer. A <b>row group</b> (target size <code>parquet.block.size</code>, typically 128 MB) holds a <b>column chunk</b> per column; each chunk is split into <b>pages</b> (about 1 MB). The footer (schema, row group list, statistics) ends with the magic bytes <code>PAR1</code>, which also start the file.</li>
        <li>Encodings: <b>dictionary</b> for repeated values, PLAIN otherwise, plus RLE / bit-packing for levels and dictionary ids.</li>
        <li>Codec per table: <code>TBLPROPERTIES ('parquet.compression'='SNAPPY')</code> (UNCOMPRESSED, SNAPPY, GZIP, ZSTD, LZ4…). ORC: <code>'orc.compress'</code>.</li>
        <li>Hive matches Parquet columns <b>by name</b> by default, so files written by other engines with a different column order still read correctly.</li>
      </ul>
L3> What Hive 4.2.1 did in our lab
      <ul>
        <li>CTAS <code>STORED AS PARQUET</code> wrote <b>UNCOMPRESSED</b> column chunks (1.09 MB); ORC used ZLIB (0.44 MB).</li>
        <li>Hive wrote timestamps as legacy <b>INT96</b> (<code>hive.parquet.write.int64.timestamp=false</code>); with the setting on, INT64 microseconds, which newer readers prefer.</li>
        <li>The Parquet writer stored sorted <code>order_id</code> PLAIN: 200 KB, against 161 bytes in ORC’s RLE.</li>
        <li><code>amount &gt; 900</code> (above the file max) skipped the whole ORC file, but the Parquet table read all 50,000 rows. On a Parquet file sorted by customer with small row groups, a lookup read 1,458 rows: Parquet row-group statistics work, but test each data type.</li>
        <li>On 50,000 rows every format answered a GROUP BY in about 3.1–3.4 s: fixed job overhead hides format differences on small data. Benchmark on realistic sizes.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Parquet and compression codecs</h2>
''' + def_block(
    '<b>Apache Parquet</b> is an open, self-describing columnar file format. A file is divided into <b>row groups</b>; each row group contains one <b>column chunk</b> per column, made of <b>pages</b> that are encoded (dictionary, plain, run-length/bit-packed) and compressed with a <b>codec</b>. The footer holds the schema and per-column-chunk statistics (min, max, null count) used for predicate pushdown. A <b>compression codec</b> is an algorithm applied to blocks of data: Snappy and LZ4 favour speed, GZIP/ZLIB and ZSTD favour compression ratio, and BZip2 gives the highest ratio at much lower speed. Codecs applied inside container formats keep files splittable.',
    'Parquet is a columnar format like ORC, used by almost every big data tool. Inside both formats you choose a compression codec: fast ones (Snappy, LZ4) for data you read all the time, small ones (ZSTD, GZIP) for data you store long. In Hive you set it per table.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Row group', 'A horizontal slice of a Parquet file (like an ORC stripe).'),
    ('Column chunk', 'All values of one column in one row group.'),
    ('Page', 'The unit of encoding and compression inside a column chunk.'),
    ('Codec', 'Compression algorithm: SNAPPY, LZ4, ZSTD, GZIP/ZLIB, BZIP2.'),
    ('Compression ratio', 'Original size ÷ compressed size (5× means one fifth).'),
    ('INT96 timestamp', 'Legacy 12-byte Parquet timestamp written by Hive by default.'),
    ('parquet.compression', 'Table or session property choosing the Parquet codec.'),
    ('orc.compress', 'Table property choosing the ORC codec (default ZLIB).'),
]) + '''

  <h3>ORC vs Parquet in our lab (same 50,000 orders)</h3>
''' + table(['', 'ORC', 'Parquet'], [
    ['Default codec in Hive 4.2.1', 'ZLIB', '<b>UNCOMPRESSED</b>'],
    ['Size with default / SNAPPY / ZSTD', '437 KB / 570 KB / 436 KB', '1,094 KB / 762 KB / 583 KB'],
    ['Sorted order_id column', '161 bytes (RLE v2)', '200,134 bytes (PLAIN)'],
    ['Slices', 'Stripes (64 MB) → row groups of 10,000 rows', 'Row groups (128 MB) → pages (1 MB)'],
    ['Skip by statistics', 'File, stripe, every 10,000 rows; bloom filters', 'Row group (and page indexes in newer readers)'],
    ['<code>amount &gt; 900</code> (above max)', '0 splits, 0 rows', '50,000 rows read'],
    ['Best fit', 'Hive warehouses, Hive ACID tables', 'Data shared with Spark, Trino, cloud tools'],
], minw=640) + lv + '''
EXAM> “ORC vs Parquet” and “Which compression codec would you choose?” are frequent. For the codec, answer with the trade-off: Snappy/LZ4 for hot, frequently read data (fast); ZSTD or ZLIB/GZIP for warm and cold data (smaller); bzip2 only for archives of text. Always compress inside a container format so files stay splittable.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Choosing and setting a codec</h2>
''' + table(['Codec', 'Strength', 'Typical use', 'Set it'], [
    ['SNAPPY', 'Very fast, moderate ratio', 'Hot tables read all day, intermediate data', "<code>'parquet.compression'='SNAPPY'</code> / <code>'orc.compress'='SNAPPY'</code>"],
    ['LZ4', 'Fastest decompression', 'Interactive queries, shuffle data', "<code>'orc.compress'='LZ4'</code>"],
    ['ZSTD', 'Good ratio, fast decompression', 'A strong default for most tables today', "<code>'parquet.compression'='ZSTD'</code>"],
    ['ZLIB / GZIP', 'Good ratio, slower', 'ORC default (ZLIB); cold data', "<code>'orc.compress'='ZLIB'</code>"],
    ['BZIP2', 'Best ratio, very slow', 'Archives of text files (splittable)', "<code>BZip2Codec</code> for text output"],
    ['NONE / UNCOMPRESSED', 'No CPU', 'Rare; already-compressed data', "Parquet’s default in our lab"],
], minw=760) + '''
''' + table(['Where', 'Setting'], [
    ['One table (recommended)', "<code>CREATE TABLE t … STORED AS PARQUET TBLPROPERTIES ('parquet.compression'='ZSTD');</code>"],
    ['A session (Parquet)', '<code>SET parquet.compression=SNAPPY;</code>'],
    ['ORC default for new tables', '<code>SET hive.exec.orc.default.compress=ZSTD;</code>'],
    ['Text / SequenceFile / Avro output', '<code>SET hive.exec.compress.output=true;</code> + <code>mapreduce.output.fileoutputformat.compress.codec</code>'],
    ['Intermediate data between stages', '<code>SET hive.exec.compress.intermediate=true;</code>'],
], minw=640) + '''
WARN> A codec setting affects only files written after it. Changing <code>TBLPROPERTIES</code> on an existing table leaves old files as they are (each file records its own codec, so mixed files still read fine). Rewrite partitions to apply the new codec.
</section>
'''

ppd = capf('l63_ppd.txt').split('\n')
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Parquet inside out, then five codecs</h2>
  <p>All outputs are real, from the Hive 4.2.1 lab (database <code>tiffingo</code>). Parquet metadata was read with Python’s pyarrow library.</p>
''' + stepper([
    ('Step 1 · A Parquet table, and its default codec',
     code('sql', 'Beeline', "CREATE TABLE f_parquet STORED AS PARQUET AS SELECT * FROM orders;\n$ ls -l …/f_parquet/       # then read the footer with pyarrow", 'f_parquet/000000_0   1,093,857 bytes   starts and ends with PAR1\n  created_by: parquet-mr version 1.15.2 (build 859eac16…)\n  num_rows: 50000   num_row_groups: 1\n  column order_id: compression: UNCOMPRESSED  encodings: PLAIN, RLE, BIT_PACKED\n                   statistics: min 100001  max 150000  null_count 0'),
     'Hive 4.2.1 uses the parquet-mr (Java) writer and, unless you set <code>parquet.compression</code>, writes uncompressed pages. Statistics are still written, per column chunk. Always set the codec explicitly for Parquet tables.'),
    ('Step 2 · Inside: encodings and sizes per column',
     code('bash', 'Terminal', "# column-chunk metadata of a SNAPPY Parquet copy (c_pq_snappy)", capf('l63_pqmeta.txt').split('\n', 1)[1]),
     'Low-cardinality columns use <b>dictionary</b> encoding, so Snappy finds little left to squeeze (compressed ≈ uncompressed). The sorted <code>order_id</code> is stored PLAIN: 200 KB, where ORC needed 161 bytes. Timestamps are the biggest column, written as 12-byte <b>INT96</b> values.'),
    ('Step 3 · Same rows, five codecs, two formats',
     code('sql', 'Beeline', "CREATE TABLE c_orc_zstd  STORED AS ORC     TBLPROPERTIES ('orc.compress'='ZSTD')        AS SELECT * FROM orders;\nCREATE TABLE c_pq_snappy STORED AS PARQUET TBLPROPERTIES ('parquet.compression'='SNAPPY') AS SELECT * FROM orders;\n-- … one table per codec, then ls -l", capf('l63_sizes.txt')),
     'For both formats ZSTD and ZLIB/GZIP give the smallest files; Snappy and LZ4 save less. ORC is smaller than Parquet with every codec on this data, mainly because of its integer encodings. ORC with no compression at all (674 KB) is only a little bigger than Parquet with ZSTD (583 KB): encoding matters as much as the codec.'),
    ('Step 4 · Speed: what each codec costs',
     code('python', 'Python', "# compress / decompress the 3.7 MB text file of 50,000 orders with each codec\n# (cramjam library, best of 5 runs, one CPU core)", capf('l63_speed.txt')),
     'The trade-off in numbers: Snappy and LZ4 compress about <b>16 times faster</b> than gzip, and LZ4 decompresses fastest. ZSTD gets gzip’s ratio while decompressing about twice as fast. bzip2 has the best ratio but decompresses at 38 MB/s, roughly 36 times slower than Snappy. Your hardware gives different absolute numbers; the order stays the same.'),
    ('Step 5 · Statistics-based skipping: Parquet vs ORC',
     code('sql', 'Beeline', "SET hive.tez.exec.print.summary=true;\nSELECT COUNT(*) AS n FROM c_pq_snappy WHERE amount > 900;          -- ORC: 0 splits\nSELECT COUNT(*) AS n FROM c_pq_snappy WHERE customer_id = 1492;\n\nSET parquet.block.size=100000;    -- small row groups, for the demo only\nCREATE TABLE pq_sorted STORED AS PARQUET TBLPROPERTIES ('parquet.compression'='SNAPPY')\n  AS SELECT * FROM orders ORDER BY customer_id;\nSELECT COUNT(*) AS n FROM pq_sorted WHERE customer_id = 1492;", '\n'.join(ppd) + '\n\n(pq_sorted: 35 row groups of about 1,460 rows; first ones: customer 1–57, 57–114, 114–173 …)'),
     'On the decimal <code>amount</code> filter Hive read every Parquet row, while the same filter skipped the whole ORC file (6.2). Row-group statistics did work on a sorted integer column: 1,458 rows read instead of 50,000. Lesson: Parquet skipping depends on the column type and the reader version, so check counters for your important filters.'),
    ('Step 6 · Files from another engine: Parquet reads by name',
     code('sql', 'Beeline', "-- written by Python/pyarrow, not Hive:\n--   part-v1.parquet (snappy): customer_id, name, city\n--   part-v2.parquet (zstd):   customer_id, plan, city, name   (new column, new order)\nCREATE EXTERNAL TABLE cust_pq (customer_id INT, name STRING, plan STRING, city STRING)\nSTORED AS PARQUET LOCATION 'file:///data/tiffingo/pq_ext';\nSELECT * FROM cust_pq ORDER BY customer_id;", capf('l63_byname.txt')),
     'Hive matched Parquet columns by <b>name</b>, so the different column order did not matter, and two codecs in the same table are fine because each file records its own. A column missing from old files came back as NULL (Parquet has no defaults, unlike Avro in 6.1).'),
    ('Step 7 · Timestamps: INT96 vs INT64',
     code('sql', 'Beeline', "SET hive.parquet.write.int64.timestamp;          -- false\nSET hive.parquet.write.int64.timestamp=true;\nCREATE TABLE pq_ts64 STORED AS PARQUET AS\n  SELECT order_id, order_ts FROM orders WHERE order_id < 100004;\nSELECT * FROM pq_ts64;\n$ pyarrow schema of pq_ts64", capf('l63_int64.txt') + '\n\noptional int64 order_ts (Timestamp(isAdjustedToUTC=false, timeUnit=microseconds))\n(default tables: optional int96 order_ts)'),
     'INT96 is a deprecated encoding that some newer tools read differently or not at all. With the setting on, Hive writes standard INT64 microsecond timestamps marked as local time (not UTC). When Parquet tables are shared with Spark or Trino, agree on the timestamp encoding and time zone (Lesson 4.1).'),
    ('Step 8 · Does the format change query time on small data?',
     code('sql', 'Beeline', "SELECT city, SUM(amount) FROM <table> GROUP BY city;   -- each table, 5 runs", capf('l63_times.txt').split('\n', 1)[1]),
     'All within 0.3 s of each other. On 50,000 rows, starting the job costs far more than reading 0.4–3.7 MB. Format and codec differences show up when tables are gigabytes or larger, where bytes read dominate. Benchmark with realistic volumes before deciding, and use counters (rows and bytes read) rather than stopwatch time on toy data.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('> CREATE TABLE f_parquet STORED AS PARQUET', W), ('    AS SELECT * FROM orders;', W), ('$ pyarrow: compression: UNCOMPRESSED', Y), ('  file: 1,093,857 bytes', Y)]),
    term([('order_id   PLAIN              200,134 B', RD), ('city       PLAIN_DICTIONARY    19,085 B', G), ('order_ts   INT96              267,267 B', Y), ('amount     FIXED_LEN(5)        99,702 B', W)], size=7.6),
    term([('ORC ZLIB      437,536', G), ('ORC ZSTD      436,490', G), ('PQ  GZIP      536,505', G), ('PQ  ZSTD      582,505', G), ('PQ  SNAPPY    762,424', Y), ('PQ  NONE    1,093,857', RD)]),
    term([('codec    ratio  compress  decompress', W), ('snappy   3.0x   655 MB/s  1385 MB/s', G), ('lz4      3.2x   670 MB/s  2593 MB/s', G), ('zstd-3   5.1x   303 MB/s  1162 MB/s', G), ('gzip-6   5.2x    40 MB/s   622 MB/s', Y), ('bzip2-9  8.0x    18 MB/s    38 MB/s', RD)], size=7.6),
    term([('> … c_pq_snappy WHERE amount > 900;', W), ('| 0 |  RECORDS_IN 50000', Y), ('> … pq_sorted WHERE customer_id = 1492;', W), ('| 41 | RECORDS_IN 1458', G)], size=7.6),
]
def pqfile(y=40):
    o = box(20, y, 34, 60, 'violet') + t(37, y + 34, 'PAR1', 6.6, bold=True, mono=True)
    for g in range(2):
        gx = 58 + g * 108
        o += box(gx, y, 104, 60, 'blue') + t(gx + 52, y + 12, f'row group {g}', 7.2, bold=True)
        for c in range(3):
            o += box(gx + 4 + c * 33, y + 18, 30, 38, 'card') + t(gx + 19 + c * 33, y + 32, f'col{c + 1}', 6.2, 'ink', mono=True) + t(gx + 19 + c * 33, y + 46, 'pages', 5.8, 'ink2')
    o += box(276, y, 64, 60, 'violet') + t(308, y + 28, 'footer', 7.4, bold=True) + t(308, y + 42, '+ PAR1', 6.6, 'ink2', mono=True)
    return o
B1 = [
    t(180, 22, 'A Parquet file', 9.4, bold=True) + pqfile() + cap('Footer: schema, row groups, statistics.', 'Codec chosen per column chunk at write time.', 'blue', y=150, h=46),
    t(180, 22, 'Encoding happens before compression', 9.4, bold=True) + box(20, 44, 150, 70, 'card') + t(95, 62, 'dictionary', 8.2, bold=True) + t(95, 80, 'Mumbai → 0, Pune → 1 …', 7.2, 'ink2', mono=True) + t(95, 96, 'already tiny', 7.2, 'green') +
    box(190, 44, 150, 70, 'card') + t(265, 62, 'PLAIN', 8.2, bold=True) + t(265, 80, '4 bytes × 50,000 ids', 7.2, 'ink2', mono=True) + t(265, 96, 'codec must do the work', 7.2, 'red') + cap('ORC’s RLE turned the same ids into 161 bytes.', '', 'blue', y=150, h=34),
    t(180, 22, 'Bytes on disk by codec', 9.4, bold=True) + codecbars(30, step=12) + cap('ORC (blue) smaller than Parquet (violet) on this data.', '', 'green', y=150, h=34),
    t(180, 22, 'Ratio vs decompression speed', 9.4, bold=True) + ''.join(fill(70, 40 + k * 20, round(SPEED[k][1] * 25), 7, 'green', rx=2) + fill(70, 48 + k * 20, max(2, round(SPEED[k][3] / 2593 * 260)), 7, 'blue', rx=2) + t(64, 50 + k * 20, SPEED[k][0], 7.2, 'ink', anchor='end', mono=True) for k in range(5)) +
    cap('green = ratio · blue = decompress speed', 'bzip2: best ratio, slowest by far.', 'blue', y=150, h=46),
    t(180, 22, 'Row-group statistics in Parquet', 9.4, bold=True) + ''.join(box(20 + k * 64, 50, 60, 40, 'green' if k == 2 else 'card') + t(50 + k * 64, 66, f'RG{23 + k}', 7.4, 'ink', bold=True) + t(50 + k * 64, 80, ['1350–1409', '1409–1469', '1469–1528', '1528–1584', '1584–1642'][k], 6.2, 'ink2', mono=True) for k in range(5)) +
    cap('Sorted ints: groups skipped (1,458 rows read).', 'Decimal amount > 900: nothing skipped in our lab.', 'amber', y=150, h=46),
]
see_caps = ['A plain Parquet CTAS wrote uncompressed pages: 1.09 MB.',
            'Per-column metadata: dictionary for repeats, PLAIN for ids, INT96 timestamps.',
            'Five codecs on two formats: ZSTD and ZLIB/GZIP give the smallest files.',
            'Speed: Snappy and LZ4 are fast; bzip2 is very slow.',
            'Parquet skipped row groups on a sorted id, but not on the decimal filter.']
behind_caps = ['A Parquet file is row groups of column chunks and pages, with the footer at the end.',
               'Encodings shrink data before the codec; PLAIN columns rely on the codec alone.',
               'Each codec trades CPU for space differently; encodings decide the rest.',
               'Fast codecs suit hot data; strong codecs suit data that is stored long and read rarely.',
               'Readers compare filters with each row group’s min and max, where the type supports it.']
two = anim_two('Parquet and codecs', 'Structure, encodings, size and speed', 'Real output', 'What happens inside the file', see, B1, see_caps, behind_caps)

# ---- scenario 1: codec policy
p1 = (t(180, 22, 'One codec policy for the lake', 9.4, bold=True) + t(180, 56, 'hot (last 7 days) · warm (90 days) · cold (years)', 8.2, 'ink2') + cap('Different data, different needs.', '(typical policy)', 'blue', y=150, h=46))
p2 = (t(180, 22, 'Hot: read all day', 9.4, bold=True) + t(180, 56, 'SNAPPY or LZ4 · fastest to decompress', 8.4, 'ink', mono=True) + cap('Real: LZ4 decompresses at 2,593 MB/s.', '', 'green', y=150, h=34))
p3 = (t(180, 22, 'Warm and cold: stored long', 9.4, bold=True) + t(180, 56, 'ZSTD · gzip-level size, faster reads', 8.4, 'ink', mono=True) + cap('Real: 5.1× ratio, 1,162 MB/s decompress.', '', 'green', y=150, h=34))
p4 = (t(180, 22, 'Re-compress when data cools', 9.4, bold=True) + t(180, 52, "INSERT OVERWRITE … PARTITION (dt='…')", 8, 'ink', mono=True) + t(180, 68, "with TBLPROPERTIES codec = ZSTD", 8, 'ink', mono=True) + cap('Old files keep their codec until rewritten.', '', 'amber', y=150, h=34))
p5 = (t(180, 22, 'Measure', 9.4, 'acc', bold=True) + t(180, 56, 'storage bill vs query CPU per month', 8.4, 'ink2') + cap('Many teams simply use ZSTD everywhere now.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'A codec policy: hot, warm and cold data',
              'Choosing codecs by how often data is read. Speeds are from our measurement.',
              'Codec policy', 'Fast codecs for frequently read recent data, ZSTD for older data, with partitions rewritten as data cools', [p1, p2, p3, p4, p5],
              ['Group data by how often it is read.',
               'Hot data uses a fast codec.',
               'Older data uses ZSTD for size with good speed.',
               'Rewrite partitions to change their codec.',
               'Watch storage and CPU costs.'],
              hid='scenario-policy')

# ---- scenario 2: sharing with Spark
h1 = (t(180, 22, 'Sharing a table with Spark and Trino', 9.4, bold=True) + t(180, 56, 'STORED AS PARQUET, codec set explicitly', 8.4, 'ink', mono=True) + cap('Parquet is every engine’s common format.', '', 'blue', y=150, h=34))
h2 = (t(180, 22, 'Timestamps', 9.4, bold=True) + t(180, 56, 'Hive default: INT96 (legacy)', 8.4, 'red', mono=True) + t(180, 74, 'hive.parquet.write.int64.timestamp=true', 8, 'green', mono=True) + cap('Agree the encoding and time zone with readers.', '', 'amber', y=150, h=34))
h3 = term([('> SELECT * FROM cust_pq ORDER BY customer_id;', W), ('| 1 | Aarav Desai | NULL  | Bengaluru |', G), ('| 4 | Diya Patil  | Gold  | Pune      |', G), ('  files written by pyarrow, other order', Y)], label='real output · Hive 4.2.1')
h4 = (t(180, 22, 'Columns by name', 9.4, bold=True) + t(180, 56, 'new columns: NULL in old files', 8.4, 'ink2') + cap('Add columns; avoid renames without a plan.', '', 'blue', y=150, h=34))
h5 = (t(180, 22, 'Check from both sides', 9.4, 'acc', bold=True) + t(180, 56, 'same COUNT, SUM and a few timestamps in each engine', 8, 'ink2') + cap('A 5-minute test avoids weeks of confusion.', '', 'green', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'One Parquet table, three engines',
              'Making a Hive Parquet table safe for Spark and Trino. The query result is real.',
              'Cross-engine Parquet', 'Set the codec and timestamp encoding explicitly, rely on by-name columns, and verify results in every engine', [h1, h2, h3, h4, h5],
              ['Use Parquet with an explicit codec for shared tables.',
               'Decide how timestamps are written.',
               'Hive read files written by another tool, by column name.',
               'New columns read as NULL in old files.',
               'Compare results in each engine.'],
              hid='scenario-sharing')

# ---- scenario 3: storage bill
c1 = (t(180, 22, 'Storage bill: 400 TB of uncompressed Parquet', 9.4, bold=True) + t(180, 56, 'written by CTAS jobs without a codec', 8.4, 'red') + cap('Like our f_parquet: UNCOMPRESSED.', '(illustrative size)', 'amber', y=150, h=46))
c2 = (t(180, 22, 'Estimate with the lab ratio', 9.4, bold=True) + t(180, 56, 'ZSTD: 582,505 / 1,093,857 = 0.53', 8.4, 'ink', mono=True) + t(180, 74, '400 TB → about 213 TB', 8.4, 'green', mono=True, bold=True) + cap('Measure on one real partition first.', '', 'blue', y=150, h=34))
c3 = (t(180, 22, 'Fix new writes first', 9.4, bold=True) + t(180, 56, "ALTER TABLE … SET TBLPROPERTIES ('parquet.compression'='ZSTD')", 7.2, 'ink', mono=True) + cap('Every new file is compressed from now on.', '', 'green', y=150, h=34))
c4 = (t(180, 22, 'Rewrite old partitions gradually', 9.4, bold=True) + t(180, 56, 'oldest first, off-peak, counts checked', 8.4, 'ink2') + cap('Each file keeps its own codec, so reads never break.', '', 'green', y=150, h=34))
c5 = (t(180, 22, 'Guard rail', 9.4, 'acc', bold=True) + t(180, 56, 'review TBLPROPERTIES in every new table', 8.4, 'ink2') + cap('A default that silently costs money.', '', 'amber', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Halving a storage bill with one property',
              'Uncompressed Parquet is an easy mistake with Hive’s default. Ratios from our lab; the 400 TB is illustrative.',
              'Storage clean-up', 'Uncompressed Parquet tables are fixed by setting a codec for new writes and rewriting old partitions gradually', [c1, c2, c3, c4, c5],
              ['Jobs wrote uncompressed Parquet for months.',
               'The lab ratio suggests ZSTD would almost halve it.',
               'Set the codec on the table for new files.',
               'Rewrite old partitions step by step.',
               'Make codec review part of table creation.'],
              hid='scenario-bill')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Inside Parquet, and what codecs cost</h2>
  <p>Left: real output. Right: what happens inside the file.</p>
''' + two + '''
  <p>Three live scenarios follow: a codec policy, sharing Parquet with other engines, and a storage bill.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Parquet and codecs at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'PAR1', 12, 'green', bold=True, mono=True) + t(60, 58, 'shared lake', 7.4, 'ink2'),
    '1. The shared format of the lake',
    'Cloud data lakes keep most curated tables in Parquet so that Spark jobs, SQL engines, notebooks and BI tools all read the same files.',
    ['Hive / Spark write', '*Parquet', 'Every engine reads']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'ZSTD', 12, 'blue', bold=True, mono=True) + t(60, 58, 'default codec', 7.4, 'ink2'),
    '2. ZSTD as the new default',
    'Many platforms have moved from Snappy or GZIP to ZSTD, because it gives gzip-like size with much faster reads.',
    ['Old codec', '*rewrite with ZSTD', 'Smaller, fast']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'Iceberg', 11, 'violet', bold=True) + t(60, 58, 'on Parquet', 7.4, 'ink2'),
    '3. Table formats on Parquet',
    'Apache Iceberg and Delta Lake usually store their data files as Parquet and add a metadata layer for snapshots and updates (Module 7).',
    ['Parquet files', '*table metadata', 'Lakehouse tables']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'pandas', 11, 'acc', bold=True, mono=True) + t(60, 58, 'data science', 7.4, 'ink2'),
    '4. Handing data to data scientists',
    'A Parquet extract with a few columns opens directly in pandas or Polars, typed and compressed, unlike a CSV dump.',
    ['Hive query', '*Parquet extract', 'Notebook']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, '₹ / TB', 11, 'acc', bold=True) + t(60, 58, 'cost control', 7.4, 'ink2'),
    '5. Storage and scan costs',
    'On cloud engines that charge per byte scanned, columnar formats plus a good codec reduce both the storage bill and the query bill.',
    ['Raw data', '*columnar + codec', 'Lower bills']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> read Lessons <a href="../01-text-sequence-and-avro/">6.1</a> and <a href="../02-orc-deep-dive/">6.2</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
