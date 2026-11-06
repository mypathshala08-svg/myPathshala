import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l25_dup.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('One ₹75,000 payment was stored three times. Kafka did nothing wrong. Then we flipped one setting.',
    'We froze one follower so acknowledgements were late. The producer thought its request was lost and retried: with idempotence <b>off</b>, the same payment landed at offsets 0, 1 and 2. With idempotence <b>on</b>, the broker recognised the retry and stored it once. You will see the producer id and sequence numbers that make the difference.',
    ['Why retries create duplicates in the first place.',
     'The three numbers (producer id, epoch, sequence) the broker checks.',
     'What idempotence does <b>not</b> protect you from.'])
cmap = concept_map('Concept map. Beginner: retry, duplicate, enable.idempotence. Intermediate: producer id, epoch, sequence numbers, max.in.flight and ordering, retry timeouts. Advanced: transactions, exactly-once, application-level deduplication.',
    [[('re', 'Retries', 'resend on error', None), ('du', 'Duplicates', 'same record twice', None), ('ei', 'enable.idempotence', 'default true', None)],
     [('pi', 'Producer id + epoch', 'who is writing', None), ('sq', 'Sequence numbers', 'per partition', None), ('mf', 'max.in.flight ≤ 5', 'ordering', None), ('to', 'Retry timing', 'backoff + deadline', B + '02-producers/01-how-a-producer-sends-a-message/')],
     [('tx', 'Transactions', 'Lesson 3.5', B + '03-consumers/05-transactions-and-exactly-once/'), ('eo', 'Exactly-once', 'end to end', B + '03-consumers/04-delivery-guarantees/'), ('ad', 'App-level dedup', 'restarts, re-sends', None)]],
    [('re', 'du'), ('du', 'ei'), ('ei', 'pi'), ('pi', 'sq'), ('sq', 'mf'), ('pi', 'tx'), ('tx', 'eo'), ('sq', 'ad'), ('re', 'to')],
    {'re', 'du', 'ei', 'pi', 'sq', 'mf', 'to', 'ad'},
    '<b>Builds on:</b> <a href="../04-acks-and-durability/">2.4 acks</a>. <b>Next:</b> Module 3, <a href="../../03-consumers/01-consumers-and-consumer-groups/">3.1 Consumers and consumer groups</a>.')
whw = why_how_where(
    'Networks lose responses, not just requests. A producer that retries cannot know whether the first attempt was stored, so without help it may store the record twice.',
    'The broker gives each producer an id; the producer numbers every batch per partition. The broker keeps the last sequences and silently drops a batch it already has.',
    'On by default in every modern Kafka client: payments, orders, CDC, anything where a duplicate costs money.',
    'It does not deduplicate across producer restarts or when your app calls produce() twice for the same business event: use transactions or business keys.')

sc_ = (t(160, 18, 'idempotence OFF', 9, 'red', bold=True) + pcol(40, 32, 'P0', ['t045', 't045', 't045'], 'red', cw=58, ch=24) + t(160, 78, 'offsets 0, 1, 2: three copies', 8, 'red') +
       t(160, 98, 'producerId: -1  (no sequence)', 7.8, 'ink2', mono=True) +
       t(480, 18, 'idempotence ON', 9, 'green', bold=True) + pcol(380, 32, 'P0', ['t045'], 'green', cw=58, ch=24) + t(480, 78, 'offset 0: one copy', 8, 'green') +
       t(480, 98, 'producerId: 7001  baseSequence: 0', 7.8, 'ink2', mono=True) + box(14, 110, 612, 24, 'card', rx=6) + t(320, 126, 'Same failure both times: follower frozen → late ack → producer timeout → retry', 8.2, 'ink', bold=True))
scene_svg = scene('Left: with idempotence off, payment t045 was stored three times at offsets 0, 1 and 2 with producerId -1. Right: with idempotence on, it was stored once at offset 0 with producerId 7001 and sequence 0. Both runs had the same failure: a frozen follower delayed the acknowledgement and the producer retried.', sc_,
                  'Retries are safe only with <tspan font-weight="700" class="s-acc">idempotence</tspan>.')
dialogue = '''R> Sir, how can a payment be stored three times? The producer sent it once.
A> The producer sent it once, did not get an answer in time, and sent it again. And again. The broker had stored every attempt; only the <i>answers</i> were late.
K> So should we turn retries off?
A> Then a short network blip loses payments. The real fix is <b>idempotence</b>: the broker remembers who sent what, using a producer id and sequence numbers, and ignores copies. Let’s create the duplicate for real, then prevent it.'''

lv = '''
LEVELS> Idempotence at three levels
L1> Numbered cheques
      <ul>
        <li>Each cheque from your chequebook has a number. If the bank receives cheque no. 17 twice, it pays only once. The producer id is your account; the sequence is the cheque number.</li>
      </ul>
L2> How it works
      <ul>
        <li>On start, the producer gets a <b>producer id (PID)</b> and <b>epoch</b> from the broker (InitProducerId).</li>
        <li>For every partition it numbers batches with a <b>sequence</b> 0, 1, 2 … The leader stores PID, epoch and sequences with each batch.</li>
        <li>If a batch arrives with a sequence already stored, the leader returns success <i>without</i> appending again. A gap in sequences gives <code>OUT_OF_ORDER_SEQUENCE_NUMBER</code>.</li>
      </ul>
L3> Rules and limits
      <ul>
        <li>Requires <code>acks=all</code>, <code>retries &gt; 0</code> and <code>max.in.flight.requests.per.connection ≤ 5</code>; brokers keep state for the last 5 batches per producer per partition, which also keeps order on retries.</li>
        <li>Without idempotence, <code>max.in.flight &gt; 1</code> plus retries can <b>reorder</b> records (batch 2 succeeds, batch 1 retried later).</li>
        <li>A restarted producer gets a <b>new PID</b>, so re-sending after a crash is not deduplicated. For read-process-write pipelines use <b>transactions</b> (<code>transactional.id</code>, Lesson 3.5), which also fence old “zombie” producers via the epoch.</li>
        <li>Retry pacing: <code>retry.backoff.ms</code> (100 ms) growing to <code>retry.backoff.max.ms</code> (1 s) with exponential backoff (KIP-580); everything stops at the delivery timeout.</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of two kafka-dump-log lines. Without idempotence: producerId -1, baseSequence -1, three batches. With idempotence: producerId 7001, producerEpoch 0, baseSequence 0, one batch.',
    t(16, 22, 'kafka-dump-log, idempotence OFF (3 batches)', 8.6, 'red', anchor='start', bold=True) +
    fields(16, 32, [('baseOffset: 0 / 1 / 2', 'red', 1), ('baseSequence: -1', 'card', 2), ('producerId: -1', 'card', None), ('producerEpoch: -1', 'card', None)]) +
    t(16, 78, 'kafka-dump-log, idempotence ON (1 batch)', 8.6, 'green', anchor='start', bold=True) +
    fields(16, 88, [('baseOffset: 0', 'green', None), ('baseSequence: 0', 'violet', 3), ('producerId: 7001', 'violet', 4), ('producerEpoch: 0', 'violet', 5)]) +
    legend(16, 144, [(1, 'Three batches', 'each retry was appended as a new batch: duplicates'),
                     (2, 'No sequence', 'the broker has nothing to compare, so it cannot detect a repeat'),
                     (3, 'Sequence 0', 'first batch of this producer for this partition'),
                     (4, 'Producer id', 'assigned by the cluster when the producer started'),
                     (5, 'Epoch', 'bumps when a producer is re-initialised; fences zombies')], size=8, gap=15, w=110),
    h=230, caption='Real dump-log fields from our two runs.')
extra = '''

  <h3>Dissect the evidence</h3>
''' + DIS

types_html = table(['Setting', 'Default (Kafka 3.0+)', 'Effect'], [
    ['enable.idempotence', 'true', 'PID + sequences; no duplicates from retries'],
    ['acks', 'all', 'required for idempotence'],
    ['retries', '2147483647 (Java)', 'retry until the delivery timeout'],
    ['max.in.flight.requests.per.connection', '5', '≤ 5 keeps order with idempotence'],
    ['retry.backoff.ms / retry.backoff.max.ms', '100 ms / 1000 ms', 'exponential pause between retries'],
    ['delivery.timeout.ms (Java) / message.timeout.ms', '120 s / 300 s', 'stop retrying, report error'],
], minw=620) + table(['Duplicate source', 'Fixed by idempotence?', 'Use instead'], [
    ['Producer retry after a lost response', 'yes', '—'],
    ['Producer app restarts and re-sends', 'no (new PID)', 'transactions or business-key dedup'],
    ['App calls produce() twice for one event', 'no', 'dedup in app (e.g. payment id)'],
    ['Consumer re-processes after a crash', 'no', 'idempotent consumer / transactions (Module 3)'],
], minw=560)
warn = 'If you explicitly set <code>acks=1</code> or <code>max.in.flight.requests.per.connection</code> above 5 in the Java client, idempotence cannot work. If you <i>also</i> set <code>enable.idempotence=true</code> explicitly, the producer fails at startup with a config error; if you left it at the default, it is silently turned off. Check effective configs, not just what you think you set.'

steps = [
    ('Step 1 · Freeze a follower, idempotence OFF',
     code('python', 'l25_dup.py', 'p = Producer({"bootstrap.servers": "k1:9092", "acks": "all", "enable.idempotence": False,\n              "retries": 10, "request.timeout.ms": 3000, "retry.backoff.ms": 500})\np.produce(topic, key="user3@upi", value="pay Rs 75000 (t045)")\n# meanwhile: docker pause k3  (a follower of this partition)', sec('== 1)', '  records in the partition:')),
     'Leader 1 appends at once but must wait for follower 3 (acks=all). Our request timed out after 3 s, so the producer retried, twice. About 8 s later the controller fenced the frozen broker (its session timed out), the ISR shrank and the leader finally answered “offset 2”.'),
    ('Step 2 · Look inside: three copies',
     code('bash', 'terminal', 'kafka-console-consumer.sh --topic idem-off --from-beginning --formatter-property print.offset=true\nkafka-dump-log.sh --files /var/lib/kafka/data/idem-off-0/00000000000000000000.log', sec('  records in the partition:', '== 2)')),
     'Offsets 0, 1, 2 all contain the same payment. The batches carry <code>producerId: -1</code> and no sequence, so the broker had no way to know they were the same.'),
    ('Step 3 · Same failure, idempotence ON',
     code('python', 'l25_dup.py', 'Producer({..., "enable.idempotence": True, ...})   # the default since Kafka 3.0', sec('== 2)')),
     'The producer again waited and retried, but now each attempt carried <code>producerId 7001, sequence 0</code>. The leader saw sequence 0 was already stored, answered success, and appended nothing new: <b>one copy</b>.'),
]

see = [term([('idempotence=False', W), ('$ docker pause k3', Y), ('delivered after 8 s -> offset 2', RD)], size=7.2),
       term([('Offset:0  pay Rs 75000 (t045)', RD), ('Offset:1  pay Rs 75000 (t045)', RD), ('Offset:2  pay Rs 75000 (t045)', RD), ('producerId: -1', W)], size=7.0),
       term([('idempotence=True -> offset 0', G), ('Offset:0  pay Rs 75000 (t045)', G), ('producerId: 7001  baseSequence: 0', G)], size=7.0)]
def flow(dup):
    o = opbox(10, 40, 'producer', 'PID 7001' if not dup else 'no PID', 'acc', 80, 30) + opbox(260, 40, 'leader', '', 'blue', 90, 30)
    o += arrow(90, 48, 260, 48, 'ink3', 1) + t(175, 44, 'try 1', 7, 'ink2') + arrow(260, 64, 90, 64, 'red', 1) + t(175, 76, 'ack late → timeout', 7, 'red')
    o += arrow(90, 96, 260, 96, 'ink3', 1) + t(175, 92, 'retry (seq 0)' if not dup else 'retry', 7, 'ink2')
    return o
B1 = [t(180, 14, 'Ack is late, producer retries', 9, bold=True) + flow(True) + t(300, 116, 'appended again', 7.6, 'red', bold=True) + cap('Retry looks like a new record.', '', 'red', y=144, h=30),
      t(180, 14, 'Three copies stored', 9, bold=True) + pcol(70, 50, 'P0', ['t045', 't045', 't045'], 'red', cw=60, ch=24) + cap('No PID: no way to detect.', '', 'red', y=144, h=30),
      t(180, 14, 'Same retry, PID + sequence', 9, bold=True) + flow(False) + t(300, 116, 'seq 0 seen → skip', 7.6, 'green', bold=True) + cap('Deduplicated by the broker.', '', 'green', y=144, h=30)]
two = anim_two('Idempotent producer', 'Retry without duplicates', 'Real outputs from the lab', 'What the leader decides', see, B1, ['Retry.', 'Duplicates.', 'Idempotent.'], ['Timeout.', 'Three copies.', 'Skip.'])
pe = peel('Retry of payment t045 with idempotence', 'From startup to the duplicate check. (Our run.)',
    [('InitProducerId', ''), ('Number batch', ''), ('First attempt', ''), ('Timeout + retry', ''), ('Leader check', ''), ('Answer', '')],
    [['InitProducerId', 'cluster assigns', 'PID 7001, epoch 0', ''], ['Number batch', 'first batch for P0', 'gets sequence 0', ''],
     ['First attempt', 'leader appends offset 0', 'waits for ISR (k3 frozen)', ''], ['Timeout + retry', 'no answer in 3 s', 'resend: PID 7001, seq 0', 'same numbers'],
     ['Leader check', 'PID 7001 seq 0', 'already at offset 0', '→ do not append'], ['Answer', 'success, offset 0', 'one copy on disk', 'proved by dump-log']],
    ['PID.', 'Number.', 'Send.', 'Retry.', 'Check.', 'Once.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Double-charged customers', 'Retries without idempotence. (Typical.)', ('Idempotence', 'Keep enable.idempotence=true (the default)'), [
    ('Old config copied', 'enable.idempotence=false', 'From a 2018 blog.', 'blue'), ('Network blip', 'responses delayed', 'Retries.', 'amber'),
    ('Payments duplicated', 'billing charges twice', 'Refunds.', 'red'), ('Remove the override', 'default true', 'acks=all.', 'green'),
    ('Same blip, no dupes', 'like Step 3', 'Fixed.', 'blue')], ['Config.', 'Blip.', 'Double.', 'Fix.', 'Safe.'], 'scenario-double') + \
       five('Real-time scenario 2', 'Duplicates after a crash', 'What idempotence cannot catch. (Typical.)', ('Beyond idempotence', 'Restarts get a new producer id; use transactions or business-key dedup'), [
    ('Producer sent t045', 'app crashed before callback', 'Unsure.', 'blue'), ('App restarts, re-sends', 'new PID 7002', 'Not a retry.', 'amber'),
    ('Broker stores it again', 'different PID', 'Duplicate.', 'red'), ('Consumer dedups by txn id', 'or transactions', 'Lesson 3.5.', 'green'),
    ('Design for it', 'idempotent consumers', 'End-to-end.', 'blue')], ['Crash.', 'Re-send.', 'Dupe.', 'Dedup.', 'Design.'], 'scenario-restart') + \
       five('Real-time scenario 3 · advanced', 'Reordered events', 'Retries with many in-flight requests. (Typical.)', ('Ordering on retry', 'Idempotence keeps order with up to 5 in-flight requests'), [
    ('PLACED then PAID', 'two batches in flight', 'Same partition.', 'blue'), ('PLACED batch fails', 'PAID succeeds', 'Retry later.', 'amber'),
    ('Without idempotence', 'PAID before PLACED', 'Wrong state.', 'red'), ('With idempotence', 'sequence gap → broker waits', 'Order kept.', 'green'),
    ('Rule', 'idempotence + in-flight ≤ 5', 'Defaults.', 'blue')], ['Two batches.', 'Failure.', 'Reorder.', 'Kept.', 'Rule.'], 'scenario-order')
assemble(HERE, h2_story='One payment, stored three times', hook_html=hk,
    narration='A TiffinGo customer complains of a triple charge. The logs show the payment service called <code>produce()</code> only once. Kabir has to explain how Kafka ended up with three copies.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Idempotent producer and retries',
    formal='An <b>idempotent producer</b> (<code>enable.idempotence=true</code>, default since Kafka 3.0) guarantees that retries do not introduce duplicates or reorder records within a partition for the lifetime of the producer session. The broker assigns a <b>producer id</b> and <b>epoch</b>; the producer attaches a monotonically increasing <b>sequence number</b> per partition to each batch. The partition leader tracks the most recent sequences per producer and rejects or acknowledges-without-append any batch whose sequence it has already written. Idempotence requires acks=all, retries enabled and at most 5 in-flight requests per connection.',
    simple='The broker remembers which producer sent which numbered batch. If the same numbered batch arrives again because of a retry, the broker says “OK, got it” but does not store it a second time.',
    term_rows=[('Retry', 'Resending after an error/timeout.'), ('Idempotent', 'Doing it twice = doing it once.'), ('Producer id (PID)', 'Id given to a producer session.'), ('Epoch', 'Version of that producer id.'), ('Sequence number', 'Per-partition batch counter.'), ('In-flight requests', 'Sent but not yet answered.'), ('OUT_OF_ORDER_SEQUENCE', 'Gap in sequences detected.'), ('Zombie producer', 'Old instance still writing.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Duplicates only happen if the app sends twice.', 'Producer retries after a lost or late response also duplicate.', 'Step 2: one produce(), three copies.'),
               ('Idempotence uses a “request id”.', 'It uses a producer id, epoch and per-partition sequence numbers.', 'Step 3: producerId 7001, baseSequence 0.'),
               ('Idempotence gives exactly-once end to end.', 'Only within one producer session; restarts and consumers need more.', 'Types table: restarts get a new PID.')],
    exam='“How does the idempotent producer work?” Broker assigns PID/epoch; producer numbers batches per partition; leader keeps last 5 sequences per PID and drops duplicates; requires acks=all, retries>0, max.in.flight ≤5; default since 3.0; covers retries within a session, not restarts (use transactions).',
    types_h2='Settings and limits', types_html=types_html, warn=warn,
    steps_h2='Create a duplicate, then prevent it', steps_intro='All outputs are real: Kafka 4.4.0, 3 brokers; Python <code>confluent-kafka</code>; one-partition topics with replicas on brokers 1, 2, 3; follower k3 frozen with <code>docker pause</code>. Script: <code>jobs/m2/l25_dup.py</code>.',
    steps=steps, two=two, peel_intro='Now peel the retry with idempotence.', peel_html=pe,
    scen_intro='Three live scenarios: double charges, crash re-sends, and reordering.', scen=scen,
    uc_h2='Idempotence at work', ucs=[uc_('pay', 'charges', 'green', '1. Payments', 'Retries during network blips never double-charge.', ['Payment', '*PID + seq', 'Once']),
        uc_('order', 'status', 'blue', '2. Order status', 'PLACED, PAID, DELIVERED stay in order despite retries.', ['Events', '*in-flight ≤ 5', 'Ordered']),
        uc_('CDC', 'changes', 'violet', '3. Database change capture', 'Connectors rely on idempotent producers (Module 7).', ['DB', '*idempotent', 'No dupes']),
        uc_('bank', 'ledger', 'acc', '4. Ledgers', 'Add business-key dedup for app restarts.', ['Txn id', '*dedup', 'Exact']),
        uc_('stream', 'EOS', 'blue', '5. Stream processing', 'Kafka Streams builds exactly-once on idempotence + transactions.', ['Input', '*transactions', 'Output'])],
    uc_note='Examples are simplified descriptions of common patterns.',
    pre='<b>Before you start:</b> <a href="../04-acks-and-durability/">2.4 acks and durability</a> (ISR, acks=all).')
