import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()

META = dict(
    module='12-multiple-clusters-and-operations', lesson='01-why-companies-run-many-clusters', n='12.1',
    module_label='Module 12 · Multiple clusters and operations',
    title='Why companies run many clusters',
    desc='Why organisations run fleets of Hadoop clusters: production, disaster recovery, staging, development, analytics sandboxes and ephemeral cloud clusters; isolation, change control, data residency (RBI payment-data storage rule), scale, mergers. What clusters share (Kerberos trust, Ranger, metastore, catalog, monitoring), federation vs separate clusters, fleet inventory from NameNode JMX on a real two-cluster lab, and the name-clash mistake that broke our first attempt. Architecture diagram, animations, quiz and interview scenarios.',
    og_desc='One cluster is never enough. Build a two-cluster fleet, hit a real network mistake, and learn why banks run prod, DR, staging and sandboxes.',
    minutes=26, level='Intermediate',
    lead='Large companies rarely run one Hadoop cluster. They run a fleet: production, a disaster-recovery copy in another region, staging, development and sandboxes, sometimes split by business unit or by country. This lesson explains why, what the clusters must share, what a fleet costs, and builds a two-cluster fleet in our lab, including the mistake we made on the way.',
    chips=['Two real clusters', 'Architecture diagram + 2 animations', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='A fleet inventory and a cluster decision helper',
    intro='<p>The first part mimics <code>fleet.py</code>: one record per NameNode, then a summary per cluster ID (federated namespaces share one). The second part turns the reasons from this lesson into a simple decision helper.</p>',
    code='''fleet = [  # what fleet.py printed in our lab
    {"name": "prod (lab8)", "cluster": "CID-01fef50a", "version": "3.5.0", "dns": 3, "files": 1680, "used_mb": 4769},
    {"name": "dr ns canteen", "cluster": "campus-cluster", "version": "3.5.0", "dns": 3, "files": 15, "used_mb": 541},
    {"name": "dr ns hostel", "cluster": "campus-cluster", "version": "3.5.0", "dns": 3, "files": 4, "used_mb": 541},
]
clusters = {}
for nn in fleet:
    c = clusters.setdefault(nn["cluster"], {"namenodes": 0, "files": 0, "used_mb": nn["used_mb"], "dns": nn["dns"]})
    c["namenodes"] += 1
    c["files"] += nn["files"]
for cid, c in clusters.items():
    print(f"{cid:15} {c['namenodes']} NameNode(s)  {c['dns']} DataNodes  {c['files']:>5} files  {c['used_mb']:>5} MB")
versions = {nn["version"] for nn in fleet}
print("versions in the fleet:", versions, "-> no drift" if len(versions) == 1 else "-> DRIFT")
''',
    anno=[
        ('    c = clusters.setdefault(nn["cluster"], {"namenodes": 0, "files": 0, "used_mb": nn["used_mb"], "dns": nn["dns"]})', 'Federated namespaces share DataNodes and the cluster ID, so we count their storage once.'),
        ('versions = {nn["version"] for nn in fleet}', 'A fleet report always checks for version drift: one forgotten cluster on an old release is a classic incident.'),
    ],
    tasks=[
        dict(label='1 · Fleet report', hint='Press <b>Run</b>. How many clusters and how many NameNodes does our lab fleet have?', code=None),
        dict(label='2 · Do we need another cluster?', hint='<b>Predict first:</b> which of these needs a new cluster and which only a new YARN queue?',
             code='''def decide(need):
    new_cluster = {"survive a data-centre loss", "rehearse an upgrade", "payment data must stay in India (prod is in Singapore)",
                   "NameNode memory is full", "developers break things"}
    return "new cluster" if need in new_cluster else "a queue or quota is enough"
for need in ["survive a data-centre loss", "fair CPU for two teams", "rehearse an upgrade",
             "payment data must stay in India (prod is in Singapore)", "limit one team's disk use"]:
    print(f"{need:54} -> {decide(need)}")
'''),
        dict(label='3 · Drift check', hint='Add a fourth cluster still on 3.3.6 to the list and print which clusters are not on the newest version.',
             code='''fleet = {"prod": "3.5.0", "dr": "3.5.0", "staging": "3.5.0", "sandbox": "3.3.6"}
newest = max(fleet.values(), key=lambda v: tuple(map(int, v.split("."))))
print("behind:", [c for c, v in fleet.items() if v != newest])
'''),
        dict(label='4 · Cost of copies', hint='Prod holds 6 PB raw (replication 3). DR keeps 40% of the data, staging a 2% sample, the sandbox 10%. How much raw storage does the fleet need in total?',
             code='''prod = 6.0
copies = {"dr": 0.40, "staging": 0.02, "sandbox": 0.10}
total = prod + sum(prod * share for share in copies.values())
print(f"fleet raw storage: {total:.2f} PB ({total / prod:.0%} of prod)")
'''),
        dict(label='5 · Spot the error', hint='This script looks up a cluster by host name, but two clusters both call their NameNode "namenode". Make the key unique.',
             code='''hosts = {"namenode": "prod", "namenode": "dr", "nn-canteen": "dr"}
print(len(hosts), "clusters found")
assert len(set(hosts.values())) == len(hosts), "two clusters share a host name"
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: a two-cluster fleet',
    intro='<p>Start the Module 8 lab (prod) and the Lesson 7.2 federation lab (DR). <code>join_clusters.sh</code> connects only the prod workers to the DR network, then <code>fleet.py</code> runs on a worker, which can see both clusters. Run <code>docker cp fleet.py lab8-worker1-1:/tmp/</code> first.</p>',
    items=[
        dict(title='Join the clusters and take inventory', file='fleet.py',
             cmd=rd('lab/fleet.py') + '\n# ---- join_clusters.sh (run on your PC) ----\n' + '\n'.join('# ' + l for l in rd('lab/join_clusters.sh').strip().split('\n')) + '\n\n# Then:\n#   docker cp fleet.py lab8-worker1-1:/tmp/\n#   docker exec lab8-worker1-1 python3 /tmp/fleet.py',
             output=rd('tx121.txt').strip(),
             note='Real output. Your cluster IDs and file counts will differ. If a job fails with “Connection refused” to an address you don\'t recognise, a container that runs a server (NameNode, ResourceManager) has joined a second network: disconnect it.'),
    ],
)

TRACE = dict(
    heading='Grouping NameNodes into clusters',
    intro='<p>Three NameNodes, two clusters: the cluster ID decides which ones belong together.</p>',
    code='''nns = [("prod", "CID-01"), ("canteen", "campus"), ("hostel", "campus")]
by_cluster = {}
for name, cid in nns:
    by_cluster.setdefault(cid, []).append(name)
for cid, names in by_cluster.items():
    print(cid, names)
''',
    notes={4: 'Group :: Same cluster ID = same DataNodes (federation). Different ID = a separate failure domain.'},
)

WORKED_INTRO = 'Four fleet decisions from different industries: when to add a cluster, what DR costs, and how many clusters to run.'
EXAMPLES = [
    dict(level='b', tag='Decision · retail', title='Queue or cluster for the analysts?',
         problem='<p>A retail chain\'s analysts run heavy ad-hoc queries on the production cluster. Twice this month they filled HDFS with temporary tables and nightly sales loads failed. Is a separate YARN queue enough?</p>',
         inp='problem: full HDFS, not CPU',
         approach=['Queues share CPU and memory, not HDFS space or NameNode load.',
                   'A space quota on their folder would stop the disk problem.',
                   'If they also need different versions or tools, give them a sandbox cluster.'],
         code='''problems = {"CPU contention": "queue", "HDFS filled": "space quota", "NameNode overloaded": "separate cluster",
            "needs new Spark version": "separate cluster"}
for p in ["HDFS filled", "CPU contention"]:
    print(f"{p:22} -> {problems[p]}")
''', notes={1: 'Match :: Each kind of interference has its own cheapest fix.'},
         tryit='Add “NameNode overloaded by millions of temp files” and see why that one needs a separate cluster.'),
    dict(level='i', tag='DR · bank', title='How big must the DR cluster be?',
         problem='<p>A bank\'s prod cluster stores 3 PB of data (before replication). Regulators require that 25% of it, the critical tables, be restorable in another city. DR uses replication 3, disks are 80% fillable. How much raw disk does DR need?</p>',
         inp='3 PB · 25% critical · replication 3 · 80% fill',
         approach=['Critical data = 3 × 0.25.', 'Raw = data × replication.', 'Divide by the fill limit.'],
         code='''data = 3.0 * 0.25
raw = data * 3 / 0.80
print(f"critical data {data:.2f} PB -> {raw:.2f} PB of raw disk in the DR cluster")
''', notes={2: 'Headroom :: Never plan to fill disks to 100%; HDFS and Linux need free space.'},
         tryit='If the DR site uses erasure coding RS-6-3 (1.5×) for cold critical data, how much disk is saved?'),
    dict(level='i', tag='Change control · telecom', title='Rehearse the upgrade',
         problem='<p>An upgrade on a telecom operator\'s prod cluster takes 6 hours of downtime if done in place, with a 20% chance of a failed job that costs another 4 hours. A blue-green move to a new cluster costs 2 hours of cut-over. Which has the smaller expected downtime?</p>',
         inp='in place 6 h + 20% × 4 h · blue-green 2 h',
         approach=['Expected in place = 6 + 0.2 × 4.', 'Blue-green = 2 (old cluster kept as fallback).', 'Compare.'],
         code='''in_place = 6 + 0.2 * 4
blue_green = 2
print(f"in place {in_place:.1f} h expected downtime, blue-green {blue_green} h (plus a second cluster for a month)")
''', notes={1: 'Risk :: Expected value = cost × probability.'},
         tryit='Add the cost of the extra hardware for a month and decide which is cheaper overall.'),
    dict(level='a', tag='Fleet design · e-commerce', title='How many clusters for a marketplace?',
         problem='<p>A marketplace needs: an order pipeline with a 99.9% SLA, a regulator-mandated copy in another city, data scientists training models nightly, developers, and an India-only rule for payment data (all its data is Indian). Propose the fleet and count clusters.</p>',
         inp='5 needs',
         approach=['Map each need to “new cluster” or “share an existing one”.', 'India-only is already satisfied if all clusters are in India.', 'Count.'],
         code='''needs = {"order pipeline SLA": "prod", "copy in another city": "dr", "nightly model training": "sandbox",
         "developers": "dev", "payment data in India": "prod (already in India)"}
clusters = {v.split(" ")[0] for v in needs.values()}
print(sorted(clusters), "->", len(clusters), "clusters, plus staging for upgrades =", len(clusters) + 1)
''', notes={2: 'Reuse :: A rule doesn\'t always need its own cluster; check whether an existing one already satisfies it.'},
         tryit='The company expands to Singapore with local customers. Which need appears, and does it add a cluster?'),
]

QUIZ = mix([
    dict(q='Which problem does a second cluster in another region solve that NameNode HA does not?', options=['A NameNode process crash', 'Losing a whole data centre', 'A slow map task', 'Too many small files'], answer=1,
         why='HA protects against a failed NameNode; DR protects against a lost site.'),
    dict(q='Why do companies keep a staging cluster?', options=['To store backups', 'To rehearse upgrades and releases before prod', 'To run the biggest jobs', 'To hold the Kerberos KDC'], answer=1,
         why='Same versions as prod, small, with masked sample data.'),
    dict(q='What do federated namespaces share that separate clusters do not?', options=['Nothing', 'DataNodes and the cluster ID', 'Only the web UI', 'Only Kerberos'], answer=1,
         why='Our lab: canteen and hostel both report clusterId campus-cluster.'),
    dict(q='Which tool usually copies data between clusters?', options=['hdfs dfs -cp', 'DistCp', 'fsck', 'Balancer'], answer=1,
         why='A MapReduce job that copies in parallel (Lesson 12.2).'),
    dict(q='Why did our first attempt to join two lab clusters fail?', options=['DistCp was not installed', 'The client resolved resourcemanager to an address on the other network where nothing listened', 'The DR cluster was full', 'Kerberos was missing'], answer=1,
         why='“Retrying connect to server: resourcemanager/172.19.0.10:8032 … Connection refused”.'),
    dict(q='Which need is best solved by a YARN queue rather than a new cluster?', options=['Data must stay in India', 'Fair sharing of CPU and memory between two teams', 'Surviving a flood', 'Testing a new Hadoop version'], answer=1,
         why='Queues share compute inside one cluster (Lesson 11.3).'),
    dict(q='Which service is typically shared by all clusters of a fleet?', options=['The NameNode', 'Kerberos identity (with trust) and Ranger policies', 'The DataNodes', 'The shuffle'], answer=1,
         why='So one login and one rule book work everywhere.'),
    dict(q='What is configuration drift?', options=['A slow network', 'Clusters that should be alike gradually getting different settings or versions', 'Data moving between racks', 'A NameNode failover'], answer=1,
         why='Avoid it by generating every cluster\'s configuration from one repository.'),
])

REVISION = [
    'A <b>fleet</b> = several independent clusters: prod, DR, staging, dev, sandboxes, ephemeral cloud clusters.',
    'Reasons: site failure (DR), change control (staging), isolation, data residency (e.g. RBI payment-data storage in India), NameNode scale, mergers, budgets.',
    'Queues share compute; quotas limit space; only a separate cluster gives a separate failure domain.',
    'Shared services: Kerberos realms with trust, Ranger, Hive Metastore/catalog, monitoring.',
    'Federation (7.2) = one cluster ID, shared DataNodes; separate clusters fail independently.',
    'Lab: prod CID-01fef50a (3 DNs, 1,680 files) + DR campus-cluster (2 namespaces); joining every container to both networks broke name resolution.',
    'Unique host names, nameservice IDs and cluster IDs across the fleet; configuration as code to avoid drift.',
]
FAQ = [
    ('Why do companies run multiple Hadoop clusters?', 'To survive the loss of a data centre (a DR cluster in another region), to test upgrades and code safely (staging and development clusters), to isolate workloads that interfere with each other, to meet data-residency rules, to work around the scale limits of one NameNode, and for organisational reasons such as mergers or separate budgets. Data moves between them with DistCp, and they share identity, authorization and metadata services.'),
    ('What is the difference between HDFS federation and multiple clusters?', 'Federation runs several NameNodes over one shared set of DataNodes with one cluster ID, to scale the namespace. Multiple clusters have separate NameNodes, DataNodes and cluster IDs, so they fail independently and can be in different places, versions or legal zones.'),
    ('What is a disaster recovery cluster in Hadoop?', 'A second cluster, usually in another region, that receives regular copies of critical data (with DistCp, often snapshot-based) and can take over the important jobs if the production site is lost. Its recovery point is the time since the last successful copy.'),
    ('How do users log in to many Hadoop clusters?', 'Each cluster uses Kerberos, either in one shared realm or in separate realms with cross-realm trust, so a user\'s ticket is accepted on every cluster. Authorization is kept consistent with central Ranger policies.'),
    ('Is it better to have one big cluster or many small ones?', 'One big cluster uses hardware more efficiently and keeps data in one place; many clusters give isolation, separate change schedules, DR and legal separation at the cost of copies and operational work. Most large organisations combine a few big shared clusters with smaller special-purpose ones.'),
]

PRACTICE_INTRO = 'Fleet exercises using our lab numbers and realistic company scenarios.'
PROBLEMS = [
    dict(level='easy', title='Count the fleet', stmt='From the fleet report, how many clusters and how many NameNodes are there?', inp='3 lines, 2 cluster IDs',
         code='''ids = ["CID-01fef50a", "campus-cluster", "campus-cluster"]
print(len(set(ids)), "clusters,", len(ids), "NameNodes")
''', explain='2 clusters and 3 NameNodes: the DR cluster is federated with two namespaces.'),
    dict(level='easy', title='Files per cluster', stmt='Add up the files per cluster ID.', inp='1,680 · 15 · 4',
         code='''print("prod:", 1680, "dr:", 15 + 4)
''', explain='prod 1,680 and DR 19 files: DR holds only what we chose to protect.'),
    dict(level='easy', title='Queue, quota or cluster?', stmt='Classify: (a) one team uses all CPU at night, (b) one team fills the disks, (c) the company must survive a city-wide power cut.', inp='3 needs',
         code='''for need, fix in [("CPU at night", "queue"), ("fills the disks", "space quota"), ("city-wide power cut", "DR cluster")]:
    print(f"{need:20} -> {fix}")
''', explain='Use the cheapest tool that actually separates the thing that interferes.'),
    dict(level='medium', title='Name clash detector', stmt='Given host names per cluster, report any host name used by more than one cluster.', inp='3 clusters',
         code='''clusters = {"lab8": ["namenode", "resourcemanager", "worker1"], "lab5": ["namenode", "datanode"],
            "lab72": ["nn-canteen", "nn-hostel", "datanode"]}
seen = {}
for c, hosts in clusters.items():
    for h in hosts:
        seen.setdefault(h, []).append(c)
print({h: cs for h, cs in seen.items() if len(cs) > 1})
''', explain='namenode (lab8, lab5) and datanode (lab5, lab72) clash. Our lab hit the first one.'),
    dict(level='medium', title='Copies make a fleet expensive', stmt='Prod: 2 PB of data. DR copies 50%, sandbox 15%, staging 1%, all with replication 3. Raw disk for the fleet?', inp='2 PB · shares',
         code='''data = 2.0
shares = {"prod": 1.0, "dr": 0.5, "sandbox": 0.15, "staging": 0.01}
print(f"{sum(data * s * 3 for s in shares.values()):.2f} PB raw")
''', explain='9.96 PB raw for 2 PB of data: copies are the hidden cost of a fleet.'),
    dict(level='medium', title='Version drift', stmt='Find clusters not on the majority version.', inp='5 clusters',
         code='''from collections import Counter
v = {"prod": "3.5.0", "dr": "3.5.0", "staging": "3.5.0", "dev": "3.4.1", "sandbox": "3.3.6"}
major = Counter(v.values()).most_common(1)[0][0]
print("majority", major, "| drifted:", [c for c, x in v.items() if x != major])
''', explain='dev and sandbox have drifted; jobs tested there may behave differently on prod.'),
    dict(level='business', title='Is a DR cluster worth it?', stmt='A day of lost payment data costs an estimated ₹40 crore; the chance of losing the site in a year is 1%. A DR cluster costs ₹1.2 crore a year. Compare expected loss and cost (illustrative).', inp='₹40 crore · 1% · ₹1.2 crore',
         code='''expected_loss = 40 * 0.01
print(f"expected loss Rs {expected_loss:.1f} crore/year vs DR Rs 1.2 crore/year")
''', explain='₹0.4 crore expected loss looks smaller, but regulators require DR anyway, and the 1% event would be existential. Risk decisions are not only averages.'),
    dict(level='advanced', title='Ephemeral or always-on?', stmt='A nightly job needs 50 nodes for 3 hours. An always-on cluster costs ₹60 per node-hour; an ephemeral cloud cluster ₹90 per node-hour plus 15 minutes of start-up. Monthly cost of each (30 nights)?', inp='50 nodes · 3 h · ₹60 vs ₹90',
         code='''always = 50 * 24 * 30 * 60
ephemeral = 50 * (3 + 0.25) * 30 * 90
print(f"always-on Rs {always:,.0f}, ephemeral Rs {ephemeral:,.0f} per month")
''', explain='₹21.6 lakh vs ₹4.4 lakh: for a few hours a day, an ephemeral cluster is far cheaper even at a higher hourly rate.'),
]

SCN_INTRO = 'Fleet questions appear in senior data-engineering and platform interviews.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Architecture · basics</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“Why would a company need more than one Hadoop cluster?”</h4>
      <p class="scn__situation">A common opening question for platform roles.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> breadth of reasons.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Disaster recovery in another region; dev/test/staging for safe changes.</li>
          <li>Isolation of critical workloads from ad-hoc ones; data residency; NameNode scale limits.</li>
          <li>Data moves with DistCp; identity, Ranger policies and metadata are shared.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Design · trade-offs</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Analysts keep breaking the nightly pipeline</h4>
      <p class="scn__situation">Ad-hoc queries on prod fill HDFS and slow the NameNode at night.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> choosing the cheapest effective isolation.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Queues for compute, space and name quotas for their folders as a first step.</li>
          <li>If NameNode load or tooling needs differ, a sandbox cluster fed with curated copies.</li>
          <li>Keep one catalog and Ranger policies so tables mean the same thing in both.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Operations · incident</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>After connecting two clusters, jobs fail with “Connection refused”</h4>
      <p class="scn__situation">The RM is up; the error names an IP nobody recognises.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> networking and naming in multi-cluster setups.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Check what the host name resolves to on the client; a multi-homed server may be reached on an address it doesn't listen on.</li>
          <li>Use unique host names and nameservice IDs per cluster; bind servers to 0.0.0.0 or set bind-host properties if multi-homing is required.</li>
          <li>Only give the machines that need it (workers running copies) access to both networks.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Governance · fleet</span><span class="scn__tag scn__tag--level">Lead</span></div>
      <h4>Seven clusters, four Hadoop versions, nobody knows which</h4>
      <p class="scn__situation">You take over a platform team after an incident on a forgotten cluster.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> fleet management habits.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Build an inventory from each NameNode/RM (version, cluster ID, capacity, owner) and a single dashboard.</li>
          <li>Configuration as code, one release train, staging rehearsal for every upgrade.</li>
          <li>Retire or merge clusters without a clear purpose; document DR drills.</li>
        </ul>
      </div></details>
    </article>
'''
