import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
sys.path.insert(0, HERE)
from scenes import detect_scene, layers_picture, baseline_picture
def cap(frames, steps, title, intro, panel, aria, hid, delay=5500):
    return anim_one('Animated', title, intro, panel, aria, cap_frames(frames, steps), [s[0] + '.' for s in steps], delay=delay, hid=hid)
def row3(k, items, tones, cap_):
    o = ''
    for i, l in enumerate(items):
        on = i <= k
        bx = box(20 + i * 112, 34, 100, 74, tones[i] if on else 'card', rx=8)
        o += (f'<g class="sa-glow">{bx}</g>' if i == k else bx) + (sa_tick(112 + i * 112, 38, 7) if i < k else '')
        for j, w in enumerate(l.split('|')): o += t(70 + i * 112, 60 + j * 14, w, 7.2 if j == 0 else 6.6, 'ink', bold=(j == 0))
        if i < 2: o += arrow(120 + i * 112, 71, 132 + i * 112, 71)
    return o + t(180, 132, cap_, 7.2, 'ink', bold=True)
def mk(t3, items, tones, caps, steps, ttl, intro, panel, aria, hid):
    return cap([t(180, 12, t3[k], 9, 'ink', bold=True) + row3(k, items, tones, caps[k]) for k in range(3)], steps, ttl, intro, panel, aria, hid)
def vt(n, name, tone, d, an, sc, ex, gd, anim, use, avoid, plain, how, words, diff, where, rw, pro):
    return vtype(n, name, tone, d, an, sc, ex, gd, anim, use, avoid, plain=plain, how=how, words=words, diff=diff, where=where, realworld=rw, pro=pro)




hk = hook('Sunday, 11:40 pm. Someone used a leaked key to start 20 servers in CityBite’s account. By 11:52 the key was disabled, the servers stopped and the on-call engineer had an SMS. The bill impact: ₹300.',
    'That is what a <b>security baseline</b> buys: <b>CloudTrail</b> recording everything, <b>GuardDuty</b> spotting the attack, <b>Security Hub</b> collecting findings, and a small automation responding in minutes. This lesson brings Module 2 together — the shared responsibility model, defence in depth, the ten-setting baseline every account needs, the detection and response chain, and incident-response steps — and on <b>your own</b> account (or in the simulator) you will turn on a CloudTrail trail, GuardDuty with sample findings, posture checks, and an alert rule.',
    ['Prevent (identity, network, encryption) + detect (CloudTrail, GuardDuty) + respond (automation).', 'Ten baseline settings stop most real-world incidents.', 'Practise incident response before you need it.'])

def story_scene():
    o = t(180, 12, 'The same attack, two accounts', 9, 'ink', bold=True)
    o += box(8, 28, 160, 74, 'red', rx=8) + t(88, 48, 'No baseline', 8.4, 'ink', bold=True) + t(88, 64, 'noticed on Monday', 7, 'ink2') + t(88, 78, 'from the bill', 7, 'ink2') + t(88, 92, '₹1 lakh+', 7.4, 'ink', bold=True)
    o += box(192, 28, 160, 74, 'green', rx=8) + t(272, 48, 'Baseline on', 8.4, 'ink', bold=True) + t(272, 64, 'GuardDuty in minutes', 7, 'ink2') + t(272, 78, 'auto-response 12 min', 7, 'ink2') + t(272, 92, '₹300', 7.4, 'ink', bold=True)
    o += t(180, 122, 'You cannot respond to what you cannot see', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Left: without a baseline the attack is noticed on Monday from the bill, costing over a lakh. Right: with the baseline, GuardDuty detects it in minutes and automation responds in 12 minutes, costing about 300 rupees.', story_scene(), 'Prevent, <tspan font-weight="700" class="s-acc">detect</tspan>, respond.', h=132)
dialogue = '''K> Sir, we already have MFA and roles. Isn’t that enough?
A> That is prevention. Something always gets through — a leaked key, a bug, an open port. You also need detection and response.
R> Which services?
A> CloudTrail records every action. GuardDuty watches those records and network logs for attacks. Security Hub collects all findings in one place. EventBridge and Lambda can respond automatically.
K> And who is responsible — AWS or us?
A> AWS secures the cloud itself; we secure what we put in it. Let’s draw the layers.'''

picture = (newbie('Security is like protecting a shop: <b>locks</b> on doors (prevention), <b>CCTV</b> (logging), a <b>guard</b> watching the CCTV for suspicious people (detection), and an <b>alarm that calls the police</b> automatically (response). AWS gives you all four; you must switch them on.',
            [('Shared responsibility', 'AWS secures the building; you secure what you keep inside'), ('Finding', 'a security problem a tool has detected'), ('Baseline', 'the minimum settings every account should have'), ('Incident', 'a security event that needs action'), ('Automation', 'a response that runs without waiting for a person')]) +
    '  <p>Security on AWS is shared: AWS protects the cloud (data centres, hardware, hypervisor); <b>you</b> protect what you put in it — identities, data, configuration. You do it in layers:</p>\n' + layers_picture() +
    '\n  <h3>The baseline every account needs</h3>\n' + baseline_picture() +
    '\n  <h3>Shared responsibility in one table</h3>\n' + table(['', 'AWS', 'You'], [['Data centres, hardware, network backbone', '✓', ''], ['Hypervisor, managed service infrastructure', '✓', ''], ['Identities, MFA, policies', '', '✓'], ['Data classification and encryption choices', '', '✓'], ['Security groups, patching EC2 guest OS', '', '✓'], ['Turning on detection and responding', '', '✓']], minw=460))

SOLVE = detect_scene()

def mapfig():
    o = t(320, 16, 'Seven security services to know first', 11, 'ink', bold=True)
    items = [('1', 'CloudTrail', 'who did what, when', 'card'), ('2', 'GuardDuty', 'threat detection', 'amber'), ('3', 'Security Hub', 'findings + posture (CSPM)', 'violet'), ('4', 'AWS Config', 'configuration history + rules', 'blue'),
             ('5', 'Inspector', 'vulnerability scanning', 'red'), ('6', 'Macie', 'sensitive data in S3', 'green'), ('7', 'Secrets Manager', 'no secrets in code', 'blue')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 8.4, 'ink', bold=True) + t(x + 78, y + 54, b, 6.8, 'ink2')
    o += t(320, 210, 'Record (1), detect (2, 5, 6), assess (3, 4), and remove secrets from code (7).', 7.4, 'ink2')
    return o
MAP = bigfig('Map of seven security services: CloudTrail, GuardDuty, Security Hub, AWS Config, Inspector, Macie, Secrets Manager.', mapfig(), h=222)

def sb(n, name, tone, d, an, ex, tip, A, use, avoid, plain, how, words, diff, rw, pro):
    return vt(n, name, tone, d, an, ex, tip, '', A, use, avoid, plain, how, words, diff, ['CLF-C02 Domain 2', 'SAA-C03 / Security Specialty', 'C-DAC cloud security'], rw, pro)

A1 = mk(['API call', 'Event recorded', 'Trail to S3'], ['call|console, CLI|SDK', 'event|who, what, IP|time', 'trail|S3 + validation|years'], ['card', 'amber', 'green'],
        ['every API call is made', 'CloudTrail records an event', 'a trail delivers events to S3 for long-term, tamper-evident storage'], [('Call', 'Any API action.', ''), ('Record', 'Event history 90 days.', ''), ('Keep', 'Trail → S3, log file validation.', '')], 'CloudTrail', 'The CCTV of your account.', 'CloudTrail', 'Animation: API call; event recorded; trail to S3.', 's1anim')
T1 = sb(1, 'AWS CloudTrail', 'card',
    '<b>CloudTrail</b> records API activity in your account — who, what action, when, from which IP, on which resource, success or failure; event history keeps 90 days of management events free, and a <b>trail</b> delivers events from all Regions to S3 (optionally CloudWatch Logs) with log-file integrity validation.',
    'CCTV with a time-stamped recording of every door opened.',
    'Investigating the Sunday attack: lookup by the leaked access key ID shows every call it made.',
    'Tip: create one multi-Region trail on day one; send it to a separate, locked log account in organisations.', A1,
    'always — it is the foundation of investigation and audit.', 'relying only on 90-day event history for compliance.',
    'A record of every action in your AWS account.',
    [('Event history', '90 days, free.'), ('Trail', 'All Regions → S3.'), ('Validation', 'Digest files.'), ('Data events', 'S3 object/Lambda level (extra cost).'), ('Lake', 'CloudTrail Lake for SQL queries.')],
    [('management event', 'control-plane action like CreateBucket'), ('data event', 'object-level action like GetObject'), ('log file validation', 'proof logs were not altered')],
    table(['', 'Event history', 'Trail'], [['Retention', '90 days', 'as long as you keep the S3 objects'], ['Cost', 'free', 'first copy of management events free; S3 storage'], ['Data events', 'no', 'optional']], minw=420),
    'CLF-C02: “which service records API calls?” → CloudTrail.',
    'CERT-In asks Indian organisations to keep logs for 180 days — a trail plus S3 lifecycle does it.')

A2 = mk(['Logs in', 'Analysis', 'Finding'], ['inputs|CloudTrail, VPC flow|DNS, EKS, S3', 'analyse|ML + threat intel|anomalies', 'finding|type + severity|→ act'], ['amber', 'violet', 'red'],
        ['GuardDuty reads CloudTrail, VPC Flow Logs and DNS logs itself', 'machine learning and threat intelligence look for attacks', 'it raises findings with a type and severity'], [('Inputs', 'No agents to install for core sources.', ''), ('Analyse', 'ML, threat intel, anomalies.', ''), ('Finding', 'Type, severity, resource.', '')], 'GuardDuty', 'The guard watching the CCTV.', 'GuardDuty', 'Animation: logs in; analysis; finding.', 's2anim')
T2 = sb(2, 'Amazon GuardDuty', 'amber',
    '<b>GuardDuty</b> is a managed threat-detection service that continuously analyses CloudTrail events, VPC Flow Logs and DNS logs (plus optional S3, EKS, RDS, Lambda, malware and runtime protection) using threat intelligence and machine learning, producing findings such as compromised credentials, crypto-mining or communication with known malicious IPs.',
    'A trained security guard who watches all CCTV screens and knows the faces of known thieves.',
    'Finding <i>CryptoCurrency:EC2/BitcoinTool.B!DNS</i>: an instance is talking to a mining pool.',
    'Tip: enable it in every Region you use (attackers pick the Regions you do not watch); 30-day free trial.', A2,
    'every account, every Region.', 'treating findings as noise — route high severity to a human or automation.',
    'An automatic guard that spots attacks in your account.',
    [('Enable', 'One click per Region.'), ('Sources', 'Trail, flow, DNS.'), ('Findings', 'Type + severity.'), ('Samples', 'Generate to test alerts.'), ('Route', 'EventBridge.')],
    [('finding', 'detected threat'), ('severity', 'low/medium/high/critical'), ('threat intelligence', 'lists of known bad IPs/domains')],
    table(['', 'GuardDuty', 'Inspector'], [['Finds', 'active threats/behaviour', 'software vulnerabilities'], ['Inputs', 'logs', 'scans of instances, images, Lambda']], minw=420),
    'Exam: “detect malicious activity / compromised instances” → GuardDuty.',
    'Use create-sample-findings to test your alert pipeline without being attacked.')

A3 = mk(['Many sources', 'One view', 'Prioritise'], ['sources|GuardDuty, Inspector|Macie, CSPM', 'view|one console|all accounts', 'act|risk score|automation'], ['violet', 'amber', 'green'],
        ['findings arrive from many services', 'Security Hub shows them in one place', 'it correlates and prioritises risk; CSPM checks configuration standards'], [('Collect', 'GuardDuty, Inspector, Macie, partners.', ''), ('Posture', 'CSPM standards checks.', ''), ('Prioritise', 'Exposure + risk analytics.', '')], 'Security Hub', 'One security dashboard.', 'Security Hub', 'Animation: many sources; one view; prioritise.', 's3anim')
T3 = sb(3, 'AWS Security Hub (and Security Hub CSPM)', 'violet',
    '<b>AWS Security Hub</b> (new version generally available since December 2025) unifies findings from GuardDuty, Inspector, Macie and Security Hub CSPM, correlating them into prioritised exposures; <b>Security Hub CSPM</b> (the original Security Hub) runs posture checks against standards such as AWS Foundational Security Best Practices and CIS benchmarks.',
    'A control room that combines CCTV, fire alarms and door sensors into one screen, sorted by danger.',
    'Monday morning: one prioritised list — a public bucket, an unpatched instance and the GuardDuty finding.',
    'Tip: the posture score shows how many controls pass — a good monthly KPI.', A3,
    'more than a handful of resources or accounts.', 'expecting it to detect threats itself — it aggregates and checks posture.',
    'One place that gathers and ranks all security problems.',
    [('Enable', 'Per account/Region or org-wide.'), ('Standards', 'FSBP, CIS.'), ('Findings', 'ASFF/OCSF format.'), ('Automation rules', 'Suppress/route.'), ('Integrations', 'Ticketing, SIEM.')],
    [('CSPM', 'cloud security posture management'), ('control', 'one automated check'), ('standard', 'a set of controls, e.g. CIS')],
    table(['', 'Security Hub', 'Security Hub CSPM'], [['Focus', 'unified findings, risk analytics', 'configuration checks'], ['Example output', 'prioritised exposure', '“S3 bucket allows public read” failed']], minw=440),
    'Exam: “central view of security findings across accounts” → Security Hub.',
    'Older material says only “Security Hub” — read the date of what you study.')

A4 = mk(['Record config', 'Rules evaluate', 'Remediate'], ['record|every change|timeline', 'rules|compliant?|managed/custom', 'fix|SSM automation|or alert'], ['blue', 'amber', 'green'],
        ['Config records every configuration change', 'rules evaluate resources as compliant or not', 'non-compliant resources can be fixed automatically'], [('Record', 'Configuration history.', ''), ('Evaluate', 'Managed/custom rules.', ''), ('Remediate', 'Automation documents.', '')], 'AWS Config', 'Was it always like this?', 'Config', 'Animation: record config; rules evaluate; remediate.', 's4anim')
T4 = sb(4, 'AWS Config', 'blue',
    '<b>AWS Config</b> records the configuration of resources over time and evaluates them against rules (for example <code>s3-bucket-ssl-requests-only</code>, <code>encrypted-volumes</code>, <code>restricted-ssh</code>), showing compliance history and optionally auto-remediating with Systems Manager Automation.',
    'A building inspector’s logbook: what changed, when, and whether it meets the code.',
    'Rule flags a security group that opened port 22 to 0.0.0.0/0 at 3 pm — and closes it automatically.',
    'Tip: Config answers “what did this resource look like last Tuesday?” — invaluable in incidents.', A4,
    'compliance, audits, drift detection.', 'recording every resource type in a learning account — costs grow with changes.',
    'A history of every setting and a checker for rules.',
    [('Recorder', 'Choose resource types.'), ('Rules', 'Managed/custom.'), ('Conformance packs', 'Bundles.'), ('Remediation', 'SSM docs.'), ('Aggregator', 'Multi-account.')],
    [('configuration item', 'snapshot of a resource'), ('conformance pack', 'set of rules'), ('remediation', 'automatic fix')],
    table(['', 'CloudTrail', 'Config'], [['Answers', 'who did it?', 'what does it look like / did it comply?'], ['Data', 'API events', 'resource configurations']], minw=420),
    'Exam: “track configuration changes and compliance” → Config; “who made the change” → CloudTrail.',
    'Lab-exam proofs like “HTTPS-only” can be confirmed by the s3-bucket-ssl-requests-only rule too.')

A5 = mk(['Discover', 'Scan', 'Prioritise'], ['discover|EC2, ECR|Lambda', 'scan|CVEs|network reach', 'score|risk|fix first'], ['red', 'amber', 'green'],
        ['Inspector discovers instances, images and functions automatically', 'scans them for known vulnerabilities and network exposure', 'scores findings so you patch the riskiest first'], [('Discover', 'Automatic.', ''), ('Scan', 'CVEs, exposure.', ''), ('Score', 'Inspector risk score.', '')], 'Inspector', 'Find unpatched software.', 'Inspector', 'Animation: discover; scan; prioritise.', 's5anim')
T5 = sb(5, 'Amazon Inspector', 'red',
    '<b>Amazon Inspector</b> continuously scans EC2 instances, container images in ECR and Lambda functions for software vulnerabilities (CVEs) and unintended network exposure, scoring findings by severity and exploitability.',
    'A mechanic checking every car in the fleet for known recalls.',
    'An old OpenSSL on the dashboard server is flagged CRITICAL; patch window scheduled.',
    'Tip: needs the SSM agent on EC2 for the deepest scans (agent-less scanning also exists).', A5,
    'you run EC2, containers or Lambda.', 'confusing it with GuardDuty — Inspector finds weaknesses, GuardDuty finds attacks.',
    'A scanner that finds unpatched software.',
    [('Enable', 'Account/org.'), ('Coverage', 'EC2, ECR, Lambda.'), ('Findings', 'CVE + score.'), ('Fix', 'Patch Manager.'), ('Report', 'SBOM export.')],
    [('CVE', 'public ID of a known vulnerability'), ('SBOM', 'software bill of materials'), ('exploitability', 'how easy to attack')],
    table(['', 'Inspector', 'Macie'], [['Looks at', 'software and network reach', 'data inside S3'], ['Finds', 'vulnerabilities', 'PII, credentials in files']], minw=420),
    'Exam: “identify software vulnerabilities in EC2” → Inspector.',
    'Wire findings to Patch Manager maintenance windows so patching is routine, not heroic.')

A6 = mk(['Inventory buckets', 'Sample data', 'Report PII'], ['inventory|public?|encrypted?', 'sample|ML + patterns|custom IDs', 'report|Aadhaar-like, cards|credentials'], ['green', 'amber', 'red'],
        ['Macie inventories buckets: public, shared, encrypted?', 'it samples objects with ML and patterns', 'it reports sensitive data such as personal data or credentials'], [('Inventory', 'Bucket security posture.', ''), ('Discover', 'Automated sensitive data discovery.', ''), ('Report', 'Findings by type and location.', '')], 'Macie', 'Where is the sensitive data?', 'Macie', 'Animation: inventory; sample; report.', 's6anim')
T6 = sb(6, 'Amazon Macie', 'green',
    '<b>Amazon Macie</b> discovers and protects sensitive data in S3: it inventories buckets (public, shared, unencrypted) and uses machine learning and pattern matching — including custom data identifiers — to find personal data, financial data and credentials inside objects.',
    'A librarian who checks every shelf for documents that should be in the locked cabinet.',
    'Macie finds a CSV with phone numbers and PAN-like values in a bucket meant for public brochures.',
    'Tip: add custom identifiers for Indian formats (e.g. student roll numbers) where built-ins do not cover them.', A6,
    'buckets may contain personal or regulated data.', 'scanning huge buckets fully without a budget — use automated sampling.',
    'A tool that finds personal or secret data hidden in your files.',
    [('Enable', 'Per Region.'), ('Inventory', 'Bucket posture.'), ('Discovery', 'Automated sampling.'), ('Jobs', 'Targeted scans.'), ('Identifiers', 'Custom regex.')],
    [('PII', 'personally identifiable information'), ('data identifier', 'pattern for a data type'), ('sensitive data discovery', 'Macie’s scanning')],
    table(['Data type', 'Example'], [['Personal', 'names, phone, addresses'], ['Financial', 'card numbers, bank accounts'], ['Credentials', 'AWS keys, private keys']], minw=360),
    'Exam: “discover PII in S3” → Macie.',
    'DPDP compliance starts with knowing where personal data is — Macie is the inventory tool.')

A7 = mk(['Secret stored', 'App fetches', 'Auto-rotate'], ['store|encrypted|with KMS', 'fetch|role permission|at runtime', 'rotate|Lambda|no app change'], ['blue', 'amber', 'green'],
        ['store the password or API key in Secrets Manager (KMS-encrypted)', 'the app fetches it at runtime using its role', 'rotation changes it automatically without code changes'], [('Store', 'Encrypted with KMS.', ''), ('Fetch', 'GetSecretValue via role.', ''), ('Rotate', 'Scheduled rotation.', '')], 'Secrets Manager', 'No secrets in code.', 'Secrets', 'Animation: secret stored; app fetches; auto-rotate.', 's7anim')
T7 = sb(7, 'AWS Secrets Manager', 'blue',
    '<b>Secrets Manager</b> stores database passwords, API keys and other secrets encrypted with KMS, lets applications retrieve them at runtime through IAM permissions, logs access in CloudTrail, and can rotate them automatically (built-in for RDS and other databases).',
    'A bank locker for passwords: the app shows its ID and gets the password just when it needs it.',
    'The dashboard reads the database password from Secrets Manager; rotation changes it every 30 days.',
    'Tip: Systems Manager Parameter Store (SecureString) is a cheaper option for simple, non-rotating config values.', A7,
    'apps need passwords or API keys.', 'storing secrets in code, AMIs, user data or environment files.',
    'A safe place for passwords that apps can fetch securely.',
    [('Create', 'Secret value.'), ('Encrypt', 'KMS key.'), ('Policy', 'Who may read.'), ('Fetch', 'SDK at runtime.'), ('Rotate', 'Lambda rotation.')],
    [('secret', 'sensitive value like a password'), ('rotation', 'regular automatic change'), ('Parameter Store', 'SSM config store, SecureString for secrets')],
    table(['', 'Secrets Manager', 'Parameter Store'], [['Rotation', 'built-in', 'no (DIY)'], ['Cost', 'per secret + API calls', 'standard tier free'], ['Best for', 'DB creds, API keys', 'config, simple secrets']], minw=420),
    'Exam: “store and rotate database credentials” → Secrets Manager.',
    'Git history scanners still find old secrets — rotate anything that was ever committed.')

SUMMARY = table(['#', 'Service', 'Question it answers', 'Layer'], [
    ['1', 'CloudTrail', 'who did what?', 'record'], ['2', 'GuardDuty', 'are we being attacked?', 'detect'], ['3', 'Security Hub', 'what matters most right now?', 'prioritise'],
    ['4', 'Config', 'what changed / is it compliant?', 'assess'], ['5', 'Inspector', 'what is unpatched/exposed?', 'detect weaknesses'], ['6', 'Macie', 'where is sensitive data?', 'data'], ['7', 'Secrets Manager', 'where do apps keep passwords?', 'prevent']], minw=560)

TYPES = ('  <p>Seven security services, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, real-world example and an expert tip.</p>\n'
         + challenge(['Which service finds an instance talking to a crypto-mining pool?', 'CloudTrail or Config: “what did this security group look like yesterday?”', 'Where should a database password live?'], 'types 2, 4 and 7') + MAP
         + jump(['CloudTrail', 'GuardDuty', 'Security Hub', 'Config', 'Inspector', 'Macie', 'Secrets']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY)

parts = wwu([
    ('Prevent', 'identity, network, encryption.', 'Stops most attacks.', 'Lessons 1.2–2.4.'),
    ('Record', 'CloudTrail trail, Config.', 'Evidence for everything.', 'All Regions, 180+ days.'),
    ('Detect', 'GuardDuty, Inspector, Macie.', 'See problems early.', 'Every Region.'),
    ('Prioritise', 'Security Hub.', 'Fix what matters first.', 'One list.'),
    ('Respond', 'EventBridge + Lambda + SNS.', 'Minutes, not days.', 'Auto-disable keys.'),
    ('Learn', 'incident reviews, guard-rails.', 'Never the same incident twice.', 'Blameless postmortems.')])

DEEP = ('  <h3>Incident response: the five steps (practise them)</h3>\n' + table(['Step', 'What you do on AWS', 'Example (leaked key)'], [
        ['1 Contain', 'stop the damage', 'deactivate the access key; stop/isolate instances (security group with no rules)'], ['2 Investigate', 'collect evidence', 'CloudTrail lookup by access key ID; GuardDuty finding details; snapshot disks'],
        ['3 Eradicate', 'remove the cause', 'delete the key, attacker-created users/roles/instances; rotate related secrets'], ['4 Recover', 'restore normal service', 'redeploy clean resources; verify bill; contact AWS Support for billing review'],
        ['5 Learn', 'prevent recurrence', 'remove long-term keys; SCPs; secret scanning; update runbook']], minw=600) +
    '  <h3>India-specific obligations to remember</h3>\n  <ul><li><b>CERT-In (April 2022 directions):</b> report specified cyber incidents within 6 hours; keep ICT system logs for 180 days within India.</li><li><b>DPDP Act 2023 and Rules (notified November 2025):</b> report personal-data breaches to the Data Protection Board and affected people; detailed report within 72 hours.</li><li>Sector regulators (RBI, SEBI, IRDAI) add their own timelines — check your sector.</li></ul>\n'
    '  <h3>An alert rule for high-severity findings</h3>\n' + code('json', 'EventBridge pattern: GuardDuty findings with severity ≥ 7', '{\n  "source": ["aws.guardduty"],\n  "detail-type": ["GuardDuty Finding"],\n  "detail": {"severity": [{"numeric": [">=", 7]}]}\n}'))

clouds = vendor_tabs('<p><b>AWS:</b> CloudTrail, GuardDuty, Security Hub (+ CSPM), Config, Inspector, Macie, Secrets Manager, Detective.</p>',
    '<p><b>Azure:</b> Activity Log, Microsoft Defender for Cloud (posture + threat protection), Azure Policy, Microsoft Sentinel (SIEM), Purview for data discovery, Key Vault.</p>',
    '<p><b>Google Cloud:</b> Cloud Audit Logs, Security Command Center (posture + threats), Sensitive Data Protection, Secret Manager, Assured Workloads.</p>') + \
    cloud3([['Audit log', 'CloudTrail', 'Activity Log', 'Cloud Audit Logs'], ['Threat detection', 'GuardDuty', 'Defender for Cloud', 'Security Command Center'], ['Posture/central view', 'Security Hub', 'Defender for Cloud / Sentinel', 'Security Command Center'], ['Secrets', 'Secrets Manager', 'Key Vault', 'Secret Manager']])

MOCKA.extend([
 mock('aws', ['CloudTrail', 'Trails', 'Create trail'], ['Dashboard', 'Event history', 'Trails'], 'Trails', [('Trail name', 'org-baseline'), ('Storage', 'new S3 bucket'), ('Log file validation', '[x] Enabled')], 'Create trail'),
 mock('aws', ['GuardDuty', 'Findings'], ['Summary', 'Findings', 'Settings'], 'Findings', [('Sample findings', 'Settings → Generate sample findings'), ('Filter', 'Severity: High')], 'Generate'),
 mock('aws', ['EventBridge', 'Rules', 'Create rule'], ['Rules', 'Event buses'], 'Rules', [('Event pattern', 'aws.guardduty · severity ≥ 7'), ('Target', 'SNS topic security-alerts')], 'Create rule'),
])

STEP1 = astep('1 · A CloudTrail trail for all Regions, with integrity validation',
    ['[[CloudTrail]] → [[Trails]] → [[Create trail]] → name <code>baseline</code> → new S3 bucket → Log file validation enabled → (multi-Region is the default) → [[Create trail]].'],
    "ACC=$(aws sts get-caller-identity --query Account --output text); TB=trail-$ACC\naws s3 mb s3://$TB --region ap-south-1\ncat > tp.json <<EOF\n{\"Version\":\"2012-10-17\",\"Statement\":[\n{\"Sid\":\"AclCheck\",\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"cloudtrail.amazonaws.com\"},\"Action\":\"s3:GetBucketAcl\",\"Resource\":\"arn:aws:s3:::$TB\"},\n{\"Sid\":\"Write\",\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"cloudtrail.amazonaws.com\"},\"Action\":\"s3:PutObject\",\"Resource\":\"arn:aws:s3:::$TB/AWSLogs/$ACC/*\",\"Condition\":{\"StringEquals\":{\"s3:x-amz-acl\":\"bucket-owner-full-control\"}}}]}\nEOF\naws s3api put-bucket-policy --bucket $TB --policy file://tp.json\naws cloudtrail create-trail --name baseline --s3-bucket-name $TB --is-multi-region-trail --enable-log-file-validation >/dev/null\naws cloudtrail start-logging --name baseline\naws cloudtrail get-trail-status --name baseline --query '[IsLogging,LatestDeliveryTime]' --output text",
    '<code>True</code> and, after a few minutes, a delivery time — events from every Region now land in your bucket, with digest files proving they were not altered.',
    'Add an S3 lifecycle rule (Lesson 4.4) to keep logs at least 180 days for CERT-In; move older ones to cheaper storage.')

STEP2 = astep('2 · GuardDuty with sample findings',
    ['[[GuardDuty]] → [[Get started]] → [[Enable GuardDuty]] (30-day free trial).', '[[Settings]] → [[Generate sample findings]] → [[Findings]]: filter High severity and open one.'],
    "DET=$(aws guardduty create-detector --enable --query DetectorId --output text 2>/dev/null || aws guardduty list-detectors --query 'DetectorIds[0]' --output text)\naws guardduty create-sample-findings --detector-id $DET\nsleep 20\naws guardduty list-findings --detector-id $DET --finding-criteria '{\"Criterion\":{\"severity\":{\"Gte\":7}}}' --max-results 5 --query FindingIds --output text | tr '\\t' '\\n' | head -3 > ids.txt\naws guardduty get-findings --detector-id $DET --finding-ids $(cat ids.txt) --query 'Findings[].[Type,Severity,Title]' --output table",
    'a table of high-severity sample findings (types like <code>CryptoCurrency:EC2/BitcoinTool.B!DNS</code> or <code>UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration…</code>), each marked as a sample.',
    'Sample findings are labelled [SAMPLE] and safe — perfect for testing alert pipelines without being attacked.')

STEP3 = astep('3 · Alert on high-severity findings (EventBridge → SNS)',
    ['[[SNS]] → [[Create topic]] <code>security-alerts</code> → [[Create subscription]] e-mail → confirm from your inbox.', '[[EventBridge]] → [[Rules]] → [[Create rule]] → pattern from the Deep dive → target SNS topic.', 'Generate sample findings again and watch your inbox.'],
    "TOPIC=$(aws sns create-topic --name security-alerts --query TopicArn --output text)\naws sns subscribe --topic-arn $TOPIC --protocol email --notification-endpoint you@example.com\ncat > pattern.json <<'EOF'\n{\"source\":[\"aws.guardduty\"],\"detail-type\":[\"GuardDuty Finding\"],\"detail\":{\"severity\":[{\"numeric\":[\">=\",7]}]}}\nEOF\naws events put-rule --name guardduty-high --event-pattern file://pattern.json >/dev/null\naws sns set-topic-attributes --topic-arn $TOPIC --attribute-name Policy --attribute-value \"{\\\"Version\\\":\\\"2012-10-17\\\",\\\"Statement\\\":[{\\\"Effect\\\":\\\"Allow\\\",\\\"Principal\\\":{\\\"Service\\\":\\\"events.amazonaws.com\\\"},\\\"Action\\\":\\\"sns:Publish\\\",\\\"Resource\\\":\\\"$TOPIC\\\"}]}\"\naws events put-targets --rule guardduty-high --targets Id=sns,Arn=$TOPIC\naws guardduty create-sample-findings --detector-id $DET --finding-types 'CryptoCurrency:EC2/BitcoinTool.B!DNS'",
    'a confirmation e-mail (click it), then within a few minutes an alert e-mail with the finding JSON — your detection → notification chain works.',
    'Replace you@example.com with your address. In production the target is often a Lambda function that also deactivates keys or isolates instances.')

prac = practical(AWS_INTRO + ' GuardDuty has a 30-day free trial; CloudTrail’s first management-event trail is free (you pay small S3 storage). Disable what you do not keep.', [AWS_SETUP, STEP1, STEP2, STEP3],
    cleanup="Keep the CloudTrail trail (good permanent practice) or delete it: <code>aws cloudtrail delete-trail --name baseline; aws s3 rb s3://$TB --force</code>. Alerts: <code>aws events remove-targets --rule guardduty-high --ids sns; aws events delete-rule --name guardduty-high; aws sns delete-topic --topic-arn $TOPIC</code>. GuardDuty after the trial: <code>aws guardduty delete-detector --detector-id $DET</code> (or keep it — recommended for real accounts).")

mist = mistakes([
    ['Only prevention, no detection.', 'MFA feels enough.', 'CloudTrail + GuardDuty + alerts on day one.'],
    ['GuardDuty in one Region only.', 'Only Mumbai is used.', 'Attackers use the Regions you ignore — enable everywhere (or block Regions by SCP).'],
    ['Alerts to an inbox nobody reads.', 'Set and forget.', 'Route high severity to on-call (SMS/chat) and automation.'],
    ['Deleting evidence while cleaning up.', 'Panic.', 'Contain first, snapshot, collect logs, then eradicate.'],
    ['Secrets in code or user data.', 'Convenience.', 'Secrets Manager / Parameter Store + roles.'],
    ['Never practising incident response.', '“It will not happen to us.”', 'Run a sample-finding drill each quarter.']])

cert = table(['Exam / syllabus', 'What is asked'], [['AWS CLF-C02', 'Shared responsibility; CloudTrail, GuardDuty, Inspector, Macie, Security Hub, Config, Secrets Manager use cases (Domain 2).'], ['SAA-C03 / Security Specialty', 'Detection and response architectures, EventBridge automation, multi-account security.'], ['C-DAC PGCP-BDA', 'Cloud security threats and controls; compliance.']], minw=560) + \
    '\n  <h3>Try exam-style questions</h3>\n' + qx('Detect compromised EC2 instances and malicious IPs?', ['GuardDuty', 'Macie', 'Config', 'Artifact'], 0, 'GuardDuty.') + \
    qx('Find personal data stored in S3?', ['Macie', 'Inspector', 'Shield', 'CloudFront'], 0, 'Macie.') + \
    qx('Store and automatically rotate database passwords?', ['Secrets Manager', 'S3', 'IAM access keys', 'CloudTrail'], 0, 'Secrets Manager.') + \
    qx('Under shared responsibility, who patches the guest OS on EC2?', ['AWS', 'the customer', 'both automatically', 'nobody'], 1, 'Customer.')

from deep_v3 import HOOD, ROLES, DOMAINS, PRO, PROJ, SIM, LADDER

assemble_v2(HERE, story_h2='Sunday 11:40 pm: caught in 12 minutes', hook_html=hk,
    narration='A leaked key started 20 servers in CityBite’s account late on Sunday. Because CloudTrail, GuardDuty and an alert automation were on, the key was disabled and the servers stopped within 12 minutes; the bill impact was about ₹300.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Security best practices',
    formal='<b>AWS security best practices</b> combine the shared responsibility model with defence in depth: strong identity (MFA, SSO, least privilege, no long-term keys), network and data protection (private networking, encryption, blocked public access), continuous recording and detection (CloudTrail, Config, GuardDuty, Inspector, Macie, Security Hub), automated response (EventBridge, Lambda, SNS) and practised incident response — applied as a baseline to every account.',
    simple='Lock the doors (prevent), switch on the CCTV and the guard (record and detect), and make the alarm call someone automatically (respond).',
    interview=['“My baseline: root MFA, SSO, roles not keys, CloudTrail in all Regions, GuardDuty and Security Hub on, default encryption, Block Public Access, budgets — then EventBridge rules that route high findings to on-call and automation.”', '“Incident response: contain (disable keys, isolate), investigate (CloudTrail, snapshots), eradicate, recover, and learn with guard-rails.”'],
    terms_rows=[('Shared responsibility', 'AWS: of the cloud; you: in the cloud.'), ('Defence in depth', 'Many layers of controls.'), ('CloudTrail trail', 'Long-term API log in S3.'), ('GuardDuty finding', 'Detected threat with severity.'), ('Security Hub', 'Unified findings and posture.'), ('AWS Config rule', 'Automated compliance check.'), ('Secrets Manager', 'Stores/rotates secrets.'), ('Incident response', 'Contain, investigate, eradicate, recover, learn.')],
    exam='Domain 2 of CLF-C02 (30%) asks which service fits a security need — use the seven-service table.',
    picture_h2='Layers, baseline and responsibility', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven security services, one by one', TYPES)],
    how_h2='Detect and respond, step by step', how_intro='A Sunday-night attack, handled by the baseline.', how_anim=SOLVE,
    parts_h2='Six parts of security on AWS', parts_html=parts, lv='',
    myth_rows=[('AWS secures my account for me.', 'AWS secures the cloud; you secure your configuration and data.', 'Big picture.'), ('Detection is only for big companies.', 'GuardDuty and CloudTrail are one click and cheap.', 'Story.'), ('Clean up first, investigate later.', 'Contain and collect evidence before deleting.', 'Deep dive.')],
    extra_secs=[('ladder', 'Learn at your level', 'From curious beginner to expert — pick your level', LADDER), ('deep', 'Deep dive', 'Incident response steps; Indian reporting rules; alert pattern', DEEP), ('hood', 'Under the hood', 'How GuardDuty, Config and Security Hub work; costs; multi-account', HOOD), ('roles', 'By role', 'Security duties of developers, data, ML, DevOps and security people', ROLES), ('domains', 'By domain', 'Security baselines by industry', DOMAINS), ('pro', 'For working professionals', 'Costs, errors, cheat sheet, checklist', PRO)],
    clouds_html=clouds, practical_html=prac + '\n  <h3 id="simulator">Practice without an account: simulator</h3>\n  <p>Switch on the baseline and watch an alert travel from GuardDuty to your inbox.</p>\n' + SIM, mistakes_html=mist, cert_html=cert, project_html=PROJ,
    can_now=['Explain shared responsibility and defence in depth.', 'Apply the ten-setting account baseline.', 'Choose the right security service for a need.', 'Build a detection → alert chain with GuardDuty, EventBridge and SNS.', 'Run the five incident-response steps.'],
    next_html='Module 2 complete. Next: <a href="../../03-compute/01-ec2-instances/">3.1 EC2 instances</a>.',
    pre='<b>Before you start:</b> Lessons 2.1–2.4.')
