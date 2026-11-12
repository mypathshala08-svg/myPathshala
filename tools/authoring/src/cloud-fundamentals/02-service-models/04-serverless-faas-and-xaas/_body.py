import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)


hk = hook('TiffinGo’s “send the daily menu at 7 a.m.” job runs for 4 seconds a day on a server that costs money 24 hours a day. Its laptops need Windows for 6 interns for 3 months. Its office files need disaster recovery. Is there an “as a service” for all of these?',
    'Yes — and that is what <b>XaaS</b> (“anything as a service”) means. <b>Serverless</b> computing runs your code only when an event happens (<b>FaaS</b>) on top of fully managed back-end services (<b>BaaS</b>), billed per use and scaling to zero. Around it a whole family of services grew: <b>CaaS</b> (containers), <b>DaaS</b> (desktops), <b>DRaaS</b> (disaster recovery), <b>SECaaS</b> (security), <b>AIaaS</b> (AI models). This lesson explains each, shows what happens inside a function invocation including cold starts, and on <b>your own</b> account you deploy a function, run it on a schedule and read its cold-start time.',
    ['Serverless = FaaS + BaaS: the classic definition interviewers expect.', 'What a “cold start” really is, millisecond by millisecond.', 'Seven XaaS models beyond IaaS, PaaS and SaaS.'])

def story_scene():
    o = t(180, 12, '4 seconds of work, 24 hours of server', 9, 'ink', bold=True)
    o += box(14, 28, 330, 30, 'card', rx=6)
    o += box(14, 28, 330, 30, 'red', rx=6) + t(179, 47, 'VM billed all day', 7.6, 'ink', bold=True)
    o += box(14, 68, 330, 30, 'card', rx=6) + box(96, 68, 4, 30, 'green', rx=1) + t(180, 87, 'function billed for 4 seconds at 7:00 a.m.', 7.6, 'ink', bold=True)
    o += t(180, 120, 'Serverless: pay only while the code runs.', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Two bars: a VM billed all day versus a function billed for four seconds at 7 a.m.', story_scene(), 'Pay for <tspan font-weight="700" class="s-acc">work</tspan>, not for waiting.', h=134)
dialogue = '''R> Sir, our menu-mailer server costs ₹700 a month to run a 4-second job once a day.
A> Make it a function. It wakes at 7 a.m., runs 4 seconds, and the monthly bill rounds to zero — Lambda’s free tier alone covers a million requests a month.
K> And the interns’ Windows laptops?
A> Desktop as a service: Windows desktops streamed from the cloud, paid per month, deleted when the internship ends.
R> So everything can be “as a service”?
A> Almost — that is XaaS. But the core idea is serverless: no servers to manage, pay per use. Let’s see how it works inside.'''

# ------------------------------------------------------------------ picture
def defsfig():
    o = t(320, 16, 'Serverless = FaaS + BaaS', 11, 'ink', bold=True)
    o += box(30, 40, 240, 170, 'blue', rx=10) + t(150, 60, 'FaaS — your code', 9, 'ink', bold=True)
    for i, n in enumerate(['small functions', 'run on events', 'billed per request + ms', 'scale 0 → 1,000s']): o += t(150, 86 + i * 22, n, 8, 'ink')
    o += t(320, 130, '+', 22, 'ink', bold=True)
    o += box(370, 40, 240, 170, 'green', rx=10) + t(490, 60, 'BaaS — managed services', 9, 'ink', bold=True)
    for i, n in enumerate(['auth (Cognito, Firebase Auth)', 'database (DynamoDB, Firestore)', 'storage, queues, APIs', 'no servers, per-use pricing']): o += t(490, 86 + i * 22, n, 8, 'ink')
    o += t(320, 234, 'Four signs of “serverless”: no servers to manage · auto-scaling (to zero) · pay per use · built-in availability.', 7.6, 'ink2')
    return o
DEFS = bigfig('Serverless shown as FaaS (small functions run on events, billed per request and millisecond, scaling from zero) plus BaaS (managed auth, databases, storage, queues with per-use pricing).', defsfig(), h=246)

def xaasfig():
    o = t(320, 16, 'The XaaS family beyond IaaS / PaaS / SaaS', 11, 'ink', bold=True)
    o += box(250, 104, 140, 48, 'amber', rx=24) + t(320, 126, 'XaaS', 11, 'ink', bold=True) + t(320, 142, 'anything as a service', 7, 'ink2')
    items = [('FaaS', 'functions', 30, 30), ('BaaS', 'serverless back ends', 250, 26), ('CaaS', 'containers', 470, 30), ('DaaS', 'virtual desktops', 470, 110), ('DRaaS', 'disaster recovery', 470, 190), ('SECaaS', 'security services', 250, 196), ('AIaaS', 'AI models via API', 30, 190), ('IaaS · PaaS · SaaS', 'the classic three', 30, 110)]
    for n, d, x, y in items:
        o += box(x, y, 140, 46, 'card' if n.startswith('IaaS') else 'blue', rx=8) + t(x + 70, y + 20, n, 8.2, 'ink', bold=True) + t(x + 70, y + 36, d, 6.8, 'ink2')
    return o
XAAS = bigfig('XaaS hub surrounded by FaaS, BaaS, CaaS, DaaS, DRaaS, SECaaS, AIaaS and the classic IaaS, PaaS and SaaS.', xaasfig(), h=252)

picture = ('  <p>The classic definition of serverless — and the one interviewers expect:</p>\n' + DEFS + '\n  <p>And the wider “anything as a service” family:</p>\n' + XAAS)

# ------------------------------------------------------------------ how: invocation + cold start
RN = {'ev': (4, 54, 54, 50, 'meter', 'Event', '7:00 cron'), 'svc': (66, 4, 60, 46, 'cloud', 'Lambda service', 'invoke API'), 'warm': (66, 104, 60, 46, 'chip', 'Warm env?', 'none'),
      'vm': (138, 54, 62, 50, 'server', 'Micro-VM', 'Firecracker'), 'init': (212, 4, 64, 46, 'gear', 'Init', 'runtime + code'), 'run': (212, 104, 64, 46, 'app', 'Handler', 'your function'), 'keep': (290, 54, 66, 50, 'disk', 'Frozen', 'reused next')}
RS = [dict(on=['ev', 'svc'], hot='svc', move=(58, 70, 70, 40, 'invoke'), head='Step 1 · An event invokes the function', text='The scheduler (or an upload, HTTP call, queue message) calls the function service', text2='with an event JSON.', svc='EventBridge Scheduler · Timer trigger · Cloud Scheduler'),
      dict(on=['ev', 'svc', 'warm'], hot='warm', move=(96, 50, 96, 104, 'look'), head='Step 2 · Is a warm environment free?', text='If an execution environment from a recent call is idle, it is reused — a warm start', text2='in a few milliseconds. At 7 a.m. there is none.', svc='Warm start: skip steps 3–4'),
      dict(on=['ev', 'svc', 'warm', 'vm'], hot='vm', move=(126, 127, 150, 90, 'create'), head='Step 3 · Cold start: create an isolated environment', text='A new Firecracker micro-VM starts on a worker host (~125 ms boot), isolated from other', text2='customers’ functions.', svc='Lesson 4.5 explains micro-VMs'),
      dict(on=['ev', 'svc', 'warm', 'vm', 'init'], hot='init', move=(200, 70, 222, 40, 'load'), head='Step 4 · Init: runtime, your code, globals', text='Download the code package, start Python/Node/Java, run code outside the handler', text2='(imports, DB clients). Logged as “Init Duration”.', svc='Keep init small; SnapStart / provisioned concurrency remove it'),
      dict(on=['ev', 'svc', 'warm', 'vm', 'init', 'run'], hot='run', move=(244, 50, 244, 104, 'call'), head='Step 5 · Run the handler', text='Your function runs (4 s to send the menu) and returns. Billing = requests +', text2='memory × duration, in 1 ms steps.', svc='Max 15 minutes per invocation on Lambda'),
      dict(on=list(RN), hot='keep', move=(276, 127, 298, 90, 'freeze'), head='Step 6 · Freeze and reuse — or scale to zero', text='The environment is frozen and reused for the next event; many events at once', text2='create many environments; idle ones are removed later.', svc='Concurrency = environments running in parallel')]
INV = flow_anim('Inside one function invocation (and a cold start)', 'What happens between an event and your code running.', 'Function invocation', 'Animation: an event invokes the function service; no warm environment; a micro-VM is created; runtime and code are initialised; the handler runs; the environment is frozen for reuse.', RN, RS, hid='faasflow')

# ------------------------------------------------------------------ types
def mapfig():
    o = t(320, 16, 'Seven “as a service” models', 11, 'ink', bold=True)
    items = [('1', 'FaaS', 'functions on events', 'blue'), ('2', 'BaaS', 'serverless back-end services', 'green'), ('3', 'CaaS', 'containers as a service', 'violet'),
             ('4', 'DaaS', 'desktops as a service', 'amber'), ('5', 'DRaaS', 'disaster recovery', 'red'), ('6', 'SECaaS', 'security as a service', 'red'), ('7', 'AIaaS', 'AI models via API', 'violet')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 8.4, 'ink', bold=True) + t(x + 78, y + 54, b, 6.8, 'ink2')
    o += t(320, 210, '1–2 together are “serverless” · 3 runs containers · 4–7 deliver desktops, resilience, security and AI as services.', 7.6, 'ink2')
    return o
MAP = bigfig('Map of seven XaaS models: FaaS, BaaS, CaaS, DaaS, DRaaS, SECaaS, AIaaS.', mapfig(), h=222)

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

A1 = mk(['Event', 'Function runs', 'Scale / zero'], ['event|HTTP, upload,|schedule, queue', 'function|your code|ms billing', 'scale|parallel copies|then zero'], ['amber', 'blue', 'green'],
        ['something happens', 'a short-lived function handles it', 'many at once, none when idle'],
        [('Event', 'An HTTP request, file upload, schedule or message arrives.', ''), ('Run', 'The function runs in a managed environment; billed per ms.', ''), ('Scale', 'Parallel copies for many events; zero when idle.', '')],
        'FaaS in action', 'Code that runs on events.', 'FaaS', 'Animation: an event; a function runs; it scales out and back to zero.', 'x1anim')
T1 = vtype(1, 'FaaS (Function as a Service)', 'blue',
    '<b>Function as a Service (FaaS)</b> executes small, stateless pieces of code in response to events on fully managed infrastructure, creating execution environments on demand, scaling automatically from zero to many parallel instances, and billing per invocation and execution time.',
    'A pressure cooker’s whistle: it acts only when the steam builds up, then goes quiet — no one stands by it all day.',
    'TiffinGo’s 7 a.m. menu mailer is a Lambda function triggered by EventBridge Scheduler: 30 runs a month × 4 s — well inside the always-free tier.',
    'AWS Lambda, Azure Functions, Google Cloud Run functions; open-source: Knative, OpenFaaS.',
    'Compute options are compared in Lesson 6.1.', A1,
    'short, event-driven, bursty work: webhooks, file processing, schedules, glue between services.',
    'long-running jobs (Lambda max 15 min), steady high traffic, or latency-critical paths sensitive to cold starts.',
    plain='You write one small piece of code; the cloud runs it only when something happens, and you pay only for those seconds.',
    how=[('Package', 'Code + dependencies (zip or container image).'), ('Configure', 'Runtime, memory, timeout, permissions role.'), ('Trigger', 'Connect an event source.'), ('Invoke', 'Cold or warm start; handler runs (see “How it works”).'), ('Observe', 'Logs, metrics, traces per invocation.')],
    words=[('handler', 'the function the platform calls'), ('invocation', 'one run of a function'), ('cold start', 'first-call delay to create an environment'), ('concurrency', 'how many copies run at the same time')],
    diff=table(['', 'FaaS', 'Container PaaS (CaaS-like)', 'VM'], [['Unit', 'function', 'container', 'server'], ['Max run time', 'minutes (Lambda 15)', 'long', 'unlimited'], ['Idle cost', '0', '0 (Cloud Run) / >0', 'full']], minw=520),
    where=['Webhooks and APIs with spiky traffic', 'File and image processing', 'Scheduled jobs and automation'],
    realworld='Lambda bills in 1 ms increments, and its always-free tier includes 1 million requests and 400,000 GB-seconds per month — why small scheduled jobs often cost nothing.',
    pro='Memory is also the CPU knob: Lambda allocates CPU in proportion to memory (a full vCPU at about 1,769 MB). Raising memory can make a CPU-bound function so much faster that it becomes <i>cheaper</i>.')

A2 = mk(['Need a back-end feature', 'Use a managed service', 'Pay per use'], ['need|login, data,|files, queues', 'service|Cognito, DynamoDB|S3, SQS', 'billing|per request|per GB'], ['amber', 'green', 'blue'],
        ['typical back-end needs of every app', 'consume them as services — no servers', 'no capacity planning, scales automatically'],
        [('Need', 'Every app needs authentication, data, files, messaging.', ''), ('Service', 'Use fully managed services for them — no servers to run.', ''), ('Per use', 'Billing per request, GB or message.', '')],
        'BaaS in action', 'Back ends you consume, not build.', 'BaaS', 'Animation: back-end needs; managed services; per-use billing.', 'x2anim')
T2 = vtype(2, 'BaaS (serverless Backend as a Service)', 'green',
    '<b>Backend as a Service (BaaS)</b> in the serverless sense means building application back ends from fully managed, per-use services — authentication, databases, storage, messaging, APIs, search — that scale automatically and require no server management, typically combined with FaaS for custom logic.',
    'Ordering a ready-made wedding package — tent, lights, sound — instead of buying the equipment: you configure it; the vendor runs it.',
    'TiffinGo’s corporate portal uses Cognito for login, DynamoDB for orders, S3 for invoices and SQS for notifications — all serverless back-end services; Lambda only adds the business rules.',
    'AWS Cognito, DynamoDB, S3, SQS/SNS, AppSync, API Gateway; Azure Entra External ID, Cosmos DB (serverless), Blob Storage, Service Bus; Google Firebase (Auth, Firestore, Storage), Pub/Sub.',
    'Mobile back ends (MBaaS) were covered in Lesson 2.2.', A2,
    'building new apps quickly with small teams; most of the back end is standard capability.',
    'you need features or performance a service cannot provide, or strict portability across clouds.',
    plain='Instead of building your own login system, database server and file server, you use ready-made cloud services for each and pay per use.',
    how=[('Choose services', 'Auth, data, storage, messaging, API.'), ('Configure', 'Tables, buckets, user pools, permissions.'), ('Connect', 'Clients or functions call them via SDK/API.'), ('Secure', 'IAM roles, tokens, fine-grained rules.'), ('Scale', 'Automatic; watch limits and costs.')],
    words=[('back end', 'the server side of an app'), ('user pool', 'a managed directory of app users'), ('per-use pricing', 'pay per request/GB, not per server')],
    diff=table(['', 'BaaS', 'Self-run back end'], [['Servers to patch', 'none', 'yes'], ['Scaling', 'automatic', 'you design it'], ['Lock-in', 'higher', 'lower']], minw=420),
    where=['Mobile and web apps', 'MVPs and hackathons', 'Event-driven systems'],
    realworld='Mike Roberts’ widely cited article “Serverless Architectures” (2016/2018, martinfowler.com) defines serverless as BaaS + FaaS — the definition most textbooks and interviews still use.',
    pro='Serverless is a spectrum, not a label: DynamoDB on-demand and S3 are fully serverless; a provisioned RDS instance is “managed” but not serverless — you still choose and pay for capacity when idle.')

A3 = mk(['Container image', 'Platform schedules it', 'Managed fleet'], ['image|your app|any language', 'orchestrator|ECS/AKS/GKE|or serverless', 'fleet|scaling, healing|load balancing'], ['violet', 'blue', 'green'],
        ['package once, run anywhere', 'the service decides where containers run', 'health, scaling and networking provided'],
        [('Image', 'Applications are packaged as container images.', ''), ('Schedule', 'A managed orchestrator places containers on capacity.', ''), ('Fleet', 'It heals, scales and load-balances them.', '')],
        'CaaS in action', 'Containers, managed.', 'CaaS', 'Animation: container image; orchestrator schedules it; managed fleet with scaling and healing.', 'x3anim')
T3 = vtype(3, 'CaaS (Containers as a Service)', 'violet',
    '<b>Containers as a Service (CaaS)</b> provides managed container orchestration and runtime — clusters, scheduling, networking, scaling and health management — so customers deploy and operate containerised applications without building orchestration infrastructure themselves; it sits between IaaS and PaaS.',
    'A shipping port with cranes and berths ready: you bring standard containers; the port moves, stacks and tracks them.',
    'TiffinGo’s 12 microservices run on Amazon EKS with Fargate profiles; the team manages Kubernetes manifests, AWS manages the control plane and capacity.',
    'Amazon ECS, EKS, Fargate; Azure Kubernetes Service, Azure Container Instances, Container Apps; Google Kubernetes Engine (incl. Autopilot), Cloud Run.',
    'Lessons 4.5, 6.1 and 7.4 cover containers in depth.', A3,
    'many containerised services need consistent deployment, scaling and networking.',
    'one simple app — serverless containers or PaaS are simpler.',
    plain='A cloud service that runs and manages lots of packed apps (containers) for you.',
    how=[('Build images', 'Push to a registry.'), ('Define', 'Task definitions / Kubernetes manifests.'), ('Run', 'Managed control plane schedules containers.'), ('Connect', 'Service discovery, load balancers.'), ('Operate', 'Autoscaling, rolling updates, logs.')],
    words=[('orchestrator', 'software that decides where containers run and keeps them healthy'), ('registry', 'storage for container images'), ('manifest', 'a file describing what to run')],
    diff=table(['', 'IaaS', 'CaaS', 'PaaS'], [['You deploy', 'VMs', 'containers', 'code'], ['You manage', 'OS and up', 'containers, manifests', 'code'], ['Flexibility', 'highest', 'high', 'medium']], minw=480),
    where=['Microservices', 'Hybrid/multi-cloud portability', 'Batch and ML on containers'],
    realworld='Kubernetes, created by Google from its Borg experience and donated to the CNCF in 2015, became the common CaaS interface — EKS, AKS and GKE all run upstream-conformant Kubernetes.',
    pro='CaaS is not automatically cheaper: an EKS cluster costs a control-plane fee per hour plus nodes. Bin-packing (fitting pods tightly onto nodes) and autoscaling with tools like Karpenter decide the real bill.')

A4 = mk(['Pick a desktop bundle', 'Stream to any device', 'Pay per user'], ['bundle|Windows/Linux|apps, size', 'stream|laptop, tablet,|thin client', 'billing|per user|monthly/hourly'], ['amber', 'blue', 'green'],
        ['a full desktop runs in the cloud', 'only pixels travel; data stays in the cloud', 'add or remove desktops in minutes'],
        [('Bundle', 'Choose an OS image, apps and size.', ''), ('Stream', 'Users connect from any device; only the screen is streamed.', ''), ('Pay', 'Per user per month or per hour; delete when done.', '')],
        'DaaS in action', 'Desktops from the cloud.', 'DaaS', 'Animation: choose a desktop bundle; stream it to any device; pay per user.', 'x4anim')
T4 = vtype(4, 'DaaS (Desktop as a Service)', 'amber',
    '<b>Desktop as a Service (DaaS)</b> delivers complete virtual desktops (Windows or Linux) hosted in the cloud and streamed to users’ devices, with the provider managing the virtual desktop infrastructure and the customer managing images, applications, users and policies; billed per user or per hour.',
    'Streaming a movie instead of buying the DVD: you watch on any screen, and nothing is stored on your device.',
    'Six interns get Windows desktops with Tally and Office for three months on Amazon WorkSpaces; their personal laptops only display the screen, company data never leaves AWS, and the desktops are deleted when the internship ends.',
    'Amazon WorkSpaces (Personal, Pool), Amazon WorkSpaces Applications (app streaming); Azure Virtual Desktop, Windows 365 Cloud PC; Omnissa Horizon and Citrix DaaS (on any cloud).',
    'Desktop virtualization was introduced in Lesson 4.1.', A4,
    'temporary staff, remote workers, BYOD, secure access to sensitive apps.',
    'users need heavy offline work or very low-latency graphics without a good connection.',
    plain='A full computer desktop that runs in the cloud and appears on any laptop or tablet through the internet.',
    how=[('Directory', 'Connect to Active Directory/Entra ID.'), ('Bundle/image', 'OS + apps + size.'), ('Provision', 'Desktop per user or pooled.'), ('Connect', 'Client app or browser streams pixels (PCoIP/DCV/RDP).'), ('Manage', 'Patching images, policies, auto-stop.')],
    words=[('virtual desktop', 'a desktop running on a server, shown remotely'), ('BYOD', 'bring your own device'), ('pooled desktop', 'shared desktops reset after use')],
    diff=table(['', 'DaaS', 'Physical laptops'], [['Data location', 'cloud', 'device'], ['Provisioning', 'minutes', 'days (buy, ship, image)'], ['Offline work', 'no', 'yes']], minw=440),
    where=['Call centres and BPOs', 'Contractors and interns', 'Secure access for banks and healthcare'],
    realworld='Microsoft launched Windows 365 in 2021 as a fixed-price “Cloud PC” per user per month — DaaS sold like a SaaS subscription.',
    pro='DaaS costs are dominated by hours, not users: auto-stop (WorkSpaces AutoStop, AVD scaling plans) for desktops idle after work hours often halves the bill.')

A5 = mk(['Continuous replication', 'Disaster declared', 'Fail over in minutes'], ['replicate|servers + disks|to cloud', 'disaster|site down|or ransomware', 'recover|launch in cloud|switch traffic'], ['blue', 'red', 'green'],
        ['changes copied continuously to a low-cost staging area', 'the primary site is lost', 'recovered machines run in the cloud; fail back later'],
        [('Replicate', 'Servers are continuously replicated to the cloud.', ''), ('Disaster', 'The primary site fails.', ''), ('Recover', 'Machines launch in the cloud within minutes; fail back later.', '')],
        'DRaaS in action', 'Disaster recovery as a service.', 'DRaaS', 'Animation: continuous replication to cloud; disaster; failover to recovered machines.', 'x5anim')
T5 = vtype(5, 'DRaaS (Disaster Recovery as a Service)', 'red',
    '<b>Disaster Recovery as a Service (DRaaS)</b> continuously replicates servers, applications and data from a primary site (on-premises or another cloud/Region) to a provider’s cloud, and orchestrates failover and failback, so organisations get a recovery site without building or paying for a second data centre.',
    'A spare house on rent that is kept furnished as a copy of yours and updated every night — you only move in if your house floods.',
    'TiffinGo’s central-kitchen billing server (on-premises) replicates to AWS with Elastic Disaster Recovery; in a drill, the server came up in Mumbai in 18 minutes with data a few seconds old.',
    'AWS Elastic Disaster Recovery, Azure Site Recovery, Google Cloud Backup and DR; partners such as Zerto and Veeam.',
    'DR strategies (backup, pilot light, warm standby) are in Lesson 7.2.', A5,
    'you need a recovery site with low RTO/RPO but cannot justify a second data centre.',
    'you never test failover — DRaaS is only as good as its drills.',
    plain='A cloud service that keeps a live copy of your servers and can start them in the cloud quickly if your main site is destroyed.',
    how=[('Agent/replication', 'Block-level replication of disks.'), ('Staging', 'Low-cost staging area with tiny instances/storage.'), ('Plan', 'Recovery order, network settings.'), ('Fail over', 'Launch recovery instances on demand.'), ('Fail back', 'Reverse replication when the primary returns.')],
    words=[('replication', 'continuously copying changes'), ('failover', 'switching to the recovery site'), ('failback', 'returning to the original site'), ('drill', 'a practice recovery')],
    diff=table(['', 'DRaaS', 'Backup only'], [['RTO', 'minutes', 'hours–days'], ['RPO', 'seconds', 'hours'], ['Cost', 'higher', 'lower']], minw=420),
    where=['On-premises servers needing a DR site', 'Cross-Region DR in the cloud', 'Ransomware recovery'],
    realworld='Azure Site Recovery replicates Hyper-V, VMware and physical servers as well as Azure VMs between regions — one of the most common first cloud workloads for enterprises that are not yet ready to migrate.',
    pro='Ransomware changes DR design: replicating instantly also replicates encryption. Point-in-time recovery points (keep many hours/days of snapshots) let you fail over to the minute <i>before</i> the attack.')

A6 = mk(['Traffic through the service', 'Inspect and protect', 'Report centrally'], ['users/apps|anywhere|any device', 'security cloud|WAF, SWG,|threat detect', 'console|alerts|one policy'], ['blue', 'red', 'green'],
        ['security delivered from the cloud, not boxes', 'filtering, firewalls and detection as a service', 'one policy and dashboard for all locations'],
        [('Route', 'Users’ and apps’ traffic or logs flow through a security service.', ''), ('Protect', 'The service filters, inspects and detects threats.', ''), ('Report', 'Central policies, alerts and reports.', '')],
        'SECaaS in action', 'Security delivered as a service.', 'SECaaS', 'Animation: traffic through a cloud security service; inspection and protection; central reporting.', 'x6anim')
T6 = vtype(6, 'SECaaS (Security as a Service)', 'red',
    '<b>Security as a Service (SECaaS)</b> delivers security capabilities — web application firewalls, DDoS protection, secure web gateways and zero-trust access, email security, threat detection, vulnerability scanning, identity and SIEM — as cloud services, without customers installing and running security appliances.',
    'Hiring a security agency with guards, CCTV control room and patrol vans instead of building your own security department.',
    'TiffinGo turned on AWS WAF in front of its API, GuardDuty for threat detection and Security Hub for a single findings view — no appliances, billed per request/event.',
    'AWS WAF, Shield, GuardDuty, Inspector, Security Hub; Microsoft Defender for Cloud, Sentinel (SIEM), Entra ID; Google Cloud Armor, Security Command Center, Google Security Operations; Zscaler, Cloudflare, CrowdStrike.',
    'Module 9 covers cloud security.', A6,
    'small teams need enterprise-grade security quickly, or users and apps are spread across many locations.',
    'you assume buying the service equals being secure — configuration and response are still yours.',
    plain='Security tools — firewalls, virus and attack detection — rented from the cloud instead of buying and running security machines.',
    how=[('Onboard', 'Enable the service or route traffic/logs to it.'), ('Policies', 'Rules, managed rule sets, baselines.'), ('Detect', 'Signals from traffic, logs and threat intelligence.'), ('Respond', 'Block automatically; alert humans.'), ('Report', 'Dashboards and compliance reports.')],
    words=[('WAF', 'web application firewall'), ('SIEM', 'system that collects and analyses security events'), ('zero trust', 'verify every access, trust no network by default')],
    diff=table(['', 'SECaaS', 'Security appliances'], [['Deployment', 'enable/subscribe', 'buy, rack, maintain'], ['Updates (signatures, rules)', 'automatic', 'your job'], ['Scale', 'elastic', 'box capacity']], minw=440),
    where=['Web apps and APIs (WAF, DDoS)', 'Remote workforce access', 'Threat detection and SIEM'],
    realworld='Google acquired Mandiant (2022) and Microsoft built Sentinel as a cloud-native SIEM — the big clouds now sell security operations as a service alongside infrastructure.',
    pro='Managed WAF rule sets block common attacks on day one, but they also block legitimate traffic sometimes — start in “count” mode, review, then switch to “block”.')

A7 = mk(['Choose a model', 'Call an API', 'Pay per token/call'], ['model|LLM, vision,|speech', 'API|prompt / image|→ response', 'billing|per token|per image'], ['violet', 'blue', 'amber'],
        ['foundation models and AI services hosted by the provider', 'one API call — no GPUs to manage', 'usage-based; guardrails and quotas apply'],
        [('Choose', 'Pick a model or AI service (text, image, speech, vision).', ''), ('Call', 'Send a prompt or file through an API; get the result.', ''), ('Pay', 'Billed per token, call or image; GPUs are the provider’s problem.', '')],
        'AIaaS in action', 'AI capability on demand.', 'AIaaS', 'Animation: choose a model; call the API; pay per token.', 'x7anim')
T7 = vtype(7, 'AIaaS (AI as a Service)', 'violet',
    '<b>AI as a Service (AIaaS)</b> provides artificial-intelligence capabilities — foundation models for text, code and images, speech, vision, translation, document extraction, and managed ML platforms — through APIs and managed services, so applications use AI without owning GPUs or training infrastructure.',
    'Hiring a translator or designer by the hour from an agency instead of employing one full-time.',
    'TiffinGo writes menu descriptions in Hindi and Marathi with a foundation model on Amazon Bedrock, and reads supplier invoices with a document-extraction API — paying per token and per page.',
    'Amazon Bedrock, SageMaker AI, Textract, Rekognition, Transcribe; Microsoft Foundry (Azure OpenAI), Azure AI services; Google Vertex AI (Gemini), Document AI, Speech-to-Text.',
    'AI services are mapped across clouds in Lesson 6.4.', A7,
    'you need AI features quickly and do not want to run GPUs or train models.',
    'data cannot leave your boundary under the provider’s terms, or per-token costs at scale exceed running your own model.',
    plain='Renting artificial intelligence from the cloud: send a question, text or picture to an online service and get an intelligent answer back.',
    how=[('Access', 'Enable models/services; check Region availability.'), ('Call', 'API/SDK with prompts or files.'), ('Ground', 'Add your data (RAG) and guardrails.'), ('Control', 'Quotas, logging, content filters.'), ('Pay', 'Per token/call; provisioned throughput for steady load.')],
    words=[('foundation model', 'a large AI model usable for many tasks'), ('token', 'a piece of a word; the billing unit for text models'), ('guardrail', 'a rule that filters unsafe or off-topic output')],
    diff=table(['', 'AIaaS API', 'Self-hosted model'], [['GPUs', 'provider’s', 'yours'], ['Time to start', 'minutes', 'days–weeks'], ['Cost at high volume', 'can be high', 'can be lower']], minw=440),
    where=['Chatbots and assistants', 'Document processing', 'Translation, speech and image analysis'],
    realworld='Product names change fast in this family: Azure AI Foundry became Microsoft Foundry (2025) and SageMaker became SageMaker AI (2024) — check current names before exams.',
    pro='Cost per answer depends far more on prompt and response length than on the model price list: caching repeated prompts and asking for short structured output often cut AIaaS bills dramatically.')

SUMMARY = table(['#', 'Model', 'You provide', 'Provider runs', 'Example'], [
    ['1', 'FaaS', 'function code', 'servers, scaling, runtime', 'Lambda, Azure Functions, Cloud Run functions'], ['2', 'BaaS', 'configuration, data', 'back-end services', 'Cognito, DynamoDB, Firebase'], ['3', 'CaaS', 'containers, manifests', 'orchestration', 'ECS/EKS, AKS, GKE'],
    ['4', 'DaaS', 'images, users', 'desktop infrastructure', 'WorkSpaces, Azure Virtual Desktop'], ['5', 'DRaaS', 'protected servers, plans', 'replication, recovery site', 'Elastic DR, Site Recovery'], ['6', 'SECaaS', 'policies, response', 'security engines', 'WAF, GuardDuty, Defender'], ['7', 'AIaaS', 'prompts, data', 'models, GPUs', 'Bedrock, Microsoft Foundry, Vertex AI']], minw=660)
CHECK = ('  <h3>Check yourself: which XaaS?</h3>\n' +
    qx('A. Resize a photo every time a customer uploads one.', ['DaaS', 'FaaS', 'DRaaS', 'IaaS'], 1, 'Event-driven function.') +
    qx('B. 50 call-centre agents need Windows desktops for a 3-month campaign.', ['DaaS', 'CaaS', 'SECaaS', 'FaaS'], 0, 'Virtual desktops.') +
    qx('C. Keep a recovery copy of on-premises servers ready in the cloud.', ['DRaaS', 'BaaS', 'AIaaS', 'PaaS'], 0, 'Disaster recovery.') +
    qx('D. Translate menus with a hosted large language model.', ['AIaaS', 'CaaS', 'DaaS', 'IaaS'], 0, 'AI API.'))

TYPES = ('  <p>Seven “as a service” models, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['Why can giving a Lambda function more memory make it cheaper?', 'Why is a provisioned RDS instance “managed” but not “serverless”?', 'Why can DRaaS replicate your ransomware?'], 'types 1, 2 and 5') + MAP
         + jump(['FaaS', 'BaaS', 'CaaS', 'DaaS', 'DRaaS', 'SECaaS', 'AIaaS']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('Trigger / event source', 'What starts a function.', 'Defines the architecture.', 'HTTP, schedule, storage, queue, stream.'),
    ('Execution role / identity', 'Permissions the function uses.', 'Least privilege per function.', 'Lambda execution role, managed identity, service account.'),
    ('Timeout and memory', 'Limits per invocation.', 'Cost and CPU depend on memory.', 'Lambda 1–900 s, 128 MB–10 GB.'),
    ('Concurrency', 'Parallel executions.', 'Protects downstream systems; account limits apply.', 'Reserved/provisioned concurrency, max instances.'),
    ('Cold start mitigations', 'Ways to avoid init delay.', 'Latency-sensitive APIs.', 'Provisioned concurrency, SnapStart, min instances, Premium plan.'),
    ('Dead-letter / retry policy', 'What happens when async calls fail.', 'No lost events.', 'Lambda DLQ/destinations, Functions retry, Pub/Sub DLQ.')])

DEEP = ('  <h3>Cold starts in numbers</h3>\n' + table(['Factor', 'Effect'], [['Runtime', 'Python/Node start fast; Java/.NET slower (JVM/CLR)'], ['Package size', 'bigger zips/images take longer to load'], ['Init code', 'heavy imports and connections add time'], ['VPC networking', 'once slow; now uses pre-created network interfaces (Hyperplane)'], ['Mitigation', 'provisioned concurrency, SnapStart (Java, Python, .NET), min instances (Cloud Run / Azure Premium)']], minw=480) +
    '\n  <h3>Serverless economics: break-even</h3>\n  <p>FaaS cost = requests × price + GB-seconds × price. A function at 1 request/second all month costs very little; at 1,000 requests/second steadily, a container fleet with a Savings Plan is usually cheaper. Calculate both (Lesson 5.5) — serverless wins on spiky and low traffic.</p>\n'
    '  <h3>XaaS and the NIST model</h3>\n  <p>NIST defines only three service models (IaaS, PaaS, SaaS). FaaS, CaaS, DaaS and the rest are industry terms that fit inside them: FaaS and CaaS sit between IaaS and PaaS, DaaS is delivered like SaaS on IaaS, and SECaaS/AIaaS are mostly SaaS/PaaS. Exams use both vocabularies.</p>')

clouds = vendor_tabs('<p><b>AWS:</b> Lambda (FaaS), Cognito/DynamoDB/S3/SQS (BaaS), ECS/EKS/Fargate (CaaS), WorkSpaces (DaaS), Elastic Disaster Recovery (DRaaS), WAF/GuardDuty/Security Hub (SECaaS), Bedrock/SageMaker AI (AIaaS).</p>',
    '<p><b>Azure:</b> Functions, Cosmos DB/Blob/Service Bus/Entra External ID, AKS/Container Apps/ACI, Azure Virtual Desktop/Windows 365, Site Recovery, Defender for Cloud/Sentinel, Microsoft Foundry/Azure AI services.</p>',
    '<p><b>Google Cloud:</b> Cloud Run functions, Firebase/Firestore/Pub/Sub, GKE/Cloud Run, partner DaaS (Citrix, Omnissa) and Chrome Enterprise, Backup and DR, Cloud Armor/Security Command Center, Vertex AI/Gemini.</p>') + \
    cloud3([['FaaS', 'Lambda', 'Azure Functions', 'Cloud Run functions'], ['CaaS', 'ECS / EKS / Fargate', 'AKS / Container Apps', 'GKE / Cloud Run'], ['DaaS', 'WorkSpaces', 'Azure Virtual Desktop / Windows 365', 'partner solutions'], ['DRaaS', 'Elastic Disaster Recovery', 'Site Recovery', 'Backup and DR'], ['AIaaS', 'Bedrock', 'Microsoft Foundry', 'Vertex AI']])

# ------------------------------------------------------------------ practical
PY = "import json, datetime\ndef lambda_handler(event, context):\n    print('Sending today\\'s menu', datetime.datetime.utcnow().isoformat())\n    return {'statusCode': 200, 'body': json.dumps({'sent': True})}"
MAIN = "import functions_framework, datetime\n@functions_framework.http\ndef menu(request):\n    print('Sending today\\'s menu', datetime.datetime.utcnow().isoformat())\n    return 'sent'"

MOCKQ.extend([
 (mock('aws', ['Lambda', 'Functions', 'Create function'], ['Dashboard', 'Applications', 'Functions', 'Layers'], 'Functions',
       [('Author from scratch', '( ) selected'), ('Function name', 'tiffingo-menu-mailer'), ('Runtime', '▾ Python 3.12'), ('Execution role', '( ) Create a new role with basic Lambda permissions')], 'Create function'),
  mock('az', ['Home', 'Function App', 'Create'], ['Basics', 'Storage', 'Networking', 'Monitoring', 'Review + create'], 'Basics',
       [('Hosting', '( ) Flex Consumption'), ('Function App name', 'tiffingo-fn-1234'), ('Runtime stack · Version', 'Python · 3.12'), ('Region', '▾ Central India')], 'Review + create'),
  mock('gcp', ['Cloud Run', 'Write a function'], ['Services', 'Jobs', 'Functions'], 'Services',
       [('Service name', 'tiffingo-menu-mailer'), ('Region · Runtime', 'asia-south1 · Python 3.12'), ('Authentication', '( ) Require authentication'), ('Entry point', 'menu')], 'Create')),
 (mock('aws', ['Amazon EventBridge', 'Schedules', 'Create schedule'], ['Rules', 'Event buses', 'Schedules', 'Pipes'], 'Schedules',
       [('Schedule name', 'menu-7am'), ('Schedule pattern', 'cron(30 1 * * ? *) — 07:00 IST'), ('Target', '▾ AWS Lambda Invoke → tiffingo-menu-mailer')], 'Create schedule'),
  mock('az', ['Home', 'tiffingo-fn-1234', 'Functions'], ['Overview', 'Functions', 'Configuration', 'Logs'], 'Functions',
       [('Template', 'Timer trigger'), ('Schedule (NCRONTAB, UTC)', '0 30 1 * * *')], 'Create'),
  mock('gcp', ['Cloud Scheduler', 'Create a job'], ['Cloud Scheduler jobs', 'App Engine Cron jobs'], 'Cloud Scheduler jobs',
       [('Name · Region', 'menu-7am · asia-south1'), ('Frequency · Time zone', '0 7 * * * · Asia/Kolkata'), ('Target', 'HTTP → function URL (OIDC token)')], 'Create')),
 (mock('aws', ['CloudWatch', 'Log groups', '/aws/lambda/tiffingo-menu-mailer'], ['Log groups', 'Logs Insights', 'Live Tail'], 'Log groups',
       [('Filter events', 'REPORT'), ('Line', 'Duration: 12 ms · Init Duration: 145 ms · Max Memory Used: 38 MB')], 'Search'),
  mock('az', ['Home', 'tiffingo-fn-1234', 'Log stream'], ['Overview', 'Functions', 'Log stream', 'Application Insights'], 'Log stream',
       [('Executed', "'Functions.menu' (Succeeded, Duration=…ms)")], 'Start'),
  mock('gcp', ['Cloud Run', 'tiffingo-menu-mailer', 'Logs'], ['Metrics', 'SLOs', 'Logs', 'Revisions'], 'Logs',
       [('Severity', '▾ Default'), ('Line', "Sending today's menu 2026-11-12T01:30:00")], 'Stream logs')),
])

STEP1 = ('1 · Deploy and invoke a function (FaaS)', tri(
    (['[[Lambda]] → [[Create function]] → [[Author from scratch]] → name <code>tiffingo-menu-mailer</code>, runtime Python 3.12, [[Create a new role with basic Lambda permissions]] → [[Create function]].', 'Replace the code with the snippet on the right → [[Deploy]] → [[Test]] → create a test event → [[Test]].', 'Read the execution result: duration, billed duration, memory used.'],
     f"cat > lambda_function.py <<'EOF'\n{PY}\nEOF\nzip fn.zip lambda_function.py\naws iam create-role --role-name tiffingo-fn-role --assume-role-policy-document \\\n  '{{\"Version\":\"2012-10-17\",\"Statement\":[{{\"Effect\":\"Allow\",\"Principal\":{{\"Service\":\"lambda.amazonaws.com\"}},\"Action\":\"sts:AssumeRole\"}}]}}'\naws iam attach-role-policy --role-name tiffingo-fn-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole\nsleep 15\nACCT=$(aws sts get-caller-identity --query Account --output text)\naws lambda create-function --function-name tiffingo-menu-mailer --runtime python3.12 --handler lambda_function.lambda_handler \\\n  --zip-file fileb://fn.zip --role arn:aws:iam::$ACCT:role/tiffingo-fn-role --memory-size 256 --timeout 10\naws lambda wait function-active --function-name tiffingo-menu-mailer\naws lambda invoke --function-name tiffingo-menu-mailer --log-type Tail out.json --query LogResult --output text | base64 -d | tail -2",
     'a REPORT line like <code>Duration: 2.1 ms Billed Duration: 3 ms Memory Size: 256 MB Max Memory Used: 38 MB Init Duration: 140 ms</code> — the Init Duration is the cold start.'),
    (['[[Function App]] → [[Create]] → [[Flex Consumption]] → name <code>tiffingo-fn-&lt;n&gt;</code>, Python 3.12, Central India → [[Review + create]].', 'In Cloud Shell create an HTTP function with Core Tools and publish (commands on the right).', 'Call <code>https://APP.azurewebsites.net/api/menu</code>.'],
     'APP=tiffingo-fn-$RANDOM; SA=tiffingofn$RANDOM\naz group create --name rg-tiffingo --location centralindia\naz storage account create --name $SA --resource-group rg-tiffingo --location centralindia --sku Standard_LRS\naz functionapp create --resource-group rg-tiffingo --name $APP --storage-account $SA \\\n  --flexconsumption-location centralindia --runtime python --runtime-version 3.12\nfunc init menu-fn --python && cd menu-fn\nfunc new --name menu --template "HTTP trigger" --authlevel anonymous\nfunc azure functionapp publish $APP\ncurl "https://$APP.azurewebsites.net/api/menu?name=TiffinGo"',
     '“Hello, TiffinGo. This HTTP triggered function executed successfully.”'),
    (['[[Cloud Run]] → [[Write a function]] → name <code>tiffingo-menu-mailer</code>, asia-south1, Python 3.12, [[Require authentication]].', 'Paste the code on the right as main.py, entry point <code>menu</code> → [[Save and redeploy]].', '[[Testing]] tab or call it with an identity token.'],
     f"mkdir menu && cd menu\ncat > main.py <<'EOF'\n{MAIN}\nEOF\necho 'functions-framework==3.*' > requirements.txt\ngcloud functions deploy tiffingo-menu-mailer --gen2 --region=asia-south1 --runtime=python312 \\\n  --source=. --entry-point=menu --trigger-http --no-allow-unauthenticated\nURL=$(gcloud functions describe tiffingo-menu-mailer --region=asia-south1 --format='value(url)')\ncurl -H \"Authorization: bearer $(gcloud auth print-identity-token)\" $URL",
     '<code>sent</code>. Without the token the URL returns 403 — the function is private.')),
    'A function exists only as code + configuration until an event arrives.')

STEP2 = ('2 · Run it every morning (scheduled event)', tri(
    (['[[Amazon EventBridge]] → [[Schedules]] → [[Create schedule]] → name <code>menu-7am</code>, recurring, cron <code>30 1 * * ? *</code> (07:00 IST = 01:30 UTC).', 'Target [[AWS Lambda Invoke]] → tiffingo-menu-mailer; let it create the execution role → [[Create schedule]].'],
     "FN=$(aws lambda get-function --function-name tiffingo-menu-mailer --query Configuration.FunctionArn --output text)\naws events put-rule --name menu-7am --schedule-expression 'cron(30 1 * * ? *)'\naws lambda add-permission --function-name tiffingo-menu-mailer --statement-id menu-7am --action lambda:InvokeFunction \\\n  --principal events.amazonaws.com --source-arn $(aws events describe-rule --name menu-7am --query Arn --output text)\naws events put-targets --rule menu-7am --targets Id=1,Arn=$FN\naws events list-targets-by-rule --rule menu-7am --query 'Targets[].Arn' --output text",
     'the function ARN as the rule’s target. For a quick test use <code>rate(5 minutes)</code> and change it back.'),
    (['In the function project add a timer function: <code>func new --name daily --template "Timer trigger"</code>, set the schedule to <code>0 30 1 * * *</code> (UTC) in function_app.py, publish again.', 'Function App → [[Functions]] → daily → [[Monitor]] shows each run.'],
     'func new --name daily --template "Timer trigger"\n# edit function_app.py: schedule="0 30 1 * * *"   (NCRONTAB with seconds, UTC)\nfunc azure functionapp publish $APP\naz functionapp function list --resource-group rg-tiffingo --name $APP --query "[].name" --output tsv',
     '<code>…/menu</code> and <code>…/daily</code> listed; runs appear under Monitor at 07:00 IST.'),
    (['[[Cloud Scheduler]] → [[Create job]] → name <code>menu-7am</code>, region asia-south1, frequency <code>0 7 * * *</code>, time zone Asia/Kolkata.', 'Target HTTP → the function URL, method GET, auth header [[Add OIDC token]] with a service account that may invoke the function → [[Create]] → [[Force run]] to test.'],
     "P=$(gcloud config get-value project)\ngcloud iam service-accounts create scheduler-invoker\ngcloud functions add-invoker-policy-binding tiffingo-menu-mailer --region=asia-south1 \\\n  --member=serviceAccount:scheduler-invoker@$P.iam.gserviceaccount.com\ngcloud scheduler jobs create http menu-7am --location=asia-south1 --schedule='0 7 * * *' --time-zone='Asia/Kolkata' \\\n  --uri=$URL --http-method=GET --oidc-service-account-email=scheduler-invoker@$P.iam.gserviceaccount.com\ngcloud scheduler jobs run menu-7am --location=asia-south1",
     'the job created and a forced run; the function log shows “Sending today’s menu”.')),
    'Scheduled functions replace the “small server that runs cron” — the most common first serverless win.')

STEP3 = ('3 · Read the cold start and the cost', tri(
    (['[[CloudWatch]] → [[Log groups]] → <code>/aws/lambda/tiffingo-menu-mailer</code> → search <code>REPORT</code>.', 'Invoke twice quickly: the first REPORT has <b>Init Duration</b> (cold), the second does not (warm).', 'Bill: [[Cost Explorer]] → service Lambda — at this volume ₹0 (always-free tier).'],
     "for i in 1 2; do aws lambda invoke --function-name tiffingo-menu-mailer --log-type Tail out.json --query LogResult --output text | base64 -d | grep REPORT; done",
     'two REPORT lines; usually only the first contains <code>Init Duration</code>. Change memory to 1024 MB and compare Duration.'),
    (['Function App → [[Log stream]] (or Application Insights → [[Live metrics]]).', 'Call the URL after 15+ idle minutes and again immediately: the first response is slower (cold start on Flex Consumption unless always-ready instances are set).'],
     'for i in 1 2; do curl -s -o /dev/null -w "%{time_total}s\\n" "https://$APP.azurewebsites.net/api/menu?name=x"; done',
     'the first time noticeably longer than the second.'),
    (['Cloud Run → service → [[Logs]]; [[Metrics]] → container startup latency.', '[[Edit & deploy new revision]] → [[Minimum number of instances]] = 1 removes cold starts (but costs money while idle).'],
     "for i in 1 2; do curl -s -o /dev/null -w '%{time_total}s\\n' -H \"Authorization: bearer $(gcloud auth print-identity-token)\" $URL; done\ngcloud functions logs read tiffingo-menu-mailer --region=asia-south1 --limit=5",
     'a slower first call after idle, faster second call, and the log lines.')),
    'Cold starts are the price of scale-to-zero; pay for minimum/provisioned instances only where latency matters.')

prac = practical(OWN_INTRO + ' Functions and schedules at this volume stay within free tiers.', [SETUP_STEP, STEP1, STEP2, STEP3],
    cleanup='<b>AWS:</b> <code>aws events remove-targets --rule menu-7am --ids 1; aws events delete-rule --name menu-7am; aws lambda delete-function --function-name tiffingo-menu-mailer; aws iam detach-role-policy --role-name tiffingo-fn-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole; aws iam delete-role --role-name tiffingo-fn-role</code>.<br>'
            '<b>Azure:</b> <code>az group delete --name rg-tiffingo --yes --no-wait</code>.<br>'
            '<b>Google Cloud:</b> <code>gcloud scheduler jobs delete menu-7am --location=asia-south1 --quiet; gcloud functions delete tiffingo-menu-mailer --region=asia-south1 --quiet; gcloud iam service-accounts delete scheduler-invoker@$P.iam.gserviceaccount.com --quiet</code>.')

mist = mistakes([
    ['Running a VM for a job that runs minutes a day.', 'Habit.', 'Scheduled functions or jobs.'],
    ['Long tasks in functions.', 'Functions feel simple.', 'Use containers/batch for > 15 min; or Step Functions/Durable Functions to orchestrate.'],
    ['Opening DB connections inside the handler.', 'Simple code.', 'Create clients outside the handler to reuse in warm starts; use proxies/pools.'],
    ['One huge role for all functions.', 'Convenience.', 'Least-privilege role per function.'],
    ['Ignoring concurrency limits.', 'Assuming infinite scale.', 'Set reserved/max concurrency to protect databases; request quota increases.'],
    ['Calling everything “serverless”.', 'Marketing.', 'Check: no servers, scale to zero, pay per use.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Serverless computing, FaaS, and the XaaS family (CaaS, DaaS, DRaaS, SECaaS…).'], ['AWS CLF-C02', 'Lambda and serverless services, Fargate, WorkSpaces, Elastic Disaster Recovery, security services, Bedrock.'], ['AZ-900', 'Serverless (Functions, Logic Apps), containers (ACI, AKS, Container Apps), Azure Virtual Desktop.'], ['Google Cloud Digital Leader', 'Serverless computing (Cloud Run, Cloud Run functions), containers (GKE), AI services.']], minw=560) + \
    qx('1. Which AWS service runs code without provisioning servers and bills per request and duration?', ['Amazon EC2', 'AWS Lambda', 'Amazon EBS', 'Amazon VPC'], 1, 'FaaS.') + \
    qx('2. Serverless is commonly defined as…', ['IaaS + PaaS', 'FaaS + BaaS', 'SaaS only', 'containers only'], 1, 'Roberts’ definition.') + \
    qx('3. Which Azure service delivers virtual Windows desktops from the cloud?', ['Azure Virtual Desktop', 'Azure Functions', 'Azure Batch', 'Azure Arc'], 0, 'DaaS.') + \
    qx('4. A cold start is…', ['a failed deployment', 'extra delay when a new execution environment is created', 'a database restore', 'a DNS timeout'], 1, 'Init delay.') + \
    qx('5. Which AWS service provides disaster recovery by replicating servers to AWS?', ['AWS Elastic Disaster Recovery', 'Amazon Inspector', 'AWS Artifact', 'Amazon Lex'], 0, 'DRaaS.') + \
    qx('6. Which is an example of AI as a service?', ['Amazon Bedrock', 'Amazon EBS', 'AWS Direct Connect', 'Amazon VPC'], 0, 'Foundation models via API.')

proj = miniproject('Mini project: make TiffinGo’s small jobs serverless',
    'Replace always-on servers with events and functions — and price it.',
    ['<b>Find</b> three jobs that run occasionally (menu mailer, nightly report trigger, photo resize).',
     '<b>Design</b> each as an event + function (+ BaaS services) diagram.',
     '<b>Build</b> one: function + schedule on your own account (steps 1–2).',
     '<b>Measure</b> cold vs warm times and memory settings (step 3).',
     '<b>Cost</b> it: monthly requests × duration × memory vs the VM it replaces.',
     '<b>XaaS map:</b> which other needs (desktops, DR, security, AI) could be bought as a service?'],
    'One working scheduled function, timings and a cost comparison.', 'This lesson + 6.1 (compute) + 7.4 (serverless architecture) + 5.5 (pricing).')

assemble_v2(HERE, story_h2='A 4-second job on a 24-hour server', hook_html=hk,
    narration='TiffinGo paid for a server all day to run a 4-second job once a morning. The fix was not a cheaper server — it was no server at all.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Serverless, FaaS and XaaS',
    formal='<b>Serverless computing</b> is a cloud execution model in which the provider dynamically manages the allocation of servers, applications are built from <b>functions (FaaS)</b> triggered by events and fully managed <b>back-end services (BaaS)</b>, resources scale automatically to zero, and billing is based on actual usage. <b>XaaS</b> (“anything as a service”) is the umbrella for delivering any IT capability — containers, desktops, disaster recovery, security, AI — as an on-demand service.',
    simple='Serverless: you write small pieces of code that run only when needed, and pay only for that time. XaaS: almost any IT need can now be rented as a service.',
    interview=['“Serverless means no server management, automatic scaling including to zero, and pay-per-use — FaaS like Lambda for code plus BaaS like DynamoDB, S3 and Cognito for the back end.”', '“XaaS extends the service models: CaaS for containers, DaaS for desktops, DRaaS for recovery, SECaaS for security, AIaaS for models.”'],
    terms_rows=[('Serverless', 'No servers to manage; pay per use.'), ('FaaS', 'Functions on events.'), ('BaaS', 'Managed back-end services.'), ('Cold start', 'Init delay of a new environment.'), ('CaaS', 'Managed containers.'), ('DaaS', 'Cloud desktops.'), ('DRaaS', 'Disaster recovery service.'), ('SECaaS', 'Security service.'), ('AIaaS', 'AI via API.'), ('XaaS', 'Anything as a service.')],
    exam='CLF-C02 asks which services are serverless (Lambda, Fargate, DynamoDB, S3) and names WorkSpaces/Elastic DR; AZ-900 asks Functions, containers and Azure Virtual Desktop.',
    picture_h2='Serverless = FaaS + BaaS, and the XaaS family', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven “as a service” models, one by one', TYPES)],
    how_h2='Inside one function invocation (and a cold start)', how_intro='What the platform does before your code runs.', how_anim=INV,
    parts_h2='Six settings of every function', parts_html=parts, lv='',
    myth_rows=[('Serverless means no servers.', 'Servers exist; you do not manage them.', 'Definition.'), ('Serverless is always cheaper.', 'At steady high load containers/VMs can be cheaper.', 'Deep dive.'), ('Cold starts make serverless unusable.', 'They are milliseconds to a second and can be mitigated.', 'How it works.')],
    extra_secs=[('deep', 'Deep dive', 'Cold starts in numbers, serverless economics, XaaS vs NIST models', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Define serverless as FaaS + BaaS and list its characteristics.', 'Explain what happens in a function invocation and a cold start.', 'Describe CaaS, DaaS, DRaaS, SECaaS and AIaaS with examples.', 'Deploy, schedule and observe a function on your own account.', 'Decide when serverless is cheaper than servers.'],
    next_html='<a href="../05-iaas-vs-paas-vs-saas-choosing-a-model/">2.5 IaaS vs PaaS vs SaaS: choosing a model</a>.',
    pre='<b>Before you start:</b> <a href="../02-paas-platform-as-a-service-and-its-types/">2.2 PaaS</a> and <a href="../03-saas-software-as-a-service/">2.3 SaaS</a>.')
