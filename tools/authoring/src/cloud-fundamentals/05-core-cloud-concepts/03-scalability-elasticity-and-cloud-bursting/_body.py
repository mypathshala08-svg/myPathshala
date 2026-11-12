import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def sc(a, b=None): return capsec('l53_scale.txt', a, b)
def sim(a, b=None): return capsec('l53_sim.txt', a, b)
def aws(a, b=None): return capsec('l53_aws.txt', a, b)
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)

hk = hook('At 8 p.m. on Diwali TiffinGo needs 22 servers. At 3 a.m. it needs 2. How many should it pay for?',
    'With the cloud: <b>only as many as each hour needs</b>. Our simulation of a Diwali day shows <b>144 server-hours</b> with elastic scaling against <b>528</b> for a fleet sized for the peak — a <b>73% saving</b> at real Mumbai prices. And scaling out works: on our 2-core lab machine, adding a second server process took the same API from <b>37.8</b> to <b>99.5 requests/s</b>. This lesson separates <b>scalability</b>, <b>elasticity</b> and <b>cloud bursting</b>, and shows every kind of auto scaling.',
    ['Scale up vs scale out — and why the cloud prefers out.', 'Elasticity: target tracking, step, scheduled and predictive scaling, step by step.', 'Cloud bursting from a private data centre, and serverless scale-to-zero.'])

def story_scene():
    o = t(180, 12, 'One day of TiffinGo traffic (requests per second)', 9, 'ink', bold=True)
    tr = [40,30,25,20,20,30,80,150,220,180,160,200,320,300,180,150,200,320,600,900,1100,800,400,150]
    pts = ' '.join(f'{16 + i * 14},{120 - v * 0.085}' for i, v in enumerate(tr))
    o += f'<polyline points="{pts}" style="fill:none;stroke:#E0A100;stroke-width:2.4"/>'
    o += f'<path d="M16,26 L340,26" style="stroke:#D64545;stroke-width:1.6;stroke-dasharray:5 3"/>' + t(338, 22, 'fixed fleet sized for 8 p.m.', 6.8, 'red', anchor='end', bold=True)
    o += t(16, 134, '00:00', 6.6, 'ink2', anchor='start') + t(180, 134, '12:00', 6.6, 'ink2') + t(340, 134, '23:00', 6.6, 'ink2', anchor='end')
    o += t(280, 70, 'Diwali peak', 7, 'ink', bold=True)
    return o
scene_svg = scene('Line chart of one day of TiffinGo traffic: low at night, a lunch bump and a large evening peak at 8 p.m.; a dashed line shows a fixed fleet sized for the peak all day.', story_scene(), 'Pay for the curve, <tspan font-weight="700" class="s-acc">not for the peak</tspan>.', h=154)
dialogue = '''R> Sir, last Diwali we bought servers for the 8 p.m. peak. For the other 23 hours they sat almost idle.
A> That is scalability without elasticity: you could handle the peak, but you paid for it all day. In the cloud the fleet can follow the curve.
K> How does it know when to grow?
A> You give it a rule — “keep average CPU at 50%” — and Auto Scaling adds or removes servers. You can also schedule known peaks, or let it predict them from history.
R> And the old office data centre?
A> It can “burst” into the cloud when it runs out of room. Let’s see all of it, with numbers.'''

def updownfig():
    o = t(320, 16, 'Two ways to grow: scale up (vertical) or scale out (horizontal)', 11, 'ink', bold=True)
    o += box(20, 32, 290, 220, 'card', rx=10) + t(165, 50, 'Scale UP — a bigger machine', 9, 'ink', bold=True)
    for i, (n, w, h) in enumerate([('t3.medium', 50, 40), ('m7i.xlarge', 70, 70), ('m7i.4xlarge', 96, 110)]):
        x = 40 + i * 92
        o += box(x, 210 - h, w, h, 'blue', rx=5) + t(x + w / 2, 226, n, 7, 'ink', bold=True)
        if i < 2:
            o += arrow(x + w + 4, 180, x + 88, 180)
    o += t(165, 244, 'simple · one box · has a ceiling · usually a restart', 7.2, 'ink2')
    o += box(330, 32, 290, 220, 'card', rx=10) + t(475, 50, 'Scale OUT — more machines', 9, 'ink', bold=True)
    o += box(400, 62, 150, 26, 'violet', rx=5) + t(475, 79, 'load balancer', 8, 'ink', bold=True)
    for i in range(6):
        x = 346 + i * 44
        o += box(x, 120, 38, 50, 'blue' if i < 4 else 'green', rx=4) + t(x + 19, 150, 'VM', 7, 'ink', bold=True)
        o += f'<path d="M475,88 L{x + 19},120" style="stroke:#999;stroke-width:1"/>'
    o += t(475, 190, '+2 added for the peak', 7.4, 'green', bold=True)
    o += t(475, 244, 'no ceiling · survives one failure · needs a stateless app', 7.2, 'ink2')
    o += t(320, 270, 'Cloud-native apps scale out; databases often scale up first, then out with read replicas or sharding.', 7.6, 'ink2')
    return o
UPDOWN = bigfig('Left: scale up from t3.medium to m7i.xlarge to m7i.4xlarge — simple but with a ceiling. Right: scale out behind a load balancer from four to six VMs — no ceiling, survives failures, needs a stateless app.', updownfig(), h=280)

def elasfig():
    o = t(320, 16, 'Scalable ≠ elastic: capacity vs demand over one day', 11, 'ink', bold=True)
    tr = [40,30,25,20,20,30,80,150,220,180,160,200,320,300,180,150,200,320,600,900,1100,800,400,150]
    def y(v): return 222 - v * 0.15
    pts = ' '.join(f'{40 + i * 24},{y(v)}' for i, v in enumerate(tr))
    o += f'<polyline points="{pts}" style="fill:none;stroke:#E0A100;stroke-width:2.6"/>'
    el = [max(2, -(-v // 50)) * 50 for v in tr]
    st = ''
    for i, v in enumerate(el):
        st += f'{40 + i * 24},{y(v)} {64 + i * 24},{y(v)} '
    o += f'<polyline points="{st}" style="fill:none;stroke:#2E8B57;stroke-width:2"/>'
    o += f'<path d="M40,{y(1100)} L616,{y(1100)}" style="stroke:#D64545;stroke-width:2;stroke-dasharray:6 3"/>'
    o += box(40, 232, 12, 6, 'amber', rx=1) + t(56, 238, 'demand', 7.4, 'ink', anchor='start') + box(130, 232, 12, 6, 'green', rx=1) + t(146, 238, 'elastic capacity (follows demand)', 7.4, 'ink', anchor='start') + box(330, 232, 12, 6, 'red', rx=1) + t(346, 238, 'fixed capacity (scalable to the peak, but paid all day)', 7.4, 'ink', anchor='start')
    o += t(320, 262, 'Simulation: elastic 144 server-hours vs fixed 528 per day → 73% less at the same On-Demand price.', 7.8, 'ink', bold=True)
    return o
ELAS = bigfig('Line chart: demand over 24 hours with an evening peak; a green step line of elastic capacity following demand; a red dashed line of fixed capacity at the peak all day. Simulation result: 144 vs 528 server-hours, 73% less.', elasfig(), h=272)

picture = ('  <p><b>Scalability</b> is the <i>ability</i> to handle more load by adding resources. <b>Elasticity</b> is doing it <i>automatically, both up and down</i>, so capacity follows demand. Start with the two directions of growth:</p>\n' + UPDOWN +
           '\n  <p>Now compare a fleet that can handle the peak (scalable) with one that follows the curve (elastic):</p>\n' + ELAS)

# how: ALB listener -> target group -> ASG with CloudWatch alarm
RN = {'u': (4, 54, 54, 50, 'phone', 'Customers', 'Diwali rush'), 'lst': (66, 54, 60, 50, 'lb', 'ALB listener', 'HTTPS :443'), 'tg': (136, 4, 64, 46, 'app', 'Target group', 'healthy VMs'),
      'cw': (136, 104, 64, 46, 'chart', 'CloudWatch', 'avg CPU'), 'asg': (212, 54, 64, 50, 'meter', 'Auto Scaling', 'target 50%'), 'new': (288, 4, 68, 46, 'server', 'New VMs', 'from template'), 'hc': (288, 104, 68, 46, 'shield', 'Health check', 'then traffic')}
RS = [dict(on=['u', 'lst', 'tg'], hot='lst', move=(58, 79, 66, 79, ''), head='Step 1 · The listener receives traffic', text='The Application Load Balancer’s listener (HTTPS :443) applies its rules and', text2='forwards each request to a healthy instance in the target group.', svc='Listener → rule → target group: the “auto-scaling listener” chain'),
      dict(on=['u', 'lst', 'tg', 'cw'], hot='cw', move=(168, 50, 168, 104, 'metrics'), head='Step 2 · Metrics show the load', text='Every instance reports CPU; CloudWatch computes the group average every minute.', text2='At 6 p.m. it climbs past 50% and keeps rising.', svc='Also possible: requests per target, queue length, custom metrics'),
      dict(on=['u', 'lst', 'tg', 'cw', 'asg'], hot='asg', move=(200, 127, 222, 104, 'alarm'), head='Step 3 · Target tracking computes the capacity', text='The policy “keep average CPU at 50%” calculates how many instances are needed', text2='and raises the desired capacity — e.g. from 6 to 12.', svc='Target tracking creates and manages the CloudWatch alarms for you'),
      dict(on=['u', 'lst', 'tg', 'cw', 'asg', 'new'], hot='new', move=(276, 70, 296, 40, 'launch'), head='Step 4 · New instances launch', text='Auto Scaling launches instances from the launch template, spread evenly across', text2='the group’s AZs. Boot + app start takes a minute or two (warm-up).', svc='Golden AMIs (Lesson 4.4) make this fast'),
      dict(on=list(RN), hot='hc', move=(322, 50, 322, 104, 'check'), head='Step 5 · Health check, then traffic', text='The load balancer sends traffic to a new instance only after it passes health', text2='checks — users never hit a half-started server.', svc='Unhealthy instances are terminated and replaced automatically'),
      dict(on=list(RN), hot='asg', move=(276, 90, 296, 120, 'scale in'), head='Step 6 · Scale in after the peak', text='After midnight CPU falls; the policy lowers the desired capacity. Connections are', text2='drained before instances terminate. Billing stops for removed instances.', svc='Elastic both ways: that is what saves the 73%')]
FLOW = flow_anim('Diwali evening: how Auto Scaling grows and shrinks the fleet', 'From the load balancer listener to new instances and back — six steps.', 'Auto scaling', 'Animation: ALB listener forwards to target group; CloudWatch average CPU rises; target tracking raises desired capacity; new instances launch from the template across AZs; they receive traffic after health checks; after the peak the group scales in.', RN, RS, hid='asflow')

# ------------------------------------------------------------------ types
def mapfig():
    o = t(320, 16, 'Seven ways capacity grows (and shrinks)', 11, 'ink', bold=True)
    items = [('1', 'Vertical scaling', 'bigger machine', 'blue'), ('2', 'Horizontal scaling', 'more machines', 'blue'), ('3', 'Elasticity', 'automatic, both ways', 'green'), ('4', 'Dynamic auto scaling', 'target tracking, step', 'green'),
             ('5', 'Scheduled + predictive', 'known or learned peaks', 'amber'), ('6', 'Cloud bursting', 'private → public overflow', 'violet'), ('7', 'Serverless scaling', 'per request, to zero', 'red')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 14 + (i % 4) * 156; y = 32 + (i // 4) * 78
        o += box(x, y, 148, 66, tn, rx=8) + pin(x + 14, y + 16, n) + t(x + 28, y + 20, a, 8, 'ink', anchor='start', bold=True) + t(x + 8, y + 46, b, 7, 'ink2', anchor='start')
    o += t(320, 208, '1–2 are directions (scalability) · 3–5 make it automatic (elasticity) · 6–7 are special cases.', 7.6, 'ink2')
    return o
MAP = bigfig('Map of seven scaling ideas: 1 vertical, 2 horizontal, 3 elasticity, 4 dynamic auto scaling, 5 scheduled and predictive, 6 cloud bursting, 7 serverless scaling.', mapfig(), h=220)

def a_vert(k):
    o = t(180, 12, ['DB on m7i.large: CPU 95%', 'Stop, change type, start', 'm7i.2xlarge: CPU 40%'][k], 9, 'ink', bold=True)
    w = [60, 60, 120][k]
    o += box(180 - w / 2, 120 - w, w, w, 'red' if k == 0 else ('card' if k == 1 else 'green'), rx=6) + t(180, 120 - w / 2, ['2 vCPU · 8 GB', 'stopped', '8 vCPU · 32 GB'][k], 7.6, 'ink', bold=True)
    o += t(180, 140, ['queries queue up', 'a few minutes of downtime (or fail over to a standby first)', 'same app, no code change — but a ceiling exists'][k], 7.2, 'red' if k == 1 else 'ink', bold=True)
    return o
A_VERT = cap([a_vert(k) for k in range(3)], [('One box is too small', 'TiffinGo’s database instance is at 95% CPU every evening.', 'The app cannot easily run on two databases.'), ('Resize', 'Stop the instance, change the instance type, start it (RDS can do it during', 'a maintenance window or by failing over to a resized standby).'), ('Bigger box, same design', 'Four times the CPU and memory, no code change. But the biggest instance', 'is the limit, and one box is still one point of failure.')],
    'Vertical scaling in action', 'Grow by moving to a bigger machine.', 'Scale up', 'Animation: database instance at 95% CPU; stopped and resized; running on a larger instance at 40% CPU.', 's1anim')
T1 = vtype(1, 'Vertical scaling (scale up / down)', 'blue',
    '<b>Vertical scaling</b> increases (or decreases) the capacity of a single resource — more vCPUs, memory, faster storage or network — by moving it to a larger (or smaller) size, without changing the number of instances.',
    'Replacing your auto-rickshaw with a mini-truck when deliveries grow: one bigger vehicle, same driver and routes — but there is a biggest truck, and if it breaks down, nothing moves.',
    'TiffinGo’s PostgreSQL database hits 95% CPU at dinner time. The team changes it from db.m7i.large to db.m7i.2xlarge during a maintenance window; CPU drops to 40%, no code changes.',
    'Change instance type in EC2/RDS, Azure VM resize, Compute Engine machine type change; Aurora Serverless v2 and Azure SQL serverless resize capacity automatically within limits.',
    '', A_VERT,
    'the software cannot be split across machines (many databases, legacy apps), or a quick fix is needed.',
    'you hit the largest size, need high availability, or need to scale many times a day — prefer scaling out.',
    plain='Making one computer stronger — more processors or memory — instead of adding more computers.',
    how=[('Pick a new size', 'Choose a larger instance type in the same family (or a different family).'), ('Stop or fail over', 'Most VMs must stop to change type; databases often fail over to a resized standby to minimise downtime.'), ('Change the type', 'The hypervisor places the VM on a host with enough capacity.'), ('Start', 'The same disk and configuration come back with more CPU/RAM.'), ('Check limits', 'Network and disk throughput also grow with instance size.')],
    words=[('instance type', 'a VM size, e.g. m7i.large = 2 vCPU, 8 GB'), ('ceiling', 'the biggest size available'), ('maintenance window', 'an agreed time for changes that may interrupt service')],
    diff=table(['', 'Vertical (up)', 'Horizontal (out)'], [['Adds', 'size of one machine', 'more machines'], ['Limit', 'largest instance', 'practically none'], ['Downtime to change', 'usually yes (brief)', 'no'], ['Needs app changes', 'no', 'often (stateless design)'], ['Failure tolerance', 'single point of failure', 'survives losing one']], minw=520),
    where=['Relational databases', 'Legacy and licensed software', 'Quick relief before re-architecting'],
    realworld='Amazon RDS lets you change a database’s instance class either immediately or during the next maintenance window; with Multi-AZ, the change is applied to the standby first and then failed over, which keeps the interruption short.',
    pro='Bigger is not always proportionally faster: memory bandwidth, licensing per core and single-threaded parts of the app cap the gain. Measure before paying for 4× the cores.')

def a_horiz(k):
    o = t(180, 12, ['1 server process: 37.8 req/s', 'Add a second process', '2 processes: 99.5 req/s (2.6×)'][k], 9, 'ink', bold=True)
    o += box(10, 50, 80, 50, 'blue', rx=6) + t(50, 80, 'load', 8, 'ink', bold=True)
    n = 1 if k == 0 else 2
    for i in range(n):
        o += box(170, 30 + i * 56, 110, 46, 'green' if (k >= 1 and i == 1) else 'blue', rx=6) + t(225, 52 + i * 56, f'server :{8101 + i}', 7.6, 'ink', bold=True) + t(225, 66 + i * 56, 'menu API', 6.8, 'ink2')
        o += packet(90, 75, 170, 53 + i * 56, '')
    o += t(180, 150, ['real measurement on a 2-core machine', 'requests now spread round-robin', 'more than 2× — one process was also queuing requests'][k], 7.2, 'ink', bold=True)
    return o
A_HORIZ = cap([a_horiz(k) for k in range(3)], [('One instance', 'The menu API runs as one server process: 37.8 requests/s at 8 parallel', 'clients (real measurement on our 2-core lab machine).'), ('Add another', 'A second identical process starts; requests are spread round-robin —', 'exactly what a load balancer does across VMs.'), ('Throughput grows', '99.5 requests/s: 2.6× (more than 2× because a single-threaded server', 'was also queuing requests). Same code, more copies.')],
    'Horizontal scaling in action', 'Grow by adding more copies — real numbers.', 'Scale out', 'Animation: one server process at 37.8 requests per second; a second process added; throughput rises to 99.5 requests per second.', 's2anim')
T2 = vtype(2, 'Horizontal scaling (scale out / in)', 'blue',
    '<b>Horizontal scaling</b> increases (or decreases) capacity by adding (or removing) instances of a resource — servers, containers or database nodes — and distributing work among them, typically behind a load balancer.',
    'Opening more billing counters in a supermarket at rush hour instead of hiring one super-fast cashier: more queues move at once, and if one counter closes, the others continue.',
    'TiffinGo’s menu API is stateless, so it runs as many identical instances behind a load balancer. In our lab, two server processes served 99.5 requests/s versus 37.8 for one.',
    'Load balancers (ALB/NLB, Azure Load Balancer/Application Gateway, Google Cloud Load Balancing) with Auto Scaling groups, VM Scale Sets, managed instance groups; Kubernetes ReplicaSets; database read replicas and sharding.',
    '', A_HORIZ,
    'web and API tiers, workers, anything stateless — the default way to scale in the cloud.',
    'the app stores session or files locally — move state to a database, cache or shared storage first.',
    plain='Adding more computers that share the work, instead of making one computer bigger.',
    how=[('Make the app stateless', 'Sessions in a cache/database, files in object storage, so any instance can serve any request.'), ('Put a load balancer in front', 'It spreads requests across healthy instances.'), ('Add instances', 'Launch more copies from the same image/template.'), ('Register', 'New instances join the target group after passing health checks.'), ('Remove', 'Drain connections and terminate instances when load falls.')],
    words=[('stateless', 'keeps no user data between requests on the server itself'), ('load balancer', 'spreads requests across servers'), ('target group', 'the set of instances a load balancer sends traffic to'), ('read replica', 'a copy of a database that serves reads')],
    diff=table(['', 'Horizontal', 'Vertical'], [['Typical tier', 'web, API, workers', 'databases, legacy'], ['Automation', 'easy (Auto Scaling)', 'harder'], ['Cost granularity', 'add one small instance at a time', 'jump to the next size']], minw=480),
    where=['Web and mobile back ends', 'Microservices on Kubernetes', 'Batch and stream processing', 'Read-heavy databases (replicas)'],
    realworld='Large consumer apps scale out to thousands of instances during events — for example, streaming and e-commerce companies publicly describe adding capacity across many instances for big launches and sales rather than buying ever-bigger single servers.',
    pro='Scaling out moves the bottleneck: once the web tier scales, the shared database or a downstream API becomes the limit. Load-test the whole chain, not just the tier you scale.')

def a_elas(k):
    o = t(180, 12, ['Demand rises → capacity rises', 'Peak → capacity at its maximum', 'Demand falls → capacity falls'][k], 9, 'ink', bold=True)
    tr = [20, 30, 60, 100, 70, 30]
    for i, v in enumerate(tr):
        show = i <= [2, 3, 5][k]
        if show:
            o += box(20 + i * 54, 130 - v, 40, v, 'amber', rx=2) + box(20 + i * 54, 130 - v - 8, 40, 6, 'green', rx=1)
    o += t(180, 148, ['servers added a few minutes after load grows', 'enough to keep CPU near the target', 'servers removed — billing stops'][k], 7.4, 'ink', bold=True)
    return o
A_ELAS = cap([a_elas(k) for k in range(3)], [('Up', 'As traffic grows, capacity (green) is added automatically just above', 'demand (orange).'), ('Peak', 'At the peak the fleet is at its largest — only for those hours.', 'Scalability made automatic.'), ('Down', 'As traffic falls, capacity is removed. This half is what on-premises', 'cannot do — and where most of the saving comes from.')],
    'Elasticity in action', 'Capacity that follows demand both ways.', 'Elasticity', 'Animation: demand bars rise, capacity bars rise just above; at peak capacity is highest; as demand falls capacity falls.', 's3anim')
T3 = vtype(3, 'Elasticity', 'green',
    '<b>Elasticity</b> (NIST: rapid elasticity) is the ability to provision and release resources automatically and quickly — scaling outward and inward with demand — so that available capacity closely matches the current workload and, to the consumer, appears unlimited.',
    'A rubber band around a bundle of papers: it stretches when you add papers and shrinks back when you remove them, always fitting the bundle.',
    'Our Diwali simulation: an elastic fleet uses 144 server-hours a day against 528 for a fleet sized for the 8 p.m. peak — 73% less at the same hourly price.',
    'EC2 Auto Scaling, Application Auto Scaling (ECS, DynamoDB, Aurora replicas), Lambda; Azure VM Scale Sets and autoscale; Google managed instance groups and autoscaler; Kubernetes HPA and Cluster Autoscaler/Karpenter.',
    '', A_ELAS,
    'demand varies by hour, day or season — almost every customer-facing app.',
    'capacity cannot start fast enough for sudden spikes (slow boot, cold caches) — keep a buffer or pre-scale.',
    plain='The cloud automatically adds computers when more people use your app and removes them when fewer people use it — so you pay roughly for what you use.',
    how=[('Measure demand', 'CPU, requests per target, queue depth, latency.'), ('Compare with a goal', 'A target or thresholds decide whether to add or remove.'), ('Provision quickly', 'New capacity comes from images/templates in minutes or seconds.'), ('Release quickly', 'Excess capacity is removed and stops being billed.'), ('Repeat continuously', 'The loop runs every minute.')],
    words=[('rapid elasticity', 'NIST’s name for this characteristic'), ('provision', 'create and prepare a resource'), ('scale in', 'remove capacity')],
    diff=table(['', 'Elasticity', 'Scalability'], [['Meaning', 'automatic, both directions, short term', 'ability to grow to handle more load'], ['Time scale', 'minutes–hours', 'months–years (capacity planning)'], ['Example', 'Auto Scaling for Diwali evening', 'architecture that can reach 10× users'], ['Can exist without the other?', 'needs scalability', 'yes (on-prem can scale, not elastically)']], minw=520),
    where=['Web and API tiers', 'Seasonal retail, ticketing, exam results', 'Batch processing', 'Event-driven systems'],
    realworld='Indian ticketing and result-announcement sites famously struggle on peak days; cloud elasticity lets such services add capacity for the event hours and release it afterwards instead of owning peak capacity all year.',
    pro='Elasticity has a speed limit: instance launch + app warm-up. If your spike rises faster than ~2–3 minutes, combine target tracking with scheduled or predictive scaling, or keep warm pools of pre-initialised instances.')

def a_dyn(k):
    o = t(180, 12, ['Target tracking: CPU 50%', 'Step scaling: thresholds', 'Cooldown / warm-up'][k], 9, 'ink', bold=True)
    o += f'<path d="M20,120 L340,120" style="stroke:#999"/>'
    pts = '20,110 60,100 100,80 140,50 180,40 220,60 260,90 300,100 340,108'
    o += f'<polyline points="{pts}" style="fill:none;stroke:#E0A100;stroke-width:2.2"/>'
    if k == 0:
        o += f'<path d="M20,75 L340,75" style="stroke:#2E8B57;stroke-width:1.6;stroke-dasharray:5 3"/>' + t(338, 70, 'target 50%', 7, 'green', anchor='end', bold=True)
        o += t(180, 145, 'the policy adds/removes just enough to stay near 50%', 7.2, 'ink', bold=True)
    if k == 1:
        for v, lab in [(60, '> 70%: +2'), (40, '> 85%: +4'), (100, '< 30%: −1')]:
            o += f'<path d="M20,{v} L340,{v}" style="stroke:#D64545;stroke-width:1.2;stroke-dasharray:3 3"/>' + t(338, v - 3, lab, 6.8, 'red', anchor='end', bold=True)
        o += t(180, 145, 'you define each step yourself', 7.2, 'ink', bold=True)
    if k == 2:
        o += box(140, 30, 80, 90, 'card', rx=3) + t(180, 70, 'warm-up', 7.6, 'ink', bold=True) + t(180, 84, '~2 min', 7, 'ink2') + t(180, 145, 'new instances are not counted until warmed up → no over-scaling', 7.2, 'ink', bold=True)
    return o
A_DYN = cap([a_dyn(k) for k in range(3)], [('Target tracking', 'You choose a metric and a target (average CPU 50%); the service computes', 'the capacity and manages the alarms. The recommended default.'), ('Step scaling', 'You define thresholds and how many instances to add or remove at each', '(above 70% add 2; above 85% add 4; below 30% remove 1).'), ('Warm-up', 'Newly launched instances are excluded from the average until warmed up,', 'so the policy does not keep adding servers while they boot.')],
    'Dynamic scaling policies', 'Reacting to metrics in real time.', 'Dynamic scaling', 'Animation: a load curve with a target tracking line at 50%; step thresholds at 70%, 85% and 30%; an instance warm-up window.', 's4anim')
T4 = vtype(4, 'Dynamic auto scaling (target tracking and step)', 'green',
    '<b>Dynamic scaling</b> adjusts capacity in response to live metrics: <b>target tracking</b> keeps a metric (e.g. average CPU or requests per target) at a chosen value, while <b>step/simple scaling</b> adds or removes fixed amounts when CloudWatch alarms cross defined thresholds.',
    'A cruise control in a car: you set 60 km/h and the car accelerates up hills and eases off downhill by itself (target tracking). Step scaling is like a rule: “if speed drops below 50, press harder; below 40, press much harder”.',
    'TiffinGo’s Auto Scaling group uses target tracking on average CPU = 50%, min 2, max 20, across two AZs. Our emulator lab created the group and the cpu50 policy and scaled to 6 instances.',
    'EC2 Auto Scaling target tracking/step/simple policies; Application Auto Scaling for ECS, DynamoDB, Aurora; Azure autoscale rules; Google autoscaler (CPU, load-balancing utilisation, custom metrics); Kubernetes Horizontal Pod Autoscaler.',
    '', A_DYN,
    'load is unpredictable or changes gradually.',
    'the metric does not reflect load (e.g. CPU for an I/O-bound app), or the spike is faster than instance start-up.',
    plain='The cloud watches a number — like how busy the servers are — and adds or removes servers automatically to keep that number at a level you chose.',
    how=[('Choose the metric', 'CPU, ALB requests per target, queue backlog per instance, or a custom metric.'), ('Set the target or steps', 'Target tracking: one value. Step: thresholds and adjustments.'), ('Alarms watch', 'CloudWatch evaluates the metric every minute.'), ('Change desired capacity', 'The group launches or terminates instances within min/max.'), ('Warm-up and cooldown', 'New instances are excluded until ready; scale-in is deliberately slower than scale-out.')],
    words=[('desired capacity', 'how many instances the group should have now'), ('min / max', 'limits the group never goes beyond'), ('CloudWatch alarm', 'a rule that fires when a metric crosses a threshold'), ('warm-up', 'time before a new instance’s metrics count')],
    diff=table(['', 'Target tracking', 'Step scaling', 'Simple scaling'], [['You define', 'target value', 'thresholds + steps', 'one threshold + one action'], ['Alarms', 'created for you', 'you create', 'you create'], ['Recommendation', 'default choice', 'when you need custom steps', 'legacy']], minw=520),
    where=['Web/API Auto Scaling groups', 'ECS services and Kubernetes deployments', 'DynamoDB provisioned capacity'],
    realworld='AWS recommends target tracking for most Auto Scaling groups because it calculates the required capacity and manages its own alarms, avoiding the tuning errors common with hand-written step policies.',
    pro='For web tiers, “ALB request count per target” usually tracks load better than CPU: it scales before CPU saturates and is independent of instance size.')

def a_sched(k):
    o = t(180, 12, ['Scheduled: known event', 'Predictive: learned pattern', 'Combined with dynamic'][k], 9, 'ink', bold=True)
    hrs = [10, 8, 8, 10, 30, 40, 35, 60, 90, 50]
    for i, v in enumerate(hrs):
        o += box(20 + i * 32, 120 - v, 24, v, 'amber', rx=2)
    if k == 0:
        o += box(250, 20, 100, 40, 'violet', rx=5) + t(300, 38, 'Diwali 6 p.m.:', 7, 'ink', bold=True) + t(300, 52, 'min = 10', 7, 'ink', bold=True) + t(180, 145, 'capacity in place before the peak starts', 7.2, 'ink', bold=True)
    if k == 1:
        for i, v in enumerate(hrs):
            o += f'<rect x="{20 + i * 32}" y="{112 - v}" width="24" height="6" style="fill:#2E8B57"/>'
        o += t(180, 145, 'ML forecast from 14 days of history launches ahead of daily peaks', 7.2, 'ink', bold=True)
    if k == 2:
        o += t(180, 145, 'predictive/scheduled set the floor; target tracking handles surprises', 7.2, 'green', bold=True)
    return o
A_SCHED = cap([a_sched(k) for k in range(3)], [('Scheduled scaling', 'For known events — Diwali evening, exam results at 10 a.m. — schedule a', 'higher minimum just before, and lower it after.'), ('Predictive scaling', 'The service learns daily/weekly patterns from history and launches capacity', 'ahead of the forecast peak.'), ('Use with dynamic', 'Scheduled or predictive capacity sets the floor; target tracking still reacts', 'to anything unexpected.')],
    'Scheduled and predictive scaling', 'Scaling before the load arrives.', 'Scheduled/predictive', 'Animation: a scheduled action raises minimum before Diwali evening; predictive scaling forecasts daily peaks; both combined with target tracking.', 's5anim')
T5 = vtype(5, 'Scheduled and predictive scaling', 'amber',
    '<b>Scheduled scaling</b> changes capacity at specified times for known demand patterns; <b>predictive scaling</b> uses machine learning on historical metrics to forecast demand and provision capacity in advance of expected peaks.',
    'A restaurant that calls extra staff every Saturday evening (scheduled) — and a manager who studies the last month’s footfall to know that Tuesday lunch will be busy too (predictive).',
    'TiffinGo knows the Diwali dinner rush starts at 6 p.m.: a scheduled action sets min = 10 at 5:45 p.m. and back to 2 at midnight. Predictive scaling handles the ordinary daily lunch and dinner peaks.',
    'EC2 Auto Scaling scheduled actions and predictive scaling policies; Azure autoscale schedules and predictive autoscale for VM Scale Sets; Google managed instance group schedules and predictive autoscaling.',
    '', A_SCHED,
    'peaks are known in advance or repeat daily/weekly, and instances take minutes to become ready.',
    'demand is truly random — then only dynamic scaling helps; predictive needs enough history.',
    plain='Adding servers before a busy time you already know about (or that the system has learned from past days), so customers never wait for servers to start.',
    how=[('Scheduled: create an action', 'At a time (cron), set min/max/desired.'), ('Predictive: learn', 'The policy analyses at least a day (ideally two weeks) of history.'), ('Forecast', 'It predicts load for the coming hours.'), ('Pre-launch', 'Capacity is launched ahead so it is warm at the peak.'), ('Dynamic still runs', 'Target tracking adds more if the forecast was too low.')],
    words=[('cron', 'a way of writing schedules (minute hour day …)'), ('forecast', 'a prediction of future load'), ('pre-warm', 'start capacity before it is needed')],
    diff=table(['', 'Scheduled', 'Predictive', 'Dynamic'], [['Trigger', 'clock', 'ML forecast', 'live metric'], ['Best for', 'known events', 'repeating patterns', 'surprises'], ['Acts', 'before', 'before', 'after load rises']], minw=480),
    where=['Sales, festivals, exam results', 'Office-hours internal apps', 'Daily batch windows'],
    realworld='Retailers commonly pre-scale for sale events with scheduled actions and load tests days before, because a sudden flood can arrive faster than reactive scaling can launch servers.',
    pro='Run predictive scaling in “forecast only” mode for a week first: it shows what it <i>would</i> have launched, so you can compare with reality before letting it act.')

def a_burst(k):
    o = t(180, 12, ['Private data centre: normal day', 'Peak exceeds private capacity', 'Overflow bursts to public cloud'][k], 9, 'ink', bold=True)
    o += box(14, 30, 160, 100, 'card', rx=8) + t(94, 46, 'office data centre', 7.6, 'ink', bold=True)
    used = [3, 6, 6][k]
    for i in range(6):
        o += box(24 + (i % 3) * 48, 56 + (i // 3) * 34, 40, 28, 'blue' if i < used else 'card', rx=3)
    if k == 1:
        o += t(94, 146, 'full — new jobs wait ⚠', 7.4, 'red', bold=True)
    if k == 2:
        o += box(200, 30, 150, 100, 'green', rx=8) + t(275, 46, 'public cloud (AWS)', 7.6, 'ink', bold=True)
        for i in range(4):
            o += box(210 + (i % 2) * 70, 56 + (i // 2) * 34, 60, 28, 'blue', rx=3) + t(240 + (i % 2) * 70, 74 + (i // 2) * 34, 'burst VM', 6.6, 'ink', bold=True)
        o += packet(174, 80, 200, 80, '') + t(180, 146, 'paid only for the overflow hours, then released', 7.2, 'green', bold=True)
    return o
A_BURST = cap([a_burst(k) for k in range(3)], [('Normal day', 'The company runs on its own data centre, half full.', 'No cloud needed.'), ('Capacity exhausted', 'Month-end processing needs twice the servers it owns.', 'Buying more for a few days a month would waste money.'), ('Burst to the cloud', 'The overflow runs on cloud VMs (connected by VPN/Direct Connect)', 'and is released afterwards.')],
    'Cloud bursting in action', 'A hybrid pattern for peaks beyond private capacity.', 'Cloud bursting', 'Animation: private data centre half full; at peak it is full and jobs wait; overflow runs on public cloud burst VMs, released afterwards.', 's6anim')
T6 = vtype(6, 'Cloud bursting', 'violet',
    '<b>Cloud bursting</b> is a hybrid-cloud deployment pattern in which an application runs in a private cloud or data centre and, when demand exceeds that capacity, the excess workload “bursts” into a public cloud, which is released when demand falls.',
    'A wedding caterer with its own kitchen that rents a second commercial kitchen only for the peak wedding season.',
    'TiffinGo’s parent company keeps its accounting batch jobs in its own data centre. At month-end the jobs need twice the capacity, so extra job runners start in AWS over a VPN and shut down after closing.',
    'AWS: VPN/Direct Connect + Auto Scaling, AWS Batch, Outposts with Region overflow; Azure: Azure Arc, ExpressRoute, Azure Batch; Google: Anthos/GKE Enterprise, Cloud Interconnect; HPC schedulers (Slurm) with cloud nodes.',
    '', A_BURST,
    'batch, rendering, analytics or test workloads with occasional peaks; data can move or is already replicated.',
    'apps tightly coupled to on-prem databases (latency), large data that must move for each burst (transfer cost), or strict data-residency rules for the burst Region.',
    plain='A company normally uses its own computers, and only when they are full does it temporarily rent extra computers from a public cloud.',
    how=[('Connect networks', 'VPN or Direct Connect between data centre and VPC.'), ('Same images', 'Workers run from images/containers usable in both places.'), ('Watch the queue', 'A scheduler sees the private capacity is full.'), ('Launch cloud workers', 'Extra workers start in the cloud and pull jobs.'), ('Move data wisely', 'Send only what jobs need; return results.'), ('Release', 'Workers terminate when the queue empties.')],
    words=[('hybrid cloud', 'using private and public cloud together'), ('Direct Connect', 'a private dedicated link to AWS'), ('batch job', 'work processed in a queue, not interactively')],
    diff=table(['', 'Cloud bursting', 'Elasticity in one cloud', 'Multi-cloud'], [['Base capacity', 'private', 'public', 'several public clouds'], ['Overflow to', 'public cloud', 'same cloud', '—'], ['Main challenge', 'networking + data movement', 'scaling policy', 'portability']], minw=520),
    where=['Rendering farms and VFX', 'Research HPC clusters', 'Month-end finance processing', 'CI/CD build peaks'],
    realworld='Research institutions with on-premises HPC clusters commonly extend their schedulers to cloud nodes for deadline peaks (a pattern supported by tools such as Slurm with cloud plugins and AWS ParallelCluster).',
    pro='Bursting is easiest for stateless, data-light work. If each burst needs terabytes of on-prem data, transfer time and egress can cancel the benefit — keep a replicated dataset in the cloud instead.')

def a_srv(k):
    o = t(180, 12, ['No requests: nothing runs', 'Burst: 1,000 at once', 'Quiet again: back to zero'][k], 9, 'ink', bold=True)
    n = [0, 12, 0][k]
    for i in range(n):
        o += box(20 + (i % 6) * 54, 34 + (i // 6) * 44, 46, 36, 'green', rx=4) + t(43 + (i % 6) * 54, 56 + (i // 6) * 44, 'λ', 9, 'ink', bold=True)
    if k != 1:
        o += t(180, 80, 'cost: ₹0 per idle hour', 9, 'ink', bold=True)
    o += t(180, 146, ['functions exist only as code', 'each request gets an execution environment, up to concurrency limits', 'environments freeze and disappear'][k], 7.2, 'ink', bold=True)
    return o
A_SRV = cap([a_srv(k) for k in range(3)], [('Zero', 'With no events, no execution environment runs and nothing is billed.', ''), ('Burst', 'A thousand photo uploads arrive: the platform starts environments in', 'parallel, up to the account’s concurrency limit — no policy to write.'), ('Back to zero', 'When events stop, environments are frozen and removed.', 'Scale-to-zero is the extreme form of elasticity.')],
    'Serverless scaling in action', 'Per-request scaling with no servers to manage.', 'Serverless', 'Animation: no environments with no requests; twelve function environments during a burst; back to zero when quiet.', 's7anim')
T7 = vtype(7, 'Serverless scaling (scale to zero)', 'red',
    '<b>Serverless scaling</b> is automatic, per-request scaling by the platform: functions or serverless containers run as many concurrent copies as incoming events require, within account concurrency limits, and scale to zero when idle, with billing only for actual use.',
    'Street-side food stalls that appear only when a festival crowd arrives and vanish when it leaves — no rent on quiet days.',
    'TiffinGo’s photo-thumbnail Lambda handles 3 uploads at midnight and 1,000 during a promotion, with no scaling policy written and no cost when nobody uploads.',
    'AWS Lambda (concurrency, provisioned concurrency), Fargate with Application Auto Scaling, App Runner; Azure Functions, Container Apps; Google Cloud Run (scale to zero, max instances).',
    '', A_SRV,
    'spiky, event-driven or unpredictable workloads; small teams.',
    'steady high-volume traffic (containers/VMs may be cheaper) or latency-critical paths sensitive to cold starts.',
    plain='You only upload code. The cloud runs as many copies as needed when requests come in and runs none when nothing is happening.',
    how=[('Event arrives', 'HTTP request, file upload, queue message.'), ('Find or create an environment', 'Warm environments are reused; otherwise a new one starts (cold start).'), ('Run in parallel', 'More simultaneous events → more environments, up to the concurrency limit.'), ('Throttle if needed', 'Beyond the limit, requests are throttled or queued.'), ('Scale to zero', 'Idle environments are removed.')],
    words=[('concurrency', 'how many copies run at the same moment'), ('throttling', 'refusing or delaying requests over a limit'), ('provisioned concurrency', 'environments kept warm in advance (paid)')],
    diff=table(['', 'Serverless', 'Auto Scaling group'], [['You configure', 'memory, concurrency limits', 'template, min/max, policy'], ['Smallest size', 'zero', 'min (often 2)'], ['Scaling speed', 'per request, seconds', 'minutes (instance boot)']], minw=480),
    where=['Event processing', 'APIs with spiky traffic', 'Scheduled jobs', 'Prototypes and internal tools'],
    realworld='AWS Lambda scales each function by adding execution environments per concurrent request; AWS documents per-function scaling rates and account-level concurrency quotas that can be raised on request.',
    pro='Set a <i>maximum</i> too: Lambda reserved concurrency or Cloud Run max-instances protects a fragile downstream database from being overwhelmed by unlimited scaling.')

SUMMARY = table(['#', 'Idea', 'How capacity changes', 'Automatic?', 'Typical use'], [
    ['1', 'Vertical scaling', 'bigger/smaller machine', 'rarely', 'databases, legacy'], ['2', 'Horizontal scaling', 'more/fewer machines', 'can be', 'web/API tiers'], ['3', 'Elasticity', 'both ways, following demand', 'yes', 'any variable load'],
    ['4', 'Dynamic (target/step)', 'reacts to metrics', 'yes', 'unpredictable load'], ['5', 'Scheduled/predictive', 'before known/learned peaks', 'yes', 'festivals, daily peaks'], ['6', 'Cloud bursting', 'private → public overflow', 'yes (hybrid)', 'batch, HPC'], ['7', 'Serverless', 'per request, to zero', 'yes', 'events, spiky APIs']], minw=640)
CHECK = ('  <h3>Check yourself: which one fits?</h3>\n' +
    qx('A. Exam results go live at exactly 10:00 on a known date.', ['Vertical scaling', 'Scheduled scaling (pre-scale)', 'Cloud bursting', 'Nothing'], 1, 'Capacity must be ready before the spike.') +
    qx('B. A single PostgreSQL server is at 95% CPU; the app cannot be split today.', ['Vertical scaling', 'Serverless', 'Cloud bursting', 'Predictive'], 0, 'Scale up the database.') +
    qx('C. An on-prem render farm needs 3× capacity for two weeks a year.', ['Cloud bursting', 'Dedicated Host', 'Vertical scaling', 'Edge location'], 0, 'Overflow to the public cloud temporarily.') +
    qx('D. Keep average CPU of a web tier at 50% automatically.', ['Target tracking', 'Scheduled action', 'Bursting', 'Reserved Instances'], 0, 'Dynamic target tracking.') +
    qx('E. Which describes elasticity rather than scalability?', ['Can grow to 10× users', 'Adds and removes capacity automatically as demand changes', 'Uses big servers', 'Uses one Region'], 1, 'Both directions, automatically.'))

TYPES = ('  <p>Seven scaling ideas, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['Why can CPU be a bad scaling metric for a web tier?', 'What protects a database from Lambda’s unlimited scaling?', 'How do you trust predictive scaling before letting it act?'], 'types 4, 7 and 5') + MAP
         + jump(['Vertical', 'Horizontal', 'Elasticity', 'Dynamic', 'Scheduled/predictive', 'Bursting', 'Serverless']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = table(['Design rule', 'Why', 'How in AWS'], [
    ['Stateless app servers', 'any instance can serve any request', 'sessions in ElastiCache/DynamoDB, files in S3'], ['Health checks', 'never send traffic to broken instances', 'ALB target group health checks'],
    ['Spread across AZs', 'scaling and availability together', 'Auto Scaling group with ≥2 AZs'], ['Fast start', 'scale before users notice', 'golden AMIs, small containers, warm pools'],
    ['Right metric', 'scale on what limits you', 'requests per target, queue backlog'], ['Limits', 'protect downstream systems and budget', 'max size, reserved concurrency, budgets']], minw=560)

DEEP = ('  <h3>Scalability, elasticity, availability — not the same</h3>\n' + table(['Term', 'Question it answers'], [['Scalability', 'Can the system handle more load if we add resources?'], ['Elasticity', 'Does capacity follow demand automatically, up and down?'], ['High availability', 'Does it keep working when a component fails?'], ['Fault tolerance', 'Does it keep working with no visible interruption?']], minw=480) +
    '\n  <h3>Amdahl’s law: why adding servers stops helping</h3>\n  <p>If 10% of the work for each request is serial (a single database lock, one shared counter), the maximum speed-up from adding more parallel servers is 10×, no matter how many you add. That is why scaling projects often end up redesigning the shared part — caches, queues, read replicas, sharding.</p>\n'
    '  <h3>Kubernetes has two levels of autoscaling</h3>\n  <ul><li><b>Pods:</b> the Horizontal Pod Autoscaler changes the number of pods by CPU/memory/custom metrics.</li><li><b>Nodes:</b> Cluster Autoscaler or Karpenter adds VMs when pods cannot be scheduled and removes empty ones.</li><li>Both must be configured — scaling pods without nodes leaves pods “Pending”.</li></ul>')

clouds = vendor_tabs('<p><b>AWS:</b> EC2 Auto Scaling (target tracking, step, scheduled, predictive, warm pools), Application Auto Scaling (ECS, DynamoDB, Aurora replicas), Elastic Load Balancing listeners and target groups, Lambda concurrency, Karpenter for EKS.</p>',
    '<p><b>Azure:</b> Virtual Machine Scale Sets with autoscale rules, schedules and predictive autoscale; App Service autoscale; Azure Functions and Container Apps scale rules (KEDA); AKS cluster autoscaler.</p>',
    '<p><b>Google Cloud:</b> managed instance groups with autoscaler (CPU, load-balancing utilisation, schedules, predictive); Cloud Run (max/min instances, scale to zero); GKE cluster autoscaler and HPA.</p>') + \
    cloud3([['Group of identical VMs', 'Auto Scaling group', 'VM Scale Set', 'Managed instance group'], ['Load balancer', 'ALB / NLB', 'Load Balancer / App Gateway', 'Cloud Load Balancing'], ['Scheduled scaling', 'Scheduled actions', 'Autoscale schedules', 'Scaling schedules'],
            ['Predictive', 'Predictive scaling', 'Predictive autoscale', 'Predictive autoscaling'], ['Serverless', 'Lambda, Fargate', 'Functions, Container Apps', 'Cloud Run']])

proof = [
    ('Step 1 · Scale out on one machine (real)', code('python', 'l53_scale.py', "procs = [Process(target=serve, args=(p,)) for p in (8101, 8102)]   # two identical API servers\nload([8101])          # 120 requests, 8 at a time, one server\nload([8101, 8102])    # same load, round-robin over two servers", sc('machine')), 'Two copies of the same API on a 2-core machine: 2.6× the throughput. A load balancer does this across VMs.'),
    ('Step 2 · Fixed vs elastic over a Diwali day (simulation)', code('python', 'l53_sim.py', "n = max(2, ceil(traffic / (CAP * TARGET)))      # target tracking at 50%, min 2 for two AZs\nfixed = ceil(max(traffic) / (CAP * TARGET))      # sized for the peak, all day", sim('hour')), 'A model, not a measurement: assumes 100 requests/s per instance at 100% CPU. Price is the real Mumbai On-Demand rate for m7i.large.'),
    ('Step 3 · An Auto Scaling group with target tracking (emulator)', code('bash', 'terminal', "aws autoscaling create-auto-scaling-group --auto-scaling-group-name menu-asg \\\n  --launch-template LaunchTemplateName=menu-lt --min-size 2 --max-size 10 --desired-capacity 2 \\\n  --availability-zones ap-south-1a ap-south-1b\naws autoscaling put-scaling-policy --auto-scaling-group-name menu-asg --policy-name cpu50 \\\n  --policy-type TargetTrackingScaling --target-tracking-configuration '{…\"TargetValue\":50.0}'\naws autoscaling set-desired-capacity --auto-scaling-group-name menu-asg --desired-capacity 6", aws('== 1)')), 'Group created across two AZs, a target-tracking policy at 50% CPU, then scaled to 6 (what the policy does when CPU stays high). Output from the moto emulator.')]

prac = practical('Every step has a <b>UI way</b> and a <b>CLI way</b>. Step 1 runs on your own computer. Steps 2–4 use AWS (<b>CLI outputs from the moto emulator</b>). t3.micro instances are Free-Tier eligible; delete the group afterwards so instances stop.', [
    ('1 · Feel horizontal scaling locally', uicli(
        ['Docker Desktop: run two containers from the same web image on ports 8081 and 8082 ([[Images]] → [[Run]] → [[Optional settings]] → host port).', 'Open both in the browser; a load balancer would spread users across them.'],
        code('bash', 'terminal', 'python3 l53_scale.py        # script in lab/jobs/m5 — starts 2 servers and load-tests 1 vs 2', sc('machine')), ui_label='UI way — Docker Desktop'),
        'Same code, more copies, more throughput.'),
    ('2 · Create an Auto Scaling group across two AZs', uicli(
        ['[[EC2]] → [[Launch Templates]] → create <code>menu-lt</code> (AMI Amazon Linux 2023, t3.micro) — Lesson 4.4.', '[[EC2]] → [[Auto Scaling Groups]] → [[Create Auto Scaling group]] → name <code>menu-asg</code> → template <code>menu-lt</code> → [[Next]].', 'Network: choose subnets in [[ap-south-1a]] and [[ap-south-1b]] → [[Next]].', 'Group size: Desired 2, Min 2, Max 10 → [[Next]] … [[Create Auto Scaling group]].'],
        code('bash', 'terminal', "aws autoscaling create-auto-scaling-group --auto-scaling-group-name menu-asg \\\n  --launch-template LaunchTemplateName=menu-lt --min-size 2 --max-size 10 --desired-capacity 2 \\\n  --vpc-zone-identifier \"subnet-aaa,subnet-bbb\"", aws('== 1)', '== 2)')), ui_label='UI way — AWS Management Console'),
        'On a real account use --vpc-zone-identifier with subnet IDs; the emulator run used --availability-zones.'),
    ('3 · Add a target-tracking policy', uicli(
        ['Open <code>menu-asg</code> → [[Automatic scaling]] tab → [[Create dynamic scaling policy]].', 'Policy type [[Target tracking scaling]] → metric [[Average CPU utilization]] → target value <code>50</code> → instance warm-up 120 s → [[Create]].', 'Optional: [[Create scheduled action]] for Diwali 17:45 → Min 10.'],
        code('bash', 'terminal', "aws autoscaling put-scaling-policy --auto-scaling-group-name menu-asg --policy-name cpu50 \\\n  --policy-type TargetTrackingScaling \\\n  --target-tracking-configuration '{\"PredefinedMetricSpecification\":{\"PredefinedMetricType\":\"ASGAverageCPUUtilization\"},\"TargetValue\":50.0}'\naws autoscaling put-scheduled-update-group-action --auto-scaling-group-name menu-asg \\\n  --scheduled-action-name diwali --recurrence \"45 12 * * *\" --min-size 10   # cron is in UTC", aws('== 2)', '== 3)')), ui_label='UI way — AWS Management Console'),
        'CloudWatch alarms for target tracking are created automatically — you will see them under CloudWatch → Alarms. 17:45 IST = 12:15 UTC (adjust the cron).'),
    ('4 · Watch it scale (and scale back)', uicli(
        ['<code>menu-asg</code> → [[Details]] → [[Edit]] → Desired capacity 6 → [[Update]].', '[[Activity]] tab: “Launching a new EC2 instance…” entries; [[Instance management]] tab: instances spread across both AZs.', 'Set Desired back to 2 and watch instances terminate.'],
        code('bash', 'terminal', "aws autoscaling set-desired-capacity --auto-scaling-group-name menu-asg --desired-capacity 6\naws autoscaling describe-auto-scaling-groups --auto-scaling-group-names menu-asg \\\n  --query 'AutoScalingGroups[].[DesiredCapacity,length(Instances)]' --output text\naws autoscaling describe-scaling-activities --auto-scaling-group-name menu-asg --max-items 5", aws('== 3)', '== 4)')), ui_label='UI way — AWS Management Console'),
        'On a real account, generate CPU load (e.g. <code>stress-ng --cpu 2</code> via user data) to see the policy scale by itself.')],
    cleanup='Console: select <code>menu-asg</code> → [[Actions]] → [[Delete]] (terminates its instances); delete the launch template. CLI: <code>aws autoscaling delete-auto-scaling-group --auto-scaling-group-name menu-asg --force-delete</code>; <code>aws ec2 delete-launch-template --launch-template-name menu-lt</code>.'.replace('[[', '<b>').replace(']]', '</b>'))

mist = mistakes([
    ['Scaling a stateful app horizontally.', 'Sessions/files stored on the instance.', 'Move state to a cache/DB/S3 first; then scale out.'],
    ['Max size too low (or no max).', 'Defaults left unchanged.', 'Set max from load tests and budget; add AWS Budgets alerts.'],
    ['Scaling on CPU for an I/O-bound app.', 'CPU is the default metric.', 'Use requests per target, latency or queue depth.'],
    ['Expecting instant scale-out for sudden spikes.', 'Boot + warm-up takes minutes.', 'Pre-scale with scheduled/predictive scaling; use warm pools; keep headroom.'],
    ['Aggressive scale-in causing flapping.', 'Thresholds too close, no cooldown.', 'Use target tracking; scale in slowly; set warm-up.'],
    ['Scaling the web tier but not the database.', 'The bottleneck moves.', 'Load-test the whole path; add read replicas, caching, connection pooling.'],
    ['Single AZ Auto Scaling group.', 'Only one subnet chosen.', 'Always select subnets in at least two AZs.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Scalability, elasticity, cloud bursting, auto-scaling and load balancing.'], ['AWS CLF-C02', 'Elasticity as a cloud benefit; Auto Scaling, ELB; scale up vs out.'], ['AZ-900', 'Scalability vs elasticity; VM Scale Sets; autoscale.'], ['Google Cloud Digital Leader', 'Elasticity, managed instance groups, serverless scaling.']], minw=520) + '\n  <h3>Exam-style questions with explanations</h3>\n' + \
    qx('1. Which describes horizontal scaling?', ['Changing to a larger instance type', 'Adding more instances behind a load balancer', 'Adding memory to a server', 'Moving to another Region'], 1, 'Scale out = more instances.') + \
    qx('2. Which AWS feature automatically adjusts the number of EC2 instances to demand?', ['Amazon EC2 Auto Scaling', 'AWS Budgets', 'Amazon S3', 'AWS Organizations'], 0, 'Auto Scaling groups with scaling policies.') + \
    qx('3. Elasticity means…', ['capacity follows demand automatically, up and down', 'servers never fail', 'data is encrypted', 'apps run in many Regions'], 0, 'Rapid elasticity (NIST).') + \
    qx('4. A private data centre sends excess load to a public cloud during peaks. This is…', ['multi-tenancy', 'cloud bursting', 'vertical scaling', 'edge computing'], 1, 'Hybrid overflow pattern.') + \
    qx('5. Which policy keeps a metric at a chosen value?', ['Simple scaling', 'Target tracking', 'Scheduled action', 'Manual'], 1, 'Target tracking.') + \
    qx('6. In Azure, which resource scales a group of identical VMs automatically?', ['Availability set', 'Virtual Machine Scale Set', 'Resource group', 'Region pair'], 1, 'VM Scale Sets.')

proj = miniproject('Mini project: an elastic menu API that survives a Diwali load test',
    'Deploy a stateless API in an Auto Scaling group behind a load balancer, load-test it, and prove it scales out and back in.',
    ['<b>App:</b> a small Flask/FastAPI menu API that does some CPU work per request; bake it into an AMI (Lesson 4.4) or install with user data.',
     '<b>Load balancer:</b> ALB with an HTTP listener → target group (health check <code>/health</code>) in two public subnets.',
     '<b>Group:</b> Auto Scaling group min 2, max 8, in two AZs, attached to the target group; target tracking on <i>ALB request count per target</i> (e.g. 200).',
     '<b>Load test:</b> from another machine run <code>hey -z 10m -c 100 http://&lt;alb-dns&gt;/menu</code>; record requests/s and p95 latency.',
     '<b>Observe:</b> screenshots of the Activity tab, CloudWatch graphs of instance count vs request count.',
     '<b>Scale in:</b> stop the test; confirm instances return to 2.',
     '<b>Report:</b> compare instance-hours used with a fixed fleet sized for the peak (use the price from Lesson 5.5). Delete everything afterwards.'],
    'Graphs showing capacity following load, and a cost comparison.', 'This lesson + 4.4 (images) + 5.5 (pricing) + Module 7 (load balancing).')

assemble_v2(HERE, story_h2='Twenty-two servers at 8 p.m., two at 3 a.m.', hook_html=hk,
    narration='Last Diwali TiffinGo bought servers for its busiest hour and paid for them every hour of the year. This year it wants capacity that follows the customers.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Scalability, elasticity and cloud bursting',
    formal='<b>Scalability</b> is the ability of a system to handle increased load by adding resources, either by enlarging existing resources (vertical scaling) or adding more of them (horizontal scaling). <b>Elasticity</b> (NIST: rapid elasticity) is the ability to provision and release resources automatically and rapidly, outward and inward, commensurate with demand. <b>Cloud bursting</b> is a hybrid deployment model in which an application normally runs in a private environment and uses public-cloud resources when demand exceeds private capacity.',
    simple='Scalability: you can grow when needed. Elasticity: the cloud grows and shrinks for you automatically. Cloud bursting: borrow public-cloud capacity only when your own data centre is full.',
    interview=['“Scalability is the ability to handle more load by adding resources — scaling up with bigger machines or out with more machines. Elasticity is doing it automatically in both directions so capacity follows demand.”', '“In AWS I put stateless instances in an Auto Scaling group across two AZs behind an ALB, with target tracking — for example average CPU 50% — plus scheduled scaling for known events.”', '“Cloud bursting is a hybrid pattern where on-premises capacity overflows into the public cloud during peaks. In a simulation of a Diwali day, elastic scaling used 144 server-hours instead of 528.”'],
    terms_rows=[('Scale up / down', 'Bigger or smaller machine.'), ('Scale out / in', 'More or fewer machines.'), ('Elasticity', 'Automatic both ways.'), ('Auto Scaling group', 'Managed set of identical instances.'), ('Target tracking', 'Keep a metric at a value.'), ('Scheduled scaling', 'Change capacity at set times.'), ('Predictive scaling', 'ML forecast → pre-launch.'), ('Cloud bursting', 'Private overflow into public cloud.'), ('Listener', 'Load balancer port + rules.'), ('Stateless', 'Keeps no session on the server.')],
    exam='CLF-C02 loves “elasticity” as a benefit of cloud and “Auto Scaling + ELB” as the answer for variable load. Know scale up vs out, and that AZ-900 calls the VM group a “scale set”.',
    picture_h2='Up vs out, and scalable vs elastic', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven scaling ideas, one by one', TYPES)],
    how_h2='Diwali evening, step by step', how_intro='From the load balancer listener to new instances and back — the full auto-scaling loop.', how_anim=FLOW,
    parts_h2='Design rules for systems that scale', parts_html=parts, lv='',
    myth_rows=[('Scalable = elastic.', 'Elastic adds automatic scale-in and scale-out.', 'Elasticity figure.'), ('Bigger servers solve everything.', 'Vertical scaling has a ceiling and a single point of failure.', 'Type 1.'), ('Auto Scaling reacts instantly.', 'Boot and warm-up take minutes — pre-scale known peaks.', 'Type 5.')],
    extra_secs=[('deep', 'Deep dive', 'Scalability vs availability, Amdahl’s law, Kubernetes’ two levels of autoscaling', DEEP)],
    clouds_html=clouds, proof_h2='Real proof: scale-out measured, elasticity simulated, Auto Scaling configured', proof_intro='Step 1 is a real measurement on our lab machine (10 Nov 2026); step 2 is a clearly labelled simulation; step 3 uses the moto AWS emulator.', proof_steps=proof,
    practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Explain scalability, elasticity and cloud bursting and how they differ.', 'Choose between vertical and horizontal scaling.', 'Explain target tracking, step, scheduled, predictive and serverless scaling.', 'Configure an Auto Scaling group and policy from the console and the CLI.', 'Estimate the cost difference between fixed and elastic capacity.'],
    next_html='<a href="../04-service-level-agreements/">5.4 Service level agreements</a>.',
    pre='<b>Before you start:</b> <a href="../../04-virtualization/04-vm-provisioning-and-migration/">4.4 (golden images, Auto Scaling)</a> and <a href="../01-regions-availability-zones-and-edge-locations/">5.1 (AZs)</a>.')
