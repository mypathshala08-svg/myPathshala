import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l51_replication.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('6 partitions, 3 brokers, 18 copies, and every broker led exactly 2. Who planned that so neatly?',
    'When you create a topic, the controller places replicas so that copies of one partition never share a broker and leadership is spread evenly. Then we <b>moved</b> a partition from brokers 1,2 to 3,1 with one command and watched its folder disappear from broker 2’s disk.',
    ['How Kafka decides which broker stores which copy.',
     'What “preferred leader” means and why replica order matters.',
     'How to move partitions between brokers safely (reassignment).'])
cmap = concept_map('Concept map. Beginner: broker, replica, replication factor. Intermediate: leader and followers, replica placement, rack awareness, reassignment. Advanced: ISR and high watermark, leader election, throttled reassignment and balancing.',
    [[('br', 'Broker', 'Lesson 1.3', B + '01-introduction/03-kafka-architecture/'), ('rp', 'Replica', 'one copy', None), ('rf', 'Replication factor', 'how many copies', None)],
     [('lf', 'Leader + followers', 'one writes', None), ('pl', 'Replica placement', 'round-robin, shifted', None), ('rk', 'Rack awareness', 'broker.rack', None), ('ra', 'Reassignment', 'move copies', None)],
     [('is', 'ISR + high watermark', 'Lesson 5.2', B + '05-replication-and-the-cluster/02-isr-and-the-high-watermark/'), ('le', 'Leader election', 'Lesson 5.3', B + '05-replication-and-the-cluster/03-leader-election/'), ('th', 'Throttles + balancing', 'safe moves', None)]],
    [('br', 'rp'), ('rp', 'rf'), ('rf', 'lf'), ('lf', 'pl'), ('pl', 'rk'), ('pl', 'ra'), ('lf', 'is'), ('lf', 'le'), ('ra', 'th')],
    {'br', 'rp', 'rf', 'lf', 'pl', 'rk', 'ra'},
    '<b>Builds on:</b> <a href="../../01-introduction/03-kafka-architecture/">1.3</a>, <a href="../../02-producers/04-acks-and-durability/">2.4</a>. <b>Next:</b> <a href="../02-isr-and-the-high-watermark/">5.2 ISR and the high watermark</a>.')
whw = why_how_where(
    'A single copy dies with its disk. Several copies on different machines (and racks) keep data safe and readable through failures.',
    'Each partition has replication.factor replicas on different brokers; the first live one in the list leads, the others fetch from it. The controller places replicas and you can move them with kafka-reassign-partitions.',
    'Every production topic (RF 3 is standard); multi-zone clusters with broker.rack; adding brokers and moving load.',
    'RF cannot exceed the number of brokers; replicas cost disk and network (RF 3 = 3× storage).')

def brk(x, n, items):
    o = box(x, 22, 196, 112, 'card', rx=8) + icon('disk', x + 8, 28, 0.85) + t(x + 98, 40, f'Broker {n}', 8.6, bold=True)
    for k, (p, lead) in enumerate(items):
        o += box(x + 10 + (k % 3) * 60, 52 + (k // 3) * 36, 54, 28, 'acc' if lead else 'blue', rx=3) + t(x + 37 + (k % 3) * 60, 70 + (k // 3) * 36, p, 7.6, 'ink', bold=lead, mono=True)
    return o
L = {1: [0, 3], 2: [1, 5], 3: [2, 4]}
sc_ = ''.join(brk(14 + (b - 1) * 208, b, [(f'P{p}', p in L[b]) for p in range(6)]) for b in (1, 2, 3))
scene_svg = scene('Topic rides-51 with 6 partitions and replication factor 3: each of the three brokers holds a copy of all six partitions and leads exactly two of them (orange).', sc_,
                  '18 copies, <tspan font-weight="700" class="s-acc">2 leaders per broker</tspan>: balanced by design.')
dialogue = '''K> Sir, we are adding brokers 4 and 5 next month. Will Kafka move existing partitions to them?
A> No. Placement happens when a topic is created. New brokers stay empty until you <b>reassign</b> partitions to them.
R> And how does Kafka place copies in the first place?
A> Round-robin over brokers, shifting the starting point for each partition, so no two copies of a partition share a broker and leaders are spread out. Let’s create a topic, count, and then move a partition by hand.'''

lv = '''
LEVELS> Replication at three levels
L1> Photocopies in three branches
      <ul>
        <li>Every important register is copied to three branch offices. One branch is “in charge” of writing in it; the others copy its new pages. If that branch closes, another one takes charge.</li>
      </ul>
L2> The rules
      <ul>
        <li><b>replication.factor</b> (topic setting; broker default <code>default.replication.factor</code>, 1 unless changed) = number of copies.</li>
        <li>The replica list order matters: the <b>first</b> replica is the <b>preferred leader</b>. Followers send Fetch requests to the leader, like consumers.</li>
        <li>Placement: round-robin with a shifting start so leaders and followers spread evenly; with <code>broker.rack</code> set, copies go to different racks/zones.</li>
      </ul>
L3> Moving and balancing
      <ul>
        <li><code>kafka-reassign-partitions.sh</code>: generate or write a JSON plan, <code>--execute</code>, then <code>--verify</code> (which also clears throttles). New replicas copy data, join the ISR, and old ones are removed.</li>
        <li>Use <code>--throttle</code> (bytes/s) to protect production traffic while copying large partitions.</li>
        <li>Reassignment does not change the leader immediately: run a preferred-leader election (Lesson 5.3). Tools such as Cruise Control automate balancing.</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of one describe line: partition 0 of rides-51, leader 1, replicas 1,2,3 where the first is the preferred leader, ISR 1,2,3, and Elr empty.',
    t(16, 22, 'kafka-topics --describe, one partition', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('Partition: 0', 'card', 1), ('Leader: 1', 'acc', 2), ('Replicas: 1,2,3', 'blue', 3), ('Isr: 1,2,3', 'green', 4), ('Elr: (empty)', 'card', 5)]) +
    legend(16, 84, [(1, 'Partition', 'one ordered log'), (2, 'Leader', 'broker serving reads and writes now'),
                    (3, 'Replicas', 'all brokers with a copy; the first (1) is the preferred leader'),
                    (4, 'ISR', 'replicas fully caught up (Lesson 5.2)'), (5, 'ELR', 'eligible leader replicas outside the ISR (Kafka 4.x)')], size=8, gap=15, w=90),
    h=172, caption='Real output from our lab.')
extra = '''

  <h3>Dissect a partition line</h3>
''' + DIS

types_html = table(['Replication factor', 'Survives', 'Disk', 'Use'], [
    ['1', 'nothing', '1×', 'dev, throwaway data'], ['2', '1 broker (but no safe min ISR 2 with a failure)', '2×', 'rarely'],
    ['3', '1 broker with min ISR 2 (writes continue)', '3×', 'standard production'], ['5', '2 brokers with min ISR 3', '5×', 'very critical data'],
], minw=600) + table(['Tool', 'Purpose'], [
    ['kafka-topics --describe', 'see replicas, leader, ISR'], ['kafka-reassign-partitions --generate/--execute/--verify', 'move replicas between brokers'],
    ['kafka-leader-election --election-type PREFERRED', 'give leadership back to the first replica'], ['broker.rack', 'spread copies across racks/zones'],
], minw=560)
warn = 'Adding brokers does not rebalance anything by itself; existing partitions stay where they are until you reassign them. When you do, throttle the copy traffic and move a few partitions at a time, or followers copying terabytes can starve producers and consumers.'

steps = [
    ('Step 1 · Create a replicated topic',
     code('bash', 'terminal', 'kafka-topics.sh --bootstrap-server k1:9092 --create --topic rides-51 --partitions 6 --replication-factor 3\nkafka-topics.sh --bootstrap-server k1:9092 --describe --topic rides-51', sec('== 1)', '== 2)')),
     'Six partitions, each with copies on all three brokers. The replica lists start at a different broker each time (1,2,3 / 2,3,1 / 3,1,2 …), so each broker is first, and therefore preferred leader, for two partitions.'),
    ('Step 2 · Count',
     code('python', 'count.py', 'Counter(leader per partition), Counter(each broker in replica lists)', sec('== 2)', '== 3)')),
     '2-2-2 leaders and 6-6-6 replicas: perfectly balanced load for reads, writes and disk.'),
    ('Step 3 · Choose placement yourself',
     code('bash', 'terminal', 'kafka-topics.sh --bootstrap-server k1:9092 --create --topic small-51 --replica-assignment 1:2,2:3', sec('== 3)', '== 4)')),
     '<code>--replica-assignment</code> lists replicas per partition: partition 0 on brokers 1 and 2, partition 1 on 2 and 3 (RF 2).'),
    ('Step 4 · Move a partition',
     code('bash', 'terminal', 'echo \'{"version":1,"partitions":[{"topic":"small-51","partition":0,"replicas":[3,1]}]}\' > /tmp/plan.json\nkafka-reassign-partitions.sh --bootstrap-server k1:9092 --reassignment-json-file /tmp/plan.json --execute\nkafka-reassign-partitions.sh --bootstrap-server k1:9092 --reassignment-json-file /tmp/plan.json --verify', sec('== 4)', '== 5)')),
     'Broker 3 copied the partition, joined the ISR, and broker 2’s replica was removed. The leader is still 1, although 3 is now first in the list: leadership does not move until a preferred election (Lesson 5.3).'),
    ('Step 5 · Proof on disk',
     code('bash', 'terminal', 'for i in 1 2 3; do docker exec k$i ls -d /var/lib/kafka/data/small-51-0; done', sec('== 5)')),
     'The partition folder now exists on brokers 1 and 3 and is gone from broker 2.'),
]

see = [term([('P0 Leader 1 Replicas 1,2,3', W), ('P1 Leader 2 Replicas 2,3,1', W), ('P2 Leader 3 Replicas 3,1,2', W)], size=7.0),
       term([('leaders : {1: 2, 2: 2, 3: 2}', G), ('replicas: {1: 6, 2: 6, 3: 6}', G)], size=7.2),
       term([('small-51 P0 Replicas: 1,2', W), ('small-51 P1 Replicas: 2,3', W)], size=7.2),
       term([('reassignment of small-51-0', W), ('is completed.', G), ('P0 Leader: 1 Replicas: 3,1', Y)], size=7.0),
       term([('k1: small-51-0', G), ('k2: -', RD), ('k3: small-51-0', G)], size=7.2)]
def three(cells, title, tone):
    o = t(180, 14, title, 9, bold=True)
    for b in range(3):
        o += box(10 + b * 116, 34, 108, 90, 'card', rx=6) + t(64 + b * 116, 48, f'broker {b+1}', 8, bold=True)
        for k, (p, c) in enumerate(cells[b + 1]):
            o += box(18 + b * 116 + (k % 3) * 32, 56 + (k // 3) * 30, 28, 24, c, rx=3) + t(32 + b * 116 + (k % 3) * 32, 72 + (k // 3) * 30, p, 7, 'ink')
    return o + cap(title, '', tone, y=144, h=30)
full = {1: [('P0', 'acc'), ('P1', 'blue'), ('P2', 'blue'), ('P3', 'acc'), ('P4', 'blue'), ('P5', 'blue')],
        2: [('P0', 'blue'), ('P1', 'acc'), ('P2', 'blue'), ('P3', 'blue'), ('P4', 'blue'), ('P5', 'acc')],
        3: [('P0', 'blue'), ('P1', 'blue'), ('P2', 'acc'), ('P3', 'blue'), ('P4', 'acc'), ('P5', 'blue')]}
B1 = [three(full, 'Copies on every broker', 'blue'), three(full, '2 leaders each (orange)', 'green'),
      three({1: [('s0', 'acc')], 2: [('s0', 'blue'), ('s1', 'acc')], 3: [('s1', 'blue')]}, 'Manual placement', 'blue'),
      three({1: [('s0', 'acc')], 2: [('s0', 'red'), ('s1', 'acc')], 3: [('s0', 'green'), ('s1', 'blue')]}, 'Copy to 3, drop from 2', 'amber'),
      three({1: [('s0', 'acc')], 2: [('s1', 'acc')], 3: [('s0', 'blue'), ('s1', 'blue')]}, 'Folder gone from broker 2', 'green')]
two = anim_two('Brokers and replication', 'Place, count, move', 'Real outputs from the lab', 'Where the copies live', see, B1, ['Create.', 'Count.', 'Assign.', 'Move.', 'Disk.'], ['Spread.', 'Balanced.', 'Manual.', 'Reassign.', 'Proof.'])
pe = peel('A reassignment, layer by layer', 'Moving small-51-0 from 1,2 to 3,1. (Simplified.)',
    [('Plan', ''), ('Controller', ''), ('Add replica', ''), ('Catch up', ''), ('Remove replica', ''), ('Verify', '')],
    [['Plan', 'JSON: replicas [3,1]', '--execute', ''], ['Controller', 'records adding [3]', 'removing [2]', 'in the metadata log'],
     ['Add replica', 'broker 3 creates', 'small-51-0 folder', 'starts fetching'], ['Catch up', 'broker 3 copies data', 'joins the ISR', '(throttle if large)'],
     ['Remove replica', 'broker 2 dropped', 'from replicas', 'folder deleted'], ['Verify', '“completed”', 'clear throttles', 'leader unchanged (1)']],
    ['Plan.', 'Record.', 'Add.', 'Copy.', 'Remove.', 'Verify.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'New brokers stay empty', 'Scaling out a cluster. (Typical.)', ('Reassignment', 'New brokers need partitions moved to them'), [
    ('Add brokers 4 and 5', 'cluster at 80% disk', 'Expect relief.', 'blue'), ('Nothing moves', 'old brokers still full', 'Surprise.', 'red'),
    ('Generate plan', '--generate with broker list', 'Review.', 'green'), ('Execute with throttle', '50 MB/s, in batches', 'Safe.', 'green'),
    ('Balanced disks', 'then preferred elections', 'Done.', 'blue')], ['Add.', 'Empty.', 'Plan.', 'Move.', 'Balance.'], 'scenario-scaleout') + \
       five('Real-time scenario 2', 'A whole zone goes down', 'Rack awareness. (Typical.)', ('broker.rack', 'Spread replicas across racks/zones'), [
    ('3 zones, no rack config', 'two copies in zone A', 'By chance.', 'blue'), ('Zone A outage', 'partition loses 2 of 3', 'Writes stop (min ISR 2).', 'red'),
    ('Set broker.rack per zone', 'new topics spread', 'Rack-aware placement.', 'green'), ('Reassign old topics', 'one copy per zone', 'Fix existing.', 'green'),
    ('Zone loss = 1 copy', 'writes continue', 'Resilient.', 'blue')], ['Setup.', 'Outage.', 'Rack.', 'Reassign.', 'Safe.'], 'scenario-rack') + \
       five('Real-time scenario 3 · advanced', 'Reassignment slows production', 'Unthrottled copy traffic. (Typical.)', ('Throttling', 'Limit replication bandwidth during moves'), [
    ('Move 2 TB partition', 'no throttle', 'Full speed copy.', 'blue'), ('Network saturated', 'produce latency × 10', 'Incident.', 'red'),
    ('--throttle 50000000', '50 MB/s replication', 'Re-run.', 'green'), ('Watch lag of new replica', 'until ISR', 'Patience.', 'green'),
    ('--verify clears throttles', 'do not forget', 'Clean.', 'blue')], ['Move.', 'Saturate.', 'Throttle.', 'Watch.', 'Clean.'], 'scenario-throttle')
assemble(HERE, h2_story='Who decides where copies live?', hook_html=hk,
    narration='TiffinGo will add two brokers next month. Kabir needs to know how Kafka places copies today, and how to move some of them to the new machines.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Brokers and replication',
    formal='Each partition is <b>replicated</b> to <code>replication.factor</code> brokers. The ordered replica list is chosen by the controller at topic creation (round-robin with shifted starting points, rack-aware when <code>broker.rack</code> is set) or given explicitly; the first replica is the <b>preferred leader</b>. The <b>leader</b> handles all produce and fetch requests; <b>followers</b> replicate by fetching from the leader. Replica placement can be changed online with <code>kafka-reassign-partitions</code>, which adds new replicas, waits for them to catch up, and removes old ones.',
    simple='Kafka keeps several copies of each partition on different brokers. One copy is in charge (leader); the others keep copying it. Kafka spreads copies and leaders evenly when you create a topic, and you can move copies later with a reassignment.',
    term_rows=[('Replica', 'One copy of a partition.'), ('Replication factor', 'Number of copies.'), ('Preferred leader', 'First replica in the list.'), ('Follower', 'Replica fetching from the leader.'), ('Replica assignment', 'Which brokers hold which copies.'), ('Reassignment', 'Moving replicas between brokers.'), ('broker.rack', 'Rack/zone label for placement.'), ('Throttle', 'Bandwidth limit for copying.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Adding brokers rebalances data automatically.', 'Partitions stay until you reassign them.', 'Step 4 was a manual move.'),
               ('Followers are pushed data by the leader.', 'Followers pull with Fetch requests, like consumers.', 'Peel animation.'),
               ('Reassignment also moves leadership.', 'Leadership changes only on election.', 'Step 4: leader stayed 1.')],
    exam='“How does Kafka replication work?” Each partition has RF replicas on different brokers; first replica = preferred leader; leader serves reads/writes, followers fetch; placement round-robin and rack-aware; move replicas with kafka-reassign-partitions (execute, verify, throttle).',
    types_h2='Replication factors and tools', types_html=types_html, warn=warn,
    steps_h2='Place, count, move', steps_intro='All outputs are real: Kafka 4.4.0, 3 brokers (KRaft). Topics <code>rides-51</code> (6 partitions, RF 3) and <code>small-51</code> (2 partitions, RF 2).',
    steps=steps, two=two, peel_intro='Now peel a reassignment.', peel_html=pe,
    scen_intro='Three live scenarios: empty new brokers, a zone outage, and throttling.', scen=scen,
    uc_h2='Replication at work', ucs=[uc_('RF3', 'standard', 'blue', '1. Production topics', 'RF 3 + min ISR 2 is the common default.', ['Topic', '*RF 3', 'Durable']),
        uc_('zones', 'cloud', 'green', '2. Multi-zone clusters', 'broker.rack per availability zone.', ['3 zones', '*rack-aware', 'Survive']),
        uc_('scale', 'grow', 'violet', '3. Scaling out', 'Reassign partitions to new brokers.', ['New broker', '*reassign', 'Balanced']),
        uc_('decom', 'retire', 'acc', '4. Retiring a broker', 'Move all replicas off before shutdown.', ['Old broker', '*move off', 'Remove']),
        uc_('auto', 'balance', 'blue', '5. Automatic balancing', 'Tools like Cruise Control plan moves for you.', ['Metrics', '*planner', 'Moves'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../../01-introduction/03-kafka-architecture/">1.3 Architecture</a>.')
