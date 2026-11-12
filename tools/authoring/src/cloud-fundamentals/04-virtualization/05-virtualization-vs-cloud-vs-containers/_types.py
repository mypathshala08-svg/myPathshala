"""Lesson 4.5 — seven ways to run an app, one by one."""
from cloudkit import *

def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)

def mapfig():
    o = t(320, 16, 'Seven ways to run an app — from “you run everything” to “you run only code”', 11, 'ink', bold=True)
    items = [('1', 'Virtualized data centre', 'your hypervisor, tickets', 'card'), ('2', 'Private cloud', 'your hardware, self-service API', 'card'), ('3', 'Public cloud VM', 'IaaS: EC2, Azure VM, GCE', 'blue'),
             ('4', 'Containers + orchestrator', 'Kubernetes / ECS on VMs', 'blue'), ('5', 'Serverless containers', 'Fargate, Cloud Run, Container Apps', 'green'), ('6', 'Serverless functions', 'Lambda, Azure Functions', 'green'), ('7', 'Micro-VMs', 'Firecracker: the engine under 5 and 6', 'violet')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 14 + (i % 4) * 156; y = 34 + (i // 4) * 84
        o += box(x, y, 148, 72, tn, rx=8) + pin(x + 14, y + 16, n) + t(x + 28, y + 20, a, 8.2, 'ink', anchor='start', bold=True) + t(x + 8, y + 44, b, 7, 'ink2', anchor='start')
    o += f'<path d="M30,226 L610,226" style="stroke:#999;stroke-width:2"/><path d="M604,221 L612,226 L604,231" style="fill:#999"/>'
    o += t(30, 244, 'you manage more', 7.4, 'ink2', anchor='start') + t(610, 244, 'you manage less (and control less)', 7.4, 'ink2', anchor='end')
    o += t(320, 266, 'Types 1–2 are about who runs the data centre; 3–6 about how much of the stack you hand over; 7 is the technology that makes 5–6 safe.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of seven ways to run an app: 1 virtualized data centre, 2 private cloud, 3 public cloud VM, 4 containers with an orchestrator, 5 serverless containers, 6 serverless functions, 7 micro-VMs; an arrow from “you manage more” to “you manage less”.', mapfig(), h=276)

# 1 virtualized DC
def a_vdc(k):
    o = t(180, 12, ['Developer raises a ticket', 'Admin creates the VM by hand', 'Three days later: a VM'][k], 9, 'ink', bold=True)
    for i, (n, sub) in enumerate([('Ravi', 'needs a VM'), ('ticket queue', 'approval'), ('admin', 'vCenter clicks'), ('VM', 'ready')]):
        x = 10 + i * 88
        on = i <= [1, 2, 3][k]
        o += box(x, 40, 78, 50, ('green' if i == 3 else 'blue') if on else 'card', rx=6) + t(x + 39, 62, n, 8, 'ink', bold=True) + t(x + 39, 78, sub, 6.8, 'ink2')
        if i < 3 and i < [1, 2, 3][k]:
            o += packet(x + 78, 65, x + 88, 65, '')
    o += t(180, 120, ['Day 1, 10:00', 'Day 2: approved · Day 3: created', 'no bill per team · no automatic scaling'][k], 7.8, 'red' if k == 2 else 'ink', bold=True)
    return o
A_VDC = cap([a_vdc(k) for k in range(3)], [('Raise a ticket', 'The developer fills a form: “2 vCPU, 4 GB, Ubuntu”. It waits in a queue', 'for a manager’s approval.'), ('Admin works by hand', 'An administrator logs into vCenter or Hyper-V Manager and creates the VM,', 'asks the network team for an IP.'), ('A VM — three days later', 'Virtualization did its job in minutes; the process took days. Costs sit in one', 'IT budget; nothing scales by itself.')],
    'A virtualized data centre', 'Virtualization without the cloud operating model.', 'Ticket-driven VMs', 'Animation: developer raises a ticket; it waits for approval; an admin creates the VM by hand; the VM is ready days later.', 'c1anim')
T1 = vtype(1, 'Virtualized data centre', 'amber',
    'A <b>virtualized data centre</b> runs its workloads as virtual machines on hypervisor clusters owned and operated by the organization, but VMs are requested, approved and created by administrators rather than through on-demand self-service, and usage is not metered per consumer.',
    'A restaurant kitchen with modern equipment but only one chef taking orders on paper: the stoves are efficient, yet every dish waits in the order queue.',
    'Until 2018 TiffinGo’s parent company ran VMware. Getting a test server meant a ticket, a manager’s approval and an admin — typically three days, even though creating the VM itself took five minutes.',
    'VMware vSphere, Microsoft Hyper-V with System Center, Nutanix AHV, Proxmox VE — used without a self-service portal or chargeback.',
    '', A_VDC,
    'workloads are stable, regulations require on-premises hosting and demand rarely changes.',
    'teams need servers quickly or often — the ticket process, not the technology, becomes the bottleneck.',
    plain='The company owns its servers and uses virtual machines, but to get one you must ask the IT team and wait. It is efficient hardware with a slow, manual process.',
    how=[('Hosts and hypervisors', 'The company buys servers and runs a hypervisor cluster.'), ('Request', 'A user asks for a VM through a ticket or email.'), ('Approval', 'A manager approves capacity and cost.'), ('Manual build', 'An admin creates the VM, asks for an IP, installs software.'), ('Hand-over', 'The user gets credentials; costs stay in one shared IT budget.')],
    words=[('vCenter', 'VMware’s management console'), ('ticket', 'a tracked request in a help-desk system'), ('chargeback / showback', 'billing (or showing) each team its usage')],
    diff=table(['', 'Virtualized DC', 'Private cloud', 'Public cloud'], [['Self-service', 'no', 'yes', 'yes'], ['Metering per team', 'no', 'yes (showback)', 'yes (bill)'], ['Elasticity', 'buy hardware first', 'up to own capacity', 'practically unlimited'], ['Who owns hardware', 'you', 'you (or a host for you)', 'provider']], minw=540),
    where=['Many banks, PSUs and government departments', 'Factories and hospitals with on-site systems', 'Small and mid-size companies with a VMware cluster'],
    realworld='Most enterprises that virtualized in 2005–2015 still run parts of their estate this way; NIST’s definition is the usual yardstick used to decide whether such an environment can honestly be called a “cloud”.',
    pro='The fastest way to turn a virtualized DC into something cloud-like is not new hardware but an API: put Terraform/Ansible plus a service catalogue in front of vCenter and the three-day ticket becomes a ten-minute pipeline.')

# 2 private cloud
def a_pc(k):
    o = t(180, 12, ['Self-service portal / API', 'Scheduler places the VM', 'Usage shown per team'][k], 9, 'ink', bold=True)
    o += box(10, 40, 80, 50, 'blue', rx=6) + t(50, 62, 'Ravi', 8, 'ink', bold=True) + t(50, 78, 'portal / CLI', 6.8, 'ink2')
    o += box(120, 30, 110, 70, 'violet' if k >= 0 else 'card', rx=6) + t(175, 50, 'OpenStack', 8, 'ink', bold=True) + t(175, 66, 'Nova · Neutron', 6.8, 'ink2') + t(175, 80, 'Cinder · Keystone', 6.8, 'ink2')
    o += box(260, 30, 90, 70, 'card' if k == 0 else 'green', rx=6) + t(305, 56, 'KVM hosts', 8, 'ink', bold=True) + t(305, 72, '(your data centre)', 6.8, 'ink2')
    if k == 0:
        o += packet(90, 65, 120, 65, 'API')
    if k == 1:
        o += packet(230, 65, 260, 65, 'boot') + t(180, 124, 'VM ready in ~1 minute, no ticket', 7.6, 'green', bold=True)
    if k == 2:
        o += box(10, 112, 340, 26, 'amber', rx=5) + t(180, 129, 'showback: kitchen team 12 vCPU · billing team 8 vCPU', 7.6, 'ink', bold=True)
    return o
A_PC = cap([a_pc(k) for k in range(3)], [('Self-service request', 'Ravi creates a VM himself in the portal or with the CLI, within his', 'team’s quota — no ticket.'), ('Scheduler places it', 'The cloud software (e.g. OpenStack Nova) picks a host, creates the network', 'port and disk, and the hypervisor boots the VM.'), ('Metered per team', 'Usage is recorded per project and shown or charged back —', 'the NIST “measured service”.')],
    'A private cloud', 'Cloud behaviour on your own hardware.', 'Private cloud', 'Animation: user calls the OpenStack API; the scheduler boots a VM on a KVM host in about a minute; usage is shown per team.', 'c2anim')
T2 = vtype(2, 'Private cloud', 'amber',
    'A <b>private cloud</b> provides cloud characteristics — on-demand self-service, resource pooling, rapid elasticity within its capacity, broad network access and measured service — on infrastructure used exclusively by one organization, whether hosted on its premises or by a third party.',
    'A company canteen with a self-service counter and a swipe card: same kitchen the company owns, but employees serve themselves and each department sees its monthly bill.',
    'TiffinGo’s parent company keeps customer data on-premises for compliance but wants developers to get servers in minutes. It installs OpenStack on its KVM hosts: teams create VMs via portal/API within quotas and see monthly showback reports.',
    'OpenStack, VMware Cloud Foundation, Microsoft Azure Local (formerly Azure Stack HCI), Nutanix, Apache CloudStack; provider-managed on-premises: AWS Outposts, Google Distributed Cloud.',
    '', A_PC,
    'data must stay in your building or country, you already own large hardware, or need predictable fixed costs.',
    'you are small — running cloud software well needs a skilled platform team; elasticity stops at the hardware you own.',
    plain='Your company keeps its own servers but runs them like a cloud: teams create servers themselves through a website or command, and each team can see how much it uses.',
    how=[('Pool hardware', 'Hypervisor hosts, storage and networks are pooled.'), ('Add a cloud control plane', 'Software such as OpenStack provides APIs for compute, network, storage and identity.'), ('Projects and quotas', 'Each team gets a project with limits.'), ('Self-service', 'Users create VMs, networks and volumes through portal/API/Terraform.'), ('Schedule', 'The scheduler places VMs on hosts with capacity.'), ('Meter', 'Usage is collected per project for showback/chargeback.')],
    words=[('OpenStack', 'open-source software to build private clouds'), ('control plane', 'the software brain that takes API requests and orchestrates'), ('quota', 'a usage limit per team'), ('showback', 'showing each team its usage without billing')],
    diff=table(['', 'Private cloud', 'Virtualized DC', 'Public cloud'], [['Self-service API', 'yes', 'no', 'yes'], ['Capacity limit', 'your hardware', 'your hardware', 'provider’s (very large)'], ['Cost model', 'capex + ops team', 'capex', 'pay per use'], ['Data location', 'your control', 'your control', 'provider Regions']], minw=540),
    where=['Banks and government with data-residency rules', 'Telecom operators', 'Research institutes (e.g. HPC clouds)', 'Large enterprises with existing data centres'],
    realworld='CERN runs one of the largest OpenStack private clouds for its physics computing, giving scientists self-service VMs on hardware it owns.',
    pro='Hybrid tools blur the line: AWS Outposts racks run real EC2 and EBS on your premises, managed by AWS through the same APIs — a “private” location with a public-cloud control plane.')

# 3 public cloud VM (REQ anim lives in the how section)
T3 = vtype(3, 'Public cloud virtual machines (IaaS)', 'blue',
    'A <b>public cloud VM</b> is a virtual machine rented on demand from a cloud provider’s shared, multi-tenant infrastructure through self-service APIs, billed per second or hour, with the provider operating the hardware and hypervisor and the customer managing the guest OS and everything above it.',
    'Renting a fully furnished flat by the night through an app: you pick size and city, get the key instantly, pay per night; the owner maintains the building, you keep your flat clean.',
    'On Diwali TiffinGo launches ten extra t3.medium instances in Mumbai in two minutes and terminates them the next morning, paying only for those hours.',
    'Amazon EC2, Azure Virtual Machines, Google Compute Engine, Oracle Cloud VMs, Indian providers such as CtrlS/Yotta/Tata cloud VMs.',
    '', '',
    'legacy or OS-specific apps, full control of the OS, steady long-running servers, lift-and-shift.',
    'you leave VMs running 24×7 when they are needed only part-time, or never patch the guest OS (your responsibility).',
    deep='<b>See it step by step</b> in the “Getting a server in a cloud” animation in the next section, and the full EC2 lesson <a href="../../02-service-models/01-iaas-infrastructure-as-a-service/">2.1</a>.',
    plain='You rent a virtual computer from a company like AWS over the internet, start it in about a minute, and pay only while it runs. They look after the hardware; you look after what runs inside.',
    how=[('Self-service API call', 'Console, CLI or Terraform calls RunInstances.'), ('Identity check', 'IAM verifies you may launch that type.'), ('Quota and capacity', 'Account limits and AZ capacity are checked.'), ('Placement', 'A scheduler picks a physical host.'), ('Virtualization', 'The hypervisor creates the VM; Nitro attaches EBS and network.'), ('Metering', 'Per-second billing starts while it is running.')],
    words=[('IaaS', 'infrastructure as a service: rented VMs, disks, networks'), ('multi-tenant', 'many customers share the same hardware'), ('per-second billing', 'you pay for the exact seconds used (with a minimum)')],
    diff=table(['', 'Cloud VM', 'Container', 'Function'], [['You manage', 'OS + runtime + app', 'image (runtime + app)', 'code'], ['Start', '~1 min', 'ms–s', 'ms–s'], ['Billing unit', 'instance-second', 'task / node', 'request + ms']], minw=520),
    where=['Web and app servers', 'Databases you manage yourself', 'Windows workloads', 'Lift-and-shift migrations'],
    realworld='Netflix runs its streaming control plane on Amazon EC2 and scales thousands of instances up in the evening peak and down at night.',
    pro='On EC2 you can see the virtualization fingerprint from inside: <code>systemd-detect-virt</code> prints <code>amazon</code> on Nitro instances and <code>xen</code> on older families — useful when a performance issue differs between t2 and t3.')

# 4 containers + orchestrator
def a_k8s(k):
    o = t(180, 12, ['Declare: run 3 copies of menu-api', 'Scheduler places pods on nodes', 'A node dies — pods are recreated'][k], 9, 'ink', bold=True)
    o += box(10, 30, 110, 46, 'violet', rx=6) + t(65, 48, 'Kubernetes', 8, 'ink', bold=True) + t(65, 64, 'replicas: 3', 7, 'ink2')
    for n in range(3):
        x = 140 + n * 72
        dead = (k == 2 and n == 0)
        o += box(x, 30, 64, 100, 'red' if dead else 'card', rx=6) + t(x + 32, 44, f'node {n + 1}', 7.4, 'ink', bold=True) + (t(x + 32, 60, 'VM (EC2)', 6.6, 'ink2'))
        pods = [] if k == 0 else ([1] if n < 3 else [])
        if k == 2:
            pods = [] if n == 0 else ([1, 1] if n == 1 else [1])
        for p_i, _ in enumerate(pods):
            o += box(x + 8, 70 + p_i * 28, 48, 22, 'blue', rx=3) + t(x + 32, 85 + p_i * 28, 'pod', 7, 'ink', bold=True)
    if k == 1:
        o += packet(120, 53, 140, 53, 'place')
    if k == 2:
        o += t(180, 146, 'node 1 failed → its pod restarted on node 2 automatically', 7.4, 'green', bold=True)
    return o
A_K8S = cap([a_k8s(k) for k in range(3)], [('Declare the desired state', 'A Deployment says: run 3 copies of the menu-api container image.', 'You describe what, not where.'), ('Schedule onto nodes', 'The scheduler places pods on worker nodes (VMs) with free CPU and memory;', 'each node’s runtime starts the containers (namespaces + cgroups).'), ('Self-healing', 'A node fails: the controller notices fewer than 3 pods running and starts', 'a replacement on a healthy node within seconds.')],
    'Containers with an orchestrator', 'How Kubernetes keeps containers running across many VMs.', 'Kubernetes', 'Animation: a deployment requests three replicas; the scheduler places pods on three VM nodes; a node fails and its pod is recreated on another node.', 'c4anim')
T4 = vtype(4, 'Containers with an orchestrator (Kubernetes, ECS)', 'blue',
    'Containers package an application with its dependencies and run as isolated processes sharing a host kernel; a <b>container orchestrator</b> such as Kubernetes or Amazon ECS schedules them across a cluster of machines (usually VMs), keeps the desired number running, connects them and rolls out new versions.',
    'A food court manager: stalls (containers) are placed in free spaces (nodes); if one counter breaks, the manager immediately sets the stall up at another counter, and adds more counters at lunchtime.',
    'TiffinGo runs menu-api, billing and notifications as containers on an EKS cluster of four EC2 nodes. During the sale the Deployment scales to 12 pods; when a node fails, its pods move to the others automatically.',
    'Kubernetes (self-managed, EKS, AKS, GKE, OpenShift), Amazon ECS, HashiCorp Nomad, Docker Swarm.',
    '', A_K8S,
    'many services, frequent releases, need for self-healing and scaling, portability across clouds.',
    'a single small app — the cluster’s operational cost and learning curve can outweigh the benefit.',
    plain='Programs are packed in small boxes (containers). A manager program (like Kubernetes) decides which computer runs which box, keeps the right number running, and restarts boxes that fail.',
    how=[('Build an image', 'Dockerfile → image pushed to a registry (ECR, Docker Hub).'), ('Declare desired state', 'YAML/JSON says: image, replicas, CPU/memory, ports.'), ('Schedule', 'The scheduler picks nodes with enough free resources.'), ('Run', 'On each node the container runtime creates namespaces and cgroups and starts the container.'), ('Connect', 'Services and load balancers give the pods a stable address.'), ('Reconcile forever', 'Controllers compare actual vs desired state and fix differences (restart, reschedule, scale).')],
    words=[('orchestrator', 'software that runs containers across many machines'), ('node', 'a machine (usually a VM) in the cluster'), ('pod', 'Kubernetes’ smallest unit: one or more containers'), ('Deployment', 'a declaration of how many copies of which image to run'), ('reconcile', 'continuously make reality match the declaration')],
    diff=table(['', 'Containers + orchestrator', 'Serverless containers', 'VMs'], [['You manage nodes?', 'yes (or managed node groups)', 'no', 'yes'], ['Control', 'high', 'medium', 'highest'], ['Billing', 'per node VM', 'per task CPU/memory-second', 'per VM']], minw=520),
    where=['Microservices platforms', 'Internal developer platforms', 'Machine-learning serving', 'Hybrid/multi-cloud apps'],
    realworld='Spotify and Airbnb have both described moving their services onto Kubernetes, and managed Kubernetes (EKS, AKS, GKE) is now the most common way large companies run microservices.',
    pro='Pods on EKS are just Linux processes on EC2 instances: VM isolation between customers, container density inside. That “containers on VMs” layering is the normal cloud pattern, not a compromise.')

# 5 serverless containers
def a_sc(k):
    o = t(180, 12, ['You give an image and a size', 'AWS finds capacity for you', 'Scale tasks, never see a server'][k], 9, 'ink', bold=True)
    o += box(10, 34, 120, 60, 'blue', rx=6) + t(70, 54, 'task definition', 8, 'ink', bold=True) + t(70, 70, 'nginx:alpine', 7, 'ink2') + t(70, 84, '0.25 vCPU · 512 MB', 7, 'ink2')
    o += box(160, 26, 190, 104, 'card', rx=6) + t(255, 42, 'AWS-managed fleet (hidden)', 7.4, 'ink2', bold=True)
    n = 0 if k == 0 else (1 if k == 1 else 4)
    for i in range(n):
        o += box(170 + (i % 2) * 90, 52 + (i // 2) * 38, 80, 32, 'green', rx=4) + t(210 + (i % 2) * 90, 66 + (i // 2) * 38, 'task', 7.4, 'ink', bold=True) + t(210 + (i % 2) * 90, 78 + (i // 2) * 38, 'own micro-VM', 6.2, 'ink2')
    if k == 1:
        o += packet(130, 64, 170, 64, 'run')
    if k == 2:
        o += t(180, 146, 'billed per vCPU-second and GB-second of each task', 7.4, 'green', bold=True)
    return o
A_SC = cap([a_sc(k) for k in range(3)], [('Give an image and a size', 'You register a task definition: image, 0.25 vCPU, 512 MB, port 80.', 'No cluster nodes to create.'), ('AWS finds capacity', 'Fargate places the task on its own hidden fleet, each task isolated', 'in its own Firecracker micro-VM.'), ('Scale tasks, not servers', 'Run 1 or 400 tasks; pay per vCPU-second and GB-second;', 'no OS to patch, no node to resize.')],
    'Serverless containers in action', 'Containers without managing any servers.', 'Fargate / Cloud Run', 'Animation: a task definition with image and size; AWS places a task in its hidden fleet in its own micro-VM; tasks scale to four with per-second billing.', 'c5anim')
T5 = vtype(5, 'Serverless containers (Fargate, Cloud Run, Container Apps)', 'green',
    '<b>Serverless containers</b> run container images on infrastructure fully managed by the cloud provider: you specify the image and the CPU/memory per task, and the platform provisions, isolates, scales and patches the underlying servers, billing per resource-second.',
    'Ordering from a cloud kitchen instead of running your own: you give the recipe (image) and portion size; where and on which stove it is cooked is not your concern.',
    'TiffinGo’s nightly invoice generator is a container that runs for 20 minutes. On Fargate it needs no cluster nodes: a scheduled task starts at 1 a.m. and costs only those 20 minutes.',
    'AWS Fargate (for ECS and EKS), AWS App Runner, Google Cloud Run, Azure Container Apps and Azure Container Instances.',
    '', A_SC,
    'containerized apps without wanting to manage nodes; spiky or scheduled workloads; small teams.',
    'you need special hardware (some GPUs), privileged containers, or the lowest cost at very steady high load (EC2 nodes can be cheaper).',
    plain='You hand the cloud a packaged app (a container) and say how much CPU and memory it needs. The cloud runs it somewhere and charges you only for that time — you never see or manage a server.',
    how=[('Register a task/service', 'Image, CPU, memory, ports, IAM role, network.'), ('Request to run', 'A service or schedule asks for N tasks.'), ('Capacity found', 'The provider selects hosts in its fleet.'), ('Isolation', 'Fargate runs each task in its own Firecracker micro-VM; Cloud Run uses its own sandboxing.'), ('Networking', 'Each task gets an ENI/IP in your VPC (Fargate awsvpc mode).'), ('Bill and scale', 'Per vCPU-second and GB-second; scale on CPU, requests or schedule.')],
    words=[('task definition', 'ECS’s description of how to run a container'), ('task', 'one running copy'), ('awsvpc mode', 'each task gets its own network card in your VPC'), ('GB-second', 'one GB of memory for one second — a billing unit')],
    diff=table(['', 'Serverless containers', 'Containers on your nodes', 'Functions'], [['Unit', 'container task', 'container on node', 'function invocation'], ['Max run time', 'unlimited (service) ', 'unlimited', 'Lambda: 15 min'], ['Nodes to manage', 'none', 'yes', 'none']], minw=520),
    where=['APIs and web apps', 'Scheduled batch jobs', 'Background workers', 'Event-driven processing that runs longer than functions allow'],
    realworld='AWS states that Fargate tasks each run in their own isolated environment and do not share kernel, CPU, memory or network interface with other tasks — implemented with Firecracker micro-VMs.',
    pro='Cloud Run scales to zero and bills per request-time by default, so an idle container service costs nothing — functions-style economics for any language and any binary that listens on a port.')

# 6 functions
def a_fn(k):
    o = t(180, 12, ['An event arrives', 'Cold start, then run handler()', 'Burst to many, then to zero'][k], 9, 'ink', bold=True)
    o += box(10, 40, 90, 50, 'blue', rx=6) + t(55, 60, 'event', 8, 'ink', bold=True) + t(55, 76, 'HTTP / S3 / queue', 6.6, 'ink2')
    if k == 0:
        o += packet(100, 65, 160, 65, 'GET /menu') + box(160, 40, 120, 50, 'card', rx=6) + t(220, 68, 'Lambda service', 8, 'ink', bold=True)
    if k == 1:
        o += box(140, 30, 120, 70, 'green', rx=6) + t(200, 48, 'micro-VM', 7.6, 'ink', bold=True) + t(200, 64, 'Python runtime', 7, 'ink2') + t(200, 80, 'handler()', 7.6, 'ink', bold=True) + packet(260, 65, 320, 65, '200 OK')
    if k == 2:
        for i in range(6):
            o += box(130 + (i % 3) * 72, 30 + (i // 3) * 44, 64, 36, 'green', rx=4) + t(162 + (i % 3) * 72, 52 + (i // 3) * 44, 'copy', 7.4, 'ink', bold=True)
        o += t(180, 140, '1,000 events → many copies · no events → nothing runs, nothing billed', 7.2, 'green', bold=True)
    return o
A_FN = cap([a_fn(k) for k in range(3)], [('An event arrives', 'An HTTP request, a file upload to S3, a queue message or a schedule', 'triggers the function.'), ('Cold start, then handler()', 'If no warm environment exists, a micro-VM and runtime start; then your', 'handler runs and returns. Warm calls skip the start.'), ('Scale out, then to zero', 'Many events → many concurrent copies. No events → nothing runs and', 'nothing is billed.')],
    'Serverless functions in action', 'Only your code, only when an event happens.', 'Functions as a Service', 'Animation: an event reaches the Lambda service; a micro-VM with runtime runs handler and returns 200; many events create many copies, no events scale to zero.', 'c6anim')
T6 = vtype(6, 'Serverless functions (FaaS)', 'green',
    '<b>Function as a Service (FaaS)</b> runs small units of code in response to events, with the provider managing all servers, runtimes and scaling; functions are short-lived and stateless, scale automatically including to zero, and are billed per request and per unit of execution time.',
    'A taxi instead of owning a car: it comes when you call, you pay per ride, and when you do not need it, it costs nothing — but you cannot keep your luggage in it overnight.',
    'When a customer uploads a dish photo to S3, a Lambda function creates a thumbnail in under a second. At night there are no uploads and the cost is zero.',
    'AWS Lambda, Azure Functions, Google Cloud Run functions (formerly Cloud Functions), Cloudflare Workers.',
    '', A_FN,
    'event-driven glue, spiky or unpredictable APIs, file and stream processing, scheduled small jobs.',
    'long jobs (Lambda max 15 minutes), steady high traffic (can cost more than containers), or latency-critical paths sensitive to cold starts.',
    plain='You upload only a small piece of code. It runs automatically whenever something happens — a web request, a file upload — and you pay only for those few milliseconds. When nothing happens, nothing runs.',
    how=[('Upload code', 'A zip or container image with a handler function, runtime and memory size.'), ('Connect a trigger', 'API Gateway/function URL, S3 event, queue, schedule.'), ('Event arrives', 'The service finds a warm execution environment or creates one (cold start: micro-VM + runtime + init code).'), ('Run handler', 'Your function runs with the event; one environment handles one request at a time.'), ('Scale', 'More concurrent events → more environments, up to account limits.'), ('Freeze and reuse', 'Idle environments are frozen, reused for later calls, then removed.')],
    words=[('FaaS', 'function as a service'), ('handler', 'the function the platform calls'), ('cold start', 'the extra time to prepare a new environment'), ('stateless', 'keeps nothing between calls — store state in a database'), ('concurrency', 'how many copies run at the same time')],
    diff=table(['', 'Functions', 'Serverless containers', 'VMs'], [['Unit', 'one invocation', 'one task', 'one server'], ['Idle cost', 'zero', 'zero (Cloud Run) / per running task', 'full'], ['Max duration', 'Lambda 15 min', 'unlimited', 'unlimited'], ['Packaging', 'code zip / image', 'container image', 'whole OS image']], minw=540),
    where=['Image/thumbnail processing', 'Webhooks and small APIs', 'Data pipeline steps', 'Scheduled housekeeping', 'Chatbot back ends'],
    realworld='AWS Lambda, launched in 2014, introduced per-request billing to mainstream cloud computing; today it is used for event processing such as resizing images uploaded to S3 and as the back end of API Gateway endpoints.',
    pro='Code outside the handler runs once per environment (during the cold start) and is then reused: open database connections and load ML models there, not inside <code>handler()</code>, or every request pays the setup cost.')

# 7 micro-VM (FC anim)
def T7(FC):
    return vtype(7, 'Micro-VMs (Firecracker)', 'violet',
        'A <b>micro-VM</b> is a lightweight virtual machine with a minimal device model and a stripped-down monitor, designed to boot in around a hundred milliseconds with very small memory overhead, combining the hardware-level isolation of VMs with the speed and density of containers. <b>Firecracker</b> is AWS’s open-source micro-VM monitor used by Lambda and Fargate.',
        'A capsule hotel: each guest gets a real private locked capsule (own walls, unlike a hostel bunk), but it is tiny, cheap and ready in seconds compared with a full hotel room.',
        'TiffinGo’s thumbnail function and invoice task run on Lambda and Fargate. Each runs in its own micro-VM, so even if another customer’s code on the same machine were malicious, it would need to break a VM boundary — not just a container — to reach TiffinGo.',
        'Firecracker (AWS Lambda, AWS Fargate), Kata Containers, Cloud Hypervisor; related sandbox: gVisor (Google Cloud Run, GKE Sandbox).',
        '', FC,
        'running untrusted or multi-tenant code with container-like speed.',
        'you need many devices, GPUs or full OS features — micro-VMs deliberately leave them out.',
        deep='<a href="../02-server-hardware-and-os-level-virtualization/#type4">4.2 hardware-assisted virtualization</a> (KVM, which Firecracker uses).',
        plain='A tiny virtual machine that starts almost as fast as a container. Each piece of customer code gets its own, so different customers are separated by a real VM wall.',
        how=[('Bare-metal host with KVM', 'Firecracker runs as a normal Linux process using KVM for hardware-assisted virtualization.'), ('Jailer', 'Each Firecracker process is locked down (cgroups, namespaces, seccomp) before it starts a VM.'), ('Minimal devices', 'Only virtio-net, virtio-block, a serial console and a minimal keyboard controller (used to reset) are emulated.'), ('Fast boot', 'A small guest kernel boots in about 125 ms; memory overhead under 5 MiB per micro-VM.'), ('Run the workload', 'The function runtime or container starts inside.'), ('Dense packing', 'Thousands of micro-VMs can run on one host.')],
        words=[('micro-VM', 'a very small, fast-booting VM'), ('VMM', 'virtual machine monitor — the program that runs a VM'), ('jailer', 'Firecracker’s helper that sandboxes each VMM process'), ('device model', 'the set of virtual hardware a VM sees')],
        diff=table(['', 'Micro-VM', 'Container', 'Full VM'], [['Own kernel', 'yes', 'no', 'yes'], ['Boot', '~125 ms', 'ms', '30–60 s'], ['Overhead', '< 5 MiB', 'tiny', 'hundreds of MB'], ['Isolation', 'VM-level', 'kernel-level', 'VM-level']], minw=520),
        where=['Serverless platforms (Lambda, Fargate)', 'Secure sandboxes for untrusted code', 'CI runners and code playgrounds'],
        realworld='AWS open-sourced Firecracker in 2018; it powers AWS Lambda and AWS Fargate, and AWS has described it as able to launch micro-VMs in as little as 125 ms with less than 5 MiB of memory overhead each.',
        pro='Firecracker is written in Rust and is about tens of thousands of lines — orders of magnitude smaller than QEMU — because every device you do not emulate is attack surface you do not have (Lesson 4.6, VM escape).')

SUMMARY = table(['#', 'Model', 'You manage', 'Start', 'Billing', 'Example'], [
    ['1', 'Virtualized DC', 'everything + tickets', 'days', 'IT budget', 'VMware cluster'], ['2', 'Private cloud', 'hardware + cloud software', '~1 min', 'showback', 'OpenStack, Azure Local'],
    ['3', 'Public cloud VM', 'OS and above', '~1 min', 'per second', 'EC2'], ['4', 'Containers + orchestrator', 'nodes + images', 'seconds', 'per node', 'EKS, AKS, GKE'],
    ['5', 'Serverless containers', 'image', 'seconds', 'per task-second', 'Fargate, Cloud Run'], ['6', 'Functions', 'code', 'ms (warm)', 'per request + ms', 'Lambda'], ['7', 'Micro-VM', '(engine under 5–6)', '~125 ms', '—', 'Firecracker']], minw=640)
CHECK = ('  <h3>Check yourself: which model fits?</h3>\n' +
    qx('A. Data must stay in the company’s own building, but teams want servers in minutes.', ['Virtualized DC', 'Private cloud', 'Public cloud functions', 'Micro-VM'], 1, 'Self-service + metering on own hardware.') +
    qx('B. A 20-minute container job runs once a night; no servers to manage.', ['Lambda', 'Serverless containers (Fargate scheduled task)', 'A VM 24×7', 'LPAR'], 1, 'Too long for Lambda’s 15 minutes; no nodes to manage.') +
    qx('C. Resize every uploaded photo, traffic is unpredictable.', ['Function triggered by S3', 'Dedicated VM', 'Private cloud', 'Virtualized DC'], 0, 'Event-driven, scales to zero.') +
    qx('D. 40 microservices, frequent releases, need self-healing and portability.', ['Containers with Kubernetes', 'One big VM', 'Functions only', 'Manual servers'], 0, 'Orchestrator schedules and heals containers.') +
    qx('E. What isolates one Lambda customer from another on the same host?', ['A VLAN', 'Firecracker micro-VMs', 'A container only', 'Nothing'], 1, 'Each execution environment runs in its own micro-VM.'))

def build(FC):
    intro = ('  <p>“Virtualization vs cloud vs containers” becomes clear when you line up the seven real ways an app can be run today — from a ticket-driven VMware cluster to a function that runs only when an event arrives. Each one, in the same order as 4.1.</p>\n'
             + challenge(['Why can Fargate safely run two customers’ containers on one host?', 'Where should you open a database connection in a Lambda function, and why?', 'How can a bare-metal EC2 instance still be “cloud”?'], 'types 5, 6 and 3 (plus the deep dive)') + MAP
             + jump(['Virtualized DC', 'Private cloud', 'Cloud VM', 'Containers', 'Serverless containers', 'Functions', 'Micro-VM']))
    return intro + T1 + T2 + T3 + T4 + T5 + T6 + T7(FC) + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY + '\n' + CHECK
