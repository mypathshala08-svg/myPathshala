import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)


hk = hook('The hospital chain has 40 servers in its Pune data centre. Departments email IT for a new server and wait three weeks. Is that a private cloud?',
    'Not yet — it is a virtualized data centre. It becomes a <b>private cloud</b> when it gets the five NIST characteristics: <b>self-service</b>, <b>broad network access</b>, <b>resource pooling</b>, <b>rapid elasticity</b> and <b>metering</b>. This lesson shows the seven building blocks, follows a VM request through <b>OpenStack</b> step by step, compares six private-cloud platforms one by one, and on <b>your own</b> account you build the private-cloud “catalogue, quota and chargeback” ideas with public-cloud tools — free.',
    ['Why a hypervisor cluster alone is not a cloud.', 'What happens inside OpenStack when you click “Launch instance”.', 'How private clouds charge departments (showback and chargeback).'])

def story_scene():
    o = t(180, 12, 'From ticket queue to self-service', 9, 'ink', bold=True)
    o += box(8, 28, 150, 74, 'red', rx=8) + t(83, 48, 'Today', 8.4, 'ink', bold=True) + t(83, 64, 'email → approval → IT', 7, 'ink2') + t(83, 78, 'builds VM by hand', 7, 'ink2') + t(83, 92, '3 weeks', 7.4, 'ink', bold=True)
    o += arrow(162, 65, 196, 65)
    o += box(200, 28, 152, 74, 'green', rx=8) + t(276, 48, 'Private cloud', 8.4, 'ink', bold=True) + t(276, 64, 'portal → quota check', 7, 'ink2') + t(276, 78, 'automation builds it', 7, 'ink2') + t(276, 92, '5 minutes', 7.4, 'ink', bold=True)
    o += t(180, 122, 'Same 40 servers — different operating model', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Left: today, a VM request goes by email and takes three weeks. Right: with a private cloud, a portal checks quota and automation builds the VM in five minutes.', story_scene(), 'A private cloud is an <tspan font-weight="700" class="s-acc">operating model</tspan>, not just hardware.', h=134)
dialogue = '''K> Sir, the hospital IT head says “we already have a private cloud — everything is on VMware”.
A> Can a doctor’s research team get a VM themselves, today, within their budget?
K> No… they raise a ticket.
A> Then it is virtualization, not cloud. A private cloud adds a self-service portal, quotas, automation and metering on top.
R> What software does that?
A> OpenStack, VMware Cloud Foundation, Azure Local, Nutanix and others. Let’s see the building blocks first.'''

# ------------------------------------------------------------------ picture
def layfig():
    o = t(320, 16, 'Seven building blocks of a private cloud', 11, 'ink', bold=True)
    L = [('7', 'Self-service portal + API', 'catalogue, requests, quotas', 'green'), ('6', 'Orchestration & automation', 'templates, IaC, workflows', 'blue'), ('5', 'Metering, showback, chargeback', 'usage per team', 'amber'),
         ('4', 'Identity & multi-tenancy', 'projects, roles, isolation', 'violet'), ('3', 'Software-defined network + storage', 'virtual networks, pooled disks', 'blue'), ('2', 'Compute virtualization', 'KVM, ESXi, Hyper-V clusters', 'blue'), ('1', 'Physical hardware + data centre', 'servers, switches, power, cooling', 'card')]
    for i, (n, a, b, tn) in enumerate(L):
        y = 28 + i * 28
        o += box(70, y, 500, 24, tn, rx=5) + pin(84, y + 12, n) + t(250, y + 16, a, 8, 'ink', bold=True) + t(450, y + 16, b, 7, 'ink2')
    o += t(320, 232, 'Blocks 1–3 = a virtualized data centre. Blocks 4–7 turn it into a cloud.', 7.6, 'ink', bold=True)
    return o
LAY = bigfig('Seven stacked layers: hardware, compute virtualization, software-defined network and storage, identity and multi-tenancy, metering, orchestration, self-service portal and API.', layfig(), h=242)

def nistfig():
    o = t(320, 16, 'Test: does it meet NIST’s five characteristics?', 11, 'ink', bold=True)
    C = [('On-demand self-service', 'portal/API, no ticket'), ('Broad network access', 'any device, standard APIs'), ('Resource pooling', 'shared clusters, quotas'), ('Rapid elasticity', 'add/remove in minutes'), ('Measured service', 'usage metered per team')]
    for i, (a, b) in enumerate(C):
        x = 12 + i * 126
        o += box(x, 34, 118, 86, 'blue', rx=8) + pin(x + 14, 48, str(i + 1)) + t(x + 59, 74, a, 7.4, 'ink', bold=True) + t(x + 59, 94, b, 6.8, 'ink2')
    o += t(320, 142, 'Missing any of the five? It is virtualization or hosting — useful, but not a cloud.', 7.6, 'ink2')
    return o
NIST = bigfig('Five boxes for NIST characteristics: on-demand self-service, broad network access, resource pooling, rapid elasticity, measured service.', nistfig(), h=152)

picture = ('  <p>A private cloud is built in layers. The bottom three exist in most data centres already; the top four are what make it a cloud:</p>\n' + LAY +
           '\n  <p>Use NIST’s five characteristics as the acceptance test:</p>\n' + NIST +
           '\n  <h3>Build vs buy vs rent</h3>\n' + table(['', 'Build (open source)', 'Buy (commercial stack)', 'Rent (hosted private)'], [
               ['Examples', 'OpenStack, CloudStack', 'VMware Cloud Foundation, Nutanix, Azure Local', 'Azure VMware Solution, GCVE, Outposts'], ['Licence cost', 'none (support optional)', 'high', 'in the monthly price'],
               ['Skills needed', 'highest', 'medium', 'lowest'], ['Time to first VM', 'weeks–months', 'weeks', 'hours–days'], ['Best for', 'telecom, large scale, no lock-in', 'enterprises with existing skills', 'no data centre / fast exit']], minw=640))

# ------------------------------------------------------------------ how: OpenStack launch
RN = {'u': (4, 54, 50, 50, 'user', 'Researcher', 'Horizon / CLI'), 'ks': (66, 4, 60, 46, 'shield', 'Keystone', 'identity'), 'nova': (66, 104, 60, 46, 'server', 'Nova', 'compute API'),
      'sch': (138, 54, 62, 50, 'gear', 'Scheduler', 'picks host'), 'gl': (212, 4, 62, 46, 'disk', 'Glance', 'image'), 'neu': (212, 104, 62, 46, 'globe', 'Neutron', 'network port'), 'kvm': (290, 54, 66, 50, 'chip', 'KVM host', 'VM boots')}
RS = [dict(on=['u', 'ks'], hot='ks', move=(54, 79, 70, 30, 'token'), head='Step 1 · Prove who you are', text='The researcher logs in; Keystone checks the user and the project (tenant) and', text2='returns a token with roles. Every later call carries that token.', svc='AWS IAM · Azure Entra ID · VMware vCenter SSO'),
      dict(on=['u', 'ks', 'nova'], hot='nova', move=(54, 79, 70, 126, 'boot'), head='Step 2 · Ask Nova for a VM', text='“openstack server create --flavor m1.small --image ubuntu …”. Nova checks the', text2='project’s quota (vCPU, RAM, instances) before anything else.', svc='Quota = how a private cloud shares limited hardware fairly'),
      dict(on=['nova', 'sch'], hot='sch', move=(126, 127, 150, 90, 'place'), head='Step 3 · Scheduler picks a host', text='Filters remove hosts without enough RAM or in the wrong zone; weights pick the', text2='best of the rest (e.g. least loaded).', svc='Same job as EC2 placement in Lesson 2.1'),
      dict(on=['sch', 'gl'], hot='gl', move=(200, 70, 222, 40, 'image'), head='Step 4 · Glance supplies the image', text='The chosen host downloads (or clones from Ceph) the Ubuntu image to build the', text2='VM’s disk.', svc='Like AMIs / Azure images / GCE images'),
      dict(on=['sch', 'gl', 'neu'], hot='neu', move=(244, 50, 244, 104, 'port'), head='Step 5 · Neutron plugs it into the network', text='A virtual port, private IP, security group rules and (optionally) a floating IP are', text2='created on the project’s own virtual network.', svc='Software-defined networking = block 3'),
      dict(on=list(RN), hot='kvm', move=(274, 127, 298, 90, 'start'), head='Step 6 · KVM boots the VM', text='nova-compute tells libvirt/KVM to start it; cloud-init applies the SSH key and', text2='user data. Ceilometer-style metering starts counting usage for the project.', svc='Minutes, no ticket: self-service + metering = cloud')]
LAUNCH = flow_anim('Inside OpenStack: one “Launch instance” click', 'The services a private cloud uses to turn a request into a running VM.', 'OpenStack launch', 'Animation: Keystone issues a token; Nova checks quota; scheduler picks a host; Glance supplies the image; Neutron creates a network port; KVM boots the VM and metering starts.', RN, RS, hid='osflow')

# ------------------------------------------------------------------ types: platforms
def mapfig():
    o = t(320, 16, 'Six ways to build a private cloud', 11, 'ink', bold=True)
    items = [('1', 'OpenStack', 'open source, modular', 'blue'), ('2', 'VMware Cloud Foundation', 'commercial, vSphere-based', 'violet'), ('3', 'Azure Local', 'Azure services on your hardware', 'blue'),
             ('4', 'Nutanix (HCI)', 'hyperconverged appliances', 'green'), ('5', 'Apache CloudStack', 'open source, simpler', 'amber'), ('6', 'Kubernetes / OpenShift', 'container private cloud', 'green')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 3) * 208; y = 32 + (i // 3) * 84
        o += box(x, y, 198, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 106, y + 34, a, 8.4, 'ink', bold=True) + t(x + 106, y + 54, b, 7, 'ink2')
    o += t(320, 210, 'All six give self-service, pooling and automation; they differ in licence, skills and ecosystem.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of six private-cloud platforms: OpenStack, VMware Cloud Foundation, Azure Local, Nutanix HCI, Apache CloudStack, Kubernetes/OpenShift.', mapfig(), h=222)

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

A1 = mk(['Pick services', 'Deploy on servers', 'Projects use it'], ['services|Nova, Neutron|Cinder, Glance…', 'deploy|Kolla / Juju|Ceph storage', 'projects|portal + API|quotas'], ['blue', 'amber', 'green'],
        ['choose the modules you need', 'install with a deployment tool on commodity servers', 'teams get AWS-like APIs inside the company'],
        [('Services', 'Pick modules: compute, network, block, image, identity.', ''), ('Deploy', 'Install with Kolla-Ansible, Juju/Sunbeam or a distribution.', ''), ('Use', 'Projects get a portal, CLI and APIs with quotas.', '')],
        'OpenStack in action', 'Build your own cloud from modules.', 'OpenStack', 'Animation: choose services; deploy on servers; projects use the cloud.', 'o1anim')
T1 = vtype(1, 'OpenStack', 'blue',
    '<b>OpenStack</b> is an open-source cloud platform made of cooperating services — Keystone (identity), Nova (compute), Neutron (networking), Cinder (block storage), Glance (images), Swift (object storage), Horizon (dashboard) and others — that turns pools of commodity servers into an IaaS cloud with APIs, multi-tenancy and quotas.',
    'A modular kitchen from separate pieces: you choose every cabinet and fit them yourself — flexible and cheap to buy, but you need a good carpenter.',
    'The hospital builds a 12-server OpenStack cloud with Ceph storage; research teams get projects with 64 vCPU quotas and launch VMs themselves.',
    'Distributions: Canonical OpenStack (Sunbeam/Charmed), Red Hat OpenStack Services on OpenShift, Mirantis, Kolla-Ansible (community); used by telecoms, CERN, banks, public clouds like OVHcloud.',
    'The launch animation above walks through Keystone → Nova → scheduler → Glance → Neutron → KVM.', A1,
    'you need large scale, no licence fees, deep customisation, or AWS-like APIs on-premises.',
    'the team is small and has no Linux/networking depth — operations are the real cost.',
    plain='Free software that turns a group of normal servers into your own AWS-like cloud.',
    how=[('Plan', 'Controllers, compute, storage nodes, networks.'), ('Deploy', 'Kolla-Ansible / Sunbeam / vendor installer.'), ('Storage', 'Usually Ceph for block, image and object.'), ('Tenants', 'Domains, projects, roles, quotas.'), ('Operate', 'Upgrades every 6-month release cycle.')],
    words=[('Nova', 'OpenStack compute service'), ('Neutron', 'OpenStack networking service'), ('Ceph', 'open-source distributed storage often used with OpenStack')],
    diff=table(['', 'OpenStack', 'VMware Cloud Foundation'], [['Licence', 'open source', 'commercial subscription'], ['Hypervisor', 'mainly KVM', 'ESXi'], ['Skill profile', 'Linux, networking, Python', 'VMware admins']], minw=440),
    where=['Telecom network functions (NFV)', 'Research and universities', 'Regional public clouds'],
    realworld='CERN runs one of the largest OpenStack clouds to process physics data, with hundreds of thousands of cores.',
    pro='Most OpenStack pain is upgrades and networking; choose a distribution with a tested upgrade path and keep the control plane highly available (3 controllers).')

A2 = mk(['vSphere estate', 'Full stack', 'Self-service'], ['vSphere|ESXi + vCenter|existing skills', 'VCF|vSAN, NSX|automation', 'portal|catalogue|policies'], ['violet', 'blue', 'green'],
        ['most enterprises already run vSphere', 'VCF adds software-defined storage, network and lifecycle', 'automation gives a self-service catalogue'],
        [('Base', 'Existing ESXi hosts and vCenter.', ''), ('Stack', 'VCF adds vSAN (storage), NSX (network), SDDC Manager (lifecycle).', ''), ('Portal', 'Automation provides catalogue and self-service.', '')],
        'VMware Cloud Foundation in action', 'From vSphere to private cloud.', 'VMware VCF', 'Animation: vSphere estate; full VCF stack; self-service portal.', 'o2anim')
T2 = vtype(2, 'VMware Cloud Foundation (VCF)', 'violet',
    '<b>VMware Cloud Foundation</b> is Broadcom’s integrated private-cloud platform combining vSphere (ESXi + vCenter) compute virtualization, vSAN software-defined storage, NSX software-defined networking and lifecycle and automation tooling, delivered as one subscription.',
    'Buying a fully fitted branded kitchen from one company: everything matches and has one warranty — at a premium price.',
    'A pharma company with 300 VMware VMs adopts VCF so labs can request VMs from a catalogue; it can also run the same stack hosted in Azure or Google Cloud.',
    'VMware Cloud Foundation and vSphere Foundation (Broadcom); hosted as Azure VMware Solution, Google Cloud VMware Engine, Oracle Cloud VMware Solution.',
    '', A2,
    'you already have VMware skills and tooling and want an integrated, supported stack.',
    'licence cost is the main concern — Broadcom’s subscription changes (2024) raised costs for many customers.',
    plain='VMware’s complete package for turning your data centre into a private cloud.',
    how=[('Hosts', 'ESXi on certified servers.'), ('Management', 'vCenter + SDDC Manager.'), ('Storage', 'vSAN pools local disks.'), ('Network', 'NSX virtual networks and firewalls.'), ('Automate', 'Catalogue and blueprints.')],
    words=[('vSphere', 'VMware’s virtualization platform'), ('vSAN', 'VMware software-defined storage'), ('NSX', 'VMware software-defined networking')],
    diff=table(['', 'VCF', 'Nutanix'], [['Hypervisor', 'ESXi', 'AHV (or ESXi)'], ['Storage', 'vSAN', 'Nutanix AOS'], ['Licensing', 'per core subscription', 'per core / node subscription']], minw=440),
    where=['Large enterprises', 'Banks and insurers', 'Hosted private clouds'],
    realworld='After Broadcom completed its acquisition of VMware in 2023, it moved to subscription bundles centred on VCF — a key reason many customers re-evaluated Nutanix, OpenStack, Azure Local and public cloud.',
    pro='Ask what you actually use: many shops pay for the full stack but only run vSphere — a licence audit is often the first private-cloud cost saving.')

A3 = mk(['Validated hardware', 'Azure Local cluster', 'Managed from Azure'], ['hardware|validated nodes|in your DC', 'cluster|Hyper-V + Storage Spaces|on-prem', 'Azure Arc|portal, policy|billing'], ['blue', 'violet', 'green'],
        ['buy certified servers from OEM partners', 'they run a hyperconverged Hyper-V cluster', 'everything is created and governed from the Azure portal'],
        [('Hardware', 'Validated servers in your own data centre.', ''), ('Cluster', 'Hyper-V compute + Storage Spaces Direct storage.', ''), ('Azure', 'Arc connects it: portal, RBAC, policy, monitoring, billing.', '')],
        'Azure Local in action', 'Azure management, your building.', 'Azure Local', 'Animation: validated hardware; on-prem cluster; managed through Azure Arc.', 'o3anim')
T3 = vtype(3, 'Microsoft Azure Local', 'blue',
    '<b>Azure Local</b> (formerly Azure Stack HCI) is Microsoft’s hyperconverged infrastructure solution that runs virtual machines, AKS clusters and selected Azure services on validated hardware in the customer’s data centre, managed through the Azure portal via Azure Arc and billed as an Azure subscription service.',
    'A franchise outlet: your own shop and staff, but the brand’s menu, systems and head-office dashboard.',
    'A hospital in a city with unreliable links runs Azure Local in its server room: VMs stay local, while IT manages them and applies policies from the Azure portal.',
    'Azure Local on OEM hardware (Dell, HPE, Lenovo and others); AWS Outposts and Google Distributed Cloud are the closest equivalents from other providers.',
    'Hybrid management (Arc) is in Lesson 3.1’s deep dive.', A3,
    'you are a Microsoft shop that needs on-prem VMs with Azure-style management.',
    'the site has no internet connectivity at all for long periods — check the current connectivity requirements.',
    plain='Microsoft’s system for running a small Azure-managed cloud on your own servers.',
    how=[('Buy', 'Validated nodes (OEM catalogue).'), ('Deploy', 'From the Azure portal.'), ('Register', 'Arc-enabled; appears as Azure resources.'), ('Run', 'VMs, AKS, Azure Virtual Desktop.'), ('Pay', 'Per physical core per month to Azure.')],
    words=[('HCI', 'hyperconverged infrastructure — compute and storage in the same nodes'), ('Azure Arc', 'extends Azure management to non-Azure resources'), ('validated', 'tested and certified by Microsoft')],
    diff=table(['', 'Azure Local', 'AWS Outposts'], [['Hardware owner', 'customer (OEM)', 'AWS'], ['Managed from', 'Azure portal via Arc', 'AWS console (Region)'], ['Services', 'VMs, AKS, AVD', 'EC2, EBS, ECS, RDS (subset)']], minw=440),
    where=['Branch offices, factories, hospitals', 'Low-latency local apps', 'Data that must stay on site'],
    realworld='Microsoft renamed Azure Stack HCI to Azure Local in late 2024 to signal one Azure-managed family for on-premises infrastructure.',
    pro='Azure Local is billed per physical core even when VMs are idle — size the cluster to real need, not to “future growth”.')

A4 = mk(['Appliance nodes', 'Add a node', 'Pool grows'], ['node|CPU + disks|in one box', 'scale out|add nodes|one at a time', 'pool|compute + storage|grows together'], ['green', 'amber', 'blue'],
        ['each node contains compute and storage', 'grow by adding identical nodes', 'the software pools them into one cluster'],
        [('Node', 'Each node has CPUs, RAM and disks.', ''), ('Add', 'Grow by adding nodes — no separate SAN.', ''), ('Pool', 'Software pools compute and storage across nodes.', '')],
        'Hyperconverged (Nutanix) in action', 'Grow one box at a time.', 'Nutanix HCI', 'Animation: appliance nodes; add a node; pooled compute and storage grows.', 'o4anim')
T4 = vtype(4, 'Nutanix and hyperconverged (HCI) platforms', 'green',
    '<b>Hyperconverged infrastructure (HCI)</b> combines compute, storage and virtualization in standard x86 nodes managed as one cluster by software; <b>Nutanix</b> Cloud Platform is a leading example, with its own AHV hypervisor, distributed storage and self-service management for private and hybrid clouds.',
    'Lego blocks: every block is the same shape, and you build a bigger structure by snapping on more.',
    'TiffinGo’s regional kitchen group buys a 3-node Nutanix cluster for its central office; when it needs more capacity it adds a fourth node in an afternoon.',
    'Nutanix Cloud Platform (AHV, AOS, Prism), Nutanix Cloud Clusters on AWS/Azure; other HCI: VMware vSAN ReadyNodes, Azure Local, HPE SimpliVity.',
    'Storage virtualization is in Lesson 4.3.', A4,
    'you want a simpler private cloud that grows in small steps without a separate storage array.',
    'compute and storage needs grow very unevenly — you may buy disks you do not need with every node.',
    plain='Ready-made boxes that each hold computing and storage, joined by software into one private cloud.',
    how=[('Nodes', 'Identical x86 servers with SSD/NVMe.'), ('Hypervisor', 'AHV (or ESXi).'), ('Distributed storage', 'Data copied across nodes (RF2/RF3).'), ('Manage', 'Single console (Prism).'), ('Scale', 'Add nodes online.')],
    words=[('hyperconverged', 'compute + storage + virtualization in each node'), ('SAN', 'storage area network — a separate storage system'), ('replication factor', 'how many copies of data are kept')],
    diff=table(['', 'HCI', 'Traditional 3-tier'], [['Storage', 'inside the nodes', 'separate SAN array'], ['Scaling', 'add nodes', 'add servers + storage separately'], ['Management', 'one console', 'several teams/tools']], minw=440),
    where=['Mid-size enterprises', 'Branch and edge sites', 'VDI farms'],
    realworld='HCI became popular for virtual desktop infrastructure (VDI): each node supports a predictable number of desktops, so capacity planning is simple.',
    pro='Three nodes is the practical minimum for resilience (data replicas plus a node failure); a two-node cluster needs a witness elsewhere.')

A5 = mk(['Management server', 'Zones and pods', 'Self-service'], ['management|one server|+ database', 'zones|pods, clusters|KVM, XenServer, ESXi', 'users|portal, API|accounts'], ['amber', 'blue', 'green'],
        ['a single management server controls the cloud', 'hardware is organised into zones, pods and clusters', 'users get a portal and API (with an AWS-compatible option)'],
        [('Manage', 'A management server and database control the cloud.', ''), ('Organise', 'Zones → pods → clusters of hypervisor hosts.', ''), ('Use', 'Self-service portal and API for accounts and projects.', '')],
        'Apache CloudStack in action', 'A simpler open-source cloud.', 'CloudStack', 'Animation: management server; zones and pods; self-service.', 'o5anim')
T5 = vtype(5, 'Apache CloudStack', 'amber',
    '<b>Apache CloudStack</b> is an open-source IaaS platform that manages pools of hypervisor hosts (KVM, XenServer/XCP-ng, VMware) from a central management server, offering a self-service portal, APIs, multi-tenancy, networking and storage orchestration — generally simpler to deploy and operate than OpenStack.',
    'A ready-to-assemble flat-pack wardrobe: fewer choices than a custom carpenter, but you can build it yourself in a weekend.',
    'A regional hosting company offers “TiffinGo-sized” VMs to local restaurants using CloudStack on 20 KVM hosts — a small public cloud built on private-cloud software.',
    'Apache CloudStack (community), ShapeBlue support; used by hosting providers and enterprises.', '', A5,
    'you want an open-source private cloud with fewer moving parts than OpenStack.',
    'you need OpenStack’s wider ecosystem (telecom NFV, many vendor drivers).',
    plain='Another free cloud software, simpler to set up, for building your own cloud.',
    how=[('Install', 'Management server + MySQL.'), ('Add zone', 'Networks, primary/secondary storage.'), ('Add hosts', 'KVM or other hypervisors.'), ('Offerings', 'Define VM sizes and templates.'), ('Tenants', 'Accounts, domains, projects.')],
    words=[('zone', 'a data-centre-level unit in CloudStack'), ('pod', 'a rack-level group of hosts'), ('offering', 'a predefined VM size or service')],
    diff=table(['', 'CloudStack', 'OpenStack'], [['Architecture', 'monolithic management server', 'many microservices'], ['Setup effort', 'lower', 'higher'], ['Ecosystem', 'smaller', 'larger']], minw=440),
    where=['Hosting and service providers', 'Mid-size private clouds', 'Education labs'],
    realworld='Several hosting companies and telcos run public cloud services for their regions on CloudStack because one small team can operate it.',
    pro='Choose by operations, not features: the platform your team can upgrade safely every year beats the one with the longest feature list.')

A6 = mk(['Kubernetes cluster', 'Platform layer', 'Developers self-serve'], ['K8s|nodes, pods|on-prem', 'platform|OpenShift / Rancher|builds, routes', 'devs|deploy apps|no tickets'], ['green', 'blue', 'green'],
        ['Kubernetes runs on bare metal or VMs in your data centre', 'a platform adds builds, registry, security, multi-tenancy', 'developers deploy apps themselves — a private PaaS'],
        [('Cluster', 'Kubernetes on your own servers.', ''), ('Platform', 'OpenShift/Rancher add builds, registry, routes, policies.', ''), ('Self-serve', 'Teams deploy containers themselves — private PaaS.', '')],
        'Container private cloud in action', 'Private PaaS on Kubernetes.', 'Kubernetes / OpenShift', 'Animation: Kubernetes cluster; platform layer; developers self-serve.', 'o6anim')
T6 = vtype(6, 'Container private cloud (Kubernetes / OpenShift)', 'green',
    'A <b>container-based private cloud</b> uses Kubernetes — often packaged as Red Hat OpenShift, SUSE Rancher or VMware Tanzu — on the organisation’s own infrastructure to give teams self-service deployment of containerised applications, effectively a <b>private PaaS</b>, sometimes with VMs managed alongside (KubeVirt / OpenShift Virtualization).',
    'A food court’s shared kitchen: every stall cooks its own dishes, but gas, water, cleaning and rules come from the food-court manager.',
    'The hospital’s IT team runs OpenShift on its private cloud so app teams deploy patient-portal services from Git without waiting for IT.',
    'Red Hat OpenShift (incl. OpenShift Virtualization), SUSE Rancher, VMware Tanzu/VKS, Google Distributed Cloud, AKS on Azure Local, EKS Anywhere.',
    'Containers vs VMs is Lesson 4.5; PaaS types are Lesson 2.2.', A6,
    'most new apps are containerised and you want a consistent platform on-prem and in clouds.',
    'the workload is mostly legacy Windows VMs — start with a VM-based private cloud.',
    plain='A private cloud for containers, where developers deploy their apps themselves on company servers.',
    how=[('Infra', 'Bare metal or VMs.'), ('Cluster', 'Control plane + workers.'), ('Platform', 'Registry, CI/CD, ingress, policies.'), ('Tenancy', 'Namespaces/projects + quotas.'), ('Operate', 'Upgrades, monitoring, backups.')],
    words=[('Kubernetes', 'open-source container orchestrator'), ('namespace', 'a tenant space inside a cluster'), ('KubeVirt', 'runs VMs inside Kubernetes')],
    diff=table(['', 'Container private cloud', 'VM private cloud'], [['Unit', 'containers', 'VMs'], ['Service model', 'PaaS-like', 'IaaS'], ['Users', 'developers', 'IT and app teams']], minw=440),
    where=['Modern application teams', 'Banks and telecoms', 'Hybrid platforms across clouds'],
    realworld='Since the VMware licensing changes, OpenShift Virtualization and other KubeVirt-based platforms have been promoted as a way to run VMs and containers on one private platform.',
    pro='Kubernetes is not a full private cloud by itself — you still need identity, networking, storage, backups and metering around it.')

SUMMARY = table(['#', 'Platform', 'Licence', 'Hypervisor / runtime', 'Typical user'], [
    ['1', 'OpenStack', 'open source', 'KVM', 'telecoms, research, large scale'], ['2', 'VMware Cloud Foundation', 'commercial', 'ESXi', 'VMware enterprises'], ['3', 'Azure Local', 'Azure subscription', 'Hyper-V', 'Microsoft shops, branches'],
    ['4', 'Nutanix HCI', 'commercial', 'AHV / ESXi', 'mid-size, VDI'], ['5', 'Apache CloudStack', 'open source', 'KVM, XCP-ng, ESXi', 'hosting providers'], ['6', 'Kubernetes / OpenShift', 'open source / commercial', 'containers (+ KubeVirt)', 'app platforms']], minw=620)
CHECK = ('  <h3>Check yourself: which platform?</h3>\n' +
    qx('A. Open source, modular, telecom NFV, very large scale.', ['OpenStack', 'Azure Local', 'Nutanix', 'VCF'], 0, 'OpenStack.') +
    qx('B. Managed from the Azure portal, runs on validated hardware on-prem.', ['CloudStack', 'Azure Local', 'OpenShift', 'VCF'], 1, 'Azure Local.') +
    qx('C. Grow by adding identical nodes with built-in storage.', ['Hyperconverged (HCI)', 'SAN-based 3-tier', 'Public cloud', 'Mainframe'], 0, 'HCI.') +
    qx('D. Developers deploy containers on company servers from Git.', ['OpenShift / Kubernetes', 'Glance', 'vSAN', 'Keystone'], 0, 'Container private cloud.'))

TYPES = ('  <p>Six platforms, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['Why is Kubernetes alone not a full private cloud?', 'What is the minimum node count for a resilient HCI cluster?', 'Which platform is billed per physical core through Azure?'], 'types 6, 4 and 3') + MAP
         + jump(['OpenStack', 'VCF', 'Azure Local', 'Nutanix', 'CloudStack', 'Kubernetes']) + T1 + T2 + T3 + T4 + T5 + T6
         + '\n  <h3 style="margin-top:34px">All six side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('Service catalogue', 'Approved templates users can launch.', 'Self-service without chaos.', 'Flavors, images, blueprints.'),
    ('Quotas', 'Per-team limits on vCPU, RAM, storage.', 'Fair sharing of fixed hardware.', 'Project quotas.'),
    ('Metering', 'Usage per project over time.', 'Showback/chargeback, capacity planning.', 'Tags, usage reports.'),
    ('Automation', 'Code that builds resources.', 'Minutes instead of weeks; no drift.', 'Terraform, Ansible, Heat.'),
    ('Capacity management', 'Buying hardware ahead of demand.', 'A private cloud cannot burst beyond what you own.', 'Headroom targets, lead times.'),
    ('Operations', 'Patching, upgrades, DR.', 'The hidden cost of private cloud.', '24×7 team, runbooks.')])

DEEP = ('  <h3>Showback vs chargeback</h3>\n  <p><b>Showback</b> reports each team’s usage and cost without billing them; <b>chargeback</b> actually transfers the cost to their budget. Start with showback — it changes behaviour (teams delete idle VMs) without accounting fights.</p>\n'
    '  <h3>Sizing a small private cloud (worked example)</h3>\n' + table(['Item', 'Value'], [['Demand', '200 VMs × 2 vCPU × 8 GiB'], ['Overcommit', 'CPU 4:1, RAM 1:1'], ['Needed', '100 physical cores, 1.6 TiB RAM'], ['Per host', '32 cores, 512 GiB'], ['Hosts', '4 for load + 1 for failure (N+1) = 5'], ['Storage', '3 replicas × 40 TB usable = 120 TB raw']], minw=420) +
    '\n  <p>N+1 and replicas mean you buy roughly 30–200% more raw capacity than you use — part of why private cloud is rarely cheaper unless utilisation is high and steady.</p>\n'
    '  <h3>Try OpenStack at home (optional, needs a strong PC)</h3>\n  <p>Canonical’s single-node OpenStack (“Sunbeam”) installs with snaps on Ubuntu Server LTS with about 4+ cores, 16 GB+ RAM and 100 GB+ disk. The flow is: <code>sudo snap install openstack</code> → <code>sunbeam prepare-node-script --bootstrap | bash -x</code> → <code>sunbeam cluster bootstrap --accept-defaults</code> → <code>sunbeam configure --accept-defaults --openrc demo-openrc</code> → <code>sunbeam launch ubuntu --name test</code>. Check Canonical’s current documentation for the exact snap channel and requirements before you start.</p>\n'
    '  <h3>Private cloud failure modes</h3>\n  <ul><li><b>Capacity cliff:</b> hardware lead times of 8–16 weeks; plan purchases on trend, not on full.</li><li><b>Control-plane outage:</b> APIs down = no new VMs; run 3 controllers.</li><li><b>Upgrade debt:</b> skipping releases makes upgrades risky; schedule them.</li><li><b>Shadow IT:</b> if the portal is slow or restrictive, teams use public cloud anyway — measure request-to-VM time.</li></ul>')

clouds = vendor_tabs('<p><b>AWS:</b> no private-cloud software to install, but AWS Outposts (AWS racks in your DC), Dedicated Hosts, and hybrid tools (Systems Manager, Direct Connect). Private-cloud ideas map to Service Catalog (catalogue), Service Quotas, cost allocation tags (showback).</p>',
    '<p><b>Azure:</b> Azure Local for on-prem private cloud managed from Azure; Azure VMware Solution for hosted VMware; template specs / Managed Applications for catalogues; Azure Policy and quotas; cost analysis by tag.</p>',
    '<p><b>Google Cloud:</b> Google Distributed Cloud (connected and air-gapped) for on-prem; Google Cloud VMware Engine for hosted VMware; sole-tenant nodes; instance templates, quotas and labels for catalogue and showback.</p>') + \
    cloud3([['On-prem stack', 'Outposts', 'Azure Local', 'Google Distributed Cloud'], ['Hosted VMware', 'partner offerings', 'Azure VMware Solution', 'Google Cloud VMware Engine'], ['Dedicated hardware', 'Dedicated Hosts', 'Dedicated Host', 'Sole-tenant nodes'], ['Catalogue item', 'Launch template / Service Catalog', 'Template spec', 'Instance template'], ['Showback', 'Cost allocation tags', 'Cost analysis by tag', 'Labels + billing reports']])

# ------------------------------------------------------------------ practical
MOCKQ.extend([
 (mock('aws', ['EC2', 'Dedicated Hosts', 'Allocate Dedicated Host'], ['Instances', 'Dedicated Hosts', 'Capacity Reservations'], 'Dedicated Hosts',
       [('Instance family', '▾ m5'), ('Availability Zone', '▾ ap-south-1a'), ('Note', 'billed per host-hour once allocated')], 'Allocate'),
  mock('az', ['Home', 'Host groups', 'Create host group'], ['Basics', 'Tags', 'Review + create'], 'Basics',
       [('Host group name', 'hg-private'), ('Region', '▾ Central India'), ('Fault domain count', '▾ 1')], 'Review + create'),
  mock('gcp', ['Compute Engine', 'Sole-tenant nodes', 'Node templates'], ['Node groups', 'Node templates'], 'Node templates',
       [('Node type', '▾ n2-node-80-640'), ('Region', '▾ asia-south1')], 'Create')),
 (mock('aws', ['EC2', 'Launch templates', 'Create launch template'], ['Instances', 'Launch templates', 'AMIs'], 'Launch templates',
       [('Name', 'catalog-small-linux'), ('AMI', '▾ Amazon Linux 2023'), ('Instance type', '▾ t3.micro'), ('Tags', 'team = research')], 'Create launch template'),
  mock('az', ['Home', 'Template specs', 'Create'], ['Basics', 'Edit template', 'Tags'], 'Basics',
       [('Name', 'catalog-small-vnet'), ('Resource group', '▾ rg-private'), ('Version', '1.0')], 'Review + create'),
  mock('gcp', ['Compute Engine', 'Instance templates', 'Create'], ['VM instances', 'Instance templates', 'Instance groups'], 'Instance templates',
       [('Name', 'catalog-small-linux'), ('Machine type', '▾ e2-small'), ('Labels', 'team = research')], 'Create')),
 (mock('aws', ['Service Quotas', 'Amazon EC2'], ['Dashboard', 'AWS services', 'Quota request history'], 'AWS services',
       [('Running On-Demand Standard instances', 'Applied quota: e.g. 32 vCPUs'), ('Action', 'Request increase at account level')], 'Request increase'),
  mock('az', ['Home', 'Quotas', 'Compute'], ['Overview', 'My quotas', 'Request history'], 'My quotas',
       [('Total Regional vCPUs · Central India', 'Usage 0 of 10'), ('Standard BS Family vCPUs', 'Usage 0 of 10')], 'New quota request'),
  mock('gcp', ['IAM & Admin', 'Quotas & system limits'], ['Quotas', 'Quota increase requests'], 'Quotas',
       [('CPUs · asia-south1', '0 / 24'), ('In-use IP addresses', '0 / 8')], 'Edit quotas')),
 (mock('aws', ['Billing', 'Cost allocation tags'], ['Bills', 'Cost Explorer', 'Cost allocation tags'], 'Cost allocation tags',
       [('User-defined tag', 'team'), ('Status', 'Inactive → Activate')], 'Activate'),
  mock('az', ['Home', 'Cost Management', 'Cost analysis'], ['Cost analysis', 'Budgets', 'Exports'], 'Cost analysis',
       [('Group by', '▾ Tag: team'), ('Scope', 'subscription')], 'Download'),
  mock('gcp', ['Billing', 'Reports'], ['Overview', 'Reports', 'Budgets & alerts'], 'Reports',
       [('Group by', '▾ Label · team'), ('Filter', 'Project: tiffingo-lab')], 'Download CSV')),
])

STEP1 = ('1 · See what dedicated (private) hardware costs — read only', tri(
    (['[[EC2]] → [[Dedicated Hosts]] → [[Allocate Dedicated Host]] — look at the options, but <b>do not allocate</b> (billed per hour).'],
     "aws ec2 describe-host-reservation-offerings --filter Name=instance-family,Values=m5 --max-items 3 \\\n  --query 'OfferingSet[].[InstanceFamily,PaymentOption,Duration,HourlyPrice]' --output table",
     'host reservation offerings for the m5 family with durations (seconds) and hourly prices — a whole physical server is far more than one small VM.'),
    (['[[Host groups]] → [[Create]] → look at the options. A host group itself is free; <b>do not add a dedicated host</b> in the lab.'],
     'az vm list-skus --location centralindia --resource-type hostGroups/hosts --query "[].name" -o tsv | head',
     'dedicated host SKUs such as <code>DSv3-Type1</code>, <code>ESv5-Type1</code> — each is a whole physical server.'),
    (['[[Sole-tenant nodes]] → [[Node templates]] → [[Create]] → browse node types; do not create a node group.'],
     'gcloud compute sole-tenancy node-types list --filter="zone:asia-south1-a" --format="table(name,guestCpus,memoryMb)" | head',
     'node types like <code>n2-node-80-640</code> (80 vCPU, 640 GB) — the unit you rent for dedicated hardware.')),
    'Dedicated hardware in a public cloud is the “hosted private” model — compare that hourly price with one VM to see why it is reserved for licensing and compliance needs.')

STEP2 = ('2 · Create a catalogue item (self-service template)', tri(
    (['[[EC2]] → [[Launch templates]] → [[Create launch template]]: name <code>catalog-small-linux</code>, Amazon Linux 2023, t3.micro, tag <code>team=research</code> → [[Create]].', 'Users can now launch only from approved templates (with IAM you can enforce that).'],
     'AMI=$(aws ssm get-parameter --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 --query Parameter.Value --output text)\naws ec2 create-launch-template --launch-template-name catalog-small-linux \\\n  --launch-template-data "{\\"ImageId\\":\\"$AMI\\",\\"InstanceType\\":\\"t3.micro\\",\\"TagSpecifications\\":[{\\"ResourceType\\":\\"instance\\",\\"Tags\\":[{\\"Key\\":\\"team\\",\\"Value\\":\\"research\\"}]}]}"\naws ec2 describe-launch-templates --launch-template-names catalog-small-linux --query "LaunchTemplates[0].[LaunchTemplateId,LatestVersionNumber]" --output text',
     '<code>lt-…  1</code> — a versioned catalogue item. Free; nothing runs until someone launches from it. (AWS Service Catalog adds portfolios and approvals on top.)'),
    (['[[Template specs]] → [[Create template spec]]: resource group <code>rg-private</code>, name <code>catalog-small-vnet</code>, version 1.0, paste a small ARM/Bicep template → [[Create]].'],
     "az group create -n rg-private -l centralindia\ncat > vnet.json <<'EOF'\n{\"$schema\":\"https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#\",\"contentVersion\":\"1.0.0.0\",\n \"resources\":[{\"type\":\"Microsoft.Network/virtualNetworks\",\"apiVersion\":\"2023-09-01\",\"name\":\"team-vnet\",\"location\":\"[resourceGroup().location]\",\n  \"tags\":{\"team\":\"research\"},\"properties\":{\"addressSpace\":{\"addressPrefixes\":[\"10.70.0.0/16\"]}}}]}\nEOF\naz ts create -g rg-private -n catalog-small-vnet -v 1.0 -l centralindia --template-file vnet.json\naz ts list -g rg-private --query \"[].name\" -o tsv",
     '<code>catalog-small-vnet</code> — a versioned template others can deploy with <code>az deployment group create --template-spec &lt;id&gt;</code>.'),
    (['[[Instance templates]] → [[Create instance template]]: name <code>catalog-small-linux</code>, e2-small, Debian 12, label <code>team=research</code> → [[Create]].'],
     'gcloud compute instance-templates create catalog-small-linux --machine-type=e2-small \\\n  --image-family=debian-12 --image-project=debian-cloud --labels=team=research\ngcloud compute instance-templates list --filter="name=catalog-small-linux"',
     'the template listed with machine type <code>e2-small</code>. Free until a VM is created from it.')),
    'A service catalogue is the heart of a private cloud: approved, versioned templates instead of hand-built servers.')

STEP3 = ('3 · Read your quotas (fair sharing of capacity)', tri(
    (['[[Service Quotas]] → [[AWS services]] → [[Amazon Elastic Compute Cloud (Amazon EC2)]] → “Running On-Demand Standard (A, C, D, H, I, M, R, T, Z) instances”.'],
     'aws service-quotas get-service-quota --service-code ec2 --quota-code L-1216C47A \\\n  --query "Quota.[QuotaName,Value]" --output text',
     'the quota name and your vCPU limit (new accounts often have small limits).'),
    (['Search [[Quotas]] → [[Compute]] → filter Region Central India.'],
     'az vm list-usage --location centralindia --query "[?contains(name.value,\'cores\')].{name:localName,used:currentValue,limit:limit}" -o table | head',
     'Total Regional vCPUs and per-family limits with current usage.'),
    (['[[IAM &amp; Admin]] → [[Quotas &amp; system limits]] → filter “CPUs” and region asia-south1.'],
     'gcloud compute regions describe asia-south1 --format="table(quotas.metric,quotas.limit,quotas.usage)" | head -12',
     'rows such as <code>CPUS 24 0</code> — limit and usage per metric.')),
    'A private cloud does the same per project. The difference: when you hit a private-cloud quota, someone may have to buy servers (weeks).')

STEP4 = ('4 · Showback: see cost by team tag', tri(
    (['[[Billing and Cost Management]] → [[Cost allocation tags]] → find <code>team</code> → [[Activate]] (appears after a tagged resource exists; takes up to 24 h).', '[[Cost Explorer]] → [[Group by]] [[Tag]] → team.'],
     'aws resourcegroupstaggingapi get-resources --tag-filters Key=team,Values=research --query "ResourceTagMappingList[].ResourceARN" --output text\naws ce list-cost-allocation-tags --status Inactive --query "CostAllocationTags[?TagKey==\'team\']"',
     'the ARN of the launch template (tagged), and the <code>team</code> tag in the list once AWS has seen it in billing data.'),
    (['[[Cost Management]] → [[Cost analysis]] → [[Group by]] → Tag → team.'],
     'az resource list --tag team=research --query "[].{name:name,type:type}" -o table',
     '<code>team-vnet</code> only after you deploy the template spec; otherwise an empty list. Cost analysis by tag is in the portal (and the Cost Management APIs).'),
    (['[[Billing]] → [[Reports]] → [[Group by]] → Label → team (labels flow into billing data).'],
     'gcloud compute instance-templates describe catalog-small-linux --format="value(properties.labels)"',
     '<code>team=research</code> — every VM from this template carries it into billing reports.')),
    'Showback is “measured service” from NIST: teams see what they use, and idle resources disappear.')

prac = practical(OWN_INTRO + ' You cannot build an OpenStack cloud in a free account, but you can practise the four things that make a private cloud a cloud — dedicated hardware choices, a catalogue, quotas and showback — with free public-cloud tools. (Optional home OpenStack: see the deep dive.)', [SETUP_STEP, STEP1, STEP2, STEP3, STEP4],
    cleanup='<b>AWS:</b> <code>aws ec2 delete-launch-template --launch-template-name catalog-small-linux</code>. '
            '<b>Azure:</b> <code>az group delete -n rg-private --yes --no-wait</code>. '
            '<b>Google Cloud:</b> <code>gcloud compute instance-templates delete catalog-small-linux --quiet</code>. Nothing in this lab costs money.')

mist = mistakes([
    ['Calling a virtualized DC a private cloud.', 'Marketing language.', 'Test against NIST’s five characteristics.'],
    ['Buying hardware for peak demand only.', 'No N+1 and replica overhead in the plan.', 'Size for peak + failure + replicas + growth lead time.'],
    ['Small team running OpenStack from source.', 'Free licence looks cheap.', 'Use a supported distribution or a simpler platform.'],
    ['No metering.', 'Seen as optional.', 'Showback from day one; it drives clean-up.'],
    ['Portal slower than a ticket.', 'Too many approvals.', 'Pre-approve catalogue items within quota.'],
    ['Ignoring upgrades.', '“If it works, don’t touch it.”', 'Plan regular upgrades; skipped releases become migrations.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Private cloud concepts; building blocks; open-source platforms such as OpenStack.'], ['AWS CLF-C02', 'On-premises vs cloud vs hybrid; Outposts; Dedicated Hosts; Service Quotas; cost allocation tags.'], ['AZ-900', 'Private and hybrid cloud; Azure Local, Azure Arc; tags and cost management.'], ['Google Cloud Digital Leader', 'Google Distributed Cloud, VMware Engine, sole-tenant nodes, modernising on-prem.']], minw=560) + \
    qx('1. Which NIST characteristic does a self-service portal provide?', ['broad network access', 'on-demand self-service', 'measured service', 'rapid elasticity'], 1, 'Self-service.') + \
    qx('2. Which OpenStack service handles identity?', ['Nova', 'Keystone', 'Glance', 'Cinder'], 1, 'Keystone.') + \
    qx('3. Which OpenStack service provides compute?', ['Neutron', 'Nova', 'Swift', 'Horizon'], 1, 'Nova.') + \
    qx('4. Combining compute and storage in each node is called…', ['HCI', 'SAN', 'CDN', 'NAS'], 0, 'Hyperconverged.') + \
    qx('5. Reporting team usage without billing them is…', ['chargeback', 'showback', 'backorder', 'cost centre transfer'], 1, 'Showback.') + \
    qx('6. A physical server dedicated to one AWS customer is…', ['Spot Instance', 'Dedicated Host', 'Savings Plan', 'Local Zone'], 1, 'Dedicated Host.')

proj = miniproject('Mini project: private-cloud proposal for the hospital',
    'Turn the hospital’s ticket-driven VMware estate into a private-cloud plan.',
    ['<b>Assess</b> today against NIST’s five characteristics (yes/no + evidence).',
     '<b>Choose</b> a platform from the six types and justify licence, skills and support.',
     '<b>Size</b> it with the deep-dive method (VMs, overcommit, N+1, replicas).',
     '<b>Catalogue:</b> define 3 approved templates (step 2) and quotas per department.',
     '<b>Showback:</b> define tags and a monthly report.',
     '<b>Compare</b> 3-year cost with a hosted private option (AVS/GCVE) and a public-cloud design.'],
    'A 2-page proposal with platform choice, sizing table, catalogue, quotas and a 3-year cost comparison.', 'Module 4 (virtualization) + 3.1 + 5.5 (pricing).')

assemble_v2(HERE, story_h2='Three weeks for one server', hook_html=hk,
    narration='The hospital’s IT team has plenty of servers and VMware licences, yet researchers wait three weeks for each new VM. Its IT head believes it already has a private cloud.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='What it takes to build a private cloud',
    formal='<b>Building a private cloud</b> means adding to pooled, virtualized infrastructure the capabilities that satisfy the NIST cloud characteristics — on-demand self-service, broad network access, resource pooling with multi-tenancy, rapid elasticity and measured service — typically through a cloud management platform (such as OpenStack, VMware Cloud Foundation, Azure Local or Nutanix) that provides identity, APIs, a service catalogue, quotas, automation and metering, for the exclusive use of one organisation.',
    simple='Take your own servers and add a self-service portal, automatic building, fair limits and usage tracking, so teams can use them like a public cloud.',
    interview=['“A private cloud is not just virtualization: it adds self-service, multi-tenancy with quotas, automation and metering — NIST’s five characteristics — for one organisation.”', '“In OpenStack, Keystone authenticates, Nova checks quota and schedules, Glance supplies the image, Neutron the network, and KVM boots the VM.”'],
    terms_rows=[('Cloud management platform', 'Software that makes infrastructure a cloud.'), ('Service catalogue', 'Approved templates for self-service.'), ('Quota', 'Per-project resource limit.'), ('Showback / chargeback', 'Report / bill usage per team.'), ('HCI', 'Compute + storage in each node.'), ('OpenStack', 'Open-source cloud platform.'), ('Keystone, Nova, Neutron, Glance', 'Identity, compute, network, image services.'), ('N+1', 'One spare unit for failure.')],
    exam='Know the NIST characteristics as a test, OpenStack service names, HCI, and the public-cloud equivalents for dedicated hardware (Dedicated Hosts, sole-tenant nodes) and on-prem (Outposts, Azure Local, Google Distributed Cloud).',
    picture_h2='Seven building blocks and the NIST test', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Six private-cloud platforms, one by one', TYPES)],
    how_h2='Inside OpenStack: one “Launch instance” click', how_intro='Follow a VM request through the services of a private cloud.', how_anim=LAUNCH,
    parts_h2='Six things a private cloud must run', parts_html=parts, lv='',
    myth_rows=[('Virtualization = private cloud.', 'Self-service, quotas, automation and metering are also needed.', 'NIST test.'), ('Private cloud is always cheaper at scale.', 'Only with high, steady utilisation and skilled staff.', 'Deep dive sizing.'), ('Open source means free.', 'Operations and support are the real cost.', 'Type 1.')],
    extra_secs=[('deep', 'Deep dive', 'Showback, sizing, OpenStack at home, failure modes', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Explain the seven building blocks of a private cloud and the NIST test.', 'Trace a VM request through OpenStack services.', 'Compare six private-cloud platforms.', 'Create catalogue items, read quotas and set up showback tags on your own account.', 'Size a small private cloud with N+1 and replicas.'],
    next_html='<a href="../03-multi-cloud-vs-hybrid-cloud/">3.3 Multi-cloud vs hybrid cloud</a>.',
    pre='<b>Before you start:</b> 3.1 and Module 4 (virtualization).')
