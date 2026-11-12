import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
C = 'l11_cloud_is_real.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('Where does your photo go when you “save it to the cloud”? Is the cloud just someone else’s computer?',
    'Yes, and no. The cloud is real buildings full of servers, but you <b>rent</b> them by the minute over the internet, start them yourself in seconds and pay only for what you use. AWS even publishes every IP range it owns: on 9 Nov 2026 the file listed <b>10,744 IPv4 ranges across 42 regions</b>, including Mumbai and Hyderabad. Google Cloud lists <b>48 regions</b>, with Mumbai and Delhi in India.',
    ['The NIST definition: 5 characteristics, 3 service models, 4 deployment models.', 'The architecture of a cloud and what happens in 8 steps when you tap “Order”.', 'Seeing real cloud infrastructure from your own laptop.'])
cmap = concept_map('Concept map. Beginner: renting computing over the internet. Intermediate: five NIST characteristics, service and deployment models. Advanced: regions, pay-as-you-go, shared responsibility.',
    [[('it', 'Own servers', 'buy, run, fix', None), ('net', 'Internet', 'broad access', None)],
     [('od', 'On-demand', 'self-service', None), ('pool', 'Pooling', 'shared hardware', None), ('el', 'Elasticity', 'grow + shrink', None), ('ms', 'Measured', 'pay per use', None)],
     [('sm', 'Service models', 'IaaS PaaS SaaS', B + '02-service-models/01-iaas-infrastructure-as-a-service/'), ('dm', 'Deployment models', 'public, private…', B + '03-deployment-models/01-public-private-hybrid-and-community-cloud/'), ('rg', 'Regions', 'Module 5', B + '05-core-cloud-concepts/01-regions-availability-zones-and-edge-locations/'), ('sr', 'Shared responsibility', 'Module 9', B + '09-cloud-security/01-shared-responsibility-model/')]],
    [('it', 'od'), ('net', 'od'), ('od', 'pool'), ('pool', 'el'), ('el', 'ms'), ('od', 'sm'), ('pool', 'dm'), ('el', 'rg'), ('ms', 'sr')],
    {'od', 'pool', 'el', 'ms'},
    '<b>Next:</b> <a href="../02-history-and-evolution-of-cloud-computing/">1.2 History and evolution</a>. <b>Related:</b> <a href="../../../linux/">Linux course</a> (every cloud server runs it).')
whw = why_how_where(
    'Buying servers takes weeks, costs lakhs up front and they sit idle most of the year. The cloud turns that into a bill you can switch on and off, like electricity.',
    'Providers build huge data centres, split machines with virtualization (Module 4), and expose them through a website (console), command line and APIs. You ask, they allocate in seconds, a meter counts usage.',
    'Websites and apps, data storage and backup, big data and AI, email and office tools (SaaS), testing environments, disaster recovery.',
    'Internet down = cloud unreachable; costs grow if you forget resources; data laws may require data in India; you trust the provider’s security for the layers they manage.')

def spike(hl=-1):
    """Traffic vs servers: own data centre (fixed 6) vs cloud (follows demand)."""
    load = [2, 2, 3, 3, 4, 9, 11, 8, 3, 2]
    cloud = [2, 2, 3, 3, 4, 9, 11, 8, 3, 2]
    o = ''
    for i, (l, c) in enumerate(zip(load, cloud)):
        x = 28 + i * 30
        o += box(x, 118 - l * 8, 12, l * 8, 'blue', rx=2)
        o += box(x + 13, 118 - c * 8, 10, c * 8, 'green' if hl != 0 else 'card', rx=2)
    o += f'<line x1="22" y1="{118 - 6 * 8}" x2="330" y2="{118 - 6 * 8}" stroke="#D64545" stroke-width="2" stroke-dasharray="5 3"/>'
    o += t(332, 118 - 6 * 8 - 4, 'own: 6 servers', 7.2, 'red', anchor='end', bold=True)
    o += t(178, 13, 'Diwali week: orders (blue) vs cloud servers (green)', 7.6, 'ink', bold=True)
    o += t(206, 128, 'days →', 7) + (box(30, 22, 66, 18, 'amber', rx=5) + t(63, 34, 'site down!', 7.4, 'red', bold=True) if hl == 1 else '')
    return o
scene_svg = scene('A bar chart of TiffinGo orders during Diwali week. Fixed own servers (6) are too few on the peak days and wasted on quiet days; cloud servers rise and fall with the orders.', spike(1),
                  'Own servers: too few on peak days, idle on quiet days. <tspan font-weight="700" class="s-acc">Cloud: follows demand</tspan>.')
dialogue = '''K> Sir, last Diwali TiffinGo’s site crashed for 3 hours. Boss says “buy 10 more servers”.
A> And for the other 360 days those servers sit idle, eating electricity. What if we could <b>rent</b> 10 servers for just Diwali week?
R> Like booking an Ola instead of buying a car?
A> Exactly. That is cloud computing. Today: what it really is, and proof that it is real hardware, not magic.'''

lv = '''
LEVELS> Cloud computing at three levels
L1> Electricity for computers
      <ul>
        <li>You don’t build a power plant at home: you plug in and pay the bill. The cloud is the same for computers, storage and software: plug in over the internet, use, pay for what you used.</li>
        <li>Gmail, Google Drive, Netflix, IRCTC and UPI apps all run on cloud-style data centres.</li>
      </ul>
L2> The NIST definition
      <ul>
        <li><b>5 characteristics:</b> on-demand self-service · broad network access · resource pooling · rapid elasticity · measured service.</li>
        <li><b>3 service models:</b> IaaS (rent machines), PaaS (rent a platform), SaaS (use finished software). Module 2.</li>
        <li><b>4 deployment models:</b> public, private, hybrid, community. Module 3.</li>
      </ul>
L3> What it means for an architect
      <ul>
        <li>Capital expense (CapEx, buy up front) becomes operating expense (OpEx, pay monthly); capacity planning becomes auto scaling.</li>
        <li>Everything is an API: the console, the CLI and Terraform all call the same APIs (Module 8).</li>
        <li>Location still matters: regions and availability zones decide latency, cost, data law and fault tolerance (Module 5).</li>
      </ul>
/LEVELS
'''
mm = mindmap('Mind map of cloud computing: definition, five characteristics, service models, deployment models, providers and benefits.', 'Cloud computing', [
    ('5 traits (NIST)', 'blue', ['on-demand', 'network access', 'pooling', 'elasticity', 'measured']),
    ('Service models', 'green', ['IaaS', 'PaaS', 'SaaS', '+ FaaS']),
    ('Deployment', 'violet', ['public', 'private', 'hybrid', 'community']),
    ('Providers', 'acc', ['AWS', 'Azure', 'Google Cloud']),
    ('Parts', 'card', ['front end', 'back end', 'network', 'data centres']),
    ('Benefits', 'amber', ['pay as you go', 'speed', 'global', 'no idle servers'])], h=300)
lay = layers('Layers of a cloud: your device and browser at the top, the internet, the provider front door (console, CLI, API), the service layer, virtualization, and physical data centres at the bottom.', [
    ('Your phone / laptop', 'browser, app, CLI', 'blue'), ('Internet', 'broad network access', 'card'),
    ('Front door: console · CLI · API', 'on-demand self-service', 'green'), ('Services', 'VMs, storage, databases, AI…', 'violet'),
    ('Virtualization', 'one machine → many VMs (pooling)', 'acc'), ('Data centres in regions', 'servers, disks, power, cooling', 'card')], hl=None, caption='Every cloud request goes down these layers and back.')
DIS = figure('Dissection of one line of AWS’s public IP range file: prefix 16.4.0.0/16, region ap-south-1 (Mumbai), service EC2.',
    t(16, 22, 'One real line from ip-ranges.json', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('16.4.0.0/16', 'blue', 1), ('ap-south-1', 'green', 2), ('EC2', 'amber', 3), ('2026-11-09', 'violet', 4)]) +
    legend(16, 84, [(1, 'IP range', '65,536 addresses AWS owns'), (2, 'Region', 'Mumbai data centres'), (3, 'Service', 'virtual machines'),
                    (4, 'File date', 'updated by AWS')], size=8, gap=15, w=90),
    h=156, caption='Cloud “magic” has addresses, buildings and a city.')
extra = '''

  <h3>The layers behind every cloud request</h3>
''' + lay + '''

  <h3>Dissect a real cloud address</h3>
''' + DIS
types_html = table(['Way to describe it', 'Says', 'Source'], [
    ['NIST SP 800-145', 'a model for on-demand network access to a shared pool of configurable resources, provisioned with minimal effort', 'US standards body (exam favourite)'],
    ['AWS', 'on-demand delivery of IT resources over the internet with pay-as-you-go pricing', 'aws.amazon.com/what-is-cloud-computing'],
    ['Google Cloud', 'on-demand access to computing resources over the internet, with pay-per-use', 'cloud.google.com/learn'],
    ['Simple', 'rent computers and software by the minute, through the internet', 'this course']], minw=600)
warn = 'Cloud is not “free storage on the internet”. Every running machine, disk, IP address and data transfer has a meter. In the hands-on lessons we always clean up at the end and set a budget alert first (Lesson 1.3 of the AWS course).'
steps = [
    ('Step 1 · AWS publishes its whole network',
     code('python', 'l11_cloud_is_real.py', 'a = json.load(urlopen("https://ip-ranges.amazonaws.com/ip-ranges.json"))\nlen(a["prefixes"]), len(a["ipv6_prefixes"]), regions', sec('== 1)', '  ap-south-1 IPv4')),
     'Tens of thousands of address blocks and 42 region codes: physical places, not a fog.'),
    ('Step 2 · What runs in Mumbai',
     code('python', 'l11_cloud_is_real.py', 'Counter(x["service"] for x in prefixes if x["region"] == "ap-south-1")', sec('  ap-south-1 IPv4', '== 2)')),
     'Virtual machines (EC2), storage (S3), DNS (Route 53), APIs: services you will use in the AWS course.'),
    ('Step 3 · Google Cloud does the same',
     code('python', 'l11_cloud_is_real.py', 'g = json.load(urlopen("https://www.gstatic.com/ipranges/cloud.json"))', sec('== 2)', '== 3)')),
     'Two Indian regions each: AWS Mumbai + Hyderabad, Google Mumbai + Delhi.'),
    ('Step 4 · One address each',
     code('python', 'l11_cloud_is_real.py', 'first EC2 range in ap-south-1; first range in asia-south1', sec('== 3)')),
     'A request from your phone to a Mumbai VM goes to an address like these.'),
]
see = [term([('10744 IPv4 prefixes', G), ('42 regions', G)], size=7.0), term([('AMAZON 167 EC2 56', W), ('S3 14', W)], size=7.0),
       term([('GCP 1153 prefixes', G), ('48 scopes', G)], size=7.0), term([('16.4.0.0/16 EC2', W), ('8.231.64.0/18', W)], size=7.0), term([('pay per use', G), ('no idle servers', G)], size=7.0)]
B1 = [spike(0), spike(1), spike(-1), spike(-1), spike(-1)]
B1 = [b + cap(c, '', tn, y=140, h=24) for b, c, tn in zip(B1, ['Fixed capacity', 'Peak: crash', 'Cloud follows', 'Quiet: shrink', 'Pay for green'], ['red', 'red', 'green', 'blue', 'green'])]
two = anim_two('Cloud computing', 'Real infrastructure, elastic use', 'Real outputs (public cloud files)', 'Diwali week at TiffinGo', see, B1, ['AWS.', 'Mumbai.', 'Google.', 'Addresses.', 'Bill.'], ['Fixed.', 'Crash.', 'Elastic.', 'Shrink.', 'Pay.'])
pe = peel('A cloud request, layer by layer', 'Riya clicks “Order” in the TiffinGo app. (Simplified.)',
    [('Phone', ''), ('Internet', ''), ('Front door', ''), ('Service', ''), ('VM', ''), ('Data centre', '')],
    [['Phone', 'HTTPS request', 'to api.tiffingo.in', ''], ['Internet', 'DNS → IP', '16.4.x.x (Mumbai)', ''], ['Front door', 'load balancer', 'picks a server', ''],
     ['Service', 'app on a VM', 'reads database', ''], ['VM', 'one slice of', 'a big server', 'pooling'], ['Data centre', 'ap-south-1', 'power, cooling, disks', '']],
    ['Tap.', 'Route.', 'Balance.', 'Process.', 'Share.', 'Physical.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Festival spike', 'Diwali orders ×4. (Typical.)', ('Elasticity', 'Add servers for a week'), [
    ('Normal: 3 servers', '₹ low bill', 'Before.', 'blue'), ('Orders ×4', 'Diwali', 'Spike.', 'red'),
    ('Auto scaling adds 9', 'in minutes', 'Grow.', 'green'), ('After festival', 'back to 3', 'Shrink.', 'green'),
    ('Bill: only that week', 'measured service', 'Pay.', 'amber')], ['Normal.', 'Spike.', 'Grow.', 'Shrink.', 'Pay.'], 'scenario-spike') + \
       five('Real-time scenario 2', 'Startup in a day', 'New app idea. (Typical.)', ('On-demand', 'No purchase order'), [
    ('Idea on Monday', '', 'Start.', 'blue'), ('Create VM + database', 'console, 10 min', 'Self-service.', 'green'),
    ('Show investors Tuesday', 'public URL', 'Demo.', 'green'), ('Idea fails', 'delete all', 'Stop.', 'amber'),
    ('Loss: a few hundred ₹', 'not lakhs', 'Cheap failure.', 'violet')], ['Idea.', 'Create.', 'Demo.', 'Delete.', 'Small loss.'], 'scenario-startup') + \
       five('Real-time scenario 3 · advanced', 'Data must stay in India', 'Regulated data. (Typical.)', ('Region choice', 'ap-south-1 / asia-south1'), [
    ('Bank data', 'RBI rules', 'Rule.', 'red'), ('Pick Indian region', 'Mumbai', 'Place.', 'green'),
    ('Backup in Hyderabad', 'second region', 'Protect.', 'green'), ('Encrypt', 'keys you control', 'Secure.', 'amber'),
    ('Audit logs', 'who did what', 'Prove.', 'blue')], ['Rule.', 'Mumbai.', 'Hyderabad.', 'Encrypt.', 'Audit.'], 'scenario-india')

clouds = vendor_tabs(
    '<p><b>AWS</b> (Amazon Web Services, 2006) is the largest public cloud. India regions: <code>ap-south-1</code> Mumbai and <code>ap-south-2</code> Hyderabad. You enter through the AWS Management Console, the AWS CLI or SDKs.</p><p>Exam: <b>AWS Certified Cloud Practitioner (CLF-C02)</b>.</p>',
    '<p><b>Microsoft Azure</b> (2010) is strong with companies already on Windows, Office 365 and Active Directory. India regions include Central India (Pune), South India (Chennai) and West India (Mumbai). Entry: Azure portal, Azure CLI, PowerShell.</p><p>Exam: <b>AZ-900 Azure Fundamentals</b>.</p>',
    '<p><b>Google Cloud</b> (2008, App Engine) is known for data, analytics and AI (BigQuery, Vertex AI). India regions: <code>asia-south1</code> Mumbai and <code>asia-south2</code> Delhi. Entry: Google Cloud console, <code>gcloud</code> CLI.</p><p>Exam: <b>Cloud Digital Leader</b>.</p>') + \
    cloud3([['Web console', 'AWS Management Console', 'Azure portal', 'Google Cloud console'], ['Command line', 'aws CLI, CloudShell', 'az CLI, Cloud Shell', 'gcloud CLI, Cloud Shell'],
            ['Virtual machine', 'EC2', 'Virtual Machines', 'Compute Engine'], ['Object storage', 'S3', 'Blob Storage', 'Cloud Storage'],
            ['India regions', 'Mumbai, Hyderabad', 'Pune, Chennai, Mumbai', 'Mumbai, Delhi'], ['Free start', 'Free plan + credits', 'Free account + credit', 'Free trial + credit']])
prac = practical('No account and no card needed today. You will look at real cloud infrastructure from your own computer (Linux, macOS or Windows with WSL). On plain Windows PowerShell use <code>Invoke-RestMethod https://ip-ranges.amazonaws.com/ip-ranges.json</code> instead of curl + jq.', [
    ('1 · Download AWS’s address list', code('bash', 'terminal', 'curl -s https://ip-ranges.amazonaws.com/ip-ranges.json -o aws.json\nls -lh aws.json'), 'A few MB of JSON, updated by AWS several times a week.'),
    ('2 · Count Mumbai ranges with jq', code('bash', 'terminal', 'sudo apt install -y jq          # once\njq \'[.prefixes[] | select(.region=="ap-south-1")] | length\' aws.json\njq -r \'.prefixes[].region\' aws.json | sort -u | wc -l'), 'Compare your numbers with Step 1–2 above; they change over time.'),
    ('3 · Do the same for Google Cloud', code('bash', 'terminal', 'curl -s https://www.gstatic.com/ipranges/cloud.json -o gcp.json\njq -r \'.prefixes[].scope\' gcp.json | sort -u | grep asia-south'), 'You should see asia-south1 and asia-south2.'),
    ('4 · Open the provider health pages', '<p>Visit <code>health.aws.amazon.com/health/status</code>, <code>azure.status.microsoft</code> and <code>status.cloud.google.com</code>. Find Mumbai on each.</p>', 'Clouds publish outages per region: one more proof they are real places.'),
    ('5 · Run the lesson script', code('bash', 'terminal', 'python3 l11_cloud_is_real.py'), 'Same output style as Step 1–4 above (numbers will be newer).')],
    cleanup='Nothing to delete: we only downloaded public files. From the AWS course onward, every lab ends with this box and a delete command.')
prac = prac.replace('<ol class="stepper">', caution('Do not create a cloud account with your card “just to look” yet. First learn budgets and alerts (AWS course, Lesson 1.3); most surprise bills come from forgotten resources.') + '<ol class="stepper">', 1)
mist = mistakes([
    ['“Cloud is just online storage like Google Drive.”', 'Drive is one SaaS product; people see only that face of the cloud.', 'Remember the 3 service models: rent machines (IaaS), platforms (PaaS) or finished apps (SaaS).'],
    ['“Cloud is always cheaper.”', 'Pay-per-use is cheap for spiky or small loads; steady 24×7 loads can cost more than owned servers.', 'Compare total cost (Lesson 1.5); use reserved/savings pricing for steady loads (Lesson 5.5).'],
    ['Surprise bill after a free trial.', 'A VM, disk, public IP or NAT gateway kept running; the meter never sleeps.', 'Budget alert first, tag resources, delete after every lab, check the billing page weekly.'],
    ['Slow app for Indian users.', 'Resources created in the default US region (e.g. us-east-1).', 'Pick ap-south-1 / Central India / asia-south1 before creating anything.'],
    ['Logging in as root / owner for daily work.', 'Sign-up account has full power; easy to keep using.', 'Enable MFA, create an admin user/role, lock the root user away (AWS 2.1).']])
cert = certbox([
    ['AWS CLF-C02', 'Domain 1 · Cloud Concepts (24%)', 'Define the AWS Cloud and its value: pay-as-you-go, elasticity, global reach, speed (agility), no guessing capacity.'],
    ['Azure AZ-900', 'Describe cloud concepts (25–30%)', 'Describe cloud computing, shared responsibility idea, consumption-based model.'],
    ['Google Cloud Digital Leader', 'Digital transformation with Google Cloud (~18%)', 'Why organisations move to cloud: speed, scale, cost model, innovation.'],
    ['C-DAC PGCP-BDA', 'Cloud Session 2', 'Definition, characteristics, components, cloud vendors (AWS/Azure/GCP).']],
    [('Which is NOT one of NIST’s five essential characteristics? (a) on-demand self-service (b) rapid elasticity (c) open source software (d) measured service', '<b>(c)</b>. The five are on-demand self-service, broad network access, resource pooling, rapid elasticity, measured service.'),
     ('A company pays only for the compute hours it used last month. Which characteristic/benefit is this?', 'Measured service → pay-as-you-go (trade capital expense for variable expense).'),
     ('TiffinGo adds servers for Diwali and removes them after. Which benefit of the cloud is this?', 'Elasticity: “stop guessing capacity”, scale out and in with demand.')])
proj = miniproject('Mini project: India cloud footprint report',
    'Write one script that prints, for AWS and Google Cloud, how many regions exist, which are in India, and how many address ranges Mumbai has; save it as a dated text report.',
    ['<code>mkdir cloud-report && cd cloud-report</code>', 'Download both JSON files with <code>curl</code> (Practical steps 1 and 3).',
     'Copy <code>l11_cloud_is_real.py</code> and add: <code>open(f"report-{date.today()}.txt","w").write(output)</code>.',
     'Run it every Monday for a month (Linux <code>cron</code>, see the Linux course) and <code>diff</code> two reports.',
     'Push the folder to GitHub (Git course) to share it.'],
    'A dated report such as “AWS 42 regions, India: ap-south-1, ap-south-2 · Mumbai: 304 entries, 221 unique IPv4 ranges”, and diffs showing new ranges over weeks.',
    'Python + JSON, Linux cron and diff, Git/GitHub.')


# ---------------- THE big picture: cloud computing architecture (textbook style)
def arch():
    o = t(320, 18, 'Cloud computing architecture', 11, 'ink', bold=True)
    o += box(16, 40, 140, 230, 'blue', rx=10) + t(86, 58, 'FRONT END', 9, 'blue', bold=True) + t(86, 70, 'what the user touches', 7.4, 'ink2')
    for i, (icn, lab) in enumerate([('phone', 'Mobile app'), ('laptop', 'Web browser'), ('user', 'CLI / API tools')]):
        y = 84 + i * 60
        o += box(30, y, 112, 48, 'card', rx=7) + ic(icn, 38, y + 12, 1, 'blue') + t(98, y + 28, lab, 8.4, 'ink', bold=True)
    o += box(170, 120, 74, 70, 'card', rx=10) + ic('globe', 195, 128, 1, 'acc') + t(207, 166, 'INTERNET', 8.4, 'ink', bold=True) + t(207, 178, 'network access', 6.8, 'ink2')
    o += arrow(156, 155, 168, 155, 'acc', 2) + arrow(244, 155, 258, 155, 'acc', 2)
    o += box(258, 40, 300, 230, 'green', rx=10) + t(408, 58, 'BACK END (provider’s data centres)', 9, 'green', bold=True)
    layers_ = [('app', 'Application', 'the app users see, e.g. Gmail, TiffinGo app'), ('cloud', 'Service', 'what the provider sells, e.g. EC2 VMs, S3, Gmail'),
               ('gear', 'Runtime cloud', 'where code runs: Linux, Java/Python, containers'), ('disk', 'Storage', 'where data lives: S3 buckets, disks, file shares'),
               ('chip', 'Infrastructure', 'physical servers, network, hypervisor → VMs')]
    for i, (icn, lab, sub) in enumerate(layers_):
        y = 68 + i * 40
        o += box(270, y, 276, 34, 'card', rx=6) + ic(icn, 278, y + 5, 1, 'green') + t(310, y + 15, lab, 8.6, 'ink', anchor='start', bold=True) + t(310, y + 27, sub, 7, 'ink2', anchor='start')
    o += box(568, 40, 60, 110, 'violet', rx=8) + ic('gear', 586, 52, 1, 'violet') + t(598, 92, 'Manage-', 7.6, 'ink', bold=True) + t(598, 102, 'ment', 7.6, 'ink', bold=True) + t(598, 116, 'monitor,', 6.6, 'ink2') + t(598, 125, 'scale, bill', 6.6, 'ink2')
    o += box(568, 160, 60, 110, 'red', rx=8) + ic('shield', 586, 172, 1, 'red') + t(598, 212, 'Security', 7.6, 'ink', bold=True) + t(598, 226, 'identity,', 6.6, 'ink2') + t(598, 235, 'encryption', 6.6, 'ink2')
    o += t(320, 292, 'Front end and back end talk over the internet. The provider runs the back end; you use it on demand and pay per use.', 8, 'ink2')
    return o
ARCH = bigfig('Cloud computing architecture: front end (mobile app, browser, CLI) connects over the internet to the back end in the provider data centres, with layers application, service, runtime cloud, storage and infrastructure, and management and security across all layers.', arch(), h=316)

def nist():
    o = t(320, 18, 'The NIST model of cloud computing: 5 + 3 + 4', 11, 'ink', bold=True)
    cols = [('5 essential characteristics', 'blue', [('user', 'On-demand self-service'), ('globe', 'Broad network access'), ('server', 'Resource pooling'), ('chart', 'Rapid elasticity'), ('meter', 'Measured service')]),
            ('3 service models', 'green', [('chip', 'IaaS: rent infrastructure'), ('gear', 'PaaS: rent a platform'), ('app', 'SaaS: use finished software')]),
            ('4 deployment models', 'violet', [('cloud', 'Public cloud'), ('shield', 'Private cloud'), ('lb', 'Hybrid cloud'), ('user', 'Community cloud')])]
    for c, (head, tn, items) in enumerate(cols):
        x = 16 + c * 208
        o += box(x, 32, 196, 30, tn, rx=8) + t(x + 98, 51, head, 9, 'ink', bold=True)
        for i, (icn, lab) in enumerate(items):
            y = 70 + i * 34
            o += box(x, y, 196, 28, 'card', rx=6) + ic(icn, x + 6, y + 3, 0.92, tn) + t(x + 34, y + 18, lab, 8.2, 'ink', anchor='start')
    return o + t(320, 252, 'Modules 2 and 3 of this course cover the service and deployment models in depth.', 8, 'ink2')
NIST = bigfig('NIST model: five essential characteristics, three service models (IaaS, PaaS, SaaS) and four deployment models (public, private, hybrid, community).', nist(), h=266)

picture = ('  <p>Every cloud, from AWS to Google Cloud, has the same two halves: a <b>front end</b> you touch and a <b>back end</b> the provider runs. Read the diagram left to right: your phone or browser sends a request over the internet; in the provider’s data centre it passes down through layers of software and hardware; management and security watch every layer.</p>\n'
    + ARCH + '\n  <p>NIST (the US standards body) defines cloud computing with a simple <b>5 + 3 + 4</b> model. Exams quote it word for word, so learn this picture.</p>\n' + NIST)

N = {'phone': (6, 58, 54, 50, 'phone', 'Riya’s phone', 'TiffinGo app'), 'dns': (70, 6, 52, 48, 'dns', 'DNS', 'name → IP'),
     'lb': (138, 58, 54, 50, 'lb', 'Load balancer', 'front door'), 'vm1': (204, 8, 50, 46, 'server', 'VM 1', 'app code'),
     'vm2': (204, 60, 50, 46, 'server', 'VM 2', 'app code'), 'vm3': (204, 110, 50, 46, 'server', 'VM 3', 'Diwali extra'),
     'db': (270, 30, 54, 50, 'db', 'Database', 'orders'), 'meter': (270, 100, 54, 50, 'meter', 'Meter', 'billing')}
REGION = '<rect x="132" y="2" width="224" height="156" rx="10" style="fill:none;stroke:var(--track);stroke-dasharray:5 3"/>' + t(300, 13, 'Mumbai region (ap-south-1)', 6.8, 'acc', bold=True)
base = ['phone', 'dns', 'lb', 'vm1', 'vm2', 'db', 'meter']
steps_ = [
    dict(on=base, hot='phone', head='Step 1 · Riya taps “Order”', text='The TiffinGo app sends an HTTPS request to api.tiffingo.in.', text2='Her phone is the front end; it needs only the internet.', svc='Front end: any phone, browser or CLI'),
    dict(on=base, hot='dns', move=(60, 70, 72, 40, 'name?'), head='Step 2 · DNS finds the address', text='DNS turns api.tiffingo.in into an IP address in Mumbai,', text2='like the 16.4.0.0/16 range in the Real proof section.', svc='AWS Route 53 · Azure DNS · Google Cloud DNS'),
    dict(on=base, hot='lb', move=(60, 83, 138, 83, 'HTTPS'), head='Step 3 · Into the region, to the load balancer', text='The request crosses the internet (broad network access) into', text2='the Mumbai region. The load balancer is the single front door.', svc='AWS Elastic Load Balancing · Azure Load Balancer · Cloud Load Balancing'),
    dict(on=base, hot='vm1', move=(192, 78, 206, 34, ''), head='Step 4 · A virtual machine runs the code', text='The load balancer picks a healthy VM. Each VM is a slice of a', text2='big physical server shared with other customers (pooling).', svc='AWS EC2 · Azure Virtual Machines · Google Compute Engine'),
    dict(on=base, hot='db', move=(254, 30, 272, 50, 'save'), head='Step 5 · The order is saved', text='The app code writes the order into a managed database that', text2='the provider patches and backs up for you.', svc='AWS RDS · Azure SQL Database · Google Cloud SQL'),
    dict(on=base, hot='phone', move=(206, 40, 60, 78, 'OK'), head='Step 6 · Reply: “Order placed!”', text='The answer travels back the same way in a fraction of a second.', text2='Riya never sees a server, only the app.', svc='Path: phone → DNS → load balancer → VM → database → phone'),
    dict(on=base + ['vm3'], hot='vm3', move=(192, 90, 206, 128, '+1 VM'), head='Step 7 · Diwali: orders ×4', text='CPU goes high, so auto scaling starts VM 3 in minutes without', text2='calling anyone (rapid elasticity + on-demand self-service).', svc='AWS EC2 Auto Scaling · Azure VM Scale Sets · Google managed instance groups'),
    dict(on=base, hot='meter', move=(254, 84, 272, 120, 'usage'), head='Step 8 · Every second is metered', text='VM-hours, GB stored and requests go to the meter → monthly', text2='bill (measured service). After Diwali VM 3 is removed.', svc='AWS Billing · Azure Cost Management · Google Cloud Billing')]
HOW = flow_anim('What happens when Riya taps “Order”', 'Eight steps from a tap to a bill. Watch which cloud service acts at each step.', 'One cloud request', 'Animated journey of one order: phone, DNS, load balancer, virtual machine, database, reply, auto scaling on Diwali, metering.', N, steps_, static=REGION, hid='journey')
how_after = '\n  <p>All <b>five characteristics</b> appeared in one order: the request came over the <b>network</b> (step 3), ran on a <b>pooled</b> VM (step 4), extra capacity came by <b>self-service</b> and <b>elasticity</b> (step 7), and everything was <b>measured</b> (step 8).</p>'


# ---------- one illustration per characteristic
def il_self():
    o = box(14, 30, 110, 80, 'card', rx=8) + ic('laptop', 50, 40, 1.4, 'blue') + box(34, 84, 70, 18, 'acc', rx=9) + t(69, 96, 'Create VM', 7.6, 'ink', bold=True)
    o += arrow(130, 70, 170, 70, 'acc', 2.4) + t(150, 62, '2 min', 7.4, 'acc', bold=True)
    o += box(178, 36, 108, 68, 'green', rx=8) + ic('server', 220, 44, 1.2, 'green') + t(232, 90, 'Your new VM', 8, 'ink', bold=True)
    return o + t(150, 132, 'No ticket, no phone call, no waiting for a vendor', 8, 'ink2')
def il_net():
    o = box(110, 40, 80, 60, 'acc', rx=30) + ic('cloud', 136, 50, 1.2, 'acc') + t(150, 92, 'Cloud', 8, 'ink', bold=True)
    for (x, y, icn, lab) in [(14, 20, 'phone', 'Phone'), (14, 90, 'laptop', 'Laptop'), (236, 20, 'server', 'Server'), (236, 90, 'user', 'CLI')]:
        o += box(x, y, 50, 40, 'card', rx=6) + ic(icn, x + 13, y + 3, 1, 'blue') + t(x + 25, y + 36, lab, 7, 'ink', bold=True)
        o += f'<line x1="{x + 50 if x < 100 else x}" y1="{y + 20}" x2="{110 if x < 100 else 190}" y2="70" style="stroke:var(--blue);stroke-width:1.6;stroke-dasharray:4 3"/>'
    return o + t(150, 140, 'Any device, any place, over standard internet', 8, 'ink2')
def il_pool():
    o = box(20, 22, 260, 96, 'card', rx=8) + t(150, 36, 'One physical server in Mumbai (96 CPUs)', 8, 'ink', bold=True)
    for k, (lab, tn, w) in enumerate([('Customer A', 'blue', 80), ('Customer B', 'green', 60), ('TiffinGo', 'amber', 70), ('free', 'card', 34)]):
        x = 30 + sum([80, 60, 70, 34][:k]) + k * 4
        o += box(x, 48, w, 56, tn, rx=6) + t(x + w / 2, 72, lab, 7.4, 'ink', bold=True) + (t(x + w / 2, 86, 'VM', 7, 'ink2') if lab != 'free' else '')
    return o + t(150, 138, 'Many customers share hardware, each in an isolated VM', 8, 'ink2')
def il_elastic():
    traffic = [2, 2, 3, 6, 9, 9, 5, 2]
    o = t(150, 16, 'Orders (line) and servers (bars)', 8, 'ink', bold=True)
    pts = ' '.join(f'{30 + i * 34},{118 - v * 10}' for i, v in enumerate(traffic))
    for i, v in enumerate(traffic):
        sv = max(1, round(v / 3 + 0.4))
        o += box(22 + i * 34, 118 - sv * 18, 16, sv * 18, 'green', rx=2)
    o += f'<polyline points="{pts}" style="fill:none;stroke:#D64545;stroke-width:2.4"/>'
    return o + t(150, 136, 'Servers rise with demand and fall after: you never guess', 8, 'ink2')
def il_meter():
    o = box(16, 26, 90, 90, 'card', rx=45) + ic('meter', 43, 46, 1.5, 'acc') + t(61, 104, 'meter', 7.4, 'ink2')
    o += arrow(112, 70, 142, 70, 'acc', 2.2)
    o += box(150, 22, 134, 96, 'card', rx=6) + t(160, 38, 'Bill · November', 8, 'ink', anchor='start', bold=True)
    for k, (a, b) in enumerate([('VM 720 h × $0.0112', '$8.06'), ('Storage 500 GB', '$12.50'), ('Requests 200k', '$1.00')]):
        o += t(160, 56 + k * 14, a, 7, 'ink2', anchor='start') + t(278, 56 + k * 14, b, 7, 'ink', anchor='end', bold=True)
    o += f'<line x1="160" y1="98" x2="278" y2="98" style="stroke:var(--line)"/>' + t(160, 110, 'Total', 7.6, 'ink', anchor='start', bold=True) + t(278, 110, '$21.56', 7.6, 'acc', anchor='end', bold=True)
    return o + t(150, 138, 'Pay for exactly what you used (Mumbai prices, Lesson 1.3)', 8, 'ink2')
parts = pic_cards([
    (il_self(), '1. On-demand self-service', 'You create servers, storage or databases yourself from a console, CLI or API, any time.', 'Journey step 7: VM 3 started by itself'),
    (il_net(), '2. Broad network access', 'Resources are reached over the network from standard devices: phone, laptop, another server.', 'Journey step 3: request over the internet'),
    (il_pool(), '3. Resource pooling', 'The provider’s big servers are shared by many customers; each gets an isolated slice (a VM).', 'Journey step 4: VM is a slice'),
    (il_elastic(), '4. Rapid elasticity', 'Capacity grows and shrinks quickly with demand and looks unlimited to you.', 'Diwali: 2 → 3 VMs and back'),
    (il_meter(), '5. Measured service', 'Every hour, GB and request is metered; you pay only for what you used, like electricity.', 'Journey step 8: the meter')])

# ---------- animation 2: elasticity through one day
def day_frame(k):
    hrs = ['9 am', '1 pm', '8 pm', '8 pm (Diwali)', '2 am']
    load = [3, 6, 7, 12, 1]
    srv = [2, 3, 3, 5, 1]
    o = t(180, 14, f'TiffinGo at {hrs[k]}', 9.4, 'ink', bold=True)
    o += t(60, 32, 'orders / minute', 7.4, 'ink2') + box(20, 40, 80, 100, 'card', rx=6) + box(34, 140 - load[k] * 8, 52, load[k] * 8, 'red', rx=3) + t(60, 136 - load[k] * 8, f'{load[k] * 100}', 8, 'ink', bold=True)
    o += arrow(108, 90, 140, 90, 'acc', 2.2) + t(124, 82, 'scale', 7, 'acc', bold=True)
    for i in range(6):
        x = 150 + (i % 3) * 66; y = 36 + (i // 3) * 58
        o += node_box(x, y, 58, 50, 'server', f'VM {i + 1}', 'running' if i < srv[k] else 'off', on=i < srv[k], hot=(i == srv[k] - 1 and k in (1, 3)))
    return o
EL_STEPS = [('9 am: normal load', 'About 300 orders a minute; 2 VMs are enough.', 'Policy: keep CPU near 50%'),
            ('1 pm: lunch rush', 'Orders double; CPU crosses 50%, auto scaling adds VM 3.', 'Scale out: + 1 VM in about 2 minutes'),
            ('8 pm: dinner', 'Load is high but steady; 3 VMs handle it.', 'No change: target met'),
            ('Diwali night', 'Orders ×4; auto scaling adds VM 4 and VM 5.', 'Scale out again; site stays up'),
            ('2 am: quiet', 'Only 100 orders; extra VMs are removed, 1 stays.', 'Scale in: the meter stops for removed VMs')]
fr = []
for k, (h, a, b) in enumerate(EL_STEPS):
    fr.append(day_frame(k) + box(6, 160, 348, 58, 'blue', rx=8) + t(14, 176, h, 8.6, 'ink', anchor='start', bold=True) + t(14, 191, a, 7.6, 'ink', anchor='start') + t(14, 206, b, 7, 'ink2', anchor='start'))
ELASTIC = anim_one('How it works', 'Elasticity through one day', 'Watch the number of running VMs follow the orders. This is what “stop guessing capacity” means.', 'Auto scaling', 'Animation: orders and running VMs at 9 am, 1 pm, 8 pm, Diwali night and 2 am.', fr, [x[0] + '.' for x in EL_STEPS], delay=5500, hid='elastic')
parts = parts + '\n  <h3>Elasticity, step by step</h3>\n' + ELASTIC + '\n  <h3>Three ways to define it</h3>\n' + types_html

SUMMARY = big_mindmap('Mind map of lesson 1.1: definition, NIST five characteristics, service models, deployment models, architecture parts, providers in India, benefits and cautions.', 'Cloud computing', [
    ('Definition', 'blue', 'cloud', ['rent IT over the internet', 'on demand, pay per use', 'NIST SP 800-145']),
    ('5 characteristics', 'green', 'chart', ['self-service', 'network access', 'pooling', 'elasticity', 'measured']),
    ('Architecture', 'violet', 'server', ['front end: app, browser', 'internet', 'back end: 5 layers', 'management + security']),
    ('Models', 'acc', 'app', ['IaaS · PaaS · SaaS', 'public · private', 'hybrid · community']),
    ('Providers (India)', 'amber', 'globe', ['AWS: Mumbai, Hyderabad', 'Azure: Pune, Chennai, Mumbai', 'GCP: Mumbai, Delhi']),
    ('Remember', 'red', 'shield', ['budget alert first', 'right region', 'delete after labs'])], h=380, caption='Lesson 1.1 on one page: use it for revision.')
cert = cert + '\n  <h3>Lesson 1.1 on one page</h3>\n' + SUMMARY
assemble_v2(HERE, story_h2='The Diwali crash that cloud would have prevented', hook_html=hk,
    narration='TiffinGo, our food-delivery startup, owns 6 servers in a rented rack. Every festival the orders jump four times and the site falls over; the rest of the year the servers sit almost idle.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='What is cloud computing?',
    formal='<b>Cloud computing</b> (NIST SP 800-145) is a model for enabling ubiquitous, convenient, on-demand network access to a shared pool of configurable computing resources (networks, servers, storage, applications and services) that can be rapidly provisioned and released with minimal management effort or service-provider interaction.',
    simple='Renting computers, storage and software over the internet, starting them yourself in minutes and paying only for what you use.',
    interview=['“Cloud computing is the on-demand delivery of IT resources such as servers, storage, databases and software over the internet, with pay-as-you-go pricing.”', '“NIST defines it by five characteristics — on-demand self-service, broad network access, resource pooling, rapid elasticity and measured service — three service models, IaaS, PaaS and SaaS, and four deployment models: public, private, hybrid and community.”', '“For example, a food-delivery app adds servers automatically during Diwali and removes them after, paying only for that week.”'],
    terms_rows=[('Cloud provider', 'Company that runs the data centres (AWS, Microsoft, Google).'), ('Region', 'A city/area with data centres, e.g. Mumbai.'), ('Front end / back end', 'What you touch / what the provider runs.'), ('Virtual machine (VM)', 'A software computer, a slice of a real server.'), ('Load balancer', 'Front door that spreads requests over servers.'), ('DNS', 'Internet phone book: name → IP address.'), ('HTTPS', 'Encrypted way browsers and apps talk to servers.'), ('API', 'A way for programs to ask a service to do something.'), ('Availability Zone', 'One or more separate data centres inside a region.'), ('Elasticity', 'Grow and shrink automatically.'), ('Measured service', 'Metered, pay per use.'), ('CapEx / OpEx', 'Buy up front / pay as you go.')],
    exam='Learn the 5 NIST characteristics word for word. AWS phrases the benefits as: trade fixed expense for variable expense, benefit from massive economies of scale, stop guessing capacity, increase speed and agility, stop spending money running data centres, go global in minutes.',
    picture_h2='Front end, back end and the NIST model', picture_html=picture,
    how_h2='One order, eight steps, five characteristics', how_intro='This is what really happens inside the cloud when a customer uses an app. Each step names the service that acts, in AWS, Azure and Google Cloud.', how_anim=HOW, how_after=how_after,
    parts_h2='The five characteristics, one by one', parts_html=parts, lv='',
    myth_rows=[('The cloud is not a real place.', '42 AWS regions and 48 Google regions, each with buildings and IP ranges.', 'Real proof, steps 1 and 3.'), ('Cloud means storage only.', 'The order used DNS, a load balancer, VMs and a database.', 'Animation, steps 2–5.'), ('Cloud is always cheaper.', 'Cheaper for spiky loads; steady loads need pricing plans.', 'Mistakes table.')],
    clouds_html=clouds, proof_h2='Proof that the cloud is real hardware', proof_intro='All outputs are real: the public IP-range files published by AWS and Google Cloud, downloaded on 10 Nov 2026 with a short Python script. Note: the AWS file lists 42 region codes because it includes special regions (GovCloud, China and others); the 34 normal commercial regions appear in Lesson 1.2.', proof_steps=steps,
    practical_html=prac, mistakes_html=mist, cert_html='', project_html='',
    can_now=['Define cloud computing in one sentence and with the NIST 5 + 3 + 4 model.', 'Draw the front end / back end architecture and name its layers.', 'Explain the 8 steps of a cloud request and which AWS/Azure/GCP service acts at each.', 'Give an example for each of the five characteristics.', 'Find real AWS and Google Cloud regions in India from public data.'], next_html='<a href="../02-history-and-evolution-of-cloud-computing/">1.2 History and evolution: how we got here, and the computing paradigms before cloud</a>.',
    pre='<b>Before you start:</b> nothing! This is the first lesson. Basic computer knowledge is enough; the <a href="../../../linux/">Linux course</a> helps for the hands-on parts.')
