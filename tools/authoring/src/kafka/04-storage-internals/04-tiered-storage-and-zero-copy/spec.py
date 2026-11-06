import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
BODY = body(HERE)
META = dict(module='04-storage-internals', lesson='04-tiered-storage-and-zero-copy', n='4.4', module_label='Module 4 · Storage internals',
    title='Tiered storage and zero-copy',
    desc='Why Kafka is fast (sequential appends, OS page cache, batches end to end, zero-copy sendfile) and how tiered storage (KIP-405, production-ready in Kafka 3.9) moves closed segments to object storage with local.retention and remote.storage.enable. Real Kafka 4.4 lab: 300,000 × 1 KB records written at 46 MB/s and read back at about 63 MB/s from the page cache, with 1.9 GB cached outside the JVM.',
    og_desc='Why Kafka is fast and how tiered storage keeps a year of data cheaply: page cache, zero-copy and KIP-405 explained.',
    minutes=22, level='Advanced',
    lead='Two big ideas: why a Kafka broker barely touches the bytes it serves (<b>page cache</b> and <b>zero-copy</b>), and how <b>tiered storage</b> keeps months of history in object storage. We measure the read path on a real cluster. <b>All outputs are real.</b>',
    chips=['~63 MB/s from page cache', 'Zero-copy explained', 'Tiered storage settings', 'Runs in your browser (Python)'])
MAIN = '''# Where does a fetch get its bytes? Local page cache, local disk, or remote tier
def serve(offset, local_start, hot_start):
    if offset < local_start:
        return "remote tier (object storage) - slower, cheap"
    if offset >= hot_start:
        return "page cache (RAM) - fastest, zero-copy if plaintext"
    return "local disk - fast sequential read"

local_start, hot_start = 1_000_000, 9_500_000     # example offsets
for off in (200_000, 5_000_000, 9_900_000):
    print(f"offset {off:>9,}: {serve(off, local_start, hot_start)}")

copies_classic, copies_zero = 4, 2
print("data copies per read: classic", copies_classic, "vs sendfile", copies_zero)
'''
RUN = dict(heading='Run the code: where reads come from', intro='<p>Three tiers of a partition in a few lines. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    if offset < local_start:', 'Below the local log start: served from the remote tier.'), ('    if offset >= hot_start:', 'Recent data: usually still in the OS page cache.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Then try offset 999,999.', code=None),
        dict(label='2 · Predict first: SSD cost', hint='<b>Predict first:</b> 5 TB/day × 365 days × RF 3 in PB?', code='print(round(5 * 365 * 3 / 1000, 1), "PB")\n'),
        dict(label='3 · With tiering', hint='Local 1 day × RF 3.', code='print(5 * 1 * 3, "TB on brokers")\n'),
        dict(label='4 · Heap vs cache', hint='64 GB machine, 6 GB heap.', code='print(64 - 6, "GB left for page cache and OS")\n'),
        dict(label='5 · Spot the error', hint='Tiering a compacted topic.', expect='error', code='policy, remote = "compact", True\nif remote and "compact" in policy:\n    raise ValueError("remote.storage.enable is not supported for compacted topics")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: measure throughput', intro='<p>Perf tools in the Kafka distribution. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Write', cmd='kafka-producer-perf-test.sh --topic big-44 --num-records 300000 --record-size 1000 --throughput -1 --producer-props bootstrap.servers=localhost:9092 linger.ms=10', file='terminal', output='300000 records sent, 48748.78 records/sec (46.49 MB/sec) …', note='Your numbers will differ.'),
           dict(title='2 · Read', cmd='kafka-consumer-perf-test.sh --bootstrap-server localhost:9092 --topic big-44 --messages 300000 --group perf-1', file='terminal', output='… 286.1023, 62.9073, 300000, 65963.0607 …', note='MB, MB/s, msgs, msgs/s.'),
           dict(title='3 · Tiered topic (with a plugin installed)', cmd='kafka-topics.sh --create --topic audit --config remote.storage.enable=true --config local.retention.ms=86400000 --config retention.ms=31536000000', file='terminal', output='Created topic audit.', note='Requires broker tiered storage setup.')])
TRACE = dict(heading='Pick a tier', intro='<p>Compare the offset with two boundaries.</p>',
    code='local_start, hot_start = 100, 900\noffset = 50\ntier = "remote" if offset < local_start else ("cache" if offset >= hot_start else "disk")\nprint(tier)\n',
    notes={3: 'Decide :: Below local start → remote.', 4: 'Result :: remote.'})
WORKED_INTRO = 'Three capacity decisions.'
EXAMPLES = [
    dict(level='b', tag='Capacity · memory', title='Size broker RAM', problem='<p>Tailing consumers should never hit disk.</p>', inp='ingest rate',
         approach=['Hot window = rate × seconds consumers lag.', 'Page cache ≥ hot window.', 'Heap small.'], code='rate_mb_s, lag_s = 100, 600\nprint(rate_mb_s * lag_s / 1024, "GB page cache needed (approx)")\n', notes={1: 'Cache :: Keep hot data in RAM.'}, tryit='Step 3.'),
    dict(level='i', tag='Capacity · tiering', title='Local vs total retention', problem='<p>Replays rare after 2 days; keep 90 days.</p>', inp='days',
         approach=['local.retention.ms = 2 days.', 'retention.ms = 90 days.', 'remote.storage.enable=true.'], code='print({"local.retention.ms": 2 * 86400000, "retention.ms": 90 * 86400000, "remote.storage.enable": "true"})\n', notes={1: 'Split :: Hot local, cold remote.'}, tryit='Scenario 2.'),
    dict(level='a', tag='Capacity · CPU', title='TLS headroom', problem='<p>Enable TLS on a cluster at 40% CPU.</p>', inp='CPU',
         approach=['Expect a CPU increase (no sendfile).', 'Measure on a staging broker.', 'Add brokers if > 60%.'], code='cpu_now, factor = 40, 1.8\nprint("estimated CPU:", cpu_now * factor, "%")\n', notes={1: 'Plan :: Measure before enabling.'}, tryit='Scenario 1.')]
QUIZ = mix([
    dict(q='Beginner: Kafka keeps hot data mainly in…', options=['The JVM heap', 'The OS page cache', 'ZooKeeper', 'The client'], answer=1, why='Step 3.'),
    dict(q='Beginner: Zero-copy means…', options=['No replication', 'Kernel sends file bytes to the socket without JVM copies', 'No compression', 'No disk'], answer=1, why='sendfile.'),
    dict(q='Beginner: Tiered storage moves old segments to…', options=['Another topic', 'Object storage (S3, GCS, Azure)', 'The consumer', 'RAM'], answer=1, why='Remote tier.'),
    dict(q='Intermediate: Zero-copy is lost when…', options=['acks=all', 'Using TLS listeners', 'Using compression', 'Using keys'], answer=1, why='Encryption in JVM.'),
    dict(q='Intermediate: Our single consumer read at about…', options=['6 MB/s', '63 MB/s', '630 MB/s', '6 GB/s'], answer=1, why='Small lab.'),
    dict(q='Intermediate: Tiered storage became production-ready in…', options=['2.0', '3.9', '4.4', 'Never'], answer=1, why='KIP-405.'),
    dict(q='Advanced: local.retention.ms controls…', options=['Total retention', 'How long data stays on broker disks', 'Consumer offsets', 'Index size'], answer=1, why='Hot tier.'),
    dict(q='Advanced: Which topics cannot use tiered storage?', options=['Keyed', 'Compacted', 'Compressed', 'Replicated'], answer=1, why='Not supported.')])
REVISION = ['Fast because: sequential appends, page cache, batches end to end, zero-copy sendfile, partitions.', 'Lab: write 46.5 MB/s; read ~63 MB/s from page cache (1.9 GB cached).',
    'TLS disables zero-copy → more CPU.', 'Tiered storage (KIP-405, GA 3.9): RemoteStorageManager plugin; remote.storage.enable; local.retention vs retention.ms.', 'Keep JVM heap small; leave RAM to the OS.']
FAQ = [('How big should the Kafka heap be?', 'Usually 4–8 GB is enough; most memory should stay free for the page cache.'),
    ('Does compression break zero-copy?', 'No. Batches are stored and sent compressed; the broker does not decompress for consumers.'),
    ('Is tiered storage in every distribution?', 'The framework is in Apache Kafka; you add a RemoteStorageManager plugin. Many managed services offer it built in.'),
    ('Do consumers notice tiered data?', 'Only through latency: fetches below the local log start are served from object storage.')]
PRACTICE_INTRO = 'Capacity programs.'
PROBLEMS = [
    dict(level='easy', title='MB/s', stmt='286 MB in 4.55 s.', inp='numbers', code='print(round(286 / 4.55, 1))\n', explain='~63 MB/s.'),
    dict(level='easy', title='Cache share', stmt='1.9 GB of 8.2 GB.', inp='numbers', code='print(round(100 * 1.9 / 8.2), "%")\n', explain='23%.'),
    dict(level='easy', title='Copies saved', stmt='Classic 4 vs sendfile 2.', inp='numbers', code='print(4 - 2)\n', explain='Fewer copies.'),
    dict(level='medium', title='Hot window', stmt='50 MB/s for 10 minutes.', inp='numbers', code='print(50 * 600 / 1024, "GB")\n', explain='~29 GB.'),
    dict(level='medium', title='Local disk', stmt='2 TB/day, local 1 day, RF 3.', inp='numbers', code='print(2 * 1 * 3, "TB")\n', explain='6 TB on brokers.'),
    dict(level='medium', title='Remote size', stmt='2 TB/day for 90 days (object storage stores 1 copy).', inp='numbers', code='print(2 * 90, "TB in object storage")\n', explain='180 TB.'),
    dict(level='business', title='Cost', stmt='180 TB × Rs 1.8/GB-month vs SSD Rs 8/GB-month × 3.', inp='numbers', code='print(180_000 * 1.8, "vs", 180_000 * 8 * 3)\n', explain='Rough monthly rupees.'),
    dict(level='business', title='Brokers', stmt='Throughput 600 MB/s at 150 MB/s per broker.', inp='numbers', code='print(600 // 150, "brokers (+ headroom)")\n', explain='Capacity plan.')]
SCN_INTRO = 'Performance and storage interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“Why is Kafka fast?”', 'List reasons.', 'answer?', '<p>Sequential disk appends, the OS page cache, batching and compression end to end, zero-copy transfer for plaintext, and partition parallelism across brokers.</p>', '“Because it stores data in memory only.”') +
    scn('Platform', 'Mid-level', 'TLS rollout', 'CPU doubled after TLS.', 'explain?', '<ul><li>No zero-copy with TLS.</li><li>Plan CPU, keep compression.</li></ul>', '“TLS is broken.”') +
    scn('Platform', 'Mid-level', 'Long retention', 'Keep 1 year of clickstream affordably.', 'design?', '<ul><li>Tiered storage with an object-store plugin.</li><li>local.retention short, retention 365 days.</li></ul>', 'Buying SSDs for a year.') +
    scn('Platform', 'Senior', 'Latency spikes', 'Tail latency spikes when a batch job reads old data.', 'fix?', '<ul><li>Page cache eviction by cold reads.</li><li>Quotas, off-peak scheduling, read from remote tier.</li></ul>', 'Bigger JVM heap.'))
