import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l91_streams.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('Read a topic, clean each order, split big and small orders into two topics, and scale it across machines. How many servers do you need besides Kafka?',
    'Zero. <b>Kafka Streams</b> is a Java <b>library</b>, not a cluster: your app is a normal program that reads, transforms and writes topics. Scaling works like a consumer group: one <b>task</b> per input partition, spread over threads and instances. In our lab a 20-line app drew its own <b>topology</b>, dropped a qty-0 order, routed 2 thalis to big-orders and 3 others to small-orders, using 2 threads and 3 tasks.',
    ['What Kafka Streams is (and is not).',
     'KStream, topology, processors, and stateless operations.',
     'Tasks, threads and instances: how it scales and recovers.'])
cmap = concept_map('Concept map. Beginner: consume-process-produce, library vs cluster. Intermediate: KStream, topology, stateless ops (filter, map, split), serdes. Advanced: tasks and threads, application.id as consumer group, exactly-once, Processor API.',
    [[('cg', 'Consumer groups', 'Lesson 3.1', B + '03-consumers/01-consumers-and-consumer-groups/'), ('cp', 'Consume-process-produce', 'the loop', None)],
     [('ks', 'Kafka Streams', 'a library', None), ('st', 'KStream', 'event stream', None), ('to', 'Topology', 'processor graph', None), ('sl', 'Stateless ops', 'filter, map, split', None)],
     [('tk', 'Tasks + threads', 'scale', None), ('ai', 'application.id', 'group + prefix', None), ('eo', 'Exactly-once', 'Lesson 3.5', B + '03-consumers/05-transactions-and-exactly-once/'), ('kt', 'KTable + state', 'Lesson 9.2', B + '09-stream-processing/02-ktables-and-state-stores/')]],
    [('cg', 'cp'), ('cp', 'ks'), ('ks', 'st'), ('st', 'to'), ('to', 'sl'), ('ks', 'tk'), ('cg', 'ai'), ('ai', 'tk'), ('ks', 'eo'), ('st', 'kt')],
    {'ks', 'st', 'to', 'sl', 'tk', 'ai'},
    '<b>Builds on:</b> Modules 2–3. <b>Next:</b> <a href="../02-ktables-and-state-stores/">9.2 KTables and state stores</a>.')
whw = why_how_where(
    'Hand-written consume-process-produce loops must solve partition assignment, offsets, retries, state, scaling and exactly-once. Kafka Streams gives all of that as a library inside your app.',
    'You describe a topology with the DSL (stream → filter → mapValues → split → to). At start the library joins a consumer group named <code>application.id</code>, gets partitions, creates one task per partition, runs tasks on stream threads, and commits offsets (and output) together.',
    'Microservices that enrich, route, aggregate or join events: fraud checks, order routing, real-time counters, alerting. Runs anywhere Java runs: containers, Kubernetes, a laptop.',
    'Java/Scala (JVM) only; input and output must be Kafka. For SQL, Python or multi-source pipelines look at Flink, Spark (Lesson 9.4) or ksqlDB.')

def topo(hl=-1):
    nodes = [('source', 'blue'), ('filter', 'amber'), ('mapValues', 'amber'), ('split', 'violet')]
    o = ''
    for k, (n, tn) in enumerate(nodes):
        o += box(6 + k * 72, 52, 64, 34, 'acc' if k == hl else tn, rx=6) + t(38 + k * 72, 73, n, 7.4, bold=True)
        if k < 3: o += arrow(70 + k * 72, 69, 78 + k * 72, 69)
    o += box(296, 26, 60, 26, 'acc' if hl == 4 else 'green', rx=5) + t(326, 43, 'big', 7.4, bold=True) + box(296, 90, 60, 26, 'acc' if hl == 4 else 'green', rx=5) + t(326, 107, 'small', 7.4, bold=True)
    return o + arrow(282, 64, 296, 40) + arrow(282, 76, 296, 102)
scene_svg = scene('A Kafka Streams topology: source topic orders-91 feeds a filter, then mapValues, then split, which writes to two sink topics, big-orders-91 and small-orders-91.', topo(),
                  'A <tspan font-weight="700" class="s-acc">topology</tspan> is your program drawn as a graph.')
dialogue = '''K> Sir, I need a service that reads orders, drops broken ones, and sends thalis to the big-kitchen topic. Do we install a stream-processing cluster?
A> Not for this. <b>Kafka Streams</b> is just a library. Your service is a normal Java app; Kafka does the coordination.
R> And if one instance dies?
A> Its partitions (tasks) move to the others, exactly like a consumer group. Let’s write it and look inside.'''

lv = '''
LEVELS> Kafka Streams at three levels
L1> A sorting conveyor
      <ul>
        <li>Parcels arrive on a belt (topic). Workers check each parcel (filter), relabel it (map), and push it onto the right outgoing belt (split/to). Add more workers and the belts are shared out among them.</li>
      </ul>
L2> The DSL
      <ul>
        <li><b>KStream</b>: an unbounded stream of key–value records. Stateless operations: <code>filter</code>, <code>map</code>/<code>mapValues</code>, <code>flatMap</code>, <code>peek</code>, <code>split().branch()</code>, <code>merge</code>, <code>selectKey</code>, <code>to</code>.</li>
        <li><b>Serdes</b> turn bytes into objects (String, Long, JSON, Avro with the registry).</li>
        <li><code>topology.describe()</code> prints sources, processors and sinks: read it to see what your code really does.</li>
      </ul>
L3> Runtime
      <ul>
        <li><code>application.id</code> = consumer group id and prefix for internal topics. Each input partition → one <b>task</b> (0_0, 0_1, 0_2 = sub-topology 0, partition n). Tasks are spread over <code>num.stream.threads</code> and instances; max parallelism = number of input partitions.</li>
        <li>Lifecycle states: CREATED → REBALANCING → RUNNING → PENDING_SHUTDOWN → NOT_RUNNING (also ERROR).</li>
        <li><code>processing.guarantee=exactly_once_v2</code> uses transactions (Lesson 3.5) to commit input offsets and outputs atomically. The lower-level <b>Processor API</b> gives full control (custom state, punctuations).</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of one topology line: Processor KSTREAM-FILTER-0000000002 with no stores, forwarding to KSTREAM-MAPVALUES-0000000003 and receiving from KSTREAM-PEEK-0000000001.',
    t(16, 22, 'One node of topology.describe() (real output)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('Processor:', 'card', 1), ('KSTREAM-FILTER-0000000002', 'amber', 2), ('(stores: [])', 'blue', 3), ('--> MAPVALUES-3', 'green', 4), ('<-- PEEK-1', 'violet', 5)]) +
    legend(16, 84, [(1, 'Kind', 'Source, Processor or Sink'), (2, 'Name', 'operation + creation number (name it with Named.as)'),
                    (3, 'Stores', 'empty = stateless'), (4, 'Children', 'where records go next'), (5, 'Parent', 'where they come from')], size=8, gap=15, w=90),
    h=172, caption='Every DSL call becomes one or more nodes.')
extra = '''

  <h3>Dissect the topology</h3>
''' + DIS

types_html = table(['Operation', 'Does', 'Changes key?', 'State?'], [
    ['filter / filterNot', 'keep or drop', 'no', 'no'], ['mapValues', 'change value', 'no', 'no'], ['map / selectKey', 'change key', 'yes (repartition later)', 'no'],
    ['flatMap(Values)', '1 → many', 'maybe', 'no'], ['split().branch()', 'route by predicate', 'no', 'no'], ['peek', 'side effect (log)', 'no', 'no'],
    ['groupBy + count/aggregate', 'aggregate', 'yes', 'yes (9.2)'],
], minw=600) + table(['Tool', 'Type', 'Best for'], [
    ['Kafka Streams', 'Java library', 'microservices on Kafka'], ['ksqlDB', 'SQL server on Streams', 'SQL users (Confluent licence)'],
    ['Apache Flink', 'cluster', 'large, multi-source, SQL/Python'], ['Spark Structured Streaming', 'cluster', 'lakehouse, Python, batch+stream'],
], minw=520)
warn = 'Prefer mapValues over map when the key does not change. Changing the key (map/selectKey) marks the stream for repartitioning: the next grouping or join writes every record to an internal -repartition topic first, which costs network and disk.'

steps = [
    ('Step 1 · The app and its topology',
     code('java', 'Kitchen91.java', 'KStream<String, String> orders = b.stream("orders-91");          // key city, value item,qty,price\nKStream<String, String> valid = orders\n    .filter((k, v) -> Integer.parseInt(v.split(",")[1]) > 0)\n    .mapValues(v -> v.toUpperCase());\nvalid.split()\n    .branch((k, v) -> v.startsWith("THALI"), Branched.withConsumer(s -> s.to("big-orders-91")))\n    .defaultBranch(Branched.withConsumer(s -> s.to("small-orders-91")));\nSystem.out.println(b.build().describe());', sec('== run', '  state CREATED')),
     'One sub-topology: source → peek → filter → mapValues → branch → two sinks.'),
    ('Step 2 · Run with 2 threads',
     code('bash', 'terminal', 'java -cp "out:libs/*" Kitchen91 2 15000     # num.stream.threads = 2', sec('  state CREATED', '== outputs')),
     'States CREATED → REBALANCING → RUNNING. 3 input partitions → 3 tasks (0_0, 0_1, 0_2) spread over 2 threads. Six orders came in; Delhi’s dosa had qty 0.'),
    ('Step 3 · Outputs',
     code('bash', 'terminal', 'kafka-console-consumer.sh --bootstrap-server k1:9092 --topic big-orders-91 --from-beginning --formatter-property print.key=true', sec('== outputs', '== the app')),
     'Two thalis went to big-orders, three to small-orders, values upper-cased, keys (cities) unchanged. The qty-0 order was filtered out.'),
    ('Step 4 · It is a consumer group',
     code('bash', 'terminal', 'kafka-consumer-groups.sh --bootstrap-server k1:9092 --describe --group kitchen-91', sec('== the app')),
     'application.id kitchen-91 is the group. Offsets 4 and 2 committed on partitions 0 and 1 (partition 2 got no data), lag 0.'),
]
see = [term([('Sub-topology: 0', W), ('SOURCE → FILTER → MAPVALUES', G), ('→ BRANCH → 2 SINKS', G)], size=6.8), term([('REBALANCING → RUNNING', G), ('3 tasks · 2 threads', Y)], size=7.0),
       term([('big: THALI x2', G), ('small: IDLI VADA LASSI', G), ('dosa qty 0 dropped', RD)], size=6.8), term([('group kitchen-91', W), ('lag 0', G)], size=7.2)]
B1 = [topo(-1), topo(0), topo(4), topo(0)]
B1 = [b + cap(c, '', tn, y=130, h=30) for b, c, tn in zip(B1, ['Topology drawn', 'Tasks read partitions', 'Two sinks', 'Offsets committed'], ['blue', 'amber', 'green', 'violet'])]
two = anim_two('Kafka Streams', 'Topology, tasks, outputs', 'Real outputs from the lab', 'Inside the app', see, B1, ['Build.', 'Run.', 'Route.', 'Group.'], ['Graph.', 'Tasks.', 'Split.', 'Commit.'])
pe = peel('One record, layer by layer', '“Pune: thali,1,150”. (Simplified.)',
    [('Poll', ''), ('Task', ''), ('Filter', ''), ('Map', ''), ('Split', ''), ('Commit', '')],
    [['Poll', 'stream thread', 'fetches batch', ''], ['Task', 'task 0_1', 'partition 1', ''], ['Filter', 'qty 1 > 0', 'pass', ''],
     ['Map', 'THALI,1,150', 'key Pune kept', ''], ['Split', 'starts with THALI', '→ big-orders-91', 'producer send'], ['Commit', 'every 30 s (100 ms EOS)', 'offset stored', 'group kitchen-91']],
    ['Fetch.', 'Route.', 'Check.', 'Change.', 'Send.', 'Commit.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Scale out', 'Orders double at lunch. (Typical.)', ('Tasks move', 'Add instances like consumers'), [
    ('1 instance, 6 tasks', 'CPU 90%', 'Busy.', 'red'), ('Start 2 more instances', 'same application.id', 'Join.', 'blue'),
    ('Rebalance', '2 tasks each', 'Cooperative.', 'amber'), ('CPU 30% each', 'lag drops', 'Fast.', 'green'),
    ('Max 6 instances useful', '= partitions', 'Limit.', 'blue')], ['Busy.', 'Add.', 'Share.', 'Relief.', 'Limit.'], 'scenario-scale') + \
       five('Real-time scenario 2', 'Poison record', 'Bad value crashes the app. (Typical.)', ('Exception handlers', 'Deserialization / processing'), [
    ('"qty" = "abc"', 'NumberFormatException', 'Thread dies.', 'red'), ('App state ERROR', 'all tasks stop', 'Outage.', 'red'),
    ('Validate in filter', 'or try/catch → DLQ', 'Code fix.', 'green'), ('default.deserialization.exception.handler', 'LogAndContinue', 'Config.', 'green'),
    ('processing.exception.handler', 'Kafka 3.9+', 'Continue + DLQ.', 'blue')], ['Bad.', 'Crash.', 'Guard.', 'Skip.', 'Handle.'], 'scenario-poison') + \
       five('Real-time scenario 3 · advanced', 'Duplicates after crash', 'At-least-once by default. (Typical.)', ('exactly_once_v2', 'Atomic read-process-write'), [
    ('Crash after send, before commit', 'restart', 'Reprocess.', 'red'), ('Duplicates downstream', 'billing x2', 'Bug.', 'red'),
    ('processing.guarantee', 'exactly_once_v2', 'Transactions.', 'green'), ('Consumers read_committed', 'see each once', 'Clean.', 'green'),
    ('Cost', 'small latency (commit 100 ms)', 'Trade-off.', 'blue')], ['Crash.', 'Dup.', 'EOS.', 'Read.', 'Cost.'], 'scenario-eos')
assemble(HERE, h2_story='A stream processor without a cluster', hook_html=hk,
    narration='TiffinGo needs a small service that cleans incoming orders and routes thalis to the big kitchen. Kabir expected to install a new cluster.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Kafka Streams',
    formal='<b>Kafka Streams</b> is a client library for building applications that process records from Kafka topics and write results to Kafka. A program defines a <b>topology</b> of processors using the high-level DSL (KStream, KTable) or the Processor API. At runtime instances sharing an <code>application.id</code> form a consumer group; the topology is split into <b>tasks</b> (one per input partition per sub-topology) executed by stream threads, with fault tolerance, state management and optional exactly-once processing.',
    simple='Kafka Streams is a Java library: you write a small program that says “read this topic, change records like this, write them there”, and the library handles splitting the work, restarts and offsets.',
    term_rows=[('KStream', 'Stream of records.'), ('Topology', 'Graph of processors.'), ('Processor', 'One step (filter, map…).'), ('Sink', 'Writes to a topic.'), ('Task', 'Topology part for one partition.'), ('Stream thread', 'Runs tasks.'), ('application.id', 'Group id + prefix.'), ('Serde', 'Serializer + deserializer.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Kafka Streams needs its own cluster.', 'It is a library inside your app.', 'Step 2: java -cp.'),
               ('More threads always help.', 'Max parallelism = input partitions.', '3 tasks.'),
               ('Streams runs on the brokers.', 'It runs in your app, brokers only store.', 'Peel.')],
    exam='“What is Kafka Streams?” Java library; DSL KStream/KTable; topology of processors; application.id = consumer group; tasks per partition over threads/instances; stateless ops filter/map/split; state stores with changelogs; exactly_once_v2.',
    types_h2='Operations and alternatives', types_html=types_html, warn=warn,
    steps_h2='Build, run, route', steps_intro='All outputs are real: Kafka Streams 4.4.0 (Java 21) against the 3-broker lab.',
    steps=steps, two=two, peel_intro='Now peel one record.', peel_html=pe,
    scen_intro='Three live scenarios: scaling out, a poison record, and duplicates.', scen=scen,
    uc_h2='Kafka Streams at work', ucs=[uc_('route', 'routing', 'blue', '1. Event routing', 'Split by type or region.', ['Events', '*split', 'Topics']),
        uc_('enrich', 'enrich', 'green', '2. Enrichment', 'Join with reference tables (9.3).', ['Orders', '*join', 'Enriched']),
        uc_('fraud', 'fraud', 'red', '3. Fraud signals', 'Counts per card per minute.', ['Payments', '*window', 'Alerts']),
        uc_('ms', 'services', 'violet', '4. Event-driven services', 'Each service a small Streams app.', ['Topic', '*app', 'Topic'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../../03-consumers/01-consumers-and-consumer-groups/">3.1 Consumer groups</a>.')
