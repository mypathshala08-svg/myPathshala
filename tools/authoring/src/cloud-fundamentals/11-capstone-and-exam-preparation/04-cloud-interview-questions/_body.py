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


hk = hook('“What is the difference between scalability and elasticity?” Meena knew it — and still answered in a way that made the interviewer frown.',
    'She recited a textbook line, gave no example, and stopped. The next candidate gave the same definition, added “for example, our canteen app scales out at lunch and back in at 2 pm — that is elasticity”, and got the offer. Interviews reward <b>definition + example + trade-off</b>. This lesson gives you the <b>seven kinds of interview questions</b>, an answer structure for each, <b>60 questions with model answers</b> from fresher to mid-level, and a short drill on <b>your own</b> account so you can talk about real numbers.',
    ['Definition → example → trade-off: the three-part answer.', 'STAR for project and behavioural questions.', 'Say “I would check…” for troubleshooting, in layers.'])

def story_scene():
    o = t(180, 12, 'Same knowledge, different answers', 9, 'ink', bold=True)
    o += box(8, 28, 160, 74, 'amber', rx=8) + t(88, 48, 'Textbook line', 8.4, 'ink', bold=True) + t(88, 64, 'no example', 7, 'ink2') + t(88, 78, 'no trade-off', 7, 'ink2') + t(88, 92, '“next question”', 7.4, 'ink', bold=True)
    o += box(192, 28, 160, 74, 'green', rx=8) + t(272, 48, 'Definition + example', 8.4, 'ink', bold=True) + t(272, 64, 'from own project', 7, 'ink2') + t(272, 78, '+ when not to use', 7, 'ink2') + t(272, 92, '“tell me more”', 7.4, 'ink', bold=True)
    o += t(180, 122, 'Interviewers test understanding, not memory', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Left: textbook line with no example or trade-off — “next question”. Right: definition plus an example from your own project plus when not to use it — “tell me more”.', story_scene(), 'Answer in <tspan font-weight="700" class="s-acc">three parts</tspan>: what, example, trade-off.', h=132)
dialogue = '''M> Sir, I gave the correct definition. Why did it not land?
A> Because hundreds of candidates can recite it. The interviewer wants to know if you have used it.
K> But freshers have no production experience.
A> You have your labs and capstone. “In my capstone, Lambda scaled from zero to fifty concurrent requests in the burst test” is real experience.
M> And if I don’t know an answer?
A> Say what you do know, how you would find out, and where you would look. Guessing confidently is worse than reasoning aloud.'''

def methodfig():
    o = t(320, 16, 'Answer structures that work', 11, 'ink', bold=True)
    S = [('Concept', 'Define → example → trade-off', 'blue', 12), ('Scenario', 'Clarify → options → choose → risks', 'amber', 172), ('Troubleshoot', 'Layers: DNS → network → app → data', 'red', 332), ('Project', 'STAR: situation, task, action, result', 'green', 492)]
    for a, b, tn, x in S:
        o += box(x, 36, 148, 80, tn, rx=8) + t(x + 74, 64, a, 9, 'ink', bold=True) + t(x + 74, 88, b, 6.6, 'ink2')
    o += t(320, 140, 'Keep answers to 60–90 seconds, then stop and let the interviewer steer.', 7.4, 'ink2')
    return o
METHOD = bigfig('Four answer structures: concept — define, example, trade-off; scenario — clarify, options, choose, risks; troubleshoot — layers DNS, network, app, data; project — STAR.', methodfig(), h=150)

picture = ('  <p>Most cloud interviews mix a few question kinds. Each has an answer structure that shows understanding in under two minutes:</p>\n' + METHOD +
           '\n  <h3>What interviewers listen for, by level</h3>\n' + table(['Level', 'They expect', 'Red flags'], [
               ['Fresher / intern', 'clear basics, labs you did yourself, curiosity', 'memorised lines, no hands-on, bluffing'],
               ['Junior (0–2 years)', 'deploy and debug common services, IAM basics, cost awareness', 'root keys, open security groups, “I just clicked”'],
               ['Mid-level (2–5 years)', 'design trade-offs, IaC, CI/CD, monitoring, incidents handled', 'no numbers, no failure stories, one-cloud tunnel vision']], minw=600))

RN = {'q': (4, 54, 50, 50, 'app', 'Question', 'listen'), 'cl': (66, 4, 62, 46, 'meter', 'Clarify', 'ask 1–2'), 'kind': (66, 104, 62, 46, 'gear', 'Kind', 'pick structure'),
      'core': (142, 54, 60, 50, 'cloud', 'Core answer', 'define'), 'ex': (216, 4, 62, 46, 'chart', 'Example', 'own project'), 'tr': (216, 104, 62, 46, 'shield', 'Trade-off', 'when not'), 'stop': (292, 54, 64, 50, 'user', 'Stop', 'invite follow-up')}
RS = [dict(on=['q'], hot='q', move=None, head='Step 1 · Listen to the whole question', text='“How would you make our web app highly available?” Pause two seconds; do not start', text2='with a service name.', svc='Silence for two seconds is fine'),
      dict(on=['q', 'cl'], hot='cl', move=(54, 79, 72, 30, 'ask'), head='Step 2 · Clarify', text='“What availability target — 99.9 or 99.99? Is it one Region today? Stateful or stateless?”', text2='One or two questions show senior thinking.', svc='Numbers change the design'),
      dict(on=['cl', 'kind'], hot='kind', move=(97, 50, 97, 104, 'scenario'), head='Step 3 · Recognise the kind', text='It is a scenario/design question → clarify, options, choose, risks.', text2='', svc='Pick the matching structure'),
      dict(on=['kind', 'core'], hot='core', move=(128, 127, 150, 100, 'answer'), head='Step 4 · Core answer', text='“Run at least two instances across Availability Zones behind a load balancer, with health', text2='checks; database in multi-AZ mode; static assets on a CDN.”', svc='Lead with the mechanism'),
      dict(on=['core', 'ex', 'tr'], hot='ex', move=(165, 54, 216, 20, 'example'), head='Step 5 · Example and trade-off', text='“In my capstone, two zones kept the app up when I stopped one instance. Multi-Region would', text2='add cost and complexity — only if the business needs regional DR.”', svc='Proof + judgement'),
      dict(on=list(RN), hot='stop', move=(278, 127, 298, 100, 'stop'), head='Step 6 · Stop and invite follow-up', text='“Happy to go deeper into the database failover or the cost side.” Then stop talking.', text2='Interviewers steer to what they want to test.', svc='60–90 seconds per answer')]
SOLVE = flow_anim('Answering an interview question, step by step', 'A scenario question answered with the structure.', 'Answer flow', 'Animation: listen; clarify; recognise the kind; core answer; example and trade-off; stop and invite follow-up.', RN, RS, hid='ivflow')

def mapfig():
    o = t(320, 16, 'Seven kinds of cloud interview questions', 11, 'ink', bold=True)
    items = [('1', 'Concept', 'define + example', 'blue'), ('2', 'Compare', 'X vs Y', 'amber'), ('3', 'Scenario / design', 'how would you…', 'violet'), ('4', 'Troubleshooting', 'it is broken…', 'red'),
             ('5', 'Security', 'how do you protect…', 'red'), ('6', 'Cost', 'bill went up…', 'green'), ('7', 'Project / behavioural', 'tell me about…', 'card')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 8.4, 'ink', bold=True) + t(x + 78, y + 54, b, 6.8, 'ink2')
    o += t(320, 210, 'A 45-minute interview typically touches four or five of these.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of seven interview question kinds: concept, compare, scenario or design, troubleshooting, security, cost, project or behavioural.', mapfig(), h=222)

def iq(n, name, tone, d, an, ex, tip, A, use, plain, how, words, diff, rw, pro):
    return vt(n, name, tone, d, an, ex, tip, '', A, use, 'you answer with a memorised line and no example.', plain, how, words, diff, ['service companies', 'product companies', 'cloud consultancies', 'campus placements'], rw, pro)

A1 = mk(['Define', 'Example', 'Trade-off'], ['define|one sentence|precise words', 'example|your lab|or project', 'trade-off|when not to|or the cost'], ['blue', 'amber', 'green'],
        ['define in one precise sentence', 'give an example from your own lab or project', 'add a trade-off or when not to use it'],
        [('Define', 'One precise sentence.', ''), ('Example', 'From your own work.', ''), ('Trade-off', 'When not to use it.', '')],
        'Concept questions', 'Three parts, under a minute.', 'Concept', 'Animation: define; example; trade-off.', 'i1anim')
T1 = iq(1, 'Concept questions', 'blue',
    '<b>Concept questions</b> ask you to explain a term — cloud computing, IaaS/PaaS/SaaS, virtualisation, Region and AZ, serverless, containers — and are answered best in three parts: precise definition, an example from your own work, and a trade-off.',
    'Explaining a recipe: what the dish is, when you last made it, and when you would cook something else.',
    'Example: “What is serverless?” → “Running code without managing servers; billed per request and duration. My capstone used Lambda for orders. Not ideal for long-running jobs or steady high load, where containers can be cheaper.”',
    'Tip: prepare 20 concept answers in this shape — they are the backbone of fresher interviews.', A1,
    'the question starts “what is…” or “explain…”.',
    'Questions asking you to explain a cloud term.',
    [('Define', 'One sentence.'), ('Example', 'Lab/project.'), ('Benefit', 'Why it matters.'), ('Trade-off', 'Limits.'), ('Stop', 'Invite follow-up.')],
    [('elevator answer', '30–60 second explanation'), ('trade-off', 'what you give up'), ('follow-up', 'deeper question on the same topic')],
    table(['Weak', 'Strong'], [['“Serverless means no servers.”', '“Servers exist, but the provider runs them; I pay per request…”'], ['textbook only', 'textbook + own example + limit']], minw=420),
    'Every cloud interview opens with concept questions; they set the interviewer’s first impression.',
    'Avoid absolute words (“always”, “never”); cloud answers are almost always “it depends — on X”.')

A2 = mk(['Shared purpose', 'Key difference', 'When each'], ['same|both do X|one line', 'differ|on one axis|e.g. control', 'choose|A when…|B when…'], ['amber', 'blue', 'green'],
        ['say what both have in common', 'name the key difference on one axis', 'say when you would choose each'],
        [('Common', 'What both do.', ''), ('Difference', 'One clear axis.', ''), ('When', 'Use A when…, B when…', '')],
        'Comparison questions', 'Common → difference → when.', 'Compare', 'Animation: shared purpose; key difference; when each.', 'i2anim')
T2 = iq(2, 'Comparison questions (X vs Y)', 'amber',
    '<b>Comparison questions</b> ask the difference between two related things — VM vs container, SG vs NACL, CloudTrail vs CloudWatch, RDS vs DynamoDB, vertical vs horizontal scaling — and are answered by stating what they share, the key difference, and when to choose each.',
    'Bus vs taxi: both get you there; one is shared and scheduled, the other private and on demand; choose by budget and urgency.',
    'Example: “Security group vs network ACL?” → “Both filter traffic in a VPC. SGs are stateful and attach to instances; NACLs are stateless and attach to subnets, with ordered allow/deny rules. I use SGs for most rules and NACLs for subnet-wide blocks.”',
    'Tip: a two-column comparison in your head (scope, state, cost, control) answers most X-vs-Y questions.', A2,
    'the question contains “vs” or “difference between”.',
    'Questions asking how two similar things differ.',
    [('Common', 'Shared purpose.'), ('Axis', 'Scope, state, control, cost.'), ('Example', 'One each.'), ('Choose', 'When each.'), ('Stop', '—')],
    [('stateful', 'remembers connections; return traffic allowed'), ('stateless', 'each packet evaluated alone'), ('axis', 'dimension of comparison')],
    table(['Pair', 'Key axis'], [['VM vs container', 'own OS vs shared kernel'], ['SG vs NACL', 'stateful/instance vs stateless/subnet'], ['RDS vs DynamoDB', 'relational SQL vs key-value at scale'], ['Vertical vs horizontal', 'bigger box vs more boxes']], minw=420),
    'Comparisons reveal depth quickly, so interviewers use them as follow-ups to concept questions.',
    'End with a choice (“I would pick… because…”); comparisons without a decision feel unfinished.')

A3 = mk(['Clarify', 'Options', 'Choose + risks'], ['clarify|users, SLA|budget, data', 'options|two designs|pros/cons', 'choose|one + why|risks, next'], ['violet', 'amber', 'green'],
        ['clarify the numbers: users, availability target, budget, data', 'outline two options with pros and cons', 'choose one, explain why, name the risks'],
        [('Clarify', 'Users, SLA, budget, data, team.', ''), ('Options', 'Two designs, honest pros/cons.', ''), ('Choose', 'Decision + risks + next steps.', '')],
        'Scenario and design questions', 'Numbers first, then options.', 'Scenario', 'Animation: clarify; options; choose and risks.', 'i3anim')
T3 = iq(3, 'Scenario and design questions', 'violet',
    '<b>Scenario questions</b> describe a business need — “design a photo-sharing app”, “move this on-premises app to cloud”, “handle a 10× traffic spike” — and test whether you clarify requirements, compare options and choose with reasons, as you did in the capstone.',
    'An architect asking how many people will live in a house before drawing it.',
    'Example: “Migrate a college ERP to cloud.” → clarify users, peak, data sensitivity, budget, team skills → rehost on VMs now vs replatform to managed DB/PaaS → choose replatform for the DB and rehost the app first; risks: data migration window, licences.',
    'Tip: reuse your capstone’s seven deliverables as a checklist — requirements, architecture, services, security, reliability, cost, operations.', A3,
    'the question starts “how would you design/migrate/handle…”.',
    'Questions where you design a solution for a situation.',
    [('Clarify', 'Numbers.'), ('Options', 'Two.'), ('Choose', 'Reasoned.'), ('Security/cost', 'Mention both.'), ('Risks', 'And mitigations.')],
    [('NFR', 'non-functional requirement'), ('RTO/RPO', 'recovery time / data-loss targets'), ('7 Rs', 'migration strategies')],
    table(['Weak', 'Strong'], [['jumps to a service list', 'asks numbers first'], ['one option', 'two options compared'], ['no risks', 'risks and mitigations']], minw=420),
    'Design questions decide most mid-level offers.',
    'Draw while you talk if there is a whiteboard — boxes, arrows, labels; it keeps both of you aligned.')

A4 = mk(['Reproduce', 'Layer by layer', 'Fix + prevent'], ['reproduce|what exactly|fails?', 'layers|DNS → network|→ app → data', 'fix|then prevent|alarm, test'], ['red', 'amber', 'green'],
        ['confirm exactly what fails and since when', 'check layer by layer: DNS, network, compute, app, data', 'fix, then prevent: alarm, test or automation'],
        [('Reproduce', 'What fails, since when, for whom?', ''), ('Layers', 'DNS → network → compute → app → data.', ''), ('Fix + prevent', 'Fix, then alarm/test/runbook.', '')],
        'Troubleshooting questions', 'Systematic beats lucky.', 'Troubleshooting', 'Animation: reproduce; layer by layer; fix and prevent.', 'i4anim')
T4 = iq(4, 'Troubleshooting questions', 'red',
    '<b>Troubleshooting questions</b> give a symptom — “the website is down”, “the VM is unreachable”, “the Lambda times out”, “S3 access denied” — and test a systematic approach: reproduce, check layer by layer, use logs and metrics, fix, then prevent recurrence.',
    'A doctor checking pulse, breathing and temperature in order before prescribing.',
    'Example: “EC2 web page not loading.” → “Is the instance running and passing status checks? Public IP? Security group allows 80? NACL? Is nginx running (systemctl status)? Logs in cloud-init-output and nginx error log? Then fix and add an alarm.”',
    'Tip: say what tool you would use at each layer — it shows real practice (dig, curl -v, status checks, Logs, Trail).', A4,
    'the question describes something broken.',
    'Questions where you find and fix a problem.',
    [('Scope', 'Who/what/when.'), ('Recent change?', 'Deploys, config.'), ('Layers', 'Network → app.'), ('Evidence', 'Logs, metrics.'), ('Prevent', 'Alarm, test.')],
    [('status checks', 'EC2 system/instance health checks'), ('curl -v', 'shows connection and HTTP details'), ('runbook', 'documented fix procedure')],
    table(['Symptom', 'First checks'], [['timeout', 'firewall, routes, public IP'], ['connection refused', 'service not listening'], ['403/AccessDenied', 'IAM/bucket policy'], ['5xx', 'app logs, dependencies']], minw=420),
    'Interviewers often extend troubleshooting questions step by step (“it is not the SG — now what?”).',
    'Always ask “what changed recently?” — most incidents follow a change.')

A5 = mk(['Identity', 'Network + data', 'Detect + respond'], ['identity|least privilege|MFA, roles', 'protect|private subnets|encryption', 'detect|logs, alerts|respond plan'], ['red', 'blue', 'green'],
        ['start with identity: least privilege, MFA, roles not keys', 'protect network and data: private subnets, encryption, no public buckets', 'detect and respond: audit logs, threat detection, incident plan'],
        [('Identity', 'Least privilege, MFA, roles.', ''), ('Protect', 'Network isolation, encryption.', ''), ('Detect', 'Logs, alerts, response.', '')],
        'Security questions', 'Identity → protect → detect.', 'Security', 'Animation: identity; network and data; detect and respond.', 'i5anim')
T5 = iq(5, 'Security questions', 'red',
    '<b>Security questions</b> ask how you would protect an account, application or data — “how do you secure S3?”, “what is least privilege?”, “someone leaked an access key — what do you do?” — and are answered in layers: identity, network, data, detection and response.',
    'Securing a house: who has keys, locked doors and windows, a safe for valuables, and an alarm.',
    'Example: “Leaked access key?” → “Deactivate the key immediately, check CloudTrail for its use, revoke sessions, rotate secrets, scan for created resources, then move the app to a role so there is no long-term key.”',
    'Tip: mention the shared responsibility model at the start — it frames every security answer.', A5,
    'the question mentions protection, leaks, compliance or access.',
    'Questions about keeping systems and data safe.',
    [('Identity', 'IAM, MFA.'), ('Network', 'Private subnets, SGs.'), ('Data', 'Encryption, KMS.'), ('Detect', 'Trail, GuardDuty.'), ('Respond', 'Plan, rotate.')],
    [('least privilege', 'only what is needed'), ('rotation', 'replacing credentials regularly'), ('blast radius', 'how much damage one failure can do')],
    table(['Question', 'Core of the answer'], [['Secure a bucket', 'block public access, policies, encryption, logging'], ['App credentials', 'roles/managed identity, secrets manager'], ['Root account', 'MFA, no keys, break-glass only']], minw=420),
    'Security is asked in almost every cloud interview, whatever the role.',
    'Never describe a shortcut you took (e.g. “I made it public to test”) without saying how you would do it properly.')

A6 = mk(['Find the driver', 'Quick wins', 'Guard-rails'], ['find|cost by service|and tag', 'cut|idle, oversized|wrong pricing', 'guard|budgets, tags|policies'], ['green', 'amber', 'blue'],
        ['find what drives the bill: by service, Region and tag', 'cut quickly: idle resources, oversized instances, wrong pricing model', 'add guard-rails: budgets, tags, policies, reviews'],
        [('Find', 'Cost by service, Region, tag.', ''), ('Cut', 'Idle, oversized, pricing model.', ''), ('Guard', 'Budgets, tags, policies.', '')],
        'Cost questions', 'Find → cut → guard.', 'Cost', 'Animation: find the driver; quick wins; guard-rails.', 'i6anim')
T6 = iq(6, 'Cost questions', 'green',
    '<b>Cost questions</b> ask how you would reduce or control a cloud bill — “our bill doubled”, “how do you choose a pricing model?”, “what is FinOps?” — and test whether you find the cost driver with data, apply quick wins, and add guard-rails.',
    'A household budget: look at the bank statement, cancel unused subscriptions, then set monthly limits.',
    'Example: “Bill doubled.” → “Cost Explorer by service and tag; found NAT gateway data and idle test instances; stopped idle, moved S3 traffic to a gateway endpoint, right-sized; added budgets and mandatory tags.”',
    'Tip: always mention data transfer (egress, NAT) — it is the most commonly forgotten cost.', A6,
    'the question mentions bills, budgets, pricing or FinOps.',
    'Questions about spending less and controlling cloud costs.',
    [('Data', 'Cost by dimension.'), ('Idle', 'Stop/delete.'), ('Right-size', 'Metrics.'), ('Pricing', 'Commit/Spot.'), ('Guard', 'Budgets, tags.')],
    [('right-sizing', 'matching size to actual use'), ('FinOps', 'shared financial accountability for cloud'), ('egress', 'data leaving the cloud, usually charged')],
    table(['Lever', 'Example'], [['Idle', 'stop dev VMs at night'], ['Size', 'downsize 10%-CPU instances'], ['Pricing', 'Savings Plans for steady load'], ['Architecture', 'serverless for spiky load']], minw=420),
    'Cost awareness distinguishes good engineers in interviews — many candidates never mention it.',
    'Quote a number from your own account (“my lab cost ₹38 last month; most was the NAT gateway”) — it is memorable.')

A7 = mk(['Situation + task', 'Action', 'Result + learning'], ['S/T|context|your role', 'action|what YOU did|specific', 'result|numbers|what you learned'], ['card', 'amber', 'green'],
        ['situation and task: the context and your role', 'action: what you personally did, specifically', 'result with numbers, and what you learned'],
        [('S/T', 'Context and your role.', ''), ('Action', 'What you did — “I”, not “we”.', ''), ('Result', 'Numbers + learning.', '')],
        'Project and behavioural questions', 'STAR in 90 seconds.', 'Project / behavioural', 'Animation: situation and task; action; result and learning.', 'i7anim')
T7 = iq(7, 'Project and behavioural questions', 'card',
    '<b>Project and behavioural questions</b> — “walk me through your project”, “tell me about a failure”, “a time you disagreed with a teammate” — are answered with STAR: situation, task, action, result, ending with what you learned.',
    'Telling a cricket story: the match situation, your role, the shots you played, the final score and what you would do differently.',
    'Example: “Your project?” → S: canteen ordering capstone; T: design and deploy within ₹5,000/month; A: I chose Lambda + DynamoDB, wrote CloudFormation, ran a burst test; R: p95 420 ms at 50 requests, cost ₹0 in free tier, torn down cleanly; learned to set alarms before load tests.',
    'Tip: prepare three stories — a project, a failure, a teamwork moment — and adapt them to many questions.', A7,
    'the question starts “tell me about a time…” or “walk me through…”.',
    'Questions about what you did and how you work with others.',
    [('Situation', 'One line.'), ('Task', 'Your goal.'), ('Action', 'Specific steps.'), ('Result', 'Numbers.'), ('Learning', 'One line.')],
    [('STAR', 'situation, task, action, result'), ('ownership', 'taking responsibility'), ('blameless', 'focusing on the system, not the person')],
    table(['Weak', 'Strong'], [['“We built an app.”', '“I designed the data model and IaC.”'], ['no numbers', 'latency, cost, users'], ['blames others', 'what I learned and changed']], minw=420),
    'Behavioural rounds are scored as seriously as technical rounds in most companies.',
    'For failure stories, pick a real, small, technical failure with a clear lesson — not a disaster and not a fake “I work too hard”.')

SUMMARY = table(['#', 'Kind', 'Signal', 'Structure'], [
    ['1', 'Concept', '“what is…”', 'define → example → trade-off'], ['2', 'Compare', '“X vs Y”', 'common → difference → when'], ['3', 'Scenario', '“how would you design…”', 'clarify → options → choose → risks'],
    ['4', 'Troubleshooting', '“it is broken…”', 'reproduce → layers → fix → prevent'], ['5', 'Security', '“how do you protect…”', 'identity → protect → detect'], ['6', 'Cost', '“bill went up…”', 'find → cut → guard'], ['7', 'Project/behavioural', '“tell me about…”', 'STAR + learning']], minw=600)

TYPES = ('  <p>Seven kinds of interview questions, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, real-world example, a sample answer and an expert tip.</p>\n'
         + challenge(['Which structure fits “the website is down”?', 'What three parts make a strong concept answer?', 'What does STAR stand for?'], 'types 4, 1 and 7') + MAP
         + jump(['Concept', 'Compare', 'Scenario', 'Troubleshoot', 'Security', 'Cost', 'Project']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY)

# ------------------------------------------------------------------ question bank
def qa(items):
    return ''.join(f'  <details class="faq"><summary>{q}</summary><p>{a}</p></details>\n' for q, a in items)

BANK = ('  <p>Sixty questions with model answers. Say each answer aloud, then compare. Replace the examples with your own labs and capstone wherever you can.</p>\n'
 '  <h3>Fresher · Fundamentals (20)</h3>\n' + qa([
  ('1. What is cloud computing?', 'On-demand access to computing resources over a network, paid for as used. NIST lists five characteristics: on-demand self-service, broad network access, resource pooling, rapid elasticity and measured service. Example: I launch a VM in a minute and pay per second. Trade-off: less physical control, and costs need watching.'),
  ('2. IaaS vs PaaS vs SaaS?', 'They differ in how much the provider manages. IaaS: VMs, I manage OS and up (EC2). PaaS: I deploy code, provider runs the platform (App Service, Elastic Beanstalk). SaaS: finished software (Gmail). Choose by how much control vs effort you want.'),
  ('3. Public, private, hybrid and multi-cloud?', 'Public: shared provider infrastructure. Private: dedicated to one organisation. Hybrid: on-premises plus public cloud working together. Multi-cloud: more than one public provider. Banks often use hybrid for regulatory data.'),
  ('4. What is a Region and an Availability Zone?', 'A Region is a geographic area; an AZ is one or more isolated data centres inside it with independent power and networking. Deploying across AZs gives high availability; across Regions gives disaster recovery.'),
  ('5. Scalability vs elasticity?', 'Scalability is the ability to grow capacity; elasticity is adding and removing capacity automatically to match demand. Auto Scaling adding instances at lunch and removing them later is elasticity.'),
  ('6. CapEx vs OpEx?', 'CapEx: upfront purchase of assets like servers. OpEx: ongoing pay-as-you-go spending. Cloud shifts IT from CapEx to OpEx, improving cash flow and agility.'),
  ('7. What is virtualisation?', 'Running multiple virtual machines on one physical host using a hypervisor. Type 1 runs on hardware (KVM, Hyper-V, ESXi); Type 2 runs on an OS (VirtualBox). It is the foundation of IaaS.'),
  ('8. VM vs container?', 'Both isolate workloads. A VM includes a full guest OS; a container shares the host kernel and packages only the app and libraries, so it starts faster and is smaller. Use VMs for full OS control, containers for portable microservices.'),
  ('9. What is serverless?', 'Running code or services without managing servers; scaling and billing per use (Lambda, Azure Functions, Cloud Run functions). Great for event-driven and spiky work; less suited to long-running or steady heavy workloads.'),
  ('10. What is object storage?', 'Storage of files as objects with metadata in buckets, accessed over HTTP (S3, Blob, Cloud Storage). Highly durable and cheap; not a file system for databases — that is block storage.'),
  ('11. Block vs file vs object storage?', 'Block: raw disks for VMs and databases (EBS). File: shared folders over NFS/SMB (EFS, Azure Files). Object: HTTP-accessed objects for files, backups and data lakes (S3).'),
  ('12. What is a VPC?', 'A logically isolated private network in the cloud where you define IP ranges, subnets, routes and firewalls. Public subnets route to an internet gateway; private subnets do not.'),
  ('13. What is a load balancer?', 'A service that distributes incoming traffic across healthy targets, removing unhealthy ones using health checks. It enables high availability and horizontal scaling.'),
  ('14. What is auto scaling?', 'Automatically adjusting the number of instances based on metrics or schedules, within minimum and maximum limits. It delivers elasticity and saves cost at quiet times.'),
  ('15. What is the shared responsibility model?', 'The provider secures the cloud itself (facilities, hardware, hypervisor); the customer secures what they put in it (data, identities, configuration). The split moves with the service model: more customer responsibility in IaaS, less in SaaS.'),
  ('16. What is IAM?', 'Identity and Access Management: who (users, groups, roles) can do what (actions) on which resources. Best practice: least privilege, MFA, roles instead of long-term keys.'),
  ('17. What is a CDN?', 'A network of edge locations caching content close to users to reduce latency and origin load (CloudFront, Azure Front Door/CDN, Cloud CDN).'),
  ('18. What is an SLA?', 'A provider’s commitment to availability, usually monthly, with service credits if missed. 99.9% allows about 43 minutes of downtime a month.'),
  ('19. What is multitenancy?', 'Multiple customers sharing the same physical infrastructure with logical isolation. It drives cloud economies of scale.'),
  ('20. Name the major cloud providers.', 'AWS, Microsoft Azure and Google Cloud lead the market; others include Oracle Cloud, IBM Cloud and Alibaba Cloud. Indian options include providers offering local data residency.')]) +
 '  <h3>Junior · Services and hands-on (20)</h3>\n' + qa([
  ('21. How do you host a static website?', 'Upload files to object storage and enable website hosting (S3 website, Azure $web, GCS website config), ideally behind a CDN with HTTPS. Keep the bucket private and let the CDN read it where possible.'),
  ('22. How does an EC2 instance access S3 securely?', 'Attach an IAM role through an instance profile; the SDK gets temporary credentials automatically. Never store access keys on the instance.'),
  ('23. Security group vs NACL?', 'SGs are stateful, instance-level, allow-only. NACLs are stateless, subnet-level, ordered allow and deny rules. Most control uses SGs.'),
  ('24. RDS vs DynamoDB?', 'RDS: managed relational databases with SQL and joins. DynamoDB: serverless key-value/document store with single-digit-millisecond latency at any scale. Choose by data model and access patterns.'),
  ('25. What happens when you stop and start an EC2 instance?', 'EBS data persists; instance-store data is lost; the public IP usually changes unless you use an Elastic IP; billing for compute stops while stopped, but EBS storage is still billed.'),
  ('26. What is an AMI / image?', 'A template with the OS and software used to launch instances. You can create your own golden images.'),
  ('27. How do you make a database highly available?', 'Use the managed multi-AZ/zone-redundant option: a standby in another AZ with automatic failover; add read replicas for read scaling and backups for recovery.'),
  ('28. What is CloudWatch vs CloudTrail?', 'CloudWatch: metrics, logs and alarms about performance. CloudTrail: audit log of API calls — who did what, when, from where.'),
  ('29. What is infrastructure as code?', 'Defining infrastructure in files (CloudFormation, Bicep, Terraform) so it is versioned, reviewed and repeatable. My capstone stack deploys and tears down from one template.'),
  ('30. What is CI/CD?', 'Continuous integration builds and tests every change; continuous delivery/deployment releases it automatically through stages. Tools: CodePipeline, Azure Pipelines, Cloud Build, GitHub Actions.'),
  ('31. Blue/green vs canary deployment?', 'Blue/green switches all traffic to a new environment at once with instant rollback; canary sends a small percentage first and increases gradually. Canary limits blast radius.'),
  ('32. What is a NAT gateway?', 'Lets instances in private subnets reach the internet for updates without being reachable from the internet. It has hourly and per-GB charges.'),
  ('33. What is Route 53 / DNS?', 'DNS translates names to IP addresses. Route 53 also offers routing policies (latency, weighted, failover) and health checks.'),
  ('34. What is a pre-signed URL?', 'A time-limited URL granting access to one private object without making it public; Azure uses SAS tokens, Google signed URLs.'),
  ('35. What is a managed identity / service account?', 'An identity for applications managed by the cloud (Azure managed identity, Google service account) so code gets tokens without stored secrets.'),
  ('36. What are tags/labels for?', 'Key-value metadata for cost allocation, automation, access control and cleanup — e.g. project=canteen, env=dev.'),
  ('37. How do you connect on-premises to cloud?', 'Site-to-site VPN over the internet (quick, cheaper) or a dedicated private link (Direct Connect, ExpressRoute, Cloud Interconnect) for consistent bandwidth.'),
  ('38. What is Kubernetes?', 'A container orchestration platform that schedules, scales and heals containers. Managed versions: EKS, AKS, GKE.'),
  ('39. What is a snapshot?', 'A point-in-time copy of a disk stored durably; used for backups and creating new disks. AWS EBS snapshots are incremental.'),
  ('40. What storage class would you use for 7-year archives?', 'An archive tier such as S3 Glacier Deep Archive, Azure Archive or Google Archive storage — cheapest per GB, with retrieval delays and costs.')]) +
 '  <h3>Mid-level · Design, operations, security, cost (20)</h3>\n' + qa([
  ('41. Design a highly available web application.', 'Clarify SLA and traffic. Stateless app on instances or containers across at least two AZs behind a load balancer with health checks and auto scaling; managed DB multi-AZ; static content on CDN; sessions in a cache; IaC, monitoring, alarms; multi-Region only if the business needs it.'),
  ('42. How would you migrate an on-premises application?', 'Assess (inventory, dependencies, licences), choose a strategy per app (7 Rs), build a landing zone (accounts, network, identity), pilot, migrate data with minimal downtime, cut over, optimise. Start with low-risk apps.'),
  ('43. What is a landing zone?', 'A pre-configured multi-account/subscription environment with identity, network, logging, security baselines and guard-rails, e.g. AWS Control Tower, Azure landing zones.'),
  ('44. RTO vs RPO?', 'RTO: how long until service is restored. RPO: how much data loss is acceptable. They decide the DR strategy — backup/restore, pilot light, warm standby or active-active.'),
  ('45. How do you handle secrets?', 'Store in Secrets Manager/Key Vault/Secret Manager, access via roles, rotate automatically, never commit to Git, and scan repositories for leaks.'),
  ('46. Someone pushed access keys to GitHub. What do you do?', 'Deactivate and delete the key immediately, review CloudTrail for misuse, remove any created resources, rotate related secrets, purge history, and move to roles/OIDC so no long-term keys exist.'),
  ('47. How do you control costs across many teams?', 'Account/subscription per team, mandatory tags, budgets with alerts, cost dashboards, commitment discounts centrally, policies preventing expensive resources, monthly FinOps reviews.'),
  ('48. The bill doubled this month. Investigate.', 'Cost Explorer by service, Region, usage type and tag; compare with last month; look for data transfer, NAT, idle or forgotten resources, logging volume; fix, then add budgets and anomaly detection.'),
  ('49. How do you design for failure?', 'Assume components fail: redundancy across AZs, health checks, retries with backoff, timeouts, circuit breakers, queues to decouple, graceful degradation, chaos testing.'),
  ('50. What is observability?', 'The ability to understand a system from its outputs — metrics, logs and traces — so you can ask new questions during incidents. Add SLOs and alerts on symptoms users feel.'),
  ('51. SLI, SLO, SLA?', 'SLI: a measured indicator (p95 latency). SLO: internal target for it (p95 under 300 ms for 99% of minutes). SLA: external contract with penalties, usually looser than the SLO.'),
  ('52. How do you secure a multi-account AWS organisation?', 'Organizations with SCPs, SSO/Identity Center, central CloudTrail and Config, GuardDuty and Security Hub delegated admin, guard-rails via Control Tower, separate log and security accounts.'),
  ('53. Containers on ECS/EKS vs serverless functions?', 'Containers for long-running services, custom runtimes, steady load; functions for event-driven, spiky, short tasks. Consider team skills and cost at your load profile.'),
  ('54. How do you choose a Region?', 'Latency to users, data-residency laws (e.g. DPDP), service availability, price, and DR pairing.'),
  ('55. How do you do zero-downtime database migrations?', 'Backward-compatible schema changes (expand/contract), replication or DMS for data, dual writes or CDC, feature flags, and a rollback plan.'),
  ('56. What is a VPC endpoint / private link?', 'Private connectivity from your network to a service without the internet; gateway endpoints for S3/DynamoDB are free and save NAT charges.'),
  ('57. Multi-cloud: when and when not?', 'When for regulation, best-of-breed services, acquisitions or negotiating leverage; not by default — it multiplies skills, tooling and security effort.'),
  ('58. What is policy as code?', 'Guard-rails written as code — SCPs, Azure Policy, Organization Policy, OPA — evaluated automatically, e.g. deny public buckets, require tags, restrict Regions.'),
  ('59. How do you run an incident?', 'Declare, assign roles (commander, communications), mitigate first, communicate status, find root cause later, write a blameless postmortem with actions.'),
  ('60. Where do you see cloud careers going?', 'More platform engineering, FinOps, security and AI/data workloads; strong fundamentals plus one deep specialty and automation skills stay valuable.')]))

parts = wwu([
    ('Resume line', 'Projects with numbers.', 'Starts the conversation.', '“Deployed X; p95 Y ms; cost ₹Z.”'),
    ('Three stories', 'Project, failure, teamwork.', 'Covers most behavioural questions.', 'STAR format.'),
    ('20 concept answers', 'Define + example + trade-off.', 'Fresher backbone.', 'Questions 1–20.'),
    ('Live demo', 'Your account or GitHub.', 'Proof of hands-on.', 'IaC repo + screenshots.'),
    ('Questions for them', 'Team, stack, on-call, learning.', 'Shows interest.', 'Prepare three.'),
    ('Mock interviews', 'Practise aloud with a timer.', 'Fluency.', 'Record and review.')])

DEEP = ('  <h3>When you do not know the answer</h3>\n  <ol><li>Say what you do know that is related.</li><li>Reason aloud: “I would expect… because…”.</li><li>Say how you would find out: documentation, a quick test, a colleague.</li><li>Never invent service names or numbers.</li></ol>\n'
    '  <h3>Questions to ask the interviewer</h3>\n  <ul><li>“Which cloud services does the team use most, and what is the IaC tool?”</li><li>“How are incidents and on-call handled?”</li><li>“What would success look like in the first 90 days?”</li></ul>\n'
    '  <h3>Live coding / hands-on rounds</h3>\n' + table(['Ask', 'Prepare'], [['write a CLI script', 'loops, --query/JMESPath, jq'], ['write IaC', 'a small CloudFormation/Bicep/Terraform template from memory'], ['debug a template', 'read error messages; validate (cfn-lint, bicep build, terraform validate)'], ['explain a diagram', 'name each box and why it is there']], minw=480))

clouds = vendor_tabs('<p><b>AWS:</b> interviews often probe EC2, VPC, IAM, S3, RDS/DynamoDB, Lambda, CloudWatch/CloudTrail and the Well-Architected pillars.</p>',
    '<p><b>Azure:</b> expect Entra ID, RBAC, VNets/NSGs, App Service, AKS, Azure SQL, Monitor, Policy and management groups.</p>',
    '<p><b>Google Cloud:</b> expect projects and IAM, VPC (global), Compute Engine, GKE, Cloud Run, BigQuery, Cloud Storage and organisation policies.</p>') + \
    cloud3([['Identity', 'IAM, Identity Center', 'Entra ID, RBAC', 'Cloud IAM'], ['Audit', 'CloudTrail', 'Activity Log', 'Audit Logs'], ['Cost view', 'Cost Explorer', 'Cost analysis', 'Billing reports'], ['Inventory', 'Tagging API / Resource Explorer', 'Resource Graph / az resource list', 'Cloud Asset Inventory']])

MOCKQ.extend([
 (mock('aws', ['IAM', 'Dashboard'], ['Dashboard', 'Security recommendations'], 'Security recommendations', [('Root user MFA', 'Enabled ✓'), ('Root access keys', 'None ✓')], 'View'),
  mock('az', ['Microsoft Entra ID', 'My sign-ins'], ['Overview', 'Roles'], 'Roles', [('Role', 'Contributor'), ('Scope', 'subscription')], 'View'),
  mock('gcp', ['IAM & Admin', 'IAM'], ['Principals', 'Roles'], 'Principals', [('you@…', 'Owner'), ('MFA', '2-Step Verification on')], 'Grant access')),
 (mock('aws', ['Billing', 'Cost Explorer'], ['Reports', 'Group by'], 'Reports', [('Group by', 'Service'), ('Last month', 'cost per service')], 'Download CSV'),
  mock('az', ['Cost Management', 'Cost analysis'], ['Accumulated', 'Services'], 'Services', [('View', 'Last month'), ('Group by', 'Service name')], 'Download'),
  mock('gcp', ['Billing', 'Reports'], ['Reports', 'Budgets & alerts'], 'Reports', [('Time range', 'Last month'), ('Group by', 'Service')], 'Download')),
 (mock('aws', ['Resource Groups', 'Tag Editor'], ['Find resources'], 'Find resources', [('Regions', 'all'), ('Resource types', 'all')], 'Search'),
  mock('az', ['All resources'], ['Overview', 'Group by type'], 'Group by type', [('Resource type', 'count'), ('Location', 'all')], 'Export'),
  mock('gcp', ['Asset Inventory', 'Resource'], ['Overview', 'Resource'], 'Resource', [('Asset type', 'count'), ('Location', 'all')], 'Export')),
])

STEP1 = ('1 · Account hygiene you can talk about (“how do you secure your account?”)', tri(
    (['[[IAM]] → [[Dashboard]] → Security recommendations: root MFA on, no root access keys.', 'Note the users and whether each has MFA.'],
     "aws iam get-account-summary --query 'SummaryMap.[AccountMFAEnabled,AccountAccessKeysPresent]' --output text\naws iam generate-credential-report >/dev/null; sleep 5\naws iam get-credential-report --query Content --output text | base64 -d | cut -d, -f1,4,8,9 | head",
     '<code>1 0</code> (root MFA on, no root keys) and a CSV of users with password, MFA and key-1 status. Say: “root has MFA and no keys; I use SSO/role sessions day to day.”'),
    (['[[Microsoft Entra ID]] → your user → [[Authentication methods]]; [[Subscriptions]] → [[Access control (IAM)]] → [[Role assignments]].'],
     "ME=$(az ad signed-in-user show --query id -o tsv)\naz role assignment list --assignee $ME --all --query \"[].{role:roleDefinitionName,scope:scope}\" -o table",
     'your roles and scopes. Say: “I work as Contributor in a lab subscription, not Owner; Conditional Access enforces MFA.”'),
    (['[[IAM &amp; Admin]] → [[IAM]] → find your principal and roles; Google Account → Security → 2-Step Verification.'],
     "P=$(gcloud config get-value project)\ngcloud projects get-iam-policy $P --flatten='bindings[].members' \\\n  --filter=\"bindings.members:user:$(gcloud config get-value account)\" --format='table(bindings.role)'",
     'your roles on the project (e.g. <code>roles/owner</code>). Say: “in a team I would use a group with narrower roles.”')),
    'Interviewers ask “how do you secure your account?” — now you answer with your own facts.')

STEP2 = ('2 · Last month’s cost by service (“what does your project cost?”)', tri(
    (['[[Billing]] → [[Cost Explorer]] → last month, group by Service.'],
     "S=$(date -d \"$(date +%Y-%m-01) -1 month\" +%Y-%m-%d); E=$(date +%Y-%m-01)\naws ce get-cost-and-usage --time-period Start=$S,End=$E --granularity MONTHLY --metrics UnblendedCost \\\n  --group-by Type=DIMENSION,Key=SERVICE --query 'ResultsByTime[0].Groups[].[Keys[0],Metrics.UnblendedCost.Amount]' --output text | sort -k2 -t$'\\t' -nr | head",
     'services sorted by last month’s cost (USD). Cost Explorer API calls are charged per request — run it once.'),
    (['[[Cost Management]] → [[Cost analysis]] → Last month → group by Service name.'],
     "S=$(date -d \"$(date +%Y-%m-01) -1 month\" +%Y-%m-%d); E=$(date -d \"$(date +%Y-%m-01) -1 day\" +%Y-%m-%d)\naz consumption usage list --start-date $S --end-date $E \\\n  --query \"[].{svc:consumedService,cost:pretaxCost}\" -o tsv | awk -F'\\t' '{c[$1]+=$2} END {for (k in c) printf \"%s\\t%.2f\\n\", k, c[k]}' | sort -k2 -nr | head",
     'cost per service namespace (e.g. <code>Microsoft.Compute</code>). Some offer types (e.g. certain free or sponsored accounts) show no usage data here — use the portal view.'),
    (['[[Billing]] → [[Reports]] → last month → group by Service.'],
     "gcloud billing projects describe $(gcloud config get-value project) --format='value(billingAccountName,billingEnabled)'\ngcloud billing budgets list --billing-account=$(gcloud billing projects describe $(gcloud config get-value project) --format='value(billingAccountName)' | cut -d/ -f2) --format='table(displayName,amount.specifiedAmount.units)'",
     'your billing account and budgets. Per-service cost is in the Reports page (or a BigQuery billing export for queries).')),
    'Have one number ready: “my labs cost about ₹X last month; the biggest item was Y, and here is how I would cut it.”')

STEP3 = ('3 · Inventory your account (“walk me through what you built”)', tri(
    (['[[Resource Groups &amp; Tag Editor]] → Tag Editor → all Regions, all types → Search.'],
     "aws resourcegroupstaggingapi get-resources --query 'ResourceTagMappingList[].ResourceARN' --output text \\\n  | tr '\\t' '\\n' | cut -d: -f3 | sort | uniq -c | sort -nr",
     'a count per service (only for tagged or previously tagged resources in this Region). Use it as the outline of your project story — and delete what you no longer need.'),
    (['[[All resources]] → group by type.'],
     "az resource list --query \"[].type\" -o tsv | sort | uniq -c | sort -nr",
     'a count per resource type across the subscription, e.g. <code>Microsoft.Storage/storageAccounts</code>.'),
    (['[[Asset Inventory]] → [[Resource]] tab → group by asset type.'],
     "gcloud services enable cloudasset.googleapis.com\ngcloud asset search-all-resources --scope=projects/$(gcloud config get-value project) --format='value(assetType)' | sort | uniq -c | sort -nr | head",
     'a count per asset type, e.g. <code>compute.googleapis.com/Instance</code>.')),
    'Walk the list top to bottom in your answer: what each resource does, why it is there, and what it costs.')

prac = practical(OWN_INTRO + ' A 20-minute drill that turns your own account into interview material: security posture, cost, and an inventory you can explain. Read-only commands; no new resources except enabling one Google API.', [SETUP_STEP, STEP1, STEP2, STEP3],
    cleanup='Nothing to delete. Optional: <b>AWS</b> remove the downloaded credential report from your shell history/notes; <b>Google Cloud</b> <code>gcloud services disable cloudasset.googleapis.com</code> if you no longer need it. Delete any leftover lab resources the inventory revealed.')

mist = mistakes([
    ['Reciting definitions with no example.', 'Memorising.', 'Define → example → trade-off.'],
    ['Jumping to services in design questions.', 'Eagerness.', 'Clarify numbers first.'],
    ['Saying “we” for everything.', 'Modesty.', 'Say what you did: “I wrote the template”.'],
    ['Bluffing an unknown.', 'Pressure.', 'Reason aloud and say how you would find out.'],
    ['Talking for five minutes.', 'Nerves.', '60–90 seconds, then invite follow-up.'],
    ['No questions for the interviewer.', 'Not prepared.', 'Prepare three.']])

cert = table(['Exam / syllabus', 'How to use this lesson'], [['C-DAC PGCP-BDA', 'Placement preparation: viva and technical interviews on the cloud module.'], ['AWS CLF-C02 / AZ-900 / CDL', 'Questions 1–40 double as revision.'], ['Associate certifications', 'Questions 21–60 match associate-level knowledge.'], ['Job interviews', 'All seven kinds; practise aloud.']], minw=560)

proj = miniproject('Mini project: your interview pack',
    'Prepare everything you need for cloud interviews in one folder.',
    ['<b>Resume lines:</b> three projects with numbers (latency, cost, users).',
     '<b>Stories:</b> project, failure, teamwork in STAR, 90 seconds each.',
     '<b>Answers:</b> record yourself answering questions 1–20; re-record the weakest five.',
     '<b>Demo:</b> your capstone IaC repository with a README and architecture diagram.',
     '<b>Account facts:</b> the three outputs from the hands-on drill.',
     '<b>Mock:</b> a 30-minute mock interview with a friend using random questions from the bank.'],
    'A folder with resume lines, stories, recordings, a demo repo and a mock-interview score.', 'Whole course.')

assemble_v2(HERE, story_h2='Correct answer, no offer', hook_html=hk,
    narration='Meena and another candidate gave the same definition of elasticity. Only one added an example from their own project and a trade-off. That candidate got the offer.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Cloud interview questions',
    formal='A <b>cloud technical interview</b> evaluates a candidate’s understanding of cloud concepts, services, architecture, security, cost management and operations, together with problem-solving and communication, through concept, comparison, scenario, troubleshooting, security, cost and behavioural questions, often supported by hands-on or whiteboard exercises.',
    simple='Interviewers check whether you understand cloud and can use it — answer with a clear definition, a real example and a trade-off.',
    interview=['“I structure answers as definition, example from my own project, then trade-off — for example, serverless for the spiky canteen workload but containers for steady load.”', '“For incidents I reproduce, check layer by layer with logs and metrics, fix, then add an alarm or test so it does not recur.”'],
    terms_rows=[('STAR', 'Situation, task, action, result.'), ('Trade-off', 'What you give up for a choice.'), ('Clarifying question', 'Question to pin down requirements.'), ('Blast radius', 'Scope of damage from a failure.'), ('SLO', 'Internal reliability target.'), ('Postmortem', 'Blameless incident review.'), ('Whiteboard round', 'Design discussion with a diagram.'), ('Follow-up', 'Deeper question on the same topic.')],
    exam='Questions 1–40 also revise CLF-C02, AZ-900 and Cloud Digital Leader content; C-DAC placement interviews draw on all of them.',
    picture_h2='Four answer structures', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven kinds of interview questions, one by one', TYPES)],
    how_h2='Answering an interview question, step by step', how_intro='A scenario question answered with the structure.', how_anim=SOLVE,
    parts_h2='Six parts of interview preparation', parts_html=parts, lv='',
    myth_rows=[('A correct definition is enough.', 'Example and trade-off make it memorable.', 'Story.'), ('Freshers have nothing to show.', 'Labs and capstone are real experience.', 'Dialogue.'), ('Never say “I don’t know”.', 'Reason aloud and say how you would find out.', 'Deep dive.')],
    extra_secs=[('bank', 'Question bank', '60 interview questions with model answers', BANK), ('deep', 'Deep dive', 'Unknown answers, questions to ask, hands-on rounds', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Recognise seven kinds of interview questions.', 'Answer with the right structure in 60–90 seconds.', 'Use your own account facts as evidence.', 'Practise 60 questions from fresher to mid-level.', 'Prepare a complete interview pack.'],
    next_html='You have completed <b>Cloud Fundamentals</b>. Continue with the <a href="../../../aws/">AWS course</a>.',
    pre='<b>Before you start:</b> the whole course, especially 10.4 and 11.1.')
