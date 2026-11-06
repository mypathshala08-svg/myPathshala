import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
BODY = body(HERE)
META = dict(module='04-storage-internals', lesson='03-retention-and-compaction', n='4.3', module_label='Module 4 · Storage internals',
    title='Retention and compaction',
    desc='Kafka clean-up policies: time and size retention (retention.ms, retention.bytes), the log start offset, and log compaction with the log cleaner, tombstones, dirty ratio and delete.retention.ms. Real Kafka 4.4 lab: four segments deleted after 60 s retention with the log start jumping to 301, and a compacted menu-prices topic reduced from 11 records to the latest 3 with a deleted dish removed.',
    og_desc='Retention deleted 4 segments; compaction kept only the latest price per dish. Kafka clean-up on a real cluster.',
    minutes=24, level='Intermediate',
    lead='Kafka never deletes on read, so how does the disk not fill up? We watch <b>retention</b> delete whole segments and <b>compaction</b> keep only the <b>latest value per key</b>, tombstones included. <b>All outputs are real.</b>',
    chips=['Log start 0 → 301', '11 records → 3', 'Tombstone removed', 'Runs in your browser (Python)'])
MAIN = '''# Compaction: keep only the latest record per key; tombstones (None) delete keys
log = [(0, "thali", "120"), (1, "dosa", "80"), (2, "thali", "130"), (3, "lassi", "40"),
       (4, "dosa", "85"), (5, "thali", "140"), (6, "lassi", "45"), (7, "dosa", "90"),
       (8, "thali", "150"), (9, "vada", "30"), (10, "vada", None)]

latest = {}
for offset, key, value in log:
    latest[key] = offset                 # remember the newest offset per key

compacted = [(o, k, v) for o, k, v in log if latest[k] == o and v is not None]
print("before:", len(log), "records")
print("after :", compacted)
'''
RUN = dict(heading='Run the code: a log cleaner', intro='<p>Our lab topic, compacted in a few lines. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    latest[key] = offset                 # remember the newest offset per key', 'The cleaner builds a key → latest offset map.'), ('compacted = [(o, k, v) for o, k, v in log if latest[k] == o and v is not None]', 'Keep only the latest; drop tombstones (after delete.retention.ms).')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Then add a new dosa price.', code=None),
        dict(label='2 · Predict first: retention', hint='<b>Predict first:</b> newest record in a segment is 70 s old; retention 60 s. Deleted?', code='print(70 > 60)\n'),
        dict(label='3 · Log start', hint='After deleting segments 0, 100, 200, 300.', code='print(301)\n'),
        dict(label='4 · Size retention', hint='retention.bytes 3 MB, 1 MB segments, 5 MB data: how many deleted?', code='print(5 - 3)\n'),
        dict(label='5 · Spot the error', hint='Offset before log start.', expect='error', code='log_start, committed = 301, 50\nif committed < log_start:\n    raise LookupError("OFFSET_OUT_OF_RANGE: data was deleted by retention")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: clean-up policies', intro='<p>Topic configs with the CLI. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Short retention', cmd='kafka-configs.sh --bootstrap-server localhost:9092 --entity-type topics --entity-name ret-43 --alter --add-config retention.ms=60000,segment.ms=10000', file='terminal', output='Completed updating config for topic ret-43.', note='Lab values only.'),
           dict(title='2 · Compacted topic', cmd='kafka-topics.sh --bootstrap-server localhost:9092 --create --topic menu-prices --config cleanup.policy=compact', file='terminal', output='Created topic menu-prices.', note='Keys required.'),
           dict(title='3 · Tombstone', cmd='echo "vada:" | kafka-console-producer.sh … --reader-property parse.key=true --reader-property key.separator=: --reader-property null.marker=', file='terminal', output='(vada with a null value)', note='Deletes the key.')])
TRACE = dict(heading='Latest per key', intro='<p>A dictionary is the whole idea.</p>',
    code='latest = {}\nfor k, v in [("thali", 120), ("thali", 130), ("dosa", 80)]:\n    latest[k] = v\nprint(latest)\n',
    notes={3: 'Overwrite :: A newer value replaces the older one.', 4: 'Result :: One value per key.'})
WORKED_INTRO = 'Three clean-up decisions.'
EXAMPLES = [
    dict(level='b', tag='Retention · plan', title='Retention for orders', problem='<p>Orders must be replayable for 14 days.</p>', inp='days',
         approach=['retention.ms = 14 days.', 'segment.ms ≤ 1 day.', 'Size disks (Lesson 1.1 formula).'], code='print({"retention.ms": 14 * 86400000, "segment.ms": 86400000})\n', notes={1: 'Rule :: Retention > worst consumer outage.'}, tryit='Warn box.'),
    dict(level='i', tag='Compaction · design', title='Menu prices as a compacted topic', problem='<p>Services need current prices on startup.</p>', inp='keys',
         approach=['Key = dish id.', 'cleanup.policy=compact.', 'Tombstone to remove a dish.'], code='print({"cleanup.policy": "compact", "min.compaction.lag.ms": 60000})\n', notes={1: 'Table :: Latest value per key.'}, tryit='Scenario 2.'),
    dict(level='a', tag='Compaction · both', title='Sessions with compact,delete', problem='<p>Latest session per user, but forget users idle 30 days.</p>', inp='policy',
         approach=['cleanup.policy=compact,delete.', 'retention.ms 30 days.', 'Key = user id.'], code='print({"cleanup.policy": "compact,delete", "retention.ms": 30 * 86400000})\n', notes={1: 'Both :: Bounded and latest.'}, tryit='Types table.')]
QUIZ = mix([
    dict(q='Beginner: Default cleanup.policy is…', options=['compact', 'delete', 'none', 'archive'], answer=1, why='Time/size retention.'),
    dict(q='Beginner: Default retention.ms is…', options=['1 day', '7 days', '30 days', 'forever'], answer=1, why='604800000.'),
    dict(q='Beginner: Compaction keeps…', options=['Oldest per key', 'Latest per key', 'Every 10th record', 'Nothing'], answer=1, why='thali=150.'),
    dict(q='Intermediate: A tombstone is…', options=['A deleted segment', 'A record with a null value', 'An ABORT marker', 'A broker'], answer=1, why='Deletes a key.'),
    dict(q='Intermediate: After retention our log start offset became…', options=['0', '100', '301', '1000'], answer=2, why='Step 2.'),
    dict(q='Intermediate: Can the active segment be compacted?', options=['Yes', 'No', 'Only at night', 'Only with acks=all'], answer=1, why='Only closed segments.'),
    dict(q='Advanced: Retention deletes a segment when…', options=['Its oldest record is too old', 'Its newest record is older than retention', 'It is read', 'It is full'], answer=1, why='Largest timestamp.'),
    dict(q='Advanced: Compaction changes offsets to…', options=['Start at 0', 'Nothing: offsets are kept', 'Negative', 'Random'], answer=1, why='Gaps.')])
REVISION = ['delete policy: retention.ms (7 days) / retention.bytes; whole closed segments; log start moves.', 'Lab: segments 0,100,200,300 deleted; log start 0 → 301; judged by newest timestamp.',
    'compact policy: latest per key; tombstone = null value deletes key after delete.retention.ms.', 'Lab: 11 records → lassi 45, dosa 90, thali 150 (offsets 6, 7, 8).',
    'Cleaner: min.cleanable.dirty.ratio, min/max.compaction.lag.ms; active segment never cleaned.', 'Retention deletes unread data: alert on lag.']
FAQ = [('Can I keep data forever?', 'Yes: retention.ms=-1 (and retention.bytes=-1). Combine with tiered storage to keep costs down (Lesson 4.4).'),
    ('Is compaction instant?', 'No. It runs in the background on closed segments when the dirty ratio and lags allow; consumers may see old values for a while.'),
    ('Can a compacted topic have records without keys?', 'No: producing a null key to a compacted topic is rejected.'),
    ('Does retention apply to compacted topics?', 'Only with cleanup.policy=compact,delete.')]
PRACTICE_INTRO = 'Clean-up programs.'
PROBLEMS = [
    dict(level='easy', title='ms to days', stmt='604800000 ms.', inp='number', code='print(604800000 / 86400000)\n', explain='7 days.'),
    dict(level='easy', title='Latest', stmt='Latest thali price.', inp='list', code='print([v for k, v in [("thali", 120), ("thali", 150)] if k == "thali"][-1])\n', explain='150.'),
    dict(level='easy', title='Deleted keys', stmt='Keys whose latest value is None.', inp='dict', code='print([k for k, v in {"vada": None, "dosa": "90"}.items() if v is None])\n', explain='vada.'),
    dict(level='medium', title='Expired segments', stmt='Segments whose newest record age > 60 s.', inp='ages', code='print([s for s, age in {0: 140, 100: 125, 301: 5}.items() if age > 60])\n', explain='[0, 100].'),
    dict(level='medium', title='Dirty ratio', stmt='Dirty 300 MB of 1 GB.', inp='numbers', code='print(300 / 1000 >= 0.5)\n', explain='Not yet cleaned (0.3).'),
    dict(level='medium', title='Compact', stmt='Compact a list of (key, value).', inp='list', code='d = {}\nfor k, v in [("a", 1), ("b", 2), ("a", 3)]: d[k] = v\nprint(d)\n', explain='Latest per key.'),
    dict(level='business', title='Disk saved', stmt='1,000 dishes, 50 updates each, 200 bytes.', inp='numbers', code='print(1000 * 50 * 200 // 1024, "KiB before;", 1000 * 200 // 1024, "KiB after")\n', explain='50× smaller.'),
    dict(level='business', title='Safe retention', stmt='Longest outage 3 days; add 2× margin.', inp='3', code='print(3 * 2, "days retention")\n', explain='6+ days.')]
SCN_INTRO = 'Clean-up interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“Retention vs compaction?”', 'Explain.', 'answer?', '<p>Retention (delete policy) removes old segments by time or size. Compaction keeps only the latest record per key and removes keys with tombstones. Use retention for event streams and compaction for state such as prices or profiles.</p>', '“Compaction compresses data.”') +
    scn('Data engineering', 'Mid-level', 'Missing data', 'A group restarted and skipped two days.', 'cause?', '<ul><li>Lag exceeded retention → OFFSET_OUT_OF_RANGE.</li><li>auto.offset.reset=latest.</li><li>Alert on lag age; longer retention.</li></ul>', '“Kafka lost data.”') +
    scn('Platform', 'Mid-level', 'Old values visible', 'Consumers still see old prices on a compacted topic.', 'explain?', '<ul><li>Active segment not compacted; dirty ratio not reached.</li><li>Expected; consumers must take the latest per key.</li></ul>', '“Compaction is broken.”') +
    scn('Platform', 'Senior', 'Erasure', 'Design customer erasure across Kafka topics.', 'design?', '<ul><li>Compacted state topics: tombstones.</li><li>Event topics: bounded retention or crypto-shredding.</li><li>Document timelines.</li></ul>', 'Editing segment files.'))
