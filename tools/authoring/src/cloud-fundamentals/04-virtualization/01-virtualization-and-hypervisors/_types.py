"""Section: Types of virtualization, one by one (imported by _body.py of lesson 4.1)."""
from cloudkit import *
from _types_extra import EXTRA
def vt(num, *a, **k):
    return vtype(num, *a, **EXTRA[num], **k)

def panels(title, ana_title, ana_svg, ana_cap, real_title, real_svg, note=''):
    o = t(320, 16, title, 11, 'ink', bold=True)
    o += box(8, 28, 206, 212, 'card', rx=10) + t(111, 44, 'Analogy: ' + ana_title, 8.2, 'ink', bold=True) + ana_svg
    for i, c in enumerate(ana_cap):
        o += t(111, 216 + i * 12, c, 6.9, 'ink2')
    o += arrow(216, 134, 228, 134)
    o += box(230, 28, 402, 212, 'card', rx=10) + t(431, 44, real_title, 8.2, 'ink', bold=True) + real_svg
    if note:
        o += t(320, 256, note, 7.4, 'ink2')
    return o

def fig(aria, content):
    return bigfig(aria, content, h=266)

# ===================================================================== overview map
def mapfig():
    o = t(320, 16, 'Types of virtualization — named after WHAT is made virtual', 11, 'ink', bold=True)
    o += box(220, 28, 200, 40, 'amber', rx=20) + t(320, 45, 'Virtualization', 10, 'ink', bold=True) + t(320, 60, 'software version of a physical resource', 7, 'ink2')
    groups = [('Compute', 'green', [('1', 'Server', 'whole machine → VMs', 'server'), ('2', 'OS-level', 'one kernel → containers', 'app'), ('3', 'Memory', 'RAM → per-VM address spaces', 'chip')]),
              ('User workspace', 'blue', [('4', 'Desktop', 'your PC → runs in data centre', 'laptop'), ('5', 'Application', 'one app → runs without install', 'app')]),
              ('Infrastructure', 'violet', [('6', 'Network', 'cables/switches → software networks', 'globe'), ('7', 'Storage', 'many disks → one pool', 'disk')]),
              ('Information', 'red', [('8', 'Data', 'many sources → one virtual view', 'db')])]
    for g, (gn, tn, items) in enumerate(groups):
        x = 12 + g * 158
        o += f'<path d="M320,68 L{x + 74},86" style="fill:none;stroke:#999;stroke-width:1.4"/>'
        o += box(x, 86, 148, 24, tn, rx=6) + t(x + 74, 102, gn, 8.6, 'ink', bold=True)
        for i, (n, name, sub, icn) in enumerate(items):
            y = 118 + i * 50
            o += box(x, y, 148, 44, 'card', rx=6) + pin(x + 13, y + 14, n) + ic(icn, x + 120, y + 9, 0.8) + t(x + 26, y + 18, name, 8.6, 'ink', anchor='start', bold=True) + t(x + 8, y + 35, sub, 6.8, 'ink2', anchor='start')
    o += t(320, 284, 'Split ONE into MANY: server, OS-level, memory, desktop (many users on few hosts). Pool MANY into ONE: storage, data. Network does both.', 7.6, 'ink2')
    o += t(320, 298, 'How server virtualization is achieved (full, para, hardware-assisted) and hardware helpers (VT-x, SR-IOV, vGPU) are covered in “How it works” below and in 4.2.', 7.2, 'ink2')
    return o
MAP = bigfig('Map of eight types of virtualization in four groups. Compute: 1 server, 2 OS-level (containers), 3 memory. User workspace: 4 desktop, 5 application. Infrastructure: 6 network, 7 storage. Information: 8 data. Note: some split one resource into many, others pool many into one.', mapfig(), h=308)

# ===================================================================== 1 server
def f_server():
    a = box(42, 56, 138, 124, 'amber', rx=4)
    for i in range(6):
        r, c = divmod(i, 2)
        a += box(52 + c * 62, 64 + r * 36, 56, 28, 'blue', rx=3) + t(80 + c * 62, 82 + r * 36, 'Flat ' + 'ABCDEF'[i], 7.4, 'ink', bold=True)
    a += box(30, 182, 162, 18, 'red', rx=3) + t(111, 195, 'one plot + foundation', 7, 'ink', bold=True)
    r = ''
    for i, (app, osn) in enumerate([('Mail', 'Windows Server'), ('Website', 'Ubuntu 24.04'), ('Accounts', 'RHEL 9')]):
        x = 240 + i * 128
        r += box(x, 54, 120, 80, 'blue', rx=6) + t(x + 60, 68, f'VM {i + 1}', 8, 'ink', bold=True) + box(x + 8, 76, 104, 22, 'card', rx=3) + t(x + 60, 91, 'app: ' + app, 7.4, 'ink') + box(x + 8, 104, 104, 22, 'green', rx=3) + t(x + 60, 119, 'guest OS: ' + osn, 7.2, 'ink')
    r += box(240, 142, 376, 26, 'amber', rx=5) + t(428, 159, 'Hypervisor (ESXi / KVM / Hyper-V / Nitro) — divides and isolates', 7.8, 'ink', bold=True)
    r += box(240, 174, 376, 26, 'card', rx=5) + t(428, 191, 'Physical server: 32 cores · 256 GB RAM · disks · network cards', 7.6, 'ink')
    r += t(428, 222, 'Flat = VM · building rules + guard = hypervisor · foundation = hardware', 7.2, 'ink2')
    return fig('Left: apartment building with six flats on one plot. Right: one physical server running three VMs (Mail on Windows Server, Website on Ubuntu, Accounts on RHEL) on a hypervisor.', panels('Server virtualization: one physical server, many virtual servers', 'an apartment building', a, ['Own lock, own kitchen per family;', 'shared land, walls, water, lift.'], 'The real thing: one host, three VMs', r))
def a_server(k):
    o = t(180, 12, ['Before: one app per server', 'Install a hypervisor on one host', 'After: five VMs on one host'][k], 9, 'ink', bold=True)
    apps = [('Mail', 8), ('Website', 15), ('Accounts', 5), ('HR', 3), ('Backup', 10)]
    if k == 0:
        for i, (n, p) in enumerate(apps):
            x = 8 + i * 70
            o += box(x, 26, 62, 100, 'card', rx=5) + ic('server', x + 22, 32, 0.8) + t(x + 31, 66, n, 7.6, 'ink', bold=True) + t(x + 31, 82, '1 server', 6.8, 'ink2') + box(x + 6, 122 - p * 1.2, 50, p * 1.2, 'red', rx=2) + t(x + 31, 98, f'{p}% busy', 7.4, 'red', bold=True)
    if k == 1:
        for i, (n, p) in enumerate(apps):
            o += box(8, 24 + i * 24, 70, 20, 'card', rx=3) + t(43, 37 + i * 24, n, 7, 'ink2')
        o += packet(80, 80, 196, 80, 'P2V')
        o += box(200, 26, 150, 104, 'card', rx=6) + ic('server', 262, 36, 0.9) + t(275, 76, 'one powerful host', 8, 'ink', bold=True) + box(208, 94, 134, 26, 'amber', rx=4) + t(275, 111, 'hypervisor installed', 7.6, 'ink', bold=True)
    if k == 2:
        o += box(8, 24, 344, 112, 'card', rx=6)
        for i, (n, p) in enumerate(apps):
            o += box(16 + i * 67, 32, 61, 46, 'blue', rx=4) + t(46 + i * 67, 50, 'VM', 7.4, 'ink2') + t(46 + i * 67, 66, n, 7.4, 'ink', bold=True)
        o += box(16, 84, 328, 20, 'amber', rx=3) + t(180, 98, 'hypervisor', 7.6, 'ink', bold=True) + box(16, 108, 328, 20, 'green', rx=3) + t(180, 122, 'host CPU 41% busy · 4 old servers switched off', 7.6, 'ink', bold=True)
    return o
A_SERVER = anim_one('Animated', 'Server virtualization in action', 'TiffinGo’s five idle office servers become five VMs on one host.', 'Server virtualization', 'Animation: five servers 3–15% busy; a hypervisor is installed on one host and servers are converted (P2V); five VMs run on one host at 41%.',
    cap_frames([a_server(k) for k in range(3)], [('One app per server', 'Mail, website, accounts, HR, backup — each on its own box.', 'Average 8.2% busy: most of the money is idle.'), ('Install a hypervisor', 'A Type 1 hypervisor goes on one powerful host;', 'each old server is converted into a VM (P2V).'), ('Five VMs, one host', 'Each app keeps its own OS and stays isolated.', 'Host 41% busy; four servers, their power and space saved.')]),
    ['Before: one app per server.', 'Install a hypervisor.', 'After: five VMs on one host.'], delay=5500, hid='t1anim')
T1 = vt(1, 'Server virtualization', 'green',
    'Server virtualization is the partitioning of one physical server into multiple isolated <b>virtual machines</b>, each with its own operating system and applications, by a software layer called a <b>hypervisor</b> that allocates and isolates CPU, memory, storage and network.',
    'An apartment building: one plot and foundation, many flats. Each family has its own lock and kitchen and cannot enter the next flat — but all share the land, walls and water. The building rules and the guard are the hypervisor.',
    'TiffinGo has five office servers (mail, website, accounts, HR, backup) averaging 8.2% CPU. Converted into five VMs on one host, the host runs at 41% and four servers are switched off (Lesson 4.6 calculates the savings). Every EC2 instance you launch is this same idea, rented.',
    'VMware vSphere/ESXi, Microsoft Hyper-V, KVM, Xen, Proxmox; in the cloud: <b>Amazon EC2</b>, <b>Azure Virtual Machines</b>, <b>Google Compute Engine</b>.',
    f_server(), A_SERVER,
    'apps need their own OS (Windows + Linux), strong isolation, or you are consolidating many lightly used servers.',
    'a workload needs the full machine (big databases, HPC) or ultra-low latency — consider bare metal or dedicated hosts.',
    '<a href="../02-server-hardware-and-os-level-virtualization/">4.2</a> (three levels) and <a href="../06-pros-cons-consolidation-and-hypervisor-security/">4.6</a> (consolidation).')

# ===================================================================== 2 OS-level
def f_os():
    a = box(32, 58, 158, 96, 'amber', rx=4)
    for i in range(4):
        a += box(40 + i * 37, 66, 32, 40, 'blue', rx=3) + t(56 + i * 37, 90, f'R{i + 1}', 7.4, 'ink', bold=True)
    a += box(40, 116, 142, 30, 'red', rx=3) + t(111, 129, 'ONE shared kitchen', 7.2, 'ink', bold=True) + t(111, 140, '+ water tank', 6.6, 'ink2')
    a += t(111, 176, 'Private rooms, cheap and quick', 7.2, 'ink') + t(111, 190, 'to move into.', 7.2, 'ink')
    r = ''
    for i, (n, f) in enumerate([('menu API', 'Alpine'), ('billing', 'Debian'), ('worker', 'Ubuntu'), ('nginx', 'Alpine')]):
        x = 240 + i * 96
        r += box(x, 54, 90, 92, 'blue', rx=6) + t(x + 45, 68, n, 8, 'ink', bold=True) + t(x + 45, 82, f + ' files', 7, 'ink2')
        for j, l in enumerate(['own PID 1', 'own IP + ports', 'own hostname']):
            r += t(x + 45, 98 + j * 12, l, 6.8, 'ink')
        r += box(x + 6, 132, 78, 12, 'red', rx=2) + t(x + 45, 141, 'cgroup limit', 6.4, 'ink', bold=True)
    r += box(240, 152, 378, 22, 'violet', rx=4) + t(429, 167, 'Container runtime (Docker / containerd)', 7.6, 'ink', bold=True)
    r += box(240, 178, 378, 22, 'green', rx=4) + t(429, 193, 'ONE Linux kernel: namespaces (rooms) + cgroups (limits)', 7.6, 'ink', bold=True)
    r += t(429, 222, 'Room = container · shared kitchen = kernel · hostel rules = namespaces + cgroups', 7.2, 'ink2')
    return fig('Left: a hostel with four private rooms and one shared kitchen. Right: four containers (menu API, billing, worker, nginx) with their own files, PID 1, IP and hostname, each with a cgroup limit, on a container runtime and one shared Linux kernel.', panels('OS-level virtualization: one kernel, many isolated containers', 'a hostel', a, ['If the kitchen breaks,', 'every room is affected.'], 'The real thing: four containers on one kernel', r))
def a_os(k):
    o = t(180, 12, ['Problem: apps clash on one OS', 'Kernel creates isolated rooms', 'Containers start in milliseconds'][k], 9, 'ink', bold=True)
    if k == 0:
        o += box(10, 26, 340, 110, 'card', rx=6) + t(180, 42, 'one Linux server', 8, 'ink', bold=True)
        o += box(20, 52, 150, 40, 'blue', rx=4) + t(95, 68, 'menu API', 8, 'ink', bold=True) + t(95, 82, 'wants port 80, Python 3.12', 6.8, 'ink2')
        o += box(190, 52, 150, 40, 'violet', rx=4) + t(265, 68, 'old billing app', 8, 'ink', bold=True) + t(265, 82, 'wants port 80, Python 3.8', 6.8, 'ink2')
        o += t(180, 116, '⚠ port 80 in use · library versions clash', 8.2, 'red', bold=True)
    if k == 1:
        for i, (n, ip) in enumerate([('menu API', '172.17.0.2:80'), ('billing', '172.17.0.3:80')]):
            x = 20 + i * 170
            o += box(x, 28, 150, 70, 'blue' if i == 0 else 'violet', rx=6) + t(x + 75, 46, n, 8.4, 'ink', bold=True) + t(x + 75, 62, 'own IP ' + ip, 7, 'ink') + t(x + 75, 76, 'own Python, own files', 7, 'ink') + t(x + 75, 90, 'PID 1 = the app', 7, 'ink')
        o += box(20, 108, 320, 24, 'green', rx=4) + t(180, 124, 'same kernel; namespaces keep them apart', 7.8, 'ink', bold=True)
    if k == 2:
        for i in range(4):
            o += box(14 + i * 86, 30, 78, 50, 'blue', rx=5) + t(53 + i * 86, 52, f'ctr {i + 1}', 8, 'ink', bold=True) + t(53 + i * 86, 68, 'started', 7, 'green', bold=True)
        o += box(14, 90, 332, 22, 'green', rx=4) + t(180, 105, 'one kernel', 7.8, 'ink', bold=True)
        o += t(180, 132, 'Our lab: 3–4 ms to start · base image 3.5 MB (a VM image: 593 MB)', 7.8, 'ink', bold=True)
    return o
A_OS = anim_one('Animated', 'OS-level virtualization in action', 'Two apps that fight on one server live happily as containers.', 'Containers', 'Animation: two apps clash on one Linux server over port 80 and Python versions; namespaces give each its own IP, files and PID 1 on the same kernel; four containers start in milliseconds.',
    cap_frames([a_os(k) for k in range(3)], [('Apps clash on one OS', 'Two apps want the same port and different library versions.', 'Without isolation, one of them has to move to another server.'), ('Namespaces build rooms', 'Each app gets its own IP, ports, files and process tree,', 'but both still use the same Linux kernel.'), ('Start in milliseconds', 'No OS to boot: a container is just an isolated process.', 'Measured in our lab: 3–4 ms, 3.5 MB base image.')]),
    ['Apps clash on one OS.', 'Namespaces build rooms.', 'Containers start in milliseconds.'], delay=5500, hid='t2anim')
T2 = vt(2, 'OS-level virtualization (containers)', 'green',
    'OS-level virtualization lets one operating-system kernel run multiple isolated user-space instances called <b>containers</b>; the kernel isolates what each can see (namespaces) and limits what each can use (cgroups), so containers share the host kernel instead of running their own.',
    'A hostel: each student gets a private, lockable room (own files, own address), cheap and quick to move into — but everybody shares one kitchen and water tank (the kernel). If the kitchen breaks, every room suffers.',
    'TiffinGo’s new menu API needs Python 3.12 and port 80; the old billing app needs Python 3.8 and also port 80. On one server they clash. As two containers they each get their own IP, files and Python, start in milliseconds and run side by side on one VM.',
    'Docker, Podman, containerd, LXC; Kubernetes runs them at scale. Cloud: <b>Amazon ECS/EKS/Fargate</b>, <b>Azure AKS/Container Apps</b>, <b>Google GKE/Cloud Run</b>.',
    f_os(), A_OS,
    'many small services, fast releases, identical dev/test/prod environments, high density.',
    'you need a different OS family (Windows app on a Linux host) or must isolate untrusted strangers’ code — use VMs or micro-VMs.',
    '<a href="../02-server-hardware-and-os-level-virtualization/">4.2</a> (build a container by hand) and <a href="../05-virtualization-vs-cloud-vs-containers/">4.5</a>.')

# ===================================================================== 3 memory
def f_mem():
    a = box(30, 56, 82, 44, 'blue', rx=4) + t(71, 74, 'Guest A key:', 7.2, 'ink') + t(71, 90, 'Room 101', 8.4, 'ink', bold=True)
    a += box(122, 56, 82, 44, 'violet', rx=4) + t(163, 74, 'Guest B key:', 7.2, 'ink') + t(163, 90, 'Room 101', 8.4, 'ink', bold=True)
    a += box(30, 112, 174, 70, 'amber', rx=4) + t(117, 128, 'Reception register', 7.8, 'ink', bold=True) + t(117, 146, 'A · 101 → real room 704', 7.4, 'ink') + t(117, 162, 'B · 101 → real room 312', 7.4, 'ink') + t(117, 176, 'empty rooms given to new guests', 6.6, 'ink2')
    r = ''
    for i, (vm, tn, frame) in enumerate([('VM A', 'blue', '0x8A000'), ('VM B', 'violet', '0x31000')]):
        x = 246 + i * 190
        r += box(x, 54, 170, 26, tn, rx=4) + t(x + 85, 71, f'{vm}: app uses virtual address 0x7f…', 7.2, 'ink', bold=True)
        r += arrow(x + 85, 80, x + 85, 90) + box(x, 90, 170, 22, 'card', rx=4) + t(x + 85, 105, 'guest page table (guest OS)', 7, 'ink')
        r += arrow(x + 85, 112, x + 85, 120) + box(x, 120, 170, 22, tn, rx=4) + t(x + 85, 135, '“my RAM address 0x1000”', 7.2, 'ink', bold=True)
        r += arrow(x + 85, 142, x + 85, 154)
        r += t(x + 85, 196, '→ real frame ' + frame, 7.2, tn, bold=True)
    r += box(246, 154, 360, 24, 'amber', rx=4) + t(426, 170, 'EPT / NPT: second page table, kept by the hypervisor, walked by the CPU', 7.4, 'ink', bold=True)
    r += box(246, 202, 360, 18, 'green', rx=4) + t(426, 215, 'Physical RAM (256 GB host)', 7.4, 'ink', bold=True)
    return fig('Left: two hotel guests both hold keys for room 101; the reception register maps them to real rooms 704 and 312. Right: two VMs both use guest-physical address 0x1000; guest page tables then the hypervisor’s EPT/NPT map them to different real RAM frames.', panels('Memory virtualization: every VM thinks its RAM starts at zero', 'hotel room numbers', a, ['Same room number on the key,', 'different real rooms.'], 'The real thing: two-stage address translation', r))
def a_mem(k):
    o = t(180, 12, ['Both VMs think they own RAM from 0', 'Hypervisor maps them to real RAM', 'Overcommit: ballooning'][k], 9, 'ink', bold=True)
    for i, (n, tn) in enumerate([('VM A (4 GB)', 'blue'), ('VM B (4 GB)', 'violet')]):
        x = 14 + i * 176
        o += box(x, 26, 156, 34, tn, rx=5) + t(x + 78, 47, n + ': 0 … 4 GB', 7.8, 'ink', bold=True)
    o += box(14, 108, 332, 26, 'card', rx=4)
    for j in range(12):
        tn = 'card'
        if k >= 1 and j in (1, 2, 3):
            tn = 'blue'
        if k >= 1 and j in (6, 7, 8):
            tn = 'violet'
        if k == 2 and j == 3:
            tn = 'green'
        if k == 2 and j in (9, 10):
            tn = 'violet'
        o += box(18 + j * 27.4, 112, 24, 18, tn, rx=2)
    o += t(180, 146, 'physical RAM frames', 7, 'ink2')
    if k == 0:
        o += t(180, 84, 'Both ask for “address 0x1000”. Who gets the real RAM?', 7.8, 'red', bold=True)
    if k == 1:
        o += packet(92, 60, 70, 110, 'EPT') + packet(268, 60, 210, 110, 'EPT') + t(180, 92, 'different real frames — they never overlap', 7.6, 'green', bold=True)
    if k == 2:
        o += box(40, 64, 90, 20, 'green', rx=10) + t(85, 78, 'balloon inflates', 7, 'ink', bold=True) + packet(110, 120, 290, 120, '')
        o += t(260, 92, 'VM B is busy: gets freed RAM', 7.4, 'violet', bold=True)
    return o
A_MEM = anim_one('Animated', 'Memory virtualization in action', 'How two VMs share one set of RAM chips without seeing each other.', 'Memory virtualization', 'Animation: two VMs both believe their memory starts at zero; the hypervisor’s EPT maps their pages to different real frames; when VM A is idle a balloon driver frees its unused RAM for busy VM B.',
    cap_frames([a_mem(k) for k in range(3)], [('Each VM sees RAM from 0', 'Every guest OS is written for a computer whose RAM starts at 0.', 'Two VMs on one host both use address 0x1000.'), ('Second-level page tables (EPT/NPT)', 'The CPU translates guest addresses to real frames using a table', 'the hypervisor controls. A VM cannot even name another VM’s RAM.'), ('Overcommit with ballooning', 'A balloon driver inside idle VM A “inflates”, so its OS hands back', 'unused pages; the hypervisor gives them to busy VM B.')]),
    ['Each VM sees RAM from 0.', 'EPT maps to real frames.', 'Ballooning reclaims idle RAM.'], delay=5500, hid='t3anim')
T3 = vt(3, 'Memory virtualization', 'green',
    'Memory virtualization abstracts physical RAM so that each virtual machine (and each process) sees its own contiguous address space starting at zero; the hypervisor, helped by CPU features such as Intel <b>EPT</b> and AMD <b>NPT</b>, maps guest-physical memory to real host memory, enforcing isolation and enabling techniques such as overcommit, ballooning and page sharing.',
    'Hotel room numbers: two guests both hold a key that says “Room 101” on their own floor plan, but the reception register maps one to real room 704 and the other to 312. Neither can open the other’s room, and empty rooms are handed to new guests.',
    'TiffinGo runs 10 VMs of 4 GB each on a 32 GB host. Most are idle at night: the hypervisor reclaims their unused pages (ballooning) and shares identical pages, such as ten copies of the same Linux libraries, as one copy (KSM / transparent page sharing).',
    'Intel EPT, AMD NPT/RVI in every modern CPU; VMware ballooning and transparent page sharing; Linux KSM; Hyper-V Dynamic Memory. In the cloud you do not see it, but it is why an EC2 VM cannot read its neighbour’s RAM.',
    f_mem(), A_MEM,
    'you want isolation between VMs (always on) and higher density on hosts with many idle VMs.',
    'overcommitting memory heavily: when every VM wants its RAM at once, the host swaps and everything slows down. Clouds do not overcommit memory on most instance types.',
    'overcommit in the deep dive below; memory pages in live migration, <a href="../04-vm-provisioning-and-migration/">4.4</a>.')

# ===================================================================== 4 desktop
def f_desk():
    a = box(34, 56, 154, 56, 'green', rx=6) + t(111, 78, 'Stadium', 8.6, 'ink', bold=True) + t(111, 94, 'the match is played here', 7, 'ink2')
    for i in range(3):
        x = 36 + i * 54
        a += arrow(111, 112, x + 23, 146) + box(x, 148, 46, 34, 'blue', rx=4) + t(x + 23, 169, 'TV', 8, 'ink', bold=True)
    r = ''
    for i, (icn, n) in enumerate([('laptop', 'Old laptop'), ('phone', 'Tablet'), ('app', 'Thin client')]):
        y = 54 + i * 52
        r += box(240, y, 88, 44, 'blue', rx=5) + ic(icn, 248, y + 10, 0.8) + t(298, y + 20, n, 7.4, 'ink', bold=True) + t(298, y + 34, 'shows screen', 6.6, 'ink2')
        r += arrow(330, y + 22, 372, 86)
    r += t(352, 222, 'pixels ↓  keys/mouse ↑', 6.8, 'ink2')
    r += box(374, 62, 92, 50, 'violet', rx=5) + t(420, 82, 'Connection', 7.8, 'ink', bold=True) + t(420, 96, 'broker', 7.8, 'ink', bold=True) + t(420, 107, 'who gets which', 6.4, 'ink2')
    r += box(374, 124, 92, 46, 'amber', rx=5) + t(420, 143, 'Golden image', 7.6, 'ink', bold=True) + t(420, 158, 'Windows + Office', 6.6, 'ink2')
    r += arrow(466, 86, 480, 86) + arrow(466, 146, 480, 146)
    r += box(482, 54, 140, 132, 'card', rx=6) + t(552, 68, 'Desktop host (DC / cloud)', 7.4, 'ink', bold=True)
    for i in range(4):
        rr, c = divmod(i, 2)
        r += box(490 + c * 66, 76 + rr * 46, 60, 40, 'blue', rx=4) + t(520 + c * 66, 93 + rr * 46, 'Win 11', 7.2, 'ink', bold=True) + t(520 + c * 66, 106 + rr * 46, 'desktop VM', 6.4, 'ink2')
    r += box(482, 192, 140, 28, 'green', rx=4) + t(552, 210, 'profiles + files (central)', 7.2, 'ink', bold=True)
    return fig('Left: a cricket match in a stadium shown live on three TVs. Right: laptops, tablets and thin clients only display screens streamed from desktop VMs on a central host; a connection broker assigns desktops cloned from a golden image; user files stay in central storage.', panels('Desktop virtualization (VDI / DaaS): your PC runs in the data centre', 'cricket on TV', a, ['Break your TV — the match goes on.', 'Watch on any screen.'], 'The real thing: desktops streamed to any device', r))
def a_desk(k):
    o = t(180, 12, ['1 · Log in from any device', '2 · Broker gives you a desktop', '3 · Only pixels travel', '4 · Laptop lost? Nothing lost'][k], 9, 'ink', bold=True)
    lt = 'red' if k == 3 else 'blue'
    o += box(10, 46, 80, 56, lt, rx=6) + ic('laptop', 38, 52, 0.9) + t(50, 92, 'agent laptop', 7.4, 'ink', bold=True)
    o += box(130, 28, 90, 40, 'violet', rx=6) + t(175, 46, 'broker', 8, 'ink', bold=True) + t(175, 60, 'checks login', 6.8, 'ink2')
    o += box(250, 28, 100, 100, 'card', rx=6) + t(300, 42, 'data centre', 7.4, 'ink', bold=True)
    for i in range(2):
        tn = 'green' if (k >= 1 and i == 0) else 'blue'
        o += box(258, 50 + i * 38, 84, 32, tn, rx=4) + t(300, 70 + i * 38, 'desktop VM ' + str(i + 1), 7.2, 'ink', bold=True)
    if k == 0:
        o += packet(90, 70, 130, 50, 'login')
    if k == 1:
        o += packet(220, 48, 258, 64, 'assign') + t(175, 96, 'clone of golden image', 7, 'ink2')
    if k == 2:
        o += packet(258, 72, 90, 72, 'pixels') + packet(90, 90, 258, 90, 'keys')
    if k == 3:
        o += t(50, 120, 'no data on it', 7.4, 'red', bold=True) + t(240, 146, 'log in from a new laptop: same desktop, same files', 7.6, 'green', bold=True)
    return o
A_DESK = anim_one('Animated', 'Desktop virtualization in action', 'A TiffinGo call-centre agent working from home.', 'VDI login', 'Animation: agent logs in from a laptop; the broker assigns a desktop VM cloned from a golden image; only screen pixels go down and keystrokes go up; if the laptop is lost no data is lost.',
    cap_frames([a_desk(k) for k in range(4)], [('Log in from any device', 'The agent opens the VDI client (or a browser) on any laptop', 'and signs in with MFA.'), ('The broker assigns a desktop', 'It finds or creates a Windows desktop VM, often a linked clone', 'of the golden image (Lesson 4.4), and connects the user.'), ('Only pixels travel', 'Screen updates stream down; keystrokes and clicks go up', '(RDP, HDX, PCoIP/Blast, DCV). Data never leaves the data centre.'), ('Laptop lost? Nothing lost', 'The laptop held no customer data. IT disables the login;', 'the agent continues tomorrow from any other device.')]),
    ['Log in from any device.', 'The broker assigns a desktop.', 'Only pixels travel.', 'Laptop lost: nothing lost.'], delay=5500, hid='t4anim')
T4 = vt(4, 'Desktop virtualization (VDI and DaaS)', 'blue',
    'Desktop virtualization separates a user’s desktop environment — operating system, applications and data — from the physical device by running it on a central server or cloud and delivering it over the network, so the device only displays the screen and sends keyboard and mouse input. Self-hosted, it is called <b>VDI</b> (Virtual Desktop Infrastructure); bought as a cloud service, <b>DaaS</b> (Desktop as a Service).',
    'Watching a cricket match on TV: the match happens in the stadium; your TV only shows it. Change or break the TV and the match goes on. Your desktop “plays” in the data centre; your laptop is just the TV.',
    'TiffinGo’s 200 call-centre agents work from home on cheap or personal laptops. Customer phone numbers and addresses must never be stored on those laptops. With VDI, every agent gets a Windows desktop in the data centre; if a laptop is stolen, IT simply disables the login. Banks and BPOs moved to this model at scale in 2020.',
    'Citrix, Omnissa (formerly VMware) Horizon, Microsoft Remote Desktop Services; cloud: <b>Amazon WorkSpaces</b>, <b>Azure Virtual Desktop</b> and <b>Windows 365</b>; on Google Cloud through partners (Citrix, Omnissa) and ChromeOS devices.',
    f_desk(), A_DESK,
    'data must stay central (finance, health, call centres), staff use many or unmanaged devices, contractors join and leave often, or you need to patch 500 desktops at once.',
    'users need heavy local graphics offline, or the network is slow and unreliable — every click travels to the data centre. Persistent per-user desktops also cost more than shared, non-persistent ones.')

# ===================================================================== 5 application
def f_app():
    a = box(26, 86, 124, 58, 'amber', rx=6) + t(88, 106, 'Food truck', 8.4, 'ink', bold=True) + t(88, 120, 'own stove, gas,', 6.8, 'ink2') + t(88, 132, 'water, menu', 6.8, 'ink2')
    a += box(150, 104, 40, 40, 'amber', rx=6) + '<circle cx="54" cy="150" r="8" style="fill:#555"/><circle cx="168" cy="150" r="8" style="fill:#555"/>'
    a += f'<path d="M18,160 L204,160" style="stroke:#999;stroke-width:2"/>' + t(111, 182, 'parks on any street', 7.2, 'ink')
    r = ''
    cols = [('Installed normally', 'red'), ('Packaged (isolated)', 'green'), ('Published / streamed', 'blue')]
    for c, (n, tn) in enumerate(cols):
        x = 238 + c * 132
        r += t(x + 62, 62, n, 8, 'ink', bold=True)
    x = 238
    r += box(x, 70, 58, 30, 'blue', rx=3) + t(x + 29, 89, 'App v1', 7.2, 'ink', bold=True) + box(x + 66, 70, 58, 30, 'violet', rx=3) + t(x + 95, 89, 'App v2', 7.2, 'ink', bold=True)
    r += box(x, 104, 124, 26, 'card', rx=3) + t(x + 62, 121, 'shared DLLs / Java / registry', 6.8, 'ink') + t(x + 62, 146, '⚠ versions clash', 7.6, 'red', bold=True)
    r += box(x, 156, 124, 24, 'green', rx=3) + t(x + 62, 172, 'Windows', 7.4, 'ink', bold=True)
    x = 370
    for i in range(2):
        r += f'<rect x="{x + i * 64}" y="68" width="58" height="80" rx="14" style="fill:none;stroke:#2E8B57;stroke-width:2;stroke-dasharray:4 3"/>'
        r += box(x + 5 + i * 64, 74, 48, 22, 'blue' if i == 0 else 'violet', rx=3) + t(x + 29 + i * 64, 89, f'App v{i + 1}', 7, 'ink', bold=True) + t(x + 29 + i * 64, 112, 'own files', 6.4, 'ink2') + t(x + 29 + i * 64, 124, '+ registry', 6.4, 'ink2') + t(x + 29 + i * 64, 136, 'bubble', 6.4, 'ink2')
    r += box(x, 156, 124, 24, 'green', rx=3) + t(x + 62, 172, 'Windows', 7.4, 'ink', bold=True)
    x = 502
    r += box(x, 70, 124, 60, 'card', rx=4) + t(x + 62, 84, 'Server', 7.6, 'ink', bold=True) + box(x + 10, 92, 104, 30, 'blue', rx=3) + t(x + 62, 111, 'app runs here', 7.2, 'ink', bold=True)
    r += arrow(x + 62, 130, x + 62, 150) + t(x + 96, 144, 'window only', 6.6, 'ink2')
    r += box(x + 20, 152, 84, 30, 'blue', rx=3) + t(x + 62, 171, 'any device', 7.2, 'ink', bold=True)
    r += t(431, 210, 'MSIX app attach, App-V', 6.8, 'ink2') + t(564, 210, 'Citrix Apps, WorkSpaces Apps, RemoteApp', 6.4, 'ink2') + t(300, 210, 'classic setup.exe', 6.8, 'ink2')
    return fig('Left: a food truck that brings its own kitchen and parks on any street. Right: three ways to run an app — installed normally with shared libraries that clash, packaged in isolated bubbles with own files and registry, and published from a server with only the window streamed to any device.', panels('Application virtualization: run an app without installing it', 'a food truck', a, ['It brings its own kitchen;', 'needs nothing from the street.'], 'The real thing: installed vs packaged vs streamed', r))
def a_app(k):
    o = t(180, 12, ['Problem: two versions cannot coexist', 'Package each app in its own bubble', 'Or publish it from a server'][k], 9, 'ink', bold=True)
    if k == 0:
        o += box(14, 28, 150, 40, 'blue', rx=5) + t(89, 44, 'Old accounts app', 7.8, 'ink', bold=True) + t(89, 58, 'needs Java 8', 7, 'ink2')
        o += box(196, 28, 150, 40, 'violet', rx=5) + t(271, 44, 'New GST tool', 7.8, 'ink', bold=True) + t(271, 58, 'needs Java 21', 7, 'ink2')
        o += box(14, 84, 332, 26, 'card', rx=4) + t(180, 101, 'one Windows PC: only one Java on the PATH', 7.6, 'ink', bold=True) + t(180, 132, '⚠ installing one breaks the other', 8.4, 'red', bold=True)
    if k == 1:
        for i, (n, j, tn) in enumerate([('Old accounts app', 'Java 8 inside', 'blue'), ('New GST tool', 'Java 21 inside', 'violet')]):
            x = 14 + i * 182
            o += f'<rect x="{x}" y="26" width="150" height="66" rx="18" style="fill:none;stroke:#2E8B57;stroke-width:2;stroke-dasharray:4 3"/>' + box(x + 12, 34, 126, 26, tn, rx=4) + t(x + 75, 51, n, 7.6, 'ink', bold=True) + t(x + 75, 78, j + ' + own files', 7, 'ink')
        o += box(14, 104, 332, 24, 'green', rx=4) + t(180, 120, 'same PC, nothing installed into Windows itself', 7.6, 'ink', bold=True)
    if k == 2:
        o += box(200, 28, 150, 92, 'card', rx=6) + t(275, 44, 'app server', 7.8, 'ink', bold=True) + box(210, 54, 130, 26, 'blue', rx=4) + t(275, 71, 'accounts app runs', 7.4, 'ink', bold=True) + box(210, 86, 130, 26, 'green', rx=4) + t(275, 103, 'data stays here', 7.4, 'ink', bold=True)
        o += box(10, 50, 110, 60, 'blue', rx=6) + ic('laptop', 52, 56, 0.9) + t(65, 98, 'Chromebook', 7.4, 'ink', bold=True)
        o += packet(200, 72, 120, 72, 'window') + packet(120, 92, 200, 92, 'clicks')
    return o
A_APP = anim_one('Animated', 'Application virtualization in action', 'TiffinGo’s accounts team needs an old app and a new one on the same PCs.', 'Application virtualization', 'Animation: an old app needing Java 8 and a new tool needing Java 21 clash on one PC; packaged in isolated bubbles both run; or the app is published from a server and only its window reaches a Chromebook.',
    cap_frames([a_app(k) for k in range(3)], [('Two versions cannot coexist', 'Installing the new tool upgrades Java and breaks the old app:', 'classic “DLL hell” on shared PCs.'), ('Package each app in a bubble', 'Each app carries its own runtime, files and registry keys, and', 'sees them as if installed — Windows itself stays clean.'), ('Or publish it from a server', 'The app runs on a server; only its window is streamed to the user’s', 'device, even a Chromebook or tablet. Data never leaves the server.')]),
    ['Two versions clash.', 'Package each app in a bubble.', 'Or publish it from a server.'], delay=5500, hid='t5anim')
T5 = vt(5, 'Application virtualization', 'blue',
    'Application virtualization runs an application isolated from the underlying operating system, without a traditional local installation — either by <b>packaging</b> it with its own virtual file system and registry so it runs in a sandbox on the device, or by <b>publishing (streaming)</b> it from a server so that it executes remotely and only its user interface is shown on the device.',
    'A food truck: it brings its own stove, gas, water and menu, so it can park on any street without needing a kitchen there — and two trucks never fight over one stove. A packaged app brings its own files and settings in the same way.',
    'TiffinGo’s accounts team must keep an old accounting app that needs Java 8 while also using a new GST tool that needs Java 21. Installed normally, one breaks the other. Packaged, both run on the same PC. For field staff on Chromebooks, the same app is published from a Windows server and only the window is streamed.',
    'Packaging: MSIX app attach, Microsoft App-V (still supported; Microsoft cancelled its retirement and extended App-V server support to 2029). Publishing: Citrix Virtual Apps, Microsoft RemoteApp; cloud: <b>Amazon WorkSpaces Applications</b> (formerly AppStream 2.0), <b>Azure Virtual Desktop RemoteApp</b>; on Google Cloud through partners.',
    f_app(), A_APP,
    'old apps must run on new OSes, conflicting versions must coexist, licences must be centrally controlled, or one app must reach many kinds of device.',
    'apps with kernel drivers or deep OS hooks (antivirus, some hardware tools) — they cannot be packaged; streamed apps need a good network.')

# ===================================================================== 6 network
def f_net():
    a = box(20, 100, 182, 46, 'card', rx=4) + f'<path d="M20,123 L202,123" style="stroke:#fff;stroke-width:2;stroke-dasharray:8 6"/>'
    for i, (tn, lab) in enumerate([('blue', 'A'), ('violet', 'B'), ('amber', 'C')]):
        a += box(28 + i * 60, 104 + (i % 2) * 22, 48, 18, tn, rx=4) + t(52 + i * 60, 117 + (i % 2) * 22, 'van ' + lab, 7, 'ink', bold=True)
    a += t(111, 70, 'One highway, many companies', 7.8, 'ink', bold=True) + t(111, 84, 'sealed, labelled vans', 7.2, 'ink2') + t(111, 170, 'Road = physical network', 7.2, 'ink') + t(111, 184, 'Seal + label = encapsulation + tag', 7.2, 'ink')
    r = ''
    for h in range(2):
        x = 240 + h * 202
        r += box(x, 54, 176, 120, 'card', rx=6) + t(x + 88, 68, f'Host {h + 1}', 7.8, 'ink', bold=True)
        r += box(x + 8, 76, 76, 30, 'blue', rx=4) + t(x + 46, 95, 'VPC A VM', 7, 'ink', bold=True) + box(x + 92, 76, 76, 30, 'violet', rx=4) + t(x + 130, 95, 'VPC B VM', 7, 'ink', bold=True)
        r += box(x + 8, 112, 160, 22, 'green', rx=3) + t(x + 88, 127, 'virtual switch + firewall rules', 7, 'ink', bold=True)
        r += box(x + 8, 140, 160, 26, 'amber', rx=3) + t(x + 88, 157, 'wrap + tag / unwrap (Nitro, VTEP)', 7, 'ink', bold=True)
    r += box(240, 186, 378, 24, 'red', rx=4) + t(429, 202, 'Physical “underlay” network: sees only host 1 ↔ host 2', 7.6, 'ink', bold=True)
    r += f'<path d="M416,150 L442,150" style="fill:none;stroke:#E0A100;stroke-width:2.4;stroke-dasharray:5 3"/>'
    return fig('Left: one highway with sealed, labelled vans of three companies. Right: two hosts each with a VPC A VM and a VPC B VM, a virtual switch with firewall rules and an encapsulation layer; a physical underlay network connects the hosts.', panels('Network virtualization: many private networks on one physical network', 'a highway with sealed vans', a, ['Vans share the road but never', 'mix their parcels.'], 'The real thing: overlays on a shared underlay', r))
def a_net(k):
    o = t(180, 12, ['VM sends a normal packet', 'Host wraps it and adds the network tag', 'Only the right VM receives it'][k], 9, 'ink', bold=True)
    for h in range(2):
        x = 8 + h * 196
        o += box(x, 26, 148, 76, 'card', rx=5) + box(x + 6, 32, 64, 28, 'blue', rx=3) + t(x + 38, 50, 'VPC A', 7.4, 'ink', bold=True) + box(x + 78, 32, 64, 28, 'violet', rx=3) + t(x + 110, 50, 'VPC B', 7.4, 'ink', bold=True)
        o += box(x + 6, 68, 136, 26, 'amber', rx=3) + t(x + 74, 85, 'wrap / unwrap', 7.2, 'ink', bold=True)
    o += box(8, 112, 344, 22, 'red', rx=4) + t(180, 127, 'physical network', 7.6, 'ink', bold=True)
    if k == 0:
        o += packet(46, 60, 46, 70, '') + t(180, 148, 'packet: 10.10.1.5 → 10.10.2.7 (inside VPC A)', 7.6, 'ink', bold=True)
    if k == 1:
        o += box(150, 66, 60, 20, 'blue', rx=3) + t(180, 80, 'tag: VPC A', 7, 'ink', bold=True) + packet(80, 100, 280, 100, 'wrapped')
    if k == 2:
        o += packet(242, 72, 242, 60, '') + t(242, 22, '', 6) + t(310, 148, 'VPC B VM never sees it', 7.6, 'violet', bold=True) + t(90, 148, 'delivered to VPC A VM', 7.6, 'green', bold=True)
    return o
A_NET = anim_one('Animated', 'Network virtualization in action', 'Kitchen VM talks to billing VM inside TiffinGo’s VPC — on hardware shared with another company.', 'Overlay network', 'Animation: a VM in VPC A sends a packet; the host wraps it and adds a VPC A tag; the physical network carries it; the other host unwraps it and delivers it only to the VPC A VM.',
    cap_frames([a_net(k) for k in range(3)], [('VM sends a normal packet', 'The VM just sends to a private IP. It has no idea the network', 'is software, or that another company’s VM sits beside it.'), ('Wrap and tag', 'The host puts the packet inside an outer packet addressed to the', 'other host, with a tag naming VPC A (VXLAN VNI or AWS’s own format).'), ('Unwrap and deliver', 'The receiving host checks the tag and the firewall rules and delivers', 'only to the VPC A VM. Same IPs in VPC B never collide.')]),
    ['VM sends a normal packet.', 'Wrap and tag.', 'Unwrap and deliver.'], delay=5500, hid='t6anim')
T6 = vt(6, 'Network virtualization', 'violet',
    'Network virtualization creates logical, software-defined networks — virtual NICs, switches, routers, firewalls and load balancers — that are decoupled from the physical network hardware, typically by encapsulating traffic in overlays (such as VXLAN) and controlling it centrally with software-defined networking (SDN).',
    'One highway shared by many courier companies. Each company’s vans are sealed and labelled, so parcels never mix even though every van uses the same road. The road is the physical network; the seal and label are encapsulation and the network tag.',
    'TiffinGo’s kitchen and billing VMs run on hosts shared with other AWS customers, some using the very same 10.10.x.x addresses. Each company’s VPC is a separate virtual network; the billing VM accepts traffic only from the kitchen subnet on port 443 — all created by API in seconds, with no new cables.',
    'VLANs, VXLAN, Open vSwitch, VMware NSX, Cisco ACI; cloud: <b>AWS VPC</b> (on Nitro cards), <b>Azure Virtual Network</b>, <b>Google VPC</b>; NFV examples: load balancers, NAT gateways, cloud firewalls.',
    f_net(), A_NET,
    'many tenants or teams share hardware, networks must be created and changed by code, or traffic between workloads must be segmented.',
    'you forget the extra header bytes (MTU problems) or plan overlapping IP ranges you will later need to connect.',
    '<a href="../03-network-storage-and-data-virtualization/">4.3</a> (packet path step by step, VLAN vs VXLAN, AWS CLI VPC lab).')

# ===================================================================== 7 storage
def f_sto():
    a = box(30, 56, 160, 40, 'blue', rx=4) + t(110, 72, 'Your passbook', 7.6, 'ink', bold=True) + t(110, 88, 'Balance ₹50,000', 8.2, 'ink', bold=True)
    for i in range(4):
        a += box(30 + i * 41, 120, 36, 46, 'amber', rx=3) + t(48 + i * 41, 146, 'vault', 6.6, 'ink')
    a += t(110, 112, 'notes spread over many vaults', 7, 'ink2') + t(110, 184, 'you never pick the vault', 7.2, 'ink')
    r = ''
    for i, (n, s) in enumerate([('VM 1 disk', '100 GB'), ('VM 2 disk', '500 GB'), ('VM 3 disk', '200 GB')]):
        x = 244 + i * 126
        r += box(x, 54, 116, 34, 'blue', rx=4) + t(x + 58, 70, n, 7.6, 'ink', bold=True) + t(x + 58, 82, s, 7, 'ink2') + arrow(x + 58, 88, x + 58, 100)
    r += box(240, 102, 380, 48, 'green', rx=6) + t(430, 120, 'Storage virtualization layer (pool)', 8.4, 'ink', bold=True) + t(430, 138, 'thin provisioning · snapshots · replication · grow online', 7.2, 'ink')
    r += arrow(430, 150, 430, 160)
    for i, (k, v) in enumerate([('SSD 1 TB', 'vendor A'), ('HDD 4 TB', 'vendor B'), ('HDD 4 TB', 'vendor B'), ('NVMe 2 TB', 'vendor C')]):
        r += cyl(250 + i * 92, 162, 74, 44, k, 'amber') + t(287 + i * 92, 220, v, 6.8, 'ink2')
    return fig('Left: a passbook showing a balance while the notes sit in many bank vaults. Right: three VM disks served from a storage virtualization pool with thin provisioning, snapshots and replication, built on four physical disks of different types and vendors.', panels('Storage virtualization: many disks pooled, virtual disks handed out', 'a bank account', a, ['You see the balance,', 'not which vault holds the notes.'], 'The real thing: one pool, many virtual disks', r))
def a_sto(k):
    o = t(180, 12, ['Problem: one server full, another empty', 'Pool all the disks', 'Hand out and grow virtual disks'][k], 9, 'ink', bold=True)
    if k == 0:
        o += box(14, 30, 150, 96, 'card', rx=6) + t(89, 46, 'Server A', 8, 'ink', bold=True) + box(24, 56, 130, 24, 'red', rx=3) + t(89, 72, 'disk 100% full', 7.6, 'ink', bold=True) + t(89, 106, 'orders DB stops', 7.4, 'red', bold=True)
        o += box(196, 30, 150, 96, 'card', rx=6) + t(271, 46, 'Server B', 8, 'ink', bold=True) + box(206, 56, 26, 24, 'green', rx=3) + box(232, 56, 104, 24, 'card', rx=3) + t(284, 72, '80% empty', 7.6, 'ink', bold=True) + t(271, 106, 'space wasted', 7.4, 'ink2')
    if k == 1:
        for i in range(4):
            o += cyl(18 + i * 86, 96, 64, 38, ['disk A', 'disk B', 'disk C', 'disk D'][i], 'amber')
        o += box(14, 30, 332, 46, 'green', rx=6) + t(180, 50, 'one pool: 11 TB, 6 TB free', 8.4, 'ink', bold=True) + t(180, 66, 'LVM volume group · SAN · Ceph · EBS', 7, 'ink')
    if k == 2:
        o += box(14, 30, 332, 30, 'green', rx=6) + t(180, 49, 'pool', 8, 'ink', bold=True)
        o += box(14, 74, 150, 40, 'blue', rx=5) + t(89, 90, 'orders DB disk', 7.6, 'ink', bold=True) + t(89, 104, '500 GB → 700 GB, online', 7, 'green', bold=True) + packet(89, 60, 89, 74, '')
        o += box(196, 74, 150, 40, 'violet', rx=5) + t(271, 90, 'snapshot', 7.6, 'ink', bold=True) + t(271, 104, 'before upgrade, instant', 7, 'ink2')
        o += t(180, 136, 'Lab (4.3): two 196 MB disks → one 392 MB pool; 10 GiB disk uses 196 KiB', 7.4, 'ink', bold=True)
    return o
A_STO = anim_one('Animated', 'Storage virtualization in action', 'No more “disk full here, empty there”.', 'Storage pool', 'Animation: server A’s disk is full while server B’s is mostly empty; all disks are pooled; virtual disks are carved from the pool, grown online and snapshotted.',
    cap_frames([a_sto(k) for k in range(3)], [('One server full, another empty', 'Disks tied to one server cannot help another — the orders', 'database stops while space sits idle next door.'), ('Pool all the disks', 'The virtualization layer joins disks of any size and vendor', 'into one pool and keeps track of every block.'), ('Hand out and grow virtual disks', 'Each VM gets a virtual disk from the pool; it can grow without', 'downtime, be snapshotted, replicated or moved.')]),
    ['One full, one empty.', 'Pool all disks.', 'Hand out and grow virtual disks.'], delay=5500, hid='t7anim')
T7 = vt(7, 'Storage virtualization', 'violet',
    'Storage virtualization pools physical storage from multiple devices — often of different types and vendors — into a single logical resource managed centrally, from which virtual disks (block), file shares or object stores are presented independently of where the data is physically kept.',
    'A bank account: your passbook shows one balance, but the notes sit in many vaults and branches. You never choose a vault; the bank moves money around without you noticing. Your virtual disk is the balance; the physical disks are the vaults.',
    'TiffinGo’s server A ran out of disk and the orders database stopped, while server B was 80% empty. After pooling, every VM’s disk comes from one pool: the orders disk grew from 500 to 700 GB without downtime, and a snapshot was taken before each upgrade. An AWS EBS volume works the same way across thousands of storage servers.',
    'Linux LVM, SAN arrays (Dell, NetApp, HPE), Ceph, VMware vSAN; cloud: <b>Amazon EBS / EFS / S3</b>, <b>Azure Managed Disks / Files / Blob</b>, <b>Google Persistent Disk / Filestore / Cloud Storage</b>.',
    f_sto(), A_STO,
    'many servers need flexible capacity, snapshots, replication or disks that outlive a server.',
    'thin-provisioned pools are overcommitted without monitoring — they fail when real space runs out.',
    '<a href="../03-network-storage-and-data-virtualization/">4.3</a> (LVM, thin provisioning, copy-on-write, EBS internals, AWS CLI lab).')

# ===================================================================== 8 data
def f_data():
    a = box(40, 56, 142, 30, 'blue', rx=4) + t(111, 75, '🔍 Mumbai → Delhi', 8, 'ink', bold=True)
    for i in range(3):
        a += box(28 + i * 58, 128, 50, 36, 'amber', rx=4) + t(53 + i * 58, 150, 'Airline ' + 'ABC'[i], 6.8, 'ink', bold=True) + arrow(53 + i * 58, 128, 111, 88)
    a += t(111, 184, 'the site owns no planes', 7.2, 'ink')
    r = ''
    for i, (n, s) in enumerate([('orders.csv', 'file'), ('cities.parquet', 'data lake'), ('crm.db', 'database')]):
        y = 56 + i * 52
        r += box(240, y, 120, 42, 'amber', rx=4) + t(300, y + 18, n, 7.6, 'ink', bold=True) + t(300, y + 32, s, 6.8, 'ink2') + arrow(360, y + 21, 392, 130)
    r += box(394, 70, 120, 120, 'green', rx=6) + t(454, 90, 'Virtual data', 8.2, 'ink', bold=True) + t(454, 104, 'layer', 8.2, 'ink', bold=True)
    for j, l in enumerate(['catalog', 'query split', 'pushdown', 'join + cache']):
        r += t(454, 124 + j * 15, l, 7, 'ink')
    r += arrow(514, 130, 532, 130) + box(534, 92, 88, 76, 'blue', rx=6) + ic('chart', 566, 100, 0.9) + t(578, 140, 'one report', 7.6, 'ink', bold=True) + t(578, 154, 'live, no copy', 6.8, 'ink2')
    return fig('Left: a travel site search for Mumbai to Delhi asking three airlines’ systems at once. Right: orders.csv, cities.parquet and crm.db feed a virtual data layer (catalog, query split, pushdown, join and cache) that returns one live report without copying data.', panels('Data virtualization: query many sources as if they were one', 'a travel booking site', a, ['Fares from every airline in one list,', 'fetched live, nothing stored.'], 'The real thing: one SQL view over three sources', r))
def a_data(k):
    o = t(180, 12, ['One question arrives', 'Split and push down to each source', 'Join and return one answer'][k], 9, 'ink', bold=True)
    o += box(8, 50, 70, 50, 'blue', rx=5) + ic('user', 31, 54, 0.9) + t(43, 92, 'manager', 7.2, 'ink', bold=True)
    o += box(118, 46, 90, 58, 'green', rx=6) + t(163, 70, 'virtual', 7.8, 'ink', bold=True) + t(163, 84, 'layer', 7.8, 'ink', bold=True)
    for i, n in enumerate(['CSV', 'Parquet', 'SQLite']):
        o += box(256, 22 + i * 40, 92, 32, 'amber', rx=4) + t(302, 42 + i * 40, n, 7.6, 'ink', bold=True)
    if k == 0:
        o += packet(78, 75, 118, 75, 'ask') + t(180, 146, '“Revenue and rating per zone?”', 7.8, 'ink', bold=True)
    if k == 1:
        o += packet(208, 60, 256, 38, '') + packet(208, 75, 256, 78, '') + packet(208, 90, 256, 118, '') + t(180, 146, 'each source returns only the rows/columns needed', 7.4, 'ink')
    if k == 2:
        o += packet(118, 75, 78, 75, 'answer') + t(180, 140, 'West · Pune 330 · Mumbai 310 | North · Delhi 300', 7.6, 'green', bold=True) + t(180, 152, '(real result, Lesson 4.3)', 6.8, 'ink2')
    return o
A_DATA = anim_one('Animated', 'Data virtualization in action', 'Management’s question answered from three systems without building a pipeline.', 'Federated query', 'Animation: a manager asks for revenue and rating per zone; the virtual layer splits the query and pushes parts to a CSV file, a Parquet file and a SQLite database; results are joined and returned live.',
    cap_frames([a_data(k) for k in range(3)], [('One question arrives', 'The manager (or a dashboard) asks one SQL question as if', 'all the data lived in one database.'), ('Split and push down', 'The layer looks up where each table lives and sends each source', 'only its part of the work: filters and needed columns.'), ('Join and return', 'Results are joined in memory and returned live — change a source', 'and the next query sees it. Nothing was copied.')]),
    ['One question arrives.', 'Split and push down.', 'Join and return.'], delay=5500, hid='t8anim')
T8 = vt(8, 'Data virtualization', 'red',
    'Data virtualization is an approach to data management that lets applications retrieve and combine data from multiple heterogeneous sources — files, databases, SaaS systems, clouds — through a single unified virtual view, without needing to know where or in what format the data is stored and without physically copying it.',
    'A travel booking site: you type “Mumbai → Delhi” once and see fares from every airline. The site owns no planes and copies no airline databases; it asks each airline live and combines the answers.',
    'TiffinGo’s orders are in CSV exports, the city list in a Parquet file in the data lake, and customer ratings in a CRM database. Management wants revenue and average rating per zone today. One federated SQL query reads all three in place — our lab answer: West · Pune 330, Mumbai 310; North · Delhi 300.',
    'Denodo, TIBCO Data Virtualization, Trino/Presto, DuckDB (our lab); cloud: <b>Amazon Athena Federated Query</b> and Redshift Spectrum, <b>Azure Synapse serverless SQL</b> and Fabric shortcuts, <b>BigQuery external tables / BigQuery Omni</b>.',
    f_data(), A_DATA,
    'you need quick, live answers across systems, data must not be copied (compliance), or you are prototyping before building pipelines.',
    'huge joins repeated every day — move that workload into a warehouse or lake; virtual queries depend on every source being up and fast.',
    '<a href="../03-network-storage-and-data-virtualization/">4.3</a> (federated query animation and DuckDB lab).')


# ===================================================================== basics first (for non-IT learners)
def basicsfig():
    o = t(320, 16, 'Basics first: a computer is like a small office', 11, 'ink', bold=True)
    items = [('chip', 'CPU', 'the worker who does the work', 'split by: server virtualization'), ('meter', 'RAM (memory)', 'the desk: papers being used right now', 'split by: memory virtualization'),
             ('disk', 'Disk (storage)', 'the cupboard: files kept for later', 'pooled by: storage virtualization'), ('globe', 'Network card', 'the phone line to other offices', 'shared by: network virtualization'),
             ('gear', 'Operating system', 'the office manager (Windows, Linux)', 'one per VM; shared by containers'), ('shield', 'Kernel', 'the manager’s core: only it may touch the hardware', 'shared by: OS-level virtualization'),
             ('app', 'Application', 'one job: billing, mail, a website', 'delivered by: application virtualization'), ('server', 'Server', 'an office that serves others all day', 'the thing VMs pretend to be')]
    for i, (icn, a, b, c) in enumerate(items):
        r, col = divmod(i, 4)
        x = 12 + col * 156; y = 30 + r * 108
        o += box(x, y, 148, 100, 'card', rx=8) + ic(icn, x + 8, y + 8, 0.9) + t(x + 38, y + 24, a, 8.8, 'ink', anchor='start', bold=True)
        words = b.split(' ')
        l1, l2 = ' '.join(words[:4]), ' '.join(words[4:])
        o += t(x + 74, y + 52, l1, 7.4, 'ink') + t(x + 74, y + 64, l2, 7.4, 'ink') + box(x + 6, y + 74, 136, 20, 'blue', rx=4) + t(x + 74, y + 88, c, 6.6, 'ink', bold=True)
    o += t(320, 262, 'Virtualization makes a software copy of one of these boxes so it can be split, shared or pooled.', 7.8, 'ink2')
    return o
BASICS = bigfig('Eight tiles explaining computer parts as an office: CPU is the worker, RAM is the desk, disk is the cupboard, network card is the phone line, operating system is the office manager, kernel is the manager’s core that alone touches hardware, application is one job, server is an office serving others. Each tile names the type of virtualization that splits, shares or pools it.', basicsfig(), h=272)

HOOK = ('  <div style="border:1px dashed var(--track);border-radius:8px;padding:10px 14px;margin:12px 0"><p style="margin:0 0 4px"><b>Already work with VMs? Try these before you read:</b></p>'
        '<ol style="margin:0"><li>Why can one TLB miss inside a VM cost six times more memory reads than on bare metal?</li><li>Why does a floating-IP failover trick from your data centre fail inside an AWS VPC?</li><li>Why might a federated query be slower than copying the data first?</li></ol>'
        '<p style="margin:4px 0 0">Answers are in the <b>“For the experienced”</b> boxes of types 3, 6 and 8.</p></div>\n')

# ===================================================================== summary + check
SUMMARY = table(['#', 'Type', 'What is virtualized', 'Analogy', 'TiffinGo scenario', 'AWS', 'Azure', 'Google Cloud'], [
    ['1', 'Server', 'whole physical server', 'apartment building', '5 servers → 1 host', 'EC2', 'Virtual Machines', 'Compute Engine'],
    ['2', 'OS-level', 'OS user space (shared kernel)', 'hostel rooms', 'apps clashing on ports/versions', 'ECS, EKS, Fargate', 'AKS, Container Apps', 'GKE, Cloud Run'],
    ['3', 'Memory', 'RAM addresses', 'hotel room numbers', '10 VMs share 32 GB', '(inside EC2/Nitro)', '(inside Hyper-V)', '(inside KVM)'],
    ['4', 'Desktop', 'user’s whole desktop', 'cricket on TV', '200 home agents', 'WorkSpaces', 'Azure Virtual Desktop, Windows 365', 'partners (Citrix, Omnissa)'],
    ['5', 'Application', 'one app', 'food truck', 'Java 8 + Java 21 apps', 'WorkSpaces Applications (ex-AppStream 2.0)', 'AVD RemoteApp, MSIX app attach', 'partners'],
    ['6', 'Network', 'switches, routers, firewalls', 'highway with sealed vans', 'kitchen vs billing networks', 'VPC', 'Virtual Network', 'VPC'],
    ['7', 'Storage', 'disks and arrays', 'bank account', 'disk full here, empty there', 'EBS, EFS, S3', 'Managed Disks, Files, Blob', 'Persistent Disk, Filestore, Cloud Storage'],
    ['8', 'Data', 'location and format of data', 'travel booking site', 'one report from 3 sources', 'Athena Federated Query', 'Synapse serverless', 'BigQuery external / Omni']], minw=900)

CHECK = ('  <h3>Check yourself: which type fits?</h3>\n' +
    qx('A. A bank wants 500 branch staff to use Windows desktops, but no customer data may ever be stored on branch PCs.', ['Storage virtualization', 'Desktop virtualization (VDI/DaaS)', 'Data virtualization', 'OS-level virtualization'], 1, 'Desktops run centrally; devices only show pixels — Amazon WorkSpaces, Azure Virtual Desktop, Citrix.') +
    qx('B. An engineering firm must run a Windows-only design app on staff Chromebooks.', ['Application virtualization (published/streamed app)', 'Network virtualization', 'Memory virtualization', 'Server virtualization only'], 0, 'Publish just that app from a server (Amazon WorkSpaces Applications, RemoteApp); only the window reaches the Chromebook.') +
    qx('C. Two departments on the same cloud hosts must be unable to reach each other’s servers, even with the same IP ranges.', ['Data virtualization', 'Network virtualization (separate VPCs)', 'Desktop virtualization', 'Storage virtualization'], 1, 'Separate virtual networks with their own tags and rules.') +
    qx('D. A finance team wants one live report joining a SaaS CRM, a MySQL database and files in S3, without building a pipeline.', ['Data virtualization (federated query)', 'Server virtualization', 'Application virtualization', 'Memory virtualization'], 0, 'Query in place, e.g. Athena Federated Query.') +
    qx('E. Ten lightly used physical servers must be reduced to two to save power and space.', ['Server virtualization (consolidation)', 'Data virtualization', 'Application virtualization', 'Network virtualization'], 0, 'Convert each server into a VM (P2V) and run them on fewer hosts.') +
    qx('F. A host with 64 GB RAM runs VMs promised 96 GB in total; idle VMs give back unused memory.', ['Storage thin provisioning', 'Memory virtualization (overcommit + ballooning)', 'Desktop virtualization', 'Containers'], 1, 'The hypervisor maps and reclaims guest memory pages.'))

INTRO = ('  <p><b>Virtualization</b> means creating a <b>virtual (software) version of something physical</b> — a server, a desktop, a network, a disk, even data — so it can be split, shared, pooled or moved without touching the hardware. The <b>type</b> of virtualization is simply named after <b>what</b> is made virtual. Here is the whole family on one map; then each type, one by one, in the same order every time: <b>definition → in plain words → analogy → how it works inside → picture → animation → how it differs from similar types → where used → real-world example → TiffinGo scenario → for the experienced → when to use</b>.</p>\n  <p><b>New to computers?</b> Read this picture first — every type below virtualizes one of these parts.</p>\n' + BASICS + HOOK + MAP +
    '\n  <p style="margin-top:6px"><b>Jump to:</b> ' + ' · '.join(f'<a href="#type{i}">{i} {n}</a>' for i, n in enumerate(['Server', 'OS-level', 'Memory', 'Desktop', 'Application', 'Network', 'Storage', 'Data'], 1)) + '</p>\n')

TYPES_SEC = INTRO + T1 + T2 + T3 + T4 + T5 + T6 + T7 + T8 + '\n  <h3 style="margin-top:34px">All eight types side by side</h3>\n' + SUMMARY + '\n' + CHECK
