import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)


hk = hook('A hospital chain wants TiffinGo to plan patient diets. Its rule: “patient data never leaves our own servers”. A government school scheme wants meal tracking on the government cloud. And the TiffinGo website runs on AWS. Is that three clouds, or one?',
    'It is one company using several <b>deployment models</b> — the answer to “<i>who owns and shares the cloud, and where does it run?</i>”. NIST defines four: <b>public</b>, <b>private</b>, <b>community</b> and <b>hybrid</b>; industry adds <b>hosted private</b> and <b>sovereign</b> clouds. This lesson explains each one with the same pattern, shows how a hybrid request really travels, and on <b>your own</b> account you build a private network inside a public cloud, keep data inside India, and register your “office” for a hybrid link — all free.',
    ['Service model (IaaS/PaaS/SaaS) answers <i>what</i> you rent; deployment model answers <i>who shares it and where</i>.', 'Why “private cloud” is about who uses it, not where the building is.', 'How India’s government cloud (MeghRaj) is a community cloud.'])

def story_scene():
    o = t(180, 12, 'One company, three kinds of cloud', 9, 'ink', bold=True)
    o += box(8, 26, 108, 70, 'green', rx=8) + t(62, 46, 'Public cloud', 8, 'ink', bold=True) + t(62, 62, 'website, app', 7, 'ink2') + t(62, 76, 'AWS Mumbai', 7, 'ink2')
    o += box(126, 26, 108, 70, 'violet', rx=8) + t(180, 46, 'Private cloud', 8, 'ink', bold=True) + t(180, 62, 'hospital diet data', 7, 'ink2') + t(180, 76, 'their data centre', 7, 'ink2')
    o += box(244, 26, 108, 70, 'amber', rx=8) + t(298, 46, 'Community cloud', 8, 'ink', bold=True) + t(298, 62, 'school meal scheme', 7, 'ink2') + t(298, 76, 'government cloud', 7, 'ink2')
    o += arrow(116, 61, 126, 61) + t(180, 118, 'Connected securely = hybrid', 8, 'ink', bold=True)
    return o
scene_svg = scene('Three boxes: public cloud for the website, private cloud for hospital diet data, community cloud for a government school meal scheme; connected securely they form a hybrid.', story_scene(), 'Decide the <tspan font-weight="700" class="s-acc">deployment model</tspan> per workload, like the service model.', h=130)
dialogue = '''R> Sir, the hospital says their data cannot go to AWS. Do we lose the contract?
A> No. Their diet records stay in their private cloud. Our planning app stays in the public cloud. We connect the two with an encrypted link — that is hybrid.
K> And the school scheme? They sent a list of “MeitY-empanelled” providers.
A> That is a community cloud: built for government departments with shared rules. Same technology, different owners and rules.
R> So public, private, community, hybrid… what decides which one?
A> Who uses it, who controls it, and where the data must live. Let’s go one by one.'''

# ------------------------------------------------------------------ picture
def ownfig():
    o = t(320, 16, 'Who uses it, who runs it, where it lives', 11, 'ink', bold=True)
    cols = [('Public', 'green', 'anyone (many tenants)', 'provider', 'provider’s Regions'), ('Private', 'violet', 'one organisation', 'you or a partner', 'your DC or a dedicated area'),
            ('Community', 'amber', 'a group with shared rules', 'members or a provider', 'provider or member DCs'), ('Hybrid', 'blue', '2+ models joined', 'mixed', 'both, connected')]
    o += t(70, 52, 'Used by', 8, 'ink', bold=True) + t(70, 98, 'Operated by', 8, 'ink', bold=True) + t(70, 144, 'Runs in', 8, 'ink', bold=True)
    for i, (n, tn, a, b, c) in enumerate(cols):
        x = 132 + i * 124
        o += box(x, 24, 114, 18, tn, rx=4) + t(x + 57, 37, n, 8.4, 'ink', bold=True)
        for j, v in enumerate([a, b, c]):
            o += box(x, 44 + j * 46, 114, 36, 'card', rx=5) + t(x + 57, 66 + j * 46, v, 6.9, 'ink')
    o += t(320, 196, 'NIST SP 800-145 defines these four. The building does not decide “private” — exclusive use does.', 7.4, 'ink2')
    return o
OWN = bigfig('Comparison grid: public cloud used by anyone and run by the provider; private by one organisation; community by a group with shared rules; hybrid joins two or more models.', ownfig(), h=208)

def axfig():
    o = t(320, 16, 'Service model × deployment model: two separate questions', 11, 'ink', bold=True)
    rows = ['IaaS', 'PaaS', 'SaaS']; cols = ['Public', 'Private', 'Community', 'Hybrid']
    ex = [['EC2, Azure VMs', 'OpenStack, VMware', 'GovCloud VMs', 'Outposts, Azure Local'], ['App Service, Cloud Run', 'OpenShift on-prem', 'MeghRaj PaaS', 'Arc-enabled services'], ['Gmail, Microsoft 365', 'self-hosted Nextcloud', 'GCC (US gov 365)', 'M365 + on-prem Exchange']]
    for j, c in enumerate(cols): o += t(176 + j * 118, 42, c, 8.2, 'ink', bold=True)
    for i, r in enumerate(rows):
        o += box(14, 52 + i * 46, 100, 38, 'blue', rx=5) + t(64, 75 + i * 46, r, 8.6, 'ink', bold=True)
        for j in range(4): o += box(120 + j * 118, 52 + i * 46, 112, 38, 'card', rx=5) + t(176 + j * 118, 75 + i * 46, ex[i][j], 6.8, 'ink')
    o += t(320, 202, 'Every cell is real: any service model can be delivered in any deployment model.', 7.4, 'ink2')
    return o
AX = bigfig('A grid with service models IaaS, PaaS, SaaS as rows and deployment models public, private, community, hybrid as columns, with an example product in every cell.', axfig(), h=212)

picture = ('  <p>Lesson 2 asked <i>what</i> you rent (IaaS, PaaS, SaaS). This module asks <i>who shares it and where it runs</i>. Three questions decide the model:</p>\n' + OWN +
           '\n  <p>The two questions are independent — every combination exists:</p>\n' + AX +
           '\n  <h3>Trade-offs in one table</h3>\n' + table(['', 'Public', 'Private', 'Community', 'Hybrid'], [
               ['Up-front cost', 'none', 'high (hardware, people)', 'shared among members', 'medium'], ['Scale', 'practically unlimited', 'limited to what you bought', 'limited, shared', 'burst to public'],
               ['Control', 'lowest', 'highest', 'shared', 'per part'], ['Compliance fit', 'good (certifications)', 'strict rules, legacy', 'sector rules (gov, health)', 'keep sensitive part private'],
               ['Ops effort', 'lowest', 'highest', 'medium', 'highest (two worlds)'], ['Example', 'TiffinGo website', 'hospital EHR', 'MeghRaj, AWS GovCloud', 'TiffinGo + hospital']], minw=640))

# ------------------------------------------------------------------ how: hybrid request
RN = {'u': (4, 54, 50, 50, 'phone', 'Dietitian', 'browser'), 'web': (66, 4, 62, 46, 'cloud', 'Planner app', 'AWS Mumbai'), 'idp': (66, 104, 62, 46, 'shield', 'Identity', 'single sign-on'),
      'vpn': (142, 54, 60, 50, 'lb', 'VPN gateway', 'encrypted'), 'fw': (216, 4, 62, 46, 'gear', 'Firewall', 'hospital edge'), 'db': (216, 104, 62, 46, 'db', 'Diet records', 'private cloud'), 'res': (292, 54, 64, 50, 'chart', 'Plan', 'no raw data out')}
RS = [dict(on=['u', 'idp'], hot='idp', move=(54, 79, 70, 126, 'login'), head='Step 1 · Sign in once', text='The dietitian logs in with the hospital’s own identity (Entra ID / SAML). The same', text2='identity works in the public app and the private systems.', svc='Shared identity is the glue of every hybrid cloud'),
      dict(on=['u', 'idp', 'web'], hot='web', move=(54, 79, 70, 30, 'HTTPS'), head='Step 2 · The planner runs in the public cloud', text='The diet-planning app (TiffinGo’s code) runs on AWS in Mumbai and scales with', text2='demand — no hardware at the hospital.', svc='Public side: elastic compute, pay per use'),
      dict(on=['web', 'vpn'], hot='vpn', move=(128, 30, 152, 66, 'IPsec'), head='Step 3 · A private, encrypted path', text='The app asks for patient diet restrictions through a site-to-site VPN (or Direct', text2='Connect / ExpressRoute / Interconnect) — never over the open internet.', svc='AWS Site-to-Site VPN · Azure VPN Gateway · Google Cloud VPN'),
      dict(on=['vpn', 'fw'], hot='fw', move=(202, 70, 226, 40, 'check'), head='Step 4 · The hospital’s firewall decides', text='Only the planner’s private IP range on port 443 to one API is allowed in. Every', text2='call is logged for the hospital’s auditors.', svc='Least privilege on both ends of the link'),
      dict(on=['fw', 'db'], hot='db', move=(247, 50, 247, 104, 'query'), head='Step 5 · Data stays in the private cloud', text='The API returns only what is needed (e.g. “low-salt, no gluten”), not the full medical', text2='record. Raw patient data never leaves the hospital.', svc='Data minimisation: send answers, not records'),
      dict(on=['db', 'res', 'web', 'u'], hot='res', move=(278, 127, 300, 90, 'plan'), head='Step 6 · The result comes back', text='The planner builds the weekly menu and shows it to the dietitian. Public scale +', text2='private data control = the reason hybrid exists.', svc='Hybrid = two models, one secure workflow')]
HYB = flow_anim('How a hybrid request really travels', 'TiffinGo’s planner in the public cloud uses diet rules from the hospital’s private cloud.', 'Hybrid request', 'Animation: sign in with shared identity; planner runs in the public cloud; encrypted VPN path; hospital firewall checks; only minimal data leaves the private database; result returns to the dietitian.', RN, RS, hid='hybflow')

# ------------------------------------------------------------------ types
def mapfig():
    o = t(320, 16, 'Six deployment models you will meet', 11, 'ink', bold=True)
    items = [('1', 'Public', 'shared, provider-run', 'green'), ('2', 'Private (on-premises)', 'one org, own DC', 'violet'), ('3', 'Hosted / dedicated private', 'one org, provider DC', 'blue'),
             ('4', 'Community', 'shared by a group', 'amber'), ('5', 'Hybrid', '2+ models connected', 'blue'), ('6', 'Sovereign', 'local control and law', 'red')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 3) * 208; y = 32 + (i // 3) * 84
        o += box(x, y, 198, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 106, y + 34, a, 8.4, 'ink', bold=True) + t(x + 106, y + 54, b, 7, 'ink2')
    o += t(320, 210, '1, 2, 4 and 5 are NIST’s four. 3 and 6 are industry variants you will see in exams and job descriptions.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of six deployment models: public, private on-premises, hosted or dedicated private, community, hybrid, sovereign.', mapfig(), h=222)

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

A1 = mk(['Shared hardware', 'Isolated tenants', 'Pay per use'], ['provider|huge Regions|millions of servers', 'tenants|your account|isolated by software', 'you|self-service|by the second'], ['green', 'blue', 'green'],
        ['the provider owns and runs data centres worldwide', 'hypervisors and networks keep tenants apart', 'sign up with a card, use, pay only for what you use'],
        [('Provider', 'The provider owns and runs the data centres.', ''), ('Tenants', 'Many customers share hardware, isolated by virtualization and networks.', ''), ('Use', 'Self-service, elastic, pay per use.', '')],
        'Public cloud in action', 'Rent from a shared pool.', 'Public cloud', 'Animation: provider-owned hardware; isolated tenants; pay-per-use self-service.', 'p1anim')
T1 = vtype(1, 'Public cloud', 'green',
    'A <b>public cloud</b> is cloud infrastructure provisioned for open use by the general public; it is owned, managed and operated by a cloud provider and exists on the provider’s premises, with resources shared among many customers (tenants) who are isolated from each other.',
    'A city bus or metro: anyone can ride, you pay per trip, and the transport company maintains the vehicles.',
    'TiffinGo’s website, order API and analytics run on AWS in Mumbai: no hardware bought, capacity doubles on Diwali weekend and drops after.',
    'AWS, Microsoft Azure, Google Cloud, Oracle Cloud, IBM Cloud, Alibaba Cloud; Indian providers such as Yotta, CtrlS, Tata Communications.',
    'Multi-tenancy and isolation are explained in Lesson 5.2.', A1,
    'you want speed, global reach, elasticity and no capital spending.',
    'a law or contract requires exclusive hardware or a specific location the provider cannot offer.',
    plain='Cloud services anyone can sign up for, run by a big provider on shared machines.',
    how=[('Sign up', 'Account + payment method.'), ('Choose Region', 'Where resources run.'), ('Provision', 'Console, CLI or API.'), ('Isolation', 'Hypervisor, VPC, IAM separate tenants.'), ('Billing', 'Metered per second / request / GB.')],
    words=[('tenant', 'one customer sharing the provider’s infrastructure'), ('Region', 'a geographic area with data centres'), ('self-service', 'you create resources yourself, no ticket to a vendor')],
    diff=table(['', 'Public', 'Private'], [['Who uses it', 'anyone', 'one organisation'], ['Cost model', 'opex, pay per use', 'capex + running costs'], ['Scale', 'huge, instant', 'what you bought']], minw=420),
    where=['Start-ups and digital products', 'Web, mobile and analytics', 'Dev/test environments'],
    realworld='Public clouds hold certifications such as ISO 27001, SOC 2 and PCI DSS — and in India MeitY empanelment — so regulated companies (banks, insurers) also run large workloads on them.',
    pro='“Shared” does not mean “less secure”: logical isolation is audited, and options like dedicated hosts, confidential computing and customer-managed keys raise isolation further without leaving the public cloud.')

A2 = mk(['Own data centre', 'Cloud software', 'Internal self-service'], ['hardware|servers, storage|you own', 'cloud stack|OpenStack / VMware|virtualization + portal', 'teams|request VMs|in minutes'], ['violet', 'blue', 'green'],
        ['the organisation buys and runs its own hardware', 'a cloud platform pools it and adds automation', 'internal teams get self-service, metered resources'],
        [('Hardware', 'The organisation owns servers, storage and network.', ''), ('Stack', 'A cloud platform (OpenStack, VMware, Azure Local) pools it.', ''), ('Self-service', 'Teams create resources through a portal or API.', '')],
        'Private cloud in action', 'Cloud features, one owner.', 'Private cloud', 'Animation: own hardware; cloud software stack; internal self-service.', 'p2anim')
T2 = vtype(2, 'Private cloud (on-premises)', 'violet',
    'A <b>private cloud</b> is cloud infrastructure provisioned for exclusive use by a single organisation; it may be owned, managed and operated by the organisation, a third party or both, and may exist on or off premises. An on-premises private cloud runs in the organisation’s own data centre with a cloud platform providing pooling, self-service and metering.',
    'Owning a car: it is only yours and you choose everything — but you pay for it, park it, insure and service it.',
    'The hospital chain runs patient records on an OpenStack private cloud in its own Pune data centre; departments get VMs from an internal portal.',
    'OpenStack, VMware Cloud Foundation, Nutanix, Red Hat OpenShift, Microsoft Azure Local, Apache CloudStack.',
    'Lesson 3.2 builds a private cloud step by step.', A2,
    'strict control, special hardware, steady predictable load or data that legally must stay on site.',
    'demand is spiky, the team is small, or speed matters more than control.',
    plain='Your own cloud, used only by your organisation, usually in your own building.',
    how=[('Buy & rack', 'Servers, storage, network.'), ('Virtualize', 'Hypervisor cluster.'), ('Cloud layer', 'Portal, API, quotas, metering.'), ('Automate', 'Templates and IaC.'), ('Operate', 'Patching, capacity, DR — all yours.')],
    words=[('on-premises', 'in your own building / data centre'), ('capex', 'capital expenditure — buying assets up front'), ('OpenStack', 'open-source software to build a cloud')],
    diff=table(['', 'Private cloud', 'Traditional data centre'], [['Self-service', 'yes (portal/API)', 'tickets'], ['Pooling', 'yes', 'servers per project'], ['Metering', 'yes', 'rarely']], minw=420),
    where=['Hospitals and banks with legacy systems', 'Defence and research', 'Telecom networks'],
    realworld='Many large banks and telecom operators run OpenStack or VMware private clouds for core systems while using public cloud for digital channels.',
    pro='A virtualized data centre is not automatically a private cloud — NIST’s five characteristics (self-service, broad access, pooling, elasticity, metering) are the test.')

A3 = mk(['Dedicated hardware', 'Provider runs it', 'Only you use it'], ['provider DC|dedicated racks|single tenant', 'managed|patching, hardware|by provider', 'you|private network|exclusive'], ['blue', 'green', 'violet'],
        ['hardware set aside for one customer in a provider’s facility', 'the provider operates the hardware and often the platform', 'private-cloud control without owning a building'],
        [('Dedicated', 'Hardware is reserved for one customer in the provider’s data centre.', ''), ('Managed', 'The provider runs hardware (and often the platform).', ''), ('Exclusive', 'The customer gets private-cloud control without a building.', '')],
        'Hosted private cloud in action', 'Private, but not in your building.', 'Hosted private', 'Animation: dedicated hardware in a provider DC; managed by the provider; used only by one customer.', 'p3anim')
T3 = vtype(3, 'Hosted / dedicated private cloud', 'blue',
    'A <b>hosted (managed or dedicated) private cloud</b> is a private cloud whose hardware is located in, and often operated by, a third-party provider’s data centre but dedicated to a single customer — for example dedicated hosts, VMware-based clouds on provider bare metal, or provider-installed racks.',
    'Renting a whole floor of an office building: only your company works there, but the landlord handles power, lifts and security.',
    'A pharma customer of TiffinGo runs its lab systems on Azure VMware Solution: dedicated bare-metal hosts, its own vCenter, inside Azure’s Central India Region.',
    'Azure VMware Solution, Google Cloud VMware Engine, AWS Dedicated Hosts and Outposts, IBM Cloud for VMware, managed private clouds from Indian DC providers.',
    'Relocating VMware estates is the “relocate” R in Lesson 2.5.', A3,
    'you need dedicated hardware or licensing but do not want to run a data centre.',
    'shared public cloud already meets the rules — dedicated hardware costs much more.',
    plain='A private cloud on machines reserved only for you, but kept and run in someone else’s data centre.',
    how=[('Order', 'Dedicated hosts / private cloud nodes.'), ('Provision', 'Provider racks and connects them.'), ('Connect', 'Private links to your network.'), ('Operate', 'Split duties: provider hardware, you workloads.'), ('Exit', 'Contracts often 1–3 years.')],
    words=[('dedicated host', 'a physical server used only by one customer'), ('single tenant', 'no other customer on the hardware'), ('managed', 'the provider does the operations work')],
    diff=table(['', 'Hosted private', 'On-premises private'], [['Building', 'provider’s', 'yours'], ['Hardware ops', 'provider', 'you'], ['Capex', 'low', 'high']], minw=420),
    where=['Per-socket/per-core licensing needs', 'VMware estates leaving their DC', 'Regulated workloads needing dedicated hardware'],
    realworld='AWS Outposts puts AWS-run racks inside the customer’s own data centre — a “private” deployment operated by the public provider, often counted as hybrid.',
    pro='Exam trap: NIST says a private cloud “may exist on or off premises” — location does not define it; exclusive use does.')

A4 = mk(['Shared mission', 'Common rules', 'Shared platform'], ['members|ministries, banks|hospitals', 'rules|security, audits|data location', 'community cloud|shared by members|cost shared'], ['amber', 'red', 'green'],
        ['organisations with the same mission or regulator', 'they agree on security, compliance and policies', 'one platform serves all of them, costs are shared'],
        [('Members', 'Organisations share a mission or regulator.', ''), ('Rules', 'They agree common security and compliance requirements.', ''), ('Platform', 'One cloud serves the group; costs and governance are shared.', '')],
        'Community cloud in action', 'Shared by a group with shared rules.', 'Community cloud', 'Animation: members with a shared mission; common rules; a shared platform.', 'p4anim')
T4 = vtype(4, 'Community cloud', 'amber',
    'A <b>community cloud</b> is cloud infrastructure provisioned for exclusive use by a specific community of organisations that have shared concerns — such as mission, security requirements, policy or compliance; it may be owned and operated by one or more members, a third party, or a combination, on or off premises.',
    'A housing society’s shared gym: only residents can use it, they agree the rules together and share the cost.',
    'The state’s mid-day meal scheme asks TiffinGo to use a MeitY-empanelled government community cloud: only government departments and their vendors use it, under the government’s security rules.',
    'MeghRaj / GI Cloud (India, through MeitY-empanelled providers), AWS GovCloud (US), Azure Government, Google Cloud for US government (Assured Workloads), sector clouds for healthcare or finance.',
    '', A4,
    'several organisations share strict, identical rules and want to share cost and effort.',
    'members’ needs differ a lot — governance becomes slow and the platform pleases nobody.',
    plain='A cloud shared only by a group of organisations that follow the same rules, like government departments.',
    how=[('Define community', 'Who may join.'), ('Agree policies', 'Security, data location, audits.'), ('Choose operator', 'A member or a provider.'), ('Onboard', 'Vetted members and vendors.'), ('Govern', 'Shared board, shared costs.')],
    words=[('empanelled', 'officially approved to supply (e.g. by MeitY)'), ('compliance', 'following laws and rules'), ('GovCloud', 'a cloud area restricted to government users and vetted staff')],
    diff=table(['', 'Community', 'Public'], [['Who may use', 'vetted members only', 'anyone'], ['Rules', 'set by the community', 'set by the provider'], ['Typical price', 'higher', 'lower']], minw=420),
    where=['Government departments', 'Healthcare networks', 'Research and universities'],
    realworld='India’s MeghRaj (GI Cloud) initiative lets ministries and states procure cloud from MeitY-empanelled providers that meet government security and audit requirements — a community-cloud model built on commercial providers.',
    pro='Many “community clouds” today are logically separated Regions of public providers (GovCloud, Azure Government) — the community is defined by access rules and personnel screening, not by separate technology.')

A5 = mk(['Two environments', 'Secure link + one identity', 'Workloads move'], ['private + public|on-prem DC|cloud Region', 'connect|VPN / Direct Connect|SSO, policies', 'use|burst, DR, split|data stays put'], ['violet', 'blue', 'green'],
        ['an on-premises or private cloud plus a public cloud', 'private network links and shared identity, management and security', 'apps use both: burst, backup, keep sensitive data private'],
        [('Two sides', 'A private (or on-premises) environment and a public cloud.', ''), ('Join', 'Private connectivity, shared identity, unified management.', ''), ('Use', 'Burst to cloud, DR, or keep sensitive parts private.', '')],
        'Hybrid cloud in action', 'Two worlds, one operation.', 'Hybrid cloud', 'Animation: private and public environments; secure connection and shared identity; workloads use both.', 'p5anim')
T5 = vtype(5, 'Hybrid cloud', 'blue',
    'A <b>hybrid cloud</b> is a composition of two or more distinct cloud infrastructures (private, community or public) that remain unique entities but are bound together by standardised or proprietary technology that enables data and application portability — for example cloud bursting for load balancing between clouds.',
    'Living in your own house but renting a banquet hall for the wedding: everyday life at home, extra capacity rented when needed — with one family managing both.',
    'TiffinGo’s planner (AWS) reads diet rules from the hospital’s private cloud over a VPN, both using the hospital’s single sign-on — the animation above.',
    'AWS Outposts, Site-to-Site VPN, Direct Connect, Systems Manager hybrid nodes; Azure Arc, Azure Local, ExpressRoute; Google Distributed Cloud, GKE Enterprise, Cloud Interconnect.',
    'Lesson 3.3 compares hybrid with multi-cloud in depth.', A5,
    'part of the system must stay on-premises (data, latency, legacy) but you want cloud elasticity for the rest.',
    'two environments double the operations work without a clear reason — the link itself is a failure point.',
    plain='Using your own private systems and a public cloud together, connected safely as one setup.',
    how=[('Network', 'VPN or dedicated link, no overlapping IPs.'), ('Identity', 'One directory / SSO.'), ('Management', 'One tool for both (Arc, SSM, GKE Enterprise).'), ('Data', 'Decide what stays and what syncs.'), ('Operate', 'Monitoring and security across both.')],
    words=[('cloud bursting', 'sending overflow load to the public cloud'), ('site-to-site VPN', 'encrypted tunnel between two networks'), ('SSO', 'single sign-on — one login for many systems')],
    diff=table(['', 'Hybrid', 'Multi-cloud'], [['Combines', 'private + public', 'two+ public providers'], ['Main reason', 'keep some on-prem', 'best-of-breed, risk'], ['Can overlap?', 'yes — hybrid multi-cloud is common', '']], minw=420),
    where=['Banks, hospitals, manufacturers', 'Disaster recovery to cloud', 'Gradual migrations'],
    realworld='Surveys of large enterprises consistently find most of them run hybrid environments — the norm, not the exception, because migrations take years.',
    pro='Overlapping private IP ranges between the office and the VPC are the commonest hybrid project blocker — plan IP addressing before the first VPC is created.')

A6 = mk(['Local law', 'Local control', 'Cloud services'], ['law|data protection|national rules', 'control|local operators|keys, staff, location', 'services|cloud features|inside the border'], ['red', 'amber', 'green'],
        ['laws require data and operations under national control', 'local staff, local keys, and data kept in the country', 'with modern cloud services instead of old systems'],
        [('Law', 'National rules on data, access and control.', ''), ('Control', 'Data, keys, operations and support stay under local control.', ''), ('Services', 'Cloud capabilities delivered inside those limits.', '')],
        'Sovereign cloud in action', 'Cloud under local control.', 'Sovereign cloud', 'Animation: local law; local control of data, keys and staff; cloud services inside the border.', 'p6anim')
T6 = vtype(6, 'Sovereign cloud', 'red',
    'A <b>sovereign cloud</b> is a cloud deployment designed so that data, operations and control remain under the jurisdiction of a specific country or region — through data residency, local operations staff, customer-held encryption keys and legal and technical guarantees against foreign access.',
    'A bank locker in your own city’s branch with your own key: the bank runs the vault, but the box, the key and the law are local.',
    'A state health mission asks that patient nutrition data be stored only in India, with encryption keys held by the state and support from India-based staff — a sovereignty requirement on top of the deployment model.',
    'AWS European Sovereign Cloud, Microsoft Cloud for Sovereignty, Google sovereign cloud offerings with local partners; Indian Regions with customer-managed keys and India-only support options.',
    'Data residency controls are in practical step 3.', A6,
    'national law, defence or critical-infrastructure rules demand local control beyond residency.',
    'ordinary residency (choose an Indian Region) already satisfies the requirement — sovereign offerings cost more and can lag on features.',
    plain='A cloud set up so that a country’s data stays in that country and is controlled under its laws.',
    how=[('Residency', 'Data stored only in-country.'), ('Keys', 'Customer- or locally-held keys (HSM).'), ('Operations', 'Local staff and support.'), ('Legal', 'Contracts against foreign access.'), ('Audit', 'Independent verification.')],
    words=[('data residency', 'where data is physically stored'), ('jurisdiction', 'which country’s laws apply'), ('HSM', 'hardware security module that guards encryption keys')],
    diff=table(['', 'Sovereign', 'Data residency only'], [['Data location', 'in-country', 'in-country'], ['Keys and staff', 'local control', 'provider default'], ['Cost', 'higher', 'normal']], minw=420),
    where=['Government and defence', 'Critical infrastructure', 'Highly regulated industries'],
    realworld='India’s Digital Personal Data Protection Act, 2023 and sector rules (for example RBI’s payment-data storage direction) drive Indian companies to choose Indian Regions and customer-managed keys.',
    pro='Residency ≠ sovereignty: a Mumbai Region keeps data in India, but sovereignty also asks who can be legally compelled to access it — that is why key ownership (BYOK/HYOK) matters.')

SUMMARY = table(['#', 'Model', 'Used by', 'Located', 'TiffinGo example'], [
    ['1', 'Public', 'anyone', 'provider Regions', 'website, order API'], ['2', 'Private (on-prem)', 'one org', 'own DC', 'hospital patient records'], ['3', 'Hosted private', 'one org', 'provider DC, dedicated', 'pharma VMware on AVS'],
    ['4', 'Community', 'members with shared rules', 'provider or member DCs', 'school meal scheme (MeghRaj)'], ['5', 'Hybrid', 'mix', 'both, connected', 'planner + hospital data'], ['6', 'Sovereign', 'jurisdiction-bound users', 'in-country, local control', 'state health mission']], minw=600)
CHECK = ('  <h3>Check yourself: which model?</h3>\n' +
    qx('A. A start-up runs everything on Google Cloud.', ['Public', 'Private', 'Community', 'Hybrid'], 0, 'Shared provider cloud.') +
    qx('B. Several state hospitals share one cloud built to health-data rules.', ['Hybrid', 'Community', 'Public', 'Private'], 1, 'Shared concerns.') +
    qx('C. A bank keeps core banking on-prem and runs its mobile app on Azure, connected by ExpressRoute.', ['Hybrid', 'Community', 'Public', 'Sovereign'], 0, 'Two models joined.') +
    qx('D. One company’s OpenStack cloud in a colocation facility, used only by it.', ['Public', 'Private', 'Community', 'Multi-cloud'], 1, 'Exclusive use.'))

TYPES = ('  <p>Each model in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['Is a private cloud defined by where the hardware sits?', 'Why are overlapping IP ranges a hybrid-cloud problem?', 'What does sovereignty add on top of data residency?'], 'types 2–3, 5 and 6') + MAP
         + jump(['Public', 'Private', 'Hosted', 'Community', 'Hybrid', 'Sovereign']) + T1 + T2 + T3 + T4 + T5 + T6
         + '\n  <h3 style="margin-top:34px">All six side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('Ownership', 'Who owns the hardware.', 'Decides capex vs opex and who refreshes servers.', 'Own DC vs provider.'),
    ('Tenancy', 'Who shares the hardware.', 'Shared (multi-tenant) vs dedicated (single-tenant).', 'Dedicated hosts cost more.'),
    ('Location', 'Where data physically lives.', 'Residency rules (DPDP Act, RBI, sector rules).', 'Choose Region; restrict others.'),
    ('Operations', 'Who patches, monitors, repairs.', 'Ops skills and cost.', 'Provider vs your team.'),
    ('Connectivity', 'How environments connect.', 'Hybrid needs private, reliable links.', 'VPN, Direct Connect, ExpressRoute, Interconnect.'),
    ('Governance', 'Who sets the rules.', 'Community clouds share governance.', 'Policies, audits, access.')])

DEEP = ('  <h3>NIST’s exact wording, and why it matters in exams</h3>\n  <p>NIST SP 800-145 lists four deployment models — private, community, public, hybrid — and says private and community clouds “may exist on or off premises”. Exams test this: a private cloud hosted by a provider is still private. “Virtual private cloud” (AWS/Google VPC) is <i>not</i> a private cloud — it is an isolated network inside the public cloud.</p>\n'
    '  <h3>Hybrid building blocks</h3>\n' + table(['Need', 'AWS', 'Azure', 'Google Cloud'], [
        ['Encrypted link over internet', 'Site-to-Site VPN', 'VPN Gateway', 'Cloud VPN (HA VPN)'], ['Private dedicated link', 'Direct Connect', 'ExpressRoute', 'Cloud Interconnect'],
        ['Cloud services on-prem', 'Outposts', 'Azure Local', 'Google Distributed Cloud'], ['Manage on-prem servers', 'Systems Manager hybrid nodes', 'Azure Arc', 'GKE Enterprise (clusters)'], ['Identity', 'IAM Identity Center + AD', 'Entra ID + AD Connect', 'Cloud Identity + GCDS']], minw=600) +
    '\n  <h3>Choosing: a quick scoring method</h3>\n  <ol><li>List rules: residency, exclusivity, audit, latency to local equipment.</li><li>If no rule forbids it → public (fastest, cheapest to start).</li><li>If a sector community exists with your rules → community.</li><li>If something must stay on-prem → hybrid, keeping only that part private.</li><li>If exclusive hardware is required → hosted/dedicated private before building your own.</li><li>If foreign legal access is a concern → sovereign options and customer-held keys.</li></ol>\n'
    '  <h3>Cost reality of private clouds</h3>\n  <p>A private cloud has to be sized for peak plus failures (N+1), refreshed every 4–6 years, and run by skilled staff around the clock. It is cheapest only when utilisation stays high and steady for years — which is why most organisations end up hybrid.</p>')

clouds = vendor_tabs('<p><b>AWS:</b> public Regions (incl. Mumbai, Hyderabad); GovCloud (US) as a community cloud; Dedicated Hosts and Outposts for dedicated/on-prem; European Sovereign Cloud; hybrid via Site-to-Site VPN, Direct Connect, Systems Manager hybrid nodes.</p>',
    '<p><b>Azure:</b> public Regions (Central/South/West India); Azure Government; Azure Local and Azure VMware Solution for private/hosted; Microsoft Cloud for Sovereignty; hybrid via Azure Arc, VPN Gateway, ExpressRoute.</p>',
    '<p><b>Google Cloud:</b> public Regions (Mumbai, Delhi); Assured Workloads for regulated/government needs; Google Distributed Cloud (connected and air-gapped) for on-prem; Google Cloud VMware Engine; hybrid via Cloud VPN, Interconnect, GKE Enterprise.</p>') + \
    cloud3([['Government cloud', 'GovCloud (US)', 'Azure Government', 'Assured Workloads'], ['Cloud on-prem', 'Outposts', 'Azure Local', 'Google Distributed Cloud'], ['Dedicated hardware', 'Dedicated Hosts', 'Dedicated Host', 'Sole-tenant nodes'], ['Hybrid management', 'Systems Manager', 'Azure Arc', 'GKE Enterprise'], ['Private link', 'Direct Connect', 'ExpressRoute', 'Cloud Interconnect']])

# ------------------------------------------------------------------ practical
MOCKQ.extend([
 (mock('aws', ['Account', 'AWS Regions'], ['Account', 'AWS Regions', 'Billing'], 'AWS Regions',
       [('Asia Pacific (Mumbai) ap-south-1', 'Enabled by default'), ('Asia Pacific (Hyderabad) ap-south-2', 'Disabled  [Enable]'), ('Region selector (top right)', '▾ Asia Pacific (Mumbai)')], 'Enable'),
  mock('az', ['Home', 'Subscriptions', 'Resource providers'], ['Overview', 'Resource providers', 'Usage + quotas'], 'Overview',
       [('Locations available', 'Central India · South India · West India · …'), ('Default location', '▾ Central India')], 'Refresh'),
  mock('gcp', ['IAM & Admin', 'Settings'], ['IAM', 'Organization policies', 'Settings'], 'Settings',
       [('Project', 'tiffingo-lab'), ('Regions', 'asia-south1 (Mumbai) · asia-south2 (Delhi) · …')], 'Save')),
 (mock('aws', ['VPC', 'Create VPC'], ['Your VPCs', 'Subnets', 'Route tables', 'Internet gateways'], 'Your VPCs',
       [('Resources to create', '[x] VPC only'), ('Name tag', 'private-only'), ('IPv4 CIDR', '10.50.0.0/16')], 'Create VPC'),
  mock('az', ['Home', 'Virtual networks', 'Create virtual network'], ['Basics', 'Security', 'IP addresses', 'Tags', 'Review + create'], 'IP addresses',
       [('Address space', '10.50.0.0/16'), ('Subnet', 'app · 10.50.1.0/24'), ('Private subnet (no default outbound)', '[x] Enable')], 'Review + create'),
  mock('gcp', ['VPC network', 'Create a VPC network'], ['VPC networks', 'Firewall', 'Routes'], 'VPC networks',
       [('Name', 'private-only'), ('Subnet creation mode', '[x] Custom'), ('Subnet', 'app · asia-south1 · 10.50.1.0/24')], 'Create')),
 (mock('aws', ['IAM', 'Users', 'your-user', 'Add permissions'], ['Permissions', 'Groups', 'Security credentials'], 'Permissions',
       [('Create inline policy', 'JSON'), ('Effect', 'Deny'), ('Condition', 'aws:RequestedRegion ≠ ap-south-1, ap-south-2')], 'Create policy'),
  mock('az', ['Home', 'Policy', 'Assign policy'], ['Overview', 'Definitions', 'Assignments', 'Compliance'], 'Assignments',
       [('Scope', 'rg-deploy'), ('Policy definition', 'Allowed locations'), ('Allowed locations', 'Central India, South India, West India')], 'Review + create'),
  mock('gcp', ['IAM & Admin', 'Organization policies'], ['IAM', 'Organization policies', 'Quotas'], 'Organization policies',
       [('Constraint', 'Google Cloud Platform - Resource Location Restriction'), ('Allowed', 'in:asia-south1-locations, in:asia-south2-locations')], 'Set policy')),
 (mock('aws', ['VPC', 'Customer gateways', 'Create'], ['Customer gateways', 'Virtual private gateways', 'Site-to-Site VPN connections'], 'Customer gateways',
       [('Name', 'office-pune'), ('BGP ASN', '65000'), ('IP address', '203.0.113.10 (your office router)')], 'Create customer gateway'),
  mock('az', ['Home', 'Local network gateways', 'Create'], ['Basics', 'Advanced', 'Tags'], 'Basics',
       [('Name', 'office-pune'), ('Endpoint', 'IP address · 203.0.113.10'), ('Address space', '192.168.10.0/24')], 'Review + create'),
  mock('gcp', ['Network Connectivity', 'VPN', 'Peer VPN gateways'], ['Cloud VPN gateways', 'Cloud VPN tunnels', 'Peer VPN gateways'], 'Peer VPN gateways',
       [('Name', 'office-pune'), ('Interfaces', 'one · 203.0.113.10')], 'Create')),
])

POL = '{"Version":"2012-10-17","Statement":[{"Sid":"IndiaOnly","Effect":"Deny",\n "NotAction":["iam:*","sts:*","organizations:*","account:*","support:*","budgets:*","ce:*","cloudfront:*","route53:*","health:*"],\n "Resource":"*","Condition":{"StringNotEquals":{"aws:RequestedRegion":["ap-south-1","ap-south-2"]}}}]}'

STEP1 = ('1 · See where the public cloud can put your data', tri(
    (['Click the Region selector (top right) — note Mumbai and Hyderabad.', 'Account menu → [[Account]] → [[AWS Regions]]: newer Regions such as Hyderabad must be [[Enable]]d before use.'],
     "aws ec2 describe-regions --all-regions --query \"Regions[?starts_with(RegionName,'ap-south')].[RegionName,OptInStatus]\" --output table",
     '<code>ap-south-1  opt-in-not-required</code> and <code>ap-south-2  not-opted-in</code> (or <code>opted-in</code>). Public cloud = you choose the Region; the provider runs the buildings.'),
    (['Search [[Subscriptions]] → your subscription → [[Resource providers]] / any Create blade → the Region list shows India Regions.'],
     'az account list-locations --query "[?metadata.geographyGroup==\'Asia Pacific\' && contains(displayName,\'India\')].{name:name,display:displayName}" -o table',
     '<code>centralindia</code>, <code>southindia</code>, <code>westindia</code> (and others where available).'),
    (['Any Create page → [[Region]] dropdown: asia-south1 (Mumbai), asia-south2 (Delhi).'],
     'gcloud compute regions list --filter="name~^asia-south" --format="table(name,status)"',
     '<code>asia-south1 UP</code> and <code>asia-south2 UP</code> (enable the Compute Engine API if prompted).')),
    'Data residency starts with a Region choice — every later step builds on it.')

STEP2 = ('2 · Build a private network inside the public cloud', tri(
    (['[[VPC]] → [[Create VPC]] → [[VPC only]], name <code>private-only</code>, CIDR <code>10.50.0.0/16</code> → [[Create VPC]].', 'Add a subnet. Do <b>not</b> attach an internet gateway — nothing in it can reach or be reached from the internet.'],
     'VPC=$(aws ec2 create-vpc --cidr-block 10.50.0.0/16 --tag-specifications \'ResourceType=vpc,Tags=[{Key=Name,Value=private-only}]\' --query Vpc.VpcId --output text)\naws ec2 create-subnet --vpc-id $VPC --cidr-block 10.50.1.0/24 --availability-zone ap-south-1a --query Subnet.SubnetId --output text\naws ec2 describe-internet-gateways --filters Name=attachment.vpc-id,Values=$VPC --query \'length(InternetGateways)\'',
     'a <code>vpc-…</code> and <code>subnet-…</code> ID, then <code>0</code> internet gateways. This is a <b>virtual private cloud</b> — isolated, but still public-cloud infrastructure (not a “private cloud”).'),
    (['[[Virtual networks]] → [[Create]] → resource group <code>rg-deploy</code>, name <code>private-only</code>, Central India.', '[[IP addresses]]: <code>10.50.0.0/16</code>, subnet <code>app 10.50.1.0/24</code> with [[Private subnet]] enabled (no default outbound internet).'],
     'az group create -n rg-deploy -l centralindia\naz network vnet create -g rg-deploy -n private-only --address-prefixes 10.50.0.0/16 \\\n  --subnet-name app --subnet-prefixes 10.50.1.0/24\naz network vnet subnet update -g rg-deploy --vnet-name private-only -n app --default-outbound false\naz network vnet subnet show -g rg-deploy --vnet-name private-only -n app --query defaultOutboundAccess',
     'JSON for the VNet, then <code>false</code> — the subnet has no implicit internet access.'),
    (['[[VPC network]] → [[Create VPC network]] → name <code>private-only</code>, [[Custom]] subnets → <code>app</code>, asia-south1, <code>10.50.1.0/24</code> → [[Create]].', 'Add no firewall rule allowing ingress and no Cloud NAT — the network is private.'],
     'gcloud compute networks create private-only --subnet-mode=custom\ngcloud compute networks subnets create app --network=private-only --region=asia-south1 --range=10.50.1.0/24 --enable-private-ip-google-access\ngcloud compute firewall-rules list --filter="network:private-only"',
     'the network and subnet created, and <b>no</b> firewall rules listed (implied deny-all ingress).')),
    'Exam trap: a VPC/VNet is an isolated network in the <b>public</b> cloud — not a private cloud.')

STEP3 = ('3 · Keep data inside India (residency guard-rail)', tri(
    (['[[IAM]] → [[Users]] → your admin user (not root) → [[Add permissions]] → [[Create inline policy]] → [[JSON]] → paste the policy on the right → name <code>india-only</code>.', 'Test: switch the console to N. Virginia and open EC2 — you get “not authorized”.'],
     f"cat > india-only.json <<'EOF'\n{POL}\nEOF\nME=$(aws sts get-caller-identity --query Arn --output text | awk -F/ '{{print $NF}}')\naws iam put-user-policy --user-name $ME --policy-name india-only --policy-document file://india-only.json\nsleep 10; aws ec2 describe-vpcs --region us-east-1 2>&1 | tail -1\naws ec2 describe-vpcs --region ap-south-1 --query 'length(Vpcs)'",
     '<code>An error occurred (UnauthorizedOperation)…</code> for us-east-1, and a number for ap-south-1. Companies apply the same rule to every account with an Organizations <b>SCP</b>. Global services (IAM, billing, CloudFront, Route 53) are excluded so the console still works.'),
    (['[[Policy]] → [[Assignments]] → [[Assign policy]] → scope <code>rg-deploy</code> → definition [[Allowed locations]] → [[Parameters]]: Central India, South India, West India → [[Review + create]].'],
     'az policy assignment create --name india-only --resource-group rg-deploy \\\n  --policy e56962a6-4747-49cd-b67b-bf8b01975c4c \\\n  --params \'{"listOfAllowedLocations":{"value":["centralindia","southindia","westindia"]}}\'\nsleep 60; az network vnet create -g rg-deploy -n test-us -l eastus --address-prefixes 10.60.0.0/16 2>&1 | grep -o RequestDisallowedByPolicy',
     '<code>RequestDisallowedByPolicy</code> — creating anything outside India in this resource group is blocked (new assignments can take a few minutes to apply).'),
    (['[[IAM &amp; Admin]] → [[Organization policies]] → [[Resource Location Restriction]] → allow <code>in:asia-south1-locations</code> and <code>in:asia-south2-locations</code>.', 'This needs an <b>organisation</b> (company Google Workspace / Cloud Identity). On a personal account, just set India defaults and check the effective policy.'],
     'P=$(gcloud config get-value project)\ngcloud config set compute/region asia-south1\ngcloud config set compute/zone asia-south1-a\ngcloud org-policies describe gcp.resourceLocations --project=$P --effective',
     'the region/zone set, then the effective constraint (empty <code>spec</code> on a personal project = no restriction; with an organisation you would see the India value groups).')),
    'Residency guard-rails turn “please use Mumbai” into a rule nobody can break by mistake — the basis of community and sovereign requirements.')

STEP4 = ('4 · Register your “office” for a hybrid link (free objects only)', tri(
    (['[[VPC]] → [[Customer gateways]] → [[Create customer gateway]]: name <code>office-pune</code>, BGP ASN 65000, IP <code>203.0.113.10</code> (a documentation address standing in for your office router).', 'Do <b>not</b> create the Site-to-Site VPN connection — that part is billed per hour.'],
     'CGW=$(aws ec2 create-customer-gateway --type ipsec.1 --bgp-asn 65000 --public-ip 203.0.113.10 \\\n  --tag-specifications \'ResourceType=customer-gateway,Tags=[{Key=Name,Value=office-pune}]\' --query CustomerGateway.CustomerGatewayId --output text)\naws ec2 describe-customer-gateways --customer-gateway-ids $CGW --query \'CustomerGateways[0].[CustomerGatewayId,IpAddress,State]\' --output text',
     '<code>cgw-…  203.0.113.10  available</code>. The next (paid) steps would be a virtual private gateway on the VPC and a VPN connection between them.'),
    (['[[Local network gateways]] → [[Create]]: name <code>office-pune</code>, IP <code>203.0.113.10</code>, address space <code>192.168.10.0/24</code> → [[Create]].', 'Do <b>not</b> create a Virtual network gateway in the lab — it bills hourly and takes 30+ minutes.'],
     'az network local-gateway create -g rg-deploy -n office-pune --gateway-ip-address 203.0.113.10 \\\n  --local-address-prefixes 192.168.10.0/24\naz network local-gateway show -g rg-deploy -n office-pune --query "{ip:gatewayIpAddress,prefix:localNetworkAddressSpace.addressPrefixes[0],state:provisioningState}"',
     '<code>203.0.113.10</code>, <code>192.168.10.0/24</code>, <code>Succeeded</code>. Note the office range does not overlap the VNet’s 10.50.0.0/16 — essential for hybrid routing.'),
    (['[[Network Connectivity]] → [[VPN]] → [[Peer VPN gateways]] → [[Create]]: name <code>office-pune</code>, one interface <code>203.0.113.10</code>.', 'Do <b>not</b> create HA VPN tunnels in the lab — tunnels bill hourly.'],
     'gcloud compute external-vpn-gateways create office-pune --interfaces=0=203.0.113.10\ngcloud compute external-vpn-gateways describe office-pune --format="value(name,interfaces[0].ipAddress,redundancyType)"',
     '<code>office-pune 203.0.113.10 SINGLE_IP_INTERNALLY_REDUNDANT</code>.')),
    'Hybrid starts with describing the other side: its public IP and private address range — no overlap with your cloud network.')

prac = practical(OWN_INTRO + ' Everything here is free: no VMs, no VPN tunnels. You will see the public-cloud footprint, build a private network inside it, enforce India-only residency, and register an on-premises site for a hybrid link.', [SETUP_STEP, STEP1, STEP2, STEP3, STEP4],
    cleanup='<b>AWS:</b> <code>aws ec2 delete-customer-gateway --customer-gateway-id $CGW</code>; delete the subnet (<code>aws ec2 describe-subnets --filters Name=vpc-id,Values=$VPC</code> → <code>delete-subnet</code>) and <code>aws ec2 delete-vpc --vpc-id $VPC</code>; <code>aws iam delete-user-policy --user-name $ME --policy-name india-only</code> (or keep it as a guard-rail). '
            '<b>Azure:</b> <code>az policy assignment delete --name india-only --resource-group rg-deploy</code>, then <code>az group delete -n rg-deploy --yes --no-wait</code>. '
            '<b>Google Cloud:</b> <code>gcloud compute external-vpn-gateways delete office-pune --quiet</code>, <code>gcloud compute networks subnets delete app --region=asia-south1 --quiet</code>, <code>gcloud compute networks delete private-only --quiet</code>.')

mist = mistakes([
    ['Calling a VPC/VNet a “private cloud”.', 'The word “private”.', 'A VPC is an isolated network in a public cloud; private cloud = exclusive infrastructure.'],
    ['Thinking private cloud must be on-premises.', 'Everyday meaning.', 'NIST: private and community clouds may be on or off premises.'],
    ['Choosing private cloud “for security” by default.', 'Fear of sharing.', 'Compare controls and certifications; public clouds are often more secure than small private ones.'],
    ['Overlapping IP ranges between office and cloud.', 'Everyone uses 10.0.0.0/16.', 'Plan an IP address map before building the first network.'],
    ['Residency by policy document only.', 'No technical guard-rail.', 'Enforce with SCPs/IAM, Azure Policy, org policies (step 3).'],
    ['Hybrid without shared identity and monitoring.', 'Network-only thinking.', 'Plan identity, management and security across both sides.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Cloud deployment models: public, private, hybrid, community — features, pros and cons.'], ['AWS CLF-C02', 'Deployment models (cloud, on-premises, hybrid); AWS Outposts, Direct Connect, VPN; Region selection for compliance.'], ['AZ-900', 'Define public, private and hybrid cloud; use cases; Azure Arc and Azure Local for hybrid.'], ['Google Cloud Digital Leader', 'Hybrid and multi-cloud, Google Distributed Cloud, GKE Enterprise, data sovereignty.']], minw=560) + \
    qx('1. Infrastructure used exclusively by one organisation but hosted in a provider’s data centre is…', ['public cloud', 'private cloud', 'community cloud', 'not a cloud'], 1, 'Exclusive use defines private.') + \
    qx('2. Which service runs AWS infrastructure inside a customer’s own data centre?', ['AWS Outposts', 'Amazon CloudFront', 'AWS Snowball', 'Amazon VPC'], 0, 'Outposts.') + \
    qx('3. Several government agencies sharing a cloud built to the same security rules is…', ['hybrid', 'community', 'public', 'multi-cloud'], 1, 'Community.') + \
    qx('4. A company keeps a database on-premises and runs its web tier in Azure, connected privately. This is…', ['public', 'hybrid', 'community', 'private'], 1, 'Hybrid.') + \
    qx('5. Which Azure service manages on-premises and other-cloud servers from Azure?', ['Azure Arc', 'Azure DevOps', 'Azure Monitor only', 'Azure Front Door'], 0, 'Arc.') + \
    qx('6. Which is a benefit of public cloud over private cloud?', ['no up-front hardware cost and rapid elasticity', 'full control of hardware', 'no shared responsibility', 'no internet needed'], 0, 'Capex → opex, elasticity.')

proj = miniproject('Mini project: deployment-model plan for TiffinGo’s three customers',
    'Decide and justify the deployment model for each workload, and design the guard-rails.',
    ['<b>List</b> TiffinGo’s workloads: website, order API, analytics, hospital diet planner, school meal tracker.',
     '<b>Rules:</b> for each, write residency, exclusivity and audit requirements.',
     '<b>Decide</b> a deployment model (and service model) per workload with one line why.',
     '<b>Hybrid design:</b> draw the hospital link: IP ranges (no overlap), VPN/dedicated link, identity, what data crosses.',
     '<b>Guard-rails:</b> write the India-only policy for your chosen cloud (step 3) and who approves exceptions.',
     '<b>Cost note:</b> estimate the monthly cost of a VPN connection/gateway in your cloud with the pricing calculator.'],
    'A one-page deployment plan with a hybrid diagram and a residency policy.', 'Module 2 (service models) + 3.1 + 6.3 (networking).')

assemble_v2(HERE, story_h2='The hospital that would not move its data', hook_html=hk,
    narration='TiffinGo signed two new customers in one week: a hospital chain whose patient data must stay on its own servers, and a state school-meal scheme that must use the government cloud. Its own website already ran on AWS.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Public, private, hybrid and community cloud',
    formal='A <b>cloud deployment model</b> describes how cloud infrastructure is provisioned and who may use it. NIST SP 800-145 defines four: <b>public</b> (open use by the general public, on the provider’s premises), <b>private</b> (exclusive use by a single organisation, on or off premises), <b>community</b> (exclusive use by a community of organisations with shared concerns) and <b>hybrid</b> (a composition of two or more distinct cloud infrastructures bound together by technology that enables data and application portability).',
    simple='Public = shared cloud anyone can rent; private = a cloud only your organisation uses; community = shared by a group with the same rules; hybrid = two of these joined together.',
    interview=['“A deployment model says who uses the cloud and where it runs: public, private, community or hybrid (NIST). Private means exclusive use — it can even be hosted by a provider.”', '“For example, we keep patient data in the hospital’s private cloud and run the planning app on AWS, connected by a site-to-site VPN with shared SSO — a hybrid design.”'],
    terms_rows=[('Deployment model', 'Who uses the cloud and where.'), ('Public cloud', 'Shared, provider-run.'), ('Private cloud', 'Exclusive to one organisation.'), ('Community cloud', 'Shared by a group with shared concerns.'), ('Hybrid cloud', 'Two or more models bound together.'), ('Sovereign cloud', 'Under a jurisdiction’s control.'), ('Data residency', 'Where data is stored.'), ('VPC', 'Isolated network in a public cloud.')],
    exam='Expect scenario questions (“which deployment model?”), Outposts / Azure Local / Arc / Google Distributed Cloud for hybrid, and the trap that private cloud may be off-premises.',
    picture_h2='Who uses it, who runs it, where it lives', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Six deployment models, one by one', TYPES)],
    how_h2='How a hybrid request really travels', how_intro='Public scale with private data — step by step.', how_anim=HYB,
    parts_h2='Six factors behind every deployment model', parts_html=parts, lv='',
    myth_rows=[('Private cloud = on-premises.', 'Private means exclusive use; it can be hosted.', 'NIST definition.'), ('Public cloud is insecure because it is shared.', 'Isolation is engineered and audited.', 'Type 1.'), ('A VPC is a private cloud.', 'It is a private network in a public cloud.', 'Step 2.')],
    extra_secs=[('deep', 'Deep dive', 'NIST wording, hybrid building blocks, choosing, private-cloud cost', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Define the four NIST deployment models and two industry variants.', 'Separate service model from deployment model.', 'Explain how a hybrid request travels securely.', 'Build a private network, enforce India-only residency and register an on-prem site on your own account.', 'Choose a deployment model per workload with reasons.'],
    next_html='<a href="../02-building-a-private-cloud/">3.2 Building a private cloud</a>.',
    pre='<b>Before you start:</b> Module 2 (service models).')
