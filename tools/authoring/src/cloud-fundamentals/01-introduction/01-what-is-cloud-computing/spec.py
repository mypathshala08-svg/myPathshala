import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
CONCEPT = True
META = dict(module='01-introduction', lesson='01-what-is-cloud-computing', n='1.1', module_label='Module 1 · Introduction to cloud computing',
    title='What is cloud computing?',
    desc='Cloud computing from zero: the NIST definition with its five characteristics, three service models and four deployment models, the layers of a cloud, AWS vs Azure vs Google Cloud, a hands-on look at real cloud infrastructure, common mistakes and exam questions for AWS CLF-C02, AZ-900 and Cloud Digital Leader.',
    og_desc='42 AWS regions, 10,744 IP ranges and a Diwali crash: what cloud computing really is, with real data and exam tips.',
    minutes=22, level='Beginner',
    lead='Cloud computing means <b>renting</b> computers, storage and software over the internet and paying only for what you use. We learn the NIST definition, see the layers, prove the cloud is real hardware with <b>real data</b>, compare AWS, Azure and Google Cloud, and finish with exam questions and a mini project.',
    chips=['NIST 5 characteristics', 'AWS · Azure · GCP', 'CLF-C02 · AZ-900 · CDL', 'Diagrams + animations'])
MAIN = '''# Own servers vs cloud for one festival year (simplified, rupees)
daily_orders = [3000] * 350 + [12000] * 15          # 15 festival days
per_server = 1000                                    # orders one server handles per day
own_servers = max(daily_orders) // per_server        # must buy for the peak
own_cost = own_servers * 90000                       # buy once (per year share)
cloud_cost = sum(-(-d // per_server) * 250 for d in daily_orders)   # 250 per server-day
print("own servers:", own_servers, " cost:", own_cost)
print("cloud server-days:", sum(-(-d // per_server) for d in daily_orders), " cost:", cloud_cost)
print("cheaper:", "cloud" if cloud_cost < own_cost else "own")
'''
RUN = dict(heading='Run the code: own vs cloud for a festival year', intro='<p>A simplified cost model. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('own_servers = max(daily_orders) // per_server        # must buy for the peak', 'Owned capacity must cover the busiest day.'), ('cloud_cost = sum(-(-d // per_server) * 250 for d in daily_orders)   # 250 per server-day', 'Cloud: pay per server per day actually used.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>.', code=None),
        dict(label='2 · Predict first: steady load', hint='<b>Predict first:</b> no festival, 3000 orders every day. Which is cheaper?', code='d = [3000] * 365\nown = 3 * 90000\ncloud = sum(3 * 250 for _ in d)\nprint(own, cloud, "cloud" if cloud < own else "own")\n'),
        dict(label='3 · Five traits', hint='List NIST’s five characteristics.', code='traits = ["on-demand self-service", "broad network access", "resource pooling", "rapid elasticity", "measured service"]\nfor i, t in enumerate(traits, 1):\n    print(i, t)\n'),
        dict(label='4 · Classify', hint='Service model of each product.', code='m = {"Gmail": "SaaS", "EC2 VM": "IaaS", "App Engine": "PaaS"}\nfor k, v in m.items():\n    print(f"{k:10} {v}")\n'),
        dict(label='5 · Spot the error', hint='A forgotten VM.', expect='error', code='running_hours = 24 * 30\nbudget_alert = None\nif budget_alert is None and running_hours > 100:\n    raise RuntimeError("VM left running 720 h with no budget alert: set alerts and delete after labs")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC', intro='<p>Any computer with Python 3 and internet. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Run the lab', cmd='python3 l11_cloud_is_real.py', file='terminal', output='  regions in the file: 42', note='Numbers grow over time.'),
           dict(title='2 · One-liner', cmd="curl -s https://ip-ranges.amazonaws.com/ip-ranges.json | jq '.prefixes | length'", file='terminal', output='10744', note='Needs jq.')])
TRACE = dict(heading='Elasticity step by step', intro='<p>Servers follow orders.</p>',
    code='orders = [3000, 12000, 3000]\nfor o in orders:\n    servers = -(-o // 1000)\n    print(o, "orders ->", servers, "servers")\n', notes={3: 'Ceiling :: round up servers.'})
WORKED_INTRO = 'Three “is this cloud?” decisions.'
EXAMPLES = [
    dict(level='b', tag='NIST', title='Is it cloud?', problem='<p>A company rents a fixed server for 3 years, booked by email, fixed monthly fee.</p>', inp='traits',
         approach=['On-demand? No (email).', 'Elastic? No.', 'Measured? No.'], code='print("hosting, not cloud: missing on-demand, elasticity, metering")\n', notes={1: 'Traditional hosting.'}, tryit='Levels: NIST.'),
    dict(level='i', tag='benefit', title='Name the benefit', problem='<p>Startup launched in a week without buying hardware.</p>', inp='story',
         approach=['No up-front cost.', 'Fast to start.', 'Benefit: agility + OpEx.'], code='print(["speed and agility", "trade CapEx for OpEx"])\n', notes={1: 'Exam wording.'}, tryit='Exam tip.'),
    dict(level='a', tag='region', title='Choose a place', problem='<p>Indian bank, data must stay in India.</p>', inp='rule',
         approach=['Indian region.', 'Second Indian region for backup.', 'Encrypt.'], code='print({"aws": ["ap-south-1", "ap-south-2"], "gcp": ["asia-south1", "asia-south2"]})\n', notes={1: 'Real region codes.'}, tryit='Step 3.')]
QUIZ = mix([{'q': 'Beginner: Cloud computing mainly means…', 'options': ['Buying servers for your office', 'Renting IT resources over the internet and paying per use', 'Using only Google Drive', 'Installing software from a CD'], 'answer': 1, 'why': 'Cloud = on-demand IT resources (servers, storage, software) over the internet with pay-as-you-go pricing. Google Drive is just one SaaS example.'}, {'q': 'Beginner: Which is one of NIST’s five essential characteristics?', 'options': ['Open-source software', 'Rapid elasticity', 'Free forever', 'Single tenant'], 'answer': 1, 'why': 'The five are on-demand self-service, broad network access, resource pooling, rapid elasticity and measured service. Open source and “free” are not part of the definition.'}, {'q': 'Beginner: In the order animation, which part turns api.tiffingo.in into an IP address?', 'options': ['Load balancer', 'DNS', 'Database', 'Meter'], 'answer': 1, 'why': 'DNS (Domain Name System) is the internet’s phone book: name → IP address. Step 2 of the animation; AWS Route 53, Azure DNS, Cloud DNS.'}, {'q': 'Intermediate: Paying only for the VM-hours you used is which characteristic?', 'options': ['Resource pooling', 'Measured service', 'Broad network access', 'Self-service'], 'answer': 1, 'why': 'Usage is metered and billed (animation step 8). Pooling is about sharing hardware; self-service is about creating resources yourself.'}, {'q': 'Intermediate: Many customers’ VMs running on the same physical server is…', 'options': ['Elasticity', 'Resource pooling', 'Measured service', 'SaaS'], 'answer': 1, 'why': 'Resource pooling (multi-tenancy): the provider shares big servers among customers, each in an isolated VM (picture card 3).'}, {'q': 'Intermediate: The AWS region code for Mumbai is…', 'options': ['us-east-1', 'ap-south-1', 'asia-south1', 'centralindia'], 'answer': 1, 'why': 'ap-south-1 = AWS Mumbai; ap-south-2 = Hyderabad. asia-south1 is Google’s Mumbai, centralindia is Azure’s Pune region.'}, {'q': 'Advanced: “Trade capital expense for variable expense” means…', 'options': ['Buy more servers up front', 'Pay as you go instead of buying up front', 'Pay a fixed monthly fee forever', 'Use only the free tier'], 'answer': 1, 'why': 'Capital expense (CapEx) = big up-front purchase; variable/operating expense (OpEx) = pay for what you use each month. This is AWS’s first cloud advantage.'}, {'q': 'Advanced: Which layer of the cloud architecture does the provider NOT run?', 'options': ['Infrastructure (servers)', 'Storage', 'Front end on the user’s phone', 'Runtime cloud'], 'answer': 2, 'why': 'The front end (your app, browser or CLI) is on the user’s side; all back-end layers (application hosting, service, runtime, storage, infrastructure) run in the provider’s data centre.'}])
REVISION = ['Cloud = on-demand IT resources over the internet, pay as you go.', 'NIST: 5 characteristics (self-service, network access, pooling, elasticity, measured), 3 service models (IaaS, PaaS, SaaS), 4 deployment models (public, private, hybrid, community).', 'Architecture: front end (app, browser, CLI) → internet → back end (application, service, runtime, storage, infrastructure) + management + security.', 'One order: phone → DNS → load balancer → VM → database → reply; auto scaling on Diwali; every second metered.', 'India regions: AWS ap-south-1/2, Azure Central/South/West India, Google asia-south1/2.', 'Always: budget alert first, right region, clean up after labs.']
FAQ = [('Is the cloud safe?', 'The provider secures buildings, hardware and its services; you secure your accounts, data and settings (shared responsibility, Module 9).'),
    ('Do I need a credit card to learn?', 'Not for this course’s concept lessons. For AWS labs you need an account; set budgets first.'),
    ('Which cloud should I learn first?', 'Concepts are the same; AWS has the largest share and the most jobs, so our hands-on course starts there, with Azure and GCP names side by side.'),
    ('Is Google Drive cloud computing?', 'Yes, it is SaaS: finished software delivered from the cloud.'),
    ('Which certification after this course?', 'AWS Cloud Practitioner (CLF-C02), Azure AZ-900 or Google Cloud Digital Leader: each lesson has a Certification corner.')]
PRACTICE_INTRO = 'Cloud programs.'
PROBLEMS = [
    dict(level='easy', title='Server-days', stmt='Servers for 7500 orders.', inp='int', code='print(-(-7500 // 1000))\n', explain='8.'),
    dict(level='easy', title='Monthly bill', stmt='3 servers × 30 days × ₹250.', inp='ints', code='print(3 * 30 * 250)\n', explain='₹22,500.'),
    dict(level='easy', title='Hours', stmt='VM forgotten for a month.', inp='int', code='print(24 * 30, "hours")\n', explain='720.'),
    dict(level='medium', title='Peak ratio', stmt='Peak vs normal.', inp='ints', code='print(12000 / 3000)\n', explain='×4.'),
    dict(level='medium', title='Region filter', stmt='India regions.', inp='list', code='r = ["us-east-1", "ap-south-1", "eu-west-1", "ap-south-2"]\nprint([x for x in r if x.startswith("ap-south")])\n', explain='Mumbai, Hyderabad.'),
    dict(level='medium', title='Utilisation', stmt='Average use of 12 owned servers.', inp='ints', code='print(round((350 * 3 + 15 * 12) / (365 * 12) * 100), "%")\n', explain='~28%: mostly idle.'),
    dict(level='business', title='Saving', stmt='Own vs cloud.', inp='ints', code='own, cloud = 1080000, 307500\nprint("save", own - cloud)\n', explain='From the RUN model.'),
    dict(level='business', title='Alert', stmt='Budget alert.', inp='floats', code='spend, budget = 1.2, 0.0\nprint("ALERT" if spend > budget else "ok")\n', explain='Zero-spend alert.')]
SCN_INTRO = 'Cloud interview questions.'
SCENARIOS = (scn('Any company · fresher', 'Fresher', '“What is cloud computing?”', 'The very first question in most cloud interviews.', 'Can you give a precise definition and an example, not just “storing files online”?', '<p>“Cloud computing is the on-demand delivery of IT resources — servers, storage, databases, software — over the internet with pay-as-you-go pricing. NIST defines it by five characteristics: on-demand self-service, broad network access, resource pooling, rapid elasticity and measured service. For example, a food-delivery app adds servers for Diwali and removes them after, paying only for that week.”</p>', 'Saying “cloud means Google Drive” or “cloud means the internet”.') +
    scn('Startup', 'Fresher', 'Why should a startup use cloud?', 'The founder has ₹5 lakh and an idea.', 'Do you know the business benefits, not just the technology?', '<ul><li>No up-front hardware (CapEx → OpEx).</li><li>Start in minutes, experiment cheaply, delete what fails.</li><li>Scale automatically if the idea succeeds; go global later.</li></ul>', '“Because it is free.” It is not; set budgets.') +
    scn('Bank', 'Mid-level', 'Where should Indian customer data live?', 'A bank wants to move an app to the cloud.', 'Do you think about data residency and resilience?', '<ul><li>Use Indian regions (e.g. AWS Mumbai + Hyderabad for DR).</li><li>Encrypt data, keep audit logs, follow RBI / DPDP rules.</li></ul>', 'Picking the default US region.') +
    scn('Ops', 'Mid-level', 'The first cloud bill is much higher than expected.', 'Finance is upset after a month.', 'Do you understand measured service and cost control?', '<ul><li>Resources kept running (VMs, disks, IPs, NAT gateways) are billed even when idle.</li><li>Fix: budgets and alerts, tags, a cleanup checklist, stop dev servers at night.</li></ul>', 'Blaming the provider.'))
