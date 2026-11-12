"""Per-type text: internal working steps, differences from neighbouring types, where used, real-world example."""
from cloudkit import table

EXTRA = {
1: dict(
    how=[('The hypervisor takes the hardware', 'A Type 1 hypervisor (ESXi, KVM, Hyper-V, Nitro) boots first, directly on the server. With VT-x/AMD-V it runs in the CPU’s most privileged “root mode”, so nothing else can control the hardware.'),
         ('A VM is defined', 'An admin or an API call describes the VM: 2 vCPUs, 4 GB RAM, a 20 GB virtual disk (a file or a volume), one virtual network card. This is just a configuration record.'),
         ('Resources are reserved', 'The hypervisor sets aside memory, builds the VM’s memory map (EPT/NPT — see type 3), creates the virtual disk and connects the virtual NIC to a virtual switch.'),
         ('The guest boots', 'The VM starts from virtual firmware (BIOS/UEFI) and loads its own kernel — Windows or Linux — which believes it owns a real computer.'),
         ('Normal instructions run directly', 'Ordinary CPU instructions of the guest run straight on the physical CPU in “non-root mode” at almost full speed — no translation.'),
         ('Sensitive actions trap to the hypervisor', 'When the guest touches hardware (I/O, interrupts, special registers) the CPU performs a <b>VM exit</b>; the hypervisor handles it (often via fast virtio/ENA drivers) and returns with a <b>VM entry</b>.'),
         ('The scheduler shares the cores', 'vCPUs are scheduled on physical cores like threads; memory isolation (EPT) and device isolation (IOMMU) make sure no VM can read another’s data.')],
    diff=table(['', 'Server virtualization (VM)', 'OS-level (container)', 'Bare metal (no virtualization)'], [
        ['What is shared', 'hardware only', 'hardware + one kernel', 'nothing — one OS owns the box'], ['Own kernel?', 'yes', 'no', 'yes (only one)'],
        ['Different OSes on one box', 'yes (Windows + Linux)', 'no', 'no'], ['Start time', '30–60 s', 'milliseconds', 'minutes (hardware boot)'],
        ['Isolation', 'strong', 'good, weaker', 'total'], ['Typical use', 'general servers, clouds', 'microservices', 'big databases, HPC, licensing']], minw=600),
    where=['Every enterprise data centre (VMware, Hyper-V clusters)', 'Every IaaS cloud: EC2, Azure VMs, Compute Engine', 'Dev/test labs that need many short-lived servers', 'Running old OS versions for legacy apps', 'Disaster-recovery sites with replicated VMs'],
    realworld='Netflix runs its streaming services on Amazon EC2 — virtual servers on AWS — and adds or removes thousands of instances as viewing rises in the evening and falls at night. None of those servers is a physical machine Netflix owns; each is a VM carved out of an AWS host by the Nitro hypervisor.'),
2: dict(
    how=[('Get the image', 'The runtime pulls the image: a stack of read-only layers (base OS files + libraries + app) from a registry such as Docker Hub or Amazon ECR.'),
         ('Build the root filesystem', 'overlayfs stacks the layers and adds a thin writable layer. Ten containers can share one image on disk; each only stores its own changes.'),
         ('Create namespaces', 'The runtime calls the Linux <code>clone()</code>/<code>unshare()</code> system calls with flags for new PID, network, mount, UTS (hostname), IPC and user namespaces. The process will now see only its own processes, files, hostname and network.'),
         ('Apply cgroup limits', 'A control group is created with limits such as <code>cpu.max</code> (0.5 CPU) and <code>memory.max</code> (256 MB); the process is placed in it. If it exceeds memory the kernel kills only that container.'),
         ('Connect the network', 'A veth pair (virtual cable) links the container’s network namespace to a bridge on the host; a NAT rule maps host port 8080 to container port 80.'),
         ('Lock it down and start', 'Dangerous kernel capabilities are dropped and a seccomp filter blocks risky system calls; then the app is started as PID 1. Every system call it makes goes directly to the shared host kernel — there is no second OS.')],
    diff=table(['', 'Container (OS-level)', 'Virtual machine', 'Plain process (no isolation)'], [
        ['Isolation by', 'namespaces + cgroups', 'hypervisor + hardware', 'only user permissions'], ['Kernel', 'shared with host', 'its own', 'shared'],
        ['Own files / IP / hostname', 'yes', 'yes', 'no'], ['Size', 'MBs', 'GBs', '—'], ['Start time', 'ms', 'tens of seconds', 'ms'], ['Can run another OS family', 'no', 'yes', 'no']], minw=560),
    where=['Microservices and APIs (Kubernetes, ECS)', 'CI/CD build and test jobs', 'Same environment on laptop, test and production', 'Machine-learning model serving', 'Batch and data jobs (Spark on Kubernetes)'],
    realworld='Google has run its own services — Search, Gmail, YouTube — in containers for well over a decade on its internal cluster manager Borg, starting billions of containers every week. Kubernetes, now used by most large companies, grew out of that experience.'),
3: dict(
    how=[('Memory is promised, not given', 'When a VM with 4 GB starts, the hypervisor records the promise but usually allocates real RAM page by page, only when the guest first touches it.'),
         ('The guest builds its own page tables', 'Inside the VM, the guest OS maps each process’s virtual addresses to what it thinks are physical addresses: guest-virtual → <b>guest-physical</b>.'),
         ('The hypervisor builds a second table', 'For each VM the hypervisor keeps an <b>EPT</b> (Intel) or <b>NPT</b> (AMD) table: guest-physical → <b>host-physical</b> (real RAM frames).'),
         ('The CPU walks both tables', 'On every memory access the CPU’s MMU translates through both tables in hardware (a “two-dimensional walk”) and caches the result in the TLB, tagged per VM, so it stays fast.'),
         ('First touch causes a fault', 'If a guest-physical page has no real frame yet, the CPU raises an EPT violation; the hypervisor picks a free frame, fills the table and resumes the VM — invisible to the guest.'),
         ('Reclaiming memory', 'When RAM is tight the hypervisor (a) asks a <b>balloon driver</b> inside idle VMs to hand back unused pages, (b) <b>shares identical pages</b> (KSM / transparent page sharing) as one copy-on-write page, and (c) as a last resort swaps VM memory to disk.')],
    diff=table(['', 'Memory virtualization (hypervisor)', 'Virtual memory (inside any OS)', 'Storage thin provisioning'], [
        ['Who does it', 'hypervisor + CPU (EPT/NPT)', 'the operating system', 'storage layer'], ['Translates', 'guest-physical → host-physical', 'process-virtual → physical (+ swap)', 'virtual disk block → physical block'],
        ['Purpose', 'isolate and share RAM between VMs', 'give each process its own address space', 'allocate disk space only when written'], ['Exists without VMs?', 'no', 'yes, on every PC', 'yes']], minw=600),
    where=['Every hypervisor host (always on — it is how VMs are isolated)', 'Private clouds and VDI farms that overcommit memory', 'Hosts running many similar VMs (page sharing of identical OS pages)', 'Live migration (memory pages copied between hosts, Lesson 4.4)'],
    realworld='VDI farms running hundreds of identical Windows desktops on VMware or KVM rely on page sharing and ballooning to fit more desktops per host, because most desktops load the same OS files and are idle much of the day. Public clouds such as EC2 generally do not overcommit memory on standard instances, which is why a VM’s RAM performance there is predictable.'),
4: dict(
    how=[('Build a golden desktop', 'IT prepares one Windows image with Office, the CRM client and security agents (Lesson 4.4).'),
         ('Create a pool', 'Desktop VMs are cloned from it: <b>persistent</b> (one per user, kept) or <b>non-persistent</b> (shared pool, reset at logout). Multi-session hosts (Azure Virtual Desktop, RDS) let many users share one Windows server VM.'),
         ('User signs in', 'The client app or a browser contacts a <b>gateway</b> and <b>connection broker</b>; identity is checked (Active Directory / Entra ID / MFA).'),
         ('Broker assigns a desktop', 'It picks a free desktop, powers it on if needed, and gives the client a short-lived connection ticket.'),
         ('Display protocol streams the screen', 'RDP, HDX, PCoIP/Blast or DCV encodes only screen changes (often as compressed video) and sends them down; keystrokes, mouse, and optionally USB, printer and audio go up. Files stay in the data centre.'),
         ('Profile and logout', 'The user’s profile and documents are mounted from central storage at login (e.g. FSLogix containers); at logout a non-persistent desktop is reset to the clean image.')],
    diff=table(['', 'Desktop virtualization (VDI/DaaS)', 'Application virtualization', 'Remote access to my own PC (RDP/AnyDesk)'], [
        ['What is delivered', 'a whole desktop', 'one app window or package', 'one specific physical PC'], ['Where it runs', 'VMs/session hosts in DC or cloud', 'server, or sandbox on device', 'the user’s office PC'],
        ['Scale', 'hundreds to thousands of users', 'many users per server', 'one user'], ['Data on device', 'none', 'none (published) / some (packaged)', 'none, but PC must stay on'],
        ['Typical use', 'call centres, banks, contractors', 'one legacy or licensed app', 'occasional personal access']], minw=620),
    where=['Call centres and BPOs (customer data must not leave)', 'Banks, insurers, hospitals (compliance)', 'Contractors and temporary staff (instant on/off-boarding)', 'Work from home on personal devices', 'Training labs that reset after every class'],
    realworld='In the 2020 lockdowns many Indian BPOs and banks moved thousands of employees to work from home within days by giving them virtual desktops (Citrix, VMware Horizon, Amazon WorkSpaces, Azure Virtual Desktop) on their own or loaned laptops — customer data stayed in the data centre while employees worked from home.'),
5: dict(
    how=[('Packaging: capture the install', 'A packaging tool (MSIX Packaging Tool, App-V sequencer) watches the app being installed and records every file and registry key into one package.'),
         ('Packaging: a virtual layer at launch', 'When the user starts the app, a filter driver puts it in a “bubble”: its file and registry calls are redirected to the package’s virtual file system and registry.'),
         ('Packaging: merged view', 'The app sees the OS plus its own files, as if installed; other apps cannot see its files, so two Java versions never meet. Writes go to a per-user layer.'),
         ('Publishing: install once on a server', 'For streamed apps, the app is installed on a Windows session host (or WorkSpaces Applications fleet instance) in the data centre or cloud.'),
         ('Publishing: user clicks an icon', 'The broker starts a session on the server that runs only that app — no full desktop.'),
         ('Publishing: only the window travels', 'The app’s window is remoted (RemoteApp, HDX) and appears on the user’s device like a local window; files are saved to central storage.')],
    diff=table(['', 'Application virtualization', 'Desktop virtualization', 'Containers'], [
        ['Unit delivered', 'one end-user app', 'whole desktop', 'server-side app/service'], ['Who uses it', 'office users', 'office users', 'developers / ops'],
        ['Isolation', 'app bubble or remote session', 'whole VM / session', 'namespaces + cgroups'], ['OS', 'mostly Windows apps', 'Windows (sometimes Linux)', 'mostly Linux'],
        ['Main problem solved', 'conflicts, old apps, any device', 'central, secure desktops', 'packaging and scaling services']], minw=600),
    where=['Legacy business apps that do not run on new Windows', 'Conflicting versions on shared PCs (labs, banks)', 'Licensed software for students on their own laptops', 'Windows apps on Chromebooks, Macs, tablets', 'Quick rollout/rollback of an app to thousands of PCs'],
    realworld='Many universities stream licensed engineering and statistics software (CAD, MATLAB-type tools) to students’ own laptops with Amazon Amazon WorkSpaces Applications (formerly AppStream 2.0) or Citrix instead of installing it on every lab PC; the app runs in the cloud and the licence is controlled centrally.'),
6: dict(
    how=[('Desired state in a controller', 'The SDN controller / cloud control plane stores what you created by API: VPCs, subnets, route tables, security groups and where every VM lives.'),
         ('State pushed to every host', 'Each host’s virtual switch (Open vSwitch, VMware vSwitch, or the AWS Nitro card) receives only the rules and mappings for VMs it hosts.'),
         ('VM sends a frame', 'The VM’s vNIC hands an ordinary Ethernet frame to the virtual switch.'),
         ('Rules and route lookup', 'The virtual switch checks firewall rules (security groups), looks up the route, and asks “which physical host has this destination IP in this virtual network?”'),
         ('Encapsulate', 'It wraps the frame: outer Ethernet + IP (host → host) + UDP + a header with the 24-bit network ID (VXLAN VNI, UDP port 4789). AWS uses its own encapsulation on Nitro.'),
         ('Underlay delivers, remote host unwraps', 'Physical routers forward the outer packet. The receiving host removes the wrapper, checks the network ID and inbound rules, and delivers to the right VM.')],
    diff=table(['', 'VLAN', 'Overlay (VXLAN / VPC)', 'SDN', 'VPN'], [
        ['What it is', 'tag on Ethernet frames', 'packets wrapped and tunnelled over IP', 'central software control of the network', 'encrypted tunnel over an untrusted network'],
        ['Number of networks', '4,094', '≈16.7 million', 'n/a (control model)', 'per tunnel'], ['Spans', 'one layer-2 domain', 'any IP network', 'whole data centre', 'sites / users over internet'],
        ['Main job', 'separate departments', 'many tenants on shared hardware', 'program the network by API', 'secure connection between places']], minw=640),
    where=['Every cloud VPC/VNet', 'Multi-tenant private clouds (VMware NSX, OpenStack)', 'Kubernetes pod networking (CNIs)', 'Telecom 5G cores and firewalls as software (NFV)', 'Micro-segmentation for security inside data centres'],
    realworld='Every Amazon VPC is network virtualization: millions of customers create private networks, often with the very same 10.0.0.0/16 ranges, on shared AWS hardware, and their traffic never mixes. Telecom operators likewise run 5G core network functions as software on cloud infrastructure instead of dedicated boxes (NFV).'),
7: dict(
    how=[('Disks join a pool', 'Physical disks (local, SAN or on many servers) are registered with the storage layer: in LVM as physical volumes in a volume group; in Ceph/EBS-style systems spread across many storage nodes.'),
         ('A virtual volume is a map', 'Creating a 100 GB volume creates a mapping table: logical block → physical location. With thin provisioning nothing is allocated yet.'),
         ('The volume is presented', 'The host sees it as a normal block device (iSCSI, NVMe-over-Fabrics, virtio-blk; on AWS via the Nitro EBS card as NVMe).'),
         ('Write path', 'The VM writes block 5,000. The layer looks up the map, allocates space on first write, writes it to two or three replicas (or erasure-coded pieces) and only then acknowledges.'),
         ('Snapshots by copy-on-write', 'A snapshot freezes the map. New writes go to new blocks; the snapshot keeps pointing at the old ones. Next snapshot stores only changed blocks.'),
         ('Background work', 'The layer rebalances data when disks are added, moves hot data to SSD and cold to HDD (tiering), and rebuilds replicas when a disk fails — the VM never notices.')],
    diff=table(['', 'Storage virtualization', 'Data virtualization', 'RAID'], [
        ['Hides', 'which disks hold the blocks', 'where and in what format data lives', 'failure of a disk in one box'], ['Unit', 'blocks, files, objects', 'tables, views', 'blocks'],
        ['Pools across', 'many disks / servers / vendors', 'many systems (DB, files, SaaS)', 'disks in one controller'], ['Example', 'EBS, LVM, Ceph, vSAN', 'Athena federated, Denodo', 'RAID 1, 5, 10']], minw=560) +
        table(['Kind of virtual storage', 'You see', 'Cloud example'], [['Block', 'a raw disk to format', 'EBS, Azure Managed Disks, Persistent Disk'], ['File', 'a shared folder (NFS/SMB)', 'EFS, FSx, Azure Files, Filestore'], ['Object', 'buckets of objects over HTTP', 'S3, Blob Storage, Cloud Storage']], minw=520),
    where=['VM disks in every cloud (EBS) and data centre (SAN, vSAN)', 'Shared file systems for many servers', 'Backups and DR via snapshots and replication', 'Data lakes on object storage', 'Kubernetes persistent volumes'],
    realworld='CERN stores and serves physics data and the disks of its private-cloud VMs on Ceph, an open-source software-defined storage system that pools thousands of ordinary disks across many servers into virtual block devices, file systems and object stores.'),
8: dict(
    how=[('Connect the sources', 'Connectors are configured for each source: a CSV/Parquet location, a MySQL or Oracle database, a SaaS API.'),
         ('Build the catalog', 'The layer reads metadata — table names, columns, types, statistics — and shows everything as virtual tables, often with friendly business names.'),
         ('Parse and plan the query', 'A user’s SQL is parsed into a plan: which tables come from which source, and what can be done where.'),
         ('Push work down', 'Filters, column choices and even joins are translated into each source’s own language (SQL dialect, API call) so the source returns as little data as possible.'),
         ('Combine', 'Partial results are fetched in parallel, joined and aggregated in the engine’s memory; hot results may be cached.'),
         ('Secure and return', 'Masking (hide card numbers) and row-level rules are applied in one place, and one result set is returned to the dashboard or app.')],
    diff=table(['', 'Data virtualization', 'ETL + data warehouse', 'Data lake'], [
        ['Data copied?', 'no — read in place', 'yes, transformed and loaded', 'yes, raw files collected'], ['Freshness', 'live', 'as of last load', 'as of last ingest'],
        ['Speed on big joins', 'slower', 'fast', 'fast with columnar files'], ['Set-up time', 'hours–days', 'weeks', 'days–weeks'], ['Best for', 'quick integration, compliance, prototypes', 'heavy repeated reporting', 'large-scale analytics, ML']], minw=600),
    where=['Live dashboards across several systems', 'Regulatory reports where data must not be copied', 'Prototyping before building ETL pipelines', 'Querying data across clouds (BigQuery Omni)', 'Giving analysts one SQL view of scattered data'],
    realworld='Amazon Athena Federated Query lets one SQL statement join data in S3 with data in DynamoDB, RDS MySQL or other sources through Lambda-based connectors, without loading it anywhere first; similar features exist in Azure Synapse serverless SQL and BigQuery.'),
}

PLAIN_PRO = {
1: ('One powerful computer is divided into several smaller “pretend computers” (virtual machines). Each pretend computer has its own Windows or Linux and its own programs, and cannot see the others. A special program called the <b>hypervisor</b> does the dividing — like a building manager who decides which flat gets which rooms.',
    'The CPU itself admits it is virtual: run <code>grep -c hypervisor /proc/cpuinfo</code> and <code>lscpu | grep -i hypervisor</code> inside any cloud VM. Our lab VM showed the hypervisor flag and “Hypervisor vendor: KVM” — the same KVM family AWS Nitro is built on.'),
2: ('Instead of making many pretend computers, the operating system makes many <b>separate rooms</b> for programs. Each program gets its own files, its own name and its own network address, but all rooms share the same engine underneath (the kernel). That makes containers tiny and very fast to start.',
    'Linux has no “container” object at all. A container is just an ordinary process placed in namespaces and a cgroup — <code>ls -l /proc/&lt;pid&gt;/ns</code> shows it. Docker and Kubernetes are convenience layers over a handful of system calls (we built one by hand in Lesson 4.2).'),
3: ('Every virtual machine believes it has its own RAM starting from the first address. The hypervisor secretly keeps a list of which real memory chip area each VM is actually using, so VMs never write over each other — and it can lend unused memory from a sleeping VM to a busy one.',
    'With two levels of page tables, one TLB miss can cost up to 24 memory reads instead of 4 (a 4-level guest walk inside a 4-level host walk). That is why huge pages (2 MB / 1 GB) give VMs such a large speed-up, and why databases on VMs are tuned to use them.'),
4: ('Your computer screen shows a desktop that is really running on a big server somewhere else. Only the picture comes to you, and only your typing and clicks go back. So any cheap laptop can be used, and if it is lost, no company data is lost with it.',
    'Microsoft offers Windows 11 Enterprise <b>multi-session</b> — many users sharing one Windows client VM — only on Azure Virtual Desktop (and Azure Local). That one licensing fact often decides between one-VM-per-user VDI and much cheaper pooled desktops.'),
5: ('You use a program without installing it in the normal way. Either the program comes in its own sealed box with everything it needs (so it never disturbs other programs), or it runs on a server and only its window appears on your screen.',
    'MSIX app attach does not even copy the app to the PC: at sign-in the package is mounted as a virtual disk from a file share, so hundreds of session hosts share one copy and an app update is just swapping that disk.'),
6: ('Many private networks are created with software on top of one set of real cables. Each company or team gets its own network, with its own rules on who may talk to whom, and nobody has to plug in a single new cable.',
    'An AWS VPC has no broadcast: ARP requests never reach other instances — the Nitro card answers them from the mapping service. That is why on-premises failover tricks based on gratuitous ARP or floating IPs do not work in AWS and are replaced by moving ENIs or Elastic IPs by API.'),
7: ('All the hard disks are poured into one big common pool. When a computer needs space, it gets a “virtual disk” from the pool, which can grow later. It never knows — or cares — which real disk holds its files.',
    'An EBS volume created from a snapshot is loaded lazily from S3: the first read of each block is much slower. That is why database teams pre-read (“initialize”) restored volumes or pay for Fast Snapshot Restore before going live.'),
8: ('Data stays where it already lives — in files, databases and online apps. A smart layer lets you ask one question across all of them, as if they were one database, and fetches only what is needed at that moment. Nothing is copied.',
    'Pushdown is everything. If the engine cannot push your WHERE filter to the source, it may pull the whole table over the network first. Always read the plan (<code>EXPLAIN</code> in Trino/Athena/DuckDB) before blaming the network.'),
}
for k, (pl, pr) in PLAIN_PRO.items():
    EXTRA[k]['plain'] = pl; EXTRA[k]['pro'] = pr

WORDS = {
1: [('CPU / core', 'the worker chip that runs instructions'), ('vCPU', 'a share of a real CPU core given to a VM'), ('kernel', 'the core part of an operating system that talks to hardware'), ('VT-x / AMD-V', 'features built into Intel/AMD chips to help hypervisors'), ('VM exit / entry', 'the CPU pausing the VM to let the hypervisor act, then resuming it'), ('virtio / ENA', 'fast “virtual-aware” drivers for disk and network'), ('IOMMU', 'a hardware guard so devices touch only their own VM’s memory')],
2: [('image', 'a ready-made package of files for a container'), ('registry', 'an online store of images (Docker Hub, ECR)'), ('overlayfs', 'stacks read-only image layers with one writable layer'), ('namespace', 'gives a process its own private view (processes, network, files, name)'), ('cgroup', 'a limit on how much CPU/memory a group of processes may use'), ('veth / bridge', 'a virtual cable / virtual switch'), ('PID 1', 'the first process in a container')],
3: [('RAM', 'fast working memory, emptied when power goes off'), ('page', 'a small 4 KB block of memory'), ('page table', 'a list mapping one kind of address to another'), ('EPT / NPT', 'the hypervisor’s extra page table, used by Intel/AMD chips'), ('MMU / TLB', 'the chip part that translates addresses / its small fast cache'), ('balloon driver', 'a helper inside the VM that hands back unused memory'), ('KSM / page sharing', 'keeping one copy of identical memory pages')],
4: [('golden image', 'a master copy of a perfectly set-up desktop'), ('persistent / non-persistent', 'desktop kept per user / reset after every logout'), ('connection broker', 'the service that decides which desktop you get'), ('gateway', 'the secure front door from the internet'), ('display protocol (RDP, HDX, PCoIP, DCV)', 'the method that sends screen pictures and receives clicks'), ('profile', 'your settings and documents, stored centrally')],
5: [('package', 'one file holding the app with all its files and settings'), ('registry', 'Windows’ settings database'), ('filter driver', 'a small piece of Windows that redirects an app’s file and settings requests'), ('session host', 'a Windows server where many users run apps'), ('published / RemoteApp', 'only the app window is shown on your device')],
6: [('vNIC', 'a virtual network card'), ('virtual switch', 'software that passes traffic between VMs'), ('security group', 'a virtual firewall: a list of allowed traffic'), ('route table', 'a list that says where traffic for each address range goes'), ('encapsulation', 'putting a packet inside another packet, like a letter in a courier envelope'), ('VXLAN / VNI', 'a common wrapping method / the network ID written on the envelope'), ('underlay', 'the real physical network underneath')],
7: [('block', 'a small fixed-size piece of a disk'), ('physical volume / volume group', 'a real disk / a pool made of real disks (LVM words)'), ('iSCSI, NVMe-oF', 'ways to reach a disk over a network'), ('replica', 'an extra copy kept for safety'), ('erasure coding', 'splitting data with extra recovery pieces, cheaper than full copies'), ('tiering', 'keeping busy data on fast disks and old data on cheap disks')],
8: [('source', 'any place data lives: a file, a database, an app'), ('connector', 'a plug-in that knows how to talk to one kind of source'), ('catalog', 'the list of all tables and columns and where they are'), ('query plan', 'the step-by-step recipe the engine makes for your question'), ('pushdown', 'sending filters to the source so it returns less data'), ('masking', 'hiding sensitive values such as card numbers')],
}
for k, w in WORDS.items():
    EXTRA[k]['words'] = w
