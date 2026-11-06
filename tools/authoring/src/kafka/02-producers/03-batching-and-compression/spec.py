import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
BODY = body(HERE)
META = dict(module='02-producers', lesson='03-batching-and-compression', n='2.3', module_label='Module 2 · Producers',
    title='Batching and compression',
    desc='How Kafka producers batch records (linger.ms, batch.size) and compress batches (gzip, snappy, lz4, zstd), where the broker stores or recompresses them, and the size limits. Real Kafka 4.4 lab with 20,000 JSON orders: 1,250 batches and 2.4 s with linger.ms=0 vs 20 batches and 0.06 s with 5 ms; on-disk size 2,268 KiB uncompressed vs 221 KiB gzip and 231 KiB zstd.',
    og_desc='linger.ms=5 turned 1,250 batches into 20; zstd shrank the log ~10×. Kafka batching and compression, measured.',
    minutes=24, level='Intermediate',
    lead='A few milliseconds of waiting and the right codec can make a producer many times faster and the log 10× smaller. We count real <b>batches on disk</b> and measure <b>five codecs</b> on 20,000 orders. <b>All outputs are real.</b>',
    chips=['1,250 → 20 batches', '5 codecs measured', 'Broker recompression', 'Runs in your browser (Python)'])
MAIN = '''# Why compressing a batch beats compressing each record
import json, zlib, random
random.seed(3)
cities = ["Mumbai", "Pune", "Delhi", "Bengaluru", "Chennai"]
orders = [json.dumps({"order_id": f"o{i:06d}", "city": random.choice(cities),
                      "amount": random.choice([120, 180, 250, 480]), "status": "PLACED"})
          for i in range(1000)]
raw = sum(len(o) for o in orders)
one_by_one = sum(len(zlib.compress(o.encode())) for o in orders)   # each record alone
as_batch = len(zlib.compress("".join(orders).encode()))             # whole batch
print("raw bytes      :", raw)
print("each record    :", one_by_one, f"({raw / one_by_one:.1f}x)")
print("one batch      :", as_batch, f"({raw / as_batch:.1f}x)")
'''
RUN = dict(heading='Run the code: batch vs single compression', intro='<p>gzip’s algorithm (zlib) on 1,000 orders. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('one_by_one = sum(len(zlib.compress(o.encode())) for o in orders)   # each record alone', 'Small inputs barely compress (and can grow).'),
          ('as_batch = len(zlib.compress("".join(orders).encode()))             # whole batch', 'Repeated field names across records compress very well.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Then try 100 and 10,000 orders.', code=None),
        dict(label='2 · Predict first: batches', hint='<b>Predict first:</b> 20,000 records, 1,000 per batch?', code='print(20000 // 1000)\n'),
        dict(label='3 · Requests saved', hint='1,250 vs 20 batches.', code='print(1250 / 20, "x fewer")\n'),
        dict(label='4 · Disk per day', hint='2 GB/day raw, 10x compression, RF 3.', code='print(2 / 10 * 3, "GB/day on the cluster")\n'),
        dict(label='5 · Spot the error', hint='A 3 MB record with a 1 MB limit.', expect='error', code='record, limit = 3_000_000, 1_048_576\nif record > limit:\n    raise ValueError("RECORD_TOO_LARGE: message is larger than max.request.size")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: tune and measure', intro='<p>Python and the perf tool. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Producer config', cmd='Producer({"bootstrap.servers": "localhost:9092", "linger.ms": 5, "compression.type": "zstd"})', file='python', output='20 batches instead of 1,250', note='Step 2.'),
           dict(title='2 · Count batches', cmd='kafka-dump-log.sh --files /var/lib/kafka/data/linger-5-0/00000000000000000000.log | grep -c baseOffset', file='terminal', output='6', note='One partition of three.'),
           dict(title='3 · Bytes on disk', cmd='du -cb /var/lib/kafka/data/comp-zstd-[0-9]/*.log | tail -1', file='terminal', output='236127\ttotal', note='≈ 231 KiB.')])
TRACE = dict(heading='When is a batch sent?', intro='<p>Full or timed out, whichever first.</p>',
    code='batch, size_limit, linger = [], 4, 5\nfor t, rec in enumerate(["a", "b", "c", "d", "e"]):\n    batch.append(rec)\n    if len(batch) == size_limit or t >= linger:\n        print("send", batch)\n        batch = []\nprint("left", batch)\n',
    notes={4: 'Trigger :: Size limit or linger time.', 7: 'Pending :: Waits for the next trigger.'})
WORKED_INTRO = 'Three tuning decisions.'
EXAMPLES = [
    dict(level='b', tag='Producer · tuning', title='Throughput profile', problem='<p>Logs: max throughput, latency not critical.</p>', inp='settings',
         approach=['linger.ms 20–50.', 'Bigger batch.size.', 'zstd or lz4.'], code='print({"linger.ms": 50, "batch.size": 262144, "compression.type": "zstd"})\n', notes={1: 'Throughput :: Fewer, bigger, compressed batches.'}, tryit='Step 2.'),
    dict(level='i', tag='Producer · tuning', title='Latency profile', problem='<p>Payments: fast acknowledgements.</p>', inp='settings',
         approach=['linger.ms 0–5.', 'lz4 (cheap CPU).', 'Keep acks=all.'], code='print({"linger.ms": 2, "compression.type": "lz4", "acks": "all"})\n', notes={1: 'Latency :: Small linger, fast codec.'}, tryit='Types table.'),
    dict(level='a', tag='Producer · cost', title='Estimate savings', problem='<p>Cluster stores 5 TB/day uncompressed with RF 3.</p>', inp='ratio 9.8',
         approach=['Divide by ratio.', 'Multiply by RF.', 'Compare.'], code='raw, ratio, rf = 5, 9.8, 3\nprint(raw * rf, "TB ->", round(raw / ratio * rf, 2), "TB per day")\n', notes={1: 'Money :: Disk and network shrink together.'}, tryit='Step 3.')]
QUIZ = mix([
    dict(q='Beginner: linger.ms controls…', options=['Retention', 'How long to wait to fill a batch', 'Replication', 'Consumer speed'], answer=1, why='Then send.'),
    dict(q='Beginner: Kafka compresses…', options=['Each record alone', 'The whole batch', 'Only keys', 'Nothing'], answer=1, why='One block.'),
    dict(q='Beginner: Which codec had the best ratio in our lab?', options=['lz4', 'gzip', 'snappy', 'none'], answer=1, why='10.3×; zstd 9.8×.'),
    dict(q='Intermediate: linger.ms=0 vs 5 on 20,000 orders gave…', options=['Same batches', '1,250 vs 20 batches', '20 vs 1,250', '1 vs 1'], answer=1, why='Step 2.'),
    dict(q='Intermediate: A batch is sent when…', options=['Only when full', 'Full or linger.ms passed', 'Every second', 'On consume'], answer=1, why='Whichever first.'),
    dict(q='Intermediate: Topic compression.type default is…', options=['gzip', 'producer', 'none', 'zstd'], answer=1, why='Keep the producer’s codec.'),
    dict(q='Advanced: Topic codec differs from producer codec. Result?', options=['Faster', 'Broker recompresses (CPU)', 'Error', 'Data loss'], answer=1, why='Avoid.'),
    dict(q='Advanced: Compression levels per codec arrived in…', options=['Kafka 0.8', 'Kafka 3.8 (KIP-390)', 'Never', 'Kafka 1.0'], answer=1, why='compression.zstd.level etc.')])
REVISION = ['Batch per partition; sent when batch.size full or linger.ms passes.', 'Lab: linger 0 → 1,250 batches 2.4 s; linger 5 → 20 batches 0.06 s.',
    'Codecs: none 2,268 KiB; gzip 221 (10.3×); snappy 413; lz4 458; zstd 231 (9.8×).', 'Whole batch compressed; broker stores as is (compression.type=producer); consumer decompresses.',
    'Limits: max.request.size, message.max.bytes; keep events small.']
FAQ = [('Which codec should I choose?', 'zstd is a good default for ratio and speed; lz4 when CPU or latency is tight; gzip only if the ratio matters most.'),
    ('Does compression increase latency?', 'Slightly (CPU), but smaller batches travel and replicate faster, so end-to-end latency often stays similar or improves.'),
    ('Does batching break ordering?', 'No. Records within a partition stay in order inside and across batches (with idempotence even on retries).'),
    ('Can consumers read compressed data?', 'Yes, all official clients decompress automatically.')]
PRACTICE_INTRO = 'Batching and compression programs.'
PROBLEMS = [
    dict(level='easy', title='Records per batch', stmt='20,000 records in 20 batches.', inp='numbers', code='print(20000 / 20)\n', explain='1,000.'),
    dict(level='easy', title='Ratio', stmt='2,268 KiB vs 231 KiB.', inp='sizes', code='print(round(2268 / 231, 1))\n', explain='9.8×.'),
    dict(level='easy', title='Speed-up', stmt='2.4 s vs 0.06 s.', inp='times', code='print(2.4 / 0.06)\n', explain='40×.'),
    dict(level='medium', title='Batch trigger', stmt='Which comes first: 16 KB at 100 B/record and 1,000 rec/s, or 5 ms?', inp='rates', code='full_ms = 16384 / 100 / 1000 * 1000\nprint(round(full_ms), "ms to fill ->", "linger" if full_ms > 5 else "size")\n', explain='Linger triggers.'),
    dict(level='medium', title='Network saved', stmt='Bytes saved per day at 10× on 50 GB.', inp='50 GB', code='print(50 - 50 / 10, "GB")\n', explain='45 GB.'),
    dict(level='medium', title='Pick a codec', stmt='Pick by priority.', inp='priority', code='prio = "cpu"\nprint({"ratio": "gzip", "cpu": "lz4", "balanced": "zstd"}[prio])\n', explain='Trade-offs.'),
    dict(level='business', title='Disk cost', stmt='Save 13.5 TB/day at Rs 2 per GB per month for 7 days retention.', inp='numbers', code='print("Rs", round(13.5 * 1024 * 7 * 2 / 30))\n', explain='Rough monthly saving.'),
    dict(level='business', title='Request count', stmt='Requests/s for 50k orders/s at 1,000 per batch.', inp='rates', code='print(50000 // 1000)\n', explain='50 vs 50,000.')]
SCN_INTRO = 'Throughput interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“What do linger.ms and batch.size do?”', 'Explain.', 'answer?', '<p>The producer batches records per partition; a batch is sent when it reaches batch.size or after linger.ms. Bigger batches mean fewer requests and better compression, at a small latency cost.</p>', '“They limit retention.”') +
    scn('Data engineering', 'Mid-level', 'Slow producer', 'A producer sends 20k msgs/s and the network is saturated.', 'tune?', '<ul><li>linger.ms 5–20, larger batch.size.</li><li>compression zstd/lz4.</li><li>Check partitions and acks.</li></ul>', 'Turning off acks.') +
    scn('Platform', 'Mid-level', 'Broker CPU', 'Broker CPU rose after a topic config change.', 'cause?', '<ul><li>Topic compression.type differs from producers.</li><li>Broker recompresses.</li><li>Set producer or align.</li></ul>', 'Adding brokers only.') +
    scn('Platform', 'Senior', 'Large payloads', 'Teams want to send 5 MB documents.', 'design?', '<ul><li>Claim-check: store in object storage, send a reference.</li><li>If needed, raise limits consistently.</li><li>Compress.</li></ul>', 'Raising only the producer limit.'))
