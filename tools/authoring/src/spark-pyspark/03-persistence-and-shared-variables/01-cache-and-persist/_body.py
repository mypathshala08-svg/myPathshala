import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
def has(n, *keys):
    return '\n'.join(l for l in capf(n).split('\n') if any(k in l for k in keys))

def opbox(x, y, label, sub='', tone='card', w=128, h=26):
    o = box(x, y, w, h, tone) + t(x + w / 2, y + (11 if sub else 16), label, 7.2, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 21, sub, 6.4, 'ink2', mono=True)
    return o

def fig(src, w, h, alt, caption):
    return f'''  <figure style="margin:18px 0">
    <img src="{src}" width="{w}" height="{h}" loading="lazy" alt="{alt}" style="max-width:100%;height:auto;border:1px solid var(--line);border-radius:8px">
    <figcaption class="muted" style="font-size:.9em;margin-top:6px">{caption}</figcaption>
  </figure>
'''

def execbox(mem='', disk='', hi=None, note=''):
    o = box(20, 24, 320, 80, 'card') + t(180, 38, 'executor', 7.4, 'ink2', bold=True)
    o += opbox(32, 46, 'memory', mem, 'acc' if hi == 'mem' else 'green', 140, 34)
    o += opbox(188, 46, 'local disk', disk, 'acc' if hi == 'disk' else 'violet', 140, 34)
    if note:
        o += t(180, 96, note, 6.8, 'ink2')
    return o

# ---------------------------------------------------------------- story
sc = (execbox('cached partitions', 'spilled partitions') +
      box(410, 12, 222, 136, 'card') + t(521, 30, 'Measured on the cluster', 8.6, bold=True) +
      ''.join(t(422, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
          ('no cache, 2nd query  : 6.7 s', 'amber'), ('MEMORY_ONLY, 2nd     : 2.7 s', 'green'), ('MEMORY_AND_DISK, 2nd : 2.2 s', 'green'),
          ('DISK_ONLY, 2nd       : 2.1 s', 'green'), ('651 MiB in 32 partitions', 'ink'), ('4 huge partitions: exit 52', 'red')])))
scene_svg = scene('Persisting keeps an RDD or DataFrame’s partitions on the executors after the first action, in memory, on local disk or both, so later actions skip recomputation. Our cluster measured each storage level and found a way to crash executors.', sc,
                  'Cache what you <tspan font-weight="700" class="s-acc">reuse</tspan>, in a form that <tspan font-weight="700" class="s-acc">fits</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Just cache everything”</h2>
  <div class="story">
    <p class="narration">After Module 2, Kabir has a new habit: he adds <code>.cache()</code> to every DataFrame. His morning report on TiffinGo’s five million orders got faster. Then one night the job died with “Command exited with code 52” on every executor, and nobody could explain why caching, of all things, broke it.</p>

{scene_svg}

K> Sir, caching made things faster. How can it crash a job?
A> Cached data takes executor memory, the same memory your tasks need to run. Spark offers several <b>storage levels</b>: memory only, memory and disk, disk only, serialised or not, replicated or not. Pick the wrong one, or cache data in partitions too big for the executor, and you trade speed for failures.
R> So when should we cache, and how?
A> Cache only what several actions reuse, choose a storage level that fits, check the Storage tab, and unpersist when done. Today we measure every level on our cluster with five million orders, look at the Storage tab, and reproduce Kabir’s crash. All outputs are real (Spark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Caching at three levels
L1> Keeping cooked food on the counter
      <ul>
        <li>Without caching, every new order cooks the dish from scratch.</li>
        <li><code>cache()</code> keeps a cooked batch on the counter (memory); if the counter is full, some goes to the fridge (disk).</li>
        <li>An overfull counter leaves no room to cook: the kitchen stops.</li>
      </ul>
L2> The API
      <ul>
        <li><code>df.cache()</code> = <code>persist()</code> with the default level: <b>MEMORY_AND_DISK</b> for DataFrames (deserialised, columnar), <b>MEMORY_ONLY</b> serialised for PySpark RDDs.</li>
        <li><code>persist(StorageLevel.X)</code>: MEMORY_ONLY, MEMORY_AND_DISK, DISK_ONLY, the <code>_2</code> variants (two replicas), OFF_HEAP.</li>
        <li>Caching is <b>lazy</b>: the first action fills it. SQL <code>CACHE TABLE</code> is eager; <code>CACHE LAZY TABLE</code> is not. Release with <code>unpersist()</code>, <code>UNCACHE TABLE</code> or <code>spark.catalog.clearCache()</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>The second query took 6.7 s uncached and 2.1–2.7 s with any storage level; filling the cache made the first query slower (21–29 s vs 15 s).</li>
        <li>5,000,000 rows with 128-character notes needed 651 MiB of cache over 32 partitions.</li>
        <li>The same data in only 4 partitions killed every 1 GiB executor while caching (exit code 52 = OutOfMemoryError); the job was aborted after 4 attempts.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Persistence and storage levels</h2>
''' + def_block(
    '<b>Persistence</b> (caching) instructs Spark to keep the computed partitions of an RDD or DataFrame on the executors after the first action that computes them, so later actions read them instead of recomputing the lineage. <code>persist(level)</code> chooses a <b>storage level</b>: whether to use memory, local disk or off-heap memory, whether to store objects serialised, and how many replicas to keep; <code>cache()</code> uses the default level (MEMORY_AND_DISK for DataFrames and Datasets, stored in Spark’s compressed in-memory columnar format; MEMORY_ONLY for RDDs). Cached blocks share executor memory with task execution and are evicted in least-recently-used order under pressure; with MEMORY_ONLY evicted partitions are recomputed, with MEMORY_AND_DISK they are written to local disk. Persistence is lazy, is lost with its executor, and should be released with <code>unpersist()</code>.',
    'cache() or persist() keeps data on the executors after it is first computed, so the next actions are faster. You choose where: memory, disk or both. It uses memory that tasks also need, so cache only what you reuse and remove it when finished.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('cache()', 'persist() with the default storage level.'),
    ('persist(level)', 'Keep data with a chosen storage level.'),
    ('Storage level', 'Memory / disk / off-heap, serialised or not, replicas.'),
    ('Serialised', 'Stored as bytes: smaller, but costs CPU to read.'),
    ('Eviction', 'Removing cached blocks when memory is needed (LRU).'),
    ('Storage tab', 'Spark UI page listing cached data, sizes and fractions.'),
    ('unpersist()', 'Remove cached data from executors.'),
    ('Exit code 52', 'An executor JVM died from OutOfMemoryError.'),
]) + '''

  <h3>Storage levels</h3>
''' + table(['Level', 'Memory', 'Disk', 'If memory is full', 'Use when'], [
    ['MEMORY_ONLY', 'yes', 'no', 'Partitions not cached; recomputed when needed', 'Fits comfortably; cheap to recompute'],
    ['MEMORY_AND_DISK (DataFrame default)', 'yes', 'yes', 'Overflow written to local disk', 'Expensive to recompute; most cases'],
    ['DISK_ONLY', 'no', 'yes', '—', 'Large, expensive results; memory needed for tasks'],
    ['MEMORY_ONLY_2, MEMORY_AND_DISK_2', 'yes', '(yes)', 'Two copies on two executors', 'Fast recovery matters (spot nodes)'],
    ['OFF_HEAP', 'off-heap', 'no', 'Needs off-heap memory enabled', 'Reduce GC pressure; advanced'],
], minw=760) + lv + '''
EXAM> “cache() vs persist()?” cache() is persist() with the default level (MEMORY_AND_DISK for DataFrames, MEMORY_ONLY for RDDs). persist() lets you choose: MEMORY_ONLY, MEMORY_AND_DISK, DISK_ONLY, replicated _2 levels or OFF_HEAP. Both are lazy and need an action to fill; release with unpersist().
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>When to cache, and when not to</h2>
''' + table(['Situation', 'Cache?', 'Why'], [
    ['Same DataFrame used by several actions or reports', 'Yes', 'Avoid repeated reads and transformations'],
    ['Iterative algorithms (ML, graphs)', 'Yes', 'Many passes over the same data'],
    ['Interactive exploration in a notebook', 'Yes, then unpersist', 'Many small queries on one dataset'],
    ['Used once', 'No', 'Filling the cache only costs time and memory'],
    ['Cheap to recompute (simple filter on Parquet)', 'Usually no', 'Reading Parquet can be as fast as reading the cache'],
    ['Bigger than the cluster’s memory', 'DISK_ONLY or write to Parquet', 'Avoid eviction storms and OOM'],
    ['Must survive executor loss or long lineage', 'Checkpoint (3.3) or write out', 'Cache is lost with its executor'],
], minw=680) + '''
WARN> A cache is not free. In our lab, the first query <b>with</b> caching took 21–29 s against 15 s without, because Spark had to build the cache. If a dataset is used once, or is as cheap to read from Parquet as from the cache, caching makes the job slower and steals memory from tasks.
</section>
'''

FIG = fig('ui-storage.webp', 1280, 520, 'Spark UI Storage tab listing a cached DataFrame of 47.5 MiB and a disk-only aggregated DataFrame with 200 partitions', 'Real screenshot: the Storage tab. The filtered orders (MEMORY_AND_DISK, 2 partitions, 100% cached, 47.5 MiB in memory) and an aggregation persisted with DISK_ONLY (200 partitions, 118.8 KiB on disk).')
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Measuring every storage level</h2>
  <p>All outputs are real: PySpark 4.3.0 in local mode (Steps 1–3, 6) and on our standalone cluster with two executors of 2 cores and 1 GiB (Steps 4–5). Data: <code>orders_big</code>, 5,000,000 orders.</p>
''' + stepper([
    ('Step 1 · cache() is lazy, and has a default level',
     code('python', 'basics.py', "df = orders.where(\"status = 'DELIVERED'\").cache()\nprint(df.storageLevel)\nprint(len(storage()))           # entries in the UI's /storage/rdd API\ndf.count()\ns = storage()[0]\nprint(s[\"numCachedPartitions\"], s[\"numPartitions\"], s[\"memoryUsed\"])", '\n'.join(capf('l31_basics.txt').split('\n')[:4])),
     'Calling <code>cache()</code> stored nothing: zero cached entries until <code>count()</code> ran. A DataFrame’s default level is <b>Disk Memory Deserialized</b> (MEMORY_AND_DISK). The 4.75 million delivered orders took only <b>47.5 MiB</b>: DataFrames are cached in a compressed columnar format, much smaller than Python objects would be.'),
    ('Step 2 · RDD defaults and persist()',
     code('python', 'basics.py', 'rdd = sc.parallelize(range(10)).cache()\nprint(rdd.getStorageLevel())\np = orders.persist(StorageLevel.DISK_ONLY)\nprint(p.storageLevel)', has('l31_basics.txt', '2)', '3)')),
     'For PySpark RDDs, <code>cache()</code> means MEMORY_ONLY with <b>serialised</b> (pickled) data: Python objects are always stored as bytes on the JVM side. <code>persist()</code> takes any <code>StorageLevel</code>; here DISK_ONLY writes the partitions to the executors’ local disks.'),
    ('Step 3 · The Storage tab',
     code('python', 'storage_tab.py', "d = o.where(\"status = 'DELIVERED'\").cache(); d.count()\nc = o.groupBy(\"city\", \"order_date\").agg(F.sum(\"amount\").alias(\"rev\")).persist(StorageLevel.DISK_ONLY); c.count()", 'Spark UI → Storage') + FIG,
     'Every cached dataset appears with its level, number of cached partitions, <b>fraction cached</b> and sizes in memory and on disk. A fraction below 100% means some partitions did not fit and will be recomputed (MEMORY_ONLY) or read from disk. The aggregated DataFrame kept 200 partitions, the default <code>spark.sql.shuffle.partitions</code>, all tiny: worth a <code>coalesce</code> before caching.'),
    ('Step 4 · Every level on the cluster',
     code('python', 'cache_levels.py (cluster)', "base = (spark.read.parquet(\"/data/orders_big\").repartition(32)\n        .withColumn(\"note\", F.concat(F.sha2(F.col(\"order_id\").cast(\"string\"), 256),\n                                     F.sha2(F.concat_ws(\"-\", \"order_id\", \"customer_id\"), 256))))\ndef q(df):\n    return df.where(\"status = 'DELIVERED'\").groupBy(\"city\").agg(F.sum(\"amount\")).collect()\nfor name in [\"MEMORY_ONLY\", \"MEMORY_AND_DISK\", \"DISK_ONLY\"]:\n    df = base.persist(getattr(StorageLevel, name))\n    q(df); q(df)                      # fill, then reuse (both timed)\n    df.unpersist(blocking=True)", capf('l31_levels32.txt')),
     'We added a 128-character note per order (random-looking hashes, so it does not compress) to make the data realistic in size: <b>651 MiB</b> cached over 32 partitions. Without a cache, the second query re-read and re-hashed everything (6.7 s). With any level, it took 2.1–2.7 s. DISK_ONLY was as fast as memory here because the lab’s disks are fast and the data was read sequentially; on busy clusters memory usually wins. Filling a cache always cost extra the first time.'),
    ('Step 5 · How caching crashed every executor',
     code('python', 'cache_levels.py (cluster), without repartition(32)', 'base = spark.read.parquet("/data/orders_big").withColumn("note", …)    # only 4 partitions\ndf = base.persist(StorageLevel.MEMORY_ONLY)\nq(df)', capf('l31_none.txt') + '\n' + capf('l31_oom.txt').replace(': org.apache.spark.SparkException: ', '').replace('Job aborted', 'SparkException: Job aborted')),
     'Kabir’s crash, reproduced. With the same data in only <b>4 partitions</b> (1,250,000 rows each), every task had to build a cached block of about 160 MiB inside a 1 GiB executor, next to Parquet decoding and hashing. Executors died with <b>exit code 52</b>, Spark’s code for OutOfMemoryError; replacements died too, and after 4 failed attempts the job was aborted. Smaller partitions (Step 4), a disk level, more executor memory or not caching at all would each have avoided it.'),
    ('Step 6 · SQL caching and cleaning up',
     code('python', 'basics.py', "spark.sql(\"CACHE TABLE delivered AS SELECT * FROM parquet.`orders_big` WHERE status = 'DELIVERED'\")\nspark.sql(\"CACHE LAZY TABLE lazy_t AS SELECT city FROM parquet.`orders_big`\")\nspark.catalog.isCached(\"delivered\")\ndf.unpersist(); p.unpersist(); spark.sql(\"UNCACHE TABLE delivered\"); spark.catalog.clearCache()", has('l31_basics.txt', '4)', 'CACHE LAZY', 'isCached', '5)')),
     'Unlike <code>cache()</code>, SQL <code>CACHE TABLE</code> is <b>eager</b>: it runs immediately (one new cached entry). <code>CACHE LAZY TABLE</code> waits for the first query. Release caches explicitly: <code>unpersist()</code> for DataFrames and RDDs, <code>UNCACHE TABLE</code> for tables, <code>clearCache()</code> for everything. Unused caches otherwise stay until memory pressure evicts them.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('df = orders.where(…).cache()', W), ('cached entries: 0', Y), ('df.count()', W), ('2 of 2 partitions, 47.5 MiB', G)], size=7.4),
    term([('DataFrame: Disk Memory Deserialized', W), ('RDD      : Memory Serialized', W), ('DISK_ONLY: Disk Serialized', W)], size=7.4),
    term([('NONE            2nd 6.7 s', Y), ('MEMORY_ONLY     2nd 2.7 s', G), ('MEMORY_AND_DISK 2nd 2.2 s', G), ('DISK_ONLY       2nd 2.1 s', G)], size=7.4),
    term([('4 partitions, MEMORY_ONLY', W), ('Lost executor 0: exited with code 52', RD), ('Lost executor 1: exited with code 52', RD), ('Task failed 4 times; aborting job', RD)], size=7.0),
    term([('CACHE TABLE delivered …   (eager)', W), ('CACHE LAZY TABLE lazy_t … (lazy)', W), ('clearCache() → 0 entries', G)], size=7.2),
]
B1 = [
    t(180, 12, 'Lazy until an action', 9.4, bold=True) + execbox('empty, then 47.5 MiB', '—', 'mem') + cap('The first action fills the cache.', '', 'blue', y=116, h=30),
    t(180, 12, 'Where and how', 9.4, bold=True) + execbox('DataFrame: columnar', 'DISK_ONLY: bytes', None) + cap('Pick the level per dataset.', '', 'violet', y=116, h=30),
    t(180, 12, 'Reuse instead of recompute', 9.4, bold=True) + execbox('32 cached partitions', '651 MiB (DISK_ONLY)', 'mem') + cap('The 2nd query reads the cache.', '', 'green', y=116, h=30),
    t(180, 12, 'Caching competes for memory', 9.4, bold=True) + execbox('160 MiB block + task', '—', 'mem', 'one 1 GiB JVM') + cap('Huge partitions → OutOfMemory.', '', 'red', y=116, h=30),
    t(180, 12, 'Release what you no longer need', 9.4, bold=True) + execbox('free', 'free', None) + cap('unpersist · UNCACHE · clearCache.', '', 'green', y=116, h=30),
]
see_caps = ['cache() did nothing until count().',
            'Defaults differ for DataFrames and RDDs.',
            'Every level made the second query faster.',
            'Four huge cached partitions killed every executor.',
            'SQL caching is eager; clean up explicitly.']
behind_caps = ['Spark marks the plan; tasks fill the blocks.',
               'Python RDD data is always stored serialised.',
               'Reading cached blocks skips Parquet and hashing.',
               'Exit code 52 = OutOfMemoryError in the executor.',
               'Freed memory goes back to tasks.']
two = anim_two('Caching', 'Keep what you reuse', 'Real lab outputs', 'Inside the executor', see, B1, see_caps, behind_caps)

# ---- scenario 1: the code 52 night
e1 = (t(180, 22, 'Nightly job: exit code 52', 9.4, bold=True) + t(180, 56, 'on every executor', 8.4, 'ink2') + cap('After adding cache().', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Check partition sizes', 9.4, bold=True) + t(180, 56, '4 partitions × 1.25 M rows', 8.4, 'ink', mono=True) + cap('~160 MiB cached per task.', '', 'amber', y=150, h=34))
e3 = (t(180, 22, 'More, smaller partitions', 9.4, bold=True) + t(180, 56, 'repartition(32) before caching', 8.4, 'ink', mono=True) + cap('651 MiB fits across executors.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Or a disk level', 9.4, bold=True) + t(180, 56, 'persist(StorageLevel.DISK_ONLY)', 8.2, 'ink', mono=True) + cap('Memory left for tasks.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Or no cache at all', 9.4, 'acc', bold=True) + t(180, 56, 'used once? remove it', 8.4, 'ink2') + cap('The cheapest fix.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'The night caching crashed the job',
              'Kabir’s incident, as we reproduced it. (Real behaviour from our lab.)',
              'Cache and OOM', 'Huge cached partitions exhaust executor memory; repartition, use a disk level or stop caching data used once', [e1, e2, e3, e4, e5],
              ['Executors die.', 'Partitions too big.', 'Repartition.', 'Use disk.', 'Or remove the cache.'],
              hid='scenario-code52')

# ---- scenario 2: notebook memory leak
b1 = (t(180, 22, 'Notebook gets slower all day', 9.4, bold=True) + t(180, 56, '20 DataFrames cached, never released', 8.2, 'ink2') + cap('Memory fills up.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Storage tab', 9.4, bold=True) + t(180, 56, 'fraction cached: 40% · 60% · …', 8.4, 'ink', mono=True) + cap('Evictions everywhere.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'Unpersist old results', 9.4, bold=True) + t(180, 56, 'df.unpersist() · clearCache()', 8.4, 'ink', mono=True) + cap('Free executor memory.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Cache one base dataset', 9.4, bold=True) + t(180, 56, 'not every intermediate step', 8.4, 'ink2') + cap('Reuse it.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Fast again', 9.4, 'acc', bold=True) + t(180, 56, 'fraction cached: 100%', 8.4, 'ink', mono=True) + cap('And tasks have room.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'A notebook that caches everything',
              'Why caches need cleaning. (Typical.)',
              'Cache hygiene', 'Too many caches evict each other and starve tasks; cache one reused dataset and unpersist the rest', [b1, b2, b3, b4, b5],
              ['Slow notebook.', 'Partial caches.', 'Release.', 'Cache less.', 'Fast again.'],
              hid='scenario-notebookcache')

# ---- scenario 3: choose level for spot clusters
u1 = (t(180, 22, 'ML training on spot nodes', 9.4, bold=True) + t(180, 56, 'features cached, 50 iterations', 8.4, 'ink2') + cap('Executors can disappear.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'One node lost', 9.4, bold=True) + t(180, 56, 'its cached partitions recomputed', 8.4, 'ink2') + cap('Slow iteration.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'MEMORY_AND_DISK_2', 9.4, bold=True) + t(180, 56, 'a second copy on another executor', 8.2, 'ink2') + cap('Survives one loss.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Cost', 9.4, bold=True) + t(180, 56, 'double the cache memory', 8.4, 'ink2') + cap('Only for expensive data.', '', 'amber', y=150, h=34))
u5 = (t(180, 22, 'Or checkpoint', 9.4, 'acc', bold=True) + t(180, 56, 'reliable storage (Lesson 3.3)', 8.4, 'ink2') + cap('Survives everything.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Caching on machines that can disappear',
              'Choosing a storage level for reliability. (Typical practice.)',
              'Replicated levels', 'Replicated storage levels keep a second copy so one lost executor does not force recomputation; checkpoints survive everything', [u1, u2, u3, u4, u5],
              ['Spot nodes.', 'Loss forces recompute.', 'Two copies.', 'Twice the memory.', 'Or checkpoint.'],
              hid='scenario-replicated')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Keep what you reuse</h2>
  <p>Left: real outputs. Right: inside the executor.</p>
''' + two + '''
  <p>Three live scenarios follow: the exit-code-52 night, a notebook that caches everything, and caching on spot nodes.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Caching at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'reports', 10, 'blue', bold=True) + t(60, 58, 'one base', 7.4, 'ink2'),
    '1. One base, many reports',
    'A cleaned, filtered dataset is cached once and feeds several aggregations in the same job.',
    ['Clean', '*cache', 'Reports']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'ML', 12, 'green', bold=True) + t(60, 58, 'iterations', 7.4, 'ink2'),
    '2. Machine learning',
    'Training data is cached before iterative algorithms make many passes over it.',
    ['Features', '*cache', 'Training']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'BI', 12, 'violet', bold=True) + t(60, 58, 'warm tables', 7.4, 'ink2'),
    '3. Warm tables for dashboards',
    'Long-running Spark SQL servers CACHE TABLE hot tables so dashboards answer quickly.',
    ['Hot table', '*CACHE TABLE', 'Fast queries']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'review', 10, 'acc', bold=True) + t(60, 58, 'cache()', 7.4, 'ink2'),
    '4. Code reviews',
    'Reviewers ask “is this reused?” for every cache() and “where is the unpersist?”.',
    ['cache()', '*review', 'Kept or removed']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'incidents', 9, 'acc', bold=True) + t(60, 58, 'OOM', 7.4, 'ink2'),
    '5. Memory incidents',
    'Exit code 52 and evictions in the Storage tab are classic signs of over-caching.',
    ['OOM', '*Storage tab', 'Fix']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> Lesson <a href="../../02-rdds/03-lazy-evaluation-and-the-dag/">2.3</a> (why every action recomputes) and <a href="../../01-introduction/03-spark-architecture/">1.3</a> (executors).</p></div>
'''
EXTRA = ''
_x = os.path.join(HERE, '_extra.py')
if os.path.exists(_x): exec(open(_x).read())
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + EXTRA + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
