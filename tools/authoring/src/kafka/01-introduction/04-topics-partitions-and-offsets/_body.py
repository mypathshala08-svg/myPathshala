import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C, M2 = 'l14_partitions.txt', 'l14_murmur2.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
HOOK = hook('We added partitions to make Kafka faster, and Mumbai’s orders jumped to a different place. Why?',
    'Every keyed event lands in a partition chosen by a hash. We will compute that hash by hand, match it to what the real broker did, and then show the one change that silently breaks ordering.',
    ['Why partition 2 stayed <b>empty</b> while partition 0 got 6 orders.',
     'How to read from the exact middle of a partition using an offset.',
     'Why Kafka refuses to ever <b>reduce</b> partitions.'])
MAP = concept_map('Concept map. Beginner: topic, partition, offset. Intermediate: key hashing (murmur2), ordering per partition, hot partitions, seeking to offsets. Advanced: changing partition count, custom partitioners, segment files.',
    [[('tp', 'Topic', 'named stream', B + '01-introduction/01-what-is-kafka/'), ('pa', 'Partition', 'ordered log', None), ('of', 'Offset', 'position number', None)],
     [('hs', 'Key → hash → partition', 'murmur2', None), ('or', 'Order per partition', 'not per topic', None), ('ho', 'Hot partitions', 'skewed keys', None), ('sk', 'Seek to offset', 'replay a slice', None)],
     [('ch', 'Adding partitions', 'keys move!', None), ('cp', 'Custom partitioners', 'Lesson 2.2', B + '02-producers/02-keys-and-partitioners/'), ('sg', 'Segment files', 'Lesson 4.1', B + '04-storage-internals/01-the-commit-log-and-segments/')]],
    [('tp', 'hs'), ('pa', 'or'), ('of', 'sk'), ('hs', 'ch'), ('ho', 'cp'), ('sk', 'sg'), ('pa', 'ho')],
    {'tp', 'pa', 'of', 'hs', 'or', 'ho', 'sk', 'ch'},
    '<b>Builds on:</b> <a href="../03-kafka-architecture/">1.3 Architecture</a>. <b>Next:</b> <a href="../05-install-kafka-and-cli-tools/">1.5 Install and CLI</a>, then producers in Module 2.')
WHW = why_how_where(
    'One log on one machine cannot grow forever or be read by many workers at once. Partitions split a topic so it scales.',
    'The producer hashes the key (murmur2) and takes it modulo the partition count; the leader appends and assigns the next offset.',
    'Order IDs, user IDs, device IDs as keys; partitions as the unit of parallelism and of ordering.',
    'Do not expect order across partitions, and do not change partition count of keyed topics casually.')

def pr(y, label, cells):
    return pcol(84, y, label, cells, 'blue', cw=42, ch=20)
sc_ = (t(14, 18, 'topic city-orders · key = city', 8.6, 'ink', anchor='start', bold=True) +
       pr(30, 'P0', ['Pune', 'Delhi', 'Chen', 'Pune', 'Delhi', 'Chen']) + pr(56, 'P1', ['Mum', 'Mum', 'Mum', 'Mum']) + pr(82, 'P2', []) +
       t(100, 96, '(empty)', 8, 'red', anchor='start') +
       ''.join(t(84 + k * 44 + 21, 116, str(k), 7.6, 'ink2', mono=True) for k in range(6)) + t(60, 116, 'offset →', 7.6, 'ink2', anchor='end') +
       box(390, 24, 236, 104, 'card') + t(508, 40, 'partition = murmur2(key) % 3', 8.2, bold=True, mono=True) +
       ''.join(t(402, 58 + k * 16, s, 7.6, 'ink2', anchor='start', mono=True) for k, s in enumerate(['Mumbai  → 1', 'Pune    → 0', 'Delhi   → 0', 'Chennai → 0'])))
scene_svg = scene('Topic city-orders with three partitions. Pune, Delhi and Chennai orders all hash to partition 0, Mumbai to partition 1, and partition 2 stays empty. Each cell is an event with an offset 0, 1, 2 and so on.', sc_,
                  'Keys decide partitions; <tspan font-weight="700" class="s-acc">offsets</tspan> number events inside each one.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Three partitions, one empty</h2>
  <div class="story">
{HOOK}
    <p class="narration">Riya keys every order by its city so a city’s orders stay in order. She sends 10 orders from 4 cities into a topic with 3 partitions and expects them to spread out evenly.</p>

{scene_svg}

R> Sir, partition 2 got nothing and partition 0 got six! Is Kafka broken?
A> Kafka did exactly what it promised: <b>same key → same partition</b>. With only 4 different keys, three of them happened to hash to partition 0. Partitions balance only when there are <b>many</b> keys.
K> So should we just add partitions?
A> Careful. Adding partitions changes the hash result. Let’s compute the hash by hand, compare it with the broker, and then add partitions to see Mumbai move.
  </div>
</section>
'''

lv = '''
LEVELS> Partitions and offsets at three levels
L1> Railway platforms
      <ul>
        <li>A topic is a station; partitions are its platforms. Every train for “Mumbai” always uses the same platform, so Mumbai trains leave in order.</li>
        <li>An offset is a train’s serial number on its platform: 0, 1, 2 … Numbers on different platforms are unrelated.</li>
      </ul>
L2> The rules
      <ul>
        <li>Offsets are per partition, start at 0 and only grow; they are never reused.</li>
        <li>Order is guaranteed <b>within</b> a partition only. Consumers can start from the beginning, the end, or any offset.</li>
        <li>With a key, the default partitioner uses <code>murmur2(key) % partitions</code> (Java client). Without a key, records are spread in “sticky” batches.</li>
      </ul>
L3> Sharp edges
      <ul>
        <li>Adding partitions changes <code>% n</code>, so existing keys can move (Mumbai: 1 → 4), breaking per-key order across the change. Partitions can never be reduced.</li>
        <li>Different client libraries can use different default partitioners: librdkafka’s default (<code>consistent_random</code>, CRC32) differs from Java’s murmur2, so set <code>partitioner=murmur2_random</code> when Python and Java produce to the same keyed topic.</li>
        <li>Few or skewed keys create <b>hot partitions</b> that limit throughput.</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of the partition formula: the key Mumbai is turned into bytes, hashed with murmur2 to 2542653612, made positive, and taken modulo 3 to give partition 1, or modulo 6 to give partition 4.',
    fields(16, 34, [('key "Mumbai"', 'green', 1), ('→ UTF-8 bytes', 'card', None), ('murmur2 = 2542653612', 'violet', 2), ('& 0x7fffffff', 'card', 3), ('% 3 = 1', 'acc', 4)]) +
    fields(16, 80, [('same key', 'green', None), ('% 6 = 4', 'red', 5), ('→ new partition after adding partitions', 'card', None)]) +
    legend(16, 132, [(1, 'Key', 'any bytes: order id, user id, city'),
                     (2, 'Hash', 'murmur2, the Java client’s default; same key → same number'),
                     (3, 'Make positive', 'clear the sign bit'),
                     (4, 'Modulo partitions', '3 partitions → Mumbai goes to partition 1 (matches the broker)'),
                     (5, 'Change n, change result', '6 partitions → partition 4: the key moved')], size=8, gap=15, w=150),
    h=222, caption='Computed by our Python script and matched to the real broker.')
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Topics, partitions and offsets</h2>
''' + def_block(
    'A <b>topic</b> is a named, logical stream of records divided into one or more <b>partitions</b>. Each partition is an ordered, immutable, append-only sequence of records, and each record in it is identified by a monotonically increasing 64-bit <b>offset</b>. Ordering is guaranteed only within a partition. The producer’s <b>partitioner</b> chooses the partition: for keyed records the default (Java) partitioner computes <code>toPositive(murmur2(key)) % numPartitions</code>; records with the same key therefore go to the same partition as long as the partition count is unchanged. Partitions are the unit of parallelism, replication and storage.',
    'A topic is split into partitions; each partition is a numbered list that only grows. The key decides which list an event joins, so events with the same key stay in order. Offsets are the numbers in each list.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Partition', 'Ordered, append-only part of a topic.'),
    ('Offset', 'Record number within a partition.'),
    ('Partitioner', 'Picks the partition for a record.'),
    ('murmur2', 'Hash used for keys (Java default).'),
    ('Log end offset', 'Next offset to be written.'),
    ('Hot partition', 'Partition with far more load.'),
    ('Seek', 'Start reading at a chosen offset.'),
    ('Sticky partitioning', 'Unkeyed records batched per partition.'),
]) + '''

  <h3>Why, how, where</h3>
''' + WHW + '''

  <h3>Concept map: what depends on what</h3>
''' + MAP + '''

  <h3>The offset ruler</h3>
  <p>Three markers explain almost every consumer problem: where the log starts, where a group has read up to, and where the next event will be written.</p>
''' + offset_ruler('Offsets 0 to 9 of one partition from old to new. Log start at 0, the group committed offset at 6, log end at 10, so lag is 4. Retention deletes from the left; producers append on the right.', label='One partition, one consumer group (illustration)') + '''
  <h3>Dissect the partition formula</h3>
''' + DIS + lv + myths([('Without a key, Kafka picks a random partition for every message.', 'Since Kafka 2.4 the producer uses sticky partitioning: it fills a batch for one partition, then switches.', 'keyless sends are covered with real batches in Lesson 2.2.'), ('Kafka keeps the whole topic in order.', 'Order is guaranteed only within a partition.', 'Step 2: offsets restart at 0 in every partition.'), ('You can reduce partitions later.', 'Partitions can only be increased.', 'Step 6: InvalidPartitionsException.')]) + '''
EXAM> “How does Kafka decide the partition and guarantee order?” Keyed records: hash(key) % partitions (murmur2 in the Java client), so same key → same partition → ordered by offset. No key: sticky/round-robin spreading. Order holds only within a partition, and increasing partitions remaps keys.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Choosing keys and partition counts</h2>
''' + table(['Key choice', 'Ordering you get', 'Risk'], [
    ['No key', 'none', 'fine for independent events; best spread'],
    ['order_id', 'per order', 'many keys → even spread'],
    ['city', 'per city', 'few keys → hot partitions (our lab)'],
    ['customer_id', 'per customer', 'a very active customer can be hot'],
    ['compound (city + order_id)', 'per order, spread by city', 'more complex consumers'],
], minw=560) + '''
''' + table(['Where to start reading', 'Setting / tool'], [
    ['From the oldest retained', '<code>auto.offset.reset=earliest</code>, <code>--from-beginning</code>'],
    ['Only new events', '<code>auto.offset.reset=latest</code> (default)'],
    ['A specific offset', '<code>consumer.seek()</code>, <code>--partition 1 --offset 2</code>'],
    ['A point in time', '<code>offsetsForTimes()</code> / reset group <code>--to-datetime</code>'],
], minw=520) + '''
WARN> Never rely on order <b>across</b> partitions, and decide the partition count early for keyed topics. In our lab, Mumbai’s order o11 went to partition 4 after growing from 3 to 6 partitions, while o1–o10 stayed in partition 1: a consumer could process o11 before o10.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Keys, offsets, seek, and the remap</h2>
  <p>All outputs are real: Kafka 4.4.0, 3 brokers, Java console tools (default murmur2 partitioner). Hash check: lab <code>jobs/m1/murmur2.py</code>.</p>
''' + stepper([
    ('Step 1 · Create and produce keyed orders',
     code('bash', 'terminal', 'kafka-topics.sh --bootstrap-server k1:9092 --create --topic city-orders --partitions 3 --replication-factor 3\nprintf \'Mumbai:o1\\nPune:o2\\nDelhi:o3\\n...\' | kafka-console-producer.sh --bootstrap-server k1:9092 \\\n  --topic city-orders --reader-property parse.key=true --reader-property key.separator=:', sec('== 1)', '== 3)')),
     'Ten orders, keys = city. The console producer splits each line at “:” into key and value.'),
    ('Step 2 · See partition and offset of every event',
     code('bash', 'terminal', 'kafka-console-consumer.sh --bootstrap-server k1:9092 --topic city-orders --from-beginning \\\n  --formatter-property print.key=true --formatter-property print.partition=true --formatter-property print.offset=true', sec('== 3)', '== 4)')),
     'Mumbai’s 4 orders are partition 1, offsets 0–3, in the order sent. Pune, Delhi and Chennai share partition 0. Partition 2 is empty: a hot/cold split caused by only 4 keys.'),
    ('Step 3 · Prove the hash by hand',
     code('python', 'murmur2.py', 'def partition(key, n):\n    return (murmur2(key.encode()) & 0x7fffffff) % n\nfor city in ["Mumbai", "Pune", "Delhi", "Chennai"]: ...', capsec(M2, 'Mumbai')),
     'Our 20-line murmur2 gives exactly the broker’s choices: Mumbai → 1, the others → 0. Nothing magic: just a hash and a modulo.'),
    ('Step 4 · End offsets and seeking',
     code('bash', 'terminal', 'kafka-get-offsets.sh --bootstrap-server k1:9092 --topic city-orders\nkafka-console-consumer.sh --bootstrap-server k1:9092 --topic city-orders --partition 1 --offset 2 ...', sec('== 4)', '== 6)')),
     '<code>city-orders:0:6</code> means partition 0’s next offset is 6. Reading partition 1 from offset 2 returns exactly o7 and o10: you can replay any slice.'),
    ('Step 5 · Add partitions: the key moves',
     code('bash', 'terminal', 'kafka-topics.sh --bootstrap-server k1:9092 --alter --topic city-orders --partitions 6\necho "Mumbai:o11" | kafka-console-producer.sh ...', sec('== 6)', '== 7)')),
     'The new Mumbai order went to partition <b>4</b>, exactly as <code>murmur2 % 6</code> predicted, while older Mumbai orders remain in partition 1. Per-key ordering is broken across the change.'),
    ('Step 6 · You can never reduce partitions',
     code('bash', 'terminal', 'kafka-topics.sh --bootstrap-server k1:9092 --alter --topic city-orders --partitions 2', sec('== 7)')),
     '<b>InvalidPartitionsException</b>: partitions only grow. To shrink you create a new topic and copy data. Choose the count carefully up front (Lesson 10.2).'),
]) + '''
</section>
'''

see = [
    term([('Partition:1 Offset:0 Mumbai o1', W), ('Partition:1 Offset:1 Mumbai o4', W), ('Partition:0 Offset:0 Pune   o2', W), ('city-orders:2:0   (empty)', RD)], size=7.2),
    term([('Mumbai  murmur2=2542653612', W), ('  3 partitions -> 1', G), ('  6 partitions -> 4', Y)], size=7.2),
    term([('--partition 1 --offset 2', W), ('Offset:2  Mumbai  o7', G), ('Offset:3  Mumbai  o10', G)], size=7.2),
    term([('--alter --partitions 6', Y), ('Partition:4  Mumbai  o11', RD), ('Partition:1  Mumbai  o1..o10', W)], size=7.2),
]
def lanes(n, extra_hi=None, mumbai=1, o11=False):
    o = ''
    data = {0: ['P', 'D', 'C', 'P', 'D', 'C'], 1: ['M', 'M', 'M', 'M']}
    for p in range(n):
        cells = data.get(p, [])
        if o11 and p == 4: cells = ['M']
        o += pcol(40, 24 + p * (18 if n > 3 else 26), f'P{p}', cells, 'blue', cw=20, ch=14 if n > 3 else 20, hi=(0,) if (o11 and p == 4) else ())
    return o
B1 = [
    t(180, 14, 'Same key → same partition', 9, bold=True) + lanes(3) + t(250, 60, 'P2 empty:', 8, 'red', anchor='start', bold=True) + t(250, 74, 'only 4 keys', 8, 'ink2', anchor='start') + cap('Few keys = uneven partitions.', '', 'amber', y=144, h=30),
    t(180, 14, 'hash % n', 9, bold=True) + opbox(20, 50, '"Mumbai"', 'key', 'green', 80, 34) + arrow(100, 67, 140, 67, 'ink3', 1) + opbox(140, 50, 'murmur2', '2542653612', 'violet', 90, 34) + arrow(230, 67, 260, 67, 'ink3', 1) + opbox(260, 50, '% 3 = 1', '', 'acc', 80, 34) + cap('Deterministic, matches broker.', '', 'blue', y=144, h=30),
    t(180, 14, 'Seek to offset 2 in P1', 9, bold=True) + pcol(60, 50, 'P1', ['o1', 'o4', 'o7', 'o10'], 'blue', cw=44, hi=(2, 3)) + arrow(152, 92, 152, 74, 'acc', 1.2) + t(152, 104, 'start here', 7.6, 'acc') + cap('Replay any slice.', '', 'green', y=144, h=30),
    t(180, 14, '6 partitions: Mumbai moves to P4', 9, bold=True) + lanes(6, o11=True) + cap('Old orders P1, new P4: order broken.', '', 'red', y=144, h=30),
]
two = anim_two('Partitions and offsets', 'Keys, hashes, offsets', 'Real outputs from the lab', 'What decides where events go', see, B1,
               ['Spread.', 'Hash.', 'Seek.', 'Remap.'], ['Skew.', 'Formula.', 'Offsets.', 'Keys move.'])
PEEL = peel('Where does “Mumbai:o11” go?', 'The producer’s decision, layer by layer. (Java client defaults.)',
    [('Record', ''), ('Serialize', ''), ('Partitioner', ''), ('Batch', ''), ('Leader append', ''), ('Offset', '')],
    [['Record', 'key = "Mumbai"', 'value = "o11"', 'topic = city-orders'],
     ['Serialize', 'key → bytes 4d 75 6d …', 'value → bytes', 'Kafka stores only bytes'],
     ['Partitioner', 'murmur2 → 2542653612', '6 partitions → 4', '(was 1 with 3)'],
     ['Batch', 'added to batch for P4', 'sent after linger.ms', 'or when batch is full'],
     ['Leader append', 'leader of P4 appends', 'to its log segment', 'followers copy'],
     ['Offset', 'P4 was empty →', 'offset 0', 'returned to producer']],
    ['Record.', 'Bytes.', 'Hash.', 'Batch.', 'Append.', 'Offset.'], 'scenario-peel')

def five(kind, title, sub, cons, lines, caps, hid):
    fr = [t(180, 22, a, 9.4, 'acc' if i == 4 else 'ink', bold=True) + t(180, 56, b, 8.4, 'ink2') + cap(c, '', tone, y=150, h=34) for i, (a, b, c, tone) in enumerate(lines)]
    return anim_one(kind, title, sub, cons[0], cons[1], fr, caps, hid=hid)
s1 = five('Real-time scenario 1', 'The hot partition', 'Few keys overload one consumer. (Typical.)',
          ('Hot partitions', 'Choose high-cardinality keys so load spreads across partitions'), [
    ('Key = city', '6 cities, 12 partitions', 'Most partitions idle.', 'blue'),
    ('Mumbai has 40% of orders', 'one partition overloaded', 'Its consumer lags.', 'red'),
    ('Change key to order_id', 'millions of keys', 'Even spread.', 'green'),
    ('Order per order kept', 'which is what we need', 'City order not needed.', 'green'),
    ('Lag gone', 'all consumers busy', 'Key choice matters.', 'blue')],
    ['City key.', 'Hot.', 'Re-key.', 'Order OK.', 'Fixed.'], 'scenario-hot')
s2 = five('Real-time scenario 2', 'Out-of-order status after scaling', 'Adding partitions to a keyed topic. (Typical.)',
          ('Partition changes', 'Increasing partitions remaps keys; drain or migrate before changing'), [
    ('Need more consumers', 'alter 12 → 24 partitions', 'In the evening peak.', 'blue'),
    ('Order o9 PAID in P5', 'DELIVERED goes to P17', 'Different consumers.', 'red'),
    ('DELIVERED processed first', 'status regresses', 'Customer confused.', 'red'),
    ('Better plan', 'new topic with 24, switch over', 'Or pause, drain, alter.', 'green'),
    ('Rule', 'size partitions up front', 'Lesson 10.2.', 'blue')],
    ['Scale.', 'Split.', 'Wrong.', 'Plan.', 'Rule.'], 'scenario-remap')
s3 = five('Real-time scenario 3 · advanced', 'Python and Java producers disagree', 'Different default partitioners. (Typical.)',
          ('Partitioner compatibility', 'Use the same partitioner in all clients that write to one keyed topic'), [
    ('Java service writes o42', 'murmur2 → P3', 'Default Java.', 'blue'),
    ('Python service writes o42', 'librdkafka default → P7', 'CRC32 consistent.', 'red'),
    ('Same key, two partitions', 'ordering lost', 'Hard to spot.', 'red'),
    ('Set partitioner', 'murmur2_random in Python', 'Same as Java.', 'green'),
    ('Test it', 'compare partitions for keys', 'Like our murmur2.py.', 'blue')],
    ['Java.', 'Python.', 'Mismatch.', 'Fix.', 'Verify.'], 'scenario-partitioner')
animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Keys, hashes, offsets</h2>
  <p>Left: real lab output. Right: what decides where events go.</p>
''' + two + '''
  <p>Now peel the producer’s decision layer by layer.</p>
''' + PEEL + '''
  <p>Three live scenarios follow: a hot partition, a remap after scaling, and mixed clients.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

def uc_(word, sub, tone, title, desc, flow_):
    return usecase(f'<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-{tone}" style="stroke:var(--{tone if tone != "acc" else "track"})"/>' + t(60, 42, word, 11, tone, bold=True) + t(60, 58, sub, 7.4, 'ink2'), title, desc, flow_)
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Keys in practice</h2>
''' + '\n'.join([
    uc_('bank', 'account', 'blue', '1. Account transactions', 'Key = account id keeps each account’s debits and credits in order.', ['Txn', '*key account', 'Ordered ledger']),
    uc_('ride', 'trip', 'green', '2. Trip updates', 'Key = trip id keeps location and status updates of one trip in order.', ['GPS', '*key trip', 'Live map']),
    uc_('IoT', 'device', 'violet', '3. Device telemetry', 'Key = device id; millions of devices spread evenly.', ['Sensors', '*key device', 'Even load']),
    uc_('shop', 'cart', 'acc', '4. Shopping carts', 'Key = user id so add/remove events apply in order.', ['Clicks', '*key user', 'Cart state']),
    uc_('logs', 'no key', 'blue', '5. Application logs', 'No key: best spread, order not needed.', ['Logs', '*sticky', 'Search']),
]) + '''
  <p class="muted">Examples are simplified descriptions of common patterns.</p>
</section>
'''
pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> <a href="../03-kafka-architecture/">1.3 Architecture</a> (leaders and replicas).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
