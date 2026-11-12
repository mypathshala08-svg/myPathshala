import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)
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


hk = hook('TiffinGo raises its first big investment. The new CTO asks: “Why are we on AWS? Should we be on Azure because our accountants use Microsoft 365, or Google because the data team loves BigQuery?” What would a good answer sound like?',
    'Not “AWS is best”. All three leading clouds can run TiffinGo. The real differences are in <b>strengths</b>, <b>ecosystem</b>, <b>organisation model</b>, <b>pricing details</b>, <b>Regions near your users</b> and <b>your team’s skills</b>. This lesson compares six providers one by one — AWS, Microsoft Azure, Google Cloud, Oracle Cloud, IBM Cloud and Indian providers — animates how each one organises accounts, billing and policies, and on <b>your own</b> accounts you inspect the hierarchy, compare India Regions and zones, and price the same VM in all three.',
    ['Why the “resource hierarchy” matters more than the logo.', 'Same VM size, three prices — and why per-hour price is only the start.', 'How to answer “which cloud is best?” in an interview without picking a fight.'])

def story_scene():
    o = t(180, 12, 'Three good answers, one decision', 9, 'ink', bold=True)
    for i, (a, b, tn) in enumerate([('AWS', 'broadest catalogue', 'amber'), ('Azure', 'Microsoft ecosystem', 'blue'), ('Google Cloud', 'data + AI, Kubernetes', 'green')]):
        x = 8 + i * 118
        o += box(x, 30, 110, 62, tn, rx=8) + t(x + 55, 54, a, 8.6, 'ink', bold=True) + t(x + 55, 72, b, 7, 'ink2')
    o += t(180, 114, 'Pick by workload, skills and ecosystem — not by headline', 7.4, 'ink', bold=True)
    return o
scene_svg = scene('Three boxes: AWS with the broadest catalogue, Azure with the Microsoft ecosystem, Google Cloud strong in data, AI and Kubernetes.', story_scene(), 'Every big cloud can run you. Choose what <tspan font-weight="700" class="s-acc">fits</tspan>.', h=126)
dialogue = '''R> Sir, the CTO wants a comparison by Friday. Should I list who has more services?
A> Counting services is the weakest argument. List what we need: managed Postgres, containers, BigQuery-style analytics, Indian Regions, and our team’s skills.
K> Our team knows AWS. The data team uses BigQuery.
A> Then the honest answer might be “AWS for apps, Google for analytics” — that is the partitioned multi-cloud from Lesson 3.3.
R> And Azure?
A> If we adopt Microsoft 365 and Entra ID, Azure becomes attractive for identity and Windows workloads. Let’s compare properly.'''

def hierfig():
    o = t(320, 16, 'How each cloud organises accounts, billing and policies', 11, 'ink', bold=True)
    cols = [('AWS', 'amber', ['Organization (root)', 'Organizational units (OUs)', 'Accounts', 'Resources (tags)']), ('Azure', 'blue', ['Entra tenant + root mgmt group', 'Management groups', 'Subscriptions → resource groups', 'Resources (tags)']), ('Google Cloud', 'green', ['Organization', 'Folders', 'Projects', 'Resources (labels)'])]
    for j, (n, tn, levels) in enumerate(cols):
        x = 20 + j * 206
        o += t(x + 92, 38, n, 9, 'ink', bold=True)
        for i, l in enumerate(levels):
            o += box(x + i * 6, 48 + i * 40, 184 - i * 12, 30, tn, rx=6) + t(x + 92, 67 + i * 40, l, 7.4, 'ink', bold=(i == 2))
            if i < 3: o += arrow(x + 92, 78 + i * 40, x + 92, 88 + i * 40)
    o += t(320, 222, 'Bold level = the main unit of isolation and billing: AWS account, Azure subscription, Google project.', 7.4, 'ink2')
    return o
HIER = bigfig('Three hierarchies: AWS organization, OUs, accounts, resources; Azure tenant and root management group, management groups, subscriptions and resource groups, resources; Google organization, folders, projects, resources.', hierfig(), h=232)

picture = ('  <p>Before services, understand how each cloud is <b>organised</b> — it decides where you put policies, budgets and access:</p>\n' + HIER +
           '\n  <h3>The big three at a glance</h3>\n' + table(['', 'AWS', 'Microsoft Azure', 'Google Cloud'], [
               ['Launched', '2006 (S3, EC2)', '2010 (Windows Azure)', '2008 (App Engine); GCP brand later'], ['Known for', 'broadest, deepest service catalogue; largest market share', 'Microsoft stack, hybrid, enterprise identity (Entra ID)', 'data analytics (BigQuery), Kubernetes (GKE), AI, global network'],
               ['India Regions', 'Mumbai, Hyderabad', 'Central India (Pune), South India (Chennai), West India (Mumbai)', 'Mumbai, Delhi'], ['Isolation unit', 'account', 'subscription (+ resource group)', 'project'],
               ['Identity', 'IAM + Identity Center', 'Entra ID', 'Cloud Identity / Workspace'], ['IaC native', 'CloudFormation, CDK', 'ARM, Bicep', 'Infrastructure Manager (Terraform)'], ['Entry certification', 'Cloud Practitioner (CLF-C02)', 'Azure Fundamentals (AZ-900)', 'Cloud Digital Leader']], minw=660) +
           '\n  <p>Synergy Research’s quarterly reports consistently rank AWS first, Microsoft second and Google third in cloud infrastructure services, together holding roughly two-thirds of the market, with the rest split among Alibaba, Oracle, IBM, Salesforce, regional providers and others.</p>')

RN = {'org': (4, 54, 50, 50, 'cloud', 'Top level', 'org / tenant'), 'grp': (66, 4, 62, 46, 'gear', 'Groups', 'OU / MG / folder'), 'unit': (66, 104, 62, 46, 'server', 'Unit', 'acct / sub / proj'),
      'pol': (142, 54, 60, 50, 'shield', 'Policy', 'SCP / Policy / org pol'), 'iam': (216, 4, 62, 46, 'user', 'Access', 'roles inherit'), 'bill': (216, 104, 62, 46, 'meter', 'Billing', 'per unit + tags'), 'res': (292, 54, 64, 50, 'app', 'Resources', 'VMs, DBs')}
RS = [dict(on=['org'], hot='org', move=None, head='Step 1 · One top-level container', text='AWS Organization · Azure tenant with root management group · Google Organization', text2='(tied to your company domain). Everything else hangs below it.', svc='Created once per company'),
      dict(on=['org', 'grp'], hot='grp', move=(54, 79, 72, 30, 'group'), head='Step 2 · Group by team or environment', text='OUs (AWS), management groups (Azure) or folders (Google): e.g. “Prod”, “Non-prod”,', text2='“Sandbox” — so rules can be applied once to many units.', svc='Design for policy, not for the org chart'),
      dict(on=['grp', 'unit'], hot='unit', move=(97, 50, 97, 104, 'contain'), head='Step 3 · The unit of isolation', text='AWS account · Azure subscription (+ resource groups inside) · Google project. Each is a', text2='security and billing boundary; TiffinGo uses one per app per environment.', svc='Blast radius stops at the unit boundary'),
      dict(on=['grp', 'unit', 'pol'], hot='pol', move=(128, 127, 150, 90, 'guard'), head='Step 4 · Guard-rails flow down', text='SCPs (AWS), Azure Policy (Azure) and organization policies (Google) set at a group', text2='apply to every unit below: “India Regions only”, “no public buckets”.', svc='Lesson 3.1 and 9.1 guard-rails live here'),
      dict(on=['pol', 'iam', 'bill'], hot='bill', move=(202, 90, 226, 126, 'cost'), head='Step 5 · Access and billing follow the tree', text='Role assignments inherit downwards (Azure, Google); AWS uses Identity Center', text2='permission sets per account. Costs roll up by unit and by tags/labels.', svc='Budgets per account / subscription / project'),
      dict(on=list(RN), hot='res', move=(278, 127, 298, 90, 'deploy'), head='Step 6 · Resources live in the unit', text='VMs, databases and buckets are created inside an account / subscription+resource group /', text2='project — and inherit every policy and permission above.', svc='Same idea, different names: learn the mapping once')]
TREE = flow_anim('How each cloud organises everything', 'The same governance idea, with three sets of names.', 'Resource hierarchy', 'Animation: top-level container; groups; unit of isolation; guard-rails flow down; access and billing follow the tree; resources live in the unit.', RN, RS, hid='treeflow')

def mapfig():
    o = t(320, 16, 'Six providers you should be able to compare', 11, 'ink', bold=True)
    items = [('1', 'Amazon Web Services', 'broadest catalogue', 'amber'), ('2', 'Microsoft Azure', 'Microsoft ecosystem + hybrid', 'blue'), ('3', 'Google Cloud', 'data, AI, Kubernetes', 'green'),
             ('4', 'Oracle Cloud (OCI)', 'Oracle DBs, price-performance', 'red'), ('5', 'IBM Cloud', 'regulated, mainframe, hybrid', 'violet'), ('6', 'Indian / regional providers', 'local presence, sovereignty', 'card')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 3) * 208; y = 32 + (i // 3) * 84
        o += box(x, y, 198, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 106, y + 34, a, 8.2, 'ink', bold=True) + t(x + 106, y + 54, b, 7, 'ink2')
    o += t(320, 210, '1–3 dominate exams and jobs; 4–6 matter in specific industries and tenders.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of six providers: AWS, Microsoft Azure, Google Cloud, Oracle Cloud, IBM Cloud, Indian and regional providers.', mapfig(), h=222)

A1 = mk(['First mover (2006)', 'Huge catalogue', 'Largest ecosystem'], ['2006|S3, EC2|first public IaaS', 'catalogue|200+ services|deep options', 'ecosystem|partners, jobs|marketplace'], ['amber', 'amber', 'green'],
        ['AWS launched S3 and EC2 in 2006', 'it offers the broadest set of services with deep configuration options', 'the largest partner, marketplace and job ecosystem'],
        [('2006', 'First large public IaaS with S3 and EC2.', ''), ('Breadth', 'Broadest catalogue, many options per service.', ''), ('Ecosystem', 'Largest market share, partners and community.', '')],
        'AWS in brief', 'Broadest and longest-running.', 'AWS', 'Animation: 2006 start; huge catalogue; largest ecosystem.', 'v1anim')
T1 = vt(1, 'Amazon Web Services (AWS)', 'amber',
    '<b>AWS</b>, Amazon’s cloud business, launched its first major infrastructure services (S3 and EC2) in 2006 and offers the broadest and deepest catalogue of cloud services — compute, storage, databases, analytics, AI/ML, IoT and more — across many Regions, with the largest market share and partner ecosystem.',
    'The largest supermarket in town: if a product exists, it is probably on a shelf — but you need a map to find it.',
    'TiffinGo started on AWS because its first engineers knew it, Mumbai was available early, and Lambda/DynamoDB fit the order API.',
    'EC2, S3, Lambda, RDS/Aurora, DynamoDB, EKS/ECS, SageMaker AI and Bedrock; Mumbai (2016) and Hyderabad (2022) Regions; certification path from Cloud Practitioner to Professional and Specialty.', '', A1,
    'you want the widest choice, the largest talent pool, or a specific AWS-only service.',
    'your organisation is deeply standardised on Microsoft licensing and identity — compare Azure carefully.',
    'Amazon’s cloud — the oldest and biggest, with the most services.',
    [('Account', 'Unit of isolation.'), ('Organizations', 'Group accounts, SCPs.'), ('Identity Center', 'SSO to accounts.'), ('Control Tower', 'Landing zone.'), ('Well-Architected', '6 pillars.')],
    [('Region / AZ', 'AWS geography (Lesson 5.1)'), ('SCP', 'service control policy'), ('Control Tower', 'AWS landing-zone service')],
    table(['', 'AWS', 'Azure'], [['Isolation unit', 'account', 'subscription'], ['Identity', 'IAM + Identity Center', 'Entra ID'], ['IaC', 'CloudFormation/CDK', 'ARM/Bicep']], minw=420),
    ['Start-ups', 'Digital natives', 'Enterprises of every kind'],
    'Synergy Research has ranked AWS as the largest cloud infrastructure provider in every quarterly report since the market began to be tracked.',
    'AWS often gives several services for one job (e.g. ECS, EKS, App Runner→ECS Express, Lambda, Beanstalk) — knowing when to pick which is the real AWS skill.')

A2 = mk(['Microsoft stack', 'Entra ID at the centre', 'Hybrid everywhere'], ['stack|Windows, SQL|.NET, M365', 'identity|Entra ID|one login', 'hybrid|Arc, Azure Local|ExpressRoute'], ['blue', 'blue', 'green'],
        ['Azure integrates tightly with Windows Server, SQL Server, .NET and Microsoft 365', 'Entra ID provides identity for Azure, M365 and thousands of apps', 'strong hybrid story with Arc, Azure Local and licensing benefits'],
        [('Stack', 'Windows Server, SQL Server, .NET, Microsoft 365.', ''), ('Identity', 'Entra ID shared with Microsoft 365.', ''), ('Hybrid', 'Arc, Azure Local, Hybrid Benefit licensing.', '')],
        'Azure in brief', 'Enterprise and Microsoft-centric.', 'Azure', 'Animation: Microsoft stack; Entra ID; hybrid everywhere.', 'v2anim')
T2 = vt(2, 'Microsoft Azure', 'blue',
    '<b>Microsoft Azure</b>, launched in 2010, is Microsoft’s cloud platform; it integrates closely with Windows Server, SQL Server, .NET, Microsoft 365 and Entra ID, offers strong hybrid capabilities (Azure Arc, Azure Local) and licensing benefits for existing Microsoft customers, and is the second-largest cloud infrastructure provider.',
    'The company canteen run by the same firm that runs your office: your ID card already works there, and the menu matches what you are used to.',
    'TiffinGo’s accounting team moved to Microsoft 365; using Entra ID for Azure and AWS SSO made identity simpler, and a Windows-based accounting tool fits Azure VMs with Hybrid Benefit.',
    'Virtual Machines, App Service, Functions, AKS, Container Apps, Azure SQL, Cosmos DB, Microsoft Fabric, Microsoft Foundry and Azure OpenAI; Central/South/West India Regions; AZ-900 → role-based certifications.', '', A2,
    'you run Microsoft workloads, use Microsoft 365/Entra ID, or need strong hybrid/on-prem integration.',
    'you assume Azure is “only for Windows” — Linux runs a large share of Azure VMs.',
    'Microsoft’s cloud — strongest for companies already using Microsoft software.',
    [('Tenant', 'Entra ID directory.'), ('Management groups', 'Policy and RBAC at scale.'), ('Subscriptions', 'Billing + isolation.'), ('Resource groups', 'Lifecycle containers.'), ('Landing zones', 'Cloud Adoption Framework.')],
    [('tenant', 'an organisation’s Entra ID directory'), ('resource group', 'container for related Azure resources'), ('Hybrid Benefit', 'reuse existing Windows/SQL licences in Azure')],
    table(['', 'Azure', 'Google Cloud'], [['Isolation unit', 'subscription', 'project'], ['Policy', 'Azure Policy', 'org policies'], ['Strength', 'Microsoft + hybrid', 'data + AI + K8s']], minw=420),
    ['Enterprises', 'Government and education', 'Windows/.NET shops'],
    'Microsoft has reported that many Fortune 500 companies use Azure, often alongside Microsoft 365 — the shared identity makes adoption easier.',
    'Exam and job interviews often test Azure’s extra level: resource groups. They are lifecycle containers, not security boundaries like subscriptions.')

A3 = mk(['Global network', 'Data + AI', 'Open source roots'], ['network|private fibre|global LB', 'data|BigQuery|Vertex AI, Gemini', 'open|Kubernetes|TensorFlow'], ['green', 'blue', 'green'],
        ['Google’s private global network carries traffic between Regions', 'BigQuery, Vertex AI and Gemini models are flagship services', 'Kubernetes began at Google; strong open-source culture'],
        [('Network', 'Private global backbone, global load balancing.', ''), ('Data + AI', 'BigQuery, Vertex AI, Gemini.', ''), ('Open source', 'Kubernetes, TensorFlow origins.', '')],
        'Google Cloud in brief', 'Data, AI and Kubernetes.', 'Google Cloud', 'Animation: global network; data and AI; open-source roots.', 'v3anim')
T3 = vt(3, 'Google Cloud', 'green',
    '<b>Google Cloud</b> provides infrastructure, platform, data and AI services built on Google’s global network and technologies; it is known for BigQuery (serverless data warehouse), Vertex AI and Gemini models, GKE (Kubernetes originated at Google), Cloud Run, and a project-based organisation model, and is the third-largest cloud infrastructure provider.',
    'A specialist kitchen with the best ovens in the city: maybe a shorter menu than the supermarket, but certain dishes come out best there.',
    'TiffinGo’s data team keeps order analytics in BigQuery (partitioned multi-cloud, Lesson 3.3) and trains demand-forecast models with Vertex AI.',
    'Compute Engine, GKE, Cloud Run, Cloud SQL, AlloyDB, Spanner, BigQuery, Vertex AI, Gemini; Mumbai (2017) and Delhi (2021) Regions; Cloud Digital Leader → Associate/Professional certifications.', '', A3,
    'data analytics, AI/ML, containers/Kubernetes and global networking are priorities.',
    'you need a very specific niche service that only another provider offers — check the catalogue.',
    'Google’s cloud — especially strong for data analysis, AI and containers.',
    [('Organization', 'Tied to Workspace/Cloud Identity domain.'), ('Folders', 'Group projects.'), ('Projects', 'Billing + isolation + APIs.'), ('Org policies', 'Guard-rails.'), ('Architecture Framework', '6 pillars.')],
    [('project', 'Google Cloud’s unit for resources, billing and APIs'), ('BigQuery', 'serverless data warehouse'), ('Vertex AI', 'Google’s ML platform')],
    table(['', 'Google Cloud', 'AWS'], [['Isolation unit', 'project', 'account'], ['Global VPC', 'yes (one VPC spans Regions)', 'no (VPC per Region)'], ['Data warehouse', 'BigQuery (serverless)', 'Redshift (+ Serverless)']], minw=440),
    ['Data-driven companies', 'AI/ML teams', 'Cloud-native start-ups'],
    'A Google Cloud VPC network is global: subnets in different Regions share one network — unlike AWS, where each VPC lives in one Region.',
    'Google projects are cheap to create and delete; using one project per app per environment makes clean-up and billing much easier.')

A4 = mk(['Oracle databases', 'OCI regions', 'Multicloud DB'], ['Oracle DB|Exadata|Autonomous DB', 'OCI|price-performance|flat egress pricing', 'multicloud|Oracle DB@Azure|@AWS, @Google'], ['red', 'amber', 'green'],
        ['Oracle Database runs best on Oracle’s own Exadata infrastructure', 'OCI competes on price-performance and simpler networking prices', 'Oracle databases are now offered inside AWS, Azure and Google data centres'],
        [('DB', 'Exadata and Autonomous Database.', ''), ('OCI', 'Price-performance; generous outbound data allowance.', ''), ('Multicloud', 'Oracle Database@Azure, @AWS, @Google Cloud.', '')],
        'Oracle Cloud in brief', 'The database specialist.', 'OCI', 'Animation: Oracle databases; OCI regions; multicloud database.', 'v4anim')
T4 = vt(4, 'Oracle Cloud Infrastructure (OCI)', 'red',
    '<b>Oracle Cloud Infrastructure</b> offers IaaS and PaaS with particular strength in running Oracle Database (Exadata, Autonomous Database) and Oracle applications, competitive compute and networking prices, and multicloud database partnerships that place Oracle Database services inside Azure, AWS and Google Cloud data centres.',
    'The original manufacturer’s service centre: if your car is that brand, they know it best — and now they also open counters inside other garages.',
    'A TiffinGo enterprise customer running Oracle E-Business Suite moved it to OCI and connected it to its Azure apps through Oracle Database@Azure.',
    'OCI Compute, Autonomous Database, Exadata Database Service, OCI Generative AI; Mumbai and Hyderabad Regions; Oracle Database@Azure/@AWS/@Google Cloud.', '', A4,
    'Oracle Database and Oracle applications are central to the business.',
    'you have no Oracle workloads and need a broad ecosystem — the big three are usually simpler.',
    'Oracle’s cloud — the natural home for companies running Oracle databases.',
    [('Tenancy', 'Top-level account.'), ('Compartments', 'Isolation and policy.'), ('DB services', 'Autonomous, Exadata.'), ('Interconnect', 'With Azure/Google.'), ('Licensing', 'BYOL options.')],
    [('Exadata', 'Oracle’s engineered database hardware'), ('Autonomous Database', 'self-managing Oracle DB'), ('compartment', 'OCI’s resource container')],
    table(['', 'OCI', 'Big three'], [['Oracle DB fit', 'best', 'via partnerships/RDS'], ['Ecosystem size', 'smaller', 'larger'], ['Typical buyer', 'Oracle shops', 'everyone']], minw=420),
    ['Banks and telecoms on Oracle', 'ERP workloads', 'High-performance DBs'],
    'Oracle Database@Azure, @AWS and @Google Cloud put Oracle-managed Exadata inside the other providers’ data centres — multicloud by design.',
    'Licensing often decides Oracle placements more than technology — always involve licensing experts.')

A5 = mk(['Regulated industries', 'Hybrid + mainframe', 'Red Hat platform'], ['regulated|banks, insurers|Cloud for FS', 'hybrid|z/OS, Power|on-prem links', 'platform|OpenShift|consulting'], ['violet', 'blue', 'green'],
        ['IBM focuses on regulated industries such as financial services', 'it connects mainframes and on-prem systems with cloud', 'Red Hat OpenShift is its main hybrid platform'],
        [('Regulated', 'Financial-services-ready controls.', ''), ('Hybrid', 'Mainframe and on-prem integration.', ''), ('Platform', 'Red Hat OpenShift across environments.', '')],
        'IBM Cloud in brief', 'Hybrid for regulated industries.', 'IBM Cloud', 'Animation: regulated industries; hybrid and mainframe; Red Hat platform.', 'v5anim')
T5 = vt(5, 'IBM Cloud', 'violet',
    '<b>IBM Cloud</b> focuses on hybrid cloud for regulated industries, with offerings built around Red Hat OpenShift, mainframe and Power Systems integration, financial-services-ready controls and consulting-led modernisation, rather than competing on catalogue breadth.',
    'A specialist bank-security contractor: not the biggest builder, but the one many banks call for vault-grade work.',
    'A bank partner of TiffinGo modernises mainframe applications with IBM while exposing APIs that TiffinGo calls from AWS.',
    'IBM Cloud VPC, Red Hat OpenShift on IBM Cloud, IBM Cloud for Financial Services, IBM watsonx; IBM Z and Power Virtual Server.', 'OpenShift was covered in 3.2.', A5,
    'mainframe/Power workloads, strict financial-services controls, or IBM-led transformation programmes.',
    'you are a start-up seeking the largest catalogue and community.',
    'IBM’s cloud — aimed at banks and large companies with old core systems.',
    [('Assess', 'Mainframe/Power estate.'), ('Platform', 'OpenShift for portability.'), ('Controls', 'FS-validated framework.'), ('Connect', 'To other clouds.'), ('Modernise', 'Gradually.')],
    [('mainframe', 'large central computer used by banks and governments'), ('Power Systems', 'IBM servers for AIX/IBM i workloads'), ('watsonx', 'IBM’s AI and data platform')],
    table(['', 'IBM Cloud', 'AWS'], [['Focus', 'hybrid, regulated, mainframe', 'breadth, scale'], ['Platform bet', 'OpenShift', 'native services'], ['Typical buyer', 'banks, insurers', 'all sizes']], minw=420),
    ['Banks and insurers', 'Mainframe shops', 'Large transformation programmes'],
    'Red Hat (acquired by IBM in 2019) gives IBM its hybrid strategy: OpenShift runs on IBM Cloud, AWS (ROSA), Azure (ARO) and on-premises.',
    'IBM often appears in Indian banking tenders together with system integrators — know it for interviews even if you build on the big three.')

A6 = mk(['Indian data centres', 'Local support + compliance', 'Government and sovereign'], ['local|Yotta, CtrlS|Tata, Sify…', 'support|INR billing|local teams', 'sovereign|MeitY-empanelled|GPU clouds'], ['card', 'blue', 'green'],
        ['Indian companies run large data centres and cloud services', 'they offer rupee billing, local support and compliance focus', 'many are MeitY-empanelled and offer sovereign and GPU clouds'],
        [('Local', 'Indian data centre and cloud companies.', ''), ('Support', 'INR billing, local teams, compliance focus.', ''), ('Sovereign', 'MeitY empanelment, government and GPU clouds.', '')],
        'Indian providers in brief', 'Local and sovereign.', 'Indian providers', 'Animation: Indian data centres; local support; government and sovereign.', 'v6anim')
T6 = vt(6, 'Indian and regional providers', 'card',
    '<b>Indian and regional cloud providers</b> — such as Yotta, CtrlS, Sify, Tata Communications, ESDS, Jio and others — operate data centres and cloud services in India, offering rupee billing, local support, MeitY empanelment for government workloads, sovereign and GPU/AI cloud options, often alongside colocation for hyperscalers.',
    'A trusted neighbourhood caterer: smaller menu than a hotel chain, but local, flexible, speaks your language and knows the local rules.',
    'A state department running TiffinGo’s school-meal integration requires a MeitY-empanelled provider; TiffinGo deploys that component with an Indian provider while the rest stays on AWS.',
    'Indian clouds with government community offerings (Lesson 3.1), GPU clouds built under national AI initiatives, colocation hosting hyperscaler edge sites.', '', A6,
    'government tenders, strict sovereignty demands, INR contracts or local GPU capacity.',
    'you need the global reach and managed-service breadth of the big three.',
    'Indian cloud companies that keep data in India and serve local and government customers.',
    [('Check', 'MeitY empanelment and certifications.'), ('Compare', 'Services vs your needs.'), ('Contract', 'SLAs, exit terms.'), ('Integrate', 'Network to other clouds.'), ('Operate', 'Monitoring and support.')],
    [('empanelment', 'government approval to supply'), ('colocation', 'renting data-centre space and power'), ('GPU cloud', 'cloud focused on AI accelerators')],
    table(['', 'Indian provider', 'Hyperscaler India Region'], [['Data location', 'India', 'India'], ['Service breadth', 'narrower', 'very broad'], ['Government empanelment', 'common', 'also available']], minw=440),
    ['Government and PSUs', 'BFSI with local preferences', 'AI start-ups needing GPUs'],
    'India’s national AI programme has supported GPU capacity from Indian providers, making them visible options for AI workloads.',
    'In tenders, check the exact empanelled services — empanelment is per offering, not a blanket approval of the company.')

SUMMARY = table(['#', 'Provider', 'Best known for', 'Isolation unit', 'Entry cert'], [
    ['1', 'AWS', 'breadth, ecosystem, market leader', 'account', 'Cloud Practitioner'], ['2', 'Azure', 'Microsoft stack, identity, hybrid', 'subscription', 'AZ-900'], ['3', 'Google Cloud', 'data, AI, Kubernetes, network', 'project', 'Cloud Digital Leader'],
    ['4', 'OCI', 'Oracle DB, price-performance', 'compartment', 'OCI Foundations'], ['5', 'IBM Cloud', 'regulated hybrid, mainframe, OpenShift', 'account + resource groups', 'IBM Cloud Advocate'], ['6', 'Indian providers', 'local, sovereign, INR', 'varies', 'vendor-specific']], minw=620)
CHECK = ('  <h3>Check yourself: which provider fits?</h3>\n' +
    qx('A. A bank running Oracle Exadata wants a managed cloud version.', ['OCI (or Oracle Database@ another cloud)', 'Google Cloud only', 'IBM only', 'None'], 0, 'Oracle DB.') +
    qx('B. A company standardised on Microsoft 365 and Windows Server.', ['Azure is a natural fit', 'Only OCI', 'Only IBM', 'No cloud'], 0, 'Microsoft ecosystem.') +
    qx('C. Serverless petabyte analytics is the priority.', ['Google Cloud (BigQuery)', 'IBM Z', 'Colocation', 'On-prem SAN'], 0, 'BigQuery.') +
    qx('D. A state tender requires MeitY empanelment and INR billing.', ['Empanelled Indian provider or empanelled hyperscaler offering', 'Any foreign SaaS', 'Personal account', 'None'], 0, 'Empanelment.'))

TYPES = ('  <p>Six providers, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['Which provider’s VPC spans Regions?', 'Is an Azure resource group a security boundary?', 'Why do Oracle databases now run inside other clouds?'], 'types 3, 2 and 4') + MAP
         + jump(['AWS', 'Azure', 'Google', 'OCI', 'IBM', 'Indian']) + T1 + T2 + T3 + T4 + T5 + T6
         + '\n  <h3 style="margin-top:34px">All six side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('Service fit', 'Do they have what you need, managed?', 'Fewer services to build yourself.', 'Postgres, K8s, analytics, AI.'),
    ('Regions + latency', 'Data centres near users and data.', 'Speed and residency.', 'India Regions, AZs.'),
    ('Ecosystem', 'Partners, marketplace, community.', 'Hiring, tools, help.', 'Job market, training.'),
    ('Pricing model', 'Compute, storage, egress, discounts.', 'Total cost, not list price.', 'Savings plans, CUDs, reservations.'),
    ('Governance model', 'Hierarchy, policy, identity.', 'Security at scale.', 'Accounts / subscriptions / projects.'),
    ('Skills + support', 'What your team knows; support plans.', 'Speed and safety.', 'Certifications, support tiers.')])

DEEP = ('  <h3>Discount models compared</h3>\n' + table(['Model', 'AWS', 'Azure', 'Google Cloud'], [['Commit to spend/usage', 'Savings Plans, Reserved Instances', 'Reservations, savings plan for compute', 'Committed use discounts (spend/resource)'], ['Automatic sustained discount', '—', '—', 'sustained use discounts (on some machine families)'], ['Spare capacity', 'Spot Instances', 'Spot VMs', 'Spot VMs'], ['Licence reuse', 'BYOL', 'Azure Hybrid Benefit', 'BYOL / sole-tenant']], minw=600) +
    '\n  <h3>How to write a fair comparison</h3>\n  <ol><li>Start from <b>requirements</b> (services, Regions, compliance, skills), not from logos.</li><li>Compare <b>like for like</b>: same vCPU/RAM generation, same storage class, same Region, same support level.</li><li>Include <b>egress, support plans and people costs</b> (Lesson 5.5).</li><li>Check <b>roadmap risk</b>: services being retired (App Runner new customers, Deployment Manager) matter.</li><li>Run a <b>small proof of concept</b> on the top two.</li></ol>\n'
    '  <h3>Answering “which cloud is best?” in an interview</h3>\n  <p>“It depends on the workload. AWS has the broadest catalogue and ecosystem, Azure fits Microsoft-centric enterprises and hybrid, Google Cloud is strong in data, AI and Kubernetes. I would decide on required services, Regions, compliance, team skills and total cost — and I’m comfortable translating between them.”</p>')

clouds = vendor_tabs('<p><b>AWS:</b> Organizations, Control Tower, Identity Center, Pricing Calculator, Well-Architected Tool; Regions in Mumbai and Hyderabad plus Local Zones in Delhi and Kolkata.</p>',
    '<p><b>Azure:</b> management groups, subscriptions, resource groups, Azure Policy, Cloud Adoption Framework landing zones, Pricing calculator, Advisor; Central, South and West India Regions.</p>',
    '<p><b>Google Cloud:</b> Organization, folders, projects, organization policies, Cloud Foundation Toolkit / landing zones, Pricing Calculator, Active Assist; Mumbai and Delhi Regions.</p>') + \
    cloud3([['Top level', 'Organization', 'Tenant + root management group', 'Organization'], ['Grouping', 'OUs', 'Management groups', 'Folders'], ['Isolation/billing unit', 'Account', 'Subscription (+ resource groups)', 'Project'], ['Guard-rails', 'SCPs', 'Azure Policy', 'Organization policies'], ['Metadata', 'Tags', 'Tags', 'Labels (and tags)']])

MOCKQ.extend([
 (mock('aws', ['AWS Organizations', 'AWS accounts'], ['AWS accounts', 'Policies', 'Services', 'Settings'], 'AWS accounts', [('Root', 'r-xxxx'), ('OU', 'Prod · Non-prod · Sandbox'), ('Account', 'tiffingo-orders-prod')], 'Add an AWS account'),
  mock('az', ['Home', 'Management groups'], ['Management groups', 'Subscriptions', 'Resource groups'], 'Management groups', [('Tenant Root Group', '└ Prod · Non-prod'), ('Subscription', 'Pay-As-You-Go')], 'Create'),
  mock('gcp', ['IAM & Admin', 'Manage resources'], ['IAM', 'Manage resources', 'Organization policies'], 'Manage resources', [('Organization', 'example.com (or No organization)'), ('Project', 'tiffingo-lab')], 'Create project')),
 (mock('aws', ['EC2', 'Settings', 'Zones'], ['EC2 Dashboard', 'Settings'], 'Settings', [('Region', 'Asia Pacific (Mumbai)'), ('Availability Zones', 'ap-south-1a · 1b · 1c'), ('Local Zones', 'Delhi · Kolkata (opt-in)')], 'Manage'),
  mock('az', ['Subscriptions', 'Resource providers', 'Locations'], ['Overview', 'Usage + quotas'], 'Overview', [('Central India', 'zones 1 · 2 · 3'), ('South India / West India', 'available')], 'Refresh'),
  mock('gcp', ['Compute Engine', 'Zones'], ['VM instances', 'Zones'], 'Zones', [('asia-south1', 'a · b · c'), ('asia-south2', 'a · b · c')], 'Refresh')),
 (mock('aws', ['AWS Pricing Calculator', 'EC2'], ['My estimate', 'Add service'], 'Add service', [('Instance', 'm7i.large · 2 vCPU · 8 GiB'), ('Region', 'Asia Pacific (Mumbai)'), ('Pricing', 'On-Demand · Linux')], 'Save'),
  mock('az', ['Pricing calculator', 'Virtual Machines'], ['Products', 'Estimates'], 'Products', [('Instance', 'D2s v5 · 2 vCPU · 8 GiB'), ('Region', 'Central India'), ('Pricing', 'Pay as you go · Linux')], 'Export'),
  mock('gcp', ['Pricing Calculator', 'Compute Engine'], ['Add to estimate'], 'Add to estimate', [('Machine type', 'n4-standard-2 · 2 vCPU · 8 GB'), ('Region', 'asia-south1'), ('Pricing', 'On-demand')], 'Add to estimate')),
])

STEP1 = ('1 · Look at your own resource hierarchy', tri(
    (['Search [[AWS Organizations]] — if you see “Create an organization”, your account is standalone (fine for learning). [[IAM]] shows your account ID top right.'],
     "aws sts get-caller-identity --query '[Account,Arn]' --output text\naws organizations describe-organization --query 'Organization.[Id,MasterAccountId]' --output text 2>&1 | tail -1",
     'your 12-digit account ID; then either an organization ID or <code>AWSOrganizationsNotInUseException</code> — a standalone account is its own isolation and billing unit.'),
    (['[[Management groups]] → you see the Tenant Root Group (create it if prompted); [[Subscriptions]] → your subscription; [[Resource groups]] inside it.'],
     'az account show --query "{tenant:tenantId,subscription:name,id:id}" -o table\naz account management-group list --query "[].{name:displayName,id:name}" -o table 2>&1 | tail -3\naz group list --query "[].{rg:name,location:location}" -o table',
     'your tenant and subscription, any management groups you can see, and your resource groups — Azure’s three levels.'),
    (['[[IAM &amp; Admin]] → [[Manage resources]] — personal accounts show “No organization” with projects directly below; company accounts show the organization and folders.'],
     'gcloud projects list --format="table(projectId,name,parent.type,parent.id)"\ngcloud organizations list 2>&1 | tail -2',
     'your projects (parent empty for personal accounts) and the organization list (empty without Workspace/Cloud Identity).')),
    'Same idea, three names: account, subscription (+ resource group), project.')

STEP2 = ('2 · Compare India Regions and zones', tri(
    (['Region selector: Mumbai and Hyderabad. [[EC2]] → [[Settings]] → [[Zones]] shows Availability Zones and opt-in Local Zones (Delhi, Kolkata).'],
     "for r in ap-south-1 ap-south-2; do echo \"== $r\"; aws ec2 describe-availability-zones --region $r --all-availability-zones \\\n  --query 'AvailabilityZones[].[ZoneName,ZoneType,OptInStatus]' --output text 2>&1 | head -6; done",
     'Mumbai’s three AZs plus Local Zones (e.g. <code>ap-south-1-del-1a local-zone</code>); Hyderabad needs opt-in to list zones.'),
    (['Create pages list India Regions; zones appear under [[Availability options]] for VMs in Central India.'],
     'az account list-locations --query "[?contains(displayName,\'India\')].{name:name,display:displayName,zones:length(availabilityZoneMappings || `[]`)}" -o table',
     'Central India with 3 zones; South India and West India listed (zone support varies by Region and subscription).'),
    (['[[Compute Engine]] → [[Zones]] lists zones per Region.'],
     'gcloud compute zones list --filter="region~asia-south" --format="table(name,region.basename(),status)"',
     '<code>asia-south1-a/b/c</code> and <code>asia-south2-a/b/c</code>, all UP.')),
    'All three offer multiple India Regions with zones — residency and resilience are possible on each.')

STEP3 = ('3 · Price the same VM size in all three', tri(
    (['[[Pricing Calculator]] → EC2 → m7i.large (2 vCPU, 8 GiB), Mumbai, Linux, On-Demand → note the monthly cost.'],
     "aws pricing get-products --region us-east-1 --service-code AmazonEC2 --filters \\\n  Type=TERM_MATCH,Field=instanceType,Value=m7i.large Type=TERM_MATCH,Field=regionCode,Value=ap-south-1 \\\n  Type=TERM_MATCH,Field=operatingSystem,Value=Linux Type=TERM_MATCH,Field=tenancy,Value=Shared \\\n  Type=TERM_MATCH,Field=preInstalledSw,Value=NA Type=TERM_MATCH,Field=capacitystatus,Value=Used \\\n  --query 'PriceList[0]' --output text | python3 -c \"import sys,json; d=json.loads(sys.stdin.read()); t=list(d['terms']['OnDemand'].values())[0]; p=float(list(t['priceDimensions'].values())[0]['pricePerUnit']['USD']); print('m7i.large Mumbai', p, '/h  ~', round(p*730,1), '/month')\"",
     'the hourly On-Demand USD price and an approximate monthly figure.'),
    (['[[Pricing calculator]] → Virtual Machines → D2s v5 (2 vCPU, 8 GiB), Central India, Linux, Pay as you go.', 'The CLI uses Azure’s public Retail Prices API — no login needed.'],
     "curl -s \"https://prices.azure.com/api/retail/prices?\\$filter=serviceName%20eq%20'Virtual%20Machines'%20and%20armRegionName%20eq%20'centralindia'%20and%20armSkuName%20eq%20'Standard_D2s_v5'%20and%20priceType%20eq%20'Consumption'\" \\\n  | python3 -c \"import sys,json; [print(i['productName'], i['skuName'], i['retailPrice'], '/h') for i in json.load(sys.stdin)['Items'] if 'Windows' not in i['productName'] and 'Spot' not in i['skuName'] and 'Low' not in i['skuName']]\"",
     'the Linux pay-as-you-go hourly price for D2s v5 in Central India.'),
    (['[[Google Cloud Pricing Calculator]] → Compute Engine → n4-standard-2 (2 vCPU, 8 GB), asia-south1, on-demand.', 'The Cloud Billing Catalog API needs an API key; the CLI confirms the machine shape.'],
     'gcloud compute machine-types describe n4-standard-2 --zone=asia-south1-a --format="value(name,guestCpus,memoryMb)"',
     '<code>n4-standard-2 2 8192</code> — then read the price in the calculator.')),
    'List prices are close; real differences come from discounts, egress, support and how well you right-size (Lesson 5.5).')

prac = practical(OWN_INTRO + ' Read-only comparisons: your hierarchy, India Regions and zones, and the price of the same VM size on each cloud. Nothing costs money.', [SETUP_STEP, STEP1, STEP2, STEP3],
    cleanup='Nothing to delete — all steps were read-only.')

mist = mistakes([
    ['Choosing by number of services.', 'Easy headline.', 'Choose by required services, Regions, skills, cost.'],
    ['Comparing different VM generations.', 'Picking cheapest-looking names.', 'Match vCPU/RAM/generation/Region.'],
    ['Ignoring egress and support costs.', 'Focus on compute.', 'Full TCO (Lesson 5.5).'],
    ['Treating resource groups as security boundaries.', 'Azure naming confusion.', 'Subscriptions/accounts/projects isolate; RGs organise.'],
    ['Assuming skills transfer automatically.', '“Cloud is cloud”.', 'Plan training and translation tables.'],
    ['Religious debates.', 'Personal preference.', 'Requirements matrix + proof of concept.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Comparison of cloud vendors (AWS, Azure, Google Cloud) and their services.'], ['AWS CLF-C02', 'AWS global infrastructure, Organizations, pricing tools.'], ['AZ-900', 'Management groups, subscriptions, resource groups hierarchy.'], ['Google Cloud Digital Leader', 'Resource hierarchy, organization/folders/projects, Google’s differentiators.']], minw=560) + \
    qx('1. In Azure, the main billing and isolation unit is…', ['resource group', 'subscription', 'tag', 'region'], 1, 'Subscription.') + \
    qx('2. In Google Cloud, resources and billing are grouped in…', ['accounts', 'projects', 'compartments', 'tenancies'], 1, 'Projects.') + \
    qx('3. AWS service to manage many accounts with policies is…', ['AWS Organizations', 'AWS Artifact', 'Amazon Lightsail', 'AWS Snow'], 0, 'Organizations.') + \
    qx('4. Which Azure level sits above subscriptions?', ['management groups', 'resource groups', 'tags', 'availability sets'], 0, 'Management groups.') + \
    qx('5. Google Cloud’s serverless data warehouse is…', ['BigQuery', 'Redshift', 'Synapse', 'Snowflake'], 0, 'BigQuery.') + \
    qx('6. Which provider offers Hybrid Benefit for existing Windows/SQL licences?', ['Azure', 'Google Cloud', 'OCI', 'IBM'], 0, 'Azure.')

proj = miniproject('Mini project: the CTO’s cloud comparison',
    'Write the comparison the new CTO asked for.',
    ['<b>Requirements:</b> list TiffinGo’s 10 must-have services, Regions and compliance needs.',
     '<b>Matrix:</b> score AWS, Azure and Google on each (have it / managed / gaps).',
     '<b>Hierarchy:</b> propose accounts/subscriptions/projects per environment for the chosen design.',
     '<b>Cost:</b> price one standard VM and one managed Postgres in all three (step 3 + calculators).',
     '<b>Skills:</b> map the team’s certifications and training needs.',
     '<b>Recommend:</b> one paragraph — single cloud or partitioned multi-cloud — with reasons.'],
    'A two-page comparison with matrix, hierarchy sketch, cost table and recommendation.', '3.3 (multi-cloud) + 5.5 (pricing) + 10.1.')

assemble_v2(HERE, story_h2='“Why are we on AWS?”', hook_html=hk,
    narration='After a funding round, TiffinGo’s new CTO asked a simple question that started a long debate: should the company stay on AWS, move to Azure with its Microsoft 365 rollout, or use Google Cloud for its data team’s favourite tools?',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='AWS vs Azure vs Google Cloud',
    formal='<b>Comparing cloud providers</b> means evaluating platforms such as Amazon Web Services, Microsoft Azure and Google Cloud (and others including Oracle, IBM and regional providers) on service fit, global and local infrastructure, resource-hierarchy and governance model, identity integration, pricing and discount models, ecosystem, support and team skills, to choose the best platform — or combination — for specific workloads.',
    simple='AWS, Azure and Google Cloud can all run most apps; compare what you need, where your users are, what your team knows and what it really costs.',
    interview=['“AWS has the broadest catalogue and largest ecosystem, Azure integrates with Microsoft 365, Entra ID and hybrid, Google Cloud leads in data analytics, AI and Kubernetes. I choose per workload on services, Regions, compliance, skills and TCO.”', '“The organisation models differ: AWS accounts under Organizations, Azure subscriptions and resource groups under management groups, Google projects under folders and an organization.”'],
    terms_rows=[('Hyperscaler', 'Very large cloud provider.'), ('Account / subscription / project', 'Isolation and billing units.'), ('OU / management group / folder', 'Grouping levels.'), ('Resource group', 'Azure lifecycle container.'), ('Landing zone', 'Pre-configured governed environment.'), ('Committed use', 'Discount for commitment.'), ('Hybrid Benefit', 'Reuse Microsoft licences.'), ('Empanelment', 'Government approval.')],
    exam='Each exam tests its own hierarchy: AWS Organizations/accounts, Azure management groups/subscriptions/resource groups, Google organization/folders/projects; plus basic differentiators.',
    picture_h2='How the clouds are organised, and the big three at a glance', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Six cloud providers, one by one', TYPES)],
    how_h2='How each cloud organises everything', how_intro='Governance follows the hierarchy — learn the mapping once.', how_anim=TREE,
    parts_h2='Six factors for choosing a provider', parts_html=parts, lv='',
    myth_rows=[('One cloud is best for everything.', 'Each has strengths; choose per workload.', 'Types.'), ('Azure is only for Windows.', 'Linux is widely used on Azure.', 'Type 2.'), ('More services = better choice.', 'Fit, skills and cost matter more.', 'Deep dive.')],
    extra_secs=[('deep', 'Deep dive', 'Discount models, fair comparisons, interview answer', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Compare AWS, Azure, Google Cloud, OCI, IBM and Indian providers.', 'Explain each cloud’s resource hierarchy and where policies and billing attach.', 'Inspect your hierarchy, compare India Regions and price equal VMs across clouds.', 'Write a requirements-based provider comparison.', 'Answer “which cloud is best?” well in an interview.'],
    next_html='<a href="../02-comparing-cloud-web-services/">10.2 Comparing cloud web services</a>.',
    pre='<b>Before you start:</b> Modules 5 and 6.')
