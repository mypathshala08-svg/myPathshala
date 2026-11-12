import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
sys.path.insert(0, HERE)
from scenes import launch_scene, capacity_picture
sys.path.insert(0, HERE)
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)
def row3(k, items, tones, cap_):
    o = ''
    for i, l in enumerate(items):
        on = i <= k
        bx = box(20 + i * 112, 34, 100, 74, tones[i] if on else 'card', rx=8)
        o += (f'<g class="sa-glow">{bx}</g>' if i == k else bx) + (sa_tick(112 + i * 112, 38, 7) if i < k else '')
        for j, w in enumerate(l.split('|')): o += t(70 + i * 112, 60 + j * 14, w, 7.2 if j == 0 else 6.6, 'ink', bold=(j == 0))
        if i < 2: o += arrow(120 + i * 112, 71, 132 + i * 112, 71)
    return o + t(180, 132, cap_, 7.2, 'ink', bold=True)
def mk(t3, items, tones, caps, steps, ttl, intro, panel, aria, hid):
    return cap([t(180, 12, t3[k], 9, 'ink', bold=True) + row3(k, items, tones, caps[k]) for k in range(3)], steps, ttl, intro, panel, aria, hid)
def vt(n, name, tone, d, an, sc, ex, gd, anim, use, avoid, plain, how, words, diff, where, rw, pro):
    return vtype(n, name, tone, d, an, sc, ex, gd, anim, use, avoid, plain=plain, how=how, words=words, diff=diff, where=where, realworld=rw, pro=pro)


hk = hook('TiffinGo’s Diwali orders jumped ten times in one evening. The single office server froze at 8 pm, and 600 dinners were late.',
    'Riya had two choices: buy three bigger servers that would sit idle the rest of the year, or <b>rent exactly what she needs, by the second, from Amazon Web Services</b>. This lesson explains what AWS is: <b>a global network of data centres</b>, <b>more than 200 services</b> you combine like building blocks, all controlled through <b>APIs</b> and paid for <b>as you use them</b>. On <b>your own</b> account you will count AWS services, see that every click is an API call recorded in CloudTrail, and check your Free Tier usage.',
    ['AWS = infrastructure + services + APIs + metered billing.', 'Seven service families cover almost everything.', 'Console, CLI and SDK all call the same API.'])

def story_scene():
    o = t(180, 12, 'Own servers vs AWS', 9, 'ink', bold=True)
    o += box(8, 28, 160, 74, 'red', rx=8) + t(88, 48, 'Buy 3 servers', 8.4, 'ink', bold=True) + t(88, 64, '₹6 lakh upfront, weeks', 7, 'ink2') + t(88, 78, 'idle 360 days a year', 7, 'ink2') + t(88, 92, 'still one building', 7.4, 'ink', bold=True)
    o += box(192, 28, 160, 74, 'green', rx=8) + t(272, 48, 'Rent on AWS', 8.4, 'ink', bold=True) + t(272, 64, 'minutes, no upfront cost', 7, 'ink2') + t(272, 78, 'scale out on Diwali night', 7, 'ink2') + t(272, 92, 'pay per second used', 7.4, 'ink', bold=True)
    o += t(180, 122, 'Capacity follows demand instead of guesses', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Left: buying three servers costs lakhs upfront, takes weeks and sits idle most of the year. Right: renting on AWS takes minutes, scales out on Diwali night and is paid per second.', story_scene(), 'Rent capacity <tspan font-weight="700" class="s-acc">when you need it</tspan>.', h=132)
dialogue = '''R> Sir, is AWS just a place to rent servers?
A> Servers are one of more than 200 services. Storage, databases, networking, security, analytics, AI — all rented the same way.
K> And how do we control all of it?
A> Every action is an API call — whether you click in the console, type a CLI command or write Python. AWS checks who you are, does it, logs it and meters it.
R> And the bill?
A> Pay as you go, per second or per request, with a Free Tier to learn on. Let’s see the big picture.'''

def bigpic():
    o = t(320, 16, 'What AWS is, in four layers', 11, 'ink', bold=True)
    L = [('You', 'console · CLI · SDK · IaC', 'blue', 36), ('APIs + IAM', 'every request authenticated, authorised, logged (CloudTrail)', 'amber', 80),
         ('200+ services', 'compute · storage · databases · networking · security · analytics & AI · management', 'green', 124),
         ('Global infrastructure', 'Regions → Availability Zones → data centres · edge locations', 'violet', 168)]
    for a, b, tn, y in L:
        o += box(40, y, 480, 38, tn, rx=8) + t(130, y + 23, a, 8.6, 'ink', bold=True) + t(350, y + 23, b, 6.8, 'ink2')
    o += box(536, 36, 92, 170, 'card', rx=8) + t(582, 104, 'Billing', 8.6, 'ink', bold=True) + t(582, 122, 'metered', 7, 'ink2') + t(582, 136, 'per second /', 7, 'ink2') + t(582, 150, 'per request', 7, 'ink2')
    for y in (55, 99, 143, 187): o += arrow(520, y, 534, y)
    o += t(320, 224, 'You call APIs; AWS runs the services on its infrastructure and meters what you use.', 7.4, 'ink2')
    return o
BIG = bigfig('Four layers: you (console, CLI, SDK, IaC) call APIs checked by IAM and logged in CloudTrail; those run 200+ services on global infrastructure of Regions, Availability Zones and edge locations; every layer is metered by billing.', bigpic(), h=236)

picture = ('  <p><b>Amazon Web Services (AWS)</b> started selling infrastructure to other companies in 2006 with S3 (storage) and EC2 (servers). Today it is the largest cloud provider by revenue. Think of it in four layers:</p>\n' + BIG +
           '\n  <h3>AWS in numbers that matter to you</h3>\n' + table(['Fact', 'Why it matters'], [
               ['More than 200 services', 'you rarely build from scratch — pick a managed service'], ['Dozens of Regions, each with 3+ Availability Zones', 'run near users; survive a data-centre failure'],
               ['India: Mumbai (ap-south-1, 2016) and Hyderabad (ap-south-2, 2022)', 'low latency and data residency for Indian users'], ['Pay as you go + Free Tier', 'learn and start small without upfront cost'],
               ['Everything is an API', 'automation, audit (CloudTrail) and infrastructure as code']], minw=560) +
           '\n  <p>You will count the live number of services and Regions yourself in the hands-on section — numbers grow every year.</p>\n  <h3>The situation that makes companies move to the cloud</h3>\n  <p>TiffinGo’s orders during Diwali week. Own servers are a flat line: paid for and idle on normal days, overwhelmed on the one day that matters. AWS capacity follows the demand curve:</p>\n' + capacity_picture())

SOLVE = launch_scene()

def mapfig():
    o = t(320, 16, 'Seven AWS service families', 11, 'ink', bold=True)
    items = [('1', 'Compute', 'EC2, Lambda, ECS', 'amber'), ('2', 'Storage', 'S3, EBS, EFS', 'green'), ('3', 'Databases', 'RDS, DynamoDB', 'blue'), ('4', 'Networking', 'VPC, Route 53, CloudFront', 'violet'),
             ('5', 'Security & identity', 'IAM, KMS, GuardDuty', 'red'), ('6', 'Analytics & AI', 'Athena, Glue, Bedrock', 'amber'), ('7', 'Management & cost', 'CloudWatch, CloudFormation', 'card')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 8.4, 'ink', bold=True) + t(x + 78, y + 54, b, 6.8, 'ink2')
    o += t(320, 210, 'This course has a module for most families; Module 1 shows how they fit together.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of seven AWS service families: compute, storage, databases, networking, security and identity, analytics and AI, management and cost.', mapfig(), h=222)

def fam(n, name, tone, d, an, ex, tip, A, use, avoid, plain, how, words, diff, rw, pro):
    return vt(n, name, tone, d, an, ex, tip, '', A, use, avoid, plain, how, words, diff, ['CLF-C02 Domain 3', 'SAA-C03', 'C-DAC PGCP-BDA cloud module'], rw, pro)

A1 = mk(['Need to run code', 'Pick the model', 'AWS service'], ['need|run an app|or a job', 'model|server · container|function', 'service|EC2 · ECS/EKS|Lambda'], ['amber', 'blue', 'green'],
        ['you need to run code', 'choose how much you manage: server, container or function', 'the matching AWS service'],
        [('Need', 'Run an app, API or job.', ''), ('Model', 'Server, container or function.', ''), ('Service', 'EC2, ECS/EKS/Fargate, Lambda.', '')],
        'Compute', 'From “run code” to a service.', 'Compute', 'Animation: need to run code; pick the model; AWS service.', 'f1anim')
T1 = fam(1, 'Compute', 'amber',
    '<b>Compute</b> services run your code: <b>EC2</b> virtual servers you manage, containers on <b>ECS</b>/<b>EKS</b> (optionally serverless with <b>Fargate</b>), and event-driven functions on <b>Lambda</b>; plus simpler options such as <b>Elastic Beanstalk</b> and <b>Lightsail</b>.',
    'Kitchens: rent an empty kitchen (EC2), a kitchen with a cooking line set up (containers), or a cook who comes only when an order arrives (Lambda).',
    'TiffinGo runs its website on EC2 and sends order SMS from a Lambda function.',
    'Tip: the less you manage, the less you can misconfigure — prefer the most managed option that fits.', A1,
    'you need CPU and memory to run something.', 'you only need to store files or data — that is storage.',
    'Services that run your programs.',
    [('Need', 'App, API, batch.'), ('Control', 'OS access needed?'), ('Model', 'VM, container, function.'), ('Size', 'Instance type / memory.'), ('Pay', 'Per second / per request.')],
    [('instance', 'a virtual server on EC2'), ('container', 'packaged app with its libraries'), ('function', 'code run per event')],
    table(['Service', 'You manage', 'Billed per'], [['EC2', 'OS and up', 'second (Linux)'], ['ECS on Fargate', 'container image', 'vCPU/GB-second'], ['Lambda', 'code only', 'request + GB-second']], minw=420),
    'Module 3 covers EC2, Auto Scaling, Lambda and Elastic Beanstalk.',
    'Graviton (Arm) instances often give better price-performance — test before you switch.')

A2 = mk(['Kind of data', 'Access pattern', 'AWS service'], ['data|files, disks|archives', 'access|HTTP · block|shared file', 'service|S3 · EBS|EFS · Glacier'], ['green', 'amber', 'blue'],
        ['what kind of data you keep', 'how it is accessed: over HTTP, as a disk, as a shared folder', 'the matching storage service'],
        [('Data', 'Objects, disks, shared files, archives.', ''), ('Access', 'HTTP, block device, NFS.', ''), ('Service', 'S3, EBS, EFS, S3 Glacier.', '')],
        'Storage', 'Data shape decides the service.', 'Storage', 'Animation: kind of data; access pattern; AWS service.', 'f2anim')
T2 = fam(2, 'Storage', 'green',
    '<b>Storage</b> services keep data durably: <b>S3</b> object storage for files and data lakes, <b>EBS</b> block disks for EC2, <b>EFS</b> shared file systems, <b>S3 Glacier</b> classes for archives, and <b>AWS Backup</b> to protect them.',
    'A warehouse (S3), a locker attached to your desk (EBS), a shared office cupboard (EFS), and deep cold storage in the basement (Glacier).',
    'TiffinGo stores menu photos in S3 and its server disk on EBS.',
    'Tip: S3 is designed for 99.999999999% (11 nines) durability — but it does not protect you from deleting your own data; use versioning.', A2,
    'you need to keep files, disks or backups.', 'you need queries with joins — that is a database.',
    'Services that keep your files and disks safe.',
    [('Shape', 'Object, block, file.'), ('Access', 'HTTP, attached, shared.'), ('Durability', 'Copies across AZs.'), ('Class', 'Hot to archive.'), ('Pay', 'GB-month + requests.')],
    [('object', 'file + metadata in a bucket'), ('block', 'raw disk volume'), ('durability', 'chance data is not lost')],
    table(['Service', 'Type', 'Typical use'], [['S3', 'object', 'images, logs, data lakes'], ['EBS', 'block', 'VM disks, databases on EC2'], ['EFS', 'file', 'shared folders for many servers']], minw=420),
    'Module 4 covers S3, EBS/EFS and storage classes.',
    'Storage is cheap per GB; requests and data transfer out often cost more — check both.')

A3 = mk(['Data model', 'Scale + access', 'AWS service'], ['model|tables · keys|cache', 'access|SQL joins|ms lookups', 'service|RDS/Aurora|DynamoDB'], ['blue', 'amber', 'green'],
        ['what your data looks like: related tables, key-value items, cached values', 'how you read it: SQL joins or fast key lookups at scale', 'the matching managed database'],
        [('Model', 'Relational, key-value, cache.', ''), ('Access', 'SQL or key lookups.', ''), ('Service', 'RDS/Aurora, DynamoDB, ElastiCache.', '')],
        'Databases', 'Model + access → engine.', 'Databases', 'Animation: data model; scale and access; AWS service.', 'f3anim')
T3 = fam(3, 'Databases', 'blue',
    '<b>Database</b> services are managed engines: <b>RDS</b> (MySQL, PostgreSQL, MariaDB, Oracle, SQL Server) and <b>Aurora</b> for relational data, <b>DynamoDB</b> for key-value at any scale, <b>ElastiCache</b> for in-memory caching, and purpose-built engines for documents, graphs and time series.',
    'Bank ledgers with linked accounts (relational), a coat-check counter with numbered tokens (key-value), and a sticky note on your monitor for things you need instantly (cache).',
    'TiffinGo keeps customers and orders in RDS PostgreSQL and caches the menu in ElastiCache.',
    'Tip: “managed” means AWS patches, backs up and fails over — you still design tables, indexes and access.', A3,
    'you need to store and query structured data.', 'you only store files — use S3.',
    'Services that store structured data and answer queries.',
    [('Model', 'Relational / NoSQL.'), ('Engine', 'MySQL, PostgreSQL…'), ('HA', 'Multi-AZ.'), ('Scale', 'Replicas / on-demand.'), ('Backups', 'Automatic.')],
    [('relational', 'tables with relationships, SQL'), ('NoSQL', 'non-tabular models, e.g. key-value'), ('Multi-AZ', 'standby copy in another AZ')],
    table(['Service', 'Model', 'Scales by'], [['RDS / Aurora', 'relational', 'bigger instance, read replicas'], ['DynamoDB', 'key-value/document', 'partitions automatically'], ['ElastiCache', 'in-memory', 'nodes / shards']], minw=420),
    'Module 5 covers RDS/Aurora, DynamoDB and ElastiCache.',
    'Choose by access pattern first; migrating between database models later is expensive.')

A4 = mk(['Private network', 'Name + route', 'Deliver fast'], ['network|VPC, subnets|security groups', 'DNS|Route 53|routing policies', 'edge|CloudFront|global caching'], ['violet', 'amber', 'green'],
        ['build a private network for your resources', 'give it a name and route users with DNS', 'deliver content fast from edge locations'],
        [('Network', 'VPC, subnets, security groups.', ''), ('DNS', 'Route 53.', ''), ('Edge', 'CloudFront.', '')],
        'Networking', 'Network → name → edge.', 'Networking', 'Animation: private network; name and route; deliver fast.', 'f4anim')
T4 = fam(4, 'Networking and content delivery', 'violet',
    '<b>Networking</b> services connect and protect resources: <b>VPC</b> private networks with subnets, route tables and security groups; <b>Route 53</b> DNS; <b>CloudFront</b> CDN; <b>Elastic Load Balancing</b>; and private links to offices with <b>Site-to-Site VPN</b> or <b>Direct Connect</b>.',
    'A gated housing society (VPC), its address in the city directory (Route 53), and branch counters across the city so people collect parcels nearby (CloudFront).',
    'tiffingo.in points (Route 53) to CloudFront, which serves images from the nearest edge and forwards orders to servers in a VPC.',
    'Tip: every account gets a default VPC per Region — fine for learning; production uses custom VPCs.', A4,
    'resources must talk to each other, to users or to your office.', 'nothing needs network design — rare in practice.',
    'Services that connect your resources safely and quickly.',
    [('VPC', 'IP range.'), ('Subnets', 'Per AZ.'), ('Rules', 'Security groups.'), ('DNS', 'Route 53.'), ('Edge', 'CloudFront.')],
    [('VPC', 'virtual private cloud network'), ('security group', 'stateful firewall for a resource'), ('edge location', 'CDN site near users')],
    table(['Service', 'Job'], [['VPC', 'private network'], ['Route 53', 'DNS + health checks'], ['CloudFront', 'CDN'], ['ELB', 'spread traffic across servers']], minw=360),
    'Module 6 covers VPC, Route 53 and CloudFront.',
    'Data transfer between AZs and out to the internet is charged — keep chatty components close.')

A5 = mk(['Who', 'What they can do', 'Protect + detect'], ['identity|users, roles|Identity Center', 'permission|IAM policies|least privilege', 'protect|KMS, WAF|GuardDuty'], ['red', 'amber', 'green'],
        ['define who: people and applications', 'define what they can do with IAM policies', 'protect data and detect threats'],
        [('Who', 'Users, groups, roles.', ''), ('What', 'Policies, least privilege.', ''), ('Protect', 'Encryption, firewalls, detection.', '')],
        'Security and identity', 'Identity first.', 'Security', 'Animation: who; what they can do; protect and detect.', 'f5anim')
T5 = fam(5, 'Security, identity and compliance', 'red',
    '<b>Security</b> services control and watch access: <b>IAM</b> and <b>IAM Identity Center</b> for identities and permissions, <b>KMS</b> for encryption keys, <b>WAF</b> and <b>Shield</b> against web attacks and DDoS, <b>GuardDuty</b> for threat detection, <b>Security Hub</b> for posture, and <b>Artifact</b> for compliance reports.',
    'An office: ID cards (identities), access rules per floor (policies), safes (KMS), guards at the gate (WAF/Shield) and CCTV (GuardDuty/CloudTrail).',
    'TiffinGo staff sign in through Identity Center with MFA; the order app uses an IAM role; card data never touches its servers.',
    'Tip: under shared responsibility, AWS secures the cloud; you secure your identities, data and configuration.', A5,
    'anyone or anything needs access, or data must be protected.', 'never — every workload needs this family.',
    'Services that decide who can do what and keep data safe.',
    [('Identity', 'Users, roles.'), ('Policy', 'Allow/deny.'), ('Encrypt', 'KMS.'), ('Shield', 'WAF/DDoS.'), ('Detect', 'GuardDuty, CloudTrail.')],
    [('IAM', 'Identity and Access Management'), ('MFA', 'second factor at sign-in'), ('KMS', 'Key Management Service')],
    table(['Service', 'Job'], [['IAM / Identity Center', 'who can do what'], ['KMS', 'encryption keys'], ['GuardDuty', 'threat detection'], ['Artifact', 'compliance reports']], minw=360),
    'Module 2 covers IAM and security best practices; Security & Compliance is 30% of CLF-C02.',
    'Turn on MFA for root on day one and never create root access keys.')

A6 = mk(['Collect', 'Process + query', 'Insight / AI'], ['collect|Kinesis|S3 data lake', 'process|Glue, EMR|Athena, Redshift', 'use|dashboards|SageMaker, Bedrock'], ['amber', 'blue', 'green'],
        ['collect data into S3 or streams', 'process and query it', 'turn it into dashboards, predictions or generative AI'],
        [('Collect', 'Kinesis streams, S3 data lake.', ''), ('Process', 'Glue, EMR, Athena, Redshift.', ''), ('Use', 'QuickSight, SageMaker, Bedrock.', '')],
        'Analytics and AI', 'Collect → process → insight.', 'Analytics & AI', 'Animation: collect; process and query; insight or AI.', 'f6anim')
T6 = fam(6, 'Analytics, machine learning and AI', 'amber',
    '<b>Analytics and AI</b> services turn data into answers: <b>Kinesis</b> for streams, <b>Glue</b> for ETL and the data catalog, <b>Athena</b> for SQL on S3, <b>Redshift</b> data warehouse, <b>EMR</b> for Spark/Hadoop, <b>QuickSight</b> dashboards, <b>SageMaker</b> for ML and <b>Bedrock</b> for generative AI models.',
    'A newspaper: reporters collect stories (Kinesis), editors clean and arrange them (Glue/EMR), readers search the archive (Athena/Redshift), columnists predict trends (SageMaker).',
    'TiffinGo streams order events, queries them with Athena to find the busiest localities, and forecasts tomorrow’s demand.',
    'Tip: for Big Data learners, S3 + Glue + Athena is the cheapest serverless starting point.', A6,
    'you analyse large data or build ML/AI features.', 'a small app database query is enough.',
    'Services that analyse big data and build AI.',
    [('Collect', 'Streams, files.'), ('Catalog', 'Glue Data Catalog.'), ('Process', 'Spark, ETL.'), ('Query', 'SQL.'), ('Predict', 'ML/GenAI.')],
    [('data lake', 'raw data in S3 for many tools'), ('ETL', 'extract, transform, load'), ('warehouse', 'database optimised for analytics')],
    table(['Service', 'Job'], [['Athena', 'SQL on S3, per TB scanned'], ['Redshift', 'warehouse'], ['EMR', 'Spark/Hadoop clusters'], ['Bedrock', 'foundation models via API']], minw=360),
    'Module 7 covers Glue, Redshift, Athena, Kinesis and EMR — central to the C-DAC Big Data syllabus.',
    'Partition and compress data in S3 (Parquet) — it cuts Athena cost dramatically.')

A7 = mk(['Define', 'Watch', 'Control cost'], ['define|CloudFormation|IaC', 'watch|CloudWatch|CloudTrail', 'cost|Budgets|Cost Explorer'], ['card', 'amber', 'green'],
        ['define infrastructure as code', 'watch metrics, logs and API activity', 'control cost with budgets and reports'],
        [('Define', 'CloudFormation / CDK.', ''), ('Watch', 'CloudWatch, CloudTrail, Config.', ''), ('Cost', 'Budgets, Cost Explorer, tags.', '')],
        'Management and cost', 'Define, watch, control.', 'Management & cost', 'Animation: define; watch; control cost.', 'f7anim')
T7 = fam(7, 'Management, governance and cost', 'card',
    '<b>Management</b> services operate everything else: <b>CloudFormation</b> (infrastructure as code), <b>CloudWatch</b> (metrics, logs, alarms), <b>CloudTrail</b> (API audit), <b>Config</b> (configuration history), <b>Systems Manager</b> (fleet operations), <b>Organizations</b> (many accounts), and <b>Budgets</b>/<b>Cost Explorer</b> for money.',
    'Running a restaurant chain: recipes written down (IaC), kitchen cameras and thermometers (CloudWatch), a visitor register (CloudTrail), and a monthly budget (Budgets).',
    'TiffinGo’s stack is a CloudFormation template; a CloudWatch alarm pages Riya if errors spike; a $20 budget e-mails her at 80%.',
    'Tip: set a budget before anything else — it is the cheapest insurance in the cloud.', A7,
    'you deploy, monitor, audit or pay for anything on AWS.', 'never skip it — unmanaged clouds become expensive and fragile.',
    'Services that set up, watch and control the cost of everything else.',
    [('IaC', 'CloudFormation.'), ('Metrics', 'CloudWatch.'), ('Audit', 'CloudTrail.'), ('Accounts', 'Organizations.'), ('Cost', 'Budgets.')],
    [('IaC', 'infrastructure defined in files'), ('alarm', 'rule on a metric'), ('Organizations', 'manage many AWS accounts')],
    table(['Service', 'Job'], [['CloudFormation', 'deploy from templates'], ['CloudWatch', 'metrics, logs, alarms'], ['CloudTrail', 'who did what'], ['Budgets', 'spending alerts']], minw=360),
    'Module 8 covers CloudWatch, CloudFormation, ECS/EKS and certifications.',
    'CloudTrail event history keeps 90 days of management events for free — create a trail to keep more.')

SUMMARY = table(['#', 'Family', 'Key services', 'Course module'], [
    ['1', 'Compute', 'EC2, Lambda, ECS/EKS, Beanstalk', '3'], ['2', 'Storage', 'S3, EBS, EFS, Glacier', '4'], ['3', 'Databases', 'RDS/Aurora, DynamoDB, ElastiCache', '5'],
    ['4', 'Networking', 'VPC, Route 53, CloudFront, ELB', '6'], ['5', 'Security & identity', 'IAM, KMS, GuardDuty, WAF', '2'], ['6', 'Analytics & AI', 'Glue, Athena, Redshift, Kinesis, EMR, SageMaker, Bedrock', '7'], ['7', 'Management & cost', 'CloudFormation, CloudWatch, CloudTrail, Budgets', '8']], minw=600)

TYPES = ('  <p>Seven AWS service families, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, real-world example and an expert tip.</p>\n'
         + challenge(['Which service gives SQL queries directly on files in S3?', 'Which service records who made an API call?', 'Which compute option needs no server management and bills per request?'], 'types 6, 7 and 1') + MAP
         + jump(['Compute', 'Storage', 'Databases', 'Networking', 'Security', 'Analytics & AI', 'Management']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY)

parts = wwu([
    ('Global infrastructure', 'Regions, AZs, edge locations.', 'Where your resources physically run.', 'Lesson 1.3.'),
    ('Services', '200+ building blocks.', 'Combine instead of building.', 'Seven families above.'),
    ('APIs', 'HTTPS requests signed with credentials.', 'Everything is automatable and auditable.', 'Console, CLI, SDK, IaC.'),
    ('IAM', 'Identity and permissions.', 'Every request is checked.', 'Module 2.'),
    ('Billing', 'Metered usage, Free Tier, budgets.', 'Pay as you go.', 'Lesson 1.2.'),
    ('Support and docs', 'Documentation, re:Post, support plans.', 'Help when stuck.', 'docs.aws.amazon.com.')])

DEEP = ('  <h3>Six advantages of cloud computing (as AWS states them)</h3>\n' + table(['Advantage', 'Meaning', 'TiffinGo example'], [
        ['Trade fixed expense for variable expense', 'pay for what you use, no upfront servers', 'no ₹6 lakh purchase'], ['Benefit from massive economies of scale', 'lower prices from AWS’s scale', 'cheaper than running one server room'],
        ['Stop guessing capacity', 'scale up and down with demand', 'Diwali night handled'], ['Increase speed and agility', 'resources in minutes', 'new feature tested same day'],
        ['Stop spending money running data centres', 'focus on the product', 'no AC, UPS, guards'], ['Go global in minutes', 'deploy in other Regions', 'Dubai expansion without a data centre']], minw=600) +
    '\n  <h3>Control plane vs data plane</h3>\n  <p>The <b>control plane</b> is the set of APIs that create, change and delete resources (RunInstances, CreateBucket). The <b>data plane</b> is the resource doing its job (your instance serving pages, S3 returning an object). AWS designs data planes to keep working even if a control plane has problems — your running server keeps serving while you briefly cannot launch new ones.</p>\n'
    '  <h3>Ways to pay</h3>\n  <ul><li><b>On-Demand:</b> per second/hour, no commitment.</li><li><b>Savings Plans / Reserved Instances:</b> 1- or 3-year commitment for a large discount.</li><li><b>Spot:</b> spare capacity at a big discount, can be interrupted.</li><li><b>Free Tier:</b> credits and always-free limits for learning (Lesson 1.2).</li></ul>')

clouds = vendor_tabs('<p><b>AWS:</b> launched 2006; largest provider by revenue; widest service catalogue; India Regions Mumbai and Hyderabad.</p>',
    '<p><b>Azure:</b> Microsoft’s cloud; strong with Microsoft 365, Windows Server and Entra ID; India Regions Central, South and West India.</p>',
    '<p><b>Google Cloud:</b> strong in data, analytics and AI (BigQuery, Vertex AI); India Regions Mumbai and Delhi.</p>') + \
    cloud3([['Virtual servers', 'EC2', 'Virtual Machines', 'Compute Engine'], ['Object storage', 'S3', 'Blob Storage', 'Cloud Storage'], ['Functions', 'Lambda', 'Azure Functions', 'Cloud Run functions'], ['API audit', 'CloudTrail', 'Activity Log', 'Cloud Audit Logs']])

MOCKA.extend([
 mock('aws', ['Console Home', 'All services'], ['Recently visited', 'All services', 'Favorites'], 'All services', [('Compute', 'EC2 · Lambda · ECS …'), ('Storage', 'S3 · EFS · Backup …'), ('Search', '▾ e.g. Athena')], 'Open'),
 mock('aws', ['CloudTrail', 'Event history'], ['Dashboard', 'Event history', 'Trails'], 'Event history', [('Lookup attributes', '▾ Event name'), ('Value', 'ListBuckets'), ('Columns', 'Event time · User name · Source IP')], 'Apply'),
 mock('aws', ['Billing and Cost Management', 'Free Tier'], ['Home', 'Bills', 'Free Tier', 'Budgets'], 'Free Tier', [('Account plan', 'Free / Paid'), ('Remaining credits', 'USD …'), ('Usage vs limit', 'per service')], 'View details'),
])

STEP1 = astep('1 · Count AWS services and see what Mumbai offers',
    ['Console top-left [[≡ Services]] → [[All services]]: scroll the families from this lesson.', 'Top-right Region menu: count the Regions listed (enabled and “not enabled”).', 'Search box → type <i>Athena</i>, <i>Lambda</i>, <i>CloudTrail</i> — open each to see where it lives.'],
    "# public, read-only list that AWS publishes in Systems Manager Parameter Store\naws ssm get-parameters-by-path --path /aws/service/global-infrastructure/services --query 'length(Parameters)'\naws ssm get-parameters-by-path --path /aws/service/global-infrastructure/regions/ap-south-1/services --query 'length(Parameters)'\naws ssm get-parameters-by-path --path /aws/service/global-infrastructure/regions --query 'length(Parameters)'\n# is Bedrock offered in Mumbai?\naws ssm get-parameters-by-path --path /aws/service/global-infrastructure/regions/ap-south-1/services \\\n  --query \"Parameters[?Value=='bedrock'].Value\" --output text",
    'three numbers — total service identifiers (a few hundred, including sub-services), services offered in Mumbai (fewer), and Regions — then <code>bedrock</code> if it is available in Mumbai.',
    'Not every service is in every Region: always check before you design.')

STEP2 = astep('2 · One action, three ways — and all are API calls in CloudTrail',
    ['Open [[S3]] in the console — the bucket list loads (this is a ListBuckets API call).', 'Wait ~5 minutes, then [[CloudTrail]] → [[Event history]] → Lookup attribute [[Event name]] = <code>ListBuckets</code>.', 'Open an event: see <code>userAgent</code>, <code>sourceIPAddress</code>, <code>userIdentity</code>.'],
    "aws s3api list-buckets --query 'length(Buckets)'                       # 2) the CLI\npython3 -c \"import boto3; print(len(boto3.client('s3').list_buckets()['Buckets']))\"   # 3) the Python SDK\nsleep 300   # CloudTrail delivers events within about 5 minutes\naws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=ListBuckets --max-results 5 \\\n  --query 'Events[].CloudTrailEvent' --output json \\\n  | python3 -c \"import sys,json; [print(e['eventTime'], e['userIdentity']['arn'].split('/')[-1], e['userAgent'][:45]) for e in map(json.loads, json.load(sys.stdin))]\"",
    'the same bucket count twice, then up to five ListBuckets events with your user name and user agents like <code>aws-cli/2…</code>, <code>Boto3/…</code> and the console — one API, three clients.',
    'This is why AWS can be fully automated and audited: there is no “click” that is not an API call.')

STEP3 = astep('3 · Pay-as-you-go in practice: your plan and Free Tier usage',
    ['[[Billing and Cost Management]] → [[Free Tier]]: see your account plan, remaining credits (newer accounts) and usage per service.', '[[Bills]]: this month’s charges by service — likely zero or a few cents.'],
    "aws freetier get-account-plan-state --region us-east-1 \\\n  --query '{plan:accountPlanType,status:accountPlanStatus,credits:accountPlanRemainingCredits.amount,expires:accountPlanExpirationDate}'\naws freetier get-free-tier-usage --region us-east-1 \\\n  --query 'freeTierUsages[].[service,description,actualUsageAmount,limit,unit]' --output table",
    'your plan type (e.g. <code>FREE</code> or <code>PAID</code>), remaining credits, and a table of Free Tier usage against limits. Older accounts may get an error on the first command — the second still works.',
    'Billing data lives in us-east-1 (N. Virginia) whatever Region you work in.')

prac = practical(AWS_INTRO + ' This first lab creates nothing — it only reads public information and your own account data, so it is free.', [AWS_SETUP, STEP1, STEP2, STEP3],
    cleanup='Nothing was created. Run <code>aws sts get-caller-identity</code> once more to confirm you are not root, and keep your budget alert switched on for the rest of the course.')

mist = mistakes([
    ['Thinking AWS = “servers on rent”.', 'EC2 is the famous one.', 'Learn the seven families; managed services save effort.'],
    ['Working as the root user.', 'It is the first login you get.', 'Create an admin user with MFA (Lesson 1.2); lock root away.'],
    ['Assuming every service is in every Region.', 'Global marketing.', 'Check the Region table or the SSM list.'],
    ['No budget alert.', '“I am only learning.”', 'Set a $5 budget before creating anything.'],
    ['Forgetting resources running.', 'Closing the browser does not stop them.', 'Clean up at the end of every lab.'],
    ['Confusing CloudTrail and CloudWatch.', 'Similar names.', 'Trail = who did what; Watch = metrics, logs, alarms.']])

cert = table(['Exam / syllabus', 'What is asked from this lesson'], [['AWS CLF-C02', 'Benefits of cloud (Domain 1); service families and use cases (Domain 3); ways to access AWS — console, CLI, SDK, IaC.'], ['C-DAC PGCP-BDA', 'Cloud platforms overview; AWS as an example public cloud.'], ['Interviews', '“What is AWS? Name services by category.”']], minw=560) + \
    '\n  <h3>Try exam-style questions</h3>\n' + qx('Which AWS service records API calls for auditing?', ['CloudWatch', 'CloudTrail', 'Config', 'Inspector'], 1, 'CloudTrail logs who did what.') + \
    qx('Which is an advantage of cloud computing?', ['trade variable expense for capital expense', 'stop guessing capacity', 'you must buy hardware upfront', 'no security responsibility'], 1, 'One of the six advantages.') + \
    qx('Which ways can you interact with AWS services? (most complete)', ['console only', 'console and CLI only', 'console, CLI, SDKs and IaC — all via APIs', 'only through support tickets'], 2, 'All are API clients.')

proj = miniproject('Mini project: an AWS map for TiffinGo',
    'Map a real app onto AWS service families.',
    ['<b>List</b> TiffinGo’s needs: website, order API, menu images, orders database, SMS, analytics, monitoring, budget.',
     '<b>Map</b> each to a family and one AWS service.',
     '<b>Check</b> with the SSM list that each service is in ap-south-1.',
     '<b>Draw</b> a one-page diagram with the four layers from this lesson.',
     '<b>Compare</b> with Azure and Google Cloud names (table above).'],
    'A one-page diagram and a table of needs → services, all available in Mumbai.', 'This lesson; Cloud Fundamentals Module 10.')

from deep_v3 import HOOD, PRO, PROJ, ROLES, DOMAINS, SIM, NEWBIE, LADDER
assemble_v2(HERE, story_h2='Diwali night and one frozen server', hook_html=hk,
    narration='TiffinGo’s orders jumped ten times on Diwali evening. The office server froze, dinners were late, and Riya had to decide: buy servers that sit idle most of the year, or rent capacity on AWS when needed.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='What is AWS?',
    formal='<b>Amazon Web Services (AWS)</b> is Amazon’s public cloud platform: a global infrastructure of Regions, Availability Zones and edge locations on which more than 200 on-demand services — compute, storage, databases, networking, security, analytics, AI and management — are provided through authenticated APIs and billed on a pay-as-you-go basis.',
    simple='AWS is Amazon renting you computers, storage, databases and many other ready-made services over the internet, and charging only for what you use.',
    interview=['“AWS is Amazon’s cloud: 200+ managed services running on Regions and Availability Zones worldwide, all controlled through APIs and billed per use.”', '“For example, a startup can run its site on EC2, keep images in S3, orders in RDS, and pay per second instead of buying servers.”'],
    terms_rows=[('Service', 'A product such as EC2 or S3.'), ('Region', 'Geographic area with AZs.'), ('Availability Zone', 'Isolated data centre(s) in a Region.'), ('API', 'Programmatic interface; every action uses one.'), ('Console', 'AWS web interface.'), ('CLI', 'Command-line tool.'), ('SDK', 'Library for programming languages.'), ('Free Tier', 'Free credits/limits for learning.')],
    exam='CLF-C02 asks about the six advantages of cloud, service families and how to access AWS (console, CLI, SDK, IaC).',
    picture_h2='AWS in four layers', picture_html=NEWBIE + picture,
    after_picture=[('types', 'Types, one by one', 'Seven AWS service families, one by one', TYPES)],
    how_h2='What happens when you click “Launch”', how_intro='One console click followed through AWS.', how_anim=SOLVE,
    parts_h2='Six parts of AWS', parts_html=parts, lv='',
    myth_rows=[('AWS is only for big companies.', 'Free Tier and per-second billing suit students and startups.', 'Story.'), ('The console and the CLI do different things.', 'Both call the same APIs.', 'Hands-on step 2.'), ('AWS secures everything for me.', 'You secure identities, data and configuration.', 'Type 5.')],
    extra_secs=[('ladder', 'Learn at your level', 'From curious beginner to expert — pick your level', LADDER), ('deep', 'Deep dive', 'Six advantages, control vs data plane, ways to pay', DEEP), ('hood', 'Under the hood', 'Endpoints, request signing, ARNs, limits and consistency', HOOD), ('roles', 'By role', 'How developers, data, ML, DevOps and security people use it', ROLES), ('domains', 'By domain', 'Banking, healthcare, retail, education, IoT, media, government', DOMAINS), ('pro', 'For working professionals', 'Real cases, support plans, Well-Architected, costs, errors, cheat sheet', PRO)],
    clouds_html=clouds, practical_html=prac + '\n  <h3 id="simulator">Practice without an account: simulator</h3>\n  <p>No account yet, or want a dry run? Do the same lab here — every command and click shows what it touches inside AWS.</p>\n' + SIM, mistakes_html=mist, cert_html=cert, project_html=PROJ,
    can_now=['Explain what AWS is in four layers.', 'Name the seven service families with examples.', 'Trace what happens when you launch a resource.', 'Show that console, CLI and SDK make the same API call.', 'Check your Free Tier usage.'],
    next_html='<a href="../02-creating-an-aws-account-and-free-tier/">1.2 Creating an AWS account and free tier</a>.',
    pre='<b>Before you start:</b> nothing — this is the first AWS lesson. Cloud Fundamentals Module 1 helps but is not required.')
