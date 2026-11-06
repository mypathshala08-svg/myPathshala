import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='05-replication-and-the-cluster', lesson='04-kraft-vs-zookeeper', n='5.4', module_label='Module 5 · Replication and the cluster',
    title='KRaft vs ZooKeeper',
    desc='How Kafka stores cluster metadata: ZooKeeper mode versus KRaft (KIP-500), the controller quorum and Raft epochs, the __cluster_metadata log, broker observers, snapshots, feature levels, dynamic quorums and ZooKeeper-to-KRaft migration. Real Kafka 4.4 lab: quorum status, a dump of 24,618 metadata records and the metadata shell image.',
    og_desc='Open Kafka’s brain: the KRaft quorum, 24,618 metadata records, and why ZooKeeper is gone in 4.x.',
    minutes=22, level='Intermediate',
    lead='Where does Kafka store who leads what? We ask the <b>KRaft quorum</b>, dump the <b>metadata log</b> and browse the <b>image</b>, and compare with the old ZooKeeper design. <b>All outputs are real.</b>',
    chips=['Quorum leader 2, epoch 17', '24,618 records', 'No ZooKeeper in 4.x', 'Runs in your browser (Python)'])
MAIN = '''# Replaying a metadata log into an image (simplified)
log = [
    {"type": "TOPIC_RECORD", "name": "small-51"},
    {"type": "PARTITION_RECORD", "topic": "small-51", "p": 0, "leader": 1, "isr": [1, 2]},
    {"type": "PARTITION_CHANGE_RECORD", "topic": "small-51", "p": 0, "isr": [1, 3]},
    {"type": "PARTITION_CHANGE_RECORD", "topic": "small-51", "p": 0, "leader": 3},
]
image = {}
for rec in log:
    if rec["type"] == "TOPIC_RECORD":
        image[rec["name"]] = {}
    elif rec["type"] == "PARTITION_RECORD":
        image[rec["topic"]][rec["p"]] = {"leader": rec["leader"], "isr": rec["isr"]}
    else:
        part = image[rec["topic"]][rec["p"]]
        part.update({k: v for k, v in rec.items() if k in ("leader", "isr")})
print(image)
'''
RUN = dict(heading='Run the code: replay the metadata log', intro='<p>State = replay of records. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('for rec in log:', 'Every node builds the same image from the same log.'), ('        part.update({k: v for k, v in rec.items() if k in ("leader", "isr")})', 'Changes are deltas.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Add a change with leader 1.', code=None),
        dict(label='2 · Predict first: majority', hint='<b>Predict first:</b> majority of 5 voters.', code='print(5 // 2 + 1)\n'),
        dict(label='3 · Tolerated', hint='Failures for 3 and 5 voters.', code='print([(n, (n - 1) // 2) for n in (3, 5)])\n'),
        dict(label='4 · Committed?', hint='Record on 2 of 3 voters.', code='print(2 >= 3 // 2 + 1)\n'),
        dict(label='5 · Spot the error', hint='Old config on Kafka 4.x.', expect='error', code='cfg = {"zookeeper.connect": "zk:2181"}\nif "zookeeper.connect" in cfg:\n    raise ValueError("ZooKeeper mode is not supported in Kafka 4.x; use process.roles + controller.quorum")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: inspect KRaft', intro='<p>Needs the 3-node lab. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Quorum status', cmd='kafka-metadata-quorum.sh --bootstrap-server k1:9092 describe --status', file='terminal', output='LeaderId: 2\nLeaderEpoch: 17\nHighWatermark: 24618\nCurrentVoters: [1, 2, 3]', note='Active controller.'),
           dict(title='2 · Replication lag', cmd='kafka-metadata-quorum.sh --bootstrap-server k1:9092 describe --replication', file='terminal', output='', note='Lag per voter/observer.'),
           dict(title='3 · Features', cmd='kafka-features.sh --bootstrap-server k1:9092 describe', file='terminal', output='metadata.version 4.4-IV2', note='Agreed versions.'),
           dict(title='4 · Format a new node', cmd='kafka-storage.sh format -t $(kafka-storage.sh random-uuid) -c server.properties --standalone', file='terminal', output='', note='First controller of a new cluster.')])
TRACE = dict(heading='Raft commit step by step', intro='<p>Append, replicate, commit.</p>',
    code='voters = {1: 24617, 2: 24618, 3: 24618}\nmajority = len(voters) // 2 + 1\nhw = sorted(voters.values(), reverse=True)[majority - 1]\nprint(majority, hw)\n',
    notes={2: 'Majority :: 2 of 3.', 3: 'HW :: Highest offset held by a majority.'})
WORKED_INTRO = 'Three KRaft decisions.'
EXAMPLES = [
    dict(level='b', tag='KRaft · dev', title='Single-node dev cluster', problem='<p>Run Kafka locally.</p>', inp='roles',
         approach=['process.roles=broker,controller.', 'Format storage.', 'Start.'], code='print({"process.roles": "broker,controller", "node.id": 1})\n', notes={1: 'Combined :: Like our lab.'}, tryit='PC step 4.'),
    dict(level='i', tag='KRaft · prod', title='Production layout', problem='<p>Size the controller quorum.</p>', inp='zones',
         approach=['3 dedicated controllers in 3 zones.', '5 if 2 failures must be tolerated.', 'Brokers separate.'], code='print({n: (n - 1) // 2 for n in (3, 5)})\n', notes={1: 'Odd :: 4 is no better than 3.'}, tryit='Run task 3.'),
    dict(level='a', tag='KRaft · migration', title='Leave ZooKeeper', problem='<p>Cluster on Kafka 3.5 with ZooKeeper.</p>', inp='version',
         approach=['Upgrade to 3.9.', 'Migrate to KRaft (dual-write, then finalize).', 'Upgrade to 4.x.'], code='print(["3.5 ZK", "3.9 ZK", "3.9 KRaft", "4.x KRaft"])\n', notes={1: 'Order :: No direct jump.'}, tryit='Scenario 2.')]
QUIZ = mix([
    dict(q='Beginner: Kafka 4.x stores metadata in…', options=['ZooKeeper', 'A KRaft quorum log', 'MySQL', 'Consumers'], answer=1, why='__cluster_metadata.'),
    dict(q='Beginner: The active controller is…', options=['Any broker', 'Leader of the controller quorum', 'The client', 'Random'], answer=1, why='Raft leader.'),
    dict(q='Beginner: KIP-500 is about…', options=['Compression', 'Removing ZooKeeper', 'Streams', 'Schemas'], answer=1, why='KRaft.'),
    dict(q='Intermediate: 3 voters tolerate how many failures?', options=['0', '1', '2', '3'], answer=1, why='Majority 2.'),
    dict(q='Intermediate: Most frequent change record in our lab was…', options=['TOPIC_RECORD', 'PARTITION_CHANGE_RECORD', 'CONFIG_RECORD', 'ACL'], answer=1, why='ISR/leader changes (9,488).'),
    dict(q='Intermediate: Brokers get metadata by…', options=['ZooKeeper watches', 'Fetching the metadata log', 'Email', 'Consumers'], answer=1, why='Observers.'),
    dict(q='Advanced: To leave ZooKeeper you must…', options=['Jump to 4.0', 'Migrate on 3.x (3.9 bridge) first', 'Delete topics', 'Nothing'], answer=1, why='Migration mode is in 3.x.'),
    dict(q='Advanced: kraft.version 1 enables…', options=['Compression', 'Dynamic controller quorum (add/remove voters)', 'Tiered storage', 'ACLs'], answer=1, why='KIP-853.')])
REVISION = ['ZooKeeper (≤3.x) = external store; KRaft (only mode in 4.x) = Raft quorum of controllers.', 'Metadata = __cluster_metadata log; active controller = quorum leader; brokers observe.',
    'Lab: leader 2, epoch 17, HW 24618, voters [1,2,3]; 9,488 PARTITION_CHANGE records.', 'Snapshots compact the log; feature levels (metadata.version) upgraded by kafka-features.', 'Migration: 3.9 bridge → KRaft → 4.x.']
FAQ = [('Is KRaft production ready?', 'Yes since 3.3 (2022); it is the only mode since 4.0.'),
    ('Do I still need an odd number of nodes?', 'For controllers, yes: 3 or 5 voters. Brokers can be any count.'),
    ('Can controllers be added later?', 'With kraft.version 1 (dynamic quorum, KIP-853) using kafka-metadata-quorum add-controller / remove-controller.'),
    ('Where is ZooKeeper still used?', 'Only in old clusters on 3.x or earlier, and by other systems such as some HBase/Hadoop setups.')]
PRACTICE_INTRO = 'KRaft programs.'
PROBLEMS = [
    dict(level='easy', title='Majority', stmt='Majority of 3.', inp='int', code='print(3 // 2 + 1)\n', explain='2.'),
    dict(level='easy', title='Tolerance', stmt='Failures with 5 voters.', inp='int', code='print((5 - 1) // 2)\n', explain='2.'),
    dict(level='easy', title='Roles', stmt='Combined node roles.', inp='str', code='print("broker,controller".split(","))\n', explain='Both.'),
    dict(level='medium', title='Count types', stmt='Count record types.', inp='list', code='from collections import Counter\nprint(Counter(["NO_OP", "PARTITION_CHANGE", "NO_OP"]))\n', explain='Like step 2.'),
    dict(level='medium', title='Quorum HW', stmt='Offsets {1:10,2:12,3:11}.', inp='dict', code='v = sorted([10, 12, 11], reverse=True)\nprint(v[1])\n', explain='11.'),
    dict(level='medium', title='Replay', stmt='Apply leader change to image.', inp='dict', code='p = {"leader": 1}\np.update({"leader": 3})\nprint(p)\n', explain='Delta.'),
    dict(level='business', title='Even voters', stmt='Is 4 better than 3?', inp='ints', code='print((4 - 1) // 2, (3 - 1) // 2)\n', explain='Both tolerate 1.'),
    dict(level='business', title='Upgrade path', stmt='Path from 3.6 ZK.', inp='list', code='print("3.6 -> 3.9 -> migrate -> 4.x")\n', explain='Bridge.')]
SCN_INTRO = 'KRaft interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“What is KRaft?”', 'Explain.', 'answer?', '<p>Kafka’s built-in metadata quorum that replaced ZooKeeper. A few controller nodes replicate a metadata log using Raft; the leader is the active controller; brokers read the log.</p>', '“A compression codec.”') +
    scn('Platform', 'Mid-level', 'Why remove ZooKeeper?', 'Manager asks.', 'answer?', '<ul><li>One system to run and secure.</li><li>Faster failover, more partitions.</li></ul>', '“ZooKeeper was buggy.”') +
    scn('Platform', 'Mid-level', 'Quorum lost', 'No topic creation works.', 'cause?', '<ul><li>Majority of controllers down.</li><li>Restore one; check describe --status.</li></ul>', 'Restarting brokers.') +
    scn('Platform', 'Senior', 'Plan migration', 'ZK cluster on 3.4.', 'plan?', '<ul><li>Upgrade to 3.9, migrate in dual-write, finalize.</li><li>Then 4.x, upgrade features.</li></ul>', 'Direct 4.0 upgrade.'))
