import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l33_offsets.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('Billing was down for an hour. Kafka knew exactly where to restart. Where was that bookmark stored?',
    'Our billing group read 120 orders, committed, and stopped. 300 more orders arrived and the lag climbed to 189 on one partition. Then we rewound the group to the beginning with one command. The bookmark itself lives in a Kafka topic, and we print it.',
    ['The difference between the <b>position</b> and the <b>committed offset</b>.',
     'Auto vs manual commits, and what each risks.',
     'How to read lag and safely rewind a group (dry run first).'])
cmap = concept_map('Concept map. Beginner: offset, commit, lag. Intermediate: auto and manual commit, sync and async, __consumer_offsets, auto.offset.reset. Advanced: reset tools, commit on revoke, monitoring lag, offsets in external stores.',
    [[('of', 'Offset', 'Lesson 1.4', B + '01-introduction/04-topics-partitions-and-offsets/'), ('cm', 'Commit', 'save progress', None), ('lg', 'Lag', 'end − committed', None)],
     [('am', 'Auto vs manual', 'enable.auto.commit', None), ('sa', 'Sync vs async', 'commit()', None), ('co', '__consumer_offsets', 'where it is stored', None), ('ar', 'auto.offset.reset', 'no commit yet', None)],
     [('rs', 'Reset tools', '--to-earliest, --shift-by', None), ('dg', 'Delivery guarantees', 'Lesson 3.4', B + '03-consumers/04-delivery-guarantees/'), ('mo', 'Lag monitoring', 'Lesson 10.1', B + '10-kafka-in-production/01-monitoring-and-consumer-lag/')]],
    [('of', 'cm'), ('cm', 'am'), ('cm', 'sa'), ('cm', 'co'), ('lg', 'mo'), ('am', 'dg'), ('co', 'rs'), ('ar', 'rs')],
    {'of', 'cm', 'lg', 'am', 'sa', 'co', 'ar', 'rs'},
    '<b>Builds on:</b> <a href="../01-consumers-and-consumer-groups/">3.1</a>, <a href="../02-rebalancing-and-partition-assignment/">3.2</a>. <b>Next:</b> <a href="../04-delivery-guarantees/">3.4 Delivery guarantees</a>.')
whw = why_how_where(
    'A consumer will restart, crash or lose partitions. Without a saved position it would re-read everything or skip data.',
    'The group commits “next offset to read” per partition to __consumer_offsets; on restart or rebalance the owner resumes from there. Lag = log end offset − committed offset.',
    'Every consumer group; lag is the main health metric of any Kafka pipeline.',
    'Committing does not mean processing succeeded; commit only after work is done (Lesson 3.4).')
sc_ = offset_ruler('One partition of orders-33 for group billing-33: committed offset 14, log end 203, lag 189.', n_total=10, committed=3, label='')
sc_ = ''
sc_ += t(14, 22, 'partition 0 of orders-33 · group billing-33', 8.6, 'ink', anchor='start', bold=True)
sc_ += box(30, 40, 580, 30, 'card', rx=4) + box(30, 40, 580 * 14 / 203, 30, 'green', rx=4) + box(30 + 580 * 14 / 203, 40, 580 * (203 - 14) / 203, 30, 'amber', rx=4)
sc_ += t(30, 90, '0', 8, 'ink2', anchor='start') + t(30 + 580 * 14 / 203, 90, 'committed 14', 8, 'green', bold=True) + t(610, 90, 'log end 203', 8, 'red', anchor='end', bold=True)
sc_ += t(320, 60, 'LAG = 203 − 14 = 189 orders not yet billed', 9, 'ink', bold=True) + t(320, 118, 'committed offset = “next record to read”, saved in __consumer_offsets', 8, 'ink2')
scene_svg = scene('Partition 0 of orders-33 for group billing-33: committed offset 14, log end offset 203, lag 189 orders not yet billed.', sc_,
                  'Lag tells you how far <tspan font-weight="700" class="s-acc">behind</tspan> a group is.')
dialogue = '''R> Sir, when billing restarts, how does it know it already billed the first 14 orders on partition 0?
A> Because it <b>committed</b> offset 14: “next time, start at 14”. That number is stored in Kafka itself, in the <code>__consumer_offsets</code> topic.
K> And the dashboard shows “lag 189”. Is that bad?
A> It means 189 orders are waiting. Lag rising is the first sign of trouble. Let’s commit by hand, watch lag grow while billing is down, and then rewind the group.'''

lv = '''
LEVELS> Offsets and commits at three levels
L1> A bookmark in a register
      <ul>
        <li>The billing clerk writes “done up to page 14” in a register. If someone else takes over, they start at page 15. Lag is how many pages are still unread.</li>
      </ul>
L2> Position vs committed
      <ul>
        <li><b>Position</b>: the next offset the consumer will fetch (in memory, moves with every poll).</li>
        <li><b>Committed offset</b>: the position saved to Kafka; used after restarts and rebalances. It is always “next to read”, not “last processed”.</li>
        <li><code>enable.auto.commit=true</code> commits the position every <code>auto.commit.interval.ms</code> (5 s) in the background; <code>false</code> means you call <code>commit()</code> yourself, synchronously (waits) or asynchronously (faster, no retry ordering).</li>
      </ul>
L3> Tools and storage
      <ul>
        <li>Commits are records in <code>__consumer_offsets</code> (50 partitions, compacted): key = group + topic + partition, value = offset, leader epoch, metadata, timestamp.</li>
        <li><code>kafka-consumer-groups.sh --reset-offsets</code> with <code>--to-earliest</code>, <code>--to-latest</code>, <code>--to-datetime</code>, <code>--to-offset</code>, <code>--shift-by</code>; always <code>--dry-run</code> first; the group must have no active members.</li>
        <li>Committed offsets of an empty group expire after <code>offsets.retention.minutes</code> (7 days); then <code>auto.offset.reset</code> decides again.</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of one record in the __consumer_offsets topic: key with group billing-33, topic orders-33 and partition 2; value with offset 0, leader epoch, metadata, commit timestamp and topic id.',
    t(16, 22, 'One commit record inside __consumer_offsets', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('key.type 1', 'card', 1), ('group billing-33', 'violet', 2), ('topic orders-33', 'blue', None), ('partition 2', 'blue', None)]) +
    fields(16, 72, [('offset 0', 'acc', 3), ('leaderEpoch -1', 'card', 4), ('commitTimestamp 1793895…', 'amber', 5), ('topicId 7fTJ1…', 'card', None)]) +
    legend(16, 124, [(1, 'Record type', '1 = offset commit (other types store group metadata)'),
                     (2, 'Who and where', 'group + topic + partition = the key; latest value wins (compaction)'),
                     (3, 'Offset', 'next record to read; 0 here because we reset to earliest'),
                     (4, 'Leader epoch', 'helps detect log truncation after leader changes; -1 for tool resets'),
                     (5, 'Timestamp', 'when it was committed; used for expiry')], size=8, gap=15, w=110),
    h=212, caption='Real record printed with OffsetsMessageFormatter.')
extra = '''

  <h3>Dissect a commit record</h3>
''' + DIS + '''

  <h3>The offset ruler again</h3>
''' + offset_ruler('Log start 0, committed 6, log end 10, lag 4.')

types_html = table(['Commit style', 'Code', 'Risk', 'Use'], [
    ['Auto (default)', 'enable.auto.commit=true', 'may commit before processing finishes → loss on crash', 'simple, loss-tolerant apps'],
    ['Manual sync', 'commit(asynchronous=False)', 'slower; safest order', 'after each batch'],
    ['Manual async', 'commit() (default async)', 'faster; failures not retried in order', 'high throughput + sync on shutdown'],
    ['Specific offsets', 'commit(offsets=[TopicPartition(t, p, o)])', 'you must pass “last processed + 1”', 'fine-grained control'],
], minw=640) + table(['Reset option', 'Moves the group to'], [
    ['--to-earliest / --to-latest', 'oldest retained / end'], ['--to-datetime 2026-11-05T10:00:00.000', 'first offset at or after that time'],
    ['--shift-by -50', '50 records back (clamped at log start)'], ['--to-offset 1000', 'an exact offset'],
], minw=520)
warn = 'Resetting offsets changes what a production group will process: <b>always run with --dry-run first</b>, stop all members (the tool refuses on an active group), and tell downstream teams, because a rewind re-processes data and a forward jump skips it.'

steps = [
    ('Step 1 · Read 120, commit manually',
     code('python', 'l33_offsets.py', 'c = Consumer({"bootstrap.servers": BS, "group.id": "billing-33",\n              "auto.offset.reset": "earliest", "enable.auto.commit": False})\n...                                   # read 120 records\nc.commit(asynchronous=False)\nkafka-consumer-groups.sh --describe --group billing-33', sec('== 1)', '== 2)')),
     'The 120 records came from partitions 0 and 2 only, so partition 1 has no commit (<code>-1001</code>) and is not listed. Partition 2 is fully read (lag 0); partition 0 has 86 still waiting.'),
    ('Step 2 · The app is down, lag grows',
     code('python', 'l33_offsets.py', 'produce(300 more orders)\nkafka-consumer-groups.sh --describe --group billing-33', sec('== 2)', '== 3)')),
     'Committed offsets stay where they were (14 and 106) while log end offsets grow: lag 189 and 107. No data is lost; it is waiting.'),
    ('Step 3 · Plan a rewind (dry run)',
     code('bash', 'terminal', 'kafka-consumer-groups.sh --bootstrap-server k1:9092 --reset-offsets --group billing-33 \\\n  --topic orders-33:0,2 --shift-by -50 --dry-run', sec('== 3)', '== 4)')),
     'The dry run shows the new offsets without changing anything: 106 − 50 = 56, and 14 − 50 is clamped to 0.'),
    ('Step 4 · Reset to earliest (execute)',
     code('bash', 'terminal', 'kafka-consumer-groups.sh --bootstrap-server k1:9092 --reset-offsets --group billing-33 \\\n  --topic orders-33 --to-earliest --execute', sec('== 4)', '== 5)')),
     'All three partitions now start at 0: the next run of billing will re-read everything (useful after fixing a bug).'),
    ('Step 5 · Where the bookmark lives',
     code('bash', 'terminal', 'kafka-console-consumer.sh --bootstrap-server k1:9092 --topic __consumer_offsets --from-beginning \\\n  --formatter org.apache.kafka.tools.consumer.OffsetsMessageFormatter', sec('== 5)')),
     'Each commit is an ordinary Kafka record: key = (group, topic, partition), value = offset and metadata. Compaction keeps only the latest per key.'),
]

see = [term([('committed: P0 14, P2 106, P1 none', W), ('P0  14  end 100  LAG 86', Y), ('P2 106  end 106  LAG 0', G)], size=7.0),
       term([('P0  14  end 203  LAG 189', RD), ('P2 106  end 213  LAG 107', RD)], size=7.2),
       term([('--shift-by -50 --dry-run', W), ('P2 NEW-OFFSET 56', W), ('P0 NEW-OFFSET 0', W)], size=7.2),
       term([('--to-earliest --execute', Y), ('P0 0  P1 0  P2 0', G)], size=7.2),
       term([('{"group":"billing-33",', W), (' "partition":2} -> {"offset":0,', W), (' "commitTimestamp":1793895…}', W)], size=7.0)]
def bar(c, e, title, tone):
    return t(180, 14, title, 9, bold=True) + box(20, 50, 320, 26, 'card', rx=3) + box(20, 50, 320 * c / max(e, 1), 26, 'green', rx=3) + t(20 + 320 * c / max(e, 1), 92, f'committed {c}', 7.6, 'green', bold=True) + t(340, 42, f'end {e}', 7.6, 'red', anchor='end', bold=True) + cap(f'LAG {e - c}', '', tone, y=144, h=30)
B1 = [bar(14, 100, 'Partition 0 after the commit', 'amber'), bar(14, 203, 'App down: end moves, commit stays', 'red'),
      bar(56, 213, 'Dry run on P2: 106 → 56', 'blue'), bar(0, 203, 'Reset to earliest', 'blue'),
      t(180, 14, '__consumer_offsets record', 9, bold=True) + opbox(20, 50, 'key', 'group+topic+partition', 'violet', 150, 34) + arrow(170, 67, 190, 67, 'ink3', 1) + opbox(190, 50, 'value', 'offset + metadata', 'acc', 150, 34) + cap('Latest per key wins.', '', 'violet', y=144, h=30)]
two = anim_two('Offsets, commits and lag', 'Bookmarks you can see', 'Real outputs from the lab', 'Committed vs log end', see, B1, ['Commit.', 'Lag grows.', 'Dry run.', 'Reset.', 'Storage.'], ['Saved.', 'Waiting.', 'Plan.', 'Rewind.', 'Record.'])
pe = peel('One manual commit, layer by layer', 'From your code to __consumer_offsets. (Simplified.)',
    [('Process batch', ''), ('commit()', ''), ('OffsetCommit', ''), ('Coordinator', ''), ('Offsets topic', ''), ('Restart', '')],
    [['Process batch', 'bill orders up to', 'offset 13 on P0', ''], ['commit()', 'position = 14', '(next to read)', 'sync: waits for reply'],
     ['OffsetCommit', 'request to the group', 'coordinator broker', ''], ['Coordinator', 'checks member and', 'generation, appends', 'a record (acks=all)'],
     ['Offsets topic', 'key billing-33/orders-33/0', 'value offset 14', 'replicated, compacted'], ['Restart', 'OffsetFetch on start', '→ 14', 'resume exactly there']],
    ['Work.', 'Commit.', 'Request.', 'Validate.', 'Store.', 'Resume.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Lag alert at lunch', 'Reading lag correctly. (Typical.)', ('Lag', 'Watch lag per partition, not just the total'), [
    ('Alert: lag 50,000', 'billing group', 'Panic?', 'blue'), ('Per partition view', 'one partition 49,000', 'Others near 0.', 'amber'),
    ('Cause: hot key or stuck member', 'check owner of that partition', 'Not capacity.', 'red'), ('Fix the member', 'restart / rebalance', 'Lag drains.', 'green'),
    ('Alert on lag growth', 'and time lag', 'Better signal.', 'blue')], ['Alert.', 'Breakdown.', 'Cause.', 'Fix.', 'Improve.'], 'scenario-lag') + \
       five('Real-time scenario 2', 'Replay after a GST bug', 'Rewind with --to-datetime. (Typical.)', ('Offset reset', 'Rewind one group to a time; others are untouched'), [
    ('Billing had a bug', '10:00–12:00', 'Wrong invoices.', 'red'), ('Stop billing pods', 'group must be inactive', 'Required.', 'amber'),
    ('Dry run to 10:00', '--to-datetime', 'Check new offsets.', 'green'), ('Execute and start fixed code', 're-bill 2 hours', 'Idempotent writes.', 'green'),
    ('Kitchen unaffected', 'own group', 'Isolation.', 'blue')], ['Bug.', 'Stop.', 'Dry run.', 'Replay.', 'Isolated.'], 'scenario-replay') + \
       five('Real-time scenario 3 · advanced', 'Offsets expired', 'A group idle for two weeks. (Typical.)', ('Offset retention', 'Empty groups lose commits after offsets.retention.minutes'), [
    ('Monthly report job', 'runs on the 1st', 'Idle 30 days.', 'blue'), ('Commits expired after 7 days', 'group has no offsets', 'Silent.', 'amber'),
    ('auto.offset.reset=latest', 'skips the whole month', 'Empty report!', 'red'), ('Store offsets or use earliest', 'or raise retention', 'Explicit.', 'green'),
    ('Or seek by time', 'offsetsForTimes', 'Deterministic.', 'blue')], ['Idle.', 'Expired.', 'Skipped.', 'Fix.', 'Seek.'], 'scenario-expiry')
assemble(HERE, h2_story='Where did billing stop?', hook_html=hk,
    narration='TiffinGo’s billing service went down during lunch. When it came back, it neither re-billed old orders nor skipped new ones. Riya wants to know how it remembered.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Offsets, commits and lag',
    formal='Each consumer tracks a <b>position</b>, the offset of the next record to fetch per assigned partition. <b>Committing</b> persists a position as the group’s <b>committed offset</b> in the internal compacted topic <code>__consumer_offsets</code>, via the group coordinator; it is used to resume after restarts and rebalances. Commits can be automatic (periodic) or manual (synchronous or asynchronous). <b>Consumer lag</b> is the difference between a partition’s log end offset and the group’s committed offset. Administrators can change committed offsets with <code>kafka-consumer-groups --reset-offsets</code> while the group is inactive.',
    simple='The consumer remembers “next record to read” and saves that number in Kafka (a commit). After a restart it continues from there. Lag is how many records are waiting after that number.',
    term_rows=[('Position', 'Next offset to fetch (in memory).'), ('Committed offset', 'Saved position for the group.'), ('Lag', 'Log end − committed.'), ('Auto commit', 'Background commit every 5 s.'), ('Manual commit', 'You call commit().'), ('__consumer_offsets', 'Topic storing commits.'), ('--dry-run', 'Show a reset without doing it.'), ('Offset retention', 'Expiry of idle group commits.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('The committed offset is the last record processed.', 'It is the next record to read (last processed + 1).', 'Step 4: reset to 0 means “start at record 0”.'),
               ('Offsets are stored in ZooKeeper or on the client.', 'They are records in the __consumer_offsets topic.', 'Step 5.'),
               ('High total lag always means too few consumers.', 'Often one partition is stuck or hot.', 'Step 2: lag 189 on P0 vs 107 on P2.')],
    exam='“Explain consumer offsets and lag.” Position = next to fetch; committed offset = saved position in __consumer_offsets used on restart/rebalance; lag = log end − committed; auto vs manual commit trade-offs; reset with kafka-consumer-groups --reset-offsets (dry run, inactive group).',
    types_h2='Commit styles and reset options', types_html=types_html, warn=warn,
    steps_h2='Commit, wait, rewind', steps_intro='All outputs are real: Kafka 4.4.0, 3 brokers; Python <code>confluent-kafka</code> 2.16.1; topic <code>orders-33</code> with 3 partitions; group <code>billing-33</code>. Script: <code>jobs/m3/l33_offsets.py</code>.',
    steps=steps, two=two, peel_intro='Now peel one manual commit.', peel_html=pe,
    scen_intro='Three live scenarios: a lag alert, a replay, and expired offsets.', scen=scen,
    uc_h2='Offsets at work', ucs=[uc_('ops', 'lag', 'blue', '1. Lag dashboards', 'Per-partition lag is the main health signal of every pipeline.', ['Groups', '*lag', 'Alerts']),
        uc_('fix', 'replay', 'green', '2. Bug-fix replays', 'Rewind one group by time after fixing code.', ['Bug', '*reset', 'Re-process']),
        uc_('new', 'backfill', 'violet', '3. New services', 'Start a new group at earliest to backfill history.', ['New app', '*earliest', 'History']),
        uc_('skip', 'poison', 'acc', '4. Skipping a bad record', 'Move one partition +1 past a corrupt record (with care).', ['Poison', '*--to-offset', 'Continue']),
        uc_('DR', 'mirror', 'blue', '5. Disaster recovery', 'MirrorMaker 2 translates group offsets to the backup cluster (10.4).', ['Primary', '*offset sync', 'Backup'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../01-consumers-and-consumer-groups/">3.1</a> and the offset ideas in <a href="../../01-introduction/04-topics-partitions-and-offsets/">1.4</a>.')
