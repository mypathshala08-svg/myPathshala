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


hk = hook('Saturday 2 am: TiffinGo’s cloud bill jumps from ₹300 a day to ₹2.4 lakh. Forty large GPU servers are mining cryptocurrency in a Region nobody uses. How did the attackers get in — and how could TiffinGo have known in minutes, not on Monday?',
    'A developer had pushed an <b>access key</b> to a public GitHub repo. Bots found it in minutes. This lesson covers the seven threats behind most cloud incidents — <b>misconfiguration</b>, <b>credential theft</b>, <b>insecure APIs</b>, <b>vulnerable workloads</b>, <b>DDoS</b>, <b>ransomware</b> and <b>insiders</b> — one by one, animates a real-style attack from leaked key to containment, and on <b>your own</b> account you switch on threat detection with sample findings, audit old keys, and set a cost-anomaly alarm that would have caught the miners.',
    ['Why attackers rarely “hack” the cloud — they log in.', 'The bill as a security signal: cryptojacking shows up as cost first.', 'What to do in the first 15 minutes after a leaked key.'])

def story_scene():
    o = t(180, 12, 'From a leaked key to a ₹2.4 lakh bill', 9, 'ink', bold=True)
    S = [('git push', 'key in code', 'amber'), ('bot scan', 'minutes', 'red'), ('40 GPUs', 'unused Region', 'red'), ('bill spike', 'found Monday', 'violet')]
    for i, (a, b, tn) in enumerate(S):
        x = 8 + i * 88
        o += box(x, 32, 80, 54, tn, rx=8) + t(x + 40, 54, a, 8, 'ink', bold=True) + t(x + 40, 70, b, 7, 'ink2')
        if i < 3: o += arrow(x + 80, 59, x + 88, 59)
    o += t(180, 110, 'Detection in minutes would have stopped it at step 2', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Timeline: key pushed to GitHub, bots scan within minutes, 40 GPU servers launched in an unused Region, bill spike found on Monday.', story_scene(), 'Attackers <tspan font-weight="700" class="s-acc">log in</tspan> more often than they break in.', h=124)
dialogue = '''K> Sir, I only pushed the code for ten minutes and then deleted the file.
A> Git keeps history, and bots scan public repos continuously. Ten minutes is plenty.
R> Couldn’t AWS stop it?
A> AWS did email a warning about an exposed key — to an inbox nobody reads. Threat detection and a cost alarm would have paged us at 2 am.
K> So what are the main threats?
A> Seven. Most start with a mistake or a stolen login, not a movie-style hack. Let’s go through them.'''

def surffig():
    o = t(320, 16, 'Where attacks enter a cloud account', 11, 'ink', bold=True)
    o += box(230, 70, 180, 90, 'blue', rx=12) + t(320, 100, 'Your cloud account', 9, 'ink', bold=True) + t(320, 118, 'data · compute · identities', 7.2, 'ink2') + t(320, 134, 'APIs · storage · networks', 7.2, 'ink2')
    E = [(40, 40, 'Leaked keys / weak passwords', 'red'), (40, 110, 'Public buckets, open ports', 'amber'), (40, 180, 'Unpatched apps, bad libraries', 'amber'), (450, 40, 'Insecure APIs', 'violet'), (450, 110, 'DDoS floods', 'violet'), (450, 180, 'Insiders, ex-staff', 'red')]
    for x, y, s, tn in E:
        o += box(x, y - 14, 150, 28, tn, rx=6) + t(x + 75, y + 4, s, 7.2, 'ink', bold=True)
        o += arrow(x + 150, y, 228, 115) if x < 200 else arrow(x, y, 412, 115)
    o += t(320, 222, 'Ransomware and data theft are what attackers do after getting in through one of these doors.', 7.4, 'ink2')
    return o
SURF = bigfig('A central box for the cloud account with arrows from six entry points: leaked keys and weak passwords, public buckets and open ports, unpatched apps, insecure APIs, DDoS floods, insiders.', surffig(), h=232)

picture = ('  <p>Cloud attack surface in one picture:</p>\n' + SURF +
           '\n  <h3>Cloud threats vs traditional threats</h3>\n' + table(['', 'Traditional data centre', 'Cloud'], [
               ['Perimeter', 'office firewall', 'identity is the perimeter (API calls from anywhere)'], ['Mistake impact', 'one server', 'one setting can expose everything, globally'], ['Speed', 'manual changes, slow', 'automation: attacker and defender both move in seconds'],
               ['Visibility', 'network taps', 'API logs (CloudTrail, Activity Log, Audit Logs)'], ['New threats', '—', 'leaked keys, cryptojacking, metadata-service abuse, cross-tenant risks']], minw=600) +
           '\n  <p>The Cloud Security Alliance publishes a regular “Top Threats to Cloud Computing” list; recent editions rank misconfiguration, identity and access management weaknesses, insecure interfaces and APIs, and inadequate cloud security strategy near the top.</p>')

RN = {'key': (4, 54, 50, 50, 'disk', 'Leaked key', 'public repo'), 'enum': (66, 4, 62, 46, 'globe', 'Recon', 'list, describe'), 'abuse': (66, 104, 62, 46, 'server', 'Abuse', '40 GPU VMs'),
      'det': (142, 54, 60, 50, 'shield', 'Detection', 'GuardDuty etc.'), 'alert': (216, 4, 62, 46, 'phone', 'Alert', 'on-call'), 'cont': (216, 104, 62, 46, 'gear', 'Contain', 'disable key'), 'rec': (292, 54, 64, 50, 'chart', 'Recover', 'review, harden')}
RS = [dict(on=['key'], hot='key', move=None, head='Step 1 · A long-lived key leaks', text='An access key with admin rights is committed to a public repository. Automated', text2='scanners (attackers’ and providers’) find it within minutes.', svc='Fix the root: no long-lived keys in code — use roles, OIDC, secrets managers'),
      dict(on=['key', 'enum'], hot='enum', move=(54, 79, 72, 30, 'API'), head='Step 2 · Reconnaissance through the API', text='The attacker calls “who am I”, lists Regions, buckets and quotas — normal API calls,', text2='but from a new country, at 2 am, by a key never used before.', svc='Every call is recorded in CloudTrail / Activity Log / Audit Logs'),
      dict(on=['enum', 'abuse'], hot='abuse', move=(97, 50, 97, 104, 'launch'), head='Step 3 · Abuse: mining and data theft', text='GPU instances start in an unused Region; buckets are copied out. Cost and data', text2='leave together.', svc='Cryptojacking + exfiltration — the two most common goals'),
      dict(on=['enum', 'abuse', 'det'], hot='det', move=(128, 127, 150, 90, 'finding'), head='Step 4 · Threat detection notices', text='Managed detection flags “API calls from a known malicious IP”, “unusual Region”,', text2='“crypto-mining traffic” — within minutes of the first calls.', svc='GuardDuty · Defender for Cloud · Security Command Center'),
      dict(on=['det', 'alert', 'cont'], hot='cont', move=(202, 66, 226, 30, 'page'), head='Step 5 · Contain in the first 15 minutes', text='Deactivate the key, stop/snapshot rogue instances, block the IP, check for new', text2='users or keys the attacker created (persistence).', svc='Runbooks or automated responses (EventBridge + Lambda / Logic Apps / Cloud Functions)'),
      dict(on=list(RN), hot='rec', move=(278, 127, 298, 90, 'fix'), head='Step 6 · Recover and harden', text='Review audit logs for everything the key did, rotate secrets, notify if personal data', text2='was taken, remove long-lived keys, add guard-rails and cost alarms.', svc='Blameless review: which control would have stopped step 1?')]
ATTACK = flow_anim('Anatomy of a cloud attack, and the response', 'A leaked key, step by step — and where defenders can step in.', 'Cloud attack', 'Animation: leaked key; API reconnaissance; abuse with mining and data theft; threat detection finding; containment; recovery and hardening.', RN, RS, hid='atkflow')

def mapfig():
    o = t(320, 16, 'Seven cloud threats', 11, 'ink', bold=True)
    items = [('1', 'Misconfiguration', 'public data, open ports', 'amber'), ('2', 'Credential theft', 'leaked keys, phishing, no MFA', 'red'), ('3', 'Insecure APIs', 'broken auth, no limits', 'violet'), ('4', 'Vulnerable workloads', 'unpatched, bad libraries', 'amber'),
             ('5', 'DDoS', 'floods to knock you offline', 'violet'), ('6', 'Ransomware', 'encrypt/delete data for money', 'red'), ('7', 'Insider threats', 'staff, ex-staff, partners', 'blue')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 8, 'ink', bold=True) + t(x + 78, y + 54, b, 6.4, 'ink2')
    o += t(320, 210, '1–2 cause most incidents; 6 is usually the result of 1, 2 or 4.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of seven threats: misconfiguration, credential theft, insecure APIs, vulnerable workloads, DDoS, ransomware, insider threats.', mapfig(), h=222)

A1 = mk(['Setting changed', 'Exposed', 'Found by scanners'], ['change|bucket public|port 22 open', 'exposure|internet-wide|in seconds', 'scanners|bots index it|data copied'], ['amber', 'red', 'red'],
        ['someone changes a setting for convenience', 'the resource becomes reachable from the whole internet', 'automated scanners find and exploit it quickly'],
        [('Change', 'A setting is loosened for convenience.', ''), ('Exposed', 'The resource is reachable from the internet.', ''), ('Found', 'Scanners find and exploit it quickly.', '')],
        'Misconfiguration in action', 'One setting, global exposure.', 'Misconfiguration', 'Animation: setting changed; exposed; found by scanners.', 't1anim')
T1 = vt(1, 'Misconfiguration', 'amber',
    '<b>Misconfiguration</b> is an insecure setting of a cloud resource — public storage, open management ports, overly permissive access policies, disabled logging or encryption — that exposes data or systems, typically caused by human error, defaults left unchanged or missing guard-rails.',
    'Leaving the shop shutter half open overnight: nobody broke anything — the door was simply not closed.',
    'The intern’s public bucket in Lesson 9.1, and a test VM with SSH open to 0.0.0.0/0 that was brute-forced within hours.',
    'Defences: AWS Config + Security Hub CSPM, Azure Policy + Defender for Cloud, Google SCC + organization policies; IaC scanning (Checkov, tfsec).', 'Guard-rails were built in 9.1.', A1,
    'always assume it will happen — automate detection and prevention.',
    'you rely on “people will be careful” — they will not, at scale.',
    'A wrong or careless setting that leaves data or servers open to the internet.',
    [('Prevent', 'Org policies, account-level blocks.'), ('Template', 'Secure IaC modules.'), ('Scan', 'IaC and posture scans.'), ('Detect', 'Config rules, alerts.'), ('Fix', 'Auto-remediation.')],
    [('posture', 'overall security state of your settings'), ('CSPM', 'cloud security posture management'), ('0.0.0.0/0', 'any IP address on the internet')],
    table(['', 'Misconfiguration', 'Vulnerability'], [['Cause', 'insecure setting', 'flaw in software'], ['Fix', 'change config', 'patch/update'], ['Found by', 'CSPM, config rules', 'vulnerability scanners']], minw=420),
    ['Storage', 'Network rules', 'IAM policies'],
    'Many of the largest cloud data exposures have been publicly accessible storage buckets or databases — no exploit needed.',
    'Shift left: scan Terraform/Bicep in the pipeline (Lesson 8.3) so misconfigurations never reach the cloud.')

A2 = mk(['Credential leaked', 'Attacker logs in', 'Acts as you'], ['leak|key in Git|phished password', 'login|valid API calls|no exploit', 'abuse|create, copy|delete'], ['red', 'red', 'amber'],
        ['a key or password is leaked, phished or guessed', 'the attacker uses it like a normal user', 'everything it can do, the attacker can do'],
        [('Leak', 'Key in code, phishing, reused password.', ''), ('Login', 'Attacker uses valid credentials.', ''), ('Abuse', 'Acts with the victim’s permissions.', '')],
        'Credential theft in action', 'They log in, they don’t break in.', 'Credential theft', 'Animation: credential leaked; attacker logs in; acts as you.', 't2anim')
T2 = vt(2, 'Credential theft and account hijacking', 'red',
    '<b>Credential theft</b> is the compromise of passwords, access keys, tokens or session cookies — through leaks in code, phishing, password reuse or malware — allowing an attacker to use legitimate cloud APIs and consoles with the victim’s permissions, often without triggering traditional security tools.',
    'Someone copying your house key: the lock works perfectly — for them too.',
    'The TiffinGo story: an admin access key in a public repo led to crypto-mining within an hour (animation above).',
    'Defences: MFA everywhere, no long-lived keys (roles, OIDC, managed identities), secrets managers, credential scanning (GitHub secret scanning), anomaly detection (GuardDuty, Defender, SCC), conditional access.', 'Identity is covered in 9.4.', A2,
    'always — identity is the cloud perimeter.',
    'root/owner accounts are used daily or keys never expire.',
    'Someone stealing a password or key and logging in as you.',
    [('MFA', 'On every human account.'), ('No static keys', 'Roles, OIDC, managed identities.'), ('Scan', 'Repos for secrets.'), ('Detect', 'Unusual locations/APIs.'), ('Rotate', 'And expire credentials.')],
    [('access key', 'a long-lived API credential (ID + secret)'), ('phishing', 'tricking someone into giving credentials'), ('session token', 'short-lived proof of login')],
    table(['', 'Long-lived key', 'Temporary credentials'], [['Lifetime', 'until deleted', 'minutes–hours'], ['Leak impact', 'high', 'limited'], ['Source', 'IAM user', 'role, OIDC, SSO']], minw=440),
    ['Developer laptops', 'CI pipelines', 'Admin accounts'],
    'GitHub, GitLab and cloud providers run secret-scanning partnerships: providers are notified when their key formats appear in public repos — but attackers scan too, often faster.',
    'First 15 minutes after a leak: deactivate (not just delete) the key, check CloudTrail for what it did, look for new users/keys/roles the attacker created.')

A3 = mk(['Public API', 'Weak checks', 'Data pulled'], ['API|/orders/{id}|internet', 'flaw|no auth on object|no rate limit', 'abuse|enumerate IDs|scrape all'], ['violet', 'red', 'red'],
        ['an application exposes an API to the internet', 'it misses an authorisation check or rate limit', 'attackers change IDs and download other customers’ data'],
        [('Expose', 'An API is reachable from the internet.', ''), ('Flaw', 'Missing object-level authorisation or rate limits.', ''), ('Abuse', 'Attackers enumerate IDs and pull data.', '')],
        'Insecure APIs in action', 'Change one number, see someone else’s order.', 'Insecure APIs', 'Animation: public API; weak checks; data pulled.', 't3anim')
T3 = vt(3, 'Insecure interfaces and APIs', 'violet',
    '<b>Insecure APIs</b> are application or management interfaces with weaknesses such as broken authentication, missing object-level authorisation, excessive data exposure, lack of rate limiting or injection flaws, allowing attackers to access or manipulate data and functions they should not.',
    'A delivery counter where anyone who says any order number gets handed that bag — no ID checked.',
    'A TiffinGo test showed /api/orders/1043 returned order 1043 to any logged-in user; changing the number revealed other customers’ addresses. Fixed by checking order ownership.',
    'Defences: API gateways (API Gateway, API Management, Apigee) with auth and throttling, WAFs, OWASP API Security Top 10 testing, schema validation.', '', A3,
    'any service exposes APIs — which is nearly every cloud app.',
    'you trust the client app to hide IDs — attackers call APIs directly.',
    'Weak web interfaces that let attackers see or change data they shouldn’t.',
    [('Authenticate', 'Every call.'), ('Authorise', 'Per object, per user.'), ('Limit', 'Rate limits, quotas.'), ('Validate', 'Input schemas.'), ('Monitor', 'Abnormal patterns.')],
    [('BOLA', 'broken object-level authorisation — the top OWASP API risk'), ('rate limiting', 'capping requests per client'), ('WAF', 'web application firewall')],
    table(['', 'API gateway', 'WAF'], [['Main job', 'auth, throttling, routing', 'block malicious request patterns'], ['Stops BOLA?', 'only with proper authorisers', 'rarely'], ['Example', 'API Gateway, APIM, Apigee', 'AWS WAF, Azure WAF, Cloud Armor']], minw=440),
    ['Mobile backends', 'Partner integrations', 'Microservices'],
    'Broken object-level authorisation has topped the OWASP API Security Top 10 in both the 2019 and 2023 editions.',
    'Test APIs as an attacker: call them with another user’s token and IDs — most BOLA bugs are found in minutes this way.')

A4 = mk(['Known flaw', 'Exposed workload', 'Exploited'], ['CVE|in library|or OS', 'workload|VM, container|not patched', 'exploit|remote code|attacker inside'], ['amber', 'amber', 'red'],
        ['a vulnerability is published in software you use', 'your VM, container image or dependency still has it', 'attackers exploit it to run their code inside'],
        [('Flaw', 'A CVE is published for software you use.', ''), ('Exposed', 'Your workload still runs the vulnerable version.', ''), ('Exploit', 'Attackers run code inside your environment.', '')],
        'Vulnerable workloads in action', 'Old software, new attackers.', 'Vulnerable workloads', 'Animation: known flaw; exposed workload; exploited.', 't4anim')
T4 = vt(4, 'Vulnerable workloads and supply chain', 'amber',
    '<b>Vulnerable workloads</b> are VMs, containers, functions or applications running software with known flaws — unpatched operating systems, outdated libraries, malicious or compromised dependencies (supply-chain attacks) — that attackers exploit to execute code, steal credentials (for example from the instance metadata service) or move laterally.',
    'A building with a lock model known to be pickable: until you change the lock, every burglar who reads the news can open it.',
    'An old image library in TiffinGo’s menu service had a remote-code-execution CVE; the container ran with a broad IAM role, so the risk was the whole account — fixed by patching and shrinking the role.',
    'Defences: Amazon Inspector, Defender for Cloud (servers, containers), Artifact Analysis / SCC; patch managers; dependency scanning (Dependabot); SBOMs; IMDSv2.', '', A4,
    'continuously — new CVEs appear daily.',
    'images are built once and never rebuilt.',
    'Programs with known security holes that haven’t been updated, which attackers use to get in.',
    [('Inventory', 'Know what runs where (SBOM).'), ('Scan', 'Images, hosts, dependencies.'), ('Prioritise', 'Exposed + exploited first.'), ('Patch', 'Rebuild images often.'), ('Limit', 'Least privilege, IMDSv2.')],
    [('CVE', 'public ID for a known vulnerability'), ('SBOM', 'software bill of materials — list of components'), ('supply-chain attack', 'compromising a library or tool many people use')],
    table(['', 'Patch in place', 'Rebuild image'], [['Speed', 'fast for one VM', 'fast for many (pipeline)'], ['Drift', 'yes', 'none'], ['Fits', 'pets (legacy VMs)', 'cattle (containers, ASGs)']], minw=440),
    ['Web servers', 'Container platforms', 'Third-party libraries'],
    'Log4Shell (CVE-2021-44228) in 2021 showed how one library flaw can affect millions of applications across every cloud at once.',
    'Vulnerability + exposure + permissions = risk. A critical CVE on an internal VM with no role is lower priority than a medium one on an internet-facing VM with admin rights.')

A5 = mk(['Normal traffic', 'Flood arrives', 'Absorbed'], ['users|1,000 req/s|healthy', 'flood|1M req/s|botnet', 'shield|edge absorbs|app stays up'], ['green', 'red', 'blue'],
        ['the app serves normal traffic', 'a botnet sends overwhelming traffic', 'edge protection and scaling absorb or filter it'],
        [('Normal', 'Normal user traffic.', ''), ('Flood', 'A botnet sends huge volumes of traffic.', ''), ('Absorb', 'Edge DDoS protection and scaling keep the app up.', '')],
        'DDoS in action', 'Too much traffic, on purpose.', 'DDoS', 'Animation: normal traffic; flood arrives; edge absorbs it.', 't5anim')
T5 = vt(5, 'Distributed denial of service (DDoS)', 'violet',
    'A <b>DDoS attack</b> floods an application or network with traffic from many sources (often botnets) to exhaust bandwidth, connections or compute so legitimate users cannot be served; attacks target network layers (L3/L4 floods) or application layers (L7 HTTP floods).',
    'Hundreds of fake customers crowding a shop’s entrance so real customers cannot get in.',
    'During a Diwali sale a competitor’s botnet sent HTTP floods at TiffinGo’s order page; CloudFront and AWS Shield Standard absorbed the network flood and a WAF rate-limit rule blocked the HTTP flood.',
    'AWS Shield Standard (free) and Advanced, WAF, CloudFront; Azure DDoS Protection (network) and IP protection, Front Door + WAF; Google Cloud Armor, Cloud CDN.', '', A5,
    'any public-facing app — use edge services and rate limits.',
    'you expose origins directly with public IPs — attackers bypass the CDN.',
    'Attackers sending massive fake traffic to make a website too busy to work.',
    [('Edge', 'Serve via CDN/LB with built-in protection.'), ('Filter', 'WAF and rate limits.'), ('Scale', 'Auto scaling absorbs bursts.'), ('Hide origin', 'Only accept traffic from the edge.'), ('Plan', 'Response contacts, runbook.')],
    [('botnet', 'many infected devices controlled by an attacker'), ('L7', 'application layer (HTTP)'), ('origin', 'your real servers behind the CDN')],
    table(['', 'Network DDoS (L3/4)', 'Application DDoS (L7)'], [['Looks like', 'packet floods', 'valid-looking HTTP requests'], ['Defence', 'provider edge (Shield, DDoS Protection)', 'WAF rules, rate limits, caching'], ['Cost risk', 'low on edge', 'scaling costs if not filtered']], minw=460),
    ['E-commerce', 'Gaming', 'Public services'],
    'Cloud providers have publicly reported mitigating record HTTP floods of hundreds of millions of requests per second using global edge capacity.',
    'Auto scaling without WAF turns a DDoS into a billing attack (“economic denial of service”) — filter before you scale.')

A6 = mk(['Attacker gets in', 'Deletes backups', 'Encrypts / extorts'], ['access|via 1, 2 or 4|admin rights', 'sabotage|backups, snapshots|logs off', 'extort|data encrypted|or leaked'], ['red', 'red', 'amber'],
        ['ransomware starts after another threat gives access', 'attackers delete backups and disable logging first', 'then encrypt or steal data and demand payment'],
        [('Access', 'Entry via credentials, misconfiguration or a vulnerability.', ''), ('Sabotage', 'Backups and logs are deleted first.', ''), ('Extort', 'Data is encrypted or leaked for ransom.', '')],
        'Ransomware in action', 'Backups are the first target.', 'Ransomware', 'Animation: attacker gets in; deletes backups; encrypts and extorts.', 't6anim')
T6 = vt(6, 'Ransomware and data destruction', 'red',
    '<b>Cloud ransomware</b> is an attack in which, after gaining access, attackers encrypt, delete or exfiltrate data — storage objects, disks, snapshots, databases — and demand payment, often first deleting backups and disabling logging so recovery and investigation are harder.',
    'A thief who first steals your spare keys and then changes all your locks, asking money for the new keys.',
    'In a tabletop exercise, TiffinGo found that its backups lived in the same account with the same admin role — one stolen key could delete both. They moved backups to a separate, locked vault.',
    'Defences: immutable backups (AWS Backup Vault Lock, Azure immutable vaults, Google Backup and DR immutability / bucket retention lock), object versioning + Object Lock, separate backup accounts, least privilege, MFA delete.', 'Backups were introduced in Lesson 6.2.', A6,
    'every account that holds important data.',
    'backups are reachable by the same credentials that production uses.',
    'Attackers locking or deleting your data and asking for money to give it back.',
    [('Isolate backups', 'Separate account/subscription.'), ('Immutable', 'Vault/Object Lock.'), ('Least privilege', 'Few can delete.'), ('Detect', 'Mass delete/encrypt alerts.'), ('Test restore', 'Regularly.')],
    [('immutable', 'cannot be changed or deleted until a set time'), ('exfiltration', 'copying data out to the attacker'), ('double extortion', 'encrypt and threaten to leak')],
    table(['', 'Normal backup', 'Immutable, isolated backup'], [['Deletable by attacker with admin key', 'yes', 'no'], ['Cost', 'base', 'slightly higher'], ['Recovery confidence', 'low', 'high']], minw=440),
    ['Databases', 'File shares', 'Object storage'],
    'Attackers in cloud ransomware cases have used legitimate features — such as encrypting objects with keys they control — so it looks like normal API activity until the data is unreadable.',
    'The test that matters: “Could our most powerful compromised credential delete our backups?” If yes, fix that before anything else.')

A7 = mk(['Trusted person', 'Misuses access', 'Damage'], ['insider|employee, contractor|ex-staff', 'misuse|copy data|change settings', 'impact|leak, sabotage|fraud'], ['blue', 'amber', 'red'],
        ['someone with legitimate access', 'uses it maliciously or carelessly', 'data leaks, sabotage or fraud follow'],
        [('Trusted', 'An employee, contractor or ex-employee with access.', ''), ('Misuse', 'Copies data or changes settings, deliberately or by mistake.', ''), ('Impact', 'Leaks, sabotage or fraud.', '')],
        'Insider threats in action', 'Trusted access, misused.', 'Insider', 'Animation: trusted person; misuses access; damage.', 't7anim')
T7 = vt(7, 'Insider threats', 'blue',
    '<b>Insider threats</b> come from people with legitimate access — employees, contractors, partners or former staff whose access was not removed — who misuse it maliciously (theft, sabotage) or negligently (mistakes, poor hygiene), and are hard to detect because their actions use valid credentials.',
    'A staff member with keys to the store room walking out with stock — or simply leaving the door open by mistake.',
    'A contractor who left TiffinGo still had a working console login three months later; the access review found it before any misuse.',
    'Defences: least privilege, SSO with automatic de-provisioning, access reviews (IAM Access Analyzer unused access, Entra access reviews, IAM recommender), separation of duties, audit logs, DLP.', '', A7,
    'always — and especially for admins and departing staff.',
    'shared admin accounts are used — nobody can tell who did what.',
    'People inside the company misusing their access, on purpose or by mistake.',
    [('Least privilege', 'Only what the role needs.'), ('SSO', 'Leaver disabled once, everywhere.'), ('Reviews', 'Quarterly access reviews.'), ('Separation', 'No single person can do everything.'), ('Audit', 'Logs + alerts on sensitive actions.')],
    [('de-provisioning', 'removing access when someone leaves'), ('separation of duties', 'splitting critical tasks between people'), ('access review', 'periodic check of who has what')],
    table(['', 'Malicious insider', 'Negligent insider'], [['Intent', 'harm or profit', 'none (mistake)'], ['Frequency', 'less common', 'more common'], ['Best control', 'least privilege + monitoring', 'guard-rails + training']], minw=440),
    ['Admins', 'Contractors', 'Departing employees'],
    'Leaver accounts that stay active are a recurring audit finding; SSO with automated de-provisioning from the HR system is the standard fix.',
    'Use break-glass admin accounts with alerts on every use, and give day-to-day admins time-bound elevation (PIM, temporary access).')

SUMMARY = table(['#', 'Threat', 'Typical entry', 'Key defence', 'Detect with'], [
    ['1', 'Misconfiguration', 'public storage, open ports', 'org policies, IaC scanning', 'CSPM (Security Hub, Defender, SCC)'], ['2', 'Credential theft', 'leaked keys, phishing', 'MFA, no static keys', 'GuardDuty, Defender, SCC'],
    ['3', 'Insecure APIs', 'missing authz, no limits', 'gateway + authz checks', 'WAF logs, API analytics'], ['4', 'Vulnerable workloads', 'unpatched CVEs', 'scan + rebuild', 'Inspector, Defender, Artifact Analysis'],
    ['5', 'DDoS', 'traffic floods', 'edge protection, WAF', 'Shield, DDoS Protection, Cloud Armor'], ['6', 'Ransomware', 'after 1, 2 or 4', 'immutable isolated backups', 'mass delete/encrypt alerts'], ['7', 'Insiders', 'valid access', 'least privilege, reviews', 'audit logs, access analyzers']], minw=660)
CHECK = ('  <h3>Check yourself: which threat?</h3>\n' +
    qx('A. Bot traffic overwhelms the login page.', ['DDoS', 'Insider', 'Misconfiguration', 'Ransomware'], 0, 'Flood.') +
    qx('B. Access key found in a public repo, used to launch miners.', ['Credential theft', 'DDoS', 'Insecure API', 'Insider'], 0, 'Leaked credential.') +
    qx('C. Changing an order ID in the URL shows another customer’s order.', ['Insecure API', 'DDoS', 'Ransomware', 'Misconfiguration of DNS'], 0, 'BOLA.') +
    qx('D. Former contractor still has console access.', ['Insider threat', 'DDoS', 'Supply chain', 'Ransomware'], 0, 'Leaver access.'))

TYPES = ('  <p>Seven threats, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['Why do attackers delete backups before encrypting data?', 'Why can auto scaling make a DDoS expensive?', 'What should you check after deactivating a leaked key?'], 'types 6, 5 and 2') + MAP
         + jump(['Misconfig', 'Credentials', 'APIs', 'Workloads', 'DDoS', 'Ransomware', 'Insiders']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('Threat detection service', 'Analyses logs and network flows for attacks.', 'Finds stolen keys, mining, malicious IPs.', 'GuardDuty, Defender for Cloud, SCC.'),
    ('Posture management (CSPM)', 'Checks settings against best practice.', 'Catches misconfiguration.', 'Security Hub CSPM, Defender CSPM, SCC.'),
    ('Vulnerability scanning', 'Finds CVEs in hosts and images.', 'Patch the right things first.', 'Inspector, Defender, Artifact Analysis.'),
    ('Edge protection', 'CDN, WAF, DDoS protection.', 'Stops floods and web attacks early.', 'Shield/WAF, Front Door/WAF, Cloud Armor.'),
    ('Immutable backups', 'Backups that cannot be deleted.', 'Ransomware recovery.', 'Backup Vault Lock, immutable vaults.'),
    ('Incident runbooks', 'Pre-written response steps.', 'Fast, calm containment.', 'Leaked key, public bucket, mining.')])

DEEP = ('  <h3>MITRE ATT&amp;CK for cloud</h3>\n  <p>MITRE’s ATT&amp;CK framework has cloud matrices (IaaS, SaaS, identity providers) describing attacker techniques: initial access with valid accounts, discovery via cloud APIs, persistence by creating new keys or roles, defence evasion by disabling logging, impact through resource hijacking (mining) or data destruction. Detection tools map their findings to these techniques.</p>\n'
    '  <h3>Leaked-key runbook (first 15 minutes)</h3>\n  <ol><li><b>Deactivate</b> the key (keep it for investigation; delete later).</li><li><b>Scope:</b> search audit logs by key ID for every action since the leak.</li><li><b>Persistence:</b> look for new users, keys, roles, policies, Lambda functions, instances in all Regions.</li><li><b>Contain:</b> stop rogue resources (snapshot first for evidence), block IPs.</li><li><b>Data:</b> check data access logs; involve legal if personal data was accessed (India’s DPDP Act requires breach notification to the Data Protection Board and affected people).</li><li><b>Prevent:</b> remove static keys, add secret scanning, cost-anomaly alarms, SCPs blocking unused Regions.</li></ol>\n'
    '  <h3>Defence in depth</h3>\n  <p>No single control stops everything. Layer them: identity (MFA, least privilege) → network (private endpoints, WAF) → workload (patched, minimal images) → data (encryption, immutable backups) → detection (threat detection, posture, cost anomalies) → response (runbooks, automation).</p>')

clouds = vendor_tabs('<p><b>AWS:</b> GuardDuty (threat detection), Security Hub CSPM (posture), Inspector (vulnerabilities), Detective (investigation), Shield and WAF (DDoS/web), Macie (sensitive data), AWS Backup Vault Lock, Cost Anomaly Detection.</p>',
    '<p><b>Azure:</b> Microsoft Defender for Cloud (CSPM + workload protection), Microsoft Sentinel (SIEM/SOAR), Azure DDoS Protection, WAF on Front Door/Application Gateway, immutable Backup vaults, Entra ID Protection, Cost Management anomaly alerts.</p>',
    '<p><b>Google Cloud:</b> Security Command Center (posture, threat detection in higher tiers), Google Security Operations (SIEM/SOAR), Cloud Armor (DDoS/WAF), Artifact Analysis, Backup and DR immutability, cost anomaly detection in Billing.</p>') + \
    cloud3([['Threat detection', 'GuardDuty', 'Defender for Cloud', 'Security Command Center'], ['SIEM / SOAR', 'Security Lake + partners', 'Microsoft Sentinel', 'Google Security Operations'], ['DDoS / WAF', 'Shield, WAF', 'DDoS Protection, WAF', 'Cloud Armor'], ['Vulnerabilities', 'Inspector', 'Defender for Servers/Containers', 'Artifact Analysis, SCC'], ['Immutable backup', 'Backup Vault Lock', 'Immutable vaults', 'Backup and DR immutability']])

MOCKQ.extend([
 (mock('aws', ['GuardDuty', 'Settings'], ['Summary', 'Findings', 'Protection plans', 'Settings'], 'Settings', [('GuardDuty', 'Enabled · 30-day free trial'), ('Sample findings', 'Generate sample findings')], 'Generate sample findings'),
  mock('az', ['Microsoft Defender for Cloud', 'Security alerts'], ['Overview', 'Recommendations', 'Security alerts', 'Environment settings'], 'Security alerts', [('Plan', 'Defender for Servers · trial'), ('Sample alerts', 'Create sample alerts')], 'Create sample alerts'),
  mock('gcp', ['Security', 'Security Command Center', 'Findings'], ['Overview', 'Findings', 'Vulnerabilities', 'Settings'], 'Findings', [('Tier', 'Standard (project)'), ('Example', 'Public bucket · Open firewall · MFA not enforced')], 'Filter')),
 (mock('aws', ['IAM', 'Credential report'], ['Users', 'Roles', 'Credential report', 'Access Analyzer'], 'Credential report', [('access_key_1_last_rotated', 'per user'), ('mfa_active', 'true / false')], 'Download credentials report'),
  mock('az', ['Microsoft Entra ID', 'App registrations', 'Certificates & secrets'], ['Overview', 'Certificates & secrets', 'Owners'], 'Certificates & secrets', [('Client secrets', 'Expires · e.g. 2027-05-10'), ('Federated credentials', 'preferred (no secret)')], 'New client secret'),
  mock('gcp', ['IAM & Admin', 'Service accounts', 'Keys'], ['Service accounts', 'Keys', 'Permissions'], 'Keys', [('User-managed keys', 'Created · Expires'), ('Org policy', 'iam.disableServiceAccountKeyCreation')], 'Add key')),
 (mock('aws', ['Billing and Cost Management', 'Cost Anomaly Detection'], ['Cost Explorer', 'Budgets', 'Cost Anomaly Detection'], 'Cost Anomaly Detection', [('Monitor', 'AWS services · tiffingo-spend'), ('Alert subscription', 'Immediate · impact ≥ $10 · email')], 'Create monitor'),
  mock('az', ['Cost Management', 'Cost alerts', 'Anomaly alert'], ['Cost analysis', 'Cost alerts', 'Budgets'], 'Cost alerts', [('Alert type', 'Anomaly'), ('Recipients', 'you@example.com')], 'Create'),
  mock('gcp', ['Billing', 'Budgets & alerts'], ['Overview', 'Reports', 'Budgets & alerts', 'Anomalies'], 'Budgets & alerts', [('Budget', '₹2,000 / month'), ('Thresholds', '50% · 90% · 100% · email + Pub/Sub')], 'Finish')),
])

STEP1 = ('1 · Turn on threat detection and see sample attacks', tri(
    (['[[GuardDuty]] → [[Get started]] → [[Enable GuardDuty]] (30-day free trial in each Region).', '[[Settings]] → [[Generate sample findings]] → [[Findings]]: open “UnauthorizedAccess:IAMUser/MaliciousIPCaller” or “CryptoCurrency:EC2/BitcoinTool.B!DNS”.'],
     "DET=$(aws guardduty create-detector --enable --finding-publishing-frequency FIFTEEN_MINUTES --query DetectorId --output text)\naws guardduty create-sample-findings --detector-id $DET\nsleep 20; aws guardduty list-findings --detector-id $DET --max-results 50 --query 'length(FindingIds)'\nID=$(aws guardduty list-findings --detector-id $DET --max-results 1 --query 'FindingIds[0]' --output text)\naws guardduty get-findings --detector-id $DET --finding-ids $ID --query 'Findings[0].[Type,Severity,Title]' --output text",
     'a few hundred sample findings and one example such as <code>Recon:IAMUser/MaliciousIPCaller  5.0  API … was invoked from a known malicious IP</code> (titles prefixed “[SAMPLE]”). Disable after the trial if you do not want charges.'),
    (['[[Microsoft Defender for Cloud]] → [[Environment settings]] → subscription → turn on [[Servers]] plan (30-day trial) → [[Security alerts]] → [[Sample alerts]] → [[Create sample alerts]].', 'Open an alert: description, affected resource, MITRE ATT&amp;CK tactic, remediation steps.'],
     'az security pricing create -n VirtualMachines --tier standard\naz security pricing show -n VirtualMachines --query "{plan:name,tier:pricingTier,trial:freeTrialRemainingTime}"\n# create sample alerts from the portal (Security alerts → Sample alerts), then:\naz security alert list --query "[].{name:alertDisplayName,severity:severity}" -o table | head',
     'tier <code>Standard</code> with trial time remaining, then sample alerts such as “[Sample alert] Suspicious process executed”. Set the plan back to Free after the lab: <code>az security pricing create -n VirtualMachines --tier free</code>.'),
    (['Search [[Security Command Center]] → activate the [[Standard]] tier for your project (free) → [[Findings]]. Standard detectors flag misconfigurations such as public buckets and open firewalls; threat detection (Event Threat Detection) needs Premium.'],
     'P=$(gcloud config get-value project)\ngcloud services enable securitycenter.googleapis.com\ngcloud scc findings list projects/$P --location=global --filter="state=\\"ACTIVE\\"" --format="table(finding.category,finding.severity,finding.resourceName)" | head',
     'active findings such as <code>OPEN_FIREWALL</code> or <code>PUBLIC_BUCKET_ACL</code> (empty on a clean new project; findings appear after the first scan).')),
    'Detection turns “found on Monday” into “paged at 2:05 am”.')

STEP2 = ('2 · Hunt for old and risky credentials', tri(
    (['[[IAM]] → [[Credential report]] → [[Download credentials report]]: check <code>mfa_active</code>, <code>access_key_1_last_rotated</code> and <code>access_key_1_last_used_date</code> for every user.', 'Deactivate keys older than 90 days or never used; prefer roles and IAM Identity Center.'],
     "aws iam generate-credential-report >/dev/null; sleep 5\naws iam get-credential-report --query Content --output text | base64 -d | cut -d, -f1,4,8,9,10,11 | head",
     'a table of users with password/MFA status and key rotation dates. Any key older than 90 days, or a root key (<code>&lt;root_account&gt;</code> with key active = true), is a finding to fix today.'),
    (['[[Microsoft Entra ID]] → [[App registrations]] → each app → [[Certificates &amp; secrets]]: check client secret expiry; switch to [[Federated credentials]] (Lesson 8.3) where possible.', '[[Users]] → [[Per-user MFA]] / Conditional Access: confirm MFA for all admins.'],
     'for id in $(az ad app list --show-mine --query "[].appId" -o tsv); do\n  az ad app credential list --id $id --query "[].{app:\'$id\',name:displayName,ends:endDateTime}" -o tsv\ndone',
     'each secret with its expiry date (empty if your apps use only federated credentials — the best case).'),
    (['[[IAM &amp; Admin]] → [[Service accounts]] → each account → [[Keys]]: user-managed JSON keys are long-lived — delete unused ones; use Workload Identity Federation instead.', 'With an organisation, enforce <code>iam.disableServiceAccountKeyCreation</code>.'],
     'for sa in $(gcloud iam service-accounts list --format="value(email)"); do\n  gcloud iam service-accounts keys list --iam-account=$sa --managed-by=user --format="table[no-heading](name.basename(),validAfterTime,validBeforeTime)" | sed "s|^|$sa  |"\ndone',
     'one line per user-managed key with creation date — ideally none.')),
    'Long-lived credentials are the attacker’s favourite door; each one you delete closes it.')

STEP3 = ('3 · Add a cost-anomaly alarm (cryptojacking early warning)', tri(
    (['[[Billing and Cost Management]] → [[Cost Anomaly Detection]] → [[Create monitor]] → [[AWS services]] → alert subscription: [[Immediate]], threshold $10, your email.'],
     "MON=$(aws ce create-anomaly-monitor --anomaly-monitor '{\"MonitorName\":\"tiffingo-spend\",\"MonitorType\":\"DIMENSIONAL\",\"MonitorDimension\":\"SERVICE\"}' --query MonitorArn --output text)\naws ce create-anomaly-subscription --anomaly-subscription \"{\\\"SubscriptionName\\\":\\\"spend-spike\\\",\\\"MonitorArnList\\\":[\\\"$MON\\\"],\\\"Subscribers\\\":[{\\\"Type\\\":\\\"EMAIL\\\",\\\"Address\\\":\\\"you@example.com\\\"}],\\\"Frequency\\\":\\\"DAILY\\\",\\\"ThresholdExpression\\\":{\\\"Dimensions\\\":{\\\"Key\\\":\\\"ANOMALY_TOTAL_IMPACT_ABSOLUTE\\\",\\\"Values\\\":[\\\"10\\\"],\\\"MatchOptions\\\":[\\\"GREATER_THAN_OR_EQUAL\\\"]}}}\"\naws ce get-anomaly-monitors --query 'AnomalyMonitors[].[MonitorName,MonitorType]' --output text",
     '<code>tiffingo-spend DIMENSIONAL</code>. Cost Anomaly Detection is free; it learns your normal spend and emails when a service suddenly costs more (immediate alerts need an SNS subscriber).'),
    (['[[Cost Management]] → [[Cost alerts]] → [[Add]] → [[Anomaly alert]] → recipients → [[Create]]. Azure also shows detected anomalies in Cost analysis (smart views).'],
     'SUB=$(az account show --query id -o tsv)\naz rest --method get --url "https://management.azure.com/subscriptions/$SUB/providers/Microsoft.CostManagement/scheduledActions?api-version=2023-11-01" --query "value[].{name:name,kind:kind}" -o table',
     'your anomaly alert listed with kind <code>InsightAlert</code> after you create it in the portal.'),
    (['[[Billing]] → [[Budgets &amp; alerts]] → [[Create budget]] (e.g. ₹2,000/month) with 50/90/100% thresholds; [[Anomalies]] (if shown for your billing account) lists unusual spend automatically.'],
     'BA=$(gcloud billing projects describe $(gcloud config get-value project) --format="value(billingAccountName)" | cut -d/ -f2)\ngcloud billing budgets create --billing-account=$BA --display-name=spend-guard --budget-amount=2000INR \\\n  --threshold-rule=percent=0.5 --threshold-rule=percent=0.9 --threshold-rule=percent=1.0\ngcloud billing budgets list --billing-account=$BA --format="table(displayName,amount.specifiedAmount.units)"',
     'the budget <code>spend-guard 2000</code>; alerts go to billing admins by email. (Use the currency of your billing account.)')),
    'Cryptojacking almost always shows up on the bill first — make the bill page you.')

prac = practical(OWN_INTRO + ' You switch on attack detection (with sample findings, no real attack needed), hunt risky credentials, and add a cost alarm. GuardDuty and Defender plans use free trials — turn them off afterwards if you do not want charges.', [SETUP_STEP, STEP1, STEP2, STEP3],
    cleanup='<b>AWS:</b> <code>aws guardduty delete-detector --detector-id $DET</code> (or keep it on — recommended for real accounts); keep the anomaly monitor (free). '
            '<b>Azure:</b> <code>az security pricing create -n VirtualMachines --tier free</code>; dismiss sample alerts. '
            '<b>Google Cloud:</b> keep the budget; SCC Standard is free.')

mist = mistakes([
    ['Deleting a leaked key file from Git and moving on.', 'Git history keeps it.', 'Deactivate the key immediately, then investigate.'],
    ['No one reads security emails.', 'Alerts go to a personal inbox.', 'Route findings to an on-call channel.'],
    ['Backups in the same account with the same admin.', 'Convenience.', 'Separate, immutable backup vaults.'],
    ['Auto scaling without WAF.', 'Scaling seen as protection.', 'Filter at the edge, then scale.'],
    ['Ignoring unused Regions.', '“We only use Mumbai.”', 'Block unused Regions; detection in all Regions.'],
    ['Shared admin accounts.', 'Simplicity.', 'Individual identities, SSO, audit trails.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Cloud security issues and threats.'], ['AWS CLF-C02', 'GuardDuty, Inspector, Shield, WAF, Security Hub, Macie, Detective; DDoS protection; leaked-credential response.'], ['AZ-900', 'Defender for Cloud, DDoS Protection, Zero Trust, defence in depth.'], ['Google Cloud Digital Leader', 'Security Command Center, Cloud Armor, threats and defence in depth.']], minw=560) + \
    qx('1. Which AWS service detects threats such as API calls from malicious IPs?', ['GuardDuty', 'Inspector', 'Artifact', 'Config'], 0, 'GuardDuty.') + \
    qx('2. Which AWS service provides free baseline DDoS protection?', ['Shield Standard', 'Macie', 'Inspector', 'KMS'], 0, 'Shield Standard.') + \
    qx('3. Which service scans EC2 and container images for vulnerabilities?', ['Amazon Inspector', 'AWS Shield', 'Amazon Detective', 'AWS Artifact'], 0, 'Inspector.') + \
    qx('4. Layering identity, network, workload, data and detection controls is called…', ['defence in depth', 'shared fate', 'elasticity', 'multi-tenancy'], 0, 'Defence in depth.') + \
    qx('5. Google Cloud’s DDoS and WAF service is…', ['Cloud Armor', 'Cloud NAT', 'Cloud Run', 'Cloud CDN only'], 0, 'Cloud Armor.') + \
    qx('6. Best first action when an access key leaks?', ['delete the GitHub repo', 'deactivate the key and review its activity', 'wait for the bill', 'change the region'], 1, 'Contain, then scope.')

proj = miniproject('Mini project: TiffinGo threat model',
    'Build a threat model and response plan for the order platform.',
    ['<b>Assets:</b> list what matters (customer data, payment tokens, compute budget).',
     '<b>Threats:</b> for each of the seven threats, one realistic TiffinGo scenario.',
     '<b>Controls:</b> one preventive and one detective control per threat (your cloud).',
     '<b>Runbooks:</b> write the leaked-key and public-bucket runbooks (deep dive).',
     '<b>Backups:</b> design isolated, immutable backups for the orders database.',
     '<b>Drill:</b> do practical steps 1–3 and screenshot one sample finding with your response.'],
    'A threat model table, two runbooks and evidence from the lab.', '9.1 + 9.2 + 8.1.')

assemble_v2(HERE, story_h2='₹2.4 lakh by Monday morning', hook_html=hk,
    narration='A developer pushed code containing an access key to a public repository and deleted it ten minutes later. By Monday, attackers had run dozens of GPU servers in an unused Region and TiffinGo’s bill had exploded.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Cloud security issues and threats',
    formal='<b>Cloud security threats</b> are potential events or actions that could compromise the confidentiality, integrity or availability of cloud resources and data — chiefly misconfiguration, compromised credentials and identities, insecure interfaces and APIs, vulnerable workloads and supply chains, denial-of-service attacks, ransomware and data destruction, and insider misuse — addressed through layered preventive, detective and responsive controls.',
    simple='The main ways cloud systems get attacked — mostly careless settings and stolen logins — and how to spot and stop them.',
    interview=['“Most cloud incidents come from misconfiguration and stolen credentials, not provider breaches. I prevent with MFA, no static keys, org policies and immutable backups; detect with GuardDuty/Defender/SCC, posture tools and cost anomalies; and respond with runbooks.”', '“For a leaked key: deactivate it, scope its activity in CloudTrail, remove persistence, contain resources, then fix the root cause.”'],
    terms_rows=[('Misconfiguration', 'Insecure setting.'), ('Credential theft', 'Stolen keys/passwords.'), ('BOLA', 'Broken object-level authorisation.'), ('CVE', 'Known vulnerability ID.'), ('DDoS', 'Traffic flood.'), ('Ransomware', 'Encrypt/delete for money.'), ('Insider threat', 'Misuse of valid access.'), ('Defence in depth', 'Layered controls.')],
    exam='CLF-C02 maps threats to services: GuardDuty (threats), Inspector (vulnerabilities), Shield/WAF (DDoS/web), Macie (sensitive data), Security Hub (posture), Detective (investigation).',
    picture_h2='Where attacks enter', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven cloud threats, one by one', TYPES)],
    how_h2='Anatomy of a cloud attack, and the response', how_intro='From leaked key to containment, step by step.', how_anim=ATTACK,
    parts_h2='Six defences every account needs', parts_html=parts, lv='',
    myth_rows=[('Hackers break the provider’s security.', 'They mostly log in with stolen or leaked credentials.', 'Type 2.'), ('Deleting the file removes a leaked secret.', 'Git history and scanners already have it.', 'Runbook.'), ('Backups protect against ransomware.', 'Only if attackers can’t delete them.', 'Type 6.')],
    extra_secs=[('deep', 'Deep dive', 'MITRE ATT&CK, leaked-key runbook, defence in depth', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Explain seven cloud threats and their typical entry points.', 'Trace a cloud attack from leaked key to recovery.', 'Map threats to AWS, Azure and Google security services.', 'Enable threat detection, audit credentials and set cost-anomaly alarms on your own account.', 'Write a first-15-minutes incident runbook.'],
    next_html='<a href="../03-privacy-and-compliance-in-the-cloud/">9.3 Privacy and compliance in the cloud</a>.',
    pre='<b>Before you start:</b> 9.1 (shared responsibility) and 8.1 (monitoring).')
