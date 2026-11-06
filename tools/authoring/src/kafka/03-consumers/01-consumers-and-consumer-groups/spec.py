import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
BODY = body(HERE)
META = dict(module='03-consumers', lesson='01-consumers-and-consumer-groups', n='3.1', module_label='Module 3 · Consumers',
    title='Consumers and consumer groups',
    desc='How Kafka consumers poll and fetch, and how consumer groups share partitions through a group coordinator with heartbeats and timeouts. Real Kafka 4.4 lab: one consumer reads 600 orders in 3 polls of 200, two more members join and the 6 partitions split 2-2-2, then kafka-consumer-groups shows members, coordinator k2 and state Stable. Plus key settings, max.poll.interval.ms and static membership.',
    og_desc='600 orders in 3 polls, then 6 partitions split 2-2-2 automatically: Kafka consumer groups on a real cluster.',
    minutes=24, level='Intermediate',
    lead='How does a consumer really read, and how do several consumers share a topic without stepping on each other? We watch <b>poll()</b> return 200 records at a time, add members and see the <b>group coordinator</b> split partitions. <b>All outputs are real.</b>',
    chips=['3 polls for 600 records', 'Automatic 2-2-2 split', 'Coordinator + state', 'Runs in your browser (Python)'])
MAIN = '''# A consumer group in miniature: the coordinator splits partitions with "range"
def range_assign(partitions, members):
    members = sorted(members)
    per, extra = divmod(len(partitions), len(members))
    out, i = {}, 0
    for k, m in enumerate(members):
        n = per + (1 if k < extra else 0)
        out[m] = partitions[i:i + n]
        i += n
    return out

parts = list(range(6))
print(range_assign(parts, ["kitchen-1"]))
print(range_assign(parts, ["kitchen-1", "kitchen-2", "kitchen-3"]))
print(range_assign(parts, ["k1", "k2", "k3", "k4"]))
'''
RUN = dict(heading='Run the code: range assignment', intro='<p>The default strategy that produced our 2-2-2 split. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    per, extra = divmod(len(partitions), len(members))', 'Each member gets an equal share; the first ones get one extra.'), ('print(range_assign(parts, ["kitchen-1", "kitchen-2", "kitchen-3"]))', 'Our lab: [0,1], [2,3], [4,5].')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Then try 7 members.', code=None),
        dict(label='2 · Predict first: polls', hint='<b>Predict first:</b> 600 records, 200 per poll. How many polls?', code='print(600 // 200)\n'),
        dict(label='3 · Poll interval', hint='Will 500 records × 1 s exceed 5 minutes?', code='print(500 * 1 > 5 * 60)\n'),
        dict(label='4 · Coordinator', hint='Which offsets partition holds a group? (simplified: hash % 50)', code='print(abs(hash("kitchen-31")) % 50)\n'),
        dict(label='5 · Spot the error', hint='Member removed.', expect='error', code='seconds_since_poll, limit = 420, 300\nif seconds_since_poll > limit:\n    raise RuntimeError("max.poll.interval.ms exceeded: member left the group")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: watch a group', intro='<p>Start two consumers in two terminals with the same group, then describe. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Consumer', cmd='kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic orders-31 --group kitchen-31', file='terminal ×2', output='(each prints only its partitions)', note='Same --group.'),
           dict(title='2 · Members', cmd='kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group kitchen-31 --members', file='terminal', output='kitchen-31  kitchen-1-34f5…  /172.21.0.1  kitchen-1  2', note='One row per member.'),
           dict(title='3 · State', cmd='kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group kitchen-31 --state', file='terminal', output='kitchen-31  k2:9092 (2)  range  Stable  3', note='Coordinator and state.')])
TRACE = dict(heading='A poll loop', intro='<p>Fetch once, hand out in slices.</p>',
    code='fetched = list(range(600))\npos, polls = 0, 0\nwhile pos < len(fetched):\n    batch = fetched[pos:pos + 200]\n    pos += len(batch)\n    polls += 1\nprint(polls, "polls")\n',
    notes={4: 'Slice :: One poll returns up to 200.', 7: 'Done :: 3 polls.'})
WORKED_INTRO = 'Three consumer-group decisions.'
EXAMPLES = [
    dict(level='b', tag='Consumer · basics', title='A clean poll loop', problem='<p>Read orders and stop cleanly.</p>', inp='topic, group',
         approach=['subscribe.', 'poll/consume in a loop.', 'close() on exit (leaves the group fast).'], code='loop = ["subscribe", "while running: msgs = consume(100, 1.0); process(msgs)", "close()"]\nprint("\\n".join(loop))\n', notes={1: 'close() :: Avoids waiting for the session timeout.'}, tryit='Step 1.'),
    dict(level='i', tag='Consumer · tuning', title='Fit work inside the poll interval', problem='<p>Each record needs a 200 ms API call.</p>', inp='timings',
         approach=['Records per poll × time < max.poll.interval.', 'Lower max.poll.records.', 'Or use worker threads.'], code='per, limit_s = 0.2, 300\nprint("max records per poll:", int(limit_s / per * 0.5), "(50% safety)")\n', notes={1: 'Budget :: Leave headroom.'}, tryit='Scenario 1.'),
    dict(level='a', tag='Consumer · deploys', title='Static membership', problem='<p>Deploys cause rebalance storms.</p>', inp='pods',
         approach=['group.instance.id = pod name.', 'session.timeout > restart time.', 'Rolling restart.'], code='print({"group.instance.id": "kitchen-pod-3", "session.timeout.ms": 60000})\n', notes={1: 'Identity :: Partitions stay with the pod.'}, tryit='Scenario 2.')]
QUIZ = mix([
    dict(q='Beginner: A consumer gets data by…', options=['Kafka pushing', 'Polling (pulling)', 'Email', 'ZooKeeper'], answer=1, why='Pull model.'),
    dict(q='Beginner: Consumers become one team by sharing…', options=['client.id', 'group.id', 'topic name only', 'host'], answer=1, why='Same group.'),
    dict(q='Beginner: 6 partitions, 3 members →', options=['6 each', '2 each', '1 each', '3 each'], answer=1, why='Step 2.'),
    dict(q='Intermediate: Who assigns partitions to members?', options=['The producer', 'The group coordinator (with the strategy)', 'ZooKeeper', 'The consumer alone'], answer=1, why='Broker k2 here.'),
    dict(q='Intermediate: The group coordinator is…', options=['A special server', 'Leader of the group’s __consumer_offsets partition', 'The controller', 'Random'], answer=1, why='Hash of group id.'),
    dict(q='Intermediate: Default auto.offset.reset is…', options=['earliest', 'latest', 'none', 'middle'], answer=1, why='New groups start at the end.'),
    dict(q='Advanced: Not polling for longer than max.poll.interval.ms →', options=['Nothing', 'Member leaves; rebalance', 'Data deleted', 'Broker restarts'], answer=1, why='Scenario 1.'),
    dict(q='Advanced: group.instance.id gives…', options=['Faster fetch', 'Static membership (no rebalance on quick restart)', 'Compression', 'Exactly-once'], answer=1, why='Scenario 2.')])
REVISION = ['Consumers pull; client fetches batches; poll/consume hands them out.', 'Lab: 600 records in 3 polls of 200.', 'Same group.id → coordinator assigns partitions (range: 2-2-2).',
    'Coordinator = leader of hash(group) partition of __consumer_offsets (k2 here); state Stable.', 'Liveness: heartbeats (session.timeout 45 s) + poll within max.poll.interval (5 min).', 'Static membership: group.instance.id.']
FAQ = [('Can one consumer read several topics?', 'Yes: subscribe(["a", "b"]) or a regex pattern; partitions of all topics are assigned within the group.'),
    ('Is a consumer thread-safe?', 'No. Use one consumer per thread; the confluent-kafka and Java consumers must not be shared across threads.'),
    ('What does auto.offset.reset=none do?', 'Throws an error if the group has no committed offset, forcing you to decide explicitly.'),
    ('Why set client.id?', 'It appears in group descriptions, logs and metrics, so you can tell which pod owns which partitions.')]
PRACTICE_INTRO = 'Consumer group programs.'
PROBLEMS = [
    dict(level='easy', title='Share', stmt='Partitions per member.', inp='6, 3', code='print(6 // 3)\n', explain='2.'),
    dict(level='easy', title='Idle', stmt='Idle members.', inp='6 partitions, 8 members', code='print(max(0, 8 - 6))\n', explain='2 idle.'),
    dict(level='easy', title='Polls', stmt='Polls for 1,000 records at 500 each.', inp='numbers', code='print(-(-1000 // 500))\n', explain='2.'),
    dict(level='medium', title='Range', stmt='Range assign 7 partitions to 3.', inp='7, 3', code='per, ex = divmod(7, 3)\nprint([per + (1 if i < ex else 0) for i in range(3)])\n', explain='[3, 2, 2].'),
    dict(level='medium', title='Round robin', stmt='Assign 7 partitions round-robin.', inp='7, 3', code='print({m: [p for p in range(7) if p % 3 == m] for m in range(3)})\n', explain='Another strategy.'),
    dict(level='medium', title='Poll budget', stmt='Max records per poll at 0.5 s each within 300 s, 50% headroom.', inp='numbers', code='print(int(300 / 0.5 * 0.5))\n', explain='300.'),
    dict(level='business', title='Throughput', stmt='3 members × 200 orders/s each.', inp='numbers', code='print(3 * 200, "orders/s")\n', explain='Scale out.'),
    dict(level='business', title='Max members', stmt='Useful members for a 12-partition topic.', inp='12', code='print(12)\n', explain='More are idle.')]
SCN_INTRO = 'Consumer interview questions.'
SCENARIOS = (scn('Any company · backend', 'Fresher', '“What is a consumer group?”', 'Explain.', 'answer?', '<p>Consumers sharing a group.id; the coordinator assigns each partition to one member so work is shared and fails over; each group keeps its own committed offsets, so different groups each get all records.</p>', '“Consumers on the same machine.”') +
    scn('Food delivery', 'Mid-level', 'Rebalance loop', 'A group keeps rebalancing every few minutes.', 'diagnose?', '<ul><li>Members exceed max.poll.interval.ms (slow processing).</li><li>Check logs for leaving the group.</li><li>Smaller batches or async workers.</li></ul>', 'Raising partitions.') +
    scn('Data engineering', 'Mid-level', 'Scaling', 'Lag grows; there are 4 partitions and 4 consumers.', 'plan?', '<ul><li>More consumers won’t help.</li><li>Add partitions (watch keys) or speed up processing.</li><li>Check per-partition lag for hot keys.</li></ul>', '“Add 4 more pods.”') +
    scn('Platform', 'Senior', 'Deploys', 'Rolling deploys cause minutes of paused consumption.', 'design?', '<ul><li>Static membership.</li><li>Cooperative or KIP-848 protocol (3.2).</li><li>Graceful close().</li></ul>', 'Deploying all pods at once.'))
