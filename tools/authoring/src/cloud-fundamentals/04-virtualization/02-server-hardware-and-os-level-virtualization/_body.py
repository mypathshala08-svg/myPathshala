import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
sys.path.insert(0, HERE)
from _types import build as build_types
from _prac import PRAC
C = 'l42.txt'; CB = 'l42b.txt'
def sec(a, b=None): return capsec(C, a, b)
def secb(a, b=None): return capsec(CB, a, b)

hk = hook('Can you run Alpine Linux on an Ubuntu machine without any virtual machine at all?',
    'Yes — and we did it in this lesson: a 3.5 MB Alpine root filesystem, entered with <code>chroot</code> and Linux <b>namespaces</b>, showed <b>“OS inside: Alpine Linux v3.24”</b> on an Ubuntu 24.04 host, with its own hostname and only its own processes — in <b>4 milliseconds</b>. That is <b>OS-level virtualization</b>, the idea behind Docker. In this lesson you will compare it with <b>server virtualization</b> (whole VMs) and <b>hardware virtualization</b> (help from the CPU and devices).',
    ['Three levels where virtualization can happen: hardware, hypervisor (server) and operating system.', 'How containers isolate with namespaces and limit with cgroups — built by hand.', 'Hardware tricks: partitioning, SR-IOV, GPU sharing.'])
def levels_scene():
    o = t(180, 12, 'Where is the “split” made?', 9, 'ink', bold=True)
    cols = [('Hardware', ['LPAR', 'LPAR'], 'firmware splits machine', 'violet'), ('Hypervisor', ['VM', 'VM', 'VM'], 'each VM has its own OS', 'amber'), ('OS kernel', ['ctr', 'ctr', 'ctr', 'ctr'], 'containers share 1 kernel', 'green')]
    for c, (n, items, sub, tn) in enumerate(cols):
        x = 8 + c * 118
        o += t(x + 55, 30, n + ' level', 8, 'ink', bold=True)
        w = 104 / len(items)
        for i, it in enumerate(items):
            o += box(x + i * w, 38, w - 4, 34, 'blue', rx=3) + t(x + i * w + (w - 4) / 2, 59, it, 6.8, 'ink', bold=True)
        o += box(x, 76, 108, 22, tn, rx=4) + t(x + 54, 91, ['firmware', 'hypervisor', 'one shared kernel'][c], 7, 'ink', bold=True) + box(x, 102, 108, 22, 'card', rx=4) + t(x + 54, 117, 'hardware', 7, 'ink')
        o += t(x + 54, 138, sub, 6.8, 'ink2')
    return o
scene_svg = scene('Three columns: hardware-level partitions split by firmware, hypervisor-level VMs each with their own OS, and OS-level containers sharing one kernel.', levels_scene(), 'The lower the split, the stronger the isolation; <tspan font-weight="700" class="s-acc">the higher, the lighter and faster</tspan>.')
dialogue = '''R> Sir, in 4.1 each VM had its own operating system. Isn’t that heavy for small apps like TiffinGo’s menu API?
A> Very heavy: a whole OS, gigabytes, a minute to boot. For many apps we only need isolation, not a separate kernel. Linux can split itself into isolated rooms — containers.
K> And banks with big IBM machines split hardware itself?
A> Right. Virtualization can happen at three levels: hardware, hypervisor, operating system. Let’s see each, and build a container by hand.'''

def three():
    o = t(320, 16, 'Three levels of server virtualization', 11, 'ink', bold=True)
    data = [('1. Hardware-level partitioning', 'violet', [('LPAR 1', 'AIX'), ('LPAR 2', 'Linux')], ['Firmware/hardware divides one big', 'machine into fixed partitions.'], 'IBM Power LPARs, mainframe partitions', 'strongest isolation · least flexible'),
            ('2. Hypervisor-based (VMs)', 'amber', [('VM 1', 'Windows'), ('VM 2', 'Linux'), ('VM 3', 'Linux')], ['A hypervisor gives each VM virtual', 'hardware; each runs its own kernel.'], 'EC2, Azure VMs, VMware, KVM', 'strong isolation · any OS · GBs, ~1 min boot'),
            ('3. OS-level (containers)', 'green', [('ctr', 'app'), ('ctr', 'app'), ('ctr', 'app'), ('ctr', 'app')], ['One kernel; namespaces isolate and', 'cgroups limit each container.'], 'Docker, Podman, LXC, Kubernetes', 'light · MBs · starts in ms · same kernel only')]
    for c, (n, tn, items, desc, ex, trade) in enumerate(data):
        x = 14 + c * 208
        o += box(x, 30, 198, 254, 'card', rx=10) + t(x + 99, 48, n, 8.8, 'ink', bold=True)
        w = 178 / len(items)
        for i, (a, b) in enumerate(items):
            o += box(x + 10 + i * w, 60, w - 4, 40, 'blue', rx=4) + t(x + 10 + i * w + (w - 4) / 2, 77, a, 7.4, 'ink', bold=True) + t(x + 10 + i * w + (w - 4) / 2, 91, b, 6.8, 'ink2')
        layer = {'violet': 'partition firmware', 'amber': 'hypervisor', 'green': 'one Linux kernel'}[tn]
        if tn == 'green':
            o += box(x + 10, 104, 178, 20, tn, rx=4) + t(x + 99, 118, 'container runtime + ' + layer, 7.2, 'ink', bold=True)
        else:
            o += box(x + 10, 104, 178, 20, tn, rx=4) + t(x + 99, 118, layer, 7.4, 'ink', bold=True)
        o += box(x + 10, 128, 178, 20, 'card', rx=4) + t(x + 99, 142, 'hardware', 7.4, 'ink')
        for i, d in enumerate(desc): o += t(x + 12, 168 + i * 13, d, 7.6, 'ink', anchor='start')
        o += t(x + 12, 210, 'e.g. ' + ex, 7.2, 'ink2', anchor='start') + t(x + 12, 236, trade, 7.2, tn, anchor='start', bold=True)
    return o
THREE = bigfig('Three panels: hardware-level partitioning (LPARs running AIX and Linux on partition firmware), hypervisor-based VMs (Windows and Linux VMs on a hypervisor), and OS-level containers (four containers on one Linux kernel). Each shows examples and trade-offs.', three(), h=294)
def ns():
    o = t(320, 16, 'One Linux kernel, many isolated rooms: namespaces + cgroups', 11, 'ink', bold=True)
    o += box(20, 220, 600, 34, 'green', rx=8) + t(320, 242, 'ONE shared Linux kernel (6.18 on our lab host)', 9, 'ink', bold=True)
    for i, (n, ospec, tn) in enumerate([('Container A: menu API', 'Alpine userspace', 'blue'), ('Container B: billing', 'Ubuntu userspace', 'violet'), ('Container C: worker', 'Debian userspace', 'amber')]):
        x = 30 + i * 198
        o += box(x, 34, 184, 176, tn, rx=10) + t(x + 92, 52, n, 8.6, 'ink', bold=True) + t(x + 92, 66, ospec, 7.4, 'ink2')
        for j, (a, b) in enumerate([('pid', 'own PID 1'), ('net', 'own IP, ports'), ('mnt', 'own / filesystem'), ('uts', 'own hostname'), ('user', 'root inside ≠ root outside')]):
            o += box(x + 10, 74 + j * 20, 164, 17, 'card', rx=3) + t(x + 16, 86 + j * 20, a, 7.4, 'ink', anchor='start', bold=True) + t(x + 168, 86 + j * 20, b, 7, 'ink2', anchor='end')
        o += box(x + 10, 178, 164, 24, 'red', rx=4) + t(x + 92, 194, ['cgroup: 0.5 CPU, 256 MB', 'cgroup: 1 CPU, 512 MB', 'cgroup: 2 CPU, 1 GB'][i], 7.4, 'ink', bold=True)
    return o
NS = bigfig('Three containers on one shared Linux kernel. Each has its own pid, net, mnt, uts and user namespaces (own PID 1, IP, filesystem, hostname, root mapping) and its own cgroup limit on CPU and memory.', ns(), h=264)
picture = ('  <p><b>Server virtualization</b> means splitting one physical server into several isolated servers. The split can be made at three different levels — and each level is used somewhere important:</p>\n' + THREE +
           '\n  <p>The third level needs a closer look, because it powers Docker and Kubernetes. Linux gives each container its own <b>view</b> of the system (namespaces) and its own <b>limits</b> (cgroups), while all of them share one kernel:</p>\n' + NS)

# animation 1: how a container starts
CN = {'cli': (4, 54, 58, 50, 'user', 'docker run', 'you'), 'img': (72, 4, 64, 46, 'disk', 'Image layers', 'read-only'), 'ovl': (72, 104, 64, 46, 'disk', 'overlayfs', '+ writable layer'),
      'ns': (146, 54, 64, 50, 'shield', 'Namespaces', 'pid net mnt uts'), 'cg': (220, 4, 64, 46, 'meter', 'cgroups', 'CPU, memory'), 'net': (220, 104, 64, 46, 'globe', 'veth + bridge', '172.17.0.2'),
      'proc': (292, 54, 62, 50, 'app', 'PID 1', 'your app')}
CS = [dict(on=['cli', 'img'], hot='img', move=(62, 70, 74, 30, 'pull'), head='Step 1 · Get the image', text='The runtime downloads the image: a stack of read-only layers', text2='(base OS files + your app). Alpine’s base is only 3.5 MB.', svc='Docker Hub, Amazon ECR, Azure Container Registry, Google Artifact Registry'),
      dict(on=['cli', 'img', 'ovl'], hot='ovl', move=(104, 50, 104, 104, 'stack'), head='Step 2 · Build the root filesystem', text='overlayfs stacks the layers and adds a thin writable layer on top,', text2='so 10 containers can share one image on disk (copy-on-write).', svc='Deleting the container deletes only the writable layer'),
      dict(on=['cli', 'img', 'ovl', 'ns'], hot='ns', move=(136, 128, 148, 80, 'isolate'), head='Step 3 · Create namespaces', text='New pid, net, mnt, uts, ipc (and often user) namespaces: the process', text2='will see its own PID 1, hostname, files and network — nothing else.', svc='Exactly what our unshare demo does by hand'),
      dict(on=['cli', 'img', 'ovl', 'ns', 'cg'], hot='cg', move=(210, 70, 222, 30, 'limit'), head='Step 4 · Apply cgroup limits', text='--cpus 0.5 --memory 256m becomes cgroup settings: the kernel', text2='throttles CPU and kills the container if it exceeds its memory.', svc='Also used by Kubernetes requests/limits and ECS task sizes'),
      dict(on=['cli', 'img', 'ovl', 'ns', 'cg', 'net'], hot='net', move=(210, 90, 222, 126, 'wire'), head='Step 5 · Plug in the network', text='A veth pair connects the container’s namespace to a host bridge;', text2='-p 8080:80 adds a port-forward rule from the host.', svc='Same veth + namespace trick as Lesson 4.3’s lab'),
      dict(on=list(CN), hot='proc', move=(284, 30, 294, 70, 'exec'), head='Step 6 · Start your app as PID 1', text='The app runs as an ordinary Linux process on the host kernel —', text2='no boot, no second OS. That is why it starts in milliseconds.', svc='ps on the host can still see it; the container cannot see the host')]
CTR = flow_anim('What happens in “docker run”', 'Six steps that turn an image into an isolated process — no hypervisor involved.', 'Starting a container', 'Animation: pull image layers, overlay filesystem, namespaces, cgroup limits, veth network, app starts as PID 1.', CN, CS, hid='ctr')

# animation 2: I/O virtualization emulated vs virtio vs SR-IOV
def io_frame(k):
    o = t(180, 12, ['Emulated device', 'Paravirtual device (virtio)', 'SR-IOV: hardware does it'][k], 9, 'ink', bold=True)
    o += box(10, 24, 90, 40, 'blue', rx=6) + t(55, 48, 'VM', 8.6, 'ink', bold=True)
    o += box(10, 112, 340, 34, 'card', rx=6) + t(180, 133, 'Physical network card (NIC)', 8.4, 'ink', bold=True)
    if k == 0:
        o += box(130, 24, 110, 40, 'amber', rx=6) + t(185, 41, 'hypervisor fakes', 7.6, 'ink', bold=True) + t(185, 55, 'an old e1000 card', 7, 'ink2')
        o += packet(100, 44, 130, 44, '') + packet(185, 64, 185, 112, '') + t(290, 50, 'many traps → slow', 8, 'red', bold=True)
    if k == 1:
        o += box(130, 24, 110, 40, 'amber', rx=6) + t(185, 41, 'virtio queue', 7.6, 'ink', bold=True) + t(185, 55, 'shared memory', 7, 'ink2')
        o += packet(100, 44, 130, 44, '') + packet(185, 64, 185, 112, '') + t(292, 50, 'few traps → fast', 8, 'green', bold=True)
    if k == 2:
        o += box(220, 70, 120, 30, 'green', rx=6) + t(280, 89, 'virtual function VF', 7.6, 'ink', bold=True)
        o += packet(100, 44, 240, 72, 'direct') + t(150, 34, 'hypervisor out of the data path', 7.6, 'green', bold=True)
    return o
IO = [('Emulated devices', 'The hypervisor pretends to be a real old network card; every operation traps.', 'Works with any OS, but slow — used only for compatibility'),
      ('Paravirtual (virtio)', 'Guest uses a “virtual-aware” driver that talks to the host through shared queues.', 'Standard in KVM/QEMU; AWS ENA and NVMe are similar ideas'),
      ('SR-IOV and hardware offload', 'The NIC itself splits into virtual functions; each VM gets one directly.', 'Near bare-metal speed; AWS Nitro cards take this further')]
IOA = anim_one('How it works', 'Hardware-assisted I/O: three ways a VM reaches the network', 'Why cloud VMs get 25–100 Gbps networking: the hardware does the virtualization.', 'I/O virtualization', 'Animation comparing an emulated network device, a paravirtual virtio device and SR-IOV with a virtual function assigned directly to the VM.', cap_frames([io_frame(k) for k in range(3)], IO), [x[0] + '.' for x in IO], delay=6000, hid='io')

parts = '\n  <h3>The three levels compared</h3>\n' + table(['', 'Hardware partition', 'VM (hypervisor)', 'Container (OS-level)'], [
    ['Own kernel', 'yes', 'yes', 'no — shares host kernel'], ['Different OS family', 'yes', 'yes (Windows + Linux)', 'no (Linux containers need a Linux kernel)'], ['Size', 'whole machine slice', 'GBs (Ubuntu cloud image 593 MB)', 'MBs (Alpine 3.5 MB)'],
    ['Start time', 'minutes', 'tens of seconds', 'milliseconds (our lab: 4 ms)'], ['Isolation', 'strongest', 'strong', 'good, weaker (shared kernel)'], ['Density per server', 'few', 'tens', 'hundreds']], minw=620)

DEEP = ('  <h3>The 8 Linux namespaces</h3>\n' + table(['Namespace', 'Isolates', 'Inside the container you see…'], [
    ['pid', 'process IDs', 'your app as PID 1, no host processes'], ['net', 'network stack', 'own interfaces, IP, routes, ports'], ['mnt', 'mount points', 'own root filesystem'], ['uts', 'hostname', 'own hostname (tiffingo-box)'],
    ['ipc', 'shared memory, queues', 'only your own IPC objects'], ['user', 'user and group IDs', 'root inside mapped to a normal user outside'], ['cgroup', 'cgroup tree view', 'only your own cgroup'], ['time', 'some clocks', 'own boot-time offsets']], minw=560) +
    '\n  <h3>Containers are not always Linux on Linux</h3>\n  <p>Docker Desktop on Windows and macOS runs a small Linux <b>VM</b> and starts containers inside it — a container still needs a Linux kernel. Windows containers need a Windows kernel. Services like AWS Fargate even run each task in its own micro-VM (Firecracker) to combine container speed with VM isolation.</p>\n'
    '  <h3>Security note</h3>\n  <p>Because containers share the host kernel, a kernel bug can let one container escape to the host. That is why multi-tenant clouds put containers of different customers in <b>separate VMs</b> or micro-VMs, and why you should run containers as a non-root user and drop capabilities.</p>')

clouds = vendor_tabs('<p><b>AWS:</b> VMs = EC2; containers = ECS, EKS (Kubernetes), Fargate (serverless containers on Firecracker micro-VMs); hardware: Nitro cards, ENA (SR-IOV-style), GPU instances.</p>',
    '<p><b>Azure:</b> VMs = Virtual Machines; containers = AKS, Container Apps, Container Instances; accelerated networking uses SR-IOV.</p>',
    '<p><b>Google Cloud:</b> VMs = Compute Engine; containers = GKE, Cloud Run (gVisor sandbox); gVNIC high-speed networking.</p>') + \
    cloud3([['Run a VM', 'EC2', 'Virtual Machines', 'Compute Engine'], ['Kubernetes', 'EKS', 'AKS', 'GKE'], ['Serverless containers', 'Fargate / App Runner', 'Container Apps / ACI', 'Cloud Run'], ['Fast networking', 'ENA, Nitro', 'Accelerated Networking (SR-IOV)', 'gVNIC']])
proof = [
    ('Step 1 · The namespaces a process lives in', code('bash', 'terminal', 'ls -l /proc/self/ns', sec('== 1)', '== 2)')), 'Each number is a namespace ID. Processes with the same IDs share that view.'),
    ('Step 2 · The host’s view', code('bash', 'terminal', 'ps -e --no-headers | wc -l; hostname', sec('== 2)', '== 3)')), '70 processes, hostname vm.'),
    ('Step 3 · A new PID, UTS and mount namespace', code('bash', 'terminal', "unshare --pid --uts --mount --fork --mount-proc \\\n  bash -c 'hostname tiffingo-box; hostname; ps -e -o pid,comm'", sec('== 3)', '== 4)')), 'Inside: bash is PID 1 and sees only 2 processes; the hostname is its own.'),
    ('Step 4 · The host is untouched', code('bash', 'terminal', 'hostname', sec('== 4)', '== 5)')), 'The UTS namespace kept the change inside.'),
    ('Step 5 · How fast?', code('bash', 'terminal', 'time unshare --pid --uts --mount --fork --mount-proc true', sec('== 5)')), 'No OS to boot — just new namespaces for a process.'),
    ('Step 6 · Alpine on Ubuntu: a container from scratch', code('bash', 'terminal', 'curl -O https://dl-cdn.alpinelinux.org/alpine/latest-stable/releases/x86_64/alpine-minirootfs-…tar.gz\nmkdir rootfs && tar -xzf alpine-minirootfs-*.tar.gz -C rootfs\nunshare --pid --uts --mount --fork --mount-proc=rootfs/proc chroot rootfs /bin/sh', secb('== 1)')), 'Different OS files (Alpine), different hostname, own PID 1 — but the same kernel 6.18 as the Ubuntu host. That is OS-level virtualization in one line.')]
prac = practical('Run these on any Linux machine, WSL2, or a cloud VM (as root or with sudo). Nothing to install except curl.', [
    ('1 · See your namespaces', code('bash', 'terminal', 'ls -l /proc/self/ns\nlsns | head'), 'lsns lists all namespaces on the machine (Docker containers show up here).'),
    ('2 · Your own hostname room', code('bash', 'terminal', "sudo unshare --uts bash -c 'hostname lab-room; hostname'\nhostname"), 'Changed inside, unchanged outside.'),
    ('3 · Your own process room', code('bash', 'terminal', "sudo unshare --pid --fork --mount-proc bash -c 'ps -e'"), 'Only bash (PID 1) and ps.'),
    ('4 · Your own network room', code('bash', 'terminal', 'sudo ip netns add room1\nsudo ip netns exec room1 ip -brief link\nsudo ip netns del room1'), 'Only a loopback interface, which is down: a brand-new network stack.'),
    ('5 · Limit memory with a cgroup (systemd)', code('bash', 'terminal', "sudo systemd-run --scope -p MemoryMax=50M python3 -c 'x = bytearray(200*1024*1024)'"), 'The process is killed (out of memory) because the cgroup allows only 50 MB — what docker --memory does. Needs a systemd + cgroup v2 system.')],
    cleanup='Namespaces vanish when their last process exits. Delete any rootfs folders you created.')
mist = mistakes([
    ['“Containers are tiny VMs.”', 'They look similar from outside.', 'Containers share the host kernel; VMs have their own. Different OS families need VMs.'],
    ['Running Linux containers directly on Windows and wondering how.', 'Docker Desktop hides a Linux VM.', 'Know that a Linux VM (WSL2/Hyper-V) runs underneath.'],
    ['Running containers as root with all capabilities.', 'Default images often use root.', 'Use a non-root USER, drop capabilities, read-only filesystem where possible.'],
    ['No memory limit on containers.', 'Default is unlimited.', 'Set --memory / Kubernetes limits so one container cannot starve the node.'],
    ['Expecting SR-IOV/GPU passthrough to allow live migration.', 'Directly assigned hardware is tied to one host.', 'Plan maintenance windows or use cloud-managed instances.']])
cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA Sessions 3–4', 'Types and uses of virtualization; containers (Session 10 Docker).'], ['AZ-900', 'Containers vs VMs (Azure Container Instances, AKS).'], ['AWS CLF-C02', 'Compute options: EC2 vs containers (ECS/EKS/Fargate) vs Lambda.']], minw=520) + '\n  <h3>Exam-style questions with explanations</h3>\n' + \
    qx('1. Which Linux features make containers possible?', ['RAID and LVM', 'namespaces and cgroups', 'DNS and DHCP', 'SSH and SFTP'], 1, 'Namespaces isolate what a process can see; cgroups limit what it can use.') + \
    qx('2. A container on an Ubuntu host reports the same kernel version as the host because…', ['it is a bug', 'containers share the host kernel', 'Docker copies the kernel', 'the VM is paused'], 1, 'OS-level virtualization isolates user space only; the kernel is shared (our lab: Alpine inside, kernel 6.18 on both).') + \
    qx('3. Which is an example of hardware-level partitioning?', ['Docker', 'IBM LPAR', 'VirtualBox', 'Kubernetes'], 1, 'LPARs are created by the machine’s firmware/hypervisor layer on IBM systems, each with its own OS.') + \
    qx('4. SR-IOV is used to…', ['encrypt disks', 'let VMs use a slice of a physical device directly for fast I/O', 'back up VMs', 'balance load across regions'], 1, 'The device exposes virtual functions assigned to VMs, bypassing the hypervisor in the data path.')
proj = miniproject('Mini project: build your own tiny container runtime in 15 lines of shell',
    'Write <code>minibox.sh</code> that runs any command inside an Alpine root filesystem with its own hostname, process tree, network and a memory limit — the core of Docker.',
    ['Download and unpack the Alpine minirootfs into <code>rootfs/</code> (proof step 6).',
     'Script line 1: <code>sudo systemd-run --scope -p MemoryMax=128M \\</code> (cgroup limit).',
     'Line 2: <code>unshare --pid --uts --mount --net --fork --mount-proc=rootfs/proc \\</code> (namespaces).',
     'Line 3: <code>chroot rootfs /bin/sh -c "hostname minibox; exec $*"</code> (own root filesystem).',
     'Run <code>./minibox.sh ps</code>, <code>./minibox.sh hostname</code>, <code>./minibox.sh ip link</code>, <code>./minibox.sh cat /etc/os-release</code>.',
     'Compare with <code>docker run --rm -it --memory 128m alpine sh</code> on a machine with Docker: same features, plus images, overlayfs and networking.'],
    'Output showing Alpine, hostname minibox, PID 1 = your command, only a loopback network.', 'Linux namespaces + cgroups + chroot (Linux course) + Docker course.')

assemble_v2(HERE, story_h2='Do we need a whole VM for a tiny menu API?', hook_html=hk,
    narration='TiffinGo’s new menu API is a 20 MB program. Giving it a full VM with its own operating system feels like renting a bus to carry one passenger.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Server, hardware and OS-level virtualization',
    formal='<b>Server virtualization</b> partitions a physical server into multiple isolated virtual servers. It can be implemented by <b>hardware-level partitioning</b> (firmware divides physical resources), <b>hypervisor-based virtualization</b> (each virtual machine runs its own guest OS on virtual hardware), or <b>OS-level virtualization</b> (the operating system kernel provides multiple isolated user-space instances — containers — using mechanisms such as Linux namespaces and cgroups). <b>Hardware virtualization</b> also denotes processor and device features (VT-x/AMD-V, SR-IOV) that support it.',
    simple='You can split a server with the hardware, with a hypervisor (VMs, each with its own OS), or inside the operating system itself (containers that share one kernel).',
    interview=['“Server virtualization splits one physical server into isolated virtual servers. It can be done at the hardware level with partitions like IBM LPARs, with a hypervisor that runs full VMs, or at the OS level with containers.”', '“OS-level virtualization uses Linux namespaces for isolation and cgroups for resource limits; containers share the host kernel, so they are megabytes in size and start in milliseconds.”', '“For example, I ran Alpine Linux inside an Ubuntu host with unshare and chroot: the OS files were Alpine but the kernel version was the host’s.”'],
    terms_rows=[('LPAR', 'Hardware/firmware partition of a big server.'), ('Container', 'Isolated processes sharing the host kernel.'), ('Namespace', 'Gives a process its own view (PID, net, mount…).'), ('cgroup', 'Limits CPU/memory for a group of processes.'), ('chroot', 'Changes a process’s root directory.'), ('overlayfs', 'Stacks image layers + a writable layer.'), ('SR-IOV', 'One device split into virtual functions for VMs.'), ('vGPU / MIG', 'One GPU shared by several VMs.')],
    exam='A favourite theory question: “Compare VMs and containers” — kernel (own vs shared), size (GB vs MB), start time (seconds/minutes vs milliseconds), isolation (stronger vs weaker), OS choice (any vs same kernel family).',
    picture_h2='Three levels, and how containers isolate', picture_html=picture,
    how_h2='What “docker run” really does', how_intro='The full sequence behind one command — namespaces, cgroups, overlay filesystem and network, step by step.', how_anim=CTR,
    parts_h2='The three levels compared', parts_html=parts,
    after_picture=[('types', 'Types, one by one', 'Seven types of server and hardware virtualization, one by one', build_types(IOA))], lv='',
    myth_rows=[('A container has its own kernel.', 'Same kernel version inside and outside.', 'Real proof step 6.'), ('Containers need Docker.', 'unshare + chroot + cgroups are enough.', 'Real proof steps 3–6.'), ('Hardware virtualization only means VT-x.', 'Also SR-IOV, vGPU, LPARs.', 'Parts.')],
    extra_secs=[('deep', 'Deep dive', 'Namespaces in detail, containers on Windows/macOS, and security', DEEP)],
    clouds_html=clouds, proof_h2='Real proof: containers by hand', proof_intro='All outputs are real, from our Ubuntu 24.04 lab machine on 10 Nov 2026 (util-linux unshare, Alpine 3.24.4 minirootfs).', proof_steps=proof,
    practical_html=PRAC, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Explain the three levels of server virtualization with examples.', 'Explain full, para- and hardware-assisted virtualization and how each handles privileged instructions.', 'Explain I/O (virtio, SR-IOV) and GPU (passthrough, vGPU, MIG) virtualization.', 'Do each practical step both in a UI and with the CLI.', 'Explain hardware virtualization features (VT-x, SR-IOV, vGPU).', 'Explain how containers use namespaces, cgroups, chroot and overlayfs.', 'Describe the six steps of docker run.', 'Build a minimal container with unshare and chroot.'],
    next_html='<a href="../03-network-storage-and-data-virtualization/">4.3 Network, storage and data virtualization</a>.',
    pre='<b>Before you start:</b> <a href="../01-virtualization-and-hypervisors/">4.1 Virtualization and hypervisors</a>.')
