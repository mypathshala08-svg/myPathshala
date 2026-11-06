import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
BODY = body(HERE)

META = dict(
    module='01-introduction', lesson='02-messaging-models-queue-vs-pub-sub', n='1.2',
    module_label='Module 1 · Start here: why Kafka?',
    title='Messaging models: queue vs pub-sub',
    desc='Point-to-point queues vs publish-subscribe, and how Kafka does both with consumer groups. Real Kafka 4.4 lab: three riders in one group share 12 orders (4 + 2 + 6), two groups each receive all 12, and a fourth consumer sits idle with no partition; plus where Kafka 4.x share groups fit.',
    og_desc='Queue or pub-sub? In Kafka the consumer group decides. Real lab: shared work, fan-out and an idle fourth consumer.',
    minutes=20, level='Beginner',
    lead='Should each order go to <b>one</b> worker or to <b>every</b> service? Kafka answers both with one idea, the <b>consumer group</b>. We prove queue style, pub-sub style and the partition limit on a real <b>Kafka 4.4</b> cluster. <b>All outputs are real.</b>',
    chips=['Queue vs pub-sub', 'Consumer groups', 'Idle consumer proof', 'Runs in your browser (Python)'],
)

MAIN = '''# Assign partitions to consumers of one group (round-robin), then fan out to groups
partitions = {0: ["o4", "o5", "o7", "o9"], 1: ["o1", "o10"], 2: ["o2", "o3", "o6", "o8", "o11", "o12"]}

def assign(consumers):
    owned = {c: [] for c in consumers}
    for p in partitions:
        owned[consumers[p % len(consumers)]].append(p)
    return owned

def orders(parts):
    return [o for p in parts for o in partitions[p]]

group = assign(["rider-A", "rider-B", "rider-C", "rider-D"])
for c, parts in group.items():
    print(c, parts, len(orders(parts)), "orders")

for g in ["sms", "analytics"]:          # each group reads everything
    print(g, "gets", len(orders(partitions)), "orders")
'''
RUN = dict(
    heading='Run the code: assignment and fan-out',
    intro='<p>The rule behind the lab in a few lines. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('        owned[consumers[p % len(consumers)]].append(p)', 'Inside a group, each partition goes to exactly one consumer.'),
        ('for g in ["sms", "analytics"]:          # each group reads everything', 'Different groups each read all partitions.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then remove rider-D and run again.', code=None),
        dict(label='2 · Predict first: idle', hint='<b>Predict first:</b> 6 consumers, 4 partitions: how many idle?',
             code='''print(max(0, 6 - 4))
'''),
        dict(label='3 · Max speed-up', hint='Parallelism is min(consumers, partitions).',
             code='''for c in (2, 3, 5, 10):
    print(c, "consumers ->", min(c, 3), "busy")
'''),
        dict(label='4 · Fan-out copies', hint='Events read in total by 3 groups.',
             code='''print(12 * 3, "reads, still 12 stored")
'''),
        dict(label='5 · Spot the error', hint='Same partition to two consumers in one group.', expect='error',
             code='''owner = {0: "rider-A"}
assert owner.get(0) in (None, "rider-B"), "partition 0 already owned by rider-A in this group"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: see the assignment',
    intro='<p>Start two console consumers in one group in two terminals, then describe the group. <b>Outputs are real</b> (Kafka 4.4.0).</p>',
    items=[
        dict(title='1 · Two members', cmd='kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic deliveries --group riders', file='terminal (×2)',
             output='(each terminal prints only its partitions’ orders)', note='Same --group.'),
        dict(title='2 · Who owns what', cmd='kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group riders', file='terminal',
             output='GROUP   TOPIC       PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG  CONSUMER-ID …', note='One consumer per partition.'),
        dict(title='3 · Another group', cmd='kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic deliveries --group sms --from-beginning', file='terminal',
             output='all 12 orders', note='Pub-sub.'),
    ],
)

TRACE = dict(
    heading='Round-robin assignment',
    intro='<p>Four consumers, three partitions.</p>',
    code='''consumers = ["r1", "r2", "r3", "r4"]
owned = {c: [] for c in consumers}
for p in range(3):
    owned[consumers[p % 4]].append(p)
print(owned)
''',
    notes={4: 'Assign :: Partition p goes to consumer p mod 4.', 5: 'Idle :: r4 owns nothing.'},
)

WORKED_INTRO = 'Three messaging decisions at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='Kafka · groups', title='SMS pods sending twice',
         problem='<p>Each SMS pod used its hostname as group.id.</p>',
         inp='2 pods',
         approach=['Same service → same group.id.', 'Pods then share partitions.', 'Each event sent once.'],
         code='''pods = ["sms-7f9", "sms-2c1"]
print("bad :", {p: "group " + p for p in pods})
print("good:", {p: "group sms" for p in pods})
''', notes={1: 'Rule :: group.id names the service, not the machine.'},
         tryit='Scenario 1.'),
    dict(level='i', tag='Kafka · sizing', title='How many partitions for riders?',
         problem='<p>Peak needs 12 parallel rider workers.</p>',
         inp='12 workers',
         approach=['Partitions ≥ peak consumers.', 'Leave headroom.', 'Changing later moves keys.'],
         code='''peak, headroom = 12, 1.5
print("partitions:", int(peak * headroom))
''', notes={1: 'Headroom :: Adding partitions later remaps keys.'},
         tryit='Step 3.'),
    dict(level='a', tag='Kafka · choice', title='Group or share group?',
         problem='<p>Independent 30-second jobs on a 1-partition topic.</p>',
         inp='job traits',
         approach=['Need ordering? classic group.', 'Independent slow jobs? share group.', 'Need per-record retry? share group.'],
         code='''needs_order, slow, independent = False, True, True
print("share group" if (slow and independent and not needs_order) else "consumer group")
''', notes={1: 'Choose :: By ordering and job shape.'},
         tryit='Lesson 6.1.'),
]

QUIZ = mix([
    dict(q='Beginner: In a queue, each message is processed by…', options=['Every consumer', 'Exactly one consumer', 'No one', 'The producer'], answer=1,
         why='Work is shared.'),
    dict(q='Beginner: In pub-sub, each message goes to…', options=['One subscriber', 'Every subscriber', 'The first one only', 'A database'], answer=1,
         why='Fan-out.'),
    dict(q='Beginner: What makes Kafka consumers share work?', options=['Same topic name', 'Same group.id', 'Same host', 'Same port'], answer=1,
         why='One group.'),
    dict(q='Intermediate: 4 consumers in one group, 3 partitions. Busy consumers?', options=['4', '3', '1', '12'], answer=1,
         why='r4 got 0 orders.'),
    dict(q='Intermediate: sms and analytics groups each received…', options=['6', '12', '4', '0'], answer=1,
         why='All records.'),
    dict(q='Intermediate: rider-C got 6 orders, rider-B 2, because…', options=['Random bug', 'Keys decide partitions; data is uneven', 'C is faster', 'Replication'], answer=1,
         why='Key distribution.'),
    dict(q='Advanced: Share groups (Kafka 4.x) allow…', options=['More consumers than partitions on the same partition', 'Global ordering', 'No acks', 'ZooKeeper'], answer=0,
         why='Queue semantics with per-record acks.'),
    dict(q='Advanced: Why can an idle consumer still be useful?', options=['It is not', 'It takes over on rebalance if another fails', 'It compresses data', 'It replicates'], answer=1,
         why='Standby.'),
])

REVISION = [
    'Queue: each message to one consumer. Pub-sub: each message to all subscribers.',
    'Kafka: same group.id = share partitions; different groups = full copies.',
    'Lab: riders 4 + 2 + 6 = 12 once; sms 12, analytics 12; r4 idle with 0.',
    'Parallelism in a group ≤ partitions.',
    'Share groups (4.x): many consumers per partition, per-record ack.',
]
FAQ = [
    ('Does each group store a copy of the data?', 'No. There is one copy of each partition (plus replicas). Groups only store their offsets in the __consumer_offsets topic.'),
    ('Can one consumer belong to several groups?', 'A consumer instance has one group.id. A service that needs two views runs two consumers.'),
    ('Why not one partition per consumer always?', 'Partitions also cost broker resources and affect ordering; choose based on peak parallelism and throughput (Lesson 10.2).'),
    ('Are share groups production-ready?', 'They are enabled in our Kafka 4.4 cluster (share.version 2). Check the release notes of your version and managed service before relying on them; Lesson 6.1 covers them in depth.'),
]

PRACTICE_INTRO = 'Programs about groups and assignment.'
PROBLEMS = [
    dict(level='easy', title='Busy consumers', stmt='min(consumers, partitions).', inp='5, 3',
         code='''print(min(5, 3))
''', explain='3 busy, 2 idle.'),
    dict(level='easy', title='Total reads', stmt='Records × groups.', inp='12, 3',
         code='''print(12 * 3)
''', explain='Each group reads all.'),
    dict(level='easy', title='Same group?', stmt='Do two pods share work?', inp='group ids',
         code='''print("sms" == "sms")
''', explain='Same id → share.'),
    dict(level='medium', title='Round-robin', stmt='Assign 5 partitions to 2 consumers.', inp='5, 2',
         code='''print({c: [p for p in range(5) if p % 2 == c] for c in range(2)})
''', explain='3 and 2.'),
    dict(level='medium', title='Load per consumer', stmt='Orders per consumer from partition sizes.', inp='[4, 2, 6]',
         code='''sizes = [4, 2, 6]
print({f"c{i}": s for i, s in enumerate(sizes)})
''', explain='Uneven keys → uneven load.'),
    dict(level='medium', title='Rebalance', stmt='r1 leaves; give its partition to r4.', inp='owners',
         code='''own = {"r1": [0], "r2": [1], "r3": [2], "r4": []}
own["r4"] += own.pop("r1")
print(own)
''', explain='Standby takes over.'),
    dict(level='business', title='Peak partitions', stmt='Peak 12 workers with 50% headroom.', inp='12',
         code='''print(int(12 * 1.5))
''', explain='18 partitions.'),
    dict(level='business', title='Duplicate SMS cost', stmt='Extra SMS at ₹0.20 for 100,000 orders.', inp='numbers',
         code='''print("₹", 100000 * 0.20)
''', explain='Wrong group.id costs money.'),
]

SCN_INTRO = 'Questions about queues, pub-sub and groups.'
SCENARIOS = (
    scn('Any company · backend', 'Fresher', '“Queue vs pub-sub?”',
        'Explain both and Kafka’s approach.',
        'answer?',
        '<p>A queue delivers each message to one of several competing consumers; pub-sub delivers each message to all subscribers. Kafka uses consumer groups: members of one group split the partitions (queue), and each group gets all messages (pub-sub).</p>', 'Mixing up group and topic.') +
    scn('E-commerce', 'Fresher', 'Duplicate processing',
        'Every order email is sent twice after scaling to 2 pods.',
        'cause?',
        '''<ul>
          <li>Pods use different group.ids.</li>
          <li>Use one group.id per service.</li>
        </ul>''', 'Adding a dedup table first.') +
    scn('Data engineering', 'Mid-level', 'Scaling limit',
        'Adding consumers does not reduce lag.',
        'diagnose?',
        '''<ul>
          <li>Consumers ≥ partitions: extras idle.</li>
          <li>Increase partitions (keys remap) or speed up processing.</li>
          <li>Check for a hot partition.</li>
        </ul>''', '“Add more consumers.”') +
    scn('Platform', 'Senior', 'Queue semantics',
        'A team wants a job queue with per-message retry on Kafka.',
        'options?',
        '''<ul>
          <li>Kafka 4.x share groups with acks and delivery count.</li>
          <li>Or classic group + retry topic + DLQ (Lesson 6.2).</li>
          <li>Or a dedicated queue system if volume is low.</li>
        </ul>''', '“Kafka cannot do queues.”')
)
