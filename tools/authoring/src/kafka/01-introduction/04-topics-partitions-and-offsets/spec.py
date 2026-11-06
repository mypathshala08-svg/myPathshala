import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
BODY = body(HERE)

META = dict(
    module='01-introduction', lesson='04-topics-partitions-and-offsets', n='1.4',
    module_label='Module 1 · Start here: why Kafka?',
    title='Topics, partitions and offsets',
    desc='How Kafka splits a topic into partitions, numbers records with offsets and picks a partition from the key. Real Kafka 4.4 lab: keyed city orders (one partition left empty), murmur2 computed by hand to match the broker, seeking to an offset, adding partitions moves Mumbai from partition 1 to 4, and partitions can never be reduced.',
    og_desc='Keys, murmur2, offsets and the partition-count trap, proven on a real Kafka 4.4 cluster.',
    minutes=26, level='Beginner',
    lead='Where does an event go, and how do you find it again? We compute Kafka’s <b>partition hash by hand</b>, match it to a real <b>Kafka 4.4</b> broker, read from an exact <b>offset</b>, and watch a key <b>move</b> when partitions are added. <b>All outputs are real.</b>',
    chips=['murmur2 by hand', 'Seek to an offset', 'Partition remap proof', 'Runs in your browser (Python)'],
)

MAIN = '''# Kafka's default (Java) partitioner, in pure Python
def murmur2(data):
    m, h = 0x5bd1e995, (0x9747b28c ^ len(data)) & 0xffffffff
    n = len(data) // 4
    for i in range(n):
        k = int.from_bytes(data[4*i:4*i+4], "little")
        k = (k * m) & 0xffffffff; k ^= k >> 24; k = (k * m) & 0xffffffff
        h = ((h * m) & 0xffffffff) ^ k
    rest = data[4*n:]
    if len(rest) == 3: h ^= rest[2] << 16
    if len(rest) >= 2: h ^= rest[1] << 8
    if len(rest) >= 1: h = ((h ^ rest[0]) * m) & 0xffffffff
    h ^= h >> 13; h = (h * m) & 0xffffffff; h ^= h >> 15
    return h

def partition(key, n):
    return (murmur2(key.encode()) & 0x7fffffff) % n

for city in ["Mumbai", "Pune", "Delhi", "Chennai"]:
    print(city, "-> 3 partitions:", partition(city, 3), "| 6 partitions:", partition(city, 6))
'''
RUN = dict(
    heading='Run the code: the partitioner',
    intro='<p>The same function our lab matched against the real broker. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    return (murmur2(key.encode()) & 0x7fffffff) % n', 'Positive hash modulo the partition count.'),
        ('    print(city, "-> 3 partitions:", partition(city, 3), "| 6 partitions:", partition(city, 6))', 'Change n and keys can move.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then add "Kolkata" and "Bengaluru".', code=None),
        dict(label='2 · Predict first: offsets', hint='<b>Predict first:</b> partition 0 has 6 events; the next offset?',
             code='''events_in_p0 = 6
print("next offset:", events_in_p0)
'''),
        dict(label='3 · Spread', hint='Count orders per partition with many keys.',
             code='''from collections import Counter
print(Counter(hash("o%d" % i) % 3 for i in range(3000)))
'''),
        dict(label='4 · Seek', hint='Read partition 1 from offset 2.',
             code='''p1 = ["o1", "o4", "o7", "o10"]
print(p1[2:])
'''),
        dict(label='5 · Spot the error', hint='Reducing partitions.', expect='error',
             code='''current, wanted = 6, 2
assert wanted >= current, f"InvalidPartitions: topic has {current} partitions; {wanted} would not be an increase"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: partitions and offsets',
    intro='<p>CLI tools from Lesson 1.5. <b>Outputs are real</b> (Kafka 4.4.0).</p>',
    items=[
        dict(title='1 · End offsets', cmd='kafka-get-offsets.sh --bootstrap-server localhost:9092 --topic city-orders', file='terminal',
             output='city-orders:0:6\ncity-orders:1:4\ncity-orders:2:0', note='Next offset per partition.'),
        dict(title='2 · Seek', cmd='kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic city-orders --partition 1 --offset 2 --formatter-property print.offset=true', file='terminal',
             output='Offset:2\to7\nOffset:3\to10', note='Exact slice.'),
        dict(title='3 · Grow', cmd='kafka-topics.sh --bootstrap-server localhost:9092 --alter --topic city-orders --partitions 6', file='terminal',
             output='(no output; describe shows PartitionCount: 6)', note='Keys may move.'),
    ],
)

TRACE = dict(
    heading='Offsets per partition',
    intro='<p>Each partition counts on its own.</p>',
    code='''next_off = {0: 0, 1: 0}
orders = [("Mumbai", 1), ("Pune", 0), ("Mumbai", 1)]
for city, p in orders:
    print(city, "-> P%d offset %d" % (p, next_off[p]))
    next_off[p] += 1
print(next_off)
''',
    notes={4: 'Assign :: Offset = current next offset.', 6: 'Independent :: P0 and P1 counters differ.'},
)

WORKED_INTRO = 'Three partitioning decisions at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='Kafka · keys', title='Pick a key for order events',
         problem='<p>Status updates of an order must stay in order.</p>',
         inp='order events',
         approach=['Key = order_id.', 'Millions of keys spread evenly.', 'Each order’s events stay in one partition.'],
         code='''from collections import Counter
print(Counter(abs(hash("o%d" % i)) % 6 for i in range(6000)))
''', notes={1: 'Spread :: High cardinality keys.'},
         tryit='Scenario 1.'),
    dict(level='i', tag='Kafka · replay', title='Re-read one partition',
         problem='<p>A consumer bug affected partition 1 from offset 2.</p>',
         inp='partition, offset',
         approach=['Seek to (P1, 2).', 'Process to end.', 'Then resume normally.'],
         code='''p1 = ["o1", "o4", "o7", "o10"]
for off in range(2, len(p1)):
    print(off, p1[off])
''', notes={1: 'Seek :: Offsets make replay precise.'},
         tryit='Step 4.'),
    dict(level='a', tag='Kafka · sizing', title='Choose a partition count once',
         problem='<p>Peak: 30 MB/s; one consumer handles 5 MB/s.</p>',
         inp='throughput',
         approach=['Partitions ≥ peak / per-consumer.', 'Add headroom.', 'Avoid changing later.'],
         code='''import math
print(math.ceil(30 / 5 * 2), "partitions (2x headroom)")
''', notes={1: 'Rule of thumb :: Lesson 10.2 refines it.'},
         tryit='Step 5.'),
]

QUIZ = mix([
    dict(q='Beginner: An offset identifies a record within…', options=['The cluster', 'A partition', 'A topic', 'A consumer'], answer=1,
         why='Offsets are per partition.'),
    dict(q='Beginner: Kafka guarantees order…', options=['Across a topic', 'Within a partition', 'Across clusters', 'Never'], answer=1,
         why='Mumbai offsets 0–3 in order.'),
    dict(q='Beginner: Same key with unchanged partition count goes to…', options=['A random partition', 'The same partition', 'Partition 0', 'All partitions'], answer=1,
         why='Hash is deterministic.'),
    dict(q='Intermediate: Why was partition 2 empty?', options=['Broker down', 'Only 4 keys hashed to 0 and 1', 'Retention', 'Bug'], answer=1,
         why='Few keys → uneven.'),
    dict(q='Intermediate: city-orders:0:6 means…', options=['6 partitions', 'Next offset of partition 0 is 6', 'Offset 0 has 6 bytes', 'Lag 6'], answer=1,
         why='Log end offset.'),
    dict(q='Intermediate: After 3 → 6 partitions, Mumbai went to…', options=['1', '4', '0', '2'], answer=1,
         why='murmur2 % 6 = 4.'),
    dict(q='Advanced: Python (librdkafka) and Java producers can put the same key in different partitions because…', options=['Different default partitioners', 'Different brokers', 'Compression', 'They cannot'], answer=0,
         why='Set murmur2_random.'),
    dict(q='Advanced: To reduce partitions you must…', options=['--alter --partitions 2', 'Create a new topic and migrate', 'Delete offsets', 'Restart'], answer=1,
         why='Partitions only grow.'),
])

REVISION = [
    'Topic → partitions (ordered, append-only) → offsets (per partition, from 0).',
    'Keyed: toPositive(murmur2(key)) % n (Java); same key → same partition.',
    'Lab: Mumbai → P1 (o1,o4,o7,o10), others → P0, P2 empty.',
    'Seek: --partition 1 --offset 2 → o7, o10.',
    '3 → 6 partitions: Mumbai → P4; order broken across change; never reduce.',
    'librdkafka default partitioner differs; use murmur2_random for compatibility.',
]
FAQ = [
    ('How many partitions should a topic have?', 'Enough for peak consumer parallelism and throughput with headroom; too many add overhead. Lesson 10.2 gives a method.'),
    ('Do offsets ever reset to 0?', 'No. Offsets keep growing; old records are deleted by retention, so the first available offset (log start offset) rises.'),
    ('What if I send no key?', 'The producer spreads records using sticky partitioning: it fills a batch for one partition, then switches. Good spread, no ordering.'),
    ('Is offset a byte position?', 'No, it is a record number. The broker’s .index file maps offsets to byte positions in the log (Lesson 4.2).'),
]

PRACTICE_INTRO = 'Partition and offset programs.'
PROBLEMS = [
    dict(level='easy', title='Next offset', stmt='After 4 records in a partition.', inp='4',
         code='''print(4)
''', explain='Offsets 0–3 used.'),
    dict(level='easy', title='Modulo', stmt='Hash 2542653612 into 3 and 6 partitions.', inp='hash',
         code='''h = 2542653612 & 0x7fffffff
print(h % 3, h % 6)
''', explain='1 and 4.'),
    dict(level='easy', title='Order per key', stmt='Filter Mumbai events in order.', inp='events',
         code='''ev = [("Mumbai", "o1"), ("Pune", "o2"), ("Mumbai", "o4")]
print([v for k, v in ev if k == "Mumbai"])
''', explain='Same partition → order kept.'),
    dict(level='medium', title='Hot partition', stmt='Share of the busiest partition.', inp='[6, 4, 0]',
         code='''c = [6, 4, 0]
print(round(100 * max(c) / sum(c)), "%")
''', explain='60% on one partition.'),
    dict(level='medium', title='Moved keys', stmt='Which keys change partition from 3 to 6?', inp='hashes',
         code='''hs = {"Mumbai": 2542653612, "Pune": 1038389049, "Delhi": 913835919, "Chennai": 532687110}
print([k for k, h in hs.items() if (h & 0x7fffffff) % 3 != (h & 0x7fffffff) % 6])
''', explain='Mumbai, Pune, Delhi move.'),
    dict(level='medium', title='Seek slice', stmt='Offsets 1..2 of a partition.', inp='list',
         code='''p = ["a", "b", "c", "d"]
print(p[1:3])
''', explain='Inclusive start, exclusive end.'),
    dict(level='business', title='Partition count', stmt='Peak 40 MB/s, 4 MB/s per consumer, 1.5× headroom.', inp='numbers',
         code='''import math
print(math.ceil(40 / 4 * 1.5))
''', explain='15 partitions.'),
    dict(level='business', title='Storage per partition', stmt='1 TB/day over 24 partitions.', inp='numbers',
         code='''print(round(1024 / 24, 1), "GB per partition per day")
''', explain='Balanced keys matter.'),
]

SCN_INTRO = 'Partitioning questions are interview favourites.'
SCENARIOS = (
    scn('Any company · data', 'Fresher', '“What is an offset?”',
        'Define it precisely.',
        'answer?',
        '<p>A per-partition, increasing number that identifies each record’s position. Consumers track the next offset to read; offsets are never reused, and order is guaranteed only within a partition.</p>', '“A byte position in the topic.”') +
    scn('E-commerce', 'Mid-level', 'Ordering bug',
        'Status updates of an order arrive out of order.',
        'diagnose?',
        '''<ul>
          <li>Check the key: must be order_id.</li>
          <li>Check for a recent partition increase.</li>
          <li>Check mixed clients with different partitioners.</li>
        </ul>''', '“Kafka does not guarantee order.”') +
    scn('Data engineering', 'Mid-level', 'Hot partition',
        'One consumer lags while others idle.',
        'fix?',
        '''<ul>
          <li>Inspect key distribution.</li>
          <li>Use a higher-cardinality key or a compound key.</li>
          <li>Salting only if per-key order is not needed.</li>
        </ul>''', 'Adding consumers.') +
    scn('Platform', 'Senior', 'Changing partitions',
        'A keyed topic must go from 12 to 48 partitions.',
        'plan?',
        '''<ol>
          <li>Create a new topic with 48 partitions.</li>
          <li>Dual-write or mirror, then switch consumers after draining.</li>
          <li>Or accept remap if per-key order across the switch is not needed.</li>
        </ol>''', '“Just alter it at peak time.”')
)
