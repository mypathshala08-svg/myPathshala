import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
CONCEPT = True
META = dict(module='01-introduction', lesson='05-on-premises-vs-cloud-vs-dedicated-servers', n='1.5', module_label='Module 1 · Introduction to cloud computing',
    title='On-premises vs cloud vs dedicated servers',
    desc='On-premises vs colocation vs dedicated (bare-metal) servers vs cloud: who manages which layer, CapEx vs OpEx, a three-year total cost of ownership (TCO) with a real AWS Mumbai price, when owning wins, AWS/Azure/GCP dedicated and hybrid options, exam questions and a TCO mini project.',
    og_desc='₹24 lakh vs ₹9.4 lakh vs ₹3.2 lakh: own servers vs cloud with a real AWS price and honest assumptions.',
    minutes=20, level='Beginner',
    lead='Buy, rent a whole machine, or rent slices by the second? We compare <b>four hosting options</b>, see <b>who manages which layer</b>, and build a <b>3-year TCO</b> with a real AWS Mumbai price.',
    chips=['On-prem · dedicated · cloud', 'Real TCO', 'CapEx vs OpEx', 'Diagrams + animations'])
MAIN = '''# 3-year TCO (₹). Cloud price real (m7i.large Mumbai); other values are assumptions.
usd, rate = 84.0, 0.10605
servers, years = 4, 3
own = servers * 250000 + servers * years * 12 * 6000 + years * 12 * 15000
cloud_247 = servers * rate * 24 * 365 * years * usd
cloud_office = servers * rate * 10 * 300 * years * usd
for name, v in [("own", own), ("cloud 24x7", cloud_247), ("cloud office hours", cloud_office)]:
    print(f"{name:20} ₹{v:12,.0f}")
'''
RUN = dict(heading='Run the code: your own TCO', intro='<p>Change the assumptions. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('own = servers * 250000 + servers * years * 12 * 6000 + years * 12 * 15000', 'Hardware + running + staff (assumptions).')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>.', code=None),
        dict(label='2 · Predict first: cheap hardware', hint='<b>Predict first:</b> server ₹80,000, no staff.', code='own = 4 * 80000 + 4 * 36 * 6000\ncloud = 4 * 0.10605 * 24 * 365 * 3 * 84\nprint(round(own), round(cloud))\n'),
        dict(label='3 · Savings plan', hint='Assume 40% off 24×7.', code='cloud = 4 * 0.10605 * 24 * 365 * 3 * 84\nprint(round(cloud * 0.6))\n'),
        dict(label='4 · Break-even hours', hint='Hours/day where cloud = own.', code='own = 2404000\nper_hour_day = 4 * 0.10605 * 365 * 3 * 84\nprint(round(own / per_hour_day, 1), "h/day")\n'),
        dict(label='5 · Spot the error', hint='Unfair compare.', expect='error', code='server_price, cloud_month = 250000, 26000\nif server_price > cloud_month:\n    raise ValueError("unfair: compare 3-year TCO, not one purchase vs one month")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC', intro='<p>Python 3. <b>Outputs are real for the cloud price.</b></p>',
    items=[dict(title='1 · Run the lab', cmd='python3 l15_compare.py', file='terminal', output='  B) cloud, running 24×7              ₹     936,430  (nothing up front)', note='Edit the * lines.')])
TRACE = dict(heading='One option step by step', intro='<p>Cloud 24×7.</p>',
    code='h = 0.10605\nhours = 24 * 365 * 3\nprint(round(4 * h * hours * 84))\n', notes={2: 'Hours :: 3 years.'})
WORKED_INTRO = 'Three hosting decisions.'
EXAMPLES = [
    dict(level='b', tag='choose', title='Short project', problem='<p>A 2-month analytics project.</p>', inp='needs', approach=['Short.', 'No purchase.', 'Cloud on-demand.'], code='print("cloud on-demand")\n', notes={1: 'Spiky/short.'}, tryit='Scenario 1.'),
    dict(level='i', tag='licence', title='Per-core licence', problem='<p>Software licensed per physical core.</p>', inp='rule', approach=['Need core visibility.', 'Dedicated host.', 'BYOL.'], code='print("AWS Dedicated Host / Azure Dedicated Host / GCP sole-tenant")\n', notes={1: 'Exam.'}, tryit='Clouds tab.'),
    dict(level='a', tag='break-even', title='Break-even', problem='<p>At how many hours/day is cloud as costly as owning?</p>', inp='numbers', approach=['Own TCO fixed.', 'Cloud per hour.', 'Divide.'], code='print(round(2404000 / (4 * 0.10605 * 365 * 3 * 84), 1))\n', notes={1: 'Beyond 24 → cloud always cheaper here.'}, tryit='RUN 4.')]
QUIZ = mix([{'q': 'Beginner: An up-front hardware purchase is…', 'options': ['OpEx', 'CapEx', 'SaaS', 'An SLA'], 'answer': 1, 'why': 'Capital expense: money spent before the servers do any work. Cloud usage is operating expense (OpEx).'}, {'q': 'Beginner: Fastest way to get 4 new servers…', 'options': ['Buy them from a vendor', 'Launch cloud VMs', 'Colocation', 'Build a data centre'], 'answer': 1, 'why': 'Animation 1: cloud VMs are ready in about 2 minutes; buying takes weeks (quotes, delivery, install).'}, {'q': 'Beginner: A whole physical server rented only to you is a…', 'options': ['Cloud VM', 'Dedicated (bare-metal) server', 'SaaS app', 'Container'], 'answer': 1, 'why': 'Dedicated = one physical machine for one customer. A cloud VM is a slice of a shared server.'}, {'q': 'Intermediate: In the “who manages which layer” picture, with a cloud VM you manage…', 'options': ['Everything', 'Only the application, data and operating system', 'Only the building', 'Nothing'], 'answer': 1, 'why': 'With IaaS the provider runs building, power, network, hardware and virtualization; you run the OS and everything above it.'}, {'q': 'Intermediate: Total cost of ownership (TCO) includes…', 'options': ['Only the hardware price', 'Hardware, power, space, network, staff, licences and downtime over years', 'Only the cloud bill', 'Only licences'], 'answer': 1, 'why': 'Animation 2 stacks hardware + power/space + staff to ₹24 lakh, far more than the ₹10 lakh purchase price.'}, {'q': 'Intermediate: Your own servers placed in a provider’s building is…', 'options': ['On-premises', 'Colocation', 'SaaS', 'Serverless'], 'answer': 1, 'why': 'Colocation: your hardware, their space, power, cooling and network.'}, {'q': 'Advanced: A steady 24×7 workload for 3 years on AWS should usually use…', 'options': ['Spot only', 'Savings Plans or Reserved Instances (or Dedicated Hosts for licences)', 'The free tier', 'Lambda'], 'answer': 1, 'why': 'Commit-based pricing gives large discounts for steady use; on-demand is best for variable or short workloads.'}, {'q': 'Advanced: Where do managed services (PaaS) sit in the layer picture?', 'options': ['You manage everything', 'Provider also manages the OS and runtime; you manage only app and data', 'Same as on-prem', 'Same as colocation'], 'answer': 1, 'why': 'PaaS (e.g. managed databases) takes over even the OS and runtime — the next step to the right, covered in Module 2.'}])
REVISION = ['On-prem, colocation, dedicated, cloud VM, managed service: each hands more layers to the provider.', 'Compare TCO (hardware, power, space, staff, downtime), never price vs one month.', 'Real: m7i.large Mumbai $0.10605/h; 3-yr: own ₹24 L*, cloud 24×7 ₹9.4 L, office hours ₹3.2 L (* assumptions).', 'Steady → commit discounts / dedicated; spiky or new → on-demand cloud; regulated → hybrid.', 'Lead time: weeks vs minutes.']
FAQ = [('Is a cloud VM a dedicated server?', 'No, a VM shares a physical host; dedicated/bare-metal options exist for single-tenant needs.'),
    ('When is on-prem better?', 'Very steady heavy loads with cheap power and existing staff, strict rules, or special hardware.'),
    ('What is Outposts / Azure Local?', 'Provider hardware running in your own data centre, managed like the cloud (hybrid).'),
    ('Why ₹84 per dollar?', 'A round assumption for illustration; use today’s rate.')]
PRACTICE_INTRO = 'TCO programs.'
PROBLEMS = [
    dict(level='easy', title='Hours in 3 years', stmt='24×365×3.', inp='ints', code='print(24 * 365 * 3)\n', explain='26,280.'),
    dict(level='easy', title='One VM 3 years', stmt='In US$.', inp='float', code='print(round(0.10605 * 26280, 2))\n', explain='$2,787.'),
    dict(level='easy', title='Rupees', stmt='×84.', inp='float', code='print(round(2787 * 84))\n', explain='≈₹2.3 lakh.'),
    dict(level='medium', title='Office share', stmt='3000 of 8760 h.', inp='ints', code='print(round(3000 / 8760 * 100), "%")\n', explain='34%.'),
    dict(level='medium', title='Saving %', stmt='C vs A.', inp='ints', code='print(round((2404000 - 320695) / 2404000 * 100), "%")\n', explain='87%.'),
    dict(level='medium', title='Cheapest', stmt='Min of dict.', inp='dict', code='d = {"own": 2404000, "247": 936430, "office": 320695}\nprint(min(d, key=d.get))\n', explain='office.'),
    dict(level='business', title='10 servers', stmt='Scale the cloud cost.', inp='float', code='print(round(936430 / 4 * 10))\n', explain='Linear.'),
    dict(level='business', title='Lead time', stmt='Days saved.', inp='ints', code='print(6 * 7, "days saved")\n', explain='~6 weeks.')]
SCN_INTRO = 'Hosting interview questions.'
SCENARIOS = (scn('Any company', 'Fresher', '“On-premises vs cloud?”', 'Classic comparison.', 'Can you compare on cost, speed, control?', '<p>“On-premises means we own and run everything — full control, high up-front cost, weeks to add capacity. Cloud means we rent virtual resources on demand — pay per use, minutes to scale, the provider runs the lower layers. We decide by TCO, speed, control and compliance.”</p>', '“Cloud is always cheaper.”') +
    scn('Product', 'Fresher', 'Dedicated server vs cloud VM', 'Hosting choice.', 'Do you know the difference?', '<ul><li>Dedicated: a whole physical server, not shared, monthly rent.</li><li>Cloud VM: a slice of a shared server, per-second billing, created in minutes.</li></ul>', '“They are the same.”') +
    scn('Finance', 'Mid-level', 'What goes into TCO?', 'Building a business case.', 'Do you include hidden costs?', '<ul><li>Hardware, power, cooling, space, network, staff, licences, downtime risk, refresh cycle; for cloud also data transfer and support.</li></ul>', 'Only the server quote.') +
    scn('Architecture', 'Senior', 'A big steady database', 'Runs 24×7 at high load.', 'Can you pick a cost model?', '<ul><li>Savings plans/reserved, dedicated hosts for licences, or keep on-prem — compare TCO yearly.</li></ul>', 'On-demand forever.'))
