import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
sys.path.insert(0, HERE)
from _types import build as build_types
from _prac import PRAC
C = 'l43.txt'; CD = 'l43_data.txt'; CA = 'l43_aws.txt'
def sec(a, b=None): return capsec(C, a, b)
def secd(a, b=None): return capsec(CD, a, b)
def seca(a, b=None): return capsec(CA, a, b)

hk = hook('If a VPC has no cables, no switch and no router box, how do packets still find their way?',
    'Because the network itself is <b>virtual</b>: software on every host wraps your packet, looks up where the destination VM lives, and ships it over a shared physical network. In this lesson we build a virtual network with a <b>virtual cable</b> (ping: <b>0% loss, 0.04 ms</b>), pool two disks into one <b>392 MB</b> storage pool, make a <b>10 GiB</b> disk that uses only <b>196 KiB</b>, and run one SQL query across a <b>CSV file, a Parquet file and a database</b> without copying any data. Then we do the same ideas in AWS with the CLI.',
    ['Network virtualization: vNIC, virtual switch, VLAN, overlay (VXLAN), SDN, VPC.', 'Storage virtualization: pools, LVM, SAN/NAS, thin provisioning, copy-on-write, snapshots.', 'Data virtualization: query many sources as one, without ETL copies.'])

def story_scene():
    o = t(180, 12, 'TiffinGo’s three new problems', 9, 'ink', bold=True)
    items = [('globe', 'Network', ['Kitchen and billing', 'must not see each other', 'on the same hosts'], 'blue'),
             ('disk', 'Storage', ['Server A disk full,', 'Server B disk 80% empty', ''], 'amber'),
             ('db', 'Data', ['Orders in CSV, cities', 'in Parquet, ratings in', 'a database'], 'violet')]
    for i, (icn, h, lines, tn) in enumerate(items):
        x = 8 + i * 118
        o += box(x, 22, 108, 104, tn, rx=8) + ic(icn, x + 44, 28, 0.85) + t(x + 54, 64, h, 8.6, 'ink', bold=True)
        for j, l in enumerate(lines):
            o += t(x + 54, 80 + j * 12, l, 6.8, 'ink2')
    o += t(180, 142, 'Answer for all three: put a software layer in between.', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Three boxes: network (kitchen and billing must be isolated on shared hosts), storage (one server full, another empty), data (orders, cities and ratings in three different formats).', story_scene(), 'Virtualize the <tspan font-weight="700" class="s-acc">network, the storage and the data</tspan>.', h=168)
dialogue = '''R> Sir, we moved TiffinGo to VMs. Now the kitchen team and the billing team share the same physical hosts. Billing has card data — can the kitchen VMs reach it?
A> Not if we give each team its own virtual network. No new cables — software decides which VM can talk to which.
K> And storage? One server is full and the other is almost empty.
A> Pool all the disks and hand out virtual disks from the pool. A disk then becomes just a number you ask for: “give me 20 GiB”.
R> Management also wants one report from orders, cities and ratings. They live in three different places.
A> Then we virtualize the data too: one query layer that reads all three where they are. Today, network, storage and data virtualization.'''

# ---------------------------------------------------------------- big figures
def netfig():
    o = t(320, 16, 'Network virtualization: many private networks on one physical network', 11, 'ink', bold=True)
    for h in range(2):
        x = 20 + h * 320
        o += box(x, 30, 280, 196, 'card', rx=10) + t(x + 140, 46, f'Physical host {h + 1}', 8.6, 'ink', bold=True)
        vms = [('Kitchen VM', '10.10.1.5', 'blue'), ('Other customer', '10.10.1.5', 'violet')] if h == 0 else [('Billing VM', '10.10.2.7', 'blue'), ('Other customer', '172.16.0.9', 'violet')]
        for i, (n, ip, tn) in enumerate(vms):
            vx = x + 14 + i * 132
            o += box(vx, 56, 120, 46, tn, rx=6) + t(vx + 60, 74, n, 7.8, 'ink', bold=True) + t(vx + 60, 88, 'vNIC ' + ip, 7, 'ink2')
            o += arrow(vx + 60, 102, vx + 60, 118)
        o += box(x + 14, 120, 252, 26, 'green', rx=5) + t(x + 140, 137, 'Virtual switch + security groups + routing (software)', 7.4, 'ink', bold=True)
        o += arrow(x + 140, 146, x + 140, 160)
        o += box(x + 14, 162, 252, 26, 'amber', rx=5) + t(x + 140, 179, 'Encapsulation (VTEP / AWS Nitro card): wrap + tag', 7.4, 'ink', bold=True)
        o += box(x + 70, 194, 140, 24, 'card', rx=5) + t(x + 140, 210, 'Physical NIC', 7.6, 'ink', bold=True)
        o += arrow(x + 140, 218, x + 140, 244)
    o += box(20, 246, 600, 30, 'red', rx=8) + t(320, 265, 'Physical “underlay” network: switches and routers only see host 1 ↔ host 2', 8.4, 'ink', bold=True)
    o += f'<path d="M300 175 C 310 150, 330 150, 340 175" style="fill:none;stroke:#E0A100;stroke-width:2.4;stroke-dasharray:5 3"/>'
    o += t(320, 296, 'Blue VMs = one virtual network (TiffinGo VPC). Violet = another customer — the same IP 10.10.1.5 is fine, the networks never mix.', 7.6, 'ink2')
    o += t(320, 310, 'The tag (VNI / VPC ID) in the wrapper decides which virtual network a packet belongs to.', 7.6, 'ink2')
    return o
NETF = bigfig('Two physical hosts. Each runs a TiffinGo VM and another customer’s VM with virtual NICs, a software virtual switch with security groups, an encapsulation layer (VTEP or AWS Nitro card) and a physical NIC. Both hosts connect to a shared physical underlay network. Packets of different virtual networks are wrapped and tagged so they never mix, even with the same IP.', netfig(), h=320)

def storfig():
    o = t(320, 16, 'Storage virtualization: many physical disks → one pool → virtual disks', 11, 'ink', bold=True)
    for i, (n, s, who) in enumerate([('VM 1 disk', '20 GiB', 'menu API'), ('VM 2 disk', '50 GiB', 'orders DB'), ('VM 3 disk', '100 GiB', 'logs'), ('Snapshot', 'of VM 2', 'before upgrade')]):
        x = 30 + i * 148
        o += box(x, 32, 134, 44, 'blue' if i < 3 else 'violet', rx=6) + t(x + 67, 50, n + ' · ' + s, 7.8, 'ink', bold=True) + t(x + 67, 64, who, 7, 'ink2')
        o += arrow(x + 67, 76, x + 67, 92)
    o += box(20, 94, 600, 92, 'green', rx=10) + t(320, 112, 'Storage virtualization layer (LVM · SAN controller · Ceph · AWS EBS)', 9, 'ink', bold=True)
    feats = [('Pooling', 'all disks = one pool'), ('Thin provisioning', 'use only what is written'), ('Copy-on-write', 'snapshots and clones'), ('Replication', 'copy to 2nd disk/site'), ('Tiering', 'hot→SSD, cold→HDD')]
    for i, (a, b) in enumerate(feats):
        x = 30 + i * 118
        o += box(x, 124, 108, 52, 'card', rx=5) + t(x + 54, 144, a, 7.6, 'ink', bold=True) + t(x + 54, 160, b, 6.8, 'ink2')
    o += arrow(320, 186, 320, 200)
    disks = [('SSD', '1 TB', 'vendor A'), ('SSD', '1 TB', 'vendor A'), ('HDD', '4 TB', 'vendor B'), ('HDD', '4 TB', 'vendor B'), ('NVMe', '2 TB', 'vendor C')]
    for i, (k, s, v) in enumerate(disks):
        x = 30 + i * 118
        o += cyl(x + 14, 204, 80, 50, k + ' ' + s, 'amber')
        o += t(x + 54, 268, v, 6.8, 'ink2')
    o += t(320, 288, 'The VM never knows which physical disk holds its blocks. Disks can be added, replaced or moved underneath without the VM noticing.', 7.6, 'ink2')
    return o
STORF = bigfig('Top: four virtual disks (20, 50 and 100 GiB VM disks and a snapshot). Middle: a storage virtualization layer such as LVM, a SAN controller, Ceph or AWS EBS, providing pooling, thin provisioning, copy-on-write, replication and tiering. Bottom: five physical disks of different types and vendors.', storfig(), h=300)

def datafig():
    o = t(320, 16, 'Data virtualization: query data where it lives, as if it were one database', 11, 'ink', bold=True)
    src = [('orders.csv', 'CSV file', 'disk'), ('cities.parquet', 'columnar file', 'disk'), ('crm.db', 'SQLite database', 'db'), ('S3 / MySQL / SaaS', 'in the cloud', 'cloud')]
    for i, (n, s, icn) in enumerate(src):
        y = 32 + i * 52
        o += box(20, y, 150, 44, 'amber', rx=6) + ic(icn, 28, y + 10, 0.9) + t(110, y + 20, n, 7.8, 'ink', bold=True) + t(110, y + 34, s, 7, 'ink2')
        o += arrow(170, y + 22, 228, 132)
    o += box(230, 50, 190, 168, 'green', rx=10) + t(325, 70, 'Virtual data layer', 9, 'ink', bold=True)
    for j, (a, b) in enumerate([('1 Catalog', 'what tables exist where'), ('2 Query planner', 'split SQL per source'), ('3 Pushdown', 'filter at the source'), ('4 Join + cache', 'combine, return result'), ('5 Security', 'mask, row-level rules')]):
        o += box(242, 80 + j * 26, 166, 22, 'card', rx=4) + t(250, 95 + j * 26, a, 7.4, 'ink', anchor='start', bold=True) + t(400, 95 + j * 26, b, 6.8, 'ink2', anchor='end')
    for i, (n, s, icn) in enumerate([('Dashboard', 'Power BI, QuickSight', 'chart'), ('Analyst', 'plain SQL', 'user'), ('App / API', 'one endpoint', 'app')]):
        y = 56 + i * 58
        o += arrow(420, 134, 470, y + 22) + box(472, y, 150, 44, 'blue', rx=6) + ic(icn, 480, y + 10, 0.9) + t(560, y + 20, n, 7.8, 'ink', bold=True) + t(560, y + 34, s, 7, 'ink2')
    o += box(20, 250, 296, 40, 'red', rx=6) + t(168, 266, 'ETL way: copy everything into a warehouse', 7.8, 'ink', bold=True) + t(168, 280, 'hours old, duplicated, more storage cost', 7, 'ink2')
    o += box(324, 250, 296, 40, 'green', rx=6) + t(472, 266, 'Virtualization way: read in place', 7.8, 'ink', bold=True) + t(472, 280, 'live data, no copy — but slower for huge joins', 7, 'ink2')
    return o
DATAF = bigfig('Left: four sources (orders.csv, cities.parquet, crm.db SQLite, cloud sources). Middle: a virtual data layer with catalog, query planner, pushdown, join and cache, and security. Right: consumers (dashboard, analyst, app). Bottom: ETL copies data into a warehouse; virtualization reads in place.', datafig(), h=300)

picture = ('  <p>In Lessons 4.1 and 4.2 we virtualized <b>servers</b>. A server is useless without a <b>network</b> to talk on, <b>storage</b> to keep files and <b>data</b> to work on — and each of these can be virtualized the same way: a software layer hides the physical details and hands out logical pieces.</p>\n'
           '  <h3>1 · Network virtualization</h3>\n  <p>Each VM gets a <b>virtual network card</b>. A <b>virtual switch</b> inside the host connects them. To make a private network that spans many hosts, the host <b>wraps</b> each packet and adds a <b>network ID</b> before sending it over the shared physical network:</p>\n' + NETF +
           '\n  <h3>2 · Storage virtualization</h3>\n  <p>Physical disks of any size and vendor are pooled. Virtual disks are cut from the pool — and the layer adds features no single disk has:</p>\n' + STORF +
           '\n  <h3>3 · Data virtualization</h3>\n  <p>The data stays in its own systems and formats. A virtual layer presents it as tables you can query together:</p>\n' + DATAF)

# ---------------------------------------------------------------- animation 1: packet across a VPC
def hdr(k):
    """packet structure strip at bottom of frame (y 112-150)"""
    o = t(8, 120, 'The packet now:', 7, 'ink2', anchor='start', bold=True)
    parts = [('outer IP host1→host2', 'red', k >= 3 and k <= 4), ('VPC tag (VNI)', 'amber', k >= 3 and k <= 4), ('inner IP 10.10.1.5→10.10.2.7 :443', 'blue', True), ('data', 'card', True)]
    x = 8
    for lab, tn, show in parts:
        w = {'outer IP host1→host2': 90, 'VPC tag (VNI)': 56, 'inner IP 10.10.1.5→10.10.2.7 :443': 140, 'data': 40}[lab]
        if show:
            o += box(x, 126, w - 2, 22, tn, rx=3) + t(x + w / 2 - 1, 140, lab, 6.4, 'ink', bold=True)
        else:
            o += f'<rect x="{x}" y="126" width="{w - 2}" height="22" rx="3" style="fill:none;stroke:#999;stroke-dasharray:3 3"/>'
        x += w
    return o
PN = {'vmA': (4, 30, 54, 48, 'server', 'Kitchen VM', '10.10.1.5'), 'vsw': (63, 30, 54, 48, 'shield', 'vSwitch+SG', 'host 1'),
      'map': (122, 2, 116, 24, 'dns', '', ''), 'tep1': (122, 30, 54, 48, 'chip', 'Wrap', 'Nitro card'),
      'net': (181, 30, 54, 48, 'globe', 'Underlay', 'physical'), 'tep2': (240, 30, 54, 48, 'chip', 'Unwrap', 'host 2'),
      'vmB': (299, 30, 56, 48, 'server', 'Billing VM', '10.10.2.7')}
def mapbox(hot):
    return box(122, 2, 116, 24, 'amber' if hot else 'card', rx=5) + t(180, 13, 'Mapping service', 7, 'ink', bold=True) + t(180, 22, '10.10.2.7 = VM on host 2', 6.2, 'ink2')
PN2 = {k: v for k, v in PN.items() if k != 'map'}
PS = [dict(on=['vmA'], hot='vmA', move=(58, 54, 63, 54, ''), extra=mapbox(False) + hdr(0), head='Step 1 · The VM sends a normal packet', text='The kitchen app calls billing at 10.10.2.7:443. The guest OS builds an ordinary IP', text2='packet and hands it to its virtual NIC (virtio / AWS ENA). It knows nothing more.', svc='The VM thinks it is on a plain LAN cable'),
      dict(on=['vmA', 'vsw'], hot='vsw', move=(58, 54, 66, 54, ''), extra=mapbox(False) + hdr(1), head='Step 2 · Virtual switch: firewall + route', text='Software on the host checks the security group (is outbound 443 allowed?) and the', text2='route table: 10.10.0.0/16 → “local”, so the target is inside the same VPC.', svc='AWS: security groups + VPC route table · Azure: NSG + VNet · GCP: firewall rules'),
      dict(on=['vmA', 'vsw', 'tep1'], hot='tep1', move=(90, 30, 150, 26, 'ask'), extra=mapbox(True) + hdr(2), head='Step 3 · Where does 10.10.2.7 live?', text='There is no real switch to “learn” MAC addresses. The host asks the mapping service:', text2='“In VPC vpc-55…, which physical host has 10.10.2.7?” Answer: host 2.', svc='AWS keeps this map in its control plane; Nitro caches it'),
      dict(on=['vmA', 'vsw', 'tep1'], hot='tep1', move=None, extra=mapbox(False) + hdr(3), head='Step 4 · Wrap (encapsulate) the packet', text='The original packet is put inside a new one addressed host 1 → host 2, with a tag', text2='saying which virtual network it belongs to (VXLAN VNI; AWS uses its own format).', svc='Done in hardware by the Nitro card, so the VM’s CPU is not used'),
      dict(on=['vmA', 'vsw', 'tep1', 'net', 'tep2'], hot='net', move=(176, 54, 240, 54, 'wire'), extra=mapbox(False) + hdr(4), head='Step 5 · Cross the physical network', text='Routers in the data centre see only host-to-host traffic. They never see 10.10.x', text2='addresses, so thousands of customers can reuse the same private IPs.', svc='The “underlay”; your VPC is the “overlay” on top of it'),
      dict(on=list(PN2), hot='vmB', move=(294, 54, 299, 54, ''), extra=mapbox(False) + hdr(5), head='Step 6 · Unwrap, check, deliver', text='Host 2 removes the wrapper, checks the tag is the same VPC and the billing VM’s', text2='inbound security group (443 from 10.10.1.0/24 allowed), then delivers. Done in µs.', svc='Wrong VPC tag or a blocked rule → the packet is silently dropped')]
PKT = flow_anim('A packet from the kitchen VM to the billing VM on another host', 'Six steps that make a VPC behave like a real cabled network — with no cables of its own.', 'Inside a virtual network', 'Animation: VM sends a packet, virtual switch checks the security group and route, mapping service finds the destination host, the packet is wrapped with a VPC tag, crosses the physical network, then is unwrapped, checked and delivered.', PN2, PS, hid='vpcpkt')

# ---------------------------------------------------------------- animation 2: thin / CoW / snapshot
def blocks(x, y, n, filled, tone, w=16, lab=''):
    o = ''
    for i in range(n):
        o += box(x + (i % 8) * (w + 2), y + (i // 8) * (w + 2), w, w, tone if i in filled else 'card', rx=2)
    return o
def st_frame(k):
    o = t(180, 12, ['Thin provisioning', 'Copy-on-write linked clone', 'Snapshot (point in time)'][k], 9, 'ink', bold=True)
    if k == 0:
        o += t(80, 30, 'What the VM sees: 10 GiB disk', 7.4, 'ink', bold=True) + blocks(8, 36, 16, set(), 'blue')
        o += t(270, 30, 'What the pool really stores', 7.4, 'ink', bold=True) + blocks(200, 36, 16, {0, 1}, 'green')
        o += packet(150, 46, 200, 46, 'write') + t(270, 90, 'only 2 blocks used', 7.4, 'green', bold=True)
        o += t(180, 120, 'Our lab: virtual size 10 GiB · disk size 196 KiB', 8, 'ink', bold=True) + t(180, 136, 'Risk: if every VM fills its disk, the pool runs out (overcommit).', 7.2, 'red')
    if k == 1:
        o += t(80, 30, 'base.qcow2 (read-only)', 7.4, 'ink', bold=True) + blocks(8, 36, 16, set(range(10)), 'amber')
        o += t(270, 30, 'clone1.qcow2 (own changes)', 7.4, 'ink', bold=True) + blocks(200, 36, 16, {3}, 'green')
        o += packet(200, 46, 150, 46, 'read') + t(180, 100, 'read: block not in clone → read from base', 7.4, 'ink')
        o += t(180, 114, 'write: copy block into clone, change it there; base never changes', 7.4, 'ink')
        o += t(180, 136, 'Our lab: clone of a 10 GiB disk = 196 KiB, created instantly.', 8, 'ink', bold=True)
    if k == 2:
        o += t(80, 30, 'Volume now', 7.4, 'ink', bold=True) + blocks(8, 36, 16, {0, 1, 2, 3, 4, 5}, 'blue')
        o += t(270, 30, 'Snapshot = frozen block map', 7.4, 'ink', bold=True) + blocks(200, 36, 16, {0, 1, 2, 3, 4}, 'violet')
        o += packet(150, 46, 200, 46, 'freeze') + t(180, 100, 'After the snapshot, changed blocks are written to new places;', 7.4, 'ink')
        o += t(180, 114, 'the snapshot still points to the old ones. Next snapshot saves only changes.', 7.4, 'ink')
        o += t(180, 136, 'AWS EBS snapshots: incremental, stored in S3, restorable in another AZ.', 8, 'ink', bold=True)
    return o
STS = [('Thin provisioning', 'A disk promises a size but takes space only when blocks are written.', 'Lets you hand out more than you own — watch the pool’s real usage.'),
       ('Copy-on-write linked clone', 'A new disk reads from a shared base image and stores only its own changes.', 'How clouds launch 100 VMs from one AMI/image in seconds.'),
       ('Snapshot', 'Freeze the block map; later writes go to new blocks, so the old view stays.', 'Backup before an upgrade; roll back in minutes.')]
STA = anim_one('How it works', 'Three tricks every storage virtualization layer uses', 'Watch which blocks are really stored. These three tricks explain cheap clones, fast launches and instant snapshots.', 'Thin, copy-on-write, snapshot', 'Animation: a 10 GiB thin disk storing only 2 blocks; a linked clone reading from a base image and writing its own block; a snapshot freezing the block map while new writes go elsewhere.', cap_frames([st_frame(k) for k in range(3)], STS), [x[0] + '.' for x in STS], delay=6500, hid='stor')

# ---------------------------------------------------------------- animation 3: federated query
FN = {'q': (4, 54, 58, 50, 'user', 'Analyst', 'one SQL'), 'pl': (74, 54, 64, 50, 'gear', 'Planner', 'split query'),
      's1': (150, 2, 64, 46, 'disk', 'orders.csv', 'CSV'), 's2': (150, 54, 64, 50, 'disk', 'cities.parquet', 'Parquet'), 's3': (150, 108, 64, 46, 'db', 'crm.db', 'SQLite'),
      'j': (226, 54, 60, 50, 'app', 'Join', 'in memory'), 'r': (296, 54, 60, 50, 'chart', 'Result', '3 rows')}
FS = [dict(on=['q', 'pl'], hot='pl', move=(62, 79, 74, 79, ''), head='Step 1 · One query arrives', text='The analyst writes one SELECT that joins orders, cities and ratings — as if all', text2='three were tables in one database. No one copied anything.', svc='Athena federated query · Synapse serverless · BigQuery external tables · Denodo · Trino'),
      dict(on=['q', 'pl'], hot='pl', move=None, head='Step 2 · Catalog + plan', text='The layer looks up each table: orders → CSV file, cities → Parquet file,', text2='ratings → SQLite. It plans a separate small read for each source.', svc='The catalog: AWS Glue Data Catalog, Unity Catalog, Hive Metastore'),
      dict(on=['q', 'pl', 's1', 's2', 's3'], hot='s2', move=(138, 79, 150, 79, 'read'), head='Step 3 · Push work down to each source', text='Each source does what it is good at: Parquet returns only the needed columns,', text2='the database filters rows itself. Less data travels.', svc='“Predicate and projection pushdown”'),
      dict(on=['q', 'pl', 's1', 's2', 's3', 'j'], hot='j', move=(214, 79, 226, 79, 'rows'), head='Step 4 · Join the pieces', text='Rows from the three sources are joined on city and order_id and grouped by zone,', text2='in memory, by the virtual layer.', svc='Heavy joins of huge tables are slow here — that is when you build a warehouse'),
      dict(on=list(FN), hot='r', move=(286, 79, 296, 79, ''), head='Step 5 · Return one answer', text='West · Pune 330, West · Mumbai 310, North · Delhi 300 — live, from the', text2='original files. Change the CSV and the next query sees it.', svc='Our lab result (DuckDB, real output)')]
FED = flow_anim('One SQL query across three formats', 'How a data-virtualization engine answers a query without moving the data first.', 'Federated query', 'Animation: analyst sends one SQL query; planner looks up the catalog; the query is pushed down to a CSV file, a Parquet file and a SQLite database; results are joined; one answer is returned.', FN, FS, hid='fed')

# ---------------------------------------------------------------- parts
parts = '\n  <h3>Compare: three kinds side by side</h3>\n' + table(['', 'Network', 'Storage', 'Data'], [
    ['Hides', 'cables, switches, routers', 'disks, arrays, vendors', 'formats and locations of data'],
    ['Hands out', 'virtual networks, subnets, firewalls', 'virtual disks, file shares, buckets', 'virtual tables / views'],
    ['Key trick', 'encapsulation + tag', 'pooling + block mapping (CoW)', 'catalog + query pushdown'],
    ['Our lab', 'netns + veth: ping 0% loss', 'LVM pool 392 MB; 10 GiB → 196 KiB', 'CSV + Parquet + SQLite in 1 query'],
    ['In AWS', 'VPC, subnets, SG, ENI', 'EBS, EFS, S3, snapshots', 'Athena federated, Redshift Spectrum']], minw=620)

DEEP = ('  <h3>Nitro Card for VPC: where AWS does network virtualization</h3>\n' + wwu([
    ('Nitro Card for VPC', 'A PCIe card in every modern EC2 host that contains the virtual switch, security groups, route lookup and encapsulation logic. The instance sees it as an ENA network device.', 'Doing this in hypervisor software used CPU that customers paid for and added jitter. Moving it to dedicated hardware frees the CPU and gives 25–200 Gbps.', 'Every Nitro-based instance (all current families). It is why security groups are enforced even if the VM is hacked — the rules are outside the VM.'),
    ('Nitro Card for EBS', 'A second card that turns network storage into an NVMe disk for the instance and encrypts data on the way.', 'An EBS volume is far away on the network; the instance must still see a fast local-looking disk.', 'Every EBS volume on Nitro instances shows up as /dev/nvme…'),
    ('Mapping service', 'A control-plane database of “which VPC IP lives on which physical host”.', 'Overlays have no switches to learn addresses, so someone must know where every VM is.', 'Consulted when a host first sends to a destination; answers cached on the Nitro card.')]) +
    '\n  <h3>VLAN vs VXLAN in numbers</h3>\n' + table(['', 'VLAN (802.1Q)', 'VXLAN overlay'], [
    ['ID size', '12 bits', '24 bits'], ['How many networks', '4,094', '≈16.7 million'], ['Spans', 'one layer-2 domain', 'any IP network, racks, data centres'],
    ['Extra header', '4 bytes', '≈50 bytes (outer Ethernet+IP+UDP+VXLAN)'], ['Created by', 'switch configuration', 'software/API']], minw=520) +
    '\n  <p><b>Why MTU matters:</b> the wrapper adds bytes. If a physical network allows 1,500-byte packets and the overlay adds 50, either the VM uses a smaller MTU or the physical network uses <b>jumbo frames</b>. AWS supports 9,001-byte MTU inside a VPC, but traffic leaving through an internet gateway uses 1,500 — a classic cause of “small requests work, big ones hang”.</p>\n'
    '  <h3>How an EBS volume actually works</h3>\n  <p>An EBS volume is not a disk in your server. It is a <b>virtual block device</b> whose blocks are spread over many storage servers in the same Availability Zone and <b>replicated</b> inside that AZ. Your instance reaches it over the network through the Nitro card. Consequences you must remember:</p>\n'
    '  <ul><li><b>An EBS volume lives in one AZ</b> — it can attach only to instances in that AZ. To move it, snapshot it and create a new volume in the other AZ (our AWS lab does exactly this).</li><li><b>Snapshots are incremental and stored in S3</b>, which is regional — so a snapshot can be restored in any AZ, or copied to another Region for disaster recovery.</li><li><b>Performance is a setting</b>: gp3 gives 3,000 IOPS and 125 MB/s baseline whatever the size, and you can buy more; on old gp2 IOPS grew with size.</li></ul>\n'
    '  <h3>Data virtualization vs ETL vs data lake</h3>\n' + table(['', 'Data virtualization', 'ETL into a warehouse', 'Data lake (+ query engine)'], [
    ['Data copied?', 'no', 'yes, transformed', 'yes, raw files in one place'], ['Freshness', 'live', 'as of last load', 'as of last ingest'],
    ['Big heavy joins', 'slow (network, sources)', 'fast', 'fast with Parquet'], ['Best for', 'quick integration, prototypes, small/medium data, compliance (“data must not move”)', 'reporting at scale', 'analytics on large history'],
    ['Cloud example', 'Athena federated query, Synapse serverless', 'Redshift, Synapse dedicated, BigQuery', 'S3 + Athena, ADLS + Synapse, GCS + BigQuery']], minw=640))

clouds = vendor_tabs('<p><b>AWS:</b> network = <b>VPC</b> (subnets, route tables, security groups, ENIs), Transit Gateway, PrivateLink — all on Nitro cards. Storage = <b>EBS</b> (block), <b>EFS/FSx</b> (file), <b>S3</b> (object), snapshots and AMIs. Data = <b>Athena Federated Query</b>, Redshift Spectrum, Glue Data Catalog.</p>',
    '<p><b>Azure:</b> network = <b>Virtual Network (VNet)</b>, NSGs, VNet peering, Accelerated Networking. Storage = <b>Managed Disks</b>, <b>Azure Files</b>, <b>Blob Storage</b>. Data = <b>Synapse serverless SQL</b> (query files in place), Microsoft Fabric OneLake shortcuts.</p>',
    '<p><b>Google Cloud:</b> network = <b>VPC</b> (global — one VPC spans all regions, subnets are regional), firewall rules, Andromeda SDN. Storage = <b>Persistent Disk / Hyperdisk</b>, <b>Filestore</b>, <b>Cloud Storage</b>. Data = <b>BigQuery external tables, federated queries, BigQuery Omni</b> (query AWS/Azure data in place).</p>') + \
    cloud3([['Virtual network', 'VPC', 'Virtual Network (VNet)', 'VPC (global)'], ['Virtual firewall', 'Security group, NACL', 'NSG', 'Firewall rules'], ['Virtual disk', 'EBS', 'Managed Disks', 'Persistent Disk / Hyperdisk'],
            ['Shared files', 'EFS, FSx', 'Azure Files', 'Filestore'], ['Object store', 'S3', 'Blob Storage', 'Cloud Storage'], ['Query data in place', 'Athena (federated)', 'Synapse serverless', 'BigQuery external / Omni']])

proof = [
    ('Step 1 · Two virtual networks and a virtual cable', code('bash', 'terminal (root)', 'ip netns add kitchen; ip netns add billing\nip link add veth-k type veth peer name veth-b\nip link set veth-k netns kitchen; ip link set veth-b netns billing\nip -n kitchen addr add 10.10.0.1/24 dev veth-k\nip -n billing addr add 10.10.0.2/24 dev veth-b\nip -n kitchen link set veth-k up; ip -n billing link set veth-b up\nip netns list; ip -n kitchen -brief addr show veth-k\nip netns exec kitchen ping -c 2 -W 1 10.10.0.2 | tail -3', sec('== 1)', '== 2)')), 'Two isolated network stacks, joined by a <b>veth pair</b> — a virtual cable with one end in each. 0% loss at 0.04 ms: no hardware moved a single bit; the kernel did it.'),
    ('Step 2 · The host cannot see them', code('bash', 'terminal', 'ip -brief link | grep -c veth', sec('== 2)', '== 3)')), 'Zero. The interfaces exist only inside their namespaces — isolation, the first promise of network virtualization. Docker and Kubernetes connect every container exactly like this.'),
    ('Step 3 · Pool two disks into one (LVM)', code('bash', 'terminal (root)', 'truncate -s 200M d1.img d2.img\nL1=$(losetup -f --show d1.img); L2=$(losetup -f --show d2.img)\npvcreate $L1 $L2; vgcreate pool $L1 $L2\npvs -o pv_name,vg_name,pv_size; vgs -o vg_name,pv_count,vg_size', sec('== 3)', '== 4)')), 'Two separate 196 MB “disks” became one 392 MB pool. From here you would cut logical volumes of any size (<code>lvcreate</code>), even bigger than any single disk.'),
    ('Step 4 · A 10 GiB disk that uses 196 KiB', code('bash', 'terminal', 'qemu-img create -f qcow2 base.qcow2 10G\nqemu-img create -f qcow2 -b base.qcow2 -F qcow2 clone1.qcow2\nqemu-img info clone1.qcow2', sec('== 4)')), 'Thin provisioning and copy-on-write together: the clone promises 10 GiB, stores only its own changes and reads the rest from <code>base.qcow2</code>.'),
    ('Step 5 · One query, three sources (DuckDB)', code('sql', 'duckdb', "INSTALL sqlite; LOAD sqlite; ATTACH 'crm.db' AS crm (TYPE sqlite);\nSELECT c.zone, o.city, count(*) AS orders, sum(o.amount) AS revenue,\n       round(avg(r.stars),1) AS avg_stars\nFROM 'orders.csv' o\nJOIN 'cities.parquet' c USING (city)\nJOIN crm.ratings r USING (order_id)\nGROUP BY ALL ORDER BY revenue DESC;", secd('== 5)')), 'A CSV file, a Parquet file and a SQLite database answered as one database — nothing was imported. That is data virtualization (federation) in its simplest form.')]

prac = practical('Part A runs on any Linux machine or WSL2 as root (install: <code>sudo apt install iproute2 iputils-ping lvm2 qemu-utils</code>, <code>pip install duckdb</code>). Part B is the same ideas in AWS with the CLI. <b>Our outputs for Part B come from the moto AWS emulator</b> — IDs will differ on your account; everything in Part B is free except a few cents for the EBS volume and snapshot if left running.', [
    ('A1 · Build a two-room network', code('bash', 'terminal', 'sudo ip netns add kitchen; sudo ip netns add billing\nsudo ip link add veth-k type veth peer name veth-b\nsudo ip link set veth-k netns kitchen; sudo ip link set veth-b netns billing\nsudo ip -n kitchen addr add 10.10.0.1/24 dev veth-k; sudo ip -n kitchen link set veth-k up\nsudo ip -n billing addr add 10.10.0.2/24 dev veth-b; sudo ip -n billing link set veth-b up\nsudo ip netns exec kitchen ping -c 2 10.10.0.2'), 'Expect 0% packet loss. Now try pinging 10.10.0.2 from the host: it fails — the host is not in that network.'),
    ('A2 · Add a firewall rule inside one room', code('bash', 'terminal', 'sudo ip netns exec billing iptables -A INPUT -p icmp -j DROP\nsudo ip netns exec kitchen ping -c 2 -W 1 10.10.0.2   # now 100% loss\nsudo ip netns del kitchen; sudo ip netns del billing'), 'A software firewall on a software network — the same idea as a security group.'),
    ('A3 · Thin disks and linked clones', code('bash', 'terminal', 'qemu-img create -f qcow2 base.qcow2 10G\nqemu-img create -f qcow2 -b base.qcow2 -F qcow2 clone1.qcow2\nqemu-img info clone1.qcow2 | grep -E "virtual size|disk size|backing"\nls -lh *.qcow2'), 'Virtual size 10 GiB, real size a few hundred KiB.'),
    ('A4 · Query three formats at once', code('bash', 'terminal', 'python3 l43_data.py   # script in tools/authoring/src/cloud-fundamentals/lab/jobs/m4'), 'Creates orders.csv, cities.parquet and crm.db, then joins them in one query.'),
    ('B1 · Create a VPC (virtual network)', code('bash', 'terminal', "aws ec2 create-vpc --cidr-block 10.10.0.0/16 \\\n  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=tiffingo-vpc}]' \\\n  --query Vpc.VpcId --output text", seca('== 1)', '== 2)')), 'A private network with 65,536 addresses exists in a second. Nothing physical was installed.'),
    ('B2 · Two subnets in two AZs', code('bash', 'terminal', 'aws ec2 create-subnet --vpc-id $VPC --cidr-block 10.10.1.0/24 --availability-zone ap-south-1a\naws ec2 create-subnet --vpc-id $VPC --cidr-block 10.10.2.0/24 --availability-zone ap-south-1b\naws ec2 describe-subnets --filters Name=vpc-id,Values=$VPC \\\n  --query \'Subnets[].[CidrBlock,AvailabilityZone,AvailableIpAddressCount]\' --output table', seca('== 2)', '== 3)')), '251, not 256: AWS reserves 5 addresses in every subnet (network, router, DNS, future, broadcast).'),
    ('B3 · The virtual router', code('bash', 'terminal', "aws ec2 describe-route-tables --filters Name=vpc-id,Values=$VPC \\\n  --query 'RouteTables[].Routes[].[DestinationCidrBlock,GatewayId,State]' --output table", seca('== 3)', '== 4)')), 'The <code>local</code> route means “anything in 10.10.0.0/16 is delivered inside the VPC” — that is step 2 of the packet animation.'),
    ('B4 · A virtual firewall', code('bash', 'terminal', 'SG=$(aws ec2 create-security-group --group-name kitchen-sg --description "kitchen API" \\\n  --vpc-id $VPC --query GroupId --output text)\naws ec2 authorize-security-group-ingress --group-id $SG --protocol tcp --port 443 --cidr 10.10.2.0/24', seca('== 4)', '== 5)')), 'Only the billing subnet may reach the kitchen API on 443. The rule is enforced on the Nitro card, outside the VM.'),
    ('B5 · A virtual disk from the storage pool', code('bash', 'terminal', 'aws ec2 create-volume --availability-zone ap-south-1a --size 20 --volume-type gp3', seca('== 5)', '== 6)')), 'A 20 GiB block device carved from the AZ’s storage fleet. It is AZ-bound.'),
    ('B6 · Move it to another AZ via a snapshot', code('bash', 'terminal', 'SN=$(aws ec2 create-snapshot --volume-id $V --description "before menu upgrade" \\\n  --query SnapshotId --output text)\naws ec2 wait snapshot-completed --snapshot-ids $SN    # real account: wait\naws ec2 create-volume --availability-zone ap-south-1b --snapshot-id $SN --volume-type gp3', seca('== 6)', '== 7)')), 'The copy-on-write snapshot (stored in S3) became a new volume in ap-south-1b — the only way to “move” an EBS volume between AZs.')],
    cleanup='<code>aws ec2 delete-volume</code> (both volumes), <code>delete-snapshot</code>, <code>delete-security-group</code>, <code>delete-subnet</code> ×2, <code>delete-vpc</code>. Snapshots and unattached volumes are billed every month until deleted. Locally: <code>ip netns del</code>, <code>vgremove</code>, <code>losetup -d</code>, delete the .img and .qcow2 files.')

mist = mistakes([
    ['Same CIDR (e.g. 10.0.0.0/16) in every VPC and office network.', 'Default examples copied everywhere.', 'Plan non-overlapping ranges up front; overlapping VPCs cannot be peered or routed later.'],
    ['Thinking a security group is a box you can “see” in the network.', 'On-premises firewalls are physical.', 'It is a rule set enforced at each instance’s virtual NIC. Think “per-instance stateful firewall”.'],
    ['Big transfers hang while small requests work.', 'MTU mismatch after encapsulation or VPN (jumbo 9,001 inside, 1,500 outside).', 'Check path MTU; lower the MTU on the interface or allow ICMP “fragmentation needed”.'],
    ['Overcommitting thin disks and running the pool out of space.', 'Thin disks look free until they fill.', 'Monitor real pool usage; set alerts at 70–80%; know your overcommit ratio.'],
    ['Trying to attach an EBS volume to an instance in another AZ.', 'EBS is AZ-scoped.', 'Snapshot → create volume in the target AZ → attach (practical B6).'],
    ['Treating snapshots as free.', 'They are incremental but accumulate.', 'Use Amazon Data Lifecycle Manager / retention rules to delete old ones.'],
    ['Using data virtualization for huge daily reports.', 'It is easy to start with.', 'Use it for live/small queries; move heavy repeated workloads to a warehouse or lake.'],
    ['Joining sources with different meanings (city codes vs names).', 'Virtual layer hides the source.', 'Define a semantic layer and clean keys before federating.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA (Linux & Cloud)', 'Types of virtualization: server, network, storage, data, desktop, application.'], ['AWS CLF-C02', 'VPC, subnets, security groups vs NACLs; EBS vs EFS vs S3; snapshots.'], ['AZ-900', 'Virtual networks, NSGs; disk, file and blob storage.'], ['Google Cloud Digital Leader', 'VPC (global), storage classes; BigQuery querying data in place.']], minw=520) + '\n  <h3>Exam-style questions with explanations</h3>\n' + \
    qx('1. Which technology lets millions of isolated customer networks share one physical data-centre network?', ['VLAN', 'Overlay networks with encapsulation (VXLAN-like)', 'RAID', 'DNS'], 1, 'VLANs have only 4,094 IDs. Overlays wrap packets with a 24-bit (or larger) network ID and carry them over the physical underlay.') + \
    qx('2. An EBS volume in ap-south-1a must be used by an instance in ap-south-1b. What do you do?', ['Attach it directly', 'Create a snapshot and restore it as a new volume in 1b', 'Change the volume’s AZ attribute', 'Use a security group'], 1, 'EBS volumes are AZ-scoped; snapshots live in S3 (regional) and can be restored in any AZ of the Region.') + \
    qx('3. A 10 GiB virtual disk uses only 196 KiB on the host. This is…', ['compression', 'thin provisioning', 'RAID 0', 'deduplication only'], 1, 'Space is allocated only when blocks are written.') + \
    qx('4. Which is an example of data virtualization?', ['Copying tables nightly into a warehouse', 'Querying S3 and an RDS database together with Athena Federated Query without moving data', 'Taking an EBS snapshot', 'Creating a VLAN'], 1, 'Data virtualization queries data in place across sources; ETL copies it.') + \
    qx('5. Why does a /24 subnet in AWS show 251 available addresses?', ['AWS bug', 'AWS reserves 5 addresses per subnet', 'Only 251 instances are allowed per VPC', 'IPv6 takes 5'], 1, 'The first four (network, VPC router, DNS, future use) and the last (broadcast) are reserved.') + \
    qx('6. Where are AWS security group rules enforced on Nitro instances?', ['Inside the guest OS firewall', 'On the Nitro networking card / virtualization layer, outside the instance', 'In the internet gateway', 'In Route 53'], 1, 'That is why a compromised OS cannot simply turn them off.')

proj = miniproject('Mini project: a mini virtual data centre on one Linux machine',
    'Combine all three kinds of virtualization: two isolated “VM rooms” on a virtual switch, disks from a pool, and one report over three data sources.',
    ['<b>Network:</b> create namespaces <code>kitchen</code>, <code>billing</code> and <code>ops</code>; create a Linux bridge <code>br0</code> (<code>ip link add br0 type bridge</code>) and connect each namespace to it with a veth pair — a virtual switch with three ports. Give them 10.10.0.1–3/24.',
     '<b>Firewall:</b> in <code>billing</code>, allow ICMP only from 10.10.0.3 (ops) with iptables. Prove kitchen → billing fails and ops → billing works.',
     '<b>Storage:</b> make three 200 MB loop disks, put them in volume group <code>pool</code>, check <code>vgs</code> shows ~588 MB.',
     '<b>Images:</b> make a 20 GiB qcow2 base and three linked clones (<code>kitchen.qcow2</code>, <code>billing.qcow2</code>, <code>ops.qcow2</code>); record real sizes with <code>du -h</code>.',
     '<b>Data:</b> extend <code>l43_data.py</code> with a fourth source (a JSON file of delivery times) and produce revenue and average delivery time per zone in one query.',
     '<b>Report:</b> write README.md with a diagram, the outputs, and one sentence per step naming the AWS service that does the same job (bridge → VPC, iptables → security group, LVM → EBS, qcow2 clone → AMI, DuckDB → Athena).',
     '<b>Clean up:</b> delete namespaces, bridge, volume group, loop devices and files.'],
    'Ping matrix (who can reach whom), vgs output, du sizes of clones, and the federated report table.', 'This lesson + Linux networking + SQL.')

assemble_v2(HERE, story_h2='Kitchen, billing and three kinds of data on shared machines', hook_html=hk,
    narration='TiffinGo now runs on a few big hosts. The kitchen and billing teams share them; disks fill unevenly; and the numbers management wants are spread over files and databases.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Network, storage and data virtualization',
    formal='<b>Network virtualization</b> combines physical network resources and functionality into software-based logical networks — virtual NICs, switches, routers and firewalls — decoupled from the underlying hardware, typically using overlays and software-defined networking. <b>Storage virtualization</b> pools physical storage from multiple devices into what appears to be a single storage resource, from which logical volumes, file systems or object stores are presented, independent of physical location. <b>Data virtualization</b> provides an abstraction layer that lets applications retrieve and manipulate data from multiple heterogeneous sources through a unified view, without requiring technical details about format or physical location and without copying it.',
    simple='Put software between users and the physical network, disks or data sources, so they get private networks, virtual disks and one combined view of data — while the real hardware and files stay hidden underneath.',
    interview=['“Network virtualization creates logical networks in software on top of a shared physical network. VMs get virtual NICs, a virtual switch forwards traffic, and overlays like VXLAN wrap each packet with a network ID so many private networks — like AWS VPCs — share one physical fabric.”', '“Storage virtualization pools many physical disks and presents virtual volumes, adding thin provisioning, snapshots, replication and tiering. EBS, SAN arrays and Linux LVM are examples.”', '“Data virtualization lets you query many sources as one without copying them — for example Athena federated query, or DuckDB joining a CSV, a Parquet file and a database in one SQL statement, which I did in a lab.”'],
    terms_rows=[('vNIC / ENI', 'Virtual network card of a VM.'), ('Virtual switch', 'Software switch inside a host.'), ('VLAN', '12-bit tag, 4,094 LANs on one switch.'), ('Overlay / VXLAN', 'Wrap packets with a 24-bit network ID.'), ('Underlay', 'The physical network carrying overlays.'), ('SDN', 'Central software controls the network.'), ('LVM', 'Linux disk pooling: PV → VG → LV.'), ('Thin provisioning', 'Allocate space only when written.'), ('Copy-on-write', 'Share blocks, store only changes.'), ('Federated query', 'One query across several sources.')],
    exam='Exam favourite: “EBS volume in another AZ?” → snapshot and restore. “Firewall at the instance level?” → security group (stateful); “at the subnet level?” → network ACL (stateless).',
    picture_h2='Three things to virtualize after the server', picture_html=picture,
    how_h2='Follow one packet through a VPC', how_intro='The most important mechanism of this lesson in full detail — six steps from one VM to another on a different host.', how_anim=PKT,
    parts_h2='Network, storage and data compared', parts_html=parts,
    after_picture=[('types', 'Types, one by one', 'Eight types inside network, storage and data virtualization', build_types(PKT, STA, FED))], lv='',
    myth_rows=[('A VPC is a set of real switches reserved for me.', 'It is software rules and encapsulation on shared hardware.', 'Packet animation, steps 3–5.'), ('A 10 GiB virtual disk uses 10 GiB.', 'Thin disks use only written blocks.', 'Proof step 4: 196 KiB.'), ('To report across systems you must copy data first.', 'Federated queries read in place.', 'Proof step 5.'), ('EBS is a disk inside my server.', 'It is network storage reached via the Nitro card.', 'Deep dive.')],
    extra_secs=[('deep', 'Deep dive', 'Nitro cards, VLAN vs VXLAN, MTU, how EBS works, and virtualization vs ETL', DEEP)],
    clouds_html=clouds, proof_h2='Real proof: virtual network, pool, thin disk and federated query', proof_intro='All outputs are real, from our Ubuntu 24.04 lab machine on 10 Nov 2026 (iproute2, LVM2, qemu-img, DuckDB).', proof_steps=proof,
    practical_html=PRAC, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Explain network virtualization: vNIC, virtual switch, VLAN, overlay, SDN, NFV, VPC.', 'Choose between block, file and object storage for a workload.', 'Do each practical step both in a UI and with the CLI.', 'Trace a packet between two VMs on different hosts in a VPC.', 'Explain storage virtualization: pooling, LVM, SAN/NAS, object storage, thin provisioning, snapshots.', 'Explain data virtualization and when to choose it over ETL.', 'Create a VPC, subnets, a security group, a volume and a snapshot with the AWS CLI.'],
    next_html='<a href="../04-vm-provisioning-and-migration/">4.4 VM provisioning, images and migration</a>.',
    pre='<b>Before you start:</b> <a href="../02-server-hardware-and-os-level-virtualization/">4.2 Server, hardware and OS-level virtualization</a>.')
