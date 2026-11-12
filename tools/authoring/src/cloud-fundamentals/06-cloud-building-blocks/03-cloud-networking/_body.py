import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)


hk = hook('A customer in Pune taps “Order”. Before the order reaches TiffinGo’s database, it passes through at least six cloud networking services. Can you name them?',
    'DNS finds the address, a CDN edge answers what it can, the request enters a <b>virtual network</b> through a gateway, a <b>load balancer</b> picks a healthy server, <b>firewall rules</b> decide what may pass, <b>route tables</b> send packets between subnets — and a private link or VPN connects the office. This lesson explains each building block, follows one request through all of them, and walks you through building a network with public and private subnets, firewall rules, private DNS and peering on <b>your own</b> AWS, Azure or Google Cloud account.',
    ['Seven networking building blocks, and how a request travels through them.', 'Why a Google VPC is global but an AWS VPC is regional.', 'Public vs private subnets — the most-asked networking interview question.'])

def story_scene():
    o = t(180, 12, 'One tap, six hops', 9, 'ink', bold=True)
    hops = [('DNS', 'violet'), ('CDN', 'green'), ('Gateway', 'blue'), ('Load bal.', 'amber'), ('Firewall', 'red'), ('App · DB', 'blue')]
    for i, (n, tn) in enumerate(hops):
        x = 6 + i * 59
        o += box(x, 34, 52, 44, tn, rx=6) + t(x + 26, 60, n, 7, 'ink', bold=True)
        if i < 5: o += arrow(x + 53, 56, x + 58, 56)
    o += t(180, 104, 'Each hop is a cloud networking service you configure.', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Six boxes in a row: DNS, CDN, gateway, load balancer, firewall, application and database — the path of one order.', story_scene(), 'Networking is the <tspan font-weight="700" class="s-acc">road system</tspan> of the cloud.', h=124)
dialogue = '''R> Sir, our database got a login attempt from Russia last night! How could they even reach it?
A> Because it sits in a public subnet with port 5432 open to 0.0.0.0/0. Anyone on the internet can knock.
K> So we close the port?
A> Better: move the database into a private subnet with no route from the internet, and let only the app servers’ security group talk to it.
R> But then how does the database download updates?
A> Through a NAT gateway — out yes, in no. Let’s learn the building blocks: networks, subnets, routes, firewalls, load balancers, DNS, CDN and hybrid links.'''

# ------------------------------------------------------------------ picture
def vpcfig():
    o = t(320, 16, 'A standard cloud network: one VPC, two AZs, public and private subnets', 10.5, 'ink', bold=True)
    o += box(150, 26, 476, 214, 'card', rx=10) + t(388, 40, 'VPC tiffingo · 10.0.0.0/16 · Region ap-south-1 (Mumbai)', 8, 'ink', bold=True)
    o += box(14, 104, 90, 40, 'green', rx=6) + t(59, 121, 'Internet', 8, 'ink', bold=True) + t(59, 135, 'customers', 6.8, 'ink2')
    o += box(122, 108, 52, 32, 'blue', rx=6) + t(148, 128, 'IGW', 7.6, 'ink', bold=True) + arrow(104, 124, 120, 124)
    for i, az in enumerate(['ap-south-1a', 'ap-south-1b']):
        x = 190 + i * 216
        o += box(x, 50, 204, 182, 'card', rx=8) + t(x + 102, 64, 'AZ ' + az, 7.4, 'ink2', bold=True)
        o += box(x + 8, 72, 188, 64, 'green', rx=6) + t(x + 102, 86, f'public subnet 10.0.{i + 1}.0/24', 7.2, 'ink', bold=True)
        o += box(x + 16, 94, 80, 30, 'amber', rx=4) + t(x + 56, 113, 'ALB node', 7, 'ink') + box(x + 106, 94, 80, 30, 'violet', rx=4) + t(x + 146, 113, 'NAT gw', 7, 'ink')
        o += box(x + 8, 146, 188, 78, 'blue', rx=6) + t(x + 102, 160, f'private subnet 10.0.{i + 11}.0/24', 7.2, 'ink', bold=True)
        o += box(x + 16, 170, 80, 44, 'card', rx=4) + t(x + 56, 196, 'app VM', 7, 'ink') + cyl(x + 112, 168, 64, 46, 'DB' if i == 0 else 'DB standby', 'card')
    o += arrow(176, 124, 196, 108)
    o += t(320, 256, 'Public subnet = its route table sends 0.0.0.0/0 to the internet gateway. Private subnet = no such route (outbound only via NAT).', 7.4, 'ink2')
    return o
VPCF = bigfig('A VPC 10.0.0.0/16 in Mumbai with an internet gateway; two availability zones, each with a public subnet holding a load balancer node and NAT gateway, and a private subnet holding an app VM and a database.', vpcfig(), h=266)

def layersfig():
    o = t(320, 16, 'Where each building block works', 11, 'ink', bold=True)
    rows = [('Global / edge', 'DNS · CDN · global load balancer · DDoS protection', 'violet'), ('Region', 'virtual network (VPC/VNet) · regional load balancer · peering · VPN / private link', 'blue'),
            ('Availability Zone', 'subnet (AWS) · NAT gateway · load balancer node', 'green'), ('Network interface', 'private IP · public IP · security group / NSG / firewall tags', 'amber')]
    for i, (n, d, tn) in enumerate(rows):
        y = 32 + i * 46
        o += box(20 + i * 20, y, 600 - i * 40, 38, tn, rx=6) + t(110 + i * 20, y + 23, n, 8.4, 'ink', bold=True) + t(400, y + 23, d, 7.6, 'ink')
    o += t(320, 232, 'Note: a Google Cloud VPC is global (subnets are regional); an Azure VNet is regional and its subnets span zones.', 7.6, 'ink2')
    return o
LAYERS = bigfig('Four nested bands: global edge with DNS, CDN, global load balancing; Region with virtual networks, regional load balancers, peering and VPN; availability zone with subnets and NAT gateways; network interface with IPs and security groups.', layersfig(), h=242)

picture = ('  <p>Almost every production cloud app uses this shape — learn it once and you can read any architecture diagram:</p>\n' + VPCF +
           '\n  <p>And where each networking service “lives”:</p>\n' + LAYERS)

# ------------------------------------------------------------------ how: one request
RN = {'u': (4, 54, 54, 50, 'phone', 'Customer', 'Pune'), 'dns': (66, 4, 60, 46, 'dns', 'DNS', 'Route 53'), 'cdn': (66, 104, 60, 46, 'globe', 'CDN edge', 'Mumbai PoP'),
      'lb': (138, 54, 62, 50, 'lb', 'Load bal.', 'public subnet'), 'sg': (212, 4, 64, 46, 'shield', 'Security grp', 'port 8080'), 'app': (212, 104, 64, 46, 'server', 'App', 'private subnet'), 'db': (290, 54, 66, 50, 'db', 'Database', 'private subnet')}
RS = [dict(on=['u', 'dns'], hot='dns', move=(58, 70, 70, 40, 'query'), head='Step 1 · DNS: name → address', text='The phone asks “what is api.tiffingo.in?”. Route 53 answers with the CDN/load', text2='balancer address (an alias record), cached for the TTL.', svc='Route 53 · Azure DNS · Cloud DNS'),
      dict(on=['u', 'dns', 'cdn'], hot='cdn', move=(28, 104, 66, 128, 'HTTPS'), head='Step 2 · The nearest edge terminates TLS', text='The request reaches the closest CDN edge; cached images return from there.', text2='API calls continue to the origin over AWS’s backbone.', svc='CloudFront · Front Door · Cloud CDN (+ WAF, DDoS protection)'),
      dict(on=['u', 'dns', 'cdn', 'lb'], hot='lb', move=(126, 127, 150, 90, 'forward'), head='Step 3 · Into the VPC, to the load balancer', text='Through the internet gateway to the ALB in the public subnets. The ALB picks', text2='a healthy target and applies routing rules (path /orders → order service).', svc='ALB · Application Gateway · Application Load Balancer (GCP)'),
      dict(on=['u', 'dns', 'cdn', 'lb', 'sg'], hot='sg', move=(200, 70, 222, 40, 'check'), head='Step 4 · Firewall rules at the instance', text='The app’s security group allows port 8080 only from the ALB’s security group —', text2='nothing else on the internet can reach the app servers.', svc='Security groups · NSGs · VPC firewall rules (stateful)'),
      dict(on=['u', 'dns', 'cdn', 'lb', 'sg', 'app'], hot='app', move=(244, 50, 244, 104, 'route'), head='Step 5 · Route table delivers the packet', text='Inside the VPC the “local” route carries traffic between subnets; the app in a', text2='private subnet receives the request. Outbound internet only via NAT.', svc='Route tables · system routes · Cloud Router'),
      dict(on=list(RN), hot='db', move=(276, 127, 298, 90, 'SQL'), head='Step 6 · App to database, then all the way back', text='The DB’s security group accepts 5432 only from the app SG. The response returns', text2='along the same path — stateful firewalls allow the replies automatically.', svc='Private subnets + SG references = defence in depth')]
REQ = flow_anim('One order, through every networking building block', 'Follow a single HTTPS request from a phone in Pune to the database — and back.', 'Request path', 'Animation: DNS lookup; CDN edge; load balancer in a public subnet; security group check; route to app in private subnet; app queries the database.', RN, RS, hid='netflow')

# ------------------------------------------------------------------ types
def mapfig():
    o = t(320, 16, 'Seven networking building blocks', 11, 'ink', bold=True)
    items = [('1', 'Virtual network & subnets', 'VPC · VNet · VPC (global)', 'blue'), ('2', 'Routing & gateways', 'route tables, IGW, NAT', 'green'), ('3', 'Firewalls', 'SG/NACL · NSG · firewall rules', 'red'),
             ('4', 'Load balancers', 'ALB/NLB · LB/App GW · Cloud LB', 'amber'), ('5', 'DNS', 'Route 53 · Azure DNS · Cloud DNS', 'violet'), ('6', 'CDN & edge', 'CloudFront · Front Door · Cloud CDN', 'green'), ('7', 'Hybrid & private links', 'VPN, Direct Connect, peering', 'blue')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 7.6, 'ink', bold=True) + t(x + 78, y + 54, b, 6.2, 'ink2')
    o += t(320, 210, '1–3 build and protect the network · 4–6 bring users in · 7 connects networks to each other and to your offices.', 7.6, 'ink2')
    return o
MAP = bigfig('Map of seven networking building blocks: 1 virtual network and subnets, 2 routing and gateways, 3 firewalls, 4 load balancers, 5 DNS, 6 CDN and edge, 7 hybrid connectivity and private links.', mapfig(), h=222)

def a_vnet(k):
    o = t(180, 12, ['Pick an address range', 'Cut it into subnets', 'Resources get private IPs'][k], 9, 'ink', bold=True)
    o += box(14, 28, 332, 104, 'blue' if k == 0 else 'card', rx=10) + t(180, 42, 'VPC 10.0.0.0/16 = 65,536 addresses (yours only)', 7.6, 'ink', bold=True)
    if k >= 1:
        for i, (n, tn) in enumerate([('10.0.1.0/24 public · 1a', 'green'), ('10.0.2.0/24 public · 1b', 'green'), ('10.0.11.0/24 private · 1a', 'blue'), ('10.0.12.0/24 private · 1b', 'blue')]):
            x = 22 + (i % 2) * 162; y = 52 + (i // 2) * 38
            o += box(x, y, 154, 32, tn, rx=5) + t(x + 77, y + 14, n, 6.8, 'ink', bold=True)
            if k == 2: o += t(x + 77, y + 26, ['ALB 10.0.1.25', 'NAT 10.0.2.9', 'app 10.0.11.40', 'DB 10.0.12.7'][i], 6.4, 'ink2', mono=True)
    o += t(180, 150, ['a private IP range (RFC 1918) that no other customer can see', '/24 = 256 addresses; AWS reserves 5 in every subnet', 'each network interface gets an address from its subnet'][k], 7.2, 'ink', bold=True)
    return o
A_VNET = cap([a_vnet(k) for k in range(3)], [('Address range', 'A virtual network gets a private CIDR block such as 10.0.0.0/16.', ''), ('Subnets', 'It is cut into smaller ranges — public and private, one per AZ (AWS).', ''), ('Private IPs', 'Every VM, load balancer node or database gets an IP from its subnet.', '')],
    'A virtual network in action', 'Your own private address space in the cloud.', 'Virtual network', 'Animation: a VPC with 10.0.0.0/16; split into public and private subnets in two AZs; resources receive private IPs.', 'n1anim')
T1 = vtype(1, 'Virtual networks and subnets (VPC / VNet)', 'blue',
    'A <b>virtual network</b> — Amazon VPC, Azure Virtual Network (VNet), Google Cloud VPC — is a logically isolated, software-defined private network in the cloud with its own IP address range (CIDR), divided into <b>subnets</b> in which resources receive private IP addresses; it is built on the provider’s overlay network (Lesson 4.3), so many customers can use the same address ranges without seeing each other.',
    'A gated housing society: the society has its own address range (Block A–D, flat numbers), outsiders cannot walk in, and each wing (subnet) has its own entrance rules.',
    'TiffinGo’s VPC <code>10.0.0.0/16</code> in Mumbai has public subnets <code>10.0.1.0/24</code> and <code>10.0.2.0/24</code> (load balancer, NAT) and private subnets <code>10.0.11.0/24</code> and <code>10.0.12.0/24</code> (app servers, database) across two AZs.',
    'Amazon VPC (regional, subnets per AZ), Azure Virtual Network (regional, subnets span zones), Google Cloud VPC (global, subnets per Region).',
    '', A_VNET,
    'always — every IaaS design starts with a network plan: CIDR sizes, subnets per tier and per AZ, room to grow, no overlap with offices.',
    'you pick a tiny or overlapping range (e.g. 192.168.1.0/24, same as the office) — peering and VPNs will fail later.',
    plain='Your own private network inside the cloud, with your own address numbers. You split it into smaller zones (subnets) for different kinds of servers.',
    how=[('Choose a CIDR', 'E.g. 10.0.0.0/16 (65,536 addresses) from the private ranges 10/8, 172.16/12, 192.168/16.'), ('Create subnets', 'Smaller CIDRs per tier and AZ, e.g. /24 (256 addresses; AWS reserves 5).'), ('Overlay', 'The provider encapsulates your packets so your 10.0.x.x never clashes with another customer’s.'), ('Attach resources', 'Network interfaces get private IPs; public IPs are optional extras.'), ('Default network', 'New accounts have a default VPC/network — fine for labs, not for production.')],
    words=[('CIDR', 'a way to write an IP range, e.g. 10.0.0.0/16'), ('subnet', 'a smaller slice of the network'), ('private IP', 'an address only reachable inside the network'), ('overlay', 'a virtual network running on top of the physical one')],
    diff=table(['', 'AWS VPC', 'Azure VNet', 'Google Cloud VPC'], [['Scope', 'one Region', 'one Region', 'global'], ['Subnet scope', 'one AZ', 'whole Region (all zones)', 'one Region (all zones)'], ['Default firewall', 'security groups (per NIC)', 'NSG (subnet or NIC)', 'firewall rules (network, by tag/SA)']], minw=560),
    where=['Every VM, database, container cluster and private endpoint', 'Separating environments (prod, test)', 'Isolating tenants or departments'],
    realworld='Amazon VPC became the default for all new EC2 accounts in 2013 (“EC2-Classic” put all customers on one flat network and was fully retired in 2023); today every EC2 instance must live in a VPC.',
    pro='Plan CIDRs like real estate: Kubernetes pods (EKS VPC CNI) take one VPC IP per pod, so a /24 subnet can run out after a handful of nodes. Many outages of “no IP addresses available” are design-time mistakes, not traffic spikes.')

def a_rt(k):
    o = t(180, 12, ['Route table of the public subnet', 'Private subnet: out via NAT only', 'Inbound from internet to private: no route'][k], 9, 'ink', bold=True)
    rows = [[('10.0.0.0/16', 'local'), ('0.0.0.0/0', 'igw-…  (internet gateway)')], [('10.0.0.0/16', 'local'), ('0.0.0.0/0', 'nat-…  (NAT gateway)')], [('10.0.0.0/16', 'local'), ('0.0.0.0/0', 'nat-…  (outbound only)')]][k]
    o += box(20, 30, 200, 70, 'card', rx=6) + t(70, 44, 'Destination', 7, 'ink2', bold=True) + t(160, 44, 'Target', 7, 'ink2', bold=True)
    for i, (d, tg) in enumerate(rows): o += t(70, 64 + i * 20, d, 7.2, 'ink', mono=True) + t(160, 64 + i * 20, tg, 6.8, 'ink', mono=True)
    o += box(236, 30, 110, 70, ['green', 'blue', 'red'][k], rx=8) + t(291, 58, ['public', 'private', 'internet →'][k], 8, 'ink', bold=True) + t(291, 76, ['in + out', 'out only', 'private: blocked'][k], 7, 'ink')
    o += t(180, 124, ['a subnet is “public” only because of this 0.0.0.0/0 → IGW route', 'servers can download updates; nobody outside can start a connection', 'no route + no public IP = unreachable from the internet'][k], 7.2, 'ink', bold=True)
    return o
A_RT = cap([a_rt(k) for k in range(3)], [('Public subnet', 'Its route table sends 0.0.0.0/0 (everything else) to the internet gateway.', ''), ('Private subnet', 'Its default route points to a NAT gateway: outbound connections work.', ''), ('No way in', 'There is no inbound path from the internet to private subnets.', '')],
    'Routing in action', 'Route tables make a subnet public or private.', 'Routing', 'Animation: public subnet route table with 0.0.0.0/0 to an internet gateway; private subnet route to a NAT gateway; inbound internet traffic to private subnets has no route.', 'n2anim')
T2 = vtype(2, 'Routing and gateways (route tables, internet gateway, NAT)', 'green',
    '<b>Route tables</b> decide where packets leaving a subnet go, using rules of the form <i>destination CIDR → target</i>; <b>gateways</b> are the targets that connect the virtual network to other places — an <b>internet gateway</b> for two-way internet access with public IPs, a <b>NAT gateway</b> for outbound-only internet access from private IPs, and VPN/transit gateways for other networks.',
    'Signboards at a society gate: “Blocks A–D → inside”, “everything else → main road”. The service lane for deliveries (NAT) lets staff go out shopping but no stranger can drive in through it.',
    'TiffinGo’s app servers in private subnets download OS patches through a NAT gateway; customers reach only the load balancer in the public subnets. The database subnet has no route to the internet at all.',
    'AWS route tables, internet gateway, NAT gateway, egress-only IGW (IPv6), Transit Gateway; Azure system routes and user-defined routes (UDR), NAT Gateway; Google Cloud routes, Cloud Router, Cloud NAT.',
    '', A_RT,
    'designing public/private tiers, forcing traffic through a firewall appliance, or connecting networks.',
    'you give private servers public IPs “to make updates work” — use NAT or private endpoints instead.',
    plain='Signposts inside the cloud network that say where each kind of traffic should go — to another server inside, out to the internet, or out through a one-way exit.',
    how=[('Local route', 'Every route table has the VPC range → local (traffic between subnets just works).'), ('Default route', '0.0.0.0/0 → IGW (public) or → NAT (private), or nothing (isolated).'), ('Longest prefix wins', 'A /24 rule beats a /16 rule beats 0.0.0.0/0.'), ('NAT', 'Replaces private source IPs with the NAT’s public IP; replies are mapped back.'), ('Association', 'Each subnet uses exactly one route table.')],
    words=[('route table', 'a list of “destination → where to send it” rules'), ('internet gateway', 'the door between a VPC and the internet'), ('NAT', 'network address translation — many private IPs share one public IP for outbound traffic'), ('0.0.0.0/0', '“any address” — the default route')],
    diff=table(['', 'Internet gateway', 'NAT gateway', 'No gateway'], [['Inbound from internet', 'yes (with public IP)', 'no', 'no'], ['Outbound to internet', 'yes', 'yes', 'no'], ['Cost', 'free', 'per hour + per GB', '—'], ['Typical subnet', 'public', 'private', 'isolated / database']], minw=520),
    where=['Public vs private tiers', 'Central egress through a firewall (UDR / TGW)', 'Isolated database subnets'],
    realworld='A NAT gateway is billed per hour <b>and per GB processed</b> — a classic surprise bill is private servers pulling large data from S3 through NAT. A free <b>S3 gateway endpoint</b> adds a route that sends S3 traffic privately and skips NAT charges.',
    pro='Since February 2024 AWS charges for every public IPv4 address ($0.005/hour, including those on instances) — one more reason for private subnets behind NAT, load balancers, or IPv6.')

def a_fw(k):
    o = t(180, 12, ['Security group: allow-list per server', 'Stateful: replies come back', 'NACL / subnet rules: allow and deny'][k], 9, 'ink', bold=True)
    o += box(230, 40, 116, 70, 'blue', rx=8) + t(288, 64, 'app VM', 8, 'ink', bold=True) + t(288, 82, 'SG: app-sg', 7, 'ink2')
    o += box(14, 30, 120, 30, 'amber', rx=5) + t(74, 49, 'ALB (alb-sg)', 7.2, 'ink') + box(14, 70, 120, 30, 'red', rx=5) + t(74, 89, 'internet 1.2.3.4', 7.2, 'ink')
    if k == 0:
        o += arrow(136, 45, 228, 60) + t(182, 44, '8080 ✔', 7, 'green', bold=True) + arrow(136, 85, 228, 90) + t(182, 100, '22 ✘', 7, 'red', bold=True)
    elif k == 1:
        o += arrow(136, 45, 228, 60) + arrow(228, 72, 136, 56) + t(182, 74, 'reply allowed automatically', 6.6, 'green', bold=True)
    else:
        o += box(160, 26, 50, 100, 'violet', rx=4) + t(185, 64, 'NACL', 7, 'ink', bold=True) + t(185, 80, 'deny', 6.6, 'red') + t(185, 92, '1.2.3.4', 6.4, 'ink')
    o += t(180, 140, ['only listed sources/ports are allowed; everything else is denied', 'return traffic of an allowed connection is always allowed', 'stateless subnet rules in number order — can block an attacker’s IP'][k], 7.2, 'ink', bold=True)
    return o
A_FW = cap([a_fw(k) for k in range(3)], [('Allow-list', 'A security group allows port 8080 only from the ALB’s security group; SSH from', 'the internet is not listed, so it is denied.'), ('Stateful', 'Replies to allowed requests are allowed back automatically.', ''), ('Subnet layer', 'Network ACLs (AWS) are stateless, ordered allow/deny rules at the subnet edge.', '')],
    'Cloud firewalls in action', 'Allow-lists at every network interface.', 'Firewall', 'Animation: security group allows 8080 from the load balancer and denies SSH from the internet; replies flow back; a network ACL denies one IP at the subnet.', 'n3anim')
T3 = vtype(3, 'Cloud firewalls (security groups, NSGs, firewall rules)', 'red',
    '<b>Cloud firewalls</b> filter traffic by protocol, port and source/destination: AWS <b>security groups</b> (stateful, allow-only, per network interface) and <b>network ACLs</b> (stateless, ordered allow/deny, per subnet), Azure <b>network security groups</b> (stateful, priority-ordered allow/deny, per subnet or NIC), and Google Cloud <b>VPC firewall rules and policies</b> (stateful, applied by network tags or service accounts).',
    'Security guards with a guest list at each flat door (security group) plus a gate guard for the whole wing (NACL/NSG): only listed visitors enter, and residents’ visitors may always leave.',
    'TiffinGo’s rules: ALB allows 443 from anywhere; app servers allow 8080 only from the ALB’s security group; the database allows 5432 only from the app security group. The Russian login attempt can no longer even reach the database.',
    'AWS security groups, network ACLs, AWS Network Firewall, AWS WAF; Azure NSGs, application security groups, Azure Firewall, WAF; Google Cloud VPC firewall rules, hierarchical firewall policies, Cloud NGFW, Cloud Armor.',
    '', A_FW,
    'always — every interface should have the tightest rules possible, referencing other groups rather than IP ranges.',
    'you open 0.0.0.0/0 to admin ports (22, 3389) or databases — one of the most common causes of cloud breaches.',
    plain='Rules that say which kinds of traffic may reach each server. Everything not on the list is blocked.',
    how=[('Default deny inbound', 'New security groups allow no inbound traffic and all outbound.'), ('Add allow rules', 'Protocol + port + source (CIDR, or another security group / tag).'), ('Stateful tracking', 'The connection is remembered; replies pass automatically.'), ('Evaluation', 'All SG rules are combined (any allow wins); NACL/NSG rules are checked in priority order.'), ('Logging', 'VPC Flow Logs / NSG flow logs / firewall logging show accepted and rejected traffic.')],
    words=[('port', 'a numbered door for a service, e.g. 443 for HTTPS'), ('stateful', 'remembers connections, so replies are allowed'), ('stateless', 'checks every packet on its own, both directions'), ('allow-list', 'only listed things are allowed')],
    diff=table(['', 'AWS security group', 'AWS network ACL', 'Azure NSG', 'GCP firewall rule'], [['Attached to', 'network interface', 'subnet', 'subnet or NIC', 'whole network, by tag/SA'], ['Stateful', 'yes', 'no', 'yes', 'yes'], ['Deny rules', 'no (allow only)', 'yes', 'yes', 'yes'], ['Order', 'all evaluated', 'by rule number', 'by priority', 'by priority']], minw=640),
    where=['Every VM, database, load balancer and endpoint', 'Tier separation (web → app → db)', 'Blocking known bad IPs (NACL / NSG / Cloud Armor)'],
    realworld='Shodan-style internet scanners find newly exposed databases within minutes; many large data leaks (open Elasticsearch, MongoDB, Redis) involved a database port open to 0.0.0.0/0 — a firewall rule, not a sophisticated hack.',
    pro='Referencing a security group as the source (“allow from alb-sg”) is better than IP ranges: when the load balancer’s IPs change or scale out, the rule still matches exactly the right interfaces — and nothing else.')

def a_lb(k):
    o = t(180, 12, ['One address in front', 'Health checks', 'Layer 7 rules'][k], 9, 'ink', bold=True)
    o += box(14, 54, 70, 40, 'green', rx=6) + t(49, 78, 'clients', 7.4, 'ink') + arrow(86, 74, 116, 74)
    o += box(118, 44, 90, 60, 'amber', rx=8) + t(163, 70, 'load balancer', 7.4, 'ink', bold=True) + t(163, 86, ['one DNS name', 'checks /health', '/orders · /menu'][k], 6.6, 'ink2')
    for i in range(3):
        bad = k == 1 and i == 1
        o += box(250, 28 + i * 40, 96, 30, 'red' if bad else 'blue', rx=5) + t(298, 47 + i * 40, (['app 1', 'app 2 ✘', 'app 3'][i] if k == 1 else (['orders 1', 'orders 2', 'menu 1'][i] if k == 2 else f'app {i + 1}')), 7, 'ink')
        if not bad: o += arrow(210, 74, 248, 43 + i * 40)
    o += t(180, 150, ['spreads requests over healthy targets in several AZs', 'an unhealthy target stops receiving traffic until it recovers', 'routes by path, host or header; terminates TLS'][k], 7.2, 'ink', bold=True)
    return o
A_LB = cap([a_lb(k) for k in range(3)], [('Front door', 'Clients connect to one DNS name; the load balancer spreads requests.', ''), ('Health checks', 'Targets failing checks are removed from rotation automatically.', ''), ('Layer 7', 'Application load balancers route by URL path or host and handle HTTPS.', '')],
    'Load balancing in action', 'One address, many healthy servers.', 'Load balancer', 'Animation: clients reach one load balancer which spreads traffic; an unhealthy target is skipped; path-based routing sends /orders and /menu to different groups.', 'n4anim')
T4 = vtype(4, 'Load balancers', 'amber',
    'A <b>load balancer</b> is a managed service that receives client connections on one address and distributes them across healthy targets (VMs, containers, IPs, functions) in one or more zones, using health checks; <b>layer 4</b> balancers forward TCP/UDP connections, <b>layer 7</b> balancers understand HTTP(S) and route by path, host or headers.',
    'The token counter at a busy bank: you take a token at one desk, and it sends you to whichever cashier is free — skipping the cashier on lunch break.',
    'TiffinGo’s ALB terminates HTTPS with a free certificate, sends <code>/api/orders</code> to the order service and <code>/</code> to the web servers, and stops sending traffic to an instance whose <code>/health</code> fails — Auto Scaling replaces it (Lesson 5.3).',
    'AWS Elastic Load Balancing: Application LB (L7), Network LB (L4), Gateway LB; Azure Load Balancer (L4), Application Gateway (L7), Front Door (global L7), Traffic Manager (DNS); Google Cloud Load Balancing (global and regional, L4/L7).',
    '', A_LB,
    'more than one server serves the same app, or you need HTTPS termination, health-based failover or path routing.',
    'a single dev server is enough — a load balancer has an hourly cost even when idle.',
    plain='A traffic police officer for your app: all visitors come to one address, and it sends each one to a server that is free and healthy.',
    how=[('Listener', 'Port/protocol it accepts (e.g. HTTPS 443) with a TLS certificate.'), ('Rules', 'L7: path/host/header conditions → target group.'), ('Target group', 'Registered targets with a health check (path, interval, thresholds).'), ('Distribution', 'Round robin / least outstanding requests (L7) or flow hash (L4) across AZs.'), ('Scale', 'The provider scales load balancer nodes automatically; global LBs use anycast IPs.')],
    words=[('layer 4', 'works with TCP/UDP connections only'), ('layer 7', 'understands HTTP: URLs, headers, cookies'), ('health check', 'a regular test request to see if a server is OK'), ('TLS termination', 'decrypting HTTPS at the load balancer'), ('anycast', 'one IP address announced from many places — users reach the nearest one')],
    diff=table(['', 'L7 (ALB, App Gateway, App LB)', 'L4 (NLB, Azure LB, Network LB)', 'DNS-based (Traffic Manager, Route 53 policies)'], [['Understands', 'HTTP paths, hosts, headers', 'IP + port', 'only names'], ['Typical use', 'web apps, APIs', 'TCP/UDP, very high throughput, static IPs', 'global failover between Regions'], ['Sees client IP', 'in X-Forwarded-For', 'yes (preserved)', '—']], minw=620),
    where=['Every multi-server web app', 'Microservices behind one domain', 'Global failover'],
    realworld='Google Cloud’s global external Application Load Balancer gives one <b>anycast IP</b> for the whole world: users in Mumbai and São Paulo hit the same IP but enter Google’s network at their nearest edge — a design that comes from Google’s own front end (GFE) for Search and YouTube.',
    pro='An ALB has no fixed IP addresses — its IPs change as it scales — so DNS must point at it with an alias/CNAME. If a partner needs fixed IPs for an allow-list, put an NLB (static Elastic IPs) or AWS Global Accelerator in front.')

def a_dns(k):
    o = t(180, 12, ['Ask the resolver', 'Follow the delegation', 'Answer cached for the TTL'][k], 9, 'ink', bold=True)
    o += box(14, 54, 70, 40, 'green', rx=6) + t(49, 78, 'phone', 7.4, 'ink')
    o += box(108, 54, 80, 40, 'card', rx=6) + t(148, 72, 'resolver', 7.4, 'ink', bold=True) + t(148, 86, '(ISP / 8.8.8.8)', 6.4, 'ink2') + arrow(86, 74, 106, 74)
    for i, n in enumerate(['root .', '.in TLD', 'tiffingo.in (Route 53)']):
        on = k >= 1 or i == 2 and k == 2
        o += box(220, 26 + i * 40, 126, 32, ('violet' if i == 2 else 'card') if k >= 1 else 'card', rx=5) + t(283, 46 + i * 40, n, 7, 'ink')
        if k >= 1: o += arrow(190, 74, 218, 42 + i * 40)
    if k == 2: o += t(148, 112, 'api → 13.x.x.x · TTL 60 s', 6.8, 'ink', bold=True, mono=True)
    o += t(180, 146, ['“What is the IP of api.tiffingo.in?”', 'root → .in → the authoritative name servers of tiffingo.in', 'the answer is cached; the next query is instant'][k], 7.2, 'ink', bold=True)
    return o
A_DNS = cap([a_dns(k) for k in range(3)], [('Query', 'The device asks a recursive resolver for the name.', ''), ('Delegation', 'The resolver asks the root, then .in, then the domain’s authoritative servers', '(e.g. Route 53).'), ('Cache', 'The answer is cached for its TTL; lower TTLs make changes faster.', '')],
    'DNS in action', 'Names to addresses, with caching.', 'DNS', 'Animation: a phone asks a resolver; the resolver follows root, .in and the authoritative servers; the answer is cached for its TTL.', 'n5anim')
T5 = vtype(5, 'DNS (managed name service)', 'violet',
    '<b>DNS</b> (Domain Name System) translates names such as <code>api.tiffingo.in</code> into IP addresses; cloud DNS services host <b>authoritative</b> zones (public or private to a virtual network) on globally distributed name servers and add routing policies — weighted, latency-based, geolocation and health-check failover.',
    'The phone contacts app: you remember “Riya”, the phone remembers the number — and if Riya changes her number, you update one entry.',
    'TiffinGo’s domain is hosted in Route 53: <code>tiffingo.in</code> is an alias to CloudFront, <code>api</code> to the ALB, and a private zone <code>tiffingo.internal</code> gives the database a stable name inside the VPC. Failover routing points to Hyderabad if Mumbai’s health check fails.',
    'Amazon Route 53 (public/private hosted zones, Resolver), Azure DNS (public and private zones), Google Cloud DNS (public/private managed zones).',
    '', A_DNS,
    'every public app (your domain) and inside networks (private zones) so services find each other by name.',
    'you hard-code IP addresses in apps — they change when servers or load balancers are replaced.',
    plain='The internet’s phone book: you type a name, DNS finds the number (IP address) of the server.',
    how=[('Register a domain', 'With any registrar; point its name servers to the cloud DNS zone.'), ('Create records', 'A/AAAA (IP), CNAME (alias name), MX (mail), TXT (verification), alias records to cloud resources.'), ('Resolve', 'Resolvers walk root → TLD → authoritative servers and cache the answer.'), ('Routing policies', 'Weighted, latency, geo, failover using health checks.'), ('Private zones', 'Names that resolve only inside linked virtual networks.')],
    words=[('domain', 'a name you own, e.g. tiffingo.in'), ('record', 'one entry: name → value'), ('TTL', 'time to live — how long resolvers may cache an answer'), ('authoritative', 'the server that holds the official answer')],
    diff=table(['', 'Public zone', 'Private zone'], [['Who can resolve', 'the whole internet', 'only linked VPCs/VNets'], ['Typical records', 'www, api, MX', 'db.internal, services'], ['Needs a registered domain', 'yes', 'no']], minw=460),
    where=['Websites and APIs', 'Service discovery inside networks', 'Disaster-recovery failover between Regions'],
    realworld='Amazon Route 53 is one of the very few AWS services with a <b>100% availability SLA</b> — DNS is so critical that its name servers are spread over hundreds of edge locations with anycast.',
    pro='Lowering the TTL only helps if you do it <i>before</i> a change: resolvers keep the old answer for the old TTL. Teams lower TTLs to 60 s a day before a migration, then raise them again.')

def a_cdn(k):
    o = t(180, 12, ['First request: cache miss', 'Next requests: served from the edge', 'Edge also protects'][k], 9, 'ink', bold=True)
    o += box(14, 54, 70, 40, 'green', rx=6) + t(49, 72, 'users', 7.4, 'ink') + t(49, 86, 'India', 6.6, 'ink2')
    o += box(120, 44, 100, 60, 'violet', rx=8) + t(170, 68, 'edge PoP', 7.6, 'ink', bold=True) + t(170, 86, ['miss', 'HIT', 'WAF + DDoS'][k], 7, 'ink2', bold=True)
    o += box(262, 44, 84, 60, 'blue' if k == 0 else 'card', rx=8) + t(304, 70, 'origin', 7.6, 'ink', bold=True) + t(304, 86, 'S3 / ALB', 6.6, 'ink2')
    o += arrow(86, 74, 118, 74)
    if k == 0: o += arrow(222, 74, 260, 74)
    if k == 2: o += box(120, 112, 100, 22, 'red', rx=4) + t(170, 127, 'bad bots blocked', 6.6, 'ink')
    o += t(180, 150, ['the edge fetches the photo from the origin and keeps a copy', '15 ms instead of 150+ ms; the origin is not even touched', 'TLS, firewall rules and DDoS absorption at the edge'][k], 7.2, 'ink', bold=True)
    return o
A_CDN = cap([a_cdn(k) for k in range(3)], [('Cache miss', 'The first request for a file goes to the origin; the edge stores a copy.', ''), ('Cache hit', 'Later requests in that area are answered by the nearby edge.', ''), ('Protection', 'Edges also terminate TLS and filter attacks before they reach your servers.', '')],
    'CDN in action', 'Content close to users.', 'CDN', 'Animation: first request misses the edge cache and goes to the origin; later requests hit the edge; the edge also blocks attacks.', 'n6anim')
T6 = vtype(6, 'CDN and edge networking', 'green',
    'A <b>content delivery network (CDN)</b> caches and serves content from <b>edge locations</b> close to users, terminating TLS there and forwarding cache misses and dynamic requests to the <b>origin</b> over the provider’s backbone; edges also host web application firewalls, DDoS protection and small edge functions.',
    'Amul’s local milk booths: milk is not carried from Anand to every home each morning — it is stocked in nearby booths.',
    'TiffinGo puts CloudFront in front of the photo bucket and the ALB. In our real Lesson 5.1 test, a photo came back from the Mumbai edge <code>BOM78</code> with “Hit from cloudfront” in about 15 ms — and S3 transfer to CloudFront is free (Lesson 5.5).',
    'Amazon CloudFront, AWS WAF, AWS Shield, Global Accelerator; Azure Front Door, Azure CDN, Azure WAF, DDoS Protection; Google Cloud CDN, Media CDN, Cloud Armor.',
    'Edge locations were introduced in Lesson 5.1.', A_CDN,
    'users are spread out, content is cacheable (images, video, JS/CSS, downloads) or you need edge security.',
    'content is private per user and cannot be cached — you still gain TLS and protection, but less speed.',
    plain='Copies of your website’s pictures and files kept in many cities, so each user gets them from somewhere nearby — faster and cheaper.',
    how=[('Distribution', 'You create a distribution with one or more origins (S3, load balancer, any HTTPS server).'), ('Anycast/DNS', 'Users are routed to the nearest edge.'), ('Cache', 'Responses are cached by cache key (path, some headers) for the TTL.'), ('Miss', 'The edge (or regional cache) fetches from the origin over the backbone.'), ('Security', 'TLS, WAF rules, bot control and DDoS absorption at the edge.')],
    words=[('edge location / PoP', 'a data-centre site close to users'), ('origin', 'where the original content lives'), ('cache hit', 'answered from the stored copy'), ('WAF', 'web application firewall — blocks malicious HTTP requests')],
    diff=table(['', 'CDN', 'Load balancer', 'DNS'], [['Caches content', 'yes', 'no', 'answers only'], ['Location', 'edge, worldwide', 'Region (or global)', 'worldwide'], ['Main benefit', 'speed + offload + protection', 'spread load', 'find the address']], minw=480),
    where=['Images, video, downloads', 'Whole websites and APIs (dynamic acceleration)', 'DDoS and bot protection'],
    realworld='AWS states CloudFront has 750+ points of presence; Indian sites in Mumbai, Delhi, Chennai, Bengaluru, Hyderabad and Kolkata keep Indian users on short paths — the reason an image can load in 15 ms although the origin is far away.',
    pro='Every distinct cache key is a separate cache entry: forwarding all cookies or query strings to the origin can drop the hit ratio to near zero. A good cache policy forwards only what changes the response.')

def a_hyb(k):
    o = t(180, 12, ['Peering: two VPCs talk privately', 'VPN over the internet', 'Dedicated private line'][k], 9, 'ink', bold=True)
    if k == 0:
        o += box(20, 40, 120, 70, 'blue', rx=8) + t(80, 70, 'VPC prod', 8, 'ink', bold=True) + t(80, 88, '10.0.0.0/16', 7, 'ink', mono=True)
        o += box(220, 40, 120, 70, 'green', rx=8) + t(280, 70, 'VPC analytics', 8, 'ink', bold=True) + t(280, 88, '10.9.0.0/16', 7, 'ink', mono=True)
        o += arrow(142, 75, 218, 75) + arrow(218, 82, 142, 82) + t(180, 68, 'peering', 7, 'ink2')
    else:
        o += box(14, 40, 110, 70, 'card', rx=8) + t(69, 70, 'office / DC', 8, 'ink', bold=True) + t(69, 88, '192.168.0.0/16', 6.8, 'ink', mono=True)
        o += box(236, 40, 110, 70, 'blue', rx=8) + t(291, 70, 'VPC', 8, 'ink', bold=True) + t(291, 88, '10.0.0.0/16', 7, 'ink', mono=True)
        o += (f'<path d="M126,75 C160,40 200,110 234,75" style="fill:none;stroke:#E0A100;stroke-width:2;stroke-dasharray:5 3"/>' + t(180, 58, 'IPsec tunnel · internet', 7, 'amber', bold=True) if k == 1
              else f'<path d="M126,75 L234,75" style="stroke:#2E8B57;stroke-width:4"/>' + t(180, 66, 'Direct Connect · 1–100 Gbps', 7, 'green', bold=True))
    o += t(180, 136, ['private IPs, no internet, no overlap allowed; not transitive', 'encrypted, quick to set up, speed depends on the internet', 'private fibre via a partner — steady latency, big bandwidth'][k], 7.2, 'ink', bold=True)
    return o
A_HYB = cap([a_hyb(k) for k in range(3)], [('Peering', 'Two virtual networks exchange traffic over private IPs on the provider’s', 'backbone.'), ('Site-to-site VPN', 'An encrypted IPsec tunnel over the internet links an office to the VPC.', ''), ('Dedicated connection', 'A private physical link from your data centre or a partner location to the', 'cloud.')],
    'Hybrid connectivity in action', 'Connecting networks to each other and to offices.', 'Hybrid networking', 'Animation: two VPCs peered; an office linked by an IPsec VPN over the internet; a dedicated private connection.', 'n7anim')
T7 = vtype(7, 'Hybrid connectivity and private links', 'blue',
    '<b>Hybrid and inter-network connectivity</b> links virtual networks to each other and to on-premises sites: <b>peering</b> (private routing between two VNets/VPCs), <b>site-to-site VPN</b> (encrypted IPsec tunnels over the internet), <b>dedicated connections</b> (private circuits such as AWS Direct Connect, Azure ExpressRoute, Google Cloud Interconnect), <b>transit hubs</b> for many networks, and <b>private endpoints</b> that expose a service inside your network without public IPs.',
    'Roads between housing societies: a private gate between two neighbouring societies (peering), an armoured van on public roads (VPN), or your own private flyover (dedicated line).',
    'TiffinGo connects its central kitchen’s billing server to the AWS VPC with a site-to-site VPN; the analytics VPC is peered with production to read replicas; S3 is reached through a VPC endpoint so data never touches the internet.',
    'AWS VPC peering, Transit Gateway, Site-to-Site VPN, Client VPN, Direct Connect, PrivateLink/VPC endpoints, Cloud WAN; Azure VNet peering, Virtual WAN, VPN Gateway, ExpressRoute, Private Link; Google VPC Network Peering, Network Connectivity Center, Cloud VPN, Cloud Interconnect, Private Service Connect.',
    '', A_HYB,
    'offices or data centres must reach cloud resources privately, or several VPCs/accounts must talk to each other.',
    'address ranges overlap (plan CIDRs first) or you expect peering to be transitive (A↔B and B↔C does not give A↔C).',
    plain='Ways to connect your cloud network privately to another cloud network or to your office — through a secure tunnel over the internet or a dedicated cable.',
    how=[('Plan addresses', 'No overlapping CIDRs between networks you connect.'), ('Peering', 'Request + accept; add routes on both sides; traffic stays on the backbone.'), ('VPN', 'Customer gateway (your router) ↔ virtual private gateway/VPN gateway; two IPsec tunnels for redundancy; BGP or static routes.'), ('Dedicated link', 'Order a port at a colocation or via a partner (e.g. in Mumbai); private VLAN to your VPCs.'), ('Hub', 'Transit Gateway / Virtual WAN / NCC connect many networks with central routing.')],
    words=[('peering', 'a private connection between two networks'), ('IPsec', 'a standard for encrypted network tunnels'), ('BGP', 'the protocol routers use to exchange routes'), ('transitive', 'if A↔B and B↔C, then A↔C — peering is NOT')],
    diff=table(['', 'Peering', 'Site-to-site VPN', 'Direct Connect / ExpressRoute / Interconnect'], [['Connects', 'cloud ↔ cloud', 'office ↔ cloud', 'data centre ↔ cloud'], ['Path', 'provider backbone', 'internet (encrypted)', 'private circuit'], ['Set-up time', 'minutes', 'hours', 'weeks'], ['Bandwidth', 'high', 'about 1.25 Gbps per AWS tunnel', '1–100 Gbps']], minw=620),
    where=['Branch offices and data centres', 'Multi-account / multi-VPC designs', 'Private access to SaaS and cloud services'],
    realworld='Indian banks connect core systems to the cloud with dedicated circuits through Direct Connect / ExpressRoute locations in Mumbai and other cities — RBI-regulated workloads often require private connectivity rather than the public internet.',
    pro='VPC peering is not transitive and does not do “edge to edge” routing: a peered VPC cannot use your NAT gateway, internet gateway or VPN. That limit is why large organisations move to Transit Gateway or Virtual WAN hubs.')

SUMMARY = table(['#', 'Building block', 'Answers the question', 'AWS', 'Azure', 'Google Cloud'], [
    ['1', 'Virtual network & subnets', 'what is my private address space?', 'VPC, subnets', 'VNet, subnets', 'VPC (global), subnets'], ['2', 'Routing & gateways', 'where does each packet go?', 'route tables, IGW, NAT GW', 'routes/UDR, NAT Gateway', 'routes, Cloud NAT'],
    ['3', 'Firewalls', 'what may pass?', 'SG, NACL', 'NSG', 'firewall rules'], ['4', 'Load balancers', 'which server answers?', 'ALB/NLB', 'Load Balancer, App Gateway', 'Cloud Load Balancing'],
    ['5', 'DNS', 'what is the address?', 'Route 53', 'Azure DNS', 'Cloud DNS'], ['6', 'CDN & edge', 'can a nearby copy answer?', 'CloudFront', 'Front Door', 'Cloud CDN'], ['7', 'Hybrid & private links', 'how do networks connect?', 'Peering, TGW, VPN, DX', 'Peering, VPN, ExpressRoute', 'Peering, VPN, Interconnect']], minw=720)
CHECK = ('  <h3>Check yourself: which building block?</h3>\n' +
    qx('A. App servers must download patches but never accept connections from the internet.', ['Internet gateway + public IPs', 'Private subnet + NAT gateway', 'CDN', 'Peering'], 1, 'Outbound only.') +
    qx('B. Block one attacker IP for a whole subnet on AWS.', ['Security group', 'Network ACL deny rule', 'Route 53', 'NAT gateway'], 1, 'SGs cannot deny.') +
    qx('C. Send /api/* to one service and /* to another.', ['Network Load Balancer', 'Application Load Balancer', 'DNS weighted record', 'NAT'], 1, 'Layer 7 path routing.') +
    qx('D. 10 Gbps steady, private link from a data centre to Azure.', ['VPN Gateway', 'ExpressRoute', 'VNet peering', 'Front Door'], 1, 'Dedicated circuit.'))

TYPES = ('  <p>Seven networking building blocks, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['Why can a peered VPC not use your NAT gateway?', 'Why does an ALB have no fixed IP — and what do you do when a partner needs one?', 'Why can EKS run out of IP addresses long before CPU?'], 'types 7, 4 and 1') + MAP
         + jump(['VPC', 'Routing', 'Firewalls', 'Load balancers', 'DNS', 'CDN', 'Hybrid']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('CIDR block', 'The address range of a network or subnet.', 'Decides how many addresses and whether networks can connect.', '10.0.0.0/16 VPC, /24 subnets.'),
    ('Public IP / Elastic IP', 'An internet-routable address on an interface.', 'Needed only on internet-facing things — and billed on AWS.', 'Elastic IP, Azure Public IP, GCP external IP.'),
    ('Network interface (ENI / NIC)', 'The virtual network card of a resource.', 'Firewalls and IPs attach here.', 'ENI, NIC, vNIC.'),
    ('Flow logs', 'Records of accepted/rejected connections.', 'Troubleshooting and security investigations.', 'VPC Flow Logs, VNet flow logs, VPC Flow Logs (GCP).'),
    ('Private endpoint', 'A private IP for a cloud service inside your network.', 'Reach S3, databases or SaaS without the internet.', 'Gateway/interface endpoints, Private Link, Private Service Connect.'),
    ('Bastion / just-in-time access', 'A managed way to reach private servers.', 'No SSH/RDP ports open to the internet.', 'Session Manager, EC2 Instance Connect Endpoint, Azure Bastion, IAP TCP forwarding.')])

DEEP = ('  <h3>Subnet maths in one minute</h3>\n' + table(['CIDR', 'Addresses', 'Usable on AWS (−5)', 'Typical use'], [['/16', '65,536', '65,531', 'a whole VPC'], ['/20', '4,096', '4,091', 'a large subnet (EKS nodes + pods)'], ['/24', '256', '251', 'a normal subnet'], ['/28', '16', '11', 'smallest AWS subnet (e.g. a NAT/firewall)']], minw=520) +
    '\n  <p>AWS reserves the first four and the last address of every subnet (network, VPC router, DNS, future use, broadcast). Azure also reserves 5; Google Cloud reserves 4.</p>\n'
    '  <h3>Shared responsibility in networking</h3>\n  <p>The provider runs the physical network, the overlay, DDoS protection of its infrastructure and the managed services. <b>You</b> design CIDRs and subnets, write firewall and route rules, decide what is public, encrypt traffic and watch flow logs. Most network incidents in the cloud are configuration, not provider failures.</p>\n'
    '  <h3>IPv6 in the cloud</h3>\n  <p>All three clouds support dual-stack VPCs. IPv6 addresses are globally unique, so there is no NAT: AWS uses an <b>egress-only internet gateway</b> to give private-subnet IPv6 instances outbound-only access — the IPv6 version of a NAT gateway, without the per-GB charge.</p>')

clouds = vendor_tabs('<p><b>AWS:</b> Amazon VPC (subnets, route tables, IGW, NAT gateway, SGs, NACLs, flow logs, endpoints), Elastic Load Balancing, Route 53, CloudFront, Global Accelerator, Transit Gateway, Site-to-Site/Client VPN, Direct Connect, PrivateLink, Network Firewall, WAF, Shield.</p>',
    '<p><b>Azure:</b> Virtual Network (subnets, UDRs, NSGs, ASGs, NAT Gateway, service/private endpoints), Load Balancer, Application Gateway, Front Door, Traffic Manager, Azure DNS, VPN Gateway, ExpressRoute, Virtual WAN, Azure Firewall, Bastion, DDoS Protection.</p>',
    '<p><b>Google Cloud:</b> VPC (global; regional subnets, routes, firewall rules/policies, Cloud NAT, Cloud Router), Cloud Load Balancing, Cloud DNS, Cloud CDN, Cloud VPN, Cloud Interconnect, Network Connectivity Center, Private Service Connect, Cloud Armor, Cloud NGFW, IAP.</p>') + \
    cloud3([['Virtual network', 'VPC (regional)', 'VNet (regional)', 'VPC (global)'], ['Firewall at the VM', 'Security group', 'NSG / ASG', 'Firewall rules (tags)'], ['Outbound for private', 'NAT gateway', 'NAT Gateway', 'Cloud NAT'], ['L7 load balancer', 'ALB', 'Application Gateway / Front Door', 'Application Load Balancer'],
            ['DNS', 'Route 53', 'Azure DNS', 'Cloud DNS'], ['CDN', 'CloudFront', 'Front Door / CDN', 'Cloud CDN'], ['Dedicated link', 'Direct Connect', 'ExpressRoute', 'Cloud Interconnect'], ['Hub for many networks', 'Transit Gateway', 'Virtual WAN', 'Network Connectivity Center']])

# ------------------------------------------------------------------ practical
MOCKQ.extend([
 (mock('aws', ['VPC dashboard', 'Create VPC'], ['VPC dashboard', 'Your VPCs', 'Subnets', 'Route tables', 'Internet gateways', 'NAT gateways', 'Security groups'], 'Your VPCs',
       [('Resources to create', '( ) VPC and more'), ('Name tag auto-generation', 'tiffingo'), ('IPv4 CIDR block', '10.0.0.0/16'), ('Number of Availability Zones', '▾ 2'), ('Public subnets · Private subnets', '2 · 2'), ('NAT gateways · VPC endpoints', '▾ None · None')], 'Create VPC'),
  mock('az', ['Home', 'Virtual networks', 'Create virtual network'], ['Basics', 'Security', 'IP addresses', 'Tags', 'Review + create'], 'IP addresses',
       [('Resource group · Name', 'rg-tiffingo · vnet-tiffingo'), ('Region', '▾ Central India'), ('IPv4 address space', '10.1.0.0/16'), ('Subnets', 'public 10.1.1.0/24 · private 10.1.2.0/24')], 'Review + create'),
  mock('gcp', ['VPC network', 'VPC networks', 'Create a VPC network'], ['VPC networks', 'IP addresses', 'Firewall', 'Routes', 'VPC network peering'], 'VPC networks',
       [('Name', 'vpc-tiffingo'), ('Subnet creation mode', '( ) Custom'), ('Subnet 1 · Region · range', 'public · asia-south1 · 10.2.1.0/24'), ('Subnet 2 · Region · range', 'private · asia-south1 · 10.2.2.0/24')], 'Create')),
 (mock('aws', ['VPC', 'Security groups', 'Create security group'], ['Subnets', 'Route tables', 'Network ACLs', 'Security groups'], 'Security groups',
       [('Security group name', 'tiffingo-web-sg'), ('VPC', '▾ tiffingo-vpc'), ('Inbound rule 1', 'HTTP · TCP 80 · Anywhere-IPv4'), ('Inbound rule 2', 'SSH · TCP 22 · My IP')], 'Create security group'),
  mock('az', ['Home', 'Network security groups', 'nsg-web', 'Inbound security rules'], ['Overview', 'Inbound security rules', 'Outbound security rules', 'Network interfaces', 'Subnets'], 'Inbound security rules',
       [('Source · Destination port', 'Any · 80'), ('Protocol · Action', '▾ TCP · Allow'), ('Priority · Name', '100 · allow-http')], 'Add'),
  mock('gcp', ['VPC network', 'Firewall', 'Create a firewall rule'], ['VPC networks', 'Firewall', 'Routes', 'Firewall policies'], 'Firewall',
       [('Name · Network', 'tiffingo-allow-http · vpc-tiffingo'), ('Direction · Action', '▾ Ingress · Allow'), ('Targets', '▾ Specified target tags: web'), ('Source IPv4 ranges · Ports', '0.0.0.0/0 · tcp:80')], 'Create')),
 (mock('aws', ['Route 53', 'Hosted zones', 'Create hosted zone'], ['Dashboard', 'Hosted zones', 'Health checks', 'Resolver', 'Profiles'], 'Hosted zones',
       [('Domain name', 'tiffingo.internal'), ('Type', '( ) Private hosted zone'), ('VPC to associate', '▾ Asia Pacific (Mumbai) · tiffingo-vpc')], 'Create hosted zone'),
  mock('az', ['Home', 'Private DNS zones', 'Create Private DNS zone'], ['Basics', 'Tags', 'Review + create'], 'Basics',
       [('Resource group', '▾ rg-tiffingo'), ('Name', 'tiffingo.internal'), ('Then: Virtual network links', '+ Add → vnet-tiffingo')], 'Review + create'),
  mock('gcp', ['Network services', 'Cloud DNS', 'Create a DNS zone'], ['Cloud DNS', 'Zones', 'Policies', 'Response policies'], 'Zones',
       [('Zone type', '( ) Private'), ('Zone name · DNS name', 'tiffingo-internal · tiffingo.internal'), ('Networks', '▾ vpc-tiffingo')], 'Create')),
 (mock('aws', ['VPC', 'Peering connections', 'Create peering connection'], ['Your VPCs', 'Peering connections', 'Route tables', 'Transit gateways'], 'Peering connections',
       [('Name', 'prod-to-analytics'), ('VPC ID (Requester)', '▾ tiffingo-vpc 10.0.0.0/16'), ('Account · Region', '( ) My account · This Region'), ('VPC ID (Accepter)', '▾ analytics 10.9.0.0/16')], 'Create peering connection'),
  mock('az', ['Home', 'vnet-tiffingo', 'Peerings', 'Add peering'], ['Overview', 'Address space', 'Subnets', 'Peerings', 'DNS servers'], 'Peerings',
       [('Remote virtual network', '▾ vnet-analytics'), ('Peering link name (remote)', 'analytics-to-tiffingo'), ('Peering link name (local)', 'tiffingo-to-analytics'), ('Allow access', '[x] Allow both networks to access each other')], 'Add'),
  mock('gcp', ['VPC network', 'VPC network peering', 'Create peering connection'], ['VPC networks', 'Firewall', 'Routes', 'VPC network peering'], 'VPC network peering',
       [('Name', 'tiffingo-to-analytics'), ('Your VPC network', '▾ vpc-tiffingo'), ('Peered VPC network', '( ) In project tiffingo-lab · vpc-analytics')], 'Create')),
])

STEP1 = ('1 · Build a network with public and private subnets', tri(
    (['[[VPC]] → [[Create VPC]] → choose [[VPC and more]] (the wizard draws a preview).', 'Name <code>tiffingo</code>, IPv4 CIDR <code>10.0.0.0/16</code>, 2 AZs, 2 public + 2 private subnets, NAT gateways [[None]] (they cost money), VPC endpoints [[None]].', '[[Create VPC]] → then open [[Route tables]]: the public one has <code>0.0.0.0/0 → igw-…</code>, the private ones only <code>local</code>.'],
     "VPC=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=tiffingo}]' --query Vpc.VpcId --output text)\nPUB=$(aws ec2 create-subnet --vpc-id $VPC --cidr-block 10.0.1.0/24 --availability-zone ap-south-1a --query Subnet.SubnetId --output text)\nPRIV=$(aws ec2 create-subnet --vpc-id $VPC --cidr-block 10.0.11.0/24 --availability-zone ap-south-1a --query Subnet.SubnetId --output text)\nIGW=$(aws ec2 create-internet-gateway --query InternetGateway.InternetGatewayId --output text)\naws ec2 attach-internet-gateway --internet-gateway-id $IGW --vpc-id $VPC\nRT=$(aws ec2 create-route-table --vpc-id $VPC --query RouteTable.RouteTableId --output text)\naws ec2 create-route --route-table-id $RT --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW\naws ec2 associate-route-table --route-table-id $RT --subnet-id $PUB\naws ec2 describe-route-tables --filters Name=vpc-id,Values=$VPC --query 'RouteTables[].Routes[].[DestinationCidrBlock,GatewayId]' --output table",
     'two route tables: the custom one with <code>0.0.0.0/0 → igw-…</code> (associated with the public subnet) and the main one with only <code>10.0.0.0/16 → local</code> (used by the private subnet).'),
    (['[[Virtual networks]] → [[Create]] → resource group <code>rg-tiffingo</code>, name <code>vnet-tiffingo</code>, Region [[Central India]].', '[[IP addresses]] tab: address space <code>10.1.0.0/16</code>; edit the default subnet to <code>public 10.1.1.0/24</code>; [[Add a subnet]] <code>private 10.1.2.0/24</code>, tick [[Enable private subnet (no default outbound access)]].', '[[Review + create]] → [[Create]].'],
     'az group create --name rg-tiffingo --location centralindia\naz network vnet create --resource-group rg-tiffingo --name vnet-tiffingo --address-prefix 10.1.0.0/16 \\\n  --subnet-name public --subnet-prefixes 10.1.1.0/24\naz network vnet subnet create --resource-group rg-tiffingo --vnet-name vnet-tiffingo --name private \\\n  --address-prefixes 10.1.2.0/24 --default-outbound-access false\naz network vnet subnet list --resource-group rg-tiffingo --vnet-name vnet-tiffingo --query "[].[name,addressPrefix]" --output table',
     'two subnets <code>public 10.1.1.0/24</code> and <code>private 10.1.2.0/24</code>. Azure routes to the internet via system routes; a private subnet without default outbound access needs a NAT Gateway for outbound traffic.'),
    (['[[VPC network]] → [[VPC networks]] → [[Create VPC network]] → name <code>vpc-tiffingo</code>, subnet creation mode [[Custom]].', 'Subnet <code>public</code>: Region [[asia-south1]], range <code>10.2.1.0/24</code>; [[Add subnet]] <code>private</code>: asia-south1, <code>10.2.2.0/24</code>, [[Private Google Access]] On.', '[[Create]] → open [[Routes]]: a default route to the internet gateway and one subnet route per subnet.'],
     'gcloud compute networks create vpc-tiffingo --subnet-mode=custom\ngcloud compute networks subnets create public --network=vpc-tiffingo --region=asia-south1 --range=10.2.1.0/24\ngcloud compute networks subnets create private --network=vpc-tiffingo --region=asia-south1 --range=10.2.2.0/24 --enable-private-ip-google-access\ngcloud compute routes list --filter="network:vpc-tiffingo"',
     'two subnets and routes including <code>0.0.0.0/0 → default-internet-gateway</code>. In Google Cloud “public” means a VM has an external IP — the subnets themselves are the same.')),
    'Each cloud defines “public” differently: AWS by the route table, Azure by outbound access settings and public IPs, Google by whether a VM gets an external IP.')

STEP2 = ('2 · Firewall rules: web open, SSH only from you', tri(
    (['[[VPC]] → [[Security groups]] → [[Create security group]] → name <code>tiffingo-web-sg</code>, VPC <code>tiffingo</code>.', 'Inbound: [[Add rule]] HTTP 80 from [[Anywhere-IPv4]]; [[Add rule]] SSH 22 from [[My IP]] → [[Create security group]].', 'Open [[Network ACLs]] and look at the default NACL: rule 100 allow all, rule * deny all.'],
     "MYIP=$(curl -s https://checkip.amazonaws.com)/32    # in CloudShell this is CloudShell's IP, not your laptop's\nSGW=$(aws ec2 create-security-group --group-name tiffingo-web-sg --description web --vpc-id $VPC --query GroupId --output text)\naws ec2 authorize-security-group-ingress --group-id $SGW --protocol tcp --port 80 --cidr 0.0.0.0/0\naws ec2 authorize-security-group-ingress --group-id $SGW --protocol tcp --port 22 --cidr $MYIP\nSGD=$(aws ec2 create-security-group --group-name tiffingo-db-sg --description db --vpc-id $VPC --query GroupId --output text)\naws ec2 authorize-security-group-ingress --group-id $SGD --protocol tcp --port 5432 --source-group $SGW\naws ec2 describe-security-groups --group-ids $SGW $SGD --query 'SecurityGroups[].[GroupName,IpPermissions[].FromPort]' --output text",
     'two groups: web with ports 80 and 22, db with 5432 — whose source is the web security group, not an IP range.'),
    (['[[Network security groups]] → [[Create]] → <code>nsg-web</code>, rg-tiffingo, Central India.', 'Open it → [[Inbound security rules]] → [[Add]]: destination port 80, TCP, Allow, priority 100; add SSH 22 with source [[My IP address]], priority 110.', '[[Subnets]] → [[Associate]] → vnet-tiffingo / public.'],
     'MYIP=$(curl -s https://ifconfig.me)/32\naz network nsg create --resource-group rg-tiffingo --name nsg-web\naz network nsg rule create --resource-group rg-tiffingo --nsg-name nsg-web --name allow-http --priority 100 \\\n  --direction Inbound --access Allow --protocol Tcp --destination-port-ranges 80\naz network nsg rule create --resource-group rg-tiffingo --nsg-name nsg-web --name allow-ssh-me --priority 110 \\\n  --direction Inbound --access Allow --protocol Tcp --destination-port-ranges 22 --source-address-prefixes $MYIP\naz network vnet subnet update --resource-group rg-tiffingo --vnet-name vnet-tiffingo --name public --network-security-group nsg-web\naz network nsg rule list --resource-group rg-tiffingo --nsg-name nsg-web --output table',
     'two custom rules (priority 100 and 110); Azure also shows default rules 65000–65500 (allow VNet, allow load balancer, deny all) with <code>--include-default</code>.'),
    (['[[VPC network]] → [[Firewall]] → [[Create firewall rule]] → name <code>tiffingo-allow-http</code>, network vpc-tiffingo, ingress, allow, target tags <code>web</code>, source <code>0.0.0.0/0</code>, TCP 80 → [[Create]].', 'Create another: <code>tiffingo-allow-ssh</code>, target tags web, source = your IP/32, TCP 22.', 'Note the implied rules: deny all ingress, allow all egress.'],
     'MYIP=$(curl -s https://ifconfig.me)/32\ngcloud compute firewall-rules create tiffingo-allow-http --network=vpc-tiffingo --direction=INGRESS \\\n  --action=ALLOW --rules=tcp:80 --source-ranges=0.0.0.0/0 --target-tags=web\ngcloud compute firewall-rules create tiffingo-allow-ssh --network=vpc-tiffingo --direction=INGRESS \\\n  --action=ALLOW --rules=tcp:22 --source-ranges=$MYIP --target-tags=web\ngcloud compute firewall-rules list --filter="network:vpc-tiffingo"',
     'two rules that apply only to VMs carrying the network tag <code>web</code>. For SSH from the browser use IAP (source range 35.235.240.0/20) instead of opening 22 to the world.')),
    'Admin ports (22/3389) should never be open to 0.0.0.0/0. The CloudShell / Cloud Shell IP is not your laptop’s IP — get yours from a “what is my IP” page when testing from your PC.')

STEP3 = ('3 · Private DNS: give the database a name', tri(
    (['[[Route 53]] → [[Hosted zones]] → [[Create hosted zone]] → domain <code>tiffingo.internal</code>, type [[Private hosted zone]], VPC: Mumbai / tiffingo → [[Create]].', '[[Create record]] → name <code>db</code>, type A, value <code>10.0.11.10</code>, TTL 300 → [[Create records]].', 'From any VM in the VPC: <code>nslookup db.tiffingo.internal</code>.'],
     "ZONE=$(aws route53 create-hosted-zone --name tiffingo.internal --caller-reference tg-$(date +%s) \\\n  --vpc VPCRegion=ap-south-1,VPCId=$VPC --hosted-zone-config PrivateZone=true --query HostedZone.Id --output text)\naws route53 change-resource-record-sets --hosted-zone-id $ZONE --change-batch \\\n  '{\"Changes\":[{\"Action\":\"CREATE\",\"ResourceRecordSet\":{\"Name\":\"db.tiffingo.internal\",\"Type\":\"A\",\"TTL\":300,\"ResourceRecords\":[{\"Value\":\"10.0.11.10\"}]}}]}'\naws route53 list-resource-record-sets --hosted-zone-id $ZONE --output table",
     'NS, SOA and your A record. Hosted zones cost $0.50/month, but a zone deleted within 12 hours of creation is not charged.'),
    (['[[Private DNS zones]] → [[Create]] → rg-tiffingo, name <code>tiffingo.internal</code> → [[Create]].', 'Open it → [[Virtual network links]] → [[Add]] → link <code>vnet-link</code> to vnet-tiffingo.', '[[Recordsets]] → [[+ Record set]] → name <code>db</code>, A, 10.1.2.10.'],
     'az network private-dns zone create --resource-group rg-tiffingo --name tiffingo.internal\naz network private-dns link vnet create --resource-group rg-tiffingo --zone-name tiffingo.internal \\\n  --name vnet-link --virtual-network vnet-tiffingo --registration-enabled false\naz network private-dns record-set a add-record --resource-group rg-tiffingo --zone-name tiffingo.internal \\\n  --record-set-name db --ipv4-address 10.1.2.10\naz network private-dns record-set a list --resource-group rg-tiffingo --zone-name tiffingo.internal --output table',
     'record <code>db</code> with 10.1.2.10. With <code>--registration-enabled true</code> VMs would register their own names automatically.'),
    (['[[Network services]] → [[Cloud DNS]] → [[Create zone]] → type [[Private]], zone name <code>tiffingo-internal</code>, DNS name <code>tiffingo.internal</code>, network vpc-tiffingo → [[Create]].', '[[Add standard]] record → <code>db</code>, A, 10.2.2.10 → [[Create]].'],
     'gcloud dns managed-zones create tiffingo-internal --dns-name=tiffingo.internal. --visibility=private \\\n  --networks=vpc-tiffingo --description="TiffinGo private zone"\ngcloud dns record-sets create db.tiffingo.internal. --zone=tiffingo-internal --type=A --ttl=300 --rrdatas=10.2.2.10\ngcloud dns record-sets list --zone=tiffingo-internal',
     'NS, SOA and the A record (note the trailing dot in DNS names).')),
    'Apps should connect to <code>db.tiffingo.internal</code>, not an IP — when the database moves, you change one record.')

STEP4 = ('4 · Peer a second network (and see “not transitive”)', tri(
    (['Create a second VPC <code>analytics</code> with CIDR <code>10.9.0.0/16</code> (must not overlap).', '[[Peering connections]] → [[Create peering connection]] → requester tiffingo, accepter analytics → [[Create]] → select it → [[Actions]] → [[Accept request]].', 'Add routes in both VPCs’ route tables: <code>10.9.0.0/16 → pcx-…</code> and <code>10.0.0.0/16 → pcx-…</code>.'],
     "VPC2=$(aws ec2 create-vpc --cidr-block 10.9.0.0/16 --query Vpc.VpcId --output text)\nPCX=$(aws ec2 create-vpc-peering-connection --vpc-id $VPC --peer-vpc-id $VPC2 --query VpcPeeringConnection.VpcPeeringConnectionId --output text)\naws ec2 accept-vpc-peering-connection --vpc-peering-connection-id $PCX\naws ec2 create-route --route-table-id $RT --destination-cidr-block 10.9.0.0/16 --vpc-peering-connection-id $PCX\nRT2=$(aws ec2 describe-route-tables --filters Name=vpc-id,Values=$VPC2 --query 'RouteTables[0].RouteTableId' --output text)\naws ec2 create-route --route-table-id $RT2 --destination-cidr-block 10.0.0.0/16 --vpc-peering-connection-id $PCX\naws ec2 describe-vpc-peering-connections --vpc-peering-connection-ids $PCX --query 'VpcPeeringConnections[0].Status.Code' --output text",
     '<code>active</code>. Try creating a peering to a VPC with 10.0.0.0/16 again — it fails: overlapping CIDRs.'),
    (['Create <code>vnet-analytics</code> with 10.9.0.0/16.', 'vnet-tiffingo → [[Peerings]] → [[Add]] → remote vnet-analytics; tick allow access both ways → [[Add]] (Azure creates both directions).'],
     'az network vnet create --resource-group rg-tiffingo --name vnet-analytics --address-prefix 10.9.0.0/16 --subnet-name s1 --subnet-prefixes 10.9.1.0/24\naz network vnet peering create --resource-group rg-tiffingo --name tiffingo-to-analytics --vnet-name vnet-tiffingo \\\n  --remote-vnet vnet-analytics --allow-vnet-access\naz network vnet peering create --resource-group rg-tiffingo --name analytics-to-tiffingo --vnet-name vnet-analytics \\\n  --remote-vnet vnet-tiffingo --allow-vnet-access\naz network vnet peering list --resource-group rg-tiffingo --vnet-name vnet-tiffingo --query "[].[name,peeringState]" --output table',
     '<code>Connected</code>. Azure adds the routes for you (system routes), no route table edits needed.'),
    (['Create a second network <code>vpc-analytics</code> (custom, subnet 10.9.1.0/24 in asia-south1).', '[[VPC network peering]] → [[Create connection]] → name <code>tiffingo-to-analytics</code>, your network vpc-tiffingo, peered network vpc-analytics → [[Create]]; repeat in the other direction.'],
     'gcloud compute networks create vpc-analytics --subnet-mode=custom\ngcloud compute networks subnets create a1 --network=vpc-analytics --region=asia-south1 --range=10.9.1.0/24\ngcloud compute networks peerings create tiffingo-to-analytics --network=vpc-tiffingo --peer-network=vpc-analytics\ngcloud compute networks peerings create analytics-to-tiffingo --network=vpc-analytics --peer-network=vpc-tiffingo\ngcloud compute networks peerings list',
     'both peerings with STATE <b>ACTIVE</b> (the first shows INACTIVE until the second side is created).')),
    'Peering is free to set up; traffic across zones/Regions is billed. Remember: peering is not transitive.')

prac = practical(OWN_INTRO + ' Nothing in these steps runs a VM; only a hosted zone and public IP lookups touch billing, and they cost nothing if deleted the same day.', [SETUP_STEP, STEP1, STEP2, STEP3, STEP4],
    cleanup='<b>AWS</b> (order matters): delete the peering connection; delete the record and hosted zone; delete security groups; detach and delete the internet gateway; delete subnets, the custom route table and both VPCs — or simply [[Your VPCs]] → select → [[Actions]] → [[Delete VPC]] (deletes subnets, route tables, IGW and SGs with it). CLI: <code>aws ec2 delete-vpc-peering-connection --vpc-peering-connection-id $PCX</code>; <code>aws route53 change-resource-record-sets …DELETE…</code> then <code>aws route53 delete-hosted-zone --id $ZONE</code>; <code>aws ec2 delete-security-group --group-id $SGD; aws ec2 delete-security-group --group-id $SGW; aws ec2 detach-internet-gateway --internet-gateway-id $IGW --vpc-id $VPC; aws ec2 delete-internet-gateway --internet-gateway-id $IGW; aws ec2 delete-subnet --subnet-id $PUB; aws ec2 delete-subnet --subnet-id $PRIV; aws ec2 delete-route-table --route-table-id $RT; aws ec2 delete-vpc --vpc-id $VPC; aws ec2 delete-vpc --vpc-id $VPC2</code>.<br>'
            '<b>Azure:</b> <code>az group delete --name rg-tiffingo --yes --no-wait</code>.<br>'
            '<b>Google Cloud:</b> <code>gcloud dns record-sets delete db.tiffingo.internal. --zone=tiffingo-internal --type=A; gcloud dns managed-zones delete tiffingo-internal; gcloud compute networks peerings delete tiffingo-to-analytics --network=vpc-tiffingo; gcloud compute networks peerings delete analytics-to-tiffingo --network=vpc-analytics; gcloud compute firewall-rules delete tiffingo-allow-http tiffingo-allow-ssh --quiet; gcloud compute networks subnets delete public private --region=asia-south1 --quiet; gcloud compute networks subnets delete a1 --region=asia-south1 --quiet; gcloud compute networks delete vpc-tiffingo vpc-analytics --quiet</code>.'.replace('[[', '<b>').replace(']]', '</b>'))

mist = mistakes([
    ['Database in a public subnet with its port open.', 'Default VPC, quick setup.', 'Private subnet + SG allowing only the app SG.'],
    ['Overlapping CIDRs (10.0.0.0/16 everywhere).', 'Copying examples.', 'Plan an IP address map across VPCs, offices and future peers.'],
    ['Subnets too small for Kubernetes.', 'Pods use VPC IPs.', 'Larger subnets (/20+) or prefix delegation / secondary ranges.'],
    ['Surprise NAT gateway bill.', 'S3 and updates flow through NAT per GB.', 'Gateway endpoints for S3/DynamoDB; Private Google Access; check flow logs.'],
    ['Hard-coded IP addresses in apps.', 'It worked once.', 'Use DNS names (private zones, load balancer DNS).'],
    ['Expecting peering to be transitive.', 'A↔B, B↔C feels like A↔C.', 'Use a hub (Transit Gateway, Virtual WAN, NCC) or direct peerings.'],
    ['SSH 22 open to the world for convenience.', 'Default wizard choice.', 'Session Manager / Instance Connect Endpoint / Bastion / IAP.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Cloud networking: virtual networks, load balancing, DNS, CDN, VPN.'], ['AWS CLF-C02', 'VPC, subnets, IGW, NAT gateway, security groups vs NACLs, Route 53, CloudFront, ELB, Direct Connect, VPN, Transit Gateway, PrivateLink, Global Accelerator, WAF/Shield.'], ['AZ-900', 'VNets, subnets, peering, VPN Gateway, ExpressRoute, Azure DNS, public and private endpoints, NSGs.'], ['Google Cloud Digital Leader', 'Global VPC, Cloud Load Balancing, Cloud CDN, Cloud DNS, Cloud VPN and Interconnect, premium network tier.']], minw=560) + \
    qx('1. Which AWS component allows instances in a private subnet to reach the internet for updates but blocks inbound connections?', ['Internet gateway', 'NAT gateway', 'Security group', 'Route 53'], 1, 'Outbound-only.') + \
    qx('2. Security groups are…', ['stateless, subnet-level', 'stateful, instance-level', 'DNS records', 'route tables'], 1, 'NACLs are stateless subnet-level.') + \
    qx('3. Which Azure service gives a private, dedicated connection from on-premises to Azure?', ['VPN Gateway', 'ExpressRoute', 'Azure DNS', 'Front Door'], 1, 'Not over the internet.') + \
    qx('4. Which AWS service caches content at edge locations?', ['Amazon CloudFront', 'Amazon VPC', 'AWS Direct Connect', 'Elastic IP'], 0, 'CDN.') + \
    qx('5. A Google Cloud VPC network is…', ['zonal', 'regional', 'global', 'per project only in one zone'], 2, 'Subnets are regional.') + \
    qx('6. Which load balancer routes HTTP requests by URL path?', ['Network Load Balancer', 'Application Load Balancer', 'Gateway Load Balancer', 'Classic DNS'], 1, 'Layer 7.')

proj = miniproject('Mini project: the TiffinGo network design',
    'Design and build the network every later lesson will use.',
    ['<b>Address plan:</b> choose CIDRs for prod, analytics and the office (no overlaps).',
     '<b>Draw it:</b> VPC/VNet with public and private subnets in two zones, IGW, NAT, ALB, app and DB tiers.',
     '<b>Rules:</b> write the firewall table (source → destination → port) for ALB, app, DB and admin access.',
     '<b>Build:</b> on your own account create the network, subnets, firewall rules, private DNS and peering (steps 1–4).',
     '<b>Request path:</b> write the 6 hops of a customer order through your design.',
     '<b>Cost:</b> list which parts cost money when idle (NAT, load balancer, public IPs, hosted zone).',
     '<b>Clean up</b> and screenshot empty lists.'],
    'A network diagram, a firewall rule table and a working lab network (then deleted).', 'This lesson + 5.1 (Regions/AZs) + 6.1 (compute) + 4.3 (network virtualization).')

assemble_v2(HERE, story_h2='A login attempt from the other side of the world', hook_html=hk,
    narration='At 3 a.m. TiffinGo’s database logged a login attempt from an unknown country. Nobody had “opened” it — the default network had. Time to understand cloud networking.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Cloud networking',
    formal='<b>Cloud networking</b> is the set of software-defined services that connect, isolate, protect and deliver cloud resources: <b>virtual networks and subnets</b>, <b>routing and gateways</b>, <b>firewalls</b>, <b>load balancers</b>, <b>DNS</b>, <b>content delivery networks</b>, and <b>hybrid connectivity</b> such as peering, VPNs and dedicated links — all configured through APIs on top of the provider’s physical network.',
    simple='The roads, gates, guards, signposts and phone book of the cloud — how traffic gets to your servers safely and quickly, and how your networks connect to each other and your office.',
    interview=['“A VPC is an isolated virtual network with its own CIDR, split into public subnets — with a route to an internet gateway — and private subnets that reach out only via NAT.”', '“Security groups are stateful allow-lists at the instance; NACLs are stateless allow/deny at the subnet. Users come in through Route 53, CloudFront and a load balancer; offices connect by VPN or Direct Connect.”'],
    terms_rows=[('VPC / VNet', 'Private virtual network.'), ('Subnet', 'Slice of the address range.'), ('CIDR', 'IP range notation.'), ('Route table', 'Where packets go.'), ('Internet gateway', 'Two-way internet door.'), ('NAT gateway', 'Outbound-only internet.'), ('Security group / NSG', 'Stateful firewall.'), ('Load balancer', 'Spreads traffic over healthy targets.'), ('CDN', 'Edge cache near users.'), ('Peering / VPN', 'Connect networks privately.')],
    exam='CLF-C02 loves security group vs NACL, public vs private subnet, NAT gateway, Route 53, CloudFront, Direct Connect vs VPN. AZ-900 asks VNets, peering, VPN Gateway, ExpressRoute, DNS and endpoints. Digital Leader asks Google’s global network and load balancing.',
    picture_h2='The standard cloud network, and where each service lives', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven networking building blocks, one by one', TYPES)],
    how_h2='One order, through every networking building block', how_intro='Follow one HTTPS request from a phone to the database.', how_anim=REQ,
    parts_h2='Six more pieces you will meet in every network', parts_html=parts, lv='',
    myth_rows=[('A subnet is public because of its name.', 'It is public because of its route to an internet gateway.', 'Type 2.'), ('Security groups can block one IP.', 'They only allow; use NACLs / NSGs / WAF to deny.', 'Type 3.'), ('Peering connects everything to everything.', 'It is not transitive.', 'Type 7.')],
    extra_secs=[('deep', 'Deep dive', 'Subnet maths, shared responsibility and IPv6', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Design a VPC/VNet with public and private subnets across zones.', 'Explain route tables, internet and NAT gateways, and why a subnet is public.', 'Write security group / NSG / firewall rules and explain stateful vs stateless.', 'Explain load balancers, DNS, CDN and hybrid connectivity options.', 'Build a network, firewall rules, private DNS and peering on your own account (console and CLI).'],
    next_html='<a href="../04-cloud-products-and-solutions-map/">6.4 Cloud products and solutions map</a>.',
    pre='<b>Before you start:</b> <a href="../../05-core-cloud-concepts/01-regions-availability-zones-and-edge-locations/">5.1 Regions and AZs</a> and <a href="../../04-virtualization/03-network-storage-and-data-virtualization/">4.3 Network virtualization</a>.')
