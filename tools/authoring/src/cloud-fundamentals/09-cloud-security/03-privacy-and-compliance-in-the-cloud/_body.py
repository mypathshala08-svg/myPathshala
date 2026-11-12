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


hk = hook('A TiffinGo customer emails: “Delete all my data — my address, my orders, my phone number.” The data sits in a database, three S3 buckets, logs, analytics in BigQuery and last month’s backups. Can TiffinGo prove it was deleted everywhere?',
    'That is <b>privacy</b> (people’s rights over their personal data) meeting <b>compliance</b> (proving you follow laws and standards). In India the <b>Digital Personal Data Protection Act, 2023</b> and its <b>Rules (notified November 2025)</b> now set those duties; banks follow RBI, cloud users follow CERT-In directions, and global customers bring GDPR, PCI DSS, HIPAA, ISO 27001 and SOC 2. This lesson explains seven frameworks one by one, animates an erasure request across a cloud system, and on <b>your own</b> account you detect personal data, set retention so data does not live forever, and keep audit logs as Indian rules require.',
    ['Privacy is about <i>using</i> data correctly; security is about <i>protecting</i> it.', 'Why “where is the data?” is the hardest compliance question in the cloud.', 'Certifications of the provider ≠ your compliance.'])

def story_scene():
    o = t(180, 12, 'One erasure request, six places', 9, 'ink', bold=True)
    P = [('Orders DB', 'blue'), ('S3 receipts', 'amber'), ('App logs', 'violet'), ('BigQuery', 'green'), ('Backups', 'red'), ('Email tool', 'card')]
    for i, (a, tn) in enumerate(P):
        x = 10 + (i % 3) * 116; y = 28 + (i // 3) * 40
        o += box(x, y, 108, 32, tn, rx=6) + t(x + 54, y + 20, a, 7.6, 'ink', bold=True)
    o += t(180, 120, 'Know where personal data lives — before the request arrives', 7.4, 'ink', bold=True)
    return o
scene_svg = scene('Six places holding one customer’s data: orders database, S3 receipts, app logs, BigQuery, backups, email tool.', story_scene(), 'You cannot delete what you <tspan font-weight="700" class="s-acc">cannot find</tspan>.', h=130)
dialogue = '''R> Sir, we deleted her row from the orders table. Done?
A> Her address is also in receipts, logs, BigQuery and backups. And our email tool has her phone number.
K> But AWS is ISO 27001 certified — aren’t we compliant?
A> AWS’s certificate covers AWS’s half. Our compliance covers what we collect, why, where we keep it, for how long, and whether we can prove it.
R> So which rules apply to us?
A> DPDP for Indian customers, RBI if we touch payments data, CERT-In for incidents and logs, and GDPR for our Dubai and London customers. Let’s map them.'''

def lifefig():
    o = t(320, 16, 'Privacy across the data lifecycle', 11, 'ink', bold=True)
    S = [('Notice + consent', 'clear purpose', 'violet'), ('Collect minimum', 'only what is needed', 'blue'), ('Store + protect', 'encrypt, restrict', 'blue'), ('Use for purpose', 'no surprise uses', 'green'), ('Share carefully', 'processors, contracts', 'amber'), ('Erase on time', 'retention, requests', 'red')]
    for i, (a, b, tn) in enumerate(S):
        x = 10 + i * 104
        o += box(x, 40, 96, 64, tn, rx=8) + t(x + 48, 66, a, 7.6, 'ink', bold=True) + t(x + 48, 84, b, 6.6, 'ink2')
        if i < 5: o += arrow(x + 96, 72, x + 104, 72)
    o += t(320, 128, 'People (data principals) can ask to access, correct or erase their data and withdraw consent at any stage.', 7.4, 'ink2')
    return o
LIFE = bigfig('Six stages: notice and consent, collect minimum, store and protect, use for purpose, share carefully, erase on time; individuals can exercise rights at any stage.', lifefig(), h=140)

def rolesfig():
    o = t(320, 16, 'Who is who in privacy law', 11, 'ink', bold=True)
    R = [('Data principal / subject', 'the customer whose data it is', 'green'), ('Data fiduciary / controller', 'TiffinGo — decides why and how', 'blue'), ('Data processor', 'AWS, Azure, Google, email tool — process on instructions', 'amber'), ('Regulator', 'Data Protection Board of India, EU authorities', 'violet')]
    for i, (a, b, tn) in enumerate(R):
        y = 32 + i * 36
        o += box(40, y, 220, 28, tn, rx=6) + t(150, y + 18, a, 8, 'ink', bold=True) + t(450, y + 18, b, 7.6, 'ink')
    o += t(320, 186, 'DPDP uses “principal” and “fiduciary”; GDPR uses “subject” and “controller”. Cloud providers are usually processors.', 7.4, 'ink2')
    return o
ROLES = bigfig('Roles: data principal or subject (the customer), data fiduciary or controller (TiffinGo), data processor (cloud providers and tools), regulator (Data Protection Board of India, EU authorities).', rolesfig(), h=196)

picture = ('  <p>Privacy follows the data through its life:</p>\n' + LIFE +
           '\n  <p>And the law gives each party a role:</p>\n' + ROLES +
           '\n  <h3>Privacy, security, compliance — the difference</h3>\n' + table(['', 'Security', 'Privacy', 'Compliance'], [['Question', 'is the data protected?', 'is it used fairly and lawfully?', 'can we prove we follow the rules?'], ['Example control', 'encryption, MFA', 'consent, purpose limits, erasure', 'audits, evidence, policies'], ['Fails when', 'data is stolen', 'data is misused even if safe', 'no evidence, even if safe']], minw=600))

RN = {'req': (4, 54, 50, 50, 'user', 'Request', 'erase me'), 'id': (66, 4, 62, 46, 'shield', 'Verify', 'identity'), 'map': (66, 104, 62, 46, 'chart', 'Data map', 'where is it?'),
      'live': (142, 54, 60, 50, 'db', 'Live systems', 'DB, S3, BQ'), 'logs': (216, 4, 62, 46, 'disk', 'Logs/backups', 'expire'), 'proc': (216, 104, 62, 46, 'cloud', 'Processors', 'email tool'), 'proof': (292, 54, 64, 50, 'meter', 'Proof', 'record + reply')}
RS = [dict(on=['req', 'id'], hot='id', move=(54, 79, 72, 30, 'verify'), head='Step 1 · Receive and verify the request', text='The customer asks for erasure through the app. TiffinGo verifies it is really her', text2='(OTP to the registered phone) and logs the request with a due date.', svc='Rights: access, correction, erasure, grievance redressal (DPDP)'),
      dict(on=['req', 'id', 'map'], hot='map', move=(97, 50, 97, 104, 'lookup'), head='Step 2 · Find every copy using the data map', text='The data inventory lists where customer_id appears: orders DB, receipts bucket,', text2='app logs, BigQuery, backups and the email marketing tool.', svc='Discovery: Macie · Microsoft Purview · Sensitive Data Protection'),
      dict(on=['map', 'live'], hot='live', move=(128, 127, 150, 90, 'delete'), head='Step 3 · Erase from live systems', text='Delete or anonymise her rows and objects; analytics keep only aggregated,', text2='non-identifiable numbers (orders per area).', svc='Keep what law requires (e.g. tax invoices) — and record why'),
      dict(on=['live', 'logs'], hot='logs', move=(202, 66, 226, 30, 'expire'), head='Step 4 · Logs and backups age out', text='Backups are not edited one by one; they expire on schedule (e.g. 35 days) and', text2='restores re-apply deletions. Logs avoid storing raw personal data.', svc='Retention policies do the work automatically (practical step 2)'),
      dict(on=['live', 'proc'], hot='proc', move=(172, 104, 226, 126, 'notify'), head='Step 5 · Tell processors to delete too', text='The email tool and any other processor receive a deletion instruction under their', text2='data-processing agreement, and confirm.', svc='Processor contracts (DPAs) make this enforceable'),
      dict(on=list(RN), hot='proof', move=(278, 127, 298, 90, 'done'), head='Step 6 · Record and confirm', text='The request record shows what was deleted where, what was retained and why, and', text2='the reply sent to the customer — evidence for an audit or the Board.', svc='Compliance = doing it AND proving it')]
ERASE = flow_anim('One erasure request across a cloud system', 'What it really takes to “delete my data”.', 'Erasure request', 'Animation: receive and verify request; find all copies with a data map; erase from live systems; logs and backups expire; processors delete; record and confirm.', RN, RS, hid='eraseflow')

def mapfig():
    o = t(320, 16, 'Seven frameworks you will meet', 11, 'ink', bold=True)
    items = [('1', 'DPDP Act 2023 + Rules', 'India · personal data', 'blue'), ('2', 'GDPR', 'EU · personal data', 'violet'), ('3', 'Indian sector rules', 'RBI · CERT-In · MeitY', 'amber'), ('4', 'ISO/IEC 27001 family', 'security management', 'green'),
             ('5', 'SOC 2', 'service-org controls report', 'green'), ('6', 'PCI DSS', 'payment card data', 'red'), ('7', 'HIPAA', 'US health data', 'card')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 7.8, 'ink', bold=True) + t(x + 78, y + 54, b, 6.6, 'ink2')
    o += t(320, 210, '1–3 and 6–7 are laws or binding rules; 4–5 are standards/attestations that prove good practice.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of seven frameworks: DPDP Act and Rules, GDPR, Indian sector rules, ISO 27001 family, SOC 2, PCI DSS, HIPAA.', mapfig(), h=222)

A1 = mk(['Notice + consent', 'Use for purpose', 'Rights + breach duty'], ['notice|clear purpose|consent', 'use|only for that|minimum data', 'duties|erase, correct|report breaches'], ['blue', 'green', 'red'],
        ['give a clear notice and get valid consent (or a legitimate use)', 'process only for that purpose and keep data accurate and secure', 'honour rights, erase when done, report breaches to the Board and users'],
        [('Notice', 'Clear notice and consent, or a legitimate use.', ''), ('Use', 'Purpose-limited, secured processing.', ''), ('Duties', 'Honour rights, erase on time, report breaches.', '')],
        'DPDP in action', 'India’s data protection law.', 'DPDP', 'Animation: notice and consent; purpose-limited use; rights and breach duties.', 'c1anim')
T1 = vt(1, 'India’s Digital Personal Data Protection Act, 2023 and Rules, 2025', 'blue',
    'The <b>DPDP Act, 2023</b> governs processing of digital personal data in India (and of Indians’ data by offerings abroad); <b>data fiduciaries</b> must give notice, obtain consent or rely on a legitimate use, limit processing to the purpose, take reasonable security safeguards, report breaches, erase data when no longer needed and honour <b>data principals’</b> rights. The <b>DPDP Rules, 2025</b>, notified on 13 November 2025, phase most obligations in over about 18 months; breaches must be reported to the Data Protection Board, with a detailed report within 72 hours.',
    'A tailor who takes your measurements only for the shirt you ordered, keeps them locked, and throws them away when you ask — and tells you if they get lost.',
    'TiffinGo rewrote its sign-up notice in English and Hindi, separated marketing consent from order processing, and set a 30-day erasure SLA (animation above).',
    'Applies to every cloud: you choose Indian Regions where needed, encrypt, log access and build erasure workflows; providers act as processors under contract.', '', A1,
    'you process digital personal data of people in India — which almost every Indian app does.',
    'you treat it as a privacy-policy text change only — it needs technical controls.',
    'India’s law on how companies must collect, use, protect and delete people’s personal data.',
    [('Notice', 'Itemised, clear language.'), ('Consent', 'Free, specific, withdrawable (consent managers possible).'), ('Safeguards', 'Encryption, access control, logs.'), ('Breach', 'Inform Board and affected people.'), ('Erasure', 'When purpose is served or consent withdrawn.')],
    [('data principal', 'the person the data is about'), ('data fiduciary', 'the organisation deciding why/how data is processed'), ('Significant Data Fiduciary', 'a fiduciary with extra duties (audits, DPO, impact assessments)')],
    table(['', 'DPDP (India)', 'GDPR (EU)'], [['Lawful bases', 'consent + listed legitimate uses', 'six lawful bases'], ['Scope', 'digital personal data', 'all personal data'], ['Max penalty', 'up to ₹250 crore per instance', 'up to €20 m or 4% of turnover']], minw=460),
    ['Consumer apps', 'Fintech, health, ed-tech', 'Any Indian business with customer data'],
    'MeitY notified the DPDP Rules on 13 November 2025 with a staggered rollout — Data Protection Board provisions first, most fiduciary obligations after about 18 months.',
    'The Act allows the government to restrict transfers to specific countries (a “negative list”) rather than requiring all data to stay in India — but sector rules (like RBI’s) can still demand local storage.')

A2 = mk(['Lawful basis', 'Rights', 'Accountability'], ['basis|consent, contract|legitimate interest', 'rights|access, erase|portability', 'prove|records, DPIA|72-hour breach'], ['violet', 'green', 'amber'],
        ['every processing needs one of six lawful bases', 'people have strong rights over their data', 'organisations must document and prove compliance'],
        [('Basis', 'Each processing activity needs a lawful basis.', ''), ('Rights', 'Access, rectification, erasure, portability, objection.', ''), ('Accountability', 'Records, impact assessments, 72-hour breach notice.', '')],
        'GDPR in action', 'Europe’s privacy rulebook.', 'GDPR', 'Animation: lawful basis; rights; accountability.', 'c2anim')
T2 = vt(2, 'GDPR (EU General Data Protection Regulation)', 'violet',
    'The <b>GDPR</b> regulates processing of personal data of people in the EU/EEA by organisations anywhere that offer them goods or services or monitor them; it requires a lawful basis, data minimisation, security, records of processing, impact assessments for high-risk processing, 72-hour breach notification and safeguards for transfers outside the EU.',
    'A strict building code in another country: if you build there — or sell houses there — you follow it, wherever your company is.',
    'TiffinGo’s London pilot needs a lawful basis for each use, a data processing agreement with AWS, and transfer safeguards for any EU data processed in India.',
    'Providers offer EU Regions, data processing addenda with standard contractual clauses, and tools for subject-access and erasure workflows.', '', A2,
    'you serve or monitor people in the EU/EEA.',
    'you assume “we are an Indian company” exempts you — GDPR is extraterritorial.',
    'Europe’s strict data protection law that also applies to foreign companies serving people in Europe.',
    [('Map', 'Records of processing.'), ('Basis', 'Pick and document.'), ('DPIA', 'For high-risk processing.'), ('Transfers', 'SCCs / adequacy.'), ('Breach', '72-hour notification.')],
    [('DPIA', 'data protection impact assessment'), ('SCCs', 'standard contractual clauses for transfers'), ('adequacy', 'EU decision that a country protects data well enough')],
    table(['', 'GDPR', 'DPDP'], [['Non-digital data', 'covered', 'not covered (digital only)'], ['DPO', 'often required', 'for Significant Data Fiduciaries'], ['Breach timeline', '72 h to authority', 'detailed report to Board within 72 h']], minw=440),
    ['EU customers', 'Global SaaS', 'Analytics and ad-tech'],
    'Regulators have issued very large GDPR fines, including against major cloud and social-media companies for unlawful transfers and transparency failures.',
    'Data residency (EU Region) does not by itself solve transfers — remote access from India to EU data is also a transfer.')

A3 = mk(['Payments data (RBI)', 'Incidents + logs (CERT-In)', 'Government cloud (MeitY)'], ['RBI|payment data|stored in India', 'CERT-In|report in 6 h|logs 180 days', 'MeitY|empanelled CSPs|gov workloads'], ['amber', 'red', 'blue'],
        ['payment system data must be stored only in India', 'cyber incidents reported within 6 hours; logs kept 180 days in India', 'government workloads use MeitY-empanelled cloud providers'],
        [('RBI', 'Payment system data stored only in India.', ''), ('CERT-In', '6-hour incident reporting; 180-day logs in India.', ''), ('MeitY', 'Empanelled providers for government cloud.', '')],
        'Indian sector rules in action', 'Rules beyond DPDP.', 'Sector rules', 'Animation: RBI payment data; CERT-In incidents and logs; MeitY empanelment.', 'c3anim')
T3 = vt(3, 'Indian sector rules (RBI, CERT-In, MeitY)', 'amber',
    '<b>Indian sector and cyber rules</b> add specific cloud obligations: RBI’s 2018 direction requires payment system data to be stored only in India, and RBI outsourcing/IT guidelines govern regulated entities’ cloud use; <b>CERT-In’s April 2022 directions</b> require reporting specified cyber incidents within 6 hours and maintaining ICT system logs for 180 days within India; MeitY empanels cloud providers for government workloads.',
    'Local municipal rules on top of national building law: the national law sets the basics, the city adds its own fire and height rules.',
    'Because TiffinGo stores UPI payment references, they stay in Mumbai/Hyderabad Regions; CloudTrail and app logs are kept 180 days; the incident runbook (9.2) now includes a 6-hour CERT-In report step.',
    'Indian Regions: AWS Mumbai/Hyderabad, Azure Central/South/West India, Google Mumbai/Delhi; log retention settings; MeitY-empanelled offerings of major and Indian providers.', 'Community/government cloud was covered in 3.1.', A3,
    'you are a regulated entity, handle payments, or run ICT systems in India (CERT-In applies broadly).',
    'logs are kept only 30 days by default — that breaks the CERT-In 180-day rule.',
    'Extra Indian rules: payment data in India (RBI), report hacks in 6 hours and keep logs 180 days (CERT-In).',
    [('Classify', 'Payment, health, personal data.'), ('Locate', 'Indian Regions where required.'), ('Logs', '180-day retention in India.'), ('Report', '6-hour CERT-In runbook step.'), ('Vendors', 'Contracts allow regulator audits.')],
    [('regulated entity', 'a bank, NBFC, payment operator etc. supervised by RBI'), ('ICT logs', 'logs from information and communication systems'), ('empanelment', 'official approval to supply to government')],
    table(['', 'RBI payment data', 'CERT-In directions'], [['Applies to', 'payment system operators and chain', 'service providers, intermediaries, data centres, body corporates'], ['Key rule', 'store only in India', 'report incidents in 6 h, logs 180 days'], ['Cloud impact', 'Region choice', 'logging configuration and runbooks']], minw=460),
    ['Fintech and payments', 'Banks and NBFCs', 'Any Indian IT service'],
    'The CERT-In directions issued in April 2022 introduced the 6-hour reporting window and 180-day log retention that many Indian cloud teams now build into their logging design.',
    'Keep 180 days of logs cheaply: hot storage 30 days, then archive tiers (Lesson 6.2) — the rule is about retention, not about keeping everything searchable.')

A4 = mk(['Risk assessment', 'Controls (Annex A)', 'Audit + improve'], ['ISMS|scope, risks|policy', 'controls|93 in 2022 version|people, process, tech', 'certify|external audit|yearly surveillance'], ['green', 'blue', 'green'],
        ['define an information security management system and assess risks', 'apply controls from Annex A that address those risks', 'an accredited auditor certifies it; it is re-checked every year'],
        [('ISMS', 'Scope, risk assessment and policies.', ''), ('Controls', 'Annex A controls chosen by risk.', ''), ('Certify', 'External audit, yearly surveillance, 3-year recertification.', '')],
        'ISO 27001 in action', 'A management system for security.', 'ISO 27001', 'Animation: risk assessment; controls; audit and improve.', 'c4anim')
T4 = vt(4, 'ISO/IEC 27001 (and 27017, 27018, 27701)', 'green',
    '<b>ISO/IEC 27001</b> is the international standard for an <b>information security management system (ISMS)</b>: an organisation defines scope, assesses risks, applies controls (Annex A; 93 controls in the 2022 edition) and is certified by an accredited auditor; related standards add cloud security (27017), protection of personal data in public clouds (27018) and privacy management (27701).',
    'A food-safety certification for a kitchen: an inspector checks that processes, hygiene and records are in place — and comes back every year.',
    'A hospital customer required ISO 27001 from TiffinGo; it scoped the ISMS to the order platform, reused AWS’s certificate for the infrastructure layer, and was certified in eight months.',
    'AWS, Azure and Google Cloud hold ISO 27001, 27017, 27018 and 27701 certificates (download in Lesson 9.1); customers certify their own ISMS on top.', '', A4,
    'customers or tenders ask for proof of a mature security programme.',
    'you expect the provider’s certificate to cover your scope — it covers theirs.',
    'An international certificate showing a company manages information security properly.',
    [('Scope', 'Systems, locations, teams.'), ('Risks', 'Assess and treat.'), ('SoA', 'Statement of Applicability.'), ('Operate', 'Policies, training, monitoring.'), ('Audit', 'Internal + certification audits.')],
    [('ISMS', 'information security management system'), ('Statement of Applicability', 'list of controls chosen and why'), ('surveillance audit', 'yearly check between certifications')],
    table(['', 'ISO 27001', 'SOC 2'], [['Output', 'certificate', 'auditor’s report'], ['Origin', 'international (ISO)', 'US (AICPA)'], ['Focus', 'management system', 'controls operating over a period']], minw=420),
    ['Enterprise vendors', 'Government tenders', 'Outsourcing firms'],
    'Many Indian IT services firms hold ISO 27001 because global clients require it in contracts.',
    'Map provider controls into your Statement of Applicability as “inherited” — that saves months of work (9.1’s inherited controls).')

A5 = mk(['Trust criteria', 'Period of testing', 'Report to customers'], ['criteria|security +|availability, privacy…', 'Type 2|3–12 months|controls tested', 'report|under NDA|for customers'], ['green', 'amber', 'blue'],
        ['controls are designed against AICPA Trust Services Criteria', 'a Type 2 audit tests they operated over months', 'customers read the report (under NDA) to trust the vendor'],
        [('Criteria', 'Security (required) plus optional availability, confidentiality, processing integrity, privacy.', ''), ('Test', 'Type 1 = design at a point; Type 2 = operation over a period.', ''), ('Share', 'Customers receive the report under NDA.', '')],
        'SOC 2 in action', 'Proof that controls actually worked.', 'SOC 2', 'Animation: trust criteria; period of testing; report to customers.', 'c5anim')
T5 = vt(5, 'SOC 2', 'green',
    'A <b>SOC 2</b> report is an independent auditor’s attestation (under AICPA standards) on a service organisation’s controls relevant to the Trust Services Criteria — security, availability, processing integrity, confidentiality and privacy; <b>Type 1</b> assesses design at a point in time and <b>Type 2</b> tests operating effectiveness over a period (typically 3–12 months).',
    'A restaurant’s hygiene inspector visiting unannounced for six months and writing a report, instead of checking once on opening day.',
    'Enterprise customers asked TiffinGo’s B2B catering platform for a SOC 2 Type 2; the auditors sampled access reviews, change approvals and backup tests over six months.',
    'Providers publish SOC 1/2/3 reports (AWS Artifact, Service Trust Portal, Compliance Reports Manager); compliance-automation tools collect evidence from cloud APIs.', '', A5,
    'you sell B2B SaaS, especially to US or global enterprises.',
    'controls exist only on paper — Type 2 tests that they ran every month.',
    'An auditor’s report proving a company’s security controls really worked over several months.',
    [('Scope', 'System and criteria.'), ('Readiness', 'Gap assessment.'), ('Operate', 'Collect evidence continuously.'), ('Audit', 'Type 1, then Type 2.'), ('Share', 'With customers under NDA.')],
    [('attestation', 'auditor’s formal opinion'), ('Trust Services Criteria', 'the AICPA control categories'), ('SOC 3', 'a public, summary version')],
    table(['', 'Type 1', 'Type 2'], [['Tests', 'design', 'operation over time'], ['Period', 'a single date', '3–12 months'], ['Customer value', 'lower', 'higher']], minw=420),
    ['B2B SaaS', 'Data processors', 'Managed service providers'],
    'Compliance-automation platforms connect to AWS, Azure and Google APIs to collect SOC 2 evidence (MFA status, encryption, logging) continuously instead of by screenshots.',
    'Logs, access reviews and change records from 8.1–8.3 are exactly the evidence SOC 2 auditors sample — good operations make audits easy.')

A6 = mk(['Card data enters', 'Small, isolated scope', 'Tested yearly'], ['card data|PAN, CVV|payment flow', 'scope|segment CDE|or use tokens', 'assess|QSA / SAQ|quarterly scans'], ['red', 'amber', 'green'],
        ['card numbers enter your systems', 'keep them in a small, isolated environment — or never touch them', 'assessments and scans every year/quarter'],
        [('Enter', 'Cardholder data enters the payment flow.', ''), ('Reduce scope', 'Isolate the cardholder data environment or use a tokenising gateway.', ''), ('Assess', 'Annual assessment, quarterly scans.', '')],
        'PCI DSS in action', 'Shrink the card-data zone.', 'PCI DSS', 'Animation: card data enters; scope reduced; tested yearly.', 'c6anim')
T6 = vt(6, 'PCI DSS', 'red',
    'The <b>Payment Card Industry Data Security Standard (PCI DSS)</b>, currently version 4.0.1, sets security requirements for any organisation that stores, processes or transmits payment card data — network segmentation, encryption, access control, logging, vulnerability management and regular testing — assessed annually by a Qualified Security Assessor or self-assessment questionnaire.',
    'Handling cash in a shop: keep it in one locked till, few people with keys, counted and audited regularly — or use a card machine so you never touch cash.',
    'TiffinGo never sees card numbers: the payment gateway’s hosted page collects them and returns a token. That kept TiffinGo’s PCI scope to a short self-assessment.',
    'Providers are PCI DSS Level 1 service providers for many services; payment gateways (Razorpay, Stripe, PayU) offer hosted checkout and tokenisation.', '', A6,
    'you accept card payments in any form.',
    'card data flows through your logs or analytics — scope explodes.',
    'Security rules for any business that handles credit or debit card details.',
    [('Avoid', 'Hosted checkout + tokens.'), ('Segment', 'Isolated CDE if you must store.'), ('Encrypt', 'In transit and at rest.'), ('Log', 'All access to card data.'), ('Test', 'Scans and pentests.')],
    [('PAN', 'primary account number — the card number'), ('CDE', 'cardholder data environment'), ('tokenisation', 'replacing card data with a meaningless token')],
    table(['', 'Store card data', 'Hosted checkout + tokens'], [['PCI scope', 'large (full assessment)', 'small (simple SAQ)'], ['Risk', 'high', 'low'], ['Effort', 'very high', 'low']], minw=440),
    ['E-commerce', 'Food delivery', 'Subscriptions'],
    'RBI’s card-on-file tokenisation rules (effective October 2022) stopped Indian merchants from storing card numbers — a regulation and PCI scope reduction in one.',
    'The cheapest PCI control is architectural: never let a card number touch your servers.')

A7 = mk(['Health data (PHI)', 'BAA signed', 'Safeguards'], ['PHI|patient records|US', 'BAA|with cloud provider|eligible services', 'safeguards|admin, physical|technical'], ['card', 'blue', 'green'],
        ['protected health information of US patients', 'a business associate agreement with the provider, eligible services only', 'administrative, physical and technical safeguards'],
        [('PHI', 'US patients’ health information.', ''), ('BAA', 'Business associate agreement; use eligible services only.', ''), ('Safeguards', 'Administrative, physical and technical controls.', '')],
        'HIPAA in action', 'US health data rules.', 'HIPAA', 'Animation: PHI; BAA signed; safeguards.', 'c7anim')
T7 = vt(7, 'HIPAA (US health data)', 'card',
    '<b>HIPAA</b> is a US law whose Privacy and Security Rules protect <b>protected health information (PHI)</b>; covered entities and their business associates — including cloud providers storing PHI — must sign <b>business associate agreements (BAAs)</b> and apply administrative, physical and technical safeguards such as access control, audit logs and encryption.',
    'A hospital’s medical-records room: only authorised staff, every access logged, and every outside contractor signs a confidentiality agreement.',
    'A US clinic wants TiffinGo’s diet planner for its patients; TiffinGo must sign a BAA with AWS and use only HIPAA-eligible services for the PHI.',
    'AWS, Azure and Google Cloud sign BAAs and publish lists of HIPAA-eligible services; India’s equivalent concerns sit under DPDP and health-sector guidelines (e.g. ABDM).', '', A7,
    'you handle US patients’ health data.',
    'you use a service not on the provider’s eligible list for PHI.',
    'A US law that protects patients’ health information, including when it is stored in the cloud.',
    [('Identify PHI', 'What and where.'), ('BAA', 'With provider and vendors.'), ('Eligible services', 'Only those.'), ('Safeguards', 'Access, audit, encryption.'), ('Breach', 'Notification rules.')],
    [('PHI', 'protected health information'), ('BAA', 'business associate agreement'), ('covered entity', 'hospital, insurer, clearinghouse')],
    table(['', 'HIPAA', 'DPDP'], [['Data', 'US health information', 'all digital personal data in India'], ['Who', 'covered entities + associates', 'all data fiduciaries'], ['Contract tool', 'BAA', 'processor contracts']], minw=440),
    ['Hospitals and clinics', 'Health-tech', 'Insurers'],
    'Cloud providers list exactly which services are HIPAA-eligible; using an ineligible service for PHI is a classic compliance gap even if it is technically secure.',
    'Compliance frameworks overlap heavily: encryption, access control, logging and incident response satisfy large parts of HIPAA, PCI, ISO and DPDP at once — build controls once, map them many times.')

SUMMARY = table(['#', 'Framework', 'Type', 'Applies when', 'Key cloud actions'], [
    ['1', 'DPDP Act + Rules', 'law (India)', 'personal data of people in India', 'notice/consent, erasure, safeguards, breach reports'], ['2', 'GDPR', 'law (EU)', 'serving people in the EU', 'lawful basis, DPIA, transfers, 72 h'],
    ['3', 'RBI / CERT-In / MeitY', 'Indian rules', 'payments, Indian ICT, government', 'India storage, 6 h reports, 180-day logs'], ['4', 'ISO 27001 family', 'certification', 'customer/tender demands', 'ISMS, controls, audits'],
    ['5', 'SOC 2', 'attestation', 'B2B SaaS', 'evidence over months'], ['6', 'PCI DSS', 'industry standard', 'card data', 'tokenise, segment, scan'], ['7', 'HIPAA', 'law (US)', 'US health data', 'BAA, eligible services']], minw=660)
CHECK = ('  <h3>Check yourself: which framework?</h3>\n' +
    qx('A. Report a cyber incident in India within 6 hours.', ['CERT-In directions', 'SOC 2', 'HIPAA', 'PCI DSS'], 0, 'CERT-In 2022.') +
    qx('B. A customer in India asks you to erase her data.', ['DPDP Act', 'PCI DSS', 'HIPAA', 'SOC 2'], 0, 'Data principal rights.') +
    qx('C. Proof that controls operated for 6 months, for a US enterprise customer.', ['SOC 2 Type 2', 'ISO 27018', 'GDPR', 'RBI'], 0, 'Type 2 report.') +
    qx('D. Card numbers stored for subscriptions.', ['PCI DSS', 'HIPAA', 'DPDP only', 'ISO 9001'], 0, 'Card data.'))

TYPES = ('  <p>Seven frameworks, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['Does AWS’s ISO 27001 certificate make TiffinGo ISO certified?', 'How long must ICT logs be kept under CERT-In directions?', 'What is the cheapest PCI DSS control?'], 'types 4, 3 and 6') + MAP
         + jump(['DPDP', 'GDPR', 'India sector', 'ISO 27001', 'SOC 2', 'PCI DSS', 'HIPAA']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('Data inventory / map', 'Where personal data lives and flows.', 'Needed for rights, breaches and audits.', 'Macie, Purview, Sensitive Data Protection.'),
    ('Classification', 'Labels: public, internal, personal, sensitive.', 'Drives controls and retention.', 'Tags/labels on buckets and tables.'),
    ('Retention policy', 'How long each data type is kept.', 'Minimisation; erasure by default.', 'Lifecycle rules, log retention.'),
    ('Data residency', 'Where data is stored and processed.', 'RBI, government, customer contracts.', 'Region choice + guard-rails (3.1).'),
    ('Processor contracts', 'DPAs, BAAs with vendors.', 'Legal basis to use cloud and SaaS.', 'Provider data processing terms.'),
    ('Evidence', 'Logs, reports, records of requests.', 'Compliance must be provable.', 'Audit logs, request register, reports.')])

DEEP = ('  <h3>Privacy-enhancing techniques</h3>\n' + table(['Technique', 'What it does', 'Cloud example'], [['Pseudonymisation', 'replace identifiers with tokens; reversible with a key', 'tokenise customer IDs in analytics'], ['Anonymisation / aggregation', 'remove ability to identify; irreversible', 'orders per area, not per person'], ['Masking', 'hide parts of values in non-prod', 'dev copies with fake phones'], ['Encryption with customer keys', 'control who can decrypt', 'KMS/Key Vault/Cloud KMS CMKs (9.4)'], ['De-identification APIs', 'detect and transform PII automatically', 'Sensitive Data Protection, Comprehend, Language PII']], minw=560) +
    '\n  <h3>Compliance is continuous</h3>\n  <p>Cloud resources change daily, so compliance checks must be automated: policy-as-code (Azure Policy initiatives, AWS Config conformance packs, organisation policies), posture dashboards mapped to standards, and evidence collected by API. A yearly audit then becomes a review of evidence you already have.</p>\n'
    '  <h3>Provider tools mapped to standards</h3>\n  <ul><li><b>AWS:</b> Audit Manager frameworks, Config conformance packs, Security Hub standards (CIS, PCI DSS, NIST).</li><li><b>Azure:</b> Defender for Cloud regulatory compliance dashboard, Azure Policy built-in initiatives (ISO 27001, PCI DSS, NIST, RBI ITF for banks).</li><li><b>Google Cloud:</b> Assured Workloads, Security Command Center compliance reports, Compliance Manager.</li></ul>')

clouds = vendor_tabs('<p><b>AWS:</b> Indian Regions (Mumbai, Hyderabad), AWS Artifact (reports, agreements incl. BAA), Macie (PII discovery), Comprehend PII detection, Audit Manager, Config conformance packs, KMS, CloudTrail Lake for long-term logs.</p>',
    '<p><b>Azure:</b> India Regions, Service Trust Portal, Microsoft Purview (data map, classification, DLP), Azure AI Language PII detection, Defender for Cloud regulatory compliance, Azure Policy initiatives, Key Vault.</p>',
    '<p><b>Google Cloud:</b> Mumbai and Delhi Regions, Compliance Reports Manager, Sensitive Data Protection (DLP: discovery, inspection, de-identification), Assured Workloads, Access Transparency, Cloud KMS/EKM.</p>') + \
    cloud3([['Find personal data', 'Macie, Comprehend PII', 'Purview, Language PII', 'Sensitive Data Protection'], ['Reports and agreements', 'Artifact', 'Service Trust Portal', 'Compliance Reports Manager'], ['Compliance dashboards', 'Audit Manager, Security Hub', 'Defender regulatory compliance', 'SCC compliance, Assured Workloads'], ['Retention', 'S3 lifecycle, CloudWatch retention', 'lifecycle management, Log Analytics retention', 'lifecycle rules, log bucket retention']])

SAMPLE = 'Order 1043 for Priya Sharma, phone 9876543210, email priya.sharma@example.com, deliver to 12 MG Road, Pune.'

MOCKQ.extend([
 (mock('aws', ['Amazon Comprehend', 'Real-time analysis'], ['Real-time analysis', 'Analysis jobs', 'Custom classification'], 'Real-time analysis', [('Analysis type', '▾ Built-in · PII'), ('Input text', 'Order 1043 for Priya Sharma, phone 98765…')], 'Analyze'),
  mock('az', ['Language Studio', 'Extract PII'], ['Extract information', 'Classify text', 'Summarize'], 'Extract information', [('Resource', 'tiffingo-language (F0 free)'), ('Text', 'Order 1043 for Priya Sharma, phone 98765…')], 'Run'),
  mock('gcp', ['Sensitive Data Protection', 'Inspection'], ['Discovery', 'Inspection', 'De-identification', 'Configuration'], 'Inspection', [('infoTypes', 'PERSON_NAME · PHONE_NUMBER · EMAIL_ADDRESS'), ('Likelihood', '▾ POSSIBLE')], 'Inspect')),
 (mock('aws', ['S3', 'tiffingo-raw', 'Lifecycle rule'], ['Objects', 'Properties', 'Management'], 'Management', [('Prefix', 'raw-orders/'), ('Expire current versions', 'after 30 days')], 'Create rule'),
  mock('az', ['Storage account', 'Lifecycle management', 'Add a rule'], ['Overview', 'Data management', 'Lifecycle management'], 'Lifecycle management', [('Filter', 'raw-orders/'), ('Delete blob', 'if last modified > 30 days')], 'Add'),
  mock('gcp', ['Cloud Storage', 'Bucket', 'Lifecycle'], ['Objects', 'Configuration', 'Lifecycle'], 'Lifecycle', [('Condition', 'Age 30 days · prefix raw-orders/'), ('Action', 'Delete object')], 'Create')),
 (mock('aws', ['CloudTrail', 'Trails', 'Create trail'], ['Dashboard', 'Event history', 'Trails'], 'Trails', [('Trail name', 'india-logs'), ('S3 bucket', 'new · lifecycle 180 days'), ('Management events', '[x] Read + Write')], 'Create trail'),
  mock('az', ['Monitor', 'Activity log', 'Diagnostic settings'], ['Activity log', 'Diagnostic settings'], 'Diagnostic settings', [('Destination', '[x] Archive to a storage account (Central India)'), ('Retention', 'lifecycle: delete after 180 days')], 'Save'),
  mock('gcp', ['Logging', 'Logs Storage', '_Default'], ['Logs Explorer', 'Logs Storage', 'Log Router'], 'Logs Storage', [('Bucket', '_Default · global'), ('Retention', '180 days (was 30)')], 'Update bucket')),
])

STEP1 = ('1 · Detect personal data in text (data discovery basics)', tri(
    (['[[Amazon Comprehend]] → [[Real-time analysis]] → analysis type [[Personally identifiable information (PII)]] → paste the sample sentence → [[Analyze]].', 'For whole buckets, Amazon Macie scans S3 for PII (30-day trial).'],
     f"aws comprehend detect-pii-entities --language-code en --region ap-south-1 \\\n  --text \"{SAMPLE}\" --query 'Entities[].[Type,Score]' --output table",
     'rows such as <code>NAME</code>, <code>PHONE</code>, <code>EMAIL</code>, <code>ADDRESS</code> with confidence scores near 0.99. Cost: a fraction of a rupee for this text.'),
    (['Create a [[Language]] resource on the free [[F0]] tier → open [[Language Studio]] → [[Extract PII]] → paste the sentence → [[Run]].'],
     f"az group create -n rg-privacy -l centralindia\naz cognitiveservices account create -n tglang$RANDOM -g rg-privacy -l centralindia --kind TextAnalytics --sku F0 --yes\nN=$(az cognitiveservices account list -g rg-privacy --query [0].name -o tsv)\nEP=$(az cognitiveservices account show -n $N -g rg-privacy --query properties.endpoint -o tsv)\nKEY=$(az cognitiveservices account keys list -n $N -g rg-privacy --query key1 -o tsv)\ncurl -s \"${{EP}}language/:analyze-text?api-version=2023-04-01\" -H \"Ocp-Apim-Subscription-Key: $KEY\" -H 'Content-Type: application/json' \\\n  -d '{{\"kind\":\"PiiEntityRecognition\",\"analysisInput\":{{\"documents\":[{{\"id\":\"1\",\"language\":\"en\",\"text\":\"{SAMPLE}\"}}]}}}}' \\\n  | python3 -c \"import sys,json; d=json.load(sys.stdin)['results']['documents'][0]; print(d['redactedText']); [print(e['category'], e['text']) for e in d['entities']]\"",
     'the redacted sentence (<code>Order 1043 for ***********, phone **********…</code>) and categories like <code>Person</code>, <code>PhoneNumber</code>, <code>Email</code>, <code>Address</code>. F0 allows a few thousand records a month free (one free Language resource per subscription).'),
    (['[[Security]] → [[Sensitive Data Protection]] → [[Inspection]] — or use the API from Cloud Shell (right). Discovery can profile whole BigQuery datasets and buckets.'],
     f"gcloud services enable dlp.googleapis.com\nP=$(gcloud config get-value project)\ncurl -s -X POST \"https://dlp.googleapis.com/v2/projects/$P/locations/asia-south1/content:inspect\" \\\n  -H \"Authorization: Bearer $(gcloud auth print-access-token)\" -H 'Content-Type: application/json' \\\n  -d '{{\"item\":{{\"value\":\"{SAMPLE}\"}},\"inspectConfig\":{{\"infoTypes\":[{{\"name\":\"PERSON_NAME\"}},{{\"name\":\"PHONE_NUMBER\"}},{{\"name\":\"EMAIL_ADDRESS\"}},{{\"name\":\"STREET_ADDRESS\"}}],\"includeQuote\":true}}}}' \\\n  | python3 -c \"import sys,json; [print(f['infoType']['name'], f.get('quote'), f['likelihood']) for f in json.load(sys.stdin)['result'].get('findings',[])]\"",
     'lines like <code>PERSON_NAME Priya Sharma LIKELY</code>, <code>EMAIL_ADDRESS priya.sharma@example.com VERY_LIKELY</code>. Small inspections fall within the free monthly allowance.')),
    'This is how data maps are built at scale: scanners find personal data in buckets, tables and logs you forgot about.')

STEP2 = ('2 · Make data expire automatically (retention = minimisation)', tri(
    (['[[S3]] → create bucket <code>tiffingo-raw-…</code> → [[Management]] → [[Create lifecycle rule]]: prefix <code>raw-orders/</code>, [[Expire current versions]] after 30 days.'],
     "B=tiffingo-raw-$RANDOM; aws s3 mb s3://$B --region ap-south-1\naws s3api put-bucket-lifecycle-configuration --bucket $B --lifecycle-configuration \\\n  '{\"Rules\":[{\"ID\":\"raw-orders-30d\",\"Status\":\"Enabled\",\"Filter\":{\"Prefix\":\"raw-orders/\"},\"Expiration\":{\"Days\":30}}]}'\naws s3api get-bucket-lifecycle-configuration --bucket $B --query 'Rules[].[ID,Expiration.Days]' --output text",
     '<code>raw-orders-30d 30</code> — raw order exports now delete themselves after 30 days; nobody has to remember.'),
    (['[[Storage account]] (Central India) → [[Lifecycle management]] → [[Add a rule]]: filter <code>raw-orders/</code>, [[Delete the blob]] if last modified more than 30 days ago.'],
     "SA=tgraw$RANDOM; az storage account create -n $SA -g rg-privacy -l centralindia --sku Standard_LRS\ncat > policy.json <<'EOF'\n{\"rules\":[{\"enabled\":true,\"name\":\"raw-orders-30d\",\"type\":\"Lifecycle\",\"definition\":{\"filters\":{\"blobTypes\":[\"blockBlob\"],\"prefixMatch\":[\"raw-orders/\"]},\"actions\":{\"baseBlob\":{\"delete\":{\"daysAfterModificationGreaterThan\":30}}}}}]}\nEOF\naz storage account management-policy create --account-name $SA -g rg-privacy --policy @policy.json\naz storage account management-policy show --account-name $SA -g rg-privacy --query \"policy.rules[].name\" -o tsv",
     '<code>raw-orders-30d</code>.'),
    (['[[Cloud Storage]] → bucket in asia-south1 → [[Lifecycle]] → [[Add a rule]]: delete object, condition age 30 days, prefix <code>raw-orders/</code>.'],
     "B=tiffingo-raw-$RANDOM; gcloud storage buckets create gs://$B --location=asia-south1\ncat > lc.json <<'EOF'\n{\"rule\":[{\"action\":{\"type\":\"Delete\"},\"condition\":{\"age\":30,\"matchesPrefix\":[\"raw-orders/\"]}}]}\nEOF\ngcloud storage buckets update gs://$B --lifecycle-file=lc.json\ngcloud storage buckets describe gs://$B --format=\"value(lifecycle_config)\"",
     'the rule with <code>age: 30</code> and the prefix.')),
    'DPDP and GDPR both expect erasure when the purpose is served — lifecycle rules make that the default.')

STEP3 = ('3 · Keep audit logs for 180 days in India (CERT-In)', tri(
    (['[[CloudTrail]] → [[Trails]] → [[Create trail]] <code>india-logs</code> → new S3 bucket in Mumbai → management events read + write → [[Create]].', 'Add a lifecycle rule on that bucket: move to Glacier after 30 days, expire after 180 days or later per your policy.'],
     "LB=tiffingo-trail-$RANDOM; aws s3 mb s3://$LB --region ap-south-1\nACC=$(aws sts get-caller-identity --query Account --output text)\naws s3api put-bucket-policy --bucket $LB --policy \"{\\\"Version\\\":\\\"2012-10-17\\\",\\\"Statement\\\":[{\\\"Effect\\\":\\\"Allow\\\",\\\"Principal\\\":{\\\"Service\\\":\\\"cloudtrail.amazonaws.com\\\"},\\\"Action\\\":\\\"s3:GetBucketAcl\\\",\\\"Resource\\\":\\\"arn:aws:s3:::$LB\\\"},{\\\"Effect\\\":\\\"Allow\\\",\\\"Principal\\\":{\\\"Service\\\":\\\"cloudtrail.amazonaws.com\\\"},\\\"Action\\\":\\\"s3:PutObject\\\",\\\"Resource\\\":\\\"arn:aws:s3:::$LB/AWSLogs/$ACC/*\\\",\\\"Condition\\\":{\\\"StringEquals\\\":{\\\"s3:x-amz-acl\\\":\\\"bucket-owner-full-control\\\"}}}]}\"\naws s3api put-bucket-lifecycle-configuration --bucket $LB --lifecycle-configuration \\\n  '{\"Rules\":[{\"ID\":\"keep-180d\",\"Status\":\"Enabled\",\"Filter\":{},\"Transitions\":[{\"Days\":30,\"StorageClass\":\"GLACIER_IR\"}],\"Expiration\":{\"Days\":180}}]}'\naws cloudtrail create-trail --name india-logs --s3-bucket-name $LB --region ap-south-1\naws cloudtrail start-logging --name india-logs --region ap-south-1\naws cloudtrail get-trail-status --name india-logs --region ap-south-1 --query IsLogging",
     '<code>true</code>. The first trail of management events is free (you pay only S3 storage). Logs stay in Mumbai, move to a cheaper tier after 30 days and are kept 180 days.'),
    (['[[Monitor]] → [[Activity log]] → [[Export Activity Logs]] / [[Diagnostic settings]] → [[Archive to a storage account]] in Central India → add a lifecycle rule deleting after 180 days.', '(Activity log itself keeps 90 days — exporting is what makes 180 possible.)'],
     "LSA=tglogs$RANDOM; az storage account create -n $LSA -g rg-privacy -l centralindia --sku Standard_LRS\nSUB=$(az account show --query id -o tsv)\naz monitor diagnostic-settings subscription create -n india-logs --location centralindia \\\n  --storage-account $(az storage account show -n $LSA -g rg-privacy --query id -o tsv) \\\n  --logs '[{\"category\":\"Administrative\",\"enabled\":true},{\"category\":\"Security\",\"enabled\":true},{\"category\":\"Policy\",\"enabled\":true}]'\naz monitor diagnostic-settings subscription list --query \"value[].name\" -o tsv",
     '<code>india-logs</code>; activity logs now land in a Central India storage account (add a 180-day lifecycle rule as in step 2).'),
    (['[[Logging]] → [[Logs Storage]] → <code>_Default</code> bucket → [[Edit bucket]] → retention 180 days. (Admin Activity audit logs in <code>_Required</code> are kept 400 days automatically.)', 'For Indian data residency of logs, create a log bucket in <code>asia-south1</code> and route logs there with the Log Router.'],
     'gcloud logging buckets update _Default --location=global --retention-days=180\ngcloud logging buckets list --format="table(name.basename(),location,retentionDays)"',
     '<code>_Default global 180</code> and <code>_Required global 400</code>. Storage beyond the first 30 days is billed per GB-month — small for a lab project.')),
    'Retention cuts both ways: delete personal data you no longer need (step 2), keep security logs as long as rules require (step 3).')

prac = practical(OWN_INTRO + ' You find personal data in text, make data expire automatically, and keep audit logs for 180 days in India. Costs are a few rupees at most.', [SETUP_STEP, STEP1, STEP2, STEP3],
    cleanup='<b>AWS:</b> <code>aws cloudtrail delete-trail --name india-logs --region ap-south-1</code> (or keep it); <code>aws s3 rb s3://$B --force</code>; <code>aws s3 rb s3://$LB --force</code>. '
            '<b>Azure:</b> <code>az monitor diagnostic-settings subscription delete -n india-logs --yes</code>; <code>az group delete -n rg-privacy --yes --no-wait</code>. '
            '<b>Google Cloud:</b> <code>gcloud storage rm -r gs://$B</code>; set <code>_Default</code> back to 30 days if you prefer: <code>gcloud logging buckets update _Default --location=global --retention-days=30</code>.')

mist = mistakes([
    ['“Our provider is certified, so we are compliant.”', 'Confusing their scope with yours.', 'Use their reports for their half; certify your own controls.'],
    ['No data map.', 'Data copied everywhere over years.', 'Discovery scans + inventory per system.'],
    ['Keeping everything forever.', 'Storage is cheap.', 'Retention policy per data type; lifecycle rules.'],
    ['Personal data in logs and analytics.', 'Debug logging, raw exports.', 'Mask/pseudonymise before logging; aggregate analytics.'],
    ['Default 30–90 day logs.', 'Not configured.', 'Export and retain 180 days in India (CERT-In).'],
    ['Card numbers in your systems.', 'Custom checkout.', 'Hosted payment page + tokens.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Privacy and compliance issues in the cloud; regulations.'], ['AWS CLF-C02', 'AWS Artifact, compliance programs, Region choice for residency, Macie, Audit Manager, Config.'], ['AZ-900', 'Service Trust Portal, Microsoft Purview, Azure Policy, compliance offerings, privacy principles.'], ['Google Cloud Digital Leader', 'Data sovereignty, compliance reports, Sensitive Data Protection, Assured Workloads.']], minw=560) + \
    qx('1. Where do you get AWS compliance reports and agreements such as a BAA?', ['AWS Artifact', 'AWS Config', 'Amazon Inspector', 'AWS Shield'], 0, 'Artifact.') + \
    qx('2. Which AWS service discovers personal data in S3?', ['Amazon Macie', 'Amazon GuardDuty', 'AWS WAF', 'Amazon Detective'], 0, 'Macie.') + \
    qx('3. Which Microsoft service maps and classifies data across an organisation?', ['Microsoft Purview', 'Azure Arc', 'Azure Bastion', 'Azure Advisor'], 0, 'Purview.') + \
    qx('4. India’s CERT-In directions require incident reporting within…', ['6 hours', '72 hours', '30 days', '1 year'], 0, '6 hours.') + \
    qx('5. A SOC 2 Type 2 report tests…', ['design at one date', 'operating effectiveness over a period', 'only physical security', 'code quality'], 1, 'Over a period.') + \
    qx('6. Simplest way to cut PCI DSS scope?', ['store cards encrypted', 'use a hosted payment page with tokenisation', 'buy more firewalls', 'use a bigger VM'], 1, 'Never touch card data.')

proj = miniproject('Mini project: TiffinGo privacy and compliance pack',
    'Prepare TiffinGo for its first DPDP review and an enterprise customer’s audit.',
    ['<b>Data map:</b> list every system holding customer data (story) with Region and owner.',
     '<b>Classification + retention:</b> a table of data types with retention periods and lifecycle rules.',
     '<b>Rights workflow:</b> write the erasure steps from the animation as a runbook with a 30-day SLA.',
     '<b>Indian rules:</b> confirm payment data stays in India and logs are kept 180 days (step 3).',
     '<b>Frameworks:</b> decide which of the seven apply and why (one line each).',
     '<b>Evidence:</b> list which logs/reports prove each control.'],
    'A data map, retention table, erasure runbook and framework applicability matrix.', '9.1 + 9.2 + 9.3 + 6.2 (storage).')

assemble_v2(HERE, story_h2='“Delete all my data”', hook_html=hk,
    narration='A loyal TiffinGo customer moved cities and asked the company to delete everything it held about her. The team deleted one database row — then realised her details were also in files, logs, analytics, backups and a marketing tool.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Privacy and compliance in the cloud',
    formal='<b>Privacy</b> in the cloud is the lawful, fair and transparent processing of personal data — collecting only what is needed, using it for stated purposes, protecting it and honouring individuals’ rights — while <b>compliance</b> is the ability to demonstrate adherence to applicable laws, regulations and standards (such as India’s DPDP Act and Rules, RBI and CERT-In directions, GDPR, ISO/IEC 27001, SOC 2, PCI DSS and HIPAA) through controls and evidence, with responsibilities shared between the cloud customer (data fiduciary/controller) and provider (processor).',
    simple='Using people’s data only in fair, legal ways — and being able to prove you follow the rules that apply to you.',
    interview=['“Privacy is about lawful use of personal data — notice, consent, purpose, minimisation, rights; compliance is proving we meet laws like DPDP and standards like ISO 27001 with evidence.”', '“In the cloud I map data, keep it in the right Region, set retention with lifecycle rules, keep 180-day logs for CERT-In, and use provider reports for their half.”'],
    terms_rows=[('Personal data', 'Data about an identifiable person.'), ('Data fiduciary / controller', 'Decides why and how.'), ('Processor', 'Processes on instructions.'), ('Data residency', 'Where data is stored.'), ('Retention', 'How long data is kept.'), ('DPIA', 'Impact assessment.'), ('Attestation', 'Auditor’s opinion (SOC 2).'), ('Tokenisation', 'Replace sensitive values with tokens.')],
    exam='Know where to get compliance reports (Artifact, Service Trust Portal), data-discovery services (Macie, Purview, Sensitive Data Protection), residency through Region choice, and the difference between provider and customer compliance.',
    picture_h2='The data lifecycle and who is who', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven compliance frameworks, one by one', TYPES)],
    how_h2='One erasure request across a cloud system', how_intro='What “delete my data” really involves.', how_anim=ERASE,
    parts_h2='Six building blocks of cloud privacy', parts_html=parts, lv='',
    myth_rows=[('Provider certification = our compliance.', 'It covers the provider’s scope only.', 'Type 4.'), ('Keeping data forever is harmless.', 'It breaks minimisation and grows breach impact.', 'Step 2.'), ('Data in an Indian Region is DPDP-compliant.', 'Residency is one control among many.', 'Type 1.')],
    extra_secs=[('deep', 'Deep dive', 'Privacy techniques, continuous compliance, provider tools', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Distinguish privacy, security and compliance.', 'Explain DPDP, GDPR, RBI/CERT-In, ISO 27001, SOC 2, PCI DSS and HIPAA at a practical level.', 'Walk an erasure request through a cloud system.', 'Detect PII, set retention and keep 180-day logs on your own account.', 'Build a data map and evidence plan.'],
    next_html='<a href="../04-identity-access-and-encryption-basics/">9.4 Identity, access and encryption basics</a>.',
    pre='<b>Before you start:</b> 9.1 and 9.2.')
