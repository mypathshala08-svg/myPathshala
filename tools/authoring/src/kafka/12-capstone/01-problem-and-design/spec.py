import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='12-capstone', lesson='01-problem-and-design', n='12.1', module_label='Module 12 · Capstone',
    title='Capstone: problem and design',
    desc='Capstone part 1: turning TiffinGo’s order-processing requirements into a Kafka design: partitions and keys, replication and durability, exactly-once processing, dead letter queue, compacted reference data, Avro schemas, Connect sink and monitoring, with a decision table linking every choice to its lesson and three design reviews.',
    og_desc='From eight requirements to a complete Kafka design, every decision linked to a lesson.',
    minutes=20, level='Advanced',
    lead='How do you design a real Kafka pipeline? We turn <b>requirements into numbers</b>, numbers into <b>decisions</b>, and decisions into a <b>topic plan</b>. <b>Lab outputs are real.</b>',
    chips=['8 requirements', '4 topics', 'Every choice → a lesson', 'Runs in your browser (Python)'])
MAIN = '''# Requirements -> decisions (the capstone rules)
import math
req = {"peak_per_s": 2000, "kb": 0.5, "consumers": 6, "must_not_lose": True, "no_double": True, "bad_pct": 5}
mb = req["peak_per_s"] * req["kb"] / 1024
design = {
    "partitions": max(math.ceil(mb / 5), req["consumers"]),
    "replication": "RF 3, min ISR 2, acks=all, idempotence" if req["must_not_lose"] else "RF 2",
    "processing": "transactions + read_committed" if req["no_double"] else "at-least-once + idempotent sink",
    "errors": "DLQ" if req["bad_pct"] > 0 else "none",
}
for k, v in design.items(): print(f"{k:12s} {v}")
'''
RUN = dict(heading='Run the code: derive a design', intro='<p>Each decision from one requirement. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    "partitions": max(math.ceil(mb / 5), req["consumers"]),', 'Parallelism decides here.'), ('    "processing": "transactions + read_committed" if req["no_double"] else "at-least-once + idempotent sink",', 'Lesson 3.5.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Set consumers to 12.', code=None),
        dict(label='2 · Predict first: MB/s', hint='<b>Predict first:</b> 2,000 × 0.5 KB.', code='print(round(2000 * 0.5 / 1024, 2))\n'),
        dict(label='3 · Key', hint='Order per city → key?', code='print("city")\n'),
        dict(label='4 · Tolerated failures', hint='RF 3, min ISR 2.', code='print(3 - 2)\n'),
        dict(label='5 · Spot the error', hint='Too few partitions for consumers.', expect='error', code='partitions, consumers = 3, 6\nif consumers > partitions:\n    raise ValueError("3 consumers would sit idle: partitions < consumers")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: the design script', intro='<p>Plain Python. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Run', cmd='python3 l121.py', file='terminal', output='  cap-orders: 6 partitions (peak 0.98 MB/s, 6 consumers), key = city (order per city)', note='Full output above.')])
TRACE = dict(heading='One decision step by step', intro='<p>Requirement → setting.</p>',
    code='must_not_lose = True\nacks = "all" if must_not_lose else "1"\nprint(acks)\n', notes={2: 'Durability :: Lesson 2.4.'})
WORKED_INTRO = 'Three design decisions.'
EXAMPLES = [
    dict(level='b', tag='Design · key', title='Choose the key', problem='<p>Order per city needed.</p>', inp='need',
         approach=['Key = city.', 'Same partition per city.', 'Watch skew.'], code='print("key = city")\n', notes={1: 'Ordering :: Per key.'}, tryit='Review 1.'),
    dict(level='i', tag='Design · durability', title='Never lose an order', problem='<p>One broker may fail.</p>', inp='config',
         approach=['RF 3.', 'min ISR 2.', 'acks=all + idempotence.'], code='print({"rf": 3, "min.insync.replicas": 2, "acks": "all"})\n', notes={1: 'Lessons :: 2.4, 5.2.'}, tryit='Decision table.'),
    dict(level='a', tag='Design · EOS', title='No double billing', problem='<p>Processor may crash.</p>', inp='pattern',
         approach=['Transactional producer.', 'Offsets in transaction.', 'read_committed readers.'], code='print("consume-transform-produce with transactions")\n', notes={1: 'Proved :: 12.3.'}, tryit='12.2.')]
QUIZ = mix([
    dict(q='Beginner: Partitions chosen for the capstone…', options=['1', '6', '24', '100'], answer=1, why='6 consumers.'),
    dict(q='Beginner: The key is…', options=['order id', 'city', 'random', 'none'], answer=1, why='Order per city.'),
    dict(q='Beginner: Bad orders go to…', options=['Nowhere', 'A DLQ topic', 'The menu', 'Logs only'], answer=1, why='Lesson 6.2.'),
    dict(q='Intermediate: Prices come from…', options=['A REST call', 'A compacted topic', 'Hard-coded', 'The DLQ'], answer=1, why='Decoupled.'),
    dict(q='Intermediate: No double counting needs…', options=['acks=0', 'Transactions + read_committed', 'More partitions', 'Compression'], answer=1, why='EOS.'),
    dict(q='Intermediate: Throughput alone needed about…', options=['1 partition', '24', '12', '60'], answer=0, why='< 1 MB/s.'),
    dict(q='Advanced: A hot city suggests…', options=['Ignore', 'Re-check the ordering requirement and key', 'Delete data', 'RF 1'], answer=1, why='Review 1.'),
    dict(q='Advanced: Schema changes should be…', options=['Unchecked', 'BACKWARD with defaults', 'NONE', 'Manual only'], answer=1, why='Lesson 8.2.')])
REVISION = ['Requirements as numbers; one decision per requirement.', 'Partitions 6 (consumers), key city, RF 3 / min ISR 2 / acks=all / idempotence.',
    'EOS processing, DLQ with reasons, compacted menu, Avro + registry, Connect sink, lag SLO.', 'Topic plan: cap-orders 6, menu compact, enriched, DLQ.', 'Reviews: hot key, menu outage, schema change.']
FAQ = [('Why not Kafka Streams for the processor?', 'You can; we used plain clients to show the transaction steps clearly. Streams with exactly_once_v2 is a good next step.'),
    ('Why 3 partitions for enriched?', 'Lower volume after filtering and only analytics reads it; sized from need.'),
    ('Where is security?', 'Add Lesson 10.3 (SASL_SSL, ACLs per app) before production.'),
    ('Can I run it in Colab?', 'Yes, with a local Kafka as in Lesson 1.6; Connect and the registry need Docker or the jar files.')]
PRACTICE_INTRO = 'Design programs.'
PROBLEMS = [
    dict(level='easy', title='MB/s', stmt='5,000/s × 1 KB.', inp='ints', code='print(round(5000 / 1024, 2))\n', explain='~4.9.'),
    dict(level='easy', title='Partitions', stmt='max(1, 8).', inp='ints', code='print(max(1, 8))\n', explain='8.'),
    dict(level='easy', title='Failures', stmt='RF 5, min ISR 3.', inp='ints', code='print(5 - 3)\n', explain='2.'),
    dict(level='medium', title='Derive', stmt='Pick processing mode.', inp='bool', code='no_double = False\nprint("EOS" if no_double else "at-least-once + idempotent sink")\n', explain='Cheaper.'),
    dict(level='medium', title='Topic plan', stmt='Print plan.', inp='list', code='for t, p in [("orders", 6), ("dlq", 3)]: print(t, p)\n', explain='Plan.'),
    dict(level='medium', title='Skew', stmt='Share of hottest key.', inp='dict', code='c = {"Mumbai": 700, "Pune": 200, "Delhi": 100}\nprint(max(c.values()) / sum(c.values()))\n', explain='0.7.'),
    dict(level='business', title='Storage', stmt='1 MB/s, 7 days, RF 3.', inp='ints', code='print(round(1 * 86400 * 7 * 3 / 1024 / 1024, 2), "TB")\n', explain='~1.7.'),
    dict(level='business', title='DLQ volume', stmt='5% of 2,000/s per hour.', inp='ints', code='print(int(2000 * 0.05 * 3600))\n', explain='360,000.')]
SCN_INTRO = 'Design interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“How do you choose partitions and keys?”', 'Explain.', 'answer?', '<p>Keys come from ordering needs (same key, same partition). Partitions from throughput per partition and how many consumers must work in parallel, plus growth.</p>', '“Always 100.”') +
    scn('E-commerce', 'Mid-level', 'Lookup data', 'Prices needed per order.', 'design?', '<ul><li>Compacted topic → local table (KTable/GlobalKTable).</li></ul>', 'Call the API per order.') +
    scn('Fintech', 'Mid-level', 'No duplicates', 'Billing events.', 'design?', '<ul><li>Idempotent producer, transactions, read_committed.</li><li>Idempotent sinks.</li></ul>', 'Hope.') +
    scn('Architecture', 'Senior', 'Review a design', 'Checklist.', 'what?', '<ul><li>“What happens when…” for each failure.</li><li>Evidence for each claim.</li></ul>', 'Approve on slides.'))
