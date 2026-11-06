import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l13_arch.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
HOOK = hook('We switched off a Kafka server in the middle of the day. What broke?',
    'Nothing. Orders kept flowing, and when the server came back it quietly took its old job back. This lesson opens the cluster to show the parts that make that possible.',
    ['Who decides which server is the “leader” of each partition (it is not ZooKeeper any more).',
     'What is inside a broker’s data folder: we count 117 sub-folders on one machine.',
     'The 5 APIs every Kafka tool and library talks to.'])
MAP = concept_map('Concept map. Beginner: broker, cluster, client APIs. Intermediate: partition leader and followers, ISR, controller quorum, internal topics. Advanced: leader election, KRaft metadata log, replication protocol.',
    [[('br', 'Broker', 'one Kafka server', None), ('cl', 'Cluster', '3+ brokers', None), ('ap', 'Client APIs', 'produce · consume · admin', None)],
     [('ld', 'Leader + followers', 'per partition', None), ('is', 'ISR', 'Lesson 5.2', B + '05-replication-and-the-cluster/02-isr-and-the-high-watermark/'), ('ct', 'Controller quorum', 'this lesson', None), ('it', 'Internal topics', '__consumer_offsets …', None)],
     [('le', 'Leader election', 'Lesson 5.3', B + '05-replication-and-the-cluster/03-leader-election/'), ('kr', 'KRaft metadata log', 'Lesson 5.4', B + '05-replication-and-the-cluster/04-kraft-vs-zookeeper/'), ('rp', 'Replication', 'Lesson 5.1', B + '05-replication-and-the-cluster/01-brokers-and-replication/')]],
    [('br', 'ld'), ('cl', 'ct'), ('ap', 'it'), ('ld', 'is'), ('ld', 'rp'), ('ct', 'kr'), ('is', 'le')],
    {'br', 'cl', 'ap', 'ld', 'ct', 'it'},
    '<b>Builds on:</b> <a href="../01-what-is-kafka/">1.1</a>, <a href="../02-messaging-models-queue-vs-pub-sub/">1.2</a>. <b>Next:</b> <a href="../04-topics-partitions-and-offsets/">1.4 Partitions and offsets</a>; deep dive in Module 5.')
WHW = why_how_where(
    'One server can fail or fill up. A cluster spreads partitions and keeps copies so no single machine matters.',
    'Brokers store partition replicas; one replica leads, others follow. A Raft quorum of controllers stores the cluster metadata and moves leadership on failure.',
    'Every Kafka deployment: on-premise, Kubernetes, and managed services such as Amazon MSK or Confluent Cloud.',
    'A single broker is fine for learning, never for production: no copies, no failover.')

def bro(x, y, n, parts, tone='card', down=False):
    op = ' opacity=".35"' if down else ''
    o = f'<g{op}>' + box(x, y, 120, 96, tone, rx=8) + t(x + 60, y + 15, f'Broker {n}', 8.6, bold=True) + t(x + 60, y + 27, 'broker + controller', 6.8, 'ink2')
    for k, (p, lead) in enumerate(parts):
        o += box(x + 10, y + 34 + k * 19, 100, 16, 'acc' if lead else 'blue', rx=3) + t(x + 60, y + 45 + k * 19, p + (' (leader)' if lead else ''), 6.8, 'ink', mono=True)
    return o + '</g>'
LAYOUT = {1: [('P2', True), ('P0', False), ('P1', False)], 2: [('P0', True), ('P1', False), ('P2', False)], 3: [('P1', True), ('P0', False), ('P2', False)]}
sc_ = ''.join(bro(30 + (n - 1) * 200, 22, n, LAYOUT[n]) for n in (1, 2, 3)) + t(320, 136, 'topic order-events: 3 partitions × 3 copies, one leader each (orange)', 8.2, 'ink2')
scene_svg = scene('Three brokers, each also a controller. Each holds a copy of partitions P0, P1 and P2; broker 1 leads P2, broker 2 leads P0, broker 3 leads P1.', sc_,
                  'Every partition has <tspan font-weight="700" class="s-acc">one leader</tspan> and two followers.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Switch a server off and watch</h2>
  <div class="story">
{HOOK}
    <p class="narration">Kabir is on TiffinGo’s platform team. The cloud provider announced maintenance: one of the three Kafka machines will reboot at lunchtime, the busiest hour.</p>

{scene_svg}

K> Sir, if broker 1 goes down, don’t we lose partition 2? It is the leader there.
A> Look closely: every partition lives on <b>all three</b> brokers. Broker 1 only <i>leads</i> P2. If it disappears, the cluster’s <b>controllers</b> promote another copy within seconds.
R> Who are these controllers?
A> Since Kafka 4.0 they are part of Kafka itself, a small voting group called the <b>KRaft quorum</b>. No ZooKeeper. Let’s inspect our cluster and then actually stop broker 1.
  </div>
</section>
'''

lv = '''
LEVELS> Architecture at three levels
L1> A dabbawala network
      <ul>
        <li>Three stations (brokers) each keep a copy of every route book (partition). For each route one station is in charge (leader); the others copy its updates (followers).</li>
        <li>A small committee (controllers) decides who is in charge. If a station closes, the committee picks another one at once.</li>
      </ul>
L2> The parts
      <ul>
        <li><b>Broker</b>: a server that stores partition replicas and serves clients. <b>Cluster</b>: brokers sharing one <code>cluster.id</code>.</li>
        <li><b>Leader replica</b> handles all reads and writes of a partition; <b>followers</b> fetch from it. Copies that are up to date form the <b>ISR</b> (in-sync replicas).</li>
        <li><b>Controllers</b> (KRaft) keep the metadata: topics, partitions, leaders, configs. In our lab each node is broker <i>and</i> controller (“combined mode”).</li>
      </ul>
L3> Under the hood
      <ul>
        <li>Metadata is itself a replicated log, <code>__cluster_metadata</code>, managed with the Raft consensus algorithm; one controller is the active leader (our lab: node 3, epoch 2).</li>
        <li>Consumer offsets live in the internal topic <code>__consumer_offsets</code> (50 partitions by default); share-group state in <code>__share_group_state</code>.</li>
        <li>Clients talk to brokers over a binary TCP protocol with versioned APIs (Produce, Fetch, Metadata …).</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of one broker data directory: meta.properties with node.id and cluster.id, the __cluster_metadata-0 folder with Raft quorum-state, 50 __consumer_offsets folders, and topic partition folders like order-events-0.',
    t(16, 22, '/var/lib/kafka/data on broker 1 (117 folders)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('meta.properties', 'amber', 1), ('__cluster_metadata-0/', 'violet', 2), ('__consumer_offsets-0 … -49', 'blue', 3)]) +
    fields(16, 72, [('__share_group_state-*', 'blue', None), ('order-events-0/  -1/  -2', 'green', 4), ('orders-0 …', 'green', None)]) +
    t(16, 116, 'meta.properties:  cluster.id=TiffinGoKafkaLab0001A  node.id=1', 7.6, 'ink2', anchor='start', mono=True) +
    t(16, 130, '__cluster_metadata-0:  .log  .index  …snapshot  quorum-state', 7.6, 'ink2', anchor='start', mono=True) +
    legend(16, 154, [(1, 'Identity', 'which cluster and which node this disk belongs to'),
                     (2, 'Metadata log', 'KRaft’s replicated log of topics, leaders, configs'),
                     (3, 'Group offsets', 'every consumer group’s bookmarks, 50 partitions'),
                     (4, 'Your data', 'one folder per partition replica on this broker')], size=8, gap=15, w=150),
    h=226, caption='Real directory listing from our lab, dissected.')
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Kafka architecture</h2>
''' + def_block(
    'A Kafka <b>cluster</b> consists of <b>brokers</b> that store topic partitions as replicated logs, and a <b>controller quorum</b> that manages cluster metadata using the <b>KRaft</b> protocol (Raft-based consensus, mandatory since Kafka 4.0). Each partition has a replication factor; one replica is the <b>leader</b>, serving produce and fetch requests, and the others are <b>followers</b> that replicate from it. Clients (producers, consumers, admin tools, Connect, Streams) discover leaders through the <b>Metadata</b> API and communicate with brokers over a versioned binary protocol on TCP.',
    'Kafka is a team of servers. Each partition is copied to several servers; one copy is in charge and the rest follow. A small built-in committee keeps track of who is in charge and replaces a failed leader automatically.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Broker', 'Server that stores partitions.'),
    ('Controller', 'Keeps cluster metadata.'),
    ('KRaft', 'Kafka’s Raft-based metadata quorum.'),
    ('Replica', 'One copy of a partition.'),
    ('Leader', 'The replica that serves clients.'),
    ('Follower', 'Replica copying the leader.'),
    ('ISR', 'Replicas fully caught up.'),
    ('Bootstrap server', 'First broker a client contacts.'),
]) + '''

  <h3>Why, how, where</h3>
''' + WHW + '''

  <h3>Concept map: what depends on what</h3>
''' + MAP + '''

  <h3>Zoom in, layer by layer</h3>
''' + zoom_layers() + '''
  <h3>Dissect a broker’s disk</h3>
''' + DIS + lv + myths([('ZooKeeper stores offsets and elects leaders.', 'Offsets live in __consumer_offsets; KRaft controllers elect leaders.', 'Step 1 (quorum) and Step 3 (internal topics).'), ('Brokers are stateless.', 'Brokers store partition data on disk; only metadata is handled by controllers.', 'Step 4: 117 partition folders on one broker.'), ('Producers ask ZooKeeper for broker IDs.', 'Clients get metadata from any broker via the Metadata API.', 'the “find the leader” peel animation below.')]) + '''
EXAM> “Explain Kafka architecture.” Brokers form a cluster and store partitions; each partition is replicated (RF) with one leader and followers; the ISR is the set of caught-up replicas. Since 4.0, KRaft controllers (a Raft quorum) store metadata in __cluster_metadata and handle leader election, replacing ZooKeeper. Clients bootstrap, fetch metadata, then talk directly to partition leaders.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Node roles and the client APIs</h2>
''' + table(['Node role (process.roles)', 'What it does', 'Typical use'], [
    ['broker,controller (combined)', 'stores data and votes on metadata', 'labs, small clusters (our lab)'],
    ['broker only', 'stores and serves partitions', 'production data nodes'],
    ['controller only', 'metadata quorum (3 or 5 nodes)', 'production control plane'],
], minw=560) + '''
''' + table(['API', 'Used by', 'Example'], [
    ['Producer', 'apps writing events', 'order app'],
    ['Consumer', 'apps reading events', 'kitchen, billing'],
    ['Admin', 'tools creating topics, configs', 'kafka-topics.sh'],
    ['Connect', 'moving data to/from systems', 'MySQL → Kafka (Module 7)'],
    ['Streams', 'processing inside Java apps', 'orders per city (Module 9)'],
], minw=560) + '''
WARN> Plan at least <b>3 brokers</b> and replication factor 3 for production, and an <b>odd</b> number of controllers (3 or 5): Raft needs a majority, so 3 controllers survive 1 failure and 5 survive 2. Combined mode is convenient but production clusters usually separate controllers.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Inspect the cluster, then break it</h2>
  <p>All outputs are real: 3 Kafka 4.4.0 nodes (k1, k2, k3) in Docker, each broker + controller. Tools run inside the containers from <code>/opt/kafka/bin</code>.</p>
''' + stepper([
    ('Step 1 · The controller quorum',
     code('bash', 'terminal', 'kafka-metadata-quorum.sh --bootstrap-server k1:9092 describe --status\nkafka-metadata-quorum.sh --bootstrap-server k1:9092 describe --replication', sec('== 1)', '== 3)')),
     'Node 3 is the active controller (leader of the metadata log, epoch 2); nodes 1 and 2 follow with lag 0. The “HighWatermark” is how many metadata records are committed. This is KRaft: no ZooKeeper anywhere.'),
    ('Step 2 · Leaders and replicas',
     code('bash', 'terminal', 'kafka-topics.sh --bootstrap-server k1:9092 --describe --topic order-events', sec('== 3)', '== 4)')),
     'Each partition has 3 replicas and a different leader: Kafka spreads leadership so every broker shares the work. <code>Isr: 2,3,1</code> means all copies are in sync.'),
    ('Step 3 · Internal topics',
     code('bash', 'terminal', 'kafka-topics.sh --bootstrap-server k1:9092 --list', sec('== 4)', '== 5)')),
     '<code>__consumer_offsets</code> stores consumer groups’ bookmarks; <code>__share_group_state</code> stores share-group progress (Kafka 4.x). They are normal Kafka topics that Kafka manages itself.'),
    ('Step 4 · A broker’s disk',
     code('bash', 'terminal', 'ls /var/lib/kafka/data; ls /var/lib/kafka/data | wc -l\ncat /var/lib/kafka/data/meta.properties\nls /var/lib/kafka/data/__cluster_metadata-0/', sec('== 5)', '== 7)')),
     'One folder per partition replica, 117 in total, mostly the 50 offsets partitions. <code>meta.properties</code> ties the disk to the cluster and node id. The metadata log has its own segments, a snapshot and <code>quorum-state</code>.'),
    ('Step 5 · Stop broker 1',
     code('bash', 'terminal', 'docker stop k1\nkafka-topics.sh --bootstrap-server k2:9092 --describe --topic order-events\necho \'o104:{"status":"PLACED"}\' | kafka-console-producer.sh --bootstrap-server k2:9092 --topic order-events ...\nkafka-get-offsets.sh --bootstrap-server k2:9092 --topic order-events', sec('== 8)', '== 9)')),
     'Partition 2 lost its leader (broker 1). Within seconds broker 2 became leader and the ISR shrank to <code>2,3</code>. A new order was still accepted: partition 0 grew from 2 to 3 events.'),
    ('Step 6 · Bring it back',
     code('bash', 'terminal', 'docker start k1\nkafka-topics.sh --bootstrap-server k2:9092 --describe --topic order-events', sec('== 9)')),
     'Broker 1 caught up and rejoined the ISR (<code>1,2,3</code>), then took back leadership of partition 2: Kafka prefers the first replica in the list (“preferred leader”) to keep load balanced.'),
]) + '''
</section>
'''

see = [
    term([('LeaderId: 3   LeaderEpoch: 2', W), ('3  Leader    Lag 0', G), ('1  Follower  Lag 0', W), ('2  Follower  Lag 0', W)], size=7.2),
    term([('P0 Leader: 2  Isr: 2,3,1', W), ('P1 Leader: 3  Isr: 3,1,2', W), ('P2 Leader: 1  Isr: 1,2,3', W)], size=7.2),
    term([('$ docker stop k1', Y), ('P2 Leader: 2  Isr: 2,3', RD), ('order-events:0:3   (write OK)', G)], size=7.2),
    term([('$ docker start k1', Y), ('P2 Leader: 1  Isr: 1,2,3', G)], size=7.2),
]
def mini(down=False, p2lead=1, isr_back=True):
    lay = {1: [('P2', p2lead == 1 and not down), ('P0', False), ('P1', False)], 2: [('P0', True), ('P1', False), ('P2', p2lead == 2)], 3: [('P1', True), ('P0', False), ('P2', False)]}
    return ''.join(bro(4 + (n - 1) * 118, 30, n, lay[n], down=(down and n == 1)) for n in (1, 2, 3))
B1 = [
    t(180, 14, 'Controllers vote (KRaft)', 9, bold=True) + ''.join(opbox(30 + k * 110, 50, f'node {k+1}', 'leader' if k == 2 else 'follower', 'acc' if k == 2 else 'card', 90, 34) for k in range(3)) + cap('Node 3 is the active controller.', '', 'violet', y=144, h=30),
    t(180, 14, 'Leaders spread across brokers', 9, bold=True) + mini() + cap('One leader per partition.', '', 'blue', y=144, h=30),
    t(180, 14, 'Broker 1 down: P2 fails over', 9, bold=True) + mini(down=True, p2lead=2) + cap('Broker 2 now leads P2.', '', 'red', y=144, h=30),
    t(180, 14, 'Broker 1 back: preferred leader', 9, bold=True) + mini() + cap('Leadership returns, ISR full.', '', 'green', y=144, h=30),
]
two = anim_two('Kafka architecture', 'Inspect, break, recover', 'Real outputs from the lab', 'What the cluster does', see, B1,
               ['Quorum.', 'Leaders.', 'Failure.', 'Recovery.'], ['KRaft.', 'Spread.', 'Failover.', 'Rebalance.'])
PEEL = peel('How a client finds the right broker', 'From “bootstrap server” to the partition leader. (Simplified.)',
    [('bootstrap.servers', ''), ('Metadata request', ''), ('Metadata reply', ''), ('Pick partition', ''), ('Talk to leader', ''), ('Leader moves', '')],
    [['bootstrap.servers', 'client knows k1:9092', 'just a starting point,', 'any broker works'],
     ['Metadata request', '“tell me about', 'topic order-events”', ''],
     ['Metadata reply', 'P0 → broker 2, P1 → 3,', 'P2 → 1, with host:port', 'of every broker'],
     ['Pick partition', 'key hash → P2', '(Lesson 1.4)', ''],
     ['Talk to leader', 'Produce/Fetch go straight', 'to broker 1, not through', 'a central router'],
     ['Leader moves', 'broker 1 fails → error', 'NOT_LEADER → client', 'refreshes metadata']],
    ['Start.', 'Ask.', 'Map.', 'Choose.', 'Direct.', 'Refresh.'], 'scenario-peel')

def five(kind, title, sub, cons, lines, caps, hid):
    fr = [t(180, 22, a, 9.4, 'acc' if i == 4 else 'ink', bold=True) + t(180, 56, b, 8.4, 'ink2') + cap(c, '', tone, y=150, h=34) for i, (a, b, c, tone) in enumerate(lines)]
    return anim_one(kind, title, sub, cons[0], cons[1], fr, caps, hid=hid)
s1 = five('Real-time scenario 1', 'Rolling restart for patching', 'Patching brokers one by one without downtime. (Typical.)',
          ('Rolling restart', 'Restart one broker at a time and wait for the ISR to be full before the next'), [
    ('Security patch needed', '3 brokers', 'No downtime allowed.', 'blue'),
    ('Restart broker 1', 'leaders move to 2 and 3', 'Clients refresh metadata.', 'green'),
    ('Wait for ISR = 1,2,3', 'broker 1 caught up', 'Check before next.', 'amber'),
    ('Repeat for 2, then 3', 'one at a time', 'Never two at once.', 'green'),
    ('Zero lost orders', 'RF 3 made it safe', 'Standard practice.', 'blue')],
    ['Patch.', 'Restart 1.', 'Wait.', 'Repeat.', 'Done.'], 'scenario-rolling')
s2 = five('Real-time scenario 2', 'Single-broker “production”', 'Why one broker is not enough. (Typical.)',
          ('Replication factor', 'With one broker, a disk failure loses data and any restart stops the business'), [
    ('Start-up runs 1 broker', 'RF 1', 'Works in testing.', 'blue'),
    ('Disk fails', 'partitions gone', 'No other copy.', 'red'),
    ('Orders since backup lost', 'apps blocked', 'Hours of outage.', 'red'),
    ('Move to 3 brokers, RF 3', 'min.insync.replicas 2', 'Lesson 2.4.', 'green'),
    ('Survives one failure', 'like our lab', 'Proven above.', 'blue')],
    ['RF 1.', 'Failure.', 'Loss.', 'Fix.', 'Safe.'], 'scenario-rf1')
s3 = five('Real-time scenario 3 · advanced', 'Losing the controller majority', 'Why controllers come in odd numbers. (Typical.)',
          ('Quorum', 'Raft needs a majority of controllers; 3 survive 1 failure, 5 survive 2'), [
    ('3 controllers', 'majority = 2', 'Healthy.', 'blue'),
    ('One fails', '2 of 3 still a majority', 'Metadata OK.', 'green'),
    ('A second fails', '1 of 3: no majority', 'No new leaders, no topic changes.', 'red'),
    ('Data path still partly works', 'existing leaders serve', 'But no failover.', 'amber'),
    ('Use 5 for big clusters', 'tolerates 2 failures', 'Separate controller nodes.', 'blue')],
    ['3 nodes.', '1 down.', '2 down.', 'Degraded.', 'Design.'], 'scenario-quorum')
animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Inspect, break, recover</h2>
  <p>Left: real lab output. Right: what the cluster does.</p>
''' + two + '''
  <p>Now peel how a client finds the right broker.</p>
''' + PEEL + '''
  <p>Three live scenarios follow: a rolling restart, a single-broker setup, and a controller quorum.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

def uc_(word, sub, tone, title, desc, flow_):
    return usecase(f'<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-{tone}" style="stroke:var(--{tone if tone != "acc" else "track"})"/>' + t(60, 42, word, 11, tone, bold=True) + t(60, 58, sub, 7.4, 'ink2'), title, desc, flow_)
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Architecture choices in practice</h2>
''' + '\n'.join([
    uc_('cloud', 'managed', 'blue', '1. Managed clusters', 'Cloud services run brokers and controllers for you; you choose brokers and storage (Lesson 11.1).', ['You', '*managed Kafka', 'Topics']),
    uc_('k8s', 'operator', 'green', '2. Kafka on Kubernetes', 'Operators such as Strimzi run brokers and controllers as pods with rolling upgrades.', ['YAML', '*operator', 'Cluster']),
    uc_('zones', 'racks', 'violet', '3. Multi-zone clusters', 'Replicas spread across availability zones (rack awareness) so a zone outage loses no data.', ['3 zones', '*rack-aware', 'Survives zone']),
    uc_('ops', 'patch', 'acc', '4. Rolling upgrades', 'Brokers are restarted one at a time; ISR checks gate each step.', ['Broker 1', '*ISR full?', 'Next broker']),
    uc_('bank', 'DR', 'blue', '5. Disaster recovery', 'A second cluster in another region receives a copy via MirrorMaker 2 (Lesson 10.4).', ['Primary', '*mirror', 'DR site']),
]) + '''
  <p class="muted">Examples are simplified descriptions of common patterns.</p>
</section>
'''
pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> <a href="../01-what-is-kafka/">1.1</a> for topics and partitions.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
