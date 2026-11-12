from cloudkit import *

def envelope_scene():
    st = sa_people(16, 40, 1) + t(62, 76, 'Head office app', 7.4, 'ink', bold=True)
    st += box(12, 92, 120, 44, 'card', rx=8) + sa_icon('file', 20, 100, 1.0, 'blue') + t(84, 112, 'sales-01.csv', 7.6, 'ink', bold=True) + t(84, 126, 'readable', 6.8, 'ink2')
    st += sa_building(150, 14, 260, 300, 'Amazon S3', 'green')
    st += sa_building(430, 14, 196, 300, 'AWS KMS', 'violet')
    st += box(452, 44, 152, 70, 'violet', rx=10) + sa_icon('key', 460, 52, 1.2, 'violet') + t(540, 70, 'KMS key', 8.6, 'ink', bold=True) + t(540, 86, 'alias/citybite-sales', 6.8, 'ink2') + t(540, 100, 'never leaves KMS (HSM)', 6.6, 'ink2')
    st += box(452, 140, 152, 60, 'red', rx=8) + t(528, 160, 'Key policy', 8.4, 'ink', bold=True) + t(528, 176, 'who may Encrypt/Decrypt', 6.8, 'ink2') + t(528, 190, 'checked on every call', 6.6, 'ink2')
    st += box(172, 220, 216, 76, 'card', rx=8) + t(280, 238, 'Stored object', 8.4, 'ink', bold=True)
    lock = lambda x, y, col='green': sa_icon('lock', x, y, 1.0, col)
    f1 = sa_flow('M132 114 C160 110 180 100 200 100', 'blue', 1.2, 3, 4, 'PutObject', 166, 88) + sa_badge(396, 302, 1) + sa_note(280, 120, 220, ['Upload over HTTPS (encrypted in transit)', 'S3 must now encrypt it at rest'], 'blue')
    f2 = sa_flow('M300 70 C360 60 420 70 452 76', 'violet', 1.2, 3, 4, 'GenerateDataKey', 380, 56) + sa_badge(396, 302, 2, 'violet') + sa_note(280, 120, 220, ['S3 asks KMS for a fresh data key', 'KMS checks the key policy first'], 'violet')
    f3 = sa_flow('M452 96 C420 110 380 120 350 130', 'violet', 1.2, 2) + '<g class="sa-pop">' + box(196, 100, 140, 54, 'amber', rx=8) + t(266, 118, 'data key (plaintext)', 7.4, 'ink', bold=True) + t(266, 132, '+ same key encrypted', 7, 'ink2') + t(266, 146, 'by the KMS key', 7, 'ink2') + '</g>' + sa_badge(396, 302, 3, 'amber') + sa_note(280, 190, 220, ['KMS returns the data key twice:', 'plain (to use) and encrypted (to store)'], 'saffron')
    f4 = '<g class="sa-pop">' + box(184, 236, 92, 50, 'green', rx=6) + lock(192, 244) + t(240, 266, 'ciphertext', 7.4, 'ink', bold=True) + box(286, 236, 92, 50, 'violet', rx=6) + sa_icon('key', 294, 244, 1.0, 'violet') + t(342, 262, 'encrypted', 7, 'ink', bold=True) + t(342, 274, 'data key', 7, 'ink') + '</g>' + sa_cross(266, 120, 9) + t(266, 104, 'plain data key erased', 7.2, 'ink', bold=True) + sa_badge(396, 302, 4, 'green') + sa_note(512, 236, 190, ['Envelope encryption:', 'data locked with data key,', 'data key locked with KMS key'], 'green')
    stored = box(184, 236, 92, 50, 'green', rx=6) + lock(192, 244) + t(240, 266, 'ciphertext', 7.4, 'ink', bold=True) + box(286, 236, 92, 50, 'violet', rx=6) + sa_icon('key', 294, 244, 1.0, 'violet') + t(342, 262, 'encrypted', 7, 'ink', bold=True) + t(342, 274, 'data key', 7, 'ink')
    f5 = stored + sa_people(16, 170, 1, 'green') + t(50, 206, 'accountant', 7.4, 'ink', bold=True) + sa_flow('M330 262 C400 230 440 200 452 180', 'violet', 1.2, 3, 4, 'Decrypt', 410, 214) + sa_tick(612, 150, 9) + sa_flow('M184 262 C120 250 60 230 40 210', 'green', 1.4, 3) + sa_badge(396, 302, 5, 'green') + sa_note(280, 120, 220, ['Download: S3 asks KMS to decrypt the', 'data key — key policy allows → file returned'], 'green')
    f6 = stored + sa_people(16, 170, 1, 'red') + t(74, 206, 'intern (s3:GetObject only)', 7.2, 'ink', bold=True) + sa_flow('M330 262 C400 230 440 200 452 180', 'red', 1.2, 3) + sa_cross(612, 150, 10) + sa_pill(100, 236, 'AccessDenied (kms:Decrypt)', 'red', 170) + sa_badge(396, 302, 6, 'red') + sa_note(280, 120, 220, ['S3 permission is not enough:', 'no kms:Decrypt → no data. Two locks.'], 'red')
    return scene_anim('Envelope encryption: what happens when S3 encrypts with KMS', 'Follow one sales file into S3 with SSE-KMS, then two people trying to read it.', 'SSE-KMS',
        'Animation: app uploads over HTTPS; S3 asks KMS for a data key; KMS returns plaintext and encrypted data keys; S3 encrypts the file, stores ciphertext with the encrypted data key and erases the plaintext key; an accountant with kms:Decrypt downloads successfully; an intern with only s3:GetObject is denied by KMS.',
        st, [(f1, 'Step 1 · Upload over HTTPS', 'the file travels encrypted in transit (TLS). At rest, the bucket’s default encryption says: SSE-KMS with key alias/citybite-sales.'),
             (f2, 'Step 2 · S3 asks KMS for a data key', 'GenerateDataKey for that KMS key. KMS first checks the key policy: may this request (via S3, for this account) use the key?'),
             (f3, 'Step 3 · Two copies of one data key', 'KMS returns a 256-bit data key in plaintext and the same key encrypted under the KMS key. The KMS key itself never leaves KMS.'),
             (f4, 'Step 4 · Encrypt, store, forget', 'S3 encrypts the file with the plaintext data key (AES-256-GCM), stores the ciphertext next to the encrypted data key and erases the plaintext key from memory.'),
             (f5, 'Step 5 · Authorised download', 'the accountant’s GetObject makes S3 send the encrypted data key to KMS Decrypt; the key policy/IAM allow kms:Decrypt, so S3 can decrypt and return the file.'),
             (f6, 'Step 6 · Two locks', 'an intern with s3:GetObject but no kms:Decrypt gets AccessDenied — reading encrypted data needs permission on the bucket and on the key.')], hid='kmsflow')

def two_locks():
    o = t(320, 16, 'SSE-S3 vs SSE-KMS with your own key: who can read?', 11, 'ink', bold=True)
    o += sa_building(12, 28, 300, 210, 'SSE-S3 (default)', 'blue') + sa_building(328, 28, 300, 210, 'SSE-KMS (customer managed key)', 'violet')
    o += sa_icon('bucket', 30, 50, 1.4, 'blue') + t(170, 64, 'one lock: S3 permission', 8.4, 'ink', bold=True)
    o += ''.join(t(26, 96 + i * 16, s, 7.6, 'ink2', anchor='start') for i, s in enumerate(['✓ encrypted at rest automatically, free', '✓ AWS manages the keys completely', '✘ anyone with s3:GetObject reads the data', '✘ no separate key audit trail per object']))
    o += sa_icon('bucket', 346, 50, 1.4, 'violet') + sa_icon('key', 380, 50, 1.4, 'violet') + t(500, 64, 'two locks: S3 + KMS key', 8.4, 'ink', bold=True)
    o += ''.join(t(342, 96 + i * 16, s, 7.6, 'ink2', anchor='start') for i, s in enumerate(['✓ reading needs s3:GetObject AND kms:Decrypt', '✓ key policy you control; disable = instant lock', '✓ every Decrypt logged in CloudTrail', '✘ ≈ USD 1/month per key + request charges']))
    o += t(320, 228, 'Auditors usually ask for the right column: separate control of keys and a log of every use.', 7.8, 'ink', bold=True)
    return bigfig('Comparison: SSE-S3 encrypts automatically for free but anyone with S3 read permission reads the data; SSE-KMS with a customer managed key needs both S3 permission and KMS decrypt permission, can be disabled instantly and logs every use.', o, h=244)

def at_rest_in_transit():
    o = t(320, 16, 'Encryption in transit and at rest', 11, 'ink', bold=True)
    o += sa_people(30, 70, 1) + t(36, 104, 'browser / app', 7.6, 'ink', bold=True)
    o += f'<path d="M60 76 L250 76" style="stroke:#2F7D5B;stroke-width:4"/>' + sa_icon('lock', 140, 50, 1.0, 'green') + t(160, 100, 'in transit: HTTPS / TLS', 8, 'ink', bold=True) + t(160, 114, 'nobody on the network can read it', 7, 'ink2')
    o += box(252, 40, 130, 70, 'blue', rx=8) + t(317, 70, 'AWS service', 8.6, 'ink', bold=True) + t(317, 86, 'S3, RDS, EBS…', 7, 'ink2')
    o += f'<path d="M382 76 L470 76" style="stroke:#7C4DDB;stroke-width:4"/>'
    o += box(472, 40, 150, 70, 'violet', rx=8) + sa_icon('disk', 480, 48, 1.0, 'violet') + t(552, 70, 'disk / storage', 8.4, 'ink', bold=True) + t(552, 86, 'at rest: AES-256', 7, 'ink2') + t(552, 100, 'keys in KMS', 7, 'ink2')
    o += t(320, 146, 'Enforce both: a bucket policy that denies aws:SecureTransport = false, and default encryption (SSE-S3 or SSE-KMS).', 7.6, 'ink2')
    o += t(320, 164, 'Prove HTTPS-only: the same CLI download with --endpoint-url http://s3.ap-south-1.amazonaws.com → AccessDenied; over https → works.', 7.6, 'ink', bold=True)
    return bigfig('Data is protected twice: in transit by HTTPS/TLS between the user and the AWS service, and at rest by AES-256 encryption on disk with keys managed in KMS.', o, h=178)
