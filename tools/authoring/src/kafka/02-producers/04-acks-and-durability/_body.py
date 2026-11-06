import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l24_acks.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('acks=0 gave us offset “None”. Where did those payments go?',
    'With one broker down and a strict durability rule, <code>acks=all</code> refused our payments, <code>acks=1</code> accepted them, and <code>acks=0</code> did not even get an offset back. Same cluster, same second: three very different promises. This lesson tests all three.',
    ['How much speed each acks level costs (real numbers).',
     'What <code>min.insync.replicas</code> really protects you from.',
     'The exact error Kafka returns when it refuses to risk your data.'])
cmap = concept_map('Concept map. Beginner: acks 0, 1, all; replication factor. Intermediate: ISR, min.insync.replicas, NOT_ENOUGH_REPLICAS, high watermark. Advanced: unclean leader election, eligible leader replicas, durability vs availability.',
    [[('a0', 'acks = 0 / 1 / all', 'who must confirm', None), ('rf', 'Replication factor', 'copies', B + '01-introduction/03-kafka-architecture/'), ('ld', 'Leader', 'takes writes', None)],
     [('is', 'ISR', 'in-sync copies', B + '05-replication-and-the-cluster/02-isr-and-the-high-watermark/'), ('mi', 'min.insync.replicas', 'safety floor', None), ('ne', 'NOT_ENOUGH_REPLICAS', 'refusal', None), ('hw', 'High watermark', 'Lesson 5.2', B + '05-replication-and-the-cluster/02-isr-and-the-high-watermark/')],
     [('ul', 'Unclean election', 'Lesson 5.3', B + '05-replication-and-the-cluster/03-leader-election/'), ('el', 'Eligible leader replicas', 'KIP-966', None), ('id', 'Idempotence', 'Lesson 2.5', B + '02-producers/05-idempotent-producer-and-retries/')]],
    [('a0', 'mi'), ('rf', 'is'), ('ld', 'hw'), ('is', 'mi'), ('mi', 'ne'), ('hw', 'ul'), ('is', 'el'), ('ne', 'id')],
    {'a0', 'rf', 'ld', 'is', 'mi', 'ne'},
    '<b>Builds on:</b> <a href="../../01-introduction/03-kafka-architecture/">1.3</a>, <a href="../01-how-a-producer-sends-a-message/">2.1</a>. <b>Next:</b> <a href="../05-idempotent-producer-and-retries/">2.5 Idempotence and retries</a>.')
whw = why_how_where(
    'Brokers fail. If a write is confirmed after only one copy exists and that broker dies, the “confirmed” record is gone.',
    'acks says how many replicas must have the record before the producer hears “OK”; min.insync.replicas sets how many in-sync copies must exist for acks=all to be accepted at all.',
    'Payments and orders: acks=all + RF 3 + min.insync 2. Metrics and telemetry: acks=1 or 0 for speed.',
    'acks=all does not help if min.insync.replicas=1 and only the leader is in sync: then it behaves like acks=1.')

def bk(x, n, state):
    tone = {'ok': 'green', 'down': 'red', 'lead': 'acc'}[state]
    return box(x, 38, 86, 50, tone, rx=8) + icon('disk', x + 8, 46, 0.8) + t(x + 54, 58, f'broker {n}', 8, bold=True) + t(x + 54, 74, {'ok': 'has copy', 'down': 'stopped', 'lead': 'leader'}[state], 7.4, 'ink2')
sc_ = (bk(14, 1, 'lead') + bk(110, 2, 'ok') + bk(206, 3, 'down') + t(160, 112, 'ISR = 2 copies, rule needs 3', 8, 'ink', bold=True) +
       ''.join(box(330, 26 + k * 34, 296, 28, tone, rx=6) + t(340, 44 + k * 34, s, 8, 'ink', anchor='start', mono=True) for k, (s, tone) in enumerate([
           ('acks=all → Not enough in-sync replicas', 'red'), ('acks=1   → offset 0, 1   (leader only)', 'amber'), ('acks=0   → offset None (no answer)', 'amber')])))
scene_svg = scene('Broker 3 is stopped, so only 2 replicas are in sync while the topic requires 3. acks=all is refused with Not enough in-sync replicas; acks=1 is accepted by the leader alone; acks=0 gets no offset back.', sc_,
                  'Same failure, three <tspan font-weight="700" class="s-acc">different promises</tspan>.')
dialogue = '''K> Sir, the payments team wants maximum speed. Can we set <code>acks=0</code>?
A> Then the producer never waits for any answer. If the broker crashes, payments vanish and nobody knows. For payments we choose <code>acks=all</code>, replication factor 3 and <code>min.insync.replicas=2</code>.
R> What does <code>min.insync.replicas</code> add?
A> It is the floor. If too few copies are healthy, Kafka <b>refuses</b> acks=all writes instead of pretending they are safe. We will measure the speed of each acks level, then stop a broker and watch the refusal.'''

lv = '''
LEVELS> acks at three levels
L1> Courier receipts
      <ul>
        <li><b>acks=0</b>: drop the parcel at the gate and walk away. <b>acks=1</b>: the reception desk signs. <b>acks=all</b>: reception and the two backup stores all sign before you get the receipt.</li>
      </ul>
L2> The rules
      <ul>
        <li><b>acks=0</b>: no response; offset unknown (<code>-1</code>); fastest, may lose data silently.</li>
        <li><b>acks=1</b>: the leader wrote it to its log; lost if the leader dies before followers copy it.</li>
        <li><b>acks=all</b> (= -1, default since Kafka 3.0): every replica currently in the ISR has it. With <code>min.insync.replicas=2</code> at least 2 copies exist before success.</li>
      </ul>
L3> Deeper details
      <ul>
        <li>If ISR size &lt; <code>min.insync.replicas</code>, the leader rejects acks=all writes with <code>NOT_ENOUGH_REPLICAS</code> (retriable): writes stop, reads continue. This trades availability for durability.</li>
        <li>Consumers only see records below the <b>high watermark</b> (replicated to all ISR members), so acks=1 data that was never replicated is never shown to consumers before a leader change.</li>
        <li><code>unclean.leader.election.enable=false</code> (default) prevents an out-of-sync replica from becoming leader and silently dropping data. Kafka 4.x adds <b>Eligible Leader Replicas</b> (KIP-966, the <code>Elr</code> column in <code>--describe</code>) to pick a safe leader after failures.</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of a durable configuration: replication factor 3, min.insync.replicas 2, producer acks all, unclean leader election disabled, and the guarantee that acknowledged records survive one broker failure.',
    t(16, 22, 'The durability recipe used by most companies', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('replication.factor=3', 'blue', 1), ('min.insync.replicas=2', 'violet', 2), ('acks=all', 'acc', 3), ('enable.idempotence=true', 'green', 4), ('unclean.leader.election=false', 'amber', 5)]) +
    box(16, 72, 600, 28, 'green', rx=4) + t(316, 90, '⇒ every acknowledged record is on ≥ 2 brokers; one broker can fail with no loss and no downtime', 8, 'ink', bold=True) + pin(18, 70, 6) +
    legend(16, 128, [(1, 'RF 3', 'three copies of each partition'), (2, 'min ISR 2', 'refuse writes if fewer than 2 copies are in sync'),
                     (3, 'acks=all', 'wait for all in-sync copies'), (4, 'Idempotence', 'retries cannot duplicate (Lesson 2.5)'),
                     (5, 'No unclean election', 'never promote a replica that missed data'), (6, 'Result', 'survive 1 failure; with 2 failures writes pause, data safe')], size=8, gap=15, w=120),
    h=232, caption='Settings 1, 2, 5 are topic/broker configs; 3, 4 are producer configs.')
extra = '''

  <h3>Dissect the durability recipe</h3>
''' + DIS

types_html = table(['acks', 'Waits for', 'Our throughput', 'Can lose acknowledged data?', 'Use for'], [
    ['0', 'nothing', '58,005 rec/s', 'yes, silently', 'metrics, GPS pings'],
    ['1', 'leader write', '48,900 rec/s', 'yes, if leader dies before replication', 'logs, clicks'],
    ['all', 'all in-sync replicas', '37,133 rec/s', 'no (with min ISR ≥ 2)', 'orders, payments'],
], minw=640) + table(['RF / min.insync.replicas', 'Broker failures tolerated (writes continue)', 'Copies per acked record'], [
    ['RF 3 / min ISR 1', '2 (but a single copy may hold the data)', '≥ 1'],
    ['RF 3 / min ISR 2', '1 (recommended)', '≥ 2'],
    ['RF 3 / min ISR 3', '0 (any failure stops writes)', '3'],
], minw=560)
warn = 'Do not set <code>min.insync.replicas</code> equal to the replication factor for important topics: then <i>any</i> single broker restart blocks writes (we did exactly that in Step 3 to show the refusal). The usual choice is RF 3 with min ISR 2.'

steps = [
    ('Step 1 · Speed of acks=0, 1, all',
     code('bash', 'terminal', 'for a in 0 1 all; do\n  kafka-producer-perf-test.sh --topic pay-24 --num-records 200000 --record-size 200 \\\n    --throughput -1 --producer-props bootstrap.servers=k1:9092 acks=$a linger.ms=5\ndone', sec('== 1)', '== 2)')),
     '200,000 records of 200 bytes, sending as fast as possible. acks=0 reached 58k records/s, acks=1 49k, acks=all 37k: the safest level cost about 36% throughput here. The high latencies are queueing in an unthrottled test on a small Docker lab, not normal per-record latency.'),
    ('Step 2 · The topic’s safety floor',
     code('bash', 'terminal', 'kafka-topics.sh --bootstrap-server k1:9092 --create --topic pay-24 --partitions 3 \\\n  --replication-factor 3 --config min.insync.replicas=2', sec('== 2)', '== 3)')),
     '<code>min.insync.replicas</code> is a topic (or broker default) setting. It only affects producers that use acks=all.'),
    ('Step 3 · Break it: too few in-sync copies',
     code('python', 'l24_fail.py', '# topic pay-24b: RF 3, min.insync.replicas=3; broker 3 stopped\nsend("all", retries=0); send("all", retries=5)\nsend("1", 0); send("0", 0)', sec('== 3)', '== 4)')),
     'ISR shrank to 2. acks=all was refused with <b>Not enough in-sync replicas</b>, even with retries. acks=1 got offsets 0 and 1 from the leader alone. acks=0 got <code>offset None</code>: the producer never learns what happened. (In a 3-node combined lab, stopping 2 nodes would also stop the controller majority, so we raised the floor to 3 instead.)'),
    ('Step 4 · Recovery',
     code('bash', 'terminal', 'docker start k3        # wait for it to rejoin the ISR\npython l24_fail.py', sec('== 4)')),
     'With 3 copies in sync again, acks=all succeeds. Notice the offsets jumped to 4 and 5: offsets 2 and 3 were taken by the acks=0 records, which <i>were</i> stored even though the producer was never told.'),
]

see = [term([('acks=0   58,005 records/sec', W), ('acks=1   48,900 records/sec', W), ('acks=all 37,133 records/sec', G)], size=7.2),
       term([('Configs: min.insync.replicas=2', W)], size=7.4),
       term([('Isr: 1,2  (broker 3 stopped)', Y), ('acks=all: Not enough in-sync replicas', RD), ('acks=1  : offset 0, 1', W), ('acks=0  : offset None', W)], size=6.8),
       term([('broker 3 back, Isr: 1,2,3', G), ('acks=all: offset 4, 5', G)], size=7.2)]
def tri(states, note, tone):
    return t(180, 14, note, 9, bold=True) + ''.join(opbox(20 + k * 112, 50, f'broker {k+1}', s, {'L': 'acc', 'F': 'green', 'X': 'red'}[s[0]], 96, 34) for k, s in enumerate(states)) + cap(note, '', tone, y=144, h=30)
B1 = [t(180, 14, 'More waiting, more safety', 9, bold=True) + ''.join(box(40, 36 + k * 30, 260 * v / 58005, 20, ['amber', 'blue', 'green'][k], rx=3) + t(46 + 260 * v / 58005, 50 + k * 30, f'acks={n}: {v:,}/s', 7.6, 'ink', anchor='start') for k, (n, v) in enumerate([('0', 58005), ('1', 48900), ('all', 37133)])) + cap('About 36% slower for safety.', '', 'blue', y=144, h=30),
      tri(['Leader', 'Follower', 'Follower'], 'Floor: at least N copies', 'violet'),
      tri(['Leader', 'Follower', 'X stopped'], 'acks=all refused', 'red'),
      tri(['Leader', 'Follower', 'Follower'], 'ISR full: writes resume', 'green')]
two = anim_two('acks and durability', 'Speed vs safety', 'Real outputs from the lab', 'Replicas behind each answer', see, B1, ['Speed.', 'Floor.', 'Refusal.', 'Recovery.'], ['Throughput.', 'min ISR.', 'Not enough.', 'Back.'])
pe = peel('One acks=all write, layer by layer', 'What the leader checks before saying OK. (Simplified.)',
    [('Producer', ''), ('Leader check', ''), ('Append', ''), ('Followers fetch', ''), ('High watermark', ''), ('Response', '')],
    [['Producer', 'Produce request, acks=all', 'timeout 30 s', ''], ['Leader check', 'ISR size ≥ min.insync?', 'no → NOT_ENOUGH_REPLICAS', 'yes → continue'],
     ['Append', 'leader writes the batch', 'to its log (page cache)', 'offset assigned'], ['Followers fetch', 'each ISR follower', 'fetches and appends', 'reports its position'],
     ['High watermark', 'all ISR have it →', 'HW moves forward', 'consumers can now see it'], ['Response', 'OK + offset to producer', '= acknowledged', 'survives a leader crash']],
    ['Send.', 'Check.', 'Write.', 'Copy.', 'Commit.', 'Ack.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Lost payments after a crash', 'acks=1 and a leader failure. (Typical.)', ('acks=all', 'Acknowledge only after replicas have the record'), [
    ('Payments with acks=1', 'leader acks at once', 'Fast.', 'blue'), ('Leader crashes', 'followers had not copied', 'Last records missing.', 'red'),
    ('New leader elected', 'without those records', 'App thought they were saved.', 'red'), ('Switch to acks=all', 'RF 3, min ISR 2', 'Recipe.', 'green'),
    ('Crash again: no loss', 'acked = on 2+ brokers', 'Proven.', 'blue')], ['acks=1.', 'Crash.', 'Gone.', 'Fix.', 'Safe.'], 'scenario-acks1') + \
       five('Real-time scenario 2', 'Writes stop during maintenance', 'min ISR equal to RF. (Typical.)', ('min.insync.replicas', 'Leave room for one broker to be down'), [
    ('Topic RF 3, min ISR 3', '“maximum safety”', 'Looks good.', 'blue'), ('Rolling restart', 'one broker down', 'ISR = 2.', 'amber'),
    ('Producers: NOT_ENOUGH_REPLICAS', 'orders blocked', 'Like Step 3.', 'red'), ('Set min ISR 2', 'tolerate one failure', 'Standard.', 'green'),
    ('Restarts are safe', 'no write outage', 'Balanced.', 'blue')], ['Strict.', 'Restart.', 'Blocked.', 'Fix.', 'Balanced.'], 'scenario-minisr') + \
       five('Real-time scenario 3 · advanced', 'Unclean leader election', 'Availability vs data. (Typical.)', ('Unclean election', 'Keep it disabled for important data'), [
    ('All ISR replicas lost', 'only an old follower left', 'Partition offline.', 'red'), ('Option A: wait', 'keep data, partition down', 'Default.', 'amber'),
    ('Option B: unclean election', 'old follower leads', 'Recent data lost.', 'red'), ('Payments: choose A', 'logs might choose B', 'Per topic.', 'green'),
    ('Kafka 4.x ELR', 'safer leader choice', 'KIP-966.', 'blue')], ['Lost ISR.', 'Wait.', 'Unclean.', 'Choose.', 'ELR.'], 'scenario-unclean')
assemble(HERE, h2_story='Fast, or safe?', hook_html=hk,
    narration='TiffinGo’s payments team wants the fastest possible producer. The platform team worries about losing payments if a broker dies. Arjun Sir sets up an experiment to settle it with numbers.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='acks and durability',
    formal='The producer configuration <b>acks</b> defines when a write is acknowledged: <code>0</code> (no acknowledgement), <code>1</code> (after the leader appends the record) or <code>all</code>/<code>-1</code> (after all members of the partition’s in-sync replica set have it). The topic/broker setting <b>min.insync.replicas</b> is the minimum ISR size required for acks=all writes; below it the leader rejects writes with <code>NOT_ENOUGH_REPLICAS</code>. Together with the replication factor and disabled unclean leader election, these settings determine durability and availability.',
    simple='acks is how many copies must confirm before the producer hears “saved”. min.insync.replicas is the minimum number of healthy copies Kafka requires before it even accepts an acks=all write.',
    term_rows=[('acks', 'Who must confirm a write.'), ('ISR', 'Replicas fully caught up.'), ('min.insync.replicas', 'Minimum ISR for acks=all.'), ('NOT_ENOUGH_REPLICAS', 'Write refused: ISR too small.'), ('High watermark', 'Last offset safe for consumers.'), ('Unclean election', 'Out-of-sync replica becomes leader.'), ('ELR', 'Eligible leader replicas (KIP-966).'), ('Durability', 'Acked data is never lost.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('The default is acks=1.', 'Since Kafka 3.0 the default is acks=all (with idempotence).', 'our producers used all by default.'),
               ('acks=all means all 3 replicas, always.', 'It means all replicas currently in the ISR; min.insync.replicas sets the floor.', 'Step 3: ISR of 2.'),
               ('acks=0 records are dropped.', 'They are usually stored; you just never know.', 'Step 4: offsets 2–3 used by acks=0 records.')],
    exam='“acks=0, 1, all?” 0 = no ack (fast, may lose), 1 = leader only (lost if leader dies before replication), all = all ISR (safe with RF 3 and min.insync.replicas=2). Below min ISR, acks=all writes fail with NOT_ENOUGH_REPLICAS. Keep unclean leader election off.',
    types_h2='Choosing acks and replicas', types_html=types_html, warn=warn,
    steps_h2='Speed and safety, measured', steps_intro='All outputs are real: Kafka 4.4.0, 3 brokers. Step 1 uses the Java <code>kafka-producer-perf-test.sh</code>; Steps 3–4 use Python <code>confluent-kafka</code> (<code>jobs/m2/l24_fail.py</code>).',
    steps=steps, two=two, peel_intro='Now peel one acks=all write.', peel_html=pe,
    scen_intro='Three live scenarios: lost payments, blocked writes, and unclean election.', scen=scen,
    uc_h2='acks choices at work', ucs=[uc_('pay', 'acks all', 'green', '1. Payments and orders', 'acks=all, RF 3, min ISR 2: no acknowledged loss.', ['Payment', '*acks=all', 'Safe']),
        uc_('logs', 'acks 1', 'blue', '2. Application logs', 'acks=1: fast, a rare loss is acceptable.', ['Logs', '*acks=1', 'Fast']),
        uc_('GPS', 'acks 0', 'violet', '3. Live GPS pings', 'acks=0: a missing ping is replaced in seconds.', ['GPS', '*acks=0', 'Fastest']),
        uc_('bank', 'ledger', 'acc', '4. Core ledgers', 'Plus transactions and no unclean election.', ['Ledger', '*strict', 'Audited']),
        uc_('ops', 'maint', 'blue', '5. Maintenance windows', 'min ISR 2 lets brokers restart without blocking writes.', ['Restart', '*ISR 2', 'No outage'])],
    uc_note='Throughput numbers are from our small Docker lab.',
    pre='<b>Before you start:</b> <a href="../../01-introduction/03-kafka-architecture/">1.3 Architecture</a> (leaders, followers, ISR).')
