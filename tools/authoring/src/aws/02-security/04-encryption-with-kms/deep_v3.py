from cloudkit import *

LADDER = ladder([
 ('Encryption scrambles data so only someone with the key can read it. The padlock in your browser is encryption while data travels; encrypted disks protect data while it rests.',
  'Look at the padlock next to a website address in your browser and click it — that is TLS, encryption in transit.',
  'If someone steals an encrypted hard disk without the key, can they read it?', 'No — they see only scrambled data.'),
 ('S3 encrypts every new object by default (SSE-S3). KMS is the AWS key service; your own key adds a second lock.',
  'Upload a file to S3 and look at its Properties → Server-side encryption.',
  'What is the difference between “in transit” and “at rest”?', 'In transit = moving over the network (HTTPS); at rest = stored on disk.'),
 ('Create a customer managed key, set bucket default SSE-KMS with Bucket Key, enforce HTTPS-only and prove it.',
  'Do the hands-on Steps 1–3 (or the simulator).',
  'A user has s3:GetObject but gets AccessDenied on an SSE-KMS object. Why?', 'They lack kms:Decrypt on the key (key policy or IAM).'),
 ('Design key policies with separation of duties, grants for services, rotation, cross-account keys and multi-Region keys.',
  'Write a key policy where SecurityAdmin manages the key but cannot decrypt, and DashboardRole can decrypt but not manage.',
  'Why does rotation not require re-encrypting old data?', 'KMS keeps old key material versions to decrypt existing data; new data uses the new material.'),
 ('Plan encryption architecture: data classification, key hierarchy per data domain, BYOK/external key stores, CloudHSM, crypto-shredding by key deletion, and audit evidence.',
  'Design a key strategy for a bank: which keys, which accounts, who administers, how deletion is approved.',
  'How can deleting a key be used deliberately?', '“Crypto-shredding”: deleting the only key makes all data encrypted under it permanently unreadable — a fast, verifiable erasure (with care for retention laws).')])

HOOD = under_hood('What KMS does internally — and the limits you design around.', [
 ('1 · Where keys live',
  '<p>KMS keys are generated and used inside FIPS 140-validated hardware security modules (HSMs) operated by AWS; the key material never leaves them in plaintext. You never see or download a KMS key (except asymmetric public keys). Applications get <b>data keys</b> instead, for local encryption.</p>'),
 ('2 · The three calls behind envelope encryption',
  table(['API', 'What it does'], [['GenerateDataKey', 'returns a new data key in plaintext + encrypted under the KMS key'], ['Decrypt', 'takes an encrypted data key (ciphertext) and returns the plaintext data key if allowed'], ['Encrypt', 'encrypts up to 4 KB directly with the KMS key (small secrets only)']], minw=480) +
  '<p>The ciphertext includes which KMS key was used, so Decrypt does not need a key id for symmetric keys.</p>'),
 ('3 · Who may use a key',
  '<p>The <b>key policy</b> is the primary control — every key has one. IAM policies grant KMS permissions only if the key policy allows the account to use IAM (the default root statement does). <b>Grants</b> give temporary, narrow permissions (used by services like EBS to decrypt a volume for an instance). <b>Encryption context</b> — key/value pairs bound to the ciphertext — adds integrity and appears in CloudTrail; conditions can require it.</p>'),
 ('4 · Rotation, deletion and multi-Region keys',
  '<ul><li>Automatic rotation creates new key material on a schedule (default 365 days, configurable 90–2,560); old material is kept to decrypt older data.</li><li>Deletion requires a 7–30 day waiting period; during it the key cannot be used — a safety net to notice mistakes.</li><li><b>Multi-Region keys</b> share key material across Regions for DR/replication; each replica has its own policy.</li></ul>'),
 ('5 · Costs and quotas',
  table(['Item', 'Typical value'], [['Customer managed key', '≈ USD 1 per month (prorated hourly)'], ['Requests', 'charged per 10,000 (Free Tier includes a monthly allowance)'], ['AWS managed / AWS owned keys', 'no monthly fee'], ['Shared request quota', 'thousands of cryptographic requests per second per account per Region (varies by Region/type)']], minw=440) +
  '<p>High-volume S3 workloads without Bucket Keys can hit the KMS request quota (<code>ThrottlingException</code>) and run up request charges — enable Bucket Keys.</p>'),
])

ROLES = by_role('Who works with encryption, and how.', [
 ('Software developer (backend)', 'Encrypts secrets and sensitive fields.', 'Secrets Manager (KMS-encrypted), KMS Encrypt for small values, AWS Encryption SDK.', 'Store the payment gateway API key in Secrets Manager; the app role has secretsmanager:GetSecretValue and kms:Decrypt on that key.', 'Never logging decrypted values; encryption context.'),
 ('App / mobile developer', 'Protects data on devices and in transit.', 'HTTPS everywhere, pre-signed URLs, client-side encryption for very sensitive uploads.', 'Upload ID documents with a pre-signed PUT URL to an SSE-KMS bucket.', 'TLS, certificate pinning basics.'),
 ('Data analyst', 'Needs kms:Decrypt to query encrypted data.', 'Athena/QuickSight roles with Decrypt on the data lake key.', 'Query fails with KMS AccessDenied → ask for key access, not bucket access.', 'Recognising KMS errors.'),
 ('Data engineer', 'Designs encryption for the lake.', 'SSE-KMS per data zone, Bucket Keys, Glue/EMR encryption settings, cross-account key sharing.', 'raw/ and curated/ use different keys; analytics account gets Decrypt on curated only.', 'Key per domain; cost control.'),
 ('ML / AI engineer', 'Encrypts training data, models and endpoints.', 'SageMaker volume/output KMS keys, encrypted S3 datasets, Bedrock with customer managed keys where supported.', 'Fine-tuned model artefacts encrypted with the team key.', 'Passing KMS key ids to training jobs.'),
 ('DevOps / cloud engineer', 'Makes encryption the default.', 'EBS encryption by default, S3 default encryption, RDS encrypted, SCPs denying unencrypted resources.', 'An SCP denies creating unencrypted RDS instances.', 'Guard-rails, key lifecycle.'),
 ('Security engineer', 'Owns key policies and evidence.', 'KMS key policies, CloudTrail Decrypt events, Config rules (s3-bucket-ssl-requests-only, encrypted-volumes).', 'Answer “who decrypted customer data in March?” from CloudTrail.', 'Key policy design, audit.')])

DOMAINS = by_domain('Encryption expectations by industry.', [
 ('Banking / fintech', 'card and account data', 'customer managed keys per data class, CloudHSM where mandated, TLS 1.2+', 'PCI DSS key management; RBI expectations on data protection'),
 ('Healthcare', 'patient records, scans', 'SSE-KMS, client-side for highly sensitive data, encryption context per patient/tenant', 'DPDP/ABDM; HIPAA encryption safeguards'),
 ('Retail / e-commerce', 'orders, addresses', 'SSE-KMS for PII buckets, Secrets Manager for API keys', 'PCI DSS; DPDP'),
 ('Education', 'student records, exam papers', 'SSE-KMS for exam papers with tight key users; HTTPS-only portals', 'exam confidentiality; student data under DPDP'),
 ('Media', 'unreleased films', 'separate keys per title; disable key to embargo', 'contractual security clauses'),
 ('Government', 'citizen data', 'keys in India Regions, strict administrators, CloudTrail evidence', 'MeitY/CERT-In requirements')])

PRO = (
 cost_calc('Worked cost example: sales bucket with SSE-KMS (Mumbai)', [
   ['Customer managed key', '1 key', '≈ USD 1 / month', '≈ USD 1.00'],
   ['KMS requests without Bucket Key', '3 million (1 per GET/PUT)', '≈ USD 0.03 / 10,000', '≈ USD 9.00'],
   ['KMS requests with Bucket Key', '≈ 30,000', '≈ USD 0.03 / 10,000', '≈ USD 0.09'],
   ['SSE-S3 alternative', '—', 'free', 'USD 0.00']],
   'with Bucket Key ≈ USD 1.1 / month',
   'Approximate prices; confirm on the KMS pricing page. Bucket Keys can cut KMS request costs by up to 99%.') +
 '  <h3>Commands for keys and encryption</h3>\n' + cheatsheet([
   ('aws kms create-key --description "…" ; aws kms create-alias --alias-name alias/x --target-key-id KEY', 'create a key with a friendly name'),
   ('aws kms get-key-policy --key-id KEY --policy-name default', 'read the key policy'),
   ('aws kms enable-key-rotation --key-id KEY --rotation-period-in-days 365', 'turn on rotation'),
   ('aws s3api put-bucket-encryption --bucket B --server-side-encryption-configuration …', 'bucket default encryption'),
   ('aws s3api head-object --bucket B --key K', 'how an object is encrypted'),
   ('aws ec2 enable-ebs-encryption-by-default', 'encrypt all new EBS volumes in the Region'),
   ('aws kms schedule-key-deletion --key-id KEY --pending-window-in-days 30', 'delete safely (cancel-key-deletion to undo)')]) +
 '  <h3>Encryption errors and fixes</h3>\n' + errors_table([
   ('An error occurred (AccessDenied) when calling the GetObject operation: User … is not authorized to perform: kms:Decrypt on resource: arn:aws:kms:…', 'reading SSE-KMS objects', 'no kms:Decrypt for that key', 'add the principal to the key policy users or allow kms:Decrypt in IAM (if the key policy permits IAM)'),
   ('An error occurred (KMS.DisabledException) when calling the GetObject operation', 'key disabled', 'the KMS key is disabled', 'enable the key'),
   ('An error occurred (KMS.KMSInvalidStateException) … pending deletion', 'key scheduled for deletion', 'key cannot be used', 'cancel-key-deletion, then enable'),
   ('An error occurred (ThrottlingException) … You have exceeded the rate at which you may call KMS', 'heavy S3 traffic', 'KMS request quota', 'enable S3 Bucket Keys; request a quota increase'),
   ('An error occurred (MalformedPolicyDocument) … The new key policy will not allow you to update the key policy in the future', 'editing a key policy', 'you removed your own admin access', 'keep the root/admin statement (AWS blocks the lock-out)')]) +
 checklist('Encryption checklist', ['S3 default encryption on (SSE-S3 minimum; SSE-KMS for sensitive data).', 'HTTPS-only bucket policies on sensitive buckets.', 'EBS encryption by default enabled in every Region you use.', 'RDS/Aurora created encrypted (cannot be switched on later in place).', 'Customer managed keys with separated admins/users and rotation on.', 'Key deletion only via an approved process; disable first.']) +
 refs([('AWS KMS developer guide', 'https://docs.aws.amazon.com/kms/latest/developerguide/overview.html'), ('Protecting data with server-side encryption (S3)', 'https://docs.aws.amazon.com/AmazonS3/latest/userguide/serv-side-encryption.html'), ('Reducing cost with S3 Bucket Keys', 'https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-key.html'), ('Key policies in AWS KMS', 'https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html')])
)

PROJ = projects([
 ('Basic', 'Encryption map of a small business', 'List every place a coaching institute stores data (S3, laptop backups, database, emails).',
  ['For each, say: encrypted at rest? in transit? who holds the key?', 'Choose SSE-S3 or SSE-KMS for each S3 bucket and justify.', 'List where HTTPS-only must be enforced.'],
  'A one-page table with justifications.', 'Estimate the monthly KMS cost of your design.'),
 ('Intermediate', 'CityBite R1 end to end', 'Sales files must be encrypted at rest, private, and refuse non-HTTPS requests — with proof.',
  ['Bucket with Block Public Access, SSE-KMS (your key) + Bucket Key.', 'HTTPS-only bucket policy.', 'Upload 3 sales CSVs; head-object proves encryption.', 'Prove HTTP is refused with --endpoint-url http://…; HTTPS works.'],
  'Commands, outputs and screenshots for each proof.', 'Add an accountant role that can decrypt and an intern role that cannot; show both outcomes.'),
 ('Advanced', 'Separation of duties with KMS', 'Security admins manage keys; data teams use them; nobody does both.',
  ['Create SecurityAdmin and DataUser roles.', 'Key policy: admins manage (no Decrypt), users Decrypt/GenerateDataKey (no management).', 'Prove: SecurityAdmin cannot read an SSE-KMS object; DataUser cannot disable the key.', 'Find both attempts in CloudTrail.'],
  'Key policy, test outputs and CloudTrail events.', 'Add encryption context and a condition requiring it.')])

SIMD = awsfig('Lab map: KMS key alias citybite-sales; S3 bucket with SSE-KMS default and HTTPS-only policy; sales file encrypted; HTTP request denied; key disabled locks data.',
    grp('acct', 10, 10, 620, 210, 'AWS account {acct} · ap-south-1', k='acct') +
    grp('vpc', 24, 30, 180, 170, 'AWS KMS', k='kms') + svc(114, 60, 'key', 'alias/citybite-sales', 'customer managed', 'violet', k='key', w=110) + svc(114, 140, 'lock', 'secret.enc', 'encrypt/decrypt', 'violet', k='enc', w=96) +
    grp('region', 230, 30, 230, 170, 'S3 · citybite-sales-{acct}', k='bucket') +
    svc(290, 70, 'shield', 'Default SSE-KMS', '+ Bucket Key', 'green', k='sse', w=96) + svc(400, 70, 'fw', 'HTTPS-only', 'bucket policy', 'red', k='pol', w=86) + svc(345, 150, 'file', 'sales/day1.csv', 'aws:kms', 'blue', k='obj', w=96) +
    link(170, 86, 240, 96, k='kl') +
    svc(550, 50, 'globe', 'http:// request', 'AccessDenied', 'red', k='http', w=96) + svc(550, 140, 'lock', 'Key disabled', 'all objects locked', 'amber', k='dis', w=96), h=230)

SIM = simlab(dict(title='Encrypt the sales bucket with your own key', intro='Create the key, make the bucket use it, prove HTTPS-only and use the emergency brake.',
  diagram=SIMD, lit=['acct', 'kms', 'bucket'], vars={'b': 'citybite-sales-123456789012'},
  steps=[
   dict(title='Create key + alias', goal='Create a customer managed key and the alias <code>alias/citybite-sales</code>.', hint='<code>aws kms create-key</code> then <code>aws kms create-alias --alias-name alias/citybite-sales --target-key-id KEYID</code>. The alias command completes the step.', answer='aws kms create-alias --alias-name alias/citybite-sales --target-key-id 1234abcd-12ab-34cd-56ef-1234567890ab',
        cli=[dict(re=r'^aws kms create-alias --alias-name alias/citybite-sales --target-key-id \S+$', out='')],
        errors=[dict(re=r'^aws kms create-key( --description .*)?( --query .*)?( --output \w+)?$', out='{\n    "KeyMetadata": {\n        "KeyId": "1234abcd-12ab-34cd-56ef-1234567890ab",\n        "KeyState": "Enabled",\n        "KeyUsage": "ENCRYPT_DECRYPT",\n        "KeySpec": "SYMMETRIC_DEFAULT",\n        "KeyManager": "CUSTOMER"\n    }\n}\n(Now give it the alias.)', ok=True),
                dict(re=r'^aws kms create-alias --alias-name citybite-sales', out='An error occurred (ValidationException): Alias must start with the prefix "alias/".')],
        console=dict(crumbs='KMS › Customer managed keys › Create key', fields=[dict(label='Key type', type='select', options=['Symmetric', 'Asymmetric', 'HMAC'], re=r'^Symmetric$', why='Use a symmetric key.'), dict(label='Alias', ph='citybite-sales', re=r'^(alias/)?citybite-sales$', why='Alias: citybite-sales')], button='Finish', out='Key 1234abcd-… created · alias/citybite-sales'),
        lights=['key'], explain='KMS generated AES-256 key material inside its HSMs. You get an ID and an alias — never the key itself. The default key policy lets your account’s IAM policies grant its use.'),
   dict(title='Encrypt a small secret', goal='Encrypt <code>secret.txt</code> with the key.', hint='<code>aws kms encrypt --key-id alias/citybite-sales --plaintext fileb://secret.txt</code>', answer='aws kms encrypt --key-id alias/citybite-sales --plaintext fileb://secret.txt',
        cli=[dict(re=r'^aws kms encrypt --key-id alias/citybite-sales --plaintext fileb://secret\.txt( --query .*)?( --output \w+)?.*$', out='{\n    "CiphertextBlob": "AQICAHhN5fM…kx8wZt0AAAB+MHwGCSqGSIb3DQEHBqBvMG0CAQAw…",\n    "KeyId": "arn:aws:kms:ap-south-1:{acct}:key/1234abcd-12ab-34cd-56ef-1234567890ab",\n    "EncryptionAlgorithm": "SYMMETRIC_DEFAULT"\n}')],
        errors=[dict(re=r'^aws kms encrypt --key-id alias/citybite-sales --plaintext file://secret\.txt', out='Works on CLI v1, but on CLI v2 binary input should use fileb:// (plain text is treated as base64 by default).', ok=True)],
        lights=['enc'], explain='The sentence became unreadable ciphertext. The blob records which key encrypted it, so decrypt needs no key id. Direct Encrypt is limited to 4 KB — bigger data uses data keys.'),
   dict(title='Bucket default SSE-KMS + Bucket Key', goal='Make <code>{b}</code> encrypt all new objects with alias/citybite-sales and Bucket Key.', hint='<code>aws s3api put-bucket-encryption --bucket {b} --server-side-encryption-configuration file://enc.json</code>', answer='aws s3api put-bucket-encryption --bucket {b} --server-side-encryption-configuration file://enc.json',
        cli=[dict(re=r'^aws s3api put-bucket-encryption --bucket {b} --server-side-encryption-configuration .*(aws:kms|file://\S+).*$', out='')],
        console=dict(crumbs='S3 › {b} › Properties › Default encryption › Edit', fields=[dict(label='Encryption type', type='select', options=['SSE-S3', 'SSE-KMS', 'DSSE-KMS'], re=r'^SSE-KMS$', why='Choose SSE-KMS.'), dict(label='AWS KMS key', type='select', options=['aws/s3', 'alias/citybite-sales'], re=r'^alias/citybite-sales$', why='Use your own key.'), dict(label='Bucket Key', type='check', must=True, why='Enable Bucket Key to cut KMS costs.')], button='Save changes', out='Default encryption: SSE-KMS (alias/citybite-sales), Bucket Key enabled'),
        lights=['sse', 'kl'], explain='From now on every new object gets a data key derived through your KMS key. With Bucket Key, S3 asks KMS for a bucket-level key occasionally instead of once per object.'),
   dict(title='Prove HTTPS-only', goal='With the HTTPS-only policy in place, try to download <code>sales/day1.csv</code> over plain HTTP.', hint='<code>aws s3 cp s3://{b}/sales/day1.csv - --endpoint-url http://s3.ap-south-1.amazonaws.com</code>', answer='aws s3 cp s3://{b}/sales/day1.csv - --endpoint-url http://s3.ap-south-1.amazonaws.com',
        cli=[dict(re=r'^aws s3 cp s3://{b}/sales/day1\.csv - --endpoint-url http://s3\.ap-south-1\.amazonaws\.com/?$', out='download failed: s3://{b}/sales/day1.csv to - An error occurred (AccessDenied) when calling the GetObject operation: User: arn:aws:iam::{acct}:user/{you} is not authorized to perform: s3:GetObject … with an explicit deny in a resource-based policy')],
        errors=[dict(re=r'^aws s3 cp s3://{b}/sales/day1\.csv -$', out='outlet,item,amount\nAndheri,thali,120\n(HTTPS works. Now prove plain HTTP is refused with --endpoint-url http://s3.ap-south-1.amazonaws.com)', ok=True),
                dict(re=r'^aws s3api head-object --bucket {b} --key sales/day1\.csv.*$', out='aws:kms   arn:aws:kms:ap-south-1:{acct}:key/1234abcd-…   True', ok=True)],
        lights=['pol', 'obj', 'http'], explain='The bucket policy’s Deny matched because aws:SecureTransport was false. Even you — the admin — are refused without HTTPS. Keep this output as evidence.'),
   dict(title='Emergency brake: disable the key', goal='Disable the key and try to read the file again.', hint='<code>aws kms disable-key --key-id 1234abcd-12ab-34cd-56ef-1234567890ab</code>', answer='aws kms disable-key --key-id 1234abcd-12ab-34cd-56ef-1234567890ab',
        cli=[dict(re=r'^aws kms disable-key --key-id \S+$', out='(key disabled)\n$ aws s3 cp s3://{b}/sales/day1.csv -\ndownload failed: … An error occurred (KMS.DisabledException) when calling the GetObject operation: arn:aws:kms:ap-south-1:{acct}:key/1234abcd-… is disabled.')],
        console=dict(crumbs='KMS › Customer managed keys › citybite-sales › Key actions', fields=[dict(label='Action', type='select', options=['Enable', 'Disable', 'Schedule key deletion'], re=r'^Disable$', why='Choose Disable (not deletion).')], button='Confirm', out='Key disabled — objects encrypted with it can no longer be read'),
        lights=['dis'], explain='No data was touched, yet every object under this key is unreadable until you enable the key again — an instant, reversible lock. Deletion, by contrast, is permanent after the waiting period.'),
  ]))
