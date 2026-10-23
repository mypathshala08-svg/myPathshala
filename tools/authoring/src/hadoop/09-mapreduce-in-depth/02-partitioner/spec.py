import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()

META = dict(
    module='09-mapreduce-in-depth', lesson='02-partitioner', n='9.2',
    module_label='Module 9 · MapReduce in depth',
    title='Partitioner',
    desc='The MapReduce Partitioner on a real Hadoop 3.5.0 cluster: 5 lakh canteen orders, 4 reducers. The default HashPartitioner left reducer 0 empty and gave reducer 2 54% of the records; a custom CounterPartitioner put each canteen counter in its own file. A partitioner returning an invalid number failed every map task with “Illegal partition for chai (4)”. Text hashCode and the (hash & Integer.MAX_VALUE) % n formula reproduced in Python, hot keys and salting, TotalOrderPartitioner, KeyFieldBasedPartitioner, quiz and interview scenarios.',
    og_desc='4 reducers, one of them empty: see why the default partitioner did that, and write one that puts each canteen counter in its own file.',
    minutes=24, level='Intermediate',
    lead='Between map and reduce, something must decide which reducer receives each key. That is the partitioner. This lesson runs the default hash partitioner and a custom one on the same 5 lakh orders, measures every reducer\'s load, reproduces Hadoop\'s hash in Python, and breaks a job on purpose with an invalid partition number.',
    chips=['Real reducer loads measured', 'Hadoop\'s hash reproduced in Python', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Reproduce Hadoop\'s HashPartitioner',
    intro='<p>This is exactly what <code>Text.hashCode()</code> and <code>HashPartitioner</code> compute, written in Python with 32-bit arithmetic. Run it and compare with the real files from the lab: chai, dosa and vada pav in <code>part-r-00002</code>, samosa alone in <code>part-r-00003</code>, nothing in <code>part-r-00000</code>.</p>',
    code='''def text_hash(s):                        # org.apache.hadoop.io.Text.hashCode()
    h = 1
    for b in s.encode("utf-8"):
        h = (31 * h + (b if b < 128 else b - 256)) & 0xFFFFFFFF   # Java int: wraps at 32 bits
    return h - (1 << 32) if h >= (1 << 31) else h              # back to a signed int

def hash_partition(key, n):              # HashPartitioner.getPartition()
    return (text_hash(key) & 0x7FFFFFFF) % n

items = ["chai", "coffee", "dosa", "idli", "poha", "samosa", "thali", "vada pav"]
n = 4
files = {p: [] for p in range(n)}
for item in items:
    files[hash_partition(item, n)].append(item)
for p in range(n):
    print(f"part-r-0000{p}: {files[p]}")
''',
    anno=[
        ('        h = (31 * h + (b if b < 128 else b - 256)) & 0xFFFFFFFF   # Java int: wraps at 32 bits', 'Java bytes are signed and ints overflow at 32 bits; Python integers don\'t, so we mask.'),
        ('    return (text_hash(key) & 0x7FFFFFFF) % n', '& Integer.MAX_VALUE clears the sign bit, so the result of % is never negative.'),
        ('    files[hash_partition(item, n)].append(item)', 'This call happens in the map task, once for every map output record (5 lakh times in our job).'),
    ],
    tasks=[
        dict(label='1 · Hash partitions', hint='Press <b>Run</b>. Does it match the lab\'s four files exactly?', code=None),
        dict(label='2 · More reducers', hint='<b>Predict first:</b> with 3, 5 and 8 reducers, will any file be empty? Notice how every key moves when the number of reducers changes.',
             code='''def text_hash(s):
    h = 1
    for b in s.encode():
        h = (31 * h + b) & 0xFFFFFFFF
    return h

items = ["chai", "coffee", "dosa", "idli", "poha", "samosa", "thali", "vada pav"]
for n in [3, 5, 8]:
    parts = [(text_hash(i) & 0x7FFFFFFF) % n for i in items]
    print(n, "reducers:", dict(zip(items, parts)), "empty:", sorted(set(range(n)) - set(parts)))
'''),
        dict(label='3 · Counter partitioner', hint='Write the custom rule: A chai, coffee · B samosa, vada pav · C poha, idli · D dosa, thali. Add up the orders per reducer using the lab counts.',
             code='''counter = {"chai": 0, "coffee": 0, "samosa": 1, "vada pav": 1, "poha": 2, "idli": 2, "dosa": 3, "thali": 3}
orders = {"chai": 149669, "coffee": 40364, "samosa": 69884, "vada pav": 69754,
          "poha": 45336, "idli": 44774, "dosa": 49927, "thali": 30292}

def get_partition(item, n):
    return counter.get(item, 0) % n

load = [0] * 4
for item, count in orders.items():
    load[get_partition(item, 4)] += count
print(load, "busiest / average =", round(max(load) / (sum(load) / 4), 2))
'''),
        dict(label='4 · Salt the hot key', hint='Chai is 30% of all orders. Split it into chai#0 … chai#3 (by order number) and spread those sub-keys over 4 reducers. What is the busiest reducer now?',
             code='''orders = {"chai": 149669, "coffee": 40364, "samosa": 69884, "vada pav": 69754,
          "poha": 45336, "idli": 44774, "dosa": 49927, "thali": 30292}
keys = {f"chai#{i}": orders["chai"] / 4 for i in range(4)}
keys.update({k: v for k, v in orders.items() if k != "chai"})
load = [0] * 4
for k, v in sorted(keys.items(), key=lambda x: -x[1]):    # biggest first, onto the emptiest reducer
    load[load.index(min(load))] += v
print([round(x) for x in load])
'''),
        dict(label='5 · Spot the error', hint='This partitioner returns the length of the item name. Run it with 4 reducers. Hadoop would throw “Illegal partition”. Make it always return 0 … n−1.',
             code='''def get_partition(item, n):
    p = len(item)
    if not 0 <= p < n:
        raise ValueError(f"Illegal partition for {item} ({p})")
    return p

for item in ["chai", "samosa", "vada pav"]:
    print(item, get_partition(item, 4))
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: hash vs custom partitioner',
    intro='<p>Use the Module 8 lab cluster (Lesson 8.1). Copy the files below and <code>student_orders.csv</code> (made by <code>make_student_orders.py</code> in Lesson 9.1) into the namenode container\'s <code>/tmp/mr9</code> folder, compile and run the lab script. It runs three jobs, about 2 minutes in total.</p>',
    items=[
        dict(title='Item revenue with a choice of partitioner', file='ItemPartition.java',
             cmd=rd('java/ItemPartition.java') + '\n// In the mr-lab folder:\n//   docker exec lab8-namenode-1 mkdir -p /tmp/mr9\n//   docker cp ItemPartition.java lab8-namenode-1:/tmp/mr9/\n//   docker cp BadPartitioner.java lab8-namenode-1:/tmp/mr9/\n//   docker exec -it lab8-namenode-1 bash\n// Inside the container:\n//   cd /tmp/mr9 && mkdir -p classes\n//   javac -cp $(hadoop classpath) -d classes *.java && jar cf mr9.jar -C classes .',
             output='(compiles silently; the jobs are run by partitioner_lab.sh below)',
             note='The partitioner runs in the map task, so its class must be inside the job jar like the Mapper and Reducer.'),
        dict(title='A partitioner that breaks the job', file='BadPartitioner.java',
             cmd=rd('java/BadPartitioner.java'),
             output='(used by ItemPartition with -D part.mode=bad)',
             note='Every item name is at least 4 characters long, so every record gets an illegal partition.'),
        dict(title='Per-reduce-task records from the JobHistory Server', file='reduce_tasks.sh',
             cmd=rd('reduce_tasks.sh') + '\n# Inside the namenode container:\n#   bash reduce_tasks.sh job_<your job id>',
             output='r_000000  reduce input records         0  groups 0\nr_000001  reduce input records    160766  groups 4\nr_000002  reduce input records    269350  groups 3\nr_000003  reduce input records     69884  groups 1',
             note='Real output for the hash run. The same counters are on the JobHistory web UI, under each reduce task.'),
        dict(title='The whole lab', file='partitioner_lab.sh',
             cmd=rd('partitioner_lab.sh') + '\n# Inside the namenode container:\n#   bash /tmp/mr9/partitioner_lab.sh',
             output=rd('tx92.txt').strip(),
             note='Real output, unedited. Your job IDs will differ; the record counts are the same because the data is generated with a fixed seed.'),
    ],
)

TRACE = dict(
    heading='Text.hashCode() for one key, byte by byte',
    intro='<p>Follow how “chai” becomes reducer 2. Watch <code>h</code> grow by ×31 plus each byte.</p>',
    code='''key = "chai"
h = 1
for b in key.encode():
    h = 31 * h + b
p = (h & 0x7FFFFFFF) % 4
print(h, p)
''',
    notes={4: 'Hash :: c=99, h=130; h=104 → 4134; a=97 → 128251; i=105 → 3975886.',
           5: 'Partition :: 3975886 % 4 = 2, so chai goes to part-r-00002.'},
)

WORKED_INTRO = 'Three partitioner problems: an empty reducer, a balanced design, and a hot key that no partitioner can fix.'
EXAMPLES = [
    dict(level='b', tag='Concept · empty reducer', title='Why did one reducer get nothing?',
         problem='<p>A job has 6 distinct keys and 6 reducers. Assume the hash spreads keys at random. What is the chance that at least one reducer gets no key at all?</p>',
         inp='6 keys · 6 reducers',
         approach=['The only way every reducer gets a key is a perfect one-to-one spread.',
                   'Count those arrangements: 6! out of 6⁶.',
                   'Subtract from 1.'],
         code='''import math
perfect = math.factorial(6) / 6 ** 6
print(f"every reducer busy: {perfect:.1%}, at least one empty: {1 - perfect:.1%}")
''', notes={2: 'Odds :: Only 720 of 46,656 ways put exactly one key on every reducer.'},
         tryit='With few keys, more reducers than keys only wastes containers. Choose reducers by data volume, and expect hashing to be uneven when keys are few.'),
    dict(level='i', tag='Design · balance', title='Pack known key sizes onto reducers',
         problem='<p>You know the order counts per item from last month. Assign the 8 items to 4 reducers so the busiest one is as light as possible, using “biggest item first, onto the emptiest reducer”.</p>',
         inp='8 items with lab counts',
         approach=['Sort items by size, biggest first.',
                   'Give each to the reducer with the least work so far.',
                   'Turn the result into a lookup table for getPartition().'],
         code='''orders = {"chai": 149669, "samosa": 69884, "vada pav": 69754, "dosa": 49927,
          "poha": 45336, "idli": 44774, "coffee": 40364, "thali": 30292}
load, table = [0] * 4, {}
for item, n in sorted(orders.items(), key=lambda x: -x[1]):
    r = load.index(min(load))
    table[item], load[r] = r, load[r] + n
print(table)
print(load)
''', notes={5: 'Greedy :: Put the next-biggest item where there is most room.'},
         tryit='The busiest reducer still has chai\'s 149,669 orders: no table can split one key. Compare with hash (269,350) and counter (190,033).'),
    dict(level='a', tag='Skew · salting', title='Count chai orders on 4 reducers at once',
         problem='<p>Chai has 149,669 orders. Show the two-step salting plan: step 1 uses keys <code>chai#0 … chai#3</code> (order number mod 4) and computes partial counts on 4 reducers; step 2 adds the partials under the key <code>chai</code>.</p>',
         inp='20 sample chai order numbers',
         approach=['Salt: key = item + "#" + (order_id % 4).',
                   'Step 1 counts each salted key separately.',
                   'Step 2 strips the salt and adds.'],
         code='''order_ids = [5, 12, 17, 22, 31, 40, 41, 58, 63, 77, 80, 91, 99, 104, 118, 123, 130, 142, 151, 160]
step1 = {}
for oid in order_ids:
    key = f"chai#{oid % 4}"
    step1[key] = step1.get(key, 0) + 1
print("step 1:", step1)
print("step 2:", {"chai": sum(step1.values())})
''', notes={3: 'Salt :: The same item now has 4 different keys, so 4 reducers can share it.'},
         tryit='Salting only works for things you can combine in pieces (counts, sums, max). Lesson 9.1\'s rule for combiners applies here too.'),
]

QUIZ = mix([
    dict(q='What does a Partitioner decide?', options=['How input is split', 'Which reduce task receives each map output key-value pair', 'The sort order of keys', 'Where output files are stored'], answer=1,
         why='getPartition(key, value, numReduceTasks) returns the reducer number.'),
    dict(q='What is the default partitioner\'s formula?', options=['key.length() % n', '(key.hashCode() & Integer.MAX_VALUE) % numReduceTasks', 'random() % n', 'the map task number % n'], answer=1,
         why='& Integer.MAX_VALUE keeps the result non-negative.'),
    dict(q='Where does the partitioner run?', options=['In the reduce task', 'In the map task, for every map output record', 'In the ResourceManager', 'In the client before submission'], answer=1,
         why='Map output is written into per-partition sections of the sort buffer.'),
    dict(q='Why was part-r-00000 empty in the hash run?', options=['Reducer 0 crashed', 'None of the 8 item names hashed to partition 0', 'The partitioner skips 0', 'Reducer 0 only writes _SUCCESS'], answer=1,
         why='With few keys, hashing is uneven; here buckets 1, 2 and 3 got everything.'),
    dict(q='What happened when getPartition() returned 4 with 4 reducers?', options=['The record went to reducer 0', '“Illegal partition for chai (4)”: map attempts failed and the job failed', 'Hadoop added a fifth reducer', 'The record was skipped'], answer=1,
         why='Valid numbers are 0 to 3; 10 failed map attempts, job FAILED.'),
    dict(q='Chai is 30% of all orders. Can a partitioner split chai over several reducers in one job?', options=['Yes, with a round-robin partitioner', 'No, all values of one key must go to one reducer; change the key (salting) instead', 'Yes, by using more reducers', 'Yes, with TotalOrderPartitioner'], answer=1,
         why='Equal keys must always get the same partition.'),
    dict(q='When is the partitioner NOT called?', options=['When there is a combiner', 'When the job has only one reducer', 'When keys are Text', 'When the input is small'], answer=1,
         why='With one reducer every pair is partition 0.'),
    dict(q='Which partitioner gives globally sorted output across all part files?', options=['HashPartitioner', 'TotalOrderPartitioner (with a sampled partition file)', 'KeyFieldBasedPartitioner', 'BinaryPartitioner'], answer=1,
         why='Reducer 0 gets the lowest key range, reducer 1 the next, and so on.'),
])

REVISION = [
    '<b>getPartition(key, value, numReduceTasks)</b> → a number 0 … n−1; equal keys must always get the same number.',
    'Runs in the <b>map task</b> on every output record; skipped when there is 1 reducer.',
    'Default <b>HashPartitioner</b>: <code>(hashCode &amp; Integer.MAX_VALUE) % n</code>; Text hash: h = 1, h = 31h + byte.',
    'Lab, 8 items on 4 reducers: hash → 0 / 160,766 / 269,350 / 69,884 (one empty); counter partitioner → 190,033 / 139,638 / 90,110 / 80,219.',
    'Out-of-range number → <b>“Illegal partition”</b>, map attempts fail, job fails (10 failed attempts in our run).',
    'A partitioner can\'t split a hot key; <b>salt</b> the key and combine partials in a second step.',
    'Others: KeyFieldBasedPartitioner (fields of text keys), TotalOrderPartitioner + InputSampler (global sort).',
]
FAQ = [
    ('What is a Partitioner in MapReduce?', 'A Partitioner decides which reduce task receives each intermediate key-value pair. Its getPartition(key, value, numReduceTasks) method returns a number between 0 and numReduceTasks - 1, and must return the same number for equal keys so that all values of a key are processed by one reducer. The default is HashPartitioner.'),
    ('How does HashPartitioner work?', 'It computes (key.hashCode() &amp; Integer.MAX_VALUE) % numReduceTasks. The bitwise AND removes the sign so the result is never negative. For Text keys the hash is computed over the UTF-8 bytes as h = 31 * h + byte, starting from 1.'),
    ('When should I write a custom partitioner?', 'When the default layout or balance is wrong for you: to send related keys to the same reducer (for example one output file per region), to balance known key sizes, to partition a composite key by its natural part for a secondary sort, or to produce range-partitioned, globally sorted output.'),
    ('What happens if getPartition returns an invalid number?', 'The map task throws java.io.IOException: Illegal partition for &lt;key&gt; (&lt;number&gt;). The attempt fails, is retried, and after the maximum number of attempts the job fails. Always return a value modulo numReduceTasks and handle unexpected keys.'),
    ('How do I handle data skew in MapReduce?', 'Find it first with per-reduce-task counters. If several keys share an overloaded reducer, a custom partitioner can spread them. If a single key is too big, change the key: add a salt (key#0 … key#n) so it spreads across reducers, then merge the partial results in a second step, and use a combiner to shrink what is shuffled.'),
]

PRACTICE_INTRO = 'Partitioner exercises using the real loads from the lab.'
PROBLEMS = [
    dict(level='easy', title='Share of the busiest reducer', stmt='Hash run: reducer loads 0, 160,766, 269,350 and 69,884. What share of all records did the busiest reducer get?', inp='4 loads',
         code='''loads = [0, 160766, 269350, 69884]
print(f"{max(loads) / sum(loads):.1%}")
''', explain='53.9%: more than half the reduce work on one of four reducers.'),
    dict(level='easy', title='Skew factor', stmt='Compute busiest ÷ average for the hash and the counter runs.', inp='two sets of loads',
         code='''for name, loads in [("hash", [0, 160766, 269350, 69884]), ("counter", [190033, 139638, 90110, 80219])]:
    print(name, round(max(loads) / (sum(loads) / len(loads)), 2))
''', explain='2.15 vs 1.52. 1.0 would be perfectly even.'),
    dict(level='easy', title='Valid partition numbers', stmt='Which of these return values are legal with 4 reducers: -1, 0, 3, 4?', inp='4 values',
         code='''print([p for p in [-1, 0, 3, 4] if 0 <= p < 4])
''', explain='Only 0 and 3. Java\'s % can give -1 for a negative hash, which is why HashPartitioner masks the sign bit.'),
    dict(level='medium', title='Java\'s negative modulo', stmt='Java computes -7 % 4 as -3. Show why (h & 0x7FFFFFFF) % 4 is needed for a negative 32-bit hash.', inp='h = -7',
         code='''import math
h = -7
java_mod = int(math.fmod(h, 4))            # Java's % keeps the sign of h
masked = ((h & 0xFFFFFFFF) & 0x7FFFFFFF) % 4
print("java % :", java_mod, " masked:", masked)
''', explain='-3 would be an illegal partition; masking gives a valid 1.'),
    dict(level='medium', title='Partition by first letter', stmt='Write a partitioner for 3 reducers: items starting a–h → 0, i–p → 1, others → 2. Where does each item go?', inp='8 items',
         code='''def get_partition(item, n=3):
    c = item[0]
    return 0 if c <= "h" else 1 if c <= "p" else 2
for i in ["chai", "coffee", "dosa", "idli", "poha", "samosa", "thali", "vada pav"]:
    print(i, get_partition(i))
''', explain='A range partitioner: the 3 files, read in order, are sorted by item. That is the idea behind TotalOrderPartitioner.'),
    dict(level='medium', title='Composite key, natural partition', stmt='Keys are (student, time). Show that hashing the whole key scatters one student over reducers, but hashing only the student keeps them together.', inp='3 orders of S0001',
         code='''def h(s):
    x = 1
    for b in s.encode():
        x = (31 * x + b) & 0xFFFFFFFF
    return (x & 0x7FFFFFFF) % 4
keys = [("S0001", "08:09"), ("S0001", "08:15"), ("S0001", "13:40")]
print("whole key :", [h(s + t) for s, t in keys])
print("student   :", [h(s) for s, t in keys])
''', explain='The whole-key hash sends one student\'s orders to different reducers; partitioning on the student keeps them in one place, which secondary sort needs (Lesson 9.7).'),
    dict(level='business', title='Is the custom partitioner worth it?', stmt='A nightly job\'s reduce phase takes as long as its busiest reducer. Reduce time is proportional to records; the hash layout\'s busiest reducer takes 40 minutes. How long would the counter layout take, and how many minutes a year are saved?', inp='269,350 vs 190,033 records',
         code='''hash_min = 40
counter_min = 40 * 190033 / 269350
print(f"{counter_min:.0f} min, saves {(hash_min - counter_min) * 365 / 60:.0f} hours a year")
''', explain='About 28 minutes, saving roughly 72 hours of waiting a year, for a 10-line class (illustrative).'),
    dict(level='advanced', title='Sample-based range partitioner', stmt='Like InputSampler + TotalOrderPartitioner: sample student IDs, pick cut points for 4 reducers, then route keys by range.', inp='a sample of 12 student IDs',
         code='''import bisect
sample = sorted(["S0004", "S0150", "S0333", "S0450", "S0701", "S0802", "S0999",
                 "S1105", "S1260", "S1500", "S1777", "S1990"])
cuts = [sample[len(sample) * i // 4] for i in range(1, 4)]
print("cut points:", cuts)
for s in ["S0001", "S0500", "S1413", "S2000"]:
    print(s, "-> reducer", bisect.bisect_right(cuts, s))
''', explain='Each reducer gets one ID range, so part-r-00000 … 00003 concatenated are in order. A bad sample gives uneven ranges, so sample enough keys.'),
]

SCN_INTRO = 'Partitioner questions test whether you understand where keys go and how to fix skew.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Concepts · basics</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“What is a partitioner and what is the default?”</h4>
      <p class="scn__situation">Asked right after the shuffle question.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> where it runs and the formula.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>It assigns each map output pair to a reduce task: getPartition(key, value, numReduceTasks) returns 0 … n−1.</li>
          <li>It runs in the map task; the default HashPartitioner uses (hashCode &amp; Integer.MAX_VALUE) % n.</li>
          <li>Same key, same partition, so all values of a key meet in one reducer.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Performance · skew</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>“99 reducers finish in 2 minutes, one takes 50 minutes”</h4>
      <p class="scn__situation">A daily job keeps missing its deadline.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> diagnosing and fixing skew.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Check that reducer's input records and groups: one huge key, or many big keys on one partition?</li>
          <li>Many keys: a custom partitioner (or more reducers) spreads them. One key: salt it (key#0..key#n), aggregate, then merge partials.</li>
          <li>Add a combiner to cut shuffled records, and filter useless keys (nulls, “unknown”) in the map.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Design · output</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“We need one output file per region”</h4>
      <p class="scn__situation">Five regions, and each regional team wants only its own file.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> custom partitioner vs MultipleOutputs.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Set 5 reducers and a partitioner mapping each region to 0–4; each part-r file then holds one region.</li>
          <li>Handle unknown regions explicitly and use % numReduceTasks to stay in range.</li>
          <li>Alternative: MultipleOutputs to write named files per region from any reducer, without tying layout to reducer count.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Sorting · design</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>“Sort 1 TB of records by key across 200 reducers”</h4>
      <p class="scn__situation">The output must be one sorted data set when the files are read in order.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> TotalOrderPartitioner.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Each reducer's output is sorted, but HashPartitioner mixes ranges, so the files aren't globally ordered.</li>
          <li>Use InputSampler to sample keys and write a partition file of 199 cut points; TotalOrderPartitioner routes key ranges.</li>
          <li>Sample enough keys to avoid uneven ranges; this is how TeraSort works.</li>
        </ul>
      </div></details>
    </article>
'''
