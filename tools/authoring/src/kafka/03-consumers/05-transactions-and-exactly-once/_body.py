import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l35_tx.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('Kafka stored a ₹5,000 debit that was cancelled. Half the consumers saw it; the other half never did. Both were right.',
    'Inside a <b>transaction</b>, records are written immediately but marked “undecided”. When we <b>aborted</b>, the records stayed on disk, yet a <code>read_committed</code> consumer skipped them, and offsets even jumped over invisible <b>marker</b> records. We also killed an old producer instance with a newer one: “fenced”.',
    ['How Kafka makes several writes and an offset commit all-or-nothing.',
     'What the hidden COMMIT and ABORT markers look like on disk.',
     'How a stuck “zombie” instance is stopped from writing.'])
cmap = concept_map('Concept map. Beginner: transaction, commit, abort. Intermediate: transactional.id, transaction coordinator, control markers, read_committed, LSO. Advanced: consume-transform-produce, zombie fencing, Kafka Streams exactly_once_v2.',
    [[('tx', 'Transaction', 'all or nothing', None), ('cm', 'commit / abort', 'decide', None), ('id', 'Idempotent producer', 'Lesson 2.5', B + '02-producers/05-idempotent-producer-and-retries/')],
     [('ti', 'transactional.id', 'stable identity', None), ('tc', 'Transaction coordinator', '__transaction_state', None), ('mk', 'Control markers', 'COMMIT / ABORT', None), ('rc', 'read_committed', 'LSO', None)],
     [('ctp', 'Consume-transform-produce', 'offsets in tx', None), ('zf', 'Zombie fencing', 'epoch', None), ('ks', 'Kafka Streams EOS', 'Lesson 9.1', B + '09-stream-processing/01-kafka-streams/')]],
    [('id', 'ti'), ('tx', 'tc'), ('cm', 'mk'), ('mk', 'rc'), ('ti', 'zf'), ('tc', 'ctp'), ('rc', 'ctp'), ('ctp', 'ks')],
    {'tx', 'cm', 'id', 'ti', 'tc', 'mk', 'rc', 'ctp', 'zf'},
    '<b>Builds on:</b> <a href="../04-delivery-guarantees/">3.4</a>, <a href="../../02-producers/05-idempotent-producer-and-retries/">2.5</a>. <b>Next:</b> Module 4, <a href="../../04-storage-internals/01-the-commit-log-and-segments/">4.1 The commit log and segments</a>.')
whw = why_how_where(
    'A processor that reads payments and writes ledger entries must never write the entries without moving its offset, or move the offset without the entries.',
    'A transactional producer writes records to many partitions and the consumer offsets, then commits or aborts all of them together; read_committed consumers only see committed data.',
    'Kafka Streams with exactly_once_v2, Flink/Spark Kafka sinks, ledger and balance pipelines, CDC fan-out.',
    'It covers Kafka. Writes to a database or an email gateway from the same code are not part of the transaction.')

sc_ = (pcol(70, 30, 'P0', ['A1', 'A2', 'A3', 'C✓', 'B1', 'B2', 'C✗', 'C1', 'C✓'], 'blue', cw=50, ch=26, hi=(3, 6, 8)) +
       ''.join(t(70 + k * 52 + 25, 72, str(k), 7.4, 'ink2', mono=True) for k in range(9)) + t(60, 72, 'offset', 7.4, 'ink2', anchor='end') +
       box(14, 86, 300, 44, 'card', rx=6) + t(24, 104, 'read_uncommitted: A1 A2 A3 B1 B2 C1', 8, 'ink', anchor='start', mono=True) + t(24, 120, '(sees the aborted B entries)', 7.6, 'red', anchor='start') +
       box(326, 86, 300, 44, 'card', rx=6) + t(336, 104, 'read_committed:   A1 A2 A3 C1', 8, 'ink', anchor='start', mono=True) + t(336, 120, '(skips B and all markers)', 7.6, 'green', anchor='start'))
scene_svg = scene('One partition holding transaction A (offsets 0 to 2) and its COMMIT marker at 3, transaction B (4 and 5) and its ABORT marker at 6, and transaction C (7) with a COMMIT marker at 8. read_uncommitted sees A, B and C; read_committed sees only A and C.', sc_,
                  'Aborted data stays on disk but is <tspan font-weight="700" class="s-acc">invisible</tspan> to read_committed.')
dialogue = '''K> Sir, our wallet service writes a debit and a payment record, then commits its input offset. If it crashes in the middle, we get a debit without a payment.
A> Then those three actions must be <b>one transaction</b>: all visible, or none. Kafka transactions do exactly that, across partitions and including the consumer offset.
R> Does an aborted transaction get deleted?
A> No. Kafka writes first and decides later with a small <b>marker</b> record. Consumers that ask for <code>read_committed</code> skip anything aborted. Let’s look at the markers on disk.'''

lv = '''
LEVELS> Transactions at three levels
L1> A bank transfer slip
      <ul>
        <li>The clerk writes debit and credit in pencil (records written), then either inks them with a stamp “APPROVED” (commit marker) or stamps “CANCELLED” (abort marker). Auditors (read_committed) read only approved entries.</li>
      </ul>
L2> The API
      <ul>
        <li>Set a stable <code>transactional.id</code>; call <code>init_transactions()</code> once.</li>
        <li>Loop: <code>begin_transaction()</code> → <code>produce()</code> to any topics → <code>send_offsets_to_transaction(offsets, consumer_group_metadata)</code> → <code>commit_transaction()</code> (or <code>abort_transaction()</code> on error).</li>
        <li>Consumers set <code>isolation.level=read_committed</code> (librdkafka default) to see only committed records; Java consumers default to <code>read_uncommitted</code>.</li>
      </ul>
L3> Under the hood
      <ul>
        <li>A <b>transaction coordinator</b> (leader of a partition of <code>__transaction_state</code>) tracks state: Ongoing → PrepareCommit/PrepareAbort → CompleteCommit/CompleteAbort.</li>
        <li>On commit/abort it writes <b>control batches</b> (markers) into every partition the transaction touched. Each marker takes an offset, so offsets have gaps for consumers.</li>
        <li>read_committed consumers read only up to the <b>last stable offset</b> (LSO): an open transaction holds back readers until it ends (bounded by <code>transaction.timeout.ms</code>, 60 s).</li>
        <li><code>init_transactions()</code> bumps the producer <b>epoch</b>; an older instance with the same transactional.id is <b>fenced</b>. Kafka 4.x adds transaction protocol v2 (KIP-890, <code>transaction.version=2</code>) for stronger fencing per transaction.</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of kafka-dump-log output for transactions: a data batch with isTransactional true and isControl false, then a control batch with isControl true containing an endTxnMarker COMMIT, both with producerId 8000.',
    t(16, 22, 'kafka-dump-log of ledger-35 (selected lines)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('baseOffset: 0 count: 3', 'blue', 1), ('producerId: 8000', 'violet', 2), ('isTransactional: true', 'card', None), ('isControl: false', 'card', None)]) +
    fields(16, 70, [('baseOffset: 3 count: 1', 'acc', 3), ('isControl: true', 'acc', None), ('endTxnMarker: COMMIT', 'green', 4), ('coordinatorEpoch: 0', 'card', None)]) +
    fields(16, 106, [('baseOffset: 6', 'red', None), ('endTxnMarker: ABORT', 'red', 5)]) +
    legend(16, 150, [(1, 'Data batch', 'A1–A3, written before the decision'), (2, 'Producer id', 'all batches of this transactional producer'),
                     (3, 'Control batch', 'a marker record that takes an offset (3)'), (4, 'COMMIT', 'everything before it from PID 8000 is visible'),
                     (5, 'ABORT', 'B1–B2 stay on disk but read_committed skips them')], size=8, gap=15, w=110),
    h=236, caption='Real dump-log fields from our run.')
extra = '''

  <h3>Dissect the markers</h3>
''' + DIS

types_html = table(['isolation.level', 'Sees open transactions?', 'Sees aborted records?', 'Default in'], [
    ['read_uncommitted', 'yes, immediately', 'yes', 'Java consumer'],
    ['read_committed', 'no (waits for LSO)', 'no', 'librdkafka (Python, Go, .NET …)'],
], minw=560) + table(['Setting', 'Default', 'Purpose'], [
    ['transactional.id', 'none', 'stable id per producer instance; enables transactions'],
    ['transaction.timeout.ms', '60 s', 'abort transactions left open longer'],
    ['transaction.state.log.replication.factor', '3', 'durability of __transaction_state'],
    ['processing.guarantee (Kafka Streams)', 'at_least_once', 'exactly_once_v2 turns on transactions'],
], minw=560)
warn = 'Give each producer instance its own <b>stable</b> transactional.id (e.g. “wallet-writer-” + partition or pod ordinal). A random id per start defeats zombie fencing; the same id on two live instances makes them fence each other continuously.'

steps = [
    ('Step 1 · Three transactions: commit, abort, commit',
     code('python', 'l35_tx.py', 'p = Producer({"bootstrap.servers": BS, "transactional.id": "ledger-writer-1"})\np.init_transactions()\np.begin_transaction(); [p.produce(T, value=f"A{i} ...") for i in (1, 2, 3)]; p.commit_transaction()\np.begin_transaction(); [p.produce(T, value=f"B{i} ...") for i in (1, 2)]; p.flush(); p.abort_transaction()\np.begin_transaction(); p.produce(T, value="C1 refund Rs 100"); p.commit_transaction()', sec('== 1)', '== 4)')),
     'Transaction B was flushed to the broker <i>before</i> we aborted, so its records really are on disk. The question is who sees them.'),
    ('Step 2 · Two kinds of readers',
     code('python', 'l35_tx.py', 'read("read_uncommitted")\nread("read_committed")', sec('== 4)', '== 5)')),
     'read_uncommitted returned the cancelled B debits; read_committed did not. Also notice the missing offsets 3, 6 (and 8): those are the markers.'),
    ('Step 3 · The markers on disk',
     code('bash', 'terminal', 'kafka-dump-log.sh --files /var/lib/kafka/data/ledger-35-0/00000000000000000000.log --print-data-log', sec('== 5)', '== 6)')),
     'Every transaction ends with a control batch: COMMIT at offset 3, ABORT at 6, COMMIT at 8. They carry no business data; consumers never receive them.'),
    ('Step 4 · The coordinator’s view',
     code('bash', 'terminal', 'kafka-transactions.sh --bootstrap-server k1:9092 list', sec('== 6)', '== 7)')),
     'The transaction coordinator (broker 1 here) knows the transactional.id, its producer id 8000 and the last state, CompleteCommit.'),
    ('Step 5 · Fencing a zombie',
     code('python', 'l35_fence.py', 'old = Producer({..., "transactional.id": "alert-writer"}); old.init_transactions(); old.begin_transaction(); old.produce(...)\nnew = Producer({..., "transactional.id": "alert-writer"}); new.init_transactions()   # epoch bumped\nold.commit_transaction()', sec('== 7)')),
     'The new instance’s <code>init_transactions()</code> bumped the epoch and aborted the old open transaction. The old instance’s commit failed: “fenced by a newer instance”. A stuck pod can never write half-finished results after its replacement starts.'),
]

see = [term([('A: 3 entries  committed', G), ('B: 2 entries  aborted', RD), ('C: 1 entry   committed', G)], size=7.2),
       term([('read_uncommitted: 0 1 2 4 5 7', Y), ('  A1 A2 A3 B1 B2 C1', Y), ('read_committed  : 0 1 2 7', G), ('  A1 A2 A3 C1', G)], size=7.0),
       term([('offset 3  endTxnMarker: COMMIT', G), ('offset 6  endTxnMarker: ABORT', RD), ('offset 8  endTxnMarker: COMMIT', G)], size=7.0),
       term([('ledger-writer-1  coordinator 1', W), ('producerId 8000  CompleteCommit', G)], size=7.0),
       term([('new instance: epoch bumped', W), ('old commit: fenced by a newer', RD), ('instance', RD)], size=7.0)]
def part(hi, note, tone):
    cells = ['A1', 'A2', 'A3', '✓', 'B1', 'B2', '✗', 'C1', '✓']
    return t(180, 14, note, 9, bold=True) + ''.join(box(10 + k * 38, 50, 34, 30, ('red' if k in (4, 5) and 'committed' in hi else ('acc' if cells[k] in '✓✗' else 'blue')), rx=3) + t(27 + k * 38, 69, cells[k], 7.6, 'ink') for k in range(9)) + cap(note, '', tone, y=144, h=30)
B1 = [part('', 'Write first, decide later', 'blue'), part('committed', 'read_committed skips B', 'green'), part('', 'Markers take offsets 3, 6, 8', 'violet'),
      t(180, 14, 'Coordinator tracks state', 9, bold=True) + opbox(110, 50, 'ledger-writer-1', 'CompleteCommit', 'violet', 140, 40) + cap('__transaction_state.', '', 'violet', y=144, h=30),
      t(180, 14, 'Epoch fences the zombie', 9, bold=True) + opbox(20, 50, 'old (epoch 0)', 'commit ✗', 'red', 130, 34) + opbox(210, 50, 'new (epoch 1)', 'owns the id', 'green', 130, 34) + cap('Only the newest instance writes.', '', 'green', y=144, h=30)]
two = anim_two('Transactions and exactly-once', 'All or nothing', 'Real outputs from the lab', 'What is on disk', see, B1, ['Write.', 'Read.', 'Markers.', 'Coordinator.', 'Fence.'], ['Pending.', 'Filter.', 'Control.', 'State.', 'Epoch.'])
pe = peel('Consume-transform-produce, exactly once', 'Read payments, write alerts, commit offsets together. (Typical loop.)',
    [('Poll input', ''), ('begin', ''), ('Produce output', ''), ('Add offsets', ''), ('commit', ''), ('Markers', '')],
    [['Poll input', 'payments t040–t049', 'from P0', 'no auto-commit'], ['begin_transaction()', 'coordinator: Ongoing', 'for this transactional.id', ''],
     ['Produce output', 'alerts to fraud-alerts', 'written, not yet visible', '(read_committed)'], ['Add offsets', 'send_offsets_to_transaction', 'payments P0 → 50', 'consumer group metadata'],
     ['commit_transaction()', 'PrepareCommit →', 'markers to fraud-alerts', 'and __consumer_offsets'], ['Markers', 'alerts visible and', 'offset 50 committed', 'together, or neither']],
    ['Read.', 'Begin.', 'Write.', 'Offsets.', 'Commit.', 'Visible.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Debit without payment', 'Atomic multi-topic writes. (Typical.)', ('Transactions', 'Write related records to several topics atomically'), [
    ('Wallet writes debit + payment', 'two topics', 'Separate sends.', 'blue'), ('Crash between them', 'debit only', 'Balance wrong.', 'red'),
    ('Wrap in a transaction', 'begin … commit', 'Both or neither.', 'green'), ('Crash now', 'transaction aborted on timeout', 'Readers see nothing.', 'green'),
    ('read_committed readers', 'consistent view', 'Fixed.', 'blue')], ['Two writes.', 'Crash.', 'Transaction.', 'Abort.', 'Consistent.'], 'scenario-atomic') + \
       five('Real-time scenario 2', 'Consumers stuck behind an open transaction', 'Last stable offset. (Typical.)', ('LSO', 'read_committed consumers wait for open transactions to end'), [
    ('Producer starts a transaction', 'then hangs (GC pause)', 'Open 60 s.', 'amber'), ('read_committed consumers', 'stop at the LSO', 'Lag grows.', 'red'),
    ('transaction.timeout.ms', 'coordinator aborts it', 'After 60 s.', 'green'), ('Consumers continue', 'skip aborted data', 'Recovered.', 'green'),
    ('Keep transactions short', 'commit every few seconds', 'Rule.', 'blue')], ['Open.', 'Stuck.', 'Timeout.', 'Continue.', 'Short.'], 'scenario-lso') + \
       five('Real-time scenario 3 · advanced', 'Two pods, one transactional.id', 'Fencing storms. (Typical.)', ('transactional.id design', 'One stable id per producer instance'), [
    ('Deployment copies config', 'both pods use “alerts-tx”', 'Same id.', 'blue'), ('Each init fences the other', 'commits keep failing', 'ProducerFenced.', 'red'),
    ('Throughput collapses', 'retries forever', 'Incident.', 'red'), ('id = name + pod ordinal', 'alerts-tx-0, alerts-tx-1', 'Unique.', 'green'),
    ('Restarts keep the same id', 'zombies still fenced', 'Correct.', 'blue')], ['Copy.', 'Fence.', 'Collapse.', 'Unique.', 'Correct.'], 'scenario-txid')
assemble(HERE, h2_story='All of it, or none of it', hook_html=hk,
    narration='TiffinGo’s wallet service reads a payment, writes a debit and a ledger entry to two topics, and commits its offset. A crash in the middle once left a debit with no payment. Kabir wants the three steps to be one.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Transactions and exactly-once',
    formal='A Kafka <b>transaction</b> lets a producer with a <code>transactional.id</code> write records to multiple partitions and commit consumer offsets atomically: either all writes become visible to <code>read_committed</code> consumers, or none do. A <b>transaction coordinator</b> persists transaction state in <code>__transaction_state</code> and, on commit or abort, writes <b>control markers</b> to each involved partition. Combined with the idempotent producer, transactions provide <b>exactly-once semantics</b> for consume-transform-produce applications within Kafka, and the producer <b>epoch</b> fences zombie instances sharing a transactional.id.',
    simple='A transaction groups several writes (and the “I have read up to here” offset) into one unit. Kafka writes them, then stamps them approved or cancelled. Careful readers see only approved data. An old copy of your app can’t sneak in writes after a new copy starts.',
    term_rows=[('transactional.id', 'Stable id of a transactional producer.'), ('Transaction coordinator', 'Broker tracking a transaction.'), ('Control marker', 'COMMIT/ABORT record in a partition.'), ('read_committed', 'See only committed data.'), ('LSO', 'Last stable offset for read_committed.'), ('send_offsets_to_transaction', 'Commit input offsets in the tx.'), ('Epoch', 'Generation of a transactional.id.'), ('Fenced', 'Old instance blocked from writing.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Aborted records are deleted.', 'They stay on disk; read_committed consumers skip them.', 'Step 2: read_uncommitted still sees B1, B2.'),
               ('Offsets are always consecutive for consumers.', 'Transaction markers take offsets, so there are gaps.', 'Step 2: offsets 3 and 6 never delivered.'),
               ('Exactly-once needs no consumer setting.', 'Downstream consumers must use read_committed (Java default is read_uncommitted).', 'Types table.')],
    exam='“How does Kafka achieve exactly-once?” Idempotent producer + transactions: begin, produce to many partitions, send_offsets_to_transaction, commit/abort; coordinator writes COMMIT/ABORT markers; read_committed consumers read up to the LSO; transactional.id epoch fences zombies. Kafka Streams: processing.guarantee=exactly_once_v2.',
    types_h2='Isolation levels and settings', types_html=types_html, warn=warn,
    steps_h2='Commit, abort, fence', steps_intro='All outputs are real: Kafka 4.4.0, 3 brokers; Python <code>confluent-kafka</code> 2.16.1; topic <code>ledger-35</code> with 1 partition. Scripts: <code>jobs/m3/l35_tx.py</code>, <code>l35_fence.py</code>.',
    steps=steps, two=two, peel_intro='Now peel a consume-transform-produce transaction.', peel_html=pe,
    scen_intro='Three live scenarios: atomic writes, an open transaction blocking readers, and a shared transactional.id.', scen=scen,
    uc_h2='Transactions at work', ucs=[uc_('wallet', 'ledger', 'green', '1. Wallet and ledger', 'Debit, credit and offset in one transaction.', ['Payment', '*transaction', 'Balanced']),
        uc_('stream', 'EOS', 'blue', '2. Kafka Streams', 'exactly_once_v2 wraps every task’s output in transactions.', ['Input', '*Streams', 'Output']),
        uc_('Flink', 'sink', 'violet', '3. Flink / Spark sinks', 'Two-phase commit sinks use Kafka transactions.', ['Job', '*2PC', 'Kafka']),
        uc_('CDC', 'fan-out', 'acc', '4. Change data fan-out', 'One DB change becomes several topic writes atomically.', ['Change', '*tx', 'Topics']),
        uc_('fraud', 'alerts', 'blue', '5. Fraud alerts', 'Read payments, write alerts and offsets exactly once.', ['Payments', '*tx', 'Alerts'])],
    uc_note='Examples are simplified descriptions of common patterns.',
    pre='<b>Before you start:</b> <a href="../04-delivery-guarantees/">3.4 Delivery guarantees</a> and <a href="../../02-producers/05-idempotent-producer-and-retries/">2.5 Idempotence</a>.')
