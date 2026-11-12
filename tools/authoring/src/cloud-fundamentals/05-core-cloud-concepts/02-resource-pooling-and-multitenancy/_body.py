import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def noisy(a, b=None): return capsec('l52_noisy.txt', a, b)
def ten(a, b=None): return capsec('l52_tenancy.txt', a, b)
def aws(a, b=None): return capsec('l52_aws.txt', a, b)
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)

hk = hook('Can three rival cloud kitchens safely use the same software, on the same servers, with the same database?',
    'Yes — that is <b>multitenancy</b>, and it is how almost every SaaS product and every public cloud works. But it has two classic dangers we reproduced in the lab: a query that forgets <code>WHERE tenant_id = …</code> returned <b>every kitchen’s orders</b>, and three “noisy neighbours” on one CPU core made the same job <b>3.8× slower (0.22 s → 0.84 s)</b> — until we gave them a lower CPU weight (<b>0.23 s</b>). This lesson explains <b>resource pooling</b>, the <b>tenancy models</b>, and how isolation really works.',
    ['Resource pooling: why one big shared pool beats many private ones.', 'Single-tenant vs multi-tenant, and the SaaS silo / bridge / pool models.', 'Noisy neighbours and data leaks — and the controls that stop them.'])

def story_scene():
    o = t(180, 12, 'TiffinGo becomes a software company', 9, 'ink', bold=True)
    for i, (n, tn) in enumerate([('Annapurna', 'blue'), ('Dabbawala', 'violet'), ('Ghar-ka-khana', 'amber')]):
        o += box(8 + i * 118, 24, 108, 40, tn, rx=6) + t(62 + i * 118, 48, n, 8, 'ink', bold=True)
        o += f'<path d="M{62 + i * 118},64 L180,84" style="stroke:#999;stroke-width:1.2"/>'
    o += box(80, 84, 200, 34, 'green', rx=8) + t(180, 105, '“TiffinGo for Kitchens” (one SaaS)', 8, 'ink', bold=True)
    o += t(180, 136, 'Shared or separate — app, servers, database?', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Three cloud kitchens, Annapurna, Dabbawala and Ghar-ka-khana, all using one SaaS product called TiffinGo for Kitchens.', story_scene(), 'Many customers, one platform: <tspan font-weight="700" class="s-acc">pooling and tenancy</tspan>.', h=150)
dialogue = '''R> Sir, three other cloud kitchens want to buy our ordering software. Do we build three copies?
A> You could — one copy each, called single-tenant. Or one shared system serving all three, called multi-tenant. Most SaaS products do the second; it is cheaper and easier to update.
K> But Annapurna must never see Dabbawala’s orders. And if Dabbawala runs a huge sale, Annapurna should not slow down.
A> Exactly the two risks: data isolation and noisy neighbours. AWS solves the same problems for millions of customers on shared hardware — that is resource pooling. Let’s see both levels.'''

def poolfig():
    o = t(320, 16, 'Resource pooling: one big shared pool, handed out on demand', 11, 'ink', bold=True)
    o += t(150, 36, 'Without pooling: private capacity per team', 8.6, 'ink', bold=True)
    for i, (n, used) in enumerate([('Kitchen team', 20), ('Billing team', 70), ('Analytics team', 10)]):
        y = 46 + i * 52
        o += box(20, y, 260, 40, 'card', rx=6) + t(30, y + 15, n + ' — own 4 servers', 7.6, 'ink', anchor='start', bold=True) + box(30, y + 22, 240, 10, 'card', rx=2) + box(30, y + 22, 2.4 * used, 10, 'red' if used > 60 else 'amber', rx=2) + t(276, y + 31, f'{used}% used', 6.8, 'ink2', anchor='end')
    o += t(150, 214, 'billing is short of capacity while the others idle', 7.4, 'red', bold=True)
    o += arrow(296, 120, 336, 120)
    o += t(480, 36, 'With pooling: one pool, assigned dynamically', 8.6, 'ink', bold=True)
    o += box(350, 46, 270, 130, 'green', rx=10) + t(485, 64, 'Shared pool: 12 servers', 8.6, 'ink', bold=True)
    for i in range(12):
        tn = ['blue', 'blue', 'violet', 'violet', 'violet', 'violet', 'violet', 'violet', 'amber', 'card', 'card', 'card'][i]
        o += box(362 + (i % 6) * 42, 76 + (i // 6) * 44, 36, 36, tn, rx=4)
    o += t(485, 196, 'kitchen 2 · billing 6 · analytics 1 · 3 free for whoever needs them', 7.2, 'ink', bold=True)
    o += t(320, 240, 'NIST: “resources are pooled to serve multiple consumers … dynamically assigned and reassigned according to demand,', 7.4, 'ink2')
    o += t(320, 254, 'with a sense of location independence” — you choose a Region, not a rack.', 7.4, 'ink2')
    return o
POOLF = bigfig('Left: without pooling, three teams each own four servers; billing is overloaded at 70% while others idle. Right: with pooling, one shared pool of twelve servers is assigned dynamically: kitchen 2, billing 6, analytics 1, three free.', poolfig(), h=264)

def spectrumfig():
    o = t(320, 16, 'Where is the boundary between tenants? Five layers, shared or not', 11, 'ink', bold=True)
    layers = ['Application', 'Database', 'Containers / runtime', 'Virtual machines', 'Physical hosts']
    cols = [('Fully single-tenant', [0, 0, 0, 0, 0], 'on-prem or Dedicated Host'), ('Dedicated VMs (silo)', [0, 0, 0, 0, 1], 'own VMs on shared hosts'), ('Shared app, own DB (bridge)', [1, 0, 1, 1, 1], 'schema/DB per tenant'), ('Fully pooled', [1, 1, 1, 1, 1], 'tenant_id on every row')]
    for c, (n, shared, ex) in enumerate(cols):
        x = 130 + c * 124
        o += t(x + 56, 40, n, 7.4, 'ink', bold=True)
        for i, L in enumerate(layers):
            y = 50 + i * 34
            o += box(x, y, 112, 28, 'green' if shared[i] else 'blue', rx=4) + t(x + 56, y + 18, 'shared' if shared[i] else 'per tenant', 7.2, 'ink', bold=bool(shared[i]))
        o += t(x + 56, 234, ex, 6.8, 'ink2')
    for i, L in enumerate(layers):
        o += t(122, 68 + i * 34, L, 7.6, 'ink', anchor='end', bold=True)
    o += t(320, 256, 'Left = more isolation and cost per tenant · Right = more sharing, lower cost, more care needed for isolation.', 7.6, 'ink2')
    return o
SPEC = bigfig('Grid of five layers (application, database, containers, virtual machines, physical hosts) for four tenancy options: fully single-tenant, dedicated VMs, shared app with own database, fully pooled — showing which layers are shared or per tenant.', spectrumfig(), h=266)

picture = ('  <p>Two ideas, two levels. <b>Resource pooling</b> is what the cloud provider does with its hardware; <b>multitenancy</b> is how many customers share one system — at the provider’s level (millions of AWS accounts on shared hosts) and at your level if you build SaaS.</p>\n' + POOLF +
           '\n  <p>“Single-tenant” and “multi-tenant” are not a yes/no choice — the boundary can be drawn at any layer:</p>\n' + SPEC)

# how it works: a SaaS request with tenant context
RN = {'u': (4, 54, 56, 50, 'user', 'Annapurna', 'staff login'), 'id': (68, 4, 60, 46, 'shield', 'Identity', 'tenant=anna'), 'gw': (68, 104, 60, 46, 'lb', 'API gateway', 'per-tenant limits'),
      'app': (140, 54, 62, 50, 'app', 'Shared app', 'tenant context'), 'db': (214, 4, 64, 46, 'db', 'Shared DB', 'WHERE tenant'), 'q': (214, 104, 64, 46, 'meter', 'Quotas', 'CPU, requests'), 'bill': (292, 54, 64, 50, 'chart', 'Metering', 'per tenant')}
RS = [dict(on=['u', 'id'], hot='id', move=(60, 70, 72, 40, 'login'), head='Step 1 · Who is this, and which tenant?', text='Login returns a token that carries the tenant ID (tenant = annapurna) along with', text2='the user’s role. Every later request carries this token.', svc='Amazon Cognito / Entra ID / any OIDC provider; custom claim “tenant_id”'),
      dict(on=['u', 'id', 'gw'], hot='gw', move=(60, 90, 72, 120, 'request'), head='Step 2 · Per-tenant limits at the door', text='The API gateway checks the token and applies the tenant’s rate limit, so one tenant’s', text2='spike cannot flood the shared service (first noisy-neighbour defence).', svc='API Gateway usage plans, throttling per API key'),
      dict(on=['u', 'id', 'gw', 'app'], hot='app', move=(128, 120, 150, 90, ''), head='Step 3 · Shared app sets the tenant context', text='The same code serves every tenant. It reads tenant_id from the token — never from', text2='a form field the user can change — and keeps it for the whole request.', svc='One deployment, one upgrade for all tenants'),
      dict(on=['u', 'id', 'gw', 'app', 'db'], hot='db', move=(202, 70, 220, 40, 'query'), head='Step 4 · Data access always filtered', text='Every query is scoped: WHERE tenant_id = :tenant, ideally enforced by the database', text2='itself (row-level security) so a forgotten filter cannot leak data.', svc='PostgreSQL row-level security; DynamoDB partition key = tenant; per-tenant IAM policies'),
      dict(on=['u', 'id', 'gw', 'app', 'db', 'q'], hot='q', move=(202, 90, 220, 120, ''), head='Step 5 · Resource quotas', text='Background jobs run with per-tenant concurrency and CPU limits, so Dabbawala’s', text2='big sale report cannot starve Annapurna (second noisy-neighbour defence).', svc='Queues per tenant, Kubernetes resource quotas, cgroup weights'),
      dict(on=list(RN), hot='bill', move=(278, 70, 296, 80, 'usage'), head='Step 6 · Meter usage per tenant', text='Orders, API calls and storage are counted per tenant for billing and for spotting', text2='heavy users — the SaaS version of the cloud’s “measured service”.', svc='Cost allocation tags, per-tenant metrics in CloudWatch')]
SAAS = flow_anim('One request through a multi-tenant SaaS', 'How a shared application keeps Annapurna’s data and performance separate from everyone else’s.', 'Tenant isolation', 'Animation: user logs in and gets a token with tenant ID; API gateway applies per-tenant limits; shared app sets tenant context; database filters by tenant; quotas limit resources; usage is metered per tenant.', RN, RS, hid='saas')

# ------------------------------------------------------------------ types
def mapfig():
    o = t(320, 16, 'Pooling and tenancy — seven ideas you must tell apart', 11, 'ink', bold=True)
    items = [('1', 'Resource pooling', 'provider shares hardware', 'green'), ('2', 'Single tenancy', 'dedicated to one customer', 'blue'), ('3', 'Infrastructure multitenancy', 'many accounts, shared hosts', 'green'),
             ('4', 'SaaS silo model', 'own stack per tenant', 'blue'), ('5', 'SaaS pool model', 'everything shared', 'green'), ('6', 'SaaS bridge model', 'shared app, own DB', 'amber'), ('7', 'Performance isolation', 'stopping noisy neighbours', 'red')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 14 + (i % 4) * 156; y = 32 + (i // 4) * 78
        o += box(x, y, 148, 66, tn, rx=8) + pin(x + 14, y + 16, n) + t(x + 28, y + 20, a, 7.8, 'ink', anchor='start', bold=True) + t(x + 8, y + 46, b, 7, 'ink2', anchor='start')
    o += t(320, 208, 'Types 1–3: what the cloud provider does · Types 4–6: how YOU build SaaS · Type 7: the problem both must solve.', 7.6, 'ink2')
    return o
MAP = bigfig('Map of seven ideas: 1 resource pooling, 2 single tenancy, 3 infrastructure multitenancy, 4 SaaS silo model, 5 SaaS pool model, 6 SaaS bridge model, 7 performance isolation.', mapfig(), h=220)

def a_pool(k):
    o = t(180, 12, ['Morning: kitchen app busy', 'Night: analytics busy', 'Same hardware, reassigned'][k], 9, 'ink', bold=True)
    for i in range(8):
        tn = (['blue'] * 6 + ['card'] * 2)[i] if k == 0 else ((['amber'] * 5 + ['blue'] + ['card'] * 2)[i] if k == 1 else ['blue', 'amber', 'violet', 'green', 'blue', 'amber', 'violet', 'card'][i])
        o += box(14 + (i % 4) * 86, 30 + (i // 4) * 50, 76, 40, tn, rx=5) + t(52 + (i % 4) * 86, 54 + (i // 4) * 50, f'server {i + 1}', 7, 'ink', bold=True)
    o += t(180, 146, ['6 of 8 servers serve morning orders', 'the same servers now run nightly reports', 'many customers, one pool, location independent'][k], 7.6, 'ink', bold=True)
    return o
A_POOL = cap([a_pool(k) for k in range(3)], [('Morning peak', 'Most of the pool serves the ordering app during breakfast orders.', 'Nothing is reserved permanently.'), ('Night batch', 'At night the same machines run analytics jobs — capacity follows demand', 'instead of sitting idle.'), ('One pool for many consumers', 'At cloud scale, millions of customers’ peaks happen at different times,', 'so the pool runs busier and cheaper than any private one.')],
    'Resource pooling in action', 'The same machines serve different work as demand moves.', 'Pooling', 'Animation: eight servers mostly serve the ordering app in the morning, analytics at night, and many customers at once.', 'p1anim')
T1 = vtype(1, 'Resource pooling', 'green',
    '<b>Resource pooling</b> is the NIST essential characteristic in which the provider’s computing resources — processing, memory, storage and network bandwidth — are pooled to serve multiple consumers using a multi-tenant model, with physical and virtual resources dynamically assigned and reassigned according to demand, and with a sense of location independence.',
    'A city’s electricity grid: power stations feed one shared grid; your house draws what it needs and you never know which station produced your electrons. No family builds its own power plant.',
    'Inside TiffinGo, the kitchen, billing and analytics teams used to own separate servers; billing ran out of capacity while analytics idled. Moving all three onto one pooled Kubernetes cluster lets billing borrow capacity at month-end.',
    'The infrastructure of every public cloud; private clouds (OpenStack), Kubernetes clusters, VMware DRS clusters; in your account: Auto Scaling groups and serverless services draw from the provider’s pool.',
    '', A_POOL,
    'demand varies over time or across teams — pooling turns idle capacity into shared headroom.',
    'one workload needs guaranteed, unshared performance or hardware (then dedicate part of the pool).',
    plain='Instead of each customer owning their own computers, the cloud company keeps one huge shared collection of computers and gives each customer a share when they need it — and takes it back when they don’t.',
    how=[('Aggregate', 'Many servers, disks and network links are managed as one pool by virtualization and cloud software.'), ('Abstract', 'Customers request resources by size (2 vCPU, 8 GB), not by physical machine.'), ('Place', 'A scheduler picks where to run each request based on free capacity.'), ('Reclaim', 'When resources are released they return to the pool for others.'), ('Statistical multiplexing', 'Because customers peak at different times, total capacity needed is far less than the sum of everyone’s peaks.'), ('Location independence', 'You choose a Region or AZ, never a specific rack or host.')],
    words=[('NIST', 'the US standards body whose cloud definition everyone uses'), ('scheduler', 'software that decides where to run things'), ('statistical multiplexing', 'sharing works because not everyone peaks at the same time'), ('location independence', 'you do not know or choose the exact machine')],
    diff=table(['', 'Resource pooling', 'Virtualization', 'Multitenancy'], [['What it is', 'a characteristic: shared, dynamically assigned capacity', 'a technology that splits hardware', 'many customers sharing one system'], ['Relationship', 'usually achieved with virtualization', 'enables pooling', 'is how pooled resources are consumed']], minw=520),
    where=['All public clouds', 'Private clouds and Kubernetes platforms', 'Shared data platforms inside companies'],
    realworld='Pooling is the economic engine of cloud providers: AWS, Azure and Google buy servers by the hundreds of thousands and keep them busy across millions of customers whose demand peaks at different times — something no single company’s private servers can match.',
    pro='Pooling is why “Insufficient capacity” errors exist: the pool is finite per AZ and instance type. Flexible designs (several instance types, several AZs, Spot with fallbacks) draw from more of the pool and fail less.')

def a_single(k):
    o = t(180, 12, ['Shared host (default)', 'Dedicated Instance', 'Dedicated Host'][k], 9, 'ink', bold=True)
    o += box(14, 28, 332, 100, 'card', rx=8) + t(180, 42, 'one physical server', 7.6, 'ink2', bold=True)
    vms = [['you', 'X', 'Y', 'Z'], ['you', 'you', 'you', ''], ['you', 'you', '', '']][k]
    for i, v in enumerate(vms):
        if v:
            o += box(24 + i * 80, 52, 72, 46, 'blue' if v == 'you' else 'violet', rx=4) + t(60 + i * 80, 79, 'your VM' if v == 'you' else f'customer {v}', 7.2, 'ink', bold=True)
    o += t(180, 116, ['other customers’ VMs on the same host', 'only your account’s VMs on this hardware', 'the whole server is yours — you see sockets and cores'][k], 7.4, 'ink', bold=True)
    o += t(180, 146, ['cheapest', 'no other customers · hardware chosen by AWS', 'for per-core licences, compliance · billed per host'][k], 7.2, 'ink2')
    return o
A_SINGLE = cap([a_single(k) for k in range(3)], [('Shared tenancy', 'By default your VM may share a physical host with other customers’ VMs,', 'isolated by the hypervisor.'), ('Dedicated Instance', 'Your instances run on hardware used only by your account, but you do not', 'control which host or see its cores.'), ('Dedicated Host', 'You rent a whole physical server: you place instances on it and see its', 'sockets and cores — useful for bring-your-own licences.')],
    'Single tenancy in action', 'Three levels of sharing hardware in EC2.', 'Tenancy', 'Animation: shared host with other customers; dedicated instance with only your VMs; dedicated host where the whole server is yours.', 'p2anim')
T2 = vtype(2, 'Single tenancy (dedicated)', 'blue',
    '<b>Single tenancy</b> means a resource — a physical server, an application instance or a database — serves exactly one customer (tenant); in the cloud it is offered as dedicated instances, dedicated hosts or single-tenant SaaS deployments, trading higher cost for stronger isolation and control.',
    'An independent bungalow: your own walls, garden and meter — maximum privacy and control, maximum cost, and every repair is yours to schedule.',
    'A large hotel chain wants TiffinGo for Kitchens but its contract demands that no other company’s data shares its database or servers. TiffinGo deploys a separate copy for it, on dedicated instances, at a premium price.',
    'AWS Dedicated Instances and Dedicated Hosts, Azure Dedicated Host, Google Cloud sole-tenant nodes; single-tenant SaaS editions (e.g. “dedicated cloud” plans).',
    '', A_SINGLE,
    'regulation or contracts demand dedicated hardware, per-core/socket licences (BYOL), or a customer pays for full isolation.',
    'it is chosen by default “for security” — cost rises sharply, and hypervisor isolation on shared hosts is already strong.',
    plain='One customer gets something entirely to themselves — their own server or their own copy of the software — with nobody else sharing it.',
    how=[('Choose tenancy at launch', 'EC2 tenancy: default (shared), dedicated, or host.'), ('Hardware fenced off', 'Dedicated instances never share a physical server with other accounts.'), ('Dedicated Host control', 'You allocate a host, see its cores/sockets, and place instances on it (host affinity).'), ('Licensing', 'Per-core software licences can be counted against the host’s physical cores.'), ('Cost', 'You pay a dedicated premium (instances) or for the whole host whether full or not.')],
    words=[('tenant', 'one customer of a shared system'), ('BYOL', 'bring your own licence'), ('host affinity', 'keeping an instance on the same physical host'), ('sole-tenant node', 'Google’s name for a dedicated physical server')],
    diff=table(['', 'Shared (default)', 'Dedicated Instance', 'Dedicated Host'], [['Other customers on hardware', 'possible', 'no', 'no'], ['See cores/sockets', 'no', 'no', 'yes'], ['Billing', 'per instance', 'per instance + fee', 'per host'], ['Typical reason', 'everything', 'compliance', 'licensing + compliance']], minw=540),
    where=['Licensed databases and Windows Server (BYOL)', 'Regulated workloads with explicit contracts', 'Enterprise SaaS “dedicated” tiers'],
    realworld='Banks and enterprises moving Windows Server and SQL Server licences to AWS commonly use Dedicated Hosts, because Microsoft licensing for some products counts physical cores — something only a host you fully control can show.',
    pro='Dedicated Instances can still share hardware with <i>other instances in your own account</i> that are not dedicated — the boundary is “no other AWS account”, not “no other workload”.')

def a_infra(k):
    o = t(180, 12, ['Three customers, one host', 'Hypervisor + Nitro isolate them', 'Each sees only its own world'][k], 9, 'ink', bold=True)
    for i, (n, tn) in enumerate([('TiffinGo', 'blue'), ('a bank', 'violet'), ('a game', 'amber')]):
        o += box(14 + i * 114, 28, 104, 50, tn, rx=5) + t(66 + i * 114, 50, n + ' VM', 7.8, 'ink', bold=True) + t(66 + i * 114, 66, 'own account', 6.8, 'ink2')
    if k >= 1:
        o += box(14, 86, 332, 24, 'amber', rx=4) + t(180, 102, 'hypervisor: memory/CPU isolation · Nitro: network, disk, encryption', 7.4, 'ink', bold=True)
    o += box(14, 116, 332, 20, 'card', rx=4) + t(180, 130, 'one physical server', 7.4, 'ink')
    if k == 2:
        o += t(180, 152, 'own VPC, own IAM, own keys — no shared network or memory', 7.4, 'green', bold=True)
    return o
A_INFRA = cap([a_infra(k) for k in range(3)], [('Many accounts, one host', 'VMs of a food app, a bank and a game may run on the same physical server', 'in the same AZ.'), ('Isolation layers', 'The hypervisor isolates CPU and memory; Nitro cards isolate network and', 'storage traffic and encrypt it; IAM separates control.'), ('Each sees only its own world', 'Every account has its own VPC, identities and keys. Shared hardware,', 'not shared data.')],
    'Infrastructure multitenancy in action', 'How a public cloud serves millions of customers on shared hosts.', 'Multitenant IaaS', 'Animation: VMs from three different accounts on one host; hypervisor and Nitro isolate them; each sees only its own VPC, IAM and keys.', 'p3anim')
T3 = vtype(3, 'Infrastructure multitenancy (public cloud)', 'green',
    '<b>Infrastructure multitenancy</b> is the public-cloud model in which workloads of many independent customers (accounts) share the same physical hosts, storage systems and networks, with logical isolation enforced by virtualization, network virtualization, identity and encryption.',
    'A large apartment complex: hundreds of families share land, lifts and water lines, but each flat has its own lock and meter; the building management (provider) guarantees one family cannot walk into another’s flat.',
    'TiffinGo’s EC2 instances in Mumbai may share physical servers with other companies’ instances. That is safe because the hypervisor, Nitro cards, VPC isolation and IAM keep accounts apart — and it is why TiffinGo pays per second instead of buying servers.',
    'Every public IaaS: Amazon EC2/EBS/VPC, Azure VMs/Managed Disks/VNet, Google Compute Engine; isolation technologies: Nitro, Hyper-V, KVM, VPC overlays (Module 4).',
    '', A_INFRA,
    'the default for nearly all cloud workloads — cheap, elastic, well isolated.',
    'rules demand dedicated hardware (type 2), or you need protection from the provider itself (consider confidential computing).',
    plain='Many different companies’ virtual computers run on the same physical machines in the cloud, but strong walls in software and hardware keep each company’s data and traffic completely separate.',
    how=[('Accounts are the top boundary', 'Each customer’s resources, identities and bills live in separate accounts.'), ('Compute isolation', 'The hypervisor gives each VM its own memory and vCPUs (Lesson 4.1 type 3).'), ('Network isolation', 'Each VPC is an overlay with its own tag; Nitro enforces security groups.'), ('Storage isolation', 'Volumes are encrypted and mapped only to their owner’s instances.'), ('Control-plane isolation', 'IAM evaluates every API call against the caller’s account.'), ('Core isolation', 'Different customers never share a CPU core’s hyper-threads (Lesson 4.6).')],
    words=[('account', 'the container for a customer’s resources and bill'), ('VPC', 'your private virtual network'), ('IAM', 'identity and access management'), ('logical isolation', 'separation enforced by software, not separate hardware')],
    diff=table(['', 'Infrastructure multitenancy', 'SaaS multitenancy (types 4–6)'], [['Who shares', 'many cloud customers', 'many customers of your app'], ['Who must isolate', 'the cloud provider', 'you, the SaaS builder'], ['Isolation tools', 'hypervisor, Nitro, VPC, IAM', 'tenant IDs, schemas, policies, quotas']], minw=520),
    where=['All IaaS and PaaS services', 'Serverless platforms (Lambda/Fargate via micro-VMs)', 'Shared object storage (S3)'],
    realworld='Amazon S3 stores data for millions of customers in the same storage fleet; every request is authorised against the bucket owner’s policies, and data is separated logically, not by giving each customer separate disks.',
    pro='In Lambda and Fargate the tenant boundary is a Firecracker micro-VM per execution environment — AWS chose VM-level isolation even for container-sized work because the tenants are strangers.')

def a_silo(k):
    o = t(180, 12, ['One stack per tenant', 'New tenant = new stack', 'Upgrade = N deployments'][k], 9, 'ink', bold=True)
    n = 3 if k == 0 else 4
    for i in range(n):
        x = 10 + i * 87
        nm = ['Annapurna', 'Dabbawala', 'Ghar-ka', 'Hotel X'][i]
        o += box(x, 28, 80, 100, 'green' if (k == 1 and i == 3) else 'blue', rx=6) + t(x + 40, 44, nm, 7, 'ink', bold=True)
        for j, l in enumerate(['app', 'DB', 'VMs']):
            o += box(x + 8, 52 + j * 24, 64, 20, 'card', rx=3) + t(x + 40, 66 + j * 24, l + (' v2' if k == 2 and i < 2 and l == 'app' else ''), 6.8, 'ink')
    o += t(180, 148, ['strongest isolation, highest cost per tenant', 'automation creates a copy in minutes', 'v2 rolled to 2 of 4 tenants so far — versions drift'][k], 7.4, 'red' if k == 2 else 'ink', bold=True)
    return o
A_SILO = cap([a_silo(k) for k in range(3)], [('Own stack per tenant', 'Each kitchen gets its own app servers, database and often its own AWS account.', 'Nothing is shared between tenants.'), ('Onboard by automation', 'A new tenant means deploying a new copy — fine with infrastructure as code.', 'Cost per tenant stays high even when idle.'), ('The upgrade problem', 'Version 2 must be rolled out N times; tenants end up on different versions,', 'which makes support harder.')],
    'The silo model in action', 'Every tenant gets its own copy.', 'Silo', 'Animation: three tenants each with their own app, DB and VMs; a fourth onboarded by automation; upgrades rolled out tenant by tenant, versions drifting.', 'p4anim')
T4 = vtype(4, 'SaaS silo model', 'blue',
    'In the <b>silo model</b> each tenant of a SaaS application receives its own dedicated set of resources — application instances, database and often a separate cloud account or VPC — so no infrastructure is shared between tenants.',
    'Franchise outlets that each have their own kitchen, staff and stock: nothing is shared, quality issues stay local, but every new outlet costs a lot to open.',
    'The hotel chain that demanded full isolation gets a silo: its own AWS account, VPC, app servers and RDS database, created from TiffinGo’s Terraform templates.',
    'Account-per-tenant with AWS Organizations and Control Tower, Azure subscriptions per tenant, Google projects per tenant; deployed with Terraform/CloudFormation StackSets.',
    '', A_SILO,
    'few large tenants, strict compliance, or very different per-tenant performance needs.',
    'you have thousands of small tenants — cost and operational effort per tenant become unmanageable.',
    plain='Each customer gets their own complete copy of the software and its own database and servers — nothing shared.',
    how=[('Template the stack', 'Describe the full tenant environment as code.'), ('Onboard', 'Create an account/VPC and deploy the stack for each tenant.'), ('Isolate by default', 'Network, IAM and data are separate by construction.'), ('Operate N copies', 'Monitoring, backups and upgrades must cover every silo.'), ('Bill', 'Cost per tenant is directly visible per account.')],
    words=[('stack', 'all the resources one application needs'), ('onboarding', 'adding a new customer to the system'), ('account-per-tenant', 'one cloud account per customer')],
    diff=table(['', 'Silo', 'Bridge', 'Pool'], [['Shared app', 'no', 'yes', 'yes'], ['Shared database', 'no', 'no (schema/DB per tenant)', 'yes (tenant_id)'], ['Isolation', 'strongest', 'medium', 'logical only'], ['Cost per tenant', 'highest', 'medium', 'lowest'], ['Onboarding speed', 'minutes–hours (automated)', 'minutes', 'seconds']], minw=560),
    where=['Enterprise and government SaaS tiers', 'Healthcare and finance SaaS', 'Premium “dedicated” plans'],
    realworld='AWS’s SaaS guidance (the SaaS Lens of the Well-Architected Framework) describes silo, pool and bridge as the core tenant-isolation models, and many SaaS companies offer silo deployments only on their premium enterprise plans.',
    pro='Silo makes “noisy neighbour” disappear but creates “noisy operations”: 300 silos means 300 databases to patch. Most mature SaaS products run a hybrid — pool for small tenants, silo for the largest.')

def a_poolm(k):
    o = t(180, 12, ['Everything shared', 'tenant_id on every row', 'Forgotten filter = data leak'][k], 9, 'ink', bold=True)
    o += box(110, 26, 140, 30, 'green', rx=6) + t(180, 45, 'one shared app', 8, 'ink', bold=True)
    o += box(80, 66, 200, 70, 'card', rx=6) + t(180, 80, 'one orders table', 7.6, 'ink', bold=True)
    rows = [('annapurna', 'order 1'), ('annapurna', 'order 2'), ('dabbawala', 'order 1')]
    for i, (tn_, it) in enumerate(rows):
        hi = (k == 1 and tn_ == 'annapurna') or k == 2
        o += box(90, 86 + i * 16, 180, 14, ('red' if k == 2 and tn_ != 'annapurna' else ('green' if hi else 'card')), rx=2) + t(96, 96 + i * 16, f'{tn_} · {it}', 6.8, 'ink', anchor='start')
    o += t(180, 152, ['cheapest; one upgrade for all', 'WHERE tenant_id = annapurna → only its rows', 'SELECT without WHERE → other tenants’ orders shown ⚠'][k], 7.4, 'red' if k == 2 else 'ink', bold=True)
    return o
A_POOLM = cap([a_poolm(k) for k in range(3)], [('Everything shared', 'One app deployment and one database serve all tenants.', 'Lowest cost, instant onboarding, one upgrade.'), ('Rows carry the tenant', 'Every table has a tenant_id; every query filters on it.', 'Our lab: Annapurna sees only its two orders.'), ('The classic bug', 'One query without the filter returned every kitchen’s orders in our lab.', 'Enforce it in the database (row-level security), not just in code.')],
    'The pool model in action', 'Maximum sharing — and the bug it invites.', 'Pool', 'Animation: one shared app and one table; tenant_id filter shows only Annapurna rows; a query without the filter leaks Dabbawala rows.', 'p5anim')
T5 = vtype(5, 'SaaS pool model', 'green',
    'In the <b>pool model</b> all tenants share the same application instances and the same database tables, with every record tagged by a tenant identifier and isolation enforced logically by the application and, ideally, by database policies such as row-level security.',
    'A shared office canteen with labelled lunch boxes: one kitchen, one fridge, everyone’s food on the same shelves — cheap and efficient, as long as nobody picks up a box without reading the name.',
    'Small kitchens sign up for TiffinGo for Kitchens in seconds: they share one app deployment and one orders table. Our lab showed why the filter must be enforced: a query without <code>WHERE tenant_id</code> returned all four orders of three kitchens.',
    'Most mass-market SaaS (CRM, accounting, e-commerce platforms); tools: PostgreSQL row-level security, DynamoDB with tenant partition keys, per-tenant IAM session policies.',
    '', A_POOLM,
    'many small tenants, low price points, fast self-service onboarding.',
    'strict regulatory isolation is required, or tenants differ hugely in size.',
    plain='All customers use the same copy of the software and the same database. Each piece of data is labelled with its owner, and the software must always check that label.',
    how=[('Tag every row', 'Each table has tenant_id; it is part of keys and indexes.'), ('Carry tenant context', 'The tenant comes from the login token, not from user input.'), ('Filter every query', 'WHERE tenant_id = :tenant on every read and write.'), ('Enforce in the database', 'Row-level security policies make the database add the filter itself.'), ('Limit and meter', 'Rate limits and quotas per tenant protect the shared resources.')],
    words=[('tenant_id', 'the column naming which customer a row belongs to'), ('row-level security', 'a database rule that hides rows a session may not see'), ('partition key', 'the key DynamoDB uses to group items')],
    diff=table(['', 'Pool', 'Bridge', 'Silo'], [['Data leak risk', 'highest (one missing filter)', 'lower (separate schemas)', 'lowest'], ['Noisy neighbour risk', 'highest', 'medium', 'none'], ['Cost per tenant', 'lowest', 'medium', 'highest']], minw=520),
    where=['Self-service SaaS with thousands of small customers', 'Free and low-price tiers', 'Internal multi-team platforms'],
    realworld='Large SaaS platforms with millions of small customers, such as online store builders and CRM tools, rely mainly on pooled, multi-tenant databases with tenant identifiers, because a separate database per small customer would be unaffordable.',
    pro='With AWS, you can make IAM enforce the pool boundary: a DynamoDB policy with <code>dynamodb:LeadingKeys</code> = the tenant ID from the session lets each request touch only its own tenant’s items — even if the application code forgets.')

def a_bridge(k):
    o = t(180, 12, ['Shared app tier', 'Separate schema per tenant', 'Move a big tenant out easily'][k], 9, 'ink', bold=True)
    o += box(110, 26, 140, 30, 'green', rx=6) + t(180, 45, 'one shared app', 8, 'ink', bold=True)
    o += box(20, 70, 320, 66, 'card', rx=6) + t(180, 84, 'one database server', 7.4, 'ink2', bold=True)
    for i, n in enumerate(['annapurna', 'dabbawala', 'ghar_ka']):
        moved = k == 2 and i == 1
        o += box(30 + i * 104, 92, 96, 36, 'card' if moved else 'amber', rx=4) + t(78 + i * 104, 114, ('(moved)' if moved else 'schema ' + n), 6.8, 'ink', bold=True)
    if k == 2:
        o += box(250, 140, 100, 20, 'blue', rx=4) + t(300, 154, 'own DB: dabbawala', 6.8, 'ink', bold=True)
    o += t(130, 152, ['', 'tables per tenant, app shared', ''][k], 7.4, 'ink', bold=True)
    return o
A_BRIDGE = cap([a_bridge(k) for k in range(3)], [('Shared app', 'All tenants use the same application deployment, like the pool model.', 'One upgrade for everyone.'), ('Separate schemas', 'Each tenant has its own schema or database on shared database servers;', 'a forgotten filter cannot cross a schema boundary.'), ('Easy to graduate', 'When Dabbawala grows big, its schema moves to its own database server', 'without changing the app.')],
    'The bridge model in action', 'Share the app, separate the data.', 'Bridge', 'Animation: one shared app; one database server with a schema per tenant; a large tenant’s schema moved to its own database.', 'p6anim')
T6 = vtype(6, 'SaaS bridge model (hybrid)', 'amber',
    'The <b>bridge model</b> mixes silo and pool: tenants share some layers (typically the application tier and database servers) while other layers are kept per tenant (typically a separate schema or database per tenant), balancing isolation and cost.',
    'A co-working space: everyone shares the reception, cafeteria and meeting rooms, but each company has its own lockable cabin and filing cabinets.',
    'TiffinGo puts every kitchen in its own PostgreSQL schema on shared RDS servers, with one shared app. When Dabbawala grows large, its schema moves to its own database — the app does not change.',
    'PostgreSQL schemas per tenant, SQL Server databases per tenant on shared instances (Azure SQL elastic pools), MongoDB databases per tenant; our lab used attached SQLite databases.',
    '', A_BRIDGE,
    'mid-sized tenants, compliance that asks for data separation but not separate servers, or a path from pool to silo.',
    'you have tens of thousands of tenants — thousands of schemas complicate migrations and connections.',
    plain='Customers share the same software, but each customer’s data is kept in its own separate section of the database.',
    how=[('Shared application', 'One deployment serves all tenants.'), ('Map tenant to schema', 'A tenant catalogue maps tenant_id → schema/database.'), ('Connect per tenant', 'Each request uses the tenant’s schema (search_path or connection string).'), ('Migrate per schema', 'Schema changes run across all tenant schemas.'), ('Graduate', 'Large tenants move to their own database server.')],
    words=[('schema', 'a named set of tables inside a database'), ('tenant catalogue', 'a lookup table of tenants and where their data lives'), ('elastic pool', 'Azure SQL feature sharing resources among many databases')],
    diff=table(['', 'Bridge', 'Pool', 'Silo'], [['Upgrade effort', 'one app, N schema migrations', 'one', 'N stacks'], ['Data separation', 'per schema/DB', 'per row', 'per stack']], minw=480),
    where=['B2B SaaS with mid-sized customers', 'Regulated SaaS that must separate data per client', 'Multi-tenant analytics'],
    realworld='Azure SQL Database elastic pools were designed for SaaS providers that keep one database per customer while sharing compute among many databases — a bridge model offered as a managed service.',
    pro='Connection pooling is the bridge model’s hidden cost: one pool per schema multiplies connections. Use a single pool and set the schema per transaction (e.g. <code>SET LOCAL search_path</code>) instead.')

def a_noisy(k):
    o = t(180, 12, ['Tenant A alone: 0.22 s', 'Three noisy neighbours: 0.84 s', 'Neighbours get low weight: 0.23 s'][k], 9, 'ink', bold=True)
    o += box(14, 110, 332, 24, 'card', rx=4) + t(180, 126, 'one shared CPU core', 7.6, 'ink', bold=True)
    o += box(14, 30, 80, 70, 'blue', rx=6) + t(54, 60, 'tenant A', 7.8, 'ink', bold=True) + t(54, 76, ['job', 'job', 'job'][k], 7, 'ink2')
    if k >= 1:
        for i in range(3):
            o += box(110 + i * 80, 30, 72, 70, 'red' if k == 1 else 'card', rx=6) + t(146 + i * 80, 60, 'noisy', 7.8, 'ink', bold=True) + t(146 + i * 80, 76, 'weight low' if k == 2 else 'busy loop', 6.8, 'ink2')
    bar = [0.22, 0.84, 0.23][k]
    o += box(14, 140, bar * 380, 12, 'green' if k != 1 else 'red', rx=2)
    return o
A_NOISY = cap([a_noisy(k) for k in range(3)], [('Alone', 'Tenant A’s job takes 0.22 s on one CPU core (median of 3, real).', 'This is its normal speed.'), ('Noisy neighbours', 'Three other tenants run busy loops on the same core with equal priority:', 'the same job now takes 0.84 s — 3.8× slower.'), ('Fair shares fix it', 'Give the neighbours a low CPU weight (nice 19 ≈ small cgroup cpu.weight):', 'tenant A is back to 0.23 s.')],
    'Noisy neighbours in action', 'Our real measurement on one shared CPU core.', 'Noisy neighbour', 'Animation: tenant A alone 0.22 s; with three noisy neighbours 0.84 s; with neighbours at low weight 0.23 s.', 'p7anim')
T7 = vtype(7, 'Performance isolation (the noisy-neighbour problem)', 'red',
    'The <b>noisy-neighbour problem</b> occurs when one tenant’s heavy use of a shared resource — CPU, memory bandwidth, disk I/O, network or database — degrades performance for other tenants; <b>performance isolation</b> is the set of controls (quotas, weights, rate limits, reserved capacity, separation) that prevents it.',
    'One flat in a building running a loud party every night: everyone shares the walls, so everyone suffers — unless the society has noise rules and enforces them.',
    'Dabbawala runs a 3-hour “all orders since 2020” report at lunchtime. In the pool model, Annapurna’s order screen slows down. TiffinGo adds per-tenant query limits and moves reports to a separate replica.',
    'Provider side: CPU credits and fixed-performance instance types, EBS provisioned IOPS, network bandwidth per instance size; your side: API Gateway throttling, per-tenant queues, Kubernetes resource quotas/limits, DynamoDB partition design, read replicas.',
    '', A_NOISY,
    'always in shared systems: plan quotas, rate limits and fair-share scheduling from day one.',
    'you rely on “everyone behaves” — one large or buggy tenant can take everyone down.',
    plain='When many customers share the same machine, one customer using too much can slow everyone else down. Rules that give each customer a fair share stop this.',
    how=[('Measure per tenant', 'Collect CPU, requests, queries and storage per tenant.'), ('Limit at the edge', 'Rate limits per tenant/API key at the gateway.'), ('Share fairly inside', 'cgroup weights/limits, Kubernetes requests/limits, separate thread pools.'), ('Queue heavy work', 'Per-tenant queues so one tenant’s backlog does not block others.'), ('Separate the heaviest', 'Move big tenants or heavy reports to their own capacity (bridge/silo).'), ('Provider level', 'Choose instance types with fixed performance or provisioned IOPS when steady performance matters.')],
    words=[('quota', 'a maximum amount a tenant may use'), ('rate limit / throttling', 'a cap on requests per second'), ('cgroup weight', 'a share of CPU relative to others'), ('steal time', 'CPU time a VM lost to other VMs on the host')],
    diff=table(['', 'Noisy neighbour', 'Data leak between tenants'], [['What breaks', 'performance', 'confidentiality'], ['Cause', 'shared capacity, no limits', 'missing tenant filter / policy'], ['Fix', 'quotas, weights, separation', 'tenant context, row-level security, IAM']], minw=480),
    where=['Every shared database, cluster and API', 'Burstable cloud instances (CPU credits)', 'Kubernetes clusters shared by teams'],
    realworld='Cloud providers expose noisy-neighbour effects as “steal time” on burstable or oversubscribed VMs; AWS designed EBS and network limits per instance size and offers provisioned IOPS precisely so that one customer’s heavy I/O does not degrade another’s.',
    pro='Our lab used <code>nice</code> as a stand-in, but the real tool is the cgroup v2 <code>cpu.weight</code> (1–10000, default 100) — Kubernetes converts a pod’s CPU <i>request</i> into exactly this weight, which is why requests matter even when limits are unset.')

SUMMARY = table(['#', 'Idea', 'Level', 'Shared', 'Isolation by', 'Cost'], [
    ['1', 'Resource pooling', 'provider', 'all hardware', 'scheduling + virtualization', 'lowest overall'], ['2', 'Single tenancy', 'provider / SaaS', 'nothing', 'dedicated hardware/stack', 'highest'],
    ['3', 'Infrastructure multitenancy', 'provider', 'hosts, storage, network', 'hypervisor, Nitro, VPC, IAM', 'low'], ['4', 'Silo model', 'SaaS', 'nothing per tenant', 'separate stacks/accounts', 'high'],
    ['5', 'Pool model', 'SaaS', 'app + DB tables', 'tenant_id + RLS + IAM', 'lowest'], ['6', 'Bridge model', 'SaaS', 'app (+ DB servers)', 'schema/DB per tenant', 'medium'], ['7', 'Performance isolation', 'both', '—', 'quotas, weights, limits', '—']], minw=680)
CHECK = ('  <h3>Check yourself: which idea fits?</h3>\n' +
    qx('A. 5,000 small shops sign up online for ₹500/month each.', ['Silo model', 'Pool model', 'Dedicated Hosts', 'Outposts'], 1, 'Many small tenants, low price, instant onboarding.') +
    qx('B. A bank customer’s contract forbids sharing servers with any other company.', ['Pool', 'Silo (and/or dedicated tenancy)', 'Bridge', 'Spot'], 1, 'Full isolation per tenant.') +
    qx('C. One tenant’s nightly report slows everyone’s app.', ['Data leak', 'Noisy neighbour — add quotas or separate the workload', 'Region outage', 'DNS issue'], 1, 'Performance isolation is missing.') +
    qx('D. Shared app, but each customer’s data must be in a separate schema.', ['Bridge model', 'Pool model', 'Silo model', 'Single tenancy'], 0, 'Shared app tier, separate data tier.') +
    qx('E. NIST’s characteristic “resources dynamically assigned to many consumers with location independence” is…', ['Broad network access', 'Resource pooling', 'Measured service', 'Rapid elasticity'], 1, 'The definition of resource pooling.'))

TYPES = ('  <p>Seven ideas that are easy to mix up. Types 1–3 are what the provider does; 4–6 are the choices you make when you build SaaS; 7 is the problem every shared system must solve. Same pattern as before for each.</p>\n'
         + challenge(['How can IAM — not your code — stop a DynamoDB query from reading another tenant’s data?', 'Why do Kubernetes CPU requests matter even with no limits set?', 'Where exactly is the tenant boundary in AWS Lambda?'], 'types 5, 7 and 3') + MAP
         + jump(['Pooling', 'Single tenancy', 'Infra multitenancy', 'Silo', 'Pool', 'Bridge', 'Noisy neighbour']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = table(['Layer', 'Isolation control', 'AWS example'], [
    ['Identity', 'tenant ID in token; per-tenant roles', 'Cognito custom claims, IAM session tags'], ['Network', 'separate VPCs/subnets or security groups', 'VPC per silo tenant; PrivateLink'],
    ['Compute', 'quotas, weights, dedicated capacity', 'ECS/EKS resource limits, Dedicated Hosts'], ['Data', 'tenant_id + RLS, schema, separate DB', 'RDS PostgreSQL RLS; DynamoDB LeadingKeys'],
    ['Encryption', 'per-tenant keys', 'KMS key per tenant'], ['Cost', 'tag every resource with tenant', 'cost allocation tag “tenant”']], minw=560)

DEEP = ('  <h3>Why pooling makes cloud cheaper: a small calculation</h3>\n  <p>Suppose 100 companies each need up to 10 servers at their own peak, but on average use 3. Owning private capacity means buying 1,000 servers. If their peaks happen at different times, a shared pool might need only about 400 servers to serve everyone’s peaks with headroom — the provider buys fewer servers per customer and keeps them busier. That margin is part of what makes per-second pricing possible.</p>\n'
    '  <h3>Isolation at the provider: what AWS shares and what it does not</h3>\n' + table(['Resource', 'Shared between customers?', 'How isolated'], [
    ['Physical host', 'yes (default tenancy)', 'hypervisor, Nitro, no shared cores'], ['CPU core hyper-threads', 'no', 'core isolation'], ['Memory', 'host RAM shared, never pages', 'EPT; memory scrubbed before reuse'],
    ['Disks (EBS)', 'storage fleet shared', 'per-volume mapping, encryption'], ['Network', 'physical fabric shared', 'VPC overlays, security groups on Nitro'], ['Control plane', 'shared APIs', 'IAM per request']], minw=560) +
    '\n  <h3>Shared responsibility for multitenancy</h3>\n  <p>The provider guarantees isolation <b>between accounts</b>. Isolation <b>between your own SaaS tenants</b> is your responsibility: tenant context, data partitioning, per-tenant limits and per-tenant keys. AWS’s SaaS Lens (Well-Architected) and the “SaaS Factory” guidance describe these patterns in detail.</p>')

clouds = vendor_tabs('<p><b>AWS:</b> pooling across EC2/S3/Lambda fleets; tenancy options default, Dedicated Instance, Dedicated Host; SaaS tools: Organizations/Control Tower (silo), Cognito claims, IAM session tags and DynamoDB LeadingKeys (pool), SaaS Lens.</p>',
    '<p><b>Azure:</b> shared infrastructure with Azure Dedicated Host option; SaaS patterns in the Azure Architecture Center (tenancy models); Azure SQL elastic pools (bridge), subscriptions per tenant (silo), Microsoft Entra ID for multi-tenant apps.</p>',
    '<p><b>Google Cloud:</b> shared infrastructure with sole-tenant nodes; projects per tenant (silo), Cloud SQL/AlloyDB with row-level security (pool), GKE namespaces and resource quotas for tenant isolation.</p>') + \
    cloud3([['Dedicated hardware', 'Dedicated Host / Instance', 'Dedicated Host', 'Sole-tenant nodes'], ['Silo boundary', 'Account per tenant', 'Subscription per tenant', 'Project per tenant'], ['Bridge helper', 'RDS schemas', 'SQL elastic pools', 'Cloud SQL databases'],
            ['Pool enforcement', 'IAM LeadingKeys, RLS', 'RLS, Entra ID claims', 'RLS, IAM conditions'], ['Per-tenant quotas', 'API Gateway usage plans', 'API Management quotas', 'Apigee quotas']])

proof = [
    ('Step 1 · Noisy neighbours on one core (real)', code('bash', 'terminal', "taskset -c 0 python3 job.py                       # tenant A alone\nfor i in 1 2 3; do taskset -c 0 python3 -c 'while True: pass' & done\ntaskset -c 0 python3 job.py                       # with 3 noisy tenants\n# restart the neighbours with: nice -n 19 …        # low CPU weight", noisy('== 1)')), 'Same job, same core: 0.22 s alone, 0.84 s with three equal-priority neighbours, 0.23 s once neighbours get a low weight. Fair-share scheduling is the cure.'),
    ('Step 2 · Pool, bridge and silo data models (real)', code('python', 'l52_tenancy.py', "db.execute('select tenant_id, item from orders')                     # forgot the filter!\ndb.execute('select item, amount from orders where tenant_id=?', ('annapurna',))\ndb.execute(\"create view v_annapurna as … where tenant_id='annapurna'\")\n# bridge: one schema (attached DB) per tenant · silo: one DB file per tenant", ten('== 1)')), 'The first query is the most common multi-tenant bug — it returned every kitchen’s orders. Views or row-level security make the filter impossible to forget.'),
    ('Step 3 · Tag resources per tenant (emulator)', code('bash', 'terminal', "aws ec2 run-instances … --tag-specifications 'ResourceType=instance,Tags=[{Key=tenant,Value=annapurna}]'\naws ec2 describe-instances --filters Name=tag:tenant,Values=annapurna", aws('== 1)', '== 3)')), 'With a “tenant” tag on every resource you can find, secure and bill everything belonging to one customer.')]

prac = practical('Every step has a <b>UI way</b> and a <b>CLI way</b>. Steps 1–2 run on your own computer; steps 3–4 use AWS (<b>CLI outputs from the moto emulator</b>). Dedicated tenancy costs extra — do not leave such instances running.', [
    ('1 · Make and fix a noisy neighbour', uicli(
        ['Windows: start three copies of a CPU-heavy program (or a video export) and a game/benchmark; watch it slow down in [[Task Manager]] → [[Processes]].', 'Right-click the heavy programs in [[Details]] → [[Set priority]] → [[Below normal]]; the benchmark speeds up again.', 'Linux desktop: [[System Monitor]] → right-click process → [[Change Priority]].'],
        code('bash', 'terminal (Linux/WSL)', "taskset -c 0 python3 job.py                        # alone\nfor i in 1 2 3; do taskset -c 0 python3 -c 'while True: pass' & done\ntaskset -c 0 python3 job.py                        # slower\npkill -f 'while True'\nfor i in 1 2 3; do taskset -c 0 nice -n 19 python3 -c 'while True: pass' & done\ntaskset -c 0 python3 job.py                        # fast again\npkill -f 'while True'", noisy('== 1)')), ui_label='UI way — Task Manager / System Monitor'),
        'Priority/weight is the same idea as cgroup cpu.weight in containers and Kubernetes CPU requests.'),
    ('2 · See a tenant data leak and stop it', uicli(
        ['Install [[DB Browser for SQLite]] → [[New Database]] → run the SQL on the right in [[Execute SQL]].', 'Run the query without WHERE — every tenant appears. Then create the view and query only the view.'],
        code('sql', 'SQLite', "CREATE TABLE orders(tenant_id, item, amount);\nINSERT INTO orders VALUES ('annapurna','order 1',250),('annapurna','order 2',180),\n                          ('dabbawala','order 1',300),('ghar-ka-khana','order 1',120);\nSELECT tenant_id, item FROM orders;                                  -- leak!\nCREATE VIEW v_annapurna AS SELECT item, amount FROM orders WHERE tenant_id='annapurna';\nSELECT * FROM v_annapurna;", ten('== 1)', '== 2)')), ui_label='UI way — DB Browser for SQLite'),
        'In PostgreSQL use row-level security: <code>ALTER TABLE orders ENABLE ROW LEVEL SECURITY; CREATE POLICY p ON orders USING (tenant_id = current_setting(\'app.tenant\'));</code>'),
    ('3 · Tag resources by tenant and find them', uicli(
        ['[[EC2]] → [[Launch instances]] → [[Add additional tags]] → Key <code>tenant</code>, Value <code>annapurna</code>.', '[[Instances]] → search bar → <code>tag:tenant = annapurna</code>.', 'Or [[Resource Groups & Tag Editor]] → [[Tag Editor]] → Region ap-south-1, tag key tenant → [[Search resources]].'],
        code('bash', 'terminal', "aws ec2 run-instances --image-id $AMI --instance-type m5.large \\\n  --tag-specifications 'ResourceType=instance,Tags=[{Key=tenant,Value=annapurna}]'\naws ec2 describe-instances --filters Name=tag:tenant,Values=annapurna \\\n  --query 'Reservations[].Instances[].InstanceId' --output text", aws('== 1)', '== 3)')), ui_label='UI way — AWS Management Console'),
        'Then activate “tenant” as a cost allocation tag (Billing → Cost allocation tags) to see cost per tenant in Cost Explorer.'),
    ('4 · Choose dedicated tenancy (look at the option)', uicli(
        ['[[EC2]] → [[Launch instances]] → [[Advanced details]] → [[Tenancy]]: [[Shared]] / [[Dedicated instance]] / [[Dedicated host]].', 'Dedicated Hosts: [[EC2]] → [[Dedicated Hosts]] → [[Allocate Dedicated Host]] (Lesson 4.6).'],
        code('bash', 'terminal', 'aws ec2 run-instances --image-id $AMI --instance-type m5.large --placement Tenancy=dedicated\naws ec2 describe-instances --query "Reservations[].Instances[].[InstanceId,Placement.Tenancy]"'), ui_label='UI way — AWS Management Console'),
        'Only for practice on a real account: dedicated instances add an hourly fee — terminate immediately.')],
    cleanup='<code>pkill -f "while True"</code> locally. AWS: terminate the tagged instances ([[Instance state]] → [[Terminate instance]] / <code>aws ec2 terminate-instances</code>).'.replace('[[', '<b>').replace(']]', '</b>'))

mist = mistakes([
    ['Taking tenant_id from a request parameter.', 'Easy to code.', 'Take it only from the authenticated token; users can change parameters.'],
    ['Relying on every developer to add WHERE tenant_id.', 'It works until someone forgets.', 'Enforce with row-level security, views or IAM conditions.'],
    ['No per-tenant limits.', '“Customers will behave.”', 'Rate limits, quotas, queues per tenant; move heavy tenants out.'],
    ['Buying Dedicated Instances “for security”.', 'Misunderstanding shared tenancy.', 'Shared hosts are isolated by the provider; dedicate only for licensing/compliance.'],
    ['Silo for thousands of tiny tenants.', 'Strong isolation feels safest.', 'Pool small tenants; silo only the large or regulated ones.'],
    ['Untagged resources in a multi-tenant account.', 'Tags added “later”.', 'Require a tenant tag at creation (tag policies); otherwise cost and cleanup per tenant are impossible.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Resource pooling, multitenancy, essential cloud characteristics.'], ['AWS CLF-C02', 'Benefits of the cloud (economies of scale), tenancy options (Dedicated Instances/Hosts), shared responsibility.'], ['AZ-900', 'Cloud characteristics; Azure Dedicated Host.'], ['Google Cloud Digital Leader', 'Multi-tenancy and shared infrastructure, sole-tenant nodes.']], minw=520) + '\n  <h3>Exam-style questions with explanations</h3>\n' + \
    qx('1. Which NIST characteristic describes providers serving many consumers from shared resources assigned dynamically?', ['On-demand self-service', 'Resource pooling', 'Measured service', 'Broad network access'], 1, 'Resource pooling, with location independence.') + \
    qx('2. Which EC2 option gives visibility of physical sockets and cores for licensing?', ['Dedicated Instance', 'Dedicated Host', 'Spot Instance', 'Reserved Instance'], 1, 'Dedicated Hosts expose the physical server.') + \
    qx('3. The cloud is cheaper partly because of economies of scale. What enables them?', ['Single tenancy', 'Pooling resources across many customers', 'Using only one Region', 'Paying upfront'], 1, 'Large shared pools keep hardware busy across many customers.') + \
    qx('4. In a multi-tenant SaaS, who is responsible for isolating tenants’ data from each other?', ['The cloud provider', 'The SaaS builder', 'The end user', 'Nobody'], 1, 'The provider isolates accounts; the SaaS builder isolates its own tenants.') + \
    qx('5. Tenant A’s app slows whenever tenant B runs reports on the shared database. This is…', ['a data leak', 'a noisy-neighbour problem', 'a DNS problem', 'vendor lock-in'], 1, 'Shared capacity without per-tenant limits.')

proj = miniproject('Mini project: a tiny multi-tenant order API with three isolation levels',
    'Build TiffinGo for Kitchens as a small API that supports pool, bridge and silo tenants — and prove isolation with tests.',
    ['<b>API:</b> FastAPI/Flask with <code>GET /orders</code>; read tenant from a signed JWT (use a fixed secret for the lab).',
     '<b>Pool:</b> PostgreSQL (Docker) table <code>orders(tenant_id, …)</code> with row-level security; set <code>app.tenant</code> per request.',
     '<b>Bridge:</b> a schema per tenant; set <code>search_path</code> per request from a tenant catalogue table.',
     '<b>Silo:</b> one tenant with its own database container; the catalogue stores its connection string.',
     '<b>Tests:</b> write pytest tests proving tenant A never sees B’s rows — including a test that deliberately omits WHERE and still sees only its rows (RLS).',
     '<b>Noisy neighbour:</b> add a per-tenant rate limit (e.g. 5 requests/s) and show with <code>hey</code> that a flood from tenant B does not slow tenant A.',
     '<b>Cloud mapping:</b> write which AWS services you would use for each part (Cognito, API Gateway usage plans, RDS RLS, Organizations for silo).'],
    'Passing isolation tests, a rate-limit demo, and a one-page design.', 'This lesson + SQL + Docker + 4.5 (containers).')

assemble_v2(HERE, story_h2='Three rival kitchens, one software', hook_html=hk,
    narration='TiffinGo’s ordering software is so good that other cloud kitchens want to use it. Selling it as a service raises two questions: what to share, and how to keep each customer safe from the others.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Resource pooling and multitenancy',
    formal='<b>Resource pooling</b> (NIST SP 800-145) is the characteristic in which a provider’s computing resources are pooled to serve multiple consumers using a multi-tenant model, with physical and virtual resources dynamically assigned and reassigned according to consumer demand and a sense of location independence. <b>Multitenancy</b> is an architecture in which a single instance of software or infrastructure serves multiple customers (tenants), each logically isolated from the others while sharing underlying resources.',
    simple='Pooling: the cloud keeps one big shared pile of computers and hands out pieces on demand. Multitenancy: many customers share the same system, each kept separate from the others.',
    interview=['“Resource pooling means the provider’s compute, storage and network are shared among many customers and assigned dynamically on demand; customers choose a Region, not a specific machine. It is what gives the cloud its economies of scale.”', '“Multitenancy is many customers sharing one system with logical isolation. In SaaS there are three models: silo — a stack per tenant, pool — everything shared with tenant IDs, and bridge — shared app with per-tenant schemas.”', '“The two risks are data leaks and noisy neighbours; I enforce tenant isolation in the database with row-level security and use per-tenant quotas. In a lab, three noisy processes made a job 3.8× slower until I lowered their CPU weight.”'],
    terms_rows=[('Tenant', 'One customer of a shared system.'), ('Resource pooling', 'Shared resources assigned on demand.'), ('Multitenancy', 'Many tenants share one system.'), ('Single tenancy', 'Dedicated to one tenant.'), ('Silo / pool / bridge', 'SaaS isolation models.'), ('Noisy neighbour', 'One tenant degrading others.'), ('Row-level security', 'DB enforces per-tenant rows.'), ('Dedicated Host', 'Whole physical server for one account.')],
    exam='CLF-C02: “economies of scale” come from pooling; Dedicated Hosts for licensing/compliance; Dedicated Instances isolate hardware per account. Expect “which characteristic is this?” questions on resource pooling.',
    picture_h2='Pooling, and where the tenant boundary can be drawn', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven pooling and tenancy ideas, one by one', TYPES)],
    how_h2='One request through a multi-tenant SaaS', how_intro='How identity, gateway, application, database, quotas and metering work together to keep tenants apart.', how_anim=SAAS,
    parts_h2='Isolation controls at every layer', parts_html=parts, lv='',
    myth_rows=[('Shared hardware means shared data.', 'Accounts are isolated by hypervisor, Nitro, VPC and IAM.', 'Type 3.'), ('Multitenancy is only for big providers.', 'Every SaaS you build decides its tenancy model.', 'Types 4–6.'), ('A filter in code is enough.', 'One forgotten WHERE leaked all tenants in our lab.', 'Proof step 2.')],
    extra_secs=[('deep', 'Deep dive', 'Why pooling is cheaper, what AWS shares between customers, shared responsibility for tenancy', DEEP)],
    clouds_html=clouds, proof_h2='Real proof: noisy neighbours and a tenant data leak', proof_intro='Steps 1–2 are real runs on our lab machine (10 Nov 2026); step 3 uses the moto AWS emulator.', proof_steps=proof,
    practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Explain resource pooling and why it creates economies of scale.', 'Explain single vs multi-tenancy at the infrastructure and SaaS level.', 'Choose between silo, pool and bridge models.', 'Detect and prevent noisy neighbours and tenant data leaks.', 'Use tags and tenancy options in AWS from the console and CLI.'],
    next_html='<a href="../03-scalability-elasticity-and-cloud-bursting/">5.3 Scalability, elasticity and cloud bursting</a>.',
    pre='<b>Before you start:</b> <a href="../01-regions-availability-zones-and-edge-locations/">5.1</a> and <a href="../../04-virtualization/06-pros-cons-consolidation-and-hypervisor-security/">4.6 (noisy neighbours, isolation)</a>.')
