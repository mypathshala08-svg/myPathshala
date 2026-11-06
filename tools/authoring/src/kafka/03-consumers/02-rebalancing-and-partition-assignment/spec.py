import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
BODY = body(HERE)
META = dict(module='03-consumers', lesson='02-rebalancing-and-partition-assignment', n='3.2', module_label='Module 3 · Consumers',
    title='Rebalancing and partition assignment',
    desc='What triggers a Kafka consumer group rebalance and how partitions are reassigned: eager vs cooperative-sticky strategies in the classic protocol and the new server-side consumer protocol (KIP-848, production-ready in Kafka 4.0). Real Kafka 4.4 lab with live traffic: when a third consumer joins, eager takes away all 6 partitions, cooperative and KIP-848 only 2.',
    og_desc='One consumer joins: eager revokes 6 of 6 partitions, cooperative and KIP-848 only 2. Rebalancing measured on Kafka 4.4.',
    minutes=26, level='Intermediate',
    lead='When a consumer joins or leaves, partitions must move. We run the <b>same join</b> under the <b>eager</b>, <b>cooperative-sticky</b> and Kafka 4’s new <b>consumer protocol</b> with live traffic and count what stops. <b>All outputs are real.</b>',
    chips=['Eager vs cooperative', 'KIP-848 consumer protocol', 'Callbacks logged', 'Runs in your browser (Python)'])
MAIN = '''# Eager vs sticky/cooperative: which partitions must move when C joins?
def range_plan(members, parts=6):
    per, extra = divmod(parts, len(members)); out, i = {}, 0
    for k, m in enumerate(sorted(members)):
        n = per + (k < extra); out[m] = list(range(i, i + n)); i += n
    return out

def sticky_plan(old, members, parts=6):
    target = parts // len(members)
    new = {m: list(old.get(m, []))[:target] for m in members}
    free = [p for p in range(parts) if not any(p in v for v in new.values())]
    for m in members:
        while len(new[m]) < target and free: new[m].append(free.pop(0))
    return new

before = {"A": [0, 1, 2], "B": [3, 4, 5]}
eager = range_plan(["A", "B", "C"])
sticky = sticky_plan(before, ["A", "B", "C"])
moved = lambda plan: sum(1 for m, ps in before.items() for p in ps if p not in plan[m])
print("eager :", eager, "moved:", moved(eager), "| but ALL 6 were revoked first")
print("sticky:", sticky, "moved:", moved(sticky))
'''
RUN = dict(heading='Run the code: what must move?', intro='<p>Compare plans when C joins. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    new = {m: list(old.get(m, []))[:target] for m in members}', 'Sticky: keep as many old partitions as possible.'), ('print("eager :", eager, "moved:", moved(eager), "| but ALL 6 were revoked first")', 'Eager revokes everything, even partitions that come back.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Then add member D.', code=None),
        dict(label='2 · Predict first: moves', hint='<b>Predict first:</b> 6 partitions, 2 → 3 members, minimum partitions that must move?', code='print(6 - 2 * (6 // 3))\n'),
        dict(label='3 · Leave', hint='B leaves: sticky plan for A and C.', code='before = {"A": [0, 1], "B": [2, 3], "C": [4, 5]}\nfree = before.pop("B")\nbefore["A"].append(free[0]); before["C"].append(free[1])\nprint(before)\n'),
        dict(label='4 · Pause cost', hint='Eager pause 2 s × 20 rebalances/day.', code='print(2 * 20, "seconds of full stop per day")\n'),
        dict(label='5 · Spot the error', hint='Mixed strategies.', expect='error', code='members = {"A": "range", "B": "cooperative-sticky"}\nif len(set(members.values())) > 1:\n    raise RuntimeError("no common assignment strategy: migrate with a rolling bounce listing both")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: choose a protocol', intro='<p>Python confluent-kafka 2.16+ against Kafka 4.x. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Cooperative', cmd='Consumer({..., "group.protocol": "classic", "partition.assignment.strategy": "cooperative-sticky"})', file='python', output='B revoked [1]  A revoked [0]  … C assigned [0, 1]', note='Use incremental_assign in callbacks.'),
           dict(title='2 · KIP-848', cmd='Consumer({..., "group.protocol": "consumer"})', file='python', output='A revoked [5]  B revoked [2]  C assigned [2, 5]', note='Broker computes the plan.'),
           dict(title='3 · Group type', cmd='kafka-groups.sh --bootstrap-server localhost:9092 --list', file='terminal', output='GROUP  TYPE  PROTOCOL\ng-consumer  Consumer  consumer', note='Shows protocol per group.')])
TRACE = dict(heading='Eager rebalance steps', intro='<p>Revoke all, then reassign.</p>',
    code='owned = {"A": [0, 1, 2], "B": [3, 4, 5]}\nrevoked = sum(len(v) for v in owned.values())\nowned = {m: [] for m in owned}\nowned = {"A": [0, 1], "B": [2, 3], "C": [4, 5]}\nprint(revoked, owned)\n',
    notes={3: 'Barrier :: Everyone empty: no processing.', 4: 'Reassign :: New plan, everyone resumes.'})
WORKED_INTRO = 'Three rebalancing decisions.'
EXAMPLES = [
    dict(level='b', tag='Rebalance · hooks', title='Commit before losing partitions', problem='<p>Re-processing after every rebalance.</p>', inp='callbacks',
         approach=['on_revoke: commit synchronously.', 'on_assign: log/load state.', 'Keep hooks fast.'], code='def on_revoke(consumer, parts):\n    print("commit before release:", [p for p in parts])   # consumer.commit(asynchronous=False)\non_revoke(None, [0, 1])\n', notes={1: 'Hook :: Last chance to save progress.'}, tryit='Scenario 2.'),
    dict(level='i', tag='Rebalance · migration', title='Move a group to cooperative', problem='<p>Eager group in production.</p>', inp='strategy',
         approach=['Bounce 1: strategy = cooperative-sticky,range.', 'Bounce 2: cooperative-sticky only.', 'Watch lag.'], code='print(["cooperative-sticky,range", "cooperative-sticky"])\n', notes={1: 'Two bounces :: Safe migration.'}, tryit='Warn box.'),
    dict(level='a', tag='Rebalance · KIP-848', title='Adopt the consumer protocol', problem='<p>Kafka 4 cluster, many groups.</p>', inp='versions',
         approach=['Brokers 4.0+.', 'Clients supporting group.protocol=consumer.', 'Roll members; tune group.consumer.* on the broker.'], code='print({"group.protocol": "consumer"}, "| broker: group.consumer.assignors=uniform,range")\n', notes={1: 'Server-side :: Fewer client knobs.'}, tryit='Step 3.')]
QUIZ = mix([
    dict(q='Beginner: A rebalance happens when…', options=['A record is produced', 'Group membership or subscriptions change', 'Every hour', 'Retention runs'], answer=1, why='Join, leave, crash, slow poll.'),
    dict(q='Beginner: Eager rebalancing…', options=['Moves nothing', 'Revokes all partitions from all members', 'Only affects the new member', 'Deletes offsets'], answer=1, why='6 of 6.'),
    dict(q='Beginner: Cooperative-sticky revoked how many in our lab?', options=['6', '2', '0', '4'], answer=1, why='Step 2.'),
    dict(q='Intermediate: In the classic protocol, who computes the assignment?', options=['The broker', 'The group leader (a client)', 'ZooKeeper', 'The producer'], answer=1, why='Client-side.'),
    dict(q='Intermediate: KIP-848 is enabled with…', options=['group.protocol=consumer', 'acks=all', 'enable.idempotence', 'linger.ms'], answer=0, why='Kafka 4.0+.'),
    dict(q='Intermediate: Best place to commit before losing partitions?', options=['on_assign', 'on_revoke', 'Never', 'In the producer'], answer=1, why='Before release.'),
    dict(q='Advanced: In KIP-848, assignments are computed by…', options=['Each member', 'The group coordinator broker (server-side assignor)', 'Controllers only', 'Clients voting'], answer=1, why='uniform / range.'),
    dict(q='Advanced: Why did cooperative need a second round 3 s later?', options=['Error', 'Freed partitions are assigned after revocation completes', 'Retention', 'Compression'], answer=1, why='Incremental protocol.')])
REVISION = ['Rebalance = reassign partitions on join/leave/crash/slow poll/subscription change.', 'Eager (range, roundrobin, sticky): revoke all → reassign (lab: 6 of 6).',
    'Cooperative-sticky: revoke only moved (lab: 2 of 6, second round +3 s).', 'KIP-848 consumer protocol (4.0+): broker assigns, members reconcile (lab: 2 of 6).',
    'Hooks: commit in on_revoke; load state in on_assign.', 'Reduce rebalances: static membership, fast polls, graceful close.']
FAQ = [('Which strategy is the default?', 'In the Java classic consumer the default list is [range, cooperative-sticky], which behaves eagerly until all members support cooperative; librdkafka defaults to range,roundrobin. Set it explicitly.'),
    ('Is KIP-848 the default in Kafka 4?', 'Brokers support it, but clients still default to group.protocol=classic; you opt in per consumer.'),
    ('Do rebalances lose data?', 'No; records stay in Kafka. But uncommitted progress may be re-processed by the new owner.'),
    ('Does Kafka Streams use this?', 'Kafka Streams has its own assignor on the classic protocol and a new streams rebalance protocol (KIP-1071) in recent versions.')]
PRACTICE_INTRO = 'Rebalance programs.'
PROBLEMS = [
    dict(level='easy', title='Moved count', stmt='Partitions moved: 6 → plan 2-2-2 from 3-3.', inp='plans', code='print(6 - 2 - 2)\n', explain='2 must move.'),
    dict(level='easy', title='Eager revoked', stmt='Revoked in eager with 3 members of 2 each.', inp='6', code='print(6)\n', explain='All.'),
    dict(level='easy', title='Pause share', stmt='2 of 6 partitions paused.', inp='2, 6', code='print(round(100 * 2 / 6), "%")\n', explain='33% vs 100%.'),
    dict(level='medium', title='Range plan', stmt='Range for 6 partitions and 4 members.', inp='6, 4', code='per, ex = divmod(6, 4)\nprint([per + (i < ex) for i in range(4)])\n', explain='[2, 2, 1, 1].'),
    dict(level='medium', title='Sticky keep', stmt='Keep old partitions up to target.', inp='old', code='old, target = [0, 1, 2], 2\nprint(old[:target], "kept;", old[target:], "released")\n', explain='Release one.'),
    dict(level='medium', title='Diff plans', stmt='Partitions that changed owner.', inp='two plans', code='a = {0: "A", 1: "A", 2: "B"}\nb = {0: "A", 1: "C", 2: "B"}\nprint([p for p in a if a[p] != b[p]])\n', explain='[1].'),
    dict(level='business', title='Lag cost', stmt='Eager pause 5 s × 100 msg/s × 6 partitions.', inp='numbers', code='print(5 * 100 * 6, "messages delayed")\n', explain='Per rebalance.'),
    dict(level='business', title='Daily rebalances', stmt='30 deploy restarts/day × 2 s.', inp='numbers', code='print(30 * 2, "s of full stop")\n', explain='Avoidable.')]
SCN_INTRO = 'Rebalancing interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“What is a consumer rebalance?”', 'Explain.', 'answer?', '<p>Reassigning partitions among group members when someone joins, leaves, crashes or stops polling. Eager strategies revoke everything first; cooperative and the new KIP-848 protocol move only what must move.</p>', '“Moving data between brokers.”') +
    scn('Food delivery', 'Mid-level', 'Pauses on deploy', 'Every deploy pauses all consumers.', 'fix?', '<ul><li>cooperative-sticky or group.protocol=consumer.</li><li>Static membership.</li><li>Graceful close and commit on revoke.</li></ul>', 'Deploying less often.') +
    scn('Data engineering', 'Mid-level', 'Duplicates after rebalance', 'Some records processed twice after scaling.', 'cause?', '<ul><li>Uncommitted progress re-read by the new owner.</li><li>Commit in on_revoke; idempotent processing.</li></ul>', '“Kafka sent them twice.”') +
    scn('Platform', 'Senior', 'Large groups', 'A group of 200 members rebalances slowly.', 'design?', '<ul><li>KIP-848: server-side, incremental.</li><li>Static membership.</li><li>Split into smaller groups/topics if needed.</li></ul>', 'Increasing session timeouts only.'))
