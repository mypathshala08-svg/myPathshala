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


hk = hook('Riya scored 82% on her practice test but failed the real exam by four marks. She knew the content. What went wrong?',
    'She read questions too fast, missed words like <b>“most cost-effective”</b> and <b>“least operational effort”</b>, and changed right answers to wrong ones. This lesson teaches the <b>seven question styles</b> cloud fundamentals exams use, a step-by-step method for answering any MCQ, and gives you a <b>60-question practice exam</b> with explanations mapped to AWS CLF-C02, AZ-900, Google Cloud Digital Leader and the C-DAC PGCP-BDA syllabus. On <b>your own</b> account you then verify a few exam facts so they stick.',
    ['Keywords that decide the answer: cheapest, least effort, most secure, highly available.', 'How to eliminate two options in ten seconds.', 'Why the “best” answer is often the managed service.'])

def story_scene():
    o = t(180, 12, 'Knowing vs scoring', 9, 'ink', bold=True)
    o += box(8, 28, 160, 74, 'amber', rx=8) + t(88, 48, 'Practice: 82%', 8.4, 'ink', bold=True) + t(88, 64, 'untimed, open notes', 7, 'ink2') + t(88, 78, 'skimmed keywords', 7, 'ink2') + t(88, 92, 'false confidence', 7.4, 'ink', bold=True)
    o += box(192, 28, 160, 74, 'green', rx=8) + t(272, 48, 'Method + timing', 8.4, 'ink', bold=True) + t(272, 64, 'read the ask twice', 7, 'ink2') + t(272, 78, 'eliminate, then choose', 7, 'ink2') + t(272, 92, 'pass with margin', 7.4, 'ink', bold=True)
    o += t(180, 122, 'Exam skill is a separate skill — practise it', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Left: practice 82% untimed with skimmed keywords gives false confidence. Right: method and timing — read the ask twice, eliminate then choose — passes with margin.', story_scene(), 'Practise the <tspan font-weight="700" class="s-acc">method</tspan>, not only the facts.', h=132)
dialogue = '''R> Sir, one question asked for the “most cost-effective” option. I picked the most reliable one.
A> Both were valid designs — the keyword decided the answer. Exams test whether you read the requirement.
K> And the “select TWO” questions?
A> Each option is true or false on its own. Never pick two that say the same thing.
R> How do I practise?
A> Timed sets, then review every explanation — including for the ones you got right. Let’s start with the question styles.'''

def methodfig():
    o = t(320, 16, 'A 5-step method for any cloud MCQ', 11, 'ink', bold=True)
    S = [('1', 'Read the ask', 'last line first', 'blue'), ('2', 'Circle keywords', 'cheapest, least effort…', 'amber'), ('3', 'Eliminate', 'wrong service, wrong scope', 'red'), ('4', 'Choose best fit', 'managed > DIY', 'green'), ('5', 'Flag + move', 'review at the end', 'violet')]
    for i, (n, a, b, tn) in enumerate(S):
        x = 12 + i * 126
        o += box(x, 36, 118, 80, tn, rx=8) + pin(x + 14, 50, n) + t(x + 59, 74, a, 8.2, 'ink', bold=True) + t(x + 59, 94, b, 6.8, 'ink2')
        if i < 4: o += arrow(x + 118, 76, x + 126, 76)
    o += t(320, 140, 'About 60–90 seconds per question; flag anything over two minutes and come back.', 7.4, 'ink2')
    return o
METHOD = bigfig('Five steps: read the ask (last line first), circle keywords, eliminate wrong options, choose the best fit (managed over do-it-yourself), flag and move on.', methodfig(), h=150)

picture = ('  <p>The method that turns knowledge into marks:</p>\n' + METHOD +
           '\n  <h3>The three exams at a glance (check official guides for current details)</h3>\n' + table(['', 'AWS CLF-C02', 'Microsoft AZ-900', 'Google Cloud Digital Leader'], [
               ['Domains', 'Cloud Concepts 24% · Security & Compliance 30% · Cloud Technology & Services 34% · Billing, Pricing & Support 12%', 'Cloud concepts · Azure architecture and services · Azure management and governance', 'Digital transformation · data · AI/ML · infrastructure and application modernisation · security and operations'],
               ['Questions', '65 (50 scored), 90 minutes', 'around 40–60, 45 minutes', 'around 50–60, 90 minutes'], ['Pass mark', '700 / 1000 (scaled)', '700 / 1000 (scaled)', 'pass/fail'], ['Style', 'multiple choice + multiple response', 'multiple choice, yes/no series, drag-and-drop', 'multiple choice + multiple select']], minw=680))

RN = {'q': (4, 54, 50, 50, 'app', 'Question', 'read'), 'ask': (66, 4, 62, 46, 'meter', 'The ask', 'last line'), 'kw': (66, 104, 62, 46, 'gear', 'Keywords', 'cheapest?'),
      'el': (142, 54, 60, 50, 'shield', 'Eliminate', '2 options out'), 'fit': (216, 4, 62, 46, 'cloud', 'Best fit', 'managed'), 'flag': (216, 104, 62, 46, 'chart', 'Flag', 'if unsure'), 'ans': (292, 54, 64, 50, 'user', 'Answer', 'move on')}
RS = [dict(on=['q'], hot='q', move=None, head='Step 1 · A scenario question', text='“A start-up wants to run code in response to S3 uploads without managing servers, with', text2='the LEAST operational overhead. Which service should it use?”', svc='Long stem, one decisive phrase'),
      dict(on=['q', 'ask'], hot='ask', move=(54, 79, 72, 30, 'read'), head='Step 2 · Read the ask first', text='“Which service should it use?” → one compute service. Now read the stem looking only', text2='for requirements.', svc='Last line first saves re-reading'),
      dict(on=['ask', 'kw'], hot='kw', move=(97, 50, 97, 104, 'circle'), head='Step 3 · Circle the keywords', text='“in response to uploads” (event-driven), “without managing servers”, “LEAST operational', text2='overhead”.', svc='Keywords map to service properties'),
      dict(on=['kw', 'el'], hot='el', move=(128, 27, 160, 54, 'remove'), head='Step 4 · Eliminate', text='Options: EC2, Lambda, Elastic Beanstalk, Lightsail. EC2 and Lightsail = servers to manage →', text2='out. Beanstalk manages servers for you but still runs instances.', svc='Two options gone in seconds'),
      dict(on=['el', 'fit'], hot='fit', move=(165, 54, 216, 20, 'choose'), head='Step 5 · Choose the best fit', text='Lambda: event-driven, serverless, least operational overhead → answer.', text2='Rule of thumb: “least effort” usually means the most managed option.', svc='Serverless/managed beats DIY for least-effort questions'),
      dict(on=list(RN), hot='ans', move=(278, 127, 298, 90, 'next'), head='Step 6 · Answer, flag if unsure, move on', text='Confident → answer and go. Unsure → best guess, flag, return at the end. Never leave', text2='blanks: there is no negative marking on these exams.', svc='Keep pace: ~1 minute per question')]
SOLVE = flow_anim('Solving one exam question, step by step', 'The method applied to a typical CLF-C02 scenario.', 'MCQ method', 'Animation: read the scenario; read the ask; circle keywords; eliminate options; choose the managed best fit; answer, flag if unsure, move on.', RN, RS, hid='mcqflow')

def mapfig():
    o = t(320, 16, 'Seven question styles', 11, 'ink', bold=True)
    items = [('1', 'Definition', 'what is X?', 'blue'), ('2', 'Which service?', 'use case → service', 'amber'), ('3', 'Shared responsibility', 'who does what', 'red'), ('4', 'Cost-optimised', 'cheapest / pricing model', 'green'),
             ('5', 'Security best practice', 'most secure way', 'red'), ('6', 'Architecture benefit', 'HA, elasticity, global', 'violet'), ('7', 'Multiple response', 'select TWO/THREE', 'card')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 8, 'ink', bold=True) + t(x + 78, y + 54, b, 6.6, 'ink2')
    o += t(320, 210, 'Recognise the style and you already know what kind of answer is wanted.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of seven question styles: definition, which service, shared responsibility, cost-optimised, security best practice, architecture benefit, multiple response.', mapfig(), h=222)

def qs(n, name, tone, d, an, ex_q, tip, A, trap, plain, how, words, diff, rw, pro):
    return vt(n, name, tone, d, an, ex_q, tip, '', A, 'you recognise this style in a question.', trap, plain, how, words, diff, ['CLF-C02', 'AZ-900', 'Cloud Digital Leader'], rw, pro)

A1 = mk(['Term in stem', 'Recall meaning', 'Match option'], ['term|“elasticity”|“CapEx”', 'recall|precise definition|not near-synonym', 'match|exact wording|avoid look-alikes'], ['blue', 'amber', 'green'],
        ['the stem names or describes a concept', 'recall the precise definition from the course', 'pick the option that matches exactly'],
        [('Spot', 'The question names or describes a concept.', ''), ('Recall', 'Precise definition, not a near-synonym.', ''), ('Match', 'Choose the exact match; avoid look-alikes.', '')],
        'Definition questions', 'Precise words win.', 'Definition', 'Animation: term in stem; recall; match.', 'q1anim')
T1 = qs(1, 'Definition questions', 'blue',
    '<b>Definition questions</b> test whether you know the precise meaning of a concept — elasticity vs scalability, CapEx vs OpEx, Region vs Availability Zone, high availability vs fault tolerance — often with near-synonyms as distractors.',
    'Spelling bee words that sound alike: “affect” and “effect” are both real words, only one fits.',
    'Example: “Which term describes automatically adding and removing resources to match demand?” → elasticity (not scalability, which can be manual and long-term).',
    'Tip: build a glossary from every lesson’s “Words used” boxes and quiz yourself with near-synonym pairs.', A1,
    'two options are both “sort of right” — the precise term wins.',
    'Questions asking you to identify a concept from its definition.',
    [('Read', 'Underline the defining phrase.'), ('Recall', 'Your glossary definition.'), ('Compare', 'Near-synonyms side by side.'), ('Choose', 'Exact match.'), ('Review', 'Add misses to glossary.')],
    [('distractor', 'a wrong option designed to look right'), ('near-synonym', 'a word with a close but different meaning'), ('stem', 'the question text')],
    table(['Pair', 'Difference'], [['Scalability vs elasticity', 'capacity growth vs automatic matching to demand'], ['HA vs fault tolerance', 'minimal downtime vs no interruption'], ['Region vs AZ', 'geographic area vs isolated data centres inside it']], minw=440),
    'Elasticity vs scalability and CapEx vs OpEx appear in almost every fundamentals exam.',
    'If two options are true statements, ask which one answers the exact question asked.')

A2 = mk(['Use case', 'Service family', 'Specific service'], ['need|store files|run code on events', 'family|object storage|functions', 'service|S3 / Blob / GCS|Lambda'], ['amber', 'blue', 'green'],
        ['the stem describes a need', 'map it to a service family', 'then to the provider’s specific service'],
        [('Need', 'Identify the job to be done.', ''), ('Family', 'Map to compute/storage/DB/network family.', ''), ('Service', 'Pick the provider service.', '')],
        'Which-service questions', 'Need → family → name.', 'Which service', 'Animation: use case; service family; specific service.', 'q2anim')
T2 = qs(2, '“Which service?” questions', 'amber',
    '<b>Which-service questions</b> describe a use case and ask for the most suitable service, often listing services from the same provider with overlapping features; the fastest route is need → service family → specific service.',
    'A hardware shop: “I need to hang a picture” → fixings → wall plug and screw, not a drill press.',
    'Example: “Which service records API calls for auditing?” → AWS CloudTrail (not CloudWatch, which is metrics/logs/alarms).',
    'Tip: use the translation table from Lesson 10.2 and the “Which service?” check-yourself boxes in every lesson.', A2,
    'similar-sounding services (CloudTrail vs CloudWatch, Inspector vs GuardDuty).',
    'Questions describing a need and asking which cloud service to use.',
    [('Need', 'One-line job.'), ('Family', 'Compute, storage, DB, network, security, ops.'), ('Specific', 'Exact service.'), ('Check', 'Managed? Region? scope?'), ('Choose', '—')],
    [('family', 'group of services for one kind of job'), ('managed service', 'provider runs the infrastructure'), ('scope', 'global, regional or zonal')],
    table(['Confusing pair', 'How to tell'], [['CloudTrail vs CloudWatch', 'who did what vs performance metrics'], ['Inspector vs GuardDuty', 'vulnerabilities vs threats'], ['Azure Policy vs RBAC', 'what resources may look like vs who may act']], minw=440),
    'Look-alike pairs are a favourite of every fundamentals exam because they test real understanding.',
    'Make a two-column “confusing pairs” sheet — it fixes most which-service mistakes.')

A3 = mk(['Layer named', 'Service model', 'Owner'], ['layer|guest OS|data, IAM', 'model|IaaS / PaaS|SaaS', 'owner|customer|or provider'], ['red', 'amber', 'green'],
        ['identify the layer (hardware, OS, data…)', 'identify the service model of the service', 'decide the owner from the model'],
        [('Layer', 'Which layer is in question?', ''), ('Model', 'IaaS, PaaS, SaaS or serverless?', ''), ('Owner', 'Provider or customer — or shared.', '')],
        'Shared-responsibility questions', 'Layer + model = owner.', 'Shared responsibility', 'Animation: layer; model; owner.', 'q3anim')
T3 = qs(3, 'Shared-responsibility questions', 'red',
    '<b>Shared-responsibility questions</b> ask who is responsible for a task — patching, physical security, data encryption choices, IAM, network rules — for a specific service; answer by identifying the layer and the service model (Lesson 9.1).',
    'A rented flat: the building owner fixes the lift; you lock your own door.',
    'Example: “Who patches the guest OS on EC2?” → the customer. “Who patches the RDS engine?” → AWS.',
    'Tip: data, identities and access are always the customer’s; physical and hypervisor layers are always the provider’s.', A3,
    'the same task belongs to different owners for different services.',
    'Questions asking whether the provider or the customer is responsible for something.',
    [('Layer', 'Physical, network, hypervisor, OS, app, data, IAM.'), ('Service', 'EC2 / RDS / Lambda / S3…'), ('Model', 'IaaS/PaaS/SaaS.'), ('Owner', 'Apply the line.'), ('Shared?', 'Patching, config, training.')],
    [('inherited control', 'fully provider'), ('shared control', 'split by layer'), ('customer-specific control', 'only customer')],
    table(['Task', 'EC2', 'RDS', 'Lambda'], [['OS patching', 'customer', 'AWS', 'AWS'], ['Data encryption choice', 'customer', 'customer', 'customer'], ['IAM permissions', 'customer', 'customer', 'customer']], minw=440),
    'Domain 2 (Security and Compliance) is the largest-but-one CLF-C02 domain at 30%, and shared responsibility is its core.',
    'If the option says “the provider is responsible for the customer’s data/IAM”, it is wrong — in every model.')

A4 = mk(['Usage pattern', 'Pricing model', 'Cheapest fit'], ['pattern|steady|spiky, interruptible', 'model|on-demand|commit, spot', 'answer|cheapest that|meets requirement'], ['green', 'amber', 'blue'],
        ['read the usage pattern: steady, spiky, interruptible, short-term', 'map it to a pricing model', 'choose the cheapest option that still meets every requirement'],
        [('Pattern', 'Steady 24×7? Short? Interruptible?', ''), ('Model', 'On-demand, commitments, spot, free tier.', ''), ('Choose', 'Cheapest that meets requirements.', '')],
        'Cost questions', 'Cheapest that still works.', 'Cost-optimised', 'Animation: usage pattern; pricing model; cheapest fit.', 'q4anim')
T4 = qs(4, 'Cost-optimised and pricing questions', 'green',
    '<b>Cost questions</b> ask for the most cost-effective option or the right pricing model for a usage pattern: steady workloads → commitments (Savings Plans, reservations, committed use); interruptible batch → Spot; short or unpredictable → on-demand or serverless; plus tools such as pricing calculators, budgets and cost explorers.',
    'Mobile plans: daily commuters buy a monthly pass, occasional riders pay per trip, flexible travellers wait for discounted off-peak seats.',
    'Example: “A batch job can be interrupted and restarted; which option is cheapest?” → Spot Instances.',
    'Tip: “cheapest” never overrides an explicit requirement (e.g. “must not be interrupted” rules out Spot).', A4,
    'steady vs interruptible vs unknown usage determines the model.',
    'Questions asking for the cheapest option or right pricing model.',
    [('Pattern', 'Duration, steadiness, interruption tolerance.'), ('Model', 'On-demand, commit, spot, serverless.'), ('Tools', 'Calculator, budgets, Cost Explorer.'), ('Check', 'Requirements still met?'), ('Choose', '—')],
    [('Savings Plan', 'AWS commitment discount'), ('Spot', 'spare capacity at large discount, can be interrupted'), ('TCO', 'total cost of ownership')],
    table(['Pattern', 'Best model'], [['Steady 24×7 for 1–3 years', 'commitment discount'], ['Interruptible batch', 'Spot'], ['Spiky/unknown', 'on-demand or serverless']], minw=420),
    'Billing, Pricing and Support is 12% of CLF-C02; Azure and Google exams test the equivalent tools and models.',
    'Watch for the support-plan questions: which plan gives a technical account manager or a response time — check the current support plan pages.')

A5 = mk(['Risk named', 'Control family', 'Most secure option'], ['risk|leaked keys|public data', 'control|IAM, MFA|encryption, guard-rails', 'answer|least privilege|no long-term keys'], ['red', 'blue', 'green'],
        ['identify the risk in the scenario', 'map it to a control family', 'choose the option that removes the risk with least privilege'],
        [('Risk', 'What could go wrong?', ''), ('Control', 'Identity, network, data, detection.', ''), ('Choose', 'Least privilege, no static secrets, managed controls.', '')],
        'Security questions', 'Remove the risk, not just reduce it.', 'Security', 'Animation: risk; control family; most secure option.', 'q5anim')
T5 = qs(5, 'Security best-practice questions', 'red',
    '<b>Security questions</b> ask for the most secure way to do something: grant access, store secrets, protect the root account, encrypt data, detect threats, or meet compliance; good answers use least privilege, roles instead of long-term keys, MFA, managed encryption and detection services.',
    'Lending your car: give the key for one trip (temporary role), not a copy of your house keys (root credentials).',
    'Example: “How should an EC2 app access S3 securely?” → an IAM role (instance profile), not access keys in code.',
    'Tip: options mentioning root user for daily tasks, public buckets, or keys in code are almost always wrong.', A5,
    'the scenario names data, credentials, access or compliance.',
    'Questions asking for the safest way to set something up.',
    [('Risk', 'Identify.'), ('Identity', 'Roles, MFA, least privilege.'), ('Data', 'Encryption, KMS.'), ('Detect', 'GuardDuty, Defender, SCC.'), ('Comply', 'Artifact, reports.')],
    [('root user', 'all-powerful first account identity'), ('instance profile', 'container for an IAM role on EC2'), ('least privilege', 'only required permissions')],
    table(['Wrong pattern', 'Right pattern'], [['root for daily tasks', 'individual users/SSO + MFA'], ['access keys in code', 'IAM role / managed identity'], ['public bucket for sharing', 'pre-signed / SAS / signed URLs']], minw=440),
    'Security & Compliance is 30% of CLF-C02 — the second-largest domain.',
    'When two options are both secure, choose the one that is managed and requires less custom work.')

A6 = mk(['Benefit asked', 'Mechanism', 'Option that delivers'], ['benefit|HA, elasticity|global reach', 'mechanism|multi-AZ|auto scaling, edge', 'answer|design choice|that provides it'], ['violet', 'amber', 'green'],
        ['identify the benefit asked: availability, elasticity, global reach, agility', 'recall the mechanism that provides it', 'choose the design that uses that mechanism'],
        [('Benefit', 'High availability, elasticity, global reach, agility.', ''), ('Mechanism', 'Multi-AZ, auto scaling, edge, managed services.', ''), ('Choose', 'Design that uses the mechanism.', '')],
        'Architecture questions', 'Benefit → mechanism → design.', 'Architecture', 'Animation: benefit asked; mechanism; option that delivers.', 'q6anim')
T6 = qs(6, 'Architecture benefit questions', 'violet',
    '<b>Architecture questions</b> ask how to achieve a quality — high availability, fault tolerance, elasticity, low latency for global users, faster delivery — or which Well-Architected pillar a practice belongs to; the answer links the benefit to a mechanism (multi-AZ, auto scaling, CDN/edge, decoupling with queues, IaC).',
    'Building a bridge: “carry more trucks” → wider deck; “survive one pillar failing” → extra pillars; “faster crossing for distant towns” → more bridges.',
    'Example: “How to make a web app highly available?” → deploy across multiple Availability Zones behind a load balancer.',
    'Tip: multi-Region is for disaster recovery or global latency; multi-AZ is the usual answer for high availability.', A6,
    'the stem asks for availability, scale, latency, resilience or a pillar.',
    'Questions about how to make a system reliable, scalable or fast.',
    [('Benefit', 'What quality?'), ('Mechanism', 'AZs, scaling, CDN, queues.'), ('Scope', 'AZ vs Region vs global.'), ('Pillar', 'Which Well-Architected pillar?'), ('Choose', '—')],
    [('multi-AZ', 'across several data centres in one Region'), ('decoupling', 'separating parts with queues/events'), ('pillar', 'Well-Architected category')],
    table(['Benefit', 'Typical mechanism'], [['High availability', 'multi-AZ + load balancer'], ['Elasticity', 'auto scaling / serverless'], ['Global low latency', 'CDN / edge locations'], ['Disaster recovery', 'multi-Region backups/standby']], minw=440),
    'Cloud Concepts (24% of CLF-C02) includes the benefits of cloud and Well-Architected design principles.',
    'Memorise the pillar names for each provider (Lesson 7.1): exams ask “which pillar?” directly.')

A7 = mk(['Count required', 'Judge each option', 'Pick distinct truths'], ['count|select TWO|select THREE', 'judge|true/false each|independently', 'pick|distinct|no duplicates'], ['card', 'amber', 'green'],
        ['note how many answers are required', 'judge every option independently as true or false', 'choose the required number of distinct true options'],
        [('Count', 'How many answers are required?', ''), ('Judge', 'Each option true or false on its own.', ''), ('Pick', 'Distinct true options; no duplicates.', '')],
        'Multiple-response questions', 'Each option is its own mini-question.', 'Multiple response', 'Animation: count required; judge each option; pick distinct truths.', 'q7anim')
T7 = qs(7, 'Multiple-response (select TWO / THREE)', 'card',
    '<b>Multiple-response questions</b> require selecting a stated number of correct options; partial credit is usually not given, so each option must be judged independently and the final set must contain distinct, fully correct statements.',
    'A team selection: each player must earn a place on their own merit — two players for the same position is a wasted pick.',
    'Example: “Which TWO are benefits of cloud? (select TWO)” → trade CapEx for variable expense; go global in minutes (not “eliminate all security responsibilities”).',
    'Tip: if two options mean the same thing, at most one is in the answer — usually neither.', A7,
    'the stem says “select TWO/THREE” or “choose all that apply”.',
    'Questions where you must choose more than one answer.',
    [('Count', 'Required number.'), ('Judge', 'True/false per option.'), ('Remove', 'Absolutes (“always”, “all”).'), ('Distinct', 'No duplicates.'), ('Check', 'Count again.')],
    [('partial credit', 'marks for some correct answers — usually not given'), ('absolute wording', '“always”, “never”, “all” — often false'), ('multiple response', 'select more than one')],
    table(['', 'Multiple choice', 'Multiple response'], [['Answers', 'one', 'two or more'], ['Scoring', 'all or nothing', 'all or nothing'], ['Strategy', 'best single', 'independent true/false']], minw=420),
    'CLF-C02 states it uses multiple-choice and multiple-response questions; the response count is always given.',
    'Options with absolutes (“eliminates all”, “never requires”) are rarely correct in cloud exams.')

SUMMARY = table(['#', 'Style', 'Signal in the stem', 'Winning move'], [
    ['1', 'Definition', '“which term describes…”', 'precise definition'], ['2', 'Which service', '“which service should…”', 'need → family → service'], ['3', 'Shared responsibility', '“who is responsible…”', 'layer + model'],
    ['4', 'Cost', '“most cost-effective”', 'pattern → pricing model'], ['5', 'Security', '“most secure”', 'least privilege, roles, managed'], ['6', 'Architecture', '“highly available / scalable”', 'benefit → mechanism'], ['7', 'Multiple response', '“select TWO”', 'independent true/false']], minw=600)

TYPES = ('  <p>Seven question styles, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, real-world example, a sample question and an expert tip.</p>\n'
         + challenge(['Which keyword makes Spot the right answer — and which rules it out?', 'Who patches the RDS database engine?', 'What is the usual answer for “highly available”?'], 'types 4, 3 and 6') + MAP
         + jump(['Definition', 'Service', 'Responsibility', 'Cost', 'Security', 'Architecture', 'Multi-response']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY)

# ------------------------------------------------------------------ the practice exam
def sec_q(title, items):
    return f'  <h3>{title}</h3>\n' + ''.join(qx(q, o, a, w) for q, o, a, w in items)

EXAM_A = sec_q('Part A · Cloud concepts (15 questions)', [
    ('A1. Which NIST characteristic lets users provision resources without human interaction with the provider?', ['broad network access', 'on-demand self-service', 'resource pooling', 'measured service'], 1, 'On-demand self-service (Lesson 1.1).'),
    ('A2. Paying monthly for what you use instead of buying servers upfront is a shift from…', ['OpEx to CapEx', 'CapEx to OpEx', 'SaaS to IaaS', 'private to public'], 1, 'Capital expense → operational expense.'),
    ('A3. Automatically adding and removing capacity to match demand is…', ['scalability', 'elasticity', 'durability', 'agility'], 1, 'Elasticity (Lesson 5.3).'),
    ('A4. Which service model gives the customer the most control over the operating system?', ['SaaS', 'PaaS', 'IaaS', 'FaaS'], 2, 'IaaS (Lesson 2.1).'),
    ('A5. Gmail used by a company is an example of…', ['IaaS', 'PaaS', 'SaaS', 'CaaS'], 2, 'Finished software = SaaS.'),
    ('A6. A company keeps its database on-premises and runs its web tier in a public cloud, connected privately. This is…', ['community cloud', 'hybrid cloud', 'multi-cloud', 'private cloud'], 1, 'Hybrid (Lesson 3.1).'),
    ('A7. Using AWS and Google Cloud together, with no on-premises systems, is…', ['hybrid', 'multi-cloud', 'community', 'sovereign'], 1, 'Multi-cloud (Lesson 3.3).'),
    ('A8. A Region contains…', ['one data centre', 'multiple isolated Availability Zones', 'only edge locations', 'one country'], 1, 'Lesson 5.1.'),
    ('A9. Processing sensor data on the device to reduce latency is…', ['grid computing', 'edge computing', 'utility computing', 'cluster computing'], 1, 'Lesson 3.4.'),
    ('A10. Which is a benefit of economies of scale in the cloud?', ['higher prices', 'lower variable costs due to provider scale', 'no need for security', 'unlimited free usage'], 1, 'Providers pass on scale savings.'),
    ('A11. Hypervisors that run directly on hardware are…', ['Type 1', 'Type 2', 'containers', 'emulators'], 0, 'Bare-metal hypervisors (Lesson 4.1).'),
    ('A12. Containers differ from VMs mainly because containers…', ['include a full guest OS', 'share the host OS kernel', 'cannot run Linux', 'are always slower'], 1, 'Lesson 4.5.'),
    ('A13. Many customers sharing the same physical infrastructure securely is…', ['multitenancy', 'single tenancy', 'colocation', 'replication'], 0, 'Lesson 5.2.'),
    ('A14. Which migration strategy moves an app to VMs without code changes?', ['refactor', 'rehost', 'repurchase', 'retire'], 1, 'Lift and shift (Lesson 2.5).'),
    ('A15. An SLA of 99.9% monthly allows roughly how much downtime?', ['4 minutes', '43 minutes', '7 hours', '3 days'], 1, '0.1% of ~43,200 minutes (Lesson 5.4).')])

EXAM_B = sec_q('Part B · Security and compliance (15 questions)', [
    ('B1. Under the shared responsibility model, who is responsible for physical data-centre security?', ['customer', 'provider', 'both equally', 'auditors'], 1, 'Security of the cloud.'),
    ('B2. Who patches the guest OS on an IaaS VM?', ['provider', 'customer', 'nobody', 'the hypervisor'], 1, 'IaaS: customer.'),
    ('B3. Most secure way for an app on a VM to read cloud storage?', ['access keys in code', 'a role / managed identity', 'root credentials', 'a public bucket'], 1, 'Lesson 9.4.'),
    ('B4. Which AWS service records who made which API call?', ['CloudWatch', 'CloudTrail', 'Inspector', 'Config'], 1, 'Audit trail.'),
    ('B5. Which AWS service detects threats such as calls from malicious IPs?', ['GuardDuty', 'Artifact', 'Macie', 'Shield'], 0, 'Lesson 9.2.'),
    ('B6. Where are AWS compliance reports (SOC, ISO) downloaded?', ['AWS Artifact', 'AWS Config', 'Trusted Advisor', 'CloudFront'], 0, 'Lesson 9.1.'),
    ('B7. In AWS policy evaluation, an explicit deny…', ['is overridden by allow', 'always wins', 'only applies to root', 'is ignored'], 1, 'Lesson 9.4.'),
    ('B8. Azure feature that requires MFA depending on sign-in risk and location?', ['Conditional Access', 'Azure Advisor', 'Resource locks', 'Arc'], 0, 'Entra ID.'),
    ('B9. Which service manages encryption keys in AWS?', ['KMS', 'Shield', 'Macie', 'Route 53'], 0, 'Key Management Service.'),
    ('B10. Which AWS service discovers personal data in S3?', ['Macie', 'GuardDuty', 'Inspector', 'WAF'], 0, 'Lesson 9.3.'),
    ('B11. India’s CERT-In directions require reporting specified incidents within…', ['6 hours', '72 hours', '7 days', '30 days'], 0, 'April 2022 directions.'),
    ('B12. India’s personal data protection law is…', ['DPDP Act 2023', 'HIPAA', 'SOX', 'PCI DSS'], 0, 'Lesson 9.3.'),
    ('B13. Free baseline DDoS protection on AWS is…', ['Shield Standard', 'Shield Advanced', 'WAF Premium', 'GuardDuty'], 0, 'Automatic for all customers.'),
    ('B14. Google Cloud’s DDoS and WAF service is…', ['Cloud Armor', 'Cloud NAT', 'Cloud CDN', 'Cloud Run'], 0, 'Lesson 9.2.'),
    ('B15. Which practice best protects the AWS root user?', ['use it daily', 'enable MFA and avoid access keys', 'share it with admins', 'store keys in Git'], 1, 'Lesson 9.4.')])

EXAM_C = sec_q('Part C · Services and technology (20 questions)', [
    ('C1. AWS service to run code without servers in response to events?', ['EC2', 'Lambda', 'Lightsail', 'Outposts'], 1, 'FaaS.'),
    ('C2. Azure equivalent of Amazon S3?', ['Blob Storage', 'Azure Files', 'Cosmos DB', 'Managed Disks'], 0, 'Lesson 10.2.'),
    ('C3. Google’s serverless data warehouse?', ['BigQuery', 'Bigtable', 'Dataproc', 'Spanner'], 0, 'Lesson 10.2.'),
    ('C4. AWS managed relational database service?', ['RDS', 'DynamoDB', 'Redshift', 'ElastiCache'], 0, 'Managed SQL.'),
    ('C5. AWS NoSQL key-value database?', ['DynamoDB', 'Aurora', 'Neptune', 'Athena'], 0, 'Lesson 10.2.'),
    ('C6. Which AWS service is a CDN?', ['CloudFront', 'Route 53', 'Direct Connect', 'Global Accelerator only'], 0, 'Content delivery.'),
    ('C7. Which AWS service is DNS?', ['Route 53', 'CloudFront', 'VPC', 'API Gateway'], 0, 'DNS.'),
    ('C8. Private, isolated network in AWS?', ['VPC', 'IAM', 'S3', 'CloudTrail'], 0, 'Lesson 6.3.'),
    ('C9. Stateful instance-level firewall in AWS?', ['security group', 'network ACL', 'route table', 'internet gateway'], 0, 'SGs are stateful.'),
    ('C10. Dedicated private connection from on-premises to AWS?', ['Direct Connect', 'VPN only', 'CloudFront', 'Snowball'], 0, 'Lesson 3.3.'),
    ('C11. AWS service for infrastructure as code?', ['CloudFormation', 'CloudTrail', 'CloudWatch', 'Config'], 0, 'Lesson 8.3.'),
    ('C12. Which AWS service compiles code and runs tests?', ['CodeBuild', 'CodeDeploy', 'CodeArtifact', 'Cloud9'], 0, 'CI.'),
    ('C13. Azure service to manage servers outside Azure?', ['Azure Arc', 'Azure Bastion', 'Front Door', 'Advisor'], 0, 'Hybrid.'),
    ('C14. AWS service that runs AWS infrastructure in your data centre?', ['Outposts', 'Local Zones', 'Wavelength', 'Snowcone'], 0, 'Lesson 3.2.'),
    ('C15. Google managed Kubernetes?', ['GKE', 'AKS', 'EKS', 'Cloud Run'], 0, 'Lesson 10.2.'),
    ('C16. Which storage class is cheapest for data rarely accessed and kept for years?', ['S3 Standard', 'S3 Glacier Deep Archive', 'EBS gp3', 'instance store'], 1, 'Lesson 6.2.'),
    ('C17. Data on instance store is lost when…', ['the instance is stopped or terminated', 'a snapshot is taken', 'IAM changes', 'never'], 0, 'Ephemeral.'),
    ('C18. Which AWS service monitors metrics and triggers alarms?', ['CloudWatch', 'CloudTrail', 'Artifact', 'Organizations'], 0, 'Lesson 8.1.'),
    ('C19. Sending 10% of traffic to a new version first is…', ['canary', 'blue/green', 'recreate', 'rolling'], 0, 'Lesson 8.2.'),
    ('C20. Azure container service that scales to zero without managing Kubernetes?', ['Container Apps', 'AKS only', 'Batch', 'VM Scale Sets'], 0, 'Lesson 6.1.')])

EXAM_D = sec_q('Part D · Billing, pricing, support and governance (10 questions)', [
    ('D1. Cheapest option for interruptible batch jobs?', ['On-Demand', 'Spot', 'Dedicated Hosts', 'Reserved for 3 years'], 1, 'Lesson 5.5.'),
    ('D2. Best pricing for a steady 24×7 workload for 3 years?', ['On-Demand', 'Savings Plans / reservations', 'Spot', 'free tier'], 1, 'Commitment.'),
    ('D3. Tool to estimate costs before building?', ['Pricing Calculator', 'CloudTrail', 'Inspector', 'GuardDuty'], 0, 'Lesson 5.5.'),
    ('D4. Which helps allocate costs to departments?', ['tags / labels', 'security groups', 'route tables', 'AMIs'], 0, 'Lesson 10.3.'),
    ('D5. Azure level above subscriptions for governance?', ['management groups', 'resource groups', 'tags', 'availability sets'], 0, 'Lesson 10.1.'),
    ('D6. Google’s unit of resources and billing?', ['project', 'account', 'tenancy', 'compartment'], 0, 'Lesson 10.1.'),
    ('D7. AWS service to manage many accounts with central policies?', ['Organizations', 'Artifact', 'Lightsail', 'Glue'], 0, 'SCPs.'),
    ('D8. Which alerts you when spending exceeds a threshold?', ['budgets', 'CloudFront', 'Route 53', 'VPC'], 0, 'Budgets.'),
    ('D9. Which typically incurs data-transfer charges?', ['data in', 'data out to the internet', 'data within one AZ on private IPs', 'none'], 1, 'Egress (Lesson 5.5).'),
    ('D10. AWS service giving best-practice checks across cost, security and performance?', ['Trusted Advisor', 'Artifact', 'Snowball', 'CodeCommit'], 0, 'Lesson 8.1.')])

PRACTICE = ('  <p>Set a <b>60-minute timer</b>, answer all 60 questions without notes, then open each to read the explanation. Score: 45+ ready to book; 36–44 revise weak parts; below 36 revisit the lessons named in the explanations.</p>\n'
            + EXAM_A + EXAM_B + EXAM_C + EXAM_D)

parts = wwu([
    ('Timed practice', 'Full sets under exam time.', 'Builds pace and stamina.', '60 questions / 60 minutes here.'),
    ('Explanation review', 'Read why each answer is right.', 'Turns mistakes into knowledge.', 'Lesson links in each explanation.'),
    ('Confusing-pairs sheet', 'Look-alike services side by side.', 'Fixes which-service errors.', 'CloudTrail vs CloudWatch…'),
    ('Official exam guide', 'Domains and weights.', 'Study the right proportions.', 'Provider certification pages.'),
    ('Official practice sets', 'Provider sample questions.', 'Real style and difficulty.', 'Skill Builder, Microsoft Learn, Google sample questions.'),
    ('Exam-day plan', 'Rest, ID, environment, pacing.', 'Avoid avoidable failures.', 'Online proctoring rules.')])

DEEP = ('  <h3>Keyword → answer cheat sheet</h3>\n' + table(['Keyword in stem', 'Usually points to'], [['least operational overhead', 'serverless / fully managed service'], ['most cost-effective, interruptible', 'Spot'], ['steady for 1–3 years', 'commitment discounts'], ['highly available', 'multiple Availability Zones'], ['disaster recovery across geographies', 'multiple Regions'], ['global users, low latency, static content', 'CDN / edge locations'], ['who did what', 'CloudTrail / Activity Log / Audit Logs'], ['performance metrics, alarms', 'CloudWatch / Azure Monitor / Cloud Monitoring'], ['temporary credentials for apps', 'roles / managed identities'], ['compliance reports', 'Artifact / Service Trust Portal / Compliance Reports Manager']], minw=560) +
    '\n  <h3>Exam-day checklist</h3>\n  <ul><li>Online: quiet room, clear desk, ID ready, system test done the day before.</li><li>First pass: answer all, flag doubtful ones; second pass: only flagged.</li><li>Do not change an answer without a clear reason — first instincts are usually right when you knew the topic.</li><li>No negative marking: never leave a question blank.</li></ul>\n'
    '  <h3>Study plan (2 weeks after this course)</h3>\n  <ol><li>Days 1–3: re-read “Check yourself” and certification sections of Modules 1–5.</li><li>Days 4–7: Modules 6–10, confusing-pairs sheet.</li><li>Days 8–10: this 60-question exam + the provider’s official practice set.</li><li>Days 11–13: revise weak domains; repeat both tests.</li><li>Day 14: rest, light review, exam.</li></ol>')

clouds = vendor_tabs('<p><b>AWS:</b> exam guide for CLF-C02, AWS Skill Builder official practice question set and practice exam, Cloud Quest, AWS re:Post for questions.</p>',
    '<p><b>Azure:</b> AZ-900 study guide, free Microsoft Learn practice assessment, learning paths with sandboxes, exam sandbox to try the interface.</p>',
    '<p><b>Google Cloud:</b> Cloud Digital Leader exam guide, sample questions, Cloud Skills Boost learning path and skill badges.</p>') + \
    cloud3([['Exam guide', 'CLF-C02 exam guide', 'AZ-900 study guide', 'CDL exam guide'], ['Free practice', 'Skill Builder practice set', 'Learn practice assessment', 'sample questions'], ['Interface demo', 'exam tutorial', 'exam sandbox', 'exam tutorial'], ['Community', 're:Post', 'Microsoft Q&A', 'Google Cloud community']])

MOCKQ.extend([
 (mock('aws', ['EC2', 'Global view'], ['Global view', 'Regions'], 'Regions', [('Regions enabled', 'count'), ('Asia Pacific (Mumbai)', '3 AZs')], 'Refresh'),
  mock('az', ['Subscriptions', 'Locations'], ['Overview', 'Locations'], 'Overview', [('Physical regions', 'count'), ('Central India', '3 zones')], 'Refresh'),
  mock('gcp', ['Compute Engine', 'Zones'], ['Zones', 'Regions'], 'Zones', [('Regions', 'count'), ('asia-south1', 'a · b · c')], 'Refresh')),
 (mock('aws', ['S3', 'new bucket', 'Properties'], ['Objects', 'Properties', 'Permissions'], 'Properties', [('Default encryption', 'SSE-S3 (enabled by default)'), ('Block Public Access', 'On (default)')], 'Edit'),
  mock('az', ['Storage account', 'Encryption'], ['Overview', 'Encryption', 'Configuration'], 'Encryption', [('Encryption type', 'Microsoft-managed keys (default)'), ('Anonymous blob access', 'Disabled (default)')], 'Save'),
  mock('gcp', ['Cloud Storage', 'Bucket', 'Configuration'], ['Objects', 'Configuration'], 'Configuration', [('Encryption', 'Google-managed (default)'), ('Public access', 'Not public')], 'Edit')),
 (mock('aws', ['Billing', 'Free Tier'], ['Bills', 'Free Tier'], 'Free Tier', [('Usage vs limit', 'per service')], 'View'),
  mock('az', ['Cost Management', 'Cost analysis'], ['Cost analysis', 'Budgets'], 'Cost analysis', [('Group by', 'Service name')], 'Download'),
  mock('gcp', ['Billing', 'Reports'], ['Reports', 'Budgets & alerts'], 'Reports', [('Group by', 'SKU')], 'Download')),
])

STEP1 = ('1 · Verify global-infrastructure facts (Regions and zones)', tri(
    (['[[EC2]] → [[EC2 Global View]] shows enabled Regions; the Region selector lists all Regions.'],
     "aws ec2 describe-regions --all-regions --query 'length(Regions)'\naws ec2 describe-availability-zones --region ap-south-1 --query 'AvailabilityZones[?ZoneType==`availability-zone`].ZoneName' --output text",
     'the total number of Regions (enabled and opt-in) and Mumbai’s three AZ names — the “Region contains multiple AZs” fact, verified.'),
    (['Any Create page → Region list; [[Subscriptions]] → [[Resource providers]] / Locations.'],
     'az account list-locations --query "length([?metadata.regionType==\'Physical\'])"\naz account list-locations --query "[?name==\'centralindia\'].availabilityZoneMappings[].logicalZone" -o tsv',
     'the number of physical Regions and Central India’s zones <code>1 2 3</code>.'),
    (['[[Compute Engine]] → [[Zones]] lists Regions and zones.'],
     'gcloud compute regions list --format="value(name)" | wc -l\ngcloud compute zones list --filter="region:asia-south1" --format="value(name)"',
     'the number of Regions and asia-south1-a/b/c.')),
    'Facts you have seen yourself are much harder to forget in the exam.')

STEP2 = ('2 · Verify security defaults (encryption and private storage)', tri(
    (['Create a bucket → [[Properties]] → Default encryption shows SSE-S3; [[Permissions]] shows Block Public Access on.'],
     "B=exam-facts-$RANDOM; aws s3 mb s3://$B --region ap-south-1 >/dev/null\naws s3api get-bucket-encryption --bucket $B --query 'ServerSideEncryptionConfiguration.Rules[0].ApplyServerSideEncryptionByDefault.SSEAlgorithm' --output text\naws s3api get-public-access-block --bucket $B --query 'PublicAccessBlockConfiguration' --output text",
     '<code>AES256</code> (encrypted by default since 2023) and four <code>True</code> values — new buckets are private and encrypted by default.'),
    (['Create a storage account → [[Encryption]] shows Microsoft-managed keys; [[Configuration]] shows anonymous blob access disabled.'],
     'az group create -n rg-exam -l centralindia >/dev/null\nSA=examfacts$RANDOM; az storage account create -n $SA -g rg-exam -l centralindia --sku Standard_LRS \\\n  --query "{encrypted:encryption.services.blob.enabled,keySource:encryption.keySource,anonymous:allowBlobPublicAccess,minTls:minimumTlsVersion}"',
     '<code>encrypted: true</code>, <code>Microsoft.Storage</code> key source, anonymous access <code>false</code>, minimum TLS 1.2.'),
    (['Create a bucket → [[Configuration]] → encryption “Google-managed”; [[Permissions]] → not public.'],
     'B=exam-facts-$RANDOM; gcloud storage buckets create gs://$B --location=asia-south1 --quiet\ngcloud storage buckets describe gs://$B --format="value(default_kms_key,public_access_prevention,uniform_bucket_level_access)"',
     'an empty KMS key (meaning Google-managed default encryption), <code>inherited</code> or <code>enforced</code>, and <code>True</code> for uniform access.')),
    'Exam answer pattern confirmed: storage is encrypted at rest by default on all three; access configuration remains your job.')

STEP3 = ('3 · Verify a pricing fact (on-demand vs commitment)', tri(
    (['[[Pricing Calculator]] → EC2 t3.micro Mumbai → compare On-Demand with a 1-year Savings Plan.'],
     "aws pricing get-products --region us-east-1 --service-code AmazonEC2 --filters \\\n  Type=TERM_MATCH,Field=instanceType,Value=t3.micro Type=TERM_MATCH,Field=regionCode,Value=ap-south-1 \\\n  Type=TERM_MATCH,Field=operatingSystem,Value=Linux Type=TERM_MATCH,Field=tenancy,Value=Shared \\\n  Type=TERM_MATCH,Field=preInstalledSw,Value=NA Type=TERM_MATCH,Field=capacitystatus,Value=Used \\\n  --query 'PriceList[0]' --output text | python3 -c \"import sys,json; d=json.loads(sys.stdin.read()); od=list(d['terms']['OnDemand'].values())[0]; print('on-demand', list(od['priceDimensions'].values())[0]['pricePerUnit']['USD']); [print(r['termAttributes'].get('LeaseContractLength'), r['termAttributes'].get('PurchaseOption'), [p['pricePerUnit']['USD'] for p in r['priceDimensions'].values() if p['unit']=='Hrs']) for r in d['terms'].get('Reserved',{}).values() if r['termAttributes'].get('OfferingClass')=='standard'][:3]\"",
     'the on-demand hourly price and several reserved options with lower hourly rates — commitment = discount, verified.'),
    (['[[Pricing calculator]] → Virtual Machines → compare Pay as you go with 1-year reserved for D2s_v5 in Central India.'],
     "curl -s \"https://prices.azure.com/api/retail/prices?\\$filter=armRegionName%20eq%20'centralindia'%20and%20armSkuName%20eq%20'Standard_D2s_v5'%20and%20serviceName%20eq%20'Virtual%20Machines'\" \\\n  | python3 -c \"import sys,json; [print(i['type'], i.get('reservationTerm',''), i['retailPrice'], i['unitOfMeasure']) for i in json.load(sys.stdin)['Items'] if 'Windows' not in i['productName'] and 'Spot' not in i['skuName'] and 'Low Priority' not in i['skuName']]\"",
     '<code>Consumption 0.101 1 Hour</code> and two <code>Reservation</code> rows (1 and 3 years, total price) at the time of writing — 1-year total ÷ 8,760 h is roughly 38% below the hourly rate.'),
    (['[[Pricing Calculator]] → Compute Engine e2-standard-2 asia-south1 → compare on-demand with 1-year committed use discount.'],
     'gcloud compute machine-types describe e2-standard-2 --zone=asia-south1-a --format="value(guestCpus,memoryMb)"',
     'the shape (2 vCPU, 8 GB); the calculator shows the committed-use discount percentage.')),
    'Pricing questions become easy once you have seen on-demand and committed prices side by side.')

prac = practical(OWN_INTRO + ' Quick “see it yourself” checks for three facts that exams love: Regions and zones, default encryption and privacy of storage, and commitment discounts. Costs: nothing (delete the test buckets/accounts).', [SETUP_STEP, STEP1, STEP2, STEP3],
    cleanup='<b>AWS:</b> <code>aws s3 rb s3://$B</code>. <b>Azure:</b> <code>az group delete -n rg-exam --yes --no-wait</code>. <b>Google Cloud:</b> <code>gcloud storage buckets delete gs://$B --quiet</code>.')

mist = mistakes([
    ['Answering before reading the ask.', 'Speed.', 'Last line first, then the stem.'],
    ['Ignoring “most cost-effective” / “least effort”.', 'Skimming.', 'Circle keywords every time.'],
    ['Changing answers without reason.', 'Doubt.', 'Change only if you find a clear error.'],
    ['Studying only one practice set.', 'Memorising answers.', 'Mix this set + official set + check-yourself boxes.'],
    ['Leaving blanks.', 'Time pressure.', 'No negative marking — always answer.'],
    ['Old exam codes and content.', 'Outdated videos.', 'Use the current official exam guide.']])

cert = table(['Exam / syllabus', 'How to use this lesson'], [['C-DAC PGCP-BDA', 'Cloud module theory exam (CCEE-style MCQs).'], ['AWS CLF-C02', 'Parts A–D mirror the four domains.'], ['AZ-900', 'Parts A–B and the Azure-specific questions; add Microsoft Learn practice assessment.'], ['Google Cloud Digital Leader', 'Parts A–B and the Google-specific questions; add official sample questions.']], minw=560)

proj = miniproject('Mini project: your exam-readiness tracker',
    'Measure and close your gaps before booking.',
    ['<b>Baseline:</b> take the 60-question exam timed; record score per part.',
     '<b>Gaps:</b> list every wrong answer with the lesson named in its explanation.',
     '<b>Confusing pairs:</b> build your sheet (at least 15 pairs).',
     '<b>Official set:</b> take the provider’s practice set; compare scores.',
     '<b>Re-test:</b> after revision, repeat both; target 75%+.',
     '<b>Book:</b> choose a date within two weeks of reaching the target.'],
    'A score table, a gap list and a booked exam date.', 'Modules 1–10.')

assemble_v2(HERE, story_h2='82% in practice, failed by four marks', hook_html=hk,
    narration='Riya practised with notes open and no timer, scoring 82%. In the real exam, under time pressure, she misread keywords and changed several correct answers. She failed by four marks.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Practice exam: cloud concepts (MCQ)',
    formal='A <b>cloud fundamentals exam</b> (such as AWS CLF-C02, Microsoft AZ-900 or Google Cloud Digital Leader) assesses conceptual understanding of cloud computing, core services, security and compliance, pricing and governance through multiple-choice and multiple-response questions; effective preparation combines domain-weighted revision, recognition of question styles, a consistent answering method and timed practice with explanation review.',
    simple='The exam checks whether you understand cloud basics; practise with a timer, learn the question types, and read every explanation.',
    interview=['“I prepared by mapping my study to the exam domains, practising timed sets, and reviewing explanations — especially look-alike services like CloudTrail vs CloudWatch.”', '“For scenario questions I read the ask first, circle keywords like least effort or most cost-effective, eliminate, then choose the managed best fit.”'],
    terms_rows=[('Stem', 'Question text.'), ('Distractor', 'Plausible wrong option.'), ('Multiple response', 'Select two or more.'), ('Scaled score', '100–1000 scale, 700 to pass (AWS/Microsoft).'), ('Domain', 'Exam topic area with a weight.'), ('Flag', 'Mark to review later.'), ('Exam guide', 'Official list of domains.'), ('Proctoring', 'Supervised exam delivery.')],
    exam='This whole lesson is exam preparation — Parts A–D follow the CLF-C02 domains and cover AZ-900 and Cloud Digital Leader concepts.',
    picture_h2='A method and the three exams', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven question styles, one by one', TYPES)],
    how_h2='Solving one exam question, step by step', how_intro='The five-step method applied.', how_anim=SOLVE,
    parts_h2='Six parts of exam preparation', parts_html=parts, lv='',
    myth_rows=[('Knowing the content guarantees a pass.', 'Method and timing matter too.', 'Story.'), ('More practice sets = better.', 'Reviewing explanations matters more.', 'Parts.'), ('The most reliable option is always right.', 'The keyword decides.', 'Type 4.')],
    extra_secs=[('exam', 'Practice exam', '60-question practice exam with explanations', PRACTICE), ('deep', 'Deep dive', 'Keyword cheat sheet, exam-day checklist, 2-week plan', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Recognise seven question styles.', 'Apply a five-step method to any MCQ.', 'Score yourself on a 60-question practice exam and find gaps.', 'Verify key exam facts on your own account.', 'Plan your exam booking.'],
    next_html='<a href="../03-lab-exam-practice-tasks/">11.3 Lab exam practice tasks</a>.',
    pre='<b>Before you start:</b> Modules 1–10.')
