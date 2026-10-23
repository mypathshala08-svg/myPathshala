import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE).replace('{{PLAYGROUND}}', playground(dict(
    title='Map where the data is',
    intro='<p>Two racks of workers. Upload a file, run the word count job, then run it again with data locality switched off and compare the network traffic and time.</p>',
    racks=2, nodes=3, features=['upload', 'job', 'locality'],
    preload=[dict(name='canteen_orders_5y.csv', sizeMB=1024)],
    **{'try': [
        dict(text='Upload a file (or use the preloaded one).', on='upload-done'),
        dict(text='Press <b>Run word count job</b> and watch one map task start per block.', on='job-done'),
        dict(text='Untick <b>Move code to data</b> and run again. What changed?', on='job-done-nolocal'),
    ]},
)))
rd = lambda f: open(os.path.join(UP, f)).read()

META = dict(
    module='08-mapreduce-fundamentals', lesson='01-thinking-in-mapreduce', n='8.1',
    module_label='Module 8 · MapReduce fundamentals',
    title='Thinking in MapReduce',
    desc='MapReduce explained from zero with a real job on a Hadoop 3.5.0 cluster with HDFS and YARN: map(k1, v1) → list(k2, v2), shuffle and sort, reduce(k2, list(v2)). Orders and revenue per item from 3 lakh and 2.7 crore canteen orders: 1 split vs 4 splits, data-local map tasks, a speculative attempt killed, counters explained, and an honest speed comparison with plain Python. Patterns (summarization, filtering, inverted index, join, top-N), Python simulation, quiz and interview scenarios.',
    og_desc='Write a real MapReduce job, run it on HDFS + YARN, and watch 4 map tasks, one speculative copy and the shuffle do the work.',
    minutes=28, level='Beginner',
    lead='MapReduce asks you for two small functions and does the rest: it runs your map on every block where it is stored, groups the results by key, and runs your reduce once per key. This lesson builds that way of thinking and runs a real job on a three-worker cluster with HDFS and YARN, reading every number Hadoop reports.',
    chips=['Real job on HDFS + YARN', 'Speculative attempt caught live', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Simulate map, shuffle and reduce',
    intro='<p>This is the same job as <code>ItemRevenue.java</code>, written as three plain Python steps so you can see the data between them. Hadoop does the shuffle for you; here we do it with a dictionary.</p>',
    code='''lines = ["order_id,item,amount", "1001,samosa,18", "1002,vada pav,20", "1003,poha,25",
         "1004,samosa,18", "1005,chai,15", "1006,poha,25", "1007,chai,15", "1008,chai,15"]

def map_fn(line):                       # one record in, zero or more (key, value) pairs out
    f = line.split(",")
    if f[0] == "order_id":
        return []
    return [(f[1], int(f[2]))]

def reduce_fn(item, amounts):           # one key with ALL its values in
    return (item, len(amounts), sum(amounts))

mapped = [pair for line in lines for pair in map_fn(line)]
print("map output :", mapped[:4], "...")

groups = {}                             # the shuffle: group by key, then sort keys
for k, v in mapped:
    groups.setdefault(k, []).append(v)
print("shuffled   :", dict(sorted(groups.items())))

for item in sorted(groups):
    print("reduce     :", reduce_fn(item, groups[item]))
''',
    anno=[
        ('    if f[0] == "order_id":', 'The header line produces no pair at all: that is why Map input records (300,001) was one more than Map output records (300,000).'),
        ('groups = {}                             # the shuffle: group by key, then sort keys', 'In Hadoop this is the shuffle and sort: partition, copy across the network, merge, sort by key.'),
        ('    return (item, len(amounts), sum(amounts))', 'The reducer sees every value of one key together, so counting and summing is trivial.'),
    ],
    tasks=[
        dict(label='1 · Map, shuffle, reduce', hint='Press <b>Run</b> and follow one item (chai) through all three steps.', code=None),
        dict(label='2 · Change the key', hint='<b>Predict first:</b> make the key the price instead of the item. How many groups will the reducer see?',
             code='''lines = ["1001,samosa,18", "1002,vada pav,20", "1003,poha,25", "1004,samosa,18", "1005,chai,15", "1006,poha,25"]
groups = {}
for line in lines:
    oid, item, amount = line.split(",")
    groups.setdefault(int(amount), []).append(oid)      # key = price now
for price in sorted(groups):
    print(price, "->", len(groups[price]), "orders", groups[price])
'''),
        dict(label='3 · Three mappers', hint='Split the input into 3 chunks, map each chunk separately (as 3 map tasks would), then shuffle all outputs together. Is the answer the same?',
             code='''lines = ["1001,samosa,18", "1002,vada pav,20", "1003,poha,25", "1004,samosa,18",
         "1005,chai,15", "1006,poha,25", "1007,chai,15", "1008,chai,15", "1009,dosa,45"]
chunks = [lines[0:3], lines[3:6], lines[6:9]]           # 3 "splits"
outputs = []
for n, chunk in enumerate(chunks):
    out = [(l.split(",")[1], int(l.split(",")[2])) for l in chunk]
    print(f"map task {n}: {out}")
    outputs += out
groups = {}
for k, v in outputs:
    groups.setdefault(k, []).append(v)
print({k: (len(v), sum(v)) for k, v in sorted(groups.items())})
'''),
        dict(label='4 · Average per item', hint='Change the reducer to print the average amount per order for each item. Why must the average be computed in the reducer and not by averaging per-mapper averages?',
             code='''groups = {"chai": [15, 15, 15], "samosa": [18, 18], "dosa": [45]}
for item, amounts in sorted(groups.items()):
    print(item, round(sum(amounts) / len(amounts), 2))
'''),
        dict(label='5 · Spot the error', hint='This mapper crashes on the very first line of the real file. Fix it so the header is skipped.',
             code='''lines = ["order_id,item,amount", "1001,samosa,18"]
for line in lines:
    oid, item, amount = line.split(",")
    print((item, int(amount)))
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: the Module 8 lab and your first job',
    intro='<p>Module 8 needs YARN, so it has its own lab cluster: a NameNode, a ResourceManager, a JobHistory Server and three workers that each run a DataNode and a NodeManager. Stop the Module 5 lab first (<code>docker compose -p lab5 stop</code>); together they need more memory than a laptop has. Put <code>docker-compose.yaml</code> and <code>config</code> in a folder called <code>mr-lab</code> and start it. Containers are small (384 MB per task) so everything fits in about 5 GB of RAM.</p>',
    items=[
        dict(title='Start the lab', file='docker-compose.yaml',
             cmd=rd('lab/docker-compose.yaml') + '\n# ---- config (same folder) ----\n' + '\n'.join('# ' + l for l in rd('lab/config').strip().split('\n')) + '\n\n# Run, in the mr-lab folder:\n#   docker compose -p lab8 up -d\n#   docker exec lab8-resourcemanager-1 yarn node -list',
             output=rd('tx81_setup.txt').strip(),
             note='Real output. Three NodeManagers and three DataNodes, one of each per worker. The ResourceManager web UI is on port 8088 inside the network, the JobHistory Server on 19888.'),
        dict(title='Item revenue as a MapReduce job', file='ItemRevenue.java',
             cmd=rd('java/ItemRevenue.java') + '\n// In the mr-lab folder (make_canteen.py is from Lesson 4.3):\n//   docker exec lab8-namenode-1 mkdir -p /tmp/mr\n//   docker cp ItemRevenue.java lab8-namenode-1:/tmp/mr/\n//   docker cp canteen_orders.csv lab8-namenode-1:/tmp/mr/\n//   docker exec -it lab8-namenode-1 bash\n// Inside the container:\n//   cd /tmp/mr\n//   hdfs dfs -mkdir -p /user/hadoop/data\n//   hdfs dfs -put canteen_orders.csv /user/hadoop/data/\n//   mkdir -p classes && javac -cp $(hadoop classpath) -d classes *.java && jar cf mr.jar -C classes .\n//   hadoop jar mr.jar ItemRevenue /user/hadoop/data/canteen_orders.csv /out/item_revenue\n//   hdfs dfs -cat /out/item_revenue/part-r-00000',
             output=rd('tx81.txt').strip(),
             note='Real output, unedited. 54 counters in total; the ones that matter most today are Launched map tasks, Data-local map tasks, Map input/output records and Reduce input groups.'),
        dict(title='90 times the data, and where each task ran', file='attempts.sh',
             cmd=rd('attempts.sh') + '\n# Inside the namenode container, in /tmp/mr:\n#   for i in $(seq 30); do tail -n +2 canteen_orders.csv; done > orders_x30.csv\n#   cat orders_x30.csv orders_x30.csv orders_x30.csv > orders_x90.csv\n#   hdfs dfs -put orders_x90.csv /user/hadoop/data/\n#   hadoop jar mr.jar ItemRevenue /user/hadoop/data/orders_x90.csv /out/item_revenue_x90\n#   bash attempts.sh job_<your job id>',
             output=rd('tx81_x90.txt').strip(),
             note='Real output (the job log is shortened to the progress and key counters). Your speculative attempt may or may not appear: it depends on whether one map runs clearly slower than the others. The built-in “mapred job -history all” printer crashed on our 7-character host names (worker1), so attempts.sh asks the JobHistory Server REST API instead.'),
    ],
)

TRACE = dict(
    heading='One record\'s trip through map, shuffle and reduce',
    intro='<p>Follow how four lines become two output rows. Watch the <code>groups</code> dictionary: it is the shuffle.</p>',
    code='''lines = ["1001,chai,15", "1002,dosa,45", "1003,chai,15", "1004,dosa,45"]
pairs = []
for line in lines:
    oid, item, amount = line.split(",")
    pairs.append((item, int(amount)))
groups = {}
for item, amount in pairs:
    groups.setdefault(item, []).append(amount)
for item in sorted(groups):
    print(item, len(groups[item]), sum(groups[item]))
''',
    notes={5: 'Map :: Each line becomes one (item, amount) pair, independently of every other line.',
           8: 'Shuffle :: All amounts of the same item end up in one list.',
           10: 'Reduce :: One output line per key.'},
)

WORKED_INTRO = 'Three MapReduce design and sizing problems: choosing the key, estimating a job, and a reducer that must be careful.'
EXAMPLES = [
    dict(level='b', tag='Design · key', title='Design a job: UPI transactions per bank',
         problem='<p>Input lines look like <code>txn_id,payer_bank,payee_bank,amount</code>. The bank wants the number of transactions and the total amount <b>sent</b> by each payer bank. What should map emit, and what does reduce do?</p>',
         inp='4 sample lines',
         approach=['The answer is per payer bank, so the key is payer_bank.',
                   'The value is the amount; the reducer counts and sums.',
                   'Simulate it on four lines.'],
         code='''lines = ["t1,SBI,HDFC,500", "t2,HDFC,SBI,1200", "t3,SBI,ICICI,250", "t4,SBI,HDFC,50"]
groups = {}
for l in lines:
    txn, payer, payee, amount = l.split(",")
    groups.setdefault(payer, []).append(int(amount))     # map: (payer, amount)
for bank in sorted(groups):
    print(bank, len(groups[bank]), sum(groups[bank]))     # reduce: count, sum
''', notes={5: 'Key :: Whatever must be combined must share a key.'},
         tryit='Change the job to count money RECEIVED per bank. Only the key in map changes.'),
    dict(level='i', tag='Sizing · tasks', title='How many map tasks, and how long?',
         problem='<p>A 1 TB file in HDFS with 128 MB blocks. The cluster has 20 workers with 8 map containers each. A map task takes 40 s. How many map tasks run, in how many waves, and roughly how long is the map phase?</p>',
         inp='1 TB · 128 MB splits · 160 containers · 40 s/task',
         approach=['Map tasks = number of splits ≈ file size / block size.',
                   'Waves = tasks / containers, rounded up.',
                   'Map phase ≈ waves × task time.'],
         code='''import math
tasks = math.ceil(1024 * 1024 / 128)
waves = math.ceil(tasks / (20 * 8))
print(f"{tasks} map tasks, {waves} waves, about {waves * 40 / 60:.0f} minutes")
''', notes={2: 'Splits :: One map task per split; a split is normally one block.'},
         tryit='Double the cluster to 40 workers. The map phase halves: this is what “scale out” means.'),
    dict(level='a', tag='Correctness · averages', title='Why you can\'t average the averages',
         problem='<p>Two map tasks each compute the average dosa price they saw and send only that average to the reducer, which averages the two. Map 1 saw 3 orders at ₹45; map 2 saw 1 order at ₹30 (a discount). Is the reducer\'s answer right? How should the map output look instead?</p>',
         inp='map 1: 45, 45, 45 · map 2: 30',
         approach=['Compute the true average over all four orders.',
                   'Compute the average of the two map averages.',
                   'Fix: emit (sum, count) and divide only in the reducer.'],
         code='''m1, m2 = [45, 45, 45], [30]
true_avg = sum(m1 + m2) / len(m1 + m2)
wrong = (sum(m1) / len(m1) + sum(m2) / len(m2)) / 2
partials = [(sum(m1), len(m1)), (sum(m2), len(m2))]          # emit (sum, count)
right = sum(s for s, c in partials) / sum(c for s, c in partials)
print(f"true {true_avg:.2f} · average of averages {wrong:.2f} · from (sum, count) {right:.2f}")
''', notes={4: 'Partials :: Sums and counts can be added safely; averages cannot.'},
         tryit='This matters again in Lesson 9.1: a combiner may run zero, one or many times, so its output must be safe to combine again.'),
]

QUIZ = mix([
    dict(q='What does the map function receive and produce?', options=['A file in, a file out', 'One key-value pair in, zero or more key-value pairs out', 'All values of a key in, one value out', 'A block in, a block out'], answer=1,
         why='map(k1, v1) → list(k2, v2); for text input k1 is the byte offset and v1 the line.'),
    dict(q='What does the reducer receive?', options=['One record at a time', 'One key with all of its values', 'The whole file', 'The output of exactly one map task'], answer=1,
         why='reduce(k2, list(v2)); values from all map tasks are gathered by the shuffle.'),
    dict(q='Who groups the map output by key?', options=['Your Mapper code', 'The framework, in the shuffle and sort', 'The NameNode', 'The client before submitting'], answer=1,
         why='You never write the shuffle; Hadoop partitions, copies, merges and sorts.'),
    dict(q='How many map tasks did the 4.7 MB file get, and why?', options=['4, one per worker', '1, because it is one split (one small block)', '6, one per item', '0, it was too small'], answer=1,
         why='“number of splits:1”: one map task per input split.'),
    dict(q='Why were 5 map tasks launched for 4 splits?', options=['One map failed', 'Speculative execution started a backup of a slow map', 'The reducer was counted as a map', 'One split was read twice by mistake'], answer=1,
         why='“Killed map tasks=1”, diagnostics: “Speculation: … succeeded first!”.'),
    dict(q='Where is intermediate map output stored?', options=['In HDFS with replication 3', 'On the local disk of the worker that ran the map', 'In the NameNode', 'In the ResourceManager'], answer=1,
         why='It is temporary; if it is lost, the map is simply rerun.'),
    dict(q='What does “Data-local map tasks=5” mean?', options=['5 maps read data from the client', 'All map attempts ran on a node that stores their block', 'The data was cached', 'There were 5 DataNodes'], answer=1,
         why='Moving code to data, as in Lesson 1.5.'),
    dict(q='Which job is a poor fit for classic MapReduce?', options=['Counting page views per day from logs', 'An algorithm that repeats 50 passes over the same data', 'Building an inverted index', 'Summing sales per store'], answer=1,
         why='Every pass writes to disk and starts new tasks; Spark keeps data in memory between passes.'),
])

REVISION = [
    '<b>map(k1, v1) → list(k2, v2)</b>; <b>shuffle and sort</b> by key; <b>reduce(k2, list(v2)) → list(k3, v3)</b>.',
    'You write Mapper, Reducer and a driver; Hadoop splits input, schedules tasks near data, shuffles, retries and writes output.',
    'One map task per input split; reducers = <code>mapreduce.job.reduces</code> (default 1); output files <code>part-r-NNNNN</code> + <code>_SUCCESS</code>.',
    'Lab: 4.7 MB → 1 map, 25 s (Python: 0.1 s); 422 MB → 4 maps on 3 workers, all data-local, 68 s; one speculative attempt killed.',
    'Map output goes to local disk, not HDFS; the output folder must not exist before the job.',
    'Design question: <b>what is the key?</b> Only values with the same key ever meet.',
    'Good fit: big batch scans and aggregations. Poor fit: iterative and interactive work (use Spark, Tez).',
]
FAQ = [
    ('What is MapReduce in Hadoop?', 'MapReduce is Hadoop\'s programming model and framework for batch processing. You write a map function that turns each input record into key-value pairs and a reduce function that combines all values of each key. The framework splits the input, runs map tasks in parallel on the nodes that store the data, shuffles and sorts the intermediate pairs by key, runs reduce tasks and writes the result to HDFS, retrying failed tasks automatically.'),
    ('What are the phases of a MapReduce job?', 'Input splitting and reading (InputFormat and RecordReader), the map phase, the shuffle and sort (partitioning, spilling, copying, merging), the reduce phase and output writing (OutputFormat). An optional combiner can run on map output before the shuffle.'),
    ('Is MapReduce still used?', 'Classic Java MapReduce is rarely chosen for new projects; Spark, Hive on Tez, Flink and cloud warehouses are more common. It still runs in many established Hadoop clusters (including tools like DistCp and Hadoop Archive, which are MapReduce jobs), and its model of map, shuffle by key and reduce underlies all of those newer engines, so it remains a core interview and design topic.'),
    ('Why is MapReduce slow for small data?', 'Every job starts an ApplicationMaster and task JVMs in YARN containers, sorts and writes map output to local disk and copies it over the network. That fixed overhead is tens of seconds; in our lab a 4.7 MB file took 25 s against 0.1 s in plain Python. The model pays off when the data is too big for one machine to read in time.'),
    ('What is speculative execution in MapReduce?', 'When a task runs noticeably slower than others of the same job, the MRAppMaster can start a duplicate attempt on another node. Whichever attempt finishes first is used and the other is killed. It protects jobs from slow nodes; it is controlled by mapreduce.map.speculative and mapreduce.reduce.speculative (both true by default).'),
]

PRACTICE_INTRO = 'MapReduce thinking exercises, using the real numbers from our lab.'
PROBLEMS = [
    dict(level='easy', title='Records lost or not?', stmt='Map input records=300001 and Map output records=300000. Explain the difference with one line of code.', inp='two counters',
         code='''print(300001 - 300000, "line produced no pair: the header 'order_id,item,amount'")
''', explain='The mapper returns early for the header, so it emits nothing for that record.'),
    dict(level='easy', title='Check the reducer', stmt='Using the output, compute the price of one dosa and one chai.', inp='dosa 49948 2247660 · chai 50170 752550',
         code='''print("dosa", 2247660 / 49948, "chai", 752550 / 50170)
''', explain='45.0 and 15.0: the menu prices, so the sums are consistent.'),
    dict(level='easy', title='Scale check', stmt='orders_x90 has 90 copies of 3 lakh orders. Check that chai\'s count in the big job equals 90 × the small job.', inp='50,170 and 4,515,300',
         code='''print(50170 * 90 == 4515300)
''', explain='True. The same code gives exactly the same answer at 90 times the size.'),
    dict(level='medium', title='Word count by hand', stmt='Write map and reduce for word count over three lines, with a dictionary as the shuffle.', inp='3 lines of feedback',
         code='''lines = ["the chai was hot", "the dosa was cold", "chai was late"]
groups = {}
for line in lines:
    for word in line.split():
        groups.setdefault(word, []).append(1)
for w in sorted(groups):
    print(w, sum(groups[w]))
''', explain='Every word becomes (word, 1); the reducer sums the ones. Lesson 8.6 runs this on 2 lakh lines.'),
    dict(level='medium', title='Inverted index', stmt='For each word, list the line numbers it appears in.', inp='3 lines',
         code='''lines = ["chai hot", "dosa cold", "chai cold"]
index = {}
for n, line in enumerate(lines, 1):
    for w in set(line.split()):
        index.setdefault(w, []).append(n)
for w in sorted(index):
    print(w, index[w])
''', explain='Map emits (word, line number); reduce collects the list. This is how search indexes are built.'),
    dict(level='medium', title='Waves of tasks', stmt='Our lab has 3 workers with 2048 MB each; a map container is 384 MB and the MRAppMaster takes 512 MB on one worker. How many maps can run at once?', inp='3 × 2048 MB · 384 MB · AM 512 MB',
         code='''per_node = 2048 // 384
print(per_node * 3 - (512 + 383) // 384, "maps at once (about)")
''', explain='About 13: 5 per worker, minus room for the AM. Our 4 maps all ran in one wave.'),
    dict(level='business', title='Rent a cluster or wait?', stmt='A monthly report scans 50 TB. One server reads at 300 MB/s. A 100-node cluster reads in parallel at the same speed per node, costing ₹40 per node-hour. Compare times and cluster cost.', inp='50 TB · 300 MB/s · 100 nodes · ₹40/node-hour',
         code='''one = 50 * 1024 * 1024 / 300 / 3600
many = one / 100
print(f"one server {one:.0f} h, cluster {many:.1f} h, cluster cost Rs {100 * max(1, many) * 40:,.0f}")
''', explain='About 49 hours vs half an hour for ₹4,000 (illustrative), and the report is ready the same morning.'),
    dict(level='advanced', title='Top-N per mapper', stmt='Each map task keeps only its local top 2 items by revenue; the reducer merges them into the global top 2. Compare with the true top 2 for these two maps.', inp='2 maps, partial revenue per item',
         code='''m1 = {"dosa": 900, "idli": 600, "chai": 300}
m2 = {"dosa": 850, "poha": 700, "idli": 100}
total = {}
for m in (m1, m2):
    for k, v in m.items():
        total[k] = total.get(k, 0) + v
print("true top 2:", sorted(total.items(), key=lambda x: -x[1])[:2])
local = [sorted(m.items(), key=lambda x: -x[1])[:2] for m in (m1, m2)]
merged = {}
for top in local:
    for k, v in top:
        merged[k] = merged.get(k, 0) + v
print("from local top 2s:", sorted(merged.items(), key=lambda x: -x[1])[:2])
''', explain='Wrong answer: map 2 dropped idli\'s 100, so idli shows 600 instead of 700 and poha takes second place. Local top-N is only safe when each key\'s full total is known in one place, e.g. after a first job that sums per item; then a second step picks the top N.'),
]

SCN_INTRO = 'MapReduce basics appear in every Hadoop interview, usually as “explain with an example” and “design a job for X”.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Concepts · basics</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“Explain MapReduce with word count”</h4>
      <p class="scn__situation">The most common opening question.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> the three phases and who does what.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Map: for each line, emit (word, 1). Runs in parallel, one task per split, near the data.</li>
          <li>Shuffle and sort (framework): all pairs with the same word go to the same reducer, sorted by key.</li>
          <li>Reduce: sum the ones for each word and write (word, count) to HDFS, one part file per reducer.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Design · keys</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>Design a job: average order value per city per month</h4>
      <p class="scn__situation">Input: order_id, city, date, amount.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> composite keys and correct averaging.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Key = (city, yyyy-mm); value = amount (or (amount, 1) if a combiner will be used).</li>
          <li>Reducer: sum and count, then divide once. Never average averages.</li>
          <li>One output line per city-month; the number of reducers decides the number of output files.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Operations · performance</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>“Our MapReduce job on 2 GB takes 3 minutes. Python on a laptop takes 20 seconds.”</h4>
      <p class="scn__situation">A manager asks why Hadoop is “slow”.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> fixed overhead vs scale.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Each job pays fixed costs: AM and container start-up, JVM launch, sort and spill to disk, shuffle over the network.</li>
          <li>For 2 GB that overhead dominates; for 20 TB the parallel read across hundreds of nodes dominates and wins by far.</li>
          <li>Options: don't use a cluster for small data, use uber mode for tiny jobs, or move to Spark/Hive on Tez for interactive work.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Internals · failures</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>“The job counters show Killed map tasks=1 but the job succeeded. Is something wrong?”</h4>
      <p class="scn__situation">A junior engineer is worried after reading the counters.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> speculation vs failure.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Killed is not failed: with speculative execution the slower of two attempts is killed once the other succeeds.</li>
          <li>Check the attempt diagnostics (“Speculation: … succeeded first!”) in the JobHistory UI or REST API.</li>
          <li>Failed task attempts (non-zero exit codes) would show up as “Failed map tasks” and are retried up to 4 times by default.</li>
        </ul>
      </div></details>
    </article>
'''
