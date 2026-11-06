import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='11-kafka-in-industry', lesson='03-whats-new-in-kafka-4', n='11.3', module_label='Module 11 · Kafka in industry',
    title='What’s new in Kafka 4',
    desc='Everything that changed in Apache Kafka 4.x: 4.0 removed ZooKeeper (KRaft only), made the KIP-848 consumer protocol GA and introduced queues; 4.1 previewed queues and the Streams rebalance protocol; 4.2 made share groups production-ready; 4.3 improved coordinators and Streams state; 4.4 added share-group dead letter queues and transactional state stores. Real lab: feature levels and group types of a Kafka 4.4 cluster.',
    og_desc='Kafka 4.0 → 4.4 in one page: no ZooKeeper, KIP-848, queues GA, share DLQ, and how to read feature levels.',
    minutes=18, level='Intermediate',
    lead='What changed since older tutorials? We walk through <b>4.0 to 4.4</b>, read our cluster’s <b>feature levels</b>, and fix outdated beliefs. <b>Lab outputs are real.</b>',
    chips=['KRaft only', 'Queues GA in 4.2', 'Share DLQ in 4.4', 'Runs in your browser (Python)'])
MAIN = '''# Which features does a cluster support? (from kafka-features describe)
levels = {"metadata.version": "4.4-IV2", "group.version": 1, "share.version": 2,
          "streams.version": 1, "transaction.version": 2, "eligible.leader.replicas.version": 1}
checks = {
    "KIP-848 consumer groups": levels["group.version"] >= 1,
    "share groups (queues)":   levels["share.version"] >= 1,
    "share-group DLQ (4.4)":   levels["share.version"] >= 2,
    "Streams broker protocol": levels["streams.version"] >= 1,
    "KIP-890 transactions":    levels["transaction.version"] >= 2,
}
for name, ok in checks.items():
    print(f"{name:26s} {'yes' if ok else 'no'}")
'''
RUN = dict(heading='Run the code: read feature levels', intro='<p>What our lab cluster supports. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    "share-group DLQ (4.4)":   levels["share.version"] >= 2,', 'Level 2 adds the 4.4 additions.'), ('levels = {"metadata.version": "4.4-IV2", "group.version": 1, "share.version": 2,', 'Copied from the lab output.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Set share.version 0.', code=None),
        dict(label='2 · Predict first: months', hint='<b>Predict first:</b> months from 4.0 (Mar 2025) to 4.4 (Oct 2026).', code='print((2026 - 2025) * 12 + (10 - 3))\n'),
        dict(label='3 · Upgrade path', hint='From 3.6 with ZooKeeper.', code='print(["3.6 ZK", "3.9 ZK", "3.9 KRaft", "4.4 KRaft"])\n'),
        dict(label='4 · Java', hint='Broker Java minimum in 4.x.', code='print(17)\n'),
        dict(label='5 · Spot the error', hint='Starting ZooKeeper on 4.x.', expect='error', code='raise FileNotFoundError("zookeeper-server-start.sh: not found (removed in Kafka 4.0)")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: check your cluster', intro='<p>Any 4.x cluster. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Features', cmd='kafka-features.sh --bootstrap-server k2:9092 describe', file='terminal', output='Feature: share.version  SupportedMaxVersion: 2  FinalizedVersionLevel: 2', note='Trimmed.'),
           dict(title='2 · Groups', cmd='kafka-groups.sh --bootstrap-server k2:9092 --list', file='terminal', output='kitchen-61  Share  share', note='Type + protocol.'),
           dict(title='3 · Upgrade a feature', cmd='kafka-features.sh --bootstrap-server k2:9092 upgrade --feature share.version=2', file='terminal', output='', note='After binaries.')])
TRACE = dict(heading='A feature check step by step', intro='<p>Level → capability.</p>',
    code='share_version = 2\nprint("queues", share_version >= 1, "dlq", share_version >= 2)\n', notes={2: 'Both :: Yes on our lab.'})
WORKED_INTRO = 'Three version decisions.'
EXAMPLES = [
    dict(level='b', tag='4.x · new cluster', title='Start right', problem='<p>New cluster today.</p>', inp='choice',
         approach=['Latest 4.x.', 'KRaft controllers.', 'KIP-848 clients.'], code='print({"version": "4.4", "group.protocol": "consumer"})\n', notes={1: 'Modern :: Defaults.'}, tryit='Table.'),
    dict(level='i', tag='4.x · clients', title='Enable KIP-848', problem='<p>Consumers still Classic.</p>', inp='config',
         approach=['group.protocol=consumer.', 'Client 3.7+/4.x.', 'Roll consumers.'], code='print({"group.protocol": "consumer"})\n', notes={1: 'Lab :: 29 Classic, 1 Consumer.'}, tryit='Step 2.'),
    dict(level='a', tag='4.x · upgrade', title='From ZooKeeper', problem='<p>3.5 + ZooKeeper.</p>', inp='path',
         approach=['3.9 bridge.', 'Migrate to KRaft.', 'Then 4.x + features.'], code='print("3.5 → 3.9 → KRaft → 4.4 → kafka-features upgrade")\n', notes={1: 'No jump :: Required.'}, tryit='Scenario 1.')]
QUIZ = mix([
    dict(q='Beginner: Kafka 4.0 removed…', options=['Partitions', 'ZooKeeper mode', 'Consumers', 'Topics'], answer=1, why='KRaft only.'),
    dict(q='Beginner: Share groups became production-ready in…', options=['4.0', '4.1', '4.2', '3.9'], answer=2, why='Feb 2026.'),
    dict(q='Beginner: New behaviour is switched on by…', options=['Restart only', 'Feature levels', 'Topic config', 'ACLs'], answer=1, why='kafka-features.'),
    dict(q='Intermediate: KIP-848 is…', options=['Tiered storage', 'New consumer rebalance protocol', 'Queues', 'KRaft'], answer=1, why='Lesson 3.2.'),
    dict(q='Intermediate: Kafka 4.4 added for share groups…', options=['Compaction', 'Dead letter queues (KIP-1191)', 'Transactions', 'ZooKeeper'], answer=1, why='share.version 2.'),
    dict(q='Intermediate: Our lab’s metadata.version was…', options=['3.9-IV0', '4.4-IV2', '4.0-IV0', 'none'], answer=1, why='Step 1.'),
    dict(q='Advanced: From a ZooKeeper 3.x cluster you must first…', options=['Jump to 4.0', 'Migrate to KRaft on 3.x (3.9)', 'Delete data', 'Use MM1'], answer=1, why='Bridge.'),
    dict(q='Advanced: KIP-1071 moves which assignment to the broker?', options=['Consumer', 'Kafka Streams tasks', 'Connect', 'ACLs'], answer=1, why='Streams protocol.')])
REVISION = ['4.0: KRaft only, KIP-848 GA, queues EA, old formats/MM1 removed, Java 17 brokers.', '4.1: queues preview, Streams protocol EA; 4.2: queues production-ready, Streams protocol GA (limited).',
    '4.3: assignment epochs, header-aware stores; 4.4: share DLQ, transactional state stores, controller unregister.', 'Feature levels: binaries first, then kafka-features upgrade.', 'Lab: 4.4.0, metadata 4.4-IV2, share.version 2; 29 Classic, 1 Consumer, 7 Share groups.']
FAQ = [('Do my 3.x clients work with 4.x brokers?', 'Modern clients (2.1+ protocol) yes; very old clients no. Upgrade clients to use new features.'),
    ('Is KIP-848 automatic?', 'No, clients opt in with group.protocol=consumer; classic remains supported.'),
    ('Where do I read release details?', 'kafka.apache.org/blog release announcements and the upgrade notes in the docs.'),
    ('What about Kafka 5?', 'Not released as of late 2026; deprecations in 4.x (e.g. broker.id) point to removals there.')]
PRACTICE_INTRO = 'Version programs.'
PROBLEMS = [
    dict(level='easy', title='GA release', stmt='Queues GA version.', inp='str', code='print("4.2")\n', explain='Feb 2026.'),
    dict(level='easy', title='Feature', stmt='share.version ≥ 2?', inp='int', code='print(2 >= 2)\n', explain='DLQ.'),
    dict(level='easy', title='Order', stmt='Sort versions.', inp='list', code='print(sorted(["4.4", "4.0", "4.2"]))\n', explain='Timeline.'),
    dict(level='medium', title='Count types', stmt='Count group types.', inp='list', code='from collections import Counter\nprint(Counter(["Classic", "Share", "Classic", "Consumer"]))\n', explain='Like step 2.'),
    dict(level='medium', title='Path', stmt='Need bridge?', inp='bool', code='zk = True\nprint("3.9 + migrate" if zk else "direct")\n', explain='Yes.'),
    dict(level='medium', title='Outdated', stmt='Flag old beliefs.', inp='list', code='b = ["needs ZooKeeper", "linger 0", "share groups"]\nprint([x for x in b if x != "share groups"])\n', explain='Two outdated.'),
    dict(level='business', title='Ops saved', stmt='Remove 3 ZK nodes.', inp='int', code='print(3, "fewer servers")\n', explain='Simpler.'),
    dict(level='business', title='Migrate jobs', stmt='Queue system retired?', inp='bool', code='print("pilot first")\n', explain='Measure.')]
SCN_INTRO = 'Kafka 4 interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“What changed in Kafka 4?”', 'Explain.', 'answer?', '<p>No ZooKeeper (KRaft only), new consumer rebalance protocol (KIP-848), queues via share groups (GA in 4.2), and later releases added a broker-side Streams protocol and share-group DLQs.</p>', '“Nothing important.”') +
    scn('Platform', 'Mid-level', 'Upgrade plan', '3.4 with ZooKeeper.', 'steps?', '<ul><li>3.9, migrate KRaft, finalise.</li><li>4.x, features, clients.</li></ul>', 'Direct to 4.4.') +
    scn('Platform', 'Mid-level', 'Old tutorial', 'Team follows 2020 docs.', 'risks?', '<ul><li>ZooKeeper commands, MM1, old defaults.</li><li>Use 4.x docs.</li></ul>', 'Ignore versions.') +
    scn('Architecture', 'Senior', 'Queues on Kafka?', 'Replace RabbitMQ?', 'answer?', '<ul><li>Share groups production-ready 4.2+, DLQ 4.4.</li><li>Check clients; pilot.</li></ul>', '“Kafka can’t.”'))
