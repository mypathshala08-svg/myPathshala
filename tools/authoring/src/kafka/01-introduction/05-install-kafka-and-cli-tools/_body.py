import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l15_install.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
HOOK = hook('Can you run a real Kafka on your laptop with one command?',
    'Yes. One <code>docker run</code> starts a complete Kafka 4.4 node (broker and controller) in seconds. Then 4 tools are enough for 90% of daily work. We will also make Kafka refuse three common mistakes so you recognise the errors later.',
    ['What the single-node default config really sets (and why it is not for production).',
     'The 4 everyday CLI tools out of 40+ in the bin folder.',
     'The exact error when you ask for 3 copies on 1 broker.'])
MAP = concept_map('Concept map. Beginner: Docker image, start a node, create a topic, console producer and consumer. Intermediate: server.properties, listeners, topic configs, CLI tool families. Advanced: 3-node cluster, Python clients, production settings.',
    [[('dk', 'docker run', 'apache/kafka:4.4.0', None), ('ct', 'Create topic', 'kafka-topics.sh', None), ('pc', 'Console produce/consume', 'try it', None)],
     [('sp', 'server.properties', 'roles, listeners, log.dirs', None), ('cf', 'Topic configs', 'kafka-configs.sh', None), ('tf', 'CLI tool families', '40+ scripts', None)],
     [('3n', '3-node cluster', 'Lesson 1.3 lab', B + '01-introduction/03-kafka-architecture/'), ('py', 'Python clients', 'Module 2', B + '02-producers/01-how-a-producer-sends-a-message/'), ('pr', 'Production settings', 'Module 10', B + '10-kafka-in-production/02-performance-tuning-and-partition-sizing/')]],
    [('dk', 'sp'), ('ct', 'cf'), ('pc', 'tf'), ('sp', '3n'), ('tf', 'py'), ('cf', 'pr')],
    {'dk', 'ct', 'pc', 'sp', 'cf', 'tf'},
    '<b>Builds on:</b> 1.1–1.4. <b>Next:</b> Module 2, <a href="../../02-producers/01-how-a-producer-sends-a-message/">2.1 How a producer sends a message</a>.')
WHW = why_how_where(
    'You learn Kafka fastest by running it. Docker removes Java and config setup.',
    'The official apache/kafka image starts one KRaft node in combined mode; scripts in /opt/kafka/bin talk to it over port 9092.',
    'Laptops, CI tests (Testcontainers), and learning labs. Production uses multi-node clusters or managed services.',
    'Never use the single-node defaults in production: replication factor 1, data in /tmp.')

sc_ = (box(14, 20, 200, 110, 'card') + t(114, 36, 'Your laptop', 8.8, bold=True) + box(30, 48, 168, 72, 'blue', rx=6) + t(114, 64, 'Docker container “kafka”', 8, bold=True) +
       t(114, 80, 'apache/kafka:4.4.0', 7.6, 'ink2', mono=True) + t(114, 94, 'broker + controller', 7.6, 'ink2') + t(114, 108, ':9092 clients  :9093 controller', 7.2, 'ink2', mono=True) +
       arrow(214, 75, 256, 75, 'acc', 1.4) +
       ''.join(opbox(256 + (k % 2) * 186, 20 + (k // 2) * 56, n, d, tone, 176, 44) for k, (n, d, tone) in enumerate([
           ('kafka-topics.sh', 'create · list · describe · alter', 'green'), ('kafka-console-producer.sh', 'type events', 'acc'),
           ('kafka-configs.sh', 'retention and other settings', 'violet'), ('kafka-console-consumer.sh', 'read events', 'blue')])))
scene_svg = scene('A Docker container running Kafka 4.4 on a laptop, with four everyday tools: kafka-topics, kafka-configs, the console producer and the console consumer.', sc_,
                  'One container, <tspan font-weight="700" class="s-acc">four tools</tspan>: enough to start.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Your own Kafka in one minute</h2>
  <div class="story">
{HOOK}
    <p class="narration">Riya wants to practise at home. She remembers installing Hadoop by hand and is worried about Java versions, ZooKeeper and config files.</p>

{scene_svg}

R> Sir, do I need to install Java and ZooKeeper first?
A> Not any more. Kafka 4 has no ZooKeeper, and the official Docker image already contains Java. One command starts a full KRaft node.
K> And then?
A> Four scripts: <code>kafka-topics</code>, <code>kafka-configs</code>, the console producer and the console consumer. We will run all of them, and also trigger three classic errors on purpose.
  </div>
</section>
'''

lv = '''
LEVELS> Installing Kafka at three levels
L1> Just run it
      <ul>
        <li>Install Docker Desktop, run one command, and you have Kafka. Stop it with <code>docker stop kafka</code>.</li>
      </ul>
L2> What the image sets up
      <ul>
        <li><code>process.roles=broker,controller</code>, <code>node.id=1</code>, one controller voter, listeners on 9092 (clients) and 9093 (controller).</li>
        <li><code>log.dirs=/tmp/kraft-combined-logs</code> inside the container: data disappears with the container unless you mount a volume.</li>
        <li><code>num.partitions=1</code>, <code>log.retention.hours=168</code> (7 days) as defaults for new topics.</li>
      </ul>
L3> Beyond one node
      <ul>
        <li>For a 3-node lab set <code>KAFKA_*</code> environment variables (node id, controller voters, advertised listeners) per container, like our <code>start_cluster.sh</code>.</li>
        <li><code>advertised.listeners</code> must be an address clients can reach; most “cannot connect” problems come from this.</li>
        <li>Without Docker: download the binary from kafka.apache.org (Java 17+), run <code>kafka-storage.sh format</code>, then <code>kafka-server-start.sh</code>.</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of the Kafka bin folder: tool families for topics and configs, console producer and consumer, groups and offsets, inspection tools like dump-log and metadata-quorum, performance tests, and Connect and Streams.',
    t(16, 22, '/opt/kafka/bin: 40+ scripts in 6 families', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('kafka-topics / kafka-configs', 'green', 1), ('console-producer / console-consumer', 'acc', 2)]) +
    fields(16, 70, [('consumer-groups / get-offsets / share-groups', 'blue', 3), ('dump-log / metadata-quorum', 'violet', 4)]) +
    fields(16, 106, [('producer-perf-test / consumer-perf-test', 'amber', 5), ('connect-* / streams-*', 'card', 6)]) +
    legend(16, 156, [(1, 'Admin', 'create, describe, alter topics and settings'),
                     (2, 'Try it', 'type and read events by hand'),
                     (3, 'Groups', 'lag, offsets, resets (Module 3)'),
                     (4, 'Inspect', 'look inside logs and the quorum (Modules 4–5)'),
                     (5, 'Benchmark', 'measure throughput (Module 10)'),
                     (6, 'Ecosystem', 'Connect and Streams (Modules 7, 9)')], size=8, gap=15, w=130),
    h=256, caption='The tools in the real 4.4.0 image, grouped.')
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Installing Kafka and the CLI tools</h2>
''' + def_block(
    'Apache Kafka is distributed as a Java binary archive and as the official <b>apache/kafka</b> container image. A node is configured through <code>server.properties</code> (or <code>KAFKA_*</code> environment variables in the image): <code>process.roles</code>, <code>node.id</code>, <code>controller.quorum.voters</code>, <code>listeners</code>, <code>advertised.listeners</code> and <code>log.dirs</code>. Storage must be formatted with a cluster ID before first start (the image does this automatically). The distribution includes command-line tools in <code>bin/</code>, built on the Admin, Producer and Consumer APIs, for managing topics and configurations, producing and consuming, inspecting groups and logs, and benchmarking.',
    'Run the official Docker image to get a working Kafka node. Use the scripts in its bin folder to create topics, change settings, and send and read events.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('apache/kafka', 'Official Docker image.'),
    ('server.properties', 'Main node config file.'),
    ('listeners', 'Ports the node opens.'),
    ('advertised.listeners', 'Address given to clients.'),
    ('log.dirs', 'Where data is stored.'),
    ('--bootstrap-server', 'Broker address for every tool.'),
    ('kafka-configs.sh', 'Read and change settings.'),
    ('Dynamic config', 'Changed without restart.'),
]) + '''

  <h3>Why, how, where</h3>
''' + WHW + '''

  <h3>Concept map: what depends on what</h3>
''' + MAP + '''

  <h3>Dissect the tool box</h3>
''' + DIS + lv + myths([('Start ZooKeeper first, then Kafka.', 'Kafka 4.x has no ZooKeeper; one KRaft node starts alone.', 'Step 1: the node elects itself controller.'), ('Use --zookeeper localhost:2181 with kafka-topics.', 'Every tool uses --bootstrap-server.', 'all commands in this lesson.'), ('The Docker defaults are fine for production.', 'RF 1 and data in /tmp are for learning only.', 'Step 2: the default server.properties.')]) + '''
EXAM> “How do you create a topic and check it?” <code>kafka-topics.sh --bootstrap-server host:9092 --create --topic t --partitions 3 --replication-factor 3</code>, then <code>--describe</code> to see partitions, leaders, replicas and ISR. Replication factor cannot exceed the number of brokers.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Ways to run Kafka</h2>
''' + table(['Option', 'Good for', 'Notes'], [
    ['Docker single node', 'learning, local dev', 'this lesson; data lost without a volume'],
    ['Docker 3 nodes', 'learning failover, replication', 'our lab start_cluster.sh'],
    ['Binary download', 'servers without Docker', 'Java 17+; format storage first'],
    ['Kubernetes operator', 'self-managed production', 'e.g. Strimzi'],
    ['Managed service', 'production without ops', 'Lesson 11.1'],
], minw=560) + '''
''' + table(['Command', 'What it does'], [
    ['<code>kafka-topics.sh --create/--list/--describe/--alter/--delete</code>', 'manage topics'],
    ['<code>kafka-configs.sh --entity-type topics --alter --add-config k=v</code>', 'change a setting live'],
    ['<code>kafka-console-producer.sh --topic t</code>', 'type events'],
    ['<code>kafka-console-consumer.sh --topic t --from-beginning</code>', 'read events'],
], minw=560) + '''
WARN> In Kafka 4.x the console tools’ <code>--property</code> option is deprecated: use <code>--reader-property</code> (producer) and <code>--formatter-property</code> (consumer). Older tutorials also use <code>--zookeeper</code>: that option no longer exists. Always use <code>--bootstrap-server</code>.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Start, explore, use, break</h2>
  <p>All outputs are real: Docker, image <code>apache/kafka:4.4.0</code>, container <code>solo</code>. Commands are run with <code>docker exec solo /opt/kafka/bin/…</code>; we show the script names only.</p>
''' + stepper([
    ('Step 1 · Start Kafka',
     code('bash', 'terminal', 'docker run -d --name solo -p 9092:9092 apache/kafka:4.4.0\ndocker logs solo | grep RaftManager', sec('$ docker run', '$ docker exec solo ls')),
     'The node formats its storage, elects <b>itself</b> leader of the controller quorum (epoch 1) and finalises features: metadata version 4.4 and share groups enabled. No ZooKeeper.'),
    ('Step 2 · What is inside',
     code('bash', 'terminal', 'docker exec solo ls /opt/kafka\ndocker exec solo grep -E "^(process.roles|node.id|...)" /opt/kafka/config/server.properties', sec('$ docker exec solo ls', '== topic CRUD')),
     'The default config: combined broker + controller, data in <code>/tmp</code>, 1 partition per new topic, 7-day retention. Perfect for learning, wrong for production.'),
    ('Step 3 · Create, list, describe',
     code('bash', 'terminal', 'kafka-topics.sh --bootstrap-server localhost:9092 --create --topic menu-updates --partitions 2\nkafka-topics.sh --bootstrap-server localhost:9092 --list\nkafka-topics.sh --bootstrap-server localhost:9092 --describe --topic menu-updates', sec('== topic CRUD', '$ kafka-configs.sh --alter')),
     'Two partitions, replication factor 1 (only one broker), leader 1. Every tool needs <code>--bootstrap-server</code>.'),
    ('Step 4 · Change a setting live',
     code('bash', 'terminal', 'kafka-configs.sh --bootstrap-server localhost:9092 --entity-type topics --entity-name menu-updates \\\n  --alter --add-config retention.ms=86400000\nkafka-configs.sh ... --describe', sec('$ kafka-configs.sh --alter', '$ kafka-console-producer.sh')),
     'Retention for this topic is now 1 day instead of 7, with no restart: a <b>dynamic</b> topic config.'),
    ('Step 5 · Produce and consume',
     code('bash', 'terminal', 'kafka-console-producer.sh --bootstrap-server localhost:9092 --topic menu-updates\n>Paneer Tikka price 220\n>Dosa back in stock\nkafka-console-consumer.sh --bootstrap-server localhost:9092 --topic menu-updates --from-beginning', sec('$ kafka-console-producer.sh', '$ kafka-topics.sh --create --topic menu-updates (again)')),
     'Both events come back. Note the hint about the new consumer rebalance protocol (KIP-848), now production-ready (Lesson 3.2). The final <code>TimeoutException</code> is just the consumer’s <code>--timeout-ms</code> ending the demo.'),
    ('Step 6 · Three errors on purpose',
     code('bash', 'terminal', 'kafka-topics.sh ... --create --topic menu-updates          # again\nkafka-topics.sh ... --create --topic x3 --replication-factor 3\nkafka-topics.sh ... --delete --topic menu-updates; kafka-topics.sh ... --list', sec('$ kafka-topics.sh --create --topic menu-updates (again)')),
     'Duplicate topic: <b>already exists</b>. RF 3 on one broker: <b>cannot be reached because only 1 broker(s) are registered</b>. Delete works and only the internal <code>__consumer_offsets</code> remains.'),
]) + '''
</section>
'''

see = [
    term([('$ docker run -d apache/kafka:4.4.0', Y), ('RaftManager: Leader epoch=1', G), ('metadataVersion=4.4-IV2', W)], size=7.2),
    term([('process.roles=broker,controller', W), ('log.dirs=/tmp/kraft-combined-logs', Y), ('num.partitions=1', W)], size=7.2),
    term([('Created topic menu-updates.', G), ('PartitionCount: 2  RF: 1', W), ('retention.ms=86400000', G)], size=7.2),
    term([('Paneer Tikka price 220', W), ('Dosa back in stock', W), ('Processed a total of 2 messages', G)], size=7.2),
    term([('Topic \'menu-updates\' already exists.', RD), ('RF of 3 cannot be reached:', RD), ('only 1 broker(s)', RD)], size=7.0),
]
B1 = [
    t(180, 14, 'One container = one KRaft node', 9, bold=True) + opbox(110, 46, 'node 1', 'broker + controller', 'acc', 140, 40) + cap('Elects itself controller.', '', 'blue', y=144, h=30),
    t(180, 14, 'Defaults for learning', 9, bold=True) + ''.join(t(30, 50 + k * 16, s, 8, c, anchor='start', mono=True) for k, (s, c) in enumerate([('RF 1 (no copies)', 'red'), ('data in /tmp', 'red'), ('1 partition default', 'ink2'), ('7-day retention', 'ink2')])) + cap('Not production settings.', '', 'amber', y=144, h=30),
    t(180, 14, 'Topic + live config', 9, bold=True) + pcol(70, 44, 'P0', [], 'blue') + pcol(70, 70, 'P1', [], 'blue') + opbox(220, 50, 'retention', '1 day', 'violet', 100, 34) + cap('Dynamic config, no restart.', '', 'green', y=144, h=30),
    t(180, 14, 'Events in, events out', 9, bold=True) + opbox(20, 50, 'producer', 'typed lines', 'acc', 90, 34) + arrow(110, 67, 140, 67, 'ink3', 1) + pcol(150, 48, '', ['Pan', 'Dosa'], 'blue') + arrow(226, 67, 250, 67, 'ink3', 1) + opbox(250, 50, 'consumer', '2 messages', 'green', 90, 34) + cap('Console tools for testing.', '', 'blue', y=144, h=30),
    t(180, 14, 'Kafka protects you', 9, bold=True) + opbox(40, 50, 'duplicate', 'rejected', 'red', 120, 34) + opbox(200, 50, 'RF > brokers', 'rejected', 'red', 120, 34) + cap('Read errors carefully.', '', 'red', y=144, h=30),
]
two = anim_two('Install Kafka and use the CLI', 'Start, use, break', 'Real outputs from the lab', 'What each step means', see, B1,
               ['Start.', 'Config.', 'Topic.', 'Events.', 'Errors.'], ['Node.', 'Defaults.', 'Config.', 'Round trip.', 'Guards.'])
PEEL = peel('What one CLI command really does', 'kafka-topics.sh --create, layer by layer. (Simplified.)',
    [('Shell script', ''), ('Java tool', ''), ('Admin client', ''), ('CreateTopics', ''), ('Controller', ''), ('Brokers', '')],
    [['Shell script', 'kafka-topics.sh is a', 'tiny wrapper around', 'kafka-run-class.sh'],
     ['Java tool', 'starts a JVM with', 'TopicCommand', '(that is why it is slow)'],
     ['Admin client', 'connects to the', 'bootstrap server', 'like any app'],
     ['CreateTopics API', 'request: name, 2 partitions,', 'RF 1', ''],
     ['Controller', 'checks RF ≤ brokers,', 'name unique, writes', 'to metadata log'],
     ['Brokers', 'see new metadata,', 'create partition folders', 'menu-updates-0, -1']],
    ['Script.', 'JVM.', 'Client.', 'Request.', 'Validate.', 'Create.'], 'scenario-peel')

def five(kind, title, sub, cons, lines, caps, hid):
    fr = [t(180, 22, a, 9.4, 'acc' if i == 4 else 'ink', bold=True) + t(180, 56, b, 8.4, 'ink2') + cap(c, '', tone, y=150, h=34) for i, (a, b, c, tone) in enumerate(lines)]
    return anim_one(kind, title, sub, cons[0], cons[1], fr, caps, hid=hid)
s1 = five('Real-time scenario 1', '“Connection refused” from my app', 'The advertised.listeners trap. (Typical.)',
          ('advertised.listeners', 'Clients connect to the address the broker advertises, not the one you typed'), [
    ('App on laptop', 'bootstrap localhost:9092', 'First call works.', 'blue'),
    ('Broker advertises k1:9092', 'a Docker hostname', 'Laptop cannot resolve it.', 'red'),
    ('Produce fails', 'cannot connect to k1', 'Confusing.', 'red'),
    ('Fix advertised address', 'localhost:9092 or a host entry', 'Or run app in Docker.', 'green'),
    ('Rule', 'advertise what clients can reach', 'Check this first.', 'blue')],
    ['Bootstrap.', 'Metadata.', 'Fail.', 'Fix.', 'Rule.'], 'scenario-listeners')
s2 = five('Real-time scenario 2', 'Data gone after restart', 'Missing volume. (Typical.)',
          ('Persistence', 'Mount a volume for log.dirs or data is lost with the container'), [
    ('Dev Kafka in Docker', 'docker rm, new container', 'Topics gone!', 'red'),
    ('log.dirs in /tmp', 'inside container', 'Not persisted.', 'amber'),
    ('Mount a volume', '-v kafka-data:/var/lib/kafka/data', 'Set log.dirs.', 'green'),
    ('Restart keeps data', 'same cluster id', 'Safe.', 'green'),
    ('For tests: fine to lose', 'Testcontainers', 'Choose consciously.', 'blue')],
    ['Restart.', 'Cause.', 'Volume.', 'Kept.', 'Choice.'], 'scenario-volume')
s3 = five('Real-time scenario 3 · advanced', 'Copy-paste from an old tutorial', 'ZooKeeper-era commands on Kafka 4. (Typical.)',
          ('Version awareness', 'Kafka 4 removed ZooKeeper options; check the version of every tutorial'), [
    ('Tutorial says --zookeeper', 'localhost:2181', 'Written for 2.x.', 'blue'),
    ('Kafka 4.4 rejects it', 'option not recognised', 'No ZooKeeper.', 'red'),
    ('Use --bootstrap-server', 'localhost:9092', 'All tools.', 'green'),
    ('--property deprecated', 'use reader/formatter-property', 'Seen in our lab.', 'amber'),
    ('Check versions', 'docs for 4.x', 'Habit.', 'blue')],
    ['Old guide.', 'Error.', 'Fix.', 'Deprecations.', 'Habit.'], 'scenario-oldtutorial')
animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Start, use, break</h2>
  <p>Left: real lab output. Right: what each step means.</p>
''' + two + '''
  <p>Now peel what one CLI command really does.</p>
''' + PEEL + '''
  <p>Three live scenarios follow: connection problems, lost data and outdated tutorials.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

def uc_(word, sub, tone, title, desc, flow_):
    return usecase(f'<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-{tone}" style="stroke:var(--{tone if tone != "acc" else "track"})"/>' + t(60, 42, word, 11, tone, bold=True) + t(60, 58, sub, 7.4, 'ink2'), title, desc, flow_)
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Where these tools are used</h2>
''' + '\n'.join([
    uc_('dev', 'laptop', 'blue', '1. Local development', 'Developers run Kafka in Docker to test producers and consumers.', ['Laptop', '*docker run', 'Test app']),
    uc_('CI', 'tests', 'green', '2. Automated tests', 'Integration tests start a throwaway Kafka container per test run.', ['Pipeline', '*container', 'Tests pass']),
    uc_('ops', 'runbook', 'violet', '3. Operations runbooks', 'On-call engineers describe topics and change retention with the CLI.', ['Alert', '*kafka-configs', 'Fixed']),
    uc_('debug', 'peek', 'acc', '4. Debugging', 'The console consumer quickly shows what is really in a topic.', ['Bug', '*console consumer', 'Evidence']),
    uc_('train', 'labs', 'blue', '5. Training labs', 'Courses like this one run small clusters in containers.', ['Learner', '*3 nodes', 'Hands-on']),
]) + '''
  <p class="muted">Examples are simplified descriptions of common practice.</p>
</section>
'''
pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> install Docker Desktop (Windows/macOS) or Docker Engine (Linux). The Kafka image is about 700 MB on disk.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
