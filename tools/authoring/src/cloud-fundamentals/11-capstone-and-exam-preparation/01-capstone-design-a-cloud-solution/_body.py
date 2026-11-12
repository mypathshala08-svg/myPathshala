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
def iac(name):
    return open(os.path.join(HERE, 'iac', name)).read().rstrip('\n')

hk = hook('Your college canteen loses 30 minutes every lunch break to queues. The principal asks your batch: “Design a cloud system so 3,000 students can pre-order and pick up in 5 minutes — safely, within ₹5,000 a month.” Where do you start?',
    'With a <b>design document</b>, not with a console. This capstone brings the whole course together: <b>requirements</b>, <b>architecture</b>, <b>service choices</b>, <b>security</b>, <b>reliability</b>, <b>cost</b> and <b>operations</b> — seven deliverables explained one by one with a worked example. The animation walks the capstone week by week, and on <b>your own</b> account you deploy a reference version <b>from code</b> (CloudFormation, Bicep or Terraform), test it, watch it, and tear it down cleanly.',
    ['Graders (and interviewers) mark the reasons behind choices, not the logo count.', 'Non-functional requirements decide most of the architecture.', 'Deploying from a template is the difference between a demo and an engineering project.'])

def story_scene():
    o = t(180, 12, 'The canteen brief', 9, 'ink', bold=True)
    for i, (a, b, tn) in enumerate([('3,000 students', 'lunch peak', 'blue'), ('5-minute pick-up', 'speed', 'green'), ('₹5,000 / month', 'budget', 'amber'), ('Safe + private', 'DPDP', 'red')]):
        x = 8 + i * 88
        o += box(x, 30, 80, 56, tn, rx=8) + t(x + 40, 54, a, 7.6, 'ink', bold=True) + t(x + 40, 70, b, 6.8, 'ink2')
    o += t(180, 108, 'Every design choice must trace back to one of these', 7.4, 'ink', bold=True)
    return o
scene_svg = scene('The capstone brief: 3,000 students at the lunch peak, 5-minute pick-up, ₹5,000 per month budget, safe and private under DPDP.', story_scene(), 'Requirements first; <tspan font-weight="700" class="s-acc">services last</tspan>.', h=122)
dialogue = '''K> Sir, can we start with Kubernetes? It looks great on a CV.
A> For 3,000 orders a day and a ₹5,000 budget? Show me which requirement needs it.
R> None, honestly. The peak is 20 minutes long; the rest of the day is almost idle.
A> Then serverless or a small PaaS fits — scale for the peak, almost zero cost at night. Kubernetes would cost more than the whole budget and need a team.
K> So the capstone is about reasons.
A> Exactly. Seven deliverables, each with its “why”. Let’s go one by one.'''

def archfig():
    o = t(320, 16, 'Reference architecture: campus canteen pre-order', 11, 'ink', bold=True)
    N = [('Students', 'phones', 62, 'violet'), ('CDN + static app', 'menu, images', 165, 'blue'), ('API', 'functions / PaaS', 268, 'amber'), ('Orders DB', 'NoSQL / SQL', 371, 'green'), ('Kitchen screen', 'live queue', 474, 'blue'), ('Monitoring', 'alarms, logs', 577, 'red')]
    for a, b, x, tn in N:
        o += box(x - 46, 50, 92, 52, tn, rx=8) + t(x, 72, a, 7.8, 'ink', bold=True) + t(x, 88, b, 6.8, 'ink2')
    for x in (108, 211, 314, 417, 520): o += arrow(x, 76, x + 11, 76)
    o += box(150, 130, 340, 36, 'card', rx=8) + t(320, 146, 'Identity (college SSO) · India Region · encryption · budgets · IaC + CI/CD', 7.4, 'ink', bold=True) + t(320, 160, 'cross-cutting controls', 6.8, 'ink2')
    o += t(320, 190, 'AWS: CloudFront + Lambda + DynamoDB · Azure: Static Web/App Service + Cosmos/SQL · Google: Firebase/Cloud Run + Firestore', 7, 'ink2')
    return o
ARCH = bigfig('Reference architecture: students on phones, CDN and static app, API on functions or PaaS, orders database, kitchen screen, monitoring; cross-cutting identity, India Region, encryption, budgets, IaC and CI/CD.', archfig(), h=200)

picture = ('  <p>A reference design the rest of the lesson justifies, piece by piece:</p>\n' + ARCH +
           '\n  <h3>Capstone brief and marking guide</h3>\n' + table(['Deliverable', 'What graders look for', 'Weight'], [
               ['1 Requirements', 'functional + non-functional, numbers, constraints', '15%'], ['2 Architecture', 'clear diagram, data flow, trust boundaries', '15%'], ['3 Service selection', 'choice + rejected alternative + reason', '15%'],
               ['4 Security + compliance', 'identity, data protection, DPDP, guard-rails', '15%'], ['5 Reliability + DR', 'SLO, failure modes, backup/restore', '10%'], ['6 Cost', 'monthly estimate, assumptions, guard-rails', '10%'], ['7 Operations + delivery', 'IaC, CI/CD, monitoring, runbook, demo', '20%']], minw=600) +
           '\n  <p>Use this table as the structure of your report and presentation — it mirrors how architecture reviews and interview case studies are judged.</p>')

RN = {'brief': (4, 54, 50, 50, 'user', 'Brief', 'week 1'), 'req': (66, 4, 62, 46, 'meter', 'Requirements', 'numbers'), 'arch': (66, 104, 62, 46, 'chart', 'Architecture', 'options'),
      'sec': (142, 54, 60, 50, 'shield', 'Security + cost', 'week 2'), 'iac': (216, 4, 62, 46, 'gear', 'IaC build', 'week 3'), 'test': (216, 104, 62, 46, 'phone', 'Test + observe', 'load, alarms'), 'demo': (292, 54, 64, 50, 'app', 'Demo + report', 'week 4')}
RS = [dict(on=['brief', 'req'], hot='req', move=(54, 79, 72, 30, 'clarify'), head='Week 1 · Turn the brief into numbers', text='3,000 students, 80% order between 12:30 and 12:50 → peak ≈ 2 orders/second; p95 < 1 s;', text2='99.5% during lunch; data in India; ₹5,000/month.', svc='Non-functional requirements drive the design'),
      dict(on=['req', 'arch'], hot='arch', move=(97, 50, 97, 104, 'design'), head='Week 1 · Two architecture options', text='Option A: serverless (functions + NoSQL). Option B: small PaaS app + managed SQL.', text2='Compare on cost at idle, peak scaling, team skills.', svc='Write an ADR for the choice (Lesson 10.3)'),
      dict(on=['arch', 'sec'], hot='sec', move=(128, 127, 150, 90, 'protect'), head='Week 2 · Security, privacy and cost', text='College SSO, least-privilege roles, encryption, DPDP notice and retention; cost model:', text2='3,000 × 22 days requests, storage, egress — well under budget for option A.', svc='Modules 9 and 5.5'),
      dict(on=['sec', 'iac'], hot='iac', move=(165, 54, 216, 20, 'code'), head='Week 3 · Build from code', text='Write the stack as CloudFormation, Bicep or Terraform; deploy with a pipeline; tags', text2='and budgets included. No console clicking for production.', svc='Practical step 1'),
      dict(on=['iac', 'test'], hot='test', move=(247, 50, 247, 104, 'load'), head='Week 3 · Test and observe', text='Send a burst of orders, watch latency and errors, fire the alarm on purpose, read', text2='logs. Fix one thing and record it.', svc='Practical step 2'),
      dict(on=list(RN), hot='demo', move=(278, 127, 298, 90, 'present'), head='Week 4 · Demo, report, tear down', text='10-minute demo: requirement → design → live system → metrics → cost. Then delete', text2='everything from code and show the empty account.', svc='Practical step 3')]
WEEKS = flow_anim('The capstone, week by week', 'From brief to demo in four weeks.', 'Capstone workflow', 'Animation: requirements in numbers; two architecture options; security, privacy and cost; build from code; test and observe; demo, report and tear down.', RN, RS, hid='capflow')

def mapfig():
    o = t(320, 16, 'Seven deliverables of a cloud solution design', 11, 'ink', bold=True)
    items = [('1', 'Requirements', 'functional + non-functional', 'blue'), ('2', 'Architecture', 'diagram + data flow', 'violet'), ('3', 'Service selection', 'choices + alternatives', 'amber'), ('4', 'Security + compliance', 'identity, data, DPDP', 'red'),
             ('5', 'Reliability + DR', 'SLOs, failures, backups', 'green'), ('6', 'Cost', 'estimate + guard-rails', 'card'), ('7', 'Operations + delivery', 'IaC, CI/CD, monitoring', 'green')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 8, 'ink', bold=True) + t(x + 78, y + 54, b, 6.6, 'ink2')
    o += t(320, 210, 'Each deliverable has a template and the worked canteen example below.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of seven deliverables: requirements, architecture, service selection, security and compliance, reliability and DR, cost, operations and delivery.', mapfig(), h=222)

A1 = mk(['Who and what', 'How well', 'Limits'], ['functional|order, pay|track, pick up', 'non-functional|peak, latency|availability', 'constraints|budget, India|DPDP, skills'], ['blue', 'amber', 'red'],
        ['list what the system must do', 'quantify how well: load, latency, availability', 'record constraints: budget, residency, skills, deadlines'],
        [('Functional', 'Features users need.', ''), ('Non-functional', 'Numbers: peak, latency, uptime, RPO/RTO.', ''), ('Constraints', 'Budget, residency, skills, time.', '')],
        'Requirements in action', 'Numbers, not adjectives.', 'Requirements', 'Animation: functional; non-functional; constraints.', 'd1anim')
T1 = vt(1, 'Requirements', 'blue',
    'The <b>requirements</b> deliverable states what the system must do (<b>functional</b> requirements), how well it must do it (<b>non-functional</b>: load, latency, availability, security, RPO/RTO) and the <b>constraints</b> it must respect (budget, data residency, regulations, skills, deadlines), expressed as measurable numbers.',
    'A tailor’s order slip: not “a nice shirt” but chest 40, sleeve 25, cotton, ready by Friday, under ₹1,500.',
    'Canteen: order, pay by UPI, see queue number, kitchen screen; peak 2 orders/s for 20 minutes; p95 < 1 s; 99.5% during 12:00–14:00; data in India; ₹5,000/month.',
    'Templates: user stories, a non-functional requirements table, constraints list.', '', A1,
    'always — every later choice must point back to a requirement.',
    'you write adjectives (“fast, scalable, secure”) without numbers.',
    'A clear list of what the system must do, how well, and within which limits.',
    [('Interview', 'Students, kitchen, admin.'), ('Quantify', 'Users, peaks, data size.'), ('NFRs', 'Latency, uptime, RPO/RTO.'), ('Constraints', 'Budget, India, DPDP.'), ('Prioritise', 'Must / should / could.')],
    [('NFR', 'non-functional requirement'), ('p95 latency', '95% of requests are faster than this'), ('MoSCoW', 'must, should, could, won’t prioritisation')],
    table(['', 'Functional', 'Non-functional'], [['Example', 'student can cancel order', 'p95 < 1 s at 2 orders/s'], ['Tested by', 'feature tests', 'load tests, monitoring'], ['Drives', 'features', 'architecture']], minw=420),
    ['Every project', 'Interviews', 'Tenders'],
    'Most architecture review failures trace back to missing or vague non-functional requirements — teams over- or under-build.',
    'Do the peak maths explicitly (users × share × window) — it usually shows a much smaller system than people imagine.')

A2 = mk(['Boxes', 'Arrows', 'Boundaries'], ['components|app, API, DB|monitoring', 'data flow|order path|numbers', 'boundaries|trust zones|Region, network'], ['violet', 'amber', 'red'],
        ['draw the components', 'draw the data flow for the main request', 'mark trust boundaries, Regions and networks'],
        [('Components', 'Each service as a box with its role.', ''), ('Flow', 'Numbered arrows for the main request.', ''), ('Boundaries', 'Trust zones, Region, private networks.', '')],
        'Architecture in action', 'A picture with a story.', 'Architecture', 'Animation: boxes; arrows; boundaries.', 'd2anim')
T2 = vt(2, 'Architecture diagram and data flow', 'violet',
    'The <b>architecture</b> deliverable is a clear diagram of components, numbered data flows and trust boundaries (internet, private network, Region, accounts), with a short narrative of how the main requests travel and where data is stored, at a level a reviewer can understand in two minutes.',
    'A metro map: stations (components), lines (flows) and zone boundaries — not the wiring inside each train.',
    'Canteen: phone → CDN/static app → API (functions) → orders table; kitchen screen polls the API; monitoring and budgets across all; everything in Mumbai.',
    'Diagram tools: draw.io/diagrams.net, Excalidraw, Lucidchart; official provider icon sets; C4 model for levels of detail.', 'Architecture styles are in Module 7.', A2,
    'always; keep one overview and one detailed diagram.',
    'you draw 40 icons without flows — reviewers cannot follow it.',
    'A drawing that shows the parts of the system and how data moves between them.',
    [('Context', 'Users and external systems.'), ('Containers', 'Apps, APIs, DBs.'), ('Flows', 'Numbered steps.'), ('Boundaries', 'Trust and network zones.'), ('Legend', 'Explain symbols.')],
    [('C4 model', 'context, containers, components, code levels'), ('trust boundary', 'where trust changes, e.g. internet → private network'), ('data flow', 'path data takes through the system')],
    table(['', 'Good diagram', 'Weak diagram'], [['Flow', 'numbered arrows', 'none'], ['Detail', 'right level', 'every icon'], ['Story', '2-minute explanation', 'needs the author']], minw=420),
    ['Design reviews', 'Interviews', 'Documentation'],
    'Many teams use the C4 model to keep diagrams readable: a context diagram for managers, container diagrams for engineers.',
    'Draw the failure path too: what happens when the database is unavailable during the lunch peak?')

A3 = mk(['Options', 'Trade-offs', 'Decision'], ['options|serverless|PaaS, VMs', 'compare|cost, scale|skills, lock-in', 'ADR|choice + why|rejected option'], ['amber', 'blue', 'green'],
        ['list two or three ways to build each part', 'compare them against the requirements', 'record the choice, the reason and what you rejected'],
        [('Options', '2–3 candidates per component.', ''), ('Compare', 'Against requirements and constraints.', ''), ('Decide', 'ADR with rejected alternative.', '')],
        'Service selection in action', 'Choice + reason + alternative.', 'Service selection', 'Animation: options; trade-offs; decision.', 'd3anim')
T3 = vt(3, 'Service selection and trade-offs', 'amber',
    'The <b>service selection</b> deliverable explains, for each component, which cloud service was chosen, which alternatives were considered and why — tied to requirements such as cost at idle, peak scaling, operational effort, skills, portability and Regional availability — usually captured as architecture decision records.',
    'Choosing a vehicle for a school trip: bus, vans or trains compared on cost, seats, time and driver availability — and writing down why you chose the bus.',
    'Canteen API: functions chosen over Kubernetes (idle cost near zero, peak 20 minutes, two-person team); orders in NoSQL over SQL (simple key access, pay-per-request) — SQL kept as option B for reporting needs.',
    'Lessons 2.5 (decision path), 6.1–6.4 (services), 10.2 (equivalents).', '', A3,
    'every significant component.',
    'you choose by popularity or CV value.',
    'Explaining which cloud services you picked, what else you considered, and why.',
    [('Shortlist', '2–3 options.'), ('Criteria', 'From requirements.'), ('Score', 'Simple matrix.'), ('ADR', 'Decision + consequences.'), ('Revisit', 'When requirements change.')],
    [('ADR', 'architecture decision record'), ('decision matrix', 'scored comparison table'), ('lock-in', 'cost of moving later')],
    table(['Criterion', 'Functions + NoSQL', 'Kubernetes + SQL'], [['Idle cost', 'near zero', 'cluster always on'], ['Peak scaling', 'automatic', 'needs tuning'], ['Ops effort', 'low', 'high'], ['Budget fit (₹5,000)', 'yes', 'no']], minw=440),
    ['Every design', 'Interviews', 'Proposals'],
    'Reviewers often ask “what did you reject and why?” first — it shows you actually compared options.',
    'One rejected alternative per decision is enough; it proves thinking without bloating the report.')

A4 = mk(['Identities', 'Data protection', 'Compliance'], ['identity|college SSO|least privilege', 'data|encrypt, minimise|retention', 'comply|DPDP notice|logs 180 d'], ['red', 'amber', 'blue'],
        ['define who and what can access each component', 'protect personal data: minimise, encrypt, retain only as needed', 'map to DPDP and CERT-In duties; add guard-rails'],
        [('Identity', 'SSO for staff, least-privilege roles for code.', ''), ('Data', 'Minimise, encrypt, retention rules.', ''), ('Comply', 'DPDP notice, rights, logs, guard-rails.', '')],
        'Security in action', 'Design it in, don’t bolt it on.', 'Security', 'Animation: identities; data protection; compliance.', 'd4anim')
T4 = vt(4, 'Security and compliance design', 'red',
    'The <b>security and compliance</b> deliverable describes identities and access (people and workloads), network exposure, data classification and protection (encryption, minimisation, retention), logging and detection, and how legal duties — DPDP for students’ personal data, CERT-In logging — are met, using the shared responsibility model.',
    'The safety plan for a school event: who gets which pass, where valuables are kept, which areas are CCTV-covered, and who to call if something goes wrong.',
    'Canteen: students log in with college SSO; the API role can only write the orders table; only roll number and name stored (no phone numbers); data deleted after the semester; logs kept 180 days; public-access blocks on storage.',
    'Module 9 lessons; provider guard-rails (SCPs/Azure Policy/org policies), KMS, threat detection.', '', A4,
    'always — especially with personal data.',
    'security is a final slide added after building.',
    'How you keep the system and students’ data safe and follow the law.',
    [('Classify', 'What personal data, how sensitive.'), ('Identity', 'SSO + roles.'), ('Network', 'Public only where needed.'), ('Data', 'Encrypt, minimise, retain.'), ('Detect', 'Logs, alarms, threat detection.')],
    [('data minimisation', 'collect only what is needed'), ('least privilege', 'only needed permissions'), ('guard-rail', 'preventive policy')],
    table(['Layer', 'Provider', 'Your team'], [['Data centre, hosts', 'yes', '—'], ['Function runtime', 'yes', '—'], ['Code, IAM, data, settings', '—', 'yes']], minw=420),
    ['Every system with users', 'Student data', 'Payments'],
    'Educational institutions hold large amounts of minors’ and students’ personal data — DPDP gives children’s data extra protection, so minimisation matters here.',
    'Write a “what we do NOT store” list — it is often the strongest privacy control and graders notice it.')

A5 = mk(['Set targets', 'Find failure modes', 'Plan recovery'], ['SLO|99.5% lunch|RPO 5 min', 'failures|AZ, DB, deploy|bad code', 'recovery|multi-AZ|backups, rollback'], ['green', 'amber', 'blue'],
        ['set availability and recovery targets', 'list how each component can fail', 'design redundancy, backups and rollback; test them'],
        [('Targets', 'SLO, RPO, RTO.', ''), ('Failure modes', 'Zone, DB, bad deploy, quota.', ''), ('Recovery', 'Multi-AZ, PITR backups, rollback; tested.', '')],
        'Reliability in action', 'Plan for failure.', 'Reliability', 'Animation: set targets; find failure modes; plan recovery.', 'd5anim')
T5 = vt(5, 'Reliability and disaster recovery', 'green',
    'The <b>reliability and DR</b> deliverable sets service-level objectives and recovery targets (RPO/RTO), lists failure modes (zone outage, database failure, bad deployment, quota limits, dependency failure) and describes the design responses — multi-AZ managed services, backups with point-in-time recovery, safe deployment and rollback, graceful degradation — and how they are tested.',
    'A wedding plan B: if it rains, the tent; if the cook falls ill, the backup caterer; if the power fails, the generator — all checked the day before.',
    'Canteen: managed services are multi-AZ by default; DynamoDB point-in-time recovery on; canary deploys with rollback; if payments fail, orders are accepted as “pay at counter”.',
    'Module 7 (availability), 8.2 (deployments), 9.2 (ransomware-safe backups).', '', A5,
    'always — scaled to the requirement (99.5% is very different from 99.99%).',
    'you promise 99.99% for a student project — cost and complexity explode.',
    'Planning how the system keeps working, and how it recovers when parts fail.',
    [('SLO', 'Per critical journey.'), ('Failure modes', 'Table with impact.'), ('Design', 'Redundancy, backups.'), ('Degrade', 'Fallback behaviour.'), ('Test', 'Game day / restore test.')],
    [('graceful degradation', 'keep core function when parts fail'), ('PITR', 'point-in-time recovery'), ('game day', 'planned failure test')],
    table(['Failure', 'Impact', 'Response'], [['Zone outage', 'none (multi-AZ)', 'managed services'], ['Bad deploy', 'errors rise', 'canary + rollback'], ['Payment API down', 'cannot pay', 'pay at counter']], minw=440),
    ['Every production system', 'Exam scenarios', 'Interviews'],
    'Reliability targets cost money: each extra “nine” roughly multiplies effort — match the target to the business (Lesson 5.4).',
    'Include one tested recovery in your demo (restore an item, roll back a version) — it convinces more than any slide.')

A6 = mk(['Usage model', 'Price it', 'Guard it'], ['usage|orders, GB|requests', 'price|calculator|free tiers', 'guard|budgets|anomaly alerts'], ['card', 'amber', 'green'],
        ['model usage from the requirements', 'price each service with calculators, showing assumptions', 'add budgets, alerts and tags'],
        [('Model', 'Orders, requests, storage, transfer.', ''), ('Price', 'Calculator estimate with assumptions.', ''), ('Guard', 'Budgets, anomaly alerts, tags.', '')],
        'Cost in action', 'Show your assumptions.', 'Cost', 'Animation: usage model; pricing; guard-rails.', 'd6anim')
T6 = vt(6, 'Cost estimate and FinOps', 'card',
    'The <b>cost</b> deliverable estimates monthly spend from a usage model (requests, compute time, storage, data transfer) using provider calculators, states assumptions and free-tier effects, compares options, and defines guard-rails — budgets, anomaly alerts, tags and clean-up — so the estimate holds in practice.',
    'A trip budget: number of people × days × meals × prices, plus a 10% buffer and a rule that nobody books a five-star hotel without asking.',
    'Canteen: ~66,000 orders/month → ~130,000 API calls, a few GB of storage and transfer — on serverless roughly within free tiers or a few hundred rupees; a ₹5,000 budget alert and anomaly detection guard it.',
    'AWS Pricing Calculator, Azure pricing calculator, Google Cloud Pricing Calculator; budgets and anomaly detection (Lessons 5.5, 9.2).', '', A6,
    'always, with assumptions written down.',
    'you show one number without the usage model behind it.',
    'Working out how much the system will cost each month, and setting alerts so it stays that way.',
    [('Usage', 'From requirements.'), ('Calculator', 'Per service.'), ('Compare', 'Option A vs B.'), ('Guard', 'Budget + anomaly alerts.'), ('Review', 'Actual vs estimate monthly.')],
    [('usage model', 'expected quantities per month'), ('free tier', 'free monthly allowance'), ('unit cost', 'cost per order')],
    table(['Item', 'Assumption', 'Note'], [['Orders', '3,000 × 22 days', '≈ 66,000/month'], ['API calls', '≈ 2 per order', '≈ 130,000/month'], ['Storage', '< 5 GB', 'menu images, orders']], minw=420),
    ['Every proposal', 'Tenders', 'Start-up planning'],
    'Graders and managers trust estimates with visible assumptions more than precise-looking totals.',
    'Add cost per order (total ÷ orders) — it makes the business case obvious.')

A7 = mk(['Infrastructure as code', 'Pipeline', 'Observe + runbook'], ['IaC|CFN / Bicep|Terraform', 'CI/CD|tests, deploy|canary', 'operate|dashboards|alarms, runbook'], ['green', 'amber', 'blue'],
        ['define everything as code', 'deploy through a tested pipeline with safe releases', 'monitor with dashboards and alarms; write the runbook'],
        [('IaC', 'Stack defined in CloudFormation, Bicep or Terraform.', ''), ('Pipeline', 'Tests, deploy, canary.', ''), ('Operate', 'Dashboards, alarms, runbook.', '')],
        'Operations in action', 'Build it the way you’ll run it.', 'Operations', 'Animation: infrastructure as code; pipeline; observe and runbook.', 'd7anim')
T7 = vt(7, 'Operations and delivery', 'green',
    'The <b>operations and delivery</b> deliverable shows how the solution is built and run: infrastructure as code, CI/CD with tests and safe releases, monitoring with dashboards and alarms on golden signals, logging, runbooks for common incidents and a clean teardown — demonstrated live.',
    'A restaurant’s kitchen manual: standard recipes (IaC), how new dishes are introduced (pipeline), what to watch during service (monitoring) and what to do if the gas fails (runbook).',
    'Canteen: the stack is one template (practical step 1), a pipeline from Lesson 8.3 deploys code, an error alarm fires to the team channel, and the runbook covers “orders not appearing on kitchen screen”.',
    'Lessons 8.1–8.3; CloudFormation, Bicep, Terraform; provider monitoring services.', '', A7,
    'always — this is what makes it engineering, not a demo.',
    'resources were created by hand and nobody can rebuild them.',
    'How the system is built from code, released safely, watched and fixed.',
    [('IaC', 'All resources in code.'), ('Pipeline', 'Test → deploy.'), ('Observe', 'Golden signals.'), ('Runbook', 'Top 3 incidents.'), ('Teardown', 'Delete from code.')],
    [('IaC', 'infrastructure as code'), ('runbook', 'step-by-step incident guide'), ('teardown', 'deleting all resources cleanly')],
    table(['', 'Hand-built', 'From code'], [['Rebuild time', 'hours/days', 'minutes'], ['Review', 'none', 'pull request'], ['Teardown', 'forgotten resources', 'one command']], minw=420),
    ['Every real project', 'Portfolio', 'Interviews'],
    'Demonstrating “delete everything and recreate it in five minutes” is one of the most convincing moments in any cloud project review.',
    'Record the demo as a short video for your portfolio (Lesson 10.4) — it outlives the deleted resources.')

SUMMARY = table(['#', 'Deliverable', 'Canteen answer (short)', 'Course lessons'], [
    ['1', 'Requirements', '3,000 users, 2 orders/s peak, p95 < 1 s, ₹5,000, India', '5.3, 5.4'], ['2', 'Architecture', 'CDN + API + NoSQL + kitchen screen + monitoring', '7.x'], ['3', 'Service selection', 'functions + NoSQL; rejected Kubernetes', '2.5, 6.x, 10.2'],
    ['4', 'Security', 'SSO, least privilege, minimise, 180-day logs', '9.x'], ['5', 'Reliability', 'multi-AZ managed, PITR, canary, pay-at-counter fallback', '7.2, 8.2'], ['6', 'Cost', 'free tier to a few hundred ₹ + budget', '5.5, 9.2'], ['7', 'Operations', 'IaC, pipeline, alarms, runbook, teardown', '8.x']], minw=620)
CHECK = ('  <h3>Check yourself: which deliverable?</h3>\n' +
    qx('A. “p95 latency under 1 second at 2 orders per second.”', ['Requirements (non-functional)', 'Cost', 'Operations', 'Architecture'], 0, 'NFR.') +
    qx('B. “We rejected Kubernetes because idle cost exceeds the budget.”', ['Service selection', 'Security', 'Reliability', 'Requirements'], 0, 'Trade-off.') +
    qx('C. “If payments fail, accept pay-at-counter.”', ['Reliability (graceful degradation)', 'Cost', 'Security', 'Architecture only'], 0, 'Fallback.') +
    qx('D. “Everything is in one Bicep file and deleted with one command.”', ['Operations and delivery', 'Requirements', 'Cost', 'Compliance'], 0, 'IaC.'))

TYPES = ('  <p>Seven deliverables, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, the canteen answer and an expert note.</p>\n'
         + challenge(['How many orders per second is the real peak for 3,000 students?', 'What should a design say it does NOT store?', 'Which single demo moment convinces reviewers most?'], 'types 1, 4 and 7') + MAP
         + jump(['Requirements', 'Architecture', 'Services', 'Security', 'Reliability', 'Cost', 'Operations']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">The canteen capstone on one page</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('Design document', '6–10 pages following the seven deliverables.', 'Graders and reviewers read it first.', 'Template in the marking table.'),
    ('Architecture diagram', 'Overview + one detailed view.', 'Explains the design in minutes.', 'diagrams.net with provider icons.'),
    ('ADRs', 'One page per big decision.', 'Shows reasoning.', 'Context, decision, consequences.'),
    ('IaC repository', 'Templates + app code + pipeline.', 'Reproducibility.', 'GitHub with README.'),
    ('Evidence', 'Screenshots, metrics, cost report.', 'Proves it worked.', 'Load test, alarm email, bill.'),
    ('Demo', '10-minute live walkthrough.', 'Final impression.', 'Requirement → design → system → metrics → teardown.')])

DEEP = ('  <h3>Other capstone briefs (choose one)</h3>\n' + table(['Brief', 'Key requirement twist'], [['Hospital diet-planner integration', 'hybrid with on-prem patient data (Lesson 3.1)'], ['State scheme dashboard', 'government cloud, citizen-scale deadlines (10.3)'], ['IoT cold-chain for vaccine boxes', 'edge filtering, offline buffering (3.4)'], ['Big Data analytics for college results', 'batch pipeline, warehouse, cost per query (10.2)'], ['Exam-result portal', 'extreme one-day peak, CDN, caching (7.5)']], minw=560) +
    '\n  <h3>Peak maths worked out</h3>\n  <p>3,000 students × 80% ordering in a 20-minute window = 2,400 orders in 1,200 s = 2 orders per second on average in the peak; allow 5× burst → design for 10 requests/second. A single small function or PaaS instance handles this; serverless auto scaling covers bursts.</p>\n'
    '  <h3>Presentation structure (10 minutes)</h3>\n  <ol><li>The problem and numbers (1 min).</li><li>Architecture and one key trade-off (3 min).</li><li>Live demo: order → kitchen screen → metrics (3 min).</li><li>Security, cost and reliability in one slide each (2 min).</li><li>Teardown proof and what you’d do next (1 min).</li></ol>')

clouds = vendor_tabs('<p><b>AWS reference:</b> CloudFront + S3 (static app), Lambda function URL or API Gateway, DynamoDB with PITR, CloudWatch alarms, IAM Identity Center/Cognito for login, CloudFormation/CDK, CodePipeline.</p>',
    '<p><b>Azure reference:</b> Static Web Apps or App Service, Azure Functions, Cosmos DB or Azure SQL, Application Insights + alerts, Entra ID for login, Bicep, GitHub Actions.</p>',
    '<p><b>Google Cloud reference:</b> Firebase Hosting or Cloud Storage + CDN, Cloud Run, Firestore or Cloud SQL, Cloud Monitoring alerts, Identity Platform, Terraform/Infrastructure Manager, Cloud Build.</p>') + \
    cloud3([['Static front end', 'S3 + CloudFront / Amplify', 'Static Web Apps / Storage static site', 'Firebase Hosting / Storage + CDN'], ['API', 'Lambda (+ API Gateway)', 'Functions / App Service', 'Cloud Run'], ['Orders DB', 'DynamoDB', 'Cosmos DB / Azure SQL', 'Firestore / Cloud SQL'], ['IaC', 'CloudFormation / CDK', 'Bicep', 'Terraform / Infrastructure Manager'], ['Monitoring', 'CloudWatch', 'Application Insights', 'Cloud Monitoring']])

AZAPP = '''mkdir app && cd app
cat > app.py <<'EOF'
from flask import Flask, request, jsonify
import uuid
app = Flask(__name__)
ORDERS = []   # demo only: in memory; use Cosmos DB / Azure SQL in your capstone
@app.post("/")
def order():
    item = {"id": str(uuid.uuid4()), "dish": (request.get_json(silent=True) or {}).get("dish", "thali")}
    ORDERS.append(item); return jsonify(item), 201
@app.get("/")
def count():
    return jsonify({"orders": len(ORDERS)})
EOF
printf "flask\\ngunicorn\\n" > requirements.txt && zip -q ../app.zip app.py requirements.txt && cd ..'''

MOCKQ.extend([
 (mock('aws', ['CloudFormation', 'Stacks', 'Create stack'], ['Stacks', 'StackSets', 'Exports'], 'Stacks', [('Template', '[x] Upload a template file · canteen.yaml'), ('Stack name', 'canteen'), ('Capabilities', '[x] I acknowledge IAM resources')], 'Submit'),
  mock('az', ['Deploy a custom template'], ['Select a template', 'Basics', 'Review + create'], 'Select a template', [('Template', 'main.bicep → build your own'), ('Resource group', 'rg-canteen · Central India')], 'Review + create'),
  mock('gcp', ['Cloud Shell', 'Terminal'], ['Editor', 'Terminal'], 'Terminal', [('$ terraform plan', 'Plan: 3 to add'), ('$ terraform apply', 'Apply complete! url = https://canteen-…run.app')], 'Run')),
 (mock('aws', ['CloudWatch', 'Metrics', 'Lambda'], ['Dashboards', 'Alarms', 'Metrics', 'Logs'], 'Metrics', [('Invocations', 'burst of 50'), ('Duration p95', 'ms'), ('Alarm', 'canteen-ErrorsAlarm · OK')], 'Add to dashboard'),
  mock('az', ['Application Insights', 'Live metrics'], ['Overview', 'Live metrics', 'Failures', 'Performance'], 'Live metrics', [('Incoming requests', 'burst of 50'), ('Response time', 'ms')], 'Pause'),
  mock('gcp', ['Cloud Run', 'canteen', 'Metrics'], ['Metrics', 'SLOs', 'Logs', 'Revisions'], 'Metrics', [('Request count', 'burst of 50'), ('Request latency p95', 'ms'), ('Instance count', 'scaled 0 → n → 0')], 'View in Monitoring')),
 (mock('aws', ['CloudFormation', 'Stacks', 'canteen'], ['Stack info', 'Events', 'Resources'], 'Stack info', [('Status', 'DELETE_COMPLETE'), ('Resources', 'table, role, function, alarm removed')], 'Delete'),
  mock('az', ['Resource groups', 'rg-canteen'], ['Overview', 'Deployments'], 'Overview', [('Delete resource group', 'type name to confirm'), ('Resources', 'all removed')], 'Delete'),
  mock('gcp', ['Cloud Shell', 'Terminal'], ['Editor', 'Terminal'], 'Terminal', [('$ terraform destroy', 'Destroy complete! Resources: 3 destroyed')], 'Run')),
])

STEP1 = ('1 · Deploy the reference stack from code', tri(
    (['Save the template on the right as <code>canteen.yaml</code> → [[CloudFormation]] → [[Create stack]] → [[Upload a template file]] → stack name <code>canteen</code> → acknowledge IAM → [[Submit]].', 'Then create the public function URL (CLI lines after the template).'],
     "cat > canteen.yaml <<'EOF'\n" + iac('canteen.yaml') + "\nEOF\naws cloudformation deploy --stack-name canteen --template-file canteen.yaml --capabilities CAPABILITY_IAM --region ap-south-1 --tags project=canteen\nFN=$(aws cloudformation describe-stacks --stack-name canteen --region ap-south-1 --query \"Stacks[0].Outputs[?OutputKey=='FunctionName'].OutputValue\" --output text)\naws lambda add-permission --function-name $FN --statement-id url --action lambda:InvokeFunctionUrl --principal '*' --function-url-auth-type NONE --region ap-south-1 >/dev/null\naws lambda add-permission --function-name $FN --statement-id url-invoke --action lambda:InvokeFunction --principal '*' --invoked-via-function-url --region ap-south-1 >/dev/null\nURL=$(aws lambda create-function-url-config --function-name $FN --auth-type NONE --region ap-south-1 --query FunctionUrl --output text); echo $URL",
     '“Successfully created/updated stack - canteen” and a function URL. Four resources from one file: table, role, function, alarm.'),
    (['Save <code>main.bicep</code> → [[Deploy a custom template]] → [[Build your own template]] → paste → resource group <code>rg-canteen</code> (Central India) → [[Review + create]].', 'Deploy the app code with the CLI lines after the template.'],
     "cat > main.bicep <<'EOF'\n" + iac('main.bicep') + "\nEOF\naz group create -n rg-canteen -l centralindia --tags project=canteen >/dev/null\nAPP=$(az deployment group create -g rg-canteen --template-file main.bicep --query properties.outputs.appName.value -o tsv)\n" + AZAPP + "\naz webapp deploy -g rg-canteen -n $APP --src-path app.zip --type zip\nURL=https://$(az webapp show -g rg-canteen -n $APP --query defaultHostName -o tsv); echo $URL",
     'the app name and its HTTPS URL; the zip deploy builds the Python app (first start can take a minute on F1). Resources: Log Analytics, Application Insights, F1 plan, web app.'),
    (['In Cloud Shell, save <code>main.tf</code> → <code>terraform init</code> → <code>terraform apply</code>. (Cloud Shell includes Terraform.)', 'The sample container stands in for your API; replace the image with your own build (Lesson 8.3).'],
     "mkdir canteen && cd canteen\ncat > main.tf <<'EOF'\n" + iac('main.tf') + "\nEOF\ngcloud services enable run.googleapis.com storage.googleapis.com\nterraform init -input=false >/dev/null\nterraform apply -auto-approve -input=false -var project=$(gcloud config get-value project) | tail -3\nURL=$(terraform output -raw url); echo $URL",
     '<code>Apply complete! Resources: 3 added</code> and a Cloud Run URL. If your organisation blocks <code>allUsers</code>, remove the IAM resource and call the service with an identity token.')),
    'One file, one command, a complete stack — and the file goes into your capstone repository.')

STEP2 = ('2 · Simulate the lunch rush and observe', tri(
    (['Run the burst on the right, then [[CloudWatch]] → [[Metrics]] → Lambda → Invocations, Duration; [[Alarms]] shows the errors alarm state.'],
     "for i in $(seq 50); do curl -s -o /dev/null -w '%{http_code} %{time_total}\\n' -X POST $URL -H 'content-type: application/json' -d '{\"dish\":\"thali\"}' & done; wait\ncurl -s $URL; echo\naws cloudwatch get-metric-statistics --namespace AWS/Lambda --metric-name Invocations --dimensions Name=FunctionName,Value=$FN \\\n  --start-time $(date -u -d '-10 min' +%FT%TZ) --end-time $(date -u +%FT%TZ) --period 600 --statistics Sum --region ap-south-1 --query 'Datapoints[0].Sum'",
     '50 lines of <code>201</code> with times well under a second, <code>{\"orders\": 50}</code>, and an Invocations sum around 51 (metrics can lag a minute or two).'),
    (['Run the burst, then [[Application Insights]] → [[Live metrics]] / [[Performance]] shows request rate and response times.'],
     "for i in $(seq 50); do curl -s -o /dev/null -w '%{http_code} %{time_total}\\n' -X POST $URL/ -H 'content-type: application/json' -d '{\"dish\":\"thali\"}' & done; wait\ncurl -s $URL/; echo",
     '<code>201</code> responses (the first may be slow while F1 warms up) and an order count. On F1 the in-memory count resets when the app restarts — exactly why the capstone design uses a database.'),
    (['Run the burst, then [[Cloud Run]] → <code>canteen</code> → [[Metrics]]: request count, latency, instance count scaling up and back to zero.'],
     "for i in $(seq 50); do curl -s -o /dev/null -w '%{http_code} %{time_total}\\n' $URL & done; wait\ngcloud run services describe canteen --region asia-south1 --format='value(status.url,status.latestReadyRevisionName)'",
     '<code>200</code> responses and the service URL and revision; the Metrics tab shows the burst and instances scaling (max 3 as set in the template).')),
    'Put a screenshot of these metrics in your report — evidence beats claims.')

STEP3 = ('3 · Tear down from code and prove the account is clean', tri(
    (['[[CloudFormation]] → stack <code>canteen</code> → [[Delete]]; the function URL and permissions go with the function.', 'Check [[Resource Groups &amp; Tag Editor]] for anything still tagged <code>project=canteen</code>.'],
     "aws cloudformation delete-stack --stack-name canteen --region ap-south-1\naws cloudformation wait stack-delete-complete --stack-name canteen --region ap-south-1\naws resourcegroupstaggingapi get-resources --tag-filters Key=project,Values=canteen --region ap-south-1 --query 'length(ResourceTagMappingList)'",
     '<code>0</code> — nothing tagged canteen remains (the tagging API can show deleted resources for a short while; re-check after a few minutes).'),
    (['[[Resource groups]] → <code>rg-canteen</code> → [[Delete resource group]] → type the name.'],
     'az group delete -n rg-canteen --yes\naz resource list --tag project=canteen --query "length(@)"',
     '<code>0</code>.'),
    (['In Cloud Shell: <code>terraform destroy</code>.'],
     "terraform destroy -auto-approve -input=false -var project=$(gcloud config get-value project) | tail -1\ngcloud run services list --region asia-south1 --filter='metadata.name=canteen' --format='value(metadata.name)' | wc -l",
     '<code>Destroy complete! Resources: 3 destroyed.</code> and <code>0</code>.')),
    'A clean teardown is part of the grade: it proves everything was in code and nothing will bill you later.')

prac = practical(OWN_INTRO + ' You deploy a reference version of the capstone from a template, load it with a lunch-rush burst, observe it, and delete everything from code. Expected cost: zero to a few rupees.', [SETUP_STEP, STEP1, STEP2, STEP3],
    cleanup='Step 3 is the cleanup. Also delete local files if you like: <code>canteen.yaml</code>, <code>main.bicep</code>, <code>app.zip</code>, the <code>canteen/</code> folder.')

mist = mistakes([
    ['Starting with services.', 'Excitement.', 'Requirements and numbers first.'],
    ['Over-engineering (Kubernetes, multi-region) for 3,000 users.', 'CV value.', 'Size to the peak maths and budget.'],
    ['No rejected alternatives.', 'Only one idea.', 'One ADR per major choice.'],
    ['Security as a last slide.', 'Time pressure.', 'Design identity and data protection from week 1.'],
    ['Cost without assumptions.', 'Guessing.', 'Usage model + calculator + budget.'],
    ['Hand-built resources.', 'Console is quicker once.', 'Everything in IaC; prove teardown.']])

cert = table(['Exam / syllabus', 'How the capstone helps'], [['C-DAC PGCP-BDA', 'Project work: design and deploy a cloud solution.'], ['AWS CLF-C02', 'Applies Well-Architected, services, pricing and security together.'], ['AZ-900', 'Combines core services, governance and cost management.'], ['Google Cloud Digital Leader', 'Business-to-technology translation and modernisation choices.']], minw=560) + \
    qx('1. Which requirement type is “99.5% availability during lunch”?', ['non-functional', 'functional', 'constraint only', 'none'], 0, 'NFR.') + \
    qx('2. Best compute for a 20-minute daily peak with near-zero idle cost?', ['serverless functions', 'always-on VM cluster', 'dedicated hosts', 'mainframe'], 0, 'Serverless.') + \
    qx('3. What makes resources easy to recreate and delete?', ['infrastructure as code', 'screenshots', 'manual notes', 'bigger VMs'], 0, 'IaC.') + \
    qx('4. Which document records a design choice and its alternatives?', ['ADR', 'SLA', 'CVE', 'SBOM'], 0, 'ADR.') + \
    qx('5. What should a cost estimate always include?', ['assumptions and usage model', 'only the total', 'logos', 'nothing'], 0, 'Assumptions.') + \
    qx('6. Accepting “pay at counter” when payments fail is…', ['graceful degradation', 'vertical scaling', 'sharding', 'tokenisation'], 0, 'Fallback.')

proj = miniproject('The capstone itself',
    'Deliver the campus canteen pre-order system (or another brief from the deep dive).',
    ['<b>Requirements:</b> functional, non-functional with numbers, constraints.',
     '<b>Architecture:</b> overview + detailed diagram with numbered flows and boundaries.',
     '<b>Services:</b> choices with one rejected alternative each (ADRs).',
     '<b>Security, reliability, cost:</b> one page each, using the templates above.',
     '<b>Build:</b> IaC + pipeline + monitoring; practical steps 1–3 as the starting point; replace the demo storage with a real database.',
     '<b>Demo:</b> 10-minute presentation with live system, metrics and teardown.'],
    'A design document, an IaC repository, evidence screenshots and a recorded 10-minute demo.', 'The whole course.')

assemble_v2(HERE, story_h2='The canteen queue', hook_html=hk,
    narration='Every lunch break the college canteen had a 30-minute queue. The principal challenged the cloud batch to design a pre-order system for 3,000 students — safe, fast and within ₹5,000 a month.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Capstone: design a cloud solution',
    formal='A <b>cloud solution design</b> translates business needs into a documented, justified and deployable architecture: measurable requirements and constraints, an architecture with data flows and trust boundaries, service selections with trade-offs, security and compliance controls, reliability and recovery plans, a cost model with guard-rails, and an operating model with infrastructure as code, CI/CD and monitoring — validated by building, testing and tearing down a working version.',
    simple='Plan a real cloud system from the needs to the running version: what it must do, how it is built, why, how safe and reliable it is, what it costs, and how it is run.',
    interview=['“I start from requirements in numbers — the canteen peak was only 2 orders per second — then compare two designs, pick serverless with NoSQL for idle cost and team size, and document why I rejected Kubernetes.”', '“I deploy from CloudFormation/Bicep/Terraform, prove it with a load burst and alarms, and tear it down from code.”'],
    terms_rows=[('Functional requirement', 'What the system does.'), ('Non-functional requirement', 'How well (latency, uptime).'), ('Constraint', 'Budget, rules, skills.'), ('ADR', 'Decision record.'), ('Graceful degradation', 'Core works when parts fail.'), ('Usage model', 'Quantities behind cost.'), ('IaC', 'Infrastructure from code.'), ('Teardown', 'Delete everything cleanly.')],
    exam='Capstones mirror exam scenario questions: identify requirements, pick the right service, apply security and cost best practices.',
    picture_h2='Reference architecture and marking guide', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven deliverables of a cloud design, one by one', TYPES)],
    how_h2='The capstone, week by week', how_intro='A four-week plan from brief to demo.', how_anim=WEEKS,
    parts_h2='Six things to hand in', parts_html=parts, lv='',
    myth_rows=[('More services = better grade.', 'Justified choices earn marks.', 'Type 3.'), ('Security can be added at the end.', 'Design it from week 1.', 'Type 4.'), ('A demo proves it works.', 'Metrics and teardown prove engineering.', 'Type 7.')],
    extra_secs=[('deep', 'Deep dive', 'Other briefs, peak maths, presentation structure', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Turn a brief into measurable requirements.', 'Produce the seven deliverables of a cloud design.', 'Justify service choices with rejected alternatives.', 'Deploy, load-test, observe and tear down a stack from IaC on your own account.', 'Present a cloud solution in 10 minutes.'],
    next_html='<a href="../02-practice-exam-cloud-concepts-mcq/">11.2 Practice exam: cloud concepts (MCQ)</a>.',
    pre='<b>Before you start:</b> Modules 1–10.')
