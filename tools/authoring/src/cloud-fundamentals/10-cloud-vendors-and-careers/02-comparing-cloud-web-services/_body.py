import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)
def row3(k, items, tones, cap_):
    o = ''
    for i, l in enumerate(items):
        on = i <= k
        o += box(20 + i * 112, 34, 100, 74, tones[i] if on else 'card', rx=8)
        for j, w in enumerate(l.split('|')): o += t(70 + i * 112, 60 + j * 14, w, 7.2 if j == 0 else 6.6, 'ink', bold=(j == 0))
        if i < 2: o += arrow(120 + i * 112, 71, 132 + i * 112, 71)
    return o + t(180, 132, cap_, 7.2, 'ink', bold=True)
def mk(t3, items, tones, caps, steps, ttl, intro, panel, aria, hid):
    return cap([t(180, 12, t3[k], 9, 'ink', bold=True) + row3(k, items, tones, caps[k]) for k in range(3)], steps, ttl, intro, panel, aria, hid)
def vt(n, name, tone, d, an, sc, ex, gd, anim, use, avoid, plain, how, words, diff, where, rw, pro):
    return vtype(n, name, tone, d, an, sc, ex, gd, anim, use, avoid, plain=plain, how=how, words=words, diff=diff, where=where, realworld=rw, pro=pro)


hk = hook('Kabir learned AWS. His new client runs on Azure, and his friend’s start-up uses Google Cloud. Does he have to learn everything again?',
    'No. Most cloud services come in <b>matching families</b>: VMs, Kubernetes, functions, object storage, managed SQL, NoSQL and data warehouses exist on all three under different names. The skill is knowing the <b>mapping</b> — and the <b>differences that matter</b> (limits, pricing units, defaults). This lesson compares seven service families one by one, animates the same web app built on three clouds, and on <b>your own</b> accounts you benchmark object storage, compare managed databases and inspect serverless runtimes and limits.',
    ['The translation table every multi-cloud engineer keeps in their head.', 'Where “the same” services really differ: limits, defaults and pricing units.', 'Why Kubernetes control planes are priced differently on each cloud.'])

def story_scene():
    o = t(180, 12, 'Same building blocks, different labels', 9, 'ink', bold=True)
    rows = [('VM', 'EC2', 'Virtual Machines', 'Compute Engine'), ('Objects', 'S3', 'Blob Storage', 'Cloud Storage'), ('Functions', 'Lambda', 'Functions', 'Cloud Run functions')]
    for i, (a, b, c, d) in enumerate(rows):
        y = 28 + i * 28
        o += box(8, y, 60, 22, 'card', rx=4) + t(38, y + 15, a, 7.2, 'ink', bold=True)
        for j, (v, tn) in enumerate([(b, 'amber'), (c, 'blue'), (d, 'green')]):
            o += box(74 + j * 96, y, 90, 22, tn, rx=4) + t(119 + j * 96, y + 15, v, 7, 'ink')
    o += t(180, 124, 'Learn the idea once, then the names', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Rows mapping VM to EC2, Virtual Machines, Compute Engine; objects to S3, Blob Storage, Cloud Storage; functions to Lambda, Functions, Cloud Run functions.', story_scene(), 'Concepts transfer; <tspan font-weight="700" class="s-acc">names and limits</tspan> change.', h=132)
dialogue = '''K> Sir, Azure has “resource groups”, Google has “projects”. My AWS notes are useless.
A> Your notes are fine. A VM is a VM; object storage is object storage. You need a translation table plus the differences.
R> Which differences?
A> Limits like how long a function may run, defaults like whether storage is private, and pricing units — per request, per vCPU-second, per GB scanned.
K> Can we test them ourselves?
A> Yes. Same file, three buckets; same database engine, three managed services. Let’s compare family by family.'''

def stackfig():
    o = t(320, 16, 'One web app, three clouds', 11, 'ink', bold=True)
    layers = [('CDN', 'CloudFront', 'Front Door / CDN', 'Cloud CDN'), ('Load balancer', 'ALB', 'Application Gateway / Front Door', 'Cloud Load Balancing'), ('Compute', 'ECS / Lambda', 'Container Apps / Functions', 'Cloud Run'),
              ('Relational DB', 'RDS / Aurora', 'Azure Database for PostgreSQL', 'Cloud SQL / AlloyDB'), ('Objects', 'S3', 'Blob Storage', 'Cloud Storage'), ('Analytics', 'Redshift / Athena', 'Fabric / Synapse', 'BigQuery')]
    o += t(170, 38, 'AWS', 8.4, 'ink', bold=True) + t(350, 38, 'Azure', 8.4, 'ink', bold=True) + t(530, 38, 'Google Cloud', 8.4, 'ink', bold=True)
    for i, (n, a, b, c) in enumerate(layers):
        y = 46 + i * 28
        o += t(70, y + 15, n, 7.4, 'ink', bold=True)
        for j, (v, tn) in enumerate([(a, 'amber'), (b, 'blue'), (c, 'green')]):
            o += box(100 + j * 180, y, 172, 22, tn, rx=4) + t(186 + j * 180, y + 15, v, 7.2, 'ink')
    o += t(320, 228, 'The architecture is identical; only service names, limits and prices differ.', 7.4, 'ink2')
    return o
STACK = bigfig('Six layers (CDN, load balancer, compute, relational DB, objects, analytics) mapped to AWS, Azure and Google Cloud services.', stackfig(), h=236)

picture = ('  <p>The same TiffinGo web app, built on each cloud:</p>\n' + STACK +
           '\n  <h3>Wider translation table</h3>\n' + table(['Need', 'AWS', 'Azure', 'Google Cloud'], [
               ['Virtual machines', 'EC2', 'Virtual Machines', 'Compute Engine'], ['Kubernetes', 'EKS', 'AKS', 'GKE'], ['Serverless containers', 'ECS on Fargate / ECS Express Mode', 'Container Apps', 'Cloud Run'], ['Functions', 'Lambda', 'Azure Functions', 'Cloud Run functions'],
               ['Object storage', 'S3', 'Blob Storage', 'Cloud Storage'], ['File storage', 'EFS / FSx', 'Azure Files / NetApp Files', 'Filestore'], ['Relational DB', 'RDS, Aurora', 'Azure SQL, Database for PostgreSQL/MySQL', 'Cloud SQL, AlloyDB, Spanner'],
               ['NoSQL', 'DynamoDB', 'Cosmos DB', 'Firestore, Bigtable'], ['Data warehouse', 'Redshift', 'Microsoft Fabric / Synapse', 'BigQuery'], ['Messaging', 'SQS, SNS, EventBridge', 'Service Bus, Event Grid', 'Pub/Sub, Eventarc'],
               ['DNS', 'Route 53', 'Azure DNS', 'Cloud DNS'], ['Monitoring', 'CloudWatch', 'Azure Monitor', 'Cloud Monitoring'], ['Generative AI', 'Bedrock', 'Microsoft Foundry / Azure OpenAI', 'Vertex AI (Gemini)']], minw=620))

RN = {'u': (4, 54, 50, 50, 'phone', 'Customer', 'orders'), 'cdn': (66, 4, 62, 46, 'globe', 'CDN', 'static files'), 'lb': (66, 104, 62, 46, 'lb', 'Load balancer', 'HTTPS'),
      'run': (142, 54, 60, 50, 'server', 'Compute', 'container'), 'db': (216, 4, 62, 46, 'db', 'SQL DB', 'orders'), 'obj': (216, 104, 62, 46, 'disk', 'Objects', 'receipts'), 'an': (292, 54, 64, 50, 'chart', 'Analytics', 'daily report')}
RS = [dict(on=['u', 'cdn'], hot='cdn', move=(54, 79, 72, 30, 'menu.jpg'), head='Step 1 · Static files from the CDN', text='Menu images come from the nearest edge: CloudFront, Front Door or Cloud CDN —', text2='same job, slightly different features and pricing per GB.', svc='Difference: edge network size, rules engine, price per GB'),
      dict(on=['u', 'lb'], hot='lb', move=(54, 79, 72, 126, 'POST'), head='Step 2 · The order hits a load balancer', text='ALB (regional), Application Gateway/Front Door, or Google’s global HTTP(S) load', text2='balancer with one anycast IP worldwide.', svc='Difference: Google’s LB is global by default'),
      dict(on=['lb', 'run'], hot='run', move=(128, 127, 150, 90, 'route'), head='Step 3 · A container handles it', text='ECS on Fargate / ECS Express Mode, Container Apps or Cloud Run — all run a container', text2='image and scale it; Cloud Run and Container Apps can scale to zero.', svc='Difference: scale-to-zero, per-request vs per-task billing'),
      dict(on=['run', 'db'], hot='db', move=(202, 66, 226, 30, 'INSERT'), head='Step 4 · The order is saved in managed SQL', text='RDS/Aurora PostgreSQL, Azure Database for PostgreSQL flexible server, or Cloud SQL/', text2='AlloyDB — same SQL, different HA options and pricing.', svc='Difference: HA model, read replicas, storage autoscaling'),
      dict(on=['run', 'obj'], hot='obj', move=(172, 104, 226, 126, 'PUT'), head='Step 5 · The receipt PDF goes to object storage', text='S3, Blob Storage or Cloud Storage: all private by default, all with lifecycle and', text2='versioning; tiers and minimum durations differ.', svc='Difference: tier names, minimum storage periods, request prices'),
      dict(on=list(RN), hot='an', move=(278, 127, 298, 90, 'query'), head='Step 6 · Nightly analytics', text='Redshift (cluster or serverless), Fabric/Synapse, or BigQuery (serverless, priced', text2='per data scanned or reserved slots) builds the daily report.', svc='Difference: pricing unit — node-hours vs GB scanned vs capacity')]
REQ = flow_anim('The same order, three clouds', 'Follow one TiffinGo order through equivalent services — and note what really differs.', 'Equivalent services', 'Animation: CDN serves static files; load balancer; container compute; managed SQL; object storage; analytics, with the key difference on each cloud.', RN, RS, hid='cmpflow')

def mapfig():
    o = t(320, 16, 'Seven service families to compare', 11, 'ink', bold=True)
    items = [('1', 'Virtual machines', 'EC2 · VMs · Compute Engine', 'amber'), ('2', 'Managed Kubernetes', 'EKS · AKS · GKE', 'violet'), ('3', 'Functions', 'Lambda · Functions · Cloud Run fn', 'green'), ('4', 'Object storage', 'S3 · Blob · Cloud Storage', 'blue'),
             ('5', 'Managed relational DB', 'RDS · Azure SQL/PG · Cloud SQL', 'blue'), ('6', 'NoSQL', 'DynamoDB · Cosmos DB · Firestore', 'violet'), ('7', 'Data warehouse', 'Redshift · Fabric · BigQuery', 'green')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 7.8, 'ink', bold=True) + t(x + 78, y + 54, b, 6, 'ink2')
    o += t(320, 210, 'For each: what is the same, what differs, and when the difference matters.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of seven service families: virtual machines, managed Kubernetes, functions, object storage, managed relational databases, NoSQL, data warehouses.', mapfig(), h=222)

A1 = mk(['Pick a size', 'Attach disks + network', 'Pay per second'], ['size|families, vCPU|RAM, CPU vendor', 'disk + net|EBS / managed disk|PD / Hyperdisk', 'billing|per second*|discount models'], ['amber', 'blue', 'green'],
        ['all three offer VM families with similar names and shapes', 'network disks and virtual networks attach in the same way', 'billing per second (with minimums) plus commitment discounts'],
        [('Size', 'Similar families: general, compute, memory, GPU.', ''), ('Attach', 'Network disks and virtual networks.', ''), ('Bill', 'Per-second billing with minimums; discounts differ.', '')],
        'VMs compared', 'Most similar family.', 'VMs', 'Animation: pick a size; attach disks and network; pay per second.', 'w1anim')
T1 = vt(1, 'Virtual machines', 'amber',
    'All three providers offer <b>virtual machines</b> in comparable families (general purpose, burstable, compute-, memory-, storage-optimised, GPU) on Intel, AMD and their own ARM chips (AWS Graviton, Azure Cobalt, Google Axion), with network block storage, per-second billing (with short minimums) and commitment and spot discounts.',
    'Renting the same model of car from three agencies: same seats and engine, different contract terms and loyalty schemes.',
    'TiffinGo priced a 2-vCPU, 8 GB VM in all three India Regions (10.1 step 3); the list prices were within a few percent — discounts and right-sizing mattered more.',
    'EC2; Azure Virtual Machines; Compute Engine.', 'VM families are in Lesson 2.1.', A1,
    'you need OS control — the family is nearly identical everywhere.',
    'you compare names instead of vCPU/RAM/generation/Region.',
    'Rented virtual servers — nearly the same on every cloud.',
    [('Family', 'Purpose letter/series.'), ('Size', 'vCPU, RAM.'), ('Image', 'OS image.'), ('Disk', 'Network block storage.'), ('Discount', 'Savings Plans / reservations / CUDs / Spot.')],
    [('ARM instance', 'VM on ARM chips — usually cheaper'), ('sustained use discount', 'Google’s automatic discount on some families'), ('spot VM', 'cheap interruptible capacity')],
    table(['', 'AWS', 'Azure', 'Google Cloud'], [['Own ARM chip', 'Graviton', 'Cobalt', 'Axion'], ['Automatic discount', '—', '—', 'sustained use (some families)'], ['Spot notice', '2 min', '30 s', '30 s']], minw=480),
    ['Lift-and-shift', 'Legacy apps', 'Special software'],
    'Interruption notices differ: AWS Spot gives a two-minute warning; Azure and Google Spot VMs give about 30 seconds — design checkpoints accordingly.',
    'Translate sizes by shape, not name: m7i.large ≈ D2s v5 ≈ n4-standard-2 (2 vCPU, 8 GiB).')

A2 = mk(['Control plane', 'Node pools', 'Add-ons'], ['control plane|managed|price differs', 'nodes|VMs or serverless|Autopilot / Fargate', 'add-ons|ingress, CSI|identity'], ['violet', 'blue', 'green'],
        ['each provider runs the Kubernetes control plane for you', 'workers run as node pools, or serverless options manage nodes too', 'networking, storage and identity add-ons integrate with each cloud'],
        [('Control plane', 'Managed by the provider; pricing differs.', ''), ('Nodes', 'Node pools or serverless nodes (Autopilot, Fargate, Auto Mode).', ''), ('Add-ons', 'Cloud-specific load balancers, storage, identity.', '')],
        'Managed Kubernetes compared', 'Same Kubernetes, different extras.', 'Kubernetes', 'Animation: control plane; node pools; add-ons.', 'w2anim')
T2 = vt(2, 'Managed Kubernetes', 'violet',
    '<b>Managed Kubernetes</b> services — Amazon EKS, Azure Kubernetes Service and Google Kubernetes Engine — run conformant Kubernetes control planes for you and integrate with each cloud’s networking, load balancers, storage and identity; they differ in control-plane pricing, upgrade cadence, node automation (GKE Autopilot, EKS Auto Mode/Fargate, AKS Automatic) and default networking.',
    'Three franchises of the same restaurant chain: the recipes (Kubernetes) are identical, the building, staff contracts and delivery partners are local.',
    'TiffinGo’s Helm charts deploy unchanged to EKS and GKE; only the ingress annotations and storage classes differ.',
    'EKS (control plane billed per cluster-hour), AKS (free control-plane tier; paid Standard tier with SLA), GKE (cluster management fee with a free-tier credit covering one cluster per billing account).', 'Containers are in Lesson 4.5.', A2,
    'you already use Kubernetes or need portability across clouds.',
    'a simpler serverless container service (Cloud Run, Container Apps, ECS) would do.',
    'Kubernetes run for you by each cloud — the same Kubernetes, with different extras.',
    [('Create', 'Cluster + node pool.'), ('Identity', 'IRSA/Pod Identity, Workload ID.'), ('Ingress', 'Cloud load balancer controller.'), ('Storage', 'CSI drivers.'), ('Upgrade', 'Release channels.')],
    [('control plane', 'Kubernetes API server and scheduler'), ('node pool', 'group of worker VMs'), ('release channel', 'automatic upgrade track')],
    table(['', 'EKS', 'AKS', 'GKE'], [['Control-plane fee', 'per cluster-hour', 'free tier / paid SLA tier', 'per cluster-hour, one free via credit'], ['Fully managed nodes', 'Auto Mode / Fargate', 'AKS Automatic', 'Autopilot'], ['Kubernetes origin', '—', '—', 'Google created Kubernetes']], minw=500),
    ['Microservices', 'Platform teams', 'Multi-cloud portability'],
    'Kubernetes was open-sourced by Google in 2014 and donated to the CNCF; all three services pass CNCF conformance tests, which is why manifests move between them.',
    'Portability is in the manifests, not the add-ons: ingress classes, storage classes and identity bindings are the parts you rewrite per cloud.')

A3 = mk(['Event arrives', 'Function runs', 'Billed per use'], ['event|HTTP, queue|upload, timer', 'run|managed runtime|limits differ', 'bill|requests + GB-s|free monthly grant'], ['green', 'amber', 'green'],
        ['an event triggers code', 'the platform runs it within its limits (time, memory, concurrency)', 'you pay per request and compute time; each has a free grant'],
        [('Event', 'HTTP, queue, upload or timer.', ''), ('Run', 'Managed runtime with limits on time, memory, concurrency.', ''), ('Bill', 'Per request + compute time; monthly free grant.', '')],
        'Functions compared', 'Same idea, different limits.', 'Functions', 'Animation: event arrives; function runs; billed per use.', 'w3anim')
T3 = vt(3, 'Functions (FaaS)', 'green',
    '<b>Function services</b> — AWS Lambda, Azure Functions and Google Cloud Run functions — run event-triggered code without servers, billed per invocation and compute time with monthly free grants; they differ in maximum run time, memory, triggers, hosting plans (Azure Consumption, Flex Consumption, Premium) and how they relate to containers (Cloud Run functions run on Cloud Run).',
    'Three taxi apps: you only pay for rides, but the maximum trip length and surge rules differ.',
    'TiffinGo’s invoice function: on Lambda it fits in the 15-minute limit; a long monthly report job was moved to Cloud Run because HTTP functions there can run up to 60 minutes.',
    'Lambda (max 15 minutes, up to 10,240 MB); Azure Functions (limits depend on plan; Consumption is shortest, Flex/Premium longer); Cloud Run functions (HTTP up to 60 minutes, event-driven up to 9 minutes).', 'Serverless is Lesson 2.4.', A3,
    'short, event-driven tasks with spiky traffic.',
    'long-running or constantly busy work — containers or VMs are cheaper.',
    'Small pieces of code that run only when something happens — each cloud has slightly different limits.',
    [('Trigger', 'Event source.'), ('Runtime', 'Python, Node, Java, .NET…'), ('Limits', 'Time, memory, payload.'), ('Scale', 'Concurrency controls.'), ('Bill', 'Requests + GB-seconds.')],
    [('GB-second', 'memory × duration billing unit'), ('cold start', 'delay when a new instance starts'), ('hosting plan', 'Azure Functions pricing/limits option')],
    table(['', 'Lambda', 'Azure Functions', 'Cloud Run functions'], [['Max duration', '15 min', 'plan-dependent', '60 min HTTP / 9 min events'], ['Built on', 'Firecracker micro-VMs', 'App Service / Flex infra', 'Cloud Run containers'], ['Free grant', '1M requests/month', 'per plan (Consumption/Flex)', '2M requests/month']], minw=520),
    ['Webhooks', 'File processing', 'Scheduled jobs'],
    'Google merged Cloud Functions into Cloud Run as “Cloud Run functions” in 2024, so a function is a container service under the hood.',
    'Always check the limit table before designing — time limits, payload sizes and concurrency defaults are the real portability problems.')

A4 = mk(['Bucket / container', 'Objects + tiers', 'Lifecycle + access'], ['bucket|S3 bucket|storage account container', 'tiers|Standard → archive|minimum durations', 'controls|lifecycle, versions|private by default'], ['blue', 'amber', 'green'],
        ['data lives in buckets (Azure: containers inside storage accounts)', 'each offers hot-to-archive tiers with different minimum storage durations', 'lifecycle, versioning and private-by-default access exist on all three'],
        [('Container', 'Buckets (Azure: storage account → container).', ''), ('Tiers', 'Hot to archive; minimum durations differ.', ''), ('Controls', 'Lifecycle, versioning, private by default.', '')],
        'Object storage compared', 'Very similar, different tiers.', 'Object storage', 'Animation: bucket; tiers; lifecycle and access.', 'w4anim')
T4 = vt(4, 'Object storage', 'blue',
    '<b>Object storage</b> — Amazon S3, Azure Blob Storage and Google Cloud Storage — stores unlimited objects in buckets/containers with HTTP APIs, 11-nines durability designs, storage tiers from hot to archive, lifecycle rules, versioning and private-by-default access; differences include Azure’s extra storage-account level, tier names and minimum storage durations, request pricing and redundancy options.',
    'Three godown companies: all store your boxes safely and charge by space and handling, but their cold-storage rules and paperwork differ.',
    'TiffinGo keeps receipts in S3 Standard-IA after 30 days; the same policy on Azure uses the Cool tier, on Google the Nearline class.',
    'S3 (Standard, Intelligent-Tiering, IA, Glacier tiers); Blob (Hot, Cool, Cold, Archive); Cloud Storage (Standard, Nearline, Coldline, Archive).', 'Storage tiers are in Lesson 6.2.', A4,
    'files, media, backups, data lakes — on any cloud.',
    'you need a file system (use file storage) or low-latency block disks.',
    'Online storage for files of any size — all clouds offer it, with different tier names.',
    [('Create', 'Bucket / storage account + container.'), ('Upload', 'API, CLI, SDK.'), ('Protect', 'Private, encryption, versioning.'), ('Tier', 'Lifecycle rules.'), ('Serve', 'Signed URLs, CDN.')],
    [('storage account', 'Azure’s top-level storage resource that holds containers'), ('minimum storage duration', 'billed minimum time for cold tiers'), ('redundancy', 'how many copies, where (LRS, ZRS, GRS…)')],
    table(['Tier idea', 'AWS', 'Azure', 'Google Cloud'], [['Frequent', 'Standard', 'Hot', 'Standard'], ['Monthly', 'Standard-IA (30 d min)', 'Cool (30 d)', 'Nearline (30 d)'], ['Quarterly', 'Glacier Instant Retrieval (90 d)', 'Cold (90 d)', 'Coldline (90 d)'], ['Archive', 'Glacier Deep Archive (180 d)', 'Archive (180 d)', 'Archive (365 d)']], minw=520),
    ['Data lakes', 'Backups', 'Media'],
    'Google Cloud Storage offers dual- and multi-region buckets with a single name and strong consistency; S3 uses Regional buckets plus optional replication.',
    'Request costs dominate for millions of tiny objects — batch small files before comparing per-GB prices.')

A5 = mk(['Choose engine', 'Managed operations', 'HA + replicas'], ['engine|PostgreSQL, MySQL|SQL Server, Oracle', 'managed|patching, backups|monitoring', 'HA|standby, replicas|failover time'], ['blue', 'green', 'amber'],
        ['the same open-source engines run on all three', 'the provider handles patching, backups and monitoring', 'high availability and replica options differ in design and price'],
        [('Engine', 'PostgreSQL, MySQL, SQL Server (and Oracle on AWS).', ''), ('Managed', 'Patching, backups, monitoring by the provider.', ''), ('HA', 'Standby, replicas and failover differ.', '')],
        'Managed SQL compared', 'Same SQL, different engines around it.', 'Managed SQL', 'Animation: choose engine; managed operations; HA and replicas.', 'w5anim')
T5 = vt(5, 'Managed relational databases', 'blue',
    '<b>Managed relational databases</b> — Amazon RDS and Aurora, Azure SQL Database/Managed Instance and Azure Database for PostgreSQL/MySQL, Google Cloud SQL, AlloyDB and Spanner — run standard SQL engines with provider-managed patching, backups and high availability; they differ in supported engines, high-availability architecture, storage design (e.g. Aurora and AlloyDB’s separated storage), global options (Spanner) and pricing.',
    'Three hospitals with the same medicines: the treatment (SQL) is the same, but rooms, specialists and billing differ.',
    'TiffinGo’s orders database is PostgreSQL 16: it could run on RDS, Azure Database for PostgreSQL flexible server or Cloud SQL with the same schema; practical step 2 lists versions and sizes on each.',
    'RDS (PostgreSQL, MySQL, MariaDB, SQL Server, Oracle, Db2), Aurora; Azure SQL family, Database for PostgreSQL/MySQL flexible server; Cloud SQL (PostgreSQL, MySQL, SQL Server), AlloyDB, Spanner.', '', A5,
    'you need SQL with transactions and do not want to run database servers.',
    'you need extreme global write scale (consider Spanner/Cosmos DB/DynamoDB) or unsupported extensions.',
    'Databases using normal SQL, run for you by the cloud — the same SQL on every cloud.',
    [('Engine + version', 'Match your app.'), ('Size', 'vCPU/RAM, storage.'), ('HA', 'Multi-AZ / zone-redundant / regional.'), ('Backups', 'PITR retention.'), ('Access', 'Private networking, IAM auth.')],
    [('PITR', 'point-in-time recovery'), ('read replica', 'copy for read traffic'), ('Multi-AZ', 'standby in another zone')],
    table(['', 'AWS', 'Azure', 'Google Cloud'], [['Cloud-native PostgreSQL-compatible', 'Aurora', 'Azure Cosmos DB for PostgreSQL (distributed)', 'AlloyDB'], ['Global relational', 'Aurora DSQL', '—', 'Spanner'], ['Oracle engine', 'RDS for Oracle', 'Oracle Database@Azure', 'Oracle Database@Google Cloud']], minw=520),
    ['Transactional apps', 'ERP', 'SaaS back ends'],
    'Aurora and AlloyDB both separate compute from distributed storage to speed up failover and replicas — a design pattern, not just a product name.',
    'Compare HA failover times and what “HA” costs (often doubling instance price) — not just the base instance price.')

A6 = mk(['Key-value / document', 'Scale automatically', 'Pick consistency'], ['model|key-value, JSON|wide-column', 'scale|partitions|serverless options', 'consistency|strong / eventual|levels'], ['violet', 'blue', 'green'],
        ['NoSQL stores items by key, documents or wide columns', 'they scale horizontally by partitioning, often serverlessly', 'consistency options differ — Cosmos DB offers five levels'],
        [('Model', 'Key-value, document or wide-column.', ''), ('Scale', 'Partitioned, often serverless.', ''), ('Consistency', 'Strong or eventual; Cosmos DB has five levels.', '')],
        'NoSQL compared', 'Fast at scale, by key.', 'NoSQL', 'Animation: data models; automatic scale; consistency choices.', 'w6anim')
T6 = vt(6, 'NoSQL databases', 'violet',
    '<b>Managed NoSQL databases</b> — Amazon DynamoDB, Azure Cosmos DB and Google Firestore/Bigtable — store key-value, document or wide-column data with horizontal scaling and millisecond latency; they differ in data model, query capability, consistency options (DynamoDB strong/eventual reads, Cosmos DB five consistency levels, Firestore strong), multi-Region writes and pricing units (capacity units, request units, operations).',
    'Locker rooms with numbered lockers: you can fetch any locker instantly by number, but searching for “all red bags” is slow unless you planned an index.',
    'TiffinGo stores live rider locations in DynamoDB keyed by rider ID; a Google-based team would use Firestore, an Azure team Cosmos DB — the access pattern design is the same.',
    'DynamoDB (on-demand/provisioned, global tables); Cosmos DB (RU/s, multiple APIs incl. NoSQL, MongoDB, Cassandra, Gremlin, Table; free tier); Firestore (document, offline sync), Bigtable (wide-column, analytics-scale).', '', A6,
    'access patterns are known, scale is high and joins are rare.',
    'you need ad-hoc queries and joins — use SQL.',
    'Very fast databases that look up data by key and grow automatically — each cloud has its own.',
    [('Access patterns', 'Design keys first.'), ('Partition key', 'Spread load.'), ('Indexes', 'Secondary indexes.'), ('Capacity', 'On-demand vs provisioned.'), ('Replication', 'Global tables / multi-region.')],
    [('partition key', 'key that decides where data is stored'), ('RU', 'Cosmos DB request unit'), ('global table', 'multi-Region replicated DynamoDB table')],
    table(['', 'DynamoDB', 'Cosmos DB', 'Firestore'], [['Pricing unit', 'read/write request units or capacity', 'request units (RU/s)', 'operations + storage'], ['Consistency', 'eventual or strong reads', '5 levels', 'strong'], ['APIs', 'DynamoDB API', 'NoSQL, MongoDB, Cassandra, Gremlin, Table', 'Firestore API']], minw=520),
    ['Sessions and carts', 'IoT and gaming', 'Mobile apps'],
    'Cosmos DB’s multiple APIs let teams migrate MongoDB or Cassandra apps with fewer code changes — a key differentiator when comparing NoSQL services.',
    'NoSQL portability is low: data models and query APIs differ. Choose deliberately; migrating later means rewriting data access.')

A7 = mk(['Load data', 'Query with SQL', 'Pay by unit'], ['load|batch, stream|from data lake', 'query|SQL at scale|columnar', 'pricing|nodes / RPUs|GB scanned / slots'], ['green', 'blue', 'amber'],
        ['data is loaded or queried directly from the data lake', 'columnar engines run SQL over billions of rows', 'pricing differs: provisioned nodes, serverless capacity, or data scanned'],
        [('Load', 'Batch, streaming or direct from the data lake.', ''), ('Query', 'Columnar SQL over huge tables.', ''), ('Pay', 'Nodes/capacity units vs data scanned vs reserved slots.', '')],
        'Data warehouses compared', 'Big SQL, different meters.', 'Warehouse', 'Animation: load data; query with SQL; pay by unit.', 'w7anim')
T7 = vt(7, 'Data warehouses', 'green',
    '<b>Cloud data warehouses</b> — Amazon Redshift (provisioned and Serverless), Microsoft Fabric Warehouse (successor path for Synapse dedicated pools) and Google BigQuery — run analytical SQL on columnar storage at petabyte scale and integrate with data lakes; their main differences are architecture (clusters vs serverless), pricing units (node-hours/RPU-hours, capacity units, bytes scanned or slot reservations) and ecosystem integration.',
    'Three printing presses for very large newspapers: all print fast, but one charges per hour of press time and another per page printed.',
    'TiffinGo’s daily demand report scans 40 GB in BigQuery (pay per data scanned); the same report on Redshift Serverless is billed by compute capacity used.',
    'Redshift, Athena (query S3 directly); Microsoft Fabric (OneLake, Warehouse, Lakehouse), Synapse; BigQuery (on-demand per TiB scanned or editions with slots), BigQuery Omni.', 'The Big Data track covers Hive and Spark — warehouses are their managed cousins.', A7,
    'many users run SQL analytics over large data.',
    'you need row-by-row transactional updates — use a relational database.',
    'Huge SQL databases for analysing data — each cloud charges in a different way.',
    [('Ingest', 'Batch/stream.'), ('Model', 'Star schemas, partitions.'), ('Query', 'SQL, BI tools.'), ('Optimise', 'Partition/cluster, materialised views.'), ('Control cost', 'Quotas, reservations.')],
    [('columnar', 'stores data by column for fast scans'), ('slot', 'BigQuery unit of compute capacity'), ('RPU', 'Redshift Serverless processing unit')],
    table(['', 'Redshift', 'Fabric', 'BigQuery'], [['Model', 'clusters or serverless', 'SaaS capacity (F SKUs)', 'serverless'], ['Pricing', 'node-hours / RPU-hours', 'capacity units', 'TiB scanned or slots'], ['Data lake', 'S3 (Spectrum/Athena)', 'OneLake', 'Cloud Storage / BigLake']], minw=500),
    ['BI and reporting', 'Data science', 'Log analytics'],
    'BigQuery’s on-demand model charges per TiB scanned, so partitioning and selecting only needed columns can cut costs dramatically.',
    'Put a maximum-bytes-billed limit on BigQuery queries and per-workgroup limits on Athena/Redshift to avoid accidental huge scans.')

SUMMARY = table(['#', 'Family', 'AWS', 'Azure', 'Google Cloud', 'Key difference'], [
    ['1', 'VMs', 'EC2', 'Virtual Machines', 'Compute Engine', 'discount models, ARM chips'], ['2', 'Kubernetes', 'EKS', 'AKS', 'GKE', 'control-plane price, node automation'], ['3', 'Functions', 'Lambda', 'Functions', 'Cloud Run functions', 'time limits, plans'],
    ['4', 'Objects', 'S3', 'Blob Storage', 'Cloud Storage', 'tier names, min durations'], ['5', 'SQL', 'RDS/Aurora', 'Azure SQL / DB for PG', 'Cloud SQL/AlloyDB/Spanner', 'HA design, engines'], ['6', 'NoSQL', 'DynamoDB', 'Cosmos DB', 'Firestore/Bigtable', 'APIs, consistency, pricing unit'], ['7', 'Warehouse', 'Redshift', 'Fabric', 'BigQuery', 'pricing unit']], minw=680)
CHECK = ('  <h3>Check yourself: which service?</h3>\n' +
    qx('A. Azure equivalent of Amazon S3.', ['Blob Storage', 'Azure Files only', 'Cosmos DB', 'Azure Disk'], 0, 'Blob.') +
    qx('B. Google equivalent of AWS Lambda.', ['Cloud Run functions', 'BigQuery', 'GKE', 'Filestore'], 0, 'Cloud Run functions.') +
    qx('C. NoSQL with five consistency levels and MongoDB API.', ['Cosmos DB', 'DynamoDB', 'Bigtable', 'Redshift'], 0, 'Cosmos DB.') +
    qx('D. Warehouse priced per TiB scanned on demand.', ['BigQuery', 'RDS', 'AKS', 'EBS'], 0, 'BigQuery on-demand.'))

TYPES = ('  <p>Seven families, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['Which function service can run an HTTP request for an hour?', 'Which archive tier has a 365-day minimum?', 'Why is NoSQL hard to move between clouds?'], 'types 3, 4 and 6') + MAP
         + jump(['VMs', 'Kubernetes', 'Functions', 'Objects', 'SQL', 'NoSQL', 'Warehouse']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('Limits and quotas', 'Max sizes, durations, rates.', 'Decide whether a design fits.', 'Function timeouts, object sizes.'),
    ('Pricing units', 'What you are billed for.', 'Same workload, different bills.', 'Requests, GB-s, RU/s, TiB scanned.'),
    ('Defaults', 'What is on/off out of the box.', 'Security and cost surprises.', 'Private storage, encryption, public IPs.'),
    ('SLAs', 'Promised availability.', 'Design for the real number.', 'Zone vs Region SLAs (5.4).'),
    ('APIs and SDKs', 'How code talks to the service.', 'Portability and lock-in.', 'S3 API widely copied; NoSQL APIs differ.'),
    ('Regional availability', 'Is the service in your Region?', 'Residency and latency.', 'Check India Regions per service.')])

DEEP = ('  <h3>Portability ladder</h3>\n' + table(['Most portable', '→', 'Least portable'], [['VMs, containers, Kubernetes, PostgreSQL/MySQL', 'object storage (S3 API widely copied), managed Kafka/Redis', 'NoSQL APIs, serverless event wiring, data warehouses’ SQL dialects and pricing, AI platform SDKs']], minw=560) +
    '\n  <h3>How to compare a service in 15 minutes</h3>\n  <ol><li>Read the <b>limits/quotas</b> page.</li><li>Read the <b>pricing</b> page: find the billing unit and free tier.</li><li>Check <b>Region availability</b> for your Regions.</li><li>Check the <b>SLA</b>.</li><li>Run a <b>tiny test</b> (practical steps).</li></ol>\n'
    '  <h3>Service name changes to watch</h3>\n  <p>Cloud names change: Cloud Functions → Cloud Run functions, Azure AI Foundry → Microsoft Foundry, Azure Stack HCI → Azure Local, AWS App Runner closed to new customers, Synapse dedicated pools → Fabric Warehouse path. Exams lag behind product changes — learn both names during transitions.</p>')

clouds = vendor_tabs('<p><b>AWS:</b> EC2, EKS, Lambda, S3, RDS/Aurora, DynamoDB, Redshift/Athena, SQS/SNS/EventBridge, CloudFront, Bedrock.</p>',
    '<p><b>Azure:</b> Virtual Machines, AKS, Functions, Blob Storage, Azure SQL / Database for PostgreSQL, Cosmos DB, Microsoft Fabric, Service Bus/Event Grid, Front Door, Microsoft Foundry.</p>',
    '<p><b>Google Cloud:</b> Compute Engine, GKE, Cloud Run (and functions), Cloud Storage, Cloud SQL/AlloyDB/Spanner, Firestore/Bigtable, BigQuery, Pub/Sub, Cloud CDN, Vertex AI.</p>') + \
    cloud3([['VMs', 'EC2', 'Virtual Machines', 'Compute Engine'], ['Kubernetes', 'EKS', 'AKS', 'GKE'], ['Functions', 'Lambda', 'Functions', 'Cloud Run functions'], ['Objects', 'S3', 'Blob Storage', 'Cloud Storage'], ['SQL', 'RDS / Aurora', 'Azure SQL / DB for PostgreSQL', 'Cloud SQL / AlloyDB'], ['NoSQL', 'DynamoDB', 'Cosmos DB', 'Firestore'], ['Warehouse', 'Redshift', 'Fabric', 'BigQuery']])

MOCKQ.extend([
 (mock('aws', ['S3', 'tiffingo-bench', 'Upload'], ['Objects', 'Properties', 'Permissions'], 'Objects', [('File', 'bench-50mb.bin'), ('Storage class', '▾ Standard')], 'Upload'),
  mock('az', ['Storage account', 'Containers', 'bench', 'Upload'], ['Overview', 'Containers'], 'Containers', [('File', 'bench-50mb.bin'), ('Access tier', '▾ Hot')], 'Upload'),
  mock('gcp', ['Cloud Storage', 'tiffingo-bench', 'Upload'], ['Objects', 'Configuration'], 'Objects', [('File', 'bench-50mb.bin'), ('Storage class', 'Standard')], 'Upload files')),
 (mock('aws', ['RDS', 'Create database'], ['Databases', 'Snapshots', 'Parameter groups'], 'Databases', [('Engine', '▾ PostgreSQL'), ('Engine version', '▾ PostgreSQL 16.x / 17.x'), ('Templates', '[x] Free tier')], 'Create database'),
  mock('az', ['Azure Database for PostgreSQL flexible servers', 'Create'], ['Basics', 'Networking', 'Security'], 'Basics', [('PostgreSQL version', '▾ 16 / 17'), ('Compute + storage', 'Burstable B1ms'), ('High availability', '[x] Zone redundant')], 'Review + create'),
  mock('gcp', ['SQL', 'Create instance', 'PostgreSQL'], ['Instances', 'Backups'], 'Instances', [('Database version', '▾ PostgreSQL 16 / 17'), ('Edition', '▾ Enterprise'), ('Availability', '[x] Multiple zones')], 'Create instance')),
 (mock('aws', ['Lambda', 'Account settings'], ['Dashboard', 'Functions'], 'Dashboard', [('Concurrent executions', 'account limit'), ('Max timeout', '15 min · memory up to 10,240 MB')], 'Create function'),
  mock('az', ['Function App', 'Create', 'Hosting'], ['Basics', 'Storage', 'Networking'], 'Basics', [('Hosting option', '▾ Flex Consumption / Premium / App Service'), ('Runtime stack', '▾ Python 3.12')], 'Review + create'),
  mock('gcp', ['Cloud Run', 'Write a function'], ['Services', 'Jobs'], 'Services', [('Runtime', '▾ Python 3.12'), ('Request timeout', 'up to 3600 s (HTTP)')], 'Create')),
])

STEP1 = ('1 · Benchmark object storage from your own Cloud Shell', tri(
    (['Create a bucket in Mumbai → [[Upload]] a test file → download it; note the time.'],
     "head -c 50M /dev/urandom > bench-50mb.bin\nB=tiffingo-bench-$RANDOM; aws s3 mb s3://$B --region ap-south-1\n/usr/bin/time -f 'upload %e s' aws s3 cp bench-50mb.bin s3://$B/ --only-show-errors\n/usr/bin/time -f 'download %e s' aws s3 cp s3://$B/bench-50mb.bin /tmp/b.bin --only-show-errors",
     'two timings in seconds. CloudShell runs in the console’s Region, so this measures intra-Region throughput; from your laptop it measures your internet link.'),
    (['Create a storage account (Central India) → container <code>bench</code> → [[Upload]] → download.'],
     "head -c 50M /dev/urandom > bench-50mb.bin\naz group create -n rg-cmp -l centralindia >/dev/null\nSA=tgbench$RANDOM; az storage account create -n $SA -g rg-cmp -l centralindia --sku Standard_LRS >/dev/null\nKEY=$(az storage account keys list -n $SA -g rg-cmp --query [0].value -o tsv)\naz storage container create --account-name $SA --account-key $KEY -n bench >/dev/null\n/usr/bin/time -f 'upload %e s' az storage blob upload --account-name $SA --account-key $KEY -c bench -f bench-50mb.bin -n bench-50mb.bin --only-show-errors >/dev/null\n/usr/bin/time -f 'download %e s' az storage blob download --account-name $SA --account-key $KEY -c bench -n bench-50mb.bin -f /tmp/b.bin --only-show-errors >/dev/null",
     'upload and download timings. Azure Cloud Shell may run in a different Region from your storage account — note where it is (<code>echo $ACC_LOCATION</code>).'),
    (['Create a bucket in asia-south1 → [[Upload files]] → download.'],
     "head -c 50M /dev/urandom > bench-50mb.bin\nB=tiffingo-bench-$RANDOM; gcloud storage buckets create gs://$B --location=asia-south1 --quiet\n/usr/bin/time -f 'upload %e s' gcloud storage cp bench-50mb.bin gs://$B/ --no-user-output-enabled\n/usr/bin/time -f 'download %e s' gcloud storage cp gs://$B/bench-50mb.bin /tmp/b.bin --no-user-output-enabled",
     'upload and download timings. Cloud Shell VMs are in a Region near you but not necessarily Mumbai.')),
    'Benchmarks only compare fairly when the client location is the same — write down where each test ran.')

STEP2 = ('2 · Compare managed PostgreSQL offerings (read-only)', tri(
    (['[[RDS]] → [[Create database]] → [[PostgreSQL]] → look at engine versions, instance classes, Multi-AZ options and the Free tier template — then cancel.'],
     "aws rds describe-db-engine-versions --engine postgres --region ap-south-1 --query 'DBEngineVersions[-5:].EngineVersion' --output text\naws rds describe-orderable-db-instance-options --engine postgres --db-instance-class db.t4g.micro --region ap-south-1 --query 'OrderableDBInstanceOptions[0].[DBInstanceClass,MultiAZCapable,StorageType]' --output text",
     'the latest PostgreSQL versions and that db.t4g.micro supports Multi-AZ with gp-class storage.'),
    (['[[Azure Database for PostgreSQL flexible servers]] → [[Create]] → look at versions, compute tiers (Burstable, General Purpose, Memory Optimized) and zone-redundant HA — then cancel.'],
     'az postgres flexible-server list-skus --location centralindia --query "[0].supportedServerEditions[].{tier:name,skus:length(supportedServerSkus)}" -o table\naz postgres flexible-server list-skus --location centralindia --query "[0].supportedServerVersions[].name" -o tsv | tail -5',
     'tiers with SKU counts and the supported PostgreSQL versions in Central India.'),
    (['[[SQL]] → [[Create instance]] → [[PostgreSQL]] → look at versions, editions (Enterprise / Enterprise Plus) and multi-zone availability — then cancel.'],
     'gcloud sql tiers list --format="table(tier,RAM,DiskQuota)" | head -8\ngcloud sql instances create x --database-version=POSTGRES_99 --region=asia-south1 2>&1 | grep -oE "POSTGRES_[0-9]+" | grep -v _99 | sort -t_ -k2 -n -u | tail -5',
     'machine tiers with RAM, and (from the deliberate error message) the list of valid PostgreSQL versions. Nothing is created.')),
    'Same engine, three managed wrappers: compare versions, HA design and price — not the SQL.')

STEP3 = ('3 · Inspect serverless runtimes and limits', tri(
    (['[[Lambda]] → [[Dashboard]] shows account concurrency; [[Create function]] lists runtimes. Configuration shows timeout up to 15 minutes and memory up to 10,240 MB.'],
     "aws lambda get-account-settings --query 'AccountLimit.[ConcurrentExecutions,CodeSizeZipped,TotalCodeSize]' --output text",
     'your concurrent-execution limit (new accounts can be lower than the default 1,000) and code-size limits.'),
    (['[[Function App]] → [[Create]] → compare hosting options (Flex Consumption, Premium, App Service) and their limits in the info boxes.'],
     'az functionapp list-runtimes --os linux --query "[].{runtime:runtime,version:version}" -o table | head -12',
     'supported Linux runtimes and versions for Azure Functions.'),
    (['[[Cloud Run]] → [[Write a function]] → runtime list; [[Container, Networking, Security]] → request timeout up to 3600 s.'],
     'gcloud functions runtimes list --region=asia-south1 --format="table(name,stage)" | head -12',
     'available runtimes (python312, nodejs22 …) and their stage.')),
    'Before porting a function, compare limits first — they decide whether code moves unchanged.')

prac = practical(OWN_INTRO + ' Side-by-side tests: storage speed, managed PostgreSQL options and serverless limits. Only the storage benchmark creates resources (a few paise).', [SETUP_STEP, STEP1, STEP2, STEP3],
    cleanup='<b>AWS:</b> <code>aws s3 rb s3://$B --force</code>. <b>Azure:</b> <code>az group delete -n rg-cmp --yes --no-wait</code>. <b>Google Cloud:</b> <code>gcloud storage rm -r gs://$B</code>. Delete <code>bench-50mb.bin</code> from each Cloud Shell.')

mist = mistakes([
    ['Assuming same name = same behaviour.', 'Translation tables hide details.', 'Read limits, defaults and SLAs.'],
    ['Porting functions without checking time limits.', 'Lambda habits.', 'Compare max duration, memory, payload.'],
    ['Comparing warehouse list prices only.', 'Different units.', 'Model a real query workload.'],
    ['Benchmarks from different locations.', 'Convenience.', 'Same client location for every test.'],
    ['Ignoring Azure’s storage-account level.', 'S3 mental model.', 'Plan account → container → blob.'],
    ['Expecting NoSQL to be portable.', '“It’s just JSON.”', 'Treat NoSQL choice as long-term.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Comparing cloud web services across providers.'], ['AWS CLF-C02', 'Choosing AWS compute, storage, database services for use cases.'], ['AZ-900', 'Azure compute, storage, database services and their use cases.'], ['Google Cloud Digital Leader', 'Google Cloud compute, storage, database and data services.']], minw=560) + \
    qx('1. AWS NoSQL key-value database?', ['DynamoDB', 'Redshift', 'Aurora', 'ElastiCache only'], 0, 'DynamoDB.') + \
    qx('2. Azure globally distributed multi-model database?', ['Cosmos DB', 'Azure SQL', 'Blob Storage', 'Synapse'], 0, 'Cosmos DB.') + \
    qx('3. Google Cloud managed Kubernetes?', ['GKE', 'EKS', 'AKS', 'Cloud Run only'], 0, 'GKE.') + \
    qx('4. Maximum AWS Lambda run time?', ['5 min', '15 min', '60 min', 'unlimited'], 1, '15 minutes.') + \
    qx('5. Azure equivalent of Amazon RDS for PostgreSQL?', ['Azure Database for PostgreSQL flexible server', 'Cosmos DB', 'Azure Files', 'Azure Cache'], 0, 'Flexible server.') + \
    qx('6. Google’s globally consistent relational database?', ['Spanner', 'Bigtable', 'Firestore', 'Memorystore'], 0, 'Spanner.')

proj = miniproject('Mini project: TiffinGo three-cloud translation sheet',
    'Build the sheet the team will use when hiring and planning.',
    ['<b>Map</b> every TiffinGo component to AWS, Azure and Google services (use the translation table).',
     '<b>Limits:</b> for functions, objects and NoSQL, record one limit that could break the design.',
     '<b>Pricing units:</b> note how each service is billed and estimate one month.',
     '<b>Benchmark:</b> run step 1 and record results with client location.',
     '<b>Portability:</b> rank components on the portability ladder.',
     '<b>Advice:</b> which two components would be hardest to move — and why.'],
    'A translation sheet with limits, pricing units, benchmark and portability notes.', '6.x + 10.1 + 10.2.')

assemble_v2(HERE, story_h2='Learn it once, use it three times', hook_html=hk,
    narration='Kabir had spent a year learning AWS. A new consulting client ran on Azure and a friend’s start-up on Google Cloud. He worried he would have to start from zero.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Comparing cloud web services',
    formal='<b>Comparing cloud web services</b> means mapping equivalent services across providers — compute, containers, functions, storage, databases, analytics, messaging and AI — and evaluating their real differences in limits and quotas, defaults, performance, availability SLAs, Regional availability, pricing units and APIs, so that designs and skills can be transferred and the best service chosen for each need.',
    simple='Most cloud services exist on every major cloud with different names; compare their limits, prices and defaults to choose well.',
    interview=['“S3, Blob Storage and Cloud Storage are equivalent object stores; Lambda, Azure Functions and Cloud Run functions are FaaS; DynamoDB, Cosmos DB and Firestore are NoSQL — but limits, consistency options and pricing units differ.”', '“I compare services by limits, pricing unit, defaults, SLA and Region availability, then run a small test.”'],
    terms_rows=[('Equivalent service', 'Same purpose, different provider.'), ('Limit / quota', 'Maximum size, rate or duration.'), ('Pricing unit', 'What is billed.'), ('Default', 'Out-of-the-box setting.'), ('Portability', 'Ease of moving.'), ('RU/s', 'Cosmos DB throughput unit.'), ('Slot', 'BigQuery compute unit.'), ('Storage account', 'Azure storage top level.')],
    exam='Exams ask “which service fits this use case” within one cloud; knowing equivalents helps with multi-cloud interview questions.',
    picture_h2='One app, three clouds, one translation table', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven service families compared, one by one', TYPES)],
    how_h2='The same order, three clouds', how_intro='Each step shows the equivalent services and the difference that matters.', how_anim=REQ,
    parts_h2='Six things to compare for any service', parts_html=parts, lv='',
    myth_rows=[('Equivalent services behave identically.', 'Limits, defaults and pricing differ.', 'Types.'), ('NoSQL is easy to move.', 'APIs and models differ.', 'Type 6.'), ('Cheapest list price wins.', 'Pricing units and usage decide.', 'Type 7.')],
    extra_secs=[('deep', 'Deep dive', 'Portability ladder, 15-minute comparison, name changes', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Map equivalent services across AWS, Azure and Google Cloud.', 'Explain key differences in limits, defaults and pricing for seven families.', 'Benchmark storage and compare managed databases and serverless limits on your own accounts.', 'Rank services by portability.', 'Build a translation sheet for a real app.'],
    next_html='<a href="../03-organisational-scenarios-which-cloud-model-fits/">10.3 Organisational scenarios: which cloud model fits</a>.',
    pre='<b>Before you start:</b> 10.1 and Module 6.')
