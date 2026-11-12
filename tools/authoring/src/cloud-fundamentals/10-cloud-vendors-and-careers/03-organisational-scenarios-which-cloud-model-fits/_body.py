import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)
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
def vt(n, name, tone, d, an, sc, ex, gd, anim, use, avoid, plain, how, words, diff, where, rw, pro):
    return vtype(n, name, tone, d, an, sc, ex, gd, anim, use, avoid, plain=plain, how=how, words=words, diff=diff, where=where, realworld=rw, pro=pro)


hk = hook('Four TiffinGo customers ask the same question in one week: a two-person start-up, a cooperative bank, a state health department and an engineering college. “Which cloud model should we use?” Should they all get the same answer?',
    'No. The right <b>deployment model</b> (Module 3), <b>service model</b> (Module 2) and <b>provider</b> (10.1) depend on the organisation: its size, money, skills, regulations, data sensitivity and growth. This lesson works through seven organisation types one by one, animates the decision for one real scenario, and on <b>your own</b> account you use the providers’ review tools, set up cost allocation by department, and check that the services a scenario needs exist in India Regions.',
    ['The same app can be right on serverless for a start-up and wrong for a bank.', 'Why government and banks start with compliance, not with features.', 'A repeatable seven-question method you can use in any interview case study.'])

def story_scene():
    o = t(180, 12, 'Same question, different organisations', 9, 'ink', bold=True)
    for i, (a, b, tn) in enumerate([('Start-up', 'speed, cash', 'green'), ('Co-op bank', 'RBI rules', 'amber'), ('State health', 'MeitY, privacy', 'red'), ('College', 'labs, budget', 'blue')]):
        x = 8 + i * 88
        o += box(x, 30, 80, 58, tn, rx=8) + t(x + 40, 54, a, 7.8, 'ink', bold=True) + t(x + 40, 70, b, 6.8, 'ink2')
    o += t(180, 110, 'Constraints decide the model — not fashion', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Four organisations asking the same question: a start-up (speed, cash), a cooperative bank (RBI rules), a state health department (MeitY, privacy), a college (labs, budget).', story_scene(), 'Start from <tspan font-weight="700" class="s-acc">constraints</tspan>, then pick the model.', h=124)
dialogue = '''R> Sir, can’t we just say “public cloud, serverless, AWS” to everyone? It worked for us.
A> For a two-person start-up, maybe. The co-op bank must follow RBI outsourcing rules and keep payment data in India. The health department needs an empanelled provider. The college wants free student credits.
K> So we need a method, not a favourite answer.
A> Seven questions: users, data sensitivity, regulations, skills, budget shape, existing systems, growth. Then deployment model, service model, provider, governance.
R> Let’s try it on each type of organisation.'''

def methodfig():
    o = t(320, 16, 'Seven questions before choosing any cloud model', 11, 'ink', bold=True)
    Q = [('1', 'Who uses it, where?', 'users, latency'), ('2', 'How sensitive is the data?', 'personal, payments, health'), ('3', 'Which rules apply?', 'DPDP, RBI, CERT-In, sector'), ('4', 'What skills exist?', 'team, partners'),
         ('5', 'What budget shape?', 'capex vs opex, credits'), ('6', 'What already exists?', 'licences, data centre, apps'), ('7', 'How will it grow?', 'spikes, scale, new markets')]
    for i, (n, a, b) in enumerate(Q):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 70
        o += box(x, y, 148, 58, 'card', rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 28, a, 7.6, 'ink', bold=True) + t(x + 78, y + 46, b, 6.6, 'ink2')
    o += box(484, 102, 148, 58, 'green', rx=8) + t(558, 124, '→ Decide', 8.4, 'ink', bold=True) + t(558, 142, 'deployment · service · provider', 6.6, 'ink2')
    o += t(320, 184, 'Answer these in order; most choices become obvious by question 3.', 7.4, 'ink2')
    return o
METHOD = bigfig('Seven questions: who uses it and where; data sensitivity; applicable rules; skills; budget shape; existing systems; growth — then decide deployment model, service model and provider.', methodfig(), h=194)

picture = ('  <p>A repeatable method beats a favourite answer:</p>\n' + METHOD +
           '\n  <h3>The three decisions</h3>\n' + table(['Decision', 'Options', 'Lesson'], [['Deployment model', 'public, private, hybrid, community, multi-cloud, sovereign', 'Module 3'], ['Service model', 'IaaS, PaaS, SaaS, serverless — per workload', 'Module 2 (2.5)'], ['Provider(s)', 'AWS, Azure, Google Cloud, OCI, IBM, Indian providers', '10.1'], ['Governance', 'hierarchy, guard-rails, identity, budgets', '9.x, 10.1']], minw=520))

RN = {'req': (4, 54, 50, 50, 'user', 'Needs', 'state health'), 'rule': (66, 4, 62, 46, 'shield', 'Rules', 'DPDP, MeitY'), 'skill': (66, 104, 62, 46, 'chart', 'Skills', 'small IT team'),
      'dep': (142, 54, 60, 50, 'cloud', 'Deployment', 'community / gov'), 'svc': (216, 4, 62, 46, 'app', 'Service', 'SaaS + PaaS'), 'prov': (216, 104, 62, 46, 'server', 'Provider', 'empanelled'), 'gov': (292, 54, 64, 50, 'gear', 'Governance', 'India-only, MFA')}
RS = [dict(on=['req'], hot='req', move=None, head='Step 1 · Understand the need', text='A state health department wants a nutrition-tracking app for 2,000 anganwadi', text2='centres, with dashboards for district officers.', svc='Users: field workers on phones, officers on laptops'),
      dict(on=['req', 'rule'], hot='rule', move=(54, 79, 72, 30, 'rules'), head='Step 2 · Rules first', text='Children’s health data (sensitive), DPDP duties, government procurement through', text2='MeitY-empanelled providers, data in India, CERT-In logging.', svc='Rules remove options before features add them'),
      dict(on=['req', 'rule', 'skill'], hot='skill', move=(97, 50, 97, 104, 'skills'), head='Step 3 · Skills and budget', text='A five-person IT cell, an annual budget (opex acceptable through the tender), no', text2='data centre staff — managed services strongly preferred.', svc='Small teams → PaaS/SaaS, not self-run IaaS'),
      dict(on=['rule', 'skill', 'dep'], hot='dep', move=(128, 127, 150, 90, 'model'), head='Step 4 · Deployment model', text='Government community cloud from an empanelled provider (Lesson 3.1), India', text2='Regions only; no hybrid needed (no on-prem systems to keep).', svc='Community / government cloud'),
      dict(on=['dep', 'svc', 'prov'], hot='prov', move=(202, 66, 226, 30, 'choose'), head='Step 5 · Service model and provider', text='Managed PostgreSQL + container PaaS + offline-capable mobile app; provider chosen', text2='among empanelled offerings by service fit and price.', svc='PaaS per workload; SaaS for email and collaboration'),
      dict(on=list(RN), hot='gov', move=(278, 127, 298, 90, 'govern'), head='Step 6 · Governance from day one', text='India-only policy, MFA for all officers, audit logs 180 days, budgets per district,', text2='erasure process for beneficiaries. Document the decision (ADR).', svc='Guard-rails turn the decision into daily practice')]
DEC = flow_anim('Deciding for one organisation, step by step', 'A state health department’s nutrition app — from needs to governance.', 'Scenario decision', 'Animation: understand needs; apply rules; check skills and budget; choose deployment model; choose service model and provider; set governance.', RN, RS, hid='scenflow')

def mapfig():
    o = t(320, 16, 'Seven organisation types', 11, 'ink', bold=True)
    items = [('1', 'Start-up', 'speed, credits, serverless', 'green'), ('2', 'Small business (SME)', 'SaaS first, simple', 'blue'), ('3', 'Large enterprise', 'hybrid, landing zones', 'violet'), ('4', 'Bank / fintech', 'RBI, residency, resilience', 'amber'),
             ('5', 'Government / PSU', 'empanelment, sovereignty', 'red'), ('6', 'Hospital / health', 'privacy, uptime, edge', 'red'), ('7', 'College / research', 'labs, HPC bursts, credits', 'card')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 8, 'ink', bold=True) + t(x + 78, y + 54, b, 6.4, 'ink2')
    o += t(320, 210, 'Each type has typical answers — use them as starting points, not rules.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of seven organisation types: start-up, small business, large enterprise, bank or fintech, government or PSU, hospital or health, college or research.', mapfig(), h=222)

A1 = mk(['Idea → MVP', 'Grow fast', 'Optimise later'], ['MVP|serverless, PaaS|managed DB', 'grow|auto scaling|credits run out', 'optimise|commitments|right-size'], ['green', 'amber', 'blue'],
        ['launch quickly with fully managed services and free credits', 'scale automatically with demand; watch the burn rate', 'once usage is steady, commit for discounts and right-size'],
        [('MVP', 'Serverless, PaaS, managed DB; startup credits.', ''), ('Grow', 'Auto scaling; cost alerts as credits end.', ''), ('Optimise', 'Commitment discounts, right-sizing.', '')],
        'Start-up in action', 'Speed first, bills second.', 'Start-up', 'Animation: idea to MVP; fast growth; later optimisation.', 'o1anim')
T1 = vt(1, 'Start-up', 'green',
    'A <b>start-up</b> typically chooses a single <b>public cloud</b> with <b>serverless and PaaS</b> services to ship quickly with a tiny team, uses startup credit programmes, avoids upfront spending, and optimises costs and architecture once product–market fit is clear.',
    'A food truck: rent the vehicle, cook simple dishes fast, move to a restaurant only when the crowds are reliable.',
    'TiffinGo’s first year: API Gateway + Lambda + DynamoDB + S3 on AWS credits; three engineers, no servers to patch.',
    'AWS Activate, Microsoft for Startups (Founders Hub), Google for Startups Cloud Program credits; serverless and managed databases on any major cloud.', '', A1,
    'small teams, uncertain demand, need for speed.',
    'you over-engineer multi-cloud or Kubernetes before having customers.',
    'New small companies: use ready-made cloud services to launch fast and pay only as they grow.',
    [('Credits', 'Apply to startup programmes.'), ('Managed first', 'Serverless/PaaS/SaaS.'), ('Guard-rails', 'Budgets, MFA, no root keys.'), ('Measure', 'Unit cost per order.'), ('Optimise', 'When usage is steady.')],
    [('MVP', 'minimum viable product'), ('burn rate', 'money spent per month'), ('product–market fit', 'customers clearly want the product')],
    table(['', 'Start-up', 'Enterprise'], [['Main constraint', 'speed and cash', 'risk and integration'], ['Model', 'public, managed', 'hybrid, governed'], ['Team', 'few generalists', 'many specialists']], minw=420),
    ['Consumer apps', 'SaaS products', 'AI start-ups'],
    'Most large cloud-native companies began on one public cloud with managed services and only later added multi-cloud or private infrastructure for specific reasons.',
    'Track cost per order (unit economics) from month one — it tells you when an architecture change is worth it.')

A2 = mk(['Buy SaaS', 'A little PaaS', 'Simple security'], ['SaaS|email, accounts|billing, CRM', 'PaaS|website, small DB|no servers', 'secure|MFA, backups|one admin'], ['blue', 'green', 'amber'],
        ['most needs are met by SaaS products', 'a website or small app runs on PaaS', 'focus on MFA, backups and a trusted partner'],
        [('SaaS', 'Email, accounting, CRM, inventory as SaaS.', ''), ('PaaS', 'Website/app on a managed platform.', ''), ('Basics', 'MFA, backups, a managed-services partner.', '')],
        'Small business in action', 'Buy, don’t build.', 'SME', 'Animation: buy SaaS; a little PaaS; simple security.', 'o2anim')
T2 = vt(2, 'Small and medium business (SME)', 'blue',
    'A <b>small or medium business</b> usually gets most value from <b>SaaS</b> (email, accounting, CRM, inventory) and simple <b>PaaS</b> hosting, avoids running servers, relies on a managed-service partner for setup, and focuses security effort on identity (MFA), backups and device protection.',
    'A neighbourhood restaurant: buys gas, POS and delivery apps as services; the owner focuses on food, not on building tools.',
    'A TiffinGo franchise partner with 12 staff uses Google Workspace, Zoho Books and a website on a managed platform — no cloud engineer needed.',
    'Microsoft 365 / Google Workspace, Zoho, Tally on cloud, Shopify; App Service, Cloud Run, Lightsail; managed-service providers.', 'SaaS types are in Lesson 2.3.', A2,
    'standard business functions and no IT team.',
    'you build custom systems that SaaS already provides.',
    'Small businesses: use online software for most things and avoid running their own servers.',
    [('Identify', 'Business functions.'), ('SaaS', 'Choose products (2.3 checklist).'), ('Identity', 'One login with MFA.'), ('Backup', 'Export/backup SaaS data.'), ('Partner', 'Local MSP for support.')],
    [('MSP', 'managed service provider'), ('SME', 'small and medium enterprise'), ('Lightsail', 'AWS’s simplified VPS service')],
    table(['', 'SME', 'Start-up'], [['Builds software?', 'rarely', 'yes (product)'], ['Main model', 'SaaS', 'serverless/PaaS'], ['Cloud skills', 'partner', 'in-house']], minw=420),
    ['Shops and restaurants', 'Clinics', 'Professional services'],
    'For many SMEs the “cloud migration” is moving email and files to Microsoft 365 or Google Workspace — a repurchase (Lesson 2.5).',
    'The biggest SME risk is identity: one phished owner account. MFA and a second admin solve most of it.')

A3 = mk(['Landing zone', 'Migrate in waves', 'Hybrid for years'], ['landing zone|accounts, policies|network hub', 'waves|7 Rs|business cases', 'hybrid|DC + cloud|one governance'], ['violet', 'amber', 'blue'],
        ['build a governed foundation: hierarchy, identity, network, guard-rails', 'migrate application portfolios in waves using the 7 Rs', 'run hybrid for years with common governance and FinOps'],
        [('Foundation', 'Landing zone with hierarchy, identity, network, policies.', ''), ('Waves', 'Migrate portfolios with the 7 Rs.', ''), ('Hybrid', 'Years of hybrid with shared governance.', '')],
        'Enterprise in action', 'Governance before workloads.', 'Enterprise', 'Animation: landing zone; migration waves; hybrid operations.', 'o3anim')
T3 = vt(3, 'Large enterprise', 'violet',
    'A <b>large enterprise</b> usually adopts <b>hybrid and often multi-cloud</b> operations: it builds a governed <b>landing zone</b> (account/subscription/project hierarchy, identity federation, network hub, guard-rails, logging), migrates application portfolios in waves using the 7 Rs, keeps some systems on-premises for years, and runs a cloud centre of excellence and FinOps practice.',
    'Moving a big joint family into a new apartment complex: first agree on rules, keys and electricity meters, then move one family at a time.',
    'A TiffinGo corporate client with 400 applications set up AWS Control Tower and Azure landing zones, then moved 60 apps in the first year while SAP stayed on-premises.',
    'AWS Control Tower and Landing Zone Accelerator, Azure landing zones (Cloud Adoption Framework), Google Cloud Foundation / landing zone blueprints; migration hubs and centres of excellence.', 'Migration strategies are in Lesson 2.5; multi-cloud in 3.3.', A3,
    'many applications, many teams and existing data centres.',
    'teams start deploying before the foundation exists — sprawl is hard to fix later.',
    'Big companies: build strong cloud rules first, then move applications step by step, keeping some on-premises.',
    [('Strategy', 'Business case, CoE.'), ('Landing zone', 'Hierarchy, identity, network, logs.'), ('Portfolio', 'Assess, 7 Rs, waves.'), ('Operate', 'FinOps, security, SRE.'), ('Modernise', 'Replatform/refactor over time.')],
    [('landing zone', 'pre-built, governed cloud environment'), ('CoE', 'cloud centre of excellence'), ('FinOps', 'financial operations for cloud costs')],
    table(['', 'Enterprise', 'SME'], [['Accounts/subscriptions', 'hundreds', 'one or two'], ['Governance', 'policy as code', 'simple settings'], ['Timeline', 'years', 'weeks']], minw=420),
    ['Manufacturing', 'Retail chains', 'IT services'],
    'All three providers publish landing-zone frameworks because most failed enterprise migrations trace back to missing governance, not missing services.',
    'Treat the landing zone as a product with an owner and a backlog — it evolves as the organisation learns.')

A4 = mk(['RBI rules', 'Resilient design', 'Exit + audit'], ['rules|outsourcing, IT|payment data in India', 'resilience|multi-AZ / DR|tested', 'audit|exit plan|regulator access'], ['amber', 'blue', 'red'],
        ['RBI directions shape what can move and how it is contracted', 'critical systems need high availability and tested DR', 'contracts must allow audits and a credible exit strategy'],
        [('Rules', 'RBI outsourcing/IT governance; payment data in India.', ''), ('Resilience', 'Multi-AZ, DR, tested recovery.', ''), ('Audit + exit', 'Regulator access, exit plans, vendor risk.', '')],
        'Bank / fintech in action', 'Compliance and resilience first.', 'Bank', 'Animation: RBI rules; resilient design; exit and audit.', 'o4anim')
T4 = vt(4, 'Bank, insurer or fintech', 'amber',
    'A <b>regulated financial institution</b> in India typically uses <b>public cloud in Indian Regions</b> (often hybrid with core systems on-premises or in a private cloud), driven by RBI directions on IT governance, outsourcing and payment-data localisation, with strong encryption and key control, multi-AZ and DR designs, audit rights in contracts and a documented exit strategy.',
    'A jewellery shop using a bank vault: fine to store gold there, but with insured contracts, inspection rights and a plan to move it if needed.',
    'A cooperative bank asks TiffinGo to integrate canteen payments: the bank’s core stays on its private cloud; TiffinGo’s payment component runs in Mumbai with CMK encryption, 180-day logs and a DR copy in Hyderabad.',
    'India Regions of AWS, Azure, Google; Oracle/IBM for legacy cores; community clouds for co-operative banks offered by some providers; HSM-backed key management.', 'Compliance details are in Lesson 9.3.', A4,
    'regulated workloads — after a risk assessment and board-approved policy.',
    'you sign contracts without audit and exit clauses — regulators will ask.',
    'Banks and payment companies: follow RBI rules, keep payment data in India, and design for no downtime.',
    [('Classify', 'Critical vs non-critical.'), ('Approve', 'Board/IT strategy committee.'), ('Design', 'India Regions, DR, CMKs.'), ('Contract', 'Audit rights, exit.'), ('Report', 'Incidents to CERT-In/RBI.')],
    [('outsourcing', 'using a third party for a service'), ('exit strategy', 'plan to move away from a provider'), ('core banking', 'main account and transaction system')],
    table(['', 'Bank', 'Start-up'], [['First question', 'is it allowed and how?', 'how fast?'], ['DR', 'tested, documented', 'often later'], ['Keys', 'CMK/HSM', 'provider defaults']], minw=420),
    ['Digital channels', 'Analytics', 'Payment gateways'],
    'Indian banks increasingly run mobile banking, analytics and customer-facing systems on public cloud while keeping core banking on dedicated infrastructure — a hybrid pattern regulators accept with proper controls.',
    'Regulators care most about concentration and exit risk: show how you would move or recover if the provider failed.')

A5 = mk(['Procurement rules', 'Empanelled cloud', 'Citizen scale'], ['procure|GeM, tenders|empanelment', 'cloud|MeitY-empanelled|India only', 'scale|millions of citizens|peaks on deadlines'], ['red', 'blue', 'green'],
        ['buying follows government procurement and empanelment', 'workloads run on MeitY-empanelled offerings in India', 'citizen services must handle huge peaks around deadlines'],
        [('Procure', 'GeM/tenders with MeitY empanelment.', ''), ('Host', 'Empanelled cloud services in India.', ''), ('Scale', 'Citizen-scale peaks and accessibility.', '')],
        'Government in action', 'Rules, residency, scale.', 'Government', 'Animation: procurement rules; empanelled cloud; citizen scale.', 'o5anim')
T5 = vt(5, 'Government or public-sector undertaking', 'red',
    'A <b>government department or PSU</b> typically uses <b>community/government cloud</b> offerings from MeitY-empanelled providers (MeghRaj), procured through tenders or GeM, with data hosted in India, strong security audits (often STQC/CERT-In-empanelled auditors) and architectures that handle citizen-scale peaks around deadlines.',
    'A city’s water board: everyone depends on it, rules are strict, demand peaks every morning, and any outage is front-page news.',
    'The state nutrition app (animation above) runs on an empanelled offering in India with managed PostgreSQL and containers, MFA for officers and 180-day logs.',
    'MeitY-empanelled offerings of AWS, Azure, Google, Oracle and Indian providers; National Informatics Centre (NIC) cloud; GeM marketplace.', 'Community clouds are in Lesson 3.1.', A5,
    'citizen services, departmental systems, data platforms for schemes.',
    'you choose non-empanelled services for government data.',
    'Government offices: buy approved cloud services through official channels and keep data in India.',
    [('Policy', 'Check cloud policy and empanelment.'), ('Procure', 'Tender/GeM.'), ('Secure', 'Audit, MFA, logging.'), ('Scale', 'Load test for deadlines.'), ('Operate', 'SLAs, helpdesk.')],
    [('GeM', 'Government e-Marketplace for procurement'), ('NIC', 'National Informatics Centre'), ('STQC', 'government testing and quality certification body')],
    table(['', 'Government', 'Enterprise'], [['Buying', 'tenders, GeM', 'contracts'], ['Provider list', 'empanelled only', 'any'], ['Peak pattern', 'deadline surges', 'business cycles']], minw=420),
    ['Citizen portals', 'Scheme databases', 'Smart city platforms'],
    'Large citizen platforms in India (tax filing, vaccination, exam results) have shown how deadline-driven traffic peaks need elastic, load-tested cloud designs.',
    'Load-test for the last day before a deadline — that is your real peak, often 10–50× an average day.')

A6 = mk(['Patient data', 'Always on', 'Devices at the edge'], ['data|health records|DPDP + sector', 'uptime|24×7 care|DR, offline', 'edge|monitors, imaging|local processing'], ['red', 'amber', 'green'],
        ['health data is highly sensitive and regulated', 'clinical systems need very high availability and offline fallbacks', 'medical devices and imaging need local processing'],
        [('Data', 'Sensitive health data under privacy rules.', ''), ('Uptime', '24×7 care; DR and offline modes.', ''), ('Edge', 'Devices and imaging processed locally.', '')],
        'Hospital in action', 'Privacy, uptime, edge.', 'Hospital', 'Animation: patient data; always on; devices at the edge.', 'o6anim')
T6 = vt(6, 'Hospital or health organisation', 'red',
    'A <b>hospital or health organisation</b> commonly runs <b>hybrid</b>: clinical systems and devices on-premises or at the edge for uptime and latency, with cloud used for patient apps, analytics, imaging archives, DR and AI; it applies strong privacy controls (DPDP, health-sector standards such as ABDM guidelines; HIPAA for US data), encryption, access logging and tested offline procedures.',
    'An ambulance service: lifesaving equipment must work in the van even with no network, while records sync to the central system later.',
    'The hospital chain from Module 3 keeps its EHR on its private cloud, uses AWS for the diet-planner integration, and archives imaging to cold storage with CMKs.',
    'Healthcare-focused services (AWS HealthLake, Azure Health Data Services, Google Cloud Healthcare API), edge platforms (Azure Local, Outposts), DR services, ABDM-integrated apps in India.', 'Hybrid patterns are in Lesson 3.3.', A6,
    'patient-facing apps, analytics, archives and DR — with clinical systems carefully planned.',
    'clinical systems depend on a single internet link with no offline mode.',
    'Hospitals: keep critical medical systems close and always running, and use the cloud for apps, analysis and backup — with strict privacy.',
    [('Classify', 'Clinical vs non-clinical.'), ('Edge', 'Local for devices/critical.'), ('Cloud', 'Apps, archive, analytics, DR.'), ('Privacy', 'Consent, access logs, encryption.'), ('Drills', 'Downtime procedures.')],
    [('EHR', 'electronic health record'), ('PACS', 'medical imaging archive system'), ('ABDM', 'Ayushman Bharat Digital Mission')],
    table(['', 'Hospital', 'Bank'], [['Main risk', 'patient safety, privacy', 'financial loss, regulation'], ['Edge needs', 'high (devices)', 'low'], ['Offline mode', 'essential', 'branch fallback']], minw=420),
    ['Hospitals', 'Diagnostic chains', 'Telemedicine'],
    'Imaging archives are a common first hospital cloud workload: huge, rarely read files fit cold storage tiers and cut on-premises storage costs.',
    'Practise “cloud down” days: if staff cannot work for an hour without the cloud app, the design is not ready for clinical use.')

A7 = mk(['Student labs', 'Research bursts', 'Tight budgets'], ['labs|sandbox accounts|credits', 'research|HPC, GPUs|on demand', 'budget|grants, policies|auto shut-down'], ['card', 'blue', 'green'],
        ['students get isolated sandbox accounts with education credits', 'researchers burst to HPC and GPU capacity for deadlines', 'budgets, auto-shutdown and policies prevent surprise bills'],
        [('Labs', 'Sandbox accounts per class with credits.', ''), ('Research', 'Burst HPC/GPU for experiments.', ''), ('Budget', 'Policies, auto-shutdown, grants.', '')],
        'College in action', 'Learn, experiment, stay in budget.', 'College', 'Animation: student labs; research bursts; tight budgets.', 'o7anim')
T7 = vt(7, 'College, university or research institute', 'card',
    'A <b>college or research institute</b> typically combines <b>public cloud sandboxes</b> for teaching (education programmes, credits, auto-expiring accounts), <b>cloud bursting</b> from on-campus HPC clusters to cloud GPUs/CPUs for research deadlines, SaaS for email and learning platforms, and strict budget guard-rails because grants and fees are fixed.',
    'A college lab with a booking sheet: students get time on equipment, big experiments book extra machines, and the lab manager watches the budget.',
    'An engineering college running the C-DAC-style Big Data course gives each student a sandbox project with a ₹1,000 budget alert; final-year AI projects burst to cloud GPUs for two weeks.',
    'AWS Academy and AWS Educate-style programmes, Azure for Students / Azure Dev Tools for Teaching, Google Cloud education credits; research credit programmes; national HPC (e.g. National Supercomputing Mission) plus cloud.', 'Cloud bursting is in Lesson 3.3.', A7,
    'teaching labs and variable research workloads.',
    'student accounts have no budgets or shutdown — one forgotten GPU VM eats the semester’s credits.',
    'Colleges: give students safe cloud practice accounts and let researchers rent big computers only when needed — within budget.',
    [('Sandboxes', 'Per student/class.'), ('Guard-rails', 'Allowed services, Regions, sizes.'), ('Budgets', 'Alerts + auto-stop.'), ('Burst', 'HPC/GPU for research.'), ('Clean-up', 'End-of-semester deletion.')],
    [('sandbox', 'isolated practice environment'), ('education credits', 'free cloud usage for learning'), ('HPC', 'high-performance computing')],
    table(['', 'College', 'Start-up'], [['Money', 'fixed budgets, grants', 'investor cash, credits'], ['Users', 'many short-term students', 'small team'], ['Key control', 'budgets + auto clean-up', 'speed + cost alerts']], minw=420),
    ['Engineering colleges', 'Research labs', 'Training institutes'],
    'Training institutes often use organisation-level guard-rails (allowed instance types, Regions) so students can experiment freely without risking large bills.',
    'Automate clean-up: tag every lab resource with course and expiry date, and delete anything past expiry nightly.')

SUMMARY = table(['#', 'Organisation', 'Typical deployment', 'Typical service models', 'First concern'], [
    ['1', 'Start-up', 'single public cloud', 'serverless, PaaS, SaaS', 'speed, cash'], ['2', 'SME', 'public (SaaS)', 'SaaS, simple PaaS', 'simplicity, identity'], ['3', 'Enterprise', 'hybrid, often multi-cloud', 'all, per workload', 'governance'],
    ['4', 'Bank / fintech', 'public India Regions + private/hybrid', 'PaaS, IaaS, SaaS', 'RBI compliance, resilience'], ['5', 'Government', 'community / government cloud', 'PaaS, SaaS', 'empanelment, residency'], ['6', 'Hospital', 'hybrid + edge', 'SaaS, PaaS, edge', 'privacy, uptime'], ['7', 'College', 'public sandboxes + HPC bursting', 'SaaS, IaaS for labs', 'budget, clean-up']], minw=660)
CHECK = ('  <h3>Check yourself: which fits?</h3>\n' +
    qx('A. Three founders, no servers, need to launch in 6 weeks.', ['public cloud, serverless + managed DB', 'private OpenStack', 'mainframe', 'community cloud'], 0, 'Start-up.') +
    qx('B. A state department building a scheme portal.', ['MeitY-empanelled cloud in India', 'any foreign SaaS', 'personal accounts', 'on-prem only'], 0, 'Government.') +
    qx('C. A hospital’s ICU monitors must work during internet outages.', ['edge/on-prem processing with cloud sync', 'cloud-only', 'SaaS only', 'nothing'], 0, 'Hospital edge.') +
    qx('D. 120 students need practice accounts this semester.', ['sandboxes with budgets and auto clean-up', 'one shared root login', 'unlimited accounts', 'no cloud'], 0, 'College.'))

TYPES = ('  <p>Seven organisation types, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['Which question usually decides the model first for banks and government?', 'Why do hospitals need offline modes?', 'What one control saves most student-lab budgets?'], 'types 4–5, 6 and 7') + MAP
         + jump(['Start-up', 'SME', 'Enterprise', 'Bank', 'Government', 'Hospital', 'College']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('Requirements matrix', 'Scored list of needs per option.', 'Makes trade-offs visible.', 'Services, rules, skills, cost.'),
    ('Architecture decision record (ADR)', 'One page: context, decision, consequences.', 'Explains choices later.', 'Stored in Git.'),
    ('Landing zone', 'Governed starting environment.', 'Safe scaling.', 'Control Tower, Azure landing zones, Google foundation.'),
    ('Cost allocation', 'Tags/labels per department.', 'Showback and budgets.', 'cost-centre tags.'),
    ('Well-Architected review', 'Structured design check.', 'Find risks early.', 'WA Tool, Azure WA review, Google framework.'),
    ('Exit plan', 'How to move or recover.', 'Regulators and risk.', 'Data export, IaC, contracts.')])

DEEP = ('  <h3>Interview case-study template</h3>\n  <ol><li><b>Clarify</b>: users, data, rules, skills, budget, existing systems, growth (the seven questions).</li><li><b>Constraints first</b>: anything legally required (residency, empanelment, RBI).</li><li><b>Deployment model</b> with one reason.</li><li><b>Service model per workload</b> (SaaS → serverless → PaaS → IaaS).</li><li><b>Provider</b> by fit and skills; mention alternatives.</li><li><b>Governance</b>: identity, guard-rails, logging, budgets, DR.</li><li><b>Risks and next steps</b>: what you would test in a proof of concept.</li></ol>\n'
    '  <h3>Typical mistakes by organisation type</h3>\n' + table(['Type', 'Typical mistake'], [['Start-up', 'premature multi-cloud/Kubernetes'], ['SME', 'no MFA, no SaaS backups'], ['Enterprise', 'workloads before landing zone'], ['Bank', 'contracts without audit/exit clauses'], ['Government', 'non-empanelled services, no peak load test'], ['Hospital', 'cloud-only clinical systems'], ['College', 'no budgets or clean-up']], minw=420))

clouds = vendor_tabs('<p><b>AWS:</b> Activate (start-ups), Control Tower + Landing Zone Accelerator (enterprises, regulated), AWS Academy (education), Well-Architected Tool and lenses (e.g. Financial Services, Government, Healthcare).</p>',
    '<p><b>Azure:</b> Microsoft for Startups, Cloud Adoption Framework and landing zones, Azure for Students / Dev Tools for Teaching, Well-Architected Review and Advisor score, industry clouds (Financial Services, Healthcare, Sovereignty).</p>',
    '<p><b>Google Cloud:</b> Google for Startups Cloud Program, Cloud Foundation / landing zones, education credits, Architecture Framework, Assured Workloads for regulated industries.</p>') + \
    cloud3([['Start-up programme', 'Activate', 'Microsoft for Startups', 'Google for Startups'], ['Landing zone', 'Control Tower / LZA', 'Azure landing zones', 'Cloud Foundation'], ['Design review', 'Well-Architected Tool', 'WA Review + Advisor', 'Architecture Framework'], ['Education', 'AWS Academy', 'Azure for Students', 'education credits']])

MOCKQ.extend([
 (mock('aws', ['Well-Architected Tool', 'Define workload'], ['Workloads', 'Lenses', 'Profiles'], 'Workloads', [('Name', 'state-nutrition-app'), ('Environment', '[x] Production'), ('Regions', 'ap-south-1'), ('Lenses', 'Well-Architected Framework')], 'Next'),
  mock('az', ['Advisor', 'Advisor score'], ['Overview', 'Advisor score', 'Recommendations'], 'Advisor score', [('Overall', 'e.g. 78%'), ('Categories', 'Cost · Security · Reliability · Operational excellence · Performance')], 'Download'),
  mock('gcp', ['Recommendations', 'Overview'], ['Overview', 'Cost', 'Security', 'Reliability'], 'Overview', [('Categories', 'Cost · Security · Performance · Reliability · Manageability · Sustainability'), ('Source', 'Active Assist')], 'View all')),
 (mock('aws', ['Billing', 'Cost allocation tags'], ['Bills', 'Cost allocation tags'], 'Cost allocation tags', [('User-defined', 'department'), ('Status', 'Active')], 'Activate'),
  mock('az', ['Policy', 'Assign policy'], ['Definitions', 'Assignments'], 'Assignments', [('Definition', 'Inherit a tag from the resource group if missing'), ('Tag name', 'department')], 'Review + create'),
  mock('gcp', ['Manage resources', 'Labels'], ['Projects', 'Labels', 'Tags'], 'Labels', [('department', 'district-pune'), ('env', 'prod')], 'Save')),
 (mock('aws', ['Regional services', 'Asia Pacific (Mumbai)'], ['Regions', 'Services'], 'Services', [('Service', 'Amazon Bedrock · Amazon EKS · AWS Lambda'), ('Availability', 'listed for ap-south-1?')], 'Search'),
  mock('az', ['Products available by region'], ['Products', 'Regions'], 'Products', [('Region', 'Central India'), ('Product', 'Container Apps · Azure Database for PostgreSQL')], 'Filter'),
  mock('gcp', ['Cloud locations', 'Products'], ['Regions', 'Products'], 'Products', [('Region', 'asia-south1 (Mumbai)'), ('Product', 'Cloud Run · Cloud SQL · Vertex AI')], 'Filter')),
])

STEP1 = ('1 · Run a structured design review for a scenario', tri(
    (['[[AWS Well-Architected Tool]] → [[Define workload]]: name <code>state-nutrition-app</code>, production, Region ap-south-1, lens Well-Architected Framework → [[Start reviewing]] → answer a few questions per pillar.'],
     "WL=$(aws wellarchitected create-workload --workload-name state-nutrition-app --description 'Scenario review' --environment PRODUCTION \\\n  --lenses wellarchitected --aws-regions ap-south-1 --review-owner you@example.com --client-request-token $RANDOM --query WorkloadId --output text)\naws wellarchitected list-answers --workload-id $WL --lens-alias wellarchitected --pillar-id security --max-results 5 --query 'AnswerSummaries[].[QuestionId,QuestionTitle]' --output table",
     'a workload ID and the first security questions (e.g. “How do you securely operate your workload?”). The tool is free.'),
    (['[[Advisor]] → [[Advisor score]] shows scores per Well-Architected pillar; the Azure Well-Architected Review assessment (Microsoft Learn) gives a full questionnaire.'],
     'SUB=$(az account show --query id -o tsv)\naz rest --method get --url "https://management.azure.com/subscriptions/$SUB/providers/Microsoft.Advisor/advisorScore?api-version=2023-01-01" \\\n  --query "value[].{category:name,score:properties.lastRefreshedScore.score}" -o table',
     'scores per category (Cost, Security, Reliability, OperationalExcellence, Performance, Advisor) — empty or low on a new subscription with no resources.'),
    (['[[Recommendations]] (Active Assist) groups findings by Architecture Framework pillars; use the framework’s checklists for the scenario review.'],
     'P=$(gcloud config get-value project)\nfor r in google.iam.policy.Recommender google.compute.instance.IdleResourceRecommender; do echo \"== $r\"; gcloud recommender recommendations list --project=$P --location=global --recommender=$r --format="value(description)" 2>/dev/null | head -3; done',
     'recommendation descriptions per recommender (possibly none on a quiet project).')),
    'Reviews turn “it depends” into a checklist — use them for every scenario answer.')

STEP2 = ('2 · Allocate costs by department (showback for any organisation)', tri(
    (['Tag resources with <code>department</code>. [[Billing and Cost Management]] → [[Cost allocation tags]] → activate <code>department</code> → Cost Explorer can group by it.'],
     "B=tg-dept-$RANDOM; aws s3 mb s3://$B --region ap-south-1\naws s3api put-bucket-tagging --bucket $B --tagging 'TagSet=[{Key=department,Value=district-pune}]'\naws ce update-cost-allocation-tags-status --cost-allocation-tags-status TagKey=department,Status=Active 2>&1 | tail -2\naws ce list-cost-allocation-tags --tag-keys department --query 'CostAllocationTags[].[TagKey,Status]' --output text",
     '<code>department Active</code> once AWS has seen the tag in billing data (new tags can take up to 24 hours to appear; activation may fail until then — retry tomorrow).'),
    (['[[Policy]] → [[Assign policy]] → “Inherit a tag from the resource group if missing” → tag name <code>department</code> → system-assigned identity → [[Create]]. Tag the resource group.'],
     "az group create -n rg-dept -l centralindia --tags department=district-pune\naz policy assignment create -n inherit-dept -g rg-dept --policy ea3f2387-9b95-492a-a190-fcdc54f7b070 \\\n  --params '{\"tagName\":{\"value\":\"department\"}}' --mi-system-assigned --location centralindia\naz storage account create -n tgdept$RANDOM -g rg-dept -l centralindia --sku Standard_LRS --query tags",
     'the new storage account automatically gets <code>{\"department\": \"district-pune\"}</code> (policy effects can take a few minutes to start).'),
    (['[[Manage resources]] → select project → [[Labels]] → add <code>department=district-pune</code>. Labels flow into billing exports and reports.'],
     'P=$(gcloud config get-value project)\ngcloud projects update $P --update-labels=department=district-pune\ngcloud projects describe $P --format="value(labels)"',
     '<code>department=district-pune</code>.')),
    'Every organisation type needs to know who spends what — tags/labels are the cheapest control.')

STEP3 = ('3 · Check that the scenario’s services exist in India Regions', tri(
    (['Open the AWS “Regional services” list → filter Asia Pacific (Mumbai) and (Hyderabad) → check each needed service.'],
     "for s in lambda eks bedrock healthlake; do printf '%-12s ' $s; aws ssm get-parameters-by-path --path /aws/service/global-infrastructure/services/$s/regions --region us-east-1 \\\n  --query \"Parameters[?Value=='ap-south-1' || Value=='ap-south-2'].Value\" --output text; echo; done",
     'each service followed by the India Regions where it is available (blank = not in India yet — a design constraint).'),
    (['Open “Products available by region” → choose Central India → search the products the scenario needs.'],
     'for p in Microsoft.App:containerApps Microsoft.DBforPostgreSQL:flexibleServers Microsoft.HealthcareApis:workspaces; do ns=${p%%:*}; rt=${p##*:}\n  printf "%-45s " $p; az provider show -n $ns --query "resourceTypes[?resourceType==\'$rt\'].locations[] | [?contains(@,\'India\')]" -o tsv | tr \'\\n\' \' \'; echo; done',
     'each resource type with the India Regions that support it.'),
    (['Open the Google Cloud “Cloud locations” page → filter asia-south1 / asia-south2 → check products.'],
     'gcloud run regions list --format="value(locationId)" | grep asia-south\ngcloud ai models list --region=asia-south1 --limit=1 2>&1 | tail -1',
     '<code>asia-south1</code>/<code>asia-south2</code> for Cloud Run, and whether Vertex AI responds in Mumbai (an error naming an unsupported location means “not available here”).')),
    'Residency rules are useless if the service you need does not exist in that Region — check early.')

prac = practical(OWN_INTRO + ' You run a structured design review, set up department cost allocation and check Regional service availability — the three checks every scenario answer needs. All free.', [SETUP_STEP, STEP1, STEP2, STEP3],
    cleanup='<b>AWS:</b> <code>aws wellarchitected delete-workload --workload-id $WL --client-request-token $RANDOM</code>; <code>aws s3 rb s3://$B --force</code>. '
            '<b>Azure:</b> <code>az policy assignment delete -n inherit-dept -g rg-dept</code>; <code>az group delete -n rg-dept --yes --no-wait</code>. '
            '<b>Google Cloud:</b> <code>gcloud projects update $P --remove-labels=department</code>.')

mist = mistakes([
    ['One answer for every organisation.', 'Personal favourite.', 'Use the seven questions.'],
    ['Features before rules.', 'Excitement about services.', 'Regulations and residency first.'],
    ['Ignoring team skills.', 'Architecture diagrams look easy.', 'Match model to who will run it.'],
    ['No exit plan for regulated bodies.', 'Optimism.', 'Document export, IaC and contracts.'],
    ['Assuming every service exists in India.', 'Global docs.', 'Check Regional availability (step 3).'],
    ['No cost allocation.', 'Small at first.', 'Tags/labels from day one.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Organisational scenarios and choosing the right cloud model.'], ['AWS CLF-C02', 'Cloud value proposition, migration, Well-Architected, cost allocation tags.'], ['AZ-900', 'Cloud models and use cases, Cloud Adoption Framework, tags and Azure Policy.'], ['Google Cloud Digital Leader', 'Digital transformation scenarios, choosing models, cost governance.']], minw=560) + \
    qx('1. A start-up with three engineers should usually prefer…', ['self-managed Kubernetes on VMs', 'managed serverless and PaaS', 'a private data centre', 'mainframes'], 1, 'Speed.') + \
    qx('2. Which AWS tool reviews workloads against best practices?', ['Well-Architected Tool', 'Artifact', 'Snowball', 'Macie'], 0, 'WA Tool.') + \
    qx('3. Azure policy that copies a resource-group tag to resources is an example of…', ['governance automation', 'DDoS protection', 'caching', 'replication'], 0, 'Policy.') + \
    qx('4. Indian government workloads typically use…', ['MeitY-empanelled cloud offerings', 'any personal account', 'unapproved SaaS', 'only on-prem'], 0, 'Empanelment.') + \
    qx('5. Why do hospitals often choose hybrid?', ['devices and critical systems need local operation', 'cloud is illegal', 'it is cheapest', 'SaaS doesn’t exist'], 0, 'Uptime + devices.') + \
    qx('6. A landing zone is…', ['a pre-configured, governed cloud environment', 'a CDN location', 'a VM size', 'a backup'], 0, 'Foundation.')

proj = miniproject('Mini project: four scenario briefs',
    'Answer the four customers from the story with a one-page brief each.',
    ['<b>Seven questions:</b> answer them for the start-up, co-op bank, state health department and college.',
     '<b>Decide:</b> deployment model, service models per workload, provider(s) — one reason each.',
     '<b>Governance:</b> three guard-rails per scenario.',
     '<b>Availability:</b> check required services in India Regions (step 3).',
     '<b>Cost:</b> one budget and allocation approach per scenario (step 2).',
     '<b>ADR:</b> write an architecture decision record for the hardest choice.'],
    'Four one-page briefs plus one ADR.', 'Modules 2, 3, 9 and 10.')

assemble_v2(HERE, story_h2='Four customers, one question', hook_html=hk,
    narration='In a single week TiffinGo’s consulting arm was asked the same question by a start-up, a cooperative bank, a state health department and an engineering college: which cloud model should we use?',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Organisational scenarios: which cloud model fits',
    formal='<b>Choosing a cloud model for an organisation</b> means analysing its users, data sensitivity, regulatory obligations, skills, budget structure, existing systems and growth, and from that selecting the deployment model (public, private, hybrid, community, multi-cloud, sovereign), the service model per workload (IaaS, PaaS, SaaS, serverless), the provider(s), and the governance needed to operate safely.',
    simple='Different organisations need different cloud setups; ask about their users, data, rules, skills and money first, then choose.',
    interview=['“I start with constraints — data sensitivity and regulations — then skills and budget. A start-up gets public cloud and serverless; a bank gets India Regions, hybrid with core on-prem, CMKs and tested DR; government uses MeitY-empanelled offerings.”', '“Then I choose service models per workload, pick providers by fit and skills, and define governance: identity, guard-rails, logging, budgets and an exit plan.”'],
    terms_rows=[('Seven questions', 'Users, data, rules, skills, budget, existing, growth.'), ('Landing zone', 'Governed foundation.'), ('ADR', 'Architecture decision record.'), ('Showback', 'Report cost by department.'), ('Empanelment', 'Government approval.'), ('Exit plan', 'How to leave a provider.'), ('CoE', 'Cloud centre of excellence.'), ('Sandbox', 'Isolated practice account.')],
    exam='Scenario questions: “Which model fits this organisation?” Answer from constraints: regulation → deployment model; skills → service model; plus Well-Architected and cost governance.',
    picture_h2='A method before an answer', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven organisation types, one by one', TYPES)],
    how_h2='Deciding for one organisation, step by step', how_intro='Apply the method to a real public-sector scenario.', how_anim=DEC,
    parts_h2='Six tools for scenario decisions', parts_html=parts, lv='',
    myth_rows=[('Public cloud is never allowed for banks.', 'It is used with RBI-compliant controls.', 'Type 4.'), ('Small businesses need cloud engineers.', 'Most need SaaS and a partner.', 'Type 2.'), ('One model fits a whole enterprise.', 'Models vary per workload.', 'Type 3.')],
    extra_secs=[('deep', 'Deep dive', 'Interview case-study template, typical mistakes', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Apply seven questions to any organisation.', 'Recommend deployment, service models and providers for seven organisation types.', 'Run a structured design review, set cost allocation and check Regional availability on your own account.', 'Write a scenario brief and ADR.', 'Answer cloud case-study interviews.'],
    next_html='<a href="../04-cloud-careers-and-certifications/">10.4 Cloud careers and certifications</a>.',
    pre='<b>Before you start:</b> Modules 2, 3 and 10.1.')
