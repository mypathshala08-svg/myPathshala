import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l104_mm2.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('Your whole data centre goes dark. A second Kafka cluster in another region has a copy of the orders, but where should the kitchen consumer continue: offset 600, offset 0, or somewhere else?',
    '<b>MirrorMaker 2</b> copies topics to another cluster as <code>primary.orders-104</code> and also <b>translates consumer offsets</b>. In our lab the group had committed 600 on the primary; on DR it resumed at <b>405</b>, not 0 and not exactly 600. That gap is by design: failover is <b>at-least-once</b>, so consumers must handle a few hundred duplicates.',
    ['Why and when to run more than one cluster.',
     'How MirrorMaker 2 works: remote topics, heartbeats, checkpoints, offset syncs.',
     'Failover and failback, and their limits.'])
cmap = concept_map('Concept map. Beginner: backup copy, region, disaster. Intermediate: MirrorMaker 2, remote topics, offset translation, active-passive. Advanced: active-active, replication policy, RPO/RTO, Cluster Linking and other replicators.',
    [[('rp', 'Replication in a cluster', 'Lesson 5.1', B + '05-replication-and-the-cluster/01-brokers-and-replication/'), ('kc', 'Kafka Connect', 'Lesson 7.1', B + '07-kafka-connect/01-kafka-connect/')],
     [('mm', 'MirrorMaker 2', 'Connect-based', None), ('rt', 'Remote topics', 'primary.orders', None), ('ot', 'Offset translation', 'checkpoints', None), ('ap', 'Active-passive DR', 'failover', None)],
     [('aa', 'Active-active', 'two writers', None), ('rr', 'RPO / RTO', 'how much, how fast', None), ('cl', 'Other replicators', 'Cluster Linking …', None), ('id', 'Idempotent consumers', 'Lesson 3.4', B + '03-consumers/04-delivery-guarantees/')]],
    [('rp', 'mm'), ('kc', 'mm'), ('mm', 'rt'), ('mm', 'ot'), ('ot', 'ap'), ('rt', 'aa'), ('ap', 'rr'), ('mm', 'cl'), ('ot', 'id')],
    {'mm', 'rt', 'ot', 'ap', 'aa', 'rr', 'cl'},
    '<b>Builds on:</b> <a href="../../05-replication-and-the-cluster/01-brokers-and-replication/">5.1</a>, <a href="../../07-kafka-connect/01-kafka-connect/">7.1</a>. <b>Next:</b> Module 11 Kafka in industry.')
whw = why_how_where(
    'Replication inside a cluster survives broker or zone failures, not a region outage, a cloud account loss, or a bad operator command. Some data must also live near users or in separate clusters for compliance and isolation.',
    'MM2 runs as Kafka Connect source connectors: MirrorSourceConnector copies records and configs into prefixed remote topics; MirrorCheckpointConnector maps group offsets using offset-sync records and can sync them into the target; MirrorHeartbeatConnector proves the link is alive.',
    'Disaster recovery (active-passive), aggregation from edge/regional clusters to a central one, migrations between clusters or to the cloud, and geo-local reads.',
    'Asynchronous: the DR copy is slightly behind (RPO > 0). Offsets differ between clusters; translation is conservative, so expect re-processing. Active-active needs care to avoid loops (MM2’s prefixes prevent them).')

def dc(hl=-1):
    o = box(8, 34, 130, 80, 'blue' if hl != 0 else 'acc', rx=8) + t(73, 52, 'primary (k1-k3)', 7.8, bold=True) + t(73, 72, 'orders-104', 7.4, mono=True) + t(73, 90, 'group @600', 7.4, mono=True)
    o += box(214, 34, 140, 80, 'green' if hl != 2 else 'acc', rx=8) + t(284, 52, 'DR (dr1)', 7.8, bold=True) + t(284, 72, 'primary.orders-104', 7.0, mono=True) + t(284, 90, 'group @405', 7.4, mono=True)
    o += box(144, 58, 64, 30, 'amber' if hl != 1 else 'acc', rx=6) + t(176, 77, 'MM2', 8, bold=True) + arrow(138, 73, 144, 73) + arrow(208, 73, 214, 73)
    return o
scene_svg = scene('MirrorMaker 2 copies topic orders-104 from the primary cluster to the DR cluster as primary.orders-104, and translates the consumer group offset from 600 on primary to 405 on DR.', dc(),
                  'Copy the data <tspan font-weight="700" class="s-acc">and</tspan> the place where each consumer was.')
dialogue = '''K> Sir, management asks: if the Mumbai region fails, how fast can kitchens continue from the Hyderabad cluster?
A> We mirror topics there with MirrorMaker 2. It also translates consumer offsets, so consumers don’t restart from zero.
R> Exactly where they stopped?
A> Close, but a bit earlier, so some orders are processed twice. Let’s measure how much.'''

lv = '''
LEVELS> Multi-cluster at three levels
L1> A photocopy in another city
      <ul>
        <li>Every page of the register is photocopied to a branch in another city, a few seconds later. If the main office burns, the branch continues, re-checking the last few pages because it is not sure which were already handled.</li>
      </ul>
L2> MirrorMaker 2 pieces
      <ul>
        <li>Config: <code>clusters = primary, dr</code>, bootstrap servers per cluster, <code>primary->dr.enabled</code>, <code>primary->dr.topics</code> / <code>.groups</code> (regex). Run with <code>connect-mirror-maker.sh mm2.properties</code> or as connectors on a Connect cluster.</li>
        <li><b>Remote topics</b> get the source alias as prefix (DefaultReplicationPolicy): <code>primary.orders-104</code>. Internal: <code>heartbeats</code>, <code>primary.checkpoints.internal</code>, <code>mm2-offset-syncs…</code>, plus mm2 configs/offsets/status.</li>
        <li><code>sync.group.offsets.enabled=true</code> writes translated offsets into the DR cluster’s group, so a consumer can just start there.</li>
      </ul>
L3> Design for failure
      <ul>
        <li>RPO = data you can lose (replication lag); RTO = time to switch (DNS, configs, consumer restarts). Measure both in drills.</li>
        <li>Offset translation uses periodic offset-sync points (<code>offset.lag.max</code>, 100 by default), so the translated offset is at or before the true one: plan for duplicates (idempotent consumers, Lesson 3.4).</li>
        <li>Failback: mirror DR → primary for the period of the outage, or use an identity replication policy for migrations. Alternatives: Confluent Cluster Linking (offset-preserving byte copy), Redpanda/WarpStream replication features, or dual writes (rarely good).</li>
      </ul>
/LEVELS
'''
TP = figure('DR cluster topics after MirrorMaker 2 started: the remote topic primary.orders-104, the internal topics heartbeats, primary.heartbeats, primary.checkpoints.internal and mm2 configs, offsets and status topics.',
    t(16, 22, 'What MM2 created on DR (real list)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('primary.orders-104', 'green', 1), ('primary.checkpoints.internal', 'amber', 2), ('heartbeats · primary.heartbeats', 'blue', 3), ('mm2-configs/offsets/status', 'card', 4)]) +
    legend(16, 84, [(1, 'Remote topic', 'the data, prefixed with the source cluster alias'), (2, 'Checkpoints', 'translated group offsets'),
                    (3, 'Heartbeats', 'link liveness and topology'), (4, 'Connect state', 'MM2 runs on Kafka Connect')], size=8, gap=15, w=90),
    h=158, caption='Offset-sync records live on the source side by default.')
extra = '''

  <h3>The topics MirrorMaker 2 creates</h3>
''' + TP

types_html = table(['Pattern', 'Writers', 'Use', 'Watch out'], [
    ['Active-passive (DR)', 'primary only', 'region failure', 'RPO > 0, duplicates on failover'], ['Active-active', 'both', 'local writes in two regions', 'conflicts; consumers read local + remote topics'],
    ['Aggregation (hub)', 'edges', 'central analytics', 'bandwidth, prefixes'], ['Migration', 'old → new', 'move cluster/cloud', 'cut-over plan, identity policy'],
], minw=620) + table(['Replicator', 'Offsets', 'Notes'], [
    ['MirrorMaker 2 (Apache)', 'translated (≤ true offset)', 'Connect-based, open source'], ['Confluent Cluster Linking', 'preserved', 'commercial, byte-for-byte'],
    ['Vendor replication (MSK Replicator, etc.)', 'varies', 'managed services'],
], minw=520)
warn = 'Practise failover before you need it. Write the runbook (stop producers, wait for lag ~0, switch bootstrap servers, start consumers on DR), run it every quarter, and make consumers idempotent: our drill re-delivered 195 orders.'

steps = [
    ('Step 1 · Primary state',
     code('bash', 'terminal', 'seq 1 1000 | … kafka-console-producer.sh --topic orders-104\nkafka-console-consumer.sh --topic orders-104 --group kitchen-104 --max-messages 600', sec('== 1)', '== 2)')),
     '1,000 orders (keyless, so all landed in p2), group kitchen-104 committed 600.'),
    ('Step 2 · Start MirrorMaker 2',
     code('properties', 'mm2.properties', 'clusters = primary, dr\nprimary.bootstrap.servers = k1:9092,k2:9092,k3:9092\ndr.bootstrap.servers = dr1:9092\nprimary->dr.enabled = true\nprimary->dr.topics = orders-104\nprimary->dr.groups = kitchen-104\nprimary->dr.sync.group.offsets.enabled = true', sec('== 2)', '== 3)')),
     'One command: <code>connect-mirror-maker.sh mm2.properties</code>. MM2 created the remote topic and its internal topics on DR.'),
    ('Step 3 · The copy',
     code('bash', 'terminal', 'kafka-get-offsets.sh --bootstrap-server dr1:9092 --topic primary.orders-104', sec('== 3)', '== 4)')),
     'All 1,000 records, same partition layout.'),
    ('Step 4 · Translated offset',
     code('bash', 'terminal', 'kafka-consumer-groups.sh --bootstrap-server dr1:9092 --describe --group kitchen-104', sec('== 4)', '== 5)')),
     'The group exists on DR at 405, not 600: translation steps back to the last offset-sync point it can prove.'),
    ('Step 5 · Failover',
     code('bash', 'terminal', 'kafka-console-consumer.sh --bootstrap-server dr1:9092 --topic primary.orders-104 --group kitchen-104', sec('== 5)', '== 6)')),
     'The consumer continued at order-406: no restart from 0, but orders 406–600 are processed a second time.'),
    ('Step 6 · Still mirroring',
     code('bash', 'terminal', 'seq 1001 1010 | … producer on primary; sleep 12; kafka-get-offsets on dr1', sec('== 6)')),
     'Ten new orders arrived on DR within seconds (this time in p1).'),
]
see = [term([('p2 committed 600', W), ('end 1000', W)], size=7.2), term([('primary.orders-104', G), ('primary.checkpoints.internal', W), ('heartbeats', W)], size=6.8),
       term([('primary.orders-104:2:1000', G)], size=7.0), term([('DR group @405', Y), ('(primary @600)', W)], size=7.2),
       term([('first on DR: order-406', Y)], size=7.2), term([('p1: 10 new', G)], size=7.2)]
B1 = [dc(0), dc(1), dc(2), dc(2), dc(2), dc(1)]
B1 = [b + cap(c, '', tn, y=128, h=30) for b, c, tn in zip(B1, ['Primary at 600', 'MM2 starts', 'Copy complete', 'Offset → 405', 'Failover continues', 'Live mirroring'], ['blue', 'amber', 'green', 'amber', 'green', 'blue'])]
two = anim_two('MirrorMaker 2', 'Copy, translate, fail over', 'Real outputs from the lab', 'Two clusters', see, B1, ['Primary.', 'Start.', 'Copy.', 'Translate.', 'Failover.', 'Live.'], ['600.', 'MM2.', '1000.', '405.', '406.', 'Flow.'])
pe = peel('Offset translation, layer by layer', 'Group at 600 on primary. (Simplified.)',
    [('Copy', ''), ('Offset sync', ''), ('Checkpoint', ''), ('Translate', ''), ('Sync group', ''), ('Resume', '')],
    [['Copy', 'source offset → target offset', 'may differ', ''], ['Offset sync', 'every ~100 offsets', '(source, target) pairs', ''], ['Checkpoint', 'group committed 600', 'read periodically', ''],
     ['Translate', 'last sync ≤ 600', '→ target 405', 'safe, never ahead'], ['Sync group', 'write 405 into', 'DR group kitchen-104', ''], ['Resume', 'consumer on DR', 'starts at 405', 'duplicates 406–600']],
    ['Copy.', 'Pair.', 'Read.', 'Map.', 'Write.', 'Resume.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Region outage drill', 'Planned failover test. (Typical.)', ('Active-passive', 'Runbook + MM2'), [
    ('Stop primary producers', 'lag → ~0', 'Drain.', 'amber'), ('Switch apps to DR', 'bootstrap servers', 'Cut over.', 'blue'),
    ('Consumers resume', 'translated offsets', 'Continue.', 'green'), ('Duplicates handled', 'idempotent writes', 'Correct.', 'green'),
    ('Measure RTO', '8 minutes', 'Improve.', 'blue')], ['Drain.', 'Switch.', 'Resume.', 'Dedupe.', 'Measure.'], 'scenario-drill') + \
       five('Real-time scenario 2', 'Move to the cloud', 'On-prem → managed Kafka. (Typical.)', ('Migration', 'Mirror, then cut over'), [
    ('Mirror all topics', 'identity policy (same names)', 'Copy.', 'blue'), ('Consumers move first', 'translated offsets', 'Read new.', 'green'),
    ('Producers move', 'stop old writes', 'Write new.', 'green'), ('Verify counts', 'end offsets, checksums', 'Check.', 'amber'),
    ('Retire old cluster', 'after retention', 'Done.', 'blue')], ['Mirror.', 'Consumers.', 'Producers.', 'Verify.', 'Retire.'], 'scenario-migrate') + \
       five('Real-time scenario 3 · advanced', 'Two regions both write', 'Active-active. (Typical.)', ('Prefixes stop loops', 'Read local + remote'), [
    ('Mumbai and Delhi accept orders', 'each local cluster', 'Two writers.', 'blue'), ('MM2 both ways', 'mumbai.orders, delhi.orders', 'Prefixed.', 'green'),
    ('No infinite loop', 'MM2 skips remote topics', 'Safe.', 'green'), ('Consumers subscribe', 'orders + *.orders', 'Full view.', 'amber'),
    ('Conflicts by design', 'key ownership per region', 'Rules.', 'blue')], ['Write.', 'Mirror.', 'No loop.', 'Read.', 'Own.'], 'scenario-aa')
assemble(HERE, h2_story='When a whole region fails', hook_html=hk,
    narration='TiffinGo’s board asks what happens if the Mumbai cloud region goes down during dinner rush. Kabir sets up a DR cluster and runs a failover drill.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Multi-cluster and MirrorMaker 2',
    formal='<b>Multi-cluster</b> architectures replicate data between independent Kafka clusters for disaster recovery, geo-locality, aggregation or migration. <b>MirrorMaker 2</b> (KIP-382) is Apache Kafka’s Connect-based replicator: it copies topics (data, partitions and configs) to <b>remote topics</b> named by a replication policy, emits heartbeats, and records checkpoints that <b>translate consumer-group offsets</b> between clusters, optionally syncing them into target groups. Replication is asynchronous.',
    simple='MirrorMaker 2 keeps a copy of your topics in another cluster, a few seconds behind, and remembers roughly where each consumer group was, so after a disaster consumers can continue there (with some repeats).',
    term_rows=[('DR', 'Disaster recovery.'), ('MirrorMaker 2', 'Cluster-to-cluster copier.'), ('Remote topic', 'Prefixed copy.'), ('Checkpoint', 'Translated group offset.'), ('Offset sync', 'Source↔target offset pair.'), ('RPO', 'Data you may lose.'), ('RTO', 'Time to recover.'), ('Failback', 'Return to primary.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Offsets are identical across clusters.', 'They differ; MM2 translates.', 'Step 4.'),
               ('Failover is exactly-once.', 'Translated offsets are earlier: duplicates.', 'Step 5: from 406.'),
               ('RF 3 covers region loss.', 'Only within the cluster’s zones.', 'Why box.')],
    exam='“How do you do Kafka DR?” Second cluster + MirrorMaker 2 (remote prefixed topics, heartbeats, checkpoints, offset translation, sync.group.offsets); active-passive vs active-active; RPO/RTO; at-least-once failover; runbooks and drills; Cluster Linking alternative.',
    types_h2='Patterns and replicators', types_html=types_html, warn=warn,
    steps_h2='A failover drill', steps_intro='All outputs are real: primary = our 3-broker Kafka 4.4 cluster, DR = single broker dr1, MirrorMaker 2 from Kafka 4.4.0.',
    steps=steps, two=two, peel_intro='Now peel offset translation.', peel_html=pe,
    scen_intro='Three live scenarios: a drill, a migration, and active-active.', scen=scen,
    uc_h2='Multi-cluster at work', ucs=[uc_('dr', 'DR', 'red', '1. Disaster recovery', 'Region outage plan.', ['Primary', '*MM2', 'DR']),
        uc_('edge', 'edge', 'blue', '2. Edge to core', 'Stores/factories to central.', ['Edges', '*mirror', 'Core']),
        uc_('mig', 'migrate', 'amber', '3. Migrations', 'On-prem → cloud.', ['Old', '*mirror', 'New']),
        uc_('geo', 'geo', 'green', '4. Geo-local reads', 'Data near users.', ['Region A', '*copy', 'Region B'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../../07-kafka-connect/01-kafka-connect/">7.1 Connect</a>.')
