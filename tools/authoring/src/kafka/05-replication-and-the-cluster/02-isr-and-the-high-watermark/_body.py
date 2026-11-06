import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l52_hw.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('The leader had 10 records. Consumers could see only 5. For almost ten seconds.',
    'We froze one follower and wrote 5 records with <code>acks=1</code>. The leader stored them instantly, but consumers were not allowed to read them: the <b>high watermark</b> waited for every in-sync replica. Only when Kafka kicked the frozen follower out of the <b>ISR</b> did the watermark jump. That one rule is why consumers never read data that could be lost.',
    ['What the ISR is and how a replica falls out of it.',
     'The difference between log end offset and high watermark.',
     'Why a single slow follower can delay what consumers see.'])
cmap = concept_map('Concept map. Beginner: ISR, follower lag, under-replicated. Intermediate: high watermark, log end offset, replica.lag.time.max.ms, broker fencing. Advanced: acks and min ISR, leader epoch truncation, eligible leader replicas.',
    [[('is', 'ISR', 'caught-up replicas', None), ('fl', 'Follower lag', 'falling behind', None), ('ur', 'Under-replicated', 'ISR < replicas', None)],
     [('hw', 'High watermark', 'consumer limit', None), ('le', 'Log end offset', 'leader’s last + 1', B + '04-storage-internals/01-the-commit-log-and-segments/'), ('lt', 'replica.lag.time.max.ms', '30 s', None), ('fe', 'Broker fencing', 'session timeout', None)],
     [('ak', 'acks + min ISR', 'Lesson 2.4', B + '02-producers/04-acks-and-durability/'), ('tr', 'Truncation by epoch', 'after failover', None), ('el', 'ELR', 'Lesson 5.3', B + '05-replication-and-the-cluster/03-leader-election/')]],
    [('is', 'hw'), ('fl', 'lt'), ('fl', 'fe'), ('lt', 'ur'), ('hw', 'le'), ('hw', 'ak'), ('is', 'el'), ('hw', 'tr')],
    {'is', 'fl', 'ur', 'hw', 'le', 'lt', 'fe'},
    '<b>Builds on:</b> <a href="../01-brokers-and-replication/">5.1</a>. <b>Next:</b> <a href="../03-leader-election/">5.3 Leader election</a>.')
whw = why_how_where(
    'If consumers read a record that only the leader has, and the leader dies, that record vanishes after failover: consumers would have seen “ghost” data.',
    'The leader tracks each follower’s fetch position. Followers that keep up form the ISR. The high watermark is the smallest log end offset in the ISR; consumers can read only below it. Laggards are dropped from the ISR so they cannot block progress forever.',
    'Every replicated partition; monitoring “under-replicated partitions” and ISR shrink/expand events is standard operations.',
    'A slow follower still in the ISR delays the high watermark (and acks=all) until it is removed.')

sc_ = (''.join(box(40 + k * 44, 30, 40, 26, 'green' if k < 5 else 'amber', rx=3) + t(60 + k * 44, 47, str(k), 8, 'ink', mono=True) for k in range(10)) + t(30, 47, 'leader', 7.6, 'ink', anchor='end', bold=True) +
       ''.join(box(40 + k * 44, 66, 40, 26, 'green' if k < 10 else 'card', rx=3) + t(60 + k * 44, 83, str(k), 8, 'ink', mono=True) for k in range(10)) + t(30, 83, 'k2', 7.6, 'ink', anchor='end', bold=True) +
       ''.join(box(40 + k * 44, 102, 40, 26, 'green' if k < 5 else 'card', rx=3) for k in range(5)) + t(30, 119, 'k3 ❄', 7.6, 'red', anchor='end', bold=True) +
       arrow(258, 22, 258, 136, 'red', 2) + t(262, 140, 'high watermark = 5', 8, 'red', anchor='start', bold=True) +
       t(540, 60, 'leader LEO 10', 8, 'ink', bold=True) + t(540, 76, 'k2 LEO 10', 8, 'ink', bold=True) + t(540, 92, 'k3 frozen at 5', 8, 'red', bold=True) + t(540, 120, 'consumers read < 5', 8, 'acc', bold=True))
scene_svg = scene('The leader and follower k2 have offsets 0 to 9, but frozen follower k3 has only 0 to 4. The high watermark stays at 5, so consumers can read only offsets below 5 until k3 leaves the ISR.', sc_,
                  'Consumers stop at the <tspan font-weight="700" class="s-acc">high watermark</tspan>, not at the leader’s end.')
dialogue = '''R> Sir, the producer got “OK” for 5 records, but my consumer doesn’t see them. Is my consumer broken?
A> No. The producer used <code>acks=1</code>, so only the leader had to store them. But consumers may read only up to the <b>high watermark</b>: the point that every in-sync replica has reached.
K> And one of our followers is stuck.
A> Exactly. Until Kafka removes it from the <b>ISR</b>, the watermark cannot move. Let’s freeze a follower and time it.'''

lv = '''
LEVELS> ISR and high watermark at three levels
L1> A class that waits
      <ul>
        <li>The teacher (leader) writes 10 lines on the board. Notes are “official” only up to the line that every listed student has copied. If one student falls asleep, the teacher waits a little, then removes them from the list and moves on.</li>
      </ul>
L2> The definitions
      <ul>
        <li><b>LEO</b> (log end offset): next offset a replica will write. <b>HW</b> (high watermark): the minimum LEO across the ISR. Consumers fetch only offsets &lt; HW.</li>
        <li><b>ISR</b>: the leader plus followers that are caught up. A follower that has not caught up for <code>replica.lag.time.max.ms</code> (30 s) is removed; it is added back when it catches up.</li>
        <li><b>Under-replicated partition</b>: ISR smaller than the replica list; the key replication health metric.</li>
      </ul>
L3> KRaft details
      <ul>
        <li>In KRaft a broker that stops heartbeating to the controller is <b>fenced</b> after <code>broker.session.timeout.ms</code> (9 s), and removed from every ISR at once: that is why our frozen follower left after about 9.6 s, not 30 s.</li>
        <li>With acks=all, the leader answers the producer only when the HW passes the batch: a stuck in-sync follower delays acks too.</li>
        <li>After a leader change, followers truncate any data above the new leader’s log using <b>leader epochs</b> (leader-epoch-checkpoint), so replicas never diverge.</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of the high watermark timeline: before the pause HW 5 with ISR 1,2,3; at t plus 0 the leader has 10 records but HW stays 5; at t plus 9.6 seconds HW becomes 10 and ISR is 1,2; after unpausing ISR is 1,2,3 again.',
    t(16, 22, 'Timeline of partition hw-52b (real)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('HW 5 · ISR 1,2,3', 'green', 1), ('pause k3', 'red', None), ('acks=1: LEO 10', 'amber', 2)]) +
    fields(16, 70, [('t+0.0 s HW 5', 'amber', 3), ('t+9.6 s HW 10 · ISR 1,2', 'green', 4), ('unpause → ISR 1,2,3', 'blue', 5)]) +
    legend(16, 122, [(1, 'Healthy', 'all three replicas in sync; HW = LEO = 5'), (2, 'Leader-only write', 'acks=1 returned at once; leader LEO is 10'),
                     (3, 'Invisible', 'consumers still limited to offsets < 5'), (4, 'Shrink', 'k3 fenced after ~9 s session timeout → removed → HW jumps'),
                     (5, 'Expand', 'k3 catches up and is added back')], size=8, gap=15, w=120),
    h=210, caption='Real values from our lab run.')
extra = '''

  <h3>Dissect the timeline</h3>
''' + DIS + '''

  <h3>The offset ruler, replicated</h3>
''' + offset_ruler('Log start 0, high watermark 5 (committed marker position), leader log end 10.', n_total=10, committed=5, label='Leader of hw-52b while k3 is frozen (HW plays the role of the green marker)')

types_html = table(['Signal', 'Meaning', 'Action'], [
    ['ISR shrink (log line / metric)', 'a follower fell behind or was fenced', 'check that broker: GC, disk, network'],
    ['UnderReplicatedPartitions > 0', 'some partitions have fewer in-sync copies', 'alert; durability reduced'],
    ['UnderMinIsrPartitionCount > 0', 'acks=all writes are failing there', 'urgent'],
    ['OfflinePartitionsCount > 0', 'no leader at all', 'critical (Lesson 5.3)'],
], minw=600) + table(['Setting', 'Default', 'Effect'], [
    ['replica.lag.time.max.ms', '30000', 'max time a follower may be behind and stay in ISR'],
    ['broker.session.timeout.ms', '9000', 'KRaft: missing heartbeats → broker fenced'],
    ['num.replica.fetchers', '1', 'parallel fetcher threads per source broker'],
], minw=560)
warn = 'Do not “fix” ISR shrinks by raising <code>replica.lag.time.max.ms</code> a lot: you keep a slow replica in the ISR, so every acks=all write and the high watermark wait for it. Fix the slow broker (disk, GC, network) instead.'

steps = [
    ('Step 1 · Healthy partition',
     code('python', 'l52_hw.py', 'sh("kafka-topics.sh --create --topic hw-52b --replica-assignment 1:2:3")\np.produce(T, value=...) x 5   # acks=1\nc.get_watermark_offsets(TopicPartition(T, 0))   # (low, high watermark)', sec('== 1)', '== 2)')),
     'Five records; every replica has them, so HW = 5 and ISR = 1,2,3.'),
    ('Step 2 · Freeze a follower, write with acks=1',
     code('python', 'l52_hw.py', 'subprocess.run(["docker", "pause", "k3"])\nfor i in range(5): p.produce(T, value=f"during-{i}")    # acks=1\np.flush()\n# poll the high watermark every 0.25 s', sec('== 2)', '== 3)')),
     'The producer got its OK immediately (leader only). The HW stayed at 5 for 9.6 s: consumers could not see offsets 5–9. Then the controller fenced the frozen broker, the ISR shrank to 1,2, and HW jumped to 10.'),
    ('Step 3 · Recovery',
     code('bash', 'terminal', 'docker unpause k3\nkafka-topics.sh --describe --under-replicated-partitions', sec('== 3)')),
     'k3 fetched the missing records and rejoined the ISR; no partition is under-replicated any more.'),
]

see = [term([('HW 5   ISR 1,2,3', G)], size=7.6),
       term([('$ docker pause k3', Y), ('acks=1 confirmed after 0.00 s', W), ('t+0.0s high watermark 5', Y)], size=7.0),
       term([('t+9.6s high watermark 10', G), ('ISR now 1,2', Y)], size=7.2),
       term([('$ docker unpause k3', W), ('HW 10   ISR 1,2,3', G), ('under-replicated: none', G)], size=7.0)]
def rows(k3_len, hw, title, tone):
    o = t(180, 14, title, 9, bold=True)
    for r, (name, n) in enumerate([('L', 10 if hw != 5 or k3_len != 5 or title.startswith('Healthy') is False else 5), ('k2', 10), ('k3', k3_len)]):
        n = 5 if title.startswith('Healthy') else n
        o += t(14, 50 + r * 24, name, 7.4, 'ink', anchor='start', bold=True) + ''.join(box(34 + k * 30, 38 + r * 24, 26, 18, 'green' if k < hw else ('amber' if k < n else 'card'), rx=2) for k in range(n))
    return o + arrow(34 + hw * 30 - 2, 32, 34 + hw * 30 - 2, 112, 'red', 1.6) + cap(title, '', tone, y=144, h=30)
B1 = [rows(5, 5, 'Healthy: HW = 5', 'green'), rows(5, 5, 'k3 frozen: HW stuck at 5', 'amber'), rows(5, 10, 'k3 fenced: HW jumps to 10', 'green'), rows(10, 10, 'k3 back in ISR', 'blue')]
two = anim_two('ISR and the high watermark', 'Freeze a follower', 'Real outputs from the lab', 'Replica logs and HW', see, B1, ['Healthy.', 'Frozen.', 'Fenced.', 'Recovered.'], ['HW 5.', 'Waiting.', 'Shrink.', 'Expand.'])
pe = peel('How the high watermark moves', 'Leader bookkeeping on every follower fetch. (Simplified.)',
    [('Produce', ''), ('Follower fetch', ''), ('Leader updates', ''), ('Compute HW', ''), ('Consumers', ''), ('Lagging follower', '')],
    [['Produce', 'leader appends', 'LEO 5 → 10', ''], ['Follower fetch', 'k2: “I have up to 10”', 'k3: no fetch (frozen)', ''],
     ['Leader updates', 'remembers each', 'follower’s LEO', 'k2 = 10, k3 = 5'], ['Compute HW', 'HW = min LEO in ISR', '= 5 while k3 is in ISR', ''],
     ['Consumers', 'fetch only < HW', 'offsets 5–9 hidden', ''], ['Lagging follower', 'fenced or too slow →', 'removed from ISR', 'HW = 10']],
    ['Write.', 'Fetch.', 'Track.', 'HW.', 'Read.', 'Shrink.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'A GC pause on one broker', 'ISR shrink and expand. (Typical.)', ('ISR churn', 'Frequent shrink/expand points to a struggling broker'), [
    ('Broker 3 long GC pauses', 'stops fetching 10 s', 'Repeatedly.', 'blue'), ('ISR shrinks, expands', 'every few minutes', 'Alerts flap.', 'amber'),
    ('acks=all latency spikes', 'waiting for broker 3', 'Users notice.', 'red'), ('Tune heap / GC, check disk', 'fix the cause', 'Not the timeout.', 'green'),
    ('Stable ISR', 'no flapping', 'Fixed.', 'blue')], ['GC.', 'Flap.', 'Latency.', 'Fix.', 'Stable.'], 'scenario-gc') + \
       five('Real-time scenario 2', 'Under-replicated for hours', 'Reduced durability. (Typical.)', ('Under-replicated partitions', 'Alert immediately; one more failure may lose data'), [
    ('Disk slow on broker 2', 'its replicas lag', 'Out of ISR.', 'amber'), ('URP = 120 partitions', 'only 2 copies in sync', 'Risky.', 'red'),
    ('Another broker fails', 'only 1 copy → under min ISR', 'Writes stop.', 'red'), ('Replace the disk', 'replicas catch up', 'URP 0.', 'green'),
    ('Alert on URP > 0', 'page on-call', 'Process.', 'blue')], ['Slow disk.', 'URP.', 'Second fault.', 'Fix.', 'Alert.'], 'scenario-urp') + \
       five('Real-time scenario 3 · advanced', 'Ghost reads prevented', 'Why HW protects consumers. (Typical.)', ('High watermark', 'Consumers never see data that could disappear in a failover'), [
    ('Leader has offsets 5–9', 'followers do not yet', 'acks=1.', 'blue'), ('If consumers read them…', 'and the leader dies', 'Data gone.', 'red'),
    ('HW blocks reads', 'until replicated', 'No ghosts.', 'green'), ('New leader truncates others', 'by leader epoch', 'Consistent.', 'green'),
    ('acks=all also waits', 'for HW to pass', 'Durable acks.', 'blue')], ['Leader only.', 'Risk.', 'HW.', 'Truncate.', 'acks=all.'], 'scenario-ghost')
assemble(HERE, h2_story='Ten records written, five visible', hook_html=hk,
    narration='A TiffinGo engineer reports that records acknowledged to the producer are not visible to consumers for several seconds. One broker has been having trouble. Riya and Kabir investigate.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='ISR and the high watermark',
    formal='The <b>in-sync replica set (ISR)</b> of a partition is the leader plus the followers that are sufficiently caught up; a follower that has not caught up within <code>replica.lag.time.max.ms</code>, or whose broker is fenced by the controller, is removed and is re-added once it catches up. The leader advances the <b>high watermark (HW)</b> to the minimum log end offset (LEO) across the ISR. Consumers can fetch only records below the HW, and acks=all produce requests complete only when the HW passes them, which guarantees that consumed and acknowledged records survive the loss of any ISR member except the last.',
    simple='The ISR is the list of copies that are up to date. The high watermark is the last position that every up-to-date copy has. Readers can only see data below it, so they never read something that might vanish if the leader dies.',
    term_rows=[('ISR', 'In-sync replicas.'), ('LEO', 'Log end offset of a replica.'), ('High watermark', 'Min LEO across the ISR.'), ('ISR shrink', 'Replica removed from ISR.'), ('ISR expand', 'Replica added back.'), ('Under-replicated', 'ISR smaller than replicas.'), ('Fenced broker', 'Broker cut off by the controller.'), ('Leader epoch', 'Generation of leadership; used to truncate.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Consumers can read everything the leader has.', 'Only up to the high watermark.', 'Step 2: offsets 5–9 hidden for 9.6 s.'),
               ('A follower leaves the ISR only after 30 s.', 'In KRaft, a fenced broker (9 s session) leaves at once.', 'Step 2: 9.6 s.'),
               ('acks=1 records are immediately readable.', 'They become readable once the ISR has them (HW).', 'Step 2.')],
    exam='“What are ISR and high watermark?” ISR = leader + caught-up followers (lag < replica.lag.time.max.ms, broker not fenced). HW = min LEO of ISR; consumers read below HW; acks=all waits for HW; under-replicated = ISR < replicas.',
    types_h2='Signals and settings', types_html=types_html, warn=warn,
    steps_h2='Freeze a follower, watch the watermark', steps_intro='All outputs are real: Kafka 4.4.0, 3 brokers; topic <code>hw-52b</code> with replicas 1,2,3 (leader 1); follower k3 frozen with <code>docker pause</code>. Script: <code>jobs/m5/l52_hw.py</code>.',
    steps=steps, two=two, peel_intro='Now peel how the leader moves the high watermark.', peel_html=pe,
    scen_intro='Three live scenarios: GC pauses, long under-replication, and ghost reads.', scen=scen,
    uc_h2='At work', ucs=[uc_('ops', 'URP', 'blue', '1. Replication monitoring', 'Alert when under-replicated partitions > 0.', ['Metrics', '*URP', 'Page']),
        uc_('acks', 'latency', 'green', '2. Producer latency', 'acks=all latency rises when an ISR member is slow.', ['Slow follower', '*HW', 'Latency']),
        uc_('fail', 'over', 'violet', '3. Safe failover', 'Only ISR members can become leader cleanly (5.3).', ['Leader dies', '*ISR', 'No loss']),
        uc_('disk', 'health', 'acc', '4. Broker health', 'ISR churn reveals bad disks and GC issues.', ['Churn', '*investigate', 'Fix']),
        uc_('read', 'safe', 'blue', '5. Consistent reads', 'Consumers never see unreplicated data.', ['Fetch', '*< HW', 'Safe'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../01-brokers-and-replication/">5.1 Brokers and replication</a> and <a href="../../02-producers/04-acks-and-durability/">2.4 acks</a>.')
