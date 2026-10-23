import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()

TX = rd('tx114.txt')
TX_123 = TX[:TX.index('== 4.')].strip()
TX_4 = TX[TX.index('== 4.'):].strip()
TUNE = rd('lab/tuning_lab.sh')
TUNE_123 = TUNE[:TUNE.index('echo "== 4.')].rstrip() + '\n'

META = dict(
    module='11-yarn', lesson='04-memory-and-cpu-tuning', n='11.4',
    module_label='Module 11 · YARN',
    title='Memory and CPU tuning',
    desc='YARN memory and CPU tuning measured on a real Hadoop 3.5.0 cluster: requests rounded up to the minimum allocation (300 → 512, 600 → 768, 1100 → 1280 MB), 12 containers of 512 MB vs 6 of 1024 MB, the DefaultResourceCalculator handing out 12 vcores on 6, the DominantResourceCalculator limiting by CPU, a real ResourceManager crash from a partial capacity-scheduler.xml, and a map task failing with “Java heap space” at -Xmx64m but succeeding at 300 MB. The memory stack, key properties, sizing a 128 GB worker, Spark executor overhead, Python calculators, quiz and interview scenarios.',
    og_desc='Ask YARN for 384 MB and get 512. Watch 12 containers become 6, CPU get ignored, and a 64 MB heap kill a job on a real cluster.',
    minutes=30, level='Intermediate',
    lead='YARN hands out memory and CPU in containers of fixed steps, and inside each container a JVM has its own, smaller heap. This lesson measures both on our three-worker cluster: how requests are rounded, how many containers fit, when CPU counts, and how a heap that is too small fails a job. Then it sizes a real production server with the same rules.',
    chips=['Rounding and packing measured', 'Real heap failure and fix', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='A container sizing calculator',
    intro='<p>This reproduces our lab: round each request up to the minimum allocation, then pack containers onto nodes by memory only (DefaultResourceCalculator) or by memory and CPU (DominantResourceCalculator). The AM goes first, as in YARN.</p>',
    code='''import math
MIN_MB = 256
NODES = [{"mb": 2048, "vc": 2} for _ in range(3)]

def normalize(mb):
    return math.ceil(mb / MIN_MB) * MIN_MB          # always rounded UP

def pack(map_mb, n_maps, am_mb=512, use_cpu=False):
    free = [dict(n) for n in NODES]
    asks = [normalize(am_mb)] + [normalize(map_mb)] * n_maps
    placed = 0
    for ask in asks:
        for n in free:
            if n["mb"] >= ask and (not use_cpu or n["vc"] >= 1):
                n["mb"] -= ask
                n["vc"] -= 1
                placed += 1
                break
    used = sum(2048 - n["mb"] for n in free)
    return placed, used

for mb in [300, 384, 600, 1100]:
    print(f"map asks {mb:4} MB -> granted {normalize(mb)} MB")
print("384 MB maps, memory only:", pack(384, 24))
print("1024 MB maps, memory only:", pack(1024, 24))
print("384 MB maps, DRF (CPU too):", pack(384, 24, use_cpu=True))
''',
    anno=[
        ('    return math.ceil(mb / MIN_MB) * MIN_MB          # always rounded UP', 'yarn.scheduler.minimum-allocation-mb is a step size: 300 and 384 both become 512.'),
        ('            if n["mb"] >= ask and (not use_cpu or n["vc"] >= 1):', 'The DefaultResourceCalculator only checks memory; the DominantResourceCalculator also needs a free vcore.'),
        ('print("384 MB maps, DRF (CPU too):", pack(384, 24, use_cpu=True))', 'Lab: 6 containers and 3072 MB under DRF, against 12 containers and 6144 MB with memory only.'),
    ],
    tasks=[
        dict(label='1 · Rounding and packing', hint='Press <b>Run</b>. Compare with the lab: 512/512/768/1280, then (12, 6144), (6, 5632) and (6, 3072).', code=None),
        dict(label='2 · Production minimum', hint='<b>Predict first:</b> with the common production minimum of 1024 MB, what do 300, 384, 600 and 1100 become?',
             code='''import math
for mb in [300, 384, 600, 1100]:
    print(mb, "->", math.ceil(mb / 1024) * 1024)
'''),
        dict(label='3 · Waves', hint='How many waves do 24 maps need when 11 or when 5 run at once (the AM takes one container)? Each wave of sleep maps took 30 s.',
             code='''import math
for at_once in [11, 5]:
    w = math.ceil(24 / at_once)
    print(f"{at_once} maps at once -> {w} waves, about {w * 30} s of map time")
'''),
        dict(label='4 · Heap per line', hint='HeapHog kept 2,147,952 lines in 222 MB of heap. Estimate the bytes per line and the heap needed for a 128 MB split of the same data.',
             code='''lines, used_mb = 2_147_952, 222
per_line = used_mb * 1024 * 1024 / lines
lines_128 = lines * 4                                  # a 128 MB split holds about 4x a 32 MB split
print(f"about {per_line:.0f} bytes per line; a 128 MB split needs ~{lines_128 * per_line / 1024**2:.0f} MB of heap")
'''),
        dict(label='5 · Spot the error', hint='This check is meant to reject a heap that does not fit in the container, but it divides the wrong way round and crashes on a zero. Fix it so it prints the heap as a percentage of the container.',
             code='''container_mb, heap_mb = 512, 0
print("heap is", container_mb / heap_mb * 100, "% of the container")
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: containers, CPU and heap',
    intro='<p>This uses the Module 8 lab (<code>mr-lab</code> folder). <code>rm.sh</code> (from Lesson 11.3) recreates only the ResourceManager with another configuration; HDFS and the NodeManagers keep running. Parts 1–3 use Hadoop\'s built-in sleep job from the MapReduce tests jar. Each part runs for a minute or two, so the whole script takes about 10 minutes.</p>',
    items=[
        dict(title='Rounding, packing and the CPU calculator', file='tuning_lab.sh',
             cmd=TUNE_123 + '\n# rm.sh (same folder) switches the ResourceManager configuration:\n' + '\n'.join('# ' + l for l in rd('lab/rm.sh').strip().split('\n')) + '\n\n# Run, in the mr-lab folder:\n#   bash tuning_lab.sh',
             output=TX_123,
             note='Real output. The vcore metric adds allocated and available vcores, so with the memory-only calculator it reports “of 12” although the three nodes offer 6.'),
        dict(title='DominantResourceCalculator: the configuration that works', file='sched-drf.env',
             cmd=rd('lab/sched-drf.env').strip() + '\n\n# Our first version had only the last line. The ResourceManager did not start:\n#   docker logs lab8-resourcemanager-1 | grep "missing child queue"',
             output=rd('lab/drf_crash.txt').strip(),
             note='Real log line from the failed first attempt. Setting any CAPACITY-SCHEDULER.XML_ key makes the apache/hadoop image write capacity-scheduler.xml with only those keys, so the queue list must be repeated.'),
        dict(title='A map that keeps every line in memory', file='HeapHog.java',
             cmd=rd('lab/java/HeapHog.java') + '\n// In the mr-lab folder:\n//   docker exec lab8-namenode-1 mkdir -p /tmp/mr11\n//   docker cp HeapHog.java lab8-namenode-1:/tmp/mr11/\n//   docker exec lab8-namenode-1 bash -c "cd /tmp/mr11 && mkdir -p c && javac -cp \\$(hadoop classpath) -d c HeapHog.java && jar cf mr11.jar -C c ."\n// Then run hog.sh below.',
             output=TX_4,
             note='Real output of hog.sh. With 64 MB of heap only the small last split (415,675 lines) survived; every 32 MB split failed 4 times and the job failed. The “7” counts distinct error lines the client printed, not attempts.'),
        dict(title='The heap experiment script', file='hog.sh',
             cmd=rd('lab/hog.sh') + '\n# Run, in the mr-lab folder:  bash hog.sh',
             output=TX_4,
             note='Real output (same run as above). orders_x30.csv is the 140 MB file from Lesson 8.1.'),
    ],
)

TRACE = dict(
    heading='Normalizing three requests',
    intro='<p>Watch each request being rounded up to the next multiple of the minimum allocation.</p>',
    code='''MIN = 256
requests = [300, 600, 1100]
granted = []
for ask in requests:
    steps = -(-ask // MIN)
    granted.append(steps * MIN)
print(granted)
''',
    notes={5: 'Ceiling :: -(-a // b) is integer ceiling division: 300 needs 2 steps of 256.',
           6: 'Granted :: The scheduler grants whole steps only.'},
)

WORKED_INTRO = 'Four sizing problems from different industries, each solved with the same memory-stack rules.'
EXAMPLES = [
    dict(level='b', tag='Banking · capacity', title='How many containers does a bank\'s worker give?',
         problem='<p>A bank\'s Hadoop worker has 128 GB RAM and 32 cores. Reserve 16 GB for the OS, the DataNode and the NodeManager. Map containers are 4 GB with 1 vcore. How many maps run at once per node, and on a 25-node cluster?</p>',
         inp='128 GB − 16 GB · 4 GB maps · 32 cores (keep 2)',
         approach=['YARN memory = RAM − reserve.',
                   'By memory: pool ÷ container size.',
                   'By CPU: usable vcores. The smaller number wins (with DRF).'],
         code='''pool_gb = 128 - 16
by_mem = pool_gb // 4
by_cpu = 32 - 2
per_node = min(by_mem, by_cpu)
print(f"by memory {by_mem}, by CPU {by_cpu} -> {per_node} per node, {per_node * 25} on 25 nodes")
''', notes={4: 'Limit :: With DRF the tighter resource decides; with the memory-only calculator only by_mem counts.'},
         tryit='Change maps to 3 GB. Memory now allows 37, so CPU (30) becomes the limit: a sign the cluster is CPU-bound.'),
    dict(level='i', tag='Telecom · rounding', title='What does a 3000 MB request really cost?',
         problem='<p>A telecom job asks for 3000 MB maps on a cluster whose minimum allocation is 1024 MB and whose NodeManagers offer 96 GB. How much memory does each map really hold, and how much is wasted per node compared with asking for exactly 3072 MB?</p>',
         inp='ask 3000 · min 1024 · 96 GB pool',
         approach=['Round up to a multiple of 1024.',
                   'Containers per node = pool ÷ granted.',
                   'Waste = granted − asked, per container.'],
         code='''import math
ask, step, pool = 3000, 1024, 96 * 1024
granted = math.ceil(ask / step) * step
per_node = pool // granted
print(f"granted {granted} MB, {per_node} per node, {(granted - ask) * per_node} MB per node granted but never asked for")
''', notes={3: 'Rounding :: 3000 needs 3 steps of 1024: 3072.'},
         tryit='Ask for 2049 MB instead. It costs 3072 too: just above a step boundary is the worst place to be.'),
    dict(level='i', tag='E-commerce · Spark', title='Sizing Spark executors on YARN',
         problem='<p>A sale-day Spark job uses executors with <code>spark.executor.memory=8g</code>. Overhead is 10% of that, at least 384 MB. The YARN minimum allocation is 1024 MB, and nodes offer 112 GB. What container does each executor get, and how many fit per node?</p>',
         inp='8 GB heap + max(384 MB, 10%) · step 1024 · 112 GB',
         approach=['Overhead = max(384, 0.10 × 8192).',
                   'Request = heap + overhead, rounded up to 1024.',
                   'Executors per node = pool ÷ container.'],
         code='''import math
heap = 8192
overhead = max(384, int(0.10 * heap))
container = math.ceil((heap + overhead) / 1024) * 1024
print(f"overhead {overhead} MB -> container {container} MB, {112 * 1024 // container} executors per node")
''', notes={3: 'Overhead :: Off-heap memory Spark needs beside the JVM heap; YARN must hold room for it.'},
         tryit='Set the executor to 7.5g (7680 MB). The container drops to 9216 MB? Check: 7680 + 768 = 8448 → 9216. Same container: the rounding hides the saving.'),
    dict(level='a', tag='Healthcare · DRF', title='Which resource limits a hospital cluster?',
         problem='<p>A hospital\'s 10-node cluster offers 64 GB and 16 vcores per node to YARN. Job A (image features) uses containers of 2 GB / 2 vcores; job B (record joins) uses 8 GB / 1 vcore. With the DominantResourceCalculator, what is each container\'s dominant share of one node, and how many of each fit on an empty node?</p>',
         inp='node 64 GB / 16 vcores · A 2 GB/2 · B 8 GB/1',
         approach=['Share of memory and share of CPU per container.',
                   'Dominant share = the larger of the two.',
                   'Fit = min(memory fit, CPU fit).'],
         code='''node_gb, node_vc = 64, 16
for name, gb, vc in [("A", 2, 2), ("B", 8, 1)]:
    mem_share, cpu_share = gb / node_gb, vc / node_vc
    dominant = "CPU" if cpu_share > mem_share else "memory"
    fit = min(node_gb // gb, node_vc // vc)
    print(f"{name}: memory {mem_share:.1%}, CPU {cpu_share:.1%} -> dominant {dominant}, {fit} per node")
''', notes={4: 'Dominant :: DRF compares users and queues on this larger share.'},
         tryit='Under the memory-only calculator job A would fit 32 per node and need 64 vcores on a 16-vcore machine: CPU oversubscribed 4×.'),
]

QUIZ = mix([
    dict(q='A map asks for 600 MB on our cluster (minimum allocation 256 MB). What does it get?', options=['600 MB', '768 MB', '512 MB', '1024 MB'], answer=1,
         why='Requests are rounded up to a multiple of the minimum allocation: real output “map asks 600 MB -> … map 768 MB”.'),
    dict(q='Why did only 6 containers run with 1024 MB maps, using 5632 of 6144 MB?', options=['A bug in YARN', 'The 512 MB AM and one 1024 MB map left 512 MB on one node that no map could use', 'Maps need 2 vcores', 'HDFS was full'], answer=1,
         why='Fragmentation: 2048 − 512 − 1024 = 512 MB, too small for another 1024 MB map.'),
    dict(q='With the DefaultResourceCalculator, 12 one-vcore containers ran on nodes that offer 6 vcores in total. Why?', options=['vcores are doubled automatically', 'It compares memory only, so CPU is not checked when placing containers', 'The sleep job uses no CPU', 'YARN counts hyper-threads'], answer=1,
         why='Use the DominantResourceCalculator (or cgroups) to make CPU count.'),
    dict(q='What changed when we switched to the DominantResourceCalculator?', options=['Nothing', 'Only 6 containers ran and half the memory stayed free: CPU became the limit', 'Containers became bigger', 'Maps ran faster'], answer=1,
         why='Each container took 50% of a node\'s CPU but only 25% of its memory.'),
    dict(q='A map fails with “Error: Java heap space”. What is too small?', options=['The NodeManager pool', 'The JVM heap (-Xmx) inside the container', 'The HDFS block', 'The minimum allocation'], answer=1,
         why='HeapHog failed at -Xmx64m and succeeded at -Xmx300m in the same 512 MB container.'),
    dict(q='Which relation must always hold?', options=['heap > container', 'heap < container ≤ NodeManager pool', 'container > NodeManager pool', 'heap = container'], answer=1,
         why='The heap needs room for off-heap memory inside the container; the container must fit on a node.'),
    dict(q='Our ResourceManager refused to start after we set only the resource-calculator key. Why?', options=['DRF is not supported', 'The image wrote a capacity-scheduler.xml containing no queues', 'The NodeManagers were down', 'Port 8088 was busy'], answer=1,
         why='“Queue configuration missing child queue names for root”: we had to repeat root.queues=default.'),
    dict(q='In production, a container is killed with “is running beyond physical memory limits”. What is the usual fix?', options=['Lower the minimum allocation', 'Raise mapreduce.map.memory.mb, or lower -Xmx so heap + off-heap fit', 'Add more DataNodes', 'Disable speculative execution'], answer=1,
         why='The process (heap plus off-heap) grew past its container. Not reproduced in our lab, where memory checks are off.'),
])

REVISION = [
    'Stack: physical RAM → reserve for OS/daemons → <code>yarn.nodemanager.resource.memory-mb</code> → containers → JVM heap (<code>-Xmx</code> ≈ 80%) + off-heap.',
    'Requests round UP to <code>yarn.scheduler.minimum-allocation-mb</code>: lab 300/384 → 512, 600 → 768, 1100 → 1280 MB.',
    'Packing: 384 MB maps → 12 containers (6144 MB); 1024 MB maps → 6 (5632 MB, 512 MB stranded).',
    'DefaultResourceCalculator = memory only (12 vcores handed out on 6); DominantResourceCalculator = memory + CPU (6 containers).',
    '“Java heap space” → raise -Xmx (and the container) or stop collecting data in memory; “beyond physical memory” → bigger container or smaller heap.',
    'Setting any CAPACITY-SCHEDULER.XML_ key in the apache/hadoop image rewrites the whole file: repeat the queues.',
    'Spark on YARN: container = executor memory + overhead (max 384 MB, 10%), rounded up.',
]
FAQ = [
    ('How do you calculate the number of containers per node in YARN?', 'Take the memory the NodeManager offers (yarn.nodemanager.resource.memory-mb) and divide by the container size after rounding it up to a multiple of yarn.scheduler.minimum-allocation-mb. If the DominantResourceCalculator is used, also divide the node\'s vcores by the vcores per container and take the smaller number. Remember the ApplicationMaster also occupies a container.'),
    ('What is the difference between mapreduce.map.memory.mb and mapreduce.map.java.opts?', 'mapreduce.map.memory.mb is the size of the YARN container for a map task: what YARN reserves and enforces. mapreduce.map.java.opts sets JVM options such as -Xmx, the maximum heap inside that container. The heap must be smaller than the container, typically about 80% of it, to leave room for off-heap memory.'),
    ('What is the DominantResourceCalculator in YARN?', 'A resource calculator for the Capacity Scheduler that considers both memory and CPU. Each request is compared on its dominant share, the larger of its memory and CPU fractions, following Dominant Resource Fairness. The default DefaultResourceCalculator compares memory only, so CPU can be oversubscribed.'),
    ('Why does YARN give a container more memory than requested?', 'The scheduler normalizes every request up to a multiple of yarn.scheduler.minimum-allocation-mb (and a similar increment for the Fair Scheduler). In our lab, with a 256 MB minimum, a 384 MB request became 512 MB and 600 MB became 768 MB.'),
    ('How do you fix “Container is running beyond physical memory limits”?', 'The task process (heap plus off-heap) used more memory than its container. Either increase the container size (mapreduce.map.memory.mb or mapreduce.reduce.memory.mb) while keeping the heap around 80% of it, or reduce the heap or off-heap use (smaller buffers, less data held in memory). For Spark, raise spark.executor.memoryOverhead.'),
]

PRACTICE_INTRO = 'Sizing and tuning exercises using the real numbers from our lab.'
PROBLEMS = [
    dict(level='easy', title='Round it', stmt='Round 384, 513 and 1025 MB up to multiples of 256 MB.', inp='three requests',
         code='''import math
print([math.ceil(x / 256) * 256 for x in (384, 513, 1025)])
''', explain='[512, 768, 1280]: one MB over a boundary costs a whole extra step.'),
    dict(level='easy', title='Lab cluster total', stmt='Three NodeManagers offer 2048 MB each. How many 512 MB containers fit, and how many maps run once the 512 MB AM is placed?', inp='3 × 2048 MB',
         code='''total = 3 * 2048 // 512
print(total, "containers,", total - 1, "maps at once")
''', explain='12 containers, 11 maps: exactly what the lab measured (running containers 12).'),
    dict(level='easy', title='Heap ratio', stmt='Our maps asked for 384 MB with -Xmx300m but were granted 512 MB. What fraction of the request and of the grant is the heap?', inp='300 / 384 · 300 / 512',
         code='''print(f"{300 / 384:.0%} of the request, {300 / 512:.0%} of the grant")
''', explain='78% of what we asked, 59% of what we got: rounding left extra off-heap room.'),
    dict(level='medium', title='Stranded memory', stmt='Each node has 2048 MB. With a 512 MB AM on one node and 1024 MB maps, how much memory can no map use?', inp='AM 512 · maps 1024',
         code='''node = 2048
left_on_am_node = node - 512 - (node - 512) // 1024 * 1024
print(left_on_am_node, "MB stranded")
''', explain='512 MB, which is why the lab used 5632 of 6144 MB.'),
    dict(level='medium', title='Pick a container size', stmt='A worker offers 96 GB to YARN. Compare 2, 3, 4 and 6 GB maps: maps per node and leftover memory.', inp='96 GB pool',
         code='''pool = 96 * 1024
for gb in (2, 3, 4, 6):
    c = gb * 1024
    print(f"{gb} GB maps: {pool // c:2d} per node, {pool % c} MB left")
''', explain='All divide evenly here; on a 100 GB pool 3 GB would strand 1 GB. Choose sizes that divide the pool.'),
    dict(level='medium', title='Heap for a lookup table', stmt='A map loads a lookup of 12 lakh entries at about 250 bytes each, plus 200 MB for the framework and buffers. What heap and what container (heap = 80%, step 1024 MB)?', inp='12 lakh × 250 B + 200 MB',
         code='''import math
heap = 1_200_000 * 250 / 1024**2 + 200
container = math.ceil(heap / 0.8 / 1024) * 1024
print(f"heap {heap:.0f} MB -> container {container} MB")
''', explain='About 486 MB of heap, so a 1024 MB container. Measure first; object overhead often doubles estimates.'),
    dict(level='business', title='Bigger containers or more nodes?', stmt='A nightly job fails with heap errors at 2 GB maps. Option A: 4 GB maps (half as many at once, job 3 h instead of 2 h). Option B: add 10 nodes at ₹40,000 each per month to keep 2 h. Which is cheaper for a job that has a 4-hour window?', inp='3 h vs 2 h · 10 × ₹40,000',
         code='''window_h, a_hours = 4, 3
print("A fits the window:", a_hours <= window_h, "| B costs Rs", 10 * 40000, "per month")
''', explain='A fits the 4-hour window at no extra cost (illustrative numbers); B only makes sense if the window shrinks or other jobs need the capacity.'),
    dict(level='advanced', title='DRF on our lab', stmt='Simulate DRF packing on our 3 nodes (2048 MB, 2 vcores) for an AM of 512 MB/1 vcore and 24 maps of 384 MB/1 vcore (rounded to 512). How many containers and how much memory are used?', inp='3 nodes · 1 AM + 24 maps',
         code='''nodes = [[2048, 2] for _ in range(3)]
placed = used = 0
for mb in [512] + [512] * 24:
    for n in nodes:
        if n[0] >= mb and n[1] >= 1:
            n[0] -= mb; n[1] -= 1; placed += 1; used += mb
            break
print(placed, "containers,", used, "MB")
''', explain='6 containers, 3072 MB: exactly the lab\'s “running containers 6 | memory 3072 of 6144 MB”.'),
]

SCN_INTRO = 'Memory and CPU sizing questions come up in every Hadoop and Spark platform interview, usually with a failure story attached.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">YARN · basics</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“What is the difference between container memory and heap memory?”</h4>
      <p class="scn__situation">A standard opening question for YARN.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> the two limits and how they relate.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Container memory (mapreduce.map.memory.mb) is what YARN reserves on a node and can enforce.</li>
          <li>Heap (-Xmx in mapreduce.map.java.opts) is the JVM\\'s object space inside that container, about 80% of it.</li>
          <li>Heap too small → OutOfMemoryError; heap plus off-heap too big → the NodeManager kills the container.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Operations · failures</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Jobs fail with “Java heap space” after a data volume increase</h4>
      <p class="scn__situation">Nothing changed in the code; input doubled after a new region was added.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> diagnosis before throwing memory at it.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Find which tasks fail (map or reduce) and why: a reducer with a hot key, or code that collects values into a list.</li>
          <li>Fix the code if it buffers data; reduce split size or add reducers to spread load.</li>
          <li>If memory is really needed, raise the container and the heap together, keeping the 80% ratio.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Capacity · design</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Size YARN for a new 40-node cluster of 256 GB / 48-core machines</h4>
      <p class="scn__situation">Each node also runs a DataNode and an HBase RegionServer with a 32 GB heap.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> reserves, steps and CPU.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Reserve OS (~8 GB), DataNode (~4 GB), NodeManager (~2 GB) and RegionServer (32 GB + overhead): about 200 GB for YARN.</li>
          <li>Pick a minimum allocation (e.g. 2 GB) and standard container sizes that divide the pool; keep 2–4 cores for daemons.</li>
          <li>Use the DominantResourceCalculator if CPU-heavy jobs share the cluster; enable cgroups for isolation.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">YARN · CPU</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“The ResourceManager UI shows more vcores used than the cluster has. Is it broken?”</h4>
      <p class="scn__situation">A junior admin sees 12 vcores in use on a 6-vcore cluster.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> resource calculators.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Not broken: the Capacity Scheduler\\'s DefaultResourceCalculator places containers by memory only, so vcores are recorded but not limited.</li>
          <li>Switch to the DominantResourceCalculator so CPU is respected; in our lab that cut 12 containers to 6.</li>
          <li>For real CPU isolation, enable the LinuxContainerExecutor with cgroups.</li>
        </ul>
      </div></details>
    </article>
'''
