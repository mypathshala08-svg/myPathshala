import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l23_batch.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('Waiting 5 milliseconds made our producer 40× faster. Why would waiting help?',
    'With <code>linger.ms=0</code> our 20,000 orders went out in 1,250 small batches and took 2.4 s. With <code>linger.ms=5</code> they went in 20 batches and took 0.06 s. Then compression shrank the stored data 10×. This lesson shows the batch on disk and every trade-off.',
    ['What a “batch” is and how big it can get.',
     'Which of gzip, snappy, lz4 and zstd won on our data, and what each costs.',
     'Where compression happens: producer, broker or consumer.'])
cmap = concept_map('Concept map. Beginner: batch, linger.ms, compression. Intermediate: batch.size, buffer memory, codecs and ratios, max request size. Advanced: broker-side compression.type, compression levels, end-to-end batching.',
    [[('ba', 'Batch', 'many records, 1 request', None), ('li', 'linger.ms', 'wait to fill', None), ('co', 'Compression', 'smaller bytes', None)],
     [('bs', 'batch.size', 'upper limit', None), ('bu', 'Buffer memory', 'Lesson 2.1', B + '02-producers/01-how-a-producer-sends-a-message/'), ('cd', 'Codecs', 'gzip snappy lz4 zstd', None), ('mr', 'max.request.size', 'record limits', None)],
     [('bc', 'Topic compression.type', 'producer or recompress', None), ('cl', 'compression levels', 'Kafka 3.8+', None), ('st', 'Segments on disk', 'Lesson 4.1', B + '04-storage-internals/01-the-commit-log-and-segments/')]],
    [('ba', 'bs'), ('li', 'bs'), ('co', 'cd'), ('ba', 'bu'), ('cd', 'bc'), ('cd', 'cl'), ('bs', 'st'), ('mr', 'bc')],
    {'ba', 'li', 'co', 'bs', 'cd', 'bc', 'cl'},
    '<b>Builds on:</b> <a href="../01-how-a-producer-sends-a-message/">2.1</a>. <b>Next:</b> <a href="../04-acks-and-durability/">2.4 acks and durability</a>.')
whw = why_how_where(
    'Every request has a fixed cost (network round trip, disk write, replication). Many tiny requests waste it; compression also saves disk and bandwidth.',
    'The producer collects records per partition until batch.size is reached or linger.ms passes, compresses the whole batch, and sends it. Brokers store the batch compressed; consumers decompress.',
    'High-volume topics: clicks, logs, orders at peak, CDC streams. JSON compresses especially well.',
    'Very latency-sensitive single events (keep linger small) and already-compressed payloads such as images (compression adds CPU, saves little).')

sc_ = (t(160, 18, 'linger.ms = 0', 9, 'red', bold=True) + ''.join(box(14 + (k % 20) * 14.5, 28 + (k // 20) * 14, 12, 10, 'red', rx=2) for k in range(60)) + t(160, 86, '1,250 tiny batches · 2.4 s', 8, 'ink2') +
       t(480, 18, 'linger.ms = 5', 9, 'green', bold=True) + ''.join(box(334 + (k % 10) * 29, 28 + (k // 10) * 26, 25, 22, 'green', rx=3) for k in range(20)) + t(480, 86, '20 big batches · 0.06 s', 8, 'ink2') +
       box(14, 100, 612, 30, 'card', rx=6) + t(320, 119, 'then compression on each batch: 2,268 KiB → 221 KiB (gzip) / 231 KiB (zstd)', 8.4, 'ink', bold=True))
scene_svg = scene('Left: with linger.ms 0, 20,000 orders went in 1,250 tiny batches taking 2.4 seconds. Right: with linger.ms 5, they went in 20 big batches taking 0.06 seconds. Compression then reduced the data from 2,268 KiB to about 221 KiB with gzip.', sc_,
                  'Small wait, <tspan font-weight="700" class="s-acc">big batches</tspan>, fewer bytes.')
dialogue = '''K> Sir, during the sale our producer used 100% network and the brokers were busy. But we only send small JSON orders.
A> How many requests? With <code>linger.ms=0</code> the producer sends as soon as it can, so you get thousands of tiny requests. Each one costs a round trip, a disk append and replication.
R> And if we wait a few milliseconds?
A> Batches fill up. One request carries hundreds of records, and compressing a big batch works much better than compressing one record. Let’s measure batches on disk and bytes for every codec.'''

lv = '''
LEVELS> Batching at three levels
L1> Shared auto-rickshaw
      <ul>
        <li>An auto that leaves with one passenger (linger 0) makes many trips. Waiting 5 seconds for 3 passengers saves fuel and the road. Packing luggage tightly (compression) fits more in each trip.</li>
      </ul>
L2> The settings
      <ul>
        <li><b>linger.ms</b>: maximum time to wait for more records (Java default 5 ms since Kafka 4.0, librdkafka 5 ms).</li>
        <li><b>batch.size</b>: maximum bytes per partition batch (Java 16 KB; librdkafka <code>batch.size</code> 1 MB and <code>batch.num.messages</code> 10,000). A batch is sent when full <i>or</i> when linger expires.</li>
        <li><b>compression.type</b>: <code>none</code>, <code>gzip</code>, <code>snappy</code>, <code>lz4</code>, <code>zstd</code>. The whole batch is compressed as one unit.</li>
      </ul>
L3> Where compression happens
      <ul>
        <li>The topic config <code>compression.type</code> defaults to <code>producer</code>: the broker stores the producer’s compressed batch as is (it still validates it). If the topic sets a different codec, the broker <b>recompresses</b>, which costs broker CPU.</li>
        <li>Consumers decompress. Since Kafka 3.8 you can also set <code>compression.gzip.level</code>, <code>compression.lz4.level</code>, <code>compression.zstd.level</code> (KIP-390).</li>
        <li>Bigger batches also raise per-record latency slightly and use more producer memory; <code>max.request.size</code> (1 MB) and the broker’s <code>message.max.bytes</code> cap one batch.</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of a compressed record batch on disk: one batch header with base offset, record count, compression codec and CRC, followed by many records compressed together into one block.',
    t(16, 22, 'One record batch on disk (as kafka-dump-log describes it)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('baseOffset: 0', 'blue', 1), ('count: 1000', 'blue', 2), ('compresscodec: zstd', 'violet', 3), ('crc ✓', 'card', 4), ('size: ~11 KB', 'amber', 5)]) +
    box(16, 70, 600, 30, 'violet', rx=4) + t(316, 89, '[ record 0 | record 1 | record 2 | … | record 999 ]   compressed together as ONE block', 8, 'ink', mono=True) + pin(18, 68, 6) +
    legend(16, 128, [(1, 'Base offset', 'first offset in the batch; records store small deltas'),
                     (2, 'Count', 'how many records travelled together'),
                     (3, 'Codec', 'chosen by the producer; stored as is when topic uses producer'),
                     (4, 'CRC', 'checksum verified by brokers and consumers'),
                     (5, 'Size', 'what the network and disk really carry'),
                     (6, 'One block', 'repeated JSON keys compress very well across records')], size=8, gap=15, w=110),
    h=232, caption='Structure from Kafka’s record batch format (magic v2); sizes illustrative.')
extra = '''

  <h3>Dissect a compressed batch</h3>
''' + DIS

types_html = table(['Codec', 'Our ratio (vs none)', 'CPU', 'Typical use'], [
    ['none', '1.0×', 'none', 'already-compressed data, tiny topics'],
    ['gzip', '10.3×', 'highest', 'best ratio when CPU is cheap'],
    ['snappy', '5.5×', 'low', 'older default in many pipelines'],
    ['lz4', '4.9×', 'very low', 'low latency, high throughput'],
    ['zstd', '9.8×', 'medium', 'modern default choice: near-gzip ratio, faster'],
], minw=560) + table(['Setting', 'Raise it when', 'Lower it when'], [
    ['linger.ms', 'throughput matters, many small records', 'each event must leave immediately'],
    ['batch.size', 'records are big or rate is high', 'memory is tight'],
    ['compression', 'JSON/text, network or disk bound', 'payload already compressed, CPU bound'],
], minw=560)
warn = 'Ratios depend on your data. Our orders are repetitive JSON, which compresses very well; random or encrypted data barely compresses. Measure with your own messages. Also, setting a topic’s <code>compression.type</code> to a codec different from the producer’s forces the broker to decompress and recompress every batch.'

steps = [
    ('Step 1 · The payload',
     code('python', 'l23_batch.py', 'events = [json.dumps({"order_id": f"o{i:06d}", "city": random.choice(cities),\n          "items": [...], "amount": ..., "status": "PLACED"}) for i in range(20000)]', sec('== payload', '== 1)')),
     '20,000 realistic JSON orders. On disk each record also carries its key, offset delta, timestamp delta and headers.'),
    ('Step 2 · linger.ms: 0 vs 5 vs 50',
     code('python', 'l23_batch.py', 'for lg in (0, 5, 50):\n    run(f"linger-{lg}", {"linger.ms": lg, "compression.type": "none"})\n# batches counted with kafka-dump-log on every partition', sec('== 1)', '== 2)')),
     'With no waiting the producer sent 1,250 batches of about 16 records and needed 2.4 s. Waiting just 5 ms gave 20 batches of 1,000 records and 0.06 s. 50 ms changed little more: the gain comes from the first few milliseconds.'),
    ('Step 3 · Five codecs',
     code('python', 'l23_batch.py', 'for c in ("none", "gzip", "snappy", "lz4", "zstd"):\n    run(f"comp-{c}", {"linger.ms": 50, "compression.type": c})\n# size = du -cb of the partitions\' .log files on the broker', sec('== 2)')),
     'gzip and zstd shrank the log about 10×, snappy and lz4 about 5×. Times are all tiny here; at large scale gzip costs the most producer CPU, lz4 the least, zstd sits between with a ratio close to gzip.'),
]

see = [term([('20,000 JSON orders, 1967 KiB of values', W)], size=7.4),
       term([('linger.ms=0   batches 1250   2.40 s', RD), ('linger.ms=5   batches   20   0.06 s', G), ('linger.ms=50  batches    3   0.04 s', G)], size=7.0),
       term([('none   2268 KiB', W), ('gzip    221 KiB  10.3x', G), ('snappy  413 KiB   5.5x', W), ('lz4     458 KiB   4.9x', W), ('zstd    231 KiB   9.8x', G)], size=7.0)]
B1 = [t(180, 14, 'Records waiting per partition', 9, bold=True) + ''.join(pcol(60, 34 + k * 26, f'P{k}', ['o'] * 5, 'card', cw=22, ch=18) for k in range(3)) + cap('Accumulator fills batches.', '', 'blue', y=144, h=30),
      t(180, 14, 'Fewer, bigger requests', 9, bold=True) + ''.join(box(20 + k * 7, 40, 5, 30, 'red', rx=1) for k in range(40)) + t(170, 86, '1,250 requests', 8, 'red') + ''.join(box(20 + k * 16, 100, 13, 30, 'green', rx=2) for k in range(20)) + t(350, 120, '20', 8, 'green', anchor='end') + cap('Same data, 60× fewer batches.', '', 'green', y=144, h=30),
      t(180, 14, 'Bytes stored', 9, bold=True) + ''.join(box(40, 34 + k * 20, 260 * v / 2268, 14, 'red' if k == 0 else 'green', rx=2) + t(46 + 260 * v / 2268, 45 + k * 20, f'{n} {v}', 7, 'ink', anchor='start') for k, (n, v) in enumerate([('none', 2268), ('gzip', 221), ('snappy', 413), ('lz4', 458), ('zstd', 231)])) + cap('Compress the whole batch.', '', 'green', y=144, h=30)]
two = anim_two('Batching and compression', 'Wait a little, send a lot', 'Real outputs from the lab', 'What changed', see, B1, ['Payload.', 'Batches.', 'Codecs.'], ['Accumulate.', 'Requests.', 'Bytes.'])
pe = peel('One batch, from memory to disk to consumer', 'Where bytes are compressed and decompressed. (Default topic setting.)',
    [('Accumulator', ''), ('Batch ready', ''), ('Compress', ''), ('Broker', ''), ('Disk', ''), ('Consumer', '')],
    [['Accumulator', 'records for P1 collect', 'in one batch', ''], ['Batch ready', 'batch.size reached', 'or linger.ms passed', ''],
     ['Compress', 'producer compresses', 'the whole batch (zstd)', 'CPU on the producer'], ['Broker', 'validates CRC, offsets', 'topic compression.type', '= producer: no recompress'],
     ['Disk', 'stored compressed', '~10× less disk', 'and replication traffic'], ['Consumer', 'fetches compressed batch', 'decompresses locally', 'CPU on the consumer']],
    ['Collect.', 'Trigger.', 'Compress.', 'Validate.', 'Store.', 'Decompress.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Network maxed out at peak', 'Too many tiny requests. (Typical.)', ('linger.ms', 'A few milliseconds of linger turn thousands of requests into a few'), [
    ('Sale: 50k orders/s', 'linger.ms=0 in old config', 'Requests explode.', 'red'), ('Broker CPU 90%', 'network busy', 'Latency rises.', 'red'),
    ('Set linger.ms=10', 'and compression=zstd', 'Config only.', 'green'), ('Requests drop', 'bytes drop ~10×', 'Headroom.', 'green'),
    ('Latency still low', 'a few ms added', 'Good trade.', 'blue')], ['Peak.', 'Busy.', 'Tune.', 'Relief.', 'Trade-off.'], 'scenario-linger') + \
       five('Real-time scenario 2', 'Broker CPU spike after a config change', 'Mismatched codecs. (Typical.)', ('Broker recompression', 'Keep topic compression.type=producer unless you need one codec'), [
    ('Admin sets topic gzip', 'producers send lz4', 'Looks harmless.', 'blue'), ('Broker recompresses', 'every batch', 'CPU spike.', 'red'),
    ('Throughput drops', 'produce latency up', 'Incident.', 'red'), ('Revert to producer', 'or align producers', 'One codec.', 'green'),
    ('Rule', 'compress at the edge', 'Producer side.', 'blue')], ['Change.', 'Recompress.', 'Impact.', 'Revert.', 'Rule.'], 'scenario-recompress') + \
       five('Real-time scenario 3 · advanced', 'RecordTooLarge', 'A huge batch or record. (Typical.)', ('Size limits', 'max.request.size, message.max.bytes and fetch sizes must agree'), [
    ('Menu images as values', '3 MB records', 'Rejected.', 'red'), ('Error: too large', 'non-retriable', 'Lost if ignored.', 'red'),
    ('Store image in object storage', 'send a link in Kafka', 'Claim-check.', 'green'), ('Or raise limits carefully', 'producer, broker, consumer', 'All three.', 'amber'),
    ('Keep events small', 'KBs, not MBs', 'Best practice.', 'blue')], ['Big.', 'Error.', 'Pointer.', 'Limits.', 'Small.'], 'scenario-size')
assemble(HERE, h2_story='Why waiting made us faster', hook_html=hk,
    narration='During TiffinGo’s Diwali sale the order producer was pinned at 100% network and brokers were busy, although each order is only ~100 bytes of JSON. Kabir suspects the producer settings.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Batching and compression',
    formal='The producer groups records destined for the same partition into a <b>record batch</b>. A batch is sent when it reaches <b>batch.size</b> bytes or when <b>linger.ms</b> has elapsed since its first record, whichever is first; multiple batches for the same broker travel in one Produce request. If <b>compression.type</b> is set, the producer compresses each batch as a unit (gzip, snappy, lz4 or zstd); brokers store batches in compressed form (recompressing only if the topic’s compression.type differs from the producer’s), and consumers decompress on read.',
    simple='The producer waits a tiny moment to collect records into a group, squeezes the group with compression, and sends it in one go. Kafka stores the group squeezed, and readers unsqueeze it.',
    term_rows=[('Record batch', 'Records sent and stored together.'), ('linger.ms', 'Wait time to fill a batch.'), ('batch.size', 'Maximum batch bytes.'), ('compression.type', 'Codec for batches.'), ('zstd', 'Modern codec, high ratio.'), ('lz4', 'Very fast codec.'), ('Recompression', 'Broker changes codec (costly).'), ('max.request.size', 'Largest request a producer sends.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Kafka compresses each message separately.', 'The whole batch is compressed as one block.', 'Step 3: 10× smaller because repeated JSON fields compress across records.'),
               ('linger.ms always adds noticeable delay.', 'A few ms often makes total throughput far higher.', 'Step 2: 2.4 s → 0.06 s with linger 5 ms.'),
               ('Brokers decompress and store raw data.', 'With compression.type=producer they store the compressed batch.', 'dump-log shows compresscodec per batch.')],
    exam='“How do you increase producer throughput?” Increase linger.ms and batch.size so batches fill, enable compression (zstd/lz4), keep acks/idempotence for safety, use enough partitions, and keep topic compression.type=producer to avoid broker recompression.',
    types_h2='Codecs and settings compared', types_html=types_html, warn=warn,
    steps_h2='Batches and bytes, measured', steps_intro='All outputs are real: Kafka 4.4.0 (3 brokers), Python <code>confluent-kafka</code> 2.16.1, topics with 3 partitions and RF 3. Batches counted with <code>kafka-dump-log.sh</code>, bytes with <code>du</code> on the broker. Script: <code>jobs/m2/l23_batch.py</code>.',
    steps=steps, two=two, peel_intro='Now peel one batch from memory to the consumer.', peel_html=pe,
    scen_intro='Three live scenarios: a saturated network, broker recompression and oversized records.', scen=scen,
    uc_h2='Batching at work', ucs=[uc_('logs', 'agents', 'blue', '1. Log pipelines', 'Big batches + lz4/zstd: terabytes per day with modest hardware.', ['Logs', '*batch + zstd', 'Cheap']),
        uc_('click', 'stream', 'green', '2. Clickstreams', 'Millions of small JSON events compress ~10×.', ['Clicks', '*compress', 'Less disk']),
        uc_('CDC', 'DB changes', 'violet', '3. Database change streams', 'Large bursts during bulk updates are smoothed by batching.', ['DB', '*batch', 'Kafka']),
        uc_('pay', 'low lat', 'acc', '4. Payments', 'Small linger keeps latency low; lz4 adds little CPU.', ['Payment', '*linger 1–5 ms', 'Fast']),
        uc_('IoT', 'edge', 'blue', '5. Edge devices', 'Compression saves expensive mobile bandwidth.', ['Device', '*gzip', 'Less data'])],
    uc_note='Ratios and timings depend on data and hardware; ours are from the lab.',
    pre='<b>Before you start:</b> <a href="../01-how-a-producer-sends-a-message/">2.1 How a producer sends a message</a>.')
