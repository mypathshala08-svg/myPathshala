import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
BODY = body(HERE)

META = dict(
    module='01-introduction', lesson='05-install-kafka-and-cli-tools', n='1.5',
    module_label='Module 1 · Start here: why Kafka?',
    title='Install Kafka 4 (KRaft) and the CLI tools',
    desc='Run Apache Kafka 4.4 with one docker run command (KRaft, no ZooKeeper), read its default server.properties, and use the everyday CLI tools: kafka-topics (create, list, describe, delete), kafka-configs (live retention change), console producer and consumer. Includes the bin tool families dissected and three real error messages.',
    og_desc='Kafka 4.4 in one docker command, the four everyday CLI tools, and three real errors explained.',
    minutes=22, level='Beginner',
    lead='Run a real <b>Kafka 4.4</b> node with <b>one command</b>, look at what it configured, and master the <b>four everyday CLI tools</b>. We also trigger three classic errors on purpose. <b>All outputs are real.</b>',
    chips=['docker run apache/kafka:4.4.0', '4 everyday tools', 'Real error messages', 'Runs in your browser (Python)'],
)

MAIN = '''# A toy "kafka-topics" with the same safety checks as the real controller
brokers = 1
topics = {}

def create(name, partitions=1, rf=1):
    if name in topics:
        return f"Error: Topic '{name}' already exists."
    if rf > brokers:
        return f"Error: replication factor {rf} cannot be reached: only {brokers} broker(s)"
    topics[name] = {"partitions": partitions, "rf": rf, "config": {}}
    return f"Created topic {name}."

def alter_config(name, key, value):
    topics[name]["config"][key] = value
    return f"Completed updating config for topic {name}."

print(create("menu-updates", 2))
print(alter_config("menu-updates", "retention.ms", 86400000))
print(topics)
print(create("menu-updates"))
print(create("x3", rf=3))
'''
RUN = dict(
    heading='Run the code: the topic tool’s checks',
    intro='<p>The checks the controller makes, in plain Python. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    if rf > brokers:', 'Replication factor can never exceed the number of brokers.'),
        ('    topics[name]["config"][key] = value', 'A dynamic config: no restart needed.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then set brokers = 3 and run again.', code=None),
        dict(label='2 · Predict first: retention', hint='<b>Predict first:</b> 86400000 ms is how many days?',
             code='''print(86400000 / 1000 / 60 / 60 / 24)
'''),
        dict(label='3 · Default retention', hint='168 hours in days.',
             code='''print(168 / 24)
'''),
        dict(label='4 · Delete', hint='Delete a topic from the dict.',
             code='''topics = {"menu-updates": {}, "__consumer_offsets": {}}
topics.pop("menu-updates")
print(list(topics))
'''),
        dict(label='5 · Spot the error', hint='Old ZooKeeper flag.', expect='error',
             code='''args = ["--zookeeper", "localhost:2181"]
assert "--bootstrap-server" in args, "Kafka 4.x: --zookeeper is not a recognized option; use --bootstrap-server"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: the whole lesson',
    intro='<p>Copy these one by one. <b>Outputs are real</b> (Kafka 4.4.0).</p>',
    items=[
        dict(title='1 · Start', cmd='docker run -d --name kafka -p 9092:9092 apache/kafka:4.4.0', file='terminal',
             output='ee1ecc07ed0f…', note='Container id.'),
        dict(title='2 · Create', cmd='docker exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic menu-updates --partitions 2', file='terminal',
             output='Created topic menu-updates.', note='RF 1 on one broker.'),
        dict(title='3 · Configure', cmd='docker exec kafka /opt/kafka/bin/kafka-configs.sh --bootstrap-server localhost:9092 --entity-type topics --entity-name menu-updates --alter --add-config retention.ms=86400000', file='terminal',
             output='Completed updating config for topic menu-updates.', note='Live change.'),
        dict(title='4 · Clean up', cmd='docker stop kafka && docker rm kafka', file='terminal',
             output='kafka\nkafka', note='Data is gone (no volume).'),
    ],
)

TRACE = dict(
    heading='Validate a create request',
    intro='<p>The controller’s two checks.</p>',
    code='''brokers = 1
existing = {"menu-updates"}
name, rf = "x3", 3
ok = name not in existing
ok = ok and rf <= brokers
print("created" if ok else "rejected")
''',
    notes={4: 'Unique :: Name is new.', 5: 'RF :: 3 > 1 broker, rejected.'},
)

WORKED_INTRO = 'Three setup tasks you will do often.'
EXAMPLES = [
    dict(level='b', tag='Kafka · CLI', title='Create a topic for menu updates',
         problem='<p>2 partitions, 1-day retention.</p>',
         inp='name, partitions, retention',
         approach=['kafka-topics --create.', 'kafka-configs --alter retention.ms.', 'Describe to verify.'],
         code='''cmds = ["kafka-topics.sh --create --topic menu-updates --partitions 2",
        "kafka-configs.sh --entity-type topics --entity-name menu-updates --alter --add-config retention.ms=86400000",
        "kafka-topics.sh --describe --topic menu-updates"]
print("\\n".join(cmds))
''', notes={1: 'Order :: Create, configure, verify.'},
         tryit='Steps 3–4.'),
    dict(level='i', tag='Kafka · Docker', title='Keep data across restarts',
         problem='<p>Dev topics disappear after docker rm.</p>',
         inp='volume',
         approach=['Create a named volume.', 'Mount it at the log dir.', 'Set KAFKA_LOG_DIRS.'],
         code='''print("docker run -d --name kafka -p 9092:9092 -v kafka-data:/var/lib/kafka/data \\\\")
print("  -e KAFKA_LOG_DIRS=/var/lib/kafka/data apache/kafka:4.4.0")
''', notes={1: 'Persist :: Volume outlives the container.'},
         tryit='Scenario 2.'),
    dict(level='a', tag='Kafka · listeners', title='Reach Kafka from host and containers',
         problem='<p>Apps on the laptop and in Docker both need access.</p>',
         inp='two networks',
         approach=['Two listeners: INTERNAL and EXTERNAL.', 'Advertise k1:19092 and localhost:9092.', 'Map protocols.'],
         code='''print("listeners=INTERNAL://:19092,EXTERNAL://:9092,CONTROLLER://:9093")
print("advertised.listeners=INTERNAL://k1:19092,EXTERNAL://localhost:9092")
''', notes={1: 'Two names :: Each client gets a reachable address.'},
         tryit='Scenario 1.'),
]

QUIZ = mix([
    dict(q='Beginner: The official Kafka Docker image is…', options=['confluent/zookeeper', 'apache/kafka', 'kafka/server', 'bitnami/hadoop'], answer=1,
         why='apache/kafka:4.4.0.'),
    dict(q='Beginner: Which option does every Kafka 4 CLI tool need?', options=['--zookeeper', '--bootstrap-server', '--host', '--broker-list only'], answer=1,
         why='ZooKeeper is gone.'),
    dict(q='Beginner: Which tool changes a topic’s retention?', options=['kafka-topics.sh --list', 'kafka-configs.sh', 'kafka-dump-log.sh', 'docker logs'], answer=1,
         why='Dynamic topic config.'),
    dict(q='Intermediate: Creating RF 3 on one broker…', options=['Works', 'Fails: only 1 broker registered', 'Creates RF 1', 'Waits'], answer=1,
         why='RF ≤ brokers.'),
    dict(q='Intermediate: Default log.dirs in the image is under…', options=['/var/lib', '/tmp', '/opt/data', '/home'], answer=1,
         why='/tmp/kraft-combined-logs.'),
    dict(q='Intermediate: Default retention is…', options=['1 day', '7 days', '30 days', 'forever'], answer=1,
         why='log.retention.hours=168.'),
    dict(q='Advanced: Apps outside Docker cannot connect although bootstrap works. Likely cause?', options=['Retention', 'advertised.listeners', 'Partitions', 'Compression'], answer=1,
         why='Clients use the advertised address.'),
    dict(q='Advanced: In 4.x, console consumer --property is…', options=['Required', 'Deprecated: use --formatter-property', 'Removed in 2.0', 'For ZooKeeper'], answer=1,
         why='Warning seen in the lab.'),
])

REVISION = [
    'docker run -d --name kafka -p 9092:9092 apache/kafka:4.4.0 → one KRaft node.',
    'Defaults: broker+controller, data in /tmp, 1 partition, 7-day retention, RF 1.',
    'Four tools: kafka-topics, kafka-configs, console producer, console consumer.',
    'Always --bootstrap-server; --zookeeper is gone; use --reader/--formatter-property.',
    'Errors: topic exists; RF > brokers; data lost without a volume.',
]
FAQ = [
    ('Can I install Kafka without Docker on Windows?', 'Yes, with Java 17+ and the binary download, but Docker (or WSL2) is simpler and matches Linux servers.'),
    ('Why do the CLI tools start slowly?', 'Each script starts a Java VM; a second or two is normal.'),
    ('How do I see all topic configs, including defaults?', 'kafka-configs.sh --describe --all --entity-type topics --entity-name &lt;topic&gt;.'),
    ('What port does Kafka use?', 'By convention 9092 for clients; 9093 is often used for the controller listener in KRaft.'),
]

PRACTICE_INTRO = 'Setup and CLI programs.'
PROBLEMS = [
    dict(level='easy', title='ms to days', stmt='Convert retention.ms to days.', inp='604800000',
         code='''print(604800000 / 86400000)
''', explain='7 days.'),
    dict(level='easy', title='Build a command', stmt='Create-topic command string.', inp='name, partitions',
         code='''n, p = "orders", 3
print(f"kafka-topics.sh --bootstrap-server localhost:9092 --create --topic {n} --partitions {p}")
''', explain='Template.'),
    dict(level='easy', title='RF check', stmt='Is RF allowed?', inp='rf 3, brokers 1',
         code='''print(3 <= 1)
''', explain='No.'),
    dict(level='medium', title='Parse describe', stmt='Read PartitionCount from describe output.', inp='line',
         code='''line = "Topic: menu-updates\\tPartitionCount: 2\\tReplicationFactor: 1"
print(dict(p.split(": ") for p in line.split("\\t"))["PartitionCount"])
''', explain='Simple parsing.'),
    dict(level='medium', title='Parse key:value', stmt='Split console input like parse.key.', inp='"Mumbai:o1"',
         code='''k, v = "Mumbai:o1".split(":", 1)
print(k, v)
''', explain='key.separator=:'),
    dict(level='medium', title='Env vars', stmt='Build KAFKA_* env for node 2.', inp='id 2',
         code='''i = 2
print({"KAFKA_NODE_ID": i, "KAFKA_ADVERTISED_LISTENERS": f"PLAINTEXT://k{i}:9092"})
''', explain='Like start_cluster.sh.'),
    dict(level='business', title='Disk for dev', stmt='1,000 events/min × 1 KB for 7 days.', inp='numbers',
         code='''print(round(1000 * 60 * 24 * 7 / 1024 / 1024, 2), "GB")
''', explain='Small for a laptop.'),
    dict(level='business', title='Retention savings', stmt='Disk saved by 1 day instead of 7.', inp='1.4 GB/day',
         code='''print(round(1.4 * 6, 1), "GB saved")
''', explain='Per-topic retention.'),
]

SCN_INTRO = 'Setup questions for freshers and ops roles.'
SCENARIOS = (
    scn('Any company · data', 'Fresher', '“How do you run Kafka locally?”',
        'Describe the steps.',
        'answer?',
        '<p>docker run apache/kafka:4.4.0 gives a KRaft node. Then kafka-topics --create, console producer to send, console consumer --from-beginning to read. Mount a volume if data must survive.</p>', '“Start ZooKeeper first.”') +
    scn('Data engineering', 'Fresher', 'RF error',
        'kafka-topics fails: replication factor cannot be reached.',
        'cause?',
        '''<ul>
          <li>RF greater than live brokers.</li>
          <li>Use RF 1 locally or start more brokers.</li>
        </ul>''', 'Retrying the same command.') +
    scn('Platform', 'Mid-level', 'Connectivity',
        'Clients time out after the first connection.',
        'debug?',
        '''<ul>
          <li>Check advertised.listeners resolves from the client.</li>
          <li>Separate internal and external listeners.</li>
          <li>Test with kafka-broker-api-versions.</li>
        </ul>''', 'Opening every port.') +
    scn('Platform', 'Senior', 'Prod config review',
        'A team copied the Docker defaults to production.',
        'what to change?',
        '''<ul>
          <li>Persistent log.dirs on real disks.</li>
          <li>3+ brokers, RF 3, min.insync.replicas 2.</li>
          <li>Separate controllers, security, monitoring.</li>
        </ul>''', '“Defaults are fine.”')
)
