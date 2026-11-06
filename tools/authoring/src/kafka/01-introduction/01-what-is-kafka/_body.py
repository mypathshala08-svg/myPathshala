import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l11_events.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)


HOOK = hook('One order, six systems, written only once. How?',
    'When you order food, the kitchen, billing, SMS, the rider app, fraud checks and analytics all learn about it within a second, yet the order app sends the event <b>one time</b>. By the end of this lesson you can explain how, and show it on a real cluster.',
    ['Why reading a Kafka event does <b>not</b> delete it (we prove it with numbers).',
     'How a service that did not exist yesterday can read last week’s orders.',
     'What one record really looks like on the broker’s disk, byte by byte.'])
B = '../../'
MAP = concept_map('Concept map for Kafka. Beginner: event, topic, producer and consumer, consumer group. Intermediate: partition and offset, keys and ordering, retention and replay. Advanced: replication, commit log on disk, KRaft. This lesson covers event, topic, producer/consumer, consumer group and retention.',
    [[('ev', 'Event (record)', 'key · value · time', None), ('tp', 'Topic', 'named stream', None), ('pc', 'Producer / consumer', 'write · pull', None), ('cg', 'Consumer group', 'own bookmark', B + '01-introduction/02-messaging-models-queue-vs-pub-sub/')],
     [('po', 'Partition + offset', 'Lesson 1.4', B + '01-introduction/04-topics-partitions-and-offsets/'), ('ky', 'Keys → order', 'Lesson 2.2', B + '02-producers/02-keys-and-partitioners/'), ('rt', 'Retention + replay', 'this lesson · 4.3', None), ('lg', 'Lag + offsets', 'Lesson 3.3', B + '03-consumers/03-offsets-commits-and-lag/')],
     [('rp', 'Replication', 'Lesson 5.1', B + '05-replication-and-the-cluster/01-brokers-and-replication/'), ('cl', 'Commit log on disk', 'Lesson 4.1', B + '04-storage-internals/01-the-commit-log-and-segments/'), ('kr', 'KRaft controllers', 'Lesson 1.3 · 5.4', B + '01-introduction/03-kafka-architecture/'), ('id', 'Idempotence (PID)', 'Lesson 2.5', B + '02-producers/05-idempotent-producer-and-retries/')]],
    [('ev', 'tp'), ('tp', 'pc'), ('pc', 'cg'), ('tp', 'po'), ('po', 'ky'), ('cg', 'lg'), ('po', 'cl'), ('cl', 'rp'), ('rp', 'kr'), ('ev', 'id' )][:0] + [('tp', 'po'), ('cg', 'lg'), ('ev', 'rt'), ('po', 'cl'), ('ky', 'id'), ('rt', 'rp')],
    {'ev', 'tp', 'pc', 'cg', 'rt'},
    '<b>Builds on:</b> nothing, start here. <b>Next:</b> <a href="../02-messaging-models-queue-vs-pub-sub/">1.2 Queue vs pub-sub</a> → <a href="../03-kafka-architecture/">1.3 Architecture</a> → <a href="../04-topics-partitions-and-offsets/">1.4 Partitions and offsets</a>.')
WHW = why_how_where(
    'Direct service-to-service calls break when one service is slow, and data is lost when nobody is listening.',
    'Producers append events to a replicated log; consumers pull and keep their own offsets; data stays for the retention period.',
    'Order and payment events, click streams, logs, database change streams, real-time analytics.',
    'Tiny volumes, request–reply needs (“answer me now”), or querying current state: use an API or a database.')
PEEL = peel('One order event, from your code to the disk', 'Follow “o102 PLACED” down through the layers. (Our lab cluster.)',
    [('Your app', ''), ('Client library', ''), ('Network', ''), ('Leader broker', ''), ('Partition log file', ''), ('Replicas', '')],
    [['Your app', 'p.produce("order-events",', '  key="o102", value=...)', 'returns at once (async)'],
     ['Client library', 'serialises key and value', 'hashes key → partition 0', 'batches records (linger)'],
     ['Network', 'one Produce request', 'goes to the LEADER of', 'partition 0 (broker 2)'],
     ['Leader broker', 'checks producerId + sequence', 'assigns offset 0', 'appends the batch'],
     ['Partition log file', 'orders-0/0000…0000.log', 'append-only, sequential', '.index and .timeindex too'],
     ['Replicas', 'brokers 3 and 1 fetch it', 'then the callback fires:', '“partition 0, offset 0”']],
    ['Your code.', 'Client: key → partition.', 'One request to the leader.', 'Offset assigned.', 'Written to disk.', 'Copied, then acknowledged.'],
    'scenario-peel')

# ---------------------------------------------------------------- story scene: direct calls vs Kafka
def svc(x, y, n, tone='card'):
    return box(x, y, 78, 24, tone) + t(x + 39, y + 15, n, 7.8, bold=True)
left = (t(150, 16, 'Without Kafka: every app calls every app', 8.6, bold=True) + svc(14, 40, 'Order app', 'acc') +
        ''.join(svc(200, 28 + k * 30, n) for k, n in enumerate(['Kitchen', 'Billing', 'SMS', 'Analytics'])) +
        ''.join(arrow(92, 52, 200, 40 + k * 30, 'red', 1) for k in range(4)) + t(146, 150 - 4, '1 slow app = order app stuck', 7.6, 'red'))
right = (t(480, 16, 'With Kafka: write once, many read', 8.6, bold=True) + svc(330, 64, 'Order app', 'acc') + arrow(408, 76, 436, 76, 'green', 1.4) +
         cyl(436, 50, 70, 52, 'Kafka', 'green') + ''.join(svc(548, 28 + k * 30, n) for k, n in enumerate(['Kitchen', 'Billing', 'SMS', 'Analytics'])) +
         ''.join(arrow(506, 76, 548, 40 + k * 30, 'green', 1) for k in range(4)))
sc_ = left + right
scene_svg = scene('Left: the order app calls kitchen, billing, SMS and analytics directly, so one slow service blocks orders. Right: the order app writes each event once to Kafka, and every service reads it at its own pace.', sc_,
                  'Kafka sits in the middle: <tspan font-weight="700" class="s-acc">write once</tspan>, read many times.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>The Diwali sale that broke TiffinGo</h2>
  <div class="story">
{HOOK}
    <p class="narration">TiffinGo, the Navi Mumbai tiffin-delivery start-up from our Hive and Spark courses, ran a Diwali sale. Orders jumped ten times. The order app called the kitchen service, then billing, then the SMS service, then analytics, one after another. The SMS provider slowed down, and suddenly nobody could place an order.</p>

{scene_svg}

K> Sir, the SMS service was slow, so why did <i>orders</i> fail?
A> Because the order app was waiting for SMS. Every service was wired directly to every other one. One slow wire and the whole chain stops.
R> So we need something in the middle that just… holds the events?
A> Exactly. That is <b>Apache Kafka</b>. The order app writes “order o101 was PLACED” <b>once</b>, Kafka stores it safely on disk, and kitchen, billing, SMS and analytics each read it whenever they are ready. If SMS is slow, only SMS is late. And a brand-new service can join tomorrow and read the full history. Let’s prove all of it on a real Kafka 4.4 cluster.
  </div>
</section>
'''

# ---------------------------------------------------------------- definition + dissection
lv = '''
LEVELS> Kafka at three levels
L1> The dabbawala notice board
      <ul>
        <li>Imagine a big notice board at the station. The order clerk pins a slip for every order. The kitchen, the cashier and the SMS boy each read the board and keep their own bookmark.</li>
        <li>Slips are not torn off after reading, so a new helper can start from the first slip. Kafka is that board, built for millions of slips a second.</li>
      </ul>
L2> The words
      <ul>
        <li>An <b>event</b> (record) is a fact: key <code>o101</code>, value <code>{"status":"PAID"}</code>, a timestamp and optional headers.</li>
        <li>Events go into a named <b>topic</b> (<code>order-events</code>), which is split into <b>partitions</b>; each event gets an <b>offset</b>, its position number.</li>
        <li><b>Producers</b> write, <b>consumers</b> read, and consumers with the same <code>group.id</code> form a <b>consumer group</b> that keeps its own bookmarks (committed offsets).</li>
      </ul>
L3> What makes it different
      <ul>
        <li>Kafka is a <b>distributed, replicated commit log</b>: an append-only file per partition, copied to several brokers.</li>
        <li>Reading does not delete. Data stays until the <b>retention</b> time or size is reached (7 days by default), so any number of groups can read, and re-read, independently.</li>
        <li>Since Kafka 4.0 the cluster manages itself with <b>KRaft</b> (no ZooKeeper).</li>
      </ul>
/LEVELS
'''
rec = figure('Dissection of one real Kafka record batch from kafka-dump-log: batch header with base offset, count, producer id and sequence, then one record with offset, timestamp, key and value, each with a numbered call-out.',
    t(16, 22, 'Batch header (one per batch)', 8.4, 'ink', anchor='start', bold=True) +
    fields(16, 32, [('baseOffset: 0', 'blue', 1), ('count: 3', 'blue', None), ('producerId: 1000', 'violet', 2), ('epoch: 0', 'violet', None), ('baseSequence: 0', 'violet', None), ('crc ✓', 'card', None)]) +
    t(16, 76, 'Record inside the batch (offset 0 of partition 0)', 8.4, 'ink', anchor='start', bold=True) +
    fields(16, 86, [('offset: 0', 'acc', 3), ('CreateTime: 1793877411229', 'amber', 4), ('key: Pune', 'green', 5), ('value: {"order":2,"amt":480}', 'card', 6)]) +
    legend(16, 140, [(1, 'Batch', 'records travel and are stored in batches (here 3 records)'),
                     (2, 'Producer id + sequence', 'lets the broker drop duplicate retries (Lesson 2.5)'),
                     (3, 'Offset', 'position inside the partition: 0, 1, 2 …'),
                     (4, 'Timestamp', 'milliseconds since 1970, set by the producer'),
                     (5, 'Key', 'decides the partition; same key → same partition'),
                     (6, 'Value', 'your data as bytes; Kafka does not look inside')], size=8, gap=15, w=160),
    h=244, caption='One real record batch from our lab (kafka-dump-log output), dissected.')
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>What is Apache Kafka?</h2>
''' + def_block(
    '<b>Apache Kafka</b> is an open-source, distributed <b>event-streaming platform</b>. It stores streams of records (events) in <b>topics</b>, each split into ordered, append-only, replicated <b>partitions</b> on a cluster of servers called <b>brokers</b>. <b>Producers</b> publish records, and <b>consumers</b>, organised in <b>consumer groups</b>, pull records at their own pace and track their position with <b>offsets</b>. Records are retained for a configured time or size regardless of consumption, which allows many independent readers, replay and high throughput with low latency.',
    'Kafka is a very fast, very safe “notice board” for events. Apps pin events on it once; any number of other apps read them whenever they want, and the events stay there for days so they can be read again.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Event / record', 'A fact that happened: key, value, time.'),
    ('Topic', 'A named stream of events.'),
    ('Partition', 'An ordered slice of a topic.'),
    ('Offset', 'Position number inside a partition.'),
    ('Broker', 'A Kafka server that stores partitions.'),
    ('Producer', 'App that writes events.'),
    ('Consumer group', 'Apps sharing one bookmark per partition.'),
    ('Retention', 'How long events are kept.'),
]) + '''

  <h3>Why, how, where</h3>
''' + WHW + '''

  <h3>Concept map: what depends on what</h3>
''' + MAP + '''

  <h3>The big picture</h3>
  <p>Everything in this course fits on this one page. Producers <b>push</b> events in; consumer groups <b>pull</b> them out; in the middle, a cluster of brokers keeps each partition with one leader and two copies.</p>
''' + big_picture() + '''
  <h3>Dissect a real record</h3>
  <p>This is what Kafka actually stored on disk for three TiffinGo orders, read with the <code>kafka-dump-log.sh</code> tool. Each number marks one part.</p>
''' + rec + '''

  <h3>Kafka facts</h3>
''' + table(['Fact', 'Value (checked Nov 2026)'], [
    ['Created at', 'LinkedIn (around 2010); Apache top-level project since 2012'],
    ['Written in', 'Java and Scala; clients in Java, Python, Go, C/C++, .NET and more'],
    ['Latest release', '<b>4.4.0</b> (22 Oct 2026); ZooKeeper removed in 4.0, KRaft only'],
    ['Default retention', '7 days (<code>log.retention.hours=168</code>)'],
    ['Licence', 'Apache License 2.0'],
], minw=520) + lv + myths([('Kafka deletes a message once it is consumed.', 'Messages stay until retention (default 7 days); any number of groups can read them.', 'Step 4: 2 + 1 + 3 = 6 events still stored after two groups read them.'), ('Kafka needs ZooKeeper.', 'Since Kafka 4.0 ZooKeeper is removed; KRaft controllers manage metadata.', 'our 4.4 cluster runs with no ZooKeeper at all (Lesson 1.3).'), ('Producers fire and forget by default.', 'Since Kafka 3.0 the default is acks=all with idempotence on.', 'the dumped batch carries producerId 1000 and sequence numbers.')]) + '''
EXAM> “What is Kafka?” Say: a distributed, partitioned, replicated commit log used as an event-streaming platform. Producers append records to topic partitions on brokers; consumers in groups pull and track offsets; records are retained by time/size, not deleted on read, so many consumers can read and replay independently.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Five jobs Kafka does</h2>
''' + table(['Use', 'What flows', 'TiffinGo example'], [
    ['Messaging / decoupling', 'events between services', 'order → kitchen, billing, SMS'],
    ['Activity tracking', 'clicks, searches, views', 'which tiffins users browse'],
    ['Log and metrics pipeline', 'app logs, metrics', 'all servers’ logs to one place'],
    ['Stream processing', 'events computed in real time', 'orders per city per minute (Module 9)'],
    ['Data integration / CDC', 'database changes', 'MySQL orders table → data lake (Module 7)'],
], minw=560) + '''

  <h3>Kafka and its neighbours</h3>
''' + table(['', 'Kafka', 'Classic queue (e.g. RabbitMQ)', 'Database'], [
    ['Read deletes data?', 'No, kept by retention', 'Yes, usually removed after ack', 'No'],
    ['Many independent readers', 'Yes (consumer groups)', 'Needs one queue per reader', 'Yes, by polling'],
    ['Replay old events', 'Yes, from any offset', 'Usually no', 'Query, not a stream'],
    ['Order guarantee', 'Per partition', 'Per queue', 'n/a'],
    ['Best at', 'High-volume event streams', 'Task queues, routing', 'Current state, queries'],
], minw=620) + '''
WARN> Kafka is not a database you query (“give me order o101”) and not a good fit for a few messages per day. It shines when many events flow continuously and several systems need them. Also, Kafka keeps order only <b>inside one partition</b>, not across a whole topic (Lesson 1.4).
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>One stream, many readers, replay</h2>
  <p>All outputs are real: Kafka 4.4.0 cluster of 3 brokers (KRaft) in Docker, Python client <code>confluent-kafka</code> 2.16. Topic <code>order-events</code> has 3 partitions. Script: lab <code>jobs/m1/l11_events.py</code>.</p>
''' + stepper([
    ('Step 1 · The order app produces events',
     code('python', 'l11_events.py', 'p = Producer({"bootstrap.servers": "k1:9092,k2:9092,k3:9092"})\nfor oid, st, city, amt in events:\n    p.produce("order-events", key=oid,\n              value=json.dumps({"order": oid, "status": st, "city": city, "amount": amt}),\n              callback=cb)          # cb prints partition and offset\np.flush()', sec('== 1)', '== 2)')),
     'Six events for three orders. All three events of <code>o101</code> landed in partition 2 with offsets 0, 1, 2, because they share the same <b>key</b>: so they stay in order. The callback is Kafka’s receipt: “stored at partition X, offset Y”.'),
    ('Step 2 · The kitchen reads',
     code('python', 'l11_events.py', 'c = Consumer({"bootstrap.servers": BS, "group.id": "kitchen",\n              "auto.offset.reset": "earliest"})\nc.subscribe(["order-events"])\nm = c.poll(1.0)           # pull, at the kitchen\'s own pace', sec('== 2)', '== 3)')),
     'The kitchen is a <b>consumer</b> in group <code>kitchen</code>. It <b>pulls</b> events; Kafka never pushes. <code>auto.offset.reset=earliest</code> means “a new group starts from the oldest event”.'),
    ('Step 3 · Billing reads the same events',
     code('python', 'l11_events.py', 'read("billing")           # a different group.id', sec('== 3)', '== 4)')),
     'Billing gets all 6 again. Each consumer group has its <b>own bookmark</b>, so groups never steal events from each other. This is how one event serves many services.'),
    ('Step 4 · Reading did not delete anything',
     code('python', 'l11_events.py', 'lo, hi = c.get_watermark_offsets(TopicPartition("order-events", pt))', sec('== 4)', '== 5)')),
     'The partitions still hold 2 + 1 + 3 = 6 events after two groups read them. Kafka deletes only when <b>retention</b> expires (7 days by default), never because someone read the data.'),
    ('Step 5 · A new service replays history',
     code('python', 'l11_events.py', 'read("analytics")         # joins later, starts from the earliest offset', sec('== 5)')),
     'An analytics service that did not exist yesterday reads the full history. With a classic queue those messages would be gone. Replay is also how you fix a bug: correct the code and read again.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- animation
see = [
    term([('sent o101 PLACED -> partition 2 offset 0', W), ('sent o102 PLACED -> partition 0 offset 0', W), ('sent o101 PAID   -> partition 2 offset 1', W)], size=7.2),
    term([('kitchen got 6 events', G), ('o101:PLACED, o101:PAID, ...', W)], size=7.4),
    term([('billing got 6 events', G), ('(same 6, separate bookmark)', W)], size=7.4),
    term([('partition 0: 2 events still stored', Y), ('partition 1: 1 events still stored', Y), ('partition 2: 3 events still stored', Y)], size=7.2),
    term([('analytics got 6 events (full history)', G)], size=7.4),
]
def topic_view(hi_group=None, extra=''):
    o = t(180, 14, 'Topic order-events (3 partitions)', 9, bold=True)
    o += pcol(70, 30, 'P0', ['o102', 'o102'], 'blue') + pcol(70, 56, 'P1', ['o103'], 'blue') + pcol(70, 82, 'P2', ['o101', 'o101', 'o101'], 'blue')
    return o + extra
B1 = [
    topic_view(extra=opbox(250, 40, 'Producer', 'order app', 'acc', 90, 34) + arrow(250, 57, 186, 57, 'acc', 1.2) + cap('Same key → same partition.', '', 'blue', y=144, h=30)),
    topic_view(extra=opbox(250, 40, 'kitchen', 'bookmark: end', 'green', 90, 34) + arrow(186, 57, 250, 57, 'green', 1.2) + cap('A group pulls and moves its bookmark.', '', 'green', y=144, h=30)),
    topic_view(extra=opbox(250, 20, 'kitchen', 'done', 'green', 90, 30) + opbox(250, 64, 'billing', 'bookmark: end', 'green', 90, 30) + arrow(186, 79, 250, 79, 'green', 1.2) + cap('Each group has its own bookmark.', '', 'green', y=144, h=30)),
    topic_view(extra=t(260, 60, 'still 6 events', 9, 'acc', bold=True) + t(260, 76, 'reading ≠ deleting', 8, 'ink2') + cap('Kept until retention (7 days).', '', 'amber', y=144, h=30)),
    topic_view(extra=opbox(250, 40, 'analytics', 'from offset 0', 'violet', 90, 34) + arrow(186, 57, 250, 57, 'violet', 1.2) + cap('New readers can replay.', '', 'blue', y=144, h=30)),
]
two = anim_two('Kafka: one stream, many readers', 'Write once, read many', 'Real outputs from the lab', 'What happens inside the topic', see, B1,
               ['Produce.', 'Kitchen reads.', 'Billing reads.', 'Still stored.', 'Replay.'],
               ['Keys pick partitions.', 'Bookmark moves.', 'Separate bookmarks.', 'Retention, not reads.', 'History available.'])

def five(kind, title, sub, cons, lines, caps, hid):
    fr = [t(180, 22, a, 9.4, 'acc' if i == 4 else 'ink', bold=True) + t(180, 56, b, 8.4, 'ink2') + cap(c, '', tone, y=150, h=34) for i, (a, b, c, tone) in enumerate(lines)]
    return anim_one(kind, title, sub, cons[0], cons[1], fr, caps, hid=hid)
s1 = five('Real-time scenario 1', 'The slow SMS provider', 'Decoupling during a sale. (Typical.)',
          ('Decoupling', 'A slow consumer only delays itself; producers and other consumers keep going'), [
    ('SMS provider slows to 5 s', 'during the Diwali sale', 'Before: orders froze.', 'red'),
    ('Orders go to Kafka', 'order app does not wait for SMS', 'Write takes milliseconds.', 'green'),
    ('Kitchen and billing on time', 'their own groups', 'Unaffected.', 'green'),
    ('SMS group lags behind', 'lag grows, then shrinks', 'Catches up later.', 'amber'),
    ('No order lost', 'events wait in Kafka', 'Retention 7 days.', 'blue')],
    ['Slow.', 'Write.', 'Others fine.', 'Lag.', 'Safe.'], 'scenario-decouple')
s2 = five('Real-time scenario 2', 'A bug in billing', 'Replay to fix wrong data. (Typical.)',
          ('Replay', 'Fix the consumer code and re-read events from an older offset'), [
    ('Billing applied wrong GST', 'for 2 hours', 'Invoices wrong.', 'red'),
    ('Fix the code', 'deploy billing v2', 'Events still in Kafka.', 'green'),
    ('Reset billing’s offsets', 'to 2 hours ago (Lesson 3.3)', 'Only billing group.', 'green'),
    ('Re-read and re-bill', 'other groups untouched', 'Kitchen unaware.', 'green'),
    ('Invoices corrected', 'no data from the app needed', 'History saved us.', 'blue')],
    ['Bug.', 'Fix.', 'Reset.', 'Re-read.', 'Fixed.'], 'scenario-replay')
s3 = five('Real-time scenario 3 · advanced', 'Adding a fraud-check service', 'A new consumer without touching producers. (Typical.)',
          ('New consumers', 'Add services by subscribing a new group; producers do not change'), [
    ('Fraud team wants orders', 'real time', 'Old way: change order app.', 'blue'),
    ('New group fraud-check', 'subscribe to order-events', 'Zero producer changes.', 'green'),
    ('Backfill from history', 'auto.offset.reset=earliest', 'Last 7 days.', 'green'),
    ('Then live', 'reads new events as they come', 'Seconds behind.', 'green'),
    ('Plug-in architecture', 'teams move independently', 'Why companies use Kafka.', 'blue')],
    ['Request.', 'Subscribe.', 'Backfill.', 'Live.', 'Pattern.'], 'scenario-newservice')
animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Write once, read many</h2>
  <p>Left: the real lab output. Right: what happens inside the topic.</p>
''' + two + '''
  <p>Now peel the same event layer by layer, from your Python call down to the broker’s disk.</p>
''' + PEEL + '''
  <p>Three live scenarios follow: a slow service, a replay to fix a bug, and a new service joining.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

def uc_(word, sub, tone, title, desc, flow_):
    return usecase(f'<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-{tone}" style="stroke:var(--{tone if tone != "acc" else "track"})"/>' + t(60, 42, word, 11, tone, bold=True) + t(60, 58, sub, 7.4, 'ink2'), title, desc, flow_)
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Where Kafka is used</h2>
''' + '\n'.join([
    uc_('ride', 'trips', 'blue', '1. Ride-hailing and food delivery', 'Trip and order events feed pricing, ETA, driver apps and fraud checks at the same time.', ['App events', '*Kafka', 'Many services']),
    uc_('UPI', 'payments', 'green', '2. Payments', 'Payment events flow to ledgers, notifications and fraud models; replay helps reconciliation.', ['Payment', '*Kafka', 'Ledger, SMS, fraud']),
    uc_('shop', 'clicks', 'violet', '3. E-commerce activity', 'Clicks and searches stream into recommendation and analytics systems.', ['Clicks', '*Kafka', 'Recommendations']),
    uc_('logs', 'metrics', 'acc', '4. Logs and monitoring', 'Thousands of servers send logs to Kafka, then to search and alerting tools.', ['Servers', '*Kafka', 'Search, alerts']),
    uc_('bank', 'CDC', 'blue', '5. Database change streams', 'Every change in a core database is captured and copied to a data lake (Module 7).', ['Database', '*Kafka', 'Data lake']),
]) + '''
  <p class="muted">Examples are simplified descriptions of common patterns, not any one company’s internal system.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> basic Python and the idea of a client and a server are enough. Helpful but optional: <a href="../../../hadoop/">Hadoop</a> for the “distributed” idea and the Spark course’s streaming module.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
