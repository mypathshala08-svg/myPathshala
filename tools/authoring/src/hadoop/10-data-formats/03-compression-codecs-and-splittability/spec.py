import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()


def section(text, start, end=None):
    """Lines of a transcript from the line starting with `start` up to (not including) `end`."""
    lines = text.strip().split('\n')
    i = next(n for n, l in enumerate(lines) if l.startswith(start))
    j = next((n for n, l in enumerate(lines) if end and l.startswith(end)), len(lines))
    return '\n'.join(lines[i:j])


TX = rd('tx103.txt')

META = dict(
    module='10-data-formats', lesson='03-compression-codecs-and-splittability', n='10.3',
    module_label='Module 10 · Data formats and compression',
    title='Compression codecs and splittability',
    desc='Hadoop compression codecs measured on a real Hadoop 3.5.0 cluster: DEFLATE, gzip, bzip2, LZ4, Snappy and Zstandard on 194 MB of CSV (ratio 16.5% to 42%, compress 0.7 s to 24 s). Splittability shown live: with 8 MB blocks a .gz file gave 1 split, .bz2 gave 4, plain text 24. Map output compression cut the shuffle from 60 MB to 2.8 MB (Snappy) and 13 KB (Zstandard). Job output compression, CompressionCodecFactory, native libraries, choosing a codec. Python simulations, quiz and interview scenarios.',
    og_desc='gzip gave one map task, bzip2 gave four. Measure six codecs and compress a shuffle from 60 MB to 13 KB.',
    minutes=26, level='Intermediate',
    lead='Compression saves disk, network and I/O, but every codec trades size against CPU, and only some can be split across map tasks. This lesson measures six Hadoop codecs on the same file, shows on a real cluster which compressed files Hadoop can split, and compresses the shuffle and the job output.',
    chips=['6 codecs measured', 'Splits: .gz 1, .bz2 4', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Compare codecs on a CSV sample',
    intro='<p>Python ships three of the algorithms Hadoop uses: <code>zlib</code> (DEFLATE, the algorithm inside gzip), <code>bz2</code> (bzip2) and <code>lzma</code> (xz, not a Hadoop codec but a useful “maximum squeeze” reference). Snappy, LZ4 and Zstandard need extra packages, so the lab numbers stand in for them.</p>',
    code='''import zlib, bz2, lzma, random, time
random.seed(1)
items = {"chai": 15, "coffee": 20, "samosa": 18, "vada pav": 20, "poha": 25, "idli": 30, "dosa": 45, "thali": 80}
rows = []
for oid in range(1, 20001):
    item = random.choice(list(items))
    rows.append(f"{oid},S{random.randint(1, 2000):04d},2026-09-{random.randint(1, 30):02d} {random.randint(8, 20):02d}:{random.randint(0, 59):02d},{item},{items[item]}")
data = ("\\n".join(rows) + "\\n").encode()
print(f"original {len(data):,} bytes")

for name, compress, decompress in [("zlib (gzip)", zlib.compress, zlib.decompress),
                                   ("bz2", bz2.compress, bz2.decompress),
                                   ("lzma (xz)", lzma.compress, lzma.decompress)]:
    t0 = time.perf_counter(); c = compress(data); t1 = time.perf_counter()
    assert decompress(c) == data
    t2 = time.perf_counter()
    print(f"{name:12} {len(c):>8,} bytes  {100 * len(c) / len(data):5.1f}%  compress {1000 * (t1 - t0):6.1f} ms  decompress {1000 * (t2 - t1):5.1f} ms")
''',
    anno=[
        ('    assert decompress(c) == data', 'Compression is lossless: decompressing gives back exactly the original bytes.'),
        ('for name, compress, decompress in [("zlib (gzip)", zlib.compress, zlib.decompress),', 'gzip and Hadoop’s DefaultCodec both use DEFLATE (zlib); gzip only adds a small header and trailer.'),
    ],
    tasks=[
        dict(label='1 · Ratio vs speed', hint='Press <b>Run</b>. Which is smallest? Which is fastest? It matches the lab: bzip2 squeezes harder but is slower.', code=None),
        dict(label='2 · Compression levels', hint='<b>Predict first:</b> is level 9 much smaller than the default level 6? Is it worth the extra time? Then check the output.',
             code='''import zlib, time, random
random.seed(1)
data = "".join(f"{i},S{random.randint(1, 2000):04d},chai,15\\n" for i in range(50000)).encode()
for level in [1, 6, 9]:
    t0 = time.perf_counter(); c = zlib.compress(data, level); ms = 1000 * (time.perf_counter() - t0)
    print(f"level {level}: {len(c):>8,} bytes ({100 * len(c) / len(data):.1f}%) in {ms:.1f} ms")
'''),
        dict(label='3 · How many map tasks?', hint='Plan splits for a file: one split per block if the codec is splittable, otherwise one split for the whole file. Try the lab files (8 MB blocks).',
             code='''import math
BLOCK = 8 * 1024 * 1024
files = [("orders_x10.csv", 194_186_990, True), ("orders_x10.csv.gz", 45_696_989, False),
         ("orders_x10.csv.bz2", 31_984_098, True), ("orders_x10.csv.zst", 50_199_622, False),
         ("orders_x10.csv.snappy", 81_629_934, False)]
for name, size, splittable in files:
    blocks = math.ceil(size / BLOCK)
    maps = blocks if splittable else 1
    print(f"{name:22} {blocks:3} blocks -> {maps:3} map task(s)")
'''),
        dict(label='4 · Data locality', hint='A non-splittable file is read by one map. At best that map runs next to its first block; what fraction of the file is read over the network?',
             code='''import math
for size_gb in [1, 10, 50]:
    blocks = math.ceil(size_gb * 1024 / 128)
    remote = (blocks - 1) / blocks
    print(f"{size_gb:3} GB gzip: {blocks:4} blocks, 1 map, {100 * remote:.0f}% read from other nodes")
'''),
        dict(label='5 · Spot the error', hint='This reader tries to start decompressing a gzip (DEFLATE) stream in the middle, as a second map task would. Run it, then explain the error.',
             code='''import zlib
data = ("1,S0001,chai,15\\n" * 5000).encode()
c = zlib.compress(data)
middle = c[len(c) // 2:]
print(zlib.decompress(middle)[:40])
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: six codecs, splits, shuffle and output',
    intro='<p>Use the Module 8 lab and the Module 10 setup from Lesson 10.1 (<code>get_jars.sh</code> and <code>formats_env.sh</code>, which put the extra jars on the classpath). <code>codecs_lab.sh</code> builds <code>orders_x10.csv</code> from Module 9\'s <code>student_orders.csv</code> (copied to <code>/tmp/mr9</code>), runs CodecBench, loads the compressed files with 8 MB blocks and runs the jobs. It takes about 12 minutes; start it in the background if your terminal times out.</p>',
    items=[
        dict(title='Compress one file with every Hadoop codec', file='CodecBench.java',
             cmd=rd('java/CodecBench.java') + '\n// Inside the namenode container, in /tmp/mr10 (with the other Module 10 classes):\n//   javac -cp $(hadoop classpath):$HADOOP_CLASSPATH -d classes *.java && jar cf mr10.jar -C classes .\n//   java -Djava.library.path=/opt/hadoop/lib/native \\\n//        -cp mr10.jar:$(hadoop classpath):$(ls /opt/hadoop/share/hadoop/tools/lib/lz4-java-*.jar) \\\n//        CodecBench orders_x10.csv',
             output=section(TX, 'codec ', '== 2.'),
             note='Real output, default compression levels, one thread. Times vary with load (a quieter run took 11.9 s for deflate and 14.4 s for bzip2); sizes do not. lz4-java sits in share/hadoop/tools/lib, which is not on the default classpath: without it, LZ4 fails with NoClassDefFoundError: net/jpountz/lz4/LZ4Factory.'),
        dict(title='Splits, shuffle compression and output compression', file='codecs_lab.sh',
             cmd=rd('codecs_lab.sh') + '\n# Run inside the namenode container:  bash /tmp/mr10/codecs_lab.sh',
             output=TX.strip(),
             note='Real output. All five input files give the same answer (chai=1496690); only bzip2 was split. The Snappy and Zstandard shuffles moved 21× and 4,500× fewer bytes.'),
    ],
)

TRACE = dict(
    heading='Why gzip can\'t be split',
    intro='<p>Compress a short file and try to decompress from the start and from the middle. Watch which one works.</p>',
    code='''import zlib
data = b"1,chai,15\\n2,dosa,45\\n3,poha,25\\n" * 3
c = zlib.compress(data)
half = len(c) // 2
whole = zlib.decompress(c)
ok_from_start = whole == data
try:
    zlib.decompress(c[half:])
    ok_from_middle = True
except zlib.error:
    ok_from_middle = False
print(ok_from_start, ok_from_middle)
''',
    notes={3: 'Compress :: One continuous DEFLATE stream; later bytes depend on earlier ones.',
           8: 'Middle :: Starting mid-stream fails: there is no header or marker to resynchronise on.',
           12: 'Result :: That is why a .gz file is always one input split.'},
)

WORKED_INTRO = 'Three compression decisions: storage saved, shuffle saved, and choosing a codec by reading pattern.'
EXAMPLES = [
    dict(level='b', tag='Storage · savings', title='How much disk does a codec save?',
         problem='<p>The canteen keeps 2 TB of raw CSV per year in HDFS with replication 3. Using our measured ratios (gzip 23.5%, Zstandard 25.9%, Snappy 42%), how much raw disk does each codec need?</p>',
         inp='2 TB × 3 replicas',
         approach=['Raw disk = data × replication.',
                   'Compressed = raw × ratio.',
                   'Compare.'],
         code='''raw = 2 * 3
for codec, ratio in [("none", 1.0), ("gzip", 0.235), ("zstd", 0.259), ("snappy", 0.42)]:
    print(f"{codec:7} {raw * ratio:5.2f} TB of disk")
''', notes={3: 'Ratio :: The ratios come from CodecBench on our CSV; your data will differ.'},
         tryit='Ratios depend on the data: CSV with few distinct values compresses well; already compressed images hardly at all.'),
    dict(level='i', tag='Shuffle · network', title='What does map output compression save per day?',
         problem='<p>A daily job without a combiner shuffles 600 GB of map output across a 1 Gbit/s (125 MB/s) network shared by 20 nodes. If Snappy reduces it to 5% (our lab gave 4.7%), how much network time per node is saved?</p>',
         inp='600 GB · 20 nodes · 125 MB/s each · 5%',
         approach=['Bytes per node = total / nodes.',
                   'Time = bytes / bandwidth.',
                   'Compare plain and compressed.'],
         code='''per_node_mb = 600 * 1024 / 20
plain = per_node_mb / 125
snappy = per_node_mb * 0.05 / 125
print(f"plain {plain / 60:.1f} min, snappy {snappy / 60:.1f} min per node")
''', notes={2: 'Bandwidth :: Every node sends and receives at about link speed in the shuffle.'},
         tryit='Real map output is less repetitive than our sorted (item, amount) pairs; 20–40% is a more typical Snappy ratio. Still a big win.'),
    dict(level='a', tag='Design · choice', title='Pick a codec for three datasets',
         problem='<p>Choose a format and codec for: (a) a 40 GB daily log file that jobs read many times, (b) map output of a heavy join job, (c) 5 years of transactions kept only for audits.</p>',
         inp='3 use cases',
         approach=['Read often and in parallel: splittable, fast to read.',
                   'Shuffle: fastest codec.',
                   'Cold: smallest size, CPU spent once.'],
         code='''choices = {
    "daily log, read often": "convert to Parquet/ORC with Snappy or ZSTD (splittable, columnar)",
    "join map output": "mapreduce.map.output.compress=true with Snappy, LZ4 or ZSTD",
    "5-year audit archive": "ORC/Parquet with ZSTD at a high level, or bzip2 if it must stay text",
}
for use, pick in choices.items():
    print(f"{use:22} -> {pick}")
''', notes={1: 'Rule :: Match the codec to how the data will be read, not just to its size.'},
         tryit='If the log must stay plain text, write it as many files of about 128–256 MB, each gzip-compressed: one map per file still gives parallelism.'),
]

QUIZ = mix([
    dict(q='Which built-in Hadoop codec is splittable?', options=['gzip', 'bzip2', 'Snappy', 'Zstandard'], answer=1,
         why='BZip2Codec implements SplittableCompressionCodec; our .bz2 file gave 4 splits.'),
    dict(q='A 6-block .gz file in HDFS is read by how many map tasks?', options=['6', '1', '3', 'One per reducer'], answer=1,
         why='Real lab: “number of splits:1” for the 6-block gzip file.'),
    dict(q='How does Hadoop know a file is gzip-compressed?', options=['It reads the NameNode metadata', 'CompressionCodecFactory matches the file extension (.gz)', 'The user must pass -D codec', 'It tries every codec'], answer=1,
         why='Rename the file without .gz and Hadoop reads raw compressed bytes as text.'),
    dict(q='Which codec compressed our CSV the most?', options=['Snappy', 'bzip2 (16.5%)', 'LZ4', 'gzip (42%)'], answer=1,
         why='bzip2 16.5%, gzip 23.5%, ZSTD 25.9%, LZ4 37.8%, Snappy 42%.'),
    dict(q='Which property enables map output compression?', options=['mapreduce.output.fileoutputformat.compress', 'mapreduce.map.output.compress', 'dfs.compress', 'io.compression.codecs.enable'], answer=1,
         why='Plus mapreduce.map.output.compress.codec to pick the codec.'),
    dict(q='Why are Snappy and LZ4 popular for the shuffle?', options=['They give the smallest files', 'They are very fast to compress and decompress', 'They are splittable', 'They need no CPU'], answer=1,
         why='0.7 s to compress 194 MB vs 14.5 s for gzip in our lab.'),
    dict(q='Why can Parquet use Snappy and still be split?', options=['Snappy is splittable in Parquet', 'Parquet compresses each page separately, inside row groups', 'Parquet files are never split', 'HDFS splits it'], answer=1,
         why='Containers compress in pieces; the file structure, not the codec, gives the split points.'),
    dict(q='What does hadoop checknative show?', options=['Which DataNodes are alive', 'Whether native libraries (libhadoop, zlib, zstd, bzip2…) are loaded', 'Java version', 'The block size'], answer=1,
         why='In our lab: hadoop, zlib, zstd, bzip2 true; openssl and ISA-L false.'),
])

REVISION = [
    'Compression trades CPU for less disk, network and I/O. Ratio and speed vary hugely between codecs.',
    'Lab, 194 MB CSV: bzip2 16.5% (24 s), gzip 23.5% (14.5 s), ZSTD 25.9% (1.4 s), LZ4 37.8% (0.7 s), Snappy 42% (0.7 s).',
    'Only <b>bzip2</b> is splittable among built-ins. Lab with 8 MB blocks: plain 24 splits, .gz/.zst/.snappy 1, .bz2 4.',
    '<code>CompressionCodecFactory</code> picks the codec by extension; <code>hdfs dfs -text</code> decompresses for you.',
    'Map output: <code>mapreduce.map.output.compress=true</code> + Snappy/LZ4/ZSTD. Lab shuffle 60 MB → 2.8 MB → 13 KB.',
    'Job output: <code>mapreduce.output.fileoutputformat.compress=true</code> + codec → <code>part-r-00000.gz</code>.',
    'Best for data read often: Parquet/ORC (or SequenceFile/Avro) with compression inside: compact AND splittable.',
]
FAQ = [
    ('Which compression formats are splittable in Hadoop?', 'Among the codecs shipped with Hadoop only bzip2 (BZip2Codec) is splittable. gzip, DEFLATE, Snappy, LZ4 and Zstandard files are each processed by a single map task. LZO becomes splittable only after building an index with the separate hadoop-lzo project. Container formats such as SequenceFile, Avro, Parquet and ORC remain splittable whatever codec they use internally, because they compress block by block.'),
    ('Why is gzip not splittable?', 'A gzip file is one continuous DEFLATE stream: decoding any part requires the state built from everything before it, and there are no markers where a reader could safely begin. A map task assigned the middle of the file could not decompress it, so Hadoop makes the whole file one split.'),
    ('How do I enable compression in a MapReduce job?', 'For intermediate data set mapreduce.map.output.compress=true and mapreduce.map.output.compress.codec (for example org.apache.hadoop.io.compress.SnappyCodec). For the final output set mapreduce.output.fileoutputformat.compress=true and mapreduce.output.fileoutputformat.compress.codec, or call FileOutputFormat.setCompressOutput and setOutputCompressorClass in the driver. Compressed input is detected automatically from the file extension.'),
    ('Which codec should I use in Hadoop?', 'For the shuffle, a fast codec: Snappy, LZ4 or Zstandard. For data that jobs read often, a columnar container (Parquet or ORC) with Snappy or Zstandard. For plain text that must be one large splittable file, bzip2. For archives, a high compression level of Zstandard, gzip or bzip2. Always test on your own data, because ratios depend heavily on content.'),
    ('What are native libraries in Hadoop?', 'libhadoop.so and system libraries (zlib, libzstd, libbz2) that implement compression and other functions in C for speed. hadoop checknative lists which are loaded. Without them Hadoop uses slower Java implementations where they exist, and codecs without a Java version fail.'),
]

PRACTICE_INTRO = 'Compression exercises using the real numbers from the lab.'
PROBLEMS = [
    dict(level='easy', title='Compression ratios', stmt='Compute each codec\'s compressed size as a percentage of 194,186,990 bytes.', inp='CodecBench sizes',
         code='''orig = 194_186_990
for name, size in [("gzip", 45_696_989), ("bzip2", 31_984_098), ("snappy", 81_629_934), ("lz4", 73_417_559), ("zstd", 50_199_622)]:
    print(f"{name:7} {100 * size / orig:.1f}%")
''', explain='23.5, 16.5, 42.0, 37.8 and 25.9%, the same numbers CodecBench printed.'),
    dict(level='easy', title='gzip vs deflate', stmt='gzip and deflate use the same algorithm. How many bytes larger is the .gz file?', inp='45,696,989 vs 45,696,977',
         code='''print(45_696_989 - 45_696_977, "bytes")
''', explain='12 bytes: only the gzip header and trailer differ.'),
    dict(level='easy', title='Shuffle saved', stmt='How many times smaller was the shuffle with Snappy and with Zstandard?', inp='60,298,184 · 2,846,994 · 13,385',
         code='''print(round(60_298_184 / 2_846_994, 1), round(60_298_184 / 13_385))
''', explain='About 21× and 4,505×. Sorted, repetitive map output compresses extremely well.'),
    dict(level='medium', title='Throughput', stmt='Compute compression speed in MB/s for gzip, ZSTD and LZ4 from the lab times.', inp='194 MB · 14.5 s · 1.4 s · 0.7 s',
         code='''mb = 194_186_990 / 1024 / 1024
for name, s in [("gzip", 14.5), ("zstd", 1.4), ("lz4", 0.7)]:
    print(f"{name:5} {mb / s:6.0f} MB/s")
''', explain='About 13, 132 and 265 MB/s on one thread: a slow codec can become the bottleneck before the disk does.'),
    dict(level='medium', title='Blocks of a compressed file', stmt='How many 8 MB blocks does each compressed file need? Compare with the fsck counts (6, 4, 6, 10).', inp='sizes from CodecBench',
         code='''import math
for name, size in [("gz", 45_696_989), ("bz2", 31_984_098), ("zst", 50_199_622), ("snappy", 81_629_934)]:
    print(name, math.ceil(size / (8 * 1024 * 1024)))
''', explain='6, 4, 6 and 10, matching fsck. Only for bz2 did blocks become splits.'),
    dict(level='medium', title='Many gzip files instead of one', stmt='A 40 GB log is written as many gzip files holding 250 MB of text each, instead of one big file. How many map tasks now?', inp='40 GB · 250 MB per file',
         code='''import math
print(math.ceil(40 * 1024 / 250), "map tasks (one per file)")
''', explain='164 map tasks: non-splittable codecs are fine when each file is small enough to be one task.'),
    dict(level='business', title='Storage bill', stmt='Cloud storage costs ₹1.8 per GB per month. 50 TB of CSV is converted to Parquet with ZSTD at about 15% of the size (Lesson 10.2 got 14.3%). What is saved per year?', inp='50 TB · ₹1.8/GB-month · 15%',
         code='''gb = 50 * 1024
saved = gb * (1 - 0.15) * 1.8 * 12
print(f"Rs {saved:,.0f} per year")
''', explain='About ₹9.4 lakh a year (illustrative prices), and scans also read 85% fewer bytes.'),
    dict(level='advanced', title='Split planner with locality', stmt='Write a function that, for a file size, block size and codec, returns the number of map tasks and how many blocks must be read remotely (assuming each splittable map is data-local and a single map is local only to block 1).', inp='file, block, codec',
         code='''import math
SPLITTABLE = {"none": True, "bzip2": True, "gzip": False, "snappy": False, "zstd": False}

def plan(size_mb, block_mb, codec):
    blocks = math.ceil(size_mb / block_mb)
    if SPLITTABLE[codec]:
        return blocks, 0
    return 1, blocks - 1

for codec in SPLITTABLE:
    maps, remote = plan(50 * 1024, 128, codec)
    print(f"{codec:7} {maps:4} maps, {remote:4} blocks read over the network")
''', explain='For 50 GB: 400 maps and no remote reads when splittable, versus 1 map pulling 399 blocks over the network for gzip, Snappy or ZSTD.'),
]

SCN_INTRO = 'Compression questions are common for data engineers: splittability, codec choice and where to compress.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Concepts · splittability</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“Why does my job on a 30 GB .gz file run only one mapper?”</h4>
      <p class="scn__situation">A classic first question about compression.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> splittable vs non-splittable codecs.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>gzip is one DEFLATE stream with no restart points, so the input format makes one split for the whole file.</li>
          <li>Fixes: recompress with bzip2, split the data into many gzip files near the block size, or convert to Parquet/ORC.</li>
          <li>Also mention lost data locality: one map reads most blocks over the network.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Performance · shuffle</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>A join job's shuffle saturates the network</h4>
      <p class="scn__situation">Reducers spend most of their time in the copy phase.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> map output compression and other shuffle reducers.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Enable mapreduce.map.output.compress with Snappy, LZ4 or ZSTD; cheap CPU for much less network.</li>
          <li>Add a combiner if the reduce is an aggregation, and emit compact types.</li>
          <li>If one side is small, use a map-side join and skip the shuffle (Lesson 9.6).</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Design · storage</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Choose a storage format and codec for a new data lake</h4>
      <p class="scn__situation">Analysts query a few columns; data arrives as gzipped JSON.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> container formats vs raw compressed files.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Land the gzip files as they come, then convert to Parquet or ORC with Snappy or ZSTD.</li>
          <li>Columnar + compression per page/stripe gives small, splittable files and column pruning.</li>
          <li>Keep file sizes around 128 MB–1 GB and compact small files.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Operations · debugging</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>A job with Zstandard works locally but fails on the cluster</h4>
      <p class="scn__situation">Tasks fail with ClassNotFoundException or “native zstd library not available”.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> native libraries and task classpaths.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Run hadoop checknative on the worker nodes; install libzstd or the Hadoop native build if missing.</li>
          <li>Ship missing jars (for example zstd-jni for Parquet) with -libjars or install them cluster-wide.</li>
          <li>Read the failed attempt's diagnostics in the JobHistory UI or yarn logs, not just the client output.</li>
        </ul>
      </div></details>
    </article>
'''
