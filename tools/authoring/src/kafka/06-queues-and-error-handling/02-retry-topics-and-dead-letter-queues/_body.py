import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l62_dlq.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('One broken order arrives. Your consumer throws, restarts, reads the same order, throws again… and 10,000 good orders wait behind it. How do real teams stop this?',
    'They split failures into <b>transient</b> (retry later) and <b>permanent</b> (never works). Transient ones go to <b>retry topics</b> with growing delays; permanent ones and exhausted retries go to a <b>dead letter queue (DLQ)</b> with headers explaining why. In our lab, 8 orders: 6 succeeded, and 2 ended in the DLQ with their error, attempt count and original offset, while the main topic never stopped.',
    ['Why a single bad record can block a whole partition.',
     'The retry-topic ladder (5 s → 30 s → DLQ) and what to put in headers.',
     'Where DLQs are built in: Kafka Connect, Spring Kafka, share groups.'])
cmap = concept_map('Concept map. Beginner: consumer, error, poison message. Intermediate: transient vs permanent errors, retry topics, DLQ, headers. Advanced: non-blocking retries, ordering trade-offs, replay from DLQ, Connect errors.tolerance, idempotency.',
    [[('cs', 'Consumer loop', 'Lesson 3.1', B + '03-consumers/01-consumers-and-consumer-groups/'), ('pm', 'Poison message', 'blocks partition', None)],
     [('tp', 'Transient vs permanent', 'classify', None), ('rt', 'Retry topics', '5 s, 30 s', None), ('dq', 'Dead letter queue', 'park', None), ('hd', 'Headers', 'why + where', None)],
     [('nb', 'Non-blocking retries', 'order trade-off', None), ('rp', 'Replay from DLQ', 'after fix', None), ('kc', 'Connect DLQ', 'Module 7', None), ('id', 'Idempotency', 'Lesson 3.4', B + '03-consumers/04-delivery-guarantees/')]],
    [('cs', 'pm'), ('pm', 'tp'), ('tp', 'rt'), ('tp', 'dq'), ('rt', 'dq'), ('dq', 'hd'), ('rt', 'nb'), ('dq', 'rp'), ('dq', 'kc'), ('rp', 'id')],
    {'pm', 'tp', 'rt', 'dq', 'hd', 'nb', 'rp'},
    '<b>Builds on:</b> <a href="../01-share-groups-queues-for-kafka/">6.1</a>, <a href="../../03-consumers/04-delivery-guarantees/">3.4</a>. <b>Next:</b> Module 7 Kafka Connect.')
whw = why_how_where(
    'Kafka has no built-in “retry this one record later” for consumer groups: offsets are per partition, so one failing record stops everything behind it (head-of-line blocking).',
    'Catch the error, classify it, and produce the record to the next topic in a ladder (retry-5s → retry-30s → dlq) with headers (attempt, error, original topic/offset, retry-at). Separate consumers read retry topics and wait until the record is due. Commit the original offset so the main flow continues.',
    'Payments, orders, webhooks, any consumer calling external APIs; Kafka Connect sinks (errors.deadletterqueue.topic.name); Spring Kafka @RetryableTopic; Uber’s and many fintechs’ published designs.',
    'Retried records lose their original order relative to newer records with the same key. If order matters per key, block that key (or the partition) instead, or park all later records of that key too.')

def ladder(hl=-1):
    names = [('orders-62', 'blue'), ('retry-5s', 'amber'), ('retry-30s', 'amber'), ('dlq', 'red')]
    o = ''
    for k, (n, tn) in enumerate(names):
        o += box(14 + k * 160, 50, 130, 44, 'acc' if k == hl else tn, rx=8) + t(79 + k * 160, 76, n, 8.4, bold=True, mono=True)
        if k < 3: o += arrow(146 + k * 160, 72, 172 + k * 160, 72)
    o += t(320, 30, 'transient failure → next rung · permanent → straight to dlq', 7.6) + t(79, 118, '✓ success: commit', 7.4) + t(559, 118, 'humans / replay', 7.4)
    return o
scene_svg = scene('The retry ladder: the main topic orders-62 sends transient failures to retry-5s, then retry-30s, and finally the dead letter queue; permanent failures go straight to the dead letter queue.', ladder(),
                  'Failures move <tspan font-weight="700" class="s-acc">sideways</tspan>, good orders keep flowing.')
dialogue = '''K> Sir, the payment gateway was down for 2 minutes and our order consumer got stuck on one order, retrying forever. Everything behind it waited.
A> Classic head-of-line blocking. Don’t retry inside the main loop forever. Move the failed order <b>aside</b> to a retry topic and continue.
R> And a malformed JSON? Retrying won’t fix it.
A> Right: that’s a <b>permanent</b> error, it goes straight to the dead letter queue. Let’s build the ladder and push 8 orders through.'''

lv = '''
LEVELS> Error handling at three levels
L1> The “problem tray”
      <ul>
        <li>A cashier with a cheque that won’t clear does not stop the queue. She puts it in a “try again at 3 pm” tray. If it fails again, it goes to the manager’s “problem” file with a note. Torn cheques go straight to the file.</li>
      </ul>
L2> The pattern
      <ul>
        <li><b>Classify</b>: transient (timeouts, 503, lock conflicts) vs permanent (bad JSON, schema mismatch, validation failure).</li>
        <li><b>Retry topics</b> with increasing delays (e.g. 5 s, 30 s, 5 min). A retry consumer reads a record, and if <code>x-retry-at</code> is in the future it waits (pause/seek or sleep) before processing.</li>
        <li><b>DLQ</b> gets permanent failures and exhausted retries. Always add headers: error class and message, attempt count, original topic, partition, offset, timestamp. Commit the original offset after producing to the next topic.</li>
      </ul>
L3> Production details
      <ul>
        <li>Producing the retry record and committing the offset are two actions: use transactions (Lesson 3.5) or make processing idempotent, or a crash between them can duplicate.</li>
        <li>Ordering per key breaks with non-blocking retries. Options: blocking retries with backoff for strictly ordered streams, or park a key (route all its later records to retry while one is pending).</li>
        <li>Built-in options: Kafka Connect <code>errors.tolerance=all</code> + <code>errors.deadletterqueue.topic.name</code> + <code>errors.deadletterqueue.context.headers.enable</code>; Spring Kafka <code>@RetryableTopic</code>/<code>DeadLetterPublishingRecoverer</code>; share groups (6.1) RELEASE with delivery-count limit. Monitor DLQ size and build a <b>replay</b> tool that re-publishes fixed records to the main topic.</li>
      </ul>
/LEVELS
'''
HD = figure('Dissection of a DLQ record: key 7, the original value, and headers x-attempt 4, x-error Transient payment gateway 503, x-original-topic orders-62, x-original-offset 6.',
    t(16, 22, 'One record in orders-62-dlq', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('key=7', 'card', 1), ('value={"id":7,…}', 'blue', 2), ('x-attempt=4', 'amber', 3), ('x-error=503', 'red', 4), ('x-original-offset=6', 'green', 5)]) +
    legend(16, 84, [(1, 'Key', 'same key as the original, keeps partitioning'), (2, 'Value', 'untouched bytes, so you can replay exactly'),
                    (3, 'Attempt', '1 original + 2 retries + this hop'), (4, 'Error', 'what broke, for triage'), (5, 'Origin', 'topic + offset: find it in the source')], size=8, gap=15, w=90),
    h=172, caption='Real record from our lab.')
extra = '''

  <h3>Dissect a DLQ record</h3>
''' + HD

types_html = table(['Strategy', 'Blocks partition?', 'Order kept?', 'Use'], [
    ['Retry in place (sleep + retry)', 'yes', 'yes', 'short blips, strictly ordered data'], ['Skip and log', 'no', 'yes (minus lost)', 'metrics, non-critical'],
    ['Retry topics + DLQ', 'no', 'no (for retried)', 'orders, webhooks, APIs'], ['DLQ only', 'no', 'no', 'permanent errors'],
    ['Share group RELEASE / REJECT', 'no', 'no', 'job queues (6.1)'],
], minw=620) + table(['Error', 'Type', 'Route'], [
    ['timeout, 503, 429', 'transient', 'retry ladder'], ['bad JSON, missing field', 'permanent', 'DLQ now'],
    ['schema / deserialization error', 'permanent', 'DLQ now'], ['DB unique violation', 'often permanent', 'DLQ or ignore (already done)'],
], minw=520)
warn = 'A DLQ nobody reads is a data-loss bin with extra steps. Alert when it grows, name an owner, and keep a replay script. Also never let a deserialization error crash the consumer: catch it and DLQ the raw bytes.'

steps = [
    ('Step 1 · Topics and orders',
     code('python', 'l62.py', "topics: orders-62, orders-62-retry-5s, orders-62-retry-30s, orders-62-dlq\norders = ['ok','ok','bad-json','ok','flaky','ok','payment-down','ok']", sec('== 1)', '== 2)')),
     'Four topics form the ladder. In the lab the 5 s and 30 s delays are shrunk to 2 s and 4 s.'),
    ('Step 2 · Process with classification',
     code('python', 'l62.py', "try:\n    process(raw)\nexcept Transient: produce(NEXT[topic], value, headers=attempt+1, error, origin, retry_at)\nexcept Permanent: produce('orders-62-dlq', value, headers=...)\nconsumer.commit(msg)", sec('== 2)', '== 3)')),
     'Orders 1–8 on the main topic finished in 0.1 s: 5 OK, malformed order 3 straight to DLQ, 5 and 7 to retry-5s. At +5.3 s order 5 succeeded on attempt 2. Order 7 climbed to retry-30s and then the DLQ at +9.3 s.'),
    ('Step 3 · Read the DLQ',
     code('python', 'dlq_reader.py', "for m in consumer('orders-62-dlq'):\n    print(m.key(), m.value(), m.headers())", sec('== 3)', '== 4)')),
     'Each DLQ record carries the original bytes and the full story: error, attempt count, original topic and offset.'),
    ('Step 4 · Count',
     code('bash', 'terminal', 'kafka-get-offsets.sh --bootstrap-server k1:9092 --topic orders-62   # and the others', sec('== 4)')),
     '8 in, 2 retried once, 1 retried twice, 2 parked. Every order is accounted for.'),
]
see = [term([('8 orders', W), ('ok 5 · bad 1 · flaky 1 · down 1', W)], size=7.2), term([('3 -> dlq (Permanent)', RD), ('5 -> retry-5s -> OK', G), ('7 -> 5s -> 30s -> dlq', Y)], size=7.0),
       term([('key 7 x-attempt 4', Y), ('x-error 503', RD), ('x-original-offset 6', W)], size=7.0), term([('orders-62 8', W), ('retry-5s 2 · retry-30s 1', W), ('dlq 2', RD)], size=7.0)]
B1 = [ladder(0), ladder(1), ladder(3), ladder(-1)]
B1 = [b + cap(c, '', tn, y=134, h=30) for b, c, tn in zip(B1, ['Main topic', 'Retry rung', 'Dead letter queue', 'Every order accounted'], ['blue', 'amber', 'red', 'green'])]
two = anim_two('Retry and DLQ', 'Ladder in action', 'Real outputs from the lab', 'Where each order went', see, B1, ['Load.', 'Process.', 'DLQ.', 'Count.'], ['Main.', 'Retry.', 'Park.', 'Balance.'])
pe = peel('Order 7, layer by layer', 'Payment gateway down. (From the lab.)',
    [('Main', ''), ('Classify', ''), ('Retry 5 s', ''), ('Retry 30 s', ''), ('DLQ', ''), ('Replay', '')],
    [['Main', 'orders-62 offset 6', 'process → 503', ''], ['Classify', 'Transient', 'produce retry-5s', 'commit offset 6'],
     ['Retry 5 s', 'wait until due', 'still 503', '→ retry-30s'], ['Retry 30 s', 'wait until due', 'still 503', '→ dlq'],
     ['DLQ', 'x-attempt 4', 'x-error 503', 'alert'], ['Replay', 'gateway fixed', 're-publish to orders-62', 'idempotent']],
    ['Fail.', 'Classify.', 'Retry.', 'Retry.', 'Park.', 'Replay.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Gateway outage', 'Payment API down 2 minutes. (Typical.)', ('Retry topics', 'Absorb transient failures'), [
    ('503s for 2 min', 'hundreds of orders', 'Transient.', 'red'), ('Retry-5s, retry-30s, retry-5m', 'ladder', 'Waits.', 'amber'),
    ('Gateway back', 'retries succeed', 'Recovered.', 'green'), ('Main topic never blocked', 'new orders fine', 'No backlog.', 'green'),
    ('DLQ empty', 'nothing lost', 'Done.', 'blue')], ['Outage.', 'Ladder.', 'Recover.', 'Flow.', 'Clean.'], 'scenario-outage') + \
       five('Real-time scenario 2', 'Schema change breaks consumer', 'New field type. (Typical.)', ('Permanent errors', 'DLQ, not retry'), [
    ('Producer deploys v2', 'price becomes string', 'Bad data.', 'blue'), ('Consumer fails parsing', 'every record', 'Permanent.', 'red'),
    ('All to DLQ', 'alert fires', 'Visible.', 'amber'), ('Fix consumer', 'handle both types', 'Deploy.', 'green'),
    ('Replay DLQ', 'to main topic', 'Recovered.', 'blue')], ['Deploy.', 'Fail.', 'Park.', 'Fix.', 'Replay.'], 'scenario-schema') + \
       five('Real-time scenario 3 · advanced', 'Out-of-order cancellation', 'Retry reorders events. (Typical.)', ('Ordering trade-off', 'Park the key'), [
    ('Order 9 placed fails', 'goes to retry', 'Pending.', 'amber'), ('Order 9 cancelled arrives', 'processed first', 'Wrong order.', 'red'),
    ('Rule: key has pending retry?', 'park later events too', 'Keep order.', 'green'), ('Retry succeeds', 'then cancel applied', 'Correct.', 'green'),
    ('Or: blocking retry', 'for ordered streams', 'Choose.', 'blue')], ['Fail.', 'Overtake.', 'Park.', 'Apply.', 'Choose.'], 'scenario-order')
assemble(HERE, h2_story='One bad order should not stop the kitchen', hook_html=hk,
    narration='Yesterday TiffinGo’s payment gateway was down for two minutes and the order consumer got stuck. Kabir needs a design where failures step aside and good orders keep flowing.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Retry topics and dead letter queues',
    formal='A <b>retry topic</b> holds records whose processing failed with a transient error, to be re-processed after a delay by a separate consumer; several retry topics with increasing delays form a <b>retry ladder</b>. A <b>dead letter queue (DLQ)</b> is a topic that stores records that cannot be processed (permanent errors or exhausted retries), with headers describing the failure, for inspection and replay. The pattern gives <b>non-blocking</b> error handling at the cost of per-key ordering.',
    simple='When an order fails, don’t keep hitting it. If the problem may pass, put it in a “try again later” topic. If it can never work, or still fails after a few tries, put it in a “problem” topic with a note. Everyone else keeps moving.',
    term_rows=[('Poison message', 'Record that always fails.'), ('Head-of-line blocking', 'One record stops those behind it.'), ('Transient error', 'May pass; retry.'), ('Permanent error', 'Will not pass; DLQ.'), ('Retry topic', 'Delayed reprocessing.'), ('DLQ', 'Parking topic for failures.'), ('Replay', 'Re-publish after fix.'), ('Backoff', 'Growing delay between tries.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Kafka retries failed consumer records for you.', 'Producer retries yes; consumer processing no (except share groups).', 'You build the ladder.'),
               ('Retry everything.', 'Permanent errors never succeed; DLQ them now.', 'Order 3.'),
               ('A DLQ means the record is lost.', 'It is parked with context and can be replayed.', 'Step 3 headers.')],
    exam='“How do you handle failures in a Kafka consumer?” Classify transient vs permanent; non-blocking retry topics with backoff and headers; DLQ with error/origin headers; commit original offset; idempotent processing; monitor and replay DLQ; ordering trade-off; Connect errors.deadletterqueue.',
    types_h2='Strategies and error types', types_html=types_html, warn=warn,
    steps_h2='Build the ladder', steps_intro='All outputs are real: Kafka 4.4.0, Python confluent-kafka 2.16, 3 brokers.',
    steps=steps, two=two, peel_intro='Now follow order 7.', peel_html=pe,
    scen_intro='Three live scenarios: an outage, a schema break, and reordering.', scen=scen,
    uc_h2='DLQs at work', ucs=[uc_('pay', 'payments', 'red', '1. Payments', 'Gateway timeouts retried with backoff.', ['Charge', '*retry', 'Settle']),
        uc_('hook', 'webhooks', 'blue', '2. Webhooks', 'Partner endpoints down for hours.', ['Event', '*ladder', 'Deliver']),
        uc_('conn', 'Connect', 'violet', '3. Kafka Connect sinks', 'errors.deadletterqueue.topic.name.', ['Record', '*bad row', 'DLQ']),
        uc_('etl', 'ETL', 'green', '4. Data pipelines', 'Bad rows parked, good rows flow.', ['Rows', '*validate', 'Warehouse'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../01-share-groups-queues-for-kafka/">6.1 Share groups</a>.')
