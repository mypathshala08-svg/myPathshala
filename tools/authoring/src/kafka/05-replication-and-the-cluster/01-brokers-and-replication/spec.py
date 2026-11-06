import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
BODY = body(HERE)
META = dict(module='05-replication-and-the-cluster', lesson='01-brokers-and-replication', n='5.1', module_label='Module 5 · Replication and the cluster',
    title='Brokers and replication',
    desc='How Kafka replicates partitions across brokers: replication factor, leaders and followers, the preferred leader, round-robin and rack-aware replica placement, manual assignment and kafka-reassign-partitions with throttles. Real Kafka 4.4 lab: 6 partitions × RF 3 give 2 leaders and 6 replicas per broker, and a partition is moved from brokers 1,2 to 3,1 and disappears from broker 2’s disk.',
    og_desc='18 copies, 2 leaders per broker, and a live partition move: Kafka replication and reassignment on 4.4.',
    minutes=22, level='Intermediate',
    lead='Where do Kafka’s copies live, and how do you move them? We create a <b>replicated topic</b>, count leaders and replicas per broker, and <b>reassign</b> a partition to another broker, checking the disks. <b>All outputs are real.</b>',
    chips=['2-2-2 leaders', 'Live reassignment', 'Rack awareness', 'Runs in your browser (Python)'])
MAIN = '''# Kafka-style replica placement: round-robin with a shifting start
def place(partitions, brokers, rf):
    plan = {}
    for p in range(partitions):
        first = p % len(brokers)
        shift = (p // len(brokers)) % (len(brokers) - 1) + 1     # vary follower order
        replicas = [brokers[first]]
        for k in range(1, rf):
            replicas.append(brokers[(first + k * shift) % len(brokers)])
        plan[p] = replicas
    return plan

plan = place(6, [1, 2, 3], 3)
for p, r in plan.items():
    print(f"P{p}: replicas {r}  preferred leader {r[0]}")
from collections import Counter
print("leaders per broker:", dict(Counter(r[0] for r in plan.values())))
'''
RUN = dict(heading='Run the code: placing replicas', intro='<p>A simplified version of Kafka’s placement. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('        first = p % len(brokers)', 'Each partition starts on the next broker: leaders spread evenly.'), ('print("leaders per broker:", dict(Counter(r[0] for r in plan.values())))', 'Our lab: 2 leaders per broker.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Then try 5 brokers.', code=None),
        dict(label='2 · Predict first: copies', hint='<b>Predict first:</b> 6 partitions × RF 3 = ?', code='print(6 * 3)\n'),
        dict(label='3 · Disk', hint='100 GB of data at RF 3.', code='print(100 * 3, "GB")\n'),
        dict(label='4 · Racks', hint='One copy per zone.', code='zones = {1: "a", 2: "b", 3: "c"}\nprint(len({zones[b] for b in [1, 2, 3]}) == 3)\n'),
        dict(label='5 · Spot the error', hint='RF larger than brokers.', expect='error', code='brokers, rf = 3, 4\nif rf > brokers:\n    raise ValueError("Replication factor: 4 larger than available brokers: 3")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: move a partition', intro='<p>Needs a multi-broker cluster. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Plan', cmd='echo \'{"version":1,"partitions":[{"topic":"small-51","partition":0,"replicas":[3,1]}]}\' > plan.json', file='terminal', output='', note='Target replicas.'),
           dict(title='2 · Execute', cmd='kafka-reassign-partitions.sh --bootstrap-server k1:9092 --reassignment-json-file plan.json --execute --throttle 50000000', file='terminal', output='Successfully started partition reassignment for small-51-0', note='50 MB/s throttle.'),
           dict(title='3 · Verify', cmd='kafka-reassign-partitions.sh --bootstrap-server k1:9092 --reassignment-json-file plan.json --verify', file='terminal', output='Reassignment of partition small-51-0 is completed.\nClearing broker-level throttles on brokers 1,2,3', note='Clears throttles.')])
TRACE = dict(heading='Reassignment steps', intro='<p>Add first, remove last.</p>',
    code='replicas = [1, 2]\ntarget = [3, 1]\nadding = [b for b in target if b not in replicas]\nreplicas = replicas + adding\nreplicas = [b for b in replicas if b in target]\nprint(adding, replicas)\n',
    notes={4: 'Add :: New copy joins and catches up.', 5: 'Remove :: Old copy dropped.'})
WORKED_INTRO = 'Three replication decisions.'
EXAMPLES = [
    dict(level='b', tag='Replication · RF', title='Choose RF', problem='<p>Orders must survive one broker failure without stopping writes.</p>', inp='failures',
         approach=['RF 3.', 'min.insync.replicas 2.', 'acks=all.'], code='print({"replication.factor": 3, "min.insync.replicas": 2})\n', notes={1: 'Standard :: Lesson 2.4 recipe.'}, tryit='Types table.'),
    dict(level='i', tag='Replication · racks', title='Three availability zones', problem='<p>Survive a full zone outage.</p>', inp='zones',
         approach=['broker.rack = zone id.', 'RF 3 → one copy per zone.', 'Consumers can fetch from nearest (client.rack).'], code='print({"broker.rack": "ap-south-1a", "client.rack (consumer)": "ap-south-1a"})\n', notes={1: 'Zones :: Copies spread automatically.'}, tryit='Scenario 2.'),
    dict(level='a', tag='Replication · ops', title='Plan a balancing move', problem='<p>Move 40 partitions to 2 new brokers.</p>', inp='size',
         approach=['Batches of 5 partitions.', 'Throttle 50 MB/s.', 'Verify, then preferred election.'], code='size_gb, mbps = 400, 50\nprint(round(size_gb * 1024 / mbps / 3600, 1), "hours of copying")\n', notes={1: 'Time :: Plan maintenance windows.'}, tryit='Scenario 3.')]
QUIZ = mix([
    dict(q='Beginner: replication.factor 3 means…', options=['3 partitions', '3 copies of each partition', '3 topics', '3 consumers'], answer=1, why='Copies.'),
    dict(q='Beginner: Who serves reads and writes?', options=['All replicas', 'The leader', 'The controller', 'The last replica'], answer=1, why='Followers copy.'),
    dict(q='Beginner: The preferred leader is…', options=['The fastest broker', 'The first replica in the list', 'Random', 'The controller'], answer=1, why='Order matters.'),
    dict(q='Intermediate: Leaders per broker in our lab were…', options=['6-0-0', '2-2-2', '3-3-0', '1-2-3'], answer=1, why='Balanced.'),
    dict(q='Intermediate: Adding new brokers…', options=['Moves partitions automatically', 'Does nothing until you reassign', 'Deletes data', 'Doubles RF'], answer=1, why='Manual move.'),
    dict(q='Intermediate: After the reassignment, the leader of small-51-0 was…', options=['3', '1', '2', 'none'], answer=1, why='Needs an election.'),
    dict(q='Advanced: broker.rack is used to…', options=['Compress', 'Spread replicas across racks/zones', 'Name topics', 'Set ACLs'], answer=1, why='Rack awareness.'),
    dict(q='Advanced: Why throttle a reassignment?', options=['To lose data', 'To protect production traffic', 'To change keys', 'It is required'], answer=1, why='Bandwidth.')])
REVISION = ['RF copies on different brokers; first replica = preferred leader; followers fetch.', 'Lab: rides-51 6 × RF 3 → leaders 2-2-2, replicas 6-6-6.',
    'Placement round-robin with shifts; rack-aware with broker.rack.', 'Reassign: plan JSON → --execute (--throttle) → --verify; leader unchanged until election.', 'Lab: small-51-0 moved 1,2 → 3,1; folder gone from broker 2.']
FAQ = [('Can I change RF of an existing topic?', 'Yes, with a reassignment plan that lists more (or fewer) replicas per partition.'),
    ('Do followers serve consumers?', 'By default no; with rack-aware fetching (client.rack + replica.selector.class) consumers can read from a nearby follower.'),
    ('What is Cruise Control?', 'An open-source tool that monitors brokers and generates balancing plans; Kafka itself does not auto-balance replicas.'),
    ('Does a replica store the same files?', 'Yes, its own segment files; segment boundaries can differ slightly between replicas.')]
PRACTICE_INTRO = 'Replication programs.'
PROBLEMS = [
    dict(level='easy', title='Copies', stmt='Total replicas for 12 partitions, RF 3.', inp='numbers', code='print(12 * 3)\n', explain='36.'),
    dict(level='easy', title='Per broker', stmt='36 replicas over 4 brokers.', inp='numbers', code='print(36 / 4)\n', explain='9 each.'),
    dict(level='easy', title='Preferred', stmt='Preferred leader of [3, 1].', inp='list', code='print([3, 1][0])\n', explain='3.'),
    dict(level='medium', title='Leader count', stmt='Leaders per broker.', inp='plan', code='from collections import Counter\nprint(Counter(r[0] for r in [[1,2,3],[2,3,1],[3,1,2],[1,3,2]]))\n', explain='Imbalance check.'),
    dict(level='medium', title='Diff plans', stmt='Replicas to add and remove.', inp='old, new', code='old, new = [1, 2], [3, 1]\nprint("add", set(new) - set(old), "remove", set(old) - set(new))\n', explain='Reassignment.'),
    dict(level='medium', title='Rack check', stmt='Do replicas use distinct racks?', inp='map', code='rack = {1: "a", 2: "a", 3: "b"}\nprint(len({rack[b] for b in [1, 2, 3]}) == 3)\n', explain='False: two in a.'),
    dict(level='business', title='Copy time', stmt='200 GB at 50 MB/s.', inp='numbers', code='print(round(200 * 1024 / 50 / 60), "minutes")\n', explain='~68 min.'),
    dict(level='business', title='Disk cost', stmt='10 TB data, RF 3 vs RF 2.', inp='numbers', code='print(10 * 3, "TB vs", 10 * 2, "TB")\n', explain='Safety costs disk.')]
SCN_INTRO = 'Replication interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“How does replication work in Kafka?”', 'Explain.', 'answer?', '<p>Each partition has RF copies on different brokers. One is the leader for reads and writes; followers fetch from it. If the leader fails, an in-sync follower becomes leader. RF 3 with min ISR 2 is typical.</p>', '“Every broker has all data.”') +
    scn('Platform', 'Mid-level', 'Scale out', 'New brokers are idle.', 'fix?', '<ul><li>Reassign partitions to them (throttled).</li><li>Preferred leader election afterwards.</li><li>Consider Cruise Control.</li></ul>', 'Restarting the cluster.') +
    scn('Platform', 'Mid-level', 'Zone outage', 'Losing a zone stops writes.', 'cause?', '<ul><li>Two replicas in the same zone.</li><li>Set broker.rack, reassign.</li></ul>', 'Raising RF only.') +
    scn('Platform', 'Senior', 'Decommission', 'Retire broker 2 with zero downtime.', 'plan?', '<ul><li>Reassign all its replicas elsewhere (throttled).</li><li>Verify none remain; elections.</li><li>Then shut down and unregister.</li></ul>', 'Just stopping it.'))
