"""Lesson 4.4 — provisioning methods and migration types, one by one."""
from cloudkit import *

def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)

def mapfig():
    o = t(320, 16, 'Provisioning methods and migration types', 11, 'ink', bold=True)
    cols = [('Provisioning: creating VMs', 'green', [('1', 'Manual install', 'ISO → install → configure'), ('2', 'Template / clone', 'full or linked copy'), ('3', 'Golden image + cloud-init', 'bake once, personalize at boot'), ('4', 'IaC + Auto Scaling', 'code creates, scaling repeats')]),
            ('Migration: moving VMs', 'violet', [('5', 'Cold migration', 'switched off, files copied'), ('6', 'Live migration', 'running, ms pause'), ('7', 'Storage migration', 'disk moves, VM stays'), ('8', 'P2V / V2V', 'physical→VM, VMware→KVM'), ('9', 'Cloud migration (rehost)', 'replicate, test, cut over')])]
    for c, (h, tn, items) in enumerate(cols):
        x = 20 + c * 310
        o += box(x, 30, 290, 26, tn, rx=6) + t(x + 145, 47, h, 8.8, 'ink', bold=True)
        for i, (n, a, b) in enumerate(items):
            y = 62 + i * 44
            o += box(x, y, 290, 38, 'card', rx=6) + pin(x + 14, y + 19, n) + t(x + 30, y + 17, a, 8.4, 'ink', anchor='start', bold=True) + t(x + 30, y + 31, b, 7, 'ink2', anchor='start')
    o += t(320, 296, 'Faster provisioning = less manual work per VM. Less downtime in migration = more data copied while the VM keeps running.', 7.4, 'ink2')
    return o
MAP = bigfig('Map: provisioning methods 1 manual install, 2 template/clone, 3 golden image + cloud-init, 4 infrastructure as code + Auto Scaling; migration types 5 cold, 6 live, 7 storage, 8 P2V/V2V, 9 cloud migration (rehost).', mapfig(), h=306)

# ---------------- 1 manual
def a_man(k):
    o = t(180, 12, ['Boot from the installer ISO', 'Install packages by hand', 'Configure by hand — server 2 differs'][k], 9, 'ink', bold=True)
    steps = ['boot ISO', 'partition disk', 'install OS', 'apt install nginx', 'copy app', 'edit configs']
    for i, s in enumerate(steps):
        on = (k == 0 and i < 3) or (k == 1 and i < 5) or k == 2
        o += box(14 + (i % 3) * 112, 30 + (i // 3) * 40, 104, 32, 'blue' if on else 'card', rx=4) + t(66 + (i % 3) * 112, 50 + (i // 3) * 40, s, 7.4, 'ink', bold=True)
    o += t(180, 128, ['≈ 30 min so far', '≈ 1.5 hours so far', '≈ 3 hours per server · server 2 has a different nginx version ⚠'][k], 7.8, 'red' if k == 2 else 'ink', bold=True)
    return o
A_MAN = cap([a_man(k) for k in range(3)], [('Boot the installer', 'Attach the OS ISO, click through the installer, partition the disk.', 'Every server repeats this.'), ('Install packages', 'Log in, install nginx, runtime and agents, copy the app.', 'Each command typed by a person.'), ('Configure by hand', 'Edit config files, open ports, create users. Server 2, built next week,', 'gets a newer package version — “configuration drift”.')],
    'Manual provisioning', 'Why nobody builds cloud servers this way.', 'Manual install', 'Animation: boot ISO, partition, install OS, install packages, copy app, edit configs — three hours per server with drift between servers.', 'p1anim')
T1 = vtype(1, 'Manual provisioning', 'green',
    '<b>Manual provisioning</b> is creating a server by installing the operating system from installation media and then installing and configuring software step by step by hand.',
    'Cooking every tiffin from scratch, separately, each morning: possible for one or two, impossible for two hundred — and no two taste exactly the same.',
    'Before virtualization, TiffinGo’s first server took a whole afternoon: install Ubuntu, install nginx, copy the app, edit configs. A second server built a month later behaved differently because package versions had changed.',
    'Any OS installer (Ubuntu, Windows Server); VirtualBox/VMware “install from ISO”. In the cloud you never install an OS by hand — every instance starts from an image.',
    '', A_MAN,
    'learning how an OS installs, or a one-off lab machine.',
    'anything you need twice — drift, slowness and human error make manual builds the main cause of “works on server 1, fails on server 2”.',
    plain='Someone sits at the computer, installs the operating system from a disc or USB, then installs every program and changes every setting by hand.',
    how=[('Attach installer media', 'Boot the (virtual) machine from an ISO image.'), ('Install the OS', 'Choose language, disk layout, users; wait for files to copy.'), ('Patch', 'Download and install updates.'), ('Install software', 'nginx, runtime, monitoring agent, the app.'), ('Configure', 'Edit config files, firewall, users, services.'), ('Document (hopefully)', 'Write down what was done — often skipped, so nobody can rebuild it exactly.')],
    words=[('ISO', 'a file containing an installation disc'), ('configuration drift', 'servers that should be identical slowly becoming different'), ('snowflake server', 'a unique hand-built server nobody can rebuild exactly')],
    diff=table(['', 'Manual', 'Template/clone', 'Golden image + cloud-init', 'IaC + Auto Scaling'], [['Time per server', 'hours', 'minutes', 'seconds–minutes', 'automatic'], ['Identical servers?', 'no (drift)', 'yes at clone time', 'yes', 'yes'], ['Repeatable by code?', 'no', 'partly', 'yes', 'fully']], minw=620),
    where=['Learning labs', 'Very old systems without images', 'Bare-metal appliances installed once'],
    realworld='Operations teams call hand-built servers “snowflakes” — each unique and impossible to recreate exactly; the move to images and infrastructure as code across the industry was largely a reaction to outages caused by such drift.',
    pro='Even a perfect manual runbook drifts, because package repositories change daily. Pinning versions in an image (type 3) is what makes a build reproducible, not the care of the person typing.')

# ---------------- 2 template / clone
def a_clone(k):
    o = t(180, 12, ['A prepared VM becomes a template', 'Full clone: copy every block', 'Linked clone: share the base, store changes'][k], 9, 'ink', bold=True)
    o += box(14, 30, 110, 60, 'amber', rx=6) + t(69, 52, 'template', 8.4, 'ink', bold=True) + t(69, 68, 'Ubuntu + nginx', 7, 'ink2') + t(69, 82, '20 GB', 7, 'ink2')
    if k == 1:
        for i in range(2):
            o += box(200 + i * 80, 30, 70, 60, 'blue', rx=6) + t(235 + i * 80, 56, f'VM {i + 1}', 8, 'ink', bold=True) + t(235 + i * 80, 72, '20 GB copy', 6.8, 'ink2')
        o += packet(124, 60, 200, 60, 'copy all') + t(180, 120, 'independent, but slow and uses full space each', 7.6, 'ink', bold=True)
    if k == 2:
        for i in range(3):
            o += box(176 + i * 60, 30, 54, 60, 'green', rx=6) + t(203 + i * 60, 56, f'VM {i + 1}', 8, 'ink', bold=True) + t(203 + i * 60, 72, '193 KB', 6.8, 'ink2')
            o += f'<path d="M{203 + i * 60},90 L69,90" style="stroke:#999;stroke-width:1;stroke-dasharray:3 3"/>'
        o += t(180, 120, 'our lab: 3 clones of a 20 GiB image in 33 ms', 7.6, 'green', bold=True)
    if k == 0:
        o += t(250, 60, 'locked: cannot be started,', 7.4, 'ink') + t(250, 74, 'only copied', 7.4, 'ink')
    return o
A_CLONE = cap([a_clone(k) for k in range(3)], [('Make a template', 'One VM is installed and configured carefully, then converted to a template', '— a read-only master that cannot run, only be copied.'), ('Full clone', 'Every block of the template disk is copied. The new VM is fully', 'independent but takes time and the full disk space.'), ('Linked clone', 'The new VM’s disk only stores its own changes and reads the rest from', 'the template — instant and tiny (copy-on-write).')],
    'Templates and clones', 'Copy a ready VM instead of installing again.', 'Template / clone', 'Animation: a prepared VM becomes a template; a full clone copies all 20 GB; linked clones share the template and store only changes, 193 KB each.', 'p2anim')
T2 = vtype(2, 'Template-based provisioning (full and linked clones)', 'green',
    '<b>Template-based provisioning</b> creates new VMs by copying a prepared master VM (a template). A <b>full clone</b> copies the entire disk and is independent; a <b>linked clone</b> shares the template’s disk and stores only its own changes using copy-on-write.',
    'A photocopier with a master sheet: you fill in the master once and copy it. A full photocopy is your own sheet; a “linked” copy is a transparent overlay on the master where you only write your changes.',
    'TiffinGo’s training team needs 30 identical lab VMs every Monday. Linked clones of one template are created in seconds and use almost no space; on Friday they are deleted and the template stays clean.',
    'VMware vSphere templates and Instant Clones, VirtualBox Clone (Full / Linked), Proxmox templates, Hyper-V differencing disks, qcow2 backing files (our lab).',
    '', A_CLONE,
    'on-premises virtualization, labs, VDI pools, test environments.',
    'linked clones depend on the base — delete or corrupt the template and every linked clone breaks; also changes to the template do not flow into existing clones.',
    plain='Instead of installing a new computer from scratch, you copy a ready one. A full copy is independent; a linked copy shares the original and saves only what is different.',
    how=[('Prepare a master VM', 'Install OS, patches and software; generalize it (e.g. Sysprep on Windows, clear machine IDs on Linux).'), ('Convert to template', 'Mark it read-only so nobody runs or changes it by mistake.'), ('Full clone', 'Copy all disk blocks to a new disk file; attach to a new VM definition.'), ('Linked clone', 'Create a small new disk whose “backing file” is the template disk; reads of unchanged blocks go to the template.'), ('Customize', 'Give the clone a new name, IP and unique IDs (guest customization).'), ('Start', 'The new VM boots in seconds.')],
    words=[('template', 'a read-only master VM used only for copying'), ('Sysprep', 'Windows tool that removes unique IDs before cloning'), ('backing file', 'the base disk a linked clone reads from'), ('copy-on-write', 'copy a block only when it is first changed')],
    diff=table(['', 'Full clone', 'Linked clone', 'Golden image (cloud)'], [['Disk space', 'full size', 'only changes', 'only changes (snapshot-based)'], ['Speed', 'minutes', 'seconds', 'seconds–minutes'], ['Depends on base?', 'no', 'yes', 'yes (snapshot), managed by cloud']], minw=540),
    where=['VMware and Hyper-V data centres', 'Training labs and VDI pools', 'Dev/test environments'],
    realworld='Non-persistent VDI pools in banks and call centres are built from linked or instant clones of one golden desktop, so hundreds of desktops share one base image and are reset at logoff.',
    pro='Long chains of linked clones/snapshots slow down reads, because each block lookup may walk several backing files. Consolidate (flatten) chains periodically — <code>qemu-img rebase</code> / <code>qemu-img commit</code> or VMware “consolidate”.')

# ---------------- 3 golden image (GOLD anim)
def T3(GOLD):
    return vtype(3, 'Golden image + cloud-init (image-based provisioning)', 'green',
        '<b>Image-based provisioning</b> launches VMs from a tested, versioned <b>golden image</b> (such as an AMI) that already contains the OS and software, and applies the last per-instance settings at first boot with an initialization tool such as <b>cloud-init</b> using user data.',
        'A ready-to-heat meal kit: the kitchen prepares 200 identical kits (bake), and each customer adds their own spice at home (fry). Fast, identical, still personal.',
        'For Diwali, TiffinGo bakes <code>tiffingo-menu-v1</code> once (AL2023 + nginx + app) and launches 20 instances from it; cloud-init sets each hostname and fetches config from Parameter Store at boot.',
        'AWS AMIs + EC2 Image Builder + user data; Azure Compute Gallery + Azure Image Builder + custom data; Google custom/machine images + startup scripts; HashiCorp Packer; cloud-init in all major Linux cloud images.',
        '', GOLD,
        'servers must be identical, fast to launch and rebuilt often — the normal cloud case.',
        'secrets or environment-specific values are baked into the image — fetch them at boot instead.',
        plain='You prepare one perfect copy of a server once, save it as an “image”, and start every new server from it. A small script runs at first start-up to give each server its own name and settings.',
        how=[('Start from a base image', 'Vendor OS image (Amazon Linux 2023, Ubuntu 24.04).'), ('Bake', 'A builder instance installs software and patches; tests run.'), ('Capture', 'The disk is snapshotted and registered as an AMI with a version name.'), ('Distribute', 'Copy the image to other Regions/accounts if needed.'), ('Launch', 'Instances start from the image; root volumes are created from its snapshot (lazily loaded).'), ('cloud-init personalizes', 'At first boot cloud-init reads user data and metadata: hostname, SSH keys, packages, scripts.')],
        words=[('AMI', 'Amazon Machine Image: what an EC2 instance boots from'), ('bake / fry', 'put it in the image / do it at boot'), ('cloud-init', 'first-boot setup program in cloud Linux images'), ('user data', 'a script or settings you pass at launch'), ('metadata', 'facts about the instance (ID, IP, Region) it can read')],
        diff=table(['', 'Golden image', 'Template (on-prem)', 'Configure at boot only'], [['Software installed', 'before launch', 'before cloning', 'during boot (slow)'], ['Boot time', 'fast', 'fast', 'slow, can fail mid-way'], ['Versioned and portable', 'yes (AMI IDs, Regions)', 'per vCenter', 'script versioned']], minw=520),
        where=['Every Auto Scaling group', 'Immutable infrastructure (replace, never patch in place)', 'Golden AMI pipelines in regulated companies', 'Kubernetes node images'],
        realworld='Large AWS users commonly run “golden AMI pipelines” with EC2 Image Builder or Packer that rebuild and test images every week with the latest patches, then roll them out by replacing instances rather than patching them in place.',
        pro='AMIs are lazily hydrated: a new root volume fetches blocks from S3 on first read. That is why the first minute of a fresh instance can show slow disk I/O, and why databases use Fast Snapshot Restore or pre-warm volumes.')

# ---------------- 4 IaC + autoscaling
def a_iac(k):
    o = t(180, 12, ['Describe servers in a file', 'plan → apply creates them', 'Auto Scaling keeps the count'][k], 9, 'ink', bold=True)
    o += box(10, 28, 150, 94, 'card', rx=6) + t(85, 44, 'main.tf', 8, 'ink', bold=True)
    for i, l in enumerate(['launch_template = menu-v1', 'min = 2, max = 20', 'desired = 2', 'scale on CPU > 60%']):
        o += t(18, 62 + i * 14, l, 6.8, 'ink', anchor='start')
    if k >= 1:
        o += packet(160, 74, 200, 74, 'apply')
        n = 2 if k == 1 else 6
        for i in range(n):
            o += box(204 + (i % 3) * 50, 32 + (i // 3) * 44, 44, 36, 'blue', rx=4) + t(226 + (i % 3) * 50, 54 + (i // 3) * 44, 'VM', 7.4, 'ink', bold=True)
    if k == 2:
        o += t(180, 140, 'traffic up → 6 VMs · one dies → replaced automatically', 7.6, 'green', bold=True)
    return o
A_IAC = cap([a_iac(k) for k in range(3)], [('Describe servers as code', 'A Terraform/CloudFormation file declares the launch template, minimum,', 'maximum and scaling rule — reviewed like any code.'), ('plan → apply', 'The tool compares the file with what exists and creates what is missing:', 'an Auto Scaling group with 2 instances.'), ('The group keeps the count', 'High CPU → it adds instances; an unhealthy instance → it is replaced.', 'Nobody provisions by hand any more.')],
    'IaC + Auto Scaling', 'Provisioning with no human in the loop.', 'Infrastructure as code', 'Animation: a Terraform file describing a launch template and scaling limits; apply creates two VMs; Auto Scaling grows to six and replaces failed VMs.', 'p4anim')
T4 = vtype(4, 'Infrastructure as code + Auto Scaling', 'green',
    '<b>Infrastructure as code (IaC)</b> defines servers, networks and their settings in declarative files that a tool applies through cloud APIs; combined with <b>Auto Scaling</b>, the platform automatically provisions, replaces and removes VMs to keep a desired count or follow load.',
    'A standing order with the dairy: you write once “2 litres every day, 4 on festival days” and the milk simply arrives — no daily phone call, and a spoiled packet is replaced automatically.',
    'TiffinGo keeps 2 menu servers normally; on Diwali evening CPU rises above 60% and the Auto Scaling group grows to 6, then shrinks after midnight. The whole setup lives in a Git repository and is reviewed like code.',
    'Terraform/OpenTofu, AWS CloudFormation and CDK, Azure Bicep/ARM, Pulumi, Ansible (configuration); scaling: EC2 Auto Scaling, Azure VM Scale Sets, Google managed instance groups.',
    '', A_IAC,
    'you run more than a handful of servers, environments must be identical (dev/test/prod), or load changes.',
    'people still change resources by hand in the console — the code and reality drift apart; scaling rules without cool-downs can flap.',
    plain='You write down, in a file, what servers you want and how many. A tool reads the file and creates them. Another service then watches the load and adds or removes servers by itself.',
    how=[('Write the desired state', 'A file lists the launch template (image, type, network) and the Auto Scaling group: min, max, desired, scaling policy.'), ('Plan', 'The tool reads current cloud state and shows the difference.'), ('Apply', 'It calls cloud APIs to create what is missing, in dependency order.'), ('Scale', 'CloudWatch metrics (CPU, requests) trigger the group to change the desired count.'), ('Heal', 'Health checks fail → the instance is terminated and a new one launched.'), ('Change by commit', 'A new image version = change one line, apply, instance refresh rolls servers.')],
    words=[('declarative', 'you say what you want, not each step'), ('Terraform plan / apply', 'preview changes / make them'), ('Auto Scaling group', 'a managed set of identical instances'), ('instance refresh', 'replace instances gradually with a new version'), ('drift', 'real resources differing from the code')],
    diff=table(['', 'IaC + Auto Scaling', 'Golden image alone', 'Manual console clicks'], [['Who launches', 'the platform', 'a person or script', 'a person'], ['Reacts to load', 'yes', 'no', 'no'], ['Reviewable history', 'Git', 'image versions', 'none']], minw=520),
    where=['Web and API tiers', 'Batch fleets', 'Multi-environment setups (dev/test/prod)', 'Disaster-recovery environments created on demand'],
    realworld='Netflix popularized “immutable infrastructure” on AWS: services are deployed by baking a new AMI and replacing the instances in Auto Scaling groups, rather than logging in and changing running servers.',
    pro='Target tracking scaling (e.g. “keep average CPU at 50%”) is usually better than step rules: the group computes the capacity itself and avoids the scale-in/scale-out flapping that hand-tuned thresholds cause.')

# ---------------- 5 cold
def a_cold(k):
    o = t(180, 12, ['Shut the VM down', 'Copy (and convert) its files', 'Start it on the new host'][k], 9, 'ink', bold=True)
    o += box(10, 30, 130, 90, 'card', rx=6) + t(75, 46, 'Host A', 8, 'ink', bold=True)
    o += box(220, 30, 130, 90, 'card', rx=6) + t(285, 46, 'Host B', 8, 'ink', bold=True)
    o += box(24, 56, 102, 50, 'red' if k == 0 else ('card' if k == 2 else 'red'), rx=5) + t(75, 78, 'VM', 8, 'ink', bold=True) + t(75, 94, 'powered off' if k < 2 else 'deleted', 7, 'ink2')
    if k == 1:
        o += packet(126, 80, 234, 80, 'disk files') + t(180, 140, 'downtime = copy time (GBs → minutes or hours)', 7.6, 'red', bold=True)
    if k == 2:
        o += box(234, 56, 102, 50, 'green', rx=5) + t(285, 78, 'VM', 8, 'ink', bold=True) + t(285, 94, 'running', 7, 'ink2') + t(180, 140, 'simple, works between any hypervisors', 7.6, 'green', bold=True)
    return o
A_COLD = cap([a_cold(k) for k in range(3)], [('Shut it down', 'The VM is powered off in a maintenance window — users see downtime.', 'Nothing in memory needs moving.'), ('Copy the files', 'Disk and configuration files are copied (and converted if the target', 'is a different hypervisor, e.g. qcow2 → vmdk).'), ('Start on the new host', 'The VM boots on host B. Simple and reliable — the cost is downtime', 'equal to the copy time.')],
    'Cold migration in action', 'The simplest way to move a VM.', 'Cold migration', 'Animation: VM powered off on host A; disk files copied to host B; VM started on host B.', 'm5anim')
T5 = vtype(5, 'Cold migration', 'violet',
    '<b>Cold migration</b> moves a virtual machine that is <b>powered off</b>: its disk and configuration files are copied (and converted if needed) to another host, datastore or platform, and the VM is started there.',
    'Moving house on a holiday: the shop is closed, everything is packed, moved and unpacked. Simple and safe, but customers cannot come that day.',
    'TiffinGo moves its old HR VM from an ageing host to a new one on a Sunday morning: shut down, copy 80 GB, start. Downtime: 25 minutes. Nobody noticed because HR does not work on Sundays.',
    'VMware cold migration, Hyper-V export/import, VirtualBox export/import appliance (OVA), qemu-img convert; AWS: a stop/start moves an EBS-backed instance to new hardware; VM Import/Export.',
    '', A_COLD,
    'downtime is acceptable, hosts have no shared storage, or the target is a different hypervisor.',
    'the service must stay up — use live migration or replication-based migration.',
    plain='Turn the virtual machine off, copy its files to the new place, and turn it on again there.',
    how=[('Plan a window', 'Agree a time when downtime is acceptable.'), ('Shut down cleanly', 'Stop the guest OS so the disk is consistent.'), ('Copy files', 'Disk images and VM config move to the new host or storage.'), ('Convert if needed', 'Change disk format (qcow2 ↔ vmdk ↔ vhdx) and drivers for a new hypervisor.'), ('Register and start', 'Create/import the VM on the target and boot it.'), ('Verify, then delete the source', 'Keep the old copy until the new one is proven.')],
    words=[('maintenance window', 'an agreed time when downtime is allowed'), ('datastore', 'where a hypervisor keeps VM files'), ('OVA / OVF', 'a package format for exporting VMs')],
    diff=table(['', 'Cold', 'Live', 'Storage migration'], [['VM running?', 'no', 'yes', 'yes'], ['What moves', 'disk + config', 'memory + CPU state (disk shared)', 'disk only'], ['Downtime', 'minutes–hours', 'milliseconds', 'none'], ['Needs', 'nothing special', 'compatible CPUs, fast link, shared storage', 'storage-aware hypervisor']], minw=560),
    where=['Moving between different hypervisors', 'Hosts without shared storage', 'Planned weekend moves of non-critical VMs'],
    realworld='On AWS, when a scheduled event warns that an instance’s hardware will be retired, stopping and starting an EBS-backed instance is a cold migration: AWS starts it on different, healthy hardware.',
    pro='A stop/start on EC2 changes the public IPv4 address (unless you use an Elastic IP) and wipes instance-store disks — a cold migration has side effects beyond downtime.')

# ---------------- 6 live (LIVE anim is in the how section)
T6 = vtype(6, 'Live migration', 'violet',
    '<b>Live migration</b> moves a <b>running</b> virtual machine — its memory, CPU and device state — from one physical host to another with only a brief pause, typically by iteratively pre-copying memory while the VM runs and then pausing it to transfer the last changed pages; network connections and the guest OS continue without reboot.',
    'Shifting a running stall from one corner of a fair to another while still serving customers: helpers copy the stock across in rounds; for the final few seconds the stall-keeper pauses, hands over the last items, and continues at the new spot.',
    'The host under TiffinGo’s orders database needs a hardware repair. The hypervisor live-migrates the database VM to another host; orders keep flowing, with a pause of a few tens of milliseconds that customers never notice.',
    'VMware vMotion, Hyper-V Live Migration, KVM/libvirt (virsh migrate --live), Xen; cloud: Google Compute Engine live-migrates VMs for host maintenance; Azure uses live migration and memory-preserving updates.',
    '', '',
    'host maintenance, load balancing across hosts, evacuating a failing host — when downtime is not acceptable.',
    'VMs with passthrough devices (GPU, SR-IOV), or very write-heavy VMs whose dirty pages outrun the network.',
    deep='<b>See it page by page</b> in the six-step live-migration animation in the next section; the deep dive explains what moves and why it may not converge.',
    plain='A running virtual machine is moved to another physical computer without switching it off. Its memory is copied over while it keeps working; it pauses for a blink at the end and then continues on the new computer.',
    how=[('Check the target', 'Compatible CPU features, enough RAM, same networks; disk on shared storage (or move it first).'), ('Pre-copy round 1', 'All memory pages are sent while the VM runs; the hypervisor tracks pages the VM changes (dirty pages).'), ('More rounds', 'Only dirty pages are sent each round; the set shrinks.'), ('Stop-and-copy', 'The VM is paused for milliseconds; the last dirty pages, CPU registers and device state are sent.'), ('Move the network identity', 'Switches/SDN learn the new location (gratuitous ARP or mapping update).'), ('Resume', 'The VM continues on the new host; the old host frees its memory.')],
    words=[('dirty page', 'a memory page changed since it was copied'), ('pre-copy / post-copy', 'copy memory before / after switching hosts'), ('converge', 'the remaining dirty set becomes small enough to finish'), ('gratuitous ARP', 'a broadcast saying “this IP is now here”')],
    diff=table(['', 'Pre-copy (default)', 'Post-copy'], [['Switch hosts', 'after memory is copied', 'immediately'], ['Missing pages', 'none', 'fetched on demand over the network'], ['Risk', 'may never converge for busy VMs', 'if the link fails mid-way, the VM is lost'], ['Use', 'almost everywhere', 'very busy VMs (QEMU/KVM supports it)']], minw=520),
    where=['Host patching and hardware repair', 'Balancing load across a cluster (VMware DRS)', 'Evacuating hosts before failure', 'Cloud host maintenance (GCE)'],
    realworld='Google Compute Engine uses live migration by default to keep VMs running during host maintenance, security patching and even some hardware failures, moving them to another host transparently.',
    pro='When memory is dirtied faster than the link can send it, KVM’s “auto-converge” deliberately slows the guest’s vCPUs until the copy catches up — the VM gets slower so the migration can finish.')

# ---------------- 7 storage migration
def a_stor(k):
    o = t(180, 12, ['VM running on old storage', 'Copy blocks while it runs', 'Switch to the new storage'][k], 9, 'ink', bold=True)
    o += box(140, 26, 80, 40, 'green', rx=6) + t(180, 50, 'VM (running)', 7.6, 'ink', bold=True)
    o += cyl(30, 90, 90, 44, 'old array', 'amber' if k < 2 else 'card') + cyl(240, 90, 90, 44, 'new array', 'green' if k >= 1 else 'card')
    if k == 0:
        o += f'<path d="M180,66 L75,90" style="stroke:#555;stroke-width:1.6"/>'
    if k == 1:
        o += f'<path d="M180,66 L75,90" style="stroke:#555;stroke-width:1.6"/>' + packet(120, 112, 240, 112, 'blocks') + t(180, 150, 'new writes mirrored to both', 7.4, 'ink', bold=True)
    if k == 2:
        o += f'<path d="M180,66 L285,90" style="stroke:#2E8B57;stroke-width:1.8"/>' + t(180, 150, 'no downtime · old array can be retired', 7.4, 'green', bold=True)
    return o
A_STOR = cap([a_stor(k) for k in range(3)], [('VM on old storage', 'The VM keeps running on its current datastore or volume.', 'The old storage array must be retired.'), ('Copy while running', 'The hypervisor copies all blocks to the new storage and mirrors new', 'writes to both, so nothing is lost.'), ('Switch', 'When both copies match, the VM’s disk is switched to the new storage', 'and the old copy deleted — no downtime.')],
    'Storage migration in action', 'Move the disk, not the VM.', 'Storage migration', 'Animation: a running VM on an old array; blocks copied to a new array with writes mirrored; the VM switched to the new array with no downtime.', 'm7anim')
T7 = vtype(7, 'Storage migration', 'violet',
    '<b>Storage migration</b> moves a running VM’s virtual disks from one storage location (datastore, array, volume type) to another while the VM continues to run on the same host, by copying blocks in the background and mirroring new writes until the copies are identical.',
    'Changing a running train’s fuel tank from the old one to a new one at the station without stopping the engine: fuel is pumped across while the engine runs, then the valve is switched.',
    'TiffinGo’s orders volume is on old gp2 storage. Using EBS Elastic Volumes they change it to gp3 and grow it from 500 to 700 GB while the database keeps running.',
    'VMware Storage vMotion, Hyper-V storage migration, libvirt block copy (virsh blockcopy); cloud: Amazon EBS Elastic Volumes (change type, size, IOPS live), Azure disk type change, Google Persistent Disk resize.',
    '', A_STOR,
    'retiring a storage array, moving to faster/cheaper storage, or rebalancing datastores.',
    'the storage network is already saturated — the copy adds heavy I/O; plan off-peak.',
    plain='The computer keeps running while its hard disk is moved to a new storage system behind the scenes.',
    how=[('Start mirror', 'The hypervisor creates the target disk and starts copying blocks.'), ('Mirror new writes', 'Every new write goes to both old and new disks.'), ('Converge', 'When all blocks are copied, both are identical.'), ('Switch', 'The VM’s disk pointer moves to the new disk atomically.'), ('Clean up', 'The old disk is removed.')],
    words=[('datastore', 'a storage location for VM disks'), ('mirror', 'write the same data to two places'), ('Elastic Volumes', 'EBS feature to change a volume while in use')],
    diff=table(['', 'Storage migration', 'Live migration', 'Cold migration'], [['What moves', 'disk', 'memory + CPU state', 'everything, switched off'], ['Host changes?', 'no', 'yes', 'yes/no'], ['Downtime', 'none', 'ms', 'minutes+']], minw=520),
    where=['Storage array refresh', 'Tiering (fast ↔ cheap storage)', 'EBS volume type/size changes', 'Datastore rebalancing'],
    realworld='Amazon EBS Elastic Volumes lets you increase size, change the volume type (for example gp2 to gp3) and adjust IOPS of a volume attached to a running instance, with the optimization happening in the background.',
    pro='After an Elastic Volumes change there is a cooldown (typically six hours) before you can modify the same volume again — plan the final size, not small steps.')

# ---------------- 8 P2V / V2V
def a_p2v(k):
    o = t(180, 12, ['Capture the physical server', 'Convert disk and drivers', 'Run it as a VM'][k], 9, 'ink', bold=True)
    o += box(10, 30, 110, 90, 'violet' if k == 0 else 'card', rx=6) + ic('server', 53, 38, 0.9) + t(65, 80, 'physical server', 7.6, 'ink', bold=True) + t(65, 96, '2014, Windows', 6.8, 'ink2')
    if k >= 1:
        o += box(130, 44, 100, 60, 'amber', rx=6) + t(180, 66, 'converter', 8, 'ink', bold=True) + t(180, 82, 'disk → vmdk/qcow2', 6.6, 'ink2') + t(180, 94, 'add virtio drivers', 6.6, 'ink2') + packet(120, 74, 130, 74, '')
    if k == 2:
        o += box(250, 30, 100, 90, 'green', rx=6) + t(300, 64, 'VM', 8.4, 'ink', bold=True) + t(300, 80, 'on hypervisor', 7, 'ink2') + packet(230, 74, 250, 74, '') + t(180, 142, 'old box switched off', 7.6, 'green', bold=True)
    return o
A_P2V = cap([a_p2v(k) for k in range(3)], [('Capture the physical server', 'A converter reads the physical machine’s disks (live, with an agent,', 'or offline from a boot disk).'), ('Convert disk and drivers', 'Disks become virtual disk files; storage/network drivers are swapped', 'for virtual ones (virtio, VMware tools) so the OS can boot.'), ('Run as a VM', 'The new VM starts on the hypervisor; the old hardware is retired.', 'V2V is the same between two hypervisors.')],
    'P2V and V2V in action', 'Turning a physical box (or another hypervisor’s VM) into a VM.', 'P2V / V2V', 'Animation: physical server captured; converter changes disk format and drivers; the result runs as a VM and the old server is switched off.', 'm8anim')
T8 = vtype(8, 'P2V and V2V conversion', 'violet',
    '<b>P2V (physical-to-virtual)</b> converts a running physical server’s disks, OS and applications into a virtual machine; <b>V2V (virtual-to-virtual)</b> converts a VM from one hypervisor or format to another (e.g. VMware → KVM/Hyper-V), changing disk formats and drivers so the guest boots on the new platform.',
    'Transferring a family recipe from an old handwritten notebook into a digital recipe app (P2V), or from one app to another (V2V): the recipe stays the same, the format changes.',
    'TiffinGo’s 2014 accounting server runs on dying hardware. P2V turns it into a VM on the new host without reinstalling the old software; later, leaving VMware, they use virt-v2v to convert it to KVM.',
    'virt-v2v and virt-p2v, VMware vCenter Converter, Microsoft Disk2VHD, qemu-img convert (our lab), StarWind V2V; cloud: AWS VM Import/Export, Azure Migrate, Google Migrate to Virtual Machines.',
    '', A_P2V,
    'consolidating old servers, leaving a hypervisor vendor, or moving to another platform.',
    'the OS lacks drivers for the virtual hardware, or licences are tied to physical hardware IDs.',
    plain='An old physical computer — or a VM made for one virtualization product — is turned into a VM that runs on a different system, without reinstalling its software.',
    how=[('Prepare', 'Inventory the server; clean up disks; note licences tied to hardware.'), ('Capture', 'Copy disks with an agent while running, or boot a converter and copy offline.'), ('Convert format', 'Raw disk → vmdk/vhdx/qcow2 (our lab converted qcow2 to vmdk, vhdx and raw).'), ('Inject drivers', 'Add virtio/VMware/Hyper-V storage and network drivers; remove hardware agents.'), ('Boot and fix', 'Start the VM, check IP, services and time sync.'), ('Retire the source', 'After testing, switch off the old system.')],
    words=[('P2V / V2V', 'physical-to-virtual / virtual-to-virtual'), ('driver injection', 'adding drivers to an OS that is not running'), ('vmdk / vhdx / qcow2', 'disk formats of VMware / Hyper-V / KVM')],
    diff=table(['', 'P2V', 'V2V', 'Cloud rehost (type 9)'], [['Source', 'physical server', 'VM on another hypervisor', 'any server'], ['Target', 'VM on-premises', 'VM on another hypervisor', 'cloud instance'], ['Typical tool', 'VMware Converter, virt-p2v', 'virt-v2v, qemu-img', 'AWS MGN, Azure Migrate']], minw=540),
    where=['Data-centre consolidation', 'Leaving VMware for KVM/Hyper-V/Proxmox', 'Preserving legacy apps that cannot be reinstalled'],
    realworld='After Broadcom’s acquisition of VMware changed licensing in 2024, many organisations started V2V projects to move VMs to Hyper-V, Nutanix AHV, Proxmox or KVM using tools such as virt-v2v.',
    pro='Windows P2V often fails at first boot with “INACCESSIBLE_BOOT_DEVICE” because the storage driver for the new virtual controller is missing — inject the driver (or start with an IDE/SATA controller, install virtio, then switch).')

# ---------------- 9 cloud rehost (MGA anim)
def T9(MGA):
    return vtype(9, 'Cloud migration — rehost with replication', 'violet',
        '<b>Rehost (lift-and-shift) migration</b> moves servers to the cloud largely unchanged, typically by installing a replication agent that continuously copies the source disks at block level into the cloud, allowing test launches and a short final cutover.',
        'Moving a shop to a new mall while it stays open: stock is copied to the new shop every evening; on opening day you only bring the last day’s sales and change the signboard.',
        'TiffinGo’s old office server moves to EC2 with AWS Application Migration Service: replication runs for a week, a test instance is launched and checked, then on Sunday the app is stopped, the final changes replicate and DNS is switched — 15 minutes of downtime.',
        'AWS Application Migration Service (MGN), Migration Hub, VM Import/Export; Azure Migrate (server migration), Azure Site Recovery; Google Migrate to Virtual Machines; for VMware estates: VMware Cloud on AWS, Azure VMware Solution, Google Cloud VMware Engine.',
        '', MGA,
        'exiting a data centre quickly, many servers, little time to re-architect.',
        'you never optimize afterwards — a lifted VM costs 24×7; right-size, replatform or modernize later.',
        plain='A copy of the old server is kept continuously updated in the cloud. When ready, you test the copy, then switch users over to it in a few minutes.',
        how=[('Discover and assess', 'Inventory servers, dependencies and sizes (Migration Hub / Azure Migrate).'), ('Install the agent', 'A replication agent is installed on each source server.'), ('Initial sync', 'Full disk copy into low-cost staging volumes in the target Region.'), ('Continuous replication', 'Every block change is sent within seconds.'), ('Test launch', 'Launch test instances from the replica (drivers converted automatically); verify the app.'), ('Cutover', 'Stop the app, let final writes replicate, launch production, switch DNS, keep the source for rollback.')],
        words=[('rehost / lift-and-shift', 'move as-is'), ('staging area', 'cheap resources holding the replica'), ('cutover', 'the moment users switch to the new system'), ('DNS TTL', 'how long clients cache a DNS answer — lower it before cutover')],
        diff=table(['', 'Rehost (MGN)', 'Replatform', 'Refactor'], [['Code changes', 'none', 'small (e.g. DB → RDS)', 'major'], ['Speed', 'fastest', 'medium', 'slowest'], ['Cloud benefit', 'lowest at first', 'medium', 'highest']], minw=520),
        where=['Data-centre exits', 'Disaster recovery to the cloud', 'Moving VMware estates'],
        realworld='AWS Application Migration Service is AWS’s recommended service for lift-and-shift: it replicates source servers (physical, VMware, Hyper-V or other clouds) continuously and converts them to run natively on EC2 at launch.',
        pro='Lower the DNS TTL of the service (e.g. to 60 s) a day before cutover. Otherwise clients keep using the old IP for hours after you switch, and your “15-minute cutover” becomes a day of split traffic.')

SUMMARY = table(['#', 'Type', 'Speed / downtime', 'Best for', 'AWS'], [
    ['1', 'Manual', 'hours per server', 'learning', '— (never in cloud)'], ['2', 'Template / clone', 'seconds–minutes', 'on-prem labs, VDI', '—'], ['3', 'Golden image + cloud-init', 'seconds–minutes', 'all cloud servers', 'AMI, Image Builder, user data'],
    ['4', 'IaC + Auto Scaling', 'automatic', 'fleets, multiple environments', 'CloudFormation/Terraform, EC2 Auto Scaling'], ['5', 'Cold migration', 'minutes–hours down', 'cross-hypervisor moves', 'stop/start, VM Import/Export'],
    ['6', 'Live migration', 'ms pause', 'host maintenance', '(inside AWS; GCE does it visibly)'], ['7', 'Storage migration', 'no downtime', 'array refresh, tiering', 'EBS Elastic Volumes'], ['8', 'P2V / V2V', 'planned window', 'consolidation, vendor exit', 'VM Import/Export'], ['9', 'Rehost to cloud', 'minutes at cutover', 'data-centre exit', 'Application Migration Service']], minw=700)
CHECK = ('  <h3>Check yourself: which type fits?</h3>\n' +
    qx('A. 30 identical lab VMs every Monday on VMware, deleted on Friday.', ['Manual install', 'Linked clones from a template', 'Live migration', 'P2V'], 1, 'Instant, tiny clones from one template.') +
    qx('B. A host needs a firmware update; its VMs must keep running.', ['Cold migration', 'Live migration', 'P2V', 'Storage migration'], 1, 'Move running VMs to other hosts.') +
    qx('C. Change an EBS volume from gp2 to gp3 without stopping the database.', ['Storage migration (Elastic Volumes)', 'Cold migration', 'Template', 'Rehost'], 0, 'EBS Elastic Volumes change type live.') +
    qx('D. Leaving VMware for Proxmox/KVM.', ['V2V conversion', 'Live migration', 'Linked clone', 'Auto Scaling'], 0, 'Convert disks and drivers between hypervisors.') +
    qx('E. 200 office servers must be in AWS within 3 months with minimal downtime.', ['Manual rebuild', 'Rehost with AWS MGN', 'Refactor everything first', 'Cold copy by USB'], 1, 'Continuous replication, test launches, short cutovers.') +
    qx('F. Web servers must grow from 2 to 6 automatically during peaks.', ['Template clones', 'IaC + Auto Scaling', 'P2V', 'Cold migration'], 1, 'Auto Scaling follows load.'))

def build(GOLD, MGA):
    intro = ('  <p>Provisioning and migration each come in several types. Below, every type gets the same treatment as in 4.1 — definition, plain words, analogy, internal steps, picture/animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
             + challenge(['Why can a brand-new EC2 instance show slow disk reads in its first minute?', 'What does KVM do when a VM dirties memory faster than live migration can copy it?', 'Why does lowering DNS TTL a day before cutover matter?'], 'types 3, 6 and 9') + MAP
             + jump(['Manual', 'Template', 'Golden image', 'IaC', 'Cold', 'Live', 'Storage', 'P2V/V2V', 'Rehost']))
    return intro + T1 + T2 + T3(GOLD) + T4 + T5 + T6 + T7 + T8 + T9(MGA) + '\n  <h3 style="margin-top:34px">All nine side by side</h3>\n' + SUMMARY + '\n' + CHECK
