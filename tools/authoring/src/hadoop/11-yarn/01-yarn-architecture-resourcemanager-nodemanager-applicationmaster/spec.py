import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()

META = dict(
    module='11-yarn', lesson='01-yarn-architecture-resourcemanager-nodemanager-applicationmaster', n='11.1',
    module_label='Module 11 · YARN',
    title='YARN architecture: ResourceManager, NodeManager, ApplicationMaster',
    desc='YARN architecture explained on a live Hadoop 3.5.0 cluster: ResourceManager (Scheduler + ApplicationsManager), NodeManagers, one ApplicationMaster per application and containers. Real jps output, yarn node -list -showDetails (2048 MB, 2 vcores per node), RM REST metrics (6144 MB, 6 vcores), and a 422 MB job holding 5 containers and 2,560 MB with 384 MB requests rounded up to 512 MB. Architecture diagram, two animations, ports, RM HA, Spark/Tez/Flink on YARN, Python simulation, quiz and interview scenarios.',
    og_desc='Who decides where your code runs? Watch YARN hand out 5 containers and 2,560 MB on a real cluster, with an architecture diagram and animations.',
    minutes=30, level='Intermediate',
    lead='YARN is the layer that turns a cluster into a pool of memory and CPU that many applications can share. This lesson takes it apart on a live cluster: the ResourceManager and its two halves, the NodeManagers on every worker, the per-job ApplicationMaster and the containers it asks for, with every number read from the running system.',
    chips=['Live cluster, real numbers', 'Architecture diagram + 2 animations', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Be the ResourceManager for one job',
    intro='<p>This model keeps the RM\'s books for our lab: three NodeManagers with 2,048 MB each, a 256 MB minimum allocation, one AM of 512 MB and four maps asking for 384 MB. Containers are granted as NodeManagers heartbeat in, one per heartbeat, in the order they arrived in our run.</p>',
    code='''import math
MIN_ALLOC = 256                                   # yarn.scheduler.minimum-allocation-mb
nodes = {"worker1": 2048, "worker2": 2048, "worker3": 2048}
used = {n: 0 for n in nodes}

def normalize(mb):                                # round UP to a multiple of the minimum
    return math.ceil(mb / MIN_ALLOC) * MIN_ALLOC

requests = [("AM", 512)] + [(f"map{i}", 384) for i in range(4)]
heartbeats = ["worker1", "worker2", "worker3", "worker1", "worker2"]   # who reported free space next

for (name, ask), node in zip(requests, heartbeats):
    size = normalize(ask)
    if used[node] + size <= nodes[node]:
        used[node] += size
        print(f"{name:5} asks {ask} MB -> gets {size} MB on {node}")

print("per node:", used)
print("allocated", sum(used.values()), "of", sum(nodes.values()), "MB in", len(requests), "containers")
''',
    anno=[
        ('    return math.ceil(mb / MIN_ALLOC) * MIN_ALLOC', 'The Scheduler normalizes every request: 384 MB becomes 512 MB, which is why 4 maps + AM held 2,560 MB.'),
        ('heartbeats = ["worker1", "worker2", "worker3", "worker1", "worker2"]   # who reported free space next', 'The Scheduler assigns containers when a NodeManager heartbeats and reports free space.'),
        ('    if used[node] + size <= nodes[node]:', 'A container must fit entirely on one node: YARN never splits a container across machines.'),
    ],
    tasks=[
        dict(label='1 · Five containers', hint='Press <b>Run</b>. Check the totals against the lab: worker1 1024, worker2 1024, worker3 512, 2,560 MB.', code=None),
        dict(label='2 · Bigger maps', hint='<b>Predict first:</b> if each map asks for 1,100 MB, what does it get, and how many such maps fit on one 2,048 MB node?',
             code='''import math
ask, MIN_ALLOC, node = 1100, 256, 2048
size = math.ceil(ask / MIN_ALLOC) * MIN_ALLOC
print("gets", size, "MB;", node // size, "fit on one node; wasted per container:", size - ask, "MB")
'''),
        dict(label='3 · How many at once?', hint='How many 512 MB containers can the whole cluster run at the same time? How many of them can be maps if one is the AM?',
             code='''total_mb, container = 3 * 2048, 512
slots = total_mb // container
print(slots, "containers in total,", slots - 1, "for tasks when one AM is running")
'''),
        dict(label='4 · Memory-only accounting', hint='The default calculator only checks memory. Put 3 containers of 512 MB and 1 vcore each on worker1 (2 vcores). Does memory fit? Do vcores?',
             code='''node = {"mb": 2048, "vcores": 2}
containers = [(512, 1)] * 3
mb = sum(c[0] for c in containers); vc = sum(c[1] for c in containers)
print(f"memory {mb}/{node['mb']} MB fits: {mb <= node['mb']}")
print(f"vcores {vc}/{node['vcores']} fits: {vc <= node['vcores']}  (the default calculator doesn't check this)")
'''),
        dict(label='5 · Spot the error', hint='A job asks for a 3,072 MB AM, but the largest allowed container is 2,048 MB here. Make the check raise a clear error, as YARN does (InvalidResourceRequestException).',
             code='''MAX_ALLOC = 2048
def request(mb):
    if mb > MAX_ALLOC:
        raise ValueError(f"Invalid resource request: {mb} MB > maximum allocation {MAX_ALLOC} MB")
    return mb
print(request(512))
print(request(3072))
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: look inside YARN',
    intro='<p>This uses the Module 8 lab (<code>docker compose -p lab8 up -d</code> in the <code>mr-lab</code> folder) and the <code>mr.jar</code> and <code>orders_x90.csv</code> from Lesson 8.1. Unlike most scripts in Module 8, this one runs <b>on your PC</b> in the <code>mr-lab</code> folder, because it looks at several containers with <code>docker exec</code>.</p>',
    items=[
        dict(title='Daemons, NodeManagers, metrics and a running job', file='yarn_arch_lab.sh',
             cmd=rd('lab/yarn_arch_lab.sh') + '\n# Run on your PC, in the mr-lab folder:\n#   bash yarn_arch_lab.sh',
             output=rd('tx111.txt').strip(),
             note='Real output. When we ran it, the previous job (and its client, RunJar) was still finishing, which is why worker2 already held one 512 MB container in step 2 and appsRunning was 1. Your container placement and port numbers (worker1:36427) will differ; the 512 MB rounding and the 6144 MB total will not.'),
    ],
)

TRACE = dict(
    heading='The Scheduler on each heartbeat',
    intro='<p>Watch the waiting requests and each node\'s free memory as three heartbeats arrive. A request is only granted on a heartbeat from a node with enough free space.</p>',
    code='''free = {"w1": 1024, "w2": 512, "w3": 2048}
waiting = [512, 512, 1024]
for node in ["w2", "w1", "w3"]:
    if waiting and free[node] >= waiting[0]:
        free[node] -= waiting.pop(0)
print(free, waiting)
''',
    notes={3: 'Heartbeat :: Each NodeManager reports its free space; the Scheduler tries to place the next request there.',
           5: 'Grant :: The node\'s free memory goes down; the request leaves the queue.'},
)

WORKED_INTRO = 'Four YARN sizing and design problems from different industries.'
EXAMPLES = [
    dict(level='b', tag='Healthcare · capacity', title='Will a hospital chain\'s job run in one wave?',
         problem='<p>A hospital chain analyses scan metadata with a job of 50 map tasks of 2 GB each. Its YARN cluster has 10 NodeManagers offering 32 GB each. How many 2 GB containers fit at once, and does the job run in a single wave (keep one 2 GB container for the AM)?</p>',
         inp='10 nodes × 32 GB · 50 maps × 2 GB · AM 2 GB',
         approach=['Containers per node = node memory / container size.',
                   'Cluster containers = per node × nodes.',
                   'Subtract the AM and compare with 50.'],
         code='''per_node = 32 // 2
total = per_node * 10
print(per_node, "per node,", total, "in the cluster,", total - 1, "for maps -> one wave:", total - 1 >= 50)
''', notes={2: 'Cluster :: YARN sees one pool of 320 GB, but each container must fit on a single node.'},
         tryit='Make each map 12 GB. Now only 2 fit per node (24 of 32 GB) and 8 GB per node is wasted.'),
    dict(level='i', tag='E-commerce · rounding', title='The cost of an awkward container size',
         problem='<p>During a sale an e-commerce team runs 400 maps asking for 1,100 MB each on a cluster with a 1,024 MB minimum allocation. How much memory is reserved but never asked for? What request size wastes nothing?</p>',
         inp='400 × 1,100 MB · minimum 1,024 MB',
         approach=['Normalized size = round up to a multiple of 1,024.',
                   'Waste per container = normalized - asked.',
                   'Multiply by 400.'],
         code='''import math
ask, minimum, n = 1100, 1024, 400
size = math.ceil(ask / minimum) * minimum
print(f"each gets {size} MB, waste {(size - ask) * n / 1024:.0f} GB across {n} containers")
''', notes={3: 'Normalize :: 1,100 MB becomes 2,048 MB: nearly half of each container is padding.'},
         tryit='Ask for 1,024 MB (and set the heap to about 80% of it) or reduce the minimum allocation to 256 MB as our lab does.'),
    dict(level='i', tag='Telecom · failures', title='How long until YARN notices a dead node?',
         problem='<p>A telecom billing cluster: NodeManagers heartbeat every 1 s; the RM declares a node LOST after 600 s without heartbeats (<code>yarn.nm.liveness-monitor.expiry-interval-ms</code>). A node with 6 running map tasks loses power. When does the RM tell the AMs, and how much task time is lost if each task had run 4 minutes?</p>',
         inp='heartbeat 1 s · expiry 600 s · 6 tasks × 4 min',
         approach=['Detection by the RM = expiry interval.',
                   'Lost work = tasks × minutes already run.',
                   'AMs often notice earlier: their tasks stop reporting progress.'],
         code='''expiry_s, tasks, minutes_done = 600, 6, 4
print(f"RM marks the node LOST after {expiry_s // 60} min; {tasks * minutes_done} task-minutes must be redone")
''', notes={2: 'Detection :: The AM may see the failure earlier through missing task status updates (mapreduce.task.timeout).'},
         tryit='Lowering the expiry to 2 minutes detects faster but also marks nodes lost during short network blips.'),
    dict(level='a', tag='Banking · multi-tenant', title='Can Spark and MapReduce share the night?',
         problem='<p>A bank\'s 30 workers each give YARN 56 GB and 16 vcores. At 1 AM a Spark job needs a 4 GB driver/AM and 20 executors of 8 GB and 4 vcores. A MapReduce job needs a 1.5 GB AM (normalized to 2 GB with a 1 GB minimum) and 300 maps of 2 GB, 1 vcore. Do both fit at once by memory? By vcores?</p>',
         inp='30 × (56 GB, 16 vcores) · Spark + MR',
         approach=['Total cluster memory and vcores.',
                   'Sum both jobs\' requests.',
                   'Compare; vcores only matter with the DominantResourceCalculator.'],
         code='''mem, vc = 30 * 56, 30 * 16
spark_mem, spark_vc = 4 + 20 * 8, 1 + 20 * 4
mr_mem, mr_vc = 2 + 300 * 2, 1 + 300
need_mem, need_vc = spark_mem + mr_mem, spark_vc + mr_vc
print(f"memory {need_mem}/{mem} GB fits: {need_mem <= mem}")
print(f"vcores {need_vc}/{vc} fits: {need_vc <= vc}")
''', notes={4: 'Total :: 766 GB of 1,680 GB and 382 of 480 vcores: both fit, even when vcores are counted.'},
         tryit='Give the MR job 1,000 maps: it now needs 2,166 GB and 1,082 vcores, more than the cluster has, so its maps run in waves while Spark keeps its executors.'),
]

QUIZ = mix([
    dict(q='What does the ResourceManager do?', options=['Runs map and reduce tasks', 'Tracks cluster resources and grants containers to applications', 'Stores HDFS blocks', 'Merges map output'], answer=1,
         why='It manages containers, not tasks; tasks are the ApplicationMaster\'s business.'),
    dict(q='How many ApplicationMasters does a cluster running 3 jobs have?', options=['1, shared', '3, one per application', 'One per NodeManager', 'None for MapReduce'], answer=1,
         why='Each application gets its own AM, e.g. one MRAppMaster per MapReduce job.'),
    dict(q='Which two parts make up the core of the ResourceManager?', options=['NameNode and DataNode', 'Scheduler and ApplicationsManager', 'Mapper and Reducer', 'JobTracker and TaskTracker'], answer=1,
         why='The Scheduler allocates resources; the ApplicationsManager accepts apps and starts their AMs.'),
    dict(q='In our lab each map asked for 384 MB. What did it get?', options=['384 MB', '512 MB', '1024 MB', '256 MB'], answer=1,
         why='Requests are rounded up to a multiple of the 256 MB minimum allocation: 4 maps + AM = 2,560 MB.'),
    dict(q='Which process appeared on worker1 only while the job ran?', options=['DataNode', 'MRAppMaster', 'NodeManager', 'ResourceManager'], answer=1,
         why='The AM (and YarnChild task JVMs) exist only for the life of the application.'),
    dict(q='Which container number is always the ApplicationMaster?', options=['The last one', 'container_…_01_000001', 'Any container on the master node', 'There is no fixed number'], answer=1,
         why='The first container of each attempt is the AM; _01_ is the attempt number.'),
    dict(q='What does “Configured Resources: memory 2048” for a NodeManager mean?', options=['The machine has 2 GB of RAM', 'The NodeManager offers 2,048 MB to YARN containers', 'Each container gets 2 GB', 'The DataNode uses 2 GB'], answer=1,
         why='It is yarn.nodemanager.resource.memory-mb; the node itself was using 5.6 GB.'),
    dict(q='Why did Hadoop 2 introduce YARN?', options=['To replace HDFS', 'Because one JobTracker scheduling the cluster AND tracking every task did not scale, and it only ran MapReduce', 'To make Java faster', 'To remove the NameNode'], answer=1,
         why='Splitting resource management (RM) from application management (AM) fixed scaling and opened the cluster to Spark, Tez and others.'),
])

REVISION = [
    '<b>ResourceManager</b> = <b>Scheduler</b> (who gets what) + <b>ApplicationsManager</b> (accept apps, start/restart AMs). One active per cluster; HA with ZooKeeper.',
    '<b>NodeManager</b> per worker: launches and monitors containers, heartbeats to the RM, runs the shuffle service and log aggregation.',
    '<b>ApplicationMaster</b> per application: requests containers (size, locality, priority), runs and retries tasks. MRAppMaster, Spark AM/driver, Tez AM.',
    '<b>Container</b> = memory + vcores on one node, one process. Requests are rounded up to the minimum allocation.',
    'Lab: 3 NMs × (2,048 MB, 2 vcores) = 6,144 MB, 6 vcores; one job held 5 containers, 2,560 MB (AM 512 + 4 × 512).',
    'Ports: 8088 RM UI/REST, 8032 clients, 8030 AMs, 8031 NMs, 8042 NM UI.',
    'YARN tracks containers, not tasks: that is why it scales and runs any framework.',
]
FAQ = [
    ('What are the main components of YARN?', 'The ResourceManager (with its Scheduler and ApplicationsManager), a NodeManager on every worker, one ApplicationMaster per application, and containers, which are allocations of memory and CPU on a node in which processes run. Optionally a Timeline Server stores application history.'),
    ('What is the difference between the ResourceManager and the ApplicationMaster?', 'The ResourceManager is a single cluster-wide service that decides how much memory and CPU each application gets and where. The ApplicationMaster belongs to one application: it asks the ResourceManager for containers and decides which tasks run in them, tracks their progress and retries failures.'),
    ('What is a container in YARN?', 'A container is a slice of one node\'s resources, a given amount of memory and virtual cores, granted by the ResourceManager to an application. The NodeManager starts one process in it (for example a map task JVM or a Spark executor) and enforces its limits.'),
    ('Why was YARN introduced in Hadoop 2?', 'In Hadoop 1 the JobTracker both scheduled the cluster and tracked every task of every job, which limited clusters to around 4,000 nodes, and fixed map and reduce slots wasted resources. YARN moves per-job work to ApplicationMasters and replaces slots with flexible containers, so clusters scale further and can run frameworks other than MapReduce.'),
    ('Can Spark run on YARN?', 'Yes. In cluster mode the Spark driver runs inside the ApplicationMaster container and executors run in other containers; in client mode the driver runs on the submitting machine and a small AM only requests executors. Hive on Tez, Flink and many other frameworks run on YARN the same way.'),
]

PRACTICE_INTRO = 'YARN architecture exercises using the real numbers from our cluster.'
PROBLEMS = [
    dict(level='easy', title='Cluster totals', stmt='Each of 3 NodeManagers offers 2,048 MB and 2 vcores. What are the cluster totals the RM reports?', inp='3 × (2048 MB, 2 vcores)',
         code='''print(3 * 2048, "MB,", 3 * 2, "vcores")
''', explain='6,144 MB and 6 vcores: totalMB and totalVirtualCores in /ws/v1/cluster/metrics.'),
    dict(level='easy', title='Explain 2,560 MB', stmt='Show how one AM of 512 MB and four maps asking 384 MB add up to 2,560 MB.', inp='AM 512 · 4 × 384 → rounded',
         code='''import math
map_size = math.ceil(384 / 256) * 256
print(512 + 4 * map_size)
''', explain='Each map is rounded to 512 MB: 512 + 4 × 512 = 2,560.'),
    dict(level='easy', title='Share of the cluster', stmt='What percentage of the cluster\'s memory did the job hold?', inp='2,560 of 6,144 MB',
         code='''print(f"{2560 / 6144:.0%}")
''', explain='About 42%: the rest was free for other applications.'),
    dict(level='medium', title='Round these requests', stmt='With a 256 MB minimum, what do requests of 100, 256, 300, 600 and 1,100 MB become?', inp='5 requests',
         code='''import math
for ask in [100, 256, 300, 600, 1100]:
    print(ask, "->", math.ceil(ask / 256) * 256)
''', explain='256, 256, 512, 768 and 1,280 MB. Lesson 11.4 confirms these on the cluster.'),
    dict(level='medium', title='Place on heartbeats', stmt='Free memory: w1 512, w2 2048, w3 1024. Heartbeats arrive w1, w2, w3, w2. Place four 1,024 MB containers.', inp='3 nodes, 4 heartbeats',
         code='''free = {"w1": 512, "w2": 2048, "w3": 1024}
waiting = 4
for node in ["w1", "w2", "w3", "w2"]:
    if waiting and free[node] >= 1024:
        free[node] -= 1024; waiting -= 1
        print("granted on", node)
print("still waiting:", waiting, free)
''', explain='w1 has no room; w2, w3 and w2 again get one each; one request waits for the next heartbeat with space.'),
    dict(level='medium', title='Count the daemons', stmt='A cluster has 2 masters (RM + NameNode on one, standby RM on the other) and 50 workers. How many YARN daemons run?', inp='2 RMs + 50 NMs',
         code='''print(2 + 50, "YARN daemons (plus one AM per running application)")
''', explain='52 long-running daemons; AMs and task containers come and go with applications.'),
    dict(level='business', title='One cluster or three?', stmt='Three teams each want their own 20-node cluster, each busy about 30% of the time. With one shared 30-node YARN cluster, average demand is 3 × 20 × 0.3 nodes. Compare node counts.', inp='3 × 20 nodes at 30%',
         code='''separate = 3 * 20
avg_demand = 3 * 20 * 0.3
print(f"separate: {separate} nodes; shared average demand: {avg_demand:.0f} nodes -> a 30-node shared cluster leaves headroom")
''', explain='60 nodes vs 30: sharing through YARN queues halves the hardware (illustrative; peak overlaps need planning, Lesson 11.3).'),
    dict(level='advanced', title='Worst-case AM memory', stmt='maximum-am-resource-percent is 0.1 by default in the Capacity Scheduler. On our 6,144 MB cluster, how many 512 MB AMs can run at once, and what happens to more applications?', inp='6144 MB · 10% · 512 MB AMs',
         code='''limit = 6144 * 0.1
print(f"AM limit {limit:.0f} MB -> {int(limit // 512)} AM(s) at once (YARN always allows at least one)")
''', explain='Only one 512 MB AM fits under 614 MB; further applications stay ACCEPTED until it finishes. This protects clusters from filling up with AMs that have no room for tasks.'),
]

SCN_INTRO = 'YARN architecture questions come up in every Hadoop and Spark interview.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Architecture · basics</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“Explain the YARN architecture”</h4>
      <p class="scn__situation">Asked in almost every big data interview.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> the roles and how they talk.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>ResourceManager (Scheduler + ApplicationsManager) manages cluster resources; NodeManagers run containers on each worker.</li>
          <li>Each application has an ApplicationMaster that requests containers and manages its own tasks.</li>
          <li>Flow: submit → AM container → AM registers and requests containers → NMs launch tasks → AM unregisters.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Operations · stuck jobs</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Jobs stay in ACCEPTED and never start</h4>
      <p class="scn__situation">The RM UI shows 15 applications ACCEPTED, cluster memory 40% used.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> AM limits and container sizing.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>ACCEPTED means the AM container hasn't been allocated: check the queue's maximum-am-resource-percent and the queue's capacity, not just total free memory.</li>
          <li>Check that the AM size fits on a single node (free memory may be fragmented across nodes) and is not above maximum-allocation-mb.</li>
          <li>Look at the application's diagnostics in the RM UI; they name the limit that blocks it.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Design · sizing</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>“Our nodes have 128 GB RAM. What should yarn.nodemanager.resource.memory-mb be?”</h4>
      <p class="scn__situation">A new cluster is being set up.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> leaving room for everything that isn't a container.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Subtract the OS, DataNode, NodeManager and other agents (often 8–16 GB), and any co-located services such as HBase.</li>
          <li>Give the rest to YARN, e.g. about 100–112 GB, and set the minimum allocation so common container sizes divide it evenly.</li>
          <li>Set vcores to the cores available to containers and use the DominantResourceCalculator if CPU matters (Lesson 11.4).</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Reliability · failures</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>“What happens if the ApplicationMaster or the ResourceManager dies?”</h4>
      <p class="scn__situation">A follow-up after the architecture question.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> recovery at each level.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>AM dies: the ApplicationsManager starts a new attempt (yarn.resourcemanager.am.max-attempts, default 2); the MapReduce AM can recover finished tasks from its history.</li>
          <li>RM dies: with RM HA, the standby becomes active through ZooKeeper; with work-preserving recovery running containers continue.</li>
          <li>NodeManager dies: after the liveness timeout its containers are reported lost and AMs rerun those tasks elsewhere.</li>
        </ul>
      </div></details>
    </article>
'''
