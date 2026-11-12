import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
sys.path.insert(0, HERE)
from _types import build as build_types
from _prac import PRAC
C = 'l44.txt'; CA = 'l44_aws.txt'
def sec(a, b=None): return capsec(C, a, b)
def seca(a, b=None): return capsec(CA, a, b)

hk = hook('How do clouds create 20 identical servers in a few minutes — and move a running server to another machine without users noticing?',
    'With a <b>golden image</b> and <b>copy-on-write clones</b> for provisioning, and <b>live migration</b> for moving. In our lab three VM disks were cloned from a 20 GiB image in <b>33 milliseconds</b>, each using <b>193 KB</b>; a disk was converted for <b>VMware, Hyper-V and raw</b> in one command each; and in AWS we baked an AMI, copied it to another Region and launched three identical VMs from a launch template.',
    ['Provisioning: manual → template → golden image + cloud-init → automatic scaling.', 'VM lifecycle and EC2 instance states.', 'Migration: cold, live (pre-copy), storage, P2V/V2V, and moving to the cloud (AWS MGN, 7 Rs).'])

def story_scene():
    o = t(180, 12, 'Diwali night at TiffinGo', 9, 'ink', bold=True)
    o += box(8, 22, 110, 100, 'blue', rx=8) + ic('server', 51, 28, 0.9) + t(63, 66, 'Need 20 servers', 8, 'ink', bold=True) + t(63, 80, 'in 10 minutes', 7, 'ink2') + t(63, 94, '(provisioning)', 7, 'acc', bold=True)
    o += box(125, 22, 110, 100, 'amber', rx=8) + ic('gear', 168, 28, 0.9) + t(180, 66, 'Host needs repair', 8, 'ink', bold=True) + t(180, 80, 'orders must not stop', 7, 'ink2') + t(180, 94, '(live migration)', 7, 'acc', bold=True)
    o += box(242, 22, 110, 100, 'violet', rx=8) + ic('cloud', 285, 28, 0.9) + t(297, 66, 'Old office server', 8, 'ink', bold=True) + t(297, 80, 'must move to AWS', 7, 'ink2') + t(297, 94, '(cloud migration)', 7, 'acc', bold=True)
    o += t(180, 140, 'One VM idea, three jobs: create fast, move live, move platforms.', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Three boxes: need 20 servers in 10 minutes (provisioning), host needs repair without stopping orders (live migration), old office server must move to AWS (cloud migration).', story_scene(), 'Because a VM is <tspan font-weight="700" class="s-acc">just files + memory</tspan>, it can be copied and moved.', h=168)
dialogue = '''R> Sir, Diwali orders are 6× normal. Installing Linux, nginx and our app by hand on 20 servers will take all night.
A> We will never install by hand again. We build one perfect server once, save it as a golden image, and clone it. Clouds clone in seconds.
K> And tomorrow the data centre wants to repair the host our database VM is on. Do we shut it down?
A> Not if the hypervisor can live-migrate: it copies the VM’s memory to another host while it runs, pauses it for a few milliseconds, and continues there.
R> And our old office server?
A> Same idea, bigger move: replicate its disk to AWS, test, then switch. Today: provisioning, the VM lifecycle, and every kind of migration.'''

# ---------------------------------------------------------------- figures
def ladder():
    o = t(320, 16, 'Four ways to provision a server — each one faster and more repeatable', 11, 'ink', bold=True)
    rows = [('1 · Manual install', 'Boot ISO → install OS → install packages → configure by hand', 'hours', 'one-off labs', 'red'),
            ('2 · Template / clone', 'Copy a prepared VM (full clone or linked clone)', 'minutes', 'VMware templates, our qcow2 clones', 'amber'),
            ('3 · Image + first-boot script', 'Launch from a golden image; cloud-init applies the last settings', 'seconds–minutes', 'AMIs + user data, Azure images, GCE images', 'blue'),
            ('4 · Code + automation', 'Terraform/CloudFormation define it; Auto Scaling creates/destroys VMs by load', 'automatic', 'Auto Scaling groups, scale sets, MIGs', 'green')]
    for i, (h, d, tm, ex, tn) in enumerate(rows):
        y = 32 + i * 62
        x = 20 + i * 30
        o += box(x, y, 600 - i * 30, 54, tn, rx=8) + t(x + 12, y + 20, h, 9, 'ink', anchor='start', bold=True) + t(x + 12, y + 38, d, 7.6, 'ink', anchor='start')
        o += t(606, y + 20, tm, 8.6, 'ink', anchor='end', bold=True) + t(606, y + 38, ex, 7, 'ink2', anchor='end')
    o += t(320, 290, 'Clouds live at levels 3 and 4: no one installs an OS on an EC2 instance — it is always launched from an image.', 7.8, 'ink2')
    return o
LADDER = bigfig('A staircase of four provisioning methods: manual install (hours), template or clone (minutes), image plus first-boot script such as cloud-init (seconds to minutes), and code plus automation with Auto Scaling (automatic).', ladder(), h=300)

def lifecycle():
    o = t(320, 16, 'VM lifecycle — generic states and their EC2 names', 11, 'ink', bold=True)
    S = {'def': (20, 60, 'Defined', 'config only'), 'prov': (165, 60, 'Provisioned', 'disk + resources'), 'run': (310, 60, 'Running', 'EC2: running'),
         'pause': (310, 170, 'Paused / suspended', 'EC2: hibernated'), 'stop': (480, 60, 'Stopped', 'EC2: stopped'), 'del': (480, 170, 'Deleted', 'EC2: terminated'),
         'mig': (165, 170, 'Migrating', 'to another host')}
    for k, (x, y, a, b) in S.items():
        tn = {'run': 'green', 'del': 'red', 'pause': 'violet', 'stop': 'amber', 'mig': 'blue'}.get(k, 'card')
        o += box(x, y, 130, 46, tn, rx=8) + t(x + 65, y + 20, a, 8.6, 'ink', bold=True) + t(x + 65, y + 36, b, 7.2, 'ink2')
    for x1, y1, x2, y2 in [(150, 83, 165, 83), (295, 83, 310, 83), (440, 74, 480, 74), (480, 94, 440, 94), (368, 106, 368, 170), (382, 170, 382, 106), (545, 106, 545, 170), (318, 106, 262, 170), (280, 170, 330, 106)]:
        o += arrow(x1, y1, x2, y2)
    o += t(460, 68, 'stop', 7, 'ink2') + t(460, 106, 'start', 7, 'ink2') + t(388, 140, 'resume', 7, 'ink2', anchor='start') + t(362, 140, 'hibernate', 7, 'ink2', anchor='end') + t(553, 140, 'terminate', 7, 'ink2', anchor='start') + t(268, 128, 'migrate', 7, 'ink2', anchor='end')
    o += box(20, 236, 600, 50, 'card', rx=8)
    o += t(30, 254, 'EC2 in-between states you will see: pending (booting) · stopping · shutting-down (terminating). Billing for compute runs only in “running”;', 7.4, 'ink', anchor='start')
    o += t(30, 270, 'EBS volumes are billed even when stopped. Stop → start usually moves an EBS-backed instance to a new physical host (a simple “cold migration”).', 7.4, 'ink', anchor='start')
    return o
LIFE = bigfig('VM lifecycle diagram: Defined → Provisioned → Running; Running ↔ Stopped (EC2 stopped); Running ↔ Paused/Suspended (EC2 hibernated); Running ↔ Migrating; Stopped → Deleted (EC2 terminated). Notes on EC2 pending, stopping and shutting-down states and billing.', lifecycle(), h=296)

def migtypes():
    o = t(320, 16, 'Kinds of migration — what moves, and how long the service stops', 11, 'ink', bold=True)
    rows = [('Cold migration', 'VM powered off; disk files copied; start on new host', 'minutes–hours', 'any hypervisor, our qemu-img convert', 'amber'),
            ('Live migration', 'Memory copied while VM runs; pause only for the last pages', 'milliseconds', 'vMotion, KVM, Hyper-V, Google Compute Engine', 'green'),
            ('Storage migration', 'Disk moved to another datastore while VM runs', 'none', 'Storage vMotion; EBS volume type change', 'blue'),
            ('P2V / V2V', 'Physical server → VM, or VMware → KVM (format change)', 'planned window', 'virt-v2v, VMware Converter, qemu-img', 'violet'),
            ('To the cloud', 'Replicate disks continuously, test, then cut over', 'minutes at cutover', 'AWS MGN, Azure Migrate, Migrate to VMs', 'red')]
    o += t(30, 40, 'Type', 7.6, 'ink2', anchor='start', bold=True) + t(170, 40, 'What happens', 7.6, 'ink2', anchor='start', bold=True) + t(470, 40, 'Downtime', 7.6, 'ink2', anchor='start', bold=True)
    for i, (a, b, c, d, tn) in enumerate(rows):
        y = 48 + i * 46
        o += box(20, y, 600, 40, tn, rx=6) + t(30, y + 24, a, 8.8, 'ink', anchor='start', bold=True) + t(170, y + 17, b, 7.6, 'ink', anchor='start') + t(170, y + 31, 'e.g. ' + d, 7, 'ink2', anchor='start') + t(470, y + 24, c, 8, 'ink', anchor='start', bold=True)
    return o
MIG = bigfig('Table-like figure of five migration kinds: cold migration (minutes to hours of downtime), live migration (milliseconds), storage migration (none), P2V/V2V (planned window), migration to the cloud (minutes at cutover), each with examples.', migtypes(), h=290)

picture = ('  <p>A VM is only <b>files</b> (its disks and configuration) plus, while running, <b>memory and CPU state</b>. Files can be copied in seconds and memory can be streamed over a network. That single fact gives us fast <b>provisioning</b> and every kind of <b>migration</b>.</p>\n'
           '  <h3>Provisioning: from hours to seconds</h3>\n' + LADDER +
           '\n  <h3>The VM lifecycle</h3>\n  <p>Every VM goes through the same states. Knowing them tells you what you pay for and what happens to data in each one:</p>\n' + LIFE +
           '\n  <h3>Migration: moving a VM</h3>\n' + MIG)

# ---------------------------------------------------------------- animation 1: golden image pipeline
GN = {'base': (4, 4, 62, 46, 'disk', 'Base image', 'AL2023 / Ubuntu'), 'bake': (4, 104, 62, 46, 'gear', 'Bake', 'Image Builder'),
      'ami': (78, 54, 62, 50, 'disk', 'Golden AMI', 'menu-v1'), 'lt': (150, 54, 62, 50, 'dns', 'Launch tmpl', 'the recipe'),
      'asg': (222, 54, 62, 50, 'meter', 'Auto Scaling', 'desired = 20'), 'vms': (294, 4, 62, 46, 'server', '20 VMs', 'CoW clones'),
      'ci': (294, 104, 62, 46, 'app', 'cloud-init', 'first boot')}
GS = [dict(on=['base'], hot='base', move=None, head='Step 1 · Start from a trusted base image', text='A vendor image (Amazon Linux 2023, Ubuntu 24.04) — only the OS, patched.', text2='Real size of the Ubuntu 24.04 cloud image today: 593 MB.', svc='AWS: SSM public parameters give the latest AMI ID · Azure Marketplace · GCE public images'),
      dict(on=['base', 'bake'], hot='bake', move=(35, 50, 35, 104, 'install'), head='Step 2 · Bake: install everything once', text='A builder VM installs nginx, the app, agents and security patches, runs tests,', text2='then is shut down. Do the slow work once, not on every server.', svc='EC2 Image Builder, HashiCorp Packer, Azure Image Builder'),
      dict(on=['base', 'bake', 'ami'], hot='ami', move=(66, 127, 92, 104, 'capture'), head='Step 3 · Capture the golden image', text='The builder’s disk is snapshotted and registered as an AMI: tiffingo-menu-v1.', text2='Version it; never change it — build v2 instead.', svc='aws ec2 create-image · copy-image to other Regions for DR'),
      dict(on=['base', 'bake', 'ami', 'lt'], hot='lt', move=(140, 79, 150, 79, ''), head='Step 4 · Write the recipe', text='A launch template stores AMI, instance type, security group, IAM role,', text2='key pair and user data — every VM will be created the same way.', svc='Launch template (AWS) · VM scale set model (Azure) · instance template (GCP)'),
      dict(on=['base', 'bake', 'ami', 'lt', 'asg', 'vms'], hot='vms', move=(284, 66, 300, 40, 'x20'), head='Step 5 · Provision many clones', text='Auto Scaling asks for 20 instances. Each root disk is a copy-on-write clone of', text2='the AMI’s snapshot, so it does not wait for 20 full copies.', svc='Our lab: 3 clones of a 20 GiB image in 33 ms, 193 KB each'),
      dict(on=list(GN), hot='ci', move=(325, 50, 325, 104, 'boot'), head='Step 6 · First boot personalizes each VM', text='cloud-init reads user data and instance metadata: sets hostname, SSH keys,', text2='config values — then the VM joins the load balancer and serves orders.', svc='“Bake” the slow parts into the image, “fry” only small per-VM settings at boot')]
GOLD = flow_anim('From base image to 20 running servers', 'The golden-image pipeline every cloud team uses. Six steps; the slow work happens only once.', 'Golden image provisioning', 'Animation: base image, bake software with Image Builder, capture golden AMI, launch template recipe, Auto Scaling creates 20 copy-on-write clones, cloud-init personalizes each VM at first boot.', GN, GS, hid='gold')

# ---------------------------------------------------------------- animation 2: live migration pre-copy
def mem(x, y, dirty, copied, cols=10, rows=3):
    o = ''
    for i in range(cols * rows):
        tn = 'red' if i in dirty else ('green' if i in copied else 'card')
        o += box(x + (i % cols) * 9, y + (i // cols) * 9, 7.5, 7.5, tn, rx=1)
    return o
LN = {'src': (4, 30, 92, 58, 'server', 'Host A (old)', 'VM running'), 'dst': (264, 30, 92, 58, 'server', 'Host B (new)', 'empty shell'),
      'sto': (134, 108, 92, 44, 'disk', 'Shared storage', 'disk not copied')}
def lm_extra(k):
    allp = set(range(30))
    src_d = [set(), {3, 8, 14, 22, 27}, {8, 22}, set(), set(), set()][k]
    dst_c = [set(), allp - {3, 8, 14, 22, 27}, allp - {8, 22}, allp, allp, allp][k]
    o = mem(7, 92 - 0, src_d, allp if k < 4 else set()) if k < 5 else ''
    o += mem(267, 92, set(), dst_c) if k >= 1 else ''
    lab = ['', 'round 1: all memory → 4 GB', 'round 2: only dirty pages → 300 MB', 'pause ≈ 50 ms: last pages + CPU state', 'network: “10.10.1.5 is here now”', 'VM runs on Host B'][k]
    if lab:
        o += box(110, 4, 140, 20, 'amber' if k != 3 else 'red', rx=10) + t(180, 18, lab, 6.8, 'ink', bold=True)
    o += t(180, 222 - 2, '', 6)
    return o
LS = [dict(on=['src', 'sto'], hot='src', move=None, extra=lm_extra(0), head='Step 1 · Prepare the destination', text='Host B checks it has a compatible CPU and enough RAM and creates an empty VM', text2='“shell”. Both hosts already see the same disk (shared storage), so no disk copy.', svc='Requirements: compatible CPUs, shared storage (or storage migration), fast network'),
      dict(on=['src', 'dst', 'sto'], hot='dst', move=(96, 50, 264, 50, 'copy RAM'), extra=lm_extra(1), head='Step 2 · Pre-copy round 1: copy all memory', text='All 4 GB of RAM pages are sent while the VM keeps running and changing pages.', text2='Pages changed during the copy are marked dirty (red).', svc='The hypervisor tracks writes using the CPU’s page tables (dirty logging)'),
      dict(on=['src', 'dst', 'sto'], hot='dst', move=(96, 50, 264, 50, 'dirty'), extra=lm_extra(2), head='Step 3 · Repeat: copy only dirty pages', text='Each round sends only what changed since the last round, so rounds get smaller:', text2='4 GB → 300 MB → 40 MB … (example numbers).', svc='If the VM dirties memory faster than the network can send, it never converges'),
      dict(on=['src', 'dst', 'sto'], hot='src', move=(96, 70, 264, 70, 'last'), extra=lm_extra(3), head='Step 4 · Stop-and-copy (the only pause)', text='The VM is paused for tens of milliseconds; the last dirty pages, CPU registers', text2='and device state are sent. Users see a tiny hiccup, connections stay open.', svc='This pause is the “downtime” of a live migration'),
      dict(on=['src', 'dst', 'sto'], hot='dst', move=None, extra=lm_extra(4), head='Step 5 · Move the network identity', text='The VM keeps its IP and MAC. The network is told it now lives on Host B', text2='(gratuitous ARP, or the SDN mapping is updated — Lesson 4.3).', svc='In a VPC-style overlay only the mapping service changes'),
      dict(on=['dst', 'sto'], hot='dst', move=None, extra=lm_extra(5), head='Step 6 · Resume on the new host', text='The VM continues on Host B; Host A frees its memory and can be repaired.', text2='The app never rebooted.', svc='Google Compute Engine does this automatically for host maintenance')]
LIVE = flow_anim('Live migration, page by page (pre-copy)', 'How a running VM moves to another host with only a few milliseconds of pause.', 'Live migration', 'Animation: destination prepared; memory copied in rounds while VM runs; dirty pages re-sent; brief stop-and-copy pause; network identity moved; VM resumes on the new host.', LN, LS, hid='live')

# ---------------------------------------------------------------- animation 3: replication-based cloud migration
def mg_frame(k):
    o = t(180, 12, ['Install the replication agent', 'Continuous block replication', 'Test launch (no downtime)', 'Cutover'][k], 9, 'ink', bold=True)
    o += box(10, 30, 120, 80, 'violet', rx=8) + ic('server', 58, 36, 0.9) + t(70, 76, 'Office server', 8, 'ink', bold=True) + t(70, 90, 'VMware / physical', 7, 'ink2')
    o += box(230, 30, 120, 80, 'blue', rx=8) + ic('cloud', 278, 36, 0.9) + t(290, 76, 'AWS staging area', 8, 'ink', bold=True) + t(290, 90, 'cheap replication VM', 7, 'ink2')
    if k == 0:
        o += box(30, 112, 80, 20, 'amber', rx=4) + t(70, 126, 'agent', 7.4, 'ink', bold=True)
    if k >= 1:
        o += packet(130, 60, 230, 60, 'blocks')
        o += t(180, 150, 'every disk write is sent within seconds', 7.2, 'ink')
    if k == 2:
        o += box(230, 112, 120, 22, 'green', rx=4) + t(290, 127, 'test VM launched ✓', 7.4, 'ink', bold=True)
    if k == 3:
        o += box(230, 112, 120, 22, 'green', rx=4) + t(290, 127, 'production VM live', 7.4, 'ink', bold=True) + box(10, 112, 120, 22, 'red', rx=4) + t(70, 127, 'old server retired', 7.4, 'ink', bold=True)
    return o
MGS = [('Install the agent', 'A small agent on the source server reads every disk at block level.', 'Works the same for physical, VMware, Hyper-V or another cloud.'),
       ('Replicate continuously', 'First a full copy, then every change, into low-cost staging volumes in AWS.', 'The source keeps serving users the whole time.'),
       ('Test launch', 'Launch a test instance from the replicated disks, convert drivers, check the app.', 'Nothing changes for users yet.'),
       ('Cutover', 'Stop the app briefly, let the last writes replicate, launch production, switch DNS.', 'Downtime = minutes; roll back by pointing DNS back.')]
MGA = anim_one('How it works', 'Moving a real server to the cloud (AWS Application Migration Service)', 'Lift-and-shift with almost no downtime: replicate first, switch later.', 'Rehost migration', 'Animation: install an agent on the office server, continuous block replication to an AWS staging area, test launch, then cutover with the old server retired.', cap_frames([mg_frame(k) for k in range(4)], MGS), [x[0] + '.' for x in MGS], delay=6000, hid='mgn')

parts = '\n  <h3>Disk image formats you will meet</h3>\n' + table(['Format', 'Used by', 'Notes'], [
    ['qcow2', 'KVM/QEMU, OpenStack', 'thin, snapshots, backing files (our lab)'], ['VMDK', 'VMware', 'often packaged as OVA/OVF'], ['VHD / VHDX', 'Hyper-V, Azure (VHD fixed)', 'Azure uploads need fixed-size VHD'],
    ['raw / img', 'everything', 'plain bytes, simplest, largest'], ['AMI', 'AWS', 'not a file: metadata + EBS snapshot(s); import with VM Import/Export']], minw=520) + \
    '\n  <h3>The 7 Rs: strategies for moving applications to the cloud</h3>\n' + table(['Strategy', 'Meaning', 'Example'], [
    ['Retire', 'Switch it off — nobody uses it', 'Old reporting server'], ['Retain', 'Keep on-premises for now', 'Mainframe with 3-year contract'], ['Rehost (lift and shift)', 'Move the VM as it is', 'MGN: office server → EC2'],
    ['Relocate', 'Move a whole VMware environment unchanged', 'VMware Cloud on AWS'], ['Replatform (lift, tinker, shift)', 'Small changes for a managed service', 'MySQL VM → Amazon RDS'],
    ['Repurchase', 'Replace with SaaS', 'Own CRM → Salesforce'], ['Refactor / re-architect', 'Rewrite to be cloud-native', 'Monolith → containers/serverless']], minw=560)

DEEP = ('  <h3>What exactly moves in a live migration</h3>\n' + table(['Piece', 'How it moves', 'Size'], [
    ['Memory (RAM)', 'pre-copy rounds, then last dirty pages', 'GBs (the bulk)'], ['CPU state', 'registers copied during the pause', 'KBs'], ['Device state', 'virtual NIC/disk queues serialized', 'KBs'],
    ['Disk', 'usually not moved (shared storage); otherwise storage migration first', '0 or GBs–TBs'], ['Network identity', 'same MAC/IP; switches/SDN told the new location', 'one message']], minw=520) +
    '\n  <p><b>Will it finish?</b> If the VM writes memory at 2 GB/s and the migration link sends 1.2 GB/s, the dirty set never shrinks. Hypervisors then slow the VM’s CPU (“auto-converge”) or switch to post-copy. That is why live migration needs fast dedicated links (10–100 Gbps) and why huge, write-heavy databases are the hardest VMs to move.</p>\n'
    '  <h3>How the big clouds handle host maintenance</h3>\n' + table(['Cloud', 'What happens to your VM'], [
    ['Google Compute Engine', 'Live-migrates most VMs by default (onHostMaintenance = MIGRATE); GPU and some special VMs are stopped instead.'],
    ['Azure', 'Most platform updates are memory-preserving (VM paused ~seconds) or live-migrated; others are announced as scheduled maintenance you can trigger yourself.'],
    ['AWS EC2', 'Nitro lets AWS update much host software without rebooting you. When hardware must be retired, you get a <b>scheduled event</b> (instance retirement / system reboot); a stop and start of an EBS-backed instance moves it to healthy hardware.']], minw=560) +
    '\n  <h3>Why AMIs launch so fast</h3>\n  <p>An AMI is a pointer to EBS snapshots stored in S3. A new instance’s root volume is created from the snapshot <b>lazily</b>: blocks are fetched from S3 the first time they are read. The VM boots immediately, but the first read of each block is slower. For databases that need full speed from the first second, AWS offers <b>Fast Snapshot Restore</b> or you pre-read (“initialize”) the volume.</p>\n'
    '  <h3>Bake vs fry</h3>\n  <p><b>Bake</b> = put it in the image (slow-changing: OS, runtime, agents). <b>Fry</b> = do it at boot with cloud-init (fast-changing: config, secrets fetched from a secrets manager). Bake too little and boots are slow and fragile; bake too much (passwords, environment names) and you need a new image for every change.</p>')

clouds = vendor_tabs('<p><b>AWS:</b> images = <b>AMIs</b> (create-image, copy-image), <b>EC2 Image Builder</b>; recipe = <b>launch templates</b>; scale = <b>EC2 Auto Scaling</b> (instance refresh to roll a new AMI); migration = <b>Application Migration Service (MGN)</b>, VM Import/Export, Migration Hub, <b>VMware Cloud on AWS</b> (relocate).</p>',
    '<p><b>Azure:</b> images = <b>Azure Compute Gallery</b>, Azure Image Builder; scale = <b>VM Scale Sets</b>; migration = <b>Azure Migrate</b> (discovery, assessment, server migration), Azure VMware Solution; maintenance = memory-preserving updates, live migration.</p>',
    '<p><b>Google Cloud:</b> images = <b>custom images, machine images</b>; recipe = <b>instance templates</b>; scale = <b>managed instance groups</b>; migration = <b>Migrate to Virtual Machines</b>, Google Cloud VMware Engine; maintenance = automatic <b>live migration</b>.</p>') + \
    cloud3([['Golden image', 'AMI', 'Compute Gallery image', 'Custom / machine image'], ['Image pipeline', 'EC2 Image Builder', 'Azure Image Builder', 'Packer / Cloud Build'], ['Launch recipe', 'Launch template', 'Scale-set model', 'Instance template'],
            ['Auto provisioning', 'Auto Scaling group', 'VM Scale Sets', 'Managed instance group'], ['Server migration', 'MGN', 'Azure Migrate', 'Migrate to VMs'], ['Run VMware as-is', 'VMware Cloud on AWS', 'Azure VMware Solution', 'Google Cloud VMware Engine']])

proof = [
    ('Step 1 · A golden image', code('bash', 'terminal', 'qemu-img create -f qcow2 golden.qcow2 20G\nqemu-img info golden.qcow2', sec('== 1)', '== 2)')), 'Our stand-in for an OS image: 20 GiB virtual, almost nothing stored yet.'),
    ('Step 2 · Provision three VMs as linked clones', code('bash', 'terminal', 'for i in 1 2 3; do\n  qemu-img create -f qcow2 -b golden.qcow2 -F qcow2 vm$i.qcow2\ndone\nls -lh vm*.qcow2', sec('== 2)', '== 3)')), '33 ms for three VM disks. This is why clouds and VDI platforms provision from shared images.'),
    ('Step 3 · Snapshot before a risky change', code('bash', 'terminal', 'qemu-img snapshot -c before-upgrade vm1.qcow2\nqemu-img snapshot -l vm1.qcow2', sec('== 3)', '== 4)')), 'If the upgrade breaks, <code>qemu-img snapshot -a before-upgrade</code> rolls back.'),
    ('Step 4 · Convert for VMware, Hyper-V, raw (V2V)', code('bash', 'terminal', 'qemu-img convert -O vmdk golden.qcow2 golden.vmdk\nqemu-img convert -O vhdx golden.qcow2 golden.vhdx\nqemu-img convert -O raw  golden.qcow2 golden.raw', sec('== 4)', '== 5)')), 'The disk is now readable by VMware and Hyper-V — the file part of a cold V2V migration (drivers inside the guest may also need changing).'),
    ('Step 5 · How big is a real cloud image?', code('bash', 'terminal', 'curl -sI https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img', sec('== 5)')), 'A complete server OS in 593 MB — small enough to cache on every host, which is part of why launches are fast.')]

prac = practical('Part A runs on any Linux/WSL2 machine (<code>sudo apt install qemu-utils</code>). Part B uses the AWS CLI. <b>Our Part B outputs come from the moto AWS emulator</b> — IDs differ on a real account. On a real account t3.micro is Free-Tier eligible; AMI snapshots cost a little per GB-month until deregistered.', [
    ('A1 · Golden image and linked clones', code('bash', 'terminal', 'qemu-img create -f qcow2 golden.qcow2 20G\nfor i in 1 2 3; do qemu-img create -f qcow2 -b golden.qcow2 -F qcow2 vm$i.qcow2; done\nls -lh *.qcow2'), 'Three tiny files that each look like a 20 GiB disk.'),
    ('A2 · Snapshot and roll back', code('bash', 'terminal', 'qemu-img snapshot -c before-upgrade vm1.qcow2\nqemu-img snapshot -l vm1.qcow2\nqemu-img snapshot -a before-upgrade vm1.qcow2   # roll back'), 'Snapshots inside the qcow2 file itself.'),
    ('A3 · Cold V2V conversion', code('bash', 'terminal', 'qemu-img convert -p -O vmdk golden.qcow2 golden.vmdk\nqemu-img info golden.vmdk'), 'Open the .vmdk in VMware Workstation or the .vhdx in Hyper-V.'),
    ('B1 · Builder VM with user data (cloud-init)', code('bash', 'terminal', "AMI=$(aws ssm get-parameter --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \\\n  --query Parameter.Value --output text)\ncat > userdata.sh <<'UD'\n#!/bin/bash\ndnf install -y nginx && echo \"TiffinGo menu v1\" > /usr/share/nginx/html/index.html && systemctl enable --now nginx\nUD\nB=$(aws ec2 run-instances --image-id $AMI --instance-type t3.micro --user-data file://userdata.sh \\\n  --query 'Instances[0].InstanceId' --output text)", seca('== 1)', '== 2)')), 'cloud-init runs the script on first boot. On a real account wait ~2 minutes and open the public IP (with port 80 allowed) to see “TiffinGo menu v1”.'),
    ('B2 · Bake the golden AMI', code('bash', 'terminal', 'G=$(aws ec2 create-image --instance-id $B --name tiffingo-menu-v1 \\\n  --description "AL2023 + nginx + menu v1" --query ImageId --output text)\naws ec2 wait image-available --image-ids $G    # real account: a few minutes\naws ec2 describe-images --image-ids $G --query \'Images[].[ImageId,Name,State]\' --output table', seca('== 2)', '== 3)')), 'create-image reboots the instance by default for a consistent disk (use --no-reboot only if you accept that risk).'),
    ('B3 · Copy the image to another Region', code('bash', 'terminal', 'aws ec2 copy-image --region ap-southeast-1 --source-region ap-south-1 \\\n  --source-image-id $G --name tiffingo-menu-v1', seca('== 3)', '== 4)')), 'AMIs are Regional. Copying is how you prepare disaster recovery or launch in a new market. The copy gets a new ID.'),
    ('B4 · Write the launch template', code('bash', 'terminal', 'aws ec2 create-launch-template --launch-template-name menu-lt \\\n  --launch-template-data "{\\"ImageId\\":\\"$G\\",\\"InstanceType\\":\\"t3.micro\\"}"', seca('== 4)', '== 5)')), 'Version 1 of the recipe. In real use add SecurityGroupIds, IamInstanceProfile and MetadataOptions (IMDSv2 required).'),
    ('B5 · Provision three identical VMs', code('bash', 'terminal', "aws ec2 run-instances --launch-template LaunchTemplateName=menu-lt --count 3\naws ec2 describe-instances --instance-ids $IDS \\\n  --query 'Reservations[].Instances[].[InstanceId,ImageId,InstanceType,State.Name]' --output table", seca('== 5)', '== 6)')), 'All three from the same golden AMI — identical by construction.'),
    ('B6 · Walk the lifecycle', code('bash', 'terminal', 'aws ec2 stop-instances  --instance-ids $ONE\naws ec2 start-instances --instance-ids $ONE', seca('== 6)', '== 7)')), 'running → stopping → stopped → pending → running. After a real stop/start the public IP changes (unless it is an Elastic IP) and the instance usually lands on a different host.')],
    cleanup='<code>aws ec2 terminate-instances</code> (all four), <code>deregister-image</code> in both Regions <b>and</b> <code>delete-snapshot</code> for the snapshots behind each AMI (deregistering does not delete them), <code>delete-launch-template</code>. Locally delete the .qcow2/.vmdk/.vhdx/.raw files.')

mist = mistakes([
    ['Installing software by hand on each server (“snowflake servers”).', 'Feels faster for the first one.', 'Bake a golden image or use user data/IaC; servers must be cattle, not pets.'],
    ['Baking passwords or API keys into an AMI.', 'Convenient at build time.', 'Fetch secrets at boot from Secrets Manager / Parameter Store with an IAM role.'],
    ['Deregistering an AMI and forgetting its snapshots.', 'Deregister does not delete the EBS snapshots.', 'Delete the snapshots too (or use Data Lifecycle Manager / Image Builder lifecycle).'],
    ['Expecting an AMI ID to work in another Region.', 'AMIs are Regional.', 'copy-image and use the new ID; use SSM parameters to look IDs up.'],
    ['Assuming stop/start keeps the public IP and instance-store data.', 'It looks like a reboot.', 'Public IP changes (use an Elastic IP); instance-store data is lost; EBS data stays.'],
    ['Live-migrating a VM with a passthrough GPU/SR-IOV NIC.', 'Directly assigned hardware cannot be copied.', 'Plan downtime or use migratable virtual devices.'],
    ['Rehosting everything, then never optimizing.', 'Lift-and-shift is fast.', 'After moving, right-size, replatform (RDS), and use Savings Plans.'],
    ['Cutting over without a rollback plan.', 'Confidence after tests.', 'Keep the source until the new system is proven; lower DNS TTL before cutover.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA (Linux & Cloud)', 'VM provisioning and migration services; VM life cycle; live migration.'], ['AWS CLF-C02', 'AMIs, launch templates, Auto Scaling; migration strategies (7 Rs), AWS MGN, Migration Hub, Snow Family.'], ['AZ-900', 'VM Scale Sets, Azure Migrate.'], ['Google Cloud Digital Leader', 'Migration approaches (lift-and-shift, improve and move, rebuild); live migration of Compute Engine VMs.']], minw=520) + '\n  <h3>Exam-style questions with explanations</h3>\n' + \
    qx('1. A company wants every new EC2 instance to start with nginx and security agents already installed. Best approach?', ['Install by hand after launch', 'Create a golden AMI and launch from it', 'Use a bigger instance', 'Use S3'], 1, 'A golden AMI bakes software in, so every instance is identical and boots ready.') + \
    qx('2. Which AWS service rehosts on-premises servers with continuous replication and minimal downtime?', ['AWS Snowball', 'AWS Application Migration Service (MGN)', 'Amazon S3 Transfer Acceleration', 'AWS Backup'], 1, 'MGN replicates block-level changes continuously and supports test launches and cutover.') + \
    qx('3. Moving a MySQL server VM to Amazon RDS is which of the 7 Rs?', ['Rehost', 'Replatform', 'Retire', 'Repurchase'], 1, 'A small change to use a managed platform, without rewriting the app.') + \
    qx('4. During pre-copy live migration, when is the VM actually paused?', ['During the whole memory copy', 'Only for the final stop-and-copy of remaining dirty pages and CPU state', 'Never', 'While the disk is copied'], 1, 'Earlier rounds run while the VM keeps working.') + \
    qx('5. An AMI built in ap-south-1 is needed in us-east-1. What do you do?', ['Use the same ID', 'Copy the AMI to us-east-1 and use the new ID', 'Share it with another account', 'Make it public'], 1, 'AMIs are Regional resources.') + \
    qx('6. Which provisioning component runs your script on an instance’s first boot?', ['IAM', 'cloud-init with user data', 'CloudTrail', 'Route 53'], 1, 'cloud-init reads user data from the instance metadata service and executes it.')

proj = miniproject('Mini project: a golden-image pipeline with a zero-downtime rollout',
    'Build menu v1 as an AMI, run it in an Auto Scaling group behind a load balancer, then roll out v2 by baking a new image — the way real teams ship server changes.',
    ['<b>Bake v1:</b> practical B1–B2 (user data installs nginx and writes “menu v1”); wait for the AMI to be <code>available</code>; terminate the builder.',
     '<b>Recipe:</b> launch template <code>menu-lt</code> with the v1 AMI, t3.micro, a security group allowing port 80 from the load balancer only, and <code>MetadataOptions HttpTokens=required</code>.',
     '<b>Load balancer:</b> create a target group (HTTP 80) and an Application Load Balancer in two public subnets (Lesson 6.3).',
     '<b>Auto Scaling:</b> <code>aws autoscaling create-auto-scaling-group --auto-scaling-group-name menu-asg --launch-template LaunchTemplateName=menu-lt,Version=\'$Latest\' --min-size 2 --max-size 4 --desired-capacity 2 --vpc-zone-identifier "subnetA,subnetB" --target-group-arns $TG</code>. Open the ALB DNS name: “menu v1”.',
     '<b>Bake v2:</b> repeat with user data writing “menu v2”; create launch template version 2 with <code>aws ec2 create-launch-template-version --source-version 1</code> and the new ImageId.',
     '<b>Roll out:</b> <code>aws autoscaling start-instance-refresh --auto-scaling-group-name menu-asg --preferences MinHealthyPercentage=50</code>; refresh the ALB URL repeatedly and watch v1 change to v2 with no errors.',
     '<b>Roll back</b> by setting the group to launch-template version 1 and refreshing again. <b>Clean up:</b> delete the ASG, ALB, target group, launch template, AMIs and their snapshots.'],
    'Screenshots of v1, the instance refresh progress, and v2 served without downtime.', 'This lesson + Lesson 2.1 (EC2) + Lesson 6.3 (cloud networking, load balancers).')

assemble_v2(HERE, story_h2='Twenty servers before dinner, and a host repair without stopping orders', hook_html=hk,
    narration='Diwali week: orders are six times normal. TiffinGo needs more servers right now, a host under its database needs repair tomorrow, and the old office server must finally move to the cloud.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='VM provisioning, lifecycle and migration',
    formal='<b>VM provisioning</b> is the process of creating a virtual machine and allocating and configuring its resources — CPU, memory, storage, network, operating system and software — typically from a template or image, manually or automatically on demand. The <b>VM lifecycle</b> is the sequence of states a VM passes through, from definition and provisioning to running, suspension, stopping and deletion. <b>VM migration</b> is the transfer of a virtual machine — its storage, memory and execution state — from one physical host or platform to another; it is <b>cold</b> when the VM is powered off and <b>live</b> when it continues running with only a brief pause.',
    simple='Provisioning = creating ready-to-use VMs quickly from a prepared image. Migration = moving a VM to another machine or platform — either switched off (cold) or while running (live).',
    interview=['“VM provisioning means creating and configuring VMs with CPU, memory, storage, network and software. In the cloud we provision from golden images like AMIs, personalize with cloud-init user data, and automate with launch templates and Auto Scaling.”', '“Live migration moves a running VM to another host: memory is copied in rounds while it runs, then the VM is paused for milliseconds to copy the last dirty pages and CPU state, and resumes on the new host with the same IP.”', '“For moving to the cloud I would use the 7 Rs; for rehosting, AWS Application Migration Service replicates disks continuously so cutover takes only minutes.”'],
    terms_rows=[('Golden image', 'Tested image with software baked in.'), ('AMI', 'Amazon Machine Image: metadata + EBS snapshots.'), ('Linked clone', 'Copy-on-write disk sharing a base.'), ('cloud-init', 'First-boot configuration from user data.'), ('Launch template', 'Saved recipe for launching instances.'), ('Cold migration', 'Move a powered-off VM.'), ('Live migration', 'Move a running VM, ms pause.'), ('Pre-copy', 'Copy memory first, then switch.'), ('P2V / V2V', 'Physical→virtual / hypervisor→hypervisor.'), ('Rehost', 'Lift-and-shift to the cloud.')],
    exam='CLF-C02 loves the 7 Rs and “which service”: MGN = rehost servers; DMS = migrate databases; Snowball = move bulk data offline; Migration Hub = track all of it.',
    picture_h2='Provisioning, lifecycle and migration in three pictures', picture_html=picture,
    how_h2='Live migration, page by page', how_intro='The most delicate mechanism of this lesson in full: how a running VM moves hosts with only milliseconds of pause.', how_anim=LIVE,
    parts_h2='Disk formats and the 7 Rs', parts_html=parts,
    after_picture=[('types', 'Types, one by one', 'Four provisioning methods and five migration types, one by one', build_types(GOLD, MGA))], lv='',
    myth_rows=[('Live migration copies the disk.', 'Usually only memory and state; the disk is on shared storage.', 'Live migration animation.'), ('Each new cloud VM copies the whole image first.', 'Root disks are created lazily from snapshots.', 'Deep dive.'), ('Stop/start is the same as reboot.', 'Stop/start can move hosts and change the public IP.', 'Lifecycle figure.')],
    extra_secs=[('deep', 'Deep dive', 'What moves in a live migration, cloud host maintenance, lazy AMI loading, bake vs fry', DEEP)],
    clouds_html=clouds, proof_h2='Real proof: clone, snapshot and convert VM disks', proof_intro='All outputs are real, from our Ubuntu 24.04 lab machine on 10 Nov 2026 (qemu-img; the image size is read live from cloud-images.ubuntu.com).', proof_steps=proof,
    practical_html=PRAC, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Do each practical step both in a UI (VirtualBox, EC2 console) and with the CLI.', 'Compare four provisioning methods and explain golden images, linked clones and cloud-init.', 'Draw the VM lifecycle and map it to EC2 states and billing.', 'Explain cold, live (pre-copy/post-copy), storage, P2V/V2V and cloud migration.', 'Choose a strategy from the 7 Rs and the matching AWS/Azure/GCP service.', 'Bake an AMI, copy it across Regions and launch identical instances with the AWS CLI.'],
    next_html='<a href="../05-virtualization-vs-cloud-vs-containers/">4.5 Virtualization vs cloud vs containers</a>.',
    pre='<b>Before you start:</b> <a href="../03-network-storage-and-data-virtualization/">4.3 Network, storage and data virtualization</a> and <a href="../../02-service-models/01-iaas-infrastructure-as-a-service/">2.1 IaaS (EC2)</a>.')
