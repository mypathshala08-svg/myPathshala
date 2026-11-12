import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
CONCEPT = True
META = dict(module='01-introduction', lesson='04-challenges-and-limitations-of-cloud', n='1.4', module_label='Module 1 · Introduction to cloud computing',
    title='Challenges and limitations of cloud',
    desc='Disadvantages and challenges of cloud computing: downtime, security misconfiguration, cost overruns, vendor lock-in, data residency (DPDP), latency, control, skills and migration, with a real Google Cloud incident feed analysis, fixes, mistakes and exam questions.',
    og_desc='8 incidents, one open 516 hours: the real challenges of cloud computing and how engineers handle them.',
    minutes=20, level='Beginner',
    lead='The cloud is not magic. We read a <b>real provider incident feed</b>, list the <b>nine challenges</b> engineers plan for, and learn the fix for each — the answer interviewers want to “what are the disadvantages of cloud?”.',
    chips=['9 challenges', 'Real incident feed', 'Fix for each', 'Diagrams + animations'])
MAIN = '''# Availability of one zone vs two independent zones (simplified)
zone = 0.999                     # each zone up 99.9% of the time
one = zone
two = 1 - (1 - zone) ** 2        # down only if BOTH are down
hours = 24 * 365
print(f"1 zone : {one:.4%}  ~{(1 - one) * hours:.1f} h down/year")
print(f"2 zones: {two:.6%}  ~{(1 - two) * hours * 60:.1f} min down/year")
'''
RUN = dict(heading='Run the code: why two zones help', intro='<p>A simplified availability model. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('two = 1 - (1 - zone) ** 2        # down only if BOTH are down', 'Independent failures multiply.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>.', code=None),
        dict(label='2 · Predict first: 99%', hint='<b>Predict first:</b> zone 99%.', code='z = 0.99\nprint(1 - (1 - z) ** 2)\n'),
        dict(label='3 · Downtime', hint='99.9% per month.', code='print(round(0.001 * 730 * 60), "minutes/month")\n'),
        dict(label='4 · Egress', hint='1 TB out at $0.09/GB (example).', code='print(1000 * 0.09, "US$")\n'),
        dict(label='5 · Spot the error', hint='Public bucket.', expect='error', code='bucket = {"public": True, "data": "customers.csv"}\nif bucket["public"]:\n    raise PermissionError("customer data in a public bucket: turn on Block Public Access")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC', intro='<p>Python 3, internet. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Run the lab', cmd='python3 l14_challenges.py', file='terminal', output='  median 10.7 h · 90th percentile 516.0 h · longest 516.0 h', note='Numbers change as incidents are added.')])
TRACE = dict(heading='Duration step by step', intro='<p>Hours between two times.</p>',
    code='from datetime import datetime\nb = datetime(2026, 6, 5, 0)\ne = datetime(2026, 6, 26, 12)\nprint((e - b).total_seconds() / 3600)\n', notes={3: 'Difference :: in hours.'})
WORKED_INTRO = 'Three risk decisions.'
EXAMPLES = [
    dict(level='b', tag='risk', title='Name the risk', problem='<p>Company cannot move away because of proprietary services.</p>', inp='story', approach=['Hard to leave.', 'Provider-specific.', 'Lock-in.'], code='print("vendor lock-in")\n', notes={1: 'Types table.'}, tryit='Scenario 3.'),
    dict(level='i', tag='fix', title='Pick the fix', problem='<p>App down when one data centre fails.</p>', inp='story', approach=['Single AZ.', 'Add second AZ.', 'Load balancer.'], code='print("multi-AZ + load balancer")\n', notes={1: 'Peel.'}, tryit='RUN.'),
    dict(level='a', tag='law', title='Residency', problem='<p>Health records of Indian patients.</p>', inp='rule', approach=['Personal data.', 'Indian region.', 'Encrypt, audit.'], code='print({"region": "ap-south-1", "encrypt": True, "logs": True})\n', notes={1: 'Compliance.'}, tryit='Types.')]
QUIZ = mix([{'q': 'Beginner: Which is a disadvantage of cloud computing?', 'options': ['Elasticity', 'Dependency on the internet', 'Pay-as-you-go', 'Self-service'], 'answer': 1, 'why': 'If users or the office cannot reach the internet, they cannot reach the cloud. The other options are advantages.'}, {'q': 'Beginner: Most cloud data leaks are caused by…', 'options': ['Provider employees', 'Customer misconfiguration (e.g. public buckets)', 'Weather', 'Bugs in Linux'], 'answer': 1, 'why': 'Animation 1: a bucket made public “for a quick test” is the classic leak. The provider secures the data centre; you secure your settings.'}, {'q': 'Beginner: It is hard to move to another provider because you used its special services. This is…', 'options': ['Latency', 'Vendor lock-in', 'Pooling', 'An SLA'], 'answer': 1, 'why': 'Proprietary services and egress fees create lock-in. Reduce it with containers, Terraform and open data formats.'}, {'q': 'Intermediate: Your app slows down because another customer’s VM on the same host uses too much CPU. This is…', 'options': ['Lock-in', 'A noisy neighbour', 'Compliance', 'Egress'], 'answer': 1, 'why': 'In shared (pooled) hardware, one tenant’s heavy use can affect others. Providers limit it; for strict needs use bigger/dedicated instances.'}, {'q': 'Intermediate: Best design to survive a single data-centre (zone) failure…', 'options': ['A bigger VM', 'Run in at least two Availability Zones behind a load balancer', 'More RAM', 'Delete logs'], 'answer': 1, 'why': 'Animation 2: the multi-zone app keeps running from zone B when zone A fails.'}, {'q': 'Intermediate: Data leaving the cloud to the internet is charged as…', 'options': ['Ingress', 'Egress / data transfer out', 'Storage', 'It is always free'], 'answer': 1, 'why': 'Uploading (ingress) is usually free; data transfer out (egress) is billed and is a common surprise cost.'}, {'q': 'Advanced: India’s 2023 personal data protection law is the…', 'options': ['GDPR', 'Digital Personal Data Protection (DPDP) Act', 'HIPAA', 'SOX'], 'answer': 1, 'why': 'The DPDP Act 2023 governs personal data of Indians; sector rules (e.g. RBI for payments) add residency requirements. GDPR is the EU law.'}, {'q': 'Advanced: Moving an application to cloud VMs without changing it is called…', 'options': ['Refactor', 'Rehost (“lift and shift”)', 'Retire', 'Repurchase'], 'answer': 1, 'why': 'One of the 7 Rs of migration. Refactor = redesign for the cloud; repurchase = switch to SaaS; retire = switch off.'}])
REVISION = ['9 challenges: downtime, security, cost, lock-in, compliance, latency, control, skills, migration (+ noisy neighbours, interoperability).', 'Most breaches = customer misconfiguration; fix with Block Public Access, least privilege, MFA, logs.', 'Survive outages: multiple AZs, health checks, a DR region; read the SLA (credits, not your losses).', 'Budgets on day one; watch egress; Indian regions for regulated data (DPDP, RBI).', '7 Rs of migration: retire, retain, rehost, relocate, repurchase, replatform, refactor.']
FAQ = [('Is the cloud less secure than my own server?', 'Usually more secure at the physical/infra level; risk moves to your configuration.'),
    ('Can I avoid lock-in fully?', 'No, but containers, Terraform, open formats and an exit plan reduce it.'),
    ('What if the internet is down?', 'Users cannot reach the cloud; use redundant ISPs for offices, and design apps to degrade gracefully.'),
    ('Do providers pay for outages?', 'SLAs give service credits, not your lost business (Lesson 5.4).')]
PRACTICE_INTRO = 'Risk programs.'
PROBLEMS = [
    dict(level='easy', title='Downtime 99.9%', stmt='Hours per year.', inp='float', code='print(round(0.001 * 8760, 2))\n', explain='8.76 h.'),
    dict(level='easy', title='Downtime 99.99%', stmt='Minutes per year.', inp='float', code='print(round(0.0001 * 8760 * 60))\n', explain='53 min.'),
    dict(level='easy', title='Days', stmt='516 hours in days.', inp='int', code='print(516 / 24)\n', explain='21.5.'),
    dict(level='medium', title='Two zones', stmt='Combined availability.', inp='float', code='z = 0.995\nprint(round(1 - (1 - z) ** 2, 6))\n', explain='99.9975%.'),
    dict(level='medium', title='Risk score', stmt='likelihood × impact.', inp='dict', code='r = {"outage": (2, 5), "leak": (3, 5), "bill": (4, 3)}\nprint(sorted(r, key=lambda k: -r[k][0] * r[k][1]))\n', explain='Prioritise.'),
    dict(level='medium', title='Median', stmt='Median hours.', inp='list', code='h = sorted([2, 5, 10.7, 12, 30, 516])\nprint((h[2] + h[3]) / 2)\n', explain='11.35.'),
    dict(level='business', title='Idle GPU', stmt='30 days × $3/h.', inp='floats', code='print(30 * 24 * 3, "US$")\n', explain='$2,160.'),
    dict(level='business', title='Egress', stmt='5 TB out.', inp='float', code='print(5000 * 0.09)\n', explain='$450 (example rate).')]
SCN_INTRO = 'Risk interview questions.'
SCENARIOS = (scn('Any company', 'Fresher', '“What are the disadvantages of cloud?”', 'Checks balanced thinking.', 'Do you know risks AND fixes?', '<p>“Internet dependency and outages, security risks mostly from misconfiguration, cost overruns, vendor lock-in, compliance and data residency, latency, less control and a skills gap. We reduce them with multi-AZ design, least-privilege IAM and MFA, budgets and tags, open standards and Indian regions for regulated data.”</p>', '“There are none.”') +
    scn('Bank', 'Mid-level', 'A bucket with customer data was public.', 'Incident call.', 'Can you respond step by step?', '<ul><li>Block public access now; check access logs for downloads.</li><li>Rotate any exposed keys, inform security/legal (DPDP), add guardrails (account-level block, config rules).</li></ul>', 'Deleting logs or hiding it.') +
    scn('Startup', 'Mid-level', 'Bill doubled this month', 'Founder is worried.', 'Do you know the usual causes?', '<ul><li>Idle VMs/disks, NAT gateways, data transfer out, forgotten test environments.</li><li>Budgets, tags, Cost Explorer by service, cleanup.</li></ul>', '“Change provider.”') +
    scn('Architecture', 'Senior', 'Design for a zone outage', 'E-commerce sale next week.', 'Do you design for failure?', '<ul><li>Two or more AZs, load balancer health checks, multi-AZ database, backups, tested DR runbook.</li></ul>', 'Single big server.'))
