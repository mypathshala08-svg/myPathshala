import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
sys.path.insert(0, HERE)
from _types import build as build_types
from _prac import PRAC
C = 'l45.txt'; CA = 'l45_aws.txt'
def sec(a, b=None): return capsec(C, a, b)
def seca(a, b=None): return capsec(CA, a, b)

hk = hook('“We run VMware, so we already have a cloud.” True or false?',
    'False — and this is one of the most common interview traps. <b>Virtualization</b> is a technology that splits hardware. <b>Cloud computing</b> is a service model: self-service, on-demand, elastic, pay-per-use, over the network — usually <i>built on</i> virtualization plus automation. <b>Containers</b> are a lighter way to package and isolate apps that can run on either. In our lab a container saw the <b>same kernel</b> as its host and started in <b>3–4 ms</b>; its base image was <b>3.5 MB</b> against <b>593 MB</b> for a VM image. Then we deploy the same menu API in AWS three ways: <b>VM, container and function</b>.',
    ['Why virtualization ≠ cloud (the NIST test).', 'VM vs container vs serverless — what each layer manages.', 'Micro-VMs (Firecracker): how Lambda and Fargate combine both.'])

def story_scene():
    o = t(180, 12, 'Three people, three words for “the same thing”', 9, 'ink', bold=True)
    for i, (who, said, tn) in enumerate([('Old IT head', '“Our VMware is our cloud.”', 'amber'), ('New developer', '“Just put it in Docker.”', 'blue'), ('CFO', '“Why pay AWS if we have VMs?”', 'violet')]):
        x = 8 + i * 118
        o += box(x, 22, 108, 92, tn, rx=8) + ic('user', x + 43, 28, 0.9) + t(x + 54, 66, who, 8, 'ink', bold=True) + t(x + 54, 84, said, 6.6, 'ink2')
    o += t(180, 134, 'All three are mixing up technology, packaging and service.', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Three people: an IT head saying our VMware is our cloud, a developer saying just put it in Docker, a CFO asking why pay AWS if we have VMs.', story_scene(), 'Let’s separate the <tspan font-weight="700" class="s-acc">technology, the packaging and the service</tspan>.', h=160)
dialogue = '''R> Sir, our old IT head says TiffinGo had a “private cloud” in 2018 because everything ran on VMware. Was that cloud?
A> It was virtualization. To get a VM, you raised a ticket and waited three days. Nobody saw a bill per team, and nothing scaled by itself.
K> And Docker? Is that a cloud too?
A> Docker is packaging: an app with its files, isolated by the kernel. You can run containers on your laptop, on VMs in your data centre, or in the cloud.
R> So what makes something a cloud?
A> Five characteristics from NIST — self-service, network access, pooling, elasticity and metering. Let’s test each word against them, and then deploy the same app as a VM, a container and a function.'''

# ---------------------------------------------------------------- figures
def stackfig():
    o = t(320, 16, 'Each layer builds on the one below — and adds something different', 11, 'ink', bold=True)
    L = [('Hardware', 'servers, disks, network', 'card', 'the physical data centre'),
         ('Virtualization', 'hypervisor: split one server into many VMs', 'amber', 'VMware ESXi, KVM, Hyper-V, Nitro'),
         ('Automation + self-service + metering', 'APIs, portal, scheduler, quotas, per-second billing', 'green', 'what turns a virtualized DC into a cloud'),
         ('Cloud services', 'IaaS (EC2) · PaaS · SaaS · managed databases', 'blue', 'AWS, Azure, Google Cloud, OpenStack private cloud'),
         ('Containers', 'package app + files; namespaces + cgroups on a VM’s kernel', 'violet', 'Docker, Kubernetes, ECS, EKS, AKS, GKE'),
         ('Serverless', 'just code or a container image; scales to zero; pay per request', 'red', 'Lambda, Fargate, Cloud Run, Azure Functions')]
    for i, (a, b, tn, ex) in enumerate(L):
        y = 268 - i * 44
        w = 600 - i * 36
        x = 20 + i * 18
        o += box(x, y, w, 38, tn, rx=7) + t(x + 12, y + 16, a, 8.8, 'ink', anchor='start', bold=True) + t(x + 12, y + 30, b, 7.2, 'ink', anchor='start') + t(x + w - 10, y + 23, ex, 7, 'ink2', anchor='end')
    o += t(320, 324, 'Virtualization alone stops at layer 2. Cloud = layers 2 + 3 offered as a service. Containers and serverless are ways to run apps on top.', 7.6, 'ink2')
    return o
STACK = bigfig('Six stacked layers from bottom to top: hardware; virtualization (hypervisor); automation, self-service and metering; cloud services (IaaS, PaaS, SaaS); containers; serverless. Each layer shows what it adds and examples.', stackfig(), h=334)

def nistfig():
    o = t(320, 16, 'The NIST test: which essential cloud characteristics does each setup have?', 11, 'ink', bold=True)
    cols = ['Virtualized data centre', 'Private cloud', 'Public cloud']
    rows = [('On-demand self-service', ['✗ ticket to admin', '✓ portal / API', '✓ console / API']),
            ('Broad network access', ['~ internal only', '✓ internal network', '✓ internet']),
            ('Resource pooling', ['✓ VMs share hosts', '✓', '✓ multi-tenant']),
            ('Rapid elasticity', ['✗ buy servers first', '~ up to own capacity', '✓ seemingly unlimited']),
            ('Measured service', ['✗ one IT budget', '✓ showback per team', '✓ per-second billing'])]
    o += box(20, 30, 200, 26, 'card', rx=4) + t(30, 47, 'NIST characteristic', 8, 'ink', anchor='start', bold=True)
    for j, c in enumerate(cols):
        o += box(228 + j * 132, 30, 126, 26, ['amber', 'green', 'blue'][j], rx=4) + t(291 + j * 132, 47, c, 7.8, 'ink', bold=True)
    for i, (n, vals) in enumerate(rows):
        y = 62 + i * 36
        o += box(20, y, 200, 30, 'card', rx=4) + t(30, y + 19, n, 8, 'ink', anchor='start', bold=True)
        for j, v in enumerate(vals):
            tn = 'green' if v.startswith('✓') else ('red' if v.startswith('✗') else 'amber')
            o += box(228 + j * 132, y, 126, 30, tn, rx=4) + t(291 + j * 132, y + 19, v, 7.4, 'ink', bold=v.startswith('✓'))
    o += t(320, 256, 'Virtualization gives pooling. Cloud needs all five. A VMware cluster becomes a private cloud only when you add', 7.6, 'ink2')
    o += t(320, 270, 'self-service, automation and metering (e.g. OpenStack, VMware Cloud Foundation, Azure Local / Azure Stack).', 7.6, 'ink2')
    return o
NIST = bigfig('Table figure: five NIST characteristics (on-demand self-service, broad network access, resource pooling, rapid elasticity, measured service) checked for a virtualized data centre (only pooling fully), a private cloud (most) and a public cloud (all five).', nistfig(), h=282)

def vcsfig():
    o = t(320, 16, 'Who manages what: VM vs container vs function', 11, 'ink', bold=True)
    layers = ['Your code', 'Runtime + libraries', 'Guest OS / kernel', 'Container runtime', 'Hypervisor', 'Hardware']
    owns = [[1, 1, 1, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0]]
    names = [('VM (EC2)', 'you patch the OS'), ('Container (ECS/Fargate)', 'you build the image'), ('Function (Lambda)', 'you write the code')]
    present = [[1, 1, 1, 0, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]]
    for c in range(3):
        x = 30 + c * 200
        o += t(x + 85, 40, names[c][0], 9, 'ink', bold=True) + t(x + 85, 54, names[c][1], 7.2, 'ink2')
        for i, L in enumerate(layers):
            y = 62 + i * 30
            if not present[c][i]:
                o += f'<rect x="{x}" y="{y}" width="170" height="26" rx="4" style="fill:none;stroke:#999;stroke-dasharray:3 3"/>' + t(x + 85, y + 17, '(not used by a plain VM)', 6.8, 'ink2')
                continue
            tn = 'blue' if owns[c][i] else 'card'
            o += box(x, y, 170, 26, tn, rx=4) + t(x + 85, y + 17, L + ('  · you' if owns[c][i] else '  · cloud'), 7.6, 'ink', bold=bool(owns[c][i]))
    o += t(320, 256, 'Blue = your job. The higher you go, the less you manage — and the less you can control.', 7.8, 'ink2')
    o += t(320, 272, 'Fargate and Lambda run each task/function in a Firecracker micro-VM: container convenience, VM isolation.', 7.6, 'ink2')
    return o
VCS = bigfig('Three stacks side by side: VM (you manage code, runtime and guest OS), container on Fargate (you manage code and runtime in the image), function on Lambda (you manage only code). Lower layers — container runtime, hypervisor, hardware — are managed by the cloud.', vcsfig(), h=284)

picture = ('  <p>Three words get mixed up all the time. Put them on one stack and the difference is obvious: <b>virtualization</b> is a layer of technology; <b>cloud</b> is what you get when that layer is automated, self-service and metered and offered as a service; <b>containers</b> and <b>serverless</b> are ways to run your app on top.</p>\n' + STACK +
           '\n  <h3>Is it a cloud? Apply the NIST test</h3>\n  <p>NIST SP 800-145 (Lesson 1.1) lists five essential characteristics. Check each setup against them:</p>\n' + NIST +
           '\n  <h3>VM, container, function: who manages what</h3>\n' + VCS)

# ---------------------------------------------------------------- animation 1: getting a server — cloud control plane
RN = {'u': (4, 54, 54, 50, 'user', 'Ravi', 'needs a VM'), 'api': (66, 54, 56, 50, 'globe', 'API / console', 'HTTPS'), 'iam': (130, 4, 56, 46, 'shield', 'IAM', 'allowed?'),
      'q': (130, 104, 56, 46, 'meter', 'Quota', 'within limit?'), 'pl': (194, 54, 56, 50, 'gear', 'Placement', 'pick a host'), 'h': (258, 54, 46, 50, 'server', 'Host', 'Nitro'),
      'm': (310, 4, 46, 46, 'chart', 'Meter', 'billing'), 'vm': (310, 104, 46, 46, 'app', 'VM', 'running')}
RS = [dict(on=['u', 'api'], hot='api', move=(58, 79, 66, 79, ''), head='Step 1 · Self-service request', text='Ravi calls RunInstances himself (console, CLI or Terraform). No ticket, no email,', text2='no waiting for an admin — NIST characteristic 1: on-demand self-service.', svc='Virtualized DC: ticket → approval → admin clicks in vCenter → days'),
      dict(on=['u', 'api', 'iam'], hot='iam', move=(94, 54, 150, 50, 'auth'), head='Step 2 · Who is asking? (IAM)', text='The request is signed with Ravi’s credentials; IAM checks his policy allows', text2='ec2:RunInstances for this instance type and Region.', svc='Replaces the human approval step with a policy'),
      dict(on=['u', 'api', 'iam', 'q'], hot='q', move=(94, 104, 140, 116, 'quota'), head='Step 3 · Check quota and capacity', text='The account’s vCPU quota is checked so one team cannot take everything.', text2='Capacity in the chosen AZ is checked too (or “InsufficientInstanceCapacity”).', svc='Service Quotas · Azure quotas · GCP quotas'),
      dict(on=['u', 'api', 'iam', 'q', 'pl'], hot='pl', move=(186, 79, 194, 79, ''), head='Step 4 · Placement (resource pooling)', text='A scheduler picks a physical host in the pool with free capacity, honouring', text2='placement groups and dedicated-host rules. You never choose the box.', svc='This is the “cloud brain” a plain hypervisor does not have'),
      dict(on=['u', 'api', 'iam', 'q', 'pl', 'h', 'vm'], hot='vm', move=(281, 104, 312, 124, 'boot'), head='Step 5 · The hypervisor creates the VM', text='Now virtualization does its part: the host’s hypervisor creates the VM from the AMI,', text2='Nitro attaches the EBS root volume and the network interface. ~1 minute.', svc='Virtualization is one step of five — not the whole cloud'),
      dict(on=list(RN), hot='m', move=(281, 54, 312, 30, 'meter'), head='Step 6 · Metering starts', text='Per-second billing begins in state “running”; usage goes to Cost Explorer with', text2='Ravi’s team tag. Terminate it and the meter stops — NIST: measured service.', svc='Elasticity: Auto Scaling repeats steps 1–6 automatically when load rises')]
REQ = flow_anim('Getting a server in a cloud: virtualization is only step 5', 'What the cloud adds around the hypervisor, step by step.', 'Cloud control plane', 'Animation: Ravi sends a self-service API request; IAM checks permission; quota and capacity are checked; the placement scheduler picks a host; the hypervisor creates the VM; billing meter starts.', RN, RS, hid='req')

# ---------------------------------------------------------------- animation 2: same app three ways
def three_frame(k):
    o = t(180, 12, ['As a VM', 'As a container', 'As a function'][k], 9, 'ink', bold=True)
    stacks = [['menu app', 'Python + libs', 'Ubuntu 24.04 kernel', 'hypervisor'], ['menu app', 'Python + libs', 'Alpine files (no kernel)', 'host kernel (shared)'], ['handler()', 'managed runtime', 'micro-VM (Firecracker)', 'AWS-managed host']][k]
    for i, s in enumerate(stacks):
        tn = ['blue', 'blue', 'amber', 'card'][i] if k < 2 else ['blue', 'card', 'card', 'card'][i]
        o += box(14, 26 + i * 28, 150, 24, tn, rx=4) + t(89, 42 + i * 28, s, 7.6, 'ink', bold=(i == 0))
    facts = [[('image', '593 MB'), ('start', '~30–60 s'), ('unit', 'whole server'), ('idle cost', 'pay while running')],
             [('image', '3.5 MB base'), ('start', '3–4 ms (our lab)'), ('unit', 'process'), ('idle cost', 'pay for the host/task')],
             [('package', 'zip, 214 bytes'), ('start', 'ms warm; cold ~100s ms'), ('unit', 'one request'), ('idle cost', 'zero (scales to 0)')]][k]
    for i, (a, b) in enumerate(facts):
        o += box(178, 26 + i * 28, 172, 24, 'green' if i == 1 else 'card', rx=4) + t(186, 42 + i * 28, a, 7.4, 'ink2', anchor='start') + t(342, 42 + i * 28, b, 7.8, 'ink', anchor='end', bold=True)
    o += t(180, 148, ['Most control, most work.', 'Light, portable, same kernel family only.', 'Least work, least control; time limit (15 min on Lambda).'][k], 7.6, 'ink', bold=True)
    return o
TS = [('As a VM', 'Full OS in the image: you patch it, size it, keep it running.', 'Use for legacy apps, special OS needs, full control.'),
      ('As a container', 'Only app files; the kernel comes from the host. Starts in milliseconds.', 'Use for microservices, CI jobs, portable deployments.'),
      ('As a function', 'Only your code; the platform runs it per request and scales to zero.', 'Use for events, APIs with spiky traffic, glue code.')]
TSA = anim_one('How it works', 'The same menu API, three ways', 'Sizes and start times from our lab and the AWS lab below.', 'VM vs container vs function', 'Animation: the menu API as a VM (593 MB image, 30–60 s start), as a container (3.5 MB base, 3–4 ms start) and as a function (214-byte zip, scales to zero).', cap_frames([three_frame(k) for k in range(3)], TS), [x[0] + '.' for x in TS], delay=6000, hid='three')

# ---------------------------------------------------------------- animation 3: Firecracker micro-VM
FN = {'req': (4, 54, 54, 50, 'globe', 'Request', 'GET /menu'), 'fe': (66, 54, 56, 50, 'lb', 'Front end', 'route'), 'w': (130, 54, 60, 50, 'server', 'Worker host', 'bare metal'),
      'fc': (198, 4, 70, 46, 'chip', 'Firecracker', 'micro-VM'), 'code': (198, 104, 70, 46, 'app', 'Your code', 'handler()'), 'resp': (300, 54, 56, 50, 'chart', 'Response', '200 OK')}
FS = [dict(on=['req', 'fe'], hot='fe', move=(58, 79, 66, 79, ''), head='Step 1 · A request arrives', text='API Gateway or a function URL sends the event to Lambda’s front end, which', text2='checks permissions and finds a worker with a warm environment for this function.', svc='Warm environment found → skip to step 4 (milliseconds)'),
      dict(on=['req', 'fe', 'w', 'fc'], hot='fc', move=(160, 54, 210, 40, 'boot'), head='Step 2 · Cold start: boot a micro-VM', text='None warm? A Firecracker micro-VM boots on a bare-metal worker. It has only a', text2='few virtual devices, so it boots in about 125 ms with ~5 MiB overhead.', svc='Firecracker: open source, written in Rust, built by AWS for Lambda and Fargate'),
      dict(on=['req', 'fe', 'w', 'fc', 'code'], hot='code', move=(233, 50, 233, 104, 'load'), head='Step 3 · Load runtime and your code', text='The Python runtime starts and imports app.py. Code outside handler() runs once', text2='here — put DB connections there so later requests reuse them.', svc='Cold start total: typically ~100 ms to a few seconds depending on runtime and code size'),
      dict(on=['req', 'fe', 'w', 'fc', 'code', 'resp'], hot='resp', move=(268, 127, 300, 90, 'return'), head='Step 4 · Run handler() and respond', text='Your function runs, returns 200 with the menu. You are billed per ms of', text2='run time × memory size. Then the micro-VM is frozen, kept warm for reuse.', svc='Each micro-VM serves one request at a time; more requests → more micro-VMs'),
      dict(on=list(FN), hot='w', move=None, head='Step 5 · Why a micro-VM and not just a container?', text='Strangers’ code runs on the same hosts. A container shares the kernel; a micro-VM', text2='has its own, so a kernel bug in one customer’s code cannot reach another’s.', svc='Same idea: Fargate tasks, Kata Containers, gVisor (Cloud Run)')]
FC = flow_anim('How serverless really runs: one request, one micro-VM', 'Containers’ speed with VM isolation — the technology behind Lambda and Fargate.', 'Firecracker micro-VMs', 'Animation: a request reaches the Lambda front end; on a cold start a Firecracker micro-VM boots in about 125 ms on a bare-metal worker; runtime and code load; the handler runs and responds; micro-VM isolation explained.', FN, FS, hid='fc')

parts = '\n  <h3>Virtualization vs cloud computing</h3>\n' + table(['', 'Virtualization', 'Cloud computing'], [
    ['What it is', 'a technology', 'a service and delivery model'], ['Main goal', 'better use of hardware', 'on-demand IT as a utility'], ['Getting a server', 'admin creates it (often days)', 'you create it (seconds–minutes, API)'],
    ['Scaling', 'manual, within owned hosts', 'automatic, practically unlimited'], ['Cost model', 'capex: buy hardware + licences', 'opex: pay per second/request'], ['Who runs hardware', 'you', 'the provider (public cloud)'],
    ['Needs the other?', 'no — works without cloud', 'usually built on it; bare-metal instances show it is not strictly required']], minw=560) + \
    '\n  <h3>VM vs container vs serverless</h3>\n' + table(['', 'Virtual machine', 'Container', 'Serverless function'], [
    ['Isolation', 'own kernel (strong)', 'shared kernel (good)', 'micro-VM per environment (strong)'], ['Size', 'GBs (593 MB image)', 'MBs (3.5 MB base)', 'KBs–MBs of code'],
    ['Start time', '30–60 s', 'milliseconds (3–4 ms lab)', 'ms warm; ~100 ms–s cold'], ['You manage', 'OS, runtime, app', 'image (runtime + app), sometimes nodes', 'only code'],
    ['Billing', 'per second while running', 'per task/node while running', 'per request + ms × memory'], ['Limits', 'few', 'same kernel family', '15-min max run (Lambda), stateless'],
    ['Best for', 'legacy, custom OS, long-running', 'microservices, portability, CI', 'events, spiky APIs, glue code']], minw=640)

DEEP = ('  <h3>Is virtualization necessary for cloud?</h3>\n  <p>Not strictly. AWS sells <b>bare-metal instances</b> (for example <code>m7i.metal-24xl</code>) with no hypervisor at all — yet they are still “cloud”, because you get them by API, in minutes, metered per second. On Nitro, even bare metal gets virtual networking and storage from the Nitro cards. So the cloud needs <b>automation, self-service and metering</b>; virtualization is the most common way to pool hardware, not the definition.</p>\n'
    '  <h3>Is virtualization sufficient for cloud?</h3>\n  <p>No. The NIST test above shows a ticket-driven VMware cluster fails self-service, elasticity and metering. Adding a portal, an API, quotas, automation and chargeback makes it a <b>private cloud</b>.</p>\n'
    '  <h3>Containers on VMs, VMs in containers</h3>\n  <ul><li>In every public cloud, containers usually run <b>on VMs</b> (EKS worker nodes are EC2 instances) — VM isolation between customers, container density inside.</li><li><b>KubeVirt</b> runs VMs as Kubernetes objects — a team can manage both with one tool.</li><li>Docker Desktop on Windows/macOS runs Linux containers inside a hidden Linux VM (Lesson 4.2).</li></ul>\n'
    '  <h3>Firecracker in numbers</h3>\n' + table(['Property', 'Firecracker micro-VM', 'Typical VM'], [
    ['Boot time', 'about 125 ms', '30–60 s'], ['Memory overhead', 'under 5 MiB per micro-VM', 'hundreds of MB'], ['Virtual devices', 'virtio-net, virtio-block, serial, a keyboard (for reset)', 'dozens (USB, graphics, sound…)'],
    ['Used by', 'AWS Lambda, AWS Fargate', 'EC2, Azure VMs, Compute Engine']], minw=520) +
    '\n  <h3>A practical decision guide</h3>\n' + table(['If you need…', 'Choose'], [
    ['Windows Server app or a custom kernel module', 'VM'], ['Lift-and-shift of an existing server', 'VM (Lesson 4.4, MGN)'], ['Many small services with frequent releases', 'containers (ECS/EKS/AKS/GKE)'],
    ['No servers to patch, steady container service', 'serverless containers (Fargate, Cloud Run, Container Apps)'], ['Code that runs on events, idle most of the time', 'functions (Lambda, Azure Functions, Cloud Run functions)'],
    ['Data must stay in your building but you want cloud-style self-service', 'private cloud (OpenStack, VMware Cloud Foundation, Outposts/Azure Local)']], minw=560))

clouds = vendor_tabs('<p><b>AWS:</b> VMs = <b>EC2</b>; containers = <b>ECS</b>, <b>EKS</b>, images in <b>ECR</b>; serverless = <b>Lambda</b>, <b>Fargate</b>, App Runner; private/hybrid = <b>Outposts</b>, VMware Cloud on AWS; isolation = Nitro + Firecracker.</p>',
    '<p><b>Azure:</b> VMs = <b>Virtual Machines</b>; containers = <b>AKS</b>, Container Instances, images in <b>ACR</b>; serverless = <b>Azure Functions</b>, <b>Container Apps</b>; private/hybrid = <b>Azure Local</b> (formerly Azure Stack HCI), Azure Arc.</p>',
    '<p><b>Google Cloud:</b> VMs = <b>Compute Engine</b>; containers = <b>GKE</b>, images in <b>Artifact Registry</b>; serverless = <b>Cloud Run</b> (containers and functions); private/hybrid = <b>Google Distributed Cloud</b>, Anthos/GKE Enterprise; sandbox = gVisor.</p>') + \
    cloud3([['Virtual machines', 'EC2', 'Virtual Machines', 'Compute Engine'], ['Kubernetes', 'EKS', 'AKS', 'GKE'], ['Simple containers', 'ECS (+ Fargate)', 'Container Instances / Container Apps', 'Cloud Run'],
            ['Functions', 'Lambda', 'Azure Functions', 'Cloud Run functions'], ['Image registry', 'ECR', 'ACR', 'Artifact Registry'], ['Cloud in your data centre', 'Outposts', 'Azure Local', 'Google Distributed Cloud']])

proof = [
    ('Step 1 · Container kernel = host kernel', code('bash', 'terminal', 'echo "host kernel:      $(uname -r)"\necho "inside container: $(unshare --pid --uts --mount --fork --mount-proc uname -r)"', sec('== 1)', '== 2)')), 'Identical. A VM would show its own kernel; a container cannot.'),
    ('Step 2 · Container start time', code('bash', 'terminal', 'for i in 1 2 3; do\n  s=$(date +%s%N); unshare --pid --uts --mount --fork --mount-proc true; e=$(date +%s%N)\n  echo "run $i: $(( (e-s)/1000000 )) ms"\ndone', sec('== 2)', '== 3)')), 'No OS to boot: creating an isolated process takes a few milliseconds. A VM boots a kernel and init system first.'),
    ('Step 3 · What you ship: container base vs VM image', code('bash', 'terminal', 'curl -sI https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img | grep -i content-length\ncurl -s https://dl-cdn.alpinelinux.org/alpine/latest-stable/releases/x86_64/latest-releases.yaml | grep -A8 minirootfs', sec('== 3)')), 'About 170× smaller. That difference is why containers are pulled and started on demand while VM images are cached and cloned (Lesson 4.4).')]

prac = practical('Part A runs on any Linux/WSL2 machine. Part B deploys the same menu API in AWS three ways. <b>Our Part B outputs come from the moto AWS emulator</b> — on a real account you will see real IDs; the Lambda function and the task definition cost nothing while idle, and the t3.micro is Free-Tier eligible.', [
    ('A1 · Prove the shared kernel yourself', code('bash', 'terminal', 'uname -r\nsudo unshare --pid --fork --mount-proc uname -r\ndocker run --rm alpine uname -r     # if Docker is installed'), 'All three print the same kernel.'),
    ('A2 · Feel the start-time difference', code('bash', 'terminal', 'time sudo unshare --pid --fork --mount-proc true\ntime docker run --rm alpine true   # includes Docker overhead, still < 1 s'), 'Compare with how long a VM takes to boot (Lesson 4.1 practical).'),
    ('B1 · As a VM (EC2)', code('bash', 'terminal', "aws ec2 run-instances --image-id $AMI --instance-type t3.micro \\\n  --query 'Instances[0].InstanceId' --output text", seca('== 1)', '== 2)')), 'You get a whole server: patch it, secure SSH, install Python, run the app, keep it alive.'),
    ('B2 · As a container (ECS on Fargate)', code('bash', 'terminal', "aws ecs create-cluster --cluster-name tiffingo\naws ecs register-task-definition --family menu-api --requires-compatibilities FARGATE \\\n  --network-mode awsvpc --cpu 256 --memory 512 --execution-role-arn $ROLE \\\n  --container-definitions '[{\"name\":\"menu\",\"image\":\"public.ecr.aws/nginx/nginx:alpine\",\n    \"portMappings\":[{\"containerPort\":80}],\"essential\":true}]'", seca('== 2)', '== 3)')), 'You describe an image and its size (0.25 vCPU, 512 MB). To run it: <code>aws ecs run-task --launch-type FARGATE --network-configuration …</code> — no EC2 instance to manage.'),
    ('B3 · As a function (Lambda)', code('bash', 'terminal', "cat > app.py <<'PY'\ndef handler(event, context):\n    return {\"statusCode\": 200, \"body\": \"TiffinGo menu: dal, roti, paneer\"}\nPY\nzip fn.zip app.py\naws lambda create-function --function-name menu-fn --runtime python3.12 --handler app.handler \\\n  --role $ROLE --zip-file fileb://fn.zip --memory-size 128 --timeout 5", seca('== 3)', '== 4)')), 'Only 214 bytes of code. On a real account run <code>aws lambda invoke --function-name menu-fn out.json && cat out.json</code> to see the menu; the first call is a cold start.')],
    cleanup='<code>aws lambda delete-function</code>, <code>aws ecs deregister-task-definition</code> + <code>delete-cluster</code>, <code>aws ec2 terminate-instances</code>, <code>aws iam delete-role</code>. Nothing else is created.')

mist = mistakes([
    ['Calling a ticket-driven VMware cluster a “private cloud”.', 'Both use VMs.', 'Check the five NIST characteristics; add self-service, automation and metering.'],
    ['Saying “containers replace VMs”.', 'Containers are lighter.', 'In the cloud, containers usually run on VMs; choose per workload.'],
    ['Running a Windows app in a Linux container.', 'Containers look like mini-OSes.', 'Containers share the host kernel: Windows apps need Windows containers or a VM.'],
    ['Putting a 20-minute job in Lambda.', 'Serverless sounds universal.', 'Lambda stops at 15 minutes; use Fargate/ECS, Batch or Step Functions.'],
    ['Ignoring cold starts for a latency-critical API.', 'Tests hit warm functions.', 'Measure p99; use provisioned concurrency, smaller packages, or containers.'],
    ['Lift-and-shifting to VMs and expecting cloud savings automatically.', 'VMs in the cloud billed 24×7.', 'Right-size, schedule off-hours, use Auto Scaling or move to containers/serverless.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA (Linux & Cloud)', 'Virtualization vs cloud computing; Docker containers.'], ['AWS CLF-C02', 'Compute choices: EC2 vs containers (ECS/EKS/Fargate) vs Lambda; shared responsibility per model.'], ['AZ-900', 'VMs vs containers vs Functions; Azure Container Instances.'], ['Google Cloud Digital Leader', 'Compute Engine vs GKE vs Cloud Run; modernization paths.']], minw=520) + '\n  <h3>Exam-style questions with explanations</h3>\n' + \
    qx('1. Which statement is correct?', ['Virtualization and cloud computing are the same', 'Cloud computing is a service model usually built on virtualization plus automation', 'Containers are a type of hypervisor', 'Cloud requires containers'], 1, 'Virtualization is the technology; cloud adds self-service, elasticity and metering and delivers it as a service.') + \
    qx('2. A team wants to run containers without managing any EC2 instances. Which AWS service?', ['Amazon EC2', 'AWS Fargate', 'Amazon EBS', 'AWS Outposts'], 1, 'Fargate is serverless compute for ECS and EKS containers.') + \
    qx('3. Which compute option charges nothing when there are no requests?', ['EC2 on-demand', 'AWS Lambda', 'Dedicated Hosts', 'Reserved Instances'], 1, 'Lambda bills per request and duration; idle costs nothing.') + \
    qx('4. Why can a Linux container not run a Windows application?', ['Too little memory', 'It shares the Linux host kernel', 'No network', 'Licensing only'], 1, 'Containers share the host kernel; Windows binaries need a Windows kernel.') + \
    qx('5. A VMware cluster where VMs are created by admins after a ticket is missing which NIST characteristics?', ['Resource pooling only', 'On-demand self-service, rapid elasticity and measured service', 'Broad network access only', 'None'], 1, 'Virtualization provides pooling; the others need automation and metering.')

proj = miniproject('Mini project: one API, three deployments, one comparison table',
    'Deploy the TiffinGo menu API as an EC2 VM, an ECS Fargate container and a Lambda function, then measure and compare them like an architect.',
    ['<b>Code:</b> a tiny Flask/FastAPI app returning the menu as JSON, plus <code>handler()</code> for Lambda (use Mangum to wrap FastAPI, or a plain handler).',
     '<b>VM:</b> launch t3.micro with user data that installs Python and runs the app with systemd (Lesson 4.4); record time from launch to first successful <code>curl</code>.',
     '<b>Container:</b> write a Dockerfile (<code>FROM python:3.12-slim</code>), build, push to ECR (<code>aws ecr create-repository</code>, <code>docker push</code>), run on Fargate with a public IP; record image size and time to first response.',
     '<b>Function:</b> zip and create the Lambda, add a function URL (<code>aws lambda create-function-url-config --auth-type NONE</code>); record cold and warm latency with <code>curl -w "%{time_total}"</code>.',
     '<b>Load:</b> run <code>hey -n 2000 -c 50</code> (or <code>ab</code>) against each; note p95 latency and errors.',
     '<b>Cost:</b> use the AWS Pricing Calculator for 1 million requests/month for each option.',
     '<b>Report:</b> a table — image size, start time, p95, monthly cost, what you must patch — and your recommendation for TiffinGo. Clean up everything.'],
    'A comparison table with measured numbers and a one-paragraph recommendation.', 'This lesson + 2.1 IaaS + Linux/Docker course + Lesson 2.4 (serverless).')

assemble_v2(HERE, story_h2='“We already have VMware — isn’t that a cloud?”', hook_html=hk,
    narration='At TiffinGo’s planning meeting, the old IT head, a new developer and the CFO each use “cloud”, “VM” and “Docker” to mean different things. Before choosing anything, the words must be separated.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Virtualization vs cloud computing vs containers',
    formal='<b>Virtualization</b> is a technology that creates virtual instances of computing resources — servers, storage, networks — on physical hardware, typically through a hypervisor. <b>Cloud computing</b> is a model for enabling ubiquitous, convenient, on-demand network access to a shared pool of configurable computing resources that can be rapidly provisioned and released with minimal management effort (NIST SP 800-145); it usually relies on virtualization plus automation, self-service and metering. A <b>container</b> is a lightweight, OS-level virtualization unit that packages an application with its dependencies and runs as isolated processes sharing the host kernel.',
    simple='Virtualization splits hardware. Cloud sells those pieces as a self-service, pay-per-use utility. Containers package an app so it runs the same anywhere, sharing the machine’s kernel.',
    interview=['“Virtualization is a technology — a hypervisor splitting one server into VMs. Cloud computing is a delivery model with self-service, broad network access, pooling, rapid elasticity and measured service; it is usually built on virtualization plus automation and billing.”', '“A virtualized data centre where admins create VMs after a ticket is not a cloud; it becomes a private cloud only with self-service, automation and metering.”', '“VMs have their own kernel and are GBs; containers share the host kernel, are MBs and start in milliseconds; serverless hides servers entirely — Lambda and Fargate run each workload in a Firecracker micro-VM.”'],
    terms_rows=[('Virtualization', 'Technology: split hardware into virtual resources.'), ('Cloud computing', 'Service model: on-demand, elastic, metered.'), ('Private cloud', 'Cloud model for one organization.'), ('Container', 'App + files, shared kernel.'), ('Orchestrator', 'Runs containers across machines (Kubernetes).'), ('Serverless', 'No servers to manage, pay per use.'), ('Micro-VM', 'Tiny fast-booting VM (Firecracker).'), ('Bare-metal instance', 'Cloud server without a hypervisor.')],
    exam='“Virtualization vs cloud” and “VM vs container” appear in almost every fresher interview and in C-DAC exams. Answer with the NIST five and the kernel/size/start-time contrast.',
    picture_h2='One stack, three ideas', picture_html=picture,
    how_h2='What the cloud adds, and one app three ways', how_intro='Two animations: the cloud control plane around the hypervisor, and the same API as a VM, a container and a function.', how_anim=REQ + TSA,
    parts_h2='The big comparisons', parts_html=parts,
    after_picture=[('types', 'Types, one by one', 'Seven ways to run an app, one by one', build_types(FC))], lv='',
    myth_rows=[('Virtualization = cloud.', 'Cloud needs self-service, elasticity and metering too.', 'NIST figure.'), ('Containers replace VMs.', 'In clouds, containers mostly run on VMs.', 'Deep dive.'), ('Serverless means no servers.', 'Servers exist; you just do not manage them (Firecracker micro-VMs).', 'Animation 3.'), ('Cloud needs virtualization.', 'Bare-metal instances are cloud too.', 'Deep dive.')],
    extra_secs=[('deep', 'Deep dive', 'Necessary vs sufficient, containers on VMs, Firecracker in numbers, decision guide', DEEP)],
    clouds_html=clouds, proof_h2='Real proof: same kernel, milliseconds, megabytes', proof_intro='All outputs are real, from our Ubuntu 24.04 lab machine on 10 Nov 2026 (image sizes read live from the Alpine and Ubuntu download servers).', proof_steps=proof,
    practical_html=PRAC, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Explain why virtualization is not the same as cloud using the NIST characteristics.', 'Explain seven ways to run an app, from a virtualized data centre to micro-VMs.', 'Deploy one API as a VM, a container and a function using both the console and the CLI.', 'Explain what turns a virtualized data centre into a private cloud.', 'Compare VMs, containers and serverless functions on isolation, size, start time, management and billing.', 'Explain how Lambda and Fargate use Firecracker micro-VMs.', 'Deploy one API as an EC2 instance, an ECS Fargate task definition and a Lambda function with the CLI.'],
    next_html='<a href="../06-pros-cons-consolidation-and-hypervisor-security/">4.6 Pros, cons, consolidation and hypervisor security</a>.',
    pre='<b>Before you start:</b> <a href="../02-server-hardware-and-os-level-virtualization/">4.2 Server, hardware and OS-level virtualization</a> and <a href="../../01-introduction/01-what-is-cloud-computing/">1.1 What is cloud computing</a>.')
