import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='09-stream-processing', lesson='01-kafka-streams', n='9.1', module_label='Module 9 · Stream processing',
    title='Kafka Streams basics',
    desc='Kafka Streams explained: a Java library for stream processing on Kafka, the KStream DSL, topologies and processors, stateless operations (filter, mapValues, split), serdes, tasks, stream threads, application.id and exactly-once. Real Kafka Streams 4.4 lab: a topology printed and run with 2 threads and 3 tasks, routing orders to two topics.',
    og_desc='A 20-line Kafka Streams 4.4 app: topology, 3 tasks on 2 threads, and orders routed to two topics.',
    minutes=24, level='Intermediate',
    lead='How do you build a stream processor with no extra cluster? We write a <b>Kafka Streams</b> app, print its <b>topology</b>, run it on <b>2 threads</b>, and route orders. <b>All outputs are real.</b>',
    chips=['Topology printed', '3 tasks · 2 threads', 'filter → map → split', 'Runs in your browser (Python)'])
MAIN = '''# Kafka Streams-style pipeline in plain Python (stateless)
orders = [("Mumbai", "idli,2,40"), ("Pune", "thali,1,150"), ("Delhi", "dosa,0,90"),
          ("Mumbai", "thali,2,300"), ("Pune", "vada,3,60"), ("Delhi", "lassi,1,45")]

def topology(records):
    out = {"big-orders": [], "small-orders": []}
    for key, value in records:
        if int(value.split(",")[1]) <= 0:          # filter
            continue
        value = value.upper()                      # mapValues
        topic = "big-orders" if value.startswith("THALI") else "small-orders"   # split
        out[topic].append((key, value))            # to
    return out

for topic, recs in topology(orders).items():
    print(topic, recs)
'''
RUN = dict(heading='Run the code: a stateless topology', intro='<p>The lab app’s logic in Python. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('        if int(value.split(",")[1]) <= 0:          # filter', 'Delhi dosa qty 0 is dropped.'), ('        topic = "big-orders" if value.startswith("THALI") else "small-orders"   # split', 'Branch by predicate.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Add a third branch for LASSI.', code=None),
        dict(label='2 · Predict first: tasks', hint='<b>Predict first:</b> input partitions 3 → tasks?', code='print(3)\n'),
        dict(label='3 · Threads', hint='3 tasks on 2 threads.', code='tasks = ["0_0", "0_1", "0_2"]\nprint({t: f"thread-{i % 2 + 1}" for i, t in enumerate(tasks)})\n'),
        dict(label='4 · Task id', hint='Decode 0_2.', code='sub, part = "0_2".split("_")\nprint("sub-topology", sub, "partition", part)\n'),
        dict(label='5 · Spot the error', hint='Bad qty value.', expect='error', code='int("abc")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: Kafka Streams', intro='<p>Needs JDK 17+ and the Kafka libs. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Libraries', cmd='docker cp k1:/opt/kafka/libs/. libs/', file='terminal', output='', note='kafka-streams-4.4.0.jar and friends.'),
           dict(title='2 · Compile', cmd='javac -proc:none -cp "libs/*" -d out src/Kitchen91.java', file='terminal', output='', note='Plain javac.'),
           dict(title='3 · Run', cmd='java -cp "out:libs/*" Kitchen91 2 15000', file='terminal', output='  state CREATED -> REBALANCING\n  state REBALANCING -> RUNNING', note='2 threads, 15 s.'),
           dict(title='4 · Reset', cmd='kafka-streams-application-reset.sh --bootstrap-server k1:9092 --application-id kitchen-91 --input-topics orders-91 --execute', file='terminal', output='', note='Reprocess from start.')])
TRACE = dict(heading='One record step by step', intro='<p>Filter, map, route.</p>',
    code='k, v = "Pune", "thali,1,150"\nkeep = int(v.split(",")[1]) > 0\nv = v.upper()\ntopic = "big" if v.startswith("THALI") else "small"\nprint(keep, v, topic)\n',
    notes={2: 'filter :: qty 1 > 0.', 3: 'mapValues :: Key unchanged.', 4: 'split :: big-orders.'})
WORKED_INTRO = 'Three Streams decisions.'
EXAMPLES = [
    dict(level='b', tag='Streams · fit', title='Library or engine?', problem='<p>Java service, Kafka in and out.</p>', inp='need',
         approach=['Kafka-to-Kafka.', 'Java team.', 'Kafka Streams.'], code='print("Kafka Streams")\n', notes={1: 'No cluster :: Just a jar.'}, tryit='Types table.'),
    dict(level='i', tag='Streams · scale', title='How many instances?', problem='<p>Input topic has 12 partitions.</p>', inp='partitions',
         approach=['12 tasks.', 'Up to 12 threads in total.', 'More are idle.'], code='print("max useful threads:", 12)\n', notes={1: 'Limit :: = partitions.'}, tryit='Scenario 1.'),
    dict(level='a', tag='Streams · EOS', title='Exactly-once routing', problem='<p>No duplicates downstream.</p>', inp='config',
         approach=['processing.guarantee=exactly_once_v2.', 'Consumers read_committed.', 'Brokers ≥ 3 for transactions.'], code='print({"processing.guarantee": "exactly_once_v2"})\n', notes={1: 'Atomic :: Offsets + outputs.'}, tryit='Scenario 3.')]
QUIZ = mix([
    dict(q='Beginner: Kafka Streams is…', options=['A cluster', 'A Java library', 'A broker plugin', 'A database'], answer=1, why='Runs in your app.'),
    dict(q='Beginner: mapValues changes…', options=['Key', 'Value only', 'Partition', 'Topic'], answer=1, why='No repartition.'),
    dict(q='Beginner: Which order was filtered out?', options=['Pune thali', 'Delhi dosa (qty 0)', 'Mumbai idli', 'None'], answer=1, why='qty > 0.'),
    dict(q='Intermediate: application.id is also…', options=['Topic name', 'Consumer group id', 'Broker id', 'Schema'], answer=1, why='Step 4.'),
    dict(q='Intermediate: 3 input partitions give…', options=['1 task', '3 tasks', '6 tasks', 'threads only'], answer=1, why='One per partition.'),
    dict(q='Intermediate: topology.describe() shows…', options=['Offsets', 'Sources, processors, sinks', 'Lag', 'ACLs'], answer=1, why='The graph.'),
    dict(q='Advanced: Changing the key causes…', options=['Nothing', 'A repartition before grouping/joining', 'Data loss', 'Compaction'], answer=1, why='Internal topic.'),
    dict(q='Advanced: exactly_once_v2 relies on…', options=['ZooKeeper', 'Transactions', 'acks=0', 'Compaction'], answer=1, why='Lesson 3.5.')])
REVISION = ['Library in your app; DSL KStream; topology of processors.', 'Stateless ops: filter, mapValues, split, peek, to.',
    'Lab: 3 tasks (0_0..0_2) on 2 threads; thali → big, others → small, qty 0 dropped.', 'application.id = consumer group; tasks = partitions.', 'EOS v2; exception handlers; repartition when key changes.']
FAQ = [('Can I use Python?', 'Not with Kafka Streams; use Faust-style libraries, Flink or Spark (Lesson 9.4).'),
    ('Where does it run?', 'Anywhere your Java app runs: containers, Kubernetes, VMs.'),
    ('How do I test it?', 'With TopologyTestDriver from kafka-streams-test-utils, no broker needed (Lesson 9.3 uses it).'),
    ('What is the new streams rebalance protocol?', 'KIP-1071 moves Streams task assignment to the broker (like KIP-848 for consumers); check your Kafka version.')]
PRACTICE_INTRO = 'Streams programs.'
PROBLEMS = [
    dict(level='easy', title='Filter', stmt='Keep qty > 0.', inp='list', code='print([q for q in [2, 0, 1] if q > 0])\n', explain='[2, 1].'),
    dict(level='easy', title='Upper', stmt='mapValues upper.', inp='str', code='print("idli,2,40".upper())\n', explain='IDLI,2,40.'),
    dict(level='easy', title='Tasks', stmt='Tasks for 8 partitions.', inp='int', code='print(8)\n', explain='8.'),
    dict(level='medium', title='Branch', stmt='Route by first word.', inp='list', code='vs = ["THALI,1", "IDLI,2"]\nprint({v: ("big" if v.startswith("THALI") else "small") for v in vs})\n', explain='Split.'),
    dict(level='medium', title='Threads', stmt='Tasks per thread, 9 tasks, 4 threads.', inp='ints', code='print([len(range(i, 9, 4)) for i in range(4)])\n', explain='[3,2,2,2].'),
    dict(level='medium', title='Safe parse', stmt='Skip bad qty.', inp='list', code='def ok(v):\n    try: return int(v) > 0\n    except ValueError: return False\nprint([ok(x) for x in ["2", "abc", "0"]])\n', explain='Guard.'),
    dict(level='business', title='Instances', stmt='Each instance 2 threads, 12 partitions.', inp='ints', code='print(12 // 2, "instances max useful")\n', explain='6.'),
    dict(level='business', title='Throughput', stmt='3 tasks × 5k rec/s.', inp='ints', code='print(3 * 5000, "rec/s")\n', explain='15k.')]
SCN_INTRO = 'Streams interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“What is Kafka Streams?”', 'Explain.', 'answer?', '<p>A Java library for building apps that read from Kafka topics, transform/aggregate/join records, and write back to Kafka, with scaling and fault tolerance via consumer groups and tasks.</p>', '“A Kafka broker feature.”') +
    scn('Platform', 'Mid-level', 'App in ERROR', 'Streams app stopped.', 'fix?', '<ul><li>Find the exception (poison record?).</li><li>Handlers, DLQ, restart.</li></ul>', 'Delete topics.') +
    scn('Platform', 'Mid-level', 'No speedup', 'Added 10 instances, same speed.', 'why?', '<ul><li>Only 3 partitions → 3 tasks.</li><li>Increase partitions (carefully).</li></ul>', 'More threads.') +
    scn('Fintech', 'Senior', 'Duplicates', 'Double charges after restarts.', 'fix?', '<ul><li>exactly_once_v2.</li><li>read_committed consumers.</li></ul>', 'Lower retries.'))
