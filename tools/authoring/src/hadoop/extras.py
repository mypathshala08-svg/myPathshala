#!/usr/bin/env python3
"""Build the Hadoop course's extra pages: courses/hadoop/playground/ and courses/hadoop/glossary/.
usage: python3 tools/authoring/src/hadoop/extras.py [SITE_ROOT]"""
import os, sys, json, html
E = html.escape
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
UP = '../../../'
COLOR = '#B45309'
SITE = 'https://myphatshala.in'


def shell(slug, title, desc, minutes, h1, lead, main, extra_head='', extra_js=''):
    url = f'{SITE}/courses/hadoop/{slug}/'
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)} | MyPhatshala</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{E(title)} · MyPhatshala">
<meta property="og:description" content="{E(desc)}">
<link rel="icon" href="{UP}assets/img/logo.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Fraunces:ital,opsz,wght@0,9..144,600;0,9..144,700;1,9..144,600&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{UP}assets/css/style.css">
<link rel="stylesheet" href="{UP}assets/css/lesson.css">
{extra_head}
<script src="{UP}assets/js/config.js"></script>
<script>try {{ const t = localStorage.getItem("mp-theme"); if (t) document.documentElement.dataset.theme = t; }} catch (e) {{}}</script>
</head>
<body style="--track:{COLOR}">
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{UP}" aria-label="MyPhatshala home"><img src="{UP}assets/img/logo.svg" width="34" height="34" alt=""><span>My<b>Phatshala</b></span></a>
    <nav class="nav" aria-label="Main">
      <a href="{UP}#tracks">All courses</a>
      <a href="../">Apache Hadoop syllabus</a>
      <button class="theme-btn" id="theme-btn" aria-label="Toggle dark mode"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg></button>
    </nav>
  </div>
</header>
<main id="main">
<section class="lesson-hero">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="{UP}">Home</a><span>›</span><a href="{UP}#track-big-data">Big Data Engineering</a><span>›</span><a href="../">Apache Hadoop</a><span>›</span><b>{E(h1)}</b></nav>
    <h1>{E(h1)}</h1>
    <p class="lead">{lead}</p>
    <div class="lesson-meta"><span>Apache Hadoop</span><span>⏱ {minutes} min</span><span>Free · no sign-up</span></div>
  </div>
</section>
<div class="wrap" style="padding-top:8px;padding-bottom:40px">
{main}
<div class="ad-slot" data-slot="bottom"></div>
</div>
</main>
<footer class="site-footer">
  <div class="wrap">
    <div><h4>MyPhatshala</h4><p>Free programming and IT lessons that show what happens behind the screen.</p></div>
    <div><h4>Learn</h4><a href="{UP}#tracks">All courses</a><a href="../">Apache Hadoop syllabus</a></div>
    <div><h4>Site</h4><a href="{UP}about.html">About</a><a href="{UP}contact.html">Contact</a><a href="{UP}privacy.html">Privacy policy</a><a href="{UP}disclaimer.html">Disclaimer</a></div>
    <div class="copyright">© MyPhatshala. All lesson content, diagrams and animations are original. Please do not copy without permission.</div>
  </div>
</footer>
{extra_js}
<script src="{UP}assets/js/ads.js"></script>
<script src="{UP}assets/js/site.js"></script>
</body>
</html>
'''


def csim(cfg):
    return '<div class="csim"><script type="application/json">' + json.dumps(cfg, ensure_ascii=False).replace('</', '<\\/') + '</script></div>'


# ------------------------------------------------------------------ playground
PG_MAIN = f'''<div class="ad-slot" data-slot="top"></div>
<section class="part">
  <h2>The full cluster</h2>
  <p>Three racks of three DataNodes, a client (edge node), two NameNodes (active and standby) and a ResourceManager. Everything you can do in the lessons is switched on here. Use the checklist as a guided tour, or just experiment.</p>
  {csim(dict(
    title='Cluster Playground: everything on',
    racks=3, nodes=3,
    features=['upload', 'fail', 'job', 'locality', 'chaos', 'ha', 'fsck'],
    preload=[dict(name='upi_txns_2025.csv', sizeMB=1024)],
    **{'try': [
        dict(text='Upload a 2 GB file with 128 MB blocks. Count the blocks and check that each has copies on two racks.', on='upload-done'),
        dict(text='Run the word count job. Note the data-local count in the Event log.', on='job-done'),
        dict(text='Untick “Move code to data” and run it again. Compare the two runs in <b>Job runs</b>.', on='job-done-nolocal'),
        dict(text='Click a DataNode to stop it, then <b>⏩ Skip to timeout</b> and watch re-replication.', on='rereplicated'),
        dict(text='Press <b>Stop active NameNode</b>. The standby takes over (High Availability).', on='nn-failover'),
        dict(text='Stop a whole rack plus one more node, skip to the timeout and run <b>hdfs fsck /</b>.', on='fsck'),
    ]},
  ))}
</section>
<section class="part">
  <h2>What each part of the picture means</h2>
  <div class="terms">
    <div class="term"><b>Client (edge node)</b><span>Where users run <code>hdfs</code> and <code>hadoop jar</code> commands. Not a DataNode, so the first replica of an upload goes to any node.</span></div>
    <div class="term"><b>NameNode</b><span>The HDFS master. Knows every file, its blocks and where each replica is (the metadata table on the right).</span></div>
    <div class="term"><b>Standby NameNode</b><span>Shown when High Availability is on. Takes over automatically if the active one fails.</span></div>
    <div class="term"><b>ResourceManager</b><span>The YARN master. Hands out containers for map and reduce tasks.</span></div>
    <div class="term"><b>Core switch / ToR switch</b><span>The network. Packets moving between racks pass through the core switch.</span></div>
    <div class="term"><b>DataNode box</b><span>A worker node. Coloured squares are block replicas (number = block of the file). The two bars at the bottom are task containers.</span></div>
    <div class="term"><b>Pink dots</b><span>Heartbeats from DataNodes to the NameNode, every 3 seconds (shown at 1× speed).</span></div>
    <div class="term"><b>Green / amber / red bars</b><span>Map tasks that are node-local / rack-local / off-rack. Violet bars are reducers.</span></div>
  </div>
  <p class="muted">Defaults follow real Hadoop: 128 MB blocks, replication 3, rack-aware placement, heartbeat every 3 seconds, a DataNode declared dead after 10 minutes 30 seconds. Transfer and task times are simplified, and some things that take minutes in a real cluster (such as noticing a lost task) happen immediately here.</p>
</section>
<section class="part">
  <h2>Lessons that use the playground</h2>
  <ul class="plain">
    <li><a href="../01-foundations/01-server-node-rack-and-data-centre/">1.1 Server, node, rack and data centre</a>: the pieces of a cluster</li>
    <li><a href="../01-foundations/02-what-is-a-cluster-masters-and-workers/">1.2 What is a cluster? Masters and workers</a>: break a worker during a job</li>
    <li><a href="../01-foundations/03-scale-out-in-practice/">1.3 Scale out in practice</a>: 3 vs 6 vs 9 nodes</li>
    <li><a href="../01-foundations/04-failures-are-normal/">1.4 Failures are normal</a>: how much can you break?</li>
    <li><a href="../01-foundations/05-move-the-code-not-the-data/">1.5 Move the code, not the data</a>: locality on and off</li>
    <li><a href="../02-why-hadoop/01-the-problem-hadoop-solved/">2.1 The problem Hadoop solved</a>: store, process, survive</li>
    <li><a href="../02-why-hadoop/03-how-hadoop-solved-each-problem/">2.3 How Hadoop solved each problem</a>: test every fix</li>
    <li><a href="../02-why-hadoop/04-hadoop-1-2-and-3-what-changed/">2.4 Hadoop 1, 2 and 3</a>: NameNode failover</li>
    <li><a href="../03-how-a-cluster-works/01-hadoop-architecture-hdfs-yarn-mapreduce-and-common/">3.1 Hadoop architecture</a>: spot the daemons</li>
    <li><a href="../03-how-a-cluster-works/02-the-life-of-a-file-and-a-job-end-to-end/">3.2 The life of a file and a job</a>: follow the Event log</li>
    <li><a href="../03-how-a-cluster-works/03-node-roles-master-worker-edge-and-gateway/">3.3 Node roles</a>: break each role</li>
    <li><a href="../04-setup/02-standalone-pseudo-distributed-and-fully-distributed-modes/">4.2 Standalone, pseudo and fully distributed</a>: one node, then many</li>
    <li><a href="../04-setup/04-configuration-files-and-web-uis/">4.4 Configuration files and web UIs</a>: block size and replication per file</li>
    <li><a href="../05-hdfs-architecture/01-namenode-and-datanode/">5.1 NameNode and DataNode</a>: metadata here, data there</li>
    <li><a href="../05-hdfs-architecture/02-blocks/">5.2 Blocks</a>: same file, different block sizes</li>
    <li><a href="../05-hdfs-architecture/03-replication-and-rack-awareness/">5.3 Replication and rack awareness</a>: replicas across racks</li>
    <li><a href="../05-hdfs-architecture/05-heartbeats-and-block-reports/">5.5 Heartbeats and block reports</a>: silence means dead</li>
  </ul>
</section>'''

# ------------------------------------------------------------------ glossary
# (term, group, meaning html, lesson link or '')
L11 = '../01-foundations/01-server-node-rack-and-data-centre/'
L12 = '../01-foundations/02-what-is-a-cluster-masters-and-workers/'
L13 = '../01-foundations/03-scale-out-in-practice/'
L14 = '../01-foundations/04-failures-are-normal/'
L15 = '../01-foundations/05-move-the-code-not-the-data/'
L21 = '../02-why-hadoop/01-the-problem-hadoop-solved/'
L22 = '../02-why-hadoop/02-from-google-s-papers-to-apache-hadoop/'
L23 = '../02-why-hadoop/03-how-hadoop-solved-each-problem/'
L24 = '../02-why-hadoop/04-hadoop-1-2-and-3-what-changed/'
L31 = '../03-how-a-cluster-works/01-hadoop-architecture-hdfs-yarn-mapreduce-and-common/'
L32 = '../03-how-a-cluster-works/02-the-life-of-a-file-and-a-job-end-to-end/'
L33 = '../03-how-a-cluster-works/03-node-roles-master-worker-edge-and-gateway/'
L34 = '../03-how-a-cluster-works/04-when-not-to-use-hadoop/'
L41 = '../04-setup/01-prerequisites-linux-java-and-ssh/'
L42 = '../04-setup/02-standalone-pseudo-distributed-and-fully-distributed-modes/'
L43 = '../04-setup/03-installing-hadoop-docker-cluster-and-ubuntu-wsl/'
L44 = '../04-setup/04-configuration-files-and-web-uis/'
L51 = '../05-hdfs-architecture/01-namenode-and-datanode/'
L52 = '../05-hdfs-architecture/02-blocks/'
L53 = '../05-hdfs-architecture/03-replication-and-rack-awareness/'
L54 = '../05-hdfs-architecture/04-fsimage-edit-log-and-checkpointing/'
L55 = '../05-hdfs-architecture/05-heartbeats-and-block-reports/'
L56 = '../05-hdfs-architecture/06-safe-mode/'
L61 = '../06-hdfs-operations/01-how-a-file-is-written-the-write-pipeline/'
L62 = '../06-hdfs-operations/02-how-a-file-is-read/'
L63 = '../06-hdfs-operations/03-hdfs-shell-commands/'
L64 = '../06-hdfs-operations/04-admin-commands-dfsadmin-fsck-and-balancer/'
L71 = '../07-hdfs-advanced/01-namenode-high-availability/'
L72 = '../07-hdfs-advanced/02-hdfs-federation/'
L73 = '../07-hdfs-advanced/03-erasure-coding/'
L74 = '../07-hdfs-advanced/04-snapshots-quotas-and-trash/'
L75 = '../07-hdfs-advanced/05-the-small-files-problem/'
L81 = '../08-mapreduce-fundamentals/01-thinking-in-mapreduce/'
L82 = '../08-mapreduce-fundamentals/02-input-splits-inputformat-and-recordreader/'
L83 = '../08-mapreduce-fundamentals/03-the-mapper/'
L84 = '../08-mapreduce-fundamentals/04-shuffle-and-sort/'
L85 = '../08-mapreduce-fundamentals/05-the-reducer/'
L86 = '../08-mapreduce-fundamentals/06-word-count-end-to-end/'
L91 = '../09-mapreduce-in-depth/01-combiner/'
L92 = '../09-mapreduce-in-depth/02-partitioner/'
L93 = '../09-mapreduce-in-depth/03-custom-writable-types/'
L94 = '../09-mapreduce-in-depth/04-counters/'
L95 = '../09-mapreduce-in-depth/05-reduce-side-join/'
L96 = '../09-mapreduce-in-depth/06-map-side-join-and-the-distributed-cache/'
L97 = '../09-mapreduce-in-depth/07-secondary-sort/'
L98 = '../09-mapreduce-in-depth/08-hadoop-streaming-with-python/'
L101 = '../10-data-formats/01-text-sequencefile-and-avro/'
L102 = '../10-data-formats/02-parquet-and-orc/'
L103 = '../10-data-formats/03-compression-codecs-and-splittability/'
L111 = '../11-yarn/01-yarn-architecture-resourcemanager-nodemanager-applicationmaster/'
L112 = '../11-yarn/02-the-life-of-a-yarn-application/'
L113 = '../11-yarn/03-schedulers-fifo-capacity-and-fair/'
L114 = '../11-yarn/04-memory-and-cpu-tuning/'
L115 = '../11-yarn/05-logs-and-debugging/'
L121 = '../12-multiple-clusters-and-operations/01-why-companies-run-many-clusters/'
L122 = '../12-multiple-clusters-and-operations/02-distcp-and-disaster-recovery/'
L123 = '../12-multiple-clusters-and-operations/03-cluster-sizing-with-real-numbers/'
L124 = '../12-multiple-clusters-and-operations/04-monitoring-and-alerts/'
L125 = '../12-multiple-clusters-and-operations/05-security-kerberos-and-ranger/'
L126 = '../12-multiple-clusters-and-operations/06-troubleshooting-playbook/'
L131 = '../13-hadoop-in-industry/01-the-hadoop-ecosystem-hive-hbase-zookeeper-and-more/'
L132 = '../13-hadoop-in-industry/02-hadoop-vs-spark/'
L133 = '../13-hadoop-in-industry/03-hadoop-in-the-cloud-and-cloudera/'
L134 = '../13-hadoop-in-industry/04-a-data-engineer-s-day-pipelines-migrations-and-the-lakehouse/'
L65 = '../06-hdfs-operations/05-the-hdfs-java-api/'
TERMS = [
    ('Server', 'Hardware and clusters', 'A computer built to run all day and serve other computers over a network.', L11),
    ('Node', 'Hardware and clusters', 'One server (or VM) that is a member of a cluster.', L11),
    ('Rack', 'Hardware and clusters', 'A cabinet of 20–40 servers sharing power and a top-of-rack switch. A failure domain and a bandwidth boundary.', L11),
    ('ToR switch', 'Hardware and clusters', '“Top of rack” switch that connects the servers in one rack and links the rack to the core network.', L11),
    ('Core (spine) switch', 'Hardware and clusters', 'Large switch connecting all the racks. Cross-rack traffic goes through it.', L11),
    ('Oversubscription', 'Hardware and clusters', 'When a switch\'s server ports add up to more bandwidth than its uplinks, for example 3 : 1.', L11),
    ('Commodity hardware', 'Hardware and clusters', 'Ordinary, affordable servers. Hadoop tolerates their failures in software.', L11),
    ('JBOD', 'Hardware and clusters', '“Just a bunch of disks”: separate disks without RAID, the usual choice for DataNodes.', L11),
    ('Cluster', 'Hardware and clusters', 'Networked nodes that work together as one system.', L12),
    ('Master node', 'Hardware and clusters', 'Coordinates the cluster: keeps metadata, tracks health, assigns work. NameNode, ResourceManager.', L12),
    ('Worker node', 'Hardware and clusters', 'Stores data and runs tasks. Usually runs a DataNode and a NodeManager.', L12),
    ('Edge (gateway) node', 'Hardware and clusters', 'The node where users log in and submit jobs; runs client tools only.', L12),
    ('Heartbeat', 'Hardware and clusters', 'Regular “I am alive” message from a worker to its master. HDFS: every 3 seconds.', L12),
    ('Shared-nothing', 'Hardware and clusters', 'Each node has its own CPU, RAM and disks; nodes share only the network.', L12),
    ('Single point of failure (SPOF)', 'Hardware and clusters', 'A part whose failure stops the whole system, such as a master with no standby.', L12),
    ('Horizontal scaling (scale out)', 'Sizing and operations', 'Adding more nodes rather than making one machine bigger.', L13),
    ('Replication factor', 'HDFS', 'How many copies of each block HDFS keeps. Default 3 (<code>dfs.replication</code>).', L13),
    ('Headroom', 'Sizing and operations', 'Free space kept on purpose (often 20–30%) so the cluster never runs full.', L13),
    ('Balancer', 'HDFS', 'Tool that moves blocks from full DataNodes to emptier ones (<code>hdfs balancer</code>).', L64),
    ('Wave', 'MapReduce', 'One round of tasks when there are more tasks than container slots.', L13),
    ('Fault tolerance', 'Sizing and operations', 'Continuing to work correctly when some parts fail.', L14),
    ('Re-replication', 'HDFS', 'Making new copies of blocks that lost replicas, until each is back to its replication factor.', L14),
    ('Under-replicated block', 'HDFS', 'A block with fewer live replicas than its replication factor.', L14),
    ('Missing block', 'HDFS', 'A block with no live replica at all. Files using it cannot be read.', L14),
    ('Checksum', 'HDFS', 'A small value computed from data to detect corruption. HDFS uses CRC32C per 512 bytes.', L62),
    ('Straggler', 'MapReduce', 'A task or node that is alive but much slower than the rest.', L14),
    ('Speculative execution', 'MapReduce', 'Running a backup copy of a slow task elsewhere; the first to finish wins.', L14),
    ('Data locality', 'MapReduce', 'Running a task on, or near, the node that holds its input block.', L15),
    ('Node-local (data-local)', 'MapReduce', 'Task runs on a node holding a replica of its input. Network distance 0.', L15),
    ('Rack-local', 'MapReduce', 'Task runs on another node in the same rack as its data. Distance 2.', L15),
    ('Off-rack', 'MapReduce', 'Task runs in a different rack from its data. Distance 4.', L15),
    ('Delay scheduling', 'YARN', 'Waiting briefly for a slot on a node with the data before running the task elsewhere.', L113),
    ('Shuffle', 'MapReduce', 'Moving map outputs across the network to the reducers, sorted by key.', L84),
    ('HDFS', 'HDFS', 'Hadoop Distributed File System: stores big files as blocks replicated across DataNodes.', ''),
    ('NameNode', 'HDFS', 'The HDFS master: file names, directories, permissions and the location of every block.', L12),
    ('DataNode', 'HDFS', 'HDFS worker that stores block replicas on its local disks and serves reads and writes.', L12),
    ('Block', 'HDFS', 'The unit HDFS stores: a file is cut into blocks of 128 MB by default (the last one can be smaller).', L52),
    ('Block report', 'HDFS', 'A DataNode\'s full list of the blocks on its disks, sent at start-up and periodically.', L12),
    ('fsimage and edit log', 'HDFS', 'The NameNode\'s saved metadata: a full snapshot (fsimage) plus a log of every change since (edits).', L54),
    ('Secondary NameNode', 'HDFS', 'Merges the edit log into the fsimage (checkpointing). It is <b>not</b> a standby and cannot take over.', L54),
    ('Standby NameNode', 'HDFS', 'In High Availability, a second NameNode kept up to date that takes over if the active one fails.', L71),
    ('Safe mode', 'HDFS', 'Read-only state of the NameNode at start-up while it waits for enough block reports.', L56),
    ('Rack awareness', 'HDFS', 'HDFS knowing which rack each node is on (from a topology script), so replicas span racks.', L11),
    ('MapReduce', 'MapReduce', 'Programming model and engine: map tasks process input splits in parallel, reduce tasks combine the results.', L81),
    ('Input split', 'MapReduce', 'The piece of input one map task processes; usually one block, but it is a logical range, not the block itself.', L82),
    ('Mapper / Reducer', 'MapReduce', 'User code that turns input records into key–value pairs (map) and combines all values for a key (reduce).', L83),
    ('Combiner', 'MapReduce', 'An optional “mini reducer” run on map output before the shuffle, to send less data. It may run 0, 1 or many times.', L91),
    ('YARN', 'YARN', 'Yet Another Resource Negotiator: Hadoop\'s cluster resource manager since Hadoop 2.', L111),
    ('ResourceManager', 'YARN', 'The YARN master: tracks free resources and grants containers to applications.', L111),
    ('NodeManager', 'YARN', 'YARN worker on each node: launches and monitors containers.', L111),
    ('ApplicationMaster', 'YARN', 'One per job: asks for containers and manages that job\'s tasks and retries.', L111),
    ('Container', 'YARN', 'A slice of a node\'s memory and CPU in which one task runs.', L111),
    ('Hadoop Common', 'History and versions', 'Shared libraries, configuration and tools used by every other Hadoop module.', L23),
    ('Schema-on-read', 'History and versions', 'Store raw data as it is and apply structure when reading it (Hive, Spark).', L23),
    ('Write once, read many', 'HDFS', 'HDFS files are written once (and can be appended) but not edited in the middle.', L21),
    ('GFS', 'History and versions', 'The Google File System (paper, 2003): the design HDFS is based on.', L22),
    ('Apache Nutch', 'History and versions', 'Open-source web search engine by Doug Cutting and Mike Cafarella where Hadoop\'s code began.', L22),
    ('JobTracker', 'History and versions', 'Hadoop 1 master that did both resource management and task scheduling for every job. Replaced by YARN.', L24),
    ('TaskTracker', 'History and versions', 'Hadoop 1 worker daemon that ran tasks in fixed map and reduce slots.', L24),
    ('Slot', 'History and versions', 'Hadoop 1\'s fixed place for one map task or one reduce task, never both.', L24),
    ('HDFS Federation', 'HDFS', 'Several independent NameNodes, each managing part of the namespace, sharing the DataNodes.', L72),
    ('JournalNodes (QJM)', 'HDFS', 'An odd-sized group of nodes storing the NameNode edit log, so the standby stays in sync (HA).', L71),
    ('Erasure coding', 'HDFS', 'Data plus parity cells (for example RS-6-3) instead of full copies: about 1.5× storage. Hadoop 3.', L73),
    ('Daemon', 'Hardware and clusters', 'A long-running background program. Every Hadoop component (NameNode, DataNode…) is a Java daemon.', L31),
    ('jps', 'Sizing and operations', 'JDK command listing running Java processes: the quickest check of which Hadoop daemons are up.', L31),
    ('fs.defaultFS', 'HDFS', 'Setting in core-site.xml that tells clients and daemons where the NameNode is, e.g. hdfs://nn1:8020.', L31),
    ('JobHistory Server', 'MapReduce', 'Keeps logs and counters of finished MapReduce jobs (web UI on port 19888).', L86),
    ('ZKFC', 'HDFS', 'ZooKeeper Failover Controller: watches a NameNode and triggers automatic failover in HA.', L71),
    ('Write pipeline', 'HDFS', 'The chain client → DN1 → DN2 → DN3 through which each block is written, with acks flowing back.', L61),
    ('Packet', 'HDFS', 'A 64 KB piece of a block sent through the write pipeline and acknowledged by every DataNode.', L32),
    ('Lease', 'HDFS', 'A write lock the NameNode gives one client, so only one writer works on a file at a time.', L32),
    ('Output committer', 'MapReduce', 'Moves successful task output into the final directory and writes the _SUCCESS marker.', L85),
    ('_SUCCESS', 'MapReduce', 'Empty file written into a job\'s output directory when the job completes successfully.', L85),
    ('Utility node', 'Hardware and clusters', 'Runs supporting services: ZooKeeper, Hive Metastore, HiveServer2, Oozie, cluster manager.', L33),
    ('Gateway node', 'Hardware and clusters', 'Another name for an edge node: client tools and configs, no core daemons.', L33),
    ('OLTP vs OLAP', 'Sizing and operations', 'OLTP: many small fast reads/writes (databases). OLAP: big scans for analysis (warehouses, Hive, Spark).', L34),
    ('TCO', 'Sizing and operations', 'Total cost of ownership: hardware, software, people, power, space and downtime over the years.', L34),
    ('WSL 2', 'Setup and configuration', 'Windows Subsystem for Linux: a real Ubuntu inside Windows, the easiest way to practise Hadoop on a Windows PC.', L41),
    ('JAVA_HOME', 'Setup and configuration', 'Environment variable pointing to the Java folder (above bin/java). Set it in hadoop-env.sh so every daemon finds Java.', L41),
    ('Passwordless SSH', 'Setup and configuration', 'Key-based login without a password; the start scripts use it to start daemons on every host, even localhost.', L41),
    ('Standalone mode', 'Setup and configuration', 'Default mode: one JVM, local files (file:///), no daemons. For debugging logic.', L42),
    ('Pseudo-distributed mode', 'Setup and configuration', 'Every daemon on one machine in its own JVM, with HDFS (replication 1) and YARN. For learning.', L42),
    ('Fully distributed mode', 'Setup and configuration', 'Masters and workers on separate machines (or containers), replication 3. Production.', L42),
    ('workers file', 'Setup and configuration', 'etc/hadoop/workers: one worker host per line, read by start-dfs.sh and start-yarn.sh.', L42),
    ('NameNode format', 'Setup and configuration', 'hdfs namenode -format: creates an empty namespace and a new cluster ID. Once per cluster; again erases HDFS.', L43),
    ('Cluster ID', 'Setup and configuration', 'ID created by formatting. DataNodes with a different one refuse to join (“Incompatible clusterIDs”).', L43),
    ('apache/hadoop image', 'Setup and configuration', 'Official Docker image of Hadoop; FILE_property=value environment lines become XML settings.', L43),
    ('*-site.xml', 'Setup and configuration', 'Your configuration files in etc/hadoop (core, hdfs, yarn, mapred). They override the defaults.', L44),
    ('*-default.xml', 'Setup and configuration', 'Built-in defaults for every property, packaged inside Hadoop\'s jars.', L44),
    ('final property', 'Setup and configuration', '&lt;final&gt;true&lt;/final&gt;: configuration files loaded later (such as a job.xml) cannot override it.', L44),
    ('-D option', 'Setup and configuration', 'Sets a property for one command or job, e.g. hdfs dfs -D dfs.replication=2 -put …', L44),
    ('/conf and /jmx', 'Setup and configuration', 'Web endpoints of every daemon: the settings in use (with source) and live metrics as JSON.', L44),
    ('Web UI ports', 'Setup and configuration', 'NameNode 9870, DataNode 9864, ResourceManager 8088, NodeManager 8042, JobHistory 19888.', L44),
    ('Block map', 'HDFS', 'NameNode\'s in-memory map from each block to the DataNodes holding it; rebuilt from block reports, never saved.', L51),
    ('blk_ and .meta files', 'HDFS', 'A replica on a DataNode disk: blk_N holds the bytes, blk_N_genstamp.meta the checksums (4 B per 512 B).', L51),
    ('Block pool', 'HDFS', 'All blocks of one namespace (BP-…); a folder on every DataNode. Federation gives each NameNode its own.', L72),
    ('RecordReader', 'MapReduce', 'Turns a split\'s bytes into records; finishes a record crossing the split end and skips a partial first line.', L82),
    ('Topology script', 'HDFS', 'Script named by net.topology.script.file.name that prints a rack for each DataNode IP or host.', L53),
    ('Over-/mis-replicated', 'HDFS', 'Over: more replicas than the target (extras deleted). Mis: enough replicas but all in one rack.', L53),
    ('setrep', 'HDFS', 'hdfs dfs -setrep [-w] N path: change a file\'s replication factor (and wait).', L53),
    ('Transaction ID (txid)', 'HDFS', 'Number given to every namespace change in the edit log; fsimage_N contains changes up to N.', L54),
    ('Checkpoint', 'HDFS', 'Merging fsimage + edit log into a new fsimage (SecondaryNameNode, Standby NameNode or saveNamespace).', L54),
    ('oiv / oev', 'HDFS', 'Offline Image Viewer and Offline Edits Viewer: read fsimage and edits files as text/XML.', L54),
    ('Stale DataNode', 'HDFS', 'No heartbeat for 30 s: still live, but can be avoided for reads and writes.', L55),
    ('Incremental block report', 'HDFS', 'Small report of replicas a DataNode received or deleted since its last report.', L55),
    ('triggerBlockReport', 'HDFS', 'hdfs dfsadmin -triggerBlockReport host:9867 makes a DataNode send a full block report now.', L55),
    ('Safe mode threshold', 'HDFS', 'int(total blocks × 0.999) must have a reported replica, then a 30 s extension, before safe mode ends.', L56),
    ('Packet', 'HDFS', 'Unit of the write pipeline: about 64 KB, i.e. 126 chunks of 512 bytes, each with a 4-byte checksum.', L61),
    ('Generation stamp', 'HDFS', 'Version number of a block (blk_N_GS); bumped when a pipeline is recovered, so stale replicas can be recognised.', L61),
    ('Pipeline recovery', 'HDFS', 'When a DataNode fails mid-write, the client rebuilds the pipeline with the survivors and a new generation stamp, then keeps writing.', L61),
    ('Network distance', 'HDFS', 'Hops between client and replica in the topology: 0 same node, 2 same rack, 4 other rack. Reads go to the nearest replica.', L62),
    ('Short-circuit read', 'HDFS', 'A client on the same machine reads the block file directly from local disk (dfs.client.read.shortcircuit, off by default).', L62),
    ('Hedged read', 'HDFS', 'If a read is slow, start a second read on another replica and use whichever finishes first.', L62),
    ('Corrupt replica', 'HDFS', 'A replica whose checksum does not match; the reader reports it (reportBadBlocks) and the NameNode replaces it.', L62),
    ('hdfs dfs', 'HDFS', 'The HDFS shell (FsShell): Linux-like commands such as -ls, -put, -cat, -mv, -rm on Hadoop file systems.', L63),
    ('Trash', 'HDFS', '/user/&lt;name&gt;/.Trash: where -rm moves files when fs.trash.interval &gt; 0 (it is 0, off, by default).', L74),
    ('getmerge', 'HDFS', 'hdfs dfs -getmerge dir local.csv: concatenates every file in an HDFS folder into one local file.', L63),
    ('dfsadmin', 'HDFS', 'hdfs dfsadmin: admin client for the NameNode (-report, -refreshNodes, -safemode, -printTopology…).', L64),
    ('fsck', 'HDFS', 'hdfs fsck path: health report of files and blocks (missing, corrupt, under-replicated); read-only by default.', L64),
    ('Decommissioning', 'HDFS', 'Retiring a DataNode safely: list it in dfs.hosts.exclude, run -refreshNodes, wait for Decommissioned.', L64),
    ('Maintenance mode', 'HDFS', 'Planned short downtime for a DataNode without copying away all its blocks.', L64),
    ('FileSystem API', 'HDFS', 'org.apache.hadoop.fs.FileSystem: the Java API (create, open, listStatus, rename, delete…) used by all Hadoop clients.', L65),
    ('WebHDFS', 'HDFS', 'REST API for HDFS on the NameNode (port 9870); data requests are redirected to DataNodes (port 9864).', L65),
    ('HttpFS', 'HDFS', 'A gateway server offering the WebHDFS API that streams data itself, so clients need to reach only one host.', L65),
    ('hflush / hsync', 'HDFS', 'Output-stream calls: hflush makes written data visible to readers; hsync also forces it to disk on the DataNodes.', L65),
    ('Active NameNode', 'HDFS', 'In HA, the one NameNode that serves clients and writes the edit log; the other waits as standby.', L71),
    ('Automatic failover', 'HDFS', 'ZooKeeper + ZKFC detect a dead active NameNode and promote the standby without a human (about 10 s in our lab).', L71),
    ('Epoch (QJM)', 'HDFS', 'A number each new active NameNode gets from the JournalNodes; writes with an older epoch are rejected, which stops a zombie NameNode.', L71),
    ('Fencing', 'HDFS', 'Making sure the old active NameNode cannot keep acting after failover (QJM epochs, plus sshfence or a shell script).', L71),
    ('Split brain', 'HDFS', 'Two NameNodes both believing they are active. HA design (epochs, fencing) exists to prevent it.', L71),
    ('Nameservice ID', 'HDFS', 'Logical name for an HA NameNode pair (hdfs://canteen/...); clients try both NameNodes behind it.', L71),
    ('ViewFS', 'HDFS', 'Client-side mount table that stitches several federated namespaces into one tree (viewfs://).', L72),
    ('Router-based Federation (RBF)', 'HDFS', 'Router servers holding a shared mount table, so clients see one namespace without client-side config.', L72),
    ('Cluster ID', 'HDFS', 'ID shared by all NameNodes of a federated cluster; DataNodes only join NameNodes with the same cluster ID.', L72),
    ('EC policy', 'HDFS', 'Erasure-coding layout set per directory, e.g. RS-6-3-1024k, RS-3-2-1024k, XOR-2-1-1024k.', L73),
    ('Block group', 'HDFS', 'In erasure coding, the set of data + parity blocks that together hold one striped piece of a file.', L73),
    ('Striping', 'HDFS', 'Splitting a file into small cells written round-robin across many DataNodes (used by erasure coding).', L73),
    ('Reed-Solomon (RS)', 'HDFS', 'The coding behind EC: RS-k-m stores k data + m parity cells and survives losing any m of them.', L73),
    ('Snapshot', 'HDFS', 'Read-only, point-in-time copy of a snapshottable directory, kept under .snapshot; created instantly, no data copied.', L74),
    ('snapshotDiff', 'HDFS', 'hdfs snapshotDiff dir s1 s2: lists created (+), deleted (-), modified (M) and renamed (R) paths.', L74),
    ('Name quota', 'HDFS', 'Limit on the number of files + directories under a directory (the directory itself counts).', L74),
    ('Space quota', 'HDFS', 'Limit on raw bytes under a directory, replication included; a new block reserves a full block × replication.', L74),
    ('Small files problem', 'HDFS', 'Millions of tiny files overload NameNode memory and RPCs and create too many map tasks; the fix is fewer, bigger files.', L75),
    ('HAR (Hadoop Archive)', 'HDFS', 'hadoop archive packs many files into a few part files plus an index, cutting NameNode objects; read via har://.', L75),
    ('Compaction', 'HDFS', 'Rewriting many small files into a few large ones (e.g. 128 MB–1 GB), typically per partition.', L75),
    ('Task attempt', 'MapReduce', 'One run of a task (attempt_…_m_000000_0). Failed attempts are retried, up to 4 by default; speculative copies are extra attempts.', L81),
    ('MRAppMaster', 'MapReduce', 'The ApplicationMaster of a MapReduce job: requests containers near the data, tracks tasks, retries and speculation.', L81),
    ('Key-value pair', 'MapReduce', 'The only data shape MapReduce passes around, e.g. (“chai”, 15). Map emits them; reduce receives a key with all its values.', L81),
    ('InputFormat', 'MapReduce', 'Defines how a job reads input: getSplits() on the client, createRecordReader() in each map task (TextInputFormat by default).', L82),
    ('Split slop', 'MapReduce', 'FileInputFormat folds a last piece of up to 10% (factor 1.1) into the previous split: 128 MB + 6.2 MB gave 1 split.', L82),
    ('CombineTextInputFormat', 'MapReduce', 'Packs many small files into one split, up to a maximum size, so fewer map tasks start.', L82),
    ('Splittable format', 'MapReduce', 'Input a reader can start in the middle of (plain text, bzip2, SequenceFile, Parquet). A gzip file is one split.', L82),
    ('setup() / cleanup()', 'MapReduce', 'Mapper and Reducer hooks that run once per task, before the first and after the last record.', L83),
    ('Context', 'MapReduce', 'The object map() and reduce() get: write(), getCounter(), getConfiguration(), getInputSplit().', L83),
    ('Writable', 'MapReduce', 'Hadoop\'s compact serialization types: Text, IntWritable, LongWritable, NullWritable. Keys must be WritableComparable.', L83),
    ('Counter', 'MapReduce', 'A named number tasks increment and the framework sums for the job, e.g. Map input records or a custom BAD_AMOUNT.', L83),
    ('Map-only job', 'MapReduce', 'A job with 0 reducers: map output goes straight to part-m-NNNNN files, with no sort or shuffle.', L83),
    ('Sort buffer (io.sort.mb)', 'MapReduce', 'mapreduce.task.io.sort.mb: the in-memory circular buffer for map output (100 MB default); it spills at 80% full.', L84),
    ('Spill', 'MapReduce', 'Writing the sorted contents of the map sort buffer to a file on local disk; 16 MB gave 18 spills in our lab.', L84),
    ('Merge factor (io.sort.factor)', 'MapReduce', 'How many sorted files are merged in one pass (10 by default); 18 spills needed an extra pass.', L84),
    ('ShuffleHandler', 'MapReduce', 'The NodeManager service (mapreduce_shuffle, port 13562) that serves map output to reducers.', L84),
    ('Reduce slowstart', 'MapReduce', 'mapreduce.job.reduce.slowstart.completedmaps (0.05): start reducers, and their copying, after 5% of maps finish.', L84),
    ('Spilled Records', 'MapReduce', 'Counter of records written to local disk by maps and reduces; far above 2 × map output means extra merge passes.', L84),
    ('HashPartitioner', 'MapReduce', 'Default partitioner: (key.hashCode() & Integer.MAX_VALUE) % numReduceTasks decides each key\'s reducer.', L85),
    ('Partition', 'MapReduce', 'The share of map output that goes to one reducer; one partition = one reduce task = one part-r file.', L85),
    ('Object reuse', 'MapReduce', 'The framework refills the same key/value objects; keep a copy (new Text(v)) if you store values.', L85),
    ('Data skew (hot key)', 'MapReduce', 'Uneven keys make one reducer do most of the work; 3 reducers gave files of 0, 79 and 38 bytes in our lab.', L85),
    ('part-r / part-m files', 'MapReduce', 'Job output files: part-r-NNNNN from reducers, part-m-NNNNN from map-only jobs, one per task.', L85),
    ('Driver', 'MapReduce', 'The main() that builds the Job: input/output paths, Mapper, Reducer, key/value classes, then waitForCompletion().', L86),
    ('hadoop jar', 'MapReduce', 'Runs a job from a jar: hadoop jar app.jar MainClass [-D key=value] in out.', L86),
    ('Uber mode', 'MapReduce', 'Runs a tiny job\'s tasks inside the ApplicationMaster\'s JVM to save container start-up (off by default).', L86),
    ('Staging directory', 'MapReduce', '/tmp/hadoop-yarn/staging/<user>/.staging/job_…: where the client uploads the jar, job.xml and split list.'.replace('<','&lt;').replace('>','&gt;'), L86),
    ('Exit code 137', 'MapReduce', 'A container killed with SIGKILL (kill -9 or out of memory); the attempt fails and is retried.', L86),
    ('mapreduce vs mapred API', 'MapReduce', 'org.apache.hadoop.mapreduce is the newer API (Context, Job); org.apache.hadoop.mapred is the older one (OutputCollector, JobConf).', L86),
    ('In-mapper combining', 'MapReduce', 'Aggregating in a HashMap inside the mapper and emitting the totals in cleanup(), instead of a combiner.', L91),
    ('Partial aggregate', 'MapReduce', 'A mergeable intermediate value such as (sum, count); an average is not one, so it can\'t be combined.', L91),
    ('Partitioner', 'MapReduce', 'Decides which reduce task gets each map output pair; getPartition() must return 0 … n-1.', L92),
    ('Salting', 'MapReduce', 'Adding a suffix (key#0 … key#n) to a hot key to spread it over reducers, then merging the parts.', L92),
    ('TotalOrderPartitioner', 'MapReduce', 'Sends key ranges (from a sampled partition file) to reducers so all part files together are globally sorted.', L92),
    ('WritableComparable', 'MapReduce', 'A Writable that can be sorted; every map output key must be one. compareTo() sets the sort order.', L93),
    ('Composite key', 'MapReduce', 'A key with several fields, such as (student, day), compared field by field.', L93),
    ('VInt / VLong', 'MapReduce', 'Variable-length numbers (WritableUtils): small values take 1 byte. Our compact key was 4.3× smaller.', L93),
    ('RawComparator', 'MapReduce', 'Compares serialized keys byte by byte without deserializing them, to speed up the sort.', L93),
    ('Dynamic counter', 'MapReduce', 'A counter named by strings at run time: getCounter("Orders by hour", "14").', L94),
    ('Counter limit', 'MapReduce', 'mapreduce.job.counters.max (120): one more fails tasks with “Too many counters: 121 max=120”.', L94),
    ('NullOutputFormat', 'MapReduce', 'An OutputFormat that writes nothing; useful when counters are the whole result.', L94),
    ('Reduce-side join', 'MapReduce', 'Both inputs are mapped to (join key, tagged record) and matched in the reducer; works for any size but shuffles everything.', L95),
    ('Tagging', 'MapReduce', 'Marking each value with its source (O| order, M| menu) so the reducer knows where it came from.', L95),
    ('MultipleInputs', 'MapReduce', 'Lets one job read several paths, each with its own InputFormat and Mapper.', L95),
    ('Map-side join', 'MapReduce', 'Joining inside the map phase with no shuffle: replicated (small side in memory) or composite (pre-sorted inputs).', L96),
    ('Distributed cache', 'MapReduce', 'Ships read-only files, archives and jars to every task: addCacheFile(uri#name), -files, -archives, -libjars.', L96),
    ('Broadcast join', 'MapReduce', 'Spark/Hive name for a replicated map-side join: the small table is copied to every task.', L96),
    ('Secondary sort', 'MapReduce', 'Getting each reduce group\'s values in a chosen order: composite key + natural-key partitioner + grouping comparator.', L97),
    ('Grouping comparator', 'MapReduce', 'setGroupingComparatorClass: decides which sorted keys share one reduce() call.', L97),
    ('Natural key', 'MapReduce', 'The field you group by (the student) inside a composite key; partitioning and grouping use only it.', L97),
    ('Hadoop Streaming', 'MapReduce', 'Runs any program that reads stdin and writes key<TAB>value lines as mapper or reducer (mapred streaming).'.replace('<','&lt;').replace('>','&gt;'), L98),
    ('PipeMapRed', 'MapReduce', 'Streaming\'s pipe to your script; “subprocess failed with code 1” means the script crashed (see yarn logs).', L98),
    ('SequenceFile', 'Data formats', 'Hadoop\'s binary file of Writable key-value pairs; header names the classes and codec; NONE, RECORD or BLOCK compression.', L101),
    ('Sync marker', 'Data formats', 'A 16-byte marker repeated inside SequenceFile and Avro files so a split can start in the middle of the file.', L101),
    ('Apache Avro', 'Data formats', 'Language-neutral binary row format; each data file carries its JSON schema; compact, splittable, compressible.', L101),
    ('Schema evolution', 'Data formats', 'Changing a schema without breaking old data: new fields need defaults (our lab: missing default → AvroTypeException).', L101),
    ('Writer vs reader schema', 'Data formats', 'Avro resolves the schema stored in the file against the one the program expects, field by field.', L101),
    ('Columnar format', 'Data formats', 'Stores a table column by column (Parquet, ORC) so readers fetch only needed columns and compress better.', L102),
    ('Parquet', 'Data formats', 'Columnar format: row groups → column chunks → pages, footer with schema and min/max statistics. Default in Spark.', L102),
    ('ORC', 'Data formats', 'Optimized Row Columnar: stripes with light-weight indexes every 10,000 rows; Hive\'s native format.', L102),
    ('Row group / stripe', 'Data formats', 'The horizontal slice of a Parquet (row group) or ORC (stripe) file; the unit that statistics let readers skip.', L102),
    ('Projection (column pruning)', 'Data formats', 'Reading only the needed columns: 192,526 bytes instead of 4,431,110 for Parquet in our lab.', L102),
    ('Predicate pushdown', 'Data formats', 'Skipping row groups or stripes whose min/max cannot match a filter; works best on sorted data (1 of 10 vs 10 of 10).', L102),
    ('Dictionary encoding', 'Data formats', 'Storing each distinct value once plus small codes per row (ORC DICTIONARY_V2[8] for 8 items).', L102),
    ('Compression codec', 'Data formats', 'A CompressionCodec: Default (deflate), Gzip, BZip2, Lz4, Snappy, ZStandard; chosen by file extension.', L103),
    ('Splittable codec', 'Data formats', 'A codec readers can start mid-file (SplittableCompressionCodec); only bzip2 among the built-ins. A .gz file is one map.', L103),
    ('Map output compression', 'Data formats', 'mapreduce.map.output.compress + codec: compresses the shuffle (lab: 60 MB → 13 KB with ZSTD).', L103),
    ('hadoop checknative', 'Data formats', 'Shows which native libraries (hadoop, zlib, zstd, bzip2, openssl, ISA-L) Hadoop can load.', L103),
    ('Scheduler (YARN)', 'YARN', 'The part of the ResourceManager that decides which application gets the next free container.', L111),
    ('ApplicationsManager', 'YARN', 'The part of the ResourceManager that accepts applications and starts (and restarts) their ApplicationMasters.', L111),
    ('Resource request', 'YARN', 'What an ApplicationMaster asks for: container size (memory, vcores), number, priority and preferred nodes/racks.', L111),
    ('Application attempt', 'YARN', 'One run of an application\'s ApplicationMaster; a failed AM gets a new attempt (2 by default).', L112),
    ('Application states', 'YARN', 'NEW → NEW_SAVING → SUBMITTED → ACCEPTED → RUNNING → FINAL_SAVING → FINISHING → FINISHED (or FAILED, KILLED).', L112),
    ('Localization', 'YARN', 'A NodeManager downloading a container\'s jars, files and archives before starting it.', L112),
    ('MB-seconds', 'YARN', 'YARN\'s usage bill per application: memory held × time (our job: 33,224 MB-seconds).', L112),
    ('FIFO scheduler', 'YARN', 'Serves applications in arrival order; a small job can wait behind a big one (120 s in our lab).', L113),
    ('Capacity Scheduler', 'YARN', 'Hadoop 3\'s default: hierarchical queues with guaranteed capacity, elastic maximum-capacity and user limits.', L113),
    ('Fair Scheduler', 'YARN', 'Shares the cluster so every running app/queue gets its fair share over time, by weight.', L113),
    ('Queue', 'YARN', 'A named share of the cluster (root.prod, root.dev); jobs pick one with mapreduce.job.queuename.', L113),
    ('user-limit-factor', 'YARN', 'Capacity Scheduler cap on one user, as a multiple of the queue\'s capacity; 1 (default) kept our big job at about 30%.', L113),
    ('Preemption (YARN)', 'YARN', 'Taking containers back from a queue over its share so an under-served queue gets its guarantee.', L113),
    ('Minimum allocation', 'YARN', 'yarn.scheduler.minimum-allocation-mb: requests are rounded up to a multiple (384 → 512 MB in our lab).', L114),
    ('DominantResourceCalculator', 'YARN', 'Counts both memory and vcores when packing containers; the default calculator counts memory only.', L114),
    ('Java heap space', 'YARN', 'OutOfMemoryError when objects outgrow -Xmx; raise the heap (and container) or stop collecting data in memory.', L114),
    ('Log aggregation', 'YARN', 'NodeManagers copy finished containers\' logs into HDFS (/tmp/logs/<user>/…) for yarn logs and JobHistory.'.replace('<','&lt;').replace('>','&gt;'), L115),
    ('yarn logs', 'YARN', 'Reads aggregated container logs: -applicationId, -containerId, -log_files, -am, -show_application_log_info.', L115),
    ('DR cluster', 'Sizing and operations', 'A cluster in another region that receives copies of critical data and takes over if the main site is lost.', L121),
    ('Data residency', 'Sizing and operations', 'Rules that some data must stay in a given country (e.g. RBI\'s rule for payment-system data in India).', L121),
    ('Configuration drift', 'Sizing and operations', 'Clusters that should be identical slowly ending up with different versions or settings.', L121),
    ('RPO / RTO', 'Sizing and operations', 'Recovery point objective (how much data you may lose) and recovery time objective (how long recovery may take).', L122),
    ('Snapshot-diff sync', 'Sizing and operations', 'distcp -update -diff s1 s2: copies only the changes between two snapshots and replays renames and deletes.', L122),
    ('Capacity planning', 'Sizing and operations', 'Turning data volume, retention, copies, headroom and growth into numbers of servers, disks and memory.', L123),
    ('TestDFSIO', 'Sizing and operations', 'HDFS read/write benchmark in the MapReduce tests jar; reports throughput per task.', L123),
    ('Oversubscription', 'Sizing and operations', 'Total server bandwidth in a rack divided by the rack\'s uplink bandwidth.', L123),
    ('Stale DataNode', 'Sizing and operations', 'No heartbeat for 30 s (dead only after 10 min 30 s); the NameNode\'s count of them can lag by minutes.', L124),
    ('Alert fatigue', 'Sizing and operations', 'Too many alerts that need no action, so real ones get ignored (e.g. staging files with replication 10).', L124),
    ('Canary job', 'Sizing and operations', 'A small scheduled job whose success and duration are monitored, to catch problems before users do.', L124),
    ('Kerberos', 'Security', 'Ticket-based network authentication; Hadoop\'s secure mode (hadoop.security.authentication=kerberos).', L125),
    ('Principal', 'Security', 'A Kerberos identity: user@REALM or service/host@REALM, e.g. nn/nn-secure@LAB.MYPHATSHALA.', L125),
    ('KDC / TGT', 'Security', 'The Key Distribution Center issues a ticket-granting ticket at kinit, then service tickets for each service.', L125),
    ('Keytab', 'Security', 'A file with a principal\'s keys so a service can log in without a password; guard it like a password.', L125),
    ('Simple authentication', 'Security', 'Hadoop\'s default: it trusts the user name the client sends (HADOOP_USER_NAME), so anyone can claim any user.', L125),
    ('HDFS ACL', 'Security', 'Extra named-user/group permissions on a file or folder (setfacl/getfacl; a + after the permission bits).', L125),
    ('Apache Ranger', 'Security', 'Central access policies enforced by plugins in HDFS, Hive, HBase and others, with masking, row filters and audit.', L125),
    ('Encryption zone', 'Security', 'An HDFS folder whose files are encrypted at rest with keys from the Hadoop KMS.', L125),
    ('Runbook', 'Sizing and operations', 'Written steps to diagnose and fix a known problem; every alert should link to one.', L126),
    ('Blameless postmortem', 'Sizing and operations', 'An incident review with timeline, root cause and actions, focused on systems rather than blame.', L126),
    ('AM resource limit', 'YARN', 'maximum-am-resource-percent (0.1): share of a queue for ApplicationMasters; beyond it jobs wait in ACCEPTED.', L126),
    ('Hive Metastore', 'Ecosystem', 'Stores table definitions (columns, format, location) shared by Hive, Spark, Trino and Impala.', L131),
    ('External table', 'Ecosystem', 'A table that points at existing files; dropping it leaves the files in place.', L131),
    ('SQL-on-Hadoop', 'Ecosystem', 'Engines that run SQL over files in HDFS or object storage: Hive, Spark SQL, Trino, Impala, Drill.', L131),
    ('Apache HBase', 'Ecosystem', 'A NoSQL store on HDFS for millisecond reads and writes by row key.', L131),
    ('Apache ZooKeeper', 'Ecosystem', 'A replicated coordination service: leader election, locks, configuration (used by HA and HBase).', L131),
    ('Apache Attic', 'Ecosystem', 'Where retired Apache projects go, e.g. Sqoop (Jun 2021) and Oozie (Feb 2025).', L131),
    ('Apache Spark', 'Ecosystem', 'A DAG engine with in-memory caching that usually runs on YARN and reads HDFS; it replaced MapReduce as the engine.', L132),
    ('Driver / executor', 'Ecosystem', 'Spark\'s planner process and its long-lived worker JVMs (YARN containers) that run tasks and cache data.', L132),
    ('RDD / DataFrame', 'Ecosystem', 'Spark\'s distributed collections: RDD = partitioned objects with lineage; DataFrame = table with a schema the optimizer can rewrite.', L132),
    ('Lazy evaluation', 'Ecosystem', 'Spark transformations only build a plan; an action (collect, write) runs it.', L132),
    ('Exchange', 'Ecosystem', 'Spark\'s name for a shuffle in a physical plan; each Exchange starts a new stage.', L132),
    ('Compute–storage separation', 'Ecosystem', 'Data stays in object storage (S3, GCS, ADLS) while clusters come and go to process it.', L133),
    ('Transient cluster', 'Ecosystem', 'A cluster created for a job or a night and deleted afterwards; you pay only while it runs.', L133),
    ('s3a / abfs / gs connectors', 'Ecosystem', 'Hadoop FileSystem clients that let jobs read and write cloud object storage with s3a://, abfs://, gs:// paths.', L133),
    ('Spot / preemptible workers', 'Ecosystem', 'Cheaper cloud machines that can be taken back; fine for task-only workers because tasks rerun.', L133),
    ('Lakehouse', 'Ecosystem', 'Open table formats on cheap storage giving warehouse features (ACID, time travel) to many engines.', L134),
    ('Apache Iceberg', 'Ecosystem', 'Open table format: snapshots, row-level DELETE/UPDATE, time travel, schema and partition evolution.', L134),
    ('Time travel', 'Ecosystem', 'Querying a table as of an older snapshot (our lab: VERSION AS OF snapshot 1 → 500,000 orders).', L134),
    ('Bronze / silver / gold', 'Ecosystem', 'Layers of a pipeline: raw as received, cleaned and typed, business-ready aggregates.', L134),
    ('Backfill', 'Ecosystem', 'Re-running a pipeline for past dates; safe only if each run is idempotent (overwrites its own partition).', L134),
    ('DistCp', 'Sizing and operations', 'Distributed copy: a map-only MapReduce job that copies files between or within clusters in parallel; -update copies only changed files.', L122),
]
CONFUSED = [
    ('Hadoop vs Spark', 'Not either/or. <b>Hadoop</b> is storage (HDFS) + resources (YARN) + an engine (MapReduce). <b>Spark</b> is an engine that usually runs on YARN and reads HDFS. In our lab five cached Spark passes took 35 s; five MapReduce jobs took 199 s.'),
    ('Data lake vs lakehouse', 'A <b>data lake</b> is files in cheap storage. A <b>lakehouse</b> adds a table format (Iceberg, Delta, Hudi) on top, giving transactions, updates, snapshots and time travel.'),
    ('Authentication vs authorization', '<b>Authentication</b> proves who you are (Kerberos tickets). <b>Authorization</b> decides what you may do (HDFS permissions, ACLs, Ranger policies). Without authentication, authorization can be bypassed by claiming another name, as our unsecured lab showed.'),
    ('Backup vs disaster recovery', 'A <b>backup</b> is a copy you can restore from, maybe slowly. <b>DR</b> is a ready second site with recent data and a rehearsed plan to switch over within the RTO.'),
    ('Capacity vs maximum-capacity vs user limit', '<b>capacity</b> is what a queue is guaranteed; <b>maximum-capacity</b> is how far it may grow when others are idle; <b>user-limit-factor</b> caps one user inside the queue. In our lab maximum-capacity 100% did nothing until user-limit-factor was raised.'),
    ('Container memory vs Java heap', 'The <b>container</b> (mapreduce.map.memory.mb) is what YARN reserves on the node; the <b>heap</b> (-Xmx) is what Java may use for objects, about 80% of it. Too small a heap gives "Java heap space"; heap + overhead above the container gets the container killed.'),
    ('Row format vs columnar format', '<b>Row formats</b> (CSV, SequenceFile, Avro) keep each record together: good for writing and reading whole records. <b>Columnar</b> (Parquet, ORC) keep each column together: good for analytics that read a few columns of many rows.'),
    ('Compressed file vs compressed container', 'A <b>.gz file</b> is one stream: not splittable, one map. A <b>container</b> (SequenceFile BLOCK, Avro, Parquet, ORC) compresses inside blocks, so the file stays splittable whatever the codec.'),
    ('Combiner vs reducer', 'A <b>reducer</b> runs once per key on all values, after the shuffle. A <b>combiner</b> runs on one map task\'s output, zero or more times, before the shuffle; it only works for operations like sum, count, max and min.'),
    ('Reduce-side vs map-side join', '<b>Reduce-side</b>: both inputs are shuffled; works for any sizes (24.4 MB shuffled, 24.8 s in our lab). <b>Map-side</b>: the small side is copied to every map task; no shuffle (18.9 s), but the small side must fit in memory.'),
    ('Partitioner vs grouping comparator', 'The <b>partitioner</b> decides which reducer gets a key. The <b>grouping comparator</b> decides which keys, already on that reducer, share one reduce() call.'),
    ('Killed vs failed task attempt', '<b>Failed</b>: the attempt crashed (exception, exit code 137) and counts toward the retry limit. <b>Killed</b>: the framework stopped it on purpose, usually the losing copy in speculative execution. Our job showed both and still succeeded.'),
    ('Map output vs job output', '<b>Map output</b> is temporary, sorted, on the worker\'s local disk, served to reducers and deleted after the job. <b>Job output</b> (part-r files) is written to HDFS with replication.'),
    ('Snapshot vs Trash', '<b>Trash</b> catches a normal <code>-rm</code> for a while, but <code>-skipTrash</code> or expiry bypasses it. A <b>snapshot</b> keeps the old state even after a -skipTrash delete, until you delete the snapshot.'),
    ('HA vs Federation', '<b>HA</b> gives one namespace two NameNodes (active + standby) for availability. <b>Federation</b> splits the namespace across several active NameNodes for scale. They can be combined.'),
    ('Replication vs erasure coding', '<b>Replication</b> keeps 3 full copies (200% overhead), fast to read and repair. <b>Erasure coding</b> keeps data + parity (e.g. 50% overhead), cheaper for cold data but costlier CPU and network on repair.'),
    ('Block vs input split', 'A <b>block</b> is how HDFS physically stores bytes (128 MB pieces). An <b>input split</b> is the logical piece one map task reads; it normally matches a block, but a record that crosses a block boundary is read whole by one split.'),
    ('NameNode vs ResourceManager', 'Both are masters, of different things. The <b>NameNode</b> manages <i>storage</i> (files and blocks). The <b>ResourceManager</b> manages <i>compute</i> (memory and CPU for jobs).'),
    ('DataNode vs NodeManager', 'Both run on a worker. The <b>DataNode</b> stores blocks; the <b>NodeManager</b> runs task containers. Running both on one machine is what makes data locality possible.'),
    ('Secondary NameNode vs Standby NameNode', 'The <b>Secondary</b> only merges the edit log into the fsimage. It cannot replace a failed NameNode. The <b>Standby</b> (HA) is a hot spare that takes over automatically.'),
    ('ResourceManager vs ApplicationMaster', 'The <b>ResourceManager</b> serves the whole cluster and hands out containers. An <b>ApplicationMaster</b> serves one job and decides which of its tasks run in those containers.'),
    ('Replication vs backup', '<b>Replication</b> keeps live copies to survive hardware failure; deletes and bad writes reach every copy. A <b>backup</b> or snapshot is a separate point-in-time copy you can restore.'),
    ('Node-local vs rack-local', '<b>Node-local</b>: the task runs on a machine holding its block. <b>Rack-local</b>: on another machine in the same rack, so data crosses only the rack switch.'),
    ('Dead vs stale DataNode', 'A <b>dead</b> node has been silent past the timeout (≈10.5 min) and its replicas are re-created elsewhere. A <b>stale</b> node has missed heartbeats for a shorter time (30 s by default) and can be avoided for reads and writes without being declared dead.'),
    ('Standalone vs pseudo-distributed', '<b>Standalone</b> runs a job inside one Java process on local files; no daemons. <b>Pseudo-distributed</b> runs every daemon (NameNode, DataNode, ResourceManager…) as a separate process on one machine, with real HDFS and YARN.'),
    ('core-default.xml vs core-site.xml', '<b>core-default.xml</b> holds Hadoop\'s built-in defaults inside the jars; never edit it. <b>core-site.xml</b> in etc/hadoop is where you override the values you need.'),
    ('Decommission vs stopping a DataNode', '<b>Decommissioning</b> copies every block away first, then marks the node Decommissioned: no moment with fewer replicas. <b>Stopping</b> it is treated as a failure: HDFS waits until the node is declared dead (≈10.5 min) before re-replicating.'),
    ('hdfs dfs -mv vs -cp', '<b>-mv</b> only renames in the NameNode, so it is instant for any size. <b>-cp</b> reads and rewrites every byte through the client (5.6 s vs 1.9 s for 403 MB in our lab).'),
    ('docker compose stop vs down', '<b>stop</b> pauses the containers and keeps their disks, so HDFS data survives. <b>down</b> deletes the containers, and without volumes the data goes with them.'),
]


def glossary_main():
    groups = []
    for t in TERMS:
        if t[1] not in groups:
            groups.append(t[1])
    body = ''
    for g in groups:
        items = sorted([t for t in TERMS if t[1] == g], key=lambda x: x[0].lower())
        body += f'<h3 class="gl-group">{E(g)}</h3>\n<div class="terms gl-terms">\n'
        for name, _, meaning, link in items:
            more = f' <a class="gl-link" href="{link}">Lesson →</a>' if link else ' <small class="muted">· later module</small>'
            body += f'  <div class="term" data-q="{E((name + " " + meaning).lower())}"><b>{E(name)}</b><span>{meaning}{more}</span></div>\n'
        body += '</div>\n'
    conf = ''.join(f'<details><summary>{E(a)}</summary><p>{b}</p></details>\n' for a, b in CONFUSED)
    return f'''<div class="ad-slot" data-slot="top"></div>
<section class="part">
  <label class="search gl-search">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>
    <input id="gl-q" type="search" placeholder="Search terms, e.g. block, rack, container…" aria-label="Search the glossary">
  </label>
  <p class="muted" id="gl-count"></p>
  <h2>Often confused</h2>
  <div class="faq">
{conf}  </div>
  <h2>All terms</h2>
{body}</section>'''


GL_CSS = '''<style>
.gl-search{display:flex;align-items:center;gap:8px;max-width:520px;padding:10px 14px;border:1px solid var(--line);border-radius:12px;background:var(--card);margin:6px 0}
.gl-search svg{width:18px;height:18px;color:var(--ink-3);flex:none}
.gl-search input{border:0;outline:0;background:none;font:inherit;color:var(--ink);width:100%}
.gl-group{margin-top:22px}
.gl-terms .term b{font-family:var(--font-body)}
.gl-link{font-weight:700;white-space:nowrap}
</style>'''
GL_JS = '''<script>
(function () {
  const q = document.getElementById("gl-q"), terms = Array.from(document.querySelectorAll(".gl-terms .term")), cnt = document.getElementById("gl-count");
  const groups = Array.from(document.querySelectorAll(".gl-group"));
  function run() {
    const s = q.value.trim().toLowerCase(); let n = 0;
    terms.forEach(t => { const on = !s || t.dataset.q.includes(s); t.hidden = !on; if (on) n++; });
    groups.forEach(g => { const box = g.nextElementSibling; g.hidden = box.querySelectorAll(".term:not([hidden])").length === 0; box.hidden = g.hidden; });
    cnt.textContent = s ? n + " matching term" + (n === 1 ? "" : "s") : terms.length + " terms";
  }
  q.addEventListener("input", run); run();
})();
</script>'''


def main():
    pg = shell('playground', 'Hadoop Cluster Playground: interactive simulator', 'An interactive simulator of a small Hadoop cluster: upload files to HDFS, see blocks and replicas on racks, stop DataNodes and NameNodes, watch re-replication and failover, and run a MapReduce job with and without data locality.', 15,
               'Cluster Playground', 'A small Hadoop cluster that runs in your browser. Upload files and watch HDFS split and replicate them, break nodes and racks, fail over the NameNode, and run a MapReduce job with and without data locality. Nothing is installed and nothing can break for real.',
               PG_MAIN, extra_head=f'<link rel="stylesheet" href="{UP}assets/css/cluster-sim.css">', extra_js=f'<script src="{UP}assets/js/cluster-sim.js"></script>')
    gl = shell('glossary', "Who's who: Hadoop glossary", 'Plain-English Hadoop glossary: racks, nodes, NameNode, DataNode, blocks, splits, YARN, containers, data locality and more, with the pairs of terms students most often confuse.', 10,
               "Who's who: Hadoop glossary", f'Every Hadoop term used in this course in one or two plain sentences, grouped by topic and searchable. Start with <b>Often confused</b>: the pairs of terms that trip up most students and interview candidates. {len(TERMS)} terms so far; the list grows with each module.',
               glossary_main(), extra_head=GL_CSS, extra_js=GL_JS)
    for slug, h in [('playground', pg), ('glossary', gl)]:
        out = os.path.join(ROOT, 'courses', 'hadoop', slug, 'index.html')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, 'w', encoding='utf-8').write(h)
        print('wrote', os.path.relpath(out, ROOT), f'({len(h) // 1024} KB)')


if __name__ == '__main__':
    main()
