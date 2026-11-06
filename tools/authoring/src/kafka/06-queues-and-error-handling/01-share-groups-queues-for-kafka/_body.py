import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l61_share.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('A topic with 2 partitions, and you want 10 chefs working on it at once. A normal consumer group says “only 2”. What now?',
    'Kafka 4.x has <b>share groups</b> (KIP-932, “Queues for Kafka”): consumers share partitions record by record, like a job queue. Each record is <b>locked</b> to one consumer, then <b>acknowledged</b>, <b>released</b> for another try, or <b>rejected</b>. In our lab, 3,000 jobs were processed with zero duplicates, and a released record came back exactly <b>5 times</b> before Kafka gave up on it.',
    ['How a share group differs from a consumer group.',
     'Acquire, lock, accept / release / reject, and the delivery count.',
     'When to use share groups and when not (ordering!).'])
cmap = concept_map('Concept map. Beginner: queue vs pub-sub, consumer group. Intermediate: share group, record lock, acknowledgement types. Advanced: delivery count limit, share-partition start offset, share coordinator, ordering trade-off.',
    [[('qp', 'Queue vs pub-sub', 'Lesson 1.2', B + '01-introduction/02-messaging-models-queue-vs-pub-sub/'), ('cg', 'Consumer group', 'Lesson 3.1', B + '03-consumers/01-consumers-and-consumer-groups/')],
     [('sg', 'Share group', 'KIP-932', None), ('lk', 'Record lock', '30 s', None), ('ak', 'Accept / release / reject', 'per record', None)],
     [('dc', 'Delivery count', 'limit 5', None), ('so', 'SPSO + in-flight window', 'state', None), ('co', 'Share coordinator', '__share_group_state', None), ('dl', 'Retries and DLQ', 'Lesson 6.2', B + '06-queues-and-error-handling/02-retry-topics-and-dead-letter-queues/')]],
    [('qp', 'sg'), ('cg', 'sg'), ('sg', 'lk'), ('lk', 'ak'), ('ak', 'dc'), ('sg', 'so'), ('so', 'co'), ('dc', 'dl')],
    {'sg', 'lk', 'ak', 'dc', 'so', 'co'},
    '<b>Builds on:</b> <a href="../../01-introduction/02-messaging-models-queue-vs-pub-sub/">1.2</a>, <a href="../../03-consumers/01-consumers-and-consumer-groups/">3.1</a>. <b>Next:</b> <a href="../02-retry-topics-and-dead-letter-queues/">6.2 Retry topics and DLQs</a>.')
whw = why_how_where(
    'Consumer groups cap parallelism at the partition count and block a partition on one slow record. Work queues (emails, image jobs, tickets) want “any free worker takes the next job”.',
    'Consumers join a share group (group.type share). The broker hands out batches of records with a time-limited lock; the consumer acknowledges each record: ACCEPT (done), RELEASE (give to someone again), REJECT (unprocessable). Unacknowledged records return when the lock expires. Each delivery increments a count; at the limit the record is archived.',
    'Job queues, notification senders, ML inference workers, anything where order does not matter but throughput and elastic workers do. Previously teams used RabbitMQ/SQS next to Kafka for this.',
    'No ordering guarantee across records, even in one partition. Offsets are tracked by the broker (share-partition), not committed by you. Needs a recent Kafka (early access in 4.0, preview in 4.1, generally available in 4.2; share.version ≥ 1) and a client that supports it (Java KafkaShareConsumer; other clients are catching up).')

def chefs(states):
    o = box(14, 30, 246, 40, 'card', rx=6) + t(137, 54, 'partition 0 records', 8, bold=True)
    for k, (lbl, tone) in enumerate(states):
        o += box(20 + k * 29, 78, 25, 24, tone, rx=3) + t(32.5 + k * 29, 94, lbl, 7, 'ink')
    for j, n in enumerate('ABC'):
        o += box(272, 24 + j * 36, 82, 30, 'blue', rx=6) + icon('chef', 274, 27 + j * 36, 0.6) + t(322, 43 + j * 36, f'chef {n}', 8, bold=True)
    return o
ST = [('1', 'green'), ('2', 'green'), ('3', 'acc'), ('4', 'acc'), ('5', 'violet'), ('6', 'blue'), ('7', 'blue'), ('8', 'card')]
scene_svg = scene('Records of one partition in different states: two acknowledged (green), two locked by chef A (orange), one locked by chef B (violet), two available (blue), one not yet fetched. Three chefs share the same partition.', chefs(ST),
                  'One partition, <tspan font-weight="700" class="s-acc">many chefs</tspan>: records are locked one by one.')
dialogue = '''K> Sir, Diwali rush: 10 kitchen workers, but the cooking-jobs topic has only 2 partitions. Consumer group gives work to 2 and 8 sit idle.
A> Because a consumer group assigns <b>whole partitions</b>. For a job queue use a <b>share group</b>: partitions are shared, records are locked one at a time.
R> And if a worker crashes holding a job?
A> The lock expires (30 s) and someone else gets it. If a job keeps failing, after 5 deliveries Kafka archives it. Let’s see it live.'''

lv = '''
LEVELS> Share groups at three levels
L1> Token counter at a canteen
      <ul>
        <li>Orders come on a counter. Any free cook picks the next ticket, writes their name on it (lock), and stamps it DONE when served. If a cook leaves without stamping, after a while the ticket goes back. A ticket that fails 5 times goes to the manager’s file.</li>
      </ul>
L2> The mechanics
      <ul>
        <li>Create by using a <b>share consumer</b> with a group id: the group is a <b>share group</b> (separate from consumer groups; listed by <code>kafka-share-groups.sh</code>).</li>
        <li>Record states: <b>Available → Acquired</b> (locked, <code>share.record.lock.duration.ms</code> 30 s) <b>→ Acknowledged</b> or back to <b>Available</b> (release/timeout) or <b>Archived</b> (reject or <code>share.delivery.count.limit</code> 5 reached).</li>
        <li>Implicit mode: everything returned by <code>poll()</code> is accepted on the next poll. Explicit mode (<code>share.acknowledgement.mode=explicit</code>): call <code>acknowledge(record, ACCEPT|RELEASE|REJECT)</code> then <code>commitSync()</code>.</li>
      </ul>
L3> Under the hood
      <ul>
        <li>Each share-partition keeps a <b>Share-Partition Start Offset (SPSO)</b> and an in-flight window up to <code>share.partition.max.record.locks</code> (2000) records. Everything below SPSO is done.</li>
        <li>State is persisted by the <b>share coordinator</b> in the internal topic <code>__share_group_state</code>, so it survives broker failover.</li>
        <li>Where a share group starts reading is <code>share.auto.offset.reset</code> (latest by default; we set earliest with kafka-configs on the group). Ordering is not guaranteed, and a retried record may be processed after newer ones.</li>
      </ul>
/LEVELS
'''
SM = figure('State machine of a record in a share group: Available goes to Acquired when fetched; Acquired goes to Acknowledged on accept, back to Available on release or lock timeout, and to Archived on reject or when the delivery count reaches the limit of 5.',
    box(20, 50, 110, 36, 'blue', rx=6) + t(75, 72, 'Available', 8.4, bold=True) +
    box(200, 50, 110, 36, 'acc', rx=6) + t(255, 72, 'Acquired (lock)', 8.4, bold=True) +
    box(400, 14, 130, 36, 'green', rx=6) + t(465, 36, 'Acknowledged', 8.4, bold=True) +
    box(400, 90, 130, 36, 'red', rx=6) + t(465, 112, 'Archived', 8.4, bold=True) +
    arrow(132, 62, 198, 62) + t(165, 56, 'fetch', 7) + arrow(198, 78, 132, 78) + t(165, 98, 'release / 30 s', 7) +
    arrow(312, 60, 398, 34) + t(350, 38, 'accept', 7) + arrow(312, 76, 398, 106) + t(350, 116, 'reject / count=5', 7),
    h=140, caption='Every delivery adds 1 to the record’s delivery count.')
extra = '''

  <h3>Life of one record</h3>
''' + SM

types_html = table(['', 'Consumer group', 'Share group'], [
    ['Unit of assignment', 'whole partition', 'individual records'], ['Max useful consumers', '= partitions', 'more than partitions'],
    ['Ordering', 'per partition', 'none guaranteed'], ['Progress', 'committed offset', 'SPSO + per-record state'],
    ['Failure of one record', 'blocks partition (or you skip)', 'release / reject, delivery count'],
    ['Replay', 'reset offsets', 'reset SPSO (kafka-share-groups --reset-offsets)'], ['Use', 'event streams, ordered processing', 'work queues'],
], minw=620) + table(['Setting', 'Default', 'Meaning'], [
    ['share.record.lock.duration.ms', '30000', 'how long a consumer holds a record'], ['share.delivery.count.limit', '5', 'deliveries before archive'],
    ['share.partition.max.record.locks', '2000', 'in-flight window per partition'], ['share.auto.offset.reset', 'latest', 'start position of a new group'],
    ['share.acknowledgement.mode (client)', 'implicit', 'or explicit'],
], minw=600)
warn = 'Share groups do not keep order. If “order 7 cancelled” must be processed after “order 7 placed”, use a normal consumer group keyed by order id. Also, a record that is released forever is silently archived after 5 deliveries: log it or route it to a DLQ (Lesson 6.2) before rejecting.'

steps = [
    ('Step 1 · A topic with only 2 partitions',
     code('bash', 'terminal', 'kafka-topics.sh --bootstrap-server k1:9092 --create --topic jobs-61 --partitions 2 --replication-factor 3\nkafka-configs.sh --bootstrap-server k1:9092 --entity-type groups --entity-name kitchen-61 --alter --add-config share.auto.offset.reset=earliest\nseq 1 3000 | sed "s/^/job-/" | kafka-console-producer.sh --bootstrap-server k1:9092 --topic jobs-61', sec('== 1)', '== 2)')),
     'The group config makes the new share group start from the beginning.'),
    ('Step 2 · Three share consumers',
     code('bash', 'terminal', 'for c in A B C; do kafka-console-share-consumer.sh --bootstrap-server k1:9092 --topic jobs-61 --group kitchen-61 --timeout-ms 10000 > chef_$c.txt & done; wait', sec('== 2)', '== 3)')),
     'Two chefs shared the work and 3,000 records were delivered with <b>3,000 unique</b>: no duplicates. Chef C got nothing: the console consumer fetches big batches, and A and B had locked everything before C joined. With slower, real processing (or smaller <code>max.poll.records</code>), work spreads across all members.'),
    ('Step 3 · Describe',
     code('bash', 'terminal', 'kafka-share-groups.sh --bootstrap-server k1:9092 --describe --group kitchen-61', sec('== 3)', '== 4)')),
     'START-OFFSET is the SPSO per partition and LAG 0 means nothing left. There is no “current offset per consumer” as in a consumer group.'),
    ('Step 4 · Reject',
     code('bash', 'terminal', 'kafka-console-share-consumer.sh … --topic small-61 --group rej2-61 --reject\nkafka-console-share-consumer.sh … --topic small-61 --group rej2-61', sec('== 4)', '== 5)')),
     'Rejected records are archived immediately; a second pass gets nothing.'),
    ('Step 5 · Release until the limit',
     code('bash', 'terminal', 'kafka-configs.sh … --entity-type groups --entity-name rel2-61 --describe --all | grep -E "delivery|lock"\nkafka-console-share-consumer.sh … --topic small-61 --group rel2-61 --release   # 3 runs', sec('== 5)')),
     'With 12 records and <code>--release</code>, one run received <b>60 = 12 × 5</b>: each record was redelivered until the delivery count reached 5, then archived. (The first run joined the new group too late for its 5 s timeout.) This is Kafka’s built-in poison-message protection.'),
]
see = [term([('jobs-61 P0, P1', W), ('3000 jobs', G)], size=7.4), term([('chef A 2117', G), ('chef B 883', G), ('unique 3000', G)], size=7.4),
       term([('P0 START 0 LAG 0', W), ('P1 START 1093 LAG 0', W)], size=7.2), term([('rejected 12', RD), ('second pass 0', W)], size=7.4),
       term([('release run: 60', Y), ('= 12 x 5, archived', W)], size=7.4)]
B1 = [chefs([(str(i), 'blue') for i in range(1, 9)]), chefs([('1', 'acc'), ('2', 'acc'), ('3', 'violet'), ('4', 'violet'), ('5', 'acc'), ('6', 'violet'), ('7', 'blue'), ('8', 'blue')]),
      chefs([(str(i), 'green') for i in range(1, 9)]), chefs([(str(i), 'red') for i in range(1, 9)]), chefs([('1', 'amber'), ('2', 'amber'), ('3', 'amber'), ('4', 'red'), ('5', 'red'), ('6', 'red'), ('7', 'red'), ('8', 'red')])]
B1 = [b + cap(c, '', tn, y=134, h=30) for b, c, tn in zip(B1, ['All available', 'Locked by A (orange) and B (violet)', 'All acknowledged', 'Rejected → archived', 'Released 5× → archived'], ['blue', 'amber', 'green', 'red', 'red'])]
two = anim_two('Share groups', 'Share, describe, reject, release', 'Real outputs from the lab', 'Record states', see, B1, ['Load.', 'Share.', 'Describe.', 'Reject.', 'Release.'], ['Available.', 'Locked.', 'Done.', 'Archived.', 'Limit 5.'])
pe = peel('One record, layer by layer', 'job-42 in share group kitchen-61. (Simplified.)',
    [('Fetch', ''), ('Lock', ''), ('Process', ''), ('Acknowledge', ''), ('Persist', ''), ('Advance', '')],
    [['Fetch', 'ShareFetch request', 'from chef A', ''], ['Lock', 'state Acquired', 'owner A, 30 s', 'delivery count 1'],
     ['Process', 'chef cooks', 'ok or failure', ''], ['Acknowledge', 'ACCEPT / RELEASE / REJECT', 'ShareAcknowledge', ''],
     ['Persist', 'share coordinator', '__share_group_state', 'survives failover'], ['Advance', 'all below done?', 'SPSO moves forward', 'window slides']],
    ['Fetch.', 'Lock.', 'Cook.', 'Ack.', 'Persist.', 'Advance.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Diwali rush', 'More workers than partitions. (Typical.)', ('Share group', 'Scale workers beyond partitions'), [
    ('2 partitions, 10 workers', 'consumer group', '8 idle.', 'red'), ('Switch to share group', 'same topic', 'No repartition.', 'green'),
    ('10 workers busy', 'records locked individually', 'Throughput up.', 'green'), ('Rush ends', 'scale to 2 workers', 'Elastic.', 'blue'),
    ('No duplicates', 'locks + acks', 'Correct.', 'blue')], ['Idle.', 'Switch.', 'Busy.', 'Shrink.', 'Safe.'], 'scenario-rush') + \
       five('Real-time scenario 2', 'Worker crashes mid-job', 'Lock timeout. (Typical.)', ('Record lock', 'Unacked records come back'), [
    ('Chef B holds 50 jobs', 'locks 30 s', 'Working.', 'blue'), ('Chef B pod killed', 'no acknowledgements', 'Crash.', 'red'),
    ('30 s later', 'locks expire', 'Available again.', 'amber'), ('Chef A gets them', 'delivery count 2', 'Retry.', 'green'),
    ('Idempotent cooking', 'dedupe by job id', 'At-least-once.', 'blue')], ['Hold.', 'Crash.', 'Expire.', 'Redeliver.', 'Dedupe.'], 'scenario-crash') + \
       five('Real-time scenario 3 · advanced', 'Poison message', 'Crashes the worker every time. (Typical.)', ('Delivery count limit', 'Archive after 5 tries'), [
    ('Bad image job', 'worker crashes', 'Lock expires.', 'red'), ('Redelivered', 'count 2, 3, 4', 'Crashes again.', 'red'),
    ('Count = 5', 'archived', 'Queue moves on.', 'green'), ('Better: catch error', 'send to DLQ, then REJECT', 'Visible.', 'green'),
    ('Alert on DLQ', 'fix and replay', 'Lesson 6.2.', 'blue')], ['Crash.', 'Repeat.', 'Archive.', 'DLQ.', 'Fix.'], 'scenario-poison')
assemble(HERE, h2_story='More workers than partitions', hook_html=hk,
    narration='TiffinGo’s Diwali rush: the cooking-jobs topic has 2 partitions but the kitchen has 10 workers. Kabir asks whether Kafka can behave like a simple job queue.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Share groups (Queues for Kafka)',
    formal='A <b>share group</b> (KIP-932) is a set of consumers that cooperatively consume records from topics without exclusive partition assignment. The broker delivers records in batches under an <b>acquisition lock</b>; each record is acknowledged by the consumer as accepted, released or rejected. The broker tracks per-record <b>delivery counts</b> and a share-partition start offset, persisted by the share coordinator, giving at-least-once, unordered, queue-like consumption.',
    simple='A share group lets many consumers pull jobs from the same partitions. Each job is locked to one worker until it says done, try again, or give up. Like a queue, but built into Kafka.',
    term_rows=[('Share group', 'Queue-style consumer group.'), ('Acquired', 'Locked to one consumer.'), ('Lock duration', '30 s default.'), ('ACCEPT', 'Done.'), ('RELEASE', 'Give back for retry.'), ('REJECT', 'Unprocessable: archive.'), ('Delivery count', 'Times delivered; limit 5.'), ('SPSO', 'Share-partition start offset.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Kafka cannot be a queue.', 'Share groups (4.x) are queues in Kafka.', 'Step 2.'),
               ('More consumers than partitions sit idle.', 'Not in a share group.', 'Scenario 1.'),
               ('A failing record retries forever.', 'Archived at delivery count 5.', 'Step 5: 60 = 12×5.')],
    exam='“Share group vs consumer group?” Share group: records (not partitions) distributed, per-record locks and acks (accept/release/reject), delivery count limit, no ordering, consumers can exceed partitions. Consumer group: exclusive partitions, ordered, committed offsets.',
    types_h2='Consumer group vs share group', types_html=types_html, warn=warn,
    steps_h2='Share, reject, release', steps_intro='All outputs are real: Kafka 4.4.0 (share.version 2), 3 brokers, console share consumer.',
    steps=steps, two=two, peel_intro='Now peel one record.', peel_html=pe,
    scen_intro='Three live scenarios: a rush, a crashed worker, and a poison message.', scen=scen,
    uc_h2='Share groups at work', ucs=[uc_('jobs', 'queue', 'blue', '1. Background jobs', 'Emails, PDFs, thumbnails.', ['Jobs', '*share group', 'Workers']),
        uc_('ml', 'inference', 'violet', '2. ML inference', 'GPU workers scale independently.', ['Requests', '*share', 'GPUs']),
        uc_('notif', 'notify', 'green', '3. Notifications', 'Order not needed, speed is.', ['Events', '*share', 'SMS/push']),
        uc_('mq', 'replace', 'amber', '4. Replacing a side queue', 'One platform instead of Kafka + RabbitMQ.', ['Kafka', '*queue too', 'Simpler'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../../03-consumers/01-consumers-and-consumer-groups/">3.1 Consumer groups</a>.')
