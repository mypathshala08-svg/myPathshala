import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='11-kafka-in-industry', lesson='01-managed-kafka-platforms', n='11.1', module_label='Module 11 · Kafka in industry',
    title='Managed Kafka platforms',
    desc='Managed Kafka explained: what providers take over and what stays with you, serverless vs provisioned vs BYOC, Apache Kafka vs Kafka-compatible engines, and the landscape in late 2026 (Amazon MSK, Google Cloud Managed Service for Apache Kafka, Confluent Cloud, Azure Event Hubs, Aiven, Instaclustr, Redpanda, WarpStream). Includes a real sizing script: 19.5 MB/s in, 78 MB/s out, 6.8 TB and 24 partitions.',
    og_desc='Size first, shop second: managed Kafka platforms compared with a real sizing script.',
    minutes=18, level='Intermediate',
    lead='Should you run Kafka yourself or rent it? We <b>size</b> TiffinGo’s workload, compare <b>operating models</b>, and list what every buyer must check. <b>Lab outputs are real.</b>',
    chips=['19.5 MB/s in', '6.76 TB stored', 'Serverless · provisioned · BYOC', 'Runs in your browser (Python)'])
MAIN = '''# Size a Kafka workload before talking to vendors
import math
peak_msgs, size_kb, retention_days, rf, groups = 20000, 1.0, 7, 3, 4
avg_ratio, compression = 0.4, 0.5

mb_in = peak_msgs * size_kb / 1024
mb_out = mb_in * groups
tb = peak_msgs * avg_ratio * size_kb * compression * 86400 * retention_days * rf / 1024**3
print(f"in {mb_in:.1f} MB/s, out {mb_out:.1f} MB/s, stored {tb:.2f} TB")
print("partitions:", max(math.ceil(mb_in / 10), 24))
'''
RUN = dict(heading='Run the code: size it', intro='<p>Your numbers first. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('mb_out = mb_in * groups', 'Every group reads everything: egress grows.'), ('print("partitions:", max(math.ceil(mb_in / 10), 24))', 'Parallelism often decides.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Set retention_days = 30.', code=None),
        dict(label='2 · Predict first: replication', hint='<b>Predict first:</b> broker-to-broker MB/s at RF 3.', code='print(19.5 * 2)\n'),
        dict(label='3 · Egress share', hint='Out vs in.', code='print(78.1 / 19.5)\n'),
        dict(label='4 · Tiered storage', hint='Keep 1 day local, rest in object storage.', code='print(round(6.76 / 7, 2), "TB local")\n'),
        dict(label='5 · Spot the error', hint='Feature not supported.', expect='error', code='raise NotImplementedError("UNSUPPORTED_VERSION: this Kafka-compatible service does not support share groups yet")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: connect to a managed cluster', intro='<p>Typical client settings. <b>Fill in your provider’s values.</b></p>',
    items=[dict(title='1 · Client config', cmd='bootstrap.servers=<provider endpoint>:9092\nsecurity.protocol=SASL_SSL\nsasl.mechanism=PLAIN|SCRAM-SHA-512|OAUTHBEARER|AWS_MSK_IAM', file='client.properties', output='', note='Same as Lesson 10.3.'),
           dict(title='2 · Smoke test', cmd='kafka-producer-perf-test.sh --topic test --num-records 10000 --record-size 1000 --throughput -1 --producer-props … --command-config client.properties', file='terminal', output='', note='Measure before you sign.')])
TRACE = dict(heading='Sizing step by step', intro='<p>In, out, stored.</p>',
    code='mb_in = 20000 * 1.0 / 1024\nmb_out = mb_in * 4\nprint(round(mb_in, 1), round(mb_out, 1))\n', notes={2: 'Fan-out :: 4 groups.'})
WORKED_INTRO = 'Three platform decisions.'
EXAMPLES = [
    dict(level='b', tag='Managed · model', title='Pick a model', problem='<p>Small team, spiky traffic.</p>', inp='need',
         approach=['Serverless.', 'Pay per use.', 'Watch limits.'], code='print("serverless")\n', notes={1: 'Start :: Small.'}, tryit='Scenario 1.'),
    dict(level='i', tag='Managed · engine', title='Apache or compatible?', problem='<p>Need transactions and Connect plugins.</p>', inp='features',
         approach=['List required APIs.', 'Test on trial.', 'Prefer Apache Kafka if unsure.'], code='print(["transactions", "KIP-848", "share groups", "Connect plugins"])\n', notes={1: 'Verify :: Not assume.'}, tryit='Table.'),
    dict(level='a', tag='Managed · cost', title='Cut egress', problem='<p>Network bill high.</p>', inp='tactics',
         approach=['client.rack fetch-from-follower.', 'Compression.', 'Fewer full re-reads.'], code='print({"client.rack": "use1-az1", "compression.type": "zstd"})\n', notes={1: 'Network :: Big line item.'}, tryit='Scenario 2.')]
QUIZ = mix([
    dict(q='Beginner: A managed service takes over…', options=['Topic design', 'Servers, upgrades, scaling', 'Your schemas', 'Your keys'], answer=1, why='Ops.'),
    dict(q='Beginner: BYOC means…', options=['Bring your own code', 'Vendor runs it in your cloud account', 'Self-managed', 'Free tier'], answer=1, why='Data stays.'),
    dict(q='Beginner: Azure Event Hubs is…', options=['Apache Kafka', 'Kafka-API compatible', 'RabbitMQ', 'Pulsar'], answer=1, why='Kafka endpoint.'),
    dict(q='Intermediate: Our egress was…', options=['19.5 MB/s', '78.1 MB/s', '6.76 TB', '24'], answer=1, why='4 groups.'),
    dict(q='Intermediate: Partitions chosen were…', options=['2', '24', '6', '100'], answer=1, why='Parallelism.'),
    dict(q='Intermediate: Often the surprise cost is…', options=['CPU', 'Network (cross-zone, egress)', 'ACLs', 'Topic names'], answer=1, why='Traffic.'),
    dict(q='Advanced: Before choosing, test…', options=['Logos', 'Your client configs and APIs on a trial', 'Nothing', 'Only price'], answer=1, why='Compatibility.'),
    dict(q='Advanced: Leaving a provider usually uses…', options=['Email', 'Replication (MM2 etc.)', 'Backups only', 'Nothing'], answer=1, why='Lesson 10.4.')])
REVISION = ['Managed = provider runs infra; you own design, clients, security policy, cost.', 'Models: serverless, provisioned, BYOC; Apache vs compatible engines.',
    'Lab sizing: 19.5 MB/s in, 78.1 out, 39.1 replication, 6.76 TB, 24 partitions.', 'Cost drivers: capacity, storage, network.', 'Check features, limits, security, SLA, exit path.']
FAQ = [('Is Confluent the same as Apache Kafka?', 'Confluent was founded by Kafka’s creators and contributes heavily; Confluent Cloud runs its own Kafka-compatible engine and adds services. Since March 2026 Confluent is part of IBM.'),
    ('Is Redpanda Kafka?', 'It implements the Kafka protocol in C++ without the JVM; clients work, but internals and some features differ.'),
    ('Can I use Kafka Streams with managed Kafka?', 'Yes, it is a client library; check required features (transactions, KIP-1071).'),
    ('What about on-prem?', 'Self-managed, or vendor platforms for Kubernetes (e.g. Strimzi operator, Confluent Platform).')]
PRACTICE_INTRO = 'Platform programs.'
PROBLEMS = [
    dict(level='easy', title='Out', stmt='10 MB/s in, 3 groups.', inp='ints', code='print(10 * 3)\n', explain='30 MB/s.'),
    dict(level='easy', title='Replication', stmt='RF 3 extra traffic.', inp='ints', code='print(10 * 2)\n', explain='20 MB/s.'),
    dict(level='easy', title='Daily', stmt='10 MB/s for a day in GB.', inp='ints', code='print(round(10 * 86400 / 1024))\n', explain='~844 GB.'),
    dict(level='medium', title='Storage', stmt='Store 7 days RF 3 compressed 0.5.', inp='floats', code='print(round(844 * 7 * 3 * 0.5 / 1024, 1), "TB")\n', explain='~8.7 TB.'),
    dict(level='medium', title='Compare', stmt='Cheapest of offers.', inp='dict', code='o = {"A": 4200, "B": 3900, "C": 5100}\nprint(min(o, key=o.get))\n', explain='B.'),
    dict(level='medium', title='Feature gap', stmt='Missing features.', inp='sets', code='need = {"transactions", "share"}\nhave = {"transactions"}\nprint(need - have)\n', explain='share.'),
    dict(level='business', title='Ops cost', stmt='1 engineer vs managed bill.', inp='ints', code='print("compare", 1 * 60000, "vs annual bill")\n', explain='TCO.'),
    dict(level='business', title='Egress saving', stmt='35% of 10k.', inp='ints', code='print(10000 * 0.35)\n', explain='3,500.')]
SCN_INTRO = 'Platform interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“What is managed Kafka?”', 'Explain.', 'answer?', '<p>A service where a provider runs Kafka (or a compatible engine) for you: servers, scaling, upgrades and monitoring. You still design topics, keys, schemas, security and watch cost.</p>', '“Kafka with no work at all.”') +
    scn('Platform', 'Mid-level', 'Choose a vendor', 'Shortlist.', 'how?', '<ul><li>Size workload, list features.</li><li>Trial with real clients; price same workload.</li></ul>', 'Pick the cheapest list price.') +
    scn('Platform', 'Mid-level', 'Bill doubled', 'Same traffic.', 'look?', '<ul><li>Network: cross-AZ, egress.</li><li>Partitions, retention.</li></ul>', 'Delete topics.') +
    scn('Bank', 'Senior', 'Residency', 'Data must stay in account.', 'options?', '<ul><li>BYOC or in-account managed (MSK) or self-managed.</li></ul>', 'Any serverless SaaS.'))
