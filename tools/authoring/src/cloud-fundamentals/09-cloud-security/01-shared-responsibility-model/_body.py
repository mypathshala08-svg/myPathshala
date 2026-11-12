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


hk = hook('A TiffinGo intern made a storage bucket public “for one day” to share menu photos. It also held 4,000 customer addresses. Whose fault was the leak — AWS’s or TiffinGo’s?',
    'TiffinGo’s. Under the <b>shared responsibility model</b>, the provider secures the <b>cloud itself</b> (buildings, hardware, hypervisors, its managed services) and the customer secures <b>what it puts in the cloud</b> (data, identities, configuration). Where the line sits depends on the service model. This lesson draws the line for six models one by one, walks through real incidents to see who fixes what, and on <b>your own</b> account you download the provider’s audit reports (their half) and lock down public access and exposed resources (your half).',
    ['“Security <i>of</i> the cloud” vs “security <i>in</i> the cloud” — the exam phrase.', 'Why data, identities and access are always yours, even in SaaS.', 'Shared controls: patching and training are split, not handed over.'])

def story_scene():
    o = t(180, 12, 'Where was the hole?', 9, 'ink', bold=True)
    o += box(8, 28, 160, 74, 'green', rx=8) + t(88, 48, 'Provider side', 8.4, 'ink', bold=True) + t(88, 64, 'data centre, disks,', 7, 'ink2') + t(88, 78, 'S3 service itself', 7, 'ink2') + t(88, 92, 'working fine', 7.4, 'ink', bold=True)
    o += box(192, 28, 160, 74, 'red', rx=8) + t(272, 48, 'Customer side', 8.4, 'ink', bold=True) + t(272, 64, 'bucket made public', 7, 'ink2') + t(272, 78, 'no block, no alert', 7, 'ink2') + t(272, 92, 'data exposed', 7.4, 'ink', bold=True)
    o += t(180, 122, 'Most cloud breaches are configuration, not provider failure', 7.4, 'ink', bold=True)
    return o
scene_svg = scene('Provider side (data centre, disks, S3 service) working fine; customer side: bucket made public with no block or alert, data exposed.', story_scene(), 'The provider gave a safe lock; <tspan font-weight="700" class="s-acc">we left the door open</tspan>.', h=132)
dialogue = '''K> Sir, isn’t AWS supposed to keep our data safe? We pay them.
A> AWS keeps the storage service safe — nobody can walk into their data centre and take our disks. But who may read our bucket is our setting.
R> So the cloud is not “someone else’s problem”.
A> Half of it is. The other half — identities, data, network rules, patching our VMs — is ours. And the half changes with IaaS, PaaS and SaaS.
K> How do we know exactly where the line is?
A> Each provider publishes it. Let’s draw it for every service model.'''

def linefig():
    o = t(320, 16, 'Who secures what, by service model', 11, 'ink', bold=True)
    layers = ['Data & content', 'Identities & access', 'Applications', 'Network controls', 'Operating system', 'Virtualization', 'Physical hosts & network', 'Data centre']
    models = [('On-prem', 8), ('IaaS', 5), ('PaaS', 3), ('SaaS', 2)]
    for i, l in enumerate(layers): o += t(96, 46 + i * 22, l, 7.4, 'ink', anchor='end')
    for j, (m, mine) in enumerate(models):
        x = 110 + j * 128
        o += t(x + 58, 32, m, 8.4, 'ink', bold=True)
        for i in range(8):
            tone = 'blue' if i < mine else 'green'
            if m == 'SaaS' and i in (1,): tone = 'amber'
            if m == 'PaaS' and i == 3: tone = 'amber'
            o += box(x, 36 + i * 22, 116, 18, tone, rx=3)
    o += box(110, 222, 12, 10, 'blue', rx=2) + t(126, 231, 'customer', 7, 'ink', anchor='start') + box(200, 222, 12, 10, 'green', rx=2) + t(216, 231, 'provider', 7, 'ink', anchor='start') + box(290, 222, 12, 10, 'amber', rx=2) + t(306, 231, 'shared / depends on service', 7, 'ink', anchor='start')
    o += t(320, 250, 'Data, identities and access are always the customer’s — in every model.', 7.6, 'ink', bold=True)
    return o
LINE = bigfig('Grid of eight layers from data down to data centre for on-premises, IaaS, PaaS and SaaS: customer owns everything on-premises, top five layers in IaaS, top three in PaaS, top two in SaaS (identities shared), provider owns the rest.', linefig(), h=260)

def ofinfig():
    o = t(320, 16, 'Security OF the cloud vs security IN the cloud', 11, 'ink', bold=True)
    o += box(20, 34, 290, 120, 'green', rx=10) + t(165, 56, 'Provider: security OF the cloud', 9, 'ink', bold=True)
    for i, s in enumerate(['facilities, guards, power', 'hardware, disposal of disks', 'hypervisor and host OS', 'global network, Regions, AZs', 'managed service software']): o += t(165, 76 + i * 15, s, 7.2, 'ink')
    o += box(330, 34, 290, 120, 'blue', rx=10) + t(475, 56, 'Customer: security IN the cloud', 9, 'ink', bold=True)
    for i, s in enumerate(['data classification + encryption choices', 'IAM users, roles, MFA, keys', 'network rules (SGs, NSGs, firewalls)', 'guest OS patching (IaaS)', 'app code, configuration, logging']): o += t(475, 76 + i * 15, s, 7.2, 'ink')
    o += t(320, 176, 'Shared controls: patch management, configuration management, awareness and training — each side does its own part.', 7.4, 'ink2')
    return o
OFIN = bigfig('Two boxes: provider is responsible for security of the cloud (facilities, hardware, hypervisor, network, managed service software); customer for security in the cloud (data, IAM, network rules, guest OS patching, app configuration).', ofinfig(), h=186)

picture = ('  <p>The line moves up as the provider manages more of the stack:</p>\n' + LINE +
           '\n  <p>AWS’s wording, used in exams:</p>\n' + OFIN +
           '\n  <h3>The same idea, three providers</h3>\n' + table(['Provider', 'Their phrase', 'Key point'], [['AWS', '“Security of the cloud” vs “security in the cloud”', 'customer owns data, IAM, OS (IaaS), network config, encryption choices'], ['Microsoft Azure', '“Shared responsibility in the cloud”', 'information and data, devices, accounts and identities are always the customer’s'], ['Google Cloud', '“Shared responsibility and shared fate”', 'Google also helps customers succeed with secure defaults, blueprints and guidance']], minw=620))

RN = {'inc': (4, 54, 50, 50, 'shield', 'Incident', 'what broke?'), 'lay': (66, 4, 62, 46, 'gear', 'Layer', 'which one?'), 'mod': (66, 104, 62, 46, 'cloud', 'Model', 'IaaS/PaaS/SaaS'),
      'own': (142, 54, 60, 50, 'user', 'Owner', 'who fixes'), 'prov': (216, 4, 62, 46, 'server', 'Provider', 'patch, report'), 'cust': (216, 104, 62, 46, 'app', 'Customer', 'config, data'), 'less': (292, 54, 64, 50, 'chart', 'Lesson', 'guard-rail')}
RS = [dict(on=['inc'], hot='inc', move=None, head='Step 1 · Something goes wrong', text='Case A: a hypervisor vulnerability is announced. Case B: TiffinGo’s bucket is public.', text2='Case C: an EC2 VM runs an unpatched web server.', svc='Every incident starts with the same question: which layer?'),
      dict(on=['inc', 'lay'], hot='lay', move=(54, 79, 72, 30, 'map'), head='Step 2 · Map it to a layer', text='A = virtualization layer. B = data and access configuration. C = guest operating', text2='system and application.', svc='Use the layer picture above'),
      dict(on=['lay', 'mod'], hot='mod', move=(97, 50, 97, 104, 'model'), head='Step 3 · Check the service model', text='S3 is a managed service; EC2 is IaaS. The same layer can belong to different owners', text2='in different services (OS is yours on EC2, AWS’s on Lambda).', svc='The line is per service, not per company'),
      dict(on=['mod', 'own', 'prov'], hot='prov', move=(202, 66, 226, 30, 'A'), head='Step 4 · Provider’s part', text='Case A: AWS/Azure/Google patch hosts, often live-migrating VMs, and publish', text2='bulletins. The customer’s job: read the bulletin, reboot if asked.', svc='Security bulletins, health dashboards'),
      dict(on=['own', 'cust'], hot='cust', move=(172, 104, 226, 126, 'B, C'), head='Step 5 · Customer’s part', text='Case B: block public access, rotate exposed data, notify if required. Case C: patch', text2='the OS and web server — EC2 does not patch your VM.', svc='Most real breaches land here'),
      dict(on=list(RN), hot='less', move=(278, 127, 298, 90, 'prevent'), head='Step 6 · Turn the lesson into a guard-rail', text='Account-wide public-access block, patch automation, alerts on risky changes —', text2='so the same mistake cannot happen twice.', svc='Practical steps 2–3 build these guard-rails')]
WHO = flow_anim('Three incidents: who fixes what?', 'Map each problem to a layer and a service model to find the owner.', 'Shared responsibility', 'Animation: incident occurs; map to layer; check service model; provider fixes infrastructure issues; customer fixes configuration, data and guest OS; add a guard-rail.', RN, RS, hid='srmflow')

def mapfig():
    o = t(320, 16, 'Six service models, six positions of the line', 11, 'ink', bold=True)
    items = [('1', 'On-premises', 'you secure everything', 'card'), ('2', 'IaaS', 'from the guest OS up', 'amber'), ('3', 'Containers (CaaS)', 'images, pods, cluster config', 'violet'),
             ('4', 'PaaS', 'app code, data, access', 'blue'), ('5', 'Serverless / FaaS', 'function code, permissions', 'green'), ('6', 'SaaS', 'data, users, settings', 'green')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 3) * 208; y = 32 + (i // 3) * 84
        o += box(x, y, 198, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 106, y + 34, a, 8.4, 'ink', bold=True) + t(x + 106, y + 54, b, 7, 'ink2')
    o += t(320, 210, 'From 1 to 6 the provider takes more layers — but never your data or identities.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of six positions: on-premises, IaaS, containers, PaaS, serverless, SaaS with what the customer secures in each.', mapfig(), h=222)

A1 = mk(['Your building', 'Your hardware', 'Your everything'], ['facility|guards, power|cooling', 'hardware|servers, disks|network', 'stack|OS, apps|data, users'], ['card', 'card', 'blue'],
        ['you secure the building and physical access', 'you buy, patch and dispose of hardware', 'and everything running on it'],
        [('Facility', 'You secure the building, power and access.', ''), ('Hardware', 'You buy, firmware-patch and dispose of devices.', ''), ('Stack', 'And every layer above.', '')],
        'On-premises responsibility', 'All layers are yours.', 'On-prem', 'Animation: facility, hardware, full stack — all customer.', 'r1anim')
T1 = vt(1, 'On-premises (the baseline)', 'card',
    'In an <b>on-premises</b> deployment the organisation is responsible for every security layer — physical facility, hardware, network, virtualization, operating systems, applications, identities and data — with no provider sharing the work.',
    'Owning a house: locks, walls, wiring, CCTV and who gets a key are all your job.',
    'TiffinGo’s old billing server in the kitchen: if its disk is stolen or its OS unpatched, no one else is responsible.',
    'Own data centres, colocation (where the colo provider handles only building and power).', '', A1,
    'regulation or latency demands it — and you can staff 24×7 security.',
    'you assume it is automatically safer — small teams rarely match provider physical and hardware security.',
    'When everything is in your own building, you protect everything yourself.',
    [('Physical', 'Access control, CCTV.'), ('Hardware', 'Firmware, disposal.'), ('Network', 'Firewalls, segmentation.'), ('Systems', 'OS and app patching.'), ('Data', 'Backups, encryption, access.')],
    [('colocation', 'renting space and power in someone else’s data centre'), ('firmware', 'low-level software inside hardware'), ('disposal', 'securely destroying old disks')],
    table(['', 'On-premises', 'IaaS'], [['Physical security', 'you', 'provider'], ['Hypervisor', 'you', 'provider'], ['Guest OS', 'you', 'you']], minw=420),
    ['Legacy systems', 'Air-gapped networks', 'Factories'],
    'Provider data centres hold certifications such as ISO 27001 and SOC 2, audited regularly — a level of physical assurance few single companies can afford alone.',
    'Moving to cloud removes the bottom layers from your list — it does not remove the top ones.')

A2 = mk(['Provider: host + hypervisor', 'You: guest OS', 'You: network + data'], ['provider|hardware|hypervisor', 'you|OS patches|agents, hardening', 'you|SGs, IAM|data, encryption'], ['green', 'blue', 'blue'],
        ['the provider secures hosts and virtualization', 'you patch and harden the guest operating system', 'and you control network rules, identities and data'],
        [('Provider', 'Hosts, hypervisor and physical network.', ''), ('Guest OS', 'You patch, harden and monitor the VM’s OS.', ''), ('Above', 'You own network rules, IAM and data.', '')],
        'IaaS responsibility', 'From the OS up is yours.', 'IaaS', 'Animation: provider host and hypervisor; customer guest OS; customer network and data.', 'r2anim')
T2 = vt(2, 'IaaS (VMs)', 'amber',
    'In <b>IaaS</b> the provider secures the physical infrastructure, host operating systems and virtualization layer, while the customer is responsible for the guest operating system (patching, hardening), installed software, network controls such as security groups, identity and access, and data.',
    'Renting an unfurnished flat: the builder handles the structure and lift; your door lock, appliances and valuables are yours.',
    'TiffinGo’s reporting VM on EC2: AWS keeps the host safe; TiffinGo must patch Ubuntu, close port 22 and back up the disk (Lesson 2.1).',
    'Amazon EC2, Azure Virtual Machines, Google Compute Engine.', 'Lesson 2.1 practical patches a VM yourself.', A2,
    'you need OS-level control — and accept OS-level duties.',
    'nobody owns patching — unpatched VMs are the classic IaaS breach.',
    'With rented virtual servers, the provider protects the machines underneath; you protect the system you install.',
    [('Harden image', 'CIS benchmarks.'), ('Patch', 'Systems Manager / Update Manager / VM Manager.'), ('Network', 'Least-open SGs/NSGs/firewalls.'), ('Access', 'No SSH keys sprawl; use session tools.'), ('Data', 'Encrypt disks, back up.')],
    [('guest OS', 'the operating system inside your VM'), ('hardening', 'removing unneeded services and settings'), ('CIS benchmark', 'published secure-configuration guide')],
    table(['', 'IaaS', 'PaaS'], [['OS patching', 'customer', 'provider'], ['Network rules', 'customer', 'mostly customer (app-level)'], ['Runtime updates', 'customer', 'provider']], minw=420),
    ['Lift-and-shift', 'Legacy apps', 'Custom software'],
    'Many cloud ransomware cases began with internet-exposed VMs running unpatched software or open RDP/SSH — customer-side layers.',
    'Use provider patch services and remove direct SSH/RDP (Session Manager, Bastion, IAP) — that shrinks your biggest IaaS duties.')

A3 = mk(['Provider: control plane', 'You: images + config', 'You: workloads'], ['managed K8s|control plane|patched', 'you|images, nodes*|RBAC, policies', 'you|secrets, network|data'], ['green', 'violet', 'blue'],
        ['managed Kubernetes services run and patch the control plane', 'you secure container images, cluster RBAC and (often) node updates', 'and workload secrets, network policies and data'],
        [('Control plane', 'Provider runs and patches it in managed Kubernetes.', ''), ('Images + config', 'You scan images, set RBAC, upgrade node pools.', ''), ('Workloads', 'Secrets, network policies and data are yours.', '')],
        'Container responsibility', 'Split inside the cluster.', 'Containers', 'Animation: provider control plane; customer images and config; customer workloads.', 'r3anim')
T3 = vt(3, 'Containers (managed Kubernetes / CaaS)', 'violet',
    'With <b>managed container services</b>, the provider secures the infrastructure and the Kubernetes control plane; the customer secures container images, cluster configuration (RBAC, network policies, admission rules), workload secrets and data — and, unless using a fully managed or serverless node option, upgrading worker nodes.',
    'A shared commercial kitchen: the owner maintains gas lines and fire systems; each cook keeps their own ingredients fresh and their station clean.',
    'TiffinGo’s order service on EKS: AWS patches the control plane; TiffinGo scans images, upgrades node groups and restricts who can kubectl into production.',
    'Amazon EKS/ECS (and Fargate), Azure AKS/Container Apps, Google GKE (Autopilot)/Cloud Run.', 'Containers are in Lesson 4.5.', A3,
    'you run containers — with node automation (Fargate, Autopilot, auto-upgrade) to shrink your share.',
    'images are pulled from anywhere unscanned, or everyone has cluster-admin.',
    'In managed container platforms, the provider runs the cluster brain; you look after your containers and their settings.',
    [('Images', 'Scan, sign, minimal base.'), ('Nodes', 'Auto-upgrade or serverless nodes.'), ('RBAC', 'Least privilege.'), ('Network', 'Policies between pods.'), ('Secrets', 'External secret stores.')],
    [('control plane', 'the Kubernetes brain (API server, scheduler)'), ('RBAC', 'role-based access control'), ('node', 'a VM that runs your containers')],
    table(['', 'EKS with node groups', 'Fargate / Autopilot'], [['Node OS patching', 'customer (managed groups help)', 'provider'], ['Control plane', 'provider', 'provider'], ['Images', 'customer', 'customer']], minw=460),
    ['Microservices', 'Platform teams', 'Hybrid Kubernetes'],
    'Container-image vulnerabilities and exposed Kubernetes dashboards/APIs have both caused real breaches — customer-side layers in every case.',
    'GKE Autopilot and EKS Auto Mode/Fargate move node patching to the provider — choosing them is a security decision, not only an ops one.')

A4 = mk(['Provider: runtime', 'You: code + config', 'You: data + access'], ['provider|OS, runtime|patching, scaling', 'you|app code|dependencies', 'you|data, users|app settings'], ['green', 'blue', 'blue'],
        ['the provider patches OS and runtime', 'you secure your code and its libraries', 'you control data, access and app configuration'],
        [('Runtime', 'Provider patches the OS and language runtime.', ''), ('Code', 'Your code and its dependencies are yours.', ''), ('Data + access', 'Data, users and configuration are yours.', '')],
        'PaaS responsibility', 'You own the app, not the server.', 'PaaS', 'Animation: provider runtime; customer code; customer data and access.', 'r4anim')
T4 = vt(4, 'PaaS', 'blue',
    'In <b>PaaS</b> the provider additionally secures the operating system, runtime and platform services; the customer remains responsible for application code and dependencies, application configuration, identities and access, network exposure settings and data.',
    'A serviced apartment: housekeeping and maintenance are included, but you still lock your suitcase and decide who you invite in.',
    'TiffinGo’s website on App Service: Microsoft patches the OS; TiffinGo must update Flask when a CVE appears and keep the database password in Key Vault.',
    'Elastic Beanstalk, RDS (managed DB), App Service, Azure SQL, App Engine, Cloud SQL.', 'PaaS types are in Lesson 2.2.', A4,
    'you want the provider to carry OS and runtime duties.',
    'you assume PaaS means “secure by default” — app vulnerabilities and weak access remain yours.',
    'On a ready platform, the provider looks after the servers; you look after your app and its data.',
    [('Dependencies', 'Scan and update libraries.'), ('Secrets', 'Key vaults, not env files in Git.'), ('Access', 'IAM + app auth.'), ('Exposure', 'Private endpoints where possible.'), ('Data', 'Backups and encryption settings.')],
    [('dependency', 'a library your code uses'), ('CVE', 'a published, numbered vulnerability'), ('private endpoint', 'access to a service over a private network address')],
    table(['', 'PaaS', 'Serverless'], [['OS / runtime', 'provider', 'provider'], ['Scaling config', 'shared', 'provider'], ['Code + permissions', 'customer', 'customer']], minw=420),
    ['Web apps', 'Managed databases', 'APIs'],
    'With managed databases, the provider patches the engine — but leaving the database publicly reachable with a weak password is still a common customer-side incident.',
    'For managed databases, the most important customer settings are: no public endpoint, IAM/Entra auth, encryption, automated backups.')

A5 = mk(['Provider: everything below', 'You: function code', 'You: permissions + events'], ['provider|servers, runtime|isolation', 'you|code, libraries|input checks', 'you|role, triggers|data'], ['green', 'blue', 'blue'],
        ['the provider secures infrastructure, runtime and isolation (e.g. Firecracker)', 'you secure function code and libraries', 'and the function’s permissions, triggers and the data it touches'],
        [('Below', 'Provider secures servers, runtime and isolation.', ''), ('Code', 'You secure code, libraries and input validation.', ''), ('Permissions', 'You scope roles, triggers and data access.', '')],
        'Serverless responsibility', 'Small code, big permissions.', 'Serverless', 'Animation: provider below; customer code; customer permissions and events.', 'r5anim')
T5 = vt(5, 'Serverless / FaaS', 'green',
    'In <b>serverless (FaaS)</b> the provider secures all infrastructure, operating systems, runtimes and the isolation between functions; the customer secures function code and dependencies, input validation, the function’s IAM permissions, event-source configuration and data.',
    'A food-delivery kitchen-for-hire: you only bring the recipe, but you decide who may order and what ingredients the cook may take from the store.',
    'TiffinGo’s scheduled Lambda that emails invoices was given “s3:*” on all buckets; a code bug could have deleted every bucket — the fix was a role limited to one prefix.',
    'AWS Lambda, Azure Functions, Cloud Run functions; Firecracker micro-VMs isolate Lambda functions.', 'Lesson 2.4 covers serverless.', A5,
    'you want the smallest operational security surface.',
    'functions get broad roles “to make it work” — permissions become the attack surface.',
    'With serverless, the provider looks after nearly everything; you look after your code and what it is allowed to do.',
    [('Least privilege', 'One role per function.'), ('Inputs', 'Validate event data.'), ('Dependencies', 'Scan packages.'), ('Secrets', 'Secrets manager.'), ('Logging', 'Trace and alert.')],
    [('event source', 'what triggers a function (upload, queue, HTTP)'), ('least privilege', 'only the permissions needed'), ('injection', 'malicious input executed as code')],
    table(['', 'Serverless', 'IaaS'], [['Customer layers', 'code, permissions, data', 'OS, network, code, data'], ['Patching effort', 'libraries only', 'everything above hypervisor'], ['Main risk', 'over-broad permissions', 'unpatched OS, open ports']], minw=440),
    ['Event processing', 'APIs', 'Automation'],
    'OWASP publishes a Serverless Top 10; event injection and over-privileged functions are near the top.',
    'Serverless shifts security from servers to identities — review function roles as carefully as firewall rules.')

A6 = mk(['Provider: whole app', 'You: users + settings', 'You: data'], ['provider|infra, app|patches, uptime', 'you|users, MFA|sharing settings', 'you|what you store|retention, DLP'], ['green', 'amber', 'blue'],
        ['the provider runs and secures the application itself', 'you manage users, MFA, roles and sharing settings', 'and the data you put in, its classification and retention'],
        [('Provider', 'Runs and secures the whole application.', ''), ('Users', 'You manage accounts, MFA, roles and sharing.', ''), ('Data', 'You own what you store, its retention and protection.', '')],
        'SaaS responsibility', 'Even here, users and data are yours.', 'SaaS', 'Animation: provider whole app; customer users and settings; customer data.', 'r6anim')
T6 = vt(6, 'SaaS', 'green',
    'In <b>SaaS</b> the provider secures the entire application and infrastructure; the customer remains responsible for its data, user accounts and authentication (MFA, SSO), access and sharing settings, device security of its users and how the application is configured.',
    'A bank locker room: the bank guards the vault; you decide who gets your key and what you put in the locker.',
    'TiffinGo uses Google Workspace: Google runs Gmail securely; TiffinGo enforces 2-step verification, removes ex-employees the same day and blocks public sharing of order sheets.',
    'Microsoft 365, Google Workspace, Salesforce, Zoho; SaaS security posture tools (SSPM).', 'SaaS types are in Lesson 2.3.', A6,
    'the function is standard — and you still configure identity and sharing carefully.',
    'you assume the vendor handles everything, including leaving accounts of former staff active.',
    'With online software, the company runs the app; you control who uses it and what data goes in.',
    [('Identity', 'SSO + MFA.'), ('Lifecycle', 'Joiners, movers, leavers.'), ('Sharing', 'External sharing policies.'), ('Data', 'Retention, DLP, backups of exports.'), ('Audit', 'Admin and sign-in logs.')],
    [('SSO', 'single sign-on'), ('DLP', 'data loss prevention — rules that stop sensitive data leaving'), ('SSPM', 'SaaS security posture management')],
    table(['', 'SaaS', 'On-premises'], [['App patching', 'provider', 'you'], ['User accounts', 'customer', 'you'], ['Data', 'customer', 'you']], minw=420),
    ['Email and collaboration', 'CRM', 'HR and finance'],
    'Several large SaaS-related breaches involved stolen credentials on accounts without MFA — the customer-side identity layer.',
    'Microsoft states that in every service model, data, endpoints, accounts and access management remain the customer’s responsibility — a line worth quoting in interviews.')

SUMMARY = table(['Layer', 'On-prem', 'IaaS', 'Containers', 'PaaS', 'Serverless', 'SaaS'], [
    ['Data', 'you', 'you', 'you', 'you', 'you', 'you'], ['Identities & access', 'you', 'you', 'you', 'you', 'you', 'you (+ provider auth)'], ['Application code', 'you', 'you', 'you', 'you', 'you', 'provider'],
    ['Runtime / OS', 'you', 'you', 'images: you; nodes: shared', 'provider', 'provider', 'provider'], ['Virtualization, hosts', 'you', 'provider', 'provider', 'provider', 'provider', 'provider'], ['Facility', 'you', 'provider', 'provider', 'provider', 'provider', 'provider']], minw=680)
CHECK = ('  <h3>Check yourself: whose job?</h3>\n' +
    qx('A. Patching the guest OS on an Azure VM.', ['Customer', 'Microsoft', 'Both equally', 'Nobody'], 0, 'IaaS: guest OS is yours.') +
    qx('B. Physical security of an AWS data centre.', ['AWS', 'Customer', 'Both', 'Auditor'], 0, 'Security of the cloud.') +
    qx('C. MFA for Microsoft 365 users.', ['Customer', 'Microsoft only', 'Nobody', 'ISP'], 0, 'Identities are always yours.') +
    qx('D. Patching the database engine on Amazon RDS.', ['AWS', 'Customer', 'Nobody', 'DBA only'], 0, 'Managed service.'))

TYPES = ('  <p>The line in six service models, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['Which two layers are yours in every model?', 'Who patches worker nodes in EKS with node groups vs Fargate?', 'What is the main security risk in serverless?'], 'types 6, 3 and 5') + MAP
         + jump(['On-prem', 'IaaS', 'Containers', 'PaaS', 'Serverless', 'SaaS']) + T1 + T2 + T3 + T4 + T5 + T6
         + '\n  <h3 style="margin-top:34px">All six side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('Inherited controls', 'Controls fully handled by the provider.', 'You can rely on their audit reports.', 'Physical, environmental.'),
    ('Shared controls', 'Both sides do their own part.', 'Patching, config, training split by layer.', 'Provider patches hosts; you patch guests.'),
    ('Customer-specific controls', 'Only you can do them.', 'Data classification, user access.', 'Zone/Region choice, MFA.'),
    ('Compliance reports', 'Third-party audits of the provider.', 'Evidence for your auditors.', 'AWS Artifact, Service Trust Portal, Compliance Reports Manager.'),
    ('Secure defaults', 'Settings the provider turns on for you.', 'Reduce customer mistakes.', 'S3 Block Public Access on by default for new buckets.'),
    ('Shared fate', 'Provider actively helps you configure securely.', 'Blueprints, guardrails, guidance.', 'Google’s term; landing zones.')])

DEEP = ('  <h3>Why most breaches land on the customer side</h3>\n  <p>Provider infrastructure is engineered, audited and attacked constantly, so failures there are rare. Customer-side layers change daily — new buckets, new users, new rules — made by many people. Industry analyses repeatedly find that the large majority of cloud security incidents involve customer misconfiguration or stolen credentials.</p>\n'
    '  <h3>Guard-rails that turn duties into defaults</h3>\n' + table(['Duty', 'AWS', 'Azure', 'Google Cloud'], [['No public storage', 'S3 Block Public Access (account level)', 'disallow blob public access (default for new accounts)', 'public access prevention (enforced)'], ['Find external exposure', 'IAM Access Analyzer', 'Defender for Cloud recommendations', 'Security Command Center, Policy Analyzer'], ['Org-wide rules', 'SCPs, resource control policies', 'Azure Policy', 'Organization policies'], ['Patching', 'Systems Manager Patch Manager', 'Update Manager', 'VM Manager OS patch management']], minw=620) +
    '\n  <h3>Using the provider’s audit reports</h3>\n  <p>Your auditors will ask how you know the provider’s half is done. The answer: download its SOC 2 / ISO 27001 reports and certificates (practical step 1), check the services you use are in scope, and map their controls to yours. You do not audit the provider’s data centre yourself.</p>')

clouds = vendor_tabs('<p><b>AWS:</b> Shared Responsibility Model (“of” vs “in”), AWS Artifact for reports, S3 Block Public Access, IAM Access Analyzer, Security Hub CSPM, Systems Manager Patch Manager, SCPs.</p>',
    '<p><b>Azure:</b> shared responsibility by service type, Service Trust Portal for reports, Microsoft Defender for Cloud (free foundational CSPM with secure score), Azure Policy, Update Manager.</p>',
    '<p><b>Google Cloud:</b> shared responsibility and shared fate, Compliance Reports Manager, Security Command Center, organization policies, public access prevention, Assured Workloads, security blueprints.</p>') + \
    cloud3([['Audit reports', 'AWS Artifact', 'Service Trust Portal', 'Compliance Reports Manager'], ['Posture management', 'Security Hub CSPM', 'Defender for Cloud', 'Security Command Center'], ['Exposure finder', 'IAM Access Analyzer', 'Defender recommendations', 'Policy Analyzer / SCC'], ['Org guard-rails', 'SCPs', 'Azure Policy', 'Organization policies']])

MOCKQ.extend([
 (mock('aws', ['AWS Artifact', 'Reports'], ['Reports', 'Agreements'], 'Reports', [('Search', 'SOC 2'), ('AWS SOC 2 Type 2 Report', 'View terms and download')], 'Download report'),
  mock('az', ['Service Trust Portal', 'Certifications, reports and white papers'], ['Home', 'Library', 'My library'], 'Library', [('Filter', 'Audit reports · SOC'), ('Azure SOC 2 Type 2', 'Download')], 'Download'),
  mock('gcp', ['Compliance Reports Manager'], ['Reports', 'Certifications'], 'Reports', [('Industry', '▾ All'), ('Report', 'Google Cloud SOC 2')], 'Download')),
 (mock('aws', ['S3', 'Block Public Access settings for this account'], ['Buckets', 'Access Points', 'Block Public Access settings'], 'Block Public Access settings', [('Block all public access', '[x] On'), ('4 settings', '[x] ACLs · [x] policies (new + existing)')], 'Save changes'),
  mock('az', ['Home', 'Storage accounts', 'Configuration'], ['Overview', 'Configuration', 'Networking'], 'Configuration', [('Allow Blob anonymous access', '[x] Disabled'), ('Minimum TLS version', '▾ Version 1.2')], 'Save'),
  mock('gcp', ['Cloud Storage', 'Buckets', 'Permissions'], ['Objects', 'Configuration', 'Permissions'], 'Permissions', [('Public access', 'Not public'), ('Prevent public access', '[x] Enforced')], 'Save')),
 (mock('aws', ['IAM', 'Access Analyzer', 'Analyzers'], ['Findings', 'Analyzers', 'Archive rules'], 'Analyzers', [('Type', '[x] External access'), ('Zone of trust', 'Current account')], 'Create analyzer'),
  mock('az', ['Microsoft Defender for Cloud', 'Recommendations'], ['Overview', 'Recommendations', 'Security posture', 'Inventory'], 'Recommendations', [('Secure score', 'e.g. 52%'), ('Top', 'MFA should be enabled for accounts with owner permissions')], 'Fix'),
  mock('gcp', ['IAM & Admin', 'Recommendations'], ['IAM', 'Policy Analyzer', 'Recommendations'], 'IAM', [('Insight', 'Unused permissions for a principal'), ('Recommendation', 'Replace Editor with a smaller role')], 'Apply')),
])

STEP1 = ('1 · Download the provider’s audit report (their half)', tri(
    (['Search [[AWS Artifact]] → [[Reports]] → search “SOC 2” → open the report → accept the terms → [[Download report]].', 'Check that the services you use (EC2, S3, Lambda…) are listed in scope.'],
     "aws artifact list-reports --query 'reports[?contains(name, `SOC`)].[name,id]' --output table --region us-east-1 | head -20",
     'a list of AWS SOC reports with IDs (AWS Artifact API; the console is the easiest way to download and accept the terms).'),
    (['Open <b>servicetrust.microsoft.com</b> → sign in with your Azure account → [[Library]] / Certifications, reports → filter SOC → [[Download]] the Azure SOC 2 report.'],
     'az account show --query "{tenant:tenantId,user:user.name}" -o table\n# Service Trust Portal is web-only: open https://servicetrust.microsoft.com and sign in with this account.',
     'your tenant and user; the portal lists SOC, ISO 27001 and other reports to download.'),
    (['Open <b>cloud.google.com/security/compliance/compliance-reports-manager</b> → choose a report (SOC 2, ISO 27001) → [[Download]] (some reports ask you to sign in and accept terms).'],
     'gcloud config list account --format="value(core.account)"\n# Compliance Reports Manager is web-based: sign in with this account to download reports.',
     'your account; the page lists Google Cloud audit reports and certificates.')),
    'These reports are the evidence for the provider’s half. You never audit their data centre — you read their auditor’s report.')

STEP2 = ('2 · Lock public access for the whole account (your half)', tri(
    (['[[S3]] → [[Block Public Access settings for this account]] → [[Edit]] → tick [[Block all public access]] → [[Save changes]] → type <code>confirm</code>.'],
     'ACC=$(aws sts get-caller-identity --query Account --output text)\naws s3control put-public-access-block --account-id $ACC --public-access-block-configuration \\\n  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true\naws s3control get-public-access-block --account-id $ACC',
     'all four settings <code>true</code>. Now nobody in this account can make a bucket public by mistake — the intern’s incident cannot repeat.'),
    (['[[Storage accounts]] → each account → [[Configuration]] → [[Allow Blob anonymous access]] = [[Disabled]] → [[Save]]. (New accounts already default to disabled.)', 'For the whole subscription, assign the built-in policy “Storage account public access should be disallowed”.'],
     'az storage account list --query "[].{name:name,anonymous:allowBlobPublicAccess,tls:minimumTlsVersion}" -o table\n# fix any account showing True:\n# az storage account update -n NAME -g RG --allow-blob-public-access false --min-tls-version TLS1_2',
     'each storage account with <code>False</code> (or empty, which means disabled on new accounts) for anonymous access.'),
    (['[[Cloud Storage]] → bucket → [[Permissions]] → [[Prevent public access]] → [[Enforce]].', 'With an organisation, set the org policy <code>storage.publicAccessPrevention</code> for all projects.'],
     'B=tiffingo-srm-$RANDOM; gcloud storage buckets create gs://$B --location=asia-south1 --public-access-prevention\ngcloud storage buckets describe gs://$B --format="value(public_access_prevention)"\ngcloud storage buckets add-iam-policy-binding gs://$B --member=allUsers --role=roles/storage.objectViewer 2>&1 | tail -1',
     '<code>enforced</code>, and the attempt to grant <code>allUsers</code> fails with a precondition error — public access is impossible on this bucket.')),
    'A guard-rail turns a duty (“remember not to make buckets public”) into a default nobody can forget.')

STEP3 = ('3 · Find what is exposed or over-permitted', tri(
    (['[[IAM]] → [[Access Analyzer]] → [[Create analyzer]] → type [[External access]], zone of trust = current account → [[Create]].', '[[Findings]] lists resources (buckets, roles, keys, queues) shared outside your account.'],
     'aws accessanalyzer create-analyzer --analyzer-name account-external --type ACCOUNT\nsleep 60; ARN=$(aws accessanalyzer list-analyzers --query "analyzers[0].arn" --output text)\naws accessanalyzer list-findings-v2 --analyzer-arn $ARN --query "findings[].[resourceType,resource,status]" --output table',
     'an empty table (nothing shared externally) or findings to review. External-access analysis is free.'),
    (['Search [[Microsoft Defender for Cloud]] → [[Recommendations]] — the free foundational CSPM gives a secure score and fixes (e.g. “MFA should be enabled for accounts with owner permissions”).'],
     'az security secure-scores list --query "[].{name:displayName,current:score.current,max:score.max}" -o table\naz security assessment list --query "[?status.code==\'Unhealthy\'].displayName" -o tsv | head -10',
     'your secure score and up to 10 unhealthy recommendations (new subscriptions may take a few hours to be assessed).'),
    (['[[IAM &amp; Admin]] → [[IAM]] — the shield icon next to principals shows unused permissions; [[Recommendations]] suggests smaller roles.'],
     'P=$(gcloud config get-value project)\ngcloud recommender insights list --project=$P --location=global --insight-type=google.iam.policy.Insight --format="table(description)" | head\ngcloud recommender recommendations list --project=$P --location=global --recommender=google.iam.policy.Recommender --format="table(description)" | head',
     'insights such as “principal has not used N permissions in 90 days” and role-reduction recommendations (projects need some history before these appear).')),
    'Posture tools check your half continuously — run them weekly, fix the top items.')

prac = practical(OWN_INTRO + ' You check the provider’s half (audit reports) and secure your half (block public access, find exposure and excess permissions). Everything here is free.', [SETUP_STEP, STEP1, STEP2, STEP3],
    cleanup='<b>AWS:</b> keep the account-level public-access block on (recommended); delete the analyzer if you want: <code>aws accessanalyzer delete-analyzer --analyzer-name account-external</code>. '
            '<b>Azure:</b> nothing created. <b>Google Cloud:</b> <code>gcloud storage buckets delete gs://$B</code>.')

mist = mistakes([
    ['“The provider secures my data.”', 'Misreading the model.', 'Data, identities and access are always the customer’s.'],
    ['Same duties assumed for every service.', 'One model for all.', 'Check the line per service (EC2 vs RDS vs Lambda).'],
    ['No one owns VM patching.', 'Gap between dev and ops.', 'Assign owners; automate with patch services.'],
    ['Public storage for “quick sharing”.', 'Convenience.', 'Account-level block + pre-signed/signed URLs.'],
    ['Ignoring provider bulletins.', 'Assuming nothing to do.', 'Subscribe to security bulletins and health events.'],
    ['Auditors asked to “check the cloud”.', 'No evidence collected.', 'Provide provider audit reports + your own controls.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Shared responsibility model in cloud security.'], ['AWS CLF-C02', 'Domain 2: shared responsibility (of vs in), how it changes for EC2, RDS, Lambda; AWS Artifact.'], ['AZ-900', 'Describe the shared responsibility model; responsibilities always retained by the customer.'], ['Google Cloud Digital Leader', 'Shared responsibility and shared fate; compliance reports.']], minw=560) + \
    qx('1. Under the AWS model, who patches the guest OS on EC2?', ['AWS', 'The customer', 'Both', 'Nobody'], 1, 'Customer.') + \
    qx('2. Which is always the customer’s responsibility in every model?', ['physical security', 'hypervisor', 'data and identities', 'host OS'], 2, 'Data + identities.') + \
    qx('3. Where do you download AWS SOC reports?', ['AWS Artifact', 'AWS Config', 'Amazon Macie', 'AWS Shield'], 0, 'Artifact.') + \
    qx('4. For Amazon RDS, who patches the database engine?', ['AWS', 'Customer', 'Both', 'Oracle'], 0, 'Managed service.') + \
    qx('5. Patch management is an example of a…', ['shared control', 'inherited control', 'customer-only control', 'provider-only control'], 0, 'Shared.') + \
    qx('6. In SaaS, who manages user accounts and MFA?', ['customer', 'provider', 'ISP', 'auditor'], 0, 'Customer.')

proj = miniproject('Mini project: TiffinGo’s responsibility matrix',
    'Build a RACI-style matrix for every system TiffinGo runs.',
    ['<b>List</b> systems: website (App Service), order API (EKS), invoices (Lambda), reports (EC2), DB (RDS), email (Workspace).',
     '<b>For each</b>, mark provider vs customer for data, identity, app, OS, network, hosts.',
     '<b>Owners:</b> name the TiffinGo team responsible for each customer row.',
     '<b>Guard-rails:</b> one automated control per row (practical steps 2–3 or the deep-dive table).',
     '<b>Evidence:</b> which provider report covers the provider rows.',
     '<b>Incident drill:</b> replay the public-bucket story with your matrix.'],
    'A one-page matrix with owners, guard-rails and evidence.', 'Module 2 (service models) + 9.1.')

assemble_v2(HERE, story_h2='The bucket that was public “for one day”', hook_html=hk,
    narration='A TiffinGo intern made a storage bucket public to share menu photos quickly. It also held customer addresses. When a researcher reported it, the team’s first question was: “Isn’t AWS supposed to stop this?”',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Shared responsibility model',
    formal='The <b>shared responsibility model</b> defines how security and compliance duties are divided between a cloud provider and its customer: the provider is responsible for security <b>of</b> the cloud (physical facilities, hardware, networking and the virtualization and managed-service layers it operates), and the customer is responsible for security <b>in</b> the cloud (data, identities and access, configuration, and — depending on the service model — operating systems, applications and network controls).',
    simple='The provider protects the cloud itself; you protect what you put in it and how you set it up. The more the provider manages, the less you do — but your data and users are always yours.',
    interview=['“AWS secures the cloud — facilities, hardware, hypervisor, managed services — and the customer secures what’s in it: data, IAM, network rules and, for IaaS, the guest OS. The line moves up with PaaS and SaaS, but data and identities stay with the customer.”', '“Patch management is a shared control: AWS patches hosts, we patch EC2 guests. RDS engine patching is AWS’s; Lambda runtime too.”'],
    terms_rows=[('Security of the cloud', 'Provider’s part.'), ('Security in the cloud', 'Customer’s part.'), ('Inherited control', 'Fully provider.'), ('Shared control', 'Split by layer.'), ('Customer-specific control', 'Only customer.'), ('Shared fate', 'Provider helps you succeed.'), ('AWS Artifact', 'Download audit reports.'), ('Guard-rail', 'Preventive default.')],
    exam='CLF-C02 Domain 2 asks who does what for EC2 vs RDS vs Lambda vs S3, shared controls (patching, configuration, training), and where to get compliance reports (Artifact). AZ-900: what the customer always retains.',
    picture_h2='Where the line sits', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'The line in six service models, one by one', TYPES)],
    how_h2='Three incidents: who fixes what?', how_intro='Apply the model to real problems, step by step.', how_anim=WHO,
    parts_h2='Six ideas inside the model', parts_html=parts, lv='',
    myth_rows=[('The cloud provider secures my data.', 'You choose who can access it.', 'Story.'), ('SaaS means no security work.', 'Users, MFA, sharing and data are yours.', 'Type 6.'), ('Private cloud avoids shared responsibility.', 'You simply take every layer.', 'Type 1.')],
    extra_secs=[('deep', 'Deep dive', 'Why breaches land on the customer side, guard-rails, audit reports', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Explain security of vs in the cloud.', 'Place the line for on-prem, IaaS, containers, PaaS, serverless and SaaS.', 'Classify inherited, shared and customer-specific controls.', 'Download provider audit reports and add public-access and exposure guard-rails on your own account.', 'Answer shared-responsibility exam scenarios.'],
    next_html='<a href="../02-cloud-security-issues-and-threats/">9.2 Cloud security issues and threats</a>.',
    pre='<b>Before you start:</b> Module 2 (service models).')
