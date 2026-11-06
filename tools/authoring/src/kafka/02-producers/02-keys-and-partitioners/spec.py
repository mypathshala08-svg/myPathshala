import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
BODY = body(HERE)
META = dict(module='02-producers', lesson='02-keys-and-partitioners', n='2.2', module_label='Module 2 · Producers',
    title='Keys and partitioners',
    desc='How Kafka producers choose partitions: explicit partition, key hashing (murmur2 in Java, consistent_random/CRC32 by default in librdkafka) and sticky partitioning for null keys, adaptive partitioning and custom partitioners. Real Kafka 4.4 lab: sticky batches seen in kafka-dump-log, the same key landing in different partitions with two partitioners, a hot key with 792 of 1,000 records, and a compound-key fix.',
    og_desc='Same key, two partitions: Kafka partitioners, sticky batches and hot keys measured on a real cluster.',
    minutes=26, level='Intermediate',
    lead='Who decides the partition? We test <b>keyless sticky batches</b>, compare the <b>Java and Python default partitioners</b> on the same keys, overload one partition with a <b>hot key</b> and fix it. <b>All outputs are real.</b>',
    chips=['Sticky batches in dump-log', 'murmur2 vs CRC32', 'Hot key fixed', 'Runs in your browser (Python)'])
MAIN = '''# Three ways to choose a partition
import zlib
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

for key in ["o101", "Mumbai", "user9@upi"]:
    java = (murmur2(key.encode()) & 0x7fffffff) % 3
    crc = zlib.crc32(key.encode()) % 3          # librdkafka "consistent" hash
    print(f"{key:10} murmur2 -> P{java}   crc32 -> P{crc}")
'''
RUN = dict(heading='Run the code: two hash functions', intro='<p>Compute both placements yourself. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    java = (murmur2(key.encode()) & 0x7fffffff) % 3', 'The Java client’s rule.'), ('    crc = zlib.crc32(key.encode()) % 3          # librdkafka "consistent" hash', 'librdkafka’s consistent partitioner uses CRC32.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Then add your own keys.', code=None),
        dict(label='2 · Predict first: hot partition', hint='<b>Predict first:</b> 70% of 1,000 records share one key. Minimum on one partition?', code='print(int(1000 * 0.7))\n'),
        dict(label='3 · Compound key', hint='Spread one key into 4.', code='keys = [f"rest-1#{i % 4}" for i in range(8)]\nprint(sorted(set(keys)))\n'),
        dict(label='4 · Sticky', hint='Simulate sticky: switch after each batch of 4.', code='parts, p = [], 0\nfor i in range(12):\n    parts.append(p)\n    if (i + 1) % 4 == 0: p = (p + 1) % 3\nprint(parts)\n'),
        dict(label='5 · Spot the error', hint='Mixed partitioners.', expect='error', code='java, python = 1, 0\nassert java == python, "same key, different partitions: set partitioner=murmur2_random"\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: choose the partitioner', intro='<p>Python confluent-kafka. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Java-compatible', cmd='Producer({"bootstrap.servers": "localhost:9092", "partitioner": "murmur2_random"})', file='python', output='Mumbai -> P1', note='Matches Java.'),
           dict(title='2 · Explicit partition', cmd='p.produce("orders", value="x", partition=2)', file='python', output='delivered to partition 2', note='Overrides the key.'),
           dict(title='3 · Batches on disk', cmd='kafka-dump-log.sh --files /var/lib/kafka/data/sticky-22-1/00000000000000000000.log', file='terminal', output='baseOffset: 0 lastOffset: 3 count: 4 …', note='One batch per line.')])
TRACE = dict(heading='Pick a partition', intro='<p>The decision order.</p>',
    code='def choose(partition, key, sticky):\n    if partition is not None:\n        return partition\n    if key is not None:\n        return hash(key) % 3\n    return sticky\nprint(choose(2, "o1", 0), choose(None, None, 1))\n',
    notes={3: 'Explicit :: Wins first.', 6: 'Keyless :: Use the current sticky partition.'})
WORKED_INTRO = 'Three partitioning decisions.'
EXAMPLES = [
    dict(level='b', tag='Partitioner · config', title='Match Java from Python', problem='<p>Python and Java write keyed orders.</p>', inp='config',
         approach=['Set partitioner=murmur2_random.', 'Test a few keys.', 'Document it.'], code='conf = {"bootstrap.servers": "localhost:9092", "partitioner": "murmur2_random"}\nprint(conf)\n', notes={1: 'One line :: Avoids split keys.'}, tryit='Step 2.'),
    dict(level='i', tag='Partitioner · skew', title='Measure key skew', problem='<p>Is any key too hot?</p>', inp='key counts',
         approach=['Count records per key.', 'Share of the top key.', 'Split if above ~20%.'], code='from collections import Counter\nc = Counter(["rest-1"] * 700 + ["rest-2"] * 300)\nk, n = c.most_common(1)[0]\nprint(k, round(100 * n / sum(c.values())), "%")\n', notes={1: 'Data first :: Measure before redesign.'}, tryit='Step 3.'),
    dict(level='a', tag='Partitioner · custom', title='A VIP partition (Java)', problem='<p>Premium customers need a dedicated partition.</p>', inp='customer tier',
         approach=['Implement Partitioner.partition().', 'Return 0 for VIP, hash for others.', 'Set partitioner.class.'],
         code='def partition(key, n, vip):\n    return 0 if key in vip else 1 + hash(key) % (n - 1)\nprint(partition("c1", 6, {"c1"}), partition("c2", 6, {"c1"}) > 0)\n', notes={1: 'Custom :: Use sparingly; documents a business rule.'}, tryit='Types table.')]
QUIZ = mix([
    dict(q='Beginner: Records with the same key go to…', options=['Random partitions', 'The same partition', 'Partition 0', 'All partitions'], answer=1, why='While the count is unchanged.'),
    dict(q='Beginner: Records with no key are…', options=['Rejected', 'Sent in sticky batches', 'Sent to partition 0', 'Duplicated'], answer=1, why='Step 1.'),
    dict(q='Beginner: The Java client’s key hash is…', options=['MD5', 'murmur2', 'SHA-256', 'CRC32'], answer=1, why='murmur2 % n.'),
    dict(q='Intermediate: librdkafka’s default partitioner is…', options=['murmur2', 'consistent_random', 'round_robin', 'sticky'], answer=1, why='CRC32 for keys.'),
    dict(q='Intermediate: Python producer matching Java uses…', options=['partitioner=murmur2_random', 'acks=all', 'linger.ms=0', 'nothing'], answer=0, why='Same hash.'),
    dict(q='Intermediate: 792 of 1,000 records on P1 means…', options=['Healthy', 'A hot key', 'Replication', 'Compression'], answer=1, why='70% one restaurant.'),
    dict(q='Advanced: Since 3.3 the Java producer’s keyless partitioning is…', options=['Random', 'Adaptive (favours faster brokers)', 'Round-robin', 'Disabled'], answer=1, why='KIP-794.'),
    dict(q='Advanced: A compound key rest-1#n keeps order…', options=['Per restaurant', 'Per sub-key only', 'Globally', 'Never'], answer=1, why='Trade-off.')])
REVISION = ['Order: explicit partition > key hash > sticky (no key).', 'Java: murmur2 % n; librdkafka default consistent_random (CRC32); use murmur2_random to match.',
    'Lab: sticky batches of 4 (P0 6, P1 16, P2 8); Mumbai P1 vs P0.', 'Hot key: 792/1,000 on P1; compound key → 445/442.', 'Adaptive partitioning (3.3+), custom Partitioner, partitioner.ignore.keys.']
FAQ = [('Can I change the partitioner of an existing topic?', 'It is a producer setting. Changing it moves keys, like adding partitions; coordinate the switch.'),
    ('Is round-robin still available?', 'Java has RoundRobinPartitioner as an optional class; most apps use the default sticky behaviour.'),
    ('How many keys are enough?', 'Many more than partitions (hundreds or thousands) for an even spread; check the top key’s share.'),
    ('Does the broker choose the partition?', 'No. The producer chooses; the broker only stores what it receives.')]
PRACTICE_INTRO = 'Partitioning programs.'
PROBLEMS = [
    dict(level='easy', title='Modulo', stmt='Partition for hash 2542653612 with 3 partitions.', inp='hash', code='print((2542653612 & 0x7fffffff) % 3)\n', explain='1.'),
    dict(level='easy', title='CRC32', stmt='CRC32 partition for "Pune".', inp='key', code='import zlib\nprint(zlib.crc32(b"Pune") % 3)\n', explain='librdkafka consistent.'),
    dict(level='easy', title='Top share', stmt='Share of 792 out of 1000.', inp='792', code='print(792 / 1000 * 100, "%")\n', explain='79%.'),
    dict(level='medium', title='Count per partition', stmt='Partition counts from a list.', inp='list', code='from collections import Counter\nprint(Counter([1, 1, 0, 2, 1]))\n', explain='Spot skew.'),
    dict(level='medium', title='Salting', stmt='Salt key with order id % 4.', inp='orders', code='print([f"rest-1#{o % 4}" for o in range(6)])\n', explain='4 sub-keys.'),
    dict(level='medium', title='Sticky runs', stmt='Group a partition list into runs.', inp='[0,0,1,1,1,2]', code='from itertools import groupby\nprint([(k, len(list(g))) for k, g in groupby([0, 0, 1, 1, 1, 2])])\n', explain='Batches.'),
    dict(level='business', title='Consumer load', stmt='Time for P1 at 100 records/s.', inp='792', code='print(round(792 / 100, 1), "s")\n', explain='Others finish in ~1 s.'),
    dict(level='business', title='Mismatch impact', stmt='Keys that disagree in Step 2.', inp='2 of 6', code='print(round(2 / 6 * 100), "% of keys split")\n', explain='Enough to break ordering.')]
SCN_INTRO = 'Partitioning interview questions.'
SCENARIOS = (scn('Any company · backend', 'Fresher', '“How is a partition chosen?”', 'Explain.', 'answer?', '<p>Explicit partition if set; otherwise hash of the key modulo the partition count (murmur2 in Java); without a key, sticky partitioning fills one partition’s batch before switching.</p>', '“Randomly.”') +
    scn('E-commerce', 'Mid-level', 'Ordering across languages', 'Java and Python producers break order.', 'fix?', '<ul><li>Different default partitioners.</li><li>Set murmur2_random in librdkafka clients.</li><li>Verify with a key placement test.</li></ul>', '“Kafka is buggy.”') +
    scn('Marketplace', 'Mid-level', 'Hot seller', 'One seller overloads a partition.', 'design?', '<ul><li>Compound key seller#n if order per seller is not needed.</li><li>Otherwise dedicate capacity.</li><li>Monitor per-partition lag.</li></ul>', 'Adding partitions only.') +
    scn('Platform', 'Senior', 'Keyless throughput', 'Logs cluster has one slow broker.', 'explain?', '<ul><li>Java adaptive partitioning sends less to slow brokers.</li><li>Tune partitioner.availability.timeout.ms.</li><li>Fix the broker.</li></ul>', 'Round-robin everything.'))
