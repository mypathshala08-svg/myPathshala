import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)


hk = hook('TiffinGo’s investors ask: “What if AWS has a bad day?” The data team wants BigQuery. The hospital keeps its data on-premises. Is TiffinGo now hybrid, multi-cloud, or both?',
    'Both — and the words mean different things. <b>Hybrid</b> joins private/on-premises with public cloud. <b>Multi-cloud</b> uses two or more public cloud providers. Most large companies are <b>hybrid multi-cloud</b>. This lesson gives six real architecture patterns (partitioned, analytics, edge, environment, business continuity, cloud bursting) one by one, animates a cross-cloud failover, and on <b>your own</b> accounts you plan non-overlapping networks, keep a copy of data in each cloud and find the portable layer — Kubernetes.',
    ['Multi-cloud is not automatically more reliable — it can double failure points.', 'Why “cloud-agnostic everything” often costs more than it saves.', 'The one design decision that makes hybrid and multi-cloud possible: IP planning.'])

def story_scene():
    o = t(180, 12, 'TiffinGo today: hybrid + multi-cloud', 9, 'ink', bold=True)
    o += box(8, 28, 104, 66, 'violet', rx=8) + t(60, 48, 'Hospital DC', 8, 'ink', bold=True) + t(60, 64, 'private', 7, 'ink2') + t(60, 78, 'diet records', 7, 'ink2')
    o += box(128, 28, 104, 66, 'amber', rx=8) + t(180, 48, 'AWS', 8, 'ink', bold=True) + t(180, 64, 'apps, orders', 7, 'ink2') + t(180, 78, 'Mumbai', 7, 'ink2')
    o += box(248, 28, 104, 66, 'blue', rx=8) + t(300, 48, 'Google Cloud', 8, 'ink', bold=True) + t(300, 64, 'BigQuery', 7, 'ink2') + t(300, 78, 'analytics', 7, 'ink2')
    o += arrow(112, 61, 128, 61) + arrow(232, 61, 248, 61)
    o += t(120, 112, 'hybrid link', 7.2, 'ink2') + t(240, 112, 'multi-cloud link', 7.2, 'ink2')
    return o
scene_svg = scene('Three boxes: hospital data centre (private), AWS (apps and orders), Google Cloud (BigQuery analytics); the first link is hybrid, the second multi-cloud.', story_scene(), 'Hybrid = private + public. Multi-cloud = <tspan font-weight="700" class="s-acc">2+ public providers</tspan>.', h=124)
dialogue = '''R> The investor wants us on two clouds “in case one fails”. Should we run everything on AWS and Azure at the same time?
A> That doubles our work and our failure points. Ask first: which failure are we afraid of? A Region outage? Then a second AWS Region may be enough.
K> But the data team really likes BigQuery.
A> That is a good multi-cloud reason: best service for a job. Analytics on Google, apps on AWS.
R> And the hospital link?
A> That is hybrid. So we are hybrid multi-cloud — on purpose, pattern by pattern.'''

# ------------------------------------------------------------------ picture
def vennfig():
    o = t(320, 16, 'Hybrid, multi-cloud, and both', 11, 'ink', bold=True)
    o += '<ellipse cx="250" cy="110" rx="150" ry="78" class="s-soft-violet" style="stroke:var(--violet);fill-opacity:.55"/>' + '<ellipse cx="390" cy="110" rx="150" ry="78" class="s-soft-blue" style="stroke:var(--blue);fill-opacity:.55"/>'
    o += t(170, 84, 'Hybrid', 9, 'ink', bold=True) + t(170, 102, 'on-prem/private', 7.2, 'ink2') + t(170, 116, '+ ONE public cloud', 7.2, 'ink2') + t(170, 138, 'bank DC + Azure', 7, 'ink')
    o += t(470, 84, 'Multi-cloud', 9, 'ink', bold=True) + t(470, 102, 'TWO+ public clouds', 7.2, 'ink2') + t(470, 116, '(no on-prem needed)', 7.2, 'ink2') + t(470, 138, 'AWS + Google', 7, 'ink')
    o += t(320, 96, 'Hybrid', 8.2, 'ink', bold=True) + t(320, 110, 'multi-cloud', 8.2, 'ink', bold=True) + t(320, 128, 'TiffinGo', 7, 'ink')
    o += t(320, 206, 'The two terms answer different questions, and most large companies are in the middle.', 7.4, 'ink2')
    return o
VENN = bigfig('Two overlapping circles: hybrid (on-premises plus one public cloud) and multi-cloud (two or more public clouds); the overlap is hybrid multi-cloud, where TiffinGo sits.', vennfig(), h=214)

picture = ('  <p>Two words, two different questions:</p>\n' + VENN +
           '\n  <h3>Hybrid vs multi-cloud in one table</h3>\n' + table(['', 'Hybrid cloud', 'Multi-cloud'], [
               ['Combines', 'private/on-prem + public', 'two or more public providers'], ['Main drivers', 'data that must stay, latency, legacy, gradual migration', 'best service per job, risk spread, negotiation, acquisitions, regulation'],
               ['Hardest problem', 'connectivity and latency to on-prem', 'different APIs, IAM, networking and skills per provider'], ['Typical tools', 'VPN/Direct Connect/ExpressRoute, Arc, Outposts, Azure Local', 'Kubernetes, Terraform, central identity, observability, FinOps tools'],
               ['NIST term?', 'yes (hybrid cloud)', 'no — industry term']], minw=620) +
           '\n  <h3>Good and bad reasons for multi-cloud</h3>\n' + table(['Good reasons', 'Weak reasons'], [
               ['A clearly better service for a job (e.g. BigQuery, a specific AI model)', '“To avoid lock-in” with no exit plan or budget'], ['Customer or regulator requires a specific provider', '“For reliability” without testing failover'],
               ['Company acquired another company on a different cloud', 'Every team picks its favourite cloud'], ['Negotiation leverage for very large spend', 'Running the same app active-active on two clouds by default']], minw=560))

# ------------------------------------------------------------------ how: failover
RN = {'u': (4, 54, 50, 50, 'phone', 'Customer', 'app'), 'dns': (66, 54, 60, 50, 'dns', 'DNS', 'health check'), 'aws': (140, 4, 66, 46, 'cloud', 'Primary', 'AWS Mumbai'),
      'az': (140, 104, 66, 46, 'cloud', 'Standby', 'other cloud'), 'rep': (220, 54, 60, 50, 'db', 'Data copy', 'replicated'), 'ops': (294, 54, 62, 50, 'chart', 'Runbook', 'tested')}
RS = [dict(on=['u', 'dns', 'aws'], hot='aws', move=(126, 79, 146, 30, 'orders'), head='Step 1 · Normal day', text='DNS sends customers to the primary stack on AWS Mumbai. A minimal standby stack', text2='sits in another provider, scaled to almost zero.', svc='Pattern: business continuity (active-passive) across providers'),
      dict(on=['aws', 'rep', 'az'], hot='rep', move=(206, 30, 236, 66, 'copy'), head='Step 2 · Data is copied continuously', text='Order data replicates to the standby side every few minutes (database export,', text2='object copies) — this sets the RPO, the data you could lose.', svc='RPO = how much data loss is acceptable'),
      dict(on=['dns', 'aws'], hot='dns', move=(96, 54, 146, 30, 'probe'), head='Step 3 · Health checks fail', text='DNS health checks to the primary fail three times in a row (Region-wide problem).', text2='Alerts page the on-call engineer.', svc='Route 53 / Traffic Manager / Cloud DNS routing policies'),
      dict(on=['dns', 'az', 'ops'], hot='ops', move=(294, 79, 206, 126, 'scale'), head='Step 4 · Runbook scales the standby', text='Automation scales the standby containers and promotes the database copy.', text2='Kubernetes and Terraform make the stacks similar enough.', svc='RTO = how long recovery takes'),
      dict(on=['u', 'dns', 'az'], hot='az', move=(126, 79, 146, 126, 'orders'), head='Step 5 · Traffic moves', text='DNS answers with the standby address; customers reconnect (TTL 60 s). Orders', text2='continue, with a few minutes of data possibly missing.', svc='Keep DNS TTLs low for failover records'),
      dict(on=list(RN), hot='ops', move=None, head='Step 6 · Fail back and learn', text='When the primary recovers, data syncs back, traffic returns and the team writes', text2='a post-incident review. Untested failover is only a hope.', svc='Game days: test failover at least twice a year')]
FAIL = flow_anim('A cross-cloud failover, step by step', 'The business-continuity pattern: primary on one provider, standby on another.', 'Cross-cloud failover', 'Animation: normal traffic to primary; data replicated; health checks fail; runbook scales the standby; DNS moves traffic; fail back and review.', RN, RS, hid='failflow')

# ------------------------------------------------------------------ types
def mapfig():
    o = t(320, 16, 'Six hybrid and multi-cloud architecture patterns', 11, 'ink', bold=True)
    items = [('1', 'Partitioned multi-cloud', 'different apps, different clouds', 'blue'), ('2', 'Analytics hybrid / multi-cloud', 'run apps here, analyse there', 'violet'), ('3', 'Edge hybrid', 'local sites + cloud', 'green'),
             ('4', 'Environment hybrid', 'dev/test in cloud, prod on-prem', 'amber'), ('5', 'Business continuity', 'DR in another place', 'red'), ('6', 'Cloud bursting', 'overflow to cloud', 'green')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 3) * 208; y = 32 + (i // 3) * 84
        o += box(x, y, 198, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 106, y + 34, a, 8.2, 'ink', bold=True) + t(x + 106, y + 54, b, 7, 'ink2')
    o += t(320, 210, 'Pattern names follow Google Cloud’s Architecture Center; AWS and Azure describe the same ideas.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of six patterns: partitioned multi-cloud, analytics hybrid/multi-cloud, edge hybrid, environment hybrid, business continuity, cloud bursting.', mapfig(), h=222)

def row3(k, items, tones, cap_):
    o = ''
    for i, l in enumerate(items):
        on = i <= k
        o += box(20 + i * 112, 34, 100, 74, tones[i] if on else 'card', rx=8)
        for j, w in enumerate(l.split('|')): o += t(70 + i * 112, 60 + j * 14, w, 7.2 if j == 0 else 6.6, 'ink', bold=(j == 0))
        if i < 2: o += arrow(120 + i * 112, 71, 132 + i * 112, 71)
    return o + t(180, 132, cap_, 7.2, 'ink', bold=True)

def mk(t3, items, tones, caps, steps, ttl, intro, panel, aria, hid):
    return cap([t(180, 12, t3[k], 9, 'ink', bold=True) + row3(k, items, tones, caps[k]) for k in range(3)], steps, ttl, intro, panel, aria, hid)

def vt(n, name, tone, d, an, sc, ex, gd, anim, use, avoid, plain, how, words, diff, where, rw, pro):
    return vtype(n, name, tone, d, an, sc, ex, gd, anim, use, avoid, plain=plain, how=how, words=words, diff=diff, where=where, realworld=rw, pro=pro)

A1 = mk(['Split by app', 'Each on its best fit', 'Few links between'], ['apps|web, ERP, ML|independent', 'placement|AWS / Azure / GCP|per app', 'links|APIs only|loose coupling'], ['blue', 'violet', 'green'],
        ['separate applications with clear boundaries', 'each runs on the provider that suits it', 'they talk only through well-defined APIs'],
        [('Split', 'Independent applications with clear boundaries.', ''), ('Place', 'Each app runs on the provider that fits it best.', ''), ('Link', 'Loose coupling through APIs keeps cross-cloud traffic low.', '')],
        'Partitioned multi-cloud in action', 'Different apps, different clouds.', 'Partitioned', 'Animation: split by application; place each on its best cloud; few API links.', 'm1anim')
T1 = vt(1, 'Partitioned multi-cloud', 'blue',
    'In a <b>partitioned multi-cloud</b> architecture, different applications or components run on different public cloud providers according to which provider best fits each workload, with loose coupling (APIs, events) between them.',
    'Shopping vegetables at the market, medicines at the pharmacy and electronics online — each from where it is best, linked only by your shopping list.',
    'TiffinGo’s customer app runs on AWS; its staff email and documents run on Microsoft 365 with Entra ID; the ML recommendation model is trained on Google Cloud.',
    'Any combination of AWS, Azure, Google Cloud, Oracle Cloud; integration through APIs, event buses, central identity (Entra ID, Okta).', '', A1,
    'applications are clearly separable and each has a strong reason to be on a specific provider.',
    'one application is split across providers with chatty traffic — latency and egress charges explode.',
    'Different apps of the same company running on different cloud companies, each where it fits best.',
    [('Map apps', 'Boundaries and data flows.'), ('Choose provider', 'Per app, with reasons.'), ('Connect', 'APIs/events, private links where needed.'), ('Identity', 'One IdP federated to all clouds.'), ('Govern', 'Common tagging, security baseline, FinOps.')],
    [('loose coupling', 'parts depend on each other only through simple interfaces'), ('IdP', 'identity provider — the system that logs users in'), ('egress', 'data leaving a cloud, usually charged')],
    table(['', 'Partitioned', 'Active-active across clouds'], [['Complexity', 'medium', 'very high'], ['Egress cost', 'low', 'high'], ['Reason', 'best fit per app', 'maximum availability']], minw=440),
    ['Enterprises after acquisitions', 'Companies using M365 + AWS', 'Teams with provider-specific needs'],
    'Many enterprises are “multi-cloud by accident”: Microsoft 365 for productivity, AWS or Google Cloud for products — partitioned by default.',
    'Watch egress: every GB that crosses providers is billed on the way out (Lesson 5.5) — partition along data boundaries, not team boundaries.')

A2 = mk(['Apps produce data', 'Copy to analytics', 'Insights flow back'], ['apps|orders, logs|AWS / on-prem', 'pipeline|batch or stream|to analytics cloud', 'analytics|BigQuery etc.|dashboards, ML'], ['amber', 'blue', 'violet'],
        ['transaction systems stay where they are', 'data is extracted and loaded into an analytics platform', 'reports and models are used by the business'],
        [('Produce', 'Transaction systems run on-prem or in one cloud.', ''), ('Move', 'Data is copied (batch/stream) to the analytics environment.', ''), ('Analyse', 'Analytics and ML run there; results flow back.', '')],
        'Analytics hybrid / multi-cloud in action', 'Run here, analyse there.', 'Analytics pattern', 'Animation: apps produce data; data copied to analytics cloud; insights flow back.', 'm2anim')
T2 = vt(2, 'Analytics hybrid / multi-cloud', 'violet',
    'The <b>analytics hybrid and multi-cloud</b> pattern keeps transactional workloads in their existing environment (on-premises or another cloud) while extracting their data into a cloud analytics platform for warehousing, reporting and machine learning.',
    'Cooking in your own kitchen but sending samples to a food-testing lab — the lab has better equipment for analysis.',
    'Every night TiffinGo exports order data from Amazon RDS to Cloud Storage and loads it into BigQuery for demand forecasting; forecasts return to the AWS app through an API.',
    'BigQuery, Snowflake, Databricks, Amazon Redshift, Azure Synapse / Microsoft Fabric; transfer tools: BigQuery Data Transfer Service, Storage Transfer Service, AWS DataSync, Azure Data Factory.',
    'Big Data pipelines are covered in the Big Data track (Hadoop, Spark, Hive, Kafka).', A2,
    'a different provider’s analytics service is clearly better or the data team already uses it.',
    'data volumes are huge and change constantly — egress costs and freshness may favour analytics in the same cloud.',
    'Running your apps in one place and copying their data to another cloud that is better at analysing it.',
    [('Extract', 'Exports, CDC streams.'), ('Transfer', 'Managed transfer services.'), ('Load', 'Warehouse / lakehouse.'), ('Model', 'BI, ML.'), ('Return', 'Results via API/reverse ETL.')],
    [('CDC', 'change data capture — streaming only the changes'), ('warehouse', 'database built for analysis'), ('reverse ETL', 'sending analytics results back to operational apps')],
    table(['', 'Analytics pattern', 'Partitioned'], [['Data flow', 'one-way bulk copy', 'API calls'], ['Latency need', 'minutes–hours', 'real time'], ['Main cost', 'egress per GB', 'per request']], minw=440),
    ['Retail and e-commerce analytics', 'Banks analysing on-prem data', 'Data science teams'],
    'BigQuery Omni lets queries run on data stored in AWS S3 or Azure Storage without moving it first — a sign of how common this pattern is.',
    'Move aggregated or compressed data where possible; a 10× smaller Parquet export means 10× less egress.')

A3 = mk(['Local sites', 'Local processing', 'Cloud for the rest'], ['sites|kitchens, factories|shops', 'edge|local servers|work offline', 'cloud|central apps|analytics, updates'], ['green', 'amber', 'blue'],
        ['many locations with local equipment', 'time-critical work runs on site, even offline', 'the cloud collects data, manages and updates the sites'],
        [('Sites', 'Many locations with local devices.', ''), ('Edge', 'Time-critical work runs locally and survives link failures.', ''), ('Cloud', 'Central management, analytics and updates.', '')],
        'Edge hybrid in action', 'Local where needed, cloud for the rest.', 'Edge hybrid', 'Animation: local sites; local processing; cloud for management and analytics.', 'm3anim')
T3 = vt(3, 'Edge hybrid', 'green',
    'The <b>edge hybrid</b> pattern runs time- and business-critical workloads locally at the edge of the network (stores, factories, kitchens) so they keep working with poor or no connectivity, while using the public cloud for everything else — central management, data aggregation, analytics and updates.',
    'Each dhaba cooks independently even if the phone lines are down, then sends the day’s accounts to head office when the line returns.',
    'Each TiffinGo kitchen runs its order screen and printers on a small local server; it keeps working during internet cuts and syncs to AWS when back online.',
    'AWS Outposts servers, IoT Greengrass; Azure Local, Azure IoT Edge, Arc; Google Distributed Cloud connected; plus lightweight Kubernetes (K3s) at sites.',
    'Edge vs fog vs grid is Lesson 3.4.', A3,
    'sites need low latency to local equipment or must survive network outages.',
    'all sites have reliable connectivity and nothing is time-critical — run centrally.',
    'Running the urgent work at each local site and using the cloud for central control and analysis.',
    [('Classify', 'What must work offline.'), ('Deploy', 'Same packages to all sites.'), ('Sync', 'Queue and forward when online.'), ('Manage', 'Central fleet management.'), ('Secure', 'Physical and device security.')],
    [('edge', 'computing close to where data is created'), ('store-and-forward', 'save locally, send later'), ('fleet', 'many identical devices or sites managed together')],
    table(['', 'Edge hybrid', 'Pure cloud'], [['Works offline', 'yes', 'no'], ['Latency to devices', 'very low', 'network-dependent'], ['Ops effort', 'higher (many sites)', 'lower']], minw=440),
    ['Retail stores', 'Factories and warehouses', 'Restaurants and kitchens'],
    'Large retailers run point-of-sale and in-store systems at each store so checkouts work during network outages, syncing to central cloud systems.',
    'Treat sites as cattle, not pets: identical images, remote updates and automatic rollback — manual fixes at 200 kitchens do not scale.')

A4 = mk(['Dev/test in cloud', 'Same tooling', 'Prod on-prem'], ['dev/test|cloud|fast, cheap', 'tooling|containers, IaC|same images', 'production|on-prem|rules, legacy'], ['blue', 'amber', 'violet'],
        ['developers get fast, disposable environments in the cloud', 'the same containers and IaC run everywhere', 'production stays on-premises (for now)'],
        [('Dev/test', 'Development and testing run in the cloud.', ''), ('Same tools', 'Containers and IaC keep environments identical.', ''), ('Prod', 'Production stays on-premises for rules or legacy reasons.', '')],
        'Environment hybrid in action', 'Build in the cloud, run at home.', 'Environment hybrid', 'Animation: dev/test in the cloud; same tooling; production on-premises.', 'm4anim')
T4 = vt(4, 'Environment hybrid', 'amber',
    'The <b>environment hybrid</b> pattern runs development, testing (and sometimes staging) environments in the public cloud while keeping production in the existing data centre, using consistent tooling so code behaves the same in both.',
    'Practising a dance in a rented hall that has mirrors and space, then performing on the home stage.',
    'The hospital lets TiffinGo developers test the diet-planner integration on AWS with synthetic data; the production integration runs in the hospital’s data centre.',
    'Container platforms (OpenShift, EKS Anywhere, AKS on Azure Local, GKE Enterprise), Terraform, CI/CD pipelines; dev environments such as Codespaces and Cloud Workstations.', '', A4,
    'production cannot move yet but teams need fast, disposable environments.',
    'environments differ (different OS, DB versions) — “works in test” bugs appear in production.',
    'Building and testing software in the cloud while the live system still runs in the company’s own data centre.',
    [('Standardise', 'Containers / images.'), ('Automate', 'IaC creates environments.'), ('Data', 'Synthetic or masked test data.'), ('Pipeline', 'Same CI/CD to both.'), ('Promote', 'Release to on-prem production.')],
    [('staging', 'final test environment before production'), ('synthetic data', 'realistic but fake data'), ('masking', 'hiding sensitive values in test copies')],
    table(['', 'Environment hybrid', 'Cloud bursting'], [['What is in cloud', 'dev/test', 'overflow production load'], ['Prod location', 'on-prem', 'on-prem + cloud at peaks'], ['Main risk', 'environment drift', 'latency, data sync']], minw=440),
    ['Regulated industries', 'Early cloud adoption', 'Large development teams'],
    'Often the first step of a migration: teams learn cloud tools on non-production workloads before moving production.',
    'Never copy real patient or customer data to test without masking — it breaks the rule that kept production on-premises in the first place.')

A5 = mk(['Primary running', 'Copy data elsewhere', 'Fail over'], ['primary|on-prem or cloud A|serving', 'replicate|backups, DB copy|to site B', 'failover|DNS switch|RTO / RPO'], ['green', 'blue', 'red'],
        ['the primary environment serves users', 'data is replicated to another place (Region, provider or on-prem)', 'on disaster, a runbook moves users to the copy'],
        [('Primary', 'The main environment serves users.', ''), ('Replicate', 'Backups and database copies go to a second site.', ''), ('Fail over', 'A tested runbook switches users within the RTO.', '')],
        'Business continuity in action', 'A second place to stand.', 'Business continuity', 'Animation: primary running; data copied elsewhere; failover.', 'm5anim')
T5 = vt(5, 'Business continuity (DR) hybrid / multi-cloud', 'red',
    'The <b>business continuity</b> pattern keeps a recovery environment — backups, a pilot light, a warm standby or a full active-active copy — in a different location (another Region, another provider, or the cloud for an on-premises primary), so that the business can recover within its RTO and RPO after a disaster.',
    'Keeping a spare house key with a trusted neighbour in another street — useless if never tested, priceless when needed.',
    'The hospital backs up diet records to the cloud nightly (hybrid DR); TiffinGo keeps a minimal standby of its order system on a second provider (animation above).',
    'AWS Elastic Disaster Recovery, AWS Backup; Azure Site Recovery, Azure Backup; Google Backup and DR Service; cross-provider tools such as Veeam, Commvault.',
    'RTO/RPO and DR tiers return in Module 8.', A5,
    'the business impact of an outage justifies the cost and the failover is tested regularly.',
    'a second Region of the same provider already meets the risk at a fraction of the effort.',
    'Keeping a ready copy of your systems and data in another place so you can switch over after a disaster.',
    [('Set targets', 'RTO and RPO per system.'), ('Choose tier', 'Backup → pilot light → warm → active-active.'), ('Replicate', 'Data continuously or on schedule.'), ('Automate', 'Runbooks / IaC.'), ('Test', 'Game days twice a year.')],
    [('RTO', 'recovery time objective — how long you can be down'), ('RPO', 'recovery point objective — how much data you can lose'), ('pilot light', 'minimal copy kept running, scaled up on disaster')],
    table(['', 'Same provider, other Region', 'Other provider'], [['Effort', 'low–medium', 'high'], ['Protects against', 'Region failure', 'provider-wide failure, account issues'], ['Tooling', 'native, same APIs', 'portable layer needed']], minw=460),
    ['Banks and payments', 'Hospitals', 'Any business with strict uptime needs'],
    'Regulators such as RBI expect regulated entities to have tested business continuity and DR plans for critical IT systems — the test results, not the plan document, are what auditors ask for.',
    'Provider-wide outages are rare; account lockout, ransomware and human error are common. Immutable backups in a separate account are often a better first step than a second cloud.')

A6 = mk(['Normal load', 'Peak arrives', 'Burst to cloud'], ['on-prem|fixed capacity|80% used', 'peak|festival demand|capacity full', 'burst|extra in cloud|then scale back'], ['violet', 'amber', 'green'],
        ['the private environment handles normal load', 'a peak exceeds what was bought', 'extra capacity starts in the cloud and stops after the peak'],
        [('Normal', 'Private capacity handles everyday load.', ''), ('Peak', 'Demand exceeds owned capacity.', ''), ('Burst', 'Overflow runs in the public cloud, then scales back.', '')],
        'Cloud bursting in action', 'Rent the peak.', 'Cloud bursting', 'Animation: normal load on-prem; peak arrives; overflow bursts to cloud.', 'm6anim')
T6 = vt(6, 'Cloud bursting', 'green',
    '<b>Cloud bursting</b> is a hybrid pattern in which an application normally runs in a private environment and, when demand exceeds its capacity, the excess load is served by additional resources in a public cloud, which are released when demand falls.',
    'A wedding family with a small house renting a banquet hall only for the reception night.',
    'The hospital’s nightly batch that recalculates diet plans for 50,000 patients runs on-prem; during monsoon admissions peaks, extra workers start in the cloud with masked data.',
    'Batch and HPC schedulers that span on-prem and cloud (Slurm, AWS Batch, Azure Batch, Google Batch), Kubernetes cluster autoscaling across environments, VMware HCX.',
    'Elasticity vs scalability is Lesson 5.3.', A6,
    'workloads are stateless or batch, data can be moved or masked, and peaks are short.',
    'the app needs low-latency access to a big on-prem database — the WAN link becomes the bottleneck.',
    'Using your own servers normally and renting extra cloud servers only when demand is too high.',
    [('Monitor', 'Capacity thresholds.'), ('Trigger', 'Queue length / utilisation.'), ('Launch', 'Pre-built images in the cloud.'), ('Route', 'Load balancer or scheduler sends overflow.'), ('Release', 'Scale cloud to zero after peak.')],
    [('burst', 'temporary overflow to extra capacity'), ('stateless', 'no local data between requests'), ('WAN', 'wide-area network link between sites')],
    table(['', 'Cloud bursting', 'Edge hybrid'], [['Cloud role', 'overflow capacity', 'central management'], ['Direction', 'on-prem → cloud at peaks', 'cloud → many sites'], ['Best for', 'batch, stateless', 'local, offline-critical']], minw=440),
    ['Research and HPC', 'Rendering and media', 'Seasonal batch processing'],
    'Bursting is talked about more than it is built: data gravity and network latency make it practical mainly for batch and HPC jobs, which is where most real examples come from.',
    'Bursting needs the cloud side pre-built and tested (images, quotas, network) — quotas for 500 vCPUs requested on the day of the peak arrive too late.')

SUMMARY = table(['#', 'Pattern', 'Hybrid or multi-cloud', 'Main reason', 'TiffinGo example'], [
    ['1', 'Partitioned', 'multi-cloud', 'best fit per app', 'apps on AWS, M365, ML on Google'], ['2', 'Analytics', 'both', 'better analytics platform', 'RDS → BigQuery'], ['3', 'Edge hybrid', 'hybrid', 'offline, low latency', 'kitchen order screens'],
    ['4', 'Environment hybrid', 'hybrid', 'fast dev/test', 'hospital integration tests'], ['5', 'Business continuity', 'both', 'disaster recovery', 'standby on second provider'], ['6', 'Cloud bursting', 'hybrid', 'peak capacity', 'monsoon diet batch']], minw=620)
CHECK = ('  <h3>Check yourself: which pattern?</h3>\n' +
    qx('A. Stores keep billing during internet cuts and sync later.', ['Edge hybrid', 'Partitioned', 'Analytics', 'Bursting'], 0, 'Local + cloud.') +
    qx('B. On-prem render farm adds cloud servers for one week of a film deadline.', ['Environment hybrid', 'Cloud bursting', 'Business continuity', 'Partitioned'], 1, 'Overflow.') +
    qx('C. Transactions on AWS, warehouse in BigQuery.', ['Analytics multi-cloud', 'Edge hybrid', 'Bursting', 'Environment hybrid'], 0, 'Analytics.') +
    qx('D. Backups of an on-prem system kept in Azure for recovery.', ['Business continuity hybrid', 'Partitioned', 'Bursting', 'Edge'], 0, 'DR.'))

TYPES = ('  <p>Six real patterns, each in the same format: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['Why is “multi-cloud for reliability” often a weak reason?', 'What makes cloud bursting hard for database-heavy apps?', 'Which pattern is often the first step of a migration?'], 'types 5, 6 and 4') + MAP
         + jump(['Partitioned', 'Analytics', 'Edge', 'Environment', 'Continuity', 'Bursting']) + T1 + T2 + T3 + T4 + T5 + T6
         + '\n  <h3 style="margin-top:34px">All six side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('Identity federation', 'One identity provider trusted by every cloud and on-prem.', 'One login, one off-boarding, consistent roles.', 'Entra ID / Okta → AWS IAM Identity Center, Google Cloud.'),
    ('Network & IP plan', 'Non-overlapping ranges, private links.', 'Without it, environments cannot be connected.', 'VPN, Direct Connect, ExpressRoute, Interconnect, cross-cloud interconnects.'),
    ('Portable runtime', 'Containers / Kubernetes.', 'Same app package everywhere.', 'EKS, AKS, GKE; OpenShift.'),
    ('Infrastructure as code', 'Same tool across providers.', 'Repeatable environments.', 'Terraform/OpenTofu, Pulumi.'),
    ('Observability', 'Logs, metrics, traces in one place.', 'One view during incidents.', 'OpenTelemetry, Grafana, Datadog.'),
    ('FinOps & governance', 'Costs and policies across providers.', 'Avoid surprises and drift.', 'FOCUS billing format, tags/labels, policy as code.')])

DEEP = ('  <h3>Lock-in: what it really is</h3>\n  <p>Lock-in is the <b>cost of leaving</b>: rewriting code for different APIs, moving data (egress + time), retraining people, and contract terms. Avoiding every provider-specific service is also costly — you give up managed services and build them yourself. A balanced approach: use managed services freely, keep data in open formats, keep business logic in containers, document an exit plan for critical systems.</p>\n'
    '  <h3>Networking between clouds</h3>\n  <p>Options, from simplest: public internet with TLS; site-to-site VPN between clouds; partner interconnects through colocation exchanges; managed cross-cloud links (for example Google Cross-Cloud Interconnect to AWS, Azure, Oracle). Each adds cost but lowers latency and jitter.</p>\n'
    '  <h3>Common multi-cloud control planes</h3>\n' + table(['Product', 'From', 'What it manages'], [['Azure Arc', 'Microsoft', 'servers, Kubernetes, data services anywhere, from Azure'], ['GKE Enterprise (fleets, attached clusters)', 'Google', 'Kubernetes clusters on Google, AWS, Azure, on-prem'], ['EKS Anywhere / EKS Hybrid Nodes', 'AWS', 'Kubernetes on your own infrastructure'], ['Systems Manager hybrid nodes', 'AWS', 'on-prem and other-cloud servers'], ['Terraform / OpenTofu', 'HashiCorp / community', 'infrastructure on all providers']], minw=560) +
    '\n  <h3>Data gravity</h3>\n  <p>Large data sets attract applications and services to wherever they live, because moving data is slow and costly. Design rule: put compute next to the biggest data, move small results instead of raw data.</p>')

clouds = vendor_tabs('<p><b>AWS:</b> hybrid via Outposts, Direct Connect, Site-to-Site VPN, Systems Manager hybrid nodes, EKS Anywhere/Hybrid Nodes; multi-cloud identity via IAM Identity Center with external IdPs; Elastic Disaster Recovery.</p>',
    '<p><b>Azure:</b> Azure Arc (servers, Kubernetes, data services anywhere), Azure Local, ExpressRoute; Entra ID as a common IdP for other clouds; Site Recovery; Microsoft Fabric for analytics across sources.</p>',
    '<p><b>Google Cloud:</b> GKE Enterprise fleets and attached clusters (EKS, AKS), Google Distributed Cloud, Cross-Cloud Interconnect, BigQuery Omni for data in AWS/Azure, Backup and DR Service.</p>') + \
    cloud3([['Manage other environments', 'Systems Manager hybrid nodes', 'Azure Arc', 'GKE Enterprise fleets'], ['Kubernetes outside the cloud', 'EKS Anywhere / Hybrid Nodes', 'AKS on Azure Local / Arc', 'GKE attached clusters'], ['Dedicated link', 'Direct Connect', 'ExpressRoute', 'Interconnect / Cross-Cloud Interconnect'], ['DR service', 'Elastic Disaster Recovery', 'Site Recovery', 'Backup and DR Service'], ['Analytics on other clouds', 'Athena federated query', 'Fabric shortcuts', 'BigQuery Omni']])

# ------------------------------------------------------------------ practical
MOCKQ.extend([
 (mock('aws', ['VPC', 'Create VPC'], ['Your VPCs', 'Subnets'], 'Your VPCs', [('Name', 'tiffingo-aws'), ('IPv4 CIDR', '10.10.0.0/16  (AWS block)')], 'Create VPC'),
  mock('az', ['Home', 'Virtual networks', 'Create'], ['Basics', 'IP addresses', 'Review + create'], 'IP addresses', [('Name', 'tiffingo-azure'), ('Address space', '10.20.0.0/16  (Azure block)')], 'Review + create'),
  mock('gcp', ['VPC network', 'Create'], ['VPC networks', 'Firewall'], 'VPC networks', [('Name', 'tiffingo-gcp'), ('Subnet', 'app · asia-south1 · 10.30.1.0/24  (GCP block)')], 'Create')),
 (mock('aws', ['S3', 'Buckets', 'Upload'], ['Buckets', 'Access Points'], 'Buckets', [('Bucket', 'tiffingo-dr-yourname'), ('File', 'menu-backup.json')], 'Upload'),
  mock('az', ['Home', 'Storage accounts', 'Containers', 'Upload'], ['Overview', 'Containers', 'Access keys'], 'Containers', [('Container', 'dr'), ('File', 'menu-backup.json')], 'Upload'),
  mock('gcp', ['Cloud Storage', 'Buckets', 'Upload'], ['Buckets', 'Monitoring', 'Settings'], 'Buckets', [('Bucket', 'tiffingo-dr-yourname'), ('File', 'menu-backup.json')], 'Upload files')),
 (mock('aws', ['EKS', 'Clusters', 'Create'], ['Clusters', 'Amazon EKS Anywhere'], 'Clusters', [('Kubernetes version', '▾ (latest supported)'), ('Note', 'look only — do not create')], 'Create cluster'),
  mock('az', ['Home', 'Kubernetes services', 'Create'], ['Basics', 'Node pools', 'Networking'], 'Basics', [('Kubernetes version', '▾ (default)'), ('Region', '▾ Central India')], 'Review + create'),
  mock('gcp', ['Kubernetes Engine', 'Clusters', 'Create'], ['Clusters', 'Fleets', 'Workloads'], 'Clusters', [('Release channel', '▾ Regular'), ('Version', '▾ (default)')], 'Create')),
 (mock('aws', ['Systems Manager', 'Hybrid activations', 'Create activation'], ['Fleet Manager', 'Hybrid activations', 'Session Manager'], 'Hybrid activations',
       [('Description', 'kitchen-servers'), ('Instance limit', '1'), ('IAM role', 'AmazonSSMRoleForInstancesQuickSetup')], 'Create activation'),
  mock('az', ['Home', 'Azure Arc', 'Machines', 'Add a single server'], ['Overview', 'Machines', 'Kubernetes clusters'], 'Machines',
       [('Resource group', '▾ rg-hybrid'), ('Region', '▾ Central India'), ('Operating system', '▾ Linux')], 'Download and run script'),
  mock('gcp', ['Kubernetes Engine', 'Fleets', 'Register cluster'], ['Clusters', 'Fleets', 'Config'], 'Fleets',
       [('Cluster type', 'Attached (EKS / AKS / other)'), ('Note', 'look only — needs an existing cluster')], 'Register')),
])

STEP1 = ('1 · Plan non-overlapping networks (one block per cloud)', tri(
    (['[[VPC]] → [[Create VPC]] → [[VPC only]] → name <code>tiffingo-aws</code>, CIDR <code>10.10.0.0/16</code>.', 'Write the plan down: AWS 10.10/16, Azure 10.20/16, Google 10.30/16, offices 192.168.x/24.'],
     "aws ec2 create-vpc --cidr-block 10.10.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=tiffingo-aws}]' --query Vpc.VpcId --output text\naws ec2 describe-vpcs --query 'Vpcs[].[VpcId,CidrBlock,Tags[?Key==`Name`]|[0].Value]' --output table",
     'your new VPC with <code>10.10.0.0/16</code> next to the default VPC (<code>172.31.0.0/16</code>) — no overlap with the other clouds’ blocks.'),
    (['[[Virtual networks]] → [[Create]] → rg <code>rg-hybrid</code>, name <code>tiffingo-azure</code>, address space <code>10.20.0.0/16</code>.'],
     'az group create -n rg-hybrid -l centralindia\naz network vnet create -g rg-hybrid -n tiffingo-azure --address-prefixes 10.20.0.0/16 --subnet-name app --subnet-prefixes 10.20.1.0/24\naz network vnet list --query "[].{name:name,space:addressSpace.addressPrefixes[0]}" -o table',
     '<code>tiffingo-azure 10.20.0.0/16</code>.'),
    (['[[VPC network]] → [[Create VPC network]] → <code>tiffingo-gcp</code>, custom subnet <code>app</code> asia-south1 <code>10.30.1.0/24</code>.'],
     'gcloud compute networks create tiffingo-gcp --subnet-mode=custom\ngcloud compute networks subnets create app --network=tiffingo-gcp --region=asia-south1 --range=10.30.1.0/24\ngcloud compute networks subnets list --network=tiffingo-gcp --format="table(name,region.basename(),ipCidrRange)"',
     '<code>app asia-south1 10.30.1.0/24</code>.')),
    'An IP plan written before the first network saves months later: overlapping ranges cannot be routed between clouds or to the office.')

STEP2 = ('2 · Keep a copy of data in each cloud (continuity basics)', tri(
    (['[[S3]] → [[Create bucket]] <code>tiffingo-dr-&lt;yourname&gt;</code> in Mumbai → [[Upload]] a small file <code>menu-backup.json</code>.'],
     'echo \'{"menu":"thali","price":150}\' > menu-backup.json\nB=tiffingo-dr-$RANDOM; aws s3 mb s3://$B --region ap-south-1\naws s3 cp menu-backup.json s3://$B/\naws s3api head-object --bucket $B --key menu-backup.json --query ETag --output text; md5sum menu-backup.json',
     'the S3 ETag and your local MD5 are the same hash — the copy is identical.'),
    (['[[Storage accounts]] → [[Create]] (Standard, LRS, Central India) → [[Containers]] → <code>dr</code> → [[Upload]] the same file.'],
     'echo \'{"menu":"thali","price":150}\' > menu-backup.json\nSA=tiffingodr$RANDOM; az storage account create -n $SA -g rg-hybrid -l centralindia --sku Standard_LRS\naz storage container create --account-name $SA -n dr --auth-mode login\naz storage blob upload --account-name $SA -c dr -f menu-backup.json --auth-mode login\naz storage blob show --account-name $SA -c dr -n menu-backup.json --auth-mode login --query properties.contentSettings.contentMd5 -o tsv',
     'a base64 MD5 of the file. (If <code>--auth-mode login</code> is denied, give yourself “Storage Blob Data Contributor” on the account.)'),
    (['[[Cloud Storage]] → [[Create]] bucket <code>tiffingo-dr-&lt;yourname&gt;</code> in asia-south1 → [[Upload files]].'],
     'echo \'{"menu":"thali","price":150}\' > menu-backup.json\nB=tiffingo-dr-$RANDOM; gcloud storage buckets create gs://$B --location=asia-south1\ngcloud storage cp menu-backup.json gs://$B/\ngcloud storage objects describe gs://$B/menu-backup.json --format="value(md5_hash)"',
     'the base64 MD5 — same file content as in the other clouds.')),
    'Copies only help if you can restore them: in a real plan, schedule copies, keep them immutable, and test a restore.')

STEP3 = ('3 · Find the portable layer: Kubernetes versions in each cloud', tri(
    (['[[EKS]] → [[Add cluster]] → [[Create]] → look at the Kubernetes version list, then cancel (a cluster bills hourly).'],
     "aws eks describe-cluster-versions --query 'clusterVersions[].[clusterVersion,versionStatus]' --output table",
     'the Kubernetes versions EKS supports and their status (standard / extended support).'),
    (['[[Kubernetes services]] → [[Create]] → [[Kubernetes cluster]] → look at the version list, then cancel.'],
     'az aks get-versions --location centralindia --query "values[].{version:version,support:capabilities.supportPlan[0]}" -o table',
     'supported AKS minor versions for Central India.'),
    (['[[Kubernetes Engine]] → [[Clusters]] → [[Create]] → [[Release channel]] → see versions, then cancel.'],
     'gcloud container get-server-config --location=asia-south1 --format="yaml(channels)"',
     'default and valid versions per release channel (Rapid, Regular, Stable).')),
    'All three run upstream-conformant Kubernetes — the same container image and manifest can run on any of them. That is why Kubernetes is the usual multi-cloud runtime.')

STEP4 = ('4 · Prepare central management for outside machines', tri(
    (['[[Systems Manager]] → [[Hybrid activations]] → [[Create activation]] → limit 1 → [[Create]]. Note the Activation Code and ID (shown once).', 'On an on-prem Linux server you would install the SSM Agent and register with them; it then appears in [[Fleet Manager]] as <code>mi-…</code>.'],
     "aws iam create-role --role-name SSMServiceRole --assume-role-policy-document '{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"ssm.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}'\naws iam attach-role-policy --role-name SSMServiceRole --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore\naws ssm create-activation --default-instance-name kitchen-01 --iam-role SSMServiceRole --registration-limit 1 --region ap-south-1",
     '<code>ActivationId</code> and <code>ActivationCode</code>. Registering standard on-prem nodes is free; advanced-tier features are paid.'),
    (['[[Azure Arc]] → [[Machines]] → [[Add/Create]] → [[Add a single server]] → [[Generate script]]: resource group <code>rg-hybrid</code>, Central India, Linux.', 'Running that script on a server installs the Connected Machine agent; the server then appears in Azure like a VM (policies, updates, monitoring).'],
     'az extension add --name connectedmachine --upgrade\naz provider register --namespace Microsoft.HybridCompute\naz connectedmachine list -g rg-hybrid -o table',
     'the provider registering and an empty list until a server runs the onboarding script. Arc’s core server management is free; extras like Defender are paid.'),
    (['[[Kubernetes Engine]] → [[Fleets]] → explore [[Register cluster]] → [[Attached]] — Google manages <b>Kubernetes clusters</b> elsewhere (EKS, AKS, on-prem), not individual servers.'],
     'gcloud services enable gkehub.googleapis.com\ngcloud container fleet memberships list',
     'an empty list — registering an outside cluster needs one (and GKE Enterprise pricing). Note the difference in approach: AWS/Azure manage servers; Google centres on Kubernetes fleets.')),
    'Hybrid management = one control plane for machines that live outside the cloud.')

prac = practical(OWN_INTRO + ' These steps are free or cost a few paise (tiny objects in storage). They build the foundations every hybrid or multi-cloud design needs: an IP plan, data copies, a portable runtime, and central management.', [SETUP_STEP, STEP1, STEP2, STEP3, STEP4],
    cleanup='<b>AWS:</b> <code>aws s3 rb s3://$B --force</code>; <code>aws ec2 delete-vpc --vpc-id &lt;vpc-id&gt;</code>; <code>aws ssm delete-activation --activation-id &lt;id&gt;</code>; detach the policy and delete <code>SSMServiceRole</code>. '
            '<b>Azure:</b> <code>az group delete -n rg-hybrid --yes --no-wait</code>. '
            '<b>Google Cloud:</b> <code>gcloud storage rm -r gs://$B</code>; <code>gcloud compute networks subnets delete app --region=asia-south1 --quiet</code>; <code>gcloud compute networks delete tiffingo-gcp --quiet</code>.')

mist = mistakes([
    ['Using hybrid and multi-cloud as synonyms.', 'Both mean “more than one place”.', 'Hybrid = private + public; multi-cloud = 2+ public providers.'],
    ['Multi-cloud “for reliability” without failover tests.', 'Assumed benefit.', 'Define RTO/RPO, automate, run game days.'],
    ['Splitting one chatty app across clouds.', 'Team preferences.', 'Partition along data boundaries; watch egress.'],
    ['Same 10.0.0.0/16 everywhere.', 'Defaults.', 'Central IP plan before building networks.'],
    ['Separate identities per cloud.', 'Each team sets up its own.', 'One IdP federated to all clouds.'],
    ['Lowest-common-denominator design.', 'Fear of lock-in.', 'Use managed services; keep data portable and an exit plan.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Hybrid and multi-cloud concepts, benefits and challenges.'], ['AWS CLF-C02', 'Hybrid architectures (Outposts, Direct Connect, VPN, Storage Gateway), DR strategies.'], ['AZ-900', 'Hybrid cloud, Azure Arc, Azure Local, ExpressRoute.'], ['Google Cloud Digital Leader', 'Hybrid and multi-cloud with GKE Enterprise, BigQuery Omni, open source and avoiding lock-in.']], minw=560) + \
    qx('1. Using AWS and Google Cloud together (no on-prem) is…', ['hybrid', 'multi-cloud', 'community', 'private'], 1, 'Multi-cloud.') + \
    qx('2. Which Azure service manages servers outside Azure from the Azure portal?', ['Azure Arc', 'Azure Bastion', 'Azure Front Door', 'Azure Advisor'], 0, 'Arc.') + \
    qx('3. Sending overflow load from on-prem to cloud at peaks is…', ['cloud bursting', 'partitioning', 'sharding', 'peering'], 0, 'Bursting.') + \
    qx('4. Which Google product queries data in AWS S3 without moving it?', ['BigQuery Omni', 'Cloud Run', 'Dataproc', 'Pub/Sub'], 0, 'Omni.') + \
    qx('5. Main prerequisite for connecting networks across environments?', ['same provider', 'non-overlapping IP ranges', 'same VM sizes', 'public IPs on all VMs'], 1, 'IP plan.') + \
    qx('6. RPO measures…', ['how long recovery takes', 'how much data loss is acceptable', 'network latency', 'cost'], 1, 'Recovery point.')

proj = miniproject('Mini project: TiffinGo’s hybrid multi-cloud blueprint',
    'Design TiffinGo’s target landscape and justify every cross-environment link.',
    ['<b>Inventory</b> workloads and where they run (hospital DC, AWS, Google, M365).',
     '<b>Pattern</b> per link: partitioned, analytics, edge, environment, continuity or bursting — with one reason.',
     '<b>IP plan:</b> one block per environment (step 1) including future Regions and offices.',
     '<b>Identity:</b> choose the IdP and map roles to each cloud.',
     '<b>Continuity:</b> RTO/RPO for orders; choose same-provider multi-Region vs second provider and explain.',
     '<b>Costs:</b> estimate monthly egress for the analytics copy (GB/day × price).'],
    'A one-page blueprint diagram with patterns, IP plan, identity and DR targets.', '3.1 + 6.3 (networking) + 5.5 (pricing) + 7.2 (availability).')

assemble_v2(HERE, story_h2='“What if AWS has a bad day?”', hook_html=hk,
    narration='At a board meeting, an investor asked what TiffinGo would do if its cloud provider failed. The data team wanted BigQuery, and the hospital link was already live. The team needed clear words before clear decisions.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Multi-cloud vs hybrid cloud',
    formal='<b>Hybrid cloud</b> is a composition of two or more distinct cloud infrastructures — typically private/on-premises and public — bound together to enable data and application portability (NIST). <b>Multi-cloud</b> is the use of cloud services from two or more public cloud providers within one organisation or architecture. An organisation that does both is said to be <b>hybrid multi-cloud</b>.',
    simple='Hybrid = your own servers plus a public cloud working together. Multi-cloud = using more than one public cloud company.',
    interview=['“Hybrid joins private/on-prem and public cloud; multi-cloud uses several public providers. They are independent — many enterprises are hybrid multi-cloud.”', '“I pick patterns deliberately: partitioned apps, analytics on the best platform, edge hybrid for sites, DR with tested RTO/RPO, bursting for batch — with one IdP, an IP plan and Kubernetes as the portable runtime.”'],
    terms_rows=[('Hybrid cloud', 'Private/on-prem + public, connected.'), ('Multi-cloud', '2+ public providers.'), ('Hybrid multi-cloud', 'Both.'), ('Lock-in', 'Cost of leaving a provider.'), ('Data gravity', 'Data attracts compute.'), ('RTO / RPO', 'Recovery time / data loss targets.'), ('Cloud bursting', 'Overflow to public cloud.'), ('IdP federation', 'One identity across clouds.')],
    exam='Expect definitions (hybrid vs multi-cloud), hybrid services (Outposts, Arc, Azure Local, GKE Enterprise, Direct Connect/ExpressRoute) and DR terms (RTO/RPO).',
    picture_h2='Hybrid, multi-cloud and both', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Six hybrid and multi-cloud patterns, one by one', TYPES)],
    how_h2='A cross-cloud failover, step by step', how_intro='What really happens in the business-continuity pattern.', how_anim=FAIL,
    parts_h2='Six foundations of hybrid and multi-cloud', parts_html=parts, lv='',
    myth_rows=[('Multi-cloud makes you more reliable.', 'Only with tested failover; otherwise it adds failure points.', 'Type 5.'), ('Hybrid and multi-cloud are the same.', 'Different questions.', 'Venn figure.'), ('Avoid all managed services to avoid lock-in.', 'That trades lock-in for operations cost.', 'Deep dive.')],
    extra_secs=[('deep', 'Deep dive', 'Lock-in, inter-cloud networking, control planes, data gravity', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Define hybrid, multi-cloud and hybrid multi-cloud precisely.', 'Choose among six architecture patterns with reasons.', 'Explain cross-cloud failover with RTO and RPO.', 'Plan IP ranges, keep data copies, compare Kubernetes and prepare hybrid management on your own accounts.', 'Discuss lock-in and data gravity in an interview.'],
    next_html='<a href="../04-cloud-vs-grid-vs-fog-vs-edge-computing/">3.4 Cloud vs grid vs fog vs edge computing</a>.',
    pre='<b>Before you start:</b> 3.1 and 3.2.')
