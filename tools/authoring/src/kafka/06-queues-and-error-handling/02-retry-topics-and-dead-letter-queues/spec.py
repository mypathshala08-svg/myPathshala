import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='06-queues-and-error-handling', lesson='02-retry-topics-and-dead-letter-queues', n='6.2', module_label='Module 6 · Queues and error handling',
    title='Retry topics and dead letter queues',
    desc='Non-blocking error handling for Kafka consumers: poison messages and head-of-line blocking, transient versus permanent errors, retry-topic ladders with backoff, dead letter queues with diagnostic headers, ordering trade-offs, replay, and built-in DLQs in Kafka Connect and Spring Kafka. Real Kafka 4.4 lab with Python: 8 orders, 6 processed, 2 parked in the DLQ with full context.',
    og_desc='Retry ladder 5 s → 30 s → DLQ on Kafka 4.4: one bad order never blocks the kitchen.',
    minutes=22, level='Intermediate',
    lead='How do you stop one bad record from blocking a partition? We build a <b>retry ladder</b> and a <b>dead letter queue</b> in Python and push 8 orders through. <b>All outputs are real.</b>',
    chips=['8 orders, 2 in DLQ', 'Headers tell the story', 'Transient vs permanent', 'Runs in your browser (Python)'])
MAIN = '''# Route failures: retry ladder vs dead letter queue
NEXT = {"orders": "retry-5s", "retry-5s": "retry-30s", "retry-30s": "dlq"}

def route(topic, error):
    if error is None:
        return "commit"
    if error in ("JSONDecodeError", "ValidationError"):
        return "dlq"                    # permanent: retrying will not help
    return NEXT[topic]                  # transient: next rung

print(route("orders", None))
print(route("orders", "JSONDecodeError"))
print(route("orders", "503"))
print(route("retry-30s", "503"))
'''
RUN = dict(heading='Run the code: the router', intro='<p>The routing rule. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('        return "dlq"                    # permanent: retrying will not help', 'Permanent → DLQ immediately.'), ('    return NEXT[topic]                  # transient: next rung', 'Transient → climb the ladder.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Add a retry-5m rung.', code=None),
        dict(label='2 · Predict first: attempts', hint='<b>Predict first:</b> attempts for main + 2 retry rungs.', code='print(1 + 2)\n'),
        dict(label='3 · Backoff', hint='Exponential delays.', code='print([5 * 6 ** i for i in range(3)])\n'),
        dict(label='4 · Headers', hint='Build DLQ headers.', code='print({"x-error": "503", "x-attempt": 4, "x-original-topic": "orders", "x-original-offset": 6})\n'),
        dict(label='5 · Spot the error', hint='Unhandled bad JSON crashes the loop.', expect='error', code='import json\njson.loads("{id: 3, kind: bad")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: the ladder', intro='<p>Needs the lab and confluent-kafka. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Run', cmd='python3 l62.py', file='terminal', output='+ 3.2s orders-62  key 3 Permanent (JSONDecodeError) -> orders-62-dlq\n+ 5.3s orders-62-retry-5s  order 5 OK (attempt 2)', note='Full log above.'),
           dict(title='2 · Peek at DLQ', cmd='kafka-console-consumer.sh --bootstrap-server k1:9092 --topic orders-62-dlq --from-beginning --property print.headers=true', file='terminal', output='x-attempt:4,x-error:Transient: payment gateway 503,…', note='Headers visible.'),
           dict(title='3 · Replay', cmd='kafka-console-consumer.sh … --topic orders-62-dlq --from-beginning --max-messages 2 | kafka-console-producer.sh … --topic orders-62', file='terminal', output='', note='After the fix (naive: drops headers/keys).')])
TRACE = dict(heading='Order 7 step by step', intro='<p>Climb, then park.</p>',
    code='topic = "orders"\nfor step in range(3):\n    topic = {"orders": "retry-5s", "retry-5s": "retry-30s", "retry-30s": "dlq"}[topic]\n    print(step + 2, topic)\n',
    notes={3: 'Next rung :: Header x-attempt +1.', 4: 'Ends in dlq :: Attempt 4.'})
WORKED_INTRO = 'Three error-handling decisions.'
EXAMPLES = [
    dict(level='b', tag='DLQ · classify', title='Which errors retry?', problem='<p>List of errors from a consumer.</p>', inp='errors',
         approach=['Network/5xx/429: transient.', 'Parse/validation: permanent.', 'Unknown: retry then DLQ.'], code='errs = ["503", "JSONDecodeError", "429"]\nprint({e: ("dlq" if "Error" in e else "retry") for e in errs})\n', notes={1: 'Rule :: Retry only what can change.'}, tryit='Types table.'),
    dict(level='i', tag='DLQ · Connect', title='DLQ for a sink connector', problem='<p>Bad rows crash a JDBC sink.</p>', inp='config',
         approach=['errors.tolerance=all.', 'errors.deadletterqueue.topic.name.', 'context headers on.'], code='print({"errors.tolerance": "all", "errors.deadletterqueue.topic.name": "dlq-jdbc", "errors.deadletterqueue.context.headers.enable": "true"})\n', notes={1: 'Module 7 :: Connect.'}, tryit='Use case 3.'),
    dict(level='a', tag='DLQ · order', title='Keep per-key order', problem='<p>Cancellations overtake retried placements.</p>', inp='design',
         approach=['Track keys with pending retries.', 'Route later records of that key to retry too.', 'Clear when resolved.'], code='pending = {"order-9"}\nkey = "order-9"\nprint("retry" if key in pending else "process")\n', notes={1: 'Park :: Order kept per key.'}, tryit='Scenario 3.')]
QUIZ = mix([
    dict(q='Beginner: A DLQ stores…', options=['Fast records', 'Records that could not be processed', 'Offsets', 'Schemas'], answer=1, why='Parking.'),
    dict(q='Beginner: Bad JSON is…', options=['Transient', 'Permanent', 'Ignored by Kafka', 'A rebalance'], answer=1, why='Never fixes itself.'),
    dict(q='Beginner: Head-of-line blocking means…', options=['Leader slow', 'One failing record stops those behind it', 'Too many partitions', 'Compression'], answer=1, why='Per-partition offsets.'),
    dict(q='Intermediate: In our lab, order 5 succeeded on…', options=['Attempt 1', 'Attempt 2 (retry-5s)', 'DLQ', 'Never'], answer=1, why='Flaky.'),
    dict(q='Intermediate: Order 7 reached the DLQ with x-attempt…', options=['1', '2', '4', '10'], answer=2, why='1 + 3 hops.'),
    dict(q='Intermediate: Why keep the original key in retry records?', options=['Compression', 'Same partitioning and dedupe', 'Required by Kafka', 'Speed'], answer=1, why='Consistency.'),
    dict(q='Advanced: Non-blocking retries can break…', options=['Durability', 'Per-key ordering', 'Compression', 'Replication'], answer=1, why='Retried record is late.'),
    dict(q='Advanced: Connect DLQ needs…', options=['errors.tolerance=all', 'acks=0', 'unclean election', 'compaction'], answer=0, why='Plus DLQ topic name.')])
REVISION = ['Classify: transient → retry ladder; permanent → DLQ immediately.', 'Headers: attempt, error, original topic/partition/offset, retry-at.',
    'Lab: 8 orders → 5 OK, order 5 OK on retry, orders 3 and 7 in DLQ; main topic done in 0.1 s.', 'Commit original offset after producing aside; idempotent processing.', 'Ordering trade-off; monitor + replay DLQ; Connect and Spring have built-ins.']
FAQ = [('How many retry topics?', 'Commonly 2–4 with growing delays (seconds to minutes). More rungs add latency and operational load.'),
    ('Why not sleep in the main consumer?', 'Short sleeps are fine for blips; long ones block the partition and can exceed max.poll.interval.ms, causing a rebalance.'),
    ('Should DLQs have retention?', 'Long enough for people to act (days to weeks), and alert on growth.'),
    ('Does Kafka have a native DLQ?', 'Not for consumer groups; Connect and frameworks provide one, and share groups archive after the delivery limit.')]
PRACTICE_INTRO = 'Error-handling programs.'
PROBLEMS = [
    dict(level='easy', title='Classify', stmt='Is 429 transient?', inp='str', code='print("429" in ["429", "503", "timeout"])\n', explain='Yes.'),
    dict(level='easy', title='Next rung', stmt='After retry-5s.', inp='dict', code='print({"retry-5s": "retry-30s"}["retry-5s"])\n', explain='retry-30s.'),
    dict(level='easy', title='Attempt', stmt='Attempt after 2 hops.', inp='int', code='print(1 + 2)\n', explain='3.'),
    dict(level='medium', title='Due?', stmt='retry_at 100, now 98.', inp='ints', code='print(98 >= 100)\n', explain='Not yet.'),
    dict(level='medium', title='Headers', stmt='Build header list.', inp='values', code='h = [("x-attempt", "2"), ("x-error", "503")]\nprint(dict(h))\n', explain='Dict view.'),
    dict(level='medium', title='Safe parse', stmt='Catch bad JSON.', inp='str', code='import json\ntry:\n    json.loads("{bad")\nexcept json.JSONDecodeError as e:\n    print("dlq:", type(e).__name__)\n', explain='No crash.'),
    dict(level='business', title='Account', stmt='Check every order accounted.', inp='ints', code='ok, dlq, total = 6, 2, 8\nprint(ok + dlq == total)\n', explain='True.'),
    dict(level='business', title='Retry delay total', stmt='Delays 5, 30, 300 s.', inp='list', code='print(sum([5, 30, 300]), "s worst case")\n', explain='335 s.')]
SCN_INTRO = 'Error-handling interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“What is a dead letter queue?”', 'Explain.', 'answer?', '<p>A topic where records that cannot be processed are parked with error details, so the main flow continues and people can fix and replay them later.</p>', '“Where deleted records go.”') +
    scn('E-commerce', 'Mid-level', 'Stuck consumer', 'Lag grows behind one record.', 'fix?', '<ul><li>Catch, classify, send aside, commit.</li><li>Retry topics + DLQ.</li></ul>', 'Restart the consumer.') +
    scn('Platform', 'Mid-level', 'DLQ overflowing', '10k records/day.', 'do?', '<ul><li>Group by x-error.</li><li>Fix root cause, replay, alert.</li></ul>', 'Delete the DLQ.') +
    scn('Fintech', 'Senior', 'Exactly once', 'Duplicate retry records after crash.', 'fix?', '<ul><li>Transactional produce + offset commit.</li><li>Or idempotent handler keyed by id.</li></ul>', 'Disable retries.'))
