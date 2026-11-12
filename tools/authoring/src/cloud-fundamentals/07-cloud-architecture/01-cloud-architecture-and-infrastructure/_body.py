import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)


hk = hook('Two teams build the same TiffinGo app on the same cloud. One survives Diwali, a data-centre power cut and a security audit at half the cost; the other does not. Same services — what was different?',
    'The <b>architecture</b>. Cloud architecture is how you arrange the provider’s <b>infrastructure</b> (Regions, AZs, networks, servers, the control plane) and services into a system — and every major cloud judges “good” architecture with the same yardstick: the <b>Well-Architected pillars</b> — operational excellence, security, reliability, performance, cost and sustainability. This lesson explains the classic cloud architecture layers, what is physically and logically inside a cloud, the difference between the <b>control plane</b> and the <b>data plane</b>, and each pillar — then you run a real architecture review on <b>your own</b> account.',
    ['The front-end / back-end architecture every textbook (and the C-DAC syllabus) draws.', 'Control plane vs data plane — why your app can keep running when the cloud console is down.', 'Six pillars that AWS, Azure and Google all use to judge designs.'])

def story_scene():
    o = t(180, 12, 'Same services, two outcomes', 9, 'ink', bold=True)
    for i, (n, s, tn) in enumerate([('Team A', 'one AZ · admin keys · no alarms', 'red'), ('Team B', '2 AZs · roles · alarms · budgets', 'green')]):
        x = 14 + i * 172
        o += box(x, 26, 160, 80, tn, rx=8) + t(x + 80, 48, n, 8.6, 'ink', bold=True) + t(x + 80, 68, s, 6.8, 'ink') + t(x + 80, 90, ['down 3 h · ₹2.1 L bill' , 'up · ₹1.0 L bill'][i], 7.2, 'ink', bold=True)
    o += t(180, 124, 'The difference is design choices, judged by six pillars.', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Two boxes: Team A with one AZ, admin keys and no alarms — down three hours and a big bill; Team B with two AZs, roles, alarms and budgets — up and half the cost.', story_scene(), 'Architecture = <tspan font-weight="700" class="s-acc">choices</tspan>, not services.', h=140)
dialogue = '''R> Sir, the investor asked for our “cloud architecture”. I sent the list of services we use.
A> A list of ingredients is not a recipe. Architecture is how they are arranged — and why.
K> How do we know if our arrangement is good?
A> AWS, Azure and Google each publish a Well-Architected Framework with the same pillars: run it well, keep it secure, keep it up, keep it fast, keep it affordable, waste less energy.
R> And the “infrastructure” part?
A> That is what the provider gives us — Regions, zones, networks, hardware and the control plane that creates things. Let’s look at both layers and then review our own design.'''

# ------------------------------------------------------------------ picture
def classicfig():
    o = t(320, 16, 'Cloud computing architecture: front end, network, back end', 11, 'ink', bold=True)
    o += box(14, 34, 150, 196, 'green', rx=10) + t(89, 52, 'FRONT END (client)', 8.4, 'ink', bold=True)
    for i, n in enumerate(['browser / mobile app', 'client software, SDK, CLI', 'thin client / kiosk']): o += box(26, 66 + i * 50, 126, 38, 'card', rx=6) + t(89, 89 + i * 50, n, 7.2, 'ink')
    o += box(178, 108, 70, 50, 'blue', rx=8) + t(213, 130, 'Internet /', 7.4, 'ink', bold=True) + t(213, 144, 'network', 7.4, 'ink', bold=True)
    o += arrow(166, 133, 176, 133) + arrow(250, 133, 262, 133)
    o += box(264, 34, 362, 196, 'card', rx=10) + t(445, 52, 'BACK END (cloud provider)', 8.4, 'ink', bold=True)
    rows = [('Application / service', 'SaaS apps, PaaS runtimes, APIs', 'violet'), ('Runtime and middleware', 'containers, functions, databases', 'blue'), ('Infrastructure', 'virtual compute, storage, network', 'green'), ('Physical resources', 'servers, disks, switches, data centres', 'amber')]
    for i, (n, d, tn) in enumerate(rows): o += box(276, 62 + i * 40, 240, 34, tn, rx=5) + t(396, 76 + i * 40, n, 7.6, 'ink', bold=True) + t(396, 89 + i * 40, d, 6.6, 'ink2')
    for j, (n, tn) in enumerate([('Management', 'amber'), ('Security', 'red')]): o += box(526 + j * 50, 62, 44, 154, tn, rx=5) + f'<text x="{548 + j * 50}" y="139" class="s-ink" font-size="8" font-weight="700" text-anchor="middle" transform="rotate(-90 {548 + j * 50} 139)">{n}</text>'
    o += t(320, 248, 'Management (provisioning, monitoring, billing) and security (identity, encryption, isolation) cut across every back-end layer.', 7.2, 'ink2')
    return o
CLASSIC = bigfig('Classic cloud architecture: front end with browsers, client software and thin clients; the internet; back end with application, runtime, infrastructure and physical layers, crossed by management and security.', classicfig(), h=258)

def physfig():
    o = t(320, 16, 'What is physically inside a cloud (AWS names; Azure and Google are similar)', 10.5, 'ink', bold=True)
    lv = [('Global backbone', 'private fibre between all Regions and 750+ edge sites', 'violet', 20, 600), ('Region (e.g. Mumbai)', 'independent area, ≥3 AZs, own control plane', 'blue', 50, 540), ('Availability Zone', 'one or more data centres, own power/cooling, ~km apart', 'green', 80, 480), ('Data centre', 'thousands of racks, power, cooling, physical security', 'amber', 110, 420), ('Rack → server (Nitro)', 'hosts with hypervisor + Nitro cards; storage and network fabric', 'red', 140, 360)]
    for i, (n, d, tn, x, w) in enumerate(lv):
        y = 32 + i * 40
        o += box(x, y, w, 34, tn, rx=6) + t(x + 12, y + 15, n, 8, 'ink', anchor='start', bold=True) + t(x + 12, y + 28, d, 6.8, 'ink', anchor='start')
    o += t(320, 242, 'You never touch these layers — you rent them through APIs. But your design decides how you use them (Lesson 5.1).', 7.4, 'ink2')
    return o
PHYS = bigfig('Nested bands: global backbone; Region; availability zone; data centre; rack and server with Nitro hypervisor.', physfig(), h=252)

picture = ('  <p>The architecture diagram every textbook and exam uses — a <b>front end</b> the user touches and a <b>back end</b> the provider runs, joined by the network:</p>\n' + CLASSIC +
           '\n  <p>And the physical <b>infrastructure</b> underneath that back end:</p>\n' + PHYS)

# ------------------------------------------------------------------ how: control plane vs data plane
RN = {'u': (4, 54, 54, 50, 'user', 'Engineer', 'console/CLI'), 'api': (66, 4, 60, 46, 'cloud', 'API endpoint', 'ec2.ap-south-1'), 'cp': (66, 104, 60, 46, 'gear', 'Control plane', 'workflows'),
      'host': (138, 54, 62, 50, 'chip', 'Host', 'configured'), 'dp': (212, 4, 64, 46, 'lb', 'Data plane', 'packets, I/O'), 'cust': (212, 104, 64, 46, 'phone', 'Customers', 'orders'), 'ok': (290, 54, 66, 50, 'shield', 'Still up', 'CP outage')}
RS = [dict(on=['u', 'api'], hot='api', move=(58, 70, 70, 40, 'API call'), head='Step 1 · A control-plane request', text='“Create a load balancer” / “launch 2 instances” — every console click is an API', text2='call to the Region’s endpoint, authenticated and logged (CloudTrail).', svc='Control plane = create, change, delete, describe'),
      dict(on=['u', 'api', 'cp'], hot='cp', move=(96, 50, 96, 104, 'workflow'), head='Step 2 · The control plane does the work', text='Workflows validate, store the desired state, pick hosts and push configuration;', text2='this part is complex and changes often.', svc='Orchestration, placement, configuration databases'),
      dict(on=['u', 'api', 'cp', 'host'], hot='host', move=(126, 127, 150, 90, 'config'), head='Step 3 · Configuration lands on the data plane', text='Hosts, load-balancer nodes and routers receive their configuration and keep a', text2='local copy.', svc='Static configuration on each data-plane component'),
      dict(on=['u', 'api', 'cp', 'host', 'dp', 'cust'], hot='dp', move=(200, 90, 222, 120, 'traffic'), head='Step 4 · The data plane serves your customers', text='Packets, disk reads and HTTP requests flow through the data plane — the simple,', text2='heavily tested, high-volume path. It does not call the control plane per request.', svc='Data plane = the running service'),
      dict(on=list(RN), hot='ok', move=(276, 127, 298, 90, ''), head='Step 5 · Static stability', text='If the control plane has an outage, you may not be able to launch or change things —', text2='but running instances and load balancers keep serving. Design for that.', svc='Pre-provision capacity; avoid control-plane calls during recovery')]
CPDP = flow_anim('Control plane vs data plane', 'Why your running app can survive a cloud console outage.', 'Control vs data plane', 'Animation: an engineer’s API call goes to the control plane, which configures hosts; customers’ traffic flows through the data plane, which keeps working even when the control plane is down.', RN, RS, hid='cpdp')

# ------------------------------------------------------------------ types: six pillars
def mapfig():
    o = t(320, 16, 'Six pillars of a well-architected cloud system', 11, 'ink', bold=True)
    items = [('1', 'Operational excellence', 'run it, improve it', 'blue'), ('2', 'Security', 'protect data and systems', 'red'), ('3', 'Reliability', 'keep working, recover', 'green'),
             ('4', 'Performance efficiency', 'right resources, fast', 'violet'), ('5', 'Cost optimisation', 'value for money', 'amber'), ('6', 'Sustainability', 'less energy and waste', 'green')]
    o += box(20, 170, 600, 26, 'card', rx=6) + t(320, 187, 'Foundation: the cloud infrastructure (Regions, AZs, services) and shared responsibility', 7.6, 'ink', bold=True)
    for i, (n, a, b, tn) in enumerate(items):
        x = 24 + i * 100
        o += box(x, 34, 92, 130, tn, rx=8) + pin(x + 14, 48, n) + t(x + 46, 80, a.split(' ')[0], 7.8, 'ink', bold=True) + t(x + 46, 94, ' '.join(a.split(' ')[1:]), 7.8, 'ink', bold=True) + t(x + 46, 130, b, 6.4, 'ink2')
    o += t(320, 214, 'AWS: 6 pillars · Azure: 5 (no separate sustainability pillar) · Google: 6 (“security, privacy and compliance”, “performance optimization”).', 7.2, 'ink2')
    return o
MAP = bigfig('Six pillars standing on a foundation of cloud infrastructure: operational excellence, security, reliability, performance efficiency, cost optimisation and sustainability.', mapfig(), h=224)

def bars(k, labels, hot, caption):
    o = ''
    for i, l in enumerate(labels):
        on = i <= k
        o += box(20 + i * 112, 34, 100, 74, hot[i] if on else 'card', rx=8)
        for j, w in enumerate(l.split('|')): o += t(70 + i * 112, 62 + j * 14, w, 7.2 if j == 0 else 6.6, 'ink', bold=(j == 0))
    return o + t(180, 132, caption, 7.2, 'ink', bold=True)

def a_ops(k):
    o = t(180, 12, ['Everything as code', 'Small, reversible changes', 'Learn from failures'][k], 9, 'ink', bold=True)
    return o + bars(k, ['IaC|templates in git', 'deploy|small + often|rollback ready', 'post-mortem|blameless|runbook updated'], ['blue', 'green', 'amber'], ['infrastructure and runbooks are versioned', 'many tiny releases instead of one risky big bang', 'every incident improves the system'][k])
A_OPS = cap([a_ops(k) for k in range(3)], [('As code', 'Infrastructure, configuration and runbooks live in version control.', ''), ('Small changes', 'Frequent, small, reversible deployments with automated checks.', ''), ('Learn', 'Blameless post-incident reviews feed improvements back.', '')],
    'Operational excellence in action', 'Run and improve the system safely.', 'Ops excellence', 'Animation: infrastructure as code; small frequent deployments with rollback; blameless post-incident reviews.', 'w1anim')
T1 = vtype(1, 'Operational excellence', 'blue',
    'The <b>operational excellence</b> pillar covers the ability to run and monitor systems to deliver business value and to continually improve processes: performing operations as code, making frequent small reversible changes, anticipating failure, observing everything and learning from operational events.',
    'A railway station that runs on a timetable, a control room and an incident register — not on one station master’s memory.',
    'TiffinGo deploys from GitHub ten times a day in small changes, every environment comes from templates (Lesson 6.4), dashboards show orders per minute, and after the Diwali outage the team wrote a blameless review and automated the fix.',
    'AWS CloudFormation, Systems Manager, CloudWatch, X-Ray; Azure DevOps/GitHub, Azure Monitor, Automation; Google Cloud Build, Cloud Deploy, Cloud Monitoring, Cloud Trace.',
    '', A_OPS,
    'always — it is what makes every other pillar sustainable over time.',
    'operations depend on manual console clicks and one person’s knowledge (the “bus factor” of one).',
    plain='Running the system smoothly: automate routine work, change things in small safe steps, watch everything, and learn from every problem.',
    how=[('Organise', 'Clear ownership, on-call, runbooks.'), ('Prepare', 'Operations as code; dashboards and alarms before launch.'), ('Operate', 'Small, frequent, reversible deployments; health checks.'), ('Observe', 'Metrics, logs, traces tied to business outcomes.'), ('Evolve', 'Post-incident reviews and game days drive improvements.')],
    words=[('runbook', 'step-by-step instructions for a routine task'), ('rollback', 'going back to the previous version'), ('blameless review', 'studying what failed without punishing people'), ('game day', 'a planned practice of failures')],
    diff=table(['', 'Operational excellence', 'Reliability'], [['Focus', 'how the team runs and changes the system', 'how the system survives failures'], ['Typical practice', 'CI/CD, runbooks, observability', 'multi-AZ, backups, failover']], minw=460),
    where=['Every production workload', 'Teams with on-call duties', 'Regulated environments needing change records'],
    realworld='Amazon has described deploying to production thousands of times a day across its services — possible only with small, automated, reversible changes, which is exactly what this pillar asks for.',
    pro='“Operations as code” includes the <i>response</i>: AWS Systems Manager Automation, Azure Automation runbooks and Google Cloud Workflows let an alarm trigger the fix itself — the runbook becomes a program, not a PDF.')

def a_sec(k):
    o = t(180, 12, ['Strong identity', 'Protect data everywhere', 'Detect and respond'][k], 9, 'ink', bold=True)
    return o + bars(k, ['least privilege|roles + MFA', 'encrypt|at rest + in transit|KMS keys', 'trace|logs + alerts|auto-response'], ['red', 'amber', 'violet'], ['nobody uses root; roles grant only what is needed', 'encryption by default, keys managed centrally', 'every action is logged and suspicious ones raise alerts'][k])
A_SEC = cap([a_sec(k) for k in range(3)], [('Identity', 'Least-privilege roles, MFA, no long-lived keys.', ''), ('Data', 'Encryption at rest and in transit; classify data.', ''), ('Detection', 'Logs everywhere, threat detection and automated response.', '')],
    'Security pillar in action', 'Defence in depth.', 'Security', 'Animation: least-privilege identity; encryption at rest and in transit; logging and automated response.', 'w2anim')
T2 = vtype(2, 'Security', 'red',
    'The <b>security</b> pillar covers protecting data, systems and assets: a strong identity foundation with least privilege, traceability, security at every layer (defence in depth), protecting data in transit and at rest, automating security controls and preparing for security events — all within the <b>shared responsibility model</b>.',
    'A bank: ID checks at the door, separate keys for each locker, CCTV everywhere, alarms connected to the police — and the bank, not the customer, guards the building.',
    'TiffinGo staff sign in with SSO + MFA, apps use roles (no keys in code), all buckets and databases are encrypted with KMS keys, private subnets protect the database (Lesson 6.3), and GuardDuty findings go to the on-call phone.',
    'IAM / Identity Center, KMS, Secrets Manager, GuardDuty, Security Hub, WAF; Microsoft Entra ID, Key Vault, Defender for Cloud, Sentinel; Cloud IAM, Cloud KMS, Security Command Center, Cloud Armor.',
    'Module 9 covers cloud security in depth.', A_SEC,
    'from the first day — retrofitting security is much harder.',
    'security is treated as one firewall at the edge, or as only the provider’s job.',
    plain='Keeping the bad guys out and the data safe: only the right people get in, everything is locked (encrypted), and every action is recorded.',
    how=[('Identity first', 'Central identity, MFA, roles, least privilege.'), ('Layers', 'Network, host, app and data controls — each assumes the others may fail.'), ('Data protection', 'Classification, encryption, backups, access logs.'), ('Detection', 'Audit logs, threat detection, alerts.'), ('Response', 'Prepared playbooks and automated containment.')],
    words=[('least privilege', 'only the permissions needed'), ('defence in depth', 'several layers of protection'), ('shared responsibility', 'provider secures the cloud; you secure what you put in it'), ('encryption', 'scrambling data so only key holders can read it')],
    diff=table(['Layer', 'Provider secures (“of the cloud”)', 'You secure (“in the cloud”)'], [['Facilities, hardware, hypervisor', 'yes', '—'], ['Identity, permissions', '—', 'yes'], ['OS on IaaS VMs', '—', 'yes'], ['Data and encryption choices', 'tools provided', 'yes']], minw=480),
    where=['Every workload', 'Compliance: PCI DSS, RBI, DPDP Act 2023', 'Multi-account landing zones'],
    realworld='India’s <b>Digital Personal Data Protection (DPDP) Act, 2023</b> makes companies responsible for safeguarding personal data they process — cloud architecture decisions (encryption, access control, breach detection) are now legal obligations, not just best practice.',
    pro='Most cloud breaches come from the customer side of shared responsibility — leaked keys, public buckets, over-broad roles — not from broken provider infrastructure. That is why every framework puts <b>identity</b> as the first security design principle.')

def a_rel(k):
    o = t(180, 12, ['No single point of failure', 'Automatic recovery', 'Tested recovery'][k], 9, 'ink', bold=True)
    return o + bars(k, ['2+ AZs|load balancer|replicas', 'health checks|auto replace|failover', 'backup restore|chaos test|DR drill'], ['green', 'blue', 'amber'], ['any one component can fail without stopping the service', 'failed parts are detected and replaced automatically', 'recovery is practised, not assumed'][k])
A_REL = cap([a_rel(k) for k in range(3)], [('Redundancy', 'Spread across AZs; no single point of failure.', ''), ('Self-healing', 'Health checks and auto scaling replace failed parts automatically.', ''), ('Practice', 'Restore backups and run failure drills regularly.', '')],
    'Reliability pillar in action', 'Expect failure; recover automatically.', 'Reliability', 'Animation: redundant components across AZs; automatic replacement after health check failure; tested backups and drills.', 'w3anim')
T3 = vtype(3, 'Reliability', 'green',
    'The <b>reliability</b> pillar covers a workload’s ability to perform its intended function correctly and consistently, recover automatically from failure, scale to meet demand and mitigate disruptions — through redundancy, health-based self-healing, managed change and regularly tested recovery.',
    'A hospital with two power lines, a diesel generator and monthly generator tests: patients never notice a power cut.',
    'TiffinGo runs app servers in two AZs behind a load balancer, the database in Multi-AZ, backups copied to Hyderabad, and once a quarter the team deliberately stops one AZ’s servers on staging to prove failover works.',
    'Multi-AZ deployments, Auto Scaling, ELB health checks, AWS Backup, Route 53 failover, Fault Injection Service; Availability Zones, VM Scale Sets, Azure Site Recovery, Chaos Studio; regional MIGs, Cloud Load Balancing, Backup and DR.',
    'Lesson 7.2 covers availability and DR strategies in detail.', A_REL,
    'the service matters to customers — set SLOs (Lesson 5.4) and design to them.',
    'you copy the provider’s SLA as your own or assume backups work without restoring them.',
    plain='Keeping the app working even when parts break — with spare copies, automatic repairs and practised recovery.',
    how=[('Set targets', 'Availability SLO, RTO and RPO per workload.'), ('Remove single points', 'Redundant components across fault domains (AZs, Regions).'), ('Detect', 'Health checks and alarms.'), ('Recover automatically', 'Replace, fail over, retry with backoff.'), ('Test', 'Backup restores, chaos experiments, DR drills.')],
    words=[('single point of failure', 'one part whose failure stops everything'), ('RTO', 'how long recovery may take'), ('RPO', 'how much data may be lost'), ('chaos engineering', 'breaking things on purpose to learn')],
    diff=table(['', 'Reliability', 'Availability (metric)', 'Durability (metric)'], [['Is', 'a design discipline', 'share of time usable', 'chance data is not lost'], ['Measured as', 'SLOs, RTO/RPO met', '99.9%, 99.99%…', '11 nines…']], minw=480),
    where=['Customer-facing apps', 'Payments and banking', 'Healthcare and public services'],
    realworld='Netflix popularised <b>chaos engineering</b> with Chaos Monkey (2011), which randomly terminated production instances so engineers had to build services that survived it; AWS Fault Injection Service and Azure Chaos Studio now offer the same idea as managed services.',
    pro='Retries can cause outages: when every client retries a slow service at once, load multiplies and it never recovers (a “retry storm”). Exponential backoff with <b>jitter</b> and circuit breakers (Lesson 7.5) are reliability features, not optimisations.')

def a_perf(k):
    o = t(180, 12, ['Right resource type', 'Go global in minutes', 'Measure and experiment'][k], 9, 'ink', bold=True)
    return o + bars(k, ['choose|compute/storage/DB|by workload', 'CDN + Regions|near users|serverless', 'benchmark|load test|new instance gens'], ['violet', 'blue', 'green'], ['NoSQL for key lookups, warehouse for analytics, GPU for ML', 'edge caching and nearby Regions cut latency', 'try new options quickly and keep what is faster'][k])
A_PERF = cap([a_perf(k) for k in range(3)], [('Select', 'Pick resource types that fit the workload’s access pattern.', ''), ('Place', 'Serve users from nearby Regions and edges.', ''), ('Review', 'Measure, load-test and adopt new, faster options.', '')],
    'Performance efficiency in action', 'Use the right resources, efficiently.', 'Performance', 'Animation: choosing resource types; placing content near users; measuring and experimenting.', 'w4anim')
T4 = vtype(4, 'Performance efficiency', 'violet',
    'The <b>performance efficiency</b> pillar covers using computing resources efficiently to meet requirements and maintaining that efficiency as demand changes and technologies evolve: selecting the right resource types and sizes, using managed and serverless services, going global with edges and Regions, and experimenting and measuring continuously.',
    'Choosing the right vehicle: a scooter for a tiffin, a tempo for a wedding order, a train for 5,000 meals — not one big truck for everything.',
    'TiffinGo moved the menu lookup from PostgreSQL to a Redis cache (from 40 ms to under 1 ms), put photos behind CloudFront and switched the API servers to Graviton instances after a load test showed better price-performance.',
    'Compute Optimizer, CloudFront, ElastiCache, Graviton; Azure Advisor performance, Front Door, Azure Managed Redis; Google Recommender, Cloud CDN, Memorystore, Axion.',
    '', A_PERF,
    'latency or throughput matter to users, or costs grow with load.',
    'you tune before measuring — optimise the slowest step, not the one you like.',
    plain='Making the app fast without wasting resources — using the right tool for each job, putting content near users, and measuring what is slow.',
    how=[('Select', 'Instance family, storage type, database model per need.'), ('Use managed/serverless', 'Let the provider handle scaling and tuning.'), ('Go global', 'Regions near users, CDN, global load balancing.'), ('Monitor', 'Latency percentiles (p95/p99), throughput, saturation.'), ('Experiment', 'Load tests, A/B different types, adopt new generations.')],
    words=[('latency', 'time for one request'), ('throughput', 'how much work per second'), ('p99', 'the time within which 99% of requests finish'), ('benchmark', 'a standard test to compare options')],
    diff=table(['', 'Performance efficiency', 'Cost optimisation'], [['Question', 'is it fast enough, efficiently?', 'is it worth what we pay?'], ['Typical trade', 'cache, bigger/faster resources', 'smaller, fewer, cheaper resources']], minw=440),
    where=['User-facing APIs', 'Data processing pipelines', 'Gaming and media'],
    realworld='Google reports that slower mobile pages lose users quickly — which is why Indian e-commerce and food apps push images and APIs through CDNs and keep Regions in Mumbai and Hyderabad close to their users.',
    pro='Average latency hides pain: an API with 50 ms average can still have a p99 of 2 seconds. All three frameworks recommend designing and alarming on <b>percentiles</b>, not averages.')

def a_cost(k):
    o = t(180, 12, ['See where money goes', 'Pay only for what you need', 'Keep optimising'][k], 9, 'ink', bold=True)
    return o + bars(k, ['tags|cost by team|budgets', 'right-size|elastic|SP + Spot', 'review|unit cost|₹ per 100 orders'], ['amber', 'green', 'blue'], ['every resource tagged; budgets and alerts', 'match capacity to demand; buy commitments for the baseline', 'track cost per business unit and improve monthly'][k])
A_COST = cap([a_cost(k) for k in range(3)], [('Visibility', 'Tags, cost reports and budgets show who spends what.', ''), ('Efficiency', 'Right-size, scale with demand, use commitments and Spot (Lesson 5.5).', ''), ('Continuous', 'Measure unit cost and review regularly — FinOps.', '')],
    'Cost optimisation in action', 'Value for money, continuously.', 'Cost', 'Animation: tagging and budgets; right-sizing and pricing models; reviewing unit cost.', 'w5anim')
T5 = vtype(5, 'Cost optimisation', 'amber',
    'The <b>cost optimisation</b> pillar covers running systems to deliver business value at the lowest price point: practising cloud financial management, measuring and attributing spend, adopting a consumption model, using the right pricing models, removing waste and analysing cost against business outcomes.',
    'Running a kitchen: buy rice in bulk because you use it daily, rent the extra tandoor only for weddings, and switch off the gas when nobody is cooking.',
    'TiffinGo tags everything by team, has budgets with alerts, a Savings Plan for the two always-on servers, Spot for reports, lifecycle rules for old photos — and tracks <b>₹ per 100 orders</b>, which fell 40% this year while orders doubled.',
    'Cost Explorer, Budgets, Savings Plans, Compute Optimizer, Trusted Advisor; Cost Management, Advisor, reservations; Billing reports, budgets, committed use discounts, Recommender.',
    'Lesson 5.5 covers pricing models in detail.', A_COST,
    'always — but balance it against reliability and performance; the cheapest design that fails is expensive.',
    'cost is checked once a quarter from the invoice, or optimisation removes redundancy that reliability needs.',
    plain='Getting the most value for the money: knowing what you spend, paying only for what you use, and choosing cheaper options where they are good enough.',
    how=[('Own it', 'Finance + engineering share responsibility (FinOps).'), ('Measure', 'Tags, cost allocation, dashboards, budgets.'), ('Consume', 'Scale to demand; turn off idle; serverless where it fits.'), ('Buy smart', 'Savings Plans/reservations for baseline, Spot for flexible work.'), ('Unit economics', 'Cost per customer/order; review trends.')],
    words=[('FinOps', 'shared financial accountability for cloud spend'), ('right-sizing', 'choosing the smallest size that does the job'), ('unit cost', 'cost per order/customer/request'), ('waste', 'resources paid for but not used')],
    diff=table(['', 'Cost optimisation', 'Cost cutting'], [['Goal', 'value per rupee', 'smallest bill'], ['Risk', 'balanced with other pillars', 'often hurts reliability/performance']], minw=420),
    where=['Every workload, especially at scale', 'Start-ups watching burn rate', 'Enterprises with chargeback'],
    realworld='The FinOps Foundation (part of the Linux Foundation) publishes the FinOps framework — inform, optimise, operate — now used by many large Indian IT services firms to manage clients’ cloud bills.',
    pro='The biggest savings are usually <b>architectural</b>, not discounts: replacing an always-on VM fleet with serverless, or a NAT-heavy design with endpoints, often saves more than any Savings Plan.')

def a_sus(k):
    o = t(180, 12, ['Measure the footprint', 'Use less', 'Use cleaner'][k], 9, 'ink', bold=True)
    return o + bars(k, ['carbon tool|kg CO₂e|per service', 'right-size|delete idle|efficient code', 'efficient chips|lower-carbon|Regions'], ['green', 'blue', 'violet'], ['provider carbon dashboards show your emissions', 'idle and oversized resources waste energy', 'efficient hardware (ARM) and greener Regions where allowed'][k])
A_SUS = cap([a_sus(k) for k in range(3)], [('Measure', 'Carbon footprint tools estimate your emissions per service and Region.', ''), ('Reduce', 'Remove idle resources, right-size, keep less data.', ''), ('Choose', 'Efficient instance types and lower-carbon Regions where requirements allow.', '')],
    'Sustainability in action', 'Less energy for the same result.', 'Sustainability', 'Animation: measuring the carbon footprint; reducing idle and oversized resources; choosing efficient hardware and greener Regions.', 'w6anim')
T6 = vtype(6, 'Sustainability', 'green',
    'The <b>sustainability</b> pillar covers minimising the environmental impact of cloud workloads — energy use and emissions — by understanding your footprint, maximising utilisation, choosing efficient hardware and services, reducing data and downstream impact, and selecting Regions by their carbon intensity where business needs allow.',
    'Sharing a bus instead of each person driving: the same journey, far less fuel per person — the cloud’s high utilisation already helps; your design decides the rest.',
    'TiffinGo deletes test environments every night (an Instance Scheduler), moved APIs to ARM (Graviton) instances, compresses photos and keeps only 90 days of debug logs — less energy, and a lower bill too.',
    'AWS Customer Carbon Footprint Tool; Azure Emissions Impact Dashboard / Microsoft Sustainability Manager; Google Cloud Carbon Footprint and region carbon data.',
    '', A_SUS,
    'you want to report or reduce emissions — increasingly asked by investors and large customers (ESG).',
    'you move data to a far-away “green” Region against latency or data-residency rules (e.g. RBI data localisation).',
    plain='Making the cloud app use less electricity and create less pollution — mostly by not wasting resources.',
    how=[('Measure', 'Use the provider’s carbon footprint tool.'), ('Set goals', 'e.g. CO₂e per 1,000 orders.'), ('Maximise utilisation', 'Right-size, autoscale, delete idle.'), ('Efficient tech', 'ARM chips, managed/serverless services, efficient code and formats.'), ('Reduce data', 'Lifecycle rules, compression, fewer copies.')],
    words=[('CO₂e', 'carbon dioxide equivalent — a standard emissions unit'), ('carbon intensity', 'emissions per unit of electricity in a grid'), ('utilisation', 'how much of a resource is actually used'), ('ESG', 'environmental, social and governance reporting')],
    diff=table(['Framework', 'Sustainability'], [['AWS Well-Architected', 'own pillar (added 2021)'], ['Google Cloud Well-Architected', 'own pillar'], ['Azure Well-Architected', 'not a separate pillar — guidance across pillars and a sustainable workloads guide']], minw=440),
    where=['ESG reporting', 'Large-scale compute and storage', 'Data-heavy analytics and AI'],
    realworld='AWS added the sustainability pillar to its Well-Architected Framework in December 2021; Google Cloud publishes carbon-free energy percentages per Region so customers can compare them.',
    pro='The single largest sustainability lever is usually <b>utilisation</b>: an idle VM still draws power. A 10% busy fleet consolidated to 60% busy instances cuts both energy and cost by about the same factor.')

SUMMARY = table(['#', 'Pillar', 'Key question', 'One TiffinGo practice', 'Review tool'], [
    ['1', 'Operational excellence', 'can we run and improve it safely?', 'IaC + small deployments + post-mortems', 'WA Tool / Azure WA Review / Google WAF'], ['2', 'Security', 'is data protected and access minimal?', 'SSO + MFA, roles, KMS, private subnets', 'Security Hub / Defender / SCC'],
    ['3', 'Reliability', 'does it survive and recover from failure?', '2 AZs, Multi-AZ DB, tested backups', 'Resilience Hub / Advisor'], ['4', 'Performance efficiency', 'right resources, fast enough?', 'Redis cache, CDN, Graviton', 'Compute Optimizer / Advisor / Recommender'],
    ['5', 'Cost optimisation', 'value for money?', 'tags, budgets, SP + Spot, ₹/100 orders', 'Cost Explorer / Cost Management / Billing'], ['6', 'Sustainability', 'least environmental impact?', 'nightly shutdowns, ARM, compression', 'Carbon footprint tools']], minw=720)
CHECK = ('  <h3>Check yourself: which pillar?</h3>\n' +
    qx('A. A design review finds the database in a single AZ.', ['Cost', 'Reliability', 'Sustainability', 'Performance'], 1, 'Single point of failure.') +
    qx('B. Developers use the root account’s access keys.', ['Security', 'Performance', 'Cost', 'Operations'], 0, 'Identity foundation.') +
    qx('C. Releases happen once a quarter with a 3-hour manual checklist.', ['Operational excellence', 'Reliability', 'Sustainability', 'Cost'], 0, 'Small, frequent, automated changes.') +
    qx('D. 40% of instances run below 5% CPU all month.', ['Security', 'Cost optimisation (and sustainability)', 'Reliability', 'Performance only'], 1, 'Right-size or remove waste.'))

TYPES = ('  <p>The six pillars, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['Why can retries make an outage worse?', 'Why is “average latency” a misleading target?', 'Which framework has no separate sustainability pillar?'], 'pillars 3, 4 and 6') + MAP
         + jump(['Operations', 'Security', 'Reliability', 'Performance', 'Cost', 'Sustainability']) + T1 + T2 + T3 + T4 + T5 + T6
         + '\n  <h3 style="margin-top:34px">All six side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('Front end', 'What users touch: browsers, apps, SDKs, CLIs.', 'Where experience and security begin.', 'Web/mobile apps, CloudShell, SDKs.'),
    ('Back end', 'Provider-run services and infrastructure.', 'Where data is stored and processed.', 'Compute, storage, databases, networking.'),
    ('Network', 'Connects front end and back end.', 'Latency, security and cost all depend on it.', 'Internet, CDN, VPN, private links.'),
    ('Control plane', 'APIs that create, change and delete resources.', 'Automation and IaC call it; changes are logged.', 'EC2 API, Azure Resource Manager, Google Cloud APIs.'),
    ('Data plane', 'The running service handling your traffic and I/O.', 'Must stay up even when the control plane is impaired.', 'Instance networking, LB nodes, storage I/O.'),
    ('Landing zone', 'A pre-built multi-account foundation with guardrails.', 'Every new project starts secure and governed.', 'AWS Control Tower, Azure landing zones, Google Cloud foundation blueprint.')])

DEEP = ('  <h3>NIST reference architecture: five actors</h3>\n' + table(['Actor', 'Role', 'Example'], [['Cloud consumer', 'uses the services', 'TiffinGo'], ['Cloud provider', 'offers the services', 'AWS, Azure, Google Cloud'], ['Cloud auditor', 'independently assesses controls', 'PCI DSS / ISO 27001 auditor'], ['Cloud broker', 'manages, combines or intermediates services', 'an MSP managing multi-cloud for clients'], ['Cloud carrier', 'provides connectivity', 'Jio, Airtel, Tata Communications']], minw=520) +
    '\n  <p>The NIST Cloud Computing Reference Architecture (SP 500-292) is the standard textbook view and appears in university and C-DAC exams; the Well-Architected frameworks are the practitioner view.</p>\n'
    '  <h3>Comparing the three frameworks</h3>\n' + table(['', 'AWS Well-Architected', 'Azure Well-Architected', 'Google Cloud Well-Architected'], [['Pillars', '6', '5', '6'], ['Review tool', 'AWS Well-Architected Tool (console)', 'Azure Well-Architected Review (assessment) + Advisor', 'framework docs + Recommender / Active Assist'], ['Extras', 'Lenses (serverless, SaaS, ML…)', 'Cloud Adoption Framework, workload guides', 'Architecture Center, industry perspectives']], minw=620) +
    '\n  <h3>Trade-offs are normal</h3>\n  <p>Pillars pull against each other: multi-Region raises reliability but also cost and complexity; heavy encryption and inspection add latency. Architecture is choosing consciously — and writing the choice down (an <b>architecture decision record</b>).</p>')

clouds = vendor_tabs('<p><b>AWS:</b> AWS Well-Architected Framework (6 pillars) and the free Well-Architected Tool; lenses; AWS Architecture Center; Control Tower landing zones; Trusted Advisor checks mapped to pillars.</p>',
    '<p><b>Azure:</b> Azure Well-Architected Framework (5 pillars), Well-Architected Review assessments, Azure Advisor recommendations by pillar, Cloud Adoption Framework and landing zones, Azure Architecture Center.</p>',
    '<p><b>Google Cloud:</b> Google Cloud Well-Architected Framework (6 pillars incl. sustainability), Architecture Center, Recommender / Active Assist recommendations, enterprise foundation blueprint.</p>') + \
    cloud3([['Framework', 'Well-Architected (6)', 'Well-Architected (5)', 'Well-Architected (6)'], ['Review', 'Well-Architected Tool', 'WA Review + Advisor score', 'Recommender + framework checklists'], ['Landing zone', 'Control Tower', 'Azure landing zones', 'foundation blueprint'], ['Reference designs', 'Architecture Center', 'Architecture Center', 'Architecture Center']])

MOCKQ.extend([
 (mock('aws', ['AWS Well-Architected Tool', 'Workloads', 'Define workload'], ['Workloads', 'Custom lenses', 'Profiles', 'Review templates', 'Dashboard'], 'Workloads',
       [('Name', 'tiffingo-orders'), ('Environment', '( ) Production'), ('Regions', '▾ Asia Pacific (Mumbai)'), ('Lenses', '[x] AWS Well-Architected Framework')], 'Next'),
  mock('az', ['Home', 'Advisor', 'Advisor score'], ['Overview', 'Advisor score', 'Reliability', 'Security', 'Performance', 'Cost', 'Operational excellence'], 'Advisor score',
       [('Subscription', '▾ Azure subscription 1'), ('Score by category', 'Reliability · Security · Performance · Cost · Operational excellence')], 'Download as CSV'),
  mock('gcp', ['Recommendations', 'Recommendations overview'], ['Overview', 'All recommendations', 'Cost', 'Security', 'Performance', 'Reliability', 'Sustainability'], 'Overview',
       [('Scope', '▾ project tiffingo-lab'), ('Categories', 'Cost · Security · Performance · Reliability · Manageability · Sustainability')], 'View all')),
 (mock('aws', ['EC2', 'Settings', 'Zones'], ['EC2 Dashboard', 'Settings', 'Zones', 'Account attributes'], 'Zones',
       [('Region', 'Asia Pacific (Mumbai) ap-south-1'), ('Availability Zones', 'ap-south-1a (aps1-az1) · ap-south-1b (aps1-az3) · ap-south-1c (aps1-az2)'), ('Local Zones / Wavelength', 'opt-in status: Not opted in')], 'Manage'),
  mock('az', ['Home', 'Subscriptions', 'Usage + quotas'], ['Overview', 'Resource providers', 'Usage + quotas', 'Cost analysis'], 'Usage + quotas',
       [('Provider · Location', '▾ Compute · Central India'), ('Total Regional vCPUs', '0 of 10 used')], 'Request increase'),
  mock('gcp', ['Compute Engine', 'Zones'], ['VM instances', 'Zones', 'Settings', 'Quotas'], 'Zones',
       [('Region', 'asia-south1'), ('Zones', 'asia-south1-a · asia-south1-b · asia-south1-c')], 'Refresh')),
 (mock('aws', ['CloudTrail', 'Event history'], ['Dashboard', 'Event history', 'Insights', 'Lake', 'Trails'], 'Event history',
       [('Lookup attributes', '▾ Event name = CreateSecurityGroup'), ('Time range', 'last 24 hours'), ('Columns', 'Event time · User name · Event source · Resource')], 'Download events'),
  mock('az', ['Home', 'Monitor', 'Activity log'], ['Overview', 'Activity log', 'Alerts', 'Metrics', 'Logs'], 'Activity log',
       [('Timespan', '▾ Last 24 hours'), ('Resource group', '▾ rg-tiffingo'), ('Operation', 'Create or Update Network Security Group')], 'Export Activity Logs'),
  mock('gcp', ['Logging', 'Logs Explorer'], ['Logs Explorer', 'Log Analytics', 'Logs Dashboard', 'Log Router'], 'Logs Explorer',
       [('Query', 'logName:"cloudaudit.googleapis.com%2Factivity"'), ('Time range', 'Last 1 day')], 'Run query')),
])

STEP1 = ('1 · Run an architecture review on your workload', tri(
    (['Search [[Well-Architected Tool]] → [[Define workload]] → name <code>tiffingo-orders</code>, environment, Region Mumbai, lens [[AWS Well-Architected Framework]] → [[Define workload]].', '[[Start reviewing]] → answer 5 questions of the [[Reliability]] pillar honestly (e.g. “How do you design for failure?”).', '[[Save and exit]] → the dashboard shows high/medium-risk items and links to improvement plans.'],
     "WID=$(aws wellarchitected create-workload --workload-name tiffingo-orders --description \"TiffinGo order API\" \\\n  --environment PRODUCTION --aws-regions ap-south-1 --lenses wellarchitected --review-owner you@example.com \\\n  --query WorkloadId --output text)\naws wellarchitected list-answers --workload-id $WID --lens-alias wellarchitected --pillar-id reliability \\\n  --query 'AnswerSummaries[].QuestionTitle' --output text | tr '\\t' '\\n' | head -5",
     'a workload ID and the first reliability questions (e.g. “How do you manage service quotas and constraints?”). The tool is free.'),
    (['Search [[Advisor]] → [[Advisor score]] — a score per category that maps to the Well-Architected pillars.', 'Open [[Reliability]] and [[Security]] recommendations; click one to see the affected resources and the fix.', 'For a full questionnaire use the Microsoft Learn “Azure Well-Architected Review” assessment (free, in the browser).'],
     'az advisor recommendation list --category HighAvailability --output table\naz advisor recommendation list --category Security --query "[].shortDescription.problem" --output tsv | head',
     'a list (possibly empty on a new subscription) of recommendations with impact High/Medium/Low.'),
    (['Search [[Recommendations]] (Active Assist) → overview by category: cost, security, performance, reliability, sustainability.', 'Open the Well-Architected Framework page from the Architecture Center and go through the reliability checklist for your design.'],
     'P=$(gcloud config get-value project)\ngcloud services enable recommender.googleapis.com\ngcloud recommender recommendations list --project=$P --location=global \\\n  --recommender=google.iam.policy.Recommender --format="table(name.basename(),description)"',
     'IAM role recommendations (least privilege) once the project has some history; empty on a brand-new project.')),
    'Reviews are only useful if you answer honestly — every “no” is an item for the improvement plan.')

STEP2 = ('2 · See the physical infrastructure you rent', tri(
    (['EC2 → [[Settings]] → [[Zones]]: the three Mumbai AZs with their zone IDs and any Local Zones.', 'Top-right Region menu: count the Regions.'],
     "aws ec2 describe-availability-zones --region ap-south-1 --query 'AvailabilityZones[].[ZoneName,ZoneId,State]' --output table\naws ec2 describe-regions --query 'length(Regions)'",
     'ap-south-1a/b/c with IDs like <code>aps1-az1</code> (the mapping differs per account — Lesson 5.1) and the number of Regions enabled for you.'),
    (['[[Subscriptions]] → your subscription → [[Usage + quotas]] → provider Compute, location Central India: your vCPU quota.', 'Search [[Azure regions]] documentation or run the CLI to list Regions and paired Regions.'],
     'az account list-locations --query "[?metadata.regionType==\'Physical\'] | length(@)"\naz account list-locations --query "[?name==\'centralindia\'].{name:name, pair:metadata.pairedRegion[0].name}" --output table\naz vm list-usage --location centralindia --query "[?name.value==\'cores\']" --output table',
     'the number of physical Regions, Central India paired with South India, and your regional vCPU limit.'),
    (['[[Compute Engine]] → [[Zones]]: asia-south1-a, -b, -c.', '[[IAM & Admin]] → [[Quotas & System Limits]] → filter “CPUs” and Region asia-south1.'],
     'gcloud compute regions list --format="value(name)" | wc -l\ngcloud compute zones list --filter="region:asia-south1" --format="table(name,status)"\ngcloud compute regions describe asia-south1 --format="table(quotas.metric,quotas.limit)" | head',
     'the number of Regions, three UP zones in Mumbai, and regional quotas such as CPUS.')),
    'Quotas are part of infrastructure design: a DR plan that needs 200 vCPUs in another Region fails if the quota there is 32.')

STEP3 = ('3 · Watch the control plane: who changed what', tri(
    (['[[CloudTrail]] → [[Event history]] → filter [[Event name]] = <code>CreateSecurityGroup</code> (or any action you did in Module 6).', 'Open an event: user, source IP, time, request parameters — the control plane’s record.'],
     "aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=CreateSecurityGroup \\\n  --max-results 5 --query 'Events[].[EventTime,Username,EventName]' --output table",
     'your own earlier API calls with time and user. Data-plane activity (packets, S3 reads) is not in this history.'),
    (['[[Monitor]] → [[Activity log]] → timespan 24 hours → filter resource group <code>rg-tiffingo</code>.', 'Open an entry → [[JSON]]: caller, operation, status.'],
     'az monitor activity-log list --offset 1d --query "[].{time:eventTimestamp, op:operationName.localizedValue, who:caller}" --output table | head -15',
     'create/update/delete operations you made, with the caller’s e-mail.'),
    (['[[Logging]] → [[Logs Explorer]] → query <code>logName:"cloudaudit.googleapis.com%2Factivity"</code> → [[Run query]].', 'Expand an entry: <code>protoPayload.methodName</code> and <code>authenticationInfo.principalEmail</code>.'],
     'gcloud logging read \'logName:"cloudaudit.googleapis.com%2Factivity"\' --freshness=1d --limit=10 \\\n  --format="table(timestamp,protoPayload.methodName,protoPayload.authenticationInfo.principalEmail)"',
     'Admin Activity audit entries such as <code>v1.compute.instances.insert</code> with your e-mail.')),
    'Every control-plane action is recorded for free (CloudTrail event history 90 days, Activity Log 90 days, Admin Activity audit logs 400 days).')

prac = practical(OWN_INTRO + ' These steps create nothing that costs money (the Well-Architected workload, recommendations and logs are free).', [SETUP_STEP, STEP1, STEP2, STEP3],
    cleanup='<b>AWS:</b> Well-Architected Tool → workload → [[Delete]]; CLI <code>aws wellarchitected delete-workload --workload-id $WID</code>. <b>Azure</b> and <b>Google Cloud:</b> nothing was created (only read).'.replace('[[', '<b>').replace(']]', '</b>'))

mist = mistakes([
    ['Calling a list of services an architecture.', 'Confusing parts with design.', 'Show arrangement, data flow, failure domains and the reasons.'],
    ['Optimising one pillar only.', 'Pressure on cost or speed.', 'Review all pillars; record trade-offs.'],
    ['Recovery that depends on the control plane.', 'Assuming you can launch capacity during an outage.', 'Pre-provision capacity; design for static stability.'],
    ['Never doing a design review.', '“We are too small.”', 'Run a free review on each important workload once a year.'],
    ['Ignoring quotas in DR plans.', 'Quotas are invisible until hit.', 'Check and raise quotas in the DR Region in advance.'],
    ['Security and cost as afterthoughts.', 'Feature pressure.', 'Make them requirements from day one.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Cloud computing architecture: front end, back end, layers; cloud infrastructure components.'], ['AWS CLF-C02', 'Well-Architected Framework pillars and design principles; global infrastructure; shared responsibility.'], ['AZ-900', 'Azure architecture components (Regions, pairs, zones, resource groups, subscriptions); Well-Architected Framework and Advisor.'], ['Google Cloud Digital Leader', 'Google infrastructure and global network; reliability and modernisation principles.']], minw=560) + \
    qx('1. Which pillar focuses on running and monitoring systems and continually improving processes?', ['Reliability', 'Operational excellence', 'Cost optimisation', 'Sustainability'], 1, 'Operations.') + \
    qx('2. “Deploy across multiple Availability Zones” improves mainly…', ['Reliability', 'Sustainability', 'Cost', 'Operational excellence'], 0, 'No single point of failure.') + \
    qx('3. Which AWS tool reviews workloads against the six pillars?', ['AWS Well-Architected Tool', 'AWS Artifact', 'Amazon Inspector', 'AWS Config'], 0, 'Free in the console.') + \
    qx('4. Which Azure service gives recommendations grouped by reliability, security, performance, cost and operational excellence?', ['Azure Advisor', 'Azure Arc', 'Azure Policy', 'Azure Monitor'], 0, 'Advisor.') + \
    qx('5. In the classic cloud architecture, the browser is part of the…', ['back end', 'front end', 'hypervisor', 'data plane'], 1, 'Client side.') + \
    qx('6. Which pillar was added to AWS Well-Architected in 2021?', ['Security', 'Sustainability', 'Reliability', 'Performance'], 1, 'Sustainability.')

proj = miniproject('Mini project: a Well-Architected review of TiffinGo',
    'Turn the pillars into a concrete improvement plan.',
    ['<b>Diagram:</b> draw TiffinGo’s current architecture (front end, network, back end, AZs).',
     '<b>Review:</b> in the AWS Well-Architected Tool (or a spreadsheet) answer at least 3 questions per pillar.',
     '<b>Risks:</b> list the top 5 high-risk items with the pillar they belong to.',
     '<b>Plan:</b> one fix per risk with effort, cost and which other pillar it affects (trade-off).',
     '<b>Control vs data plane:</b> mark which recovery steps need the control plane and how you avoid them.',
     '<b>Record decisions:</b> write two architecture decision records (ADRs).'],
    'A risk list, an improvement plan and two ADRs.', 'This lesson + Modules 5–6.')

assemble_v2(HERE, story_h2='Same services, different results', hook_html=hk,
    narration='Two teams used the same cloud services; one design survived failures and cost half as much. The difference was architecture — and the cloud providers have written down how to judge it.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Cloud architecture and infrastructure',
    formal='<b>Cloud architecture</b> is the structured arrangement of cloud components — front-end clients, the network, and back-end services built on the provider’s <b>infrastructure</b> (global Regions, availability zones, data centres, servers, storage and networking, managed by a <b>control plane</b> and serving traffic through a <b>data plane</b>) — designed to meet functional requirements and the quality attributes of operational excellence, security, reliability, performance efficiency, cost optimisation and sustainability.',
    simple='Cloud infrastructure is what the provider owns and runs; cloud architecture is how you arrange its services into an app that is safe, reliable, fast and affordable.',
    interview=['“Cloud architecture has a front end — browsers, apps, SDKs — and a back end of provider services on global infrastructure: Regions, AZs, data centres, with a control plane for APIs and a data plane that serves traffic.”', '“I evaluate designs with the Well-Architected pillars — operational excellence, security, reliability, performance efficiency, cost optimisation and sustainability — and record trade-offs.”'],
    terms_rows=[('Front end', 'Client side.'), ('Back end', 'Provider-run services.'), ('Infrastructure', 'Regions, AZs, DCs, hardware.'), ('Control plane', 'APIs that change resources.'), ('Data plane', 'Running service path.'), ('Static stability', 'Keep working without control-plane calls.'), ('Well-Architected', 'Framework of pillars.'), ('Pillar', 'Quality area of a design.'), ('Landing zone', 'Governed multi-account foundation.'), ('ADR', 'Architecture decision record.')],
    exam='CLF-C02 asks the six pillars and which practice belongs to which; AZ-900 asks Azure architecture components and Advisor; C-DAC asks the front-end/back-end architecture and layers.',
    picture_h2='The classic architecture, and the infrastructure under it', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Six pillars of good architecture, one by one', TYPES)],
    how_h2='Control plane vs data plane', how_intro='The most important internal split in every cloud service.', how_anim=CPDP,
    parts_h2='Six terms every architecture discussion uses', parts_html=parts, lv='',
    myth_rows=[('Architecture is the list of services.', 'It is how they are arranged, and why.', 'Story.'), ('If the console is down, my app is down.', 'Data planes keep running; design for static stability.', 'How it works.'), ('Good architecture means highest availability.', 'It balances six pillars.', 'Types.')],
    extra_secs=[('deep', 'Deep dive', 'NIST reference architecture, comparing frameworks, trade-offs', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Draw the classic front-end/back-end cloud architecture and its layers.', 'Describe the physical infrastructure behind a cloud Region.', 'Explain control plane vs data plane and static stability.', 'Explain the six Well-Architected pillars with examples.', 'Run an architecture review and read audit logs on your own account.'],
    next_html='<a href="../02-scalability-availability-and-fault-tolerance/">7.2 Scalability, availability and fault tolerance</a>.',
    pre='<b>Before you start:</b> Module 5 (core concepts) and Module 6 (building blocks).')
