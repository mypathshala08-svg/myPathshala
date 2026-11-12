import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from cloudkit import *
sys.path.insert(0, HERE)
from scenes import envelope_scene, two_locks, at_rest_in_transit
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




hk = hook('CityBite’s auditor asked two questions: “Is the sales data encrypted?” and “Who can decrypt it?” The IT head could answer the first. Not the second.',
    'Encryption is easy to switch on in AWS; <b>controlling who can decrypt</b> is the real skill. This lesson explains encryption in transit and at rest, how <b>AWS KMS</b> keys work, why S3 uses <b>envelope encryption</b>, the difference between SSE-S3, SSE-KMS and other options, and how a <b>key policy</b> becomes a second lock next to IAM. On <b>your own</b> account (or in the simulator) you will create a key, encrypt a message, make a bucket encrypt everything with your key, refuse plain-HTTP requests, and watch a disabled key lock the data instantly.',
    ['In transit = HTTPS; at rest = encrypted storage with keys in KMS.', 'SSE-KMS adds a second lock: reading needs kms:Decrypt too.', 'Disable a key and every object it protects becomes unreadable at once.'])

def story_scene():
    o = t(180, 12, '“Who can decrypt it?”', 9, 'ink', bold=True)
    o += box(8, 28, 160, 74, 'red', rx=8) + t(88, 48, 'Default encryption', 8.4, 'ink', bold=True) + t(88, 64, 'encrypted — yes', 7, 'ink2') + t(88, 78, 'who decrypts? anyone', 7, 'ink2') + t(88, 92, 'with S3 read', 7.4, 'ink', bold=True)
    o += box(192, 28, 160, 74, 'green', rx=8) + t(272, 48, 'Own KMS key', 8.4, 'ink', bold=True) + t(272, 64, 'key policy decides', 7, 'ink2') + t(272, 78, 'every use in CloudTrail', 7, 'ink2') + t(272, 92, 'disable = lock all', 7.4, 'ink', bold=True)
    o += t(180, 122, 'Encryption is a switch; key control is a design', 7.6, 'ink', bold=True)
    return o
scene_svg = scene('Left: with default encryption the data is encrypted, but anyone with S3 read permission can read it. Right: with your own KMS key, a key policy decides who can decrypt, every use is logged and disabling the key locks everything.', story_scene(), 'Control the <tspan font-weight="700" class="s-acc">keys</tspan>, control the data.', h=132)
dialogue = '''R> Sir, S3 already encrypts everything since 2023. Aren’t we done?
A> The data is encrypted on disk, yes. But anyone allowed to read the bucket gets it decrypted automatically. The auditor wants to know who controls decryption.
K> So we need our own key?
A> A customer managed key in KMS. Then reading needs two permissions: s3:GetObject and kms:Decrypt. And CloudTrail records every single decrypt.
R> And “encrypted connection only”?
A> That is in transit — a bucket policy that refuses any request not using HTTPS. Let’s see how S3 and KMS work together.'''

picture = (newbie('Encryption turns readable data into scrambled text that only someone with the right <b>key</b> can unscramble. <b>KMS is a bank locker room for keys</b>: the keys never leave the locker; you send things in to be locked or unlocked, and the locker room checks your ID every time and writes it in a register.',
            [('Encryption', 'scrambling data so only key-holders can read it'), ('Key', 'the secret used to scramble/unscramble'), ('At rest', 'data sitting on a disk'), ('In transit', 'data travelling over the network'), ('HTTPS / TLS', 'the padlock in your browser — encryption in transit'), ('KMS', 'AWS service that stores and uses keys safely')]) +
    '  <p>Two places to protect data, one service to manage the keys:</p>\n' + at_rest_in_transit() +
    '\n  <h3>Situation — the auditor’s second question</h3>\n' + two_locks() +
    '\n  <h3>Facts to know</h3>\n' + table(['Fact', 'Detail'], [['S3 default', 'every new object is encrypted with SSE-S3 since January 2023'], ['KMS key types', 'AWS owned, AWS managed (aws/s3, aws/ebs…), customer managed'], ['Customer managed key cost', '≈ USD 1 per key per month (prorated) + per-request charges'], ['Rotation', 'automatic, default yearly; configurable 90–2,560 days; on-demand rotation available'], ['Deletion', 'scheduled with a 7–30 day waiting period — deleted keys make data unrecoverable']], minw=500))

SOLVE = envelope_scene()

def mapfig():
    o = t(320, 16, 'Seven ways to encrypt data on AWS', 11, 'ink', bold=True)
    items = [('1', 'SSE-S3', 'S3-managed keys (default)', 'blue'), ('2', 'SSE-KMS (aws/s3)', 'AWS managed KMS key', 'violet'), ('3', 'SSE-KMS (your key)', 'customer managed key', 'violet'), ('4', 'DSSE-KMS', 'two layers of encryption', 'amber'),
             ('5', 'SSE-C', 'you send the key each time', 'card'), ('6', 'Client-side', 'encrypt before upload', 'green'), ('7', 'In transit (TLS)', 'HTTPS-only policies', 'red')]
    for i, (n, a, b, tn) in enumerate(items):
        x = 12 + (i % 4) * 156; y = 32 + (i // 4) * 84
        o += box(x, y, 148, 70, tn, rx=8) + pin(x + 16, y + 16, n) + t(x + 80, y + 34, a, 8.2, 'ink', bold=True) + t(x + 78, y + 54, b, 6.8, 'ink2')
    o += t(320, 210, '1–6 protect data at rest (who holds the key changes); 7 protects data in transit.', 7.4, 'ink2')
    return o
MAP = bigfig('Map of seven encryption options: SSE-S3, SSE-KMS with the AWS managed key, SSE-KMS with a customer managed key, DSSE-KMS, SSE-C, client-side encryption, encryption in transit with TLS.', mapfig(), h=222)

def en(n, name, tone, d, an, ex, tip, A, use, avoid, plain, how, words, diff, rw, pro):
    return vt(n, name, tone, d, an, ex, tip, '', A, use, avoid, plain, how, words, diff, ['CLF-C02 Domain 2', 'SAA-C03 / Security Specialty', 'C-DAC lab exams'], rw, pro)

A1 = mk(['Upload', 'S3 encrypts', 'S3 decrypts'], ['upload|any object|no settings', 'encrypt|AES-256|S3-owned keys', 'read|S3 permission|only'], ['blue', 'green', 'amber'],
        ['you upload an object', 'S3 encrypts it with keys it manages', 'anyone with S3 read permission gets it decrypted'], [('Upload', 'Nothing to configure.', ''), ('Encrypt', 'AES-256, S3-managed keys.', ''), ('Read', 'S3 permission alone.', '')], 'SSE-S3', 'Free, automatic.', 'SSE-S3', 'Animation: upload; S3 encrypts; S3 decrypts.', 'k1anim')
T1 = en(1, 'SSE-S3 (Amazon S3 managed keys)', 'blue',
    '<b>SSE-S3</b> encrypts each object at rest with AES-256 using keys that S3 creates and manages entirely; it is applied by default to all new objects (since January 2023), costs nothing, and decryption needs only S3 read permission.',
    'A building where every flat’s door locks automatically — but the building manager holds all keys.',
    'TiffinGo’s menu photos: SSE-S3 is enough; they are public on the website anyway.',
    'Tip: “encrypted at rest” requirements are met by SSE-S3; “control who can decrypt” is not.', A1,
    'data needs encryption at rest without key control requirements.', 'auditors require separate key control or key-usage logs.',
    'S3 locks your files automatically with its own keys.',
    [('Default', 'On for new objects.'), ('Algorithm', 'AES-256.'), ('Keys', 'Managed by S3.'), ('Cost', 'Free.'), ('Header', 'x-amz-server-side-encryption: AES256.')],
    [('AES-256', 'standard strong encryption'), ('at rest', 'stored data'), ('SSE', 'server-side encryption')],
    table(['', 'SSE-S3', 'SSE-KMS'], [['Extra permission to read', 'none', 'kms:Decrypt'], ['Key usage log', 'no', 'CloudTrail per use'], ['Cost', 'free', 'KMS charges']], minw=420),
    'Exam: “encrypt at rest with no extra cost or management” → SSE-S3.',
    'head-object shows ServerSideEncryption = AES256 for SSE-S3 objects.')

A2 = mk(['Upload', 'aws/s3 key', 'Decrypt via KMS'], ['upload|SSE-KMS|no key id', 'key|AWS managed|aws/s3', 'read|S3 + KMS|logged'], ['violet', 'amber', 'green'],
        ['request SSE-KMS without naming a key', 'S3 uses the AWS managed key aws/s3', 'decrypt calls are logged; the key policy is AWS’s'], [('Upload', 'SSE-KMS.', ''), ('Key', 'aws/s3 (AWS managed).', ''), ('Log', 'CloudTrail shows KMS use.', '')], 'SSE-KMS (AWS managed key)', 'KMS without your own key.', 'aws/s3', 'Animation: upload; aws/s3 key; decrypt via KMS.', 'k2anim')
T2 = en(2, 'SSE-KMS with the AWS managed key (aws/s3)', 'violet',
    '<b>SSE-KMS with the AWS managed key</b> encrypts objects with data keys from the KMS key <code>aws/s3</code>, which AWS creates and rotates in your account; KMS use is logged, but you cannot edit its key policy, so any principal in the account with S3 access can use it.',
    'A bank locker whose rules are set by the bank — logged, but not customised for you.',
    'A quick step up from SSE-S3 when logs of key use are wanted.',
    'Tip: aws/s3 cannot be shared across accounts — use a customer managed key for cross-account access.', A2,
    'you want KMS logging without managing a key.', 'you need cross-account sharing or a custom key policy.',
    'KMS encryption with a key AWS manages for you.',
    [('Key', 'aws/s3.'), ('Policy', 'AWS-defined.'), ('Rotation', 'Yearly by AWS.'), ('Logs', 'CloudTrail.'), ('Cost', 'Requests only.')],
    [('AWS managed key', 'KMS key created by an AWS service in your account'), ('alias', 'friendly name like aws/s3'), ('rotation', 'new key material over time')],
    table(['', 'AWS managed', 'Customer managed'], [['Edit key policy', 'no', 'yes'], ['Cross-account', 'no', 'yes'], ['Monthly key fee', 'no', '≈ USD 1']], minw=420),
    'Know AWS owned vs AWS managed vs customer managed keys.',
    'Most new designs skip aws/s3 and go straight to a customer managed key or stay with SSE-S3.')

A3 = mk(['Create key', 'Key policy', 'Bucket default'], ['create|symmetric|alias', 'policy|who may|use/admin', 'bucket|SSE-KMS|+ Bucket Key'], ['violet', 'red', 'green'],
        ['create a customer managed symmetric key with an alias', 'write the key policy: administrators and users', 'set it as the bucket’s default encryption with S3 Bucket Keys'], [('Create', 'Symmetric, alias.', ''), ('Policy', 'Admins vs users.', ''), ('Use', 'Bucket default + Bucket Key.', '')], 'SSE-KMS (your key)', 'Two locks you control.', 'CMK', 'Animation: create key; key policy; bucket default.', 'k3anim')
T3 = en(3, 'SSE-KMS with a customer managed key', 'violet',
    '<b>SSE-KMS with a customer managed key</b> uses a KMS key you create and control — its key policy, rotation, enable/disable and deletion — so reading objects requires S3 permission <i>and</i> kms:Decrypt on the key; every use is logged, and <b>S3 Bucket Keys</b> reduce KMS request costs by up to 99%.',
    'Your own locker in the bank with your own access register: the bank opens it only for people on your list.',
    'CityBite’s sales bucket encrypted with alias/citybite-sales; only the dashboard role and accountants may decrypt.',
    'Tip: separate key administrators (manage the key) from key users (encrypt/decrypt) in the key policy.', A3,
    'auditors require key control, separation of duties or cross-account sharing.', 'you will forget the key and delete it — deleted keys mean lost data.',
    'Encryption with your own key and your own list of who may unlock.',
    [('Create', 'aws kms create-key.'), ('Alias', 'alias/name.'), ('Key policy', 'Root + admins + users.'), ('Bucket', 'Default SSE-KMS.'), ('Bucket Key', 'Fewer KMS calls.')],
    [('customer managed key', 'KMS key you create and control'), ('key policy', 'resource policy on the key — required'), ('S3 Bucket Key', 'bucket-level data key to cut KMS calls')],
    table(['Permission', 'Who'], [['kms:Create*, Enable/Disable, ScheduleKeyDeletion, PutKeyPolicy', 'key administrators'], ['kms:Encrypt, Decrypt, GenerateDataKey*', 'key users (apps, roles)'], ['kms:CreateGrant', 'services acting for users']], minw=460),
    'Lab exams: “data must be encrypted when stored” — SSE-S3 meets it; SSE-KMS with your key shows deeper understanding.',
    'The default key policy gives the account root full access and lets IAM policies grant use — keep that statement or you can lock yourself out.')

A4 = mk(['Layer 1', 'Layer 2', 'Two keys'], ['layer 1|KMS data key|AES-256', 'layer 2|second encryption|different key', 'result|dual-layer|compliance'], ['amber', 'violet', 'green'],
        ['the object is encrypted once', 'and again with a second, independent layer', 'meets rules that demand two layers'], [('First', 'Layer one.', ''), ('Second', 'Independent layer.', ''), ('Use', 'Strict compliance.', '')], 'DSSE-KMS', 'Belt and braces.', 'DSSE', 'Animation: layer 1; layer 2; two keys.', 'k4anim')
T4 = en(4, 'DSSE-KMS (dual-layer server-side encryption)', 'amber',
    '<b>DSSE-KMS</b> applies two independent layers of AES-256 encryption to each object using KMS keys, for workloads whose compliance rules require multiple layers of encryption at rest; it costs more than SSE-KMS.',
    'A document in a locked box inside a second locked safe.',
    'Defence and some government workloads with multi-layer mandates.',
    'Tip: choose it only when a rule demands two layers — otherwise SSE-KMS is enough.', A4,
    'a regulation explicitly requires dual-layer encryption.', 'general workloads — extra cost without benefit.',
    'S3 encrypts your file twice.',
    [('Header', 'aws:kms:dsse.'), ('Keys', 'KMS.'), ('Layers', 'Two.'), ('Cost', 'Higher.'), ('Use', 'Compliance only.')],
    [('dual-layer', 'two independent encryptions'), ('mandate', 'a rule you must follow'), ('aws:kms:dsse', 'the encryption type value')],
    table(['', 'SSE-KMS', 'DSSE-KMS'], [['Layers', 'one', 'two'], ['Typical use', 'most regulated data', 'explicit multi-layer mandates']], minw=420),
    'Rare in CLF; appears in security discussions.',
    'Check that downstream tools (Athena, replication) support DSSE objects before switching.')

A5 = mk(['You hold key', 'Send with request', 'S3 forgets it'], ['key|in your app|or HSM', 'send|with every|PUT and GET', 'S3|uses then|discards key'], ['card', 'amber', 'red'],
        ['you keep the key yourself', 'you send it with every upload and download', 'S3 uses it and never stores it'], [('Hold', 'Your key.', ''), ('Send', 'Headers on each request (HTTPS).', ''), ('Lose it', 'Data gone.', '')], 'SSE-C', 'You hold the key.', 'SSE-C', 'Animation: you hold key; send with request; S3 forgets it.', 'k5anim')
T5 = en(5, 'SSE-C (customer-provided keys)', 'card',
    '<b>SSE-C</b> lets you supply your own encryption key in request headers on every PUT and GET; S3 encrypts/decrypts with it and stores only a salted hash to validate later requests — if you lose the key, the data is unrecoverable.',
    'You bring your own padlock and keep the only key; the warehouse locks and unlocks only when you hand it over.',
    'An organisation whose policy is that keys never rest in any cloud service.',
    'Tip: many AWS features (some replication and console views) do not work with SSE-C objects — test first.', A5,
    'you must keep keys entirely outside AWS.', 'teams that may lose keys, or need the console to read objects.',
    'You give S3 the key every time; S3 never keeps it.',
    [('Generate', 'Your key.'), ('PUT', 'Key in headers.'), ('GET', 'Same key again.'), ('HTTPS', 'Required.'), ('Store', 'Yourself.')],
    [('customer-provided key', 'your own key sent per request'), ('salted hash', 'fingerprint to check the key, not the key'), ('key loss', 'permanent data loss')],
    table(['', 'SSE-KMS', 'SSE-C'], [['Who stores the key', 'KMS', 'you'], ['Lose key =', 'impossible by mistake (waiting period)', 'data lost']], minw=420),
    'Exam: “company must manage keys outside AWS” → SSE-C or client-side encryption.',
    'If you need your own key material inside KMS instead, look at imported key material or external key stores.')

A6 = mk(['Encrypt locally', 'Upload ciphertext', 'AWS never sees plaintext'], ['encrypt|in your app|SDK/Encryption SDK', 'upload|ciphertext|any service', 'AWS|stores only|scrambled data'], ['green', 'amber', 'blue'],
        ['encrypt the data in your application first', 'upload only the ciphertext', 'AWS never sees the plaintext'], [('Encrypt', 'AWS Encryption SDK / S3 encryption client.', ''), ('Upload', 'Ciphertext only.', ''), ('Decrypt', 'In your app.', '')], 'Client-side', 'Encrypt before it leaves you.', 'Client-side', 'Animation: encrypt locally; upload ciphertext; AWS never sees plaintext.', 'k6anim')
T6 = en(6, 'Client-side encryption', 'green',
    '<b>Client-side encryption</b> encrypts data inside your application before sending it to AWS (for example with the AWS Encryption SDK or the Amazon S3 Encryption Client, often with keys from KMS), so storage services hold only ciphertext and never the plaintext.',
    'Writing your letter in a secret code before posting it — the post office only carries gibberish.',
    'A hospital app encrypts scan reports on the device before upload.',
    'Tip: you own the complexity — key handling, rotation and search on encrypted data are your problem.', A6,
    'the provider must never see plaintext.', 'you need S3 Select/Athena on the data — they cannot read ciphertext.',
    'Scramble the data yourself before it goes to the cloud.',
    [('Library', 'Encryption SDK.'), ('Key', 'KMS or your own.'), ('Encrypt', 'Before upload.'), ('Store', 'Ciphertext.'), ('Decrypt', 'In app.')],
    [('Encryption SDK', 'AWS library for envelope encryption'), ('ciphertext', 'scrambled data'), ('plaintext', 'readable data')],
    table(['', 'Server-side', 'Client-side'], [['Who encrypts', 'AWS service', 'your app'], ['Service can read', 'yes (when authorised)', 'no']], minw=420),
    'Know the difference: server-side vs client-side.',
    'Combine with KMS so keys still get policies, rotation and logs.')

A7 = mk(['Client', 'TLS', 'Deny plain HTTP'], ['client|browser, CLI|SDK', 'TLS|encrypted|channel', 'policy|aws:SecureTransport|false → Deny'], ['red', 'amber', 'green'],
        ['the client connects to AWS', 'TLS encrypts the connection (HTTPS)', 'a bucket policy refuses any request not using TLS'], [('Client', 'Connects.', ''), ('TLS', 'Encrypted channel.', ''), ('Enforce', 'Deny aws:SecureTransport=false.', '')], 'In transit', 'Padlock on the wire.', 'TLS', 'Animation: client; TLS; deny plain HTTP.', 'k7anim')
T7 = en(7, 'Encryption in transit (TLS) and HTTPS-only policies', 'red',
    '<b>Encryption in transit</b> protects data moving between clients and AWS (and between services) using TLS; AWS endpoints support HTTPS, and a bucket or resource policy that denies requests where <code>aws:SecureTransport</code> is false enforces it — you can also require a minimum TLS version with <code>s3:TlsVersion</code>.',
    'A sealed envelope instead of a postcard: the postman can carry it but not read it.',
    'CityBite R1: “any request that does not use HTTPS must be refused — prove it”.',
    'Tip: prove it with <code>--endpoint-url http://s3.ap-south-1.amazonaws.com</code> → AccessDenied.', A7,
    'always — enforce HTTPS-only on sensitive buckets.', 'assuming HTTPS is enforced because the CLI uses it by default.',
    'The padlock that protects data while it travels.',
    [('TLS', 'Encrypted channel.'), ('Policy', 'Deny SecureTransport=false.'), ('Version', 's3:TlsVersion ≥ 1.2.'), ('Test', 'http endpoint → denied.'), ('Certificates', 'ACM for your sites.')],
    [('TLS', 'Transport Layer Security'), ('HTTPS', 'HTTP over TLS'), ('ACM', 'AWS Certificate Manager')],
    table(['', 'In transit', 'At rest'], [['Protects', 'data on the network', 'data on disk'], ['AWS tool', 'TLS, ACM, policies', 'SSE-S3/KMS, EBS/RDS encryption']], minw=420),
    'Exam: “ensure all S3 access uses HTTPS” → bucket policy with aws:SecureTransport.',
    'Inside a VPC, traffic between your own services is your responsibility — use TLS there too.')

SUMMARY = table(['#', 'Option', 'Who holds the key', 'Use when'], [
    ['1', 'SSE-S3', 'S3', 'default, free'], ['2', 'SSE-KMS aws/s3', 'KMS (AWS managed)', 'logs without own key'], ['3', 'SSE-KMS customer key', 'KMS (you control)', 'audits, separation of duties'],
    ['4', 'DSSE-KMS', 'KMS, two layers', 'multi-layer mandates'], ['5', 'SSE-C', 'you (per request)', 'keys must stay outside AWS'], ['6', 'Client-side', 'you / KMS', 'AWS must never see plaintext'], ['7', 'TLS in transit', 'TLS sessions', 'always']], minw=560)

TYPES = ('  <p>Seven ways to encrypt data on AWS, each in the same pattern: definition, plain words, analogy, internal steps, animation, differences, real-world example and an expert tip.</p>\n'
         + challenge(['Which option makes reading need kms:Decrypt as well as s3:GetObject?', 'How do you prove HTTP requests are refused?', 'What happens if you lose an SSE-C key?'], 'types 3, 7 and 5') + MAP
         + jump(['SSE-S3', 'aws/s3', 'Your key', 'DSSE', 'SSE-C', 'Client-side', 'TLS']) + T1 + T2 + T3 + T4 + T5 + T6 + T7
         + '\n  <h3 style="margin-top:34px">All seven side by side</h3>\n' + SUMMARY)

parts = wwu([
    ('KMS key', 'symmetric AES-256 key inside KMS (HSM-backed).', 'Never leaves KMS.', 'alias/citybite-sales.'),
    ('Key policy', 'resource policy on the key — mandatory.', 'Decides who may administer/use.', 'admins vs users.'),
    ('Data keys', 'per-object keys from GenerateDataKey.', 'Envelope encryption, fast.', 'stored encrypted with the object.'),
    ('Rotation', 'new key material on a schedule.', 'Limits exposure; old data still readable.', 'yearly default.'),
    ('Enable / disable / delete', 'key states.', 'Instant lock; deletion is permanent.', '7–30 day waiting period.'),
    ('Logs', 'every API use in CloudTrail.', 'Answers “who decrypted?”.', 'Decrypt events per object read.')])

DEEP = ('  <h3>A key policy with separation of duties</h3>\n' + code('json', 'Key policy for alias/citybite-sales',
 '{\n  "Version": "2012-10-17",\n  "Statement": [\n    {"Sid": "AccountRootFullAccess", "Effect": "Allow",\n     "Principal": {"AWS": "arn:aws:iam::111122223333:root"}, "Action": "kms:*", "Resource": "*"},\n    {"Sid": "KeyAdministrators", "Effect": "Allow",\n     "Principal": {"AWS": "arn:aws:iam::111122223333:role/SecurityAdmin"},\n     "Action": ["kms:Create*", "kms:Describe*", "kms:Enable*", "kms:List*", "kms:Put*", "kms:Update*",\n                "kms:Revoke*", "kms:Disable*", "kms:Get*", "kms:Delete*", "kms:TagResource",\n                "kms:UntagResource", "kms:ScheduleKeyDeletion", "kms:CancelKeyDeletion"],\n     "Resource": "*"},\n    {"Sid": "KeyUsers", "Effect": "Allow",\n     "Principal": {"AWS": ["arn:aws:iam::111122223333:role/DashboardRole",\n                           "arn:aws:iam::111122223333:role/Accountants"]},\n     "Action": ["kms:Encrypt", "kms:Decrypt", "kms:ReEncrypt*", "kms:GenerateDataKey*", "kms:DescribeKey"],\n     "Resource": "*"}\n  ]\n}') +
 '  <p>Administrators can manage the key but not decrypt data; users can decrypt but not delete or change the key. <code>"Resource": "*"</code> in a key policy means “this key”.</p>\n'
 '  <h3>HTTPS-only bucket policy (CityBite R1)</h3>\n' + code('json', 'Deny any request without TLS', '{\n  "Version": "2012-10-17",\n  "Statement": [{\n    "Sid": "DenyInsecureTransport", "Effect": "Deny", "Principal": "*", "Action": "s3:*",\n    "Resource": ["arn:aws:s3:::citybite-sales", "arn:aws:s3:::citybite-sales/*"],\n    "Condition": {"Bool": {"aws:SecureTransport": "false"}}\n  }]\n}'))

clouds = vendor_tabs('<p><b>AWS:</b> KMS (customer managed keys, key policies, rotation), SSE-S3/SSE-KMS/DSSE-KMS/SSE-C, CloudHSM, EBS/RDS encryption, ACM for TLS.</p>',
    '<p><b>Azure:</b> Storage Service Encryption with Microsoft-managed or customer-managed keys in Key Vault / Managed HSM; “secure transfer required” setting for HTTPS only.</p>',
    '<p><b>Google Cloud:</b> default encryption at rest; CMEK with Cloud KMS; CSEK (customer-supplied); Cloud HSM and External Key Manager.</p>') + \
    cloud3([['Key service', 'AWS KMS', 'Azure Key Vault', 'Cloud KMS'], ['Your own keys for storage', 'SSE-KMS (customer managed)', 'customer-managed keys', 'CMEK'], ['Customer-supplied per request', 'SSE-C', 'customer-provided keys (Blob)', 'CSEK'], ['HTTPS only', 'aws:SecureTransport policy', 'secure transfer required', 'default HTTPS endpoints']])

MOCKA.extend([
 mock('aws', ['KMS', 'Customer managed keys', 'Create key'], ['Configure key', 'Labels', 'Key administrators', 'Key usage'], 'Configure key', [('Key type', '( ) Symmetric'), ('Key usage', 'Encrypt and decrypt'), ('Alias', 'citybite-sales')], 'Finish'),
 mock('aws', ['S3', 'citybite-sales-…', 'Properties', 'Default encryption'], ['Objects', 'Properties', 'Permissions'], 'Properties', [('Encryption type', 'SSE-KMS'), ('AWS KMS key', 'alias/citybite-sales'), ('Bucket Key', '[x] Enable')], 'Save changes'),
 mock('aws', ['KMS', 'Customer managed keys', 'citybite-sales'], ['General configuration', 'Key policy', 'Key rotation'], 'General configuration', [('Status', 'Enabled'), ('Key actions', '▾ Disable · Schedule key deletion')], 'Disable'),
])

STEP1 = astep('1 · Create a KMS key and encrypt a message',
    ['[[KMS]] → [[Customer managed keys]] → [[Create key]] → Symmetric, Encrypt and decrypt → alias <code>citybite-sales</code> → you as administrator and user → [[Finish]].'],
    "KID=$(aws kms create-key --description 'CityBite sales lab' --query KeyMetadata.KeyId --output text)\naws kms create-alias --alias-name alias/citybite-sales --target-key-id $KID\necho 'Outlet 3 sold 120 thalis' > secret.txt\naws kms encrypt --key-id alias/citybite-sales --plaintext fileb://secret.txt --query CiphertextBlob --output text | base64 -d > secret.enc\nhead -c 60 secret.enc | od -c | head -3\naws kms decrypt --ciphertext-blob fileb://secret.enc --query Plaintext --output text | base64 -d\naws kms get-key-rotation-status --key-id $KID",
    'unreadable bytes for <code>secret.enc</code>, then the original sentence after decrypt (no key id needed — the ciphertext says which key), and <code>KeyRotationEnabled: false</code> (turn it on with enable-key-rotation).',
    'Direct KMS encrypt works only for up to 4 KB; larger data uses data keys (envelope encryption) — exactly what S3 does for you.')

STEP2 = astep('2 · Bucket that encrypts with your key and refuses plain HTTP',
    ['[[S3]] → create <code>citybite-sales-ACCOUNTID</code> → [[Properties]] → [[Default encryption]] → SSE-KMS, key <code>alias/citybite-sales</code>, Bucket Key enabled.', '[[Permissions]] → [[Bucket policy]] → paste the HTTPS-only policy from the Deep dive (change the bucket name).'],
    "ACC=$(aws sts get-caller-identity --query Account --output text); B=citybite-sales-$ACC\naws s3 mb s3://$B --region ap-south-1\naws s3api put-bucket-encryption --bucket $B --server-side-encryption-configuration \\\n  '{\"Rules\":[{\"ApplyServerSideEncryptionByDefault\":{\"SSEAlgorithm\":\"aws:kms\",\"KMSMasterKeyID\":\"alias/citybite-sales\"},\"BucketKeyEnabled\":true}]}'\naws s3api put-bucket-policy --bucket $B --policy \"{\\\"Version\\\":\\\"2012-10-17\\\",\\\"Statement\\\":[{\\\"Effect\\\":\\\"Deny\\\",\\\"Principal\\\":\\\"*\\\",\\\"Action\\\":\\\"s3:*\\\",\\\"Resource\\\":[\\\"arn:aws:s3:::$B\\\",\\\"arn:aws:s3:::$B/*\\\"],\\\"Condition\\\":{\\\"Bool\\\":{\\\"aws:SecureTransport\\\":\\\"false\\\"}}}]}\"\nprintf 'outlet,item,amount\\nAndheri,thali,120\\n' > day1.csv\naws s3 cp day1.csv s3://$B/sales/day1.csv\naws s3api head-object --bucket $B --key sales/day1.csv --query '[ServerSideEncryption,SSEKMSKeyId,BucketKeyEnabled]' --output text\naws s3 cp s3://$B/sales/day1.csv - --endpoint-url http://s3.ap-south-1.amazonaws.com",
    '<code>aws:kms arn:aws:kms:ap-south-1:…:key/… True</code> — encrypted with your key — and then <code>An error occurred (AccessDenied)</code> for the plain-HTTP request: proof that non-HTTPS access is refused.',
    'The same command without --endpoint-url (HTTPS) works — keep both outputs as evidence for “any request without HTTPS must be refused”.')

STEP3 = astep('3 · Disable the key — watch everything lock',
    ['[[KMS]] → key → [[Key actions]] → [[Disable]] → try to download <code>day1.csv</code> in the S3 console → error → [[Enable]] again.'],
    "aws kms disable-key --key-id $KID\naws s3 cp s3://$B/sales/day1.csv - 2>&1 | tail -1\naws kms enable-key --key-id $KID\naws s3 cp s3://$B/sales/day1.csv -\naws kms enable-key-rotation --key-id $KID\naws ec2 get-ebs-encryption-by-default --region ap-south-1\naws ec2 enable-ebs-encryption-by-default --region ap-south-1",
    'a KMS error (<code>KMS.DisabledException</code>) while disabled, the CSV again after enabling, rotation turned on, and EBS encryption by default switched on for the Region (new disks are encrypted automatically).',
    'Disabling a key is an emergency brake: every object encrypted with it becomes unreadable instantly, without touching the data.')

prac = practical(AWS_INTRO + ' A customer managed key costs about USD 1 per month (prorated); schedule its deletion at the end. Everything else is free-tier.', [AWS_SETUP, STEP1, STEP2, STEP3],
    cleanup="<code>aws s3 rb s3://$B --force; aws kms delete-alias --alias-name alias/citybite-sales; aws kms schedule-key-deletion --key-id $KID --pending-window-in-days 7</code>. Keep EBS encryption by default on — it is a good permanent setting. Delete <code>secret.txt</code>, <code>secret.enc</code>, <code>day1.csv</code>.")

mist = mistakes([
    ['Thinking SSE-S3 answers “who can decrypt?”.', 'Encrypted = controlled.', 'Use SSE-KMS with a customer managed key + key policy.'],
    ['Removing the root statement from a key policy.', 'Trying to tighten.', 'Keep the account root statement or you may lock yourself out.'],
    ['Deleting a key “to clean up”.', 'Tidy habits.', 'Deleted keys = unreadable data; disable first, delete only when sure.'],
    ['Huge KMS bills from S3.', 'One KMS call per object.', 'Enable S3 Bucket Keys.'],
    ['Assuming HTTPS is enforced.', 'CLI uses HTTPS by default.', 'Add the aws:SecureTransport Deny and prove it.'],
    ['Granting s3:GetObject and wondering why reads fail.', 'Forgot the key.', 'Grant kms:Decrypt on the key (key policy or IAM).']])

cert = table(['Exam / syllabus', 'What is asked'], [['AWS CLF-C02', 'Encryption at rest and in transit; KMS; shared responsibility for encryption (Domain 2).'], ['SAA-C03 / Security Specialty', 'SSE options, key policies, envelope encryption, Bucket Keys, cross-account keys, rotation.'], ['C-DAC lab exams', '“Encrypted when stored” and “refuse non-HTTPS — prove it”; encrypted server disks.']], minw=560) + \
    '\n  <h3>Try exam-style questions</h3>\n' + qx('Which gives separate control over who can decrypt S3 data?', ['SSE-S3', 'SSE-KMS with a customer managed key', 'S3 versioning', 'S3 Transfer Acceleration'], 1, 'Key policy.') + \
    qx('Enforce HTTPS for all S3 requests to a bucket?', ['bucket policy denying aws:SecureTransport false', 'enable versioning', 'SSE-S3', 'Block Public Access'], 0, 'SecureTransport.') + \
    qx('Reduce KMS request costs for an SSE-KMS bucket?', ['S3 Bucket Keys', 'Glacier', 'Requester Pays', 'CloudFront'], 0, 'Bucket Keys.') + \
    qx('What happens to data when its KMS key is disabled?', ['it is deleted', 'it cannot be decrypted until the key is enabled', 'it becomes public', 'nothing'], 1, 'Locked, not deleted.')

from deep_v3 import HOOD, ROLES, DOMAINS, PRO, PROJ, SIM, LADDER

assemble_v2(HERE, story_h2='“Who can decrypt the sales data?”', hook_html=hk,
    narration='CityBite’s auditor asked whether sales data was encrypted and who could decrypt it. Default encryption answered the first; only a customer managed KMS key with a key policy and CloudTrail logs answered the second.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Encryption with KMS',
    formal='<b>AWS Key Management Service (KMS)</b> creates and controls cryptographic keys in hardware security modules that never export them, and performs encryption, decryption and data-key generation under <b>key policies</b> and IAM, logging every use in CloudTrail; AWS services such as S3, EBS and RDS use KMS keys through <b>envelope encryption</b> to protect data at rest, while TLS protects data in transit.',
    simple='KMS keeps the keys locked away and only uses them for people and services on the key’s list; S3 and other services use those keys to lock your data on disk.',
    interview=['“I encrypt at rest with SSE-KMS using a customer managed key whose key policy separates administrators from users, enable Bucket Keys for cost, and enforce TLS with an aws:SecureTransport Deny.”', '“S3 uses envelope encryption: a per-object data key encrypts the data, and the KMS key encrypts the data key — the KMS key never leaves KMS.”'],
    terms_rows=[('KMS key', 'Key held inside KMS.'), ('Customer managed key', 'KMS key you control.'), ('Key policy', 'Mandatory resource policy on a key.'), ('Data key', 'Per-object key from GenerateDataKey.'), ('Envelope encryption', 'Data key encrypts data; KMS key encrypts data key.'), ('SSE-S3 / SSE-KMS', 'S3 encryption options.'), ('Bucket Key', 'Cuts KMS calls for S3.'), ('TLS', 'Encryption in transit.')],
    exam='CLF-C02 asks about encryption at rest/in transit and KMS; SAA/Security test SSE options, key policies and HTTPS-only policies.',
    picture_h2='In transit, at rest, and who holds the keys', picture_html=picture,
    after_picture=[('types', 'Types, one by one', 'Seven ways to encrypt data, one by one', TYPES)],
    how_h2='Envelope encryption, step by step', how_intro='One file into S3 with SSE-KMS, and two people trying to read it.', how_anim=SOLVE,
    parts_h2='Six parts of a KMS key', parts_html=parts, lv='',
    myth_rows=[('Encrypted data is safe from anyone with S3 access.', 'With SSE-S3, S3 permission is enough to read.', 'Situation.'), ('KMS sends your key to S3.', 'The KMS key never leaves KMS; only data keys do.', 'Animation step 3.'), ('Deleting a key is a harmless cleanup.', 'It makes all data under it unreadable forever.', 'Mistakes.')],
    extra_secs=[('ladder', 'Learn at your level', 'From curious beginner to expert — pick your level', LADDER), ('deep', 'Deep dive', 'Key policy with separation of duties; HTTPS-only bucket policy', DEEP), ('hood', 'Under the hood', 'HSMs, data keys, grants, rotation, multi-Region keys, quotas', HOOD), ('roles', 'By role', 'Encryption work for developers, data, ML, DevOps and security', ROLES), ('domains', 'By domain', 'Encryption requirements by industry', DOMAINS), ('pro', 'For working professionals', 'Costs, errors, cheat sheet, checklist', PRO)],
    clouds_html=clouds, practical_html=prac + '\n  <h3 id="simulator">Practice without an account: simulator</h3>\n  <p>Create the key, encrypt the bucket, prove HTTPS-only and lock everything with one command.</p>\n' + SIM, mistakes_html=mist, cert_html=cert, project_html=PROJ,
    can_now=['Explain encryption in transit vs at rest.', 'Choose between SSE-S3, SSE-KMS, DSSE-KMS, SSE-C and client-side.', 'Create a KMS key with a key policy that separates duties.', 'Make a bucket encrypt with your key and refuse plain HTTP — and prove it.', 'Use disable/enable, rotation and EBS default encryption.'],
    next_html='<a href="../05-security-best-practices/">2.5 Security best practices</a>.',
    pre='<b>Before you start:</b> Lessons 2.1–2.3.')
