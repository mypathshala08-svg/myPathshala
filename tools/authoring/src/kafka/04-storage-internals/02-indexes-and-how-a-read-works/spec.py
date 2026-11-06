import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
BODY = body(HERE)
META = dict(module='04-storage-internals', lesson='02-indexes-and-how-a-read-works', n='4.2', module_label='Module 4 · Storage internals',
    title='Indexes and how a read works',
    desc='How a Kafka broker finds an offset: choose the segment by base-offset file name, binary-search the sparse memory-mapped offset index, scan a few batches; and how the time index turns timestamps into offsets. Real Kafka 4.4 lab: offset 5000 located by hand via segment 3413 and index entry 4999 → byte 488000, the 185-entry index dissected, and a consumer fetching offset 5000.',
    og_desc='Find offset 5000 without reading 4,999 records: Kafka’s segment names, sparse index and time index, done by hand.',
    minutes=22, level='Intermediate',
    lead='How does Kafka jump straight to offset 5,000? We do the broker’s <b>three-step lookup by hand</b> on a real partition: file names, the <b>sparse offset index</b>, a short scan, plus the <b>time index</b>. <b>All outputs are real.</b>',
    chips=['Lookup done by hand', 'Sparse index dissected', 'Time index', 'Runs in your browser (Python)'])
MAIN = '''# Kafka's read path: segment by name, floor in a sparse index, short scan
import bisect
segments = [0, 3413, 6830]                       # base offsets (file names)
index_3413 = [(3442, 6022), (3462, 12044), (4999, 488000), (5020, 494022)]  # (offset, byte position)
batches = [(4999, 4999, 488000), (5000, 5000, 488356), (5001, 5010, 488712)]  # (base, last, position)

target = 5000
seg = segments[bisect.bisect_right(segments, target) - 1]
offs = [o for o, _ in index_3413]
off, pos = index_3413[bisect.bisect_right(offs, target) - 1]
print("1) segment:", seg)
print("2) index floor:", off, "-> byte", pos)
for base, last, p in batches:
    if p >= pos and base <= target <= last:
        print("3) found in batch", base, "-", last, "at byte", p)
        break
'''
RUN = dict(heading='Run the code: the three-step lookup', intro='<p>The broker’s algorithm with our lab’s numbers. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('seg = segments[bisect.bisect_right(segments, target) - 1]', 'Largest base offset ≤ target: pick the file.'), ('off, pos = index_3413[bisect.bisect_right(offs, target) - 1]', 'Floor entry in the sparse index: jump close.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Then look for 7000.', code=None),
        dict(label='2 · Predict first: entries', hint='<b>Predict first:</b> 1 MiB segment, one entry per ~6 KB?', code='print(1_048_576 // 6022)\n'),
        dict(label='3 · Index size', hint='185 entries × 8 bytes.', code='print(185 * 8)\n'),
        dict(label='4 · Time lookup', hint='First offset at or after a timestamp.', code='tidx = [(1000, 3422), (1028, 3501), (1077, 3600)]\nprint(next(o for t, o in tidx if t >= 1020))\n'),
        dict(label='5 · Spot the error', hint='Offset before log start.', expect='error', code='log_start, target = 301, 100\nif target < log_start:\n    raise LookupError("OFFSET_OUT_OF_RANGE: auto.offset.reset decides where to start")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: read the indexes', intro='<p>Inside the broker container. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Offset index', cmd='kafka-dump-log.sh --files /var/lib/kafka/data/seg-41-0/00000000000000003413.index | head -3', file='terminal', output='offset: 3442 position: 6022\noffset: 3462 position: 12044', note='Sparse entries.'),
           dict(title='2 · Time index', cmd='kafka-dump-log.sh --files /var/lib/kafka/data/seg-41-0/00000000000000003413.timeindex | head -2', file='terminal', output='timestamp: 1793896851338 offset: 3422', note='Time → offset.'),
           dict(title='3 · Offset by time', cmd='kafka-get-offsets.sh --bootstrap-server localhost:9092 --topic seg-41 --time 1793896851366', file='terminal', output='seg-41:0:<offset>', note='Uses the time index.')])
TRACE = dict(heading='Floor in a sorted list', intro='<p>Binary search, as in the broker.</p>',
    code='import bisect\noffs = [3442, 3462, 4999, 5020]\ni = bisect.bisect_right(offs, 5000) - 1\nprint("floor:", offs[i])\n',
    notes={3: 'Search :: Index of the last entry ≤ 5000.', 4: 'Floor :: 4999, then scan forward.'})
WORKED_INTRO = 'Three index decisions.'
EXAMPLES = [
    dict(level='b', tag='Index · lookup', title='Which segment?', problem='<p>Offset 9000 in our partition.</p>', inp='bases',
         approach=['Sort base offsets.', 'Largest ≤ 9000.', 'Open that segment.'], code='bases = [0, 3413, 6830]\nprint(max(b for b in bases if b <= 9000))\n', notes={1: 'Names :: No data read.'}, tryit='Step 1.'),
    dict(level='i', tag='Index · tuning', title='index.interval.bytes trade-off', problem='<p>Faster seeks vs bigger index files.</p>', inp='intervals',
         approach=['Entries ≈ segment / interval.', 'Bytes = entries × 8.', 'Scan ≤ interval per seek.'], code='for iv in (1024, 4096, 65536):\n    print(iv, "->", 1_048_576 // iv * 8, "bytes of index; scan <=", iv, "bytes")\n', notes={1: 'Default 4 KB :: Good balance.'}, tryit='Types table.'),
    dict(level='a', tag='Index · time', title='Trustworthy timestamps', problem='<p>Producers have skewed clocks.</p>', inp='topic config',
         approach=['message.timestamp.type=LogAppendTime.', 'Broker stamps time at append.', 'Time index becomes monotonic.'], code='print({"message.timestamp.type": "LogAppendTime"})\n', notes={1: 'Safe :: Time resets behave.'}, tryit='Warn box.')]
QUIZ = mix([
    dict(q='Beginner: To find a segment, Kafka compares…', options=['Record values', 'Segment file names (base offsets)', 'Timestamps only', 'Keys'], answer=1, why='Step 1.'),
    dict(q='Beginner: The offset index maps…', options=['Key → value', 'Offset → byte position', 'Time → key', 'Partition → broker'], answer=1, why='.index.'),
    dict(q='Beginner: The time index maps…', options=['Timestamp → offset', 'Offset → time', 'Key → time', 'Broker → time'], answer=0, why='.timeindex.'),
    dict(q='Intermediate: Why is the index sparse?', options=['Bug', 'Small and fast; a short scan finishes the job', 'Compression', 'Replication'], answer=1, why='~1 entry per 4 KB.'),
    dict(q='Intermediate: Our index had 185 entries and was…', options=['10 MiB', '1,480 bytes', '185 KB', '8 bytes'], answer=1, why='8 bytes each.'),
    dict(q='Intermediate: Floor entry for 5000 pointed to…', options=['Offset 5000', 'Offset 4999 at byte 488000', 'Offset 0', 'Offset 6830'], answer=1, why='Step 3.'),
    dict(q='Advanced: Index files are accessed via…', options=['SQL', 'Memory mapping (mmap)', 'HTTP', 'ZooKeeper'], answer=1, why='Fast lookups.'),
    dict(q='Advanced: Searching by record key needs…', options=['.index', 'An external store / Streams state', '.timeindex', 'A bigger interval'], answer=1, why='Not indexed by key.')])
REVISION = ['Read path: segment by base-offset name → binary search .index → scan .log.', 'Lab: target 5000 → segment 3413 → index 4999 → byte 488000 → batch 5000.',
    'Sparse: entry per index.interval.bytes (4 KB); 185 entries = 1,480 bytes.', '.timeindex: timestamp → offset; used by --to-datetime, offsetsForTimes, time retention.', 'Indexes are mmap’d; no key index.']
FAQ = [('What if an index is corrupt?', 'After an unclean shutdown Kafka rebuilds indexes of affected segments from the .log during recovery.'),
    ('Do consumers see the index?', 'No; it is internal to the broker. Consumers only send offsets.'),
    ('Why does the fetch return records before my offset?', 'Fetches return whole batches; the client drops records before the requested offset.'),
    ('Does compaction change the index?', 'Cleaned segments are rewritten with new indexes; offsets stay the same with gaps.')]
PRACTICE_INTRO = 'Index programs.'
PROBLEMS = [
    dict(level='easy', title='Entries', stmt='Index entries for 1 MiB at 4 KB.', inp='numbers', code='print(1_048_576 // 4096)\n', explain='256 maximum.'),
    dict(level='easy', title='Bytes', stmt='Index size for 256 entries.', inp='256', code='print(256 * 8)\n', explain='2,048 bytes.'),
    dict(level='easy', title='Relative offset', stmt='Offset 5000 in segment 3413.', inp='numbers', code='print(5000 - 3413)\n', explain='Stored as 1587.'),
    dict(level='medium', title='Floor', stmt='Floor of 5000 in [3442, 4999, 5020].', inp='list', code='print(max(x for x in [3442, 4999, 5020] if x <= 5000))\n', explain='4999.'),
    dict(level='medium', title='Scan bytes', stmt='Bytes scanned from 488000 to 488356.', inp='numbers', code='print(488356 - 488000)\n', explain='356 bytes.'),
    dict(level='medium', title='Time to offset', stmt='First offset with ts ≥ 1050.', inp='pairs', code='t = [(1000, 3422), (1028, 3501), (1077, 3600)]\nprint(next(o for ts, o in t if ts >= 1050))\n', explain='3600.'),
    dict(level='business', title='Saved reads', stmt='Bytes not read thanks to the index (488,000).', inp='numbers', code='print(round(488000 / 1024), "KiB skipped")\n', explain='Per seek.'),
    dict(level='business', title='Replay speed', stmt='Seeks per second if each takes 0.2 ms.', inp='0.2 ms', code='print(int(1000 / 0.2))\n', explain='Thousands per second.')]
SCN_INTRO = 'Index interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“How does Kafka read from an offset?”', 'Explain.', 'answer?', '<p>The broker picks the segment whose base offset is the largest ≤ target, binary-searches its sparse offset index for the nearest earlier entry, then scans forward in the .log to the batch containing the offset.</p>', '“It scans from the start.”') +
    scn('Data engineering', 'Mid-level', 'Replay by time', 'How do you replay from yesterday 6 pm?', 'answer?', '<ul><li>reset-offsets --to-datetime (or offsetsForTimes).</li><li>Time index → offsets per partition.</li><li>Check producer timestamps.</li></ul>', 'Searching values.') +
    scn('Platform', 'Mid-level', 'Slow consumers', 'A lagging group slows the whole broker.', 'explain?', '<ul><li>Index lookup is cheap; reading old segments hits disk and evicts page cache.</li><li>Throttle (quotas), tiered storage.</li></ul>', '“The index is too big.”') +
    scn('Platform', 'Senior', 'Key lookups', 'Product wants Kafka as an order lookup API.', 'design?', '<ul><li>Kafka has no key index.</li><li>Materialise to a DB or Kafka Streams interactive queries.</li><li>Keep Kafka as the log.</li></ul>', 'Scanning topics per request.'))
