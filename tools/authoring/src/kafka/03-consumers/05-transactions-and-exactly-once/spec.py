import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
BODY = body(HERE)
META = dict(module='03-consumers', lesson='05-transactions-and-exactly-once', n='3.5', module_label='Module 3 · Consumers',
    title='Transactions and exactly-once',
    desc='Kafka transactions: transactional.id, begin/commit/abort, the transaction coordinator, COMMIT and ABORT control markers, read_committed vs read_uncommitted, the last stable offset, send_offsets_to_transaction and zombie fencing. Real Kafka 4.4 lab: an aborted debit stays on disk but read_committed skips it, markers take offsets 3, 6 and 8, and a newer producer fences an older one.',
    og_desc='Aborted records stay on disk but disappear for read_committed; markers and fencing proven on Kafka 4.4.',
    minutes=28, level='Advanced',
    lead='How does Kafka make several writes and an offset commit <b>all-or-nothing</b>? We commit and abort real <b>transactions</b>, read with both isolation levels, find the hidden <b>markers</b> on disk and <b>fence</b> a zombie producer. <b>All outputs are real.</b>',
    chips=['Commit vs abort', 'Markers on disk', 'Zombie fenced', 'Runs in your browser (Python)'])
MAIN = '''# A partition with transactional writes and markers; two kinds of readers
log = []                                   # (offset, pid, kind, value)
def write(pid, value): log.append((len(log), pid, "data", value))
def marker(pid, kind): log.append((len(log), pid, kind, None))

for v in ("A1", "A2", "A3"): write(8000, v)
marker(8000, "COMMIT")
for v in ("B1", "B2"): write(8000, v)
marker(8000, "ABORT")
write(8000, "C1"); marker(8000, "COMMIT")

def read(committed_only):
    out, pending = [], []
    for off, pid, kind, v in log:
        if kind == "data":
            (pending if committed_only else out).append((off, v))
        elif kind == "COMMIT":
            out += pending; pending = []
        else:                                   # ABORT
            pending = []
    return out

print("read_uncommitted:", read(False))
print("read_committed  :", read(True))
'''
RUN = dict(heading='Run the code: markers decide visibility', intro='<p>Our lab partition, modelled. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('        elif kind == "COMMIT":', 'The COMMIT marker makes pending records visible.'), ('            pending = []', 'ABORT throws them away for read_committed readers.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Then make transaction B commit.', code=None),
        dict(label='2 · Predict first: offsets', hint='<b>Predict first:</b> which offsets are markers?', code='print([3, 6, 8])\n'),
        dict(label='3 · Open transaction', hint='No marker yet: what does read_committed see?', code='log = [(0, "A1"), (1, "A2")]   # no COMMIT yet\nprint("read_committed sees:", [])\n'),
        dict(label='4 · Fencing', hint='Higher epoch wins.', code='current_epoch, request_epoch = 1, 0\nprint("fenced" if request_epoch < current_epoch else "ok")\n'),
        dict(label='5 · Spot the error', hint='Zombie commit.', expect='error', code='epoch_now, my_epoch = 1, 0\nif my_epoch < epoch_now:\n    raise RuntimeError("This instance has been fenced by a newer instance")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: a transaction', intro='<p>Python confluent-kafka. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Transactional producer', cmd='p = Producer({"bootstrap.servers": "localhost:9092", "transactional.id": "ledger-writer-1"}); p.init_transactions(); p.begin_transaction(); p.produce("ledger-35", value="A1"); p.commit_transaction()', file='python', output='(no error = committed)', note='One-time init.'),
           dict(title='2 · Read committed only', cmd='Consumer({..., "isolation.level": "read_committed"})', file='python', output='[(0, "A1"), (1, "A2"), (2, "A3"), (7, "C1")]', note='librdkafka default.'),
           dict(title='3 · Inspect', cmd='kafka-transactions.sh --bootstrap-server localhost:9092 list', file='terminal', output='ledger-writer-1  1  8000  CompleteCommit', note='Coordinator view.')])
TRACE = dict(heading='Commit makes it visible', intro='<p>Pending until the marker.</p>',
    code='visible, pending = [], []\npending.append("A1")\npending.append("A2")\nvisible += pending\npending = []\nprint(visible, pending)\n',
    notes={3: 'Written :: On disk, not yet visible.', 4: 'COMMIT :: Marker makes them visible.'})
WORKED_INTRO = 'Three transaction designs.'
EXAMPLES = [
    dict(level='b', tag='Transactions · basics', title='Atomic debit + ledger', problem='<p>Two topics must change together.</p>', inp='events',
         approach=['init_transactions once.', 'begin; produce both; commit.', 'abort on any error.'], code='steps = ["begin", "produce(debits)", "produce(ledger)", "commit (or abort)"]\nprint(" -> ".join(steps))\n', notes={1: 'Atomic :: Both or neither.'}, tryit='Scenario 1.'),
    dict(level='i', tag='Transactions · EOS loop', title='Read-process-write', problem='<p>Fraud detector must not double-alert.</p>', inp='payments',
         approach=['Consumer: enable.auto.commit=false.', 'Inside tx: produce alerts + send_offsets_to_transaction.', 'Downstream: read_committed.'], code='print(["poll", "begin", "produce alerts", "send_offsets_to_transaction(positions, group_metadata)", "commit"])\n', notes={1: 'EOS :: Output and progress together.'}, tryit='Peel animation.'),
    dict(level='a', tag='Transactions · ids', title='Choose transactional.id', problem='<p>3 pods of the same service.</p>', inp='pods',
         approach=['Stable per pod: name + ordinal.', 'Same id after restart (fences zombie).', 'Never random.'], code='print([f"fraud-tx-{i}" for i in range(3)])\n', notes={1: 'Identity :: Enables fencing.'}, tryit='Scenario 3.')]
QUIZ = mix([
    dict(q='Beginner: A transaction makes writes…', options=['Faster', 'All visible or none', 'Compressed', 'Ordered globally'], answer=1, why='Atomic.'),
    dict(q='Beginner: After abort, the records are…', options=['Deleted', 'On disk but skipped by read_committed', 'Moved', 'Duplicated'], answer=1, why='Step 2.'),
    dict(q='Beginner: Consumers that skip aborted data use…', options=['read_uncommitted', 'read_committed', 'acks=all', 'linger.ms'], answer=1, why='Isolation level.'),
    dict(q='Intermediate: Offsets 3, 6, 8 were missing because…', options=['Deleted', 'They are COMMIT/ABORT markers', 'Compaction', 'Lag'], answer=1, why='Control batches.'),
    dict(q='Intermediate: Java consumer default isolation level is…', options=['read_committed', 'read_uncommitted', 'serializable', 'none'], answer=1, why='librdkafka defaults to read_committed.'),
    dict(q='Intermediate: To commit input offsets inside a transaction use…', options=['commit()', 'send_offsets_to_transaction()', 'flush()', 'seek()'], answer=1, why='EOS loop.'),
    dict(q='Advanced: An open transaction makes read_committed consumers…', options=['Read everything', 'Stop at the last stable offset', 'Crash', 'Skip the partition'], answer=1, why='LSO.'),
    dict(q='Advanced: A zombie is fenced because…', options=['Its IP is blocked', 'A newer instance bumped the epoch', 'Timeout', 'ACLs'], answer=1, why='Step 5.')])
REVISION = ['Transaction: begin → produce (many partitions) → send_offsets → commit/abort.', 'Coordinator + __transaction_state; COMMIT/ABORT control markers take offsets.',
    'Lab: read_uncommitted A1–A3, B1–B2, C1; read_committed A1–A3, C1; markers at 3, 6, 8.', 'read_committed reads up to the LSO; Java default read_uncommitted, librdkafka read_committed.',
    'Epoch fencing: new init_transactions() fences old instance (“fenced by a newer instance”).', 'Kafka Streams: processing.guarantee=exactly_once_v2.']
FAQ = [('Do I need transactions for every producer?', 'No. Use them when writes must be atomic across partitions or with consumer offsets. Idempotence alone is enough for simple producers.'),
    ('Can a transaction span two clusters?', 'No. Transactions are within one Kafka cluster.'),
    ('What happens if the producer dies mid-transaction?', 'The coordinator aborts it after transaction.timeout.ms, or immediately when a new instance with the same transactional.id calls init_transactions().'),
    ('Is exactly-once slower?', 'Some latency per commit (markers, coordinator round trips). Batch several records per transaction to amortise it.')]
PRACTICE_INTRO = 'Transaction programs.'
PROBLEMS = [
    dict(level='easy', title='Visible count', stmt='Committed data records.', inp='A 3, B aborted 2, C 1', code='print(3 + 1)\n', explain='4.'),
    dict(level='easy', title='Markers', stmt='Markers for 3 transactions in 1 partition.', inp='3', code='print(3)\n', explain='One per transaction per partition.'),
    dict(level='easy', title='Gap', stmt='Offsets missing from consumer view.', inp='9 offsets, 6 data', code='print(9 - 6)\n', explain='Markers (3) for read_uncommitted.'),
    dict(level='medium', title='Filter aborted', stmt='Keep committed transactions only.', inp='dict', code='tx = {"A": ("COMMIT", ["A1", "A2"]), "B": ("ABORT", ["B1"])}\nprint([r for s, rs in tx.values() if s == "COMMIT" for r in rs])\n', explain='read_committed.'),
    dict(level='medium', title='Markers per tx', stmt='Partitions touched = markers.', inp='3 partitions', code='print(3, "markers for one transaction across 3 partitions")\n', explain='One each.'),
    dict(level='medium', title='Epoch check', stmt='Which instance may write?', inp='epochs', code='print(max({"old": 0, "new": 1}.items(), key=lambda x: x[1])[0])\n', explain='Newest.'),
    dict(level='business', title='Wrong balances avoided', stmt='Crashes/month 4 × 200 half-written payments.', inp='numbers', code='print(4 * 200, "inconsistent records avoided")\n', explain='Why transactions.'),
    dict(level='business', title='Throughput', stmt='Commit every 500 records at 2,000 rec/s.', inp='numbers', code='print(2000 / 500, "commits per second")\n', explain='Batch transactions.')]
SCN_INTRO = 'Transaction interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“How does Kafka do exactly-once?”', 'Explain.', 'answer?', '<p>Idempotent producers stop retry duplicates; transactions group output records and consumer offsets so they commit or abort together; consumers use read_committed. Kafka Streams turns this on with exactly_once_v2.</p>', '“acks=all makes it exactly-once.”') +
    scn('Fintech', 'Mid-level', 'Aborted data seen', 'A Java report shows cancelled debits.', 'cause?', '<ul><li>Java default read_uncommitted.</li><li>Set isolation.level=read_committed.</li></ul>', '“The abort failed.”') +
    scn('Data engineering', 'Mid-level', 'Stuck consumers', 'read_committed consumers stop moving.', 'diagnose?', '<ul><li>An open/hanging transaction holds the LSO.</li><li>kafka-transactions.sh to find it.</li><li>Short transactions; timeouts.</li></ul>', 'Restarting brokers.') +
    scn('Platform', 'Senior', 'Fencing errors', 'Producers keep getting ProducerFenced.', 'fix?', '<ul><li>Two live instances share a transactional.id.</li><li>Unique stable id per instance.</li></ul>', 'Random ids per start.'))
