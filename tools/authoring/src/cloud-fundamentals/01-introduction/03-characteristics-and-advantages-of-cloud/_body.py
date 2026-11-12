import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
C = 'l13_measured.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('“Pay only for what you use” — how exactly does the cloud measure that, and what does it cost?',
    'Every resource has a meter, and AWS publishes the price list as JSON. In Mumbai today: S3 storage <b>$0.025 per GB-month</b>, a request <b>$0.000005</b>, a t3.micro virtual machine <b>$0.0112 per hour</b>. TiffinGo’s 500 GB of menu photos cost about <b>$13.50 a month</b>; a 2-hour lab on a t3.medium costs <b>$0.09</b>. Delete them, and the bill stops.',
    ['The capacity-vs-demand picture behind every cloud decision.', 'Six AWS advantages, the AZ-900 benefits, and how exams phrase them.', 'How a real bill is made from a real price list, and scale up vs scale out.'])
cmap = concept_map('Concept map. Beginner: five characteristics. Intermediate: six advantages. Advanced: price list, pricing models, economies of scale.',
    [[('wc', 'What is cloud', 'Lesson 1.1', B + '01-introduction/01-what-is-cloud-computing/'), ('hi', 'History', 'Lesson 1.2', B + '01-introduction/02-history-and-evolution-of-cloud-computing/')],
     [('od', 'On-demand', 'self-service', None), ('bn', 'Broad network', 'any device', None), ('rp', 'Pooling', 'multitenant', None), ('re', 'Elasticity', 'scale in/out', None)],
     [('ms', 'Measured', 'price list', None), ('adv', '6 advantages', 'AWS wording', None), ('ch', 'Challenges', 'Lesson 1.4', B + '01-introduction/04-challenges-and-limitations-of-cloud/'), ('pm', 'Pricing models', 'Lesson 5.5', B + '05-core-cloud-concepts/05-cloud-pricing-models/')]],
    [('wc', 'od'), ('hi', 'rp'), ('od', 'bn'), ('rp', 're'), ('re', 'ms'), ('ms', 'adv'), ('adv', 'ch'), ('ms', 'pm')],
    {'od', 'bn', 'rp', 're', 'ms', 'adv'},
    '<b>Next:</b> <a href="../04-challenges-and-limitations-of-cloud/">1.4 Challenges and limitations</a>.')
whw = why_how_where(
    'Exams and interviews ask the five characteristics and six advantages almost word for word; managers decide cloud vs own servers on these benefits.',
    'Self-service portals and APIs give on-demand access; data centres are reached over the internet; virtualization pools hardware; auto scaling adds and removes capacity; meters record every GB, hour and request into a bill.',
    'Startups (speed), seasonal businesses (elasticity), global apps (go global in minutes), analytics (big compute for a short time).',
    'Benefits only appear if you use them: forgotten resources, wrong sizes and data transfer can erase savings.')
def meters(hl=-1):
    items = [('Storage', '$0.025/GB-mo', 'blue'), ('Requests', '$0.005/1,000', 'green'), ('VM t3.micro', '$0.0112/h', 'violet'), ('VM t3.medium', '$0.0448/h', 'acc')]
    o = t(180, 16, 'Every resource has a meter (AWS Mumbai, real prices)', 8.2, 'ink', bold=True)
    for i, (a, p, tn) in enumerate(items):
        x = 14 + i * 86
        o += box(x, 28, 76, 70, 'amber' if i == hl else tn, rx=8)
        o += f'<circle cx="{x + 38}" cy="56" r="16" style="fill:none;stroke:currentColor" class="s-ink2" stroke-width="1.5"/><line x1="{x + 38}" y1="56" x2="{x + 48}" y2="46" stroke="#D64545" stroke-width="2"/>'
        o += t(x + 38, 84, a, 7.6, 'ink', bold=True) + t(x + 38, 94, p, 7, 'ink2')
    return o + t(180, 128, 'Bill = Σ (usage × price). Delete → meter stops.', 8.4, 'ink', bold=True)
scene_svg = scene('Four meters: S3 storage 0.025 dollars per GB-month, requests 0.005 dollars per thousand, t3.micro 0.0112 dollars per hour, t3.medium 0.0448 dollars per hour.', meters(),
                  'Real Mumbai prices from AWS’s public price list, 9 Nov 2026.')
dialogue = '''K> Sir, the finance team doesn’t trust “pay only for what you use”. They want numbers.
A> Good! AWS publishes every price as a file. We will read the Mumbai price list ourselves and calculate TiffinGo’s photo bill.
R> And the five characteristics from 1.1 — will we see each one?
A> Yes, one by one, and the six advantages exams love. Let’s go.'''
lv = '''
LEVELS> Characteristics and advantages at three levels
L1> Like a mobile prepaid plan
      <ul>
        <li>You recharge yourself (on-demand), use it anywhere (network access), share towers with millions (pooling), upgrade data for a weekend (elasticity), and see exact usage in the app (measured).</li>
      </ul>
L2> The five NIST characteristics
      <ul>
        <li><b>On-demand self-service:</b> get resources without calling anyone. <b>Broad network access:</b> through standard networks from phones, laptops, servers.</li>
        <li><b>Resource pooling:</b> provider hardware is shared by many tenants, location-independent. <b>Rapid elasticity:</b> scale out and in, seemingly unlimited. <b>Measured service:</b> usage metered, reported, billed.</li>
      </ul>
L3> The six advantages (AWS wording)
      <ul>
        <li>Trade fixed (capital) expense for variable expense · benefit from massive economies of scale · stop guessing capacity · increase speed and agility · stop spending money running and maintaining data centres · go global in minutes.</li>
        <li>Other lists add: high availability, reliability, security tooling, sustainability (shared efficient data centres), innovation (managed AI, analytics).</li>
      </ul>
/LEVELS
'''
mm = mindmap('Mind map: five NIST characteristics and six advantages of cloud computing, plus extra benefits and the price list.', 'Cloud benefits', [
    ('NIST traits', 'blue', ['self-service', 'network access', 'pooling', 'elasticity', 'measured']),
    ('Money', 'green', ['CapEx → OpEx', 'economies of scale', 'no data centre']),
    ('Speed', 'violet', ['agility', 'minutes not weeks', 'experiment cheaply']),
    ('Scale', 'acc', ['stop guessing', 'auto scaling', 'go global']),
    ('Extras', 'card', ['availability', 'security tools', 'sustainability']),
    ('Proof', 'amber', ['price list JSON', '$0.025/GB-mo', '$0.0112/h'])], h=290)
lay = layers('How a bill is built in layers: usage records from meters, rated by the price list, summed per service, minus credits and discounts, gives your invoice.', [
    ('Invoice', 'what you pay this month', 'acc'), ('Credits / discounts', 'free tier, savings plans', 'green'),
    ('Per service totals', 'EC2, S3, data transfer…', 'violet'), ('Rating', 'usage × price list (JSON)', 'blue'),
    ('Usage records', 'GB-hours, requests, VM-seconds', 'card'), ('Meters on every resource', 'measured service', 'card')], hl=3, caption='Measured service, from meter to invoice.')
DIS = figure('Dissection of one price: 0.025 US dollars per GB-month for S3 Standard storage in ap-south-1, first 50 TB tier.',
    t(16, 22, 'One price from the AWS price list (real)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('$0.025', 'blue', 1), ('GB-Mo', 'green', 2), ('0–51200 GB', 'amber', 3), ('ap-south-1', 'violet', 4)]) +
    legend(16, 84, [(1, 'Price', 'US dollars'), (2, 'Unit', 'one GB stored for a month'), (3, 'Tier', 'cheaper above 50 TB'), (4, 'Region', 'prices differ by region')], size=8, gap=15, w=90),
    h=156, caption='Volume tiers = economies of scale passed to you.')
extra = '\n\n  <h3>From meter to invoice</h3>\n' + lay + '\n\n  <h3>Dissect one price</h3>\n' + DIS
types_html = table(['Characteristic', 'Means', 'Real example'], [
    ['On-demand self-service', 'you create resources yourself, any time', 'launch a VM from the console in 2 minutes'],
    ['Broad network access', 'reach it over standard networks and devices', 'manage AWS from the mobile app'],
    ['Resource pooling', 'shared physical resources, multi-tenant', 'many customers’ VMs on one server'],
    ['Rapid elasticity', 'scale out/in quickly, looks unlimited', 'Diwali: 3 → 12 servers'],
    ['Measured service', 'usage metered and billed', '$0.0112 per VM-hour, per-second billing']], minw=600)
warn = 'Elasticity is not automatic: you must configure auto scaling (AWS course 3.4). And measured service works both ways: an idle VM still shows on the meter every hour.'
steps = [
    ('Step 1 · The price list is public', code('python', 'l13_measured.py', 'u = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/ap-south-1/index.json"\nd = json.load(urlopen(u))', sec('== 1)', '== 2)')), 'Anyone can download it: measured service is transparent.'),
    ('Step 2 · Storage price tiers', code('python', 'l13_measured.py', 'products where volumeType == "Standard" → OnDemand price dimensions', sec('== 2)', '== 3)')), 'The more you store, the cheaper per GB: economies of scale.'),
    ('Step 3 · Even requests are metered', code('python', 'l13_measured.py', 'usagetype == "APS3-Requests-Tier1"', sec('== 3)', '== 4)')), 'Half a paisa per 1,000 uploads — tiny, but counted.'),
    ('Step 4 · TiffinGo’s photo bill', code('python', 'l13_measured.py', '500 * storage_price + 200000 * request_price', sec('== 4)', '== 5)')), 'About $13.50/month, no hardware bought.'),
    ('Step 5 · Virtual machines by the hour', code('python', 'l13_measured.py', 'EC2 ap-south-1 price file (315 MB) → Linux, shared, on-demand', sec('== 5)')), 'Bigger machine, higher hourly price; a 2-hour lab costs cents.'),
]
see = [term([('380 S3 products', W), ('2026-11-09', W)], size=7.0), term([('$0.025 / GB-mo', G), ('$0.023 > 512 TB', G)], size=7.0), term([('$0.000005 / req', W)], size=7.0),
       term([('storage $12.50', W), ('total $13.50', G)], size=7.0), term([('t3.micro $0.0112/h', W), ('2 h lab $0.09', G)], size=7.0)]
B1 = [meters(i) for i in (-1, 0, 1, 0, 3)]
B1 = [b + cap(c, '', tn, y=136, h=24) for b, c, tn in zip(B1, ['Public', 'Tiers', 'Requests', 'Bill', 'Per hour'], ['blue', 'green', 'green', 'acc', 'violet'])]
two = anim_two('Measured service', 'Reading a real price list', 'Real outputs (AWS price list)', 'Meters', see, B1, ['Public.', 'Tiers.', 'Requests.', 'Bill.', 'VMs.'], ['Open.', 'Scale.', 'Tiny.', '$13.50.', 'Hourly.'])
pe = peel('Elasticity, layer by layer', 'What happens when Diwali orders arrive. (Simplified.)',
    [('Metric', ''), ('Alarm', ''), ('Policy', ''), ('Launch', ''), ('Register', ''), ('Shrink', '')],
    [['Metric', 'CPU 80%', 'on 3 servers', ''], ['Alarm', 'above target', 'for 3 min', ''], ['Policy', 'add 2 servers', 'up to 12', ''],
     ['Launch', 'new VMs', 'from template', 'minutes'], ['Register', 'load balancer', 'sends traffic', ''], ['Shrink', 'CPU 20%', 'remove extras', 'save']],
    ['Watch.', 'Alarm.', 'Decide.', 'Launch.', 'Serve.', 'Scale in.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Exam results day', 'Traffic ×20 for one day. (Typical.)', ('Elasticity', 'Scale out, then in'), [
    ('Normal: 2 servers', '', 'Before.', 'blue'), ('Results at 10 am', 'traffic ×20', 'Spike.', 'red'),
    ('Auto scaling → 30', 'minutes', 'Grow.', 'green'), ('Evening → 2', '', 'Shrink.', 'green'), ('Paid for 1 busy day', '', 'Measured.', 'amber')], ['Normal.', 'Spike.', 'Grow.', 'Shrink.', 'Pay.'], 'scenario-results') + \
       five('Real-time scenario 2', 'Go global in minutes', 'Expanding to Dubai. (Typical.)', ('Regions', 'Deploy where users are'), [
    ('Users in UAE', 'slow from Mumbai', 'Need.', 'blue'), ('Pick me-central-1', 'UAE region', 'Place.', 'green'),
    ('Same template', 'deploy again', 'Copy.', 'green'), ('DNS routes by location', '', 'Route.', 'acc'), ('Live in a day', 'no new office', 'Global.', 'amber')], ['Need.', 'Region.', 'Deploy.', 'Route.', 'Live.'], 'scenario-global') + \
       five('Real-time scenario 3 · advanced', 'Experiment cheaply', 'Try a big ML model. (Typical.)', ('Agility', 'Rent, test, delete'), [
    ('Need 8 GPUs', 'for 6 hours', 'Need.', 'blue'), ('Rent GPU VMs', 'on demand', 'Start.', 'green'),
    ('Train + test', '', 'Work.', 'green'), ('Delete', 'meter stops', 'Stop.', 'amber'), ('Cost: hours, not a ₹1 crore purchase', '', 'Agility.', 'violet')], ['Need.', 'Rent.', 'Train.', 'Delete.', 'Cheap.'], 'scenario-gpu')
clouds = vendor_tabs(
    '<p><b>AWS</b> lists six advantages (trade CapEx for variable expense, economies of scale, stop guessing capacity, speed and agility, stop running data centres, go global in minutes). Price list: AWS Price List bulk JSON and the Pricing Calculator.</p>',
    '<p><b>Azure</b> (AZ-900) groups benefits as high availability, scalability (vertical/horizontal), elasticity, reliability, predictability (performance + cost), security, governance and manageability. Prices: Azure Retail Prices API and Pricing Calculator.</p>',
    '<p><b>Google Cloud</b> stresses speed of innovation, data and AI, sustainability (carbon-free energy goal) and per-second billing with sustained-use discounts. Prices: Cloud Billing Catalog API and Pricing Calculator.</p>') + \
    cloud3([['Price calculator', 'AWS Pricing Calculator', 'Azure Pricing Calculator', 'Google Cloud Pricing Calculator'], ['Public price API', 'Price List API / bulk JSON', 'Retail Prices API', 'Cloud Billing Catalog API'], ['VM billing', 'per second (Linux, min 60 s)', 'per second', 'per second (min 1 min)'], ['Auto scaling', 'EC2 Auto Scaling', 'VM Scale Sets', 'Managed instance groups']])
prac = practical('Read a real price list and estimate a bill. No account needed.', [
    ('1 · Download the S3 Mumbai price list', code('bash', 'terminal', 'curl -s -o s3.json https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/ap-south-1/index.json\nls -lh s3.json'), 'About 0.5 MB.'),
    ('2 · Find the storage price with jq', code('bash', 'terminal', "jq -r '.products[] | select(.attributes.volumeType==\"Standard\" and .attributes.storageClass==\"General Purpose\") | .sku' s3.json"), 'Copy the SKU, then look it up under .terms.OnDemand.'),
    ('3 · Run the lesson script', code('bash', 'terminal', 'python3 l13_measured.py'), 'Matches Steps 1–4 (prices may change).'),
    ('4 · Cross-check in the AWS Pricing Calculator', '<p>Open <code>calculator.aws</code> → Add service → S3 → region Asia Pacific (Mumbai) → 500 GB Standard, 200,000 PUT requests.</p>', 'Should be close to $13.50/month.'),
    ('5 · Try Azure and Google calculators', '<p>Same 500 GB in Azure Blob (Central India, Hot) and Google Cloud Storage (asia-south1, Standard).</p>', 'Write the three numbers in a table: your first cloud comparison.')],
    cleanup='Nothing to clean: price files are public. Never paste real account IDs or keys into public calculators’ shared links.')
prac = prac.replace('<ol class="stepper">', caution('Prices in this lesson are list prices in US dollars on 9–10 Nov 2026, before tax and without free tier. Always check the calculator for today’s numbers.') + '<ol class="stepper">', 1)
mist = mistakes([
    ['Mixing up elasticity and scalability.', 'Both talk about size.', 'Scalability = can grow to handle more; elasticity = grows and shrinks automatically with demand.'],
    ['Forgetting that idle resources are still metered.', 'Measured service counts time, not work.', 'Stop or delete after use; schedule dev servers off at night.'],
    ['Ignoring data transfer cost.', 'Uploading is usually free, downloading/out to internet is not.', 'Check “Data transfer out” in the calculator.'],
    ['Comparing prices across regions blindly.', 'Prices differ by region.', 'Compare the same region; pick Indian regions for Indian users.'],
    ['Quoting the six advantages in your own words in the exam.', 'Options use AWS’s exact wording.', 'Memorise the six phrases.']])
cert = certbox([
    ['AWS CLF-C02', 'Domain 1 · Cloud Concepts (24%)', 'The six advantages; economies of scale; elasticity vs scalability; agility.'],
    ['AWS CLF-C02', 'Domain 4 · Billing & Pricing (12%)', 'Pay-as-you-go, Pricing Calculator, price varies by region.'],
    ['Azure AZ-900', 'Describe the benefits of using cloud services', 'High availability, scalability, elasticity, reliability, predictability, security, governance, manageability.'],
    ['Google Cloud Digital Leader', 'Digital transformation', 'Total cost of ownership, agility, innovation.'],
    ['C-DAC PGCP-BDA', 'Cloud Session 2', 'Characteristics and benefits.']],
    [('A company no longer buys servers for its peak season and instead adds capacity automatically. Which advantage? (a) go global in minutes (b) stop guessing capacity (c) economies of scale', '<b>(b) Stop guessing capacity</b> (elasticity).'),
     ('Lower prices because AWS buys hardware for millions of customers is…', '<b>Benefit from massive economies of scale.</b>'),
     ('Azure: the ability to automatically add and remove resources based on demand is…', '<b>Elasticity</b> (scalability is the ability to grow).')])
proj = miniproject('Mini project: three-cloud storage bill calculator',
    'A command-line Python tool that asks for GB and requests and prints the monthly bill in AWS Mumbai using the live price list.',
    ['Start from <code>l13_measured.py</code>; read GB and requests with <code>input()</code>.', 'Cache the JSON file locally so you download it once a day.', 'Add Azure and Google prices by hand (from their calculators) as a dictionary.', 'Print a table of the three clouds and the cheapest.', 'Bonus: wrap it as a shell script <code>bill 500 200000</code> (Shell scripting course).'],
    'A table like “AWS $13.50 · Azure $x · GCP $y”.', 'Python + JSON, cloud pricing, shell scripting.')

# ===== v3 =====
def cap_vs_demand():
    import math
    o = t(320, 16, 'Capacity vs demand: own servers vs cloud', 11, 'ink', bold=True)
    X0, Y0, W, H = 60, 40, 540, 200
    o += f'<line x1="{X0}" y1="{Y0 + H}" x2="{X0 + W}" y2="{Y0 + H}" style="stroke:var(--line)"/><line x1="{X0}" y1="{Y0}" x2="{X0}" y2="{Y0 + H}" style="stroke:var(--line)"/>'
    o += t(X0 - 8, Y0 + 8, 'servers', 7.6, 'ink2', anchor='end') + t(X0 + W, Y0 + H + 14, 'months →', 7.6, 'ink2', anchor='end')
    dem = [30, 34, 40, 38, 45, 52, 60, 58, 70, 95, 72, 65]
    pts = [(X0 + i * W / 11, Y0 + H - d * 1.6) for i, d in enumerate(dem)]
    own = Y0 + H - 80 * 1.6
    # waste area (own above demand) and shortage (demand above own)
    poly = ' '.join(f'{x:.0f},{y:.0f}' for x, y in pts)
    o += f'<polygon points="{X0},{own} {X0 + W},{own} ' + ' '.join(f'{x:.0f},{max(y, own):.0f}' for x, y in reversed(pts)) + '" style="fill:#D64545;opacity:.12"/>'
    o += f'<line x1="{X0}" y1="{own}" x2="{X0 + W}" y2="{own}" style="stroke:#D64545;stroke-width:3;stroke-dasharray:8 4"/>' + t(X0 + 6, own - 6, 'Own servers bought for a forecast (fixed)', 8.4, 'red', anchor='start', bold=True)
    cl = ' '.join(f'{x:.0f},{y - 6:.0f}' for x, y in pts)
    o += f'<polyline points="{cl}" style="fill:none;stroke:var(--green);stroke-width:3"/>'
    o += f'<polyline points="{poly}" style="fill:none;stroke:var(--blue);stroke-width:2.4"/>'
    px, py = pts[9]
    o += f'<circle cx="{px}" cy="{py}" r="5" style="fill:#D64545"/>' + t(px, py - 12, 'Diwali: demand > own → crash', 8.2, 'red', bold=True)
    o += t(X0 + 140, own + 40, 'red area = paid for, never used (waste)', 8.2, 'red')
    o += box(X0 + 330, Y0 + H - 46, 200, 38, 'card', rx=6) + f'<line x1="{X0 + 340}" y1="{Y0 + H - 34}" x2="{X0 + 364}" y2="{Y0 + H - 34}" style="stroke:var(--blue);stroke-width:2.4"/>' + t(X0 + 370, Y0 + H - 31, 'actual demand', 8, 'ink', anchor='start')
    o += f'<line x1="{X0 + 340}" y1="{Y0 + H - 18}" x2="{X0 + 364}" y2="{Y0 + H - 18}" style="stroke:var(--green);stroke-width:3"/>' + t(X0 + 370, Y0 + H - 15, 'cloud capacity (follows demand)', 8, 'ink', anchor='start')
    return o
CVD = bigfig('Line chart: actual demand rises over 12 months with a Diwali peak. A fixed red line shows own servers bought for a forecast: the area above demand is waste, and at Diwali demand crosses it and the site crashes. A green line shows cloud capacity following demand closely.', cap_vs_demand(), h=268,
             caption='The single most important cloud picture: no waste, no shortage.')
def six():
    items = [('meter', 'Trade fixed expense for variable expense', 'pay as you go, not up front'), ('chip', 'Benefit from massive economies of scale', 'lower price per unit'),
             ('chart', 'Stop guessing capacity', 'scale with real demand'), ('gear', 'Increase speed and agility', 'resources in minutes'),
             ('server', 'Stop spending on data centres', 'focus on your product'), ('globe', 'Go global in minutes', 'regions worldwide')]
    o = t(320, 16, 'The six advantages of cloud computing (AWS wording)', 11, 'ink', bold=True)
    for i, (icn, a, b) in enumerate(items):
        x = 14 + (i % 3) * 208; y = 32 + (i // 3) * 88
        o += box(x, y, 198, 78, ['blue', 'green', 'violet', 'acc', 'amber', 'blue'][i], rx=10) + ic(icn, x + 10, y + 10, 1.2, 'acc')
        words = a.split(' ')
        l1 = ' '.join(words[:3]); l2 = ' '.join(words[3:])
        o += t(x + 46, y + 22, l1, 8.6, 'ink', anchor='start', bold=True) + t(x + 46, y + 35, l2, 8.6, 'ink', anchor='start', bold=True) + t(x + 12, y + 62, b, 8, 'ink2', anchor='start')
    return o
SIX = bigfig('Six tiles: trade fixed expense for variable expense; benefit from massive economies of scale; stop guessing capacity; increase speed and agility; stop spending money running data centres; go global in minutes.', six(), h=216)
picture = ('  <p>Lesson 1.1 showed <b>what</b> the cloud is (its 5 characteristics). This lesson shows <b>why companies pay for it</b>. Start with the picture every cloud architect knows: a company that buys servers must guess its future demand.</p>\n'
           + CVD + '\n  <p>From that picture come the six advantages that AWS lists, and that the CLF-C02 exam quotes word for word:</p>\n' + SIX)

# animation 1: from meter to bill (real prices)
BN = {'vm': (8, 20, 70, 50, 'server', 'VM t3.micro', 'runs 720 h'), 's3': (8, 88, 70, 50, 'disk', 'S3 storage', '500 GB'),
      'meter': (100, 54, 64, 50, 'meter', 'Meter', 'usage records'), 'price': (186, 8, 70, 50, 'dns', 'Price list', 'public JSON'),
      'total': (186, 92, 70, 50, 'chart', 'Per service', 'totals'), 'bill': (278, 54, 74, 50, 'app', 'Invoice', 'month end')}
BS = [dict(on=['vm', 's3'], hot='vm', head='Step 1 · Resources run', text='TiffinGo runs one t3.micro VM all month and stores 500 GB of photos.', text2='Nothing is bought; both were created from the console.', svc='AWS EC2 + S3 · Azure VM + Blob · Google Compute Engine + Cloud Storage'),
      dict(on=['vm', 's3', 'meter'], hot='meter', move=(78, 45, 100, 72, 'seconds'), head='Step 2 · The meter records usage', text='Every VM-second, every GB-hour stored and every request is recorded.', text2='This is NIST’s “measured service”.', svc='AWS Cost and Usage Report · Azure usage details · GCP billing export'),
      dict(on=['vm', 's3', 'meter', 'price'], hot='price', move=(164, 70, 188, 36, 'rate'), head='Step 3 · Look up the real price', text='Mumbai prices from the public price list: t3.micro $0.0112 per hour,', text2='S3 Standard $0.025 per GB-month, $0.000005 per request.', svc='Same file we read in the Real proof section'),
      dict(on=['vm', 's3', 'meter', 'price', 'total'], hot='total', move=(220, 58, 220, 92, '×'), head='Step 4 · Usage × price, per service', text='EC2: 720 h × $0.0112 = $8.06   ·   S3: 500 GB × $0.025 = $12.50', text2='Requests: 200,000 × $0.000005 = $1.00', svc='Each service appears as its own line on the bill'),
      dict(on=list(BN), hot='bill', move=(256, 117, 280, 80, '$21.56'), head='Step 5 · The invoice', text='Total about $21.56 for the month (before tax and free tier).', text2='Delete the VM and photos → next month’s bill for them is $0.', svc='AWS Billing · Azure Cost Management + Billing · Google Cloud Billing')]
BILL = flow_anim('From a running VM to a monthly bill', 'How “pay only for what you use” really works, with real Mumbai prices.', 'Measured service', 'Animation: resources run, meter records usage, price list lookup, usage times price per service, invoice.', BN, BS, hid='bill')

# animation 2: scalability vs elasticity
def sc_frame(k):
    o = ''
    if k == 0:
        o += t(180, 14, 'Starting point: 1 small VM (2 vCPU)', 9, 'ink', bold=True) + node_box(150, 40, 60, 56, 'server', 't3.medium', '2 vCPU, 4 GB', hot=True)
    elif k == 1:
        o += t(180, 14, 'Vertical scaling (scale UP)', 9, 'ink', bold=True) + node_box(60, 50, 60, 56, 'server', 't3.medium', '2 vCPU', on=False) + arrow(126, 78, 170, 78, 'acc', 2.4)
        o += box(176, 24, 120, 104, 'amber', rx=8, sw=2.6) + ic('server', 222, 38, 1.2, 'acc') + t(236, 86, 'm7i.2xlarge', 9, 'ink', bold=True) + t(236, 100, '8 vCPU, 32 GB', 8, 'ink2') + t(236, 116, 'restart needed', 7.4, 'red')
    elif k == 2:
        o += t(180, 14, 'Horizontal scaling (scale OUT)', 9, 'ink', bold=True)
        for i in range(4):
            o += node_box(30 + i * 78, 44, 62, 56, 'server', f'VM {i + 1}', '2 vCPU', hot=i >= 1)
        o += t(180, 124, 'add more machines behind a load balancer', 8, 'ink2')
    elif k == 3:
        o += t(180, 14, 'Elasticity: automatic, both directions', 9, 'ink', bold=True)
        for i in range(4):
            o += node_box(30 + i * 78, 44, 62, 56, 'server', f'VM {i + 1}', 'removed' if i >= 2 else 'kept', on=i < 2)
        o += t(180, 124, 'night: auto scaling removes VM 3 and VM 4', 8, 'green', bold=True)
    return o
SC = [('Need: more power for the app', 'Orders double. How do we get more capacity?', 'Two ways to scale, and one way to scale automatically'),
      ('Scale up (vertical)', 'Replace with a bigger machine: more CPU and RAM in one VM.', 'Simple, but has a ceiling and usually a restart'),
      ('Scale out (horizontal)', 'Add more machines of the same size behind a load balancer.', 'Almost no ceiling; needs an app that can run on many VMs'),
      ('Elasticity', 'Scale out and back in automatically as demand changes.', 'Scalability = can grow · Elasticity = grows and shrinks by itself')]
fr = [sc_frame(k) + box(6, 158, 348, 62, 'blue', rx=8) + t(14, 174, h, 9, 'ink', anchor='start', bold=True) + t(14, 190, a, 7.6, 'ink', anchor='start') + t(14, 206, b, 7.2, 'ink2', anchor='start') for k, (h, a, b) in enumerate(SC)]
SCALE = anim_one('How it works', 'Scalability vs elasticity', 'The difference exams love to ask. Watch the same app scale three ways.', 'Scaling', 'Animation: one VM, scale up to a bigger VM, scale out to more VMs, elasticity removes VMs at night.', fr, ['Need.', 'Scale up.', 'Scale out.', 'Elastic.'], delay=6000, hid='scale')

parts = cards([
    ('1. Trade fixed expense for variable expense', 'No ₹10 lakh purchase order: TiffinGo pays $21.56 this month and only for what ran.', 'CapEx → OpEx'),
    ('2. Benefit from massive economies of scale', 'AWS buys hardware for millions of customers; S3 gets cheaper per GB above 50 TB ($0.025 → $0.024 → $0.023).', 'lower unit price'),
    ('3. Stop guessing capacity', 'No forecast needed: the green line in the picture follows demand.', 'elasticity'),
    ('4. Increase speed and agility', 'A new test server takes 2 minutes instead of a 6-week purchase.', 'experiment cheaply'),
    ('5. Stop spending money running data centres', 'No AC, power backup, racks or hardware repairs for TiffinGo.', 'focus on the app'),
    ('6. Go global in minutes', 'Launch in the UAE region (me-central-1) with the same template.', 'regions worldwide')]) + \
    '\n  <h3>Other advantages you will see in textbooks</h3>\n' + cards([
    ('Backup and disaster recovery', 'Copies of data in another zone or region in minutes, instead of tapes in a cupboard.', 'reliability'),
    ('Collaboration and mobility', 'Teams open the same files and apps from anywhere, on any device.', 'broad network access'),
    ('Security tools built in', 'Encryption, identity, firewalls and audit logs are ready-made services.', 'you still configure them'),
    ('Sustainability', 'Large shared data centres use energy more efficiently than small server rooms.', 'shared efficiency'),
    ('Innovation', 'Rent AI, analytics and IoT services by the hour instead of building them.', 'try new tech cheaply'),
    ('Automatic updates', 'The provider patches hardware and managed services.', 'less maintenance')]) + \
    '\n  <h3>Azure (AZ-900) lists the benefits differently</h3>\n' + table(['AZ-900 benefit', 'Meaning', 'Example'], [
    ['High availability', 'service keeps running despite failures', 'two zones behind a load balancer'],
    ['Scalability', 'can handle more load (up or out)', 'bigger VM or more VMs'],
    ['Elasticity', 'scales automatically with demand', 'Diwali auto scaling'],
    ['Reliability', 'recovers from failures, spreads across regions', 'backups, second region'],
    ['Predictability', 'performance and cost can be forecast', 'budgets, pricing calculator'],
    ['Security', 'tools and physical security from the provider', 'encryption, identity'],
    ['Governance', 'policies and compliance rules applied everywhere', 'Azure Policy, tags'],
    ['Manageability', 'manage the cloud and in the cloud (portal, CLI, templates)', 'automation, monitoring']], minw=600)

SUMMARY = big_mindmap('Mind map of lesson 1.3: capacity vs demand, six advantages, scaling, measured service, AZ-900 benefits, cautions.', 'Why cloud pays', [
    ('Big picture', 'red', 'chart', ['own: fixed capacity', 'waste + shortage', 'cloud follows demand']),
    ('6 advantages', 'green', 'meter', ['CapEx → OpEx', 'economies of scale', 'stop guessing capacity', 'speed, no DCs, global']),
    ('Scaling', 'violet', 'server', ['up = bigger VM', 'out = more VMs', 'elastic = automatic']),
    ('Bill', 'acc', 'app', ['meter → price list', 'usage × price', '$21.56 example']),
    ('AZ-900 words', 'blue', 'cloud', ['availability, reliability', 'predictability', 'governance, manageability']),
    ('Watch out', 'amber', 'shield', ['idle still billed', 'data transfer out', 'compare same region'])], h=380, caption='Lesson 1.3 on one page.')
cert = cert + '\n  <h3>Lesson 1.3 on one page</h3>\n' + SUMMARY

assemble_v2(HERE, story_h2='Finance wants proof of “pay only for what you use”', hook_html=hk,
    narration='TiffinGo wants to move its 500 GB of menu photos and its app server to the cloud. The finance team asks two questions: why is this better than buying, and what exactly will we pay?',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Advantages of cloud computing',
    formal='The <b>advantages of cloud computing</b> follow from its essential characteristics: organisations <b>trade capital expense for variable expense</b>, <b>benefit from economies of scale</b>, <b>stop guessing capacity</b> through elasticity, <b>increase speed and agility</b>, <b>stop spending on running data centres</b> and <b>go global in minutes</b>. Microsoft additionally lists high availability, scalability, reliability, predictability, security, governance and manageability.',
    simple='You stop buying computers for a guess, pay only for what you use, get resources in minutes anywhere in the world, and let the provider run the buildings.',
    interview=['“The main advantages are: we trade capital expense for variable expense, benefit from the provider’s economies of scale, stop guessing capacity because of elasticity, gain speed and agility, stop spending on data centres, and can go global in minutes.”', '“Scalability means the system can grow; elasticity means it grows and shrinks automatically with demand.”', '“For example, in AWS Mumbai a t3.micro costs about 1.1 cents an hour and S3 storage 2.5 cents per GB-month, so a small app costs a few dollars a month and nothing once deleted.”'],
    terms_rows=[('CapEx', 'Up-front capital purchase.'), ('OpEx', 'Pay-as-you-go running cost.'), ('Economies of scale', 'Cheaper per unit at huge size.'), ('Agility', 'Speed to try and deliver.'), ('Scale up / vertical', 'Bigger machine.'), ('Scale out / horizontal', 'More machines.'), ('Elasticity', 'Automatic scale out and in.'), ('Price list', 'Public prices as data.')],
    exam='AZ-900 calls pay-as-you-go the <b>consumption-based model</b> (no up-front cost, pay for what you use). “Stop guessing capacity” = elasticity; “trade capital expense for variable expense” = pay-as-you-go; “massive economies of scale” = lower unit prices. Scalability vs elasticity is a favourite AZ-900 question.',
    picture_h2='Capacity vs demand, and the six advantages', picture_html=picture,
    how_h2='How the bill is made, and how scaling works', how_intro='Two animations: first, how a running VM becomes a line on your bill (real prices); second, the difference between scaling up, scaling out and elasticity.', how_anim=BILL + SCALE,
    parts_h2='The six advantages, with TiffinGo examples', parts_html=parts, lv='',
    myth_rows=[('Cloud prices are secret.', 'AWS publishes them as JSON.', 'Real proof step 1.'), ('Scalability and elasticity are the same.', 'Elasticity is automatic and works in both directions.', 'Animation 2.'), ('Cloud is always cheaper.', 'Idle resources and data transfer can cost more.', 'Mistakes table.')],
    clouds_html=clouds, proof_h2='Reading AWS’s real price list', proof_intro='All outputs are real: AWS Price List bulk files for ap-south-1 (Mumbai), published 9 Nov 2026, downloaded 10 Nov 2026.', proof_steps=steps,
    practical_html=prac, mistakes_html=mist, cert_html='', project_html='', can_now=['Draw the capacity-vs-demand picture and point out waste and shortage.', 'List the six AWS advantages in exam wording and give an example of each.', 'Explain scale up, scale out and elasticity.', 'Calculate a simple monthly bill from a price list.', 'Name the AZ-900 benefits, including the consumption-based model.'],
    next_html='<a href="../04-challenges-and-limitations-of-cloud/">1.4 Challenges and limitations: what can go wrong, and how engineers prevent it</a>.',
    pre='<b>Before you start:</b> <a href="../01-what-is-cloud-computing/">1.1</a> (the five characteristics).')
