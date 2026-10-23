import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()

META = dict(
    module='08-mapreduce-fundamentals', lesson='05-the-reducer', n='8.5',
    module_label='Module 8 · MapReduce fundamentals',
    title='The Reducer',
    desc='The Hadoop MapReduce Reducer on a real Hadoop 3.5.0 cluster: reduce(key, Iterable values) once per key in sorted order, setup and cleanup, HashPartitioner and how many reducers to run. Real runs: 3 reducers give files of 0, 79 and 38 bytes (keys dealt by hash, reproduced in Python), 10 reducers give 4 empty files and a speculative reduce, 0 reducers make a map-only job. The object-reuse trap caught live: chai [113456, 113456, 113456]. Output committer, _SUCCESS, skew, Python simulation, quiz and interview scenarios.',
    og_desc='Three reducers, one empty file, and the same order ID three times: two reducer surprises explained on a real cluster.',
    minutes=26, level='Intermediate',
    lead='The reducer is where the answer for each key is computed and written. This lesson shows exactly how it is called, how keys are dealt to reducers, what the number of reducers does to your output, and the one Java habit (copying values) that every Hadoop programmer learns the hard way, all with real runs on the Module 8 cluster.',
    chips=['Partitions reproduced in Python', 'Object-reuse bug caught live', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Partition, group and reduce like Hadoop',
    intro='<p>This model deals keys to reducers with Hadoop\'s real <code>Text</code> hash, groups values per key, and calls a reduce function once per key in sorted order. Its partitions match the files our cluster wrote.</p>',
    code='''pairs = [("samosa", 18), ("vada pav", 20), ("poha", 25), ("samosa", 18), ("chai", 15),
         ("idli", 30), ("dosa", 45), ("chai", 15), ("poha", 25), ("idli", 30)]

def text_hash(s):                         # Hadoop's Text.hashCode()
    h = 1
    for b in s.encode():
        h = (31 * h + b) & 0xffffffff
    return h

def partition(key, n):                    # HashPartitioner
    return (text_hash(key) & 0x7fffffff) % n

def reduce_fn(key, values):
    return f"{key}\\t{len(values)}\\t{sum(values)}"

R = 3
parts = [{} for _ in range(R)]
for k, v in pairs:
    parts[partition(k, R)].setdefault(k, []).append(v)

for r in range(R):
    lines = [reduce_fn(k, parts[r][k]) for k in sorted(parts[r])]
    print(f"part-r-{r:05d}:", lines if lines else "(empty)")
''',
    anno=[
        ('    return (text_hash(key) & 0x7fffffff) % n', 'The HashPartitioner: clear the sign bit, then modulo the number of reducers. Same key, same reducer, always.'),
        ('    lines = [reduce_fn(k, parts[r][k]) for k in sorted(parts[r])]', 'Each reducer handles its keys in sorted order, one reduce() call per key.'),
        ('    print(f"part-r-{r:05d}:", lines if lines else "(empty)")', 'Reducer 0 gets no keys but still writes a file: our part-r-00000 was 0 bytes.'),
    ],
    tasks=[
        dict(label='1 · Three reducers', hint='Press <b>Run</b>. Compare with the real files: 00001 had chai, dosa, samosa, vada pav; 00002 had idli, poha.', code=None),
        dict(label='2 · Ten reducers', hint='<b>Predict first:</b> how many of 10 files will be empty with 6 keys? Then check where each item goes.',
             code='''def text_hash(s):
    h = 1
    for b in s.encode():
        h = (31 * h + b) & 0xffffffff
    return h
items = ["chai", "dosa", "idli", "poha", "samosa", "vada pav"]
used = {}
for it in items:
    used.setdefault((text_hash(it) & 0x7fffffff) % 10, []).append(it)
for r in range(10):
    print(f"part-r-{r:05d}", used.get(r, "(empty)"))
'''),
        dict(label='3 · The reuse trap', hint='The framework reuses one value object. This simulates it with a mutable class. Fix the bug by storing a copy.',
             code='''class Text:                         # a mutable value, like Hadoop's Text
    def __init__(self): self.v = ""
    def set(self, v): self.v = v
    def __repr__(self): return self.v

def values_iterator(ids):           # like Hadoop: ONE object, refilled each step
    t = Text()
    for i in ids:
        t.set(i)
        yield t

first3 = []
for t in values_iterator(["104221", "150350", "113456"]):
    first3.append(t)                # keeps a reference, not a copy
print(first3)
'''),
        dict(label='4 · Skew check', hint='One key holds most records. Compute records per reducer for 4 reducers and the ratio of the largest to the average.',
             code='''counts = {"chai": 900_000, "dosa": 40_000, "idli": 35_000, "poha": 30_000, "samosa": 50_000, "vada pav": 45_000}
def text_hash(s):
    h = 1
    for b in s.encode():
        h = (31 * h + b) & 0xffffffff
    return h
load = [0] * 4
for k, c in counts.items():
    load[(text_hash(k) & 0x7fffffff) % 4] += c
avg = sum(load) / 4
print(load, f"largest is {max(load) / avg:.1f}x the average")
'''),
        dict(label='5 · Spot the error', hint='Values can be read only once. This reducer loops twice (once to count, once to sum). Fix it with a single pass.',
             code='''def values():                      # a one-pass iterator, like Hadoop's Iterable
    for v in [15, 15, 15]:
        yield v
vals = values()
count = sum(1 for _ in vals)
total = sum(vals)
print("average", total / count, "count", count)
assert total == 45, "second pass saw no values"
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: number of reducers and the reuse trap',
    intro='<p>Use the Module 8 lab from Lesson 8.1, with <code>canteen_orders.csv</code> in HDFS and <code>mr.jar</code> built from <code>ItemRevenue.java</code> and <code>SampleOrders.java</code>. The script runs ItemRevenue with 3, 10 and 0 reducers, lists every output file with its size and keys, then runs SampleOrders with and without copying values. It takes about 3 minutes.</p>',
    items=[
        dict(title='First three order IDs per item', file='SampleOrders.java',
             cmd=rd('java/SampleOrders.java') + '\n// Inside the namenode container, in /tmp/mr:\n//   javac -cp $(hadoop classpath) -d classes *.java && jar cf mr.jar -C classes .\n//   hadoop jar mr.jar SampleOrders /user/hadoop/data/canteen_orders.csv /out/sample_ok\n//   hadoop jar mr.jar SampleOrders -D sample.copy=false /user/hadoop/data/canteen_orders.csv /out/sample_bug',
             output='''$ hdfs dfs -cat /out/sample_ok/part-r-00000
chai	[104221, 150350, 113456]
dosa	[78778, 213441, 200658]
idli	[101007, 50991, 101001]
poha	[199796, 104049, 99562]
samosa	[151000, 300992, 300987]
vada pav	[101030, 268025, 50984]
$ hdfs dfs -cat /out/sample_bug/part-r-00000
chai	[113456, 113456, 113456]
dosa	[200658, 200658, 200658]
idli	[101001, 101001, 101001]
poha	[99562, 99562, 99562]
samosa	[300987, 300987, 300987]
vada pav	[50984, 50984, 50984]''',
             note='Real output. In the buggy run every list holds the last ID that the reused object contained. Your IDs may differ (value order within a key is not defined), but the bug pattern is the same.'),
        dict(title='3, 10 and 0 reducers, and the reuse trap', file='reducer_lab.sh',
             cmd=rd('reducer_lab.sh') + '\n# Copy into the namenode container and run:\n#   docker cp reducer_lab.sh lab8-namenode-1:/tmp/mr/\n#   docker exec lab8-namenode-1 bash /tmp/mr/reducer_lab.sh',
             output=rd('tx85.txt').strip(),
             note='Real output, unedited. The empty files and their positions follow directly from the hash of each item name; “Launched reduce tasks=11” for 10 reducers includes one speculative attempt.'),
    ],
)

TRACE = dict(
    heading='How a reducer walks through its keys',
    intro='<p>A reducer\'s input is one sorted stream of (key, value) pairs. Grouping means: keep reading while the key stays the same, then call reduce for that key.</p>',
    code='''stream = [("chai", 15), ("chai", 15), ("dosa", 45), ("samosa", 18), ("samosa", 18)]
current, values = None, []
for key, value in stream:
    if key != current and current is not None:
        print("reduce", current, sum(values))
        values = []
    current = key
    values.append(value)
print("reduce", current, sum(values))
''',
    notes={4: 'New key :: The stream is sorted, so a change of key means the previous group is complete.',
           5: 'Call :: One reduce call per key; the values were collected only for this key.',
           9: 'Last group :: The final key is reduced when the stream ends.'},
)

WORKED_INTRO = 'Three reducer problems: choosing the count, predicting output files, and spotting skew.'
EXAMPLES = [
    dict(level='b', tag='Sizing · count', title='How many reducers for this cluster?',
         problem='<p>A cluster has 20 workers, each able to run 6 reduce containers at once. Using Hadoop\'s guideline of 0.95 or 1.75 × total containers, what are the two candidate reducer counts?</p>',
         inp='20 nodes × 6 containers',
         approach=['Total containers = nodes × containers per node.',
                   '0.95 × total: all reducers start in one wave.',
                   '1.75 × total: two waves, better load balancing.'],
         code='''slots = 20 * 6
print("one wave :", int(0.95 * slots))
print("two waves:", int(1.75 * slots))
''', notes={2: 'One wave :: Slightly below capacity leaves room for failed tasks to rerun.'},
         tryit='Then check the output: if the job writes 20 GB, 114 reducers give files of about 180 MB each, which is healthy.'),
    dict(level='i', tag='Prediction · files', title='Which file will each item land in?',
         problem='<p>Using Hadoop\'s Text hash and the HashPartitioner, predict the output file of each item for 4 reducers.</p>',
         inp='6 items · 4 reducers',
         approach=['Take each item\'s Text hash with the sign bit cleared (h = 31h + byte, 32-bit).',
                   'Take the remainder by 4.',
                   'Group the items by remainder.'],
         code='''hashes = {"chai": 3975886, "dosa": 4012954, "idli": 4151129,      # Text hash & MAX_VALUE,
          "poha": 4370105, "samosa": 2125311487, "vada pav": 827806702}  # computed as in the Run box
files = {}
for item, h in hashes.items():
    files.setdefault(h % 4, []).append(item)
for r in range(4):
    print(f"part-r-{r:05d}", files.get(r, []))
''', notes={5: 'Partition :: The same arithmetic Hadoop uses: (hash & Integer.MAX_VALUE) % reducers.'},
         tryit='Change 4 to 3 and you get exactly the files from our lab.'),
    dict(level='a', tag='Skew · diagnosis', title='Why does one reducer take an hour?',
         problem='<p>A job with 50 reducers shows 49 reducers finishing in 2 minutes and one running for 60. The reducer counters show “Reduce input records” of about 2 lakh for most tasks and 9 crore for the slow one. What is the cause, and roughly how much faster could the job be if the load were spread evenly?</p>',
         inp='49 × 2 lakh records · 1 × 9 crore records · 60 min',
         approach=['The slow reducer has about 450× more records: one hot key.',
                   'Time is roughly proportional to records.',
                   'Even spread = total records / 50 per reducer.'],
         code='''normal, hot = 200_000, 90_000_000
total = 49 * normal + hot
per_minute = hot / 60
even = total / 50
print(f"hot reducer has {hot / normal:.0f}x the normal load")
print(f"even spread: {even:,.0f} records each, about {even / per_minute:.1f} min")
''', notes={4: 'Even :: Adding reducers does not help: one key always goes to one reducer.'},
         tryit='The fix is in the key, not the reducer count: combine early (9.1), or salt the hot key into several sub-keys and add the results in a second step.'),
]

QUIZ = mix([
    dict(q='How often is reduce() called in a reduce task?', options=['Once per record', 'Once per distinct key in its partition, in sorted key order', 'Once per map task', 'Once per reduce task'], answer=1,
         why='setup once, reduce per key, cleanup once.'),
    dict(q='What is the default number of reducers in Hadoop MapReduce?', options=['0', '1', 'One per DataNode', 'Equal to the number of maps'], answer=1,
         why='mapreduce.job.reduces defaults to 1.'),
    dict(q='With 3 reducers, our part-r-00000 was empty. Why?', options=['Reducer 0 crashed', 'No item name hashed to partition 0', 'The file was still being written', 'HDFS hides small files'], answer=1,
         why='Keys are assigned by (hash & MAX) % 3; none of the six items gave 0.'),
    dict(q='Why did every item show the same order ID three times without a copy?', options=['The data had duplicates', 'The values iterator reuses one Text object, so the list held three references to it', 'The mapper emitted each ID three times', 'The partitioner was wrong'], answer=1,
         why='Copy what you keep: new Text(value).'),
    dict(q='What happens with mapreduce.job.reduces=0?', options=['The job fails', 'A map-only job: no shuffle or sort, output files part-m-*', 'One reducer is used anyway', 'Maps write to the NameNode'], answer=1,
         why='Our run wrote part-m-00000 with unsorted map output.'),
    dict(q='Is the output of a job with several reducers globally sorted?', options=['Yes, always', 'No: each part file is sorted, but keys are spread across files by hash', 'Only if there are 10 reducers', 'Only for numeric keys'], answer=1,
         why='Use one reducer or TotalOrderPartitioner for a global order.'),
    dict(q='In what order do the values of one key arrive at the reducer?', options=['Sorted ascending', 'In no guaranteed order', 'In input file order', 'Sorted descending'], answer=1,
         why='Our IDs came as 104221, 150350, 113456; ordering values needs a secondary sort.'),
    dict(q='Which change does NOT fix a reducer overloaded by one hot key?', options=['Adding a combiner', 'Salting the hot key', 'Doubling the number of reducers', 'A custom partitioner'], answer=2,
         why='All values of one key still go to a single reducer.'),
])

REVISION = [
    '<code>Reducer&lt;KEYIN, VALUEIN, KEYOUT, VALUEOUT&gt;</code>: setup once, <b>reduce(key, values, ctx)</b> once per key in sorted order, cleanup once.',
    'Keys go to reducers by <b>HashPartitioner</b>: <code>(hash &amp; MAX_VALUE) % reduces</code>; same key → same reducer.',
    'Default 1 reducer; set with <code>setNumReduceTasks</code> or <code>-D mapreduce.job.reduces</code>; guideline 0.95 or 1.75 × containers.',
    'Lab: 3 reducers → 0, 79, 38 bytes; 10 reducers → 4 empty files; 0 reducers → part-m-00000, unsorted.',
    '<b>Values are a one-pass iterator over a reused object</b>: aggregate as you go, copy anything you keep.',
    'Value order within a key is undefined; each part file is sorted, not the whole output.',
    'Output: part-r-NNNNN via the output committer (_temporary → final), then _SUCCESS; replicated in HDFS.',
    'Skew: one hot key = one slow reducer; more reducers don\'t help.',
]
FAQ = [
    ('What does the Reducer do in Hadoop MapReduce?', 'After the shuffle and sort, each reduce task receives a partition of the intermediate keys. For each key, in sorted order, Hadoop calls reduce(key, values, context) with all the values for that key. The reducer typically aggregates them and writes output records, which go to one file per reduce task (part-r-NNNNN) in HDFS.'),
    ('How do I set the number of reducers?', 'In the driver call job.setNumReduceTasks(n), or pass -D mapreduce.job.reduces=n on the command line when the driver uses GenericOptionsParser or ToolRunner. The default is 1. The Hadoop documentation suggests 0.95 or 1.75 times (nodes × maximum containers per node); in practice also aim for output files of reasonable size.'),
    ('Why are some reducer output files empty?', 'Keys are assigned to reducers by the partitioner, by default (key.hashCode() &amp; Integer.MAX_VALUE) % numReduceTasks. If no key hashes to a given partition, that reducer receives nothing but still writes its (empty) part file. In our lab, 6 keys and 10 reducers left 4 files empty.'),
    ('Why do I get the same value repeated when I store reducer values in a list?', 'Hadoop reuses a single Writable instance for the values of the Iterable and refills it at every step. Storing the object stores a reference to that one instance, which ends up holding the last value. Store a copy instead, for example new Text(value) or the primitive from value.get().'),
    ('Can a MapReduce job have zero reducers?', 'Yes. With setNumReduceTasks(0) the job is map-only: there is no shuffle or sort, and each map task writes its output directly to the output directory as part-m-NNNNN. This is used for filtering, cleaning and conversion jobs.'),
]

PRACTICE_INTRO = 'Reducer exercises using the real files and counters from our lab.'
PROBLEMS = [
    dict(level='easy', title='Bytes per file', stmt='part-r-00001 (chai, dosa, samosa, vada pav) is 79 bytes and part-r-00002 (idli, poha) is 38. Check 79 by building the four lines.', inp='4 output lines',
         code='''lines = ["chai\\t50170\\t752550", "dosa\\t49948\\t2247660", "samosa\\t50021\\t900378", "vada pav\\t49986\\t999720"]
print(sum(len(l) + 1 for l in lines), "bytes")
''', explain='79: each line plus its newline character.'),
    dict(level='easy', title='Empty files', stmt='With 6 keys and 10 reducers, how many files must be empty at the very least?', inp='6 keys · 10 reducers',
         code='''print(10 - 6, "at least; more if two keys share a reducer")
''', explain='4, which is exactly what we got: every item happened to land on a different reducer.'),
    dict(level='easy', title='Reducer input', stmt='The reducer saw Reduce input records=300000 and Reduce input groups=6. How many values per reduce() call, on average?', inp='300,000 / 6',
         code='''print(300000 / 6)
''', explain='50,000 values per call: each item has about 50,000 orders.'),
    dict(level='medium', title='Single pass', stmt='Write a reducer that returns count, sum and max of a key\'s values in ONE loop over an iterator.', inp='iterator of amounts',
         code='''def reduce_fn(key, values):
    n = s = 0
    m = None
    for v in values:
        n += 1; s += v
        m = v if m is None or v > m else m
    return key, n, s, m
print(reduce_fn("dosa", iter([45, 45, 40, 45])))
''', explain='One pass is all you get; keep running totals instead of a list.'),
    dict(level='medium', title='Group a sorted stream', stmt='Given a sorted stream of (key, value), produce one line per key with the sum, without building a dictionary.', inp='sorted pairs',
         code='''from itertools import groupby
stream = [("chai", 15), ("chai", 15), ("idli", 30), ("poha", 25), ("poha", 25)]
for key, group in groupby(stream, key=lambda kv: kv[0]):
    print(key, sum(v for _, v in group))
''', explain='This is how Hadoop groups: the input is sorted, so equal keys are next to each other.'),
    dict(level='medium', title='Partition a new item', stmt='The canteen adds “upma”. With 3 reducers, which file will it go to?', inp='“upma”, 3 reducers',
         code='''h = 1
for b in "upma".encode():
    h = (31 * h + b) & 0xffffffff
print("part-r-%05d" % ((h & 0x7fffffff) % 3))
''', explain='The hash decides; adding one key never moves the other items.'),
    dict(level='business', title='Files per day', stmt='A daily job uses 400 reducers and writes 8 GB. A team keeps the output for a year. How many files and what average size? Suggest a better reducer count for files of about 256 MB.', inp='400 reducers · 8 GB/day · 365 days',
         code='''files = 400 * 365
print(f"{files:,} files a year, {8 * 1024 / 400:.0f} MB each")
print("better reducer count:", 8 * 1024 // 256)
''', explain='1,46,000 files of 20 MB a year; 32 reducers would give 256 MB files and about 11,700 files (Lesson 7.5).'),
    dict(level='advanced', title='Salting a hot key', stmt='chai has 9 lakh records and the other keys 50,000 each. Salt chai into 4 sub-keys (chai#0 … chai#3) and show the load per reducer drops, then combine the salted totals.', inp='record counts per key',
         code='''counts = {"chai": 900_000, "dosa": 50_000, "idli": 50_000, "poha": 50_000}
salted = {}
for k, c in counts.items():
    parts = 4 if k == "chai" else 1
    for i in range(parts):
        key = f"{k}#{i}" if parts > 1 else k
        salted[key] = c // parts
print("largest group before:", max(counts.values()), "after:", max(salted.values()))
total_chai = sum(v for k, v in salted.items() if k.startswith("chai#"))
print("chai recombined:", total_chai)
''', explain='The biggest reduce group drops from 9 lakh to 2.25 lakh records; a small second step adds chai#0 … chai#3 back to 9 lakh.'),
]

SCN_INTRO = 'Reducer questions test whether you have actually written MapReduce code: partitioning, reducer count and object reuse come up again and again.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Concepts · partitioning</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“How does Hadoop decide which reducer gets a key?”</h4>
      <p class="scn__situation">A standard follow-up after explaining word count.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> the Partitioner and its guarantee.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>The Partitioner; by default HashPartitioner: (key.hashCode() &amp; Integer.MAX_VALUE) % numReduceTasks.</li>
          <li>Guarantee: all values of one key go to the same reducer, so reduce sees the complete group.</li>
          <li>Side effect: load depends on key distribution; few keys or a hot key give uneven reducers (we saw files of 0, 79 and 38 bytes).</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Coding · bug</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>A reducer collects values into a list and all entries are identical</h4>
      <p class="scn__situation">Code review of a reducer that builds a list of the last 10 transactions per customer.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> knowledge of Writable reuse.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Hadoop reuses one key and one value object while iterating; the list stores references to the same instance.</li>
          <li>Fix: add a copy (new Text(v), WritableUtils.clone, or extract primitives).</li>
          <li>Also check memory: collecting all values of a hot key can exhaust the heap; keep only what is needed.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Performance · skew</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>The job is stuck at “reduce 99%” for an hour</h4>
      <p class="scn__situation">All but one reducer finished quickly.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> skew diagnosis and fixes.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Compare “Reduce input records” and shuffle bytes per reduce task; one task with far more input means a hot key.</li>
          <li>Find the key (sample the map output or count keys in a quick job); often null or a default value.</li>
          <li>Fix: filter or handle the junk key, use a combiner, salt the hot key and merge in a second step, or a custom partitioner. More reducers alone won't help.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Design · output</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“I need one sorted output file. Do I set 1 reducer?”</h4>
      <p class="scn__situation">An analyst wants a single report file sorted by customer.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> trade-offs between one reducer and total order.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>1 reducer works for small outputs, but all data passes through one task: slow for big outputs.</li>
          <li>For large data use TotalOrderPartitioner (sampled key ranges), so files 0 … n−1 are in order and can be concatenated.</li>
          <li>Or keep many reducers and sort/merge downstream (getmerge only concatenates, it does not sort).</li>
        </ul>
      </div></details>
    </article>
'''
