import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)


hk = hook('TiffinGo has five jobs to run: an order API, a menu website, photo resizing, a nightly sales report and a “dishes you may like” model. Should all five run on virtual machines?',
    'No. Clouds offer a whole <b>menu of compute products</b> — virtual machines, bare-metal servers, Kubernetes, serverless containers, functions, app platforms, and batch/GPU services. They differ in one thing above all: <b>how much you manage versus how much the provider manages</b>. This lesson explains each, shows what happens inside the cloud when you click “Launch”, and walks you through launching a VM and a serverless container on <b>your own</b> AWS, Azure or Google Cloud account.',
    ['Seven kinds of compute — when to pick which.', 'What really happens in the 30 seconds after “Launch instance”.', 'How to read names like m7i.large, Standard_D2s_v5 and e2-standard-2.'])

def story_scene():
    o = t(180, 12, 'Five jobs, five different shapes', 9, 'ink', bold=True)
    jobs = [('Order API', '24×7', 'blue'), ('Menu site', 'just code', 'violet'), ('Photo resize', 'on upload', 'green'), ('Sales report', 'nightly', 'amber'), ('ML model', 'needs GPU', 'red')]
    for i, (n, s, tn) in enumerate(jobs):
        x = 6 + i * 70
        o += box(x, 26, 64, 64, tn, rx=8) + t(x + 32, 52, n, 7, 'ink', bold=True) + t(x + 32, 70, s, 6.6, 'ink2')
    o += t(180, 112, 'One size does not fit all: each job maps to a different compute product.', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Five boxes: order API running 24×7, menu website that is just code, photo resizing on upload, a nightly sales report, an ML model needing a GPU.', story_scene(), 'Match the <tspan font-weight="700" class="s-acc">job</tspan> to the compute product.', h=130)
dialogue = '''R> Sir, we already have two VMs. Let’s just add more VMs for everything.
A> Photo resizing runs for 2 seconds when someone uploads a picture. A VM would sit idle the other 23 hours and 59 minutes.
K> So a function for that?
A> Yes. The menu site is plain code — an app platform builds and runs it for us. The nightly report can use a batch service on cheap Spot capacity. The model needs a GPU instance only while training.
R> And the order API?
A> VMs or containers — it runs all day and we want control. Let’s look at the full menu of compute and learn to choose.'''

# ------------------------------------------------------------------ picture
def specfig():
    o = t(320, 16, 'The compute spectrum: who manages what', 11, 'ink', bold=True)
    cols = ['Bare metal', 'Virtual machine', 'Kubernetes', 'Serverless containers', 'App platform (PaaS)', 'Functions']
    layers = ['Your code', 'Runtime / libraries', 'Container / scaling', 'Operating system', 'Virtualization', 'Physical server']
    # you manage (blue) until index, provider (green) after
    you = [[1, 1, 1, 1, 1, 0], [1, 1, 1, 1, 0, 0], [1, 1, 1, 0.5, 0, 0], [1, 1, 0.5, 0, 0, 0], [1, 0.5, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0]]
    for c, name in enumerate(cols):
        x = 120 + c * 86
        o += t(x + 40, 38, name, 7, 'ink', bold=True)
        for r, lay in enumerate(layers):
            v = you[c][r]
            tn = 'blue' if v == 1 else ('amber' if v == 0.5 else 'green')
            o += box(x, 46 + r * 28, 80, 24, tn, rx=3)
    for r, lay in enumerate(layers):
        o += t(112, 62 + r * 28, lay, 7.4, 'ink', anchor='end', bold=True)
    o += box(120, 222, 14, 10, 'blue', rx=2) + t(138, 231, 'you manage', 7.4, 'ink', anchor='start') + box(220, 222, 14, 10, 'amber', rx=2) + t(238, 231, 'shared (you configure)', 7.4, 'ink', anchor='start')
    o += box(370, 222, 14, 10, 'green', rx=2) + t(388, 231, 'provider manages', 7.4, 'ink', anchor='start')
    o += t(320, 254, '← more control and more work          less work and less control →', 8, 'ink2')
    return o
SPEC = bigfig('Grid of six compute products from bare metal to functions against six layers from physical server to your code; moving right, the provider manages more layers and you manage fewer.', specfig(), h=264)

def chooserfig():
    o = t(320, 16, 'Which compute? A quick decision path', 11, 'ink', bold=True)
    qs = [('Runs only when an event happens, finishes in minutes?', 'Functions'), ('A web app or API as plain code, no OS work wanted?', 'App platform (PaaS)'), ('Packaged as a container image?', 'Serverless containers → or Kubernetes if many services'),
          ('Big parallel jobs or needs GPUs?', 'Batch / accelerated'), ('Needs full OS control, any software?', 'Virtual machine'), ('Needs the physical server (licence, own hypervisor)?', 'Bare metal')]
    for i, (q, a) in enumerate(qs):
        y = 32 + i * 34
        o += box(10, y, 360, 26, 'card', rx=5) + t(190, y + 17, q, 7.6, 'ink') + arrow(372, y + 13, 400, y + 13) + t(386, y + 8, 'yes', 6.6, 'green', bold=True)
        o += box(402, y, 228, 26, ['green', 'violet', 'blue', 'amber', 'blue', 'red'][i], rx=5) + t(516, y + 17, a, 7.6, 'ink', bold=True)
    o += t(320, 248, 'Ask from the top: start with the most managed option that fits, move down only when you need more control.', 7.6, 'ink2')
    return o
CHOOSER = bigfig('Decision path: event-driven short code → functions; plain web app → PaaS; container image → serverless containers or Kubernetes; big parallel or GPU work → batch or accelerated; full OS control → VM; physical server needed → bare metal.', chooserfig(), h=258)

picture = ('  <p>Every compute product sits somewhere on one spectrum — from “you run everything above the bare server” to “you only write the function”:</p>\n' + SPEC +
           '\n  <p>And a practical way to choose, asked from the most managed option downwards:</p>\n' + CHOOSER)

# ------------------------------------------------------------------ how: what happens when you click Launch
RN = {'you': (4, 54, 54, 50, 'user', 'You', 'Launch'), 'api': (66, 4, 60, 46, 'cloud', 'EC2 API', 'Region endpoint'), 'iam': (66, 104, 60, 46, 'shield', 'IAM', 'allowed?'),
      'pl': (138, 54, 62, 50, 'gear', 'Placement', 'pick a host'), 'disk': (212, 4, 64, 46, 'disk', 'EBS volume', 'from the AMI'), 'net': (212, 104, 64, 46, 'lb', 'ENI + IP', 'security group'), 'host': (290, 54, 66, 50, 'chip', 'Nitro host', 'boots the VM')}
RS = [dict(on=['you', 'api'], hot='api', move=(58, 70, 70, 40, 'request'), head='Step 1 · An API call, signed by you', text='Console click or CLI command — both become a signed RunInstances request to the', text2='Region’s EC2 endpoint (e.g. ec2.ap-south-1.amazonaws.com).', svc='Every console action is an API call — that is why the CLI can do everything'),
      dict(on=['you', 'api', 'iam'], hot='iam', move=(96, 50, 96, 104, 'check'), head='Step 2 · Permission and limits', text='IAM checks your user may run instances, use that image, subnet and role; quotas', text2='(vCPU limit per Region) are checked. Fail here → “UnauthorizedOperation”.', svc='IAM policies; Service Quotas (On-Demand vCPU limit)'),
      dict(on=['you', 'api', 'iam', 'pl'], hot='pl', move=(126, 127, 150, 90, ''), head='Step 3 · Placement: which physical server?', text='The control plane picks an AZ (your subnet decides) and a host with free capacity', text2='for that instance type. No capacity → “InsufficientInstanceCapacity”.', svc='Placement groups can ask for spread, cluster or partition'),
      dict(on=['you', 'api', 'iam', 'pl', 'disk'], hot='disk', move=(200, 70, 222, 40, 'image'), head='Step 4 · The root disk is created from the image', text='A new EBS volume is created from the AMI’s snapshot — your copy of the OS.', text2='Data loads lazily from S3-backed snapshot blocks as they are first read.', svc='AMI = snapshot + launch settings (Lesson 4.4)'),
      dict(on=['you', 'api', 'iam', 'pl', 'disk', 'net'], hot='net', move=(200, 90, 222, 120, 'network'), head='Step 5 · A network card, an IP, a firewall', text='An elastic network interface is attached in your subnet with a private IP (and a public', text2='IP if asked); the security group rules apply at that interface.', svc='VPC, subnet, security group — Lesson 6.3'),
      dict(on=list(RN), hot='host', move=(276, 127, 298, 90, ''), head='Step 6 · The hypervisor boots your VM', text='The Nitro hypervisor starts the VM; cloud-init runs your user data. State: pending →', text2='running (billing starts); status checks 2/2 pass a minute later.', svc='Same flow in Azure (Resource Manager) and Google Cloud (Compute Engine API)')]
LAUNCH = flow_anim('What happens in the 30 seconds after “Launch instance”', 'From your click to a running server — six steps inside the cloud.', 'Launching a VM', 'Animation: you send a request to the EC2 API; IAM and quotas are checked; placement picks a host; an EBS root volume is created from the AMI; a network interface with IP and security group is attached; the Nitro host boots the VM.', RN, RS, hid='launchflow')

# ------------------------------------------------------------------ types
def mapfig():
    o = t(320, 16, 'Seven kinds of cloud compute', 11, 'ink', bold=True)
    items = [('1', 'Virtual machines', 'EC2 · Azure VMs · Compute Engine', 'blue'), ('2', 'Bare metal', 'whole physical server', 'red'), ('3', 'Managed Kubernetes', 'EKS · AKS · GKE', 'violet'),
             ('4', 'Serverless containers', 'Fargate · Container Apps · Cloud Run', 'green'), ('5', 'Functions (FaaS)', 'Lambda · Functions · Cloud Run fn', 'green'), ('6', 'App platforms (PaaS)', 'Beanstalk · App Service · App Engine', 'violet'), ('7', 'Batch & accelerated', 'Batch services, GPU instances', 'amber')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 7.8, 'ink', bold=True) + t(x + 78, y + 54, b, 6.4, 'ink2')
    o += t(320, 210, '1–2 give you servers · 3–4 run containers · 5–6 run your code · 7 runs big jobs and special hardware.', 7.6, 'ink2')
    return o
MAP = bigfig('Map of seven compute types: 1 virtual machines, 2 bare metal, 3 managed Kubernetes, 4 serverless containers, 5 functions, 6 app platforms, 7 batch and accelerated computing.', mapfig(), h=222)

def a_vm(k):
    o = t(180, 12, ['Pick image + size', 'Runs beside other VMs', 'Stop → resize → start'][k], 9, 'ink', bold=True)
    o += box(14, 30, 150, 96, 'card', rx=8) + t(89, 46, 'physical host', 7, 'ink2')
    for i in range(3):
        mine = i == 0
        tn = ('blue' if mine and k > 0 else ('card' if not mine else 'amber')) if not (k == 2 and mine) else 'green'
        lab = ['you: m7i.large', 'other customer', 'other customer'][i] if k else ['your choice', '', ''][i]
        o += box(24 + i * 46, 56, 40, 54, tn if (k or mine) else 'card', rx=4) + t(44 + i * 46, 86, ['VM', 'VM', 'VM'][i] if (k or mine) else '', 7, 'ink')
    o += t(89, 120, 'hypervisor (Nitro)', 6.6, 'ink2')
    o += box(186, 30, 160, 96, ['amber', 'blue', 'green'][k], rx=8)
    o += t(266, 56, ['AMI: Amazon Linux 2023', 'state: running', 'm7i.large → m7i.xlarge'][k], 7.6, 'ink', bold=True)
    o += t(266, 78, ['type: m7i.large', '2 vCPU · 8 GiB', 'stopped, type changed'][k], 7.4, 'ink') + t(266, 98, ['disk: EBS 8 GiB', 'public IP 13.x.x.x', 'started (maybe on a new host)'][k], 7, 'ink2')
    o += t(180, 146, ['you choose the OS image and the hardware size', 'your VM shares the host but is isolated by the hypervisor', 'vertical scaling = stop, change size, start'][k], 7.4, 'ink', bold=True)
    return o
A_VM = cap([a_vm(k) for k in range(3)], [('Choose', 'Pick an OS image (AMI/marketplace image) and an instance type (vCPU, memory).', ''), ('Run', 'The VM runs on a physical host shared with other customers’ VMs; the', 'hypervisor keeps them isolated.'), ('Resize', 'Stop the VM, change the type, start it again — it may come back on a', 'different host (local instance-store data is lost).')],
    'A VM in action', 'Image + size → running server → resize.', 'Virtual machine', 'Animation: choosing an image and size; the VM running on a shared physical host; stopping and resizing it.', 'c1anim')
T1 = vtype(1, 'Virtual machines (IaaS compute)', 'blue',
    'A <b>virtual machine (VM) instance</b> is a software-defined server with its own operating system, virtual CPUs, memory, disks and network interfaces, created on demand from an <b>image</b> on a provider’s physical host and isolated from other VMs by a hypervisor. You choose the image and size and manage everything from the OS upward.',
    'Renting a furnished flat in a big building: your own lockable flat with your own kitchen, but the building, water and electricity belong to the owner.',
    'TiffinGo’s order API runs on two m7i.large VMs in two AZs behind a load balancer (Lesson 5.3). The team installs Java, the app and a monitoring agent itself, and patches the OS every month.',
    'Amazon EC2 (and Lightsail for simple fixed-price VPS), Azure Virtual Machines (and Virtual Machine Scale Sets), Google Compute Engine (and managed instance groups).',
    '', A_VM,
    'you need full control of the OS, any software, long-running servers, or a lift-and-shift of existing servers.',
    'the job is short or event-driven (pay for idle time) or you do not want to patch operating systems.',
    plain='A computer you rent over the internet. You pick how big it is and which operating system it runs; it starts in a minute; you look after everything installed on it.',
    how=[('Pick an image', 'AMI (AWS), image (Azure/GCP): OS plus pre-installed software.'), ('Pick a size', 'Instance type / VM size sets vCPUs, memory, network and disk limits.'), ('Place and boot', 'The control plane picks a host in your AZ; the hypervisor boots it (see “How it works”).'), ('Attach storage and network', 'Root disk from the image, extra block disks, a network interface in your subnet.'), ('Operate', 'You patch, monitor, back up and scale (Auto Scaling groups / scale sets / MIGs).')],
    words=[('image', 'a saved template of an OS disk'), ('instance type', 'the hardware size of the VM'), ('vCPU', 'a virtual processor — usually one hardware thread'), ('hypervisor', 'software that runs and isolates VMs')],
    diff=table(['', 'VM', 'Bare metal', 'Container'], [['Has its own OS kernel', 'yes', 'yes (the real one)', 'no — shares the host kernel'], ['Start time', '~1 minute', 'several minutes', 'seconds'], ['Shared hardware', 'yes, isolated by hypervisor', 'no', 'yes, isolated by the kernel']], minw=520),
    where=['Web/app servers, legacy and packaged software', 'Databases you manage yourself', 'Development and test machines'],
    realworld='Amazon EC2 launched in 2006 and today offers hundreds of instance types; all current-generation types run on the <b>AWS Nitro System</b>, which moves networking, storage and security to dedicated cards so almost all of the host’s CPU goes to customer VMs.',
    pro='“vCPU” is not the same everywhere: on most x86 types a vCPU is one hyper-thread (half a physical core), but on AWS Graviton (ARM) instances a vCPU is a full physical core — so a 2-vCPU Graviton and a 2-vCPU Intel instance are not equal for CPU-heavy work.')

def a_bm(k):
    o = t(180, 12, ['The whole server is yours', 'Bring your own hypervisor', 'Direct hardware access'][k], 9, 'ink', bold=True)
    o += box(40, 30, 280, 96, 'red' if k == 0 else 'card', rx=8) + t(180, 46, 'physical server: m7i.metal-24xl · 96 vCPU · 384 GiB', 7.4, 'ink', bold=True)
    if k == 0:
        o += box(60, 58, 240, 54, 'blue', rx=6) + t(180, 90, 'your OS directly on the hardware (no hypervisor)', 7.6, 'ink')
    elif k == 1:
        o += box(60, 56, 240, 20, 'violet', rx=4) + t(180, 70, 'your hypervisor (e.g. VMware, KVM)', 7.2, 'ink')
        for i in range(4): o += box(64 + i * 60, 82, 52, 30, 'blue', rx=4) + t(90 + i * 60, 101, 'your VM', 6.6, 'ink')
    else:
        o += box(60, 58, 110, 54, 'blue', rx=6) + t(115, 88, 'licence per core', 7.2, 'ink') + box(190, 58, 110, 54, 'green', rx=6) + t(245, 82, 'CPU counters,', 7.2, 'ink') + t(245, 96, 'special drivers', 7.2, 'ink')
    o += t(180, 146, ['no other customer on this machine', 'run nested virtualization yourself', 'per-core licences and low-level tools work'][k], 7.4, 'ink', bold=True)
    return o
A_BM = cap([a_bm(k) for k in range(3)], [('Whole server', 'You rent the entire physical server; your OS runs directly on the hardware.', ''), ('Your own hypervisor', 'You can install your own hypervisor and run your own VMs on it.', ''), ('Direct access', 'Per-core/per-socket licences, performance counters and special drivers', 'see the real hardware.')],
    'Bare metal in action', 'No hypervisor between you and the hardware.', 'Bare metal', 'Animation: one physical server dedicated to you; your own hypervisor with your VMs; per-core licences and direct hardware features.', 'c2anim')
T2 = vtype(2, 'Bare-metal servers', 'red',
    'A <b>bare-metal instance</b> gives a customer an entire physical server with no provider hypervisor in between, provisioned through the same cloud APIs as VMs, so the operating system — or the customer’s own hypervisor — runs directly on the hardware.',
    'Renting a whole independent house instead of a flat: nobody else lives there, you can rebuild the inside as you like — and you pay for every room.',
    'TiffinGo does not need bare metal. A bank client that runs a licensed database billed per physical core, or a team that must run its own VMware hypervisor, would use it.',
    'EC2 *.metal instance types (e.g. m7i.metal-24xl), Amazon EC2 Dedicated Hosts (whole host, but VMs still); Azure BareMetal Infrastructure (e.g. SAP HANA) and Azure VMware Solution; Google Compute Engine bare-metal instances (e.g. C3 metal) and Google Cloud VMware Engine.',
    '', A_BM,
    'licences need physical cores, you must run your own hypervisor or need hardware features a VM hides.',
    'a normal VM would do — bare metal is large, slower to start and you lose some VM conveniences.',
    plain='Instead of a slice of a server, you rent the whole physical machine. Nothing else runs on it.',
    how=[('Same API', 'You launch it like any instance (choose a .metal type).'), ('No provider hypervisor', 'The OS boots on the hardware; the Nitro cards still handle network/storage/security.'), ('Full hardware', 'All cores, memory and devices are yours.'), ('Your stack', 'Install your own hypervisor or OS tools if needed.'), ('Billing', 'Per second/hour like a VM, but for the whole machine.')],
    words=[('bare metal', 'a physical server with nothing virtual in between'), ('nested virtualization', 'running VMs inside a VM'), ('per-core licence', 'software priced per physical CPU core')],
    diff=table(['', 'Bare-metal instance', 'Dedicated Host', 'Dedicated Instance'], [['Hypervisor', 'none (yours if you want)', 'provider’s', 'provider’s'], ['Hardware shared?', 'no', 'no — you see sockets/cores', 'no — but not visible to you'], ['Main reason', 'own hypervisor, HW features', 'BYOL licences', 'isolation compliance']], minw=560),
    where=['VMware and other hypervisor workloads', 'Per-core licensed databases', 'Security tools and performance profiling'],
    realworld='AWS introduced bare-metal EC2 instances in 2017–2018; they made <b>VMware Cloud on AWS</b> possible, letting VMware run its own hypervisor on AWS hardware. Today Azure VMware Solution and Google Cloud VMware Engine use the same idea.',
    pro='On AWS, bare metal and VMs run on the <i>same</i> Nitro hardware: because the Nitro cards (not a software hypervisor) handle networking and storage, AWS can sell the very same server either as one .metal instance or as many VMs.')

def a_k8s(k):
    o = t(180, 12, ['Managed control plane', 'Worker nodes you choose', 'Pods scheduled and scaled'][k], 9, 'ink', bold=True)
    o += box(120, 26, 120, 34, 'green', rx=6) + t(180, 41, 'control plane', 7.6, 'ink', bold=True) + t(180, 53, 'run by EKS / AKS / GKE', 6.6, 'ink2')
    if k >= 1:
        for i in range(3):
            o += box(20 + i * 112, 78, 100, 52, 'blue', rx=6) + t(70 + i * 112, 92, f'node {i + 1} (VM)', 7, 'ink', bold=True)
            if k == 2:
                for j in range(2 + (i == 0)): o += box(28 + i * 112 + j * 30, 100, 26, 22, 'violet', rx=3) + t(41 + i * 112 + j * 30, 115, 'pod', 6, 'ink')
            o += arrow(180, 62, 70 + i * 112, 76)
    o += t(180, 148, ['the provider runs and patches the Kubernetes brain', 'you pick node size and count (or let the provider: Autopilot/Fargate)', 'Kubernetes places pods on nodes and adds more when load grows'][k], 7.2, 'ink', bold=True)
    return o
A_K8S = cap([a_k8s(k) for k in range(3)], [('Control plane', 'The provider runs the Kubernetes API server, scheduler and etcd for you.', ''), ('Nodes', 'Worker nodes are VMs in your account (or managed nodes such as GKE', 'Autopilot / EKS on Fargate).'), ('Pods', 'Kubernetes schedules containers (pods) onto nodes, restarts them and', 'scales them; node autoscaling adds VMs.')],
    'Managed Kubernetes in action', 'The provider runs the brain; you run the workloads.', 'Managed Kubernetes', 'Animation: a managed control plane; three worker node VMs; pods scheduled onto the nodes.', 'c3anim')
T3 = vtype(3, 'Managed Kubernetes and container orchestration', 'violet',
    '<b>Managed Kubernetes</b> is a service in which the provider operates the Kubernetes <b>control plane</b> (API server, scheduler, etcd) with an SLA, while the customer’s containerised workloads run on worker nodes — VMs in the customer’s account or provider-managed capacity. Proprietary orchestrators such as Amazon ECS fill the same role.',
    'A food court: the management runs the building, electricity and seating plan (control plane); each stall (pod) is placed where there is space, and new counters are opened when queues grow.',
    'When TiffinGo splits its app into 12 microservices (orders, payments, delivery tracking…), it moves them to a managed Kubernetes cluster so every service is deployed, scaled and restarted the same way.',
    'Amazon EKS and Amazon ECS, Azure Kubernetes Service (AKS), Google Kubernetes Engine (GKE, incl. Autopilot); Red Hat OpenShift on each cloud.',
    '', A_K8S,
    'you run many containerised services, want one consistent platform across clouds, or need Kubernetes features and tools.',
    'you have one or two simple services — serverless containers (type 4) give the same result with far less to learn and operate.',
    plain='A system that runs many containers for you across a group of servers — starting them, restarting them when they crash and adding more when busy. The cloud company runs the system’s “brain”.',
    how=[('Create a cluster', 'The provider creates a highly available control plane.'), ('Add capacity', 'Node groups (VMs) or serverless node options.'), ('Describe the app', 'YAML manifests: Deployment (how many pods), Service (how to reach them).'), ('Schedule', 'The scheduler places pods on nodes with free CPU/memory.'), ('Self-heal and scale', 'Crashed pods restart; HPA adds pods, cluster autoscaler adds nodes.')],
    words=[('container', 'an app packed with everything it needs, sharing the host OS kernel'), ('pod', 'the smallest unit Kubernetes runs — one or more containers'), ('node', 'a machine (usually a VM) that runs pods'), ('control plane', 'the part that decides what runs where')],
    diff=table(['', 'Managed Kubernetes', 'Serverless containers', 'VMs'], [['You manage', 'manifests, nodes (unless Autopilot)', 'only the image and settings', 'OS and everything above'], ['Learning curve', 'high', 'low', 'medium'], ['Portability', 'high (Kubernetes everywhere)', 'medium', 'medium']], minw=540),
    where=['Microservice platforms', 'Hybrid and multi-cloud setups', 'ML and data platforms (Kubeflow, Spark on K8s)'],
    realworld='Kubernetes was open-sourced by Google in 2014, based on its internal Borg system; Google launched the first managed Kubernetes service (now GKE) in 2015, followed by AKS and EKS in 2018.',
    pro='On EKS you pay for the control plane per cluster-hour on top of the nodes — many small clusters cost more than one shared cluster with namespaces. GKE also charges a cluster management fee but gives one zonal or Autopilot cluster per billing account free of that fee.')

def a_sc(k):
    o = t(180, 12, ['Give an image', 'Requests arrive → instances scale', 'Quiet → scale in (or to zero)'][k], 9, 'ink', bold=True)
    o += box(14, 34, 90, 70, 'amber', rx=8) + t(59, 62, 'container', 7.6, 'ink', bold=True) + t(59, 78, 'image', 7.6, 'ink') + arrow(106, 69, 130, 69)
    o += box(132, 30, 214, 84, 'card', rx=8) + t(239, 44, 'platform (Fargate / Container Apps / Cloud Run)', 6.6, 'ink2')
    n = [1, 4, 0][k]
    for i in range(n): o += box(142 + i * 50, 56, 42, 44, 'green', rx=4) + t(163 + i * 50, 82, 'copy', 6.8, 'ink')
    if n == 0: o += t(239, 82, 'no copies running → ₹0 (Cloud Run, Container Apps)', 7, 'ink')
    o += t(180, 140, ['no servers or cluster to set up — just the image and CPU/memory', 'the platform adds copies as requests grow', 'and removes them when traffic drops'][k], 7.2, 'ink', bold=True)
    return o
A_SC = cap([a_sc(k) for k in range(3)], [('Give an image', 'You hand over a container image plus CPU, memory, port and scaling limits.', ''), ('Scale out', 'The platform starts more copies as requests or CPU rise; a load balancer or', 'URL is provided.'), ('Scale in', 'When traffic drops, copies are removed — on Cloud Run and Container Apps', 'even to zero.')],
    'Serverless containers in action', 'Containers without servers or clusters.', 'Serverless containers', 'Animation: a container image handed to the platform; copies added as requests arrive; scaled in to zero when quiet.', 'c4anim')
T4 = vtype(4, 'Serverless containers', 'green',
    '<b>Serverless container</b> services run container images without the customer provisioning or managing servers or cluster nodes: you specify the image, CPU, memory and scaling rules; the provider supplies isolated compute, networking and often an HTTPS endpoint, and bills for the resources the containers use.',
    'Ordering from a cloud kitchen platform: you give the recipe (image); the platform finds kitchen space, cooks as many as are ordered and charges only for the cooking.',
    'TiffinGo’s new “track my tiffin” API is a single container. On Cloud Run or Azure Container Apps it gets an HTTPS URL, scales with lunch-time traffic and drops to zero at night; on AWS the same container runs on ECS with Fargate (ECS Express Mode creates the load balancer and scaling for you).',
    'AWS Fargate (with ECS or EKS), Amazon ECS Express Mode; Azure Container Apps, Azure Container Instances; Google Cloud Run.',
    '', A_SC,
    'you have a containerised web app, API or worker and want no servers, simple scaling and a quick start.',
    'you need special hardware, privileged access to the host or very long-running steady workloads where VMs with Savings Plans are cheaper.',
    plain='You give the cloud a packed app (a container). It runs it, gives you a web address and adds or removes copies with traffic. No servers to look after.',
    how=[('Push an image', 'To a registry: Amazon ECR, Azure Container Registry, Artifact Registry (public images work too).'), ('Define the service', 'CPU, memory, port, environment variables, min/max instances.'), ('Platform runs it', 'Each task/instance gets isolated compute (Fargate uses Firecracker micro-VMs).'), ('Traffic', 'A managed endpoint or load balancer routes requests to healthy copies.'), ('Scale', 'Based on requests, CPU or queue length; to zero where supported.')],
    words=[('container image', 'a packaged app ready to run'), ('registry', 'an online store of container images'), ('task / revision', 'one running version of your container service'), ('scale to zero', 'no copies running when there is no traffic')],
    diff=table(['', 'Serverless containers', 'Functions', 'Managed Kubernetes'], [['Unit', 'container image', 'function code', 'pods on nodes'], ['Max run time', 'long (a service)', 'limited (Lambda 15 min)', 'unlimited'], ['Scale to zero', 'Cloud Run, Container Apps: yes; Fargate services: no', 'yes', 'no (nodes stay)']], minw=560),
    where=['Web APIs and microservices', 'Background workers', 'Internal tools and prototypes'],
    realworld='AWS stopped accepting new customers for <b>AWS App Runner</b> from 30 April 2026 and recommends <b>Amazon ECS Express Mode</b> — one command or click that creates the ECS service on Fargate, an internet-facing load balancer, auto scaling and an HTTPS URL.',
    pro='Cloud Run lets one instance handle many requests at once (concurrency, default 80) while Lambda handles one request per execution environment — so the same traffic can need far fewer Cloud Run instances, and costs behave differently.')

def a_fn(k):
    o = t(180, 12, ['An event arrives', 'A copy of the function runs', 'Many events → many copies'][k], 9, 'ink', bold=True)
    o += box(14, 40, 90, 60, 'amber', rx=8) + t(59, 66, 'photo', 7.6, 'ink', bold=True) + t(59, 82, 'uploaded', 7.4, 'ink')
    o += arrow(106, 70, 136, 70) + t(120, 62, 'event', 6.6, 'ink2')
    n = [0, 1, 5][k]
    o += box(140, 30, 206, 84, 'card', rx=8) + t(243, 44, 'resize function', 7.2, 'ink2')
    for i in range(n): o += box(150 + i * 38, 58, 32, 40, 'green', rx=4) + t(166 + i * 38, 82, 'λ', 9, 'ink', bold=True)
    if n == 0: o += t(243, 80, 'nothing running, nothing billed', 7.4, 'ink')
    o += t(180, 138, ['S3 / Blob / Cloud Storage emits an “object created” event', 'runs ~2 s, writes the thumbnail, billed per ms', 'the platform runs copies in parallel, then removes them'][k], 7.2, 'ink', bold=True)
    return o
A_FN = cap([a_fn(k) for k in range(3)], [('Event', 'Something happens — an upload, an HTTP request, a schedule, a queue message.', ''), ('Run', 'The platform starts (or reuses) an execution environment and calls your', 'function; billing is per request and per millisecond.'), ('Scale', 'Many events at once → many copies in parallel, up to your concurrency limit;', 'idle → zero.')],
    'Functions in action', 'Code that runs only when something happens.', 'Functions', 'Animation: a photo upload triggers an event; one function copy runs; many uploads run many copies in parallel.', 'c5anim')
T5 = vtype(5, 'Functions (Function as a Service)', 'green',
    '<b>Function as a Service (FaaS)</b> runs small pieces of code in response to <b>events</b> — HTTP requests, file uploads, queue messages, schedules — on fully managed, automatically scaled infrastructure, billed per invocation and execution time, with no cost when idle.',
    'A doorbell: nothing happens until someone presses it; each press rings once; ten visitors at once get ten rings.',
    'Every time a customer uploads a tiffin photo, a function makes three thumbnail sizes in about 2 seconds. TiffinGo pays for those seconds only — not for a server waiting all day.',
    'AWS Lambda, Azure Functions, Google Cloud Run functions (formerly Cloud Functions).',
    'The internals (micro-VMs, cold starts) were covered in Lesson 4.5.', A_FN,
    'work is short, event-driven and bursty — glue between services, file processing, webhooks, scheduled tasks.',
    'jobs run for long (Lambda max 15 minutes), need steady high throughput (often cheaper on containers/VMs) or very low latency on every call (cold starts).',
    plain='You write only a small piece of code and say “run this when X happens”. The cloud runs it, as many times as needed, and charges per run.',
    how=[('Upload code', 'A zip or container image plus a handler name and runtime (Python, Node.js, Java…).'), ('Connect a trigger', 'HTTP endpoint, storage event, queue, schedule.'), ('Invoke', 'The platform starts an execution environment (cold start) or reuses a warm one.'), ('Run and bill', 'Charged per request + GB-seconds (memory × time), per millisecond on Lambda.'), ('Scale', 'Parallel copies per event, up to a concurrency limit; idle → zero.')],
    words=[('event', 'a signal that something happened'), ('trigger', 'the rule that connects an event to a function'), ('cold start', 'extra delay when a new copy must start'), ('GB-second', 'memory size × run time, the billing unit')],
    diff=table(['', 'Functions', 'Serverless containers', 'PaaS'], [['You deploy', 'a function', 'a container image', 'an app (code)'], ['Billing', 'per request + ms', 'per vCPU/memory-second', 'per plan / instance'], ['Best at', 'events, glue', 'APIs, web services', 'whole web apps']], minw=520),
    where=['Image/video processing on upload', 'Webhooks and chatbots', 'Scheduled jobs and automation'],
    realworld='AWS Lambda launched in November 2014 and started the “serverless” category; it bills in 1-millisecond increments (since December 2020) and runs each execution environment in a Firecracker micro-VM.',
    pro='Lambda’s free tier (1 million requests and 400,000 GB-seconds a month) is an <b>always-free</b> offer — it did not change with the July 2025 Free Tier update, so small event-driven apps can run for ₹0 indefinitely.')

def a_paas(k):
    o = t(180, 12, ['Push your code', 'Platform builds and runs it', 'Deploy a new version safely'][k], 9, 'ink', bold=True)
    o += box(14, 40, 80, 60, 'violet', rx=8) + t(54, 66, 'app code', 7.6, 'ink', bold=True) + t(54, 82, 'git / zip', 7, 'ink2') + arrow(96, 70, 120, 70)
    o += box(122, 28, 224, 92, 'card', rx=8) + t(234, 42, 'App Service / Beanstalk / App Engine', 6.8, 'ink2')
    if k >= 1:
        o += box(132, 50, 60, 24, 'green', rx=4) + t(162, 66, 'runtime', 6.8, 'ink') + box(200, 50, 60, 24, 'green', rx=4) + t(230, 66, 'LB + TLS', 6.8, 'ink') + box(268, 50, 70, 24, 'green', rx=4) + t(303, 66, 'scaling', 6.8, 'ink')
    if k == 2:
        o += box(132, 84, 96, 26, 'blue', rx=4) + t(180, 101, 'v1 (production)', 6.8, 'ink') + box(238, 84, 100, 26, 'amber', rx=4) + t(288, 101, 'v2 (staging slot)', 6.8, 'ink')
    o += t(180, 142, ['no OS, no web server setup', 'runtime, load balancer, HTTPS, scaling and patching are managed', 'test v2 in a slot, then swap — roll back by swapping again'][k], 7.2, 'ink', bold=True)
    return o
A_PAAS = cap([a_paas(k) for k in range(3)], [('Push code', 'Deploy source code or a package with a git push, zip upload or pipeline.', ''), ('Platform runs it', 'The platform provides the language runtime, web server, load balancer, HTTPS', 'certificate and scaling.'), ('Release safely', 'New versions go to a staging slot/version; swap or split traffic, and roll', 'back the same way.')],
    'App platform in action', 'Push code, get a running web app.', 'PaaS', 'Animation: code pushed to the platform; runtime, load balancer and scaling provided; a new version tested in a staging slot then swapped.', 'c6anim')
T6 = vtype(6, 'App platforms (PaaS)', 'violet',
    'An <b>application platform (PaaS)</b> runs web applications and APIs from source code or packages: the provider manages the operating system, language runtime, web server, load balancing, scaling and patching, while the customer manages the application code, its configuration and data.',
    'A tiffin-service kitchen you rent by the hour with stoves, gas and cleaning included: you bring only your recipe and ingredients.',
    'TiffinGo’s menu website (Python/Flask) runs on Azure App Service: the team pushes code from GitHub, a staging slot shows the new festival menu, and they swap it live at 6 a.m. on Diwali.',
    'AWS Elastic Beanstalk, Azure App Service, Google App Engine; also Heroku and similar platforms.',
    '', A_PAAS,
    'you build a standard web app or API and want to spend time on code, not servers.',
    'you need unusual OS-level software or fine control of the runtime — then containers or VMs fit better.',
    plain='You hand over your website’s code; the platform sets up and runs everything needed to put it online and keeps it updated.',
    how=[('Choose a runtime', 'Python, Node.js, Java, .NET, PHP… (or a container).'), ('Deploy', 'From git, zip, or CI/CD; the platform builds it.'), ('Provision', 'Instances, load balancer, HTTPS certificate, health checks.'), ('Operate', 'Auto scaling rules, logs, OS and runtime patching by the provider.'), ('Release', 'Slots / versions / environments for blue-green deployments.')],
    words=[('runtime', 'the language engine your code needs, e.g. Python 3.12'), ('deployment slot', 'a second copy of the app for testing before going live'), ('blue-green', 'two versions side by side; switch traffic between them')],
    diff=table(['', 'PaaS', 'Serverless containers', 'VM'], [['You provide', 'source code', 'container image', 'whole server setup'], ['OS patching', 'provider', 'provider', 'you'], ['Typical unit', 'web app', 'service', 'server']], minw=480),
    where=['Company websites and portals', 'REST APIs and back-ends for mobile apps', 'Student and start-up projects'],
    realworld='Google App Engine (2008) was one of the first PaaS products; Azure App Service hosts web apps in many languages with deployment slots, and AWS Elastic Beanstalk creates EC2, load balancer and Auto Scaling resources in your own account to run uploaded code.',
    pro='Elastic Beanstalk is “PaaS you can see”: every resource it creates (EC2, ALB, ASG) is visible and billed in your account — you can SSH into its instances. Azure App Service and App Engine standard keep the underlying VMs hidden.')

def a_batch(k):
    o = t(180, 12, ['Jobs wait in a queue', 'Compute grows for the jobs', 'Done → back to zero'][k], 9, 'ink', bold=True)
    o += box(14, 32, 90, 90, 'amber', rx=8) + t(59, 48, 'job queue', 7.4, 'ink', bold=True)
    for i in range([5, 2, 0][k]): o += box(24, 56 + i * 12, 70, 9, 'card', rx=2)
    o += arrow(106, 76, 130, 76)
    o += box(132, 32, 214, 90, 'card', rx=8) + t(239, 46, 'compute environment (Spot / GPU VMs)', 6.8, 'ink2')
    n = [0, 6, 0][k]
    for i in range(n): o += box(140 + (i % 3) * 66, 56 + (i // 3) * 32, 60, 26, 'green' if i < 4 else 'red', rx=4) + t(170 + (i % 3) * 66, 73 + (i // 3) * 32, 'Spot VM' if i < 4 else 'GPU VM', 6.6, 'ink')
    if n == 0: o += t(239, 84, ['nothing running yet', '', 'scaled to zero — results in storage'][k], 7.2, 'ink')
    o += t(180, 144, ['submit thousands of jobs; the service schedules them', 'it launches the right VMs (often Spot, GPUs if asked)', 'and terminates them when the queue is empty'][k], 7.2, 'ink', bold=True)
    return o
A_BATCH = cap([a_batch(k) for k in range(3)], [('Queue', 'You submit jobs (a container + command) to a queue.', ''), ('Scale out', 'The service launches VMs that fit the jobs — CPU, memory, GPUs — often on', 'Spot to save money.'), ('Scale in', 'When jobs finish and the queue is empty, the VMs are terminated.', '')],
    'Batch and accelerated compute in action', 'Big jobs on temporary fleets.', 'Batch / GPU', 'Animation: jobs waiting in a queue; a compute environment of Spot and GPU VMs grows to run them; it scales back to zero.', 'c7anim')
T7 = vtype(7, 'Batch, HPC and accelerated (GPU) compute', 'amber',
    '<b>Batch computing</b> services schedule large numbers of jobs onto automatically provisioned compute and release it when done; <b>accelerated computing</b> instances add GPUs or other accelerators (e.g. AWS Trainium/Inferentia, Google TPUs) for parallel maths such as ML training, inference, rendering and simulation.',
    'A wedding caterer hiring extra cooks and big kadhais only for the wedding week, then sending them home.',
    'TiffinGo’s nightly sales report and its weekly “dishes you may like” model training run as batch jobs: the report on Spot CPU instances, the training on one GPU instance for 2 hours — then everything scales back to zero.',
    'AWS Batch, AWS ParallelCluster, EC2 P/G (NVIDIA GPU), Trn/Inf (AWS chips); Azure Batch, Azure CycleCloud, NC/ND-series GPU VMs; Google Cloud Batch, A3/G2 GPU VMs, Cloud TPU.',
    '', A_BATCH,
    'you have large, parallel or periodic jobs, or work that needs GPUs only some of the time.',
    'the work is interactive or tiny — or GPUs sit idle (they are among the most expensive instances).',
    plain='For very big jobs, the cloud quickly lends you many machines — or machines with powerful graphics chips (GPUs) for AI — and takes them back when the job is finished.',
    how=[('Define a job', 'A container image + command + CPU/memory/GPU needs.'), ('Queue', 'Jobs wait with priorities and dependencies.'), ('Provision', 'The service starts suitable instances (On-Demand or Spot, with GPUs if requested).'), ('Run in parallel', 'Array jobs split work into thousands of pieces; HPC uses fast networks (EFA, InfiniBand).'), ('Release', 'Instances terminate when the queue is empty; results land in storage.')],
    words=[('batch job', 'work that runs without a user waiting, e.g. overnight'), ('GPU', 'a chip with thousands of small cores for parallel maths'), ('HPC', 'high-performance computing — many machines working on one problem'), ('array job', 'one job split into many similar pieces')],
    diff=table(['', 'Batch service', 'Auto Scaling group', 'Functions'], [['Scales on', 'queue length', 'CPU/requests', 'events'], ['Job length', 'minutes to days', 'service (always on)', 'up to 15 min (Lambda)'], ['GPUs', 'yes', 'yes', 'no (Lambda)']], minw=520),
    where=['Nightly ETL and reports', 'ML training and inference', 'Genomics, rendering, engineering simulations'],
    realworld='GPU capacity is so scarce for AI training that providers sell it by reservation: <b>EC2 Capacity Blocks for ML</b> let customers reserve GPU instances for a future date and duration, similar to booking a hall for an event.',
    pro='Batch and GPU work are where Spot and commitments interact: training that checkpoints can run on Spot GPUs at a large discount, while production inference usually needs reserved or On-Demand capacity — mixing both is standard practice.')

SUMMARY = table(['#', 'Compute', 'You manage', 'Billing unit', 'Scales to zero?', 'TiffinGo uses it for'], [
    ['1', 'Virtual machines', 'OS and up', 'per second/hour', 'no', 'order API'], ['2', 'Bare metal', 'everything above hardware', 'per hour (whole server)', 'no', '— (bank client case)'],
    ['3', 'Managed Kubernetes', 'manifests, often nodes', 'nodes + cluster fee', 'no', 'future microservices'], ['4', 'Serverless containers', 'image + settings', 'vCPU/memory-seconds', 'Cloud Run, Container Apps', 'tracking API'],
    ['5', 'Functions', 'function code', 'requests + GB-seconds', 'yes', 'photo resizing'], ['6', 'App platforms', 'app code', 'plan/instances', 'some tiers', 'menu website'], ['7', 'Batch & GPU', 'job definitions', 'instances while jobs run', 'yes', 'reports, ML training']], minw=700)
CHECK = ('  <h3>Check yourself: which compute fits?</h3>\n' +
    qx('A. Send a WhatsApp message whenever an order is marked “delivered”.', ['VM', 'Function', 'Bare metal', 'Kubernetes'], 1, 'Short, event-driven.') +
    qx('B. Move 40 VMware VMs to the cloud without changing the hypervisor.', ['Functions', 'VMware on bare metal (e.g. Azure VMware Solution)', 'PaaS', 'Cloud Run'], 1, 'Needs own hypervisor → bare metal-based VMware services.') +
    qx('C. A single containerised API, small team, spiky traffic.', ['Serverless containers', 'Bare metal', 'Self-managed Kubernetes', 'Mainframe'], 0, 'Least to operate, scales automatically.') +
    qx('D. Train an image-recognition model once a week.', ['Function', 'Batch job on a GPU instance', 'PaaS', 'Free tier VM'], 1, 'Temporary GPU capacity.'))

TYPES = ('  <p>Seven kinds of compute, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['Why is a 2-vCPU Graviton instance not the same as a 2-vCPU Intel one?', 'Why can one Cloud Run instance replace many Lambda environments for the same traffic?', 'Which AWS container service stopped taking new customers in 2026, and what replaced it?'], 'types 1, 4 and 4') + MAP
         + jump(['VMs', 'Bare metal', 'Kubernetes', 'Serverless containers', 'Functions', 'PaaS', 'Batch & GPU']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY + '\n' + CHECK)

# ------------------------------------------------------------------ parts: instance naming
def namefig():
    o = t(320, 16, 'Reading instance names in three clouds', 11, 'ink', bold=True)
    rows = [('AWS', [('m', 'family: general purpose'), ('7', 'generation'), ('i', 'Intel CPU (g = Graviton, a = AMD)'), ('.large', 'size: 2 vCPU · 8 GiB')], 'm7i.large'),
            ('Azure', [('D', 'family: general purpose'), ('2', '2 vCPUs'), ('s', 'premium SSD capable'), ('_v5', 'version 5')], 'Standard_D2s_v5'),
            ('Google', [('e2', 'series (cost-optimised)'), ('-standard', 'type: 4 GB per vCPU'), ('-2', '2 vCPUs'), ('', '')], 'e2-standard-2')]
    for i, (cl, parts, full) in enumerate(rows):
        y = 34 + i * 70
        o += t(40, y + 30, cl, 9, 'ink', bold=True) + box(76, y, 140, 50, 'blue', rx=6) + t(146, y + 30, full, 9.5, 'ink', bold=True, mono=True)
        for j, (p, d) in enumerate(parts):
            if not p: continue
            x = 232 + j * 100
            o += box(x, y, 94, 50, 'card', rx=6) + t(x + 47, y + 20, p, 9, 'ink', bold=True, mono=True) + t(x + 47, y + 38, d, 5.9, 'ink2')
    o += t(320, 252, 'Families: general purpose (M, D, E2/N2), compute optimised (C, F, C3), memory optimised (R, E, M3), storage (I, L), accelerated (P, G, NC/ND, A3).', 7, 'ink2')
    return o
NAMES = bigfig('Instance name anatomy: AWS m7i.large = family m, generation 7, Intel, size large; Azure Standard_D2s_v5 = family D, 2 vCPUs, premium storage, version 5; Google e2-standard-2 = series e2, standard type, 2 vCPUs.', namefig(), h=262)

parts = (NAMES + wwu([
    ('Image (AMI / VM image)', 'The OS disk template the server starts from.', 'Every new server starts identical; golden images bake in your software.', 'AMIs, Azure Compute Gallery, GCE images.'),
    ('Instance type / VM size', 'vCPU, memory, network and disk limits as one package.', 'Right-sizing is the biggest compute saving.', 'm7i.large · Standard_D2s_v5 · e2-standard-2.'),
    ('Key pair / SSH key', 'Public key on the server, private key with you.', 'Password-less, safer login.', 'EC2 key pairs, Azure SSH keys, OS Login (GCP).'),
    ('User data / custom data / startup script', 'A script that runs at first boot.', 'Automates installation — no manual setup.', 'cloud-init on Linux in all three clouds.'),
    ('Instance metadata', 'A local endpoint (169.254.169.254) describing the instance.', 'Apps get their ID, Region and temporary credentials.', 'IMDSv2 on AWS (Lesson 4.6), Azure IMDS, GCE metadata server.'),
    ('Groups of instances', 'Templates + scaling groups.', 'Self-healing and elastic fleets (Lesson 5.3).', 'Auto Scaling groups, VM Scale Sets, managed instance groups.')]))

DEEP = ('  <h3>Instance families: picking the right shape</h3>\n' + table(['Need', 'AWS', 'Azure', 'Google Cloud'], [
    ['Balanced web/app', 'M (m7i, m7g)', 'D-series', 'E2, N2, N4, C4'], ['CPU-heavy (encoding, gaming servers)', 'C (c7i, c7g)', 'F-series', 'C3, C4, H3'], ['Memory-heavy (in-memory DB, caches)', 'R, X', 'E, M-series', 'M3, X4'],
    ['Small, bursty', 'T (t3, t4g) — CPU credits', 'B-series — CPU credits', 'E2 shared-core (e2-micro/small)'], ['Local fast disks', 'I (i4i)', 'L-series', 'Z3'], ['GPU / AI', 'P, G, Trn, Inf', 'NC, ND, NV', 'A3, G2, TPU']], minw=600) +
    '\n  <h3>Burstable instances: CPU credits</h3>\n  <p>T-family (AWS), B-series (Azure) and E2 shared-core (Google) give a <b>baseline</b> CPU share and let you burst above it using accumulated <b>credits</b>. Perfect for mostly idle servers; a busy server on a burstable type either slows to the baseline or (AWS “unlimited” mode) pays extra.</p>\n'
    '  <h3>Graviton, Cobalt, Axion: ARM in the cloud</h3>\n  <p>All three providers now design their own ARM server chips — AWS <b>Graviton</b>, Microsoft <b>Azure Cobalt</b>, Google <b>Axion</b> — offering better price-performance for many Linux workloads. Interpreted languages (Python, Node.js, Java) usually run unchanged; compiled code and containers need ARM builds.</p>\n'
    '  <h3>Quotas: why “Launch” can fail on a new account</h3>\n  <p>Each Region has <b>service quotas</b> (e.g. a vCPU limit for On-Demand instances, GPU limits often zero on new accounts). Errors like <code>VcpuLimitExceeded</code> (AWS), <code>QuotaExceeded</code> (Azure) or <code>QUOTA_EXCEEDED</code> (Google) mean: request an increase in Service Quotas / Quotas pages.</p>')

clouds = vendor_tabs('<p><b>AWS:</b> EC2 (VMs, bare metal, Dedicated Hosts, Spot), Lightsail (simple VPS), Auto Scaling, ECS/EKS, Fargate, ECS Express Mode, Lambda, Elastic Beanstalk, AWS Batch, ParallelCluster, Outposts (on-premises).</p>',
    '<p><b>Azure:</b> Virtual Machines, VM Scale Sets, Dedicated Host, Azure VMware Solution, AKS, Container Apps, Container Instances, Functions, App Service, Azure Batch, CycleCloud, Azure Local (on-premises).</p>',
    '<p><b>Google Cloud:</b> Compute Engine (VMs, bare metal, sole-tenant nodes, Spot VMs), managed instance groups, GKE (Standard/Autopilot), Cloud Run, Cloud Run functions, App Engine, Cloud Batch, Cloud TPU, Google Distributed Cloud (on-premises).</p>') + \
    cloud3([['Virtual machines', 'EC2', 'Virtual Machines', 'Compute Engine'], ['Scaling group', 'Auto Scaling group', 'VM Scale Sets', 'Managed instance group'], ['Managed Kubernetes', 'EKS', 'AKS', 'GKE'], ['Serverless containers', 'Fargate (ECS Express Mode)', 'Container Apps', 'Cloud Run'],
            ['Functions', 'Lambda', 'Azure Functions', 'Cloud Run functions'], ['App platform', 'Elastic Beanstalk', 'App Service', 'App Engine'], ['Batch', 'AWS Batch', 'Azure Batch', 'Cloud Batch'], ['Simple VPS', 'Lightsail', '—', '—']])

# ------------------------------------------------------------------ practical (own account)
WEB_AL = '#!/bin/bash\ndnf install -y nginx\necho "<h1>TiffinGo menu — served from $(hostname)</h1>" > /usr/share/nginx/html/index.html\nsystemctl enable --now nginx'
WEB_DEB = '#!/bin/bash\napt-get update && apt-get install -y nginx\necho "<h1>TiffinGo menu — served from $(hostname)</h1>" > /var/www/html/index.html\nsystemctl enable --now nginx'
# console sketches for steps 1–4 (consumed in order by tri())
MOCKQ.extend([
 (mock('aws', ['EC2', 'Instances', 'Launch an instance'], ['Dashboard', 'Instances', 'Launch templates', 'AMIs', 'Volumes', 'Security Groups', 'Key Pairs'], 'Instances',
       [('Name and tags · Name', 'tiffingo-vm'), ('Application and OS Images (AMI)', '▾ Amazon Linux 2023 AMI — Free tier eligible'), ('Instance type', '▾ t3.micro — 2 vCPU · 1 GiB'), ('Key pair (login)', '▾ Proceed without a key pair'),
        ('Network settings', '[x] Allow HTTP traffic from the internet'), ('Advanced details · User data', '#!/bin/bash  dnf install -y nginx …')], 'Launch instance'),
  mock('az', ['Home', 'Virtual machines', 'Create a virtual machine'], ['Basics', 'Disks', 'Networking', 'Management', 'Monitoring', 'Advanced', 'Tags', 'Review + create'], 'Basics',
       [('Resource group', '▾ (New) rg-tiffingo'), ('Virtual machine name', 'tiffingo-vm'), ('Region', '▾ (Asia Pacific) Central India'), ('Image', '▾ Ubuntu Server 24.04 LTS - x64 Gen2'), ('Size', '▾ Standard_B1s - 1 vcpu, 1 GiB memory'),
        ('Select inbound ports', '▾ HTTP (80), SSH (22)')], 'Review + create'),
  mock('gcp', ['Compute Engine', 'VM instances', 'Create an instance'], ['Machine configuration', 'OS and storage', 'Data protection', 'Networking', 'Observability', 'Security', 'Advanced'], 'Machine configuration',
       [('Name', 'tiffingo-vm'), ('Region', '▾ asia-south1 (Mumbai)'), ('Zone', '▾ asia-south1-a'), ('Machine type', '▾ e2-micro (2 vCPU, 1 core, 1 GB memory)'), ('Networking · Firewall', '[x] Allow HTTP traffic'), ('Advanced · Startup script', '#!/bin/bash  apt-get install -y nginx …')], 'Create')),
 (mock('aws', ['EC2', 'Instances', 'i-0abc… (tiffingo-vm)'], ['Instances', 'Details', 'Status and alarms', 'Monitoring', 'Security', 'Networking', 'Storage'], 'Details',
       [('Instance state', 'Running'), ('Instance type', 't3.micro'), ('Availability Zone', 'ap-south-1a'), ('Public IPv4 address', '13.233.x.x')], 'Connect'),
  mock('az', ['Home', 'Virtual machines', 'tiffingo-vm', 'Run command'], ['Overview', 'Connect', 'Networking', 'Disks', 'Size', 'Run command', 'Metrics'], 'Run command',
       [('Command', '▾ RunShellScript'), ('Linux Shell Script', 'systemctl is-active nginx; nproc; free -m')], 'Run'),
  mock('gcp', ['Compute Engine', 'VM instances'], ['VM instances', 'Instance templates', 'Instance groups', 'Disks', 'Snapshots', 'Images'], 'VM instances',
       [('tiffingo-vm · asia-south1-a', 'Status: Running · External IP 34.x.x.x'), ('Connect', '▾ SSH — Open in browser window')], 'SSH')),
 (mock('aws', ['EC2', 'Instances', 'Change instance type'], ['Instances', 'Instance state', 'Actions', 'Instance settings'], 'Instance settings',
       [('Current instance type', 't3.micro'), ('New instance type', '▾ t3.small — 2 vCPU · 2 GiB')], 'Apply'),
  mock('az', ['Home', 'Virtual machines', 'tiffingo-vm', 'Size'], ['Overview', 'Availability + scale', 'Size', 'Disks', 'Networking'], 'Size',
       [('Current size', 'Standard_B1s'), ('Select a size', '▾ B2s — 2 vCPUs, 4 GiB')], 'Resize'),
  mock('gcp', ['Compute Engine', 'VM instances', 'tiffingo-vm', 'Edit'], ['Details', 'Edit', 'Machine configuration', 'Networking'], 'Machine configuration',
       [('Machine type', '▾ e2-small (2 vCPU, 1 core, 2 GB memory)'), ('Note', 'Stop the VM before changing the machine type')], 'Save')),
 (mock('aws', ['Amazon Elastic Container Service', 'Express mode'], ['Clusters', 'Namespaces', 'Task definitions', 'Express mode', 'Account settings'], 'Express mode',
       [('Image URI', 'public.ecr.aws/nginx/nginx:latest'), ('Task execution role', '▾ Create new role'), ('Infrastructure role', '▾ Create new role')], 'Create'),
  mock('az', ['Home', 'Container Apps', 'Create Container App'], ['Basics', 'Container', 'Bindings', 'Ingress', 'Tags', 'Review + create'], 'Container',
       [('Container app name', 'tiffingo-hello'), ('Region', '▾ Central India'), ('Use quickstart image', '[x] Simple hello world container'), ('Ingress · Accepting traffic from', '▾ Anywhere, target port 80')], 'Review + create'),
  mock('gcp', ['Cloud Run', 'Deploy container', 'Service'], ['Services', 'Jobs', 'Worker pools', 'Domain mappings'], 'Services',
       [('Container image URL', 'us-docker.pkg.dev/cloudrun/container/hello'), ('Service name', 'tiffingo-hello'), ('Region', '▾ asia-south1 (Mumbai)'), ('Authentication', '[x] Allow public access')], 'Create')),
])

STEP1 = ('1 · Launch a Linux VM that serves a web page', tri(
    (['[[EC2]] → [[Instances]] → [[Launch instances]]. Name: <code>tiffingo-vm</code>.', 'Image: [[Amazon Linux 2023 AMI]]. Instance type: [[t3.micro]] (free-tier eligible).', 'Key pair: [[Proceed without a key pair]] (we will use the browser connect) — or create one if you want SSH from your laptop.',
      'Network settings → [[Edit]]: keep the default VPC; [[Allow SSH traffic from]] Anywhere (lab only), tick [[Allow HTTP traffic from the internet]].', '[[Advanced details]] → [[User data]]: paste the script on the right (the part between the EOF lines) → [[Launch instance]].'],
     f"cat > web.sh <<'EOF'\n{WEB_AL}\nEOF\nSG=$(aws ec2 create-security-group --group-name tiffingo-web --description \"TiffinGo lab web\" --query GroupId --output text)\naws ec2 authorize-security-group-ingress --group-id $SG --protocol tcp --port 80 --cidr 0.0.0.0/0\nID=$(aws ec2 run-instances --instance-type t3.micro --security-group-ids $SG \\\n  --image-id resolve:ssm:/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \\\n  --user-data file://web.sh \\\n  --tag-specifications 'ResourceType=instance,Tags=[{{Key=Name,Value=tiffingo-vm}}]' \\\n  --query 'Instances[0].InstanceId' --output text)\naws ec2 wait instance-running --instance-ids $ID\nIP=$(aws ec2 describe-instances --instance-ids $ID --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)\nsleep 60; curl http://$IP",
     'state <b>Running</b>, status checks <b>2/2 passed</b>, and <code>&lt;h1&gt;TiffinGo menu — served from ip-172-31-…&lt;/h1&gt;</code> from curl or in the browser at <code>http://PUBLIC-IP</code>. If the page does not load, wait a minute — user data is still installing nginx.'),
    (['[[Virtual machines]] → [[Create]] → [[Azure virtual machine]].', 'Resource group: [[Create new]] <code>rg-tiffingo</code>; name <code>tiffingo-vm</code>; Region [[(Asia Pacific) Central India]]; image [[Ubuntu Server 24.04 LTS]]; size [[Standard_B1s]].',
      'Authentication: [[SSH public key]], username <code>azureuser</code>, [[Generate new key pair]]. Inbound ports: tick [[HTTP (80)]] and [[SSH (22)]].', '[[Advanced]] tab → [[Custom data]]: paste the Ubuntu script (between the EOF lines) → [[Review + create]] → [[Create]] → download the private key when asked.'],
     f"cat > web.sh <<'EOF'\n{WEB_DEB}\nEOF\naz group create --name rg-tiffingo --location centralindia\naz vm create --resource-group rg-tiffingo --name tiffingo-vm --image Ubuntu2404 \\\n  --size Standard_B1s --admin-username azureuser --generate-ssh-keys --custom-data web.sh\naz vm open-port --resource-group rg-tiffingo --name tiffingo-vm --port 80\nIP=$(az vm show --show-details --resource-group rg-tiffingo --name tiffingo-vm --query publicIps --output tsv)\nsleep 60; curl http://$IP",
     'JSON output with <code>\"powerState\": \"VM running\"</code> and a <code>publicIpAddress</code>, then the TiffinGo heading from curl. If the B1s size is not offered in Central India for your subscription, pick another small size such as Standard_B2ats_v2.'),
    (['[[Compute Engine]] → [[VM instances]] → [[Create instance]] (enable the Compute Engine API if asked).', 'Name <code>tiffingo-vm</code>; Region [[asia-south1 (Mumbai)]], zone [[asia-south1-a]]; machine type [[e2-micro]].', '[[OS and storage]]: Debian 12. [[Networking]]: tick [[Allow HTTP traffic]].',
      '[[Advanced]] → [[Automation]] → [[Startup script]]: paste the Debian script (between the EOF lines) → [[Create]].'],
     f"cat > web.sh <<'EOF'\n{WEB_DEB}\nEOF\ngcloud compute instances create tiffingo-vm --zone=asia-south1-a --machine-type=e2-micro \\\n  --image-family=debian-12 --image-project=debian-cloud --tags=http-server \\\n  --metadata-from-file=startup-script=web.sh\ngcloud compute firewall-rules create allow-http --allow=tcp:80 --target-tags=http-server\nIP=$(gcloud compute instances describe tiffingo-vm --zone=asia-south1-a --format='get(networkInterfaces[0].accessConfigs[0].natIP)')\nsleep 60; curl http://$IP",
     'a table row with STATUS <b>RUNNING</b> and an EXTERNAL_IP, then the TiffinGo heading. Note: Google’s always-free e2-micro applies only in some US Regions; in Mumbai it uses your trial credit (a few rupees a day).')),
    'User data / custom data / startup script runs once at first boot through cloud-init (Google uses its guest agent) — that is how fleets of identical servers are built without logging in.')

STEP2 = ('2 · Look inside the running VM', tri(
    (['Select the instance → [[Connect]] → [[EC2 Instance Connect]] → [[Connect]] — a terminal opens in the browser.', 'Run <code>curl -s http://169.254.169.254/latest/meta-data/instance-type -H "X-aws-ec2-metadata-token: $(curl -s -X PUT http://169.254.169.254/latest/api/token -H \'X-aws-ec2-metadata-token-ttl-seconds: 60\')"</code> → prints the type from the metadata service.', '[[Monitoring]] tab: CPU utilization graph; [[Actions]] → [[Monitor and troubleshoot]] → [[Get system log]] shows the boot log.'],
     "aws ec2 describe-instances --instance-ids $ID \\\n  --query 'Reservations[0].Instances[0].[InstanceType,Placement.AvailabilityZone,State.Name,PrivateIpAddress]' --output table\naws ec2 get-console-output --instance-id $ID --latest --output text | tail -20     # boot log",
     'type <code>t3.micro</code>, an AZ such as <code>ap-south-1a</code>, state running; the boot log ends with cloud-init “finished” lines.'),
    (['Open the VM → [[Operations]] → [[Run command]] → [[RunShellScript]] → enter <code>systemctl is-active nginx; nproc; free -m</code> → [[Run]].', 'Or [[Connect]] → [[SSH]] using the downloaded key: <code>ssh -i key.pem azureuser@PUBLIC-IP</code>.', '[[Monitoring]] → [[Metrics]] → Percentage CPU.'],
     'az vm run-command invoke --resource-group rg-tiffingo --name tiffingo-vm --command-id RunShellScript \\\n  --scripts "systemctl is-active nginx; nproc; free -m"\naz vm get-instance-view --resource-group rg-tiffingo --name tiffingo-vm \\\n  --query "instanceView.statuses[].displayStatus" --output tsv',
     '<code>active</code>, <code>1</code> vCPU and about 900 MB memory for B1s; “Provisioning succeeded” and “VM running”.'),
    (['In [[VM instances]] click [[SSH]] next to the VM — a browser terminal opens.', 'Run <code>curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/machine-type</code>.', 'Open the VM → [[Observability]] tab for CPU and network graphs; [[Serial port 1 (console)]] shows the boot log.'],
     'gcloud compute ssh tiffingo-vm --zone=asia-south1-a --command="systemctl is-active nginx; nproc; free -m"\ngcloud compute instances get-serial-port-output tiffingo-vm --zone=asia-south1-a | tail -20',
     '<code>active</code>, <code>2</code> vCPUs (e2-micro has 2 shared vCPUs) and about 1 GB memory; startup-script lines in the serial log.')),
    'Every cloud gives a VM a local metadata service at 169.254.169.254 — that is where the instance learns its own type, zone and temporary credentials.')

STEP3 = ('3 · Resize it (vertical scaling)', tri(
    (['Select the instance → [[Instance state]] → [[Stop instance]] → wait for Stopped.', '[[Actions]] → [[Instance settings]] → [[Change instance type]] → [[t3.small]] → [[Apply]].', '[[Instance state]] → [[Start instance]]. Note: the public IP changes (use an Elastic IP when it must not).'],
     'aws ec2 stop-instances --instance-ids $ID && aws ec2 wait instance-stopped --instance-ids $ID\naws ec2 modify-instance-attribute --instance-id $ID --instance-type "{\\"Value\\": \\"t3.small\\"}"\naws ec2 start-instances --instance-ids $ID && aws ec2 wait instance-running --instance-ids $ID\naws ec2 describe-instances --instance-ids $ID --query \'Reservations[0].Instances[0].[InstanceType,PublicIpAddress]\' --output text',
     '<code>t3.small</code> and a <b>new</b> public IP — proof that stop/start may move the VM to another host.'),
    (['Open the VM → [[Availability + scale]] → [[Size]] → pick [[Standard_B2s]] → [[Resize]] (Azure restarts the VM; if the size is not available it asks you to stop first).'],
     'az vm resize --resource-group rg-tiffingo --name tiffingo-vm --size Standard_B2s\naz vm show --resource-group rg-tiffingo --name tiffingo-vm --query hardwareProfile.vmSize --output tsv',
     '<code>Standard_B2s</code>. The public IP normally stays (it is a separate resource).'),
    (['[[Stop]] the VM → [[Edit]] → [[Machine configuration]] → machine type [[e2-small]] → [[Save]] → [[Start / Resume]].'],
     'gcloud compute instances stop tiffingo-vm --zone=asia-south1-a\ngcloud compute instances set-machine-type tiffingo-vm --zone=asia-south1-a --machine-type=e2-small\ngcloud compute instances start tiffingo-vm --zone=asia-south1-a',
     '<code>e2-small</code> in the console; an ephemeral external IP may change after stop/start.')),
    'Vertical scaling needs a restart in every cloud — one reason Lesson 5.3 prefers scaling out.')

STEP4 = ('4 · Run a container without managing servers', tri(
    (['[[Elastic Container Service]] → left menu [[Express mode]].', 'Image URI: <code>public.ecr.aws/nginx/nginx:latest</code>. Task execution role and Infrastructure role: [[Create new role]] for both.', '[[Create]] → watch the [[Resources]] tab; when done open the [[Application URL]].'],
     "ACCT=$(aws sts get-caller-identity --query Account --output text)\naws iam create-role --role-name ecsTaskExecutionRole --assume-role-policy-document \\\n  '{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"ecs-tasks.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}'\naws iam create-role --role-name ecsInfrastructureRoleForExpressServices --assume-role-policy-document \\\n  '{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"ecs.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}'\naws iam attach-role-policy --role-name ecsTaskExecutionRole \\\n  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy\naws iam attach-role-policy --role-name ecsInfrastructureRoleForExpressServices \\\n  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSInfrastructureRoleforExpressGatewayServices\nsleep 20   # IAM roles take a few seconds to become usable\naws ecs create-express-gateway-service --service-name tiffingo-hello \\\n  --primary-container image=public.ecr.aws/nginx/nginx:latest \\\n  --execution-role-arn arn:aws:iam::$ACCT:role/ecsTaskExecutionRole \\\n  --infrastructure-role-arn arn:aws:iam::$ACCT:role/ecsInfrastructureRoleForExpressServices \\\n  --monitor-resources",
     'resources created one by one (service, load balancer, target group, scaling policy) and an Application URL like <code>https://tiffingo-hello.ecs.ap-south-1.on.aws/</code> showing “Welcome to nginx!”. This creates a load balancer that costs money every hour — delete it in the cleanup.'),
    (['Search [[Container Apps]] → [[Create]] → [[Container App]].', 'Resource group <code>rg-tiffingo</code>, name <code>tiffingo-hello</code>, Region [[Central India]], new Container Apps environment.', '[[Container]] tab: tick [[Use quickstart image]] → [[Simple hello world container]]. [[Ingress]]: enabled, [[Accepting traffic from anywhere]], target port 80 → [[Review + create]] → [[Create]] → open the [[Application Url]].'],
     'az containerapp up --name tiffingo-hello --resource-group rg-tiffingo --location centralindia \\\n  --image mcr.microsoft.com/k8se/quickstart:latest --target-port 80 --ingress external\naz containerapp show --name tiffingo-hello --resource-group rg-tiffingo \\\n  --query properties.configuration.ingress.fqdn --output tsv',
     'a URL like <code>https://tiffingo-hello.&lt;random&gt;.centralindia.azurecontainerapps.io</code> showing the Azure Container Apps welcome page. If the CLI asks to install the <code>containerapp</code> extension, answer Y.'),
    (['[[Cloud Run]] → [[Deploy container]] → [[Service]].', '[[Test with a sample container]] (or image <code>us-docker.pkg.dev/cloudrun/container/hello</code>); name <code>tiffingo-hello</code>; Region [[asia-south1 (Mumbai)]].', 'Authentication: [[Allow public access]] (unauthenticated) → [[Create]] → open the URL at the top.'],
     'gcloud run deploy tiffingo-hello --image=us-docker.pkg.dev/cloudrun/container/hello \\\n  --region=asia-south1 --allow-unauthenticated\ngcloud run services describe tiffingo-hello --region=asia-south1 --format="value(status.url)"',
     '“Service URL: https://tiffingo-hello-….asia-south1.run.app” and a page saying “It’s running!”. With no traffic it scales to zero instances.')),
    'Same container, three platforms: Fargate behind a load balancer (AWS), Container Apps on a managed Kubernetes-based environment (Azure), Cloud Run on Google’s serverless infrastructure.')

prac = practical(OWN_INTRO + ' Steps 1–4 take about 40 minutes; with clean-up, the cost is a few rupees of credit.', [SETUP_STEP, STEP1, STEP2, STEP3, STEP4],
    cleanup='<b>AWS:</b> ECS → [[Clusters]] → [[default]] → [[Services]] → select <code>tiffingo-hello</code> → [[Delete service]]; EC2 → select <code>tiffingo-vm</code> → [[Instance state]] → [[Terminate]]; then delete security group <code>tiffingo-web</code>. CLI: <code>aws ecs delete-express-gateway-service --service-arn ARN</code> (ARN from <code>aws ecs list-services --cluster default</code>); <code>aws ec2 terminate-instances --instance-ids $ID</code>; <code>aws ec2 wait instance-terminated --instance-ids $ID; aws ec2 delete-security-group --group-id $SG</code>.<br>'
            '<b>Azure:</b> [[Resource groups]] → <code>rg-tiffingo</code> → [[Delete resource group]] (removes the VM, disk, IP and container app together). CLI: <code>az group delete --name rg-tiffingo --yes --no-wait</code>.<br>'
            '<b>Google Cloud:</b> [[VM instances]] → select → [[Delete]]; [[Cloud Run]] → select → [[Delete]]; [[VPC network]] → [[Firewall]] → delete <code>allow-http</code>. CLI: <code>gcloud compute instances delete tiffingo-vm --zone=asia-south1-a --quiet; gcloud run services delete tiffingo-hello --region=asia-south1 --quiet; gcloud compute firewall-rules delete allow-http --quiet</code>.<br>'
            'Then check your bill page next day — it should show only a few rupees.'.replace('[[', '<b>').replace(']]', '</b>'))

mist = mistakes([
    ['Everything on VMs “because we know VMs”.', 'Habit.', 'Use the decision path: most managed option that fits.'],
    ['Picking a big instance “to be safe”.', 'No measurement.', 'Start small, watch CPU/memory, right-size (Compute Optimizer / Advisor / Recommender).'],
    ['Forgetting stopped VMs still cost.', 'Disks and IPs keep billing.', 'Terminate/delete when done; delete disks and IPs too.'],
    ['Opening SSH (22) to the whole internet permanently.', 'Default wizard choice.', 'Use browser connect / Session Manager / Bastion / IAP; restrict to your IP.'],
    ['Long jobs in functions.', 'Functions feel easy.', 'Lambda stops at 15 minutes — use containers or batch for long work.'],
    ['Launch fails with a quota error.', 'New accounts have low vCPU/GPU quotas.', 'Request a quota increase; choose smaller sizes.'],
    ['Containers on Kubernetes for one tiny app.', 'Hype.', 'Serverless containers first; Kubernetes when you have many services.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Compute services in the cloud: VMs, containers, serverless.'], ['AWS CLF-C02', 'EC2 instance types and families, purchasing options, Auto Scaling, Lambda, ECS/EKS/Fargate, Elastic Beanstalk, Batch, Lightsail, Outposts.'], ['AZ-900', 'VMs, VM Scale Sets, availability sets, Azure Virtual Desktop, containers (ACI, Container Apps, AKS), Functions, App Service.'], ['Google Cloud Digital Leader', 'Compute Engine, GKE, Cloud Run, App Engine, Cloud Run functions — choosing by level of management.']], minw=560) + \
    qx('1. Which AWS service runs code in response to events without provisioning servers?', ['Amazon EC2', 'AWS Lambda', 'Amazon EBS', 'Amazon VPC'], 1, 'Functions as a service.') + \
    qx('2. A developer wants to upload a web app’s code and let the platform handle capacity, load balancing and health monitoring on AWS. Which service?', ['AWS Elastic Beanstalk', 'Amazon EC2 only', 'AWS Batch', 'Amazon S3'], 0, 'PaaS on AWS.') + \
    qx('3. Which Azure service runs containers without managing servers and can scale to zero?', ['Azure Container Apps', 'Azure Dedicated Host', 'Azure Virtual Desktop', 'Azure Blob Storage'], 0, 'Serverless containers.') + \
    qx('4. Which EC2 family is best for a memory-intensive in-memory database?', ['C', 'R', 'T', 'P'], 1, 'R = memory optimised.') + \
    qx('5. Which Google Cloud product is a managed Kubernetes service?', ['App Engine', 'GKE', 'Cloud Run functions', 'Compute Engine'], 1, 'Google Kubernetes Engine.') + \
    qx('6. Which compute option lets you run your own hypervisor on cloud hardware?', ['Functions', 'Bare-metal instances', 'PaaS', 'Burstable instances'], 1, 'No provider hypervisor in between.')

proj = miniproject('Mini project: a compute plan for TiffinGo',
    'Map every TiffinGo workload to the right compute product — and prove one of them on your own account.',
    ['<b>List the workloads:</b> order API, menu website, photo resizing, nightly report, weekly ML training, admin VM for Tally.',
     '<b>Choose:</b> for each, pick a compute type using the decision path; write one line why.',
     '<b>Size:</b> pick an instance family/size or memory/CPU setting for each; note the pricing model from Lesson 5.5.',
     '<b>Prove one:</b> on your own account, deploy the menu page on a VM with a startup script (step 1) and the tracking API as a serverless container (step 4).',
     '<b>Compare:</b> record time to set up, what you had to manage and the cost shown in the billing page next day.',
     '<b>Clean up</b> everything and screenshot the empty resource lists.'],
    'A one-page compute plan (workload → product → size → pricing model) and two working URLs before clean-up.', 'This lesson + 5.3 (scaling) + 5.5 (pricing) + 4.5 (containers and serverless).')

assemble_v2(HERE, story_h2='Five jobs, one question: where should each run?', hook_html=hk,
    narration='TiffinGo now runs five very different jobs. The team’s first instinct is “more VMs”. The cloud offers a whole menu — and the right choice saves money and work.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Cloud compute products and services',
    formal='<b>Cloud compute services</b> provide on-demand processing capacity in different forms of abstraction — <b>virtual machines</b> and <b>bare-metal servers</b> (IaaS), <b>container orchestration</b> and <b>serverless containers</b>, <b>functions</b> (FaaS), <b>application platforms</b> (PaaS), and <b>batch and accelerated computing</b> — each trading control for operational simplicity and billed by the resources and time consumed.',
    simple='Different ways to rent computing power: a whole server, a virtual server, a place to run containers, or just “run my code when something happens”.',
    interview=['“Cloud compute ranges from IaaS — EC2, Azure VMs, Compute Engine — through containers on EKS/AKS/GKE or serverless containers like Fargate and Cloud Run, to functions such as Lambda and PaaS like App Service.”', '“I choose the most managed option that fits: functions for events, PaaS or serverless containers for web apps, VMs when I need OS control, bare metal for licensing or my own hypervisor.”'],
    terms_rows=[('Instance', 'One running VM.'), ('Instance type / VM size', 'The hardware shape.'), ('Image (AMI)', 'Template OS disk.'), ('User data', 'First-boot script.'), ('Bare metal', 'Whole physical server.'), ('Container', 'Packaged app sharing the host kernel.'), ('Kubernetes', 'Container orchestrator.'), ('FaaS', 'Functions run on events.'), ('PaaS', 'Platform runs your code.'), ('vCPU', 'Virtual CPU (often one hyper-thread).')],
    exam='CLF-C02 asks which AWS compute service fits a scenario (EC2, Lambda, Fargate, ECS/EKS, Beanstalk, Batch, Lightsail) and about EC2 families. AZ-900 and Digital Leader ask the same choice for Azure and Google Cloud.',
    picture_h2='The compute spectrum, and how to choose', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven kinds of compute, one by one', TYPES)],
    how_h2='What happens when you click “Launch instance”', how_intro='The same six steps run, in some form, in every cloud.', how_anim=LAUNCH,
    parts_h2='Parts of every VM: name, image, key, startup script, metadata, groups', parts_html=parts, lv='',
    myth_rows=[('Serverless means there are no servers.', 'There are servers — you just do not manage them.', 'Types 4–5.'), ('A vCPU is a CPU core.', 'Usually a hyper-thread; on Graviton a full core.', 'Type 1 expert note.'), ('Kubernetes is always the modern choice.', 'For one or two services it is overhead.', 'Type 3.')],
    extra_secs=[('deep', 'Deep dive', 'Instance families, burstable CPU credits, ARM chips and quotas', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Explain seven kinds of cloud compute and choose one for a workload.', 'Describe what happens inside the cloud when a VM is launched.', 'Read instance names in AWS, Azure and Google Cloud.', 'Launch, inspect, resize and delete a VM on your own account (console and CLI).', 'Run a container without managing servers on AWS, Azure or Google Cloud.'],
    next_html='<a href="../02-storage-systems-in-the-cloud/">6.2 Storage systems in the cloud</a>.',
    pre='<b>Before you start:</b> <a href="../../05-core-cloud-concepts/05-cloud-pricing-models/">5.5 Pricing models</a> (set a budget!) and <a href="../../04-virtualization/05-virtualization-vs-cloud-vs-containers/">4.5 Virtualization vs cloud vs containers</a>.')
