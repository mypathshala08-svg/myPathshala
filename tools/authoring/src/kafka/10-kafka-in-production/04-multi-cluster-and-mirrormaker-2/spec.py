import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='10-kafka-in-production', lesson='04-multi-cluster-and-mirrormaker-2', n='10.4', module_label='Module 10 · Kafka in production',
    title='Multi-cluster and MirrorMaker 2',
    desc='Running more than one Kafka cluster: disaster recovery, aggregation, migration and geo-replication with MirrorMaker 2 (remote topics, heartbeats, checkpoints, offset syncs, group offset sync), active-passive vs active-active, RPO and RTO, and alternatives such as Cluster Linking. Real Kafka 4.4 lab: 1,000 orders mirrored to a DR cluster and a failover drill where the consumer resumed at a translated offset of 405 instead of 600.',
    og_desc='A real failover drill with MirrorMaker 2: offset 600 on primary became 405 on DR.',
    minutes=22, level='Advanced',
    lead='What happens when a whole region fails? We mirror topics with <b>MirrorMaker 2</b>, read the <b>translated offsets</b>, and fail a consumer over to the DR cluster. <b>All outputs are real.</b>',
    chips=['primary.orders-104', '600 → 405', 'At-least-once failover', 'Runs in your browser (Python)'])
MAIN = '''# Offset translation from offset-sync points (MM2-style, simplified)
syncs = [(0, 0), (101, 101), (203, 203), (304, 304), (405, 405), (707, 707)]   # (source, target)
committed_on_primary = 600

def translate(src_offset):
    best = max((s, t) for s, t in syncs if s <= src_offset)   # last proven point
    return best[1]

t = translate(committed_on_primary)
print("primary committed:", committed_on_primary, "-> DR offset:", t)
print("records processed twice after failover:", committed_on_primary - t)
'''
RUN = dict(heading='Run the code: translation', intro='<p>Why DR resumes earlier. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    best = max((s, t) for s, t in syncs if s <= src_offset)   # last proven point', 'Never ahead of the truth.'), ('print("records processed twice after failover:", committed_on_primary - t)', 'Our lab: 195.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Add a sync at 590.', code=None),
        dict(label='2 · Predict first: name', hint='<b>Predict first:</b> remote topic name.', code='print("primary" + "." + "orders-104")\n'),
        dict(label='3 · RPO', hint='Replication lag 3 s at 2,000 msg/s.', code='print(3 * 2000, "messages at risk")\n'),
        dict(label='4 · Loop guard', hint='Skip remote topics.', code='topics = ["orders", "dr.orders"]\nprint([t for t in topics if "." not in t])\n'),
        dict(label='5 · Spot the error', hint='Unreachable DR.', expect='error', code='raise TimeoutError("Timed out waiting for a node assignment. Call: listTopics (dr.bootstrap.servers unreachable)")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: MirrorMaker 2', intro='<p>Needs two clusters. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Start', cmd='connect-mirror-maker.sh mm2.properties', file='terminal', output='', note='Dedicated MM2 mode.'),
           dict(title='2 · Remote topic', cmd='kafka-get-offsets.sh --bootstrap-server dr1:9092 --topic primary.orders-104', file='terminal', output='primary.orders-104:2:1000', note='Copied.'),
           dict(title='3 · Translated group', cmd='kafka-consumer-groups.sh --bootstrap-server dr1:9092 --describe --group kitchen-104', file='terminal', output='primary.orders-104 2 405 1000 595', note='Synced.')])
TRACE = dict(heading='Failover step by step', intro='<p>Translate, resume, dedupe.</p>',
    code='primary, dr = 600, 405\nreprocessed = list(range(dr + 1, primary + 1))\nprint(len(reprocessed), reprocessed[:3])\n',
    notes={2: 'Duplicates :: 406..600.'})
WORKED_INTRO = 'Three multi-cluster decisions.'
EXAMPLES = [
    dict(level='b', tag='DR · pattern', title='Choose a pattern', problem='<p>Survive region loss, one writer.</p>', inp='need',
         approach=['Active-passive.', 'MM2 primary → DR.', 'Runbook.'], code='print("active-passive + MM2")\n', notes={1: 'Simple :: Most common.'}, tryit='Types table.'),
    dict(level='i', tag='DR · consumers', title='Handle duplicates', problem='<p>195 orders re-delivered.</p>', inp='design',
         approach=['Idempotent writes (upsert by order id).', 'Or dedupe store.', 'Test in drills.'], code='print("INSERT … ON CONFLICT (order_id) DO NOTHING")\n', notes={1: 'Safe :: Lesson 3.4.'}, tryit='Step 5.'),
    dict(level='a', tag='DR · migration', title='Keep topic names', problem='<p>Migrate, no prefixes.</p>', inp='policy',
         approach=['IdentityReplicationPolicy.', 'One direction only.', 'Cut over, retire old.'], code='print({"replication.policy.class": "org.apache.kafka.connect.mirror.IdentityReplicationPolicy"})\n', notes={1: 'Careful :: Loops if bidirectional.'}, tryit='Scenario 2.')]
QUIZ = mix([
    dict(q='Beginner: MirrorMaker 2 copies…', options=['Brokers', 'Topics between clusters', 'Schemas only', 'Users'], answer=1, why='Replicator.'),
    dict(q='Beginner: Remote topic for orders from primary is…', options=['orders', 'primary.orders', 'orders.primary', 'dr.orders'], answer=1, why='Prefix.'),
    dict(q='Beginner: MM2 runs on…', options=['ZooKeeper', 'Kafka Connect', 'Spark', 'Flink'], answer=1, why='Connectors.'),
    dict(q='Intermediate: Group at 600 on primary resumed on DR at…', options=['0', '405', '600', '1000'], answer=1, why='Translated.'),
    dict(q='Intermediate: Failover with MM2 is…', options=['Exactly-once', 'At-least-once', 'At-most-once', 'Lossless always'], answer=1, why='Duplicates.'),
    dict(q='Intermediate: RPO means…', options=['Recovery time', 'Data you may lose', 'Replication factor', 'Partitions'], answer=1, why='Point objective.'),
    dict(q='Advanced: Prefixes in active-active prevent…', options=['Compression', 'Replication loops', 'ACLs', 'Lag'], answer=1, why='Skip remote topics.'),
    dict(q='Advanced: An offset-preserving alternative is…', options=['Cluster Linking', 'Compaction', 'Tiered storage', 'Share groups'], answer=0, why='Commercial.')])
REVISION = ['Multi-cluster for DR, aggregation, migration, geo.', 'MM2: source, checkpoint, heartbeat connectors; prefixed remote topics.',
    'Lab: 1,000 copied; group 600 → 405 on DR; consumer resumed at order-406; new orders keep flowing.', 'Failover at-least-once; idempotent consumers; RPO/RTO drills.', 'Active-active with prefixes; identity policy for migrations; Cluster Linking alternative.']
FAQ = [('Does MM2 copy ACLs and configs?', 'Topic configs and ACLs can be synced (sync.topic.configs, sync.topic.acls) with some limits.'),
    ('Why 405 not 600?', 'Offsets are translated only at offset-sync points; the result is the last safe point at or before 600.'),
    ('Can consumers read both clusters?', 'Yes: subscribe to orders and *.orders for active-active.'),
    ('Is MM1 still used?', 'Legacy MirrorMaker 1 was removed in Kafka 4.0; use MM2.')]
PRACTICE_INTRO = 'Multi-cluster programs.'
PROBLEMS = [
    dict(level='easy', title='Name', stmt='Remote name for payments from mumbai.', inp='str', code='print("mumbai.payments")\n', explain='Prefix.'),
    dict(level='easy', title='Duplicates', stmt='600 vs 405.', inp='ints', code='print(600 - 405)\n', explain='195.'),
    dict(level='easy', title='Copy check', stmt='Same end offsets?', inp='ints', code='print(1000 == 1000)\n', explain='Yes.'),
    dict(level='medium', title='Translate', stmt='Last sync ≤ 250.', inp='list', code='s = [0, 101, 203, 304]\nprint(max(x for x in s if x <= 250))\n', explain='203.'),
    dict(level='medium', title='Filter remote', stmt='Local topics only.', inp='list', code='ts = ["orders", "delhi.orders", "menu"]\nprint([t for t in ts if "." not in t])\n', explain='Local.'),
    dict(level='medium', title='Dedupe', stmt='Skip seen ids.', inp='list', code='seen, out = set(), []\nfor i in [405, 406, 406, 407]:\n    if i not in seen: seen.add(i); out.append(i)\nprint(out)\n', explain='Unique.'),
    dict(level='business', title='RTO', stmt='Steps 2+3+3 min.', inp='ints', code='print(2 + 3 + 3, "minutes")\n', explain='8.'),
    dict(level='business', title='Bandwidth', stmt='40 MB/s across regions per day.', inp='ints', code='print(round(40 * 86400 / 1024 / 1024, 1), "TB/day")\n', explain='~3.3.')]
SCN_INTRO = 'Multi-cluster interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“How do you replicate Kafka across regions?”', 'Explain.', 'answer?', '<p>Run a second cluster and replicate with MirrorMaker 2 (or a vendor tool). It copies topics, syncs configs and translates consumer offsets so consumers can fail over.</p>', '“Set RF to 6.”') +
    scn('Platform', 'Mid-level', 'Duplicates after failover', 'Business complains.', 'fix?', '<ul><li>Expected with translation.</li><li>Idempotent consumers.</li></ul>', 'Disable MM2.') +
    scn('Platform', 'Mid-level', 'DR lag', 'DR 10 min behind.', 'do?', '<ul><li>More MM2 tasks, bandwidth, compression.</li><li>Monitor replication latency.</li></ul>', 'Ignore it.') +
    scn('Architecture', 'Senior', 'Two regions write', 'Design.', 'answer?', '<ul><li>Active-active with prefixes.</li><li>Key ownership, consumers read local+remote.</li></ul>', 'Same topic names both ways without policy.'))
