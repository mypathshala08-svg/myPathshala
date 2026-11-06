import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l54_kraft.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('Who elected the elector? The controller that picked new leaders in 5.3 was itself elected, by a log.',
    'Since Kafka 4.0 there is no ZooKeeper. The cluster’s own metadata (topics, partitions, ISR, brokers, configs) is a Kafka log, <code>__cluster_metadata</code>, replicated with the <b>Raft</b> protocol among controller voters. In our lab that log held 24,618 records, and 9,488 of them were ISR/leader changes.',
    ['What ZooKeeper did and why Kafka removed it (KIP-500).',
     'How KRaft works: voters, active controller, metadata log, snapshots.',
     'How to inspect it yourself, and how old clusters migrated.'])
cmap = concept_map('Concept map. Beginner: metadata, controller. Intermediate: ZooKeeper, KRaft quorum, metadata log, brokers as observers. Advanced: Raft epochs and high watermark, snapshots, feature levels, ZooKeeper to KRaft migration, dynamic quorum.',
    [[('md', 'Metadata', 'who leads what', None), ('ct', 'Controller', 'Lesson 5.3', B + '05-replication-and-the-cluster/03-leader-election/')],
     [('zk', 'ZooKeeper (old)', 'external', None), ('kq', 'KRaft quorum', 'voters 1,2,3', None), ('ml', '__cluster_metadata', 'a Kafka log', None), ('ob', 'Brokers observe', 'fetch metadata', None)],
     [('rf', 'Raft epoch + HW', 'like 5.2', B + '05-replication-and-the-cluster/02-isr-and-the-high-watermark/'), ('sn', 'Snapshots', 'compact state', None), ('fv', 'Feature levels', 'metadata.version', None), ('mg', 'ZK → KRaft migration', 'Kafka 3.x', None)]],
    [('md', 'ct'), ('ct', 'zk'), ('ct', 'kq'), ('kq', 'ml'), ('ml', 'ob'), ('kq', 'rf'), ('ml', 'sn'), ('kq', 'fv'), ('zk', 'mg')],
    {'md', 'ct', 'zk', 'kq', 'ml', 'ob', 'rf', 'sn', 'fv', 'mg'},
    '<b>Builds on:</b> <a href="../../01-introduction/03-kafka-architecture/">1.3</a>, <a href="../03-leader-election/">5.3</a>. <b>Next:</b> Module 6 queues and error handling.')
whw = why_how_where(
    'ZooKeeper was a second distributed system to run, secure and tune; metadata had to be copied from it to brokers, limiting partitions (~200k) and slowing controller failover.',
    'A few nodes run process.roles=controller and form a Raft quorum (controller.quorum.voters / bootstrap servers). The leader of that quorum is the active controller; it appends every change to __cluster_metadata. Brokers fetch the log and apply it, like followers.',
    'Every Kafka 4.x cluster (ZooKeeper mode was removed in 4.0, March 2025). Small clusters use combined nodes (broker+controller, like our lab); production uses 3 or 5 dedicated controllers.',
    'A quorum of N voters survives (N−1)/2 failures: 3 voters → 1, 5 → 2. Lose the majority and no metadata changes (no elections) can happen.')

def zkpic():
    o = t(160, 18, 'Before: ZooKeeper mode', 8.6, bold=True) + box(70, 30, 180, 44, 'violet', rx=8) + t(160, 56, 'ZooKeeper ensemble', 8, bold=True)
    for k in range(3):
        o += box(20 + k * 100, 110, 80, 40, 'acc' if k == 0 else 'blue', rx=6) + t(60 + k * 100, 134, 'controller' if k == 0 else f'broker {k+1}', 7.4)
        o += arrow(60 + k * 100, 108, 160, 76)
    return o
def krpic():
    o = t(480, 18, 'Now: KRaft mode', 8.6, bold=True) + box(370, 30, 220, 44, 'green', rx=8) + t(480, 50, '__cluster_metadata (Raft)', 8, bold=True) + t(480, 64, 'voters 1,2,3 · leader 2', 7.2)
    for k in range(3):
        o += box(360 + k * 84, 110, 72, 40, 'acc' if k == 1 else 'blue', rx=6) + t(396 + k * 84, 134, f'node {k+1}', 7.4)
        o += arrow(396 + k * 84, 108, 480, 76)
    return o
scene_svg = scene('Left: old ZooKeeper mode, where an external ZooKeeper ensemble stores metadata and one broker acts as controller. Right: KRaft mode, where Kafka nodes themselves form a Raft quorum storing metadata in the __cluster_metadata log; node 2 is the active controller.', zkpic() + krpic(),
                  'One system instead of two: <tspan font-weight="700" class="s-acc">metadata is a Kafka log</tspan>.')
dialogue = '''K> Sir, old blogs say “start ZooKeeper first, then Kafka”. Our lab never started ZooKeeper. Did we skip something?
A> No. Kafka 4.x has no ZooKeeper at all. It stores its own metadata using <b>KRaft</b>, Kafka + Raft.
R> So who is the controller in our lab?
A> Let’s ask the quorum. Then we’ll open the metadata log itself and read the record that made broker 3 a leader in 5.3.'''

lv = '''
LEVELS> Cluster metadata at three levels
L1> The minutes book
      <ul>
        <li>A committee (the voters) keeps one official minutes book. The chairperson (active controller) writes every decision; members copy it; a decision counts once most members have it. If the chair leaves, members vote a new chair. Everyone else (brokers) reads the book to know the rules.</li>
      </ul>
L2> How KRaft works
      <ul>
        <li><code>process.roles</code>: <code>broker</code>, <code>controller</code>, or both (combined). Controllers listed in <code>controller.quorum.voters</code> (static) or discovered via <code>controller.quorum.bootstrap.servers</code> (dynamic quorum, KIP-853, <code>kraft.version 1</code>).</li>
        <li>Raft: voters elect a leader per <b>epoch</b> (our lab: epoch 17, leader 2). The leader appends records; a record is committed when a majority has it (the quorum <b>high watermark</b>, 24618 in our lab, same idea as Lesson 5.2).</li>
        <li>Brokers are <b>observers</b>: they fetch the metadata log and keep an in-memory <b>image</b>. Brokers register and send heartbeats; a broker without heartbeats for <code>broker.session.timeout.ms</code> is fenced.</li>
      </ul>
L3> Snapshots, features, migration
      <ul>
        <li>The log is periodically compacted into <b>snapshots</b> (<code>metadata.log.max.record.bytes.between.snapshots</code>), so a restarting node loads a snapshot plus a short tail.</li>
        <li><b>Feature levels</b> (<code>metadata.version</code>, <code>kraft.version</code>, <code>group.version</code>, <code>eligible.leader.replicas.version</code> …) are agreed by the quorum and upgraded with <code>kafka-features.sh upgrade</code> after all nodes run the new binary.</li>
        <li><b>Migration</b>: ZooKeeper clusters had to move to KRaft on Kafka 3.x (3.9 is the bridge release) using the dual-write migration mode, then upgrade to 4.x. You cannot upgrade a ZooKeeper cluster directly to 4.0.</li>
      </ul>
/LEVELS
'''
CMP = table(['', 'ZooKeeper mode (≤ 3.x)', 'KRaft mode (3.3+ GA, only mode in 4.x)'], [
    ['Systems to run', 'Kafka + ZooKeeper', 'Kafka only'], ['Metadata store', 'ZooKeeper znodes', '__cluster_metadata log (Raft)'],
    ['Controller', 'one broker, elected via ZooKeeper', 'leader of controller quorum'], ['Controller failover', 'reload all metadata from ZK (slow)', 'standby already has the log (fast)'],
    ['Partition scale', '~200k per cluster in practice', 'millions (design goal)'], ['Propagation to brokers', 'RPCs from controller', 'brokers fetch the log'],
    ['Security config', 'two systems (SASL/ACLs for ZK too)', 'one'],
], minw=660)
HIST = figure('Timeline: 2019 KIP-500 proposed; 2021 Kafka 2.8 early access KRaft; 2022 Kafka 3.3 KRaft production ready; 2024 Kafka 3.9 last release with ZooKeeper and migration bridge; 2025 Kafka 4.0 removes ZooKeeper; 2026 Kafka 4.4 used in our lab.',
    ''.join(box(14 + k * 104, 30, 96, 46, tn, rx=6) + t(62 + k * 104, 48, y, 8.4, bold=True) + t(62 + k * 104, 64, d, 6.8)
            for k, (y, d, tn) in enumerate([('2019', 'KIP-500', 'violet'), ('2021', '2.8 preview', 'blue'), ('2022', '3.3 prod-ready', 'blue'), ('2024', '3.9 bridge', 'amber'), ('2025', '4.0 no ZK', 'green'), ('2026', '4.4 (lab)', 'acc')])),
    h=96, caption='From proposal to ZooKeeper removal.')
extra = '''

  <h3>ZooKeeper vs KRaft</h3>
''' + CMP + '''
  <h3>How we got here</h3>
''' + HIST

types_html = table(['Node role', 'process.roles', 'Use'], [
    ['Combined', 'broker,controller', 'dev, small clusters (our lab)'], ['Dedicated controller', 'controller', 'production: 3 or 5 nodes'],
    ['Broker only', 'broker', 'production data nodes'],
], minw=520) + table(['Tool', 'Shows'], [
    ['kafka-metadata-quorum.sh describe --status / --replication', 'leader, epoch, HW, voters, lag'],
    ['kafka-dump-log.sh --cluster-metadata-decoder', 'raw metadata records'], ['kafka-metadata-shell.sh', 'browse the image like a filesystem'],
    ['kafka-features.sh describe / upgrade', 'feature levels'], ['kafka-storage.sh format', 'format a node with a cluster id'],
], minw=560)
warn = 'Run an odd number of controller voters (3 or 5) on separate machines. With combined nodes like our lab, stopping 2 of 3 nodes loses the quorum: no leader elections or topic changes can happen until a majority returns.'

steps = [
    ('Step 1 · Ask the quorum',
     code('bash', 'terminal', 'kafka-metadata-quorum.sh --bootstrap-server k1:9092 describe --status', sec('== 1)', '== 2)')),
     'Node 2 is the active controller in Raft epoch 17. 24,618 metadata records are committed on a majority. Voters are 1, 2, 3.'),
    ('Step 2 · Read the metadata log',
     code('bash', 'terminal', 'kafka-dump-log.sh --cluster-metadata-decoder --files 00000000000000000000.log | grep -o \'"type":"[A-Z_]*"\' | sort | uniq -c | sort -rn', sec('== 2)', '== 3)')),
     'The log is ordinary records. NO_OP records are the leader’s heartbeat-like appends; 9,488 PARTITION_CHANGE records are every ISR shrink/expand and election from Lessons 5.1–5.3. The payload shown is the preferred election from 5.3: leader 3, ISR [3,1]. (We ran it on a copy of the file because the live directory is locked.)'),
    ('Step 3 · Browse the image',
     code('bash', 'terminal', 'kafka-metadata-shell.sh --snapshot meta.log\nls /image; ls /image/cluster/brokers; cat /image/topics/byName/rides-51/0', sec('== 3)', '== 4)')),
     'The image is the result of replaying the log: brokers, topics, configs, ACLs, quotas. The partition registration shows replicas, isr, elr, leader 2, leaderEpoch and partitionEpoch.'),
    ('Step 4 · Feature levels',
     code('bash', 'terminal', 'kafka-features.sh --bootstrap-server k1:9092 describe', sec('== 4)')),
     'metadata.version 4.4-IV2, ELR on (eligible.leader.replicas.version 1), new consumer protocol (group.version 1), share groups (share.version 2). kraft.version 0 means a static voter set.'),
]
see = [term([('LeaderId 2', G), ('LeaderEpoch 17', W), ('HW 24618', W), ('Voters [1,2,3]', W)], size=7.2),
       term([('NO_OP 14399', W), ('PARTITION_CHANGE 9488', Y), ('TOPIC 88', W)], size=7.2),
       term([('/image/topics/.../0', W), ('leader=2 isr=[1,2,3]', G)], size=7.2),
       term([('metadata.version 4.4-IV2', G), ('kraft.version 0', W)], size=7.2)]
def q(lead, hl):
    o = t(180, 14, hl, 9, bold=True)
    for k in range(3):
        o += box(20 + k * 112, 34, 100, 50, 'acc' if k + 1 == lead else 'blue', rx=6) + t(70 + k * 112, 62, f'voter {k+1}', 7.8, bold=k + 1 == lead)
    return o + box(60, 96, 240, 26, 'green', rx=4) + t(180, 113, '__cluster_metadata', 7.6, mono=True)
B1 = [q(2, 'Quorum leader 2'), q(2, 'Records in the log'), q(2, 'Replayed into an image'), q(2, 'Agreed feature levels')]
two = anim_two('KRaft', 'Quorum, log, image, features', 'Real outputs from the lab', 'Inside the controller', see, B1, ['Quorum.', 'Log.', 'Image.', 'Features.'], ['Leader.', 'Records.', 'State.', 'Versions.'])
pe = peel('One metadata change, layer by layer', 'The preferred election of small-51-0 in Lesson 5.3. (Simplified.)',
    [('Request', ''), ('Controller', ''), ('Raft append', ''), ('Commit', ''), ('Brokers apply', ''), ('Clients', '')],
    [['Request', 'ElectLeaders RPC', 'from the CLI', ''], ['Controller', 'active = node 2', 'checks ISR [1,3]', 'chooses 3'],
     ['Raft append', 'PARTITION_CHANGE', 'leader 3, epoch+1', ''], ['Commit', 'majority of voters', 'quorum HW moves', ''],
     ['Brokers apply', 'fetch metadata log', 'broker 3 becomes leader', 'broker 1 follower'], ['Clients', 'metadata refresh', 'send to broker 3', '']],
    ['Ask.', 'Decide.', 'Append.', 'Commit.', 'Apply.', 'Route.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Following an old tutorial', 'ZooKeeper instructions on Kafka 4.x. (Typical.)', ('KRaft only', 'zookeeper.connect no longer exists'), [
    ('Blog: start ZooKeeper', 'zookeeper-server-start.sh', 'Missing in 4.x.', 'blue'), ('Error', 'script / config not found', 'Confusion.', 'red'),
    ('kafka-storage.sh format', 'cluster id + controller config', 'KRaft way.', 'green'), ('process.roles=broker,controller', 'single node', 'Start.', 'green'),
    ('Works', 'use 4.x docs', 'Done.', 'blue')], ['Old.', 'Fail.', 'Format.', 'Roles.', 'Run.'], 'scenario-oldblog') + \
       five('Real-time scenario 2', 'Migrating a ZooKeeper cluster', 'Bank on Kafka 3.6. (Typical.)', ('ZK → KRaft migration', 'Must happen on 3.x first'), [
    ('Upgrade to 3.9', 'bridge release', 'Prereq.', 'blue'), ('Add KRaft controllers', 'zookeeper.metadata.migration.enable', 'Dual write.', 'green'),
    ('Roll brokers to KRaft', 'one by one', 'Careful.', 'amber'), ('Finalize, remove ZK', 'no way back after', 'Point of no return.', 'red'),
    ('Upgrade to 4.x', 'now allowed', 'Done.', 'blue')], ['3.9.', 'Controllers.', 'Brokers.', 'Finalize.', '4.x.'], 'scenario-migrate') + \
       five('Real-time scenario 3 · advanced', 'Lost the controller quorum', 'Two of three controllers down. (Typical.)', ('Majority', '3 voters tolerate 1 failure'), [
    ('Controllers 1 and 3 down', 'only 2 alive', 'No majority.', 'red'), ('Effects', 'no elections, no new topics', 'Existing leaders keep serving.', 'amber'),
    ('Restore one controller', 'majority again', 'Quorum back.', 'green'), ('Elections resume', 'fenced brokers handled', 'Healthy.', 'green'),
    ('Fix design', '5 voters across zones', 'Prevent.', 'blue')], ['Down.', 'Frozen.', 'Restore.', 'Resume.', 'Design.'], 'scenario-quorum')
assemble(HERE, h2_story='Where does Kafka keep its own brain?', hook_html=hk,
    narration='Kabir found a 2020 tutorial that starts ZooKeeper before Kafka. Our lab has no ZooKeeper. Today we find out where the cluster’s metadata lives now, and open it.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='KRaft vs ZooKeeper',
    formal='<b>KRaft</b> (Kafka Raft, KIP-500) is Kafka’s built-in metadata quorum. Controller nodes replicate the <code>__cluster_metadata</code> topic with a Raft-based protocol; the quorum leader is the <b>active controller</b>, which serialises all metadata changes as records. Brokers fetch this log and maintain a metadata image. It replaced <b>Apache ZooKeeper</b>, the external coordination service Kafka used until 3.x; ZooKeeper mode was removed in Kafka 4.0.',
    simple='Kafka used to need a separate system, ZooKeeper, to remember which broker leads what. Now Kafka keeps that information in its own special log, copied among a few controller nodes that vote on a leader. One system, faster failover, many more partitions.',
    term_rows=[('ZooKeeper', 'Old external metadata store.'), ('KRaft', 'Kafka’s Raft metadata quorum.'), ('Voter', 'Controller in the quorum.'), ('Active controller', 'Quorum leader.'), ('__cluster_metadata', 'Metadata log.'), ('Observer', 'Broker reading the log.'), ('Snapshot', 'Compacted metadata state.'), ('metadata.version', 'Metadata feature level.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Kafka needs ZooKeeper.', 'Not since 4.0; KRaft is the only mode.', 'Our lab has none.'),
               ('The controller is a separate product.', 'It is a Kafka process role.', 'process.roles.'),
               ('Metadata is in a database.', 'It is a Kafka log you can dump.', 'Step 2.')],
    exam='“KRaft vs ZooKeeper?” KRaft stores metadata in __cluster_metadata replicated by Raft among controller voters; active controller = quorum leader; brokers fetch the log; faster failover, more partitions, one system. ZooKeeper removed in 4.0; migrate on 3.x (3.9 bridge).',
    types_h2='Node roles and tools', types_html=types_html, warn=warn,
    steps_h2='Open the cluster’s brain', steps_intro='All outputs are real: Kafka 4.4.0, 3 combined KRaft nodes, cluster TiffinGoKafkaLab0001A.',
    steps=steps, two=two, peel_intro='Now peel one metadata change.', peel_html=pe,
    scen_intro='Three live scenarios: an old tutorial, a migration, and a lost quorum.', scen=scen,
    uc_h2='KRaft at work', ucs=[uc_('new', '4.x', 'green', '1. Every new cluster', 'KRaft is the only mode.', ['Format', '*KRaft', 'Run']),
        uc_('big', 'scale', 'blue', '2. Huge partition counts', 'Metadata as a log scales further.', ['Topics', '*log', 'Millions']),
        uc_('mig', 'upgrade', 'amber', '3. Legacy migrations', 'ZooKeeper clusters move via 3.9.', ['ZK', '*migrate', 'KRaft']),
        uc_('ops', 'debug', 'violet', '4. Debugging', 'Quorum and metadata tools.', ['Issue', '*inspect', 'Fix'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../03-leader-election/">5.3 Leader election</a>.')
