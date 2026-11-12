import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)


hk = hook('TiffinGo stores order records, a shared “recipes” folder, 3 TB of food photos, seven-year-old GST invoices and nightly backups. Can one kind of cloud storage do all of that well?',
    'No — clouds sell storage in different <b>shapes</b>: <b>block</b> disks for servers, shared <b>file</b> systems, <b>object</b> storage for unlimited files over HTTPS, cheap <b>archive</b> tiers, fast but temporary <b>local</b> disks, <b>snapshots and backups</b>, and services to move data in from offices and data centres. Each has a different speed, durability and price — Mumbai prices go from $0.025 to $0.0045 per GB-month for the same photo. This lesson explains every shape, shows what happens inside S3 when you upload a file, and walks you through buckets, lifecycle rules, disks, snapshots and share links on <b>your own</b> AWS, Azure or Google Cloud account.',
    ['Seven kinds of cloud storage — and which job each is for.', 'Why S3 promises 11 nines of durability, and what that really means.', 'How to share a private file for one hour without making it public.'])

def story_scene():
    o = t(180, 12, 'Five kinds of data, five storage needs', 9, 'ink', bold=True)
    items = [('Orders DB', 'fast disk', 'blue'), ('Recipes', 'shared folder', 'violet'), ('Photos', '3 TB, web', 'green'), ('Invoices', 'keep 7 yrs', 'amber'), ('Backups', 'nightly', 'red')]
    for i, (n, s, tn) in enumerate(items):
        x = 6 + i * 70
        o += box(x, 26, 64, 64, tn, rx=8) + t(x + 32, 52, n, 7.2, 'ink', bold=True) + t(x + 32, 70, s, 6.6, 'ink2')
    o += t(180, 112, 'Speed, sharing, size, price and retention differ — so does the right storage.', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Five boxes: orders database needs a fast disk, recipes need a shared folder, 3 TB of photos for the web, invoices kept seven years, nightly backups.', story_scene(), 'Choose storage by <tspan font-weight="700" class="s-acc">how the data is used</tspan>.', h=130)
dialogue = '''R> Sir, the server disk is full again. Let’s just buy a bigger disk and put everything on it.
A> The database needs a fast disk, yes. But 3 TB of photos on a server disk means paying for SSD and serving every photo through our server.
K> Then where do photos go?
A> Object storage — S3, Blob Storage or Cloud Storage. Unlimited size, served over HTTPS, and old photos can slide to a cheaper tier automatically.
R> And the 2019 invoices nobody opens?
A> Archive tier — a fraction of the price, slower to read. And backups as snapshots in another place. Different data, different storage. Let’s see them all.'''

# ------------------------------------------------------------------ picture
def shapesfig():
    o = t(320, 16, 'Three ways to store bytes: block, file, object', 11, 'ink', bold=True)
    cols = [('BLOCK', 'blue', 'a raw disk attached to ONE server', ['server sees /dev/nvme1n1', 'you format it (ext4, NTFS)', 'fast, low latency (IOPS)'], 'EBS · Managed Disks · Persistent Disk'),
            ('FILE', 'violet', 'a shared folder for MANY servers', ['mount over NFS / SMB', 'folders, permissions, locks', 'many servers at once'], 'EFS/FSx · Azure Files · Filestore'),
            ('OBJECT', 'green', 'files + metadata in a bucket, over HTTPS', ['PUT / GET by key (URL)', 'no folders really, no edits', 'unlimited size, cheapest'], 'S3 · Blob Storage · Cloud Storage')]
    for i, (n, tn, d, ls, ex) in enumerate(cols):
        x = 12 + i * 208
        o += box(x, 30, 200, 194, tn, rx=10) + t(x + 100, 50, n, 11, 'ink', bold=True) + t(x + 100, 68, d, 7.2, 'ink2')
        if i == 0:
            o += box(x + 60, 80, 80, 28, 'card', rx=4) + t(x + 100, 98, 'server', 7.4, 'ink') + arrow(x + 100, 110, x + 100, 124) + cyl(x + 76, 126, 48, 30, 'disk', 'card')
        elif i == 1:
            for j in range(3): o += box(x + 14 + j * 60, 80, 52, 24, 'card', rx=4) + t(x + 40 + j * 60, 96, 'server', 7, 'ink') + arrow(x + 40 + j * 60, 106, x + 100, 124)
            o += box(x + 64, 126, 72, 30, 'card', rx=4) + t(x + 100, 145, '/shared', 7.4, 'ink', mono=True)
        else:
            o += box(x + 20, 80, 70, 24, 'card', rx=4) + t(x + 55, 96, 'app / browser', 6.8, 'ink') + arrow(x + 92, 92, x + 118, 92) + t(x + 105, 86, 'HTTPS', 6, 'ink2')
            o += box(x + 120, 78, 66, 78, 'card', rx=6) + t(x + 153, 92, 'bucket', 7, 'ink', bold=True)
            for j in range(3): o += box(x + 128, 98 + j * 18, 50, 14, 'green', rx=2)
        for j, l in enumerate(ls): o += t(x + 100, 172 + j * 13, l, 7, 'ink')
        o += t(x + 100, 216, ex, 6.4, 'ink2', bold=True)
    o += t(320, 244, 'Rule of thumb: databases and OS → block · shared app folders → file · media, data lakes, backups, websites → object.', 7.6, 'ink2')
    return o
SHAPES = bigfig('Three columns: block storage is a raw disk attached to one server; file storage is a shared folder mounted by many servers; object storage keeps files with metadata in a bucket accessed over HTTPS.', shapesfig(), h=254)

def tiersfig():
    o = t(320, 16, 'Hot to cold: the same photo, six price points (S3, Mumbai, $ per GB-month, Nov 2026)', 10, 'ink', bold=True)
    rows = [('S3 Standard', 0.025, 'ms access · no minimum', 'red'), ('Standard-IA', 0.0138, 'ms · 30-day min · retrieval fee', 'amber'), ('One Zone-IA', 0.011, 'ms · one AZ only', 'amber'),
            ('Glacier Instant Retrieval', 0.005, 'ms · 90-day min · higher fee', 'blue'), ('Glacier Flexible Retrieval', 0.0045, 'minutes–hours · 90-day min', 'blue'), ('Glacier Deep Archive', None, 'hours (12–48) · 180-day min · cheapest', 'violet')]
    for i, (n, p, s, tn) in enumerate(rows):
        y = 32 + i * 34; w = (p or 0.0018) / 0.025 * 300
        o += t(176, y + 16, n, 8, 'ink', anchor='end', bold=True) + box(184, y, w, 24, tn, rx=4)
        o += t(190 + w, y + 16, (f'${p}' if p else 'lowest tier') + '  ·  ' + s, 7.4, 'ink', anchor='start')
    o += t(320, 248, 'Cheaper to store = slower or costlier to read, with a minimum storage period. Lifecycle rules move objects down automatically.', 7.6, 'ink2')
    return o
TIERS = bigfig('Bar chart of S3 storage classes in Mumbai: Standard $0.025, Standard-IA $0.0138, One Zone-IA $0.011, Glacier Instant Retrieval $0.005, Glacier Flexible Retrieval $0.0045, and Deep Archive the lowest tier with 12–48 hour retrieval.', tiersfig(), h=258)

picture = ('  <p>First the three basic <b>shapes</b> of storage — how a program actually reaches the bytes:</p>\n' + SHAPES +
           '\n  <p>Then the <b>temperature</b> ladder inside object storage — real Mumbai prices from AWS’s price file:</p>\n' + TIERS)

# ------------------------------------------------------------------ how: an S3 upload
RN = {'app': (4, 54, 54, 50, 'phone', 'App', 'PUT photo'), 'fe': (66, 4, 60, 46, 'globe', 'S3 endpoint', 'HTTPS'), 'auth': (66, 104, 60, 46, 'shield', 'Auth', 'IAM + policy'),
      'idx': (138, 54, 62, 50, 'dns', 'Index', 'key → location'), 'az1': (212, 4, 64, 46, 'disk', 'AZ a', 'pieces'), 'az2': (212, 104, 64, 46, 'disk', 'AZ b · c', 'pieces'), 'ok': (290, 54, 66, 50, 'chart', '200 OK', 'ETag')}
RS = [dict(on=['app', 'fe'], hot='fe', move=(58, 70, 70, 40, 'PUT'), head='Step 1 · An HTTPS PUT to the bucket', text='The app sends PUT /photos/thali.jpg to tiffingo-photos.s3.ap-south-1.amazonaws.com', text2='with the bytes, headers (content type, metadata) and a signature.', svc='Same for Azure Blob (PUT Blob) and Cloud Storage (JSON/XML API)'),
      dict(on=['app', 'fe', 'auth'], hot='auth', move=(96, 50, 96, 104, 'check'), head='Step 2 · Who are you, may you write?', text='The signature proves identity; IAM policies, the bucket policy and Block Public', text2='Access settings are evaluated. Encryption (SSE-S3 by default) is applied.', svc='403 AccessDenied comes from this step'),
      dict(on=['app', 'fe', 'auth', 'idx'], hot='idx', move=(126, 127, 150, 90, ''), head='Step 3 · The key goes into the index', text='S3 records key → where the pieces live. “Folders” are just a prefix in the key', text2='(photos/2026/thali.jpg) — there is no real directory tree.', svc='Keys, prefixes, metadata, version ID (if versioning is on)'),
      dict(on=['app', 'fe', 'auth', 'idx', 'az1', 'az2'], hot='az2', move=(200, 70, 222, 120, 'copy'), head='Step 4 · Stored redundantly across AZs', text='The data is split, protected with erasure coding and spread over devices in at', text2='least three AZs (S3 Standard) before the write is confirmed.', svc='Designed for 99.999999999% (11 nines) durability'),
      dict(on=list(RN), hot='ok', move=(276, 127, 298, 90, ''), head='Step 5 · 200 OK with an ETag', text='Only now does S3 reply 200 OK. Since Dec 2020 every later GET or LIST sees the', text2='new object immediately — strong read-after-write consistency.', svc='Lifecycle rules may later move it to IA or Glacier automatically')]
UPLOAD = flow_anim('What happens when you upload a photo to S3', 'Five steps between your PUT and a durable object.', 'Object upload', 'Animation: an app sends an HTTPS PUT; authentication and policies are checked; the key is indexed; data is stored redundantly across availability zones; S3 returns 200 OK with an ETag.', RN, RS, hid='s3flow')

# ------------------------------------------------------------------ types
def mapfig():
    o = t(320, 16, 'Seven kinds of cloud storage', 11, 'ink', bold=True)
    items = [('1', 'Block storage', 'EBS · Managed Disks · PD', 'blue'), ('2', 'File storage', 'EFS/FSx · Files · Filestore', 'violet'), ('3', 'Object storage', 'S3 · Blob · Cloud Storage', 'green'),
             ('4', 'Archive / cold tiers', 'Glacier · Archive · Archive class', 'amber'), ('5', 'Local (ephemeral) disks', 'instance store · temp disk · Local SSD', 'red'), ('6', 'Snapshots & backup', 'AWS Backup · Azure Backup · Backup and DR', 'blue'), ('7', 'Hybrid & data transfer', 'gateways, DataSync, Data Box', 'violet')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 7.8, 'ink', bold=True) + t(x + 78, y + 54, b, 6.2, 'ink2')
    o += t(320, 210, '1–3 are the basic shapes · 4–5 are the coldest and the fastest · 6–7 protect and move data.', 7.6, 'ink2')
    return o
MAP = bigfig('Map of seven storage types: 1 block, 2 file, 3 object, 4 archive and cold tiers, 5 local ephemeral disks, 6 snapshots and backup, 7 hybrid storage and data transfer.', mapfig(), h=222)

def a_blk(k):
    o = t(180, 12, ['Create a volume in an AZ', 'Attach, format, mount', 'Grow it while running'][k], 9, 'ink', bold=True)
    o += box(14, 30, 150, 96, 'card', rx=8) + t(89, 44, 'AZ ap-south-1a', 7, 'ink2')
    o += box(30, 54, 118, 28, 'blue' if k else 'card', rx=4) + t(89, 72, 'EC2 instance' if k else '(server)', 7.4, 'ink')
    o += cyl(60, 90, 60, 30, ['gp3 20 GiB', 'gp3 20 GiB', 'gp3 50 GiB'][k], 'amber' if k != 2 else 'green')
    if k: o += arrow(89, 84, 89, 90)
    o += box(186, 30, 160, 96, 'card', rx=8)
    o += t(266, 52, ['aws ec2 create-volume', 'mkfs.ext4 /dev/nvme1n1', 'modify-volume --size 50'][k], 7.4, 'ink', bold=True, mono=True)
    o += t(266, 76, ['--size 20 --volume-type gp3', 'mount /dev/nvme1n1 /data', 'growpart + resize2fs'][k], 7, 'ink', mono=True)
    o += t(266, 100, ['lives in ONE AZ', 'one server at a time*', 'no downtime'][k], 7.4, 'ink2')
    o += t(180, 146, ['a raw disk, replicated inside its AZ', 'the OS sees a new disk and uses it like a local one', 'size, IOPS and throughput can change online'][k], 7.2, 'ink', bold=True)
    return o
A_BLK = cap([a_blk(k) for k in range(3)], [('Create', 'A volume is created in one AZ with a size and type (e.g. gp3 SSD).', ''), ('Attach and mount', 'Attached to an instance in the same AZ; the OS formats and mounts it.', ''), ('Modify', 'Size and performance can be raised while the disk is in use; then grow', 'the file system.')],
    'Block storage in action', 'A network disk for one server.', 'Block storage', 'Animation: a gp3 volume created in an AZ; attached to an EC2 instance, formatted and mounted; grown from 20 to 50 GiB online.', 's1anim')
T1 = vtype(1, 'Block storage (cloud disks)', 'blue',
    '<b>Block storage</b> provides raw storage volumes, divided into fixed-size blocks, that are attached to a server over the provider’s network and appear to the operating system as a local disk, which it formats with a file system. Volumes persist independently of the server, are replicated within one Availability Zone, and are sized and priced by capacity and performance (IOPS, throughput).',
    'A pen drive that only one laptop can use at a time — but stored in a safe locker room next door and copied automatically so it does not die.',
    'TiffinGo’s PostgreSQL server keeps its data on a 100 GiB gp3 EBS volume (3,000 IOPS baseline). Before Diwali they raise IOPS to 6,000 without downtime, and a daily snapshot goes to S3-backed storage.',
    'Amazon EBS (gp3, io2, st1, sc1), Azure Managed Disks (Standard HDD/SSD, Premium SSD v2, Ultra), Google Persistent Disk and Hyperdisk.',
    '', A_BLK,
    'a single server needs a fast, persistent disk — OS disks, databases, anything that expects a hard drive.',
    'many servers must share the same files (use file storage) or you want to serve files to the internet (use object storage).',
    plain='A hard disk in the cloud. You attach it to one server; the server uses it like its own disk. If the server is deleted, the disk can survive.',
    how=[('Create', 'Pick the AZ, size and type; the volume is replicated across devices inside that AZ.'), ('Attach', 'The hypervisor (Nitro card on AWS) presents it as an NVMe device to the VM.'), ('Use', 'The OS formats it (ext4, xfs, NTFS) and reads/writes blocks over the network.'), ('Performance', 'gp3: 3,000 IOPS and 125 MB/s baseline, raised independently of size; io2 for very high IOPS.'), ('Protect', 'Snapshots copy changed blocks incrementally to regional storage (type 6).')],
    words=[('block', 'a small fixed-size piece of a disk'), ('IOPS', 'input/output operations per second — how many small reads/writes'), ('throughput', 'MB per second for big reads/writes'), ('mount', 'connect a disk to a folder in the OS')],
    diff=table(['', 'Block', 'File', 'Object'], [['Accessed as', 'a disk (/dev/…)', 'a folder (NFS/SMB)', 'URLs over HTTPS'], ['Shared by', 'one server (multi-attach is rare)', 'many servers', 'any number of clients'], ['Edit part of a file', 'yes', 'yes', 'no — replace the whole object'], ['Scope', 'one AZ', 'Region (or one AZ)', 'Region (or multi-Region)']], minw=560),
    where=['Boot/OS disks of every VM', 'Self-managed databases', 'Applications that expect a local file system'],
    realworld='Amazon EBS launched in 2008; its <b>gp3</b> type (2020) separated performance from size — before that, gp2 IOPS grew only with disk size, so people bought huge disks just for speed.',
    pro='An EBS volume lives in one AZ — you cannot attach a 1a volume to a 1b instance. To move it, snapshot (regional) and create a new volume in the other AZ. Azure ZRS disks and Google regional persistent disks are exceptions that replicate synchronously across two or three zones.')

def a_file(k):
    o = t(180, 12, ['One file system', 'Many servers mount it', 'Grows and shrinks by itself'][k], 9, 'ink', bold=True)
    o += box(120, 96, 120, 40, 'violet', rx=8) + t(180, 114, 'EFS / Azure Files', 7.6, 'ink', bold=True) + t(180, 128, ['empty', '/recipes shared', '0.5 → 40 GB used'][k], 6.8, 'ink2')
    if k >= 1:
        for i in range(3):
            o += box(20 + i * 120, 30, 80, 30, 'blue', rx=4) + t(60 + i * 120, 49, ['web 1a', 'web 1b', 'report'][i], 7.2, 'ink') + arrow(60 + i * 120, 62, 180, 94)
        o += t(180, 80, 'NFS / SMB', 6.8, 'ink2')
    o += t(180, 152, ['a managed network file system in your VPC', 'all see the same files, with locks and permissions', 'pay per GB stored (and throughput mode)'][k], 7.2, 'ink', bold=True)
    return o
A_FILE = cap([a_file(k) for k in range(3)], [('Create', 'A managed file system with mount targets in your network.', ''), ('Mount', 'Several servers, in different AZs, mount it over NFS or SMB and share files.', ''), ('Elastic', 'Capacity grows and shrinks with your files — no disk sizing.', '')],
    'File storage in action', 'One shared folder for many servers.', 'File storage', 'Animation: a managed file system; three servers mount it over NFS or SMB; capacity grows automatically.', 's2anim')
T2 = vtype(2, 'File storage (managed network file systems)', 'violet',
    '<b>Cloud file storage</b> is a managed, shared file system accessed over network file protocols — <b>NFS</b> (Linux) or <b>SMB</b> (Windows) — that many servers can mount at the same time, with a familiar hierarchy of folders, file permissions and locking.',
    'The shared “Recipes” almirah in the office kitchen: every cook can open the same files, and the almirah grows if you add more.',
    'TiffinGo’s web servers in two AZs show recipe PDFs uploaded by kitchen managers; both read and write the same <code>/recipes</code> folder on Amazon EFS, so a PDF uploaded through one server is visible on the other at once.',
    'Amazon EFS (NFS), Amazon FSx (Windows File Server, NetApp ONTAP, Lustre, OpenZFS); Azure Files (SMB/NFS), Azure NetApp Files; Google Filestore, Google Cloud NetApp Volumes.',
    '', A_FILE,
    'several servers or containers need the same files, or a lift-and-shift app expects a shared drive or home directories.',
    'only one server uses the data (block is cheaper and faster) or files are served to users on the internet (object is far cheaper).',
    plain='A shared network folder in the cloud. Many servers can open the same files at the same time, just like a shared drive in an office.',
    how=[('Create', 'A file system in a Region (or one AZ for cheaper options).'), ('Mount targets', 'Network endpoints in your subnets, protected by security groups.'), ('Mount', '<code>mount -t nfs4 …</code> on Linux or map a drive letter (SMB) on Windows.'), ('Consistency', 'Locks and close-to-open consistency let many clients work safely.'), ('Billing', 'Per GB-month stored (EFS) or per provisioned capacity (Filestore, FSx, Azure Files premium).')],
    words=[('NFS', 'Network File System — Linux file sharing protocol'), ('SMB', 'Server Message Block — Windows file sharing protocol'), ('mount target', 'the network address servers use to reach the file system'), ('Lustre', 'a very fast file system for HPC')],
    diff=table(['', 'EFS / Azure Files / Filestore', 'EBS-type block disk', 'S3-type object'], [['Many servers at once', 'yes', 'no', 'yes (via API)'], ['Protocol', 'NFS / SMB', 'block device', 'HTTPS'], ['Typical price per GB', 'higher', 'medium', 'lowest']], minw=520),
    where=['Shared content for web farms', 'Home directories, lift-and-shift Windows shares', 'HPC and ML training data (FSx for Lustre)'],
    realworld='Amazon FSx for NetApp ONTAP and Azure NetApp Files run NetApp’s storage OS as a managed cloud service — enterprises move existing NAS workloads to the cloud without changing how applications see their files.',
    pro='EFS Standard stores data across multiple AZs, so it is regional, but a mount target sits in one AZ — clients should mount the target in their own AZ to avoid cross-AZ latency and data transfer charges.')

def a_obj(k):
    o = t(180, 12, ['Create a bucket', 'PUT objects by key', 'GET by URL — public only if allowed'][k], 9, 'ink', bold=True)
    o += box(150, 30, 196, 100, 'green', rx=10) + t(248, 46, 'bucket: tiffingo-photos', 7.6, 'ink', bold=True)
    objs = ['photos/2026/thali.jpg', 'photos/2026/poha.jpg', 'menu/diwali.pdf']
    for i in range([0, 3, 3][k]): o += box(160, 56 + i * 22, 176, 18, 'card', rx=3) + t(248, 69 + i * 22, objs[i], 6.8, 'ink', mono=True)
    if k == 0: o += t(248, 88, 'name is global; data stays in Mumbai', 7, 'ink')
    o += box(14, 54, 110, 46, 'blue', rx=8) + t(69, 74, ['console / CLI', 'app (SDK)', 'browser'][k], 7.6, 'ink', bold=True) + t(69, 90, ['create', 'PUT', 'GET (signed URL)'][k], 7, 'ink2')
    o += arrow(126, 77, 148, 77)
    o += t(180, 150, ['unique name, one Region, private by default', '“folders” are only prefixes in the key', 'Block Public Access stays on; share with signed URLs'][k], 7.2, 'ink', bold=True)
    return o
A_OBJ = cap([a_obj(k) for k in range(3)], [('Bucket', 'A container with a globally unique name in one Region; private by default.', ''), ('Objects', 'Each object = key + data + metadata, written with PUT; prefixes look like folders.', ''), ('Access', 'Objects are read with GET over HTTPS — by apps with credentials, or by anyone', 'holding a time-limited signed URL.')],
    'Object storage in action', 'Unlimited files over HTTPS.', 'Object storage', 'Animation: a bucket created; objects uploaded by key; read over HTTPS with signed URLs while the bucket stays private.', 's3anim')
T3 = vtype(3, 'Object storage', 'green',
    '<b>Object storage</b> stores data as <b>objects</b> — the bytes, a unique key and metadata — in flat containers called <b>buckets</b> (S3, Cloud Storage) or <b>containers</b> in a storage account (Azure Blob), accessed through an HTTPS API, scaling to virtually unlimited capacity with very high durability and the lowest price per GB.',
    'A cloak room with token numbers: you hand over a bag, get a token (key), and later get the same bag back by showing the token — you never walk into the room or rearrange shelves.',
    'TiffinGo keeps 3 TB of food photos in an S3 bucket in Mumbai (≈ $77 a month at $0.025/GB). The mobile app uploads directly to S3 with short-lived signed URLs, and CloudFront serves the photos to customers.',
    'Amazon S3, Azure Blob Storage (in a storage account), Google Cloud Storage; S3-compatible stores such as MinIO on-premises.',
    '', A_OBJ,
    'media, documents, logs, backups, data lakes, static websites — anything written once and read many times.',
    'you need to edit parts of a file in place or run a database on it (use block), or need a POSIX file system (use file).',
    plain='A giant online store for files of any size. Each file gets a name (key); programs save and fetch files over the internet; you never run out of space.',
    how=[('Bucket', 'Create it in a Region with a globally unique name.'), ('PUT', 'Upload an object with a key; metadata and encryption are applied (see “How it works”).'), ('Durable copies', 'S3 Standard spreads data over ≥3 AZs; Azure LRS keeps 3 copies in one datacentre, ZRS across zones, GRS also in the paired Region.'), ('GET / LIST', 'Read by key; list by prefix; byte-range reads for big files.'), ('Manage', 'Versioning, lifecycle rules, replication, access policies, event notifications.')],
    words=[('object', 'a file plus its name and labels'), ('bucket', 'a top-level container for objects'), ('key', 'the object’s full name, e.g. photos/2026/thali.jpg'), ('durability', 'the chance your data is NOT lost — different from availability'), ('ETag', 'a fingerprint of the object that S3 returns after an upload'), ('erasure coding', 'splitting data into pieces plus spare pieces so lost ones can be rebuilt')],
    diff=table(['', 'Amazon S3', 'Azure Blob Storage', 'Google Cloud Storage'], [['Container', 'bucket', 'storage account → container', 'bucket'], ['Hot / cool / cold / archive', 'Standard / IA / Glacier IR / Glacier', 'Hot / Cool / Cold / Archive', 'Standard / Nearline / Coldline / Archive'], ['Multi-location option', 'Cross-Region Replication', 'GRS / GZRS', 'dual- and multi-region buckets']], minw=600),
    where=['Images, videos and downloads for apps', 'Data lakes for analytics (Athena, Synapse, BigQuery)', 'Backups, logs and static websites'],
    realworld='Amazon S3 launched on 14 March 2006 as AWS’s first generally available service; it is designed for 99.999999999% durability — if you store 10 million objects, you can expect to lose one about every 10,000 years.',
    pro='S3 became <b>strongly consistent</b> for all operations in December 2020 — before that, overwrites and deletes were only eventually consistent, and big data tools needed add-ons (like EMRFS consistent view) to avoid reading stale files.')

def a_arc(k):
    o = t(180, 12, ['Day 0: Standard', 'Day 30: lifecycle moves it', 'Day 365: archive — restore before reading'][k], 9, 'ink', bold=True)
    tiers = [('Standard', 'red'), ('IA', 'amber'), ('Archive', 'violet')]
    for i, (n, tn) in enumerate(tiers):
        x = 20 + i * 112
        o += box(x, 40, 100, 70, tn if i == k else 'card', rx=8) + t(x + 50, 64, n, 8, 'ink', bold=True)
        if i == k: o += box(x + 30, 74, 40, 26, 'green', rx=3) + t(x + 50, 91, 'invoice', 6.4, 'ink')
        if i < 2: o += arrow(x + 102, 75, x + 110, 75)
    o += t(180, 132, ['$0.025/GB-month, read any time', '$0.0138, read in ms, small retrieval fee', 'lowest price; restore takes minutes to hours'][k], 7.4, 'ink')
    o += t(180, 150, ['new invoice, opened often', 'rarely opened after a month', 'kept for 7-year GST rules, almost never read'][k], 7.2, 'ink', bold=True)
    return o
A_ARC = cap([a_arc(k) for k in range(3)], [('Hot', 'New data sits in the standard (hot) class.', ''), ('Cooler', 'A lifecycle rule moves it to an infrequent-access class after 30 days.', ''), ('Archive', 'After a year it moves to an archive class: cheapest storage, but you must', 'restore it (minutes to hours) before reading.')],
    'Archive tiers in action', 'Data cools down — and its price follows.', 'Archive storage', 'Animation: an invoice in standard storage; moved to infrequent access after 30 days; moved to archive after a year.', 's4anim')
T4 = vtype(4, 'Cold and archive storage tiers', 'amber',
    '<b>Archive and cold storage</b> classes keep rarely accessed data at a much lower price per GB in exchange for <b>higher retrieval cost, slower access</b> (from milliseconds to hours) and a <b>minimum storage duration</b>; <b>lifecycle policies</b> move objects between classes automatically by age.',
    'Old school certificates: last year’s marksheet stays in the drawer, the Class 10 one goes to a trunk in the loft — cheap to keep, but you need a ladder and time to get it.',
    'TiffinGo must keep GST invoices for years. A lifecycle rule moves invoice PDFs to Standard-IA after 30 days and to Glacier Deep Archive after a year; an auditor’s request is restored within 12 hours.',
    'S3 Standard-IA, One Zone-IA, Glacier Instant/Flexible Retrieval, Glacier Deep Archive, Intelligent-Tiering; Azure Blob Cool, Cold and Archive tiers; Google Nearline, Coldline and Archive classes.',
    '', A_ARC,
    'data is kept for compliance, backup or history and read rarely — logs, old invoices, raw video, old backups.',
    'data is read often or deleted soon — retrieval fees and minimum durations can make “cheap” tiers more expensive.',
    plain='Cheaper shelves for data you almost never open. Storing is very cheap, but getting the data back is slower and costs a little.',
    how=[('Classes', 'Each class has a storage price, retrieval price, access time and minimum duration.'), ('Lifecycle rule', 'E.g. “after 30 days → IA, after 365 days → Deep Archive, delete after 8 years”.'), ('Transition', 'The service moves objects in the background; the key stays the same.'), ('Restore', 'Archive objects need a restore request (expedited/standard/bulk) before GET.'), ('Auto-tiering', 'S3 Intelligent-Tiering moves objects by observed access, for a small monitoring fee.')],
    words=[('lifecycle rule', 'automatic “move or delete after N days” instruction'), ('retrieval fee', 'charge per GB read from a cold class'), ('minimum duration', 'you pay for at least this many days even if you delete earlier'), ('rehydrate / restore', 'bring archived data back to a readable tier')],
    diff=table(['Cloud', 'Cool (≈30-day min)', 'Cold (≈90-day min)', 'Archive (hours to read)'], [['AWS', 'S3 Standard-IA', 'Glacier Instant / Flexible Retrieval', 'Glacier Deep Archive (180-day min)'], ['Azure', 'Cool', 'Cold', 'Archive (180-day min)'], ['Google', 'Nearline (30)', 'Coldline (90)', 'Archive (365-day min, but read in ms)']], minw=600),
    where=['Compliance archives (tax, health, banking)', 'Old backups and logs', 'Media archives and raw research data'],
    realworld='Google Cloud’s Archive class is unusual: data is available in milliseconds like its other classes, but with the highest retrieval fee and a 365-day minimum — AWS Deep Archive and Azure Archive instead require a restore that takes hours.',
    pro='Lifecycle transitions themselves cost money per 1,000 objects. Millions of tiny objects moved to Glacier can cost more in transition requests than you save — S3 by default no longer transitions objects smaller than 128 KB for this reason.')

def a_eph(k):
    o = t(180, 12, ['Disk inside the host', 'Very fast scratch space', 'Stop or host fails → data gone'][k], 9, 'ink', bold=True)
    o += box(40, 30, 280, 100, 'card', rx=10) + t(180, 46, 'physical host', 7, 'ink2')
    o += box(60, 56, 110, 34, 'blue' if k < 2 else 'card', rx=4) + t(115, 77, 'your VM' if k < 2 else '(VM stopped)', 7.4, 'ink')
    o += box(190, 56, 110, 60, 'red' if k < 2 else 'card', rx=4) + t(245, 80, 'local NVMe SSD', 7.4, 'ink', bold=True) + t(245, 98, ['instance store', 'cache · temp · shuffle', 'wiped'][k], 7, 'ink2')
    if k == 1: o += arrow(172, 73, 188, 80)
    o += t(180, 150, ['physically attached to the server, not over the network', 'millions of IOPS, no extra charge (included in the price)', 'never keep the only copy of anything here'][k], 7.2, 'ink', bold=True)
    return o
A_EPH = cap([a_eph(k) for k in range(3)], [('Local disk', 'Some instance types include NVMe SSDs physically inside the host.', ''), ('Fast scratch', 'Very low latency and high IOPS — ideal for caches, temp files, Spark', 'shuffle.'), ('Ephemeral', 'Stop, terminate or a host failure wipes it. Reboot keeps it.', '')],
    'Ephemeral storage in action', 'Fast, free with the instance — and temporary.', 'Instance store', 'Animation: a VM with a local NVMe disk on the same host; used as fast scratch space; data wiped when the VM stops.', 's5anim')
T5 = vtype(5, 'Local (ephemeral) instance storage', 'red',
    '<b>Ephemeral (instance) storage</b> is disk physically attached to the host that runs a VM — <b>instance store</b> on AWS, the <b>temporary disk</b> on Azure, <b>Local SSD</b> on Google Cloud — offering very high performance at no or low extra cost, but whose data is lost when the instance stops, is terminated, or the host fails.',
    'A whiteboard in the meeting room: fastest to write on, perfect during the meeting — and wiped clean when the next team comes in.',
    'TiffinGo’s nightly report runs Spark on i4i instances: shuffle files go to the local NVMe disks for speed; inputs and final results live in S3, so losing a node only means re-running a task.',
    'EC2 instance store (i4i, c7gd, m7gd…), Azure temporary disk (D: on Windows, /mnt on Linux) and local NVMe on L-series, Google Local SSD.',
    '', A_EPH,
    'data is temporary or can be rebuilt — caches, buffers, scratch space, replicated databases (Cassandra, Kafka with replicas).',
    'you need the data after a stop or failure — use block storage or replicate it elsewhere.',
    plain='A very fast disk inside the same machine as your server. Great for temporary work; everything on it disappears if the server stops.',
    how=[('Included', 'Comes with certain instance types (a “d” in the name, e.g. m7gd, or i-family).'), ('Attached locally', 'NVMe directly on the host — no network hop.'), ('Use', 'Format and mount like any disk (some AMIs do it automatically).'), ('Survives reboot', 'A reboot keeps data; stop/hibernate/terminate or host failure erases it.'), ('Protect by design', 'Replicate across nodes or keep the source of truth in S3/EBS.')],
    words=[('ephemeral', 'temporary — lasts only as long as the instance'), ('NVMe', 'a very fast interface for SSDs'), ('scratch space', 'a place for temporary working files'), ('shuffle', 'data exchanged between nodes in Spark/Hadoop jobs')],
    diff=table(['', 'Instance store / Local SSD', 'Block volume (EBS/PD)'], [['Survives stop', 'no', 'yes'], ['Latency', 'lowest (local)', 'low (network)'], ['Extra charge', 'none on AWS (in instance price)', 'per GB-month'], ['Snapshots', 'no', 'yes']], minw=460),
    where=['Big-data scratch (Spark, Hadoop)', 'Caches and buffers', 'Distributed databases with replicas'],
    realworld='Azure VMs show a temporary disk with a file called <b>DATALOSS_WARNING_README.txt</b> on Windows — Microsoft’s blunt reminder that anything there can vanish during maintenance or resizing.',
    pro='Hadoop/HDFS on cloud VMs often used instance store with 3× replication. Modern cloud data platforms (EMR, Dataproc, Databricks) instead keep data in object storage and use local disks only for shuffle — separating storage from compute so clusters can be deleted.')

def a_bak(k):
    o = t(180, 12, ['Day 1: full snapshot', 'Day 2+: only changed blocks', 'Backup plan: schedule, retention, copy'][k], 9, 'ink', bold=True)
    o += cyl(20, 50, 70, 46, 'EBS 100 GiB', 'blue')
    if k < 2:
        o += arrow(92, 73, 128, 73)
        for i in range(10):
            ch = k == 0 or i in (2, 7)
            o += box(132 + i * 21, 58, 18, 30, 'green' if ch else 'card', rx=2)
        o += t(237, 104, ['all used blocks copied (e.g. 40 GB)', 'only 2 changed blocks copied (e.g. 3 GB)'][k], 7, 'ink')
    else:
        for i, (n, tn) in enumerate([('daily 2 a.m.', 'amber'), ('keep 35 days', 'blue'), ('copy → Hyderabad', 'violet')]):
            o += box(110 + i * 80, 52, 74, 46, tn, rx=6) + t(147 + i * 80, 79, n, 6.8, 'ink', bold=True)
    o += t(180, 140, ['stored in regional (S3-backed) storage, not in the AZ', 'incremental = fast and cheap; each snapshot still restores fully', 'AWS Backup / Azure Backup / Backup and DR automate it'][k], 7.2, 'ink', bold=True)
    return o
A_BAK = cap([a_bak(k) for k in range(3)], [('First snapshot', 'A full point-in-time copy of the used blocks, stored regionally.', ''), ('Incremental', 'Later snapshots copy only blocks changed since the last one — yet any snapshot', 'restores the complete disk.'), ('Backup plan', 'A policy schedules backups, keeps them for N days and copies them to another', 'Region or account.')],
    'Snapshots and backup in action', 'Point-in-time copies, incremental and automated.', 'Backup', 'Animation: a full first snapshot of a disk; later snapshots copy only changed blocks; a backup plan with schedule, retention and cross-Region copy.', 's6anim')
T6 = vtype(6, 'Snapshots and backup', 'blue',
    'A <b>snapshot</b> is a point-in-time, usually incremental copy of a volume or file system stored in durable regional storage; <b>backup services</b> automate snapshots and other copies with schedules, retention, encryption, cross-Region/account copies and restore testing, often across many services (VMs, disks, databases, file systems).',
    'Taking a photo of your whiteboard every evening: tomorrow you only need to note what changed, but any photo shows the whole board as it was.',
    'TiffinGo’s backup plan snapshots the database volume every night at 2 a.m., keeps 35 days, and copies weekly backups to the Hyderabad Region and a separate “backup” AWS account — so a ransomware attack on the main account cannot delete them.',
    'EBS snapshots, AWS Backup (with Vault Lock); Azure Backup, Recovery Services vaults; Google Cloud Backup and DR, persistent disk snapshots.',
    '', A_BAK,
    'any data you cannot afford to lose — databases, VM disks, file systems — with retention matching business and legal needs.',
    'you treat replication as backup: replication copies mistakes and deletions too; backups let you go back in time.',
    plain='Automatic “save points” of your disks and databases. If something breaks or is deleted, you go back to yesterday’s save point.',
    how=[('Point in time', 'The snapshot captures the volume at one moment (crash-consistent; app-consistent with agents).'), ('Incremental', 'Only blocks changed since the previous snapshot are stored.'), ('Regional storage', 'Snapshots are stored outside the AZ, so they survive an AZ failure.'), ('Restore', 'Create a new volume (in any AZ of the Region) or copy to another Region.'), ('Policies', 'Schedules, retention, immutability (vault lock) and restore tests.')],
    words=[('snapshot', 'a point-in-time copy of a disk'), ('incremental', 'copying only what changed'), ('retention', 'how long backups are kept'), ('immutable', 'cannot be changed or deleted, even by an admin, until the period ends')],
    diff=table(['', 'Snapshot / backup', 'Replication', 'Archive tier'], [['Goes back in time', 'yes', 'no — copies changes immediately', 'only what you archived'], ['Protects against deletion / ransomware', 'yes (with immutability)', 'no', 'partly'], ['Main goal', 'recovery', 'availability / DR', 'cheap long-term keeping']], minw=560),
    where=['Nightly database and VM backups', 'Before risky changes (upgrade, migration)', 'Compliance retention'],
    realworld='Ransomware groups now routinely look for and delete cloud backups first. That is why AWS Backup Vault Lock, Azure immutable vaults and Google backup vaults offer WORM-style locks that even the account’s administrators cannot remove.',
    pro='Deleting an old snapshot rarely frees what you expect: because snapshots are incremental, blocks still referenced by later snapshots are kept. Only blocks unique to the deleted snapshot are removed — so cost drops less than its “size” suggests.')

def a_hyb(k):
    o = t(180, 12, ['On-premises file server', 'Gateway: local cache, cloud capacity', 'Bulk move: online or by device'][k], 9, 'ink', bold=True)
    o += box(14, 34, 120, 92, 'card', rx=8) + t(74, 50, 'office / data centre', 7, 'ink2') + box(30, 60, 88, 26, 'blue', rx=4) + t(74, 77, 'servers, PCs', 7, 'ink')
    if k >= 1: o += box(30, 92, 88, 26, 'amber', rx=4) + t(74, 109, ['', 'gateway VM (cache)', 'DataSync agent'][k], 6.8, 'ink')
    o += box(226, 34, 120, 92, 'green', rx=8) + t(286, 74, 'S3 / Blob / GCS', 7.6, 'ink', bold=True) + t(286, 92, 'cloud storage', 7, 'ink2')
    if k >= 1: o += arrow(136, 100, 224, 80) + t(180, 82, ['', 'NFS/SMB → S3', 'TB over the network'][k], 6.8, 'ink2')
    if k == 2: o += box(150, 104, 60, 22, 'violet', rx=3) + t(180, 119, 'or a device', 6.6, 'ink')
    o += t(180, 146, ['local storage keeps filling up', 'users still see a normal file share; data lives in the cloud', 'DataSync / Data Box / Transfer Appliance / Data Transfer Terminal'][k], 7.2, 'ink', bold=True)
    return o
A_HYB = cap([a_hyb(k) for k in range(3)], [('On-premises', 'Office file servers fill up and need backup.', ''), ('Gateway', 'A gateway VM presents a normal file share locally but stores files in cloud', 'object storage, caching recent ones.'), ('Bulk transfer', 'Large datasets move online (DataSync, Storage Transfer Service, AzCopy) or on', 'physical devices when the network is too slow.')],
    'Hybrid storage and data transfer in action', 'Connecting existing sites to cloud storage.', 'Hybrid storage', 'Animation: an on-premises office; a storage gateway caching files locally and storing them in the cloud; bulk transfer online or with a device.', 's7anim')
T7 = vtype(7, 'Hybrid storage and data transfer', 'violet',
    '<b>Hybrid storage</b> services connect on-premises systems to cloud storage — for example a <b>storage gateway</b> that exposes a local file, volume or tape interface while keeping data in the cloud — and <b>data transfer</b> services move large datasets into the cloud online (agents, managed transfer) or offline using physical storage devices.',
    'A neighbourhood courier counter: you hand parcels over locally as always, and the courier quietly moves them to the big warehouse in the city.',
    'TiffinGo buys a smaller kitchen chain with a 20 TB file server. An AWS DataSync agent copies the files to S3 over the office internet in a few nights; the kitchen staff keep using a familiar file share through a Storage Gateway with a local cache.',
    'AWS Storage Gateway (File, Volume, Tape), AWS DataSync, AWS Transfer Family (SFTP), AWS Data Transfer Terminal; Azure File Sync, AzCopy, Azure Data Box; Google Storage Transfer Service, Transfer Appliance.',
    '', A_HYB,
    'offices or data centres must use cloud storage transparently, or you are migrating terabytes to petabytes.',
    'a simple upload tool would do, or the network is fast enough that a device adds only delay.',
    plain='Tools that link your office’s storage to the cloud, and that move huge amounts of data into the cloud — over the internet or on shipped disks.',
    how=[('Gateway', 'A VM or appliance on-premises presents NFS/SMB/iSCSI/tape.'), ('Cache', 'Recently used data stays local for speed.'), ('Cloud backend', 'All data is stored as objects in S3 / Blob / Cloud Storage.'), ('Online transfer', 'Agents copy, verify and schedule transfers with bandwidth limits.'), ('Offline transfer', 'Ruggedised devices or drop-off locations for when “network time > shipping time”.')],
    words=[('gateway', 'a bridge between an on-prem protocol and a cloud service'), ('iSCSI', 'block storage over a network'), ('SFTP', 'secure file transfer protocol'), ('offline transfer', 'moving data on physical devices')],
    diff=table(['Data size over a 100 Mbit/s link', 'Approx. transfer time'], [['1 TB', '≈ 1 day'], ['10 TB', '≈ 10 days'], ['100 TB', '≈ 3–4 months → use a device or faster link']], minw=420),
    where=['Branch offices and file-server replacement', 'Backup to cloud (virtual tape libraries)', 'Data centre migration'],
    realworld='AWS no longer accepts new customers for <b>Snowball Edge</b> and no longer offers Snow Family devices for new orders; for offline migration it now points to the <b>AWS Data Transfer Terminal</b> (bring your own drives to an AWS location) and partner services, and to DataSync for online transfer. Azure Data Box and Google Transfer Appliance remain available.',
    pro='The old exam fact “use Snowmobile for exabytes” is history — AWS retired the Snowmobile truck in 2024. Check current product availability before answering migration questions from older practice tests.')

SUMMARY = table(['#', 'Storage', 'Accessed as', 'Persistence', 'Typical price (relative)', 'TiffinGo uses it for'], [
    ['1', 'Block', 'disk on one server', 'until deleted (one AZ)', 'medium', 'database disk'], ['2', 'File', 'NFS/SMB share', 'until deleted', 'higher', 'shared recipes folder'],
    ['3', 'Object', 'HTTPS API', 'until deleted (multi-AZ)', 'lowest hot price', 'photos, website files'], ['4', 'Archive tiers', 'API + restore', 'with minimum duration', 'very low', 'old GST invoices'],
    ['5', 'Local / ephemeral', 'local disk', 'lost on stop', 'included', 'Spark scratch'], ['6', 'Snapshots & backup', 'restore', 'by retention policy', 'low (incremental)', 'nightly DB backup'], ['7', 'Hybrid & transfer', 'gateway / agent', '—', 'per GB / per hour', 'acquired chain’s files']], minw=700)
CHECK = ('  <h3>Check yourself: which storage fits?</h3>\n' +
    qx('A. Four web servers must read and write the same uploaded PDFs.', ['Block', 'File storage', 'Instance store', 'Archive'], 1, 'Shared mount.') +
    qx('B. Keep 10 years of call recordings that are almost never played.', ['S3 Standard', 'Deep Archive / Archive tier', 'EBS io2', 'Local SSD'], 1, 'Cheapest long-term.') +
    qx('C. The data disk of a self-managed MySQL server.', ['Object', 'Block storage', 'File', 'Archive'], 1, 'Low-latency disk for one server.') +
    qx('D. Temporary files of a big Spark job, recreated if lost.', ['Instance store / Local SSD', 'Glacier', 'Azure Files', 'Backup vault'], 0, 'Fast and ephemeral.'))

TYPES = ('  <p>Seven kinds of storage, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['Why can an EBS volume in ap-south-1a not be attached to an instance in 1b — and how do you move it?', 'Why might moving millions of tiny files to Glacier cost more than it saves?', 'Why does deleting a 40 GB snapshot sometimes free almost nothing?'], 'types 1, 4 and 6') + MAP
         + jump(['Block', 'File', 'Object', 'Archive', 'Ephemeral', 'Backup', 'Hybrid']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('Durability', 'Probability that stored data is not lost over a year.', 'Decides whether you need extra copies.', 'S3/Blob/GCS designed for 11 nines; EBS io2 99.999%, gp3 99.8–99.9%.'),
    ('Availability', 'Probability you can read/write right now.', 'An SLA number, different from durability (Lesson 5.4).', 'S3 Standard 99.9% SLA, One Zone-IA lower.'),
    ('Redundancy option', 'How many copies, where.', 'Trade price against surviving an AZ or Region loss.', 'Azure LRS/ZRS/GRS/GZRS; GCS region/dual/multi-region; S3 Standard vs One Zone.'),
    ('Performance', 'IOPS, throughput, latency.', 'Databases need IOPS; analytics needs throughput.', 'gp3/io2, Premium SSD v2/Ultra, Hyperdisk.'),
    ('Encryption', 'Data encrypted at rest and in transit.', 'On by default for new data in S3, Blob and GCS.', 'SSE-S3/SSE-KMS, Azure SSE with platform or customer keys, CMEK.'),
    ('Access control', 'Who can read/write.', 'Most data leaks are misconfigured buckets.', 'IAM + bucket policies, Block Public Access; Azure RBAC + SAS; GCS IAM + uniform access.')])

DEEP = ('  <h3>Durability vs availability, with numbers</h3>\n  <p>S3 Standard is designed for <b>99.999999999%</b> durability (lose about 1 of 10 million objects every 10,000 years) but its SLA is <b>99.9%</b> availability (Lesson 5.4). A short outage makes data <i>unreachable</i>, not lost. Block volumes are different: an EBS gp3 volume has an annual failure rate of 0.1–0.2% — that is why databases need snapshots.</p>\n'
    '  <h3>Azure redundancy options in one table</h3>\n' + table(['Option', 'Copies', 'Survives'], [['LRS', '3 in one datacentre', 'disk/server failure'], ['ZRS', '3 across availability zones', 'a zone outage'], ['GRS', 'LRS + 3 in the paired Region', 'a Region disaster (failover needed)'], ['GZRS', 'ZRS + 3 in the paired Region', 'zone and Region failures']], minw=480) +
    '\n  <h3>Erasure coding: how 11 nines are possible</h3>\n  <p>Instead of keeping three full copies, object stores split data into <i>k</i> data pieces plus <i>m</i> parity pieces (like RAID across many machines and AZs). Any <i>k</i> pieces rebuild the object, so several devices — or a whole AZ — can fail at once. Background processes constantly check checksums and repair lost pieces.</p>\n'
    '  <h3>Request costs: the other half of the storage bill</h3>\n  <p>Object storage charges per request too (PUT/LIST cost more than GET). A design that writes millions of tiny files can pay more for requests than for storage — batch small records into bigger files (e.g. Parquet) for analytics.</p>')

clouds = vendor_tabs('<p><b>AWS:</b> EBS (block), EFS and FSx (file), S3 with storage classes and Intelligent-Tiering (object), S3 Glacier classes (archive), instance store, EBS snapshots and AWS Backup, Storage Gateway, DataSync, Transfer Family, Data Transfer Terminal.</p>',
    '<p><b>Azure:</b> Managed Disks (block), Azure Files and Azure NetApp Files (file), Blob Storage with Hot/Cool/Cold/Archive tiers (object), temporary disk, Azure Backup, Azure File Sync, AzCopy, Data Box, Storage Explorer.</p>',
    '<p><b>Google Cloud:</b> Persistent Disk and Hyperdisk (block), Filestore and NetApp Volumes (file), Cloud Storage with Standard/Nearline/Coldline/Archive (object), Local SSD, snapshots and Backup and DR, Storage Transfer Service, Transfer Appliance.</p>') + \
    cloud3([['Block disks', 'EBS', 'Managed Disks', 'Persistent Disk / Hyperdisk'], ['File shares', 'EFS, FSx', 'Azure Files, NetApp Files', 'Filestore, NetApp Volumes'], ['Object', 'S3', 'Blob Storage', 'Cloud Storage'], ['Archive', 'Glacier classes', 'Archive tier', 'Archive class'],
            ['Local disk', 'instance store', 'temporary disk', 'Local SSD'], ['Backup', 'AWS Backup', 'Azure Backup', 'Backup and DR'], ['Hybrid', 'Storage Gateway', 'File Sync', 'Storage Transfer Service'], ['Bulk/offline', 'DataSync, Data Transfer Terminal', 'AzCopy, Data Box', 'Transfer Appliance']])

# ------------------------------------------------------------------ practical
# console sketches for steps 1–4 (consumed in order by tri())
MOCKQ.extend([
 (mock('aws', ['Amazon S3', 'Buckets', 'Create bucket'], ['General purpose buckets', 'Directory buckets', 'Table buckets', 'Access Points', 'Storage Lens'], 'General purpose buckets',
       [('AWS Region', 'Asia Pacific (Mumbai) ap-south-1'), ('Bucket name', 'tiffingo-photos-yourname'), ('Block Public Access settings', '[x] Block all public access'), ('Default encryption', '▾ SSE-S3 (Amazon S3 managed keys)')], 'Create bucket'),
  mock('az', ['Home', 'Storage accounts', 'Create a storage account'], ['Basics', 'Advanced', 'Networking', 'Data protection', 'Encryption', 'Tags', 'Review + create'], 'Basics',
       [('Resource group', '▾ rg-tiffingo'), ('Storage account name', 'tiffingoyourname'), ('Region', '▾ (Asia Pacific) Central India'), ('Redundancy', '▾ Locally-redundant storage (LRS)')], 'Review + create'),
  mock('gcp', ['Cloud Storage', 'Buckets', 'Create a bucket'], ['Overview', 'Buckets', 'Monitoring', 'Settings'], 'Buckets',
       [('Name your bucket', 'tiffingo-photos-yourname'), ('Location type', '▾ Region — asia-south1 (Mumbai)'), ('Default storage class', '▾ Standard'), ('Prevent public access', '[x] Enforce public access prevention on this bucket')], 'Create')),
 (mock('aws', ['Amazon S3', 'tiffingo-photos-…', 'Lifecycle rule'], ['Objects', 'Properties', 'Permissions', 'Metrics', 'Management', 'Access Points'], 'Management',
       [('Lifecycle rule name', 'cool-then-archive'), ('Rule scope', '[x] Apply to all objects in the bucket'), ('Transition current versions', '▾ Standard-IA after 30 days · Glacier Deep Archive after 365'), ('Expire noncurrent versions', '90 days')], 'Create rule'),
  mock('az', ['Home', 'tiffingo…', 'Lifecycle management', 'Add a rule'], ['Overview', 'Containers', 'Data protection', 'Lifecycle management', 'Access keys'], 'Lifecycle management',
       [('Rule name', 'cool-then-archive'), ('Rule scope', '[x] Apply rule to all blobs'), ('If base blobs were', '▾ Last modified more than 30 days ago'), ('Then', '▾ Move to cool storage')], 'Add'),
  mock('gcp', ['Cloud Storage', 'tiffingo-photos-…', 'Add object lifecycle rule'], ['Objects', 'Configuration', 'Permissions', 'Protection', 'Lifecycle', 'Observability'], 'Lifecycle',
       [('Select an action', '▾ Set storage class to Nearline'), ('Select object conditions', 'Age: 30 days')], 'Create')),
 (mock('aws', ['EC2', 'Volumes', 'Create volume'], ['Instances', 'Volumes', 'Snapshots', 'Lifecycle Manager'], 'Volumes',
       [('Volume type', '▾ General Purpose SSD (gp3)'), ('Size (GiB)', '4'), ('IOPS · Throughput', '3000 · 125 MiB/s'), ('Availability Zone', '▾ ap-south-1a (same as the VM)')], 'Create volume'),
  mock('az', ['Home', 'tiffingo-vm', 'Disks'], ['Overview', 'Disks', 'Size', 'Networking', 'Run command'], 'Disks',
       [('Data disks', '+ Create and attach a new disk'), ('Disk name · Size', 'data1 · 4 GiB'), ('Storage type', '▾ Standard SSD (locally-redundant storage)')], 'Apply'),
  mock('gcp', ['Compute Engine', 'Disks', 'Create a disk'], ['VM instances', 'Disks', 'Snapshots', 'Images'], 'Disks',
       [('Name', 'data1'), ('Location', '▾ Single zone — asia-south1-a'), ('Disk type', '▾ Balanced persistent disk'), ('Size', '10 GB')], 'Create')),
 (mock('aws', ['Amazon S3', 'tiffingo-photos-…', 'menu/menu.txt'], ['Properties', 'Permissions', 'Versions', 'Object actions'], 'Object actions',
       [('Object actions', '▾ Share with a presigned URL'), ('Time interval until the presigned URL expires', '60 minutes')], 'Create presigned URL'),
  mock('az', ['Home', 'photos', 'menu/menu.txt', 'Generate SAS'], ['Overview', 'Versions', 'Generate SAS', 'Edit'], 'Generate SAS',
       [('Signing method', '( ) Account key'), ('Permissions', '▾ Read'), ('Expiry', 'today + 1 hour'), ('Allowed protocols', '▾ HTTPS only')], 'Generate SAS token and URL'),
  mock('gcp', ['IAM & Admin', 'Service accounts', 'Create service account'], ['IAM', 'Service accounts', 'Roles', 'Audit logs'], 'Service accounts',
       [('Service account name', 'url-signer'), ('Grant this service account access', '▾ (none here — grant on the bucket)')], 'Create and continue')),
])

STEP1 = ('1 · Create a private bucket and upload a file', tri(
    (['[[S3]] → [[Create bucket]] → Region [[Asia Pacific (Mumbai)]]; name <code>tiffingo-photos-&lt;yourname&gt;</code> (globally unique).', 'Keep [[Block all public access]] ON, encryption default (SSE-S3) → [[Create bucket]].', 'Open the bucket → [[Upload]] → [[Add files]] → pick any small file (e.g. menu.txt) → [[Upload]]. Click the object and note its [[Object URL]] — opening it gives AccessDenied (private).'],
     'B=tiffingo-photos-$RANDOM$RANDOM\naws s3 mb s3://$B --region ap-south-1\necho "Diwali thali — ₹249" > menu.txt\naws s3 cp menu.txt s3://$B/menu/menu.txt\naws s3 ls s3://$B --recursive --human-readable\naws s3api get-public-access-block --bucket $B',
     '<code>make_bucket: …</code>, <code>upload: ./menu.txt to s3://…/menu/menu.txt</code>, the object listed with its size, and all four public-access blocks <code>true</code>.'),
    (['[[Storage accounts]] → [[Create]] → resource group <code>rg-tiffingo</code>, name <code>tiffingo&lt;yourname&gt;</code> (3–24 lowercase letters/digits), Region [[Central India]], redundancy [[LRS]] → [[Review + create]] → [[Create]].', 'Open it → [[Data storage]] → [[Containers]] → [[+ Container]] <code>photos</code>, access level [[Private]].', 'Open <code>photos</code> → [[Upload]] → choose a file → [[Upload]].'],
     'SA=tiffingo$RANDOM\naz group create --name rg-tiffingo --location centralindia\naz storage account create --name $SA --resource-group rg-tiffingo --location centralindia \\\n  --sku Standard_LRS --kind StorageV2 --allow-blob-public-access false\naz storage container create --account-name $SA --name photos --auth-mode key\necho "Diwali thali — ₹249" > menu.txt\naz storage blob upload --account-name $SA --container-name photos --name menu/menu.txt --file menu.txt --auth-mode key\naz storage blob list --account-name $SA --container-name photos --auth-mode key --output table',
     '<code>"provisioningState": "Succeeded"</code>, <code>{"created": true}</code> and a table row for <code>menu/menu.txt</code> in tier Hot.'),
    (['[[Cloud Storage]] → [[Buckets]] → [[Create]] → name <code>tiffingo-photos-&lt;yourname&gt;</code>; location type [[Region]] → [[asia-south1 (Mumbai)]]; class [[Standard]].', 'Access control: keep [[Enforce public access prevention]] ticked, [[Uniform]] access → [[Create]].', '[[Upload files]] → pick a small file.'],
     'B=tiffingo-photos-$RANDOM$RANDOM\ngcloud storage buckets create gs://$B --location=asia-south1 --uniform-bucket-level-access --public-access-prevention\necho "Diwali thali — ₹249" > menu.txt\ngcloud storage cp menu.txt gs://$B/menu/menu.txt\ngcloud storage ls --long gs://$B/**',
     '<code>Creating gs://…/</code>, <code>Copying file://menu.txt</code> and the object listed with size and date.')),
    'Bucket names are global (one namespace for everyone); the data still lives only in the Region you chose.')

LC_AWS = '{"Rules":[{"ID":"cool-then-archive","Status":"Enabled","Filter":{"Prefix":""},"Transitions":[{"Days":30,"StorageClass":"STANDARD_IA"},{"Days":365,"StorageClass":"DEEP_ARCHIVE"}],"NoncurrentVersionExpiration":{"NoncurrentDays":90}}]}'
LC_AZ = '{"rules":[{"enabled":true,"name":"cool-then-archive","type":"Lifecycle","definition":{"actions":{"baseBlob":{"tierToCool":{"daysAfterModificationGreaterThan":30},"tierToArchive":{"daysAfterModificationGreaterThan":365}}},"filters":{"blobTypes":["blockBlob"]}}}]}'
LC_GCP = '{"rule":[{"action":{"type":"SetStorageClass","storageClass":"NEARLINE"},"condition":{"age":30}},{"action":{"type":"SetStorageClass","storageClass":"ARCHIVE"},"condition":{"age":365}}]}'
STEP2 = ('2 · Turn on versioning and a lifecycle rule', tri(
    (['Bucket → [[Properties]] → [[Bucket Versioning]] → [[Edit]] → [[Enable]] → [[Save changes]].', 'Upload menu.txt again with different text → [[Objects]] → toggle [[Show versions]]: two versions.', '[[Management]] → [[Create lifecycle rule]] → name <code>cool-then-archive</code>, apply to all objects → transition current versions to [[Standard-IA]] after 30 days and [[Glacier Deep Archive]] after 365; expire noncurrent versions after 90 days → [[Create rule]].'],
     f"aws s3api put-bucket-versioning --bucket $B --versioning-configuration Status=Enabled\necho \"Diwali thali — ₹229 (offer)\" > menu.txt && aws s3 cp menu.txt s3://$B/menu/menu.txt\naws s3api list-object-versions --bucket $B --prefix menu/ --query 'Versions[].[VersionId,IsLatest,Size]' --output table\naws s3api put-bucket-lifecycle-configuration --bucket $B --lifecycle-configuration '{LC_AWS}'\naws s3api get-bucket-lifecycle-configuration --bucket $B",
     'two versions (one <code>IsLatest True</code>) and the lifecycle rule echoed back.'),
    (['Storage account → [[Data management]] → [[Data protection]] → tick [[Enable versioning for blobs]] → [[Save]].', 'Upload menu.txt again (overwrite) → open the blob → [[Versions]] tab shows the old one.', '[[Data management]] → [[Lifecycle management]] → [[Add a rule]] → name <code>cool-then-archive</code> → base blobs: modified more than 30 days ago → [[Move to cool storage]]; add 365 days → [[Move to archive storage]] → [[Add]].'],
     f"az storage account blob-service-properties update --account-name $SA --resource-group rg-tiffingo --enable-versioning true\necho \"Diwali thali — ₹229 (offer)\" > menu.txt\naz storage blob upload --account-name $SA --container-name photos --name menu/menu.txt --file menu.txt --overwrite --auth-mode key\naz storage blob list --account-name $SA --container-name photos --include v --auth-mode key --query \"[].{{name:name, version:versionId, current:isCurrentVersion}}\" --output table\naz storage account management-policy create --account-name $SA --resource-group rg-tiffingo --policy '{LC_AZ}'",
     'two rows for menu/menu.txt (one current) and the policy JSON returned.'),
    (['Bucket → [[Protection]] tab → [[Object versioning]] → [[Off]] → turn [[On]].', 'Upload menu.txt again → [[Objects]] → [[Show]] → [[Live and noncurrent objects]].', '[[Lifecycle]] tab → [[Add a rule]] → [[Set storage class to Nearline]] → age 30 days → [[Create]]; add another: [[Archive]] at 365 days.'],
     f"gcloud storage buckets update gs://$B --versioning\necho \"Diwali thali — ₹229 (offer)\" > menu.txt && gcloud storage cp menu.txt gs://$B/menu/menu.txt\ngcloud storage ls --all-versions gs://$B/menu/\ncat > lc.json <<'EOF'\n{LC_GCP}\nEOF\ngcloud storage buckets update gs://$B --lifecycle-file=lc.json\ngcloud storage buckets describe gs://$B --format=\"default(lifecycle_config)\"",
     'two lines ending in <code>#&lt;generation&gt;</code> (two versions) and the two lifecycle rules.')),
    'Versioning protects against accidental overwrite and delete; lifecycle rules keep the bill falling as data ages — both are one-time settings.')

STEP3 = ('3 · Add a block disk to a VM and snapshot it', tri(
    (['Use the VM from Lesson 6.1 (or launch one). Note its AZ under [[Networking]].', '[[EC2]] → [[Volumes]] → [[Create volume]] → [[gp3]], 4 GiB, same AZ → [[Create volume]].', 'Select it → [[Actions]] → [[Attach volume]] → pick the instance → [[Attach]]. Connect and run <code>lsblk</code>, then <code>sudo mkfs -t xfs /dev/nvme1n1 && sudo mkdir /data && sudo mount /dev/nvme1n1 /data</code>.', 'Select the volume → [[Actions]] → [[Create snapshot]] → [[Create snapshot]].'],
     "AZ=$(aws ec2 describe-instances --instance-ids $ID --query 'Reservations[0].Instances[0].Placement.AvailabilityZone' --output text)\nVOL=$(aws ec2 create-volume --availability-zone $AZ --size 4 --volume-type gp3 --query VolumeId --output text)\naws ec2 wait volume-available --volume-ids $VOL\naws ec2 attach-volume --volume-id $VOL --instance-id $ID --device /dev/sdf\nSNAP=$(aws ec2 create-snapshot --volume-id $VOL --description \"tiffingo lab\" --query SnapshotId --output text)\naws ec2 describe-snapshots --snapshot-ids $SNAP --query 'Snapshots[0].[State,VolumeSize,Progress]' --output text",
     '<code>lsblk</code> shows a 4G <code>nvme1n1</code>; the snapshot goes from <code>pending</code> to <code>completed 100%</code>.'),
    (['Open the VM from Lesson 6.1 → [[Settings]] → [[Disks]] → [[Create and attach a new disk]] → 4 GiB Standard SSD → [[Apply]].', 'Connect and run <code>lsblk</code> (the new disk is usually <code>sdc</code>), then format and mount it.', '[[Disks]] → open the data disk → [[Create snapshot]] → name <code>data1-snap</code> → [[Review + create]] → [[Create]].'],
     'az vm disk attach --resource-group rg-tiffingo --vm-name tiffingo-vm --name data1 --new --size-gb 4 --sku StandardSSD_LRS\naz vm run-command invoke --resource-group rg-tiffingo --name tiffingo-vm --command-id RunShellScript --scripts "lsblk"\naz snapshot create --resource-group rg-tiffingo --name data1-snap --source data1\naz snapshot show --resource-group rg-tiffingo --name data1-snap --query "[provisioningState,diskSizeGB]" --output tsv',
     'a 4G disk in lsblk; snapshot <code>Succeeded 4</code>.'),
    (['[[Compute Engine]] → [[Disks]] → [[Create disk]] → name <code>data1</code>, zone [[asia-south1-a]] (same as the VM), 10 GB balanced → [[Create]].', 'Open the VM → [[Edit]] → [[Additional disks]] → [[Attach existing disk]] → data1 → [[Save]]. SSH and run <code>lsblk</code>.', '[[Snapshots]] → [[Create snapshot]] → source disk data1 → [[Create]].'],
     'gcloud compute disks create data1 --size=10GB --type=pd-balanced --zone=asia-south1-a\ngcloud compute instances attach-disk tiffingo-vm --disk=data1 --zone=asia-south1-a\ngcloud compute ssh tiffingo-vm --zone=asia-south1-a --command="lsblk"\ngcloud compute snapshots create data1-snap --source-disk=data1 --source-disk-zone=asia-south1-a\ngcloud compute snapshots list',
     'a 10G <code>sdb</code> in lsblk; snapshot <code>data1-snap</code> with STATUS READY.')),
    'The disk must be in the same zone as the VM; the snapshot is regional — that is how you move a disk to another zone.')

STEP4 = ('4 · Share a private file for one hour', tri(
    (['Open the object → [[Object actions]] → [[Share with a presigned URL]] → 60 minutes → [[Create presigned URL]] → copy and open it in a private browser window.'],
     'aws s3 presign s3://$B/menu/menu.txt --expires-in 3600\n# open the printed URL in a browser; after 1 hour it returns AccessDenied',
     'a long URL with <code>X-Amz-Expires=3600</code> and <code>X-Amz-Signature=…</code> that shows the file without making the bucket public.'),
    (['Open the blob → [[Generate SAS]] → permissions [[Read]], expiry 1 hour from now → [[Generate SAS token and URL]] → copy [[Blob SAS URL]].'],
     'END=$(date -u -d "+1 hour" +%Y-%m-%dT%H:%MZ)\naz storage blob generate-sas --account-name $SA --container-name photos --name menu/menu.txt \\\n  --permissions r --expiry $END --https-only --full-uri --auth-mode key --output tsv',
     'a URL ending in <code>?se=…&amp;sp=r&amp;sig=…</code> — a shared access signature valid for one hour.'),
    (['Signed URLs need a service account in Google Cloud: [[IAM & Admin]] → [[Service accounts]] → [[Create service account]] <code>url-signer</code>.', 'On the bucket → [[Permissions]] → [[Grant access]] → principal url-signer → role [[Storage Object Viewer]].', 'Give yourself [[Service Account Token Creator]] on url-signer, then run the CLI command (the console has no button for signed URLs).'],
     'P=$(gcloud config get-value project)\ngcloud iam service-accounts create url-signer\ngcloud storage buckets add-iam-policy-binding gs://$B --member=serviceAccount:url-signer@$P.iam.gserviceaccount.com --role=roles/storage.objectViewer\ngcloud iam service-accounts add-iam-policy-binding url-signer@$P.iam.gserviceaccount.com \\\n  --member=user:$(gcloud config get-value account) --role=roles/iam.serviceAccountTokenCreator\ngcloud storage sign-url gs://$B/menu/menu.txt --duration=1h --impersonate-service-account=url-signer@$P.iam.gserviceaccount.com',
     'a table with a <code>signed_url</code> containing <code>X-Goog-Signature</code>. If you get a permission error, wait a minute for IAM to update and retry.')),
    'Never make a bucket public to share one file: a signed URL / SAS gives one file, read-only, for a limited time.')

prac = practical(OWN_INTRO + ' Steps 1–4 take about 40 minutes and stay within free credits.', [SETUP_STEP, STEP1, STEP2, STEP3, STEP4],
    cleanup='<b>AWS:</b> empty and delete the bucket (versioned objects too); detach and delete the volume; delete the snapshot. CLI: <code>aws s3 rm s3://$B --recursive; aws s3api delete-objects --bucket $B --delete "$(aws s3api list-object-versions --bucket $B --query \'{Objects: Versions[].{Key:Key,VersionId:VersionId}}\')"; aws s3 rb s3://$B</code>; <code>aws ec2 detach-volume --volume-id $VOL; aws ec2 wait volume-available --volume-ids $VOL; aws ec2 delete-volume --volume-id $VOL; aws ec2 delete-snapshot --snapshot-id $SNAP</code>.<br>'
            '<b>Azure:</b> [[Resource groups]] → <code>rg-tiffingo</code> → [[Delete resource group]] (storage account, disk, snapshot and VM together). CLI: <code>az group delete --name rg-tiffingo --yes --no-wait</code>.<br>'
            '<b>Google Cloud:</b> <code>gcloud storage rm --recursive --all-versions gs://$B; gcloud storage buckets delete gs://$B; gcloud compute instances detach-disk tiffingo-vm --disk=data1 --zone=asia-south1-a; gcloud compute disks delete data1 --zone=asia-south1-a --quiet; gcloud compute snapshots delete data1-snap --quiet; gcloud iam service-accounts delete url-signer@$P.iam.gserviceaccount.com --quiet</code>.'.replace('[[', '<b>').replace(']]', '</b>'))

mist = mistakes([
    ['Making a bucket public to share a few files.', 'Quickest way to “make it work”.', 'Keep Block Public Access on; use signed URLs / SAS or CloudFront with origin access control.'],
    ['Thinking replication or RAID is a backup.', 'Copies feel safe.', 'Replication copies deletions too; keep versioned, immutable, point-in-time backups.'],
    ['Storing the only copy on instance store / temp disk.', 'It looks like a normal disk.', 'Ephemeral = lost on stop; keep data on block/object storage.'],
    ['Huge gp2/gp3 disks bought only for speed.', 'Old gp2 habit.', 'On gp3 raise IOPS/throughput independently of size.'],
    ['Archiving data that is read monthly.', 'Chasing the lowest per-GB price.', 'Count retrieval fees and minimum durations; use Intelligent-Tiering if unsure.'],
    ['Forgetting old versions and snapshots.', 'Invisible in the normal view.', 'Lifecycle rules for noncurrent versions; snapshot retention policies.'],
    ['Disk in a different zone than the VM.', 'Zones not checked.', 'Create disks in the VM’s AZ; move via snapshot.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Cloud storage systems: block, file, object; storage virtualization; data management in the cloud.'], ['AWS CLF-C02', 'S3 and storage classes, S3 lifecycle, EBS, EFS, FSx, instance store, AWS Backup, Storage Gateway, DataSync, Snow Family status.'], ['AZ-900', 'Storage accounts, redundancy (LRS/ZRS/GRS/GZRS), Blob access tiers, Azure Files, disks, AzCopy, Storage Explorer, File Sync, Data Box, migration tools.'], ['Google Cloud Digital Leader', 'Cloud Storage classes, Persistent Disk, Filestore, data lifecycle and choosing storage by access pattern.']], minw=560) + \
    qx('1. Which AWS service is object storage?', ['Amazon EBS', 'Amazon S3', 'Amazon EFS', 'Instance store'], 1, 'S3.') + \
    qx('2. Which storage keeps data only while the instance is running?', ['EBS', 'S3', 'Instance store', 'EFS'], 2, 'Ephemeral.') + \
    qx('3. Which Azure redundancy option copies data across availability zones in one Region?', ['LRS', 'ZRS', 'GRS', 'RA-GRS'], 1, 'Zone-redundant storage.') + \
    qx('4. Multiple Linux EC2 instances need a shared file system that scales automatically. Which service?', ['Amazon EBS', 'Amazon EFS', 'S3 Glacier', 'Instance store'], 1, 'NFS shared file system.') + \
    qx('5. A company must keep records for 7 years and rarely access them. Lowest-cost S3 class?', ['S3 Standard', 'S3 Standard-IA', 'S3 Glacier Deep Archive', 'S3 One Zone-IA'], 2, 'Cheapest archive.') + \
    qx('6. Which Google Cloud Storage class has a 30-day minimum and suits monthly access?', ['Standard', 'Nearline', 'Coldline', 'Archive'], 1, 'Nearline.')

proj = miniproject('Mini project: a storage plan for TiffinGo',
    'Put every kind of TiffinGo data in the right storage, with protection and a falling bill.',
    ['<b>Inventory:</b> orders DB, recipes share, photos (3 TB), invoices (7 yrs), nightly backups, Spark scratch.',
     '<b>Choose:</b> a storage type and class for each, with one line why.',
     '<b>Protect:</b> versioning, backup plan (schedule, retention, cross-Region copy), immutability where needed.',
     '<b>Lifecycle:</b> write the lifecycle rules (days → class → delete) for photos and invoices.',
     '<b>Prove it:</b> on your own account create the bucket with versioning + lifecycle, a disk snapshot and a one-hour share link (steps 1–4).',
     '<b>Cost:</b> estimate the monthly storage bill with the pricing calculator before and after lifecycle rules.',
     '<b>Clean up</b> and screenshot empty resource lists.'],
    'A one-page storage plan with classes, rules, backups and monthly cost.', 'This lesson + 5.5 (pricing) + 6.1 (VMs) + 4.3 (storage virtualization).')

assemble_v2(HERE, story_h2='The disk is full — again', hook_html=hk,
    narration='TiffinGo’s server disk keeps filling with photos, invoices and backups. Buying a bigger disk is the reflex; choosing the right kind of storage is the fix.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Storage systems in the cloud',
    formal='<b>Cloud storage services</b> provide persistent, network-accessible capacity in several forms — <b>block</b> volumes attached to servers, shared <b>file</b> systems, and <b>object</b> storage accessed by API — with tiers that trade price for access speed, built-in redundancy across devices, zones or Regions, and pay-per-use billing by capacity, requests, retrieval and data transfer.',
    simple='Places in the cloud to keep data: disks for servers, shared folders, and an unlimited file store over the internet — each with cheaper “cold” options for old data.',
    interview=['“Block storage like EBS is a network disk for one instance; file storage like EFS or Azure Files is a shared NFS/SMB file system; object storage like S3 stores objects in buckets over HTTPS with 11-nines durability.”', '“I pick by access pattern, then use storage classes and lifecycle rules for cost, and snapshots/backups with immutability for protection.”'],
    terms_rows=[('Block storage', 'Network disk for one server.'), ('File storage', 'Shared NFS/SMB file system.'), ('Object storage', 'Objects in buckets via HTTPS.'), ('Storage class / tier', 'Price vs access speed.'), ('Lifecycle rule', 'Automatic move/delete by age.'), ('Snapshot', 'Point-in-time copy.'), ('Durability', 'Chance data is not lost.'), ('IOPS', 'Operations per second.'), ('Ephemeral', 'Lost when the instance stops.'), ('Signed URL / SAS', 'Time-limited access link.')],
    exam='CLF-C02 asks to match S3, EBS, EFS, instance store, Glacier, Storage Gateway and Backup to scenarios. AZ-900 asks storage redundancy options, access tiers and migration tools. Digital Leader asks Cloud Storage classes.',
    picture_h2='Three shapes of storage, and the temperature ladder', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven kinds of storage, one by one', TYPES)],
    how_h2='What happens when you upload a photo to S3', how_intro='The same idea applies to Azure Blob and Google Cloud Storage.', how_anim=UPLOAD,
    parts_h2='Six properties to compare in any storage service', parts_html=parts, lv='',
    myth_rows=[('Eleven nines means it is always available.', 'Durability ≠ availability (99.9% SLA).', 'Deep dive.'), ('Replication is a backup.', 'It replicates deletions too.', 'Type 6.'), ('Folders exist in S3.', 'Only key prefixes.', 'How it works, step 3.')],
    extra_secs=[('deep', 'Deep dive', 'Durability vs availability, Azure redundancy, erasure coding, request costs', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Explain block, file and object storage and choose one for a workload.', 'Use storage classes and lifecycle rules to cut cost.', 'Explain snapshots, backups, immutability and why replication is not backup.', 'Create a bucket, versioning, lifecycle rule, disk, snapshot and signed URL on your own account (console and CLI).', 'Choose a hybrid or bulk transfer option.'],
    next_html='<a href="../03-cloud-networking/">6.3 Cloud networking</a>.',
    pre='<b>Before you start:</b> <a href="../01-compute-products-and-services/">6.1 Compute</a> (step 3 reuses its VM) and <a href="../../04-virtualization/03-network-storage-and-data-virtualization/">4.3 Storage virtualization</a>.')
