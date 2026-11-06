import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l113_new.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('If you learned Kafka from a 2022 tutorial, how much of it is now wrong?',
    'More than you think. Kafka 4.0 (March 2025) <b>removed ZooKeeper</b>, made the <b>new consumer rebalance protocol</b> (KIP-848) GA, and shipped <b>queues</b> (share groups) in early access. Through 4.1, 4.2, 4.3 and 4.4 (October 2026) queues became production-ready, Kafka Streams got broker-side rebalancing, and 4.4 added dead letter queues for share groups. Our lab cluster reports exactly these features through its <b>feature levels</b>.',
    ['The big changes in 4.0 and what they replaced.',
     'What 4.1–4.4 added, release by release.',
     'How to check your own cluster and upgrade safely.'])
cmap = concept_map('Concept map. Beginner: versions, what changed. Intermediate: KRaft only, KIP-848, share groups, Java and client changes. Advanced: feature levels, streams rebalance protocol, upgrade path from 3.x, deprecations.',
    [[('k3', 'Kafka 3.x', 'with ZooKeeper', None), ('kr', 'KRaft', 'Lesson 5.4', B + '05-replication-and-the-cluster/04-kraft-vs-zookeeper/')],
     [('k4', 'Kafka 4.0', 'Mar 2025', None), ('cg', 'KIP-848 groups', 'Lesson 3.2', B + '03-consumers/02-rebalancing-and-partition-assignment/'), ('sg', 'Share groups', 'Lesson 6.1', B + '06-queues-and-error-handling/01-share-groups-queues-for-kafka/'), ('rl', '4.1 → 4.4', 'releases', None)],
     [('fl', 'Feature levels', 'kafka-features', None), ('sr', 'Streams protocol', 'KIP-1071', None), ('dl', 'Share DLQ', 'KIP-1191', None), ('up', 'Upgrade path', '3.9 bridge', None)]],
    [('k3', 'kr'), ('kr', 'k4'), ('k4', 'cg'), ('k4', 'sg'), ('k4', 'rl'), ('rl', 'fl'), ('rl', 'sr'), ('rl', 'dl'), ('k3', 'up')],
    {'k4', 'rl', 'fl', 'sr', 'dl', 'up'},
    '<b>Builds on:</b> <a href="../../05-replication-and-the-cluster/04-kraft-vs-zookeeper/">5.4</a>, <a href="../../06-queues-and-error-handling/01-share-groups-queues-for-kafka/">6.1</a>. <b>Next:</b> Module 12 capstone.')
whw = why_how_where(
    'Kafka changes several times a year. Old tutorials, blog posts and even interview questions still assume ZooKeeper, eager rebalances and “Kafka is not a queue”. Knowing what changed avoids wrong designs and failed upgrades.',
    'Each release adds KIPs (Kafka Improvement Proposals). New on-disk or protocol behaviour is switched on with <b>feature levels</b> (metadata.version, group.version, share.version …) after all nodes run the new binaries, so upgrades are two steps: roll binaries, then upgrade features.',
    'Every new cluster (4.x), every upgrade plan, every architecture review, and interviews that ask “what is new in Kafka?”.',
    'You cannot jump from a ZooKeeper cluster straight to 4.x (migrate to KRaft on 3.9 first). Kafka 4.x clients and brokers need newer Java (Java 11+ for clients, 17+ for brokers and tools).')

def tl(hl=-1):
    ev = [('4.0', 'Mar 25', 'no ZK, KIP-848'), ('4.1', 'Sep 25', 'queues preview'), ('4.2', 'Feb 26', 'queues GA'), ('4.3', 'May 26', 'Streams state'), ('4.4', 'Oct 26', 'share DLQ')]
    o = t(180, 18, 'Kafka 4.x releases', 7.6)
    for k, (v, d, n) in enumerate(ev):
        o += box(6 + k * 70, 30, 64, 70, 'acc' if k == hl else ('green' if k == 4 else 'blue'), rx=6) + t(38 + k * 70, 50, v, 10, bold=True) + t(38 + k * 70, 66, d, 6.6) + t(38 + k * 70, 86, n, 5.9)
    return o
scene_svg = scene('Timeline of Kafka 4 releases: 4.0 in March 2025 removed ZooKeeper and made KIP-848 GA; 4.1 in September 2025 previewed queues; 4.2 in February 2026 made queues production-ready; 4.3 in May 2026 improved Streams state; 4.4 in October 2026 added dead letter queues for share groups.', tl(),
                  'Five releases in 19 months: <tspan font-weight="700" class="s-acc">queues went from idea to GA</tspan>.')
dialogue = '''K> Sir, a candidate in today’s interview said “Kafka needs ZooKeeper and cannot do queues”. I almost agreed.
A> That was true in 2022. Since 4.0 there is no ZooKeeper at all, and since 4.2 queues are production-ready.
R> How do I know what my own cluster supports?
A> Ask it. Feature levels tell you which new protocols are switched on. Let’s look at ours.'''

lv = '''
LEVELS> Kafka 4 at three levels
L1> A new phone OS
      <ul>
        <li>The phone is the same shape, but some old apps (ZooKeeper, old rebalance) were removed and new ones arrived (queues). Some features only switch on after every part of the system is updated (feature levels).</li>
      </ul>
L2> 4.0 (March 2025): the big break
      <ul>
        <li><b>KRaft only</b> (KIP-500/833): ZooKeeper mode removed; migrate on 3.x first. Old message formats v0/v1 and MirrorMaker 1 removed; many deprecated APIs and configs gone.</li>
        <li><b>KIP-848 consumer protocol GA</b>: broker-driven, incremental rebalances (<code>group.protocol=consumer</code>), Lesson 3.2.</li>
        <li><b>Queues (KIP-932) early access</b>, transaction protocol improvements (KIP-890), ELR (KIP-966), default <code>linger.ms</code> 5 ms, Java 17 for brokers.</li>
      </ul>
L3> 4.1 to 4.4
      <ul>
        <li><b>4.1</b> (Sep 2025): queues preview; Streams rebalance protocol (KIP-1071) early access; plugin metrics (KIP-877); OAuth jwt-bearer (KIP-1139).</li>
        <li><b>4.2</b> (Feb 2026): <b>share groups production-ready</b>, RENEW acknowledgement (KIP-1222), share lag metrics (KIP-1226); Streams rebalance protocol GA with a limited feature set; DLQ support in Streams exception handlers (KIP-1034); standardised CLI arguments (KIP-1147).</li>
        <li><b>4.3</b> (May 2026): assignment epochs to reduce fencing (KIP-1251), headers in state stores (KIP-1271/1285), cordoned log dirs (KIP-1066), MM2 multi-group offset translation (KIP-1239).</li>
        <li><b>4.4</b> (Oct 2026): <b>dead letter queues for share groups</b> (KIP-1191, share.version 2), transactional state stores in Streams (KIP-892), unregistering controllers (KIP-1312), new Linux I/O metrics (KIP-1291); <code>broker.id</code> and <code>kafka-broker-api-versions.sh</code> deprecated.</li>
      </ul>
/LEVELS
'''
FV = figure('Feature levels of our lab cluster: metadata.version 4.4-IV2, kraft.version 0, group.version 1, share.version 2, streams.version 1, transaction.version 2, eligible.leader.replicas.version 1.',
    t(16, 22, 'kafka-features describe (real, our lab)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('metadata 4.4-IV2', 'blue', 1), ('group 1', 'green', 2), ('share 2', 'violet', 3), ('streams 1', 'amber', 4), ('transaction 2', 'card', 5), ('ELR 1', 'card', 6)]) +
    legend(16, 84, [(1, 'metadata.version', 'on-disk metadata format of this release'), (2, 'group.version', '1 = KIP-848 consumer groups on'), (3, 'share.version', '2 = share groups + DLQ (4.4)'),
                    (4, 'streams.version', '1 = Streams rebalance protocol'), (5, 'transaction.version', '2 = KIP-890 transactions'), (6, 'eligible.leader.replicas', '1 = ELR (Lesson 5.3)')], size=8, gap=15, w=110),
    h=186, caption='Upgrade binaries first, then kafka-features upgrade.')
extra = '''

  <h3>Your cluster tells you</h3>
''' + FV

types_html = table(['Old (≤ 3.x) belief', 'Now (4.x)', 'Lesson'], [
    ['Start ZooKeeper first', 'No ZooKeeper; KRaft controllers', '5.4'], ['Rebalances stop the world', 'KIP-848 incremental, broker-driven', '3.2'],
    ['Kafka is not a queue', 'Share groups, production-ready since 4.2', '6.1'], ['Streams assigns tasks in the client', 'Broker-side Streams protocol (KIP-1071)', '9.1'],
    ['linger.ms default 0', 'Default 5 ms', '2.3'], ['MirrorMaker 1', 'Removed; use MM2', '10.4'], ['Message format v0/v1', 'Removed', '4.1'],
], minw=620)
warn = 'Upgrading from a ZooKeeper-based 3.x cluster: first upgrade to 3.9, migrate metadata to KRaft, finalise, then upgrade to 4.x. Check clients too: very old clients (pre-2.1 protocol versions) cannot talk to 4.x brokers.'

steps = [
    ('Step 1 · Ask the cluster',
     code('bash', 'terminal', 'kafka-topics.sh --version\nkafka-features.sh --bootstrap-server k2:9092 describe', sec('== 1)', '== 2)')),
     'Version 4.4.0, metadata.version 4.4-IV2. share.version 2 means share groups with the 4.4 additions; group.version 1 means the KIP-848 protocol is available.'),
    ('Step 2 · Group types in one cluster',
     code('bash', 'terminal', 'kafka-groups.sh --bootstrap-server k2:9092 --list    # count TYPE/PROTOCOL', sec('== 2)')),
     'Our lab collected Classic consumer groups (most clients still default to the classic protocol), Connect and Schema Registry groups, one KIP-848 Consumer group (Lesson 3.2) and seven Share groups (Lesson 6.1).'),
]
see = [term([('kafka 4.4.0', G), ('metadata 4.4-IV2', W), ('share.version 2', G)], size=7.0), term([('29 Classic/consumer', W), ('1 Consumer/consumer', G), ('7 Share/share', G)], size=7.0)]
B1 = [tl(4), tl(2)]
B1 = [b + cap(c, '', tn, y=126, h=30) for b, c, tn in zip(B1, ['Our lab: 4.4', 'Queues GA in 4.2'], ['green', 'blue'])]
two = anim_two('Kafka 4', 'Ask the cluster', 'Real outputs from the lab', 'Release timeline', see, B1, ['Features.', 'Groups.'], ['4.4.', 'Types.'])
pe = peel('A feature upgrade, layer by layer', 'Turning on a new feature level. (Simplified.)',
    [('Binaries', ''), ('Check', ''), ('Upgrade', ''), ('Record', ''), ('Use', ''), ('Rollback?', '')],
    [['Binaries', 'roll brokers + controllers', 'one at a time', ''], ['Check', 'kafka-features describe', 'supported max', ''], ['Upgrade', 'kafka-features upgrade', '--feature share.version=2', ''],
     ['Record', 'FeatureLevelRecord', 'in metadata log', 'Lesson 5.4'], ['Use', 'clients/brokers use', 'new protocol', ''], ['Rollback?', 'binaries: yes before', 'some levels: one-way', 'read notes']],
    ['Roll.', 'Check.', 'Raise.', 'Log.', 'Use.', 'Careful.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Old tutorial in a new job', 'Team still runs 2.8 with ZooKeeper. (Typical.)', ('Upgrade path', 'Via 3.9 and KRaft'), [
    ('Kafka 2.8 + ZooKeeper', 'unsupported', 'Risk.', 'red'), ('Upgrade to 3.9', 'rolling', 'Bridge.', 'amber'),
    ('ZK → KRaft migration', 'dual-write, finalise', 'Lesson 5.4.', 'green'), ('Upgrade to 4.x', 'then features', 'Modern.', 'green'),
    ('Enable KIP-848 clients', 'group.protocol=consumer', 'Faster rebalances.', 'blue')], ['Old.', '3.9.', 'KRaft.', '4.x.', 'Enable.'], 'scenario-upgrade') + \
       five('Real-time scenario 2', 'Drop RabbitMQ?', 'Jobs on a separate queue. (Typical.)', ('Share groups', 'Production-ready since 4.2'), [
    ('Two systems to run', 'Kafka + RabbitMQ', 'Cost.', 'amber'), ('Share groups on 4.4', 'acks, delivery limit, DLQ', 'Capability.', 'green'),
    ('Check client support', 'Java full; others vary', 'Gate.', 'amber'), ('Pilot one job type', 'measure', 'Test.', 'blue'),
    ('Retire queue if fit', 'one platform', 'Simpler.', 'green')], ['Two.', 'Queues.', 'Clients.', 'Pilot.', 'One.'], 'scenario-queues') + \
       five('Real-time scenario 3 · advanced', 'Interview: what’s new?', 'Senior role. (Typical.)', ('Talk in KIPs', 'Show you track releases'), [
    ('No ZooKeeper (4.0)', 'KRaft only', 'Answer 1.', 'blue'), ('KIP-848 rebalances', 'broker-driven', 'Answer 2.', 'blue'),
    ('Queues GA (4.2) + DLQ (4.4)', 'KIP-932, KIP-1191', 'Answer 3.', 'green'), ('Streams protocol', 'KIP-1071', 'Answer 4.', 'green'),
    ('Feature levels', 'safe upgrades', 'Depth.', 'violet')], ['ZK.', '848.', 'Queues.', 'Streams.', 'Features.'], 'scenario-interview')
assemble(HERE, h2_story='What changed since your tutorial', hook_html=hk,
    narration='In an interview, a candidate told Kabir that Kafka needs ZooKeeper and cannot do queues. Kabir realises many people learned Kafka before version 4.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='What’s new in Kafka 4',
    formal='<b>Apache Kafka 4.x</b> is the major line that began with 4.0 (March 2025), the first release without ZooKeeper (KRaft-only), with the next-generation consumer group protocol (KIP-848) generally available and queues for Kafka (KIP-932) in early access. Subsequent minor releases (4.1–4.4) added production-ready share groups, a broker-side Kafka Streams rebalance protocol (KIP-1071), share-group dead letter queues (KIP-1191) and many operational improvements, enabled through <b>feature levels</b> managed with <code>kafka-features</code>.',
    simple='Kafka 4 dropped ZooKeeper, made rebalances smooth, and learned to act as a job queue. Each later version adds more; your cluster’s feature levels show what is switched on.',
    term_rows=[('KIP', 'Kafka Improvement Proposal.'), ('KRaft', 'Built-in metadata quorum.'), ('KIP-848', 'New consumer protocol.'), ('KIP-932', 'Share groups (queues).'), ('KIP-1071', 'Streams rebalance protocol.'), ('KIP-1191', 'Share-group DLQ.'), ('Feature level', 'Switch for new behaviour.'), ('Bridge release', '3.9 for ZK migration.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Kafka needs ZooKeeper.', 'Not since 4.0.', 'Lesson 5.4.'),
               ('Kafka cannot be a queue.', 'Share groups GA since 4.2.', 'Step 2: 7 share groups.'),
               ('Upgrading binaries enables everything.', 'Feature levels must be raised too.', 'Peel.')],
    exam='“What is new in Kafka 4?” 4.0: KRaft only, KIP-848 GA, queues EA, old formats/MM1 removed, Java 17; 4.1: queues preview, Streams protocol EA; 4.2: share groups production-ready, Streams protocol GA (limited); 4.3: assignment epochs, header-aware stores; 4.4: share DLQ (KIP-1191), transactional state stores (KIP-892). Feature levels; upgrade via 3.9.',
    types_h2='Old beliefs, new facts', types_html=types_html, warn=warn,
    steps_h2='Ask your cluster', steps_intro='All outputs are real: our Kafka 4.4.0 lab cluster after Modules 1–10. Release facts from the Apache Kafka 4.1–4.4 announcements.',
    steps=steps, two=two, peel_intro='Now peel a feature upgrade.', peel_html=pe,
    scen_intro='Three live scenarios: an old cluster, dropping a queue, and an interview.', scen=scen,
    uc_h2='Kafka 4 at work', ucs=[uc_('new', 'new', 'green', '1. New clusters', 'KRaft-only, 4.x defaults.', ['Format', '*4.x', 'Run']),
        uc_('up', 'upgrade', 'amber', '2. Upgrades', '3.9 bridge, then 4.x.', ['ZK', '*migrate', 'KRaft']),
        uc_('q', 'queues', 'violet', '3. Queues', 'Share groups + DLQ.', ['Jobs', '*share', 'Workers']),
        uc_('st', 'streams', 'blue', '4. Streams apps', 'Broker-side assignment.', ['App', '*KIP-1071', 'Tasks'])],
    uc_note='Release details summarised from official announcements; check the upgrade notes for your exact versions.',
    pre='<b>Before you start:</b> <a href="../../05-replication-and-the-cluster/04-kraft-vs-zookeeper/">5.4 KRaft</a>.')
