import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l12_models.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)


HOOK = hook('Why did the fourth rider get zero orders?',
    'We added a fourth delivery worker to go faster, and Kafka gave it <b>nothing</b>. The reason is the single most important rule of consumer groups, and it decides how fast any Kafka system can ever go.',
    ['How the <b>same</b> topic behaves like a queue for riders and like a broadcast for SMS and analytics.',
     'The exact rule Kafka uses to give partitions to consumers.',
     'When Kafka 4.x <b>share groups</b> break that rule on purpose.'])
B = '../../'
MAP = concept_map('Concept map. Beginner: queue, pub-sub, consumer group. Intermediate: partition assignment, idle consumers, rebalancing, offsets per group. Advanced: share groups, retry and DLQ, partition sizing.',
    [[('q', 'Queue (point-to-point)', 'one consumer each', None), ('ps', 'Pub-sub', 'every subscriber', None), ('cg', 'Consumer group', 'group.id', None)],
     [('as', 'Partition assignment', 'this lesson', None), ('id', 'Idle consumers', 'this lesson', None), ('rb', 'Rebalancing', 'Lesson 3.2', B + '03-consumers/02-rebalancing-and-partition-assignment/'), ('of', 'Offsets per group', 'Lesson 3.3', B + '03-consumers/03-offsets-commits-and-lag/')],
     [('sg', 'Share groups', 'Lesson 6.1', B + '06-queues-and-error-handling/01-share-groups-queues-for-kafka/'), ('dl', 'Retry topics + DLQ', 'Lesson 6.2', B + '06-queues-and-error-handling/02-retry-topics-and-dead-letter-queues/'), ('sz', 'Partition sizing', 'Lesson 10.2', B + '10-kafka-in-production/02-performance-tuning-and-partition-sizing/')]],
    [('q', 'as'), ('cg', 'as'), ('as', 'id'), ('ps', 'of'), ('id', 'rb'), ('as', 'sg'), ('rb', 'dl'), ('id', 'sz')],
    {'q', 'ps', 'cg', 'as', 'id'},
    '<b>Builds on:</b> <a href="../01-what-is-kafka/">1.1 What is Kafka?</a> <b>Next:</b> <a href="../03-kafka-architecture/">1.3 Architecture</a>, then consumers in depth in Module 3.')
WHW = why_how_where(
    'Some work must be done once (deliver an order); some news must reach everyone (order placed). Systems need both.',
    'Same group.id → partitions split among members. Different group.ids → each group reads all partitions with its own offsets.',
    'Worker pools (riders, email senders) and fan-out to many services (SMS, analytics, fraud).',
    'Classic groups cannot use more workers than partitions, and cannot ack one record at a time: use share groups or retry topics.')
PEEL = peel('How Kafka splits a group’s work', 'What happens when rider-A, B and C join group riders. (Simplified.)',
    [('Consumers start', ''), ('Find coordinator', ''), ('Join the group', ''), ('Assignment', ''), ('Fetch', ''), ('Commit', '')],
    [['Consumers start', 'each sets group.id="riders"', 'and subscribes to', 'topic deliveries'],
     ['Group coordinator', 'one broker is responsible', 'for this group (by a hash', 'of the group id)'],
     ['Join the group', 'all 3 members register', 'and send heartbeats', 'to stay alive'],
     ['Assignment', '3 partitions, 3 members', 'P0→A, P1→B, P2→C', 'a 4th member gets nothing'],
     ['Fetch', 'each pulls only from', 'its own partitions', 'so each order once'],
     ['Commit', 'offsets saved per group', 'in __consumer_offsets', 'other groups unaffected']],
    ['Start.', 'Coordinator.', 'Join.', 'Assign.', 'Fetch.', 'Commit.'], 'scenario-peel')

def q_side(x, title, tone, outs):
    o = t(x + 150, 16, title, 8.6, bold=True) + opbox(x, 60, 'Producer', '12 orders', 'acc', 80, 34) + arrow(x + 80, 77, x + 104, 77, 'ink3', 1.2)
    o += box(x + 104, 50, 70, 54, 'card') + t(x + 139, 81, 'topic', 8, bold=True)
    for k, (n, s) in enumerate(outs):
        o += arrow(x + 174, 77, x + 210, 34 + k * 38, tone, 1) + opbox(x + 210, 20 + k * 38, n, s, 'green' if tone == 'green' else 'violet', 90, 28)
    return o
sc_ = q_side(10, 'Queue: workers SHARE the work', 'green', [('rider-A', '4 orders'), ('rider-B', '2 orders'), ('rider-C', '6 orders')]) + \
      q_side(330, 'Pub-sub: every subscriber gets ALL', 'violet', [('sms', '12 orders'), ('analytics', '12 orders')])
scene_svg = scene('Left: in queue style, three riders share twelve orders so each order is delivered once. Right: in publish-subscribe style, the SMS and analytics services each receive all twelve orders.', sc_,
                  'In Kafka, the <tspan font-weight="700" class="s-acc">consumer group</tspan> decides which model you get.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Deliver once, or tell everyone?</h2>
  <div class="story">
{HOOK}
    <p class="narration">TiffinGo has two very different needs. Each order must be picked up by <b>exactly one</b> rider, not three. But every order must also reach <b>both</b> the SMS service and analytics.</p>

{scene_svg}

R> Sir, the first one sounds like a queue and the second like a broadcast. Do we need two different systems?
A> Old setups often used a queue product for one and a pub-sub product for the other. Kafka does both with one idea: the <b>consumer group</b>. Consumers in the <b>same</b> group share the partitions, like a queue. <b>Different</b> groups each get everything, like pub-sub.
K> And if we hire a fourth rider?
A> Then you will see Kafka’s famous limit with your own eyes. Let’s run it.
  </div>
</section>
'''

lv = '''
LEVELS> Messaging models at three levels
L1> Two kinds of announcements
      <ul>
        <li><b>Queue:</b> a token counter. Each token is served by one free counter clerk. Work is divided.</li>
        <li><b>Pub-sub:</b> a railway announcement. Everyone on the platform hears every message.</li>
      </ul>
L2> How Kafka maps them
      <ul>
        <li>Queue = many consumers, <b>one</b> <code>group.id</code>. Each partition is given to one consumer in the group.</li>
        <li>Pub-sub = several <b>different</b> group ids. Each group reads every partition with its own offsets.</li>
        <li>Both at once is normal: <code>riders</code> shares work while <code>sms</code> and <code>analytics</code> each get everything.</li>
      </ul>
L3> Limits and the new queue
      <ul>
        <li>In a classic consumer group a partition has at most one consumer, so parallelism ≤ number of partitions; extra consumers sit idle.</li>
        <li>Kafka 4.x adds <b>share groups</b> (KIP-932): many consumers can share one partition, with per-record acknowledgement and redelivery, like a traditional queue (Lesson 6.1). In our 4.4 cluster the feature is enabled (<code>share.version=2</code>).</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Messaging models</h2>
''' + def_block(
    'In <b>point-to-point (queue)</b> messaging each message is consumed by exactly one of the competing consumers, distributing work. In <b>publish-subscribe</b> messaging each message is delivered to every subscriber. Kafka generalises both through <b>consumer groups</b>: within a group, each partition is assigned to one member, so members share the load (queue semantics); across groups, every group independently receives all records (pub-sub semantics). Kafka 4.x additionally provides <b>share groups</b>, where multiple consumers cooperatively consume from the same partitions with per-record acknowledgement.',
    'Same group = share the work. Different groups = everyone gets a full copy. One Kafka topic can do both at the same time.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Point-to-point', 'Each message to one consumer.'),
    ('Publish-subscribe', 'Each message to every subscriber.'),
    ('group.id', 'Name that makes consumers a group.'),
    ('Assignment', 'Which partitions a consumer owns.'),
    ('Idle consumer', 'Group member with no partition.'),
    ('Share group', 'Kafka 4.x queue-style group.'),
    ('Fan-out', 'One event to many readers.'),
    ('Competing consumers', 'Workers sharing one queue.'),
]) + '''

  <h3>Why, how, where</h3>
''' + WHW + '''

  <h3>Concept map: what depends on what</h3>
''' + MAP + '''

  <h3>Dissect the group assignment</h3>
''' + figure('Three partitions of the deliveries topic, each owned by one rider in group riders; a fourth rider has no partition. Separately, groups sms and analytics each read all three partitions.',
    pcol(60, 34, 'P0', ['o4', 'o5', 'o7', 'o9'], 'blue') + pcol(60, 60, 'P1', ['o1', 'o10'], 'blue') + pcol(60, 86, 'P2', ['o2', 'o3', 'o6', 'o8', 'o11', 'o12'], 'blue') +
    t(60, 22, 'deliveries topic', 8.4, 'ink', anchor='start', bold=True) +
    ''.join(arrow(282, 44 + k * 26, 330, 44 + k * 26, 'green', 1) + opbox(330, 32 + k * 26, f'rider-{"ABC"[k]}', '', 'green', 70, 22) for k in range(3)) +
    opbox(330, 112, 'rider-D', 'no partition', 'red', 70, 28) + pin(326, 30, 1) + pin(326, 110, 2) +
    opbox(470, 40, 'group sms', 'P0+P1+P2', 'violet', 100, 28) + opbox(470, 78, 'group analytics', 'P0+P1+P2', 'violet', 100, 28) + pin(466, 38, 3) +
    legend(20, 166, [(1, 'One partition → one consumer', 'inside a group (queue style); 4 + 2 + 6 = 12 orders, each once'),
                     (2, 'Idle consumer', 'more consumers than partitions: the extra one gets nothing'),
                     (3, 'Different groups', 'each reads all partitions with its own offsets (pub-sub)')], size=8, gap=16, w=200),
    h=236, caption='Real assignment from our lab, drawn.') + lv + myths([('Kafka is only pub-sub, not a queue.', 'One consumer group behaves like a queue; Kafka 4.x also has share groups.', 'Step 1: 12 orders delivered once across 3 riders.'), ('More consumers always means more speed.', 'In a classic group, consumers beyond the partition count are idle.', 'Step 3: r4 received 0 orders.'), ('Every group gets a copy of the data on disk.', 'There is one copy of each partition; groups only store offsets.', '__consumer_offsets holds the bookmarks (Lesson 1.3).')]) + '''
EXAM> “How does Kafka support both queue and pub-sub?” Consumers with the same group.id split the partitions (each record to one member); consumers in different groups each receive all records. Parallelism inside a group is limited by the partition count. Kafka 4.x share groups add queue semantics with per-record acks.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Which model when</h2>
''' + table(['Need', 'Kafka setup', 'Example'], [
    ['Split work across workers', 'N consumers, one group.id', 'riders share deliveries'],
    ['Every service sees every event', 'one group per service', 'sms, analytics, fraud'],
    ['Both', 'one group per service, many members each', '3 SMS workers in group sms'],
    ['Queue with per-message ack, more workers than partitions', 'share group (Kafka 4.x)', 'packing jobs (Lesson 6.1)'],
], minw=560) + '''
WARN> Adding consumers beyond the partition count does <b>not</b> speed up a classic group: in our lab the 4th rider received 0 orders. Plan partitions for your maximum parallelism. Also, with keyed data, one partition can get far more work than others (rider-C had 6 orders, rider-B only 2).
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Queue, pub-sub, idle consumer</h2>
  <p>All outputs are real: Kafka 4.4.0, 3 brokers, <code>confluent-kafka</code> 2.16. Topic <code>deliveries</code> has 3 partitions and 12 keyed orders. Script: <code>jobs/m1/l12_models.py</code> (consumers run as threads).</p>
''' + stepper([
    ('Step 1 · Queue style: one group',
     code('python', 'l12_models.py', 'for name in ["rider-A", "rider-B", "rider-C"]:\n    Consumer({"bootstrap.servers": BS, "group.id": "riders",\n              "client.id": name, "auto.offset.reset": "earliest"})', sec('== 1)', '== 2)')),
     'Three consumers with the same <code>group.id</code>. Kafka gave each one partition, so each order was delivered <b>once</b> (4 + 2 + 6 = 12). The split is uneven because keys decide partitions.'),
    ('Step 2 · Pub-sub style: two groups',
     code('python', 'l12_models.py', 'run(["sms-svc"], "sms")\nrun(["analytics-svc"], "analytics")', sec('== 2)', '== 3)')),
     'Different <code>group.id</code>s: each service received all 12. Nothing was copied in Kafka; each group simply keeps its own offsets.'),
    ('Step 3 · The fourth rider',
     code('python', 'l12_models.py', 'run(["r1", "r2", "r3", "r4"], "riders4")', sec('== 3)')),
     '4 consumers, 3 partitions: <code>r4</code> was assigned nothing and processed 0 orders. It is still useful as a standby: if <code>r1</code> crashes, a rebalance gives its partition to <code>r4</code> (Lesson 3.2).'),
]) + '''
</section>
'''

see = [
    term([('rider-A: partitions [0] -> 4 orders', W), ('rider-B: partitions [1] -> 2 orders', W), ('rider-C: partitions [2] -> 6 orders', W), ('total delivered: 12 (each order once)', G)], size=7.0),
    term([('analytics-svc: 12 orders', G), ('sms-svc: 12 orders', G)], size=7.4),
    term([('r1: partitions [0] -> 4 orders', W), ('r2: partitions [1] -> 2 orders', W), ('r3: partitions [2] -> 6 orders', W), ('r4: partitions [] -> 0 orders', RD)], size=7.0),
]
def parts(extra):
    return pcol(60, 30, 'P0', ['4'], 'blue', cw=40) + pcol(60, 56, 'P1', ['2'], 'blue', cw=40) + pcol(60, 82, 'P2', ['6'], 'blue', cw=40) + extra
B1 = [
    t(180, 14, 'One group shares partitions', 9, bold=True) + parts(''.join(arrow(102, 40 + k * 26, 200, 40 + k * 26, 'green', 1) + opbox(200, 30 + k * 26, f'rider-{"ABC"[k]}', '', 'green', 80, 20) for k in range(3))) + cap('Each order once.', '', 'green', y=144, h=30),
    t(180, 14, 'Two groups, full copies', 9, bold=True) + parts(opbox(200, 34, 'sms', 'all 12', 'violet', 90, 28) + opbox(200, 74, 'analytics', 'all 12', 'violet', 90, 28) + arrow(102, 66, 200, 48, 'violet', 1) + arrow(102, 66, 200, 88, 'violet', 1)) + cap('Own offsets per group.', '', 'violet', y=144, h=30),
    t(180, 14, 'More consumers than partitions', 9, bold=True) + parts(''.join(opbox(200, 26 + k * 26, f'r{k+1}', '', 'green', 60, 20) for k in range(3)) + opbox(200, 104, 'r4', 'idle', 'red', 60, 26)) + cap('Max parallelism = partitions.', '', 'red', y=144, h=30),
]
two = anim_two('Queue vs pub-sub in Kafka', 'Groups decide the model', 'Real outputs from the lab', 'How partitions are assigned', see, B1,
               ['Queue.', 'Pub-sub.', 'Idle.'], ['Shared work.', 'Fan-out.', 'Limit.'])

def five(kind, title, sub, cons, lines, caps, hid):
    fr = [t(180, 22, a, 9.4, 'acc' if i == 4 else 'ink', bold=True) + t(180, 56, b, 8.4, 'ink2') + cap(c, '', tone, y=150, h=34) for i, (a, b, c, tone) in enumerate(lines)]
    return anim_one(kind, title, sub, cons[0], cons[1], fr, caps, hid=hid)
s1 = five('Real-time scenario 1', 'Double SMS to customers', 'Two SMS workers in different groups. (Typical.)',
          ('Same group for workers', 'Workers of one service must share one group.id or each event is processed twice'), [
    ('Customers get 2 SMS', 'per order', 'Complaints.', 'red'),
    ('Two SMS pods', 'group.id = hostname', 'Two groups!', 'red'),
    ('Each group reads all', 'pub-sub by mistake', 'Duplicate work.', 'amber'),
    ('Fix: group.id = sms', 'same for all pods', 'Queue style.', 'green'),
    ('One SMS per order', 'pods share partitions', 'Fixed.', 'blue')],
    ['Bug.', 'Cause.', 'Fan-out.', 'Fix.', 'Done.'], 'scenario-dupsms')
s2 = five('Real-time scenario 2', 'Scaling riders for a sale', 'Hitting the partition limit. (Typical.)',
          ('Partitions cap parallelism', 'Plan enough partitions for peak consumers'), [
    ('Sale: 10× orders', 'scale to 12 rider pods', '3 partitions only.', 'blue'),
    ('9 pods idle', 'lag still grows', 'No speed-up.', 'red'),
    ('Add partitions 3 → 12', 'kafka-topics --alter', 'Keys may move (1.4).', 'amber'),
    ('12 pods busy', 'lag drops', 'Parallel.', 'green'),
    ('Plan ahead', 'partitions ≥ peak consumers', 'Design rule.', 'blue')],
    ['Sale.', 'Idle.', 'Alter.', 'Busy.', 'Rule.'], 'scenario-scale')
s3 = five('Real-time scenario 3 · advanced', 'Slow jobs, few partitions', 'When a share group fits better. (Typical.)',
          ('Share groups', 'Use share groups when jobs are independent and slow and you need more workers than partitions'), [
    ('Invoice PDF jobs', '30 s each, 1 partition', 'One consumer only.', 'blue'),
    ('Classic group', 'other workers idle', 'Backlog.', 'red'),
    ('Share group (4.x)', 'many workers per partition', 'Per-record ack.', 'green'),
    ('Failed job redelivered', 'delivery count limit', 'Then DLQ (6.2).', 'amber'),
    ('Order not needed', 'so sharing is safe', 'Choose by need.', 'blue')],
    ['Jobs.', 'Stuck.', 'Share.', 'Retry.', 'Choose.'], 'scenario-share')
animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Groups decide the model</h2>
  <p>Left: real lab output. Right: how partitions were assigned.</p>
''' + two + '''
  <p>Now peel the group protocol layer by layer.</p>
''' + PEEL + '''
  <p>Three live scenarios follow: duplicate SMS, scaling for a sale, and slow jobs.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

def uc_(word, sub, tone, title, desc, flow_):
    return usecase(f'<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-{tone}" style="stroke:var(--{tone if tone != "acc" else "track"})"/>' + t(60, 42, word, 11, tone, bold=True) + t(60, 58, sub, 7.4, 'ink2'), title, desc, flow_)
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Both models at work</h2>
''' + '\n'.join([
    uc_('ride', 'dispatch', 'blue', '1. Dispatch workers', 'A pool of dispatch workers shares ride requests in one group.', ['Requests', '*one group', 'Each once']),
    uc_('pay', 'fan-out', 'green', '2. Payment fan-out', 'Ledger, SMS and fraud each subscribe with their own group.', ['Payments', '*many groups', 'All services']),
    uc_('shop', 'emails', 'violet', '3. Email sending', 'Email workers share a topic; scaling is limited by partitions.', ['Email jobs', '*group', 'Sent once']),
    uc_('IoT', 'sensors', 'acc', '4. Sensor data', 'Alerts and storage read the same sensor stream independently.', ['Sensors', '*fan-out', 'Alerts + lake']),
    uc_('docs', 'jobs', 'blue', '5. Document processing', 'Slow independent jobs suit share groups in Kafka 4.x.', ['Jobs', '*share group', 'Workers']),
]) + '''
  <p class="muted">Examples are simplified descriptions of common patterns.</p>
</section>
'''
pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> read <a href="../01-what-is-kafka/">1.1 What is Kafka?</a> for topics, partitions and consumer groups.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
