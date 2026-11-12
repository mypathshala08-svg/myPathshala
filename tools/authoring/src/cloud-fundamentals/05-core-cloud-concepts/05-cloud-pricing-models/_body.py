import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def pr(a, b=None): return capsec('l55_prices.txt', a, b)
def aws(a, b=None): return capsec('l55_aws.txt', a, b)
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)


hk = hook('The same m7i.large server in Mumbai can cost ₹6,813 a month — or ₹2,839. Same hardware, same Region. What changes?',
    'Only the <b>pricing model</b>. On-Demand is the full price; a 3-year <b>Savings Plan</b> cuts it by about half; <b>Spot</b> uses spare capacity at a deep discount but can be taken back with a two-minute warning. On top of that, <b>data leaving the cloud</b> is billed per GB, storage gets cheaper in <b>tiers</b>, and <b>licences</b> can double a Windows bill. This lesson uses real Mumbai prices to show every model — and when each one is the right choice.',
    ['Seven pricing models, each with real numbers from AWS’s public price files.', 'Why the cheapest option is often the wrong one.', 'The hidden line on every cloud bill: data transfer out.'])

def story_scene():
    o = t(180, 12, 'One server, three prices (Mumbai, m7i.large, per month)', 8.6, 'ink', bold=True)
    for i, (n, v, tn, s) in enumerate([('On-Demand', '₹6,813', 'red', 'no commitment'), ('Savings Plan 3 yr', '₹3,424', 'amber', 'promise $/hour'), ('Spot', '₹2,839', 'green', 'can be reclaimed')]):
        x = 10 + i * 117
        o += box(x, 24, 106, 92, tn, rx=8) + t(x + 53, 46, n, 7.6, 'ink', bold=True) + t(x + 53, 72, v, 13, 'ink', bold=True) + t(x + 53, 96, s, 6.8, 'ink2')
    o += t(180, 134, 'Same hardware. The price depends on what you promise — and what you risk.', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Three boxes for the same m7i.large server in Mumbai: On-Demand ₹6,813 a month, 3-year Compute Savings Plan ₹3,424, Spot ₹2,839.', story_scene(), 'Pick the model that fits the <tspan font-weight="700" class="s-acc">workload</tspan>, not the lowest number.', h=154)
dialogue = '''R> Sir, our AWS bill doubled after Diwali. Everything is On-Demand. Can we just switch to Spot? It is 58% cheaper!
A> For the nightly report job, yes. For the order API, no — Spot capacity can be taken back with two minutes’ notice.
K> Then how do we save on servers that run all the time?
A> Commit. A Savings Plan says “we will spend $X per hour for 1 or 3 years” and AWS gives a lower rate. Our two base servers are on 24×7 — perfect fit.
R> And the ₹18,000 line called “data transfer”?
A> That is 2 TB of tiffin photos leaving AWS to customers’ phones. Data in is free; data out is charged per GB. A CDN and smaller images fix that. Let’s go model by model.'''

# ------------------------------------------------------------------ picture
def ladderfig():
    o = t(320, 16, 'One m7i.large in Mumbai, running all month (730 h) — ₹ per month by pricing model', 10.5, 'ink', bold=True)
    rows = [('On-Demand', 6813, 0, 'red'), ('Compute Savings Plan 1 yr', 5029, 26, 'amber'), ('EC2 Instance Savings Plan 1 yr', 4499, 34, 'amber'),
            ('Compute Savings Plan 3 yr', 3424, 50, 'blue'), ('EC2 Instance Savings Plan 3 yr', 3098, 55, 'blue'), ('Spot (snapshot)', 2839, 58, 'green')]
    for i, (n, v, s, tn) in enumerate(rows):
        y = 34 + i * 34; w = v / 6813 * 330
        o += t(196, y + 15, n, 8, 'ink', anchor='end', bold=True) + box(204, y, w, 24, tn, rx=4)
        o += t(204 + w + 6, y + 15, f'₹{v:,}' + (f'  (−{s}%)' if s else ''), 8, 'ink', anchor='start', bold=True)
    o += t(320, 252, 'Real prices from AWS public price files, 10 Nov 2026 · Linux · no upfront · ₹88 per US$ assumed · Spot changes every few minutes.', 7.2, 'ink2')
    o += t(320, 268, 'Bigger commitment (longer term, narrower scope) → lower price. Spot is cheapest but can be interrupted.', 7.6, 'ink', bold=True)
    return o
LADDER = bigfig('Horizontal bar chart: On-Demand ₹6,813; Compute Savings Plan 1 year ₹5,029; EC2 Instance Savings Plan 1 year ₹4,499; Compute Savings Plan 3 years ₹3,424; EC2 Instance Savings Plan 3 years ₹3,098; Spot ₹2,839.', ladderfig(), h=280)

def driversfig():
    o = t(320, 16, 'What a cloud bill is made of — the four meters (and what is free)', 11, 'ink', bold=True)
    cols = [('Compute', 'per second / hour', ['EC2, containers, Lambda', 'priced by size × time', 'biggest line for most'], 'blue'),
            ('Storage', 'per GB-month', ['S3, EBS, backups', 'cheaper tiers for cold data', 'snapshots add up'], 'violet'),
            ('Data transfer OUT', 'per GB', ['to the internet: $0.1093/GB', 'between Regions / AZs', 'first 100 GB/month free'], 'red'),
            ('Requests & extras', 'per million / per unit', ['API calls, IPs, load balancers', 'NAT gateway hours + GB', 'support plan %'], 'amber')]
    for i, (n, u, ls, tn) in enumerate(cols):
        x = 12 + i * 156
        o += box(x, 30, 148, 150, tn, rx=8) + t(x + 74, 52, n, 9, 'ink', bold=True) + t(x + 74, 68, u, 7.4, 'ink2')
        for j, l in enumerate(ls):
            o += t(x + 74, 96 + j * 22, l, 7.4, 'ink')
    o += box(12, 194, 616, 46, 'green', rx=8) + t(320, 212, 'Usually free: data transfer IN · data from S3/EC2 to CloudFront · the control plane (creating/describing resources)', 7.8, 'ink', bold=True)
    o += t(320, 230, 'You pay for what you RUN, STORE and SEND OUT — not for what you upload.', 7.6, 'ink2')
    return o
DRIVERS = bigfig('Four boxes: compute priced per second or hour; storage per GB-month; data transfer out per GB with the first 100 GB a month free; requests and extras such as NAT gateways and IP addresses. A green bar: data transfer in and transfer to CloudFront are usually free.', driversfig(), h=250)

picture = ('  <p>Every pricing model in this lesson changes one thing: <b>how much you pay per unit</b>. First see the units — the four meters on any bill:</p>\n' + DRIVERS +
           '\n  <p>Then see how much the <b>same server</b> costs under each model — real Mumbai numbers:</p>\n' + LADDER)

# ------------------------------------------------------------------ how: from usage to bill
RN = {'use': (4, 54, 56, 50, 'server', 'Usage', 'metered'), 'pl': (68, 4, 60, 46, 'dns', 'Price list', 'rate per unit'), 'disc': (68, 104, 60, 46, 'meter', 'Discounts', 'SP / RI / tiers'),
      'bill': (140, 54, 62, 50, 'chart', 'Bill', 'monthly'), 'ce': (214, 4, 64, 46, 'chart', 'Cost Explorer', 'by tag/service'), 'bud': (214, 104, 64, 46, 'shield', 'Budget', 'alert at 80%'), 'act': (290, 54, 66, 50, 'gear', 'Optimise', 'right-size')}
RS = [dict(on=['use'], hot='use', move=(32, 54, 32, 30, ''), head='Step 1 · Every resource is metered', text='Each running instance, GB stored and GB sent out is recorded as a usage line —', text2='EC2 Linux per second (minimum 60 s), S3 per GB-month, transfer per GB.', svc='Usage type examples: APS3-BoxUsage:m7i.large, APS3-DataTransfer-Out-Bytes'),
      dict(on=['use', 'pl'], hot='pl', move=(60, 70, 72, 40, 'rate'), head='Step 2 · The price list gives the rate', text='Each usage type has a public rate in that Region (On-Demand m7i.large in Mumbai:', text2='$0.10605/hour). Prices differ by Region, OS and licence.', svc='AWS Price List API, Pricing Calculator, Azure Retail Prices API, GCP SKUs'),
      dict(on=['use', 'pl', 'disc'], hot='disc', move=(98, 50, 98, 104, 'apply'), head='Step 3 · Discounts are applied automatically', text='Savings Plans / Reserved Instances cover matching usage first; volume tiers and', text2='free-tier allowances reduce the rest. Spot is billed at its own price.', svc='You never “attach” a Savings Plan to a server — billing matches it'),
      dict(on=['use', 'pl', 'disc', 'bill'], hot='bill', move=(128, 127, 150, 90, ''), head='Step 4 · The bill adds it up', text='Usage × rate − discounts + tax (GST in India) = the monthly invoice,', text2='broken down by service, Region and line item.', svc='Billing and Cost Management → Bills; Cost and Usage Report (CUR) for detail'),
      dict(on=['use', 'pl', 'disc', 'bill', 'ce', 'bud'], hot='bud', move=(202, 70, 222, 120, 'watch'), head='Step 5 · Watch it: Cost Explorer and Budgets', text='Cost Explorer shows trends by service and by tag (team, app). A Budget e-mails', text2='you at 80% of the limit — before the month ends, not after.', svc='Tags like project=tiffingo make costs traceable'),
      dict(on=list(RN), hot='act', move=(278, 127, 298, 90, ''), head='Step 6 · Optimise and repeat', text='Right-size idle servers, move steady load to Savings Plans, batch to Spot,', text2='cold data to cheaper tiers, images through a CDN. Then measure again.', svc='This loop is called FinOps')]
BILL = flow_anim('From usage to bill: how cloud pricing is calculated', 'Every pricing model plugs into the same six-step pipeline.', 'Cloud billing', 'Animation: resources metered; price list rate applied; Savings Plan and tier discounts applied; monthly bill; Cost Explorer and Budget alerts; optimisation loop.', RN, RS, hid='billflow')

# ------------------------------------------------------------------ types
def mapfig():
    o = t(320, 16, 'Seven pricing models you must tell apart', 11, 'ink', bold=True)
    items = [('1', 'On-Demand / pay-as-you-go', 'no commitment, full rate', 'red'), ('2', 'Commitment discounts', 'Savings Plans, Reserved', 'amber'), ('3', 'Spot / preemptible', 'spare capacity, interruptible', 'green'),
             ('4', 'Free tier & credits', 'learn and start for free', 'blue'), ('5', 'Tiered & volume pricing', 'more use → lower unit price', 'violet'), ('6', 'Licensing models', 'included, BYOL, subscription', 'amber'), ('7', 'Data transfer pricing', 'out costs, in is free', 'red')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 7.8, 'ink', bold=True) + t(x + 80, y + 54, b, 7, 'ink2')
    o += t(320, 210, '1–3 decide the compute rate · 4–5 change what you pay as usage grows · 6–7 are the lines people forget.', 7.6, 'ink2')
    return o
MAP = bigfig('Map of seven pricing models: 1 On-Demand, 2 commitment discounts, 3 Spot, 4 free tier and credits, 5 tiered and volume pricing, 6 licensing models, 7 data transfer pricing.', mapfig(), h=222)

# type 1 — on-demand
def a_od(k):
    o = t(180, 12, ['Start any time', 'Pay per second', 'Stop: billing stops'][k], 9, 'ink', bold=True)
    on = k < 2
    o += box(20, 30, 110, 70, 'blue' if on else 'card', rx=8) + t(75, 60, 'm7i.large', 8.4, 'ink', bold=True) + t(75, 78, 'running' if on else 'stopped', 7.4, 'green' if on else 'ink2')
    o += box(170, 30, 170, 70, 'card', rx=8) + t(255, 52, 'meter', 7.6, 'ink2') + t(255, 74, ['0 s', '3,600 s → $0.10605', '3,600 s → $0.10605 (frozen)'][k], 9, 'ink', bold=True)
    o += t(180, 130, ['no contract, no upfront — launch in seconds', 'Linux: billed per second, minimum 60 s', 'no more compute charge (EBS disks still billed)'][k], 7.4, 'ink', bold=True)
    return o
A_OD = cap([a_od(k) for k in range(3)], [('Start any time', 'Launch an instance whenever you like; no contract, no upfront payment.', ''), ('Pay per second', 'The meter runs while it runs: Linux EC2 per second (60 s minimum).', 'One hour of m7i.large in Mumbai = $0.10605.'), ('Stop: billing stops', 'Stopped instances stop compute charges; attached disks are still', 'billed per GB-month.')],
    'On-Demand in action', 'Pay only while it runs.', 'On-Demand', 'Animation: an instance starts, the meter counts seconds and dollars, the instance stops and the compute meter freezes.', 'p1anim')
T1 = vtype(1, 'On-Demand (pay-as-you-go)', 'red',
    '<b>On-Demand</b> (pay-as-you-go) pricing charges a fixed published rate for each unit of a resource — per second, hour, GB or request — only while you use it, with <b>no upfront payment and no long-term commitment</b>. It is the default model for every cloud service.',
    'An auto-rickshaw meter: you pay for exactly the distance travelled, at the posted rate, and can get out any time. Convenient — but daily commuting by auto costs more than a monthly bus pass.',
    'TiffinGo’s Diwali surge: 10 extra m7i.large servers for 6 evening hours × 7 days = 420 instance-hours = <b>$44.54 (≈ ₹3,920)</b> On-Demand. Buying those 10 servers for the year would mean paying for 87,600 hours of capacity.',
    'EC2 On-Demand, Azure pay-as-you-go VMs, Google Compute Engine on-demand; also S3, Lambda and most managed services by default.',
    '', A_OD,
    'workloads are new, spiky, short-lived or unpredictable — experiments, peaks, anything you may turn off soon.',
    'servers run 24×7 for months — you are paying the highest rate for a steady load (use type 2).',
    plain='You switch it on, you pay for the time it is on, you switch it off. No contract. It is the most flexible and the most expensive per hour.',
    how=[('Publish', 'The provider publishes a rate per usage type per Region (e.g. Mumbai m7i.large Linux = $0.10605/h).'), ('Meter', 'The service records usage — seconds running, GB stored, requests.'), ('Multiply', 'Usage × rate for the billing period.'), ('Stop', 'When you stop or delete the resource, that meter stops; related meters (disks, IPs) may continue.'), ('Invoice', 'Charged monthly in arrears to your card or invoice.')],
    words=[('pay-as-you-go', 'pay only for what you use, after you use it'), ('per second billing', 'charged by the second instead of rounding up to the hour'), ('in arrears', 'billed after the month ends')],
    diff=table(['', 'On-Demand', 'Savings Plan / Reserved', 'Spot'], [['Commitment', 'none', '1 or 3 years', 'none'], ['Price', 'full', '~26–55% less (our data)', 'up to ~90% less'], ['Can be taken away?', 'no', 'no', 'yes, 2-minute notice'], ['Best for', 'spiky, short, unknown', 'steady 24×7 base', 'fault-tolerant batch']], minw=560),
    where=['Development and test environments', 'Traffic peaks above the committed base', 'New products whose usage is unknown'],
    realworld='AWS moved Linux EC2 from per-hour to <b>per-second billing</b> (60-second minimum) in October 2017; Google Compute Engine also bills per second. A 10-minute test now costs 10 minutes, not an hour.',
    pro='On-Demand is not just “the expensive option” — it is the only model with <b>no capacity risk and no commitment risk</b>. Mature teams deliberately keep 20–30% of compute On-Demand so they can change instance families without stranding commitments.')

# type 2 — commitment
def a_sp(k):
    o = t(180, 12, ['Promise a spend per hour', 'Usage under the promise: discounted', 'Usage above: On-Demand'][k], 9, 'ink', bold=True)
    o += f'<path d="M20,70 L340,70" style="stroke:#E0A100;stroke-width:1.8;stroke-dasharray:5 3"/>' + t(338, 64, 'commitment $/h', 7, 'amber', anchor='end', bold=True)
    hs = [40, 46, 50, 44, 62, 78, 90, 58, 42, 40]
    for i, h in enumerate(hs):
        x = 26 + i * 31; top = 130 - h
        if k >= 1:
            base = min(h, 60)
            o += box(x, 130 - base, 22, base, 'amber', rx=2)
            if k == 2 and h > 60: o += box(x, top, 22, h - 60, 'red', rx=2)
        else:
            o += box(x, top, 22, h, 'card', rx=2)
    o += t(180, 148, ['1 or 3 years, e.g. $0.05/h of compute', 'covered at the Savings Plan rate', 'extra usage billed at the On-Demand rate'][k], 7.4, 'ink', bold=True)
    return o
A_SP = cap([a_sp(k) for k in range(3)], [('Promise a spend per hour', 'You commit to a dollar amount of compute per hour for 1 or 3 years.', ''), ('Usage under the promise', 'Every hour, billing applies the lower Savings Plan rate to matching usage', 'up to the commitment.'), ('Usage above the promise', 'Anything over the commitment is billed On-Demand. Unused commitment is', 'still paid — the risk you accept.')],
    'Savings Plans in action', 'A spending promise, applied hour by hour.', 'Savings Plan', 'Animation: a dashed commitment line; hourly usage bars below the line are covered by the Savings Plan; peaks above the line are billed On-Demand.', 'p2anim')
T2 = vtype(2, 'Commitment discounts: Savings Plans and Reserved Instances', 'amber',
    '<b>Commitment-based pricing</b> gives a lower rate in exchange for committing to a consistent amount of usage for a <b>1- or 3-year term</b>. On AWS: <b>Savings Plans</b> (commit to $/hour of compute) and <b>Reserved Instances</b> (commit to an instance configuration); on Azure: <b>Reservations</b> and savings plans for compute; on Google Cloud: <b>committed use discounts (CUDs)</b>.',
    'A monthly metro pass: you pay less per trip because you promise to travel every day. If you fall sick for a week, the pass is still paid.',
    'TiffinGo runs 2 m7i.large servers 24×7 all year. A 3-year Compute Savings Plan brings each from ₹6,813 to ₹3,424 a month — over 3 years one server costs <b>$1,401 instead of $2,787</b>. The Diwali extras stay On-Demand.',
    'AWS Savings Plans (Compute, EC2 Instance, SageMaker), EC2/RDS Reserved Instances; Azure Reservations and Azure savings plan for compute; Google Cloud resource-based and spend-based CUDs.',
    '', A_SP,
    'part of your usage is steady and predictable for at least a year — size the commitment to the minimum you always run.',
    'usage is uncertain or shrinking, or you might move to another architecture (e.g. serverless) soon — an unused commitment is pure loss.',
    plain='You promise to keep using (and paying for) a certain amount for 1 or 3 years. In return you get a big discount. Longer promise and fewer choices = bigger discount.',
    how=[('Choose the type', 'Compute Savings Plan (any family, size, Region, also Fargate/Lambda) or EC2 Instance Savings Plan (one family in one Region) or a Reserved Instance.'), ('Choose term and payment', '1 or 3 years; All Upfront, Partial Upfront or No Upfront — more upfront = slightly lower rate.'), ('Commit', 'E.g. $0.10/hour of compute. You are billed this every hour of the term.'), ('Automatic matching', 'Each hour billing applies the discount to eligible usage, highest savings first.'), ('Overflow and waste', 'Usage above the commitment is On-Demand; commitment not used that hour is wasted.')],
    words=[('term', 'the length of the promise: 1 or 3 years'), ('upfront', 'paying part or all of it in advance'), ('instance family', 'a group of similar servers, e.g. m7i'), ('utilisation', 'how much of your commitment you actually used')],
    diff=table(['', 'Compute Savings Plan', 'EC2 Instance Savings Plan', 'Standard Reserved Instance'], [['Flexible across', 'family, size, Region, OS, Fargate, Lambda', 'size, OS within one family + Region', 'little (can modify some attributes)'], ['m7i.large 3 yr, Mumbai', '$0.0533/h (−50%)', '$0.04822/h (−55%)', 'similar to EC2 Instance SP'], ['Capacity reservation', 'no', 'no', 'only zonal RIs'], ['Resell unused?', 'no', 'no', 'Standard RIs: RI Marketplace']], minw=600),
    where=['24×7 web and app servers, databases', 'Steady container and Lambda baseline', 'Long-running analytics clusters'],
    realworld='AWS launched Savings Plans in November 2019 and recommends them over Reserved Instances for most compute; AWS states discounts of up to 72% versus On-Demand. In our real Mumbai data, a 3-year EC2 Instance Savings Plan for m7i.large is 55% cheaper.',
    pro='Savings Plans are applied to the usage with the <b>highest discount percentage first</b>, not to a server you choose — so a Compute SP bought for EC2 may end up covering Fargate. And RIs/Savings Plans do <b>not</b> reserve capacity; for guaranteed capacity you need On-Demand Capacity Reservations (paid even when idle).')

# type 3 — spot
def a_spot(k):
    o = t(180, 12, ['Spare capacity, cheap', 'Capacity needed back', 'Two minutes later'][k], 9, 'ink', bold=True)
    o += box(14, 28, 200, 96, 'card', rx=8) + t(114, 42, 'AWS capacity pool (m7i, ap-south-1a)', 7, 'ink2')
    for i in range(8):
        x = 24 + (i % 4) * 46; y = 50 + (i // 4) * 36
        tn = 'blue' if i < 4 else ('green' if (k == 0 or i < 6) else 'card')
        if k == 1 and i >= 4: tn = 'green' if i >= 6 else 'blue'
        if k == 2: tn = 'blue' if i < 6 else ('green' if i == 7 else 'card')
        o += box(x, y, 38, 28, tn, rx=4) + t(x + 19, y + 18, 'OD' if tn == 'blue' else ('Spot' if tn == 'green' else 'free'), 6.6, 'ink')
    o += box(226, 36, 120, 80, ['green', 'amber', 'red'][k], rx=8) + t(286, 60, ['Spot price', '⚠ interruption', 'Spot stopped'][k], 8, 'ink', bold=True)
    o += t(286, 80, ['$0.0442/h (−58%)', 'notice sent', 'job checkpointed'][k], 7.4, 'ink') + t(286, 98, ['', '2-minute warning', 'retry elsewhere'][k], 7, 'ink2')
    o += t(180, 144, ['unused servers are sold at a discount', 'On-Demand customers need the capacity back', 'your app must save state and continue later'][k], 7.4, 'ink', bold=True)
    return o
A_SPOT = cap([a_spot(k) for k in range(3)], [('Spare capacity, cheap', 'Unused servers in a pool are offered as Spot at a large discount.', ''), ('Capacity needed back', 'When On-Demand demand rises, AWS sends a two-minute interruption notice', 'to some Spot instances.'), ('Interrupted', 'The instance is stopped, hibernated or terminated. A well-built job saved', 'its progress and restarts on other Spot capacity.')],
    'Spot in action', 'Cheap because it can be taken back.', 'Spot', 'Animation: a capacity pool with On-Demand and Spot servers; demand rises; a two-minute notice; Spot instances are reclaimed.', 'p3anim')
T3 = vtype(3, 'Spot (preemptible) pricing', 'green',
    '<b>Spot</b> pricing sells a provider’s <b>spare capacity at a steep discount</b> — on AWS up to about 90% off On-Demand — on the condition that the provider can <b>reclaim it</b> when it needs the capacity back, with a short warning (two minutes on AWS, about 30 seconds on Azure and Google Cloud).',
    'Standby airline tickets: the empty seats are sold cheaply at the gate, but if a full-fare passenger turns up, you wait for the next flight.',
    'TiffinGo’s nightly sales report and photo-resizing jobs run on Spot: m7i.large at <b>$0.0442/h vs $0.10605/h</b> (58% less at our snapshot). The jobs checkpoint every few minutes, so an interruption only delays them. The order API never runs on Spot.',
    'EC2 Spot Instances (and Spot in EC2 Auto Scaling / EKS / EMR / Batch), Azure Spot Virtual Machines, Google Cloud Spot VMs (successor to preemptible VMs).',
    '', A_SPOT,
    'work is fault-tolerant, stateless or checkpointed, and flexible in time and instance type — CI builds, batch, big data, rendering, ML training with checkpoints.',
    'the workload must not stop — databases, payment APIs, a single critical server — or when the job cannot restart from a checkpoint.',
    plain='The cloud company sells its empty servers cheaply. The catch: when it needs them back, it gives you a short warning and takes them. Great for work that can pause and continue.',
    how=[('Spare pools', 'Each instance type in each AZ is a separate capacity pool with its own Spot price.'), ('Request', 'You launch Spot (directly, via Auto Scaling or a fleet), optionally setting a maximum price.'), ('Price moves slowly', 'The Spot price changes gradually with long-term supply and demand — you pay the current Spot price, not a bid.'), ('Interruption notice', 'When capacity is needed, AWS sends a 2-minute notice (instance metadata + EventBridge) and often an earlier rebalance recommendation.'), ('Reclaim', 'The instance is terminated, stopped or hibernated; diversified fleets replace it from other pools.')],
    words=[('capacity pool', 'one instance type in one AZ'), ('interruption', 'the provider taking the server back'), ('checkpoint', 'saving progress so work can resume'), ('fleet', 'a group of instances requested together, across types')],
    diff=table(['', 'Spot', 'On-Demand', 'Savings Plan'], [['Price', 'lowest, varies', 'fixed, highest', 'fixed, discounted'], ['Interruptible', 'yes', 'no', 'no'], ['Commitment', 'none', 'none', '1–3 years'], ['Warning before loss', 'AWS 2 min · Azure/GCP ~30 s', '—', '—']], minw=560),
    where=['CI/CD build runners', 'Big-data and EMR/Spark task nodes', 'Rendering, simulations, ML training with checkpoints'],
    realworld='Amazon EMR and EC2 Auto Scaling support <b>mixed instance policies</b>: a base of On-Demand plus Spot spread across several instance types and AZs, so one pool’s interruption removes only a few nodes. AWS’s own guidance is to stay flexible across at least 10 instance types for Spot.',
    pro='Since 2017 AWS Spot is <b>not an auction</b> any more: you pay the current Spot price, which changes gradually. Setting a high max price does not protect you from interruption — capacity, not price, triggers most interruptions. Diversify pools and use the price-capacity-optimized allocation strategy instead.')

# type 4 — free tier
def a_free(k):
    o = t(180, 12, ['Sign up: credits', 'Use services: credits drop', 'Limit reached or 6 months'][k], 9, 'ink', bold=True)
    left = [200, 140, 0][k]
    o += box(20, 34, 320, 30, 'card', rx=6) + box(20, 34, max(2, left / 200 * 320), 30, 'green', rx=6) + t(180, 54, f'credits left: ${left}', 9, 'ink', bold=True)
    o += box(20, 78, 150, 46, 'blue' if k < 2 else 'card', rx=8) + t(95, 98, 'Free plan', 8, 'ink', bold=True) + t(95, 114, ['up to 6 months', 'month 3 of 6', 'ends → upgrade?'][k], 7, 'ink2')
    o += box(190, 78, 150, 46, 'amber' if k == 2 else 'card', rx=8) + t(265, 98, 'Paid plan', 8, 'ink', bold=True) + t(265, 114, ['not yet', 'not yet', 'pay-as-you-go'][k], 7, 'ink2')
    o += t(180, 144, ['$100 at sign-up, up to $100 more for activities', 'EC2, RDS, Lambda… paid from credits', 'no surprise bill on the free plan; upgrade to continue'][k], 7.2, 'ink', bold=True)
    return o
A_FREE = cap([a_free(k) for k in range(3)], [('Sign up', 'A new AWS account gets $100 in credits, plus up to $100 more by completing', 'getting-started activities.'), ('Use services', 'Eligible usage is paid from the credits; always-free offers (e.g. Lambda requests)', 'do not use them.'), ('End of the free plan', 'After 6 months or when credits run out, the free-plan account closes unless', 'you upgrade to a paid plan.')],
    'Free tier in action', 'How a new account learns for free.', 'Free tier', 'Animation: a credit bar falls from $200 to zero; the free plan runs up to six months; then the choice to upgrade to a paid plan.', 'p4anim')
T4 = vtype(4, 'Free tier and credits', 'blue',
    'A <b>free tier</b> lets customers use limited amounts of services at no charge — as <b>credits</b> for new accounts, <b>trial periods</b>, or <b>always-free</b> monthly allowances. Since July 2025, new AWS customers get up to <b>$200 in credits</b> and can choose a <b>free plan</b> for up to 6 months; Azure offers $200 credit for 30 days; Google Cloud offers $300 credit for 90 days, each with always-free products.',
    'Free samples at a sweet shop: a fixed amount to taste, a few items always free with every visit, and beyond that you pay the normal price.',
    'Each TiffinGo intern opens a personal AWS account on the free plan to practise EC2 and S3 from this course; the credits cover the labs, and the free plan cannot run up a bill. Company workloads stay in the paid account.',
    'AWS Free Tier (credits, free plan, always-free offers such as Lambda 1 million requests/month), Azure free account, Google Cloud Free Program ($300 trial + Free Tier).',
    '', A_FREE,
    'learning, prototypes and proofs of concept — and to check the real cost of a design before committing.',
    'you assume “free tier” means a production system is free, or forget resources running after credits or the trial end.',
    plain='New customers get some free money (credits) and some services are free up to a small limit every month. Good for learning. Not for running a business.',
    how=[('Eligibility', 'New accounts (or always-free offers for everyone).'), ('Credits applied first', 'Eligible usage on the bill is paid from credits.'), ('Always-free allowances', 'Some services have a free monthly quota (e.g. Lambda requests) that resets each month.'), ('Guardrails', 'AWS’s free plan blocks some expensive services and closes the account when credits or 6 months end, unless you upgrade.'), ('Alerts', 'Free-tier usage alerts and Budgets warn you near the limits.')],
    words=[('credits', 'money added to your account that pays the bill first'), ('always-free', 'a small allowance that never expires'), ('trial', 'a time-limited free period')],
    diff=table(['', 'AWS', 'Azure', 'Google Cloud'], [['New-customer credit', 'up to $200 (since 15 Jul 2025)', '$200 for 30 days', '$300 for 90 days'], ['Free period', 'free plan up to 6 months', '12 months of popular services', 'trial 90 days'], ['Always-free', 'yes (e.g. Lambda, DynamoDB)', 'yes (55+ services)', 'yes (e.g. e2-micro in some US regions)']], minw=560),
    where=['Students and certification practice', 'Start-up prototypes', 'Evaluating a new service'],
    realworld='On 15 July 2025 AWS replaced the old “12-month free tier” for new accounts with credits ($100 at sign-up, up to $100 more for activities) and a choice between a free plan (up to 6 months) and a paid plan. Accounts created before that keep the legacy free tier.',
    pro='Start-up programmes give far more than the free tier: AWS Activate, Microsoft for Startups and Google for Startups Cloud Program offer credits worth thousands of dollars to eligible start-ups — often the real reason a young company picks its first cloud.')

# type 5 — tiered / volume
def a_tier(k):
    o = t(180, 12, ['Tier 1: first 50 TB', 'Tier 2: next 450 TB', 'Automatic: sustained use'][k], 9, 'ink', bold=True)
    for i, (lab, p, tn) in enumerate([('0–50 TB', '$0.025', 'violet'), ('50–500 TB', '$0.024', 'blue'), ('500 TB +', '$0.023', 'green')]):
        x = 20 + i * 110
        on = (k == 0 and i == 0) or (k == 1 and i <= 1) or k == 2
        o += box(x, 34, 100, 60, tn if on and k < 2 else 'card', rx=6) + t(x + 50, 58, lab, 8, 'ink', bold=True) + t(x + 50, 78, p + '/GB-mo', 7.6, 'ink')
    if k == 2:
        o += box(20, 100, 320, 26, 'amber', rx=6) + t(180, 117, 'GCP: run a VM most of the month → up to 30% off automatically', 7.6, 'ink', bold=True)
    o += t(180, 144, ['S3 Standard, Mumbai — the first 50 TB each month', 'only the GB beyond 50 TB get the lower price', 'no commitment, no action — just more usage'][k], 7.4, 'ink', bold=True)
    return o
A_TIER = cap([a_tier(k) for k in range(3)], [('First tier', 'The first 50 TB stored each month in S3 Standard (Mumbai) cost $0.025 per GB.', ''), ('Next tier', 'Only the usage above 50 TB is charged at $0.024 — like income-tax slabs,', 'in reverse.'), ('Sustained use', 'Google Cloud automatically discounts some VM families that run a large part', 'of the month — up to 30%, no commitment.')],
    'Tiered pricing in action', 'More usage → lower unit price, automatically.', 'Tiered pricing', 'Animation: three S3 price tiers fill one after another; then Google sustained use discounts apply automatically.', 'p5anim')
T5 = vtype(5, 'Tiered, volume and sustained-use pricing', 'violet',
    '<b>Tiered (volume) pricing</b> lowers the unit price as monthly usage passes thresholds — each tier’s rate applies only to the usage within that tier. <b>Sustained-use discounts</b> (Google Cloud) automatically reduce the price of eligible VMs that run for a large part of the month. Neither needs a commitment.',
    'Income-tax slabs, in reverse: the first slab is charged at one rate, only the amount above it at the next — and here each slab gets cheaper.',
    'TiffinGo stores 3 TB of photos: all of it is in the first S3 tier ($0.025/GB-month). Tiers do not help at this size — but moving year-old photos to S3 Glacier Instant Retrieval ($0.005, 80% cheaper) does. That is a <b>storage-class</b> choice, the cousin of tiering.',
    'S3 and Azure Blob storage tiers by volume, data-transfer-out tiers, CloudFront price classes; Google Cloud sustained use discounts (N1, N2, N2D, C2 and others).',
    '', A_TIER,
    'usage is large and growing — the discount arrives automatically; still compare storage classes and commitments.',
    'you expect tiers to make a small workload cheap — at small scale, choosing the right class or model matters far more.',
    plain='The more you use, the cheaper each extra unit becomes — automatically. Big users pay a little less per GB than small users.',
    how=[('Thresholds', 'The price list defines ranges per month (0–50 TB, 50–500 TB, 500 TB+).'), ('Fill in order', 'Usage fills the first tier, then the next.'), ('Rate per tier', 'Each tier’s portion is multiplied by that tier’s rate.'), ('Sum', 'The tier amounts add up to the line item.'), ('Sustained use (GCP)', 'For eligible VMs, the share of the month a VM runs sets an automatic discount, up to 30%.')],
    words=[('tier', 'a usage range with its own price'), ('GB-month', 'one GB stored for one month'), ('storage class', 'a type of storage with a different price and access speed')],
    diff=table(['', 'Tiered / volume', 'Sustained use (GCP)', 'Commitment (type 2)'], [['Needs a promise?', 'no', 'no', 'yes, 1–3 years'], ['Trigger', 'monthly volume', 'running most of the month', 'signing up'], ['Typical saving', 'a few %', 'up to 30%', '~25–72%']], minw=560),
    where=['Object storage at scale', 'Data transfer out', 'Always-on VMs on Google Cloud'],
    realworld='AWS’s Mumbai price file (Nov 2026) lists S3 Standard at $0.025/GB for the first 50 TB, $0.024 for the next 450 TB and $0.023 above 500 TB; Standard-IA is $0.0138 and Glacier Instant Retrieval $0.005.',
    pro='Tier thresholds are usually counted <b>per account (or per consolidated-billing family)</b>, not per bucket. That is one reason companies use AWS Organizations with consolidated billing: usage of all accounts is added together to reach cheaper tiers and share Savings Plans.')

# type 6 — licensing
def a_lic(k):
    o = t(180, 12, ['Licence included', 'Bring your own licence', 'SaaS subscription'][k], 9, 'ink', bold=True)
    if k == 0:
        o += box(30, 34, 130, 70, 'blue', rx=8) + t(95, 60, 'VM hours', 8, 'ink', bold=True) + t(95, 78, 'compute rate', 7, 'ink2')
        o += t(180, 72, '+', 14, 'ink', bold=True) + box(200, 34, 130, 70, 'amber', rx=8) + t(265, 60, 'Windows / SQL', 8, 'ink', bold=True) + t(265, 78, 'licence per hour', 7, 'ink2')
    elif k == 1:
        o += box(30, 34, 130, 70, 'blue', rx=8) + t(95, 60, 'VM hours', 8, 'ink', bold=True) + t(95, 78, 'base (Linux) rate', 7, 'ink2')
        o += t(180, 72, '+', 14, 'ink', bold=True) + box(200, 34, 130, 70, 'green', rx=8) + t(265, 60, 'your licence', 8, 'ink', bold=True) + t(265, 78, 'already owned', 7, 'ink2')
    else:
        o += box(60, 34, 240, 70, 'violet', rx=8) + t(180, 58, 'per user per month', 9, 'ink', bold=True) + t(180, 78, 'software + hosting + updates', 7.4, 'ink2')
    o += t(180, 130, ['easy: the provider bills the licence with the VM', 'cheaper if you already own eligible licences', 'no servers at all — Microsoft 365, Salesforce'][k], 7.4, 'ink', bold=True)
    return o
A_LIC = cap([a_lic(k) for k in range(3)], [('Licence included', 'The hourly price includes the software licence (e.g. Windows Server).', ''), ('Bring your own licence', 'Use licences you already own (where terms allow) and pay only the', 'base compute rate — e.g. Azure Hybrid Benefit.'), ('SaaS subscription', 'For SaaS you pay per user (or per tier) per month; there is no', 'server to price at all.')],
    'Licensing models in action', 'Who pays for the software, and how.', 'Licensing', 'Animation: licence-included VM price as compute plus licence; BYOL as compute plus your own licence; SaaS as a per-user monthly subscription.', 'p6anim')
T6 = vtype(6, 'Licensing models: licence-included, BYOL and subscription', 'amber',
    '<b>Software licensing models</b> decide how commercial software is paid for in the cloud: <b>licence-included</b> (the licence cost is built into the hourly price), <b>bring your own licence (BYOL)</b> (reuse licences you already own, where the vendor’s terms allow), and <b>subscription</b> (per user or per tier per month, typical of SaaS and Marketplace products).',
    'Renting a car with or without a driver: “driver included” costs more per day; if you already have a driver on your payroll, you rent only the car.',
    'TiffinGo’s accounts team needs one Windows server for Tally. Licence-included Windows on EC2 costs noticeably more per hour than the same size on Linux. If they owned eligible licences they could look at BYOL on Dedicated Hosts; for e-mail they simply subscribe to SaaS per user.',
    'AWS licence-included Windows/SQL Server, AWS License Manager, EC2 Dedicated Hosts for BYOL; Azure Hybrid Benefit; Google Cloud sole-tenant nodes for BYOL; AWS/Azure/GCP Marketplace subscriptions.',
    '', A_LIC,
    'commercial software is part of the stack — compare licence-included vs BYOL vs a managed/SaaS alternative before migrating.',
    'you assume on-prem licences can be moved freely — many vendors restrict cloud use or require dedicated hardware.',
    plain='Some software (like Windows or SQL Server) needs a paid licence. You can pay for it inside the cloud price, bring a licence you already bought, or rent finished software per user per month.',
    how=[('Licence-included', 'The usage type includes the licence; billing shows a higher rate (e.g. “Windows” instead of “Linux/UNIX”).'), ('BYOL', 'You prove eligibility (e.g. Software Assurance), launch with the base rate, and track licences (AWS License Manager).'), ('Dedicated hardware if required', 'Some licences are per physical core/socket — they need Dedicated Hosts or sole-tenant nodes.'), ('Subscription', 'SaaS or Marketplace products bill per user, per hour or per tier, often through the cloud bill.'), ('Audit', 'Vendors can audit licence use — keep records.')],
    words=[('licence', 'legal permission to use paid software'), ('BYOL', 'bring your own licence'), ('Software Assurance', 'a Microsoft add-on that gives licence-mobility rights'), ('Marketplace', 'an online store of third-party software inside the cloud console')],
    diff=table(['', 'Licence-included', 'BYOL', 'SaaS subscription'], [['Who pays the vendor', 'cloud provider (passed on)', 'you, already', 'you, monthly'], ['Effort', 'lowest', 'tracking + compliance', 'none (no servers)'], ['Usually cheapest when', 'short-term or small', 'you own many eligible licences', 'standard business apps']], minw=560),
    where=['Windows Server and SQL Server workloads', 'Oracle and other enterprise databases', 'Office, CRM and HR SaaS'],
    realworld='<b>Azure Hybrid Benefit</b> lets customers with eligible Windows Server and SQL Server licences (with Software Assurance or qualifying subscriptions) pay the base, Linux-equivalent compute rate on Azure — Microsoft’s main pricing lever in migrations from on-premises Windows estates.',
    pro='Licence cost can dwarf compute: an SQL Server Enterprise licence-included instance can cost several times the same instance on Linux. Moving the database to an open-source engine (PostgreSQL, Aurora) is often the single largest saving in a migration — a pricing decision disguised as a technology decision.')

# type 7 — data transfer
def a_dt(k):
    o = t(180, 12, ['Data IN: free', 'Data OUT to the internet: per GB', 'Between AZs / Regions'][k], 9, 'ink', bold=True)
    o += box(120, 40, 90, 70, 'blue', rx=8) + t(165, 70, 'AWS Mumbai', 8.4, 'ink', bold=True) + t(165, 88, 'ap-south-1', 7, 'ink2')
    if k == 0:
        o += box(10, 52, 80, 46, 'card', rx=8) + t(50, 79, 'upload', 8, 'ink') + arrow(92, 75, 118, 75) + t(105, 66, '$0', 7.4, 'green', bold=True)
    elif k == 1:
        o += box(266, 52, 84, 46, 'card', rx=8) + t(308, 72, 'customers’', 7.4, 'ink') + t(308, 86, 'phones', 7.4, 'ink') + arrow(212, 75, 264, 75) + t(238, 66, '$0.1093/GB', 7, 'red', bold=True)
    else:
        o += box(250, 28, 100, 40, 'amber', rx=6) + t(300, 44, 'other AZ', 7.4, 'ink', bold=True) + t(300, 59, '$0.01/GB each way', 6.6, 'ink') + arrow(212, 62, 248, 50)
        o += box(250, 82, 100, 40, 'amber', rx=6) + t(300, 98, 'other Region', 7.4, 'ink', bold=True) + t(300, 113, '$0.086/GB', 6.6, 'ink') + arrow(212, 90, 248, 102)
    o += t(180, 144, ['uploading data into the cloud costs nothing', '2 TB a month out ≈ $213 (first 100 GB free)', 'chatty multi-AZ apps pay for cross-AZ traffic'][k], 7.4, 'ink', bold=True)
    return o
A_DT = cap([a_dt(k) for k in range(3)], [('Data in is free', 'Uploading into AWS (ingress) has no transfer charge.', ''), ('Data out is billed', 'Data leaving Mumbai to the internet: $0.1093/GB after the first 100 GB a month', '(free across all Regions).'), ('Inside the cloud too', 'Traffic between AZs ($0.01/GB in each direction for EC2) and between Regions', '($0.086/GB from Mumbai) is billed as well.')],
    'Data transfer in action', 'The meter that surprises everyone.', 'Data transfer', 'Animation: upload into AWS is free; data out to customers is charged per GB; cross-AZ and cross-Region traffic is also charged.', 'p7anim')
T7 = vtype(7, 'Data transfer (egress) pricing', 'red',
    '<b>Data transfer pricing</b> charges per GB for data moving <b>out of</b> a cloud Region — to the internet (<b>egress</b>), to another Region, and in many cases between Availability Zones — while data transfer <b>in</b> (ingress) is generally free. Rates fall in volume tiers and vary by Region.',
    'A hotel where checking in is free but every bag you take out of the building costs a fee — and taking bags between the hotel’s own wings costs a little too.',
    'TiffinGo serves 2 TB of tiffin photos a month straight from EC2 in Mumbai: (2,048 − 100) GB × $0.1093 = <b>$212.92 (≈ ₹18,737) a month</b> — more than three always-on m7i.large servers. Fix: compress images and serve them through CloudFront (origin-to-CloudFront transfer is free).',
    'AWS Data Transfer (internet, inter-Region, inter-AZ), CloudFront; Azure bandwidth pricing and Azure Front Door; Google Cloud network egress (Premium vs Standard tier) and Cloud CDN.',
    '', A_DT,
    'designing any architecture — estimate GB out per month, keep chatty services in the same AZ where safe, and put a CDN in front of public content.',
    'you assume “storage is cheap so the app is cheap” — serving that data out can cost far more than storing it.',
    plain='Putting data into the cloud is free. Taking data out — to users, to another region, sometimes even to another data centre in the same region — is charged by the GB.',
    how=[('Metered at the edge of each boundary', 'Bytes leaving a Region (or crossing AZs) are counted per account.'), ('Direction matters', 'In is free; out to the internet, to another Region, or across AZs is charged.'), ('Free allowance', 'First 100 GB/month out to the internet is free, aggregated across Regions (AWS, since Dec 2021).'), ('Tiers', 'Mumbai: $0.1093/GB for the next 10 TB, then $0.085, $0.082, $0.080.'), ('Cheaper paths', 'S3/EC2 → CloudFront is free; CloudFront then bills its own (usually lower) per-GB rate to viewers.')],
    words=[('egress', 'data leaving the cloud'), ('ingress', 'data coming into the cloud'), ('CDN', 'content delivery network: caches content near users'), ('inter-AZ', 'between two data-centre groups in one Region'), ('NAT gateway', 'a managed gateway that lets private servers reach the internet — charged per hour and per GB')],
    diff=table(['Path (from Mumbai, AWS, Nov 2026)', 'Price'], [['Internet → AWS (in)', 'free'], ['AWS → internet, first 100 GB/month', 'free (all Regions combined)'], ['AWS → internet, next 10 TB', '$0.1093/GB'], ['AWS Mumbai → another AWS Region', '$0.086/GB'], ['EC2 → EC2 in another AZ', '$0.01/GB each direction'], ['S3/EC2 → CloudFront', 'free']], minw=480),
    where=['Video, images and downloads served to users', 'Multi-Region replication and DR', 'Analytics that pull data out of the cloud'],
    realworld='In 2024 AWS, Google Cloud and Microsoft Azure all announced that customers moving their data <b>off</b> the platform can request waived egress fees — a response to customer pressure and the EU Data Act. Day-to-day egress is still billed.',
    pro='Egress is why “multi-cloud” is expensive in practice: an app in one cloud reading a database in another pays internet egress on every query. And NAT gateways add a per-GB processing charge on top — routing S3 traffic through a free <b>S3 gateway endpoint</b> instead of NAT is a classic quick win.')

SUMMARY = table(['#', 'Model', 'Saves money by', 'Main risk', 'TiffinGo uses it for'], [
    ['1', 'On-Demand', 'no waste — pay only while running', 'highest unit price', 'Diwali peaks, experiments'], ['2', 'Savings Plans / Reserved', 'committing for 1–3 years', 'unused commitment', '2 always-on servers'],
    ['3', 'Spot', 'using spare capacity', 'interruption (2 min)', 'nightly reports, image resizing'], ['4', 'Free tier & credits', 'free allowances', 'forgotten resources after it ends', 'intern practice accounts'],
    ['5', 'Tiered / sustained use', 'volume', 'little at small scale', 'S3 (later, at scale)'], ['6', 'Licensing', 'BYOL or switching software', 'licence compliance', 'one Windows server; SaaS mail'],
    ['7', 'Data transfer', 'CDN, compression, same-AZ design', 'surprise egress bills', 'photos via CloudFront']], minw=680)
CHECK = ('  <h3>Check yourself: which model fits?</h3>\n' +
    qx('A. A video-transcoding queue that can restart any job, flexible on instance type.', ['On-Demand', 'Spot', '3-year Savings Plan', 'Free tier'], 1, 'Fault-tolerant, flexible batch → Spot.') +
    qx('B. A production database running 24×7 for the next 3 years.', ['Spot', 'On-Demand', 'Reserved Instance / Savings Plan', 'Free tier'], 2, 'Steady, long-lived → commitment discount.') +
    qx('C. A one-day hackathon prototype.', ['3-year RI', 'On-Demand (or free-tier credits)', 'Dedicated Host', 'BYOL'], 1, 'Short and uncertain → no commitment.') +
    qx('D. The bill’s fastest-growing line is “DataTransfer-Out-Bytes”.', ['Buy RIs', 'Serve content via a CDN and compress it', 'Switch to Spot', 'Use bigger instances'], 1, 'Egress problem → CDN, compression, caching.'))

TYPES = ('  <p>Seven pricing models, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['Does setting a high maximum price stop your Spot instance being interrupted?', 'Which Savings Plan quietly ends up covering your Fargate tasks — and why?', 'Why can a cross-cloud app pay internet egress on every database query?'], 'types 3, 2 and 7') + MAP
         + jump(['On-Demand', 'Commitment', 'Spot', 'Free tier', 'Tiered', 'Licensing', 'Data transfer']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('Unit price', 'The rate per second, GB or request in one Region.', 'Every estimate starts here.', 'AWS Pricing Calculator, Azure Pricing Calculator, Google Cloud Pricing Calculator.'),
    ('Region', 'The same service costs differently per Region.', 'Mumbai vs Hyderabad vs Virginia — compare before you choose (Lesson 5.1).', 'Price pages and the Price List API by Region.'),
    ('Commitment', 'Term (1/3 yr) and payment option (all/partial/no upfront).', 'The biggest lever for steady workloads.', 'Savings Plans, Reservations, CUDs.'),
    ('Tags', 'Labels like project=tiffingo, env=prod.', 'Without tags nobody knows which team spent what.', 'Cost allocation tags, Azure tags, GCP labels.'),
    ('Budgets & alerts', 'Thresholds that notify or act.', 'Catch mistakes in days, not at month end.', 'AWS Budgets, Azure Cost Management budgets, GCP budget alerts.'),
    ('TCO', 'Total cost of ownership, including people and facilities.', 'Compare cloud with on-premises fairly.', 'Migration Evaluator, Azure TCO calculator.')])

DEEP = ('  <h3>TCO: comparing cloud with your own data centre honestly</h3>\n'
    '  <p><b>Total cost of ownership (TCO)</b> adds every cost of running a workload for its life — not only the server price. On-premises: hardware, power and cooling, space, network, licences, staff, maintenance and refresh every 4–5 years, plus the capacity you buy for the peak and leave idle. Cloud: usage, data transfer, support plan, tools and the (smaller) operations team.</p>\n'
    + table(['Cost item', 'On-premises', 'Cloud'], [['Hardware', 'CapEx upfront, refreshed every 4–5 yrs', 'none — inside the hourly price'], ['Capacity for peaks', 'bought and idle most of the year', 'pay for peak hours only (5.3)'], ['Power, cooling, space', 'you pay', 'included'], ['Staff', 'hardware + facilities + ops', 'mostly ops/FinOps'], ['Data transfer', 'ISP bandwidth', 'per GB out (type 7)'], ['Exit cost', 'hardware resale', 'egress + re-platforming']], minw=560) +
    '\n  <p>Our Diwali example in numbers: 10 extra servers for 420 hours cost <b>$44.54</b> On-Demand; owning them means paying for <b>87,600</b> server-hours of capacity a year. That idle capacity is where most cloud savings come from.</p>\n'
    '  <h3>CapEx vs OpEx</h3>\n  <ul><li><b>CapEx</b> (capital expenditure): buy assets upfront and depreciate them — classic data centres.</li><li><b>OpEx</b> (operational expenditure): pay as you consume — cloud. A 3-year all-upfront Savings Plan moves cloud spending back towards CapEx-like behaviour.</li></ul>\n'
    '  <h3>Dedicated options and their price</h3>\n  <p>Dedicated Instances and Dedicated Hosts (Lesson 5.2) cost more because the hardware is not shared; they are bought for compliance or per-core licences (type 6), not to save money. Capacity Reservations guarantee capacity at the On-Demand rate whether you use it or not.</p>\n'
    '  <h3>FinOps in one paragraph</h3>\n  <p><b>FinOps</b> is the practice of making engineering, finance and business teams jointly accountable for cloud spend: <b>inform</b> (tags, dashboards), <b>optimise</b> (right-size, commitments, Spot, storage classes) and <b>operate</b> (budgets, reviews, unit cost such as “₹ per 100 orders”).</p>')

clouds = vendor_tabs('<p><b>AWS:</b> On-Demand, Savings Plans (Compute, EC2 Instance, SageMaker), Reserved Instances (Standard, Convertible), Spot, Dedicated Hosts; Free Tier credits and free plan; AWS Pricing Calculator, Cost Explorer, Budgets, Cost and Usage Report, Compute Optimizer; Price List API.</p>',
    '<p><b>Azure:</b> pay-as-you-go, Reservations (1/3 yr), Azure savings plan for compute, Spot Virtual Machines, Azure Hybrid Benefit (BYOL), Dev/Test pricing; free account; Azure Pricing Calculator, TCO calculator, Cost Management + Billing, Advisor; Retail Prices API.</p>',
    '<p><b>Google Cloud:</b> on-demand, sustained use discounts (automatic), committed use discounts (resource-based and spend-based), Spot VMs, sole-tenant nodes; $300 free trial + Free Tier; Pricing Calculator, Cloud Billing reports, budgets and alerts, Recommender; Cloud Billing Catalog API.</p>') + \
    cloud3([['Pay per use', 'On-Demand', 'pay-as-you-go', 'on-demand'], ['Commitment', 'Savings Plans, RIs', 'Reservations, savings plan', 'CUDs'], ['Spare capacity', 'Spot (2-min notice)', 'Spot VMs (30 s)', 'Spot VMs (30 s)'], ['Automatic discount', '—', '—', 'sustained use'], ['BYOL', 'Dedicated Hosts, License Manager', 'Azure Hybrid Benefit', 'sole-tenant nodes'], ['Estimate', 'Pricing Calculator', 'Pricing + TCO calculators', 'Pricing Calculator'], ['Track', 'Cost Explorer, Budgets', 'Cost Management', 'Billing reports, budgets']])

proof = [
    ('Step 1 · One server, six prices (real Mumbai price files)', code('python', 'l55_prices.py', "base = od['m7i.large']['usd_hour']          # On-Demand, from the AWS Price List API\nfor name, p in plans:                        # Savings Plans offer file + Spot snapshot\n    print(name, p, p * 730 * 88, 1 - p / base)", pr('== 1)', '== 2)')), 'Prices from AWS’s public price files on 10 Nov 2026; ₹88 per US$ and 730 h/month are our assumptions.'),
    ('Step 2 · The Diwali peak, On-Demand', code('python', 'l55_prices.py', 'h = 10 * 7 * 6     # 10 servers × 7 days × 6 evening hours', pr('== 2)', '== 3)')), 'Elasticity (5.3) and On-Demand together: pay for 420 hours, not 87,600.'),
    ('Step 3 · The egress bill', code('python', 'l55_prices.py', '(2048 - 100) * 0.1093     # 2 TB out, first 100 GB free, Mumbai rate', pr('== 3)', '== 4)')), 'Rates from the AWSDataTransfer offer file for ap-south-1 (11 Nov 2026).'),
    ('Step 4 · Tiers and storage classes', code('python', 'l55_prices.py', "for tier in s3_standard_tiers: print(tier)", pr('== 4)', '== 5)')), 'From the AmazonS3 offer file for ap-south-1. Classes save far more than tiers at small scale.'),
    ('Step 5 · Three years of one server', code('python', 'l55_prices.py', 'p * 730 * 36       # hourly rate × hours in 3 years', pr('== 5)')), 'A 3-year commitment halves the compute bill for a steady server.'),
    ('Step 6 · A budget that warns you (emulator)', code('bash', 'terminal', 'aws budgets create-budget --account-id $ACCT --budget file://budget.json \\\n  --notifications-with-subscribers file://notify.json', aws('== 1)')), '<b>Emulator output</b> (moto). On a real account the budget e-mails you at 80% of actual spend.')]

prac = practical('Every step has a <b>UI way</b> and a <b>CLI way</b>. Steps 1–2 cost nothing; step 3’s first two budgets are free on AWS; Cost Explorer API calls cost $0.01 each. Budget CLI output is from the <b>moto emulator</b>.', [
    ('1 · Estimate a monthly bill', uicli(
        ['Open <b>calculator.aws</b> → [[Create estimate]] → search [[Amazon EC2]] → [[Configure]].', 'Region [[Asia Pacific (Mumbai)]], OS Linux, instance <code>m7i.large</code>, quantity 2, usage 100% (24×7).', 'Under pricing strategy compare [[On-Demand]] vs [[Compute Savings Plans]] 3 yr → [[Save and add service]].', 'Add [[Data Transfer]]: 2 TB/month out to the internet → [[Save and view summary]] → [[Share]] to get a link.'],
        code('bash', 'terminal', "# real account: the Price List API lives in us-east-1 (and a few other Regions)\naws pricing get-products --region us-east-1 --service-code AmazonEC2 \\\n  --filters Type=TERM_MATCH,Field=instanceType,Value=m7i.large \\\n            Type=TERM_MATCH,Field=regionCode,Value=ap-south-1 \\\n            Type=TERM_MATCH,Field=operatingSystem,Value=Linux \\\n            Type=TERM_MATCH,Field=tenancy,Value=Shared \\\n            Type=TERM_MATCH,Field=preInstalledSw,Value=NA \\\n            Type=TERM_MATCH,Field=capacitystatus,Value=Used \\\n  --max-results 1 | head -c 600"), ui_label='UI way — AWS Pricing Calculator'),
        'Expected: about $155/month On-Demand for the two servers (2 × $0.10605 × 730) plus about $213 for 2 TB out.'),
    ('2 · Check the Spot price and interruption risk', uicli(
        ['EC2 console → [[Spot Requests]] → [[Pricing history]] → instance type <code>m7i.large</code>, platform Linux → see the price per AZ.', 'Open the [[Spot Instance advisor]] page → Region Mumbai → note the “frequency of interruption” band for m7i.large.', 'Compare with the On-Demand rate from step 1.'],
        code('bash', 'terminal', 'aws ec2 describe-spot-price-history --region ap-south-1 --instance-types m7i.large \\\n  --product-descriptions "Linux/UNIX" --start-time $(date -u +%Y-%m-%dT%H:%M:%S) \\\n  --query "SpotPriceHistory[].[AvailabilityZone,SpotPrice]" --output table'), ui_label='UI way — EC2 console'),
        'Our snapshot on 10 Nov 2026: $0.0442/h vs $0.10605 On-Demand (−58%). The emulator returns placeholder Spot prices, so this step is only meaningful on a real account.'),
    ('3 · Create a budget alert — do this first on any new account', uicli(
        ['[[Billing and Cost Management]] → [[Budgets]] → [[Create budget]] → [[Use a template]] → [[Monthly cost budget]].', 'Name <code>tiffingo-monthly</code>, amount <code>50</code> USD, e-mail <code>owner@tiffingo.in</code> → [[Create budget]].', 'Edit → [[Add an alert threshold]]: 80% of [[Actual]] and 100% of [[Forecasted]].'],
        code('bash', 'terminal', "ACCT=$(aws sts get-caller-identity --query Account --output text)\naws budgets create-budget --account-id $ACCT \\\n  --budget '{\"BudgetName\":\"tiffingo-monthly\",\"BudgetLimit\":{\"Amount\":\"50\",\"Unit\":\"USD\"},\"TimeUnit\":\"MONTHLY\",\"BudgetType\":\"COST\"}' \\\n  --notifications-with-subscribers '[{\"Notification\":{\"NotificationType\":\"ACTUAL\",\"ComparisonOperator\":\"GREATER_THAN\",\"Threshold\":80,\"ThresholdType\":\"PERCENTAGE\"},\"Subscribers\":[{\"SubscriptionType\":\"EMAIL\",\"Address\":\"owner@tiffingo.in\"}]}]'\naws budgets describe-budgets --account-id $ACCT --output text", aws('== 1)', '== 2)')), ui_label='UI way — AWS Management Console'),
        'You now get an e-mail before a forgotten server becomes a big bill.'),
    ('4 · Read your costs and get a Savings Plan recommendation', uicli(
        ['[[Billing and Cost Management]] → [[Cost Explorer]] → last 3 months, [[Group by]] [[Service]], then [[Usage type]] — find the DataTransfer-Out line.', '[[Savings Plans]] → [[Recommendations]] → Compute, 1 year, No upfront, based on the last 30 days → read the estimated savings.', '[[Cost allocation tags]] → activate <code>project</code> so next month you can group by it.'],
        code('bash', 'terminal', "aws ce get-cost-and-usage --time-period Start=2026-10-01,End=2026-11-01 \\\n  --granularity MONTHLY --metrics UnblendedCost --group-by Type=DIMENSION,Key=SERVICE\naws ce get-savings-plans-purchase-recommendation --savings-plans-type COMPUTE_SP \\\n  --term-in-years ONE_YEAR --payment-option NO_UPFRONT --lookback-period-in-days THIRTY_DAYS"), ui_label='UI way — AWS Management Console'),
        'Real account only (Cost Explorer data is not emulated). A brand-new account has little data — revisit after a month.')],
    cleanup='Console: [[Budgets]] → select <code>tiffingo-monthly</code> → [[Actions]] → [[Delete]] (or keep it — the first two budgets are free). CLI: <code>aws budgets delete-budget --account-id $ACCT --budget-name tiffingo-monthly</code>. No other resources were created.'.replace('[[', '<b>').replace(']]', '</b>'))

mist = mistakes([
    ['Running steady 24×7 servers On-Demand for years.', 'Nobody owns the bill.', 'Cover the always-on minimum with a Savings Plan; review monthly.'],
    ['Buying a commitment for the peak.', 'Sizing to the busiest hour.', 'Commit only to the baseline; peaks stay On-Demand or Spot.'],
    ['Putting a database or payment API on Spot.', 'Seeing only the price.', 'Spot only for interruptible, checkpointed work.'],
    ['Ignoring data transfer in estimates.', 'Storage looks cheap.', 'Estimate GB out; use a CDN, compression and same-AZ design.'],
    ['No budget on a new account.', '“It’s only practice.”', 'Create a budget with alerts on day one.'],
    ['Comparing cloud server price with a server’s purchase price.', 'Forgetting power, staff, idle peak capacity.', 'Do a TCO comparison over 3–5 years.'],
    ['Forgetting stopped instances still have disks, IPs and snapshots.', 'Thinking “stopped = free”.', 'Delete unused EBS volumes, Elastic IPs and old snapshots.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Cloud pricing models and economics of cloud computing.'], ['AWS CLF-C02', 'On-Demand, Reserved Instances, Savings Plans, Spot, Dedicated Hosts; Free Tier; Pricing Calculator, Cost Explorer, Budgets, Cost and Usage Report; consolidated billing; tags.'], ['AZ-900', 'Factors affecting cost, Pricing and TCO calculators, Cost Management, tags, reservations, Azure Hybrid Benefit.'], ['Google Cloud Digital Leader', 'CapEx vs OpEx, on-demand vs committed and sustained use discounts, budgets and quotas.']], minw=560) + \
    qx('1. Which model gives the largest discount for interruptible, flexible batch work?', ['On-Demand', 'Spot Instances', 'Dedicated Hosts', 'Reserved Instances'], 1, 'Spot uses spare capacity — up to about 90% off, interruptible.') + \
    qx('2. A steady workload will run for 3 years. Lowest cost with flexibility to change instance family and Region?', ['On-Demand', 'Compute Savings Plan', 'Spot', 'Dedicated Instance'], 1, 'Compute Savings Plans apply across families, sizes and Regions.') + \
    qx('3. Which is usually free?', ['Data transfer out to the internet', 'Data transfer into AWS from the internet', 'Data between Regions', 'NAT gateway processing'], 1, 'Ingress is free.') + \
    qx('4. Which tool alerts you when costs exceed a threshold?', ['AWS Budgets', 'AWS Artifact', 'Amazon Inspector', 'AWS Config'], 0, 'Budgets send alerts on actual or forecasted cost.') + \
    qx('5. In Azure, reusing existing Windows Server licences with Software Assurance is…', ['Azure Reservations', 'Azure Hybrid Benefit', 'Spot VMs', 'Dev/Test pricing'], 1, 'BYOL benefit.') + \
    qx('6. Google Cloud discount that applies automatically when eligible VMs run most of the month:', ['Committed use discount', 'Sustained use discount', 'Spot VM', 'Free trial'], 1, 'No commitment needed.')

proj = miniproject('Mini project: a pricing plan for TiffinGo',
    'Turn a real architecture into a monthly bill — then cut it without losing reliability.',
    ['<b>Inventory:</b> list TiffinGo’s workloads — order API (24×7), Diwali peaks, nightly reports, 3 TB photos, 2 TB/month served out.',
     '<b>Estimate:</b> build an AWS Pricing Calculator estimate, all On-Demand, Mumbai; share the link.',
     '<b>Commit:</b> move the always-on baseline to a Compute Savings Plan (compare 1 vs 3 years, no upfront).',
     '<b>Spot:</b> move the nightly reports to Spot; describe how the job checkpoints and retries.',
     '<b>Storage + egress:</b> put photos behind CloudFront, move photos older than a year to a cheaper class; re-estimate.',
     '<b>Guardrails:</b> create a budget with 80% actual / 100% forecast alerts and a project tag.',
     '<b>Report:</b> a one-page table — before, after, saving %, and the risk each change adds.'],
    'Two calculator links, a budget, and a one-page cost plan with savings and risks.', 'This lesson + 5.1 (Regions) + 5.3 (elasticity) + 5.4 (SLAs).')

assemble_v2(HERE, story_h2='The bill that doubled after Diwali', hook_html=hk,
    narration='After the Diwali rush, TiffinGo’s AWS bill doubled. Everything ran On-Demand, and a mysterious line called “data transfer” had appeared. Time to learn how the cloud actually charges.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Cloud pricing models',
    formal='A <b>cloud pricing model</b> is the set of rules by which a provider charges for resources: the <b>unit</b> (per second, GB-month, GB transferred, request), the <b>rate</b> per Region, and the <b>terms</b> that change that rate — no commitment (On-Demand), a 1- or 3-year commitment (Savings Plans, Reserved Instances, committed use discounts), interruptible spare capacity (Spot), free allowances, volume tiers, licensing options and data transfer charges.',
    simple='How you pay for the cloud: per use, cheaper if you promise long-term use, cheapest if you accept interruptions — plus charges for storage and for data going out.',
    interview=['“Cloud pricing is consumption-based: compute per second or hour, storage per GB-month, data transfer out per GB — ingress is free. On top, there are levers: On-Demand for flexibility, Savings Plans or Reserved Instances for steady 1–3 year usage, and Spot for interruptible work at up to 90% off.”', '“I cover the baseline with commitments, peaks with On-Demand, batch with Spot, and watch the bill with tags, Cost Explorer and Budgets.”'],
    terms_rows=[('On-Demand', 'Full rate, no commitment.'), ('Savings Plan', 'Commit $/hour for 1–3 yr.'), ('Reserved Instance', 'Commit to an instance configuration.'), ('Spot', 'Spare capacity, interruptible.'), ('Free tier', 'Credits and free allowances.'), ('Tiered pricing', 'Cheaper per unit at volume.'), ('BYOL', 'Bring your own licence.'), ('Egress', 'Data out — billed per GB.'), ('TCO', 'Total cost of ownership.'), ('CapEx / OpEx', 'Upfront vs pay-as-you-go spending.')],
    exam='CLF-C02 always has pricing-model questions (On-Demand vs RI/Savings Plans vs Spot vs Dedicated Hosts) and billing tools (Pricing Calculator, Cost Explorer, Budgets). AZ-900 asks about cost factors, calculators and Azure Hybrid Benefit; Digital Leader about CapEx/OpEx and discounts.',
    picture_h2='What you pay for, and how the price changes', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven pricing models, one by one', TYPES)],
    how_h2='From usage to bill', how_intro='Every model above plugs into the same billing pipeline.', how_anim=BILL,
    parts_h2='Six things in every cloud cost decision', parts_html=parts, lv='',
    myth_rows=[('The cloud is always cheaper.', 'Only if you use elasticity, commitments and the right models — lift-and-shift On-Demand can cost more.', 'TCO deep dive.'), ('Spot is just cheaper On-Demand.', 'It can be taken back with two minutes’ warning.', 'Type 3.'), ('Storage is the big cost.', 'Serving data out often costs more than storing it.', 'Type 7.')],
    extra_secs=[('deep', 'Deep dive', 'TCO, CapEx vs OpEx, dedicated options and FinOps', DEEP)],
    clouds_html=clouds, proof_h2='Proof: real Mumbai prices, calculated', proof_intro='Steps 1–5 use AWS’s public price files for ap-south-1 (10–11 Nov 2026); step 6 uses the moto AWS emulator.', proof_steps=proof,
    practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Explain On-Demand, Savings Plans/Reserved, Spot, free tier, tiered, licensing and data transfer pricing.', 'Choose the right model for a workload and justify it.', 'Estimate a monthly bill with the Pricing Calculator and the Price List API.', 'Create a budget alert from the console and the CLI.', 'Explain TCO and CapEx vs OpEx.'],
    next_html='Module 6 — <a href="../../06-cloud-building-blocks/01-compute-products-and-services/">6.1 Compute products and services</a>.',
    pre='<b>Before you start:</b> <a href="../03-scalability-elasticity-and-cloud-bursting/">5.3 Elasticity</a> and <a href="../04-service-level-agreements/">5.4 SLAs</a>.')
