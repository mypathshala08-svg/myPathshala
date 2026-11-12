from cloudkit import *

LADDER = ladder([
 ('A server should never carry a permanent password to AWS. It gets a “day pass” (role) that works only for the jobs it needs and expires by itself.',
  'Think of a delivery app rider: the app gives a one-time OTP for each delivery instead of your house key. List two more examples of “temporary passes” in daily life.',
  'If a day pass is stolen at night, what happens next morning?', 'It no longer works — temporary credentials expire.'),
 ('Role = permissions; instance profile = how the role is attached to an EC2 server; the server fetches temporary keys automatically.',
  'Do Step 1 of the hands-on (or the simulator) and find the role inside the instance profile.',
  'Do you run aws configure on an EC2 server?', 'No. Attach a role; the CLI and SDK find it automatically.'),
 ('Scope a server role to folders; add explicit Denies; require IMDSv2; prove allowed and denied actions from the server.',
  'Do Steps 2–3: launch the self-testing server and read its proof file.',
  'Which permission must the person launching the instance have?', 'iam:PassRole on that role (plus ec2:RunInstances).'),
 ('Choose the right mechanism for EC2, Lambda, ECS (task vs execution role) and EKS; enforce IMDSv2 with SCPs; replace roles on running instances.',
  'Swap the role on the running instance with replace-iam-instance-profile-association and watch the permissions change within minutes.',
  'Why separate ECS task role and task execution role?', 'The execution role is for ECS itself (pull image, logs); the task role is for your code — mixing them over-privileges the app.'),
 ('Design org-wide credential hygiene: no long-term keys anywhere, OIDC for CI/CD, credential exfiltration detection (GuardDuty), data perimeters with aws:SourceVpc / aws:ResourceOrgID.',
  'Write a bucket policy that only accepts requests from your VPC endpoint or your organisation, then test from CloudShell (should fail) and the instance (should work).',
  'GuardDuty finding “InstanceCredentialExfiltration”: what happened?', 'Credentials issued to an EC2 instance role were used from outside AWS/that instance — likely stolen via SSRF or a compromised host.')])

HOOD = under_hood('The mechanics behind instance credentials — what really happens on the host.', [
 ('1 · Rotation and expiry',
  '<p>EC2 obtains credentials for the role from STS and makes them available through IMDS; they are refreshed automatically well before they expire (typically valid for a few hours; new ones appear at least five minutes before the old ones expire). SDKs cache them and re-read IMDS when needed — your code never handles refresh.</p>'),
 ('2 · iam:PassRole — the anti-escalation lock',
  '<p>To attach a role to an instance (or a Lambda function, ECS task, Glue job…), the <i>caller</i> needs <code>iam:PassRole</code> on that role. Without this, any developer could launch a server with an admin role and borrow admin power. Grant it narrowly: <code>"Resource": "arn:aws:iam::ACCOUNT:role/app-*"</code>, optionally with <code>iam:PassedToService = ec2.amazonaws.com</code>.</p>'),
 ('3 · IMDSv2 details',
  table(['Setting', 'Meaning', 'Recommendation'], [['HttpTokens', 'optional (v1+v2) or required (v2 only)', 'required'], ['HttpPutResponseHopLimit', 'how many network hops the token response can travel', '1 for plain EC2; 2 if containers on the host need IMDS'], ['HttpEndpoint', 'enable/disable IMDS entirely', 'enabled (disable only if nothing needs it)'], ['InstanceMetadataTags', 'expose instance tags via IMDS', 'enable if apps read tags']], minw=560) +
  '<p>Change on a running instance with <code>aws ec2 modify-instance-metadata-options --instance-id … --http-tokens required</code>.</p>'),
 ('4 · How it looks in CloudTrail',
  '<p>Calls made by the server appear with <code>userIdentity.type = AssumedRole</code> and an ARN like <code>arn:aws:sts::ACCOUNT:assumed-role/LabAppRole/i-0abc123…</code> — the session name is the <b>instance ID</b>, so you can trace every action to one server. Credential use from an unexpected IP is what GuardDuty’s credential-exfiltration findings detect.</p>'),
 ('5 · Data perimeter conditions',
  '<p>Even valid role keys can be limited to where they are used: <code>aws:SourceVpc</code> / <code>aws:SourceVpce</code> (request must come through your VPC endpoint), <code>aws:ec2InstanceSourceVPC</code> and <code>aws:ec2InstanceSourcePrivateIPv4</code> (credentials must be used from the instance’s own VPC/IP), <code>aws:PrincipalOrgID</code> and <code>aws:ResourceOrgID</code> (only identities/resources of your organisation). Together they make stolen credentials far less useful.</p>'),
])

ROLES = by_role('Who meets instance and execution roles, and how.', [
 ('Software developer (backend)', 'Writes code that just works with roles.', 'boto3/SDK default chain, no credential code; local dev via SSO profile, prod via role.', 'Same code runs on a laptop (SSO profile) and on EC2 (instance role) without changes.', 'Never reading keys from config; testing AccessDenied paths.'),
 ('App / mobile developer', 'Backends on Lambda/Amplify use execution roles.', 'Lambda execution roles, Amplify service roles.', 'API function may write to one DynamoDB table only.', 'Least-privilege execution roles.'),
 ('Data analyst', 'Rarely sees roles directly; notebooks or BI tools may use them.', 'QuickSight/Athena service roles; SageMaker notebooks for analysis.', 'Why the dashboard cannot read a new bucket: the QuickSight role lacks access.', 'Asking for access to the right role, not personal keys.'),
 ('Data engineer', 'Every job runs as a role.', 'Glue job roles, EMR instance profiles (EC2 role for EMR nodes), Airflow (MWAA) execution role.', 'EMR nodes read raw/ and write curated/ through the cluster’s instance profile.', 'Per-job roles, prefix scoping, KMS permissions.'),
 ('ML / AI engineer', 'Training jobs and endpoints assume execution roles.', 'SageMaker execution role, Bedrock access via role, GPU instances with instance profiles.', 'Training job reads datasets/ and writes models/; cannot read HR data.', 'Separating training and inference roles.'),
 ('DevOps / cloud engineer', 'Designs roles, PassRole, IMDS defaults.', 'Launch templates with profiles and IMDSv2, SCPs enforcing IMDSv2, OIDC roles for CI.', 'Account-wide default: IMDSv2 required for every new instance.', 'Guard-rails at scale.'),
 ('Security engineer', 'Detects misuse.', 'GuardDuty credential-exfiltration findings, CloudTrail session names, data perimeters.', 'Alert when LabAppRole credentials are used outside the VPC.', 'Credential-theft paths and detection.')])

DOMAINS = by_domain('Server identity rules by industry.', [
 ('Banking / fintech', 'payment and lending servers', 'one role per service, IMDSv2 enforced by SCP, VPC endpoints + aws:SourceVpce conditions', 'RBI: no shared credentials; audit trail per server'),
 ('Healthcare', 'patient-record apps', 'roles scoped to patient-data prefixes with KMS key policies; explicit Deny on export buckets', 'DPDP/ABDM: least privilege for systems, not just people'),
 ('Retail / e-commerce', 'catalogue, orders', 'per-microservice task roles on ECS; Lambda execution roles per function', 'PCI DSS: application credentials protected and rotated'),
 ('Education', 'student portals, labs', 'portal role: read notes, write logs, deny submissions; sandbox accounts for students', 'student submissions private; proof of access controls'),
 ('Manufacturing / IoT', 'plant gateways', 'IoT credentials provider (X.509 → temporary role creds) for devices', 'one compromised device must not unlock others'),
 ('Government', 'citizen portals', 'roles + VPC endpoints, no internet access for data servers', 'CERT-In logging; data localisation')])

PRO = (
 '  <h3>Commands for instance roles</h3>\n' + cheatsheet([
   ('aws ec2 associate-iam-instance-profile --instance-id i-… --iam-instance-profile Name=LabAppRole', 'attach a role to a running instance'),
   ('aws ec2 replace-iam-instance-profile-association --association-id iip-assoc-… --iam-instance-profile Name=NewRole', 'swap the role without restarting'),
   ('aws ec2 describe-iam-instance-profile-associations --filters Name=instance-id,Values=i-…', 'which role an instance has'),
   ('aws ec2 modify-instance-metadata-options --instance-id i-… --http-tokens required --http-put-response-hop-limit 1', 'enforce IMDSv2'),
   ('aws ec2 modify-instance-metadata-defaults --http-tokens required --region ap-south-1', 'account default: IMDSv2 for new instances in a Region'),
   ("aws ec2 describe-instances --query 'Reservations[].Instances[?MetadataOptions.HttpTokens==`optional`].InstanceId' --output text", 'find instances still allowing IMDSv1')]) +
 '  <h3>Errors and fixes</h3>\n' + errors_table([
   ('An error occurred (UnauthorizedOperation) … You are not authorized to perform: iam:PassRole on resource: arn:aws:iam::…:role/LabAppRole', 'launching with a profile', 'launcher lacks iam:PassRole', 'allow iam:PassRole on that role ARN'),
   ('Value (LabAppRole) for parameter iamInstanceProfile.name is invalid. Invalid IAM Instance Profile name', 'run-instances right after creating', 'profile missing or not yet propagated', 'create the profile, add the role, wait ~10 s'),
   ('Unable to locate credentials (on the instance)', 'CLI on the server', 'no profile attached, or IMDS hop limit too low for containers, or IMDS disabled', 'attach a profile; check metadata options'),
   ('curl: (22) The requested URL returned error: 401', 'calling IMDS without a token', 'IMDSv2 required — expected', 'use the PUT token flow (SDKs do it automatically)'),
   ('An error occurred (AccessDenied) when calling the PutObject operation', 'server writing', 'role policy lacks that prefix, or an explicit Deny', 'check the exact key prefix and Deny statements'),
   ('Invalid principal in policy: "SERVICE":"ec2.amazon.com"', 'creating the role', 'typo in the service principal', 'use ec2.amazonaws.com')]) +
 checklist('Server identity checklist', ['Every instance has a dedicated role via an instance profile.', 'No ~/.aws/credentials or keys in env files, images or user data.', 'IMDSv2 required (and account default set).', 'Role policy scoped to exact prefixes; explicit Deny for must-never actions.', 'iam:PassRole granted narrowly.', 'Allowed and denied actions tested from the server and saved as evidence.']) +
 refs([('IAM roles for Amazon EC2', 'https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html'), ('Use IMDSv2', 'https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html'), ('Using instance profiles', 'https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_switch-role-ec2_instance-profiles.html'), ('Granting permission to pass a role', 'https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_passrole.html')])
)

PROJ = projects([
 ('Basic', 'Draw and explain a server identity', 'A college portal server must read notes and write logs.',
  ['Draw the chain: role → trust policy → permission policy → instance profile → instance → IMDSv2 → SDK.', 'Write the permission policy for notes/ (read) and logs/ (write).', 'Explain in three sentences why keys on the server are dangerous.'],
  'A diagram and the policy JSON.', 'Add the explicit Deny statements and explain why they matter.'),
 ('Intermediate', 'Self-proving server', 'Your institute’s auditor wants evidence the portal server cannot read student submissions.',
  ['Build the lab: bucket with three prefixes, role, profile, IMDSv2.', 'Launch with user data that writes the proof file to logs/.', 'Add one more test: list submissions/ (should be denied).', 'Collect the proof file, describe-instances output and the CloudTrail AccessDenied event.'],
  'Proof file + two screenshots or CLI outputs.', 'Repeat after swapping the role to a broader one and show the proof changes.'),
 ('Advanced', 'Stolen-credential drill', 'Show that stolen instance credentials are limited in time and place.',
  ['On the instance, print the temporary keys from IMDSv2 and note the expiry.', 'Add a bucket policy Deny when aws:SourceVpce is not your VPC endpoint (create an S3 gateway endpoint).', 'Try the same keys from CloudShell (export them) — show AccessDenied.', 'Enable GuardDuty and look for credential-exfiltration findings (may take time).'],
  'Commands, outputs, and a short incident-style write-up.', 'Use aws:ec2InstanceSourceVPC in the role policy instead and compare.')])

SIMD = awsfig('Lab map: S3 bucket with notes, submissions and logs; role LabAppRole with trust for EC2 and a policy; instance profile; EC2 instance with IMDSv2; proof file written to logs.',
    grp('acct', 10, 10, 620, 210, 'AWS account {acct} · ap-south-1', k='acct') +
    grp('region', 24, 30, 230, 172, 'S3 · edu-lab-{acct}', k='bucket') +
    svc(70, 60, 'folder', 'notes/', 'read ✓', 'green', k='notes') + svc(160, 60, 'folder', 'submissions/', 'denied ✘', 'red', k='subs', w=80) + svc(115, 140, 'folder', 'logs/', 'proof file', 'blue', k='logs') +
    svc(320, 50, 'role', 'LabAppRole', 'trust: EC2', 'amber', k='role') + svc(320, 140, 'key', 'LabAppPolicy', 'read · write · deny', 'violet', k='pol', w=84) + link(320, 104, 320, 138, k='lp') +
    svc(430, 95, 'app', 'Instance profile', 'holds the role', 'blue', k='prof', w=86) + link(358, 76, 388, 106, k='rp') +
    grp('vpc', 490, 30, 130, 172, 'EC2 · t3.micro', k='ec2') + svc(555, 70, 'server', 'role-lab', 'IMDSv2 only', 'green', k='inst', w=80) + svc(555, 145, 'chip', 'user data', 'runs tests', 'card', k='ud', w=80) +
    link(474, 120, 512, 96, k='attach') + link(512, 160, 160, 170, k='write'), h=230)

SIM = simlab(dict(title='Build a server that proves its own permissions', intro='Create the role and profile, launch the server with IMDSv2, then read the proof it writes to S3 — without logging in.',
  diagram=SIMD, lit=['acct', 'bucket', 'notes', 'subs', 'logs'], vars={'b': 'edu-lab-123456789012'},
  steps=[
   dict(title='Create the role (trust EC2)', goal='Create role <code>LabAppRole</code> with a trust policy for <code>ec2.amazonaws.com</code>.', hint='<code>aws iam create-role --role-name LabAppRole --assume-role-policy-document file://trust.json</code>', answer='aws iam create-role --role-name LabAppRole --assume-role-policy-document file://trust.json',
        cli=[dict(re=r'^aws iam create-role --role-name LabAppRole --assume-role-policy-document file://\S+( --query .*)?$', out='{\n    "Role": {\n        "RoleName": "LabAppRole",\n        "Arn": "arn:aws:iam::{acct}:role/LabAppRole",\n        "AssumeRolePolicyDocument": {"Statement": [{"Effect": "Allow", "Principal": {"Service": "ec2.amazonaws.com"}, "Action": "sts:AssumeRole"}]}\n    }\n}')],
        errors=[dict(re=r'ec2\.amazon\.com', out='An error occurred (MalformedPolicyDocument) when calling the CreateRole operation: Invalid principal in policy: "SERVICE":"ec2.amazon.com"\n→ The service principal is ec2.amazonaws.com')],
        console=dict(crumbs='IAM › Roles › Create role', fields=[dict(label='Trusted entity type', type='select', options=['AWS account', 'AWS service', 'Web identity'], re=r'^AWS service$', why='Choose AWS service.'), dict(label='Use case', type='select', options=['EC2', 'Lambda', 'ECS Task'], re=r'^EC2$', why='The server is EC2.'), dict(label='Role name', ph='LabAppRole', re=r'^LabAppRole$', why='Name it LabAppRole.')], button='Create role', out='Role LabAppRole created (instance profile LabAppRole created too)'),
        lights=['role'], explain='The trust policy says <i>only the EC2 service</i> may assume this role. It has no permissions yet.'),
   dict(title='Attach the scoped policy', goal='Attach <code>LabAppPolicy</code> (read notes/, write logs/, deny submissions/ and deletes) to the role.', hint='<code>aws iam put-role-policy --role-name LabAppRole --policy-name LabAppPolicy --policy-document file://policy.json</code>', answer='aws iam put-role-policy --role-name LabAppRole --policy-name LabAppPolicy --policy-document file://policy.json',
        cli=[dict(re=r'^aws iam put-role-policy --role-name LabAppRole --policy-name LabAppPolicy --policy-document file://\S+$', out=''), dict(re=r'^aws iam attach-role-policy --role-name LabAppRole --policy-arn arn:aws:iam::{acct}:policy/LabAppPolicy$', out='')],
        errors=[dict(re=r'^aws iam attach-role-policy --role-name LabAppRole --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess$', out='Attached — but that gives full access to every bucket, including submissions. Lab requirement broken. Use the scoped LabAppPolicy.')],
        console=dict(crumbs='IAM › Roles › LabAppRole › Add permissions', fields=[dict(label='Policy', type='select', options=['AmazonS3FullAccess', 'AmazonS3ReadOnlyAccess', 'LabAppPolicy'], re=r'^LabAppPolicy$', why='Least privilege: LabAppPolicy only.')], button='Add permissions', out='LabAppPolicy attached to LabAppRole'),
        lights=['pol', 'lp'], explain='Now the role can: GetObject on notes/*, PutObject on logs/*. Two explicit Denies make “never submissions” and “never delete” permanent, even if someone adds a broad Allow later.'),
   dict(title='Instance profile', goal='Create instance profile <code>LabAppRole</code> and add the role to it (the console does this for you).', hint='create-instance-profile, then add-role-to-instance-profile. The second command completes the step.', answer='aws iam add-role-to-instance-profile --instance-profile-name LabAppRole --role-name LabAppRole',
        cli=[dict(re=r'^aws iam add-role-to-instance-profile --instance-profile-name LabAppRole --role-name LabAppRole$', out='')],
        errors=[dict(re=r'^aws iam create-instance-profile --instance-profile-name LabAppRole$', out='{ "InstanceProfile": { "InstanceProfileName": "LabAppRole", "Roles": [] } }\n(Empty profile. Now add the role.)', ok=True)],
        console=dict(crumbs='IAM › Roles › LabAppRole › Summary', fields=[dict(label='Instance profile ARN shown?', type='check', must=True, why='The console created the profile automatically — tick to confirm.')], button='Confirm', out='Instance profile arn:aws:iam::{acct}:instance-profile/LabAppRole holds LabAppRole'),
        lights=['prof', 'rp'], explain='The instance profile is the clip that attaches exactly one role to an instance. CLI users forget it; console users get it automatically.'),
   dict(title='Launch with IMDSv2 + user data', goal='Launch a t3.micro with profile <code>LabAppRole</code>, IMDSv2 required and user data <code>proof.sh</code>.', hint='<code>aws ec2 run-instances --image-id … --instance-type t3.micro --iam-instance-profile Name=LabAppRole --metadata-options HttpTokens=required --user-data file://proof.sh</code>',
        answer='aws ec2 run-instances --image-id resolve:ssm:/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 --instance-type t3.micro --iam-instance-profile Name=LabAppRole --metadata-options HttpTokens=required --user-data file://proof.sh',
        cli=[dict(re=r'^aws ec2 run-instances .*--iam-instance-profile Name=LabAppRole.*--metadata-options HttpTokens=required.*--user-data file://proof\.sh.*$', out='{\n    "Instances": [{\n        "InstanceId": "i-0a1b2c3d4e{rnd}",\n        "State": {"Name": "pending"},\n        "IamInstanceProfile": {"Arn": "arn:aws:iam::{acct}:instance-profile/LabAppRole"},\n        "MetadataOptions": {"HttpTokens": "required"}\n    }]\n}'), dict(re=r'^aws ec2 run-instances .*--metadata-options HttpTokens=required.*--iam-instance-profile Name=LabAppRole.*--user-data file://proof\.sh.*$', out='{ "Instances": [{ "InstanceId": "i-0a1b2c3d4e{rnd}", "State": {"Name": "pending"} }] }')],
        errors=[dict(re=r'^aws ec2 run-instances (?!.*--iam-instance-profile).*', out='Launched — but with no role the proof will say “Unable to locate credentials”. Add --iam-instance-profile Name=LabAppRole.'),
                dict(re=r'^aws ec2 run-instances (?!.*HttpTokens=required).*--iam-instance-profile.*', out='Launched with IMDSv1 allowed. The lab requires IMDSv2: add --metadata-options HttpTokens=required.')],
        console=dict(crumbs='EC2 › Launch an instance › Advanced details', fields=[dict(label='IAM instance profile', type='select', options=['No IAM role', 'LabAppRole'], re=r'^LabAppRole$', why='Choose LabAppRole.'), dict(label='Metadata version', type='select', options=['V1 and V2 (token optional)', 'V2 only (token required)'], re=r'^V2 only', why='Require IMDSv2.'), dict(label='User data pasted (proof.sh)', type='check', must=True, why='Paste the proof.sh script into User data.')], button='Launch instance', out='Launched i-0a1b2c3d4e{rnd} with LabAppRole, IMDSv2 required'),
        lights=['ec2', 'inst', 'ud', 'attach'], explain='EC2 assumed LabAppRole for this instance. At first boot, cloud-init runs proof.sh: the CLI on the server gets keys through IMDSv2 and tests its own access.'),
   dict(title='Read the proof', goal='Print the proof file the server wrote to <code>logs/</code>.', hint='<code>aws s3 cp s3://{b}/logs/proof-i-0a1b2c3d4e{rnd}.txt -</code> (or list logs/ first).', answer='aws s3 cp s3://{b}/logs/proof-i-0a1b2c3d4e{rnd}.txt -',
        cli=[dict(re=r'^aws s3 cp s3://{b}/logs/proof-i-0a1b2c3d4e{rnd}\.txt -$', out='Thu Nov 12 10:42:03 UTC 2026\narn:aws:sts::{acct}:assumed-role/LabAppRole/i-0a1b2c3d4e{rnd}\nread notes: ALLOWED\nread submissions: DENIED\ndelete notes: DENIED\nIMDSv1 call: 401')],
        errors=[dict(re=r'^aws s3 ls s3://{b}/logs/?$', out='2026-11-12 10:42:05        212 proof-i-0a1b2c3d4e{rnd}.txt\n(Now print it with aws s3 cp … -)', ok=True)],
        console=dict(crumbs='S3 › {b} › logs/', fields=[dict(label='Object to open', ph='proof-i-0a1b2c3d4e{rnd}.txt', re=r'^proof-i-0a1b2c3d4e{rnd}\.txt$', why='Open proof-i-0a1b2c3d4e{rnd}.txt')], button='Open', out='read notes ALLOWED · submissions DENIED · delete DENIED · IMDSv1 401'),
        lights=['logs', 'write', 'notes', 'subs'], explain='Evidence, written by the server itself: it acted as <b>assumed-role/LabAppRole/&lt;instance-id&gt;</b>, could read notes, could not read submissions or delete, and IMDSv1 is blocked (401). No login, no keys.'),
  ]))
