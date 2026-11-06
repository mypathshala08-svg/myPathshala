import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l41_segments.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('Kafka stored 10,000 orders in a file named 00000000000000003413.log. Why that strange name?',
    'A partition is not one big file. It is a chain of <b>segments</b>, each named after the first offset inside it. We forced Kafka to roll segments, listed every file it created, and found two tiny surprises: a minimum segment size, and index files that shrink when a segment is closed.',
    ['Why a partition is split into segments at all.',
     'What each of the 5 file types in a partition folder is for.',
     'Which segment is “active”, and why only it is written.'])
cmap = concept_map('Concept map. Beginner: commit log, partition folder, segment. Intermediate: segment.bytes and segment.ms, active segment, base offset names, producer snapshots. Advanced: indexes, retention by segment, compaction, tiered storage.',
    [[('cl', 'Commit log', 'append-only', B + '01-introduction/01-what-is-kafka/'), ('pf', 'Partition folder', 'topic-partition', B + '01-introduction/03-kafka-architecture/'), ('sg', 'Segment', '.log file', None)],
     [('rl', 'Roll rules', 'segment.bytes / .ms', None), ('ac', 'Active segment', 'only one written', None), ('bn', 'Base offset name', '20 digits', None), ('sn', 'Snapshots', 'producer state', None)],
     [('ix', 'Indexes', 'Lesson 4.2', B + '04-storage-internals/02-indexes-and-how-a-read-works/'), ('rt', 'Retention + compaction', 'Lesson 4.3', B + '04-storage-internals/03-retention-and-compaction/'), ('ts', 'Tiered storage', 'Lesson 4.4', B + '04-storage-internals/04-tiered-storage-and-zero-copy/')]],
    [('cl', 'sg'), ('pf', 'sg'), ('sg', 'rl'), ('rl', 'ac'), ('sg', 'bn'), ('ac', 'sn'), ('bn', 'ix'), ('rl', 'rt'), ('rt', 'ts')],
    {'cl', 'pf', 'sg', 'rl', 'ac', 'bn', 'sn'},
    '<b>Builds on:</b> <a href="../../01-introduction/03-kafka-architecture/">1.3</a>, <a href="../../02-producers/03-batching-and-compression/">2.3</a>. <b>Next:</b> <a href="../02-indexes-and-how-a-read-works/">4.2 Indexes</a>.')
whw = why_how_where(
    'One endless file could never be cleaned up cheaply: deleting old data would mean rewriting it. Segments let Kafka delete or compact whole files.',
    'Each partition appends to its active segment; when it reaches segment.bytes or segment.ms, Kafka closes it and starts a new one named after the next offset.',
    'Every Kafka topic; segment size affects retention granularity, file handles, recovery time and tiered storage uploads.',
    'Very small segments create thousands of files and open handles; very large ones delay retention and compaction.')

segs = [('00…000.log', '0 – 3,412', 'closed', 'green'), ('00…3413.log', '3,413 – 6,829', 'closed', 'green'), ('00…6830.log', '6,830 – 9,999', 'ACTIVE', 'acc')]
sc_ = ''.join(box(14 + k * 206, 30, 196, 70, tone, rx=8) + icon('disk', 22 + k * 206, 38, 0.9) + t(52 + k * 206, 52, n, 8.4, 'ink', anchor='start', bold=True, mono=True) + t(112 + k * 206, 72, 'offsets ' + r, 8, 'ink2') + t(112 + k * 206, 88, s, 7.8, 'acc' if s == 'ACTIVE' else 'green', bold=True) + (arrow(210 + k * 206, 65, 220 + k * 206, 65, 'ink3', 1.4) if k < 2 else '') for k, (n, r, s, tone) in enumerate(segs))
sc_ += t(320, 120, 'partition seg-41-0 · 10,000 orders · segment.bytes = 1 MiB · new records go only to the active segment', 8, 'ink2')
scene_svg = scene('Partition seg-41-0 split into three segments: offsets 0 to 3,412 and 3,413 to 6,829 are closed; offsets 6,830 to 9,999 are in the active segment.', sc_,
                  'A partition is a <tspan font-weight="700" class="s-acc">chain of segment files</tspan>.')
dialogue = '''R> Sir, in Lesson 1.3 each partition was a folder. Is all the data in one file?
A> No. A partition is a chain of <b>segments</b>. Kafka writes only to the newest one, the <b>active</b> segment. When it gets big or old enough, Kafka closes it and opens another.
K> Why bother?
A> Because deleting old data then means deleting a whole old file, not rewriting a giant one. Let’s make segments small so we can watch them roll.'''

lv = '''
LEVELS> Segments at three levels
L1> A register with numbered notebooks
      <ul>
        <li>The order clerk writes in notebook #1 until it is full, then starts notebook #3413, named after the first order number in it. Old notebooks are closed and can be thrown away whole.</li>
      </ul>
L2> The files in a partition folder
      <ul>
        <li><code>.log</code>: the record batches (Lesson 2.3’s format). <code>.index</code>: offset → byte position. <code>.timeindex</code>: timestamp → offset (Lesson 4.2).</li>
        <li><code>.snapshot</code>: producer state (producer ids and sequences for idempotence, Lesson 2.5) at that segment boundary, so restarts do not need to scan everything.</li>
        <li><code>leader-epoch-checkpoint</code> and <code>partition.metadata</code> (topic id) for replication safety.</li>
      </ul>
L3> Roll rules and limits
      <ul>
        <li>A new segment is rolled when the active one would exceed <code>segment.bytes</code> (default 1 GiB; minimum 1 MiB in Kafka 4.x), or is older than <code>segment.ms</code> (7 days), or its index is full.</li>
        <li>Indexes of the active segment are pre-allocated (<code>segment.index.bytes</code>, 10 MiB) and trimmed to their real size when the segment closes.</li>
        <li>Each segment is a few open file handles; brokers with thousands of partitions need high <code>ulimit -n</code> and <code>vm.max_map_count</code>.</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of a partition folder: closed segment files with trimmed index sizes, the active segment with 10 MB pre-allocated index files, producer state snapshot files, the leader epoch checkpoint and partition metadata.',
    t(16, 22, '/var/lib/kafka/data/seg-41-0  (sizes in bytes)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('1,047,693 …0000.log', 'green', 1), ('1,488 …0000.index', 'blue', 2), ('516 …0000.timeindex', 'blue', None)]) +
    fields(16, 70, [('971,323 …6830.log', 'acc', 3), ('10,485,760 …6830.index', 'amber', 4), ('10 …6830.snapshot', 'violet', 5)]) +
    fields(16, 106, [('8 leader-epoch-checkpoint', 'card', 6), ('43 partition.metadata', 'card', None)]) +
    legend(16, 152, [(1, 'Closed segment', 'just under 1 MiB: the next batch would not fit, so Kafka rolled'),
                     (2, 'Trimmed index', 'shrunk to its real size when the segment closed'),
                     (3, 'Active segment', 'the only file receiving new batches'),
                     (4, 'Pre-allocated index', '10 MiB reserved while active'),
                     (5, 'Producer snapshot', 'idempotence state at the segment boundary'),
                     (6, 'Epoch checkpoint', 'which leader epoch started at which offset')], size=8, gap=15, w=120),
    h=252, caption='Real file sizes from our lab.')
extra = '''

  <h3>Dissect a partition folder</h3>
''' + DIS

types_html = table(['Setting', 'Default', 'Effect'], [
    ['segment.bytes', '1 GiB (min 1 MiB)', 'roll when the active segment is this big'],
    ['segment.ms', '7 days', 'roll at least this often (even if small)'],
    ['segment.index.bytes', '10 MiB', 'pre-allocated index size; roll when full'],
    ['segment.jitter.ms', '0', 'random delay to avoid all partitions rolling at once'],
    ['log.dirs', 'broker setting', 'one or more disks; partitions spread across them'],
], minw=560) + table(['File', 'Contains', 'Read by'], [
    ['NNN.log', 'record batches', 'fetch, replication, dump-log'],
    ['NNN.index', 'offset → position (sparse)', 'fetch by offset'], ['NNN.timeindex', 'timestamp → offset (sparse)', 'offsetsForTimes, time retention'],
    ['NNN.snapshot', 'producer ids, sequences', 'restart, idempotence'], ['leader-epoch-checkpoint', 'epoch → start offset', 'replica truncation'],
], minw=560)
warn = 'Kafka 4.x rejects <code>segment.bytes</code> below 1 MiB (our first attempt failed with “Value must be at least 1048576”). Tiny segments were a common trick in old tutorials; with real traffic they mean huge file counts and slow restarts.'

steps = [
    ('Step 1 · Try a tiny segment',
     code('python', 'l41_segments.py', 'fresh("seg-41", 1, 3, {"segment.bytes": "16384"})', sec('== 0)', '== 1)')),
     'Kafka 4.4 refuses: the minimum is 1 MiB. So we used exactly 1 MiB and wrote 10,000 orders of about 300 bytes each.'),
    ('Step 2 · The folder',
     code('bash', 'terminal', 'cd /var/lib/kafka/data/seg-41-0 && stat -c "%10s  %n" *', sec('== 1)', '== 2)')),
     'Three segments. The two closed ones are just under 1 MiB with small, trimmed indexes; the active one has 10 MiB pre-allocated <code>.index</code> and <code>.timeindex</code> files. <code>.snapshot</code> files appear at segment boundaries.'),
    ('Step 3 · Names are base offsets',
     code('bash', 'terminal', 'ls *.log\nkafka-dump-log.sh --files 00000000000000003413.log | head -2', sec('== 2)', '== 4)')),
     'The second file is called <code>…3413.log</code> because its first batch starts at offset 3413, at byte position 0. To find offset 5000 Kafka only has to compare file names (Lesson 4.2).'),
    ('Step 4 · Offsets and size',
     code('bash', 'terminal', 'kafka-get-offsets.sh --topic seg-41 --time -2    # log start\nkafka-get-offsets.sh --topic seg-41 --time -1    # log end\nkafka-log-dirs.sh --describe --topic-list seg-41', sec('== 4)')),
     'Log start 0, log end 10,000. About 3 MB on each of the 3 brokers: replication multiplies disk use.'),
]

see = [term([('segment.bytes=16384:', W), ('Value must be at least 1048576', RD)], size=7.2),
       term([('1047693  …0000.log', W), ('1048092  …3413.log', W), (' 971323  …6830.log (active)', Y), ('10485760 …6830.index', Y)], size=7.0),
       term([('00000000000000003413.log', G), ('baseOffset: 3413 position: 0', W)], size=7.2),
       term([('log start seg-41:0:0', W), ('log end   seg-41:0:10000', W), ('3,067,108 bytes × 3 brokers', W)], size=7.0)]
def chain(n_active, note, tone):
    o = t(180, 14, note, 9, bold=True)
    for k in range(3):
        o += box(14 + k * 115, 50, 105, 40, 'acc' if k == n_active else ('green' if k < n_active else 'card'), rx=6) + t(66 + k * 115, 74, ['0', '3413', '6830'][k], 9, 'ink', bold=True, mono=True)
    return o + cap(note, '', tone, y=144, h=30)
B1 = [chain(0, 'Minimum 1 MiB', 'red'), chain(2, 'Two closed, one active', 'green'), chain(1, 'Name = first offset', 'blue'), chain(2, 'Replicated 3×', 'blue')]
two = anim_two('The commit log and segments', 'Roll, name, replicate', 'Real outputs from the lab', 'The segment chain', see, B1, ['Limit.', 'Folder.', 'Names.', 'Size.'], ['Refused.', 'Roll.', 'Base offset.', 'Copies.'])
pe = peel('A batch arrives at the leader', 'Where it is written. (Simplified.)',
    [('Produce request', ''), ('Validate', ''), ('Active segment', ''), ('Append', ''), ('Index entry?', ''), ('Roll?', '')],
    [['Produce request', 'batch for seg-41-0', '10 records, 3,011 bytes', ''], ['Validate', 'CRC, sequence (idempotence)', 'assign offsets', ''],
     ['Active segment', '…6830.log', 'is the only writable file', ''], ['Append', 'write at the end', '(page cache, sequential)', ''],
     ['Index entry?', 'every index.interval.bytes', 'add offset → position', 'and time → offset'], ['Roll?', 'next batch > segment.bytes', 'or segment.ms passed →', 'close, open new file']],
    ['Arrive.', 'Check.', 'Pick file.', 'Write.', 'Index.', 'Roll.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Too many open files', 'Small segments at scale. (Typical.)', ('Segment sizing', 'Keep segments large enough; raise file limits'), [
    ('Broker with 4,000 partitions', 'segment.ms = 1 hour', 'Many segments.', 'blue'), ('Each segment = 3+ files', 'mmap’d indexes', '100k+ handles.', 'amber'),
    ('Broker crashes', '“Too many open files”', 'Outage.', 'red'), ('Raise ulimit, vm.max_map_count', 'bigger segments', 'Defaults are sane.', 'green'),
    ('Stable', 'fewer files', 'Fixed.', 'blue')], ['Many.', 'Handles.', 'Crash.', 'Tune.', 'Stable.'], 'scenario-files') + \
       five('Real-time scenario 2', 'Retention that never deletes', 'Huge segments, low traffic. (Typical.)', ('Retention granularity', 'Only closed segments can be deleted'), [
    ('Topic retention 1 day', 'segment.bytes 1 GiB', 'Low traffic.', 'blue'), ('Segment never fills', 'active for 7 days', 'Cannot delete.', 'red'),
    ('Data kept 7+ days', 'compliance risk', 'Surprise.', 'red'), ('Set segment.ms = 1 hour', 'segments roll hourly', 'Deletable.', 'green'),
    ('Retention works', 'Lesson 4.3', 'Fixed.', 'blue')], ['Config.', 'No roll.', 'Too long.', 'Fix.', 'Works.'], 'scenario-granularity') + \
       five('Real-time scenario 3 · advanced', 'Slow restart after a crash', 'Log recovery. (Typical.)', ('Recovery', 'Unflushed segments are checked on unclean restart'), [
    ('Broker killed (power loss)', 'no clean shutdown', 'Recovery needed.', 'red'), ('Active segments re-validated', 'CRCs, indexes rebuilt', 'Takes time.', 'amber'),
    ('Snapshots help', 'producer state not rescanned', 'Faster.', 'green'), ('num.recovery.threads.per.data.dir', 'parallel recovery', 'Tune.', 'green'),
    ('Replication covers data', 'followers serve meanwhile', 'No loss with RF 3.', 'blue')], ['Crash.', 'Validate.', 'Snapshots.', 'Threads.', 'Safe.'], 'scenario-recovery')
assemble(HERE, h2_story='Why is my data in “…3413.log”?', hook_html=hk,
    narration='Kabir opens a broker’s data folder during an incident and sees files named <code>00000000000000003413.log</code>, <code>.index</code>, <code>.snapshot</code>. Riya asks what each of them is.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='The commit log and segments',
    formal='Each partition replica is stored as a <b>log</b>: an ordered sequence of <b>segments</b> in the partition directory. A segment consists of a <code>.log</code> file holding record batches and associated <code>.index</code> and <code>.timeindex</code> files, named by the segment’s <b>base offset</b> (20 digits). Only the last, <b>active</b> segment is appended to; Kafka <b>rolls</b> a new active segment when <code>segment.bytes</code>, <code>segment.ms</code> or the index size limit is reached. Closed segments are immutable and are the unit of retention, compaction and tiered-storage upload.',
    simple='A partition is a series of files. Kafka writes only to the newest file; when it is full or old, Kafka starts a new one named after the first record number it will hold. Old files are never changed, only deleted or cleaned as a whole.',
    term_rows=[('Segment', 'One file of a partition’s log.'), ('Active segment', 'The one being written.'), ('Base offset', 'First offset in a segment (its name).'), ('Roll', 'Close the active segment, open a new one.'), ('segment.bytes', 'Size that triggers a roll.'), ('segment.ms', 'Age that triggers a roll.'), ('.snapshot', 'Producer state checkpoint.'), ('log.dirs', 'Broker data directories.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('A partition is one big file.', 'It is a chain of segment files.', 'Step 2: three segments.'),
               ('Segment names are random ids.', 'They are the base offset of the first record.', 'Step 3: …3413.log starts at 3413.'),
               ('You can set segments as small as you like.', 'Kafka 4.x enforces a 1 MiB minimum for segment.bytes.', 'Step 1.')],
    exam='“How does Kafka store a partition on disk?” As a directory of segments; each has .log (record batches), .index (offset→position), .timeindex (time→offset), named by base offset; only the active segment is appended; roll on segment.bytes/segment.ms; retention and compaction work per closed segment.',
    types_h2='Settings and files', types_html=types_html, warn=warn,
    steps_h2='Make segments roll', steps_intro='All outputs are real: Kafka 4.4.0, 3 brokers; topic <code>seg-41</code>, 1 partition, RF 3, <code>segment.bytes=1048576</code>; 10,000 JSON orders of about 300 bytes. Script: <code>jobs/m4/l41_segments.py</code>.',
    steps=steps, two=two, peel_intro='Now peel where one batch is written.', peel_html=pe,
    scen_intro='Three live scenarios: too many files, retention that never deletes, and slow recovery.', scen=scen,
    uc_h2='Segments at work', ucs=[uc_('ops', 'disk', 'blue', '1. Capacity planning', 'Segments explain disk use per partition and replica.', ['Partitions', '*segments', 'GB']),
        uc_('ret', 'cleanup', 'green', '2. Retention', 'Old segments are deleted whole (Lesson 4.3).', ['Old files', '*delete', 'Free disk']),
        uc_('tier', 'cloud', 'violet', '3. Tiered storage', 'Closed segments are uploaded to object storage (4.4).', ['Segment', '*upload', 'S3']),
        uc_('debug', 'dump', 'acc', '4. Debugging', 'kafka-dump-log reads segments directly during incidents.', ['Issue', '*dump-log', 'Evidence']),
        uc_('backup', 'files', 'blue', '5. Recovery', 'Snapshots and indexes speed up broker restarts.', ['Restart', '*snapshots', 'Fast'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../../01-introduction/03-kafka-architecture/">1.3 Architecture</a> and <a href="../../02-producers/03-batching-and-compression/">2.3 Batches</a>.')
