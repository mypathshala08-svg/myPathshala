import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)


hk = hook('TiffinGo uses Gmail, Zoho Books, Freshdesk, Canva, Razorpay and Zoom — and owns zero servers for any of them. When the support tool had an outage, whose problem was it? And when an ex-employee still had access to the accounts software, whose problem was that?',
    'The first was the <b>vendor’s</b>; the second was <b>TiffinGo’s</b>. In <b>Software as a Service (SaaS)</b> the provider runs the entire application — infrastructure, platform, code, updates — and you simply use it through a browser, app or API, usually per user per month. But identity, access, configuration and your data stay your responsibility. This lesson explains horizontal and vertical SaaS, multi-tenant and single-tenant delivery, API-first and low-code SaaS, buying SaaS through cloud marketplaces, how a SaaS request reaches your company’s data — and on <b>your own</b> account you set up single sign-on for a SaaS app and track SaaS spend.',
    ['Seven ways SaaS is built and sold — including the one India is famous for.', 'How one SaaS app serves thousands of companies without mixing their data.', 'Why “the vendor handles everything” is the most dangerous SaaS myth.'])

def story_scene():
    o = t(180, 12, 'Six SaaS apps, zero servers', 9, 'ink', bold=True)
    for i, n in enumerate(['Gmail', 'Zoho Books', 'Freshdesk', 'Canva', 'Razorpay', 'Zoom']):
        x = 14 + (i % 3) * 114; y = 26 + (i // 3) * 42
        o += box(x, y, 104, 34, 'green', rx=6) + t(x + 52, y + 21, n, 7.6, 'ink', bold=True)
    o += t(180, 128, 'Vendor runs the software · TiffinGo owns users, settings and data.', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Six boxes for SaaS products used by TiffinGo: Gmail, Zoho Books, Freshdesk, Canva, Razorpay and Zoom.', story_scene(), 'Rent the <tspan font-weight="700" class="s-acc">software</tspan>, not the servers.', h=142)
dialogue = '''R> Sir, Freshdesk was down for an hour today. Should we have hosted our own helpdesk?
A> Then the outage — and the patching, backups and upgrades — would be ours. With SaaS the vendor runs all of it; we check their status page and SLA.
K> But Manoj left two months ago and could still log into Zoho Books.
A> That one is on us. In SaaS we still own who has access, how it is configured, and our data. Single sign-on fixes it: disable him once, and every app locks him out.
R> So SaaS is not “no responsibility”.
A> It is “less responsibility”. Let’s see the types and where the line is.'''

# ------------------------------------------------------------------ picture
def respfig():
    o = t(320, 16, 'Shared responsibility in SaaS: still yours vs the vendor’s', 11, 'ink', bold=True)
    o += box(14, 32, 300, 196, 'blue', rx=10) + t(164, 50, 'STILL YOURS', 9, 'ink', bold=True)
    for i, n in enumerate(['Who has accounts (joiners/leavers)', 'Passwords, MFA, single sign-on', 'Roles and sharing settings', 'Your data: what you upload, export, retain', 'Devices and browsers used to access it', 'Compliance of how you use it']):
        o += box(26, 60 + i * 27, 276, 22, 'card', rx=4) + t(164, 75 + i * 27, n, 7.4, 'ink')
    o += box(326, 32, 300, 196, 'green', rx=10) + t(476, 50, 'THE VENDOR’S', 9, 'ink', bold=True)
    for i, n in enumerate(['Application code and features', 'Updates and security patches', 'Servers, OS, databases, scaling', 'Availability (per SLA) and backups of the service', 'Physical and network security', 'Certifications (ISO 27001, SOC 2…)']):
        o += box(338, 60 + i * 27, 276, 22, 'card', rx=4) + t(476, 75 + i * 27, n, 7.4, 'ink')
    o += t(320, 246, 'Most SaaS incidents in companies are on the left: leaked passwords, ex-employees, over-shared files.', 7.4, 'ink2')
    return o
RESP = bigfig('Two columns: still yours — accounts, MFA and SSO, roles and sharing, your data, devices, compliance; the vendor’s — application code, updates, servers and scaling, availability and service backups, physical security, certifications.', respfig(), h=256)

def tenfig():
    o = t(320, 16, 'Multi-tenancy: one application, thousands of customers', 11, 'ink', bold=True)
    for i, (n, tn) in enumerate([('TiffinGo', 'green'), ('Ravi Caterers', 'amber'), ('City Hospital', 'violet')]):
        o += box(14, 40 + i * 62, 120, 46, tn, rx=8) + t(74, 60 + i * 62, n, 7.8, 'ink', bold=True) + t(74, 76 + i * 62, f'tenant {i + 1}', 6.8, 'ink2') + arrow(136, 63 + i * 62, 196, 132)
    o += box(198, 96, 140, 72, 'blue', rx=10) + t(268, 122, 'one app version', 8, 'ink', bold=True) + t(268, 140, 'shared servers', 7, 'ink') + t(268, 154, 'tenant ID on every request', 6.6, 'ink2')
    o += arrow(340, 132, 400, 132)
    o += box(402, 40, 224, 184, 'card', rx=10) + t(514, 58, 'data, separated by tenant', 8, 'ink', bold=True)
    for i, (n, tn) in enumerate([('tenant 1 rows / schema / DB', 'green'), ('tenant 2 rows / schema / DB', 'amber'), ('tenant 3 rows / schema / DB', 'violet')]):
        o += box(414, 70 + i * 48, 200, 38, tn, rx=6) + t(514, 93 + i * 48, n, 7.2, 'ink')
    o += t(320, 244, 'Isolation by row (tenant_id), schema or separate database — Lesson 5.2 compares pool, bridge and silo models.', 7.4, 'ink2')
    return o
TEN = bigfig('Three customer companies as tenants connect to one shared application version, which keeps each tenant’s data separated by rows, schemas or separate databases.', tenfig(), h=254)

picture = ('  <p>SaaS removes almost all the stack from your hands — but not all of it:</p>\n' + RESP + '\n  <p>And how one SaaS application serves many companies at once:</p>\n' + TEN)

# ------------------------------------------------------------------ how
RN = {'u': (4, 54, 54, 50, 'laptop', 'Employee', 'opens app'), 'idp': (66, 4, 60, 46, 'shield', 'Company IdP', 'Entra / Okta'), 'saas': (66, 104, 60, 46, 'cloud', 'SaaS edge', 'tiffingo.zoho…'),
      'route': (138, 54, 62, 50, 'dns', 'Tenant router', 'tenant = TiffinGo'), 'app': (212, 4, 64, 46, 'server', 'Shared app', 'v2026.11'), 'data': (212, 104, 64, 46, 'db', 'Tenant data', 'isolated'), 'upd': (290, 54, 66, 50, 'gear', 'Vendor', 'ships updates')}
RS = [dict(on=['u', 'saas'], hot='saas', move=(28, 104, 66, 128, 'HTTPS'), head='Step 1 · Open the app in a browser', text='The employee goes to the company’s SaaS address (often a sub-domain or org name).', text2='Nothing is installed; any device with a browser works.', svc='Delivered over the internet — the defining SaaS trait'),
      dict(on=['u', 'saas', 'idp'], hot='idp', move=(58, 70, 70, 40, 'SSO'), head='Step 2 · Single sign-on through your identity provider', text='The SaaS redirects to the company’s IdP (SAML/OIDC); MFA and policies apply;', text2='a signed token comes back. Leavers disabled in the IdP lose access everywhere.', svc='Microsoft Entra ID, Okta, Google, IAM Identity Center'),
      dict(on=['u', 'saas', 'idp', 'route'], hot='route', move=(126, 127, 150, 90, 'tenant'), head='Step 3 · The tenant is identified', text='From the token or URL the platform knows this user belongs to tenant “TiffinGo”', text2='and attaches the tenant ID to every request.', svc='Tenant context — the heart of multi-tenant SaaS'),
      dict(on=['u', 'saas', 'idp', 'route', 'app', 'data'], hot='data', move=(244, 50, 244, 104, 'query'), head='Step 4 · Shared code, separated data', text='The same application version serves everyone; every query is filtered by tenant', text2='(or goes to the tenant’s own schema/database).', svc='Pool / bridge / silo isolation (Lesson 5.2)'),
      dict(on=list(RN), hot='upd', move=(276, 127, 298, 90, 'deploy'), head='Step 5 · The vendor updates everyone continuously', text='New features and security fixes roll out to all tenants — often weekly — without', text2='any customer downtime or installation.', svc='No versions to upgrade; read the release notes')]
FLOW = flow_anim('One SaaS login, from browser to your data', 'How a multi-tenant SaaS app serves your company.', 'SaaS request', 'Animation: employee opens the SaaS app; single sign-on through the company identity provider; tenant identified; shared application reads tenant-isolated data; vendor ships updates to all tenants.', RN, RS, hid='saasflow')

# ------------------------------------------------------------------ types
def mapfig():
    o = t(320, 16, 'Seven kinds of SaaS', 11, 'ink', bold=True)
    items = [('1', 'Horizontal SaaS', 'any industry: mail, CRM', 'green'), ('2', 'Vertical SaaS', 'one industry: clinics, schools', 'amber'), ('3', 'Multi-tenant SaaS', 'shared app and infra', 'blue'),
             ('4', 'Single-tenant SaaS', 'dedicated per customer', 'violet'), ('5', 'API-first SaaS', 'payments, SMS, maps', 'blue'), ('6', 'Low-code SaaS', 'build apps without code', 'green'), ('7', 'Marketplace SaaS', 'bought via cloud bill', 'amber')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 7.8, 'ink', bold=True) + t(x + 78, y + 54, b, 6.8, 'ink2')
    o += t(320, 210, '1–2 = who it is for · 3–4 = how it is delivered · 5–7 = how it is used and bought.', 7.6, 'ink2')
    return o
MAP = bigfig('Map of seven kinds of SaaS: horizontal, vertical, multi-tenant, single-tenant, API-first, low-code, marketplace SaaS.', mapfig(), h=222)

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

A1 = mk(['Same need everywhere', 'One product, all industries', 'Per-user pricing'], ['need|email, docs,|chat, CRM', 'product|Microsoft 365 /|Google Workspace', 'pricing|₹ per user|per month'], ['green', 'blue', 'amber'],
        ['every business needs mail, documents, meetings, accounting', 'the same features sold to banks, schools and caterers', 'pay for the seats you use; add or remove monthly'],
        [('Need', 'A function every business has: mail, documents, CRM, accounting.', ''), ('Product', 'One product serves all industries.', ''), ('Pricing', 'Typically per user per month, scaled up and down.', '')],
        'Horizontal SaaS in action', 'One product for every industry.', 'Horizontal SaaS', 'Animation: common business needs; one product for all industries; per-user pricing.', 's1anim')
T1 = vtype(1, 'Horizontal SaaS', 'green',
    '<b>Horizontal SaaS</b> delivers software for a business function that is common across industries — email and productivity, collaboration, CRM, HR, accounting, customer support, design — to a broad market of customers of every type.',
    'A general store: rice, soap and stationery that every household buys, whatever the family’s profession.',
    'TiffinGo uses Google Workspace for mail and documents, Freshdesk for customer support and Zoho Books for GST accounting — the same products a law firm or a school would use.',
    'Microsoft 365, Google Workspace, Salesforce, Zoho One, Freshworks, Slack, Zoom, Canva, Atlassian Cloud.',
    '', A1,
    'the function is standard and you do not want to build or run it.',
    'you need deep industry-specific workflows — vertical SaaS may fit better.',
    plain='Software that every kind of business needs — like email, documents or accounting — rented online per user.',
    how=[('Sign up', 'Create an organisation (tenant).'), ('Add users', 'Per-seat licences, often via SSO.'), ('Configure', 'Policies, roles, integrations.'), ('Use', 'Browser and mobile apps.'), ('Scale', 'Add/remove seats monthly.')],
    words=[('seat', 'one paid user licence'), ('tenant / organisation', 'your company’s own space in the SaaS app'), ('subscription', 'regular payment for continued use')],
    diff=table(['', 'Horizontal SaaS', 'Vertical SaaS'], [['Market', 'all industries', 'one industry'], ['Features', 'general', 'industry workflows, compliance'], ['Examples', 'Microsoft 365, Zoho, Freshdesk', 'clinic, school, restaurant software']], minw=440),
    where=['Email and collaboration', 'CRM, support, HR, accounting', 'Design and video meetings'],
    realworld='India is a major SaaS exporter: <b>Zoho</b> (Chennai) and <b>Freshworks</b> (Chennai origin, listed on Nasdaq in 2021) sell horizontal SaaS — CRM, accounting, helpdesk — to businesses worldwide.',
    pro='Horizontal SaaS often becomes a platform: Salesforce, Microsoft 365 and Zoho let customers build custom apps on top (low-code, APIs), which is why “SaaS” and “PaaS” blur at the large vendors.')

A2 = mk(['One industry’s workflow', 'Built-in compliance', 'Deep integrations'], ['industry|clinics, schools|restaurants', 'rules|GST, health,|education norms', 'integrations|POS, labs,|aggregators'], ['amber', 'red', 'blue'],
        ['designed around one industry’s daily work', 'regulations of that sector are built in', 'connects to the sector’s specific systems'],
        [('Workflow', 'The product models one industry’s daily process.', ''), ('Compliance', 'Sector rules (tax, health, education) are built in.', ''), ('Integrations', 'It connects to the sector’s devices and partners.', '')],
        'Vertical SaaS in action', 'Software for one industry.', 'Vertical SaaS', 'Animation: industry workflow; built-in compliance; sector integrations.', 's2anim')
T2 = vtype(2, 'Vertical SaaS', 'amber',
    '<b>Vertical SaaS</b> delivers software designed for the workflows, data and regulations of one specific industry — such as healthcare, education, restaurants, logistics or banking — often combining several functions (operations, billing, compliance, integrations) for that sector.',
    'A specialist medical store: it stocks exactly what clinics need, and the staff understand prescriptions and regulations.',
    'TiffinGo’s kitchens use a restaurant-management SaaS: kitchen order tickets, recipe costing, inventory, GST invoices and integration with food-delivery aggregators — features no general accounting tool has.',
    'Veeva (life sciences), Toast (restaurants), Practo Ray (clinics), school-management SaaS, core-banking SaaS; many Indian vertical SaaS start-ups.',
    '', A2,
    'your industry has specific workflows or regulations a generic tool handles badly.',
    'the vertical vendor is small and your exit plan (data export) is unclear.',
    plain='Software made for one kind of business — like a clinic, a school or a restaurant — with all its special needs built in.',
    how=[('Industry model', 'Data and screens follow the sector’s process.'), ('Compliance', 'Built-in rules and reports.'), ('Integrations', 'Sector devices, partners, government portals.'), ('Payments', 'Often embedded billing/payments.'), ('Updates', 'Regulatory changes delivered centrally.')],
    words=[('vertical', 'one industry'), ('compliance', 'following rules and regulations'), ('integration', 'connecting with other systems')],
    diff=table(['', 'Vertical SaaS', 'Horizontal SaaS + customisation'], [['Fit for industry', 'high out of the box', 'needs configuration/dev'], ['Market size', 'smaller', 'larger'], ['Vendor risk', 'often smaller vendors', 'large vendors']], minw=440),
    where=['Healthcare and clinics', 'Schools and coaching institutes', 'Restaurants, logistics, construction'],
    realworld='Veeva Systems built a large business selling CRM and content software only to pharmaceutical and life-sciences companies — originally on top of Salesforce’s platform, a classic vertical SaaS story.',
    pro='When a GST rule changes, every customer of a vertical SaaS gets the fix at once — one of the biggest hidden benefits for small businesses that cannot track every regulation themselves.')

A3 = mk(['Shared everything', 'Tenant ID everywhere', 'One upgrade for all'], ['shared|app + infra|+ database', 'tenant_id|in every query|and log', 'release|all tenants|same day'], ['blue', 'red', 'green'],
        ['lowest cost per customer', 'isolation is enforced in software', 'one version to run, test and secure'],
        [('Shared', 'All customers share the same application instances and infrastructure.', ''), ('Isolation', 'Every request and query carries the tenant ID.', ''), ('One version', 'The vendor upgrades everyone together.', '')],
        'Multi-tenant SaaS in action', 'One app, many customers.', 'Multi-tenant', 'Animation: shared application and infrastructure; tenant ID on every query; one release for all tenants.', 's3anim')
T3 = vtype(3, 'Multi-tenant SaaS', 'blue',
    '<b>Multi-tenant SaaS</b> serves many customer organisations (tenants) from a single shared deployment of the application and infrastructure, keeping each tenant’s data and configuration logically isolated, so that the vendor runs one version, scales economically and delivers updates to all tenants at once.',
    'An apartment building: many families, one building, one lift and one water tank — each flat locked and private.',
    'Freshdesk serves TiffinGo and thousands of other companies from shared infrastructure; TiffinGo sees only its own tickets because every query is filtered by its account ID.',
    'Most SaaS: Salesforce, Microsoft 365, Google Workspace, Zoho, Freshworks, Slack. Built on cloud services with tenant-aware databases (row-level security, partition keys).',
    'Lesson 5.2 explains pooling and the pool/bridge/silo isolation models.', A3,
    'standard SaaS for many customers — this is the default model.',
    'a customer needs physical isolation, custom versions or its own encryption keys and the vendor cannot offer them.',
    plain='One copy of the software serves many companies at the same time, while each company’s data is kept separate and private.',
    how=[('Onboard tenant', 'Create tenant record, admin user, settings.'), ('Identify', 'Tenant from domain/token on every request.'), ('Isolate', 'Row-level security, per-tenant schema or DB, per-tenant keys.'), ('Meter', 'Usage per tenant for billing and limits.'), ('Release', 'Feature flags per tenant; one codebase.')],
    words=[('tenant', 'one customer organisation'), ('row-level security', 'database rules that show each tenant only its rows'), ('noisy neighbour', 'a tenant whose load slows others')],
    diff=table(['', 'Multi-tenant', 'Single-tenant'], [['Cost per customer', 'lowest', 'higher'], ['Isolation', 'logical', 'physical/dedicated'], ['Upgrades', 'everyone together', 'per customer schedule']], minw=440),
    where=['Almost all mass-market SaaS', 'SMB products', 'Freemium apps'],
    realworld='Salesforce’s multi-tenant architecture (described in its engineering papers) runs every customer on shared “pods” with metadata-driven customisation — the design that made SaaS economically possible at scale.',
    pro='The biggest multi-tenant bug is a missing tenant filter: one query without <code>WHERE tenant_id = ?</code> leaks data across customers. Teams enforce isolation in the database (PostgreSQL row-level security, DynamoDB IAM leading-key conditions) rather than trusting every developer.')

A4 = mk(['Dedicated stack', 'Customer-specific controls', 'Vendor still operates'], ['dedicated|app + DB|per customer', 'controls|own keys, region|upgrade window', 'operations|vendor runs|patches, backups'], ['violet', 'red', 'green'],
        ['each big customer gets its own instance', 'customer keys, chosen Region, scheduled upgrades', 'it is still SaaS — the customer does not run it'],
        [('Dedicated', 'Each customer gets a separate deployment of app and data.', ''), ('Controls', 'Own encryption keys, Region, network and upgrade timing.', ''), ('Operated', 'The vendor still runs and maintains it.', '')],
        'Single-tenant SaaS in action', 'SaaS with a private copy.', 'Single-tenant', 'Animation: a dedicated stack per customer; customer-specific controls; vendor operates it.', 's4anim')
T4 = vtype(4, 'Single-tenant (dedicated) SaaS', 'violet',
    '<b>Single-tenant SaaS</b> gives each customer a dedicated instance of the application and data store — sometimes in the customer’s chosen Region or even its own cloud account — while the vendor still operates, patches and supports it; it trades higher cost for stronger isolation, customisation and control.',
    'An independent bungalow in a gated colony managed by one maintenance company: your own house, but someone else fixes the plumbing.',
    'A large bank buying a customer-support SaaS demands a dedicated instance in the Mumbai Region with its own encryption keys and a quarterly upgrade window — the vendor offers a single-tenant “enterprise” edition.',
    'Enterprise/dedicated editions of many SaaS products (e.g. dedicated Atlassian or ServiceNow instances); BYOC (“bring your own cloud”) SaaS deployed into the customer’s AWS/Azure/GCP account.',
    '', A4,
    'regulated or very large customers need physical isolation, data residency or custom upgrade timing.',
    'you choose it by default — it costs more and you may lag behind on features.',
    plain='The SaaS company runs a separate private copy of the software just for you — more privacy and control, at a higher price.',
    how=[('Provision', 'Dedicated environment per customer (often by IaC).'), ('Locate', 'Customer’s Region or account.'), ('Secure', 'Customer-managed keys, private connectivity.'), ('Operate', 'Vendor patches, backs up, monitors.'), ('Upgrade', 'On an agreed schedule.')],
    words=[('dedicated instance', 'a copy used by only one customer'), ('BYOC', 'bring your own cloud — the SaaS runs in the customer’s account'), ('customer-managed key', 'an encryption key the customer controls')],
    diff=table(['', 'Single-tenant SaaS', 'Self-hosted software'], [['Who operates', 'vendor', 'customer'], ['Updates', 'vendor-managed', 'customer-managed'], ['Isolation', 'dedicated', 'dedicated']], minw=440),
    where=['Banks, insurers, government', 'Healthcare with strict data rules', 'Large enterprises'],
    realworld='“Bring your own cloud” deployments have grown with data platforms — for example, Databricks runs its data plane inside the customer’s AWS, Azure or Google Cloud account while managing the control plane as SaaS.',
    pro='India’s data-localisation rules for payments (RBI, 2018) pushed many payment-related SaaS vendors to offer India-only, often dedicated deployments — a regulatory driver for single-tenant SaaS.')

A5 = mk(['Sign up, get API keys', 'Call the API from code', 'Pay per use'], ['account|API key|sandbox', 'your app|POST /payments|SDK', 'billing|per transaction|per SMS'], ['blue', 'green', 'amber'],
        ['the “user interface” is an API', 'your app embeds payments, SMS, maps, search', 'usage-based pricing, no seats'],
        [('Sign up', 'Create an account and API keys; test in a sandbox.', ''), ('Integrate', 'Your app calls the vendor’s API or SDK.', ''), ('Pay per use', 'Billing per transaction, message or request.', '')],
        'API-first SaaS in action', 'Software you call, not click.', 'API SaaS', 'Animation: sign up and get API keys; app calls the API; usage-based billing.', 's5anim')
T5 = vtype(5, 'API-first SaaS', 'blue',
    '<b>API-first SaaS</b> delivers a complete capability — payments, messaging, maps, identity, search, email — primarily through APIs and SDKs that developers embed in their own applications, typically with usage-based pricing, instead of offering an end-user interface.',
    'Hiring a courier company for every delivery: you do not build vans; you call them with an address and pay per parcel.',
    'TiffinGo’s app takes UPI and card payments through Razorpay’s API, sends OTPs through an SMS API and shows delivery routes with a maps API — three capabilities it would never build itself.',
    'Razorpay, Stripe, Twilio, SendGrid, Google Maps Platform, Algolia, Auth0/Okta CIC; cloud-provider APIs (Amazon SES, Azure Communication Services).',
    '', A5,
    'a capability is complex, regulated or not your core business (payments, messaging, identity).',
    'costs per call grow faster than your revenue — negotiate volume pricing or reconsider at scale.',
    plain='Ready-made services that programmers plug into their own apps — like payments or SMS — paying for each use.',
    how=[('Account', 'API keys, sandbox environment.'), ('Integrate', 'SDK or HTTPS calls; webhooks for results.'), ('Secure', 'Keys in a secret store; verify webhook signatures.'), ('Go live', 'KYC/compliance where required.'), ('Monitor', 'Usage, errors, costs.')],
    words=[('API key', 'a secret that identifies your app to the service'), ('webhook', 'the service calling your URL when something happens'), ('sandbox', 'a test mode with fake money/messages')],
    diff=table(['', 'API-first SaaS', 'End-user SaaS'], [['User', 'developers / your app', 'employees in a browser'], ['Pricing', 'per call/transaction', 'per user'], ['Example', 'payment gateway', 'accounting app']], minw=440),
    where=['Payments and UPI', 'SMS, WhatsApp, email notifications', 'Maps, search, identity'],
    realworld='India’s payment gateways (Razorpay, PayU, Cashfree) are API-first SaaS: they handle RBI compliance, card networks and UPI so merchants integrate a few API calls instead of becoming payment companies.',
    pro='API keys are the passwords of API-first SaaS: leaked keys in a public GitHub repo are found by bots within minutes. Use restricted keys, rotate them, and keep them in a secrets manager.')

A6 = mk(['Model the data', 'Drag and drop screens', 'Publish to users'], ['data|tables, sheets|or SaaS data', 'builder|forms, flows|no code', 'app|web + mobile|shared with team'], ['green', 'violet', 'blue'],
        ['start from a spreadsheet or table', 'build forms, approvals and automations visually', 'the app runs on the vendor’s SaaS platform'],
        [('Data', 'Start from tables, spreadsheets or existing SaaS data.', ''), ('Build', 'Assemble screens and workflows visually.', ''), ('Publish', 'The app is hosted and run by the vendor.', '')],
        'Low-code SaaS in action', 'Apps without programming.', 'Low-code', 'Animation: model data; drag-and-drop builder; app published to users.', 's6anim')
T6 = vtype(6, 'Low-code / no-code SaaS', 'green',
    '<b>Low-code / no-code SaaS platforms</b> let business users and developers build applications, forms, workflows and automations through visual designers on top of hosted data and connectors, with the vendor running the resulting apps as SaaS.',
    'Building with LEGO instead of carving wood: ready-made blocks snap together quickly — fine for many things, not for everything.',
    'TiffinGo’s kitchen manager built a daily stock-check app in an afternoon with Google AppSheet on top of a Google Sheet; Power Apps does the same on Microsoft 365.',
    'Microsoft Power Apps / Power Automate, Google AppSheet, Zoho Creator, Salesforce Platform, Airtable.',
    '', A6,
    'internal tools, forms and approvals that would otherwise wait months for developers.',
    'apps become business-critical with complex logic, scale or security needs — move them to proper development with tests and pipelines.',
    plain='Websites where you can make your own small apps by dragging and dropping, without writing much code.',
    how=[('Connect data', 'Sheets, tables, SaaS connectors.'), ('Design UI', 'Forms, lists, dashboards.'), ('Automate', 'Triggers, approvals, notifications.'), ('Secure', 'Sharing and roles via the organisation’s identity.'), ('Govern', 'IT sets policies (data loss prevention, environments).')],
    words=[('low-code', 'little programming needed'), ('citizen developer', 'a business user who builds apps'), ('connector', 'a ready-made link to another app')],
    diff=table(['', 'Low-code SaaS', 'Custom development'], [['Speed', 'hours–days', 'weeks–months'], ['Flexibility', 'platform limits', 'unlimited'], ['Who builds', 'business + IT', 'developers']], minw=440),
    where=['Internal tools and forms', 'Approvals and field data collection', 'Quick prototypes'],
    realworld='Microsoft reports that its Power Platform is used across most large enterprises, and governments use AppSheet/Power Apps for field surveys — showing how far low-code SaaS has moved beyond hobby use.',
    pro='Shadow IT risk: dozens of unmanaged low-code apps can hold customer data with weak sharing settings. Platform admins should enforce data-loss-prevention policies and environment rules from the start.')

A7 = mk(['Find in the marketplace', 'Subscribe with the cloud account', 'One bill'], ['listing|SaaS product|pricing plans', 'subscribe|cloud identity|private offer', 'billing|on cloud invoice|counts to commits'], ['amber', 'blue', 'green'],
        ['SaaS products listed inside the cloud console', 'procurement through your existing cloud agreement', 'charges appear on the AWS/Azure/GCP bill'],
        [('Find', 'Browse SaaS listings in the cloud marketplace.', ''), ('Subscribe', 'Subscribe using your cloud account; private offers for negotiated prices.', ''), ('Bill', 'Charges appear on the cloud bill and may count towards commitments.', '')],
        'Marketplace SaaS in action', 'Buy SaaS like a cloud service.', 'Marketplace', 'Animation: find a SaaS listing; subscribe through the cloud account; charges on the cloud bill.', 's7anim')
T7 = vtype(7, 'SaaS bought through cloud marketplaces', 'amber',
    '<b>Marketplace SaaS</b> is third-party SaaS listed and purchased through a cloud provider’s marketplace — AWS Marketplace, Microsoft Marketplace (Azure), Google Cloud Marketplace — using the customer’s cloud account for subscription and billing, often with private offers and eligibility to count towards cloud spending commitments.',
    'Buying from a mall instead of individual shops: one entry gate, one membership card, one bill — many brands inside.',
    'TiffinGo subscribes to a log-analytics SaaS through AWS Marketplace: no new vendor contract, the charge appears on the AWS invoice, and finance sees it under the same budget.',
    'AWS Marketplace, Microsoft Marketplace / Azure Marketplace, Google Cloud Marketplace (SaaS, containers, AMIs, data products).',
    '', A7,
    'you already have a cloud agreement and want faster procurement and consolidated billing.',
    'the marketplace price or terms are worse than buying direct — compare and use private offers.',
    plain='Buying online software through your cloud provider’s shop, so it is paid on the same cloud bill.',
    how=[('Discover', 'Search the marketplace by category.'), ('Evaluate', 'Free trials, pricing plans, reviews.'), ('Subscribe', 'Accept terms with the cloud account; SSO link to the vendor.'), ('Bill', 'Usage/contract charges on the cloud invoice.'), ('Govern', 'Private marketplace / approved products list.')],
    words=[('marketplace', 'an online store of third-party software'), ('private offer', 'a negotiated price for one customer'), ('procurement', 'the company process of buying')],
    diff=table(['', 'Marketplace purchase', 'Direct purchase'], [['Contract', 'standard or private offer via the cloud', 'separate vendor contract'], ['Billing', 'cloud invoice', 'vendor invoice'], ['Counts to cloud commitment', 'often yes', 'no']], minw=440),
    where=['Security, monitoring and data tools', 'Enterprise procurement', 'Start-up programmes'],
    realworld='Large enterprises increasingly route software purchases through cloud marketplaces because eligible spend can count towards their committed cloud spend agreements — turning the marketplace into a procurement channel, not just a catalogue.',
    pro='Admins can create a <b>private marketplace</b> (AWS) or restrict purchases (Azure, Google) so employees can only subscribe to approved SaaS — an easy control against shadow IT spend.')

SUMMARY = table(['#', 'SaaS kind', 'Key trait', 'Example', 'TiffinGo'], [
    ['1', 'Horizontal', 'any industry', 'Microsoft 365, Zoho', 'mail, accounting'], ['2', 'Vertical', 'one industry', 'restaurant/clinic SaaS', 'kitchen management'], ['3', 'Multi-tenant', 'shared app, isolated data', 'Freshdesk, Salesforce', 'support desk'],
    ['4', 'Single-tenant', 'dedicated instance', 'enterprise editions, BYOC', 'bank partner'], ['5', 'API-first', 'used from code', 'Razorpay, Twilio, Maps', 'payments, OTP'], ['6', 'Low-code', 'build apps visually', 'Power Apps, AppSheet', 'stock-check app'], ['7', 'Marketplace', 'bought via cloud bill', 'AWS/Azure/Google marketplaces', 'log analytics']], minw=640)
CHECK = ('  <h3>Check yourself: which SaaS kind?</h3>\n' +
    qx('A. A school wants attendance, fees and report cards in one tool.', ['Horizontal SaaS', 'Vertical SaaS', 'IaaS', 'DBaaS'], 1, 'Industry-specific.') +
    qx('B. A developer adds UPI payments to an app with a few API calls.', ['API-first SaaS', 'Low-code', 'Single-tenant', 'IaaS'], 0, 'Payment API.') +
    qx('C. A bank requires its own instance in Mumbai with its own keys.', ['Multi-tenant', 'Single-tenant SaaS', 'MBaaS', 'Private cloud IaaS only'], 1, 'Dedicated.') +
    qx('D. Finance wants a monitoring tool billed on the existing AWS invoice.', ['Direct contract', 'Marketplace SaaS', 'Low-code', 'Bare metal'], 1, 'Marketplace.'))

TYPES = ('  <p>Seven kinds of SaaS, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['What single missing line of SQL is the classic multi-tenant data leak?', 'Why did RBI rules push some SaaS vendors towards single-tenant deployments?', 'How do API keys usually leak?'], 'types 3, 4 and 5') + MAP
         + jump(['Horizontal', 'Vertical', 'Multi-tenant', 'Single-tenant', 'API-first', 'Low-code', 'Marketplace']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('Subscription / licence', 'What you pay for: seats, usage or tiers.', 'Drives cost and features.', 'Per user per month, per transaction, annual contracts.'),
    ('Single sign-on (SSO)', 'Log in with the company identity provider.', 'One place to enable MFA and remove leavers.', 'SAML/OIDC with Entra ID, Okta, Google, IAM Identity Center.'),
    ('SCIM provisioning', 'Automatic creation/removal of SaaS accounts from the IdP.', 'No forgotten ex-employee accounts.', 'Entra ID/Okta → SaaS user sync.'),
    ('Admin console', 'Where you set policies, roles and sharing.', 'Most SaaS risk is misconfiguration.', 'Microsoft 365 admin, Google Admin, Zoho admin.'),
    ('Data export / API', 'How to get your data out.', 'Your exit plan and backups.', 'CSV/JSON export, APIs, backup tools.'),
    ('SLA and status page', 'The vendor’s uptime promise and incident page.', 'Know what is promised and where to check.', 'status.* pages, SLA documents (Lesson 5.4).')])

DEEP = ('  <h3>NIST definition of SaaS</h3>\n  <p>NIST SP 800-145: “The capability provided to the consumer is to use the provider’s applications running on a cloud infrastructure. The applications are accessible from various client devices through either a thin client interface, such as a web browser, or a program interface. The consumer does not manage or control the underlying cloud infrastructure … with the possible exception of limited user-specific application configuration settings.”</p>\n'
    '  <h3>SaaS characteristics</h3>\n  <ul><li>Accessed over the internet from any device; nothing to install.</li><li>Subscription or usage pricing (OpEx).</li><li>Vendor-managed updates — everyone on the latest version.</li><li>Multi-tenant economics.</li><li>Configurable, not customisable at code level.</li></ul>\n'
    '  <h3>Evaluating a SaaS vendor (checklist)</h3>\n' + table(['Question', 'Why'], [['Where is our data stored (Region)?', 'DPDP Act, RBI, sector rules'], ['SSO, MFA and SCIM supported?', 'access control and leavers'], ['Certifications (ISO 27001, SOC 2)?', 'vendor security assurance'], ['SLA and credits?', 'availability promise'], ['Export and deletion on exit?', 'avoid lock-in, compliance'], ['Backup of our data?', 'vendor backups protect the service, not your mistakes']], minw=480))

clouds = vendor_tabs('<p><b>AWS:</b> SaaS-style services from AWS itself (Amazon Connect, Amazon Q Business, QuickSight), AWS Marketplace for third-party SaaS, IAM Identity Center for SSO to SaaS apps, SaaS Factory and SaaS Lens for vendors building SaaS on AWS.</p>',
    '<p><b>Azure / Microsoft:</b> Microsoft 365, Dynamics 365, Power Platform (SaaS); Microsoft Entra ID enterprise apps for SSO and SCIM to thousands of SaaS apps; Microsoft Marketplace; guidance for building multi-tenant SaaS on Azure.</p>',
    '<p><b>Google:</b> Google Workspace, Looker, AppSheet (SaaS); Cloud Identity / Workspace SAML apps for SSO; Google Cloud Marketplace; multi-tenancy guidance for vendors building SaaS.</p>') + \
    cloud3([['Business SaaS', 'Amazon Connect, Q Business', 'Microsoft 365, Dynamics 365', 'Google Workspace'], ['Low-code', 'App Studio', 'Power Apps', 'AppSheet'], ['SSO to SaaS apps', 'IAM Identity Center', 'Entra ID enterprise apps', 'Cloud Identity SAML apps'], ['Marketplace', 'AWS Marketplace', 'Microsoft Marketplace', 'Google Cloud Marketplace']])

# ------------------------------------------------------------------ practical
MOCKQ.extend([
 (mock('aws', ['AWS Marketplace', 'Discover products'], ['Discover products', 'Manage subscriptions', 'Private Marketplace', 'Vendor Insights'], 'Discover products',
       [('Search', 'helpdesk'), ('Delivery method', '[x] SaaS'), ('Pricing model', '[x] Free trial')], 'View purchase options'),
  mock('az', ['Home', 'Marketplace'], ['Get Started', 'Service Providers', 'Management', 'My Marketplace'], 'Get Started',
       [('Search the Marketplace', 'helpdesk'), ('Product type', '▾ SaaS'), ('Pricing', '▾ Free trial')], 'Subscribe'),
  mock('gcp', ['Marketplace', 'Browse'], ['Browse', 'Your products', 'Your orders'], 'Browse',
       [('Search', 'helpdesk'), ('Type', '[x] SaaS'), ('Price', '[x] Free trial')], 'Subscribe')),
 (mock('aws', ['IAM Identity Center', 'Applications', 'Add application'], ['Dashboard', 'Users', 'Groups', 'Applications', 'Settings'], 'Applications',
       [('Setup preference', '( ) I want to select an application from the catalog'), ('Application catalog', 'search “Salesforce” / “Slack” / “Zoom”'), ('Then', 'assign users or groups')], 'Next'),
  mock('az', ['Home', 'Microsoft Entra ID', 'Enterprise applications', 'Browse gallery'], ['Overview', 'Users', 'Groups', 'Enterprise applications'], 'Enterprise applications',
       [('Search application', 'Zoom'), ('Name', 'Zoom (TiffinGo)'), ('Then', 'Single sign-on → SAML · Users and groups → Assign')], 'Create'),
  mock('gcp', ['Google Admin console', 'Apps', 'Web and mobile apps'], ['Users', 'Groups', 'Apps', 'Security'], 'Apps',
       [('Add app', '▾ Search for apps'), ('Search', 'Zoom (SAML)'), ('Service status', 'ON for TiffinGo staff')], 'Continue')),
 (mock('aws', ['Billing and Cost Management', 'Cost Explorer'], ['Home', 'Bills', 'Cost Explorer', 'Budgets'], 'Cost Explorer',
       [('Filters · Billing entity', 'AWS Marketplace'), ('Group by', '▾ Service')], 'Apply'),
  mock('az', ['Home', 'Cost Management', 'Cost analysis'], ['Overview', 'Cost analysis', 'Budgets', 'Invoices'], 'Cost analysis',
       [('Filter · Publisher type', 'Marketplace'), ('Group by', '▾ Service name')], 'Apply'),
  mock('gcp', ['Billing', 'Reports'], ['Overview', 'Reports', 'Cost table', 'Budgets & alerts'], 'Reports',
       [('Filters · Services', 'Marketplace products'), ('Group by', '▾ Service')], 'Apply')),
])

STEP1 = ('1 · Find a SaaS product in your cloud marketplace', tri(
    (['Console search → [[AWS Marketplace]] → [[Discover products]] → search <code>helpdesk</code>, filter delivery method [[SaaS]] and pricing [[Free trial]].', 'Open a listing: read [[Pricing]], [[Usage information]], [[Support]] and the vendor’s data-location statement.', 'Do not subscribe unless you want to; [[Manage subscriptions]] shows what your account already uses.'],
     "# The catalogue is browsed in the UI; the CLI shows what you already subscribed to (billing by entity):\naws ce get-cost-and-usage --time-period Start=$(date -d '-30 days' +%F),End=$(date +%F) --granularity MONTHLY \\\n  --metrics UnblendedCost --filter '{\"Dimensions\":{\"Key\":\"BILLING_ENTITY\",\"Values\":[\"AWS Marketplace\"]}}'",
     'listings with SaaS delivery and trial options; the CLI shows $0 Marketplace spend on a new account.'),
    (['Portal search → [[Marketplace]] → search <code>helpdesk</code> → product type [[SaaS]].', 'Open a listing: [[Plans + Pricing]], [[Overview]], publisher information.', '[[Cost Management]] later shows SaaS charges under publisher type Marketplace.'],
     '# Browsing is UI-only; list Marketplace charges on your subscription:\naz consumption marketplace list --top 10 --output table',
     'SaaS listings with plans; the CLI shows no Marketplace usage on a new subscription.'),
    (['[[Marketplace]] → filter type [[SaaS]] → search <code>helpdesk</code>.', 'Open a product: pricing, [[Overview]], [[Support]]. [[Your orders]] shows subscriptions.'],
     '# Google Cloud Marketplace browsing has no gcloud command; check which APIs/products are enabled in the project:\ngcloud services list --enabled --format="value(config.title)" | head',
     'SaaS listings; your enabled Google services in the project.')),
    'Compare a marketplace listing with buying directly — same product, different contract and billing path.')

STEP2 = ('2 · Connect a SaaS app to single sign-on', tri(
    (['[[IAM Identity Center]] → [[Enable]] (if not yet) → [[Applications]] → [[Add application]] → [[I want to select an application from the catalog]].', 'Search a SaaS app (e.g. Zoom, Slack, Salesforce) → note the SAML settings it needs → [[Submit]] → [[Assign users and groups]].', 'Users then see the app in the AWS access portal; disabling a user in Identity Center removes access to all assigned apps.'],
     "INST=$(aws sso-admin list-instances --query 'Instances[0].InstanceArn' --output text)\naws sso-admin list-application-providers --query 'ApplicationProviders[].DisplayData.DisplayName' --output text | tr '\\t' '\\n' | head -20\naws sso-admin list-applications --instance-arn $INST --query 'Applications[].Name'",
     'catalog application names (e.g. Salesforce, Slack, Zoom) and the applications already configured in your instance.'),
    (['[[Microsoft Entra ID]] → [[Enterprise applications]] → [[New application]] → search the gallery (e.g. Zoom) → [[Create]].', 'Open it → [[Single sign-on]] → [[SAML]] (shows the values to paste in the SaaS admin) → [[Users and groups]] → [[Add user/group]].', '[[Provisioning]] (for apps that support SCIM) creates and removes SaaS accounts automatically.'],
     'az rest --method get --url "https://graph.microsoft.com/v1.0/applicationTemplates?\\$filter=displayName eq \'Zoom\'" --query "value[].{id:id, name:displayName}"\n# create an instance of the gallery app (use the id from above):\naz rest --method post --url "https://graph.microsoft.com/v1.0/applicationTemplates/TEMPLATE_ID/instantiate" --body \'{"displayName":"Zoom (TiffinGo)"}\'\naz ad sp list --display-name "Zoom (TiffinGo)" --query "[].{name:displayName, appId:appId}" --output table',
     'the gallery template, then a new enterprise application and service principal “Zoom (TiffinGo)”. The free Entra ID tier supports SSO for gallery apps.'),
    (['SSO to SaaS is configured in the Google Admin console (Cloud Identity Free or Workspace): [[Apps]] → [[Web and mobile apps]] → [[Add app]] → [[Search for apps]].', 'Pick a SAML app (e.g. Zoom), copy the IdP details into the SaaS admin, then turn the service [[ON]] for a group.', 'Disabling the user in Admin console blocks every SAML app at once.'],
     '# SAML app setup has no gcloud command (it lives in the Admin console / Admin SDK).\n# Check which Google identity you are using and its organisation:\ngcloud config get-value account\ngcloud organizations list',
     'your account and, if you use Cloud Identity/Workspace, your organisation ID.')),
    'SSO is the single most important SaaS control: one place for MFA, one switch for leavers.')

STEP3 = ('3 · See your SaaS spend in one place', tri(
    (['[[Billing and Cost Management]] → [[Cost Explorer]] → filter [[Billing entity]] = AWS Marketplace, group by service.', '[[Budgets]] → create a budget filtered to Marketplace spend.'],
     "aws ce get-cost-and-usage --time-period Start=$(date -d '-90 days' +%F),End=$(date +%F) --granularity MONTHLY \\\n  --metrics UnblendedCost --group-by Type=DIMENSION,Key=BILLING_ENTITY --output table",
     'costs split into “AWS” and “AWS Marketplace” per month.'),
    (['[[Cost Management]] → [[Cost analysis]] → add filter [[Publisher type]] = Marketplace → group by service name.', 'Microsoft 365/Dynamics licences appear in the Microsoft 365 admin center billing instead.'],
     'az consumption marketplace list --top 20 --query "[].{product:offerName, cost:pretaxCost, date:usageStart}" --output table',
     'Marketplace line items (empty on a new subscription).'),
    (['[[Billing]] → [[Reports]] → filter services to Marketplace products, group by service.', 'Workspace subscriptions are billed in the Google Admin console billing section.'],
     '# Detailed SaaS cost queries use the billing export to BigQuery; list your billing accounts:\ngcloud billing accounts list',
     'your billing account(s); Marketplace products appear as services in Reports.')),
    'Finance’s question “what SaaS do we pay for?” is easier to answer when purchases go through one channel.')

prac = practical(OWN_INTRO + ' Nothing here costs money unless you choose to subscribe to a paid SaaS product.', [SETUP_STEP, STEP1, STEP2, STEP3],
    cleanup='<b>AWS:</b> IAM Identity Center → Applications → select the test app → [[Actions]] → [[Delete]] (or keep it).<br><b>Azure:</b> [[Enterprise applications]] → the test app → [[Properties]] → [[Delete]], or <code>az ad sp delete --id APP_ID</code>.<br><b>Google:</b> Admin console → the SAML app → [[Delete app]]. Cancel any SaaS trial you started in a marketplace.'.replace('[[', '<b>').replace(']]', '</b>'))

mist = mistakes([
    ['Believing the vendor handles all security.', 'Misreading SaaS shared responsibility.', 'Own identity, MFA, sharing settings and data.'],
    ['Separate passwords for every SaaS app.', 'Quick sign-ups.', 'SSO + SCIM through one identity provider.'],
    ['No exit plan.', 'Easy to start, hard to leave.', 'Check export formats and contract terms before buying.'],
    ['Assuming the vendor backs up your data for you.', 'Service backups ≠ your restore needs.', 'Use retention features or third-party backup for critical SaaS data.'],
    ['Shadow IT: teams buying SaaS on personal cards.', 'Slow procurement.', 'Approved catalogue, marketplace, SaaS management.'],
    ['Leaked API keys for API-first SaaS.', 'Keys in code.', 'Secrets manager, restricted keys, rotation.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'SaaS: definition, characteristics, examples, multi-tenancy, benefits and challenges.'], ['AWS CLF-C02', 'Identify SaaS vs PaaS vs IaaS; AWS Marketplace; IAM Identity Center for SSO.'], ['AZ-900', 'Describe SaaS and its shared responsibility; use cases (Microsoft 365, Dynamics 365); Entra ID.'], ['Google Cloud Digital Leader', 'Google Workspace as SaaS; choosing SaaS vs building; Marketplace.']], minw=560) + \
    qx('1. Microsoft 365 is an example of…', ['IaaS', 'PaaS', 'SaaS', 'on-premises'], 2, 'SaaS.') + \
    qx('2. In SaaS, the customer is still responsible for…', ['patching servers', 'data and user access', 'the application code', 'data centre power'], 1, 'Data + identities.') + \
    qx('3. Serving many customers from one shared application instance with isolated data is…', ['single tenancy', 'multi-tenancy', 'virtualization', 'bare metal'], 1, 'Multi-tenant.') + \
    qx('4. Which AWS service lists third-party software including SaaS you can buy with your AWS account?', ['AWS Marketplace', 'AWS Artifact', 'AWS Config', 'Amazon S3'], 0, 'Marketplace.') + \
    qx('5. A main benefit of SaaS is…', ['full control of the OS', 'no software installation or maintenance for the customer', 'no internet needed', 'unlimited customisation of code'], 1, 'Vendor-managed.') + \
    qx('6. Which Microsoft service provides SSO to thousands of SaaS apps?', ['Azure DNS', 'Microsoft Entra ID', 'Azure Files', 'Azure Batch'], 1, 'Entra ID.')

proj = miniproject('Mini project: TiffinGo’s SaaS inventory and access review',
    'Take control of the SaaS your company already uses.',
    ['<b>Inventory:</b> list every SaaS app (mail, accounting, support, design, payments) with owner, cost and number of users.',
     '<b>Classify:</b> horizontal/vertical, multi/single-tenant, API-first, low-code, marketplace.',
     '<b>Responsibility table:</b> for each app, what is the vendor’s and what is yours.',
     '<b>SSO plan:</b> which apps support SAML/OIDC and SCIM; prioritise the ones with sensitive data.',
     '<b>Prove one:</b> connect one SaaS app to SSO in your identity provider (step 2).',
     '<b>Exit plan:</b> for the two most critical apps, how would you export your data?'],
    'An inventory, a responsibility table, an SSO roadmap and one working SSO connection.', 'This lesson + 2.1–2.2 + 5.4 (SLAs).')

assemble_v2(HERE, story_h2='Six apps, zero servers', hook_html=hk,
    narration='TiffinGo runs on SaaS — mail, accounts, support, design, payments, meetings. One day the support tool went down; another day an ex-employee still had access. Two incidents, two different owners.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='What is SaaS?',
    formal='<b>Software as a Service (SaaS)</b> is a cloud service model in which the provider delivers a complete application running on cloud infrastructure, accessed by users over the internet through a browser, app or API, typically on a subscription or usage basis; the consumer does not manage the infrastructure, platform or application, apart from limited user-specific configuration — but remains responsible for its users, access settings and data.',
    simple='Ready-made software you use over the internet and pay for monthly — the company that makes it runs everything; you just log in and use it.',
    interview=['“SaaS is complete software delivered over the internet — Microsoft 365, Salesforce, Zoho. The vendor manages infrastructure, platform, code and updates; the customer manages users, access, configuration and data.”', '“Most SaaS is multi-tenant: one application serves many customers with logical data isolation; enterprises may buy single-tenant editions.”'],
    terms_rows=[('SaaS', 'Software over the internet.'), ('Tenant', 'Customer organisation.'), ('Multi-tenancy', 'Shared app, isolated data.'), ('Horizontal SaaS', 'All industries.'), ('Vertical SaaS', 'One industry.'), ('SSO', 'One login for many apps.'), ('SCIM', 'Automatic user provisioning.'), ('API-first SaaS', 'Used from code.'), ('Low-code', 'Visual app building.'), ('Marketplace', 'Buy via cloud account.')],
    exam='Expect “classify this service” (SaaS vs PaaS vs IaaS), shared responsibility for SaaS, and Marketplace/Entra ID/Identity Center questions.',
    picture_h2='The SaaS responsibility line, and multi-tenancy', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven kinds of SaaS, one by one', TYPES)],
    how_h2='One SaaS login, from browser to your data', how_intro='How a multi-tenant SaaS serves your company.', how_anim=FLOW,
    parts_h2='Six things every SaaS admin manages', parts_html=parts, lv='',
    myth_rows=[('The vendor is responsible for everything.', 'Identity, access and data stay yours.', 'Responsibility figure.'), ('SaaS data is automatically backed up for me.', 'Service backups protect the vendor’s service; plan your own retention/backup.', 'Mistakes.'), ('SaaS cannot be customised.', 'It is configured, extended via APIs and low-code — not changed at code level.', 'Types 5–6.')],
    extra_secs=[('deep', 'Deep dive', 'NIST definition, SaaS characteristics, vendor evaluation checklist', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Define SaaS and its shared responsibility.', 'Explain horizontal, vertical, multi-tenant, single-tenant, API-first, low-code and marketplace SaaS.', 'Describe how multi-tenant SaaS isolates customers.', 'Connect a SaaS app to single sign-on.', 'Find SaaS spend and evaluate a SaaS vendor.'],
    next_html='<a href="../04-serverless-faas-and-xaas/">2.4 Serverless, FaaS and XaaS</a>.',
    pre='<b>Before you start:</b> <a href="../02-paas-platform-as-a-service-and-its-types/">2.2 PaaS</a>.')
