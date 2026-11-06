import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='05-replication-and-the-cluster', lesson='03-leader-election', n='5.3', module_label='Module 5 · Replication and the cluster',
    title='Leader election',
    desc='How Kafka elects partition leaders: failover from the ISR, leader epochs and fencing, preferred-leader elections and automatic rebalancing, controlled shutdown, unclean elections and Eligible Leader Replicas (KIP-966). Real Kafka 4.4 lab: a leader broker is killed during 160 writes and all 160 are delivered with a 9.8 s pause.',
    og_desc='Kill the leader mid-write: 160/160 delivered, 9.8 s pause. Kafka 4.4 leader election lab.',
    minutes=22, level='Intermediate',
    lead='What happens when a leader broker dies mid-write? We <b>kill it</b> under load, time the failover, and use a <b>preferred election</b> to put leadership back. <b>All outputs are real.</b>',
    chips=['160/160 delivered', '9.8 s failover', 'Preferred election', 'Runs in your browser (Python)'])
MAIN = '''# Simplified controller: elect a new leader from the ISR
replicas = [1, 2, 3]
isr = [1, 2, 3]
leader, epoch = 1, 4

def fail(broker):
    global leader, epoch, isr
    isr = [b for b in isr if b != broker]
    if leader == broker:
        candidates = [b for b in replicas if b in isr]
        leader = candidates[0] if candidates else None
        epoch += 1
    print(f"broker {broker} down -> leader {leader}, epoch {epoch}, isr {isr}")

fail(1)
fail(2)
'''
RUN = dict(heading='Run the code: a tiny controller', intro='<p>Elections in a few lines. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('        candidates = [b for b in replicas if b in isr]', 'Only ISR members, in replica order.'), ('        epoch += 1', 'New epoch fences the old leader.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Then add fail(3).', code=None),
        dict(label='2 · Predict first: preferred', hint='<b>Predict first:</b> preferred leader of [3, 1].', code='print([3, 1][0])\n'),
        dict(label='3 · Imbalance', hint='Broker leads 7 of 18 partitions; fair share 6.', code='print(round((7 - 6) / 6 * 100), "% > 10% -> rebalance")\n'),
        dict(label='4 · Quorum math', hint='Failures tolerated by RF 3, min ISR 2.', code='print(3 - 2)\n'),
        dict(label='5 · Spot the error', hint='Stale leader writes.', expect='error', code='current, request = 6, 5\nif request < current:\n    raise RuntimeError("FENCED_LEADER_EPOCH: 5 < 6")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: elections', intro='<p>Needs the 3-node lab. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Preferred election', cmd='kafka-leader-election.sh --bootstrap-server k1:9092 --election-type PREFERRED --topic small-51 --partition 0', file='terminal', output='Successfully completed leader election (PREFERRED) for partitions small-51-0', note='Leader → 3.'),
           dict(title='2 · Kill a leader', cmd='docker kill k1', file='terminal', output='k1', note='Run while producing.'),
           dict(title='3 · Who leads now', cmd='kafka-topics.sh --bootstrap-server k2:9092 --describe --topic rides-51', file='terminal', output='Topic: rides-51  Partition: 0  Leader: 2  Replicas: 1,2,3  Isr: 2,3', note='ISR member 2.'),
           dict(title='4 · All preferred', cmd='kafka-leader-election.sh --bootstrap-server k1:9092 --election-type PREFERRED --all-topic-partitions', file='terminal', output='', note='After restart.')])
TRACE = dict(heading='Failover step by step', intro='<p>Fence, choose, publish.</p>',
    code='isr = [1, 2, 3]\nisr.remove(1)\nleader = isr[0]\nepoch = 4 + 1\nprint(leader, epoch, isr)\n',
    notes={2: 'Fence :: Broker 1 missed heartbeats.', 3: 'Choose :: First live ISR replica.', 4: 'Epoch :: Old leader is fenced.'})
WORKED_INTRO = 'Three election decisions.'
EXAMPLES = [
    dict(level='b', tag='Election · failover', title='No loss on crash', problem='<p>Leader dies while orders arrive.</p>', inp='config',
         approach=['acks=all.', 'Retries + idempotence (defaults).', 'RF 3, min ISR 2.'], code='print({"acks": "all", "enable.idempotence": True, "min.insync.replicas": 2})\n', notes={1: 'Lab :: 160/160 delivered.'}, tryit='Step 3.'),
    dict(level='i', tag='Election · balance', title='Leaders after restart', problem='<p>Broker 3 leads most partitions.</p>', inp='counts',
         approach=['Wait for auto rebalance (300 s).', 'Or PREFERRED for all partitions.', 'Check LeaderCount.'], code='print("kafka-leader-election.sh --election-type PREFERRED --all-topic-partitions")\n', notes={1: 'Even :: Balance load.'}, tryit='Scenario 1.'),
    dict(level='a', tag='Election · unclean', title='Offline partition decision', problem='<p>ISR empty, logs topic.</p>', inp='topic',
         approach=['Payments: wait.', 'Logs: allow unclean per topic.', 'Document the loss.'], code='print({"payments": "unclean=false", "debug-logs": "unclean=true"})\n', notes={1: 'Per topic :: Not cluster-wide.'}, tryit='Scenario 2.')]
QUIZ = mix([
    dict(q='Beginner: Who chooses the new leader?', options=['The producer', 'The controller', 'The consumer', 'ZooKeeper (in 4.x)'], answer=1, why='Active controller.'),
    dict(q='Beginner: New leaders normally come from…', options=['Any replica', 'The ISR', 'The newest broker', 'Consumers'], answer=1, why='Caught-up copies.'),
    dict(q='Beginner: In our lab, records delivered after killing the leader…', options=['120/160', '160/160', '40/160', '0'], answer=1, why='Retries.'),
    dict(q='Intermediate: The ~10 s pause was mostly…', options=['Election time', 'Failure detection (session timeout)', 'Disk copy', 'Consumer lag'], answer=1, why='9 s session.'),
    dict(q='Intermediate: After broker 1 returned, the leader was…', options=['1 immediately', 'still 2', 'none', '3'], answer=1, why='Waits for rebalance.'),
    dict(q='Intermediate: A preferred election moves leadership to…', options=['The fastest broker', 'The first replica', 'The controller', 'Random'], answer=1, why='Replica order.'),
    dict(q='Advanced: The leader epoch prevents…', options=['Compression', 'Zombie leaders writing stale data', 'Rebalances', 'Retention'], answer=1, why='Fencing.'),
    dict(q='Advanced: An unclean election can…', options=['Never lose data', 'Lose committed records', 'Create partitions', 'Speed up acks'], answer=1, why='Out-of-sync leader.')])
REVISION = ['Controller elects new leader from ISR/ELR in replica order; epoch + 1.', 'Lab: killed leader 1 → leader 2, 160/160 delivered, 9.8 s gap (detection).',
    'Preferred election returns leadership; auto every 300 s if imbalance > 10%.', 'Unclean election: availability over data; off by default.', 'Controlled shutdown moves leaders before stop.']
FAQ = [('Can I make failover faster?', 'Lower broker.session.timeout.ms carefully; too low causes false fencing. Graceful shutdowns are near-instant anyway.'),
    ('Do consumers notice?', 'They get NOT_LEADER errors, refresh metadata and continue from their offsets; no data is skipped.'),
    ('What is leaderRecoveryState?', 'Shows whether a partition recovered after an unclean election (RECOVERING) or is normal (RECOVERED).'),
    ('Is ELR on by default?', 'In Kafka 4.x clusters with eligible.leader.replicas.version 1, as in our lab.')]
PRACTICE_INTRO = 'Election programs.'
PROBLEMS = [
    dict(level='easy', title='Next leader', stmt='Replicas [1,2,3], ISR [2,3], 1 died.', inp='lists', code='print([b for b in [1,2,3] if b in [2,3]][0])\n', explain='2.'),
    dict(level='easy', title='Epoch', stmt='Epoch after 3 elections from 4.', inp='int', code='print(4 + 3)\n', explain='7.'),
    dict(level='easy', title='Preferred?', stmt='Is leader 2 preferred for [1,2,3]?', inp='list', code='print(2 == [1,2,3][0])\n', explain='No.'),
    dict(level='medium', title='Offline', stmt='Leader if ISR empty and unclean off.', inp='list', code='isr = []\nprint(isr[0] if isr else None)\n', explain='None: offline.'),
    dict(level='medium', title='Skew', stmt='Leader counts {1:2,2:6,3:4}.', inp='dict', code='c = {1: 2, 2: 6, 3: 4}\nprint(max(c, key=c.get))\n', explain='Broker 2 hot.'),
    dict(level='medium', title='Gap', stmt='Longest gap between timestamps.', inp='list', code='ts = [0, 0.1, 0.2, 10.0, 10.1]\nprint(max(b - a for a, b in zip(ts, ts[1:])))\n', explain='9.8.'),
    dict(level='business', title='Lost writes', stmt='10/s for 9.8 s without retries.', inp='numbers', code='print(int(10 * 9.8))\n', explain='~98 at risk.'),
    dict(level='business', title='Fence check', stmt='Accept request epoch 7 when current 7?', inp='ints', code='print(7 >= 7)\n', explain='Yes.')]
SCN_INTRO = 'Election interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“What happens if a Kafka broker dies?”', 'Explain.', 'answer?', '<p>Partitions it led get a new leader from their ISR, chosen by the controller. Producers and consumers refresh metadata and retry. With RF 3 and acks=all no committed data is lost.</p>', '“The topic is lost.”') +
    scn('Platform', 'Mid-level', 'Hot broker', 'One broker leads 60%.', 'fix?', '<ul><li>Preferred election.</li><li>Check auto.leader.rebalance.enable.</li></ul>', 'Adding partitions.') +
    scn('Fintech', 'Mid-level', 'Unclean on?', 'Someone set unclean=true cluster-wide.', 'risk?', '<ul><li>Committed payments may vanish.</li><li>Set false; per-topic only for logs.</li></ul>', 'Ignoring it.') +
    scn('Platform', 'Senior', 'Slow failover', 'Producers stall 30 s on crash.', 'diagnose?', '<ul><li>Session timeout, client request.timeout/metadata.max.age.</li><li>Prefer controlled shutdown for maintenance.</li></ul>', 'Raising retries only.'))
