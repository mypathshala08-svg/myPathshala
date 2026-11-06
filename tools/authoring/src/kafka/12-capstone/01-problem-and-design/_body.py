import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l121_design.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('Eight business requirements. How many Kafka decisions hide inside them, and which lesson answers each one?',
    'About a dozen: partitions, keys, replication, acks, idempotence, transactions, retention, compaction, error handling, schemas, sinks and monitoring. In this capstone we turn TiffinGo’s requirements into a <b>design</b>, then build it (12.2) and attack it (12.3). Every decision links back to the lesson that taught it.',
    ['How to turn requirements into topics, keys and configs.',
     'The capstone architecture end to end.',
     'Why each choice, and what you would change at 100× scale.'])
cmap = concept_map('Concept map of the capstone: requirements lead to topic design (partitions, keys), durability (RF, min ISR, acks, idempotence), processing (transactions, DLQ), data contracts (Schema Registry), integration (Connect) and operations (monitoring, security, DR).',
    [[('rq', 'Requirements', 'TiffinGo', None), ('td', 'Topic design', '1.4, 10.2', B + '10-kafka-in-production/02-performance-tuning-and-partition-sizing/')],
     [('du', 'Durability', '2.4, 5.2', B + '02-producers/04-acks-and-durability/'), ('pr', 'Exactly-once processing', '3.5', B + '03-consumers/05-transactions-and-exactly-once/'), ('er', 'Errors + DLQ', '6.2', B + '06-queues-and-error-handling/02-retry-topics-and-dead-letter-queues/'), ('sc', 'Schemas', '8.1', B + '08-schemas/01-schema-registry/')],
     [('cn', 'Connect sink', '7.1', B + '07-kafka-connect/01-kafka-connect/'), ('cp', 'Compacted menu', '4.3', B + '04-storage-internals/03-retention-and-compaction/'), ('mo', 'Monitoring', '10.1', B + '10-kafka-in-production/01-monitoring-and-consumer-lag/'), ('bu', 'Build it', '12.2', B + '12-capstone/02-build-the-pipeline/')]],
    [('rq', 'td'), ('rq', 'du'), ('td', 'pr'), ('du', 'pr'), ('pr', 'er'), ('td', 'sc'), ('pr', 'cn'), ('pr', 'cp'), ('cn', 'mo'), ('mo', 'bu')],
    {'rq', 'td', 'du', 'pr', 'er', 'sc', 'cn', 'cp', 'mo'},
    '<b>Uses:</b> the whole course. <b>Next:</b> <a href="../02-build-the-pipeline/">12.2 Build the pipeline</a>.')
whw = why_how_where(
    'Real projects fail on design, not syntax: wrong keys break ordering, too few partitions cap scale, a missing DLQ stops everything, a missing contract breaks consumers. Writing decisions down before coding prevents that.',
    'List requirements with numbers, derive each Kafka setting from one requirement, write it as a topic plan and a data-flow diagram, and name the lesson or test that proves it.',
    'Every new pipeline, architecture review and system-design interview (“design an order processing system with Kafka”).',
    'A design is a hypothesis: 12.2 builds it and 12.3 breaks it to check every claim.')

def arch(hl=-1):
    parts = [('app', 'orders (Avro)', 'card'), ('cap-orders', '6 p · key city', 'blue'), ('processor', 'EOS + menu', 'violet'), ('enriched', 'Connect → file', 'green')]
    o = ''
    for k, (n, d, tn) in enumerate(parts):
        o += box(6 + k * 88, 36, 80, 50, 'acc' if k == hl else tn, rx=6) + t(46 + k * 88, 56, n, 7.6, bold=True) + t(46 + k * 88, 74, d, 6.2)
        if k < 3: o += arrow(86 + k * 88, 61, 94 + k * 88, 61)
    o += box(182, 98, 80, 26, 'red' if hl != 4 else 'acc', rx=5) + t(222, 115, 'DLQ', 7.6, bold=True) + arrow(222, 86, 222, 98)
    o += box(96, 98, 80, 26, 'amber', rx=5) + t(136, 115, 'cap-menu', 7.2, bold=True) + arrow(176, 111, 182, 100)
    return o + t(180, 22, 'TiffinGo order pipeline', 7.6)
scene_svg = scene('Capstone architecture: the app produces Avro orders to cap-orders (6 partitions, key city); an exactly-once processor enriches them with prices from the compacted cap-menu topic and writes cap-orders-enriched or the DLQ; Kafka Connect writes enriched orders to a file sink.', arch(),
                  'One flow, every lesson: <tspan font-weight="700" class="s-acc">produce → process → sink</tspan>, with a DLQ.')
dialogue = '''K> Sir, the CTO wants the new order pipeline on Kafka by next month. Where do I even start?
A> Not with code. Write the requirements as numbers, then derive every setting from one of them.
R> And how do we know the design is right?
A> We build it exactly as written, then break a broker in the middle and audit every single order.'''

lv = '''
LEVELS> Designing at three levels
L1> The story
      <ul>
        <li>Customers place orders; the kitchen needs them with prices; bad orders must not block good ones; nothing may be lost or counted twice; analytics wants a copy.</li>
      </ul>
L2> The decisions
      <ul>
        <li><b>Key = city</b>: order per city, spread across partitions (watch for hot keys, Lesson 2.2). <b>6 partitions</b>: 6 parallel consumers.</li>
        <li><b>RF 3, min ISR 2, acks=all, idempotence</b>: survive one broker loss without losing writes (2.4, 2.5, 5.2).</li>
        <li><b>Transactions + read_committed</b>: each order lands once in enriched <i>or</i> DLQ, even across crashes (3.5). <b>Compacted menu</b> as a lookup table (4.3). <b>Avro + registry</b> (8.1). <b>Connect sink</b> (7.1).</li>
      </ul>
L3> At 100× scale
      <ul>
        <li>Partitions from measured rates (10.2); move the processor to Kafka Streams or Flink with state stores instead of an in-memory menu (9.2, 9.4); share groups for non-ordered side jobs (6.1).</li>
        <li>Security per app (10.3), lag-in-seconds SLOs (10.1), a DR cluster with MirrorMaker 2 (10.4), and possibly a managed platform (11.1).</li>
      </ul>
/LEVELS
'''
DT = table(['Requirement', 'Decision', 'Lesson'], [
    ['2,000 orders/s peak, 6 consumers', '6 partitions', '10.2'], ['Order per city', 'key = city', '2.2'], ['Must not lose', 'RF 3, min ISR 2, acks=all, idempotent', '2.4, 2.5, 5.2'],
    ['No double counting', 'transactions + read_committed', '3.5'], ['Bad orders (~5%)', 'DLQ with x-error header', '6.2'], ['Prices change', 'compacted cap-menu', '4.3'],
    ['Many teams read', 'Avro + Schema Registry', '8.1'], ['Copy to analytics', 'Connect sink', '7.1'], ['60 s SLO', 'lag alerts', '10.1'],
], minw=600)
extra = '''

  <h3>Decision table</h3>
''' + DT

types_html = table(['Topic', 'Partitions', 'Policy', 'Key'], [
    ['cap-orders', '6', 'delete, 7 days, min ISR 2', 'city'], ['cap-menu', '3', 'compact', 'item'], ['cap-orders-enriched', '3', 'delete, min ISR 2', 'city'], ['cap-orders-dlq', '3', 'delete, 30 days', 'city'],
], minw=560)
warn = 'A design review should ask “what happens when…” for each part: a broker dies, the processor crashes mid-batch, a bad order arrives, the menu changes, a consumer is slow, the schema changes. If the design has no answer, add one before coding.'

steps = [
    ('Step 1 · Requirements as numbers',
     code('python', 'l121.py', 'req = {"orders_peak_per_s": 2000, "order_kb": 0.5, "consumers_max": 6, "latency_slo_s": 60,\n       "keep_days": 7, "must_not_lose": True, "order_per_city": True, "bad_orders_pct": 5}', sec('== 1)', '== 2)')),
     'Every later decision points back to one of these lines.'),
    ('Step 2 · Derive decisions',
     code('python', 'l121.py', 'parts = max(math.ceil(mb / 5), req["consumers_max"])', sec('== 2)', '== 3)')),
     'Throughput needs only 1 partition (under 1 MB/s); parallelism needs 6. Durability, processing and error choices follow from the flags.'),
    ('Step 3 · Topic plan',
     code('python', 'l121.py', 'for t, p, c in topics: print(t, p, "RF 3", c)', sec('== 3)')),
     'Four topics, each with a reason. 12.2 creates exactly these.'),
]
see = [term([('2000/s · 0.5 KB', W), ('6 consumers · 60 s SLO', W)], size=7.0), term([('6 partitions, key city', G), ('RF 3 · min ISR 2 · acks=all', G), ('transactions + DLQ', G)], size=6.8), term([('cap-orders 6', W), ('cap-menu compact', W), ('enriched · dlq', W)], size=7.0)]
B1 = [arch(0), arch(1), arch(2)]
B1 = [b + cap(c, '', tn, y=128, h=30) for b, c, tn in zip(B1, ['Requirements', 'Decisions', 'Topic plan'], ['blue', 'violet', 'green'])]
two = anim_two('Capstone design', 'Requirements → decisions', 'Real outputs from the design script', 'The architecture', see, B1, ['Needs.', 'Derive.', 'Plan.'], ['Numbers.', 'Settings.', 'Topics.'])
pe = peel('One order through the design, layer by layer', 'Order 1: Delhi, idli × 1. (From the plan.)',
    [('Produce', ''), ('Store', ''), ('Process', ''), ('Write', ''), ('Commit', ''), ('Sink', '')],
    [['Produce', 'Avro, schema id', 'key Delhi', 'acks=all, idempotent'], ['Store', 'cap-orders p(Delhi)', 'RF 3, ISR ≥ 2', ''], ['Process', 'read_committed', 'price from cap-menu', 'idli = 45'],
     ['Write', 'enriched (or DLQ)', 'inside a transaction', ''], ['Commit', 'offsets in same tx', 'exactly once', ''], ['Sink', 'Connect file sink', 'analytics copy', '']],
    ['Send.', 'Keep.', 'Enrich.', 'Write.', 'Commit.', 'Copy.'], 'scenario-peel')
scen = five('Design review 1', 'Hot city', 'Mumbai has 70% of orders. (Typical.)', ('Key choice', 'Ordering vs balance'), [
    ('Key city', 'Mumbai partition hot', 'Skew.', 'red'), ('Need: order per order, not per city?', 're-check requirement', 'Question.', 'amber'),
    ('Key = order id or restaurant', 'better spread', 'Option.', 'green'), ('Keep city for per-city aggregates', 'separate topic', 'Option.', 'green'),
    ('Decide with data', 'measure skew', 'Done.', 'blue')], ['Skew.', 'Ask.', 'Re-key.', 'Split.', 'Measure.'], 'scenario-hot') + \
       five('Design review 2', 'Menu service down', 'Lookup unavailable. (Typical.)', ('Local table', 'Compacted topic, not RPC'), [
    ('Processor calls menu API', 'per order', 'Coupled.', 'red'), ('API down', 'pipeline stops', 'Outage.', 'red'),
    ('Use compacted cap-menu', 'local copy', 'Decouple.', 'green'), ('Updates flow as events', 'latest wins', 'Fresh.', 'green'),
    ('No runtime dependency', 'resilient', 'Done.', 'blue')], ['Call.', 'Down.', 'Table.', 'Events.', 'Safe.'], 'scenario-menu') + \
       five('Design review 3', 'Schema change next quarter', 'Add delivery slot. (Typical.)', ('BACKWARD evolution', 'Default value'), [
    ('New field slot', 'needed', 'Change.', 'blue'), ('Add with default', 'registry OK', 'Compatible.', 'green'),
    ('Upgrade consumers first', 'BACKWARD', 'Order.', 'amber'), ('Producers send slot', 'new data', 'Roll.', 'green'),
    ('Old data still readable', 'default fills', 'Done.', 'blue')], ['Need.', 'Default.', 'Consumers.', 'Producers.', 'Safe.'], 'scenario-schema')
assemble(HERE, h2_story='From requirements to a Kafka design', hook_html=hk,
    narration='TiffinGo’s CTO asks Kabir for a production order pipeline on Kafka. Before any code, he writes down what the business needs, as numbers.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='The capstone design',
    formal='The <b>capstone</b> is an end-to-end order pipeline: an Avro producer writes orders keyed by city to a replicated topic; an exactly-once processor (transactions, read_committed) enriches each order with prices from a compacted reference topic and writes it either to an enriched topic or to a dead letter queue with error headers; Kafka Connect copies enriched orders to a sink; monitoring tracks lag and counts.',
    simple='Orders go in, get prices added, good ones go to one topic and bad ones to a problem topic, and a connector copies the good ones out. Every order must end up in exactly one place.',
    term_rows=[('Requirement', 'What the business needs.'), ('Decision', 'Setting derived from it.'), ('Topic plan', 'Topics + configs.'), ('Data flow', 'Path of a record.'), ('Reference data', 'Lookup table (menu).'), ('Enrichment', 'Adding fields.'), ('Reconciliation', 'Counts must match.'), ('Design review', '“What happens when…”.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('More partitions are safer.', 'Size from needs: 6 here.', 'Step 2.'),
               ('Exactly-once is a broker setting.', 'It is a pattern: idempotence + transactions + read_committed.', 'Decision table.'),
               ('Design can wait until code works.', 'Keys and partitions are hard to change later.', 'Review 1.')],
    exam='“Design an order pipeline with Kafka.” Requirements → partitions (rates, consumers), key (ordering), RF 3/min ISR 2/acks=all/idempotence, EOS processing, DLQ, compacted reference data, schemas, Connect sink, monitoring, security, DR.',
    types_h2='The topic plan', types_html=types_html, warn=warn,
    steps_h2='Requirements to plan', steps_intro='All outputs are real: a small design script that turns requirements into decisions.',
    steps=steps, two=two, peel_intro='Now follow one order through the design.', peel_html=pe,
    scen_intro='Three design reviews: a hot city, a menu outage, and a schema change.', scen=scen,
    uc_h2='Where this design appears', ucs=[uc_('food', 'delivery', 'blue', '1. Food and grocery delivery', 'Orders, prices, kitchens.', ['Orders', '*pipeline', 'Kitchen']),
        uc_('ecom', 'e-commerce', 'green', '2. E-commerce checkout', 'Validate, price, route.', ['Cart', '*pipeline', 'Fulfilment']),
        uc_('pay', 'payments', 'red', '3. Payments', 'Exactly-once, DLQ.', ['Payments', '*EOS', 'Ledger']),
        uc_('iot', 'IoT', 'violet', '4. IoT ingestion', 'Validate, enrich, sink.', ['Devices', '*pipeline', 'Lake'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> Modules 1–11.')
