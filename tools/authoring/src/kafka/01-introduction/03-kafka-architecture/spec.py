import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
BODY = body(HERE)

META = dict(
    module='01-introduction', lesson='03-kafka-architecture', n='1.3',
    module_label='Module 1 · Start here: why Kafka?',
    title='Kafka architecture',
    desc='Brokers, clusters, partition leaders and followers, ISR and the KRaft controller quorum, inspected on a real 3-node Kafka 4.4 cluster: quorum status, leaders per partition, internal topics, a broker data directory dissected, then a broker stopped and restarted to watch failover and preferred-leader recovery.',
    og_desc='Open up a real Kafka 4.4 cluster: KRaft quorum, leaders, ISR, a broker’s disk, and live failover.',
    minutes=26, level='Beginner',
    lead='What is inside a Kafka cluster? We inspect a real <b>3-node Kafka 4.4</b> cluster: the <b>KRaft controller quorum</b>, partition <b>leaders and followers</b>, the broker’s disk, and then we <b>switch a broker off</b> to watch failover. <b>All outputs are real.</b>',
    chips=['3 brokers, KRaft', 'Live failover', 'Broker disk dissected', 'Runs in your browser (Python)'],
)

MAIN = '''# Leader failover in miniature
replicas = {"P0": [2, 3, 1], "P1": [3, 1, 2], "P2": [1, 2, 3]}   # first = preferred leader
alive = {1, 2, 3}

def leaders():
    return {p: next(b for b in r if b in alive) for p, r in replicas.items()}

def isr():
    return {p: [b for b in r if b in alive] for p, r in replicas.items()}

print("normal  :", leaders())
alive.discard(1)                          # docker stop k1
print("k1 down :", leaders(), isr()["P2"])
alive.add(1)                              # docker start k1
print("k1 back :", leaders())
'''
RUN = dict(
    heading='Run the code: failover in miniature',
    intro='<p>The rule behind the lab’s failover. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    return {p: next(b for b in r if b in alive) for p, r in replicas.items()}', 'The first live replica in the list leads (the preferred leader when all are up).'),
        ('alive.discard(1)                          # docker stop k1', 'Broker 1 disappears: P2 moves to broker 2.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then also stop broker 2.', code=None),
        dict(label='2 · Predict first: majority', hint='<b>Predict first:</b> 5 controllers, how many may fail?',
             code='''n = 5
print("majority:", n // 2 + 1, "can fail:", n - (n // 2 + 1))
'''),
        dict(label='3 · Leaders per broker', hint='Count leaders each broker holds.',
             code='''leaders = {"P0": 2, "P1": 3, "P2": 1}
from collections import Counter
print(Counter(leaders.values()))
'''),
        dict(label='4 · Folders', hint='Partition folders on one broker.',
             code='''offsets, share, topics = 50, 0, 3 + 3 + 3
print(offsets + topics, "folders (approx)")
'''),
        dict(label='5 · Spot the error', hint='RF 3 on one broker.', expect='error',
             code='''brokers, rf = 1, 3
assert rf <= brokers, "replication factor 3 cannot be reached: only 1 broker"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: inspect a cluster',
    intro='<p>Use the lab’s <code>start_cluster.sh</code> (3 nodes) or a single node. <b>Outputs are real</b> (Kafka 4.4.0).</p>',
    items=[
        dict(title='1 · Quorum', cmd='kafka-metadata-quorum.sh --bootstrap-server k1:9092 describe --status', file='terminal',
             output='ClusterId: TiffinGoKafkaLab0001A\nLeaderId: 3\nLeaderEpoch: 2', note='Active controller.'),
        dict(title='2 · Leaders', cmd='kafka-topics.sh --bootstrap-server k1:9092 --describe --topic order-events', file='terminal',
             output='Partition: 2  Leader: 1  Replicas: 1,2,3  Isr: 1,2,3', note='One leader each.'),
        dict(title='3 · Failover', cmd='docker stop k1 && kafka-topics.sh --bootstrap-server k2:9092 --describe --topic order-events', file='terminal',
             output='Partition: 2  Leader: 2  Replicas: 1,2,3  Isr: 2,3', note='Seconds later.'),
    ],
)

TRACE = dict(
    heading='Pick the next leader',
    intro='<p>First replica that is still alive.</p>',
    code='''replicas = [1, 2, 3]
alive = {2, 3}
leader = None
for b in replicas:
    if b in alive:
        leader = b
        break
print("new leader:", leader)
''',
    notes={4: 'Scan :: Replica list order matters.', 7: 'Elect :: Broker 2 leads P2.'},
)

WORKED_INTRO = 'Three architecture decisions for TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='Kafka · sizing', title='How many brokers?',
         problem='<p>A new production cluster.</p>',
         inp='RF and failures to survive',
         approach=['RF 3 to survive 1 broker loss safely.', 'At least 3 brokers.', 'More brokers for disk and throughput.'],
         code='''rf = 3
print("min brokers:", rf, "survives:", rf - 1, "broker loss (with min.insync.replicas=2: 1)")
''', notes={1: 'Rule :: Brokers ≥ RF.'},
         tryit='Step 5.'),
    dict(level='i', tag='Kafka · controllers', title='Combined or separate controllers?',
         problem='<p>Lab uses combined mode; what for production?</p>',
         inp='cluster size',
         approach=['Small or dev: combined.', 'Production: 3 dedicated controllers.', 'Large: 5 controllers.'],
         code='''for brokers in (3, 12, 60):
    print(brokers, "brokers ->", "combined ok" if brokers <= 3 else "3 dedicated" if brokers < 50 else "5 dedicated")
''', notes={1: 'Guideline :: Separate control from data at scale.'},
         tryit='Types table.'),
    dict(level='a', tag='Kafka · zones', title='Spread replicas across zones',
         problem='<p>3 availability zones.</p>',
         inp='broker.rack',
         approach=['Set broker.rack per zone.', 'Kafka places replicas in different racks.', 'A zone outage leaves 2 copies.'],
         code='''rack = {1: "az-a", 2: "az-b", 3: "az-c"}
print("P0 replicas in", [rack[b] for b in [2, 3, 1]])
''', notes={1: 'Rack-aware :: Survives a zone failure.'},
         tryit='Use case 3.'),
]

QUIZ = mix([
    dict(q='Beginner: A broker is…', options=['A client library', 'A Kafka server storing partitions', 'A topic', 'A consumer'], answer=1,
         why='Brokers form the cluster.'),
    dict(q='Beginner: Who serves reads and writes for a partition?', options=['Any follower', 'The leader replica', 'The controller', 'ZooKeeper'], answer=1,
         why='Followers copy the leader.'),
    dict(q='Beginner: In Kafka 4.x metadata is managed by…', options=['ZooKeeper', 'KRaft controllers', 'Hive', 'The producer'], answer=1,
         why='ZooKeeper was removed in 4.0.'),
    dict(q='Intermediate: After stopping broker 1, P2’s ISR became…', options=['1,2,3', '2,3', '1', 'empty'], answer=1,
         why='Broker 2 took over.'),
    dict(q='Intermediate: Consumer offsets are stored in…', options=['ZooKeeper', '__consumer_offsets topic', 'The client disk', 'meta.properties'], answer=1,
         why='50 partitions by default.'),
    dict(q='Intermediate: Why did broker 1 lead P2 again after restart?', options=['Random', 'Preferred leader = first replica', 'It is bigger', 'Alphabetical'], answer=1,
         why='Keeps load balanced.'),
    dict(q='Advanced: 3 controllers. How many can fail and keep a majority?', options=['0', '1', '2', '3'], answer=1,
         why='Majority of 3 is 2.'),
    dict(q='Advanced: A client with only k1:9092 as bootstrap…', options=['Can only use broker 1', 'Learns all brokers from Metadata', 'Fails', 'Uses ZooKeeper'], answer=1,
         why='Bootstrap is just a starting point.'),
])

REVISION = [
    'Cluster = brokers (data) + controllers (metadata, KRaft).',
    'Partition replicas: one leader, followers; ISR = caught-up replicas.',
    'Lab: controller leader 3; P0→2, P1→3, P2→1; 117 folders on a broker.',
    'Stop k1: P2 leader → 2, ISR 2,3, writes still OK; restart: preferred leader returns.',
    'Internal topics: __consumer_offsets, __share_group_state, __cluster_metadata.',
    'Production: ≥3 brokers, RF 3, odd controllers (3 or 5).',
]
FAQ = [
    ('Is ZooKeeper still needed?', 'No. Kafka 4.0 removed ZooKeeper; clusters must use KRaft. Older 3.x clusters migrate before upgrading (Lesson 5.4).'),
    ('Do consumers read from followers?', 'By default consumers read from leaders. Kafka also supports fetching from the closest replica (rack-aware fetching) to save cross-zone traffic.'),
    ('How fast is failover?', 'Usually a few seconds in a healthy cluster, depending on session timeouts and client retries; in our lab the new leader was in place within the 12 seconds we waited.'),
    ('What is a bootstrap server?', 'Any broker address the client uses for its first Metadata request. List two or three so startup works even if one is down.'),
]

PRACTICE_INTRO = 'Programs about cluster architecture.'
PROBLEMS = [
    dict(level='easy', title='Majority', stmt='Majority of n controllers.', inp='3, 5',
         code='''for n in (3, 5):
    print(n, n // 2 + 1)
''', explain='2 and 3.'),
    dict(level='easy', title='Copies', stmt='Partition replicas in a cluster.', inp='3 partitions, RF 3',
         code='''print(3 * 3)
''', explain='9 replicas spread over brokers.'),
    dict(level='easy', title='Leader', stmt='First live replica.', inp='[1,2,3], alive {2,3}',
         code='''print(next(b for b in [1, 2, 3] if b in {2, 3}))
''', explain='2.'),
    dict(level='medium', title='ISR', stmt='Remove a dead broker from each ISR.', inp='dead 1',
         code='''isr = {"P0": [2, 3, 1], "P2": [1, 2, 3]}
print({p: [b for b in r if b != 1] for p, r in isr.items()})
''', explain='Matches the lab.'),
    dict(level='medium', title='Leader balance', stmt='Leaders per broker.', inp='map',
         code='''from collections import Counter
print(Counter({"P0": 2, "P1": 3, "P2": 2}.values()))
''', explain='Broker 2 has 2 while 1 is down.'),
    dict(level='medium', title='Disk per broker', stmt='GB per broker for 900 GB of data, RF 3, 3 brokers.', inp='900',
         code='''print(900 * 3 / 3, "GB")
''', explain='Each broker stores a full copy here.'),
    dict(level='business', title='Downtime cost', stmt='1 hour outage at 2,000 orders/hour × ₹300.', inp='numbers',
         code='''print("₹", 2000 * 300)
''', explain='Why RF 3 is worth it.'),
    dict(level='business', title='Zones', stmt='Copies left after one zone fails (RF 3, 3 zones).', inp='3',
         code='''print(3 - 1)
''', explain='Still writable with min ISR 2.'),
]

SCN_INTRO = 'Architecture questions interviewers ask.'
SCENARIOS = (
    scn('Any company · data', 'Fresher', '“Explain Kafka architecture.”',
        'Name the parts and how they relate.',
        'answer?',
        '<p>A cluster of brokers stores topic partitions; each partition is replicated with one leader and followers; the ISR is the caught-up set. KRaft controllers (since 4.0, replacing ZooKeeper) hold metadata and elect leaders. Clients bootstrap, get metadata, and talk directly to leaders.</p>', 'Describing ZooKeeper as current.') +
    scn('Platform', 'Mid-level', 'Broker failure',
        'A broker died. What happens to producers?',
        'answer?',
        '''<ul>
          <li>Controllers elect new leaders from the ISR.</li>
          <li>Producers get NOT_LEADER errors, refresh metadata and retry.</li>
          <li>With RF 3 and acks=all no acknowledged data is lost.</li>
        </ul>''', '“Data on that broker is lost.”') +
    scn('Platform', 'Mid-level', 'Patching',
        'How do you upgrade brokers without downtime?',
        'steps?',
        '''<ol>
          <li>One broker at a time.</li>
          <li>Wait until ISR is full and no under-replicated partitions.</li>
          <li>Preferred leaders rebalance automatically.</li>
        </ol>''', 'Restarting all brokers together.') +
    scn('Platform', 'Senior', 'Control plane',
        'Design the controller setup for 40 brokers across 3 zones.',
        'design?',
        '''<ul>
          <li>3 or 5 dedicated controllers, one per zone (5 to survive 2 failures).</li>
          <li>broker.rack per zone for replica placement.</li>
          <li>Monitor quorum lag and active controller changes.</li>
        </ul>''', 'Even number of controllers.')
)
