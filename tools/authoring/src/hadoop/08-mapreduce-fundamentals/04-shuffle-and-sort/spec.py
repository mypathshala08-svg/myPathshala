import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()

META = dict(
    module='08-mapreduce-fundamentals', lesson='04-shuffle-and-sort', n='8.4',
    module_label='Module 8 · MapReduce fundamentals',
    title='Shuffle and sort',
    desc='The MapReduce shuffle and sort measured on a real Hadoop 3.5.0 cluster: the map-side sort buffer (io.sort.mb, “soft limit at 13421773”), 18 vs 5 vs 2 spills, “Merging 18 sorted segments” with io.sort.factor 10, Spilled Records 31,354,091 vs 27,000,000 explained, 107,999,586 bytes fetched by the reducer, HashPartitioner sending 4 items to one reducer and none to another, slowstart, fetchers, the ShuffleHandler and sorted reducer input. Python simulations of spill-and-merge and the partitioner, quiz and interview scenarios.',
    og_desc='Same job, same answer, 18 spills or 2: open the shuffle between map and reduce on a real cluster and read every counter.',
    minutes=30, level='Intermediate',
    lead='Between map() writing a pair and reduce() receiving it, Hadoop partitions, sorts, spills to disk, merges, copies over the network and merges again. This lesson opens that box on a real cluster: the same job with three sort-buffer sizes, the task logs that show every spill and merge pass, and the counters that tell you what it cost.',
    chips=['18 spills vs 2, measured', 'HashPartitioner reproduced', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Simulate the map-side sort buffer, spills and merge',
    intro='<p>A tiny map task: the buffer holds only 4 pairs, so it spills often. Each spill is sorted by (partition, key). At the end the spills are merged with at most <code>FACTOR</code> files per pass, just like <code>io.sort.factor</code>.</p>',
    code='''import heapq
BUFFER, FACTOR, REDUCERS = 4, 3, 2
pairs = [("samosa", 18), ("chai", 15), ("poha", 25), ("dosa", 45), ("chai", 15),
         ("idli", 30), ("samosa", 18), ("chai", 15), ("vada pav", 20), ("poha", 25)]

def part(key):                                  # same formula as Hadoop's HashPartitioner on Text
    h = 1
    for b in key.encode():
        h = (31 * h + b) & 0xFFFFFFFF
    return (h & 0x7FFFFFFF) % REDUCERS

spills, buf, written = [], [], 0
for k, v in pairs:
    buf.append((part(k), k, v))
    if len(buf) == BUFFER:                      # buffer full: sort and spill
        spills.append(sorted(buf)); written += len(buf); buf = []
if buf:
    spills.append(sorted(buf)); written += len(buf)
print(len(spills), "spills:", [[k for p, k, v in s] for s in spills])

passes = 0
while len(spills) > 1:                          # merge at most FACTOR files per pass
    group, spills = spills[:FACTOR], spills[FACTOR:]
    merged = list(heapq.merge(*group))
    written += len(merged); passes += 1
    spills.append(merged)
print("merge passes:", passes, "| records written to disk on the map side:", written)
for p, k, v in spills[0]:
    print("partition", p, k, v)
''',
    anno=[
        ('def part(key):                                  # same formula as Hadoop\'s HashPartitioner on Text', 'Text.hashCode() is WritableComparator.hashBytes: start at 1, multiply by 31, add each (signed) byte. ASCII bytes are positive, so this matches exactly.'),
        ('    if len(buf) == BUFFER:                      # buffer full: sort and spill', 'Hadoop spills at 80% (spill.percent), in a background thread, while the map keeps writing.'),
        ('    merged = list(heapq.merge(*group))', 'Merging sorted files never needs to load them fully: it reads the smallest head of each, like heapq.merge.'),
    ],
    tasks=[
        dict(label='1 · Spill and merge', hint='Press <b>Run</b>. Count how many records were written: why is it more than 10? Then set <code>FACTOR = 10</code> and run again.', code=None),
        dict(label='2 · Reproduce the 3 reducers', hint='<b>Predict first:</b> in our lab with 3 reducers, part-r-00000 was empty. Which partition does each item get with 3 and with 10 reducers?',
             code='''def text_hash(s):
    h = 1
    for b in s.encode():
        h = (31 * h + b) & 0xFFFFFFFF
    return h

items = ["chai", "dosa", "idli", "poha", "samosa", "vada pav"]
for r in (3, 10):
    print(r, "reducers:", {k: (text_hash(k) & 0x7FFFFFFF) % r for k in items})
'''),
        dict(label='3 · Spilled Records', hint='Explain our counters: 9,000,000 map output records. With 2–10 spills, Spilled Records was 27,000,000; with 18 spills 31,354,091. How many records were written in the extra merge pass?',
             code='''out = 9_000_000
normal = out * 2 + out          # map: spill + final merge; reduce: 1 write
print("2-10 spills:", normal)
print("extra pass wrote:", 31_354_091 - normal, "records, about", round((31_354_091 - normal) / out * 18), "of 18 spills")
'''),
        dict(label='4 · How many spills?', hint='A map emits 108 MB of materialized output with io.sort.mb = 16 and spill.percent 0.80. Estimate the number of spills, then try 64 and 200. (Real: 18, 5, 2; the buffer also stores 16 bytes of metadata per record.)',
             code='''import math
data_mb, records = 108, 9_000_000
for mb in (16, 64, 200):
    usable = mb * 0.8
    need = data_mb + records * 16 / 1024**2       # data + per-record metadata in the buffer
    print(mb, "MB buffer ->", math.ceil(need / usable), "spills (estimate)")
'''),
        dict(label='5 · Spot the error', hint='Java hash codes can be negative (int overflow), and Java\'s <code>%</code> keeps the sign. This partitioner forgot the <code>&amp; Integer.MAX_VALUE</code> step and returns a negative reducer number. Fix it.',
             code='''import math
reducers = 3
h = -1234567891                          # a negative Java hash code
p = int(math.fmod(h, reducers))          # Java's % : the result keeps the sign of h
files = ["part-r-00000", "part-r-00001", "part-r-00002"]
assert p >= 0, f"partition {p} is negative: Illegal partition"
print(files[p])
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: three sort buffers, one job',
    intro='<p>Run this inside the namenode container of the Module 8 lab (Lesson 8.1), in <code>/tmp/mr</code> where <code>mr.jar</code> and <code>orders_x30.csv</code> already are. It runs ItemRevenue three times with a different <code>mapreduce.task.io.sort.mb</code>, prints the shuffle counters, counts the spills in the map task log with <code>yarn logs</code>, and shows the merge passes. It takes about 3 minutes.</p>',
    items=[
        dict(title='Shuffle lab', file='shuffle_lab.sh',
             cmd=rd('shuffle_lab.sh') + '\n# In the mr-lab folder:\n#   docker cp shuffle_lab.sh lab8-namenode-1:/tmp/mr/\n#   docker exec lab8-namenode-1 bash /tmp/mr/shuffle_lab.sh',
             output=rd('tx84.txt').strip(),
             note='Real output. Log aggregation must be on (yarn.log-aggregation-enable=true in the lab config) for yarn logs to work after the job. Times vary; the spill counts and Spilled Records do not, for the same data and buffer.'),
    ],
)

TRACE = dict(
    heading='Merging three sorted spill files',
    intro='<p>The merger never re-sorts: it repeatedly takes the smallest head among the sorted files. Watch the output grow in key order.</p>',
    code='''import heapq
s0 = [("chai", 15), ("samosa", 18)]
s1 = [("chai", 15), ("dosa", 45)]
s2 = [("idli", 30), ("poha", 25)]
merged = []
for pair in heapq.merge(s0, s1, s2):
    merged.append(pair)
print([k for k, v in merged])
''',
    notes={6: 'Merge :: Each step looks only at the first remaining pair of each file.',
           8: 'Result :: One sorted stream: equal keys are now next to each other, ready for reduce().'},
)

WORKED_INTRO = 'Three shuffle calculations: traffic, buffer sizing and skew.'
EXAMPLES = [
    dict(level='b', tag='Traffic · all-to-all', title='How many pieces does the shuffle copy?',
         problem='<p>A job has 800 map tasks and 50 reducers. Each map writes one partition per reducer. How many map-output pieces are fetched, and how many fetch threads work at once if every reducer uses the default 5?</p>',
         inp='800 maps · 50 reducers · 5 fetchers',
         approach=['Pieces = maps × reducers.',
                   'Parallel fetches = reducers × parallelcopies.',
                   'Each fetcher handles pieces one after another.'],
         code='''maps, reducers, fetchers = 800, 50, 5
print(maps * reducers, "pieces;", reducers * fetchers, "fetches in parallel;",
      maps * reducers // (reducers * fetchers), "rounds")
''', notes={2: 'All-to-all :: Every reducer needs something from every map.'},
         tryit='Double the reducers to 100: the pieces double too, and each one is half as big. Many tiny pieces are slow to fetch.'),
    dict(level='i', tag='Tuning · buffer', title='Pick io.sort.mb so a map spills once',
         problem='<p>Each map task emits 150 MB of map output (2 crore records). The buffer also needs 16 bytes of metadata per record, and a spill starts at 80%. What io.sort.mb avoids a second spill, and what container size does that suggest?</p>',
         inp='150 MB data · 2 crore records · 16 B metadata · 0.80',
         approach=['Buffer need = data + records × 16 B.',
                   'Divide by 0.8 for the spill threshold.',
                   'The heap must hold the buffer plus the task itself.'],
         code='''import math
need = 150 + 2e7 * 16 / 1024**2
mb = math.ceil(need / 0.8)
print(f"io.sort.mb >= {mb} MB; heap about {mb + 200} MB; container about {math.ceil((mb + 200) / 0.8)} MB")
''', notes={3: 'Threshold :: The spill starts at 80% full.'},
         tryit='If that container is too big for your cluster, compress map output or add a combiner first: it shrinks the data instead of growing the buffer.'),
    dict(level='a', tag='Skew · partitions', title='When one reducer gets everything',
         problem='<p>Orders per city are partitioned by city over 4 reducers. Mumbai has 70% of all orders. Using a simple partitioner (city index % 4), how much does each reducer receive out of 10 crore records, and how long does the slowest take at 50 lakh records per minute?</p>',
         inp='city shares · 4 reducers · 50 lakh rec/min',
         approach=['Sum the shares per partition.',
                   'Time = records / speed for each reducer.',
                   'The job waits for the slowest.'],
         code='''shares = {"Mumbai": .70, "Pune": .10, "Delhi": .08, "Chennai": .06, "Kolkata": .04, "Jaipur": .02}
load = [0.0] * 4
for i, (city, s) in enumerate(shares.items()):
    load[i % 4] += s * 100_000_000
for r, n in enumerate(load):
    print(f"reducer {r}: {n / 1e7:.1f} crore records, {n / 5_000_000:.0f} min")
''', notes={4: 'Skew :: The key decides the reducer, no matter how big that key is.'},
         tryit='Salting splits the hot key (Mumbai_0 … Mumbai_3) across reducers, and a second small step adds the parts. Lesson 9.2 builds a custom partitioner.'),
]

QUIZ = mix([
    dict(q='Where does map output go before reducers fetch it?', options=['HDFS with replication 3', 'The local disk of the worker that ran the map', 'The ResourceManager', 'The reducer\'s memory directly'], answer=1,
         why='It is served by the NodeManager\'s ShuffleHandler; if lost, the map is rerun.'),
    dict(q='What does “soft limit at 13421773” mean for io.sort.mb = 16?', options=['The map may emit at most 13,421,773 records', 'A spill starts when the 16 MB buffer is 80% full', 'The reducer heap size', 'The maximum file size in HDFS'], answer=1,
         why='16,777,216 × 0.80 = 13,421,773 (mapreduce.map.sort.spill.percent).'),
    dict(q='Why did the 16 MB run need an extra merge pass?', options=['It had 18 spills, more than io.sort.factor (10)', 'The reducer failed', 'Compression was on', 'There were 3 reducers'], answer=0,
         why='“Merging 9 intermediate segments out of a total of 18”, then the last 10.'),
    dict(q='Spilled Records was 27,000,000 for 9,000,000 map output records. Why 3×?', options=['Replication 3', 'Map spill + map final merge + reducer write', 'Three reducers', 'Three map tasks'], answer=1,
         why='With one spill only, it would have been 2× (18,000,000).'),
    dict(q='How does the default partitioner choose a reducer?', options=['Round robin', '(key.hashCode() & Integer.MAX_VALUE) % numReduceTasks', 'Alphabetically', 'By map task number'], answer=1,
         why='HashPartitioner. Our 3-reducer run left part-r-00000 empty.'),
    dict(q='In what order does a reducer receive keys?', options=['Random', 'Sorted by key within that reducer', 'In the order the maps finished', 'Sorted across all reducers'], answer=1,
         why='Each part file is sorted; there is no global order across part files by default.'),
    dict(q='When do reducers start fetching map output (by default)?', options=['After all maps finish', 'After 5% of maps have finished (slowstart 0.05)', 'Before any map starts', 'Only after the job is 50% done'], answer=1,
         why='Copying overlaps with the remaining maps; reduce() itself waits for every map.'),
    dict(q='Which change does NOT reduce shuffle traffic?', options=['A combiner', 'Compressing map output', 'Filtering records in the mapper', 'A bigger io.sort.mb'], answer=3,
         why='A bigger buffer means fewer spills (less local disk I/O), but the same bytes still travel.'),
])

REVISION = [
    'Map side: <b>partition</b> → circular <b>buffer</b> (<code>io.sort.mb</code>) → sort by (partition, key) → [combiner] → <b>spill</b> at 80% → <b>merge</b> (<code>io.sort.factor</code> 10) → one sorted file per map on local disk.',
    'Reduce side: after slowstart (5%), <b>fetchers</b> (5) copy the reducer\'s partition from every map via the NodeManager <b>ShuffleHandler</b> (13562) → merge → <code>reduce()</code> per key, keys sorted.',
    'Lab: io.sort.mb 16/64/200 → 18/5/2 spills; Spilled Records 31,354,091 / 27,000,000 / 27,000,000; shuffle bytes 107,999,586 every time.',
    'Spilled Records ideal = 2 × map output; 3× with several spills; more with extra merge passes.',
    'HashPartitioner: <code>(hash &amp; MAX_VALUE) % R</code>. 3 reducers: 4 items in part 1, 2 in part 2, part 0 empty.',
    'Keys are sorted within each reducer, not globally. Number of reducers = number of output files.',
    'Reduce shuffle cost: emit less, combiner, compress map output; then tune the buffer.',
]
FAQ = [
    ('What is shuffle and sort in MapReduce?', 'It is the framework phase between map and reduce. Map output pairs are partitioned by key, sorted and written to the map node\'s local disk; each reducer then copies its partition from every map over HTTP, merges the copies into one sorted stream and calls reduce once per key with all its values. The programmer does not write it, but can customise it with a partitioner, sort and grouping comparators and a combiner.'),
    ('What is a spill in Hadoop MapReduce?', 'Map output is first collected in an in-memory circular buffer of mapreduce.task.io.sort.mb. When it reaches mapreduce.map.sort.spill.percent (80% by default), a background thread sorts the contents by partition and key, runs the combiner if one is set, and writes them to a spill file on local disk. At the end of the map, all spill files are merged into one output file.'),
    ('Where is the intermediate output of a map task stored?', 'On the local disk of the node that ran the map task (in the NodeManager\'s local directories), not in HDFS. It is temporary and served to reducers by the NodeManager\'s shuffle service. If that node fails before the reducers have fetched it, the map task is re-executed elsewhere.'),
    ('What is the role of the partitioner?', 'It decides which reducer receives each intermediate key, so that all values of a key reach the same reducer. The default HashPartitioner computes (key.hashCode() &amp; Integer.MAX_VALUE) % numReduceTasks. A custom partitioner can balance load or route ranges of keys to reducers (for example for a total sort).'),
    ('Are keys sorted in the final output of a MapReduce job?', 'Within each reducer\'s output file, yes: the reducer processes keys in sorted order. Across output files there is no global order with the default hash partitioner, because keys are spread by hash. A global order needs one reducer or a range partitioner such as TotalOrderPartitioner.'),
]

PRACTICE_INTRO = 'Shuffle exercises using the real counters and log lines from the lab.'
PROBLEMS = [
    dict(level='easy', title='Soft limit', stmt='Compute the spill threshold in bytes for io.sort.mb = 16, 64 and 100 with spill.percent 0.80.', inp='MB × 1,048,576 × 0.8',
         code='''for mb in (16, 64, 100):
    print(mb, int(mb * 1024 * 1024 * 0.8))
''', explain='13,421,772 for 16 MB; the log printed 13421773 because Hadoop rounds the float.'),
    dict(level='easy', title='Spills to merge passes', stmt='With io.sort.factor 10, how many merge passes do 2, 5, 10, 18 and 40 spills need (roughly: keep merging up to 10 at a time until one file is left)?', inp='spills, factor 10',
         code='''for spills in (2, 5, 10, 18, 40):
    n, passes = spills, 0
    while n > 1:
        n = n - min(10, n) + 1
        passes += 1
    print(spills, "spills ->", passes, "pass(es)")
''', explain='1 pass up to 10 spills, 2 for 18 (our log: 9 merged first, then the last 10). Hadoop chooses the first pass size cleverly so the final pass has exactly 10.'),
    dict(level='easy', title='Pieces to fetch', stmt='Our 422 MB job had 4 maps and 1 reducer: “Shuffled Maps =4”. How many pieces would 4 maps and 3 reducers create?', inp='maps × reducers',
         code='''print(4 * 1, "and", 4 * 3)
''', explain='4 and 12: every reducer fetches one piece from every map.'),
    dict(level='medium', title='Partition a new item', stmt='The canteen adds “pav bhaji” and “masala chai”. Which of 3 reducers will each go to?', inp='HashPartitioner on Text',
         code='''def p(s, r):
    h = 1
    for b in s.encode():
        h = (31 * h + b) & 0xFFFFFFFF
    return (h & 0x7FFFFFFF) % r
for item in ["pav bhaji", "masala chai"]:
    print(item, p(item, 3))
''', explain='The partition depends only on the bytes of the key and the number of reducers, so you can predict it before running the job.'),
    dict(level='medium', title='Materialized bytes', stmt='Map output bytes were 89,999,580 and materialized bytes 107,999,586 for 9,000,000 records. How many extra bytes per record does the intermediate format add?', inp='two counters',
         code='''print((107_999_586 - 89_999_580) / 9_000_000, "bytes per record")
''', explain='About 2 bytes: the key length and value length, each stored as a 1-byte variable-length integer for these small records (plus a few bytes of checksum per file).'),
    dict(level='medium', title='Merge sorted runs', stmt='Merge three sorted lists of keys without sorting the combined list.', inp='3 sorted runs',
         code='''import heapq
runs = [["chai", "dosa", "poha"], ["chai", "idli"], ["dosa", "samosa", "vada pav"]]
print(list(heapq.merge(*runs)))
''', explain='This is exactly what the map-side merger and the reducer\'s merger do with spill files and fetched segments.'),
    dict(level='business', title='Is a bigger buffer worth it?', stmt='A nightly job runs 2,000 maps. Raising io.sort.mb from 100 to 300 MB saves 3 s per map (fewer spills) but each map container grows by 256 MB. The cluster has spare memory only for 1,800 maps at once at the bigger size (vs 2,000 now). Which is faster overall if each map takes 60 s?', inp='2,000 maps · 60 s vs 57 s · 2,000 vs 1,800 slots',
         code='''import math
now = math.ceil(2000 / 2000) * 60
big = math.ceil(2000 / 1800) * 57
print(f"now {now} s, bigger buffer {big} s")
''', explain='60 s vs 114 s: the saving per task is lost because the maps no longer fit in one wave. Tuning must consider the whole cluster.'),
    dict(level='advanced', title='Simulate slowstart', stmt='10 maps finish at seconds 20, 22, 25, 30, 31, 33, 40, 41, 45, 60. Reducers start when slowstart × maps have finished. When do they start for 0.05, 0.5 and 1.0, and how many seconds of copying can overlap the maps?', inp='finish times, slowstart',
         code='''import math
done = [20, 22, 25, 30, 31, 33, 40, 41, 45, 60]
for s in (0.05, 0.5, 1.0):
    need = max(1, math.ceil(s * len(done)))
    start = sorted(done)[need - 1]
    print(f"slowstart {s}: reducers start at {start} s, can copy for {60 - start} s while maps run")
''', explain='Early start overlaps copying with slow maps, but the reducer holds its container while waiting; busy clusters often raise slowstart to 0.8 or so.'),
]

SCN_INTRO = 'The shuffle is where performance and skew questions come from, at every level of experience.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Concepts · basics</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“What happens between the mapper and the reducer?”</h4>
      <p class="scn__situation">A standard follow-up to word count.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> partition, sort, spill, fetch, merge.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Each pair gets a partition (HashPartitioner), goes into the sort buffer, is sorted by partition and key and spilled to local disk; spills are merged into one file per map.</li>
          <li>Reducers fetch their partition from every map over HTTP (NodeManager ShuffleHandler), merge them and call reduce once per key, in sorted order.</li>
          <li>A combiner can shrink data on the map side before it travels.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Performance · counters</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Spilled Records is 5 times Map output records</h4>
      <p class="scn__situation">A long-running aggregation job; the team asks what to tune.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> reading counters, buffer and merge settings.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Ideal is 2×; 3× means several spills; 5× means extra merge passes (more spills than io.sort.factor) on map or reduce side.</li>
          <li>Reduce map output first: combiner, filter early, compact keys, compress map output (Snappy/LZ4).</li>
          <li>Then raise io.sort.mb (and the map heap/container) and io.sort.factor; check the task logs for “Merging N intermediate segments”.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Skew · partitioning</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>99 reducers finish in 3 minutes, one runs for 2 hours</h4>
      <p class="scn__situation">A join on customer_id; many records have customer_id = NULL.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> hot keys and how the partitioner routes them.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>All values of one key go to one reducer: the NULL key is one giant partition. Check the reducer's “Reduce input records” and shuffle bytes.</li>
          <li>Filter or handle NULLs separately; salt hot keys (key + random suffix) and aggregate in two steps; or a custom partitioner.</li>
          <li>More reducers do not help: the hot key still lands on one of them.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Failures · shuffle</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Reducers fail with “Too many fetch failures” after a node dies</h4>
      <p class="scn__situation">The job eventually succeeds but takes twice as long.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> where map output lives.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Map output is on the dead node's local disk, not HDFS, so reducers can't fetch it.</li>
          <li>After repeated fetch failures the MRAppMaster marks those maps failed and reruns them elsewhere; reducers then fetch the new output.</li>
          <li>The delay is the rerun of finished maps; healthy disks, NodeManager monitoring and blacklisting bad nodes reduce it.</li>
        </ul>
      </div></details>
    </article>
'''
