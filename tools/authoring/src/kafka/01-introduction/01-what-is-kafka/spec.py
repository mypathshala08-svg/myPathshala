import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
BODY = body(HERE)

META = dict(
    module='01-introduction', lesson='01-what-is-kafka', n='1.1',
    module_label='Module 1 · Start here: why Kafka?',
    title='What is Kafka?',
    desc='What Apache Kafka is and why companies use it, shown on a real Kafka 4.4 cluster: one stream of TiffinGo order events read by kitchen, billing and analytics consumer groups independently, events that stay after reading, replay from history, and a real record batch dissected (offset, key, value, timestamp, producer id).',
    og_desc='Kafka explained with a real 3-broker Kafka 4.4 lab: write once, read many, replay, and a dissected record.',
    minutes=22, level='Beginner',
    lead='Kafka is the “notice board” in the middle of modern apps: write each event <b>once</b>, let <b>any number</b> of services read it at their own pace, and <b>replay</b> history when needed. We prove it on a real <b>Kafka 4.4</b> cluster and dissect what Kafka actually stores. <b>All outputs are real.</b>',
    chips=['Kafka 4.4.0 (KRaft)', 'Real record dissected', 'Write once, read many', 'Runs in your browser (Python)'],
)

MAIN = '''# A tiny model of a Kafka topic: an append-only list + one bookmark per group
log = []                       # the partition: events are only appended
bookmarks = {}                 # group.id -> next offset to read

def produce(event):
    log.append(event)
    return len(log) - 1        # the offset Kafka returns

def poll(group):
    pos = bookmarks.get(group, 0)          # new group starts at the earliest event
    batch = log[pos:]
    bookmarks[group] = len(log)            # commit the new position
    return batch

for e in ["o101 PLACED", "o102 PLACED", "o101 PAID"]:
    print("offset", produce(e), "<-", e)

print("kitchen  :", poll("kitchen"))
print("billing  :", poll("billing"))
produce("o101 DELIVERED")
print("kitchen  :", poll("kitchen"))       # only the new event
print("analytics:", poll("analytics"))     # full history
print("still stored:", len(log), "events")
'''
RUN = dict(
    heading='Run the code: a topic in miniature',
    intro='<p>Kafka’s core idea in 20 lines of Python. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    pos = bookmarks.get(group, 0)          # new group starts at the earliest event', 'Each consumer group has its own bookmark (committed offset).'),
        ('print("still stored:", len(log), "events")', 'Reading never removes events; only retention does.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then add a group called "sms".', code=None),
        dict(label='2 · Predict first: offsets', hint='<b>Predict first:</b> what offset does the 5th event get?',
             code='''log = ["a", "b", "c", "d"]
log.append("e")
print(len(log) - 1)
'''),
        dict(label='3 · Retention', hint='Delete events older than the first 2 (like retention).',
             code='''log = ["e0", "e1", "e2", "e3"]
start = 2
print("kept:", log[start:], "log start offset:", start)
'''),
        dict(label='4 · Lag', hint='How far behind is a group?',
             code='''end_offset, committed = 6, 2
print("lag =", end_offset - committed)
'''),
        dict(label='5 · Spot the error', hint='A queue that deletes on read.', expect='error',
             code='''queue = ["o101"]
queue.pop(0)
print("billing gets:", queue[0])
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: your first events',
    intro='<p>Start Kafka with Docker (full setup in Lesson 1.5), then use the CLI tools inside the container. <b>Outputs are real</b> (Kafka 4.4.0).</p>',
    items=[
        dict(title='1 · Start Kafka', cmd='docker run -d --name kafka -p 9092:9092 apache/kafka:4.4.0', file='terminal',
             output='ee1ecc07ed0f…', note='A single KRaft node.'),
        dict(title='2 · Write events', cmd='docker exec -it kafka /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic menu-updates', file='terminal',
             output='>Paneer Tikka price 220\n>Dosa back in stock', note='Type lines, Ctrl+C to stop.'),
        dict(title='3 · Read them', cmd='docker exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic menu-updates --from-beginning', file='terminal',
             output='Paneer Tikka price 220\nDosa back in stock', note='Run it twice: the events are still there.'),
    ],
)

TRACE = dict(
    heading='Two groups, one log',
    intro='<p>Watch the two bookmarks move independently.</p>',
    code='''log = ["o101 PLACED", "o102 PLACED"]
kitchen = 0
billing = 0
kitchen = len(log)
log.append("o101 PAID")
billing = len(log)
print(kitchen, billing, len(log))
''',
    notes={4: 'Kitchen :: Reads 2 events, bookmark = 2.', 6: 'Billing :: Reads all 3, bookmark = 3.'},
)

WORKED_INTRO = 'Three design decisions TiffinGo makes with Kafka.'
EXAMPLES = [
    dict(level='b', tag='Kafka · decoupling', title='Stop the chain of calls',
         problem='<p>The order app calls 4 services one by one.</p>',
         inp='4 downstream services',
         approach=['Order app writes one event per change.', 'Each service is a consumer group.', 'Slow services only delay themselves.'],
         code='''services = ["kitchen", "billing", "sms", "analytics"]
print("order app writes 1 event; groups:", services)
''', notes={1: 'Decouple :: Producer does not know the consumers.'},
         tryit='Step 1.'),
    dict(level='i', tag='Kafka · keys', title='Keep each order’s events in order',
         problem='<p>PAID must never be processed before PLACED.</p>',
         inp='events for o101',
         approach=['Use order_id as the key.', 'Same key → same partition.', 'A partition is read in order.'],
         code='''events = [("o101", "PLACED"), ("o101", "PAID"), ("o101", "DELIVERED")]
print([s for k, s in events if k == "o101"])
''', notes={1: 'Order :: Guaranteed per partition (Lesson 1.4).'},
         tryit='Step 1 output: offsets 0, 1, 2.'),
    dict(level='a', tag='Kafka · retention', title='How long to keep events?',
         problem='<p>Analytics may need to replay a week; finance asks for 30 days.</p>',
         inp='events/day, size',
         approach=['Default 7 days.', 'Set retention per topic.', 'Size disks: events/day × size × days × replicas.'],
         code='''per_day, size_kb, days, rf = 2_000_000, 1, 30, 3
print(round(per_day * size_kb * days * rf / 1024 / 1024, 1), "GB")
''', notes={1: 'Capacity :: Replicas multiply disk use.'},
         tryit='Lesson 4.3.'),
]

QUIZ = mix([
    dict(q='Beginner: Kafka is best described as…', options=['A relational database', 'A distributed event-streaming platform (commit log)', 'A web server', 'A cache'], answer=1,
         why='Topics of append-only partitions on brokers.'),
    dict(q='Beginner: After a consumer reads an event, Kafka…', options=['Deletes it', 'Keeps it until retention', 'Moves it to another topic', 'Locks it'], answer=1,
         why='2 + 1 + 3 = 6 events still stored.'),
    dict(q='Beginner: Two services both need every order. Use…', options=['One consumer group', 'Two consumer groups', 'Two topics with copies', 'A database trigger'], answer=1,
         why='Each group has its own offsets.'),
    dict(q='Intermediate: Why did all o101 events go to partition 2?', options=['Random', 'Same key → same partition', 'Partition 2 is the leader', 'Alphabetical'], answer=1,
         why='Keyed records keep order.'),
    dict(q='Intermediate: A new group with auto.offset.reset=earliest starts…', options=['At the newest event', 'At the oldest retained event', 'At offset 100', 'Nowhere'], answer=1,
         why='Analytics got the full history.'),
    dict(q='Intermediate: Kafka guarantees order…', options=['Across the whole topic', 'Within one partition', 'Never', 'Only for strings'], answer=1,
         why='Ordering is per partition.'),
    dict(q='Advanced: In the dumped batch, producerId and sequence are used for…', options=['Compression', 'Dropping duplicate retries (idempotence)', 'Choosing partitions', 'Security'], answer=1,
         why='Lesson 2.5.'),
    dict(q='Advanced: Since Kafka 4.0, cluster metadata is managed by…', options=['ZooKeeper', 'KRaft (Raft quorum of controllers)', 'Hive Metastore', 'etcd'], answer=1,
         why='ZooKeeper was removed in 4.0.'),
])

REVISION = [
    'Kafka = distributed, partitioned, replicated commit log for event streams.',
    'Producer writes once; many consumer groups read independently.',
    'Reading does not delete; retention (default 7 days) does.',
    'Topic → partitions → offsets; same key → same partition → ordered.',
    'Lab: 6 events, kitchen 6, billing 6, still stored 6, analytics replay 6.',
    'Record = offset, timestamp, key, value, headers; producerId + sequence for idempotence.',
    'Kafka 4.4.0 (Oct 2026), KRaft only.',
]
FAQ = [
    ('Is Kafka a message queue?', 'It can act like one (one consumer group sharing work, Lesson 1.2), but it is a log: messages stay after reading and many groups can read them. Kafka 4.x also adds share groups for true queue semantics (Lesson 6.1).'),
    ('Why is Kafka so fast?', 'Sequential disk writes, batching, compression, the OS page cache and zero-copy transfer to consumers (Module 4).'),
    ('Do I need Java to use Kafka?', 'Brokers run on Java, but clients exist for Python, Go, Node.js and others. This course uses Python clients.'),
    ('Is Kafka free?', 'Apache Kafka is open source (Apache 2.0). Managed services such as Confluent Cloud, Amazon MSK or Aiven charge for hosting (Lesson 11.1).'),
    ('What does “event streaming” mean?', 'Capturing events as they happen, storing them durably, and processing them continuously rather than in nightly batches.'),
]

PRACTICE_INTRO = 'Programs that model Kafka’s core ideas.'
PROBLEMS = [
    dict(level='easy', title='Append and offset', stmt='Return the offset of each new event.', inp='3 events',
         code='''log = []
for e in ["a", "b", "c"]:
    log.append(e); print(e, "->", len(log) - 1)
''', explain='Offsets start at 0.'),
    dict(level='easy', title='Two groups', stmt='Both groups read all events.', inp='log of 3',
         code='''log = ["a", "b", "c"]
print({"kitchen": log[0:], "billing": log[0:]})
''', explain='Independent bookmarks.'),
    dict(level='easy', title='Lag', stmt='Lag = end offset − committed offset.', inp='10, 7',
         code='''print(10 - 7)
''', explain='3 events behind.'),
    dict(level='medium', title='Group by key', stmt='Keep events of each order together.', inp='events',
         code='''ev = [("o1", "PLACED"), ("o2", "PLACED"), ("o1", "PAID")]
by = {}
for k, s in ev: by.setdefault(k, []).append(s)
print(by)
''', explain='Like a partition per key.'),
    dict(level='medium', title='Replay from offset', stmt='Read from offset 2.', inp='log',
         code='''log = ["e0", "e1", "e2", "e3"]
print(log[2:])
''', explain='Seek to an offset.'),
    dict(level='medium', title='Retention', stmt='Keep only events newer than 7 days.', inp='ages',
         code='''ages = [1, 3, 8, 10]
print([a for a in ages if a <= 7])
''', explain='Old events are deleted by age.'),
    dict(level='business', title='Disk size', stmt='2M events/day, 1 KB, 7 days, 3 replicas.', inp='numbers',
         code='''print(round(2_000_000 * 7 * 3 / 1024 / 1024, 1), "GB")
''', explain='About 40 GB.'),
    dict(level='business', title='Fan-out', stmt='Direct calls vs Kafka for 5 producers and 6 consumers.', inp='5, 6',
         code='''print("direct links:", 5 * 6, " with Kafka:", 5 + 6)
''', explain='Kafka reduces wiring.'),
]

SCN_INTRO = 'First-round Kafka questions.'
SCENARIOS = (
    scn('Any company · backend', 'Fresher', '“What is Kafka and why use it?”',
        'Explain in one minute.',
        'answer?',
        '<p>Kafka is a distributed event-streaming platform: producers append events to topics split into partitions on brokers, and consumer groups read them independently using offsets. Events are kept for a retention period, so many services can read and replay them. It decouples services and handles very high throughput.</p>', '“It is a database.”') +
    scn('Food delivery', 'Fresher', 'Slow service',
        'The SMS service is slow and blocks orders.',
        'fix?',
        '''<ul>
          <li>Publish order events to Kafka.</li>
          <li>SMS becomes a consumer group.</li>
          <li>Slow SMS only increases its own lag.</li>
        </ul>''', 'Adding retries in the order app.') +
    scn('Data engineering', 'Mid-level', 'Queue or Kafka?',
        'When would you not use Kafka?',
        'judgement?',
        '''<ul>
          <li>Few messages per day or simple task queues: a simple queue may do.</li>
          <li>Need to query current state: use a database.</li>
          <li>Kafka when volume is high, many readers, or replay is needed.</li>
        </ul>''', '“Kafka for everything.”') +
    scn('Platform', 'Senior', 'Ordering',
        'Payments for one account must be processed in order.',
        'design?',
        '''<ul>
          <li>Key = account_id so one account maps to one partition.</li>
          <li>One consumer per partition in the group processes sequentially.</li>
          <li>Idempotent producer to avoid duplicates.</li>
        </ul>''', '“Kafka orders the whole topic.”')
)
