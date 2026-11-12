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


hk = hook('TiffinGo’s reporting job needs to read one folder of one bucket. Today it runs with an admin access key that never expires. If that key leaks, what can an attacker do — and even if they copy the files, could encryption still save the data?',
    'With an admin key: everything. With a <b>role</b> that can only read that folder: almost nothing. And if the data is encrypted with a <b>key you control</b>, disabling that key makes stolen copies unreadable. This lesson covers the seven basics of cloud identity and encryption — <b>identities</b>, <b>authentication & MFA</b>, <b>authorisation policies</b>, <b>federation & SSO</b>, <b>encryption at rest</b>, <b>encryption in transit</b> and <b>key management</b> — animates how one request is checked and decrypted, and on <b>your own</b> account you build a least-privilege identity, encrypt and “shred” data with a managed key, and enforce TLS.',
    ['Explicit deny beats allow — and “no rule” means no.', 'Envelope encryption: why KMS never encrypts your 5 GB file directly.', 'Why roles and managed identities beat access keys.'])

def story_scene():
    o = t(180, 12, 'Same job, two identities', 9, 'ink', bold=True)
    o += box(8, 28, 160, 74, 'red', rx=8) + t(88, 48, 'Admin access key', 8.4, 'ink', bold=True) + t(88, 64, 'never expires', 7, 'ink2') + t(88, 78, 'can do anything', 7, 'ink2') + t(88, 92, 'leak = total loss', 7.4, 'ink', bold=True)
    o += box(192, 28, 160, 74, 'green', rx=8) + t(272, 48, 'Role + least privilege', 8.4, 'ink', bold=True) + t(272, 64, '1-hour credentials', 7, 'ink2') + t(272, 78, 'read reports/ only', 7, 'ink2') + t(272, 92, 'leak = tiny impact', 7.4, 'ink', bold=True)
    o += t(180, 122, 'Plus encryption with a key you can switch off', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Left: an admin access key that never expires can do anything, so a leak is total loss. Right: a role with one-hour credentials that can only read reports, so a leak has tiny impact.', story_scene(), 'Give every identity <tspan font-weight="700" class="s-acc">only what it needs</tspan>.', h=132)
dialogue = '''K> Sir, admin was quicker. Every time I gave fewer permissions, something broke.
A> That pain is temporary; a leaked admin key is permanent damage. Start with what the job really calls, then add only what fails.
R> And encryption? S3 already encrypts everything.
A> Yes, by default. But with our own KMS key, we decide who can decrypt — and we can turn the key off in an emergency.
K> So identity says who may ask, encryption decides who can read.
A> Exactly. Let’s go one by one.'''

def aaafig():
    o = t(320, 16, 'Identity and access in four questions', 11, 'ink', bold=True)
    Q = [('Who are you?', 'identity', 'user, role, service', 'blue'), ('Prove it', 'authentication', 'password + MFA, token', 'violet'), ('What may you do?', 'authorisation', 'policies, roles', 'amber'), ('What did you do?', 'auditing', 'CloudTrail, logs', 'green')]
    for i, (a, b, c, tn) in enumerate(Q):
        x = 14 + i * 154
        o += box(x, 34, 146, 92, tn, rx=8) + t(x + 73, 58, a, 9, 'ink', bold=True) + t(x + 73, 80, b, 7.6, 'ink') + t(x + 73, 100, c, 7, 'ink2')
        if i < 3: o += arrow(x + 146, 80, x + 154, 80)
    o += t(320, 148, 'Identity is the new perimeter: in the cloud, every action is an authenticated, authorised, logged API call.', 7.4, 'ink2')
    return o
AAA = bigfig('Four boxes: who are you (identity), prove it (authentication), what may you do (authorisation), what did you do (auditing).', aaafig(), h=158)

def encfig():
    o = t(320, 16, 'Where data needs encryption', 11, 'ink', bold=True)
    o += box(20, 50, 150, 70, 'violet', rx=10) + t(95, 78, 'User / app', 8.6, 'ink', bold=True) + t(95, 96, 'browser, API client', 7, 'ink2')
    o += arrow(170, 85, 240, 85) + t(205, 76, 'TLS', 8, 'ink', bold=True) + t(205, 104, 'in transit', 7, 'ink2')
    o += box(240, 50, 160, 70, 'blue', rx=10) + t(320, 78, 'Cloud service', 8.6, 'ink', bold=True) + t(320, 96, 'in use (confidential computing)', 6.8, 'ink2')
    o += arrow(400, 85, 470, 85) + t(435, 104, 'storage', 7, 'ink2')
    o += box(470, 50, 150, 70, 'green', rx=10) + t(545, 78, 'Disk / object / DB', 8.6, 'ink', bold=True) + t(545, 96, 'at rest', 7, 'ink2')
    o += box(240, 140, 160, 40, 'amber', rx=8) + t(320, 158, 'KMS / Key Vault / Cloud KMS', 7.8, 'ink', bold=True) + t(320, 172, 'keys, access policy, audit', 6.8, 'ink2')
    o += arrow(400, 160, 520, 122)
    o += t(320, 204, 'Three states of data: in transit, at rest, in use. Keys live separately from the data.', 7.4, 'ink2')
    return o
ENC = bigfig('Data travels from user to cloud service with TLS (in transit), is processed (in use) and stored on disk/object/database (at rest); a key management service holds the keys separately.', encfig(), h=214)

picture = ('  <p>Identity and access answer four questions:</p>\n' + AAA +
           '\n  <p>Encryption protects data in each state:</p>\n' + ENC +
           '\n  <h3>Same ideas, three clouds</h3>\n' + table(['Concept', 'AWS', 'Azure', 'Google Cloud'], [
               ['Directory of people', 'IAM Identity Center (or IAM users)', 'Microsoft Entra ID', 'Cloud Identity / Google Workspace'], ['Workload identity', 'IAM roles (instance profiles, task roles)', 'managed identities', 'service accounts (attached)'],
               ['Permissions', 'IAM policies (JSON)', 'Azure RBAC role assignments', 'IAM roles bound to principals'], ['Keys', 'AWS KMS, CloudHSM', 'Key Vault, Managed HSM', 'Cloud KMS, Cloud HSM, EKM']], minw=620))

RN = {'u': (4, 54, 50, 50, 'user', 'Analyst', 'MFA login'), 'sts': (66, 4, 62, 46, 'shield', 'STS / token', '1-hour creds'), 'call': (66, 104, 62, 46, 'globe', 'API call', 'TLS, signed'),
      'pol': (142, 54, 60, 50, 'gear', 'Policy check', 'deny > allow'), 's3': (216, 4, 62, 46, 'disk', 'Storage', 'encrypted object'), 'kms': (216, 104, 62, 46, 'meter', 'KMS', 'decrypt data key'), 'ok': (292, 54, 64, 50, 'chart', 'Result', 'logged')}
RS = [dict(on=['u', 'sts'], hot='sts', move=(54, 79, 72, 30, 'MFA'), head='Step 1 · Authenticate and get temporary credentials', text='Riya signs in through SSO with MFA and assumes the “report-reader” role; STS', text2='returns credentials valid for one hour.', svc='IAM Identity Center + STS · Entra ID tokens · Google OAuth tokens'),
      dict(on=['sts', 'call'], hot='call', move=(97, 50, 97, 104, 'sign'), head='Step 2 · Make a signed request over TLS', text='The CLI signs “GetObject reports/oct.csv” with the temporary key and sends it over', text2='HTTPS — encrypted in transit, tamper-evident.', svc='SigV4 signatures · bearer tokens · TLS 1.2+'),
      dict(on=['call', 'pol'], hot='pol', move=(128, 127, 150, 90, 'evaluate'), head='Step 3 · Evaluate every applicable policy', text='Explicit deny anywhere? → denied. Otherwise an allow is needed in identity and/or', text2='resource policies (and within any SCP/permission boundary). No allow → implicit deny.', svc='Default = deny; least privilege decides what is allowed'),
      dict(on=['pol', 's3'], hot='s3', move=(202, 66, 226, 30, 'allowed'), head='Step 4 · Storage finds the encrypted object', text='The object is stored encrypted with a data key; the data key itself is stored', text2='encrypted by the KMS key (envelope encryption).', svc='SSE-KMS · storage service encryption with CMK · CMEK'),
      dict(on=['s3', 'kms'], hot='kms', move=(247, 50, 247, 104, 'decrypt?'), head='Step 5 · KMS checks its own key policy', text='KMS decrypts the data key only if Riya’s role may use this key — a second, separate', text2='permission. Key disabled? Decrypt fails: the data is unreadable.', svc='Key policies / Key Vault access / KMS IAM — separation of duties'),
      dict(on=list(RN), hot='ok', move=(278, 127, 298, 90, 'response'), head='Step 6 · Data returned, everything logged', text='Storage decrypts with the data key and returns the file over TLS. The API call and the', text2='KMS decrypt are both recorded in the audit trail.', svc='Two audit records: storage access + key use')]
REQ = flow_anim('One request: authenticated, authorised, decrypted', 'What happens when an analyst reads an encrypted report.', 'Access + encryption', 'Animation: MFA sign-in and temporary credentials; signed TLS request; policy evaluation with deny precedence; encrypted object found; KMS checks key policy and decrypts data key; data returned and logged.', RN, RS, hid='reqflow')

def mapfig():
    o = t(320, 16, 'Seven basics of identity and encryption', 11, 'ink', bold=True)
    items = [('1', 'Identities', 'users, groups, roles, services', 'blue'), ('2', 'Authentication + MFA', 'prove who you are', 'violet'), ('3', 'Authorisation', 'policies, RBAC, least privilege', 'amber'), ('4', 'Federation + SSO', 'one login, many systems', 'blue'),
             ('5', 'Encryption at rest', 'disks, objects, databases', 'green'), ('6', 'Encryption in transit', 'TLS everywhere', 'green'), ('7', 'Key management', 'KMS, CMKs, HSMs, rotation', 'red')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 7.8, 'ink', bold=True) + t(x + 78, y + 54, b, 6.4, 'ink2')
    o += t(320, 210, '1–4 control who can ask; 5–7 control who can read even if data is copied.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of seven basics: identities, authentication and MFA, authorisation, federation and SSO, encryption at rest, encryption in transit, key management.', mapfig(), h=222)

A1 = mk(['People', 'Groups', 'Workloads'], ['users|Riya, Kabir|humans', 'groups|analysts, admins|assign once', 'roles / MIs|apps, functions|no passwords'], ['blue', 'blue', 'green'],
        ['each person gets their own identity', 'permissions are given to groups, not individuals', 'applications use roles or managed identities, not stored keys'],
        [('People', 'One identity per person; no sharing.', ''), ('Groups', 'Assign permissions to groups.', ''), ('Workloads', 'Apps use roles/managed identities with temporary credentials.', '')],
        'Identities in action', 'Who is who.', 'Identities', 'Animation: people; groups; workload identities.', 'i1anim')
T1 = vt(1, 'Identities: users, groups, roles and service identities', 'blue',
    'An <b>identity</b> (principal) is anything that can make requests: <b>human users</b> (ideally from a central directory), <b>groups</b> that collect users for permission assignment, and <b>workload identities</b> — IAM roles, Azure managed identities, Google service accounts — that applications assume to receive short-lived credentials without stored secrets. The <b>root/owner account</b> is a special identity to lock away.',
    'An office: each employee has a personal ID card, departments get floor access, and the delivery robot has its own badge that only opens the store room.',
    'TiffinGo moved the reporting job from an admin key to an IAM role attached to its container; analysts are in an “analysts” group in IAM Identity Center.',
    'AWS IAM users/groups/roles, IAM Identity Center; Microsoft Entra ID users/groups, managed identities, service principals; Google Cloud Identity users/groups, service accounts.', '', A1,
    'always — one identity per person and per workload.',
    'people share logins or apps use a person’s credentials.',
    'Accounts for people and apps, so the cloud always knows who is asking.',
    [('Root', 'MFA, no keys, lock away.'), ('People', 'From SSO directory.'), ('Groups', 'Permissions via groups.'), ('Workloads', 'Roles/managed identities.'), ('Lifecycle', 'Remove leavers automatically.')],
    [('principal', 'any identity that can make a request'), ('role', 'an identity assumed temporarily, with its own permissions'), ('managed identity', 'Azure identity for a resource, credentials handled by Azure')],
    table(['', 'IAM user + access key', 'Role / managed identity'], [['Credential lifetime', 'until rotated', 'minutes–hours, automatic'], ['Leak risk', 'high', 'low'], ['Best for', 'rare legacy cases', 'apps, pipelines, people via SSO']], minw=460),
    ['Every account', 'Applications', 'Pipelines'],
    'AWS’s own guidance is to avoid IAM users with long-term keys for humans and to use IAM Identity Center or federation instead.',
    'Name roles after the job, not the person (“report-reader”, not “kabir-role”) — permissions should outlive staff changes.')

A2 = mk(['Something you know', 'Something you have', 'Verified login'], ['password|or passkey|first factor', 'MFA|app, key, phone|second factor', 'session|token issued|short-lived'], ['violet', 'amber', 'green'],
        ['a password or passkey is the first factor', 'a second factor — authenticator app or security key — is required', 'only then is a session token issued'],
        [('Know', 'Password or passkey.', ''), ('Have', 'Authenticator app or hardware key.', ''), ('Session', 'A short-lived token is issued.', '')],
        'Authentication + MFA in action', 'Prove it twice.', 'MFA', 'Animation: something you know; something you have; verified login.', 'i2anim')
T2 = vt(2, 'Authentication and multi-factor authentication (MFA)', 'violet',
    '<b>Authentication</b> verifies that an identity is who it claims to be; <b>multi-factor authentication (MFA)</b> requires two or more independent factors — something you know (password), have (authenticator app, hardware security key, passkey) or are (biometrics) — greatly reducing the risk from stolen passwords. Phishing-resistant MFA (FIDO2 keys, passkeys) is strongest.',
    'An ATM: the card (have) and the PIN (know) — neither alone is enough.',
    'After the leaked-key incident, TiffinGo enforced MFA for every console user and security keys for the two admins.',
    'AWS IAM MFA (virtual, FIDO2), Identity Center MFA; Entra MFA, Conditional Access, security defaults; Google 2-Step Verification, security keys. Azure has been enforcing MFA for portal and CLI sign-ins since 2024–2025.', '', A2,
    'for every human login — especially root/owner and admins.',
    'you rely on SMS codes for admins — SIM-swap attacks defeat them.',
    'Logging in with a password plus a second proof, like a code from your phone.',
    [('Enrol', 'Authenticator or security key.'), ('Enforce', 'Policies require MFA.'), ('Root', 'Hardware key on root/owner.'), ('Conditional', 'Stronger checks for risky sign-ins.'), ('Recover', 'Backup methods, break-glass.')],
    [('factor', 'one type of proof'), ('phishing-resistant', 'cannot be tricked into giving codes to fake sites'), ('passkey', 'device-bound credential replacing passwords')],
    table(['', 'SMS code', 'Authenticator app', 'Security key / passkey'], [['Phishing resistance', 'low', 'medium', 'high'], ['SIM-swap risk', 'yes', 'no', 'no'], ['Best for', 'basic users', 'most users', 'admins']], minw=480),
    ['All human accounts', 'Admins', 'Root/owner'],
    'Microsoft has reported that MFA blocks the vast majority of automated account-compromise attacks — one of the highest-value controls available.',
    'Root/owner accounts: hardware MFA, no access keys, credentials in a safe, alerts on every sign-in.')

A3 = mk(['Request arrives', 'Policies evaluated', 'Allow or deny'], ['request|action + resource|+ context', 'evaluate|identity, resource|boundaries, SCPs', 'decision|explicit deny wins|default deny'], ['amber', 'blue', 'green'],
        ['every request names an action on a resource with context', 'all applicable policies are evaluated together', 'explicit deny wins; without an allow the answer is no'],
        [('Request', 'Action + resource + context (IP, MFA, time).', ''), ('Evaluate', 'Identity, resource, boundary and organisation policies.', ''), ('Decide', 'Explicit deny > allow > implicit deny.', '')],
        'Authorisation in action', 'Default deny, least privilege.', 'Authorisation', 'Animation: request; policies evaluated; allow or deny.', 'i3anim')
T3 = vt(3, 'Authorisation: policies, RBAC and least privilege', 'amber',
    '<b>Authorisation</b> decides what an authenticated identity may do. Cloud platforms evaluate policies — identity-based, resource-based, permission boundaries, organisation guard-rails — with <b>default deny</b> and <b>explicit deny overriding allow</b>; Azure and Google use <b>role-based access control (RBAC)</b> assignments at a scope; conditions enable attribute-based control (ABAC). <b>Least privilege</b> grants only the permissions a task needs.',
    'Hotel key cards: your card opens your room and the gym, not other rooms — and the manager can block a card instantly.',
    'The report-reader role allows s3:GetObject only on reports/* and has an explicit deny on deletes; the old admin key was deleted (practical step 1).',
    'AWS IAM policies, SCPs, permission boundaries, IAM Access Analyzer policy generation; Azure RBAC built-in/custom roles, Azure Policy, PIM; Google IAM predefined/custom roles, IAM Conditions, deny policies, IAM recommender.', '', A3,
    'every identity — start narrow and widen only on real errors.',
    'you grant “*” or Owner/Editor “temporarily” — temporary becomes permanent.',
    'Rules that decide exactly what each person or app is allowed to do.',
    [('Default deny', 'Nothing unless allowed.'), ('Allow narrowly', 'Specific actions + resources.'), ('Guard-rails', 'SCPs/Azure Policy/org policies.'), ('Review', 'Unused-permission findings.'), ('Elevate JIT', 'Time-bound admin (PIM).')],
    [('least privilege', 'only the permissions needed'), ('scope', 'where a role applies: account, subscription, project, resource'), ('JIT access', 'just-in-time, temporary elevation')],
    table(['', 'AWS IAM', 'Azure RBAC', 'Google IAM'], [['Unit', 'JSON policy statements', 'role assignment at scope', 'role binding on resource hierarchy'], ['Deny', 'explicit deny statements', 'deny assignments (limited)', 'IAM deny policies'], ['Org guard-rail', 'SCPs', 'Azure Policy', 'org policies']], minw=520),
    ['Every workload', 'Admin access', 'Cross-account sharing'],
    'Access-analysis tools across providers report that most granted permissions are never used — the gap least privilege closes.',
    'Generate policies from real usage (IAM Access Analyzer policy generation, Google IAM recommender) instead of guessing.')

A4 = mk(['Company directory', 'Trust set up', 'One login everywhere'], ['IdP|Entra ID, Google|Okta', 'federation|SAML / OIDC|trust', 'SSO|AWS, Azure, GCP|SaaS apps'], ['blue', 'violet', 'green'],
        ['people exist once, in the company identity provider', 'clouds and apps trust it through SAML or OIDC', 'one login (with MFA) reaches every system; leavers are disabled once'],
        [('Directory', 'People exist once in the identity provider.', ''), ('Trust', 'Clouds and SaaS trust it via SAML/OIDC.', ''), ('SSO', 'One login with MFA; disable once on leaving.', '')],
        'Federation + SSO in action', 'One identity, many systems.', 'Federation', 'Animation: company directory; trust set up; one login everywhere.', 'i4anim')
T4 = vt(4, 'Federation and single sign-on (SSO)', 'blue',
    '<b>Federation</b> lets a cloud or application trust identities from an external <b>identity provider (IdP)</b> using standards such as SAML 2.0 and OpenID Connect; <b>single sign-on</b> lets users authenticate once (with MFA) and access many systems. <b>Workload identity federation</b> applies the same idea to machines — for example GitHub Actions obtaining cloud tokens via OIDC without stored keys.',
    'A national ID card accepted by banks, airports and telecoms — each trusts the issuer instead of issuing its own card.',
    'TiffinGo connected Google Workspace to AWS IAM Identity Center and Azure; when a contractor left, disabling one Workspace account removed access to all three (Lesson 9.2’s insider threat).',
    'AWS IAM Identity Center, IAM OIDC/SAML providers; Entra ID (enterprise apps, external identities); Google Workforce and Workload Identity Federation; Okta, Ping.', 'OIDC for pipelines was used in Lesson 8.3.', A4,
    'more than a handful of people or more than one cloud/SaaS.',
    'local users are still created alongside SSO — leavers slip through.',
    'One company login that works for all cloud accounts and apps.',
    [('Pick IdP', 'Entra ID, Google, Okta.'), ('Connect', 'SAML/OIDC trust.'), ('Map', 'Groups → roles/permission sets.'), ('Enforce', 'MFA and conditional access at IdP.'), ('Automate', 'SCIM provisioning and de-provisioning.')],
    [('IdP', 'identity provider'), ('SAML / OIDC', 'standards for federated login'), ('SCIM', 'standard for automatic user provisioning')],
    table(['', 'SAML', 'OIDC'], [['Format', 'XML assertions', 'JSON web tokens'], ['Typical use', 'enterprise web SSO', 'modern apps, workloads, mobile'], ['Workload federation', 'rare', 'common (GitHub → cloud)']], minw=440),
    ['Enterprises', 'Multi-cloud', 'CI/CD pipelines'],
    'Workload identity federation removed the most-leaked secret type from many pipelines: long-lived cloud keys stored in CI systems.',
    'Map IdP groups to cloud roles (permission sets / RBAC) — then access changes are HR/group changes, not cloud tickets.')

A5 = mk(['Data written', 'Encrypted on disk', 'Copy is useless'], ['write|object, disk|database', 'encrypt|AES-256|data key', 'stolen copy|ciphertext|without key'], ['green', 'blue', 'amber'],
        ['the service writes data to storage', 'it is encrypted with AES-256 using a data key', 'a copied disk or file is unreadable without the key'],
        [('Write', 'Data is written to disk/object/database.', ''), ('Encrypt', 'AES-256 with a data key, protected by a KMS key.', ''), ('Protect', 'A stolen copy is ciphertext without the key.', '')],
        'Encryption at rest in action', 'Locked when stored.', 'At rest', 'Animation: data written; encrypted on disk; copy is useless.', 'i5anim')
T5 = vt(5, 'Encryption at rest', 'green',
    '<b>Encryption at rest</b> protects stored data — block volumes, object storage, databases, backups — by encrypting it (typically AES-256) with keys held in a key management service; all three major providers encrypt stored data by default with provider-managed keys, and customers can choose <b>customer-managed keys (CMKs)</b> for control over key policy, rotation, disabling and audit.',
    'Valuables in a locker: even if someone carries the locker away, they still need the key.',
    'TiffinGo’s reports bucket uses SSE-KMS with its own key; the “report-reader” role must be allowed in the key policy too — two locks, two permissions (animation step 5).',
    'S3/EBS/RDS encryption with AWS KMS; Azure Storage Service Encryption, Azure Disk Encryption, TDE for SQL with Key Vault; Google default encryption, CMEK with Cloud KMS.', '', A5,
    'always (it is default) — add CMKs for sensitive or regulated data.',
    'you think default encryption stops an over-permitted user — it does not; access control still decides.',
    'Scrambling stored data so a stolen copy cannot be read without the key.',
    [('Default', 'Provider keys, automatic.'), ('CMK', 'Your key in KMS.'), ('Policy', 'Who may use the key.'), ('Rotate', 'Automatic yearly rotation.'), ('Shred', 'Disable/schedule deletion of key.')],
    [('AES-256', 'standard strong symmetric encryption'), ('CMK', 'customer-managed key'), ('crypto-shredding', 'making data unreadable by destroying its key')],
    table(['', 'Provider-managed key', 'Customer-managed key'], [['Effort', 'none', 'some'], ['Control', 'provider policy', 'your key policy, disable, audit'], ['Cost', 'free', 'small per key + requests']], minw=440),
    ['Databases', 'Object storage', 'Backups'],
    'Amazon S3 has encrypted all new objects by default (SSE-S3) since January 2023; Azure and Google encrypt stored data by default too.',
    'Encryption at rest mainly protects against physical theft and some insider paths; most breaches use valid credentials, which decrypt transparently — identity remains the main control.')

A6 = mk(['Client connects', 'TLS handshake', 'Encrypted channel'], ['client|browser, CLI|app', 'handshake|certificate check|key exchange', 'channel|AES-GCM|tamper-proof'], ['violet', 'amber', 'green'],
        ['a client connects to a service endpoint', 'TLS verifies the server certificate and agrees keys', 'all traffic is encrypted and integrity-protected'],
        [('Connect', 'Client connects to an HTTPS endpoint.', ''), ('Handshake', 'Certificate verified; session keys agreed.', ''), ('Protect', 'Traffic encrypted and tamper-evident.', '')],
        'Encryption in transit in action', 'Locked while travelling.', 'In transit', 'Animation: client connects; TLS handshake; encrypted channel.', 'i6anim')
T6 = vt(6, 'Encryption in transit (TLS)', 'green',
    '<b>Encryption in transit</b> protects data moving between clients and services or between services, normally with <b>TLS</b> (1.2 or 1.3): the server proves its identity with a certificate, keys are exchanged, and traffic is encrypted and integrity-protected; cloud APIs require HTTPS, and customers enforce TLS on their own endpoints, storage and databases (including mutual TLS between services).',
    'A sealed, tamper-evident courier bag: nobody on the way can read or change the contents unnoticed.',
    'TiffinGo enforces HTTPS-only on its bucket and storage account, minimum TLS 1.2, and certificates from ACM/Key Vault/Certificate Manager auto-renew (practical step 3).',
    'AWS Certificate Manager, load-balancer TLS policies, S3 aws:SecureTransport; Azure App Service/Front Door TLS, storage minimum TLS; Google-managed certificates, SSL policies, Certificate Manager.', '', A6,
    'always, including internal service-to-service traffic.',
    'TLS terminates at a load balancer and continues as plain HTTP across untrusted networks.',
    'Scrambling data while it travels over the network, like the padlock in your browser.',
    [('Certificates', 'Managed, auto-renewing.'), ('Minimum version', 'TLS 1.2+.'), ('Enforce', 'HTTPS-only policies.'), ('Internal', 'TLS/mTLS between services.'), ('Monitor', 'Expiry alerts.')],
    [('TLS', 'Transport Layer Security'), ('certificate', 'signed proof of a server’s identity'), ('mTLS', 'mutual TLS — both sides present certificates')],
    table(['', 'TLS 1.2', 'TLS 1.3'], [['Handshake', '2 round trips', '1 round trip'], ['Old ciphers', 'some allowed', 'removed'], ['Status', 'minimum today', 'preferred']], minw=420),
    ['Web apps and APIs', 'Database connections', 'Service mesh'],
    'Cloud providers have retired TLS 1.0 and 1.1 on their API endpoints, so outdated clients must be upgraded.',
    'Managed certificates remove the most common TLS outage: an expired certificate nobody renewed.')

A7 = mk(['Key created in KMS', 'Envelope encryption', 'Control + audit'], ['KMS key|never leaves|HSM-backed', 'data key|encrypts data|wrapped by KMS key', 'control|policy, rotation|disable, logs'], ['red', 'amber', 'green'],
        ['a master key is created inside the KMS and never leaves it', 'data keys encrypt the data; the KMS key encrypts (wraps) the data keys', 'policies, rotation, disabling and audit logs give you control'],
        [('Create', 'A KMS key lives inside HSM-backed infrastructure.', ''), ('Envelope', 'Data keys encrypt data; the KMS key wraps data keys.', ''), ('Control', 'Policy, rotation, disable, audit every use.', '')],
        'Key management in action', 'Guard the keys, not just the data.', 'Key management', 'Animation: key created in KMS; envelope encryption; control and audit.', 'i7anim')
T7 = vt(7, 'Key management (KMS, CMK, HSM, envelope encryption)', 'red',
    '<b>Key management</b> covers creating, storing, using, rotating and destroying cryptographic keys. Cloud KMS services keep master keys inside hardware security modules (HSMs), perform <b>envelope encryption</b> (data encrypted with data keys; data keys encrypted by a KMS key), enforce key-use policies separate from data permissions, rotate keys and log every use; options range from provider-managed keys to customer-managed, customer-supplied/external keys and dedicated HSMs.',
    'A bank vault holds the master key; each locker has its own small key, kept in an envelope sealed by the master key. Lose the master key — or lock it away — and no envelope can be opened.',
    'TiffinGo’s KMS key for reports: automatic yearly rotation, only the report-reader role and the backup service may decrypt, and the incident runbook includes “disable key” to make leaked copies useless (practical step 2).',
    'AWS KMS, CloudHSM, external key store; Azure Key Vault (Standard/Premium), Managed HSM; Google Cloud KMS, Cloud HSM, Cloud External Key Manager.', '', A7,
    'you need control, separation of duties or the ability to revoke access to data.',
    'you delete a key with data still encrypted under it — that data is gone forever (deletion waits 7–30 days to prevent accidents).',
    'Looking after the secret keys that lock your data — where they live, who can use them, and when they change.',
    [('Create', 'Symmetric/asymmetric keys.'), ('Policy', 'Key users vs key admins.'), ('Use', 'Encrypt/decrypt via API.'), ('Rotate', 'Automatic versions.'), ('Retire', 'Disable, then scheduled deletion.')],
    [('HSM', 'tamper-resistant hardware that protects keys'), ('envelope encryption', 'encrypting data keys with a master key'), ('BYOK / HYOK', 'bring / hold your own key')],
    table(['', 'Provider-managed', 'Customer-managed (KMS)', 'External / dedicated HSM'], [['Control', 'low', 'high', 'highest'], ['Effort', 'none', 'low', 'high'], ['Use when', 'default', 'regulated data', 'sovereignty, strict regulation']], minw=500),
    ['Regulated data', 'Multi-tenant SaaS (key per tenant)', 'Sovereignty needs (3.1)'],
    'Envelope encryption is why KMS can protect terabytes: the KMS only ever encrypts small data keys, so the master key never leaves the HSM and large files never travel to KMS.',
    'Separate key administrators (can manage, cannot decrypt) from key users (can decrypt, cannot manage) — classic separation of duties auditors look for.')

SUMMARY = table(['#', 'Basic', 'Protects against', 'AWS', 'Azure', 'Google Cloud'], [
    ['1', 'Identities', 'shared/anonymous access', 'IAM roles, Identity Center', 'Entra ID, managed identities', 'Cloud Identity, service accounts'], ['2', 'MFA', 'stolen passwords', 'IAM MFA, Identity Center', 'Entra MFA, Conditional Access', '2-Step Verification, keys'],
    ['3', 'Authorisation', 'excess permissions', 'IAM policies, SCPs', 'RBAC, Azure Policy, PIM', 'IAM roles, deny policies'], ['4', 'Federation/SSO', 'orphan accounts, key sprawl', 'Identity Center, OIDC providers', 'Entra enterprise apps', 'Workforce/Workload Identity Federation'],
    ['5', 'At rest', 'stolen disks/copies', 'KMS-backed SSE', 'SSE + Key Vault CMK', 'default + CMEK'], ['6', 'In transit', 'eavesdropping', 'ACM, TLS policies', 'TLS settings, Front Door', 'managed certs, SSL policies'], ['7', 'Key management', 'loss of key control', 'KMS, CloudHSM', 'Key Vault, Managed HSM', 'Cloud KMS, HSM, EKM']], minw=700)
CHECK = ('  <h3>Check yourself: which basic?</h3>\n' +
    qx('A. An EC2 app reads S3 without any stored keys.', ['IAM role (workload identity)', 'MFA', 'TLS', 'HSM'], 0, 'Role.') +
    qx('B. A deny statement and an allow statement both match.', ['Deny wins', 'Allow wins', 'Newest wins', 'Random'], 0, 'Explicit deny overrides.') +
    qx('C. Disabling a key makes all copies of data unreadable.', ['Key management / crypto-shredding', 'SSO', 'RBAC', 'TLS'], 0, 'Key control.') +
    qx('D. Disabling one Workspace account removes AWS, Azure and SaaS access.', ['Federation + SSO', 'Encryption at rest', 'HSM', 'Default deny'], 0, 'Central identity.'))

TYPES = ('  <p>Seven basics, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, where used, real-world example, TiffinGo scenario and an expert note.</p>\n'
         + challenge(['If default encryption is on, why can a leaked admin key still read everything?', 'What wins when allow and deny both match?', 'Why does KMS never receive your 5 GB file?'], 'types 5, 3 and 7') + MAP
         + jump(['Identities', 'MFA', 'Authorisation', 'Federation', 'At rest', 'In transit', 'Keys']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY + '\n' + CHECK)

parts = wwu([
    ('Root / owner account', 'The all-powerful first identity.', 'If lost, everything is lost.', 'Hardware MFA, no keys, break-glass only.'),
    ('Permission boundary / guard-rail', 'Maximum permissions possible.', 'Limits damage of mistakes.', 'SCPs, permission boundaries, Azure Policy, org policies.'),
    ('Temporary credentials', 'Tokens that expire.', 'Leaks age out quickly.', 'STS, managed identity tokens, OAuth.'),
    ('Key policy', 'Who may use/manage a key.', 'Second lock on encrypted data.', 'KMS key policy, Key Vault RBAC, KMS IAM.'),
    ('Secrets manager', 'Stores passwords and API keys.', 'No secrets in code or images.', 'Secrets Manager, Key Vault, Secret Manager.'),
    ('Access reviews', 'Periodic check of who has what.', 'Removes creep and leavers.', 'Access Analyzer, Entra access reviews, IAM recommender.')])

DEEP = ('  <h3>Zero Trust in one paragraph</h3>\n  <p><b>Zero Trust</b> means never trusting a request because of where it comes from (inside the office network); every request is authenticated, authorised with least privilege and continuously evaluated using identity, device health and context. Cloud identity, MFA, conditional access and fine-grained policies are its building blocks.</p>\n'
    '  <h3>AWS policy evaluation, precisely</h3>\n  <ol><li>Start with implicit deny.</li><li>Any explicit deny in any applicable policy (SCP, resource, identity, boundary, session) → final deny.</li><li>Organisations SCPs/RCPs must allow the action.</li><li>Resource-based policy allow may grant access (same account).</li><li>Identity-based policy must allow (and permission boundary and session policy, if present, must also allow).</li><li>Otherwise → implicit deny.</li></ol>\n'
    '  <h3>Encryption in use (confidential computing)</h3>\n  <p>Data must be decrypted to be processed — unless it runs in a hardware-protected <b>trusted execution environment</b>. AWS Nitro Enclaves, Azure confidential VMs/containers and Google Confidential VMs keep data encrypted in memory and isolated even from cloud operators, for very sensitive workloads.</p>\n'
    '  <h3>Key and secret hygiene checklist</h3>\n  <ul><li>No long-lived access keys for humans; workloads use roles/managed identities/service account attachment.</li><li>Secrets in a secrets manager with rotation.</li><li>CMKs for regulated data, automatic rotation on, key admins ≠ key users.</li><li>TLS 1.2+ everywhere with managed certificates.</li><li>Alert on: root sign-in, MFA disabled, key disabled/scheduled for deletion, policy attached with “*”.</li></ul>')

clouds = vendor_tabs('<p><b>AWS:</b> IAM (users, groups, roles, policies), IAM Identity Center (SSO), STS, Organizations SCPs, IAM Access Analyzer, KMS, CloudHSM, Secrets Manager, Certificate Manager.</p>',
    '<p><b>Azure:</b> Microsoft Entra ID (SSO, MFA, Conditional Access, PIM), managed identities, Azure RBAC, Key Vault and Managed HSM, App Service/Front Door TLS, Defender for Cloud identity recommendations.</p>',
    '<p><b>Google Cloud:</b> Cloud Identity, IAM roles and conditions, deny policies, service accounts, Workload/Workforce Identity Federation, Cloud KMS, Cloud HSM, External Key Manager, Secret Manager, Certificate Manager.</p>') + \
    cloud3([['SSO / directory', 'IAM Identity Center', 'Entra ID', 'Cloud Identity'], ['Workload identity', 'IAM roles', 'Managed identities', 'Service accounts'], ['Least-privilege help', 'Access Analyzer', 'PIM, access reviews', 'IAM recommender'], ['Key management', 'KMS / CloudHSM', 'Key Vault / Managed HSM', 'Cloud KMS / HSM / EKM'], ['Secrets', 'Secrets Manager', 'Key Vault secrets', 'Secret Manager']])

MOCKQ.extend([
 (mock('aws', ['IAM', 'Roles', 'Create role'], ['Users', 'User groups', 'Roles', 'Policies'], 'Roles', [('Trusted entity', '[x] AWS account · this account'), ('Permissions', 'inline: s3:GetObject on reports/*'), ('Role name', 'report-reader')], 'Create role'),
  mock('az', ['Storage account', 'Access control (IAM)', 'Add role assignment'], ['Overview', 'Access control (IAM)', 'Containers'], 'Access control (IAM)', [('Role', 'Storage Blob Data Reader'), ('Assign access to', '[x] Managed identity · id-report-reader'), ('Scope', 'container: reports')], 'Review + assign'),
  mock('gcp', ['Cloud Storage', 'Bucket', 'Permissions', 'Grant access'], ['Objects', 'Configuration', 'Permissions'], 'Permissions', [('New principals', 'report-reader@PROJECT.iam.gserviceaccount.com'), ('Role', 'Storage Object Viewer')], 'Save')),
 (mock('aws', ['Key Management Service', 'Customer managed keys'], ['AWS managed keys', 'Customer managed keys', 'Custom key stores'], 'Customer managed keys', [('Alias', 'tiffingo-reports'), ('Key rotation', '[x] Automatically rotate every year'), ('Key state', 'Enabled → Disable')], 'Key actions'),
  mock('az', ['Key vaults', 'kv-tiffingo', 'Keys'], ['Overview', 'Keys', 'Secrets', 'Access control (IAM)'], 'Keys', [('Key', 'reports-key · RSA 2048'), ('Enabled', '[x] Yes → No')], 'Save'),
  mock('gcp', ['Security', 'Key Management', 'tiffingo-ring'], ['Key rings', 'Keys', 'Versions'], 'Keys', [('Key', 'reports-key · symmetric'), ('Version 1', 'Enabled → Disable'), ('Rotation', 'every 365 days')], 'Disable')),
 (mock('aws', ['S3', 'Bucket', 'Permissions', 'Bucket policy'], ['Objects', 'Properties', 'Permissions'], 'Permissions', [('Statement', 'Deny if aws:SecureTransport = false'), ('Effect', 'HTTP requests rejected')], 'Save changes'),
  mock('az', ['Storage account', 'Configuration'], ['Overview', 'Configuration', 'Networking'], 'Configuration', [('Secure transfer required', '[x] Enabled'), ('Minimum TLS version', '▾ Version 1.2')], 'Save'),
  mock('gcp', ['Network security', 'SSL policies', 'Create'], ['Cloud Armor', 'SSL policies', 'Firewall policies'], 'SSL policies', [('Name', 'tls12-modern'), ('Minimum TLS version', '▾ TLS 1.2'), ('Profile', '▾ Modern')], 'Create')),
])

STEP1 = ('1 · Build a least-privilege identity and test allow vs deny', tri(
    (['[[S3]] → create bucket <code>tiffingo-reports-…</code> with folders <code>reports/</code> and <code>private/</code>.', '[[IAM]] → [[Roles]] → [[Create role]] → trusted entity [[AWS account]] (this account) → inline policy allowing <code>s3:GetObject</code> on <code>reports/*</code> only → name <code>report-reader</code>.', 'Use the role (switch role in the console, or assume-role in the CLI) and try both folders.'],
     "B=tiffingo-reports-$RANDOM; aws s3 mb s3://$B --region ap-south-1\necho 'october totals' > oct.csv; aws s3 cp oct.csv s3://$B/reports/oct.csv; aws s3 cp oct.csv s3://$B/private/salaries.csv\nACC=$(aws sts get-caller-identity --query Account --output text)\naws iam create-role --role-name report-reader --assume-role-policy-document \"{\\\"Version\\\":\\\"2012-10-17\\\",\\\"Statement\\\":[{\\\"Effect\\\":\\\"Allow\\\",\\\"Principal\\\":{\\\"AWS\\\":\\\"arn:aws:iam::$ACC:root\\\"},\\\"Action\\\":\\\"sts:AssumeRole\\\"}]}\" >/dev/null\naws iam put-role-policy --role-name report-reader --policy-name read-reports --policy-document \"{\\\"Version\\\":\\\"2012-10-17\\\",\\\"Statement\\\":[{\\\"Effect\\\":\\\"Allow\\\",\\\"Action\\\":\\\"s3:GetObject\\\",\\\"Resource\\\":\\\"arn:aws:s3:::$B/reports/*\\\"}]}\"\nsleep 10\nread AK SK ST < <(aws sts assume-role --role-arn arn:aws:iam::$ACC:role/report-reader --role-session-name riya --duration-seconds 900 \\\n  --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' --output text)\nAWS_ACCESS_KEY_ID=$AK AWS_SECRET_ACCESS_KEY=$SK AWS_SESSION_TOKEN=$ST aws s3 cp s3://$B/reports/oct.csv - \nAWS_ACCESS_KEY_ID=$AK AWS_SECRET_ACCESS_KEY=$SK AWS_SESSION_TOKEN=$ST aws s3 cp s3://$B/private/salaries.csv - 2>&1 | tail -1",
     '<code>october totals</code> for reports/, then <code>An error occurred (403) … Forbidden</code> for private/ — implicit deny. The temporary credentials expire in 15 minutes.'),
    (['[[Managed Identities]] → [[Create]] <code>id-report-reader</code>.', 'Storage account → container <code>reports</code> → [[Access control (IAM)]] → [[Add role assignment]] → [[Storage Blob Data Reader]] → the managed identity → scope = this container only.', '[[Check access]] → select the identity → it shows read on <code>reports</code>, nothing on <code>private</code>.'],
     "az group create -n rg-iam -l centralindia\nSA=tgiam$RANDOM; az storage account create -n $SA -g rg-iam -l centralindia --sku Standard_LRS --allow-blob-public-access false\naz identity create -g rg-iam -n id-report-reader\nPID=$(az identity show -g rg-iam -n id-report-reader --query principalId -o tsv)\nSCOPE=$(az storage account show -n $SA -g rg-iam --query id -o tsv)/blobServices/default/containers/reports\naz storage container create --account-name $SA -n reports --auth-mode login; az storage container create --account-name $SA -n private --auth-mode login\naz role assignment create --assignee-object-id $PID --assignee-principal-type ServicePrincipal --role 'Storage Blob Data Reader' --scope $SCOPE\naz role assignment list --assignee $PID --all --query \"[].{role:roleDefinitionName,scope:scope}\" -o table",
     'one assignment: <code>Storage Blob Data Reader</code> scoped to <code>…/containers/reports</code>. An app running with this identity (VM, App Service, Function) reads reports and gets 403 on private — with no password anywhere. (If container creation is denied, give yourself “Storage Blob Data Contributor” on the account.)'),
    (['[[IAM &amp; Admin]] → [[Service accounts]] → [[Create]] <code>report-reader</code> (no project role).', 'Bucket <code>tiffingo-reports-…</code> → [[Permissions]] → [[Grant access]] → the service account → [[Storage Object Viewer]] (bucket level only).', 'Test with impersonation from Cloud Shell (right).'],
     "P=$(gcloud config get-value project); ME=$(gcloud config get-value account)\nB=tiffingo-reports-$RANDOM; B2=tiffingo-private-$RANDOM\ngcloud storage buckets create gs://$B gs://$B2 --location=asia-south1\necho 'october totals' > oct.csv; gcloud storage cp oct.csv gs://$B/reports/oct.csv; gcloud storage cp oct.csv gs://$B2/salaries.csv\ngcloud iam service-accounts create report-reader\nSA=report-reader@$P.iam.gserviceaccount.com\ngcloud storage buckets add-iam-policy-binding gs://$B --member=serviceAccount:$SA --role=roles/storage.objectViewer\ngcloud iam service-accounts add-iam-policy-binding $SA --member=user:$ME --role=roles/iam.serviceAccountTokenCreator\nsleep 30\ngcloud storage cat gs://$B/reports/oct.csv --impersonate-service-account=$SA\ngcloud storage cat gs://$B2/salaries.csv --impersonate-service-account=$SA 2>&1 | tail -1",
     '<code>october totals</code>, then a <code>403 … does not have storage.objects.get access</code> error for the other bucket (IAM changes can take a minute to apply).')),
    'Least privilege in practice: the identity can do exactly one job. Everything else is denied by default.')

STEP2 = ('2 · Encrypt with your own key — then “shred” access by disabling it', tri(
    (['[[Key Management Service]] → [[Customer managed keys]] → [[Create key]] → symmetric → alias <code>tiffingo-reports</code> → enable automatic rotation.', 'Encrypt a small secret, decrypt it, then [[Key actions]] → [[Disable]] and try again.'],
     "KEY=$(aws kms create-key --description 'tiffingo reports' --query KeyMetadata.KeyId --output text)\naws kms create-alias --alias-name alias/tiffingo-reports --target-key-id $KEY\naws kms enable-key-rotation --key-id $KEY\naws kms encrypt --key-id alias/tiffingo-reports --plaintext fileb://oct.csv --query CiphertextBlob --output text | base64 -d > oct.enc\naws kms decrypt --ciphertext-blob fileb://oct.enc --query Plaintext --output text | base64 -d\naws kms disable-key --key-id $KEY\naws kms decrypt --ciphertext-blob fileb://oct.enc 2>&1 | tail -1",
     '<code>october totals</code> after decrypt, then <code>DisabledException … is disabled</code>. Any data (S3 objects, EBS, RDS) encrypted under this key becomes unreadable until you re-enable it. A KMS key costs about $1 a month, prorated.'),
    (['[[Key vaults]] → [[Create]] <code>kv-tiffingo-…</code> (Standard, RBAC permission model) → give yourself [[Key Vault Crypto Officer]] → [[Keys]] → [[Generate]] <code>reports-key</code> (RSA 2048).', 'Encrypt a small value, decrypt it, then set the key [[Enabled]] = No and try again.'],
     "KV=kv-tiffingo-$RANDOM; az keyvault create -n $KV -g rg-iam -l centralindia --enable-rbac-authorization true\naz role assignment create --assignee $(az ad signed-in-user show --query id -o tsv) --role 'Key Vault Crypto Officer' --scope $(az keyvault show -n $KV --query id -o tsv)\nsleep 30; az keyvault key create --vault-name $KV -n reports-key --kty RSA --size 2048 >/dev/null\nCT=$(az keyvault key encrypt --vault-name $KV -n reports-key --algorithm RSA-OAEP-256 --value $(echo -n 'data-key-123' | base64) --query result -o tsv)\naz keyvault key decrypt --vault-name $KV -n reports-key --algorithm RSA-OAEP-256 --value $CT --query result -o tsv | base64 -d; echo\naz keyvault key set-attributes --vault-name $KV -n reports-key --enabled false >/dev/null\naz keyvault key decrypt --vault-name $KV -n reports-key --algorithm RSA-OAEP-256 --value $CT 2>&1 | tail -1",
     '<code>data-key-123</code> (a wrapped data key — envelope encryption), then an error that the operation is not allowed on a disabled key. Key Vault Standard charges per operation — a few paise here.'),
    (['[[Security]] → [[Key Management]] → [[Create key ring]] <code>tiffingo-ring</code> (asia-south1) → [[Create key]] <code>reports-key</code>, rotation 365 days.', 'Encrypt, decrypt, then disable the key version and try again.'],
     "gcloud services enable cloudkms.googleapis.com\ngcloud kms keyrings create tiffingo-ring --location=asia-south1\ngcloud kms keys create reports-key --keyring=tiffingo-ring --location=asia-south1 --purpose=encryption --rotation-period=365d --next-rotation-time=$(date -u -d '+365 days' +%Y-%m-%dT%H:%M:%SZ)\ngcloud kms encrypt --key=reports-key --keyring=tiffingo-ring --location=asia-south1 --plaintext-file=oct.csv --ciphertext-file=oct.enc\ngcloud kms decrypt --key=reports-key --keyring=tiffingo-ring --location=asia-south1 --ciphertext-file=oct.enc --plaintext-file=-\ngcloud kms keys versions disable 1 --key=reports-key --keyring=tiffingo-ring --location=asia-south1\ngcloud kms decrypt --key=reports-key --keyring=tiffingo-ring --location=asia-south1 --ciphertext-file=oct.enc --plaintext-file=- 2>&1 | tail -1",
     '<code>october totals</code>, then <code>FAILED_PRECONDITION … is not enabled</code>. Key rings cannot be deleted (they are free); key versions cost a few cents a month until destroyed.')),
    'Two locks: identity decides who may ask; the key decides who can read. Disabling the key is your emergency brake.')

STEP3 = ('3 · Enforce encryption in transit (TLS only)', tri(
    (['Bucket → [[Permissions]] → [[Bucket policy]] → add a statement denying any request where <code>aws:SecureTransport</code> is false → [[Save changes]].'],
     "aws s3api put-bucket-policy --bucket $B --policy \"{\\\"Version\\\":\\\"2012-10-17\\\",\\\"Statement\\\":[{\\\"Sid\\\":\\\"TLSOnly\\\",\\\"Effect\\\":\\\"Deny\\\",\\\"Principal\\\":\\\"*\\\",\\\"Action\\\":\\\"s3:*\\\",\\\"Resource\\\":[\\\"arn:aws:s3:::$B\\\",\\\"arn:aws:s3:::$B/*\\\"],\\\"Condition\\\":{\\\"Bool\\\":{\\\"aws:SecureTransport\\\":\\\"false\\\"}}}]}\"\naws s3 ls s3://$B/reports/\naws s3 ls s3://$B/reports/ --endpoint-url http://s3.ap-south-1.amazonaws.com 2>&1 | tail -1\ncurl -sv https://s3.ap-south-1.amazonaws.com -o /dev/null 2>&1 | grep -m1 -E 'SSL connection using|TLSv1'",
     'the listing over HTTPS, <code>AccessDenied</code> over plain HTTP (explicit deny wins), and a line such as <code>SSL connection using TLSv1.3</code>.'),
    (['Storage account → [[Configuration]] → [[Secure transfer required]] = Enabled, [[Minimum TLS version]] = 1.2 → [[Save]]. (Both are defaults for new accounts — verify.)'],
     "az storage account update -n $SA -g rg-iam --https-only true --min-tls-version TLS1_2\naz storage account show -n $SA -g rg-iam --query \"{httpsOnly:enableHttpsTrafficOnly,minTls:minimumTlsVersion}\"\ncurl -s -o /dev/null -w '%{http_code}\\n' http://$SA.blob.core.windows.net/reports?restype=container",
     '<code>httpsOnly: true, minTls: TLS1_2</code>, and an HTTP 4xx code for the plain-HTTP request.'),
    (['Cloud Storage always uses HTTPS. For your own load-balanced apps: [[Network security]] → [[SSL policies]] → [[Create]] <code>tls12-modern</code>, minimum TLS 1.2, profile Modern → attach to the HTTPS load balancer.'],
     "gcloud compute ssl-policies create tls12-modern --profile=MODERN --min-tls-version=1.2\ngcloud compute ssl-policies describe tls12-modern --format='value(minTlsVersion,profile)'\ncurl -sv https://storage.googleapis.com -o /dev/null 2>&1 | grep -m1 -E 'SSL connection using|TLSv1'",
     '<code>TLS_1_2 MODERN</code> and a TLS 1.3 connection to Google’s endpoint. SSL policies are free; attach them to HTTPS/SSL proxy load balancers.')),
    'Explicit deny for non-TLS traffic is a one-line control auditors love — and it shows deny precedence in action.')

prac = practical(OWN_INTRO + ' You build a least-privilege identity and watch allow vs deny, encrypt with your own key and disable it, and enforce TLS. Costs: a KMS/Key Vault/Cloud KMS key for a few hours — a few rupees at most.', [SETUP_STEP, STEP1, STEP2, STEP3],
    cleanup='<b>AWS:</b> <code>aws kms schedule-key-deletion --key-id $KEY --pending-window-in-days 7</code>; <code>aws kms delete-alias --alias-name alias/tiffingo-reports</code>; <code>aws s3 rb s3://$B --force</code>; <code>aws iam delete-role-policy --role-name report-reader --policy-name read-reports</code>; <code>aws iam delete-role --role-name report-reader</code>. '
            '<b>Azure:</b> <code>az group delete -n rg-iam --yes --no-wait</code>; then <code>az keyvault purge -n $KV</code> (soft-deleted vaults keep the name for 90 days). '
            '<b>Google Cloud:</b> <code>gcloud kms keys versions destroy 1 --key=reports-key --keyring=tiffingo-ring --location=asia-south1</code>; <code>gcloud storage rm -r gs://$B gs://$B2</code>; <code>gcloud iam service-accounts delete $SA --quiet</code>; <code>gcloud compute ssl-policies delete tls12-modern --quiet</code>.')

mist = mistakes([
    ['Admin access for apps “to make it work”.', 'Permission errors are annoying.', 'Start minimal; add only what fails; use policy generators.'],
    ['Long-lived access keys for people.', 'Habit from on-prem.', 'SSO + temporary credentials.'],
    ['Root/owner used daily.', 'Convenience.', 'Hardware MFA, no keys, break-glass only.'],
    ['Thinking encryption replaces access control.', 'Default encryption is transparent.', 'Identity decides who reads; keys add a second lock.'],
    ['Deleting a KMS key with data under it.', 'Cleanup zeal.', 'Disable first; deletion is irreversible after the waiting period.'],
    ['Secrets in code or env files in Git.', 'Quick setup.', 'Secrets manager + managed identities.']])

cert = table(['Exam / syllabus', 'What is asked'], [['C-DAC PGCP-BDA', 'Identity and access management; encryption basics.'], ['AWS CLF-C02', 'IAM users, groups, roles, policies; root user protection; MFA; Identity Center; least privilege; KMS, encryption at rest/in transit; Secrets Manager; ACM.'], ['AZ-900', 'Entra ID, authentication vs authorisation, MFA, Conditional Access, RBAC, Zero Trust, Key Vault.'], ['Google Cloud Digital Leader', 'IAM, least privilege, encryption by default, Cloud KMS, identity federation.']], minw=560) + \
    qx('1. Best way for an EC2 application to access S3?', ['store access keys on the instance', 'attach an IAM role', 'use the root user', 'make the bucket public'], 1, 'Role via instance profile.') + \
    qx('2. In AWS policy evaluation, an explicit deny…', ['is overridden by allow', 'always wins', 'only applies to root', 'is ignored in SCPs'], 1, 'Deny wins.') + \
    qx('3. Which Azure feature applies MFA based on sign-in risk and location?', ['Conditional Access', 'Azure Advisor', 'Resource locks', 'Blueprints'], 0, 'Conditional Access.') + \
    qx('4. Which AWS service creates and controls encryption keys?', ['AWS KMS', 'AWS Shield', 'Amazon Macie', 'AWS Config'], 0, 'KMS.') + \
    qx('5. Verifying identity is ___; deciding permissions is ___.', ['authorisation; authentication', 'authentication; authorisation', 'auditing; encryption', 'federation; MFA'], 1, 'AuthN then AuthZ.') + \
    qx('6. Encrypting data keys with a master key is called…', ['envelope encryption', 'hashing', 'tokenisation', 'salting'], 0, 'Envelope.')

proj = miniproject('Mini project: TiffinGo identity and encryption design',
    'Redesign TiffinGo’s access and encryption from “admin keys everywhere” to least privilege.',
    ['<b>Inventory</b> every identity: people, pipelines, apps, functions — and their current permissions.',
     '<b>Identity plan:</b> SSO for people (groups → roles), roles/managed identities for workloads, no long-lived keys.',
     '<b>Policies:</b> write the report-reader policy and one for the order API; add an explicit deny for deletes.',
     '<b>Keys:</b> decide which data gets CMKs, who administers vs uses each key, rotation and emergency disable.',
     '<b>Transit:</b> TLS 1.2+ everywhere, managed certificates, HTTPS-only storage.',
     '<b>Verify:</b> run practical steps 1–3 and record the allow/deny and disabled-key results.'],
    'An identity map, two policies, a key plan and lab evidence.', '9.1–9.4 + 8.3 (OIDC).')

assemble_v2(HERE, story_h2='An admin key for a read-only job', hook_html=hk,
    narration='TiffinGo’s nightly reporting job only needed to read one folder of one bucket — yet it ran with an administrator access key that never expired. After Lesson 9.2’s incident, the team asked how to make the next leak harmless.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Identity, access and encryption basics',
    formal='<b>Identity and access management (IAM)</b> establishes who or what is making a request (identity), verifies it (authentication, ideally with MFA or federation) and determines what it may do (authorisation through policies and roles, following least privilege), with all actions audited. <b>Encryption</b> protects data at rest and in transit (and, with confidential computing, in use) using keys managed in key management services, where key policies, rotation and the ability to disable keys add a separate layer of control over who can read data.',
    simple='Make sure every person and app has its own identity, proves who it is, and can only do its own job — and lock the data itself with keys you control.',
    interview=['“Authentication proves identity, authorisation decides permissions. I use SSO with MFA for people, roles or managed identities for workloads, least-privilege policies with default deny, and guard-rails like SCPs.”', '“Encryption at rest is default; I add customer-managed KMS keys for sensitive data — envelope encryption, rotation, separate key admins and users — and enforce TLS 1.2+ in transit.”'],
    terms_rows=[('Principal', 'An identity that can act.'), ('Authentication', 'Prove who you are.'), ('Authorisation', 'Decide what you may do.'), ('MFA', 'Two or more factors.'), ('Least privilege', 'Only needed permissions.'), ('Federation / SSO', 'Trust an external IdP; one login.'), ('CMK', 'Customer-managed key.'), ('Envelope encryption', 'Data keys wrapped by a master key.')],
    exam='CLF-C02: protect root (MFA, no keys), IAM users/groups/roles/policies, least privilege, Identity Center, KMS vs CloudHSM, Secrets Manager, ACM. AZ-900: authentication vs authorisation, Entra ID, MFA, Conditional Access, RBAC, Zero Trust.',
    picture_h2='Four questions and three states of data', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven basics of identity and encryption, one by one', TYPES)],
    how_h2='One request: authenticated, authorised, decrypted', how_intro='How identity and encryption work together on every read.', how_anim=REQ,
    parts_h2='Six controls around identity and keys', parts_html=parts, lv='',
    myth_rows=[('Encryption protects data from anyone with access.', 'Authorised identities decrypt transparently.', 'Type 5.'), ('Allow beats deny if it is more specific.', 'Explicit deny always wins.', 'Step 1 + 3.'), ('Access keys are fine if rotated.', 'Temporary credentials and roles are far safer.', 'Type 1.')],
    extra_secs=[('deep', 'Deep dive', 'Zero Trust, policy evaluation, confidential computing, hygiene checklist', DEEP)],
    clouds_html=clouds, practical_html=prac, mistakes_html=mist, cert_html=cert, project_html=proj,
    can_now=['Explain identities, authentication, MFA, authorisation, federation and SSO.', 'Describe policy evaluation with default and explicit deny.', 'Explain encryption at rest, in transit and envelope encryption with KMS.', 'Build a least-privilege identity, encrypt and disable a key, and enforce TLS on your own account.', 'Design identity and key plans for an application.'],
    next_html='Module 10 — <a href="../../10-cloud-vendors-and-careers/01-aws-vs-azure-vs-google-cloud/">10.1 AWS vs Azure vs Google Cloud</a>.',
    pre='<b>Before you start:</b> 9.1–9.3.')
