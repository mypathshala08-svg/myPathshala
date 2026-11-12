import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def sla(a, b=None): return capsec('l54_sla.txt', a, b)
def aws(a, b=None): return capsec('l54_aws.txt', a, b)
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)

hk = hook('AWS promises 99.99% for EC2. TiffinGo was down for 40 minutes on a Friday night. Does AWS owe it money?',
    'Probably a <b>service credit</b> — not compensation for lost orders. An SLA is a contract with precise definitions: 99.99% allows only <b>4.3 minutes</b> of downtime a month, but only for deployments in <b>two or more Availability Zones</b>, and a miss returns <b>10%</b> of that month’s EC2 bill (30% below 99%, 100% below 95%). Also, three 99.99% / 99.99% / 99.95% components in a chain give only <b>99.93%</b> together. This lesson teaches how to read an SLA, calculate availability and design to meet your own targets.',
    ['SLA, SLO, SLI and error budgets — the vocabulary interviewers expect.', 'The “nines” and composite availability, calculated.', 'Service credits, exclusions and how to claim — the fine print.'])

def story_scene():
    o = t(180, 12, 'Friday 8:10 p.m.: orders stop', 9, 'ink', bold=True)
    o += box(10, 24, 100, 90, 'red', rx=8) + t(60, 56, '40 min', 13, 'ink', bold=True) + t(60, 80, 'outage', 8, 'ink') + t(60, 98, '≈ 380 lost orders', 6.8, 'ink2')
    o += box(130, 24, 100, 90, 'card', rx=8) + t(180, 52, 'EC2 SLA', 8.4, 'ink', bold=True) + t(180, 72, '99.99%', 12, 'ink', bold=True) + t(180, 92, '= 4.3 min/month', 7, 'ink2')
    o += box(250, 24, 100, 90, 'amber', rx=8) + t(300, 52, 'You get back', 8, 'ink', bold=True) + t(300, 74, '10% credit', 10, 'ink', bold=True) + t(300, 94, 'if eligible', 7, 'ink2')
    o += t(180, 134, 'An SLA limits the provider’s liability — it does not insure your business.', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Three boxes: a 40-minute outage with about 380 lost orders; the EC2 SLA of 99.99%, equal to 4.3 minutes a month; a 10% service credit if eligible.', story_scene(), 'Read the SLA — and <tspan font-weight="700" class="s-acc">design for your own target</tspan>.', h=154)
dialogue = '''R> Sir, AWS says 99.99%. We were down 40 minutes. They must pay for our lost orders!
A> Let’s read the SLA. It covers EC2 when your instances run in two or more AZs and all of them lose connectivity together. Were ours in two AZs?
R> …Only ap-south-1a.
A> Then the Region-level SLA did not even apply; the instance-level SLA is 99.5%. And the remedy is a service credit — a percentage of the EC2 bill — never your lost revenue.
K> So the SLA is not our safety net?
A> It is the provider’s promise for its part. Our availability is our design: multiple AZs, health checks, our own SLOs. Let’s learn the vocabulary and the maths.'''

def ninesfig():
    o = t(320, 16, 'The “nines”: what each availability percentage really allows', 11, 'ink', bold=True)
    rows = [('99%', 432.0, '7.2 h/month', 'red'), ('99.5%', 216.0, '3.6 h/month', 'red'), ('99.9%', 43.2, '43 min/month', 'amber'), ('99.95%', 21.6, '22 min/month', 'amber'), ('99.99%', 4.3, '4.3 min/month', 'green'), ('99.999%', 0.4, '26 s/month', 'green')]
    for i, (p, m, lab, tn) in enumerate(rows):
        y = 34 + i * 36
        o += t(90, y + 18, p, 10, 'ink', anchor='end', bold=True) + box(100, y + 4, max(3, m * 1.1), 22, tn, rx=3) + t(108 + max(3, m * 1.1), y + 19, lab, 8, 'ink', anchor='start', bold=True)
    o += t(320, 262, 'Every extra “nine” cuts allowed downtime by 10× — and usually multiplies cost and design effort.', 7.8, 'ink2')
    o += t(320, 278, 'Real examples (provider SLAs, Nov 2026): EC2 instance 99.5% · S3 Standard 99.9% · RDS Multi-AZ 99.95% · EC2 multi-AZ 99.99%.', 7.4, 'ink2')
    return o
NINES = bigfig('Bar chart of allowed monthly downtime: 99% = 432 minutes, 99.5% = 216, 99.9% = 43.2, 99.95% = 21.6, 99.99% = 4.3, 99.999% = 26 seconds.', ninesfig(), h=290)

def stackfig():
    o = t(320, 16, 'SLA, SLO, SLI — three words, three jobs', 11, 'ink', bold=True)
    items = [('SLI', 'indicator — what you MEASURE', '“% of /order requests answered in < 300 ms with 2xx, over 5-minute windows”', 'blue'),
             ('SLO', 'objective — what you AIM for (internal)', '“99.95% of requests succeed each month” → error budget 0.05% ≈ 21.6 min', 'green'),
             ('SLA', 'agreement — what you PROMISE (contract)', '“99.9% monthly uptime or 10% credit” — set looser than the SLO', 'amber')]
    for i, (a, b, c, tn) in enumerate(items):
        y = 34 + i * 70
        o += box(20, y, 600, 60, tn, rx=8) + t(46, y + 36, a, 14, 'ink', bold=True) + t(96, y + 24, b, 9, 'ink', anchor='start', bold=True) + t(96, y + 44, c, 7.8, 'ink', anchor='start')
    o += t(320, 256, 'Measure (SLI) → aim higher internally (SLO) → promise lower externally (SLA), so you can miss the goal without breaching the contract.', 7.6, 'ink2')
    return o
STACK = bigfig('Three stacked boxes: SLI, the measured indicator; SLO, the internal objective with its error budget; SLA, the external contract set looser than the SLO.', stackfig(), h=268)

picture = ('  <p>Everything in this lesson rests on one table — how much downtime each percentage allows in a 30-day month:</p>\n' + NINES +
           '\n  <p>And on three words people mix up all the time:</p>\n' + STACK)

# how: life of an SLA incident
RN = {'inc': (4, 54, 56, 50, 'server', 'Incident', 'AZ issue'), 'hc': (68, 4, 60, 46, 'shield', 'Health check', 'SLI drops'), 'al': (68, 104, 60, 46, 'chart', 'Alarm', 'on-call paged'),
      'fo': (140, 54, 62, 50, 'lb', 'Failover', 'other AZ'), 'calc': (214, 4, 64, 46, 'meter', 'Uptime %', 'for the month'), 'cl': (214, 104, 64, 46, 'dns', 'Claim', 'Support case'), 'cr': (290, 54, 66, 50, 'chart', 'Credit', '10/30/100%')}
RS = [dict(on=['inc', 'hc'], hot='hc', move=(60, 70, 72, 40, ''), head='Step 1 · Something breaks; your SLI shows it', text='A problem in one AZ makes requests fail. Your health checks (from outside, every', text2='30 s) see errors — your own measurement, not the provider’s status page.', svc='Route 53 health checks, CloudWatch Synthetics, uptime monitors'),
      dict(on=['inc', 'hc', 'al'], hot='al', move=(98, 50, 98, 104, 'alarm'), head='Step 2 · Alarm and response', text='After 3 failed checks an alarm pages the on-call engineer and opens an incident.', text2='Every minute now spends your error budget.', svc='CloudWatch alarm → SNS → phone/Slack/PagerDuty'),
      dict(on=['inc', 'hc', 'al', 'fo'], hot='fo', move=(128, 127, 150, 90, ''), head='Step 3 · Design limits the damage', text='Because the app runs in two AZs, the load balancer stops sending traffic to the', text2='failed AZ. With one AZ, you would simply wait for the provider.', svc='This is the difference between 40 minutes and 2 minutes'),
      dict(on=['inc', 'hc', 'al', 'fo', 'calc'], hot='calc', move=(202, 70, 222, 40, 'minutes'), head='Step 4 · Compute monthly uptime', text='Monthly Uptime % = 100% − % of minutes unavailable (as the SLA defines it).', text2='40 min in a 30-day month → 99.907%: below 99.99% → 10% credit tier.', svc='Read the definition — e.g. EC2 Region-level requires ≥2 AZs all unavailable'),
      dict(on=['inc', 'hc', 'al', 'fo', 'calc', 'cl'], hot='cl', move=(246, 50, 246, 104, 'claim'), head='Step 5 · Claim it yourself, in time', text='Open a Support case with dates, times, Region/AZ, resource IDs and request logs', text2='before the end of the second billing cycle after the incident.', svc='Credits are not automatic for most SLAs'),
      dict(on=list(RN), hot='cr', move=(278, 127, 298, 90, ''), head='Step 6 · Receive a service credit', text='If valid, a credit (10%, 30% or 100% of the affected service’s monthly charge)', text2='is applied to future bills — not cash, not lost revenue.', svc='Your real protection is architecture and your own SLOs')]
LIFE = flow_anim('One outage, from first error to service credit', 'What happens — and what you must do — when a provider misses its SLA.', 'SLA incident', 'Animation: incident; health check SLI drops; alarm pages on-call; failover to another AZ; monthly uptime computed; credit claimed through a support case; service credit applied.', RN, RS, hid='slaflow')

# ------------------------------------------------------------------ types
def mapfig():
    o = t(320, 16, 'Seven SLA ideas you must tell apart', 11, 'ink', bold=True)
    items = [('1', 'Service-based SLA', 'same terms for all customers', 'amber'), ('2', 'Customer / multi-level SLA', 'negotiated, layered', 'amber'), ('3', 'SLO', 'internal target', 'green'), ('4', 'SLI', 'the measurement', 'blue'),
             ('5', 'Error budget', 'allowed unreliability', 'green'), ('6', 'Composite availability', 'chains and redundancy', 'violet'), ('7', 'Credits and exclusions', 'the fine print', 'red')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 14 + (i % 4) * 156; y = 32 + (i // 4) * 78
        o += box(x, y, 148, 66, tn, rx=8) + pin(x + 14, y + 16, n) + t(x + 28, y + 20, a, 7.8, 'ink', anchor='start', bold=True) + t(x + 8, y + 46, b, 7, 'ink2', anchor='start')
    o += t(320, 208, '1–2: kinds of agreement · 3–5: how engineers manage reliability · 6–7: maths and fine print.', 7.6, 'ink2')
    return o
MAP = bigfig('Map of seven SLA ideas: 1 service-based SLA, 2 customer-based and multi-level SLA, 3 SLO, 4 SLI, 5 error budget, 6 composite availability, 7 service credits and exclusions.', mapfig(), h=220)

def a_svc(k):
    o = t(180, 12, ['One public SLA per service', 'Same for every customer', 'Read the definitions'][k], 9, 'ink', bold=True)
    docs = [('EC2', '99.99% region · 99.5% instance'), ('S3 Standard', '99.9%'), ('RDS Multi-AZ', '99.95%'), ('Lambda', '99.95%')]
    for i, (n, v) in enumerate(docs):
        o += box(14 + (i % 2) * 172, 28 + (i // 2) * 52, 160, 44, 'amber', rx=5) + t(94 + (i % 2) * 172, 46 + (i // 2) * 52, n, 8, 'ink', bold=True) + t(94 + (i % 2) * 172, 62 + (i // 2) * 52, v, 7, 'ink2')
    o += t(180, 148, ['each AWS service publishes its own SLA page', 'TiffinGo and a bank get exactly the same terms', '“unavailable” is defined precisely — e.g. ≥2 AZs for EC2’s 99.99%'][k], 7.2, 'ink', bold=True)
    return o
A_SVC = cap([a_svc(k) for k in range(3)], [('One SLA per service', 'Every major cloud service has its own published SLA with a monthly', 'uptime commitment and credit tiers.'), ('Same for everyone', 'A service-based SLA applies identically to all customers of that service —', 'you cannot negotiate it on a normal account.'), ('Definitions decide', 'Each SLA defines “unavailable” precisely; EC2’s 99.99% needs instances in', 'two or more AZs to be unavailable at the same time.')],
    'Service-based SLAs', 'The public, one-size-fits-all promise.', 'Service SLA', 'Animation: SLA cards for EC2, S3, RDS Multi-AZ and Lambda; same terms for every customer; precise definitions.', 'l1anim')
T1 = vtype(1, 'Service-based SLA (public cloud SLA)', 'amber',
    'A <b>service-based SLA</b> is a single agreement that applies the same commitments to all customers of a particular service — for a cloud provider, the published service level agreement for each service, specifying the availability commitment, how it is measured, the service credits and the exclusions.',
    'The warranty card that comes with a TV: every buyer gets the same terms, printed in advance; you cannot negotiate it at the shop.',
    'TiffinGo relies on the published SLAs: EC2 99.99% for multi-AZ deployments (99.5% per instance), S3 Standard 99.9%, RDS Multi-AZ 99.95%, Lambda 99.95%. None was negotiated.',
    'AWS service SLAs (aws.amazon.com/legal/service-level-agreements), Azure SLA for Online Services, Google Cloud SLAs per product.',
    '', A_SVC,
    'using any public cloud service — know the SLA of every component on your critical path.',
    'assuming a service has an SLA at all (some features, previews and free tiers have none) or that the headline number applies to your design.',
    plain='The cloud company publishes, for each service, how reliable it promises to be and what it gives back if it fails. Everyone gets the same promise.',
    how=[('Published per service', 'Each service has an SLA document with a version and effective date.'), ('Commitment', 'A monthly uptime percentage (e.g. 99.99%).'), ('Measurement', 'A precise definition of “unavailable” and how minutes are counted.'), ('Remedy', 'Service credit tiers as a percentage of that service’s monthly charge.'), ('Exclusions', 'Situations not covered (your errors, force majeure, previews).'), ('Claim process', 'How and by when to request a credit.')],
    words=[('SLA', 'service level agreement: a contractual promise'), ('commitment', 'the promised uptime percentage'), ('service credit', 'money off future bills, not a cash refund')],
    diff=table(['', 'Service-based SLA', 'Customer-based SLA', 'Multi-level SLA'], [['Covers', 'one service, all customers', 'one customer, all its services', 'layers: corporate, customer, service'], ['Negotiable', 'no', 'yes', 'yes'], ['Typical in', 'public cloud', 'enterprise outsourcing', 'large enterprises, MSPs']], minw=560),
    where=['Every public cloud service', 'SaaS products’ standard plans', 'Telecom/ISP standard plans'],
    realworld='The AWS EC2 SLA (as of Nov 2026) commits to 99.99% Region-level monthly uptime for instances in two or more AZs and 99.5% for an individual instance, with credits of 10%, 30% or 100% depending on how far uptime falls.',
    pro='SLA documents change. AWS keeps “prior versions … not currently in effect” pages — compare them and you will see, for example, the single-instance EC2 SLA rising from 90% to 99.5% over the years.')

def a_cust(k):
    o = t(180, 12, ['Corporate level', 'Customer level', 'Service level'][k], 9, 'ink', bold=True)
    for i, (n, d, tn) in enumerate([('Corporate', 'applies to all customers: security, support hours', 'violet'), ('Customer', 'this bank: named contacts, penalties, reports', 'blue'), ('Service', 'per service: payments API 99.95%', 'amber')]):
        on = i <= k
        o += box(20 + i * 20, 28 + i * 40, 320 - i * 40, 34, tn if on else 'card', rx=6) + t(180, 42 + i * 40, n + ' SLA', 8, 'ink', bold=True) + t(180, 55 + i * 40, d, 6.8, 'ink2')
    return o
A_CUST = cap([a_cust(k) for k in range(3)], [('Corporate level', 'Terms that apply to every customer of the provider — security, support,', 'general obligations.'), ('Customer level', 'Terms negotiated for one customer — penalties, reports, named contacts.', ''), ('Service level', 'Targets per service for that customer — e.g. payments API 99.95%,', 'reports 99.5%.')],
    'Customer and multi-level SLAs', 'Agreements tailored to one big customer.', 'Multi-level SLA', 'Animation: three stacked layers — corporate, customer and service-level SLA.', 'l2anim')
T2 = vtype(2, 'Customer-based and multi-level SLA', 'amber',
    'A <b>customer-based SLA</b> covers all the services provided to one particular customer under a single negotiated agreement; a <b>multi-level SLA</b> structures commitments in layers — corporate (all customers), customer (one customer) and service (each service for that customer).',
    'A wedding caterer’s contract with one family: general terms everyone signs, plus special terms for this family, plus details for each event (mehendi, sangeet, reception).',
    'When TiffinGo sells its platform to a hotel chain, the contract includes a customer-level SLA — 99.9% for ordering, response within 1 hour for severity-1 issues, monthly reports — layered on TiffinGo’s standard terms.',
    'Enterprise agreements with cloud providers and MSPs, ITIL service level management, outsourcing contracts; the cloud provider’s own SLA stays service-based underneath.',
    '', A_CUST,
    'you provide services to large customers or receive managed services from partners.',
    'promising more than your providers’ SLAs and your architecture can support — your SLA must be backed by your design.',
    plain='A special agreement written for one big customer, often in layers: general rules, rules for this customer, and targets for each service they use.',
    how=[('Negotiate', 'Customer and provider agree targets, measurements, penalties and reporting.'), ('Layer', 'Corporate terms + customer terms + per-service targets.'), ('Back with OLAs', 'Internal operational level agreements and supplier SLAs must support each promise.'), ('Report', 'Regular SLA reports and reviews.'), ('Penalties/credits', 'Applied as agreed if targets are missed.')],
    words=[('ITIL', 'a widely used framework for IT service management'), ('OLA', 'operational level agreement between internal teams'), ('MSP', 'managed service provider')],
    diff=table(['', 'Customer-based', 'Service-based'], [['Unit', 'one customer', 'one service'], ['Written by', 'both parties', 'the provider alone']], minw=420),
    where=['Enterprise SaaS contracts', 'IT outsourcing and managed services', 'Telecom enterprise links'],
    realworld='ITIL, the IT service management framework widely used by Indian IT services companies, describes service-based, customer-based and multi-level SLA structures as standard options for service level management.',
    pro='Your SLA can never safely exceed the composite availability of everything beneath it (type 6). A 99.99% customer promise on top of a single-AZ 99.5% instance is a promise you cannot keep.')

def a_slo(k):
    o = t(180, 12, ['SLO set tighter than the SLA', 'This month so far', 'Below SLO → act before the SLA breaks'][k], 9, 'ink', bold=True)
    o += f'<path d="M20,40 L340,40" style="stroke:#2E8B57;stroke-width:1.6;stroke-dasharray:5 3"/>' + t(338, 36, 'SLO 99.95%', 7, 'green', anchor='end', bold=True)
    o += f'<path d="M20,80 L340,80" style="stroke:#D64545;stroke-width:1.6;stroke-dasharray:5 3"/>' + t(338, 76, 'SLA 99.9%', 7, 'red', anchor='end', bold=True)
    if k >= 1:
        pts = '20,30 80,32 140,34 200,36' + (' 260,52 300,58' if k == 2 else '')
        o += f'<polyline points="{pts}" style="fill:none;stroke:#2B6CB0;stroke-width:2.4"/>'
    o += t(180, 130, ['gap = safety margin', 'actual availability (SLI) above both lines', 'freeze risky releases, fix reliability — the contract is still met'][k], 7.4, 'ink', bold=True)
    return o
A_SLO = cap([a_slo(k) for k in range(3)], [('Tighter than the SLA', 'The internal objective (99.95%) sits above the external promise (99.9%):', 'the gap is a safety margin.'), ('Track it', 'The measured SLI is plotted against the SLO all month.', ''), ('React early', 'When the SLI drops below the SLO, the team stops risky releases and fixes', 'reliability — before customers are owed credits.')],
    'SLOs in action', 'The internal target that protects the external promise.', 'SLO', 'Animation: SLO line at 99.95% above SLA line at 99.9%; measured SLI above both; then dropping below the SLO but still above the SLA, triggering action.', 'l3anim')
T3 = vtype(3, 'SLO (service level objective)', 'green',
    'A <b>service level objective</b> is an internal target value or range for a service level, measured by an SLI over a period — for example, “99.95% of order requests succeed in a rolling 30 days” — used by engineering teams to make reliability decisions; it is usually stricter than any external SLA.',
    'Your own exam target: the college passes you at 40% (SLA), but you aim for 75% (SLO) so a bad day still keeps you safely above 40.',
    'TiffinGo sets an SLO of 99.95% monthly success for /order (≈ 21.6 minutes of failures allowed) while offering hotel customers an SLA of 99.9%.',
    'Google SRE practices; Amazon CloudWatch Application Signals SLOs, Azure Monitor SLOs via workbooks, Google Cloud Service Monitoring SLOs; open-source: Prometheus + Sloth/OpenSLO.',
    '', A_SLO,
    'any service users depend on — define SLOs before you need them.',
    'setting 100% (impossible) or SLOs nobody measures or acts on.',
    plain='A goal your own team sets for how reliable a service should be — usually a bit stricter than what you promise customers, so you have room for mistakes.',
    how=[('Pick what users feel', 'Availability and latency of key user journeys.'), ('Choose an SLI', 'How you will measure it (type 4).'), ('Set the target and window', 'e.g. 99.95% over 30 days.'), ('Derive the error budget', '100% − SLO (type 5).'), ('Review', 'Weekly SLO reports drive priorities.')],
    words=[('SLO', 'service level objective: internal target'), ('rolling window', 'the last N days, moving every day'), ('user journey', 'a task a user performs, like placing an order')],
    diff=table(['', 'SLO', 'SLA', 'SLI'], [['What', 'target', 'contract', 'measurement'], ['Audience', 'engineers, product', 'customers, legal', 'engineers'], ['If missed', 'change priorities', 'credits/penalties', '—'], ['Typical value', 'stricter (99.95%)', 'looser (99.9%)', 'actual (e.g. 99.97%)']], minw=520),
    where=['Site reliability engineering (SRE) teams', 'Platform and API teams', 'Product reliability reviews'],
    realworld='Google’s Site Reliability Engineering book popularised SLOs and error budgets as the way to balance reliability and feature speed; many companies now publish internal SLO dashboards for every critical service.',
    pro='Set SLOs on user-visible behaviour, not on servers. “CPU < 80%” is not an SLO; “99% of /order requests complete in under 300 ms” is.')

def a_sli(k):
    o = t(180, 12, ['Count good events', 'Count all events', 'SLI = good ÷ all'][k], 9, 'ink', bold=True)
    for i in range(20):
        bad = i in (7, 15)
        o += box(14 + (i % 10) * 34, 30 + (i // 10) * 34, 28, 28, ('red' if bad else 'green') if k >= 1 or not bad else 'green', rx=3)
    o += t(180, 120, ['18 requests answered 2xx in < 300 ms', '20 requests in the window', 'SLI = 18 / 20 = 90% for this tiny window'][k], 7.8, 'ink', bold=True)
    o += t(180, 140, 'real systems count millions of requests per window', 7, 'ink2')
    return o
A_SLI = cap([a_sli(k) for k in range(3)], [('Good events', 'Define “good” precisely: HTTP 2xx and under 300 ms for /order.', 'Count them.'), ('All events', 'Count every valid request in the same window (exclude health checks).', ''), ('The ratio', 'SLI = good ÷ all. Compare it with the SLO every few minutes and', 'over the month.')],
    'SLIs in action', 'Turning “reliable” into a number.', 'SLI', 'Animation: 20 request boxes, 18 good and 2 bad; SLI = 18/20 = 90% for the window.', 'l4anim')
T4 = vtype(4, 'SLI (service level indicator)', 'blue',
    'A <b>service level indicator</b> is a carefully defined quantitative measure of some aspect of the service level, typically expressed as the ratio of good events to valid events — for example, the proportion of requests served successfully within a latency threshold.',
    'A speedometer: the number on the dial is the indicator; the speed limit is the objective; the fine for overspeeding is the agreement.',
    'TiffinGo’s SLI for ordering: “share of POST /order requests that return 2xx within 300 ms, measured at the load balancer”. A Route 53 health check adds an outside-in availability SLI.',
    'Load-balancer logs and metrics (ALB 5xx, TargetResponseTime), CloudWatch Synthetics canaries, Route 53 health checks, Azure Application Insights availability tests, Google Cloud Monitoring uptime checks.',
    '', A_SLI,
    'you need an objective, comparable measure of reliability.',
    'measuring only server metrics, or only from inside the system — users experience DNS, network and CDN too.',
    plain='The number that tells you how well the service actually performed — for example, the percentage of orders that went through quickly.',
    how=[('Define good', 'Status codes, latency threshold, correctness.'), ('Choose where to measure', 'Load balancer, client, synthetic probes from outside.'), ('Collect', 'Count good and total events per window.'), ('Compute', 'good ÷ total, per window and per month.'), ('Alert', 'Alert on fast SLO burn, not on every error.')],
    words=[('metric', 'a number recorded over time'), ('synthetic check', 'a robot that regularly calls your site like a user'), ('latency', 'how long a response takes'), ('p99', 'the time within which 99% of requests finish')],
    diff=table(['', 'SLI', 'Monitoring metric'], [['Represents', 'user experience', 'any system detail'], ['Example', 'successful fast orders %', 'CPU utilisation']], minw=420),
    where=['Every SLO', 'Status pages', 'Incident detection'],
    realworld='Route 53 health checks probe an endpoint from checkers in multiple AWS locations and mark it unhealthy when enough checkers fail — an outside-in availability indicator that the emulator lab in this lesson configures.',
    pro='Measure at the load balancer <i>and</i> outside-in: the load balancer cannot see a DNS or certificate failure that stops every user before reaching it.')

def a_eb(k):
    o = t(180, 12, ['SLO 99.95% → budget 21.6 min', 'Spend it on releases and incidents', 'Budget gone → freeze, fix reliability'][k], 9, 'ink', bold=True)
    used = [0, 12, 24][k]
    o += box(20, 50, 320, 30, 'card', rx=4) + box(20, 50, min(320, used / 21.6 * 320), 30, 'green' if used < 15 else 'red', rx=4)
    o += t(180, 70, f'{used} of 21.6 minutes used', 8.4, 'ink', bold=True)
    o += t(180, 112, ['permission to take risks', 'a 7-min deploy incident + a 5-min dependency outage', 'stop risky launches until next window'][k], 7.6, 'ink', bold=True)
    return o
A_EB = cap([a_eb(k) for k in range(3)], [('The budget', '100% − 99.95% = 0.05% of a 30-day month = 21.6 minutes of allowed', 'failure. That is the error budget.'), ('Spend it', 'Bad deploys, experiments and incidents use it up. Budget left = freedom', 'to ship features faster.'), ('Overspent', 'When the budget is exhausted, the team pauses risky changes and works', 'on reliability until it recovers.')],
    'Error budgets in action', 'How reliability and speed are balanced.', 'Error budget', 'Animation: a 21.6-minute budget bar; partly used by incidents; fully spent leading to a release freeze.', 'l5anim')
T5 = vtype(5, 'Error budget', 'green',
    'An <b>error budget</b> is the amount of unreliability a service may have within an SLO window — 100% minus the SLO — which teams consciously “spend” on releases, experiments and incidents, and which, when exhausted, triggers a shift of effort from features to reliability.',
    'A mobile data pack: 2 GB a day. Use it as you like; when it runs out, you stop streaming until tomorrow.',
    'TiffinGo’s 99.95% SLO gives a 21.6-minute monthly budget. A bad release used 7 minutes, a payment-gateway outage 5 minutes. With 9.6 minutes left, a risky database migration is postponed to next month.',
    'SRE practice; tooling: CloudWatch Application Signals SLO burn rate, Google Cloud SLO burn-rate alerts, Datadog/Grafana SLO dashboards.',
    '', A_EB,
    'teams argue about “stability vs speed” — the budget turns it into a number.',
    'nobody has the authority to freeze releases when the budget is spent — then it is just a chart.',
    plain='The amount of failure you are allowed in a month. While some is left, the team can take risks; when it is used up, the team focuses on making things stable.',
    how=[('Compute', 'Budget = (1 − SLO) × events or minutes in the window.'), ('Track burn', 'How fast failures consume the budget.'), ('Alert on burn rate', 'e.g. budget would be gone in 2 days at the current rate.'), ('Policy', 'Agreed actions at 50%, 75%, 100% spent.'), ('Reset', 'New window, new budget.')],
    words=[('burn rate', 'how quickly the error budget is being used'), ('release freeze', 'pausing deployments'), ('window', 'the period the budget covers')],
    diff=table(['', 'Error budget', 'Downtime allowance in an SLA'], [['Purpose', 'steer engineering decisions', 'define contract breach'], ['Owner', 'engineering + product', 'legal / commercial']], minw=420),
    where=['SRE teams', 'Fast-moving product teams', 'Platform teams offering internal SLOs'],
    realworld='Google’s SRE book describes error budgets as the mechanism that lets product teams launch quickly while reliability stays within the agreed SLO, ending the classic conflict between development and operations.',
    pro='Alert on <i>multi-window burn rate</i> (e.g. 2% of the monthly budget in 1 hour AND in 5 minutes) — it pages for real problems quickly without waking people for brief blips.')

def a_comp(k):
    o = t(180, 12, ['In series: all must work', 'In parallel: one is enough', 'Real design: both'][k], 9, 'ink', bold=True)
    if k == 0:
        for i, (n, v) in enumerate([('web', '99.99'), ('app', '99.99'), ('DB', '99.95')]):
            o += box(20 + i * 110, 50, 90, 40, 'blue', rx=5) + t(65 + i * 110, 68, n, 8, 'ink', bold=True) + t(65 + i * 110, 82, v + '%', 7, 'ink2')
            if i < 2:
                o += arrow(110 + i * 110, 70, 130 + i * 110, 70)
        o += t(180, 120, '0.9999 × 0.9999 × 0.9995 = 99.93% (30 min/month)', 8, 'red', bold=True)
    if k == 1:
        for i in range(2):
            o += box(130, 34 + i * 50, 100, 38, 'green', rx=5) + t(180, 57 + i * 50, 'instance 99.5%', 7.6, 'ink', bold=True)
        o += t(180, 140, '1 − (0.005)² = 99.9975% (if failures are independent)', 7.6, 'green', bold=True)
    if k == 2:
        o += box(20, 50, 90, 40, 'violet', rx=5) + t(65, 74, 'ALB', 8, 'ink', bold=True) + arrow(110, 70, 130, 70)
        for i in range(2):
            o += box(130, 32 + i * 46, 90, 36, 'green', rx=5) + t(175, 54 + i * 46, f'app AZ {"ab"[i]}', 7.4, 'ink', bold=True)
        o += arrow(220, 70, 240, 70) + box(240, 50, 100, 40, 'amber', rx=5) + t(290, 74, 'DB Multi-AZ', 7.6, 'ink', bold=True)
        o += t(180, 140, 'redundancy where it is cheap; accept the weakest series link', 7.4, 'ink', bold=True)
    return o
A_COMP = cap([a_comp(k) for k in range(3)], [('In series', 'If a request needs web, app and DB, multiply availabilities: 99.99 × 99.99 ×', '99.95 = 99.93% — lower than the weakest part (our lab calculation).'), ('In parallel', 'Two independent instances of 99.5% each: the service is down only if both', 'fail: 1 − 0.005² = 99.9975%.'), ('Real systems', 'Load balancer → redundant app instances in two AZs → Multi-AZ database:', 'redundancy raises each stage; the series still multiplies.')],
    'Composite availability in action', 'Why chains get weaker and redundancy gets stronger.', 'Composite SLA', 'Animation: three components in series give 99.93%; two parallel instances give 99.9975%; a real design combines both.', 'l6anim')
T6 = vtype(6, 'Composite availability (composite SLA)', 'violet',
    'The <b>composite availability</b> of a system is derived from its components: for components that must all work (in series), multiply their availabilities; for redundant components where any one suffices (in parallel), availability = 1 − the product of their unavailabilities, assuming independent failures.',
    'A train journey with three connections: if each is 99% on time, catching all three is only about 97% likely (series). Having two possible trains for one leg makes that leg far more reliable (parallel).',
    'TiffinGo’s order path — web 99.99%, app 99.99%, database 99.95% — gives 99.93% overall (30 minutes a month), so it cannot promise 99.95% to customers. Two instances of 99.5% each in different AZs give 99.9975% for that tier.',
    'Microsoft Azure Well-Architected guidance on composite SLAs, AWS Well-Architected reliability pillar, Google Cloud reliability guide.',
    '', A_COMP,
    'designing or promising availability for a multi-component system.',
    'failures are correlated (same AZ, same deployment, same dependency) — the parallel formula then overstates availability.',
    plain='A system is only as reliable as the combination of its parts: chaining parts together lowers reliability; having spare copies raises it.',
    how=[('Draw the request path', 'List every component a request must pass.'), ('Series: multiply', 'A = A1 × A2 × … × An.'), ('Parallel: complement', 'A = 1 − (1 − A1)(1 − A2).'), ('Combine', 'Compute parallel groups first, then multiply the series.'), ('Convert to minutes', 'Downtime = (1 − A) × minutes in month.'), ('Challenge independence', 'Shared AZs, code or dependencies break the parallel assumption.')],
    words=[('series', 'one after another; all needed'), ('parallel', 'alternatives; any one is enough'), ('correlated failure', 'several parts failing for the same reason')],
    diff=table(['', 'Series', 'Parallel (redundant)'], [['Formula', 'A1 × A2', '1 − (1−A1)(1−A2)'], ['Effect', 'lower than weakest', 'higher than strongest'], ['Example', 'app → DB', 'two app instances in two AZs']], minw=440),
    where=['Architecture reviews', 'Writing customer SLAs', 'Choosing multi-AZ vs multi-Region'],
    realworld='Microsoft’s Azure architecture guidance explicitly teaches composite SLAs — for example, that a web app depending on a database has a lower combined SLA than either service alone — and recommends redundancy to raise it.',
    pro='The parallel formula assumes independence. Two instances in the same AZ, running the same buggy release, are not independent — real availability will be far below 99.9975%.')

def a_cr(k):
    o = t(180, 12, ['Monthly uptime 99.907%', 'Check eligibility and exclusions', 'Claim → 10% credit'][k], 9, 'ink', bold=True)
    tiers = [('≥ 99.99%', '0%'), ('99.0 – 99.99%', '10%'), ('95.0 – 99.0%', '30%'), ('< 95.0%', '100%')]
    for i, (a, b) in enumerate(tiers):
        hi = i == 1 and k >= 0
        o += box(20, 26 + i * 26, 200, 22, 'amber' if hi else 'card', rx=3) + t(30, 41 + i * 26, a, 7.6, 'ink', anchor='start', bold=hi) + t(210, 41 + i * 26, b, 7.6, 'ink', anchor='end', bold=hi)
    side = [['40 min down in 30 days', '→ 99.907%'], ['were ≥2 AZs affected?', 'your fault? force majeure?'], ['Support case by end of', '2nd billing cycle + logs']][k]
    o += t(290, 50, side[0], 7.2, 'ink', bold=True) + t(290, 64, side[1], 7.2, 'ink')
    o += t(180, 146, ['EC2 Region-level tiers (Nov 2026)', 'single-AZ deployment → only the 99.5% instance-level SLA applies', 'credit = 10% of the affected EC2 charges for that month'][k], 7.2, 'ink', bold=True)
    return o
A_CR = cap([a_cr(k) for k in range(3)], [('Find the tier', '40 minutes of unavailability in a 30-day month = 99.907%, inside the', '99.0–99.99% band of the EC2 Region-level SLA.'), ('Check the fine print', 'Region-level needs instances in ≥2 AZs all unavailable; exclusions include', 'your own software, actions and force majeure.'), ('Claim on time', 'Open a Support case with dates, Region/AZ, resource IDs and logs before the end', 'of the second billing cycle. A valid claim gives a 10% credit.')],
    'Service credits in action', 'From uptime percentage to money off the bill.', 'Credits', 'Animation: EC2 credit tiers; 99.907% falls in the 10% tier; eligibility and exclusions checked; claim filed via support case.', 'l7anim')
T7 = vtype(7, 'Service credits and exclusions', 'red',
    'A <b>service credit</b> is the remedy in most cloud SLAs: a percentage of the monthly charge for the affected service, credited against future bills when measured uptime falls below the commitment, subject to eligibility rules, <b>exclusions</b> (events not covered) and a claim process within a deadline.',
    'A late-delivery coupon from a food app: if the order is late you get ₹50 off your next order — not the cost of the dinner party it spoiled, and only if you claim within the app’s rules.',
    'TiffinGo’s 40-minute outage happened while all instances ran only in ap-south-1a, so the 99.99% Region-level SLA did not apply; under the 99.5% instance-level SLA, 40 minutes (99.907%) was within the commitment — no credit at all.',
    'AWS: credits via AWS Support case; Azure: credit requests through the Azure portal support request; Google Cloud: request via Cloud Billing support. Terms per service SLA.',
    '', A_CR,
    'an incident clearly breaches an SLA you qualified for — claim it; it also documents the incident.',
    'treating credits as insurance — they rarely cover more than a fraction of the bill and never lost revenue.',
    plain='If the cloud company fails to meet its promise, it gives you a discount on a future bill — but only if your setup qualified, the cause was theirs, and you ask in time.',
    how=[('Measure', 'Uptime per the SLA’s own definition of “unavailable”.'), ('Find the tier', 'Map uptime to a credit percentage.'), ('Check eligibility', 'Deployment requirements (e.g. multiple AZs) and exclusions.'), ('Collect evidence', 'Times, resource IDs, logs.'), ('Claim before the deadline', 'Support case with the required subject and data.'), ('Receive credit', 'Applied to future bills of that service.')],
    words=[('exclusion', 'a situation the SLA does not cover'), ('force majeure', 'events beyond anyone’s control, e.g. natural disasters'), ('billing cycle', 'one monthly bill period')],
    diff=table(['', 'Service credit', 'Penalty / damages', 'Insurance'], [['Who pays', 'provider, as bill discount', 'provider, as negotiated', 'insurer'], ['Covers lost revenue', 'no', 'sometimes (negotiated)', 'possibly'], ['Typical in', 'public cloud', 'enterprise contracts', 'business continuity plans']], minw=520),
    where=['Every public-cloud SLA', 'SaaS and hosting contracts'],
    realworld='The EC2 SLA requires credit requests to be received by the end of the second billing cycle after the incident, with dates, times, Region/AZ, resource IDs and request logs; incomplete requests are disqualified, and the exclusions cover factors outside AWS’s reasonable control and the customer’s own software and actions.',
    pro='Credits are usually capped at the affected service’s monthly charge. If your bill is ₹5,000 for EC2 and an outage cost ₹5,00,000 in orders, the SLA gives at most ₹5,000 — build availability, do not buy it from the SLA.')

SUMMARY = table(['#', 'Idea', 'Answers', 'Example'], [
    ['1', 'Service-based SLA', 'what the provider promises everyone', 'EC2 99.99% (multi-AZ)'], ['2', 'Customer / multi-level SLA', 'what is promised to one customer', 'hotel chain contract 99.9%'],
    ['3', 'SLO', 'what we aim for', '99.95% of orders succeed'], ['4', 'SLI', 'what we measure', 'good ÷ all requests'], ['5', 'Error budget', 'how much failure we can afford', '21.6 min/month'],
    ['6', 'Composite availability', 'what the whole system achieves', '99.93% for web→app→DB'], ['7', 'Credits and exclusions', 'what we get back, when', '10% credit if eligible']], minw=600)
CHECK = ('  <h3>Check yourself: which idea is it?</h3>\n' +
    qx('A. “99.95% of /order requests succeed in 30 days” — written by the engineering team.', ['SLA', 'SLO', 'SLI', 'Error budget'], 1, 'An internal objective.') +
    qx('B. “Share of requests answered 2xx within 300 ms.”', ['SLI', 'SLA', 'Exclusion', 'Credit'], 0, 'A measurement.') +
    qx('C. Web 99.99%, app 99.99%, DB 99.95% in series gives about…', ['99.99%', '99.95%', '99.93%', '99.999%'], 2, 'Multiply: ≈ 99.93%.') +
    qx('D. The EC2 99.99% Region-level SLA applies when…', ['you run one instance', 'instances run in two or more AZs', 'you pay upfront', 'you use Spot'], 1, 'Multi-AZ deployments.') +
    qx('E. AWS misses an SLA. What do you normally receive?', ['Cash for lost revenue', 'A service credit on a future bill, if claimed', 'Nothing ever', 'Free hardware'], 1, 'Credits, by claim, within the deadline.'))

TYPES = ('  <p>Seven SLA ideas, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['Why can a 99.99% EC2 SLA give you nothing after a 40-minute outage?', 'Why might two redundant instances deliver far less than 99.9975%?', 'What should page you: one error, or burn rate?'], 'types 7, 6 and 5') + MAP
         + jump(['Service SLA', 'Customer SLA', 'SLO', 'SLI', 'Error budget', 'Composite', 'Credits']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = table(['SLA section', 'What to look for', 'EC2 example (Nov 2026)'], [
    ['Service commitment', 'the percentage, and per what scope', '99.99% Region-level; 99.5% instance-level'], ['Definitions', 'what counts as “unavailable”', 'all instances in ≥2 AZs without external connectivity'],
    ['Measurement period', 'monthly / per billing cycle', 'monthly uptime percentage'], ['Credits', 'tiers and caps', '10% / 30% / 100%'],
    ['Claim process', 'how, where, deadline, evidence', 'Support case by end of 2nd billing cycle, with logs'], ['Exclusions', 'what is never covered', 'outside AWS’s control, your software/actions, suspension']], minw=600)

DEEP = ('  <h3>SLAs of common services (headline commitments, Nov 2026)</h3>\n' + table(['Service', 'AWS', 'Azure', 'Google Cloud'], [
    ['VMs, single instance', 'EC2 99.5%', 'VM 99.9% (premium/ultra disks)', 'Compute Engine 99.9% (99.95% memory-optimized)'], ['VMs across zones', 'EC2 99.99% (≥2 AZs)', '99.99% (2+ availability zones)', '99.99% (multiple zones)'],
    ['Object storage', 'S3 Standard 99.9%', 'Blob Storage 99.9% (LRS, hot)', 'Cloud Storage (multi-region) 99.95%'], ['Managed relational DB', 'RDS Multi-AZ 99.95%', 'Azure SQL up to 99.995%', 'Cloud SQL HA 99.99%'], ['Functions', 'Lambda 99.95%', 'Functions (premium) 99.95%', 'Cloud Run 99.95%']], minw=640) +
    '\n  <p>Treat these as orientation, not contract text: each SLA has conditions (tiers, redundancy options, regions). Always read the current SLA page before promising anything.</p>\n'
    '  <h3>Availability vs durability</h3>\n  <p><b>Availability</b> = can I use it right now? (S3 Standard: 99.9% SLA). <b>Durability</b> = will my data still exist? (S3 is designed for 99.999999999% — eleven nines — durability). A service can be briefly unavailable without losing any data. Exams mix these on purpose.</p>\n'
    '  <h3>RTO and RPO: the disaster-recovery cousins</h3>\n  <ul><li><b>RTO</b> (recovery time objective): how long you may be down after a disaster.</li><li><b>RPO</b> (recovery point objective): how much recent data you may lose.</li><li>Multi-AZ gives small RTO/RPO for AZ failures; multi-Region DR is needed for Region-wide disasters (Lesson 7.2).</li></ul>')

clouds = vendor_tabs('<p><b>AWS:</b> per-service SLAs (aws.amazon.com/legal/service-level-agreements); credits via AWS Support; AWS Health Dashboard for events affecting your account; Route 53 health checks and CloudWatch Synthetics for your own SLIs; CloudWatch Application Signals for SLOs.</p>',
    '<p><b>Azure:</b> “Service Level Agreements for Online Services” document; credit claims via an Azure support request; Azure Service Health; Application Insights availability tests; composite-SLA guidance in the Well-Architected Framework.</p>',
    '<p><b>Google Cloud:</b> per-product SLAs; credits requested through Cloud Billing support; Google Cloud Service Health; Cloud Monitoring uptime checks and SLO monitoring with burn-rate alerts.</p>') + \
    cloud3([['SLA documents', 'per service', 'Online Services SLA', 'per product'], ['Provider incidents', 'AWS Health Dashboard', 'Service Health', 'Service Health'], ['Outside-in checks', 'Route 53 health checks, Synthetics', 'Availability tests', 'Uptime checks'],
            ['SLO tooling', 'CloudWatch Application Signals', 'Azure Monitor / workbooks', 'Service Monitoring SLOs']])

proof = [
    ('Step 1 · The nines, calculated', code('python', 'l54_sla.py', "M = 30 * 24 * 60\nfor a in [99.0, 99.5, 99.9, 99.95, 99.99, 99.999]:\n    print(a, (100 - a) / 100 * M, 'min/month')", sla('== 1)', '== 2)')), 'Pure arithmetic — but the table every architect should know by heart.'),
    ('Step 2 · Composite availability', code('python', 'l54_sla.py', 's = 0.9999 * 0.9999 * 0.9995        # web × app × db (series)\np = 1 - (1 - 0.995) ** 2             # two instances in parallel', sla('== 2)', '== 4)')), 'Chains lose availability; redundancy gains it — if failures are independent.'),
    ('Step 3 · From uptime to service credit (EC2 tiers)', code('python', 'l54_sla.py', 'credit = 0 if up >= 99.99 else (10 if up >= 99.0 else (30 if up >= 95.0 else 100))', sla('== 4)')), 'Tiers from the EC2 Region-level SLA (Nov 2026). The credit applies to the affected EC2 charges only.'),
    ('Step 4 · Measure your own SLI: health check + alarm (emulator)', code('bash', 'terminal', "aws route53 create-health-check --caller-reference tiffingo-$(date +%s) \\\n  --health-check-config Type=HTTPS,FullyQualifiedDomainName=tiffingo.in,ResourcePath=/health,RequestInterval=30,FailureThreshold=3\naws cloudwatch put-metric-alarm --alarm-name tiffingo-down --namespace AWS/Route53 \\\n  --metric-name HealthCheckStatus --dimensions Name=HealthCheckId,Value=$HC \\\n  --statistic Minimum --period 60 --evaluation-periods 1 --threshold 1 --comparison-operator LessThanThreshold", aws('== 1)', '== 3)')), 'An outside-in check every 30 s and an alarm after one unhealthy minute. Output from the moto emulator.')]

prac = practical('Every step has a <b>UI way</b> and a <b>CLI way</b>. Steps 1–2 need only a browser or spreadsheet; steps 3–4 use AWS (<b>CLI outputs from the moto emulator</b>). Route 53 health checks have a small monthly charge on a real account — delete them after practice.', [
    ('1 · Build the “nines” table yourself', uicli(
        ['Open Excel/Google Sheets: column A = 99, 99.5, 99.9, 99.95, 99.99, 99.999.', 'Column B formula: <code>=(100-A2)/100*30*24*60</code> → minutes per month.', 'Add series: <code>=0.9999*0.9999*0.9995</code>; parallel: <code>=1-(1-0.995)^2</code>.'],
        code('bash', 'terminal', 'python3 l54_sla.py        # script in lab/jobs/m5', sla('== 1)', '== 3)')), ui_label='UI way — spreadsheet'),
        'Keep this sheet; you will reuse it in every architecture review.'),
    ('2 · Read a real SLA', uicli(
        ['Search “Amazon Compute Service Level Agreement” and open the AWS page.', 'Find: the commitment, the definition of “Region-Level Unavailable”, the credit table, the claim deadline, the exclusions.', 'Do the same for “Azure SLA Virtual Machines” and “Compute Engine SLA”.'],
        code('bash', 'terminal', 'curl -s https://aws.amazon.com/ec2-sla/ | grep -o -i -E "99\\.99%|99\\.5%" | sort | uniq -c'), ui_label='UI way — browser'),
        'Write a 5-line summary per SLA: commitment, condition, credits, deadline, top exclusion.'),
    ('3 · Create an outside-in health check (your SLI)', uicli(
        ['[[Route 53]] → [[Health checks]] → [[Create health check]].', 'Name <code>tiffingo-health</code>, endpoint by [[Domain name]] <code>tiffingo.in</code>, protocol [[HTTPS]], path <code>/health</code>.', '[[Advanced configuration]]: Request interval [[Standard (30 seconds)]], Failure threshold 3 → [[Next]] → [[Create alarm]]: Yes → SNS topic with your e-mail → [[Create health check]].'],
        code('bash', 'terminal', "aws route53 create-health-check --caller-reference tiffingo-$(date +%s) \\\n  --health-check-config Type=HTTPS,FullyQualifiedDomainName=tiffingo.in,ResourcePath=/health,RequestInterval=30,FailureThreshold=3", aws('== 1)', '== 2)')), ui_label='UI way — AWS Management Console'),
        'Health checkers in several AWS locations probe your site — the user’s view, not the server’s.'),
    ('4 · Alarm when it fails', uicli(
        ['[[CloudWatch]] (Region N. Virginia — Route 53 metrics live there) → [[Alarms]] → [[Create alarm]] → [[Select metric]] → [[Route 53]] → [[Health Check Metrics]] → <code>HealthCheckStatus</code>.', 'Statistic [[Minimum]], period 1 minute, condition [[Lower than]] 1 → notification to an SNS topic → [[Create alarm]].', '[[AWS Health Dashboard]] → [[Your account health]]: provider-side events affecting you.'],
        code('bash', 'terminal', "aws cloudwatch put-metric-alarm --region us-east-1 --alarm-name tiffingo-down \\\n  --namespace AWS/Route53 --metric-name HealthCheckStatus --dimensions Name=HealthCheckId,Value=$HC \\\n  --statistic Minimum --period 60 --evaluation-periods 1 --threshold 1 --comparison-operator LessThanThreshold", aws('== 2)', '== 3)')), ui_label='UI way — AWS Management Console'),
        'Now you have evidence (times, durations) if you ever need to claim a credit.')],
    cleanup='Console: [[Route 53]] → [[Health checks]] → select → [[Delete health check]]; [[CloudWatch]] → [[Alarms]] → select → [[Delete]]. CLI: <code>aws route53 delete-health-check --health-check-id $HC</code>; <code>aws cloudwatch delete-alarms --alarm-names tiffingo-down --region us-east-1</code>.'.replace('[[', '<b>').replace(']]', '</b>'))

mist = mistakes([
    ['Promising customers the provider’s SLA number.', 'Copying 99.99% from the EC2 page.', 'Compute your composite availability; promise below your SLO.'],
    ['Single-AZ design, expecting the 99.99% SLA.', 'Not reading the definition.', 'Run in ≥2 AZs; know which SLA (region vs instance) applies.'],
    ['Treating credits as insurance.', 'Misreading “compensation”.', 'Credits are capped bill discounts; plan resilience and business insurance separately.'],
    ['Not claiming within the deadline.', 'Credits are not automatic.', 'Record incidents with evidence; claim by the end of the second billing cycle.'],
    ['Confusing availability with durability.', 'Both are percentages.', 'Availability = reachable now; durability = data not lost (S3: 11 nines designed).'],
    ['Measuring SLIs only from inside.', 'Server metrics are easy.', 'Add outside-in checks (health checks, synthetics) that see DNS/TLS/CDN problems.'],
    ['Setting a 100% SLO.', 'It sounds ambitious.', 'Impossible and blocks all change; choose a realistic SLO with an error budget.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Service level agreements in cloud computing.'], ['AWS CLF-C02', 'High availability with multiple AZs; AWS Health Dashboard; support plans and response times.'], ['AZ-900', 'SLAs for Azure services, composite SLAs, actions that raise/lower SLAs, service lifecycle (preview has no SLA).'], ['Google Cloud Digital Leader', 'SLAs, SLOs, SLIs and SRE basics.']], minw=520) + '\n  <h3>Exam-style questions with explanations</h3>\n' + \
    qx('1. What does a 99.9% monthly SLA allow?', ['about 4 minutes', 'about 43 minutes', 'about 7 hours', 'no downtime'], 1, '0.1% × 43,200 minutes ≈ 43.2 minutes.') + \
    qx('2. Which raises the composite availability of an app tier?', ['Adding more components in series', 'Deploying redundant instances across availability zones', 'Using a preview service', 'Removing health checks'], 1, 'Parallel redundancy raises availability.') + \
    qx('3. In Azure, a service in public preview typically has…', ['a 99.99% SLA', 'no SLA', 'a 100% SLA', 'a negotiated SLA'], 1, 'Previews are usually excluded from SLAs.') + \
    qx('4. The internal reliability target used by engineering teams is the…', ['SLA', 'SLO', 'SLI', 'RTO'], 1, 'Service level objective.') + \
    qx('5. If AWS misses an SLA commitment, customers typically get…', ['a refund of all costs', 'service credits applied to future bills, upon request', 'free Reserved Instances', 'nothing'], 1, 'Credits per the SLA terms.') + \
    qx('6. Which AWS tool shows events affecting your own resources?', ['AWS Health Dashboard', 'Amazon Inspector', 'AWS Artifact', 'Cost Explorer'], 0, 'Your account health view.')

proj = miniproject('Mini project: an SLO dashboard and a realistic SLA for TiffinGo',
    'Turn reliability into numbers: measure an SLI, set an SLO with an error budget, and write a customer SLA you can actually keep.',
    ['<b>Path:</b> draw TiffinGo’s order path (CloudFront → ALB → app in 2 AZs → RDS Multi-AZ) and write each component’s SLA.',
     '<b>Composite:</b> compute the system availability in a spreadsheet (series + parallel).',
     '<b>SLI:</b> create a Route 53 health check (or a free uptime monitor) on a test endpoint; collect a week of data.',
     '<b>SLO:</b> choose an SLO below the composite; compute the error budget in minutes.',
     '<b>Alerting:</b> CloudWatch alarm on the health check; optionally a burn-rate alarm on ALB 5xx ÷ requests.',
     '<b>SLA draft:</b> write a one-page customer SLA (commitment below the SLO, definition, credit tiers, exclusions, claim process).',
     '<b>Review:</b> list three design changes that would raise availability, with their cost.'],
    'A spreadsheet, a week of SLI data, an SLO with error budget, and a one-page SLA.', 'This lesson + 5.1 (AZs) + 5.3 (scaling) + Module 7 (architecture).')

assemble_v2(HERE, story_h2='Forty minutes on a Friday night', hook_html=hk,
    narration='TiffinGo’s dinner rush stopped for forty minutes. The founder opened the AWS SLA expecting compensation — and learned what an SLA really promises.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Service level agreements (and SLOs and SLIs)',
    formal='A <b>service level agreement (SLA)</b> is a formal, usually contractual commitment between a service provider and a customer that defines the expected level of service — such as monthly uptime — how it is measured, the remedies (typically service credits) if it is not met, and exclusions. It is supported internally by <b>service level objectives (SLOs)</b>, target values for service levels, measured by <b>service level indicators (SLIs)</b>.',
    simple='An SLA is the provider’s written promise about reliability and what you get back if it breaks the promise. SLOs are your own targets; SLIs are the measurements.',
    interview=['“An SLA is a contractual commitment — for example EC2 promises 99.99% monthly uptime for multi-AZ deployments — with service credits if it is missed and a list of exclusions. It limits the provider’s liability; it doesn’t cover my lost revenue.”', '“Internally we set SLOs, stricter than any SLA, measured by SLIs such as the share of successful requests under 300 ms, and manage risk with an error budget.”', '“Composite availability multiplies in series — web, app and DB at 99.99, 99.99 and 99.95 give about 99.93% — so we add redundancy across AZs where it is cheap.”'],
    terms_rows=[('SLA', 'Contractual commitment + remedies.'), ('SLO', 'Internal target.'), ('SLI', 'Measured indicator.'), ('Error budget', '100% − SLO.'), ('Monthly uptime %', '100% − % of minutes unavailable.'), ('Service credit', 'Bill discount if SLA missed.'), ('Exclusion', 'Case not covered.'), ('Composite SLA', 'Availability of combined components.'), ('Availability vs durability', 'Reachable now vs not lost.'), ('RTO / RPO', 'Recovery time / data-loss objectives.')],
    exam='AZ-900 asks how actions affect SLAs (more redundancy raises it; preview services have none) and about composite SLAs. CLF-C02 tests multi-AZ for high availability and the AWS Health Dashboard.',
    picture_h2='The nines, and SLA vs SLO vs SLI', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven SLA ideas, one by one', TYPES)],
    how_h2='One outage, from first error to service credit', how_intro='What happens during and after a provider incident — and what is your job at each step.', how_anim=LIFE,
    parts_h2='How to read any SLA: six sections', parts_html=parts, lv='',
    myth_rows=[('99.99% means AWS will never be down.', 'It allows 4.3 minutes a month and only for qualifying designs.', 'Nines figure.'), ('An SLA pays for my losses.', 'Credits are capped bill discounts.', 'Type 7.'), ('My system’s SLA equals the cloud’s.', 'Components multiply; your design decides.', 'Type 6.')],
    extra_secs=[('deep', 'Deep dive', 'Common service SLAs side by side, availability vs durability, RTO and RPO', DEEP)],
    clouds_html=clouds, proof_h2='Proof: the arithmetic, and your own SLI measurement', proof_intro='Steps 1–3 are calculations with tiers from the EC2 SLA page (Nov 2026); step 4 uses the moto AWS emulator.', proof_steps=proof,
    practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Explain SLA, SLO, SLI and error budget and how they relate.', 'Convert availability percentages to downtime and compute composite availability.', 'Read an SLA’s definitions, credits, exclusions and claim process.', 'Explain service-based, customer-based and multi-level SLAs.', 'Set up an outside-in health check and alarm from the console and the CLI.'],
    next_html='<a href="../05-cloud-pricing-models/">5.5 Cloud pricing models</a>.',
    pre='<b>Before you start:</b> <a href="../01-regions-availability-zones-and-edge-locations/">5.1 (AZs)</a> and <a href="../03-scalability-elasticity-and-cloud-bursting/">5.3</a>.')
