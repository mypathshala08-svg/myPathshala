import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l111_sizing.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('You have learned to run brokers, controllers, Connect, a registry, monitoring, security and DR. Most companies pay someone else to do all of it. Who, and what do they still leave to you?',
    'Managed services run Kafka (or a Kafka-compatible engine) for you: <b>Confluent Cloud</b>, <b>Amazon MSK</b>, <b>Google Cloud Managed Service for Apache Kafka</b>, <b>Azure Event Hubs</b> (Kafka API), <b>Aiven</b>, <b>Instaclustr</b>, <b>Redpanda Cloud</b>, <b>WarpStream</b> and others. They take the servers; you still own <b>topic design, partitions, keys, schemas, client configs, security policy and cost</b>. We sized TiffinGo’s needs first: 19.5 MB/s in, 78 MB/s out, 6.8 TB stored, 24 partitions.',
    ['What “managed” takes off your plate, and what stays with you.',
     'Deployment models: serverless, provisioned, BYOC; Kafka vs Kafka-compatible.',
     'How to compare and choose, starting from your own numbers.'])
cmap = concept_map('Concept map. Beginner: self-managed vs managed. Intermediate: serverless, provisioned, BYOC, Kafka-compatible engines. Advanced: sizing, cost drivers, lock-in, migration, compliance.',
    [[('sm', 'Self-managed', 'Modules 1–10', B + '10-kafka-in-production/01-monitoring-and-consumer-lag/'), ('mg', 'Managed service', 'someone runs it', None)],
     [('sl', 'Serverless', 'pay per use', None), ('pv', 'Provisioned', 'brokers you size', None), ('by', 'BYOC', 'in your account', None), ('kc', 'Kafka-compatible', 'API, not Apache code', None)],
     [('sz', 'Sizing', 'MB/s, TB, partitions', B + '10-kafka-in-production/02-performance-tuning-and-partition-sizing/'), ('co', 'Cost drivers', 'egress, storage', None), ('lk', 'Lock-in', 'extras vs API', None), ('mi', 'Migration', 'Lesson 10.4', B + '10-kafka-in-production/04-multi-cluster-and-mirrormaker-2/')]],
    [('sm', 'mg'), ('mg', 'sl'), ('mg', 'pv'), ('mg', 'by'), ('mg', 'kc'), ('pv', 'sz'), ('sz', 'co'), ('kc', 'lk'), ('lk', 'mi')],
    {'mg', 'sl', 'pv', 'by', 'kc', 'sz', 'co', 'lk'},
    '<b>Builds on:</b> Module 10. <b>Next:</b> <a href="../02-kafka-vs-rabbitmq-pulsar-and-others/">11.2 Kafka vs RabbitMQ, Pulsar and others</a>.')
whw = why_how_where(
    'Running Kafka well needs on-call engineers, upgrades, capacity planning and security work. For many teams that effort costs more than a managed bill.',
    'The provider runs brokers, storage, upgrades, monitoring and often Connect, a schema registry and stream processing; you connect with SASL_SSL/OAuth/IAM, create topics via API/Terraform, and pay by capacity, throughput, storage and network.',
    'Startups and most enterprises on public cloud; teams without Kafka specialists; regulated firms using BYOC to keep data in their own accounts.',
    'Less control (broker configs, versions, plugins), possible cost surprises (cross-zone and egress traffic, partitions), and vendor-specific features that are hard to leave.')

def models(hl=-1):
    parts = [('self-managed', 'you run all', 'card'), ('provisioned', 'you size brokers', 'blue'), ('serverless', 'pay per use', 'green'), ('BYOC', 'vendor ops, your VPC', 'violet')]
    o = ''
    for k, (n, d, tn) in enumerate(parts):
        o += box(8 + k * 88, 40, 80, 60, 'acc' if k == hl else tn, rx=8) + t(48 + k * 88, 62, n, 7.6, bold=True) + t(48 + k * 88, 80, d, 6.4)
    return o + t(180, 24, 'who operates what', 7.6)
scene_svg = scene('Four ways to run Kafka: self-managed where you run everything, provisioned managed where you size brokers, serverless where you pay per use, and bring-your-own-cloud where the vendor operates inside your cloud account.', models(),
                  'Same Kafka API, four <tspan font-weight="700" class="s-acc">operating models</tspan>.')
dialogue = '''K> Sir, our self-run cluster needs a full-time person. Should TiffinGo move to a managed Kafka?
A> Maybe. First write down our own numbers: MB/s in and out, storage, partitions, security needs. Then compare offers on the same numbers.
R> Are they all real Apache Kafka?
A> No. Some run Apache Kafka, some run their own engine that speaks the Kafka protocol. Both can work; you must know which you are buying.'''

lv = '''
LEVELS> Managed Kafka at three levels
L1> Own car, lease, taxi
      <ul>
        <li>Self-managed is owning a car (you service it). Provisioned is a lease (fixed size, someone services it). Serverless is a taxi (pay per ride). BYOC is a chauffeur driving your own car.</li>
      </ul>
L2> The market (late 2026)
      <ul>
        <li><b>Apache Kafka, managed</b>: Amazon MSK (standard and Express brokers), Google Cloud Managed Service for Apache Kafka, Aiven, Instaclustr and others.</li>
        <li><b>Kafka-compatible engines</b>: Confluent Cloud (its Kora engine), Azure Event Hubs (Kafka endpoint), Redpanda (C++ engine), WarpStream and other object-storage-based designs.</li>
        <li>Extras differ: managed connectors, schema registry, Flink/stream processing, cluster linking, table formats (Iceberg/Delta). Confluent has been part of IBM since March 2026.</li>
      </ul>
L3> Choosing well
      <ul>
        <li>Start from your workload (lesson lab): ingress/egress MB/s, partitions, retention, latency SLO, number of client apps.</li>
        <li>Cost drivers: throughput units or brokers, storage (tiered/object storage lowers it), <b>network</b> (cross-AZ replication and consumer egress often dominate), connectors and extras.</li>
        <li>Check: Kafka version and feature support (KIP-848, share groups, transactions), security (private networking, IAM/OAuth), limits (partitions, message size), SLA, regions, exit path (MirrorMaker 2/replicators).</li>
      </ul>
/LEVELS
'''
SZ = figure('Sizing summary for TiffinGo from the lab script: 19.5 MB/s in, 78.1 MB/s out with 4 consumer groups, 39.1 MB/s replication traffic, 6.76 TB stored for 7 days, 24 partitions.',
    ''.join(box(10 + k * 124, 30, 116, 60, tn, rx=8) + t(68 + k * 124, 54, v, 11, bold=True) + t(68 + k * 124, 76, l, 7.2)
            for k, (v, l, tn) in enumerate([('19.5 MB/s', 'in (peak)', 'blue'), ('78.1 MB/s', 'out, 4 groups', 'amber'), ('39.1 MB/s', 'replication', 'violet'), ('6.76 TB', '7 days, RF 3', 'green'), ('24', 'partitions', 'acc')])),
    h=110, caption='Bring these numbers to every vendor conversation.')
extra = '''

  <h3>Your numbers first</h3>
''' + SZ

types_html = table(['Service', 'Engine', 'Models', 'Notes'], [
    ['Amazon MSK', 'Apache Kafka', 'provisioned (standard, Express), serverless', 'IAM auth, MSK Connect'],
    ['Google Cloud Managed Service for Apache Kafka', 'Apache Kafka', 'provisioned (vCPU/RAM)', 'IAM, VPC'],
    ['Confluent Cloud', 'Kora (Kafka-compatible)', 'serverless tiers, dedicated, BYOC (WarpStream)', 'connectors, Flink, Cluster Linking'],
    ['Azure Event Hubs', 'Event Hubs (Kafka API)', 'tiers / throughput units', 'not all Kafka features'],
    ['Aiven / Instaclustr', 'Apache Kafka', 'provisioned, BYOC', 'multi-cloud'],
    ['Redpanda Cloud', 'Redpanda (Kafka API)', 'serverless, dedicated, BYOC', 'C++, no JVM'],
    ['WarpStream', 'object-storage agents (Kafka API)', 'BYOC', 'stateless agents'],
], minw=720)
warn = 'Do not compare price lists before you know your own traffic. Network charges (cross-zone replication, consumer egress) can exceed broker costs, and Kafka-compatible engines may not support every API you use (transactions, KIP-848, share groups, Connect plugins). Test your real client configs against a trial cluster.'

steps = [
    ('Step 1 · Workload',
     code('python', 'l111.py', 'peak_msgs, size_kb, retention_days, rf = 20000, 1.0, 7, 3\nmbps_in = peak_msgs * size_kb / 1024\nmbps_out = mbps_in * consumer_groups', sec('== 1)', '== 2)')),
     'Out is 4× in because four groups read everything; replication adds 2× in between brokers (a cost line in many clouds).'),
    ('Step 2 · Partitions',
     code('python', 'l111.py', 'need = max(mbps_in / per_partition, consumers_wanted)', sec('== 2)', '== 3)')),
     'Throughput alone needs 2 partitions; parallelism needs 24. Many managed tiers price or limit partitions, so this matters.'),
    ('Step 3 · Models',
     code('python', 'l111.py', 'serverless | provisioned | BYOC', sec('== 3)')),
     'Same numbers, three pricing shapes. Ask each vendor to price this exact workload.'),
]
see = [term([('19.5 MB/s in', W), ('78.1 MB/s out', Y), ('6.76 TB', W)], size=7.0), term([('need 2 for MB/s', W), ('choose 24', G)], size=7.2), term([('serverless', W), ('provisioned', W), ('BYOC', W)], size=7.2)]
B1 = [models(0), models(1), models(-1)]
B1 = [b + cap(c, '', tn, y=118, h=30) for b, c, tn in zip(B1, ['Know your load', 'Size partitions', 'Pick a model'], ['blue', 'amber', 'green'])]
two = anim_two('Managed Kafka', 'Numbers before vendors', 'Real outputs from the lab script', 'Operating models', see, B1, ['Load.', 'Partitions.', 'Models.'], ['MB/s.', '24.', 'Choose.'])
pe = peel('Moving to managed Kafka, layer by layer', 'TiffinGo’s plan. (Simplified.)',
    [('Measure', ''), ('Shortlist', ''), ('Test', ''), ('Secure', ''), ('Migrate', ''), ('Operate', '')],
    [['Measure', 'MB/s, TB, partitions', 'latency SLO', ''], ['Shortlist', 'region, features', 'Kafka vs compatible', ''], ['Test', 'trial cluster', 'our clients + configs', 'perf-test'],
     ['Secure', 'private link', 'OAuth/IAM, ACLs', ''], ['Migrate', 'MirrorMaker 2', 'consumers then producers', 'Lesson 10.4'], ['Operate', 'lag + cost dashboards', 'quotas, budgets', '']],
    ['Numbers.', 'Shortlist.', 'Trial.', 'Lock.', 'Move.', 'Run.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Startup with no Kafka team', 'Launch in 3 weeks. (Typical.)', ('Serverless', 'Start small, pay per use'), [
    ('No ops engineers', 'tight deadline', 'Constraint.', 'amber'), ('Serverless tier', 'API keys, few partitions', 'Start.', 'green'),
    ('Managed connectors', 'DB → topic', 'No Connect cluster.', 'green'), ('Watch bill vs traffic', 'budget alerts', 'Control.', 'blue'),
    ('Re-evaluate at scale', 'dedicated or BYOC', 'Grow.', 'blue')], ['Small.', 'Serverless.', 'Connect.', 'Budget.', 'Grow.'], 'scenario-startup') + \
       five('Real-time scenario 2', 'Surprise network bill', 'Egress larger than brokers. (Typical.)', ('Cost drivers', 'Traffic, not just brokers'), [
    ('4 consumer groups in other zones', 'cross-AZ fetch', 'Cost.', 'red'), ('Rack-aware fetching', 'client.rack', 'Fetch nearby.', 'green'),
    ('Compression', 'zstd', 'Fewer bytes.', 'green'), ('Fewer full re-reads', 'compacted views', 'Less egress.', 'green'),
    ('Bill down 35%', 'same SLO', 'Done.', 'blue')], ['Bill.', 'Nearby.', 'Compress.', 'Reduce.', 'Save.'], 'scenario-cost') + \
       five('Real-time scenario 3 · advanced', 'Regulated bank', 'Data must stay in our account. (Typical.)', ('BYOC / self-managed', 'Control plane vs data plane'), [
    ('Regulator: data residency', 'own account, own keys', 'Constraint.', 'amber'), ('BYOC offer', 'vendor runs agents in our VPC', 'Option.', 'blue'),
    ('Or MSK in our account', 'Apache Kafka', 'Option.', 'blue'), ('Check access paths', 'who can see data', 'Audit.', 'amber'),
    ('Decide on controls + cost', 'documented', 'Done.', 'green')], ['Rule.', 'BYOC.', 'MSK.', 'Audit.', 'Decide.'], 'scenario-bank')
assemble(HERE, h2_story='Who runs your Kafka?', hook_html=hk,
    narration='TiffinGo’s self-run cluster now needs a full-time engineer. The CTO asks Kabir to compare managed Kafka offers for next year.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Managed Kafka platforms',
    formal='A <b>managed Kafka platform</b> is a service in which a provider operates the Kafka (or Kafka-protocol-compatible) infrastructure, including provisioning, scaling, upgrades, monitoring and often ecosystem components, under a <b>serverless</b>, <b>provisioned</b> or <b>bring-your-own-cloud (BYOC)</b> model. Users keep responsibility for data modelling, client configuration, access policy and cost management.',
    simple='Instead of running Kafka servers yourself, you rent Kafka from a provider. They keep it running; you still design topics, keys, schemas and permissions, and watch the bill.',
    term_rows=[('Managed', 'Provider operates it.'), ('Serverless', 'Pay per use, no brokers to size.'), ('Provisioned', 'You choose capacity.'), ('BYOC', 'Vendor runs it in your cloud account.'), ('Kafka-compatible', 'Speaks the protocol, different engine.'), ('Egress', 'Data leaving a zone/region (billed).'), ('SLA', 'Promised availability.'), ('Lock-in', 'Hard to leave.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Managed means no Kafka knowledge needed.', 'Topic, key, schema and client design stay with you.', 'Hook.'),
               ('Every “Kafka” service runs Apache Kafka.', 'Several are Kafka-compatible engines.', 'Table.'),
               ('Broker price is the main cost.', 'Network and storage often dominate.', 'Scenario 2.')],
    exam='“Self-managed vs managed Kafka?” Managed removes ops (upgrades, scaling, monitoring) but limits control; models serverless/provisioned/BYOC; Apache Kafka vs compatible engines; size from MB/s, TB, partitions; cost = capacity + storage + network; check features and exit path.',
    types_h2='The landscape', types_html=types_html, warn=warn,
    steps_h2='Size before you shop', steps_intro='All outputs are real: a small Python sizing script for TiffinGo’s planned workload (no vendor accounts used; service facts from public product pages, late 2026).',
    steps=steps, two=two, peel_intro='Now peel a move to managed Kafka.', peel_html=pe,
    scen_intro='Three live scenarios: a startup, a network bill, and a regulated bank.', scen=scen,
    uc_h2='Managed Kafka at work', ucs=[uc_('start', 'startups', 'green', '1. Fast start', 'Serverless clusters in minutes.', ['Idea', '*serverless', 'Live']),
        uc_('ent', 'enterprise', 'blue', '2. Enterprise platforms', 'Dedicated clusters, private links.', ['Teams', '*dedicated', 'Platform']),
        uc_('bank', 'regulated', 'violet', '3. Regulated data', 'BYOC or in-account.', ['Data', '*BYOC', 'Compliance']),
        uc_('mig', 'migrate', 'amber', '4. Leaving on-prem', 'Mirror, cut over.', ['On-prem', '*MM2', 'Cloud'])],
    uc_note='Service descriptions are summaries of public information (late 2026) and change often; check current vendor documentation.',
    pre='<b>Before you start:</b> <a href="../../10-kafka-in-production/02-performance-tuning-and-partition-sizing/">10.2 Sizing</a>.')
