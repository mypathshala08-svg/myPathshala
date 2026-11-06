import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l42_index.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('A consumer asked for order 5,000 out of 10,000. Kafka found it without reading the first 4,999. How?',
    'Kafka uses three cheap lookups: compare <b>file names</b> to pick the segment, jump with a <b>sparse index</b> to a nearby byte position, then scan a few batches. We performed each step by hand on a real partition and then let a consumer do it.',
    ['Why Kafka’s index has only one entry every few KB, not one per record.',
     'How “give me orders from 10:00” works without a database.',
     'Why reading old data is still fast.'])
cmap = concept_map('Concept map. Beginner: offset lookup, segment by name. Intermediate: sparse offset index, time index, index.interval.bytes, binary search. Advanced: memory-mapped indexes, offsetsForTimes, page cache and zero-copy.',
    [[('lk', 'Find an offset', 'seek / fetch', B + '01-introduction/04-topics-partitions-and-offsets/'), ('sn', 'Segment by name', 'Lesson 4.1', B + '04-storage-internals/01-the-commit-log-and-segments/')],
     [('oi', 'Offset index', 'offset → position', None), ('ti', 'Time index', 'time → offset', None), ('iv', 'index.interval.bytes', 'sparseness', None), ('bs', 'Binary search', 'floor entry', None)],
     [('mm', 'Memory-mapped', 'mmap', None), ('ot', 'offsetsForTimes', 'seek by time', B + '03-consumers/03-offsets-commits-and-lag/'), ('zc', 'Page cache + zero-copy', 'Lesson 4.4', B + '04-storage-internals/04-tiered-storage-and-zero-copy/')]],
    [('lk', 'sn'), ('sn', 'oi'), ('oi', 'bs'), ('iv', 'oi'), ('ti', 'ot'), ('oi', 'mm'), ('bs', 'zc')],
    {'lk', 'sn', 'oi', 'ti', 'iv', 'bs', 'mm'},
    '<b>Builds on:</b> <a href="../01-the-commit-log-and-segments/">4.1</a>. <b>Next:</b> <a href="../03-retention-and-compaction/">4.3 Retention and compaction</a>.')
whw = why_how_where(
    'Consumers start at arbitrary offsets (restarts, replays, lagging groups) and by time (“since 10:00”). Scanning gigabytes for each request would be far too slow.',
    'Pick the segment by base offset, binary-search its sparse offset index for the nearest entry at or before the target, then scan forward a few KB in the .log. Time lookups go through the time index first.',
    'Every fetch, every consumer seek, offset resets --to-datetime, retention by time, follower replication.',
    'Indexes are rebuilt on unclean shutdown; very large index intervals mean longer scans; indexes do not help search by key or value.')

sc_ = (''.join(box(14 + k * 70, 30, 62, 32, 'acc' if k == 1 else 'card', rx=4) + t(45 + k * 70, 50, b, 8, 'ink', bold=True, mono=True) for k, b in enumerate(['0', '3413', '6830'])) +
       t(115, 80, '① segment: largest base ≤ 5000', 7.8, 'acc', bold=True) +
       box(230, 30, 180, 60, 'blue', rx=6) + t(320, 46, '② .index (185 entries)', 8, bold=True) + t(320, 62, '4999 → byte 488000', 8, 'ink', mono=True) + t(320, 78, 'binary search, floor', 7.4, 'ink2') +
       arrow(410, 60, 440, 60, 'acc', 1.4) + box(440, 30, 186, 60, 'green', rx=6) + t(533, 46, '③ .log from byte 488000', 8, bold=True) + t(533, 62, 'batch 4999, batch 5000 ✓', 8, 'ink', mono=True) + t(533, 78, 'scan only a few KB', 7.4, 'ink2') +
       t(320, 118, 'offset 5000 found by reading ~0.4 KB instead of ~490 KB', 8.4, 'ink', bold=True))
scene_svg = scene('Finding offset 5000: first pick segment 3413 by comparing base offsets, then binary-search the offset index to get byte position 488000 for offset 4999, then scan the log from there to reach offset 5000.', sc_,
                  'Three cheap steps: <tspan font-weight="700" class="s-acc">name, index, short scan</tspan>.')
dialogue = '''K> Sir, the billing group was reset to offset 5000. Does the broker read the whole partition to find it?
A> Never. Segment files are named by their first offset, so it picks the right file by comparing names. Inside, a small <b>index</b> maps some offsets to byte positions. It jumps close and reads only a few batches.
R> And for “from 10:00 am”?
A> A second index maps timestamps to offsets. Let’s do the lookup ourselves with <code>kafka-dump-log</code>, step by step.'''

lv = '''
LEVELS> Indexes at three levels
L1> A book’s index
      <ul>
        <li>The library has many volumes named by first page number (segments). Each volume has an index listing every 20th page (sparse). To find page 5000: pick the volume, look up the nearest listed page, flip a few pages.</li>
      </ul>
L2> The two indexes
      <ul>
        <li><b>.index</b>: entries (relative offset, byte position), added every <code>index.interval.bytes</code> (4 KB default) of appended data.</li>
        <li><b>.timeindex</b>: entries (timestamp, offset) giving the earliest offset with a timestamp ≥ that time.</li>
        <li>Lookup: binary search for the largest entry ≤ target, then scan the log forward batch by batch.</li>
      </ul>
L3> Implementation details
      <ul>
        <li>Each offset entry is 8 bytes (4-byte relative offset + 4-byte position); time entries 12 bytes. 185 entries ≈ 1.5 KB: our closed index was exactly 1,480 bytes.</li>
        <li>Index files are <b>memory-mapped</b>; lookups touch the most recent pages first (good for tailing consumers).</li>
        <li>Batches are the unit: the index points to batch starts, and fetches return whole batches; the client discards records before the requested offset.</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of offset index entries from kafka-dump-log: offset 3442 at position 6022, offset 3462 at 12044, each entry about 6 KB apart because index.interval.bytes was 4096 and batches were 3011 bytes.',
    t(16, 22, 'kafka-dump-log of 00000000000000003413.index (first entries)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('offset: 3442', 'blue', 1), ('position: 6022', 'acc', 2)]) + fields(260, 34, [('offset: 3462', 'blue', None), ('position: 12044', 'acc', None)]) +
    fields(16, 70, [('… 185 entries', 'card', 3), ('every ~6 KB (2 batches)', 'amber', 4), ('file 1,480 bytes', 'green', 5)]) +
    legend(16, 122, [(1, 'Offset', 'stored relative to the segment base (3413) in 4 bytes'),
                     (2, 'Position', 'byte offset in the .log where that batch region starts'),
                     (3, 'Sparse', 'not every offset: one entry per ~index.interval.bytes'),
                     (4, 'Interval', '4,096-byte setting + 3,011-byte batches → an entry every 2 batches'),
                     (5, 'Size', '185 × 8 bytes = 1,480 bytes, matching the folder listing')], size=8, gap=15, w=110),
    h=210, caption='Real index entries from our lab partition.')
extra = '''

  <h3>Dissect the offset index</h3>
''' + DIS

types_html = table(['Lookup', 'Uses', 'Example'], [
    ['By offset', 'segment names + .index + scan', 'consumer seek(5000), committed offset'],
    ['By time', '.timeindex → offset, then as above', 'reset --to-datetime, offsetsForTimes'],
    ['Earliest / latest', 'log start / log end offsets', 'auto.offset.reset'],
    ['By key or value', 'not supported (scan or external index)', 'use a database or Kafka Streams store'],
], minw=600) + table(['Setting', 'Default', 'Effect'], [
    ['index.interval.bytes', '4096', 'smaller → bigger index, shorter scans'],
    ['segment.index.bytes', '10 MiB', 'max index size per segment (roll when full)'],
    ['message.timestamp.type', 'CreateTime', 'or LogAppendTime (broker time) for the time index'],
], minw=560)
warn = 'Searching by time uses record timestamps. With <code>CreateTime</code> (default) a producer with a wrong clock can write “future” or “past” timestamps that confuse time-based resets and retention. Use <code>message.timestamp.type=LogAppendTime</code> when producer clocks cannot be trusted.'

steps = [
    ('Step 1 · Pick the segment by name',
     code('python', 'l42_index.py', 'bases = [int(s.split(".")[0]) for s in segment_files]\nseg = bases[bisect.bisect_right(bases, 5000) - 1]', sec('== 1)', '== 2)')),
     'Three files; the largest base offset not above 5000 is 3413. No data was read.'),
    ('Step 2 · Look in the sparse index',
     code('bash', 'terminal', 'kafka-dump-log.sh --files /var/lib/kafka/data/seg-41-0/00000000000000003413.index', sec('== 2)', '== 3)')),
     '185 entries cover about 1 MiB of log: one entry per ~6 KB. Each says “around this offset, the batch starts at this byte”.'),
    ('Step 3 · Floor entry, then scan',
     code('python', 'l42_index.py', 'floor = max(p for p in pairs if p[0] <= 5000)     # binary search in Kafka\n# read the .log from that byte position', sec('== 3)', '== 4)')),
     'The index entry for 4999 points to byte 488,000. Reading from there, the very next batch is offset 5000. Kafka read a few hundred bytes instead of almost half a megabyte.'),
    ('Step 4 · The time index',
     code('bash', 'terminal', 'kafka-dump-log.sh --files /var/lib/kafka/data/seg-41-0/00000000000000003413.timeindex', sec('== 4)', '== 5)')),
     'Each entry maps a timestamp (ms) to an offset. “Orders since 10:00” becomes: find the timestamp in the time index, get an offset, then do Steps 1–3.'),
    ('Step 5 · A consumer does it for real',
     code('python', 'l42_index.py', 'c.assign([TopicPartition("seg-41", 0, 5000)])\nm = c.poll(1.0)', sec('== 5)')),
     'The broker performed exactly this lookup and returned offset 5000 (order o5000).'),
]

see = [term([('segments: [0, 3413, 6830]', W), ('-> segment 3413', G)], size=7.4),
       term([('offset: 3442 position: 6022', W), ('offset: 3462 position: 12044', W), ('(185 entries)', W)], size=7.2),
       term([('floor 4999 -> byte 488000', G), ('batch 4999 @488000', W), ('batch 5000 @488356 ✓', G)], size=7.2),
       term([('timestamp: …851338 offset: 3422', W), ('timestamp: …851366 offset: 3501', W)], size=7.0),
       term([('got offset 5000', G), ('{"order": "o5000", ...}', W)], size=7.2)]
def look(stage, title, tone):
    boxes = [('segment', '3413'), ('index', '4999→488000'), ('scan', '→ 5000'), ('time idx', 'ts→offset'), ('fetch', 'o5000')]
    return t(180, 14, title, 9, bold=True) + ''.join(opbox(6 + k * 70, 50, n, d, 'acc' if k == stage else 'card', 64, 34) for k, (n, d) in enumerate(boxes)) + cap(title, '', tone, y=144, h=30)
B1 = [look(0, 'Compare file names', 'blue'), look(1, 'Binary-search the index', 'blue'), look(2, 'Short forward scan', 'green'), look(3, 'Time → offset', 'violet'), look(4, 'Broker returns the batch', 'green')]
two = anim_two('Indexes and reads', 'Find offset 5000', 'Real outputs from the lab', 'Which lookup step', see, B1, ['Segment.', 'Index.', 'Scan.', 'Time.', 'Fetch.'], ['Names.', 'Sparse.', 'Floor.', 'Timestamps.', 'Done.'])
pe = peel('A Fetch request for offset 5000', 'Inside the broker. (Simplified.)',
    [('Fetch request', ''), ('Segment', ''), ('Offset index', ''), ('Position', ''), ('Read batches', ''), ('Send', '')],
    [['Fetch request', 'seg-41 P0 from 5000', 'max bytes per partition', ''], ['Segment', 'floor of base offsets', '→ …3413.log', ''],
     ['Offset index', 'mmap’d file', 'binary search → 4999', ''], ['Position', 'byte 488000', 'in the .log', ''],
     ['Read batches', 'scan to batch containing', '5000, then read up to', 'the size limit'], ['Send', 'whole batches to client', '(zero-copy when plaintext)', 'client skips < 5000']],
    ['Ask.', 'File.', 'Index.', 'Jump.', 'Read.', 'Send.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Replay from 10:00', 'Time index in action. (Typical.)', ('Seek by time', 'Time index turns a timestamp into an offset quickly'), [
    ('Bug since 10:00', 'replay billing', 'Need offsets.', 'blue'), ('--to-datetime 10:00', 'broker uses .timeindex', 'Per partition.', 'green'),
    ('Then offset index', 'jump to positions', 'Fast.', 'green'), ('Group reset done', 'seconds, not minutes', 'Even for TBs.', 'green'),
    ('Watch producer clocks', 'CreateTime skew', 'Or LogAppendTime.', 'amber')], ['Need.', 'Time idx.', 'Offset idx.', 'Reset.', 'Caveat.'], 'scenario-time') + \
       five('Real-time scenario 2', 'Lagging consumer reads old data', 'Cold reads from disk. (Typical.)', ('Old data reads', 'Indexes make the lookup cheap; disk I/O is the cost'), [
    ('Analytics group 2 days behind', 'reads old segments', 'Not in page cache.', 'amber'), ('Index lookups are cheap', 'small mmap files', 'Fast.', 'green'),
    ('But log pages come from disk', 'evict hot data', 'Others slow down.', 'red'), ('Throttle or separate brokers', 'or tiered storage', 'Lesson 4.4.', 'green'),
    ('Monitor disk reads', 'per broker', 'Ops.', 'blue')], ['Lag.', 'Index.', 'Disk.', 'Mitigate.', 'Watch.'], 'scenario-cold') + \
       five('Real-time scenario 3 · advanced', '“Find order o5000 by id”', 'Kafka is not a key-value store. (Typical.)', ('Lookups by key', 'Indexes are by offset and time only'), [
    ('Support wants order o5000', 'by order id', 'Not an offset.', 'blue'), ('Kafka has no key index', 'would scan the topic', 'Slow.', 'red'),
    ('Materialise to a store', 'Kafka Streams / DB', 'Indexed by key.', 'green'), ('Or compacted topic', 'latest per key (4.3)', 'Still no lookup.', 'amber'),
    ('Right tool', 'Kafka streams, DB queries', 'Design.', 'blue')], ['Request.', 'No index.', 'Store.', 'Compaction.', 'Tool.'], 'scenario-key')
assemble(HERE, h2_story='Finding order 5,000 without reading 4,999', hook_html=hk,
    narration='TiffinGo’s billing group was reset to offset 5000 after a bug. Riya wonders whether the broker has to read through every earlier order to get there.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Indexes and how a read works',
    formal='Each log segment has a sparse <b>offset index</b> (<code>.index</code>) mapping relative offsets to physical byte positions in the <code>.log</code>, and a <b>time index</b> (<code>.timeindex</code>) mapping timestamps to offsets; entries are added after every <code>index.interval.bytes</code> of appended data. To serve a fetch, the broker selects the segment with the greatest base offset not exceeding the target, binary-searches the memory-mapped offset index for the greatest entry not exceeding the target, and scans forward through record batches. Time-based lookups first resolve a timestamp to an offset through the time index.',
    simple='Kafka finds data in three cheap steps: pick the right file by its name, use a small table of “offset → byte position” to jump close, then read forward a little. To search by time, a second small table turns a time into an offset first.',
    term_rows=[('Offset index', 'Offset → byte position.'), ('Time index', 'Timestamp → offset.'), ('Sparse index', 'Entries only every few KB.'), ('index.interval.bytes', 'Data between entries.'), ('Floor entry', 'Largest entry ≤ target.'), ('Memory-mapped', 'File accessed like RAM.'), ('offsetsForTimes', 'API: time → offset.'), ('LogAppendTime', 'Broker-assigned timestamps.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Kafka scans the partition to find an offset.', 'It uses file names and a sparse index, then scans only a few KB.', 'Step 3.'),
               ('Kafka indexes every record.', 'One entry per ~4 KB of data (sparse).', 'Step 2: 185 entries for ~1 MiB.'),
               ('You can look up a record by key in Kafka.', 'Only by offset or time; use a store for keys.', 'Scenario 3.')],
    exam='“How does Kafka find an offset quickly?” Segment chosen by base-offset file names; sparse memory-mapped .index binary search → byte position; short scan in .log. Time lookups use .timeindex (timestamp → offset). index.interval.bytes controls sparseness.',
    types_h2='Lookups and settings', types_html=types_html, warn=warn,
    steps_h2='Do the lookup by hand', steps_intro='All outputs are real: Kafka 4.4.0; topic <code>seg-41</code> from Lesson 4.1 (10,000 orders, 3 segments, <code>index.interval.bytes=4096</code>). Script: <code>jobs/m4/l42_index.py</code>.',
    steps=steps, two=two, peel_intro='Now peel a fetch request inside the broker.', peel_html=pe,
    scen_intro='Three live scenarios: replay by time, cold reads, and lookups by key.', scen=scen,
    uc_h2='Indexes at work', ucs=[uc_('replay', 'time', 'blue', '1. Time-based replays', 'Reset groups to a time in seconds.', ['Timestamp', '*.timeindex', 'Offsets']),
        uc_('lag', 'catch-up', 'green', '2. Catching up', 'Lagging consumers jump straight to their offset.', ['Commit', '*.index', 'Fetch']),
        uc_('repl', 'followers', 'violet', '3. Replication', 'Followers fetch from the leader with the same lookup.', ['Follower', '*fetch', 'Copy']),
        uc_('ret', 'time', 'acc', '4. Time retention', 'The time index tells which segments are old.', ['Segments', '*max time', 'Delete']),
        uc_('audit', 'window', 'blue', '5. Audit windows', 'Read exactly the records between two times.', ['Start/end', '*offsetsForTimes', 'Slice'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../01-the-commit-log-and-segments/">4.1 The commit log and segments</a>.')
