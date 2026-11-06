import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
K, ST = 'l22_keys.txt', 'l22_sticky.txt'
def sec(c, a, b=None, drop=()):
    return capsec(c, a, b, drop)
B = '../../'
hk = hook('The same key went to two different partitions. Same Kafka, same topic. How?',
    'A Java service and a Python service wrote the key <code>Mumbai</code> to the same topic, and Kafka stored it in partition 1 for one and partition 0 for the other. Nothing was broken: they used different <b>partitioners</b>. This lesson shows every way a partition is chosen, and how to fix hot keys.',
    ['How records <b>without</b> a key are spread (and why it is not random).',
     'Which client libraries agree on key placement, and which do not.',
     'How one restaurant with 70% of orders overloads one partition, and a 1-line fix.'])
cmap = concept_map('Concept map. Beginner: key, null key, same key same partition. Intermediate: murmur2, sticky partitioning, librdkafka partitioners, hot keys. Advanced: adaptive partitioning, custom partitioners, compound keys and salting.',
    [[('ky', 'Key', 'order_id, user_id', None), ('nk', 'No key', 'spread for throughput', None), ('sm', 'Same key → same partition', 'Lesson 1.4', B + '01-introduction/04-topics-partitions-and-offsets/')],
     [('mm', 'murmur2', 'Java default', None), ('sk', 'Sticky partitioning', 'per batch', None), ('lr', 'librdkafka options', 'consistent_random …', None), ('hk', 'Hot keys', 'skew', None)],
     [('ad', 'Adaptive partitioning', 'slow brokers avoided', None), ('cp', 'Custom partitioner', 'Java interface', None), ('sa', 'Compound key / salting', 'spread hot keys', None)]],
    [('ky', 'mm'), ('nk', 'sk'), ('sm', 'lr'), ('sk', 'ad'), ('mm', 'cp'), ('hk', 'sa'), ('ky', 'hk')],
    {'ky', 'nk', 'sm', 'mm', 'sk', 'lr', 'hk', 'sa'},
    '<b>Builds on:</b> <a href="../01-how-a-producer-sends-a-message/">2.1</a>, <a href="../../01-introduction/04-topics-partitions-and-offsets/">1.4</a>. <b>Next:</b> <a href="../03-batching-and-compression/">2.3 Batching and compression</a>.')
whw = why_how_where(
    'The partition decides ordering, parallelism and load. A wrong key choice causes out-of-order events or one overloaded consumer.',
    'With a key: hash(key) % partitions. Without a key: fill one partition’s batch, then move on (sticky). You can also name a partition or plug in your own partitioner.',
    'Order and account ids for ordering; no key for logs and metrics; compound keys for very active entities.',
    'Do not salt a key when you need strict per-key order, and do not mix partitioners across clients on one topic.')

sc_ = (box(14, 22, 296, 112, 'card', rx=10) + t(162, 40, 'Java client (murmur2)', 9, bold=True) + icon('gear', 28, 50, 1.0) +
       ''.join(t(62, 62 + k * 15, s, 7.8, 'ink2', anchor='start', mono=True) for k, s in enumerate(['o101   → P2', 'Mumbai → P1', 'user9@upi → P2'])) +
       box(330, 22, 296, 112, 'card', rx=10) + t(478, 40, 'Python default (consistent_random)', 9, bold=True) + icon('chart', 344, 50, 1.0) +
       ''.join(t(378, 62 + k * 15, s, 7.8, c, anchor='start', mono=True) for k, (s, c) in enumerate([('o101   → P2', 'ink2'), ('Mumbai → P0  ✗', 'red'), ('user9@upi → P0  ✗', 'red')])))
scene_svg = scene('Left: the Java client with murmur2 puts o101 in partition 2, Mumbai in partition 1 and user9@upi in partition 2. Right: the Python default consistent_random puts Mumbai and user9@upi in partition 0, so the same keys land in different partitions.', sc_,
                  'Same key, different <tspan font-weight="700" class="s-acc">partitioner</tspan>, different partition.')
dialogue = '''R> Sir, our Java order service and the new Python offers service both use key = city. Why are Mumbai events in two partitions?
A> Each client library has a default partitioner. The Java client uses <b>murmur2</b>; Python’s confluent-kafka (librdkafka) defaults to <b>consistent_random</b>, which uses a different hash (CRC32).
K> So ordering per city is broken?
A> Yes, across the two services. The fix is one line: <code>"partitioner": "murmur2_random"</code> in Python. Today we test every partitioning mode on the cluster, including records with no key and a very hot key.'''

lv = '''
LEVELS> Partitioning at three levels
L1> Sorting parcels
      <ul>
        <li>Parcels with an address (key) always go to the same counter for that area. Parcels without an address go to whichever counter is filling a sack right now, until the sack is full.</li>
      </ul>
L2> The rules
      <ul>
        <li><b>Explicit partition</b> in <code>produce(..., partition=2)</code> wins over everything.</li>
        <li><b>Key</b>: the partitioner hashes the key bytes. Java: <code>murmur2 % n</code>. librdkafka: chosen by <code>partitioner</code> (default <code>consistent_random</code> = CRC32 for keyed, random for null keys).</li>
        <li><b>No key</b>: sticky partitioning: one partition until a batch is sent, then another (Java since 2.4, KIP-480; librdkafka with <code>sticky.partitioning.linger.ms</code>).</li>
      </ul>
L3> Advanced details
      <ul>
        <li>Since Kafka 3.3 the Java producer’s built-in partitioner is <b>adaptive</b> (KIP-794) for keyless records: it sends more to faster brokers and can avoid unavailable ones (<code>partitioner.adaptive.partitioning.enable</code>, <code>partitioner.availability.timeout.ms</code>). <code>partitioner.ignore.keys=true</code> spreads even keyed records.</li>
        <li>A custom Java partitioner implements <code>org.apache.kafka.clients.producer.Partitioner</code> (method <code>partition(...)</code>) and is set with <code>partitioner.class</code>.</li>
        <li>librdkafka partitioners: <code>random</code>, <code>consistent</code>, <code>consistent_random</code>, <code>murmur2</code>, <code>murmur2_random</code>, <code>fnv1a</code>, <code>fnv1a_random</code>. The <code>_random</code> variants spread null keys randomly; only <code>murmur2*</code> match Java placement.</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of the partition decision: an explicit partition wins; otherwise a key is hashed by the configured partitioner and taken modulo the partition count; otherwise sticky partitioning fills one partition batch at a time.',
    t(16, 22, 'How the producer picks a partition (in this order)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('partition=2 given?', 'acc', 1), ('→ use it', 'card', None)]) +
    fields(16, 70, [('key present?', 'green', 2), ('→ hash(key bytes) % partitions', 'card', None), ('hash = murmur2 / CRC32 / FNV-1a', 'violet', 3)]) +
    fields(16, 106, [('no key', 'blue', 4), ('→ sticky: same partition until the batch is sent', 'card', None)]) +
    legend(16, 156, [(1, 'Explicit', 'you choose; rare (e.g. replaying one partition)'),
                     (2, 'Keyed', 'same key → same partition while the count is unchanged'),
                     (3, 'Hash function', 'depends on the client and its partitioner setting'),
                     (4, 'Keyless', 'big batches, good spread over time, no ordering')], size=8, gap=15, w=110),
    h=228, caption='The three paths, as implemented by the Java client and librdkafka.')
extra = '''

  <h3>Dissect the partition decision</h3>
''' + DIS

types_html = table(['Strategy', 'Config', 'Ordering', 'Spread'], [
    ['Key = business id', 'default (Java) / murmur2_random (Python)', 'per key', 'good with many keys'],
    ['No key', 'sticky (default)', 'none', 'very good, big batches'],
    ['Compound key', 'key = "rest-1#3"', 'per sub-key only', 'spreads hot keys'],
    ['Explicit partition', 'produce(partition=n)', 'you decide', 'you decide'],
    ['Custom partitioner', 'partitioner.class (Java)', 'your rule', 'your rule'],
    ['Ignore keys', 'partitioner.ignore.keys=true (Java)', 'none', 'like keyless'],
], minw=620)
warn = 'If Java and Python (or Go, .NET, Node) producers write the same keyed topic, set the same hash everywhere: <code>partitioner=murmur2_random</code> for librdkafka-based clients. Also, a <b>null</b> key and an <b>empty</b> key are not the same: the Java client hashes an empty key like any other key, while librdkafka’s <code>*_random</code> partitioners treat empty and null keys alike (random spread).'

steps = [
    ('Step 1 · No key: sticky batches',
     code('bash', 'terminal', 'seq -f "log line %02g ..." 1 30 | kafka-console-producer.sh --bootstrap-server k1:9092 --topic sticky-22 \\\n  --command-property batch.size=300 --command-property linger.ms=100\nkafka-dump-log.sh --files /var/lib/kafka/data/sticky-22-*/00000000000000000000.log', sec(ST, '      6 Partition:0')),
     'The Java console producer sent 30 keyless lines. With a tiny <code>batch.size</code> of 300 bytes each batch held 4 records, and each batch went to <b>one</b> partition before the producer moved on: P0, P1 and P2 received whole batches, not one record each. Totals 6 / 16 / 8: sticky is fair over time, not per record.'),
    ('Step 2 · Two partitioners, same keys',
     code('python', 'l22_keys.py', 'run("k-murmur", {"partitioner": "murmur2_random"}, keys)     # Java-compatible\nrun("k-crc",    {"partitioner": "consistent_random"}, keys)  # librdkafka default', sec(K, '== 2)', '== 3)')),
     'Four keys happened to agree, but <code>Mumbai</code> and <code>user9@upi</code> landed in different partitions. Our hand-written murmur2 (Lesson 1.4) confirms the left column exactly. Agreement on some keys makes this bug easy to miss in testing.'),
    ('Step 3 · A hot key',
     code('python', 'l22_keys.py', 'items = [("rest-1" if i % 10 < 7 else f"rest-{i}", "o") for i in range(1000)]\nCounter(partition for _, partition in run("hot-22", {"partitioner": "murmur2_random"}, items))', sec(K, '== 3)', '== 4)')),
     'Restaurant 1 sends 70% of orders, so partition 1 got 792 of 1,000 records. Its consumer does 8× the work of the others: lag grows on one partition only.'),
    ('Step 4 · Fix with a compound key',
     code('python', 'l22_keys.py', 'key = f"rest-1#{i % 4}"     # 4 sub-keys for the hot restaurant', sec(K, '== 4)')),
     'Splitting restaurant 1 into 4 sub-keys spreads it over partitions 0 and 1 (445 / 442). Order is now kept per sub-key, not per restaurant: fine for independent orders, wrong if the restaurant’s events must be strictly ordered.'),
]

see = [term([('30 keyless records', W), ('P0: 4 + 2   P1: 4+4+4+4   P2: 4 + 4', W), ('whole batches, not round-robin', G)], size=7.0),
       term([('Mumbai   murmur2 -> P1', W), ('Mumbai   consistent_random -> P0', RD), ('user9@upi -> P2 vs P0', RD)], size=7.0),
       term([('records per partition:', W), ('{0: 95, 1: 792, 2: 113}', RD)], size=7.4),
       term([('compound key rest-1#n', W), ('{0: 445, 1: 442, 2: 113}', G)], size=7.4)]
def bars3(vals, title, tone):
    mx = max(vals)
    return t(180, 14, title, 9, bold=True) + ''.join(box(60 + k * 90, 130 - 90 * v / mx, 50, 90 * v / mx, tone if v != mx or tone == 'green' else 'red', rx=3) + t(85 + k * 90, 140, f'P{k}: {v}', 7.6, 'ink') for k, v in enumerate(vals))
B1 = [t(180, 14, 'Sticky: batch by batch', 9, bold=True) + ''.join(box(20 + k * 40, 50, 34, 24, ['blue', 'green', 'violet', 'green', 'blue', 'green', 'violet', 'green'][k], rx=3) + t(37 + k * 40, 66, ['P0', 'P1', 'P2', 'P1', 'P0', 'P1', 'P2', 'P1'][k], 7.4, 'ink') for k in range(8)) + t(180, 96, 'each box = one batch of 4 records', 7.6, 'ink2') + cap('Fewer, bigger requests.', '', 'blue', y=144, h=30),
      t(180, 14, 'Different hash functions', 9, bold=True) + opbox(20, 50, '"Mumbai"', '', 'green', 70, 30) + arrow(90, 65, 120, 50, 'ink3', 1) + arrow(90, 65, 120, 82, 'ink3', 1) + opbox(120, 36, 'murmur2', '→ P1', 'blue', 100, 28) + opbox(120, 72, 'CRC32', '→ P0', 'red', 100, 28) + cap('Set murmur2_random in Python.', '', 'red', y=144, h=30),
      bars3([95, 792, 113], 'Hot key overloads P1', 'blue'),
      bars3([445, 442, 113], 'Compound key spreads it', 'green')]
two = anim_two('Keys and partitioners', 'Where records go', 'Real outputs from the lab', 'What the partitioner did', see, B1,
               ['Sticky.', 'Mismatch.', 'Hot key.', 'Fixed.'], ['Batches.', 'Hashes.', 'Skew.', 'Spread.'])
pe = peel('Key “Mumbai” through two partitioners', 'Same bytes, two decisions. (Our run.)',
    [('Key bytes', ''), ('Partitioner setting', ''), ('Java: murmur2', ''), ('Python default: CRC32', ''), ('Modulo 3', ''), ('Result', '')],
    [['Key bytes', '4d 75 6d 62 61 69', '"Mumbai" in UTF-8', ''], ['Partitioner setting', 'Java: built-in', 'librdkafka: partitioner=', 'consistent_random'],
     ['murmur2', '2542653612', '& 0x7fffffff', ''], ['CRC32', 'a different 32-bit hash', 'of the same bytes', ''],
     ['Modulo 3', 'murmur2 → 1', 'CRC32 → 0', ''], ['Result', 'two partitions for', 'one key: order lost', 'fix: murmur2_random']],
    ['Bytes.', 'Setting.', 'Java.', 'Python.', 'Modulo.', 'Mismatch.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Out-of-order city offers', 'Mixed clients on one topic. (Typical.)', ('Partitioner compatibility', 'All producers of a keyed topic must use the same hash'), [
    ('Java + Python producers', 'key = city', 'Same topic.', 'blue'), ('Mumbai in P1 and P0', 'two consumers', 'Race.', 'red'),
    ('Old offer applied last', 'wrong price shown', 'Complaint.', 'red'), ('Set murmur2_random', 'in Python config', 'One line.', 'green'),
    ('Test placement', 'compare partitions per key', 'In CI.', 'blue')], ['Setup.', 'Split.', 'Bug.', 'Fix.', 'Test.'], 'scenario-mixed') + \
       five('Real-time scenario 2', 'The mega restaurant', 'Hot key in production. (Typical.)', ('Hot keys', 'Split very active keys when per-key order is not needed'), [
    ('Cloud kitchen = 70%', 'key = restaurant', 'P1 overloaded.', 'red'), ('Consumer of P1 lags', 'others idle', 'Late orders.', 'red'),
    ('Key = rest#n', 'n = order_id % 4', 'Spread.', 'green'), ('Order per sub-key', 'acceptable here', 'Orders independent.', 'amber'),
    ('Lag even again', 'all consumers busy', 'Fixed.', 'blue')], ['Hot.', 'Lag.', 'Split.', 'Trade-off.', 'Balanced.'], 'scenario-hot') + \
       five('Real-time scenario 3 · advanced', 'A slow broker', 'Adaptive partitioning for keyless data. (Typical.)', ('Adaptive partitioning', 'Java producers send fewer keyless records to slow brokers (KIP-794)'), [
    ('Broker 2 disk is slow', 'its partitions lag', 'Keyless logs.', 'blue'), ('Old sticky/round-robin', 'same share to every partition', 'Queues grow.', 'red'),
    ('Adaptive (3.3+)', 'more to fast brokers', 'Default on.', 'green'), ('Availability timeout', 'skip unresponsive broker', 'Optional.', 'green'),
    ('Keyed data unaffected', 'key decides', 'Know the scope.', 'blue')], ['Slow.', 'Old way.', 'Adaptive.', 'Skip.', 'Scope.'], 'scenario-adaptive')
assemble(HERE, h2_story='Same key, two partitions', hook_html=hk,
    narration='TiffinGo added a Python service that publishes city offers into the same topic as the Java order service. Riya notices Mumbai offers sometimes arrive before older Mumbai events.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Keys and partitioners',
    formal='The <b>partitioner</b> is the producer component that selects the target partition of each record. If the record specifies a partition, it is used. Otherwise, for a non-null key, the partition is derived from a hash of the serialized key modulo the number of partitions (the Java client uses murmur2; librdkafka-based clients use the configured <code>partitioner</code>). For a null key, the producer uses <b>sticky partitioning</b>, sending a whole batch to one partition before switching (adaptive in the Java client since 3.3). Custom partitioners may implement other rules.',
    simple='Give a key when events must stay in order: same key, same partition. Give no key when order does not matter: the producer fills one partition’s batch at a time. Make sure all your apps hash keys the same way.',
    term_rows=[('Partitioner', 'Chooses the partition.'), ('murmur2', 'Java client’s key hash.'), ('consistent_random', 'librdkafka default (CRC32).'), ('Sticky partitioning', 'Whole batch to one partition.'), ('Hot key', 'Key with far more traffic.'), ('Compound key', 'Key + extra part to spread.'), ('Adaptive partitioning', 'Favours faster brokers.'), ('Null key', 'No key at all (not empty).')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Records without a key are spread randomly, one by one.', 'They are sent in sticky batches to one partition at a time.', 'Step 1: batches of 4 per partition.'),
               ('All Kafka clients put a key in the same partition.', 'Only clients using murmur2 match the Java client.', 'Step 2: Mumbai → P1 vs P0.'),
               ('More partitions always fix a hot key.', 'A hot key still maps to one partition; you must change the key.', 'Step 3: 792 of 1,000 on P1.')],
    exam='“How does the Kafka producer choose a partition?” Explicit partition if given; else hash(key) % numPartitions (murmur2 in Java); else sticky (adaptive since 3.3). Same key → same partition → ordered; mixed clients need the same hash; hot keys need compound keys or salting.',
    types_h2='Partitioning strategies', types_html=types_html, warn=warn,
    steps_h2='Every partitioning mode, measured', steps_intro='All outputs are real: Kafka 4.4.0, 3 brokers; Java console producer for Step 1, Python <code>confluent-kafka</code> 2.16.1 for Steps 2–4. Script: <code>jobs/m2/l22_keys.py</code>.',
    steps=steps, two=two, peel_intro='Now peel one key through both partitioners.', peel_html=pe,
    scen_intro='Three live scenarios: mixed clients, a mega restaurant, and a slow broker.', scen=scen,
    uc_h2='Key choices at work', ucs=[uc_('bank', 'account', 'blue', '1. Bank transactions', 'Key = account id: debits and credits stay in order.', ['Txn', '*key account', 'Ordered']),
        uc_('logs', 'no key', 'green', '2. Application logs', 'No key: sticky batches give the best throughput.', ['Logs', '*sticky', 'Fast']),
        uc_('shop', 'seller', 'violet', '3. Marketplace sellers', 'Very large sellers get compound keys to avoid hot partitions.', ['Orders', '*seller#n', 'Balanced']),
        uc_('ride', 'trip', 'acc', '4. Trip events', 'Key = trip id across Java and Go services with the same hash.', ['Apps', '*murmur2', 'Consistent']),
        uc_('IoT', 'device', 'blue', '5. Device telemetry', 'Key = device id: millions of keys spread evenly.', ['Devices', '*key', 'Even'])],
    uc_note='Examples are simplified descriptions of common patterns.',
    pre='<b>Before you start:</b> <a href="../01-how-a-producer-sends-a-message/">2.1</a> and <a href="../../01-introduction/04-topics-partitions-and-offsets/">1.4 (murmur2)</a>.')
