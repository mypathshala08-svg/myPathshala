import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
BODY = body(HERE)
META = dict(module='04-storage-internals', lesson='01-the-commit-log-and-segments', n='4.1', module_label='Module 4 · Storage internals',
    title='The commit log and segments',
    desc='How Kafka stores a partition on disk as a chain of segments: .log, .index, .timeindex, .snapshot, leader-epoch-checkpoint and partition.metadata, base-offset file names, the active segment and roll rules (segment.bytes, segment.ms). Real Kafka 4.4 lab: 10,000 orders roll into three 1 MiB segments, the 1 MiB minimum is enforced, and pre-allocated indexes shrink when a segment closes.',
    og_desc='10,000 orders, three segments, files named by base offset: Kafka’s on-disk log opened up on 4.4.',
    minutes=22, level='Intermediate',
    lead='A partition is not one file. We force a real <b>Kafka 4.4</b> partition to <b>roll segments</b>, list every file it creates, and learn why files are named by <b>base offset</b> and why only one segment is ever written. <b>All outputs are real.</b>',
    chips=['3 segments rolled', 'Every file explained', '1 MiB minimum found', 'Runs in your browser (Python)'])
MAIN = '''# A partition as a chain of segments
SEGMENT_BYTES = 1_048_576
segments = [[0, 0]]                      # [base_offset, size_bytes]
def append(offset, size):
    if segments[-1][1] + size > SEGMENT_BYTES:   # roll: next batch would not fit
        segments.append([offset, 0])
    segments[-1][1] += size

offset = 0
while offset < 10_000:
    append(offset, 3011)                 # one batch of 10 records, 3,011 bytes
    offset += 10

for base, size in segments:
    print(f"{base:020d}.log  {size:>9,} bytes")
print("active segment:", f"{segments[-1][0]:020d}.log")
'''
RUN = dict(heading='Run the code: rolling segments', intro='<p>The roll rule with our lab’s batch size. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    if segments[-1][1] + size > SEGMENT_BYTES:   # roll: next batch would not fit', 'Kafka rolls before a batch would exceed segment.bytes.'), ('    print(f"{base:020d}.log  {size:>9,} bytes")', 'File names are the base offset padded to 20 digits.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Compare with the lab’s 3413 and 6830.', code=None),
        dict(label='2 · Predict first: segments', hint='<b>Predict first:</b> 1 GiB of data, 1 GiB segments?', code='print(1)\n'),
        dict(label='3 · File name', hint='Name for base offset 6830.', code='print(f"{6830:020d}.log")\n'),
        dict(label='4 · Files per partition', hint='Segments × 4 files.', code='print(3 * 4, "files (+2 metadata)")\n'),
        dict(label='5 · Spot the error', hint='Too small a segment.', expect='error', code='seg = 16384\nif seg < 1048576:\n    raise ValueError(f"Invalid value {seg} for configuration segment.bytes: Value must be at least 1048576")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: look at segments', intro='<p>Inside the broker container. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Topic', cmd='kafka-topics.sh --bootstrap-server localhost:9092 --create --topic seg-41 --config segment.bytes=1048576', file='terminal', output='Created topic seg-41.', note='1 MiB minimum.'),
           dict(title='2 · Files', cmd='ls -l /var/lib/kafka/data/seg-41-0/', file='terminal', output='00000000000000000000.log\n00000000000000003413.log\n00000000000000006830.log …', note='After ~3 MB.'),
           dict(title='3 · First batch of a segment', cmd='kafka-dump-log.sh --files /var/lib/kafka/data/seg-41-0/00000000000000003413.log | head -2', file='terminal', output='baseOffset: 3413 lastOffset: 3422 count: 10 … position: 0 size: 3011', note='Position 0 in the new file.')])
TRACE = dict(heading='When does it roll?', intro='<p>Size check before each append.</p>',
    code='limit, size, segs = 10, 0, [0]\nfor off, s in enumerate([4, 4, 4, 4]):\n    if size + s > limit:\n        segs.append(off); size = 0\n    size += s\nprint(segs)\n',
    notes={3: 'Check :: Would this batch overflow?', 4: 'Roll :: New segment named by offset.'})
WORKED_INTRO = 'Three segment decisions.'
EXAMPLES = [
    dict(level='b', tag='Segments · read', title='Find the segment for an offset', problem='<p>Which file holds offset 5000?</p>', inp='bases',
         approach=['List base offsets.', 'Pick the largest ≤ 5000.', 'Open that file.'], code='import bisect\nbases = [0, 3413, 6830]\nprint(bases[bisect.bisect_right(bases, 5000) - 1])\n', notes={1: 'Binary search :: Names make it fast.'}, tryit='Lesson 4.2.'),
    dict(level='i', tag='Segments · retention', title='Make retention precise', problem='<p>1-day retention, 50 MB/day traffic.</p>', inp='traffic',
         approach=['Segments must close to be deleted.', 'segment.ms 1 hour.', 'Deletion lag ≤ 1 hour.'], code='print({"retention.ms": 86400000, "segment.ms": 3600000})\n', notes={1: 'Granularity :: Roll often enough.'}, tryit='Scenario 2.'),
    dict(level='a', tag='Segments · ops', title='Estimate file handles', problem='<p>2,000 partitions, 20 segments each.</p>', inp='counts',
         approach=['~3 open files per segment (log + 2 indexes).', 'Multiply.', 'Set ulimit well above.'], code='print(2000 * 20 * 3, "file handles; set ulimit -n >= 200000")\n', notes={1: 'Ops :: Plan limits.'}, tryit='Scenario 1.')]
QUIZ = mix([
    dict(q='Beginner: A partition on disk is…', options=['One file', 'A chain of segments', 'A database table', 'In ZooKeeper'], answer=1, why='Step 2.'),
    dict(q='Beginner: Which segment receives new records?', options=['The oldest', 'The active (newest)', 'All of them', 'Random'], answer=1, why='Only one.'),
    dict(q='Beginner: A segment file is named after…', options=['The time', 'Its base offset', 'The topic id', 'A random id'], answer=1, why='…3413.log.'),
    dict(q='Intermediate: Default segment.bytes is…', options=['1 MiB', '1 GiB', '10 GiB', '100 KB'], answer=1, why='Minimum 1 MiB.'),
    dict(q='Intermediate: Why was the active .index 10 MiB?', options=['Corrupt', 'Pre-allocated; trimmed when closed', 'Full of data', 'Compression'], answer=1, why='segment.index.bytes.'),
    dict(q='Intermediate: .snapshot files store…', options=['Record data', 'Producer state (ids, sequences)', 'Consumer offsets', 'ACLs'], answer=1, why='Idempotence state.'),
    dict(q='Advanced: Retention can delete…', options=['Single records', 'Whole closed segments', 'The active segment only', 'Indexes only'], answer=1, why='Per segment.'),
    dict(q='Advanced: A low-traffic topic with 1 GiB segments keeps data longer than retention because…', options=['Bug', 'The segment never closes', 'Compression', 'Replication'], answer=1, why='Use segment.ms.')])
REVISION = ['Partition = chain of segments; only the active one is written.', 'Files: .log, .index, .timeindex, .snapshot, leader-epoch-checkpoint, partition.metadata.',
    'Name = 20-digit base offset (lab: 0, 3413, 6830).', 'Roll: segment.bytes (1 GiB, min 1 MiB), segment.ms (7 days), index full.', 'Active indexes pre-allocated 10 MiB, trimmed on close.', 'Retention/compaction/tiering work on closed segments.']
FAQ = [('Does Kafka fsync every write?', 'No. It writes to the OS page cache and relies on replication for durability; flush.messages/flush.ms exist but are rarely changed.'),
    ('Can I read segment files directly?', 'Yes, with kafka-dump-log.sh, for debugging. Never edit them while the broker runs.'),
    ('What is in partition.metadata?', 'The topic id, so a re-created topic with the same name cannot be confused with old data.'),
    ('Do followers have the same segment names?', 'Usually the same offsets, but followers roll on their own; segment boundaries can differ between replicas.')]
PRACTICE_INTRO = 'Segment programs.'
PROBLEMS = [
    dict(level='easy', title='Pad', stmt='Format 42 as a segment name.', inp='42', code='print(f"{42:020d}.log")\n', explain='20 digits.'),
    dict(level='easy', title='Segments', stmt='3 MB of data with 1 MiB segments.', inp='3 MB', code='import math\nprint(math.ceil(3 * 1_000_000 / 1_048_576))\n', explain='3.'),
    dict(level='easy', title='Batches per segment', stmt='1 MiB / 3,011-byte batches.', inp='numbers', code='print(1_048_576 // 3011)\n', explain='348 batches.'),
    dict(level='medium', title='Pick segment', stmt='Segment for offset 7000.', inp='bases', code='bases = [0, 3413, 6830]\nprint(max(b for b in bases if b <= 7000))\n', explain='6830.'),
    dict(level='medium', title='Roll by time', stmt='Segments per day with segment.ms 1 hour.', inp='24', code='print(24)\n', explain='At least 24.'),
    dict(level='medium', title='Parse name', stmt='Base offset from a file name.', inp='name', code='print(int("00000000000000003413.log".split(".")[0]))\n', explain='3413.'),
    dict(level='business', title='Disk per replica', stmt='3 MB × 3 replicas.', inp='numbers', code='print(3 * 3, "MB")\n', explain='RF multiplies.'),
    dict(level='business', title='Files per broker', stmt='1,000 partitions × 10 segments × 4 files.', inp='numbers', code='print(1000 * 10 * 4)\n', explain='40,000 files.')]
SCN_INTRO = 'Storage interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“How is a Kafka partition stored?”', 'Explain.', 'answer?', '<p>As a directory of segments. Each segment has a .log of record batches plus .index and .timeindex, named by base offset. Only the active segment is appended; closed segments are immutable and deleted or compacted as a whole.</p>', '“In a database.”') +
    scn('Platform', 'Mid-level', 'Retention not working', 'Data older than retention is still there.', 'cause?', '<ul><li>Active segment never rolled.</li><li>Lower segment.ms.</li><li>Check retention check interval.</li></ul>', '“Kafka ignores retention.”') +
    scn('Platform', 'Mid-level', 'File limits', 'Broker crashes with too many open files.', 'fix?', '<ul><li>Raise ulimit and vm.max_map_count.</li><li>Fewer/larger segments, fewer partitions.</li></ul>', 'Restarting repeatedly.') +
    scn('Platform', 'Senior', 'Segment sizing', 'Choose segment settings for a 2 TB/day topic with 3-day retention.', 'design?', '<ul><li>Default 1 GiB is fine (thousands of segments).</li><li>segment.ms bounds deletion delay.</li><li>Consider tiered storage for longer history.</li></ul>', 'Tiny segments.'))
