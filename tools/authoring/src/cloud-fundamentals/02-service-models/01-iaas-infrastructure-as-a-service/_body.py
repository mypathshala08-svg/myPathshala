import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
C = 'l21_iaas.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)

hk = hook('Can you get a brand-new server in Mumbai in under two minutes, without buying anything?',
    'Yes — that is <b>Infrastructure as a Service (IaaS)</b>. You rent the raw building blocks — a virtual machine, a disk, a network, a firewall — and you install and run everything on top. AWS Mumbai alone offers <b>849 instance types</b> (sizes of VM), from a 2-vCPU <code>t3.micro</code> at <b>$0.0112 per hour</b> to huge memory and GPU machines. In this lesson you will launch, inspect, stop and delete one with the AWS CLI, step by step.',
    ['What IaaS gives you and what you still manage.', 'What happens inside AWS when you launch a VM, and how its lifecycle affects the bill.', 'A full CLI walkthrough (and the console screen) to launch a web server — and clean it up.'])

def stack_scene():
    rows = [('Application + data', 'you'), ('Runtime / middleware', 'you'), ('Operating system', 'you'), ('Virtualization', 'AWS'), ('Servers + storage', 'AWS'), ('Networking + data centre', 'AWS')]
    o = t(180, 13, 'IaaS: who manages what?', 9, 'ink', bold=True)
    for i, (n, w) in enumerate(rows):
        y = 20 + i * 22
        o += box(40, y, 200, 19, 'blue' if w == 'you' else 'green', rx=4) + t(50, y + 13, n, 8, 'ink', anchor='start', bold=True)
        o += t(250, y + 13, 'TiffinGo team' if w == 'you' else 'cloud provider', 7.6, 'blue' if w == 'you' else 'green', anchor='start', bold=True)
    return o
scene_svg = scene('A six-layer stack: application and data, runtime, operating system are managed by the TiffinGo team; virtualization, servers and storage, networking and data centre are managed by the cloud provider.', stack_scene(), 'With IaaS you <tspan font-weight="700" class="s-acc">rent the bottom half</tspan> and run the top half yourself.')
dialogue = '''K> Sir, the new TiffinGo menu website needs a Linux server with nginx. Should I ask finance to buy one?
A> No purchase order needed. With IaaS we rent a virtual machine in Mumbai, choose its size, open the web port in a firewall, and it boots in about a minute.
R> Then who installs Linux updates and nginx?
A> We do — that is the deal with IaaS: AWS runs the hardware and the virtualization; we run the operating system and the app. Let’s see exactly how a launch works, then do it with the CLI.'''

# ---------- big picture 1: responsibility stack across on-prem vs IaaS
def resp():
    layers_ = ['Applications', 'Data', 'Runtime', 'Middleware', 'Operating system', 'Virtualization', 'Servers', 'Storage', 'Networking']
    o = t(320, 16, 'What you manage: on-premises vs IaaS', 11, 'ink', bold=True)
    for c, (name, you_n) in enumerate([('On-premises', 9), ('IaaS (EC2, Azure VMs, Compute Engine)', 5)]):
        x = 60 + c * 290
        o += t(x + 130, 36, name, 9, 'ink', bold=True)
        for r, lab in enumerate(layers_):
            mine = r < you_n
            o += box(x, 44 + r * 25, 260, 21, 'blue' if mine else 'green', rx=4) + t(x + 10, 58 + r * 25, lab, 8.4, 'ink', anchor='start', bold=True) + t(x + 250, 58 + r * 25, 'You' if mine else 'Provider', 8, 'blue' if mine else 'green', anchor='end', bold=True)
    o += arrow(326, 160, 346, 160, 'acc', 2.4)
    return o + t(320, 280, 'The provider takes over the 4 bottom layers; you still patch the OS and run everything above it.', 8.4, 'ink2')
RESP = bigfig('Two stacks of nine layers. On-premises: you manage applications, data, runtime, middleware, operating system, virtualization, servers, storage and networking. IaaS: you manage applications, data, runtime, middleware and operating system; the provider manages virtualization, servers, storage and networking.', resp(), h=290)

# ---------- big picture 2: the building blocks of one IaaS server
def blocks():
    o = t(320, 16, 'The building blocks of one IaaS server (AWS names)', 11, 'ink', bold=True)
    o += box(14, 30, 612, 250, 'card', rx=12) + t(26, 46, 'Region: Asia Pacific (Mumbai) ap-south-1', 8.6, 'acc', anchor='start', bold=True)
    o += box(30, 56, 400, 212, 'green', rx=10) + t(42, 72, 'Availability Zone ap-south-1a', 8.2, 'green', anchor='start', bold=True)
    o += box(46, 82, 368, 176, 'card', rx=8) + t(58, 98, 'VPC (your private network) → subnet 10.0.1.0/24', 8, 'ink', anchor='start', bold=True)
    o += box(70, 110, 210, 136, 'violet', rx=8, sw=2.2) + t(80, 126, 'Security group (firewall)', 8, 'violet', anchor='start', bold=True) + t(80, 138, 'allow 80 from all · 22 from my IP', 7, 'ink2', anchor='start')
    o += node_box(90, 150, 80, 56, 'server', 'EC2 instance', 't3.micro')
    o += node_box(186, 150, 80, 56, 'disk', 'EBS volume', '8 GB root disk')
    o += f'<line x1="170" y1="178" x2="186" y2="178" style="stroke:var(--green);stroke-width:2"/>'
    o += t(175, 228, 'built from an AMI (Amazon Linux 2023)', 7.4, 'ink2')
    o += node_box(306, 120, 92, 52, 'globe', 'Public IP', '54.x.x.x')
    o += node_box(306, 186, 92, 52, 'shield', 'Key pair', 'tiffingo-key.pem')
    o += node_box(452, 70, 160, 60, 'user', 'You (CLI / console)', 'run-instances')
    o += node_box(452, 150, 160, 60, 'gear', 'User data', 'start-up script')
    o += node_box(452, 216, 160, 52, 'meter', 'Billing', 'per second while running')
    o += arrow(452, 100, 430, 100, 'acc', 2) + arrow(452, 180, 270, 180, 'acc', 1.6)
    return o
BLOCKS = bigfig('An Availability Zone inside the Mumbai region holds a VPC subnet; inside it a security group wraps an EC2 instance with an EBS root volume built from an AMI. The instance has a public IP and a key pair; on the right you launch it from the CLI or console, a user-data start-up script configures it, and billing counts per second.', blocks(), h=290)
picture = ('  <p>IaaS is the bottom layer of the cloud: you rent <b>infrastructure</b> — compute, storage and network — and build on it like on your own server, without owning hardware. First, the responsibility line:</p>\n' + RESP +
           '\n  <p>Second, the pieces. A “server” in IaaS is not one thing; it is several resources working together. Learn these names — every lab and every exam uses them:</p>\n' + BLOCKS)

# ---------- animation 1: what happens when you launch
LN = {'you': (4, 54, 58, 50, 'user', 'You', 'aws CLI'), 'api': (72, 6, 62, 48, 'dns', 'EC2 API', 'ap-south-1'), 'iam': (72, 104, 62, 48, 'shield', 'IAM', 'allowed?'),
      'host': (146, 54, 62, 50, 'chip', 'Host in AZ', 'Nitro'), 'vm': (220, 6, 62, 48, 'server', 'New VM', 't3.micro'), 'ebs': (220, 104, 62, 48, 'disk', 'EBS disk', 'from AMI'),
      'net': (294, 6, 62, 48, 'lb', 'Network', 'subnet + SG'), 'boot': (294, 104, 62, 48, 'gear', 'Boot', 'user data')}
LS = [dict(on=['you', 'api'], hot='you', move=(62, 79, 74, 30, 'run'), head='Step 1 · You call RunInstances', text='aws ec2 run-instances --image-id ami-… --instance-type t3.micro …', text2='The console “Launch instance” button sends exactly the same API call.', svc='AWS EC2 API · Azure Resource Manager · Google Compute Engine API'),
      dict(on=['you', 'api', 'iam'], hot='iam', move=(103, 54, 103, 104, 'check'), head='Step 2 · Are you allowed?', text='The API checks your signature and IAM policy (ec2:RunInstances)', text2='and your account limits. If not allowed: “UnauthorizedOperation”.', svc='AWS IAM · Microsoft Entra ID + RBAC · Google Cloud IAM'),
      dict(on=['you', 'api', 'iam', 'host'], hot='host', move=(134, 30, 148, 70, 'place'), head='Step 3 · Find a physical host', text='The scheduler picks a server in an Availability Zone (ap-south-1a)', text2='with free capacity for 2 vCPU + 1 GiB. State: pending.', svc='The provider’s placement service; you only see the AZ'),
      dict(on=['you', 'api', 'iam', 'host', 'vm', 'ebs'], hot='ebs', move=(208, 79, 222, 128, 'disk'), head='Step 4 · Create the VM and its disk', text='The hypervisor carves out the VM; a root EBS volume is created', text2='from the AMI snapshot (Amazon Linux 2023) and attached.', svc='AWS Nitro + EBS · Azure Hyper-V + Managed Disk · Google KVM + Persistent Disk'),
      dict(on=['you', 'api', 'iam', 'host', 'vm', 'ebs', 'net'], hot='net', move=(282, 30, 296, 30, 'NIC'), head='Step 5 · Plug it into the network', text='A network interface joins your subnet, gets a private IP (10.x)', text2='and a public IP; the security group firewall wraps it.', svc='AWS VPC + security group · Azure VNet + NSG · Google VPC + firewall rules'),
      dict(on=list(LN), hot='boot', move=(251, 128, 296, 128, 'boot'), head='Step 6 · Boot and run user data', text='Linux boots; cloud-init runs your user-data script once (installs nginx).', text2='Status checks pass → state: running. Billing starts per second.', svc='EC2 user data · Azure custom data · GCE startup-script (all use cloud-init)')]
LAUNCH = flow_anim('What happens when you launch a VM', 'One CLI command triggers six steps inside AWS. Each step names the equivalent in Azure and Google Cloud.', 'Launching an instance', 'Animation: CLI call to EC2 API, IAM permission check, placement on a host in an AZ, VM and EBS disk created from the AMI, network interface with security group, boot with user data.', LN, LS, hid='launch')

# ---------- animation 2: lifecycle and billing
def life_frame(k):
    states = [('pending', 'amber'), ('running', 'green'), ('stopping', 'amber'), ('stopped', 'blue'), ('terminated', 'red')]
    o = t(180, 12, 'EC2 instance lifecycle', 9, 'ink', bold=True)
    for i, (s, tn) in enumerate(states):
        x = 8 + i * 70
        o += box(x, 26, 62, 34, 'amber' if i == k else ('card' if i != k else tn), rx=8, sw=2.6 if i == k else None) + t(x + 31, 47, s, 8, 'ink', bold=True)
        if i < 4: o += arrow(x + 62, 43, x + 70, 43, 'ink3', 1.4)
    bill = [('VM compute', [0, 1, 0, 0, 0]), ('EBS disk', [1, 1, 1, 1, 0]), ('Public IPv4', [1, 1, 0, 0, 0])]
    for j, (n, on) in enumerate(bill):
        y = 76 + j * 24
        o += t(70, y + 13, n, 8, 'ink', anchor='end', bold=True) + box(78, y, 200, 18, 'green' if on[k] else 'card', rx=4) + t(178, y + 13, 'billed' if on[k] else 'not billed', 7.6, 'ink', bold=bool(on[k]))
    return o
LF = [('pending', 'AWS is placing and booting the VM.', 'Disk and IP exist; compute billing starts when it is running'),
      ('running', 'The VM serves users: compute, disk and public IP are all billed.', 't3.micro in Mumbai: $0.0112 per hour, billed per second (min 60 s)'),
      ('stopping', 'You ran stop-instances. The OS shuts down cleanly.', 'Data on the EBS disk is kept'),
      ('stopped', 'No compute charge — but the EBS disk is still billed.', 'Stopped ≠ free. Start it again any time (it may move to a new host)'),
      ('terminated', 'Deleted for ever. The root disk is deleted too (default).', 'Nothing more to pay. Create an AMI first if you need a copy')]
fr = [life_frame(k) + box(6, 158, 348, 62, 'blue', rx=8) + t(14, 174, f'State: {h}', 9, 'ink', anchor='start', bold=True) + t(14, 190, a, 7.6, 'ink', anchor='start') + t(14, 206, b, 7.2, 'ink2', anchor='start') for k, (h, a, b) in enumerate(LF)]
LIFE = anim_one('How it works', 'Lifecycle and the bill', 'Every state changes what you pay. This is the most common source of surprise bills for students.', 'Instance lifecycle', 'Animation of EC2 states pending, running, stopping, stopped, terminated, showing which of compute, EBS disk and public IPv4 are billed in each.', fr, ['Pending.', 'Running.', 'Stopping.', 'Stopped.', 'Terminated.'], delay=6000, hid='lifecycle')
how_after = '\n  <p>Since February 2024 AWS also charges for every public IPv4 address ($0.005 per hour). Release unused Elastic IPs and do not give public IPs to servers that do not need them.</p>'


# ================================================================== TYPES: VM families (added v4)
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

def famfig():
    o = t(320, 16, 'Six VM families — same idea in every cloud', 11, 'ink', bold=True)
    fams = [('1', 'General purpose', 'balanced CPU : RAM', 'm7i · Dsv5 · N4/E2', 'blue'), ('2', 'Burstable', 'cheap, CPU credits', 't3/t4g · B · e2-micro', 'green'), ('3', 'Compute optimised', 'more CPU per GB', 'c7i · Fsv2 · C4', 'amber'),
            ('4', 'Memory optimised', 'more RAM per vCPU', 'r7i/x2 · E/M · M3', 'violet'), ('5', 'Storage optimised', 'fast local NVMe', 'i4i · Lsv3 · Z3', 'blue'), ('6', 'Accelerated', 'GPUs / AI chips', 'p5/g6 · NC/ND · A3/G2', 'red')]
    for i, (n, a, b, c, tn) in enumerate(fams):
        x = 12 + (i % 3) * 208; y = 32 + (i // 3) * 92
        o += box(x, y, 198, 80, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 106, y + 30, a, 8.6, 'ink', bold=True) + t(x + 106, y + 48, b, 7, 'ink2') + t(x + 106, y + 66, c, 6.8, 'ink')
    o += t(320, 228, 'Read a name: AWS m7i.large = family m · generation 7 · Intel (i) · size large', 7.4, 'ink2')
    return o
FAMMAP = bigfig('Map of six VM families with AWS, Azure and Google examples: general purpose, burstable, compute optimised, memory optimised, storage optimised, accelerated.', famfig(), h=240)

F1 = mk(['Mixed load', 'Balanced box', 'Steady service'], ['app server|CPU + RAM|both used', 'general purpose|1 vCPU : 4 GiB|m · D · N4', 'result|predictable|price-performance'], ['blue', 'blue', 'green'],
        ['an app that uses CPU and memory evenly', '4 GiB RAM per vCPU is the usual ratio', 'the safe default when you do not know yet'],
        [('Load', 'The app uses CPU and memory in similar measure.', ''), ('Fit', 'General purpose gives about 4 GiB RAM per vCPU.', ''), ('Run', 'Steady, predictable performance at a fair price.', '')],
        'General purpose in action', 'The default choice.', 'General purpose', 'Animation: mixed load; balanced instance; steady service.', 'f1anim')
T1 = vtype(1, 'General purpose', 'blue',
    '<b>General-purpose</b> instances provide a balance of compute, memory and networking (typically about 4 GiB of memory per vCPU) for workloads that use these resources in roughly equal proportion.',
    'A family car: not the fastest, not the biggest boot, but good at most trips.',
    'TiffinGo’s order API containers run on two m7i.large (2 vCPU, 8 GiB) instances behind a load balancer — CPU and memory both sit around 40%.',
    'AWS M family (m7i, m7g Graviton, m7a); Azure D-series (Dsv5, Dasv6); Google N4, N2, E2 standard.', '', F1,
    'you are unsure, or the app is a typical web/app server or small database.',
    'one resource is clearly the bottleneck — pick the specialised family and pay less.',
    plain='Normal all-rounder machines with a fair mix of processor and memory.',
    how=[('Ratio', 'About 1 vCPU : 4 GiB.'), ('Sizes', 'large, xlarge, 2xlarge … double each step.'), ('Network', 'Bandwidth grows with size.'), ('Choose CPU', 'Intel, AMD or ARM (Graviton/Cobalt/Axion).'), ('Right-size', 'Watch metrics, then move up or down.')],
    words=[('vCPU', 'virtual CPU — usually one hyper-thread of a physical core'), ('GiB', 'gibibyte, 1,024 MiB'), ('ARM', 'processor design used by Graviton, Cobalt and Axion chips; usually cheaper')],
    diff=table(['', 'General purpose', 'Burstable'], [['CPU', 'full, always', 'baseline + credits'], ['Price', 'medium', 'lowest'], ['Best for', 'steady load', 'mostly idle load']], minw=420),
    where=['Web and app servers', 'Small and medium databases', 'Microservices and containers'],
    realworld='Most production fleets start on general-purpose instances; cost reviews later move outliers to compute- or memory-optimised families.',
    pro='ARM general-purpose instances (AWS Graviton, Azure Cobalt, Google Axion) typically give better price-performance — check that your software has ARM builds before switching.')

F2 = mk(['Quiet hours', 'Save credits', 'Short burst'], ['idle|CPU 5%|below baseline', 'credits|bank fills up|while idle', 'burst|100% CPU|spends credits'], ['green', 'blue', 'amber'],
        ['most of the day the CPU is nearly idle', 'unused baseline turns into CPU credits', 'a spike spends credits; when empty, CPU is throttled (or billed extra)'],
        [('Idle', 'The VM runs below its baseline CPU most of the time.', ''), ('Bank', 'Unused baseline is saved as CPU credits.', ''), ('Burst', 'Spikes spend credits; empty bank = throttled or extra charge.', '')],
        'Burstable in action', 'Cheap until you are busy all day.', 'Burstable', 'Animation: idle VM earns credits; credits are banked; a burst spends them.', 'f2anim')
T2 = vtype(2, 'Burstable (shared-core)', 'green',
    '<b>Burstable</b> instances provide a baseline level of CPU performance with the ability to burst above it using accumulated <b>CPU credits</b>, at a lower price than general-purpose instances; they suit workloads that are idle most of the time.',
    'A mobile prepaid data pack: light daily use is cheap, but streaming all day empties it fast.',
    'The TiffinGo menu website gets traffic only at lunch and dinner — a t3.micro (10% baseline) earns credits overnight and spends them at 1 pm.',
    'AWS T family (t3, t3a, t4g); Azure B-series (Bsv2, Basv2, Bpsv2); Google E2 shared-core (e2-micro, e2-small, e2-medium).',
    'CPU-credit internals are animated in the deep dive below.', F2,
    'labs, dev/test, small websites, low-traffic internal tools.',
    'CPU stays high for hours — credits run out and the VM slows down or (in unlimited mode) costs more than a general-purpose one.',
    plain='Very cheap small machines that are fine when mostly idle and can speed up for short bursts.',
    how=[('Baseline', 'e.g. t3.micro = 10% of each vCPU.'), ('Earn', 'Credits accrue below baseline.'), ('Spend', 'Above baseline uses credits.'), ('Empty', 'Standard mode throttles; unlimited mode bills extra.'), ('Watch', 'CPUCreditBalance metric.')],
    words=[('baseline', 'the CPU % you can use forever without credits'), ('CPU credit', 'one vCPU at 100% for one minute (AWS)'), ('throttle', 'force the CPU down to baseline')],
    diff=table(['', 'Burstable', 'General purpose'], [['Sustained CPU', 'limited', 'full'], ['Cost', 'lowest', 'higher'], ['Surprise risk', 'credit drain', 'low']], minw=420),
    where=['Course labs and free tiers', 'Small websites and blogs', 'Bastion / jump hosts'],
    realworld='Free-tier and free-credit offers are built around burstable sizes: t3.micro/t4g.micro on AWS, B1s/B-series on Azure, e2-micro on Google Cloud.',
    pro='AWS T3/T3a/T4g launch in <i>unlimited</i> mode by default — they never throttle, but sustained use adds surplus-credit charges. Check the credit specification on long-running jobs.')

F3 = mk(['CPU-bound job', 'More cores per GB', 'Done faster'], ['job|encoding, batch|CPU 100%', 'compute optimised|1 vCPU : 2 GiB|c · F · C4', 'result|shorter run|lower bill'], ['amber', 'amber', 'green'],
        ['the job waits on the processor, not memory', 'more, faster CPU and less RAM for the money', 'finishing sooner can cost less overall'],
        [('Job', 'Work that keeps CPUs at 100%: encoding, batch, game servers.', ''), ('Fit', 'Compute-optimised: about 2 GiB per vCPU and high clock speeds.', ''), ('Result', 'Shorter runtime, lower total cost.', '')],
        'Compute optimised in action', 'Pay for CPU, not idle RAM.', 'Compute optimised', 'Animation: CPU-bound job; compute-optimised instance; job finishes faster.', 'f3anim')
T3 = vtype(3, 'Compute optimised', 'amber',
    '<b>Compute-optimised</b> instances offer a high ratio of CPU to memory (typically about 2 GiB per vCPU) and high-performance processors, for compute-bound workloads such as batch processing, media encoding, scientific modelling, gaming servers and high-traffic web front ends.',
    'A sports bike: built for speed, not for carrying luggage.',
    'Every night TiffinGo converts 2,000 kitchen videos to mobile formats; on c7i.2xlarge the batch finishes in 40 minutes instead of 70 on general purpose.',
    'AWS C family (c7i, c7g, c7a), HPC instances (hpc7); Azure F-series (Fsv2, Fasv6), HB/HC for HPC; Google C4, C3, H3 (HPC).', '', F3,
    'profiling shows CPU is the bottleneck and memory is mostly unused.',
    'the app needs lots of memory (caches, JVM heaps) — it will swap and slow down.',
    plain='Machines with more and faster processor power for jobs that do heavy calculation.',
    how=[('Profile', 'CPU near 100%, memory low.'), ('Ratio', 'About 1 vCPU : 2 GiB.'), ('Clock', 'Higher sustained frequencies.'), ('Scale out', 'Often many instances for batch.'), ('Combine', 'With Spot for cheap batch.')],
    words=[('compute-bound', 'limited by processor speed'), ('HPC', 'high-performance computing — many tightly connected machines'), ('encoding', 'converting audio/video formats')],
    diff=table(['', 'Compute optimised', 'Memory optimised'], [['RAM per vCPU', '~2 GiB', '~8 GiB or more'], ['Bottleneck solved', 'CPU', 'memory'], ['Example', 'video encoding', 'in-memory DB']], minw=420),
    where=['Batch and media processing', 'Game servers', 'Scientific and financial models'],
    realworld='Media companies run transcoding farms on compute-optimised Spot fleets, because jobs are CPU-bound and can restart if interrupted.',
    pro='A bigger, faster instance can be cheaper per job: cost = price per hour × hours. Measure cost per unit of work, not per hour.')

F4 = mk(['Big data in RAM', 'Lots of memory', 'No disk waits'], ['data|20 GB working set|cache, DB', 'memory optimised|1 vCPU : 8 GiB+|r · E · M3', 'result|in-memory|fast queries'], ['violet', 'violet', 'green'],
        ['the working set must fit in memory', 'eight or more GiB per vCPU, up to terabytes', 'queries never wait for the disk'],
        [('Data', 'The working set (database, cache, Spark data) is large.', ''), ('Fit', 'Memory-optimised: 8 GiB+ per vCPU, up to many TiB.', ''), ('Result', 'Data stays in RAM — no swapping, fast queries.', '')],
        'Memory optimised in action', 'Keep the data in RAM.', 'Memory optimised', 'Animation: large working set; memory-optimised instance; fast in-memory queries.', 'f4anim')
T4 = vtype(4, 'Memory optimised', 'violet',
    '<b>Memory-optimised</b> instances provide a high ratio of memory to CPU (typically 8 GiB per vCPU, with extra-large sizes offering terabytes of RAM) for workloads that process large data sets in memory, such as relational and in-memory databases, caches, real-time analytics and SAP HANA.',
    'A big dining table: more people can work on the same meal at once without running back to the kitchen.',
    'TiffinGo’s analytics team runs Spark on r7i.2xlarge (8 vCPU, 64 GiB) so a whole month of orders fits in memory — the C-DAC Big Data modules use exactly this kind of node.',
    'AWS R family (r7i, r7g), X (x2iedn), High Memory (u-*); Azure E-series, M-series (Mv2/Mv3); Google M3, N2/N4 highmem, X4 for the largest SAP systems.', '', F4,
    'memory is the bottleneck: databases, caches, Spark/Hadoop executors, SAP HANA.',
    'the workload is CPU-bound — you pay for RAM you do not use.',
    plain='Machines with a lot of memory, for programs that keep big data in RAM.',
    how=[('Measure', 'Working set and memory pressure.'), ('Ratio', '8 GiB+ per vCPU.'), ('NUMA', 'Large sizes span sockets — tune apps.'), ('Licence', 'Some DB licences are per core — fewer, bigger-RAM cores save money.'), ('Monitor', 'Memory needs an agent (not default metrics).')],
    words=[('working set', 'the data an app touches often'), ('in-memory', 'kept in RAM rather than on disk'), ('SAP HANA', 'an in-memory enterprise database')],
    diff=table(['', 'Memory optimised', 'Storage optimised'], [['Speeds up', 'RAM access', 'local disk I/O'], ['Data size', 'fits in RAM', 'larger than RAM'], ['Example', 'Redis, Spark', 'Cassandra, Kafka']], minw=420),
    where=['Databases and caches', 'Spark / Hadoop analytics', 'SAP and ERP systems'],
    realworld='SAP HANA certified instances reach tens of terabytes of RAM — AWS High Memory, Azure M-series and Google X4 exist mainly for these systems.',
    pro='Default VM metrics in all three clouds do not include memory usage — install the CloudWatch agent / Azure Monitor agent / Ops Agent before deciding to right-size memory.')

F5 = mk(['Many small reads', 'Local NVMe', 'Low latency'], ['I/O|millions of IOPS|random reads', 'storage optimised|NVMe on the host|i · L · Z3', 'result|microseconds|fast DB'], ['blue', 'blue', 'green'],
        ['the app is waiting on disk reads and writes', 'very fast SSDs attached to the physical host', 'but data is lost if the VM moves — replicate it'],
        [('I/O', 'The workload does huge numbers of disk reads/writes.', ''), ('Fit', 'Storage-optimised: local NVMe SSDs on the host.', ''), ('Care', 'Local disks are ephemeral — the app must replicate data.', '')],
        'Storage optimised in action', 'Disk speed, not CPU, is the limit.', 'Storage optimised', 'Animation: heavy disk I/O; local NVMe instance; low latency with replication.', 'f5anim')
T5 = vtype(5, 'Storage optimised', 'blue',
    '<b>Storage-optimised</b> instances provide high, low-latency local storage throughput and IOPS — usually large local NVMe SSDs attached directly to the host — for workloads such as NoSQL databases, data warehousing, search engines and log processing; the local storage is ephemeral.',
    'Keeping your tools on your own workbench instead of fetching them from the store room each time.',
    'TiffinGo’s Kafka cluster for real-time order events runs on i4i instances: local NVMe gives the low write latency, and Kafka replication protects the data.',
    'AWS I family (i4i, i4g, im4gn), D family (d3 — dense HDD); Azure L-series (Lsv3, Lasv3); Google Z3.', 'Instance storage vs network disks is explained in Lesson 6.2.', F5,
    'the software replicates its own data (Cassandra, Kafka, Elasticsearch, ClickHouse).',
    'you need disks that survive stop/start — use network disks (EBS, managed disks, persistent disks).',
    plain='Machines with very fast disks built in, for databases and tools that read and write data all the time.',
    how=[('Local NVMe', 'SSD physically in the host.'), ('Ephemeral', 'Lost on stop, host failure or terminate.'), ('Replicate', 'App keeps 3 copies across nodes/AZs.'), ('Format', 'Mount at boot (user data).'), ('Back up', 'To object storage.')],
    words=[('IOPS', 'input/output operations per second'), ('NVMe', 'fast SSD interface'), ('ephemeral', 'temporary; does not survive the VM moving')],
    diff=table(['', 'Local NVMe', 'Network disk'], [['Latency', 'lowest', 'low'], ['Survives stop', 'no', 'yes'], ['Snapshots', 'no', 'yes']], minw=420),
    where=['NoSQL databases', 'Kafka and search clusters', 'Data warehouses'],
    realworld='Self-managed Cassandra and Elasticsearch clusters are classic storage-optimised users — and the reason managed services like Keyspaces or OpenSearch Service exist.',
    pro='Because instance storage is wiped when the VM stops, automation must re-format and re-join the node on boot — test that path before production.')

F6 = mk(['Train a model', 'GPU instance', 'Hours, not weeks'], ['AI job|matrix maths|millions of ops', 'accelerated|GPU / AI chip|p · NC · A3', 'result|parallel|much faster'], ['red', 'amber', 'green'],
        ['deep learning, graphics, simulations', 'thousands of GPU cores work in parallel', 'pay a high hourly price only while training'],
        [('Job', 'Matrix-heavy work: training, inference, rendering.', ''), ('Fit', 'Accelerated instances add GPUs or AI chips.', ''), ('Result', 'Parallel work finishes far faster; stop when done.', '')],
        'Accelerated computing in action', 'Rent GPUs by the hour.', 'Accelerated', 'Animation: AI training job; GPU instance; fast parallel training.', 'f6anim')
T6 = vtype(6, 'Accelerated computing (GPU / AI chips)', 'red',
    '<b>Accelerated-computing</b> instances add hardware accelerators — GPUs, FPGAs or custom AI chips — to perform massively parallel work such as machine-learning training and inference, graphics rendering, video processing and scientific simulation far faster than CPUs.',
    'Hiring a team of 1,000 helpers to roll rotis at the same time instead of one expert cook.',
    'TiffinGo trains a demand-forecast model once a week on a g6 GPU instance for two hours, then stops it — renting instead of buying a ₹15 lakh GPU server.',
    'AWS P (p5), G (g6), Inf2 (Inferentia), Trn1/Trn2 (Trainium); Azure NC, ND, NV series; Google A3/A4 (NVIDIA GPUs), G2, and Cloud TPU.', '', F6,
    'the workload is parallel and supported by GPU libraries (CUDA, PyTorch, TensorFlow).',
    'the code is single-threaded or not GPU-enabled — you pay a premium for idle accelerators.',
    plain='Machines with graphics cards or special AI chips for very heavy maths like training AI models.',
    how=[('Quota', 'GPU quotas often start at 0 — request early.'), ('Image', 'Use deep-learning images with drivers.'), ('Data', 'Stage data close (object storage, fast disks).'), ('Run', 'Train / render.'), ('Stop', 'Highest hourly prices — never leave idle.')],
    words=[('GPU', 'graphics processor with thousands of small cores'), ('inference', 'using a trained model to predict'), ('TPU', 'Google’s custom AI accelerator')],
    diff=table(['', 'GPU', 'Custom AI chip'], [['Flexibility', 'any CUDA workload', 'supported frameworks'], ['Price-performance', 'good', 'often better for its target'], ['Examples', 'NVIDIA H100', 'Trainium, Inferentia, TPU']], minw=420),
    where=['AI/ML training and inference', '3D rendering and VFX', 'Genomics and simulations'],
    realworld='GPU capacity is the scarcest IaaS resource: providers offer capacity reservations and scheduled blocks for ML training because on-demand GPUs are often unavailable.',
    pro='New accounts usually have GPU quotas of zero; requesting quota in the right Region days before you need it is part of the plan, not an afterthought.')

TYPESUM = table(['#', 'Family', 'RAM per vCPU', 'AWS', 'Azure', 'Google Cloud'], [
    ['1', 'General purpose', '~4 GiB', 'M', 'D', 'N4, N2, E2'], ['2', 'Burstable', 'varies', 'T', 'B', 'E2 shared-core'], ['3', 'Compute optimised', '~2 GiB', 'C', 'F', 'C4, C3, H3'],
    ['4', 'Memory optimised', '8 GiB+', 'R, X, U', 'E, M', 'M3, X4, highmem'], ['5', 'Storage optimised', 'varies + NVMe', 'I, D', 'L', 'Z3'], ['6', 'Accelerated', 'varies + GPU', 'P, G, Inf, Trn', 'NC, ND, NV', 'A3, G2, TPU']], minw=600)
TCHECK = ('  <h3>Check yourself: which family?</h3>\n' +
    qx('A. Redis cache holding 50 GB of sessions.', ['Compute optimised', 'Memory optimised', 'Burstable', 'Accelerated'], 1, 'Data in RAM.') +
    qx('B. A student lab server idle most of the day.', ['Burstable', 'Storage optimised', 'Memory optimised', 'Accelerated'], 0, 'Cheap with credits.') +
    qx('C. Nightly video transcoding at 100% CPU.', ['Compute optimised', 'Memory optimised', 'Storage optimised', 'Burstable'], 0, 'CPU-bound.') +
    qx('D. Kafka brokers needing very low-latency local disk.', ['Storage optimised', 'General purpose', 'Accelerated', 'Burstable'], 0, 'Local NVMe.'))
TYPESEC = ('  <p>Every cloud sells VMs in the same six families. Each is shown in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, a real-world example, a TiffinGo scenario and an expert note.</p>\n'
           + challenge(['Why can a burstable VM become slow every afternoon?', 'Why must apps on storage-optimised VMs replicate their own data?', 'Which family suits Spark executors best?'], 'types 2, 5 and 4') + FAMMAP
           + jump(['General', 'Burstable', 'Compute', 'Memory', 'Storage', 'Accelerated']) + T1 + T2 + T3 + T4 + T5 + T6
           + '\n  <h3 style="margin-top:34px">All six side by side</h3>\n' + TYPESUM + '\n' + TCHECK)

# ---------- parts
TYPES = capsec('l21_types.txt', '== instance types')
parts = cards([
    ('AMI (Amazon Machine Image)', 'The template disk: OS + software. We use Amazon Linux 2023, looked up from a public SSM parameter so it is always the latest.', 'what to boot'),
    ('Instance type', 'The size: vCPUs, memory, network. t3.micro = 2 vCPU, 1 GiB; t3.medium = 2 vCPU, 4 GiB.', 'how big'),
    ('Key pair', 'Public key stays on the VM; you keep the private .pem file to log in with SSH. AWS cannot recover it.', 'how to log in'),
    ('Security group', 'A stateful firewall around the instance: allow port 80 from everyone, port 22 only from your IP.', 'who may connect'),
    ('EBS volume', 'Network disk that survives stop/start. Root volume is deleted on terminate by default.', 'where data lives'),
    ('User data', 'A script that runs once at first boot (as root) — installs and configures software automatically.', 'automation'),
    ('Region and AZ', 'ap-south-1 = Mumbai; ap-south-1a/b/c = separate data centres. Spread servers across AZs for availability.', 'where it runs'),
    ('Public / private IP', 'Private 10.x for traffic inside the VPC; public IP for the internet (billed).', 'how to reach it')]) + \
    '\n  <h3>Instance families: the letter tells you the purpose</h3>\n' + table(['Letter', 'Family', 'Good for', 'Example'], [
    ['t', 'Burstable general purpose', 'small websites, dev/test, labs', 't3.micro, t4g.small'],
    ['m', 'General purpose', 'balanced apps, app servers', 'm7i.large'],
    ['c', 'Compute optimised', 'CPU-heavy: batch, gaming, encoding', 'c7i.xlarge'],
    ['r / x / u', 'Memory optimised', 'big databases, in-memory analytics (Spark)', 'r7i.2xlarge'],
    ['i / d', 'Storage optimised', 'very fast local disks, NoSQL, data warehouses', 'i4i.large'],
    ['p / g', 'Accelerated (GPU)', 'machine learning, graphics', 'g5.xlarge'],
    ['suffix g / a / i', 'CPU maker', 'g = AWS Graviton (ARM, cheaper), a = AMD, i = Intel', 't4g = ARM']], minw=600) + \
    '\n  <p>Real count from the AWS price list for Mumbai (Linux, shared tenancy):</p>\n' + code('text', 'l21_types.txt', 'python3 ec2_types.py ec2_ap-south-1.json', TYPES)

clouds = vendor_tabs(
    '<p><b>AWS EC2</b>: AMIs, instance types, key pairs, security groups, EBS, user data. CLI: <code>aws ec2 run-instances</code>. Free-plan friendly sizes: t3.micro / t4g.micro.</p>',
    '<p><b>Azure Virtual Machines</b>: images, VM sizes (e.g. Standard_B1s), SSH keys, Network Security Groups, managed disks, custom data. CLI: <code>az vm create --resource-group rg-tiffingo --name web1 --image Ubuntu2204 --size Standard_B1s --admin-username azureuser --generate-ssh-keys</code></p>',
    '<p><b>Google Compute Engine</b>: images, machine types (e.g. e2-micro), OS Login / SSH keys, VPC firewall rules, persistent disks, startup scripts. CLI: <code>gcloud compute instances create web1 --zone=asia-south1-a --machine-type=e2-micro --image-family=debian-12 --image-project=debian-cloud --metadata-from-file=startup-script=startup.sh</code></p>') + \
    cloud3([['VM service', 'EC2', 'Virtual Machines', 'Compute Engine'], ['Template image', 'AMI', 'Image (Marketplace / gallery)', 'Image / image family'], ['Size', 'Instance type (t3.micro)', 'VM size (Standard_B1s)', 'Machine type (e2-micro)'],
            ['Firewall', 'Security group', 'Network Security Group', 'VPC firewall rule'], ['Disk', 'EBS volume', 'Managed disk', 'Persistent disk'], ['Start-up script', 'User data', 'Custom data', 'startup-script metadata'],
            ['Create from CLI', 'aws ec2 run-instances', 'az vm create', 'gcloud compute instances create'], ['Mumbai location', 'ap-south-1', 'West India / Central India (Pune)', 'asia-south1']])

# ---------- console wireframe (simplified, unbranded)
def wire():
    o = t(320, 16, 'Console “Launch instance” page — simplified wireframe with numbered steps', 10, 'ink', bold=True)
    o += box(14, 28, 612, 300, 'card', rx=10) + box(14, 28, 612, 26, 'blue', rx=10) + t(28, 46, 'EC2  ›  Instances  ›  Launch an instance          Region: Asia Pacific (Mumbai) ▾', 8.4, 'ink', anchor='start', bold=True)
    fields = [('1', 'Name and tags', 'tiffingo-web'), ('2', 'Application and OS image (AMI)', 'Amazon Linux 2023 · 64-bit (x86)'), ('3', 'Instance type', 't3.micro  ·  2 vCPU · 1 GiB'), ('4', 'Key pair (login)', 'tiffingo-key  [Create new key pair]'),
              ('5', 'Network settings', 'Security group: allow HTTP 80 from anywhere · SSH 22 from My IP'), ('6', 'Configure storage', '1 × 8 GiB gp3 root volume'), ('7', 'Advanced details › User data', '#!/bin/bash  dnf install -y nginx …')]
    for i, (n, lab, val) in enumerate(fields):
        y = 64 + i * 34
        o += f'<circle cx="34" cy="{y + 13}" r="10" style="fill:var(--track)"/>' + t(34, y + 17, n, 9, extra=' style="fill:#fff"', bold=True)
        o += t(52, y + 11, lab, 8.4, 'ink', anchor='start', bold=True) + box(52, y + 15, 380, 15, 'card', rx=3) + t(58, y + 26, val, 7.6, 'ink2', anchor='start')
    o += box(460, 64, 150, 120, 'green', rx=8) + t(535, 82, 'Summary', 9, 'ink', bold=True) + t(470, 100, 'Number of instances: 1', 7.6, 'ink', anchor='start') + t(470, 116, 'Image: Amazon Linux 2023', 7.6, 'ink', anchor='start') + t(470, 132, 'Type: t3.micro', 7.6, 'ink', anchor='start')
    o += f'<circle cx="474" cy="160" r="10" style="fill:var(--track)"/>' + t(474, 164, '8', 9, extra=' style="fill:#fff"', bold=True) + box(490, 150, 108, 22, 'acc', rx=11) + t(544, 165, 'Launch instance', 8.4, 'ink', bold=True)
    return o
WIRE = bigfig('Simplified wireframe of a cloud console launch page with eight numbered steps: name and tags, image, instance type, key pair, network settings and security group, storage, user data, and the Launch instance button.', wire(), h=340, caption='Simplified drawing for learning; the real console layout changes over time, the fields stay the same.')
console_map = table(['#', 'Console field', 'CLI option', 'Our value'], [
    ['1', 'Name and tags', '--tag-specifications', 'Name=tiffingo-web, course=cloud-fundamentals'], ['2', 'AMI', '--image-id', 'latest Amazon Linux 2023 (from SSM)'],
    ['3', 'Instance type', '--instance-type', 't3.micro'], ['4', 'Key pair', '--key-name', 'tiffingo-key'], ['5', 'Network settings', '--security-group-ids (and --subnet-id)', 'sg-… (80 open, 22 my IP)'],
    ['6', 'Storage', '--block-device-mappings', 'default 8 GiB gp3'], ['7', 'User data', '--user-data file://userdata.sh', 'installs nginx'], ['8', 'Launch instance', 'aws ec2 run-instances', '—']], minw=600)
CONSOLE = ('  <p>Prefer clicking? The console does exactly what the CLI does. Follow the numbers; the table maps each field to the CLI option you will use in the next section.</p>\n' + WIRE + console_map)

# ---------- hands-on CLI
prac_intro = ('Steps 1–10 launch a web server, check it, stop it and delete everything. Steps 11–16 go deeper: an extra disk, a snapshot, a fixed IP, an IAM role and IMDSv2. <b>About the outputs:</b> they come from a full practice run on <b>moto 5.2.5, an AWS-compatible emulator</b>, using the real <b>AWS CLI 2.39.7</b>. Commands, options and output format are the same as on a real account; IDs, IP addresses and the account number (123456789012) will be different for you. '
              'Set up first: install AWS CLI v2, run <code>aws configure</code> with an IAM user’s keys (never the root user), region <code>ap-south-1</code>, and create a zero-spend budget alert.')
STEPS = [
    ('1 · Check who you are and the region', code('bash', 'terminal', 'aws sts get-caller-identity\naws configure get region', sec('== 1)', '== 2)')), 'Always run this first: it proves which account and user the CLI is using — the commonest cause of “I can’t see my instance” is the wrong account or region.'),
    ('2 · Find the latest Amazon Linux image', code('bash', 'terminal', 'AMI=$(aws ssm get-parameter \\\n  --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64 \\\n  --query Parameter.Value --output text)\necho $AMI', sec('== 2)', '== 3)')), 'AMI IDs differ per region and change with every update; the public SSM parameter always returns the current one for your region.'),
    ('3 · Pick a size', code('bash', 'terminal', "aws ec2 describe-instance-types --instance-types t3.micro t3.medium \\\n  --query 'InstanceTypes[].[InstanceType,VCpuInfo.DefaultVCpus,MemoryInfo.SizeInMiB]' --output table", sec('== 3)', '== 4)')), 't3.micro is enough for a small website and fits student budgets ($0.0112/h in Mumbai).'),
    ('4 · Create a key pair', code('bash', 'terminal', 'aws ec2 create-key-pair --key-name tiffingo-key \\\n  --query KeyMaterial --output text > tiffingo-key.pem\nchmod 400 tiffingo-key.pem', sec('== 4)', '== 5)')), 'AWS keeps only the public key. The private key is shown once — if you lose the .pem file you cannot SSH in. chmod 400 stops SSH complaining about “UNPROTECTED PRIVATE KEY FILE”.'),
    ('5 · Create the firewall (security group)', code('bash', 'terminal', 'SG=$(aws ec2 create-security-group --group-name tiffingo-web \\\n  --description "TiffinGo web server" --query GroupId --output text)\naws ec2 authorize-security-group-ingress --group-id $SG --protocol tcp --port 80 --cidr 0.0.0.0/0\naws ec2 authorize-security-group-ingress --group-id $SG --protocol tcp --port 22 --cidr $(curl -s https://checkip.amazonaws.com)/32', sec('== 5)', '== 6)')), 'Web (80) open to the world; SSH (22) only from your own IP. In our run, 203.0.113.25 is a documentation IP standing in for “my IP”.'),
    ('6 · Launch with a start-up script', code('bash', 'terminal', "cat > userdata.sh <<'EOF'\n#!/bin/bash\ndnf install -y nginx\necho \"<h1>TiffinGo menu - served from EC2 in Mumbai</h1>\" > /usr/share/nginx/html/index.html\nsystemctl enable --now nginx\nEOF\nIID=$(aws ec2 run-instances --image-id $AMI --instance-type t3.micro \\\n  --key-name tiffingo-key --security-group-ids $SG --user-data file://userdata.sh \\\n  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=tiffingo-web},{Key=course,Value=cloud-fundamentals}]' \\\n  --query 'Instances[0].InstanceId' --output text)\necho $IID", sec('== 6)', '== 7)')), 'One API call = the six steps of the first animation. The tags let you find (and bill-track) everything from this course later.'),
    ('7 · Check state, zone and IPs', code('bash', 'terminal', "aws ec2 wait instance-running --instance-ids $IID\naws ec2 describe-instances --instance-ids $IID --query 'Reservations[0].Instances[0].{State:State.Name,Type:InstanceType,Zone:Placement.AvailabilityZone,PrivateIP:PrivateIpAddress,PublicIP:PublicIpAddress,Image:ImageId}' --output table", sec('== 7)', '== 8)')), 'On a real account, wait about a minute for user data, then open http://PUBLIC-IP in a browser or run curl — you should see the “TiffinGo menu” heading.'),
    ('8 · Stop and start', code('bash', 'terminal', 'aws ec2 stop-instances --instance-ids $IID\naws ec2 start-instances --instance-ids $IID', sec('== 8)', '== 9)')), 'Each line shows previous state → new state. While stopped you pay only for the disk; a new public IP is usually given after start.'),
    ('9 · Clean up everything', code('bash', 'terminal', 'aws ec2 terminate-instances --instance-ids $IID\naws ec2 wait instance-terminated --instance-ids $IID\naws ec2 delete-security-group --group-id $SG\naws ec2 delete-key-pair --key-name tiffingo-key\nrm tiffingo-key.pem userdata.sh', sec('== 9)', '== 10)')), 'Terminate first: a security group in use cannot be deleted. The root EBS disk is deleted with the instance.'),
    ('10 · Prove nothing is left', code('bash', 'terminal', "aws ec2 describe-instances --filters Name=instance-state-name,Values=pending,running,stopping,stopped \\\n  --query 'length(Reservations)' --output text", sec('== 10)')), '0 = nothing running or stopped. Do this after every lab; then check Billing → Bills the next day.')]

# ======================= DEEP DIVE =======================
D = 'l21_deep.txt'
def dsec(a, b=None):
    return capsec(D, a, b)

# D1 Nitro
def nitro():
    o = t(320, 16, 'Inside one EC2 host: the AWS Nitro System', 11, 'ink', bold=True)
    o += box(20, 30, 600, 260, 'card', rx=12)
    for i, (n, sub, tn) in enumerate([('Your VM (t3.micro)', 'Amazon Linux', 'blue'), ('Customer B VM', 'Windows', 'green'), ('Customer C VM', 'Ubuntu', 'violet'), ('free capacity', '', 'card')]):
        o += box(40 + i * 146, 44, 132, 60, tn, rx=8) + t(106 + i * 146, 70, n, 8.6, 'ink', bold=True) + t(106 + i * 146, 86, sub, 7.4, 'ink2')
    o += box(40, 116, 570, 34, 'amber', rx=8) + t(325, 137, 'Nitro Hypervisor — very thin (KVM-based): only splits CPU and memory between VMs', 8.6, 'ink', bold=True)
    o += box(40, 162, 400, 50, 'card', rx=8) + t(240, 178, 'Physical server: CPUs, RAM', 8.6, 'ink', bold=True) + t(240, 196, 'vCPU = one hardware thread of a real core', 7.6, 'ink2')
    for i, (n, sub) in enumerate([('Nitro Card: VPC', 'networking + SG'), ('Nitro Card: EBS', 'remote disks, encryption'), ('Nitro Card: storage', 'local NVMe (instance store)')]):
        o += box(40 + i * 192, 224, 180, 50, 'violet', rx=8) + t(130 + i * 192, 244, n, 8.2, 'ink', bold=True) + t(130 + i * 192, 260, sub, 7.4, 'ink2')
    o += box(452, 162, 158, 50, 'red', rx=8) + t(531, 182, 'Nitro Security Chip', 8.2, 'ink', bold=True) + t(531, 198, 'protects firmware', 7.4, 'ink2')
    return o + t(320, 298, 'Networking, storage and security run on dedicated Nitro cards, so almost all of the server’s CPU goes to customer VMs.', 7.8, 'ink2')
NITRO = bigfig('Diagram of one EC2 host: several customers’ VMs on top of a thin Nitro hypervisor, on a physical server with CPUs and RAM; separate Nitro cards handle VPC networking, EBS storage and local NVMe storage; a Nitro security chip protects the firmware.', nitro(), h=308)

# D2 burstable credits animation
def cred_frame(k):
    cpu = [5, 5, 60, 60, 10][k]; cred = [144, 156, 110, 20, 0][k]
    o = t(180, 12, 't3.micro: CPU credits (baseline 10% per vCPU)', 8.6, 'ink', bold=True)
    o += t(60, 32, 'CPU use', 7.6, 'ink2') + box(30, 40, 60, 100, 'card', rx=4) + box(30, 140 - cpu, 60, cpu, 'red' if cpu > 10 else 'green', rx=2) + t(60, 136 - cpu, f'{cpu}%', 8, 'ink', bold=True)
    o += f'<line x1="26" y1="130" x2="94" y2="130" style="stroke:#E0A100;stroke-dasharray:3 2;stroke-width:1.6"/>' + t(98, 133, 'baseline 10%', 6.8, 'amber', anchor='start')
    o += t(250, 32, 'credit balance (max 288)', 7.6, 'ink2') + box(190, 40, 120, 100, 'card', rx=4) + box(190, 140 - cred / 2.88, 120, cred / 2.88, 'blue', rx=2) + t(250, 136 - cred / 2.88 - 2, str(cred), 8.4, 'ink', bold=True)
    return o
CR = [('Quiet night', 'CPU below 10%: the instance earns 12 credits per hour.', 'One credit = one vCPU at 100% for one minute'),
      ('Credits pile up', 'Unused credits accumulate up to 288 (24 hours of earning).', 'Like a prepaid balance for bursts'),
      ('Lunch rush: burst', 'CPU jumps to 60%: credits are spent faster than earned.', 'The site stays fast thanks to the saved credits'),
      ('Credits running low', 'A long burst drains the balance.', 'Watch the CloudWatch metric CPUCreditBalance'),
      ('Credits = 0', 'Standard mode: throttled to 10%. Unlimited (T3 default): keeps bursting, small extra charge.', 'Steady high CPU? Choose an m or c instance instead of t')]
fr = [cred_frame(k) + box(6, 158, 348, 62, 'blue', rx=8) + t(14, 174, h, 9, 'ink', anchor='start', bold=True) + t(14, 190, a, 7.4, 'ink', anchor='start') + t(14, 206, b, 7.2, 'ink2', anchor='start') for k, (h, a, b) in enumerate(CR)]
CREDITS = anim_one('How it works', 'Burstable instances and CPU credits', 'Why a cheap t3.micro is fast for a small website but slow for heavy jobs.', 'CPU credits', 'Animation of a t3.micro earning CPU credits when idle, spending them during a burst, and being throttled or charged extra when credits run out.', fr, ['Earn.', 'Save.', 'Burst.', 'Drain.', 'Empty.'], delay=5500, hid='credits')

# D3 storage tables
STOR = table(['', 'EBS volume', 'Instance store'], [
    ['What it is', 'network disk attached through the Nitro EBS card', 'NVMe disk physically inside the host'],
    ['Survives stop / start', 'yes', 'no — data is lost on stop or host failure'],
    ['Survives terminate', 'root: no (default); extra volumes: yes unless set', 'no'],
    ['Lives in', 'one Availability Zone, replicated inside it', 'that one host'],
    ['Backup', 'snapshots (incremental, stored by AWS, copy to other regions)', 'you must copy data elsewhere'],
    ['Use for', 'OS, databases, anything you must keep', 'cache, scratch space, temporary data']], minw=600) + \
    '\n  <p>EBS volume types (choose by IOPS = operations per second, and MB/s):</p>\n' + table(['Type', 'Kind', 'Performance', 'Use for'], [
    ['gp3 (default)', 'SSD, general purpose', '3,000 IOPS and 125 MB/s included; up to 16,000 IOPS / 1,000 MB/s', 'boot disks, most apps'],
    ['io2 Block Express', 'SSD, provisioned IOPS', 'up to 256,000 IOPS, very low latency', 'big critical databases'],
    ['st1', 'HDD, throughput optimised', 'high MB/s, low IOPS', 'logs, big sequential data (Kafka, Hadoop)'],
    ['sc1', 'HDD, cold', 'cheapest, slowest', 'rarely read archives']], minw=600)

# D4 network path animation (stateful vs stateless)
NN = {'user': (4, 54, 50, 50, 'phone', 'User', 'internet'), 'igw': (62, 54, 52, 50, 'globe', 'Internet', 'gateway'), 'rt': (122, 54, 52, 50, 'dns', 'Route', 'table'),
      'nacl': (182, 54, 52, 50, 'shield', 'NACL', 'subnet'), 'sg': (242, 54, 52, 50, 'shield', 'Security', 'group'), 'vm': (302, 54, 52, 50, 'server', 'EC2', ':80')}
NS = [dict(on=['user', 'igw'], hot='igw', move=(54, 79, 64, 79, ''), head='Step 1 · Request reaches the VPC', text='The browser sends HTTP to the Elastic/public IP. The internet gateway', text2='translates the public IP to the instance’s private IP (10.0.1.x).', svc='AWS internet gateway · Azure public IP · Google external IP'),
      dict(on=['user', 'igw', 'rt'], hot='rt', move=(114, 79, 124, 79, ''), head='Step 2 · Route table', text='The subnet’s route table says where packets go: 0.0.0.0/0 → internet', text2='gateway makes this a public subnet.', svc='Route tables in VPC / VNet / Google VPC routes'),
      dict(on=['user', 'igw', 'rt', 'nacl'], hot='nacl', move=(174, 79, 184, 79, 'rule #100'), head='Step 3 · Network ACL (subnet firewall, stateless)', text='Rules checked in number order for the whole subnet. Stateless: the', text2='reply must be allowed separately (outbound ports 1024–65535).', svc='Default NACL allows everything; custom ones need both directions'),
      dict(on=list(NN)[:5], hot='sg', move=(234, 79, 244, 79, 'allow 80'), head='Step 4 · Security group (instance firewall, stateful)', text='Only allow rules. Stateful: if inbound 80 is allowed, the reply', text2='goes out automatically — no outbound rule needed.', svc='AWS security group · Azure NSG (on NIC/subnet) · Google firewall rule'),
      dict(on=list(NN), hot='vm', move=(294, 79, 304, 79, 'GET /'), head='Step 5 · nginx answers', text='The packet reaches the network interface (ENI) of the instance;', text2='nginx replies and the response returns the same way.', svc='The ENI keeps its private IP for the life of the instance')]
NETA = flow_anim('How a web request enters your VPC', 'Five checkpoints between a browser and nginx. Knowing them is how you debug “site not loading”.', 'VPC path', 'Animation of a request passing internet gateway, route table, network ACL, security group and reaching the EC2 instance.', NN, NS, hid='netpath')
IPS = table(['Address', 'Example', 'Changes?', 'Billed?'], [
    ['Private IPv4', '10.0.1.25', 'kept for the instance’s life', 'free'],
    ['Auto public IPv4', '13.x.x.x', 'new one after every stop/start', '$0.005/hour while assigned'],
    ['Elastic IP', 'fixed 13.x.x.x', 'never, until you release it', '$0.005/hour, attached or not'],
    ['IPv6', '2406:da1a:…', 'kept', 'free']], minw=560)

# D5 role + IMDSv2 animation
MN = {'app': (6, 54, 64, 52, 'app', 'Your app', 'on EC2'), 'imds': (98, 6, 76, 52, 'dns', 'Metadata', '169.254.169.254'), 'sts': (98, 104, 76, 52, 'shield', 'IAM / STS', 'temp creds'),
      'role': (204, 104, 70, 52, 'user', 'IAM role', 'S3 read-only'), 's3': (290, 54, 64, 52, 'disk', 'S3 bucket', 'menu files')}
MS = [dict(on=['app', 'imds'], hot='imds', move=(70, 70, 100, 36, 'PUT token'), head='Step 1 · Ask for a session token (IMDSv2)', text='curl -X PUT http://169.254.169.254/latest/api/token', text2='-H "X-aws-ec2-metadata-token-ttl-seconds: 21600"', svc='This link-local address works only from inside the instance'),
      dict(on=['app', 'imds', 'sts', 'role'], hot='sts', move=(136, 58, 136, 104, 'creds?'), head='Step 2 · Get the role’s temporary credentials', text='GET …/latest/meta-data/iam/security-credentials/tiffingo-web-role', text2='with the token header. STS gives keys valid for a few hours, auto-renewed.', svc='Instance profile = the box that carries the role to EC2'),
      dict(on=list(MN), hot='s3', move=(70, 82, 292, 80, 'read'), head='Step 3 · The app calls S3', text='The AWS SDK/CLI on the instance finds the credentials by itself:', text2='aws s3 ls s3://tiffingo-menu works with no keys stored anywhere.', svc='Azure: managed identity · Google: service account attached to the VM'),
      dict(on=list(MN), hot='role', move=(274, 130, 300, 106, 'deny'), head='Step 4 · Least privilege in action', text='The role allows only S3 read. A write or a call to EC2 is denied,', text2='so a hacked web app cannot delete data or launch servers.', svc='Never put access keys in code or on the server')]
META_A = flow_anim('How a server gets permissions without passwords', 'The secure way for code on EC2 to call other AWS services: an IAM role, delivered through the instance metadata service.', 'IAM role + IMDSv2', 'Animation: app gets a token from the metadata service, gets temporary credentials for its IAM role, calls S3, and is denied anything outside the role.', MN, MS, hid='imds')

CONNECT = table(['Method', 'Needs port 22 open?', 'Needs a key file?', 'Best for'], [
    ['SSH with key pair', 'yes (from your IP)', 'yes (.pem)', 'learning, quick admin'],
    ['EC2 Instance Connect', 'yes (from AWS’s range or yours)', 'no — a one-time key is pushed for 60 s', 'browser login without managing keys'],
    ['Session Manager (Systems Manager)', 'no', 'no — uses an IAM role + agent', 'production: no open ports, every session logged'],
    ['Serial console', 'no', 'needs a password user', 'rescue when networking is broken']], minw=600)
PRICING = table(['Option', 'Discount vs On-Demand', 'Commitment', 'Use when'], [
    ['On-Demand', '—', 'none, per second', 'labs, new or unpredictable workloads'],
    ['Savings Plans', 'up to 72%', '$ per hour for 1 or 3 years', 'steady usage, flexible across instance types'],
    ['Reserved Instances', 'up to 72%', '1 or 3 years for a type/region', 'steady, known instance type'],
    ['Spot Instances', 'up to 90%', 'none — AWS can take it back with 2 minutes’ notice', 'batch jobs, Spark/EMR workers, CI, rendering'],
    ['Dedicated Hosts', 'costlier', 'per host', 'per-core licences, compliance'],
    ['Capacity Reservations', 'none (on-demand price)', 'reserve capacity in an AZ', 'guarantee capacity for an event']], minw=620)
PLACE = cards([('Cluster placement group', 'Instances packed close together in one AZ for the lowest network latency.', 'HPC, tightly coupled jobs'),
    ('Spread placement group', 'Each instance on different hardware (max 7 per AZ per group).', 'a few critical servers'),
    ('Partition placement group', 'Groups of instances on separate racks.', 'Hadoop, Kafka, Cassandra')])
OTHERS = table(['Provider', 'IaaS VM service', 'Note'], [
    ['AWS', 'EC2', 'largest choice of instance types'], ['Microsoft Azure', 'Virtual Machines', 'strong for Windows / Microsoft licences'], ['Google Cloud', 'Compute Engine', 'per-second billing, sustained-use discounts'],
    ['Oracle Cloud', 'Compute', 'Oracle databases, generous free tier'], ['DigitalOcean, Linode (Akamai)', 'Droplets / Linodes', 'simple VMs for developers'],
    ['Indian providers', 'Yotta, CtrlS, ESDS, Sify, others', 'local data centres; many empanelled for government under MeghRaj']], minw=600)
PROSCONS = cards([('IaaS strengths', 'Full control of OS and software; any language or legacy app; lift-and-shift migrations; pay per second; scale in minutes.', 'flexibility'),
    ('IaaS weaknesses', 'You still patch, secure, back up and monitor the OS; more work than PaaS/SaaS; misconfiguration risk.', 'responsibility'),
    ('Choose IaaS when', 'You need a custom OS setup, special software, full control, or are moving existing servers quickly (rehost).', 'decision')])

DEEP = ('  <p>Everything above lets you <b>use</b> IaaS. This section explains what is happening <b>underneath</b>, so you can design, troubleshoot and answer deeper interview questions.</p>\n'
    '  <h3>1. Inside the physical host</h3>\n  <p>A vCPU in EC2 is one hardware thread of a real CPU core. AWS runs a very thin hypervisor and moves networking, storage and security onto separate cards — this is why your VM gets nearly bare-metal speed and why one customer cannot reach another’s memory.</p>\n' + NITRO +
    '\n  <p>Each piece of the Nitro System, explained:</p>\n' + wwu([
    ('Nitro Card for VPC', 'A PCIe card that does all VPC networking for the host: the virtual switch, security-group checks, route lookups, and wrapping each packet with your VPC’s ID before it crosses the physical network. Your instance sees it as an ENA network adapter.', 'In older clouds this ran as software in the hypervisor and used CPU you paid for, adding jitter. In hardware it is faster (up to 100–200 Gbps) and the rules sit outside your VM, so even a hacked OS cannot switch off its security group.', 'Every Nitro instance (all current families). Every packet you send passes through it — Lesson 4.3 follows one step by step.'),
    ('Nitro Card for EBS', 'A card that turns remote EBS storage into an NVMe disk inside the instance and encrypts data on the way.', 'The disk lives on storage servers elsewhere in the AZ; the VM must still see a fast local-looking disk, and encryption must not cost VM CPU.', 'Every EBS volume on Nitro instances appears as <code>/dev/nvme…</code>.'),
    ('Nitro Card for instance storage', 'Controls the NVMe SSDs physically inside the host and encrypts them.', 'Very fast scratch disk for caches and temp data.', 'Instance types with “d” (m6id, c6gd…) and storage-optimized i4i; data is lost on stop/terminate.'),
    ('Nitro Controller', 'The card that manages the whole host: it talks to the EC2 control plane, starts and stops VMs, and holds the root of trust.', 'Management must not run on the same CPUs as customers, and AWS staff must have no path into customer memory.', 'Every Nitro host; it is why there is no operator SSH access to the hypervisor.'),
    ('Nitro Hypervisor', 'A thin KVM-based layer that only assigns CPU and memory to VMs; all I/O is done by the cards.', 'Less code means fewer bugs, less overhead and fewer reboots for updates.', 'All virtualized Nitro instances; bare-metal (.metal) instances skip it but still use the cards.'),
    ('Nitro Security Chip', 'A chip on the motherboard that checks and protects the host’s firmware.', 'Stops tampering below the hypervisor (the hyperjacking risk in Lesson 4.6).', 'Every Nitro host.')]) +
    '\n  <h3>2. Burstable CPU (the “t” family)</h3>\n' + CREDITS +
    '\n  <h3>3. Storage: EBS vs instance store</h3>\n' + STOR + '\n  <p>EBS volumes live in <b>one Availability Zone</b>: you can attach a volume only to an instance in the same AZ. To move data to another AZ or region, take a <b>snapshot</b> and create a new volume from it.</p>\n' +
    '\n  <h3>4. Networking: from the internet to your instance</h3>\n' + NETA + '\n  <p>Public addresses and what they cost:</p>\n' + IPS +
    '\n  <h3>5. Permissions on the server: IAM roles and the metadata service</h3>\n' + META_A + '\n' + caution('Require <b>IMDSv2</b> (token-based) on every instance. With the old IMDSv1, a bug in a web app (server-side request forgery) could read the role’s credentials. New AL2023 launches use IMDSv2 by default; check with <code>describe-instances</code>.') +
    '\n  <h3>6. Four ways to log in</h3>\n' + CONNECT +
    '\n  <h3>7. Pricing models in depth</h3>\n' + PRICING + '\n  <p>Example: a t3.micro web server in Mumbai at $0.0112/h costs ≈ $8.18 for a full month On-Demand. The same steady server under a 3-year commitment costs much less, while a nightly 1-hour Spark job on Spot workers can cost a fraction of On-Demand — if your job can survive interruptions.</p>\n' +
    '\n  <h3>8. Placement groups and tenancy</h3>\n' + PLACE + '\n  <p><b>Tenancy:</b> default (shared hardware), <b>dedicated instance</b> (hardware used only by your account), <b>dedicated host</b> (you see and control the physical server — needed for some per-core licences).</p>\n' +
    '\n  <h3>9. Limits and health</h3>\n  <ul><li><b>Quotas:</b> each account has a vCPU limit per instance family per region (“Running On-Demand Standard instances”). A new account may hit it; request an increase in Service Quotas.</li><li><b>Status checks:</b> <i>system</i> check (AWS hardware/network — fix by stop/start to move hosts) and <i>instance</i> check (your OS — fix inside the VM); newer instances also have an attached EBS check.</li><li><b>Monitoring:</b> CloudWatch collects CPU, network and disk metrics every 5 minutes by default (1 minute with detailed monitoring). Memory and disk-space metrics need the CloudWatch agent.</li></ul>\n' +
    '\n  <h3>10. IaaS in the market, strengths and weaknesses</h3>\n' + OTHERS + PROSCONS)

DEEP_STEPS = [
    ('11 · Add a 20 GiB gp3 data disk', code('bash', 'terminal', 'VOL=$(aws ec2 create-volume --availability-zone ap-south-1a --size 20 \\\n  --volume-type gp3 --iops 3000 --throughput 125 --query VolumeId --output text)\naws ec2 attach-volume --volume-id $VOL --instance-id $IID --device /dev/sdf', dsec('== A)', '== B)')), 'Same AZ as the instance. Inside Linux it appears as an NVMe device (lsblk); format with <code>sudo mkfs -t xfs</code> and mount it.'),
    ('12 · Back it up with a snapshot', code('bash', 'terminal', 'SNAP=$(aws ec2 create-snapshot --volume-id $VOL --description "tiffingo data backup" --query SnapshotId --output text)\naws ec2 describe-snapshots --snapshot-ids $SNAP', dsec('== B)', '== C)')), 'Snapshots are incremental: only changed blocks are stored after the first one.'),
    ('13 · A fixed public IP (Elastic IP)', code('bash', 'terminal', 'ALLOC=$(aws ec2 allocate-address --domain vpc --query AllocationId --output text)\naws ec2 associate-address --instance-id $IID --allocation-id $ALLOC', dsec('== C)', '== D)')), 'The address stays the same across stop/start — useful for DNS. Billed whether attached or not.'),
    ('14 · Permissions with an IAM role', code('bash', 'terminal', 'aws iam create-role --role-name tiffingo-web-role --assume-role-policy-document file://trust.json\naws iam attach-role-policy --role-name tiffingo-web-role \\\n  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess\naws iam create-instance-profile --instance-profile-name tiffingo-web-profile\naws iam add-role-to-instance-profile --instance-profile-name tiffingo-web-profile --role-name tiffingo-web-role\naws ec2 associate-iam-instance-profile --instance-id $IID --iam-instance-profile Name=tiffingo-web-profile', dsec('== D)', '== E)')), 'trust.json lets the EC2 service assume the role. On the instance, <code>aws s3 ls</code> now works with no keys (animation in the deep dive).'),
    ('15 · Enforce IMDSv2', code('bash', 'terminal', 'aws ec2 modify-instance-metadata-options --instance-id $IID --http-tokens required --http-endpoint enabled', dsec('== E)', '== F)')), 'Token required = IMDSv2 only.'),
    ('16 · Clean up in the right order', code('bash', 'terminal', 'aws ec2 disassociate-address --association-id <eipassoc-id>; aws ec2 release-address --allocation-id $ALLOC\naws ec2 terminate-instances --instance-ids $IID; aws ec2 wait instance-terminated --instance-ids $IID\naws ec2 delete-volume --volume-id $VOL; aws ec2 delete-snapshot --snapshot-id $SNAP\n# remove role from profile, delete profile, detach policy, delete role', dsec('== F)')), 'Elastic IPs and snapshots are the two things students most often forget — they keep billing silently.')]

# ================================================================== own-account practical (v4)
MOCKQ.extend([
 (mock('aws', ['EC2', 'Instance types'], ['Instances', 'Instance types', 'Launch templates', 'AMIs', 'Key Pairs'], 'Instance types',
       [('Filter', 'Free tier eligible = true'), ('t3.micro', '2 vCPU · 1 GiB · Up to 5 Gigabit'), ('t4g.micro', '2 vCPU · 1 GiB · ARM (Graviton)')], 'Launch instance'),
  mock('az', ['Home', 'Virtual machines', 'Create', 'Select a VM size'], ['All sizes', 'B-series', 'D-series', 'E-series', 'F-series'], 'B-series',
       [('Search', 'B1s'), ('Standard_B1s', '1 vCPU · 1 GiB · burstable'), ('Standard_B2ats_v2', '2 vCPU · 1 GiB · burstable (AMD)')], 'Select'),
  mock('gcp', ['Compute Engine', 'Create an instance', 'Machine configuration'], ['General purpose', 'Compute optimized', 'Memory optimized', 'Storage optimized', 'GPUs'], 'General purpose',
       [('Series', '▾ E2'), ('Machine type', '▾ e2-micro (2 vCPU, 1 core, 1 GB memory)'), ('Region', '▾ asia-south1 (Mumbai)')], 'Create')),
 (mock('aws', ['EC2', 'Instances', 'Launch an instance'], ['Dashboard', 'Instances', 'AMIs', 'Security Groups', 'Key Pairs'], 'Instances',
       [('Name', 'tiffingo-iaas'), ('AMI', '▾ Amazon Linux 2023 AMI'), ('Instance type', '▾ t3.micro'), ('Key pair (login)', '▾ tiffingo-key  (Create new key pair)'), ('Network settings', '[x] Allow SSH traffic from  My IP')], 'Launch instance'),
  mock('az', ['Home', 'Virtual machines', 'Create a virtual machine'], ['Basics', 'Disks', 'Networking', 'Management', 'Review + create'], 'Basics',
       [('Resource group', '▾ (New) rg-iaas'), ('Name', 'tiffingo-iaas'), ('Image', '▾ Ubuntu Server 24.04 LTS'), ('Authentication type', '[x] SSH public key'), ('Public inbound ports', '▾ SSH (22)')], 'Review + create'),
  mock('gcp', ['Compute Engine', 'VM instances', 'Create an instance'], ['Machine configuration', 'OS and storage', 'Networking', 'Security'], 'Machine configuration',
       [('Name', 'tiffingo-iaas'), ('Zone', '▾ asia-south1-a'), ('Machine type', '▾ e2-micro'), ('OS and storage', 'Debian GNU/Linux 12 (bookworm)')], 'Create')),
 (mock('aws', ['EC2', 'Instances', 'Connect to instance'], ['EC2 Instance Connect', 'Session Manager', 'SSH client', 'EC2 serial console'], 'EC2 Instance Connect',
       [('Username', 'ec2-user'), ('Terminal', '$ sudo dnf upgrade -y   →  Complete!')], 'Connect'),
  mock('az', ['Home', 'Virtual machines', 'tiffingo-iaas', 'Updates'], ['Overview', 'Connect', 'Updates', 'Run command', 'Disks'], 'Updates',
       [('Pending updates', 'Security · Critical · Other'), ('Action', 'One-time update  /  Check for updates')], 'One-time update'),
  mock('gcp', ['Compute Engine', 'VM instances', 'SSH-in-browser'], ['VM instances', 'OS patch management', 'Snapshots'], 'VM instances',
       [('tiffingo-iaas', 'Connect: SSH ▾'), ('Terminal', '$ sudo apt-get upgrade -y  →  0 upgraded … done')], 'SSH')),
 (mock('aws', ['EC2', 'Volumes'], ['Instances', 'Volumes', 'Snapshots', 'Elastic IPs'], 'Volumes',
       [('Instance state', 'Stopped'), ('Volume vol-0… · 8 GiB gp3', 'In-use (still billed)'), ('Public IPv4', 'released on stop')], 'Start instance'),
  mock('az', ['Home', 'Virtual machines', 'tiffingo-iaas', 'Overview'], ['Overview', 'Disks', 'Networking', 'Size'], 'Overview',
       [('Status', 'Stopped (deallocated)'), ('OS disk', 'tiffingo-iaas_OsDisk… · still billed'), ('Note', '“Stopped” inside the OS ≠ deallocated')], 'Start'),
  mock('gcp', ['Compute Engine', 'Disks'], ['VM instances', 'Disks', 'Snapshots', 'Images'], 'Disks',
       [('VM status', 'TERMINATED (stopped)'), ('Disk tiffingo-iaas · 10 GB balanced', 'In use by tiffingo-iaas · billed')], 'Start / Resume')),
 (mock('aws', ['EC2', 'Snapshots', 'Create snapshot'], ['Volumes', 'Snapshots', 'Lifecycle Manager'], 'Snapshots',
       [('Resource type', '[x] Volume'), ('Volume ID', '▾ vol-0… (tiffingo-iaas root)'), ('Description', 'before-upgrade')], 'Create snapshot'),
  mock('az', ['Home', 'Snapshots', 'Create snapshot'], ['Basics', 'Encryption', 'Networking', 'Tags'], 'Basics',
       [('Resource group', '▾ rg-iaas'), ('Name', 'tiffingo-iaas-snap'), ('Source disk', '▾ tiffingo-iaas_OsDisk…'), ('Snapshot type', '[x] Incremental')], 'Review + create'),
  mock('gcp', ['Compute Engine', 'Snapshots', 'Create a snapshot'], ['Disks', 'Snapshots', 'Snapshot schedules'], 'Snapshots',
       [('Name', 'tiffingo-iaas-snap'), ('Source disk', '▾ tiffingo-iaas'), ('Location', '▾ Multi-regional (asia)')], 'Create')),
])

STEP1 = ('1 · Find a size and an image', tri(
    (['[[EC2]] → [[Instance types]] → filter [[Free tier eligible]] = true; compare vCPU, memory and network.', '[[AMIs]] → [[Public images]] → search “al2023” to see Amazon Linux images.'],
     "aws ec2 describe-instance-types --filters Name=free-tier-eligible,Values=true \\\n  --query 'InstanceTypes[].[InstanceType,VCpuInfo.DefaultVCpus,MemoryInfo.SizeInMiB]' --output table\naws ssm get-parameter --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \\\n  --query Parameter.Value --output text",
     'a short table such as t3.micro 2 / 1024 and t4g.micro 2 / 1024, then the current Amazon Linux 2023 AMI ID for your Region (<code>ami-…</code>).'),
    (['[[Virtual machines]] → [[Create]] → [[See all sizes]] → filter by family (B, D, E, F…) and compare.'],
     'az vm list-sizes --location centralindia --query "[?starts_with(name,\'Standard_B\')].{size:name,vcpu:numberOfCores,mem_mb:memoryInMB}" --output table\naz vm image list --publisher Canonical --offer ubuntu-24_04-lts --sku server --location centralindia --all --query "[-1].urn" --output tsv',
     'B-series sizes with cores and memory, then the newest Ubuntu 24.04 image URN.'),
    (['[[Compute Engine]] → [[Create instance]] → [[Machine configuration]] → browse General purpose / Compute / Memory / Storage optimized / GPUs tabs.'],
     'gcloud compute machine-types list --zones=asia-south1-a --filter="name~^e2-(micro|small|medium)$"\ngcloud compute images describe-from-family debian-12 --project=debian-cloud --format="value(name)"',
     'e2-micro, e2-small, e2-medium with CPUs and memory, then a Debian 12 image name.')),
    'The family letter (Types section) tells you the purpose; the size tells you how much.')

STEP2 = ('2 · Launch a VM that only you can log into', tri(
    (['[[Launch instances]] → name <code>tiffingo-iaas</code>, Amazon Linux 2023, t3.micro.', 'Key pair → [[Create new key pair]] <code>tiffingo-key</code> (.pem) — the browser downloads it once.', 'Network settings → [[Allow SSH traffic from]] [[My IP]] (never Anywhere) → [[Launch instance]].'],
     "aws ec2 create-key-pair --key-name tiffingo-key --query KeyMaterial --output text > tiffingo-key.pem && chmod 400 tiffingo-key.pem\nSG=$(aws ec2 create-security-group --group-name tiffingo-ssh --description \"SSH from my IP\" --query GroupId --output text)\naws ec2 authorize-security-group-ingress --group-id $SG --protocol tcp --port 22 --cidr $(curl -s https://checkip.amazonaws.com)/32\nIID=$(aws ec2 run-instances --instance-type t3.micro --key-name tiffingo-key --security-group-ids $SG \\\n  --image-id resolve:ssm:/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \\\n  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=tiffingo-iaas}]' --query 'Instances[0].InstanceId' --output text)\naws ec2 wait instance-running --instance-ids $IID\nIP=$(aws ec2 describe-instances --instance-ids $IID --query 'Reservations[0].Instances[0].PublicIpAddress' --output text); echo $IP",
     'an instance ID <code>i-…</code>, state running, and a public IP. In CloudShell, <code>checkip</code> returns CloudShell’s IP — run this step from your laptop terminal, or use EC2 Instance Connect in step 3.'),
    (['[[Create a virtual machine]]: resource group <code>rg-iaas</code>, name <code>tiffingo-iaas</code>, Central India, Ubuntu Server 24.04 LTS, Standard_B1s.', 'Authentication: [[SSH public key]] → [[Generate new key pair]]; inbound ports [[SSH (22)]].', '[[Review + create]] → [[Create]] → [[Download private key and create resource]].'],
     'az group create --name rg-iaas --location centralindia\naz vm create --resource-group rg-iaas --name tiffingo-iaas --image Ubuntu2404 --size Standard_B1s \\\n  --admin-username azureuser --generate-ssh-keys --public-ip-sku Standard\nIP=$(az vm show --show-details -g rg-iaas -n tiffingo-iaas --query publicIps -o tsv); echo $IP',
     'JSON with <code>"powerState": "VM running"</code> and <code>publicIpAddress</code>; your SSH key is saved in <code>~/.ssh/</code>. <code>az vm create</code> opens port 22 by default — restrict it to your IP in the NSG for anything beyond a lab.'),
    (['[[Create instance]]: name <code>tiffingo-iaas</code>, asia-south1-a, e2-micro, [[OS and storage]] Debian 12 → [[Create]].', 'Google manages SSH keys for you (OS Login / metadata keys) when you click [[SSH]].'],
     'gcloud compute instances create tiffingo-iaas --zone=asia-south1-a --machine-type=e2-micro \\\n  --image-family=debian-12 --image-project=debian-cloud\ngcloud compute instances list --filter="name=tiffingo-iaas"',
     'a row with STATUS <b>RUNNING</b>, internal and external IPs. The default network’s <code>default-allow-ssh</code> rule allows port 22; tighten it for real work.')),
    'In IaaS the login keys and the firewall are your responsibility — the provider never sees your private key.')

STEP3 = ('3 · Log in and patch the OS yourself', tri(
    (['Select the instance → [[Connect]] → [[EC2 Instance Connect]] → [[Connect]] (or SSH from your laptop).', 'Run <code>sudo dnf upgrade -y</code>, then <code>sudo dnf install -y nginx &amp;&amp; sudo systemctl enable --now nginx</code>.'],
     'ssh -i tiffingo-key.pem ec2-user@$IP "sudo dnf upgrade -y && sudo dnf install -y nginx && sudo systemctl enable --now nginx && systemctl is-active nginx"',
     'dnf prints the packages it updated (or “Nothing to do”), ends with <code>Complete!</code>, then <code>active</code>. Patching the guest OS is <b>your</b> job in IaaS — AWS patches only the hardware and hypervisor.'),
    (['VM → [[Updates]] (Update Manager) → [[Check for updates]] → [[One-time update]] — or [[Connect]] → [[SSH]].', 'Inside: <code>sudo apt-get update &amp;&amp; sudo apt-get upgrade -y</code>.'],
     'ssh azureuser@$IP "sudo apt-get update && sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y && sudo apt-get install -y nginx && systemctl is-active nginx"',
     'apt lists upgraded packages, then <code>active</code>. Azure Update Manager can schedule this, but deciding and testing patches is still yours.'),
    (['[[VM instances]] → [[SSH]] next to the VM — a browser terminal opens.', 'Run <code>sudo apt-get update &amp;&amp; sudo apt-get upgrade -y</code>. (Optional: [[VM Manager]] → [[OS patch management]] for scheduled patching.)'],
     'gcloud compute ssh tiffingo-iaas --zone=asia-south1-a \\\n  --command="sudo apt-get update && sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y && sudo apt-get install -y nginx && systemctl is-active nginx"',
     'the first run creates an SSH key for you; apt output; then <code>active</code>.')),
    'This is the line that separates IaaS from PaaS: on PaaS the provider would have patched the OS for you (Lesson 2.2).')

STEP4 = ('4 · Stop it and see what is still billed', tri(
    (['[[Instance state]] → [[Stop instance]]. Then [[Volumes]]: the root volume is still “In-use” — and billed.'],
     "aws ec2 stop-instances --instance-ids $IID\naws ec2 wait instance-stopped --instance-ids $IID\naws ec2 describe-volumes --filters Name=attachment.instance-id,Values=$IID \\\n  --query 'Volumes[].[VolumeId,Size,VolumeType,State]' --output table",
     '<code>running → stopping</code>, then a row like <code>vol-… 8 gp3 in-use</code>. Compute billing stopped; the 8 GiB disk (~$0.7/month in Mumbai) did not.'),
    (['VM → [[Stop]] (this deallocates it). [[Disks]] still shows the OS disk.', 'Shutting down from inside Linux leaves it “Stopped” but <b>still allocated and billed for compute</b> — always stop from the portal/CLI.'],
     'az vm deallocate -g rg-iaas -n tiffingo-iaas\naz vm get-instance-view -g rg-iaas -n tiffingo-iaas --query "instanceView.statuses[1].displayStatus" -o tsv\naz disk list -g rg-iaas --query "[].{disk:name,gb:diskSizeGb,state:diskState}" -o table',
     '<code>VM deallocated</code>, and the OS disk with state <code>Reserved</code> (attached, still billed).'),
    (['[[VM instances]] → ⋮ → [[Stop]]. [[Disks]] still lists the boot disk “In use by tiffingo-iaas”.'],
     'gcloud compute instances stop tiffingo-iaas --zone=asia-south1-a\ngcloud compute instances describe tiffingo-iaas --zone=asia-south1-a --format="value(status)"\ngcloud compute disks list --filter="name=tiffingo-iaas" --format="table(name,sizeGb,type.basename(),status)"',
     '<code>TERMINATED</code> (Google’s word for stopped) and the 10 GB disk with status <code>READY</code> — still billed.')),
    'Stopped ≠ free. Disks, snapshots and reserved IPs bill until you delete them.')

STEP5 = ('5 · Back up the disk with a snapshot', tri(
    (['[[Volumes]] → select the root volume → [[Actions]] → [[Create snapshot]] → description <code>before-upgrade</code>.'],
     "VOL=$(aws ec2 describe-volumes --filters Name=attachment.instance-id,Values=$IID --query 'Volumes[0].VolumeId' --output text)\nSNAP=$(aws ec2 create-snapshot --volume-id $VOL --description before-upgrade --query SnapshotId --output text)\naws ec2 wait snapshot-completed --snapshot-ids $SNAP\naws ec2 describe-snapshots --snapshot-ids $SNAP --query 'Snapshots[0].[SnapshotId,State,VolumeSize]' --output text",
     '<code>snap-… completed 8</code>. Snapshots are incremental and stored regionally (across AZs).'),
    (['[[Snapshots]] → [[Create]] → source disk = the VM’s OS disk, type [[Incremental]] → [[Review + create]].'],
     'DISK=$(az vm show -g rg-iaas -n tiffingo-iaas --query storageProfile.osDisk.managedDisk.id -o tsv)\naz snapshot create -g rg-iaas -n tiffingo-iaas-snap --source $DISK --incremental true\naz snapshot list -g rg-iaas --query "[].{name:name,gb:diskSizeGb,state:provisioningState}" -o table',
     'a snapshot row with <code>Succeeded</code>.'),
    (['[[Disks]] → the boot disk → [[Create snapshot]] → name <code>tiffingo-iaas-snap</code> → [[Create]].'],
     'gcloud compute snapshots create tiffingo-iaas-snap --source-disk=tiffingo-iaas --source-disk-zone=asia-south1-a\ngcloud compute snapshots list --filter="name=tiffingo-iaas-snap" --format="table(name,diskSizeGb,status)"',
     '<code>tiffingo-iaas-snap 10 READY</code>.')),
    'Backups of a VM are your responsibility in IaaS — the provider keeps the disk durable, not your history of changes.')

AWS_EXTRA = [(s[0].replace(s[0].split(' · ')[0], 'AWS extra ' + 'ABCDEF'[i]), s[1], s[2]) for i, s in enumerate(DEEP_STEPS[:5])]
prac_intro = (OWN_INTRO + ' Steps 1–5 work in all three clouds. The optional <b>AWS extra</b> steps after them (data disk, snapshot, Elastic IP, IAM role, IMDSv2) show outputs from a practice run on <b>moto</b>, an AWS-compatible emulator, with the real AWS CLI — IDs will differ on your account; start the instance again before them (<code>aws ec2 start-instances --instance-ids $IID</code>).')
prac = practical(prac_intro, [SETUP_STEP, STEP1, STEP2, STEP3, STEP4, STEP5] + AWS_EXTRA,
    cleanup='<b>AWS:</b> <code>aws ec2 terminate-instances --instance-ids $IID</code>; wait; <code>aws ec2 delete-snapshot --snapshot-id $SNAP</code>; <code>aws ec2 delete-security-group --group-id $SG</code>; <code>aws ec2 delete-key-pair --key-name tiffingo-key</code> (and release any Elastic IP, delete extra volumes/snapshots, the role and instance profile if you did the extras). '
            '<b>Azure:</b> <code>az group delete --name rg-iaas --yes --no-wait</code> (removes VM, disk, snapshot, IP, NSG). '
            '<b>Google Cloud:</b> <code>gcloud compute instances delete tiffingo-iaas --zone=asia-south1-a --quiet</code> and <code>gcloud compute snapshots delete tiffingo-iaas-snap --quiet</code>. '
            'Cost if cleaned up the same day: well under ₹10 on any cloud.')
prac = prac.replace('<ol class="stepper">', caution('Never open SSH (port 22) to 0.0.0.0/0 on a server you keep, never use the root user’s keys in the CLI, and never commit the .pem file or access keys to GitHub. Bots scan for all three within minutes.') + '<ol class="stepper">', 1)

mist = mistakes([
    ['“I launched an instance but cannot see it.”', 'The console or CLI is pointed at another region (often us-east-1).', 'Check the region selector / <code>aws configure get region</code>; use ap-south-1 everywhere.'],
    ['SSH: “Connection timed out”.', 'Port 22 not allowed from your IP, no public IP, or wrong IP after a restart.', 'Fix the security group rule (your current IP /32), check the public IP in describe-instances.'],
    ['SSH: “UNPROTECTED PRIVATE KEY FILE” or “Permission denied (publickey)”.', 'Key file permissions too open, wrong key, or wrong user name.', '<code>chmod 400 key.pem</code>; user is <code>ec2-user</code> on Amazon Linux, <code>ubuntu</code> on Ubuntu.'],
    ['Web page does not load.', 'Port 80 closed, nginx not installed, or user data failed.', 'Check the SG rule; SSH in and read <code>/var/log/cloud-init-output.log</code>; <code>systemctl status nginx</code>.'],
    ['Bill keeps coming after “stopping” the server.', 'Stopped instances still pay for EBS disks and Elastic IPs.', 'Terminate when finished; release Elastic IPs; delete old snapshots.'],
    ['Data lost after terminate.', 'Root volume has DeleteOnTermination = true by default.', 'Create an AMI or snapshot first, or keep data on a separate volume / S3.'],
    ['“Cannot attach volume: different Availability Zone”.', 'EBS volumes are AZ-bound.', 'Create the volume in the instance’s AZ, or snapshot → new volume in the right AZ.'],
    ['A t3 server becomes slow every afternoon.', 'CPU credits run out in standard mode (or unlimited charges pile up).', 'Watch CPUCreditBalance; move steady high-CPU work to m/c families.'],
    ['Access keys saved in a file on the server or in GitHub.', 'Quick way to give the app permissions.', 'Use an IAM role (instance profile); rotate and delete any leaked keys immediately.'],
    ['Instance cannot start: “VcpuLimitExceeded”.', 'Account vCPU quota for that family/region reached.', 'Terminate unused instances or request a quota increase in Service Quotas.'],
    ['“UnauthorizedOperation” on run-instances.', 'IAM user lacks ec2:RunInstances (or iam:PassRole for a role).', 'Attach a suitable policy to the user/group; read the decoded message with <code>aws sts decode-authorization-message</code>.']])

# ---------- certification (explained)
def q(qtext, opts, ans, why):
    li = ''.join(f'<li>{"<b>✔ " if i == ans else ""}{o}{"</b>" if i == ans else ""}</li>' for i, o in enumerate(opts))
    return f'  <details class="faq"><summary>{qtext}</summary><ol type="a">{li}</ol><p><b>Why:</b> {why}</p></details>\n'
cert = table(['Exam', 'Domain', 'What this lesson covers'], [
    ['AWS CLF-C02', 'Domain 3 · Cloud Technology & Services (34%)', 'EC2 as IaaS, instance types, AMIs, EBS, regions/AZs, security groups.'],
    ['AWS CLF-C02', 'Domain 2 · Security (30%) · Domain 4 · Billing (12%)', 'Shared responsibility for EC2 (you patch the OS); on-demand billing per second.'],
    ['Azure AZ-900', 'Describe Azure compute and networking services', 'Virtual machines, VM sizes, NSGs, IaaS vs PaaS.'],
    ['Google Cloud Digital Leader', 'Modernize infrastructure and applications', 'Compute Engine as IaaS; when to use VMs.'],
    ['C-DAC PGCP-BDA', 'Sessions 3–4, 8–9 (lab: create EC2)', 'Introduction to IaaS, examples; launching and accessing a Linux VM.']], minw=600) + '\n  <h3>Exam-style questions with explanations</h3>\n' + \
    q('1. A company runs its app on EC2. Who is responsible for installing security patches on the guest operating system?', ['AWS', 'The customer', 'Both equally', 'The internet provider'], 1, 'With IaaS the customer manages the OS and above. AWS patches the hypervisor, hardware and facilities. This shared-responsibility question appears in almost every CLF-C02 paper.') + \
    q('2. Which is an example of IaaS?', ['Amazon EC2', 'AWS Elastic Beanstalk', 'Gmail', 'Amazon Rekognition'], 0, 'EC2 gives raw virtual machines. Beanstalk is PaaS (it manages the platform), Gmail is SaaS, Rekognition is an AI service.') + \
    q('3. A web server is stopped (not terminated) for the weekend. What is still charged?', ['Nothing', 'Compute hours', 'The attached EBS volume (and any Elastic IP)', 'Data transfer in'], 2, 'Stopped instances do not pay for compute, but storage on EBS and unattached/idle public IPs are still billed.') + \
    q('4. Which EC2 feature acts as a virtual firewall controlling inbound and outbound traffic for an instance?', ['IAM role', 'Security group', 'AMI', 'Key pair'], 1, 'Security groups are stateful firewalls attached to instances (network interfaces). IAM controls who can call APIs; a key pair is for login; an AMI is the image.') + \
    q('5. Which pricing model suits a steady web server that will run 24×7 for 3 years at the lowest cost?', ['On-Demand', 'Savings Plans / Reserved Instances', 'Spot Instances', 'Dedicated Hosts'], 1, 'Commitment-based pricing gives the biggest discount for steady use. Spot is cheap but can be interrupted; Dedicated Hosts are for licensing/compliance.') + \
    q('6. Which purchasing option gives the biggest discount but can be interrupted with a 2-minute warning?', ['Reserved Instances', 'Spot Instances', 'Savings Plans', 'Dedicated Hosts'], 1, 'Spot uses spare capacity at up to 90% off; AWS can reclaim it. Good for fault-tolerant batch work, not for a single critical web server.') + \
    q('7. Data on which storage is lost when an instance is stopped?', ['EBS gp3 volume', 'Instance store', 'S3', 'EBS snapshot'], 1, 'Instance store is physically on the host; stopping moves the VM to another host, so the data is gone. EBS survives stop/start.') + \
    q('8. What is the most secure way for an application on EC2 to read from S3?', ['Store access keys in the code', 'Attach an IAM role through an instance profile', 'Make the bucket public', 'Use the root user'], 1, 'Roles give temporary, auto-rotated credentials via the metadata service; nothing secret is stored on the server.') + \
    q('9. A security group allows inbound port 443. What about the response traffic?', ['It must be allowed by an outbound rule', 'It is allowed automatically because security groups are stateful', 'It is blocked', 'Only for IPv6'], 1, 'Security groups track connections (stateful). Network ACLs are stateless and need explicit rules both ways.') + \
    q('10. What is the purpose of EC2 user data?', ['To store user passwords', 'To run a script automatically at first boot', 'To list IAM users', 'To encrypt EBS'], 1, 'User data scripts run as root through cloud-init at launch; they install and configure software without logging in.')

# ---------- mini project
proj = miniproject('Mini project: TiffinGo menu website on EC2 with a backup image',
    'Launch a web server that shows TiffinGo’s menu, update the page over SSH, save a reusable image (AMI), then launch a second copy from that image — and clean up.',
    ['<b>Set up:</b> <code>aws configure</code> (IAM user, region ap-south-1); create a budget alert of $1.',
     '<b>Launch:</b> as in practical step 2, but also allow port 80 in the security group and pass a user-data script that installs nginx (<code>--user-data file://userdata.sh</code>, as in Lesson 6.1).',
     '<b>Test:</b> <code>aws ec2 wait instance-status-ok --instance-ids $IID</code>, then <code>PUB=$(aws ec2 describe-instances --instance-ids $IID --query "Reservations[0].Instances[0].PublicIpAddress" --output text)</code> and <code>curl http://$PUB</code> → expect the “TiffinGo menu” heading.',
     '<b>Update the menu:</b> <code>ssh -i tiffingo-key.pem ec2-user@$PUB</code>, then <code>echo "&lt;p&gt;Today: Paneer thali ₹150&lt;/p&gt;" | sudo tee -a /usr/share/nginx/html/index.html</code>; refresh the browser.',
     '<b>Save an image:</b> <code>IMG=$(aws ec2 create-image --instance-id $IID --name tiffingo-web-v1 --query ImageId --output text)</code>; <code>aws ec2 wait image-available --image-ids $IMG</code>.',
     '<b>Launch a copy:</b> <code>aws ec2 run-instances --image-id $IMG --instance-type t3.micro --security-group-ids $SG --key-name tiffingo-key</code> — the new server already has nginx and the updated menu (no user data needed).',
     '<b>Clean up:</b> terminate both instances, <code>aws ec2 deregister-image --image-id $IMG</code>, delete the AMI’s snapshot (<code>aws ec2 describe-snapshots --owner-ids self</code> → <code>delete-snapshot</code>), delete the security group and key pair; then <code>aws ec2 describe-instances --filters Name=instance-state-name,Values=pending,running,stopping,stopped --query "length(Reservations)"</code> should print 0.'],
    'Two identical web servers showing the updated TiffinGo menu, then nothing left running and no snapshot left behind.',
    'EC2 + security groups + key pairs + user data + AMIs/EBS snapshots + SSH (Linux course).')

assemble_v2(HERE, story_h2='The new menu website needs a server today', hook_html=hk,
    narration='TiffinGo is launching a menu website for its Pune and Mumbai kitchens. It needs one Linux server with nginx, today. Kabir’s first instinct is to buy a server.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='What is IaaS?',
    formal='<b>Infrastructure as a Service (IaaS)</b> is a cloud service model in which the provider delivers virtualized computing infrastructure — virtual machines, block and object storage, and networking — on demand over the internet, while the customer controls and manages the operating system, middleware, runtime, data and applications (NIST SP 800-145).',
    simple='You rent virtual servers, disks and networks by the second, and install and run everything on them yourself.',
    interview=['“IaaS is the cloud service model where the provider gives virtualized infrastructure — virtual machines, storage and networks — on demand, and we manage the operating system and everything above it.”', '“Examples are Amazon EC2, Azure Virtual Machines and Google Compute Engine. We choose an image, an instance type, a key pair and a security group, and pay per second while it runs.”', '“For example, I launched a t3.micro in Mumbai with a user-data script that installed nginx, then terminated it to stop the bill.”'],
    terms_rows=[('Instance', 'One virtual machine in EC2.'), ('AMI', 'Image used to create the VM’s disk.'), ('Instance type', 'Size: vCPU, memory, network.'), ('Key pair', 'Public/private keys for SSH login.'), ('Security group', 'Stateful firewall around the instance.'), ('EBS', 'Network block disk for the instance.'), ('User data', 'Script run at first boot.'), ('VPC / subnet', 'Your private network and its IP range.')],
    exam='CLF-C02 loves two IaaS facts: under shared responsibility the <b>customer patches the guest OS</b> on EC2, and a <b>security group</b> is the instance-level firewall. Also know the pricing options: On-Demand, Savings Plans/Reserved, Spot, Dedicated Hosts.',
    picture_h2='What you rent, and the pieces of one server', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Six VM families, one by one', TYPESEC)],
    how_h2='Inside a launch, and how the lifecycle drives the bill', how_intro='Two animations: what AWS does in the seconds after you launch, and how each state of the instance changes what you pay.', how_anim=LAUNCH + LIFE, how_after=how_after,
    parts_h2='Every part of an EC2 instance', parts_html=parts, lv='',
    myth_rows=[('A stopped server costs nothing.', 'Its EBS disk and public IPs are still billed.', 'Lifecycle animation.'), ('IaaS means AWS manages my server.', 'AWS runs hardware + virtualization; you run the OS and app.', 'Responsibility picture.'), ('One instance type fits all.', '849 types in Mumbai, by family letter.', 'Parts table.')],
    clouds_html=clouds,
    extra_secs=[('deep', 'Deep dive', 'Under the hood: hardware, CPU credits, storage, network, identity, pricing', DEEP), ('console', 'Visual: the console', 'Launching from the console, field by field', CONSOLE)],
    practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Explain IaaS and what you vs the provider manage.', 'Name every part of an EC2 instance and its Azure/GCP equivalent.', 'Describe the six steps behind run-instances.', 'Pick the right VM family for a workload.', 'Launch, log into, patch, stop and snapshot a VM on AWS, Azure or Google Cloud — UI or CLI.', 'Avoid the common SSH, region and billing mistakes.'],
    next_html='<a href="../02-paas-platform-as-a-service-and-its-types/">2.2 PaaS: let the platform run your code</a>.',
    pre='<b>Before you start:</b> Module 1, especially <a href="../../01-introduction/05-on-premises-vs-cloud-vs-dedicated-servers/">1.5 who manages which layer</a>. Linux basics help (SSH, nginx).')
