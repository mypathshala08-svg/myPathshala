import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()

META = dict(
    module='09-mapreduce-in-depth', lesson='06-map-side-join-and-the-distributed-cache', n='9.6',
    module_label='Module 9 · MapReduce in depth',
    title='Map-side join and the distributed cache',
    desc='Map-side (replicated, broadcast) join in Hadoop MapReduce, run on a real Hadoop 3.5.0 cluster: the menu shipped to every map task with the distributed cache (addCacheFile with #symlink, -files, -archives, -libjars), loaded into a HashMap in setup(), and 5 lakh orders joined in a map-only job. 459,636 joined rows, 0 bytes shuffled, 18.9 s vs 24.8 s and 24.4 MB shuffled for the reduce-side join. Localization, memory limits, composite join, Hive map join and Spark broadcast join. Python simulation, quiz and interview scenarios.',
    og_desc='Ship the small table to every mapper and skip the shuffle: a real map-side join with the distributed cache, 0 bytes shuffled.',
    minutes=26, level='Intermediate',
    lead='When one side of a join is small, the cheapest join moves nothing but that small side. This lesson ships a menu file to every map task with Hadoop\'s distributed cache, joins 5 lakh orders while they are read, and compares it with the reduce-side join of Lesson 9.5 on the same cluster and data.',
    chips=['0 bytes shuffled, measured', 'Distributed cache explained', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Simulate a broadcast join, split by split',
    intro='<p>Every “map task” below gets its own copy of the small table, builds a dictionary once (its <code>setup()</code>), and joins its own split. There is no shuffle step at all, and each task\'s output keeps its input order.</p>',
    code='''menu_lines = ["chai,drink,15,A", "samosa,snack,18,B", "dosa,meal,45,D", "idli,breakfast,30,C"]
splits = [["1,S1413,2026-09-14 15:30,dosa,45", "2,S0973,2026-09-26 20:11,samosa,18"],
          ["3,S0007,2026-09-01 13:37,coffee,20", "4,S0002,2026-09-03 08:10,chai,15"],
          ["5,S0042,2026-09-09 14:05,idli,30"]]
joined = without_menu = 0
for n, split in enumerate(splits):
    category = {}                                   # setup(): once per map task
    for line in menu_lines:
        f = line.split(",")
        category[f[0]] = f[1]
    out = []
    for order in split:                             # map(): once per record
        cat = category.get(order.split(",")[3])
        if cat is None:
            without_menu += 1
            continue
        joined += 1
        out.append(order + "," + cat)
    print(f"part-m-0000{n}: {out}")
print("ORDERS_JOINED =", joined, " ORDERS_WITHOUT_MENU =", without_menu)
''',
    anno=[
        ('    category = {}                                   # setup(): once per map task', 'In Java this is the HashMap filled in setup() from the ./menu symlink: once per task, never per record.'),
        ('        cat = category.get(order.split(",")[3])', 'The join itself: one dictionary lookup. No shuffle, no sort, no reducer.'),
        ('            without_menu += 1', 'Coffee is missing from this menu, so its order is counted and dropped (an inner join). Our lab counted 40,364 of them.'),
    ],
    tasks=[
        dict(label='1 · Join each split', hint='Press <b>Run</b>. Notice each part file keeps the order of its split.', code=None),
        dict(label='2 · Left outer join', hint='Change the code so orders without a menu row are still written, with the category <code>unknown</code>. How many rows come out now?',
             code='''category = {"chai": "drink", "dosa": "meal"}
orders = ["1,S1413,2026-09-14 15:30,dosa,45", "3,S0007,2026-09-01 13:37,coffee,20", "4,S0002,2026-09-03 08:10,chai,15"]
for o in orders:
    print(o + "," + category.get(o.split(",")[3], "unknown"))
'''),
        dict(label='3 · Will it fit?', hint='<b>Predict first:</b> a Java HashMap entry costs roughly 5× the raw line size. Which small tables fit in our 300 MB map heap, leaving half the heap for the task itself?',
             code='''heap_mb, overhead = 300, 5
for name, mb in [("menu.csv", 0.0002), ("IFSC codes", 25), ("students", 40), ("customers", 2048)]:
    need = mb * overhead
    print(f"{name:10} {mb:>9} MB on disk -> ~{need:8.1f} MB in heap ->", "fits" if need < heap_mb / 2 else "too big: use a reduce-side join")
'''),
        dict(label='4 · Shuffle saved', hint='How many bytes did the map-side join avoid moving, and what share of the input file is that?',
             code='''shuffle_reduce_side = 24_448_645
input_bytes = 19_417_051
print(f"{shuffle_reduce_side:,} bytes not shuffled = {shuffle_reduce_side / input_bytes:.0%} of the input size")
'''),
        dict(label='5 · Spot the error', hint='This setup() code reads the menu but builds the dictionary with the wrong column order. Fix the key so lookups by item work.',
             code='''menu_lines = ["chai,drink,15,A", "dosa,meal,45,D"]
category = {}
for line in menu_lines:
    f = line.split(",")
    category[f[1]] = f[0]
print(category["dosa"])
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: map-side vs reduce-side join',
    intro='<p>Use the Module 8 lab cluster (lab8) with <code>student_orders.csv</code> and <code>menu.csv</code> from Lesson 9.1 (<code>make_student_orders.py</code>). Copy both Java files of Lessons 9.5 and 9.6 into <code>/tmp/mr9</code> in the namenode container, compile them into <code>mr9.jar</code>, and run <code>join_lab.sh</code>. It removes “coffee” from the menu first so you can see unmatched orders being counted.</p>',
    items=[
        dict(title='The map-side join', file='JoinMapSide.java',
             cmd=rd('java/JoinMapSide.java') + '\n// Inside the namenode container, in /tmp/mr9:\n//   mkdir -p classes && javac -cp $(hadoop classpath) -d classes *.java && jar cf mr9.jar -C classes .\n//   hadoop jar mr9.jar JoinMapSide /user/hadoop/data/student_orders.csv /user/hadoop/data/menu.csv /out/JoinMapSide',
             output=rd('tx95.txt').strip(),
             note='Real output of join_lab.sh, which runs both joins. Times vary from run to run; the shuffle bytes and counters do not.'),
        dict(title='Both joins, compared', file='join_lab.sh',
             cmd=rd('join_lab.sh') + '\n# Inside the namenode container:  bash /tmp/mr9/join_lab.sh',
             output=rd('tx95.txt').strip().split('== JoinMapSide')[0].strip(),
             note='The reduce-side half of the same run. MENU_NOT_FIRST=4 shows why the reduce-side reducer must buffer orders: for 4 of 8 items the menu row did not arrive first.'),
    ],
)

TRACE = dict(
    heading='setup() once, map() many times',
    intro='<p>Watch the dictionary being built once, then used for every order. Coffee is not in the menu.</p>',
    code='''menu = ["chai,drink", "dosa,meal"]
category = {}
for line in menu:
    item, cat = line.split(",")
    category[item] = cat
orders = ["dosa,45", "coffee,20", "chai,15"]
for o in orders:
    item = o.split(",")[0]
    print(o, "->", category.get(item))
''',
    notes={5: 'setup() :: The whole small table goes into memory before the first order is read.',
           9: 'map() :: One lookup per order; coffee gives None and would be counted as ORDERS_WITHOUT_MENU.'},
)

WORKED_INTRO = 'Three map-side join decisions: memory sizing, choosing the join, and how much the cache really copies.'
EXAMPLES = [
    dict(level='b', tag='Sizing · memory', title='Can the student table be broadcast?',
         problem='<p>The college wants every order joined with its student\'s department. The student file has 20,000 lines of about 60 bytes. Map tasks have a 300 MB heap. Assuming a hash map entry costs about 5× the raw line, does it fit comfortably (under half the heap)?</p>',
         inp='20,000 × 60 B · 5× overhead · 300 MB heap',
         approach=['Raw size = lines × bytes per line.',
                   'Heap needed ≈ raw × 5.',
                   'Compare with half the heap.'],
         code='''raw_mb = 20_000 * 60 / 1024**2
need = raw_mb * 5
print(f"raw {raw_mb:.2f} MB -> about {need:.1f} MB of heap; fits: {need < 300 / 2}")
''', notes={2: 'Overhead :: Strings, map entries and object headers make Java data several times larger than the file.'},
         tryit='Try 2 crore customers of 100 bytes each. The answer changes completely.'),
    dict(level='i', tag='Design · choice', title='Which join for which pair of tables?',
         problem='<p>Pick a join method for each: (a) 2 TB of orders with an 8-line menu; (b) 2 TB of orders with 1.5 TB of payments, both written by jobs with 200 reducers using the same partitioner on order_id, sorted; (c) 2 TB of orders with 1.5 TB of complaints, no special layout.</p>',
         inp='3 pairs of tables',
         approach=['Small side fits in memory → replicated map-side join.',
                   'Both sorted and identically partitioned → composite map-side join.',
                   'Otherwise → reduce-side join.'],
         code='''def choose(small_mb, same_layout):
    if small_mb < 100:
        return "replicated map-side join (distributed cache)"
    if same_layout:
        return "composite map-side join (CompositeInputFormat)"
    return "reduce-side join"
for name, small, layout in [("a", 0.001, False), ("b", 1.5e6, True), ("c", 1.5e6, False)]:
    print(name, "->", choose(small, layout))
''', notes={2: 'Rule :: The memory check comes first; it is the cheapest join when it applies.'},
         tryit='Add a case: 2 TB of orders with a 900 MB product table. Which would you pick, and what would you change first?'),
    dict(level='a', tag='Internals · cache', title='How many copies does the distributed cache make?',
         problem='<p>A job with 400 map tasks runs on 50 workers (8 tasks per worker) and ships a 30 MB lookup file with <code>-files</code>. How much is downloaded from HDFS if the file is localized per node, compared with a naive design that reads it from HDFS in every task?</p>',
         inp='400 tasks · 50 nodes · 30 MB',
         approach=['Localization downloads once per node per job.',
                   'Naive: once per task.',
                   'Compare.'],
         code='''tasks, nodes, mb = 400, 50, 30
print(f"distributed cache: {nodes * mb:,} MB   naive per task: {tasks * mb:,} MB")
''', notes={2: 'Per node :: The NodeManager keeps one local copy and every container of the job links to it.'},
         tryit='Public cache files (world-readable in HDFS) can even be shared across jobs and users on the same node.'),
]

QUIZ = mix([
    dict(q='What makes a replicated map-side join possible?', options=['Both tables are sorted', 'One table is small enough to hold in each map task\'s memory', 'The tables have the same number of columns', 'There is exactly one reducer'], answer=1,
         why='Each map task loads the full small table into a hash map.'),
    dict(q='How much data did our map-side join shuffle?', options=['24,448,645 bytes', '0 bytes: it was a map-only job', '20,851,062 bytes', '459,636 bytes'], answer=1,
         why='No reducer means no shuffle; the reduce-side join shuffled 24.4 MB.'),
    dict(q='Where is the small table loaded?', options=['In map(), for every record', 'In setup(), once per map task', 'In the driver', 'In the reducer'], answer=1,
         why='Real log: “menu loaded in setup(): 7 items”.'),
    dict(q='What does "#menu" do in addCacheFile(new URI(".../menu_nocoffee.csv#menu"))?', options=['Comments out the file', 'Creates a symlink called menu in the task\'s working directory', 'Renames the file in HDFS', 'Makes the file private'], answer=1,
         why='The mapper opened it with new FileReader("menu").'),
    dict(q='How often does a NodeManager download a cache file for one job?', options=['Once per record', 'Once per node; containers on that node link to the local copy', 'Once per map task', 'Never, tasks read it from HDFS'], answer=1,
         why='This is called localization.'),
    dict(q='In what order are rows written by a map-only join?', options=['Sorted by key', 'In the same order as each task\'s input split', 'Random', 'Grouped by category'], answer=1,
         why='There is no sort phase without a reducer: order 1, then order 2 in part-m-00000.'),
    dict(q='Which generic option ships extra jars to the task classpath?', options=['-files', '-libjars', '-archives', '-D'], answer=1,
         why='-archives unpacks zip/tar files; -files ships plain files.'),
    dict(q='Two 2 TB tables, both sorted by key and partitioned identically into 200 files. Which map-side join fits?', options=['Replicated join', 'Composite join (CompositeInputFormat)', 'No join is possible', 'A combiner join'], answer=1,
         why='It merges matching partitions in the map, with no memory limit.'),
])

REVISION = [
    '<b>Replicated (broadcast) join</b>: ship the small table to every map task, load into a HashMap in <code>setup()</code>, look up in <code>map()</code>; map-only, no shuffle.',
    'Ship files with <code>job.addCacheFile(uri#name)</code>, or <code>-files</code>, <code>-archives</code> (unpacked), <code>-libjars</code> (classpath); needs GenericOptionsParser/ToolRunner.',
    'NodeManagers <b>localize</b> cache files once per node; each container gets a symlink (<code>./menu</code>).',
    'Lab: 459,636 joined rows, 0 bytes shuffled, 18.9 s vs reduce-side 24.8 s and 24,448,645 bytes shuffled; same rows.',
    'Output: one <code>part-m</code> per map task, in input order (no sort).',
    'Rule: small side must fit in the map heap (Java objects take several times the file size).',
    'Two big tables: reduce-side join, or <b>composite join</b> if both are sorted and identically partitioned.',
    'Modern equivalents: Hive map join, Spark broadcast hash join (10 MB default threshold).',
]
FAQ = [
    ('What is a map-side join in Hadoop?', 'A join performed in the map phase without a shuffle. In the replicated form, the smaller data set is distributed to every map task (usually with the distributed cache), loaded into memory in setup(), and each record of the larger data set is joined by a lookup. The job can be map-only, so it avoids sorting and transferring data to reducers.'),
    ('What is the distributed cache in Hadoop?', 'A mechanism to make read-only files, archives and jars available to all tasks of a job. Files are registered with Job.addCacheFile() or the -files, -archives and -libjars options; each NodeManager downloads them from HDFS once per node (localization) and links them into each container\'s working directory, optionally under a name given after # in the URI.'),
    ('When should I use a map-side join instead of a reduce-side join?', 'When one input is small enough to fit in each map task\'s memory (with room to spare), or when both inputs are already sorted by the join key and partitioned identically. Otherwise use a reduce-side join, which works for any sizes but shuffles both inputs.'),
    ('Why is a map-side join faster?', 'It avoids the shuffle: no map output sorting and spilling, no network transfer to reducers, no merge and no reduce tasks. In our lab the reduce-side join moved 24.4 MB across the network and took 24.8 s; the map-side join moved nothing and took 18.9 s for the same 459,636 rows.'),
    ('What happens if the small table is too big for a map-side join?', 'Each map task holds its own full copy in heap, so the tasks fail with OutOfMemoryError or are killed by YARN for exceeding container memory, and retries fail the same way. Increase map memory only if the table is moderately sized; otherwise switch to a reduce-side join or pre-partition both inputs for a composite join.'),
]

PRACTICE_INTRO = 'Map-side join exercises using the real numbers from the lab.'
PROBLEMS = [
    dict(level='easy', title='Check the counters', stmt='Show that ORDERS_JOINED + ORDERS_WITHOUT_MENU equals Map input records.', inp='459,636 + 40,364',
         code='''print(459636 + 40364 == 500000)
''', explain='True: every order was either joined or counted as having no menu row.'),
    dict(level='easy', title='Output sizes', stmt='Add the three part-m file sizes and compare with Bytes Written.', inp='9,020,852 + 8,993,924 + 2,836,286',
         code='''print(9020852 + 8993924 + 2836286, "vs", 20851062)
''', explain='20,851,062 both: the same bytes as the reduce-side join\'s single part-r file.'),
    dict(level='easy', title='Time saved', stmt='How much faster was the map-side join, in seconds and percent?', inp='24,828 ms vs 18,943 ms',
         code='''print(f"{(24828 - 18943) / 1000:.1f} s faster, {1 - 18943 / 24828:.0%} less time")
''', explain='About 5.9 s (24%) on a tiny lab; on terabytes the saved shuffle matters far more.'),
    dict(level='medium', title='Build the lookup', stmt='Read menu lines into a dictionary item → (category, price) and join two orders, printing the order with category and menu price.', inp='menu + 2 orders',
         code='''menu = ["chai,drink,15,A", "thali,meal,80,D"]
lookup = {}
for line in menu:
    item, cat, price, counter = line.split(",")
    lookup[item] = (cat, int(price))
for o in ["7,S0010,2026-09-02 13:05,thali,80", "8,S0011,2026-09-02 13:06,chai,15"]:
    cat, price = lookup[o.split(",")[3]]
    print(o, "->", cat, price)
''', explain='The same setup()/map() pattern, carrying two columns from the small table.'),
    dict(level='medium', title='Check the bill', stmt='Using the joined lookup, count orders whose amount differs from the menu price.', inp='3 orders',
         code='''price = {"chai": 15, "dosa": 45}
orders = ["1,S1,t,chai,15", "2,S2,t,dosa,40", "3,S3,t,dosa,45"]
bad = [o for o in orders if int(o.split(",")[4]) != price[o.split(",")[3]]]
print(len(bad), "mismatched:", bad)
''', explain='1 mismatch. A map-side join plus a counter is a cheap data-quality check over billions of rows.'),
    dict(level='medium', title='Cache downloads', stmt='3 workers ran our 3 map tasks. How many times was the menu downloaded from HDFS if each task landed on a different node, and if all 3 landed on one node?', inp='3 tasks',
         code='''for nodes_used in (3, 1):
    print(f"tasks on {nodes_used} node(s): {nodes_used} download(s)")
''', explain='Once per node per job, however many tasks run there.'),
    dict(level='business', title='Broadcast or shuffle?', stmt='A daily job joins 3 TB of transactions with a 5 MB merchant table. A reduce-side join shuffles the 3 TB; at 1 GB/s of total network bandwidth, how long does the shuffle alone take, and what does broadcasting cost instead to 400 nodes?', inp='3 TB · 1 GB/s · 5 MB × 400 nodes',
         code='''shuffle_s = 3 * 1024 / 1
broadcast_mb = 5 * 400
print(f"shuffle ~{shuffle_s / 60:.0f} min of network time; broadcast {broadcast_mb / 1024:.1f} GB in total")
''', explain='About 51 minutes of network time versus copying 2 GB once. That is why every engine broadcasts small tables.'),
    dict(level='advanced', title='Composite join by hand', stmt='Two inputs are sorted by order_id and split into the same 2 partitions. Merge-join partition by partition without loading either fully into memory.', inp='2 × 2 sorted partitions',
         code='''A = [[(1, "dosa"), (3, "chai")], [(4, "idli"), (6, "thali")]]
B = [[(1, "UPI"), (2, "cash"), (3, "UPI")], [(4, "card"), (6, "UPI")]]
for pa, pb in zip(A, B):
    i = j = 0
    while i < len(pa) and j < len(pb):
        if pa[i][0] == pb[j][0]:
            print(pa[i][0], pa[i][1], pb[j][1]); i += 1; j += 1
        elif pa[i][0] < pb[j][0]:
            i += 1
        else:
            j += 1
''', explain='Orders 1, 3, 4 and 6 are joined, walking both sorted lists once. This only works because both sides use the same partitioning and sort order.'),
]

SCN_INTRO = 'Join strategies are a favourite interview topic for data engineers, from MapReduce to Spark.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Concepts · joins</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“What is the difference between a map-side and a reduce-side join?”</h4>
      <p class="scn__situation">Asked in almost every Hadoop interview.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> where the join happens and the condition.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Reduce-side: both inputs are mapped to (join key, tagged record) and shuffled; the reducer combines them. Works for any sizes but moves all data.</li>
          <li>Map-side: the small table is broadcast with the distributed cache and looked up in each mapper; no shuffle, often map-only.</li>
          <li>Condition: the small side fits in mapper memory (or both inputs are sorted and identically partitioned for a composite join).</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Operations · memory</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>A map-side join job that ran for a year now fails with OutOfMemoryError</h4>
      <p class="scn__situation">Every map attempt fails four times; nothing in the code changed.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> that you suspect the growing small side.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Check the size of the cached file: the “small” table has probably grown. Each task holds a full copy in heap.</li>
          <li>Short term: raise mapreduce.map.memory.mb and -Xmx together, or load only the needed columns and rows.</li>
          <li>Long term: add a size check in the driver and fall back to a reduce-side join above a threshold, as Hive and Spark do automatically.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Internals · cache</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>“How does a file added with -files reach the mapper?”</h4>
      <p class="scn__situation">A follow-up after you mention the distributed cache.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> the localization path.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>The client uploads local files to the job's staging directory in HDFS and records them in job.xml.</li>
          <li>Before launching containers, each NodeManager downloads (localizes) the files once into its local cache.</li>
          <li>Each container gets a symlink in its working directory, so the task opens the file by its plain name.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Design · modern</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>“Spark is doing a sort-merge join with a 3 MB table. Why, and how do you fix it?”</h4>
      <p class="scn__situation">A slow Spark job joins a fact table with a small lookup table.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> broadcast joins beyond MapReduce.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Spark broadcasts only when it knows the table is below spark.sql.autoBroadcastJoinThreshold (10 MB default); missing statistics or a filtered subquery can hide the size.</li>
          <li>Use a broadcast hint (broadcast(df) or /*+ BROADCAST(t) */) or compute statistics.</li>
          <li>It is the same idea as the MapReduce replicated join: ship the small side, avoid shuffling the big side.</li>
        </ul>
      </div></details>
    </article>
'''
