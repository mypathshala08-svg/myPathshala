import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)


hk = hook('TiffinGo is moving 8 systems to the cloud: the order API, the website, accounting, the kitchen billing PC, email, a 10-year-old Java reporting tool, an Excel-macro inventory “system” and a legacy fax gateway. Should all of them go to EC2?',
    'No — each system deserves its own answer, and the answer is a <b>service model</b> (IaaS, PaaS, SaaS, serverless) reached through a <b>migration strategy</b>. The industry uses the <b>7 Rs</b>: retire, retain, rehost, relocate, replatform, repurchase, refactor — and each one lands on a different model. This lesson gives you a decision path, the trade-offs in one table, the classic “pizza as a service” picture, and the 7 Rs one by one — then on <b>your own</b> account you price the same app three ways and get right-sizing recommendations.',
    ['A decision path from “is there SaaS?” down to “do I need the OS?”.', 'The 7 Rs of migration — and which service model each one produces.', 'Why the cheapest per-hour option is rarely the cheapest overall.'])

def story_scene():
    o = t(180, 12, 'Eight systems, one question each', 9, 'ink', bold=True)
    items = [('Order API', 'blue'), ('Website', 'green'), ('Accounting', 'violet'), ('Billing PC', 'amber'), ('Email', 'violet'), ('Java reports', 'blue'), ('Excel inventory', 'amber'), ('Fax gateway', 'red')]
    for i, (n, tn) in enumerate(items):
        x = 10 + (i % 4) * 86; y = 26 + (i // 4) * 40
        o += box(x, y, 80, 32, tn, rx=6) + t(x + 40, y + 20, n, 7, 'ink', bold=True)
    o += t(180, 124, 'IaaS? PaaS? SaaS? Serverless? Or retire it?', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Eight TiffinGo systems — order API, website, accounting, billing PC, email, Java reports, Excel inventory, fax gateway — each needing a service-model decision.', story_scene(), 'Decide <tspan font-weight="700" class="s-acc">per workload</tspan>, not per company.', h=136)
dialogue = '''R> Sir, the consultant says “lift everything to EC2, it’s fastest”.
A> Fastest to move, maybe not best to run. Email? We already use Gmail — that is SaaS, done. The fax gateway nobody has used since 2022 — retire it.
K> And the old Java reporting tool?
A> Rehost it on a VM first, then later replatform to a managed database. The order API we are rewriting anyway — serverless or containers.
R> So different answers for different systems.
A> Exactly. Let’s build the decision path and learn the 7 Rs.'''

# ------------------------------------------------------------------ picture
def pizzafig():
    o = t(320, 16, 'Pizza as a service: who does what', 11, 'ink', bold=True)
    layers = ['Dining table', 'Drinks', 'Oven', 'Electricity / gas', 'Pizza dough', 'Toppings', 'Cheese']
    models = [('Made at home', 9), ('Take & bake', 4), ('Delivery', 2), ('Dine out', 0)]
    cloud = ['On-premises', 'IaaS', 'PaaS', 'SaaS']
    for j, (m, _) in enumerate(models):
        x = 150 + j * 120
        o += t(x + 52, 34, m, 8.2, 'ink', bold=True) + t(x + 52, 46, '= ' + cloud[j], 7, 'ink2')
        mine = [7, 4, 2, 0][j]
        for i, l in enumerate(layers):
            o += box(x, 54 + i * 24, 104, 20, 'blue' if i < mine else 'green', rx=3) + t(x + 52, 68 + i * 24, l, 6.8, 'ink')
    o += box(150, 230, 14, 10, 'blue', rx=2) + t(168, 239, 'you do it', 7.2, 'ink', anchor='start') + box(250, 230, 14, 10, 'green', rx=2) + t(268, 239, 'the vendor does it', 7.2, 'ink', anchor='start')
    o += t(76, 130, 'The famous', 7.4, 'ink', bold=True) + t(76, 144, 'analogy, in', 7.4, 'ink', bold=True) + t(76, 158, 'one picture', 7.4, 'ink', bold=True)
    return o
PIZZA = bigfig('Pizza-as-a-service analogy: made at home (on-premises, you do everything), take and bake (IaaS), delivery (PaaS), dine out (SaaS, the vendor does everything).', pizzafig(), h=250)

def decfig():
    o = t(320, 16, 'Choosing a model: a decision path per workload', 11, 'ink', bold=True)
    qs = [('Is the system still needed?', 'no → RETIRE', 'red'), ('Does a SaaS product meet the need?', 'yes → SaaS (repurchase)', 'violet'), ('Is it event-driven, short, spiky?', 'yes → serverless (FaaS + BaaS)', 'green'),
          ('Does the code run on a supported runtime / container?', 'yes → PaaS / container PaaS', 'blue'), ('Needs OS control, special software, licences?', 'yes → IaaS (VMs)', 'amber'), ('Cannot move yet (latency, rules, hardware)?', 'yes → RETAIN on-premises / hybrid', 'card')]
    for i, (q, a, tn) in enumerate(qs):
        y = 30 + i * 34
        o += box(14, y, 350, 26, 'card', rx=5) + t(189, y + 17, q, 7.6, 'ink') + arrow(366, y + 13, 392, y + 13) + box(394, y, 232, 26, tn, rx=5) + t(510, y + 17, a, 7.6, 'ink', bold=True)
    o += t(320, 244, 'Ask from the top: prefer the most managed option that meets the requirement; move down only when you must.', 7.4, 'ink2')
    return o
DEC = bigfig('Decision path: is it still needed (no → retire); does SaaS fit (yes → SaaS); event-driven (yes → serverless); supported runtime (yes → PaaS); needs OS control (yes → IaaS); cannot move (retain).', decfig(), h=254)

picture = ('  <p>The analogy every cloud trainer uses — and it really helps:</p>\n' + PIZZA + '\n  <p>And a decision path to apply to each workload:</p>\n' + DEC +
           '\n  <h3>The trade-offs in one table</h3>\n' + table(['', 'IaaS', 'PaaS', 'SaaS', 'Serverless'], [
               ['You manage', 'OS, runtime, app, data', 'app, data', 'users, settings, data', 'functions, config, data'], ['Control', 'highest', 'medium', 'lowest', 'low–medium'], ['Time to start', 'hours–days', 'minutes', 'minutes', 'minutes'],
               ['Ops effort', 'high', 'low', 'very low', 'very low'], ['Billing', 'per VM hour', 'per plan/instance', 'per user / usage', 'per request + duration'], ['Portability', 'high', 'medium', 'low (data export)', 'low–medium'],
               ['Typical use', 'lift-and-shift, special software', 'web apps, APIs, DBs', 'email, CRM, accounting', 'events, APIs, automation']], minw=640))

# ------------------------------------------------------------------ how: deciding one workload
RN = {'w': (4, 54, 54, 50, 'app', 'Workload', 'Java reports'), 'q1': (66, 4, 60, 46, 'meter', 'Needed?', 'yes'), 'q2': (66, 104, 60, 46, 'cloud', 'SaaS fits?', 'no'),
      'q3': (138, 54, 62, 50, 'gear', 'Runtime ok?', 'Java 8 old'), 'iaas': (212, 4, 64, 46, 'server', 'Rehost', 'IaaS VM now'), 'paas': (212, 104, 64, 46, 'db', 'Replatform', 'RDS later'), 'plan': (290, 54, 66, 50, 'chart', 'Plan', 'cost + date')}
RS = [dict(on=['w', 'q1'], hot='q1', move=(58, 70, 70, 40, 'ask'), head='Step 1 · Is it still needed?', text='Usage logs show 40 managers open the Java reports every Monday — keep it.', text2='(The fax gateway failed this test and was retired.)', svc='Retire first — the cheapest migration is no migration'),
      dict(on=['w', 'q1', 'q2'], hot='q2', move=(96, 50, 96, 104, 'search'), head='Step 2 · Is there SaaS that does this?', text='A BI SaaS could replace it, but the reports have 60 custom calculations — not', text2='this quarter. Note it for later.', svc='Repurchase is often the biggest long-term win'),
      dict(on=['w', 'q1', 'q2', 'q3'], hot='q3', move=(126, 127, 150, 90, 'check'), head='Step 3 · Can it run on a managed platform?', text='It needs Java 8 and a local file share; App Service supports Java but the app', text2='would need changes. Not today.', svc='PaaS needs supported runtimes and 12-factor-ish apps'),
      dict(on=['w', 'q1', 'q2', 'q3', 'iaas'], hot='iaas', move=(200, 70, 222, 40, 'move'), head='Step 4 · Rehost on IaaS now', text='Move the VM as-is (rehost) to EC2/Azure VM/Compute Engine — fast, low risk,', text2='same behaviour. The team still patches the OS.', svc='Migration tools: Application Migration Service, Azure Migrate, Migrate to VMs'),
      dict(on=['w', 'q1', 'q2', 'q3', 'iaas', 'paas'], hot='paas', move=(244, 50, 244, 104, 'improve'), head='Step 5 · Replatform the database next', text='Move its MySQL from the VM to a managed database (RDS/Azure Database/Cloud SQL)', text2='— less ops work, same app code.', svc='Rehost → replatform → refactor is a common journey'),
      dict(on=list(RN), hot='plan', move=(276, 127, 298, 90, 'record'), head='Step 6 · Record the decision and the cost', text='Write down model, strategy, TCO for 3 years and the review date (an', text2='architecture decision record).', svc='Revisit yearly — the right model changes over time')]
DECIDE = flow_anim('Deciding the model for one workload', 'Apply the decision path to TiffinGo’s old Java reporting tool.', 'Model decision', 'Animation: ask if the workload is needed; whether SaaS fits; whether a managed runtime fits; rehost on IaaS now; replatform the database next; record the decision and cost.', RN, RS, hid='decflow')

# ------------------------------------------------------------------ types: 7 Rs
def mapfig():
    o = t(320, 16, 'The 7 Rs of cloud migration — and where each lands', 11, 'ink', bold=True)
    items = [('1', 'Retire', 'switch it off', 'red'), ('2', 'Retain', 'keep on-premises (for now)', 'card'), ('3', 'Rehost', '“lift and shift” → IaaS', 'amber'),
             ('4', 'Relocate', 'move the hypervisor → VMware in cloud', 'violet'), ('5', 'Replatform', '“lift and reshape” → PaaS', 'blue'), ('6', 'Repurchase', '“drop and shop” → SaaS', 'violet'), ('7', 'Refactor', 're-architect → serverless/cloud-native', 'green')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 8.4, 'ink', bold=True) + t(x + 78, y + 54, b, 6.4, 'ink2')
    o += t(320, 210, 'Effort and benefit both grow from rehost → replatform → refactor; repurchase and retire are often the quickest wins.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of the 7 Rs: retire, retain, rehost to IaaS, relocate to cloud VMware, replatform to PaaS, repurchase to SaaS, refactor to serverless/cloud-native.', mapfig(), h=222)

def row3(k, items, tones, cap_):
    o = ''
    for i, l in enumerate(items):
        on = i <= k
        o += box(20 + i * 112, 34, 100, 74, tones[i] if on else 'card', rx=8)
        for j, w in enumerate(l.split('|')): o += t(70 + i * 112, 60 + j * 14, w, 7.2 if j == 0 else 6.6, 'ink', bold=(j == 0))
        if i < 2: o += arrow(120 + i * 112, 71, 132 + i * 112, 71)
    return o + t(180, 132, cap_, 7.2, 'ink', bold=True)

def mk(t3, items, tones, caps, steps, ttl, intro, panel, aria, hid):
    return cap([t(180, 12, t3[k], 9, 'ink', bold=True) + row3(k, items, tones, caps[k]) for k in range(3)], steps, ttl, intro, panel, aria, hid)

A1 = mk(['Find unused systems', 'Agree with owners', 'Switch off, archive'], ['inventory|usage logs|last login', 'owners|“still needed?”|data retention', 'retire|archive data|delete servers'], ['amber', 'blue', 'red'],
        ['usage data shows what nobody uses', 'confirm and decide what data must be kept', 'archive, decommission, save licences and effort'],
        [('Find', 'Usage data reveals systems nobody uses.', ''), ('Agree', 'Owners confirm; legal retention is checked.', ''), ('Retire', 'Archive needed data and switch the system off.', '')],
        'Retire in action', 'The cheapest migration is none.', 'Retire', 'Animation: find unused systems; agree with owners; archive and switch off.', 'r1anim')
T1 = vtype(1, 'Retire', 'red',
    '<b>Retire</b> means decommissioning applications that are no longer useful, after archiving any data that must be kept — removing them from the migration scope entirely.',
    'Clearing the loft before moving house: why pay movers to carry things nobody has used in years?',
    'TiffinGo’s fax gateway had zero traffic since 2022: its few old records went to S3 Glacier Deep Archive and the server was switched off — one less system to migrate, patch or pay for.',
    'Discovery tools (AWS Application Discovery Service / Migration Hub, Azure Migrate discovery, Google Migration Center) to find usage; archive storage tiers for retained data (Lesson 6.2).',
    '', A1,
    'a system has little or no use, or its function exists elsewhere.',
    'legal/regulatory retention requires access to its data — archive properly first.',
    plain='Switching off old systems that nobody needs any more instead of moving them.',
    how=[('Discover', 'Inventory + usage metrics.'), ('Confirm', 'Business owner sign-off.'), ('Retain data', 'Export and archive per policy.'), ('Decommission', 'Shut down, remove access, cancel licences.'), ('Record', 'Update the asset register.')],
    words=[('decommission', 'permanently take out of service'), ('archive', 'keep data cheaply for rare access'), ('asset register', 'list of a company’s systems')],
    diff=table(['', 'Retire', 'Retain'], [['System after', 'gone', 'still running on-premises'], ['Cost after', 'archive only', 'full on-premises cost']], minw=420),
    where=['Duplicate or unused apps', 'Systems replaced by SaaS', 'End-of-life software'],
    realworld='AWS migration guidance commonly reports that a portfolio assessment finds a noticeable share of applications (often around 10%) that can simply be retired — savings before any migration starts.',
    pro='Retiring also shrinks the attack surface: unpatched forgotten servers are classic entry points for attackers.')

A2 = mk(['Some systems must stay', 'Connect them to cloud', 'Revisit later'], ['constraints|latency, hardware|regulation, licence', 'hybrid|VPN / Direct Connect|shared identity', 'review|in 6–12 months|new options'], ['card', 'blue', 'green'],
        ['factory machines, mainframes, very recent purchases', 'they work with cloud systems through hybrid links', 'retain is a decision for now, not forever'],
        [('Constraints', 'Latency, special hardware, regulation or a recent investment keep it on-premises.', ''), ('Hybrid', 'Connect it with VPN/dedicated links and shared identity.', ''), ('Revisit', 'Review the decision periodically.', '')],
        'Retain in action', 'Not yet, and that is fine.', 'Retain', 'Animation: constraints keep a system on-premises; hybrid connection; review later.', 'r2anim')
T2 = vtype(2, 'Retain (revisit)', 'blue',
    '<b>Retain</b> means keeping an application where it is — usually on-premises — for now, because of constraints such as latency to local equipment, unsupported hardware, regulation, licensing, recent investment or business priority, while connecting it to the cloud and revisiting later.',
    'Keeping grandmother’s heavy wooden almirah in the old house until the new flat has a strong enough wall.',
    'The kitchen billing PC is connected to receipt printers and a weighing scale; it stays in the kitchen (retain), syncing sales to the cloud every night.',
    'Hybrid tools: Site-to-Site VPN/Direct Connect, ExpressRoute, Cloud Interconnect; AWS Outposts, Azure Local, Google Distributed Cloud for cloud services on-premises (Module 3).',
    '', A2,
    'there is a real constraint or no business case yet.',
    '“retain” becomes the default for everything difficult — it should come with a reason and a review date.',
    plain='Keeping some systems where they are for now, because there is a good reason they cannot move yet.',
    how=[('Record reason', 'Latency, hardware, regulation, licence, cost.'), ('Integrate', 'Hybrid networking and identity.'), ('Protect', 'Backups/DR possibly to the cloud.'), ('Set review date', 'Re-assess with new services.'), ('Plan exit', 'What must change to move it.')],
    words=[('hybrid', 'combining on-premises and cloud'), ('latency', 'delay; local equipment may need very low delay'), ('review date', 'when to reconsider the decision')],
    diff=table(['', 'Retain', 'Rehost'], [['Location', 'on-premises', 'cloud IaaS'], ['Effort now', 'none', 'migration'], ['Ongoing cost', 'data-centre costs', 'cloud costs']], minw=420),
    where=['Factory and point-of-sale systems', 'Mainframes', 'Regulated systems awaiting approval'],
    realworld='Retail chains often retain store systems (POS, scales, printers) while moving head-office systems to the cloud — and sync data nightly or in real time.',
    pro='AWS’s own model calls this “Retain (revisit)” — the word revisit matters: technologies like Outposts or Local Zones can remove yesterday’s blocking constraint.')

A3 = mk(['Replicate the server', 'Cut over', 'Same app, cloud VM'], ['replicate|disks to cloud|continuously', 'cutover|short downtime|DNS switch', 'IaaS|EC2 / Azure VM|Compute Engine'], ['amber', 'red', 'blue'],
        ['agent copies the whole server', 'test, then switch users over in a short window', 'nothing in the app changed — only where it runs'],
        [('Replicate', 'A migration tool copies the whole server’s disks to the cloud.', ''), ('Cut over', 'After testing, users are switched in a short window.', ''), ('Run', 'The same OS and app now run on a cloud VM.', '')],
        'Rehost in action', 'Lift and shift to IaaS.', 'Rehost', 'Animation: replicate a server to the cloud; cut over; run on a cloud VM.', 'r3anim')
T3 = vtype(3, 'Rehost (lift and shift) → IaaS', 'amber',
    '<b>Rehost</b> (“lift and shift”) moves an application with its operating system to cloud virtual machines without changing its code or architecture, typically using block-level replication tools — the fastest migration path, landing on <b>IaaS</b>.',
    'Moving house with all your furniture exactly as it is — quick, but the old sofa still doesn’t fit the new room perfectly.',
    'The 10-year-old Java reporting tool is replicated with AWS Application Migration Service and cut over on a Sunday night; Monday morning managers see the same reports from EC2.',
    'AWS Application Migration Service (MGN), Azure Migrate (server migration), Google Migrate to Virtual Machines; VM import tools.',
    'VM migration internals (P2V/V2V) are in Lesson 4.4.', A3,
    'deadlines (data-centre exit), many servers, or as a first step before optimising.',
    'you never come back to optimise — you keep paying for over-sized VMs and manual patching.',
    plain='Copying a server exactly as it is into the cloud, without changing the software.',
    how=[('Discover', 'Inventory servers and dependencies.'), ('Replicate', 'Agent-based continuous disk replication.'), ('Test', 'Launch test instances in the cloud.'), ('Cut over', 'Final sync, switch DNS/users.'), ('Optimise later', 'Right-size, Savings Plans, replatform.')],
    words=[('lift and shift', 'move without changes'), ('cutover', 'the moment users switch to the new system'), ('replication agent', 'software that copies disk changes')],
    diff=table(['', 'Rehost', 'Replatform', 'Refactor'], [['Code changes', 'none', 'small', 'large'], ['Speed', 'fastest', 'medium', 'slowest'], ['Cloud benefit', 'low', 'medium', 'highest']], minw=480),
    where=['Large data-centre exits', 'Legacy apps', 'First wave of a migration'],
    realworld='Large enterprise migrations usually begin with rehost waves because they hit data-centre lease deadlines; optimisation comes in later waves.',
    pro='Rehosted servers are often 2–4× over-sized because they were sized for on-premises peaks; right-sizing with Compute Optimizer / Advisor / Recommender after a few weeks of metrics is the cheapest win (step 2 of the lab).')

A4 = mk(['VMware on-premises', 'Same VMware in the cloud', 'vMotion VMs'], ['vSphere|data centre|VMs', 'cloud VMware|on bare metal|in cloud', 'vMotion / HCX|no VM changes|fast moves'], ['violet', 'blue', 'green'],
        ['an existing VMware estate', 'a managed VMware stack on cloud bare metal', 'VMs move without conversion, often live'],
        [('Source', 'A VMware vSphere estate on-premises.', ''), ('Target', 'The same VMware stack running on cloud bare metal.', ''), ('Move', 'VMs move with HCX/vMotion — no conversion.', '')],
        'Relocate in action', 'Move the hypervisor, not the VMs’ format.', 'Relocate', 'Animation: VMware on-premises; VMware on cloud bare metal; VMs moved with vMotion/HCX.', 'r4anim')
T4 = vtype(4, 'Relocate (hypervisor-level move)', 'violet',
    '<b>Relocate</b> moves virtual machines at the hypervisor level — for example from on-premises VMware vSphere to a VMware environment running on cloud bare metal — without converting or changing the VMs, often with live migration; the workloads land on a cloud-hosted private-cloud style IaaS.',
    'Moving an entire shop’s shelves on a truck as they are, then placing them in the new mall unit — products are not even taken off the shelves.',
    'A bank TiffinGo supplies moved 300 VMware VMs to Azure VMware Solution in weeks with HCX, keeping its VMware tools and skills, and planned to modernise afterwards.',
    'Azure VMware Solution, Google Cloud VMware Engine, VMware-based offerings on AWS (partner/Broadcom), Oracle Cloud VMware Solution.',
    'Bare metal and VMware in the cloud are in Lesson 6.1.', A4,
    'large VMware estates must move quickly without re-platforming each VM.',
    'licensing costs dominate — check current VMware licensing terms before choosing.',
    plain='Moving whole groups of virtual machines to the same kind of virtualization software running in the cloud, without changing the machines.',
    how=[('Provision', 'Managed VMware private cloud on bare metal.'), ('Connect', 'Network extension (HCX, ExpressRoute/VPN).'), ('Migrate', 'Bulk or live vMotion.'), ('Operate', 'Same vCenter tools.'), ('Modernise', 'Later move to native services.')],
    words=[('vMotion', 'VMware’s live VM migration'), ('HCX', 'VMware tool for large-scale migration and network extension'), ('private cloud (here)', 'a dedicated VMware environment in a public cloud')],
    diff=table(['', 'Relocate', 'Rehost'], [['Target', 'VMware on cloud bare metal', 'native cloud VMs'], ['VM conversion', 'none', 'yes (drivers, format)'], ['Skills', 'existing VMware', 'cloud-native IaaS']], minw=440),
    where=['Big VMware estates', 'Data-centre exits with tight deadlines', 'DR for VMware'],
    realworld='After Broadcom’s acquisition of VMware (completed 2023) licensing changed significantly, and VMware-in-cloud offerings changed with it — a reminder that relocate decisions depend on vendor terms as much as technology.',
    pro='Relocate is often a stepping stone: it buys time (exit the data centre) while teams later rehost or replatform VM by VM into native services.')

A5 = mk(['Same app', 'Swap a component', 'Less to manage'], ['app|unchanged code|mostly', 'swap|self-run MySQL →|managed DB', 'result|PaaS parts|less ops'], ['blue', 'amber', 'green'],
        ['keep the application architecture', 'replace self-managed parts with managed services', 'backups, patching, scaling handled by the provider'],
        [('Keep', 'The application code and design stay mostly the same.', ''), ('Swap', 'Self-managed parts move to managed services (DB, app platform, containers).', ''), ('Benefit', 'Less operational work and better resilience.', '')],
        'Replatform in action', 'Lift, tinker and shift.', 'Replatform', 'Animation: same app; swap self-managed components for managed services; less to manage.', 'r5anim')
T5 = vtype(5, 'Replatform (lift and reshape) → PaaS', 'blue',
    '<b>Replatform</b> (“lift, tinker and shift”) moves an application to the cloud while making targeted optimisations — such as moving a self-managed database to a managed database, the app to an application platform or containers — without changing its core architecture, landing on <b>PaaS</b> services.',
    'Moving house and replacing the old gas stove with the new building’s piped-gas stove: same kitchen routine, less maintenance.',
    'TiffinGo’s website moves from a VM running Apache + MySQL to Azure App Service + Azure Database for MySQL: the PHP code changes only its connection settings; patching and backups are now Azure’s job.',
    'Elastic Beanstalk, RDS/Aurora, ECS/Fargate; App Service, Azure SQL Managed Instance, Container Apps; App Engine, Cloud SQL, Cloud Run.',
    'PaaS types are in Lesson 2.2.', A5,
    'clear operational wins (managed DB, managed runtime) for modest change.',
    'hidden dependencies (local file writes, OS tools) break on the platform — test thoroughly.',
    plain='Moving an app to the cloud and, on the way, swapping some self-managed parts for ready-made cloud services.',
    how=[('Assess', 'Which components have managed equivalents?'), ('Adapt', 'Config changes, small code tweaks (storage, sessions).'), ('Migrate data', 'Database Migration Service / DMS.'), ('Deploy', 'App platform or containers.'), ('Operate', 'Provider handles patching/backups.')],
    words=[('replatform', 'move with small changes to use managed services'), ('managed instance', 'a nearly fully compatible managed database (e.g. SQL Server)'), ('DMS', 'database migration service')],
    diff=table(['', 'Replatform', 'Rehost'], [['Ops work after', 'lower', 'unchanged'], ['Effort', 'medium', 'low'], ['Lands on', 'PaaS', 'IaaS']], minw=420),
    where=['Web apps with standard stacks', 'Databases', 'Java/.NET apps moving to containers'],
    realworld='Azure SQL Managed Instance exists specifically to make replatforming SQL Server easier: near-100% compatibility with on-premises SQL Server features as a PaaS database.',
    pro='Database migration services (AWS DMS, Azure DMS, Google Database Migration Service) support continuous replication, so the database cutover can be minutes even when the data is terabytes.')

A6 = mk(['Current custom tool', 'Choose SaaS', 'Migrate data, switch'], ['custom|old CRM|self-hosted', 'SaaS|Zoho / Salesforce|subscription', 'switch|import data|retire old'], ['amber', 'violet', 'green'],
        ['an in-house or licensed product you run yourself', 'a SaaS product does the same job', 'move data and users, then retire the old system'],
        [('Current', 'A custom or self-hosted product.', ''), ('Choose', 'A SaaS product meets the need.', ''), ('Switch', 'Import data, train users, retire the old system.', '')],
        'Repurchase in action', 'Drop and shop.', 'Repurchase', 'Animation: a self-run system; choose SaaS; migrate data and switch.', 'r6anim')
T6 = vtype(6, 'Repurchase (drop and shop) → SaaS', 'violet',
    '<b>Repurchase</b> (“drop and shop”) replaces an existing application with a different product — usually <b>SaaS</b> — moving data and users to it and retiring the old system.',
    'Selling your old car and switching to a monthly cab subscription for office travel.',
    'TiffinGo replaces its Excel-macro “inventory system” with a restaurant-inventory SaaS; data is imported from the spreadsheets and staff are trained in one week.',
    'Microsoft 365, Google Workspace, Salesforce, Zoho, ServiceNow, Workday; cloud marketplaces for purchasing (Lesson 2.3).',
    'SaaS kinds are in Lesson 2.3.', A6,
    'the function is standard (email, CRM, HR, accounting, inventory) and a good SaaS exists.',
    'heavy customisations are business-critical and cannot be re-created — weigh the cost of change.',
    plain='Throwing away the old software and buying a ready-made online product that does the same job.',
    how=[('Requirements', 'What must the new product do?'), ('Select', 'Evaluate SaaS (Lesson 2.3 checklist).'), ('Migrate', 'Data import, integrations, SSO.'), ('Train', 'Users and admins.'), ('Retire', 'Switch off the old system.')],
    words=[('drop and shop', 'replace instead of moving'), ('data migration', 'moving records to the new system'), ('change management', 'helping people adopt the new way')],
    diff=table(['', 'Repurchase', 'Refactor'], [['Build effort', 'none (configure)', 'high'], ['Differentiation', 'standard features', 'unique features'], ['Ongoing ops', 'vendor', 'you']], minw=420),
    where=['Email and collaboration', 'CRM, HR, accounting', 'Helpdesk and ITSM'],
    realworld='Moving from on-premises Exchange email to Microsoft 365 or Google Workspace is the most common repurchase in the world — many companies’ first “cloud migration”.',
    pro='Repurchase changes your responsibility profile completely: patching disappears, but identity, data governance and exit planning become the critical work (Lesson 2.3).')

A7 = mk(['Break apart', 'Rebuild cloud-native', 'Scale and evolve'], ['analyse|domains|bottlenecks', 'rebuild|functions, events|managed data', 'cloud-native|auto scale|fast releases'], ['amber', 'green', 'blue'],
        ['understand domains and pain points', 're-architect with serverless, containers, managed services', 'highest agility and efficiency — highest effort'],
        [('Analyse', 'Identify domains, bottlenecks and goals.', ''), ('Rebuild', 'Re-architect with serverless, containers, events and managed data.', ''), ('Evolve', 'Gain elasticity, resilience and faster releases.', '')],
        'Refactor in action', 'Re-architect for the cloud.', 'Refactor', 'Animation: analyse the application; rebuild it cloud-native; scale and evolve.', 'r7anim')
T7 = vtype(7, 'Refactor / re-architect → cloud-native', 'green',
    '<b>Refactor</b> (re-architect) changes an application’s architecture and code to use cloud-native capabilities — microservices, serverless functions, managed databases, event-driven integration, containers — to gain scalability, agility and efficiency that the existing design cannot reach; it is the highest-effort, highest-benefit strategy.',
    'Rebuilding an old house into a modern apartment with lifts, solar panels and piped gas — expensive, but life afterwards is much easier.',
    'TiffinGo’s order API is being rewritten as API Gateway + Lambda + DynamoDB + EventBridge (Lessons 7.3–7.4), moved feature by feature with the strangler fig pattern.',
    'AWS Lambda, ECS/EKS, DynamoDB, EventBridge, Step Functions; Azure Functions, Container Apps/AKS, Cosmos DB, Event Grid; Cloud Run, GKE, Firestore/Spanner, Pub/Sub.',
    'Architecture styles are in Lesson 7.4.', A7,
    'the business needs scale, speed of change or cost efficiency the current design blocks.',
    'there is no clear business driver — refactoring for its own sake is expensive.',
    plain='Redesigning and rewriting an app so it uses the cloud’s modern services properly.',
    how=[('Business case', 'Which limits must be removed?'), ('Domain design', 'Boundaries, events, data ownership.'), ('Incremental', 'Strangler fig, feature by feature.'), ('Automate', 'IaC, CI/CD, observability.'), ('Optimise', 'Costs, performance, reliability.')],
    words=[('cloud-native', 'designed for the cloud: elastic, managed, automated'), ('re-architect', 'change the structure of a system'), ('strangler fig', 'replace a system piece by piece')],
    diff=table(['', 'Refactor', 'Replatform'], [['Architecture change', 'yes', 'no'], ['Effort', 'high', 'medium'], ['Benefit', 'highest', 'moderate']], minw=420),
    where=['Core customer-facing systems', 'Products that must scale fast', 'Systems with high change rates'],
    realworld='AWS publicised the “6 Rs” (from Gartner’s earlier 5 Rs) and later added a 7th R, Relocate; Azure’s Cloud Adoption Framework uses similar terms (rehost, refactor, rearchitect, rebuild, replace).',
    pro='Refactor does not have to mean rewrite: extracting one hot path (e.g. checkout) into serverless while rehosting the rest often delivers most of the benefit for a fraction of the cost.')

SUMMARY = table(['#', 'R', 'Lands on', 'Effort', 'TiffinGo system'], [
    ['1', 'Retire', '— (off)', 'very low', 'fax gateway'], ['2', 'Retain', 'on-premises / hybrid', 'none now', 'kitchen billing PC'], ['3', 'Rehost', 'IaaS', 'low', 'Java reporting tool (wave 1)'],
    ['4', 'Relocate', 'cloud VMware (IaaS)', 'low', '— (bank partner’s VMware)'], ['5', 'Replatform', 'PaaS', 'medium', 'website + MySQL'], ['6', 'Repurchase', 'SaaS', 'low–medium', 'Excel inventory, email (Gmail)'], ['7', 'Refactor', 'serverless / cloud-native', 'high', 'order API']], minw=600)
CHECK = ('  <h3>Check yourself: which R?</h3>\n' +
    qx('A. Move 200 VMs before the data-centre lease ends in 3 months, no code changes.', ['Refactor', 'Rehost', 'Repurchase', 'Retire'], 1, 'Lift and shift.') +
    qx('B. Replace self-hosted Exchange with Microsoft 365.', ['Repurchase', 'Replatform', 'Relocate', 'Retain'], 0, 'Drop and shop.') +
    qx('C. Move the app’s MySQL from a VM to a managed database, code unchanged.', ['Replatform', 'Refactor', 'Retire', 'Rehost'], 0, 'Lift and reshape.') +
    qx('D. Rewrite the order system as serverless microservices.', ['Rehost', 'Refactor', 'Retain', 'Relocate'], 1, 'Re-architect.'))

TYPES = ('  <p>The 7 Rs, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note. Each R leads to a different service model.</p>\n'
         + challenge(['Why are rehosted VMs often 2–4× over-sized?', 'What does “revisit” in “Retain (revisit)” remind you to do?', 'Which R often removes the most risk before any migration starts?'], 'types 3, 2 and 1') + MAP
         + jump(['Retire', 'Retain', 'Rehost', 'Relocate', 'Replatform', 'Repurchase', 'Refactor']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('Control', 'How much of the stack you can change.', 'Special software or OS settings need IaaS.', 'Kernel modules, agents, licensed software.'),
    ('Speed to market', 'How quickly you can deliver.', 'PaaS/SaaS/serverless start in minutes.', 'MVPs, campaigns, new products.'),
    ('Skills', 'What your team can operate.', 'IaaS needs sysadmin skills; SaaS needs admin skills.', 'Small teams favour managed models.'),
    ('Total cost of ownership', 'All costs over years, including people.', 'Per-hour prices mislead (Lesson 5.5).', 'Ops hours, licences, downtime.'),
    ('Compliance and residency', 'Where data lives and who controls it.', 'May restrict SaaS choices or require dedicated options.', 'DPDP Act, RBI, sector rules.'),
    ('Portability / lock-in', 'How hard it is to move later.', 'IaaS most portable; SaaS least.', 'Containers and open standards help.')])

DEEP = ('  <h3>Mixing models is normal</h3>\n  <p>Real systems combine models: TiffinGo’s order platform uses SaaS (Razorpay, Gmail), PaaS (RDS, App Service), serverless (Lambda) and IaaS (one VM for the reporting tool). The question is never “IaaS or PaaS for the company” but “which model for this component”.</p>\n'
    '  <h3>TCO example (illustrative, 3 years, one small web app)</h3>\n' + table(['Cost item', 'IaaS VM', 'PaaS', 'Serverless'], [['Compute', 'VM 24×7', 'plan 24×7', 'per request'], ['OS patching & hardening', '~4 h/month of staff time', '0', '0'], ['Scaling & HA setup', 'you build it', 'setting', 'built in'], ['Backups', 'you configure', 'built in', 'built in (managed DB)'], ['Best when', 'special needs', 'steady web apps', 'spiky / low traffic']], minw=520) +
    '\n  <p>Staff hours are usually the biggest hidden cost — at even ₹1,000/hour, 4 hours a month of patching is ₹1.4 lakh over 3 years.</p>\n'
    '  <h3>Frameworks for migration decisions</h3>\n  <ul><li><b>AWS:</b> Migration Acceleration Program, Migration Hub, 7 Rs, Cloud Adoption Framework (AWS CAF).</li><li><b>Azure:</b> Cloud Adoption Framework (strategy, plan, ready, adopt), Azure Migrate.</li><li><b>Google Cloud:</b> Migration Center, Cloud Adoption Framework, migration paths (lift and shift, improve and move, rip and replace).</li></ul>')

clouds = vendor_tabs('<p><b>AWS:</b> IaaS (EC2), PaaS (Elastic Beanstalk, RDS), serverless (Lambda, Fargate), SaaS via AWS Marketplace; migration: Application Migration Service, Database Migration Service, Migration Hub, Migration Evaluator; Compute Optimizer for right-sizing.</p>',
    '<p><b>Azure:</b> IaaS (VMs), PaaS (App Service, Azure SQL), serverless (Functions, Container Apps), SaaS (Microsoft 365, Dynamics 365); migration: Azure Migrate, Database Migration Service, Azure VMware Solution; Advisor for right-sizing.</p>',
    '<p><b>Google Cloud:</b> IaaS (Compute Engine), PaaS (App Engine, Cloud SQL), serverless (Cloud Run), SaaS (Google Workspace); migration: Migration Center, Migrate to Virtual Machines, Database Migration Service, Google Cloud VMware Engine; Recommender for right-sizing.</p>') + \
    cloud3([['Rehost tool', 'Application Migration Service', 'Azure Migrate', 'Migrate to Virtual Machines'], ['Relocate target', 'VMware partner offerings', 'Azure VMware Solution', 'Google Cloud VMware Engine'], ['DB replatform', 'DMS → RDS/Aurora', 'DMS → Azure SQL / MI', 'DMS → Cloud SQL / AlloyDB'], ['Assessment', 'Migration Hub / Evaluator', 'Azure Migrate assessment', 'Migration Center'], ['Right-sizing', 'Compute Optimizer', 'Advisor', 'Recommender']])

# ------------------------------------------------------------------ practical
MOCKQ.extend([
 (mock('aws', ['AWS Pricing Calculator', 'Add service'], ['My Estimate', 'Add service', 'Groups'], 'Add service',
       [('Group 1 · IaaS', 'Amazon EC2 t3.small Linux, 730 h, Mumbai'), ('Group 2 · PaaS', 'Elastic Beanstalk = the EC2 + load balancer it creates'), ('Group 3 · Serverless', 'Lambda 1M requests, 256 MB, 200 ms + API Gateway')], 'Save and view summary'),
  mock('az', ['Pricing calculator', 'Your estimate'], ['Products', 'Example scenarios', 'Saved estimates'], 'Products',
       [('IaaS', 'Virtual Machines · B1s · Central India · 730 h'), ('PaaS', 'App Service · Linux · Basic B1'), ('Serverless', 'Functions · Flex Consumption · 1M executions')], 'Export'),
  mock('gcp', ['Google Cloud Pricing Calculator', 'Estimate'], ['Add to estimate', 'Estimate summary'], 'Add to estimate',
       [('IaaS', 'Compute Engine · e2-small · asia-south1 · 730 h'), ('PaaS', 'App Engine · F1 instance class'), ('Serverless', 'Cloud Run · 1M requests · 0.25 vCPU')], 'Share')),
 (mock('aws', ['Compute Optimizer', 'Dashboard'], ['Dashboard', 'EC2 instances', 'Auto Scaling groups', 'EBS volumes', 'Lambda functions'], 'Dashboard',
       [('Account status', '[x] Opted in'), ('Findings', 'Over-provisioned · Under-provisioned · Optimized')], 'View recommendations'),
  mock('az', ['Home', 'Advisor', 'Cost'], ['Overview', 'Cost', 'Reliability', 'Performance'], 'Cost',
       [('Recommendation', 'Right-size or shut down underutilized virtual machines'), ('Potential yearly savings', 'shown per resource')], 'Download'),
  mock('gcp', ['Recommendations', 'Cost'], ['Overview', 'Cost', 'Performance', 'Security'], 'Cost',
       [('Recommender', 'VM machine type recommendations'), ('Example', 'e2-standard-4 → e2-standard-2 (CPU < 10%)')], 'Apply')),
])

STEP1 = ('1 · Price the same web app three ways', tri(
    (['Open <b>calculator.aws</b> → [[Create estimate]] → [[Add group]] three times: IaaS, PaaS, Serverless.', 'IaaS: EC2 t3.small, Linux, Mumbai, 730 h. PaaS: Elastic Beanstalk itself is free — price the EC2 (+ load balancer if multi-instance) it creates. Serverless: Lambda 1 million requests/month, 256 MB, 200 ms, plus API Gateway HTTP API 1 million requests.', '[[View summary]] → compare monthly cost — then add ~4 hours/month of patching time to the IaaS row yourself.'],
     "aws pricing get-products --region us-east-1 --service-code AmazonEC2 \\\n  --filters Type=TERM_MATCH,Field=instanceType,Value=t3.small Type=TERM_MATCH,Field=regionCode,Value=ap-south-1 \\\n            Type=TERM_MATCH,Field=operatingSystem,Value=Linux Type=TERM_MATCH,Field=tenancy,Value=Shared \\\n            Type=TERM_MATCH,Field=preInstalledSw,Value=NA Type=TERM_MATCH,Field=capacitystatus,Value=Used \\\n  --query 'PriceList[0]' --output text | python3 -c \"import sys,json; d=json.loads(sys.stdin.read()); t=list(d['terms']['OnDemand'].values())[0]; print(list(t['priceDimensions'].values())[0]['pricePerUnit'])\"",
     'the On-Demand hourly price in USD for t3.small in Mumbai; × 730 = the monthly IaaS compute cost. Lambda at this volume is mostly inside the free tier.'),
    (['Open the <b>Azure Pricing calculator</b> → add [[Virtual Machines]] (B1s, Central India), [[App Service]] (Linux, Basic B1) and [[Azure Functions]] (Flex Consumption, 1M executions).', 'Compare monthly totals; note what each includes (App Service includes the runtime, TLS, scaling settings).'],
     "curl -s \"https://prices.azure.com/api/retail/prices?\\$filter=serviceName%20eq%20'Azure%20App%20Service'%20and%20armRegionName%20eq%20'centralindia'%20and%20skuName%20eq%20'B1'%20and%20priceType%20eq%20'Consumption'\" \\\n  | python3 -c \"import sys,json; [print(i['productName'], i['meterName'], i['retailPrice'], i['unitOfMeasure']) for i in json.load(sys.stdin)['Items'][:5]]\"",
     'retail prices for App Service B1 in Central India per hour from Azure’s public price API (no sign-in needed).'),
    (['Open the <b>Google Cloud Pricing Calculator</b> → add Compute Engine (e2-small, asia-south1, 730 h), App Engine standard (F1/F2), and Cloud Run (1M requests, 0.25 vCPU, 256 MiB).', 'Compare; Cloud Run’s free tier covers small apps.'],
     'gcloud compute machine-types describe e2-small --zone=asia-south1-a --format="value(guestCpus,memoryMb)"\n# Prices come from the calculator or the Cloud Billing Catalog API (needs an API key); the CLI shows the shape you are pricing.',
     'e2-small = 2 shared vCPUs, 2,048 MB — the machine you priced.')),
    'Per-hour prices are only half of TCO — add the people-hours each model needs.')

STEP2 = ('2 · Right-size before (and after) you choose', tri(
    (['[[Compute Optimizer]] → [[Get started]] → [[Opt in]] (free).', 'After about 30 hours of metrics, [[EC2 instances]] shows each instance as over-provisioned, under-provisioned or optimized, with cheaper suggestions.'],
     'aws compute-optimizer update-enrollment-status --status Active\naws compute-optimizer get-enrollment-status\naws compute-optimizer get-ec2-instance-recommendations --query "instanceRecommendations[].[instanceArn,finding,recommendationOptions[0].instanceType]" --output table',
     '<code>Active</code>, then (once there is data) a table of findings; empty on an account without running instances.'),
    (['[[Advisor]] → [[Cost]] → “Right-size or shut down underutilized virtual machines” and reservation suggestions.'],
     'az advisor recommendation list --category Cost --query "[].{problem:shortDescription.problem, impact:impact, resource:impactedValue}" --output table',
     'cost recommendations (empty if you have no long-running VMs).'),
    (['[[Recommendations]] → [[Cost]] → machine-type (“rightsizing”) and idle-VM recommendations per zone.'],
     'P=$(gcloud config get-value project)\ngcloud recommender recommendations list --project=$P --location=asia-south1-a \\\n  --recommender=google.compute.instance.MachineTypeRecommender --format="table(description,primaryImpact.costProjection.cost.units)"',
     'machine-type recommendations with projected savings (needs VMs with a few days of metrics).')),
    'Right-sizing is part of choosing a model: a rehosted VM that is 4× too big may make IaaS look more expensive than it should — or hide that PaaS is cheaper.')

prac = practical(OWN_INTRO + ' Both steps only read prices and recommendations — nothing is created that costs money.', [SETUP_STEP, STEP1, STEP2],
    cleanup='Nothing to delete. On AWS you can opt out of Compute Optimizer with <code>aws compute-optimizer update-enrollment-status --status Inactive</code> (it is free either way).')

mist = mistakes([
    ['One model for the whole company.', 'Standardisation instinct.', 'Decide per workload with the decision path.'],
    ['Lift and shift everything, never optimise.', 'Deadline pressure.', 'Plan waves: rehost → right-size → replatform.'],
    ['Comparing only per-hour prices.', 'Easy to compare.', 'Compare 3-year TCO including staff time and downtime.'],
    ['Refactoring without a business case.', 'Technology enthusiasm.', 'Refactor where scale/agility limits hurt; repurchase or rehost elsewhere.'],
    ['Forgetting retire.', 'Inventory not checked.', 'Usage-based portfolio assessment first.'],
    ['Ignoring data residency in SaaS choices.', 'Feature focus.', 'Check Region, certifications and export before buying.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Comparison of IaaS, PaaS and SaaS; choosing a service model.'], ['AWS CLF-C02', 'Shared responsibility across service models; migration strategies (7 Rs); AWS CAF; migration tools.'], ['AZ-900', 'Compare IaaS, PaaS, SaaS; shared responsibility; use cases for each.'], ['Google Cloud Digital Leader', 'Choosing between IaaS/PaaS/SaaS/serverless; modernisation and migration paths.']], minw=560) + \
    qx('1. Which model gives the customer the most control over the operating system?', ['SaaS', 'PaaS', 'IaaS', 'FaaS'], 2, 'IaaS.') + \
    qx('2. Moving an app to cloud VMs without code changes is…', ['refactor', 'rehost', 'repurchase', 'retire'], 1, 'Lift and shift.') + \
    qx('3. Replacing an on-premises CRM with Salesforce is…', ['replatform', 'repurchase', 'relocate', 'retain'], 1, 'Drop and shop.') + \
    qx('4. Moving a database from a VM to Amazon RDS without changing the app is…', ['replatform', 'rehost', 'refactor', 'retire'], 0, 'Lift and reshape.') + \
    qx('5. For which model is the customer responsible for the fewest layers?', ['IaaS', 'PaaS', 'SaaS', 'on-premises'], 2, 'SaaS.') + \
    qx('6. Which AWS tool recommends right-sized EC2 instance types from utilisation data?', ['AWS Compute Optimizer', 'AWS Artifact', 'Amazon Macie', 'AWS Snowball'], 0, 'Compute Optimizer.')

proj = miniproject('Mini project: TiffinGo’s migration plan for 8 systems',
    'Turn the decision path and the 7 Rs into a real plan.',
    ['<b>Table</b> the 8 systems with owner, users, usage and constraints.',
     '<b>Decide</b> an R and a service model for each using the decision path; one line why.',
     '<b>Waves:</b> group them into 3 migration waves (quick wins first: retire, repurchase).',
     '<b>Cost:</b> price at least 2 systems in two models with the calculators (step 1).',
     '<b>Right-size:</b> note how you will right-size rehosted VMs after a month (step 2).',
     '<b>Decision records:</b> write ADRs for the two hardest choices.'],
    'A one-page migration plan with R, model, wave and cost per system.', 'Module 2 + 5.5 (pricing) + 7.4 (refactor patterns).')

assemble_v2(HERE, story_h2='Eight systems, one consultant’s answer', hook_html=hk,
    narration='A consultant suggested moving all eight TiffinGo systems to virtual machines. The founder wanted to know whether one answer could really be right for email, a fax gateway and a brand-new order API.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='IaaS vs PaaS vs SaaS: choosing a model',
    formal='Choosing a <b>cloud service model</b> means deciding, per workload, how much of the technology stack the organisation manages — <b>IaaS</b> (infrastructure; you manage OS and up), <b>PaaS</b> (platform; you manage application and data), <b>SaaS</b> (software; you manage users, settings and data) or <b>serverless</b> (functions and managed services) — based on control, speed, skills, total cost of ownership, compliance and portability, typically reached through migration strategies known as the <b>7 Rs</b>.',
    simple='For each system, decide how much you want to run yourself: the computer (IaaS), just your code (PaaS/serverless), or nothing but the settings (SaaS).',
    interview=['“I choose per workload: SaaS if a product fits, serverless for event-driven pieces, PaaS for standard apps and managed databases, and IaaS when I need OS control or for fast lift-and-shift.”', '“Migration strategies are the 7 Rs — retire, retain, rehost, relocate, replatform, repurchase, refactor — each landing on a different model.”'],
    terms_rows=[('Service model', 'IaaS / PaaS / SaaS / serverless.'), ('7 Rs', 'Migration strategies.'), ('Rehost', 'Lift and shift → IaaS.'), ('Replatform', 'Lift and reshape → PaaS.'), ('Repurchase', 'Drop and shop → SaaS.'), ('Refactor', 'Re-architect → cloud-native.'), ('Relocate', 'Hypervisor-level move.'), ('Retain', 'Keep for now.'), ('Retire', 'Switch off.'), ('TCO', 'Total cost of ownership.')],
    exam='Expect “which model gives most control”, “who patches the OS in PaaS”, and migration-strategy scenarios (rehost vs replatform vs repurchase vs refactor).',
    picture_h2='Pizza as a service, the decision path and the trade-offs', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'The 7 Rs of migration, one by one', TYPES)],
    how_h2='Deciding the model for one workload', how_intro='The decision path applied to a real system.', how_anim=DECIDE,
    parts_h2='Six factors that decide the model', parts_html=parts, lv='',
    myth_rows=[('IaaS is cheapest because VMs are cheap per hour.', 'Staff time and idle capacity often make it the most expensive.', 'Deep dive TCO.'), ('Everything must be refactored to benefit from cloud.', 'Rehost, replatform and repurchase all have their place.', 'The 7 Rs.'), ('One model per company.', 'Models are mixed per component.', 'Deep dive.')],
    extra_secs=[('deep', 'Deep dive', 'Mixing models, TCO example, migration frameworks', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Compare IaaS, PaaS, SaaS and serverless on control, effort, cost and portability.', 'Apply a decision path to choose a model per workload.', 'Explain the 7 Rs and which model each produces.', 'Price one app in three models and right-size resources on your own account.', 'Write a migration plan with waves and decision records.'],
    next_html='Module 3 — <a href="../../03-deployment-models/01-public-private-hybrid-and-community-cloud/">3.1 Public, private, hybrid and community cloud</a>.',
    pre='<b>Before you start:</b> Lessons 2.1–2.4.')
