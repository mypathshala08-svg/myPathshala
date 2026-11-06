import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l102_perf.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('Same cluster, same data, same acks=all. One setting change took the producer from 16 MB/s to 64 MB/s. Which one, and why did compression make it slower?',
    'Bigger <b>batches</b> and a little <b>linger</b>: 16.1 → 64.4 MB/s and average latency 1,727 → 212 ms. Then lz4 compression <i>lowered</i> throughput to 53 MB/s on our CPU-bound single VM, and bigger consumer fetches did not help either. Tuning is about finding <b>your</b> bottleneck, so we measure each change one at a time and size partitions with arithmetic, not guesses.',
    ['A method: find the bottleneck, change one thing, measure.',
     'Producer, broker and consumer settings that matter.',
     'How many partitions, and what too many costs.'])
cmap = concept_map('Concept map. Beginner: throughput, latency, perf-test tools. Intermediate: batching, linger, compression, fetch sizes, partitions. Advanced: partition sizing, broker threads, OS page cache, trade-offs and limits.',
    [[('bt', 'Batching + compression', 'Lesson 2.3', B + '02-producers/03-batching-and-compression/'), ('mn', 'Monitoring', 'Lesson 10.1', B + '10-kafka-in-production/01-monitoring-and-consumer-lag/')],
     [('pt', 'Perf-test tools', 'measure', None), ('pr', 'Producer knobs', 'batch, linger, acks', None), ('cn', 'Consumer knobs', 'fetch, poll', None), ('pa', 'Partitions', 'parallelism', None)],
     [('sz', 'Partition sizing', 'MB/s ÷ per-partition', None), ('br', 'Broker threads + OS', 'io/network, page cache', None), ('tr', 'Trade-offs', 'latency vs throughput', None), ('zc', 'Zero-copy', 'Lesson 4.4', B + '04-storage-internals/04-tiered-storage-and-zero-copy/')]],
    [('bt', 'pr'), ('mn', 'pt'), ('pt', 'pr'), ('pt', 'cn'), ('pr', 'pa'), ('pa', 'sz'), ('cn', 'br'), ('pr', 'tr'), ('br', 'zc')],
    {'pt', 'pr', 'cn', 'pa', 'sz', 'br', 'tr'},
    '<b>Builds on:</b> <a href="../../02-producers/03-batching-and-compression/">2.3</a>, <a href="../01-monitoring-and-consumer-lag/">10.1</a>. <b>Next:</b> <a href="../03-security-tls-sasl-and-acls/">10.3 Security</a>.')
whw = why_how_where(
    'Defaults favour safety and moderate latency. At scale, a few settings decide whether you need 6 brokers or 20, and the wrong partition count is hard to undo (changing it re-maps keys).',
    'Measure with kafka-producer-perf-test and kafka-consumer-perf-test, read broker idle % and latencies, change one variable, measure again. Producer throughput comes from fewer, bigger requests; consumer throughput from parallel partitions; partitions from target MB/s and desired consumer parallelism.',
    'Capacity planning for launches and sales days, cost reduction, fixing latency SLO misses, choosing partition counts for new topics.',
    'Every gain has a price: linger adds latency, compression costs CPU, more partitions cost memory, file handles, longer failovers and more metadata.')

def bars(vals, labels, hl=-1, unit='MB/s'):
    mx = max(vals); o = ''
    for k, (v, l) in enumerate(zip(vals, labels)):
        w = int(v / mx * 210)
        o += t(8, 46 + k * 26, l, 7.2, 'ink', anchor='start') + box(120, 34 + k * 26, max(w, 4), 18, 'acc' if k == hl else 'blue', rx=3) + t(126 + w + 22, 47 + k * 26, f'{v:g}', 7.4, bold=True)
    return o + t(180, 20, f'throughput ({unit})', 7.6)
P = [16.08, 64.37, 53.07]; PL = ['defaults', 'batch+linger', '+ lz4']
scene_svg = scene('Producer throughput in our lab: defaults 16.08 MB/s, batch.size 256 KB with linger 20 ms 64.37 MB/s, adding lz4 compression 53.07 MB/s.', bars(P, PL, 1),
                  'One change, <tspan font-weight="700" class="s-acc">4× throughput</tspan>; the next one made it worse.')
dialogue = '''K> Sir, for the Diwali sale we expect 4× orders. Should we just add brokers?
A> First measure. Often the producer sends tiny requests. One config change can give more than three new brokers.
R> And compression always helps, right?
A> It saves network and disk, but costs CPU. On some machines it is slower. Let’s test each knob alone.'''

lv = '''
LEVELS> Tuning at three levels
L1> Loading a truck
      <ul>
        <li>Sending each parcel on its own scooter is slow. Waiting a moment to fill a truck (linger, batch size) moves far more per trip. Shrinking parcels (compression) helps only if packing them does not take longer than driving.</li>
      </ul>
L2> The knobs
      <ul>
        <li><b>Producer</b>: <code>batch.size</code> (16 KB default), <code>linger.ms</code> (5 ms default since Kafka 4.0), <code>compression.type</code> (zstd/lz4), <code>acks</code>, <code>buffer.memory</code>, <code>max.in.flight.requests.per.connection</code> (≤ 5 with idempotence).</li>
        <li><b>Consumer</b>: <code>fetch.min.bytes</code>, <code>fetch.max.wait.ms</code>, <code>max.partition.fetch.bytes</code>, <code>max.poll.records</code>; and more consumers up to the partition count.</li>
        <li><b>Broker</b>: <code>num.network.threads</code>, <code>num.io.threads</code>, <code>num.replica.fetchers</code>, disks (JBOD/RAID), and the OS page cache (Kafka relies on it; don’t give the JVM all the RAM).</li>
      </ul>
L3> Partition sizing
      <ul>
        <li>partitions ≥ max(target MB/s ÷ producer MB/s per partition, target MB/s ÷ consumer MB/s per partition, desired consumer instances). Measure per-partition rates on your hardware; plan for 1–2 years of growth.</li>
        <li>Costs of many partitions: more open files and memory, more replication fetches, longer leader elections and restarts, more metadata. KRaft raised cluster limits a lot, but per-broker counts in the low thousands are still a common guideline.</li>
        <li>Adding partitions later changes key → partition mapping (ordering per key breaks across the change); plan keyed topics generously.</li>
      </ul>
/LEVELS
'''
FX = figure('Partition sizing worked example: target 60 MB/s, measured 10 MB/s per partition for producers and 5 MB/s per partition for consumers, 8 consumer instances wanted; the answer is the maximum of 6, 12 and 8, which is 12 partitions.',
    t(16, 22, 'Sizing: take the largest need', 8.6, 'ink', anchor='start', bold=True) +
    box(16, 36, 180, 48, 'blue', rx=6) + t(106, 56, '60 ÷ 10 MB/s (produce)', 7.6) + t(106, 72, '= 6', 9, bold=True) +
    box(206, 36, 180, 48, 'amber', rx=6) + t(296, 56, '60 ÷ 5 MB/s (consume)', 7.6) + t(296, 72, '= 12', 9, bold=True) +
    box(396, 36, 120, 48, 'violet', rx=6) + t(456, 56, 'consumers wanted', 7.6) + t(456, 72, '= 8', 9, bold=True) +
    box(526, 36, 100, 48, 'green', rx=6) + t(576, 56, 'max →', 7.6) + t(576, 72, '12', 11, bold=True),
    h=120, caption='Use rates you measured, then add growth headroom.')
extra = '''

  <h3>Sizing in one picture</h3>
''' + FX

types_html = table(['Change (lab)', 'Throughput', 'Avg latency', 'Lesson'], [
    ['defaults', '16.1 MB/s', '1,727 ms', 'tiny requests'], ['batch 256 KB + linger 20 ms', '64.4 MB/s', '212 ms', 'fewer, bigger requests'],
    ['+ lz4', '53.1 MB/s', '240 ms', 'CPU-bound here'], ['1 partition (tuned)', '40.4 MB/s', '559 ms', 'one leader, one queue'],
    ['12 partitions (tuned)', '62.6 MB/s', '88 ms', 'parallel batches'], ['consumer bigger fetches', '47.2 → 44.0 MB/s', '—', 'not the bottleneck here'],
], minw=620)
warn = 'Never copy tuning values from a blog. Our lz4 and fetch results went the “wrong” way because everything ran on one VM (no real network). On real networks compression often wins. Measure on hardware like production, change one setting at a time, and keep the numbers.'

steps = [
    ('Step 1 · Producer knobs',
     code('bash', 'terminal', 'kafka-producer-perf-test.sh --topic perf-12p --num-records 200000 --record-size 1000 --throughput -1 \\\n  --producer-props bootstrap.servers=k1:9092 acks=all batch.size=262144 linger.ms=20 [compression.type=lz4]', sec('== 1)', '== 2)')),
     'Bigger batches and 20 ms linger: 4× throughput and 8× lower average latency (less queueing). lz4 cost more CPU than it saved here.'),
    ('Step 2 · Partitions',
     code('bash', 'terminal', 'same tuned producer → topic perf-1p (1 partition) vs perf-12p (12 partitions)', sec('== 2)', '== 3)')),
     'One partition = one leader and one batch queue: 40 MB/s. Twelve spread over 3 brokers: 63 MB/s and much lower latency.'),
    ('Step 3 · Consumer fetches',
     code('bash', 'terminal', 'kafka-consumer-perf-test.sh --bootstrap-server k1:9092 --topic perf-12p --messages 200000 [--command-config big-fetch.properties]', sec('== 3)')),
     'Bigger fetches did not raise throughput here: the single consumer thread was the limit. The fix for consumers is usually more consumers (up to partitions), or faster processing.'),
]
see = [term([('defaults 16.08 MB/s', W), ('batch+linger 64.37 MB/s', G), ('+lz4 53.07 MB/s', Y)], size=6.9),
       term([('1 partition 40.41 MB/s', W), ('12 partitions 62.60 MB/s', G)], size=7.0), term([('default 47.2 MB/s', W), ('big fetch 44.0 MB/s', Y)], size=7.0)]
B1 = [bars(P, PL, 1), bars([40.41, 62.60], ['1 partition', '12 partitions'], 1), bars([47.24, 44.0], ['default fetch', 'big fetch'], 0)]
B1 = [b + cap(c, '', tn, y=118, h=30) for b, c, tn in zip(B1, ['Batching wins', 'Partitions add parallelism', 'Not the bottleneck'], ['green', 'blue', 'amber'])]
two = anim_two('Tuning', 'Producer, partitions, consumer', 'Real outputs from the lab', 'Measured, not guessed', see, B1, ['Producer.', 'Partitions.', 'Consumer.'], ['4x.', 'Parallel.', 'No gain.'])
pe = peel('Why batching wins, layer by layer', '200,000 × 1 KB records. (Simplified.)',
    [('Records', ''), ('Batches', ''), ('Requests', ''), ('Broker', ''), ('Replicate', ''), ('Ack', '')],
    [['Records', '200,000 × 1 KB', '', ''], ['Batches', '16 KB → ~16 per batch', '256 KB → ~256 per batch', ''], ['Requests', '~12,500 batches', 'vs ~800', 'per partition queues'],
     ['Broker', 'fewer requests', 'less CPU per MB', 'request handlers idle'], ['Replicate', 'followers fetch', 'bigger chunks', ''], ['Ack', 'acks=all', 'fewer round trips', 'lower queueing latency']],
    ['Many.', 'Pack.', 'Fewer.', 'Cheaper.', 'Copy.', 'Ack.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Sale day 4×', 'Capacity plan. (Typical.)', ('Measure first', 'Tune before buying'), [
    ('Expect 4× orders', 'brokers at 60%', 'Worry.', 'amber'), ('Perf-test producers', 'tiny batches found', 'Bottleneck.', 'blue'),
    ('linger 10 ms, batch 128 KB', 'staged rollout', 'Tune.', 'green'), ('Broker CPU −40%', 'headroom', 'Win.', 'green'),
    ('Add 1 broker, not 4', 'cost saved', 'Done.', 'blue')], ['Plan.', 'Test.', 'Tune.', 'Gain.', 'Buy less.'], 'scenario-sale') + \
       five('Real-time scenario 2', 'Too many partitions', 'Every team asked for 100. (Typical.)', ('Partition cost', 'Size from numbers'), [
    ('50 topics × 100 partitions', 'RF 3', '15,000 replicas.', 'red'), ('Restarts take 20 min', 'elections, logs', 'Pain.', 'red'),
    ('Size from MB/s', 'most need 6–12', 'Recompute.', 'green'), ('Merge tiny topics', 'or fewer partitions for new ones', 'Reduce.', 'green'),
    ('Policy', 'review > 24 partitions', 'Govern.', 'blue')], ['Many.', 'Slow.', 'Size.', 'Reduce.', 'Policy.'], 'scenario-many') + \
       five('Real-time scenario 3 · advanced', 'Latency SLO missed', 'p99 produce 400 ms. (Typical.)', ('Find the queue', 'Client or broker?'), [
    ('Client: record-queue-time high', 'buffer full', 'Producer side.', 'amber'), ('Broker: RequestQueueTimeMs high', 'handlers busy', 'Broker side.', 'amber'),
    ('Here: broker idle 90%', 'so client side', 'Narrow.', 'blue'), ('Raise batch, lower linger, more partitions', 'test', 'Fix.', 'green'),
    ('p99 60 ms', 'SLO met', 'Done.', 'green')], ['Client?', 'Broker?', 'Narrow.', 'Fix.', 'Met.'], 'scenario-p99')
assemble(HERE, h2_story='Faster without more brokers', hook_html=hk,
    narration='TiffinGo expects four times the orders on Diwali sale day. Before buying brokers, Kabir measures what the current cluster can really do.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Performance tuning and partition sizing',
    formal='<b>Performance tuning</b> is the iterative process of identifying the limiting resource (client CPU, network, broker request handling, disk, replication) and adjusting producer, consumer, broker and OS settings to meet throughput and latency targets. <b>Partition sizing</b> chooses a partition count from measured per-partition throughput and the required consumer parallelism, balancing it against the per-partition overhead.',
    simple='Measure how fast things are, find what is slowest, change one setting, and measure again. Pick the number of partitions with simple arithmetic from how much data you have and how many consumers you want.',
    term_rows=[('Throughput', 'MB/s or records/s.'), ('Latency', 'Time per record.'), ('batch.size', 'Max bytes per batch.'), ('linger.ms', 'Wait to fill batches.'), ('fetch.min.bytes', 'Min data per fetch.'), ('Bottleneck', 'The slowest resource.'), ('Perf-test', 'Built-in load tools.'), ('Headroom', 'Spare capacity.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Compression is always faster.', 'It costs CPU; on our VM lz4 was slower.', 'Step 1.'),
               ('More partitions are always better.', 'They cost memory, files and failover time.', 'Scenario 2.'),
               ('Bigger fetches always help consumers.', 'Not if processing is the limit.', 'Step 3.')],
    exam='“How do you tune Kafka?” Measure with perf tools; producer batch.size/linger/compression/acks; consumer fetch sizes and parallelism; broker threads, disks, page cache; partitions = max(MB/s ÷ per-partition rates, consumers); one change at a time.',
    types_h2='What each change did', types_html=types_html, warn=warn,
    steps_h2='One knob at a time', steps_intro='All outputs are real: Kafka 4.4.0, 3 brokers on one VM, 200,000 × 1 KB records, acks=all.',
    steps=steps, two=two, peel_intro='Now peel why batching wins.', peel_html=pe,
    scen_intro='Three live scenarios: a sale day, too many partitions, and a latency SLO.', scen=scen,
    uc_h2='Tuning at work', ucs=[uc_('sale', 'events', 'amber', '1. Sale-day planning', 'Test at 4× load.', ['Forecast', '*perf-test', 'Plan']),
        uc_('cost', 'cost', 'green', '2. Cost reduction', 'Batching and compression cut brokers.', ['Metrics', '*tune', 'Fewer brokers']),
        uc_('slo', 'latency', 'blue', '3. Latency SLOs', 'Find the queue, fix it.', ['p99', '*diagnose', 'Met']),
        uc_('new', 'topics', 'violet', '4. New topics', 'Partitions from arithmetic.', ['MB/s', '*formula', 'Count'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../01-monitoring-and-consumer-lag/">10.1 Monitoring</a>.')
