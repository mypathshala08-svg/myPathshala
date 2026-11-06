import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
BODY = body(HERE)
META = dict(module='02-producers', lesson='05-idempotent-producer-and-retries', n='2.5', module_label='Module 2 · Producers',
    title='Idempotent producer and retries',
    desc='How Kafka retries create duplicates and how the idempotent producer prevents them with a producer id, epoch and per-partition sequence numbers. Real Kafka 4.4 lab: a frozen follower delays acks=all, the producer retries, and one payment is stored three times with idempotence off but once with it on, proven with kafka-dump-log. Plus ordering with in-flight requests, retry backoff and what idempotence cannot cover.',
    og_desc='We made Kafka store one payment three times, then fixed it with idempotence: PID and sequence numbers proven on disk.',
    minutes=26, level='Intermediate',
    lead='Retries keep data safe but can <b>duplicate</b> it. We create a real duplicate on a Kafka 4.4 cluster, read the <b>producer id and sequence numbers</b> on disk, and prevent it with the <b>idempotent producer</b>. <b>All outputs are real.</b>',
    chips=['Real duplicate created', 'PID + sequence on disk', 'Limits explained', 'Runs in your browser (Python)'])
MAIN = '''# A leader that deduplicates by (producer id, sequence)
log, seen = [], {}            # seen[(pid, partition)] = last sequence written

def append(pid, seq, value, idempotent=True):
    if idempotent and seen.get(pid, -1) >= seq:
        return f"duplicate seq {seq}: not stored again"
    log.append(value)
    if idempotent:
        seen[pid] = seq
    return f"stored at offset {len(log) - 1}"

for attempt in range(3):                       # first try + 2 retries
    print("idempotent off:", append(None, -1, "t045", idempotent=False))
log.clear()
for attempt in range(3):
    print("idempotent on :", append(7001, 0, "t045"))
print("copies stored:", log.count("t045"))
'''
RUN = dict(heading='Run the code: dedup by sequence', intro='<p>The leader’s check in a few lines. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    if idempotent and seen.get(pid, -1) >= seq:', 'Already have this producer’s sequence? Then it is a retry.'), ('for attempt in range(3):                       # first try + 2 retries', 'Same record sent three times, like our lab.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Then send seq 1 after seq 0.', code=None),
        dict(label='2 · Predict first: restart', hint='<b>Predict first:</b> app restarts with PID 7002 and re-sends seq 0. Stored again?', code='seen = {7001: 0}\nprint("stored again:", seen.get(7002, -1) < 0)\n'),
        dict(label='3 · Gap', hint='Sequence jumps from 0 to 2.', code='last, got = 0, 2\nprint("OUT_OF_ORDER_SEQUENCE" if got > last + 1 else "ok")\n'),
        dict(label='4 · Backoff', hint='Exponential backoff 100 ms doubling, max 1000.', code='b = 100\nfor i in range(6):\n    print(min(b, 1000)); b *= 2\n'),
        dict(label='5 · Spot the error', hint='Conflicting config.', expect='error', code='conf = {"enable.idempotence": True, "acks": "1"}\nif conf["enable.idempotence"] and conf["acks"] != "all":\n    raise ValueError("ConfigException: idempotence requires acks=all")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: see PID and sequence', intro='<p>Produce with defaults, then dump the log. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Produce', cmd='python l25_dup.py idem-on on', file='terminal', output='enable.idempotence=True: delivered after 9 s -> [\'offset 0\']', note='Pause a follower first to force retries.'),
           dict(title='2 · Dump', cmd='kafka-dump-log.sh --files /var/lib/kafka/data/idem-on-0/00000000000000000000.log', file='terminal', output='baseOffset: 0 … baseSequence: 0 lastSequence: 0 producerId: 7001 producerEpoch: 0', note='Proof.'),
           dict(title='3 · Java config', cmd='props.put("enable.idempotence", "true"); props.put("acks", "all");', file='Java', output='(defaults since Kafka 3.0)', note='Explicit is clearer.')])
TRACE = dict(heading='Retry with a sequence', intro='<p>Second attempt is recognised.</p>',
    code='stored = {}\nfor attempt in (1, 2):\n    key = (7001, 0)\n    if key in stored:\n        print("attempt", attempt, "duplicate")\n    else:\n        stored[key] = "t045"\n        print("attempt", attempt, "stored")\n',
    notes={4: 'Check :: PID + sequence already present?', 7: 'First :: Stored once.'})
WORKED_INTRO = 'Three duplicate-prevention decisions.'
EXAMPLES = [
    dict(level='b', tag='Idempotence · config', title='Audit producer configs', problem='<p>Find services that disabled idempotence.</p>', inp='configs',
         approach=['Search for enable.idempotence=false.', 'Search acks=1/0 on critical topics.', 'Fix.'], code='configs = {"pay": {"enable.idempotence": False}, "orders": {}}\nprint([s for s, c in configs.items() if c.get("enable.idempotence") is False])\n', notes={1: 'Audit :: Old overrides cause dupes.'}, tryit='Scenario 1.'),
    dict(level='i', tag='Idempotence · consumer', title='Dedup by business key', problem='<p>Restarts may re-send payments.</p>', inp='txn ids',
         approach=['Every event carries txn_id.', 'Consumer keeps processed ids.', 'Skip repeats.'], code='done = set()\nfor txn in ["t045", "t046", "t045"]:\n    if txn in done: print("skip", txn); continue\n    done.add(txn); print("process", txn)\n', notes={1: 'End to end :: Covers what idempotence misses.'}, tryit='Scenario 2.'),
    dict(level='a', tag='Idempotence · transactions', title='When to use transactional.id', problem='<p>Read payments, write alerts, commit offsets atomically.</p>', inp='pipeline',
         approach=['Set transactional.id (stable per instance).', 'begin, produce, send offsets, commit.', 'Consumers use read_committed.'], code='steps = ["init_transactions", "begin_transaction", "produce(alert)", "send_offsets_to_transaction", "commit_transaction"]\nprint(" -> ".join(steps))\n', notes={1: 'EOS :: Lesson 3.5 in depth.'}, tryit='Types table.')]
QUIZ = mix([
    dict(q='Beginner: Why can retries duplicate records?', options=['Kafka bug', 'The first write succeeded but its response was lost/late', 'Compression', 'Partitions'], answer=1, why='Step 1.'),
    dict(q='Beginner: Idempotence default since Kafka 3.0 is…', options=['false', 'true', 'only in Java', 'removed'], answer=1, why='With acks=all.'),
    dict(q='Beginner: With idempotence on, our payment was stored…', options=['3 times', 'once', 'never', 'twice'], answer=1, why='Step 3.'),
    dict(q='Intermediate: The broker detects duplicates using…', options=['Message value', 'Producer id + sequence number', 'Timestamp', 'Key'], answer=1, why='PID 7001, seq 0.'),
    dict(q='Intermediate: Idempotence requires…', options=['acks=0', 'acks=all and in-flight ≤ 5', 'one partition', 'compression'], answer=1, why='Rules.'),
    dict(q='Intermediate: dump-log showed producerId -1 because…', options=['Error', 'Idempotence was off', 'acks=0', 'Old Kafka'], answer=1, why='No PID.'),
    dict(q='Advanced: A producer restart then re-send is…', options=['Deduplicated', 'Not deduplicated (new PID)', 'Rejected', 'Reordered'], answer=1, why='Use transactions/business keys.'),
    dict(q='Advanced: Without idempotence, in-flight > 1 with retries can cause…', options=['Reordering', 'Compression', 'Faster acks', 'Nothing'], answer=0, why='Batch 2 before batch 1.')])
REVISION = ['Retries + lost/late response = duplicates (lab: offsets 0, 1, 2).', 'Idempotence: PID + epoch + per-partition sequence; leader skips seen sequences.',
    'Lab: producerId 7001, baseSequence 0, one copy.', 'Needs acks=all, retries, in-flight ≤ 5; default since 3.0; keeps order on retry.',
    'Not covered: producer restarts, app double-sends, consumer re-processing → transactions / business-key dedup.', 'Backoff 100 ms → 1 s; stop at delivery timeout.']
FAQ = [('Does idempotence slow the producer?', 'Very little; the extra fields are a few bytes per batch and the broker check is cheap. It is on by default for that reason.'),
    ('How long does the broker remember a producer id?', 'Until producer state expires (transactional.id.expiration.ms / producer.id.expiration.ms, about a day by default) if the producer stays idle.'),
    ('Is idempotence per topic?', 'Per producer session and per partition: sequences are tracked separately for each partition the producer writes.'),
    ('What is a zombie producer?', 'An old instance (e.g. after a network split) that keeps writing. Transactions bump the epoch so the broker rejects the zombie.')]
PRACTICE_INTRO = 'Retry and dedup programs.'
PROBLEMS = [
    dict(level='easy', title='Count copies', stmt='Copies of t045 in a log.', inp='log', code='print(["t045", "t045", "t045"].count("t045"))\n', explain='3 without idempotence.'),
    dict(level='easy', title='Retries in deadline', stmt='Attempts in 120 s with 30 s timeout.', inp='numbers', code='print(120 // 30)\n', explain='About 4.'),
    dict(level='easy', title='Sequence next', stmt='Next sequence after 41.', inp='41', code='print(41 + 1)\n', explain='42.'),
    dict(level='medium', title='Dedup set', stmt='Keep first occurrence only.', inp='list', code='seen, out = set(), []\nfor x in ["a", "b", "a", "c", "b"]:\n    if x not in seen: seen.add(x); out.append(x)\nprint(out)\n', explain='Consumer-side dedup.'),
    dict(level='medium', title='Backoff total', stmt='Total wait for 5 retries with doubling from 100 ms, max 1000.', inp='numbers', code='print(sum(min(100 * 2 ** i, 1000) for i in range(5)))\n', explain='1,500 ms.'),
    dict(level='medium', title='Gap check', stmt='Detect sequence gaps.', inp='[0,1,3]', code='s = [0, 1, 3]\nprint([b for a, b in zip(s, s[1:]) if b != a + 1])\n', explain='Gap at 3.'),
    dict(level='business', title='Refund cost', stmt='0.1% of 1,00,000 payments duplicated × Rs 500.', inp='numbers', code='print("Rs", int(100000 * 0.001 * 500))\n', explain='Rs 50,000 in refunds.'),
    dict(level='business', title='Throughput impact', stmt='Idempotence overhead ~1% on 37k/s.', inp='37133', code='print(round(37133 * 0.99))\n', explain='Negligible.')]
SCN_INTRO = 'Idempotence interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“What is an idempotent producer?”', 'Explain.', 'answer?', '<p>A producer whose retries cannot create duplicates: the broker assigns a producer id and the producer numbers batches per partition; the leader ignores a batch whose sequence it already wrote. Default since Kafka 3.0.</p>', '“It uses unique message ids generated by the app.”') +
    scn('Fintech', 'Mid-level', 'Duplicates', 'Duplicate payments appear during network issues.', 'diagnose?', '<ul><li>Check enable.idempotence and acks.</li><li>dump-log: producerId -1 means off.</li><li>Fix config; add business-key dedup.</li></ul>', 'Setting retries=0.') +
    scn('Data engineering', 'Mid-level', 'Restarts', 'Duplicates appear after producer restarts.', 'explain?', '<ul><li>New PID after restart.</li><li>Idempotence is per session.</li><li>Transactions or consumer dedup.</li></ul>', '“Idempotence is broken.”') +
    scn('Platform', 'Senior', 'Exactly-once', 'Design exactly-once from payments to alerts.', 'design?', '<ul><li>Idempotent producer + transactional.id.</li><li>Offsets committed in the transaction.</li><li>read_committed consumers; idempotent sinks.</li></ul>', '“Kafka is exactly-once by default.”'))
