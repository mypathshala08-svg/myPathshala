import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
sys.path.insert(0, HERE)
from _types import build as build_types
from _prac import PRAC
C = 'l46.txt'; CA = 'l46_aws.txt'
def sec(a, b=None): return capsec(C, a, b)
def seca(a, b=None): return capsec(CA, a, b)

hk = hook('If another company’s VM runs on the same physical server as yours, can it read your data?',
    'Normally no — the hypervisor keeps VMs apart. But in 2018 <b>Meltdown and Spectre</b> showed that CPU caches shared by VMs could leak secrets, and in 2015 the <b>VENOM</b> bug let code in a VM attack the hypervisor through a virtual floppy controller. In this lesson we read our own lab server’s CPU security report (<b>19 known side-channel entries</b>, each “Not affected” or “Mitigation”), calculate what consolidation saves (<b>5 servers at 8.2% → 1 host at 41%, ≈10,512 kWh a year</b>), and harden the parts AWS lets <i>you</i> control with the CLI.',
    ['Advantages and disadvantages of virtualization — honestly.', 'Server consolidation step by step, with real numbers.', 'Hypervisor security: VM escape, side channels, hyperjacking, sprawl — and how clouds defend.'])

def story_scene():
    o = t(180, 12, 'Two questions at the board meeting', 9, 'ink', bold=True)
    o += box(8, 22, 168, 100, 'green', rx=8) + ic('chart', 80, 28, 0.9) + t(92, 66, 'CFO', 8.6, 'ink', bold=True) + t(92, 82, '“How much do we save if we', 7, 'ink2') + t(92, 94, 'merge our 5 servers?”', 7, 'ink2')
    o += box(184, 22, 168, 100, 'red', rx=8) + ic('shield', 256, 28, 0.9) + t(268, 66, 'Security officer', 8.6, 'ink', bold=True) + t(268, 82, '“Who else is on that host,', 7, 'ink2') + t(268, 94, 'and can they see our data?”', 7, 'ink2')
    o += t(180, 140, 'Both are right to ask. Virtualization has a price list and a risk list.', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Two people: the CFO asking how much merging five servers saves, and a security officer asking who else is on the host and whether they can see the data.', story_scene(), 'Benefits, costs and <tspan font-weight="700" class="s-acc">risks of sharing one machine</tspan>.', h=160)
dialogue = '''R> Sir, our five old office servers — mail, website, accounts, HR and backup — are mostly idle. The CFO wants them merged.
A> That is server consolidation, the original reason virtualization became popular. We measure, size, place, migrate and switch off. We will calculate the savings.
K> But the security officer is worried. If all five run on one host, one hacked VM could reach the others?
A> That is the VM escape risk. And on a public cloud your VM shares hardware with strangers, so side channels matter too. Every benefit has a cost.
R> So we need the full balance sheet.
A> Exactly: pros, cons, consolidation with numbers, and how hypervisors and clouds are defended — and what is still your job.'''

# ---------------------------------------------------------------- figures
def consfig():
    o = t(320, 16, 'Server consolidation: TiffinGo’s five office servers (real calculation from our lab)', 11, 'ink', bold=True)
    apps = [('Mail', 8), ('Website', 15), ('Accounts', 5), ('HR', 3), ('Backup', 10)]
    o += t(150, 40, 'Before: 5 physical servers', 9, 'ink', bold=True)
    for i, (n, p) in enumerate(apps):
        x = 24 + i * 54
        o += box(x, 52, 46, 120, 'card', rx=5) + box(x + 4, 168 - p * 1.12, 38, p * 1.12, 'red', rx=2) + t(x + 23, 164 - p * 1.12, f'{p}%', 7.4, 'ink', bold=True) + t(x + 23, 186, n, 7.2, 'ink')
    o += t(150, 206, 'average CPU used 8.2% · 5 × 300 W · 5 licences · 5 to patch', 7.4, 'ink2')
    o += arrow(296, 112, 344, 112) + t(320, 104, 'P2V', 7.4, 'ink', bold=True)
    o += t(480, 40, 'After: 1 host, 5 VMs', 9, 'ink', bold=True)
    o += box(380, 52, 200, 120, 'card', rx=6)
    y = 168
    for n, p in apps:
        h = p * 2.6
        y -= h
        o += box(390, y, 120, h, 'blue', rx=2) + t(450, y + h / 2 + 2.4, f'{n} {p}%', 6.2 if p > 4 else 5.6, 'ink', bold=True)
    o += t(545, 120, '41% used', 8.4, 'green', bold=True) + t(545, 134, '+ headroom', 7, 'ink2')
    o += t(480, 186, 'hypervisor', 7.2, 'ink') + t(480, 206, '1 × 300 W · fewer boxes to patch', 7.4, 'ink2')
    o += box(20, 220, 600, 52, 'green', rx=8) + t(320, 240, 'Saved: 4 servers × 300 W = 1,200 W ≈ 10,512 kWh per year — plus rack space, cooling, network ports and hardware refresh cost.', 7.8, 'ink', bold=True)
    o += t(320, 258, 'Target 60–70% average on a host: enough headroom for peaks and for taking one host out for maintenance (N+1).', 7.4, 'ink2')
    return o
CONS = bigfig('Bar chart: before consolidation, five servers (Mail 8%, Website 15%, Accounts 5%, HR 3%, Backup 10% CPU, average 8.2%). After P2V, one host runs all five as VMs at 41% CPU. Savings: 1,200 W, about 10,512 kWh per year, plus space and cooling.', consfig(), h=282)

def threatfig():
    o = t(320, 16, 'Where a virtualized server can be attacked', 11, 'ink', bold=True)
    o += box(20, 34, 180, 70, 'red', rx=8) + t(110, 54, 'Attacker’s VM', 9, 'ink', bold=True) + t(110, 70, '(a hacked VM, or a stranger', 7, 'ink2') + t(110, 82, 'on a public cloud host)', 7, 'ink2')
    o += box(230, 34, 180, 70, 'blue', rx=8) + t(320, 54, 'Your VM', 9, 'ink', bold=True) + t(320, 70, 'secrets in memory,', 7, 'ink2') + t(320, 82, 'disk, keys', 7, 'ink2')
    o += box(440, 34, 180, 70, 'violet', rx=8) + t(530, 54, 'Management plane', 9, 'ink', bold=True) + t(530, 70, 'vCenter, ESXi host client,', 7, 'ink2') + t(530, 82, 'cloud console + API keys', 7, 'ink2')
    o += box(20, 128, 600, 40, 'amber', rx=8) + t(320, 146, 'Hypervisor + virtual devices (emulated disk, NIC, floppy…)', 9, 'ink', bold=True) + t(320, 160, 'large code = large attack surface', 7.2, 'ink2')
    o += box(20, 190, 600, 36, 'card', rx=8) + t(320, 212, 'Shared physical CPU (caches, branch predictor, SMT siblings) · memory · disks', 8.6, 'ink', bold=True)
    pins = [(110, 104, 110, 128, '1'), (110, 226, 320, 104, '2'), (530, 104, 470, 128, '3'), (200, 69, 230, 69, '4')]
    for x1, y1, x2, y2, n in pins:
        o += f'<path d="M{x1},{y1} L{x2},{y2}" style="fill:none;stroke:#D64545;stroke-width:2;stroke-dasharray:4 3"/>'
    o += pin(122, 116, 1, 'red') + pin(200, 160, 2, 'red') + pin(500, 116, 3, 'red') + pin(215, 58, 4, 'red')
    rows = [('1 VM escape', 'bug in a virtual device lets guest code run in the hypervisor (VENOM 2015)'), ('2 Side channel', 'measure shared-cache timing to read another VM’s data (Spectre/Meltdown/L1TF 2018)'),
            ('3 Management plane', 'steal admin access, then control every VM (ESXiArgs ransomware 2023)'), ('4 Network', 'flat virtual network lets a hacked VM scan neighbours (fix: segmentation, Lesson 4.3)')]
    for i, (a, b) in enumerate(rows):
        o += t(24, 248 + i * 14, a, 7.6, 'red', anchor='start', bold=True) + t(130, 248 + i * 14, b, 7.4, 'ink', anchor='start')
    o += t(24, 312, '+ VM sprawl (forgotten unpatched VMs), image/snapshot leaks, and hyperjacking (a malicious hypervisor installed under the OS).', 7.4, 'ink2', anchor='start')
    return o
THREAT = bigfig('Threat map: an attacker’s VM, your VM and the management plane above a hypervisor with virtual devices, above shared physical CPU and memory. Four numbered attack paths: VM escape through a virtual device bug, side channels through shared CPU caches, management-plane compromise, and network attacks between VMs. Plus VM sprawl, image leaks and hyperjacking.', threatfig(), h=322)

picture = ('  <p>Virtualization gives big savings and flexibility — and adds a new layer that must be run, paid for and defended. First, the most famous benefit, with numbers:</p>\n' + CONS +
           '\n  <h3>The new attack surface</h3>\n  <p>The hypervisor sits under every VM. If it fails or is broken into, every VM on that host is affected. These are the paths attackers use:</p>\n' + THREAT)

# ---------------------------------------------------------------- animation 1: consolidation project
CN = {'m': (4, 54, 54, 50, 'chart', 'Measure', '30 days'), 's': (64, 54, 54, 50, 'meter', 'Right-size', 'vCPU, RAM'), 'p': (124, 54, 54, 50, 'app', 'Place', 'bin-packing'),
      'mig': (184, 54, 54, 50, 'server', 'Migrate', 'P2V'), 'off': (244, 54, 54, 50, 'gear', 'Retire', 'old boxes'), 'mon': (304, 54, 52, 50, 'shield', 'Monitor', 'headroom')}
CS = [dict(on=['m'], hot='m', move=None, head='Step 1 · Measure real usage', text='Collect CPU, RAM, disk I/O and network for every server for weeks, including', text2='month-end peaks. Our five: 8, 15, 5, 3 and 10% CPU — average 8.2%.', svc='Tools: VMware Aria/vRealize, Azure Migrate discovery, AWS Migration Evaluator'),
      dict(on=['m', 's'], hot='s', move=(58, 79, 64, 79, ''), head='Step 2 · Right-size each future VM', text='Give each VM what it really needs (+ a margin), not what the old box had.', text2='A 16-core server using 5% becomes a 2-vCPU VM.', svc='Biggest single saving in most projects'),
      dict(on=['m', 's', 'p'], hot='p', move=(118, 79, 124, 79, ''), head='Step 3 · Place VMs on hosts (bin packing)', text='Fit VMs onto as few hosts as possible while keeping a target (60–70% CPU)', text2='and separating VMs that must not fail together (anti-affinity).', svc='Never put both database replicas on one host'),
      dict(on=['m', 's', 'p', 'mig'], hot='mig', move=(178, 79, 184, 79, ''), head='Step 4 · Migrate (P2V)', text='Convert each physical server to a VM (Lesson 4.4): copy disks, change drivers,', text2='test, cut over in a maintenance window, keep the old box for rollback.', svc='VMware Converter, virt-v2v, Azure Migrate, AWS MGN'),
      dict(on=['m', 's', 'p', 'mig', 'off'], hot='off', move=(238, 79, 244, 79, ''), head='Step 5 · Retire the old hardware', text='Wipe disks securely, cancel support contracts and licences, free rack space.', text2='Our case: 4 servers × 300 W = 1,200 W ≈ 10,512 kWh saved per year.', svc='Savings appear only when the old boxes are really switched off'),
      dict(on=list(CN), hot='mon', move=(298, 79, 304, 79, ''), head='Step 6 · Monitor and keep N+1', text='Watch host usage and contention (CPU ready time, memory ballooning). Keep', text2='enough spare capacity to move all VMs off one host for maintenance.', svc='Cloud equivalent: AWS Compute Optimizer and Azure Advisor right-sizing tips')]
CONA = flow_anim('A consolidation project in six steps', 'How the CFO’s question becomes a plan, from measurement to monitoring.', 'Server consolidation', 'Animation: measure usage, right-size VMs, place them on hosts by bin-packing with anti-affinity, migrate with P2V, retire old hardware, monitor and keep N+1 capacity.', CN, CS, hid='cons')

# ---------------------------------------------------------------- animation 2: VM escape and the layers that stop it
EN = {'att': (4, 54, 58, 50, 'user', 'Attacker', 'root in VM 1'), 'dev': (72, 54, 62, 50, 'disk', 'Virtual device', 'emulated'), 'qemu': (144, 54, 62, 50, 'gear', 'Device process', 'QEMU'),
      'sb': (216, 4, 62, 46, 'shield', 'Sandbox', 'seccomp, sVirt'), 'hv': (216, 104, 62, 46, 'chip', 'Hypervisor', 'kernel'), 'v2': (290, 54, 66, 50, 'server', 'VM 2', 'victim')}
ES = [dict(on=['att'], hot='att', move=None, head='Step 1 · Attacker controls one VM', text='They got root inside VM 1 (stolen password, unpatched app). Inside a VM, root', text2='is still only root of that VM. Their goal: reach VM 2 or the host.', svc='On a public cloud the attacker can simply rent a VM — assume hostile neighbours'),
      dict(on=['att', 'dev'], hot='dev', move=(62, 79, 72, 79, 'bad I/O'), head='Step 2 · Send malformed commands to a virtual device', text='They write crafted values to the emulated device’s I/O ports — like VENOM', text2='(CVE-2015-3456), which overflowed a buffer in QEMU’s virtual floppy controller.', svc='Every emulated device is code the attacker can talk to'),
      dict(on=['att', 'dev', 'qemu'], hot='qemu', move=(134, 79, 144, 79, 'exploit'), head='Step 3 · Code runs in the device process', text='The bug lets the attacker’s code run inside the QEMU process on the host —', text2='a “VM escape”. Now it tries to touch other VMs’ memory and files.', svc='This is why patch speed for hypervisors is critical'),
      dict(on=['att', 'dev', 'qemu', 'sb'], hot='sb', move=(175, 54, 230, 40, 'blocked'), head='Step 4 · Defence 1: sandbox the device process', text='Each VM’s QEMU runs as its own unprivileged user, with seccomp system-call filters', text2='and SELinux/AppArmor labels (sVirt): it can open only that VM’s disk files.', svc='libvirt does this by default; Firecracker uses a “jailer” for the same reason'),
      dict(on=['att', 'dev', 'qemu', 'sb', 'hv'], hot='hv', move=None, head='Step 5 · Defence 2: smaller attack surface', text='Remove devices nobody needs (no floppy!), use simple virtio devices, or move', text2='them into hardware: AWS Nitro and Firecracker expose only a few devices.', svc='Less code = fewer bugs. Firecracker: virtio-net, virtio-block, serial, keyboard'),
      dict(on=list(EN), hot='v2', move=None, head='Step 6 · VM 2 stays safe — if you also did your part', text='Layered defences stop the escape. Your part: patch hosts quickly (or let the cloud', text2='do it), keep guest OSes patched, and do not give VMs needless privileges.', svc='Defence in depth: no single layer is trusted completely')]
ESC = flow_anim('Anatomy of a VM escape — and the layers that stop it', 'Based on the real VENOM bug (2015). Six steps from a hacked VM to a protected neighbour.', 'VM escape', 'Animation: attacker with root in VM 1 sends malformed I/O to an emulated device, exploits a bug to run code in the QEMU process, is blocked by sandboxing (seccomp, sVirt), faces a minimal device set, and VM 2 stays safe.', EN, ES, hid='esc')

# ---------------------------------------------------------------- animation 3: side channels
def sc_frame(k):
    o = t(180, 12, ['Shared CPU cache', 'Mitigation in software', 'Mitigation by not sharing'][k], 9, 'ink', bold=True)
    o += box(14, 26, 150, 34, 'red', rx=5) + t(89, 47, 'Attacker VM', 8, 'ink', bold=True)
    o += box(196, 26, 150, 34, 'blue', rx=5) + t(271, 47, 'Your VM (secret key)', 8, 'ink', bold=True)
    if k < 2:
        o += box(14, 80, 332, 34, 'amber', rx=5) + t(180, 101, 'one physical core: L1 cache + branch predictor shared (SMT)', 7.6, 'ink', bold=True)
        o += packet(271, 60, 220, 80, 'loads') + packet(89, 60, 140, 80, 'timing')
    if k == 0:
        o += t(180, 134, 'Attacker times its own memory reads and infers which', 7.4, 'ink') + t(180, 146, 'cache lines your VM touched → leaks bits of the key.', 7.4, 'ink')
    if k == 1:
        o += box(140, 66, 80, 14, 'green', rx=3) + t(180, 76, 'flush on switch', 6.6, 'ink', bold=True)
        o += t(180, 134, 'Microcode + kernel: flush caches/buffers on VM switch,', 7.4, 'ink') + t(180, 146, 'barriers against speculation (our host: “Mitigation: …”).', 7.4, 'ink')
    if k == 2:
        o += box(14, 80, 150, 34, 'amber', rx=5) + t(89, 101, 'core A', 7.6, 'ink', bold=True) + box(196, 80, 150, 34, 'green', rx=5) + t(271, 101, 'core B (only yours)', 7.6, 'ink', bold=True)
        o += t(180, 134, 'Never place two customers on sibling threads of one core,', 7.4, 'ink') + t(180, 146, 'or rent a whole server (Dedicated Host / sole-tenant node).', 7.4, 'ink')
    return o
SCS = [('Side channel through a shared cache', 'Two VMs on sibling hardware threads share caches; timing differences leak data.', 'Spectre, Meltdown, L1TF, MDS (2018–2019) made this real.'),
       ('Patch: flush and fence', 'CPU microcode and kernels flush shared buffers and block risky speculation.', 'Costs some performance; check /sys/devices/system/cpu/vulnerabilities.'),
       ('Isolate: do not share cores', 'Clouds never split one core between customers; Dedicated Hosts remove neighbours entirely.', 'AWS: vCPUs of different customers never share a core; Dedicated Hosts for compliance.')]
SCA = anim_one('How it works', 'Side-channel attacks between VMs, and the two ways to stop them', 'No bug in the hypervisor needed — just shared hardware. Three frames.', 'Side channels', 'Animation: attacker and victim VMs share one CPU core’s cache, attacker infers secrets by timing; mitigation by flushing caches on switch; mitigation by giving each customer its own cores or a dedicated host.', cap_frames([sc_frame(k) for k in range(3)], SCS), [x[0] + '.' for x in SCS], delay=6000, hid='side')

parts = '  <h3>Advantages</h3>\n' + wwu([
    ('Server consolidation', 'Running many workloads as VMs on fewer physical hosts.', 'Typical servers were 5–15% busy; power, space and hardware were wasted.', 'Every virtualized data centre; our lab: 5 servers → 1 host.'),
    ('Isolation', 'A crash or compromise in one VM does not directly affect others.', 'Mixing apps on one OS let one bad app break everything.', 'Separate VMs for web, database, test.'),
    ('Fast provisioning and cloning', 'New servers from images in seconds–minutes (Lesson 4.4).', 'Buying and installing hardware took weeks.', 'Dev/test environments, Auto Scaling, VDI.'),
    ('Snapshots, backup and DR', 'Whole-machine images can be copied, replicated and restarted elsewhere.', 'Rebuilding a physical server after a disaster took days.', 'EBS snapshots, VMware SRM, Azure Site Recovery, AWS Elastic Disaster Recovery.'),
    ('Hardware independence and legacy support', 'VMs see standard virtual hardware, so they move between host models; old OSes keep running.', 'Old apps tied to dying hardware.', 'Running a Windows 2012 app on new servers; migrating between hosts.'),
    ('Energy and green IT', 'Fewer, busier servers use less power and cooling.', 'Data centres use a large share of electricity.', 'Our calculation: ≈10,512 kWh/yr saved.')]) + \
    '  <h3>Disadvantages</h3>\n' + wwu([
    ('Performance overhead', 'Some CPU, memory and I/O cost for the virtualization layer (small with VT-x, virtio, Nitro).', 'Trapping and emulation take time.', 'Latency-critical trading, HPC; use bare metal or SR-IOV.'),
    ('Host is a single point of failure', 'One host failure stops all its VMs.', 'Consolidation puts eggs in one basket.', 'Mitigate with HA clusters, anti-affinity, multiple AZs.'),
    ('Noisy neighbours / contention', 'VMs compete for CPU, cache, disk and network.', 'Overcommit and shared hardware.', 'Watch CPU-ready, steal time (%st in top); right-size; dedicated instances.'),
    ('VM sprawl', 'Too many forgotten VMs because creating them is easy.', 'No cost or effort to create → no reason to delete.', 'Unpatched, unknown VMs become security holes and cost money; tag and expire them.'),
    ('Licensing and skills complexity', 'Licences may count physical cores or hosts; admins need new skills.', 'Vendors price per socket/core/host.', 'Windows Server, Oracle, SQL Server on virtual hosts; Broadcom-era VMware licensing changes.'),
    ('New attack surface', 'Hypervisor, virtual devices and management tools can be attacked.', 'More layers = more code.', 'VM escape, side channels, ESXi ransomware (figure above).')]) + \
    '  <h3>Defences you can choose</h3>\n' + wwu([
    ('Confidential computing', 'VM memory encrypted by the CPU so even the host/hypervisor cannot read it.', 'Protect data in use from a compromised or curious host.', 'AMD SEV-SNP, Intel TDX; AWS Nitro Enclaves, Azure and GCP confidential VMs.'),
    ('Dedicated host / sole tenancy', 'A whole physical server reserved for one customer.', 'Compliance and per-socket licensing; no neighbours.', 'AWS Dedicated Hosts, Azure Dedicated Host, GCP sole-tenant nodes.')])

DEEP = ('  <h3>Real incidents that shaped hypervisor security</h3>\n' + table(['Year', 'Name', 'What happened', 'Lesson learned'], [
    ['2015', 'VENOM (CVE-2015-3456)', 'Buffer overflow in QEMU’s virtual floppy controller allowed guest-to-host code execution', 'Remove unused virtual devices; sandbox device processes'],
    ['2018', 'Meltdown / Spectre', 'CPU speculative execution leaked memory across processes and VMs', 'Hardware itself can break isolation; patch microcode + kernels'],
    ['2018', 'L1TF / Foreshadow', 'Leaked L1 cache data between VMs on sibling hyper-threads', 'Do not share a core between untrusted VMs'],
    ['2023', 'ESXiArgs ransomware', 'Mass attacks on internet-exposed, unpatched ESXi hosts (OpenSLP, CVE-2021-21974) encrypted VM files', 'Never expose management interfaces; patch hosts']], minw=640) +
    '\n  <h3>How the big clouds defend the hypervisor</h3>\n  <ul><li><b>AWS Nitro:</b> networking, storage and management moved to dedicated Nitro cards; a minimal KVM-based hypervisor; the Nitro system is designed with <b>no operator access</b> — no SSH or console for AWS staff to reach customer memory. Hypervisor updates are often applied live, without rebooting guests.</li>'
    '<li><b>Core isolation:</b> EC2 does not let vCPUs of different customers share a physical core’s hyper-threads; Azure and GCP use similar core scheduling.</li><li><b>Firecracker:</b> tiny device model plus a jailer process for Lambda/Fargate micro-VMs.</li>'
    '<li><b>Confidential VMs:</b> memory encrypted by the CPU (AMD SEV-SNP, Intel TDX) on Azure, Google Cloud and AWS; AWS Nitro Enclaves isolate secrets inside an instance.</li></ul>\n'
    '  <h3>Shared responsibility for the virtualization layer</h3>\n' + table(['Layer', 'Your own VMware/KVM', 'Public cloud IaaS (EC2)'], [
    ['Physical hosts, firmware, hypervisor patching', 'you', 'cloud provider'], ['Side-channel mitigations on hosts', 'you (microcode, BIOS, kernel)', 'cloud provider'], ['Management plane security', 'you (vCenter, ESXi)', 'you: IAM users, MFA, keys'],
    ['Guest OS patching', 'you', 'you'], ['VM network segmentation', 'you', 'you: VPC, security groups'], ['Disk encryption', 'you', 'you choose; EBS encryption by default'], ['VM sprawl / inventory', 'you', 'you: tags, Config, budgets']], minw=600) +
    '\n  <h3>Consolidation maths you will be asked</h3>\n  <p><b>Consolidation ratio</b> = physical servers before ÷ hosts after (ours: 5:1; 10–20:1 is common). <b>vCPU:pCPU overcommit</b> of 3–4:1 is usual for general workloads but must be watched through CPU-ready/steal time. Plan hosts for <b>N+1</b>: if 4 hosts at 70% must survive one failure, the other 3 must absorb 4×70/3 ≈ 93% — too tight; aim for ≈60% or add a host.</p>')

clouds = vendor_tabs('<p><b>AWS:</b> Nitro System (cards + minimal hypervisor + no operator access), <b>Dedicated Hosts</b> and Dedicated Instances, <b>Nitro Enclaves</b>, AMD SEV-SNP on some instances, <b>EBS encryption by default</b>, <b>IMDSv2</b>; right-sizing with <b>Compute Optimizer</b>; sustainability data in the Customer Carbon Footprint Tool.</p>',
    '<p><b>Azure:</b> hardened Hyper-V hypervisor, <b>Azure Dedicated Host</b>, <b>Confidential VMs</b> (AMD SEV-SNP, Intel TDX), Trusted Launch (Secure Boot + vTPM), Azure Advisor right-sizing, Emissions Impact Dashboard.</p>',
    '<p><b>Google Cloud:</b> KVM-based hypervisor with hardened device emulation, <b>Shielded VMs</b> (Secure Boot, vTPM, integrity monitoring), <b>Confidential VMs</b>, <b>sole-tenant nodes</b>, gVisor sandbox, Active Assist recommendations, Carbon Footprint reports.</p>') + \
    cloud3([['Whole physical server', 'Dedicated Hosts', 'Dedicated Host', 'Sole-tenant nodes'], ['Encrypted VM memory', 'SEV-SNP instances, Nitro Enclaves', 'Confidential VMs', 'Confidential VMs'], ['Secure/verified boot', 'UEFI Secure Boot, NitroTPM', 'Trusted Launch', 'Shielded VMs'],
            ['Right-sizing advice', 'Compute Optimizer', 'Azure Advisor', 'Active Assist / Recommender'], ['Carbon reporting', 'Customer Carbon Footprint Tool', 'Emissions Impact Dashboard', 'Carbon Footprint']])

proof = [
    ('Step 1 · Our lab CPU’s side-channel report', code('bash', 'terminal', 'cd /sys/devices/system/cpu/vulnerabilities\nfor f in meltdown spectre_v1 spectre_v2 l1tf mds retbleed; do\n  printf "%-12s %s\\n" $f "$(cat $f)"\ndone\nls | wc -l', sec('== 1)', '== 2)')), 'The Linux kernel lists every known CPU side-channel issue and how it is handled on this machine: newer CPUs are “Not affected” by Meltdown, L1TF and MDS; Spectre needs software mitigations. Run this on any Linux VM — including an EC2 instance.'),
    ('Step 2 · The consolidation calculation', code('python', 'consolidate.py', 'apps = {"Mail": 8, "Website": 15, "Accounts": 5, "HR": 3, "Backup": 10}   # % CPU of one server each\nprint("before: 5 physical servers, average CPU used:", round(sum(apps.values())/5, 1), "%")\nprint("after : 1 host with 5 VMs, CPU used:", sum(apps.values()), "%")\nwatts = 300\nprint("power saved: 4 servers ×", watts, "W =", 4*watts, "W ≈", round(4*watts*24*365/1000), "kWh per year")', sec('== 2)')), 'The 300 W per server is an assumption for a typical 1U server; replace it with your servers’ measured power. Remember the host also needs headroom.')]

prac = practical('Part A runs on any Linux machine or cloud VM. Part B hardens the virtualization settings that <b>you</b> control in AWS. <b>Our Part B outputs come from the moto AWS emulator</b>; on a real account a Dedicated Host is billed per hour while allocated — release it immediately after the test.', [
    ('A1 · Check your CPU’s side-channel status', code('bash', 'terminal', 'grep . /sys/devices/system/cpu/vulnerabilities/*'), 'Run it on your laptop and on a cloud VM and compare.'),
    ('A2 · Am I a VM, and is my host busy?', code('bash', 'terminal', 'systemd-detect-virt        # kvm, amazon, microsoft, none…\ntop -bn1 | head -3          # %st = CPU time stolen by the hypervisor for other VMs'), 'A high %st (steal) on a cloud VM means noisy neighbours or a CPU-credit limit (t3 instances).'),
    ('A3 · Remove what you do not need', code('bash', 'terminal', '# KVM/libvirt: list a VM’s devices and remove unused ones (floppy, sound, USB tablet)\nvirsh dumpxml myvm | grep -E "<(disk|sound|input|controller) "\nvirsh detach-device myvm floppy.xml --config'), 'Smaller device set = smaller attack surface (VENOM lesson).'),
    ('B1 · Which hypervisor runs each instance type?', code('bash', 'terminal', "aws ec2 describe-instance-types --instance-types t3.micro m5.large t2.micro \\\n  --query 'InstanceTypes[].[InstanceType,Hypervisor]' --output text", seca('== 1)', '== 2)')), 'Current families run on Nitro; old ones like t2 on Xen. Prefer Nitro types for security and performance.'),
    ('B2 · Encrypt all new EBS volumes by default', code('bash', 'terminal', 'aws ec2 get-ebs-encryption-by-default\naws ec2 enable-ebs-encryption-by-default', seca('== 2)', '== 3)')), 'Per Region. Every new volume and snapshot is then encrypted with KMS — a stolen snapshot is useless.'),
    ('B3 · Require IMDSv2 on launch', code('bash', 'terminal', "aws ec2 run-instances --image-id $AMI --instance-type t3.micro \\\n  --metadata-options HttpTokens=required,HttpPutResponseHopLimit=1", seca('== 3)', '== 4)')), 'Blocks the classic attack where a vulnerable web app is tricked into fetching role credentials from the metadata service (Lesson 2.1).'),
    ('B4 · No neighbours: a Dedicated Host', code('bash', 'terminal', "aws ec2 allocate-hosts --availability-zone ap-south-1a --instance-family m5 --quantity 1\naws ec2 describe-hosts --host-ids $H \\\n  --query 'Hosts[].[HostId,AvailabilityZone,State,HostProperties.InstanceFamily]' --output text", seca('== 4)', '== 5)')), 'A physical server just for your account — for compliance or per-core licences. Expensive: use only when required.')],
    cleanup='<code>aws ec2 terminate-instances</code>, <code>aws ec2 release-hosts --host-ids $H</code> (billing stops only after release). Keep EBS encryption by default <b>on</b> in real accounts.')

mist = mistakes([
    ['Consolidating without measuring peaks.', 'Averages hide month-end spikes.', 'Measure for weeks, size for peak + headroom, keep N+1.'],
    ['Putting both database replicas on the same host.', 'Placement left to defaults.', 'Use anti-affinity rules / spread placement groups / different AZs.'],
    ['Exposing ESXi or vCenter to the internet.', 'Convenient remote admin.', 'VPN or bastion only, MFA, patch quickly.'],
    ['Leaving unused virtual devices (floppy, USB, sound) on server VMs.', 'Default templates.', 'Strip devices from templates; use virtio.'],
    ['Never deleting test VMs (VM sprawl).', 'Creating is free and easy.', 'Tag owner + expiry; scheduled clean-up; AWS Config / budgets alerts.'],
    ['Assuming the cloud patches your guest OS.', 'The provider patches the hypervisor.', 'Guest OS patching is yours (SSM Patch Manager, Azure Update Manager).'],
    ['Ignoring steal time on cloud VMs.', 'App looks slow for “no reason”.', 'Check %st; switch from burstable to fixed-performance types or larger sizes.'],
    ['Buying Dedicated Hosts “for security” by default.', 'Fear of neighbours.', 'Nitro isolation is strong; use dedicated hosts only for licensing/compliance needs.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA (Linux & Cloud)', 'Pros and cons of virtualization; server consolidation; hypervisor security.'], ['AWS CLF-C02', 'Shared responsibility; Dedicated Hosts vs Dedicated Instances; EBS encryption; sustainability pillar.'], ['AZ-900', 'Shared responsibility; Azure Dedicated Host; confidential computing basics.'], ['Google Cloud Digital Leader', 'Shielded and Confidential VMs; sole tenancy; sustainability.']], minw=520) + '\n  <h3>Exam-style questions with explanations</h3>\n' + \
    qx('1. The main business benefit of server consolidation is…', ['more physical servers', 'higher utilization and lower hardware, power and space costs', 'no need for backups', 'faster CPUs'], 1, 'Many under-used servers become VMs on fewer, busier hosts.') + \
    qx('2. An attacker’s code in a VM runs on the host through a virtual device bug. This is…', ['phishing', 'VM escape', 'DDoS', 'SQL injection'], 1, 'VENOM (2015) is the classic example.') + \
    qx('3. In AWS, who patches the hypervisor of EC2 hosts?', ['the customer', 'AWS', 'both equally', 'nobody'], 1, 'Security “of” the cloud — physical hosts and virtualization — is AWS’s responsibility; the guest OS is yours.') + \
    qx('4. A company must use per-physical-core software licences and see the host’s sockets/cores. Which option?', ['Spot Instances', 'Dedicated Hosts', 'Lambda', 'Reserved Instances only'], 1, 'Dedicated Hosts give visibility of physical cores and sockets for bring-your-own-licence.') + \
    qx('5. Which risk comes from VMs being too easy to create?', ['side channel', 'VM sprawl', 'hyperjacking', 'live migration'], 1, 'Forgotten, unpatched VMs cost money and become entry points.') + \
    qx('6. Which technology protects VM memory even from the host and hypervisor?', ['VLAN', 'Confidential computing (AMD SEV-SNP / Intel TDX)', 'RAID 1', 'NAT gateway'], 1, 'The CPU encrypts guest memory with keys the hypervisor cannot read.')

proj = miniproject('Mini project: a consolidation and security assessment report',
    'Act as TiffinGo’s cloud consultant: measure five “servers”, design the consolidated layout, and produce a hardening checklist with evidence.',
    ['<b>Measure:</b> run five Docker containers or five small VMs, each with a different load (<code>stress-ng --cpu 1 --cpu-load 8</code>, 15, 5, 3, 10); collect CPU with <code>docker stats</code> or <code>sar</code> every minute for an hour.',
     '<b>Size and place:</b> in a spreadsheet, compute averages and peaks, choose VM sizes, and place them on hosts at a 60% target with N+1. Mark anti-affinity pairs.',
     '<b>Savings:</b> extend <code>consolidate.py</code> to read your CSV and compute servers saved, kWh and ₹ per year (use your electricity tariff).',
     '<b>Security evidence:</b> on each Linux machine, save <code>grep . /sys/devices/system/cpu/vulnerabilities/*</code> and <code>systemd-detect-virt</code>.',
     '<b>AWS checks:</b> run practical B1–B3 on your account (or the emulator) and record EBS-encryption-by-default and IMDSv2 status for every instance (<code>aws ec2 describe-instances --query "Reservations[].Instances[].MetadataOptions.HttpTokens"</code>).',
     '<b>Report:</b> one page each for savings, risks (use the threat map), and a 10-item hardening checklist (patching, MFA on management plane, no exposed ESXi, device minimization, encryption, IMDSv2, tagging/expiry, anti-affinity, backups, monitoring steal time).'],
    'A three-page report with numbers, a placement diagram and a checklist backed by command output.', 'Lessons 4.1–4.6 + Linux performance tools + Module 9 security (later).')

assemble_v2(HERE, story_h2='Five idle servers and one worried security officer', hook_html=hk,
    narration='TiffinGo’s office still runs five old physical servers. The CFO wants them merged to save money; the security officer wants to know what sharing one machine really risks.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Advantages, disadvantages, consolidation and hypervisor security',
    formal='<b>Server consolidation</b> is the practice of running multiple workloads, previously on separate physical servers, as virtual machines on fewer physical hosts to increase utilization and reduce hardware, energy and operating costs. <b>Hypervisor security</b> is the protection of the virtualization layer — the hypervisor, its virtual devices and its management interfaces — against threats such as VM escape, side-channel attacks between co-resident VMs, hyperjacking and management-plane compromise, so that isolation between virtual machines is preserved.',
    simple='Consolidation = fewer, busier machines instead of many idle ones. Hypervisor security = making sure the layer that separates VMs cannot be broken, bypassed or taken over.',
    interview=['“Virtualization’s advantages are consolidation, isolation, fast provisioning, snapshots and DR, hardware independence and energy savings; the disadvantages are some overhead, the host as a single point of failure, noisy neighbours, VM sprawl, licensing complexity and a new attack surface.”', '“Server consolidation means measuring real usage, right-sizing, placing VMs on fewer hosts with headroom and anti-affinity, migrating with P2V and retiring old hardware — in my lab five servers averaging 8.2% CPU fit on one host at 41%.”', '“Key hypervisor threats are VM escape through device bugs like VENOM, side channels like Spectre and L1TF, hyperjacking and management-plane attacks; defences include minimal device models, sandboxing, core isolation, patching, secure boot and confidential computing.”'],
    terms_rows=[('Consolidation ratio', 'Servers before ÷ hosts after.'), ('Overcommit', 'More vCPU/RAM promised than physically present.'), ('N+1', 'Capacity to lose one host safely.'), ('Steal time', 'CPU time taken by other VMs.'), ('VM escape', 'Breaking out of a VM into the host.'), ('Side channel', 'Leak via shared hardware timing.'), ('Hyperjacking', 'Malicious hypervisor under the OS.'), ('VM sprawl', 'Uncontrolled forgotten VMs.'), ('Confidential VM', 'CPU-encrypted VM memory.'), ('Dedicated Host', 'Whole physical server for one customer.')],
    exam='Shared responsibility: AWS patches hosts and hypervisors (“security of the cloud”); you patch guest OSes, configure security groups, IAM and encryption (“security in the cloud”).',
    picture_h2='Savings in one picture, risks in another', picture_html=picture,
    how_h2='A consolidation project, step by step', how_intro='How the CFO’s question becomes a plan — from measurement to monitoring.', how_anim=CONA,
    parts_h2='Advantages, disadvantages and defences', parts_html=parts,
    after_picture=[('types', 'Threats, one by one', 'Six threats to a virtualized environment, one by one', build_types(ESC, SCA))], lv='',
    myth_rows=[('VMs are perfectly isolated.', 'Device bugs and CPU side channels have broken isolation.', 'Deep dive incidents.'), ('Consolidation always saves money.', 'Only after old servers are retired and licences checked.', 'Animation step 5.'), ('In the cloud, security is the provider’s job.', 'Guest OS, IAM, network rules and encryption are yours.', 'Shared-responsibility table.'), ('A dedicated host is needed for security.', 'Mostly for licensing/compliance; Nitro isolates well.', 'Mistakes.')],
    extra_secs=[('deep', 'Deep dive', 'Real incidents, how clouds defend the hypervisor, shared responsibility, consolidation maths', DEEP)],
    clouds_html=clouds, proof_h2='Real proof: CPU security report and consolidation numbers', proof_intro='Real output from our Ubuntu 24.04 lab machine on 10 Nov 2026. The 300 W figure is a stated assumption.', proof_steps=proof,
    practical_html=PRAC, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['List and explain the advantages and disadvantages of virtualization.', 'Explain six threats (VM escape, side-channel, hyperjacking, management plane, sprawl, lateral movement) with real incidents and defences.', 'Harden a VM and an AWS account using both the UI and the CLI.', 'Plan a server consolidation in six steps and calculate savings.', 'Explain VM escape, side channels, hyperjacking, management-plane attacks and VM sprawl with real examples.', 'Explain how Nitro, Firecracker, core isolation and confidential computing protect VMs.', 'Turn on EBS encryption by default, require IMDSv2 and allocate a Dedicated Host with the AWS CLI.'],
    next_html='<a href="../../05-core-cloud-concepts/01-regions-availability-zones-and-edge-locations/">Module 5 · 5.1 Regions, Availability Zones and edge locations</a>.',
    pre='<b>Before you start:</b> <a href="../01-virtualization-and-hypervisors/">4.1</a>, <a href="../04-vm-provisioning-and-migration/">4.4</a> and <a href="../05-virtualization-vs-cloud-vs-containers/">4.5</a>.')
