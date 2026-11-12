import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
C = 'l15_compare.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('Buy servers, rent a dedicated server, or use the cloud — which one is cheaper and when?',
    'It depends on how you use them. With a <b>real</b> AWS Mumbai price ($0.10605/h for an m7i.large) and clearly marked assumptions for hardware, power and staff, 4 servers for 3 years cost about <b>₹24 lakh</b> owned, <b>₹9.4 lakh</b> in the cloud running 24×7, and <b>₹3.2 lakh</b> if you switch them off outside office hours. Getting them: <b>3–8 weeks</b> vs <b>2 minutes</b>.',
    ['On-premises, colocation, dedicated (bare-metal) and cloud servers compared.', 'Total cost of ownership (TCO): what to include.', 'When owning still wins.'])
cmap = concept_map('Concept map. Beginner: own vs rent. Intermediate: dedicated vs virtual, TCO. Advanced: hybrid, reserved pricing, when on-prem wins.',
    [[('ch', 'Challenges', 'Lesson 1.4', B + '01-introduction/04-challenges-and-limitations-of-cloud/'), ('ad', 'Advantages', 'Lesson 1.3', B + '01-introduction/03-characteristics-and-advantages-of-cloud/')],
     [('op', 'On-premises', 'you own all', None), ('col', 'Colocation', 'your box, their room', None), ('ded', 'Dedicated server', 'rented box', None), ('cl', 'Cloud VM', 'rented slice', None)],
     [('tco', 'TCO', '3-year cost', None), ('hyb', 'Hybrid', 'Lesson 3.1', B + '03-deployment-models/01-public-private-hybrid-and-community-cloud/'), ('pr', 'Pricing models', 'Lesson 5.5', B + '05-core-cloud-concepts/05-cloud-pricing-models/'), ('vz', 'Virtualization', 'Module 4', B + '04-virtualization/01-virtualization-and-hypervisors/')]],
    [('ch', 'op'), ('ad', 'cl'), ('op', 'col'), ('col', 'ded'), ('ded', 'cl'), ('op', 'tco'), ('cl', 'tco'), ('cl', 'hyb'), ('cl', 'pr'), ('ded', 'vz')],
    {'op', 'col', 'ded', 'cl', 'tco'},
    '<b>Next:</b> <a href="../06-real-world-applications-of-cloud/">1.6 Real-world applications</a>.')
whw = why_how_where(
    'This is the first decision in every IT project and a classic interview question. Wrong choice = wasted lakhs or a slow, stuck team.',
    'On-prem: you buy hardware, space, power, network, staff. Colocation: you buy hardware, rent the room. Dedicated: provider owns one physical server just for you. Cloud: provider owns everything; you rent virtual slices by the second.',
    'Banks and governments often run hybrid; startups go cloud-first; steady heavy workloads (big databases, render farms) sometimes stay on dedicated or on-prem.',
    'Our TCO uses marked assumptions (*): your hardware price, power tariff and staff cost change the answer. Always redo it with your numbers.')
def bars(hl=-1):
    vals = [('Own', 24.0, 'red'), ('Cloud 24×7', 9.4, 'blue'), ('Cloud office hrs', 3.2, 'green')]
    o = t(180, 16, '3-year cost of 4 servers (₹ lakh)', 8.4, 'ink', bold=True)
    for i, (lab, v, tn) in enumerate(vals):
        y = 30 + i * 34; w = v * 8.5
        o += box(110, y, w, 22, 'amber' if i == hl else tn, rx=4) + t(104, y + 15, lab, 8, 'ink', anchor='end', bold=True) + t(116 + w, y + 15, f'₹{v} L', 8, 'ink', anchor='start')
    return o + t(180, 140, 'own: weeks to get · cloud: minutes', 8, 'ink2')
scene_svg = scene('Bar chart of three-year cost: own servers 24 lakh rupees, cloud running all the time 9.4 lakh, cloud in office hours only 3.2 lakh.', bars(),
                  'Real cloud price, <tspan font-weight="700" class="s-acc">assumptions for own servers marked</tspan>.')
dialogue = '''K> Sir, the vendor quoted ₹10 lakh for 4 servers. That’s cheaper than 3 years of cloud, no?
A> The server price is only the start. Power, AC, rack space, network, spare parts and the person who fixes it at 2 am — that is total cost of ownership.
R> And the cloud bill depends on hours.
A> Exactly. Let’s compare honestly: own, dedicated, and cloud with real prices.'''
lv = '''
LEVELS> Own vs rent at three levels
L1> Car, taxi and rented car
      <ul>
        <li>On-prem = buying a car (you pay, park, service it). Dedicated server = monthly rented car, only yours. Cloud = Ola/Uber per ride: no parking, pay per km, more cars on festivals.</li>
      </ul>
L2> Four hosting options
      <ul>
        <li><b>On-premises:</b> everything in your building. <b>Colocation:</b> your servers in a provider’s data centre. <b>Dedicated server (bare metal):</b> one physical machine rented monthly. <b>Cloud:</b> virtual machines and services, self-service, per second.</li>
        <li>Cloud dedicated options also exist: AWS Dedicated Hosts / bare-metal instances, Azure Dedicated Host, Google sole-tenant nodes — for licensing or compliance.</li>
      </ul>
L3> TCO thinking
      <ul>
        <li>TCO = hardware + software licences + power/cooling + space + network + staff + downtime risk + refresh every 3–5 years. Cloud TCO = usage + data transfer + support plan + staff to run it well.</li>
        <li>Steady 24×7 loads: use reserved/savings pricing (up to roughly 70% off on-demand on AWS) or consider dedicated; spiky or experimental loads: on-demand cloud wins.</li>
      </ul>
/LEVELS
'''
mm = mindmap('Mind map comparing on-premises, colocation, dedicated servers and cloud by cost, speed, control and examples.', 'Where to run?', [
    ('On-premises', 'red', ['you own all', 'max control', 'CapEx']),
    ('Colocation', 'violet', ['your servers', 'their room/power', 'mixed']),
    ('Dedicated', 'blue', ['one rented box', 'monthly fee', 'no sharing']),
    ('Cloud', 'green', ['virtual, per second', 'elastic', 'OpEx']),
    ('TCO parts', 'amber', ['hardware, power', 'staff, space', 'downtime']),
    ('Pick when', 'card', ['steady → reserve', 'spiky → cloud', 'rules → hybrid'])], h=290)
lay = layers('Who manages which layer in each option: on-prem you manage all six; colocation the provider manages building, power and network; dedicated also hardware; cloud IaaS also virtualization.', [
    ('Application + data', 'you, in every option', 'blue'), ('Operating system', 'you (cloud IaaS too)', 'blue'),
    ('Virtualization', 'you · provider in cloud', 'green'), ('Physical server', 'you · provider in dedicated/cloud', 'green'),
    ('Network, power, cooling', 'you · provider in colo/dedicated/cloud', 'violet'), ('Building', 'you · provider in all rented options', 'violet')], hl=3, caption='Moving right (own → cloud) hands lower layers to the provider.')
DIS = figure('Dissection of one result line: option B cloud running 24 by 7, 936,430 rupees, nothing up front.',
    t(16, 22, 'One result line (real price, marked assumptions)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('B) cloud 24×7', 'blue', 1), ('₹9,36,430', 'green', 2), ('$0.10605/h', 'amber', 3), ('₹84/$ *', 'violet', 4)]) +
    legend(16, 84, [(1, 'Option', '4 VMs always on, 3 years'), (2, 'Total', '4 × h × 26,280 h × rate'), (3, 'Real price', 'm7i.large Mumbai'), (4, 'Assumption', 'exchange rate')], size=8, gap=15, w=90),
    h=156, caption='Change any assumption, rerun, decide.')
extra = '\n\n  <h3>Who manages which layer</h3>\n' + lay + '\n\n  <h3>Dissect one result</h3>\n' + DIS
types_html = table(['Option', 'You pay', 'Get it in', 'Control', 'Best for'], [
    ['On-premises', 'hardware + building + staff (up front)', 'weeks–months', 'full', 'strict rules, steady big loads, existing DC'],
    ['Colocation', 'hardware + rack rent', 'weeks', 'high', 'own kit without own building'],
    ['Dedicated server', 'monthly rent per machine', 'hours–days', 'high (no sharing)', 'steady loads, licences tied to cores'],
    ['Cloud VM', 'per second / hour', 'minutes', 'OS and up', 'spiky, new, global, experiments'],
    ['Cloud managed service', 'per use', 'minutes', 'settings only', 'databases, queues, AI without admin work']], minw=640)
warn = 'Never compare a server’s purchase price with a cloud monthly bill. Compare 3-year TCO on both sides, and include staff time, power and downtime for owned servers, and data transfer and support for cloud.'
steps = [
    ('Step 1 · The real cloud price', code('python', 'l15_compare.py', 'e = json.load(open("ec2_aps1_prices.json"))   # extracted from the AWS price list\nh = e["m7i.large"]["usd_hour"]', sec('== 1)', '== 2)')), 'From Lesson 1.3’s Mumbai EC2 price file.'),
    ('Step 2 · Three options, three years', code('python', 'l15_compare.py', 'own = hardware* + 36 × power/space* + 36 × staff*\ncloud_247 = 4 × h × 24 × 365 × 3 × ₹84*\ncloud_busy = 4 × h × 10 × 300 × 3 × ₹84*', sec('== 2)', '== 3)')), 'Assumptions (*) are illustrative; the cloud price is real.'),
    ('Step 3 · What the numbers say', code('python', 'l15_compare.py', 'compare B vs A, C vs A', sec('== 3)', '== 4)')), 'With these numbers cloud wins; with cheaper hardware or full-time heavy use, own/dedicated can win.'),
    ('Step 4 · Time to capacity', code('python', 'l15_compare.py', 'typical lead time', sec('== 4)')), 'Speed is often worth more than the cost difference.'),
]
see = [term([('m7i.large', W), ('$0.10605/h', G)], size=7.0), term([('A own ₹24.0 L', RD), ('B cloud ₹9.4 L', W), ('C office ₹3.2 L', G)], size=6.8),
       term([('C saves ₹20.8 L', G)], size=7.0), term([('own 3–8 weeks', RD), ('cloud 2 min', G)], size=7.0), term([('redo with', W), ('your numbers', W)], size=7.0)]
B1 = [bars(i) for i in (1, 0, 2, -1, -1)]
B1 = [b + cap(c, '', tn, y=146, h=20) for b, c, tn in zip(B1, ['Real price', 'Own: biggest', 'Switch off = cheapest', 'Weeks vs minutes', 'Your TCO'], ['blue', 'red', 'green', 'acc', 'violet'])]
two = anim_two('Own vs cloud', 'A 3-year TCO with real prices', 'Real outputs (price + marked assumptions)', 'The comparison', see, B1, ['Price.', 'Totals.', 'Verdict.', 'Speed.', 'Redo.'], ['Real.', 'Own.', 'Off.', 'Fast.', 'Yours.'])
pe = peel('Getting a new server, layer by layer', 'Own vs cloud. (Typical.)',
    [('Need', ''), ('Approve', ''), ('Order', ''), ('Install', ''), ('Configure', ''), ('Use', '')],
    [['Need', 'more capacity', '', ''], ['Approve', 'budget meeting', 'own: days', ''], ['Order', 'vendor quote', 'own: weeks', 'cloud: skip'],
     ['Install', 'rack, cable, power', 'own: days', 'cloud: skip'], ['Configure', 'OS + app', 'both', 'cloud: template'], ['Use', 'serve users', 'own: week 5', 'cloud: minute 2']],
    ['Need.', 'Approve.', 'Order.', 'Install.', 'Configure.', 'Use.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'College lab', '60 students, 3 months/year. (Typical.)', ('Cloud', 'Pay only during the course'), [
    ('Lab needed 3 months', '', 'Need.', 'blue'), ('Own: 60 PCs idle 9 months', '', 'Waste.', 'red'),
    ('Cloud VMs per student', 'office hours', 'Rent.', 'green'), ('Delete after course', '', 'Stop.', 'green'), ('Cost ≈ hours used', '', 'Save.', 'amber')], ['Need.', 'Idle.', 'Rent.', 'Delete.', 'Save.'], 'scenario-lab') + \
       five('Real-time scenario 2', 'Big steady database', 'Runs 24×7 for years. (Typical.)', ('Reserved / dedicated', 'Commit for discount'), [
    ('DB at 80% CPU always', '', 'Steady.', 'blue'), ('On-demand is costly', '', 'Problem.', 'amber'),
    ('Savings plan / reserved', '1–3 years', 'Commit.', 'green'), ('Or dedicated host', 'licences', 'Option.', 'violet'), ('Compare TCO yearly', '', 'Review.', 'amber')], ['Steady.', 'Costly.', 'Commit.', 'Dedicated.', 'Review.'], 'scenario-steady') + \
       five('Real-time scenario 3 · advanced', 'Hybrid bank', 'Core banking stays, apps move. (Typical.)', ('Hybrid', 'Best of both'), [
    ('Core system on-prem', 'regulated', 'Keep.', 'red'), ('Mobile app on cloud', 'elastic', 'Move.', 'green'),
    ('Private link between', 'VPN / Direct Connect', 'Connect.', 'blue'), ('Analytics in cloud', 'copies of data', 'Use.', 'green'), ('Plan full move later', '', 'Evolve.', 'violet')], ['Keep.', 'Move.', 'Link.', 'Analyse.', 'Evolve.'], 'scenario-hybrid')
clouds = vendor_tabs(
    '<p><b>AWS:</b> EC2 on-demand, Savings Plans / Reserved Instances for steady use, Dedicated Hosts and bare-metal (<code>*.metal</code>) instances, Outposts (AWS hardware in your data centre), Pricing Calculator and Migration Evaluator for TCO.</p>',
    '<p><b>Azure:</b> Virtual Machines, Reservations and Savings plan, Azure Dedicated Host, Azure Stack HCI / Azure Local (on-prem), Azure Hybrid Benefit for Windows/SQL licences, TCO calculator.</p>',
    '<p><b>Google Cloud:</b> Compute Engine with per-second billing, sustained-use and committed-use discounts, sole-tenant nodes, Bare Metal Solution, Google Distributed Cloud (on-prem), pricing calculator.</p>') + \
    cloud3([['On-demand VM', 'EC2 On-Demand', 'Pay-as-you-go VM', 'Compute Engine'], ['Commit discount', 'Savings Plans / RIs', 'Reservations / Savings plan', 'Committed use discounts'], ['Single-tenant', 'Dedicated Hosts', 'Dedicated Host', 'Sole-tenant nodes'], ['Cloud in your DC', 'Outposts', 'Azure Local', 'Distributed Cloud']])
prac = practical('Do your own TCO for 4 servers. No account needed.', [
    ('1 · Collect your own numbers', '<p>Ask a vendor (or search) for a 2-CPU, 8 GB rack server price, your electricity rate and rack/AC cost, and a part-time admin cost.</p>', 'Write them as variables.'),
    ('2 · Get a real cloud price', code('bash', 'terminal', 'python3 ec2_prices.py ec2_ap-south-1.json   # or use calculator.aws: m7i.large, Mumbai, Linux'), 'Lesson 1.3 shows how the file is read.'),
    ('3 · Edit and run the script', code('bash', 'terminal', 'nano l15_compare.py      # change the * lines\npython3 l15_compare.py'), 'Same output format as Step 2.'),
    ('4 · Add a savings-plan line', '<p>In the AWS Pricing Calculator choose “Compute Savings Plans, 3 years, no upfront” for the same instance and add option D.</p>', 'Steady 24×7 load usually drops a lot.'),
    ('5 · Write the recommendation', '<p>Three lines: cheapest option, fastest option, risk notes. This is what managers read.</p>', 'Keep it for the capstone.')],
    cleanup='Nothing created. Calculator estimates can be saved as a link; do not put company secrets in their names.')
mist = mistakes([
    ['Comparing server price vs one cloud month.', 'Ignoring power, staff, space, refresh.', 'Compare 3-year TCO on both sides.'],
    ['Running cloud VMs 24×7 when used 10 h/day.', 'Habit from owned servers.', 'Schedule stop/start; use auto scaling.'],
    ['Paying on-demand for steady load for years.', 'Not knowing commit discounts.', 'Savings plans / reserved / committed-use (Lesson 5.5).'],
    ['Calling a cloud VM a “dedicated server”.', 'Both look like one machine.', 'A VM shares hardware; dedicated = whole physical server for you.'],
    ['Forgetting data transfer in TCO.', 'Cloud egress is easy to miss.', 'Add expected GB out per month.']])
cert = certbox([
    ['AWS CLF-C02', 'Domain 1 · Cloud Concepts', 'Economics of the cloud: TCO, fixed vs variable cost, Pricing Calculator, Migration Evaluator; licensing (BYOL, Dedicated Hosts).'],
    ['AWS CLF-C02', 'Domain 4 · Billing & Pricing', 'On-Demand vs Reserved Instances vs Savings Plans vs Spot vs Dedicated Hosts.'],
    ['Azure AZ-900', 'Cloud concepts; cost management', 'CapEx vs OpEx, consumption-based model, TCO calculator, Hybrid Benefit.'],
    ['Google Cloud Digital Leader', 'Modernize infrastructure', 'On-prem vs cloud trade-offs, TCO.'],
    ['C-DAC PGCP-BDA', 'Session 2 / 5–6', 'Benefits and limitations; cloud vs traditional.']],
    [('Which model converts large up-front hardware purchases into monthly bills? (a) CapEx (b) OpEx (c) colocation', '<b>(b) OpEx</b> (operational expenditure).'),
     ('A licence requires per-physical-core counting. Which AWS option fits? ', '<b>Dedicated Hosts</b> (visibility of sockets/cores, BYOL).'),
     ('Which tool estimates savings of moving on-prem servers to AWS?', '<b>Migration Evaluator</b> (and the Pricing Calculator for costs).')])
proj = miniproject('Mini project: TCO comparison sheet',
    'Build a small CSV-based TCO tool that compares own, dedicated and cloud for any number of servers.',
    ['Make <code>inputs.csv</code> with columns: item, value, source (real/assumption).', 'Read it in Python (<code>csv</code> module); compute the three options for 1, 4 and 10 servers.', 'Print a table and save <code>tco_result.csv</code>.', 'Open the CSV in a spreadsheet and draw a bar chart.', 'Bonus: commit to GitHub with a README explaining assumptions.'],
    'A table and chart showing which option is cheapest for each size.', 'Python + CSV, spreadsheets, Git.')

# ===== v3 =====
def who():
    layers_ = ['Application + data', 'Operating system', 'Virtualization', 'Server hardware', 'Network', 'Power + cooling', 'Building']
    cols = [('On-premises', 7), ('Colocation', 4), ('Dedicated', 2), ('Cloud VM (IaaS)', 2), ('Managed (PaaS)', 1)]
    you_ = {0: 7, 1: 4, 2: 3, 3: 2, 4: 1}   # how many top layers YOU manage
    o = t(320, 16, 'Who manages which layer?', 11, 'ink', bold=True)
    for r, lab in enumerate(layers_):
        o += t(128, 50 + r * 30, lab, 8.4, 'ink', anchor='end', bold=True)
    for c, (name, _) in enumerate(cols):
        x = 140 + c * 100
        o += t(x + 46, 32, name, 8.2, 'ink', bold=True)
        for r in range(7):
            mine = r < you_[c]
            if c == 3 and r == 2: mine = False
            o += box(x, 36 + r * 30, 92, 24, 'blue' if mine else 'green', rx=4) + t(x + 46, 52 + r * 30, 'You' if mine else 'Provider', 8, 'ink', bold=not mine)
    o += box(150, 252, 14, 12, 'blue', rx=2) + t(170, 262, 'you buy, run and fix', 8, 'ink', anchor='start') + box(330, 252, 14, 12, 'green', rx=2) + t(350, 262, 'provider does it for you', 8, 'ink', anchor='start')
    return o
WHO = bigfig('Grid of seven layers (application and data, operating system, virtualization, server hardware, network, power and cooling, building) against four options. On-premises: you manage all seven. Colocation: you manage application, OS, virtualization and hardware. Dedicated server: you manage application, OS and virtualization. Cloud VM: you manage application and OS. Managed service (PaaS): you manage only application and data.', who(), h=276)
picture = ('  <p>All five options run the same app (the fifth, a managed service such as a managed database, is a preview of Module 2). The difference is <b>who looks after each layer</b>. Moving from left to right, the provider takes over more layers, and you pay for it as a service instead of buying it.</p>\n' + WHO +
           '\n  <p>The more layers you hand over, the faster you can start and the less you buy up front — but the less control you have. That trade-off is the whole decision.</p>')

# animation 1: getting 4 servers — own vs cloud
def lead_frame(k):
    own = ['Approve', 'Quotes + PO', 'Delivery', 'Install', 'Ready']
    o = t(180, 12, 'Getting 4 new servers', 9, 'ink', bold=True)
    o += t(10, 34, 'Own', 8.4, 'red', anchor='start', bold=True) + t(10, 112, 'Cloud', 8.4, 'green', anchor='start', bold=True)
    for i, s in enumerate(own):
        x = 50 + i * 62
        o += box(x, 26, 56, 40, 'amber' if i == k else ('red' if i < k else 'card'), rx=6) + t(x + 28, 42, s.split(':')[0][:12], 6.8, 'ink', bold=True) + t(x + 28, 56, ['day 1', 'week 2', 'week 4', 'week 5', 'week 6'][i], 6.6, 'ink2')
    o += box(50, 94, 56, 40, 'green' if k >= 0 else 'card', rx=6) + t(78, 110, 'API call', 6.8, 'ink', bold=True) + t(78, 124, 'minute 0', 6.6, 'ink2')
    o += box(112, 94, 56, 40, 'green', rx=6) + t(140, 110, '4 VMs ready', 6.8, 'ink', bold=True) + t(140, 124, 'minute 2', 6.6, 'ink2')
    o += t(260, 118, '✔ cloud done since week 0', 8, 'green', bold=True) if k >= 1 else ''
    return o
LD = [('Day 1 · Need is approved', 'Own: a budget meeting approves 4 servers. Cloud: someone runs one command.', 'Cloud: aws ec2 run-instances --count 4 … → 4 VMs in about 2 minutes'),
      ('Week 2 · Quotes and purchase order', 'Own: three vendor quotes, finance approval, purchase order.', 'Cloud users have already tested the app for two weeks'),
      ('Week 4 · Delivery', 'Own: hardware arrives; someone signs and checks it.', 'Lead time is the hidden cost of owning'),
      ('Week 5 · Rack, cable, install OS', 'Own: data-centre work, cabling, OS install, security patches.', 'In the cloud, the provider did all of this before you asked'),
      ('Week 6 · Ready', 'Own: servers finally serve users, six weeks later.', 'Speed and agility = one of the six advantages (Lesson 1.3)')]
fr = [lead_frame(k) + box(6, 158, 348, 62, 'blue', rx=8) + t(14, 174, h, 9, 'ink', anchor='start', bold=True) + t(14, 190, a, 7.4, 'ink', anchor='start') + t(14, 206, b, 7.2, 'ink2', anchor='start') for k, (h, a, b) in enumerate(LD)]
LEAD = anim_one('How it works', 'Four new servers: six weeks vs two minutes', 'Same need, two paths. Watch the own-server path crawl while the cloud path finishes at once.', 'Lead time', 'Animation comparing own servers (approval, purchase, delivery, install, ready in week 6) with cloud (API call, ready in 2 minutes).', fr, [x[0].split('·')[1].strip() + '.' for x in LD], delay=5500, hid='lead')

# animation 2: TCO builds up
def tco_frame(k):
    own_parts = [('Hardware', 10.0, 'red'), ('Power + space', 8.64, 'amber'), ('Staff', 5.4, 'violet')]
    o = t(180, 12, '3-year cost (₹ lakh)', 9, 'ink', bold=True)
    y0 = 140
    acc = 0
    for i, (n, v, tn) in enumerate(own_parts):
        if i <= k:
            o += box(60, y0 - (acc + v) * 4.8, 70, v * 4.8, tn, rx=2) + t(136, y0 - (acc + v / 2) * 4.8 + 3, f'{n} {v}', 7.4, 'ink', anchor='start')
            acc += v
    o += t(95, y0 + 12, 'Own', 8.4, 'red', bold=True) + (t(95, y0 - acc * 4.8 - 5, f'₹{acc:.1f} L', 8.4, 'ink', bold=True) if k >= 0 else '')
    if k >= 3:
        o += box(250, y0 - 9.36 * 4.8, 40, 9.36 * 4.8, 'blue', rx=2) + t(270, y0 - 9.36 * 4.8 - 5, '₹9.4 L', 8, 'ink', bold=True) + t(270, y0 + 12, '24×7', 7.6, 'blue', bold=True)
    if k >= 4:
        o += box(300, y0 - 3.21 * 4.8, 40, 3.21 * 4.8, 'green', rx=2) + t(320, y0 - 3.21 * 4.8 - 5, '₹3.2 L', 8, 'ink', bold=True) + t(320, y0 + 12, 'office hrs', 7.6, 'green', bold=True)
    return o
TC = [('Own: hardware first', '4 servers × ₹2.5 lakh = ₹10 lakh, paid on day 1 (assumption).', 'Capital expense: money leaves before any user is served'),
      ('Own: + power, AC, rack space', '₹6,000 per server per month × 36 months = ₹8.64 lakh (assumption).', 'Running costs people forget when comparing prices'),
      ('Own: + staff time', 'A part-time admin share, ₹15,000 × 36 = ₹5.4 lakh (assumption). Total ₹24 lakh.', 'Total cost of ownership (TCO), not purchase price'),
      ('Cloud running 24×7', '4 × m7i.large × $0.10605/h (real Mumbai price) × 3 years ≈ ₹9.4 lakh.', 'Nothing up front; includes hardware, power, building'),
      ('Cloud only in office hours', 'Stop the VMs at night and on holidays: ≈ ₹3.2 lakh.', 'Measured service rewards switching off')]
fr = [tco_frame(k) + box(6, 158, 348, 62, 'blue', rx=8) + t(14, 174, h, 9, 'ink', anchor='start', bold=True) + t(14, 190, a, 7.2, 'ink', anchor='start') + t(14, 206, b, 7.2, 'ink2', anchor='start') for k, (h, a, b) in enumerate(TC)]
TCOA = anim_one('How it works', 'Total cost of ownership, block by block', 'Watch the 3-year cost of owning build up, then compare it with the cloud (real price, marked assumptions).', 'TCO', 'Animation stacking hardware, power and staff costs for own servers to 24 lakh rupees, then cloud 24x7 at 9.4 lakh and office hours at 3.2 lakh.', fr, ['Hardware.', 'Power.', 'Staff.', 'Cloud 24×7.', 'Office hours.'], delay=6000, hid='tco')

parts = cards([
    ('On-premises', 'Your building, your servers, your staff. Full control, biggest up-front cost, slowest to change.', 'banks’ core systems'),
    ('Colocation', 'Your servers in a provider’s data centre: they give space, power, cooling and network.', 'own kit, no building'),
    ('Dedicated server (bare metal)', 'One whole physical server rented monthly; not shared with anyone.', 'steady loads, licences'),
    ('Cloud VM', 'A virtual slice of a shared server, created in minutes and billed per second.', 'spiky, new, global')]) + '\n  <h3>Side by side</h3>\n' + types_html

SUMMARY = big_mindmap('Mind map of lesson 1.5: four options, who manages what, TCO parts, speed, when to choose which, cloud dedicated options.', 'Where to run?', [
    ('4 options', 'blue', 'server', ['on-premises', 'colocation', 'dedicated', 'cloud VM']),
    ('Who manages', 'violet', 'gear', ['own: all 7 layers', 'cloud VM: app + OS', 'rest = provider']),
    ('TCO', 'red', 'meter', ['hardware + power', 'space + staff', 'downtime, refresh']),
    ('Speed', 'green', 'chart', ['own: ~6 weeks', 'cloud: ~2 minutes']),
    ('Choose', 'acc', 'app', ['spiky / new → cloud', 'steady → commit / dedicated', 'rules → hybrid']),
    ('Cloud dedicated', 'amber', 'shield', ['AWS Dedicated Hosts', 'Azure Dedicated Host', 'GCP sole-tenant'])], h=380, caption='Lesson 1.5 on one page.')
cert = cert + '\n  <h3>Lesson 1.5 on one page</h3>\n' + SUMMARY

assemble_v2(HERE, story_h2='The ₹10 lakh quote', hook_html=hk,
    narration='TiffinGo needs 4 more servers. A vendor quotes ₹10 lakh. Kabir thinks buying is cheaper than renting. Arjun Sir asks for a fair, three-year comparison.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='On-premises vs cloud vs dedicated servers',
    formal='<b>On-premises</b> infrastructure is owned and operated by the organisation in its own facility; <b>colocation</b> places owned hardware in a provider’s facility; a <b>dedicated server</b> (bare metal) is a single physical server leased to one customer; <b>cloud</b> resources are virtualized, multi-tenant, self-service and metered. They are compared by <b>total cost of ownership (TCO)</b>, provisioning time, control and compliance.',
    simple='Buy and run it yourself, rent one whole machine, or rent slices of the provider’s machines by the second.',
    interview=['“On-premises means we own and run everything; colocation puts our servers in someone else’s data centre; a dedicated server is a whole physical machine rented only to us; the cloud gives virtual resources on demand, billed per use.”', '“The choice depends on total cost of ownership, speed, control and compliance: cloud wins for variable or new workloads; steady 24×7 loads need reserved pricing, dedicated hosts or sometimes on-prem.”', '“With a real AWS Mumbai price, four servers for three years were about ₹9 lakh in the cloud versus about ₹24 lakh owned with our assumptions, and new capacity took minutes instead of weeks.”'],
    terms_rows=[('On-premises', 'Your building, your servers.'), ('Colocation', 'Your servers, their building.'), ('Dedicated / bare metal', 'One physical server just for you.'), ('Cloud VM', 'Virtual slice, per second.'), ('TCO', 'All costs over years.'), ('CapEx / OpEx', 'Up-front / running cost.'), ('Lead time', 'Time to get capacity.'), ('Hybrid', 'Mix of on-prem and cloud.')],
    exam='CapEx vs OpEx is asked in all three exams. AWS: Dedicated Hosts (BYOL, per-core licences) vs Dedicated Instances (hardware not shared, less visibility). Azure: Hybrid Benefit lowers licence cost. Compare TCO, not purchase price.',
    picture_h2='Who manages which layer', picture_html=picture,
    how_h2='Six weeks vs two minutes, and the true 3-year cost', how_intro='Two animations: the time to get new servers, and how total cost builds up for owning versus renting.', how_anim=LEAD + TCOA,
    parts_h2='The four options in one line each', parts_html=parts, lv='',
    myth_rows=[('Buying is always cheaper long term.', 'Not once power, space and staff are added.', 'Animation 2.'), ('Cloud must run 24×7.', 'Office hours: ₹3.2 L vs ₹9.4 L.', 'Animation 2.'), ('Cloud has no single-tenant option.', 'Dedicated Hosts, sole-tenant nodes.', 'Clouds tab.')],
    clouds_html=clouds, proof_h2='A three-year TCO with a real price', proof_intro='The cloud price is real (AWS Mumbai price list, 9 Nov 2026); own-server costs are illustrative assumptions marked *.', proof_steps=steps,
    practical_html=prac, mistakes_html=mist, cert_html='', project_html='', can_now=['Say who manages which layer in on-premises, colocation, dedicated, cloud VM and managed services.', 'Build a 3-year TCO and explain why purchase price is not enough.', 'Explain lead time: weeks for owned servers, minutes in the cloud.', 'Choose a pricing approach for steady vs spiky workloads.'],
    next_html='<a href="../06-real-world-applications-of-cloud/">1.6 Real-world applications: how industries put cloud building blocks together</a>.',
    pre='<b>Before you start:</b> <a href="../03-characteristics-and-advantages-of-cloud/">1.3</a>, <a href="../04-challenges-and-limitations-of-cloud/">1.4</a>.')
