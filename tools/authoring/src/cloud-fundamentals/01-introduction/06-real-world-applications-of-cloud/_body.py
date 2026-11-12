import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
C = 'l16_apps.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('Who actually uses the cloud, and for what? Only tech companies?',
    'Everyone: streaming, payments, hospitals, farms, weather offices, schools, governments. Even science data lives there: the <b>Registry of Open Data on AWS</b> lists <b>1,474 public datasets</b> — <b>527</b> tagged life sciences, <b>310</b> satellite imagery, <b>197</b> weather, <b>154</b> agriculture. Anyone can analyse Sentinel-2 or Landsat satellite images without downloading petabytes.',
    ['Eight industries mapped to the same cloud building blocks.', 'Two real workloads step by step: live cricket streaming and satellite crop advice.', 'What India’s national-scale digital platforms teach about cloud design.'])
cmap = concept_map('Concept map. Beginner: apps you use daily. Intermediate: application areas and patterns. Advanced: big data and AI pipelines on cloud.',
    [[('wc', 'What is cloud', 'Lesson 1.1', B + '01-introduction/01-what-is-cloud-computing/'), ('sm', 'Service models', 'Module 2', B + '02-service-models/01-iaas-infrastructure-as-a-service/')],
     [('web', 'Web + mobile', 'apps', None), ('data', 'Big data', 'analytics', None), ('ai', 'AI / ML', 'GPUs', None), ('bk', 'Backup + DR', 'storage', None)],
     [('iot', 'IoT', 'devices', None), ('gov', 'e-Gov', 'India', None), ('sci', 'Science', 'open data', None), ('bp', 'Building blocks', 'Module 6', B + '06-cloud-building-blocks/04-cloud-products-and-solutions-map/')]],
    [('wc', 'web'), ('sm', 'web'), ('web', 'data'), ('data', 'ai'), ('web', 'bk'), ('data', 'iot'), ('web', 'gov'), ('data', 'sci'), ('ai', 'bp')],
    {'web', 'data', 'ai', 'bk', 'iot', 'gov', 'sci'},
    '<b>Module 1 done!</b> <b>Next:</b> <a href="../../02-service-models/01-iaas-infrastructure-as-a-service/">Module 2 · Service models</a>. <b>Related:</b> <a href="../../../spark-pyspark/">PySpark</a>, <a href="../../../kafka/">Kafka</a>.')
whw = why_how_where(
    'Knowing real applications helps you answer “where is cloud used?” and pick project ideas for placements and capstones.',
    'Each application maps to a few cloud building blocks: compute (VMs, containers, functions), storage (object, block), databases, queues/streams, analytics and AI services, CDN.',
    'Entertainment, finance, healthcare, education, government, retail, logistics, agriculture, science, gaming, telecom.',
    'Examples describe common practice; companies rarely publish full architectures, so we name patterns, not secret details.')
def apps(hl=-1):
    items = [('Streaming', 'blue'), ('Payments', 'green'), ('Health', 'violet'), ('Education', 'amber'), ('e-Gov', 'acc'), ('Retail', 'blue'), ('Agri', 'green'), ('Science', 'violet'), ('Gaming', 'amber'), ('AI', 'acc')]
    o = t(180, 14, 'One cloud, many industries', 8.4, 'ink', bold=True)
    for i, (a, tn) in enumerate(items):
        x = 16 + (i % 5) * 68; y = 26 + (i // 5) * 52
        o += box(x, y, 60, 40, 'amber' if i == hl else tn, rx=8) + t(x + 30, y + 24, a, 8, 'ink', bold=True)
    return o + t(180, 140, 'same building blocks: compute · storage · data · AI · network', 7.6, 'ink2')
scene_svg = scene('Ten industry tiles that run on the cloud: streaming, payments, health, education, e-government, retail, agriculture, science, gaming, AI.', apps(),
                  'Different industries, <tspan font-weight="700" class="s-acc">same cloud building blocks</tspan>.')
dialogue = '''R> Sir, for my capstone I want a “cloud project”, but what do real companies use cloud for?
A> Look around: the video you streamed, the UPI payment, your vaccine certificate, the weather forecast. And scientists share whole satellite archives on the cloud.
K> Can we see that data?
A> Yes — AWS publishes a registry of open datasets. Let’s count what is there and map each industry to cloud building blocks.'''
lv = '''
LEVELS> Cloud applications at three levels
L1> Apps you already use
      <ul>
        <li>Video and music streaming, online classes, food delivery, cab booking, UPI and banking apps, email, maps, photo backup, online games.</li>
      </ul>
L2> Ten application areas
      <ul>
        <li><b>Web & mobile apps</b> · <b>storage, backup & DR</b> · <b>big data analytics</b> · <b>AI/ML and GenAI</b> · <b>IoT</b> (sensors, smart meters) · <b>media streaming & CDN</b> · <b>e-commerce</b> · <b>healthcare</b> · <b>education</b> (LMS, virtual labs) · <b>e-governance</b>.</li>
        <li>Also: dev/test environments, high-performance computing (simulations), gaming servers, virtual desktops.</li>
      </ul>
L3> Patterns behind them
      <ul>
        <li>Web app = load balancer + auto-scaled compute + managed DB + CDN. Data lake = object storage + Spark/SQL engines (our PySpark and Hive courses). Streaming = Kafka/Kinesis + stream processing. AI = GPUs + managed ML platforms + model APIs.</li>
        <li>Open data on cloud: analyse where the data lives instead of downloading it (“bring compute to data”, same idea as Hadoop).</li>
      </ul>
/LEVELS
'''
mm = mindmap('Mind map of real-world cloud applications grouped by area.', 'Cloud in real life', [
    ('Consumer', 'blue', ['streaming', 'social media', 'gaming']),
    ('Business', 'green', ['e-commerce', 'CRM / ERP SaaS', 'email, office']),
    ('Data + AI', 'violet', ['data lakes', 'ML training', 'GenAI apps']),
    ('Public sector', 'acc', ['e-governance', 'health records', 'education']),
    ('Physical world', 'amber', ['IoT sensors', 'agriculture', 'smart cities']),
    ('Science', 'card', ['genomics', 'satellites', 'climate'])], h=290)
lay = layers('A typical cloud application stack: users and CDN at the top, then app compute, data stores, analytics and AI, all on provider infrastructure.', [
    ('Users + CDN', 'phones, browsers, edge cache', 'blue'), ('App layer', 'VMs, containers, functions', 'green'),
    ('Data stores', 'object storage, databases', 'violet'), ('Analytics', 'Spark, SQL engines, dashboards', 'acc'),
    ('AI / ML', 'training, model APIs', 'amber'), ('Cloud infrastructure', 'regions, AZs, network', 'card')], hl=2, caption='Most applications use 3–5 of these layers.')
DIS = figure('Dissection of a registry entry: dataset sentinel-2, tags satellite imagery and earth observation, stored in S3, free to access.',
    t(16, 22, 'One open dataset on AWS (real)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('sentinel-2', 'blue', 1), ('satellite imagery', 'green', 2), ('S3 bucket', 'amber', 3), ('free to read', 'violet', 4)]) +
    legend(16, 84, [(1, 'Dataset', 'ESA Sentinel-2 images'), (2, 'Tags', 'how the registry groups it'), (3, 'Where', 'object storage'), (4, 'Access', 'analyse in place')], size=8, gap=15, w=90),
    h=156, caption='Bring the computation to the data, not the data to you.')
extra = '\n\n  <h3>The stack behind a cloud application</h3>\n' + lay + '\n\n  <h3>Dissect an open dataset</h3>\n' + DIS
types_html = table(['Area', 'Example (India-flavoured)', 'Cloud pattern', 'Service model'], [
    ['Web & mobile', 'food delivery, cab apps', 'LB + auto scaling + DB + CDN', 'IaaS/PaaS'],
    ['Payments', 'UPI apps on sale days', 'elastic compute, queues, multi-AZ', 'IaaS/PaaS'],
    ['Streaming', 'cricket live streams', 'CDN + video encoding', 'PaaS'],
    ['Education', 'LMS, online exams, virtual labs', 'SaaS + VMs per student', 'SaaS/IaaS'],
    ['Healthcare', 'tele-consultation, health records', 'encrypted storage, Indian regions', 'PaaS/SaaS'],
    ['e-Governance', 'digital certificates, citizen portals', 'government community cloud (MeghRaj)', 'IaaS/PaaS'],
    ['Agriculture', 'crop monitoring from satellites', 'open data + analytics', 'PaaS'],
    ['Big data & AI', 'fraud detection, recommendations', 'data lake + Spark + ML', 'PaaS'],
    ['Backup & DR', 'office file backup', 'object storage + lifecycle', 'IaaS/SaaS'],
    ['IoT', 'smart electricity meters', 'IoT hub + streams + DB', 'PaaS']], minw=640)
warn = 'In interviews do not claim a specific company “runs entirely on AWS/Azure” unless it is published. Say “apps like X typically use…” and describe the pattern.'
steps = [
    ('Step 1 · Count the open datasets', code('python', 'l16_apps.py', 'h = urlopen("https://registry.opendata.aws/").read()\nnames = re.findall(r\'<h3><a href="/([^/"]+)/">\', h)', sec('== 1)', '== 2)')), 'Public, free-to-access data stored on cloud object storage.'),
    ('Step 2 · Top topics', code('python', 'l16_apps.py', 'Counter(tags).most_common(15)', sec('== 2)', '== 3)')), 'Life sciences, satellites, health, climate, agriculture, ML: cloud is everywhere in science.'),
    ('Step 3 · Famous datasets', code('python', 'l16_apps.py', 'names containing sentinel / landsat / noaa / covid', sec('== 3)')), 'Satellite images, weather radar, COVID research: analysed in place with Spark or Athena.'),
]
see = [term([('1474 datasets', G), ('8714 tag uses', W)], size=7.0), term([('life sciences 527', W), ('satellite 310', W)], size=7.0), term([('sentinel-2', G), ('usgs-landsat', G)], size=7.0),
       term([('weather 197', W), ('agriculture 154', W)], size=7.0), term([('ML 161', G)], size=7.0)]
B1 = [apps(i) for i in (7, 7, 6, 3, 9)]
B1 = [b + cap(c, '', tn, y=146, h=20) for b, c, tn in zip(B1, ['Science data', 'Topics', 'Farms from space', 'Weather', 'AI'], ['violet', 'violet', 'green', 'amber', 'acc'])]
two = anim_two('Cloud applications', 'Open data on the cloud', 'Real outputs (registry.opendata.aws)', 'Industries', see, B1, ['Count.', 'Topics.', 'Famous.', 'Weather.', 'ML.'], ['Science.', 'Topics.', 'Agri.', 'Climate.', 'AI.'])
pe = peel('A UPI-style payment on sale day, layer by layer', 'Common pattern for payment apps. (Simplified.)',
    [('Tap Pay', ''), ('Edge', ''), ('App', ''), ('Queue', ''), ('Bank switch', ''), ('Analytics', '')],
    [['Tap Pay', 'mobile app', '', ''], ['Edge', 'CDN + WAF', 'blocks attacks', ''], ['App', 'auto-scaled', 'containers', 'elastic'],
     ['Queue', 'smooths spikes', 'no lost requests', ''], ['Bank switch', 'secure link', 'to bank/NPCI', 'hybrid'], ['Analytics', 'stream to fraud model', '', 'AI']],
    ['Tap.', 'Protect.', 'Scale.', 'Buffer.', 'Settle.', 'Watch.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Cricket final stream', 'Millions watch at once. (Typical.)', ('CDN + elasticity', 'Edge caches video'), [
    ('Match starts', 'viewers ×50', 'Spike.', 'red'), ('Video encoded in cloud', 'many bitrates', 'Prepare.', 'blue'),
    ('CDN edges serve', 'near users', 'Deliver.', 'green'), ('Origin auto-scales', '', 'Scale.', 'green'), ('After match: shrink', '', 'Save.', 'amber')], ['Spike.', 'Encode.', 'Edge.', 'Scale.', 'Shrink.'], 'scenario-stream') + \
       five('Real-time scenario 2', 'Farm advisory from satellites', 'Crop health for a district. (Typical.)', ('Open data + Spark', 'Analyse in place'), [
    ('Need crop health', '', 'Question.', 'blue'), ('Sentinel-2 on S3', 'open data', 'Data.', 'green'),
    ('Spark on cloud', 'compute NDVI', 'Analyse.', 'violet'), ('Map per village', '', 'Result.', 'green'), ('SMS advice to farmers', '', 'Act.', 'amber')], ['Ask.', 'Data.', 'Spark.', 'Map.', 'SMS.'], 'scenario-agri') + \
       five('Real-time scenario 3 · advanced', 'Hospital AI', 'X-ray triage. (Typical.)', ('AI + compliance', 'Indian region, encrypted'), [
    ('X-rays uploaded', 'encrypted', 'Ingest.', 'blue'), ('Stored in India region', '', 'Comply.', 'violet'),
    ('Model flags urgent cases', 'GPU inference', 'AI.', 'green'), ('Doctor reviews', '', 'Human.', 'amber'), ('Audit log', '', 'Prove.', 'blue')], ['Upload.', 'Store.', 'Flag.', 'Review.', 'Audit.'], 'scenario-health')
clouds = vendor_tabs(
    '<p><b>AWS:</b> Registry of Open Data (used here), case studies at aws.amazon.com/solutions/case-studies, building blocks: EC2, S3, RDS, Kinesis, EMR, SageMaker, Bedrock, CloudFront.</p>',
    '<p><b>Azure:</b> Azure Open Datasets, Planetary Computer (earth data), strong in enterprise apps with Microsoft 365, Dynamics, Power BI; building blocks: VMs, Blob, SQL, Event Hubs, Synapse, Azure AI.</p>',
    '<p><b>Google Cloud:</b> BigQuery public datasets, Earth Engine (satellite analysis), Vertex AI; strong in analytics and AI; building blocks: Compute Engine, Cloud Storage, Pub/Sub, Dataflow, BigQuery.</p>') + \
    cloud3([['Public datasets', 'Registry of Open Data', 'Azure Open Datasets', 'BigQuery public datasets'], ['Earth / satellite', 'Sentinel, Landsat on S3', 'Planetary Computer', 'Earth Engine'], ['Streaming data', 'Kinesis / MSK', 'Event Hubs', 'Pub/Sub'], ['ML platform', 'SageMaker / Bedrock', 'Azure AI Foundry / ML', 'Vertex AI']])
prac = practical('Explore real cloud datasets and list a public bucket without an account.', [
    ('1 · Browse the registry', '<p>Open <code>registry.opendata.aws</code>, search “sentinel-2” and “india”.</p>', 'Each page shows the S3 location and licence.'),
    ('2 · Install the AWS CLI', code('bash', 'terminal', 'pip install awscli     # or the official installer\naws --version'), 'Free; no account needed for public data with --no-sign-request.'),
    ('3 · List a public bucket', code('bash', 'terminal', 'aws s3 ls --no-sign-request s3://noaa-ghcn-pds/ --region us-east-1 | head'), 'You are reading cloud object storage directly.'),
    ('4 · Download one small file', code('bash', 'terminal', 'aws s3 ls --no-sign-request s3://noaa-ghcn-pds/csv/by_year/ | tail -3\naws s3 cp --no-sign-request s3://noaa-ghcn-pds/csv/by_year/1763.csv .'), 'Weather records from 1763: a few KB.'),
    ('5 · Run the lesson script', code('bash', 'terminal', 'python3 l16_apps.py'), 'Same as Steps 1–3.')],
    cleanup='Delete downloaded files. Public open-data reads are free for you; the data owner/AWS pays. Never use --no-sign-request on private data.')
mist = mistakes([
    ['Downloading huge datasets to a laptop.', 'Habit from small files.', 'Analyse in the cloud next to the data (Athena, Spark, BigQuery).'],
    ['Claiming a company’s exact cloud setup.', 'Guessing from news.', 'Describe patterns; cite published case studies only.'],
    ['Picking a capstone with no real data.', 'Toy CSVs.', 'Use open datasets (weather, satellite, transport) for real scale.'],
    ['Ignoring licences of open data.', '“Public” ≠ any use.', 'Read the licence on the registry page.'],
    ['Thinking cloud = only IT companies.', 'Visible apps are tech.', 'Health, farming, government and science are big users.']])
cert = certbox([
    ['AWS CLF-C02', 'Domain 3 · Cloud Technology & Services (34%)', 'Match use cases to services: web (EC2, ELB), storage (S3), analytics (Athena, EMR), ML (SageMaker), CDN (CloudFront).'],
    ['Azure AZ-900', 'Describe Azure architecture and services', 'Typical workloads and matching services.'],
    ['Google Cloud Digital Leader', 'Data transformation; AI', 'Value of data and AI in industries; public datasets, BigQuery, Vertex AI.'],
    ['C-DAC PGCP-BDA', 'Sessions 5–6, 8–9 lab', 'Cloud products and solutions; exposure to big data technologies on cloud.']],
    [('A company wants to analyse petabytes of satellite images without buying storage. Best approach?', 'Use the open dataset in cloud object storage and analyse in place with a managed query/Spark service.'),
     ('Which service delivers video to millions with low latency? (a) S3 Glacier (b) CloudFront (c) IAM', '<b>(b) CloudFront</b>, a CDN.')])
proj = miniproject('Module 1 project: “Cloud in India” fact sheet (combines 1.1–1.6)',
    'One script that builds a dated HTML fact sheet: regions in India (1.1), AWS service growth (1.2), real prices (1.3), recent incidents (1.4), TCO line (1.5) and top open-data topics (1.6).',
    ['Make a folder <code>cloud-factsheet</code> and copy the six lesson scripts into it.', 'Change each script’s <code>print</code> into a function that returns its lines.', 'Write <code>build.py</code> that calls them and writes <code>factsheet.html</code> with one section each.', 'Run weekly with <code>cron</code>; commit each version to GitHub.', 'Later (AWS course): host it as an S3 static website and send the link.'],
    'A one-page HTML fact sheet you can share with classmates, updated weekly with real data.', 'Everything from Module 1 + Python, HTML, cron, Git, later S3.')

# ===== v3 =====
def matrix():
    blocks = [('server', 'Compute'), ('disk', 'Storage'), ('db', 'Database'), ('lb', 'Streaming'), ('chart', 'Analytics'), ('chip', 'AI / ML'), ('globe', 'CDN')]
    inds = [('Food delivery app', [1, 0, 1, 1, 1, 1, 1]), ('UPI payments', [1, 0, 1, 1, 1, 1, 0]), ('Cricket live stream', [1, 1, 0, 1, 0, 0, 1]),
            ('Online exams / LMS', [1, 1, 1, 0, 1, 0, 1]), ('Hospital records + AI', [1, 1, 1, 0, 1, 1, 0]), ('e-Governance portal', [1, 1, 1, 0, 1, 0, 1]),
            ('Satellite crop advice', [1, 1, 0, 0, 1, 1, 0]), ('Smart electricity meters', [1, 1, 1, 1, 1, 0, 0])]
    o = t(320, 16, 'Same building blocks, different industries', 11, 'ink', bold=True)
    for j, (icn, n) in enumerate(blocks):
        x = 230 + j * 56
        o += ic(icn, x + 12, 26, 0.9, 'acc') + t(x + 22, 60, n, 7.8, 'ink', bold=True)
    for i, (n, row) in enumerate(inds):
        y = 70 + i * 25
        o += box(14, y, 206, 21, 'card', rx=4) + t(22, y + 14, n, 8.2, 'ink', anchor='start', bold=True)
        for j, v in enumerate(row):
            x = 230 + j * 56
            o += box(x + 4, y, 36, 21, 'green' if v else 'card', rx=4) + (t(x + 22, y + 15, '●', 9, 'green') if v else '')
    return o + t(320, 286, 'Learn the blocks once (Module 6), and you can design for any industry.', 8.4, 'ink2')
MAT = bigfig('Matrix of eight industries against seven cloud building blocks (compute, storage, database, streaming, analytics, AI/ML, CDN), with dots showing which blocks each industry uses.', matrix(), h=296)
picture = ('  <p>Every industry uses the cloud, but under the hood they all assemble the <b>same few building blocks</b>. The table below is the key idea of this lesson: read across a row to see what an app needs.</p>\n' + MAT)

# animation 1: cricket live stream
SN = {'cam': (6, 56, 54, 50, 'chip', 'Stadium', 'camera feed'), 'enc': (72, 56, 60, 50, 'gear', 'Encoder', '4 qualities'),
      'org': (144, 56, 60, 50, 'disk', 'Origin', 'video pieces'), 'e1': (226, 6, 56, 46, 'globe', 'Edge', 'Mumbai'),
      'e2': (226, 58, 56, 46, 'globe', 'Edge', 'Delhi'), 'e3': (226, 110, 56, 46, 'globe', 'Edge', 'Chennai'), 'view': (294, 56, 60, 50, 'phone', 'Viewers', 'millions')}
SS = [dict(on=['cam', 'enc'], hot='cam', move=(60, 81, 72, 81, ''), head='Step 1 · The camera sends one live feed', text='The stadium sends one high-quality video stream into the cloud.', text2='Only one upload, no matter how many people watch.', svc='AWS Elemental MediaLive · partner encoders on Azure (Azure Media Services retired 2024) · Google Live Stream API'),
      dict(on=['cam', 'enc', 'org'], hot='enc', move=(132, 81, 144, 81, '4×'), head='Step 2 · Encode into many qualities', text='The encoder makes 4 versions (1080p down to 240p) and cuts', text2='them into 2–6 second pieces, so slow phones still play.', svc='Adaptive bitrate streaming (HLS / DASH)'),
      dict(on=['cam', 'enc', 'org', 'e1', 'e2', 'e3'], hot='org', move=(204, 81, 228, 30, 'copy'), head='Step 3 · Pieces go to the origin, then edges', text='The origin stores the pieces; CDN edge locations in many cities', text2='copy them close to viewers.', svc='AWS S3 + CloudFront · Azure Front Door/CDN · Google Cloud CDN'),
      dict(on=list(SN), hot='view', move=(282, 83, 296, 83, 'video'), head='Step 4 · Each viewer gets video from a nearby city', text='A viewer in Chennai downloads from the Chennai edge, not the stadium.', text2='Fast start, little buffering, origin stays calm.', svc='Broad network access + CDN'),
      dict(on=list(SN), hot='e2', move=(282, 30, 296, 70, '×50'), head='Step 5 · Final over: viewers ×50', text='Edges absorb the spike; the origin and encoder scale out automatically.', text2='After the match everything scales back in and the bill drops.', svc='Elasticity + measured service on a real event')]
STREAM = flow_anim('A cricket final, streamed live', 'One of the biggest cloud workloads in India: millions of viewers in one evening.', 'Live streaming', 'Animation: stadium camera, encoder, origin, CDN edges in Mumbai, Delhi and Chennai, millions of viewers, spike in the final over.', SN, SS, hid='stream')

# animation 2: satellite crop advice with open data
FN = {'sat': (6, 20, 60, 50, 'globe', 'Sentinel-2', 'satellite'), 's3': (6, 96, 60, 50, 'disk', 'Open data', 'S3 bucket'),
      'spark': (96, 56, 66, 50, 'chip', 'Spark job', 'NDVI per field'), 'tbl': (190, 20, 66, 50, 'db', 'Results', 'per village'),
      'map': (190, 96, 66, 50, 'chart', 'Map', 'crop health'), 'sms': (284, 56, 70, 50, 'phone', 'SMS advice', 'farmers')}
FS = [dict(on=['sat', 's3'], hot='sat', move=(36, 70, 36, 96, 'images'), head='Step 1 · The satellite photographs every field', text='ESA’s Sentinel-2 images India every few days. The images are', text2='published free as open data in cloud storage (Lesson real proof).', svc='Registry of Open Data on AWS · Microsoft Planetary Computer · Google Earth Engine'),
      dict(on=['sat', 's3', 'spark'], hot='spark', move=(66, 121, 98, 81, 'read'), head='Step 2 · Compute next to the data', text='A Spark cluster in the same region reads only the district’s tiles', text2='and computes NDVI (a greenness score) for every field.', svc='AWS EMR · Azure HDInsight/Databricks · Google Dataproc (PySpark course)'),
      dict(on=['sat', 's3', 'spark', 'tbl'], hot='tbl', move=(162, 70, 192, 45, 'save'), head='Step 3 · Store results per village', text='Small results table: village, field, NDVI, change since last week.', text2='Megabytes, not the terabytes of raw images.', svc='Object storage + query engine (Athena / BigQuery)'),
      dict(on=['sat', 's3', 'spark', 'tbl', 'map'], hot='map', move=(223, 70, 223, 96, ''), head='Step 4 · Draw a crop-health map', text='Officers see red patches where crops are stressed.', text2='', svc='Dashboards: QuickSight · Power BI · Looker'),
      dict(on=list(FN), hot='sms', move=(256, 121, 286, 81, 'alert'), head='Step 5 · Advice reaches farmers', text='Farmers in red zones get an SMS in their language: check irrigation.', text2='Whole pipeline costs a few dollars of compute per run.', svc='AWS SNS · Azure Communication Services · partner SMS gateways')]
FARM = flow_anim('Crop advice from space, step by step', 'Open data + cloud compute: a real pattern used by agri-tech teams.', 'Big data on cloud', 'Animation: Sentinel-2 satellite images in open cloud storage, Spark job computes NDVI, results, map, SMS to farmers.', FN, FS, hid='farm')

parts = '  <p>Ten areas where the cloud is used today, with the pattern behind each.</p>\n' + types_html + cards([
    ('Payments', 'Sale days multiply UPI-style traffic; elastic compute, queues and multi-AZ keep payments flowing.', 'elastic + reliable'),
    ('e-Governance', 'Citizen portals and digital certificates; the Government of India’s MeghRaj (GI Cloud) initiative guides government cloud use.', 'community cloud'),
    ('Education', 'Online classes, exams and per-student lab VMs that are deleted after the semester.', 'pay per semester'),
    ('Science and open data', '1,474 datasets on AWS alone: genomes, satellites, weather, climate.', 'bring compute to data')]) + '\n  <h3>What India’s national digital platforms teach</h3>\n  <p>Platforms such as <b>UPI</b> (payments), <b>DigiLocker</b> (documents), <b>CoWIN</b> (vaccination) and <b>IRCTC</b> (train tickets) serve crores of people, often in sudden spikes: a Tatkal booking window, a vaccination slot release, a festival sale. We do not claim which provider each one uses, but every one of them needs the same cloud ideas you learned in this module:</p>\n' + table(['Spike moment', 'Cloud idea that handles it', 'Lesson'], [
        ['Tatkal window opens at 10 am', 'elasticity + queues so requests wait instead of failing', '1.1, 1.3'],
        ['Vaccination slots released', 'auto scaling, caching, CDN for static pages', '1.3, 1.6'],
        ['Sale-day payments', 'multiple zones, managed databases, monitoring', '1.4'],
        ['Citizen documents', 'encrypted storage, Indian regions, audit logs (DPDP)', '1.4'],
        ['Government departments', 'MeghRaj: empanelled cloud services for government', '1.6']], minw=600)

SUMMARY = big_mindmap('Mind map of lesson 1.6: industries, building blocks, streaming pattern, open data pattern, India examples, cautions.', 'Cloud in real life', [
    ('Industries', 'blue', 'app', ['payments, streaming', 'health, education', 'e-gov, agriculture']),
    ('Building blocks', 'green', 'server', ['compute, storage, DB', 'streaming, analytics', 'AI, CDN']),
    ('Streaming', 'violet', 'globe', ['encode once', 'CDN edges', 'scale for the final over']),
    ('Open data', 'acc', 'disk', ['1,474 datasets', 'Sentinel-2, NOAA', 'compute next to data']),
    ('India', 'amber', 'user', ['UPI-scale apps', 'MeghRaj', 'Indian regions']),
    ('Careful', 'red', 'shield', ['read licences', 'don’t claim secrets', 'patterns, not guesses'])], h=380, caption='Lesson 1.6 on one page.')
cert = cert + '\n  <h3>Lesson 1.6 on one page</h3>\n' + SUMMARY

assemble_v2(HERE, story_h2='A capstone idea from the sky', hook_html=hk,
    narration='Riya must pick a capstone. She wants real data and a real cloud use case, not a toy CSV. Arjun Sir shows her how industries really use the cloud — and where the world keeps its open data.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Real-world applications of cloud computing',
    formal='<b>Cloud applications</b> are workloads delivered using cloud resources and services, including web and mobile applications, payments, media streaming, e-commerce, healthcare, education, e-governance, IoT, big data analytics, artificial intelligence and scientific computing, each composed from compute, storage, database, streaming, analytics, AI and content-delivery building blocks.',
    simple='Almost every app you use — and much of science and government — is built from the same few cloud building blocks put together differently.',
    interview=['“Cloud computing is used in payments, video streaming, e-commerce, healthcare, education, e-governance, IoT, big data analytics and AI.”', '“Each application combines a few building blocks: elastic compute, object storage, managed databases, streaming, analytics engines, AI services and a CDN.”', '“For example, a live cricket stream is encoded once in the cloud and served from CDN edges in each city, and satellite open data is analysed in place with Spark instead of being downloaded.”'],
    terms_rows=[('Workload', 'An application running on the cloud.'), ('CDN / edge', 'Copies of content in many cities.'), ('Encoder', 'Turns video into many qualities.'), ('Open data', 'Public datasets anyone can use.'), ('NDVI', 'Satellite greenness score for crops.'), ('Data lake', 'Raw data in object storage.'), ('IoT', 'Internet-connected devices.'), ('Bring compute to data', 'Analyse where data lives.')],
    exam='Exams give a use case and ask for the service: static website → S3 + CloudFront; analytics on S3 → Athena; big data → EMR; ML → SageMaker; IoT → IoT Core; video → Elemental MediaLive + CloudFront. Azure/GCP equivalents are in the Clouds section.',
    picture_h2='Industries × building blocks', picture_html=picture,
    how_h2='Two real workloads, step by step', how_intro='Two common patterns animated: live video for millions, and big-data analysis of satellite open data.', how_anim=STREAM + FARM,
    parts_h2='Ten application areas', parts_html=parts, lv='',
    myth_rows=[('Cloud is only for IT companies.', '527 life-science datasets in one registry.', 'Real proof step 2.'), ('You must download data to analyse it.', 'Compute next to the data.', 'Animation 2.'), ('Streaming needs one huge server.', 'CDN edges in many cities.', 'Animation 1.')],
    clouds_html=clouds, proof_h2='What the world keeps on the cloud', proof_intro='All outputs are real: the Registry of Open Data on AWS home page, read on 10 Nov 2026.', proof_steps=steps,
    practical_html=prac, mistakes_html=mist, cert_html='', project_html='', can_now=['Map any app to cloud building blocks (compute, storage, database, streaming, analytics, AI, CDN).', 'Explain step by step how a live stream reaches millions.', 'Explain “bring compute to data” with satellite open data.', 'Read a public open-data bucket with the AWS CLI.', 'Say which cloud ideas national-scale platforms need for spikes.'],
    next_html='<a href="../../02-service-models/01-iaas-infrastructure-as-a-service/">Module 2 · 2.1 IaaS: renting infrastructure</a>.',
    pre='<b>Before you start:</b> <a href="../05-on-premises-vs-cloud-vs-dedicated-servers/">1.5</a>.')
