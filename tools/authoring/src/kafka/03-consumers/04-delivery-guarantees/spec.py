import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
BODY = body(HERE)
META = dict(module='03-consumers', lesson='04-delivery-guarantees', n='3.4', module_label='Module 3 · Consumers',
    title='Delivery guarantees',
    desc='At-most-once, at-least-once and exactly-once in Kafka, proven by crashing a consumer. Real Kafka 4.4 lab: 50 invoices, a hard crash after 25; committing before processing lost invoices 26 to 30, committing after processing sent 21 to 25 twice. Plus idempotent processing, idempotency keys, offsets stored with results, and what Kafka exactly-once covers.',
    og_desc='Crash a Kafka consumer two ways: 5 invoices lost or 5 sent twice. Delivery guarantees, measured.',
    minutes=24, level='Intermediate',
    lead='“At-least-once” and “exactly-once” are interview favourites. We <b>crash a real billing worker</b> after 25 of 50 invoices and count what was <b>lost</b> or <b>sent twice</b>, then show how real systems get “once”. <b>All outputs are real.</b>',
    chips=['5 lost vs 5 doubled', 'Commit order matters', 'Idempotent sinks', 'Runs in your browser (Python)'])
MAIN = '''# Simulate the crash: commit before vs after processing
def run(mode, n=50, batch=10, crash_after=25):
    sent, committed, done = [], 0, 0
    for attempt in range(2):                     # first run crashes, second continues
        pos = committed
        while pos < n:
            batch_ids = list(range(pos + 1, min(pos + batch, n) + 1))
            if mode == "atmost": committed = batch_ids[-1]
            crashed = False
            for i in batch_ids:
                sent.append(i); done += 1
                if attempt == 0 and done == crash_after: crashed = True; break
            if crashed: break
            if mode == "atleast": committed = batch_ids[-1]
            pos = batch_ids[-1]
    lost = sorted(set(range(1, n + 1)) - set(sent))
    twice = sorted(i for i in set(sent) if sent.count(i) > 1)
    return len(sent), lost, twice

for mode in ("atmost", "atleast"):
    total, lost, twice = run(mode)
    print(mode, "sent:", total, "lost:", lost, "twice:", twice)
'''
RUN = dict(heading='Run the code: crash simulation', intro='<p>The same experiment as the lab, in pure Python. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('            if mode == "atmost": committed = batch_ids[-1]', 'Commit first: a crash skips the rest of this batch.'), ('            if mode == "atleast": committed = batch_ids[-1]', 'Commit last: a crash repeats this batch.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Then change batch to 5.', code=None),
        dict(label='2 · Predict first: duplicates', hint='<b>Predict first:</b> batch 10, crash after 25, commit after. How many twice?', code='print(25 - 20)\n'),
        dict(label='3 · Idempotent sink', hint='Dedup by invoice id.', code='db = set()\nfor inv in [21, 22, 21, 23, 22]:\n    db.add(inv)\nprint(sorted(db))\n'),
        dict(label='4 · Smaller batches', hint='Duplicates with batch 1 (commit per record).', code='print(25 - 24, "(only the record in flight)")\n'),
        dict(label='5 · Spot the error', hint='Commit before work.', expect='error', code='committed, processed = 30, 25\nif committed > processed:\n    raise RuntimeError(f"records {processed + 1}-{committed} committed but never processed: data loss")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: crash test', intro='<p>Scripts from the lab folder. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Run both modes', cmd='python l34_run.py', file='terminal', output='at-most-once: processed 45 unique 45 missing 5\nat-least-once: processed 55 unique 50 missing 0 processed twice 5', note='Bootstrap k1:9092 → your broker.'),
           dict(title='2 · Inspect the log', cmd='sort /tmp/inv-atleast.log | uniq -d', file='terminal', output='invoice-21\ninvoice-22\ninvoice-23\ninvoice-24\ninvoice-25', note='The duplicates.')])
TRACE = dict(heading='Where the crash lands', intro='<p>Commit after work.</p>',
    code='committed = 20\nsent = list(range(1, 26))\ncrash = True\nresume = committed + 1\nresent = list(range(resume, 26))\nprint("resent:", resent)\n',
    notes={4: 'Resume :: From the last commit.', 5: 'Repeat :: 21–25 again.'})
WORKED_INTRO = 'Three designs for “once”.'
EXAMPLES = [
    dict(level='b', tag='Guarantee · choose', title='Pick per use case', problem='<p>Metrics, invoices, Kafka-to-Kafka enrichment.</p>', inp='use cases',
         approach=['Metrics: at-most-once.', 'Invoices: at-least-once + dedup.', 'Enrichment: transactions.'], code='print({"metrics": "at-most-once", "invoices": "at-least-once + dedup", "enrich": "exactly-once (tx)"})\n', notes={1: 'Fit :: Cost vs risk.'}, tryit='Types table.'),
    dict(level='i', tag='Guarantee · sink', title='Upsert by id', problem='<p>Replays must not double-bill.</p>', inp='invoice ids',
         approach=['Primary key = invoice_id.', 'INSERT … ON CONFLICT DO NOTHING.', 'Commit after the batch.'], code='print("INSERT INTO invoices(id, amount) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING")\n', notes={1: 'Idempotent :: Repeats are harmless.'}, tryit='Peel animation.'),
    dict(level='a', tag='Guarantee · atomic', title='Offsets in the same DB transaction', problem='<p>Exactly-once into PostgreSQL.</p>', inp='DB',
         approach=['BEGIN; insert results; update offsets table; COMMIT.', 'On start: read offsets, seek.', 'Disable Kafka commits.'], code='steps = ["BEGIN", "INSERT results", "UPSERT offsets(topic, partition, next)", "COMMIT"]\nprint(" ; ".join(steps))\n', notes={1: 'Atomic :: Both or neither.'}, tryit='Scenario 3.')]
QUIZ = mix([
    dict(q='Beginner: Commit before processing gives…', options=['At-least-once', 'At-most-once', 'Exactly-once', 'Nothing'], answer=1, why='May lose.'),
    dict(q='Beginner: Process then commit gives…', options=['At-most-once', 'At-least-once', 'Exactly-once', 'Loss'], answer=1, why='May repeat.'),
    dict(q='Beginner: In our at-least-once run, how many invoices were sent twice?', options=['0', '5', '25', '50'], answer=1, why='21–25.'),
    dict(q='Intermediate: Duplicates in at-least-once equal…', options=['All records', 'Work done since the last commit', 'Random', 'One batch always'], answer=1, why='Uncommitted work.'),
    dict(q='Intermediate: Best common practice for payments:', options=['At-most-once', 'At-least-once + idempotent writes', 'No commits', 'acks=0'], answer=1, why='No loss, harmless repeats.'),
    dict(q='Intermediate: Smaller commit intervals mean…', options=['More loss', 'Fewer re-processed records, more commit overhead', 'Nothing', 'Exactly-once'], answer=1, why='Trade-off.'),
    dict(q='Advanced: Kafka exactly-once guarantees cover…', options=['External SMS calls', 'Kafka outputs and offsets in a transaction', 'Everything', 'Only producers'], answer=1, why='Not side effects.'),
    dict(q='Advanced: Exactly-once into a database is achieved by…', options=['acks=all', 'Storing offsets with results atomically or idempotent upserts', 'More partitions', 'Compression'], answer=1, why='Scenario 3.')])
REVISION = ['At-most-once: commit → process (lab: 5 lost, 26–30).', 'At-least-once: process → commit (lab: 5 twice, 21–25).', 'Duplicates = work since last commit; loss = committed but unprocessed.',
    'Effectively once: at-least-once + idempotent processing (ids, upserts, idempotency keys).', 'Exactly-once in Kafka: idempotent producer + transactions + read_committed (3.5).', 'External side effects need their own idempotency.']
FAQ = [('Which guarantee does auto-commit give?', 'Usually at-least-once, because it commits positions already returned by poll at the next poll. With async processing it can become at-most-once.'),
    ('Is exactly-once slower?', 'Transactions add some latency (commit markers, coordinator round trips), typically small at reasonable batch sizes.'),
    ('Does Spark give exactly-once with Kafka?', 'Spark Structured Streaming achieves end-to-end exactly-once with replayable sources, checkpoints and idempotent/transactional sinks.'),
    ('Can a consumer get duplicates even with an idempotent producer?', 'Yes: producer idempotence prevents duplicate writes, not repeated reads after a consumer crash.')]
PRACTICE_INTRO = 'Delivery guarantee programs.'
PROBLEMS = [
    dict(level='easy', title='Lost', stmt='Committed 30, processed 25.', inp='numbers', code='print(30 - 25)\n', explain='5 lost.'),
    dict(level='easy', title='Twice', stmt='Committed 20, processed 25.', inp='numbers', code='print(25 - 20)\n', explain='5 twice.'),
    dict(level='easy', title='Unique', stmt='Count unique sends.', inp='list', code='print(len(set([1, 2, 2, 3])))\n', explain='3.'),
    dict(level='medium', title='Dedup', stmt='Keep first occurrence.', inp='list', code='seen = set(); out = []\nfor x in [21, 22, 21, 23]:\n    if x not in seen: seen.add(x); out.append(x)\nprint(out)\n', explain='Idempotent consumer.'),
    dict(level='medium', title='Window', stmt='Max duplicates with commit every 100 records.', inp='100', code='print(100 - 1)\n', explain='Up to 99.'),
    dict(level='medium', title='Classify', stmt='Commit order → guarantee.', inp='order', code='order = ["process", "commit"]\nprint("at-least-once" if order[0] == "process" else "at-most-once")\n', explain='Rule.'),
    dict(level='business', title='Refund cost', stmt='5 duplicate invoices × Rs 300.', inp='numbers', code='print("Rs", 5 * 300)\n', explain='Per crash, without dedup.'),
    dict(level='business', title='Lost revenue', stmt='5 lost invoices × Rs 300 × 10 crashes/month.', inp='numbers', code='print("Rs", 5 * 300 * 10)\n', explain='Why not at-most-once.')]
SCN_INTRO = 'Delivery semantics interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“at-least-once vs at-most-once?”', 'Explain with commits.', 'answer?', '<p>At-most-once commits before processing, so a crash skips records. At-least-once commits after processing, so a crash repeats records. Most systems use at-least-once with idempotent processing.</p>', '“Kafka decides it automatically.”') +
    scn('Fintech', 'Mid-level', 'Duplicate invoices', 'Customers get duplicate invoices after crashes.', 'fix?', '<ul><li>Expected with at-least-once.</li><li>Idempotent sink keyed by invoice_id.</li><li>Commit smaller batches.</li></ul>', 'Switching to at-most-once.') +
    scn('Data engineering', 'Mid-level', 'Exactly-once claim', 'A vendor says “exactly-once SMS with Kafka”.', 'evaluate?', '<ul><li>Kafka EOS covers Kafka writes and offsets.</li><li>SMS needs an idempotency key or dedup store.</li></ul>', 'Accepting the claim.') +
    scn('Platform', 'Senior', 'Ledger pipeline', 'Design exactly-once from Kafka to a PostgreSQL ledger.', 'design?', '<ul><li>Offsets stored in the same DB transaction.</li><li>seek() on start.</li><li>Or upserts by entry id.</li></ul>', 'Relying on auto-commit.'))
