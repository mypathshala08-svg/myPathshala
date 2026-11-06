import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()

def orcfile(x=20, y=36, hi=None, w=320):
    """Diagram of an ORC file: stripes (index | data | footer), file footer, postscript."""
    o = ''
    parts = [('Stripe 1', 'stripe'), ('Stripe 2', 'stripe'), ('…', 'gap'), ('File footer', 'footer'), ('Postscript', 'ps')]
    cx = x
    for name, kind in parts:
        pw = 70 if kind == 'stripe' else (24 if kind == 'gap' else 66)
        tone = 'blue' if kind == 'stripe' else ('card' if kind == 'gap' else 'violet')
        if hi and name in hi:
            tone = 'acc'
        o += box(cx, y, pw - 4, 46, tone) + t(cx + (pw - 4) / 2, y + 27, name, 7.4, bold=True)
        cx += pw
    return o

# ---------------------------------------------------------------- story
sc = (box(10, 12, 300, 128, 'card') + t(160, 30, 'Support: “show customer 1492’s orders”', 8.4, bold=True) +
      ''.join(fill(24 + k * 54, 46, 48, 40, 'red', rx=3) + t(48 + k * 54, 70, f'RG{k}', 7.6, 'ink', bold=True) for k in range(5)) +
      t(160, 104, 'every 10,000-row group has ids 1 … 2000', 7.6, 'ink2') + t(160, 124, 'read 50,000 rows to find 41', 8, 'red', bold=True) +
      box(330, 12, 300, 128, 'green') + t(480, 30, 'Same data, sorted by customer_id', 8.4, 'green', bold=True) +
      ''.join(fill(344 + k * 54, 46, 48, 40, 'green' if k == 3 else 'grey', rx=3) + t(368 + k * 54, 66, f'RG{k}', 7.6, 'ink', bold=True) + t(368 + k * 54, 79, ['1–404', '404–800', '…', '1205–1604', '1604–2000'][k], 6, 'ink2', mono=True) for k in range(5)) +
      t(480, 104, 'min/max says only RG3 can hold 1492', 7.6, 'ink2') + t(480, 124, 'read 10,000 rows', 8, 'green', bold=True))
scene_svg = scene('Unsorted, every row group of the ORC file contains customer ids from 1 to 2000, so all 50,000 rows are read to find 41 orders. Sorted by customer id, the min and max statistics show that only one row group can contain customer 1492, so 10,000 rows are read.', sc,
                  'ORC keeps <tspan font-weight="700" class="s-acc">min/max statistics</tspan> for every 10,000 rows. Good data order lets Hive skip the rest.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“The table is ORC. Why does a lookup still read everything?”</h2>
  <div class="story">
    <p class="narration">Every few minutes TiffinGo’s support tool asks Hive for one customer’s orders. The table is already ORC, the format everyone recommends, yet Hive’s counters show it reading all 50,000 rows to return 41. Kabir wants to understand what is inside an ORC file and how Hive decides what it can skip.</p>

{scene_svg}

K> Sir, I thought ORC was supposed to be fast. It reads every row for one customer!
A> ORC is fast at <b>skipping</b>, but it can only skip what its statistics rule out. It stores min and max for every column of every 10,000 rows. Our orders are in time order, so every group of 10,000 rows contains customers from 1 to 2000, and nothing can be ruled out.
R> So we sort the data by customer?
A> That is one answer; a <b>bloom filter</b> is another. Today we open a real ORC file with <code>hive --orcfiledump</code>, read its stripes, statistics, encodings and indexes, and then measure exactly how many rows Hive reads with each trick. All outputs are real, from Hive 4.2.1.
  </div>
</section>
'''

lv = '''
LEVELS> ORC at three levels
L1> A book with a contents page and an index
      <ul>
        <li>An ORC file stores each column separately and compresses it, so reading two columns does not touch the other seven.</li>
        <li>It also writes a “contents page”: for each column, the smallest and largest value, the count and the sum, for the whole file and for every block of 10,000 rows.</li>
        <li>When you ask for <code>amount &gt; 900</code> and the contents page says the maximum is 880, Hive skips the whole file without reading a single row.</li>
      </ul>
L2> The structure of an ORC file
      <ul>
        <li><b>Stripes:</b> large horizontal slices of rows (default target 64 MB). Each stripe has an <b>index</b> section, a <b>data</b> section (one or more streams per column) and a stripe footer.</li>
        <li><b>Row groups:</b> every 10,000 rows (<code>orc.row.index.stride</code>) the row index records min/max/count/sum per column and positions to jump to.</li>
        <li><b>File footer</b> (schema, stripe list, file statistics) and <b>postscript</b> (compression, footer length, ends with “ORC”) sit at the end, so a reader starts from the last bytes.</li>
        <li><b>Encodings:</b> integers use run-length encoding v2 (sorted ids compress to almost nothing); low-cardinality strings use a dictionary.</li>
        <li><b>Predicate pushdown:</b> with <code>hive.optimize.index.filter=true</code> (default) Hive passes WHERE conditions to the ORC reader, which skips files, stripes and row groups.</li>
      </ul>
L3> What helps skipping, measured in our lab
      <ul>
        <li>Statistics only help when values are <b>clustered</b>. Unsorted <code>customer_id</code>: every row group has min 1 max 2000 → 50,000 rows read. Sorted: 10,000.</li>
        <li><b>Bloom filters</b> (<code>orc.bloom.filter.columns</code>) answer “is this value possibly here?” per row group. With 1,000-row groups they cut a lookup from 50,000 to 30,000 rows, and grew the index from 890 bytes to 65,439 bytes.</li>
        <li>A smaller <code>orc.row.index.stride</code> alone did nothing for an unsorted column.</li>
        <li><code>amount &gt; 900</code> was eliminated before any task ran (0 splits): split generation read the file statistics.</li>
        <li>ORC is also the format for Hive ACID tables (Module 7) and enables vectorised reading in batches of rows.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>ORC (Optimized Row Columnar)</h2>
''' + def_block(
    '<b>ORC</b> is a self-describing, typed, columnar file format for Hadoop workloads. An ORC file consists of <b>stripes</b> of rows, each containing an <b>index</b> section (row-group statistics and stream positions, optionally bloom filters), the column <b>data</b> streams and a stripe footer, followed by a <b>file footer</b> (schema, stripe locations, column statistics) and a <b>postscript</b> (compression parameters and footer length). Light-weight encodings (run-length, dictionary) and a general-purpose codec (ZLIB, Snappy, LZ4, ZSTD) reduce size. Column statistics at file, stripe and row-group level, plus optional bloom filters, allow <b>predicate pushdown</b>: skipping data that cannot match a query’s filter.',
    'ORC stores a table column by column, compresses each column, and writes a summary (min, max, count, sum) for every 10,000 rows. When your WHERE clause cannot match a summary, Hive skips those rows entirely.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Stripe', 'A big block of rows (default target 64 MB) with its own index and data.'),
    ('Row group', 'Every 10,000 rows of a stripe; the unit of skipping.'),
    ('Postscript', 'The last bytes of the file: how to read the footer. Ends with “ORC”.'),
    ('Column statistics', 'count, hasNull, min, max, sum per column, per file / stripe / row group.'),
    ('RLE v2', 'Run-length encoding for integers: sorted ids shrink to a few bytes.'),
    ('Dictionary encoding', 'Store each distinct string once and refer to it by number.'),
    ('Predicate pushdown (PPD)', 'Passing WHERE conditions to the reader so it skips data.'),
    ('Bloom filter', 'A compact bit set that says “definitely not here” or “maybe here”.'),
]) + '''

  <h3>ORC table properties you will use</h3>
''' + table(['Property', 'Default', 'Effect'], [
    ['<code>orc.compress</code>', 'ZLIB (<code>hive.exec.orc.default.compress</code>)', 'NONE, ZLIB, SNAPPY, LZ4, ZSTD (Lesson 6.3)'],
    ['<code>orc.stripe.size</code>', '64 MB', 'Size of each stripe in bytes'],
    ['<code>orc.row.index.stride</code>', '10,000', 'Rows per row group (0 disables the row index)'],
    ['<code>orc.create.index</code>', 'true', 'Write row-group indexes'],
    ['<code>orc.bloom.filter.columns</code>', '(none)', 'Comma-separated columns that get bloom filters'],
    ['<code>orc.bloom.filter.fpp</code>', '0.05', 'Target false-positive probability'],
    ['<code>hive.optimize.index.filter</code>', 'true (our lab)', 'Push WHERE conditions into the ORC reader'],
], minw=680) + lv + '''
EXAM> “Explain the ORC file structure” is a classic. Draw stripes (index data, row data, stripe footer), then the file footer and postscript. Mention the three levels of statistics (file, stripe, row group of 10,000 rows), lightweight encodings plus compression, predicate pushdown and bloom filters, and that ORC is required for Hive ACID tables.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Ways ORC avoids reading data</h2>
''' + table(['Technique', 'Skips', 'Needs', 'Real result'], [
    ['Column projection', 'Columns not in the query', 'Nothing: ORC is columnar', 'Read only the streams of the columns you name'],
    ['File / stripe statistics', 'Whole files and stripes', 'A filter outside the min/max range', '<code>amount &gt; 900</code>: 0 splits, 0 rows'],
    ['Row-group index', 'Groups of 10,000 rows', 'Values clustered in the file', '<code>amount &gt; 870</code>: 30,000 of 50,000 rows'],
    ['Sorting the data', 'Makes the above work for a column', '<code>ORDER BY</code> / <code>SORT BY</code> on write', 'customer lookup: 10,000 instead of 50,000'],
    ['Bloom filter', 'Row groups that cannot hold a value', '<code>orc.bloom.filter.columns</code>; works for = and IN', 'customer lookup: 30,000 instead of 50,000'],
    ['Partitions / buckets', 'Folders and files (Module 5)', 'Filter on the partition / bucket column', '1,621 instead of 50,000'],
], minw=720) + '''
WARN> Bloom filters cost space and write time, and help only equality lookups (<code>=</code>, <code>IN</code>) on high-cardinality columns. For ranges, sort the data instead. Add them to the columns your lookups actually use, not to every column.
</section>
'''

ppd = capf('l62_ppd.txt').split('\n')
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Open an ORC file, then make Hive skip</h2>
  <p>All outputs are real, from the Hive 4.2.1 lab (database <code>tiffingo</code>). <code>f_orc</code> is the 50,000 orders written with CTAS in Lesson 6.1.</p>
''' + stepper([
    ('Step 1 · Look inside the file',
     code('bash', 'Terminal', "hive --orcfiledump /opt/hive/data/warehouse/tiffingo.db/f_orc/000000_0", capf('l62_dump.txt').split('…')[0].rstrip()),
     'The dump starts at the end of the file: the postscript gives the compression (ZLIB, 256 KB compression chunks) and the footer gives the schema and row count. “File Version 0.12 … by ORC Java 2.1.2” tells you which writer produced it; readers use this to handle old files.'),
    ('Step 2 · Statistics and bytes per column',
     code('bash', 'Terminal', "# … same dump, File Statistics section", 'File Statistics:\n' + capf('l62_dump.txt').split('File Statistics:')[1].split('…')[0].rstrip()),
     'Column 0 is the whole row (struct); columns 1–9 follow the schema. Look at <b>bytesOnDisk</b>: order_id, a sorted sequence, needs only <b>161 bytes</b> for 50,000 values, while the random customer_id needs 80,971. order_ts is the biggest column. These min/max/sum values are what predicate pushdown compares with your WHERE clause.'),
    ('Step 3 · Stripes and encodings',
     code('bash', 'Terminal', "# … same dump, Stripes section", '\n'.join(capf('l62_dump.txt').split('Stripes:')[1].split('\n')[:14]).rstrip() + '\n…\nFile length: 437536 bytes\nFile raw data size: 24650000 bytes'),
     '50,000 rows fit in one stripe (data 435,805 bytes, index 890 bytes). Integer columns use <code>DIRECT_V2</code> (run-length encoding v2), and the strings city, payment and status use <code>DICTIONARY_V2</code> with 8, 4 and 3 distinct values: each row stores a small number, not the text. Hive estimates the raw data at 24.6 MB; on disk it takes 0.44 MB.'),
    ('Step 4 · Row-group indexes: where skipping happens',
     code('bash', 'Terminal', "hive --orcfiledump --rowindex 2,7 …/f_orc/000000_0      # columns 2 = customer_id, 7 = amount", 'Row group indices for column 2:\n  Entry 0: count: 10000 hasNull: false min: 1 max: 2000 …\n  Entry 1: count: 10000 hasNull: false min: 1 max: 2000 …\n  … (entries 2–4 also 1 … 2000)\nRow group indices for column 7:\n  Entry 0: count: 10000 hasNull: false min: 40 max: 840 …\n  Entry 1: count: 10000 hasNull: false min: 40 max: 880 …\n  Entry 2: count: 10000 hasNull: false min: 40 max: 840 …\n  Entry 3: count: 10000 hasNull: false min: 40 max: 880 …\n  Entry 4: count: 10000 hasNull: false min: 40 max: 880 …'),
     'One entry per 10,000 rows. For customer_id every group covers the full range 1–2000, so no customer can ever be ruled out. For amount, groups 0 and 2 never go above 840: a filter <code>amount &gt; 870</code> can skip them.'),
    ('Step 5 · Predicate pushdown in action (and switched off)',
     code('sql', 'Beeline', "SET hive.tez.exec.print.summary=true;\nSELECT COUNT(*) AS n FROM f_orc WHERE amount > 870;\nSELECT COUNT(*) AS n FROM f_orc WHERE amount > 900;\n\nSET hive.optimize.index.filter=false;    -- turn PPD off and repeat", '\n'.join(ppd[8:12]) + '\n\n' + capf('l62_ppd_off.txt')),
     'Exactly as the index predicted: 3 of 5 row groups read (30,000 rows) for 4 matching orders. For <code>amount &gt; 900</code> the file maximum is 880, so Hive created <b>no splits at all</b>. With pushdown off, both queries read all 50,000 rows and return the same answers, only slower.'),
    ('Step 6 · The customer lookup: unsorted vs sorted',
     code('sql', 'Beeline', "CREATE TABLE orders_sorted STORED AS ORC AS\n  SELECT * FROM orders ORDER BY customer_id;\n\nSELECT COUNT(*) AS n FROM f_orc         WHERE customer_id = 1492;\nSELECT COUNT(*) AS n FROM orders_sorted WHERE customer_id = 1492;", '\n'.join(ppd[0:4])),
     'Same 41 orders. Sorted, each row group covers a narrow range of customers (real min–max: 1–404, 404–800, 800–1205, 1205–1604, 1604–2000), so only the group whose min–max includes 1492 is read. Sorting is free at query time but costs a sort when writing, and you can sort by only one order, so pick the column your filters use most.'),
    ('Step 7 · Bloom filters for lookups on unsorted data',
     code('sql', 'Beeline', "CREATE TABLE orders_stride STORED AS ORC\n  TBLPROPERTIES ('orc.row.index.stride'='1000') AS SELECT * FROM orders;\nCREATE TABLE orders_bloom STORED AS ORC\n  TBLPROPERTIES ('orc.bloom.filter.columns'='customer_id',\n                 'orc.row.index.stride'='1000') AS SELECT * FROM orders;\n\nSELECT COUNT(*) AS n FROM orders_stride WHERE customer_id = 1492;\nSELECT COUNT(*) AS n FROM orders_bloom  WHERE customer_id = 1492;\n\n$ hive --orcfiledump --rowindex 2 …/orders_bloom/000000_0",
          '\n'.join(ppd[4:8]) + '\n\n  Stripe: offset: 3 data: 435805 rows: 50000 tail: 186 index: 65439\n    Stream: column 2 section BLOOM_FILTER_UTF8 start: 1508 length 59891\n    Bloom filters for column 2:\n      Entry 0: numHashFunctions: 7 bitCount: 9600 popCount: 4199 loadFactor: 0.4374 …'),
     'Smaller row groups alone changed nothing (still 1–2000 in each). With a bloom filter per 1,000-row group, Hive could prove that 20 of the 50 groups do not contain customer 1492 and read 30,000 rows. The customer has 41 orders spread across the month, so most groups “maybe” contain it. The price: the index grew from 890 bytes to 65,439 bytes.'),
    ('Step 8 · Stripe size and vectorised reading',
     code('sql', 'Beeline', "CREATE TABLE orders_smallstripe STORED AS ORC\n  TBLPROPERTIES ('orc.stripe.size'='131072') AS SELECT * FROM orders;\n$ hive --orcfiledump …/orders_smallstripe/000000_0 | grep 'Stripe:'\n\nEXPLAIN VECTORIZATION SUMMARY SELECT city, SUM(amount) FROM f_orc GROUP BY city;",
          '  Stripe: offset: 3 data: 46148 rows: 5000 tail: 159 index: 325\n  Stripe: offset: 46635 data: 46154 rows: 5000 tail: 158 index: 325\n  … (10 stripes of 5,000 rows)\nFile length: 467324 bytes      (one 64 MB-target stripe: 437536)\n\nPLAN VECTORIZATION:\n  enabled: true\n  enabledConditionsMet: [hive.vectorized.execution.enabled IS true]\n…\n            Execution mode: vectorized\n            Map Vectorization:\n                enabled: true\n                enabledConditionsMet: hive.vectorized.use.vectorized.input.format IS true'),
     'Small stripes made 10 stripes and a 7% bigger file (more indexes and footers, less compression context). Production keeps the 64 MB default so a task reads big sequential blocks. ORC also feeds Hive’s <b>vectorised</b> engine, which processes columns in batches of 1,024 rows instead of one row at a time (Module 8).'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('$ hive --orcfiledump …/f_orc/000000_0', W), ('File Version: 0.12 with ORC_14 by ORC Java 2.1.2', G), ('Rows: 50000   Compression: ZLIB', G), ('Stripe: offset: 3 data: 435805 rows: 50000', G), ('File length: 437536 bytes', G)], size=7.6),
    term([('Column 1 (order_id)    bytesOnDisk: 161', G), ('Column 2 (customer_id) bytesOnDisk: 80971', Y), ('Column 4 (city)  DICTIONARY_V2[8]', G), ('Column 7 (amount) min: 40 max: 880', G)], size=7.6),
    term([('> … WHERE amount > 870;', W), ('| 4 |   RECORDS_IN_Map_1: 30000', G), ('> … WHERE amount > 900;', W), ('| 0 |   RAW_INPUT_SPLITS_Map_1: 0', G)]),
    term([('> … f_orc WHERE customer_id = 1492;', W), ('| 41 |  RECORDS_IN 50000', RD), ('> … orders_sorted WHERE customer_id = 1492;', W), ('| 41 |  RECORDS_IN 10000', G)], size=7.6),
    term([('> … orders_stride WHERE customer_id = 1492;', W), ('| 41 |  RECORDS_IN 50000', Y), ('> … orders_bloom  WHERE customer_id = 1492;', W), ('| 41 |  RECORDS_IN 30000', G), ('  index: 890 → 65,439 bytes', Y)], size=7.6),
]
def rgs(y, labels, hi):
    return ''.join(box(20 + k * 64, y, 60, 40, 'green' if k in hi else 'card') + t(50 + k * 64, y + 16, f'RG{k}', 7.8, 'ink', bold=True) + t(50 + k * 64, y + 31, labels[k], 6.6, 'ink2', mono=True) for k in range(5))
B1 = [
    t(180, 22, 'Read from the end of the file', 9.4, bold=True) + orcfile(hi={'Postscript', 'File footer'}) + arrow(320, 100, 230, 100, 'acc', 2) + t(180, 120, 'postscript → footer → stripe list → stripes', 7.8, 'ink2', mono=True) + cap('The footer holds schema, stripes and statistics.', '', 'blue', y=150, h=34),
    t(180, 22, 'Inside a stripe', 9.4, bold=True) + box(20, 40, 90, 70, 'violet') + t(65, 60, 'index', 8.2, bold=True) + t(65, 76, 'min/max per', 7, 'ink2') + t(65, 88, '10,000 rows', 7, 'ink2') +
    box(114, 40, 170, 70, 'blue') + t(199, 60, 'data streams', 8.2, bold=True) + t(199, 76, 'col 1 · col 2 · … · col 9', 7, 'ink2', mono=True) + t(199, 90, 'RLE v2 · dictionary · ZLIB', 7, 'ink2', mono=True) +
    box(288, 40, 52, 70, 'card') + t(314, 72, 'footer', 7.6, bold=True) + cap('Each column is its own stream: read only what you need.', '', 'blue', y=150, h=34),
    t(180, 22, 'amount > 870: compare with each max', 9.4, bold=True) + rgs(46, ['max 840', 'max 880', 'max 840', 'max 880', 'max 880'], {1, 3, 4}) + t(180, 112, 'file max 880 → amount > 900 skips the file', 7.8, 'green', mono=True, bold=True) + cap('Groups 0 and 2 can never match.', '', 'green', y=150, h=34),
    t(180, 22, 'Sorted data → narrow min/max', 9.4, bold=True) + rgs(46, ['1–404', '404–800', '800–1205', '1205–1604', '1604–2000'], {3}) + cap('Only RG3 can hold customer 1492.', 'Unsorted, every group is 1–2000.', 'green', y=150, h=46),
    t(180, 22, 'Bloom filter: “definitely not here”', 9.4, bold=True) + ''.join(fill(20 + k * 6.4, 50, 5, 30, 'green' if (k * 7) % 5 < 3 else 'grey', rx=1) for k in range(50)) + t(180, 98, '50 groups of 1,000 rows: 30 maybe, 20 no', 7.8, 'ink2', mono=True) + cap('No false negatives, some false positives.', 'Works for = and IN, not ranges.', 'blue', y=150, h=46),
]
see_caps = ['orcfiledump shows the writer, compression, row count and stripes.',
            'Sorted ids take 161 bytes; small text columns use dictionaries.',
            'Pushdown read 30,000 rows for amount > 870 and nothing for amount > 900.',
            'Sorting by customer cut a lookup from 50,000 rows to 10,000.',
            'A bloom filter cut the unsorted lookup to 30,000 rows.']
behind_caps = ['A reader starts at the postscript, reads the footer, then jumps to the stripes it needs.',
               'Each stripe has index, data and footer; each column is a separate compressed stream.',
               'The reader compares the filter with each row group’s min and max and skips impossible groups.',
               'When data is sorted, each group covers a narrow range, so most groups are ruled out.',
               'Each group’s bloom filter can prove a value is absent; groups that might contain it are read.']
two = anim_two('Inside ORC', 'Footer, stripes, statistics and skipping', 'Real dump and Beeline output', 'What the ORC reader does', see, B1, see_caps, behind_caps)

# ---- scenario 1: daily table sorted at write time
w1 = (t(180, 22, 'Nightly load of yesterday’s orders', 9.4, bold=True) + t(180, 56, 'support looks up by customer all day', 8.4, 'ink2') + cap('Choose the write order for the reads.', '', 'blue', y=150, h=34))
w2 = (t(180, 22, 'Write sorted', 9.4, bold=True) + t(180, 54, "INSERT OVERWRITE … PARTITION (order_date='…')", 7.8, 'ink', mono=True) + t(180, 70, 'SELECT … DISTRIBUTE BY customer_id SORT BY customer_id;', 7.8, 'ink', mono=True) + cap('Each file is sorted by customer.', '', 'green', y=150, h=34))
w3 = (t(180, 22, 'Lookups skip row groups', 9.4, bold=True) + rgs(46, ['1–404', '404–800', '800–1205', '1205–1604', '1604–2000'], {3}) + cap('Real lab: 10,000 of 50,000 rows read.', '', 'green', y=150, h=34))
w4 = (t(180, 22, 'Bonus: better compression', 9.4, bold=True) + t(180, 56, 'sorted ids → long runs → RLE shrinks them', 8.2, 'ink2') + cap('order_id (sorted) took 161 bytes for 50,000 values.', '', 'blue', y=150, h=34))
w5 = (t(180, 22, 'Trade-off', 9.4, 'acc', bold=True) + t(180, 56, 'one sort order per file; sorting costs write time', 8.2, 'ink2') + cap('Sort by the most common filter column.', '', 'amber', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Sort at write time for fast lookups',
              'A table read by customer many times a day should be written sorted by customer. Counts are real.',
              'Sorted writes', 'Writing each partition sorted by customer makes ORC row-group statistics selective, so lookups read one group', [w1, w2, w3, w4, w5],
              ['The table is loaded once a night and read by customer all day.',
               'Write it sorted with DISTRIBUTE BY and SORT BY.',
               'Lookups then skip most row groups.',
               'Sorted columns also compress better.',
               'You get one sort order per file, so choose it carefully.'],
              hid='scenario-sorted')

# ---- scenario 2: bloom filter decision
b1 = (t(180, 22, 'Fraud team: “all events for this card”', 9.4, bold=True) + t(180, 56, 'card ids are random; data is sorted by time', 8.2, 'ink2') + cap('Sorting by card would hurt time queries.', '', 'amber', y=150, h=34))
b2 = (t(180, 22, 'Add a bloom filter on card_id', 9.4, bold=True) + t(180, 56, "TBLPROPERTIES ('orc.bloom.filter.columns'='card_id')", 7.8, 'ink', mono=True) + cap('Time order stays; lookups skip many groups.', '', 'green', y=150, h=34))
b3 = term([('> … orders_bloom WHERE customer_id = 1492;', W), ('| 41 |  RECORDS_IN 30000 (was 50000)', G), ('  BLOOM_FILTER_UTF8 stream: 59,891 bytes', Y)], label='real output · Hive 4.2.1 (customer_id as the example)')
b4 = (t(180, 22, 'When it helps most', 9.4, bold=True) + t(180, 56, 'a value appears in few row groups', 8.4, 'ink2') + t(180, 74, '(rare ids, recent events, error codes)', 8.2, 'ink2') + cap('A customer with orders all month: modest gain.', '', 'blue', y=150, h=34))
b5 = (t(180, 22, 'Tuning', 9.4, 'acc', bold=True) + t(180, 56, 'orc.bloom.filter.fpp (default 0.05) · stride', 8.2, 'ink2', mono=True) + cap('Lower fpp = bigger filters, fewer false hits.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'A bloom filter for a column you cannot sort by',
              'When the data must stay sorted by time, a bloom filter still speeds up lookups on another column. Result is real.',
              'Bloom filters', 'A bloom filter on an id column lets ORC skip row groups that cannot contain the id, at the cost of a larger index', [b1, b2, b3, b4, b5],
              ['Lookups on a column the data is not sorted by.',
               'Add a bloom filter on that column.',
               'In our lab: 30,000 rows read instead of 50,000.',
               'Bloom filters shine when a value appears in only a few groups.',
               'Tune the false-positive rate and stride.'],
              hid='scenario-bloom')

# ---- scenario 3: debugging a slow ORC query
d1 = (t(180, 22, '“ORC table, still slow” checklist', 9.4, bold=True) + t(180, 56, 'measure first: RECORDS_IN, INPUT_FILES', 8.4, 'ink', mono=True) + cap('Know how much was really read.', '', 'blue', y=150, h=34))
d2 = (t(180, 22, '1 · Is pushdown on?', 9.4, bold=True) + t(180, 56, 'SET hive.optimize.index.filter;  → true', 8.4, 'ink', mono=True) + cap('Off: 50,000 rows for every filter (real).', '', 'amber', y=150, h=34))
d3 = (t(180, 22, '2 · Can statistics rule anything out?', 9.4, bold=True) + t(180, 56, 'orcfiledump --rowindex N: min/max per group', 8, 'ink', mono=True) + cap('All groups 1–2000? Sort or add a bloom filter.', '', 'blue', y=150, h=34))
d4 = (t(180, 22, '3 · Is the filter pushable?', 9.4, bold=True) + t(180, 56, 'col = v, col > v, IN, BETWEEN, IS NULL: yes', 8, 'ink2', mono=True) + t(180, 74, 'upper(col) = v, col LIKE \'%x\': no', 8, 'red', mono=True) + cap('Functions on the column hide it from the reader.', '', 'amber', y=150, h=34))
d5 = (t(180, 22, '4 · Files and stripes healthy?', 9.4, 'acc', bold=True) + t(180, 56, 'many tiny files or stripes → Lesson 5.4', 8.4, 'ink2') + cap('Fix layout, then measure again.', '', 'green', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Debugging a slow ORC query',
              'A practical checklist that uses the tools from this lesson.',
              'ORC tuning checklist', 'Measure rows read, confirm pushdown is on, inspect row-group statistics, keep filters pushable and check file layout', [d1, d2, d3, d4, d5],
              ['Start from the counters: how many rows were read?',
               'Make sure predicate pushdown is enabled.',
               'Inspect min/max per row group with orcfiledump.',
               'Write filters the reader can evaluate.',
               'Check for small files and tiny stripes.'],
              hid='scenario-debug')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>How the ORC reader decides what to read</h2>
  <p>Left: real orcfiledump and Beeline output. Right: what the ORC reader does.</p>
''' + two + '''
  <p>Three live scenarios follow: sorting at write time, a bloom filter decision, and a tuning checklist.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>ORC at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'ORC', 13, 'green', bold=True, mono=True) + t(60, 58, 'warehouse', 7.4, 'ink2'),
    '1. The default for Hive warehouses',
    'Large Hive warehouses store curated tables in ORC with ZLIB or ZSTD; many vendor distributions make ORC the default for managed tables.',
    ['Curated data', '*STORED AS ORC', 'Fast scans']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'ACID', 13, 'blue', bold=True, mono=True) + t(60, 58, 'updates', 7.4, 'ink2'),
    '2. Transactional tables',
    'Hive’s UPDATE, DELETE and MERGE work on ORC tables: base and delta files are ORC, and compaction rewrites them (Module 7).',
    ['Changes', '*ORC deltas', 'Compaction']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'bloom', 12, 'violet', bold=True, mono=True) + t(60, 58, 'lookups', 7.4, 'ink2'),
    '3. Point lookups on big tables',
    'Telecom and payments teams add bloom filters on phone numbers, card ids or transaction ids so investigation queries skip most of the data.',
    ['Id lookup', '*bloom filter', 'Few row groups']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'SORT BY', 11, 'acc', bold=True, mono=True) + t(60, 58, 'write order', 7.4, 'ink2'),
    '4. Layout tuned for queries',
    'Teams write partitions sorted by the main filter column (customer, device, store) so ORC statistics skip most row groups.',
    ['Nightly load', '*sorted write', 'Selective stats']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'Spark/Trino', 9, 'acc', bold=True) + t(60, 58, 'read ORC too', 7.4, 'ink2'),
    '5. Shared with other engines',
    'Spark, Trino and Presto read ORC natively and use the same statistics and bloom filters, so a well-written ORC table speeds up every engine.',
    ['ORC files', '*same statistics', 'Any engine']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> read Lesson <a href="../01-text-sequence-and-avro/">6.1</a> (formats) and partition pruning (<a href="../../05-partitioning-and-bucketing/01-partitioning/">5.1</a>).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
