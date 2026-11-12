"""Lesson 4.6 — hypervisor security threats, one by one (with defences)."""
from cloudkit import *

def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)

def mapfig():
    o = t(320, 16, 'Six threats to a virtualized environment — and where they strike', 11, 'ink', bold=True)
    items = [('1', 'VM escape', 'guest code breaks into the hypervisor', 'red'), ('2', 'Side-channel', 'secrets leak through shared CPU', 'red'), ('3', 'Hyperjacking', 'a fake hypervisor under the OS', 'violet'),
             ('4', 'Management-plane attack', 'steal the admin console / API keys', 'violet'), ('5', 'VM sprawl', 'forgotten, unpatched VMs', 'amber'), ('6', 'Lateral movement', 'hop from VM to VM on a flat network', 'amber')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 14 + (i % 3) * 206; y = 34 + (i // 3) * 82
        o += box(x, y, 198, 70, tn, rx=8) + pin(x + 14, y + 16, n) + t(x + 28, y + 20, a, 8.6, 'ink', anchor='start', bold=True) + t(x + 10, y + 46, b, 7.2, 'ink2', anchor='start')
    o += t(320, 218, 'Red: break the isolation itself · Violet: take over the layer below or above · Amber: caused by how VMs are operated.', 7.6, 'ink2')
    return o
MAP = bigfig('Map of six threats: 1 VM escape, 2 side-channel, 3 hyperjacking, 4 management-plane attack, 5 VM sprawl, 6 lateral movement, grouped by whether they break isolation, take over a layer, or come from operations.', mapfig(), h=230)

def T1(ESC):
    return vtype(1, 'VM escape', 'red',
        'A <b>VM escape</b> is an attack in which code running inside a virtual machine exploits a vulnerability in the hypervisor or its emulated devices to execute code on the host, breaking isolation and potentially reaching other VMs on the same host.',
        'A prisoner who finds a crack in the cell wall that leads into the guards’ room: from there, every other cell can be opened.',
        'Suppose one of TiffinGo’s VMs is hacked through an old web plugin. If the host still exposed an old emulated floppy controller with a known bug, the attacker could try to escape to the host and reach the billing VM. Patched hosts, removed devices and sandboxed device processes stop this.',
        'Real cases: VENOM (CVE-2015-3456, QEMU floppy controller), and VM-escape bugs regularly found in contests like Pwn2Own; defences: libvirt sVirt + seccomp, Firecracker jailer, minimal devices, prompt hypervisor patching (done by the provider in public clouds).',
        '', ESC,
        'always assume it is possible: patch hypervisors quickly, remove unused virtual devices, and keep guests patched so attackers never get the first foothold.',
        'you give guest VMs passthrough hardware or extra privileges without need — every extra device and permission is attack surface.',
        plain='Normally a program inside a virtual machine cannot touch anything outside it. A VM escape is when an attacker finds a bug that lets them break out of the VM and control the real machine underneath.',
        how=[('Get a foothold', 'The attacker gains code execution inside one VM (stolen password, unpatched app) — or simply rents a VM in a public cloud.'), ('Probe the device model', 'They talk to virtual devices (disk, NIC, floppy, USB, graphics) through I/O ports and memory-mapped registers.'), ('Trigger a bug', 'Malformed input overflows a buffer in the emulation code running on the host.'), ('Run code in the host process', 'The attacker now runs code in the VMM process (e.g. QEMU).'), ('Try to go further', 'From there they try to read other VMs’ memory or files, or escalate to the host kernel.'), ('Defences', 'Sandboxing of the VMM process (separate user, seccomp, SELinux/AppArmor), minimal device sets, IOMMU, fast patching.')],
        words=[('exploit', 'code that abuses a bug'), ('device model', 'the virtual hardware a hypervisor emulates'), ('buffer overflow', 'writing past the end of a memory area'), ('seccomp', 'a Linux filter that blocks dangerous system calls'), ('sVirt', 'SELinux labels that confine each VM’s process')],
        diff=table(['', 'VM escape', 'Container escape', 'Side-channel'], [['Boundary broken', 'hypervisor', 'shared kernel', 'none — data leaks through hardware'], ['Needs a software bug?', 'yes (hypervisor/device)', 'yes (kernel/runtime)', 'no (hardware behaviour)'], ['Typical fix', 'patch, sandbox, fewer devices', 'patch kernel, drop privileges, use micro-VMs', 'microcode, core isolation']], minw=560),
        where=['Multi-tenant clouds', 'Shared hosting and VDI', 'Malware analysis sandboxes (attackers try to escape them)'],
        realworld='VENOM (2015) let code in a guest overflow a buffer in QEMU’s virtual floppy controller — a device almost nobody used — affecting Xen, KVM and VirtualBox hosts until patched; it is why modern platforms strip unused devices.',
        pro='A VM-escape bug in the hypervisor is among the most valuable findings in security contests such as Pwn2Own, with prizes in the hundreds of thousands of dollars — a measure of how hard, and how damaging, they are.')

def T2(SCA):
    return vtype(2, 'Side-channel attacks between VMs', 'red',
        'A <b>side-channel attack</b> extracts secret information not by breaking software isolation but by measuring physical effects of shared hardware — cache timing, branch prediction, power use — so that a VM can infer data processed by another VM running on the same CPU.',
        'Guessing a neighbour’s PIN from the beeps of the ATM keypad: you never touch their card or the machine, you just listen carefully to something you both share.',
        'If TiffinGo’s payment-signing VM shared a CPU core with a hostile VM, cache timing could leak bits of its signing key. Clouds prevent this by never letting two customers share a core and by patching CPU microcode; for extra assurance TiffinGo could use a Dedicated Host.',
        'Spectre and Meltdown (2018), L1TF/Foreshadow (2018), MDS (2019); defences: CPU microcode updates, kernel mitigations, core scheduling (no SMT sharing between tenants), Dedicated Hosts / sole-tenant nodes, confidential VMs.',
        '', SCA,
        'you handle cryptographic keys or highly sensitive data on shared hardware — rely on provider core isolation, keep guests patched, consider dedicated or confidential instances.',
        'turning off kernel mitigations “for performance” on shared systems.',
        plain='Two virtual machines can share the same tiny memory inside a processor chip. By very precisely timing its own work, one VM can sometimes guess what the other is doing — and leak secrets — without breaking any rules of the software.',
        how=[('Co-location', 'Attacker and victim run on the same physical core or share caches.'), ('Prime', 'The attacker fills cache lines with its own data.'), ('Victim runs', 'The victim’s secret-dependent code evicts some lines.'), ('Probe', 'The attacker times reloading its data; slow = evicted = the victim touched that line.'), ('Infer', 'Repeated many times, patterns reveal bits of keys or memory (Spectre adds speculative execution to read beyond bounds).'), ('Defend', 'Flush buffers on VM switch, fence speculation, never share cores between tenants, dedicate hardware.')],
        words=[('cache', 'a small fast memory inside the CPU'), ('SMT / hyper-threading', 'two threads sharing one physical core'), ('speculative execution', 'the CPU guessing ahead and running instructions early'), ('microcode', 'firmware inside the CPU that can be updated')],
        diff=table(['', 'Side-channel', 'VM escape'], [['Breaks software isolation?', 'no', 'yes'], ['Root cause', 'shared hardware behaviour', 'bug in hypervisor code'], ['Fix lives in', 'CPU microcode, scheduling, hardware choice', 'hypervisor patches, sandboxing']], minw=480),
        where=['Multi-tenant public clouds', 'Shared VDI hosts', 'Browsers (JavaScript timers were coarsened after Spectre)'],
        realworld='When Meltdown and Spectre were disclosed in January 2018, AWS, Azure and Google patched and rebooted or live-migrated their entire fleets; AWS states that EC2 never lets vCPUs of different customers share a physical core’s hyper-threads.',
        pro='Run <code>grep . /sys/devices/system/cpu/vulnerabilities/*</code> on any instance: the kernel lists each known CPU issue and whether it is “Not affected”, “Mitigation: …” or “Vulnerable” — our lab shows 19 entries.')

def a_hj(k):
    o = t(180, 12, ['Normal boot chain', 'Hyperjacking: a rogue layer underneath', 'Secure + measured boot stop it'][k], 9, 'ink', bold=True)
    layers = [('Firmware (UEFI)', 'card'), ('Hypervisor (signed)', 'amber'), ('Guest OS', 'blue'), ('Apps', 'blue')]
    if k == 1:
        layers = [('Firmware (UEFI)', 'card'), ('ROGUE hypervisor', 'red'), ('Hypervisor / OS', 'amber'), ('Apps', 'blue')]
    for i, (n, tn) in enumerate(layers):
        y = 118 - i * 26
        o += box(60, y, 240, 22, tn, rx=4) + t(180, y + 15, n, 7.8, 'ink', bold=True)
    if k == 1:
        o += t(180, 152, 'the rogue layer sees and changes everything above it', 7.2, 'red', bold=True)
    if k == 2:
        o += t(180, 152, 'TPM records a hash of every stage for attestation', 7.2, 'green', bold=True) + t(30, 70, '✓ signature', 7, 'green', anchor='start', bold=True) + t(30, 82, 'checked', 7, 'green', anchor='start', bold=True)
    return o
A_HJ = cap([a_hj(k) for k in range(3)], [('Normal boot chain', 'Firmware starts a signed hypervisor, which starts the guest OS and apps.', 'Each layer trusts the one below.'), ('Hyperjacking', 'Malware installs its own thin hypervisor underneath (or replaces the real one).', 'It can watch and alter everything above, invisible to the OS.'), ('Secure and measured boot', 'Secure Boot refuses unsigned hypervisors; a TPM records hashes of each stage', 'so remote attestation can prove the chain is genuine.')],
    'Hyperjacking in action', 'Taking over the layer below the OS.', 'Hyperjacking', 'Animation: normal boot chain of firmware, hypervisor, OS, apps; a rogue hypervisor inserted below; secure boot and TPM measurement verifying each stage.', 'h3anim')
T3 = vtype(3, 'Hyperjacking (malicious hypervisor)', 'violet',
    '<b>Hyperjacking</b> is an attack in which an adversary installs a malicious hypervisor beneath an operating system, or replaces or tampers with the legitimate hypervisor, gaining control over all virtual machines and data above it while remaining hidden from them.',
    'A fake building manager who quietly replaces the real one: residents keep living normally, unaware that someone now holds every master key and reads every letter.',
    'If an attacker with physical or admin access replaced the hypervisor on TiffinGo’s on-premises host with a tampered build, every VM would be compromised. UEFI Secure Boot and TPM-based measured boot would refuse or flag the unsigned hypervisor.',
    'Research proof-of-concept “Blue Pill” (2006); real-world: attackers deploying malicious vSphere Installation Bundles (VIBs) to ESXi hosts for persistence (reported in 2022); defences: UEFI Secure Boot, TPM/vTPM, measured boot and attestation, signed hypervisor packages, hardware roots of trust (AWS Nitro Security Chip).',
    '', A_HJ,
    'you run your own hypervisors — enable Secure Boot for hosts, accept only signed packages and monitor for unexpected changes.',
    'hosts allow unsigned modules or community packages, or admin access to hosts is widely shared.',
    plain='An attacker secretly slips a fake “manager program” underneath the operating system. From there it can watch and control everything, while the operating system has no idea.',
    how=[('Gain high privilege', 'The attacker needs admin/root on the host, firmware access or physical access.'), ('Insert a layer', 'Install a thin malicious hypervisor that moves the running OS into a VM (Blue Pill idea), or plant a malicious module in the real hypervisor.'), ('Hide', 'The rogue layer intercepts what the OS sees, making itself invisible.'), ('Abuse', 'Read memory, steal keys, alter traffic of every VM.'), ('Defend: verify the chain', 'Secure Boot checks signatures of each boot stage; measured boot records hashes in a TPM for attestation; only signed modules allowed.')],
    words=[('UEFI Secure Boot', 'firmware feature that only starts signed boot software'), ('TPM', 'a security chip that records measurements of what booted'), ('attestation', 'proving to a remote party what software is running'), ('VIB', 'a software package installed into VMware ESXi')],
    diff=table(['', 'Hyperjacking', 'VM escape', 'Management-plane attack'], [['Attacker position', 'below / inside the hypervisor', 'inside a guest', 'at the admin console'], ['Usually needs', 'host admin or physical access', 'one guest + a bug', 'stolen credentials'], ['Best defence', 'secure/measured boot, signed code', 'patch, sandbox', 'MFA, no exposure, least privilege']], minw=560),
    where=['On-premises hypervisor hosts', 'Laptops (bootkits / hypervisor rootkits)', 'Firmware supply-chain attacks'],
    realworld='In 2022 Mandiant reported attackers installing malicious vSphere Installation Bundles on VMware ESXi hosts to gain persistent, hard-to-detect control of the hypervisor and its VMs; VMware responded with guidance to enforce Secure Boot and accept only signed bundles.',
    pro='Cloud providers anchor trust in their own hardware: the AWS Nitro Security Chip and Google’s Titan chip verify firmware and boot code before the host runs, so a customer never has to trust software it cannot see.')

def a_mp(k):
    o = t(180, 12, ['Admin console exposed to the internet', 'Attacker logs in / exploits it', 'Fix: no exposure, MFA, patching'][k], 9, 'ink', bold=True)
    o += box(130, 30, 100, 40, 'violet' if k < 2 else 'green', rx=6) + t(180, 48, 'vCenter / ESXi', 7.6, 'ink', bold=True) + t(180, 62, 'or cloud console', 6.8, 'ink2')
    for i in range(4):
        o += box(20 + i * 86, 100, 74, 30, 'red' if k == 1 else 'blue', rx=4) + t(57 + i * 86, 119, ('locked' if k == 1 else 'VM ' + str(i + 1)), 7.4, 'ink', bold=True)
        o += f'<path d="M180,70 L{57 + i * 86},100" style="stroke:#999;stroke-width:1.2"/>'
    if k == 0:
        o += box(10, 30, 90, 40, 'red', rx=6) + t(55, 54, 'internet', 7.6, 'ink', bold=True) + packet(100, 50, 130, 50, '')
    if k == 1:
        o += box(10, 30, 90, 40, 'red', rx=6) + t(55, 54, 'attacker', 7.6, 'ink', bold=True) + packet(100, 50, 130, 50, 'exploit') + t(180, 146, 'all VM files encrypted at once', 7.6, 'red', bold=True)
    if k == 2:
        o += box(250, 30, 100, 40, 'green', rx=6) + t(300, 48, 'VPN + MFA', 7.6, 'ink', bold=True) + t(300, 62, 'least privilege', 6.8, 'ink2') + t(180, 146, 'management reachable only from admin network', 7.4, 'green', bold=True)
    return o
A_MP = cap([a_mp(k) for k in range(3)], [('Exposed management', 'The hypervisor’s management interface is reachable from the internet', 'and not patched.'), ('One login controls every VM', 'The attacker exploits it (or uses stolen passwords/API keys) and encrypts', 'or deletes every VM at once — no need to break any VM.'), ('Fix', 'Keep management on a private admin network behind VPN, require MFA,', 'patch quickly, give admins only the rights they need.')],
    'Management-plane attack in action', 'Why attackers go for the console, not the VM.', 'Management plane', 'Animation: vCenter/ESXi exposed to the internet; attacker exploits it and encrypts all VMs; fix with private admin network, VPN, MFA and least privilege.', 'h4anim')
T4 = vtype(4, 'Management-plane attacks', 'violet',
    'A <b>management-plane attack</b> targets the interfaces used to administer the virtualized environment — hypervisor management consoles (vCenter, ESXi host client, Hyper-V Manager), cloud consoles, APIs and their credentials — so the attacker can create, change, snapshot, steal or destroy many VMs at once without breaking into any of them.',
    'Instead of picking the lock of each flat, the thief steals the building manager’s master-key cabinet.',
    'If an AWS access key with administrator rights from TiffinGo leaked on GitHub, an attacker could snapshot every database volume and copy it out, or delete every instance — no VM vulnerability needed. MFA, least-privilege IAM roles and no long-lived keys prevent this.',
    'Real case: ESXiArgs ransomware (Feb 2023) mass-encrypted internet-exposed, unpatched ESXi hosts via the OpenSLP flaw CVE-2021-21974; leaked cloud keys are a leading cause of cloud breaches. Defences: MFA, private admin networks, patching, IAM least privilege, AWS CloudTrail / Azure Activity Log monitoring.',
    '', A_MP,
    'always: treat hypervisor consoles and cloud root/admin accounts as the crown jewels.',
    'management ports are open to the internet, admin accounts are shared, or long-lived access keys are stored in code.',
    plain='Rather than attacking each virtual machine, the attacker steals the “remote control” that manages all of them — an admin login or API key — and then controls everything at once.',
    how=[('Find the console', 'Scan the internet for exposed ESXi/vCenter, or search code repositories for leaked cloud keys.'), ('Get in', 'Exploit an unpatched flaw, guess/steal passwords, or use a leaked key.'), ('Act at scale', 'Snapshot and copy disks, change security groups, create crypto-mining VMs, encrypt or delete VMs.'), ('Hide', 'Disable logging or create new admin users.'), ('Defend', 'Private management networks, MFA everywhere, least privilege, short-lived credentials (IAM roles), patching, audit logs with alerts.')],
    words=[('management plane', 'the tools and APIs used to control infrastructure'), ('MFA', 'multi-factor authentication: password + code/device'), ('least privilege', 'give only the permissions needed'), ('CloudTrail', 'AWS log of every API call')],
    diff=table(['', 'Management-plane attack', 'VM escape', 'Lateral movement'], [['Entry point', 'admin console / API keys', 'a guest VM', 'one compromised VM'], ['Blast radius', 'every VM it controls', 'one host', 'reachable VMs'], ['Key defence', 'MFA, no exposure, IAM', 'patching, sandboxing', 'segmentation']], minw=560),
    where=['On-premises VMware/Hyper-V estates', 'Cloud accounts (console, CLI keys)', 'Kubernetes API servers'],
    realworld='In February 2023 the ESXiArgs ransomware campaign encrypted VM files on thousands of internet-exposed VMware ESXi servers worldwide by exploiting CVE-2021-21974 in the OpenSLP service, a flaw for which a patch had existed since 2021.',
    pro='In AWS the management plane <i>is</i> IAM. A single policy with <code>"Action": "*"</code> on a CI user is functionally equivalent to an internet-exposed vCenter — audit with IAM Access Analyzer and replace keys with roles.')

def a_spr(k):
    o = t(180, 12, ['Creating VMs is easy…', '…so nobody deletes them', 'Fix: tags, expiry, inventory'][k], 9, 'ink', bold=True)
    n = [4, 12, 6][k]
    for i in range(n):
        old = k == 1 and i >= 4
        o += box(14 + (i % 6) * 56, 30 + (i // 6) * 44, 48, 36, 'red' if old else ('green' if k == 2 else 'blue'), rx=4) + t(38 + (i % 6) * 56, 46 + (i // 6) * 44, 'VM', 7.2, 'ink', bold=True) + t(38 + (i % 6) * 56, 58 + (i // 6) * 44, 'owner?' if old else ('tagged' if k == 2 else 'in use'), 6.2, 'ink2')
    o += t(180, 140, ['test VMs for a demo', '8 forgotten VMs · unpatched · still billed', 'owner + expiry tags · auto-stop · weekly report'][k], 7.6, 'red' if k == 1 else ('green' if k == 2 else 'ink'), bold=True)
    return o
A_SPR = cap([a_spr(k) for k in range(3)], [('Easy to create', 'A few test VMs are launched for a demo — in seconds, no approval.', 'Nothing wrong yet.'), ('Forgotten', 'Months later 8 VMs have no known owner: unpatched, still exposed,', 'still billed — the classic entry point and cost leak.'), ('Fix', 'Mandatory owner and expiry tags, automatic stop/delete of expired VMs,', 'and a regular inventory and cost report per owner.')],
    'VM sprawl in action', 'The risk that comes from virtualization being easy.', 'VM sprawl', 'Animation: four test VMs; months later twelve, eight with no owner, unpatched and billed; fixed with tags, expiry and inventory.', 'h5anim')
T5 = vtype(5, 'VM sprawl', 'amber',
    '<b>VM sprawl</b> is the uncontrolled growth of virtual machines — created easily and then forgotten — that remain running or stored without an owner, patching or monitoring, increasing cost, licence exposure and attack surface.',
    'A fridge in a shared office: everyone puts boxes in, nobody takes them out. Months later nobody knows whose they are, the space is full, and something has gone bad.',
    'TiffinGo’s developers launched 30 test instances during a hackathon. Six months later eight still run, unpatched, one with SSH open to the internet, costing ₹40,000 a month. Tag policies and an auto-stop schedule now catch this.',
    'Tools: AWS Config, Resource Groups and Tag Editor, AWS Budgets, Trusted Advisor, Instance Scheduler on AWS; Azure Policy and Advisor; GCP Recommender; VMware Aria Operations reclamation reports.',
    '', A_SPR,
    'you run any shared environment — enforce tags, budgets and scheduled clean-up from day one.',
    'test resources live in the same account as production with no tags or budgets.',
    plain='Because making virtual machines is so easy, people make many and forget about them. The forgotten ones keep costing money and, since nobody updates them, become easy targets for attackers.',
    how=[('Easy creation', 'Self-service lets anyone launch VMs in seconds.'), ('No ownership record', 'VMs are created without owner, project or expiry tags.'), ('Drift into neglect', 'People leave or projects end; VMs keep running.'), ('Risk builds', 'Missing patches, open ports, old credentials, licence and cost leakage.'), ('Defend', 'Tag policies (deny launch without tags), budgets and alerts, scheduled stop of non-production, periodic inventory and deletion.')],
    words=[('tag', 'a label (key = value) attached to a resource'), ('tag policy', 'a rule requiring certain tags'), ('budget alert', 'a notification when spend passes a limit'), ('inventory', 'a list of everything that exists')],
    diff=table(['', 'VM sprawl', 'Shadow IT', 'Configuration drift'], [['What', 'too many forgotten VMs', 'IT bought without approval', 'servers slowly differing'], ['Cause', 'easy creation, no clean-up', 'slow official process', 'manual changes'], ['Fix', 'tags, expiry, inventory', 'fast official self-service', 'images + IaC']], minw=540),
    where=['Development and test accounts', 'VDI pools', 'Large VMware estates', 'Lab and training environments'],
    realworld='Cloud cost and security reports from providers and analysts consistently list idle or unused resources and unpatched forgotten instances among the top causes of wasted spend and exposure; AWS Trusted Advisor and Compute Optimizer exist partly to find them.',
    pro='Use a Service Control Policy or tag policy that denies <code>ec2:RunInstances</code> unless an <code>owner</code> and <code>expiry</code> tag are present — prevention at creation is far cheaper than detection later.')

def a_lat(k):
    o = t(180, 12, ['Flat network: every VM reaches every VM', 'Attacker hops from web to database', 'Segmentation: only allowed paths'][k], 9, 'ink', bold=True)
    vms = [('web', 30, 40), ('app', 150, 40), ('db', 270, 40), ('hr', 90, 100), ('backup', 210, 100)]
    for n, x, y in vms:
        tn = 'red' if (k == 1 and n in ('web', 'db', 'hr')) else 'blue'
        o += box(x, y, 64, 30, tn, rx=4) + t(x + 32, y + 19, n, 7.6, 'ink', bold=True)
    if k < 2:
        for a in range(5):
            for b in range(a + 1, 5):
                o += f'<path d="M{vms[a][1] + 32},{vms[a][2] + 15} L{vms[b][1] + 32},{vms[b][2] + 15}" style="stroke:#bbb;stroke-width:0.8"/>'
    if k == 1:
        o += packet(62, 55, 302, 55, 'hop') + packet(62, 70, 122, 100, '')
    if k == 2:
        o += f'<path d="M94,55 L150,55" style="stroke:#2E8B57;stroke-width:2"/><path d="M214,55 L270,55" style="stroke:#2E8B57;stroke-width:2"/>' + t(180, 150, 'web → app → db only; hr and backup isolated', 7.4, 'green', bold=True)
    return o
A_LAT = cap([a_lat(k) for k in range(3)], [('Flat network', 'All VMs sit on one network and can reach each other on any port.', 'Convenient — and dangerous.'), ('Lateral movement', 'An attacker who compromises the web VM scans and hops directly', 'to the database and HR VMs.'), ('Segmentation', 'Security groups / micro-segmentation allow only web → app → db on', 'specific ports; everything else is blocked, so one breach stays small.')],
    'Lateral movement in action', 'Why one hacked VM should not mean all VMs.', 'Lateral movement', 'Animation: five VMs on a flat network all connected; attacker hops from web to db and hr; segmentation allows only web to app to db.', 'h6anim')
T6 = vtype(6, 'Lateral movement between VMs', 'amber',
    '<b>Lateral movement</b> is the technique attackers use after compromising one machine to move to other machines in the same environment — exploiting flat virtual networks, shared credentials and open ports — and it is contained by network segmentation and least-privilege access.',
    'A burglar who enters through one unlocked flat and then walks freely through internal doors into every other flat, because nobody locked them.',
    'TiffinGo’s web VM gets compromised through a vulnerable plugin. Because the database security group accepts traffic only from the app tier on port 5432, and HR is in another VPC, the attacker cannot reach either.',
    'Defences: security groups and NACLs, VPC/subnet separation, VMware NSX / Illumio micro-segmentation, Azure NSGs, GCP firewall rules, zero-trust access, no shared admin passwords.',
    '', A_LAT,
    'always: design “default deny” between tiers and allow only required ports.',
    'all VMs sit in one subnet with an “allow all inside” rule, or the same admin password is reused on every VM.',
    plain='After breaking into one computer, attackers try to jump to the others nearby. If every computer can talk freely to every other, one break-in becomes a disaster.',
    how=[('Initial compromise', 'One VM is hacked.'), ('Discover', 'The attacker scans the internal network for reachable hosts and ports.'), ('Harvest credentials', 'Passwords, SSH keys or cloud credentials found on the first VM.'), ('Move', 'Log in to or exploit the next VM; repeat.'), ('Defend', 'Segment networks (default deny), unique credentials, IAM roles instead of keys, monitoring of east-west traffic.')],
    words=[('east-west traffic', 'traffic between servers inside the data centre'), ('segmentation', 'splitting a network into zones with rules between them'), ('micro-segmentation', 'rules down to individual VMs or workloads'), ('zero trust', 'never trust a connection just because it is internal')],
    diff=table(['', 'Lateral movement', 'VM escape'], [['Path', 'over the network between VMs', 'through the hypervisor'], ['Needs a hypervisor bug?', 'no', 'yes'], ['Main defence', 'segmentation, credentials hygiene', 'patching, sandboxing']], minw=480),
    where=['Every multi-tier application', 'Flat on-premises VLANs', 'Cloud VPCs with permissive security groups'],
    realworld='Most large ransomware incidents involve lateral movement: attackers enter through one machine and spread across the network before encrypting; segmentation is one of the controls most frequently recommended by national cyber agencies such as CERT-In and CISA.',
    pro='Security groups can reference other security groups: allow port 5432 on the db-sg <i>only from</i> app-sg, not from an IP range. New app instances are allowed automatically, nothing else ever is.')

SUMMARY = table(['#', 'Threat', 'Breaks / abuses', 'Key defence', 'In public cloud, who defends?'], [
    ['1', 'VM escape', 'hypervisor/device bug', 'patch, sandbox, fewer devices', 'provider (hypervisor); you (guest patching)'], ['2', 'Side-channel', 'shared CPU', 'microcode, core isolation, dedicated', 'provider; you choose dedicated/confidential'],
    ['3', 'Hyperjacking', 'boot chain / hypervisor', 'secure + measured boot, signed code', 'provider'], ['4', 'Management plane', 'admin console, keys', 'MFA, least privilege, no exposure', 'you (IAM)'],
    ['5', 'VM sprawl', 'operations', 'tags, budgets, clean-up', 'you'], ['6', 'Lateral movement', 'flat networks, shared creds', 'segmentation, roles', 'you (security groups)']], minw=680)
CHECK = ('  <h3>Check yourself: which threat is it?</h3>\n' +
    qx('A. Thousands of ESXi servers exposed to the internet are encrypted through an old OpenSLP bug.', ['Side-channel', 'Management-plane attack', 'VM sprawl', 'Hyperjacking'], 1, 'ESXiArgs (2023) attacked the hypervisor’s management service.') +
    qx('B. A guest exploits a bug in an emulated floppy controller to run code on the host.', ['VM escape', 'Lateral movement', 'VM sprawl', 'Side-channel'], 0, 'VENOM (2015).') +
    qx('C. An audit finds 40 unowned, unpatched test VMs still running.', ['VM sprawl', 'Hyperjacking', 'Side-channel', 'VM escape'], 0, 'Easy creation without clean-up.') +
    qx('D. Cache-timing measurements leak a key from a neighbouring VM.', ['Side-channel', 'Management-plane attack', 'Lateral movement', 'P2V'], 0, 'No software bug — shared hardware.') +
    qx('E. After hacking the web VM, the attacker reaches the HR database directly.', ['Lateral movement', 'Hyperjacking', 'VM sprawl', 'Cold migration'], 0, 'Fix with segmentation and default-deny rules.'))

def build(ESC, SCA):
    intro = ('  <p>Virtualization’s benefits come with a new set of risks. Each threat below follows the 4.1 pattern — definition, plain words, analogy, how it works step by step, picture/animation, differences, where it shows up, a real incident, the TiffinGo scenario and an expert note — and always ends with the defence.</p>\n'
             + challenge(['Why does a missing floppy drive make a hypervisor safer?', 'How can an IAM policy be as dangerous as an exposed vCenter?', 'How do you stop VM sprawl at creation time rather than finding it later?'], 'types 1, 4 and 5') + MAP
             + jump(['VM escape', 'Side-channel', 'Hyperjacking', 'Management plane', 'VM sprawl', 'Lateral movement']))
    return intro + T1(ESC) + T2(SCA) + T3 + T4 + T5 + T6 + '\n  <h3 style="margin-top:34px">All six side by side</h3>\n' + SUMMARY + '\n' + CHECK
