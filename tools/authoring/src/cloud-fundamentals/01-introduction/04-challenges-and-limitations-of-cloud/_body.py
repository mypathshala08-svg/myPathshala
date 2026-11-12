import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
C = 'l14_challenges.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('If the cloud is so good, why do companies still lose money, data and sleep over it?',
    'Because the cloud has real limits. Google Cloud’s public status feed, which keeps the most recent incidents, listed <b>8</b> on 10 Nov 2026; one about network traffic from <b>Delhi, Chennai and Mumbai</b> stayed open for <b>516 hours</b> (21 days). Add surprise bills, vendor lock-in, data-law rules, skills gaps and security mistakes. Knowing these is what separates a cloud user from a cloud engineer.',
    ['Nine challenges: downtime, security, cost, lock-in, compliance, latency, control, skills, migration.', 'Reading a real provider incident feed.', 'How each challenge is reduced in practice.'])
cmap = concept_map('Concept map. Beginner: what can go wrong. Intermediate: nine challenges and their fixes. Advanced: SLAs, multi-region, governance.',
    [[('adv', 'Advantages', 'Lesson 1.3', B + '01-introduction/03-characteristics-and-advantages-of-cloud/'), ('net', 'Internet dependency', '', None)],
     [('down', 'Downtime', 'incidents', None), ('sec', 'Security', 'misconfig', None), ('cost', 'Cost overrun', 'forgotten', None), ('lock', 'Lock-in', 'proprietary', None)],
     [('sla', 'SLAs', 'Lesson 5.4', B + '05-core-cloud-concepts/04-service-level-agreements/'), ('ha', 'Multi-AZ / region', 'Lesson 7.2', B + '07-cloud-architecture/02-scalability-availability-and-fault-tolerance/'), ('sr', 'Shared responsibility', 'Lesson 9.1', B + '09-cloud-security/01-shared-responsibility-model/'), ('mc', 'Multi-cloud', 'Lesson 3.3', B + '03-deployment-models/03-multi-cloud-vs-hybrid-cloud/')]],
    [('adv', 'down'), ('net', 'down'), ('down', 'sla'), ('down', 'ha'), ('sec', 'sr'), ('cost', 'sla'), ('lock', 'mc'), ('adv', 'cost')],
    {'down', 'sec', 'cost', 'lock', 'sla', 'ha'},
    '<b>Next:</b> <a href="../05-on-premises-vs-cloud-vs-dedicated-servers/">1.5 On-premises vs cloud vs dedicated</a>.')
whw = why_how_where(
    'Every cloud decision is a trade-off. Interviewers ask “what are the disadvantages?” to see if you think like an engineer, not a salesperson.',
    'Challenges come from sharing (security, noisy neighbours), distance (latency, internet dependency), the provider’s control (outages, lock-in) and the pay-per-use model (cost surprises).',
    'Architecture reviews, migration plans, risk registers, audits (banking, health, government), exam “limitations” questions.',
    'No cloud is 100% available; even multi-region designs reduce, not remove, risk.')
def risks(hl=-1):
    items = [('Downtime', 'red'), ('Security', 'red'), ('Cost', 'amber'), ('Lock-in', 'amber'), ('Compliance', 'violet'), ('Latency', 'blue'), ('Control', 'blue'), ('Skills', 'green'), ('Migration', 'green')]
    o = box(130, 54, 100, 40, 'acc', rx=20) + t(180, 78, 'Your cloud app', 8.6, 'ink', bold=True)
    import math
    for i, (lab, tn) in enumerate(items):
        a = -math.pi / 2 + i * 2 * math.pi / 9; x = 180 + 150 * math.cos(a); y = 74 + 58 * math.sin(a)
        o += f'<line x1="180" y1="74" x2="{x:.0f}" y2="{y:.0f}" stroke="currentColor" class="s-ink2" opacity=".35"/>'
        o += box(x - 32, y - 10, 64, 20, 'amber' if i == hl else tn, rx=10) + t(x, y + 3.5, lab, 7.4, 'ink', bold=True)
    return o
scene_svg = scene('Nine risks around a cloud application: downtime, security, cost, lock-in, compliance, latency, control, skills, migration.', risks(0),
                  'Nine challenges to plan for — <tspan font-weight="700" class="s-acc">none is a reason to avoid cloud, all need a plan</tspan>.')
dialogue = '''K> Sir, the TiffinGo app was slow for users in Pune last June, but our servers were fine!
A> The problem may not be ours. Providers publish incidents. Let’s read Google Cloud’s feed — one incident was about traffic from Delhi, Chennai and Mumbai.
R> So the cloud also fails?
A> Everything fails sometimes. Today: the nine challenges of cloud and what engineers do about each.'''
lv = '''
LEVELS> Cloud challenges at three levels
L1> Renting a flat, not owning it
      <ul>
        <li>The landlord fixes the building (provider), but if the water supply stops (outage) you wait; you can’t knock down walls (control); moving out is effort (lock-in); and the bill depends on how much you use (cost).</li>
      </ul>
L2> The nine challenges
      <ul>
        <li><b>Downtime</b> and internet dependency · <b>security & privacy</b> (mostly misconfiguration) · <b>cost overruns</b> · <b>vendor lock-in</b> · <b>compliance / data residency</b> (e.g. India’s DPDP Act 2023, RBI rules) · <b>latency</b> · <b>limited control</b> over hardware · <b>skills gap</b> · <b>migration complexity</b>.</li>
      </ul>
L3> How architects reduce them
      <ul>
        <li>Multi-AZ and multi-region designs, backups and DR (RTO/RPO); least-privilege IAM and encryption; budgets, tags and FinOps; open standards (containers, Terraform, SQL) to limit lock-in; Indian regions for residency; CDNs for latency; training and certification for skills.</li>
      </ul>
/LEVELS
'''
mm = mindmap('Mind map of cloud challenges and their fixes.', 'Cloud challenges', [
    ('Availability', 'red', ['outages', 'internet down', '→ multi-AZ, DR']),
    ('Security', 'violet', ['misconfiguration', 'leaked keys', '→ IAM, MFA']),
    ('Money', 'amber', ['surprise bills', 'data transfer', '→ budgets, tags']),
    ('Lock-in', 'blue', ['proprietary APIs', 'egress fees', '→ open standards']),
    ('Law', 'green', ['data residency', 'DPDP, RBI', '→ Indian regions']),
    ('People', 'card', ['skills gap', 'migration effort', '→ training, certs'])], h=290)
lay = layers('Where each challenge sits: your users and internet at the top, your configuration in the middle, the provider’s infrastructure at the bottom.', [
    ('Users + internet', 'latency, ISP outages', 'blue'), ('Your account settings', 'security misconfig, IAM', 'red'),
    ('Your architecture', 'single AZ = single point of failure', 'amber'), ('Your bill', 'forgotten resources, egress', 'amber'),
    ('Provider services', 'regional incidents, API changes', 'violet'), ('Provider data centres', 'power, network, hardware', 'card')], hl=1, caption='Most incidents customers suffer start in the middle layers — theirs.')
DIS = figure('Dissection of a real Google Cloud incident: began 5 June 2026, network traffic from Delhi, Chennai, Mumbai, severity medium, open 516 hours.',
    t(16, 22, 'One real incident record', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('2026-06-05', 'blue', 1), ('Delhi, Chennai, Mumbai', 'green', 2), ('medium', 'amber', 3), ('516 h', 'violet', 4)]) +
    legend(16, 84, [(1, 'Begin', 'when it started'), (2, 'Scope', 'traffic from Indian cities'), (3, 'Severity', 'provider’s rating'), (4, 'Duration', 'begin → end in the feed')], size=8, gap=15, w=90),
    h=156, caption='Long “open” time = tracking period, not 21 days of total outage.')
extra = '\n\n  <h3>Where challenges live</h3>\n' + lay + '\n\n  <h3>Dissect a real incident</h3>\n' + DIS
types_html = table(['Challenge', 'What goes wrong', 'Typical fix'], [
    ['Downtime', 'provider or internet outage', 'multi-AZ/region, health checks, DR plan'],
    ['Security & privacy', 'public bucket, leaked key, weak IAM', 'MFA, least privilege, encryption, audits'],
    ['Cost overrun', 'idle VMs, NAT gateways, data transfer out', 'budgets, alerts, tags, rightsizing'],
    ['Vendor lock-in', 'proprietary services, egress fees', 'containers, Terraform, open formats, exit plan'],
    ['Compliance', 'data must stay in India, audits', 'Indian regions, certifications, logs'],
    ['Latency', 'users far from region', 'nearest region, CDN, edge'],
    ['Limited control', 'no hardware access, provider changes', 'SLAs, support plans, managed services'],
    ['Skills gap', 'team new to cloud', 'training, certification, guardrails'],
    ['Migration', 'old apps hard to move', '6 Rs strategy (rehost, replatform, refactor…)']], minw=620)
warn = 'Most cloud data breaches are customer misconfigurations (open storage buckets, leaked access keys), not the provider being hacked. Read Lesson 9.1 shared responsibility before you build anything public.'
steps = [
    ('Step 1 · Providers publish incidents', code('python', 'l14_challenges.py', 'inc = json.load(urlopen("https://status.cloud.google.com/incidents.json"))', sec('== 1)', '== 2)')), 'The public feed keeps recent incidents; history beyond that is in past reports.'),
    ('Step 2 · Severity', code('python', 'l14_challenges.py', 'Counter(i["severity"] for i in last_12_months)', sec('== 2)', '== 3)')), 'Mostly medium; one high.'),
    ('Step 3 · How long they stay open', code('python', 'l14_challenges.py', 'end - begin in hours; median, 90th percentile, longest', sec('== 3)', '== 4)')), 'Half end within ~11 hours; one tracking record stayed open 21 days.'),
    ('Step 4 · Did India get hit?', code('python', 'l14_challenges.py', 'affected locations contain asia-south1 / asia-south2', sec('== 4)', '== 5)')), 'One: traffic from Indian cities in June 2026. Internet paths are part of “the cloud”.'),
    ('Step 5 · Which products', code('python', 'l14_challenges.py', 'Counter(product titles)', sec('== 5)')), 'Databases, storage, serverless and analytics: no service is immune.'),
]
see = [term([('8 incidents', W), ('last 12 months', W)], size=7.0), term([('medium 6 high 1', W), ('low 1', W)], size=7.0), term([('median 10.7 h', G), ('longest 516 h', RD)], size=7.0),
       term([('India: 1', RD), ('2026-06-05', W)], size=7.0), term([('Cloud Run 3', W), ('BigQuery 3', W)], size=7.0)]
B1 = [risks(i) for i in (0, 0, 0, 5, 1)]
B1 = [b + cap(c, '', tn, y=146, h=20) for b, c, tn in zip(B1, ['Outages happen', 'Severity', 'Duration', 'Latency from India', 'Every product'], ['red', 'amber', 'amber', 'blue', 'violet'])]
two = anim_two('Cloud challenges', 'Reading a real incident feed', 'Real outputs (Google Cloud status)', 'Nine risks', see, B1, ['Feed.', 'Severity.', 'Hours.', 'India.', 'Products.'], ['Down.', 'Rate.', 'Long.', 'Network.', 'Any.'])
pe = peel('A regional outage, layer by layer', 'What happens and what saves you. (Simplified.)',
    [('Fault', ''), ('Detect', ''), ('Impact', ''), ('Failover', ''), ('Recover', ''), ('Review', '')],
    [['Fault', 'zone network', 'problem', ''], ['Detect', 'health checks fail', 'alarms fire', ''], ['Impact', 'single-AZ app', 'goes down', 'bad design'],
     ['Failover', 'multi-AZ app', 'shifts traffic', 'good design'], ['Recover', 'provider fixes', 'incident closed', ''], ['Review', 'post-incident', 'report', 'learn']],
    ['Break.', 'Notice.', 'Hurt.', 'Survive.', 'Fix.', 'Learn.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Public bucket leak', 'Customer data exposed. (Typical.)', ('Misconfiguration', 'Block public access'), [
    ('Bucket made public', 'for a quick test', 'Mistake.', 'red'), ('Search bots find it', 'hours later', 'Leak.', 'red'),
    ('Block Public Access on', 'account level', 'Fix.', 'green'), ('Encrypt + log', '', 'Harden.', 'green'), ('Audit with config rules', '', 'Prevent.', 'amber')], ['Public.', 'Found.', 'Block.', 'Encrypt.', 'Audit.'], 'scenario-leak') + \
       five('Real-time scenario 2', 'The ₹2 lakh bill', 'Student lab left on. (Typical.)', ('Cost control', 'Budgets + cleanup'), [
    ('GPU VM for a demo', '', 'Start.', 'blue'), ('Forgot to stop', '30 days', 'Mistake.', 'red'),
    ('Bill arrives', 'shock', 'Pain.', 'red'), ('Budget alert at $1', 'next time', 'Fix.', 'green'), ('Cleanup checklist', 'every lab', 'Habit.', 'amber')], ['Start.', 'Forget.', 'Bill.', 'Alert.', 'Habit.'], 'scenario-bill') + \
       five('Real-time scenario 3 · advanced', 'Lock-in', 'Moving clouds is hard. (Typical.)', ('Portability', 'Open standards'), [
    ('Built on proprietary DB', '', 'Then.', 'blue'), ('Price rises / new rules', '', 'Change.', 'amber'),
    ('Export costs + rewrite', 'egress fees', 'Pain.', 'red'), ('Containers + Terraform', 'portable layers', 'Design.', 'green'), ('Exit plan documented', '', 'Ready.', 'green')], ['Proprietary.', 'Change.', 'Cost.', 'Portable.', 'Plan.'], 'scenario-lockin')
clouds = vendor_tabs(
    '<p><b>AWS:</b> AWS Health Dashboard (public + personal), Trusted Advisor (cost, security, limits), AWS Budgets, Well-Architected reliability pillar, Region/AZ design.</p>',
    '<p><b>Azure:</b> Azure Status + Service Health, Azure Advisor, Cost Management budgets, availability zones and region pairs.</p>',
    '<p><b>Google Cloud:</b> status.cloud.google.com (public incidents JSON used here), Personalized Service Health, Recommender, budgets and alerts.</p>') + \
    cloud3([['Public status page', 'health.aws.amazon.com', 'azure.status.microsoft', 'status.cloud.google.com'], ['Your own incidents', 'AWS Health (personal)', 'Service Health', 'Personalized Service Health'], ['Advice engine', 'Trusted Advisor', 'Azure Advisor', 'Recommender / Active Assist'], ['Budget alerts', 'AWS Budgets', 'Cost Management budgets', 'Cloud Billing budgets']])
prac = practical('Check the health of three clouds and read incidents yourself. No account needed.', [
    ('1 · Google incidents as JSON', code('bash', 'terminal', "curl -s https://status.cloud.google.com/incidents.json | jq '.[] | {begin, severity, d: .external_desc[0:60]}' | head -40"), 'Each object is one incident.'),
    ('2 · Filter India', code('bash', 'terminal', "curl -s https://status.cloud.google.com/incidents.json | jq -r '.[] | select(tostring | test(\"asia-south\")) | .begin + \" \" + .external_desc[0:70]'"), 'Matches Step 4.'),
    ('3 · AWS and Azure status pages', '<p>Open <code>health.aws.amazon.com/health/status</code> and <code>azure.status.microsoft</code>; filter Asia Pacific (Mumbai) / Central India.</p>', 'Note the format each uses.'),
    ('4 · Run the lesson script', code('bash', 'terminal', 'python3 l14_challenges.py'), 'Same output style as Steps 1–5.'),
    ('5 · Write a 5-line risk register', '<p>For TiffinGo: risk, likelihood, impact, fix, owner. Use the types table.</p>', 'This is real work in every migration project.')],
    cleanup='Nothing created. Keep your risk register; you will reuse it in the capstone (Module 11).')
mist = mistakes([
    ['Running production in one availability zone.', 'Simplest setup, cheapest.', 'Use at least 2 AZs behind a load balancer (Lesson 7.2).'],
    ['Making storage public “for testing”.', 'Quick sharing; forgotten later.', 'Use pre-signed links; keep Block Public Access on.'],
    ['Assuming the provider backs up your data.', 'Shared responsibility misunderstood.', 'Configure backups/versioning yourself; test restores.'],
    ['No budget alert on a new account.', 'Sign-up does not force one.', 'Create a zero-spend + monthly budget on day one.'],
    ['Picking a US region for Indian personal data.', 'Default region in tutorials.', 'Check data-residency rules; use Indian regions.']])
cert = certbox([
    ['AWS CLF-C02', 'Domain 1 · Cloud Concepts', 'Design principles: design for failure, multi-AZ; migration strategies (the 6/7 Rs); Cloud Adoption Framework basics.'],
    ['AWS CLF-C02', 'Domain 2 · Security & Compliance', 'Misconfiguration risk, shared responsibility, AWS Artifact for compliance reports.'],
    ['Azure AZ-900', 'Describe cloud concepts / management', 'Reliability, availability, Service Health, Advisor.'],
    ['Google Cloud Digital Leader', 'Trust and security; Scaling with operations', 'Reliability, incident response, shared fate.'],
    ['C-DAC PGCP-BDA', 'Sessions 3–4', 'Challenges of the cloud environment.']],
    [('Which is the MOST common cause of cloud data exposure? (a) provider hardware theft (b) customer misconfiguration (c) solar flares', '<b>(b)</b> Customer misconfiguration (e.g. public buckets).'),
     ('A company fears it cannot leave a provider easily. This risk is…', '<b>Vendor lock-in.</b> Reduce with open standards and an exit plan.'),
     ('Running in multiple Availability Zones mainly protects against…', 'A single data-centre (zone) failure: higher availability.')])
proj = miniproject('Mini project: cloud status watcher',
    'A script that checks the Google Cloud incident feed every hour and prints a line when an incident mentions an Indian region.',
    ['Copy the Step 4 filter into <code>watch.py</code>; remember seen incident ids in a file.', 'Print new matches with time and description.', 'Schedule with <code>cron</code>: <code>0 * * * * python3 /home/you/watch.py &gt;&gt; watch.log</code>.', 'Bonus: send yourself an email/Telegram message (later: AWS SNS, Lesson 7.2 of the AWS course).'],
    'A <code>watch.log</code> that grows only when Indian regions are affected.', 'Python + JSON, Linux cron, later AWS SNS.')

# ===== v3 =====
def where():
    o = t(320, 16, 'Where each cloud challenge lives', 11, 'ink', bold=True)
    # columns: users, internet, your account, provider region
    o += box(14, 36, 110, 210, 'blue', rx=10) + t(69, 54, 'Users', 9, 'blue', bold=True) + ic('phone', 44, 70, 1.1, 'blue') + ic('laptop', 74, 70, 1.1, 'blue')
    o += box(138, 36, 104, 210, 'card', rx=10) + t(190, 54, 'Internet', 9, 'ink', bold=True) + ic('globe', 178, 70, 1.1, 'acc')
    o += box(256, 36, 170, 210, 'violet', rx=10) + t(341, 54, 'Your cloud account', 9, 'violet', bold=True) + ic('user', 330, 66, 1.1, 'violet')
    o += box(440, 36, 186, 210, 'green', rx=10) + t(533, 54, 'Provider region (Mumbai)', 9, 'green', bold=True) + ic('server', 522, 66, 1.1, 'green')
    for x1, x2 in [(124, 138), (242, 256), (426, 440)]:
        o += arrow(x1, 140, x2, 140, 'acc', 2)
    badges = [(26, 104, 'Latency', 'far region = slow', 'blue'), (26, 160, 'Skills gap', 'team is new to cloud', 'blue'),
              (148, 104, 'Internet down', 'no access at all', 'red'), (148, 160, 'Data transfer', 'egress fees', 'amber'),
              (266, 104, 'Misconfiguration', 'public bucket, weak IAM', 'red'), (266, 152, 'Cost overrun', 'forgotten resources', 'amber'), (266, 200, 'Lock-in', 'proprietary services', 'amber'),
              (452, 104, 'Outage', 'zone / region incident', 'red'), (452, 152, 'Less control', 'provider decides hardware', 'violet'), (452, 200, 'Compliance', 'data must stay in India', 'violet')]
    for x, y, a, b, tn in badges:
        w = 92 if x < 250 else (150 if x < 440 else 162)
        o += box(x, y, w, 38, tn, rx=6) + t(x + 8, y + 16, a, 8.2, 'ink', anchor='start', bold=True) + t(x + 8, y + 29, b, 7, 'ink2', anchor='start')
    return o + t(320, 262, 'Red = can stop your service · amber = can cost you money · violet = limits your choices', 8, 'ink2')
WHERE = bigfig('Map of cloud challenges by location: users (latency, skills gap), internet (internet down, data transfer fees), your cloud account (misconfiguration, cost overrun, lock-in), provider region (outage, less control, compliance).', where(), h=274,
               caption='')
picture = ('  <p>The cloud solves many problems (Lesson 1.3) but creates new ones. A good engineer knows <b>where</b> each problem can appear. Follow a request from the user to the provider: every box has its own risks.</p>\n' + WHERE +
           '\n  <p>Notice that most red boxes sit in <b>your account</b>, not at the provider. That is why “the cloud is insecure” is usually wrong: misconfiguration by customers causes most incidents.</p>')

# animation 1: a public-bucket leak and its fix
LN = {'dev': (8, 20, 64, 50, 'user', 'Developer', 'quick test'), 'bucket': (100, 20, 72, 50, 'disk', 'Storage bucket', 'customers.csv'),
      'bot': (100, 98, 72, 50, 'globe', 'Scanner bot', 'internet'), 'alert': (204, 20, 64, 50, 'shield', 'Security alert', 'Macie / Config'),
      'block': (204, 98, 64, 50, 'shield', 'Block Public', 'Access ON'), 'log': (290, 58, 64, 50, 'dns', 'Audit log', 'who did what')}
LS = [dict(on=['dev', 'bucket'], hot='dev', move=(72, 45, 100, 45, 'public'), head='Step 1 · A “quick test” makes a bucket public', text='The developer sets the bucket to public to share one file with a colleague.', text2='Customer data is also in that bucket.', svc='AWS S3 · Azure Blob container · Google Cloud Storage bucket'),
      dict(on=['dev', 'bucket', 'bot'], hot='bot', move=(136, 98, 136, 70, 'scan'), head='Step 2 · Bots find it within hours', text='Automated scanners search the internet for open buckets all day.', text2='They list the files and download customers.csv.', svc='This is the most common cause of cloud data leaks'),
      dict(on=['dev', 'bucket', 'bot', 'alert'], hot='alert', move=(172, 45, 204, 45, 'alarm'), head='Step 3 · A security service raises an alert', text='A managed checker sees “public bucket with personal data” and alerts.', text2='Without it, the company may learn from the news.', svc='AWS Macie, Config, Security Hub · Microsoft Defender for Cloud · Security Command Center'),
      dict(on=['dev', 'bucket', 'bot', 'alert', 'block'], hot='block', move=(236, 70, 236, 98, 'fix'), head='Step 4 · Turn on Block Public Access', text='One account-level switch blocks every public bucket, now and in future.', text2='Share files with time-limited pre-signed links instead.', svc='AWS S3 Block Public Access · Azure “allow blob public access = off” · GCP public access prevention'),
      dict(on=list(LN), hot='log', move=(268, 123, 292, 83, 'trail'), head='Step 5 · Find out who and when', text='The audit log shows which user changed the setting and when.', text2='Lesson learned: least privilege + guardrails + logs (Module 9).', svc='AWS CloudTrail · Azure Activity Log · Google Cloud Audit Logs')]
LEAK = flow_anim('A public bucket leak, step by step', 'The number-one cloud mistake, how it is discovered and how it is fixed.', 'Misconfiguration', 'Animation: developer makes bucket public, scanner bot finds it, alert fires, block public access, audit log.', LN, LS, hid='leak')

# animation 2: single-AZ vs multi-AZ during an outage
def az_frame(k):
    o = t(180, 12, ['Normal day: app in two zones', 'Zone A fails (power / network)', 'Single-zone app: DOWN', 'Multi-zone app: still UP'][k], 9, 'ink', bold=True)
    failed = k >= 1
    o += box(70, 20, 130, 128, 'red' if failed else 'card', rx=8) + t(135, 34, 'Zone A (Mumbai)', 7.6, 'ink', bold=True)
    o += box(214, 20, 130, 128, 'card', rx=8) + t(279, 34, 'Zone B (Mumbai)', 7.6, 'ink', bold=True)
    o += node_box(4, 62, 56, 50, 'lb', 'Load', 'balancer', hot=(k == 3))
    if k < 3:
        o += node_box(100, 50, 70, 50, 'server', 'App VM', 'zone A', on=not failed, hot=(k == 0))
        o += node_box(100 + 0, 104 - 0 + 0, 70, 0, 'server', '', '') if False else ''
    if k in (0, 3):
        o += node_box(244, 50, 70, 50, 'server', 'App VM', 'zone B', hot=(k == 3))
        o += packet(60, 87, 244, 75, 'traffic') if k == 3 else packet(60, 87, 100, 75, '')
    if k == 3:
        o += node_box(100, 50, 70, 50, 'server', 'App VM', 'zone A', on=False)
    if k == 2:
        o += t(135, 120, '✘ site down', 10, 'red', bold=True)
    if failed:
        o += t(135, 140, '⚡ zone failure', 8, 'red', bold=True)
    return o
AZ = [('Normal', 'The load balancer sends users to the app in zone A (and B, if you built it).', 'Availability Zone = one or more separate data centres in a region'),
      ('Fault', 'A power or network problem hits zone A. It happens a few times a year somewhere.', 'Providers publish these as incidents (see Real proof)'),
      ('Single-zone design', 'All servers were in zone A, so the whole app is down until AWS fixes it.', 'Cheapest design, but one zone = one point of failure'),
      ('Multi-zone design', 'Health checks fail in A; the load balancer sends everyone to zone B.', 'Users barely notice. This is how outages are survived.')]
fr = [az_frame(k) + box(6, 158, 348, 62, 'blue', rx=8) + t(14, 174, h, 9, 'ink', anchor='start', bold=True) + t(14, 190, a, 7.6, 'ink', anchor='start') + t(14, 206, b, 7.2, 'ink2', anchor='start') for k, (h, a, b) in enumerate(AZ)]
AZA = anim_one('How it works', 'Surviving a zone outage', 'Outages will happen. The design decides whether users notice.', 'Single zone vs multi zone', 'Animation: app in zone A and B, zone A fails, single-zone app goes down, multi-zone app keeps running via zone B.', fr, ['Normal.', 'Fault.', 'Single zone.', 'Multi zone.'], delay=6000, hid='az')

parts = cards([
    ('1. Downtime and internet dependency', 'Provider incidents and internet outages make apps unreachable.', 'fix: multi-AZ, multi-region, DR'),
    ('2. Security and privacy', 'Mostly customer misconfiguration: public buckets, leaked keys, weak passwords.', 'fix: MFA, least privilege, encryption'),
    ('3. Cost overrun', 'Forgotten VMs, NAT gateways, idle IPs and data transfer out.', 'fix: budgets, tags, cleanup'),
    ('4. Vendor lock-in', 'Proprietary services and egress fees make moving hard.', 'fix: containers, Terraform, exit plan'),
    ('5. Compliance and data residency', 'Laws like India’s DPDP Act and RBI rules decide where data may live.', 'fix: Indian regions, audits'),
    ('6. Latency', 'Users far from the region feel delay.', 'fix: nearest region, CDN'),
    ('7. Limited control', 'You cannot choose hardware or patch times of managed services.', 'fix: SLAs, support plans'),
    ('8. Skills gap', 'Teams new to cloud make costly mistakes.', 'fix: training, certification, guardrails'),
    ('9. Migration complexity', 'Old apps were not built for the cloud.', 'fix: 7 Rs strategy'),
    ('10. Noisy neighbours', 'On shared hardware another customer’s heavy VM can slow yours a little.', 'fix: right instance type, dedicated options'),
    ('11. Interoperability and portability', 'Data formats and APIs differ between clouds, so moving or mixing them is work.', 'fix: open formats (Parquet, SQL), containers'),
    ('12. Multi-tenancy isolation', 'Many customers share hardware; a flaw in isolation would be serious, so providers harden hypervisors.', 'fix: provider certifications, encryption'),
    ('13. Understanding SLAs', 'An SLA promises e.g. 99.99% and pays service credits, not your lost sales.', 'fix: design for failure anyway (Lesson 5.4)')]) + '\n  <h3>Challenges and fixes at a glance</h3>\n' + types_html

SUMMARY = big_mindmap('Mind map of lesson 1.4: where challenges live, top risks, fixes, design for failure, laws, people.', 'Cloud challenges', [
    ('Stop service', 'red', 'shield', ['outage', 'internet down', 'misconfiguration']),
    ('Cost money', 'amber', 'meter', ['forgotten resources', 'data transfer out', 'lock-in exit cost']),
    ('Limit choice', 'violet', 'gear', ['less control', 'data residency', 'provider changes']),
    ('Fixes', 'green', 'chart', ['multi-AZ + DR', 'MFA, least privilege', 'budgets + tags']),
    ('Leak lesson', 'blue', 'disk', ['public bucket', 'Block Public Access', 'audit logs']),
    ('People', 'acc', 'user', ['skills gap', 'training + certs', '7 Rs migration'])], h=380, caption='Lesson 1.4 on one page.')
cert = cert + '\n  <h3>Lesson 1.4 on one page</h3>\n' + SUMMARY

assemble_v2(HERE, story_h2='Slow in Pune, but our servers were fine', hook_html=hk,
    narration='In June, TiffinGo users in western India complained of slow loading. The team’s servers looked healthy. Was it them, the internet, or the cloud? And could something worse happen?',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Challenges and limitations of cloud computing',
    formal='The <b>challenges of cloud computing</b> are the risks and constraints of consuming shared, remote, provider-operated infrastructure: availability and network dependency, security and privacy, cost management, vendor lock-in, regulatory compliance and data residency, latency, reduced control, skills shortage and migration complexity.',
    simple='The cloud can still go down, can be set up wrongly, can cost more than expected, can be hard to leave and must follow data laws — so engineers plan for each.',
    interview=['“Cloud has trade-offs: downtime and internet dependency, security and privacy risks mostly from customer misconfiguration, cost overruns, vendor lock-in, compliance and data residency, latency, limited control and a skills gap.”', '“We reduce them with multi-AZ or multi-region design, least-privilege IAM, MFA and encryption, budgets and tagging, open standards like containers and Terraform, and Indian regions for regulated data.”', '“For example, a public storage bucket is the classic leak; Block Public Access and audit logs prevent and trace it.”'],
    terms_rows=[('Outage / incident', 'Service unavailable, reported by the provider.'), ('Availability Zone', 'Separate data centre(s) inside a region.'), ('Misconfiguration', 'Wrong settings by the customer.'), ('Vendor lock-in', 'Hard to move providers.'), ('Egress fee', 'Charge for data leaving the cloud.'), ('Data residency', 'Where data must physically stay.'), ('Latency', 'Network delay.'), ('DR', 'Disaster recovery plan.')],
    exam='AWS frameworks to know by name: the <b>Well-Architected Framework</b> (6 pillars incl. reliability, security, cost optimisation) for designing safely, and the <b>Cloud Adoption Framework (CAF)</b> for planning a migration. Typical questions: “Which is a disadvantage of cloud?” (internet dependency, lock-in, less control); “How to improve availability?” (multiple AZs/regions); “Who causes most breaches?” (customer misconfiguration). AWS migration: the 7 Rs (retire, retain, rehost, relocate, repurchase, replatform, refactor).',
    picture_h2='A map of where things go wrong', picture_html=picture,
    how_h2='A data leak and a zone outage, step by step', how_intro='Two real-world failure stories, animated: how a leak happens and is fixed, and how good design survives an outage.', how_anim=LEAK + AZA,
    parts_h2='Nine challenges and their fixes', parts_html=parts, lv='',
    myth_rows=[('Big clouds never fail.', '8 incidents in one provider feed in a year.', 'Real proof step 1.'), ('The provider causes most breaches.', 'Customer misconfiguration does.', 'Animation 1.'), ('Outages always take you down.', 'Multi-AZ designs keep running.', 'Animation 2.')],
    clouds_html=clouds, proof_h2='Reading a real incident feed', proof_intro='All outputs are real: Google Cloud’s public incidents.json, downloaded 10 Nov 2026.', proof_steps=steps,
    practical_html=prac, mistakes_html=mist, cert_html='', project_html='', can_now=['Point out where each challenge lives: users, internet, your account, provider.', 'Explain how a public-bucket leak happens and the three fixes.', 'Explain why a multi-AZ design survives a zone outage.', 'List the challenges with one fix each, including noisy neighbours and lock-in.', 'Name the 7 Rs of migration and the Well-Architected Framework.'],
    next_html='<a href="../05-on-premises-vs-cloud-vs-dedicated-servers/">1.5 On-premises vs cloud vs dedicated servers: which to choose and what it really costs</a>.',
    pre='<b>Before you start:</b> <a href="../03-characteristics-and-advantages-of-cloud/">1.3</a>.')
