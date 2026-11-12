import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)


hk = hook('At 9:12 p.m. one Mumbai data centre loses cooling and every server in it shuts down. TiffinGo’s customers keep ordering without noticing. A competitor is down for three hours. What did TiffinGo build that the competitor did not?',
    'Three different things people mix up: <b>high availability</b> (stay up through a failure inside a Region, usually by running in several AZs), <b>fault tolerance</b> (no visible interruption at all), and <b>disaster recovery</b> (come back after a whole Region or the data is lost — with a chosen RTO and RPO). Scalability (Lesson 5.3) keeps you fast under load; these keep you alive under failure. This lesson explains redundancy, multi-AZ design, the four classic DR strategies and fault isolation — then on <b>your own</b> account you build a group of servers across zones, kill one and watch it heal, and copy a backup to another Region.',
    ['HA vs fault tolerance vs DR — three terms interviewers love to test.', 'The four DR strategies from cheapest to fastest, with real RTO/RPO.', 'Watch the cloud replace a server you deleted.'])

def story_scene():
    o = t(180, 12, '9:12 p.m.: one AZ goes dark', 9, 'ink', bold=True)
    for i, (n, tn) in enumerate([('AZ 1a', 'green'), ('AZ 1b', 'red'), ('AZ 1c', 'green')]):
        x = 14 + i * 114
        o += box(x, 26, 104, 70, tn, rx=8) + t(x + 52, 46, n, 8, 'ink', bold=True) + t(x + 52, 66, ['2 app VMs ✔', 'power/cooling ✘', '2 app VMs ✔'][i], 7, 'ink') + t(x + 52, 84, ['DB primary', '—', 'DB standby'][i], 6.6, 'ink2')
    o += t(180, 118, 'TiffinGo: spread over 3 AZs → customers notice nothing.', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Three availability zones; zone 1b fails; zones 1a and 1c keep the app and database running.', story_scene(), 'Plan for failure, and failure becomes <tspan font-weight="700" class="s-acc">routine</tspan>.', h=134)
dialogue = '''R> Sir, AWS had an incident in one Mumbai AZ last night. Our dashboard shows… nothing happened?
A> Exactly what we paid for. Our servers are in three AZs behind a load balancer, and the database has a standby in another AZ.
K> So we are safe from everything?
A> From an AZ failure, yes. If the whole Mumbai Region had a problem, or someone deleted the database, that is disaster recovery — backups and a plan in Hyderabad.
R> How fast could we be back then?
A> That is the question of RTO and RPO. Let’s learn the strategies and what each costs.'''

# ------------------------------------------------------------------ picture
def threefig():
    o = t(320, 16, 'Scalability vs high availability vs fault tolerance vs disaster recovery', 10.5, 'ink', bold=True)
    cols = [('Scalability', 'handle more load', 'add capacity (5.3)', 'Diwali traffic ×10', 'blue'), ('High availability', 'stay up through failures', 'short blip allowed', 'one AZ fails', 'green'),
            ('Fault tolerance', 'no interruption at all', 'zero downtime, extra cost', 'a disk/server dies mid-request', 'violet'), ('Disaster recovery', 'come back after a disaster', 'RTO / RPO targets', 'Region outage, ransomware', 'amber')]
    for i, (n, a, b, c, tn) in enumerate(cols):
        x = 12 + i * 156
        o += box(x, 32, 148, 160, tn, rx=8) + t(x + 74, 54, n, 8.6, 'ink', bold=True) + t(x + 74, 80, a, 7.4, 'ink') + t(x + 74, 104, b, 7, 'ink2') + t(x + 74, 136, 'protects against:', 6.6, 'ink2') + t(x + 74, 152, c, 7, 'ink', bold=True)
    o += box(12, 204, 616, 30, 'card', rx=6) + t(320, 223, 'Availability is measured in nines (Lesson 5.4); durability is a different promise (data not lost).', 7.6, 'ink')
    return o
THREE = bigfig('Four boxes: scalability handles more load; high availability stays up through failures with a short blip; fault tolerance means no interruption; disaster recovery comes back after a disaster within RTO and RPO targets.', threefig(), h=244)

def drfig():
    o = t(320, 16, 'Four DR strategies: cost rises as RTO/RPO fall', 11, 'ink', bold=True)
    o += f'<path d="M50,220 L620,220 M50,220 L50,30" style="stroke:currentColor;stroke-width:1.2;opacity:.5"/>' + t(335, 238, 'cost and complexity →', 7.6, 'ink2') + f'<text x="30" y="125" class="s-ink2" font-size="7.6" text-anchor="middle" transform="rotate(-90 30 125)">← faster recovery (lower RTO / RPO)</text>'
    for i, (n, r, p, tn) in enumerate([('Backup & restore', 'RTO hours–days', 'RPO hours', 'amber'), ('Pilot light', 'RTO tens of minutes', 'RPO minutes', 'blue'), ('Warm standby', 'RTO minutes', 'RPO seconds–minutes', 'green'), ('Multi-site active/active', 'RTO ≈ 0', 'RPO ≈ 0', 'violet')]):
        x = 70 + i * 140; y = 160 - i * 40
        o += box(x, y, 128, 52, tn, rx=8) + t(x + 64, y + 18, n, 7.6, 'ink', bold=True) + t(x + 64, y + 32, r, 6.8, 'ink') + t(x + 64, y + 44, p, 6.8, 'ink')
    return o
DRF = bigfig('Chart: four disaster recovery strategies from bottom-left to top-right — backup and restore (RTO hours to days), pilot light (tens of minutes), warm standby (minutes), multi-site active/active (near zero) — with cost increasing.', drfig(), h=246)

picture = ('  <p>Four words that describe four different goals:</p>\n' + THREE + '\n  <p>And when a whole Region or your data is at risk, choose a disaster-recovery strategy by how fast you must be back:</p>\n' + DRF)

# ------------------------------------------------------------------ how: an AZ failure
RN = {'u': (4, 54, 54, 50, 'phone', 'Customers', 'orders'), 'lb': (66, 4, 60, 46, 'lb', 'Load bal.', '3 AZs'), 'a': (66, 104, 60, 46, 'server', 'AZ 1a', '2 VMs'),
      'b': (138, 54, 62, 50, 'server', 'AZ 1b ✘', 'failed'), 'hc': (212, 4, 64, 46, 'shield', 'Health chk', 'fails ×2'), 'asg': (212, 104, 64, 46, 'meter', 'Auto Scaling', 'replace'), 'db': (290, 54, 66, 50, 'db', 'DB failover', 'standby → primary')}
RS = [dict(on=['u', 'lb', 'a', 'b'], hot='b', move=(126, 30, 150, 60, 'power'), head='Step 1 · An AZ fails', text='Servers in AZ 1b stop responding. Requests already sent there time out — the only', text2='moment customers could notice (a retry fixes it).', svc='Failure domain = AZ'),
      dict(on=['u', 'lb', 'a', 'b', 'hc'], hot='hc', move=(200, 70, 222, 40, 'probe'), head='Step 2 · Health checks detect it', text='The load balancer’s checks to 1b fail twice in a row (e.g. 2 × 10 s) and those', text2='targets are marked unhealthy.', svc='ELB / Azure LB probes / Google health checks'),
      dict(on=['u', 'lb', 'a', 'b', 'hc'], hot='lb', move=(58, 70, 70, 40, 'reroute'), head='Step 3 · Traffic shifts to healthy AZs', text='New requests go only to 1a and 1c. Capacity is lower, so each AZ should be', text2='sized to carry the load of a lost AZ (static stability, N+1).', svc='Spread across ≥3 AZs: lose one = lose 33%'),
      dict(on=['u', 'lb', 'a', 'b', 'hc', 'asg'], hot='asg', move=(244, 50, 244, 104, 'launch'), head='Step 4 · Auto Scaling replaces capacity', text='The group launches replacement instances in the healthy AZs to get back to the', text2='desired count — if capacity and quotas there allow.', svc='ASG / VM Scale Set / regional MIG'),
      dict(on=list(RN), hot='db', move=(276, 127, 298, 90, 'promote'), head='Step 5 · The database fails over', text='Multi-AZ RDS promotes the synchronous standby and moves the DNS name — typically', text2='60–120 seconds. Apps reconnect; no committed data is lost (RPO 0).', svc='RDS Multi-AZ · Azure SQL zone-redundant · Cloud SQL HA')]
AZFAIL = flow_anim('What happens when one Availability Zone fails', 'Five steps between a failure and a recovered service — without a human.', 'AZ failure', 'Animation: an availability zone fails; health checks detect it; the load balancer routes to healthy zones; auto scaling replaces instances; the database fails over to its standby.', RN, RS, hid='azfail')

# ------------------------------------------------------------------ types
def mapfig():
    o = t(320, 16, 'Seven ways to stay up and come back', 11, 'ink', bold=True)
    items = [('1', 'Redundancy (N+1)', 'no single point of failure', 'blue'), ('2', 'Multi-AZ active-active', 'HA inside a Region', 'green'), ('3', 'Backup & restore', 'cheapest DR', 'amber'),
             ('4', 'Pilot light', 'core data live, rest off', 'blue'), ('5', 'Warm standby', 'small copy running', 'green'), ('6', 'Multi-site active/active', 'two Regions serving', 'violet'), ('7', 'Fault isolation', 'bulkheads, cells, degrade', 'red')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 7.6, 'ink', bold=True) + t(x + 78, y + 54, b, 6.8, 'ink2')
    o += t(320, 210, '1–2 = high availability · 3–6 = disaster-recovery strategies · 7 = limit the blast radius of any failure.', 7.6, 'ink2')
    return o
MAP = bigfig('Map of seven resilience techniques: redundancy, multi-AZ active-active, backup and restore, pilot light, warm standby, multi-site active/active, fault isolation.', mapfig(), h=222)

def steps3(k, items, tones, caption):
    o = ''
    for i, l in enumerate(items):
        on = i <= k
        o += box(20 + i * 112, 34, 100, 74, tones[i] if on else 'card', rx=8)
        for j, w in enumerate(l.split('|')): o += t(70 + i * 112, 60 + j * 14, w, 7.2 if j == 0 else 6.6, 'ink', bold=(j == 0))
    return o + t(180, 132, caption, 7.2, 'ink', bold=True)

def a_red(k):
    o = t(180, 12, ['One of everything', 'N+1: one spare', 'Spare takes over'][k], 9, 'ink', bold=True)
    for i in range(4):
        tn = 'card' if (k == 0 and i > 0) else ('red' if (k == 2 and i == 0) else ('green' if i < 3 or k else 'card'))
        if k == 0 and i == 0: tn = 'amber'
        lab = ['web', 'web', 'web', 'spare'][i] if k else ['web', '', '', ''][i]
        if k == 2 and i == 0: lab = 'web ✘'
        o += box(30 + i * 78, 40, 66, 56, tn, rx=6) + t(63 + i * 78, 72, lab, 7.4, 'ink', bold=True)
    o += t(180, 124, ['if this one box fails, the service stops (SPOF)', 'size for peak + one extra (or one extra AZ)', 'the remaining capacity still carries peak load'][k], 7.2, 'ink', bold=True)
    return o
A_RED = cap([a_red(k) for k in range(3)], [('SPOF', 'A single server, disk or link whose failure stops the whole service.', ''), ('N+1', 'Run one more unit than the peak needs.', ''), ('Absorb', 'When one fails, the others carry the load while it is replaced.', '')],
    'Redundancy in action', 'Remove single points of failure.', 'Redundancy', 'Animation: a single server as a single point of failure; N+1 servers; one fails and the rest carry the load.', 'r1anim')
T1 = vtype(1, 'Redundancy (no single point of failure, N+1)', 'blue',
    '<b>Redundancy</b> means duplicating critical components — servers, disks, network paths, power, whole zones — so that the failure of any one does not stop the service; <b>N+1</b> (or N+2) sizing keeps at least one spare beyond the capacity the peak load needs.',
    'A car with a spare tyre — or better, a bus with six wheels at the back: one puncture and it still drives.',
    'TiffinGo needs 4 servers at Diwali peak; it runs 6 across three AZs (2 per AZ). Losing a whole AZ leaves 4 — exactly the peak need.',
    'Load balancers with multiple targets, RAID/replicated storage (EBS, managed disks), Multi-AZ databases, redundant Direct Connect/ExpressRoute links, dual VPN tunnels.',
    '', A_RED,
    'any component whose failure would stop customers — find SPOFs on your architecture diagram first.',
    'you duplicate without health checks and automatic failover — a spare nobody switches to is useless.',
    plain='Keeping a spare of everything important, so that when one part breaks, the spare quietly takes over.',
    how=[('Find SPOFs', 'Walk the request path: DNS, LB, app, cache, DB, network links.'), ('Duplicate', 'Two or more of each, in different failure domains.'), ('Size N+1', 'Peak capacity plus spare (per AZ lost).'), ('Detect', 'Health checks per component.'), ('Fail over automatically', 'LB routing, DB promotion, DNS failover.')],
    words=[('SPOF', 'single point of failure'), ('N+1', 'needed amount plus one spare'), ('failure domain', 'things that fail together, e.g. one AZ'), ('failover', 'switching to the spare')],
    diff=table(['', 'Redundancy', 'Backup'], [['Protects against', 'component failure (now)', 'data loss, corruption (later restore)'], ['Recovery time', 'seconds', 'minutes to hours'], ['Copies mistakes?', 'yes (replicas copy deletes)', 'no (point in time)']], minw=440),
    where=['Web/app tiers', 'Databases (replicas, Multi-AZ)', 'Network links and power'],
    realworld='Cloud data centres themselves are built N+1 or 2N for power and cooling — but a whole facility can still fail (fire, cooling, fibre cuts), which is why providers expose AZs and ask you to add your own redundancy across them.',
    pro='Redundant components that share a hidden dependency are not redundant: two servers in different AZs that both read one config file from a single-AZ NFS server still have a SPOF. Draw dependencies, not just boxes.')

def a_maz(k):
    o = t(180, 12, ['Spread across AZs', 'Synchronous DB standby', 'One AZ lost, service continues'][k], 9, 'ink', bold=True)
    for i in range(3):
        bad = k == 2 and i == 1
        o += box(20 + i * 112, 30, 100, 90, 'red' if bad else 'card', rx=8) + t(70 + i * 112, 44, f'AZ 1{"abc"[i]}', 7.4, 'ink2', bold=True)
        o += box(30 + i * 112, 52, 80, 24, 'red' if bad else 'blue', rx=4) + t(70 + i * 112, 68, 'app ×2', 7, 'ink')
        if i != 1: o += box(30 + i * 112, 84, 80, 26, ('green' if i == 0 else ('amber' if k < 2 else 'green')) if k >= 1 else 'card', rx=4) + t(70 + i * 112, 101, ['DB primary', '', 'DB standby' if k < 2 else 'DB (ok)'][i] if k >= 1 else '', 6.8, 'ink')
    if k == 1: o += arrow(112, 97, 254, 97) + t(180, 92, 'sync copy', 6.4, 'ink2')
    o += t(180, 140, ['the load balancer spreads requests over all zones', 'every write is committed in two AZs before “OK”', 'zones 1a and 1c carry on; the failed zone is replaced later'][k], 7.2, 'ink', bold=True)
    return o
A_MAZ = cap([a_maz(k) for k in range(3)], [('Spread', 'App instances run in every AZ behind one load balancer.', ''), ('Replicate', 'The database writes synchronously to a standby in another AZ.', ''), ('Survive', 'An AZ failure removes a third of capacity; the rest keeps serving.', '')],
    'Multi-AZ in action', 'High availability inside one Region.', 'Multi-AZ', 'Animation: app instances in three zones; database primary with a synchronous standby; one zone fails and service continues.', 'r2anim')
T2 = vtype(2, 'Multi-AZ (active-active within a Region)', 'green',
    'A <b>multi-AZ architecture</b> runs a workload’s components in two or more Availability Zones of one Region at the same time — stateless tiers active in every zone behind a load balancer, data tiers with synchronous replication to a standby or zone-redundant service — so the loss of a zone causes at most a brief disruption.',
    'A restaurant chain with three kitchens in the same city: if one kitchen’s gas fails, orders are cooked in the other two, still hot and on time.',
    'TiffinGo’s app runs in ap-south-1a, 1b and 1c behind one ALB; the PostgreSQL database is RDS Multi-AZ; Redis has a replica in another AZ; S3 is regional by design. Last night’s AZ incident went unnoticed.',
    'ELB + Auto Scaling across AZs, RDS/Aurora Multi-AZ, EFS, S3; Azure zone-redundant services (VMSS zones, zone-redundant SQL, ZRS storage); Google regional MIGs, regional persistent disks, Cloud SQL HA, regional GKE clusters.',
    '', A_MAZ,
    'almost every production workload — it is the default high-availability design in the cloud and needed for the 99.99% EC2 SLA (Lesson 5.4).',
    'you think multi-AZ protects against Region-wide problems, bad deployments or deleted data — it does not.',
    plain='Running copies of your app in two or three separate data-centre groups of the same city, so if one has a problem, the others keep serving.',
    how=[('Subnets per AZ', 'Public and private subnets in each zone (Lesson 6.3).'), ('Stateless tier', 'Instances in every AZ; LB health checks; ASG keeps counts.'), ('Stateful tier', 'Synchronous replication or zone-redundant managed service.'), ('Static stability', 'Each AZ sized so the rest carry the load without new launches.'), ('Failover', 'Automatic: LB stops routing, DB promotes standby.')],
    words=[('synchronous replication', 'a write is confirmed only after both copies have it'), ('stateless', 'keeps no user data locally, any copy can serve any request'), ('zone-redundant', 'automatically spread across zones by the provider')],
    diff=table(['', 'Multi-AZ', 'Multi-Region'], [['Protects against', 'data-centre / zone failure', 'Region-wide events, regulatory needs'], ['Replication', 'synchronous (RPO 0)', 'usually asynchronous (RPO seconds+)'], ['Latency between sites', '~1–2 ms', 'tens of ms'], ['Cost and complexity', 'moderate', 'high']], minw=520),
    where=['Every production web/API tier', 'Databases needing RPO 0 for zone failures', 'Kubernetes regional clusters'],
    realworld='AWS designs AZs to be physically separate by a meaningful distance (many kilometres) yet within about 100 km of each other, so synchronous replication between them is fast enough for databases — the key that makes multi-AZ practical.',
    pro='Cross-AZ traffic is billed (about $0.01/GB each way on EC2), so chatty services spread across AZs can cost more than expected — “AZ-affinity” routing (send traffic to targets in the same AZ when healthy) reduces both cost and latency.')

def a_dr(k, kind):
    labels = {'br': ['Backups|copied to DR Region', 'Disaster|Region down', 'Restore|build everything|from backups'],
              'pl': ['Core data|replicated live', 'Disaster|switch on', 'Scale up|app servers|from images'],
              'ws': ['Small full copy|running in DR', 'Disaster|promote DB', 'Scale out|to full size|shift traffic'],
              'aa': ['Both Regions|serve users', 'One Region fails', 'Other Region|takes all traffic|DNS / global LB']}[kind]
    cap_ = {'br': ['nightly snapshots and DB backups go to Hyderabad', 'nothing is running in the DR Region yet', 'hours to days: infrastructure from IaC, data from backups'],
            'pl': ['database replica always on; servers off (images ready)', 'turn on the pilot light', 'tens of minutes to full service'],
            'ws': ['a scaled-down but complete copy handles test traffic', 'promote the replica to primary', 'minutes to full capacity'],
            'aa': ['traffic split by latency or geography', 'health checks remove it from DNS / global LB', 'near-zero downtime; data conflicts must be designed for'] }[kind][k]
    o = t(180, 12, ['Normal days', 'Disaster', 'Recovery'][k], 9, 'ink', bold=True)
    return o + steps3(k, labels, ['blue', 'red', 'green'], cap_)
A_BR = cap([a_dr(k, 'br') for k in range(3)], [('Normal', 'Backups and IaC templates are copied to another Region.', ''), ('Disaster', 'The primary Region is unavailable; nothing runs in DR yet.', ''), ('Recover', 'Create infrastructure from templates and restore data — hours to days.', '')],
    'Backup and restore in action', 'Cheapest DR: copies, and a plan to rebuild.', 'Backup & restore', 'Animation: backups copied to another Region; disaster; restore everything from backups.', 'r3anim')
A_PL = cap([a_dr(k, 'pl') for k in range(3)], [('Normal', 'Only the core — the database replica — runs in the DR Region.', ''), ('Disaster', 'The team “turns up the pilot light”.', ''), ('Recover', 'App servers start from images and scale up — tens of minutes.', '')],
    'Pilot light in action', 'Core data live, everything else ready to start.', 'Pilot light', 'Animation: a live database replica in the DR Region; disaster; app servers launched from images.', 'r4anim')
A_WS = cap([a_dr(k, 'ws') for k in range(3)], [('Normal', 'A smaller but fully working copy runs in the DR Region.', ''), ('Disaster', 'Promote the database and send traffic to DR.', ''), ('Recover', 'Scale the copy out to full size — minutes.', '')],
    'Warm standby in action', 'A small full copy, always running.', 'Warm standby', 'Animation: a scaled-down full copy in the DR Region; disaster; promoted and scaled to full size.', 'r5anim')
A_AA = cap([a_dr(k, 'aa') for k in range(3)], [('Normal', 'Both Regions serve real users at the same time.', ''), ('Failure', 'One Region fails health checks.', ''), ('Recover', 'DNS / global load balancing sends all users to the healthy Region.', '')],
    'Multi-site active/active in action', 'Two Regions, both live.', 'Active/active', 'Animation: two Regions serving traffic; one fails; the other takes all traffic.', 'r6anim')

T3 = vtype(3, 'Backup and restore (DR)', 'amber',
    '<b>Backup and restore</b> is the simplest disaster-recovery strategy: data is backed up regularly and copied to another Region (and ideally another account), infrastructure is defined as code, and after a disaster the environment is rebuilt and the data restored — the lowest cost, with the longest RTO (hours to days) and an RPO equal to the backup interval.',
    'Keeping photocopies of all your documents at your parents’ house in another city: cheap, but after a fire you still need days to rebuild your files.',
    'TiffinGo’s internal reporting system copies nightly snapshots and database backups to Hyderabad and a separate backup account. If Mumbai were lost, the team would rebuild it from templates in about 6 hours, losing at most one day of report data — acceptable for an internal tool.',
    'AWS Backup (cross-Region, cross-account copy, Vault Lock), EBS/RDS snapshot copy, S3 Cross-Region Replication; Azure Backup with cross-region restore, GRS vaults; Google Backup and DR, multi-regional snapshot storage.',
    '', A_BR,
    'RTO of hours and RPO of hours are acceptable, or as the baseline for every workload (every system needs backups anyway).',
    'customers cannot wait hours — and never without regular restore tests.',
    plain='Keep copies of your data in another city, and if disaster strikes, rebuild everything there from the copies. Cheap but slow.',
    how=[('Back up', 'Snapshots, DB backups and logs on a schedule.'), ('Copy away', 'To another Region and account; make them immutable.'), ('Codify', 'All infrastructure in templates (Lesson 6.4).'), ('Restore', 'Deploy templates in the DR Region, restore data, switch DNS.'), ('Test', 'Restore drills to measure the real RTO.')],
    words=[('RTO', 'recovery time objective — how long you may be down'), ('RPO', 'recovery point objective — how much recent data you may lose'), ('cross-Region copy', 'a backup duplicated to another Region'), ('immutable', 'cannot be changed or deleted for a period')],
    diff=table(['Strategy', 'RTO', 'RPO', 'Running in DR', 'Cost'], [['Backup & restore', 'hours–days', 'hours', 'nothing', '$'], ['Pilot light', '10s of minutes', 'minutes', 'data tier', '$$'], ['Warm standby', 'minutes', 'seconds–minutes', 'small full copy', '$$$'], ['Multi-site active/active', '≈ 0', '≈ 0 (design-dependent)', 'full copy', '$$$$']], minw=560),
    where=['Internal tools and reporting', 'Dev/test environments', 'Baseline protection for every system'],
    realworld='Ransomware has made the “separate account + immutable vault” part essential: attackers with admin credentials delete in-Region backups first; locked, cross-account copies survive.',
    pro='An untested backup is a hope, not a plan: teams often discover during the first real restore that snapshots lack a dependency (KMS key permissions in the other Region, a missing parameter store value). Restore drills measure the true RTO.')
T4 = vtype(4, 'Pilot light (DR)', 'blue',
    '<b>Pilot light</b> keeps the core of a workload — usually the data tier — continuously replicated and running in the recovery Region, while application servers and other components exist only as images and templates (switched off or at zero); during a disaster they are started and scaled up, giving an RTO of tens of minutes and an RPO of minutes or less.',
    'The small flame in a gas geyser: almost nothing burns all day, but turning the knob brings full heat in seconds.',
    'TiffinGo’s customer database has a cross-Region read replica in Hyderabad; AMIs and the launch template are copied there and the Auto Scaling group is defined at size 0. A runbook promotes the replica and sets the group to 6 — about 30 minutes to full service.',
    'Aurora Global Database / RDS cross-Region read replicas, AMI copy, ASG at 0, Elastic Disaster Recovery; Azure SQL geo-replication, Azure Site Recovery; Cloud SQL cross-region replicas, Spanner multi-region.',
    '', A_PL,
    'the data must be nearly current (low RPO) but tens of minutes of downtime are acceptable.',
    'nobody has practised the switch-on — the first attempt during a real disaster usually fails.',
    plain='Keep only the most important part (the data) live in another city; everything else is ready to switch on when needed.',
    how=[('Replicate data', 'Asynchronous cross-Region replica of the database and objects.'), ('Prepare compute', 'Images, templates and scaling groups at size 0 in DR.'), ('Detect', 'Decide (often a human) to fail over.'), ('Ignite', 'Promote replica, scale up servers, update config.'), ('Switch traffic', 'DNS failover / global LB.')],
    words=[('read replica', 'a continuously updated read-only copy'), ('promote', 'turn a replica into a writable primary'), ('asynchronous', 'copies shortly after the write, not during it')],
    diff=table(['', 'Pilot light', 'Warm standby'], [['App servers in DR', 'off (images only)', 'running, scaled down'], ['Can serve traffic immediately', 'no', 'yes, at reduced capacity'], ['Cost', 'lower', 'higher']], minw=440),
    where=['Customer databases with moderate RTO', 'E-commerce back-office systems', 'Regulated workloads needing a second Region'],
    realworld='AWS Elastic Disaster Recovery continuously replicates servers’ disks to a low-cost staging area in another Region and launches full instances only during a drill or disaster — a managed pilot light.',
    pro='Pilot light depends on the control plane in the DR Region during the disaster (to launch instances). During large events many customers launch at once — reserve capacity (Capacity Reservations) for critical tiers if your RTO is strict.')
T5 = vtype(5, 'Warm standby (DR)', 'green',
    '<b>Warm standby</b> runs a scaled-down but fully functional copy of the whole workload in the recovery Region at all times, with data continuously replicated; during a disaster the copy is promoted and scaled out to full production capacity, giving an RTO of minutes.',
    'A second cricket team that plays every practice match: smaller squad, but fully trained — on match day you just add players.',
    'TiffinGo’s ordering API runs in Hyderabad on 2 small instances with an Aurora secondary Region, serving internal test traffic. Route 53 failover sends customers there if Mumbai’s health checks fail, and Auto Scaling grows it to 6 within minutes.',
    'Aurora Global Database, DynamoDB global tables, Route 53 failover routing, ASG; Azure Front Door/Traffic Manager, geo-replicated SQL, Site Recovery; Cloud Load Balancing, Cloud SQL replicas, regional MIGs.',
    '', A_WS,
    'customer-facing systems that need recovery in minutes but cannot justify a full second Region.',
    'the standby is never tested with real traffic — configuration drift makes it fail when needed.',
    plain='A small but complete working copy of your app runs in another city all the time; in a disaster it is quickly made bigger and takes over.',
    how=[('Run small', 'All tiers deployed in DR at reduced size.'), ('Replicate', 'Data asynchronously; config via the same IaC.'), ('Verify', 'Synthetic or internal traffic proves it works.'), ('Fail over', 'Promote data, scale out, switch DNS/LB.'), ('Fail back', 'Re-sync and return when the primary is healthy.')],
    words=[('standby', 'a copy waiting to take over'), ('fail back', 'returning to the original site after recovery'), ('synthetic traffic', 'test requests that imitate users')],
    diff=table(['', 'Warm standby', 'Multi-site active/active'], [['DR copy serves real users normally', 'no (or little)', 'yes'], ['Capacity in DR', 'reduced', 'full'], ['Data conflicts', 'rare (one writer)', 'must be designed for']], minw=460),
    where=['Customer-facing APIs and portals', 'Payment front-ends', 'SaaS products with strict SLAs'],
    realworld='Aurora Global Database replicates with typical lag under a second and AWS documents cross-Region managed failover in about a minute — enough for warm-standby RTOs measured in minutes.',
    pro='DNS failover is only as fast as client caching: a 300-second TTL can keep some users on the dead Region for minutes. Use low TTLs on failover records or anycast-based global load balancing (Global Accelerator, Front Door, Google global LB).')
T6 = vtype(6, 'Multi-site active/active (DR)', 'violet',
    '<b>Multi-site active/active</b> runs full production capacity in two or more Regions simultaneously, each serving live traffic, with data replicated between them; when one Region fails, traffic is routed to the others with near-zero downtime — the fastest and most expensive strategy, requiring the application to handle multi-Region data consistency.',
    'Two branches of a bank in different cities, both open and serving customers; if one closes for a flood, customers simply go to the other.',
    'TiffinGo will not need this soon — but a national payments partner does: it serves North India from Delhi and South India from Hyderabad, and either Region can take 100% of traffic.',
    'DynamoDB global tables, Aurora Global Database (write forwarding), S3 Multi-Region Access Points, Route 53 latency routing, Global Accelerator; Cosmos DB multi-region writes, Front Door; Spanner multi-region, Firestore multi-region, global external Application Load Balancer.',
    '', A_AA,
    'downtime is extremely expensive or regulated, and the business can fund double capacity and engineering effort.',
    'the data model cannot tolerate concurrent writes in two places — conflicting updates (two discounts applied to one order) need careful design.',
    plain='Two complete copies of the app in two cities, both serving customers all the time. If one city has a problem, the other already handles everyone.',
    how=[('Full deploy', 'Identical stacks in each Region from the same IaC.'), ('Route users', 'Latency-based DNS or global load balancer.'), ('Replicate data', 'Multi-Region databases; decide conflict resolution.'), ('Health-based routing', 'Unhealthy Region removed automatically.'), ('Capacity', 'Each Region can absorb the other’s load.')],
    words=[('global table', 'a database table replicated and writable in several Regions'), ('conflict resolution', 'deciding which of two simultaneous updates wins'), ('latency routing', 'sending users to the fastest Region')],
    diff=table(['', 'Active/active', 'Active/passive (warm/pilot)'], [['Users served by both', 'yes', 'no'], ['Failover', 'automatic, instant', 'promotion step'], ['Data writes', 'possibly in both', 'one primary']], minw=440),
    where=['Payments, trading, large consumer platforms', 'Global apps needing low latency everywhere', 'Systems with regulatory uptime demands'],
    realworld='Google Cloud Spanner offers multi-region configurations with an SLA of 99.999% availability, using synchronous replication and TrueTime clocks — one of the few databases designed for strongly consistent active/active across Regions.',
    pro='The CAP theorem says that during a network partition you must choose between consistency and availability; most multi-Region active/active designs choose availability with “last writer wins” or app-level reconciliation — understand what your database does before trusting it with money.')

def a_iso(k):
    o = t(180, 12, ['Without isolation', 'Bulkheads / cells', 'Graceful degradation'][k], 9, 'ink', bold=True)
    if k == 0:
        for i in range(6): o += box(24 + i * 54, 40, 46, 46, 'red', rx=4) + t(47 + i * 54, 68, 'users', 6.6, 'ink')
        o += t(180, 108, 'one bad deployment or noisy customer → everyone down', 7.4, 'ink')
    elif k == 1:
        for i in range(3):
            o += box(24 + i * 112, 34, 100, 66, 'red' if i == 1 else 'green', rx=6) + t(74 + i * 112, 56, f'cell {i + 1}', 7.6, 'ink', bold=True) + t(74 + i * 112, 76, ['33% users', 'fails ✘', '33% users'][i], 6.8, 'ink')
        o += t(180, 116, 'a failure hurts only one cell’s customers', 7.4, 'ink')
    else:
        for i, (n, tn) in enumerate([('orders ✔', 'green'), ('payments ✔', 'green'), ('recommendations ✘', 'amber')]):
            o += box(20 + i * 112, 40, 100, 50, tn, rx=6) + t(70 + i * 112, 69, n, 7, 'ink', bold=True)
        o += t(180, 110, 'show “popular dishes” instead of personal suggestions', 7.4, 'ink')
    o += t(180, 140, ['the blast radius is 100%', 'shuffle sharding / cells limit the blast radius', 'core flows keep working; extras switch off'][k], 7.2, 'ink', bold=True)
    return o
A_ISO = cap([a_iso(k) for k in range(3)], [('No isolation', 'A single shared system means any fault affects all users.', ''), ('Cells', 'Split users into independent cells; a fault stays in one.', ''), ('Degrade', 'Non-essential features fail softly so the core keeps working.', '')],
    'Fault isolation in action', 'Limit the blast radius.', 'Fault isolation', 'Animation: a shared system where one fault affects everyone; isolated cells where a fault affects one cell; graceful degradation keeping core features alive.', 'r7anim')
T7 = vtype(7, 'Fault isolation and graceful degradation', 'red',
    '<b>Fault isolation</b> limits the <b>blast radius</b> of a failure by partitioning a system into independent units — bulkheads, cells, shards, separate accounts and Regions — so that a fault, bad deployment or overload in one unit does not spread; <b>graceful degradation</b> keeps core functions running by switching off or simplifying non-essential features when dependencies fail.',
    'A ship divided into watertight compartments: a hole floods one compartment, not the whole ship — and the captain switches off the lights in the dining hall to keep the engines running.',
    'TiffinGo deploys new versions to one city’s cell first (Pune), then the rest. When the recommendation service timed out last month, the app showed “popular dishes” instead and orders continued normally.',
    'AWS cell-based architecture guidance, shuffle sharding (Route 53), separate accounts via Organizations, AppConfig feature flags; Azure deployment stamps, Front Door; Google Cloud project/Region isolation, feature flags; circuit breakers (Lesson 7.5).',
    '', A_ISO,
    'one failure or one customer could otherwise affect everyone — multi-tenant SaaS, large platforms, risky deployments.',
    'you add so many partitions that operating them becomes the main risk — start with accounts/Regions and staged deployments.',
    plain='Splitting the system into separate compartments so a problem in one part does not sink the whole app — and turning off nice-to-have features to keep the important ones working.',
    how=[('Partition', 'Cells/shards by customer, city or tenant; separate accounts.'), ('Independent stacks', 'Each cell has its own compute and data.'), ('Route', 'A thin routing layer maps users to cells.'), ('Stage changes', 'Deploy to one cell, watch, then continue.'), ('Degrade', 'Timeouts, fallbacks and feature flags for non-critical dependencies.')],
    words=[('blast radius', 'how many users a failure affects'), ('bulkhead', 'a wall that stops a failure spreading'), ('cell', 'a complete independent copy serving a subset of users'), ('feature flag', 'a switch to turn a feature on or off without deploying')],
    diff=table(['', 'Redundancy', 'Fault isolation'], [['Goal', 'survive a component failure', 'limit how far any failure spreads'], ['Helps against bad deployments?', 'no (replicas get the same bug)', 'yes (staged, per cell)']], minw=460),
    where=['Multi-tenant SaaS', 'Large consumer apps', 'Deployment safety (canary, staged rollouts)'],
    realworld='AWS builds many of its own services as cells and uses <b>shuffle sharding</b> in Route 53 — each customer’s domains get a different random combination of name servers, so an attack on one customer rarely affects the exact same set used by another.',
    pro='Most large outages are caused by changes, not hardware. Staged rollouts with automatic rollback (by cell, AZ, then Region) are the most effective fault-isolation tool — the reason providers deploy to one AZ in one Region first.')

SUMMARY = table(['#', 'Technique', 'Protects against', 'Typical RTO', 'Cost'], [
    ['1', 'Redundancy N+1', 'component failure', 'seconds', '$'], ['2', 'Multi-AZ', 'zone failure', 'seconds–2 min', '$$'], ['3', 'Backup & restore', 'Region loss, data loss', 'hours–days', '$'],
    ['4', 'Pilot light', 'Region loss', 'tens of minutes', '$$'], ['5', 'Warm standby', 'Region loss', 'minutes', '$$$'], ['6', 'Multi-site active/active', 'Region loss', '≈ 0', '$$$$'], ['7', 'Fault isolation', 'bad changes, noisy tenants, cascading failure', 'limits impact', '$–$$']], minw=600)
CHECK = ('  <h3>Check yourself: which strategy fits?</h3>\n' +
    qx('A. An internal HR app; 1 day of downtime and 1 day of data loss acceptable.', ['Active/active', 'Backup & restore', 'Warm standby', 'Pilot light'], 1, 'Cheapest that meets RTO/RPO.') +
    qx('B. An order API that must recover from a Region outage within 10 minutes.', ['Backup & restore', 'Warm standby', 'Single AZ', 'Instance store'], 1, 'Minutes RTO.') +
    qx('C. Stay up when one data centre in Mumbai fails.', ['Multi-AZ', 'Bigger instance', 'Cross-Region backup only', 'CDN only'], 0, 'High availability in-Region.') +
    qx('D. A bad deployment should affect at most 10% of users.', ['More replicas', 'Cells and staged rollouts', 'Larger database', 'Spot'], 1, 'Fault isolation.'))

TYPES = ('  <p>Seven techniques, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['Why can a 300-second DNS TTL break your “5-minute” failover?', 'What does the CAP theorem force multi-Region active/active designs to choose?', 'Why do replicas not protect you from a bad deployment?'], 'types 5, 6 and 7') + MAP
         + jump(['Redundancy', 'Multi-AZ', 'Backup & restore', 'Pilot light', 'Warm standby', 'Active/active', 'Isolation']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('RTO', 'Maximum acceptable downtime after a disaster.', 'Decides the DR strategy and its cost.', '“Order API: 15 minutes.”'),
    ('RPO', 'Maximum acceptable data loss measured in time.', 'Decides backup frequency or replication.', '“Orders: 0; reports: 24 hours.”'),
    ('Health check', 'Automated probe of a component.', 'Triggers failover and replacement.', 'LB target checks, Route 53 checks.'),
    ('Failover', 'Switching to a standby.', 'Can be automatic (Multi-AZ DB) or manual (Region DR).', 'RDS Multi-AZ, Route 53 failover, Front Door.'),
    ('Static stability', 'Works without changing anything during a failure.', 'Control planes may be impaired in big events.', 'Pre-provisioned N+1 capacity per AZ.'),
    ('Game day / DR drill', 'Planned practice of failure.', 'Finds the gaps before real disasters.', 'Fault Injection Service, Chaos Studio, scripted drills.')])

DEEP = ('  <h3>Availability maths for redundancy</h3>\n  <p>If one server is up 99% of the time and failures are independent, two in parallel give 1 − 0.01² = <b>99.99%</b>; three give 99.9999%. Real failures are correlated (same AZ, same bug, same deployment), so spreading across failure domains matters more than the count (Lesson 5.4).</p>\n'
    '  <h3>Choosing RTO and RPO with the business</h3>\n' + table(['System', 'Cost of 1 hour down', 'RTO', 'RPO', 'Strategy'], [['Order API', 'high (lost orders)', '15 min', '≈ 0', 'Multi-AZ + warm standby'], ['Customer database', 'high', '30 min', '< 1 min', 'Multi-AZ + pilot light / global DB'], ['Analytics', 'low', '1 day', '24 h', 'backup & restore'], ['Marketing site', 'medium', '1 h', '1 day', 'static site + CDN + backup']], minw=600) +
    '\n  <h3>Shared responsibility for resilience</h3>\n  <p>The provider is responsible for the resilience <i>of</i> the cloud (AZs, Regions, services meeting their SLAs); you are responsible for resilience <i>in</i> the cloud — using multiple AZs, backups, DR plans and testing. A single-AZ design is a customer choice, not a provider failure.</p>')

clouds = vendor_tabs('<p><b>AWS:</b> multiple AZs per Region, ELB + Auto Scaling, RDS/Aurora Multi-AZ, Aurora Global Database, DynamoDB global tables, S3 replication, AWS Backup, Elastic Disaster Recovery, Route 53 failover, Global Accelerator, Resilience Hub, Fault Injection Service.</p>',
    '<p><b>Azure:</b> availability zones, VM Scale Sets, zone-redundant services, region pairs, geo-replication, Azure Site Recovery, Azure Backup with cross-region restore, Traffic Manager, Front Door, Chaos Studio.</p>',
    '<p><b>Google Cloud:</b> zones and regional resources (regional MIGs, regional persistent disks, regional GKE), Cloud SQL HA and cross-region replicas, Spanner multi-region, Backup and DR, global load balancing.</p>') + \
    cloud3([['Group across zones', 'Auto Scaling group (multi-AZ)', 'VM Scale Set (zones 1 2 3)', 'regional managed instance group'], ['HA database', 'RDS Multi-AZ', 'zone-redundant Azure SQL', 'Cloud SQL HA'], ['Cross-Region DB', 'Aurora Global Database', 'SQL geo-replication / failover groups', 'Cloud SQL cross-region replica / Spanner'], ['DR orchestration', 'Elastic Disaster Recovery', 'Azure Site Recovery', 'Backup and DR'], ['Chaos testing', 'Fault Injection Service', 'Chaos Studio', '—']])

MOCKQ.extend([
 (mock('aws', ['EC2', 'Auto Scaling groups', 'Create Auto Scaling group'], ['Launch templates', 'Auto Scaling groups', 'Instances'], 'Auto Scaling groups',
       [('Auto Scaling group name', 'tiffingo-asg'), ('Launch template', '▾ tiffingo-lt'), ('Availability Zones and subnets', '▾ ap-south-1a, ap-south-1b (default subnets)'), ('Desired · Min · Max', '2 · 2 · 4')], 'Create Auto Scaling group'),
  mock('az', ['Home', 'Virtual machine scale sets', 'Create'], ['Basics', 'Spot', 'Disks', 'Networking', 'Scaling', 'Management', 'Health'], 'Basics',
       [('Scale set name', 'tiffingo-vmss'), ('Region · Availability zone', '▾ Central India · Zones 1, 2'), ('Orchestration mode', '( ) Flexible'), ('Image · Size', 'Ubuntu Server 24.04 LTS · Standard_B1s'), ('Initial instance count', '2')], 'Review + create'),
  mock('gcp', ['Compute Engine', 'Instance groups', 'Create instance group'], ['Instance groups', 'Instance templates', 'Health checks'], 'Instance groups',
       [('Name · Instance template', 'tiffingo-mig · tiffingo-tpl'), ('Location', '( ) Multiple zones — asia-south1 (a, b)'), ('Autoscaling mode', '▾ Off: do not autoscale'), ('Number of instances', '2')], 'Create')),
 (mock('aws', ['EC2', 'Auto Scaling groups', 'tiffingo-asg'], ['Details', 'Activity', 'Automatic scaling', 'Instance management'], 'Activity',
       [('Activity history', 'Terminating EC2 instance: i-0abc… (health check)'), ('', 'Launching a new EC2 instance: i-0def… in ap-south-1a')], 'Refresh'),
  mock('az', ['Home', 'tiffingo-vmss', 'Instances'], ['Overview', 'Instances', 'Scaling', 'Health and repair'], 'Instances',
       [('Instances', 'tiffingo-vmss_1 (zone 1) · tiffingo-vmss_2 (zone 2)'), ('Health and repair', '[x] Enable automatic repairs (needs health monitoring)')], 'Delete'),
  mock('gcp', ['Compute Engine', 'Instance groups', 'tiffingo-mig'], ['Overview', 'Details', 'Monitoring', 'Errors'], 'Overview',
       [('Instances', 'tiffingo-mig-x1 (asia-south1-a) · tiffingo-mig-y2 (asia-south1-b)'), ('Status', 'Recreating instance tiffingo-mig-x1')], 'Refresh')),
 (mock('aws', ['EC2', 'Snapshots', 'Copy snapshot'], ['Volumes', 'Snapshots', 'Lifecycle Manager'], 'Snapshots',
       [('Source snapshot', 'snap-0abc… (ap-south-1)'), ('Destination Region', '▾ Asia Pacific (Hyderabad) ap-south-2'), ('Encrypt this snapshot', '[x] (uses the KMS key in Hyderabad)')], 'Copy snapshot'),
  mock('az', ['Home', 'Snapshots', 'Create snapshot'], ['Basics', 'Encryption', 'Networking', 'Advanced', 'Review + create'], 'Basics',
       [('Region', '▾ South India'), ('Source type · Source', '▾ Snapshot · dr-src-snap (Central India)'), ('Snapshot type', '( ) Incremental')], 'Review + create'),
  mock('gcp', ['Compute Engine', 'Snapshots', 'Create a snapshot'], ['Disks', 'Snapshots', 'Images'], 'Snapshots',
       [('Name · Source disk', 'dr-snap · dr-disk'), ('Location', '( ) Regional — asia-south2 (Delhi)')], 'Create')),
])

STEP1 = ('1 · Run two servers across two zones', tri(
    (['[[EC2]] → [[Launch templates]] → [[Create launch template]] → name <code>tiffingo-lt</code>, Amazon Linux 2023, t3.micro → [[Create]].', '[[Auto Scaling groups]] → [[Create Auto Scaling group]] → template tiffingo-lt → default VPC, pick subnets in [[ap-south-1a]] and [[ap-south-1b]].', 'Desired 2, min 2, max 4 → [[Create Auto Scaling group]] → [[Instance management]]: one instance per AZ.'],
     "aws ec2 create-launch-template --launch-template-name tiffingo-lt --launch-template-data \\\n  '{\"ImageId\":\"resolve:ssm:/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64\",\"InstanceType\":\"t3.micro\"}'\nSUBNETS=$(aws ec2 describe-subnets --filters Name=default-for-az,Values=true --query 'Subnets[0:2].SubnetId' --output text | tr '\\t' ',')\naws autoscaling create-auto-scaling-group --auto-scaling-group-name tiffingo-asg \\\n  --launch-template LaunchTemplateName=tiffingo-lt --min-size 2 --max-size 4 --desired-capacity 2 \\\n  --vpc-zone-identifier \"$SUBNETS\"\nsleep 60\naws autoscaling describe-auto-scaling-groups --auto-scaling-group-names tiffingo-asg \\\n  --query 'AutoScalingGroups[0].Instances[].[InstanceId,AvailabilityZone,HealthStatus]' --output table",
     'two instances in two different AZs, both <code>Healthy</code>.'),
    (['[[Virtual machine scale sets]] → [[Create]] → rg-tiffingo, name <code>tiffingo-vmss</code>, Central India, availability zones [[Zones 1, 2]], orchestration [[Flexible]].', 'Image Ubuntu Server 24.04 LTS, size Standard_B1s, SSH key → [[Scaling]]: initial count 2 → [[Review + create]] → [[Create]].', 'Open it → [[Instances]]: one VM in zone 1 and one in zone 2.'],
     'az group create --name rg-tiffingo --location centralindia\naz vmss create --resource-group rg-tiffingo --name tiffingo-vmss --orchestration-mode Flexible \\\n  --image Ubuntu2404 --vm-sku Standard_B1s --instance-count 2 --zones 1 2 \\\n  --admin-username azureuser --generate-ssh-keys\naz vm list --resource-group rg-tiffingo --query "[].{name:name, zone:zones[0]}" --output table',
     'two VMs, zone 1 and zone 2. If B1s is not available in a zone, use another small size such as Standard_B2ats_v2.'),
    (['[[Instance templates]] → [[Create instance template]] → <code>tiffingo-tpl</code>, e2-micro, Debian 12 → [[Create]].', '[[Instance groups]] → [[Create instance group]] → [[New managed instance group (stateless)]] → template tiffingo-tpl, location [[Multiple zones]] asia-south1 (a, b), autoscaling off, 2 instances → [[Create]].'],
     'gcloud compute instance-templates create tiffingo-tpl --machine-type=e2-micro \\\n  --image-family=debian-12 --image-project=debian-cloud\ngcloud compute instance-groups managed create tiffingo-mig --region=asia-south1 \\\n  --zones=asia-south1-a,asia-south1-b --template=tiffingo-tpl --size=2\ngcloud compute instance-groups managed list-instances tiffingo-mig --region=asia-south1',
     'two instances, one in asia-south1-a and one in asia-south1-b, STATUS RUNNING.')),
    'One group, many zones: the scaling service keeps the count and spreads instances for you.')

STEP2 = ('2 · Kill a server and watch it heal', tri(
    (['[[Instances]] → select one tiffingo-asg instance → [[Instance state]] → [[Terminate instance]].', 'Back in the group → [[Activity]] tab: “Terminating…” then “Launching a new EC2 instance…” within a minute or two.'],
     "VICTIM=$(aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names tiffingo-asg --query 'AutoScalingGroups[0].Instances[0].InstanceId' --output text)\naws ec2 terminate-instances --instance-ids $VICTIM\nsleep 120\naws autoscaling describe-scaling-activities --auto-scaling-group-name tiffingo-asg --max-items 3 \\\n  --query 'Activities[].[StartTime,Description]' --output table",
     'an activity “Launching a new EC2 instance … due to an instance taken out of service in response to an EC2 health check”.'),
    (['Open one VM of the scale set → [[Delete]]. The scale set now has 1 VM — Azure keeps your new count.', 'Scale set → [[Scaling]] → set instance count back to 2 → [[Save]] (or enable [[Automatic repairs]] with a health probe — repairs start after a 30–90 minute grace period).'],
     'VM=$(az vm list --resource-group rg-tiffingo --query "[0].name" --output tsv)\naz vm delete --resource-group rg-tiffingo --name $VM --yes\naz vmss show --resource-group rg-tiffingo --name tiffingo-vmss --query sku.capacity\naz vmss scale --resource-group rg-tiffingo --name tiffingo-vmss --new-capacity 2\naz vm list --resource-group rg-tiffingo --query "[].{name:name, zone:zones[0]}" --output table',
     'capacity 1 after the delete, then 2 again after scaling. Lesson: on Azure, self-healing needs automatic repairs + health monitoring; deleting is treated as your intent.'),
    (['[[VM instances]] → select one tiffingo-mig instance → [[Delete]].', 'Open the instance group → the instance shows “Recreating” and a new one starts in the same zone.'],
     'V=$(gcloud compute instance-groups managed list-instances tiffingo-mig --region=asia-south1 --format="value(instance.basename())" --limit=1)\nZ=$(gcloud compute instance-groups managed list-instances tiffingo-mig --region=asia-south1 --format="value(instance.segment(-3))" --limit=1)\ngcloud compute instances delete $V --zone=$Z --quiet\nsleep 60\ngcloud compute instance-groups managed list-instances tiffingo-mig --region=asia-south1',
     'the MIG recreates the instance (CURRENT_ACTION RECREATING → NONE) to keep the target size of 2.')),
    'This is self-healing: the group compares desired with actual and fixes the difference — the core of high availability.')

STEP3 = ('3 · Put a backup in another Region (DR)', tri(
    (['[[Volumes]] → [[Create volume]] gp3 1 GiB in ap-south-1a → select → [[Create snapshot]].', '[[Snapshots]] → select it → [[Actions]] → [[Copy snapshot]] → destination [[Asia Pacific (Hyderabad)]] → [[Copy snapshot]] (enable the Hyderabad Region first if it is not enabled).', 'Switch the console to Hyderabad → [[Snapshots]]: the copy appears.'],
     "VOL=$(aws ec2 create-volume --availability-zone ap-south-1a --size 1 --volume-type gp3 --query VolumeId --output text)\naws ec2 wait volume-available --volume-ids $VOL\nSNAP=$(aws ec2 create-snapshot --volume-id $VOL --query SnapshotId --output text)\naws ec2 wait snapshot-completed --snapshot-ids $SNAP\nDR=$(aws ec2 copy-snapshot --source-region ap-south-1 --source-snapshot-id $SNAP --region ap-south-2 --query SnapshotId --output text)\naws ec2 describe-snapshots --snapshot-ids $DR --region ap-south-2 --query 'Snapshots[0].[State,Progress]' --output text",
     'a snapshot ID in ap-south-2 with state <code>pending</code> → <code>completed</code>. ap-south-2 is an opt-in Region; enable it under [[Account]] → [[AWS Regions]] if needed.'),
    (['[[Disks]] → [[Create]] → <code>dr-disk</code>, 4 GiB, Central India → [[Create]]; open it → [[Create snapshot]] → incremental → <code>dr-src-snap</code>.', '[[Snapshots]] → [[Create]] → Region [[South India]], source = snapshot dr-src-snap, incremental → [[Create]] (a cross-region copy).'],
     'az disk create --resource-group rg-tiffingo --name dr-disk --size-gb 4 --location centralindia\naz snapshot create --resource-group rg-tiffingo --name dr-src-snap --source dr-disk --incremental true\nSRC=$(az snapshot show --resource-group rg-tiffingo --name dr-src-snap --query id --output tsv)\naz snapshot create --resource-group rg-tiffingo --name dr-copy-southindia --location southindia \\\n  --source $SRC --incremental true --copy-start true\naz snapshot show --resource-group rg-tiffingo --name dr-copy-southindia --query "[location,provisioningState]" --output tsv',
     '<code>southindia Succeeded</code> (the copy may take a few minutes; <code>completionPercent</code> shows progress).'),
    (['[[Disks]] → [[Create disk]] → <code>dr-disk</code>, asia-south1-a, 10 GB → [[Create]].', '[[Snapshots]] → [[Create snapshot]] → source dr-disk, location [[Regional]] → [[asia-south2 (Delhi)]] → [[Create]].'],
     'gcloud compute disks create dr-disk --size=10GB --zone=asia-south1-a\ngcloud compute snapshots create dr-snap --source-disk=dr-disk --source-disk-zone=asia-south1-a --storage-location=asia-south2\ngcloud compute snapshots describe dr-snap --format="value(status,storageLocations)"',
     '<code>READY [\'asia-south2\']</code> — the backup lives in Delhi, outside the Mumbai Region. You can restore it into any Region.')),
    'This is the first rung of the DR ladder (backup and restore). Next would be replicating the database and copying images — pilot light.')

prac = practical(OWN_INTRO + ' Two tiny VMs run for about 15 minutes; snapshots of 1–10 GB cost paise — delete everything at the end.', [SETUP_STEP, STEP1, STEP2, STEP3],
    cleanup='<b>AWS:</b> <code>aws autoscaling delete-auto-scaling-group --auto-scaling-group-name tiffingo-asg --force-delete; aws ec2 delete-launch-template --launch-template-name tiffingo-lt; aws ec2 delete-snapshot --snapshot-id $DR --region ap-south-2; aws ec2 delete-snapshot --snapshot-id $SNAP; aws ec2 delete-volume --volume-id $VOL</code>. Console: delete the group (instances terminate), template, volume and both snapshots (switch Region for the copy).<br>'
            '<b>Azure:</b> <code>az group delete --name rg-tiffingo --yes --no-wait</code> (the South India snapshot is in the same resource group).<br>'
            '<b>Google Cloud:</b> <code>gcloud compute instance-groups managed delete tiffingo-mig --region=asia-south1 --quiet; gcloud compute instance-templates delete tiffingo-tpl --quiet; gcloud compute snapshots delete dr-snap --quiet; gcloud compute disks delete dr-disk --zone=asia-south1-a --quiet</code>.')

mist = mistakes([
    ['Everything in one AZ.', 'Default subnet, quick start.', 'Spread stateless tiers across ≥2 AZs; Multi-AZ databases.'],
    ['Thinking multi-AZ = disaster recovery.', 'Both sound like “backup”.', 'Multi-AZ is HA in one Region; DR needs another Region/account and backups.'],
    ['No RTO/RPO agreed with the business.', 'Nobody asked.', 'Write RTO/RPO per system; pick the cheapest strategy that meets them.'],
    ['Backups never restored.', 'Restore tests feel optional.', 'Quarterly restore drills; measure real RTO.'],
    ['Each AZ sized for a third of peak.', 'Cost saving.', 'N+1 per AZ (static stability) for critical tiers.'],
    ['High DNS TTLs on failover records.', 'Defaults.', 'Low TTLs or anycast global load balancing.'],
    ['DR quotas and KMS keys missing in the other Region.', 'Only primary Region configured.', 'Mirror quotas, keys, parameters and images in DR; test.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Scalability, availability, fault tolerance and disaster recovery in cloud architecture.'], ['AWS CLF-C02', 'High availability with multiple AZs, Auto Scaling, ELB, DR strategies (backup & restore, pilot light, warm standby, multi-site), AWS Backup, Elastic Disaster Recovery.'], ['AZ-900', 'Availability zones, region pairs, VM scale sets, availability sets, Azure Site Recovery, Azure Backup.'], ['Google Cloud Digital Leader', 'Reliability on Google Cloud: zones/regions, regional MIGs, multi-region services, SRE concepts.']], minw=560) + \
    qx('1. Which DR strategy keeps only core data running in the recovery Region?', ['Backup & restore', 'Pilot light', 'Warm standby', 'Multi-site'], 1, 'Pilot light.') + \
    qx('2. Deploying across multiple Availability Zones primarily provides…', ['Disaster recovery from Region loss', 'High availability', 'Lower cost', 'Data compression'], 1, 'HA inside a Region.') + \
    qx('3. RPO describes…', ['how long you may be down', 'how much data you may lose', 'how fast pages load', 'how many users'], 1, 'Recovery point objective.') + \
    qx('4. Which Azure service replicates VMs to another Region for disaster recovery?', ['Azure Backup', 'Azure Site Recovery', 'Azure Advisor', 'Azure Arc'], 1, 'Site Recovery.') + \
    qx('5. A Google Cloud regional managed instance group…', ['runs in one zone', 'spreads instances across zones of a Region', 'is global', 'needs Kubernetes'], 1, 'Regional MIG.') + \
    qx('6. Which strategy has the lowest RTO and highest cost?', ['Backup & restore', 'Pilot light', 'Warm standby', 'Multi-site active/active'], 3, 'Both sites live.')

proj = miniproject('Mini project: a resilience plan for TiffinGo',
    'Decide how each system survives failures and disasters — and prove one piece.',
    ['<b>Targets:</b> RTO and RPO for order API, customer DB, analytics and the marketing site.',
     '<b>SPOF hunt:</b> mark every single point of failure on the architecture diagram.',
     '<b>HA design:</b> multi-AZ layout with N+1 sizing per AZ.',
     '<b>DR choice:</b> pick a strategy per system with a cost estimate (Lesson 5.5).',
     '<b>Prove it:</b> on your own account, run a group across zones, kill an instance, and copy a backup to another Region (steps 1–3); record times.',
     '<b>Drill plan:</b> a quarterly game-day checklist.'],
    'An RTO/RPO table, a DR choice per system and timings from your self-healing test.', 'This lesson + 5.3 (scaling) + 5.4 (SLAs) + 6.2 (storage).')

assemble_v2(HERE, story_h2='One data centre goes dark', hook_html=hk,
    narration='At 9:12 p.m. a cooling failure shut down one Mumbai data centre. TiffinGo’s customers noticed nothing; a competitor was down for three hours. The difference was designed months earlier.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Scalability, availability and fault tolerance',
    formal='<b>Scalability</b> is a system’s ability to handle increased load by adding resources; <b>availability</b> is the proportion of time it is operational; <b>high availability</b> designs minimise downtime through redundancy and automatic failover across failure domains; <b>fault tolerance</b> is the ability to continue operating without interruption when components fail; <b>disaster recovery</b> restores service after a large-scale event within a defined <b>recovery time objective (RTO)</b> and <b>recovery point objective (RPO)</b>.',
    simple='Scalability = handle more users. High availability = keep running when a part breaks. Fault tolerance = users notice nothing at all. Disaster recovery = come back after a big disaster.',
    interview=['“HA keeps a service up through component or zone failures — typically multi-AZ with load balancing, auto scaling and Multi-AZ databases. Fault tolerance means zero interruption. DR is about recovering from a Region-level or data-loss event within an RTO and RPO.”', '“DR strategies go from backup & restore (cheapest, hours) through pilot light and warm standby to multi-site active/active (near zero, most expensive).”'],
    terms_rows=[('Availability', 'Share of time usable.'), ('High availability', 'Survive failures with little downtime.'), ('Fault tolerance', 'No interruption.'), ('Disaster recovery', 'Recover after a disaster.'), ('RTO', 'Max downtime.'), ('RPO', 'Max data loss.'), ('SPOF', 'Single point of failure.'), ('N+1', 'One spare.'), ('Failover', 'Switch to standby.'), ('Blast radius', 'Who is affected.')],
    exam='CLF-C02 asks HA vs DR, the four DR strategies with RTO/RPO, and multi-AZ. AZ-900 asks zones, region pairs, scale sets and Site Recovery.',
    picture_h2='Four goals, and the DR ladder', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven resilience techniques, one by one', TYPES)],
    how_h2='What happens when one Availability Zone fails', how_intro='Self-healing, step by step.', how_anim=AZFAIL,
    parts_h2='Six words for every resilience discussion', parts_html=parts, lv='',
    myth_rows=[('Multi-AZ is disaster recovery.', 'It is high availability inside one Region.', 'Type 2.'), ('More replicas protect against bad deployments.', 'Replicas copy the bug; isolate and stage changes.', 'Type 7.'), ('The cloud provider handles DR for us.', 'Resilience in the cloud is your responsibility.', 'Deep dive.')],
    extra_secs=[('deep', 'Deep dive', 'Availability maths, choosing RTO/RPO, shared responsibility', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Explain scalability, HA, fault tolerance and DR and how they differ.', 'Design a multi-AZ architecture with N+1 sizing.', 'Choose a DR strategy from RTO and RPO.', 'Explain fault isolation and graceful degradation.', 'Build a multi-zone group, test self-healing and copy a backup to another Region on your own account.'],
    next_html='<a href="../03-multi-tier-architecture/">7.3 Multi-tier architecture</a>.',
    pre='<b>Before you start:</b> <a href="../../05-core-cloud-concepts/03-scalability-elasticity-and-cloud-bursting/">5.3 Scalability</a> and <a href="../../05-core-cloud-concepts/04-service-level-agreements/">5.4 SLAs</a>.')
