import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l112_compare.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('Five orders go into RabbitMQ and five into Kafka. A billing service joins five minutes later. Who still has the orders for it?',
    'Only Kafka. In our lab RabbitMQ 4.4 handed the five orders to two competing consumers and, once acknowledged, they were <b>gone</b>: the late billing consumer got nothing. Kafka kept all five; two groups each read all five, and a new group <b>replayed</b> them. That one difference, a <b>queue that deletes</b> versus a <b>log that keeps</b>, explains most of the “Kafka vs X” question.',
    ['Message broker vs distributed log, shown with a real test.',
     'Kafka vs RabbitMQ, Pulsar, cloud queues and others.',
     'A simple way to choose, and when to use two together.'])
cmap = concept_map('Concept map. Beginner: queue vs log, ack deletes vs retention. Intermediate: RabbitMQ exchanges and quorum queues, Pulsar segments and BookKeeper, cloud queues. Advanced: ordering and replay needs, routing, multi-tenancy, choosing and combining.',
    [[('qp', 'Queue vs pub-sub', 'Lesson 1.2', B + '01-introduction/02-messaging-models-queue-vs-pub-sub/'), ('sg', 'Share groups', 'Lesson 6.1', B + '06-queues-and-error-handling/01-share-groups-queues-for-kafka/')],
     [('rb', 'RabbitMQ', 'smart broker', None), ('kf', 'Kafka', 'durable log', None), ('pl', 'Pulsar', 'log + queue, tiers', None), ('cq', 'Cloud queues/streams', 'SQS, Pub/Sub, Kinesis', None)],
     [('rp', 'Replay + retention', 'reprocess', None), ('rt', 'Routing', 'exchanges, filters', None), ('mt', 'Multi-tenancy', 'namespaces', None), ('ch', 'Choose / combine', 'decision', None)]],
    [('qp', 'rb'), ('qp', 'kf'), ('sg', 'kf'), ('kf', 'pl'), ('kf', 'cq'), ('kf', 'rp'), ('rb', 'rt'), ('pl', 'mt'), ('rp', 'ch'), ('rt', 'ch')],
    {'rb', 'kf', 'pl', 'cq', 'rp', 'rt', 'mt', 'ch'},
    '<b>Builds on:</b> <a href="../../01-introduction/02-messaging-models-queue-vs-pub-sub/">1.2</a>, <a href="../../06-queues-and-error-handling/01-share-groups-queues-for-kafka/">6.1</a>. <b>Next:</b> <a href="../03-whats-new-in-kafka-4/">11.3 What’s new in Kafka 4</a>.')
whw = why_how_where(
    'Interviewers and architects ask it constantly, and picking the wrong tool is expensive: a task queue on Kafka can be awkward; an event history on RabbitMQ is impossible once messages are acked.',
    'RabbitMQ routes messages through exchanges into queues and deletes them after acknowledgement (streams are the exception). Kafka appends to partitioned logs and keeps data by retention; consumers track their own offsets. Pulsar stores segments in BookKeeper with stateless brokers and supports both streaming and queue subscriptions.',
    'RabbitMQ: task queues, RPC, complex routing, per-message TTL/priority. Kafka: event streaming, many independent consumers, replay, CDC, analytics. Pulsar: multi-tenant, geo-replicated messaging with tiered storage. Cloud services when you want zero operations on one cloud.',
    'Kafka has no per-message routing or priorities and (before share groups) no per-message acks; RabbitMQ has limited replay and lower throughput for huge fan-out; Pulsar has more moving parts (BookKeeper, ZooKeeper/metadata store).')

def qvl(hl=-1):
    o = box(8, 30, 160, 84, 'amber' if hl != 0 else 'acc', rx=8) + t(88, 46, 'queue (RabbitMQ)', 7.8, bold=True)
    for k in range(5): o += box(16 + k * 30, 58, 26, 20, 'card', rx=3) + t(29 + k * 30, 72, f'o{k+1}', 6.6, 'ink')
    o += t(88, 100, 'ack → deleted', 7.2)
    o += box(190, 30, 164, 84, 'blue' if hl != 1 else 'acc', rx=8) + t(272, 46, 'log (Kafka)', 7.8, bold=True)
    for k in range(5): o += box(198 + k * 30, 58, 26, 20, 'green', rx=3) + t(211 + k * 30, 72, f'o{k+1}', 6.6, 'ink')
    return o + t(272, 100, 'kept; each group has an offset', 7.0)
scene_svg = scene('Left: a RabbitMQ queue where messages are deleted after acknowledgement. Right: a Kafka log where the same messages are kept and each consumer group keeps its own offset.', qvl(),
                  'A queue <tspan font-weight="700" class="s-acc">forgets</tspan>; a log remembers.')
dialogue = '''K> Sir, my friend’s company uses RabbitMQ and says Kafka is overkill. Who is right?
A> Both, for different jobs. RabbitMQ is a smart post office: route a message, deliver it, forget it. Kafka is a shared ledger: write once, many readers, read again any time.
R> Can we see the difference, not just hear it?
A> Same five orders into both, then a late consumer. Let’s run it.'''

lv = '''
LEVELS> Comparing at three levels
L1> Post office vs newspaper archive
      <ul>
        <li>A post office delivers each letter once and keeps nothing (queue). A newspaper archive keeps every edition, and any reader can start from any date (log).</li>
      </ul>
L2> The main differences
      <ul>
        <li><b>Storage</b>: RabbitMQ deletes acked messages (except RabbitMQ Streams); Kafka retains by time/size or compaction.</li>
        <li><b>Consumers</b>: RabbitMQ competing consumers on a queue, broker tracks delivery; Kafka groups track offsets, any number of groups read independently; Kafka share groups (4.x) add queue-style per-record acks.</li>
        <li><b>Routing</b>: RabbitMQ exchanges (direct, topic, fanout, headers), priorities, per-message TTL; Kafka routes by topic and key only.</li>
        <li><b>Scale</b>: Kafka partitions scale to very high throughput and long retention; RabbitMQ quorum queues favour moderate rates and low latency per message.</li>
      </ul>
L3> Others
      <ul>
        <li><b>Apache Pulsar</b>: brokers are stateless, storage in Apache BookKeeper; topics with segments, tiered storage, multi-tenancy (tenants/namespaces), exclusive/shared/failover/key_shared subscriptions, built-in geo-replication.</li>
        <li><b>Cloud</b>: AWS SQS (queue) and Kinesis (stream), Google Pub/Sub, Azure Service Bus / Event Hubs; <b>NATS JetStream</b>, <b>Redis Streams</b> for lighter needs; <b>Redpanda</b> as a Kafka-API engine.</li>
        <li>Many systems use two: RabbitMQ (or share groups) for task dispatch, Kafka as the event backbone. With Kafka 4.x share groups, some teams no longer need a separate queue.</li>
      </ul>
/LEVELS
'''
DM = figure('Decision guide: if you need replay or many independent consumers, use a log such as Kafka; if you need per-message routing, priorities or RPC, use RabbitMQ; if you need simple work distribution on Kafka, use share groups; if you want zero operations on one cloud, use that cloud’s queue or stream service.',
    t(16, 22, 'Which one? Start from the need', 8.6, 'ink', anchor='start', bold=True) +
    ''.join(box(16, 34 + k * 30, 300, 24, 'card', rx=4) + t(26, 50 + k * 30, q, 7.6, 'ink', anchor='start') + arrow(318, 46 + k * 30, 340, 46 + k * 30) + box(342, 34 + k * 30, 280, 24, tn, rx=4) + t(482, 50 + k * 30, a, 7.6, bold=True)
            for k, (q, a, tn) in enumerate([('Replay history? Many independent readers?', 'Kafka (log)', 'blue'), ('Complex routing, priorities, RPC replies?', 'RabbitMQ', 'amber'),
                                             ('Task queue but already on Kafka?', 'Kafka share groups (6.1)', 'green'), ('Multi-tenant, geo, tiered by design?', 'Pulsar (or Kafka + tiered storage)', 'violet'),
                                             ('Zero ops, one cloud, modest scale?', 'SQS / Pub/Sub / Service Bus', 'card')])),
    h=192, caption='Answer the questions top to bottom.')
extra = '''

  <h3>A quick decision guide</h3>
''' + DM

types_html = table(['', 'Kafka', 'RabbitMQ', 'Pulsar', 'Cloud queue (SQS)'], [
    ['Model', 'partitioned log', 'queues + exchanges', 'segmented log + subscriptions', 'queue'], ['After consume', 'kept (retention)', 'deleted on ack', 'kept per policy', 'deleted'],
    ['Replay', 'yes', 'no (except Streams)', 'yes', 'no'], ['Ordering', 'per partition', 'per queue (single consumer)', 'per partition/key', 'FIFO queues only'],
    ['Routing', 'topic + key', 'rich (exchanges)', 'topics, filters', 'basic'], ['Ops', 'brokers + KRaft', 'nodes (quorum queues)', 'brokers + BookKeeper + metadata', 'none (managed)'],
], minw=720)
warn = 'Compare on your access pattern, not on benchmarks from blogs. Throughput numbers depend on message size, durability settings and hardware; a fair test uses the same durability (e.g. Kafka acks=all vs RabbitMQ quorum queues with publisher confirms).'

steps = [
    ('Step 1 · RabbitMQ',
     code('python', 'l112.py', "ch.queue_declare(queue='orders-112', durable=True, arguments={'x-queue-type': 'quorum'})\nch.confirm_delivery()\nfor o in orders: ch.basic_publish(exchange='', routing_key='orders-112', body=o)\nm, props, body = ch.basic_get('orders-112'); ch.basic_ack(m.delivery_tag)", sec('== 1)', '== 2)')),
     'Two consumers shared the five orders (3 + 2) and acked them; the queue emptied. The late billing consumer found nothing. (RabbitMQ 4 also refused a classic transient queue: deprecated, so we used a quorum queue.)'),
    ('Step 2 · Kafka',
     code('python', 'l112.py', "for o in orders: p.produce('orders-112', o.encode())\nread('kitchen-112'); read('billing-112'); read('audit-112')   # three groups", sec('== 2)')),
     'Each group got all five; the topic still holds them; a new group replayed from the start.'),
]
see = [term([('depth 5', W), ('A: o1 o3 o5 · B: o2 o4', W), ('depth 0', Y), ('late C: nothing', RD)], size=6.8),
       term([('kitchen: 5', G), ('billing: 5', G), ('still 5 in topic', G), ('replay OK', G)], size=7.0)]
B1 = [qvl(0), qvl(1)]
B1 = [b + cap(c, '', tn, y=124, h=30) for b, c, tn in zip(B1, ['Acked = gone', 'Kept for every group'], ['amber', 'blue'])]
two = anim_two('Kafka vs RabbitMQ', 'Same orders, two models', 'Real outputs (RabbitMQ 4.4, Kafka 4.4)', 'Queue vs log', see, B1, ['RabbitMQ.', 'Kafka.'], ['Deleted.', 'Retained.'])
pe = peel('One order in each system, layer by layer', 'order-1. (Simplified.)',
    [('Publish', ''), ('Store', ''), ('Deliver', ''), ('Ack/commit', ''), ('After', ''), ('Late reader', '')],
    [['Publish', 'Rabbit: to exchange', 'Kafka: to topic partition', ''], ['Store', 'Rabbit: in queue (Raft)', 'Kafka: appended to log', ''], ['Deliver', 'Rabbit: pushed to one consumer', 'Kafka: pulled by each group', ''],
     ['Ack/commit', 'Rabbit: ack', 'Kafka: commit offset', ''], ['After', 'Rabbit: removed', 'Kafka: still in log', ''], ['Late reader', 'Rabbit: nothing', 'Kafka: reads from offset 0', '']],
    ['Send.', 'Store.', 'Deliver.', 'Confirm.', 'After.', 'Late.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Email sending jobs', 'Priorities and retries per job. (Typical.)', ('RabbitMQ fits', 'Or share groups'), [
    ('Jobs with priority', 'urgent OTP first', 'Need.', 'blue'), ('RabbitMQ priority queue', 'per-message TTL', 'Fit.', 'green'),
    ('Dead-letter exchange', 'failed jobs', 'Retry.', 'green'), ('No replay needed', 'jobs done = done', 'OK.', 'blue'),
    ('Or Kafka share groups', 'if on Kafka already', 'Alternative.', 'amber')], ['Need.', 'Rabbit.', 'DLX.', 'Done.', 'Alt.'], 'scenario-email') + \
       five('Real-time scenario 2', 'New analytics team', 'Needs last 30 days of orders. (Typical.)', ('Kafka fits', 'Replay'), [
    ('Orders were in RabbitMQ', 'already acked', 'Gone.', 'red'), ('Move events to Kafka', 'retention 30 days', 'Keep.', 'green'),
    ('Analytics new group', 'reads from start', 'Replay.', 'green'), ('Other teams unaffected', 'own offsets', 'Independent.', 'blue'),
    ('Keep Rabbit for tasks', 'two tools', 'Combine.', 'blue')], ['Lost.', 'Kafka.', 'Replay.', 'Isolate.', 'Combine.'], 'scenario-analytics') + \
       five('Real-time scenario 3 · advanced', 'SaaS with 500 tenants', 'Isolation and geo. (Typical.)', ('Pulsar or Kafka?', 'Tenancy model'), [
    ('500 tenants', 'quotas, namespaces', 'Need.', 'blue'), ('Pulsar tenants/namespaces', 'built-in', 'Option.', 'violet'),
    ('Kafka: prefixed ACLs + quotas', 'per tenant', 'Option.', 'blue'), ('Team skills, ecosystem', 'Connect, Streams', 'Weigh.', 'amber'),
    ('Decide by ops cost', 'and features', 'Done.', 'green')], ['Need.', 'Pulsar.', 'Kafka.', 'Weigh.', 'Decide.'], 'scenario-tenants')
assemble(HERE, h2_story='Queue or log?', hook_html=hk,
    narration='A friend’s company uses RabbitMQ and says Kafka is overkill. Kabir wants a fair, hands-on answer for TiffinGo.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Kafka vs RabbitMQ, Pulsar and others',
    formal='<b>Message brokers</b> such as RabbitMQ route messages to queues and remove them once consumers acknowledge them, optimising per-message delivery and routing. <b>Distributed logs</b> such as Kafka append records to partitioned, replicated logs retained independently of consumption, letting many consumer groups read and replay at their own pace. <b>Pulsar</b> combines a log with queue-style subscriptions on a layered architecture (stateless brokers, BookKeeper storage).',
    simple='RabbitMQ is like a post office: deliver and forget. Kafka is like an archive: keep everything, let anyone read from any point. Pulsar tries to do both with a different design. Pick by what you need to do with the data afterwards.',
    term_rows=[('Queue', 'Delete after ack.'), ('Log', 'Keep by retention.'), ('Exchange', 'RabbitMQ router.'), ('Quorum queue', 'Replicated Rabbit queue.'), ('Replay', 'Read old data again.'), ('BookKeeper', 'Pulsar storage layer.'), ('Subscription', 'Pulsar consumer mode.'), ('Fan-out', 'Many readers of one stream.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Kafka is a faster RabbitMQ.', 'Different models: log vs queue.', 'Lab.'),
               ('RabbitMQ cannot scale.', 'It scales well for its use cases; replay is the gap.', 'Table.'),
               ('Kafka cannot do queues.', 'Share groups (4.x) add queue semantics.', 'Lesson 6.1.')],
    exam='“Kafka vs RabbitMQ?” Log (retained, replay, many groups, partitions, high throughput) vs broker (routing, ack-delete, priorities, RPC); Pulsar: stateless brokers + BookKeeper, multi-tenant; choose by replay/fan-out vs routing/tasks; often combined.',
    types_h2='Side by side', types_html=types_html, warn=warn,
    steps_h2='Same orders, two systems', steps_intro='All outputs are real: RabbitMQ 4.4.0 (quorum queue, pika) and Kafka 4.4.0 (confluent-kafka), five orders each.',
    steps=steps, two=two, peel_intro='Now peel one order in both.', peel_html=pe,
    scen_intro='Three live scenarios: email jobs, a new analytics team, and many tenants.', scen=scen,
    uc_h2='Each tool at work', ucs=[uc_('task', 'tasks', 'amber', '1. Task queues', 'RabbitMQ or share groups.', ['Jobs', '*queue', 'Workers']),
        uc_('events', 'events', 'blue', '2. Event backbone', 'Kafka topics, many consumers.', ['Services', '*log', 'Everyone']),
        uc_('rpc', 'RPC', 'violet', '3. Request/reply', 'RabbitMQ reply queues.', ['Client', '*reply-to', 'Server']),
        uc_('cloud', 'cloud', 'green', '4. Simple cloud apps', 'SQS / Pub/Sub.', ['App', '*managed queue', 'Worker'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../../01-introduction/02-messaging-models-queue-vs-pub-sub/">1.2 Messaging models</a>.')
