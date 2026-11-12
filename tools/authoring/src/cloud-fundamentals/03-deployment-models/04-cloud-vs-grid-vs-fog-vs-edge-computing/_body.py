import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)


hk = hook('TiffinGo puts a temperature sensor in every delivery bag: hot food must stay above 60 °C. 2,000 bags send a reading every second. Should all 7 million readings a hour go to the cloud?',
    'No — that is what <b>edge</b> and <b>fog</b> computing are for: filter and act <b>close to the device</b>, send only what matters to the <b>cloud</b>. And before cloud there were <b>cluster</b>, <b>grid</b> and <b>utility</b> computing — each solved a different problem and each survives inside today’s cloud. This lesson explains all six with the same pattern, animates one reading travelling sensor → edge → fog → cloud, and on <b>your own</b> account you build a small edge-to-cloud pipeline that sends only the alerts.',
    ['Why grid computing (volunteers, scientists) is not the same as cloud.', 'Edge vs fog: the device, or the layer between device and cloud?', 'Google retired Cloud IoT Core in 2023 — what replaced it.'])

def story_scene():
    o = t(180, 12, 'Where should the thinking happen?', 9, 'ink', bold=True)
    for i, (a, b, tn) in enumerate([('Sensor', 'in the bag', 'green'), ('Edge', 'rider phone', 'amber'), ('Fog', 'kitchen gateway', 'violet'), ('Cloud', 'AWS Mumbai', 'blue')]):
        x = 8 + i * 88
        o += box(x, 34, 80, 56, tn, rx=8) + t(x + 40, 56, a, 8.2, 'ink', bold=True) + t(x + 40, 72, b, 7, 'ink2')
        if i < 3: o += arrow(x + 80, 62, x + 88, 62)
    o += t(180, 112, 'Millions of readings in, a few alerts out', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Four boxes in a row: sensor in the bag, edge (rider phone), fog (kitchen gateway), cloud (AWS Mumbai); millions of readings in, a few alerts out.', story_scene(), 'Process <tspan font-weight="700" class="s-acc">near the data</tspan>, store and learn in the cloud.', h=124)
dialogue = '''K> Sir, the vendor says each sensor can stream straight to the cloud.
A> And pay for 7 million messages an hour, plus the rider’s mobile data? And if the network drops in a tunnel, the alert is lost.
R> So the phone checks the temperature itself?
A> The phone — the edge — checks each reading. The kitchen gateway — the fog — collects all bags in its area and decides who to call. The cloud keeps history and learns which routes cool food.
K> And grid computing? It was in my syllabus.
A> Older idea, different problem. Let’s line them all up.'''

# ------------------------------------------------------------------ picture
def tierfig():
    o = t(320, 16, 'Four tiers: distance from the data vs power', 11, 'ink', bold=True)
    T = [('Devices / sensors', 'billions', 'micro-seconds', 'tiny', 'green'), ('Edge', 'millions', '< 10 ms', 'small', 'amber'), ('Fog', 'thousands', '10–50 ms', 'medium', 'violet'), ('Cloud', 'dozens of Regions', '50–200 ms+', 'huge', 'blue')]
    o += t(80, 44, 'Tier', 8, 'ink', bold=True) + t(260, 44, 'How many', 8, 'ink', bold=True) + t(390, 44, 'Latency to data', 8, 'ink', bold=True) + t(530, 44, 'Compute power', 8, 'ink', bold=True)
    for i, (a, b, c, d, tn) in enumerate(T):
        y = 52 + i * 34
        o += box(16, y, 130, 28, tn, rx=5) + t(81, y + 18, a, 7.8, 'ink', bold=True) + t(260, y + 18, b, 7.6, 'ink') + t(390, y + 18, c, 7.6, 'ink') + t(530, y + 18, d, 7.6, 'ink')
    o += arrow(612, 60, 612, 176) + t(600, 196, 'more power, farther away', 7, 'ink2', anchor='end')
    return o
TIER = bigfig('Table-like figure: devices (billions, microseconds, tiny power), edge (millions, under 10 ms, small), fog (thousands, 10–50 ms, medium), cloud (dozens of Regions, 50–200 ms, huge power).', tierfig(), h=206)

def histfig():
    o = t(320, 16, 'How we got here: one idea at a time', 11, 'ink', bold=True)
    H = [('1980s–90s', 'Cluster', 'many PCs, one room'), ('1990s–2000s', 'Grid', 'many sites, shared'), ('1960s idea, 2000s', 'Utility', 'pay per use'), ('2006 →', 'Cloud', 'on-demand services'), ('2012 →', 'Fog', 'layer near devices'), ('2015 →', 'Edge', 'at the device')]
    for i, (y, n, d) in enumerate(H):
        x = 14 + i * 104
        o += box(x, 40, 96, 74, ['blue', 'amber', 'card', 'green', 'violet', 'red'][i], rx=7) + t(x + 48, 58, y, 6.8, 'ink2') + t(x + 48, 78, n, 9, 'ink', bold=True) + t(x + 48, 98, d, 6.8, 'ink2')
        if i < 5: o += arrow(x + 96, 77, x + 104, 77)
    o += t(320, 136, 'Dates are approximate; each idea lives on inside the next (clusters inside cloud Regions, utility billing in cloud pricing).', 7.2, 'ink2')
    return o
HIST = bigfig('Timeline of six ideas: cluster (1980s–90s), grid (1990s–2000s), utility (pay-per-use idea), cloud (2006 on), fog (2012 on), edge (2015 on).', histfig(), h=146)

picture = ('  <p>The six terms are easier when you see them as answers to different questions. First, the four tiers between a device and the cloud:</p>\n' + TIER +
           '\n  <p>And the history — each idea built on the one before:</p>\n' + HIST +
           '\n  <h3>One table to remember</h3>\n' + table(['', 'Cluster', 'Grid', 'Utility', 'Cloud', 'Fog', 'Edge'], [
               ['Question it answers', 'one big computer from many?', 'share computers across organisations?', 'pay only for use?', 'on-demand IT services?', 'process between device and cloud?', 'process at the device?'],
               ['Ownership', 'one org', 'many orgs', 'provider', 'provider / org', 'org / telco', 'org / user'], ['Location', 'one data centre', 'many sites', 'provider', 'Regions', 'near devices (LAN, base stations)', 'on / next to the device'],
               ['Coupling', 'tight, fast network', 'loose, internet', '—', 'loose', 'medium', '—'], ['Example', 'Hadoop / HPC cluster', 'WLCG, BOINC', 'electricity-like billing', 'AWS, Azure, GCP', 'kitchen gateway', 'rider phone, camera']], minw=720))

# ------------------------------------------------------------------ how: one reading
RN = {'s': (4, 54, 50, 50, 'meter', 'Sensor', '58 °C'), 'e': (66, 54, 60, 50, 'phone', 'Edge', 'rider app'), 'f': (140, 4, 66, 46, 'server', 'Fog', 'kitchen gateway'),
      'q': (140, 104, 66, 46, 'disk', 'Local buffer', 'offline queue'), 'c': (220, 54, 64, 50, 'cloud', 'Cloud', 'ingest + store'), 'm': (296, 54, 60, 50, 'chart', 'Analytics', 'routes, ML')}
RS = [dict(on=['s', 'e'], hot='e', move=(54, 79, 70, 79, '58°C'), head='Step 1 · The sensor reports', text='The bag sensor sends a reading every second over Bluetooth to the rider’s phone.', text2='Sending 3,600 readings an hour to the cloud would be wasteful.', svc='Device tier: tiny compute, battery-powered'),
      dict(on=['s', 'e'], hot='e', move=None, head='Step 2 · The edge decides in milliseconds', text='The app checks the rule “below 60 °C for 30 s”. Normal readings are summarised', text2='(1 per minute); 58 °C for 30 s raises an alert immediately on the phone.', svc='Edge: AWS IoT Greengrass · Azure IoT Edge · on-device code'),
      dict(on=['e', 'q'], hot='q', move=(96, 104, 146, 126, 'store'), head='Step 3 · No network? Store and forward', text='In a tunnel the phone queues the alert locally and retries when the signal returns —', text2='nothing is lost.', svc='Offline-first design is the heart of edge computing'),
      dict(on=['e', 'f'], hot='f', move=(96, 54, 146, 30, 'alert'), head='Step 4 · The fog node coordinates the area', text='The kitchen gateway receives alerts from all riders nearby, sees two cold bags on', text2='one route, and dispatches a fresh meal from the closest kitchen.', svc='Fog: local servers, telco MEC, Local Zones, Outposts'),
      dict(on=['f', 'c'], hot='c', move=(206, 30, 230, 66, 'events'), head='Step 5 · The cloud ingests what matters', text='Only alerts and per-minute summaries reach the cloud (MQTT/HTTPS): 99% less', text2='traffic than raw readings.', svc='AWS IoT Core · Azure IoT Hub · Google Pub/Sub (IoT Core retired 2023)'),
      dict(on=['c', 'm'], hot='m', move=(284, 79, 300, 79, 'learn'), head='Step 6 · Cloud analytics improve the edge', text='History shows one route loses heat on hot afternoons; the cloud trains a model and', text2='pushes new thresholds back to the edge apps.', svc='Cloud = storage, analytics, ML, fleet updates')]
READ = flow_anim('One temperature reading: sensor → edge → fog → cloud', 'Watch where each decision is made.', 'Edge to cloud', 'Animation: sensor reports to rider phone; edge applies rule; offline buffering; kitchen fog node coordinates; cloud ingests alerts; analytics push new thresholds back.', RN, RS, hid='edgeflow')

# ------------------------------------------------------------------ types
def mapfig():
    o = t(320, 16, 'Six computing models, one by one', 11, 'ink', bold=True)
    items = [('1', 'Cluster computing', 'many machines, one system, one site', 'blue'), ('2', 'Grid computing', 'shared resources across organisations', 'amber'), ('3', 'Utility computing', 'pay-per-use metering model', 'card'),
             ('4', 'Cloud computing', 'on-demand services over the network', 'green'), ('5', 'Fog computing', 'layer between devices and cloud', 'violet'), ('6', 'Edge computing', 'processing at or next to the device', 'red')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 3) * 208; y = 32 + (i // 3) * 84
        o += box(x, y, 198, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 106, y + 34, a, 8.4, 'ink', bold=True) + t(x + 106, y + 54, b, 6.8, 'ink2')
    o += t(320, 210, '1–3 came first and live inside cloud today; 5–6 extend the cloud towards devices.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of six models: cluster, grid, utility, cloud, fog, edge computing.', mapfig(), h=222)

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

A1 = mk(['Many nodes', 'Fast network', 'Work as one'], ['nodes|same hardware|one room', 'network|low latency|InfiniBand/Ethernet', 'job|split + combine|scheduler'], ['blue', 'amber', 'green'],
        ['similar computers in one place', 'a fast local network links them tightly', 'a scheduler splits one job across all nodes'],
        [('Nodes', 'Similar machines in one data centre.', ''), ('Network', 'A fast, low-latency network links them.', ''), ('One job', 'A scheduler splits work and combines results.', '')],
        'Cluster computing in action', 'Many machines, one system.', 'Cluster', 'Animation: many nodes; fast network; work as one.', 'c1anim')
T1 = vt(1, 'Cluster computing', 'blue',
    '<b>Cluster computing</b> links a group of similar computers (nodes), usually in one location over a fast local network, so that they work together as a single system — for high performance (HPC), high availability (failover) or load balancing — under one administrative domain.',
    'A team of rowers in one boat: same boat, same rhythm, one direction.',
    'TiffinGo’s analytics team runs a 10-node Spark cluster (Amazon EMR / Dataproc) to process a year of orders in 20 minutes.',
    'Hadoop and Spark clusters (EMR, HDInsight, Dataproc), HPC clusters (Slurm, AWS ParallelCluster, Azure CycleCloud), Kubernetes clusters, database failover clusters.',
    'The Big Data track builds Hadoop and Spark clusters step by step.', A1,
    'a job can be split into parallel parts or a service needs failover within one site.',
    'nodes are spread across the internet with slow, unreliable links — that is grid territory.',
    'Many computers in one place connected tightly so they act like one powerful computer.',
    [('Install', 'Same OS/software on all nodes.'), ('Network', 'Fast interconnect.'), ('Scheduler', 'Slurm, YARN, Kubernetes.'), ('Split', 'Divide data/tasks.'), ('Combine', 'Gather results / fail over.')],
    [('node', 'one computer in a cluster'), ('HPC', 'high-performance computing'), ('scheduler', 'software that assigns work to nodes')],
    table(['', 'Cluster', 'Grid'], [['Location', 'one site', 'many sites'], ['Ownership', 'one org', 'many orgs'], ['Network', 'fast LAN', 'internet / WAN']], minw=420),
    ['Big Data (Hadoop/Spark)', 'Scientific HPC', 'High-availability databases'],
    'Every cloud Region is built from clusters: EC2 hosts, storage clusters and Kubernetes clusters are the cluster idea at enormous scale.',
    'Cluster placement groups (AWS), proximity placement groups (Azure) and compact placement (Google) exist to give cloud clusters the low-latency network HPC needs.')

A2 = mk(['Many organisations', 'Middleware joins them', 'Big shared job'], ['sites|universities, labs|own their PCs', 'middleware|authentication|job brokers', 'job|millions of tasks|run where free'], ['amber', 'blue', 'green'],
        ['independent organisations contribute computers', 'grid middleware handles identity, data and scheduling', 'huge workloads run on whatever resources are free'],
        [('Sites', 'Independent organisations contribute computers.', ''), ('Middleware', 'Grid software handles identity, data and job brokering.', ''), ('Job', 'Many tasks run wherever capacity is free.', '')],
        'Grid computing in action', 'Shared across organisations.', 'Grid', 'Animation: many organisations; middleware joins them; a big shared job runs.', 'c2anim')
T2 = vt(2, 'Grid computing', 'amber',
    '<b>Grid computing</b> coordinates loosely coupled, geographically distributed and often heterogeneous resources owned by different organisations, through grid middleware, so they can be shared to solve large problems — typically batch scientific workloads — as a “virtual organisation”.',
    'A national blood-donation network: hospitals in many cities share stock through a common system, each still owning its own bank.',
    'A university research project volunteers spare PCs from five colleges to simulate monsoon patterns overnight — the same idea TiffinGo could never use for real-time orders.',
    'Worldwide LHC Computing Grid (WLCG), Open Science Grid / OSG, BOINC volunteer computing (e.g. Einstein@Home), India’s GARUDA grid (C-DAC).',
    '', A2,
    'massive batch jobs can be split into independent tasks and organisations want to share idle capacity.',
    'you need interactive services, fast responses or a commercial SLA — use cloud.',
    'Computers owned by different organisations in different places shared together to run very large jobs.',
    [('Join', 'Sites install middleware.'), ('Identity', 'Certificates for users and sites.'), ('Submit', 'Jobs to a broker.'), ('Match', 'Broker finds free resources.'), ('Collect', 'Results returned and stored.')],
    [('middleware', 'software that connects different systems'), ('virtual organisation', 'a group sharing resources across institutions'), ('volunteer computing', 'public donating idle PC time')],
    table(['', 'Grid', 'Cloud'], [['Owners', 'many organisations', 'one provider'], ['Access', 'by membership', 'self-service, pay per use'], ['Workload', 'batch science', 'any, incl. interactive']], minw=420),
    ['Particle physics', 'Climate and genomics research', 'Volunteer science projects'],
    'CERN’s Worldwide LHC Computing Grid links computing centres in dozens of countries to process data from the Large Hadron Collider. India’s C-DAC built the GARUDA national grid for research institutions.',
    'Grid and cloud converged: many research grids now add cloud capacity for peaks, and cloud batch services borrowed grid ideas (job brokers, data locality).')

A3 = mk(['Measure use', 'Price per unit', 'Pay the bill'], ['meter|CPU-hours, GB|requests', 'tariff|price per unit|like electricity', 'bill|only what you used|monthly'], ['card', 'amber', 'green'],
        ['every resource is measured', 'each unit has a price', 'customers pay for consumption, not ownership'],
        [('Meter', 'Every resource use is measured.', ''), ('Tariff', 'Each unit has a published price.', ''), ('Bill', 'Customers pay only for what they used.', '')],
        'Utility computing in action', 'IT like electricity.', 'Utility', 'Animation: measure use; price per unit; pay the bill.', 'c3anim')
T3 = vt(3, 'Utility computing', 'card',
    '<b>Utility computing</b> is a service-provisioning model in which computing resources (processing, storage, network) are metered and charged by usage, like a public utility such as electricity or water, instead of being bought as fixed assets.',
    'Your electricity meter: you do not own the power station, you pay for the units you used this month.',
    'TiffinGo pays for Lambda by request and S3 by GB-month — the utility model inside the cloud (Lesson 5.5).',
    'The billing model of every cloud provider; earlier: IBM and Sun “pay per CPU-hour” offerings in the early 2000s.',
    'Pricing models are covered in Lesson 5.5.', A3,
    'usage varies and you prefer opex to capex.',
    'usage is constant and very high for years — owning or committing may be cheaper.',
    'Paying for computing the way you pay for electricity — only for what you use.',
    [('Meter', 'Collect usage records.'), ('Rate', 'Apply prices per unit.'), ('Aggregate', 'Per account / tag.'), ('Invoice', 'Monthly bill.'), ('Optimise', 'Use less, pay less.')],
    [('metering', 'measuring how much is used'), ('opex', 'operating expenditure — ongoing spending'), ('tariff', 'price list per unit')],
    table(['', 'Utility computing', 'Cloud computing'], [['What it is', 'a billing/business model', 'a full service model'], ['Includes self-service?', 'not necessarily', 'yes'], ['Relationship', 'one ingredient', 'uses utility billing']], minw=440),
    ['Every public cloud bill', 'Shared HPC centres charging per core-hour', 'Telecom data plans'],
    'John McCarthy suggested in 1961 that computing might one day be organised as a public utility — the idea behind today’s pay-as-you-go clouds.',
    'Utility computing is a pricing model, not a technology; exams like the distinction: cloud = utility billing + self-service + elasticity + broad access + pooling.')

A4 = mk(['Pooled data centres', 'Self-service APIs', 'Elastic, metered'], ['Regions|AZs, clusters|huge pools', 'self-service|console, CLI, API|minutes', 'elastic|scale up/down|pay per use'], ['green', 'blue', 'green'],
        ['providers pool resources in Regions worldwide', 'customers create services on demand', 'capacity grows and shrinks; usage is metered'],
        [('Pools', 'Providers pool resources in Regions.', ''), ('Self-service', 'Customers provision on demand by API.', ''), ('Elastic', 'Scale up and down; pay for what is used.', '')],
        'Cloud computing in action', 'The five characteristics together.', 'Cloud', 'Animation: pooled data centres; self-service APIs; elastic and metered.', 'c4anim')
T4 = vt(4, 'Cloud computing', 'green',
    '<b>Cloud computing</b> is a model for enabling ubiquitous, convenient, on-demand network access to a shared pool of configurable computing resources that can be rapidly provisioned and released with minimal management effort or service-provider interaction (NIST SP 800-145) — combining self-service, broad access, pooling, elasticity and metered (utility) billing.',
    'A cab app: book any size of car in minutes, ride as long as you need, pay per trip — and the company handles the cars.',
    'Everything TiffinGo runs on AWS, Azure and Google Cloud in this course.',
    'AWS, Microsoft Azure, Google Cloud, Oracle Cloud, IBM Cloud, Alibaba Cloud and regional providers.',
    'Lesson 1.1 introduced the five characteristics.', A4,
    'you need on-demand, elastic IT with global reach and managed services.',
    'workloads need sub-10 ms responses to local devices or must run offline — add edge/fog.',
    'Using computing services over the internet whenever you need them, paying only for what you use.',
    [('Request', 'API / console.'), ('Provision', 'From shared pools.'), ('Run', 'Managed by provider (per service model).'), ('Scale', 'Elastic.'), ('Bill', 'Metered.')],
    [('elastic', 'grows and shrinks automatically'), ('on-demand', 'available when requested, without waiting'), ('Region', 'geographic group of data centres')],
    table(['', 'Cloud', 'Edge'], [['Location', 'central Regions', 'near devices'], ['Latency', 'tens–hundreds of ms', 'a few ms'], ['Power', 'virtually unlimited', 'limited']], minw=420),
    ['Web and mobile apps', 'Big Data and AI', 'Enterprise IT'],
    'Amazon launched S3 and EC2 in 2006, the usual start date for modern public cloud; Google App Engine (2008) and Windows Azure (2010) followed.',
    'Cloud is now stretching outwards — Local Zones, Outposts, Azure Local, Google Distributed Cloud — blurring the line with fog and edge.')

A5 = mk(['Many devices', 'Local fog node', 'Cloud upstream'], ['devices|sensors, cameras|phones', 'fog|gateway, MEC|aggregates', 'cloud|history, ML|management'], ['green', 'violet', 'blue'],
        ['many devices in an area produce data', 'a nearby fog node aggregates, filters and coordinates', 'it sends summaries upstream and receives updates'],
        [('Devices', 'Many devices in an area produce data.', ''), ('Fog node', 'A nearby node aggregates, filters and coordinates.', ''), ('Cloud', 'Summaries go up; models and policies come down.', '')],
        'Fog computing in action', 'The layer between devices and cloud.', 'Fog', 'Animation: many devices; local fog node aggregates; cloud upstream.', 'c5anim')
T5 = vt(5, 'Fog computing', 'violet',
    '<b>Fog computing</b> (term popularised by Cisco around 2012) is a distributed layer of compute, storage and networking between end devices and the cloud — on gateways, routers, local servers or telco base stations — that aggregates, filters and processes data from many nearby devices and coordinates them, while forwarding selected data to the cloud.',
    'A local area manager between delivery riders and head office: collects reports from all riders in the area, solves local problems, and sends a daily summary upward.',
    'Each TiffinGo kitchen’s gateway collects bag alerts from all riders in its delivery zone and reassigns orders locally (step 4 of the animation).',
    'Industrial gateways, AWS Local Zones and Wavelength (telco 5G edge), Azure Extended Zones / private MEC, Google Distributed Cloud connected; open frameworks like EdgeX Foundry; standards from the OpenFog Consortium (merged into the Industrial Internet Consortium in 2019).',
    '', A5,
    'many devices in an area need coordination, aggregation or low latency, but each device is too weak to do it alone.',
    'devices are few and capable (edge alone suffices) or latency is not critical (cloud alone suffices).',
    'A middle layer near the devices — like a local gateway — that collects and processes their data before the cloud.',
    [('Connect', 'Devices to a gateway (MQTT, BLE, Wi-Fi).'), ('Aggregate', 'Combine streams.'), ('Decide', 'Local rules and coordination.'), ('Buffer', 'Store when uplink fails.'), ('Forward', 'Summaries to cloud.')],
    [('gateway', 'device connecting local devices to wider networks'), ('MEC', 'multi-access edge computing at telecom base stations'), ('aggregation', 'combining many readings into fewer')],
    table(['', 'Fog', 'Edge'], [['Where', 'between devices and cloud (LAN/telco)', 'on or next to one device'], ['Scope', 'many devices', 'one device / site'], ['Example', 'kitchen gateway', 'rider phone']], minw=440),
    ['Smart factories', 'Smart cities and traffic', 'Connected vehicles'],
    'Telcos place compute inside 5G networks (AWS Wavelength with operators, Azure private MEC) so apps like video analytics get single-digit-millisecond latency — fog by another name.',
    'Many vendors now call everything outside the Region “edge”; in exams and the C-DAC syllabus keep the distinction: edge = at the device, fog = the layer between.')

A6 = mk(['Data born here', 'Decide here', 'Send only results'], ['device|camera, sensor|phone, car', 'edge compute|on-device / next to it|ms decisions', 'upstream|alerts, summaries|to fog/cloud'], ['red', 'amber', 'green'],
        ['data is created at the device', 'processing happens on or right next to it, in milliseconds', 'only alerts and summaries travel upstream'],
        [('Data', 'Data is created at the device.', ''), ('Decide', 'Processing on or next to the device, in milliseconds.', ''), ('Send', 'Only results travel upstream.', '')],
        'Edge computing in action', 'Think where the data is born.', 'Edge', 'Animation: data born at the device; decision at the edge; only results sent.', 'c6anim')
T6 = vt(6, 'Edge computing', 'red',
    '<b>Edge computing</b> places processing and storage at or very near the source of data — on the device itself or on hardware next to it — to reduce latency and bandwidth, keep working without connectivity and keep sensitive data local, sending only results or summaries to fog or cloud.',
    'A cook tasting and adjusting salt at the stove instead of sending every spoonful to the head chef.',
    'The rider’s phone checks every bag reading and raises a “cold food” alert within a second, even in a tunnel (steps 2–3 of the animation).',
    'AWS IoT Greengrass, Outposts servers, Snowball Edge (existing customers); Azure IoT Edge; Google Distributed Cloud edge; on-device AI (TensorFlow Lite, ONNX Runtime); CDN edge functions (CloudFront Functions, Lambda@Edge, Cloudflare Workers).',
    'CDN edge locations were introduced in Lesson 5.1.', A6,
    'decisions must be immediate, bandwidth is costly, connectivity is unreliable or data must stay local (privacy).',
    'processing needs lots of data from many places or heavy compute — do it in the cloud.',
    'Processing data right where it is created — on the device or next to it — instead of sending it all far away.',
    [('Collect', 'Read sensors/cameras.'), ('Infer', 'Rules or small ML model.'), ('Act', 'Alert / control locally.'), ('Buffer', 'Store and forward.'), ('Update', 'New models/rules pushed from cloud.')],
    [('latency', 'delay between action and response'), ('bandwidth', 'how much data a link can carry'), ('inference', 'running a trained model to get a prediction')],
    table(['', 'Edge', 'Cloud'], [['Decision time', 'ms', '50–200 ms+ round trip'], ['Works offline', 'yes', 'no'], ['Compute', 'limited', 'massive']], minw=420),
    ['IoT and wearables', 'Video analytics and self-driving', 'Retail and kitchens'],
    'Modern phones and cameras run AI models on-device (face unlock, keyword spotting), sending nothing to the cloud for the decision itself — edge computing in everyone’s pocket.',
    'Fleet management is the hard part: updating models and fixing bugs on 2,000 devices safely needs staged rollouts and rollback — the cloud’s job in an edge design.')

SUMMARY = table(['#', 'Model', 'Core idea', 'Where it runs', 'TiffinGo example'], [
    ['1', 'Cluster', 'many machines as one', 'one data centre', 'Spark on EMR/Dataproc'], ['2', 'Grid', 'share across organisations', 'many sites', '— (research use)'], ['3', 'Utility', 'pay per use', 'provider billing', 'Lambda/S3 billing'],
    ['4', 'Cloud', 'on-demand services', 'provider Regions', 'apps on AWS'], ['5', 'Fog', 'layer between device and cloud', 'gateways, MEC', 'kitchen gateway'], ['6', 'Edge', 'process at the source', 'device / next to it', 'rider phone check']], minw=600)
CHECK = ('  <h3>Check yourself: which model?</h3>\n' +
    qx('A. Universities in 30 countries share computing for physics data.', ['Grid', 'Edge', 'Utility', 'Fog'], 0, 'Grid.') +
    qx('B. A camera detects a fall and alarms without internet.', ['Edge', 'Grid', 'Cloud', 'Cluster'], 0, 'Edge.') +
    qx('C. A factory gateway aggregates 500 sensors and forwards summaries.', ['Fog', 'Grid', 'Utility', 'Cluster'], 0, 'Fog.') +
    qx('D. You pay per GB-month for storage.', ['Utility model', 'Grid', 'Edge', 'Fog'], 0, 'Utility.'))

TYPES = ('  <p>Six models in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['Is utility computing a technology or a pricing model?', 'Edge or fog: where does the rider’s phone fit, and the kitchen gateway?', 'Why did grid computing stay mostly in research?'], 'types 3, 5–6 and 2') + MAP
         + jump(['Cluster', 'Grid', 'Utility', 'Cloud', 'Fog', 'Edge']) + T1 + T2 + T3 + T4 + T5 + T6
         + '\n  <h3 style="margin-top:34px">All six side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('Latency', 'Delay from event to decision.', 'Safety and UX need ms at the edge.', 'Alerts, video, control loops.'),
    ('Bandwidth', 'How much data the link can carry.', 'Raw data is expensive to send.', 'Filter, compress, summarise.'),
    ('Connectivity', 'Is the network always there?', 'Edge must work offline.', 'Store and forward.'),
    ('Privacy', 'Where personal data goes.', 'Keep raw data local; send results.', 'Faces, health, location.'),
    ('Compute power', 'What each tier can run.', 'Heavy ML training needs cloud.', 'Train in cloud, infer at edge.'),
    ('Fleet management', 'Updating thousands of nodes.', 'Bugs at scale need safe rollouts.', 'OTA updates, canaries, rollback.')])

DEEP = ('  <h3>Protocols you will meet</h3>\n' + table(['Protocol', 'Used for', 'Why'], [['MQTT', 'device → gateway/cloud messages', 'tiny overhead, publish/subscribe, works on weak links'], ['HTTPS', 'APIs, uploads', 'universal, but heavier per message'], ['CoAP', 'very constrained devices', 'UDP-based, small'], ['Bluetooth LE / Zigbee / LoRaWAN', 'sensor to nearby gateway', 'low power, short or long range']], minw=520) +
    '\n  <h3>Cloud IoT services today</h3>\n  <p><b>AWS IoT Core</b> (MQTT broker, device registry, rules engine) and <b>Azure IoT Hub</b> remain the main managed IoT ingest services. <b>Google retired Cloud IoT Core on 16 August 2023</b>; Google Cloud now relies on partners for device management and on Pub/Sub, Dataflow and BigQuery for ingest and analytics — the practical below uses Pub/Sub.</p>\n'
    '  <h3>Bandwidth maths for the TiffinGo bags</h3>\n' + table(['Design', 'Messages per hour (2,000 bags)', 'Approx. data per day*'], [['Raw to cloud (1/s)', '7,200,000', '≈ 34 GB'], ['Edge summary (1/min) + alerts', '≈ 120,000 + alerts', '≈ 0.6 GB'], ['Fog aggregate per zone (1/min)', '≈ 1,200 + alerts', '≈ 6 MB']], minw=520) +
    '\n  <p>*Assuming about 200 bytes per message. Per-message pricing makes the difference even larger than per-GB.</p>\n'
    '  <h3>Where the cloud providers put “edge” today</h3>\n  <ul><li><b>CDN edge locations</b>: hundreds of points of presence for caching and edge functions.</li><li><b>Metro / telco edge</b>: AWS Local Zones and Wavelength, Azure Extended Zones, Google Distributed Cloud connected.</li><li><b>On-premises edge</b>: Outposts servers, Azure Local, Google Distributed Cloud.</li><li><b>Device edge</b>: Greengrass, IoT Edge, on-device ML runtimes.</li></ul>')

clouds = vendor_tabs('<p><b>AWS:</b> IoT Core (MQTT ingest, rules), IoT Greengrass (edge runtime), Local Zones and Wavelength (fog/metro edge), Outposts servers, CloudFront Functions and Lambda@Edge; clusters with EMR and ParallelCluster.</p>',
    '<p><b>Azure:</b> IoT Hub (ingest, device twins), IoT Edge (containers on devices), Extended Zones and private MEC, Azure Local; clusters with HDInsight, CycleCloud; Azure Front Door edge.</p>',
    '<p><b>Google Cloud:</b> Pub/Sub (ingest — Cloud IoT Core retired Aug 2023), Dataflow and BigQuery for analytics, Google Distributed Cloud for edge, Cloud CDN / Media CDN; clusters with Dataproc, GKE, Cloud HPC Toolkit.</p>') + \
    cloud3([['Device ingest', 'IoT Core', 'IoT Hub', 'Pub/Sub (+ partners)'], ['Edge runtime', 'IoT Greengrass', 'IoT Edge', 'Google Distributed Cloud / partners'], ['Metro / telco edge', 'Local Zones, Wavelength', 'Extended Zones, private MEC', 'Distributed Cloud connected'], ['Data cluster', 'EMR', 'HDInsight / Fabric', 'Dataproc'], ['HPC cluster', 'ParallelCluster', 'CycleCloud', 'Cluster Toolkit']])

# ------------------------------------------------------------------ practical
EDGE = '''cat > edge.py <<'EOF'
# Simulated rider phone: 60 readings, sends only alerts (below 60 C for 3+ readings)
import json, random
random.seed(7); low = 0
for s in range(60):
    t = round(random.gauss(66, 3) - (8 if 30 <= s < 36 else 0), 1)
    low = low + 1 if t < 60 else 0
    if low == 3:
        print(json.dumps({"bag": "B-101", "second": s, "temp_c": t, "alert": "food cooling"}))
EOF
python3 edge.py'''

MOCKQ.extend([
 (mock('aws', ['AWS IoT', 'MQTT test client'], ['Connect', 'Test', 'Manage', 'Message routing'], 'Test',
       [('Subscribe to a topic', 'tiffingo/bags/#'), ('Publish to a topic', 'tiffingo/bags/B-101'), ('Message payload', '{"temp_c": 58.2, "alert": "food cooling"}')], 'Publish'),
  mock('az', ['Home', 'IoT Hub', 'Create'], ['Basics', 'Networking', 'Management', 'Review + create'], 'Basics',
       [('IoT hub name', 'tiffingo-hub-yourname'), ('Region', '▾ Central India'), ('Tier', '▾ Free (8,000 messages/day)')], 'Review + create'),
  mock('gcp', ['Pub/Sub', 'Topics', 'Create topic'], ['Topics', 'Subscriptions', 'Snapshots'], 'Topics',
       [('Topic ID', 'bag-alerts'), ('Add a default subscription', '[x] bag-alerts-sub')], 'Create')),
 (mock('aws', ['AWS IoT', 'MQTT test client', 'Subscriptions'], ['Connect', 'Test', 'Manage'], 'Test',
       [('tiffingo/bags/#', '{"bag":"B-101","second":32,"temp_c":57.0,"alert":"food cooling"}')], 'Clear'),
  mock('az', ['Home', 'IoT Hub', 'tiffingo-hub', 'Devices'], ['Overview', 'Devices', 'Built-in endpoints', 'Metrics'], 'Devices',
       [('Device ID', 'rider-phone-101'), ('Metrics · Telemetry messages sent', '1')], 'Add device'),
  mock('gcp', ['Pub/Sub', 'Subscriptions', 'bag-alerts-sub'], ['Topics', 'Subscriptions'], 'Subscriptions',
       [('Messages', 'Pull'), ('Message body', '{"bag":"B-101","second":32,"temp_c":57.0,…}')], 'Pull')),
 (mock('aws', ['Billing', 'Free Tier'], ['Bills', 'Free Tier', 'Cost Explorer'], 'Free Tier',
       [('AWS IoT Core', 'messages used this month'), ('Tip', 'publish alerts, not raw readings')], 'View all'),
  mock('az', ['Home', 'IoT Hub', 'tiffingo-hub', 'Metrics'], ['Overview', 'Metrics', 'Pricing and scale'], 'Metrics',
       [('Total number of messages used', 'today vs 8,000 free'), ('Tier', 'F1')], 'Add metric'),
  mock('gcp', ['Pub/Sub', 'Topics', 'bag-alerts', 'Metrics'], ['Topics', 'Subscriptions'], 'Topics',
       [('Published message count', 'per minute'), ('Published bytes', 'per minute')], 'Explore')),
])

STEP1 = ('1 · Create the cloud end: a message ingest point', tri(
    (['[[IoT Core]] → [[Test]] → [[MQTT test client]] → [[Subscribe to a topic]]: <code>tiffingo/bags/#</code> → [[Subscribe]]. Keep this tab open.', 'IoT Core needs no setup to receive messages from the CLI; real devices also need a registered thing and certificate.'],
     "aws iot describe-endpoint --endpoint-type iot:Data-ATS --query endpointAddress --output text\naws iot create-thing --thing-name rider-phone-101",
     'an endpoint like <code>a1b2c3…-ats.iot.ap-south-1.amazonaws.com</code> and the new thing’s ARN.'),
    (['[[IoT Hub]] → [[Create]]: resource group <code>rg-edge</code>, name <code>tiffingo-hub-yourname</code>, Central India, tier [[Free]] → [[Create]].', '[[Devices]] → [[Add device]] <code>rider-phone-101</code>.'],
     'az extension add --name azure-iot --upgrade\naz group create -n rg-edge -l centralindia\nHUB=tiffingo-hub-$RANDOM; az iot hub create -n $HUB -g rg-edge --sku F1 --partition-count 2\naz iot hub device-identity create -n $HUB -d rider-phone-101',
     'JSON for the hub (<code>"sku": {"name": "F1"}</code>) and the device. Only one free F1 hub is allowed per subscription.'),
    (['[[Pub/Sub]] → [[Topics]] → [[Create topic]]: <code>bag-alerts</code>, tick [[Add a default subscription]] → [[Create]].', 'Google retired Cloud IoT Core in 2023; devices or gateways now publish to Pub/Sub (directly or via a partner platform).'],
     'gcloud pubsub topics create bag-alerts\ngcloud pubsub subscriptions create bag-alerts-sub --topic=bag-alerts',
     '<code>Created topic [projects/…/topics/bag-alerts]</code> and the subscription.')),
    'The cloud tier receives events; deciding <i>which</i> events to send is the edge’s job (next step).')

STEP2 = ('2 · Run an “edge” filter and send only the alerts', tri(
    (['Run the simulated phone on the right in CloudShell; it prints only alert lines.', 'In the [[MQTT test client]] tab you should see the alert arrive on <code>tiffingo/bags/B-101</code>.'],
     EDGE + '\nEP=$(aws iot describe-endpoint --endpoint-type iot:Data-ATS --query endpointAddress --output text)\npython3 edge.py | while read -r line; do\n  aws iot-data publish --endpoint-url https://$EP --topic tiffingo/bags/B-101 \\\n    --cli-binary-format raw-in-base64-out --payload "$line"\ndone',
     '60 readings simulated, typically one alert line printed and published; it appears in the MQTT test client. 60 readings → 1 message: that is the edge saving bandwidth.'),
    (['Run the simulated phone in Cloud Shell (Bash).', '[[IoT Hub]] → [[Metrics]] → “Telemetry messages sent” rises by the number of alerts (metrics lag a few minutes).'],
     EDGE + '\npython3 edge.py | while read -r line; do\n  az iot device send-d2c-message -n $HUB -d rider-phone-101 --data "$line"\ndone\naz iot hub monitor-events -n $HUB --timeout 20 --enqueued-time $(($(date +%s)-120))000',
     'the alert JSON in <code>monitor-events</code> output (if monitor-events needs extra packages, the Metrics blade still shows the message count).'),
    (['Run the simulated phone in Cloud Shell.', '[[Subscriptions]] → <code>bag-alerts-sub</code> → [[Messages]] → [[Pull]] shows the alert.'],
     EDGE + '\npython3 edge.py | while read -r line; do\n  gcloud pubsub topics publish bag-alerts --message="$line"\ndone\ngcloud pubsub subscriptions pull bag-alerts-sub --auto-ack --limit=5',
     'a <code>messageIds</code> line per alert, then the alert JSON in the pulled messages.')),
    'Change the threshold in edge.py or remove the filter and count how many messages would have been sent — that number is your bandwidth and message bill.')

STEP3 = ('3 · Check usage against the free allowance', tri(
    (['[[Billing and Cost Management]] → [[Free Tier]] — AWS IoT Core message usage appears here (with some delay).'],
     'aws cloudwatch get-metric-statistics --namespace AWS/IoT --metric-name PublishIn.Success --start-time $(date -u -d "-1 hour" +%FT%TZ) --end-time $(date -u +%FT%TZ) --period 3600 --statistics Sum --query "Datapoints[0].Sum"',
     'the number of successful publishes in the last hour (a small number; may show <code>null</code> for a few minutes).'),
    (['[[IoT Hub]] → [[Metrics]] → “Total number of messages used” — compare with 8,000/day on F1.'],
     'az iot hub show-quota-metrics -n $HUB -o table',
     '<code>TotalMessages</code> current value and max value (8,000 for F1).'),
    (['[[Pub/Sub]] → [[Topics]] → <code>bag-alerts</code> → [[Metrics]]: published message count and bytes.'],
     'gcloud pubsub topics describe bag-alerts\ngcloud pubsub subscriptions describe bag-alerts-sub --format="value(ackDeadlineSeconds,messageRetentionDuration)"',
     'topic details and subscription settings (deadline 10 s, retention 7 days by default). Pub/Sub has a monthly free data allowance.')),
    'Message-based pricing is why edge filtering matters: cost grows with every message you choose to send.')

prac = practical(OWN_INTRO + ' You build the edge-to-cloud path: a cloud ingest point, a simulated rider phone (edge) that filters 60 readings into a few alerts, and a usage check. Everything fits free tiers.', [SETUP_STEP, STEP1, STEP2, STEP3],
    cleanup='<b>AWS:</b> <code>aws iot delete-thing --thing-name rider-phone-101</code>; close the MQTT test client. '
            '<b>Azure:</b> <code>az group delete -n rg-edge --yes --no-wait</code> (deletes the hub). '
            '<b>Google Cloud:</b> <code>gcloud pubsub subscriptions delete bag-alerts-sub --quiet</code>; <code>gcloud pubsub topics delete bag-alerts --quiet</code>. Delete <code>edge.py</code> from Cloud Shell if you like.')

mist = mistakes([
    ['Treating grid and cloud as the same.', 'Both share resources.', 'Grid: many owners, membership, batch. Cloud: one provider, self-service, pay per use.'],
    ['Calling utility computing a technology.', 'The word “computing”.', 'It is a metering/pricing model inside cloud.'],
    ['Streaming all raw sensor data to the cloud.', 'Simplest to build.', 'Filter and summarise at edge/fog.'],
    ['Edge apps that fail without network.', 'Cloud-first habits.', 'Store-and-forward, local decisions.'],
    ['Mixing up edge and fog.', 'Vendors use “edge” for everything.', 'Edge = at the device; fog = the layer between.'],
    ['Building on Google Cloud IoT Core.', 'Old tutorials.', 'Retired Aug 2023 — use Pub/Sub or a partner platform.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Cloud vs grid vs cluster vs utility; fog and edge computing concepts.'], ['AWS CLF-C02', 'Edge locations, Local Zones, Wavelength, Outposts; IoT services at a high level.'], ['AZ-900', 'Hybrid and edge options; IoT Hub; Azure Local.'], ['Google Cloud Digital Leader', 'Edge and distributed cloud; Pub/Sub for event ingestion.']], minw=560) + \
    qx('1. Resources owned by many organisations, shared for big batch jobs, is…', ['cluster', 'grid', 'edge', 'fog'], 1, 'Grid.') + \
    qx('2. Paying for compute like electricity describes…', ['utility computing', 'edge computing', 'grid computing', 'fog computing'], 0, 'Utility.') + \
    qx('3. Processing on the device itself to cut latency is…', ['edge', 'grid', 'utility', 'cluster'], 0, 'Edge.') + \
    qx('4. Which AWS offering puts compute inside telecom 5G networks?', ['Wavelength', 'Snowball', 'Glacier', 'Route 53'], 0, 'Wavelength.') + \
    qx('5. Which Google service should new designs use for device event ingestion?', ['Cloud IoT Core', 'Pub/Sub', 'Cloud Functions only', 'Filestore'], 1, 'IoT Core retired; Pub/Sub.') + \
    qx('6. Many similar machines in one site acting as one system is…', ['cluster', 'grid', 'fog', 'utility'], 0, 'Cluster.')

proj = miniproject('Mini project: TiffinGo hot-bag monitoring design',
    'Design the full edge–fog–cloud system for 2,000 bags and justify each tier.',
    ['<b>Tiers:</b> list what runs on the sensor, phone (edge), kitchen gateway (fog) and cloud.',
     '<b>Rules:</b> write the alert rule and what happens offline.',
     '<b>Bandwidth:</b> calculate daily messages and GB with and without edge filtering (deep-dive table).',
     '<b>Cloud:</b> choose ingest (IoT Core / IoT Hub / Pub/Sub) and storage/analytics.',
     '<b>Updates:</b> plan how new thresholds reach all phones safely (staged rollout).',
     '<b>Build:</b> extend edge.py (step 2) to also send a per-minute summary and measure message counts.'],
    'An architecture diagram, a bandwidth table and a working edge filter script.', 'Module 3 + 5.1 (edge locations) + Big Data track (Kafka, Spark).')

assemble_v2(HERE, story_h2='Seven million readings an hour', hook_html=hk,
    narration='TiffinGo added temperature sensors to its delivery bags so food stays hot. The vendor suggested streaming every reading straight to the cloud. The team asked where the thinking should really happen.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Cloud vs grid vs fog vs edge computing',
    formal='<b>Cluster computing</b> joins similar computers in one place into one system; <b>grid computing</b> coordinates distributed resources owned by different organisations for shared large-scale work; <b>utility computing</b> meters and bills computing like a public utility; <b>cloud computing</b> provides on-demand, self-service, elastic, metered access to pooled resources over the network (NIST); <b>fog computing</b> is a distributed layer between devices and the cloud that aggregates and processes data near its source; <b>edge computing</b> processes data at or next to the device that creates it.',
    simple='Cluster = many machines in one room as one; grid = many organisations sharing machines; utility = pay per use; cloud = rent IT services on demand; fog = a middle layer near devices; edge = process right at the device.',
    interview=['“Edge processes at the device, fog is the layer between devices and cloud, and the cloud does storage, analytics and fleet management. For example, the phone checks food temperature, the kitchen gateway coordinates, the cloud learns.”', '“Grid shares resources across organisations for batch science; cloud is one provider’s self-service, elastic, pay-per-use pool; utility computing is the billing model inside cloud.”'],
    terms_rows=[('Cluster', 'Many machines as one, one site.'), ('Grid', 'Shared across organisations.'), ('Utility computing', 'Pay-per-use model.'), ('Cloud', 'On-demand, elastic, metered services.'), ('Fog', 'Layer between devices and cloud.'), ('Edge', 'Processing at the device.'), ('MQTT', 'Lightweight publish/subscribe protocol.'), ('Latency', 'Delay to a decision.')],
    exam='Expect definitions and differences (especially grid vs cloud, edge vs fog), edge offerings (edge locations, Local Zones, Wavelength, Outposts) and the fact that Google Cloud IoT Core is retired.',
    picture_h2='Four tiers and six ideas', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Six computing models, one by one', TYPES)],
    how_h2='One reading: sensor → edge → fog → cloud', how_intro='Where each decision is made, and why.', how_anim=READ,
    parts_h2='Six factors that decide where to compute', parts_html=parts, lv='',
    myth_rows=[('Grid = cloud.', 'Different owners, access and workloads.', 'Type 2.'), ('Edge replaces the cloud.', 'Edge decides fast; cloud stores, learns and manages.', 'Animation step 6.'), ('Utility computing is a product.', 'It is a pricing model.', 'Type 3.')],
    extra_secs=[('deep', 'Deep dive', 'Protocols, IoT services today, bandwidth maths, where “edge” lives', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Define and compare cluster, grid, utility, cloud, fog and edge computing.', 'Explain where each decision happens in an edge–fog–cloud design.', 'Estimate bandwidth savings from edge filtering.', 'Build an edge-to-cloud alert pipeline on AWS, Azure or Google Cloud.', 'Name current IoT/edge services and the IoT Core retirement.'],
    next_html='Module 4 — <a href="../../04-virtualization/01-virtualization-and-hypervisors/">4.1 Virtualization and hypervisors</a>.',
    pre='<b>Before you start:</b> 3.1–3.3 and Lesson 5.1 (Regions and edge locations).')
