import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l53_election.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('We killed a leader broker in the middle of 160 writes. How many records were lost?',
    'Zero: 160 of 160 delivered. The controller picked a new leader from the ISR, the producer refreshed its metadata and retried, and the longest pause was <b>9.8 s</b>. Here is exactly what happened, why it took ~10 s, and how leadership comes back home afterwards.',
    ['Who chooses a new leader, and from which replicas.',
     'Preferred, automatic and unclean elections, and when each happens.',
     'Why failover took ~10 s, and how ELR (Kafka 4.x) makes elections safer.'])
cmap = concept_map('Concept map. Beginner: leader, follower, broker failure. Intermediate: controller, ISR, preferred election, auto rebalance. Advanced: leader epoch, unclean election, ELR, fencing timeouts.',
    [[('ld', 'Leader', 'Lesson 5.1', B + '05-replication-and-the-cluster/01-brokers-and-replication/'), ('fl', 'Broker failure', 'crash / stop', None)],
     [('ct', 'Controller', 'decides', None), ('is', 'ISR', 'Lesson 5.2', B + '05-replication-and-the-cluster/02-isr-and-the-high-watermark/'), ('pe', 'Preferred election', 'go home', None), ('ar', 'Auto rebalance', '300 s check', None)],
     [('ep', 'Leader epoch', 'fencing', None), ('un', 'Unclean election', 'data loss', None), ('el', 'ELR', 'KIP-966', None), ('kr', 'KRaft', 'Lesson 5.4', B + '05-replication-and-the-cluster/04-kraft-vs-zookeeper/')]],
    [('ld', 'fl'), ('fl', 'ct'), ('ct', 'is'), ('is', 'pe'), ('pe', 'ar'), ('ct', 'ep'), ('is', 'un'), ('is', 'el'), ('ct', 'kr')],
    {'ld', 'fl', 'ct', 'is', 'pe', 'ar', 'ep', 'un', 'el'},
    '<b>Builds on:</b> <a href="../01-brokers-and-replication/">5.1</a>, <a href="../02-isr-and-the-high-watermark/">5.2</a>, <a href="../../02-producers/04-acks-and-durability/">2.4</a>. <b>Next:</b> <a href="../04-kraft-vs-zookeeper/">5.4 KRaft vs ZooKeeper</a>.')
whw = why_how_where(
    'A partition with no leader cannot accept writes or serve reads. Elections restore service in seconds without a human.',
    'The active controller notices the broker is gone (missed heartbeats → fenced after broker.session.timeout.ms, 9 s default), picks the next live replica in the ISR as leader, bumps the leader epoch and writes a PARTITION_CHANGE record; brokers and clients follow.',
    'Every broker crash, restart, rolling upgrade (controlled shutdown moves leaders first), and preferred-leader rebalancing.',
    'If no ISR member survives, the partition stays offline unless you allow an unclean election (possible data loss).')

def nodes(lead, dead=(), isr=(1, 2, 3)):
    o = ''
    for b in (1, 2, 3):
        x = 30 + (b - 1) * 200
        tone = 'red' if b in dead else ('acc' if b == lead else ('blue' if b in isr else 'card'))
        o += box(x, 40, 150, 70, tone, rx=8) + icon('disk', x + 8, 48, 0.8) + t(x + 90, 64, f'broker {b}', 8.6, bold=True) + \
             t(x + 90, 84, 'DOWN' if b in dead else ('LEADER' if b == lead else ('in ISR' if b in isr else 'catching up')), 7.6, 'ink', bold=b == lead)
    return o
scene_svg = scene('Partition 0 of rides-51: broker 1 was leader and is killed; broker 2, which was in the ISR, becomes the new leader; broker 3 stays a follower.', nodes(2, dead=(1,), isr=(2, 3)),
                  'Leader 1 died → <tspan font-weight="700" class="s-acc">ISR member 2 takes over</tspan>, 160/160 delivered.')
dialogue = '''K> Sir, if broker 1 dies at 2 a.m., does someone have to wake up and pick a new leader?
A> No. The controller does it. It only chooses from the <b>ISR</b>, because those replicas have every committed record.
R> How fast?
A> Detection is the slow part: the controller waits for the broker’s session to time out (about 9 s). The switch itself is milliseconds. Let’s kill a leader while a producer writes, and time it.'''

lv = '''
LEVELS> Leader election at three levels
L1> A new team captain
      <ul>
        <li>If the captain leaves the field, the coach picks the next player who knows all the plays (the ISR). Later, when the old captain returns and is fit, the coach may give the armband back (preferred election).</li>
      </ul>
L2> The rules
      <ul>
        <li>The <b>controller</b> runs every election. A new leader is chosen from the ISR, in replica-list order.</li>
        <li>Each election bumps the <b>leader epoch</b>; requests carrying an old epoch are rejected, so a returning old leader cannot write stale data (fencing).</li>
        <li><b>Preferred election</b> moves leadership back to the first replica. Automatic when <code>auto.leader.rebalance.enable=true</code> (default): every <code>leader.imbalance.check.interval.seconds</code> (300) if a broker’s imbalance exceeds <code>leader.imbalance.per.broker.percentage</code> (10). Manual: <code>kafka-leader-election.sh --election-type PREFERRED</code>.</li>
      </ul>
L3> When the ISR is empty
      <ul>
        <li><b>Unclean election</b> (<code>unclean.leader.election.enable=true</code>, default false) lets an out-of-sync replica lead: availability now, but records it never copied are lost and offsets are truncated on others.</li>
        <li><b>ELR</b> (Eligible Leader Replicas, KIP-966, on in Kafka 4.x via <code>eligible.leader.replicas.version</code>): replicas that left the ISR <i>without missing committed data</i> (HW-safe) stay eligible, so many “ISR empty” cases recover cleanly instead of needing an unclean election.</li>
        <li>Rolling restarts use <b>controlled shutdown</b>: the broker asks the controller to move its leaders away before stopping, so clients see almost no pause.</li>
      </ul>
/LEVELS
'''
TL = figure('Timeline of our failover: broker 1 is killed at second 0; for about 9 seconds produce requests to it fail and the producer retries; the controller fences broker 1 and elects broker 2; deliveries resume, with a longest gap of 9.8 seconds.',
    t(16, 22, 'Failover timeline (lab, rides-51 P0)', 8.6, 'ink', anchor='start', bold=True) +
    box(20, 40, 600, 20, 'card', rx=3) + box(20, 40, 50, 20, 'green', rx=3) + box(70, 40, 470, 20, 'red', rx=3) + box(540, 40, 80, 20, 'green', rx=3) +
    t(45, 80, 't0 kill', 7.4) + t(300, 80, '~9 s: heartbeats missing, producer retries', 7.4) + t(560, 80, 'leader 2', 7.4, bold=True) +
    t(320, 104, 'broker.session.timeout.ms 9000 → fence → elect from ISR → PARTITION_CHANGE (epoch+1)', 7.6, mono=True),
    h=124, caption='Detection dominates; the election itself is fast.')
extra = '''

  <h3>Where the 9.8 seconds went</h3>
''' + TL

types_html = table(['Election type', 'Trigger', 'Chooses from', 'Data loss?'], [
    ['Failure (clean)', 'leader fenced or shut down', 'ISR (and ELR)', 'no'],
    ['Preferred', 'auto rebalance / kafka-leader-election PREFERRED', 'first replica, if in ISR', 'no'],
    ['Controlled shutdown', 'broker stopping gracefully', 'other ISR members', 'no'],
    ['Unclean', 'ISR empty + unclean enabled (or --election-type UNCLEAN)', 'any live replica', 'possible'],
], minw=620) + table(['Setting', 'Default', 'Effect'], [
    ['auto.leader.rebalance.enable', 'true', 'automatic preferred elections'], ['leader.imbalance.check.interval.seconds', '300', 'how often'],
    ['leader.imbalance.per.broker.percentage', '10', 'threshold'], ['unclean.leader.election.enable', 'false', 'allow out-of-sync leaders'],
    ['broker.session.timeout.ms', '9000', 'failure detection'],
], minw=600)
warn = 'Never enable unclean.leader.election.enable on topics where loss matters (payments, orders). It trades committed data for a few minutes of availability, and consumers may even see offsets go backwards.'

steps = [
    ('Step 1 · Leader is not the preferred one',
     code('bash', 'terminal', 'kafka-topics.sh --bootstrap-server k1:9092 --describe --topic small-51', sec('== 1)', '== 2)')),
     'After the 5.1 reassignment, partition 0 has replicas 3,1 (preferred = 3) but leader 1.'),
    ('Step 2 · Preferred election',
     code('bash', 'terminal', 'kafka-leader-election.sh --bootstrap-server k1:9092 --election-type PREFERRED --topic small-51 --partition 0', sec('== 2)', '== 3)')),
     'Leadership moved to broker 3, the first replica. No data moves: only who leads.'),
    ('Step 3 · Kill the leader under load',
     code('python', 'failover.py', 'producer: 10 records/s to P0 (acks=all, retries); after 40 sends: docker kill k1', sec('== 3)', '== 4)')),
     '160 of 160 delivered, 0 failed. The producer’s retries (delivery.timeout.ms 120 s) covered the ~9.8 s gap. Broker 2 (next in ISR) became leader; ISR shrank to 2,3.'),
    ('Step 4 · Broker returns',
     code('bash', 'terminal', 'docker start k1; sleep 20\nkafka-topics.sh --bootstrap-server k1:9092 --describe --topic rides-51', sec('== 4)')),
     'Broker 1 caught up and rejoined the ISR, but leader is still 2. Automatic rebalance runs every 300 s and only if imbalance exceeds 10%, so leadership returns later (or run step 2 by hand).'),
]
see = [term([('P0 Leader 1 Replicas 3,1', Y)], size=7.4), term([('PREFERRED done', G), ('P0 Leader 3 Replicas 3,1', G)], size=7.4),
       term([('delivered 160/160', G), ('gap 9.8 s', Y), ('Leader 2 Isr 2,3', W)], size=7.2), term([('Isr 1,2,3', G), ('Leader still 2', Y)], size=7.4)]
B1 = [nodes(1, isr=(1, 3)), nodes(3, isr=(1, 3)), nodes(2, dead=(1,), isr=(2, 3)), nodes(2)]
B1 = [b + cap(c, '', tn, y=130, h=30) for b, c, tn in zip(B1, ['Leader 1, preferred 3', 'Preferred election → 3', 'Kill 1 → leader 2', 'Back in ISR, still follower'], ['amber', 'green', 'red', 'blue'])]
two = anim_two('Leader election', 'Preferred, failover, return', 'Real outputs from the lab', 'Who leads', see, B1, ['Before.', 'Prefer.', 'Kill.', 'Return.'], ['Mismatch.', 'Fixed.', 'Failover.', 'Rejoin.'])
pe = peel('A failover, layer by layer', 'Broker 1 crashes while leading rides-51 P0. (Simplified.)',
    [('Crash', ''), ('Detect', ''), ('Elect', ''), ('Publish', ''), ('Clients', ''), ('Rejoin', '')],
    [['Crash', 'broker 1 killed', 'requests time out', ''], ['Detect', 'no heartbeats', 'session 9 s', 'controller fences 1'],
     ['Elect', 'ISR [1,2,3] minus 1', 'first live = 2', 'epoch + 1'], ['Publish', 'PARTITION_CHANGE', 'in metadata log', 'brokers apply'],
     ['Clients', 'NOT_LEADER error', 'refresh metadata', 'retry to broker 2'], ['Rejoin', 'broker 1 truncates to HW', 'fetches, rejoins ISR', 'later preferred election']],
    ['Crash.', 'Detect.', 'Elect.', 'Publish.', 'Retry.', 'Rejoin.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'All leaders on one broker', 'After a rolling restart. (Typical.)', ('Preferred election', 'Move leadership back to first replicas'), [
    ('Rolling restart', 'brokers 1, 2, 3 in turn', 'Leaders move away.', 'blue'), ('Broker 3 leads 70%', 'hot CPU and network', 'Imbalance.', 'red'),
    ('Wait 300 s or run PREFERRED', 'auto rebalance', 'Fix.', 'green'), ('Leaders 2-2-2 again', 'balanced', 'Healthy.', 'green'),
    ('Monitor', 'LeaderCount per broker', 'Alert on skew.', 'blue')], ['Restart.', 'Skew.', 'Elect.', 'Balanced.', 'Watch.'], 'scenario-skew') + \
       five('Real-time scenario 2', 'Offline partition', 'All ISR copies lost. (Typical.)', ('Unclean election', 'Availability vs consistency'), [
    ('ISR shrank to 1', 'then that broker died', 'No ISR left.', 'blue'), ('OfflinePartitionsCount 1', 'writes fail', 'Outage.', 'red'),
    ('Option A: wait', 'bring the broker back', 'No loss.', 'green'), ('Option B: UNCLEAN', 'kafka-leader-election --election-type UNCLEAN', 'Loss possible.', 'amber'),
    ('Postmortem', 'RF 3, min ISR 2, ELR', 'Prevent.', 'blue')], ['Shrink.', 'Offline.', 'Wait.', 'Unclean.', 'Prevent.'], 'scenario-offline') + \
       five('Real-time scenario 3 · advanced', 'Zombie leader', 'Network partition. (Typical.)', ('Leader epoch fencing', 'Old leaders cannot write'), [
    ('Broker 1 isolated', 'still thinks it leads', 'Zombie.', 'blue'), ('Controller elects 2', 'epoch 5 → 6', 'New leader.', 'green'),
    ('Broker 1 reconnects', 'sends epoch 5 data', 'Stale.', 'red'), ('Rejected', 'FENCED_LEADER_EPOCH', 'Safe.', 'green'),
    ('Broker 1 truncates', 'follows leader 2', 'Consistent.', 'blue')], ['Isolate.', 'Elect.', 'Return.', 'Fence.', 'Follow.'], 'scenario-zombie')
assemble(HERE, h2_story='Who takes over when a leader dies?', hook_html=hk,
    narration='At 2 a.m. a broker in TiffinGo’s cluster crashed. Orders kept flowing. Kabir wants to know who replaced the leader, how fast, and why the old broker did not get its leadership back.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Leader election',
    formal='<b>Leader election</b> is the controller’s choice of a new leader for a partition, normally from the live members of the ISR (or ELR) in replica-list order. It happens on leader failure, controlled shutdown, reassignment, and <b>preferred-leader election</b> (manual or automatic rebalancing). Each election increments the <b>leader epoch</b>, which fences stale leaders. An <b>unclean election</b> may select an out-of-sync replica when explicitly enabled, risking loss of committed records.',
    simple='When a partition’s leader disappears, the controller picks a fully caught-up copy to lead instead. Later it can hand leadership back to the “preferred” broker. Picking a copy that is behind is possible but can lose data, so it is off by default.',
    term_rows=[('Controller', 'Node that runs elections.'), ('Leader epoch', 'Election counter; fences old leaders.'), ('Preferred leader', 'First replica.'), ('Preferred election', 'Return leadership to it.'), ('Auto rebalance', 'Periodic preferred elections.'), ('Unclean election', 'Out-of-sync replica leads.'), ('ELR', 'Safe non-ISR candidates (KIP-966).'), ('Controlled shutdown', 'Move leaders before stopping.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('A crashed leader loses unconfirmed writes.', 'With acks=all + retries, producers resend; we lost 0 of 160.', 'Step 3.'),
               ('Leadership returns as soon as the broker restarts.', 'Only after it rejoins ISR and a preferred election runs.', 'Step 4: still 2.'),
               ('Any replica can become leader.', 'Only ISR/ELR members, unless unclean is enabled.', 'Types table.')],
    exam='“What happens when a leader broker fails?” Controller detects (session timeout), elects next live ISR replica, bumps leader epoch, publishes metadata; clients get NOT_LEADER, refresh, retry. Preferred election restores balance; unclean election risks loss; ELR (KIP-966) widens safe choices.',
    types_h2='Election types and settings', types_html=types_html, warn=warn,
    steps_h2='Elect, kill, return', steps_intro='All outputs are real: Kafka 4.4.0, 3 KRaft nodes. Topics from Lesson 5.1.',
    steps=steps, two=two, peel_intro='Now peel a failover.', peel_html=pe,
    scen_intro='Three live scenarios: leader skew, an offline partition, and a zombie leader.', scen=scen,
    uc_h2='Elections at work', ucs=[uc_('crash', 'failover', 'red', '1. Broker crash', 'Seconds of pause, no loss with acks=all.', ['Crash', '*elect ISR', 'Resume']),
        uc_('roll', 'upgrade', 'blue', '2. Rolling upgrades', 'Controlled shutdown moves leaders first.', ['Stop', '*move leaders', 'Upgrade']),
        uc_('bal', 'balance', 'green', '3. Leader balance', 'Auto preferred elections every 300 s.', ['Skew', '*PREFERRED', 'Even']),
        uc_('dr', 'disaster', 'amber', '4. Disaster choices', 'Unclean election as a last resort.', ['ISR empty', '*decide', 'Recover'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../02-isr-and-the-high-watermark/">5.2 ISR</a>.')
