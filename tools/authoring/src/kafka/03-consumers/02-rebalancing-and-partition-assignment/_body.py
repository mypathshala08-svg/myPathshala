import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l32_rebalance.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('A third worker joined. Under one protocol, all 6 partitions were taken away. Under another, only 2. Same Kafka.',
    'A <b>rebalance</b> moves partitions between consumers when someone joins or leaves. The old “eager” way stops everyone; the “cooperative” way and Kafka 4’s new <b>consumer protocol</b> (KIP-848) move only what must move. We ran all three on the same cluster with live traffic.',
    ['What triggers a rebalance, and who decides the new assignment.',
     'Why eager rebalancing pauses the whole group.',
     'How Kafka 4’s server-side protocol changes the game.'])
cmap = concept_map('Concept map. Beginner: rebalance, join, leave. Intermediate: assignment strategies, eager vs cooperative, revoke and assign callbacks. Advanced: KIP-848 consumer protocol, server-side assignors, static membership.',
    [[('rb', 'Rebalance', 'move partitions', None), ('jn', 'Member joins/leaves', 'or crashes', None), ('cb', 'on_assign / on_revoke', 'your hooks', None)],
     [('st', 'Assignment strategies', 'range, round-robin, sticky', None), ('eg', 'Eager', 'stop the world', None), ('cs', 'Cooperative-sticky', 'incremental', None), ('cm', 'Commit on revoke', 'Lesson 3.3', B + '03-consumers/03-offsets-commits-and-lag/')],
     [('k8', 'KIP-848 protocol', 'group.protocol=consumer', None), ('sa', 'Server-side assignors', 'uniform, range', None), ('sm', 'Static membership', 'Lesson 3.1', B + '03-consumers/01-consumers-and-consumer-groups/')]],
    [('jn', 'rb'), ('rb', 'st'), ('st', 'eg'), ('st', 'cs'), ('cb', 'cm'), ('cs', 'k8'), ('k8', 'sa'), ('rb', 'sm')],
    {'rb', 'jn', 'cb', 'st', 'eg', 'cs', 'k8'},
    '<b>Builds on:</b> <a href="../01-consumers-and-consumer-groups/">3.1</a>. <b>Next:</b> <a href="../03-offsets-commits-and-lag/">3.3 Offsets, commits and lag</a>.')
whw = why_how_where(
    'Members come and go (scaling, deploys, crashes). Partitions must be re-shared so none is orphaned and none is read twice.',
    'The group coordinator detects the change; partitions are revoked from some members and assigned to others, by the client (classic) or by the broker (consumer protocol).',
    'Autoscaling consumer pods, rolling deploys, crashed workers, new topics matching a pattern.',
    'Frequent rebalances (flapping members, slow polls) hurt throughput; fix the cause instead of tuning around it.')

sc_ = ''
for k, (title, revoked, tone) in enumerate([('classic eager', 6, 'red'), ('classic cooperative', 2, 'green'), ('consumer (KIP-848)', 2, 'green')]):
    x = 14 + k * 208
    sc_ += box(x, 22, 196, 112, 'card', rx=8) + t(x + 98, 40, title, 8.6, bold=True)
    sc_ += ''.join(box(x + 14 + i * 29, 54, 24, 24, tone if i < revoked else 'blue', rx=3) + t(x + 26 + i * 29, 70, f'P{i}', 7, 'ink') for i in range(6))
    sc_ += t(x + 98, 100, f'{revoked} of 6 partitions taken away', 8, tone, bold=True) + t(x + 98, 118, 'from A and B when C joined', 7.4, 'ink2')
scene_svg = scene('When consumer C joined a group of A and B on a 6-partition topic: classic eager took all 6 partitions away, classic cooperative-sticky took only 2, and the new consumer protocol took only 2.', sc_,
                  'Same event, very different <tspan font-weight="700" class="s-acc">disruption</tspan>.')
dialogue = '''K> Sir, every time a kitchen pod restarts, all consumers stop for a moment. Why should pod 1 stop when pod 3 restarts?
A> Because the group is using the old <b>eager</b> protocol: on every change, every member gives back <i>all</i> its partitions and waits for a new plan.
R> Is there a better way?
A> Two. <b>Cooperative-sticky</b> moves only the partitions that must move. And Kafka 4 made the new <b>consumer protocol</b> production-ready: the broker computes assignments and reconciles members one by one. We will run all three with live traffic.'''

lv = '''
LEVELS> Rebalancing at three levels
L1> Reshuffling counters
      <ul>
        <li>A new cook joins. Eager: everyone leaves their counter, the manager reassigns all counters, everyone walks back. Cooperative: only two cooks hand over one counter each; the rest keep cooking.</li>
      </ul>
L2> Classic protocol (client-side)
      <ul>
        <li>Triggers: a member joins, leaves, crashes (no heartbeat), exceeds the poll interval, or the subscribed topics change.</li>
        <li>One member, the <b>leader</b> of the group, runs the assignment strategy (<code>partition.assignment.strategy</code>): <code>range</code>, <code>roundrobin</code>, <code>sticky</code> (eager) or <code>cooperative-sticky</code> (incremental, KIP-429).</li>
        <li>Your hooks: <code>on_revoke</code> (commit offsets, flush state) and <code>on_assign</code> (load state). With cooperative mode you call <code>incremental_assign/unassign</code>.</li>
      </ul>
L3> Consumer protocol (KIP-848, production-ready in Kafka 4.0)
      <ul>
        <li>Enable with <code>group.protocol=consumer</code>. The <b>broker</b> computes assignments (server-side assignors <code>uniform</code> or <code>range</code>) and sends each member its target through heartbeats.</li>
        <li>Members reconcile independently: a partition is first revoked from its old owner, then given to the new one. No global “stop the world” barrier, no group-wide sync.</li>
        <li>Client-side settings like <code>partition.assignment.strategy</code> and <code>session.timeout.ms</code> are replaced by broker/group configs (e.g. <code>group.consumer.session.timeout.ms</code>).</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of the eager rebalance log lines from our lab: A revoked partitions 0 to 2, B revoked 3 to 5, then A assigned 0 and 1, C assigned 4 and 5, B assigned 2 and 3, all within 20 milliseconds.',
    t(16, 22, 'Eager rebalance, as our callbacks logged it (time relative to C joining)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('-0.01s B revoked [3, 4, 5]', 'red', 1), ('-0.01s A revoked [0, 1, 2]', 'red', None)]) +
    fields(16, 70, [('-0.00s A assigned [0, 1]', 'green', 2), ('+0.00s C assigned [4, 5]', 'green', 3), ('+0.00s B assigned [2, 3]', 'green', None)]) +
    legend(16, 124, [(1, 'Revoke everything', 'eager: every member gives back all partitions first'),
                     (2, 'Reassign', 'the group leader’s range strategy computes a fresh plan'),
                     (3, 'Newcomer', 'C gets 4 and 5; B’s partitions moved from [3,4,5] to [2,3]')], size=8, gap=15, w=130),
    h=184, caption='Real callback log from our run.')
extra = '''

  <h3>Dissect an eager rebalance</h3>
''' + DIS

types_html = table(['Protocol / strategy', 'Who assigns', 'Partitions paused on a join', 'Notes'], [
    ['classic + range / roundrobin', 'group leader (client)', 'all of them (eager)', 'simple, disruptive'],
    ['classic + sticky', 'client', 'all revoked, mostly same returned', 'eager, keeps locality'],
    ['classic + cooperative-sticky', 'client', 'only the moved ones', 'two rounds (we saw a 3 s second step)'],
    ['consumer (KIP-848)', 'broker (uniform / range)', 'only the moved ones', 'Kafka 4.0+ brokers and clients'],
], minw=640)
warn = 'Do not mix eager and cooperative strategies blindly in one group; migrate with a rolling bounce that lists both (e.g. <code>cooperative-sticky,range</code>) and then remove the old one. For the consumer protocol, upgrade brokers and clients first; a classic group can be converted when all members switch.'

steps = [
    ('Step 1 · Eager (classic + range)',
     code('python', 'l32_rebalance.py', 'MODES["eager"] = {"group.protocol": "classic", "partition.assignment.strategy": "range"}\n# A and B consume 6 partitions while a producer sends 100 msg/s; C joins after 14 s', sec('== eager', '== cooperative')),
     'At the moment C joined, A and B gave back <b>all 6</b> partitions and received a fresh plan 10–20 ms later. B even changed from [3,4,5] to [2,3]. On our tiny topic the pause was a fraction of a second; with state to save, slow callbacks or many members it can be seconds to minutes.'),
    ('Step 2 · Cooperative-sticky',
     code('python', 'l32_rebalance.py', 'MODES["cooperative"] = {"group.protocol": "classic", "partition.assignment.strategy": "cooperative-sticky"}\n# callbacks use incremental_assign / incremental_unassign', sec('== cooperative', '== consumer')),
     'Only one partition each left A and B. They kept processing the other two. A second round 3 s later handed the freed partitions 0 and 1 to C: two partitions were unowned for those 3 seconds, everything else ran on.'),
    ('Step 3 · The new consumer protocol (KIP-848)',
     code('python', 'l32_rebalance.py', 'MODES["consumer"] = {"group.protocol": "consumer"}   # broker computes assignments', sec('== consumer')),
     'The broker decided: A gave up 5, B gave up 2, then C received [2, 5]. Again only 2 of 6 moved. The revocations happened about 4 s before C’s assignment arrived on its next heartbeat: members reconcile one at a time, without a group-wide barrier.'),
]

see = [term([('A revoked [0, 1, 2]', RD), ('B revoked [3, 4, 5]', RD), ('A [0,1]  C [4,5]  B [2,3]', W), ('taken away: 6 of 6', RD)], size=7.0),
       term([('B revoked [1]   A revoked [0]', Y), ('+3.01s C assigned [0, 1]', G), ('taken away: 2 of 6', G)], size=7.0),
       term([('A revoked [5]   B revoked [2]', Y), ('C assigned [2, 5]', G), ('taken away: 2 of 6', G)], size=7.0)]
def grid(owner, title, tone):
    col = {'A': 'blue', 'B': 'violet', 'C': 'green', '-': 'red'}
    return t(180, 14, title, 9, bold=True) + ''.join(box(30 + i * 50, 50, 44, 34, col[o], rx=4) + t(52 + i * 50, 66, f'P{i}', 7.6, 'ink', bold=True) + t(52 + i * 50, 78, o if o != '-' else 'paused', 7, 'ink2') for i, o in enumerate(owner))
B1 = [grid('------', 'Eager: everyone stops', 'red') + cap('All 6 revoked, then reassigned.', '', 'red', y=144, h=30),
      grid('-A-BAB'.replace('-A-BAB', '--ABAB'), 'Cooperative: two pause', 'green') + cap('Moved partitions only.', '', 'green', y=144, h=30),
      grid('BBCAAC', 'Consumer protocol: broker plans', 'green') + cap('Incremental, no barrier.', '', 'green', y=144, h=30)]
two = anim_two('Rebalancing', 'Three protocols, one join', 'Real outputs from the lab', 'Which partitions paused', see, B1, ['Eager.', 'Cooperative.', 'KIP-848.'], ['Stop all.', 'Move two.', 'Server-side.'])
pe = peel('A member joins under KIP-848', 'Server-side reconciliation, step by step. (Simplified.)',
    [('C heartbeats', ''), ('Broker plans', ''), ('Revoke targets', ''), ('A and B release', ''), ('C receives', ''), ('Stable', '')],
    [['C heartbeats', 'ConsumerGroupHeartbeat', '“I subscribe to reb-…”', 'gets a member id'], ['Broker plans', 'group epoch +1', 'uniform assignor:', 'target 2-2-2'],
     ['Revoke targets', 'A must drop P5', 'B must drop P2', '(on their next heartbeat)'], ['A and B release', 'commit + on_revoke', 'acknowledge in heartbeat', 'keep other partitions'],
     ['C receives', 'P2 and P5', 'once they are free', 'starts fetching'], ['Stable', 'all members at', 'target assignment', 'no global pause']],
    ['Join.', 'Plan.', 'Revoke.', 'Release.', 'Assign.', 'Stable.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Autoscaling storms', 'Eager rebalances during traffic spikes. (Typical.)', ('Incremental rebalancing', 'Use cooperative-sticky or the consumer protocol'), [
    ('Autoscaler adds 1 pod/min', '12 pods, eager range', 'Every add = full stop.', 'red'), ('All partitions paused', 'lag spikes each minute', 'Bad at peak.', 'red'),
    ('Switch to cooperative', 'rolling migration', 'Two-step.', 'green'), ('Or consumer protocol', 'Kafka 4 brokers + clients', 'Server-side.', 'green'),
    ('Only moved partitions pause', 'smooth scaling', 'Fixed.', 'blue')], ['Scale.', 'Pause.', 'Cooperative.', 'KIP-848.', 'Smooth.'], 'scenario-autoscale') + \
       five('Real-time scenario 2', 'Lost work during revoke', 'Not committing in on_revoke. (Typical.)', ('Revoke hook', 'Commit processed offsets before giving a partition away'), [
    ('Member processed 400 records', 'auto-commit every 5 s', 'Not yet committed.', 'blue'), ('Partition revoked', 'new owner starts at last commit', 'Re-processes 400.', 'red'),
    ('Duplicates downstream', 'double SMS', 'Complaints.', 'red'), ('Commit in on_revoke', 'synchronously', 'Before release.', 'green'),
    ('Minimal re-processing', 'only in-flight records', 'Better.', 'blue')], ['Work.', 'Revoke.', 'Dupes.', 'Hook.', 'Better.'], 'scenario-revoke') + \
       five('Real-time scenario 3 · advanced', 'Stateful consumers', 'Moving local state with partitions. (Typical.)', ('Sticky assignment', 'Keep partitions where their state is'), [
    ('Fraud detector keeps windows', 'per partition in memory', 'State is local.', 'blue'), ('Eager range rebalance', 'partitions shuffle', 'State lost/rebuilt.', 'red'),
    ('Sticky / cooperative', 'most stay put', 'State kept.', 'green'), ('on_assign loads state', 'from a store or topic', 'Recover.', 'green'),
    ('Kafka Streams does this', 'state stores + changelogs', 'Module 9.', 'blue')], ['State.', 'Shuffle.', 'Sticky.', 'Restore.', 'Streams.'], 'scenario-stateful')
assemble(HERE, h2_story='Why does everyone stop when one pod restarts?', hook_html=hk,
    narration='TiffinGo autoscales its kitchen consumers. Every time a pod is added or restarted, all pods pause for a moment and lag jumps. Kabir wants to know whether this is unavoidable.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Rebalancing and partition assignment',
    formal='A <b>rebalance</b> redistributes partitions among the members of a consumer group when membership or subscriptions change. In the <b>classic</b> protocol, members rejoin via the coordinator and the elected group leader computes an assignment using the configured <code>partition.assignment.strategy</code>; <b>eager</b> strategies revoke all partitions from all members first, while <b>cooperative</b> (incremental) strategies revoke only partitions that move, completing in additional rounds. In the <b>consumer</b> protocol (KIP-848, production-ready in Kafka 4.0) the group coordinator computes target assignments server-side and members reconcile incrementally through heartbeats.',
    simple='When consumers join or leave, Kafka re-shares the partitions. The old way makes everyone hand back everything; newer ways only move the partitions that need a new owner, so the rest keep working.',
    term_rows=[('Rebalance', 'Re-sharing partitions in a group.'), ('Eager', 'Revoke all, then reassign.'), ('Cooperative', 'Revoke only what moves.'), ('Group leader', 'Member computing the plan (classic).'), ('on_revoke', 'Hook before losing partitions.'), ('on_assign', 'Hook after getting partitions.'), ('KIP-848', 'New server-side consumer protocol.'), ('Assignor', 'Algorithm that builds the plan.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Every rebalance stops the whole group.', 'Only eager strategies do; cooperative and KIP-848 move a few partitions.', 'Steps 1–3: 6 vs 2 vs 2 partitions taken away.'),
               ('The broker always decides assignments.', 'In the classic protocol a client (the group leader) decides; in KIP-848 the broker does.', 'Types table.'),
               ('Rebalances only happen when consumers crash.', 'Joins, leaves, slow polls and subscription changes also trigger them.', 'Step 1: a join triggered it.')],
    exam='“What is a rebalance and how do you reduce its impact?” Partition reassignment on membership change. Use cooperative-sticky or group.protocol=consumer (KIP-848) for incremental moves, static membership for restarts, commit in on_revoke, and keep polls within max.poll.interval.ms.',
    types_h2='Protocols and strategies', types_html=types_html, warn=warn,
    steps_h2='One join, three protocols', steps_intro='All outputs are real: Kafka 4.4.0, 3 brokers; Python <code>confluent-kafka</code> 2.16.1. A producer sends 100 messages/s to 6 partitions; consumers A and B run; C joins after 14 s. Times are relative to C joining. Script: <code>jobs/m3/l32_rebalance.py</code>.',
    steps=steps, two=two, peel_intro='Now peel a KIP-848 join.', peel_html=pe,
    scen_intro='Three live scenarios: autoscaling, lost work on revoke, and stateful consumers.', scen=scen,
    uc_h2='Rebalancing at work', ucs=[uc_('k8s', 'scale', 'blue', '1. Autoscaled consumers', 'Incremental rebalancing keeps lag flat while pods scale.', ['Pods', '*cooperative', 'Smooth']),
        uc_('ops', 'deploy', 'green', '2. Rolling deploys', 'Static membership + KIP-848 avoid storms.', ['Deploy', '*static', 'No pause']),
        uc_('state', 'windows', 'violet', '3. Stateful processors', 'Sticky assignment keeps local state useful.', ['State', '*sticky', 'Fast restart']),
        uc_('ETL', 'connect', 'acc', '4. Kafka Connect', 'Connect workers also rebalance tasks incrementally.', ['Tasks', '*incremental', 'Connectors']),
        uc_('regex', 'topics', 'blue', '5. Pattern subscriptions', 'New matching topics trigger a rebalance to add them.', ['New topic', '*rebalance', 'Consumed'])],
    uc_note='Pause lengths depend on group size and callbacks; our lab topic was small.',
    pre='<b>Before you start:</b> <a href="../01-consumers-and-consumer-groups/">3.1 Consumers and consumer groups</a>.')
