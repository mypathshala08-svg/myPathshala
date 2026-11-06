import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l34_guarantees.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('Same 50 invoices, same crash. One version lost 5 invoices; the other sent 5 twice. The only difference: one line moved.',
    'We crashed a billing worker after invoice 25. When it committed <b>before</b> sending invoices, invoices 26–30 vanished. When it committed <b>after</b>, invoices 21–25 went out twice. This lesson turns “at-most-once / at-least-once / exactly-once” from buzzwords into something you can measure.',
    ['Where loss and duplicates really come from.',
     'Why most systems choose at-least-once plus idempotent processing.',
     'What exactly-once really means in Kafka (and what it does not).'])
cmap = concept_map('Concept map. Beginner: at-most-once, at-least-once, exactly-once. Intermediate: commit order, crash points, idempotent processing. Advanced: transactions, read_committed, end-to-end exactly-once with external systems.',
    [[('am', 'At-most-once', 'may lose', None), ('al', 'At-least-once', 'may duplicate', None), ('eo', 'Exactly-once', 'neither', None)],
     [('co', 'Commit order', 'before or after work', B + '03-consumers/03-offsets-commits-and-lag/'), ('cr', 'Crash points', 'where it fails', None), ('ip', 'Idempotent processing', 'dedup by id', None), ('pi', 'Producer idempotence', 'Lesson 2.5', B + '02-producers/05-idempotent-producer-and-retries/')],
     [('tx', 'Transactions', 'Lesson 3.5', B + '03-consumers/05-transactions-and-exactly-once/'), ('rc', 'read_committed', 'hide aborted data', None), ('ex', 'External systems', 'DB, email, payments', None)]],
    [('am', 'co'), ('al', 'co'), ('co', 'cr'), ('al', 'ip'), ('eo', 'tx'), ('pi', 'tx'), ('tx', 'rc'), ('ip', 'ex')],
    {'am', 'al', 'eo', 'co', 'cr', 'ip'},
    '<b>Builds on:</b> <a href="../03-offsets-commits-and-lag/">3.3</a>, <a href="../../02-producers/05-idempotent-producer-and-retries/">2.5</a>. <b>Next:</b> <a href="../05-transactions-and-exactly-once/">3.5 Transactions</a>.')
whw = why_how_where(
    'Crashes happen between “do the work” and “save progress”. Which one you do first decides whether you can lose or repeat work.',
    'Commit first → at-most-once. Work first, then commit → at-least-once. Make the work idempotent, or put output and offsets in one transaction → effectively exactly-once.',
    'Payments and invoices (at-least-once + dedup), metrics (at-most-once is fine), Kafka-to-Kafka pipelines (transactions).',
    'No setting gives exactly-once for side effects outside Kafka (an SMS, an HTTP call) by itself: the external action must be idempotent.')

sc_ = (t(160, 18, 'commit BEFORE work (at-most-once)', 8.8, 'red', bold=True) + ''.join(box(14 + i * 5.8, 32, 5, 26, 'red' if 25 <= i < 30 else 'green', rx=1) for i in range(50)) + t(160, 76, 'invoices 26–30 never sent', 8, 'red') +
       t(480, 18, 'commit AFTER work (at-least-once)', 8.8, 'amber', bold=True) + ''.join(box(334 + i * 5.8, 32, 5, 26, 'amber' if 20 <= i < 25 else 'green', rx=1) for i in range(50)) + t(480, 76, 'invoices 21–25 sent twice', 8, 'amber') +
       box(14, 96, 612, 32, 'card', rx=6) + t(320, 116, 'Same 50 invoices · worker crashes after the 25th · restarts and continues', 8.4, 'ink', bold=True))
scene_svg = scene('Left: committing before processing lost invoices 26 to 30 after a crash. Right: committing after processing sent invoices 21 to 25 twice. Both runs had 50 invoices and a crash after the 25th.', sc_,
                  'The order of <tspan font-weight="700" class="s-acc">commit</tspan> and work decides loss vs duplicates.')
dialogue = '''R> Sir, the interview question was “Does Kafka give exactly-once?” I said yes.
A> Kafka gives you the tools. Your consumer code decides. If it commits the offset and then crashes before sending the invoice, that invoice is lost forever. If it sends and then crashes before committing, it sends again on restart.
K> So which is better?
A> For money, a duplicate you can detect is better than a silent loss. Let’s crash a worker on purpose, both ways, and count.'''

lv = '''
LEVELS> Delivery guarantees at three levels
L1> Ticking the register
      <ul>
        <li>At-most-once: tick “done” first, then deliver. If you faint in between, the parcel is never delivered. At-least-once: deliver first, then tick. If you faint, someone delivers it again.</li>
      </ul>
L2> In consumer code
      <ul>
        <li><b>At-most-once</b>: commit, then process. Crash after commit → those records are skipped.</li>
        <li><b>At-least-once</b>: process, then commit (the usual choice; also what auto-commit gives in the normal case, though auto-commit can drift into at-most-once if processing is async).</li>
        <li><b>Exactly-once (effectively)</b>: at-least-once + <b>idempotent processing</b> (dedup by a business id, upserts), or Kafka transactions for Kafka-to-Kafka pipelines.</li>
      </ul>
L3> Where each layer stands
      <ul>
        <li>Producer → broker: idempotence removes retry duplicates (2.5).</li>
        <li>Consume → process → produce within Kafka: transactions commit output records and input offsets atomically; downstream consumers use <code>isolation.level=read_committed</code> (3.5). Kafka Streams enables this with <code>processing.guarantee=exactly_once_v2</code>.</li>
        <li>Kafka → external system (DB, email): needs an idempotent sink or storing offsets in the same database transaction as the result.</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of the at-least-once crash: batches of 10 records, commit after batch 2 at offset 20, crash after processing record 25, restart from offset 20, records 21 to 25 processed twice.',
    t(16, 22, 'At-least-once crash, step by step (batches of 10)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('batch 1: 1–10 ✓ commit 10', 'green', 1), ('batch 2: 11–20 ✓ commit 20', 'green', None), ('batch 3: 21–25 sent', 'amber', 2), ('💥 crash', 'red', 3)]) +
    fields(16, 72, [('restart: committed = 20', 'blue', 4), ('re-send 21–25', 'amber', 5), ('continue 26–50', 'green', None)]) +
    legend(16, 124, [(1, 'Commit after work', 'progress saved only after the batch is done'), (2, 'Partial batch', '5 invoices sent, commit not reached'),
                     (3, 'Crash', 'os._exit(1): no clean shutdown, no commit'), (4, 'Resume point', 'last committed offset'),
                     (5, 'Duplicates', 'exactly the uncommitted work: 5 invoices')], size=8, gap=15, w=130),
    h=210, caption='Mechanism behind our real at-least-once result.')
extra = '''

  <h3>Dissect the duplicate</h3>
''' + DIS

types_html = table(['Guarantee', 'How (consumer)', 'On crash', 'Good for'], [
    ['At-most-once', 'commit, then process', 'lose the uncommitted batch', 'metrics, GPS pings'],
    ['At-least-once', 'process, then commit', 'repeat the uncommitted batch', 'most systems (+ dedup)'],
    ['Exactly-once (Kafka → Kafka)', 'transactions + read_committed', 'no loss, no duplicate in outputs', 'stream processing'],
    ['Effectively-once (Kafka → DB)', 'at-least-once + idempotent upsert / offsets in same DB tx', 'duplicate absorbed', 'payments, ledgers'],
], minw=640)
warn = '“Exactly-once” in Kafka means each input record’s effects on <b>Kafka</b> (output records and committed offsets) happen exactly once. It does not stop your code from calling an SMS gateway twice. Design external side effects to be idempotent (send with an idempotency key, upsert by id).'

steps = [
    ('Step 1 · The worker',
     code('python', 'l34_worker.py', 'while idle < 20:\n    msgs = c.consume(10, 1.0)\n    if mode == "atmost": c.commit(asynchronous=False)      # commit BEFORE processing\n    for m in msgs:\n        out.write(m.value().decode() + "\\n")                # "send the invoice"\n        done += 1\n        if done == crash_after: os._exit(1)                 # crash\n    if mode == "atleast": c.commit(asynchronous=False)     # commit AFTER processing', None),
     'One worker, two modes. It reads batches of 10, writes each invoice to a log file (our “sent invoices”), and crashes hard after the 25th. Then a new run of the same group continues.'),
    ('Step 2 · At-most-once',
     code('bash', 'terminal', 'python l34_run.py      # mode atmost: 50 invoices, crash after 25, restart', sec('== at-most-once', '== at-least-once')),
     'Batch 3 (21–30) was committed before processing. The crash happened at 25, so on restart the group began at 30: invoices 26–30 were <b>never sent</b>. 45 of 50.'),
    ('Step 3 · At-least-once',
     code('bash', 'terminal', 'python l34_run.py      # mode atleast', sec('== at-least-once')),
     'The last commit was after batch 2 (offset 20). On restart the group re-read 21–30: invoices 21–25 were <b>sent twice</b>, none lost. 55 sends, 50 unique.'),
]

see = [term([('consume 10 → commit? → process → commit?', W), ('crash after record 25', RD)], size=7.0),
       term([('at-most-once', W), ('processed 45  unique 45  missing 5', RD), ('missing: invoice-26 … invoice-30', RD)], size=7.0),
       term([('at-least-once', W), ('processed 55  unique 50  missing 0', Y), ('twice: invoice-21 … invoice-25', Y)], size=7.0)]
def strip(colors, title, tone, note):
    return t(180, 14, title, 9, bold=True) + ''.join(box(18 + i * 6.5, 50, 5.5, 34, colors(i), rx=1) for i in range(50)) + t(180, 104, note, 8, 'ink2') + cap(title, '', tone, y=144, h=30)
B1 = [strip(lambda i: 'green' if i < 20 else ('amber' if i < 25 else 'card'), 'Crash after 25', 'blue', 'committed up to 20 (at-least) / 30 (at-most)'),
      strip(lambda i: 'red' if 25 <= i < 30 else 'green', 'At-most-once: 5 lost', 'red', 'commit came before the work'),
      strip(lambda i: 'amber' if 20 <= i < 25 else 'green', 'At-least-once: 5 twice', 'amber', 'work came before the commit')]
two = anim_two('Delivery guarantees', 'Crash, then count', 'Real outputs from the lab', 'Which invoices were affected', see, B1, ['Worker.', 'At-most.', 'At-least.'], ['Crash.', 'Lost.', 'Twice.'])
pe = peel('At-least-once + idempotent sink = effectively once', 'How payment systems absorb duplicates. (Typical design.)',
    [('Read batch', ''), ('Check id', ''), ('Upsert', ''), ('Commit', ''), ('Crash + replay', ''), ('Result', '')],
    [['Read batch', 'invoices 21–30', 'each has invoice_id', ''], ['Check id', 'already in DB?', 'invoice_id is the', 'primary key'],
     ['Upsert', 'INSERT … ON CONFLICT', 'DO NOTHING', 'safe to repeat'], ['Commit', 'offset after the batch', 'is written', ''],
     ['Crash + replay', '21–25 come again', 'upsert sees the ids', 'nothing changes'], ['Result', 'no loss', '(at-least-once)', 'no visible duplicate']],
    ['Read.', 'Check.', 'Upsert.', 'Commit.', 'Replay.', 'Once.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Missing invoices', 'At-most-once by accident. (Typical.)', ('Commit after work', 'Never commit before the work is durable'), [
    ('Auto-commit + async processing', 'work in a thread pool', 'Commit runs ahead.', 'blue'), ('Pod OOM-killed', 'tasks lost', 'Offsets already committed.', 'red'),
    ('Invoices never sent', 'customers not billed', 'Silent loss.', 'red'), ('Manual commit after tasks finish', 'track completed offsets', 'At-least-once.', 'green'),
    ('Dedup downstream', 'invoice_id key', 'Effectively once.', 'blue')], ['Setup.', 'Crash.', 'Loss.', 'Fix.', 'Dedup.'], 'scenario-missing') + \
       five('Real-time scenario 2', 'Double SMS', 'Duplicates in an external side effect. (Typical.)', ('Idempotent side effects', 'Use an idempotency key for external calls'), [
    ('At-least-once SMS sender', 'crash after sending', 'Replay.', 'blue'), ('Customer gets 2 SMS', 'per replay', 'Annoying.', 'amber'),
    ('Store sent message ids', 'in Redis/DB with TTL', 'Check first.', 'green'), ('Or provider idempotency key', 'same key → one SMS', 'Provider dedups.', 'green'),
    ('Kafka EOS cannot help here', 'side effect is outside Kafka', 'Design it in.', 'blue')], ['Sender.', 'Twice.', 'Store ids.', 'Key.', 'Limit.'], 'scenario-sms') + \
       five('Real-time scenario 3 · advanced', 'Offsets in the database', 'Atomic result + offset. (Typical.)', ('Same-transaction offsets', 'Store the offset with the result to get exactly-once into a DB'), [
    ('Ledger in PostgreSQL', 'needs exactly-once', 'No duplicates allowed.', 'blue'), ('One DB transaction', 'insert entries + save offset', 'Atomic.', 'green'),
    ('On start: read offset from DB', 'consumer.seek()', 'Not Kafka commits.', 'green'), ('Crash anywhere', 'either both saved or neither', 'Consistent.', 'green'),
    ('Same idea as Spark checkpoints', 'and Connect sinks', 'Common pattern.', 'blue')], ['Need.', 'Atomic.', 'Seek.', 'Crash.', 'Pattern.'], 'scenario-dboffsets')
assemble(HERE, h2_story='Lost or doubled?', hook_html=hk,
    narration='After a crash in TiffinGo’s billing worker, some customers got two invoices and, in an older version of the code, some got none. Riya has an interview tomorrow with the question “Explain Kafka delivery guarantees.”',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Delivery guarantees',
    formal='Delivery semantics describe how many times a record’s processing takes effect in the presence of failures. <b>At-most-once</b>: offsets are committed before processing, so a failure may skip records. <b>At-least-once</b>: offsets are committed after processing, so a failure may repeat records. <b>Exactly-once</b>: each record’s effect occurs once; in Kafka it is provided for read-process-write pipelines within Kafka by idempotent producers and transactions with read_committed consumers, and for external systems by idempotent writes or by atomically storing results with offsets.',
    simple='If you save progress before doing the work, a crash can lose work. If you save after, a crash can repeat work. To get “once”, make repeats harmless or save the work and the progress together.',
    term_rows=[('At-most-once', 'Never twice, may lose.'), ('At-least-once', 'Never lost, may repeat.'), ('Exactly-once', 'Once, despite failures.'), ('Idempotent processing', 'Repeating has no extra effect.'), ('Idempotency key', 'Id that makes repeats detectable.'), ('Upsert', 'Insert or update by key.'), ('read_committed', 'Read only committed transactions.'), ('Side effect', 'Action outside Kafka (SMS, API).')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Kafka is exactly-once by default.', 'Default consumers are at-least-once (or at-most-once by mistake).', 'Steps 2–3: 5 lost or 5 doubled.'),
               ('Exactly-once means the SMS is sent once.', 'It covers Kafka outputs and offsets, not external calls.', 'Scenario 2.'),
               ('At-least-once means lots of duplicates.', 'Only the uncommitted work since the last commit repeats.', 'Step 3: exactly 5 (21–25).')],
    exam='“Explain at-most/at-least/exactly-once in Kafka.” Commit before processing = at-most-once; process then commit = at-least-once; exactly-once = idempotent producer + transactions + read_committed (Kafka to Kafka) or idempotent/atomic sinks for external systems.',
    types_h2='Choosing a guarantee', types_html=types_html, warn=warn,
    steps_h2='Crash a worker, count the invoices', steps_intro='All outputs are real: Kafka 4.4.0; Python <code>confluent-kafka</code>; topic with 50 invoices; batches of 10; the worker hard-crashes (<code>os._exit</code>) after 25 invoices, then a second run continues. Scripts: <code>jobs/m3/l34_worker.py</code>, <code>l34_run.py</code>.',
    steps=steps, two=two, peel_intro='Now peel how real systems turn at-least-once into “once”.', peel_html=pe,
    scen_intro='Three live scenarios: missing invoices, double SMS, and offsets in the database.', scen=scen,
    uc_h2='Guarantees at work', ucs=[uc_('pay', 'ledger', 'green', '1. Payments', 'At-least-once + idempotent ledger writes by payment id.', ['Payments', '*upsert', 'Once']),
        uc_('GPS', 'pings', 'blue', '2. Location pings', 'At-most-once is fine; a newer ping replaces a lost one.', ['GPS', '*fast', 'Map']),
        uc_('stream', 'EOS', 'violet', '3. Stream processing', 'Kafka Streams exactly_once_v2 for Kafka-to-Kafka.', ['Input', '*transactions', 'Output']),
        uc_('DB', 'sink', 'acc', '4. Database sinks', 'Connect sinks upsert by key so replays are harmless.', ['Topic', '*upsert', 'DB']),
        uc_('mail', 'notify', 'blue', '5. Notifications', 'Idempotency keys stop duplicate emails and SMS.', ['Alert', '*key', 'One message'])],
    uc_note='Examples are simplified descriptions of common patterns.',
    pre='<b>Before you start:</b> <a href="../03-offsets-commits-and-lag/">3.3 Offsets, commits and lag</a>.')
