import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
sys.path.insert(0, HERE)
from _types import TYPES_SEC
from _prac import PRAC
C = 'l41.txt'
def sec(a, b=None):
    return capsec(C, a, b)

hk = hook('How can one physical computer pretend to be five different computers at the same time — each with its own Windows or Linux?',
    'With <b>virtualization</b>. A thin layer of software called a <b>hypervisor</b> sits between the hardware and the operating systems, hands each one a slice of CPU, memory, disk and network, and keeps them completely apart. Every cloud VM you will ever use — EC2, Azure VMs, Compute Engine — runs on a hypervisor. Our own lab machine reports <b>Hypervisor vendor: KVM</b>: it is itself a VM.',
    ['What virtualization and a hypervisor are, why they were invented, and where they are used.', 'Type 1 vs Type 2 hypervisors, and how a hypervisor actually runs a VM (CPU, memory, I/O).', 'Full virtualization, paravirtualization and hardware-assisted virtualization.'])

def before_after():
    o = t(180, 12, 'Server room → one server with a hypervisor', 8.8, 'ink', bold=True)
    for i, n in enumerate(['Mail', 'Web', 'Accounts', 'HR', 'Backup']):
        o += box(8 + i * 34, 24, 30, 54, 'red', rx=3) + t(23 + i * 34, 44, n[:4], 6.4, 'ink', bold=True) + t(23 + i * 34, 60, ['8%', '15%', '5%', '3%', '10%'][i], 6.6, 'red', bold=True)
    o += t(92, 94, '5 servers, mostly idle', 7.4, 'red', bold=True) + arrow(180, 52, 204, 52, 'acc', 2.4)
    o += box(208, 20, 146, 112, 'card', rx=6)
    for i in range(5):
        o += box(214 + i * 27, 26, 24, 40, 'blue', rx=3) + t(226 + i * 27, 50, 'VM', 6.4, 'ink', bold=True)
    o += box(214, 72, 134, 18, 'amber', rx=3) + t(281, 84, 'hypervisor', 7.4, 'ink', bold=True) + box(214, 94, 134, 30, 'green', rx=3) + t(281, 113, '1 server · 41% busy', 7.4, 'ink', bold=True)
    return o
scene_svg = scene('Left: five physical servers, each running one application at 3 to 15 percent CPU. Right: one physical server with a hypervisor running the same five applications as virtual machines, 41 percent busy.', before_after(), 'Same five apps, <tspan font-weight="700" class="s-acc">four fewer servers</tspan>.')
dialogue = '''K> Sir, our old server room has five servers — mail, website, accounts, HR, backup — and each is busy only 3 to 15% of the time.
A> That is the exact problem virtualization was invented for. Put a hypervisor on one strong server and run all five as virtual machines.
R> But mail runs on Windows and the website on Linux. Can they share one machine?
A> Yes. Each VM gets its own operating system and believes it owns the hardware. The hypervisor is the referee. Let’s see how it does that trick.'''

# ---------- big picture
def stacks():
    o = t(320, 16, 'Without and with virtualization', 11, 'ink', bold=True)
    # without
    x = 30
    o += t(x + 120, 38, 'Traditional: one OS per server', 9, 'ink', bold=True)
    o += box(x, 50, 240, 36, 'blue', rx=6) + t(x + 120, 72, 'Applications', 9, 'ink', bold=True)
    o += box(x, 92, 240, 36, 'green', rx=6) + t(x + 120, 114, 'Operating system (talks to hardware directly)', 8.4, 'ink', bold=True)
    o += box(x, 134, 240, 36, 'card', rx=6) + t(x + 120, 156, 'Hardware: CPU · RAM · disk · network', 8.4, 'ink', bold=True)
    o += t(x + 120, 190, '1 server = 1 OS = usually 1 app', 8, 'red', bold=True)
    # with
    x = 340
    o += t(x + 135, 38, 'Virtualized: many OSes on one server', 9, 'ink', bold=True)
    for i, (os_, app, tn) in enumerate([('Windows', 'Mail', 'blue'), ('Linux', 'Website', 'green'), ('Linux', 'Accounts', 'violet')]):
        xx = x + i * 92
        o += box(xx, 50, 86, 30, tn, rx=5) + t(xx + 43, 69, app, 8.2, 'ink', bold=True)
        o += box(xx, 82, 86, 26, tn, rx=5) + t(xx + 43, 99, os_ + ' (guest)', 7.6, 'ink')
        o += t(xx + 43, 120, f'VM {i + 1}', 7.6, 'ink2', bold=True)
    o += box(x, 128, 270, 26, 'amber', rx=5) + t(x + 135, 145, 'Hypervisor (virtual machine monitor)', 8.6, 'ink', bold=True)
    o += box(x, 158, 270, 26, 'card', rx=5) + t(x + 135, 175, 'Hardware (the host)', 8.4, 'ink', bold=True)
    o += t(x + 135, 202, '1 server = many isolated VMs', 8, 'green', bold=True)
    return o
STACKS = bigfig('Left stack: applications, operating system, hardware — one OS per server. Right stack: three virtual machines each with its own guest OS and app, on top of a hypervisor, on top of the hardware host.', stacks(), h=220)
def types():
    o = t(320, 16, 'Type 1 (bare-metal) vs Type 2 (hosted) hypervisor', 11, 'ink', bold=True)
    for c, (name, layers_, ex, use) in enumerate([
        ('Type 1 · bare-metal', [('VM', 'VM', 'VM'), 'Hypervisor', 'Hardware'], 'VMware ESXi · Microsoft Hyper-V · Xen · KVM · AWS Nitro', 'data centres and every public cloud'),
        ('Type 2 · hosted', [('VM', 'VM', ''), 'Hypervisor app (VirtualBox)', 'Host OS (Windows / macOS / Linux)', 'Hardware'], 'Oracle VirtualBox · VMware Workstation · Parallels', 'laptops: learning, testing, demos')]):
        x = 30 + c * 310
        o += t(x + 135, 38, name, 9.4, 'ink', bold=True)
        y = 48
        vms = layers_[0]
        for i, v in enumerate(vms):
            if v: o += box(x + i * 92, y, 86, 30, 'blue', rx=5) + t(x + 43 + i * 92, y + 19, 'VM (guest OS)', 7.6, 'ink', bold=True)
        y += 36
        for lab in layers_[1:]:
            tn = 'amber' if 'ypervisor' in lab else ('violet' if 'Host OS' in lab else 'card')
            o += box(x, y, 270, 30, tn, rx=5) + t(x + 135, y + 19, lab, 8.2, 'ink', bold=True); y += 36
        o += t(x + 135, 212, ex, 7.6, 'ink2') + t(x + 135, 228, 'Used in: ' + use, 7.8, 'green', bold=True)
    o += t(320, 252, 'Type 1 runs directly on the hardware: faster, more secure. Type 2 is an app on your normal OS: easy to install.', 8, 'ink2')
    return o
TYPES = bigfig('Type 1 hypervisor: VMs on a hypervisor directly on hardware; examples ESXi, Hyper-V, Xen, KVM, Nitro; used in data centres and clouds. Type 2: VMs on a hypervisor application running on a host operating system on hardware; examples VirtualBox, VMware Workstation, Parallels; used on laptops.', types(), h=262)
picture = ('  <p><b>Virtualization</b> means creating a <i>virtual</i> (software) version of something physical — a computer, a disk, a network. The most important kind is <b>server virtualization</b>: one physical machine running many virtual machines. Compare the two stacks:</p>\n' + STACKS +
    '\n  <p>The new layer in the middle is the <b>hypervisor</b>. There are two kinds, and you will meet both — one on your laptop, the other in every cloud:</p>\n' + TYPES)

# ---------- animation 1: how a hypervisor runs a VM
HN = {'app': (6, 4, 66, 44, 'app', 'App in VM', 'web server'), 'gos': (6, 56, 66, 44, 'gear', 'Guest OS', 'Linux kernel'), 'vcpu': (90, 4, 70, 44, 'chip', 'vCPU', 'virtual CPU'),
      'hv': (90, 56, 70, 44, 'shield', 'Hypervisor', 'KVM'), 'core': (178, 4, 80, 44, 'chip', 'Physical core', 'Xeon'), 'ram': (178, 56, 80, 44, 'disk', 'Host RAM', 'real memory'),
      'vdisk': (276, 4, 78, 44, 'disk', 'Virtual disk', 'web1.qcow2'), 'nic': (276, 56, 78, 44, 'globe', 'Virtual NIC', 'virtio-net')}
HS = [dict(on=['app', 'gos'], hot='gos', head='Step 1 · The guest OS boots inside the VM', text='Linux starts as if on a real computer: it sees 2 CPUs, 1 GiB RAM, a disk,', text2='a network card. All of these are virtual — created by the hypervisor.', svc='Guest = the VM’s OS · Host = the physical machine'),
      dict(on=['app', 'gos', 'vcpu', 'core', 'hv'], hot='core', move=(160, 26, 180, 26, 'time slice'), head='Step 2 · vCPU → time on a real core', text='The hypervisor schedules each vCPU onto a physical core for a few', text2='milliseconds at a time, like the OS schedules processes.', svc='More vCPUs than cores = CPU overcommit (fine if VMs are idle)'),
      dict(on=['app', 'gos', 'hv', 'ram'], hot='ram', move=(160, 78, 180, 78, 'map'), head='Step 3 · Guest memory → host memory', text='The guest thinks its RAM starts at address 0. The hypervisor (with CPU', text2='help: Intel EPT / AMD NPT) maps it to real RAM no other VM can touch.', svc='Isolation: VM A can never read VM B’s memory'),
      dict(on=['app', 'gos', 'hv', 'vcpu'], hot='hv', move=(39, 56, 92, 78, 'trap'), head='Step 4 · Privileged instruction → trap', text='When the guest kernel tries something only hardware may do (change', text2='page tables, halt the CPU), the CPU exits to the hypervisor, which does it safely.', svc='Called a VM exit / VM entry (hardware-assisted virtualization)'),
      dict(on=['app', 'gos', 'hv', 'vdisk'], hot='vdisk', move=(160, 70, 278, 26, 'write'), head='Step 5 · Disk write → a file on the host', text='The app saves an order; the guest writes to its “disk”; the hypervisor', text2='turns that into a write to web1.qcow2 on the host (or a network disk).', svc='virtio-blk / virtio-scsi drivers make this fast'),
      dict(on=list(HN), hot='nic', move=(160, 86, 278, 78, 'packet'), head='Step 6 · Network packet → virtual switch', text='Packets from the virtual NIC go to a virtual switch/bridge on the host', text2='and out of the real network card, with the VM’s own IP and MAC.', svc='In AWS this is done in hardware by the Nitro Card for VPC')]
HOW = flow_anim('How a hypervisor runs a virtual machine', 'Six things the hypervisor does every second for every VM: boot, CPU, memory, privileged instructions, disk and network.', 'Inside a hypervisor', 'Animation: guest OS boots; vCPU scheduled on a physical core; guest memory mapped to host RAM; privileged instruction trapped by the hypervisor; disk write becomes a qcow2 file write; network packet goes to a virtual switch.', HN, HS, hid='hv')

# ---------- animation 2: three techniques with CPU rings
def ring_frame(k):
    o = t(180, 12, ['The problem: only ring 0 may control hardware', 'Full virtualization (binary translation)', 'Paravirtualization (hypercalls)', 'Hardware-assisted (Intel VT-x / AMD-V)'][k], 8.8, 'ink', bold=True)
    rings = [(80, 'ring 3: apps'), (60, 'ring 1–2'), (40, 'ring 0: kernel')]
    cx, cy = 90, 92
    for r, lab in rings:
        o += f'<circle cx="{cx}" cy="{cy}" r="{r}" style="fill:none;stroke:var(--line);stroke-width:1.4"/>'
    o += f'<circle cx="{cx}" cy="{cy}" r="20" class="s-soft-acc" style="stroke:var(--track)"/>' + t(cx, cy + 3, 'HW', 7.4, 'ink', bold=True)
    o += t(cx, cy - 66, 'ring 3 apps', 6.6, 'ink2') + t(cx, cy - 46, 'ring 1', 6.6, 'ink2') + t(cx, cy - 27, 'ring 0', 6.6, 'ink2')
    notes = [['Guest kernels expect ring 0.', 'The hypervisor needs ring 0 too.', 'Two bosses, one ring: x86 was', 'not designed for this (before 2005).'],
             ['Guest kernel moved to ring 1.', 'Hypervisor scans its code and', 'rewrites dangerous instructions', 'on the fly. Works, but slow-ish.', 'VMware (1999).'],
             ['Guest OS is modified to call the', 'hypervisor directly (hypercall)', 'instead of touching hardware.', 'Fast, but needs a changed kernel.', 'Xen (2003), virtio drivers.'],
             ['CPU adds “root mode” for the', 'hypervisor and “non-root mode”', 'for guests, each with rings 0–3.', 'Unmodified guests, near full speed.', 'KVM, Hyper-V, ESXi, Nitro today.']][k]
    for i, n in enumerate(notes):
        o += t(186, 40 + i * 16, n, 7.8, 'ink' if i else 'ink', anchor='start', bold=(i == 0))
    if k == 3:
        o += box(176, 124, 172, 22, 'green', rx=6) + t(262, 139, 'VM exit ⇄ VM entry', 8, 'ink', bold=True)
    return o
RS = [('Why x86 was hard to virtualize', 'Operating systems run their kernel in ring 0, the most privileged CPU mode.', 'A hypervisor must stay above every guest kernel'),
      ('Technique 1: full virtualization', 'Unmodified guest; the hypervisor translates privileged instructions in software.', 'Any OS works; CPU cost for translation'),
      ('Technique 2: paravirtualization', 'The guest kernel is changed to ask the hypervisor nicely (hypercalls).', 'Fast; today mainly used for disk and network drivers (virtio)'),
      ('Technique 3: hardware-assisted', 'Intel VT-x (2005) and AMD-V (2006) add a hypervisor mode in the CPU.', 'This is how all clouds work today; your CPU must have it enabled')]
RINGS = anim_one('How it works', 'Three ways to virtualize a CPU', 'Why “VT-x enabled in BIOS” matters — the CPU rings story in four frames.', 'Virtualization techniques', 'Animation of x86 CPU protection rings and three techniques: binary translation, paravirtualization and hardware-assisted virtualization with root and non-root modes.', cap_frames([ring_frame(k) for k in range(4)], RS), [x[0] + '.' for x in RS], delay=6500, hid='rings')

# ---------- parts
parts = wwu([
    ('Virtualization', 'Creating software versions of hardware (computer, disk, network) so one physical resource can serve many users.', 'Servers were expensive and 85–95% idle; IT was slow to provision.', 'Every data centre and cloud; your laptop for test VMs.'),
    ('Hypervisor (VMM)', 'The software layer that creates, runs and isolates VMs and shares the hardware among them.', 'Someone must be the referee between many operating systems on one machine.', 'KVM (AWS, Google), Hyper-V (Azure), ESXi (companies), VirtualBox (laptops).'),
    ('Host and guest', 'Host = the physical machine (and its OS for Type 2). Guest = the OS running inside a VM.', 'Two words to say “which side” of the hypervisor something runs on.', 'Logs, drivers, commands: “run this on the host, not in the guest”.'),
    ('vCPU', 'A virtual CPU given to a VM; it is scheduled onto a hardware thread of a real core.', 'Lets you size VMs independently of physical CPUs.', 'EC2 t3.micro = 2 vCPUs; overcommit in private clouds.'),
    ('Virtual memory mapping (EPT / NPT)', 'CPU feature that translates guest memory addresses to real host memory in hardware.', 'Software translation was slow and complex.', 'Every modern hypervisor; keeps VMs’ memory separate.'),
    ('Virtual disk', 'A file (qcow2, vmdk, vhdx, raw) or network volume that the guest sees as a disk.', 'Disks become portable files you can copy, snapshot and move.', 'VirtualBox .vdi, VMware .vmdk, Hyper-V .vhdx, KVM .qcow2, AWS EBS.'),
    ('Virtual NIC and switch', 'A software network card in the VM plugged into a software switch on the host.', 'Many VMs must share a few physical network ports safely.', 'Linux bridge, Open vSwitch, Hyper-V switch, AWS Nitro VPC card.'),
    ('VT-x / AMD-V', 'CPU extensions that add a special mode for hypervisors.', 'Make unmodified guests run at near-native speed and safely.', 'Must be “Enabled” in BIOS/UEFI for VirtualBox, Hyper-V, WSL2, KVM.')])
HVTABLE = table(['Hypervisor', 'Type', 'Made by', 'Where you meet it'], [
    ['KVM (+ QEMU)', 'Type 1 (Linux kernel module)', 'open source (Linux)', 'Google Cloud, AWS Nitro is KVM-based, OpenStack, Proxmox'],
    ['Xen', 'Type 1', 'open source (Linux Foundation)', 'older AWS instances, Citrix'],
    ['VMware ESXi', 'Type 1', 'Broadcom (VMware)', 'company data centres, private clouds'],
    ['Microsoft Hyper-V', 'Type 1', 'Microsoft', 'Azure, Windows Server, WSL2 underneath'],
    ['AWS Nitro Hypervisor', 'Type 1 (KVM-based)', 'Amazon', 'all current EC2 instances'],
    ['Oracle VirtualBox', 'Type 2', 'Oracle (free)', 'student laptops'],
    ['VMware Workstation / Fusion', 'Type 2', 'Broadcom (VMware)', 'developer laptops'],
    ['Parallels Desktop', 'Type 2', 'Parallels', 'Windows on Macs']], minw=620)
parts += '\n  <h3>Hypervisors you will meet</h3>\n' + HVTABLE

DEEP = ('  <h3>Overcommit: selling more than you have</h3>\n  <p>Because most VMs are idle most of the time, a hypervisor can give out more vCPUs (and sometimes memory) than physically exist — for example 64 vCPUs on a 32-thread server. It works until many VMs get busy together; then they wait for CPU (“steal time”, visible as <code>st</code> in <code>top</code>). Public clouds sell fixed sizes and avoid heavy overcommit; private clouds tune it carefully.</p>\n'
    '  <h3>Nested virtualization</h3>\n  <p>Running a hypervisor inside a VM (our lab machine is a VM; Docker inside it would be a third layer). Useful for labs and testing; usually slower. Some cloud instance types allow it, and bare-metal instances (<code>*.metal</code>) give direct hardware access instead.</p>\n'
    '  <h3>Popek and Goldberg (1974): when can a CPU be virtualized?</h3>\n  <p>A classic result: a CPU is easy to virtualize if every “sensitive” instruction (one that touches hardware state) traps when run in user mode. Old x86 broke this rule for 17 instructions — the reason for binary translation and paravirtualization until VT-x/AMD-V fixed it. A favourite viva question.</p>\n'
    '  <h3>Timeline</h3>\n' + table(['Year', 'Milestone'], [['1960s–70s', 'IBM CP/CMS and VM/370 virtualize mainframes'], ['1998–1999', 'VMware founded; VMware Workstation virtualizes x86 with binary translation'], ['2003', 'Xen: open-source paravirtualization'], ['2005–2006', 'Intel VT-x and AMD-V in CPUs'], ['2007', 'KVM merged into the Linux kernel'], ['2008', 'Microsoft Hyper-V; EPT/NPT memory virtualization in CPUs'], ['2017', 'AWS Nitro hypervisor (KVM-based)']], minw=480))

clouds = vendor_tabs('<p><b>AWS:</b> current EC2 instances run on the <b>Nitro Hypervisor</b> (KVM-based); older generations used Xen. Bare-metal instances (<code>*.metal</code>) give you the server without a hypervisor.</p>',
    '<p><b>Azure:</b> runs a customised <b>Hyper-V</b>. Windows 11 with WSL2 or Hyper-V uses the same hypervisor on your laptop.</p>',
    '<p><b>Google Cloud:</b> Compute Engine uses a hardened <b>KVM</b>. Nested virtualization can be enabled on some VMs.</p>') + \
    cloud3([['Hypervisor', 'Nitro (KVM-based)', 'Hyper-V', 'KVM'], ['No-hypervisor option', '*.metal instances', 'Dedicated Host (still Hyper-V)', 'Bare Metal Solution / sole-tenant'], ['Disk format to import VMs', 'VMDK, VHD, raw, OVA (VM Import)', 'VHD (fixed)', 'VMDK, VHD, raw (image import)']])
proof = [
    ('Step 1 · Does the CPU have VT-x/AMD-V? Are we inside a VM?', code('bash', 'terminal', "grep -c -E -w 'vmx|svm' /proc/cpuinfo\ngrep -c -w hypervisor /proc/cpuinfo\nlscpu | grep -E 'Hypervisor vendor|Virtualization type'", sec('== 1)', '== 2)')), 'Our lab machine is a KVM virtual machine (hypervisor flag present). It shows 0 vmx/svm because the cloud does not pass VT-x into this VM — so we cannot run another fast VM inside it. On your laptop you will usually see a number > 0.'),
    ('Step 2 · A virtual disk is just a file', code('bash', 'terminal', 'qemu-img create -f qcow2 web1.qcow2 10G', sec('== 2)', '== 3)')), 'This is the hard disk of a future VM.'),
    ('Step 3 · Thin provisioning', code('bash', 'terminal', "qemu-img info web1.qcow2\nls -lh web1.qcow2", sec('== 3)')), 'The guest will see 10 GiB, but the file uses only 196 KiB until data is written. This is how clouds and private clouds “give” big disks cheaply.')]
prac = practical('Make your own first VM on your laptop. Two paths: VirtualBox (Windows/macOS/Linux) or KVM (Linux). These steps are from the official tools; the exact screens and versions on your computer may differ.', [
    ('1 · Check virtualization is enabled', '<p><b>Windows:</b> Task Manager → Performance → CPU → “Virtualization: Enabled”. <b>Linux:</b> <code>grep -c -E -w "vmx|svm" /proc/cpuinfo</code> should be &gt; 0. If disabled, turn on Intel VT-x / AMD SVM in BIOS/UEFI.</p>', 'Without it, VirtualBox offers only 32-bit guests or refuses to start a VM.'),
    ('2a · VirtualBox: create the VM', '<p>Install VirtualBox → New → Name <code>tiffingo-lab</code>, ISO = Ubuntu Server 24.04 → 2 CPUs, 2048 MB RAM, 20 GB disk (dynamically allocated) → Finish → Start, and install Ubuntu.</p>', '“Dynamically allocated” = thin provisioning, like the qcow2 above.'),
    ('2b · KVM on Linux: create the VM', code('bash', 'terminal', 'sudo apt install -y qemu-kvm libvirt-daemon-system virtinst\nsudo usermod -aG libvirt $USER    # log out and in\nvirt-install --name tiffingo-lab --memory 2048 --vcpus 2 \\\n  --disk size=20 --cdrom ubuntu-24.04-live-server-amd64.iso --os-variant ubuntu24.04\nvirsh list --all'), 'virt-install talks to libvirt, which drives QEMU + KVM.'),
    ('3 · Look from inside the guest', code('bash', 'terminal', "lscpu | grep -E 'Hypervisor vendor|Virtualization type'\nsystemd-detect-virt"), 'Inside VirtualBox you will see “Oracle” / oracle; inside KVM “KVM” / kvm — the guest knows it is virtual.'),
    ('4 · Take a snapshot', '<p>VirtualBox: Machine → Take Snapshot “fresh-install”. KVM: <code>virsh snapshot-create-as tiffingo-lab fresh-install</code>.</p>', 'Break things freely, then roll back in seconds.')],
    cleanup='Delete the VM (VirtualBox: Remove → Delete all files; KVM: <code>virsh destroy</code> + <code>virsh undefine --remove-all-storage</code>) when you need the disk space back.')
mist = mistakes([
    ['VirtualBox shows only 32-bit options / “VT-x is not available”.', 'Virtualization is disabled in BIOS, or Hyper-V/WSL2 is holding VT-x on Windows.', 'Enable VT-x/SVM in BIOS; on Windows turn on “Windows Hypervisor Platform” or use VirtualBox 7+ which can run alongside Hyper-V.'],
    ['VM is very slow.', 'No hardware acceleration, too little RAM, or emulated (not virtio) disk/network.', 'Enable VT-x, give enough RAM, install guest additions / virtio drivers.'],
    ['Host freezes when VMs start.', 'Gave VMs more RAM than the host has.', 'Leave at least 25–30% of RAM for the host; overcommit carefully.'],
    ['Confusing host and guest.', 'Commands typed in the wrong window.', 'Check the prompt/hostname; name VMs clearly.'],
    ['“Virtualization = cloud.”', 'Both use VMs.', 'Cloud adds self-service, metering and broad network access on top (Lesson 1.2).']])
cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA Sessions 3–4', 'Introduction to virtualization, types and uses, hypervisor.'], ['AZ-900', 'Virtual machines as IaaS; Hyper-V basis of Azure (background).'], ['AWS CLF-C02', 'EC2 runs on virtualization; Nitro; bare-metal instances (background).']], minw=520) + '\n  <h3>Exam-style questions with explanations</h3>\n' + \
    qx('1. Which of these is a Type 2 hypervisor?', ['VMware ESXi', 'Oracle VirtualBox', 'Microsoft Hyper-V', 'Xen'], 1, 'VirtualBox installs as an application on a host OS. ESXi, Hyper-V and Xen run directly on the hardware (Type 1).') + \
    qx('2. In paravirtualization the guest operating system…', ['is unmodified', 'is modified to call the hypervisor through hypercalls', 'runs without a hypervisor', 'must be Windows'], 1, 'The guest kernel knows it is virtual and asks the hypervisor directly — faster, but needs a changed or enlightened OS.') + \
    qx('3. Intel VT-x and AMD-V provide…', ['GPU acceleration', 'hardware support for running hypervisors and unmodified guests', 'disk encryption', 'faster internet'], 1, 'They add a root/non-root CPU mode so guests run at near-native speed while the hypervisor keeps control.') + \
    qx('4. Which component isolates the memory of two VMs on the same host?', ['The guest OS', 'The hypervisor (with EPT/NPT hardware support)', 'The application', 'DNS'], 1, 'The hypervisor maps each guest’s memory to separate real memory; the CPU’s second-level page tables enforce it.') + \
    qx('5. AWS EC2 instances today run on…', ['VMware ESXi', 'the Nitro Hypervisor (KVM-based)', 'VirtualBox', 'no hypervisor at all'], 1, 'Nitro is a lightweight KVM-based hypervisor with I/O offloaded to Nitro cards; *.metal instances skip the hypervisor.')
proj = miniproject('Mini project: a two-VM home lab',
    'Build two VMs on your laptop (web and db), connect them on a private virtual network, and prove they can talk — the same idea as an EC2 web server and database in a VPC.',
    ['Create VM <b>web</b> and VM <b>db</b> (2 GB RAM each) with VirtualBox or KVM.', 'Attach both to an <b>internal / host-only network</b> (VirtualBox) or the default libvirt network (KVM).', 'In each guest run <code>ip -brief addr</code> and note the IPs.', 'From web: <code>ping -c 3 &lt;db-ip&gt;</code>. On db: <code>sudo apt install -y postgresql</code>; from web connect with <code>psql -h &lt;db-ip&gt;</code> (allow it in pg_hba.conf).', 'Snapshot both VMs; break something; restore the snapshot.', 'Write down which parts map to cloud: VM → EC2, virtual network → VPC, snapshot → EBS snapshot.'],
    'Two VMs talking privately, and snapshots you can roll back to.', 'Virtualization + Linux + networking + databases.')

assemble_v2(HERE, story_h2='Five servers, all half asleep', hook_html=hk,
    narration='TiffinGo bought an older company with its own server room: five servers, one application each, busy 3–15% of the time, eating electricity and AC.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='What are virtualization and a hypervisor?',
    formal='<b>Virtualization</b> is the creation of a software-based (virtual) version of a computing resource — such as a server, storage device, network or operating system — so that one physical resource can be divided into multiple isolated execution environments. A <b>hypervisor</b> (virtual machine monitor, VMM) is the software that creates and runs virtual machines, allocating CPU, memory, storage and I/O to each and isolating them from one another.',
    simple='Virtualization makes one real computer behave like several separate computers; the hypervisor is the referee that shares the hardware and keeps them apart.',
    interview=['“Virtualization creates virtual versions of hardware so one physical server can run many isolated virtual machines, each with its own OS.”', '“The hypervisor, or virtual machine monitor, allocates CPU, memory, disk and network to each VM. Type 1 runs on bare metal — ESXi, Hyper-V, Xen, KVM; Type 2 runs on a host OS — VirtualBox, VMware Workstation.”', '“Modern hypervisors use hardware-assisted virtualization, Intel VT-x or AMD-V. For example, AWS EC2 runs on the KVM-based Nitro hypervisor.”'],
    terms_rows=[('Virtual machine (VM)', 'A software computer with its own OS.'), ('Hypervisor / VMM', 'Creates, runs and isolates VMs.'), ('Host', 'The physical machine.'), ('Guest', 'The OS inside a VM.'), ('Type 1', 'Hypervisor on bare metal.'), ('Type 2', 'Hypervisor as an app on a host OS.'), ('vCPU', 'Virtual CPU scheduled on a real core.'), ('VT-x / AMD-V', 'CPU support for hypervisors.')],
    exam='Know the two hypervisor types with examples, the three techniques (full, para, hardware-assisted), and that VT-x/AMD-V must be enabled. C-DAC theory papers often ask: “Differentiate Type 1 and Type 2 hypervisors with examples.”',
    picture_h2='Before and after, and the two kinds of hypervisor', picture_html=picture,
    how_h2='Inside a hypervisor, and the three techniques', how_intro='Two animations: what the hypervisor does for one VM every second, and how CPUs became virtualizable.', how_anim=HOW + RINGS,
    parts_h2='Every term: what it is, why it exists, where it is used', parts_html=parts, lv='',
    myth_rows=[('A VM is slower than a real server by a lot.', 'With VT-x/EPT and virtio, overhead is a few percent.', 'Animation 2.'), ('Type 2 hypervisors are used in clouds.', 'Clouds use Type 1 (KVM, Hyper-V, Nitro).', 'Types picture.'), ('Our lab machine is a physical server.', 'lscpu says Hypervisor vendor: KVM.', 'Real proof step 1.')],
    extra_secs=[('deep', 'Deep dive', 'Overcommit, nesting, the theory, and the timeline', DEEP)],
    clouds_html=clouds, proof_h2='Proof on a real Linux machine', proof_intro='All outputs are real, from our cloud lab machine on 10 Nov 2026 (QEMU tools 8.x).', proof_steps=proof,
    practical_html=PRAC, mistakes_html=mist, cert_html=cert, project_html=proj,
    after_picture=[('types', 'Types of virtualization', 'Types of virtualization, one by one', TYPES_SEC)],
    can_now=['Define virtualization and hypervisor and say why they exist.', 'Name the eight types of virtualization and explain each with a definition, an analogy, a real scenario and cloud examples.', 'Compare Type 1 and Type 2 hypervisors with examples.', 'Explain how a hypervisor handles CPU, memory, privileged instructions, disk and network.', 'Explain full, para- and hardware-assisted virtualization.', 'Create a VM on your laptop and detect a hypervisor from inside Linux.'],
    next_html='<a href="../02-server-hardware-and-os-level-virtualization/">4.2 Server, hardware and OS-level virtualization</a>.',
    pre='<b>Before you start:</b> <a href="../../01-introduction/02-history-and-evolution-of-cloud-computing/">1.2</a> (the virtualization → cloud animation). Linux basics help.')
