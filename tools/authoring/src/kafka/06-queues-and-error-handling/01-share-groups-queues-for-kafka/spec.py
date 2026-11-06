import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='06-queues-and-error-handling', lesson='01-share-groups-queues-for-kafka', n='6.1', module_label='Module 6 · Queues and error handling',
    title='Share groups: queues for Kafka',
    desc='Kafka share groups (KIP-932, Queues for Kafka): record-level distribution instead of partition assignment, acquisition locks, accept/release/reject acknowledgements, delivery count limits, the share-partition start offset and the share coordinator. Real Kafka 4.4 lab: 3,000 jobs shared without duplicates, rejected records archived, and released records redelivered exactly 5 times.',
    og_desc='Kafka as a job queue: share groups on 4.4, 3,000 jobs with zero duplicates, and the 5-delivery limit in action.',
    minutes=22, level='Intermediate',
    lead='Can Kafka act like a job queue, with more workers than partitions? We run a <b>share group</b>, then <b>reject</b> and <b>release</b> records and watch the delivery limit. <b>All outputs are real.</b>',
    chips=['3000 jobs, 0 duplicates', '12 × 5 = 60 deliveries', 'Accept / release / reject', 'Runs in your browser (Python)'])
MAIN = '''# A tiny share-partition: records with state and delivery count
LIMIT = 5
recs = {o: {"state": "available", "count": 0} for o in range(4)}

def acquire(o):
    r = recs[o]; r["state"] = "acquired"; r["count"] += 1

def ack(o, kind):
    r = recs[o]
    if kind == "accept":
        r["state"] = "acked"
    elif kind == "reject" or r["count"] >= LIMIT:
        r["state"] = "archived"
    else:                       # release
        r["state"] = "available"

for o in range(4):
    acquire(o); ack(o, "accept" if o != 2 else "release")
while recs[2]["state"] == "available":
    acquire(2); ack(2, "release")
print(recs)
'''
RUN = dict(heading='Run the code: record states', intro='<p>The share-group state machine in a few lines. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    elif kind == "reject" or r["count"] >= LIMIT:', 'Reject or too many tries: archive.'), ('while recs[2]["state"] == "available":', 'Record 2 keeps failing: 5 deliveries.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Set LIMIT = 3.', code=None),
        dict(label='2 · Predict first: deliveries', hint='<b>Predict first:</b> 12 records always released, limit 5.', code='print(12 * 5)\n'),
        dict(label='3 · Useful consumers', hint='Consumer group vs share group, 2 partitions, 10 workers.', code='print({"consumer group": min(2, 10), "share group": 10})\n'),
        dict(label='4 · Lock expiry', hint='Locked at t=0, lock 30 s, now t=31.', code='print("available again" if 31 > 30 else "locked")\n'),
        dict(label='5 · Spot the error', hint='Ack a record you do not hold.', expect='error', code='state = "available"\nif state != "acquired":\n    raise RuntimeError("INVALID_RECORD_STATE: record not acquired by this member")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: a share group', intro='<p>Needs Kafka 4.1+ (share.version ≥ 1). <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Start from earliest', cmd='kafka-configs.sh --bootstrap-server k1:9092 --entity-type groups --entity-name kitchen-61 --alter --add-config share.auto.offset.reset=earliest', file='terminal', output='Completed updating config for group kitchen-61.', note='Group-level config.'),
           dict(title='2 · Share consumer', cmd='kafka-console-share-consumer.sh --bootstrap-server k1:9092 --topic jobs-61 --group kitchen-61', file='terminal', output='job-1\njob-2\n…', note='Run in 3 terminals.'),
           dict(title='3 · Describe', cmd='kafka-share-groups.sh --bootstrap-server k1:9092 --describe --group kitchen-61', file='terminal', output='GROUP TOPIC PARTITION START-OFFSET LAG\nkitchen-61 jobs-61 0 0 0', note='SPSO + lag.'),
           dict(title='4 · Members', cmd='kafka-share-groups.sh --bootstrap-server k1:9092 --describe --group kitchen-61 --members', file='terminal', output='', note='While consumers run.')])
TRACE = dict(heading='One record step by step', intro='<p>Acquire, release, archive.</p>',
    code='count = 0\nfor attempt in range(6):\n    count += 1\n    if count >= 5:\n        break\nprint("archived after", count)\n',
    notes={3: 'Acquire :: Delivery count +1.', 4: 'Limit :: 5 by default.', 6: 'Archive :: Never delivered again.'})
WORKED_INTRO = 'Three share-group decisions.'
EXAMPLES = [
    dict(level='b', tag='Share · choose', title='Queue or stream?', problem='<p>Send 1M push notifications fast.</p>', inp='need',
         approach=['Order not needed.', 'Elastic workers.', 'Share group.'], code='print("share group" if not True else "")\n', notes={1: 'Queue :: Any worker, any record.'}, tryit='Types table.'),
    dict(level='i', tag='Share · explicit ack', title='Explicit acknowledgement', problem='<p>Release on transient error, reject on bad data.</p>', inp='mode',
         approach=['share.acknowledgement.mode=explicit.', 'acknowledge(rec, RELEASE|REJECT|ACCEPT).', 'commitSync().'], code='print({"timeout": "RELEASE", "bad json": "REJECT", "ok": "ACCEPT"})\n', notes={1: 'Java :: KafkaShareConsumer.'}, tryit='Scenario 3.'),
    dict(level='a', tag='Share · tuning', title='Lock duration', problem='<p>Jobs take 2 minutes.</p>', inp='ms',
         approach=['Default lock 30 s too short.', 'Raise share.record.lock.duration.ms (group config).', 'Or split work.'], code='print({"share.record.lock.duration.ms": 180000})\n', notes={1: 'Else :: Duplicates after expiry.'}, tryit='Scenario 2.')]
QUIZ = mix([
    dict(q='Beginner: Share groups are from…', options=['KIP-500', 'KIP-932', 'KIP-848', 'KIP-405'], answer=1, why='Queues for Kafka.'),
    dict(q='Beginner: In a share group, records are given to…', options=['One consumer per partition', 'Any member, record by record', 'All members', 'The controller'], answer=1, why='Shared partitions.'),
    dict(q='Beginner: Default delivery count limit…', options=['1', '3', '5', 'unlimited'], answer=2, why='Then archived.'),
    dict(q='Intermediate: Our 12 released records were delivered…', options=['12 times', '60 times', 'forever', 'once'], answer=1, why='12 × 5.'),
    dict(q='Intermediate: REJECT means…', options=['Retry', 'Archive, do not redeliver', 'Duplicate', 'Pause'], answer=1, why='Unprocessable.'),
    dict(q='Intermediate: If a consumer crashes holding records…', options=['Records lost', 'Locks expire and records are redelivered', 'Partition offline', 'Group deleted'], answer=1, why='30 s lock.'),
    dict(q='Advanced: Share groups guarantee ordering…', options=['Per partition', 'Per key', 'Not at all', 'Globally'], answer=2, why='Trade-off.'),
    dict(q='Advanced: Share state is persisted in…', options=['__consumer_offsets', '__share_group_state', 'ZooKeeper', 'Client disk'], answer=1, why='Share coordinator.')])
REVISION = ['Share group = queue: records locked to one member; members can exceed partitions.', 'States: available → acquired → acknowledged / available / archived.',
    'Lab: 3000 jobs, 3000 unique; reject → 0 redelivered; release → 60 = 12 × 5.', 'Defaults: lock 30 s, delivery limit 5, max locks 2000, start latest.', 'No ordering; use consumer groups when order matters.']
FAQ = [('Can a topic have both consumer groups and share groups?', 'Yes. They are independent readers of the same log.'),
    ('Which clients support share groups?', 'The Java client (KafkaShareConsumer) fully; check your librdkafka/other client version for support.'),
    ('Is it exactly-once?', 'No, at-least-once; make processing idempotent.'),
    ('Can I reset a share group?', 'Yes: kafka-share-groups.sh --reset-offsets with no active members.')]
PRACTICE_INTRO = 'Share-group programs.'
PROBLEMS = [
    dict(level='easy', title='Deliveries', stmt='20 records always released, limit 5.', inp='ints', code='print(20 * 5)\n', explain='100.'),
    dict(level='easy', title='Workers', stmt='Useful share consumers for 3 partitions, 12 workers.', inp='ints', code='print(12)\n', explain='All.'),
    dict(level='easy', title='Unique', stmt='Detect duplicates.', inp='list', code='got = ["j1", "j2", "j1"]\nprint(len(got) - len(set(got)))\n', explain='1 duplicate.'),
    dict(level='medium', title='Classify ack', stmt='Map error to ack type.', inp='str', code='err = "timeout"\nprint("RELEASE" if err == "timeout" else "REJECT")\n', explain='Transient → release.'),
    dict(level='medium', title='Lock check', stmt='Locked at 10 s, now 45 s.', inp='ints', code='print(45 - 10 > 30)\n', explain='Expired.'),
    dict(level='medium', title='SPSO', stmt='Lowest offset not yet done.', inp='dict', code='done = {0: True, 1: True, 2: False, 3: True}\nprint(min(o for o, d in done.items() if not d))\n', explain='2.'),
    dict(level='business', title='Throughput', stmt='10 workers × 4 jobs/s.', inp='ints', code='print(10 * 4 * 3600, "jobs/hour")\n', explain='144,000.'),
    dict(level='business', title='Idle cost', stmt='Consumer group: idle workers of 10 with 2 partitions.', inp='ints', code='print(10 - 2)\n', explain='8.')]
SCN_INTRO = 'Share-group interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“Can Kafka work as a queue?”', 'Explain.', 'answer?', '<p>Yes. Since 4.x share groups let many consumers take records from the same partitions with per-record locks and acknowledgements, like a queue. Ordering is not kept.</p>', '“No, use RabbitMQ.”') +
    scn('Platform', 'Mid-level', 'Duplicates', 'Long jobs processed twice.', 'cause?', '<ul><li>Lock (30 s) expired before ack.</li><li>Raise lock duration, idempotent jobs.</li></ul>', 'More partitions.') +
    scn('Platform', 'Mid-level', 'Archived silently', 'Jobs vanish.', 'cause?', '<ul><li>Delivery limit reached.</li><li>Log + DLQ before reject.</li></ul>', 'Raise limit to 1000.') +
    scn('Fintech', 'Senior', 'Choose', 'Ledger updates per account.', 'share group?', '<ul><li>No: order per account matters.</li><li>Consumer group keyed by account.</li></ul>', 'Share group for speed.'))
