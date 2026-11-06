import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l44_zerocopy.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('Our tiny lab broker read 286 MB to a consumer at about 63 MB/s. Where did the CPU go? Mostly nowhere.',
    'Kafka is fast for boring reasons: it appends sequentially, lets the operating system cache files in memory, and for plaintext connections sends file bytes straight to the network socket without copying them through Java (<b>zero-copy</b>). And since Kafka 3.9, old segments can move to cheap object storage (<b>tiered storage</b>) so retention can be months instead of days.',
    ['Why Kafka uses the page cache instead of its own memory cache.',
     'What zero-copy is and when it is switched off.',
     'How tiered storage splits a partition between local disk and S3-like storage.'])
cmap = concept_map('Concept map. Beginner: sequential writes, page cache, why Kafka is fast. Intermediate: zero-copy sendfile, batching end to end, TLS cost. Advanced: tiered storage, remote storage manager, local vs total retention.',
    [[('sq', 'Sequential I/O', 'append only', B + '04-storage-internals/01-the-commit-log-and-segments/'), ('pc', 'Page cache', 'OS memory', None), ('fs', 'Why Kafka is fast', 'summary', None)],
     [('zc', 'Zero-copy (sendfile)', 'disk → socket', None), ('be', 'Batches end to end', 'Lesson 2.3', B + '02-producers/03-batching-and-compression/'), ('tl', 'TLS cost', 'no zero-copy', B + '10-kafka-in-production/03-security-tls-sasl-and-acls/')],
     [('ts', 'Tiered storage', 'KIP-405', None), ('rs', 'RemoteStorageManager', 'plugin (S3, GCS, Azure)', None), ('lr', 'local.retention vs retention', 'hot vs total', B + '04-storage-internals/03-retention-and-compaction/')]],
    [('sq', 'pc'), ('pc', 'zc'), ('be', 'zc'), ('zc', 'tl'), ('fs', 'ts'), ('ts', 'rs'), ('ts', 'lr')],
    {'sq', 'pc', 'fs', 'zc', 'be', 'ts', 'rs', 'lr'},
    '<b>Builds on:</b> 4.1–4.3. <b>Next:</b> Module 5, <a href="../../05-replication-and-the-cluster/01-brokers-and-replication/">5.1 Brokers and replication</a>.')
whw = why_how_where(
    'Kafka must move huge volumes cheaply, and keeping months of data on broker SSDs is expensive and slows recovery.',
    'Sequential appends + page cache + batch-level transfer (sendfile for plaintext) keep CPU low; tiered storage uploads closed segments to object storage and serves old reads from there.',
    'High-throughput clusters (logs, clicks, CDC) and long-retention topics (audit, ML training data, replay).',
    'TLS disables zero-copy (encryption needs user-space copies); tiered storage needs a plugin, does not support compacted topics, and remote reads are slower.')

sc_ = (box(14, 24, 296, 112, 'card', rx=8) + t(162, 40, 'Classic read path', 8.6, bold=True) +
       ''.join(opbox(26 + k * 70, 56, n, '', 'red' if k in (1, 2) else 'card', 62, 26) + (arrow(88 + k * 70, 69, 96 + k * 70, 69, 'ink3', 1) if k < 3 else '') for k, n in enumerate(['disk', 'kernel', 'app copy', 'socket'])) +
       t(162, 106, '4 copies, 2 through the application', 7.8, 'red') +
       box(330, 24, 296, 112, 'card', rx=8) + t(478, 40, 'Kafka with sendfile (plaintext)', 8.6, bold=True) +
       opbox(350, 56, 'page cache', '', 'green', 90, 26) + arrow(440, 69, 470, 69, 'green', 1.4) + opbox(470, 56, 'socket / NIC', '', 'green', 110, 26) +
       t(478, 106, 'bytes never enter the JVM heap', 7.8, 'green', bold=True))
scene_svg = scene('Left: a classic read path copies data from disk to kernel to the application and back to the socket. Right: Kafka with sendfile sends bytes from the page cache straight to the socket without entering the Java heap.', sc_,
                  '<tspan font-weight="700" class="s-acc">Zero-copy</tspan>: the broker does not touch the bytes it sends.')
dialogue = '''R> Sir, how does one Kafka broker send gigabytes per second? Java is not that fast at copying bytes.
A> It mostly does not copy them. Kafka stores batches exactly as consumers will read them. For plaintext connections it asks the operating system to send file bytes straight to the network: <b>zero-copy</b>. And recent data is already in RAM, in the OS <b>page cache</b>.
K> And our finance team wants one year of history. Do we buy huge SSDs?
A> Kafka 3.9 made <b>tiered storage</b> production-ready: closed segments go to object storage like S3, and only recent data stays on the broker. Let’s measure the read side first.'''

lv = '''
LEVELS> Speed and storage at three levels
L1> A godown and a shop counter
      <ul>
        <li>Fresh stock sits on the counter (page cache) and is handed out in sealed boxes (batches) without opening them (zero-copy). Old stock moves to a cheap far-away godown (object storage) and is fetched only when someone asks.</li>
      </ul>
L2> Why Kafka is fast
      <ul>
        <li><b>Sequential I/O</b>: only appends to the active segment; disks and SSDs love this.</li>
        <li><b>Page cache</b>: Kafka keeps little in the JVM; the OS caches recently written segments, so tailing consumers read from RAM.</li>
        <li><b>Batches end to end</b>: producer batch = stored batch = fetched batch, compressed once (Lesson 2.3).</li>
        <li><b>Zero-copy</b>: for plaintext listeners, <code>FileChannel.transferTo</code> (Linux <code>sendfile</code>) moves bytes from page cache to socket.</li>
      </ul>
L3> Tiered storage (KIP-405, GA in Kafka 3.9)
      <ul>
        <li>Broker: <code>remote.log.storage.system.enable=true</code> plus a <b>RemoteStorageManager</b> plugin (open-source plugins exist for S3, GCS and Azure) and the built-in topic-based <b>RemoteLogMetadataManager</b> (<code>__remote_log_metadata</code>).</li>
        <li>Topic: <code>remote.storage.enable=true</code>, <code>local.retention.ms/bytes</code> (hot data on broker) and <code>retention.ms</code> (total, including remote).</li>
        <li>Closed segments (with indexes) are copied to remote storage; reads below the local log start are served from remote. Not supported for compacted topics.</li>
      </ul>
/LEVELS
'''
tier = figure('Tiered storage layout: one partition whose older closed segments live in object storage, the recent closed segments and the active segment on the broker disk; local retention 1 day, total retention 1 year.',
    t(16, 22, 'One partition with tiered storage (example settings)', 8.6, 'ink', anchor='start', bold=True) +
    ''.join(box(16 + k * 46, 40, 40, 30, 'violet', rx=3) for k in range(7)) + t(176, 88, 'remote: object storage (S3/GCS/Azure)', 8, 'violet', bold=True) + pin(18, 38, 1) +
    ''.join(box(350 + k * 46, 40, 40, 30, 'blue', rx=3) for k in range(4)) + box(534, 40, 60, 30, 'acc', rx=3) + t(564, 59, 'active', 7.6, 'ink', bold=True) + t(470, 88, 'local: broker disk', 8, 'blue', bold=True) + pin(352, 38, 2) + pin(536, 38, 3) +
    legend(16, 120, [(1, 'Remote tier', 'closed segments + indexes uploaded; kept until retention.ms (e.g. 1 year)'),
                     (2, 'Local tier', 'recent closed segments kept until local.retention.ms (e.g. 1 day)'),
                     (3, 'Active segment', 'always local; never uploaded until closed')], size=8, gap=16, w=120),
    h=184, caption='Concept diagram; tiered storage needs a storage plugin and was not run in our lab.')
DIS = figure('Dissection of the consumer perf test output: 286 MB consumed at about 63 MB per second and 66 thousand messages per second, twice, with the broker page cache holding about 1.9 GB.',
    t(16, 22, 'kafka-consumer-perf-test on big-44 (300,000 × 1 KB)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('286.1 MB read', 'blue', 1), ('run 1: 62.9 MB/s', 'green', 2), ('run 2: 64.8 MB/s', 'green', None), ('~66,000 msg/s', 'acc', 3)]) +
    fields(16, 70, [('Cached: 1,906,992 kB', 'violet', 4), ('MemTotal: 8,214,984 kB', 'card', None)]) +
    legend(16, 118, [(1, 'Data', '3 partitions of uncompressed 1 KB records'), (2, 'Throughput', 'one consumer, small Docker lab; real clusters reach GB/s'),
                     (3, 'Records/s', 'fetched as batches, not one by one'), (4, 'Page cache', 'the OS kept recent segments in RAM: no disk reads')], size=8, gap=15, w=110),
    h=190, caption='Real numbers from our lab run.')
extra = '''

  <h3>Dissect the read test</h3>
''' + DIS + '''

  <h3>Tiered storage at a glance</h3>
''' + tier

types_html = table(['Speed trick', 'Where', 'Switched off when'], [
    ['Sequential append', 'broker log', 'never'], ['Page cache', 'broker OS', 'memory pressure, lagging readers evict hot data'],
    ['Batching + compression', 'producer → disk → consumer', 'linger 0, no compression'], ['Zero-copy sendfile', 'broker → consumer/follower', 'TLS listeners, down-conversion for very old clients'],
], minw=600) + table(['Tiered storage setting', 'Level', 'Meaning'], [
    ['remote.log.storage.system.enable', 'broker', 'turn the feature on'],
    ['remote.log.storage.manager.class.name', 'broker', 'the storage plugin class (S3, GCS, Azure …)'],
    ['remote.storage.enable', 'topic', 'tier this topic'],
    ['local.retention.ms / local.retention.bytes', 'topic', 'how much stays on broker disks'],
    ['retention.ms', 'topic', 'total retention including remote'],
], minw=600)
warn = 'Do not give the Kafka JVM most of the machine’s RAM. Kafka needs only a modest heap (often 4–8 GB); the rest should be left to the OS page cache, which is where Kafka’s read speed comes from. And remember that TLS (Lesson 10.3) removes zero-copy, so encrypted clusters need more CPU.'

steps = [
    ('Step 1 · Write about 290 MB',
     code('bash', 'terminal', 'kafka-producer-perf-test.sh --topic big-44 --num-records 300000 --record-size 1000 --throughput -1 \\\n  --producer-props bootstrap.servers=k1:9092 linger.ms=10 batch.size=262144', sec('== 1)', '== 2)')),
     '300,000 records of 1 KB at about 46 MB/s with acks=all to 3 replicas on our small lab machine.'),
    ('Step 2 · Read it back twice',
     code('bash', 'terminal', 'kafka-consumer-perf-test.sh --bootstrap-server k1:9092 --topic big-44 --messages 300000 --group perf-1', sec('== 2)', '== 3)')),
     'About 63–65 MB/s for a single consumer. The two runs are the same because the data was already in the page cache after writing: nothing had to come from disk.'),
    ('Step 3 · Where the data was',
     code('bash', 'terminal', 'grep -E "^(MemTotal|Cached)" /proc/meminfo\ndu -sh /var/lib/kafka/data/big-44-*', sec('== 3)')),
     'The OS page cache held about 1.9 GB, more than the 290 MB topic. This memory is not in the Kafka JVM, which is why a Kafka heap stays small.'),
]

see = [term([('300000 records sent', W), ('46.49 MB/sec', G)], size=7.4),
       term([('run 1: 62.9 MB/sec', G), ('run 2: 64.8 MB/sec', G), ('66,000 msg/sec over 286 MB', W)], size=7.2),
       term([('MemTotal: 8214984 kB', W), ('Cached:   1906992 kB', G), ('87M 87M 116M on disk', W)], size=7.2)]
B1 = [t(180, 14, 'Sequential append', 9, bold=True) + ''.join(box(20 + k * 32, 54, 28, 28, 'green', rx=3) for k in range(10)) + arrow(340, 68, 346, 68, 'acc', 1.4) + cap('Disk-friendly writes.', '', 'green', y=144, h=30),
      t(180, 14, 'Served from page cache', 9, bold=True) + opbox(20, 50, 'page cache', 'RAM (OS)', 'green', 110, 34) + arrow(130, 67, 220, 67, 'green', 1.4) + opbox(220, 50, 'consumer', '~63 MB/s', 'blue', 110, 34) + cap('No disk reads needed.', '', 'green', y=144, h=30),
      t(180, 14, 'JVM heap stays small', 9, bold=True) + box(20, 50, 320, 30, 'card', rx=4) + box(20, 50, 320 * 1.9 / 8.2, 30, 'green', rx=4) + t(30, 70, 'page cache 1.9 GB', 7.6, 'ink', anchor='start', bold=True) + cap('Leave RAM to the OS.', '', 'blue', y=144, h=30)]
two = anim_two('Why Kafka is fast', 'Write, read, cache', 'Real outputs from the lab', 'Where the bytes live', see, B1, ['Write.', 'Read.', 'Cache.'], ['Sequential.', 'Page cache.', 'Small heap.'])
pe = peel('A consumer fetch with zero-copy', 'From request to network card. (Plaintext listener.)',
    [('Fetch request', ''), ('Index lookup', ''), ('File region', ''), ('sendfile', ''), ('Network', ''), ('Consumer', '')],
    [['Fetch request', 'big-44 P0 from offset N', 'up to fetch.max.bytes', ''], ['Index lookup', 'segment + position', '(Lesson 4.2)', ''],
     ['File region', 'start byte, length', 'whole batches', 'no parsing of records'], ['sendfile', 'kernel copies page-cache', 'pages to the socket', 'JVM never sees bytes'],
     ['Network', 'NIC sends batches', 'compressed as stored', ''], ['Consumer', 'decompresses, parses', 'CPU spent on the client', 'not the broker']],
    ['Ask.', 'Locate.', 'Region.', 'Kernel.', 'Wire.', 'Client.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'CPU doubled after enabling TLS', 'Zero-copy lost. (Typical.)', ('TLS and zero-copy', 'Encryption needs copies through the JVM'), [
    ('Security team enables TLS', 'all listeners', 'Required.', 'blue'), ('Broker CPU 35% → 70%', 'same traffic', 'Surprise.', 'red'),
    ('Reason: no sendfile', 'bytes encrypted in JVM', 'Expected.', 'amber'), ('Plan CPU headroom', 'modern CPUs AES-NI', 'Or more brokers.', 'green'),
    ('Keep compression on', 'fewer bytes to encrypt', 'Helps.', 'blue')], ['TLS.', 'CPU.', 'Why.', 'Plan.', 'Compress.'], 'scenario-tls') + \
       five('Real-time scenario 2', 'One year of history on SSDs', 'Tiered storage for long retention. (Typical.)', ('Tiered storage', 'Keep hot data local, history in object storage'), [
    ('Finance wants 1 year replay', '5 TB/day', '1.8 PB on SSD!', 'red'), ('Enable tiered storage', 'S3 plugin', 'Kafka 3.9+.', 'green'),
    ('local.retention 1 day', 'retention 365 days', 'Topic configs.', 'green'), ('Brokers small and fast', 'recover quickly', 'Less data per broker.', 'green'),
    ('Old reads slower', 'from object storage', 'Acceptable for replay.', 'amber')], ['Need.', 'Enable.', 'Configure.', 'Benefits.', 'Trade-off.'], 'scenario-tier') + \
       five('Real-time scenario 3 · advanced', 'Backfill job slows everyone', 'Page cache pollution. (Typical.)', ('Page cache', 'Old reads evict hot pages'), [
    ('ML backfill reads 30 days', 'from the start', 'Huge cold read.', 'blue'), ('Pages for recent data evicted', 'tailing consumers hit disk', 'Latency up.', 'red'),
    ('Quotas for the backfill', 'consumer_byte_rate', 'Throttle.', 'green'), ('Or read from remote tier', 'tiered storage', 'Separate path.', 'green'),
    ('Schedule off-peak', 'and monitor', 'Ops.', 'blue')], ['Backfill.', 'Evict.', 'Quota.', 'Tier.', 'Schedule.'], 'scenario-backfill')
assemble(HERE, h2_story='Fast reads, cheap history', hook_html=hk,
    narration='TiffinGo’s clicks topic grows to terabytes. The platform team asks two questions: how can three brokers keep up, and how can finance get a year of history without buying a mountain of SSDs?',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Tiered storage and zero-copy',
    formal='Kafka achieves high throughput by appending sequentially to segment files, relying on the operating system <b>page cache</b> instead of an in-process cache, transferring record batches unchanged end to end, and using <b>zero-copy</b> transfer (<code>FileChannel.transferTo</code>, i.e. <code>sendfile</code>) from page cache to socket for plaintext connections. <b>Tiered storage</b> (KIP-405, production-ready since Kafka 3.9) extends a partition’s log to a remote object store through a pluggable <code>RemoteStorageManager</code>: closed segments are copied remotely, local copies are deleted after <code>local.retention.ms/bytes</code>, and fetches below the local log start are served from remote storage until <code>retention.ms</code>.',
    simple='Kafka is fast because it writes files in order, lets the operating system keep recent data in memory, and sends stored batches straight to the network without copying them through Java. With tiered storage, old data moves to cheap cloud storage while new data stays on the brokers.',
    term_rows=[('Page cache', 'OS memory caching files.'), ('Sequential I/O', 'Writing/reading in order.'), ('Zero-copy', 'Kernel sends file data directly.'), ('sendfile', 'Linux call for zero-copy.'), ('Tiered storage', 'Old segments in object storage.'), ('RemoteStorageManager', 'Plugin for the remote tier.'), ('local.retention.ms', 'How long data stays on brokers.'), ('JVM heap', 'Kafka process memory (keep small).')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Kafka caches data in its own memory.', 'It relies on the OS page cache; the JVM heap stays small.', 'Step 3: 1.9 GB cached outside the JVM.'),
               ('Zero-copy always works.', 'TLS listeners disable it.', 'Scenario 1.'),
               ('Kafka cannot keep data for a year affordably.', 'Tiered storage keeps history in object storage.', 'Scenario 2.')],
    exam='“Why is Kafka fast?” Sequential appends, OS page cache, batching + compression end to end, zero-copy sendfile for plaintext, partition parallelism. “What is tiered storage?” KIP-405 (GA 3.9): closed segments uploaded via a RemoteStorageManager plugin; local.retention for hot data, retention.ms for total; not for compacted topics.',
    types_h2='Speed tricks and tiering settings', types_html=types_html, warn=warn,
    steps_h2='Measure the read path', steps_intro='All outputs are real: Kafka 4.4.0, 3 brokers in Docker on one small VM; topic <code>big-44</code>, 3 partitions, RF 3. Tiered storage needs a storage plugin and object store, so it is explained, not run, here.',
    steps=steps, two=two, peel_intro='Now peel a zero-copy fetch.', peel_html=pe,
    scen_intro='Three live scenarios: TLS cost, a year of history, and a backfill job.', scen=scen,
    uc_h2='At work', ucs=[uc_('logs', 'GB/s', 'blue', '1. Log platforms', 'Page cache + zero-copy serve many consumers cheaply.', ['Logs', '*sendfile', 'Consumers']),
        uc_('audit', '1 year', 'green', '2. Audit history', 'Tiered storage keeps a year in object storage.', ['Segments', '*S3', 'Replay']),
        uc_('ML', 'training', 'violet', '3. ML training data', 'Backfills read from the remote tier.', ['History', '*remote', 'Models']),
        uc_('secure', 'TLS', 'acc', '4. Encrypted clusters', 'Plan extra CPU when zero-copy is off.', ['TLS', '*CPU', 'Capacity']),
        uc_('cloud', 'managed', 'blue', '5. Managed services', 'Many offer tiered storage built in (Lesson 11.1).', ['Topic', '*tiered', 'Cheaper'])],
    uc_note='Throughput numbers are from our small lab VM; production clusters are much faster.',
    pre='<b>Before you start:</b> <a href="../01-the-commit-log-and-segments/">4.1</a>–<a href="../03-retention-and-compaction/">4.3</a>.')
