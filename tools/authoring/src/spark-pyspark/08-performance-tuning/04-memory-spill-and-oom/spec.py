import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='08-performance-tuning', lesson='04-memory-spill-and-oom', n='8.4',
    module_label='Module 8 · Performance tuning',
    title='Memory, spill and OOM',
    desc='Spark memory measured with PySpark 4.3.0: the unified memory model ((heap − 300 MB) × 0.6), the same sort of 5M wide rows at 3 GB (no spill) and 1 GB (736 MiB spilled, 91 MiB on disk), spill removed with 64 partitions, a real java.lang.OutOfMemoryError from collect_list per city, and three fixes that work at 1 GB, plus memoryOverhead and driver OOMs.',
    og_desc='Same Spark job at 3 GB and 1 GB: 736 MiB of spill, then a real OutOfMemoryError, and the fixes that worked without more memory.',
    minutes=30, level='Intermediate → Advanced',
    lead='Spill keeps a job alive; OOM kills it. This lesson explains Spark’s <b>unified memory model</b>, then shrinks memory on purpose to produce real spill and a real <code>OutOfMemoryError</code>, and fixes both without adding memory. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', 'Spill measured', 'Real OOM', 'Runs in your browser (Python)'],
)

MAIN = '''# Spark executor memory layout (unified memory model)
heap_mb = 8 * 1024            # spark.executor.memory = 8g
fraction = 0.6                # spark.memory.fraction
storage_fraction = 0.5        # spark.memory.storageFraction
cores = 4                     # spark.executor.cores

usable = heap_mb - 300
unified = usable * fraction
print("user memory      :", round(usable * (1 - fraction)), "MB")
print("unified          :", round(unified), "MB")
print("protected storage:", round(unified * storage_fraction), "MB")
print("execution / task :", round(unified / cores), "MB (if no cache)")
print("overhead         :", max(384, round(heap_mb * 0.10)), "MB off-heap")
'''
RUN = dict(
    heading='Run the code: executor memory layout',
    intro='<p>Compute how an executor heap is divided. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('unified = usable * fraction', 'Shared by execution (sort, join, aggregation) and storage (cache, broadcast).'),
        ('print("execution / task :", round(unified / cores), "MB (if no cache)")', 'Concurrent tasks share execution memory; each gets between 1/(2N) and 1/N of it.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then try 1 GB heap with 2 cores, like the lab.', code=None),
        dict(label='2 · Predict first: spill', hint='<b>Predict first:</b> a task must sort 900 MB with 434 MB of unified memory for 2 tasks.',
             code='''unified, tasks, need = 434, 2, 900
per_task = unified / tasks        # each running task gets about 1/N
print(round(per_task), "MB available ->", "spill" if need > per_task else "fits")
'''),
        dict(label='3 · More partitions', hint='Split the sort into 16x more partitions.',
             code='''need_mb, parts_before, parts_after = 900, 4, 64
print(need_mb * parts_before / parts_after, "MB per task")
'''),
        dict(label='4 · Overhead for Python', hint='Default overhead for a 16 GB executor.',
             code='''print(max(384, 16 * 1024 * 0.10), "MB")
'''),
        dict(label='5 · Spot the error', hint='One group must hold a 1.2 GB list in a 1 GB executor.', expect='error',
             code='''group_mb, unified_mb = 1200, 434
assert group_mb < unified_mb, "a single group cannot spill: java.lang.OutOfMemoryError: Java heap space"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: memory',
    intro='<p>Start with <code>pyspark --driver-memory 1g</code>. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Heap size', cmd='sc._jvm.java.lang.Runtime.getRuntime().maxMemory() // 2**20', file='pyspark',
             output='1024', note='Unified ≈ (1024 − 300) × 0.6.'),
        dict(title='2 · Spill', cmd='wide.orderBy("amount").write.format("noop").mode("overwrite").save()\n# Spark UI → Stages → Spill (Memory) / Spill (Disk)', file='pyspark',
             output='Spill (Memory): 736.0 MiB   Spill (Disk): 91.4 MiB', note='Disk is compressed.'),
        dict(title='3 · OOM', cmd='wide.groupBy("city").agg(F.collect_list("pad")).write.format("noop").mode("overwrite").save()', file='pyspark',
             output='java.lang.OutOfMemoryError: Java heap space', note='The JVM dies; restart the shell.'),
    ],
)

TRACE = dict(
    heading='An external sort in miniature',
    intro='<p>Sort with a memory limit of 3 values: sort runs, spill them, merge.</p>',
    code='''import heapq
data = [9, 2, 7, 4, 8, 1, 6]
limit = 3
runs = []
for i in range(0, len(data), limit):
    runs.append(sorted(data[i:i + limit]))
print(runs)
print(list(heapq.merge(*runs)))
''',
    notes={3: 'Memory :: Only 3 values fit at once.', 6: 'Spill :: Each sorted run goes to disk.', 8: 'Merge :: Read runs back in order.'},
)

WORKED_INTRO = 'Three memory problems at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='Memory · spill', title='Is this spill a problem?',
         problem='<p>A stage shuffles 20 GB and spills 2 GB.</p>',
         inp='spill vs shuffle',
         approach=['Compare spill with shuffle read.', 'Small ratio: fine.', 'Large ratio: more partitions.'],
         code='''print(round(2 / 20, 2), "-> acceptable" if 2 / 20 < 0.5 else "-> tune")
''', notes={1: 'Ratio :: A little spill is normal.'},
         tryit='Step 2.'),
    dict(level='i', tag='Memory · partitions', title='Partitions to stop spilling',
         problem='<p>Each task sorts 1.5 GB; execution memory per task is ~400 MB.</p>',
         inp='1.5 GB per task',
         approach=['Need tasks ≤ ~300 MB.', 'Multiply partitions.', 'Or rely on AQE advisory size.'],
         code='''import math
print("x", math.ceil(1500 / 300), "more partitions")
''', notes={1: 'Headroom :: Leave room for overhead.'},
         tryit='Step 2, 64 partitions.'),
    dict(level='a', tag='Memory · OOM', title='Find the unspillable object',
         problem='<p>A job OOMs in one task of a groupBy.</p>',
         inp='stack trace + task metrics',
         approach=['Which aggregation? collect_list / collect_set?', 'Is one key huge?', 'Replace with aggregates or partitioned writes.'],
         code='''aggs = ["sum", "collect_list", "count"]
print([a for a in aggs if a.startswith("collect")])
''', notes={1: 'Suspects :: Lists and sets grow with group size.'},
         tryit='Step 3.'),
]

QUIZ = mix([
    dict(q='Beginner: Spill means…', options=['Data lost', 'Data written to local disk to continue', 'Job failed', 'Cache cleared'], answer=1,
         why='Slow but safe.'),
    dict(q='Beginner: Default spark.memory.fraction?', options=['0.2', '0.6', '0.75', '1.0'], answer=1,
         why='Of heap minus 300 MB.'),
    dict(q='Beginner: Execution memory is used by…', options=['cache()', 'Sorts, joins, aggregations', 'Python only', 'Logs'], answer=1,
         why='Storage is for cache/broadcast.'),
    dict(q='Intermediate: Why is Spill (Memory) bigger than Spill (Disk)?', options=['Bug', 'Disk spill is serialized and compressed', 'Lost data', 'Cache'], answer=1,
         why='736 vs 91 MiB.'),
    dict(q='Intermediate: Lab fix that removed spill at 1 GB?', options=['cache()', '64 partitions instead of 4', 'collect()', 'broadcast'], answer=1,
         why='Smaller tasks.'),
    dict(q='Intermediate: Why did collect_list per city OOM?', options=['Too many partitions', 'Each city list must be one in-memory object', 'Disk full', 'Python error'], answer=1,
         why='Groups cannot spill.'),
    dict(q='Advanced: “Container killed for exceeding memory limits” with Pandas UDFs. Raise…', options=['spark.executor.memory', 'spark.executor.memoryOverhead', 'shuffle partitions', 'maxResultSize'], answer=1,
         why='Python is off-heap.'),
    dict(q='Advanced: Driver OOM during a join usually means…', options=['Skew', 'A large broadcast', 'Too many partitions', 'Spill'], answer=1,
         why='Broadcast sides are collected on the driver.'),
])

REVISION = [
    'Heap: 300 MB reserved, user (40%), unified (60%) = execution + storage.',
    'Spill: execution memory full → sorted runs on disk; slow, not fatal.',
    'Lab: 1 GB sort spilled 736 MiB (91 MiB disk); 64 partitions removed it.',
    'OOM: an unspillable object (huge group, broadcast, collect) does not fit.',
    'collect_list per city OOMed at 1 GB; per customer and window top-5 worked.',
    'Python/Arrow memory is off-heap: <code>spark.executor.memoryOverhead</code>.',
    'Fix the big thing first; then size memory. Avoid huge heaps (GC).',
]
FAQ = [
    ('How much executor memory should I give?', 'Common shapes are 4–5 cores with 16–32 GB per executor, then tune from spill and GC time in the UI.'),
    ('Is spill always bad?', 'No. Some spill is normal for big sorts; worry when spill is many times the shuffle size or the stage is dominated by it.'),
    ('What is GC time in the UI?', 'Time the JVM spent in garbage collection; above ~10% of task time suggests memory pressure or too many objects.'),
    ('Does caching cause OOM?', 'Rarely; cached blocks are evicted or stored on disk depending on the storage level, but they reduce memory for execution.'),
    ('Why does the driver need memory?', 'It holds plans, broadcast tables while building them, collected results and accumulators; keep heavy data off it.'),
]

PRACTICE_INTRO = 'Programs about memory and spill.'
PROBLEMS = [
    dict(level='easy', title='Unified memory', stmt='Unified memory for a 4 GB heap.', inp='4096 MB',
         code='''print((4096 - 300) * 0.6)
''', explain='About 2.2 GB.'),
    dict(level='easy', title='Spill ratio', stmt='Memory ÷ disk spill.', inp='736 vs 91.4 MiB',
         code='''print(round(736 / 91.4, 1))
''', explain='Compression and serialization.'),
    dict(level='easy', title='Overhead', stmt='Default overhead for a 2 GB executor.', inp='2048 MB',
         code='''print(max(384, 2048 * 0.1))
''', explain='Minimum 384 MB.'),
    dict(level='medium', title='Per-task memory', stmt='Execution memory per task.', inp='16 GB heap, 5 cores',
         code='''print(round((16 * 1024 - 300) * 0.6 / 5), "MB")
''', explain='Upper bound with no cache.'),
    dict(level='medium', title='Partitions needed', stmt='Partitions so each task sorts ≤ 256 MB.', inp='40 GB shuffle',
         code='''import math
print(math.ceil(40 * 1024 / 256))
''', explain='160 partitions.'),
    dict(level='medium', title='External sort', stmt='Number of spill runs.', inp='3 GB with 400 MB memory',
         code='''import math
print(math.ceil(3000 / 400))
''', explain='8 runs merged.'),
    dict(level='business', title='Memory cost', stmt='Extra GB-hours from doubling memory on 50 executors for 2 h daily.', inp='+8 GB each',
         code='''print(50 * 8 * 2, "GB-hours per day")
''', explain='Fix the cause instead.'),
    dict(level='business', title='Retry cost', stmt='Wasted minutes from 4 failed OOM attempts of 25 min.', inp='4 × 25',
         code='''print(4 * 25, "minutes")
''', explain='Fail fast, fix the group.'),
]

SCN_INTRO = 'Memory questions test whether you understand what really runs out.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“What is spill?”',
        'Explain spill in Spark.',
        'is it an error?',
        '<p>When a sort, join or aggregation runs out of execution memory, Spark writes sorted chunks to local disk and merges them later. The job continues, slower. It appears as Spill (Memory) and Spill (Disk) in the stage page.</p>', 'Calling spill a failure.') +
    scn('Data engineering', 'Mid-level', 'Heavy spill',
        'A stage spills 50 GB for a 10 GB shuffle.',
        'what to do?',
        '''<ul>
          <li>Increase shuffle partitions or the AQE advisory size so tasks are smaller.</li>
          <li>Check for skew (one task spilling most).</li>
          <li>Then consider executor memory or fewer cores per executor.</li>
        </ul>''', 'Only adding memory.') +
    scn('Data engineering', 'Mid-level', 'Executor OOM',
        'One task fails with Java heap space.',
        'diagnose?',
        '''<ol>
          <li>Find the operation: collect_list, big row, broadcast, UDF state.</li>
          <li>Check task metrics for skew.</li>
          <li>Replace giant groups; salt; write partitioned output.</li>
        </ol>''', 'Retrying with the same config.') +
    scn('Platform', 'Senior', 'Executor shape',
        'Choose executor size for 64-core, 256 GB nodes.',
        'reasoning?',
        '''<ul>
          <li>~5 cores per executor → 12 executors per node (leave OS/daemon cores).</li>
          <li>~18 GB heap + overhead each, leaving node headroom.</li>
          <li>Validate with spill, GC time and container kills.</li>
        </ul>''', 'One giant executor per node.')
)
