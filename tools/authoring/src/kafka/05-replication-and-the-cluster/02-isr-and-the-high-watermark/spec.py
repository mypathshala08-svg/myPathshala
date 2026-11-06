import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
BODY = body(HERE)
META = dict(module='05-replication-and-the-cluster', lesson='02-isr-and-the-high-watermark', n='5.2', module_label='Module 5 · Replication and the cluster',
    title='ISR and the high watermark',
    desc='The in-sync replica set (ISR), replica.lag.time.max.ms, the log end offset (LEO) and the high watermark (HW): why consumers only see committed records, and how acks and min.insync.replicas interact with a slow follower. Real Kafka 4.4 lab: a paused follower freezes the HW at 5, is removed from the ISR after about 10 s, and rejoins after it catches up.',
    og_desc='A frozen follower, a stuck high watermark, and an ISR that shrinks then heals: Kafka 4.4 lab.',
    minutes=22, level='Intermediate',
    lead='Why can a consumer not read a record the leader already has? We <b>pause a follower</b> and watch the <b>high watermark</b> stop, the <b>ISR</b> shrink and then heal. <b>All outputs are real.</b>',
    chips=['HW stuck at 5', 'ISR 1,2,3 → 1,2 → 1,2,3', 'LEO vs HW', 'Runs in your browser (Python)'])
MAIN = '''# High watermark = smallest LEO among ISR members
leo = {1: 10, 2: 10, 3: 5}          # broker -> log end offset
isr = {1, 2, 3}
lag_ms = {1: 0, 2: 0, 3: 35000}
MAX_LAG = 30000                      # replica.lag.time.max.ms (Kafka 4.x default)

def hw(isr):
    return min(leo[b] for b in isr)

print("HW with slow follower in ISR:", hw(isr))
isr = {b for b in isr if lag_ms[b] <= MAX_LAG}
print("ISR after lag check:", sorted(isr))
print("HW now:", hw(isr))
'''
RUN = dict(heading='Run the code: computing the high watermark', intro='<p>The HW rule in a few lines. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    return min(leo[b] for b in isr)', 'Committed = copied by every ISR member.'), ('isr = {b for b in isr if lag_ms[b] <= MAX_LAG}', 'A lagging follower is removed: HW can move again.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Then set lag of 3 to 0.', code=None),
        dict(label='2 · Predict first: HW', hint='<b>Predict first:</b> LEOs 8, 7, 9.', code='print(min([8, 7, 9]))\n'),
        dict(label='3 · Visible records', hint='Consumer sees offsets below HW.', code='hw = 5\nprint(list(range(hw)))\n'),
        dict(label='4 · min ISR', hint='acks=all with ISR 1 and min.insync 2.', code='isr, min_isr = 1, 2\nprint("accepted" if isr >= min_isr else "NotEnoughReplicas")\n'),
        dict(label='5 · Spot the error', hint='Write rejected.', expect='error', code='isr, min_isr = 1, 2\nif isr < min_isr:\n    raise RuntimeError("NOT_ENOUGH_REPLICAS: ISR 1 < min.insync.replicas 2")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: freeze a follower', intro='<p>Needs the 3-broker Docker lab. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Check ISR', cmd='kafka-topics.sh --bootstrap-server k1:9092 --describe --topic hw-52', file='terminal', output='Topic: hw-52  Partition: 0  Leader: 1  Replicas: 1,2,3  Isr: 1,2,3', note='All in sync.'),
           dict(title='2 · Pause a follower', cmd='docker pause k3', file='terminal', output='k3', note='Process frozen, no fetches.'),
           dict(title='3 · Watch ISR shrink', cmd='kafka-topics.sh --bootstrap-server k1:9092 --describe --topic hw-52', file='terminal', output='Topic: hw-52  Partition: 0  Leader: 1  Replicas: 1,2,3  Isr: 1,2', note='After ~9.6 s in our lab: k3 was fenced (9 s session timeout), faster than the 30 s lag rule.'),
           dict(title='4 · Heal', cmd='docker unpause k3; kafka-topics.sh --bootstrap-server k1:9092 --describe --under-replicated-partitions', file='terminal', output='', note='Empty output = no URP.')])
TRACE = dict(heading='One write, step by step', intro='<p>LEO moves first, HW follows.</p>',
    code='leo = {1: 5, 2: 5, 3: 5}\nleo[1] = 10\nleo[2] = 10\nhw = min(leo[b] for b in (1, 2, 3))\nprint(hw)\n',
    notes={2: 'Leader append :: LEO 10 on leader only.', 3: 'Follower fetch :: Broker 2 catches up.', 4: 'HW :: Still 5 because broker 3 is behind.'})
WORKED_INTRO = 'Three ISR decisions.'
EXAMPLES = [
    dict(level='b', tag='ISR · visibility', title='Why the consumer waits', problem='<p>Leader has offset 9, consumer only reads up to 4.</p>', inp='LEO, HW',
         approach=['HW = 5.', 'Records ≥ HW are not committed.', 'Consumers read below HW.'], code='leo, hw = 10, 5\nprint("visible:", hw, "hidden:", leo - hw)\n', notes={1: 'Safety :: Never read data that could vanish.'}, tryit='Run task 3.'),
    dict(level='i', tag='ISR · durability', title='acks=all vs acks=1', problem='<p>One follower is slow.</p>', inp='acks',
         approach=['acks=1: OK immediately (lab 0.00 s).', 'acks=all: waits for ISR.', 'After shrink, acks=all proceeds with ISR 2 ≥ min 2.'], code='print({"acks=1": "fast, risky", "acks=all + min.insync=2": "safe"})\n', notes={1: 'Trade-off :: Latency vs durability.'}, tryit='Scenario 2.'),
    dict(level='a', tag='ISR · tuning', title='Pick replica.lag.time.max.ms', problem='<p>ISR flaps during GC pauses.</p>', inp='ms',
         approach=['Default 30 s (4.x).', 'Too low → flapping.', 'Too high → slow writes wait longer.'], code='print({"replica.lag.time.max.ms": 30000})\n', notes={1: 'Balance :: Flapping vs stall.'}, tryit='Scenario 3.')]
QUIZ = mix([
    dict(q='Beginner: ISR stands for…', options=['In-sync replicas', 'Internal storage record', 'Index segment range', 'Input stream reader'], answer=0, why='Replicas caught up with the leader.'),
    dict(q='Beginner: Consumers read up to…', options=['LEO', 'High watermark', 'Segment end', 'Any offset'], answer=1, why='Only committed data.'),
    dict(q='Beginner: HW is…', options=['Max LEO', 'Min LEO in ISR', 'Average LEO', 'Leader LEO'], answer=1, why='Copied by all ISR.'),
    dict(q='Intermediate: In our lab, after pausing k3 the HW…', options=['Jumped to 10 immediately', 'Stayed 5 until ISR shrank', 'Went to 0', 'Disappeared'], answer=1, why='Moved to 10 after ~9.6 s.'),
    dict(q='Intermediate: A follower leaves the ISR when…', options=['It lags longer than replica.lag.time.max.ms', 'It has fewer messages once', 'The consumer is slow', 'The topic is compacted'], answer=0, why='Time-based.'),
    dict(q='Intermediate: acks=1 with a paused follower…', options=['Fails', 'Succeeds quickly', 'Blocks forever', 'Duplicates'], answer=1, why='Leader only.'),
    dict(q='Advanced: ISR 1 and min.insync.replicas 2 with acks=all gives…', options=['Success', 'NotEnoughReplicas error', 'Data loss', 'Rebalance'], answer=1, why='Write refused.'),
    dict(q='Advanced: URP means…', options=['Unread partitions', 'Under-replicated partitions', 'Unique record pointer', 'Unclean partition'], answer=1, why='ISR smaller than replicas.')])
REVISION = ['LEO = next offset per replica; HW = min LEO across ISR; consumers read below HW.', 'Follower out of ISR after replica.lag.time.max.ms without catching up.',
    'Lab: pause k3 → HW stays 5, ISR 1,2 after ~9.6 s, HW 10; unpause → ISR 1,2,3.', 'acks=all waits for ISR; min.insync.replicas sets the floor.', 'Monitor URP and IsrShrinksPerSec.']
FAQ = [('Does ISR shrink lose data?', 'No; it removes a slow copy so writes can continue. Data is lost only if all ISR copies are lost.'),
    ('Who decides ISR changes?', 'The partition leader proposes; in KRaft the controller records a PARTITION_CHANGE (AlterPartition).'),
    ('What is ELR?', 'Eligible Leader Replicas (KIP-966): replicas that left ISR but are known to hold all committed data, so they can safely become leader.'),
    ('Why did our follower leave after 9.6 s, not 30 s?', 'A paused broker also stops heartbeating to the controller; after broker.session.timeout.ms (9 s) it is fenced and removed from all ISRs at once. replica.lag.time.max.ms applies to a live but slow follower.'),
    ('Why does HW lag on followers?', 'Followers learn the HW from the leader in the next fetch response, so it is a little behind.')]
PRACTICE_INTRO = 'ISR and HW programs.'
PROBLEMS = [
    dict(level='easy', title='HW', stmt='HW for LEOs 12, 9, 11.', inp='list', code='print(min([12, 9, 11]))\n', explain='9.'),
    dict(level='easy', title='Hidden', stmt='Records leader has but consumers cannot see.', inp='numbers', code='print(12 - 9)\n', explain='3.'),
    dict(level='easy', title='URP?', stmt='Replicas 3, ISR 2.', inp='numbers', code='print(2 < 3)\n', explain='Under-replicated.'),
    dict(level='medium', title='Lag filter', stmt='Keep followers within 30 s.', inp='dict', code='lag = {2: 1000, 3: 45000}\nprint([b for b, l in lag.items() if l <= 30000])\n', explain='[2].'),
    dict(level='medium', title='Accept write?', stmt='acks=all, ISR 2, min 2.', inp='numbers', code='print(2 >= 2)\n', explain='Accepted.'),
    dict(level='medium', title='HW after shrink', stmt='Remove broker 3 then HW.', inp='dict', code='leo = {1: 10, 2: 10, 3: 5}\nprint(min(v for b, v in leo.items() if b != 3))\n', explain='10.'),
    dict(level='business', title='Tolerated failures', stmt='RF 3, min ISR 2.', inp='numbers', code='print(3 - 2, "broker can fail with writes on")\n', explain='1.'),
    dict(level='business', title='Alert', stmt='Alert if any URP.', inp='list', code='urp = ["orders-3"]\nprint("ALERT" if urp else "ok")\n', explain='Page on-call.')]
SCN_INTRO = 'ISR interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“What is the high watermark?”', 'Explain.', 'answer?', '<p>The offset up to which all in-sync replicas have the data. Consumers read only below it, so they never see a record that could disappear after a leader change.</p>', '“The biggest offset in the log.”') +
    scn('Fintech', 'Mid-level', 'Slow writes', 'acks=all latency spikes.', 'cause?', '<ul><li>A slow follower still in ISR.</li><li>Check disk/network; ISR shrinks after lag time.</li></ul>', 'Switching to acks=0.') +
    scn('Platform', 'Mid-level', 'ISR flapping', 'IsrShrinks every minute.', 'fix?', '<ul><li>GC or network stalls.</li><li>Tune JVM, check num.replica.fetchers, lag time.</li></ul>', 'Lowering RF.') +
    scn('Platform', 'Senior', 'NotEnoughReplicas', 'Producers fail after 2 brokers down.', 'decide?', '<ul><li>Intended: protects durability.</li><li>Restore brokers; avoid lowering min ISR unless loss acceptable.</li></ul>', 'Setting min.insync.replicas=1 silently.'))
