"""Lesson 4.3 — types of network, storage and data virtualization, one by one."""
from cloudkit import *

def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)

def mapfig():
    o = t(320, 16, 'Network, storage and data virtualization — the types inside each', 11, 'ink', bold=True)
    cols = [('Network', 'violet', [('1', 'VLAN', 'tag splits one switch'), ('2', 'Overlay (VXLAN / VPC)', 'wrap + tag over IP'), ('3', 'SDN', 'central software brain'), ('4', 'NFV', 'network boxes as software')]),
            ('Storage', 'amber', [('5', 'Block', 'virtual disks (EBS, SAN)'), ('6', 'File', 'shared folders (EFS, NAS)'), ('7', 'Object', 'buckets over HTTP (S3)')]),
            ('Data', 'red', [('8', 'Data virtualization', 'one query, many sources')])]
    for c, (h, tn, items) in enumerate(cols):
        x = 20 + c * 208
        o += box(x, 30, 196, 26, tn, rx=6) + t(x + 98, 47, h + ' virtualization', 8.8, 'ink', bold=True)
        for i, (n, a, b) in enumerate(items):
            y = 64 + i * 50
            o += box(x, y, 196, 44, 'card', rx=6) + pin(x + 14, y + 14, n) + t(x + 28, y + 18, a, 8.4, 'ink', anchor='start', bold=True) + t(x + 10, y + 36, b, 7, 'ink2', anchor='start')
    o += t(320, 278, 'Network types answer “how do we separate traffic?”; storage types “how is capacity presented?”; data virtualization “how do we query without copying?”', 7.4, 'ink2')
    return o
MAP = bigfig('Map: network virtualization types 1 VLAN, 2 overlay (VXLAN/VPC), 3 SDN, 4 NFV; storage virtualization types 5 block, 6 file, 7 object; data virtualization type 8.', mapfig(), h=290)

# ---------------------------------------------------------------- 1 VLAN
def a_vlan(k):
    o = t(180, 12, ['One switch, everyone mixed', 'Ports get VLAN IDs', 'Tagged trunk carries both'][k], 9, 'ink', bold=True)
    o += box(110, 60, 140, 30, 'card', rx=5) + t(180, 79, 'one physical switch', 8, 'ink', bold=True)
    pcs = [('Kitchen PC', 'blue', 10), ('Kitchen PC', 'blue', 10), ('Billing PC', 'violet', 20), ('Billing PC', 'violet', 20)]
    for i, (n, tn, v) in enumerate(pcs):
        x = 10 + i * 88
        o += box(x, 112, 76, 30, tn if k >= 1 else 'card', rx=4) + t(x + 38, 126, n, 7, 'ink', bold=True) + (t(x + 38, 137, f'VLAN {v}', 6.6, 'ink2') if k >= 1 else '')
        o += f'<path d="M{x + 38},112 L180,90" style="stroke:#999;stroke-width:1.2"/>'
    if k == 0:
        o += t(180, 40, 'every PC hears every broadcast ⚠', 7.8, 'red', bold=True)
    if k == 1:
        o += t(180, 40, 'kitchen frames never reach billing ports', 7.8, 'green', bold=True)
    if k == 2:
        o += box(270, 28, 80, 26, 'amber', rx=4) + t(310, 45, 'router / host', 7, 'ink', bold=True) + packet(250, 70, 300, 54, 'tag 10|20')
    return o
A_VLAN = cap([a_vlan(k) for k in range(3)], [('One switch, everyone mixed', 'All PCs on one switch share one network: broadcasts reach everyone', 'and billing traffic is visible to kitchen machines.'), ('Ports get VLAN IDs', 'The admin puts kitchen ports in VLAN 10 and billing in VLAN 20; the switch', 'only forwards frames between ports of the same VLAN.'), ('A tagged trunk carries both', 'Between switches (or to a server/hypervisor) one “trunk” link carries both,', 'each frame stamped with a 4-byte 802.1Q tag holding its VLAN ID.')],
    'VLANs in action', 'Splitting one office switch into separate networks.', 'VLAN', 'Animation: one switch with mixed PCs; ports assigned VLAN 10 and 20; a tagged trunk carries both VLANs to a router.', 't1anim')
T1 = vtype(1, 'VLAN (virtual LAN)', 'violet',
    'A <b>VLAN</b> divides one physical layer-2 switched network into multiple isolated logical networks by assigning switch ports to VLAN IDs and tagging Ethernet frames with a 12-bit identifier (IEEE 802.1Q), so devices in different VLANs cannot communicate without a router.',
    'One office floor with coloured badges: kitchen staff with blue badges can only enter blue rooms, billing staff with violet badges only violet rooms — same building, same corridors, separate access.',
    'TiffinGo’s head office has one switch for 40 PCs. Billing PCs handle card data, so the network admin puts them in VLAN 20 and kitchen PCs in VLAN 10; the hypervisor host’s uplink is a trunk carrying both, so VMs can be placed in either.',
    'Every managed switch (Cisco, Juniper, Aruba, TP-Link); hypervisor port groups (VMware vSwitch VLAN IDs, Linux bridge VLAN filtering, Hyper-V VLAN ID). Clouds do not expose VLANs to customers — they use overlays (type 2).',
    '', A_VLAN,
    'separating departments, guest Wi-Fi, voice phones or hypervisor management traffic inside one site.',
    'you need thousands of tenants or networks that span data centres — 4,094 IDs and one layer-2 domain are not enough.',
    plain='One real network switch is set up so that it behaves like several separate switches. Computers in one group cannot see traffic of another group, even though they are plugged into the same box.',
    how=[('Assign ports', 'The admin sets switch port 1–20 to VLAN 10 (kitchen) and 21–40 to VLAN 20 (billing).'), ('Forward within a VLAN only', 'The switch keeps a separate MAC-address table per VLAN and floods broadcasts only to ports of the same VLAN.'), ('Tag on trunks', 'Links that carry several VLANs (switch-to-switch, switch-to-hypervisor) add a 4-byte 802.1Q tag with the 12-bit VLAN ID to each frame.'), ('Hypervisor reads tags', 'The virtual switch on a host delivers tagged frames only to VMs in the matching port group.'), ('Route between VLANs', 'To talk across VLANs, traffic must go through a router or firewall, where rules apply.')],
    words=[('layer 2', 'the Ethernet level: switching by MAC address'), ('MAC address', 'a network card’s hardware address'), ('broadcast', 'a message sent to every device on the network'), ('trunk', 'a link carrying several VLANs at once'), ('802.1Q', 'the standard for VLAN tags')],
    diff=table(['', 'VLAN', 'Overlay (VXLAN / VPC)', 'Physically separate switches'], [['ID size', '12 bits (4,094)', '24 bits (~16.7 million)', 'n/a'], ['Spans', 'one layer-2 domain', 'any IP network', 'one building'], ['Created by', 'switch config', 'software / API', 'buying hardware'], ['Cost', 'free on managed switches', 'software', 'high']], minw=560),
    where=['Office and campus networks', 'Hypervisor host networking (management, storage, VM traffic)', 'Guest Wi-Fi isolation', 'Data-centre racks'],
    realworld='Almost every enterprise office and campus — banks, hospitals, universities — separates staff, guest Wi-Fi, CCTV and IP phones into different VLANs on the same switches, and VMware/Hyper-V hosts carry VM networks as tagged VLANs on their uplinks.',
    pro='The 4,094 limit is why public clouds abandoned VLANs for customer networks: a cloud with a million customers would run out of IDs on day one. VXLAN’s 24-bit VNI was designed exactly for that.')

# ---------------------------------------------------------------- 2 overlay (PKT anim from lesson)
def T2(PKT):
    return vtype(2, 'Overlay networks (VXLAN, Geneve, cloud VPCs)', 'violet',
        'An <b>overlay network</b> is a virtual network built on top of an existing IP network (the underlay) by <b>encapsulating</b> each packet — wrapping the original frame inside a new UDP/IP packet with a virtual-network identifier — so that many isolated layer-2 or layer-3 networks can share the same physical infrastructure and span racks and data centres.',
        'Courier vans on a highway: each company’s parcels go into sealed vans labelled with the company’s name. The highway only sees vans going from depot A to depot B; at the depot the van is opened and parcels go to the right company.',
        'TiffinGo’s kitchen VM (10.10.1.5) calls the billing VM (10.10.2.7) inside its VPC. Another AWS customer on the same physical host uses the very same 10.10.x addresses — overlays keep both networks apart.',
        'VXLAN, Geneve, NVGRE; VMware NSX, Open vSwitch/OVN, Kubernetes CNIs (Calico VXLAN, Flannel, Cilium); cloud: AWS VPC (own encapsulation on Nitro), Azure VNet, Google VPC (Andromeda).',
        '', '',
        'many tenants or teams share hardware, networks are created by API, or a network must span racks and sites.',
        'MTU is forgotten (the wrapper adds ~50 bytes) or troubleshooting tools only look at the underlay.',
        deep='<b>See it step by step</b> in the six-step packet animation in the next section (“Follow one packet through a VPC”); then the deep dive (Nitro Card for VPC, VLAN vs VXLAN, MTU).',
        plain='Each company or team gets its own private network made purely of software. When a message travels between two servers, it is put inside a sealed envelope with the network’s name on it, carried over the shared cables, and opened only at the other end.',
        how=[('Control plane knows everything', 'The cloud or SDN controller stores every VPC, subnet and which host each VM is on.'), ('VM sends an ordinary packet', 'The guest sends to a private IP as if on a normal LAN.'), ('Look up the destination host', 'The host’s virtual switch (or Nitro card) asks “which physical host has 10.10.2.7 in this VPC?”'), ('Encapsulate', 'Wrap: outer Ethernet + IP (host 1 → host 2) + UDP (port 4789 for VXLAN) + VXLAN header with a 24-bit VNI.'), ('Underlay routes it', 'Physical routers see only host-to-host UDP traffic.'), ('Decapsulate and deliver', 'Host 2 removes the wrapper, checks the VNI and security rules, delivers to the VM.')],
        words=[('underlay', 'the real physical network'), ('overlay', 'the virtual network carried on top'), ('encapsulation', 'putting one packet inside another'), ('VNI', 'VXLAN network identifier, 24 bits'), ('VTEP', 'the endpoint that wraps/unwraps (a host or switch)'), ('UDP 4789', 'the standard port used by VXLAN')],
        diff=table(['', 'Overlay', 'VLAN', 'VPN'], [['Purpose', 'many virtual networks on shared hardware', 'separate a local network', 'secure link across an untrusted network'], ['Encrypted by default?', 'no (isolated by tag)', 'no', 'yes'], ['Scale', 'millions of networks', '4,094', 'per tunnel'], ['Typical place', 'inside clouds and data centres', 'offices', 'office ↔ cloud, home ↔ office']], minw=560),
        where=['Every public-cloud VPC/VNet', 'Private clouds (OpenStack, NSX)', 'Kubernetes pod networks', 'Stretching networks between data centres'],
        realworld='Every Amazon VPC, Azure VNet and Google VPC is an overlay: millions of customers create networks, often with identical 10.0.0.0/16 ranges, on shared physical networks without their traffic ever mixing.',
        pro='An AWS VPC has no broadcast or multicast: ARP requests never reach other instances — the Nitro card answers them from the mapping service. That is why gratuitous-ARP failover from on-premises clusters does not work in AWS.')

# ---------------------------------------------------------------- 3 SDN
def a_sdn(k):
    o = t(180, 12, ['Before: log into every switch', 'A central controller holds the plan', 'Rules pushed to every device'][k], 9, 'ink', bold=True)
    for i in range(4):
        x = 14 + i * 86
        o += box(x, 104, 74, 34, 'card' if k < 2 else 'green', rx=5) + t(x + 37, 121, f'switch {i + 1}', 7.4, 'ink', bold=True) + (t(x + 37, 132, 'rules ✓', 6.6, 'ink2') if k == 2 else '')
    if k == 0:
        o += box(140, 30, 80, 34, 'red', rx=5) + t(180, 51, 'admin', 8, 'ink', bold=True)
        for i in range(4):
            o += f'<path d="M180,64 L{51 + i * 86},104" style="stroke:#D64545;stroke-width:1.4;stroke-dasharray:4 3"/>'
        o += t(180, 90, 'CLI on each box · slow · errors', 7.2, 'red', bold=True)
    if k >= 1:
        o += box(110, 26, 140, 40, 'violet', rx=6) + t(180, 44, 'SDN controller', 8.4, 'ink', bold=True) + t(180, 58, 'desired state via API', 7, 'ink2')
    if k == 2:
        for i in range(4):
            o += packet(180, 66, 51 + i * 86, 104, '')
    return o
A_SDN = cap([a_sdn(k) for k in range(3)], [('Before: box by box', 'Changing a network meant logging into each switch and router', 'and typing commands — slow and error-prone.'), ('One central brain', 'An SDN controller stores the desired network as data, reachable by API', '(“kitchen may reach billing on 443”).'), ('Push to every device', 'The controller programs forwarding rules into every switch or host;', 'devices just forward packets (data plane).')],
    'SDN in action', 'Separating the network’s brain from its muscles.', 'Software-defined networking', 'Animation: admin configures four switches one by one; then a central SDN controller holds the desired state; the controller pushes rules to all four switches.', 't3anim')
T3 = vtype(3, 'SDN (software-defined networking)', 'violet',
    '<b>Software-defined networking</b> separates the network’s <b>control plane</b> (decisions about where traffic should go) from its <b>data plane</b> (forwarding packets), centralising control in software controllers that program network devices through open interfaces and APIs.',
    'A metro rail system: trains (data plane) just follow signals; one central control room (control plane) decides routes and sets all signals at once — no driver decides alone.',
    'When TiffinGo opens a new city, a Terraform file creates the VPC, subnets, route tables and security groups. The cloud’s SDN controller programs thousands of hosts in seconds — nobody touches a switch.',
    'OpenFlow, OpenDaylight, ONOS, VMware NSX, Cisco ACI, Juniper Contrail; cloud: the VPC control planes of AWS, Azure and Google (Andromeda); SD-WAN products for branch offices.',
    '', A_SDN,
    'networks change often, must be automated, or must be consistent across many devices.',
    'the controller becomes a single point of failure — it must itself be highly available.',
    plain='Instead of configuring every network box by hand, one central program decides how traffic should flow and sends instructions to all boxes automatically. The boxes just follow orders.',
    how=[('Describe the desired network', 'An admin or tool (console, API, Terraform) declares networks, routes and rules.'), ('Controller stores the state', 'The SDN controller keeps the full picture: topology, policies, where each workload is.'), ('Compute forwarding rules', 'It converts policy into match → action rules (e.g. “dst 10.10.2.0/24, port 443 → allow, send to host 7”).'), ('Program the data plane', 'Rules are pushed to switches or virtual switches via southbound APIs (OpenFlow, OVSDB, vendor APIs).'), ('Devices forward', 'Each device forwards packets at line rate using those rules.'), ('Feedback', 'Devices report status and events back so the controller can react (link down, VM moved).')],
    words=[('control plane', 'the part that decides routes and rules'), ('data plane', 'the part that actually moves packets'), ('controller', 'central software holding the network’s plan'), ('southbound API', 'how the controller talks to devices'), ('northbound API', 'how apps and admins talk to the controller')],
    diff=table(['', 'SDN', 'Traditional networking', 'NFV'], [['Where decisions are made', 'central controller', 'each device', 'n/a — about running functions as software'], ['Change method', 'API / code', 'device CLI', 'deploy a VM/container'], ['Relationship', 'controls the network', '—', 'often controlled by SDN']], minw=520),
    where=['Cloud VPC control planes', 'Data-centre fabrics', 'SD-WAN for branch offices', 'Campus networks with central policy'],
    realworld='Google describes its data-centre and Andromeda virtual networks as software-defined, and SD-WAN is now common in Indian banks and retail chains to manage hundreds of branch links centrally.',
    pro='“Infrastructure as code” for networks only works because of SDN: a Terraform plan is just a diff of desired state the controller converges to — the same reconciliation loop idea as Kubernetes.')

# ---------------------------------------------------------------- 4 NFV
def a_nfv(k):
    o = t(180, 12, ['Before: special hardware boxes', 'Same functions as software', 'Scale by adding copies'][k], 9, 'ink', bold=True)
    names = ['firewall', 'load balancer', 'router']
    if k == 0:
        for i, n in enumerate(names):
            o += box(14 + i * 116, 40, 100, 56, 'red', rx=6) + t(64 + i * 116, 64, n, 8, 'ink', bold=True) + t(64 + i * 116, 80, 'appliance', 7, 'ink2')
        o += t(180, 124, 'buy, rack, cable each box · weeks', 7.8, 'red', bold=True)
    else:
        o += box(14, 108, 332, 26, 'card', rx=5) + t(180, 125, 'ordinary servers + hypervisor / cloud', 7.6, 'ink', bold=True)
        for i, n in enumerate(names):
            cnt = 1 if k == 1 or i != 1 else 3
            for c in range(cnt):
                o += box(14 + i * 116 + c * 8, 40 - c * 6, 100, 50, 'green', rx=6) + t(64 + i * 116 + c * 8, 62 - c * 6, n, 7.6, 'ink', bold=True) + t(64 + i * 116 + c * 8, 78 - c * 6, 'VM / container', 6.8, 'ink2')
        if k == 2:
            o += t(180, 150, 'Diwali traffic: 3 load-balancer copies in minutes', 7.6, 'green', bold=True)
    return o
A_NFV = cap([a_nfv(k) for k in range(3)], [('Special hardware boxes', 'Firewalls, load balancers and routers used to be dedicated appliances', 'bought, racked and cabled one by one.'), ('Same functions as software', 'NFV runs them as VMs or containers on ordinary servers — or as', 'a cloud service you create by API.'), ('Scale by copies', 'Need more capacity? Start more copies; delete them after the peak.', 'Cloud load balancers do this automatically.')],
    'NFV in action', 'Network boxes become software.', 'Network functions virtualization', 'Animation: three hardware appliances; the same functions as VMs on ordinary servers; the load balancer scaled to three copies.', 't4anim')
T4 = vtype(4, 'NFV (network functions virtualization)', 'violet',
    '<b>Network functions virtualization</b> implements network functions — firewalls, load balancers, routers, NAT, VPN gateways, even mobile-network cores — as software running on standard servers (as VMs or containers) instead of on dedicated proprietary hardware appliances.',
    'Instead of buying a separate calculator, camera and music player, you install apps on one smartphone. The functions are the same; the hardware is general-purpose.',
    'For the Diwali sale TiffinGo’s load balancer must handle 6× traffic. With a cloud load balancer (NFV as a service) capacity grows automatically; with the old hardware box they would have had to buy a bigger appliance weeks in advance.',
    'Open-source and vendor virtual appliances (pfSense, VyOS, F5 BIG-IP VE, Palo Alto VM-Series); cloud: AWS Elastic Load Balancing, NAT Gateway, Network Firewall, VPN; Azure Load Balancer, Azure Firewall; Google Cloud Load Balancing, Cloud NAT.',
    '', A_NFV,
    'network capacity must change quickly, or you want firewalls and load balancers created by code.',
    'very high, steady throughput where specialised hardware is still cheaper per Gbps.',
    plain='Network devices like firewalls and load balancers used to be special boxes you had to buy. Now they are just programs running on normal servers or provided by the cloud, so you can create more of them in minutes.',
    how=[('Pick the function', 'Firewall, load balancer, router, NAT, VPN, 5G core function…'), ('Package as software', 'The vendor ships it as a VM image or container image (a VNF/CNF).'), ('Deploy on standard servers', 'It runs on a hypervisor or Kubernetes, often with SR-IOV/DPDK for fast packet processing.'), ('Chain functions', 'Traffic is steered through several functions in order (service chaining), usually programmed by SDN.'), ('Orchestrate', 'An orchestrator (e.g. ETSI MANO, Kubernetes) starts, scales and heals the functions.')],
    words=[('appliance', 'a dedicated hardware box for one job'), ('VNF / CNF', 'virtual / cloud-native (container) network function'), ('DPDK', 'a library for very fast packet processing in software'), ('service chaining', 'sending traffic through several functions in order')],
    diff=table(['', 'NFV', 'SDN', 'Hardware appliance'], [['What it changes', 'where network functions run', 'how the network is controlled', '—'], ['Runs on', 'standard servers / cloud', 'controller + devices', 'proprietary hardware'], ['Scaling', 'add copies', 'n/a', 'buy bigger box']], minw=520),
    where=['Cloud load balancers, NAT gateways, firewalls', 'Telecom 4G/5G core networks', 'Branch-office virtual routers (SD-WAN)', 'Security appliances in private clouds'],
    realworld='Telecom operators worldwide, including India’s large 5G operators, run 5G core network functions as cloud-native software on standard servers rather than on single-purpose boxes — NFV at national scale.',
    pro='An AWS Network Load Balancer is itself NFV built on Hyperplane, AWS’s internal distributed network function platform, which also powers NAT Gateway and PrivateLink — so one service team’s scaling work benefits all three.')

# ---------------------------------------------------------------- 5 block (STA anim)
def T5(STA):
    return vtype(5, 'Block storage virtualization', 'amber',
        '<b>Block storage virtualization</b> pools physical disks and presents <b>virtual block devices</b> (volumes) — raw sequences of fixed-size blocks that a server formats with its own file system — mapping each logical block to physical locations that the server never sees.',
        'A bank account: your passbook shows a balance; the bank decides which vault holds the notes and moves them without telling you.',
        'TiffinGo’s orders database runs on a 500 GB EBS gp3 volume. When it needs more space the volume is grown to 700 GB online, and a snapshot is taken before every upgrade.',
        'Linux LVM, SAN arrays over iSCSI/Fibre Channel/NVMe-oF, Ceph RBD, VMware vSAN; cloud: Amazon EBS, Azure Managed Disks, Google Persistent Disk / Hyperdisk.',
        '', STA,
        'databases, boot disks and anything that needs a raw disk with low latency.',
        'many servers must share the same files at once — use file storage; or storing huge amounts of unstructured data cheaply — use object storage.',
        deep='the deep dive below (how an EBS volume really works) and practical A3, B5, B6.',
        plain='Many real hard disks are combined into one pool, and each computer is given a “virtual hard disk” cut from the pool. The computer formats and uses it exactly like a real disk, never knowing which physical disks hold its data.',
        how=[('Pool the disks', 'Physical disks are added to a pool (LVM volume group, SAN array, or a distributed cluster).'), ('Create a volume', 'A volume of N GB is a mapping table: logical block → physical place; thin volumes map nothing yet.'), ('Present it', 'The server sees a block device (iSCSI, NVMe-oF, virtio-blk; on EC2 an NVMe device from the Nitro card).'), ('Server formats it', 'The guest OS creates its own file system (ext4, XFS, NTFS) on the blocks.'), ('Write path', 'Each write is mapped, allocated if new, written to replicas, then acknowledged.'), ('Snapshots and growth', 'Copy-on-write snapshots freeze the map; volumes can be enlarged online.')],
        words=[('block', 'a small fixed-size chunk of a disk (often 4 KB)'), ('volume', 'a virtual disk'), ('file system', 'the way an OS organizes files on a disk (ext4, NTFS)'), ('IOPS', 'input/output operations per second — disk speed'), ('replica', 'an extra copy for safety')],
        diff=table(['', 'Block', 'File', 'Object'], [['You get', 'a raw disk', 'a shared folder', 'a bucket of objects'], ['Accessed by', 'one server (usually)', 'many servers at once', 'any app over HTTP'], ['Protocol', 'NVMe, iSCSI, FC', 'NFS, SMB', 'HTTP REST (S3 API)'], ['Best for', 'databases, boot disks', 'shared content, home folders', 'backups, media, data lakes'], ['AWS', 'EBS', 'EFS, FSx', 'S3']], minw=560),
        where=['Every VM’s boot disk', 'Databases (MySQL, PostgreSQL, Oracle)', 'Kubernetes persistent volumes', 'SAN-backed VMware clusters'],
        realworld='Every EC2 instance boots from an EBS volume — a virtual block device spread over many storage servers in one Availability Zone and replicated inside it — and AWS documents EBS as designed for high durability within an AZ.',
        pro='gp3 decoupled performance from size: 3,000 IOPS and 125 MB/s baseline at any size, buyable separately. On old gp2, teams over-provisioned terabytes just to get IOPS — a classic cost leak worth checking in any audit.')

# ---------------------------------------------------------------- 6 file
def a_file(k):
    o = t(180, 12, ['Three servers need the same files', 'Mount one shared file system', 'Change once, everyone sees it'][k], 9, 'ink', bold=True)
    for i in range(3):
        x = 14 + i * 118
        o += box(x, 28, 100, 40, 'blue', rx=5) + t(x + 50, 46, f'web server {i + 1}', 7.6, 'ink', bold=True) + t(x + 50, 60, '/var/www/menu' if k >= 1 else 'own copy ⚠', 6.8, 'ink2' if k >= 1 else 'red')
    if k >= 1:
        o += box(90, 104, 180, 34, 'amber', rx=6) + t(180, 120, 'shared file system (NFS)', 8, 'ink', bold=True) + t(180, 132, 'EFS / Azure Files / Filestore', 6.8, 'ink2')
        for i in range(3):
            o += f'<path d="M{64 + i * 118},68 L180,104" style="stroke:#999;stroke-width:1.2"/>'
    if k == 2:
        o += packet(64, 68, 150, 104, 'save') + t(300, 96, 'new menu photo visible', 7.2, 'green', bold=True) + t(300, 150, '', 6)
    return o
A_FILE = cap([a_file(k) for k in range(3)], [('Same files, three servers', 'Three web servers each keep their own copy of menu photos;', 'an upload to one is missing on the others.'), ('Mount one shared file system', 'All three mount the same network file system at /var/www/menu', 'using NFS (Linux) or SMB (Windows).'), ('Change once, seen everywhere', 'A photo saved by server 1 is immediately visible to servers 2 and 3.', 'The storage service handles locking, growth and replication.')],
    'File storage virtualization in action', 'One folder shared by many servers.', 'Shared file system', 'Animation: three web servers with separate copies; they mount one shared NFS file system; a file saved by one is visible to all.', 't6anim')
T6 = vtype(6, 'File storage virtualization (NAS, shared file systems)', 'amber',
    '<b>File storage virtualization</b> presents storage as a shared, hierarchical <b>file system</b> — folders and files — accessed over the network with protocols such as NFS or SMB, so many servers and users can read and write the same files while the physical location of the data is hidden and can change.',
    'A shared office cupboard with labelled folders: everyone takes and returns files from the same cupboard, and the office manager can move the cupboard to a bigger room without anyone changing how they find a folder.',
    'TiffinGo runs three web servers behind a load balancer. Menu photos uploaded through one server must appear on all three, so the photo folder is an Amazon EFS file system mounted by all of them.',
    'NAS appliances (NetApp, Dell PowerScale), Windows file servers with DFS namespaces, CephFS, GlusterFS; cloud: Amazon EFS and FSx (Windows, NetApp ONTAP, Lustre, OpenZFS), Azure Files and Azure NetApp Files, Google Filestore.',
    '', A_FILE,
    'many servers or users need the same files at once (web content, home folders, shared datasets, legacy apps).',
    'a single database needs the lowest latency (use block) or you store billions of objects for the web (use object).',
    plain='A shared folder that lives on the network. Many computers can open, change and save the same files at the same time, as if the folder were on each of their own disks.',
    how=[('Create a file system', 'The storage system (NAS or cloud service) creates a file system on its pooled disks.'), ('Export it', 'It is shared over the network via NFS (Linux) or SMB (Windows), with access rules.'), ('Mount on clients', 'Each server mounts it at a path, e.g. <code>/var/www/menu</code> or drive <code>Z:</code>.'), ('Open, read, write', 'File operations travel over the network; the server handles locks so two writers do not corrupt a file.'), ('Grow and protect behind the scenes', 'Capacity grows automatically (EFS), snapshots and replication run without clients noticing.')],
    words=[('NAS', 'network-attached storage: a file server appliance'), ('NFS / SMB', 'the file-sharing languages of Linux / Windows'), ('mount', 'attach a file system to a folder path'), ('lock', 'a rule that stops two programs writing the same file at once')],
    diff=table(['', 'File (NAS)', 'Block (SAN)', 'Object'], [['Unit', 'files in folders', 'blocks', 'objects with keys'], ['Shared by many at once', 'yes', 'usually no', 'yes'], ['Network protocol', 'NFS, SMB', 'iSCSI, FC, NVMe-oF', 'HTTP'], ['Who owns the file system', 'the storage system', 'the server', 'none (flat namespace)']], minw=540),
    where=['Shared web content and uploads', 'User home folders', 'Machine-learning training datasets', 'Lift-and-shift of apps that expect a shared drive'],
    realworld='Amazon EFS is used to give many EC2 instances, containers (ECS/EKS) and Lambda functions the same shared files at once, and grows and shrinks automatically as files are added or removed.',
    pro='NFS metadata operations (create, stat, rename) are the usual bottleneck, not bandwidth — workloads with millions of tiny files (e.g. node_modules, Python environments) feel slow on any network file system. Put them on block storage and share only the data.')

# ---------------------------------------------------------------- 7 object
def a_obj(k):
    o = t(180, 12, ['PUT: send an object with a key', 'Stored as copies across devices', 'GET it from anywhere by its key'][k], 9, 'ink', bold=True)
    o += box(10, 40, 90, 50, 'blue', rx=6) + ic('app', 43, 46, 0.8) + t(55, 82, 'TiffinGo app', 7, 'ink', bold=True)
    o += box(140, 34, 90, 62, 'amber', rx=6) + t(185, 54, 'bucket', 8, 'ink', bold=True) + t(185, 70, 'menu/paneer.jpg', 6.8, 'ink2') + t(185, 84, '+ metadata', 6.6, 'ink2')
    if k == 0:
        o += packet(100, 65, 140, 65, 'PUT')
    if k >= 1:
        for i in range(3):
            o += cyl(250 + (i % 2) * 52, 30 + i * 36, 44, 30, f'AZ {i + 1}', 'green')
        o += packet(230, 60, 260, 60, '') if k == 1 else ''
    if k == 2:
        o += box(10, 110, 90, 30, 'violet', rx=5) + t(55, 129, 'phone / CDN', 7, 'ink', bold=True) + packet(185, 96, 100, 120, 'GET')
    o += t(180, 152, 'https://bucket.s3…/menu/paneer.jpg' if k == 2 else '', 6.8, 'ink2')
    return o
A_OBJ = cap([a_obj(k) for k in range(3)], [('PUT an object with a key', 'The app uploads a photo over HTTPS with a key (menu/paneer.jpg) and', 'optional metadata. No disk, no folder tree to manage.'), ('Copied across devices', 'The service splits/replicates the object across many disks in several', 'Availability Zones before saying “OK”.'), ('GET it by key from anywhere', 'Any app, phone or CDN fetches it with the key over HTTPS;', 'capacity is practically unlimited and billed per GB stored.')],
    'Object storage in action', 'Storage that is just an address and an object.', 'Object storage', 'Animation: app PUTs an object with a key into a bucket; it is replicated across three Availability Zones; a phone or CDN GETs it by key over HTTPS.', 't7anim')
T7 = vtype(7, 'Object storage virtualization', 'amber',
    '<b>Object storage</b> virtualizes storage as a flat namespace of <b>objects</b> — each the data itself plus metadata and a unique key — stored in buckets and accessed over HTTP APIs, with the system hiding all disks, servers and replicas behind the key.',
    'A cloakroom with tokens: you hand over a coat and get token 274. You don’t know or care which rack it hangs on; show the token and you get the coat back.',
    'TiffinGo stores every menu photo and nightly database backup in Amazon S3. The mobile app loads photos by URL through a CDN; old backups move to cheaper storage classes automatically.',
    'Ceph RGW, MinIO, NetApp StorageGRID; cloud: Amazon S3, Azure Blob Storage, Google Cloud Storage (all accessible with S3-style or native HTTP APIs).',
    '', A_OBJ,
    'storing large amounts of unstructured data: images, video, backups, logs, data-lake files.',
    'an app needs a mounted disk or frequent small in-place edits — objects are replaced whole, not edited.',
    plain='Each file is stored as a single “object” with a unique name (key). You put it in and get it back using that name over the internet. You never see disks or folders — the service handles where and how many copies are kept.',
    how=[('Create a bucket', 'A named container in a Region.'), ('PUT an object', 'Send the bytes, a key and metadata over HTTPS.'), ('Durably store', 'The service splits or replicates the object across many disks and (for S3 Standard) multiple Availability Zones before confirming.'), ('Index by key', 'A metadata index maps key → locations; there is no real folder tree (“/” in keys is just part of the name).'), ('GET / list', 'Clients fetch by key or list keys by prefix.'), ('Lifecycle', 'Rules move old objects to cheaper classes or delete them.')],
    words=[('object', 'the data + its metadata + a key'), ('bucket', 'a named container for objects'), ('key', 'the object’s unique name'), ('REST API', 'a web interface using HTTP verbs (PUT, GET, DELETE)'), ('storage class', 'a price/performance tier')],
    diff=table(['', 'Object', 'File', 'Block'], [['Edit in place', 'no — replace whole object', 'yes', 'yes'], ['Scale', 'practically unlimited', 'large', 'per volume'], ['Access', 'HTTP from anywhere', 'mounted on servers', 'attached to one server'], ['Cost per GB', 'lowest', 'medium', 'higher']], minw=520),
    where=['Images, video, downloads', 'Backups and archives', 'Data lakes (Parquet files)', 'Static websites', 'Logs'],
    realworld='Amazon S3 is designed for 99.999999999% (eleven nines) durability of objects over a year by storing data redundantly across multiple devices and Availability Zones; it underpins data lakes and backups for a vast number of companies.',
    pro='S3 has offered strong read-after-write consistency for all PUTs and DELETEs since December 2020 — older tutorials that warn about “eventual consistency” for overwrites are out of date.')

# ---------------------------------------------------------------- 8 data (FED anim)
def T8(FED):
    return vtype(8, 'Data virtualization (federated query)', 'red',
        '<b>Data virtualization</b> provides a logical layer that lets applications query and combine data from multiple heterogeneous sources — files, databases, SaaS systems, clouds — through one unified view, without copying the data and without needing to know its location or format.',
        'A travel booking site: one search shows fares from every airline, fetched live; the site owns no planes and copies no airline databases.',
        'Management wants revenue and average rating per zone today. Orders are in CSV, cities in Parquet, ratings in a SQLite CRM. One DuckDB query joins all three in place — West · Pune 330, Mumbai 310; North · Delhi 300.',
        'Denodo, TIBCO Data Virtualization, Trino/Starburst, Dremio, DuckDB; cloud: Amazon Athena Federated Query and Redshift Spectrum, Azure Synapse serverless SQL and Fabric shortcuts, BigQuery external tables, federated queries and BigQuery Omni.',
        '', FED,
        'live answers across systems are needed quickly, data must not be copied, or you prototype before building pipelines.',
        'the same heavy joins run every day on big data — copy it into a warehouse or lake instead.',
        plain='Data stays where it already lives. A smart layer lets you ask one question across many places as if they were one database, and fetches only what is needed. Nothing is copied.',
        how=[('Connect sources', 'Connectors are set up for files, databases and SaaS APIs.'), ('Catalog', 'Table and column metadata is collected into one catalog.'), ('Plan', 'A SQL query is parsed into a plan naming which source serves which table.'), ('Push down', 'Filters and column choices are sent to each source in its own language.'), ('Combine', 'Partial results are fetched in parallel, joined and aggregated.'), ('Govern', 'Masking and row-level rules are applied before the result is returned.')],
        words=[('connector', 'a plug-in that talks to one kind of source'), ('catalog', 'the list of tables and where they live'), ('pushdown', 'letting the source filter so less data moves'), ('federated', 'spread across several independent systems')],
        diff=table(['', 'Data virtualization', 'ETL + warehouse', 'Storage virtualization'], [['Unit', 'tables / views', 'tables', 'blocks / files / objects'], ['Data copied?', 'no', 'yes', 'n/a'], ['Hides', 'location and format of data', '—', 'which disks hold bytes']], minw=520),
        where=['Live cross-system dashboards', 'Regulatory reporting without copies', 'Prototyping data products', 'Multi-cloud analytics'],
        realworld='Amazon Athena Federated Query uses Lambda-based connectors to run one SQL query over S3 together with sources such as DynamoDB, RDS and on-premises databases, without loading the data first.',
        pro='Always read the plan: <code>EXPLAIN</code> in Trino, Athena or DuckDB shows whether your WHERE clause was pushed to the source. If not, the engine may pull the whole table across the network first.')

SUMMARY = table(['#', 'Type', 'Hides', 'You get', 'AWS', 'Azure', 'Google Cloud'], [
    ['1', 'VLAN', 'one shared switch', 'separate LANs', '— (not exposed)', '—', '—'], ['2', 'Overlay', 'shared physical network', 'private networks by API', 'VPC', 'VNet', 'VPC'],
    ['3', 'SDN', 'per-device configuration', 'network as code', 'VPC control plane', 'VNet control plane', 'Andromeda'], ['4', 'NFV', 'appliance hardware', 'firewalls/LBs as software', 'ELB, NAT GW, Network Firewall', 'Load Balancer, Azure Firewall', 'Cloud Load Balancing, Cloud NAT'],
    ['5', 'Block', 'physical disks', 'virtual disks', 'EBS', 'Managed Disks', 'Persistent Disk / Hyperdisk'], ['6', 'File', 'file servers', 'shared folders', 'EFS, FSx', 'Azure Files', 'Filestore'],
    ['7', 'Object', 'disks, servers, replicas', 'buckets + keys', 'S3', 'Blob Storage', 'Cloud Storage'], ['8', 'Data', 'location + format of data', 'one SQL view', 'Athena Federated', 'Synapse serverless', 'BigQuery external / Omni']], minw=760)
CHECK = ('  <h3>Check yourself: which type fits?</h3>\n' +
    qx('A. Three web servers must show the same uploaded menu photos.', ['Block storage', 'File storage (shared NFS)', 'VLAN', 'Data virtualization'], 1, 'A shared file system mounted by all servers.') +
    qx('B. A company stores 50 TB of videos and backups cheaply and serves them over HTTPS.', ['Object storage', 'Block storage', 'File storage', 'NFV'], 0, 'Object storage scales cheaply and is accessed over HTTP.') +
    qx('C. An office must separate guest Wi-Fi from staff PCs on the same switches.', ['VLAN', 'Overlay', 'Object storage', 'Data virtualization'], 0, 'A VLAN per group on the same switches.') +
    qx('D. A firewall must scale up for a sale and down afterwards without buying hardware.', ['SDN', 'NFV', 'VLAN', 'Block storage'], 1, 'Run the firewall as software (or a cloud service).') +
    qx('E. A database server needs a low-latency 500 GB disk.', ['Object storage', 'Block storage (EBS)', 'File storage', 'Data virtualization'], 1, 'Databases use block volumes.') +
    qx('F. Network changes must be made through code and applied to thousands of hosts at once.', ['SDN', 'VLAN', 'Object storage', 'P2V'], 0, 'A central controller programs every device.'))

def build(PKT, STA, FED):
    intro = ('  <p>Lesson 4.1 introduced network, storage and data virtualization in one block each. Here we open each one up into the <b>types</b> you will actually meet — four for networks, three for storage, one for data — in the same order as 4.1: definition, plain words, analogy, internal steps, picture/animation, differences, where used, real-world example, TiffinGo scenario, expert note.</p>\n'
             + challenge(['Why can’t a public cloud give each customer a VLAN?', 'Why do millions of tiny files feel slow on any network file system?', 'What changed about S3 consistency in 2020?'], 'types 1, 6 and 7') + MAP
             + jump(['VLAN', 'Overlay', 'SDN', 'NFV', 'Block', 'File', 'Object', 'Data']))
    return intro + T1 + T2(PKT) + T3 + T4 + T5(STA) + T6 + T7 + T8(FED) + '\n  <h3 style="margin-top:34px">All eight side by side</h3>\n' + SUMMARY + '\n' + CHECK
