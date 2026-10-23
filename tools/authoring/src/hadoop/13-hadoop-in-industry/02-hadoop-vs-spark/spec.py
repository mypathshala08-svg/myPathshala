import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()

META = dict(
    module='13-hadoop-in-industry', lesson='02-hadoop-vs-spark', n='13.2',
    module_label='Module 13 · Hadoop in industry today',
    title='Hadoop vs Spark',
    desc='Hadoop MapReduce vs Apache Spark, measured on the same Hadoop 3.5.0 cluster: Spark 4.0.4 on YARN reading HDFS gives the same item revenue as the MapReduce job of Lesson 8.1 (RDD 7.4 s, DataFrame 11.3 s), and its physical plan shows the map, combiner (partial aggregate) and shuffle (Exchange). Five passes over 9 million orders: MapReduce 199 s, Spark without cache 75.3 s, Spark with cache 35.3 s. DAG, lazy evaluation, RDD/DataFrame, Catalyst, executors vs containers, lineage, when MapReduce still fits, Spark versions on EMR, Dataproc and Cloudera. Python model, quiz and interview scenarios.',
    og_desc='Same cluster, same data: five MapReduce jobs took 199 s, cached Spark took 35 s. See why, and why Spark still runs on Hadoop.',
    minutes=30, level='Intermediate',
    lead='Spark did not replace Hadoop; it replaced MapReduce. In this lesson Spark runs on our own YARN cluster and reads our HDFS files, gives exactly the same answers as our MapReduce job, and shows inside its plan the map, combiner and shuffle you already know. Then we measure where it wins: five passes over the same data take 199 s as MapReduce jobs and 35 s with Spark caching.',
    chips=['Spark 4.0.4 on our YARN', 'MapReduce vs Spark, timed', 'Runs in your browser (Python)'],
)

MODEL = '''# Per-pass times measured on our lab (5 passes over 9 M orders, 140 MB)
MR_PASS = 199 / 5                     # every pass is a new MapReduce job: start + read + write
NOCACHE_FIRST, NOCACHE_NEXT = 19.8, (15.6 + 13.5 + 13.6 + 12.8) / 4
CACHE_FIRST, CACHE_NEXT = 21.4, (4.2 + 3.7 + 3.3 + 2.7) / 4

def mapreduce(k):
    return k * MR_PASS

def spark(k, cache):
    if cache:
        return CACHE_FIRST + (k - 1) * CACHE_NEXT
    return NOCACHE_FIRST + (k - 1) * NOCACHE_NEXT

'''

RUN = dict(
    heading='A model of k passes, fitted to our runs',
    intro='<p>The per-pass times below are our measurements. The model predicts any number of passes; check that k = 5 gives back the lab totals (199 s, 75.3 s, 35.3 s). It leaves out Spark\'s one-time application start-up (about 46 s in our lab), which MapReduce pays inside every pass.</p>',
    code=MODEL + '''for k in [1, 5, 10, 20]:
    mr, nc, c = mapreduce(k), spark(k, False), spark(k, True)
    print(f"{k:>2} passes: MapReduce {mr:6.1f} s | Spark {nc:6.1f} s | Spark+cache {c:5.1f} s | {mr / c:4.1f}x")
''',
    anno=[
        ('MR_PASS = 199 / 5                     # every pass is a new MapReduce job: start + read + write', 'Five ItemRevenue jobs took 39, 39, 39, 41 and 41 s: about 40 s each, every time.'),
        ('CACHE_FIRST, CACHE_NEXT = 21.4, (4.2 + 3.7 + 3.3 + 2.7) / 4', 'Pass 1 pays for reading and filling the cache; the next passes cost about 3.5 s.'),
        ('        return CACHE_FIRST + (k - 1) * CACHE_NEXT', 'The cached line grows slowly, so the advantage grows with every extra pass.'),
    ],
    tasks=[
        dict(label='1 · k passes', hint='Press <b>Run</b>. At how many passes is cached Spark 10× faster than MapReduce?', code=None),
        dict(label='2 · One pass only', hint='<b>Predict first:</b> for a single pass, which is faster: Spark with cache or without? Why?',
             code=MODEL + '''print("1 pass, no cache:", spark(1, False), "s")
print("1 pass, cache   :", spark(1, True), "s   (filling the cache costs time and is never reused)")
'''),
        dict(label='3 · Lazy evaluation', hint='Transformations only record a plan; the action runs it. Count how often the source is read with and without cache.',
             code='''reads = 0
def source():
    global reads
    reads += 1
    return [15, 18, 20, 25, 30, 45]

plan = [lambda xs: [x for x in xs if x >= 18], lambda xs: [x * 2 for x in xs]]   # recorded, not run
def action(cached=None):
    data = cached if cached is not None else source()
    for step in plan:
        data = step(data)
    return len(data)

for _ in range(3):
    action()
print("no cache, 3 actions -> source read", reads, "times")
reads = 0
cache = source()
for _ in range(3):
    action(cache)
print("cache,    3 actions -> source read", reads, "time")
'''),
        dict(label='4 · 200 shuffle partitions', hint='Our plan said hashpartitioning(item, 200). With only 6 items, how many of the 200 reduce partitions can get any data? (Spark hashes with Murmur3; this sketch uses Java\'s String hash. Spark\'s adaptive execution then merges the empty partitions.)',
             code='''def text_hash(s):                     # Java String.hashCode
    h = 0
    for ch in s:
        h = (31 * h + ord(ch)) & 0xFFFFFFFF
    return h - (1 << 32) if h >= 1 << 31 else h
items = ["chai", "dosa", "idli", "poha", "samosa", "vada pav"]
used = {abs(text_hash(i)) % 200 for i in items}
print(len(used), "of 200 partitions have data")
'''),
        dict(label='5 · Spot the error', hint='This "reduceByKey" crashes when a partition has no rows. Give reduce() a starting value so an empty partition is fine.',
             code='''from functools import reduce
partitions = [[("chai", 15), ("chai", 15)], []]
for p in partitions:
    print(reduce(lambda a, b: (a[0], a[1] + b[1]), p))
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

SETUP = ('# One-time setup on the namenode container of the Module 8 lab (no Spark daemons needed):\n'
         '#   curl -O https://dlcdn.apache.org/spark/spark-4.0.4/spark-4.0.4-bin-hadoop3.tgz\n'
         '#   mkdir -p /tmp/opt && tar xzf spark-4.0.4-bin-hadoop3.tgz -C /tmp/opt\n'
         '#   export SPARK_HOME=/tmp/opt/spark-4.0.4-bin-hadoop3 HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop\n')

PCRUN = dict(
    heading='Run it on your PC: Spark on the Module 8 cluster',
    intro='<p>Spark needs no daemons of its own here: unpack it on the namenode container, point <code>HADOOP_CONF_DIR</code> at the Hadoop configuration, and <code>spark-submit --master yarn</code> asks our ResourceManager for an ApplicationMaster and executors, just like <code>hadoop jar</code>. Executors of 512–768 MB fit our 2 GB NodeManagers. The outputs below are real; Spark\'s INFO/WARN log lines and the YARN status report are filtered out.</p>',
    items=[
        dict(title='Item revenue: RDD and DataFrame', file='item_revenue_spark.py',
             cmd=rd('lab/item_revenue_spark.py') + '\n' + SETUP +
                 '#   $SPARK_HOME/bin/spark-submit --master yarn --num-executors 3 --executor-memory 512m \\\n'
                 '#       --executor-cores 1 --driver-memory 512m item_revenue_spark.py /user/hadoop/data/canteen_orders.csv',
             output=rd('tx132a.txt').strip(),
             note='Same numbers as ItemRevenue.java (Lesson 8.1). The DataFrame is slower here because inferSchema reads the file once more to guess the column types.'),
        dict(title='Five passes, without and with cache', file='iterative_spark.py',
             cmd=rd('lab/iterative_spark.py') + '\n' + SETUP +
                 '#   for c in nocache cache; do\n'
                 '#     $SPARK_HOME/bin/spark-submit --master yarn --num-executors 3 --executor-memory 768m \\\n'
                 '#       --executor-cores 1 --driver-memory 512m iterative_spark.py /user/hadoop/data/orders_x30.csv $c\n'
                 '#   done',
             output=rd('tx132b.txt').strip(),
             note='orders_x30.csv is the 140 MB, 9 million order file from Lesson 8.1. Timings vary from run to run; the pattern does not.'),
        dict(title='The same five passes as MapReduce jobs', file='iterative_mr.sh',
             cmd=rd('lab/iterative_mr.sh') + '\n# Run inside the namenode container:  bash iterative_mr.sh',
             output=rd('tx132c.txt').strip(),
             note='Each pass runs ItemRevenue over the whole file as a new job: new ApplicationMaster, new map and reduce JVMs, a full HDFS read and an HDFS write.'),
    ],
)

TRACE = dict(
    heading='Lazy transformations, one action',
    intro='<p>Spark records transformations and runs them only when an action asks for a result. Watch the plan grow without any data moving, then the action run it all at once.</p>',
    code='''orders = [("chai", 15), ("dosa", 45), ("chai", 15)]
plan = []
plan.append(("filter", lambda p: p[1] >= 15))
plan.append(("map", lambda p: (p[0], 1)))
result = {}
for p in orders:
    if plan[0][1](p):
        k, v = plan[1][1](p)
        result[k] = result.get(k, 0) + v
print(result)
''',
    notes={3: 'Transformation :: Only a plan entry is added; no row is touched yet.',
           6: 'Action :: Now every row flows through the whole plan in one pass.',
           9: 'Reduce :: Counting per key, like reduceByKey.'},
)

WORKED_INTRO = 'Four decisions engineers face when choosing between MapReduce and Spark, worked with our measured numbers.'
EXAMPLES = [
    dict(level='b', tag='Fintech · iterations', title='Ten passes for a fraud model',
         problem='<p>A UPI fraud team needs 10 passes over the same data. Using our lab\'s per-pass times, how long would MapReduce and cached Spark take, and how does Spark\'s one-time 46 s start-up change the answer?</p>',
         inp='MR 39.8 s/pass · cache 21.4 s + 3.475 s/pass · start-up 46 s',
         approach=['MapReduce: passes × 39.8 s.',
                   'Spark: first pass + 9 cheap passes.',
                   'Add Spark\'s start-up once and compare again.'],
         code='''mr = 10 * 199 / 5
spark = 21.4 + 9 * (4.2 + 3.7 + 3.3 + 2.7) / 4
print(f"MapReduce {mr:.0f} s, Spark+cache {spark:.1f} s, with start-up {spark + 46:.1f} s ({mr / (spark + 46):.1f}x)")
''', notes={2: 'Cache :: Only pass 1 reads HDFS.'},
         tryit='Even counting the start-up, Spark is about 4× faster at 10 passes, and the gap keeps growing.'),
    dict(level='i', tag='Telecom · memory', title='Will the data fit in the cache?',
         problem='<p>A telecom company wants to cache 2 TB of call records (CSV) for a 10-pass analysis. It has 100 executors of 16 GB. Spark\'s unified memory is (heap − 300 MB) × 0.6, shared by cache and execution. Stored as a columnar cache, the data is roughly the size of Parquet (our Lesson 10.2 ratio: 4.4 MB Parquet for 19.4 MB CSV). Does it fit?</p>',
         inp='2 TB CSV · 100 × 16 GB executors · ratio 4.4/19.4',
         approach=['Usable memory per executor = (16,384 − 300) × 0.6 MB.',
                   'Total = per executor × 100.',
                   'Cached size ≈ 2 TB × Parquet ratio.'],
         code='''per_exec_gb = (16384 - 300) * 0.6 / 1024
total_gb = per_exec_gb * 100
cached_gb = 2048 * 4.4 / 19.4
print(f"memory {total_gb:.0f} GB, data cached ~{cached_gb:.0f} GB, fits: {cached_gb < total_gb}")
''', notes={1: 'Unified memory :: Execution (shuffles, joins) shares this space; leave room.'},
         tryit='It fits with room to spare; as raw Java objects (RDD cache) it could be 2–3× the CSV size and would not. With MEMORY_AND_DISK the overflow spills to local disk instead of failing.'),
    dict(level='i', tag='E-commerce · choice', title='Which engine for which job?',
         problem='<p>An e-commerce platform has three workloads: (a) a nightly one-pass copy of 50 TB of logs into an archive on a memory-poor old cluster, (b) a sales dashboard refreshed every minute from Kafka, (c) a recommendation model with 30 passes. Pick an engine for each.</p>',
         inp='3 workloads',
         approach=['One pass, no reuse, little memory: MapReduce (or DistCp) is fine.',
                   'Streaming: Spark Structured Streaming.',
                   'Many passes: Spark with cache.'],
         code='''jobs = {"a: one-pass 50 TB copy": (1, False), "b: dashboard every minute": (0, True), "c: 30-pass model": (30, False)}
for name, (passes, streaming) in jobs.items():
    engine = "Spark Structured Streaming" if streaming else ("Spark + cache" if passes > 1 else "MapReduce/DistCp is fine")
    print(f"{name:28} -> {engine}")
''', notes={3: 'Rule of thumb :: Reuse and latency favour Spark; a single scan does not need it.'},
         tryit='Most teams still write (a) in Spark today for one engine and one skill set; the point is that MapReduce is not wrong for it.'),
    dict(level='a', tag='Insurance · migration', title='Is rewriting 400 MapReduce jobs worth it?',
         problem='<p>An insurer runs 400 MapReduce jobs nightly, using 6,000 container-hours a night. Rewriting a job in Spark SQL takes 2 developer-days (₹8,000 per day). Assume the rewritten jobs use 55% fewer container-hours, and a container-hour costs ₹4 (illustrative). How long until the rewrite pays back?</p>',
         inp='400 jobs · 2 days × ₹8,000 · 6,000 container-hours/night · −55% · ₹4/hour',
         approach=['Cost = jobs × days × daily rate.',
                   'Saving per night = 6,000 × 0.55 × ₹4.',
                   'Payback = cost ÷ saving per night.'],
         code='''cost = 400 * 2 * 8000
saving = 6000 * 0.55 * 4
print(f"rewrite Rs {cost:,}, saves Rs {saving:,.0f} a night, payback {cost / saving:.0f} nights")
''', notes={3: 'Payback :: Ignores testing and risk; real projects migrate the heaviest jobs first.'},
         tryit='About 485 nights at these numbers. Starting with the 50 jobs that use most container-hours usually pays back far faster.'),
]

QUIZ = mix([
    dict(q='In our lab, where did Spark\'s executors run?', options=['On a separate Spark cluster', 'In YARN containers on our Hadoop workers', 'Only on the client machine', 'Inside the NameNode'], answer=1,
         why='spark-submit --master yarn asked our ResourceManager for an AM and 3 executor containers.'),
    dict(q='What did Spark replace in the Hadoop stack?', options=['HDFS', 'MapReduce, the processing engine', 'YARN', 'The NameNode'], answer=1,
         why='HDFS and YARN stayed; Spark ran on them.'),
    dict(q='Five passes over the same 140 MB: which result is from our lab?', options=['MapReduce 199 s, cached Spark 35.3 s', 'MapReduce 35 s, Spark 199 s', 'Both about 75 s', 'Spark could not run on YARN'], answer=0,
         why='Uncached Spark took 75.3 s.'),
    dict(q='In the Spark plan, what is "Exchange hashpartitioning(item, 200)"?', options=['Reading the CSV', 'The shuffle, partitioning rows by item into 200 partitions', 'Writing to HDFS', 'Caching'], answer=1,
         why='Exchange is Spark\'s name for a shuffle.'),
    dict(q='What does "HashAggregate(partial_count, partial_sum)" before the Exchange correspond to?', options=['A reducer', 'A combiner: aggregating inside each map task before the shuffle', 'A partitioner', 'Speculative execution'], answer=1,
         why='Lesson 9.1: combine before shuffling.'),
    dict(q='Why was the first cached pass slower than the others?', options=['It read HDFS and filled the cache', 'The cache was broken', 'YARN was restarting', 'It used MapReduce'], answer=0,
         why='21.4 s, then 4.2, 3.7, 3.3 and 2.7 s from memory.'),
    dict(q='How does Spark recover a lost cached partition?', options=['From a replica in HDFS only', 'By recomputing it from its lineage', 'It cannot; the job fails', 'By restarting the whole application'], answer=1,
         why='Each RDD/DataFrame knows the steps that built it.'),
    dict(q='Which job gains least from Spark over MapReduce?', options=['A 30-pass machine learning model', 'An interactive SQL notebook', 'A single pass copying a huge file on a memory-poor cluster', 'A streaming dashboard'], answer=2,
         why='One pass with no reuse is limited by disks for both engines.'),
])

REVISION = [
    'Spark is a DAG engine with lazy transformations, actions, long-lived <b>executors</b>, a <b>driver</b>, caching and <b>lineage</b>; Catalyst and Tungsten optimize DataFrames and SQL.',
    'Spark usually runs <b>on</b> Hadoop: YARN containers for executors, HDFS for data. It replaced MapReduce, not HDFS or YARN.',
    'Mapping: map/filter = map, reduceByKey = combiner + shuffle + reduce, Exchange = shuffle, partition = split, executor = container.',
    'Lab: same answers as Lesson 8.1; RDD 7.4 s, DataFrame 11.3 s; spark-submit 46 s including start-up.',
    'Lab, 5 passes over 9 M orders: MapReduce 199 s; Spark 75.3 s; Spark + cache 35.3 s (passes 2–5: 2.7–4.2 s).',
    'Spark wins most on iterative, interactive and streaming work; a single huge scan is disk-bound for both.',
    'Oct 2026: Spark 4.2/4.1/4.0 current, 3.5 LTS to Nov 2027; EMR 7.14, Dataproc 2.3 and Cloudera 7.3.2 ship Spark 3.5.',
]
FAQ = [
    ('Is Spark a replacement for Hadoop?', 'Spark replaces Hadoop MapReduce as the processing engine, not Hadoop as a whole. Spark has no storage or resource manager of its own, so on most Hadoop clusters it runs on YARN and reads HDFS. It can also run on Kubernetes or its standalone manager with cloud object storage, which is how many new platforms use it.'),
    ('Why is Spark faster than MapReduce?', 'Spark plans a whole multi-step job as one DAG, keeps intermediate data in memory or on local disk instead of writing it to HDFS between steps, reuses long-lived executors instead of starting a JVM per task, can cache datasets across passes, and optimizes DataFrame/SQL plans with Catalyst and Tungsten. In our lab, five passes took 199 s with MapReduce and 35.3 s with cached Spark.'),
    ('Is MapReduce still used?', 'Yes, but mostly for existing jobs and tools built on it, such as DistCp and Hadoop Archive. New batch, SQL, machine learning and streaming work is usually written in Spark (or Hive on Tez, Flink, Trino), often running on the same YARN cluster as the old MapReduce jobs.'),
    ('What is the difference between an RDD and a DataFrame?', 'An RDD is a distributed collection of objects transformed with functions you write; Spark cannot see inside those functions. A DataFrame is a table with a schema, written with SQL or column expressions, which the Catalyst optimizer can rewrite (for example reading only needed columns and aggregating before the shuffle). DataFrames are the recommended API for most work.'),
    ('Does Spark need more memory than MapReduce?', 'Usually yes. Executors are long-lived and use memory for caching and for shuffles and joins; when memory runs short Spark spills to disk, and badly sized executors can fail with out-of-memory errors. MapReduce streams data through short-lived tasks and needs less memory, at the cost of disk I/O between steps.'),
]

PRACTICE_INTRO = 'Exercises using the real MapReduce and Spark numbers from our cluster.'
PROBLEMS = [
    dict(level='easy', title='Speed-ups', stmt='Compute how many times faster cached Spark was than MapReduce, and than uncached Spark, for 5 passes.', inp='199 s · 75.3 s · 35.3 s',
         code='''print(f"vs MapReduce {199 / 35.3:.1f}x, vs uncached Spark {75.3 / 35.3:.1f}x")
''', explain='About 5.6× and 2.1×. Part of the first gap is the HDFS write and job start-up in every MapReduce pass, the rest is caching.'),
    dict(level='easy', title='Cost of the first pass', stmt='What share of the cached run\'s 35.3 s was spent in pass 1?', inp='21.4 s of 35.3 s',
         code='''print(f"{21.4 / 35.3:.0%}")
''', explain='About 61%: reading HDFS and filling the cache dominate a short run.'),
    dict(level='easy', title='Same answer?', stmt='Check that Spark\'s chai revenue equals the MapReduce result from Lesson 8.1 and that the price works out.', inp='50170 orders, 752550',
         code='''print(752550 == 50170 * 15)
''', explain='True: every chai costs ₹15 in this dataset, and both engines agree.'),
    dict(level='medium', title='When does caching pay?', stmt='The cached run\'s first pass costs 1.6 s more than the uncached one, but every later pass saves about 10.4 s. From how many passes is caching worth it?', inp='21.4 vs 19.8 · 3.475 vs 13.875',
         code='''for k in range(1, 4):
    print(k, "passes: cache", round(21.4 + (k - 1) * 3.475, 1), "no cache", round(19.8 + (k - 1) * 13.875, 1))
''', explain='From 2 passes on. With a single pass, caching only costs time.'),
    dict(level='medium', title='Word count, Spark style', stmt='Simulate flatMap → map → reduceByKey on three lines.', inp='3 lines of feedback',
         code='''lines = ["chai was hot", "dosa was cold", "chai was late"]
words = [w for line in lines for w in line.split()]       # flatMap
pairs = [(w, 1) for w in words]                           # map
counts = {}
for w, n in pairs:                                        # reduceByKey
    counts[w] = counts.get(w, 0) + n
print(sorted(counts.items()))
''', explain='The same three steps as Lesson 8.6\'s WordCount.java, written as one chain in Spark: lines.flatMap(split).map(lambda w: (w, 1)).reduceByKey(add).'),
    dict(level='medium', title='Partitions from blocks', stmt='textFile makes about one partition per HDFS block. How many partitions do 140 MB and 4.7 MB files get with 128 MB blocks?', inp='140,759,640 and 4,692,009 bytes',
         code='''import math
for size in [140_759_640, 4_692_009]:
    print(size, "->", max(2, math.ceil(size / (128 * 1024 * 1024))), "partitions")
''', explain='Both get 2 (textFile asks for at least 2 partitions by default), matching "partitions: 2" in our RDD run.'),
    dict(level='business', title='Cluster time saved per day', stmt='A bank runs 120 iterative jobs a day, 10 passes each. Using our per-pass numbers, how many cluster-hours a day does cached Spark save over MapReduce?', inp='120 jobs × 10 passes',
         code='''mr = 10 * 39.8
spark = 21.4 + 9 * 3.475 + 46
print(f"{120 * (mr - spark) / 3600:.1f} hours of job time saved per day")
''', explain='About 10 hours of job time a day on our lab\'s scale (illustrative); on real clusters, multiply by the containers each job holds.'),
    dict(level='advanced', title='Recompute from lineage', stmt='Three cached partitions; executor 2 dies and loses partition 1. Recompute only that partition from its lineage and check the total is unchanged.', inp='3 partitions, lineage = filter ≥ 18 then double',
         code='''source = [[15, 18, 20], [25, 30, 45], [18, 80, 15]]
lineage = lambda part: [x * 2 for x in part if x >= 18]
cache = [lineage(p) for p in source]
before = sum(map(sum, cache))
cache[1] = None                              # executor lost
recomputed = 0
for i, p in enumerate(cache):
    if p is None:
        cache[i] = lineage(source[i]); recomputed += 1
print("recomputed", recomputed, "partition; total same:", sum(map(sum, cache)) == before)
''', explain='Only the lost partition is rebuilt, from its source block and its recipe. MapReduce instead re-runs the failed task from its HDFS input.'),
]

SCN_INTRO = 'Hadoop vs Spark is asked in almost every big data interview, often as a trap: the best answers start by saying Spark usually runs on Hadoop.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Concepts · basics</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>"Hadoop or Spark: which is better?"</h4>
      <p class="scn__situation">An opening question in a data engineering interview.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> that you know they are not alternatives.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Hadoop is storage (HDFS) + resources (YARN) + an engine (MapReduce); Spark is an engine, commonly running on YARN and HDFS.</li>
          <li>As engines, Spark is faster for multi-step, iterative and interactive work: memory between steps, long-lived executors, Catalyst.</li>
          <li>Example: on one cluster, five passes took 199 s as MapReduce jobs and 35 s with cached Spark.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Internals · plans</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>"Explain this Spark plan in MapReduce terms"</h4>
      <p class="scn__situation">The interviewer shows FileScan → HashAggregate(partial) → Exchange → HashAggregate.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> real understanding of shuffles.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>FileScan with a narrow ReadSchema is the map input with column pruning.</li>
          <li>The partial aggregate is a combiner inside each map task; Exchange hashpartitioning is the shuffle with a hash partitioner.</li>
          <li>The final aggregate is the reducer; a stage boundary sits at each Exchange.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Operations · memory</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>A Spark job that was fast in testing fails with executor OOM in production</h4>
      <p class="scn__situation">The team cached a large DataFrame and joins it with another.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> memory sizing and options.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Check executor memory vs cached size (Storage tab in the Spark UI), skewed keys, and shuffle partition counts.</li>
          <li>Use MEMORY_AND_DISK, cache only what is reused, cache columnar DataFrames rather than object RDDs, raise memory or partitions.</li>
          <li>Fix skew (salting, AQE skew join) and broadcast small tables (Lesson 9.6).</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Architecture · migration</span><span class="scn__tag scn__tag--level">Lead</span></div>
      <h4>"Should we rewrite all our MapReduce jobs in Spark?"</h4>
      <p class="scn__situation">A company has 400 stable MapReduce jobs on a Hadoop cluster.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> pragmatic migration thinking.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Not all at once: rank jobs by cluster-hours and business value; rewrite the heaviest and the multi-step chains first.</li>
          <li>Run old and new side by side on the same YARN queues and compare outputs row by row before switching.</li>
          <li>Keep jobs that are one-pass, stable and cheap; write all new work in Spark SQL/DataFrames.</li>
        </ul>
      </div></details>
    </article>
'''
