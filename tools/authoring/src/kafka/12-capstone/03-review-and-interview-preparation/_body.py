import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l123_chaos.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('We killed a broker two seconds into processing 3,000 orders. How many of the 6,000 orders ended up missing or duplicated?',
    '<b>Zero.</b> The audit read 3,728 enriched + 2,272 DLQ records, all 6,000 order ids, each exactly once. Getting there was not free: on the first attempt our processor gave up too early while the group coordinator moved, and processed nothing. That is the review lesson: <b>exactly-once is a property you test under failure</b>, not a setting you trust. Then we use the whole course to prepare for interviews.',
    ['How to attack your own pipeline (chaos test + audit).',
     'A review checklist for any Kafka system.',
     'Interview preparation: the questions that come up, mapped to lessons.'])
cmap = concept_map('Concept map of the review: chaos test, audit, checklist and interview topics across producers, consumers, storage, replication, queues, Connect, schemas, streams and production.',
    [[('bd', 'Built pipeline', '12.2', B + '12-capstone/02-build-the-pipeline/'), ('ch', 'Chaos test', 'kill a broker', None)],
     [('au', 'Audit', 'ids exactly once', None), ('rl', 'Leader election', '5.3', B + '05-replication-and-the-cluster/03-leader-election/'), ('tx', 'Transactions', '3.5', B + '03-consumers/05-transactions-and-exactly-once/'), ('ck', 'Review checklist', 'every system', None)],
     [('iq', 'Interview Q&A', 'by module', None), ('sd', 'System design', 'patterns', None), ('mn', 'Monitoring', '10.1', B + '10-kafka-in-production/01-monitoring-and-consumer-lag/'), ('nx', 'What’s new', '11.3', B + '11-kafka-in-industry/03-whats-new-in-kafka-4/')]],
    [('bd', 'ch'), ('ch', 'au'), ('ch', 'rl'), ('au', 'tx'), ('au', 'ck'), ('ck', 'iq'), ('ck', 'sd'), ('ck', 'mn'), ('iq', 'nx')],
    {'ch', 'au', 'ck', 'iq', 'sd'},
    '<b>Uses:</b> the whole course. <b>Next:</b> build your own project, and review any lesson from the course page.')
whw = why_how_where(
    'Pipelines look correct when everything works. Failures (broker loss, coordinator moves, crashes mid-transaction) are where data is lost or doubled, and where interviews dig.',
    'Run the pipeline, inject a failure at a random moment, let it finish, then audit with an independent read_committed reader: every id present, exactly once. Repeat for each failure type. Then walk a checklist and practise explaining each decision.',
    'Release checklists, game days, architecture reviews, and interviews for data engineer, platform and backend roles.',
    'A passing test proves only the failures you tried. Keep the audit script and run it after every change.')

def chaos(hl=-1):
    o = ''
    for k in range(3):
        o += box(10 + k * 70, 34, 60, 40, 'red' if (k == 2 and hl >= 1) else 'blue', rx=6) + t(40 + k * 70, 58, f'k{k+1}', 9, bold=True)
    o += t(180, 22, 'kill k3 at t+2 s', 7.6)
    o += box(230, 34, 124, 40, 'green' if hl >= 2 else 'violet', rx=6) + t(292, 52, 'audit', 8, bold=True) + t(292, 66, '6000 ids, once', 7.2)
    return o + arrow(220, 54, 230, 54)
scene_svg = scene('Chaos test: three brokers k1, k2, k3; k3 is killed two seconds into processing; an audit then checks that all 6,000 order ids appear exactly once.', chaos(2),
                  'Kill a broker, then audit: <tspan font-weight="700" class="s-acc">6,000 ids, each exactly once</tspan>.')
dialogue = '''K> Sir, the pipeline passed. Can we ship it?
A> It passed when nothing broke. Now we kill a broker in the middle and count every order again.
R> And if it passes that too?
A> Then you can explain it in any interview: what you chose, why, and how you proved it. Let’s break it.'''

lv = '''
LEVELS> Review at three levels
L1> A fire drill
      <ul>
        <li>A building is safe only if people get out during a drill. A pipeline is correct only if the counts still match after you pull a plug.</li>
      </ul>
L2> The review checklist
      <ul>
        <li><b>Data</b>: keys and ordering, partitions from numbers, schemas and compatibility mode, retention/compaction.</li>
        <li><b>Durability</b>: RF 3, min ISR 2, acks=all, idempotence; EOS where duplicates matter; idempotent sinks otherwise.</li>
        <li><b>Errors</b>: DLQ with reasons, retries with backoff, alert on DLQ rate; poison-message handling.</li>
        <li><b>Operations</b>: lag-in-time alerts, URP/offline alerts, security (TLS, SASL, ACLs, quotas), DR plan and drills, upgrade path.</li>
      </ul>
L3> What our drill taught
      <ul>
        <li>The first run stopped after a fixed number of empty polls while the group coordinator and transaction coordinator on k3 failed over, and processed nothing: timeouts in your own loop can turn a 10-second hiccup into “done”. We changed the loop to run until the expected count or a generous deadline.</li>
        <li>With k3 dead, RF 3 / min ISR 2 kept writes going, the transactional producer reconnected to a new coordinator, and the audit found every id once.</li>
      </ul>
/LEVELS
'''
IQ = table(['Area', 'Typical question', 'Lessons'], [
    ['Basics', 'Topic, partition, offset, consumer group? Kafka vs a queue?', '1.2–1.4, 11.2'], ['Producers', 'acks, idempotence, batching, partitioner, ordering?', '2.1–2.5'],
    ['Consumers', 'Rebalances (KIP-848), commits, lag, delivery semantics, EOS?', '3.1–3.5'], ['Storage', 'Segments, indexes, retention vs compaction, zero-copy?', '4.1–4.4'],
    ['Replication', 'ISR, high watermark, leader election, KRaft?', '5.1–5.4'], ['Queues/errors', 'Share groups, retries, DLQ?', '6.1–6.2'],
    ['Integration', 'Connect, CDC with Debezium, Schema Registry, compatibility?', '7.1–8.2'], ['Processing', 'Streams vs Spark vs Flink, KTable, windows, joins?', '9.1–9.4'],
    ['Production', 'Monitoring, tuning, partitions, security, DR?', '10.1–10.4'], ['Industry', 'Managed options, Kafka 4 changes?', '11.1–11.3'],
], minw=660)
extra = '''

  <h3>Interview map: question → lesson</h3>
''' + IQ

types_html = table(['Failure to test', 'Expected result', 'Tested here'], [
    ['Broker killed during processing', 'all ids once, writes continue (min ISR 2)', 'yes: 6,000/6,000'], ['Processor crash mid-transaction', 'aborted batch re-processed, no duplicates visible', 'Lesson 3.5'],
    ['Leader failover while producing', 'no loss with acks=all + retries', 'Lesson 5.3: 160/160'], ['Bad records', 'DLQ, pipeline continues', '12.2: 1,159'],
    ['Region loss', 'DR with translated offsets, duplicates handled', 'Lesson 10.4'],
], minw=620)
warn = 'Do not end a processing loop on “no data for N polls” in tests or batch jobs: during coordinator failover a healthy consumer can receive nothing for 10+ seconds. Stop on an expected count, a deadline, or end offsets reached.'

steps = [
    ('Step 1 · Attack',
     code('python', 'l123.py', "threading.Thread(target=lambda: (time.sleep(2), subprocess.run(['docker', 'kill', 'k3']))).start()\n# same exactly-once loop as 12.2, until 3,000 new orders are handled or 120 s", sec('== 1)', '== 2)')),
     '3,000 new orders (ids 3001–6000) were waiting. Broker 3 was killed two seconds in.'),
    ('Step 2 · Finish under failure',
     code('python', 'l123.py', 'tp.begin_transaction() … tp.send_offsets_to_transaction(…) … tp.commit_transaction()', sec('== 2)', '== 3)')),
     '15 transactions, 12.9 s, all 3,000 handled with only two brokers.'),
    ('Step 3 · Audit',
     code('python', 'l123.py', "e, d = read_ids('cap-orders-enriched'), read_ids('cap-orders-dlq')   # read_committed\nprint(sorted(set(e) | set(d)) == list(range(1, 6001)) and len(e) + len(d) == 6000)", sec('== 3)')),
     'All 6,000 ids, none missing, none twice, across both runs (12.2 and this one).'),
]
see = [term([('3000 waiting', W), ('t+2s: docker kill k3', RD)], size=7.2), term([('1887 + 1113 = 3000', G), ('15 transactions, 12.9 s', W)], size=7.0), term([('enriched 3728 · dlq 2272', W), ('6000 unique', G), ('exactly once: True', G)], size=7.0)]
B1 = [chaos(1), chaos(1), chaos(2)]
B1 = [b + cap(c, '', tn, y=104, h=30) for b, c, tn in zip(B1, ['Broker killed', 'Still processing', 'Audit passes'], ['red', 'amber', 'green'])]
two = anim_two('Chaos test', 'Kill, finish, audit', 'Real outputs from the lab', 'Under failure', see, B1, ['Kill.', 'Finish.', 'Audit.'], ['k3.', '3000.', '6000.'])
pe = peel('Surviving the kill, layer by layer', 'k3 dies at t+2 s. (Simplified.)',
    [('Fence', ''), ('Elect', ''), ('Coordinator', ''), ('Abort/retry', ''), ('Commit', ''), ('Audit', '')],
    [['Fence', 'controller fences k3', '~9 s session', 'Lesson 5.2'], ['Elect', 'new leaders from ISR', 'min ISR 2 holds', 'Lesson 5.3'], ['Coordinator', 'group + txn coordinators', 'move to live brokers', ''],
     ['Abort/retry', 'open transaction aborted', 'batch re-read', 'read_committed hides it'], ['Commit', 'new transactions', 'offsets + outputs', 'atomic'], ['Audit', '6,000 ids', 'exactly once', '']],
    ['Fence.', 'Elect.', 'Move.', 'Retry.', 'Commit.', 'Check.'], 'scenario-peel')
scen = five('Interview 1', '“Design a payment event pipeline”', 'System design. (Typical.)', ('Use the capstone', 'Explain every choice'), [
    ('Requirements as numbers', 'rate, SLO, durability', 'Start.', 'blue'), ('Topics, keys, partitions', 'ordering per account', 'Design.', 'blue'),
    ('Durability + EOS', 'RF 3, min ISR 2, transactions', 'Safety.', 'green'), ('Errors, schemas, sinks', 'DLQ, registry, Connect', 'Complete.', 'green'),
    ('Ops: lag, security, DR', 'and how you tested it', 'Senior.', 'violet')], ['Numbers.', 'Topics.', 'Safety.', 'Edges.', 'Ops.'], 'scenario-design') + \
       five('Interview 2', '“How do you get exactly-once?”', 'Deep dive. (Typical.)', ('Three parts', 'Producer, transactions, readers'), [
    ('Idempotent producer', 'PID + sequence', 'No dup writes.', 'blue'), ('Transactions', 'outputs + offsets atomic', 'No dup processing.', 'green'),
    ('read_committed readers', 'skip aborted', 'Clean reads.', 'green'), ('Sinks idempotent', 'outside Kafka', 'End to end.', 'amber'),
    ('Proof', 'chaos + audit', 'Credible.', 'violet')], ['Producer.', 'Tx.', 'Readers.', 'Sinks.', 'Proof.'], 'scenario-eos') + \
       five('Interview 3', '“A consumer is lagging. What do you do?”', 'Troubleshooting. (Typical.)', ('Method', 'Measure, locate, fix'), [
    ('Lag in time', 'vs SLO', 'Measure.', 'blue'), ('Commits moving?', 'stuck vs slow', 'Locate.', 'amber'),
    ('Slow: scale to partitions', 'or batch work', 'Fix.', 'green'), ('Stuck: poison record?', 'DLQ, handler', 'Fix.', 'green'),
    ('Broker side?', 'URP, idle %', 'Check.', 'violet')], ['Measure.', 'Locate.', 'Scale.', 'Unstick.', 'Broker.'], 'scenario-lag')
assemble(HERE, h2_story='Break it, then explain it', hook_html=hk,
    narration='The pipeline from 12.2 works. Before the CTO signs off, Kabir kills a broker in the middle of processing and audits every order. Then he prepares for the interviews that come with the new job title.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Review and interview preparation',
    formal='A <b>production review</b> verifies a streaming system against its requirements under failure: <b>fault injection</b> (e.g. broker termination during processing) followed by an independent <b>audit</b> that checks completeness and uniqueness of every record, plus a checklist covering data design, durability, error handling, security and operations. <b>Interview preparation</b> maps common questions to the concepts and evidence gathered in each lesson.',
    simple='Break your system on purpose, then count everything again. If the numbers still match, you understand it well enough to explain it in an interview.',
    term_rows=[('Chaos test', 'Inject a failure.'), ('Audit', 'Independent count check.'), ('Game day', 'Planned failure drill.'), ('Checklist', 'Review questions.'), ('Coordinator', 'Group/transaction manager.'), ('Failover', 'Switch to healthy node.'), ('System design', 'Interview architecture task.'), ('Evidence', 'Numbers that prove a claim.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('If it works once, it works.', 'Test under failure.', 'Step 1.'),
               ('Exactly-once is a config flag.', 'A tested pattern with audits.', 'Step 3.'),
               ('“No data for a while” means done.', 'Failovers pause delivery.', 'Level 3.')],
    exam='“How do you prove a Kafka pipeline is correct?” Fault injection (kill broker/processor), independent read_committed audit (every id once), checklists (keys, partitions, RF/min ISR/acks, EOS, DLQ, schemas, security, monitoring, DR), repeated after changes.',
    types_h2='Failures to test', types_html=types_html, warn=warn,
    steps_h2='Kill, finish, audit', steps_intro='All outputs are real: the 12.2 pipeline with 3,000 more orders, broker k3 killed two seconds into processing, then a full audit of all 6,000 orders.',
    steps=steps, two=two, peel_intro='Now peel how it survived.', peel_html=pe,
    scen_intro='Three interview questions answered with this course.', scen=scen,
    uc_h2='After the course', ucs=[uc_('proj', 'project', 'blue', '1. Your own project', 'Reuse 12.2, add Streams or Spark.', ['Idea', '*pipeline', 'Demo']),
        uc_('cert', 'study', 'green', '2. Certification study', 'Revise by module.', ['Lessons', '*quiz', 'Exam']),
        uc_('job', 'interviews', 'violet', '3. Interviews', 'Use real lab numbers.', ['Question', '*evidence', 'Offer']),
        uc_('work', 'work', 'amber', '4. At work', 'Checklist + chaos tests.', ['System', '*review', 'Confidence'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../02-build-the-pipeline/">12.2 Build the pipeline</a>.')
