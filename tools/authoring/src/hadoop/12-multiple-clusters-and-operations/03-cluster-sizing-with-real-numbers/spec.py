import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()

META = dict(
    module='12-multiple-clusters-and-operations', lesson='03-cluster-sizing-with-real-numbers', n='12.3',
    module_label='Module 12 · Multiple clusters and operations',
    title='Cluster sizing with real numbers',
    desc='How to size a Hadoop cluster step by step: storage (data per day × compression × retention × replication or erasure coding + temp space + headroom + growth), worker count, NameNode heap from file and block counts, YARN containers from a batch window, memory and CPU per node, network and master nodes. A full UPI-style example (2 TB a day, 3 years, 4-hour window → 40 workers, or 22 with erasure coding) and real TestDFSIO measurements from our lab: 113 MB/s for one writer, about 210 MB/s total for six, 320 MB/s for one reader. Python sizing calculator, quiz and interview scenarios.',
    og_desc='2 TB a day for 3 years: 40 workers with replication, 22 with erasure coding. Size a Hadoop cluster step by step, with real benchmark numbers.',
    minutes=32, level='Intermediate',
    lead='Sizing is arithmetic with a few honest assumptions. This lesson walks through the whole calculation for a payments company, from terabytes per day to the number of servers, NameNode heap and containers, and measures our own lab with TestDFSIO so you can see where real throughput numbers come from and why a laptop\'s numbers must not be copied into a production plan.',
    chips=['Full worked sizing, every number shown', 'Real TestDFSIO benchmark', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='A cluster sizing calculator',
    intro='<p>The assumptions are at the top. Change one and see which part of the cluster moves. Storage usually decides the number of workers; compute checks that the nightly work fits the window.</p>',
    code='''import math
# --- assumptions (change these) ---
RAW_TB_DAY, RATIO, DAYS = 2.0, 0.25, 3 * 365     # raw data per day, Parquet+zstd size ratio, retention
REPL, TEMP, FILL, GROWTH = 3, 1.25, 0.70, 1.3     # replication, +25% temp/shuffle, keep disks 70% full, +30%
DISK_TB_PER_NODE = 12 * 8                         # 12 disks of 8 TB
NIGHTLY_SCAN_TB, MB_S_PER_CONTAINER, WINDOW_H = 60, 20, 3

stored = RAW_TB_DAY * RATIO * DAYS                # TB kept, one copy
data = stored * REPL
disk = data * TEMP / FILL * GROWTH
workers = math.ceil(disk / DISK_TB_PER_NODE)
print(f"one copy {stored:.1f} TB -> x{REPL} = {data:.1f} TB -> disk to buy {disk:.1f} TB -> {workers} workers")

files = RAW_TB_DAY * RATIO * 1024 * 1024 / 256 * DAYS   # 256 MB files
blocks = files * 2                                      # 128 MB blocks
print(f"{files:,.0f} files, {blocks:,.0f} blocks -> about {(files + blocks) * 150 / 2**30:.1f} GB of NameNode heap")

containers = NIGHTLY_SCAN_TB * 1024 * 1024 / MB_S_PER_CONTAINER / (WINDOW_H * 3600)
print(f"nightly work needs {containers:.0f} containers at once; {workers} workers x 30 = {workers * 30}")
''',
    anno=[
        ('disk = data * TEMP / FILL * GROWTH', 'Temp space for shuffle and staging, headroom so disks never pass 70%, and a year of growth.'),
        ('blocks = files * 2                                      # 128 MB blocks', 'Heap depends on the number of files and blocks, not on bytes (Lesson 7.5).'),
        ('containers = NIGHTLY_SCAN_TB * 1024 * 1024 / MB_S_PER_CONTAINER / (WINDOW_H * 3600)', 'Total work in container-seconds divided by the seconds you have.'),
    ],
    tasks=[
        dict(label='1 · Size the cluster', hint='Press <b>Run</b>. Which number decides the cluster size here: storage or compute?', code=None),
        dict(label='2 · Shorter retention', hint='<b>Predict first:</b> the regulator allows 1 year instead of 3. How many workers now?',
             code='''import math
for days in [3 * 365, 365]:
    disk = 2.0 * 0.25 * days * 3 * 1.25 / 0.70 * 1.3
    print(f"{days:4} days -> {disk:7.1f} TB -> {math.ceil(disk / 96)} workers")
'''),
        dict(label='3 · Erasure coding for cold data', hint='Keep the last 90 days with replication 3 and everything older with RS-6-3 (1.5×). How many workers?',
             code='''import math
day = 2.0 * 0.25
data = day * 90 * 3 + day * (3 * 365 - 90) * 1.5
disk = data * 1.25 / 0.70 * 1.3
print(f"{data:.1f} TB of data -> {disk:.1f} TB of disk -> {math.ceil(disk / 96)} workers")
'''),
        dict(label='4 · The small-files disaster', hint='Same 0.5 TB a day, but written as 1 MB files instead of 256 MB files. What happens to NameNode heap?',
             code='''for size_mb in [256, 1]:
    files = 0.5 * 1024 * 1024 / size_mb * 3 * 365
    blocks = files * max(1, size_mb // 128)
    print(f"{size_mb:4} MB files: {files:13,.0f} files -> {(files + blocks) * 150 / 2**30:7.1f} GB heap")
'''),
        dict(label='5 · Spot the error', hint='This window check crashes for a job whose setup takes the whole window. Make it report "does not fit" instead.',
             code='''work_container_s, window_s, setup_s = 3_145_728, 10_800, 10_800
containers = work_container_s / (window_s - setup_s)
print(round(containers), "containers")
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: benchmark your own cluster',
    intro='<p>TestDFSIO ships with Hadoop in the MapReduce tests jar. Each map task writes (or reads) one file; the result is the throughput per task. Run it inside the Module 8 lab\'s namenode container. It takes about 3 minutes and removes its files with <code>-clean</code> at the end.</p>',
    items=[
        dict(title='TestDFSIO: 1, 3 and 6 parallel writers and readers', file='dfsio_lab.sh',
             cmd=rd('lab/dfsio_lab.sh') + '\n# On your PC, in the mr-lab folder:\n#   docker cp dfsio_lab.sh lab8-namenode-1:/tmp/\n#   docker exec lab8-namenode-1 bash /tmp/dfsio_lab.sh',
             output=rd('tx123.txt').strip(),
             note='Real output. “Throughput mb/sec” is per task (total MB ÷ the sum of task times). Multiply by the number of tasks for an approximate cluster total: about 113, 185 and 210 MB/s for writes. All three workers share one laptop disk, so the total stops growing. Reads look fast because the files were just written and sit in memory (page cache).'),
    ],
)

TRACE = dict(
    heading='From terabytes a day to workers',
    intro='<p>Follow the storage calculation one multiplication at a time.</p>',
    code='''raw_day = 2.0
stored_day = raw_day * 0.25
three_years = stored_day * 1095
copies = three_years * 3
with_temp = copies * 1.25
to_buy = with_temp / 0.70 * 1.3
workers = -(-to_buy // 96)
print(stored_day, three_years, copies, round(to_buy, 1), workers)
''',
    notes={2: 'Compression :: 2 TB of raw JSON/CSV becomes about 0.5 TB of Parquet with zstd (assumption).',
           4: 'Replication :: Three copies of everything.',
           6: 'Headroom :: Divide by 0.70 so disks stay 70% full; multiply by 1.3 for growth.',
           7: 'Workers :: Round UP: you can\'t buy 39.7 servers.'},
)

WORKED_INTRO = 'Four sizing problems from different industries. Every assumption is written down, because a sizing is only as good as its assumptions.'
EXAMPLES = [
    dict(level='b', tag='Telecom · storage', title='How much disk for call records?',
         problem='<p>A telecom operator produces 800 GB of call detail records (CDRs) a day. They are kept for 2 years as ORC (about 20% of raw size), with replication 3, 25% temp space, disks at most 70% full. How many workers with 12 × 10 TB disks?</p>',
         inp='800 GB/day · 2 years · ORC 20% · 3 copies',
         approach=['Stored per day = raw × ratio.', 'Data = stored × days × 3.', 'Disk = data × 1.25 ÷ 0.70; workers = disk ÷ 120 TB, rounded up.'],
         code='''import math
stored_tb = 0.8 * 0.20 * 730
data = stored_tb * 3
disk = data * 1.25 / 0.70
print(f"{stored_tb:.1f} TB stored, {data:.1f} TB with copies, {disk:.1f} TB disk -> {math.ceil(disk / 120)} workers")
''', notes={3: 'Copies :: Replication triples the data on disk.'},
         tryit='Add 30% growth (× 1.3). One more worker is needed.'),
    dict(level='i', tag='Healthcare · NameNode', title='A hospital that stores millions of small files',
         problem='<p>A hospital chain stores imaging metadata and report PDFs: 4 lakh files a day, average 300 KB each, kept 5 years. Estimate the NameNode heap at about 150 bytes per file and per block, and compare with packing each day into 1 GB SequenceFiles (Lesson 10.1).</p>',
         inp='4,00,000 files/day × 300 KB · 5 years',
         approach=['Small files: 1 block each → 2 objects per file.', 'Packed: day size ÷ 1 GB files, 8 blocks each.', 'Heap = objects × 150 B.'],
         code='''import math
days = 5 * 365
small = 400_000 * days * 2
day_gb = 400_000 * 300 / 1024 / 1024
packed_files = math.ceil(day_gb) * days
packed = packed_files * (1 + 8)
print(f"small files: {small * 150 / 2**30:.0f} GB heap; packed: {packed * 150 / 2**30:.2f} GB heap")
''', notes={3: 'Small files :: Each tiny file costs a file object and a block object.'},
         tryit='Bytes on disk are the same either way. Only the NameNode cares, and it cares a lot: about 204 GB vs 0.26 GB.'),
    dict(level='i', tag='E-commerce · compute', title='Will the sale-day report finish in time?',
         problem='<p>On a sale day an e-commerce company must process 45 TB of clickstream between midnight and 3 AM. Each 4 GB container processes about 25 MB/s. The cluster has 30 workers with 30 containers each. Does it fit, and how much of the cluster does it use?</p>',
         inp='45 TB · 3 hours · 25 MB/s per container · 900 containers',
         approach=['Container-seconds = MB ÷ MB/s.', 'Concurrent containers = container-seconds ÷ window seconds.', 'Compare with 30 × 30.'],
         code='''work_s = 45 * 1024 * 1024 / 25
need = work_s / (3 * 3600)
have = 30 * 30
print(f"needs {need:.0f} containers at once, has {have} -> {100 * need / have:.0f}% of the cluster")
''', notes={2: 'Concurrency :: Work spread evenly across the window; real jobs have waves and skew, so keep slack.'},
         tryit='Leave room for skew and retries: plan to use at most about 70% of the cluster for the critical job.'),
    dict(level='a', tag='Government · growth', title='Five years of a welfare scheme\'s data',
         problem='<p>A state welfare scheme stores 300 GB a day (after Parquet compression) and grows 40% a year. Data is kept forever. With replication 3, 25% temp space and 70% fill, how many 96 TB workers are needed at the end of each of the next 5 years?</p>',
         inp='300 GB/day in year 1 · +40%/year · keep forever',
         approach=['Each year adds 365 × that year\'s daily volume.', 'Accumulate, then apply copies, temp and fill.', 'Round up per year.'],
         code='''import math
total, daily = 0.0, 0.3
for year in range(1, 6):
    total += daily * 365
    disk = total * 3 * 1.25 / 0.70
    print(f"year {year}: {total:7.1f} TB kept -> {math.ceil(disk / 96):3} workers")
    daily *= 1.4
''', notes={4: 'Accumulation :: Keep-forever data only grows; growth compounds on top.'},
         tryit='Moving data older than a year to erasure coding (1.5×) or to object storage changes the slope, not just the start.'),
]

QUIZ = mix([
    dict(q='Which usually decides the number of workers in a big Hadoop cluster?', options=['The number of users', 'Storage: data × retention × copies, plus headroom', 'The NameNode heap', 'The number of racks'], answer=1,
         why='Compute is then checked against the batch window; it rarely needs more nodes than storage does.'),
    dict(q='Why divide by 0.70 when sizing disks?', options=['HDFS uses 30% for metadata', 'To keep disks at most 70% full, leaving room for temp data, rebalancing and failures', 'Because of compression', 'Because of replication'], answer=1,
         why='Full disks break jobs and DataNodes; plan headroom.'),
    dict(q='What drives NameNode heap?', options=['Total bytes stored', 'The number of files, directories and blocks', 'The number of DataNodes', 'The replication factor only'], answer=1,
         why='About 150 bytes per object as a rule of thumb (Lesson 7.5).'),
    dict(q='In our TestDFSIO run, what happened to per-task write throughput from 1 to 6 parallel writers?', options=['It stayed at 113 MB/s', 'It fell from 113 to 35 MB/s while the total rose only to about 210 MB/s', 'It doubled', 'The job failed'], answer=1,
         why='All workers share one laptop disk, so the total saturates.'),
    dict(q='Why are lab benchmark numbers NOT used directly for a production plan?', options=['They are always too high', 'The lab shares one laptop disk and network; production nodes have many disks and their own NICs', 'TestDFSIO is not accurate', 'Production uses a different HDFS'], answer=1,
         why='Benchmark the real hardware, or use measured numbers from similar nodes.'),
    dict(q='How does erasure coding RS-6-3 change storage for cold data compared with replication 3?', options=['No change', 'From 3× to 1.5× the data size', 'From 3× to 6×', 'It removes the need for temp space'], answer=1,
         why='In the example: 40 workers with replication, 22 with cold data on RS-6-3.'),
    dict(q='A nightly job needs 3,145,728 container-seconds and has a 3-hour window. How many containers must run at once?', options=['About 29', 'About 291', 'About 2,910', 'About 87'], answer=1,
         why='3,145,728 ÷ 10,800 s ≈ 291.'),
    dict(q='Which masters does an HA Hadoop cluster typically need at minimum?', options=['One NameNode', 'Two NameNodes, three JournalNodes, three ZooKeeper servers, two ResourceManagers', 'Five NameNodes', 'One ZooKeeper'], answer=1,
         why='Odd-sized quorums of 3 (or 5) tolerate failures (Lesson 7.1).'),
])

REVISION = [
    '<b>Storage:</b> raw/day × compression ratio × retention days × copies (3, or about 1.5 with EC) × 1.25 temp ÷ 0.70 fill × growth.',
    '<b>Workers</b> = disk needed ÷ disk per node, rounded up. Example: 2 TB/day, 3 years → 3,812.9 TB → 40 workers (22 with cold data on RS-6-3).',
    '<b>NameNode heap</b> ≈ (files + blocks) × 150 B; keep files large. 2.2 M files + 4.5 M blocks ≈ 0.9 GB of objects; give the NameNode generous headroom.',
    '<b>Compute:</b> containers at once = work (container-seconds) ÷ window seconds; example 291 vs 1,200 available.',
    '<b>Per node:</b> RAM − reserve (OS, DataNode, NodeManager) = YARN pool; balance memory per vcore (Lesson 11.4).',
    '<b>Masters:</b> 2 NameNodes, 3 JournalNodes, 3 ZooKeeper, 2 ResourceManagers, JobHistory, plus edge nodes.',
    '<b>Benchmark</b> real hardware: our laptop lab wrote 113 MB/s with one task and saturated near 210 MB/s total.',
]
FAQ = [
    ('How do you calculate the size of a Hadoop cluster?', 'Start from storage: daily data volume × compression ratio × retention period × replication factor (3, or about 1.5 with erasure coding), add 20–30% for temporary and shuffle data, divide by the target disk fill (around 70%) and add growth. Divide by usable disk per worker to get the number of workers. Then check compute against the batch window, size the NameNode heap from the expected number of files and blocks, and add masters and edge nodes.'),
    ('How much memory does a NameNode need?', 'Roughly 150 bytes per file, directory and block object as a rule of thumb, often summarised as about 1 GB of heap per million blocks. The real driver is the number of objects, so a cluster full of small files needs far more heap than one with the same bytes in large files. Leave plenty of headroom for growth and garbage collection.'),
    ('What is TestDFSIO?', 'A benchmark in the Hadoop MapReduce tests jar. Each map task writes or reads one file in HDFS, and the job reports throughput per task and average I/O rate. It measures the storage path end to end (client, DataNodes, disks, network) and is used before and after hardware or configuration changes.'),
    ('Why keep HDFS disks below 70–80% full?', 'Jobs need temporary space for map output, staging and new data; the balancer needs room to move blocks; when a node or disk fails, its replicas are re-created on the others; and nearly full disks make DataNodes and NodeManagers unhealthy. Headroom is what keeps a failure from turning into an outage.'),
    ('Is it cheaper to run Hadoop in the cloud?', 'It depends on utilisation. Steady, always-busy clusters are often cheaper on owned or reserved hardware; spiky or experimental workloads benefit from cloud clusters that are created for a job and deleted, with data kept in object storage. Compare the full cost: servers, power, space and staff on one side; compute hours, storage, data transfer and support on the other.'),
]

PRACTICE_INTRO = 'Sizing exercises. Write your assumptions first, then calculate.'
PROBLEMS = [
    dict(level='easy', title='Copies on disk', stmt='10 TB of data with replication 3 vs RS-6-3 erasure coding: how much disk does each use?', inp='10 TB',
         code='''print("replication 3:", 10 * 3, "TB   RS-6-3:", 10 * 1.5, "TB")
''', explain='30 TB vs 15 TB. Our lab measured the same 2:1 shape: 422 MB vs 235 MB (Lesson 7.3, RS-3-2 there).'),
    dict(level='easy', title='Aggregate throughput', stmt='Our TestDFSIO run reported 61.82 MB/s per task with 3 writers and 34.99 with 6. What was the total in each case?', inp='per-task throughput × tasks',
         code='''print(round(3 * 61.82, 1), round(6 * 34.99, 1), "MB/s")
''', explain='About 185 and 210 MB/s: doubling the writers added only 13% because one disk was shared.'),
    dict(level='easy', title='Compression saves workers', stmt='The UPI example stores 0.5 TB/day as Parquet+zstd. If it stored raw CSV (2 TB/day), how many workers would 3 years need?', inp='2 TB/day, no compression',
         code='''import math
disk = 2.0 * 1095 * 3 * 1.25 / 0.70 * 1.3
print(f"{disk:.0f} TB -> {math.ceil(disk / 96)} workers")
''', explain='159 workers instead of 40: the file format is a sizing decision (Lesson 10.2).'),
    dict(level='medium', title='Memory per vcore', stmt='A worker has 256 GB RAM and 32 cores. Reserve 32 GB and 2 cores for the OS and daemons. With 1 vcore per container, what container size uses memory and CPU evenly?', inp='224 GB, 30 vcores',
         code='''print(f"{224 / 30:.1f} GB per vcore")
''', explain='About 7.5 GB: smaller containers leave memory idle, bigger ones leave cores idle (Lesson 11.4).'),
    dict(level='medium', title='Ingest bandwidth', stmt='0.5 TB of new data arrives every day and must be loaded in a 2-hour window with 3 replicas. What write bandwidth must the cluster sustain?', inp='0.5 TB × 3 in 2 hours',
         code='''mb = 0.5 * 1024 * 1024 * 3
print(f"{mb / 7200:.0f} MB/s across the cluster")
''', explain='About 218 MB/s, close to what our whole laptop lab could write. Forty production workers do this easily.'),
    dict(level='medium', title='How many racks?', stmt='40 workers, 3 masters and 2 edge nodes, with at most 20 servers per rack. How many racks, and why spread masters across racks?', inp='45 servers, 20 per rack',
         code='''import math
print(math.ceil(45 / 20), "racks")
''', explain='3 racks. Put the two NameNodes and the three JournalNodes in different racks so one rack failure can\'t take the quorum down.'),
    dict(level='business', title='Own or rent?', stmt='Owning 40 workers costs ₹6 crore over 3 years including power and staff (illustrative). A cloud cluster of the same size costs ₹1,500 per node-hour (illustrative). Above what average number of busy hours a day is owning cheaper?', inp='₹6 crore / 3 years vs ₹1,500 × 40 nodes per hour',
         code='''own_per_day = 6e7 / (3 * 365)
cloud_per_hour = 1500 * 40
print(f"break-even at {own_per_day / cloud_per_hour:.1f} cluster-hours a day")
''', explain='About 0.9 hours a day with these made-up prices. Plug in real quotes before any decision; the shape of the calculation is what matters.'),
    dict(level='advanced', title='A sizing function', stmt='Write size(raw_tb_day, ratio, days, copies) returning the number of 96 TB workers (25% temp, 70% fill, 30% growth). Check it against the UPI example.', inp='2.0, 0.25, 1095, 3',
         code='''import math
def size(raw_tb_day, ratio, days, copies, node_tb=96):
    disk = raw_tb_day * ratio * days * copies * 1.25 / 0.70 * 1.3
    return math.ceil(disk / node_tb)
print(size(2.0, 0.25, 1095, 3), size(2.0, 0.25, 1095, 1.5))
''', explain='40 and 20. The 22 in the lesson keeps the last 90 days with 3 copies; putting everything on erasure coding would give 20.'),
]

SCN_INTRO = 'Sizing questions are common for experienced roles. Interviewers look for a method and stated assumptions, not a memorised number.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Sizing · method</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>“We ingest 5 TB a day and keep it 2 years. How many nodes?”</h4>
      <p class="scn__situation">The classic open question.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> a method with assumptions out loud.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Ask: format and compression, replication or EC, growth, node hardware.</li>
          <li>Storage: 5 × ratio × 730 × 3 × 1.25 ÷ 0.7 × growth; divide by usable disk per node.</li>
          <li>Then check compute against the processing window and NameNode heap against file counts.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">NameNode · capacity</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>The NameNode needs a restart every few weeks: heap is full</h4>
      <p class="scn__situation">Storage is only 40% used.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> objects vs bytes.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Heap tracks files and blocks, so check FilesTotal and BlocksTotal and the average file size per folder.</li>
          <li>Fix the writers producing small files; compact old data (Lesson 7.5).</li>
          <li>Short term: raise heap with GC tuning; long term: federation if one namespace is too big (Lesson 7.2).</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Benchmarks · honesty</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“Our test cluster writes 200 MB/s. Is that good?”</h4>
      <p class="scn__situation">A trainee ran TestDFSIO on three virtual machines.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> understanding what was measured.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Ask what is shared: if all VMs use one physical disk, adding writers won't add throughput.</li>
          <li>Look at per-task vs total, and whether reads came from page cache.</li>
          <li>Benchmark the real hardware with realistic file sizes and concurrency.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Planning · growth</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Finance asks for a 3-year hardware budget</h4>
      <p class="scn__situation">Data grows 40% a year and nobody deletes anything.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> retention and tiering as levers.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Model year by year with compounding growth; buy in phases, not all at once.</li>
          <li>Propose levers: retention policies, better formats, erasure coding or archive storage for cold data.</li>
          <li>Present a range with assumptions, and review it every quarter against real usage.</li>
        </ul>
      </div></details>
    </article>
'''
