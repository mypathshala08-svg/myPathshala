import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l122_pipeline.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('3,000 orders in. How many come out the other side, and can you prove not one was lost or doubled?',
    'We built the whole design from 12.1 in one script: 4 topics, an Avro producer, an <b>exactly-once</b> processor with a compacted menu and a <b>DLQ</b>, and a <b>Kafka Connect</b> sink. Result: <b>1,841 enriched + 1,159 in the DLQ = 3,000</b>, group lag 0, and 1,841 lines in the sink file. Every number reconciles.',
    ['Building each part of the pipeline, step by step.',
     'Exactly-once consume-transform-produce in Python.',
     'Reconciling counts and reading the DLQ.'])
cmap = concept_map('Concept map of the build: topics, menu, Avro producer, exactly-once processor, DLQ, Connect sink and reconciliation, each linked to the lesson that taught it.',
    [[('ds', 'Design', '12.1', B + '12-capstone/01-problem-and-design/'), ('tp', 'Topics + configs', '1.4', None)],
     [('pd', 'Avro producer', '8.1, 2.5', B + '08-schemas/01-schema-registry/'), ('mn', 'Compacted menu', '4.3', B + '04-storage-internals/03-retention-and-compaction/'), ('eo', 'EOS processor', '3.5', B + '03-consumers/05-transactions-and-exactly-once/'), ('dq', 'DLQ', '6.2', B + '06-queues-and-error-handling/02-retry-topics-and-dead-letter-queues/')],
     [('sk', 'Connect sink', '7.1', B + '07-kafka-connect/01-kafka-connect/'), ('rc', 'Reconcile', 'counts', None), ('lg', 'Lag 0', '10.1', B + '10-kafka-in-production/01-monitoring-and-consumer-lag/'), ('rv', 'Break it', '12.3', B + '12-capstone/03-review-and-interview-preparation/')]],
    [('ds', 'tp'), ('tp', 'pd'), ('tp', 'mn'), ('pd', 'eo'), ('mn', 'eo'), ('eo', 'dq'), ('eo', 'sk'), ('dq', 'rc'), ('sk', 'rc'), ('rc', 'lg'), ('lg', 'rv')],
    {'tp', 'pd', 'mn', 'eo', 'dq', 'sk', 'rc', 'lg'},
    '<b>Builds on:</b> <a href="../01-problem-and-design/">12.1</a>. <b>Next:</b> <a href="../03-review-and-interview-preparation/">12.3 Review and interview preparation</a>.')
whw = why_how_where(
    'A design is only a claim until a working pipeline shows the counts add up. Building it end to end also reveals glue problems (serializers, isolation levels, connector configs) that single lessons hide.',
    'One Python script creates the topics, loads the menu, produces 3,000 Avro orders, runs a transactional processor that writes either enriched or DLQ records and commits offsets in the same transaction, then registers a Connect sink and checks counts and lag.',
    'A template for real projects and for your portfolio; run it on the course VM or in Colab against a local cluster (see Lesson 1.6).',
    'The processor here is a single Python process with the menu in memory; at scale you would run several instances (consumer group) or use Kafka Streams/Flink.')

def flow(hl=-1, nums=('3000', '1841', '1159', '1841')):
    o = box(6, 40, 70, 40, 'blue' if hl != 0 else 'acc', rx=6) + t(41, 56, 'orders', 7.4, bold=True) + t(41, 72, nums[0], 8, bold=True)
    o += box(96, 40, 76, 40, 'violet' if hl != 1 else 'acc', rx=6) + t(134, 56, 'processor', 7.4, bold=True) + t(134, 72, 'EOS', 7.4)
    o += box(192, 22, 76, 36, 'green' if hl != 2 else 'acc', rx=6) + t(230, 38, 'enriched', 7.2, bold=True) + t(230, 52, nums[1], 8, bold=True)
    o += box(192, 70, 76, 36, 'red' if hl != 3 else 'acc', rx=6) + t(230, 86, 'DLQ', 7.2, bold=True) + t(230, 100, nums[2], 8, bold=True)
    o += box(288, 22, 66, 36, 'amber' if hl != 4 else 'acc', rx=6) + t(321, 38, 'file sink', 7.0, bold=True) + t(321, 52, nums[3], 8, bold=True)
    return o + arrow(76, 60, 96, 60) + arrow(172, 54, 192, 40) + arrow(172, 66, 192, 88) + arrow(268, 40, 288, 40)
scene_svg = scene('The built pipeline: 3,000 orders enter, the exactly-once processor sends 1,841 to the enriched topic and 1,159 to the DLQ, and the Connect file sink receives 1,841 lines.', flow(),
                  '<tspan font-weight="700" class="s-acc">1,841 + 1,159 = 3,000</tspan>: every order accounted for.')
dialogue = '''K> Sir, the design is approved. Do I build each piece separately?
A> Build it all, end to end, small. Then count: what went in must equal what came out, in exactly one place.
R> And the bad orders?
A> They go to the DLQ with a reason. We will count them by reason too.'''

lv = '''
LEVELS> Building at three levels
L1> An assembly line
      <ul>
        <li>Raw orders arrive, a worker checks and prices each, good ones go to the kitchen shelf, bad ones to the problem tray, and a copy of the shelf goes to the office. At the end of the day, shelf + tray must equal what arrived.</li>
      </ul>
L2> The pieces
      <ul>
        <li><b>Producer</b>: <code>acks=all</code>, <code>enable.idempotence=true</code>, AvroSerializer (schema auto-registered).</li>
        <li><b>Processor</b>: consumer with <code>isolation.level=read_committed</code>, <code>enable.auto.commit=false</code>; transactional producer (<code>transactional.id</code>); per batch: begin → produce enriched/DLQ → <code>send_offsets_to_transaction</code> → commit.</li>
        <li><b>Sink</b>: FileStreamSink with StringConverter and <code>consumer.override.isolation.level=read_committed</code> so it never sees aborted data.</li>
      </ul>
L3> Details that matter
      <ul>
        <li>End offsets of transactional topics include <b>commit markers</b>, so enriched shows 1,849 offsets for 1,841 records: count records, not offsets.</li>
        <li>The menu topic is compacted; the processor loads the latest value per item (idli updated 40 → 45).</li>
        <li>DLQ records keep the order and add <code>x-error</code> and <code>x-original-offset</code> headers, so you can group by reason and replay after a fix.</li>
      </ul>
/LEVELS
'''
REC = figure('Reconciliation: 3,000 orders produced; 1,841 enriched plus 1,159 DLQ equals 3,000; DLQ reasons 764 quantity not positive and 395 unknown item; group lag 0; 1,841 lines in the sink file.',
    t(16, 22, 'Reconciliation (real numbers)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('in 3000', 'blue', 1), ('enriched 1841', 'green', 2), ('DLQ 1159', 'red', 3), ('lag 0', 'violet', 4), ('sink 1841', 'amber', 5)]) +
    legend(16, 84, [(1, 'Produced', '3,000 Avro orders'), (2, 'Enriched', 'priced, inside transactions'), (3, 'DLQ', '764 qty ≤ 0 + 395 unknown item'),
                    (4, 'Lag', 'processor committed everything'), (5, 'Sink', 'Connect wrote every enriched record')], size=8, gap=15, w=90),
    h=172, caption='1,841 + 1,159 = 3,000 and sink = enriched.')
extra = '''

  <h3>Reconcile like an auditor</h3>
''' + REC

types_html = table(['Part', 'Key settings', 'From lesson'], [
    ['Producer', 'acks=all, idempotence, AvroSerializer', '2.4, 2.5, 8.1'], ['Menu', 'cleanup.policy=compact', '4.3'],
    ['Processor', 'read_committed, transactional.id, send_offsets_to_transaction', '3.5'], ['DLQ', 'x-error, x-original-offset headers', '6.2'],
    ['Sink', 'FileStreamSink, consumer.override.isolation.level=read_committed', '7.1'], ['Checks', 'counts, lag, DLQ reasons', '10.1'],
], minw=620)
warn = 'Do not reconcile with end offsets on transactional topics: commit/abort markers take offsets too (enriched had 1,849 offsets for 1,841 records). Count records with a read_committed consumer.'

steps = [
    ('Step 1 · Topics',
     code('python', 'l122.py', "for k, t in T.items():\n    cfg = {'cleanup.policy': 'compact'} if k == 'menu' else {'min.insync.replicas': '2'}\n    a.create_topics([NewTopic(t, 6 if k == 'orders' else 3, 3, config=cfg)])", sec('== 1)', '== 2)')),
     'Exactly the topic plan from 12.1.'),
    ('Step 2 · Produce Avro orders',
     code('python', 'l122.py', "p = Producer({'bootstrap.servers': BS, 'acks': 'all', 'enable.idempotence': True})\nfor k, v in menu.items(): p.produce('cap-menu', key=k, value=str(v))\np.produce('cap-menu', key='idli', value='45')   # price update\nfor i in range(1, 3001): p.produce('cap-orders', key=o['city'], value=ser(o, ctx))", sec('== 2)', '== 3)')),
     '3,000 orders in 0.2 s; the schema was registered (id 9 in our registry). About a quarter have qty 0 and a sixth order “pizza”, which is not on the menu.'),
    ('Step 3 · Exactly-once processor',
     code('python', 'l122.py', "tp.begin_transaction()\nfor m in msgs:\n    o = de(m.value(), ctx)\n    if bad(o): tp.produce('cap-orders-dlq', …, headers=[('x-error', reason), ('x-original-offset', str(m.offset()))])\n    else:      tp.produce('cap-orders-enriched', …)\ntp.send_offsets_to_transaction(c.position(c.assignment()), c.consumer_group_metadata())\ntp.commit_transaction()", sec('== 3)', '== 4)')),
     'Every order went to exactly one output; idli used the latest compacted price 45; revenue per city computed on the way.'),
    ('Step 4 · Reconcile',
     code('python', 'l122.py', "end offsets · consumer-groups lag · DLQ grouped by x-error", sec('== 4)', '== 5)')),
     'Lag 0. DLQ reasons: 764 quantity, 395 unknown item. End offsets include transaction markers (see warning).'),
    ('Step 5 · Sink',
     code('python', 'l122.py', "requests.put('http://localhost:8083/connectors/cap-sink/config', json={'connector.class': 'org.apache.kafka.connect.file.FileStreamSinkConnector', 'topics': 'cap-orders-enriched', 'consumer.override.isolation.level': 'read_committed', …})", sec('== 5)')),
     'The connector is RUNNING and the file has 1,841 lines, one per enriched order.'),
]
see = [term([('cap-orders 6', W), ('menu, enriched, dlq 3', W)], size=7.0), term([('3000 Avro orders 0.2 s', G), ('schema id 9', W)], size=7.0),
       term([('1841 + 1159 = 3000', G), ('idli = 45', Y)], size=7.0), term([('lag 0', G), ('qty 764 · unknown 395', RD)], size=7.0), term([('RUNNING', G), ('1841 lines', G)], size=7.0)]
B1 = [flow(0), flow(0), flow(1), flow(3), flow(4)]
B1 = [b + cap(c, '', tn, y=126, h=30) for b, c, tn in zip(B1, ['Topics ready', '3,000 orders in', 'Exactly once', 'Counts match', 'Sink complete'], ['blue', 'blue', 'violet', 'green', 'amber'])]
two = anim_two('The pipeline', 'Build and reconcile', 'Real outputs from the lab', 'Where every order went', see, B1, ['Topics.', 'Produce.', 'Process.', 'Reconcile.', 'Sink.'], ['Plan.', '3000.', 'EOS.', 'Match.', 'File.'])
pe = peel('One transaction, layer by layer', 'A batch of 500 orders. (Simplified.)',
    [('Consume', ''), ('Begin', ''), ('Write', ''), ('Offsets', ''), ('Commit', ''), ('Visible', '')],
    [['Consume', '500 records', 'read_committed', ''], ['Begin', 'begin_transaction', 'transactional.id cap-processor-1', ''], ['Write', 'enriched + DLQ records', 'not yet visible', ''],
     ['Offsets', 'send_offsets_to_transaction', 'group cap-processor', ''], ['Commit', 'markers written', 'all partitions', 'atomic'], ['Visible', 'read_committed readers', 'and the sink see them', '']],
    ['Read.', 'Start.', 'Write.', 'Offsets.', 'Commit.', 'Visible.'], 'scenario-peel')
scen = five('Build issue 1', 'Sink shows extra records', 'Aborted data in the file. (Typical.)', ('Isolation level', 'read_committed everywhere'), [
    ('Processor aborted a batch', 'retry', 'Normal.', 'blue'), ('Sink read_uncommitted', 'default', 'Leak.', 'red'),
    ('consumer.override.isolation.level', 'read_committed', 'Fix.', 'green'), ('Counts match again', 'file = enriched', 'Clean.', 'green'),
    ('Check every consumer', 'of transactional topics', 'Rule.', 'blue')], ['Abort.', 'Leak.', 'Fix.', 'Match.', 'Rule.'], 'scenario-iso') + \
       five('Build issue 2', 'Producer fenced', 'Two processors, same transactional.id. (Typical.)', ('Unique transactional.id', 'One per instance/partition set'), [
    ('Scale to 2 instances', 'same id', 'Conflict.', 'red'), ('Old one fenced', 'ProducerFenced', 'Error.', 'red'),
    ('id per instance', 'cap-processor-1, -2', 'Fix.', 'green'), ('Group shares partitions', 'each EOS', 'Scale.', 'green'),
    ('Or Kafka Streams EOS v2', 'handles it', 'Simpler.', 'blue')], ['Scale.', 'Fenced.', 'Unique.', 'Share.', 'Streams.'], 'scenario-fence') + \
       five('Build issue 3', 'DLQ keeps growing', '38% of orders bad. (Typical.)', ('Read the DLQ', 'Fix the source'), [
    ('1,159 of 3,000 in DLQ', 'too many', 'Alarm.', 'red'), ('Group by x-error', '764 qty ≤ 0', 'Cause.', 'amber'),
    ('App sends qty 0 for drafts', 'bug upstream', 'Root.', 'amber'), ('Fix app + replay valid ones', 'after fix', 'Repair.', 'green'),
    ('Alert on DLQ rate', '> 5%', 'Prevent.', 'blue')], ['Grow.', 'Group.', 'Root.', 'Replay.', 'Alert.'], 'scenario-dlq')
assemble(HERE, h2_story='Build it end to end', hook_html=hk,
    narration='The design from 12.1 is approved. Kabir builds the whole pipeline in one evening and must prove to the CTO that not a single order was lost or doubled.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Building the pipeline',
    formal='The capstone pipeline implements <b>consume-transform-produce with exactly-once semantics</b>: a transactional producer writes enriched or dead-letter records and the consumer’s offsets in one atomic transaction, while downstream consumers (including the Connect sink) read with <code>read_committed</code>. Reference data comes from a compacted topic, records are Avro-encoded with a schema registry, and correctness is verified by <b>reconciliation</b> of record counts and consumer lag.',
    simple='We built the full system and counted: everything that went in came out exactly once, either as a priced order or as a problem record with a reason.',
    term_rows=[('EOS', 'Exactly-once semantics.'), ('transactional.id', 'Producer identity for transactions.'), ('read_committed', 'See only committed data.'), ('Commit marker', 'Takes an offset.'), ('Reconciliation', 'In = out checks.'), ('Reference data', 'Menu prices.'), ('x-error', 'DLQ reason header.'), ('Sink', 'Copy out of Kafka.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('End offsets = record counts.', 'Markers take offsets on transactional topics.', 'Step 4.'),
               ('EOS needs Kafka Streams.', 'Plain clients can do it with transactions.', 'Step 3.'),
               ('A DLQ means data loss.', 'Records kept with reasons, replayable.', 'Step 4.')],
    exam='“Build an exactly-once enrichment pipeline.” Idempotent Avro producer; transactional processor (read_committed, send_offsets_to_transaction); DLQ with headers; compacted lookup topic; Connect sink with read_committed; reconcile counts; lag 0.',
    types_h2='Parts and settings', types_html=types_html, warn=warn,
    steps_h2='Five steps, one script', steps_intro='All outputs are real: Kafka 4.4.0 (3 brokers), Schema Registry 8.1, Kafka Connect 4.4, Python confluent-kafka 2.16. Script: lab/jobs/m12/l122.py.',
    steps=steps, two=two, peel_intro='Now peel one transaction.', peel_html=pe,
    scen_intro='Three build issues you will meet.', scen=scen,
    uc_h2='Reuse this pipeline', ucs=[uc_('tpl', 'template', 'blue', '1. Project template', 'Copy, change topics and rules.', ['Script', '*adapt', 'Your project']),
        uc_('port', 'portfolio', 'green', '2. Portfolio', 'Show EOS + DLQ + sink.', ['Repo', '*README', 'Interview']),
        uc_('vm', 'VM/Colab', 'violet', '3. Run on VM or Colab', 'See Lesson 1.6 setup.', ['Docker', '*lab', 'Run']),
        uc_('ext', 'extend', 'amber', '4. Extend', 'Streams window, MM2 DR.', ['Pipeline', '*add', 'More'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../01-problem-and-design/">12.1 Design</a>.')
