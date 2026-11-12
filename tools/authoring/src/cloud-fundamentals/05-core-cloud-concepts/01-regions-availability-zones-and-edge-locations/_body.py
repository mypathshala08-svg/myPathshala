import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def lat(a, b=None): return capsec('l51_latency.txt', a, b)
def edge(a, b=None): return capsec('l51_edge.txt', a, b)
def aws(a, b=None): return capsec('l51_aws.txt', a, b)
def ipr(a, b=None): return capsec('l11_cloud_is_real.txt', a, b)
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)

hk = hook('Why did TiffinGo’s app feel slow in Pune even though AWS is “in the cloud”?',
    'Because the cloud is not a fog — it is <b>real buildings in real cities</b>. TiffinGo had launched in <b>us-east-1 (Virginia)</b>, the console’s default. From a home connection in Maharashtra we measured a TCP connection to Virginia at <b>285 ms</b>, to Mumbai at <b>55 ms</b> — and to the Mumbai <b>CloudFront edge (BOM78)</b> in just <b>15 ms</b>. Where you put things decides speed, law and survival. This lesson explains <b>Regions, Availability Zones, edge locations</b>, and their newer cousins.',
    ['The hierarchy: global network → Regions → Availability Zones → data centres, plus edge locations.', 'How to choose a Region (latency, law, services, price) — with real measurements.', 'Local Zones, Wavelength and Outposts: the cloud moving closer to users.'])

def story_scene():
    o = t(180, 12, 'One app, three places to run it', 9, 'ink', bold=True)
    for i, (city, ms, tn) in enumerate([('Virginia (us-east-1)', '285 ms', 'red'), ('Mumbai (ap-south-1)', '55 ms', 'amber'), ('Edge in Mumbai (BOM78)', '15 ms', 'green')]):
        x = 8 + i * 118
        o += box(x, 24, 108, 92, tn, rx=8) + ic('globe' if i < 2 else 'lb', x + 42, 30, 0.9) + t(x + 54, 72, city, 6.9, 'ink', bold=True) + t(x + 54, 94, ms, 12, 'ink', bold=True)
    o += t(180, 134, 'Measured from a home connection in Maharashtra, 10 Nov 2026', 7.2, 'ink2')
    return o
scene_svg = scene('Three boxes: Virginia region 285 ms, Mumbai region 55 ms, Mumbai edge location 15 ms, measured from Maharashtra.', story_scene(), 'Distance is time: <tspan font-weight="700" class="s-acc">put things near your users</tspan>.', h=160)
dialogue = '''R> Sir, customers in Pune say the menu takes ages to load. Our servers are on AWS, so why?
A> Which Region did you launch in?
R> The console said “N. Virginia”, I just clicked Launch.
A> That is a data centre region in the USA — 13,000 km away. Every request crosses an ocean twice. And card payment data has to stay in India anyway.
K> So we move everything to Mumbai?
A> To Mumbai, spread across at least two Availability Zones so one building’s power failure cannot stop us, and with images served from CloudFront edge locations in Indian cities. Let’s understand each piece.'''

# ------------------------------------------------------------------ figures
def hierfig():
    o = t(320, 16, 'AWS global infrastructure — from the whole planet down to one building', 11, 'ink', bold=True)
    o += box(20, 30, 600, 44, 'violet', rx=10) + t(320, 50, 'Global network: private fibre linking everything', 9, 'ink', bold=True) + t(320, 66, 'AWS: 39 geographic Regions · 124 Availability Zones · 750+ CloudFront PoPs (AWS figures, Nov 2026)', 7.4, 'ink2')
    o += arrow(160, 74, 160, 92) + arrow(480, 74, 480, 92)
    o += box(20, 94, 300, 168, 'card', rx=10) + t(170, 112, 'Region: ap-south-1 (Mumbai)', 9, 'ink', bold=True) + t(170, 126, 'a separate geographic area; data stays here unless you move it', 7, 'ink2')
    for i in range(3):
        x = 30 + i * 96
        o += box(x, 136, 88, 104, 'blue', rx=6) + t(x + 44, 152, f'AZ {"abc"[i]}', 8.4, 'ink', bold=True) + t(x + 44, 164, f'aps1-az{[1,3,2][i]}', 6.8, 'ink2')
        for j in range(2):
            o += box(x + 8, 172 + j * 30, 72, 24, 'card', rx=4) + t(x + 44, 188 + j * 30, 'data centre', 6.8, 'ink')
    o += t(170, 256, 'AZs: separate power, cooling, network; < 100 km apart', 7, 'ink2')
    o += box(340, 94, 280, 76, 'green', rx=10) + t(480, 112, 'Edge locations (PoPs)', 9, 'ink', bold=True) + t(480, 128, 'in many more cities: Mumbai, Delhi, Chennai,', 7, 'ink2') + t(480, 140, 'Bengaluru, Hyderabad, Kolkata…', 7, 'ink2') + t(480, 158, 'CloudFront cache · Route 53 DNS · Global Accelerator', 7.2, 'ink', bold=True)
    o += box(340, 180, 280, 82, 'amber', rx=10) + t(480, 198, 'Extensions closer to users', 9, 'ink', bold=True) + t(480, 216, 'Local Zones (city) · Wavelength (inside 5G networks)', 7.2, 'ink') + t(480, 232, 'Outposts (AWS racks in your data centre)', 7.2, 'ink') + t(480, 250, 'each attached to a parent Region', 7, 'ink2')
    o += t(320, 284, 'Rule of thumb: Region = WHERE your data lives · AZ = HOW you survive a building failure · Edge = HOW FAST users get content.', 7.6, 'ink2')
    return o
HIER = bigfig('Hierarchy figure: global network; a Region (Mumbai) containing three Availability Zones, each with one or more data centres; edge locations in many Indian cities running CloudFront, Route 53 and Global Accelerator; extensions closer to users: Local Zones, Wavelength, Outposts.', hierfig(), h=296)

def latfig():
    o = t(320, 16, 'Real measurement: TCP connect time from Maharashtra to AWS Regions (median of 5)', 11, 'ink', bold=True)
    data = [('me-central-1 (UAE)', 42), ('ap-south-1 (Mumbai)', 55), ('ap-south-2 (Hyderabad)', 64), ('ap-southeast-1 (Singapore)', 70), ('eu-central-1 (Frankfurt)', 162), ('eu-west-1 (Ireland)', 165), ('us-east-1 (Virginia)', 285), ('us-west-2 (Oregon)', 293), ('sa-east-1 (São Paulo)', 324), ('ap-southeast-2 (Sydney)', 402)]
    for i, (n, ms) in enumerate(data):
        y = 32 + i * 24
        tn = 'green' if ms < 80 else ('amber' if ms < 200 else 'red')
        o += t(196, y + 14, n, 7.8, 'ink', anchor='end') + box(204, y + 2, ms * 1.0, 18, tn, rx=3) + t(210 + ms * 1.0, y + 15, f'{ms} ms', 7.6, 'ink', anchor='start', bold=True)
    o += t(20, 290, 'Surprise: the UAE Region answered faster than Mumbai — internet routes, not map distance, decide latency. Always measure.', 7.4, 'ink2', anchor='start')
    return o
LATF = bigfig('Bar chart of measured TCP connect times from Maharashtra: UAE 42 ms, Mumbai 55, Hyderabad 64, Singapore 70, Frankfurt 162, Ireland 165, Virginia 285, Oregon 293, São Paulo 324, Sydney 402.', latfig(), h=300)

picture = ('  <p>A cloud provider’s infrastructure is organised in layers. Learn this one picture and most exam questions on global infrastructure answer themselves:</p>\n' + HIER +
           '\n  <p>Why does it matter? Because every extra thousand kilometres adds delay to <i>every</i> request. We measured it from a real home connection in Maharashtra:</p>\n' + LATF)

# ------------------------------------------------------------------ how it works: request path
RN = {'u': (4, 54, 54, 50, 'phone', 'Customer', 'Pune'), 'dns': (66, 4, 60, 46, 'dns', 'Route 53', 'DNS'), 'e': (66, 104, 60, 46, 'lb', 'Edge BOM78', 'CloudFront'),
      'lb': (140, 54, 60, 50, 'lb', 'Load bal.', 'ap-south-1'), 'a': (214, 4, 64, 46, 'server', 'AZ a', 'menu VM'), 'b': (214, 104, 64, 46, 'server', 'AZ b', 'menu VM'), 'db': (292, 54, 64, 50, 'db', 'Database', 'Multi-AZ')}
RS = [dict(on=['u', 'dns'], hot='dns', move=(58, 70, 70, 40, 'lookup'), head='Step 1 · DNS finds the nearest entry point', text='The app asks for tiffingo.in. Route 53 (answered from an edge location) returns', text2='the address of the nearest CloudFront edge — here BOM78 in Mumbai.', svc='Route 53 runs at edge locations worldwide; latency-based routing picks the closest healthy endpoint'),
      dict(on=['u', 'dns', 'e'], hot='e', move=(58, 90, 70, 120, 'GET'), head='Step 2 · The edge serves what it has cached', text='Menu photos and CSS are cached at the edge: “Hit from cloudfront”. The phone gets', text2='them in ~15 ms instead of a round trip to the Region.', svc='Real header we saw: x-cache: Hit from cloudfront · x-amz-cf-pop: BOM78-P9'),
      dict(on=['u', 'dns', 'e', 'lb'], hot='lb', move=(126, 120, 150, 90, 'miss'), head='Step 3 · Dynamic requests go to the Region', text='Prices and orders cannot be cached, so the edge forwards them over AWS’s private', text2='network to the load balancer in the Mumbai Region (ap-south-1).', svc='The AWS backbone is usually faster and steadier than the public internet'),
      dict(on=['u', 'dns', 'e', 'lb', 'a', 'b'], hot='a', move=(200, 70, 220, 40, 'route'), head='Step 4 · The load balancer picks a healthy AZ', text='Requests are spread over menu servers in AZ a and AZ b — separate buildings', text2='with their own power, a few kilometres apart.', svc='Elastic Load Balancing is itself spread across the AZs you enable'),
      dict(on=list(RN), hot='db', move=(278, 30, 300, 60, 'query'), head='Step 5 · The database answers', text='The primary database runs in one AZ and copies every write synchronously to a', text2='standby in another AZ (Multi-AZ).', svc='Amazon RDS Multi-AZ, Azure zone-redundant SQL, Cloud SQL high availability'),
      dict(on=list(RN), hot='b', move=(200, 90, 220, 120, 'all'), extra=box(212, 2, 68, 50, 'red', rx=7) + t(246, 30, 'AZ a DOWN', 7.6, 'ink', bold=True), head='Step 6 · An AZ fails — users barely notice', text='A power failure takes out AZ a. Health checks fail; the load balancer sends', text2='everything to AZ b; the database fails over to its standby in about a minute or two.', svc='This is why every production design spans at least two AZs')]
PATH = flow_anim('A customer request across edge, Region and Availability Zones', 'Six steps from a phone in Pune to TiffinGo’s servers — and what happens when a building fails.', 'Request path', 'Animation: DNS lookup returns the nearest edge; edge serves cached content; dynamic requests go to the Mumbai Region load balancer; it spreads load over two AZs; the Multi-AZ database answers; when AZ a fails, traffic shifts to AZ b.', RN, RS, hid='path')

# ------------------------------------------------------------------ types
def mapfig():
    o = t(320, 16, 'Six kinds of location in a cloud — biggest to closest to the user', 11, 'ink', bold=True)
    items = [('1', 'Region', 'where data lives; 3+ AZs', 'violet'), ('2', 'Availability Zone', 'isolated data centres in a Region', 'blue'), ('3', 'Edge location (PoP)', 'cache + DNS in many cities', 'green'),
             ('4', 'Local Zone', 'cloud in a big city, near users', 'amber'), ('5', 'Wavelength Zone', 'inside a telecom 5G network', 'amber'), ('6', 'Outposts', 'AWS racks in your building', 'red')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 14 + (i % 3) * 206; y = 32 + (i // 3) * 80
        o += box(x, y, 198, 68, tn, rx=8) + pin(x + 14, y + 16, n) + t(x + 28, y + 20, a, 8.6, 'ink', anchor='start', bold=True) + t(x + 10, y + 46, b, 7.2, 'ink2', anchor='start')
    o += t(320, 210, 'Azure: regions, availability zones, edge sites, Extended Zones, Azure Local · Google Cloud: regions, zones, edge PoPs, Distributed Cloud.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of six location types: 1 Region, 2 Availability Zone, 3 edge location, 4 Local Zone, 5 Wavelength Zone, 6 Outposts, with Azure and Google equivalents.', mapfig(), h=222)

def a_region(k):
    o = t(180, 12, ['Four questions decide the Region', 'Compliance and latency first', 'Then services and price'][k], 9, 'ink', bold=True)
    q = [('Law / compliance', 'must data stay in India?'), ('Latency', 'where are users?'), ('Services', 'is the service offered?'), ('Price', 'same VM, different cost')]
    for i, (a, b) in enumerate(q):
        x = 10 + (i % 2) * 172; y = 28 + (i // 2) * 56
        on = (k == 0) or (k == 1 and i < 2) or (k == 2)
        tn = 'green' if (k == 1 and i < 2) or (k == 2 and i >= 2) else ('blue' if on else 'card')
        o += box(x, y, 164, 48, tn, rx=6) + t(x + 82, y + 20, a, 8, 'ink', bold=True) + t(x + 82, y + 36, b, 7, 'ink2')
    o += t(180, 150, ['', 'RBI rule + users in India → Mumbai or Hyderabad', 'both offer the needed services → Mumbai, Hyderabad as DR'][k], 7.6, 'green', bold=True)
    return o
A_REGION = cap([a_region(k) for k in range(3)], [('Four questions', 'Compliance, latency, service availability and price decide where', 'a workload should live — in that order of priority.'), ('Law and latency first', 'Payment data must be stored in India (RBI), and customers are in India:', 'only Indian Regions qualify.'), ('Then services and price', 'Check that every needed service exists in the Region and compare prices;', 'pick Mumbai as primary and Hyderabad for disaster recovery.')],
    'Choosing a Region', 'A decision, not a default.', 'Region choice', 'Animation: four criteria — compliance, latency, services, price; compliance and latency narrow choices to Indian Regions; services and price pick Mumbai with Hyderabad for DR.', 't1anim')
T1 = vtype(1, 'Region', 'violet',
    'A <b>Region</b> is a separate geographic area where a cloud provider operates a cluster of data centres, organised into multiple isolated Availability Zones; most resources are created in a specific Region, and data stays in that Region unless you explicitly move or replicate it.',
    'A country branch of a bank: the Mumbai branch keeps Mumbai accounts. Each branch is independent; moving money to another branch is a deliberate transfer.',
    'TiffinGo moves from us-east-1 to <b>ap-south-1 (Mumbai)</b>: latency drops from 285 ms to about 55 ms, and payment data stays in India as RBI requires. <b>ap-south-2 (Hyderabad)</b> becomes the disaster-recovery Region.',
    'AWS Regions (e.g. ap-south-1 Mumbai, ap-south-2 Hyderabad), Azure regions (Central India, South India, West India, Jio India West/Central), Google Cloud regions (asia-south1 Mumbai, asia-south2 Delhi).',
    '', A_REGION,
    'deciding where any workload and its data will live — always choose deliberately.',
    'accepting the console’s default Region, or assuming every service and instance type exists in every Region.',
    plain='A Region is a city-sized area where the cloud company has several data centres. You pick the Region when you create something, and your data stays there unless you copy it somewhere else.',
    how=[('Pick a Region per resource', 'Console Region selector, <code>--region</code> in the CLI, or provider default.'), ('Independent control plane', 'Each Region has its own API endpoints (ec2.ap-south-1.amazonaws.com) and is isolated from others, so a failure in one Region does not spread.'), ('Data stays put', 'Objects, volumes and databases stay in the Region; copying to another Region is explicit (S3 replication, AMI copy, snapshots).'), ('Opt-in Regions', 'Regions launched after March 2019 (like Hyderabad) must be enabled per account before use.'), ('Prices differ', 'The same instance costs differently per Region; data transfer between Regions is billed.')],
    words=[('data residency', 'a rule that data must be stored in a particular country'), ('endpoint', 'the web address of a service’s API in one Region'), ('opt-in Region', 'a Region you must enable before using'), ('DR', 'disaster recovery: a second site to recover in')],
    diff=table(['', 'Region', 'Availability Zone', 'Edge location'], [['Size', 'geographic area (city/metro)', 'one or more data centres', 'small site in a city'], ['Count (AWS)', '39', '124', '750+ PoPs'], ['You choose it for', 'law, latency, services, price', 'surviving a building failure', 'speed of delivery'], ['Runs', 'almost all services', 'your VMs, DBs, subnets', 'CloudFront, Route 53, Global Accelerator']], minw=560),
    where=['Every resource you create (VMs, buckets, databases)', 'Data-residency compliance (RBI, DPDP Act considerations)', 'Disaster recovery to a second Region', 'Serving users in different continents'],
    realworld='RBI’s 2018 directive on storage of payment system data requires payment data to be stored only in India; this is a major reason Indian banks, wallets and fintechs run in the Mumbai and Hyderabad cloud Regions.',
    pro='Region counts disagree between sources: AWS’s infrastructure page lists 39 geographic Regions (Nov 2026), while the public ip-ranges.json we parsed in Lesson 1.1 contains 42 region codes — it also includes GovCloud, China and Regions that are announced or opt-in. Always say which list you mean.')

def a_az(k):
    o = t(180, 12, ['Two AZs, load balanced', 'Power failure in AZ a', 'Traffic and database shift to AZ b'][k], 9, 'ink', bold=True)
    o += box(130, 24, 100, 30, 'violet', rx=6) + t(180, 43, 'load balancer', 8, 'ink', bold=True)
    for i, n in enumerate(['AZ a', 'AZ b']):
        x = 20 + i * 180
        down = k >= 1 and i == 0
        o += box(x, 70, 140, 70, 'red' if down else 'card', rx=8) + t(x + 70, 150, n + (' — power lost' if down else ''), 8, 'ink', bold=True)
        o += box(x + 10, 94, 56, 36, 'blue' if not down else 'card', rx=4) + t(x + 38, 116, 'app', 7.4, 'ink', bold=True)
        role = 'primary' if (i == 0 and k < 2) or (i == 1 and k == 2) else 'standby'
        o += box(x + 74, 94, 56, 36, 'green' if role == 'primary' and not down else 'card', rx=4) + t(x + 102, 110, 'DB', 7.4, 'ink', bold=True) + t(x + 102, 122, role, 6.2, 'ink2')
        if not (k == 2 and i == 0):
            o += f'<path d="M180,54 L{x + 38},94" style="stroke:{"#2E8B57" if not down else "#ccc"};stroke-width:1.6"/>'
    if k == 2:
        o += t(180, 18, '', 1)
    return o
A_AZ = cap([a_az(k) for k in range(3)], [('Spread over two AZs', 'App servers in AZ a and AZ b behind a load balancer; the database primary', 'in AZ a with a synchronous standby in AZ b.'), ('A whole building fails', 'Power, cooling or network trouble takes out AZ a. In a single-AZ design', 'the site would be down now.'), ('Fail over to AZ b', 'Health checks remove AZ a from the load balancer; the standby database is', 'promoted. Customers see at most a short blip.')],
    'Availability Zones in action', 'Why production always spans at least two AZs.', 'AZ failover', 'Animation: app and database across AZ a and AZ b; AZ a loses power; load balancer and database fail over to AZ b.', 't2anim')
T2 = vtype(2, 'Availability Zone (AZ)', 'blue',
    'An <b>Availability Zone</b> is one or more discrete data centres within a Region, with redundant power, cooling and networking, physically separated from the other AZs of the Region but connected to them by high-bandwidth, low-latency links, so that applications can be designed to survive the failure of a single location.',
    'Three separate kitchens of one restaurant chain in different parts of the same city: a fire or power cut in one kitchen does not stop the others, and they are close enough to deliver to the same customers quickly.',
    'TiffinGo runs two menu servers — one in ap-south-1a, one in ap-south-1b — behind a load balancer, with an RDS Multi-AZ database. When a power problem hits one AZ, orders continue from the other.',
    'AWS AZs (3 in Mumbai, 3 in Hyderabad), Azure availability zones (at least 3 in every zone-enabled region), Google Cloud zones (e.g. asia-south1-a/b/c).',
    '', A_AZ,
    'any production workload — spread servers, load balancers and databases across at least two AZs.',
    'you pin everything to one AZ “to save on data transfer”, or assume your “ap-south-1a” is the same physical place as another account’s “ap-south-1a”.',
    plain='Inside each Region there are several separate data-centre sites, a few kilometres apart, each with its own electricity and cooling. If one site has a problem, your app can keep running from another.',
    how=[('Separate sites', 'Each AZ has independent power, cooling and network; AWS says AZs are a meaningful distance apart but within 100 km of each other.'), ('Fast links', 'AZs in a Region are joined by redundant fibre with single-digit-millisecond latency, so synchronous replication is practical.'), ('You place resources', 'Subnets, VMs and volumes live in one AZ; load balancers and Multi-AZ databases span several.'), ('Names are shuffled per account', 'ap-south-1a in your account may be a different physical AZ from ap-south-1a in mine; the AZ ID (aps1-az1) is the true, shared identifier.'), ('Fail over', 'Health checks detect a failed AZ and route traffic to healthy ones.')],
    words=[('subnet', 'a slice of a VPC’s addresses, always in one AZ'), ('Multi-AZ', 'running a copy in a second AZ that takes over automatically'), ('synchronous replication', 'every write is saved in both places before it is confirmed'), ('AZ ID', 'the fixed identifier of a physical AZ, e.g. aps1-az1')],
    diff=table(['', 'AZ', 'Region', 'Azure availability set'], [['Protects against', 'loss of a data-centre site', 'loss of a whole area (with multi-Region)', 'rack / host failure inside one data centre'], ['Distance', 'kilometres', 'hundreds–thousands of km', 'same building'], ['Typical SLA (VMs)', 'AWS 99.99% region-level; Azure 99.99% across zones', 'design-dependent', 'Azure 99.95%']], minw=560),
    where=['Every production web tier', 'Databases with Multi-AZ standby', 'Kubernetes clusters with nodes in 3 AZs', 'Load balancers'],
    realworld='AWS publishes post-event summaries of major incidents; several have affected a single AZ (power or cooling issues), and customers that had spread across AZs generally kept running — which is why AWS’s Region-level EC2 SLA of 99.99% applies only to multi-AZ deployments.',
    pro='Because AZ letters are mapped per account, two companies cannot coordinate “both use ap-south-1a” for low latency — share AZ IDs (aps1-az1) instead. Our lab shows ap-south-1b mapped to aps1-az3.')

def a_edge(k):
    o = t(180, 12, ['First request: cache miss', 'Edge stores a copy', 'Next users: cache hit in ~15 ms'][k], 9, 'ink', bold=True)
    o += box(10, 40, 80, 50, 'blue', rx=6) + ic('phone', 38, 44, 0.8) + t(50, 82, 'user, Pune', 7, 'ink', bold=True)
    o += box(130, 34, 100, 62, 'green' if k >= 1 else 'card', rx=6) + t(180, 54, 'Edge BOM78', 8, 'ink', bold=True) + t(180, 70, 'Mumbai', 7, 'ink2') + (t(180, 86, 'menu.jpg cached', 6.8, 'green', bold=True) if k >= 1 else '')
    o += box(270, 34, 80, 62, 'violet', rx=6) + t(310, 58, 'origin', 8, 'ink', bold=True) + t(310, 74, 'S3 / Region', 7, 'ink2')
    if k == 0:
        o += packet(90, 65, 130, 65, 'GET') + packet(230, 65, 270, 65, 'miss') + t(180, 128, 'x-cache: Miss from cloudfront — fetched from origin', 7.2, 'ink', bold=True)
    if k == 1:
        o += packet(270, 80, 230, 80, 'copy') + t(180, 128, 'kept until its TTL expires', 7.2, 'ink', bold=True)
    if k == 2:
        o += packet(130, 65, 90, 65, 'HIT') + t(180, 128, 'x-cache: Hit from cloudfront · connect 15 ms (real)', 7.2, 'green', bold=True)
    return o
A_EDGE = cap([a_edge(k) for k in range(3)], [('First request: miss', 'The nearest edge does not have the file yet, so it fetches it from the', 'origin (S3 bucket or server in the Region).'), ('The edge keeps a copy', 'The file is cached at the edge for its time-to-live (TTL).', 'Bigger regional edge caches hold less popular files.'), ('Everyone nearby gets a hit', 'Later users in the area get it straight from the edge — our measurement:', 'BOM78, “Hit from cloudfront”, 15 ms to connect.')],
    'Edge locations in action', 'Content delivered from the nearest city, not the Region.', 'CDN caching', 'Animation: first request misses at edge BOM78 and fetches from origin; edge caches a copy; next request hits the edge with 15 ms connect time.', 't3anim')
T3 = vtype(3, 'Edge location (point of presence)', 'green',
    'An <b>edge location</b> (point of presence, PoP) is a smaller site in a major city, separate from Regions, where the provider runs latency-sensitive global services — content caching (CDN), DNS, DDoS protection and network acceleration — so that users are served from a location close to them.',
    'A local delivery hub for an online store: popular items are stocked in a hub in your city, so they reach you in hours; rare items still come from the main warehouse.',
    'TiffinGo serves menu photos through CloudFront. A customer in Pune gets them from the Mumbai edge BOM78 — we saw “Hit from cloudfront”, 15 ms to connect — while orders still go to the Region.',
    'AWS CloudFront (750+ PoPs, 15 regional edge caches), Route 53, AWS Global Accelerator, AWS Shield; Azure Front Door and Azure CDN edge sites; Google Cloud CDN and Media CDN on Google’s edge PoPs (200+ network edge locations).',
    '', A_EDGE,
    'serving images, video, downloads, websites and APIs to users spread over many cities; protecting against DDoS.',
    'content changes every second or must never be cached (set cache rules carefully), or you expect to run your own VMs at an edge — edge locations run provider services only.',
    plain='Small cloud sites in many cities keep copies of popular files (pictures, videos, web pages) so they reach you quickly from nearby, instead of travelling from a faraway data centre every time.',
    how=[('DNS steers the user', 'The CDN’s DNS returns the address of a nearby PoP.'), ('Check the cache', 'If the file is cached and fresh, it is returned at once (hit).'), ('Miss: ask upstream', 'If not, the PoP asks a regional edge cache, then the origin.'), ('Store with TTL', 'The response is cached for its time-to-live.'), ('Dynamic traffic', 'Uncacheable requests still enter the provider’s backbone at the edge, which is often faster than the public internet.'), ('Protect', 'DDoS protection and web-application firewalls run at the edge, far from your servers.')],
    words=[('CDN', 'content delivery network'), ('PoP', 'point of presence: an edge site'), ('origin', 'where the original content lives'), ('cache hit / miss', 'found / not found in the cache'), ('TTL', 'how long a cached copy stays valid')],
    diff=table(['', 'Edge location', 'Region', 'Local Zone'], [['Runs your VMs?', 'no — provider services only', 'yes', 'yes (selected services)'], ['Count', 'hundreds', 'dozens', 'dozens'], ['Main job', 'cache, DNS, protection', 'everything', 'low-latency compute near a city']], minw=520),
    where=['Websites and mobile apps (images, JS, CSS)', 'Video streaming', 'Software downloads and game patches', 'DNS (Route 53 answers from edges)', 'DDoS protection'],
    realworld='Video and e-commerce services rely on CDNs to absorb big events: the response headers we captured show aws.amazon.com and AWS’s static-content domain being served by CloudFront’s Mumbai PoP (BOM78), named after Mumbai airport’s code.',
    pro='PoP names use the nearest airport code: BOM (Mumbai), DEL (Delhi), MAA (Chennai), BLR (Bengaluru), HYD (Hyderabad), CCU (Kolkata). Read <code>x-amz-cf-pop</code> in any CloudFront response to see which city served you.')

def a_lz(k):
    o = t(180, 12, ['Parent Region far from a city', 'Local Zone in that city', 'Low latency for local users'][k], 9, 'ink', bold=True)
    o += box(220, 30, 130, 60, 'violet', rx=6) + t(285, 54, 'Parent Region', 8, 'ink', bold=True) + t(285, 70, 'ap-south-1 (Mumbai)', 7, 'ink2')
    o += box(10, 30, 90, 60, 'blue', rx=6) + t(55, 56, 'users in', 7.6, 'ink', bold=True) + t(55, 70, 'Delhi NCR', 7.6, 'ink', bold=True)
    if k == 0:
        o += packet(100, 60, 220, 60, '~1,150 km')
    if k >= 1:
        o += box(120, 96, 90, 50, 'amber', rx=6) + t(165, 116, 'Local Zone', 7.8, 'ink', bold=True) + t(165, 130, 'Delhi', 7, 'ink2') + f'<path d="M210,120 L285,90" style="stroke:#999;stroke-dasharray:4 3"/>'
    if k == 2:
        o += packet(55, 90, 120, 120, 'few ms') + t(260, 140, 'same VPC, same APIs', 7.2, 'green', bold=True)
    return o
A_LZ = cap([a_lz(k) for k in range(3)], [('Region far from users', 'Users in Delhi NCR reach the Mumbai Region over ~1,150 km —', 'fine for most apps, too slow for some.'), ('A Local Zone in the city', 'A Local Zone places EC2, EBS and a few other services in a city,', 'connected back to its parent Region.'), ('Low latency, same tools', 'Extend your VPC with a subnet in the Local Zone; local users get', 'single-digit-millisecond latency.')],
    'Local Zones in action', 'Cloud capacity inside a big city.', 'Local Zone', 'Animation: Delhi users far from the Mumbai Region; a Local Zone in Delhi attached to the parent Region; local users get low latency with the same VPC and APIs.', 't4anim')
T4 = vtype(4, 'Local Zone', 'amber',
    'A <b>Local Zone</b> is an extension of a Region placed in a large metropolitan area, providing selected services such as compute, block storage and load balancing close to end users for single-digit-millisecond latency, while connecting back to the parent Region for other services.',
    'A branch counter of your bank opened inside your office complex: you get quick service for common tasks; complex work is still done at the main branch.',
    'TiffinGo’s live kitchen-camera feed for Delhi customers needs very low latency. Video processing VMs run in a Local Zone near Delhi, attached to the Mumbai Region’s VPC.',
    'AWS Local Zones (opt-in per zone; AWS has announced Local Zones in Delhi and Kolkata — check the current list), Azure Extended Zones, Google Cloud’s nearest equivalent is Google Distributed Cloud connected / edge offerings.',
    '', A_LZ,
    'media production, real-time gaming, AR/VR, or apps that need very low latency for users in one city.',
    'you need every AWS service — Local Zones offer only a subset; and they are usually a single zone, so design for failover to the Region.',
    plain='A small piece of a cloud Region placed inside a big city, so people in that city get very fast responses, while it stays connected to the main Region.',
    how=[('Opt in', 'Enable the Local Zone group for your account (EC2 settings or CLI).'), ('Extend the VPC', 'Create a subnet in the Local Zone (it appears as an extra AZ-like zone).'), ('Launch resources', 'Run supported instance types, EBS volumes, load balancers there.'), ('Traffic stays local', 'Users in the city connect to nearby infrastructure.'), ('Back to the Region', 'Other services (S3, DynamoDB…) are reached through the parent Region.')],
    words=[('parent Region', 'the Region a Local Zone belongs to'), ('opt-in', 'switched off until you enable it'), ('metro', 'a big city area')],
    diff=table(['', 'Local Zone', 'Wavelength Zone', 'Outposts'], [['Located in', 'provider site in a metro', 'telecom 5G network', 'your own data centre'], ['Who owns the building', 'provider', 'telecom operator', 'you'], ['Main purpose', 'low latency for a city', 'ultra-low latency for 5G devices', 'on-prem latency / data residency']], minw=520),
    where=['Media rendering and live video', 'Multiplayer gaming servers', 'Hybrid migrations near on-prem data centres', 'Real-time analytics for a city'],
    realworld='AWS introduced Local Zones in Los Angeles in 2019 for media and entertainment studios that needed single-digit-millisecond latency for rendering and editing, and later expanded to many metros worldwide.',
    pro='Local Zone traffic to the internet can exit locally, but anything that calls Regional services (S3, DynamoDB, SSM) crosses back to the parent Region — profile which calls are on the hot path before assuming “local” means “fast”.')

T5 = vtype(5, 'Wavelength Zone', 'amber',
    'A <b>Wavelength Zone</b> embeds cloud compute and storage inside a telecommunications provider’s 5G network, so traffic from mobile devices reaches the application without leaving the carrier network, giving ultra-low latency for mobile and connected-device applications.',
    'A food stall set up inside a railway station: travellers do not even need to step out of the station to eat.',
    'A future TiffinGo feature — live AR menus on phones at a food festival — would benefit from processing inside the 5G network, if a Wavelength Zone exists with the local carrier.',
    'AWS Wavelength (with partner telecom operators in selected countries — check availability in India), Azure private MEC (multi-access edge compute) with operators, Google Distributed Cloud Edge with telecom partners.',
    '', '',
    'connected cars, AR/VR on phones, live video analytics, industrial IoT over 5G.',
    'users are not on the partner carrier’s 5G network — then there is no benefit.',
    plain='Cloud servers placed inside a mobile company’s 5G network, so phones and devices connected to that network get extremely fast responses.',
    how=[('Carrier hosts the zone', 'The telecom operator houses AWS infrastructure in its 5G network edge.'), ('Extend the VPC', 'Create a subnet in the Wavelength Zone and a carrier gateway.'), ('Device traffic stays in the network', 'Phones reach the app through the carrier network without internet hops.'), ('Region for the rest', 'Databases and other services stay in the parent Region.')],
    words=[('5G', 'the fifth generation of mobile networks'), ('carrier gateway', 'the connection between the zone and the mobile network'), ('MEC', 'multi-access edge computing: compute inside telecom networks')],
    diff=table(['', 'Wavelength', 'Local Zone'], [['Inside', 'telecom 5G network', 'provider metro site'], ['Best for', 'mobile/5G devices', 'all users in a city']], minw=420),
    where=['AR/VR and cloud gaming on phones', 'Connected vehicles', 'Smart factories over private 5G'],
    realworld='AWS launched Wavelength in 2019 with Verizon in the US and later added operators in other countries, placing EC2 inside their 5G networks for low-latency mobile applications.',
    pro='A Wavelength subnet gets carrier IP addresses, not public internet IPs — devices on other networks may not reach it directly, which surprises teams that test from office Wi-Fi.')

def f_out():
    a = box(34, 60, 154, 110, 'amber', rx=6) + t(111, 80, 'Your building', 8.4, 'ink', bold=True)
    a += box(54, 92, 50, 60, 'violet', rx=3) + t(79, 126, 'AWS', 7, 'ink', bold=True) + t(79, 138, 'rack', 6.8, 'ink2') + box(118, 92, 50, 60, 'card', rx=3) + t(143, 126, 'your', 7, 'ink') + t(143, 138, 'servers', 6.8, 'ink2')
    a += t(111, 190, 'The bank’s ATM inside', 7, 'ink') + t(111, 202, 'your office', 7, 'ink')
    r = box(240, 56, 170, 140, 'card', rx=8) + t(325, 74, 'Your data centre', 8.4, 'ink', bold=True) + box(252, 84, 146, 50, 'violet', rx=5) + t(325, 104, 'AWS Outposts rack', 8, 'ink', bold=True) + t(325, 120, 'EC2 · EBS · RDS · ECS/EKS', 6.8, 'ink2')
    r += box(252, 142, 146, 44, 'card', rx=5) + t(325, 162, 'factory systems /', 7.4, 'ink') + t(325, 176, 'local data', 7.4, 'ink')
    r += box(450, 56, 170, 140, 'blue', rx=8) + t(535, 74, 'Parent Region', 8.4, 'ink', bold=True) + t(535, 94, 'ap-south-1', 7.4, 'ink2') + t(535, 124, 'control plane:', 7.2, 'ink') + t(535, 138, 'console, APIs, updates', 7.2, 'ink') + t(535, 158, 'managed by AWS', 7.2, 'ink2')
    r += f'<path d="M410,126 L450,126" style="stroke:#555;stroke-width:2;stroke-dasharray:5 3"/>' + t(430, 116, 'service link', 6.6, 'ink2')
    r += t(431, 218, 'Same APIs and console as the Region — hardware in your building, operated by AWS', 7.2, 'ink2')
    return apanels('Left: a bank ATM placed inside an office building. Right: an AWS Outposts rack in the customer data centre next to local systems, connected by a service link to its parent Region which provides the control plane.', 'Outposts: AWS racks in your own data centre', 'an ATM inside your office', a, ['The bank’s machine,', 'your premises.'], 'The real thing: Outposts + parent Region', r)
T6 = vtype(6, 'Outposts (on-premises extension)', 'red',
    '<b>AWS Outposts</b> is a fully managed service that installs AWS-designed racks or servers in a customer’s own data centre or site, running AWS compute, storage and selected services locally with the same APIs, tools and console as the parent Region, which provides the control plane.',
    'A bank installing its own ATM inside your office: the machine and its software belong to and are run by the bank, but it sits on your premises for convenience.',
    'TiffinGo’s parent company has a central kitchen factory with machines that must respond in milliseconds and a rule that some data stays on-site. An Outposts rack there runs the control software with the same tools the cloud team uses in Mumbai.',
    'AWS Outposts racks and servers, Azure Local (formerly Azure Stack HCI) and Azure Stack Hub, Google Distributed Cloud.',
    f_out(), '',
    'workloads must stay on-premises (latency to local machines, data residency) but you want cloud APIs and operations.',
    'the service link to the Region is unreliable or the workload is small — you pay for the whole rack capacity.',
    plain='The cloud company puts its own computers inside your building. They work exactly like the cloud — same tools — but the data and processing stay in your premises.',
    how=[('Order', 'Choose a configuration; AWS delivers and installs the rack.'), ('Service link', 'The rack connects to its parent Region over your network or Direct Connect.'), ('Same APIs', 'Launch EC2/EBS on the Outpost from the normal console, selecting the Outpost subnet.'), ('AWS operates it', 'Hardware monitoring, patching and replacement are handled by AWS.'), ('Local data', 'Data on the Outpost stays on-premises; control-plane calls go to the Region.')],
    words=[('on-premises', 'in your own building or data centre'), ('control plane', 'the management side: APIs, console'), ('service link', 'the network connection back to the Region')],
    diff=table(['', 'Outposts', 'Private cloud (OpenStack)', 'Local Zone'], [['Who operates hardware', 'AWS', 'you', 'AWS'], ['Where', 'your site', 'your site', 'AWS metro site'], ['APIs', 'AWS', 'OpenStack', 'AWS']], minw=520),
    where=['Factories and hospitals with local systems', 'Data-residency needs where no Region exists', 'Low-latency trading or media workflows', 'Gradual migration of on-prem apps'],
    realworld='AWS Outposts became generally available in 2019 and is used by manufacturers, hospitals and financial firms that need AWS services next to on-premises systems or must keep data in a particular location.',
    pro='If the service link drops, running Outposts instances keep running, but you cannot launch or change resources until it returns — the control plane lives in the Region. Design operations runbooks for that “disconnected” mode.')

SUMMARY = table(['#', 'Location', 'Where', 'You run there', 'Pick it for', 'Azure', 'Google Cloud'], [
    ['1', 'Region', 'geographic area', 'almost everything', 'law, latency, services, price', 'region', 'region'], ['2', 'AZ', 'data centres in a Region', 'VMs, subnets, DB copies', 'surviving a site failure', 'availability zone', 'zone'],
    ['3', 'Edge location', 'many cities', 'CDN, DNS, protection (provider)', 'fast content delivery', 'Front Door / CDN edge', 'Cloud CDN edge'], ['4', 'Local Zone', 'big city', 'EC2, EBS, some services', 'low latency in one city', 'Extended Zones', 'Distributed Cloud'],
    ['5', 'Wavelength', 'telecom 5G network', 'EC2, EBS', '5G device latency', 'private MEC', 'Distributed Cloud Edge'], ['6', 'Outposts', 'your building', 'EC2, EBS, RDS, EKS…', 'on-prem + cloud APIs', 'Azure Local / Stack Hub', 'Distributed Cloud']], minw=820)
CHECK = ('  <h3>Check yourself: which location fits?</h3>\n' +
    qx('A. Payment data must stay in India and most users are in India.', ['us-east-1', 'An Indian Region (Mumbai/Hyderabad)', 'An edge location', 'Any Region'], 1, 'Compliance and latency both point to an Indian Region.') +
    qx('B. The site must survive a power failure in one data centre.', ['Use two Availability Zones', 'Use one bigger VM', 'Use an edge location', 'Use a Local Zone only'], 0, 'Spread across AZs with a load balancer and Multi-AZ DB.') +
    qx('C. Images load slowly for users all over India.', ['CloudFront edge locations', 'Outposts', 'Bigger EC2 instance', 'Wavelength'], 0, 'Cache static content at edges near users.') +
    qx('D. A factory needs AWS APIs on machines inside its own building.', ['Outposts', 'Edge location', 'Region', 'Availability Zone'], 0, 'AWS-managed racks on-premises.') +
    qx('E. Two companies both use “ap-south-1a”. Are they in the same building?', ['Always', 'Not necessarily — compare AZ IDs', 'Never', 'Only on weekends'], 1, 'AZ names are mapped per account; AZ IDs are fixed.'))

TYPES = ('  <p>Clouds place resources at six kinds of location. Each one, in the same pattern as Module 4: definition, plain words, analogy, how it works inside, picture or animation, how it differs, where it is used, a real-world example, TiffinGo’s scenario and an expert note.</p>\n'
         + challenge(['Why do sources disagree on how many AWS Regions there are?', 'Why can’t two companies agree to “both use ap-south-1a”?', 'How can you tell which city’s edge served a web page?'], 'types 1, 2 and 3') + MAP
         + jump(['Region', 'AZ', 'Edge', 'Local Zone', 'Wavelength', 'Outposts']) + T1 + T2 + T3 + T4 + T5 + T6
         + '\n  <h3 style="margin-top:34px">All six side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = table(['Factor', 'What to check', 'Example'], [
    ['1. Compliance / data residency', 'laws and contracts on where data may live', 'RBI payment data in India; government data rules'],
    ['2. Latency to users', 'measure from where users are', 'Maharashtra: Mumbai 55 ms, Virginia 285 ms'],
    ['3. Service and feature availability', 'is every service, instance type, GPU offered there?', 'newer services launch in us-east-1 first'],
    ['4. Price', 'compare the same resources across Regions', 'Region prices for the same instance differ'],
    ['5. Disaster-recovery partner', 'a second Region far enough away', 'Mumbai primary, Hyderabad DR'],
    ['6. Sustainability / power', 'some Regions report higher renewable energy share', 'provider sustainability reports']], minw=560)

DEEP = ('  <h3>Global vs regional vs zonal services</h3>\n' + table(['Scope', 'Meaning', 'AWS examples'], [
    ['Global', 'one instance worldwide', 'IAM, Route 53, CloudFront, Organizations'], ['Regional', 'lives in a Region, spread over its AZs automatically', 'S3, DynamoDB, Lambda, SQS, VPC'],
    ['Zonal', 'lives in one AZ — you must spread it yourself', 'EC2 instance, EBS volume, subnet']], minw=520) +
    '\n  <h3>Data transfer: location costs money too</h3>\n  <ul><li>Data <b>into</b> AWS from the internet is free; data <b>out</b> to the internet is billed (the first 100 GB per month across services is free).</li><li>Traffic <b>between AZs</b> in a Region is billed in each direction (a small per-GB charge) — a reason chatty services are placed carefully, but never a reason to give up multi-AZ.</li><li>Traffic <b>between Regions</b> is billed per GB — replicate deliberately.</li><li>Edge delivery (CloudFront) often costs less per GB than serving directly from the Region.</li></ul>\n'
    '  <h3>Azure and Google: the same ideas, different words</h3>\n  <ul><li><b>Azure region pairs</b>: most regions are paired with another in the same geography at least 300 miles away; platform updates roll out one region of a pair at a time, and one region per pair is prioritised for recovery in a large outage.</li><li><b>Azure availability zones</b>: every zone-enabled region has at least three.</li><li><b>Google Cloud</b> lists 43 regions and 130 zones (Nov 2026); a Google VPC is <b>global</b> — one network spans all regions, with regional subnets.</li></ul>')

clouds = vendor_tabs('<p><b>AWS:</b> 39 geographic Regions, 124 Availability Zones (Nov 2026), 750+ CloudFront PoPs and 15 regional edge caches; Local Zones, Wavelength Zones, Outposts. India: ap-south-1 Mumbai and ap-south-2 Hyderabad.</p>',
    '<p><b>Azure:</b> regions grouped into geographies, many with region pairs; zone-enabled regions have at least three availability zones; Front Door/CDN edge sites; Extended Zones; Azure Local for on-premises. India: Central India (Pune), South India (Chennai), West India (Mumbai) and others.</p>',
    '<p><b>Google Cloud:</b> 43 regions and 130 zones, 200+ network edge locations (Nov 2026); global VPC; Google Distributed Cloud for edge and on-premises. India: asia-south1 (Mumbai) and asia-south2 (Delhi).</p>') + \
    cloud3([['Geographic unit', 'Region', 'Region (in a geography)', 'Region'], ['Isolated location in it', 'Availability Zone', 'Availability zone', 'Zone'], ['Content edge', 'CloudFront PoPs', 'Front Door / CDN', 'Cloud CDN / Media CDN'],
            ['City extension', 'Local Zones', 'Extended Zones', 'Distributed Cloud'], ['On-premises', 'Outposts', 'Azure Local / Stack Hub', 'Distributed Cloud'], ['India locations', 'Mumbai, Hyderabad', 'Pune, Chennai, Mumbai…', 'Mumbai, Delhi']])

proof = [
    ('Step 1 · Latency from India to ten Regions (real)', code('bash', 'terminal on a computer in Maharashtra', 'for r in ap-south-1 ap-south-2 ap-southeast-1 me-central-1 eu-west-1 eu-central-1 \\\n         us-east-1 us-west-2 sa-east-1 ap-southeast-2; do\n  # median of 5 TCP connects to each Region’s EC2 API endpoint\n  …curl -w "%{time_connect}" https://ec2.$r.amazonaws.com/…\ndone', lat('== 1)')), 'Indian and Gulf Regions answer in 40–65 ms; the US in about 290 ms. Every request from Pune to Virginia pays that 285 ms at least once — usually several times (TCP + TLS handshakes).'),
    ('Step 2 · Which edge served us? (real)', code('bash', 'terminal', "curl -sI https://d1.awsstatic.com/ | grep -i -E 'x-amz-cf-pop|x-cache|age'", edge('== 2)', '== 3)')), 'BOM78 = a CloudFront PoP in Mumbai. “Hit” means the file came from the edge’s cache; <code>age</code> says it has been cached for about 20 hours.'),
    ('Step 3 · Edge vs far Region (real)', code('bash', 'terminal', 'curl -s -o /dev/null -w "connect %{time_connect}s total %{time_total}s\\n" https://d1.awsstatic.com/', edge('== 3)')), 'Connecting to the edge took 15 ms — 19× faster than reaching Virginia.'),
    ('Step 4 · AZ names vs AZ IDs (emulator)', code('bash', 'terminal', "aws ec2 describe-availability-zones --region ap-south-1 \\\n  --query 'AvailabilityZones[].[ZoneName,ZoneId,State]' --output table", aws('== 1)', '== 2)')), 'In this account ap-south-1b is aps1-az3. Another account may see a different mapping. (Output from the moto emulator; the three Mumbai zone IDs match AWS’s published ones.)'),
    ('Step 5 · How many Regions does AWS publish IP ranges for? (real)', code('bash', 'terminal', 'curl -s https://ip-ranges.amazonaws.com/ip-ranges.json | python3 -c "…count regions…"', ipr('== 1)', '== 2)')), '42 region codes in the IP file vs 39 geographic Regions on AWS’s infrastructure page — the IP list also covers GovCloud, China and announced/opt-in Regions.')]

prac = practical('Every step shows a <b>UI way</b> and a <b>CLI way</b>. Steps 1–2 work from any computer with a browser and curl. Steps 3–5 use the AWS console or CLI; <b>CLI outputs marked “emulator” come from the moto AWS emulator</b>. None of these steps costs money.', [
    ('1 · Measure latency from your own location', uicli(
        ['Open a browser and visit an online “AWS latency test” page that pings Region endpoints (many free ones exist), or use the CLI on the right.', 'Note your three fastest Regions — they may not be the nearest on the map.'],
        code('bash', 'terminal (Linux/macOS/WSL; Windows PowerShell has curl.exe)', 'for r in ap-south-1 ap-south-2 me-central-1 ap-southeast-1 us-east-1; do\n  printf "%-15s " $r\n  curl -s -o /dev/null -w "%{time_connect}\\n" https://ec2.$r.amazonaws.com/\ndone', lat('== 1)')), ui_label='UI way — browser'),
        'Our surprise: UAE beat Mumbai from a Maharashtra ISP. Measure from where your users are.'),
    ('2 · See which edge location serves you', uicli(
        ['Open <code>https://aws.amazon.com</code> in Chrome/Edge → press [[F12]] → [[Network]] tab → reload.', 'Click the first request → [[Headers]] → [[Response Headers]]: find <code>x-amz-cf-pop</code> (e.g. BOM78) and <code>x-cache</code>.'],
        code('bash', 'terminal', "curl -sI https://d1.awsstatic.com/ | grep -i -E 'x-amz-cf-pop|x-cache|age'", edge('== 2)', '== 3)')), ui_label='UI way — browser developer tools'),
        'The first three letters are an airport code: BOM = Mumbai, DEL = Delhi, MAA = Chennai.'),
    ('3 · List Regions and choose one', uicli(
        ['AWS Console → top-right [[Region selector]] (e.g. “N. Virginia”) → choose [[Asia Pacific (Mumbai) ap-south-1]].', 'At the bottom of the list, [[Manage Regions]] (or Account → [[AWS Regions]]) shows which opt-in Regions such as [[Asia Pacific (Hyderabad)]] are enabled.'],
        code('bash', 'terminal', "aws ec2 describe-regions --all-regions \\\n  --query 'Regions[].[RegionName,OptInStatus]' --output table\naws configure set region ap-south-1      # make Mumbai your CLI default"), ui_label='UI way — AWS Management Console'),
        'Set the default once and you will never launch in Virginia by accident again.'),
    ('4 · AZ names and AZ IDs', uicli(
        ['[[EC2]] → [[Dashboard]] → panel [[Zones]] (or [[Settings]] → [[Zones]]): lists each zone’s name and Zone ID.', 'Compare with a colleague’s account: the same name may show a different ID.'],
        code('bash', 'terminal', "aws ec2 describe-availability-zones --region ap-south-1 \\\n  --query 'AvailabilityZones[].[ZoneName,ZoneId,State]' --output table", aws('== 1)', '== 2)')), ui_label='UI way — AWS Management Console'),
        'Output from the moto emulator. Use Zone IDs when coordinating across accounts.'),
    ('5 · Opt in to a Region or a Local Zone (look, do not necessarily enable)', uicli(
        ['Region: Account menu → [[AWS Regions]] → select [[Asia Pacific (Hyderabad)]] → [[Enable]] (takes minutes).', 'Local Zone: [[EC2]] → [[Settings]] → [[Zones]] → filter [[Local Zones]] → select a zone group → [[Manage]] → [[Enabled]].'],
        code('bash', 'terminal', "aws account enable-region --region-name ap-south-2\naws account get-region-opt-status --region-name ap-south-2\n\naws ec2 describe-availability-zones --all-availability-zones --region ap-south-1 \\\n  --filters Name=zone-type,Values=local-zone --query 'AvailabilityZones[].[ZoneName,GroupName,OptInStatus]'\naws ec2 modify-availability-zone-group --region ap-south-1 --group-name <group-name> --opt-in-status opted-in"), ui_label='UI way — AWS Management Console'),
        'Enabling is free; you pay only for resources you create there. Needs account-level permissions (not available on every learner account).')],
    cleanup='Nothing to clean up — these steps only read information or change account settings. If you enabled a Region or Local Zone only for practice, you may disable it again from the same screen (or <code>aws account disable-region</code>).')

mist = mistakes([
    ['Launching in the console’s default Region (often N. Virginia).', 'Nobody looked at the Region selector.', 'Set your default Region in the console and in <code>aws configure</code>; check it before every launch.'],
    ['Everything in one AZ “to keep it simple”.', 'Default subnet choices, cost worries.', 'Use at least two AZs for anything in production; the Region-level SLA requires it.'],
    ['“My resource disappeared!”', 'Looking at a different Region in the console.', 'Resources are regional — switch the Region selector.'],
    ['Assuming every service/instance type exists everywhere.', 'New features launch Region by Region.', 'Check the Regional Services List or describe-instance-type-offerings before designing.'],
    ['Copying data between Regions without noticing the bill.', 'Cross-Region replication and transfers are billed per GB.', 'Replicate only what DR needs; watch Cost Explorer “data transfer”.'],
    ['Choosing a Region only by map distance.', 'Internet routes are not straight lines.', 'Measure latency from real user locations (our UAE vs Mumbai surprise).'],
    ['Thinking an edge location can run your VM.', 'Confusing PoPs with Local Zones.', 'Edges run provider services (CDN, DNS); use Local Zones for your own compute near a city.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Global infrastructure: regions, availability zones, edge locations.'], ['AWS CLF-C02', 'Regions, AZs, edge locations, Local Zones, Wavelength, Outposts; how to choose a Region; high availability with multiple AZs.'], ['AZ-900', 'Regions, region pairs, sovereign regions, availability zones.'], ['Google Cloud Digital Leader', 'Regions and zones, global network, edge.']], minw=520) + '\n  <h3>Exam-style questions with explanations</h3>\n' + \
    qx('1. Which statement about Availability Zones is correct?', ['An AZ is a CloudFront cache', 'An AZ is one or more isolated data centres within a Region', 'An AZ spans several Regions', 'Each account has one AZ'], 1, 'AZs are isolated locations inside a Region with independent power and networking.') + \
    qx('2. What is the main purpose of an edge location?', ['Run RDS databases', 'Cache and deliver content close to users (CloudFront), DNS', 'Store EBS snapshots', 'Host IAM'], 1, 'Edges serve CloudFront, Route 53 and similar latency-sensitive global services.') + \
    qx('3. A company must keep data in its own data centre but wants AWS APIs. Which service?', ['Local Zones', 'AWS Outposts', 'Wavelength', 'CloudFront'], 1, 'Outposts runs AWS infrastructure on-premises.') + \
    qx('4. Which factor should usually be checked FIRST when selecting a Region?', ['Colour of the console', 'Compliance / data residency requirements', 'Number of AZs only', 'Alphabetical order'], 1, 'Legal requirements can rule Regions out entirely; then latency, services, price.') + \
    qx('5. To achieve high availability for EC2, you should…', ['use a bigger instance', 'deploy across multiple Availability Zones', 'use one AZ with backups', 'use edge locations'], 1, 'Multiple AZs protect against the failure of one location.') + \
    qx('6. In Azure, which feature pairs regions at least 300 miles apart for disaster recovery?', ['Availability sets', 'Region pairs', 'Resource groups', 'Front Door'], 1, 'Region pairs get sequential updates and prioritised recovery.')

proj = miniproject('Mini project: choose and design TiffinGo’s Region strategy',
    'Produce a one-page, evidence-based Region decision and a multi-AZ layout — the kind of document architects present.',
    ['<b>Requirements:</b> write TiffinGo’s constraints — users in Maharashtra, Delhi NCR and Bengaluru; payment data must stay in India; budget sensitive.',
     '<b>Measure:</b> run the latency script (practical step 1) from at least two cities (ask friends/colleagues), and record the medians.',
     '<b>Check services:</b> <code>aws ec2 describe-instance-type-offerings --region ap-south-1 --filters Name=instance-type,Values=m7i.large</code> and the same for ap-south-2; check that RDS and the services you need exist in both.',
     '<b>Compare prices:</b> look up the same instance’s On-Demand price in both Indian Regions (AWS Pricing Calculator).',
     '<b>Decide:</b> fill a scorecard (compliance, latency, services, price, DR) and pick primary + DR Regions.',
     '<b>Design:</b> draw a diagram: CloudFront → ALB in 2 AZs → app servers in 2 AZs → RDS Multi-AZ; S3 with cross-Region replication to the DR Region for backups.',
     '<b>Estimate cost</b> of the design in the AWS Pricing Calculator and attach the link.'],
    'A one-page decision with measured latency, a scorecard, a multi-AZ diagram and a cost estimate.', 'This lesson + 4.3 (VPC) + 5.4 (SLAs) + 5.5 (pricing).')

assemble_v2(HERE, story_h2='Fast in Virginia, slow in Pune', hook_html=hk,
    narration='TiffinGo’s first cloud servers were launched with the console’s default Region. Indian customers noticed: every tap on the app crossed an ocean.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Regions, Availability Zones and edge locations',
    formal='A <b>Region</b> is a physical location in the world where a cloud provider clusters data centres; each Region is isolated from others and consists of multiple <b>Availability Zones</b> — one or more discrete data centres with redundant power, networking and connectivity, physically separated but linked by low-latency networks. <b>Edge locations</b> (points of presence) are separate sites in many cities that run latency-sensitive services such as content delivery and DNS close to end users.',
    simple='A Region is a city-area where the cloud has data centres; Availability Zones are separate buildings inside it so one failure does not stop you; edge locations are small sites in many cities that deliver content quickly.',
    interview=['“AWS organises its infrastructure into Regions — isolated geographic areas — each with multiple Availability Zones, which are separate data centres with independent power and networking, connected by low-latency links. I deploy across at least two AZs for high availability and choose the Region by compliance, latency, service availability and cost.”', '“Edge locations are separate points of presence in many cities that run CloudFront, Route 53 and Global Accelerator to serve users with low latency.”', '“For example, from Maharashtra I measured about 55 ms to Mumbai and 285 ms to Virginia, and CloudFront served our static files from the Mumbai PoP BOM78 in 15 ms.”'],
    terms_rows=[('Region', 'Geographic area with several AZs.'), ('Availability Zone', 'Isolated data centre(s) in a Region.'), ('AZ ID', 'Fixed identifier, e.g. aps1-az1.'), ('Edge location / PoP', 'City site for CDN and DNS.'), ('Regional edge cache', 'Bigger cache between PoPs and origin.'), ('Local Zone', 'Region extension in a metro.'), ('Wavelength Zone', 'Compute inside a 5G network.'), ('Outposts', 'AWS racks on your premises.'), ('Latency', 'Delay for data to travel.'), ('Data residency', 'Rule on where data must be stored.')],
    exam='CLF-C02: “high availability” → multiple AZs; “low latency content delivery” → CloudFront/edge; “disaster recovery” → multiple Regions; “on-premises with AWS APIs” → Outposts. AZ-900: region pairs and sovereign regions.',
    picture_h2='The global infrastructure in one picture — and what distance costs', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Six kinds of cloud location, one by one', TYPES)],
    how_h2='Follow one request from a phone to the Region', how_intro='Edge, Region and AZs working together — including the moment one AZ fails.', how_anim=PATH,
    parts_h2='How to choose a Region: six factors', parts_html=parts, lv='',
    myth_rows=[('“The cloud” is not in any particular place.', 'Every resource lives in a real Region and AZ.', 'Hierarchy figure.'), ('Nearest on the map = fastest.', 'Internet routes decide; UAE beat Mumbai in our test.', 'Latency chart.'), ('One AZ is enough if the VM is big.', 'Size does not protect against a site failure.', 'Type 2 animation.')],
    extra_secs=[('deep', 'Deep dive', 'Global vs regional vs zonal services, data-transfer costs, Azure and Google differences', DEEP)],
    clouds_html=clouds, proof_h2='Real proof: latency, edges and AZ IDs', proof_intro='Steps 1–3 and 5 are real measurements from a home connection in Maharashtra and AWS’s public files on 10 Nov 2026; step 4 is from the moto emulator.', proof_steps=proof,
    practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Explain Regions, Availability Zones and edge locations and how they relate.', 'Choose a Region using compliance, latency, services, price and DR — with measurements.', 'Explain Local Zones, Wavelength Zones and Outposts and when to use each.', 'Explain AZ names vs AZ IDs and global/regional/zonal services.', 'Do each practical step in the console or with the CLI.'],
    next_html='<a href="../02-resource-pooling-and-multitenancy/">5.2 Resource pooling and multitenancy</a>.',
    pre='<b>Before you start:</b> <a href="../../01-introduction/01-what-is-cloud-computing/">1.1 What is cloud computing</a> and <a href="../../04-virtualization/03-network-storage-and-data-virtualization/">4.3 (VPC)</a> help.')
