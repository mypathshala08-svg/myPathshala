import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
BODY = body(HERE)
META = dict(module='03-consumers', lesson='03-offsets-commits-and-lag', n='3.3', module_label='Module 3 · Consumers',
    title='Offsets, commits and lag',
    desc='Kafka consumer position vs committed offset, auto and manual (sync/async) commits, the __consumer_offsets topic, consumer lag and resetting offsets safely. Real Kafka 4.4 lab: a billing group commits after 120 orders, lag grows to 189 while it is down, a dry-run shift-by and a reset to earliest, and a real commit record printed from __consumer_offsets.',
    og_desc='Lag 189, a dry-run rewind and a real __consumer_offsets record: Kafka offsets and commits on a live cluster.',
    minutes=24, level='Intermediate',
    lead='How does a consumer know where to restart? We <b>commit</b> by hand, watch <b>lag</b> grow while the app is down, <b>rewind</b> the group safely, and print the bookmark from <code>__consumer_offsets</code>. <b>All outputs are real.</b>',
    chips=['Manual commit', 'Lag 189 measured', 'Dry-run reset', 'Runs in your browser (Python)'])
MAIN = '''# Position, commit and lag for one partition
log_end = 100            # next offset the producer will write
position = 0             # next offset this consumer will read
committed = None         # saved bookmark (None = never committed)

def process(n):
    global position
    position += n        # we read n records

def commit():
    global committed
    committed = position # "next to read", not "last read"

process(14); commit()
print("committed:", committed, "lag:", log_end - committed)
log_end += 103           # app down, more orders arrive
print("after outage lag:", log_end - committed)
process(50)              # read 50 more but crash before commit
print("restart resumes at:", committed, "(the 50 will be read again)")
'''
RUN = dict(heading='Run the code: position vs commit', intro='<p>Why commits matter after a crash. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    committed = position # "next to read", not "last read"', 'A commit saves the next offset to read.'), ('print("restart resumes at:", committed, "(the 50 will be read again)")', 'Uncommitted progress is re-processed after a restart.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Then commit after the 50.', code=None),
        dict(label='2 · Predict first: lag', hint='<b>Predict first:</b> end 213, committed 106. Lag?', code='print(213 - 106)\n'),
        dict(label='3 · Shift', hint='Shift-by −50 from 14 (clamp at 0).', code='print(max(0, 14 - 50), max(0, 106 - 50))\n'),
        dict(label='4 · Expiry', hint='Commits idle for 9 days with 7-day retention?', code='print("expired" if 9 > 7 else "kept")\n'),
        dict(label='5 · Spot the error', hint='Reset on an active group.', expect='error', code='active_members = 2\nif active_members:\n    raise RuntimeError("Assignments can only be reset if the group is inactive")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: lag and resets', intro='<p>CLI against your cluster. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Lag', cmd='kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group billing-33', file='terminal', output='billing-33  orders-33  0  14  203  189', note='CURRENT-OFFSET, LOG-END-OFFSET, LAG.'),
           dict(title='2 · Dry run', cmd='kafka-consumer-groups.sh --bootstrap-server localhost:9092 --reset-offsets --group billing-33 --topic orders-33:0,2 --shift-by -50 --dry-run', file='terminal', output='billing-33  orders-33  2  56\nbilling-33  orders-33  0  0', note='Nothing changed yet.'),
           dict(title='3 · By time', cmd='kafka-consumer-groups.sh --bootstrap-server localhost:9092 --reset-offsets --group billing-33 --all-topics --to-datetime 2026-11-05T10:00:00.000 --execute', file='terminal', output='(new offsets per partition)', note='Stop the group first.')])
TRACE = dict(heading='Lag over time', intro='<p>End moves, commit stays.</p>',
    code='end, committed = 100, 14\nlag = end - committed\nend += 103\nlag2 = end - committed\ncommitted = end\nprint(lag, lag2, end - committed)\n',
    notes={3: 'Outage :: New records arrive.', 5: 'Catch up :: Commit reaches the end, lag 0.'})
WORKED_INTRO = 'Three offset decisions.'
EXAMPLES = [
    dict(level='b', tag='Offsets · commit', title='Commit after each batch', problem='<p>Billing must not skip orders on crash.</p>', inp='batches',
         approach=['enable.auto.commit=false.', 'Process the batch.', 'commit(asynchronous=False).'], code='for batch in [[1, 2], [3, 4]]:\n    print("bill", batch); print("commit next =", batch[-1] + 1)\n', notes={1: 'Order :: Process, then commit.'}, tryit='Step 1.'),
    dict(level='i', tag='Offsets · async', title='Fast commits with a safe exit', problem='<p>Sync commits slow us down.</p>', inp='throughput',
         approach=['Async commit per batch.', 'Sync commit in on_revoke and on shutdown.', 'Ignore older async failures.'], code='print(["commit(async) per batch", "commit(sync) in on_revoke", "commit(sync) before close()"])\n', notes={1: 'Pattern :: Speed + safety at the edges.'}, tryit='Types table.'),
    dict(level='a', tag='Offsets · ops', title='Lag-based alert', problem='<p>Alert only on real trouble.</p>', inp='lag samples',
         approach=['Track lag per partition.', 'Alert if lag grows for 5 minutes.', 'Show time lag too.'], code='samples = [100, 300, 700, 1500, 3100]\nprint("alert:", all(b > a for a, b in zip(samples, samples[1:])))\n', notes={1: 'Trend :: Growing lag matters, not a single spike.'}, tryit='Scenario 1.')]
QUIZ = mix([
    dict(q='Beginner: Lag is…', options=['Network delay', 'Log end offset − committed offset', 'Partition count', 'Retention'], answer=1, why='Records waiting.'),
    dict(q='Beginner: A committed offset means…', options=['Last record processed', 'Next record to read', 'First record', 'Deleted offset'], answer=1, why='+1 rule.'),
    dict(q='Beginner: Commits are stored in…', options=['ZooKeeper', '__consumer_offsets', 'The client file system', 'meta.properties'], answer=1, why='Step 5.'),
    dict(q='Intermediate: enable.auto.commit=true commits…', options=['After you process', 'Every auto.commit.interval.ms, in the background', 'Never', 'Per record'], answer=1, why='5 s default.'),
    dict(q='Intermediate: Why was partition 1 missing from describe?', options=['Deleted', 'No committed offset yet', 'Leader down', 'Compression'], answer=1, why='-1001.'),
    dict(q='Intermediate: Before executing a reset you should…', options=['Restart brokers', 'Run --dry-run and stop the group', 'Delete the topic', 'Nothing'], answer=1, why='Safety.'),
    dict(q='Advanced: An idle group’s commits expire after…', options=['1 hour', 'offsets.retention.minutes (7 days)', 'Never', '1 year'], answer=1, why='Scenario 3.'),
    dict(q='Advanced: --shift-by -50 from offset 14 gives…', options=['-36', '0 (clamped)', '64', 'error'], answer=1, why='Step 3.')])
REVISION = ['Position (memory) vs committed offset (Kafka); committed = next to read.', 'Auto commit every 5 s vs manual sync/async; commit after processing.',
    'Lag = log end − committed (lab: 189 and 107 after outage).', 'Reset: --dry-run first, inactive group; to-earliest/latest/datetime/offset/shift-by.',
    '__consumer_offsets record: key group+topic+partition, value offset + metadata; compacted.', 'Offsets of empty groups expire after 7 days.']
FAQ = [('Can I store offsets outside Kafka?', 'Yes, e.g. in the same database transaction as your results; on start use seek() to that offset. Spark Structured Streaming keeps offsets in its checkpoint.'),
    ('Does commit() commit all partitions?', 'Without arguments it commits the current positions of all assigned partitions.'),
    ('What is “time lag”?', 'How old the oldest unread record is; often more meaningful than a record count for alerts.'),
    ('Can two groups share offsets?', 'No. Offsets are per group; a new group.id starts fresh according to auto.offset.reset.')]
PRACTICE_INTRO = 'Offset programs.'
PROBLEMS = [
    dict(level='easy', title='Lag', stmt='End 203, committed 14.', inp='numbers', code='print(203 - 14)\n', explain='189.'),
    dict(level='easy', title='Next offset', stmt='Commit after processing offset 41.', inp='41', code='print(41 + 1)\n', explain='42.'),
    dict(level='easy', title='Total lag', stmt='Sum per-partition lag.', inp='[189, 0, 107]', code='print(sum([189, 0, 107]))\n', explain='296.'),
    dict(level='medium', title='Clamp', stmt='Shift each offset by −50, clamp at 0.', inp='[14, 106]', code='print([max(0, o - 50) for o in [14, 106]])\n', explain='[0, 56].'),
    dict(level='medium', title='Catch-up time', stmt='Lag 30,000 at 500/s net.', inp='numbers', code='print(30000 / 500, "s")\n', explain='60 s.'),
    dict(level='medium', title='Re-processed', stmt='Read 50 after last commit, then crash.', inp='50', code='print(50, "records re-read")\n', explain='At-least-once.'),
    dict(level='business', title='Billing delay', stmt='Lag 189 orders at 3 bills/s.', inp='numbers', code='print(round(189 / 3), "s behind")\n', explain='Time lag.'),
    dict(level='business', title='Replay window', stmt='Orders in 2 hours at 50/min.', inp='numbers', code='print(2 * 60 * 50)\n', explain='6,000 to re-bill.')]
SCN_INTRO = 'Offset interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“What is consumer lag?”', 'Explain and measure.', 'answer?', '<p>The number of records between a partition’s log end offset and the group’s committed offset. Check with kafka-consumer-groups --describe or metrics; rising lag means consumers are falling behind.</p>', '“The network latency.”') +
    scn('Fintech', 'Mid-level', 'Re-processing', 'After a fix, billing must re-run the last 2 hours.', 'steps?', '<ol><li>Stop the group.</li><li>--reset-offsets --to-datetime … --dry-run, then --execute.</li><li>Start the fixed app; idempotent writes.</li></ol>', 'Deleting the topic.') +
    scn('Data engineering', 'Mid-level', 'Auto commit', 'Messages are lost when the app crashes.', 'cause?', '<ul><li>Auto-commit committed before processing finished.</li><li>Manual commit after processing.</li></ul>', '“Kafka deleted them.”') +
    scn('Platform', 'Senior', 'Monthly job', 'A monthly job reads nothing.', 'diagnose?', '<ul><li>Offsets expired (7 days idle).</li><li>auto.offset.reset=latest skipped data.</li><li>Seek by time or store offsets.</li></ul>', 'Blaming retention of the topic.'))
