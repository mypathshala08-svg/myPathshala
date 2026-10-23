import os
HERE = os.path.dirname(os.path.abspath(__file__))
BODY = body(HERE)
rd = lambda f: open(os.path.join(HERE, f)).read()

META = dict(
    module='07-hdfs-advanced', lesson='05-the-small-files-problem', n='7.5',
    module_label='Module 7 · HDFS advanced',
    title='The small files problem',
    desc='The HDFS small files problem measured on a real Hadoop 3.5.0 cluster: the same 338,894 bytes as 10,000 files vs 1 file. Upload 281 s vs 2.1 s, read 15.2 s vs 1.9 s, NameNode FilesTotal 41 → 10,043 and BlocksTotal 31 → 10,031, fsck average block size 33 B. Then the fix: a Hadoop Archive (HAR) packs them into 4 files, readable by name through har://. NameNode memory sizing, one task per file, compaction, SequenceFiles, CombineFileInputFormat. Python simulations, quiz and interview scenarios.',
    og_desc='10,000 tiny files took 281 seconds to upload; the same bytes as one file took 2. Measure the small files problem, then fix it.',
    minutes=26, level='Intermediate',
    lead='HDFS is built for big files. Store the same data as thousands of tiny files and the NameNode\'s memory, every client call and every job pay for it. This lesson measures the cost on a real cluster with 10,000 files against one, explains where the time and memory go, and fixes it with a Hadoop Archive and better writing habits.',
    chips=['281 s vs 2 s, measured', 'HAR fix on a real cluster', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Count the NameNode\'s work for small and big files',
    intro='<p>This model counts NameNode objects (files + blocks), NameNode calls and map tasks for the same data stored as many small files or a few big ones. The cost per object comes from the common rule of thumb of about 150 bytes of heap.</p>',
    code='''import math
BLOCK = 128 * 1024 * 1024
HEAP_PER_OBJECT = 150                       # bytes, rule of thumb

def cost(total_bytes, n_files):
    size = total_bytes / n_files
    blocks_per_file = max(1, math.ceil(size / BLOCK))
    objects = n_files * (1 + blocks_per_file)
    calls = n_files * (2 + blocks_per_file)   # create + complete + addBlock per block
    tasks = n_files * blocks_per_file         # about one split per block (one per small file)
    return objects, calls, tasks, objects * HEAP_PER_OBJECT

data = 338_894
for n in [10_000, 1]:
    o, c, t, heap = cost(data, n)
    print(f"{n:>6} files: {o:>6} objects, {c:>6} NameNode calls, {t:>6} map tasks, ~{heap / 1024:.0f} KB heap")
''',
    anno=[
        ('    objects = n_files * (1 + blocks_per_file)', 'Each file is at least two objects: the file and its block. Our lab: +10,000 files and +10,000 blocks.'),
        ('    calls = n_files * (2 + blocks_per_file)   # create + complete + addBlock per block', 'Each file needs its own create, addBlock and complete calls, the reason 10,000 uploads took 281 s.'),
        ('    tasks = n_files * blocks_per_file         # about one split per block (one per small file)', 'Frameworks create about one split per file: 10,000 tiny tasks, mostly start-up overhead.'),
    ],
    tasks=[
        dict(label='1 · Small vs big', hint='Press <b>Run</b>. Then try the same data as 100 files. Where is the sweet spot?', code=None),
        dict(label='2 · Scale it up', hint='<b>Predict first:</b> 10 crore small files of 50 KB vs the same data in 1 GB files. How much NameNode heap does each need?',
             code='''n_small, size_small = 100_000_000, 50 * 1024
total = n_small * size_small
for name, n, blocks in [("small files", n_small, 1), ("1 GB files", total // 1024**3, 8)]:
    objects = n * (1 + blocks)
    print(f"{name:11} {n:>12,} files -> {objects * 150 / 1024**3:.1f} GB heap")
'''),
        dict(label='3 · Average file size', hint='Compute average file size per folder from <code>-count</code> output and flag folders with many files (over 100) averaging below 1 MB. One small file is fine; thousands are the problem.',
             code='''rows = [("/small", 10000, 338894), ("/big", 1, 338894), ("/warehouse/sales", 1200, 160_000_000_000)]
for path, files, size in rows:
    avg = size / files
    print(f"{path:18} avg {avg:>14,.0f} B", "<- small files!" if files > 100 and avg < 1024**2 else "")
'''),
        dict(label='4 · Compaction plan', hint='How many output files should a compaction job write for 45 GB of data with a target of 256 MB per file?',
             code='''import math
data_gb, target_mb = 45, 256
print(math.ceil(data_gb * 1024 / target_mb), "files")
'''),
        dict(label='5 · Spot the error', hint='This compaction code divides by the number of output files, which is zero for an empty partition. Guard against it.',
             code='''data_mb, target_mb = 0, 256
files = data_mb // target_mb
print("bytes per file:", data_mb / files)
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: 10,000 files vs 1, then archive them',
    intro='<p>Run this against the Module 5 lab cluster. It creates 10,000 tiny CSV files and one file with the same bytes inside the namenode container, uploads both, reads NameNode counters from <code>/jmx</code>, compares reads, then packs the small files into a Hadoop Archive. It takes about 6 minutes, most of it the small-file upload.</p>',
    items=[
        dict(title='Small files lab', file='small_files_lab.sh',
             cmd=rd('small_files_lab.sh') + '\n# Run:  bash small_files_lab.sh',
             output=rd('tx_small.txt').strip(),
             note='Real output. Timings vary; the ratio stays dramatic. The JMX counters refresh with a delay, which is why the line after the big file still shows the earlier values; fsck shows its 1 file and 1 block.'),
    ],
)

TRACE = dict(
    heading='Packing small files into one container',
    intro='<p>A container (like a SequenceFile or a HAR) stores many small files inside one big file and keeps an index of where each one starts. Follow three files being packed and one being read back.</p>',
    code='''files = {"o_1.csv": b"1,chai,20\\n", "o_2.csv": b"2,poha,30\\n", "o_3.csv": b"3,dosa,40\\n"}
container = b""
index = {}
for name, data in files.items():
    index[name] = (len(container), len(data))
    container += data
start, length = index["o_2.csv"]
print(index)
print(container[start:start + length])
''',
    notes={5: 'Index :: Like HAR\'s _index file: name → (offset, length) inside part-0.',
           7: 'Read :: One lookup in the index, then one read from the big file.'},
)

WORKED_INTRO = 'Three small-files calculations: NameNode heap, job overhead, and the payoff of compaction.'
EXAMPLES = [
    dict(level='b', tag='Sizing · heap', title='How much NameNode memory do small files cost?',
         problem='<p>A team writes 20 lakh files a day, each 30 KB (one block each), and keeps them for 180 days. Using about 150 bytes per object, how much NameNode heap do they occupy?</p>',
         inp='20,00,000/day · 180 days · 2 objects/file',
         approach=['Files kept = per day × days.',
                   'Objects = files × 2 (file + block).',
                   'Heap = objects × 150 B.'],
         code='''files = 2_000_000 * 180
objects = files * 2
print(f"{files:,} files -> {objects * 150 / 1024**3:.0f} GB of NameNode heap")
''', notes={2: 'Objects :: Bytes of data don\'t matter here, only counts.'},
         tryit='About 100 GB of heap for roughly 10 TB of data. Written as hourly 1 GB files, the same data would need a few MB.'),
    dict(level='i', tag='Jobs · overhead', title='How long do 10,000 tiny tasks take?',
         problem='<p>A job reads 10,000 small files, one map task each. Each task spends 1.5 s starting and 0.05 s working. With 200 task slots, how long does the map phase take, compared with 2 tasks reading 2 big files (1.5 s + 40 s work each)?</p>',
         inp='10,000 × (1.5 + 0.05) s / 200 slots vs 2 × 41.5 s',
         approach=['Waves = tasks / slots.',
                   'Time = waves × task time.',
                   'Compare.'],
         code='''import math
small = math.ceil(10_000 / 200) * (1.5 + 0.05)
big = math.ceil(2 / 200) * (1.5 + 40)
print(f"small files: {small:.1f} s ({10_000 * 1.5 / 3600:.1f} task-hours of pure start-up)")
print(f"big files  : {big:.1f} s")
''', notes={2: 'Waves :: 10,000 tasks on 200 slots run in 50 waves.'},
         tryit='The small-file job is faster in wall time here, but it burns 4.2 hours of cluster time on start-up alone. CombineFileInputFormat packs many files per task to avoid this.'),
    dict(level='a', tag='Operations · payoff', title='Is a nightly compaction job worth it?',
         problem='<p>A streaming job creates 2,880 files per partition per day across 50 partitions. Compaction rewrites each day into 2 files per partition, costing 20 minutes of a 40-node cluster (₹600 per node-hour). Each NameNode object costs ₹0.0002 per day in extra heap and GC (illustrative). Compare the yearly cost with and without compaction.</p>',
         inp='2,880 × 50 files/day · compaction 20 min × 40 nodes',
         approach=['Objects avoided per day.',
                   'Objects accumulate: day d keeps d days of files.',
                   'Compare with compaction cost.'],
         code='''files_per_day = 2880 * 50
avoided_per_day = (files_per_day - 2 * 50) * 2           # files + blocks
heap_cost = sum(avoided_per_day * d for d in range(1, 366)) * 0.0002
compaction_cost = 365 * 20 / 60 * 40 * 600
print(f"heap/GC cost avoided: Rs {heap_cost:,.0f}  compaction cost: Rs {compaction_cost:,.0f}")
''', notes={4: 'Accumulation :: Objects pile up every day the files are kept.'},
         tryit='The bigger win is not money: without compaction, a year adds about 10 crore objects and the NameNode eventually can\'t restart within its maintenance window.'),
]

QUIZ = mix([
    dict(q='Why are small files a problem for HDFS?', options=['They use more DataNode disk per byte', 'Every file and block is an object in NameNode memory and needs its own calls, regardless of size', 'HDFS can\'t store files under 1 MB', 'They are slower to compress'], answer=1,
         why='In our lab both folders used 1,016,682 raw bytes; only the object counts differed.'),
    dict(q='How long did uploading 10,000 tiny files take vs one file with the same bytes?', options=['About the same', '281 s vs 2.1 s', '15 s vs 2 s', '10 s vs 1 s'], answer=1,
         why='Three NameNode calls and a pipeline per file.'),
    dict(q='What average block size did fsck report for /small?', options=['128 MB', '33 B', '4 KB', '338,894 B'], answer=1,
         why='10,000 blocks for 338,894 bytes.'),
    dict(q='What happens in MapReduce/Spark with 10,000 small input files (by default)?', options=['One task reads them all', 'About one split and task per file', 'They are skipped', 'They are merged automatically'], answer=1,
         why='CombineFileInputFormat or compaction avoid this.'),
    dict(q='What did the Hadoop Archive contain?', options=['10,000 files', '_index, _masterindex, part-0 and _SUCCESS', 'Only an index', 'A zip file'], answer=1,
         why='Data in part-0, names and offsets in the index.'),
    dict(q='How do you read a file inside a HAR?', options=['hdfs dfs -unhar', 'Through a har:// path, e.g. har:///archives/orders.har/o_42.csv', 'It must be extracted first', 'With fsck'], answer=1,
         why='Real: printed “42,chai,20”.'),
    dict(q='Which fix removes the problem at its source?', options=['Bigger NameNode heap', 'Writing larger files (batching) in the producing application', 'More DataNodes', 'Lower replication'], answer=1,
         why='Everything else is cleanup after the fact.'),
    dict(q='Which tool reduces task overhead but NOT NameNode objects?', options=['HAR', 'Compaction', 'CombineFileInputFormat', 'Writing bigger files'], answer=2,
         why='It groups files into fewer splits; the files still exist.'),
])

REVISION = [
    'Small files cost the <b>NameNode</b> (≈150 B per file/folder/block, rule of thumb), <b>RPCs</b> and <b>tasks</b>, not DataNode disk.',
    'Lab (338,894 bytes): 10,000 files upload 281 s vs 2.1 s; read 15.2 s vs 1.9 s; +10,000 files and blocks; fsck avg block 33 B.',
    'DataNode raw bytes were identical (1,016,682): blocks are only as big as their data.',
    'Fixes: write bigger files at source; scheduled <b>compaction</b> (Spark, Hive, Delta OPTIMIZE, Iceberg rewrite); containers (SequenceFile, Avro, Parquet).',
    '<b>HAR</b>: <code>hadoop archive -archiveName x.har -p /src /dest</code>; read via <code>har://</code>; immutable.',
    '<b>CombineFileInputFormat</b> reduces tasks, not NameNode objects.',
    'Watch average file size (<code>-count</code>), use name quotas on landing zones.',
]
FAQ = [
    ('What is the small files problem in Hadoop?', 'When data is stored as many files much smaller than the block size, the NameNode must keep an object in memory for each file and block, handle separate RPCs for each, and jobs create a task per file. Memory, NameNode load and job overhead grow with the number of files, not the amount of data, which limits scalability and performance.'),
    ('How do you solve the small files problem?', 'Prevent it by writing larger files (batching, sensible streaming intervals, fewer reducers). Clean up existing data with compaction jobs that rewrite small files into large ones, Hadoop Archives (HAR) for rarely accessed data, or container formats like SequenceFile/Avro/Parquet. Use CombineFileInputFormat to reduce task counts when reading.'),
    ('What is a Hadoop Archive (HAR)?', 'An archive created by the hadoop archive command (a MapReduce job) that packs many files into a few large part files plus index files. The original paths remain readable through the har:// file system, while the NameNode stores only the archive\'s few files. HAR files are immutable.'),
    ('Do small files waste DataNode disk space in HDFS?', 'Not in the way local file systems do: an HDFS block replica only occupies the bytes it contains. In our lab, 10,000 small files and one big file used the same raw bytes. The waste is in NameNode memory, RPC load and job overhead.'),
    ('What file size should data in HDFS have?', 'As a guideline, hundreds of MB to a few GB per file: at least around the block size (128 MB) and big enough that jobs have reasonably sized splits, while not so big that a single file limits parallelism (for non-splittable formats).'),
]

PRACTICE_INTRO = 'Small-files exercises using the real counts and timings from the lab.'
PROBLEMS = [
    dict(level='easy', title='Objects added', stmt='FilesTotal went 41 → 10,043 and BlocksTotal 31 → 10,031. How many objects did the NameNode gain?', inp='two counters',
         code='''print((10043 - 41) + (10031 - 31), "objects")
''', explain='20,002: 10,000 files, 2 folders and 10,000 blocks.'),
    dict(level='easy', title='Slowdown factors', stmt='Compute how many times slower upload and read were for the small files.', inp='281,026 vs 2,133 ms · 15,168 vs 1,892 ms',
         code='''print(f"upload {281026 / 2133:.0f}x slower, read {15168 / 1892:.1f}x slower")
''', explain='About 132× slower to upload and 8× slower to read, for identical bytes.'),
    dict(level='easy', title='Average file size', stmt='What is the average size of the 10,000 files?', inp='338,894 bytes / 10,000',
         code='''print(338894 / 10000, "bytes")
''', explain='About 34 bytes; fsck reports 33 B (rounded down).'),
    dict(level='medium', title='Heap after a year', stmt='An app creates 5,000 small files per hour, each one block, kept forever. How many objects after one year, and roughly how much heap at 150 B each?', inp='5,000/hour × 8,760 hours',
         code='''files = 5000 * 8760
print(f"{files * 2:,} objects -> {files * 2 * 150 / 1024**3:.1f} GB")
''', explain='8.76 crore objects, about 12 GB of heap from a single application.'),
    dict(level='medium', title='Parse the HAR index idea', stmt='Given an index of name → (offset, length) and the big file, read o_3.csv.', inp='index + bytes',
         code='''part0 = b"1,chai,20\\n2,poha,30\\n3,dosa,40\\n"
index = {"o_1.csv": (0, 10), "o_2.csv": (10, 10), "o_3.csv": (20, 10)}
o, l = index["o_3.csv"]
print(part0[o:o + l])
''', explain='b"3,dosa,40\\n": one index lookup and one read from part-0, like har:// does.'),
    dict(level='medium', title='Tasks with combining', stmt='10,000 small files of 34 bytes; CombineFileInputFormat packs files into splits of up to 128 MB. How many tasks?', inp='10,000 × 34 B',
         code='''import math
print(max(1, math.ceil(10000 * 34 / (128 * 1024**2))), "task(s)")
''', explain='1 task instead of 10,000, but the NameNode still holds 20,000 objects.'),
    dict(level='business', title='Fix the writer or buy RAM?', stmt='Option A: a bigger NameNode server with 512 GB RAM for ₹35 lakh. Option B: 3 developer-weeks (₹1.5 lakh each) to batch writes, which removes 90% of new small files. Which is cheaper, and which keeps working next year?', inp='₹35 lakh vs 3 × ₹1.5 lakh',
         code='''a, b = 35, 3 * 1.5
print(f"A: Rs {a} lakh, B: Rs {b} lakh")
''', explain='B costs ₹4.5 lakh vs ₹35 lakh (illustrative) and stops the growth; A only postpones the problem.'),
    dict(level='advanced', title='Compaction planner', stmt='Given partition sizes (MB) and file counts, plan how many output files each partition needs at a 256 MB target, and how many objects are saved.', inp='3 partitions',
         code='''import math
parts = {"dt=2026-10-19": (5400, 2880), "dt=2026-10-20": (6100, 2880), "dt=2026-10-21": (300, 1500)}
saved = 0
for p, (mb, files) in parts.items():
    out = max(1, math.ceil(mb / 256))
    saved += (files - out) * 2
    print(f"{p}: {files} -> {out} files")
print("objects saved:", saved)
''', explain='22 + 24 + 2 output files; about 14,424 objects saved. Real compaction jobs also respect sort order and table formats.'),
]

SCN_INTRO = 'The small files problem is one of the most asked Hadoop interview topics, from freshers to architects.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">HDFS · basics</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“Why is HDFS bad at small files?”</h4>
      <p class="scn__situation">Almost guaranteed in a Hadoop interview.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> NameNode memory and task overhead.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Every file and block is an object in NameNode RAM (~150 bytes each); millions of tiny files exhaust the heap.</li>
          <li>Each file means separate NameNode calls and DataNode connections, and one map task per file.</li>
          <li>Fixes: bigger files at source, compaction, HAR or SequenceFiles, CombineFileInputFormat.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Streaming · design</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>A Spark Streaming job writes 50,000 files an hour</h4>
      <p class="scn__situation">Analysts' queries on the output table get slower each week; the NameNode heap keeps growing.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> write-side and cleanup-side fixes.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Reduce output partitions per micro-batch (coalesce) and increase the trigger interval if freshness allows.</li>
          <li>Use a table format (Delta/Iceberg/Hudi) and schedule compaction (OPTIMIZE / rewrite) for closed partitions.</li>
          <li>Monitor average file size per partition and alert when it drops.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Operations · cleanup</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Find the folders causing the most NameNode load</h4>
      <p class="scn__situation">The cluster has 40 crore objects; you must find who owns them without hammering the NameNode.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> offline analysis.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Fetch the latest fsimage (<code>hdfs dfsadmin -fetchImage</code>) and convert it with the Offline Image Viewer to a delimited file.</li>
          <li>Aggregate by folder: file count, total size, average size; rank by file count with small average size.</li>
          <li>Work with owners: compaction or HAR for old data, writer fixes for new data, name quotas on landing folders.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Concepts · trade-offs</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“HAR or SequenceFile?”</h4>
      <p class="scn__situation">A follow-up after you list solutions.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> when each fits.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>HAR keeps the original paths readable through har:// with no code change for readers; good for archives. It is immutable and reading has index overhead.</li>
          <li>SequenceFile packs files as key-value records (name → bytes); efficient and splittable for MapReduce, but readers must use the container.</li>
          <li>For tabular data, compaction into Parquet is usually better than both.</li>
        </ul>
      </div></details>
    </article>
'''
