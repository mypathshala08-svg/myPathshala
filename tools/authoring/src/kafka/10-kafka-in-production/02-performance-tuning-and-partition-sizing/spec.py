import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='10-kafka-in-production', lesson='02-performance-tuning-and-partition-sizing', n='10.2', module_label='Module 10 · Kafka in production',
    title='Performance tuning and partition sizing',
    desc='A measured approach to Kafka performance: producer batch.size, linger.ms, compression and acks; consumer fetch settings and parallelism; broker threads, disks and page cache; and partition sizing from measured per-partition throughput and consumer parallelism. Real Kafka 4.4 lab with perf-test tools: batching raised throughput from 16 to 64 MB/s, 12 partitions beat 1, and two popular tweaks did not help.',
    og_desc='16 → 64 MB/s with one change; lz4 and big fetches did not help. Measured Kafka 4.4 tuning.',
    minutes=22, level='Advanced',
    lead='How do you make Kafka faster without guessing? We change <b>one setting at a time</b> with the perf-test tools and size <b>partitions</b> with arithmetic. <b>All outputs are real.</b>',
    chips=['16 → 64 MB/s', '1 vs 12 partitions', 'Not every tweak helps', 'Runs in your browser (Python)'])
MAIN = '''# Partition sizing from measured rates
import math
target_mb_s = 60
produce_per_partition = 10     # measured MB/s
consume_per_partition = 5      # measured MB/s
consumers_wanted = 8
growth = 1.5                   # plan for 18 months

need = max(target_mb_s * growth / produce_per_partition,
           target_mb_s * growth / consume_per_partition,
           consumers_wanted)
print("partitions:", math.ceil(need))
'''
RUN = dict(heading='Run the code: size partitions', intro='<p>The sizing formula. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('need = max(target_mb_s * growth / produce_per_partition,', 'Take the largest need.'), ('growth = 1.5                   # plan for 18 months', 'Adding partitions later remaps keys.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Set consumers_wanted = 30.', code=None),
        dict(label='2 · Predict first: gain', hint='<b>Predict first:</b> 64.37 ÷ 16.08.', code='print(round(64.37 / 16.08, 1))\n'),
        dict(label='3 · Batch count', hint='200,000 KB in 16 KB vs 256 KB batches.', code='print(200000 // 16, 200000 // 256)\n'),
        dict(label='4 · Replication load', hint='60 MB/s in, RF 3.', code='print(60 * 2, "MB/s follower traffic")\n'),
        dict(label='5 · Spot the error', hint='Missing bootstrap.', expect='error', code='raise ValueError("Missing required configuration \\"bootstrap.servers\\" which has no default value.")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: perf tests', intro='<p>Needs the lab. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Producer', cmd='kafka-producer-perf-test.sh --topic perf-12p --num-records 200000 --record-size 1000 --throughput -1 --producer-props bootstrap.servers=k1:9092 acks=all batch.size=262144 linger.ms=20', file='terminal', output='67499.156261 records/sec (64.37 MB/sec), 211.52 ms avg latency', note='Tuned.'),
           dict(title='2 · Consumer', cmd='kafka-consumer-perf-test.sh --bootstrap-server k1:9092 --topic perf-12p --messages 200000 --group perf-1', file='terminal', output='', note='MB/s, msg/s.')])
TRACE = dict(heading='Requests step by step', intro='<p>Bigger batches, fewer requests.</p>',
    code='records_kb = 200000\nfor batch_kb in (16, 256):\n    print(batch_kb, "KB batches ->", records_kb // batch_kb, "batches")\n',
    notes={3: 'Fewer :: 12,500 vs 781.'})
WORKED_INTRO = 'Three tuning decisions.'
EXAMPLES = [
    dict(level='b', tag='Tune · method', title='Where to start', problem='<p>Throughput too low.</p>', inp='method',
         approach=['Baseline perf-test.', 'Check broker idle %.', 'Change one knob.'], code='print(["baseline", "find bottleneck", "one change", "measure"])\n', notes={1: 'Method :: Repeatable.'}, tryit='Steps.'),
    dict(level='i', tag='Tune · producer', title='High-throughput producer', problem='<p>Logs pipeline, latency less important.</p>', inp='config',
         approach=['batch.size 256 KB.', 'linger.ms 20–50.', 'compression zstd; measure.'], code='print({"batch.size": 262144, "linger.ms": 20, "compression.type": "zstd"})\n', notes={1: 'Trade :: Latency for throughput.'}, tryit='Step 1.'),
    dict(level='a', tag='Tune · partitions', title='Partition count', problem='<p>New 60 MB/s topic, 8 consumers.</p>', inp='numbers',
         approach=['Measure per-partition rates.', 'max(6, 12, 8) = 12.', 'Add growth headroom.'], code='print(max(60 // 10, 60 // 5, 8))\n', notes={1: 'Formula :: Figure.'}, tryit='Run code.')]
QUIZ = mix([
    dict(q='Beginner: The biggest gain in our lab came from…', options=['Compression', 'batch.size + linger', 'More consumers', 'acks=0'], answer=1, why='4×.'),
    dict(q='Beginner: Kafka 4.x default linger.ms is…', options=['0', '5', '100', '1000'], answer=1, why='Changed in 4.0.'),
    dict(q='Beginner: Tools to measure…', options=['ping', 'kafka-*-perf-test', 'top', 'curl'], answer=1, why='Built in.'),
    dict(q='Intermediate: lz4 lowered throughput because…', options=['It is broken', 'CPU was the bottleneck on one VM', 'Disk full', 'acks'], answer=1, why='Measure.'),
    dict(q='Intermediate: 12 partitions beat 1 because…', options=['Compression', 'Parallel leaders and batches', 'Smaller records', 'ACLs'], answer=1, why='Parallelism.'),
    dict(q='Intermediate: Bigger fetches did not help since…', options=['Wrong syntax', 'One consumer thread was the limit', 'Topic empty', 'TLS'], answer=1, why='Step 3.'),
    dict(q='Advanced: Adding partitions later…', options=['Is free', 'Changes key → partition mapping', 'Deletes data', 'Needs ZooKeeper'], answer=1, why='Plan ahead.'),
    dict(q='Advanced: Kafka relies heavily on…', options=['JVM heap for data', 'OS page cache', 'Swap', 'GPU'], answer=1, why='Leave RAM for it.')])
REVISION = ['Method: baseline → bottleneck → one change → measure.', 'Lab: 16.08 → 64.37 MB/s (batch+linger); lz4 53.07; 1p 40.41 vs 12p 62.60; fetch no gain.',
    'Producer: batch.size, linger.ms, compression, acks; consumer: fetch.*, parallelism.', 'Broker: threads, disks, page cache.', 'Partitions = max(MB/s ÷ rates, consumers) × growth; too many cost.']
FAQ = [('Is acks=1 a tuning knob?', 'It lowers latency but risks data loss; tune batching first and keep acks=all for important data.'),
    ('How big should the JVM heap be?', 'Often 6–8 GB for brokers; leave the rest of RAM to the page cache.'),
    ('Which compression is best?', 'zstd usually compresses best, lz4 is fastest; measure with your data.'),
    ('Can I reduce partitions?', 'No; you must create a new topic and migrate.')]
PRACTICE_INTRO = 'Tuning programs.'
PROBLEMS = [
    dict(level='easy', title='Gain', stmt='62.60 vs 40.41 MB/s.', inp='floats', code='print(round(62.60 / 40.41, 2))\n', explain='1.55×.'),
    dict(level='easy', title='Batches', stmt='1 MB data in 64 KB batches.', inp='ints', code='print(1024 // 64)\n', explain='16.'),
    dict(level='easy', title='Partitions', stmt='30 MB/s at 5 MB/s each.', inp='ints', code='print(30 // 5)\n', explain='6.'),
    dict(level='medium', title='Sizing', stmt='Formula with growth 2.', inp='ints', code='import math\nprint(math.ceil(max(40 * 2 / 10, 40 * 2 / 8, 6)))\n', explain='10.'),
    dict(level='medium', title='Pick best', stmt='Best run.', inp='dict', code='r = {"defaults": 16.08, "batch": 64.37, "lz4": 53.07}\nprint(max(r, key=r.get))\n', explain='batch.'),
    dict(level='medium', title='Replica count', stmt='12 partitions RF 3 on 3 brokers.', inp='ints', code='print(12 * 3 // 3, "replicas per broker")\n', explain='12.'),
    dict(level='business', title='Brokers saved', stmt='CPU −40% on 10 brokers.', inp='ints', code='print(10 - round(10 * 0.6))\n', explain='~4.'),
    dict(level='business', title='Daily data', stmt='60 MB/s for a day.', inp='ints', code='print(round(60 * 86400 / 1024 / 1024, 2), "TB")\n', explain='~4.9 TB.')]
SCN_INTRO = 'Tuning interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“How do you increase producer throughput?”', 'Explain.', 'answer?', '<p>Batch more: raise batch.size and linger.ms, enable compression if CPU allows, use enough partitions, and measure with kafka-producer-perf-test.</p>', '“acks=0 always.”') +
    scn('Platform', 'Mid-level', 'How many partitions?', 'New topic.', 'answer?', '<ul><li>max(throughput ÷ per-partition rates, consumer count).</li><li>Headroom, not 1,000.</li></ul>', 'As many as possible.') +
    scn('Platform', 'Mid-level', 'Consumer slow', 'Lag grows.', 'fix?', '<ul><li>More consumers up to partitions.</li><li>Faster processing, batching writes.</li></ul>', 'Bigger fetch only.') +
    scn('Platform', 'Senior', 'p99 high', 'Produce p99 500 ms.', 'diagnose?', '<ul><li>Client queue time vs broker queue time.</li><li>Threads, disk, replication.</li></ul>', 'Add brokers blindly.'))
