import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='12-capstone', lesson='02-build-the-pipeline', n='12.2', module_label='Module 12 · Capstone',
    title='Capstone: build the pipeline',
    desc='Capstone part 2: building the TiffinGo order pipeline end to end on Kafka 4.4: topics, an idempotent Avro producer with Schema Registry, an exactly-once Python processor with a compacted menu and a dead letter queue, a Kafka Connect sink with read_committed, and reconciliation. Real result: 1,841 enriched + 1,159 DLQ = 3,000 orders, lag 0, 1,841 lines in the sink.',
    og_desc='3,000 orders in, 1,841 + 1,159 out, lag 0: an end-to-end exactly-once Kafka pipeline.',
    minutes=28, level='Advanced',
    lead='Can we build the whole design and prove every order is accounted for? We create the <b>topics</b>, <b>produce</b> Avro orders, run an <b>exactly-once</b> processor with a <b>DLQ</b>, add a <b>Connect sink</b>, and <b>reconcile</b>. <b>All outputs are real.</b>',
    chips=['1841 + 1159 = 3000', 'Lag 0', 'EOS + DLQ + sink', 'Runs in your browser (Python)'])
MAIN = '''# The processor logic, without Kafka (route each order exactly once)
menu = {"idli": 45, "dosa": 90, "thali": 150, "vada": 60, "lassi": 45}
orders = [{"id": 1, "city": "Delhi", "item": "idli", "qty": 1},
          {"id": 2, "city": "Pune", "item": "pizza", "qty": 1},
          {"id": 3, "city": "Mumbai", "item": "dosa", "qty": 0},
          {"id": 4, "city": "Pune", "item": "thali", "qty": 2}]
enriched, dlq = [], []
for o in orders:
    reason = "qty must be > 0" if o["qty"] <= 0 else ("unknown item" if o["item"] not in menu else None)
    if reason:
        dlq.append((o["id"], reason))
    else:
        enriched.append({**o, "amount": o["qty"] * menu[o["item"]]})
print("enriched", enriched)
print("dlq", dlq)
print("reconciles:", len(enriched) + len(dlq) == len(orders))
'''
RUN = dict(heading='Run the code: route and reconcile', intro='<p>The processor’s rules. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    reason = "qty must be > 0" if o["qty"] <= 0 else ("unknown item" if o["item"] not in menu else None)', 'Same reasons as the lab DLQ.'), ('print("reconciles:", len(enriched) + len(dlq) == len(orders))', 'The check that matters.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Add pizza to the menu.', code=None),
        dict(label='2 · Predict first: lab sum', hint='<b>Predict first:</b> 1,841 + 1,159.', code='print(1841 + 1159)\n'),
        dict(label='3 · DLQ share', hint='1,159 of 3,000.', code='print(round(1159 / 3000 * 100, 1), "%")\n'),
        dict(label='4 · Markers', hint='Offsets vs records.', code='print(1849 - 1841, "commit markers")\n'),
        dict(label='5 · Spot the error', hint='Same transactional.id twice.', expect='error', code='raise RuntimeError("ProducerFencedException: there is a newer producer with the same transactional.id")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: the pipeline', intro='<p>Needs the lab cluster, Schema Registry (sr) and Connect (kc). <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Start services', cmd='docker start k1 k2 k3 sr kc', file='terminal', output='', note='From Modules 7–8.'),
           dict(title='2 · Run', cmd='python3 l122.py', file='terminal', output='== 3) processor (transactions, read_committed): 1841 enriched + 1159 to DLQ = 3000 in 9.9 s', note='About 40 s total.'),
           dict(title='3 · Check the sink', cmd='wc -l ~/lab/kafka/connect/data/cap-enriched.txt', file='terminal', output='1841', note='Matches.')])
TRACE = dict(heading='One order step by step', intro='<p>Check, price, route.</p>',
    code='o = {"item": "idli", "qty": 1}\nprice = {"idli": 45}[o["item"]]\nprint(o["qty"] * price)\n', notes={2: 'Menu :: Latest compacted value.', 3: 'Amount :: 45.'})
WORKED_INTRO = 'Three build decisions.'
EXAMPLES = [
    dict(level='b', tag='Build · producer', title='Safe producer', problem='<p>No duplicates on retry.</p>', inp='config',
         approach=['acks=all.', 'enable.idempotence=true.', 'Avro serializer.'], code='print({"acks": "all", "enable.idempotence": True})\n', notes={1: 'Lesson 2.5.'}, tryit='Step 2.'),
    dict(level='i', tag='Build · EOS', title='Transaction loop', problem='<p>Exactly once into two topics.</p>', inp='steps',
         approach=['begin.', 'produce outputs.', 'send_offsets_to_transaction.', 'commit.'], code='print(["begin", "produce", "send_offsets", "commit"])\n', notes={1: 'Atomic.'}, tryit='Step 3.'),
    dict(level='a', tag='Build · sink', title='Sink isolation', problem='<p>Sink must not see aborted data.</p>', inp='config',
         approach=['consumer.override.isolation.level.', 'read_committed.', 'Allowed by worker policy.'], code='print({"consumer.override.isolation.level": "read_committed"})\n', notes={1: 'Clean.'}, tryit='Issue 1.')]
QUIZ = mix([
    dict(q='Beginner: Orders produced in the lab…', options=['1,841', '3,000', '1,159', '6,000'], answer=1, why='Step 2.'),
    dict(q='Beginner: Bad orders went to…', options=['Enriched', 'DLQ', 'Menu', 'Deleted'], answer=1, why='1,159.'),
    dict(q='Beginner: The sink file had…', options=['3,000 lines', '1,841 lines', '0', '1,159'], answer=1, why='= enriched.'),
    dict(q='Intermediate: idli price used was…', options=['40', '45', '90', '0'], answer=1, why='Compacted latest.'),
    dict(q='Intermediate: Offsets are committed…', options=['Auto every 5 s', 'Inside the transaction', 'Never', 'By the sink'], answer=1, why='EOS.'),
    dict(q='Intermediate: Enriched end offsets 1,849 vs 1,841 records because…', options=['Bug', 'Transaction markers', 'Duplicates', 'Compaction'], answer=1, why='Markers.'),
    dict(q='Advanced: Two processor instances need…', options=['Same transactional.id', 'Different transactional.ids', 'No ids', 'acks=0'], answer=1, why='Fencing.'),
    dict(q='Advanced: DLQ reasons came from…', options=['Topic names', 'x-error headers', 'Keys', 'Offsets'], answer=1, why='Grouped.')])
REVISION = ['Topics per plan; menu compacted; producer acks=all + idempotence + Avro.', 'Processor: read_committed, transactions, offsets in tx, DLQ with headers.',
    'Lab: 3,000 → 1,841 enriched + 1,159 DLQ (764 qty, 395 unknown); lag 0.', 'Connect sink read_committed: 1,841 lines.', 'Count records, not offsets, on transactional topics.']
FAQ = [('Why Python and not Java?', 'To keep the transaction steps visible; the same pattern works in any client with transactions.'),
    ('How do I scale the processor?', 'Run more instances in the same group with unique transactional.ids, or move to Kafka Streams EOS v2.'),
    ('Where are revenue numbers stored?', 'Here only printed; a Kafka Streams KTable or a windowed aggregation (Module 9) would store them.'),
    ('How do I replay the DLQ?', 'Fix the cause, then re-publish chosen DLQ records to cap-orders (Lesson 6.2).')]
PRACTICE_INTRO = 'Pipeline programs.'
PROBLEMS = [
    dict(level='easy', title='Sum', stmt='Reconcile.', inp='ints', code='print(1841 + 1159 == 3000)\n', explain='True.'),
    dict(level='easy', title='Amount', stmt='2 thali × 150.', inp='ints', code='print(2 * 150)\n', explain='300.'),
    dict(level='easy', title='Latest price', stmt='Compacted log.', inp='list', code='print(dict([("idli", 40), ("idli", 45)])["idli"])\n', explain='45.'),
    dict(level='medium', title='Reasons', stmt='Group DLQ.', inp='list', code='from collections import Counter\nprint(Counter(["qty", "unknown", "qty"]))\n', explain='Counts.'),
    dict(level='medium', title='Revenue', stmt='Sum by city.', inp='list', code='r = {}\nfor c, a in [("Pune", 90), ("Pune", 300), ("Delhi", 45)]: r[c] = r.get(c, 0) + a\nprint(r)\n', explain='Per city.'),
    dict(level='medium', title='Unique', stmt='Duplicates?', inp='list', code='ids = [1, 2, 3, 3]\nprint(len(ids) - len(set(ids)))\n', explain='1.'),
    dict(level='business', title='DLQ alert', stmt='Rate above 5%?', inp='floats', code='print(1159 / 3000 > 0.05)\n', explain='Yes: fix upstream.'),
    dict(level='business', title='Throughput', stmt='3,000 in 9.9 s.', inp='floats', code='print(round(3000 / 9.9), "orders/s")\n', explain='~303.')]
SCN_INTRO = 'Build interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“Walk me through your pipeline.”', 'Explain.', 'answer?', '<p>Avro orders with an idempotent producer; a transactional processor reads committed data, enriches from a compacted menu, writes enriched or DLQ and commits offsets in the same transaction; Connect copies enriched data out; counts reconcile.</p>', '“It reads and writes.”') +
    scn('Data', 'Mid-level', 'Counts off by 8', 'Offsets vs records.', 'why?', '<ul><li>Transaction markers take offsets.</li><li>Count with a reader.</li></ul>', 'Data loss.') +
    scn('Data', 'Mid-level', 'Sink duplicates', 'After processor retries.', 'fix?', '<ul><li>read_committed in the sink.</li></ul>', 'Delete the file.') +
    scn('Platform', 'Senior', 'Scale 10×', 'Processor CPU bound.', 'plan?', '<ul><li>More instances, unique transactional ids.</li><li>Or Streams/Flink with state stores.</li></ul>', 'Bigger VM only.'))
