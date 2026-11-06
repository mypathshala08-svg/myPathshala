import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l31_groups.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('600 orders arrived in only 3 trips. How does one poll() bring back 200 records?',
    'A Kafka consumer does not ask for one message at a time. It <b>fetches</b> big chunks from partition leaders in the background, and each <code>poll()</code> hands you a slice. Then two colleagues joined the same group and Kafka split the 6 partitions 2-2-2 without anyone writing a single line of coordination code.',
    ['What really happens inside <code>poll()</code>.',
     'Who decides which consumer gets which partition (the group coordinator).',
     'How to see every member, its partitions and the group state from the CLI.'])
cmap = concept_map('Concept map. Beginner: consumer, poll loop, group.id. Intermediate: fetch, group coordinator, assignment, heartbeats, group states. Advanced: rebalancing protocols, offsets and lag, static membership.',
    [[('cn', 'Consumer', 'pulls records', None), ('pl', 'Poll loop', 'poll → process', None), ('gi', 'group.id', 'one team', B + '01-introduction/02-messaging-models-queue-vs-pub-sub/')],
     [('fe', 'Fetching', 'batches from leaders', None), ('co', 'Group coordinator', 'a broker', None), ('as', 'Assignment', 'who owns what', None), ('hb', 'Heartbeats + timeouts', 'liveness', None)],
     [('rb', 'Rebalancing', 'Lesson 3.2', B + '03-consumers/02-rebalancing-and-partition-assignment/'), ('of', 'Offsets + lag', 'Lesson 3.3', B + '03-consumers/03-offsets-commits-and-lag/'), ('sm', 'Static membership', 'group.instance.id', None)]],
    [('cn', 'fe'), ('pl', 'hb'), ('gi', 'co'), ('co', 'as'), ('as', 'rb'), ('hb', 'rb'), ('pl', 'of'), ('hb', 'sm')],
    {'cn', 'pl', 'gi', 'fe', 'co', 'as', 'hb'},
    '<b>Builds on:</b> <a href="../../01-introduction/02-messaging-models-queue-vs-pub-sub/">1.2</a>, Module 2. <b>Next:</b> <a href="../02-rebalancing-and-partition-assignment/">3.2 Rebalancing</a>.')
whw = why_how_where(
    'One consumer cannot keep up with a busy topic, and if it dies someone must take over. Groups share the work and recover automatically.',
    'Consumers with the same group.id register with a group coordinator broker; partitions are divided among members; each member fetches from its partitions’ leaders and polls records in batches.',
    'Every service that reads Kafka: kitchen and billing services, stream processors, sink connectors, Spark jobs.',
    'A group cannot use more active members than partitions, and a member that stops polling is treated as dead.')

sc_ = (cyl(14, 30, 120, 90, 'orders-31', 'blue') + t(74, 136, '6 partitions, 600 orders', 7.6, 'ink2') +
       ''.join(arrow(134, 75, 236, 40 + k * 36, 'green', 1.2) + box(236, 22 + k * 36, 170, 30, 'green', rx=6) + icon('chef', 244, 25 + k * 36, 0.95) + t(276, 41 + k * 36, f'kitchen-{k+1}: P{2*k}, P{2*k+1}', 8, 'ink', anchor='start', bold=True) for k in range(3)) +
       box(440, 30, 186, 90, 'violet', rx=8) + t(533, 48, 'group coordinator', 8.6, bold=True) + t(533, 64, 'broker k2', 7.8, 'ink2', mono=True) + t(533, 82, 'members: 3', 7.8, 'ink2') + t(533, 98, 'state: Stable', 7.8, 'ink2') +
       arrow(406, 75, 440, 75, 'violet', 1, dash=True))
scene_svg = scene('Topic orders-31 with 6 partitions is read by group kitchen-31: kitchen-1 owns partitions 0 and 1, kitchen-2 owns 2 and 3, kitchen-3 owns 4 and 5. Broker k2 is the group coordinator; the group has 3 members and is Stable.', sc_,
                  'One group, three members, <tspan font-weight="700" class="s-acc">two partitions each</tspan>.')
dialogue = '''R> Sir, I wrote a consumer with a <code>while True: poll()</code> loop. Is it reading one message per call?
A> No. Behind <code>poll()</code> the client fetches large batches from each partition leader and keeps them in memory. Each call just hands you the next records. We will see 200 per call.
K> And if we start more copies of the same program?
A> If they share the same <code>group.id</code>, one broker, the <b>group coordinator</b>, splits the partitions among them. Start them and watch the assignment change.'''

lv = '''
LEVELS> Consumers at three levels
L1> Kitchen staff
      <ul>
        <li>Orders arrive on six counters (partitions). One cook can serve all six; when two more cooks join, the manager (coordinator) gives each cook two counters. Nobody serves the same counter twice.</li>
      </ul>
L2> The poll loop
      <ul>
        <li><code>subscribe([topic])</code>, then loop: <code>poll()</code> (one record) or <code>consume(n)</code> (up to n), process, commit (Lesson 3.3), repeat.</li>
        <li>The client fetches in the background (<code>fetch.min.bytes</code>, <code>fetch.max.wait.ms</code>, <code>max.partition.fetch.bytes</code>); Java returns up to <code>max.poll.records</code> (500) per poll.</li>
        <li>The <b>group coordinator</b> is the leader of the <code>__consumer_offsets</code> partition chosen by hashing the group id.</li>
      </ul>
L3> Liveness and states
      <ul>
        <li>A member is alive while it sends <b>heartbeats</b> (<code>session.timeout.ms</code>, 45 s default) and keeps calling poll within <code>max.poll.interval.ms</code> (5 min). Slow processing beyond that → the member is removed and its partitions move.</li>
        <li>Group states: Empty, PreparingRebalance, CompletingRebalance, Stable, Dead (classic protocol); the new consumer protocol (KIP-848) uses Empty, Assigning, Reconciling, Stable.</li>
        <li><b>Static membership</b> (<code>group.instance.id</code>) lets a restarted pod keep its partitions without a rebalance, within the session timeout.</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of kafka-consumer-groups describe members output: group name, consumer id made of client id plus a unique suffix, host, client id and number of partitions.',
    t(16, 22, 'kafka-consumer-groups.sh --describe --members (one row)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('kitchen-31', 'violet', 1), ('kitchen-1-34f5d1aa-…', 'blue', 2), ('/172.21.0.1', 'card', 3), ('kitchen-1', 'green', 4), ('#PARTITIONS 2', 'acc', 5)]) +
    t(34, 82, '--describe --state:  COORDINATOR k2:9092 (2)   ASSIGNMENT-STRATEGY range   STATE Stable   #MEMBERS 3', 7.8, 'ink2', anchor='start', mono=True) + pin(18, 78, 6) +
    legend(16, 116, [(1, 'Group', 'all members share offsets and partitions'), (2, 'Consumer id', 'client.id + random suffix, given by the coordinator'),
                     (3, 'Host', 'where the member runs'), (4, 'Client id', 'your label; set it to find pods in logs'),
                     (5, 'Partitions', 'how many this member owns now'), (6, 'Coordinator + state', 'broker managing the group; Stable = no rebalance in progress')], size=8, gap=15, w=140),
    h=218, caption='Real output from our lab, dissected.')
extra = '''

  <h3>Dissect the group view</h3>
''' + DIS + '''

  <h3>Consumer settings you meet first</h3>
''' + table(['Setting', 'Default', 'What it controls'], [
    ['group.id', 'none', 'which group (and offsets) this consumer uses'],
    ['auto.offset.reset', 'latest', 'where a new group starts: earliest / latest / none'],
    ['enable.auto.commit', 'true', 'commit offsets automatically (Lesson 3.3)'],
    ['max.poll.records (Java)', '500', 'records returned per poll'],
    ['fetch.min.bytes / fetch.max.wait.ms', '1 byte / 500 ms', 'how long a fetch waits for data'],
    ['session.timeout.ms', '45 s', 'no heartbeat for this long → member removed'],
    ['max.poll.interval.ms', '5 min', 'no poll for this long → member leaves the group'],
    ['group.protocol', 'classic (4.x clients may choose consumer)', 'rebalance protocol (Lesson 3.2)'],
], minw=620)

types_html = table(['Consumer style', 'API', 'When'], [
    ['Group subscribe', '<code>subscribe([t])</code> + group.id', 'normal services; automatic assignment and failover'],
    ['Manual assign', '<code>assign([TopicPartition(t, 2)])</code>', 'tools, replays, one specific partition; no group coordination'],
    ['Batch consume', '<code>consume(num_messages=200)</code>', 'higher throughput processing'],
    ['Share group (4.x)', '<code>kafka-console-share-consumer</code>, ShareConsumer API', 'queue-style work (Lesson 6.1)'],
], minw=600)
warn = 'Long processing inside the poll loop (calling a slow API for each record) can exceed <code>max.poll.interval.ms</code>: the member is kicked out, its partitions move, and records are processed twice. Keep work per poll small, or hand it to worker threads while the loop keeps polling.'

steps = [
    ('Step 1 · One consumer, many records per poll',
     code('python', 'l31_groups.py', 'c = Consumer({"bootstrap.servers": BS, "group.id": "kitchen-31",\n              "auto.offset.reset": "earliest", "client.id": "kitchen-1"})\nc.subscribe(["orders-31"], on_assign=lambda cons, parts: print("on_assign:", ...))\nmsgs = c.consume(num_messages=200, timeout=1.0)', sec('== 1)', '== 2)')),
     'Alone in the group, kitchen-1 was assigned all 6 partitions (the <code>on_assign</code> callback tells you). Each <code>consume(200)</code> returned 200 records, mixing partitions: 600 orders in 3 calls.'),
    ('Step 2 · Two more members join',
     code('python', 'l31_groups.py', 'for name in ("kitchen-2", "kitchen-3"):\n    m = Consumer({"bootstrap.servers": BS, "group.id": "kitchen-31", "client.id": name})\n    m.subscribe(["orders-31"], on_assign=...)', sec('== 2)', '== 3)')),
     'Nobody told kitchen-1 to give anything up. The coordinator triggered a rebalance and the default <code>range</code> strategy split the partitions 2-2-2.'),
    ('Step 3 · The members, from the broker',
     code('bash', 'terminal', 'kafka-consumer-groups.sh --bootstrap-server k1:9092 --describe --group kitchen-31 --members', sec('== 3)', '== 4)')),
     'Each member’s id is its <code>client.id</code> plus a unique suffix. Set a meaningful client.id (pod name) so you can find a slow member.'),
    ('Step 4 · Coordinator and state',
     code('bash', 'terminal', 'kafka-consumer-groups.sh --bootstrap-server k1:9092 --describe --group kitchen-31 --state', sec('== 4)')),
     'Broker k2 coordinates this group (another group may land on another broker). <b>Stable</b> means members agree on the assignment.'),
]

see = [term([('on_assign: [0, 1, 2, 3, 4, 5]', W), ('poll 1: 200 records', W), ('total 600 records in 3 polls', G)], size=7.2),
       term([('kitchen-1 now owns: [0, 1]', G), ('kitchen-2 owns: [2, 3]', G), ('kitchen-3 owns: [4, 5]', G)], size=7.2),
       term([('kitchen-1-34f5…  kitchen-1  2', W), ('kitchen-2-9cd7…  kitchen-2  2', W), ('kitchen-3-db36…  kitchen-3  2', W)], size=7.0),
       term([('COORDINATOR k2:9092 (2)', W), ('STRATEGY range  STATE Stable', G), ('#MEMBERS 3', W)], size=7.2)]
def owners(groups):
    o = ''
    for k, (n, ps) in enumerate(groups):
        o += opbox(200, 30 + k * 34, n, ', '.join(f'P{p}' for p in ps), 'green', 140, 28)
    return o + ''.join(pcol(40, 30 + k * 18, f'P{k}', ['…'], 'blue', cw=60, ch=14) for k in range(6))
B1 = [t(180, 14, 'One member owns all', 9, bold=True) + owners([('kitchen-1', range(6))]) + cap('Fetch big, hand out per poll.', '', 'blue', y=144, h=30),
      t(180, 14, 'Coordinator splits partitions', 9, bold=True) + owners([('kitchen-1', [0, 1]), ('kitchen-2', [2, 3]), ('kitchen-3', [4, 5])]) + cap('range strategy: 2-2-2.', '', 'green', y=144, h=30),
      t(180, 14, 'Broker sees members', 9, bold=True) + owners([('kitchen-1', [0, 1]), ('kitchen-2', [2, 3]), ('kitchen-3', [4, 5])]) + cap('client.id helps find pods.', '', 'blue', y=144, h=30),
      t(180, 14, 'Coordinator: broker 2', 9, bold=True) + opbox(120, 50, 'k2', 'Stable · 3 members', 'violet', 120, 40) + cap('Group state Stable.', '', 'violet', y=144, h=30)]
two = anim_two('Consumers and consumer groups', 'Poll, split, observe', 'Real outputs from the lab', 'What the group does', see, B1, ['Poll.', 'Join.', 'Members.', 'State.'], ['Fetch.', 'Assign.', 'Describe.', 'Coordinator.'])
pe = peel('What happens inside poll()', 'From subscribe to records in your hand. (Simplified.)',
    [('subscribe()', ''), ('Find coordinator', ''), ('Join + assign', ''), ('Fetch', ''), ('poll() returns', ''), ('Heartbeat', '')],
    [['subscribe()', 'only records the topics', 'nothing happens yet', ''], ['Find coordinator', 'hash(group.id) →', '__consumer_offsets partition', '→ its leader (k2)'],
     ['Join + assign', 'members register', 'strategy assigns', 'on_assign callback'], ['Fetch', 'background fetches from', 'each partition leader', 'into an in-memory queue'],
     ['poll() returns', 'next records from', 'the queue (up to n)', 'your code processes'], ['Heartbeat', 'keeps membership alive', 'missed → removed', '→ rebalance (3.2)']],
    ['Subscribe.', 'Coordinator.', 'Assign.', 'Fetch.', 'Deliver.', 'Stay alive.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Kicked out for being slow', 'max.poll.interval.ms exceeded. (Typical.)', ('Poll interval', 'Keep processing per poll short or the member is removed'), [
    ('Billing calls a slow GST API', '500 records × 1 s each', 'One poll = 8 min.', 'blue'), ('max.poll.interval 5 min', 'member removed', 'Partitions move.', 'red'),
    ('Another member re-processes', 'uncommitted records', 'Duplicates.', 'red'), ('Smaller batches', 'max.poll.records 50', 'Or async workers.', 'green'),
    ('Stable again', 'poll every few seconds', 'Fixed.', 'blue')], ['Slow API.', 'Kicked.', 'Repeat.', 'Tune.', 'Stable.'], 'scenario-pollinterval') + \
       five('Real-time scenario 2', 'Pods restarting during deploy', 'Static membership. (Typical.)', ('Static membership', 'group.instance.id lets a restarting member keep its partitions'), [
    ('Rolling deploy of 6 pods', 'each restart = rebalance', '6 rebalances.', 'red'), ('Set group.instance.id', 'pod-1 … pod-6', 'Stable identity.', 'green'),
    ('Pod restarts within timeout', 'keeps its partitions', 'No rebalance.', 'green'), ('Session timeout tuned', 'longer than restart time', 'e.g. 60 s.', 'amber'),
    ('Smooth deploys', 'no processing pauses', 'Done.', 'blue')], ['Deploy.', 'Identity.', 'Keep.', 'Tune.', 'Smooth.'], 'scenario-static') + \
       five('Real-time scenario 3 · advanced', 'Hot coordinator', 'Many groups on one broker. (Typical.)', ('Coordinators', 'Each group has one coordinator broker chosen by hashing its id'), [
    ('500 consumer groups', 'heavy rebalancing', 'One broker busy.', 'blue'), ('Coordinator = leader of', 'hash(group) % 50 offsets partition', 'Spread by hash.', 'blue'),
    ('Unlucky hash + busy groups', 'one broker overloaded', 'Slow joins.', 'red'), ('Rebalance leadership', 'of __consumer_offsets', 'Spread load.', 'green'),
    ('Reduce churn', 'static members, KIP-848', 'Fewer rebalances.', 'blue')], ['Many groups.', 'Hash.', 'Hot.', 'Spread.', 'Calm.'], 'scenario-coordinator')
assemble(HERE, h2_story='Three cooks, six counters', hook_html=hk,
    narration='TiffinGo’s kitchen service reads all orders with one consumer. At lunch it falls behind. Kabir starts two more copies of the same program and wonders how they will avoid cooking the same order twice.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Consumers and consumer groups',
    formal='A Kafka <b>consumer</b> reads records by repeatedly <b>polling</b>; the client <b>fetches</b> batches of records from partition leaders and returns them to the application in order per partition. Consumers that share a <b>group.id</b> form a <b>consumer group</b>, coordinated by a broker acting as <b>group coordinator</b>, which tracks membership through heartbeats and ensures each partition is assigned to exactly one member. The group stores its progress as committed offsets in the internal topic <code>__consumer_offsets</code>.',
    simple='A consumer keeps asking Kafka for new records. Several consumers with the same group name become a team: one broker acts as the team manager and gives each member its own partitions, so no record is handled twice and the work is shared.',
    term_rows=[('poll()', 'Get the next records.'), ('Fetch', 'Background download from leaders.'), ('Group coordinator', 'Broker managing a group.'), ('Assignment', 'Partitions owned by a member.'), ('Heartbeat', '“I am alive” signal.'), ('session.timeout.ms', 'Max silence before removal.'), ('max.poll.interval.ms', 'Max time between polls.'), ('client.id', 'Your label for a consumer.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Kafka pushes messages to consumers.', 'Consumers pull; the client fetches in the background.', 'Step 1: 200 records per consume call.'),
               ('ZooKeeper tracks consumer offsets.', 'Offsets live in __consumer_offsets; a broker coordinates the group.', 'Step 4: coordinator k2.'),
               ('You must code which consumer reads which partition.', 'The coordinator assigns automatically when you subscribe.', 'Step 2: 2-2-2 split.')],
    exam='“How do consumer groups work?” Members with the same group.id register with a coordinator broker; partitions are assigned so each partition has one member; members heartbeat and poll within max.poll.interval.ms; offsets are committed to __consumer_offsets; failures or joins trigger a rebalance.',
    types_h2='Ways to consume', types_html=types_html, warn=warn,
    steps_h2='A group in action', steps_intro='All outputs are real: Kafka 4.4.0, 3 brokers; Python <code>confluent-kafka</code> 2.16.1; topic <code>orders-31</code>, 6 partitions, 600 orders. Script: <code>jobs/m3/l31_groups.py</code>.',
    steps=steps, two=two, peel_intro='Now peel what happens inside poll().', peel_html=pe,
    scen_intro='Three live scenarios: a slow member, rolling deploys, and a busy coordinator.', scen=scen,
    uc_h2='Consumer groups at work', ucs=[uc_('food', 'kitchen', 'blue', '1. Order processing', 'Kitchen pods share order partitions and fail over automatically.', ['Orders', '*group', 'Pods']),
        uc_('mail', 'senders', 'green', '2. Notification senders', 'SMS and email workers scale up to the partition count.', ['Alerts', '*group', 'Senders']),
        uc_('ETL', 'sinks', 'violet', '3. Sink connectors', 'Kafka Connect tasks are consumer group members (Module 7).', ['Topic', '*tasks', 'Database']),
        uc_('Spark', 'stream', 'acc', '4. Spark jobs', 'Spark reads Kafka with its own offset tracking (Lesson 9.4).', ['Topic', '*Spark', 'Lake']),
        uc_('ops', 'monitor', 'blue', '5. Operations', 'kafka-consumer-groups shows members and lag during incidents.', ['Alert', '*describe', 'Fix'])],
    uc_note='Examples are simplified descriptions of common patterns.',
    pre='<b>Before you start:</b> <a href="../../01-introduction/02-messaging-models-queue-vs-pub-sub/">1.2 Queue vs pub-sub</a> and Module 2.')
