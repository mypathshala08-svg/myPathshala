import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
B = '../../'
V = 'l12_virt.txt'

hk = hook('Who invented the cloud? Was it Amazon in 2006, or is it much older?',
    'The cloud is the answer to a 60-year-old problem: <b>computers are expensive, and most of the time they sit idle</b>. Every era — mainframes, PCs, server rooms, grids, virtualization — fixed one part of that problem and created a new one. In 2006 AWS put the last pieces together: rent a slice of a server, start it yourself, pay by the hour.',
    ['Six eras, each as a picture: what it solved and what it broke.', 'Virtualization: the one technology that made the cloud possible.', 'When AWS, Azure and Google Cloud started, and what came next.'])

def bar_scene():
    eras = [('1960s', 'Mainframe'), ('1980s', 'PC'), ('1990s', 'Server room'), ('2000s', 'Virtualization'), ('2006+', 'Cloud')]
    idle = [10, 70, 85, 40, 10]
    o = t(180, 14, 'How much of the paid-for computer sat idle? (typical)', 8.2, 'ink', bold=True)
    for i, ((y, n), v) in enumerate(zip(eras, idle)):
        x = 22 + i * 66
        o += box(x, 120 - v, 44, v, 'red' if v > 50 else 'green', rx=4) + t(x + 22, 114 - v, f'{v}%', 8, 'ink', bold=True)
        o += t(x + 22, 132, y, 7.4, 'ink', bold=True) + t(x + 22, 142, n, 6.8, 'ink2')
    return o
scene_svg = scene('Bar chart: typical share of idle paid-for computing in each era: mainframe low, PCs and server rooms high, virtualization lower, cloud low because you pay only when used.', bar_scene(),
                  'The whole history is a fight against <tspan font-weight="700" class="s-acc">idle, paid-for computers</tspan>.', h=172)
dialogue = '''R> Sir, my uncle worked on a bank mainframe in the 1980s. He says “cloud is just mainframes again”. Is he right?
A> Half right! Both share one big pool of computing and charge for use. But in between, the world went through PCs, server rooms full of idle machines, and then virtualization. Each step fixed something.
K> So the cloud is the latest fix?
A> Yes. Let’s walk through the eras like a story, one picture at a time, and see what problem each one solved.'''

# ---------- big picture: illustrated evolution
def era_pic(x, kind):
    o = ''
    if kind == 'mainframe':
        o += box(x + 30, 6, 40, 46, 'blue', rx=4) + t(x + 50, 34, 'MF', 8, 'ink', bold=True)
        for k in range(3):
            tx = x + 4 + k * 34
            o += box(tx, 64, 24, 16, 'card', rx=2) + f'<line x1="{tx + 12}" y1="64" x2="{x + 50}" y2="52" style="stroke:var(--line)"/>'
    elif kind == 'pc':
        for k in range(3):
            tx = x + 6 + k * 32
            o += box(tx, 20, 26, 20, 'card', rx=2) + box(tx + 8, 42, 10, 4, 'card', rx=1) + ic('user', tx + 4, 52, 0.75, 'blue')
    elif kind == 'room':
        for k in range(4):
            o += box(x + 10 + k * 22, 10, 18, 66, 'card', rx=2) + ''.join(box(x + 12 + k * 22, 14 + j * 15, 14, 10, 'red' if (k + j) % 3 else 'green', rx=1) for j in range(4))
    elif kind == 'grid':
        for k in range(6):
            cx_, cy_ = x + 18 + (k % 3) * 32, 22 + (k // 3) * 36
            o += ic('server', cx_ - 9, cy_ - 9, 0.75, 'violet')
        o += f'<rect x="{x + 4}" y="6" width="92" height="72" rx="8" style="fill:none;stroke:var(--violet);stroke-dasharray:4 3"/>'
    elif kind == 'vm':
        o += box(x + 8, 8, 84, 70, 'card', rx=4) + t(x + 50, 20, 'one server', 7, 'ink2')
        for k, tn in enumerate(['blue', 'green', 'amber']):
            o += box(x + 14 + k * 26, 28, 22, 42, tn, rx=3) + t(x + 25 + k * 26, 52, 'VM', 6.6, 'ink', bold=True)
    elif kind == 'cloud':
        o += box(x + 6, 10, 88, 54, 'acc', rx=27) + ic('cloud', x + 38, 18, 1, 'acc') + t(x + 50, 54, 'rent + meter', 7, 'ink', bold=True)
        o += ic('phone', x + 10, 64, 0.6, 'blue') + ic('laptop', x + 74, 64, 0.6, 'blue')
    return o
def evolution():
    eras = [('1960s–70s', 'Mainframe + terminals', 'mainframe', 'Solved: computing for big firms', 'Broke: very costly, central'),
            ('1980s–90s', 'Personal computers', 'pc', 'Solved: computer on every desk', 'Broke: scattered, hard to manage'),
            ('1990s–2000s', 'Server rooms (client-server, web)', 'room', 'Solved: shared apps over a network', 'Broke: one app per server, idle'),
            ('late 1990s', 'Grid / utility computing', 'grid', 'Solved: pool machines for big jobs', 'Broke: hard to use, for experts'),
            ('1999 →', 'Virtualization', 'vm', 'Solved: many VMs on one server', 'Broke: still your own hardware'),
            ('2006 →', 'Cloud computing', 'cloud', 'Solved: rent VMs, self-service, pay/hour', 'Next: serverless, AI, edge')]
    o = t(320, 16, 'The evolution of computing, era by era', 11, 'ink', bold=True)
    for i, (yr, name, kind, good, bad) in enumerate(eras):
        col, row = i % 3, i // 3
        x = 14 + col * 208; y = 30 + row * 168
        o += box(x, y, 198, 158, 'acc' if kind == 'cloud' else 'card', rx=10)
        o += t(x + 12, y + 18, yr, 8.4, 'acc', anchor='start', bold=True) + t(x + 12, y + 32, name, 9, 'ink', anchor='start', bold=True)
        o += t(x + 12, y + 136, '✔ ' + good, 7.2, 'green', anchor='start') + t(x + 12, y + 149, '✘ ' + bad, 7.2, 'red', anchor='start')
        if i < 5:
            if col < 2:
                o += arrow(x + 198, y + 80, x + 208, y + 80, 'acc', 2)
    return o
def evolution2():
    # place pictures with vertical offset per card
    eras = ['mainframe', 'pc', 'room', 'grid', 'vm', 'cloud']
    o = ''
    for i, kind in enumerate(eras):
        col, row = i % 3, i // 3
        x = 14 + col * 208; y = 30 + row * 168
        o += f'<g transform="translate(0,{y + 40})">' + era_pic(x + 49, kind) + '</g>'
    return o
EVO = bigfig('Six illustrated eras: mainframe with terminals, personal computers, server rooms with mostly idle servers, grid computing, virtualization with three VMs on one server, and cloud computing rented over the internet; each with what it solved and what problem it left.', evolution() + evolution2(), h=386,
             caption='Read left to right, top then bottom: each era fixes the problem (✘) of the one before.')
def years_chart():
    data = [(2006, 1), (2009, 3), (2010, 10), (2012, 22), (2014, 47), (2016, 91), (2017, 141), (2018, 223), (2020, 300), (2022, 363), (2024, 410), (2026, 436)]
    o = t(320, 16, 'How fast the cloud grew: AWS services in the AWS SDK (cumulative)', 10, 'ink', bold=True)
    o += f'<line x1="50" y1="200" x2="620" y2="200" style="stroke:var(--line)"/>'
    for i, (y, v) in enumerate(data):
        x = 60 + i * 47; hgt = v * 0.38
        o += box(x, 200 - hgt, 30, hgt, 'acc' if y in (2017, 2018) else 'blue', rx=3) + t(x + 15, 194 - hgt, str(v), 8, 'ink', bold=True) + t(x + 15, 214, str(y), 8, 'ink2')
    return o + t(320, 236, 'Real data from botocore 1.43.127 (10 Nov 2026), by year of each service’s oldest API version. 2017–2018 added 132 services.', 7.8, 'ink2')
GROW = bigfig('Bar chart of AWS services known by the AWS SDK, cumulative: 1 in 2006, 22 in 2012, 91 in 2016, 223 in 2018, 363 in 2022, 436 in 2026.', years_chart(), h=248)
picture = ('  <p>Read the picture like a comic strip. Every era was built to fix the biggest pain of the era before it. Look at the green tick (what it solved) and the red cross (what it left broken) — the next card fixes that cross.</p>\n'
           + EVO + '\n  <p>Once the cloud arrived, it grew very fast. The AWS SDK (the library every cloud tool uses) shows how many services AWS added each year:</p>\n' + GROW)

# ---------- animation 1: the same app across eras (TiffinGo's grandfather company)
def era_frame(k):
    o = ''
    if k == 0:   # mainframe
        o += node_box(150, 10, 64, 54, 'chip', 'Mainframe', 'bank HQ', hot=True)
        for i in range(4):
            o += node_box(14 + i * 86, 98, 60, 46, 'laptop', f'Terminal {i + 1}', 'no CPU') + f'<line x1="{44 + i * 86}" y1="98" x2="182" y2="64" style="stroke:var(--line)"/>'
    elif k == 1:  # PCs
        for i in range(5):
            o += node_box(10 + i * 70, 40, 60, 54, 'laptop', f'PC {i + 1}', 'own copy', hot=(i == 2))
        o += t(180, 120, 'every desk has its own software and files', 8, 'ink2')
    elif k == 2:  # server room
        for i, (n, u) in enumerate([('Mail', '8%'), ('Website', '15%'), ('Accounts', '5%'), ('HR', '3%'), ('Backup', '10%')]):
            o += node_box(10 + i * 70, 30, 60, 54, 'server', n + ' server', f'busy {u}', hot=True)
        o += t(180, 112, 'one application per server → mostly idle', 8.4, 'red', bold=True)
    elif k == 3:  # virtualization
        o += box(40, 16, 280, 116, 'card', rx=10) + t(180, 30, 'ONE physical server + hypervisor', 8.4, 'ink', bold=True)
        for i, n in enumerate(['Mail', 'Website', 'Accounts', 'HR', 'Backup']):
            o += node_box(48 + i * 54, 40, 48, 50, 'server', 'VM', n, hot=True)
        o += t(180, 120, 'busy 41% · 4 servers switched off', 8, 'green', bold=True)
    elif k == 4:  # cloud
        o += box(150, 10, 200, 128, 'card', rx=10) + t(250, 24, 'Provider region (Mumbai)', 8, 'acc', bold=True)
        for i in range(6):
            o += node_box(158 + (i % 3) * 63, 32 + (i // 3) * 52, 56, 48, 'server', 'VM', 'rented' if i < 4 else 'other customer', on=True, hot=i < 4)
        o += node_box(10, 50, 70, 54, 'user', 'Bank IT', 'console/API') + packet(80, 77, 158, 77, 'create VM')
    elif k == 5:  # serverless
        o += node_box(10, 50, 70, 54, 'phone', 'Customer', 'opens app') + packet(80, 77, 150, 77, 'request')
        o += box(150, 20, 196, 110, 'green', rx=10) + ic('gear', 236, 34, 1.2, 'green') + t(248, 76, 'Function runs 200 ms', 8.6, 'ink', bold=True) + t(248, 92, 'no server to manage', 7.6, 'ink2') + t(248, 108, 'billed per millisecond', 7.6, 'ink2')
    return o
ERAS = [('1975 · Mainframe', 'The bank rents time on one huge computer. Branch terminals have no CPU.', 'Solved: computing for a big firm · Problem: costly, everything central'),
        ('1990 · PCs', 'Every clerk gets a PC with its own copy of software and files.', 'Solved: computing on every desk · Problem: messy to manage and share'),
        ('2000 · Server room', 'Shared apps move to servers: one application per server.', 'Solved: sharing over the network · Problem: servers idle 85–95%'),
        ('2008 · Virtualization', 'A hypervisor runs all five apps as VMs on one server.', 'Solved: idle hardware · Problem: still buy, house and fix servers'),
        ('2016 · Cloud', 'The bank rents VMs in Mumbai from a console; pays per hour.', 'Solved: no hardware to own · Shared with other customers (pooling)'),
        ('2024 · Serverless', 'Code runs only when a customer acts, billed per millisecond.', 'Solved: no servers to manage at all · Next: AI services, edge')]
fr = []
for k, (h, a, b) in enumerate(ERAS):
    fr.append(era_frame(k) + box(6, 158, 348, 62, 'blue', rx=8) + t(14, 174, h, 9, 'ink', anchor='start', bold=True) + t(14, 190, a, 7.6, 'ink', anchor='start') + t(14, 206, b, 7.2, 'ink2', anchor='start'))
ERA_ANIM = anim_one('How it works', 'One bank, fifty years: watch the setup change', 'The same banking work, done the way each era allowed. Each frame shows the setup, what it solved and what problem pushed the next change.', 'Evolution', 'Animation of one bank’s IT from mainframe to PCs, server room, virtualization, cloud and serverless.', fr, [x[0].split('·')[1].strip() + '.' for x in ERAS], delay=6000, hid='eras')

# ---------- animation 2: how virtualization turned into cloud
VN = {'hw': (130, 112, 100, 42, 'chip', 'Physical server', '96 CPUs, 384 GB'), 'hv': (130, 64, 100, 42, 'gear', 'Hypervisor', 'KVM / Xen'),
      'v1': (40, 10, 70, 46, 'server', 'VM A', '2 CPU'), 'v2': (145, 10, 70, 46, 'server', 'VM B', '4 CPU'), 'v3': (250, 10, 70, 46, 'server', 'VM C', '8 CPU'),
      'portal': (10, 98, 100, 52, 'laptop', 'Self-service', 'console + API'), 'meter': (250, 98, 100, 52, 'meter', 'Meter', 'per second')}
VS = [dict(on=['hw'], hot='hw', head='Step 1 · One powerful physical server', text='A modern server has dozens of CPU cores and hundreds of GB of RAM.', text2='One application alone uses only a small part of it.', svc='This is the “Infrastructure” layer from Lesson 1.1'),
      dict(on=['hw', 'hv'], hot='hv', head='Step 2 · Add a hypervisor', text='A thin software layer (KVM, Xen, Hyper-V, VMware ESXi) takes over', text2='the hardware and can split it into isolated pieces.', svc='AWS Nitro (KVM-based) · Azure Hyper-V · Google KVM'),
      dict(on=['hw', 'hv', 'v1', 'v2', 'v3'], hot='v2', move=(180, 64, 180, 56, ''), head='Step 3 · Many virtual machines', text='Each VM gets its own CPUs, memory and operating system,', text2='isolated from the others. Utilisation goes up, servers go down.', svc='This is virtualization (1999 →): still inside YOUR data centre'),
      dict(on=['hw', 'hv', 'v1', 'v2', 'v3', 'portal'], hot='portal', move=(110, 120, 150, 40, 'create'), head='Step 4 · Add self-service', text='Put a website and API in front so customers create VMs themselves,', text2='in minutes, with no ticket to the IT team.', svc='On-demand self-service (NIST)'),
      dict(on=list(VN), hot='meter', move=(215, 34, 290, 100, 'usage'), head='Step 5 · Add a meter and open it to everyone', text='Count every VM-second and bill it. Let anyone on the internet sign up.', text2='Virtualization + self-service + metering + internet = public cloud.', svc='AWS EC2 (2006) · Azure VMs (preview 2012, GA 2013) · Google Compute Engine (2012/13)')]
VIRT = flow_anim('From virtualization to cloud in five steps', 'Why do people say “virtualization made the cloud possible”? Watch a single server turn into a cloud service.', 'Virtualization → cloud', 'Animation: physical server, hypervisor, virtual machines, self-service portal, meter.', VN, VS, hid='virt')
how_after = '\n  <p>Notice: steps 1–3 existed in company data centres from about 2000. The <b>cloud</b> appeared when providers added steps 4 and 5 and opened them to anyone with a card. That is exactly the NIST list from Lesson 1.1.</p>'

# ---------- parts: era cards with pictures
def card_pic(kind, title_):
    return box(10, 10, 280, 104, 'card', rx=8) + f'<g transform="translate(60,22) scale(1.3)">' + era_pic(0, kind) + '</g>' + t(150, 132, title_, 8.4, 'ink', bold=True)
parts = '  <p>The picture above showed the eras; here is the detail of each, in one line of story and one idea the cloud kept.</p>\n' + cards([('1. Mainframe and time-sharing (1960s–70s)', 'Huge, costly computers shared by many users through “dumb” terminals; companies paid for computer time. In 1961 John McCarthy said computing could one day be sold like a public utility.', 'Idea kept: sharing + metering'), ('2. Personal computers (1980s–90s)', 'Cheap PCs put computing on every desk, but data and software were scattered and hard to manage.', 'Idea kept: cheap standard hardware'), ('3. Client-server and the web (1990s)', 'Shared applications moved to servers reached over networks and the internet. Usually one application per server, so most servers sat idle.', 'Idea kept: access over the network'), ('4. Grid and utility computing (late 1990s–2000s)', 'Many computers pooled to solve big scientific jobs; companies tried “utility” pricing. Powerful but hard to use.', 'Idea kept: resource pooling'), ('5. Virtualization (1999 →)', 'VMware (1999), Xen (2003) and KVM (2007) let one server run many isolated virtual machines, raising utilisation.', 'Idea kept: VMs, multitenancy'), ('6. Cloud computing (2006 →)', 'AWS S3 (March 2006) and EC2 (August 2006) let anyone rent storage and VMs over the internet, self-service, by the hour. Salesforce (1999) had already sold software as a service.', 'Today: serverless, containers, AI')])
parts += '\n  <h3>The six eras at a glance</h3>\n' + table(['Era', 'Years', 'Key idea', 'What the cloud kept from it'], [
    ['Mainframe', '1960s–1970s', 'one computer, many users, pay for time', 'sharing + metering'],
    ['Personal computer', '1980s–1990s', 'computer on every desk', 'cheap standard hardware'],
    ['Client-server / web', '1990s', 'shared apps over networks', 'broad network access'],
    ['Grid / utility', 'late 1990s–2000s', 'pool many computers', 'resource pooling'],
    ['Virtualization', '1999 →', 'many VMs on one server', 'IaaS, multitenancy'],
    ['Cloud', '2006 →', 'self-service, on-demand, pay-as-you-go', 'everything as a service']], minw=620)

clouds = vendor_tabs(
    '<p><b>AWS:</b> S3 (March 2006), EC2 (August 2006), RDS (2009), Lambda serverless (2014). India: Mumbai region (2016), Hyderabad (2022).</p>',
    '<p><b>Microsoft Azure:</b> announced as “Windows Azure” in 2008, generally available in 2010 (started as PaaS), renamed Microsoft Azure in 2014. India: Pune, Chennai and Mumbai regions from 2015.</p>',
    '<p><b>Google Cloud:</b> App Engine (2008, PaaS first), Cloud Storage (2010), BigQuery (2011–12), Compute Engine (2012–13). India: Mumbai (2017), Delhi (2021).</p>') + \
    cloud3([['First service', 'S3 storage (2006)', 'Windows Azure PaaS (2010)', 'App Engine PaaS (2008)'], ['Started as', 'IaaS', 'PaaS', 'PaaS'], ['Serverless', 'Lambda (2014)', 'Functions (2016)', 'Cloud Functions (2017 beta)'], ['Hypervisor', 'Nitro (KVM-based)', 'Hyper-V', 'KVM'], ['First India region', 'Mumbai (2016)', 'Pune / Chennai / Mumbai (2015)', 'Mumbai (2017)']])

prac = practical('Prove virtualization with your own eyes: check whether the machine you are using is a virtual machine. Works on Linux, WSL on Windows, or any cloud VM.', [
    ('1 · Ask the CPU', code('bash', 'terminal', "lscpu | grep -E 'CPU\\(s\\)|Model name|Hypervisor vendor|Virtualization type'", capsec(V, '== 1)', '== 2)')), 'Our cloud lab machine shows a Hypervisor vendor (KVM): it is a VM, a 2-CPU slice of a big Xeon server.'),
    ('2 · Look for the hypervisor flag', code('bash', 'terminal', 'grep -o -w hypervisor /proc/cpuinfo | head -1', capsec(V, '== 2)', '== 3)')), 'If this word appears, a hypervisor is under you. On a physical laptop it is usually absent.'),
    ('3 · Ask systemd', code('bash', 'terminal', 'systemd-detect-virt', capsec(V, '== 3)')), 'Our lab is a container inside a VM inside a physical server: three layers, each an era of this lesson. On a VM you may see kvm, microsoft or vmware; on bare metal, none.'),
    ('4 · Compare with your laptop', '<p>Run the same three commands on your own computer (WSL counts as a VM: you will see Microsoft / Hyper-V).</p>', 'Write down: physical or virtual?')],
    cleanup='Nothing to clean: these commands only read information.')
mist = mistakes([
    ['“Amazon invented cloud computing.”', 'AWS made it a mass-market business, so it is remembered as the start.', 'Say: the utility idea is from 1961, SaaS from 1999 (Salesforce), public IaaS cloud from 2006 (AWS).'],
    ['Thinking virtualization = cloud.', 'Every cloud uses virtualization, so they look the same.', 'Virtualization is the technology; cloud adds self-service, metering and internet access (animation above).'],
    ['Confusing grid and cloud.', 'Both pool many computers.', 'Grid: big shared jobs for experts; cloud: on-demand self-service for anyone (Lesson 3.4).'],
    ['Using old product names in exams.', 'Products get renamed (Windows Azure → Microsoft Azure, Azure AD → Microsoft Entra ID).', 'Check current names in the provider docs before exams.']])
SUMMARY = big_mindmap('Mind map of lesson 1.2: problem, eras, key enabler, providers, modern era, India.', 'Cloud history', [
    ('The problem', 'red', 'meter', ['computers are costly', 'most sit idle', 'every era fixed a part']),
    ('Eras', 'blue', 'chart', ['mainframe → PC', 'server room → grid', 'virtualization → cloud']),
    ('Key enabler', 'violet', 'gear', ['hypervisor + VMs', '+ self-service', '+ metering = cloud']),
    ('Providers', 'acc', 'cloud', ['AWS 2006 (IaaS)', 'Google 2008 (PaaS)', 'Azure 2010 (PaaS)']),
    ('Modern era', 'green', 'app', ['containers 2013–14', 'serverless 2014', 'AI services 2020s']),
    ('India', 'amber', 'globe', ['Azure 2015', 'AWS Mumbai 2016', 'GCP Mumbai 2017'])], h=380, caption='Lesson 1.2 on one page.')
cert = certbox([
    ['AWS CLF-C02', 'Domain 1 · Cloud Concepts', 'Why the cloud: trade capital expense for variable expense, stop guessing capacity; history itself is not asked.'],
    ['Azure AZ-900', 'Describe cloud concepts', 'Cloud computing and its benefits; current names (Microsoft Entra ID).'],
    ['Google Cloud Digital Leader', 'Digital transformation', 'Why organisations move from on-premises to cloud.'],
    ['C-DAC PGCP-BDA', 'Cloud Session 2 · Sessions 3–4', 'Cloud paradigms; virtualization, hypervisor.']],
    [('Which technology most directly made IaaS possible? (a) SQL (b) virtualization (c) HTML (d) email', '<b>(b) Virtualization</b>: one server can be sold as many isolated VMs.'),
     ('What did the cloud add on top of virtualization?', 'On-demand self-service, metering (pay per use) and access for anyone over the internet.'),
     ('Utility computing means…', 'Paying for computing like electricity: metered and on demand.')]) + '\n  <h3>Lesson 1.2 on one page</h3>\n' + SUMMARY
proj = miniproject('Mini project: is it physical or virtual?',
    'A tiny script that reports whether any Linux machine is physical, a VM or a container — useful on every cloud server you log into.',
    ['Create <code>whereami.sh</code> with the three commands from the hands-on.', 'Print one line: <code>physical</code>, <code>VM (KVM)</code> or <code>container in VM</code> using <code>if</code> checks (Shell scripting course).', 'Run it on your laptop, WSL and later on an AWS EC2 instance (AWS course 3.1).', 'Save the three outputs in a table: you have seen three eras of this lesson on real machines.'],
    'Lines like “container inside a KVM virtual machine”.', 'Linux commands, shell scripting, later AWS EC2.')


# ===== computing paradigms (C-DAC Session 2) =====
def par_pic(kind, x, y):
    o = ''
    if kind == 'central':
        o += box(x + 48, y, 44, 34, 'blue', rx=4) + t(x + 70, y + 21, 'one', 7, 'ink', bold=True)
        for k in range(4):
            tx = x + 6 + k * 34
            o += box(tx, y + 54, 26, 14, 'card', rx=2) + f'<line x1="{tx + 13}" y1="{y + 54}" x2="{x + 70}" y2="{y + 34}" style="stroke:var(--line)"/>'
    elif kind == 'parallel':
        o += box(x + 20, y, 100, 68, 'card', rx=6) + t(x + 70, y + 12, 'one machine, shared memory', 6.4, 'ink2')
        for k in range(8):
            o += box(x + 26 + (k % 4) * 23, y + 18 + (k // 4) * 24, 19, 19, 'green', rx=3) + t(x + 35.5 + (k % 4) * 23, y + 31 + (k // 4) * 24, 'C', 6.6, 'ink', bold=True)
    elif kind == 'distributed':
        pts = [(x + 14, y + 6), (x + 110, y + 6), (x + 14, y + 52), (x + 110, y + 52), (x + 62, y + 28)]
        for i, (a, b) in enumerate(pts):
            for (c, d) in pts[i + 1:]:
                o += f'<line x1="{a + 9}" y1="{b + 9}" x2="{c + 9}" y2="{d + 9}" style="stroke:var(--line);stroke-dasharray:3 2"/>'
        for a, b in pts:
            o += ic('laptop', a, b, 0.75, 'violet')
    elif kind == 'cluster':
        o += box(x + 10, y, 120, 68, 'card', rx=6) + t(x + 70, y + 12, 'same rack, fast LAN', 6.4, 'ink2')
        o += box(x + 56, y + 18, 28, 16, 'acc', rx=3) + t(x + 70, y + 29, 'master', 6, 'ink', bold=True)
        for k in range(5):
            o += box(x + 16 + k * 22, y + 44, 18, 18, 'blue', rx=3) + f'<line x1="{x + 25 + k * 22}" y1="{y + 44}" x2="{x + 70}" y2="{y + 34}" style="stroke:var(--line)"/>'
    elif kind == 'grid':
        for k, (lab, dx, dy) in enumerate([('Univ A', 0, 0), ('Lab B', 84, 0), ('Univ C', 0, 44), ('Lab D', 84, 44)]):
            o += box(x + 6 + dx, y + dy, 50, 24, 'violet', rx=4) + t(x + 31 + dx, y + 15 + dy, lab, 6.6, 'ink', bold=True)
        o += box(x + 48, y + 28, 44, 14, 'acc', rx=7) + t(x + 70, y + 38, 'middleware', 6, 'ink', bold=True)
    elif kind == 'cloud':
        o += box(x + 20, y, 100, 44, 'acc', rx=22) + ic('cloud', x + 60, y + 6, 0.9, 'acc') + t(x + 70, y + 38, 'provider pool', 6.6, 'ink', bold=True)
        for k, icn in enumerate(['user', 'phone', 'laptop', 'user']):
            o += ic(icn, x + 14 + k * 32, y + 50, 0.7, 'blue')
    return o
def paradigms():
    items = [('central', 'Centralized', '1 computer, many terminals', 'mainframe'),
             ('parallel', 'Parallel', 'many cores, 1 machine, 1 task', 'multicore, GPU'),
             ('distributed', 'Distributed', 'many computers, network, messages', 'web, email, DNS'),
             ('cluster', 'Cluster', 'same machines, one place, act as one', 'Hadoop, Spark, HPC'),
             ('grid', 'Grid', 'many organisations share for big jobs', 'scientific grids'),
             ('cloud', 'Cloud', 'on-demand, self-service, metered, anyone', 'AWS, Azure, GCP')]
    o = t(320, 16, 'Six computing paradigms', 11, 'ink', bold=True)
    for i, (k, n, d, e) in enumerate(items):
        col, row = i % 3, i // 3
        x = 14 + col * 208; y = 30 + row * 150
        o += box(x, y, 198, 140, 'acc' if k == 'cloud' else 'card', rx=10) + t(x + 12, y + 18, f'{i + 1}. {n}', 9.4, 'ink', anchor='start', bold=True)
        o += par_pic(k, x + 29, y + 28)
        o += t(x + 12, y + 114, d, 7.6, 'ink', anchor='start') + t(x + 12, y + 128, 'e.g. ' + e, 7.2, 'ink2', anchor='start')
    return o
PAR = bigfig('Six computing paradigms with pictures: centralized (one computer, many terminals), parallel (many cores in one machine), distributed (many networked computers), cluster (identical machines in one place acting as one), grid (computers from many organisations joined by middleware), cloud (provider pool used on demand by anyone).', paradigms(), h=338)
def job_frame(k):
    labels = [('1 CPU', 1, 'blue'), ('8 cores', 8, 'green'), ('cluster 20 nodes', 20, 'blue'), ('grid: 4 universities', 40, 'violet'), ('cloud: 100 VMs', 100, 'acc')]
    o = t(180, 12, 'Job: count words in 1 TB of text', 9, 'ink', bold=True)
    hrs = [100, 13, 5, 3, 1]
    for i, (lab, n, tn) in enumerate(labels[:k + 1]):
        y = 24 + i * 26
        w = max(6, hrs[i] * 2.0)
        o += t(96, y + 13, lab, 7.4, 'ink', anchor='end', bold=True) + box(102, y + 2, w, 16, 'amber' if i == k else tn, rx=3) + t(108 + w, y + 14, f'≈{hrs[i]} h', 7.4, 'ink', anchor='start', bold=True)
    return o
JOB = [('1 · One CPU (centralized)', 'One processor reads 1 TB alone: about 100 hours (illustrative).', 'Simple, but too slow for big data'),
       ('2 · Parallel', 'Split the work across 8 cores of one machine that share memory.', 'Faster, but limited by one machine’s size'),
       ('3 · Cluster', '20 identical machines in one rack act as one system (like Hadoop/Spark).', 'Your own cluster: fast, but you buy and run it'),
       ('4 · Grid', 'Spare computers of 4 universities join through grid middleware.', 'Big power, but shared, slower to organise, for experts'),
       ('5 · Cloud', 'Rent 100 VMs (or a managed Spark service) for one hour, then delete them.', 'Same distributed idea, on demand and pay per use')]
fr = [job_frame(k) + box(6, 158, 348, 62, 'blue', rx=8) + t(14, 174, h, 9, 'ink', anchor='start', bold=True) + t(14, 190, a, 7.4, 'ink', anchor='start') + t(14, 206, b, 7.2, 'ink2', anchor='start') for k, (h, a, b) in enumerate(JOB)]
JOBA = anim_one('How it works', 'One big job, five paradigms', 'The same task done the way each paradigm allows (times are illustrative, to compare ideas).', 'Paradigms', 'Animation: a 1 TB word count on one CPU (100 h), 8 cores (13 h), a 20-node cluster (5 h), a university grid (3 h) and 100 cloud VMs (1 h).', fr, ['One CPU.', 'Parallel.', 'Cluster.', 'Grid.', 'Cloud.'], delay=5500, hid='paradigm-job')
PAR_TABLE = table(['Paradigm', 'Coupling', 'Where', 'Who owns / uses', 'Example'], [
    ['Centralized', 'one machine', 'one room', 'one organisation', 'mainframe'],
    ['Parallel', 'very tight (shared memory)', 'inside one machine', 'one program', 'multicore CPU, GPU'],
    ['Distributed', 'loose (messages over network)', 'anywhere', 'many systems cooperating', 'the web, DNS, email'],
    ['Cluster', 'tight (fast LAN), same hardware', 'one data centre', 'one organisation', 'Hadoop, Spark, HPC clusters'],
    ['Grid', 'loose, different hardware', 'many organisations', 'research communities', 'scientific / volunteer grids'],
    ['Cloud', 'loose to tight, virtualized', 'provider regions', 'anyone, on demand, metered', 'AWS, Azure, Google Cloud']], minw=640)
PAR_HTML = ('  <p>Before “cloud” became the word, computer scientists already had names for ways of using many computers. C-DAC calls them <b>cloud paradigms</b>; exams and vivas often ask how cloud differs from <b>cluster</b> and <b>grid</b>. Here they are as pictures:</p>\n' + PAR
            + '\n  <p>Watch one big job go faster as we move through the paradigms, and notice what changes with the cloud: not the idea (many computers), but <b>who owns them and how you get them</b>.</p>\n' + JOBA
            + '\n  <h3>Side by side</h3>\n' + PAR_TABLE
            + '\n  <p><b>Two more enablers:</b> <b>web services and APIs</b> (SOA, 2000s) let programs request resources over HTTP — every cloud action today is an API call; and <b>containers</b> (Docker 2013, Kubernetes 2014) package apps so they run the same on any cloud.</p>')

assemble_v2(HERE, story_h2='Is the cloud just mainframes again?', hook_html=hk,
    narration='Riya’s uncle ran a bank mainframe in the 1980s. He says the cloud is nothing new. Riya wants to know what really changed between his mainframe and today’s cloud.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='History and evolution of cloud computing',
    formal='The <b>evolution of cloud computing</b> runs from 1960s mainframe time-sharing and the idea of <b>utility computing</b>, through personal computers, client-server computing and the internet, grid computing and hardware <b>virtualization</b>, to on-demand public clouds (AWS 2006, Google App Engine 2008, Microsoft Azure 2010) and today’s serverless, container and AI services.',
    simple='First people shared one big computer, then everyone owned one, then companies filled rooms with half-idle servers, then split servers into VMs — and finally providers started renting those VMs to anyone, by the hour.',
    interview=['“Cloud computing evolved from 1960s mainframe time-sharing and the idea of utility computing, through client-server computing, the internet, grid computing and virtualization.”', '“Virtualization was the key enabler: one physical server can run many isolated VMs. Providers added self-service, metering and internet access, and the public cloud began with AWS S3 and EC2 in 2006, followed by Google App Engine in 2008 and Azure in 2010.”', '“Since then it has moved to containers, serverless with AWS Lambda in 2014, and today AI services.”'],
    terms_rows=[('Mainframe', 'Big central computer shared by many users.'), ('Time-sharing', 'Many users take turns on one computer.'), ('Utility computing', 'Computing paid like electricity.'), ('Client-server', 'Clients ask, servers answer over a network.'), ('Grid computing', 'Many computers pooled for big jobs.'), ('Hypervisor', 'Software that runs VMs on hardware.'), ('Virtual machine', 'A software computer, a slice of a server.'), ('Serverless', 'Run code without managing servers.')],
    exam='Remember the enabling technologies (internet, virtualization, cheap hardware, web APIs) and the milestones: Salesforce 1999 (SaaS), AWS S3/EC2 2006 (IaaS), Google App Engine 2008 (PaaS), Azure 2010, Lambda 2014 (serverless).',
    picture_h2='Six eras in one picture', picture_html=picture,
    how_h2='Watch the setup change, then watch a server become a cloud', how_intro='Two animations. First, one bank doing the same work across fifty years. Second, the exact steps that turned virtualization into the cloud.', how_anim=ERA_ANIM + VIRT, how_after=how_after,
    parts_h2='The six eras, one by one', parts_html=parts, lv='',
    myth_rows=[('Cloud is a 2006 invention.', 'The idea is from 1961; 2006 is when it became a business.', 'Era cards 1 and 6.'), ('Virtualization and cloud are the same.', 'Cloud = virtualization + self-service + metering + internet.', 'Animation 2.'), ('The cloud stopped growing.', '436 AWS services in the SDK; still growing.', 'Growth chart.')],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html='', project_html='',
    extra_secs=[('paradigms', 'Computing paradigms', 'Centralized, parallel, distributed, cluster, grid and cloud', PAR_HTML)],
    can_now=['Tell the history of cloud as six eras, each fixing the previous problem.', 'Explain why virtualization was the key enabler and what the cloud added on top.', 'Compare centralized, parallel, distributed, cluster, grid and cloud computing.', 'Name the launch years of AWS, Google Cloud and Azure and their first Indian regions.', 'Check whether a Linux machine is physical, a VM or a container.'],
    next_html='<a href="../03-characteristics-and-advantages-of-cloud/">1.3 Advantages of cloud computing: why companies pay for it</a>.',
    pre='<b>Before you start:</b> <a href="../01-what-is-cloud-computing/">1.1 What is cloud computing?</a>')
