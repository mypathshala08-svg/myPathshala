import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()

META = dict(
    module='08-mapreduce-fundamentals', lesson='02-input-splits-inputformat-and-recordreader', n='8.2',
    module_label='Module 8 · MapReduce fundamentals',
    title='Input splits, InputFormat and RecordReader',
    desc='How Hadoop MapReduce turns a file into map tasks and records, measured on a real Hadoop 3.5.0 cluster: 1 split for 4.7 MB, 5 splits with 1 MB blocks or split.maxsize, 1 split for a 2-block 134 MB file (the 1.1 split slop), 2 splits with split.minsize 256 MB. A line crossing the block boundary at byte 1,048,576 is read whole by one map and skipped by the next: 300,001 records, none lost or doubled. InputFormat, FileSplit, TextInputFormat, KeyValueTextInputFormat, NLineInputFormat, CombineTextInputFormat, splittable vs gzip. Python simulations, quiz and interview scenarios.',
    og_desc='HDFS cuts blocks by bytes, not lines. See on a real cluster how the RecordReader keeps every line whole, and why 2 blocks gave 1 map.',
    minutes=26, level='Intermediate',
    lead='Before a single map task runs, Hadoop has already decided how many there will be and which bytes each one reads. This lesson opens up that decision (the InputFormat and its splits) and the reader inside each map task that turns bytes into records, using a small job that reports exactly what every split saw.',
    chips=['Boundary line caught on a real cluster', '2 blocks → 1 split, explained', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Compute splits like FileInputFormat',
    intro='<p>This is the core of <code>FileInputFormat.getSplits()</code> for one file: the split size formula and the 1.1 slop rule. The file sizes are the real ones from our lab, and the printed counts match the job logs.</p>',
    code='''MB = 1024 * 1024
SLOP = 1.1

def get_splits(length, block=128 * MB, min_size=1, max_size=2**63 - 1):
    split_size = max(min_size, min(max_size, block))
    splits, start, remaining = [], 0, length
    while remaining / split_size > SLOP:
        splits.append((start, split_size))
        start += split_size
        remaining -= split_size
    if remaining:
        splits.append((start, remaining))
    return splits

files = {"canteen_orders.csv": 4_692_009, "orders_x30.csv": 140_759_640, "orders_x90.csv": 422_278_920}
print("A", len(get_splits(files["canteen_orders.csv"])), "split(s)")
print("B", get_splits(files["canteen_orders.csv"], block=1 * MB))
print("D", len(get_splits(files["orders_x30.csv"])), "split(s)")
print("E", len(get_splits(files["orders_x90.csv"])), "split(s)")
print("F", len(get_splits(files["orders_x90.csv"], min_size=256 * MB)), "split(s) with minsize 256 MB")
''',
    anno=[
        ('    split_size = max(min_size, min(max_size, block))', 'The formula from FileInputFormat.computeSplitSize(). With default min and max it is simply the block size.'),
        ('    while remaining / split_size > SLOP:', 'Keep cutting full splits only while more than 1.1 splits are left; the rest becomes the last split.'),
        ('print("D", len(get_splits(files["orders_x30.csv"])), "split(s)")', '140,759,640 / 134,217,728 = 1.049, below 1.1: two blocks, one split, exactly as the job log said.'),
    ],
    tasks=[
        dict(label='1 · Count the splits', hint='Press <b>Run</b>. Compare every line with the lab table: 1, 5, 1, 4 and 2.', code=None),
        dict(label='2 · Where does the slop bite?', hint='<b>Predict first:</b> for which file sizes between 128 MB and 160 MB does the job get only 1 split?',
             code='''MB = 1024 * 1024
for size_mb in [130, 135, 140, 140.8, 141, 150, 160]:
    n = 1 if size_mb / 128 <= 1.1 else 2
    print(f"{size_mb:6} MB -> {n} split(s)")
'''),
        dict(label='3 · Read across a boundary', hint='A LineRecordReader in miniature. Split the text at byte 20 and read both halves. Which split gets the line that crosses byte 20?',
             code='''data = b"1001,chai,15\\n1002,dosa,45\\n1003,poha,25\\n"

def read_split(start, length):
    end, pos, out = start + length, start, []
    if start != 0:                                  # skip the partial first line
        pos = data.index(b"\\n", start) + 1
    while pos <= end and pos < len(data):           # a line STARTING at or before end is ours
        nl = data.index(b"\\n", pos)
        out.append((pos, data[pos:nl].decode()))
        pos = nl + 1
    return out

print("split 0:", read_split(0, 20))
print("split 1:", read_split(20, len(data) - 20))
'''),
        dict(label='4 · Tune maps for a CPU-heavy job', hint='A 1 GB file, 128 MB blocks. Which split.maxsize gives 32 map tasks? Check with the formula.',
             code='''MB = 1024 * 1024
length = 1024 * MB
for max_mb in [128, 64, 32, 16]:
    size = max(1, min(max_mb * MB, 128 * MB))
    n = 0
    remaining = length
    while remaining / size > 1.1:
        remaining -= size; n += 1
    print(f"maxsize {max_mb:3} MB -> {n + (1 if remaining else 0)} splits")
'''),
        dict(label='5 · Spot the error', hint='This reader forgets to skip the partial first line when its split does not start at 0. Run it: the boundary line is read in two broken pieces. Fix it with the rule from task 3.',
             code='''data = b"1001,chai,15\\n1002,dosa,45\\n"
start = 20                                          # inside "1002,dosa,45"
first = data[start:data.index(b"\\n", start)].decode()
oid, item, amount = first.split(",")
print("record:", oid, item, amount)
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: peek inside every split',
    intro='<p>Use the Module 8 lab from Lesson 8.1 (<code>lab8</code>). <code>SplitPeek.java</code> is a map-only job that writes one line per split. <code>splits_lab.sh</code> runs it six ways. It takes about 3 minutes.</p>',
    items=[
        dict(title='A job that reports its own split', file='SplitPeek.java',
             cmd=rd('java/SplitPeek.java') + '\n// In the mr-lab folder:\n//   docker cp SplitPeek.java lab8-namenode-1:/tmp/mr/\n//   docker exec -it lab8-namenode-1 bash\n// Inside the container (canteen_orders.csv and orders_x30/x90 from Lesson 8.1 are already in HDFS):\n//   cd /tmp/mr\n//   mkdir -p classes && javac -cp $(hadoop classpath) -d classes *.java && jar cf mr.jar -C classes .\n//   hadoop jar mr.jar SplitPeek /user/hadoop/data/canteen_orders.csv /out/peek_a\n//   hdfs dfs -cat /out/peek_a/part-m-*',
             output=rd('tx82.txt').split('== B')[0].strip(),
             note='Real output. The key the mapper receives is the byte offset of each line, so first_offset and last_offset are simply the first and last keys it saw.'),
        dict(title='Six ways to split the same data', file='splits_lab.sh',
             cmd=rd('splits_lab.sh') + '\n# Inside the namenode container:\n#   bash /tmp/mr/splits_lab.sh',
             output=rd('tx82.txt').strip(),
             note='Real output. Which worker ran each split will differ on your machine; split boundaries, offsets and record counts will be identical because the data is generated with a fixed seed.'),
    ],
)

TRACE = dict(
    heading='Who reads the line that crosses the boundary?',
    intro='<p>Two readers share 39 bytes, cut at byte 20. Follow <code>pos</code> in each: the second reader jumps past the first newline, the first reads past its end.</p>',
    code='''data = "1001,chai,15\\n1002,dosa,45\\n1003,poha,25\\n"
for start, end in [(0, 20), (20, 39)]:
    pos = start
    if start != 0:
        pos = data.index("\\n", start) + 1
    lines = []
    while pos <= end and pos < len(data):
        nl = data.index("\\n", pos)
        lines.append(data[pos:nl])
        pos = nl + 1
    print(start, end, lines)
''',
    notes={5: 'Skip :: Split 1 starts inside “1002,dosa,45”, so it throws away bytes up to the newline.',
           7: 'Read on :: Split 0 starts “1002,dosa,45” at byte 13, before its end (20), so it reads the whole line.',
           11: 'Result :: Each line printed exactly once.'},
)

WORKED_INTRO = 'Three split calculations: from block layout to map count, a boundary check, and choosing a split size.'
EXAMPLES = [
    dict(level='b', tag='Splits · count', title='How many map tasks will this job get?',
         problem='<p>A folder holds three files: 300 MB, 130 MB and 20 MB, with 128 MB blocks and default split settings. How many map tasks run?</p>',
         inp='300 MB · 130 MB · 20 MB',
         approach=['Splits are computed per file.',
                   'Apply the 1.1 slop rule to each file.',
                   'Add them up.'],
         code='''def n_splits(mb, size=128):
    n, rem = 0, mb
    while rem / size > 1.1:
        rem -= size; n += 1
    return n + (1 if rem else 0)
files = [300, 130, 20]
print([n_splits(f) for f in files], "->", sum(n_splits(f) for f in files), "map tasks")
''', notes={6: 'Per file :: 300 MB → 128 + 172 (1.34 > 1.1) → 128 + 128 + 44: 3 splits.'},
         tryit='130 MB is only 1.016 splits, so 1 map. The 20 MB file still costs a whole map task of its own.'),
    dict(level='i', tag='Records · boundary', title='Check a boundary from the job output',
         problem='<p>SplitPeek reported for split 1: <code>last_offset=2097145 last_line=138805,idli,30</code>, and split 2 started at byte 2,097,152 with <code>first_offset=2097160</code>. Show that no line was lost between them.</p>',
         inp='2,097,145 · "138805,idli,30" · 2,097,160',
         approach=['The last line of split 1 ends at its offset + its length + 1 (newline).',
                   'That must be exactly where split 2\'s first record starts.'],
         code='''last_offset, last_line = 2097145, "138805,idli,30"
ends_at = last_offset + len(last_line) + 1
print("line ends at", ends_at, "| split 2 first record", 2097160, "| match:", ends_at == 2097160)
print("bytes read past the split end:", ends_at - 2097152)
''', notes={2: 'End :: 14 characters plus the newline.'},
         tryit='Do the same for split 0 → 1: 1,048,564 + len("71484,poha,25") + 1.'),
    dict(level='a', tag='Tuning · size', title='Pick a split size for a 10 GB job',
         problem='<p>A 10 GB text file, 128 MB blocks, on a cluster with 40 free map containers. Each map has a fixed 6 s start-up and processes 50 MB/s. Compare 128 MB splits, 256 MB splits (split.minsize) and 64 MB splits (split.maxsize).</p>',
         inp='10 GB · 40 containers · 6 s start · 50 MB/s',
         approach=['Maps = size / split size; waves = maps / 40.',
                   'Time per map = 6 s + split / 50 MB/s.',
                   'Total ≈ waves × time per map.'],
         code='''import math
for split in [64, 128, 256]:
    maps = math.ceil(10 * 1024 / split)
    waves = math.ceil(maps / 40)
    t = waves * (6 + split / 50)
    print(f"{split:3} MB: {maps:3} maps, {waves} waves, ~{t:.0f} s")
''', notes={5: 'Waves :: Fewer, bigger maps mean fewer start-ups but coarser balancing.'},
         tryit='Here 256 MB wins on paper, but bigger splits read more data across nodes and recover more slowly if a map fails. 128 MB is the usual default for good reason.'),
]

QUIZ = mix([
    dict(q='Who computes the input splits, and when?', options=['Each map task, when it starts', 'The client, at job submission (InputFormat.getSplits())', 'The NameNode, when the file is written', 'The reducer'], answer=1,
         why='Our client log printed “number of splits:5” before any task ran.'),
    dict(q='What does TextInputFormat give the mapper as the key?', options=['The line number', 'The byte offset of the line in the file', 'The first field of the CSV', 'Nothing (NullWritable)'], answer=1,
         why='LongWritable offsets like 1048578.'),
    dict(q='A line starts in split 0 and ends in split 1. Who reads it?', options=['Both, each its own part', 'Split 0\'s reader reads it whole; split 1\'s reader skips it', 'Split 1 only', 'Nobody; it is dropped'], answer=1,
         why='Lab: split 0 ended with 71484,poha,25; split 1 started at 1048578.'),
    dict(q='Why did orders_x30.csv (2 blocks: 128 MB + 6.2 MB) get only 1 split?', options=['The file is compressed', 'The remaining size was below 1.1 × split size (split slop)', 'The second block was missing', 'Maps can\'t start on block 2'], answer=1,
         why='140,759,640 / 134,217,728 = 1.049.'),
    dict(q='What is the split size with default settings?', options=['64 MB always', 'max(minSize, min(maxSize, blockSize)), i.e. the block size', 'The file size', 'mapreduce.job.maps'], answer=1,
         why='Defaults: minSize 1, maxSize unlimited.'),
    dict(q='split.maxsize = 1 MB on a 4.7 MB file stored as one block gave how many splits?', options=['1', '5', '4', '47'], answer=1,
         why='Splits are logical byte ranges and need not match blocks.'),
    dict(q='Why does a 10 GB .gz file get only one map task?', options=['gzip files are always small', 'gzip is not splittable: a reader can\'t start in the middle', 'HDFS stores it in one block', 'The InputFormat rejects it'], answer=1,
         why='Module 10 compares splittable codecs.'),
    dict(q='Which InputFormat helps when a job reads 10,000 small files?', options=['NLineInputFormat', 'CombineTextInputFormat', 'KeyValueTextInputFormat', 'SequenceFileOutputFormat'], answer=1,
         why='It packs many files into one split.'),
])

REVISION = [
    '<b>InputFormat</b>: <code>getSplits()</code> on the client, <code>createRecordReader()</code> in each map task.',
    'One map task per <b>split</b>; a split is a byte range (FileSplit: path, start, length, hosts), not a copy of data.',
    '<code>splitSize = max(minSize, min(maxSize, blockSize))</code>; last piece up to 1.1 × is merged (slop).',
    'Lab: 4.7 MB → 1 split; 1 MB blocks or maxsize 1 MB → 5; 134 MB in 2 blocks → 1; 422 MB → 4, minsize 256 MB → 2.',
    'TextInputFormat: key = byte offset (LongWritable), value = line (Text).',
    'LineRecordReader: skip the partial first line (unless start = 0), read past the end to finish the last line; each line read once.',
    'Non-splittable files (gzip) → 1 split per file; many small files → use CombineTextInputFormat.',
]
FAQ = [
    ('What is the difference between an HDFS block and an input split?', 'A block is the physical unit HDFS stores and replicates (128 MB by default). An input split is a logical byte range computed by the job\'s InputFormat; one map task processes one split. By default a split equals a block, but split.minsize and split.maxsize change that, and the RecordReader reads records that cross block boundaries whole, so a split\'s records may extend slightly into the next block.'),
    ('How is the number of mappers decided in Hadoop?', 'By the number of input splits that the InputFormat computes. For FileInputFormat it depends on the file sizes, block size, mapreduce.input.fileinputformat.split.minsize and split.maxsize, the 1.1 split slop, and whether files are splittable. You cannot set the number of map tasks directly in the new API.'),
    ('How does Hadoop handle records that cross block boundaries?', 'The LineRecordReader of a split that does not start at byte 0 skips everything up to the first newline, because that partial line belongs to the previous split. Every reader keeps reading while the next line starts at or before the end of its split, so it finishes a line that crosses the boundary by reading a few bytes of the next block. Each line is therefore processed exactly once.'),
    ('What does TextInputFormat pass to the mapper?', 'For each line, a LongWritable key holding the byte offset where the line starts in the file, and a Text value holding the line without its line terminator. The offset is often ignored by the mapper.'),
    ('Why does my job have only one mapper for a large file?', 'Usually because the file is compressed with a non-splittable codec such as gzip, the InputFormat marks it as not splittable, or split.minsize is set larger than the file. A file just slightly bigger than one block (up to 10% more) also gets a single split because of the split slop.'),
]

PRACTICE_INTRO = 'Split and record-reader exercises using the real offsets and sizes from our lab.'
PROBLEMS = [
    dict(level='easy', title='Records add up', stmt='Add the record counts of the five splits and compare with the single-split run.', inp='70,485 · 67,321 · 65,498 · 65,574 · 31,123',
         code='''parts = [70485, 67321, 65498, 65574, 31123]
print(sum(parts), sum(parts) == 300001)
''', explain='300,001 in both runs: the boundary rule loses and duplicates nothing.'),
    dict(level='easy', title='Last split length', stmt='The file is 4,692,009 bytes and splits are 1 MB. What is the length of the last split?', inp='4,692,009 · 1,048,576',
         code='''print(4692009 - 4 * 1048576)
''', explain='497,705 bytes, exactly what SplitPeek printed.'),
    dict(level='easy', title='Slop ratio', stmt='Compute the ratio that decided orders_x30.csv\'s single split.', inp='140,759,640 / 134,217,728',
         code='''print(round(140759640 / 134217728, 3), "<= 1.1 -> one split")
''', explain='1.049: below 1.1, so no separate split for the 6.2 MB tail.'),
    dict(level='medium', title='Boundary at split 3', stmt='Split 3 ended at byte 4,194,304; its last line started at 4,194,301 (269877,samosa,18). Where does split 4 start reading?', inp='4,194,301 + line + newline',
         code='''print(4194301 + len("269877,samosa,18") + 1)
''', explain='4,194,318, the first_offset of split 4. Map 3 read 14 bytes past its end.'),
    dict(level='medium', title='KeyValueTextInputFormat', stmt='Parse output lines of Lesson 8.1 the way KeyValueTextInputFormat does: key before the first tab, value after.', inp='part-r-00000 lines',
         code='''lines = ["chai\\t50170\\t752550", "vada pav\\t49986\\t999720"]
for l in lines:
    key, value = l.split("\\t", 1)
    print(repr(key), "->", repr(value))
''', explain='Only the first tab separates; the value keeps the rest. Useful for chaining jobs.'),
    dict(level='medium', title='NLineInputFormat', stmt='5,000 lines, N = 50 lines per split. How many maps, and which lines does map 7 get?', inp='5,000 lines · N = 50',
         code='''n = 50
print(5000 // n, "maps; map 7 gets lines", 7 * n + 1, "to", 8 * n)
''', explain='100 maps; map 7 (counting from 0) gets lines 351–400.'),
    dict(level='business', title='The gzip bottleneck', stmt='A daily 60 GB gzip file takes one map 2 hours. Recompressed to splittable 128 MB pieces on a cluster with 100 free containers, each piece takes 45 s plus 5 s start-up. Estimate the new map time.', inp='60 GB · 100 containers · 50 s per map',
         code='''import math
maps = math.ceil(60 * 1024 / 128)
waves = math.ceil(maps / 100)
print(maps, "maps,", waves, "waves, about", round(waves * 50 / 60), "minutes instead of 120")
''', explain='480 maps in 5 waves: about 4 minutes instead of 2 hours (illustrative numbers).'),
    dict(level='advanced', title='A full LineRecordReader check', stmt='Generate 1,000 order lines, cut them into 7 equal byte ranges, read each with the boundary rule, and verify that every line is read exactly once.', inp='1,000 lines · 7 splits',
         code='''import random
random.seed(1)
items = ["chai", "dosa", "poha", "idli"]
data = "".join(f"{1000 + i},{random.choice(items)},{random.randint(10, 50)}\\n" for i in range(1000))
size = len(data) // 7 + 1
seen = []
for start in range(0, len(data), size):
    end = start + size
    pos = 0 if start == 0 else data.index("\\n", start) + 1
    while pos <= end and pos < len(data):
        nl = data.index("\\n", pos)
        seen.append(data[pos:nl]); pos = nl + 1
print(len(seen), "lines read;", len(set(seen)) == 1000 and len(seen) == 1000)
''', explain='1000 lines read exactly once, whatever the cut points. Try other split counts.'),
]

SCN_INTRO = 'Splits come up whenever an interviewer asks how many mappers a job will have, or why a job is slow.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Concepts · basics</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“Block vs input split?”</h4>
      <p class="scn__situation">A classic Hadoop interview question.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> physical vs logical.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Block: physical storage unit of HDFS, fixed size, replicated, cut by bytes.</li>
          <li>Split: logical unit of work for one map task, computed by the InputFormat at submission; usually one block.</li>
          <li>Records crossing a block edge are read whole by the split they start in; min/max split size can make splits differ from blocks.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Internals · records</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“A line is split across two blocks. Does the mapper get half a line?”</h4>
      <p class="scn__situation">Follow-up to the first question.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> the LineRecordReader rule.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>No. The reader of the first split reads past its end to finish the line (a remote read of a few bytes if needed).</li>
          <li>The reader of the next split skips its partial first line, because it belongs to the previous split.</li>
          <li>So each line is processed exactly once; only the split starting at byte 0 doesn't skip.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Performance · tuning</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>A job on one 50 GB file runs with a single mapper for 3 hours</h4>
      <p class="scn__situation">The cluster is mostly idle while it runs.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> splittability diagnosis.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Check “number of splits” in the client log; one split for 50 GB almost always means a non-splittable codec (gzip) or a custom isSplitable() returning false.</li>
          <li>Fix upstream: write splittable files (bzip2, or Parquet/ORC/Avro with block compression) or many smaller gzip files.</li>
          <li>Short term: decompress once into HDFS as plain text, or repartition with a one-off job.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Tuning · map count</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>“How do you increase or decrease the number of mappers?”</h4>
      <p class="scn__situation">Often asked right after “how is the number of mappers decided”.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> knowing which knob does what.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>More maps: lower mapreduce.input.fileinputformat.split.maxsize (or write with a smaller block size).</li>
          <li>Fewer maps: raise split.minsize, or use CombineTextInputFormat for many small files.</li>
          <li>Mention the trade-off: more maps add start-up overhead; fewer, bigger maps lose locality and parallelism.</li>
        </ul>
      </div></details>
    </article>
'''
