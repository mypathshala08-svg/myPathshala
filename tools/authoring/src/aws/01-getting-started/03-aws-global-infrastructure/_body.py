import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
sys.path.insert(0, HERE)
from scenes import az_failure, single_vs_multi, latency_map
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


hk = hook('At 1:10 pm on a weekday, one data centre in Mumbai lost power. TiffinGo’s app kept taking lunch orders. The competitor across the road was down for two hours.',
    'Both ran on AWS Mumbai. TiffinGo had placed its servers in <b>two Availability Zones</b>; the competitor had everything in one. This lesson explains how AWS’s physical world is built — <b>Regions</b>, <b>Availability Zones</b>, <b>data centres</b>, <b>Local Zones</b>, <b>Wavelength Zones</b>, <b>Outposts</b> and <b>edge locations</b> — how to choose a Region, and how failure is contained. On <b>your own</b> account (or in the simulator) you will list Regions, map AZ names to AZ IDs, find the Delhi and Kolkata Local Zones, and measure latency to Regions yourself.',
    ['Region = where your data lives; AZ = how you survive a data-centre failure.', 'AZ names differ between accounts — AZ IDs do not.', 'Edge locations bring content close to users; they are not where your servers run.'])

def story_scene():
    o = t(180, 12, 'Same Region, different design', 9, 'ink', bold=True)
    o += box(8, 28, 160, 74, 'red', rx=8) + t(88, 48, 'Competitor', 8.4, 'ink', bold=True) + t(88, 64, 'all servers in one AZ', 7, 'ink2') + t(88, 78, 'AZ loses power', 7, 'ink2') + t(88, 92, 'down 2 hours', 7.4, 'ink', bold=True)
    o += box(192, 28, 160, 74, 'green', rx=8) + t(272, 48, 'TiffinGo', 8.4, 'ink', bold=True) + t(272, 64, 'servers in 2 AZs + LB', 7, 'ink2') + t(272, 78, 'one AZ loses power', 7, 'ink2') + t(272, 92, 'orders keep flowing', 7.4, 'ink', bold=True)
    o += t(180, 122, 'Availability is a design choice, not a default', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Left: the competitor ran everything in one Availability Zone and was down two hours when it lost power. Right: TiffinGo ran in two AZs behind a load balancer and kept taking orders.', story_scene(), 'Spread across <tspan font-weight="700" class="s-acc">AZs</tspan>, survive a data centre.', h=132)
dialogue = '''R> Sir, I thought AWS never goes down.
A> AWS builds each Availability Zone to fail independently. Whether your app survives depends on whether you used more than one.
K> And if the whole Mumbai Region had a problem?
A> Rare, but possible. Then you need a second Region — Hyderabad — with a copy of your data. That is disaster recovery, and it costs more.
R> Our Dubai customers say the menu photos load slowly.
A> That is distance, not failure. Edge locations cache the photos near them. Let’s draw the whole map.'''

def bigpic():
    o = t(320, 14, 'AWS global infrastructure, from the planet to one data centre', 10.5, 'ink', bold=True)
    o += grp('cloud', 10, 24, 620, 250, 'AWS Cloud — 39 Regions, 124 Availability Zones (Nov 2026)')
    o += grp('region', 22, 44, 372, 186, 'Region: Asia Pacific (Mumbai) ap-south-1')
    for i, (az, azid) in enumerate([('AZ aps1-az1', 'e.g. ap-south-1a'), ('AZ aps1-az2', 'e.g. ap-south-1b'), ('AZ aps1-az3', 'e.g. ap-south-1c')]):
        x = 34 + i * 120
        o += grp('az', x, 64, 110, 120, az)
        o += t(x + 55, 84, 'name: ' + azid, 6.4, 'ink2')
        for j in range(2):
            o += box(x + 12 + j * 46, 92, 40, 40, 'blue', rx=4) + ai('server', x + 20 + j * 46, 96, 0.9) + t(x + 32 + j * 46, 144, 'data centre', 5.6, 'ink2')
        o += t(x + 55, 172, 'own power, cooling, network', 5.8, 'ink2')
    o += t(208, 204, 'AZs: many km apart, within 100 km; names map to IDs differently per account', 6.6, 'ink2')
    o += arrow(144, 124, 154, 124) + arrow(264, 124, 274, 124)
    o += grp('region', 404, 44, 120, 86, 'Region ap-south-2')
    o += t(464, 80, 'Hyderabad', 8, 'ink', bold=True) + t(464, 96, '3 AZs', 6.8, 'ink2') + t(464, 112, 'DR / data residency', 6.4, 'ink2')
    o += grp('onprem', 404, 140, 120, 90, 'Local Zones')
    o += t(464, 170, 'Delhi · Kolkata', 7.6, 'ink', bold=True) + t(464, 186, 'parent: ap-south-1', 6.4, 'ink2') + t(464, 202, 'single-digit ms to the city', 6.2, 'ink2')
    o += svc(580, 60, 'globe', 'Edge locations', 'CloudFront PoPs', 'amber', w=84)
    o += svc(580, 130, 'server', 'Outposts', 'AWS rack in your DC', 'violet', w=84)
    o += svc(580, 200, 'phone', 'Wavelength', '5G operator edge', 'green', w=84)
    o += t(320, 262, 'Region → AZs → data centres; Local Zones, Wavelength and Outposts extend a Region; edge locations serve content.', 7, 'ink2')
    return o
BIG = bigfig('AWS global infrastructure: the AWS Cloud contains Regions such as Mumbai ap-south-1, which has three Availability Zones each made of one or more data centres with independent power and networking; Hyderabad ap-south-2 is a second Indian Region; Local Zones in Delhi and Kolkata extend Mumbai; edge locations, Outposts and Wavelength Zones sit outside Regions.', bigpic(), h=280)

picture = ('  <p>AWS’s physical world has one main hierarchy and four extensions. Learn the hierarchy first:</p>\n' + BIG + '\n  <h3>Two situations every architect must picture</h3>\n  <p><b>Situation 1 — a data centre loses power.</b> Same Region, same outage, two different designs:</p>\n' + single_vs_multi() + '\n  <p><b>Situation 2 — customers far from the Region.</b> Distance, not failure, makes Dubai users wait:</p>\n' + latency_map() +
    '\n  <h3>The numbers (check the live page — they grow every year)</h3>\n' + table(['Item', 'Count / fact', 'Source of truth'], [
        ['Regions', '39 geographic Regions, 124 Availability Zones; more announced (Saudi Arabia, Chile)', 'AWS Global Infrastructure page'],
        ['Availability Zones per Region', 'at least 3 in most Regions; Mumbai 3, Hyderabad 3', '<code>aws ec2 describe-availability-zones</code>'],
        ['India', 'Regions: Mumbai (2016), Hyderabad (2022); Local Zones: Delhi, Kolkata (parent Mumbai); many edge locations', 'console Region list; Local Zones page'],
        ['AZ separation', 'many kilometres apart, all within 100 km of each other in a Region', 'AWS Regions and AZs page'],
        ['Edge network', 'hundreds of edge locations and regional edge caches worldwide for CloudFront and Route 53', 'CloudFront key features page']], minw=600))


SOLVE = az_failure()

def mapfig():
    o = t(320, 16, 'Seven building blocks of AWS global infrastructure', 11, 'ink', bold=True)
    items = [('1', 'Region', 'e.g. ap-south-1', 'blue'), ('2', 'Availability Zone', 'isolated location', 'green'), ('3', 'Data centre', 'building inside an AZ', 'card'), ('4', 'Local Zone', 'Delhi, Kolkata', 'amber'),
             ('5', 'Wavelength Zone', 'inside 5G networks', 'violet'), ('6', 'Outposts', 'AWS rack on-premises', 'red'), ('7', 'Edge location', 'CloudFront / Route 53', 'amber')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 8.4, 'ink', bold=True) + t(x + 78, y + 54, b, 6.8, 'ink2')
    o += t(320, 210, '1–3 are the core hierarchy; 4–6 extend a Region closer to users; 7 serves content and DNS at the edge.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of seven building blocks: Region, Availability Zone, data centre, Local Zone, Wavelength Zone, Outposts, edge location.', mapfig(), h=222)

def gi(n, name, tone, d, an, ex, tip, A, use, avoid, plain, how, words, diff, rw, pro):
    return vt(n, name, tone, d, an, ex, tip, '', A, use, avoid, plain, how, words, diff, ['CLF-C02 Domain 3', 'SAA-C03 (resilient design)', 'C-DAC cloud module'], rw, pro)

A1 = mk(['Pick Region', 'Resources live there', 'Data stays there'], ['choose|latency, law|services, price', 'create|VPC, S3, RDS|in that Region', 'stays|unless you|copy it out'], ['blue', 'amber', 'green'],
        ['choose a Region by latency, law, services and price', 'regional resources are created in that Region only', 'data stays in the Region unless you replicate it'],
        [('Choose', 'Latency, compliance, services, price.', ''), ('Create', 'Resources live in that Region.', ''), ('Stay', 'Data does not leave unless you copy it.', '')],
        'Region', 'A deliberate, legal choice.', 'Region', 'Animation: pick Region; resources live there; data stays there.', 'g1anim')
T1 = gi(1, 'Region', 'blue',
    'A <b>Region</b> is a separate geographic area (such as <code>ap-south-1</code>, Mumbai) containing multiple isolated Availability Zones; Regions are independent of each other, and data stays in the Region where you put it unless you explicitly copy it elsewhere.',
    'A city with several independent power stations: you choose which city to live in; the city’s design keeps the lights on.',
    'TiffinGo chooses ap-south-1 for Indian customers and keeps a backup copy in ap-south-2 (Hyderabad).',
    'Tip: pick the Region first and write it down — moving a running system between Regions later is a migration project.', A1,
    'you create almost any resource.', 'you assume a resource in Mumbai is visible in Singapore — it is not.',
    'One of AWS’s geographic areas, such as Mumbai.',
    [('Latency', 'Close to users.'), ('Law', 'Data residency rules.'), ('Services', 'Is the service there?'), ('Price', 'Varies by Region.'), ('DR', 'Pair with a second Region.')],
    [('Region code', 'ap-south-1, us-east-1…'), ('opt-in Region', 'newer Regions disabled by default'), ('partition', 'aws, aws-cn, aws-us-gov — separate worlds')],
    table(['', 'Mumbai ap-south-1', 'Hyderabad ap-south-2', 'N. Virginia us-east-1'], [['Opened', '2016', '2022', '2006'], ['Best for', 'most Indian workloads', 'Indian DR, second Region', 'global services, newest features']], minw=460),
    'Exams test “choose a Region by compliance, proximity, service availability and pricing”.',
    'Prices differ by Region — the same instance can cost noticeably more or less; compare in the Pricing Calculator.')

A2 = mk(['AZ a', 'AZ b', 'AZ c'], ['AZ a|own power|own network', 'AZ b|many km away|<100 km', 'AZ c|fast private|links'], ['green', 'green', 'green'],
        ['each AZ has independent power, cooling and network', 'AZs are separated by meaningful distance, within 100 km', 'high-bandwidth, low-latency links allow synchronous replication'],
        [('Isolated', 'Own power, cooling, network.', ''), ('Separated', 'Many km apart, within 100 km.', ''), ('Linked', 'Low-latency private fibre.', '')],
        'Availability Zone', 'Fail separately, work together.', 'AZ', 'Animation: AZ a; AZ b; AZ c.', 'g2anim')
T2 = gi(2, 'Availability Zone (AZ)', 'green',
    'An <b>Availability Zone</b> is one or more discrete data centres with redundant power, networking and connectivity in a Region; AZs in a Region are physically separated (many kilometres, but within 100 km) and connected by high-bandwidth, low-latency links, so applications can run across them for high availability.',
    'Three branches of the same bank in one city, each with its own generator: one branch flooding does not stop the others.',
    'TiffinGo runs web servers in ap-south-1a and ap-south-1b behind a load balancer.',
    'Tip: “highly available” in an exam answer almost always means “across multiple AZs”.', A2,
    'you need the system to survive a data-centre failure.', 'you put a single instance in one AZ and call it “highly available”.',
    'An isolated group of data centres inside a Region.',
    [('Subnet', 'Each subnet lives in one AZ.'), ('Spread', 'Instances in 2–3 AZs.'), ('LB', 'Distributes across AZs.'), ('Replicate', 'Multi-AZ DB.'), ('Pay', 'Inter-AZ data transfer.')],
    [('AZ name', 'ap-south-1a — mapped per account'), ('AZ ID', 'aps1-az1 — same physical AZ for everyone'), ('Multi-AZ', 'deployed across AZs')],
    table(['', 'Single AZ', 'Multi-AZ'], [['Survives data-centre failure', 'no', 'yes'], ['Cost', 'lower', 'more instances + inter-AZ transfer'], ['Typical use', 'dev/test', 'production']], minw=420),
    'Most exam scenario answers for “highly available” are multi-AZ, not multi-Region.',
    'Use AZ IDs (aps1-az1) when coordinating with another account — ap-south-1a in your account may be a different building from ap-south-1a in theirs.')

A3 = mk(['Building', 'Racks + power', 'Your VM'], ['building|guarded|no visits', 'inside|servers, UPS|generators', 'host|runs your|instance'], ['card', 'amber', 'blue'],
        ['AWS data centres are guarded buildings you never visit', 'inside: racks of servers, redundant power and cooling', 'your instance runs on a host in one of them'],
        [('Building', 'Secure, unmarked, no customer visits.', ''), ('Inside', 'Racks, UPS, generators, cooling.', ''), ('Host', 'Your instance runs on one server.', '')],
        'Data centre', 'Physical layer AWS secures.', 'Data centre', 'Animation: building; racks and power; your VM.', 'g3anim')
T3 = gi(3, 'Data centre', 'card',
    'A <b>data centre</b> is the physical building housing servers, storage and network equipment; AWS does not disclose locations, customers never visit them, and physical security of the data centre is AWS’s responsibility under the shared responsibility model.',
    'A bank’s cash vault: you use the money, but you never walk into the vault.',
    'Auditors check AWS’s physical security through SOC and ISO reports in AWS Artifact, not by visiting.',
    'Tip: “Who is responsible for physical security?” → AWS, always.', A3,
    'auditors ask about physical security.', 'you plan for “one data centre” — design at the AZ level instead.',
    'The physical building where AWS servers run.',
    [('Security', 'Guards, CCTV, biometrics.'), ('Power', 'UPS + generators.'), ('Cooling', 'Redundant.'), ('Disposal', 'Disks destroyed securely.'), ('Audit', 'SOC/ISO reports.')],
    [('colocation', 'renting rack space in someone else’s building'), ('UPS', 'battery backup'), ('SOC report', 'independent audit of controls')],
    table(['Layer', 'Responsible'], [['Building, guards, power', 'AWS'], ['Hardware, hypervisor', 'AWS'], ['Your data and configuration', 'you']], minw=360),
    'Shared responsibility questions always place physical security with AWS.',
    'Download AWS Artifact reports when a customer’s security questionnaire asks about data-centre controls.')

A4 = mk(['Parent Region', 'Local Zone', 'Users nearby'], ['parent|ap-south-1|Mumbai', 'zone|Delhi / Kolkata|opt in', 'users|ms latency|in that city'], ['blue', 'amber', 'green'],
        ['every Local Zone has a parent Region', 'you opt in, then place selected resources there', 'users in that city get single-digit-millisecond latency'],
        [('Parent', 'Attached to a Region (Mumbai).', ''), ('Opt in', 'Enable the zone group; add a subnet.', ''), ('Users', 'Very low latency in that city.', '')],
        'Local Zone', 'A Region’s outpost in a city.', 'Local Zone', 'Animation: parent Region; Local Zone; users nearby.', 'g4anim')
T4 = gi(4, 'Local Zone', 'amber',
    'A <b>Local Zone</b> extends a Region into a metro area, placing selected compute, storage and database services close to users for single-digit-millisecond latency; India has Local Zones in <b>Delhi</b> (<code>ap-south-1-del-1a</code>) and <b>Kolkata</b> (<code>ap-south-1-ccu-1a</code>), both with Mumbai as parent Region; you opt in and use them through subnets of your VPC.',
    'A franchise counter of a Mumbai restaurant in Delhi: a small menu, but much faster for Delhi customers.',
    'A Delhi gaming studio runs game servers in the Delhi Local Zone; its databases stay in Mumbai.',
    'Tip: only a subset of services and instance types are available in a Local Zone — check before designing.', A4,
    'users in one city need very low latency (gaming, live media, trading tools).', 'you just need “India” — Mumbai or Hyderabad is enough.',
    'A small extension of a Region in another city.',
    [('Opt in', 'modify-availability-zone-group.'), ('Subnet', 'In the Local Zone.'), ('Launch', 'Supported types only.'), ('Connect', 'Via parent Region.'), ('Pay', 'Often higher prices.')],
    [('parent Region', 'the Region a Local Zone belongs to'), ('zone group', 'ap-south-1-del-1'), ('zone type', 'local-zone')],
    table(['', 'Region', 'Local Zone'], [['Services', 'all for that Region', 'selected'], ['AZs', '3+', 'usually one zone'], ['Use', 'everything', 'latency-sensitive parts']], minw=420),
    'CLF-C02 asks which option gives the lowest latency to users in a specific metro: Local Zone.',
    'Local Zones are opt-in; enabling one is free — you pay only for resources you launch there.')

A5 = mk(['5G phone', 'Telco edge', 'Your app'], ['device|on 5G|network', 'Wavelength|inside telco|data centre', 'app|ultra-low|latency'], ['violet', 'amber', 'green'],
        ['a phone or device is on a 5G network', 'Wavelength Zone sits inside the telecom operator’s data centre', 'traffic reaches your app without leaving the operator network'],
        [('Device', 'On a partner 5G network.', ''), ('Zone', 'Inside the operator’s network.', ''), ('App', 'Ultra-low latency to mobile users.', '')],
        'Wavelength Zone', 'AWS inside the mobile network.', 'Wavelength', 'Animation: 5G phone; telco edge; your app.', 'g5anim')
T5 = gi(5, 'Wavelength Zone', 'violet',
    'A <b>Wavelength Zone</b> embeds AWS compute and storage inside a telecommunications provider’s 5G network, so traffic from mobile devices reaches applications without leaving the operator network — for ultra-low-latency mobile use cases; availability depends on partner operators and cities.',
    'A food stall inside the railway station instead of outside it: commuters do not even leave the platform.',
    'Connected-car alerts or AR shopping apps that must respond in milliseconds to phones on 5G.',
    'Tip: Wavelength is about <b>mobile/5G</b> latency; Local Zones are about <b>city</b> latency for any network.', A5,
    'mobile apps on 5G need the lowest possible latency.', 'your users are on broadband/Wi-Fi — use Local Zones or a Region.',
    'AWS computers placed inside a 5G mobile network.',
    [('Partner', 'Telecom operator.'), ('Opt in', 'Zone group.'), ('Subnet', 'In the zone.'), ('Carrier gateway', 'Connects to mobile network.'), ('App', 'Low-latency edge part.')],
    [('5G', 'fifth-generation mobile network'), ('carrier gateway', 'routes traffic to/from the operator network'), ('MEC', 'multi-access edge computing')],
    table(['', 'Local Zone', 'Wavelength Zone'], [['Located', 'metro area', 'inside a 5G operator network'], ['Best for', 'city users on any network', 'mobile devices on 5G']], minw=420),
    'Exam keyword: “5G” or “mobile edge” → Wavelength.',
    'Check the AWS Wavelength locations page for current operators and cities before promising it to a client.')

A6 = mk(['Order rack', 'AWS installs', 'Same APIs'], ['order|in console|sized rack', 'install|in your DC|AWS-managed', 'use|EC2, EBS, RDS|on-premises'], ['red', 'amber', 'green'],
        ['order an Outposts rack sized for your needs', 'AWS delivers, installs and maintains it in your data centre', 'you use the same AWS APIs and console, on-premises'],
        [('Order', 'Choose capacity.', ''), ('Install', 'AWS installs and manages it in your building.', ''), ('Use', 'Same APIs, tools and services locally.', '')],
        'Outposts', 'AWS hardware in your building.', 'Outposts', 'Animation: order rack; AWS installs; same APIs.', 'g6anim')
T6 = gi(6, 'AWS Outposts', 'red',
    '<b>AWS Outposts</b> is fully managed AWS infrastructure (racks or servers) installed in a customer’s own data centre or site, running AWS services such as EC2, EBS and RDS locally with the same APIs and tools, connected back to a parent Region — for low latency to on-premises systems, local data processing or data residency.',
    'Renting a branded vending machine for your office: the company stocks and repairs it, you use it on your floor.',
    'A hospital processes imaging locally on Outposts because the scanners and the data must stay on site.',
    'Tip: Outposts is a hybrid-cloud answer: “AWS services on-premises”.', A6,
    'data or latency must stay on your site but you want AWS APIs.', 'you only need a VPN to AWS — that is not Outposts.',
    'AWS servers installed and managed in your own building.',
    [('Order', 'Console.'), ('Site prep', 'Power, network, space.'), ('Install', 'By AWS.'), ('Link', 'To parent Region.'), ('Operate', 'AWS maintains hardware.')],
    [('hybrid cloud', 'on-premises + cloud working together'), ('service link', 'connection from Outpost to its Region'), ('rack', 'cabinet of servers')],
    table(['', 'Local Zone', 'Outposts'], [['Who owns the building', 'AWS', 'you'], ['Who manages hardware', 'AWS', 'AWS'], ['Why', 'city latency', 'on-premises latency, residency']], minw=420),
    'CLF-C02: “run AWS infrastructure on-premises” → Outposts.',
    'Outposts needs reliable connectivity to its parent Region for management — plan network redundancy.')

A7 = mk(['User request', 'Nearest edge', 'Cache or origin'], ['user|Dubai|opens menu', 'edge|nearest PoP|Route 53 too', 'cache|hit: instant|miss: Mumbai'], ['amber', 'blue', 'green'],
        ['a user anywhere requests content', 'DNS routes them to the nearest edge location', 'cache hit is served instantly; a miss is fetched from the origin and cached'],
        [('Request', 'User opens a page.', ''), ('Edge', 'Nearest point of presence.', ''), ('Serve', 'From cache, or fetch from origin.', '')],
        'Edge location', 'Content near users.', 'Edge', 'Animation: user request; nearest edge; cache or origin.', 'g7anim')
T7 = gi(7, 'Edge locations (points of presence)', 'amber',
    '<b>Edge locations</b> are sites in many more cities than Regions where AWS runs CloudFront (content delivery), Route 53 (DNS), Global Accelerator and edge security (Shield, WAF); <b>regional edge caches</b> sit between edge locations and the origin to keep more content close to users. Your servers do not run there.',
    'Local courier pickup counters: the warehouse is in Mumbai, but parcels wait at a counter near you.',
    'TiffinGo’s menu photos in Mumbai are cached at an edge location near Dubai customers.',
    'Tip: “reduce latency for static content to global users” → CloudFront (edge locations).', A7,
    'you serve images, videos, files or APIs to users far from your Region.', 'you think you can launch EC2 at an edge location — you cannot.',
    'Small AWS sites near users that cache and deliver content.',
    [('DNS', 'Route 53 at the edge.'), ('Cache', 'CloudFront.'), ('Origin', 'S3 / ALB / EC2.'), ('TTL', 'How long cached.'), ('Security', 'WAF, Shield at the edge.')],
    [('PoP', 'point of presence'), ('origin', 'where the original content lives'), ('cache hit', 'served from the edge')],
    table(['', 'Region', 'Edge location'], [['Runs your servers', 'yes', 'no'], ['Count', 'tens', 'hundreds'], ['Used by', 'all regional services', 'CloudFront, Route 53, Global Accelerator, WAF']], minw=420),
    'Edge locations are in Domain 3 of CLF-C02 and in every CloudFront question.',
    'Most of a CloudFront bill is data out; caching more (longer TTLs) cuts both latency and origin cost.')

SUMMARY = table(['#', 'Block', 'What it is', 'Use it for'], [
    ['1', 'Region', 'geographic area with 3+ AZs', 'where data lives; compliance'], ['2', 'Availability Zone', 'isolated DCs in a Region', 'high availability'], ['3', 'Data centre', 'physical building', '(AWS’s job)'],
    ['4', 'Local Zone', 'Region extension in a metro', 'city latency (Delhi, Kolkata)'], ['5', 'Wavelength Zone', 'inside 5G networks', 'mobile edge'], ['6', 'Outposts', 'AWS rack on-premises', 'hybrid, on-site data'], ['7', 'Edge location', 'CDN/DNS sites', 'fast content worldwide']], minw=600)

TYPES = ('  <p>Seven building blocks, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, real-world example and an expert tip.</p>\n'
         + challenge(['Why can ap-south-1a be a different building in two accounts?', 'Which block gives Delhi users the lowest latency for a game server?', 'Can you run EC2 at an edge location?'], 'types 2, 4 and 7') + MAP
         + jump(['Region', 'AZ', 'Data centre', 'Local Zone', 'Wavelength', 'Outposts', 'Edge']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY)

parts = wwu([
    ('Region choice', 'Latency, law, services, price.', 'The most permanent decision.', 'Write it in the design doc.'),
    ('Multi-AZ design', 'Every tier in 2–3 AZs.', 'Survives a data-centre failure.', 'Subnets per AZ, LB, Multi-AZ DB.'),
    ('Multi-Region (DR)', 'Second Region with data copies.', 'Survives a Region-wide event.', 'Backups, replication, Route 53 failover.'),
    ('Edge delivery', 'CloudFront, Route 53.', 'Speed for distant users.', 'Cache static content.'),
    ('Extensions', 'Local Zones, Wavelength, Outposts.', 'Special latency/residency needs.', 'Opt in deliberately.'),
    ('Global services', 'IAM, Route 53, CloudFront, Organizations.', 'Not tied to one Region.', 'Billing data in us-east-1.')])

DEEP = ('  <h3>How to choose a Region — a four-question test</h3>\n' + table(['Question', 'Why', 'For TiffinGo'], [
        ['1. Compliance: must data stay in a country?', 'laws such as DPDP, RBI rules, contracts', 'India → ap-south-1 or ap-south-2'], ['2. Proximity: where are the users?', 'latency', 'Mumbai, Pune, Delhi → ap-south-1'],
        ['3. Services: is everything I need available?', 'new services start in a few Regions', 'check the SSM list / Region table'], ['4. Price: what does it cost here?', 'prices vary by Region', 'compare in the Pricing Calculator']], minw=560) +
    '\n  <h3>Resilience ladder: how far should you go?</h3>\n' + table(['Design', 'Survives', 'Relative cost', 'Typical RTO'], [
        ['Single instance, one AZ', 'instance reboot', '1×', 'hours'], ['Multi-AZ (2–3 AZs)', 'data-centre / AZ failure', '~1.5–2×', 'seconds–minutes'],
        ['Backup to another Region', 'Region-wide event (restore)', '+ storage', 'hours'], ['Warm standby in second Region', 'Region-wide event', '~2×', 'minutes'], ['Active-active multi-Region', 'Region-wide event, near zero downtime', '2×+ and complex', 'near zero']], minw=560) +
    '\n  <p>Most business systems in India run multi-AZ in Mumbai with backups copied to Hyderabad — a good balance of cost and safety.</p>')

clouds = vendor_tabs('<p><b>AWS:</b> 39 Regions, 124 AZs; India: Mumbai, Hyderabad Regions, Delhi and Kolkata Local Zones.</p>',
    '<p><b>Azure:</b> Regions with availability zones in many (Central India has zones); paired Regions for DR; Azure Local/Arc for on-premises.</p>',
    '<p><b>Google Cloud:</b> Regions with zones (asia-south1 Mumbai, asia-south2 Delhi); global VPC network; Google Distributed Cloud for on-premises.</p>') + \
    cloud3([['Geographic area', 'Region', 'Region', 'Region'], ['Isolated location', 'Availability Zone', 'Availability zone', 'Zone'], ['On-premises extension', 'Outposts', 'Azure Local', 'Google Distributed Cloud'], ['CDN edge', 'CloudFront edge locations', 'Front Door / CDN PoPs', 'Cloud CDN edge']])

MOCKA.extend([
 mock('aws', ['EC2', 'Global View', 'Region explorer'], ['Global View', 'Region explorer', 'Global search'], 'Region explorer', [('Asia Pacific (Mumbai)', 'ap-south-1 · Enabled'), ('Asia Pacific (Hyderabad)', 'ap-south-2 · Disabled (opt-in)'), ('US East (N. Virginia)', 'us-east-1 · Enabled')], 'Refresh'),
 mock('aws', ['EC2', 'Settings', 'Zones'], ['Dashboard', 'Settings', 'Zones'], 'Zones', [('Availability Zones', 'ap-south-1a · aps1-az1 …'), ('Local Zones', 'ap-south-1-del-1 · Not opted in'), ('Action', '▾ Manage')], 'Update'),
 mock('aws', ['CloudShell'], ['Terminal', 'Actions'], 'Terminal', [('Command', 'curl -w "%{time_connect}" …'), ('Output', 'ap-south-1 0.004 · us-east-1 0.19')], 'Run'),
])

STEP1 = astep('1 · List Regions and see which are enabled',
    ['[[EC2]] → [[EC2 Global View]] → [[Region explorer]]: enabled Regions and resource counts.', 'Top-right Region menu: Regions shown in grey need opting in (Account → [[AWS Regions]]).'],
    "aws ec2 describe-regions --all-regions --query 'Regions[].[RegionName,OptInStatus]' --output table\naws ec2 describe-regions --all-regions --query 'length(Regions)'",
    'a table of every Region with <code>opt-in-not-required</code>, <code>opted-in</code> or <code>not-opted-in</code>, and the total count. Hyderabad (ap-south-2) is an opt-in Region.',
    'Regions launched after March 2019 are disabled until you opt in — a safety feature so nothing runs in a Region you did not choose.')

STEP2 = astep('2 · Map AZ names to AZ IDs, and find the Local Zones',
    ['[[EC2]] → [[Settings]] → [[Zones]]: see AZ names, AZ IDs and Local Zones with their opt-in status.', 'Optional (free): opt in to the Delhi Local Zone group.'],
    "aws ec2 describe-availability-zones --region ap-south-1 \\\n  --query 'AvailabilityZones[].[ZoneName,ZoneId,ZoneType,State]' --output table\naws ec2 describe-availability-zones --region ap-south-1 --all-availability-zones \\\n  --filters Name=zone-type,Values=local-zone --query 'AvailabilityZones[].[ZoneName,ZoneId,OptInStatus,ParentZoneId]' --output table\n# optional, free: enable the Delhi Local Zone group\naws ec2 modify-availability-zone-group --region ap-south-1 --group-name ap-south-1-del-1 --opt-in-status opted-in",
    'three AZs (<code>ap-south-1a/b/c</code>) with IDs like <code>aps1-az1</code>, then <code>ap-south-1-del-1a</code> (aps1-del1-az1) and <code>ap-south-1-ccu-1a</code> (aps1-ccu1-az1). Compare AZ IDs with a classmate: the same name may map to a different ID.',
    'AWS shuffles AZ names per account so that everybody choosing “a” does not crowd one building. AZ IDs are the real, shared identifiers.')

STEP3 = astep('3 · Measure latency to Regions yourself',
    ['Open [[CloudShell]] (Mumbai). Run the loop below, then run it again from your laptop terminal and compare.'],
    "for r in ap-south-1 ap-south-2 ap-southeast-1 me-central-1 eu-west-1 us-east-1; do\n  printf '%-15s ' $r\n  curl -s -o /dev/null -w '%{time_connect}s\\n' https://ec2.$r.amazonaws.com/\ndone",
    'TCP connect times in seconds: a few milliseconds to ap-south-1, tens of ms to Singapore and the Gulf, 100+ ms to Ireland and N. Virginia. From your laptop, add your ISP’s delay.',
    'Light in fibre needs about 5 ms per 1,000 km one way — distance is the floor no technology removes. That is why Region choice and edge caching matter.')

prac = practical(AWS_INTRO + ' This lab only reads information (and optionally opts in to a Local Zone, which is free). Cost: zero.', [AWS_SETUP, STEP1, STEP2, STEP3],
    cleanup='Nothing to delete. If you opted in to the Delhi Local Zone and want to undo it: <code>aws ec2 modify-availability-zone-group --region ap-south-1 --group-name ap-south-1-del-1 --opt-in-status not-opted-in</code> (allowed only when nothing is running there).')

mist = mistakes([
    ['Calling one instance “highly available”.', 'It is running, so it feels available.', 'At least two instances in two AZs behind a load balancer.'],
    ['Assuming ap-south-1a is the same building for everyone.', 'Same name.', 'Use AZ IDs (aps1-az1) across accounts.'],
    ['Choosing us-east-1 by default.', 'Tutorials use it.', 'Choose by users and law — usually ap-south-1 for India.'],
    ['Thinking edge locations run servers.', 'They are “AWS sites”.', 'They cache content and run DNS/edge functions only.'],
    ['Multi-Region for everything.', 'More = safer.', 'Multi-AZ + cross-Region backups is enough for most; active-active costs 2×+.'],
    ['Ignoring inter-AZ data cost.', 'Same Region feels free.', 'Inter-AZ traffic is charged per GB in each direction; keep chatty parts together or cache.']])

cert = table(['Exam / syllabus', 'What is asked'], [['AWS CLF-C02', 'Regions, AZs, edge locations; choosing a Region; Local Zones, Wavelength, Outposts (Domain 3); high availability = multi-AZ.'], ['SAA-C03', 'Multi-AZ vs multi-Region designs, DR strategies, AZ IDs in shared VPCs.'], ['C-DAC PGCP-BDA', 'Cloud infrastructure and data centres; availability.']], minw=560) + \
    '\n  <h3>Try exam-style questions</h3>\n' + qx('A company must keep data in India and serve Indian users with low latency. Best Region?', ['us-east-1', 'ap-south-1', 'eu-west-1', 'any edge location'], 1, 'Compliance + proximity.') + \
    qx('Which provides high availability for a web app?', ['larger instance', 'instances in multiple Availability Zones behind a load balancer', 'one instance with a static IP', 'an edge location'], 1, 'Multi-AZ.') + \
    qx('Which runs AWS infrastructure in your own data centre?', ['Local Zones', 'Wavelength', 'Outposts', 'CloudFront'], 2, 'Outposts.') + \
    qx('Which extends AWS into 5G networks for mobile low latency?', ['Wavelength Zones', 'Local Zones', 'Regions', 'Snowball'], 0, '5G → Wavelength.')

sys.path.insert(0, HERE)
from deep_v3 import HOOD, ROLES, DOMAINS, PRO, PROJ, SIM, NEWBIE, LADDER

assemble_v2(HERE, story_h2='1:10 pm, one data centre goes dark', hook_html=hk,
    narration='At lunch time one Mumbai data centre lost power. TiffinGo, spread over two Availability Zones, kept taking orders; a competitor in a single AZ was down for two hours.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='AWS global infrastructure',
    formal='The <b>AWS global infrastructure</b> is the worldwide physical foundation of AWS: geographically separate <b>Regions</b>, each made of multiple isolated, interconnected <b>Availability Zones</b> built from one or more data centres; extended by <b>Local Zones</b>, <b>Wavelength Zones</b> and <b>Outposts</b>; and complemented by <b>edge locations</b> for content delivery and DNS — enabling customers to choose where data resides and to design for high availability and low latency.',
    simple='AWS has data-centre groups (AZs) in many cities (Regions). Put your app in more than one AZ to survive failures, pick the Region for your users and laws, and use edge locations to deliver content fast.',
    interview=['“A Region is a geographic area like Mumbai with at least three isolated Availability Zones; I deploy across AZs for high availability and copy backups to a second Region for disaster recovery.”', '“Edge locations run CloudFront and Route 53 near users; Local Zones such as Delhi extend Mumbai for single-digit-millisecond latency; Outposts bring AWS on-premises.”'],
    terms_rows=[('Region', 'Geographic area, e.g. ap-south-1.'), ('Availability Zone', 'Isolated data centres in a Region.'), ('AZ ID', 'Stable ID, e.g. aps1-az1.'), ('Local Zone', 'Region extension in a city.'), ('Wavelength Zone', 'AWS inside 5G networks.'), ('Outposts', 'AWS racks on-premises.'), ('Edge location', 'CDN/DNS site near users.'), ('Opt-in Region', 'Disabled until you enable it.')],
    exam='CLF-C02 Domain 3 always has questions on Regions vs AZs vs edge locations, choosing a Region, and which extension fits a scenario.',
    picture_h2='From the planet to one data centre', picture_html=NEWBIE + picture,
    after_picture=[('types', 'Types, one by one', 'Seven building blocks, one by one', TYPES)],
    how_h2='An Availability Zone fails — what happens', how_intro='TiffinGo’s outage, step by step.', how_anim=SOLVE,
    parts_h2='Six parts of designing with global infrastructure', parts_html=parts, lv='',
    myth_rows=[('AWS never fails.', 'AZs can fail; design decides whether you survive.', 'Story.'), ('ap-south-1a is the same everywhere.', 'Names are mapped per account; IDs are not.', 'Type 2.'), ('More Regions is always better.', 'Multi-AZ + cross-Region backups suit most.', 'Deep dive.')],
    extra_secs=[('ladder', 'Learn at your level', 'From curious beginner to expert — pick your level', LADDER), ('deep', 'Deep dive', 'Choosing a Region, the resilience ladder', DEEP), ('hood', 'Under the hood', 'AZ ID mapping, network latency, partitions, global vs regional, data-transfer paths', HOOD), ('roles', 'By role', 'How developers, data, ML, DevOps and security people use it', ROLES), ('domains', 'By domain', 'Banking, healthcare, retail, education, IoT, media, government', DOMAINS), ('pro', 'For working professionals', 'Quotas, costs, errors, cheat sheet, checklist', PRO)],
    clouds_html=clouds, practical_html=prac + '\n  <h3 id="simulator">Practice without an account: simulator</h3>\n  <p>Explore Regions, AZ IDs and Local Zones here first — the map lights up as you go.</p>\n' + SIM, mistakes_html=mist, cert_html=cert, project_html=PROJ,
    can_now=['Explain Regions, AZs, data centres and the four extensions.', 'Choose a Region with the four-question test.', 'Design for an AZ failure and explain what happens.', 'Map AZ names to AZ IDs and find Local Zones.', 'Measure latency to Regions yourself.'],
    next_html='<a href="../04-aws-management-console-and-cli/">1.4 AWS Management Console and CLI</a>.',
    pre='<b>Before you start:</b> Lessons 1.1 and 1.2 (account with an admin user and budget).')
