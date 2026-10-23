import os
HERE = os.path.dirname(os.path.abspath(__file__))
BODY = body(HERE)
rd = lambda f: open(os.path.join(HERE, f)).read()

META = dict(
    module='07-hdfs-advanced', lesson='02-hdfs-federation', n='7.2',
    module_label='Module 7 · HDFS advanced',
    title='HDFS federation',
    desc='HDFS federation on a real Hadoop 3.5.0 cluster: two independent NameNodes (canteen and hostel) sharing three DataNodes, one cluster ID, two block pools visible on the DataNode disk, a ViewFS mount table giving clients one tree, “Renames across Mount points not supported”, and one namespace surviving while the other NameNode is down. Federation vs HA, ViewFS vs Router-Based Federation, NameNode memory sizing, Python simulations, quiz and interview scenarios.',
    og_desc='When one NameNode\'s memory is not enough: split the namespace, share the DataNodes. A real two-NameNode cluster.',
    minutes=26, level='Advanced',
    lead='HA protects the NameNode from failure, but not from its own limits: every file and block lives in one NameNode\'s memory. Federation runs several independent NameNodes, each owning part of the folder tree, on the same DataNodes. This lesson builds a two-NameNode cluster, looks at the block pools on a DataNode\'s disk, and shows what works and what doesn\'t across namespaces.',
    chips=['Real two-NameNode cluster', 'Block pools on disk', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='A mount table that routes paths to NameNodes',
    intro='<p>ViewFS is essentially a longest-prefix lookup: the path\'s mount point decides which NameNode answers. This program routes a few paths and refuses a rename across mount points, like our real cluster did.</p>',
    code='''mounts = {"/canteen": "hdfs://nn-canteen:8020/canteen",
          "/hostel":  "hdfs://nn-hostel:8020/hostel",
          "/tmp":     "hdfs://nn-hostel:8020/tmp"}

def resolve(path):
    best = max((m for m in mounts if path == m or path.startswith(m + "/")), key=len, default=None)
    if best is None:
        raise FileNotFoundError(path + " is not under any mount point")
    return mounts[best] + path[len(best):]

def rename(src, dst):
    s, d = resolve(src), resolve(dst)
    if s.split("/")[2] != d.split("/")[2]:
        return "mv: Renames across Mount points not supported"
    return f"renamed inside {s.split('/')[2]}"

for p in ["/canteen/orders.csv", "/hostel/rooms.csv", "/tmp/x"]:
    print(f"{p:22} -> {resolve(p)}")
print(rename("/canteen/orders.csv", "/hostel/orders.csv"))
print(rename("/hostel/rooms.csv", "/tmp/rooms.csv"))
''',
    anno=[
        ('    best = max((m for m in mounts if path == m or path.startswith(m + "/")), key=len, default=None)', 'The longest matching mount point wins, so nested mounts (e.g. <code>/data</code> and <code>/data/logs</code>) work.'),
        ('    if s.split("/")[2] != d.split("/")[2]:', 'Different NameNodes behind source and target: no single NameNode can rename atomically. Our cluster printed exactly this message.'),
        ('print(rename("/hostel/rooms.csv", "/tmp/rooms.csv"))', 'Interesting: <code>/hostel</code> and <code>/tmp</code> are on the same NameNode here, so the logic allows it. Real ViewFS is stricter by default and refuses renames between any two different mount points.'),
    ],
    tasks=[
        dict(label='1 · Route paths', hint='Press <b>Run</b>. Add a mount <code>/exams</code> on a third NameNode and route <code>/exams/2026/results.csv</code>.', code=None),
        dict(label='2 · NameNode memory', hint='Rule of thumb: about 150 bytes of NameNode heap per object (file, folder or block). How much heap do 40 crore files with 1.2 blocks each need?',
             code='''files = 400_000_000
objects = files + files * 1.2            # files + blocks (folders ignored)
heap_gb = objects * 150 / 1024**3
print(f"{objects:,.0f} objects -> about {heap_gb:.0f} GB of NameNode heap")
'''),
        dict(label='3 · Split the namespace', hint='Split the folders across 2 NameNodes so object counts are as even as possible (greedy: biggest first to the emptier one).',
             code='''folders = {"/warehouse": 120_000_000, "/user": 60_000_000, "/tmp": 90_000_000, "/logs": 70_000_000, "/ml": 40_000_000}
nns = {"nn1": [], "nn2": []}
load = {"nn1": 0, "nn2": 0}
for f, n in sorted(folders.items(), key=lambda kv: -kv[1]):
    target = min(load, key=load.get)
    nns[target].append(f); load[target] += n
print(nns)
print({k: f"{v / 1e6:.0f} M objects" for k, v in load.items()})
'''),
        dict(label='4 · Block pools on one DataNode', hint='A DataNode stores one folder per block pool. Given the sizes per pool, compute each pool’s share of the disk.',
             code='''pools = {"BP-1200013783 (canteen)": 2.5, "BP-343349822 (hostel)": 0.572}   # MB, from du -sh
total = sum(pools.values())
for p, mb in pools.items():
    print(f"{p:26} {mb:5.2f} MB  {mb / total:.0%}")
'''),
        dict(label='5 · Spot the error', hint='This path is not under any mount point, so resolving it raises an error, like ViewFS does. Add a mount for <code>/research</code>.',
             code='''mounts = {"/canteen": "hdfs://nn-canteen:8020/canteen"}
path = "/research/data.csv"
match = [m for m in mounts if path.startswith(m + "/")]
print(mounts[match[0]])
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: two NameNodes, three DataNodes',
    intro='<p>Create a folder <code>hdfs-fed-lab</code> with <code>config</code>, <code>docker-compose.yaml</code>, <code>nnf.sh</code>, and a subfolder <code>client-conf</code> containing the client <code>core-site.xml</code> (ViewFS mount table) shown below. Run <code>chmod 777 client-conf</code>, start with <code>docker compose -p lab72 up -d --scale datanode=3</code>, wait 45 seconds, then run <code>federation_lab.sh</code>.</p>',
    items=[
        dict(title='Lab files', file='docker-compose.yaml',
             cmd=rd('lab/docker-compose.yaml') + '\n# ---- config ----\n' + rd('lab/config') + '\n# ---- nnf.sh ----\n' + rd('lab/nnf.sh') + '\n# ---- client-conf/core-site.xml ----\n' + rd('lab/client-core-site.xml'),
             output='''lab72-datanode-1 Up 45 seconds
lab72-datanode-2 Up 45 seconds
lab72-datanode-3 Up 45 seconds
lab72-nn-canteen-1 Up 45 seconds
lab72-nn-hostel-1 Up 46 seconds
$ docker exec lab72-datanode-1 ls /tmp/hadoop-hadoop/dfs/data/current/
BP-1200013783-172.21.0.3-1792598083981
BP-343349822-172.21.0.2-1792598083339
VERSION''',
             note='Real output. ViewFS mount entries contain “/”, which Docker env files don\'t allow, so the mount table lives in a separate client config folder used with <code>HADOOP_CONF_DIR=/opt/client-conf</code>.'),
        dict(title='The federation experiments', file='federation_lab.sh',
             cmd=rd('federation_lab.sh') + '\n# Run:  bash federation_lab.sh',
             output=rd('tx_fed.txt').strip(),
             note='Real output. Your block pool IDs and IP addresses will differ.'),
    ],
)

TRACE = dict(
    heading='A DataNode registering with two NameNodes',
    intro='<p>At start-up, a DataNode reads every nameservice from its configuration and registers with each, creating one block pool folder per NameNode.</p>',
    code='''nameservices = {"nsc": "BP-1200013783", "nsh": "BP-343349822"}
cluster_id = "campus-cluster"
folders = []
for ns, pool in nameservices.items():
    nn_cluster = "campus-cluster"
    if nn_cluster == cluster_id:
        folders.append(pool)
print("block pool folders:", folders)
''',
    notes={4: 'One per NameNode :: The DataNode runs a separate service thread for each nameservice.',
           6: 'Same cluster :: A NameNode with a different cluster ID would be rejected.'},
)

WORKED_INTRO = 'Three federation calculations: when one NameNode is too small, how to split, and what federation buys in failure isolation. Each runs live and is traced in memory.'
EXAMPLES = [
    dict(level='b', tag='Sizing · heap', title='When does one NameNode stop being enough?',
         problem='<p>A NameNode server can give the NameNode at most 192 GB of heap. Using the rule of thumb of 150 bytes per object, how many objects fit, and how many files is that if, on average, each file brings 0.1 folders and 1.5 blocks with it?</p>',
         inp='192 GB · 150 B/object · 2.6 objects per file',
         approach=['Objects = heap / 150 bytes.',
                   'Each file costs 1 + 0.1 + 1.5 = 2.6 objects.',
                   'Files = objects / 2.6.'],
         code='''heap = 192 * 1024**3
objects = heap / 150
print(f"{objects / 1e9:.2f} billion objects -> about {objects / 2.6 / 1e6:.0f} million files")
''', notes={2: 'Rule of thumb :: Real per-object memory varies with path lengths, replication and version.'},
         tryit='Small files make it worse: 1 GB stored as 1,000 files costs about 1,000× the NameNode memory of one 1 GB file (Lesson 7.5).'),
    dict(level='i', tag='Design · split', title='Two namespaces from five top-level folders',
         problem='<p>Split /warehouse (12 crore objects), /tmp (9 crore), /logs (7 crore), /user (6 crore) and /ml (4 crore) between two NameNodes as evenly as possible, keeping each folder whole.</p>',
         inp='5 folders, 38 crore objects',
         approach=['Sort folders by size.',
                   'Give each to the NameNode with fewer objects so far.',
                   'Compare totals.'],
         code='''folders = [("/warehouse", 12), ("/tmp", 9), ("/logs", 7), ("/user", 6), ("/ml", 4)]
a, b = [], []
for f, n in folders:
    (a if sum(x[1] for x in a) <= sum(x[1] for x in b) else b).append((f, n))
print("nn1:", a, sum(x[1] for x in a), "crore")
print("nn2:", b, sum(x[1] for x in b), "crore")
''', notes={3: 'Greedy :: Largest first, into the lighter side.'},
         tryit='Real splits also consider who uses what: keep folders that jobs rename between in the same namespace.'),
    dict(level='a', tag='Availability · isolation', title='How much keeps working when one NameNode fails?',
         problem='<p>Jobs touch namespaces in this pattern: 50% only nsA, 30% only nsB, 20% both. If nsA becomes unavailable (and is not HA), what fraction of jobs can still run?</p>',
         inp='50% A · 30% B · 20% both',
         approach=['Jobs needing A fail.',
                   'Only B-only jobs survive.',
                   'Compare with a single NameNode, where all fail.'],
         code='''only_a, only_b, both = 0.5, 0.3, 0.2
print(f"federated: {only_b:.0%} of jobs keep running; single NameNode: 0%")
''', notes={1: 'Dependencies :: Jobs spanning namespaces share the risk of both.'},
         tryit='Federation limits the blast radius; HA on each nameservice removes most of the risk.'),
]

QUIZ = mix([
    dict(q='What problem does HDFS federation mainly solve?', options=['NameNode failure', 'The limits of a single NameNode (memory and RPC load for one namespace)', 'DataNode disk failures', 'Slow networks'], answer=1,
         why='HA solves failure; federation scales the namespace across NameNodes.'),
    dict(q='In federation, what do the NameNodes share?', options=['The namespace', 'DataNodes and the cluster ID', 'The edit log', 'Nothing at all'], answer=1,
         why='Each has its own namespace and block pool; storage is shared.'),
    dict(q='What is a block pool?', options=['A cache of hot blocks', 'The set of blocks belonging to one namespace, stored in a BP-… folder on each DataNode', 'A group of DataNodes', 'A replication policy'], answer=1,
         why='Our DataNode had two: BP-1200013783-… and BP-343349822-….'),
    dict(q='How do clients see one directory tree over several NameNodes?', options=['They can\'t', 'ViewFS mount table or Router-Based Federation', 'By listing each NameNode separately only', 'Through the JournalNodes'], answer=1,
         why='ViewFS is client-side; RBF routers hold the mount table centrally.'),
    dict(q='What happened when we moved /canteen/orders.csv to /hostel/?', options=['It moved instantly', 'mv: Renames across Mount points not supported', 'It copied silently', 'The NameNode crashed'], answer=1,
         why='A rename is a single-NameNode metadata operation.'),
    dict(q='With nn-canteen stopped, what still worked?', options=['Nothing', '/hostel', '/canteen', 'Only the root /'], answer=1,
         why='Each namespace fails independently.'),
    dict(q='Can a federated nameservice also be HA?', options=['No, they are exclusive', 'Yes, each nameservice can have an active and standby NameNode', 'Only in Hadoop 1', 'Only with ViewFS'], answer=1,
         why='HA and federation are orthogonal and are often combined.'),
    dict(q='Why must all federated NameNodes be formatted with the same cluster ID?', options=['For licensing', 'DataNodes only serve NameNodes of their own cluster', 'To share the edit log', 'It isn\'t needed'], answer=1,
         why='Our NameNodes were formatted with -clusterId campus-cluster.'),
])

REVISION = [
    'Federation = several <b>independent NameNodes</b>, each with its own namespace and <b>block pool</b>, sharing DataNodes.',
    'Same <b>cluster ID</b> (<code>-clusterId</code> at format); <code>dfs.nameservices</code> lists all; DataNodes register with each.',
    'DataNode disk: one <code>current/BP-…</code> folder per namespace (lab: 2.5 M canteen, 572 K hostel).',
    'Unified view: <b>ViewFS</b> (client mount table) or <b>RBF</b> (routers + state store).',
    'No rename across namespaces (“Renames across Mount points not supported”); copy + delete instead.',
    'Failure isolation: one NameNode down affects only its namespace; combine with HA per nameservice.',
    'Why: NameNode heap ~150 bytes/object (rule of thumb) and RPC load; split busy or small-file-heavy trees.',
]
FAQ = [
    ('What is HDFS federation?', 'A way to scale the HDFS namespace by running multiple independent NameNodes. Each manages its own namespace and block pool, while all of them share the same DataNodes, which store blocks for every pool in separate directories. Clients see a unified namespace through ViewFS or Router-Based Federation.'),
    ('What is the difference between HDFS HA and federation?', 'HA provides availability for one namespace: an active and standby NameNode hold the same metadata and the standby takes over on failure. Federation provides scalability and isolation: several NameNodes hold different parts of the namespace. They can be combined, with each federated nameservice running as an HA pair.'),
    ('What is ViewFS?', 'A client-side file system (viewfs://) that uses a mount table in the client configuration to map paths like /canteen and /hostel to directories in different HDFS namespaces, giving one logical tree.'),
    ('What is Router-Based Federation?', 'A server-side approach introduced in Hadoop 2.9/3.0: stateless router processes accept client requests on one address and forward them to the right nameservice using a mount table kept in a shared state store. Mount points can be changed centrally without updating clients.'),
    ('Does federation increase the size limit of a single directory tree?', 'No. Each namespace still lives in one NameNode. Federation helps when the overall namespace can be split into separate subtrees across NameNodes.'),
]

PRACTICE_INTRO = 'Federation exercises using the real IDs, sizes and messages from the lab.'
PROBLEMS = [
    dict(level='easy', title='Parse a block pool ID', stmt='Extract the random part, the NameNode IP and the creation time (ms) from a block pool ID.', inp='BP-1200013783-172.21.0.3-1792598083981',
         code='''bp = "BP-1200013783-172.21.0.3-1792598083981"
_, rnd, ip, ms = bp.split("-")
print(rnd, ip, ms)
''', explain='1200013783, 172.21.0.3 (the NameNode that created it), 1792598083981 ms since 1970.'),
    dict(level='easy', title='Which NameNode?', stmt='Using the lab mount table, print which NameNode serves /tmp/x.', inp='/canteen, /hostel, /tmp mounts',
         code='''mounts = {"/canteen": "nn-canteen", "/hostel": "nn-hostel", "/tmp": "nn-hostel"}
print(next(nn for m, nn in mounts.items() if "/tmp/x".startswith(m + "/")))
''', explain='nn-hostel: /tmp was mounted on the hostel namespace.'),
    dict(level='easy', title='Pool shares', stmt='From du -sh: 2.5 M and 572 K. What percentage of the DataNode\'s HDFS data belongs to each pool?', inp='2.5 MB, 0.572 MB',
         code='''a, b = 2.5, 0.572
print(f"canteen {a / (a + b):.0%}, hostel {b / (a + b):.0%}")
''', explain='About 81% and 19%: one disk, two namespaces.'),
    dict(level='medium', title='Heap check', stmt='A NameNode has 120 GB of heap. Using 150 bytes per object, will 50 crore objects fit?', inp='120 GB · 50 crore',
         code='''need = 500_000_000 * 150 / 1024**3
print(f"needs {need:.0f} GB -> {'fits' if need <= 120 else 'does not fit: federate or reduce objects'}")
''', explain='About 70 GB: fits, with headroom for growth and GC.'),
    dict(level='medium', title='Cross-mount moves', stmt='List which of these moves are renames (same mount) and which need copy + delete.', inp='3 moves',
         code='''moves = [("/canteen/a", "/canteen/archive/a"), ("/canteen/a", "/hostel/a"), ("/hostel/r", "/hostel/old/r")]
mount = lambda p: "/" + p.split("/")[1]
for s, d in moves:
    print(s, "->", d, ":", "rename" if mount(s) == mount(d) else "copy + delete")
''', explain='Only the canteen→hostel move crosses mount points.'),
    dict(level='medium', title='Live DataNodes per NameNode', stmt='Parse the report lines and check both NameNodes see the same number of DataNodes.', inp='two lines',
         code='''lines = ["nn-canteen: Live datanodes (3):", "nn-hostel: Live datanodes (3):"]
counts = [int(l.split("(")[1].split(")")[0]) for l in lines]
print(counts, "same" if len(set(counts)) == 1 else "different")
''', explain='3 and 3: every DataNode serves both namespaces.'),
    dict(level='business', title='Bigger server or federation?', stmt='Option A: one NameNode server with 512 GB RAM, ₹40 lakh. Option B: two 256 GB servers, ₹14 lakh each, plus ₹3 lakh/year extra operations for 3 years. Which is cheaper over 3 years?', inp='A ₹40 lakh · B 2 × ₹14 lakh + 3 × ₹3 lakh',
         code='''a = 40
b = 2 * 14 + 3 * 3
print(f"A: Rs {a} lakh, B: Rs {b} lakh ->", "federation cheaper" if b < a else "bigger server cheaper")
''', explain='₹37 lakh vs ₹40 lakh (illustrative), and B also isolates failures and avoids one giant JVM heap with long GC pauses.'),
    dict(level='advanced', title='Mount table resolver', stmt='Implement longest-prefix resolution with nested mounts /data → nn1 and /data/logs → nn2.', inp='2 nested mounts',
         code='''mounts = {"/data": "nn1", "/data/logs": "nn2"}
def ns(path):
    return mounts[max((m for m in mounts if path == m or path.startswith(m + "/")), key=len)]
for p in ["/data/sales/x", "/data/logs/app.log", "/data/logsheet.csv"]:
    print(p, "->", ns(p))
''', explain='/data/logs/app.log goes to nn2; /data/logsheet.csv still goes to nn1 because the match is on whole path components.'),
]

SCN_INTRO = 'Federation questions appear in senior Hadoop administrator and platform architect interviews.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">HDFS · concepts</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“HA and federation: what's the difference?”</h4>
      <p class="scn__situation">Often asked right after HA.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> availability vs scalability.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>HA: same namespace on an active and standby NameNode; protects against NameNode failure.</li>
          <li>Federation: different namespaces on independent NameNodes sharing DataNodes; scales metadata and isolates workloads.</li>
          <li>They combine: each federated nameservice can be an HA pair.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Operations · capacity</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>NameNode heap at 90% and GC pauses growing</h4>
      <p class="scn__situation">A 600-million-object namespace on one HA pair; RPC queue times are rising during the day.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> options in order of effort.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>First reduce objects: find small-file-heavy folders, compact them, clean /tmp and old data, use HAR or table compaction.</li>
          <li>Tune heap and GC; consider Observer NameNodes for read-heavy load.</li>
          <li>If growth continues, federate: move high-churn trees (/tmp, staging, a big tenant) to a new nameservice, behind routers so paths don't change.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Design · ViewFS vs RBF</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Rolling out federation to 2,000 client machines</h4>
      <p class="scn__situation">You add a second nameservice. Edge nodes, Spark jobs, Airflow workers and BI tools all access HDFS.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> client configuration management.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>With ViewFS, every client needs the new mount table; any stale config breaks paths. Manageable with strong config management.</li>
          <li>With Router-Based Federation, clients point to the routers once; mount changes are made centrally with <code>dfsrouteradmin</code>.</li>
          <li>Run several routers behind a nameservice for availability, and monitor the state store.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Troubleshooting</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>A new NameNode is up, but no DataNode registers with it</h4>
      <p class="scn__situation">The second NameNode shows 0 live DataNodes; DataNode logs show an incompatible cluster ID.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> cluster ID and block pools.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>The new NameNode was formatted without the existing cluster ID, so DataNodes refuse it.</li>
          <li>Reformat the empty new NameNode with <code>-clusterId &lt;existing id&gt;</code> (from any DataNode's VERSION file), add it to <code>dfs.nameservices</code>, and refresh DataNodes (<code>dfsadmin -refreshNamenodes</code>).</li>
          <li>Never reformat a NameNode that already holds data.</li>
        </ul>
      </div></details>
    </article>
'''
