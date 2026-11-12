"""Lesson 4.2 — types of server and hardware virtualization, one by one (TYPES standard)."""
from cloudkit import *

def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)

# ---------------------------------------------------------------- map
def mapfig():
    o = t(320, 16, 'Server and hardware virtualization: where the split is made, and how', 11, 'ink', bold=True)
    o += box(220, 28, 200, 36, 'amber', rx=18) + t(320, 50, 'Splitting one server', 9.6, 'ink', bold=True)
    cols = [('By firmware', 'violet', [('1', 'Hardware partitioning', 'LPARs on big servers')]),
            ('By a hypervisor (VMs)', 'amber', [('2', 'Full virtualization', 'guest unmodified, rewritten'), ('3', 'Paravirtualization', 'guest modified, asks'), ('4', 'Hardware-assisted', 'CPU catches it (VT-x)')]),
            ('By the OS kernel', 'green', [('5', 'OS-level', 'containers, one kernel')]),
            ('Hardware helpers', 'blue', [('6', 'I/O virtualization', 'virtio, SR-IOV'), ('7', 'GPU virtualization', 'vGPU, MIG, passthrough')])]
    for c, (h, tn, items) in enumerate(cols):
        x = 12 + c * 158
        o += f'<path d="M320,64 L{x + 74},80" style="fill:none;stroke:#999;stroke-width:1.4"/>' + box(x, 80, 148, 24, tn, rx=6) + t(x + 74, 96, h, 8.2, 'ink', bold=True)
        for i, (n, a, b) in enumerate(items):
            y = 112 + i * 48
            o += box(x, y, 148, 42, 'card', rx=6) + pin(x + 13, y + 14, n) + t(x + 26, y + 18, a, 8.2, 'ink', anchor='start', bold=True) + t(x + 8, y + 34, b, 6.9, 'ink2', anchor='start')
    o += t(320, 272, 'Types 2–4 are three answers to one question: what happens when a guest kernel runs a privileged instruction?', 7.6, 'ink2')
    return o
MAP = bigfig('Map: splitting one server by firmware (1 hardware partitioning), by a hypervisor (2 full virtualization, 3 paravirtualization, 4 hardware-assisted), by the OS kernel (5 OS-level containers), plus hardware helpers (6 I/O virtualization, 7 GPU virtualization).', mapfig(), h=284)

# ---------------------------------------------------------------- 1 LPAR
def f_lpar():
    a = box(34, 56, 156, 128, 'amber', rx=4)
    for i in range(3):
        a += box(42 + i * 50, 64, 42, 92, 'blue', rx=3) + t(63 + i * 50, 112, f'Flat {i + 1}', 7, 'ink', bold=True)
        a += f'<path d="M{88 + i * 50},62 L{88 + i * 50},158" style="stroke:#555;stroke-width:3"/>' if i < 2 else ''
    a += t(111, 172, 'brick walls + own meters', 7, 'ink', bold=True)
    r = ''
    for i, (n, osn, res) in enumerate([('LPAR 1', 'z/OS · core banking', '8 cores · 512 GB'), ('LPAR 2', 'Linux · web', '4 cores · 128 GB'), ('LPAR 3', 'test / DR', 'shared cores')]):
        x = 240 + i * 128
        r += box(x, 54, 120, 74, 'blue', rx=6) + t(x + 60, 70, n, 8, 'ink', bold=True) + t(x + 60, 86, osn, 7, 'ink') + t(x + 60, 112, res, 7, 'ink2')
    r += box(240, 136, 376, 26, 'violet', rx=5) + t(428, 153, 'Partition firmware (PR/SM on IBM Z, PowerVM on IBM Power)', 7.6, 'ink', bold=True)
    r += box(240, 168, 376, 26, 'card', rx=5) + t(428, 185, 'One very large machine: hundreds of cores · terabytes of RAM', 7.6, 'ink')
    r += box(240, 200, 180, 26, 'amber', rx=5) + t(330, 217, 'HMC: admin console', 7.4, 'ink', bold=True) + t(522, 217, 'boundaries enforced in hardware', 7.2, 'ink2')
    return apanels('Left: a bungalow divided by brick walls into three flats with separate meters. Right: one large server divided by partition firmware into LPAR 1 (z/OS core banking), LPAR 2 (Linux web) and LPAR 3 (test/DR), managed from a Hardware Management Console.',
        'Hardware partitioning: firmware cuts a big machine into fixed parts', 'walls, not curtains', a, ['Very private and predictable,', 'but moving a wall takes planning.'], 'The real thing: LPARs on one large server', r)
def a_lpar(k):
    o = t(180, 12, ['One huge machine', 'Define partitions at the console', 'Each LPAR boots its own OS'][k], 9, 'ink', bold=True)
    o += box(10, 26, 340, 108, 'card', rx=6)
    if k == 0:
        o += t(180, 70, '200 cores · 16 TB RAM · many I/O adapters', 8.4, 'ink', bold=True) + t(180, 90, 'too big for one workload', 7.6, 'ink2')
    if k >= 1:
        for i, (n, w) in enumerate([('LPAR 1', 140), ('LPAR 2', 96), ('LPAR 3', 76)]):
            x = 18 + [0, 148, 252][i]
            o += box(x, 34, w, 60 if k == 1 else 60, 'blue' if k == 2 else 'card', rx=4) + t(x + w / 2, 58, n, 8, 'ink', bold=True)
            o += t(x + w / 2, 76, ['8 cores, 512 GB', '4 cores', 'shared'][i] if k == 1 else ['z/OS', 'Linux', 'AIX'][i], 7, 'ink2' if k == 1 else 'ink', bold=k == 2)
        o += box(18, 102, 324, 24, 'violet', rx=4) + t(180, 118, 'partition firmware enforces the walls', 7.6, 'ink', bold=True)
    return o
A_LPAR = cap([a_lpar(k) for k in range(3)], [('One huge machine', 'Mainframes and big Power servers have hundreds of cores and', 'terabytes of RAM — far more than one workload needs.'), ('Define partitions', 'At the Hardware Management Console the admin assigns cores, memory', 'and I/O adapters to each logical partition (dedicated or shared).'), ('Each LPAR boots its own OS', 'Firmware enforces the boundaries; each partition runs z/OS, Linux', 'or AIX as if it were a separate machine.')],
    'Hardware partitioning in action', 'How a bank splits one mainframe.', 'LPARs', 'Animation: a huge machine; partitions defined at the console with cores and memory; each LPAR boots its own operating system on partition firmware.', 't1anim')
T1 = vtype(1, 'Hardware-level partitioning (LPAR)', 'violet',
    'Hardware partitioning divides one large physical server’s processors, memory and I/O adapters into separate <b>logical partitions (LPARs)</b>, each running its own operating system, with the boundaries enforced by the machine’s firmware rather than by a software hypervisor on top of an OS.',
    'A big bungalow divided into flats with brick walls and separate electricity meters. Very private and predictable — but moving a wall needs planning, unlike curtains you can slide.',
    'TiffinGo’s payment partner bank runs core banking, its internet-banking web tier and a test copy as three LPARs on one mainframe. A spike in test cannot slow production, because cores and memory are fenced by firmware.',
    'IBM PR/SM on IBM Z mainframes, IBM PowerVM on IBM Power servers (AIX, IBM i, Linux); in the cloud: IBM Power Virtual Server.',
    f_lpar(), A_LPAR,
    'you run a very large, mission-critical server (banking, airline reservations, telecom billing) and need strict, predictable isolation.',
    'you need hundreds of small, short-lived servers — VMs or containers are far more flexible and cheaper.',
    plain='A very big, very expensive computer is cut into a few fixed sections using controls built into the machine itself. Each section then behaves like a completely separate computer with its own operating system.',
    how=[('One large machine', 'Mainframes and big Power servers have many processors, terabytes of memory and many I/O adapters.'), ('Firmware hypervisor is built in', 'The partition manager (PR/SM on IBM Z, PowerVM on Power) is part of the machine’s firmware — it is always there, below every OS.'), ('Admin defines partitions', 'On the Hardware Management Console (HMC) the admin assigns each LPAR dedicated or shared processors, an amount of memory and I/O adapters.'), ('Boundaries enforced by hardware/firmware', 'An LPAR cannot address memory or devices outside its assignment.'), ('Each LPAR boots its own OS', 'z/OS, AIX, IBM i or Linux; I/O can be dedicated, or shared through a Virtual I/O Server (VIOS) partition.'), ('Adjust carefully', 'Dynamic LPAR lets admins move processors and memory between running partitions within limits.')],
    words=[('firmware', 'software built into the hardware'), ('LPAR', 'logical partition'), ('mainframe', 'very large, highly reliable server used by banks and airlines'), ('HMC', 'the admin console for IBM Power partitions'), ('VIOS', 'a special partition that shares disks and network cards among other LPARs')],
    diff=table(['', 'Hardware partition (LPAR)', 'Hypervisor VM', 'Container'], [['Split made by', 'machine firmware', 'hypervisor software', 'OS kernel'], ['Granularity', 'few, large partitions', 'many VMs', 'hundreds of containers'], ['Change speed', 'planned', 'seconds–minutes', 'milliseconds'], ['Isolation', 'strongest', 'strong', 'good'], ['Typical hardware', 'IBM Z, IBM Power', 'any x86/ARM server', 'any Linux host']], minw=560),
    where=['Core banking and payments', 'Airline and railway reservation systems', 'Telecom billing', 'Insurance and government record systems'],
    realworld='IBM Z mainframes run every workload inside LPARs; a single recent IBM Z system supports up to 85 LPARs, and banks typically place production, test and disaster-recovery systems in separate partitions of the same machine.',
    pro='On IBM Z the hypervisor z/VM itself runs inside an LPAR, so Linux guests there are virtualized twice — by design. IBM’s CP-67 and VM/370 (1960s–70s) are where the term “virtual machine” comes from.')

# ---------------------------------------------------------------- techniques 2-4 shared visuals
def tech_frame(kind, k):
    o = t(180, 12, {'full': ['Guest kernel thinks it is in charge', 'Hypervisor scans the code', 'Sensitive instruction is rewritten'], 'para': ['Guest kernel is modified', 'It makes a hypercall', 'Split drivers share memory rings'], 'hw': ['Hypervisor enters VMX root mode', 'Guest runs in non-root ring 0', 'Sensitive event → VM exit → VM entry']}[kind][k], 9, 'ink', bold=True)
    o += box(10, 26, 160, 50, 'blue', rx=6) + t(90, 44, 'Guest kernel', 8.2, 'ink', bold=True)
    o += box(10, 92, 340, 30, 'amber', rx=6) + t(180, 112, 'Hypervisor', 8.4, 'ink', bold=True)
    o += box(10, 128, 340, 18, 'card', rx=4) + t(180, 141, 'CPU + hardware', 7.4, 'ink')
    if kind == 'full':
        o += t(90, 62, ['“I am in ring 0”', 'actually ring 1', 'POPF → call to hypervisor'][k], 7.2, 'ink2')
        if k >= 1:
            o += box(196, 26, 154, 50, 'green' if k == 2 else 'card', rx=6) + t(273, 44, 'binary translator', 7.8, 'ink', bold=True) + t(273, 60, ['', 'reads each code block', 'rewritten block cached'][k], 7, 'ink2')
            o += packet(170, 50, 196, 50, 'scan' if k == 1 else '')
        if k == 2:
            o += packet(273, 76, 273, 92, '')
    if kind == 'para':
        o += t(90, 62, ['source changed: “I know I am a VM”', 'hypercall: “update my page table”', 'frontend driver'][k], 6.8, 'ink2')
        if k == 1:
            o += packet(90, 76, 90, 92, 'hypercall')
        if k == 2:
            o += box(196, 26, 154, 50, 'green', rx=6) + t(273, 44, 'backend driver (Dom0)', 7.6, 'ink', bold=True) + t(273, 60, 'real disk / network', 7, 'ink2') + packet(170, 50, 196, 50, 'ring')
    if kind == 'hw':
        o += t(90, 62, ['', 'ring 0, non-root mode', 'touches I/O port'][k], 7.2, 'ink2')
        if k == 0:
            o += box(196, 26, 154, 50, 'green', rx=6) + t(273, 44, 'VMXON + VMCS', 7.8, 'ink', bold=True) + t(273, 60, 'per-vCPU control block', 7, 'ink2')
        if k == 1:
            o += t(273, 50, 'normal instructions run', 7.4, 'green', bold=True) + t(273, 64, 'directly at full speed', 7.4, 'green', bold=True)
        if k == 2:
            o += packet(60, 76, 60, 92, 'exit') + packet(140, 92, 140, 76, 'entry') + t(273, 50, 'CPU itself traps —', 7.4, 'ink', bold=True) + t(273, 64, 'no code rewriting', 7.4, 'ink', bold=True)
    return o
TECH = table(['', 'Full virtualization (binary translation)', 'Paravirtualization', 'Hardware-assisted'], [
    ['Guest OS modified?', 'no', 'yes (kernel or drivers)', 'no'], ['Privileged instruction handled by', 'hypervisor rewrites code on the fly', 'guest calls hypervisor (hypercall)', 'CPU traps it automatically (VM exit)'],
    ['Speed', 'good, overhead on kernel code', 'very good for I/O', 'near-native (with EPT, virtio)'], ['Needs CPU support?', 'no', 'no', 'yes (VT-x / AMD-V)'],
    ['Classic examples', 'VMware Workstation/ESX before 2006; QEMU TCG', 'Xen PV; early EC2', 'KVM, Hyper-V, ESXi today, Nitro'], ['Today', 'emulating other CPU types', 'lives on as PV drivers (virtio, ENA)', 'the default everywhere']], minw=640)

A_FULL = cap([tech_frame('full', k) for k in range(3)], [('Guest thinks it is in charge', 'The unmodified kernel believes it runs in ring 0, but the hypervisor', 'has quietly moved it to ring 1.'), ('Scan before running', 'The binary translator reads each block of kernel code just before', 'it runs; ordinary user code runs directly.'), ('Rewrite the dangerous ones', 'Instructions that would misbehave in ring 1 (e.g. POPF) are replaced', 'with calls into the hypervisor; the result is cached for reuse.')],
    'Full virtualization in action', 'How VMware virtualized x86 before CPUs could help.', 'Binary translation', 'Animation: the guest kernel thinks it is in ring 0; the binary translator scans code blocks; sensitive instructions are rewritten into hypervisor calls and cached.', 't2anim')
T2 = vtype(2, 'Full virtualization (binary translation)', 'amber',
    'Full virtualization presents a complete simulation of the hardware so that an <b>unmodified</b> guest operating system runs exactly as on a real machine. On x86 before CPU support existed, the hypervisor achieved this by <b>binary translation</b>: rewriting the guest kernel’s sensitive instructions on the fly.',
    'A live interpreter at a meeting: the speaker talks normally and never changes a word, while the interpreter quietly rephrases the few sentences that would cause trouble.',
    'A TiffinGo developer needs to test an ARM build of the delivery app on an x86 laptop. QEMU translates the ARM instructions to x86 at run time — slow, but it works with no changes to the app or OS.',
    'Historic: VMware Workstation (1999) and ESX before hardware support; today: QEMU’s TCG translator for running other CPU architectures. Clouds no longer use binary translation for x86 guests.',
    '', A_FULL,
    'you must run an unmodified OS where hardware support is missing, or emulate a different CPU type.',
    'performance matters — on modern CPUs hardware-assisted virtualization is faster and simpler.',
    plain='The operating system inside the VM is not changed at all and does not know it is in a VM. The hypervisor quietly watches the OS’s most powerful instructions and swaps the dangerous ones for safe versions just before they run.',
    how=[('Deprivilege the guest', 'The hypervisor runs the guest kernel in ring 1 instead of ring 0, so it cannot directly control the CPU.'), ('Run user code directly', 'Applications inside the VM (ring 3) run straight on the CPU.'), ('Translate kernel code', 'Before a block of guest kernel code runs, the translator scans it.'), ('Replace sensitive instructions', 'Instructions such as POPF that silently behave differently outside ring 0 are replaced with jumps into the hypervisor.'), ('Cache the result', 'Translated blocks are cached so the cost is paid once.'), ('Emulate devices', 'Disks and network cards are emulated in software (e.g. an old Intel e1000 NIC) so the guest’s standard drivers work.')],
    words=[('ring 0 / ring 3', 'CPU privilege levels: 0 = most powerful (kernel), 3 = least (apps)'), ('binary translation', 'rewriting machine code while the program runs'), ('POPF', 'an x86 instruction that changes CPU flags'), ('emulated device', 'a fake hardware device made by software')],
    diff=TECH,
    where=['Running x86 VMs on CPUs without VT-x (before 2006)', 'Emulating ARM/RISC-V on x86 for development', 'Some security research and sandboxing tools'],
    realworld='VMware’s first product, VMware Workstation (1999), virtualized x86 with binary translation — at a time when the x86 architecture was considered “not virtualizable”. That breakthrough is what started the server-virtualization industry.',
    pro='Classic x86 had about 17 “sensitive but unprivileged” instructions that broke the Popek–Goldberg virtualization rules — they did not trap, they just behaved differently. Binary translation existed purely to catch those 17.')

A_PARA = cap([tech_frame('para', k) for k in range(3)], [('The guest kernel is modified', 'Its source code is changed so it knows it runs on a hypervisor', '(e.g. Xen PV Linux).'), ('It makes a hypercall', 'Instead of executing privileged instructions, it calls the hypervisor', 'directly — like a system call, one level down. Few traps, fast.'), ('Split drivers', 'A frontend driver in the guest and a backend driver in a driver domain', 'share memory rings to move disk and network data efficiently.')],
    'Paravirtualization in action', 'The guest cooperates with the hypervisor instead of being tricked.', 'Paravirtualization', 'Animation: modified guest kernel; hypercall to the hypervisor; frontend and backend drivers exchanging data over shared memory rings.', 't3anim')
T3 = vtype(3, 'Paravirtualization', 'amber',
    'Paravirtualization is a technique in which the guest operating system is <b>modified</b> to know that it runs on a hypervisor, replacing privileged operations with explicit calls to the hypervisor (<b>hypercalls</b>) and using paravirtual device drivers, which reduces trapping and emulation overhead.',
    'A hotel guest who phones reception for room service instead of walking into the kitchen: the guest knows the rules and asks politely, so nobody has to stop and catch him.',
    'TiffinGo’s first cloud servers in the early days of EC2 ran on Xen. Today its instances use ENA and NVMe drivers — paravirtual-style drivers that know they talk to the Nitro system rather than to a real old network card.',
    'Xen (PV guests), Hyper-V “enlightenments”, virtio drivers in KVM/QEMU, AWS ENA and NVMe drivers, VMware PVSCSI and VMXNET3.',
    '', A_PARA,
    'I/O performance matters — paravirtual drivers are standard in every modern VM even when the CPU part is hardware-assisted.',
    'you cannot modify or add drivers to the guest OS (closed, very old systems).',
    plain='The operating system inside the VM is told the truth — “you are a virtual machine” — and is changed slightly so that, instead of touching hardware, it simply asks the hypervisor to do it.',
    how=[('Modify the guest', 'The guest kernel source (or just its drivers) is changed to be hypervisor-aware.'), ('Hypercalls replace privileged instructions', 'For page-table updates, timers or interrupts the kernel calls the hypervisor directly — like a system call one level down.'), ('Batch work', 'Many updates can be sent in one hypercall, cutting the number of expensive switches.'), ('Split drivers', 'A frontend driver in the guest places requests in a shared-memory ring; a backend driver in the hypervisor or a driver domain (Xen Dom0) performs the real I/O.'), ('Notify, do not trap', 'Event channels/doorbells tell the other side there is work, instead of trapping on every register access.'), ('Hybrid today', 'Modern VMs use hardware-assisted CPU virtualization plus paravirtual drivers (called PVHVM in Xen).')],
    words=[('hypercall', 'a request from the guest kernel to the hypervisor'), ('Dom0 / driver domain', 'a privileged VM in Xen that owns the real devices'), ('shared ring', 'a circular queue in memory both sides read and write'), ('virtio', 'the standard paravirtual driver family for KVM')],
    diff=TECH,
    where=['Disk and network drivers in every modern VM (virtio, ENA, NVMe, PVSCSI)', 'Xen-based platforms', 'Windows on Hyper-V (enlightenments)'],
    realworld='Amazon EC2 launched in 2006 on the Xen hypervisor, and many early instances used paravirtual (PV) AMIs. AWS now recommends HVM AMIs on Nitro, but the paravirtual idea lives on in the ENA network and NVMe storage drivers every instance uses.',
    pro='Windows is a paravirtualized guest too: on Hyper-V it detects the hypervisor via CPUID and uses “enlightenments” — hypercalls for TLB flushes, spinlock waits and timers — which is why Windows runs noticeably better on Hyper-V-aware hypervisors.')

A_HW = cap([tech_frame('hw', k) for k in range(3)], [('Turn on VMX root mode', 'The hypervisor enables Intel VT-x (VMXON) and creates a control block', '(VMCS) for every virtual CPU.'), ('Guest runs in non-root ring 0', 'The unmodified guest kernel really runs in ring 0 — but in “non-root” mode,', 'so ordinary instructions run directly at full speed.'), ('VM exit and VM entry', 'A sensitive event (I/O, certain registers) makes the CPU itself save the guest state', 'and jump to the hypervisor (VM exit); it handles it and resumes (VM entry).')],
    'Hardware-assisted virtualization in action', 'The CPU itself catches the dangerous instructions.', 'VT-x / AMD-V', 'Animation: hypervisor enables VMX root mode and a VMCS per vCPU; the guest runs in non-root ring 0 at full speed; a sensitive event causes a VM exit to the hypervisor and a VM entry back.', 't4anim')
T4 = vtype(4, 'Hardware-assisted virtualization', 'amber',
    'Hardware-assisted virtualization uses processor extensions — <b>Intel VT-x</b> and <b>AMD-V</b> — that add a separate privilege mode for the hypervisor, so unmodified guest kernels run in their normal ring 0 while sensitive operations automatically cause a <b>VM exit</b> to the hypervisor; companion features (EPT/NPT for memory, VT-d/AMD-Vi IOMMU for devices) reduce overhead further.',
    'A building with automatic sensor doors: no guard has to watch every door. When someone tries to enter a restricted room, the door itself alerts security, who decides and lets the person continue.',
    'TiffinGo’s new developer installs VirtualBox and gets “VT-x is disabled in the BIOS”. After enabling Intel Virtualization Technology in the BIOS, the Ubuntu VM boots in seconds — the CPU is now doing the trapping that software used to do.',
    'Every modern hypervisor relies on it: KVM, Hyper-V, VMware ESXi, Xen HVM, VirtualBox, AWS Nitro Hypervisor; Apple Hypervisor.framework on Macs.',
    '', A_HW,
    'always — it is the default on all current CPUs and clouds.',
    'the BIOS setting is off, or another hypervisor (Hyper-V/WSL2) already owns VT-x on Windows — other hypervisors may then run slower or fail.',
    plain='Modern processors were given a special “manager mode” for the hypervisor. The operating system in the VM runs normally, and whenever it tries something dangerous, the processor itself pauses it and hands control to the hypervisor.',
    how=[('Enable VMX', 'The hypervisor executes VMXON (Intel) and enters VMX root mode — the new top privilege level.'), ('Create a VMCS per vCPU', 'A Virtual Machine Control Structure stores the guest’s registers, the host’s registers and which events must cause exits.'), ('Enter the guest', 'VMLAUNCH/VMRESUME switches the CPU into non-root mode; the guest kernel runs in its real ring 0.'), ('Run directly', 'Almost all guest instructions run natively at full speed.'), ('VM exit', 'On configured events (I/O ports, some registers, HLT, EPT violation) the CPU saves guest state to the VMCS and jumps to the hypervisor.'), ('Handle and resume', 'The hypervisor emulates or completes the operation and executes VMRESUME. EPT/NPT avoid exits for page-table changes; the IOMMU lets devices be given safely to VMs.')],
    words=[('VT-x / AMD-V', 'virtualization features in Intel / AMD CPUs'), ('VMX root / non-root', 'hypervisor mode / guest mode'), ('VMCS', 'a memory block holding one virtual CPU’s saved state and rules'), ('VM exit / entry', 'switch from guest to hypervisor / back'), ('EPT / NPT', 'hardware memory translation for VMs'), ('IOMMU (VT-d)', 'hardware that limits which memory a device may access')],
    diff=TECH,
    where=['Every public cloud VM', 'Every enterprise hypervisor', 'Laptop hypervisors (VirtualBox, Hyper-V, WSL2, Docker Desktop VMs)', 'Android emulator with hardware acceleration'],
    realworld='Intel shipped VT-x in 2005 and AMD followed with AMD-V in 2006. KVM, merged into Linux 2.6.20 in 2007, was designed to require these extensions — and today the AWS Nitro Hypervisor is built on KVM.',
    pro='Performance tuning of a hypervisor is mostly the art of avoiding VM exits. On a KVM host, <code>perf kvm stat live</code> shows exit reasons and counts; features like APICv/posted interrupts exist only to remove exits for interrupts.')

# ---------------------------------------------------------------- 5 OS-level (container by hand)
def a_ctr(k):
    o = t(180, 12, ['Download a tiny OS file tree', 'New namespaces: own PID 1 and hostname', 'chroot: Alpine files on the Ubuntu kernel'][k], 9, 'ink', bold=True)
    o += box(10, 112, 340, 24, 'green', rx=4) + t(180, 128, 'Ubuntu 24.04 host · kernel 6.18 (shared)', 7.8, 'ink', bold=True)
    if k == 0:
        o += box(10, 30, 160, 60, 'card', rx=6) + t(90, 52, 'alpine-minirootfs', 8, 'ink', bold=True) + t(90, 68, '3.5 MB → 8.7 MB unpacked', 7, 'ink2') + packet(170, 60, 230, 60, 'curl')
        o += box(232, 30, 118, 60, 'amber', rx=6) + t(291, 56, 'rootfs/', 8.2, 'ink', bold=True) + t(291, 72, '/bin /etc /lib', 7, 'ink2')
    if k == 1:
        o += box(10, 30, 340, 70, 'blue', rx=6) + t(180, 50, 'unshare --pid --uts --mount --fork', 8, 'ink', bold=True) + t(180, 70, 'inside: PID 1 = sh · hostname tiffingo-box', 7.6, 'ink') + t(180, 86, 'host still sees 70 processes and hostname “vm”', 7, 'ink2')
    if k == 2:
        o += box(10, 30, 340, 70, 'blue', rx=6) + t(180, 50, 'chroot rootfs /bin/sh', 8, 'ink', bold=True) + t(180, 70, '/etc/os-release → Alpine Linux v3.24', 7.6, 'green', bold=True) + t(180, 86, 'uname -r → 6.18 (the host’s kernel)', 7.4, 'ink')
    return o
A_CTR = cap([a_ctr(k) for k in range(3)], [('Get a tiny OS file tree', 'Download the Alpine minimal root filesystem: just files, no kernel.', 'Real size in our lab: 3.5 MB, 8.7 MB unpacked.'), ('Create namespaces', 'unshare gives the shell its own process tree and hostname;', 'the host is untouched.'), ('chroot into Alpine', 'Inside, the OS files are Alpine; the kernel is still the host’s 6.18.', 'That is OS-level virtualization — a container, built by hand.')],
    'OS-level virtualization in action', 'Our real lab: Alpine Linux running on an Ubuntu host with no VM.', 'Container by hand', 'Animation: download Alpine minirootfs; unshare creates PID and UTS namespaces; chroot into Alpine shows Alpine files with the host kernel.', 't5anim')
T5 = vtype(5, 'OS-level virtualization (containers)', 'green',
    'OS-level virtualization is a method in which the operating-system kernel allows multiple isolated user-space instances — <b>containers</b> — to run on one host; each has its own view of processes, network, files and hostname (namespaces) and its own resource limits (cgroups), while all share the host kernel.',
    'A hostel: private lockable rooms for each student, quick and cheap to move into, but one shared kitchen and water tank — the kernel. If the kitchen breaks, every room is affected.',
    'TiffinGo’s 20 MB menu API does not need its own operating system. As a container it runs beside the billing service on the same VM, starts in milliseconds and cannot see billing’s files or processes.',
    'Docker, Podman, containerd, CRI-O, LXC/LXD; Kubernetes; cloud: Amazon ECS/EKS/Fargate, Azure AKS/Container Apps, Google GKE/Cloud Run.',
    '', A_CTR,
    'many small services, fast deployments, consistent environments, high density.',
    'you need a different OS family or must isolate untrusted strangers on one host — use VMs or micro-VMs.',
    deep='the docker run animation and namespace table below; <a href="../01-virtualization-and-hypervisors/#type2">4.1 type 2</a>; <a href="../05-virtualization-vs-cloud-vs-containers/">4.5</a>.',
    plain='Instead of creating whole pretend computers, the operating system creates separate, locked rooms for programs. Each program sees only its own files and its own processes, but all rooms run on the same core of the operating system — so they are tiny and start almost instantly.',
    how=[('Get the files', 'A container image (or here, a root filesystem) holds the OS files and the app — but no kernel.'), ('Isolate the view', 'The kernel creates new namespaces: PID (own process list), mount (own files), UTS (own hostname), network (own IP), IPC, user.'), ('Change the root', 'chroot/pivot_root makes the image’s folder the process’s “/”.'), ('Limit resources', 'cgroups cap CPU, memory and I/O for the group.'), ('Start the app', 'The app becomes PID 1 inside; every system call goes to the shared host kernel.'), ('Clean up', 'When the last process exits, the namespaces disappear.')],
    words=[('root filesystem', 'the folder tree an OS needs: /bin, /etc, /lib…'), ('chroot', 'make a folder look like “/” to a process'), ('namespace', 'a private view of one kind of system resource'), ('cgroup', 'a resource limit for a group of processes'), ('PID 1', 'the first process; when it ends, the container ends')],
    diff=table(['', 'Container', 'VM (types 2–4)', 'LPAR (type 1)'], [['Kernel', 'shared', 'own', 'own'], ['Size', 'MBs', 'GBs', 'very large'], ['Start', 'ms', '30–60 s', 'minutes'], ['Different OS family', 'no', 'yes', 'yes']], minw=520),
    where=['Microservices on Kubernetes/ECS', 'CI/CD pipelines', 'Data and ML jobs', 'Developer laptops (Docker Desktop)'],
    realworld='Google runs Search, Gmail and YouTube in containers on its internal Borg system and has said it starts billions of containers a week; Kubernetes was created from that experience.',
    pro='A container “image” is just a tarball of layers plus a JSON config (the OCI spec). <code>docker save alpine | tar -t</code> shows the layers — no magic, no kernel inside.')

# ---------------------------------------------------------------- 6 I/O (anim passed from _body)
def T6(IOA):
    return vtype(6, 'I/O virtualization (emulated, virtio, SR-IOV)', 'blue',
        'I/O virtualization lets multiple virtual machines share physical input/output devices — network cards, disk controllers, GPUs — either by <b>emulating</b> a device in software, by <b>paravirtual</b> drivers (virtio) that exchange data through shared memory, or by hardware <b>SR-IOV</b>, where one PCIe device presents many lightweight virtual functions that are assigned directly to VMs.',
        'A restaurant kitchen with one serving window: at first a waiter carries every plate (emulation), then a conveyor belt is added (virtio), and finally each table gets its own serving hatch straight from the kitchen (SR-IOV).',
        'TiffinGo’s order API on EC2 needs to handle Diwali traffic. Its instance uses the Elastic Network Adapter, which uses SR-IOV-style direct access, so packets bypass the hypervisor and the instance gets up to tens of Gbps with low jitter.',
        'QEMU emulated devices (e1000, IDE), virtio-net/virtio-blk, SR-IOV NICs (Intel, Mellanox/NVIDIA); cloud: AWS ENA (enhanced networking), Azure Accelerated Networking, Google gVNIC.',
        '', IOA,
        'network or storage performance matters — use virtio at least, SR-IOV/enhanced networking where offered.',
        'you need live migration of VMs with directly assigned devices; and emulated devices only for very old guests.',
        plain='Many virtual machines must share one real network card and one disk controller. There are three ways: the hypervisor pretends to be the card (slow), the VM uses a special driver that hands data over efficiently (fast), or the card itself splits into many mini-cards, one for each VM (fastest).',
        how=[('Emulated device', 'The hypervisor presents a well-known old device (e.g. Intel e1000). Every register access by the guest driver causes a trap and is emulated in software.'), ('Paravirtual (virtio)', 'The guest uses a virtio driver; requests are placed in shared-memory queues (virtqueues) and the host is notified once per batch.'), ('Host side', 'A backend (QEMU, vhost in the kernel, or hardware) processes the queue and talks to the real device.'), ('SR-IOV: physical and virtual functions', 'An SR-IOV device has one Physical Function (PF, managed by the host) and many Virtual Functions (VFs) — light PCIe devices.'), ('Assign a VF', 'The hypervisor assigns a VF to a VM; the IOMMU ensures the VF can access only that VM’s memory.'), ('Direct data path', 'Packets flow between the VM and the card without the hypervisor in the way — near bare-metal speed.')],
        words=[('I/O', 'input/output: network, disk and other device traffic'), ('PCIe', 'the slot/bus where cards plug into a server'), ('virtqueue', 'a shared queue for virtio requests'), ('PF / VF', 'the full device / one lightweight slice of it'), ('IOMMU', 'hardware guard for device memory access')],
        diff=table(['', 'Emulated', 'Paravirtual (virtio)', 'SR-IOV / passthrough'], [['Guest driver', 'standard old driver', 'virtio driver', 'vendor VF driver (e.g. ENA)'], ['Hypervisor in data path', 'yes, every access', 'yes, per batch', 'no'], ['Speed', 'slow', 'fast', 'near native'], ['Live migration', 'easy', 'easy', 'hard (device tied to host)']], minw=560),
        where=['High-throughput cloud networking (ENA, Accelerated Networking, gVNIC)', 'Telecom network functions (NFV)', 'Storage-heavy databases (NVMe)', 'Old guests that only have generic drivers (emulated)'],
        realworld='AWS documents that enhanced networking on EC2 uses SR-IOV to give higher bandwidth, higher packet-per-second performance and lower latency; Azure’s Accelerated Networking is also built on SR-IOV.',
        pro='On Nitro, AWS went one step further than SR-IOV: the ENA and NVMe “devices” the instance sees are implemented by Nitro cards, so even the VF logic lives outside the host CPU.')

# ---------------------------------------------------------------- 7 GPU
def f_gpu():
    a = box(34, 60, 154, 100, 'amber', rx=8) + t(111, 78, 'One big oven', 8.4, 'ink', bold=True)
    for i in range(3):
        a += box(44 + i * 48, 90, 40, 56, 'blue', rx=3) + t(64 + i * 48, 122, f'tray {i + 1}', 6.8, 'ink', bold=True)
    a += t(111, 184, 'Rent a whole oven, a time slot,', 7, 'ink') + t(111, 196, 'or a fixed shelf', 7, 'ink')
    r = ''
    for i, (n, d, tn) in enumerate([('Passthrough', 'whole GPU → one VM', 'violet'), ('vGPU / time-slicing', 'GPU shared in turns', 'amber'), ('MIG partitions', 'fixed slices, own memory', 'green')]):
        x = 240 + i * 128
        r += box(x, 54, 120, 60, tn, rx=6) + t(x + 60, 74, n, 8, 'ink', bold=True) + t(x + 60, 92, d, 6.8, 'ink2')
        vms = 1 if i == 0 else (4 if i == 1 else 3)
        for j in range(vms):
            r += box(x + 4 + j * (112 / vms), 122, 112 / vms - 4, 22, 'blue', rx=3) + t(x + 2 + j * (112 / vms) + (112 / vms) / 2, 137, 'VM', 6.8, 'ink', bold=True)
        r += arrow(x + 60, 150, x + 60, 166)
    r += box(240, 168, 376, 30, 'card', rx=6) + t(428, 188, 'One physical GPU (e.g. NVIDIA A100 / H100 / A10)', 8, 'ink', bold=True)
    r += t(428, 222, 'MIG: up to 7 isolated GPU instances, each with its own memory and compute', 7.2, 'ink2')
    return apanels('Left: one big oven rented whole, by time slot or by fixed shelf. Right: one physical GPU shared three ways — passthrough to one VM, vGPU time-slicing among four VMs, MIG partitions into fixed slices for three VMs.',
        'GPU virtualization: one expensive GPU, many users', 'one big oven', a, ['Expensive equipment', 'is shared, not duplicated.'], 'The real thing: three ways to share a GPU', r)
T7 = vtype(7, 'GPU virtualization (passthrough, vGPU, MIG)', 'blue',
    'GPU virtualization lets one physical graphics/AI accelerator be used by several virtual machines or containers — by <b>passing</b> the whole GPU to one VM, by <b>time-slicing</b> it among many (vGPU), or by <b>partitioning</b> it in hardware into isolated instances with dedicated memory and compute (e.g. NVIDIA Multi-Instance GPU, MIG).',
    'One big, expensive oven in a bakery: you can rent the whole oven, rent it by time slot, or rent one fixed shelf. Nobody buys a new oven for each small cake.',
    'TiffinGo’s “dish photo quality” model needs only a fraction of a large GPU for inference. Using a MIG slice (or a fractional-GPU VM) instead of a whole GPU cuts the cost while keeping its memory separate from other jobs.',
    'NVIDIA vGPU software, NVIDIA MIG (A100, H100 and later), AMD MxGPU, Kubernetes GPU time-slicing; cloud: GPU instances on EC2, Azure NV-series with fractional GPUs, GKE with multi-instance GPUs.',
    f_gpu(), '',
    'GPUs are under-used by single jobs (inference, virtual desktops, notebooks).',
    'training large models that need the full GPU and fast GPU-to-GPU links — use whole GPUs/passthrough.',
    plain='Graphics and AI chips (GPUs) are very expensive. Instead of giving each user a whole one, the chip is shared: given whole to one machine, shared in turns, or cut into fixed slices.',
    how=[('Passthrough', 'The hypervisor gives the entire GPU to one VM using the IOMMU; the VM’s normal driver controls it directly.'), ('vGPU (mediated)', 'A host driver time-slices the GPU among VMs; each VM sees a virtual GPU with a share of memory.'), ('MIG', 'On supported NVIDIA GPUs the hardware itself is split into up to 7 instances, each with dedicated memory, cache and compute units — strong isolation.'), ('Scheduler', 'In Kubernetes, the GPU device plugin advertises whole GPUs, MIG slices or time-sliced replicas to pods.'), ('Monitor', 'Use nvidia-smi / DCGM to see utilization per instance.')],
    words=[('GPU', 'a processor with thousands of small cores, used for graphics and AI'), ('passthrough', 'giving a real device directly to one VM'), ('MIG', 'NVIDIA’s hardware partitioning of one GPU'), ('time-slicing', 'taking turns on the same hardware')],
    diff=table(['', 'Passthrough', 'vGPU / time-slicing', 'MIG'], [['Users per GPU', '1', 'many', 'up to 7'], ['Isolation', 'full', 'weaker (shared memory bandwidth)', 'strong (hardware)'], ['Best for', 'training, max speed', 'virtual desktops, light jobs', 'inference, notebooks']], minw=520),
    where=['AI inference serving', 'Virtual desktops for designers (VDI with GPU)', 'Data-science notebooks for many students', 'Cloud gaming'],
    realworld='NVIDIA’s Multi-Instance GPU lets an A100 or H100 be split into up to seven isolated GPU instances, and Google Kubernetes Engine supports scheduling pods onto these MIG slices.',
    pro='MIG isolation is in hardware — separate memory controllers and L2 cache slices — so one tenant cannot slow another’s memory bandwidth, unlike time-slicing where a busy neighbour still competes.')

SUMMARY = table(['#', 'Type', 'Split made by', 'Guest modified?', 'Speed', 'Where you meet it'], [
    ['1', 'Hardware partitioning', 'firmware', 'no', 'native', 'IBM Z, IBM Power'], ['2', 'Full (binary translation)', 'hypervisor rewriting code', 'no', 'good', 'early VMware, QEMU TCG'],
    ['3', 'Paravirtualization', 'hypervisor + cooperating guest', 'yes', 'very good I/O', 'Xen PV, virtio, ENA'], ['4', 'Hardware-assisted', 'hypervisor + CPU (VT-x/AMD-V)', 'no', 'near native', 'KVM, Hyper-V, ESXi, Nitro'],
    ['5', 'OS-level', 'OS kernel', 'n/a (shared kernel)', 'native', 'Docker, Kubernetes'], ['6', 'I/O virtualization', 'hypervisor / NIC (SR-IOV)', 'driver only', 'up to native', 'ENA, Accelerated Networking'], ['7', 'GPU virtualization', 'driver / GPU hardware (MIG)', 'driver only', 'up to native', 'AI inference, VDI']], minw=700)
CHECK = ('  <h3>Check yourself: which type fits?</h3>\n' +
    qx('A. A bank wants production, test and DR copies of core banking on one mainframe, with fixed, guaranteed processors for production.', ['OS-level virtualization', 'Hardware partitioning (LPARs)', 'Full virtualization', 'GPU virtualization'], 1, 'Firmware-enforced LPARs give fixed, predictable resources.') +
    qx('B. VirtualBox says “VT-x is disabled”. Which type of virtualization is it trying to use?', ['Paravirtualization', 'Hardware-assisted virtualization', 'Binary translation', 'SR-IOV'], 1, 'VT-x is the CPU extension for hardware-assisted virtualization; enable it in the BIOS.') +
    qx('C. A Linux VM’s disk is slow because it uses an emulated IDE controller. Best fix?', ['Add RAM', 'Switch to virtio (paravirtual) drivers', 'Use LPARs', 'Use MIG'], 1, 'virtio removes most traps on I/O.') +
    qx('D. Ten data-science students need GPUs for small notebooks; one A100 is available.', ['Passthrough to one VM', 'MIG or time-slicing', 'Binary translation', 'LPAR'], 1, 'Split the GPU into slices or time-share it.') +
    qx('E. Which technique requires changing the guest operating system?', ['Full virtualization', 'Paravirtualization', 'Hardware-assisted', 'Containers'], 1, 'The guest is modified to use hypercalls.'))

def build(IOA):
    intro = ('  <p>Lesson 4.1 showed the eight <i>things</i> that can be virtualized. This lesson zooms into the most important one — the <b>server</b> — and asks two questions: <b>where</b> is the split made (firmware, hypervisor or OS kernel), and <b>how</b> does a hypervisor deal with a guest operating system that wants full control of the CPU? Each type follows the same order as in 4.1.</p>\n'
             + challenge(['Why did x86 need binary translation when IBM mainframes did not?', 'Why is SR-IOV fast but bad for live migration — and what did AWS do differently?', 'Why does MIG isolate tenants better than GPU time-slicing?'], 'types 2, 6 and 7') + MAP
             + jump(['LPAR', 'Full', 'Para', 'Hardware-assisted', 'OS-level', 'I/O', 'GPU']))
    return intro + T1 + T2 + T3 + T4 + T5 + T6(IOA) + T7 + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY + '\n' + CHECK
