import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
BODY = body(HERE)

META = dict(
    module='03-persistence-and-shared-variables', lesson='01-cache-and-persist', n='3.1',
    module_label='Module 3 · Persistence and shared variables',
    title='cache and persist: storage levels',
    desc='Caching in Spark 4.3.0, measured: cache() is lazy, DataFrames default to MEMORY_AND_DISK in a compressed columnar format (4.75 M orders in 47.5 MiB), PySpark RDDs to serialised MEMORY_ONLY; MEMORY_ONLY, MEMORY_AND_DISK and DISK_ONLY compared on a cluster (second query 6.7 s uncached vs 2.1–2.7 s cached, 651 MiB), the Storage tab, CACHE TABLE vs CACHE LAZY TABLE, and how caching four huge partitions killed every executor with exit code 52.',
    og_desc='cache() made the report 3× faster, then crashed every executor with exit code 52. Storage levels, measured on a real Spark cluster.',
    minutes=34, level='Intermediate',
    lead='Module 3 is about keeping and sharing data across a Spark application. This lesson starts with <b>cache() and persist()</b>: what they really store, how each storage level performs on our cluster, how to read the Storage tab, and how careless caching can crash a job. <b>All outputs and screenshots are real</b> (Spark 4.3.0).',
    chips=['Spark 4.3.0 cluster', 'Every storage level timed', 'An OOM reproduced', 'Runs in your browser (Python)'],
)

MAIN = '''# When does caching pay off? A cost model using the lab's timings
read_and_compute = 6.7     # s: a query without cache (2nd run, lab)
from_cache = 2.4           # s: a query reading the cache (lab: 2.1-2.7)
fill_extra = 6.2           # s: extra time to build the cache on first use (lab: 21.5 vs 15.3)

for uses in (1, 2, 3, 5, 10):
    no_cache = uses * read_and_compute
    cached = (read_and_compute + fill_extra) + (uses - 1) * from_cache
    better = "cache" if cached < no_cache else "no cache"
    print(f"{uses:2} uses: no cache {no_cache:5.1f} s | cache {cached:5.1f} s -> {better}")
'''
RUN = dict(
    heading='Run the code: should I cache?',
    intro='<p>A small cost model with the timings measured in Step 4: caching costs extra once and saves time on every reuse. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('fill_extra = 6.2           # s: extra time to build the cache on first use (lab: 21.5 vs 15.3)', 'The first query with MEMORY_AND_DISK took 21.5 s against 15.3 s without caching.'),
        ('    cached = (read_and_compute + fill_extra) + (uses - 1) * from_cache', 'Pay once to fill, then cheap reads.'),
    ],
    tasks=[
        dict(label='1 · Find the break-even', hint='Press <b>Run</b>. From how many uses does caching win?', code=None),
        dict(label='2 · Predict first: memory needed', hint='<b>Predict first:</b> does 651 MiB fit in two executors with about 434 MiB storage memory each?',
             code='''cache_mib, executors, storage_mib = 651, 2, 434
print("fits" if cache_mib <= executors * storage_mib else "does not fit", f"({cache_mib} of {executors * storage_mib} MiB)")
'''),
        dict(label='3 · Partition size', hint='Size of one cached partition for 4 and 32 partitions.',
             code='''total = 651
for parts in (4, 32):
    print(parts, "partitions ->", round(total / parts), "MiB each")
'''),
        dict(label='4 · Choose a level', hint='Pick a storage level for each case.',
             code='''cases = {"small lookup, reused 20x": "MEMORY_ONLY",
         "large, expensive, reused 3x": "MEMORY_AND_DISK",
         "huge result, memory needed by tasks": "DISK_ONLY",
         "spot nodes, expensive to rebuild": "MEMORY_AND_DISK_2"}
for k, v in cases.items():
    print(f"{v:18} <- {k}")
'''),
        dict(label='5 · Spot the error', hint='This code caches a DataFrame that is used only once.', expect='error',
             code='''uses = {"orders_clean": 1}
for name, n in uses.items():
    assert n > 1, f"{name} is used {n} time(s): caching only adds cost"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: inspect caches',
    intro='<p>In the <code>pyspark</code> shell. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Storage level of a DataFrame', cmd="df = spark.read.parquet(\"orders_big\").where(\"status = 'DELIVERED'\").cache()\ndf.storageLevel", file='pyspark',
             output='StorageLevel(True, True, False, True, 1)   # Disk Memory Deserialized 1x Replicated', note='useDisk, useMemory, useOffHeap, deserialized, replication.'),
        dict(title='2 · Cached datasets through the REST API', cmd='curl -s http://localhost:4040/api/v1/applications/<app-id>/storage/rdd', file='terminal',
             output='[ { "id" : 6, "name" : "*(1) Filter (isnotnull(status#5) AND (status#5 = DELIVERED)) …",\n    "numPartitions" : 2, "numCachedPartitions" : 2,\n    "storageLevel" : "Disk Memory Deserialized 1x Replicated",\n    "memoryUsed" : 49771776, "diskUsed" : 0 } ]   (shortened)', note='memoryUsed 49,771,776 bytes = 47.5 MiB, as in the Storage tab.'),
        dict(title='3 · Is a table cached?', cmd='spark.sql("CACHE TABLE delivered AS SELECT * FROM parquet.`orders_big` WHERE status = \'DELIVERED\'")\nspark.catalog.isCached("delivered")', file='pyspark',
             output='True', note='CACHE TABLE runs at once; add LAZY to wait for the first query.'),
    ],
)

TRACE = dict(
    heading='How MEMORY_ONLY and MEMORY_AND_DISK handle a full memory',
    intro='<p>Follow what happens to partitions when memory runs out.</p>',
    code='''memory_mib, part_mib = 100, 30
partitions = ["p0", "p1", "p2", "p3", "p4"]
for level in ("MEMORY_ONLY", "MEMORY_AND_DISK"):
    used, mem, disk, missing = 0, [], [], []
    for p in partitions:
        if used + part_mib <= memory_mib:
            mem.append(p); used += part_mib
        elif level == "MEMORY_AND_DISK":
            disk.append(p)
        else:
            missing.append(p)
    print(level, "memory:", mem, "disk:", disk, "recompute:", missing)
''',
    notes={6: 'Fits :: Kept in memory.', 8: 'Spill :: MEMORY_AND_DISK writes the rest to local disk.', 10: 'Recompute :: MEMORY_ONLY simply does not cache it; later actions recompute it.'},
)

WORKED_INTRO = 'Three caching decisions from real jobs.'
EXAMPLES = [
    dict(level='b', tag='Performance · caching', title='Cache a reused base',
         problem='<p>Three reports use the same filtered orders. Cache it properly.</p>',
         inp='orders_big',
         approach=['Cache the filtered base.', 'Trigger it once.', 'Unpersist at the end.'],
         code='''print("""base = orders.where("status = 'DELIVERED'").cache()
base.count()                       # fill the cache
report_city(base); report_day(base); report_top(base)
base.unpersist()""")
''', notes={2: 'Fill :: Otherwise the first report pays for filling the cache.'},
         tryit='Check the Storage tab: 100% cached, 47.5 MiB.'),
    dict(level='i', tag='Reliability · memory', title='Fix an exit-code-52 job',
         problem='<p>A job caching a wide DataFrame kills executors with exit code 52.</p>',
         inp='4 partitions, 651 MiB cached, 1 GiB executors',
         approach=['Check partition sizes.', 'Repartition to more partitions or use DISK_ONLY.', 'Remove the cache if used once.'],
         code='''total_mib, parts, exec_heap_mib = 651, 4, 1024
per_part = total_mib / parts
print(f"{per_part:.0f} MiB per cached partition in a {exec_heap_mib} MiB executor")
print("fix: repartition(32) ->", round(total_mib / 32), "MiB each, or persist(DISK_ONLY)")
''', notes={3: 'Rule :: Keep partitions to tens or low hundreds of MB, well below executor memory.'},
         tryit='Our cluster ran fine with 32 partitions (Step 4).'),
    dict(level='a', tag='Architecture · reuse', title='Cache, checkpoint or write?',
         problem='<p>A cleaned dataset is used by two jobs on different days.</p>',
         inp='cleaned orders',
         approach=['Cache lives only in one application.', 'Checkpoint is for lineage, not sharing.', 'Write a table.'],
         code='''print("within one application, reused  -> cache()/persist()")
print("very long lineage, one app       -> checkpoint() (Lesson 3.3)")
print("used by other jobs or days       -> write Parquet/Delta/Iceberg table")
''', notes={1: 'Scope :: Cached data disappears when the application ends.'},
         tryit='Module 5 covers writing tables; Lesson 11.5 lakehouse tables.'),
]

QUIZ = mix([
    dict(q='Beginner: When is a cache filled?', options=['When cache() is called', 'At the first action that computes the data', 'At start-up', 'Never'], answer=1,
         why='0 cached entries until count().'),
    dict(q='Beginner: What is a DataFrame’s default storage level?', options=['MEMORY_ONLY', 'MEMORY_AND_DISK', 'DISK_ONLY', 'OFF_HEAP'], answer=1,
         why='Shown as Disk Memory Deserialized.'),
    dict(q='Beginner: How do you release a cached DataFrame?', options=['del df', 'df.unpersist()', 'df.cache(False)', 'restart Python'], answer=1,
         why='Or UNCACHE TABLE / clearCache().'),
    dict(q='Intermediate: How are PySpark RDDs cached by default?', options=['Deserialised in memory', 'Serialised in memory (MEMORY_ONLY)', 'On disk', 'Off-heap'], answer=1,
         why='Python objects are stored as bytes.'),
    dict(q='Intermediate: What does CACHE TABLE do differently from cache()?', options=['Nothing', 'It caches eagerly, immediately', 'It writes to disk only', 'It replicates'], answer=1,
         why='CACHE LAZY TABLE waits for a query.'),
    dict(q='Intermediate: Why was the first cached query slower than the uncached one?', options=['Bug', 'Building the cache costs extra time', 'Fewer partitions', 'Disk failure'], answer=1,
         why='21.5 s vs 15.3 s.'),
    dict(q='Advanced: What does executor exit code 52 indicate?', options=['Network error', 'OutOfMemoryError in the executor JVM', 'Python crash', 'Normal exit'], answer=1,
         why='Caching 4 huge partitions caused it.'),
    dict(q='Advanced: With MEMORY_ONLY, what happens to partitions that do not fit?', options=['Written to disk', 'Not cached; recomputed when needed', 'The job fails', 'Compressed'], answer=1,
         why='MEMORY_AND_DISK would spill them.'),
])

REVISION = [
    '<code>cache()</code> = <code>persist()</code> with the default level; both are <b>lazy</b> (filled by the first action).',
    'Defaults: DataFrame MEMORY_AND_DISK (compressed columnar; 4.75 M rows = 47.5 MiB); PySpark RDD MEMORY_ONLY serialised.',
    'Levels: MEMORY_ONLY (recompute if evicted), MEMORY_AND_DISK (spill), DISK_ONLY, <code>_2</code> (two replicas), OFF_HEAP.',
    'Lab (651 MiB, 32 partitions): 2nd query 6.7 s uncached vs 2.1–2.7 s cached; filling costs extra the first time.',
    'Storage tab: level, cached partitions, <b>fraction cached</b>, memory and disk sizes.',
    'Caching 4 huge partitions in 1 GiB executors → exit code 52 (OOM) → job aborted.',
    '<code>CACHE TABLE</code> is eager, <code>CACHE LAZY TABLE</code> is lazy; clean up with unpersist / UNCACHE / clearCache.',
]
FAQ = [
    ('Is cache() the same as persist()?', 'Yes, cache() is persist() with the default storage level. Use persist() when you want a different level, such as DISK_ONLY.'),
    ('Does caching survive the end of the application?', 'No. Cached blocks live in executors and disappear when the application stops or an executor is lost. To reuse data across jobs, write it to storage.'),
    ('Why is a cached DataFrame so much smaller than the raw data?', 'Spark caches DataFrames in a columnar format with compression per column, so repeated values (cities, statuses) take very little space. Random strings, like our hashes, do not compress.'),
    ('How much memory can caches use?', 'Executors share one unified region between execution and storage (spark.memory.fraction, 0.6 of the heap minus 300 MB by default). Caches can use most of it when tasks do not need it, and are evicted when tasks do (Lesson 8.4).'),
    ('Should I cache before a write?', 'Only if the same DataFrame is also used by another action. A single write does not benefit from caching.'),
]

PRACTICE_INTRO = 'Programs about cache sizes, levels and break-even points.'
PROBLEMS = [
    dict(level='easy', title='Speed-up', stmt='Speed-up of the second query from caching.', inp='6.7 s vs 2.2 s',
         code='''print(round(6.7 / 2.2, 1), "x")
''', explain='MEMORY_AND_DISK in Step 4.'),
    dict(level='easy', title='MiB from bytes', stmt='Convert memoryUsed to MiB.', inp="49,771,776 bytes",
         code='''print(round(49771776 / 2**20, 1), "MiB")
''', explain='The Storage tab shows the same 47.5 MiB.'),
    dict(level='easy', title='Fraction cached', stmt='Fraction of cached partitions.', inp='24 of 32',
         code='''print(f"{24 / 32:.0%}")
''', explain='Below 100% means some partitions are recomputed or read from disk.'),
    dict(level='medium', title='Break-even uses', stmt='Minimum uses for caching to win.', inp='6.7 s plain, 2.4 s cached, 6.2 s extra fill',
         code='''n = 1
while 6.7 * n <= 6.7 + 6.2 + 2.4 * (n - 1):
    n += 1
print(n, "uses")
''', explain='Below that, caching costs more than it saves.'),
    dict(level='medium', title='Partitions for a target size', stmt='Partitions so each cached block is about 20 MiB.', inp='651 MiB',
         code='''import math
print(math.ceil(651 / 20))
''', explain='repartition(33) or the nearest round number such as 32.'),
    dict(level='medium', title='Replicated cost', stmt='Memory needed for MEMORY_AND_DISK_2.', inp='651 MiB',
         code='''print(651 * 2, "MiB across the cluster")
''', explain='Two copies: twice the memory.'),
    dict(level='business', title='Daily savings', stmt='Cluster minutes saved per day with caching.', inp='40 reports × 4.5 s saved',
         code='''print(40 * 4.5 / 60, "minutes")
''', explain='Small per report, real at scale.'),
    dict(level='business', title='Cost of an OOM night', stmt='Rerun cost after a failed nightly job.', inp='3 h job fails at 2.5 h, rerun 3 h',
         code='''print(2.5 + 3, "hours of cluster time instead of 3")
''', explain='A wrong cache can almost double a night’s compute.'),
]

SCN_INTRO = 'Caching questions test practical judgement, not just API knowledge.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', 'cache vs persist',
        'What is the difference between cache() and persist()?',
        'do you know storage levels?',
        '<p>cache() is persist() with the default storage level: MEMORY_AND_DISK for DataFrames, MEMORY_ONLY for RDDs. persist() lets me choose MEMORY_ONLY, MEMORY_AND_DISK, DISK_ONLY, replicated _2 levels or OFF_HEAP. Both are lazy: the first action fills the cache. I release it with unpersist().</p>', 'Saying cache() writes to disk permanently.') +
    scn('Data engineering', 'Mid-level', 'When not to cache',
        'A colleague caches every DataFrame. Is that good?',
        'do you know the costs?',
        '''<ul>
          <li>Caching costs time to fill and memory that tasks need.</li>
          <li>Cache only data reused by several actions; unpersist after.</li>
          <li>For data used once, or cheap to reread from Parquet, caching makes jobs slower.</li>
        </ul>''', '“Caching is always good.”') +
    scn('Platform', 'Mid-level', 'Executors exit with code 52',
        'After adding cache(), executors die with exit code 52.',
        'can you diagnose memory problems?',
        '''<ol>
          <li>Exit code 52 = OutOfMemoryError in the executor JVM.</li>
          <li>Check cached size and partition sizes in the Storage/Stages tabs.</li>
          <li>Repartition to smaller partitions, use DISK_ONLY or MEMORY_AND_DISK, add executor memory, or drop the cache.</li>
        </ol>''', 'Only increasing executor memory without looking.') +
    scn('Architecture', 'Senior', 'Caching strategy for a shared cluster',
        'Many teams share a cluster; caches cause evictions and failures.',
        'can you set guidelines?',
        '''<ul>
          <li>Cache only reused datasets; unpersist in finally blocks; prefer writing intermediate tables for cross-job reuse.</li>
          <li>Size partitions sensibly; choose disk levels for large data; monitor fraction cached.</li>
          <li>Isolate interactive and batch workloads; set executor memory per workload.</li>
        </ul>''', 'Banning caching completely.')
)
